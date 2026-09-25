# SkyWynn admin config contract (v1, kit 1.1, 2026-09-25)

Skyy's direction: **everything a server owner might change must be doable in game**, and the game and the files always agree.
Each Skyy mod keeps owning its settings and its own files. It describes them once (a schema) and puts that description plus one
function on the bridge. SkyyMenu 0.3 (the Mods section, `/modconfig`) only draws pages and passes clicks back. Without SkyyMenu nothing
changes: the mod still reads its files and its admin commands still work.

Source of truth: `research/Server-Setup-Spec.md` sections 1.3-1.4 and 6. Implementation: `tools/skyycfg.py` (a code generator every
build script imports, so each jar carries its own copy). Proof: `python tools/skyycfg_test.py` (bare JVM, spec 8.2 a-j, 8.1.3, 8.1.4,
and section Q for kit 1.1: 273 checks, 29 schemas that must fail, 3 that must build).
The player Settings registry (`settings:*`, research/Settings-Spec.md) is a separate twin with the same key, page and never-throws rules.

## Kit versions

The contract version (header element 0) stays `"1"`. The kit version is `KIT_VERSION` in `tools/skyycfg.py` (also `CfgRows.KIT` in a
jar built with 1.1). Every jar carries its own copy, so jars built with different kit versions run side by side; a mod gets a kit
fix only when it is rebuilt at its own next version.

| Kit | Where | What changed |
|---|---|---|
| 1.0 | the 18 jars of round 3/4 (deploy set of 2026-09-25 04:11) | first version |
| 1.1 | each adopter's next version | the five round-4 gaps below; the bridge keys, the header layout of every existing row, the op arguments old callers send, the file, log, history and export formats are unchanged |

