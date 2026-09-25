# Player Settings menu: build spec (SkyyMenu 0.2 + adoption in every Skyy mod)

*Written 2026-09-24 by the research workflow `skywynn-settings-spec`. Research only: no build script, mod folder or game file was changed.*
*Builds on `SkyyMenu/build_skyymenu_0.1.2.py` (live) and on the newest build script of every other Skyy mod (listed in section 3). Owner: Skyy (they/them).*

**Skyy's ask (2026-09-24, looking at the SkyWynn Menu):** "id add a settings menu where you can adjust all the settings like chat notifications for different things."

**Legend.** VERIFIED = seen in `HytaleServer.jar` / `Assets.zip` (read-only), in a verified-in-game page of ours, or in our own scripts. UNVERIFIED = design that still needs the tests in section 5. `[SKYY?]` = a choice Skyy should confirm.

---

## 0. Verdict (plain words)

**It can be built in one round, and no mod depends on another.** SkyyMenu 0.2 owns the Settings page, a `/settings` command and a small **settings registry** on the `skyy.bridge` map. Every other mod does two small things. It **registers** its switches at startup, and it **asks** before sending a message ("is `skills.xpGain` on for this player?"). If SkyyMenu is missing, the question has no answer and the mod behaves exactly as it does today.

| Piece | Where | Size |
|---|---|---|
| Registry + per-player storage + 3 bridge functions | SkyyMenu 0.2 (`SetReg`, `SetStore`, `SetGetFn`, `SetRegFn`, `SetSetFn`) | ~250 lines of Java |
| Settings page (8 tabs, ON/OFF rows, reset) + `/settings` + a Settings icon in the menu | SkyyMenu 0.2 (`SettingsPage`, `SettingsCmd`, one MENU DATA entry) | ~200 lines |
| Adoption: 1 check helper + registration + 1-3 line gates per message | 12 mods (section 3) | 10-40 lines each |

**What players get:** 28 switches now (4 more arrive with SkyyExploration and SkyyIslands 0.5.x) in 8 SkyBlock-like tabs. Every switch defaults to **ON**, so nothing changes until a player turns something off. Settings are **per player**: the same on every profile.

**What stays on no matter what:** replies to your own commands and clicks, anything that takes something from you or changes you (death coin loss, admin class changes, crash repairs, items dropped after a switch), setup you must finish (create a profile, pick a class), one-time notices, and the "profile changed" page banners. Section 2.3 lists them all with reasons.

**VERIFIED building blocks:**
- `/settings` is free as a top-level command. Vanilla `WorldSettingsCommand` is named `settings` (alias `ws`), but only `WorldCommand` references it, so it is the `/world settings` subcommand. No Skyy build script registers a `settings` command today. SkyyIslands 0.5 plans `/island settings`, a subcommand, so there is no clash.
- A 1120 px wide page renders: SkyyCollections 0.2 uses 1120 x 840 ("this is beautiful!"). A 952 px tall page renders: SkyyMenu 0.1.2.
- ON/OFF rows are proven: SkyyHud 0.3.6 `WidgetsPage` has a label + `ON` + `OFF` TextButton per row, with the active button green. Skyy called it "beautiful".
- Opening one page straight from another page's click handler, without closing first, is proven: SkyyHud `WidgetsPage` -> `SettingsPage` -> `EditorPage`.
- Dynamic ids with an index suffix plus `b.set("#Id.Text", v)` on labels appended in the same build are proven: SkyyCollections `SkyyCCatFound<i>`.
- Icon items exist with icon files in `Assets.zip`: `Furniture_Crude_Torch` (`Icons/ItemsGenerated/Furniture_Crude_Torch.png`) and `Deco_Lever`. SkyBlock's Settings icon is a Redstone Torch, so the torch is the match.

---

## 1. Architecture

### 1.1 What the references do (short)
- **Hypixel SkyBlock:** Settings sits in the SkyBlock Menu (a Redstone Torch in the bottom row, also `/viewsettings`). It is a categorized click menu: Personal (Sounds, User Interface, **Chat Feedback**, Fishing), **Comms** (invites and alerts from other players, trade requests), Island Settings, API, and more. The notification switches live in Chat Feedback (ability messages, mining feedback, the famous **sack notifications**) and in Comms (who may invite or message you). Sources: hypixelskyblock.minecraft.wiki/w/Settings, /w/Settings/UI, hypixel-skyblock.fandom.com/wiki/Settings, the hypixel.net "Sack notifications" thread.
- **Wynncraft:** no menu. It has a flat list of `/toggle <name>` commands (`music`, `popups`, `guildjoin`, `100`, `bombbell`, `pouchmsg`, ...). Players on its forum ask for a real options menu. Sources: wynncraft.wiki.gg/wiki/Commands, forums.wynncraft.com "Options Menu".
- **Our choice:** SkyBlock's structure (a menu icon, tabs by game area, one row per message type), with the Comms idea folded into the General tab. Some General switches **refuse** the other player instead of just hiding the line (party invites, teleport requests, private messages). Otherwise the other player waits or keeps writing to someone who never sees it.

### 1.2 Ownership and the bridge contract

SkyyMenu 0.2 puts three `java.util.function.Function` objects on the bridge in `setup()`. It never removes them, the same rule as `profile:fn:key`. Arguments are always `Object[]` of `java.lang` types. Never pass a mod's own classes across the bridge: each mod has its own classloader.

| Bridge key | Call | Returns | Notes |
|---|---|---|---|
| `settings:fn:register` | `apply(new Object[] { String mod, String key, String label, String category, Boolean def, String help })` | `Boolean.TRUE` accepted, `FALSE` rejected (bad key or too few elements) | Idempotent. The same mod registering again updates label and help. A different mod registering the same key (shared keys such as `rewards.late`) is accepted, and the first registration's values are kept. If the defaults differ, the log warns once. `help` (element 5) is optional. |
| `settings:fn:get` | `apply(new Object[] { UUID player, String key })` | `Boolean`: the player's choice, else the admin default, else the registered default. `null` = unknown key and no stored value | This is the only call on hot paths. Lock-free after the first read of that player (section 1.4). |
| `settings:fn:set` | `apply(new Object[] { UUID player, String key, Boolean value })` or `{ ..., Boolean onlyIfUnset }` | `TRUE` = the stored state now matches the request: written, or skipped because `onlyIfUnset` and the player already chose. `FALSE` = could not be saved (settings file unreadable, bad args) | Used by migrations and the `/skills quiet`, `/tree quiet` shortcuts. |
| `settings:def:<key>` | plain value `Object[]` (the same 6 elements as register) | - | **Load-order fallback.** Every adopter writes it at setup, whether or not SkyyMenu is loaded. SkyyMenu drains every `settings:def:*` key right after it puts its functions, and again on each page build. `fn:get` also looks it up lazily for an unknown key. So plugin load order never matters. |

**Key format:** `[a-z][A-Za-z0-9.]{2,47}`, for example `skills.xpGain`. Keys go into properties files, so no `=`, `:` or spaces.
**Category ids** (element 3): `skills`, `collections`, `sacks`, `combat`, `coins`, `profiles`, `cooking`, `general`. An unknown id goes to `general`.
**Labels** are clipped to 48 characters and help lines to 100. They are shown with `b.set(...)`, so any character is safe.

**Guarantees** (write them into a later `tools/SETTINGS-CONTRACT.md`, the PROFILES-CONTRACT style):
1. Never throws. Bad input gives `null` / `FALSE`.
2. Never calls another mod, never writes the bridge from `get`/`set`, never touches ECS or inventories. It holds only its own `SetStore.class` monitor, and only around its own file I/O. So calling it from inside your own locks is safe and no lock cycle is possible. SkyyEssentials `prune()` is `synchronized` on `EssStore.class` and will call it.
3. Safe from any thread. After a player's file is loaded, `get` is two `ConcurrentHashMap` reads plus a `HashMap` read, with no lock and no I/O. The first `get` for a player in this JVM reads one small file (a few ms). SkyyMenu preloads it at PlayerReadyEvent on the scheduler, so world threads practically never do it.
4. `set` updates memory at once and saves 500 ms later on `HytaleServer.SCHEDULED_EXECUTOR` (atomic write, section 1.4). It never writes files on the caller's thread.

### 1.3 The adopter helper (one per mod, javassist-safe)

Each mod adds these two static methods to the class that already has its `bridge()` helper (section 3 names it per mod). Write them in that script's token style (`{PKG}` f-strings or `@PKG@`).

```java
// Settings registry (SkyyMenu 0.2+, research/Settings-Spec.md). No SkyyMenu = no answer = today's behaviour (on).
public static boolean notifyOn(java.util.UUID u, String key) {
  if (u == null || key == null) return true;
  try {
    Object f = bridge().get("settings:fn:get");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(new Object[] { u, key });
      if (r instanceof Boolean) return ((Boolean) r).booleanValue();
    }
  } catch (Throwable t) { }
  return true;
}
public static void regSetting(String key, String label, String cat, boolean def, String help) {
  try {
    Object[] a = new Object[] { "SkyyXxx", key, label, cat, Boolean.valueOf(def), help };   // SkyyXxx = this mod's name
    java.util.Map br = bridge();                        // must be a CREATING bridge() (see SkyySacks note in 3.4)
    br.put("settings:def:" + key, a);
    Object f = br.get("settings:fn:register");
    if (f instanceof java.util.function.Function) ((java.util.function.Function) f).apply(a);
  } catch (Throwable t) { }
}
```

Rules for every gate:
- **Gate only the `sendMessage` / popup call.** Never gate the work: payments, throttle timers, "told" latches, logs, XP, drops and cancels all run as before. This matters where a latch sits in the same condition (SkyySacks `fuelWarnOnce()`): keep the latch call first and put the setting check after `&&`, so the latch is still used.
  **The one deliberate exception:** the three refusing General switches (`party.invites`, `tpa.requests`, `msg.private`, sections 1.1 and 3.11) stop the invite, request or message itself. That goes further than "chat notifications", so those three rows are built only after Skyy confirms the refuse behaviour (section 6, first `[SKYY?]`). Section 6 also gives the hide-only version to build if Skyy says no.
- **Put the check before the message's own throttle timestamp** when the throttle exists only for that message (Classes `WARNED`/`POPPED`, Cooking `LAST`). A hidden line then does not use up the cooldown of a line that is shown.
- **Admin master switches stay and win.** A line is sent only if the server config allows it AND the player's setting is on: `xp.properties feedback=`, `perk.doubleDropMessage=`, `cooking.properties messages=`.
- Registration happens in the plugin's `setup()`, one `regSetting(...)` per key, with the exact label, category, default and help from section 2.

