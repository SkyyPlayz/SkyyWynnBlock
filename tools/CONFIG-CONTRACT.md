# SkyWynn admin config contract (v1, 2026-09-25)

Skyy's direction: **everything a server owner might change must be doable in game**, and the game and the files always agree.
Each Skyy mod keeps owning its settings and its own files. It describes them once (a schema) and puts that description plus one
function on the bridge. SkyyMenu 0.3 (the Mods section, `/modconfig`) only draws pages and passes clicks back. Without SkyyMenu nothing
changes: the mod still reads its files and its admin commands still work.

Source of truth: `research/Server-Setup-Spec.md` sections 1.3-1.4 and 6. Implementation: `tools/skyycfg.py` (a code generator every
build script imports, so each jar carries its own copy). Proof: `python tools/skyycfg_test.py` (bare JVM, spec 8.2 a-j, 8.1.3, 8.1.4).
The player Settings registry (`settings:*`, research/Settings-Spec.md) is a separate twin with the same key, page and never-throws rules.

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
| 7 | Object[] | rows, each `Object[11]` of Strings, display order |
| 8 | String | files, comma list relative to the world's `mods/` folder |
| 9 | String | note, max 100 characters |

**Row** = `Object[11]`: `0` key (`[A-Za-z][A-Za-z0-9._-]{0,79}`, never used inside a UI id), `1` label (max 40), `2` category id,
`3` type, `4` default (canonical text), `5` min, `6` max (`""` = none; int/dec/range: bounds; text: length; items: entry count; table:
bounds of its numeric columns), `7` opts, `8` unit (`%`, `coins`, `h`, `min`, `s`, `ms`, `blocks`, `x`, `""`: the unit the admin types,
the code carries and the file stores), `9` flags, `10` help (max 100).

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
| `action` | `""` | the button text | the mod |
| `color` | `#rrggbb` (the widget is v2) | - | the pattern |

Table extension: `<valueType>` may be one type for every column or one per column joined by `|` (`text|dec|text;both;Category|Base
price|Name`). Column types: `int`, `dec`, `text`, `bool`. Entry keys: 1-120 printable ASCII characters without spaces, `= : # ! [ ] \ |`.

## The op function `config:fn:<Mod>`: `apply(new Object[] { String op, ... })`

`who` = the admin's `UUID`, `name` = their username, `confirm` = `"yes"` or `""`, `via` = `menu`, `command`, `import`, `restore`, `undo`,
+ `console` (the server console, the only via that accepts `who = null`).
**Unknown op or bad argument types -> `null`** (SkyyMenu hides that button). Extensions over the spec are marked +.

| op | Arguments after op | Returns |
|---|---|---|
| `get` | `key` | current value text; `null` = unknown key; `""` for table/link/action rows |
| `set` | `key, value` (`null` = reset to default)`, who, name, confirm, via` | R |
| `keys` | `tableKey, filter` (`""` = all; case-insensitive on entry and values) | `Object[] { String[] entries, String[] labels, String[] values }`, values = columns joined by `|`, max 500; labels = the entry keys |
| `tset` | `tableKey, entry, value, who, name, confirm` [+ `via`] | R |
| `add` | `tableKey, entry, value, who, name, confirm` [+ `via`] | R |
| `remove` | `tableKey, entry, who, name, confirm` [+ `via`] | R |
| `action` | `actionKey, who, name, confirm` [+ `via`] | R (the mod's own answer) |
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
`danger` flag stays the page's CONFIRM tag); `danger` tables ask for tset/add/remove and `danger` actions always, unless `confirm=never`;
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
   (`CfgFile.class`, in-memory state) and the log queue monitor (`CfgLog.class`, a leaf). File I/O happens under a third monitor
   (`CfgSaveTask.class`) that only the save task and the mod's own `CfgPub.flush/shutdown` take. No mod code (hooks, reload routines,
   `customGet`/`customSet`, actions) ever runs while a kit monitor is held; under the kit monitor the kit only edits its own memory,
   writes `field:` values by reflection and reads the engine's item map.

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
| `custom:<Class>[@<file>[:<k1>,<k2>]]` | the mod's `static String customGet(String key)` and `static Object[] customSet(String key, String value)` returning R, optionally with a 4th element `String[] { fileKey1, value1, fileKey2, value2 }` (value `null` removes the line) that the kit writes through, versions and logs. Optional `static String customRead(String key, java.util.Map fileValues)` makes the row restorable. A custom **table** also needs `static String[] customKeys(String tableKey)`; its entries are addressed as `tableKey[entry]`. |
| `action:<Class>.<method>` | `static Object[] method(java.util.UUID who, String name)` returning R |
| `none` / `""` | link rows |

Options appended with `;`: `after=<Class>.<m>` (`static void m(String key)` after a `field:` set), `check=<Class>.<m>` (`static String
m(String key, String value)`: `null` = fine, text = refuse with that reason, `?text` = ask that question first; tables pass
`tableKey[entry]` and `null` for a removal; **actions** pass the action key and `null`, before the confirm step, so a refusal stops the
action), `confirm=on|off|up|down|always|never` (only on a `danger` row: `on`/`off` for `bool` rows, `up`/`down` for `int`/`dec` rows,
`always`/`never` for any row; tables and actions take `always`/`never` only), `sep=<c>` (a table's column separator in the file,
default `,`), `entry=key|item|itemprefix` (table entries must be item ids, or ids / `Prefix*`). `<Class>` = a simple name in PKG or a full
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
`01`; hooks, reload routines and custom methods exist with the right signature (at `kit.write`). + Spec 2.12 words the unit rule as
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
  key `tableKey[entry]`, the columns joined by `|`, and `(none)` for the side that does not exist, so the inverse op (`add` <-> `remove`,
  `tset` with the old columns) restores an entry exactly. Status values: `ok`, `restart`, `done` (actions), `clamped`, `invalid` (a hand
  edit the kit could not use), `overridden`, `file` (a hand edit of a custom row's file key). SkyyMenu offers Undo only on `ok` lines.
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
| A mod hook throws | Caught; `error` (or `bad` for a `check=` hook) with "see the server log". |
| Bare JVM (no HytaleServer) | Saves run on a daemon fallback thread instead of the scheduler (test harness only). |

## Known limits of v1

- Hand edits are noticed at the kit's next write of that file or on `reload`, not by polling (no periodic work, by rule).
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