Kit 1.1 fixes (each marked 1.1 further down):
1. **Hand-edited table lines are checked** like an in-game change (entry key, columns, bounds, the row's `check=` hook). A refused line is
   logged `invalid`, memory keeps the old value, its reload routine does not run for it, and the file keeps the typed line. Under
   concurrency memory never shows a hand-typed value that has not passed: a line waiting for its `check=` hook is held like a refused
   one, only the entry's newest change may apply when the hook answers, and the `reload` op never merges a file a save is writing.
2. **1-column tables** keep `|` inside their value (never split, never turned into `sep=`), and a table without number columns takes
   its text length from the row max (1-2000; 200 without a max) and takes no min (build-checked).
3. **A custom row's file lines run the mod's `RELOAD`** after the write, like a `reload:` row (not for `restart`). Before any reload
   routine runs, the kit writes every other file of the mod whose in-game changes are still only in memory, so the routine never
   reads a stale file back into a `field:` value; when such a file cannot be written (or another thread saves it while the routine
   runs), the kit sets those `field:` values again after the routine.
4. **A lone reload request runs**: `CfgFile.wants()` counts a queued reload routine (`CfgFile.addReloads`) with no changed line.
5. **Action rows can take a typed value** (`value=<type>`, published as a 12th row element).

What each live adopter gains when it is next rebuilt (nothing changes in a jar until then; no adopter has to change code):

| Fix | Adopters (live version) |
|---|---|
| 1 hand-edited table lines checked | SkyyAccessories 0.4.4 (`bonus`), SkyyCollections 0.2.2 (`rewards`), SkyyCooking 0.1.2 (`xp`, `tree`), SkyyExploration 0.2.1 (`chest.xp`, `zone.xp`, `title`), SkyyRolls 0.1.5 (`cost`), SkyySkills 0.4.3 (`block`, `prefix`, `suffix`, `combat.role`, `alchemy.xp`, `smithing.xp`), SkyyTrees 0.2.2 (`dust.perTree`, `nodes.<Tree>`) |
| 2 1-column tables | lets SkyyCollections bind its `coll.` lines (spec 4.11) as a 1-column table (needs the next SkyyMenu's table view too, see Known limits); the existing 1-column tables (Accessories `bonus`, Collections `rewards`, Skills `block`/`prefix`/`suffix`, Trees `nodes.*`, Menu `settings.defaults`) accept `|` and keep the 200 cap (no max set) |
| 3 custom rows run `RELOAD` | SkyyEssentials 0.1.3 (`tradeOpenMode` -> `TCfg.reloadKit`), SkyyIslands 0.5.2 (`defaults.perm.*`, `defaults.visit.mode`, `tint.resend` -> `IslandHooks.reloadCfg`), SkyySkills 0.4.3 (`levels.scale`, `levels.max` -> `SkillKit.reload`: its SkillKitArm workaround becomes unnecessary), SkyyMenu (`menu.tooltips`, `settings.defaults` -> `MenuCfg.load`, which reads only config.properties: no visible change; the stale-read guard keeps a pending config.properties change from being read back old). SkyyClasses' custom row hands back no lines (unchanged) |
| 4 lone reload request | SkyySkills 0.4.3 (its curve rows' `CfgFile.addReloads` + `force` arm; `force` is no longer needed) |
| 5 value actions | new rows only (e.g. spec 5.7's "N" for SkyySkills' curve actions, which 0.4.3 had to model as custom int rows); needs the next SkyyMenu for the typed field |

In a mod's own code (1.1): `CfgFile.addReloads(f, set)` + `CfgFile.saveSoon(f)` is enough to run a reload routine once (no
`CfgFile.force`), and a custom row's file lines arm `RELOAD` by themselves.

## Bridge keys (System.getProperties().get("skyy.bridge"), a ConcurrentHashMap)

| Key | Value | Written by |
|---|---|---|
| `config:def:<Mod>` | `Object[]` mod header (below) | the mod, in `setup()` after its own config load, whether or not SkyyMenu exists |
| `config:fn:<Mod>` | `java.util.function.Function` taking an `Object[]` op (below) | the mod, same time |
| `config:epoch:<Mod>` | `Long`, +1 after every successful change from any source (menu, command, import, restore, undo, hand edit) | the mod |

`<Mod>` = the plugin name without version (`SkyyEconomy`), matching `Skyy[A-Z][A-Za-z]{1,30}`. Keys are **never removed**. There is no
`config:fn:register`: SkyyMenu scans the bridge for `config:def:` keys each time it builds the Mods list, so load order never matters.
Everything that crosses the bridge is a `java.lang` type (`String`, `String[]`, `Object[]`, `Long`, `Integer`, `Boolean`), a
`java.util.UUID` or a `Function`. **All setting values travel as canonical text**, exactly as the export code carries them.

## Mod header `config:def:<Mod>` = `Object[10]`

| # | Type | Meaning |
|---|---|---|
| 0 | String | contract version `"1"`. A newer one = "needs a newer SkyyMenu"; do not call it. |
| 1 | String | mod name |
| 2 | String | page title, max 24 characters |
| 3 | String | running version |
| 4 | String | the admin node the mod re-checks on every change (`skyyeconomy.admin`); SkyyMenu uses it only to show "view only" |
| 5 | String[] | category ids, max 16, `[a-z][a-zA-Z0-9]{0,15}`, display order (a fresh copy per publish) |
| 6 | String[] | category labels, max 20 characters |
| 7 | Object[] | rows, each `Object[11]` of Strings (`Object[12]` for an action row with `value=`, kit 1.1), display order |
| 8 | String | files, comma list relative to the world's `mods/` folder |
| 9 | String | note, max 100 characters |

**Row** = `Object[11]`: `0` key (`[A-Za-z][A-Za-z0-9._-]{0,79}`, never used inside a UI id), `1` label (max 40), `2` category id,
`3` type, `4` default (canonical text), `5` min, `6` max (`""` = none; int/dec/range: bounds; text: length; items: entry count; table:
bounds of its numeric columns, or 1.1: the text length of a table without int/dec columns, whose min stays `""`), `7` opts, `8` unit (`%`, `coins`, `h`,
`min`, `s`, `ms`, `blocks`, `x`, `""`: the unit the admin types, the code carries and the file stores), `9` flags, `10` help (max 100).
**1.1:** an action row bound with `value=<type>` is `Object[12]`: `11` = the value type (`int`, `dec`, `text`, `bool`, `range`, `color`);
its `4` default is the value used when a caller sends none (a field's start text), `5`/`6`/`8` bound the value like a scalar row of
that type. Every other row stays `Object[11]` exactly as before; a reader that needs only elements 0-10 (SkyyMenu 0.3 checks
`length >= 11`) keeps working.

**Flags:** `live` applies at once, `restart` saved and used after a restart (a `reload:` row or table never runs its reload routine for
its own change, and the mod's reload routine must not apply restart keys it happens to re-read), `new` applies to new things only,
`danger` needs the confirm step, `part` a part switch (a `bool` row that must also carry `danger`, spec 3; confirms only when switched
OFF), `adv` hidden until Advanced is on, `ro` shown, not editable.

**Types and opts:**

| Type | Value text | opts | The mod checks |
|---|---|---|---|
| `bool` | `true` / `false` (typed also on/off/yes/no/1/0) | `01` = the file stores `1`/`0` | the word |
| `int` | plain digits (typed `2k`, `1.5m`, `1,000`, `90s`, `3%` are accepted) | `step=N` | whole, fits a long, min/max |
| `dec` | decimal with `.`, trailing zeros dropped (`0.10` -> `0.1`) | `step=N` | min/max |
| `text` | one line, trimmed | - | length (default max 2000), the mod's own `check=` rule |
| `choice` | one listed value (typed value or label, any case) | `value|Label,value|Label` (each label 1-20 characters) | in the list |
| `items` | `Ore_Iron,Ore_Gold` or `Food_Bread:5` or `Skyy_Sack_*` | `qty` and/or `prefix` | ids exist, qty 1-9999, no duplicates, no lone `*` |
| `range` | `5-10` or `5` (typed `5%-10%`, `5 - 10`) | - | lo <= hi, both within min/max |
| `table` | `""`; entries via `keys`/`tset`/`add`/`remove` | `<valueType>;<none|type|held|both>;<Col1|Col2|Col3>` | per entry |
| `link` | `""` | the command SkyyMenu runs as the admin | - |
| `action` | `""` (1.1 with `value=`: the typed value travels in the `action` op) | the button text | the mod (+ the value like its value type) |
| `color` | `#rrggbb` (the widget is v2) | - | the pattern |

Table extension: `<valueType>` may be one type for every column or one per column joined by `|` (`text|dec|text;both;Category|Base
price|Name`). Column types: `int`, `dec`, `text`, `bool`. Entry keys: 1-120 printable ASCII characters without spaces, `= : # ! [ ] \ |`.
Text columns: at most 200 characters; **1.1:** a table without int/dec columns takes its text length from the row max (a whole number
1-2000, build-checked; 200 when it has no max); its min must stay empty (there is no minimum cell length; the build refuses one). **1.1, 1-column tables:** the value is the one column exactly as typed, `|` included:
never split on `|`, written to the file as is (not through `sep=`), shown and logged whole (e.g. SkyyCollections' 7-field `coll.` lines).
A table with 2-3 columns still joins its columns with `|` in values and maps `|` to `sep=` in the file.

## The op function `config:fn:<Mod>`: `apply(new Object[] { String op, ... })`

`who` = the admin's `UUID`, `name` = their username, `confirm` = `"yes"` or `""`, `via` = `menu`, `command`, `import`, `restore`, `undo`,
+ `console` (the server console, the only via that accepts `who = null`).
**Unknown op or bad argument types -> `null`** (SkyyMenu hides that button). Extensions over the spec are marked +.

| op | Arguments after op | Returns |
|---|---|---|
| `get` | `key` | current value text; `null` = unknown key; `""` for table/link/action rows |
| `set` | `key, value` (`null` = reset to default)`, who, name, confirm, via` | R |
| `keys` | `tableKey, filter` (`""` = all; case-insensitive on entry and values) | `Object[] { String[] entries, String[] labels, String[] values }`, values = columns joined by `|`, max 500; labels = the entry keys (1.1: a key-family entry removed while the list is read is left out, never listed with an empty value) |
| `tset` | `tableKey, entry, value, who, name, confirm` [+ `via`] | R |
| `add` | `tableKey, entry, value, who, name, confirm` [+ `via`] | R |
| `remove` | `tableKey, entry, who, name, confirm` [+ `via`] | R |
| `action` | `actionKey, who, name, confirm` [+ `via`] [+ `value`, 1.1] | R (the mod's own answer). `value` (String) only counts for a `value=` row: validated like a scalar row of its type (`bad` with the reason); `null`/absent = the row default, or `bad` "Type a value for <label> first." when it has none. A plain action ignores it. |
| `reload` | `who, name` [+ `via`] | R; message says how many values were changed by hand |
| `export` | `scope` (`changed` default, `all`) | `String` code; `null` while a file is unreadable |
| `import` | `code, who, name, mode` (`preview` / `apply`) | R; message = the change list (+ skipped keys) |
| `versions` | - | `String[]` newest first, each `id \t file \t time \t who \t summary`, max KEEP per file |
| `restore` | `id, who, name, mode` (`preview` / `apply`) | R; touches only the file the id names |
| `log` | `Integer max` (1-200; any Number) | `String[]` newest first, each `time \t name \t uuid \t via \t key \t old \t new \t status` |
| `status` | - | `String[] { state, message }`: `unreadable` > `unsaved` > `restart` > `ok` |

**Result R** = `Object[] { String status, String value, String message }`:
- `ok` applied now (`value` = the stored canonical value; `message` e.g. `Interest per payout: 3% - saved (applies now).`). Setting a value
  that is already stored answers `ok` with `... is already 3%.` and writes and logs nothing.
- `restart` saved to the file, used after a server restart (also answered by `tset`/`add`/`remove` on a `restart` table).
- `confirm` **nothing changed**; `message` = the question (max 200 characters). Repeat the same call with `confirm = "yes"`.
- `bad` nothing changed; `message` = why (`Must be a whole number from 0 to 100%.`), the typed text stays in the page.
- `denied` `who` lacks the node (write ops only). `error` a file cannot be read or written, or an internal error. `unknown` key.

Which changes ask `confirm` (the mod decides, spec 1.4.2): `danger` rows on any change; `part` rows only when switched OFF; a `danger`
row may narrow that with `confirm=on|off|up|down|always|never` (the build refuses `confirm=` on a row without `danger`, so the published
`danger` flag stays the page's CONFIRM tag); `danger` tables ask for tset/add/remove and `danger` actions always, unless `confirm=never`
(1.1: a value action's question shows the value, `Give XP (250)? <help>`);
a `check=` hook (scalar, table and action rows) may refuse (`bad`) or ask its own question by answering `?<question>`, with or without
`danger`. SkyyMenu itself always confirms import apply, restore apply, undo and every `remove`.

## Guarantees

1. **Never throws.** Write ops turn any `Throwable` into `{ "error", null, "internal error - see the server log" }`; read ops return
   `null`. One warning line either way.
2. **Never calls another Skyy mod** and never writes another mod's bridge keys. The only outside calls are the engine's
   `PermissionsModule.get().hasPermission(who, NODE)` and `Item.getAssetMap().getAsset(id)` (both inside `try`, false on any error).
3. **Never touches ECS, worlds or inventories.** An `action` that needs the world is the mod's own code and schedules itself with
   `world.execute(...)`, answering `ok` with "working on it".
4. **Never writes a file on the caller's thread.** Memory changes at once; the file is written about 500 ms later on
   `HytaleServer.SCHEDULED_EXECUTOR` (one save per burst), atomically. A failed write is retried every 30 s and at shutdown.
5. **Never overwrites an unreadable file.** While a file cannot be read (a folder with its name, a lock, an I/O error) every change to it
   returns `error`, nothing is written, and the log warns once.
6. **Locks** (safe from any thread and inside a caller's own locks, no cycle possible): a bridge caller only ever takes the kit monitor
   (`CfgFile.class`, in-memory state) and the log queue monitor (`CfgLog.class`, a leaf), plus (1.1) the save monitor for the `reload`
   op's read + merge. File I/O happens under that third monitor (`CfgSaveTask.class`), which otherwise only the save task and the mod's
   own `CfgPub.flush/shutdown` take. No mod code (hooks, reload routines, `customGet`/`customSet`, actions) ever runs while a kit
   monitor is held; under the kit monitor the kit only edits its own memory,
   writes `field:` values by reflection and reads the engine's item map. 1.1: the `check=` hooks of hand-edited table lines run after
   the locked part of a save (`CfgSaveTask.saveLocked`, then `CfgFn.handChecks` with no kit lock held) or, for the `reload` op, on the
   caller's thread between the merge and the apply; the kit's own entry / column checks run under the kit monitor (pure kit code), in
   the same monitor hold as the merge (`CfgFile.mergeApply`). 1.1: the `reload` op reads and merges each file under the save monitor
   too (`CfgSaveTask.readMerge`: file I/O and kit memory only), so it waits while a save is writing that file instead of merging the
   older text; the order stays save monitor -> kit monitor -> log monitor, and no mod code runs under any of them. Before the mod's
   reload routines run, `CfgSaveTask.runReloads` takes the save monitor for a moment (`quiet`) so a save that is writing finishes
   first.

## Permission and trust boundary

Every `set`, `tset`, `add`, `remove`, `action`, `reload`, `import` apply and `restore` apply re-checks the mod's own node for `who`.
`who = null` means **the server console** and is accepted only with the explicit `via = "console"` (the mod's console command branch,
`CfgFn.cmdSetConsole`). A `null` with any other `via`, `command` included, is `denied`: a player whose UUID a command handler failed to
resolve is never mistaken for the console. `import` and `restore` apply always need a real `who`. Reads (`get`, `keys`, `versions`,
`log`, `status`, `export`, previews) need no node: SkyyMenu checks `skyymenu.modconfig` through its one `guard()` before every call. The bridge is JVM-wide, so any installed jar can call it with any UUID: the re-check protects against
a stale page, a SkyyMenu bug and an admin who lost the node mid-session, **not** against other server code (every jar is trusted, as on any
Hytale server). Players cannot call Java code, and reads expose nothing beyond the files.

## Inside a mod: adopting the kit

```python
import skyycfg as CFG
kit = CFG.emit(pool, PKG, MOD="SkyyParty", TITLE="Party", VERSION=VERSION, NODE="skyyparty.admin",
               CATS=[("party", "Party")], ROWS=ROWS, FILES=["Skyy_SkyyParty/config.properties"],
               RELOAD=None, KEEP=20, ALIASES=(), DEFAULTS={"config.properties": DEFAULT_TEXT})
# ... compile the rest of the mod ...
kit.write(OUT)      # deferred checks (hook methods exist with the right signature), then writeFile for the 7 kit classes
```

- `setup()`, after the mod's own config load: `PKG.CfgPub.start(getDataDirectory().getParent(), getLogger());`
- `shutdown()`: `PKG.CfgPub.shutdown();` (writes every pending change and log line now; `CfgPub.flush()` does the same any time).
- Admin commands share the menu path (spec 1.4.3): `String msg = PKG.CfgFn.cmdSet(key, typed, uuid, username);` (confirm is implied,
  `via=command`, validated, logged, versioned; a `null` uuid is refused with "Could not tell who sent this command - nothing was
  changed." and one warning) and `PKG.CfgFn.cmdGet(key)`. The command's own console branch, and only it, calls
  `PKG.CfgFn.cmdSetConsole(key, typed)` (`via=console`, logged `by console`). Code in the mod may also call the bridge function.
- Generated classes (in PKG): `CfgRows`, `CfgLog`, `CfgHist`, `CfgSaveTask`, `CfgFile`, `CfgFn`, `CfgPub`. Emit once per package.
- The config class and every `field:`-bound field must exist in the pool **before** `emit()`; hooks may be compiled before or after.
- `DEFAULTS` = the mod's default file texts: used for the `01` build check, to seed a file that is missing when the kit must write it,
  and as the default entries of key-family tables (export `changed`).

**Binding grammar** (the build tuple's last element, index 11; never published):

| Binding | Meaning |
|---|---|
| `field:<Class>.<FIELD>[*<scale>][@<file>[:<fileKey>]]` | `public static volatile` int/long/double/boolean/String. `set` validates in the row's unit, writes the field (x scale) with the primitive `Field` setters, updates the file line (row unit, never scaled), schedules the save. `get` = field / scale. |
| `reload[:<Class>.<method>][@<file>[:<fileKey>]]` | file line only; the routine (default `RELOAD`) runs after the atomic write, outside every kit lock. The mod's loader does unit conversion, so no scale. |
| `custom:<Class>[@<file>[:<k1>,<k2>]]` | the mod's `static String customGet(String key)` and `static Object[] customSet(String key, String value)` returning R, optionally with a 4th element `String[] { fileKey1, value1, fileKey2, value2 }` (value `null` removes the line) that the kit writes through, versions and logs; **1.1:** when at least one such line is taken, the mod's `RELOAD` runs after the atomic write (not for a `restart` row or a `restart` answer), so a mod no longer arms it by hand. Optional `static String customRead(String key, java.util.Map fileValues)` makes the row restorable. A custom **table** also needs `static String[] customKeys(String tableKey)`; its entries are addressed as `tableKey[entry]` (its file lines run `RELOAD` the same way). |
| `action:<Class>.<method>` | `static Object[] method(java.util.UUID who, String name)` returning R; **1.1** with `;value=<type>`: `static Object[] method(java.util.UUID who, String name, String value)` (the canonical typed value) |
| `none` / `""` | link rows |

Options appended with `;`: `after=<Class>.<m>` (`static void m(String key)` after a `field:` set), `check=<Class>.<m>` (`static String
m(String key, String value)`: `null` = fine, text = refuse with that reason, `?text` = ask that question first; tables pass
`tableKey[entry]` and `null` for a removal, **1.1** also for every hand-edited line (a `?text` answer counts as fine there: nobody to
ask); **actions** pass the action key and `null` (1.1: the canonical typed value for a `value=` action), before the confirm step, so a
refusal stops the action), `confirm=on|off|up|down|always|never` (only on a `danger` row: `on`/`off` for `bool` rows, `up`/`down` for
`int`/`dec` rows, `always`/`never` for any row; tables and actions take `always`/`never` only), `sep=<c>` (a table's column separator in
the file, default `,`; a 1-column table never uses it), `entry=key|item|itemprefix` (table entries must be item ids, or ids /
`Prefix*`), **1.1** `value=int|dec|text|bool|range|color` (action rows only: the action takes a typed value of that type, bounded by
the row's min / max / unit, default = the row default; `choice` and `items` are not possible because an action's opts is its button
text). `<Class>` = a simple name in PKG or a full
name; `<file>` = a path under `mods/` or the unique end of one `FILES` entry. Defaults: file = `FILES[0]` (a `custom:` row in a mod with
more than one file must name its file), fileKey = the row key, a table's prefix = the row key + `.`. A table binds
`reload@<file>:<prefix>`: every line `<prefix><entry>=<col1><sep><col2>...` is an entry (an empty prefix owns the whole file). **One owner
per file key:** two rows never bind the same key of one file, two table prefixes in one file never overlap (`combat.` and `combat.role`),
and no scalar or `custom:` file key lies inside a table's family.

**Build checks** (emit fails the build): header limits; keys valid and unique; labels <= 40, help <= 100, choice labels 1-20 (spec 2.5
widths); category ids exist; flags known; a `part` row is `bool` and carries `danger`; units known; min/max numeric and ordered; opts
valid per type; `confirm=` only on `danger` rows and only in the forms above; the default passes its own row (item ids against
`Assets.zip` when found); choice defaults in the list; a `custom:` row names its file when there are several `FILES`; one owner per file
key (above); every `field:` names a `public static volatile`, non-final field of a type the row may bind; the **unit rule**: a numeric
field named `*_MS` (or just `MS`), `*Ms` (camelCase), `*MILLIS` or `*Millis` must be bound with unit `ms` and no scale, `s` with
`*1000`, `min` with `*60000` or `h` with `*3600000`, a row with unit `ms` must bind such a field, any other scale fails, an int field
needs min and max, and `max x scale` must fit the field; a `bool` row whose file key the default file writes as `1`/`0` needs opts
`01`; hooks, reload routines and custom methods exist with the right signature (at `kit.write`; a `value=` action's method takes the
third `String`). 1.1: `value=` only on action rows and only with `int`, `dec`, `text`, `bool`, `range` or `color`; a value action's
default passes its value type and bounds (a text value's min / max are whole lengths); a plain action or link row keeps an empty
default; a table without int/dec columns has no max or a whole max 1-2000 (its text length) and no min. + Spec 2.12 words the unit rule as
"ends in `_MS`, `MS` or `MILLIS`"; the kit does not treat a bare trailing `MS` after a letter as milliseconds, because plural names
(`MAX_ITEMS`, `DEFAULT_TEAMS`) end in those letters, and it adds the camelCase forms the codebase also uses.

## Files: write-through, hand edits, history, log

- **Line-preserving write (spec 1.4.4).** Only the changed key's lines change: its value is replaced on every live line of that key
  (the last one wins when the mod reads the file) and continuation lines are dropped; else a template line `#key=value` / `# key=value`
  whose value is one token is uncommented in place (a doc comment with spaces in its text is never touched); else the line is appended
  under one `# ---- changed in game (SkyWynn Menu) ----` header. Values and keys are escaped the `java.util.Properties` way with every
  non-ASCII character as `\uXXXX`, so ISO-8859-1 and UTF-8 readers see the same value. Comments, blank lines, order and line endings (LF
  or CRLF) are kept byte for byte. Atomic write: tmp file, fsync, `ATOMIC_MOVE` + `REPLACE_EXISTING` (plain replace fallback), 5 x 20 ms
  retries on `FileSystemException`.
- **Hand edits.** Before each write the kit compares the file's modified time and size with what it last read or wrote. If they differ it
  re-reads the file, logs every changed **bound** key `via=file` (unbound keys, e.g. a counter the mod writes itself, are merged silently),
  applies them (the mod's `RELOAD`, or for mods without one the kit sets `field:` rows itself and clamps like a loader; `restart` rows and
  tables are only logged and wait for the next start), then applies the
  pending in-game changes on top (a key edited both ways keeps the in-game value; the hand edit is logged `overridden`). A hand edit is
  never lost. The `reload` op does the same at once (read on the caller's thread, merge in memory; the save task writes and runs the
  routines).
- **1.1: hand-edited table lines** (a `reload:` key-family table) get the same checks as `tset`/`add`/`remove`: the entry key (and
  `entry=item`), the column count, types and bounds, the text length, no `|` typed into a 2-3 column line (the kit never writes one
  there; the mod's loader splits on `sep=`), then the row's `check=` hook with `tableKey[entry]` and the
  canonical columns (`null` for a removed line). A line that passes is logged `ok` and runs the row's reload routine (not for a
  `restart` table). A refused line is logged `invalid` (`tableKey[entry] \t <value memory keeps> \t <typed value> \t invalid`), **memory
  keeps the old value** (what `keys`, export, import / restore compares and the restart status see; a refused new entry stays absent, a
  refused removal stays listed), no reload routine runs for it, and the file keeps the typed line. A line that waits for its `check=`
  hook is held the same way until the hook accepts it (memory never shows a value that has not passed), and a hook answering after a
  newer change of the entry (an in-game edit, a newer hand edit) changes nothing in memory; its log line still records the verdict. The old value is held until that
  entry changes again (an in-game `tset`/`add`/`remove`, an import or restore of it, or a later hand edit that passes) or the server
  restarts (the kit does not check lines at start; the mod's own loader decides what a bad line means). Undo is not offered on `invalid`
  lines. Scalar `reload:` rows are unchanged (logged `ok`, the mod's loader clamps).
- **Clamps (spec 1.4.2).** Typed values are rejected, never clamped. Values read from a file are clamped as the mod's loader does; at start
  and after a `RELOAD` run the kit logs every `field:` row whose file text differs from the running value `status=clamped` (once per value).
- **Versions (spec 1.4.5).** Before every write the file as it is on disk is copied to
  `Skyy_<Mod>/config-history/<fileId>.<yyyyMMdd-HHmmss-SSS>.bak` (`fileId` = its path under `mods/` with `/` -> `~`), skipped when equal to
  that file's newest copy, and `id \t file \t time \t who \t summary` (`id = <fileId>#<stamp>`) is appended to `config-history/index.log`.
  The newest KEEP (default 20) per file are kept. One change touching several files (an import) makes one version per file with the same
  stamp. `restore` diffs a copy against the current values of the rows bound to that one file and applies the differences through the
  normal path as one batch (`via=restore`), which makes its own version, so a restore can be undone the same way. Rows that do not validate
  in this version are kept and listed; custom rows without `customRead` and custom tables are not restored (listed).
- **Change log (spec 1.4.6).** `Skyy_<Mod>/config-changes.log`, UTF-8, one line per change:
  `2026-09-24T21:40:12 \t Skyy \t <uuid or -> \t menu \t bank.interestPercent \t 2 \t 3 \t ok`, plus one server INFO line
  `[SkyyEconomy] config bank.interestPercent 2 -> 3 by Skyy (menu)`. Tabs and line breaks inside values become spaces. Table lines use
  key `tableKey[entry]`, the columns joined by `|` (1.1: a 1-column value whole, `|` included), and `(none)` for the side that does not
  exist, so the inverse op (`add` <-> `remove`, `tset` with the old columns) restores an entry exactly. An action logs old `""` and new
  `(action)`; **1.1:** a `value=` action logs its canonical value in the old column (new stays `(action)`, status `done`), so a Changes
  view that knows `(action)` keeps working. Status values: `ok`, `restart`, `done` (actions), `clamped`, `invalid` (a hand
  edit the kit could not use; 1.1 also a table line its checks refused), `overridden`, `file` (a hand edit of a custom row's file key).
  SkyyMenu offers Undo only on `ok` lines.
  Lines are queued in memory and appended by the save task; the file rotates at 1 MB, keeping 3 old files.

## Export and import codes (spec 1.4.7)

`SKYY1.<Mod>.<base64url(deflate(utf8 text)) without padding>.<crc32 of the utf8 text, 8 hex digits>`. Deflate is the zlib format
(`java.util.zip.Deflater`, Python `zlib.compress`). The text is `key=value` lines of row keys plus `_mod=`, `_ver=`, `_date=`; a table is
carried as `_table=<key>` followed by `<key>[<entry>]=<cols>` lines, and **a code that carries a table replaces that whole table** on import.
Scope `changed` = only values that differ from the default (a key-family table only when its entries differ from the `DEFAULTS` file).
`ro`, link and action rows are never exported. Import checks the code shape, the mod name (or one of the mod's `ALIASES`, e.g. SkyyEconomy
accepting SkyyBank codes), the checksum and `_mod=`; validates **every** value (including `check=` hooks) before anything changes; lists and
skips unknown or read-only keys; `preview` returns the change list, `apply` applies it in one batch (`via=import`). A code never holds
player data. White space pasted into a code is ignored.

## Failure modes

| Situation | What happens |
|---|---|
| SkyyMenu missing or older than 0.3 | Nothing visible changes; admin commands work through `cmdSet` (now logged and versioned). |
| A config file unreadable | `status = unreadable` with the file name; every change to that file returns `error`; the file is never written; one warning. Other files keep working. Fix or delete it, then Reload. |
| A write fails (e.g. a Windows handle without delete sharing) | Memory keeps the change, `status = unsaved`, retried every 30 s and at shutdown, one warning. Further changes are accepted. |
| A file is missing when the kit must write | It is created from the `DEFAULTS` text plus the change. |
| Two admins change the same key | Last one wins; both are logged. |
| A mod hook throws | Caught; `error` (or `bad` for a `check=` hook) with "see the server log". A hand-edited table line whose `check=` hook throws is logged `invalid` (1.1). |
| A hand-edited table line fails its checks (1.1) | Logged `invalid`; memory keeps the old value; the file keeps the line; no reload for it. Fix the line (or set the entry in game), then Reload. |
| A reload routine is due while another file of the mod has unsaved in-game changes (1.1) | That file is written first, then the routine runs once for both. If it cannot be written (a failed write, `status = unsaved`), the routine reads its old text, so the kit then sets that file's pending `field:` values again (no `clamped` line); the 30 s retry writes the file. |
| A value action is called without a value (SkyyMenu 0.3 / 0.3.1) (1.1) | The row default is used; without a default the answer is `bad` "Type a value for <label> first." |
| Bare JVM (no HytaleServer) | Saves run on a daemon fallback thread instead of the scheduler (test harness only). |

## Known limits of v1 (kit 1.1)

- Hand edits are noticed at the kit's next write of that file or on `reload`, not by polling (no periodic work, by rule).
- **SkyyMenu 0.3's table editor (kept as is in 0.3.1) splits every value on `|` into its column cells and caps a cell at 200
  characters**, whatever the
  kit accepts. A 1-column table whose values hold `|` or more than 200 characters (1.1) must therefore wait for a SkyyMenu whose table
  view keeps a 1-column value whole and uses the row max as the cell length: with SkyyMenu 0.3, Set on such a row would send only the
  first `|` field. Until then bind such lines read-only or leave them to the file + Reload (the kit now checks those hand edits).
- **Value actions (1.1)** are drawn by SkyyMenu 0.3 / 0.3.1 as a plain button that sends no value, so they run with the row default
  (or answer "Type a value ... first."); a typed-value field needs the next SkyyMenu (send the text as the 7th `action` argument and
  pre-fill it with row element 4). No live mod publishes one yet.
- A refused hand-edited table line's held old value lives in memory only: after a restart the kit shows the line as it is in the file.
- A hand edit of a `custom:` **table**'s lines is neither logged nor applied by the kit (`rowFor` maps file keys only to scalar rows and
  `reload:` key-family tables, so those lines count as unbound and are merged silently): only the mod's own reader applies it, and
  Changes / Undo never show it (the file copy in History still holds it after the kit's next write). Example: SkyyMenu's
  `settings.defaults` in `settings-defaults.properties`, applied by SkyyMenu's 30 s re-read. A scalar `custom:` row's listed file keys
  (SkyyMenu's `menu.tooltips`) are logged `file` as usual. Adopters that need an audited table bind it `reload:`.
- An import apply is all or nothing for `field:`/`reload:` rows and key-family tables; a `customSet` may still refuse after the others
  were applied (answered `error` "Imported with problems").
- `color` has no widget yet; `link` rows are drawn by SkyyMenu only.
- Mods adopting the kit must keep their config fields `public static volatile` and their reload routines free of world access (or wrap
  it in `world.execute`), and must not keep whole-file writers that rewrite a file the kit also writes.
- Every installed jar is trusted (see the trust boundary).