### 1.4 SkyyMenu internals (0.2)

New classes in `com.skyy.menu`. They are listed in the order methods must be added (javassist, no forward references):

| Class | Role |
|---|---|
| `MenuUtil` (existing) | + `atomicWrite(Path, byte[])`: copy `ProfCfg.atomicWrite` from `build_skyyprofiles_0.1.py` verbatim (tmp, fsync, `ATOMIC_MOVE`+`REPLACE_EXISTING`, fallback to plain replace, 5 x 20 ms retries on `FileSystemException`). |
| `SetReg` | The registry. Fields first (javassist: every field before the methods that use it): `DEFS` (`ConcurrentHashMap` key -> `Object[6]`), `WARNED` (`ConcurrentHashMap` key -> `Boolean`, the one-time "conflicting default" warning in `register`, like the SkyyClasses `ClassRules.WARNED` field), `ADMIN` (`volatile HashMap` key -> `Boolean`, replaced wholesale), `ADMIN_FILE` (`java.nio.file.Path`, set in `setup()`), `ADMIN_MTIME` (`volatile long`, the `lastModified` that `loadAdmin` last read). Then the methods: `validKey`, `clip`, `catIndex`, `register(Object)` (`synchronized`), `drain()`, `def(String)`, `info(String)`, `rank(String)`, `keysOf(int cat)`, `loadAdmin(boolean first)`. |
| `SetStore` | Per-player values. `DIR`, `VALS` (`ConcurrentHashMap` uuid string -> `HashMap`, copy-on-write), `BROKEN` (uuid string -> `Long` time of the failed read), `DIRTY`, `NAMES`. Methods `fileOf`, `load` (`synchronized`), `isBroken`, `get`, `saveNow` (`synchronized`). |
| `SetSaveTask` | `Runnable(String k)` -> `SetStore.saveNow(k)`. |
| `SetStore` (cont.) | `saveSoon`, `set` (`synchronized`), `resetAll` (`synchronized`), `retryDirty`, `pruneOffline(java.util.Set onlineUuidStrings)`, `flushAll`. |
| `SetLoadTask` | `Runnable(String k)` -> `SetStore.load(k)` (the preload). |
| `SetGetFn`, `SetRegFn`, `SetSetFn` | The three bridge Functions. |
| `SettingsPage` | The page (section 4). Add its fields + constructor right after the `MenuPage` constructor, because `MenuPage.openSettings` and `SettingsPage`'s "< SkyWynn Menu" button reference each other. This is the SkyyHud `SettingsPage`/`EditorPage` pattern: constructors first, methods after. |
| `SettingsCmd` | `/settings` (alias `/skysettings`). |

Core Java (javassist-safe; `MenuData`/`MenuUtil`/`SetReg`/`SetStore` carry the `@PKG@.` prefix in the script):

```java
// ---- SetReg fields (one CtField.make each, before any SetReg method)
public static final java.util.concurrent.ConcurrentHashMap DEFS = new java.util.concurrent.ConcurrentHashMap();
public static final java.util.concurrent.ConcurrentHashMap WARNED = new java.util.concurrent.ConcurrentHashMap();
public static volatile java.util.HashMap ADMIN = new java.util.HashMap();
public static java.nio.file.Path ADMIN_FILE = null;
public static volatile long ADMIN_MTIME = -1L;
// ---- SetReg methods
public static boolean validKey(String k) {
  if (k == null || k.length() < 3 || k.length() > 48) return false;
  char c0 = k.charAt(0);
  if (c0 < 'a' || c0 > 'z') return false;
  for (int i = 0; i < k.length(); i++) {
    char c = k.charAt(i);
    if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '.')) return false;
  }
  return true;
}
public static String clip(Object o, int max) {
  if (o == null) return "";
  String s = String.valueOf(o).replace('\n', ' ').replace('\r', ' ').trim();
  return s.length() > max ? s.substring(0, max) : s;
}
public static int catIndex(String c) {
  for (int i = 0; i < MenuData.SET_CAT_ID.length; i++) if (MenuData.SET_CAT_ID[i].equals(c)) return i;
  return MenuData.SET_CAT_ID.length - 1;                 // "general" is the last tab
}
public static synchronized boolean register(Object o) {
  try {
    if (!(o instanceof Object[])) return false;
    Object[] a = (Object[]) o;
    if (a.length < 5) return false;
    String key = a[1] == null ? null : String.valueOf(a[1]);
    if (!validKey(key)) return false;
    String mod = clip(a[0], 32);
    String label = clip(a[2], 48);
    if (label.length() == 0) label = key;
    String cat = MenuData.SET_CAT_ID[catIndex(a[3] == null ? "" : String.valueOf(a[3]))];
    Boolean def = a[4] instanceof Boolean ? (Boolean) a[4] : Boolean.TRUE;
    String help = a.length > 5 ? clip(a[5], 100) : "";
    Object[] old = (Object[]) DEFS.get(key);
    if (old != null && !mod.equals(old[0])) {
      if (!def.equals(old[4]) && WARNED.putIfAbsent(key, Boolean.TRUE) == null)
        MenuUtil.warn("setting " + key + ": " + mod + " wants default " + def + ", " + old[0] + " registered " + old[4] + " first - keeping " + old[4]);
      return true;
    }
    DEFS.put(key, new Object[] { mod, key, label, cat, def, help });
    return true;
  } catch (Throwable t) { return false; }
}
public static void drain() {
  try {
    java.util.Iterator it = MenuUtil.bridge().entrySet().iterator();
    while (it.hasNext()) {
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      Object k = e.getKey();
      if (k instanceof String && ((String) k).startsWith("settings:def:")) register(e.getValue());
    }
  } catch (Throwable t) { MenuUtil.warn("settings drain failed: " + t); }
}
public static Object[] info(String key) {
  Object[] d = (Object[]) DEFS.get(key);
  if (d == null) {
    Object v = MenuUtil.bridge().get("settings:def:" + key);
    if (v != null && register(v)) d = (Object[]) DEFS.get(key);
  }
  return d;
}
public static Boolean def(String key) {
  Object a = ADMIN.get(key);
  if (a instanceof Boolean) return (Boolean) a;
  Object[] d = info(key);
  return d == null ? null : (Boolean) d[4];
}
public static int rank(String key) {
  for (int i = 0; i < MenuData.SET_ORDER.length; i++) if (MenuData.SET_ORDER[i].equals(key)) return i;
  return 9000;
}
public static String[] keysOf(int cat) {
  String id = MenuData.SET_CAT_ID[cat];
  java.util.ArrayList rows = new java.util.ArrayList();
  java.util.Iterator it = DEFS.values().iterator();
  while (it.hasNext()) {
    Object[] d = (Object[]) it.next();
    if (id.equals(d[3])) rows.add(String.valueOf(10000 + rank((String) d[1])) + "\t" + (String) d[1]);
  }
  java.util.Collections.sort(rows);
  String[] out = new String[rows.size()];
  for (int i = 0; i < out.length; i++) { String s = (String) rows.get(i); out[i] = s.substring(s.indexOf('\t') + 1); }
  return out;
}

// ---- SetStore
public static synchronized java.util.HashMap load(String k) {
  Object m = VALS.get(k);
  if (m != null) return (java.util.HashMap) m;
  long now = System.currentTimeMillis();
  Long bad = (Long) BROKEN.get(k);
  if (bad != null && now - bad.longValue() < 30000L) return null;
  java.util.HashMap out = new java.util.HashMap();
  try {
    java.nio.file.Path f = fileOf(k);
    if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {
      java.util.Properties p = new java.util.Properties();
      java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
      try { p.load(new java.io.InputStreamReader(in, "UTF-8")); } finally { in.close(); }
      java.util.Iterator it = p.stringPropertyNames().iterator();
      while (it.hasNext()) {
        String key = (String) it.next();
        if (key.startsWith("_") || !SetReg.validKey(key)) continue;
        String v = p.getProperty(key, "").trim();
        if (v.equalsIgnoreCase("true")) out.put(key, Boolean.TRUE);
        else if (v.equalsIgnoreCase("false")) out.put(key, Boolean.FALSE);
      }
    }
  } catch (Throwable t) {
    if (bad == null) MenuUtil.warn("settings/" + k + ".properties cannot be read (" + t + ") - defaults are used and the file is NOT overwritten; read again every 30 s");
    BROKEN.put(k, Long.valueOf(now));
    return null;
  }
  BROKEN.remove(k);
  VALS.put(k, out);
  return out;
}
public static Boolean get(java.util.UUID u, String key) {
  if (u == null || key == null) return null;
  String k = u.toString();
  Object m = VALS.get(k);
  java.util.HashMap vals = m != null ? (java.util.HashMap) m : load(k);
  if (vals != null) {
    Object v = vals.get(key);
    if (v instanceof Boolean) return (Boolean) v;
  }
  return SetReg.def(key);
}
// 1 = the stored state matches the request, 0 = not saved (file unreadable)
public static synchronized int set(java.util.UUID u, String key, boolean val, boolean onlyIfUnset) {
  String k = u.toString();
  java.util.HashMap cur = load(k);
  if (cur == null) return 0;
  if (onlyIfUnset && cur.containsKey(key)) return 1;
  java.util.HashMap nx = new java.util.HashMap(cur);
  nx.put(key, Boolean.valueOf(val));
  VALS.put(k, nx);
  saveSoon(k);
  return 1;
}
public static synchronized int resetAll(java.util.UUID u) {
  String k = u.toString();
  if (load(k) == null) return 0;
  VALS.put(k, new java.util.HashMap());
  saveSoon(k);
  return 1;
}
public static void saveSoon(String k) {
  if (DIRTY.putIfAbsent(k, Boolean.TRUE) != null) return;           // a save is already scheduled; it writes the newest map
  try { HytaleServer.SCHEDULED_EXECUTOR.schedule(new SetSaveTask(k), 500L, java.util.concurrent.TimeUnit.MILLISECONDS); }
  catch (Throwable t) { saveNow(k); }
}
```

`saveNow(k)` (`synchronized`): `DIRTY.remove(k)`. Return if `VALS` has no map for `k` or `BROKEN` has `k` (never overwrite an unreadable file). Otherwise build the text by hand, with keys sorted:
```
# SkyyMenu settings of one player (uuid <k>). Only the switches this player changed are listed - everything else uses the default.
# Change them in game with /settings. Hand edits while the player is online are overwritten.
_v=1
_name=<MenuUtil.cleanName(NAMES.get(k))>
party.chat=false
skills.xpGain=false
```
Then call `MenuUtil.atomicWrite(fileOf(k), text.getBytes("UTF-8"))`. On failure: warn and `DIRTY.put(k, TRUE)` (retried by `retryDirty()` in `SeenTick` every 30 s and by `flushAll()` in `shutdown()`).

**Storage:** `<world>/mods/Skyy_SkyyMenu/settings/<uuid>.properties`, through `getDataDirectory().resolveSibling("Skyy_SkyyMenu").resolve("settings")` like `Given.DIR`. Per **player** (`uuid.toString()`, never `pkey`): settings are UI preferences, PROFILES-CONTRACT rule 6 ("Menu data is per PLAYER"), and SkyBlock's settings are account-wide too. An empty map (after a reset) writes a file with only the header.

**Admin defaults (server backbone, pack goal):** `Skyy_SkyyMenu/settings-defaults.properties`. On first start, if the file is missing, write a template: two comment lines ("Server-wide defaults for /settings. A player's own choice always wins. Remove the # and set true or false; re-read within 30 s.") and one commented line per `SET_ORDER` key (`#skills.xpGain=true`). `loadAdmin` re-reads it when `lastModified` changes (from `SeenTick`). A bad line is ignored and logged. Reset-to-defaults returns a player to these admin defaults.

**Plugin wiring (`SkyyMenuPlugin`):**
- `setup()` after the existing lines: set `SetStore.DIR` and `SetReg.ADMIN_FILE`, call `SetReg.loadAdmin(true)`, then `MenuUtil.bridge().put(...)` the three functions (`register`, `get`, `set`), **then** `SetReg.drain()`, then `getCommandRegistry().registerCommand(new SettingsCmd())`.
- `MenuReady.accept`: also `SetStore.NAMES.put(u.toString(), pr.getUsername())` and schedule `new SetLoadTask(u.toString())` with 0 ms delay on `SCHEDULED_EXECUTOR` (the preload, off the world thread). On the first ready of the JVM (static boolean), check `MenuUtil.cmd("settings")`. If it is not a `SettingsCmd` instance, warn once: `another mod owns /settings - players can use /skysettings or the SkyWynn Menu` (duplicate command names are silently last-wins, HANDOFF).
- `SeenTick.run` (every 30 s): also `SetStore.retryDirty()`, `SetStore.pruneOffline(online uuid strings)` (drops cached maps of offline players that are not dirty, so a hand edit while offline is read at the next join), and `SetReg.loadAdmin(false)`.
- `shutdown()`: `SetStore.flushAll()` (saves every dirty map synchronously) before `super.shutdown()`. Functions stay on the bridge (profiles rule).
- **writeFile list:** add every new class. Add a build assert that every `pool.makeClass` result is written. SkyySacks' self-test `GrantTask` is dead code only because it was left out of that list.

### 1.5 Failure modes

| Situation | What happens |
|---|---|
| SkyyMenu not installed / older than 0.2 | No `settings:fn:get`: every `notifyOn` returns true, and the `quiet` commands keep their old behaviour. Nothing breaks. `settings:def:*` keys sit unused in the bridge. |
| Mod loads before SkyyMenu | Its `settings:def:*` keys are drained at SkyyMenu `setup()`. |
| Mod not updated yet | Its rows do not appear (only registered keys are listed) and its messages behave as today. |
| Player's settings file unreadable | `get` returns defaults, `set` returns FALSE, and the file is never overwritten. The page shows a red status: "Your settings file could not be read - changes are not saved. Tell an admin." The file is read again every 30 s. |
| Save fails (Windows lock) | Memory keeps the change. Retried every 30 s and at shutdown. Logged. |
| SkyyMenu removed after players changed settings | Messages come back ("default on"). Files stay on disk and are used again when SkyyMenu returns. |

---

## 2. The settings list

### 2.1 Tabs (display order)

| # | Tab text | Header (set with `b.set`) | Category id |
|---|---|---|---|
| 0 | Skills | Skills | `skills` |
| 1 | Collections | Collections | `collections` |
| 2 | Sacks | Sacks & Crafting | `sacks` |
| 3 | Combat | Combat & Classes | `combat` |
| 4 | Coins | Coins & Bank | `coins` |
| 5 | Profiles | Profiles & Islands | `profiles` |
| 6 | Cooking | Cooking & Trees | `cooking` |
| 7 | General | General (party, teleports, messages) | `general` |

Tab buttons use one word because `&` has never been used in inline UI text, which is UNVERIFIED. The full name goes into the header label through `b.set`, which "is safe for anything" (HANDOFF section 2).

### 2.2 Every switch (all default ON)

Label <= 40 characters. The help line shows under the label (<= 90 characters so it fits 774 px at FontSize 16). "Covers" refers to the inventory rows of each mod. `SET_ORDER` in MENU DATA = this table's key column, top to bottom.

| Tab | Key | Label | Help line (exact) | Registered by | Covers |
|---|---|---|---|---|---|
| Skills | `skills.xpGain` | Skill XP gains | +12 Mining XP (340/500) while you gather, fight, smelt, brew and move | SkyySkills | Skills #1 (every skill incl. Acrobatics) |
| Skills | `skills.levelUp` | Skill level-ups | SKILL LEVEL UP with the coins it paid and the XP for the next level | SkyySkills | Skills #2 |
| Skills | `skills.doubleDrop` | Double drops | Double drop x3! from the Mining, Foraging and Farming perks | SkyySkills | Skills #6 |
| Skills | `skills.extraPotion` | Extra potions | Extra potion! from the Alchemy perk | SkyySkills | Skills #7 |
| Skills | `skills.combatHints` | No combat XP hints | Why a kill gave no combat XP - once per reason each session | SkyySkills | Skills #5 (all 5 reasons) |
| Skills | `explore.chunkXp` | Exploration map XP | +1,240 Exploration XP from 18 new chunks - at most every 30 s | SkyyExploration (when built) | planned chunk line; replaces `/explore quiet` |
| Skills | `explore.finds` | Exploration finds | Loot chests, chest luck, new zones and new titles | SkyyExploration (when built) | planned chest, luck, zone and title lines |
| Collections | `coll.newCollection` | New collections | New collection: Copper Ore! - the first item of a kind you gather | SkyyCollections | Coll #2 |
| Collections | `coll.tierUp` | Collection tier-ups | COLLECTION UP with its rewards and the recipes it unlocked | SkyyCollections | Coll #3, #4, #5 (merged) |
| Sacks | `sacks.benchDone` | Furnace and Tannery done | Your Furnace is done - open /craft to collect | SkyySacks | Sacks #1 |
| Sacks | `sacks.benchFuel` | Furnace out of fuel | Your Furnace ran out of fuel - once until you add more | SkyySacks | Sacks #2 |
| Combat | `classes.blockedChat` | Blocked weapon - chat line | Only Archers can use bows... - at most every 3 s. The hit is blocked either way | SkyyClasses | Classes #1 |
| Combat | `classes.blockedPopup` | Blocked weapon - popup | The popup with the weapon's icon - at most every 1.5 s | SkyyClasses | Classes #2 |
| Coins | `coins.payReceived` | Payments from players | Steve paid you 500 coins - the coins arrive either way | SkyyCoins | Coins #3 |
| Coins | `bank.interest` | Bank interest | You earned 120 coins interest - one line per payout | SkyyBank | Bank #4 |
| Coins | `rewards.late` | Late reward payouts | Coins and XP paid later because another mod was not ready | SkyySkills + SkyyCollections (shared key, identical values) | Skills #3, Coll #6, Coll #7 (merged) |
| Profiles | `profiles.loginStatus` | Profile on login | Playing profile Strawberry (Archer) - when you join | SkyyProfiles | Profiles #2 |
| Profiles | `islands.protection` | Island protection warnings | You can only build on islands you are a member of - at most every 3 s | SkyyIslands | Islands #13, #14, #15, #16 (merged) |
| Profiles | `islands.hubOnLogin` | Hub on login | Welcome back! You start in the hub - when you log in on an island | SkyyIslands | Islands #17 |
| Profiles | `islands.buildRights` | Build rights given to you | Steve gave you build rights on their island | SkyyIslands | Islands #18 |
| Profiles | `islands.visitPing` | Visitors on your island | Steve is visiting your island - the island's Visit ping must be on too | SkyyIslands 0.5.x | planned 0.5 visit ping |
| Profiles | `islands.visitWelcome` | Welcome when you visit | What visitors may do, when you arrive on someone's island | SkyyIslands 0.5.x | planned 0.5 visitor welcome line |
| Cooking | `cooking.grade` | Food Grade changes | Your food now comes out Grade 3 - and the campfire accessory hint | SkyyCooking | Cooking #1, #6 (merged) |
| Cooking | `cooking.procs` | Cooking bonus procs | Gourmet!, Signature Dish!, Batch Cook!, Prep Cook! and Frugal! | SkyyCooking | Cooking #2, #3, #4, #5 (merged) |
| Cooking | `trees.bonus` | Tree bonus totals | Tree bonus: +2 Copper Ore, extra drops x1, +3 coins | SkyyTrees | Trees #1 |
| Cooking | `trees.abilities` | Vein Burst and Tree Feller | Vein Burst! +6 ore (ready again in 40 s) | SkyyTrees | Trees #2, #3 (merged) |
| General | `party.invites` | Party invites | OFF: nobody can invite you - they are told you are not taking invites | SkyyParty | Party #7 (refuses) |
| General | `party.members` | Party join, leave and leader | Steve joined, left, disconnected or is now the party leader | SkyyParty | Party #8, #9, #10, #11 (merged) |
| General | `party.chat` | Party chat | [Party] lines from other members - your own lines always show | SkyyParty | Party #12 |
| General | `tpa.requests` | Teleport requests | OFF: nobody can send you /tpa or /tpahere - they are told | SkyyEssentials | Ess #13 (refuses) |
| General | `tpa.updates` | Teleport request updates | Denied, expired and cancelled requests - accepted ones always show | SkyyEssentials | Ess #15, #16, #17 + the `/tpacancel` notice to the target (merged; requests not yet accepted) |
| General | `msg.private` | Private messages | OFF: /msg and /reply to you are refused and the sender is told | SkyyEssentials | Ess #18 (refuses) |

Counts: Skills 5 (+2 planned), Collections 2, Sacks 2, Combat 2, Coins 3, Profiles 4 (+2 planned), Cooking 4, General 6. That is 28 now and 32 with the planned rows. The page shows 7 rows per tab page. No tab needs a second page, and the Prev/Next code is there for future keys.

**Merges made (duplicates):** the four island-protection texts are one switch. Party join, leave, disconnect and leader change are one. Teleport denied, expired, offline-cancelled and `/tpacancel`-cancelled are one (all about a request that was never accepted). The Collections tier-up header, reward lines and recipe count are one (they print as one block). The Cooking Grade-up and campfire hint are both "your Grade changed". The four cooking procs are one. Vein Burst and Tree Feller are one. The three "paid later" lines from Skills and Collections are one shared key.

### 2.3 Never toggleable (always shown), and why

LOCKED 2026-09-25 (Skyy): this list stays as written. These messages stay always shown.

| Message (mod #) | Why it cannot be switched off |
|---|---|
| **Replies to your own action:** every typed-command reply (usage, "no permission", errors), page status lines, Bazaar trade results (Bazaar), `/pay` sender line (Coins), `/tpa` sender lines, "Accepted..." (Ess #14), profile switch / create confirmations (Profiles #4, #6), class chosen (Classes #7), skill tree open failed (Skills #8), retired accessory click (Acc #6), the `/island visit` reply "Visiting X's island - look, don't touch (they can /island invite you to build)." (Islands, `IslandCmd.visit`, already live in 0.4.4; it is **not** `islands.visitWelcome`, see 3.10) | You just asked for it. Hiding it makes buttons and commands look broken. |
| Teleport accepted: "X accepted your request. Teleporting..." / "X accepted and is teleporting to you" (Ess #14) | It announces that you, or someone next to you, is about to move. |
| How an accepted teleport ended: the mover's "[TPA] Teleporting to X." (`MoveTask.run`) and "[TPA] Teleport cancelled: <why>" to both players (`MoveTask.fail`, `ReadDestTask.fail`: a player went offline, the destination world closed, "is already teleporting" / "is changing worlds, try again" after 8 retries, "something went wrong") | It follows the always-shown "accepted... Teleporting..." line. Hidden, a player is told they are about to move and then nothing happens, which reads as a bug, and "try again" is something they must act on. `tpa.updates` covers only requests that were never accepted. |
| Coins lost on death (Coins #2) | Something was taken from you. Silent coin loss reads as a bug. |
| Admin changed or reset your class / profile class (Classes #5, #6, Profiles #12) | Your character changed without your action. |
| Flight turned off because your permission was removed (Ess #19) | You might fall. It is also staff-only. |
| Items that did not fit back after a switch and were added or dropped (Profiles #5) | Data-loss adjacent: you need to pick them up. |
| Profile file unreadable, switch interrupted and paused, crash repair outcome, failed switch waiting for an admin (Profiles #8, #9, #10, #11) | Critical safety notices. #10 explains why your inventory changed. |
| SkyyIslands missing, sent to world spawn (Profiles #7) | System fallback: you were moved somewhere unexpected. |
| Create-your-profile welcome and the reminder after skipping (Profiles #1, #3); no-class reminder and the class picker auto-open without SkyyProfiles (Classes #3, #4) | Setup you must finish before you can fight. They stop by themselves once done. |
| SkyWynn Menu item given / inventory full (Menu #4, #5); starter coins (Coins #1) | One-time onboarding (the menu item) or once per profile (coins). They explain what just appeared in your inventory or purse. |
| Old Combat XP moved to your class skill (Skills #4); "Collections now count items" (Coll #1) | One-time notices. A switch cannot be set before the notice appears. |
| "Your profile changed - click a tab to refresh" on an open bag / craft page (Sacks #3, #4) | Data safety: it stops you from clicking on a stale profile's page. |
| Party disbanded ("... The party has been disbanded.") and "X is now the party leader" **to the new leader** | Your party state changed. The rest of `party.members` stays switchable. |

Each tab shows its own "Always shown" line under the rows (section 4.3) so players know what stays.

### 2.4 Migration of the existing toggles

| Old toggle | Stored | New keys | How |
|---|---|---|---|
| `/skills quiet` | `quiet=true` in `Skyy_SkyySkills/players/<pkey>.properties` (per profile) | `skills.xpGain`, `skills.doubleDrop`, `skills.extraPotion` (exactly what quiet hid; level-ups were never hidden) | **One-shot move** (3.1): when the registry exists and the active profile has `quiet=true`, set the 3 keys OFF with `onlyIfUnset`. If all three calls return TRUE, clear `quiet` in that profile file. Without the registry `quiet` works as today. |
| `/tree quiet` | `quiet=true` in `Skyy_SkyyTrees/players/<pkey>.properties` | `trees.bonus` | Same one-shot move (3.2). |
| `/explore quiet` (planned) | `players/<pkey>.properties quiet` | `explore.chunkXp` | SkyyExploration is not built yet: build it on the registry from the start (3.12). |
| Server configs `feedback`, `feedbackMs`, `perk.doubleDropMessage` (xp.properties), `messages` (cooking.properties), `promptEveryLogin` (Classes, Profiles), `feedbackMs` (trees.properties) | server-wide | unchanged | They stay admin master switches and throttles. A player switch can only hide more, never show what the admin turned off. |

Old per-profile quiet flags become one per-player setting. If profile 1 had `quiet=true` and profile 2 had not, the player ends up with the three switches OFF everywhere, which is the most likely intent. After "Reset all to defaults" a later move from a not-yet-visited quiet profile can turn them off once more. That edge is rare and documented, not solved. The `quiet` commands stay as **shortcuts** (3.1, 3.2) and their replies point to `/settings`.

---

## 3. Per-mod adoption

Every row lands on top of whatever version the running rounds produce (feedback round 2 already queues SkyySkills 0.4.2, SkyyTrees 0.2.1, SkyyCollections 0.2.1, SkyySacks 0.7.5, SkyyIslands 0.5.1). The version numbers below are "the next version of that mod". Line numbers refer to the newest scripts today and will shift, so the class.method and the quoted statement are the anchor. Each mod: add the helper (1.3) to the named class, register in `setup()`, gate the listed sends, and add nothing else.

### 3.1 SkyySkills (next: 0.4.2, from `build_skyyskills_0.4.1.py`)
Line numbers below are from 0.4.1 (the Exploration row; same message set as 0.4, renumbered). Build on 0.4.1, never on 0.4: 0.4.1 says a player file with Exploration XP must never be saved by 0.4 again.
Helper class: **`SkillStore`** (has the creating `bridge()`, `pkey`, `quiet`, `QUIET`, `DIRTY`). Skills needs a legacy fallback and the quiet move, so its helper differs from 1.3:
```java
public static void moveQuiet(java.util.UUID u) {
  String k = pkey(u);
  if (!QUIET.containsKey(k)) return;
  Object f = bridge().get("settings:fn:set");
  if (!(f instanceof java.util.function.Function)) return;
  java.util.function.Function sf = (java.util.function.Function) f;
  int ok = 0;
  if (Boolean.TRUE.equals(sf.apply(new Object[] { u, "skills.xpGain", Boolean.FALSE, Boolean.TRUE }))) ok++;
  if (Boolean.TRUE.equals(sf.apply(new Object[] { u, "skills.doubleDrop", Boolean.FALSE, Boolean.TRUE }))) ok++;
  if (Boolean.TRUE.equals(sf.apply(new Object[] { u, "skills.extraPotion", Boolean.FALSE, Boolean.TRUE }))) ok++;
  if (ok == 3 && QUIET.remove(k) != null) { DIRTY.put(k, Boolean.TRUE); SkillCfg.info("moved /skills quiet of " + k + " to /settings"); }
}
public static boolean notifyOn(java.util.UUID u, String key) {
  if (u == null || key == null) return true;
  try {
    Object f = bridge().get("settings:fn:get");
    if (f instanceof java.util.function.Function) {
      moveQuiet(u);
      Object r = ((java.util.function.Function) f).apply(new Object[] { u, key });
      if (r instanceof Boolean) return ((Boolean) r).booleanValue();
    }
  } catch (Throwable t) { }
  if (key.equals("skills.xpGain") || key.equals("skills.doubleDrop") || key.equals("skills.extraPotion")) return !quiet(u);
  return true;
}
```
Also add `regSetting` (1.3, mod `"SkyySkills"`).

| Message | Site (today) | Change |
|---|---|---|
| +XP line (incl. Acrobatics, which calls `SkillMsg.note` from `Acro.flush`) | `SkillMsg.note` (~2392): `if ({PKG}.SkillStore.quiet(u)) return;` | -> `if (!{PKG}.SkillStore.notifyOn(u, "skills.xpGain")) return;` |
| SKILL LEVEL UP + `next:` line | `SkillXp.gain3` (~2606-2618) | Before the loop: `boolean lvOn = {PKG}.SkillStore.notifyOn(u, "skills.levelUp");`. Wrap **only** the two `pr.sendMessage` calls in `if (lvOn)`. `shown += coins`, `SkillMsg.send(pr)` and `publish(u)` stay unconditional. |
| Late payout line | `SkillXp.gain3` (~2621) | Condition becomes `paid != null && paid[2] > shown && {PKG}.SkillStore.notifyOn(u, "rewards.late")`. |
| Combat XP hints (5 reasons) | `SkillClass.tellOnce` (~1936) | First line inside `try`: `if (!{PKG}.SkillStore.notifyOn(pr.getUuid(), "skills.combatHints")) return;` (before `claimTold`, so the hint can still show later in the session after switching it back on). |
| Double drop | `Perks.doubled` (~3004): `if ({PKG}.SkillStore.quiet(u)) return;` | -> `if (!{PKG}.SkillStore.notifyOn(u, "skills.doubleDrop")) return;` (the drops were already given by `give` above; keep `PerkCfg.DD_MSG`). |
| Extra potion | `Brew.extraPotion` (~3065): `if (what == null \|\| {PKG}.SkillStore.quiet(u)) return;` | -> `if (what == null \|\| !{PKG}.SkillStore.notifyOn(u, "skills.extraPotion")) return;` |
| Legacy Combat XP moved (Perks.migrate), tree-open errors (SkillBonus.openTree), command replies | - | no change (2.3) |

`/skills quiet` (`QuietCmd.execute`, ~4816) becomes a shortcut when the registry exists:
```java
java.util.UUID u = pr.getUuid();
Object f = {PKG}.SkillStore.bridge().get("settings:fn:set");
if (f instanceof java.util.function.Function) {
  java.util.function.Function sf = (java.util.function.Function) f;
  boolean anyOn = {PKG}.SkillStore.notifyOn(u, "skills.xpGain") || {PKG}.SkillStore.notifyOn(u, "skills.doubleDrop") || {PKG}.SkillStore.notifyOn(u, "skills.extraPotion");
  Boolean nv = anyOn ? Boolean.FALSE : Boolean.TRUE;
  int ok = 0;
  if (Boolean.TRUE.equals(sf.apply(new Object[] { u, "skills.xpGain", nv }))) ok++;
  if (Boolean.TRUE.equals(sf.apply(new Object[] { u, "skills.doubleDrop", nv }))) ok++;
  if (Boolean.TRUE.equals(sf.apply(new Object[] { u, "skills.extraPotion", nv }))) ok++;
  if (ok < 3) { pr.sendMessage({MSG}.raw("[Skills] Could not save your settings - try again or tell an admin.")); return; }
  pr.sendMessage({MSG}.raw(anyOn ? "[Skills] XP, double-drop and extra-potion messages hidden (level ups still show). One switch per message: /settings" : "[Skills] XP, double-drop and extra-potion messages shown. One switch per message: /settings"));
  return;
}
// else: today's toggleQuiet code unchanged
```
`setup()`: register `skills.xpGain`, `skills.levelUp`, `skills.doubleDrop`, `skills.extraPotion`, `skills.combatHints` (category `skills`) and `rewards.late` (category `coins`), with the section 2.2 labels and help lines.

### 3.2 SkyyTrees (next: 0.2.1, from `build_skyytrees_0.2.py`)
Line numbers below are from 0.2 (the Acrobatics + Exploration trees; same message lines as 0.1, renumbered).
Helper class: **`TreeStore`** (creating `bridge()`, `pkey`, `data`, `dataK`, `dirty`, `TreeData.quiet`/`.bad`). Add `clearQuiet(TreeData d)` (`synchronized`: `if (!d.quiet) return false; d.quiet = false; return true;`), then:
```java
public static void moveQuiet(java.util.UUID u) {
  String k = pkey(u);
  TreeData d = dataK(k, u);
  if (d == null || !d.quiet || d.bad) return;
  Object f = bridge().get("settings:fn:set");
  if (!(f instanceof java.util.function.Function)) return;
  if (!Boolean.TRUE.equals(((java.util.function.Function) f).apply(new Object[] { u, "trees.bonus", Boolean.FALSE, Boolean.TRUE }))) return;
  if (clearQuiet(d)) dirty(k);
}
public static boolean notifyOn(java.util.UUID u, String key) {
  if (u == null || key == null) return true;
  try {
    Object f = bridge().get("settings:fn:get");
    if (f instanceof java.util.function.Function) {
      if ("trees.bonus".equals(key)) moveQuiet(u);
      Object r = ((java.util.function.Function) f).apply(new Object[] { u, key });
      if (r instanceof Boolean) return ((Boolean) r).booleanValue();
    }
  } catch (Throwable t) { }
  if ("trees.bonus".equals(key)) return !data(u).quiet;
  return true;
}
```
| Message | Site | Change |
|---|---|---|
| Tree bonus line | `TreeMsg.flush` (~1547): `if (@PKG@.TreeStore.data(u).quiet) return;` | -> `if (!@PKG@.TreeStore.notifyOn(u, "trees.bonus")) return;` (`take` already cleared the pending totals: correct, a hidden line is dropped, not queued) |
| Vein Burst | `TreeAbil.vein` (~1773): `@PKG@.TreeMsg.say(pr, "Vein Burst! ...")` | wrap in `if (@PKG@.TreeStore.notifyOn(pr.getUuid(), "trees.abilities"))` |
| Tree Feller | `TreeAbil.feller` (~1794) | same wrap. The horizontal rework in 0.2.1 keeps the same line. |

`/tree quiet` (`TreeOps.quiet` / `TreeQuietCmd`): when `settings:fn:set` exists, flip `trees.bonus` (new value = `!notifyOn(u, "trees.bonus")`) and reply `[Trees] Tree bonus messages hidden/shown. More switches: /settings`. Otherwise today's code runs. `setup()`: register `trees.bonus`, `trees.abilities` (category `cooking`).

### 3.3 SkyyCollections (next: 0.2.1, from `build_skyycollections_0.2.py`)
Helper class: **`CollUtil`** (creating `bridge()`): 1.3 helper, mod `"SkyyCollections"`.

| Message | Site | Change |
|---|---|---|
| New collection | `CollCredit.creditOne` (~1697) | condition becomes `on && r[0] <= 0L && r[1] > 0L && @PKG@.CollUtil.notifyOn(u, "coll.newCollection")` |
| COLLECTION UP + reward lines + recipe count | `CollCredit.creditOne` (~1703-1705) | after `if (!on) return;`: `boolean tierOn = @PKG@.CollUtil.notifyOn(u, "coll.tierUp");` then `if (tierOn) announce(pr, R, c, ot + 1, nt);` and `if (tierOn && now > before) ...recipes line`. `settle` and `publish` above stay unconditional. |
| "some rewards are owed" | `CollCredit.creditOne` (~1706) | `if (paid[2] != 0L && @PKG@.CollUtil.notifyOn(u, "rewards.late")) ...` |
| "Paid for earlier collection tiers" | `CollRewards.settleAll` (~1467) | condition gets `&& @PKG@.CollUtil.notifyOn(u, "rewards.late")`. The payment and `mark(...)` stay above it, unchanged. |
| Migration note (`CollUnlocks.firstSight`) | - | no change |

`setup()`: register `coll.newCollection`, `coll.tierUp` (category `collections`) and `rewards.late` (category `coins`, same label and help as Skills).

### 3.4 SkyySacks (next: 0.7.5, from `build_skyysacks_0.7.4.py`)
Helper class: **`SackPool`**. Its `bridge()` is **read-only** (returns `EMPTY_MAP` when absent, and `put` would throw). Add a creating `bridgeW()` (the synchronized create pattern from `SkillStore.bridge`) and use it in `regSetting`. `notifyOn` uses the read-only `bridge()`.

| Message | Site | Change |
|---|---|---|
| Bench done | `ProcTask.run` (~3149) | `if ({PKG}.SackPool.notifyOn(u, "sacks.benchDone")) pr.sendMessage(...)`. The `CraftLog.line(k, "DONE ...")` stays unconditional. |
| Out of fuel | `ProcTask.run` (~3151): `} else if (pb.fuelWarnOnce()) {` | keep the latch call as is. Inside: `if ({PKG}.SackPool.notifyOn(u, "sacks.benchFuel")) pr.sendMessage(...)`, so the latch is used even when hidden and switching back on does not replay an old warning. |
| Profile-changed page banners (`SacksPage.profileNotice`, `CraftPage.profileNotice`) | - | no change (2.3) |

`setup()`: register `sacks.benchDone`, `sacks.benchFuel` (category `sacks`). Later bag features (a SkyBlock-style "items added to your bags" line) get their own `sacks.*` key when they exist.

### 3.5 SkyyClasses (next: 0.1.5, from `build_skyyclasses_0.1.4.py`)
Helper class: **`ClassCfg`** (creating `bridge()`): 1.3 helper, mod `"SkyyClasses"`.

| Message | Site | Change |
|---|---|---|
| Blocked weapon chat | `ClassRules.tell` (~1021) | first line: `if (!@PKG@.ClassCfg.notifyOn(u, "classes.blockedChat")) return;` (before the `WARNED` throttle) |
| Blocked weapon popup | `ClassRules.popup` (~1030) | first line inside `try`: `if (!@PKG@.ClassCfg.notifyOn(u, "classes.blockedPopup")) return;` (before `POPPED`) |
| No-class reminder + picker auto-open (`ReadyTask.run`), admin set/reset lines, class confirm | - | no change (2.3). `DamageLock` keeps blocking the damage whatever the switches say. |

`setup()`: register `classes.blockedChat`, `classes.blockedPopup` (category `combat`).

### 3.6 SkyyCooking (next: 0.1.2, from `build_skyycooking_0.1.1.py`)
Helper class: **`Cook`** (creating `bridge()`): 1.3 helper, mod `"SkyyCooking"`. Add a 4-argument `tell` **before** the old one's callers (javassist order), and keep the 3-argument version delegating with `key = null`:
```java
public static void tell(@PR@ pr, String msg, boolean force, String key) {
  if (pr == null || msg == null || !@PKG@.CookCfg.MESSAGES) return;
  if (key != null && !notifyOn(pr.getUuid(), key)) return;          // before LAST: a hidden line does not eat the 2.5 s cooldown
  long now = System.currentTimeMillis();
  Long l = (Long) LAST.get(pr.getUuid());
  if (!force && l != null && now - l.longValue() < 2500L) return;
  LAST.put(pr.getUuid(), Long.valueOf(now));
  pr.sendMessage(@MSG@.raw("[Cooking] " + msg).color("#ffb070"));
}
```
| Message | Site | Change |
|---|---|---|
| Grade up | `CookXpTask.run` (~1537) | `tell(pr, ..., true, "cooking.grade")`. `TOLD.put` stays before it, so a hidden Grade counts as told. |
| Proc note (Gourmet / Signature / Batch / Prep / Frugal) | `CookXpTask.run` (~1538) | `tell(pr, this.note, false, "cooking.procs")` |
| Campfire hint | `Cook.campHint` (~1465) | `tell(pr, s, true, "cooking.grade")` (`CAMP_TOLD` stays before) |

`setup()`: register `cooking.grade`, `cooking.procs` (category `cooking`).

### 3.7 SkyyCoins (next: 0.1.6, from `build_skyycoins_0.1.5.py`)
Helper class: **`CoinStore`** (creating `bridge()`): 1.3 helper, mod `"SkyyCoins"`.

| Message | Site | Change |
|---|---|---|
| Payment received | `PayCmd.execute` (~568): `target.sendMessage(... paid you ...)` | `if ({PKG}.CoinStore.notifyOn(target.getUuid(), "coins.payReceived")) target.sendMessage(...)`. The sender's reply and the transfer are unchanged. |
| Starter coins, death loss (`CoinTask.run`) | - | no change (2.3) |

`setup()`: register `coins.payReceived` (category `coins`). Note for later, not this build: `/pay` has no rate limit (a `/pay you 1` spam vector). The switch hides the spam, but a per-payer cooldown belongs in SkyyCoins.

### 3.8 SkyyBank (next: 0.1.3, from `build_skyybank_0.1.2.py`)
Helper class: **`BankStore`** (creating `bridge()`): 1.3 helper, mod `"SkyyBank"`.

| Message | Site | Change |
|---|---|---|
| Interest | `BankTick.interest`, the second loop (over `uni.getPlayers()`, ~491) | wrap only the send: `if ({PKG}.BankStore.notifyOn(pr.getUuid(), "bank.interest")) pr.sendMessage(...);`. **VERIFIED safe (0.1.2):** the payout happens earlier in the method. The first loop calls `BankStore.payInterest(key, ...)` for every account file, online or not, then `BankConfig.LAST` moves on and `BankConfig.save()` runs. Only after that does the loop over online players start, and all it does is send the "[Bank] You earned" line. So a player with the switch OFF still gets every coin. Do not move the gate into the first loop, `payInterest` or the `earned` map. |

`setup()`: register `bank.interest` (category `coins`).

### 3.9 SkyyProfiles (next: 0.1.1, from `build_skyyprofiles_0.1.py`)
Helper class: **`ProfCfg`** (creating `bridge()`): 1.3 helper, mod `"SkyyProfiles"`. Keep this change **minimal**: SkyyProfiles is crash-safety code. It gets one gate and one registration, and nothing on the switch path.

| Message | Site | Change |
|---|---|---|
| "Playing profile X (Class)" | `ReadyTask.run` (~2061) | `if (@PKG@.ProfCfg.notifyOn(u, "profiles.loginStatus")) pr.sendMessage(...)`. `ReadyTask` runs on the scheduler, so a first-read file access there is fine. |
| Everything else | - | no change (2.3) |

`setup()`: register `profiles.loginStatus` (category `profiles`).

### 3.10 SkyyIslands (next: 0.5.1, on top of the island-settings 0.5 build)
Helper class: **`IslandStore`** (its `bridge()` creates via `putIfAbsent`): 1.3 helper, mod `"SkyyIslands"`.

| Message | Site (0.4.4 names) | Change |
|---|---|---|
| Protection warnings (4 texts) | `GuardSystem` handle (~909-914, shared by GuardDamage / Break / Place / Pickup) and `GuardUse` | inside the 3 s throttle block, after `WARNED.put(...)`: wrap both sends in `if ({PKG}.IslandStore.notifyOn(u, "islands.protection"))`. `setCancelled(true)` stays unconditional. |
| Hub on login | `RouteTask.run` (~801): `if ({PKG}.HubCmd.sendToHub(st, r, pr, w)) pr.sendMessage(...)` | **Keep the teleport call unconditional:** `boolean sent = {PKG}.HubCmd.sendToHub(st, r, pr, w); if (sent && {PKG}.IslandStore.notifyOn(pr.getUuid(), "islands.hubOnLogin")) pr.sendMessage(...);`. Do not put `notifyOn` first in the `&&`, or a player with the switch OFF is never routed. |
| Build rights received | `IslandCmd` invite branch (~629): `target.sendMessage(...)` | `if ({PKG}.IslandStore.notifyOn(target.getUuid(), "islands.buildRights")) target.sendMessage(...)` |
| "Visiting X's island - look, don't touch (they can /island invite you to build)." (live since 0.4.4) | `IslandCmd.visit` (~637), sent to the visitor right after `go(...)` | no change, always shown (2.3): it replies to the visitor's own `/island visit`. `islands.visitWelcome` is only the 0.5 `ArrivalTask` line, which fires on every arrival (also after a `/tpa`). Note for the 0.5 build: a `/island visit` visitor would then get both lines, so 0.5 may shorten this reply to "Visiting X's island." and leave the rules to the welcome line. That is SkyyIslands' call (Island-Settings-Spec), not a settings change. |
| 0.5 visit ping (spec 4.7) | new `ArrivalTask` code | send to each receiver (owner + co-op) only when the island's `visit.notify=1` **and** `notifyOn(receiver, "islands.visitPing")` |
| 0.5 visitor welcome line | new `ArrivalTask` code | `if (notifyOn(visitor, "islands.visitWelcome"))` |
| Expelled / banned / "may not enter" reasons (0.5) | - | never gated: they explain why you were moved |

`setup()`: register `islands.protection`, `islands.hubOnLogin`, `islands.buildRights`, and (with the 0.5 code) `islands.visitPing`, `islands.visitWelcome` (category `profiles`).

### 3.11 SkyyParty (next: 0.1.3, from `build_skyyparty_0.1.2.py`) and SkyyEssentials (next: 0.1.1, from `build_skyyessentials_0.1.py`)
Neither has a `bridge()`. Add the creating `bridge()` (the `SkillStore` pattern) plus the 1.3 helper to **`PartyStore`** and **`EssStore`**.

**SkyyParty.** Add the new overloads first, then make the old ones delegate (`key = null`):
```java
public static void broadcastTo(java.util.Set s, String msg, String key, java.util.UUID self) {
  java.util.Iterator it = s.iterator();
  while (it.hasNext()) {
    java.util.UUID m = (java.util.UUID) it.next();
    PlayerRef p = online(m);
    if (p == null) continue;
    if (key != null && !m.equals(self) && !notifyOn(m, key)) continue;
    p.sendMessage(Message.raw(msg));
  }
}
public static void broadcast(java.util.UUID anyMember, String msg, String key, java.util.UUID self) {
  java.util.Set s = membersOf(anyMember);
  if (s != null) broadcastTo(s, msg, key, self);
}
```
| Message | Site | Change |
|---|---|---|
| Invite | `InviteCmd.execute` (~170), before `INVITES.put` | `if (!{PKG}.PartyStore.notifyOn(target.getUuid(), "party.invites")) { pr.sendMessage({MSG}.raw(target.getUsername() + " is not taking party invites right now.")); return; }` (no invite is stored) |
| Joined | `AcceptCmd` (~189) | `broadcast(pr.getUuid(), ... " joined the party!", "party.members", pr.getUuid())` (the joiner's own copy always shows) |
| Left / disconnected | `LeaveCmd` (~205), `PartyQuit` (~281) | `broadcastTo(s, ..., "party.members", null)` |
| Disbanded | `LeaveCmd` (~203), `PartyQuit` (~279) | unchanged, always shown (2.3) |
| New leader | `LeaveCmd` (~208), `PartyQuit` (~284) | `broadcastTo(s, ..., "party.members", newLeader)` (the new leader always sees it) |
| Party chat | `PartyChatCmd` (~246) | `broadcast(pr.getUuid(), "[Party] ...", "party.chat", pr.getUuid())` |

`setup()`: register `party.invites`, `party.members`, `party.chat` (category `general`).

**SkyyEssentials.**
| Message | Site | Change |
|---|---|---|
| Incoming /tpa, /tpahere | `EssStore.request` (~495), **before** `tryAdd` | `if (!notifyOn(target.getUuid(), "tpa.requests")) { say(pr, "[TPA] " + them + " is not taking teleport requests.", ERR); return; }` (nothing is stored, no cooldown used) |
| Accepted | `EssStore.accept` | unchanged (2.3) |
| Denied | `EssStore.deny` (~537) | `if (notifyOn(r.from, "tpa.updates")) sayTo(r.from, ...)` |
| Expired / went offline | `EssStore.prune` (~453-458) | each `say(f, ...)` / `say(t, ...)` gets `notifyOn(<that player's uuid>, "tpa.updates")` (safe inside the `synchronized` prune: guarantee 2) |
| `/tpacancel` notice to the target ("X cancelled their teleport request.") | `TpaCancelCmd` execute loop (~642): `{ES}.sayTo(r.to, ...)` | `if ({ES}.notifyOn(r.to, "tpa.updates")) {ES}.sayTo(r.to, ...);`. `cancelFrom` and the sender's "Cancelled N teleport request(s)." reply stay unconditional. |
| After an accept: "Teleporting to X." and "Teleport cancelled: <why>" | `MoveTask.run` (~330), `MoveTask.fail` (~258-260), `ReadDestTask.fail` (~347-349), reached from both `hop()` and `run()` and from `retryLater` after 8 tries | unchanged, always shown (2.3). They are the outcome of an accepted teleport, not a request update, so `tpa.updates` does not cover them. |
| Private message | `EssStore.pm` (~540), after the existing checks, before the two `say` calls | `if (!notifyOn(target.getUuid(), "msg.private")) { say(pr, target.getUsername() + " has private messages turned off.", ERR); return; }` (`LAST_PM` is not updated). `/reply` goes through `pm()` too. If the **sender** has their own PMs off, add after a successful send: `if (!notifyOn(pr.getUuid(), "msg.private")) say(pr, "(Your own private messages are off, so replies to you are refused - /settings)", INFO);` |
| Fly disabled by permission (`FlyTask` mode 0) | - | unchanged (2.3) |

`setup()`: register `tpa.requests`, `tpa.updates`, `msg.private` (category `general`). There is no staff bypass in this version. `[SKYY?]` Should staff (`skyyessentials.fly`-level perms) always get through?

### 3.12 SkyyExploration (planned, not built: build it on the registry from day one)
Helper in its `ExpCfg`/`ExpStore` class. Register `explore.chunkXp`, `explore.finds` (category `skills`). Gate the chunk XP line (Exploration-Build-Spec 2.5) with `explore.chunkXp`. `/explore quiet` then becomes the same shortcut as 3.1: flip the key when the registry exists, else the per-profile `quiet` flag. Gate the loot chest line (2.3 step 6), chest luck (2.4), zone discovered (2.6) and new title (2.8) with `explore.finds`. The Exploration spec calls the chest line "not quiet-able". With a real settings page it becomes switchable, default ON.

### 3.13 No change
SkyyHud (no unprompted messages), SkyyBazaar (only replies and click results), SkyyAccessories (the retired-accessory line is a click reply), SkyyRolls (admin tool). SkyyMenu's own GrantTask lines are never gated (2.3).

---

## 4. UI (SkyyMenu 0.2)

### 4.1 Where it opens
- **Menu icon:** a new MENU DATA entry, next to the Mods button. LOCKED 2026-09-25 (Skyy): the Settings icon sits next to Mods. Was: slot **51**, the bottom row next to Close, the way SkyBlock puts its Redstone Torch next to Close. Mods is at slot 40. Server Setup already fills slot 41, immediately right of Mods, so the torch goes in slot **39**, immediately left of Mods. The bottom row reads Back 45, Prev 48, Close 49, Next 50. Slot 50 stays reserved for Next. SkyyMenu 0.3.2 still places the torch at slot 51.
  `("main", 39, "Furniture_Crude_Torch", "Settings", ["Turn chat messages on or off - one switch per message, for every mod.", "Your settings are the same on every profile.", "Command: /settings"], "Click to open!", "settings")`
  Build check: add `"settings"` to the allowed actions in the `ENTRIES` assert. `MenuPage.click`: `if (act.equals("settings")) { openSettings(ref, st); return; }` with
  ```java
  public void openSettings(@REF@ ref, @ST@ st) {
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (p != null) p.getPageManager().openCustomPage(ref, st, new @PKG@.SettingsPage(this.playerRef, 0));
  }
  ```
  The page is opened directly. The menu is **not** closed first (the 0.1.2 rule; SkyyHud does the same page-to-page), and this does not depend on who owns the `/settings` name.
- **Command:** `SettingsCmd`, `super("settings", "Open your settings - turn chat messages on or off")`, `addAliases(new String[] { "skysettings" })`, `setPermissionGroups(new String[] { "hytale:Adventurer" })` (command rule 1). No arguments (command rule 2 needs none). `execute` opens `new SettingsPage(pr, 0)`. On failure: `[Settings] Could not open your settings.`
- **MODS list:** SkyyMenu entry gets `"/settings (or /skysettings) - turn chat messages on or off"`. SkyySkills gets `"/skills quiet - hide the +XP messages (also in /settings)"`. SkyyTrees gets its `/tree quiet` line the same way.

### 4.2 Layout (1120 x 930, fits the verified 1120 width and 952 height)

```
+--------------------------------------------------------------------------------------------------+
| ======================================== gold accent 3 px ======================================= |
|                                         Settings  (28 bold)                                       |
|       Your own settings - the same on every profile. Click ON or OFF, it saves at once. (16)      |
|  [   Skills   ] [ Collections ] [   Sacks    ] [   Combat   ]      tab row 1 (252 x 48 each)      |
|  [   Coins    ] [  Profiles   ] [  Cooking   ] [  General   ]      tab row 2                      |
|  Skills   -   5 settings                                              (24 bold, gold)              |
|  +-----------------------------------------------------------------------------+ [ ON ] [ OFF ]   |
|  | Skill XP gains                                             (21 bold, white) |  120x52  120x52  |
|  | +12 Mining XP (340/500) while you gather, fight, smelt...  (16, grey-blue)  |                  |
|  +-----------------------------------------------------------------------------+                  |
|  ... up to 7 rows (70 px + 6 px gap) ...                                                          |
|  Always shown: the one-time note when your old Combat XP moves to your class skill.   (15, dim)   |
|                        Skill XP gains: OFF - saved.                         (status, 17 bold)     |
|  [< Prev] [Next >]   [ Reset all to defaults ]   [ < SkyWynn Menu ]   [ Close ]                   |
+--------------------------------------------------------------------------------------------------+
```

Height budget: padding 2 x 14, accent 3, title 48, hint 26, tabs 58 + 58, gap 8, header 40, rows 7 x 76 = 532, always 26, status 30, footer 62. Total 919 <= 930. Build-time assert, as the menu does with `_tall`. Width: row = 14 spacer + 774 text + 120 ON + 10 + 120 OFF = 1038 <= 1080 inner. Tabs 4 x 252 + 3 x 12 = 1044. Footer 150 + 150 + 300 + 220 + 170 + 4 x 10 = 1030.

### 4.3 Inline strings (Python constants in MENU DATA, validated like the menu's `UI` dict)
All ids start with `SkyyStg`, have no underscores, and the root anchor is Width/Height only. Button styles: `BS` = the menu's brown `TextButtonStyle` (FontSize 18). `ON_SEL` = SkyyHud's green (`#7fe07f` / text `#062a06`, hover `#a0f0a0`, pressed `#5fb05f`). `OFF_SEL` = `#e07070` / text `#2a0606`, hover `#f09090`, pressed `#b05050`. `TAB_SEL` = `#e0b060` / text `#2a1a00`. `RESET_ARM` = `#a03030` / text `#ffffff`.

| Constant | String |
|---|---|
| `UI_SROOT` | `Group #SkyyStg { Anchor: (Width: 1120, Height: 930); Background: #0b1524(0.96); Padding: (Horizontal: 20, Vertical: 14); LayoutMode: Top; }` |
| `UI_SACCENT` | `Group { Anchor: (Height: 3); Background: #e0b060; }` |
| `UI_STITLE` | `Label #SkyyStgTitle { Anchor: (Height: 48); Text: "Settings"; Style: (FontSize: 28, RenderBold: true, TextColor: #ffe9c9, HorizontalAlignment: Center, VerticalAlignment: Center); }` |
| `UI_SHINT` | `Label #SkyyStgHint { Anchor: (Height: 26); Text: ""; Style: (FontSize: 16, TextColor: #9fb8cc, HorizontalAlignment: Center, VerticalAlignment: Center); }` |
| `UI_STABS0` / `UI_STABS1` | `Group #SkyyStgTabs0 { Anchor: (Height: 58); LayoutMode: Left; Padding: (Top: 5); }` (and `...Tabs1`) |
| `UI_STAB[i]` / `UI_STABSEL[i]` | `TextButton #SkyyStgTab<i> { Anchor: (Width: 252, Height: 48); Text: "<tab text>"; ` + `BS`/`TAB_SEL` + ` }` |
| `UI_SSP12` / `UI_SSP10` / `UI_SSP14` | `Label { Anchor: (Width: 12, Height: 48); Text: ""; }` (10 x 52, 14 x 52 variants) |
| `UI_SGAP8` / `UI_SGAP6` | `Group { Anchor: (Height: 8); }` / `Group { Anchor: (Height: 6); }` |
| `UI_SHEAD` | `Label #SkyyStgHead { Anchor: (Height: 40); Text: ""; Style: (FontSize: 24, RenderBold: true, TextColor: #e0b060, VerticalAlignment: Center); }` |
| `UI_SROWS` | `Group #SkyyStgRows { Anchor: (Height: 532); LayoutMode: Top; }` |
| `UI_SROW[r]` | `Group #SkyyStgRow<r> { Anchor: (Height: 70); Background: #142030(0.92); LayoutMode: Left; Padding: (Top: 9); }` |
| `UI_STXT[r]` | `Group #SkyyStgTxt<r> { Anchor: (Width: 774, Height: 52); LayoutMode: Top; }` |
| `UI_SNAME[r]` | `Label #SkyyStgName<r> { Anchor: (Height: 28); Text: ""; Style: (FontSize: 21, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); }` |
| `UI_SDESC[r]` | `Label #SkyyStgDesc<r> { Anchor: (Height: 24); Text: ""; Style: (FontSize: 16, TextColor: #b8c8d8, VerticalAlignment: Center); }` |
| `UI_SON[r]` / `UI_SONSEL[r]` | `TextButton #SkyyStgOn<r> { Anchor: (Width: 120, Height: 52); Text: "ON"; ` + `BS`/`ON_SEL` + ` }` |
| `UI_SOFF[r]` / `UI_SOFFSEL[r]` | `TextButton #SkyyStgOff<r> { Anchor: (Width: 120, Height: 52); Text: "OFF"; ` + `BS`/`OFF_SEL` + ` }` |
| `UI_SEMPTY` | `Label #SkyyStgEmpty { Anchor: (Height: 80); Text: ""; Style: (FontSize: 19, TextColor: #c9dff0, HorizontalAlignment: Center, VerticalAlignment: Center); }` |
| `UI_SALWAYS` | `Label #SkyyStgAlways { Anchor: (Height: 26); Text: ""; Style: (FontSize: 15, TextColor: #8fa0b0, VerticalAlignment: Center); }` |
| `UI_SSTATUS` | `Label #SkyyStgStatus { Anchor: (Height: 30); Text: ""; Style: (FontSize: 17, RenderBold: true, TextColor: #ffd27f, HorizontalAlignment: Center, VerticalAlignment: Center); }` |
| `UI_SFOOT` | `Group #SkyyStgFoot { Anchor: (Height: 62); LayoutMode: Left; Padding: (Top: 6); }` |
| `UI_SPREV` / `UI_SNEXT` | `TextButton #SkyyStgPrev { Anchor: (Width: 150, Height: 50); Text: "< Prev"; BS }` / `#SkyyStgNext` `"Next >"` |
| `UI_SRESET` / `UI_SRESETARM` | `TextButton #SkyyStgReset { Anchor: (Width: 300, Height: 50); Text: "Reset all to defaults"; BS }` / same id, `Text: "Click again to reset ALL"`, `RESET_ARM` |
| `UI_SMENU` | `TextButton #SkyyStgMenu { Anchor: (Width: 220, Height: 50); Text: "< SkyWynn Menu"; BS }` |
| `UI_SCLOSE` | `TextButton #SkyyStgClose { Anchor: (Width: 170, Height: 50); Text: "Close"; BS }` |

Fixed inline text uses only characters already proven inline (letters, digits, space, `< > / -`). Everything from other mods (labels, help lines) and every sentence with `&`, `:` or `(` goes through `b.set("#Id.Text", ...)`.

**Per-tab data (MENU DATA):** `SET_CAT_ID`, `SET_TAB` (the one-word tab texts), `SET_HEAD` (headers with `&`), `SET_ALWAYS`:
- skills: `Always shown: the one-time note when your old Combat XP moves to your class skill.`
- collections: `Always shown: the one-time note about how collections count items.`
- sacks: `Always shown: the profile-changed notice on an open bag or craft page.`
- combat: `Always shown: the reminder to pick a class and admin changes to your class. Blocked hits stay blocked.`
- coins: `Always shown: coins you lose when you die, and your starter coins.`
- profiles: `Always shown: profile setup, switch problems, crash repairs and items that did not fit back.`
- cooking: `Everything on this tab can be switched off.`
- general: `Always shown: accepted teleports and how they ended, party disbanded, and replies to your own commands and clicks.`

Also `SET_ORDER` (section 2.2 keys, in order) and `SET_ROWS = 7`.

### 4.4 Behaviour
- **build():** `SetReg.drain()`, clamp `cat` and `pageNo`, append root, accent, title, hint and both tab rows. For tab `i`, append a spacer when `i % 4 != 0` and bind `#SkyyStgTab<i>` -> `EventData.of("a", "stab" + i)`. Then gap, header, rows. For each visible row `r`: store `rowKeys[r] = key`, `Boolean v = SetStore.get(u, key)` (`on = v == null || v`), append row, spacer, text group, name, desc, ON (selected if on), spacer, OFF (selected if off), gap. `b.set` the name and help. Bind `son<r>` / `soff<r>`. With no rows, append `UI_SEMPTY` and set it to `Nothing to switch here yet - the mods for this tab are not installed or not updated.`. Header text: `SET_HEAD[cat] + "   -   " + n + (n == 1 ? " setting" : " settings") + (pages > 1 ? "   -   page " + (pageNo + 1) + " of " + pages : "")`. Then the Always line, status and footer (Prev/Next only when `pages > 1`). Reset uses the armed variant while `now - armedAt <= 10000`. Bind `sprev snext sreset smenu sclose`. If `SetStore.isBroken(u)` and the status is empty, the status becomes `Your settings file could not be read - changes are not saved. Tell an admin.`
- **handleDataEvent** (match `data.indexOf(payload + "\"")`, the proven pattern; `son1"` can never match `son11"` or `soff1"`): `sclose` -> `setPage(None)`. `smenu` -> `openCustomPage(ref, st, new MenuPage(this.playerRef, "main"))`. `sreset` -> first click arms (`Click Reset again within 10 seconds to reset EVERY tab to its default.`), a second click within 10 s runs `SetStore.resetAll(u)` (`Every setting is back to its default.` or the unreadable-file text). Any other click disarms. `stab<i>` -> `cat = i; pageNo = 0`. `sprev/snext` -> page. `son<r>` / `soff<r>` -> `SetStore.set(u, rowKeys[r], on, false)`, status `<Label>: ON - saved.` / `<Label>: OFF - saved.` or the unreadable text. Every branch ends in `rebuild()` (click handlers may rebuild freely). Wrap everything in `try/catch` with `MenuUtil.warn`.
- **Never:** no MouseEntered/MouseExited bindings, no timers or periodic updates (the armed Reset reverts on the next click, not on a timer), no `setPage(None)` before opening another page. `CustomPageLifetime.CanDismiss` means Esc closes it.
- **Who sees a row.** LOCKED 2026-09-25 (Skyy), to be built: settings visibility is permission-based. A player sees only the settings they have permission to change. A basic player who is not an admin does not see admin-only or restricted settings. Those rows are hidden. The page does not draw a greyed-out or disabled entry for them. SkyyMenu 0.3.2 still lists every registered key of the open tab.
- A change made elsewhere while the page is open (`/skills quiet` in chat) shows at the next click. That is acceptable, since there are no periodic updates.

### 4.5 Build-time checks (in the SkyyMenu 0.2 script)
Copy the menu's existing checks to the new strings: balanced `{}`/`()`, no underscore in any `#Id`, no `Anchow`/`;;`, root anchor Width/Height only, height budget <= 930, and every `UI_S*` string present in `MenuData.class` after the build (the existing post-build constant-pool check). Also: `len(SET_CAT_ID) == 8`, every `SET_ORDER` key passes `validKey`, no duplicate keys, every help line in the section 2.2 table <= 90 characters (put the table in MENU DATA as `SET_KNOWN` for this check and for the admin template), slot 39 free in `main`, icon `Furniture_Crude_Torch` exists (`need_item`), and every `makeClass` is in the `writeFile` list.

---

## 5. Test checklist

### 5.1 Static (before any deploy)
1. `python tools/ci/lint.py`: 0 fails (ids, `/settings` has `setPermissionGroups`).
2. SkyyMenu 0.2 build passes every 4.5 assert. The jar loads under `-Xverify:all` with HytaleServer.jar on the classpath (the jpype harness used in earlier rounds).
3. Bare-JVM harness (jpype, `SetStore.DIR` and `ADMIN_FILE` in the scratchpad):
   a. `register` + `get`: no file -> registered default. `set(false)` -> `get` false. After 600 ms the file has `key=false` + `_v=1`.
   b. `onlyIfUnset`: after an explicit ON, `set(false, onlyIfUnset)` returns TRUE and the value stays ON.
   c. `resetAll` -> `get` = default, file keeps only the header.
   d. Unreadable file (a directory named `<uuid>.properties`, or a file held open with an exclusive lock): `get` = default, `set` = FALSE, the file is unchanged byte-for-byte, and the warn is logged once.
   e. Load order: put `settings:def:x.y` before creating the Functions -> after `drain()` the key is listed. `get` for an unregistered key with a def key registers it lazily.
   f. Admin file `skills.xpGain=false` -> `get` false without a player value. A player's explicit ON wins.
   g. Conflicting default from a second mod -> first kept, one warning.
   h. 8 threads x 10,000 `get` while another thread toggles `set`: no exception, values only ever true/false.
4. Each adopted mod: its build passes its own checks. Grep the new script: every `notifyOn(` key appears in its `regSetting(` list, and every key exists in `SET_ORDER` (a small cross-check script in the round, no build-script edits).

### 5.2 In game, one account (Skyy)
1. `/settings` opens the page: 8 tabs and rows only for installed, updated mods. `/skysettings` opens it too. The server log has no "another mod owns /settings" warning.
2. SkyWynn Menu: the torch next to Mods (slot 39) opens Settings. "< SkyWynn Menu" returns to the menu. Clicks keep working after each switch (the 0.1.2 Loading... bug must not come back).
3. Skills tab: Skill XP gains OFF -> mine stone: no `+XP` line, and XP is still earned (check `/skills`). A level-up still shows. Level-ups OFF -> the next level-up is silent and its coins are still paid (`/balance`).
4. Relog -> still OFF. Switch profile (`/profiles`) -> still OFF (per player).
5. `/skills quiet` -> the three Skills switches flip together. The page shows it after a click. `/skills quiet` again -> all ON.
6. Migration: on a test world, set `quiet=true` in `Skyy_SkyySkills/players/<uuid>.properties` while the server is stopped, start with the new jars and gain XP -> no `+XP` line, the page shows the three switches OFF, and the Skills file now says `quiet=false`. The same for `/tree quiet` and `trees.bonus`.
7. Reset all: the first click turns the button red ("Click again..."), the second resets every tab to ON. Waiting 10 s between clicks does not reset.
8. Every tab's switch, once each: Collections (gather a new item type / reach a tier), Sacks (queue ore in the Furnace, let it finish, run it dry), Classes (hit with a wrong weapon: no chat, no popup, and the hit is still blocked), Cooking (cook until a proc, Grade change), Trees (Spread/Vein Burst), Bank (`/bankconfig` with a short interval), Profiles (relog: no "Playing profile" line).
9. Always-on check: with **every** switch OFF, die with coins -> the coin-loss line still shows. `/skills` and `/pay` replies still show.
10. Remove SkyyMenu from the set (test world only) -> every message is back, no errors in the log. Put it back -> the old choices return.
11. Admin defaults: edit `settings-defaults.properties` (`party.chat=false`) -> within 30 s a fresh player sees Party chat OFF.
12. Broken file: make the player's settings file unreadable (server stopped: replace it with a folder of the same name) -> the page shows the red status, changes do not save, and the folder is untouched.

### 5.3 In game, two accounts (A = Skyy, B = second account; TEST-CHECKLIST multiplayer rule)
1. A turns Party invites OFF. B `/party invite A` -> B is told "A is not taking party invites right now". No invite is pending (`/party accept` on A says none).
2. A turns Teleport requests OFF. B `/tpa A` -> B is told. A sees nothing. Turn it back ON: `/tpa` works and B's cooldown was not used by the refusal. Then A turns Teleport request updates OFF: B `/tpa A`, B `/tpacancel` -> A sees no "cancelled their teleport request" line. B `/tpa A`, A `/tpaccept` -> both still see the accepted lines and B sees "Teleporting to A." (always shown, 2.3).
3. A turns Private messages OFF. B `/msg A hi` -> refused with the message. A `/msg B hi` works, and A gets the "(Your own private messages are off...)" note.
4. Party chat OFF on A: B `/pc hi` -> A sees nothing, B sees their own line. `party.members` OFF on A: B leaves -> A sees nothing. If A becomes leader, A still sees "A is now the party leader".
5. `coins.payReceived` OFF on A: B `/pay A 10` -> A sees no line, A's balance +10, B gets the normal reply.
6. `islands.protection` OFF on B: B visits A's island and tries to break a block -> no chat line, and the block is still protected.
7. Settings are private: B changing a switch never changes A's (two separate files in `Skyy_SkyyMenu/settings/`).

---

## 6. Open points

- LOCKED 2026-09-25 (Skyy): the Settings icon sits next to the Mods button (slot 39, left of Mods at 40). Was: slot 51, the bottom row next to Close. SkyyMenu 0.3.2 still places the torch at slot 51.
- `[SKYY?]` **Answer before the build round.** Party invites / teleport requests / private messages **refuse** when OFF (Hypixel-style privacy) instead of just hiding the line. OK? This is the only place the spec gates the action and not just the message (1.3), and it goes further than "chat notifications". Do not build these three rows on a guess: if the round has to start without an answer, leave the three keys out of `regSetting` and `SET_ORDER` (25 switches until then) and add them in a follow-up. If Skyy says **hide only**, build these rows instead:
  - `party.invites`: the invite is stored and the sender's "Invited X..." reply is unchanged. Only `target.sendMessage(... invited you to a party! ...)` in `InviteCmd.execute` (~173) gets `if ({PKG}.PartyStore.notifyOn(target.getUuid(), "party.invites"))`. Help line: `Party invites from other players - hidden invites still expire after 60 s`.
  - `tpa.requests`: `tryAdd` and both sender replies are unchanged. Only the two `say(target, ...)` request lines in `EssStore.request` (~499, ~502) get `if (notifyOn(target.getUuid(), "tpa.requests"))`. Help line: `Incoming /tpa and /tpahere requests - you can still /tpaccept a hidden one`.
  - `msg.private`: the sender's `[you -> X]` echo, `LAST_PM` and `/reply` are unchanged. Only `say(target, "[" + ... + " -> you] " + text, PM)` in `EssStore.pm` (~547) gets `if (notifyOn(target.getUuid(), "msg.private"))`. Drop the "(Your own private messages are off...)" note. Help line: `Private messages to you - the sender is not told you hid them`.
  - In each case the refusal texts go, the three 2.2 help lines change as above, section 1.1's "Some General switches refuse..." sentence goes, and the 5.3 tests 1-3 become "A sees nothing, B's command works as normal".
- `[SKYY?]` A staff bypass for the refusing switches (so an admin's `/msg` always arrives)?
- LOCKED 2026-09-25 (Skyy): the always-on list in section 2.3 stays as written. Nothing on that list becomes switchable for now.
- LOCKED 2026-09-25 (Skyy), to be built: settings visibility is permission-based. A player sees only the settings they have permission to change. A basic player who is not an admin does not see admin-only or restricted settings. Those rows are hidden. The page does not draw a greyed-out or disabled entry for them. SkyyMenu 0.3.2 still shows every registered key of the open tab.
- **Later (0.2.1+):** link rows (register with a `String` command in element 4 instead of a `Boolean`; the row shows one "Open" button that runs the command as the player without closing first): "HUD layout" -> `/skyyhud` (SkyyHud 0.3.7), "Island settings" -> `/island settings` (SkyyIslands 0.5.1), so Settings becomes the one place for every personal setting. Also a Wynncraft-style `/settings <key> on|off` for power users (needs a usage variant), and sound switches once any Skyy mod plays sounds.
- After the build: copy 1.2 into `tools/SETTINGS-CONTRACT.md`, add a TEST-CHECKLIST section from 5.2/5.3, add `SkyyMenu 0.2` to `tools/deploy_set.py`'s set, and update HANDOFF section 3. Other workflows own those files, so this spec does not touch them.
