"""Derive SkyyMenu/build_skyymenu_0.3.19.py from the LIVE SkyyMenu 0.3.18 (python tools/menu_0_3_19_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: ... -> menu_0_3_18_patch.py -> 0.3.18 (= the tools/deploy_set.py SET pin,
generated - never re-run its patch, never re-build it) -> this patch -> 0.3.19. The harness SkyyMenu/test_skyymenu_0.3.19.py is its own
file.

0.3.19 = LAG FIXES + THE HUB HOTKEY (Skyy 2026-10-13: "During/ before we consolidate the mods together, lets audit the code structure, and
make sure they are working together in the smoothest easiest lag free way possible" + "With the new 0.7.0 update, can we edit/ add our
buttons to the inventory?" -> popup "Hotkey now + probe the icon panel"; research/Code-Structure-Audit.md findings 9, 10, 17 + pattern 1,
research/Inventory-Offhand-0.7.md option d2):
 A. LOCK-FREE BRIDGE: MenuUtil.bridge() caches the skyy.bridge map in the static volatile MenuUtil.BRIDGE; only the very first call takes
    synchronized(System.class) (to create the map exactly as before, same identity); the kit's CfgRows.bridge does the same.
 B. ONE PRIVATE WRITER THREAD "SkyyMenu-IO" (MenuIO: a one-thread ScheduledThreadPoolExecutor, daemon, made on first use) for every file the
    menu reads or writes after start: the player settings saves (500 ms after a change) and the join preload, the menu layout saves (300 ms)
    and preload, the Server Setup export files, SkyyMenu's own Server Setup rows (the config kit's CfgFile.schedule - its save task - is
    pointed at MenuIO in this jar; the kit's fallback thread stays), the menu-item records (given-profile/<key>.txt) and the 30 s upkeep
    (SeenTick: retried saves, layout flush, the settings-defaults re-read) - never HytaleServer.SCHEDULED_EXECUTOR, the engine's ONE
    scheduler thread every mod and the engine share (0.3.18: an fsync there stalled every mod's timers). Same order as before (one
    thread), same files, same delays. Shutdown: the tickers stop, MenuIO drains (pending saves run, at most 2 s), then the synchronous
    flushes of 0.3.18 run as before; a task offered after that runs inline (0.3.18's "executor refused" fallback).
 C. THE MENU ITEM GRANT (GrantTask, finding 10): the file checks (the record of the profile, the 0.1-0.3.3 legacy flag migration) run on
    SkyyMenu-IO, NOT on the world thread; the task hops to the player's world thread ONLY when an item may be needed, and there it only
    counts the item and gives it (same rules: SkyyProfiles busy = wait, one held = record it, none = give one, full = message). The
    record is written back on SkyyMenu-IO (GivenSave). A profile switch between the check and the world hop sends the task back to the
    file check (the storage key is compared on the world thread).
 D. THE PROFILE WATCH (GivenTick) asks SkyyProfiles' key function only when the player's profile:epoch:<uuid> changed (a switch or a new
    profile bumps it - tools/PROFILES-CONTRACT.md rule 3); 0.3.18 called it for every online player every 2 s. Without an epoch value it
    keeps 0.3.18's check. It runs on SkyyMenu-IO.
 E. THE MENU'S SAFETY NET (MenuWatch) BACKS OFF: after 3 healthy checks in a row (the test click arrived, nothing sent since) the next
    check waits 2 s (FIX ROUND: 2 s at most); any packet the menu sends (a redraw, a heal) starts again at 1 s - a stuck page right after a
    teleport is still found within the first second. (FIX ROUND: 2 s at most - H.)
 F. THE SETTINGS / SERVER SETUP PAGES READ A SMALL INDEX (MenuIdx, finding 17) of the bridge's settings:def:* keys and config:def:<Mod>
    names instead of scanning the whole bridge (thousands of keys) at every page open. The index is built once at start (setup's drain is
    unchanged) and at the first player's arrival (on SkyyMenu-IO), and rebuilt on SkyyMenu-IO when the bridge size changed or it is older
    than 60 s (at most every 2 s); a page reads the newest index at once (the very first page open of a server run builds it in place).
 G. THE HUB HOTKEY (Skyy 2026-10-13 popup "Hotkey now + probe the icon panel"): DOUBLE-TAP CROUCH (two crouch presses within 0.4 s while
    standing on the ground - not sprinting, sliding, rolling, climbing, swimming, flying, gliding, mounted, sitting or sleeping; at most
    once every 1.5 s) opens the SkyWynn Menu. The only key gesture proven to reach the server with ANY item or an empty hand: the client's
    crouch state is sent with every movement update (the server's MovementStatesComponent - SkyySkills' sprint roll and the Monk air jump
    read the same states live; KeyProbe 0.2 recorded them), while the Ability / Use / Pick keys only reach the server when the item in
    hand has an interaction for them (research/Inventory-Offhand-0.7.md, InteractionContext.getRootInteractionId 0.7.0 bytecode).
    MenuHotkey = an EntityTickingSystem on players (one component read per player per tick; a per-player state only after the first
    crouch); the open is queued on the player's world thread (HotkeyOpen) and only happens when no other page is open. A player switch
    "Hub hotkey: double-tap crouch" (menu.hotkey, General, ON by default; admins can change the default in settings-defaults.properties).
    The menu item and /skymenu (/menu, /sbmenu) stay. The menu item's grant message names the hotkey.
 H. FIX ROUND (critic findings, 2026-10-13):
    - the hotkey never opens over an open container window (a chest, a bench, a SkyyVault / SkyyEssentials window: setPageWithWindows
      leaves getCustomPage() null) nor while SkyyProfiles is switching the player's profile (profile:busy) - same rule as /skymenu;
      every refused open is one INFO line ("hub hotkey: <player> - <why>, not opened"; at most one per cooldown per player);
    - the gesture's timing is a Server Setup row (Menu, Advanced): menu.hotkeyGapMs (200-800 ms, default 400) and menu.hotkeyCooldownMs
      (500-10000 ms, default 1500) in config.properties (hotkeyGapMs / hotkeyCooldownMs; MenuCfg.HOTKEY_GAP_MS / HOTKEY_COOLDOWN_MS,
      read live by MenuHotkey.step); the switch's server default is the menu.hotkey line of the existing Player settings defaults table;
    - the profile watch never uses up a profile change it did not act on: a refused Given.schedule (a task still pending) forgets the
      player's EPOCH so the next tick looks again, and a GrantTask that ends while the profile still wants its item (30 tries used up,
      no world, MenuIO refused) does the same - 0.3.18's every-2-s retry for exactly those cases;
    - the menu's safety net backs off to 2 s at most (1 s -> 2 s), so a click the game drops is healed within 2 s;
    - the grant message says the hotkey is a /settings switch.
No other behaviour change, no saved-data format change (one new optional settings key + two optional config.properties keys), no new
file; ROUND_PINS = {}.
Every change below is recorded (CHANGES) and undone at the end to prove the generated script is 0.3.18 outside them, byte for byte.
"""
import os
import ast

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.18.py")
dst = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.19.py")
CR, LF = chr(13), chr(10)


def load(p):
    raw = open(p, encoding="utf8", newline="").read()
    return raw.replace(CR + LF, LF), (CR + LF if (CR + LF) in raw else LF)


s, NL = load(src)
OLD = s
assert 'VERSION = "0.3.18"' in s and "0.3.18: THE HYTALE 0.7.0 PORT" in s and "MenuIO" not in s, "not the generated 0.3.18 script"
CHANGES = []            # (new text, old text) of every change, in order: undone at the end


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:120])
    s = s.replace(old, new, 1)
    CHANGES.append((new, old))


_set = None
for _n in ast.parse(open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf-8").read()).body:
    if isinstance(_n, ast.Assign) and any(isinstance(_t, ast.Name) and _t.id == "SET" for _t in _n.targets):
        _set = dict(ast.literal_eval(_n.value))
if _set is not None and _set.get("SkyyMenu") != "0.3.18":
    print("NOTE: tools/deploy_set.py SET pins SkyyMenu %s, this patch derives from 0.3.18" % _set.get("SkyyMenu"))

# ================================================================================================ docstring + version
rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.18: THE HYTALE 0.7.0 PORT''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.19: LAG FIXES + THE HUB HOTKEY (notes: tools/menu_0_3_19_patch.py; Skyy 2026-10-13 "lets audit the code structure, and make sure they
       are working together in the smoothest easiest lag free way possible" + the popup "Hotkey now + probe the icon panel"): lock-free
       bridge; one private writer thread SkyyMenu-IO (MenuIO) for every settings / layout / Server Setup / menu-item file and the 30 s
       upkeep (never HytaleServer.SCHEDULED_EXECUTOR); the menu item grant checks its files on SkyyMenu-IO and only counts / gives on the
       world thread; the profile watch acts on profile:epoch changes; the menu's safety net backs off (1 -> 2 s while healthy);
       Settings / Server Setup read a small index (MenuIdx) instead of scanning the bridge; DOUBLE-TAP CROUCH opens the SkyWynn Menu
       (MenuHotkey, player switch menu.hotkey ON by default; not over an open window; timing in Server Setup). No saved-data
       format change. ROUND_PINS = {}.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.19.py.
0.3.18: THE HYTALE 0.7.0 PORT''')
rep('VERSION = "0.3.18"\n', 'VERSION = "0.3.19"\n')

# ================================================================================================ G: the player switch + texts
rep('''    ("menu.tooltips",        "general",     "Menu hover tooltips",          "Pop-up text when you hover an item in the SkyWynn Menu - OFF stops stuck tooltips", "SkyyMenu"),
]''', '''    ("menu.tooltips",        "general",     "Menu hover tooltips",          "Pop-up text when you hover an item in the SkyWynn Menu - OFF stops stuck tooltips", "SkyyMenu"),
    # 0.3.19: the hub hotkey (Skyy 2026-10-13 "Hotkey now"): double-tap crouch while standing opens the SkyWynn Menu - ON by default
    ("menu.hotkey",          "general",     "Hub hotkey: double-tap crouch", "Tap crouch twice quickly while standing on the ground to open the SkyWynn Menu", "SkyyMenu"),
]''')
rep('''TIPS_KEY = "menu.tooltips"      # the 0.1.3 Hover Tooltips book (slot 8) and the Settings row are this one key''',
    '''TIPS_KEY = "menu.tooltips"      # the 0.1.3 Hover Tooltips book (slot 8) and the Settings row are this one key
HOTKEY_KEY = "menu.hotkey"      # 0.3.19: the hub hotkey's player switch (MenuHotkey / HotkeyOpen)
HOTKEY_GAP_MS = 400             # 0.3.19: the second crouch press must come within this many ms of the first (default; Server Setup)
HOTKEY_COOLDOWN_MS = 1500       # 0.3.19: at most one open per this many ms per player (default; Server Setup)''')
rep('''     "commands": ["/skymenu%ALIASES% - open the menu or replace a lost menu item",''',
    '''     "commands": ["/skymenu%ALIASES% - open the menu or replace a lost menu item",
                  "Double-tap crouch while standing - open the menu (switch: /settings)",''')
rep('''    this.pr.sendMessage(@MSG@.raw("[SkyWynn] You got the SkyWynn Menu! Right-click it to open teleports, your bags, skills, the bazaar and more. Lost it? Type /skymenu."));''',
    '''    this.pr.sendMessage(@MSG@.raw("[SkyWynn] You got the SkyWynn Menu! Right-click it (or double-tap crouch, if the Hub hotkey switch is on in /settings) to open teleports, your bags, skills, the bazaar and more. Lost it? Type /skymenu."));''')
rep('''F(dat, "public static final String TIPS_KEY = %s;" % jstr(TIPS_KEY))''', '''F(dat, "public static final String TIPS_KEY = %s;" % jstr(TIPS_KEY))
F(dat, "public static final String HOTKEY_KEY = %s;" % jstr(HOTKEY_KEY))          # 0.3.19
assert HOTKEY_KEY in [k[0] for k in OWN_SETTINGS], "0.3.19: the hotkey switch is one of SkyyMenu's own settings (ON by default)"''')

# ================================================================================================ G: engine tokens + probes
rep('''    "CAL":  "com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier$CalculationType",
}''', '''    "CAL":  "com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier$CalculationType",
    # 0.3.19: the hub hotkey - an EntityTickingSystem on players reading the server's copy of the client's movement states
    "ETS":  "com.hypixel.hytale.component.system.tick.EntityTickingSystem",
    "QRY":  "com.hypixel.hytale.component.query.Query",
    "ACH":  "com.hypixel.hytale.component.ArchetypeChunk",
    "CB":   "com.hypixel.hytale.component.CommandBuffer",
    "MSC":  "com.hypixel.hytale.server.core.entity.movement.MovementStatesComponent",
    "MVS":  "com.hypixel.hytale.protocol.MovementStates",
}''')
rep('''# 0.3.10: every engine member the Stats page uses''', '''# 0.3.19: every engine member the hub hotkey uses (the movement states are public fields of protocol.MovementStates)
for c, m in ((T["PLB"], "getEntityStoreRegistry"), (T["MSC"], "getComponentType"), (T["MSC"], "getMovementStates"), (T["ACH"], "getReferenceTo"),
             (T["MVS"], "crouching"), (T["MVS"], "onGround"), (T["MVS"], "sprinting"), (T["MVS"], "sliding"), (T["MVS"], "rolling"),
             (T["MVS"], "mantling"), (T["MVS"], "climbing"), (T["MVS"], "flying"), (T["MVS"], "gliding"), (T["MVS"], "swimming"),
             (T["MVS"], "inFluid"), (T["MVS"], "mounting"), (T["MVS"], "sitting"), (T["MVS"], "sleeping"), (T["ST"], "getExternalData"),
             (T["EST"], "getWorld"), (T["PGM"], "getCustomPage"), (T["PGM"], "openCustomPage"), (T["PLA"], "getWindowManager"),
             ("com.hypixel.hytale.server.core.entity.entities.player.windows.WindowManager", "getWindows")):
    B.probe(pool, c, m)
assert str(pool.get("com.hypixel.hytale.server.core.entity.entities.player.windows.WindowManager").getDeclaredMethod("getWindows").getReturnType().getName()) \\
    == "java.util.List", "FIX ROUND: WindowManager.getWindows() returns a java.util.List (0.7.0)"
assert [str(m.getName()) for m in pool.get(T["ETS"]).getDeclaredMethods() if J["Modifier"].isAbstract(m.getModifiers())] == ["tick"], \\
    "0.3.19: EntityTickingSystem's only abstract method is tick (getQuery comes from the system base)"
# 0.3.10: every engine member the Stats page uses''')

# ================================================================================================ the new classes
rep('''spt  = mk("SpawnTask")      # 0.3.18: the Spawn tile's async spawn point (Hytale 0.7.0) -> the player's world thread -> spawnResolved
''', '''spt  = mk("SpawnTask")      # 0.3.18: the Spawn tile's async spawn point (Hytale 0.7.0) -> the player's world thread -> spawnResolved
mio  = mk("MenuIO")         # 0.3.19: the private writer thread SkyyMenu-IO (every settings / layout / Server Setup / item-record file)
midx = mk("MenuIdx")        # 0.3.19: the small index of the bridge's settings:def:* keys + config:def:<Mod> names (Settings / Server Setup)
gsv  = mk("GivenSave")      # 0.3.19: writes a menu-item record on SkyyMenu-IO
mhk  = mk("MenuHotkey", T["ETS"])   # 0.3.19: the hub hotkey (double-tap crouch) - EntityTickingSystem on players
hko  = mk("HotkeyOpen")     # 0.3.19: opens the menu for the hotkey on the player's world thread
''')
rep('''         scl, stp, sta, stc, pet, lay, lsv, spt, pl)''', '''         scl, stp, sta, stc, pet, lay, lsv, spt, mio, midx, gsv, mhk, hko, pl)''')

# ================================================================================================ A: lock-free bridge
rep('''F(utl, "public static @LOG@ LOG;")
M(utl, r"""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""")''', '''F(utl, "public static @LOG@ LOG;")
# 0.3.19 A: lock-free bridge (research/Code-Structure-Audit.md pattern 1; the tools/skyycfg.py kit snippet): cached in BRIDGE after the
# first call; only that call takes the System.class monitor, to create the map exactly like before (same identity, same creation)
F(utl, "public static volatile java.util.Map BRIDGE;")
M(utl, r"""
public static java.util.Map bridge0() {
  Object o = System.getProperties().get("skyy.bridge");
  if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
  return (java.util.Map) o;
}""")
M(utl, r"""
public static java.util.Map bridge() {
  java.util.Map m = BRIDGE;
  if (m != null) return m;
  synchronized (java.lang.System.class) { m = bridge0(); }
  BRIDGE = m;
  return m;
}""")''')

# ================================================================================================ B: MenuIO + F: MenuIdx (before Given)
rep('''# ================= Given: persisted "already got the menu item" records + session guards =================''', '''# ================= 0.3.19 B: MenuIO - the private writer thread "SkyyMenu-IO" =================
# One daemon thread (a one-thread ScheduledThreadPoolExecutor, made on first use) for every file SkyyMenu reads or writes after start
# and the 30 s upkeep - never HytaleServer.SCHEDULED_EXECUTOR (the engine's one scheduler thread that every mod and the engine share).
# schedule() = false when it cannot take the task (not running: before setup or after stop) - every caller then does what 0.3.18 did
# when the shared executor refused (runs it inline). stop(): no new tasks, the queued ones run (at most waitMs), then the rest is dropped
# (the shutdown flushes of setup()'s counterpart write everything still dirty right after, as in 0.3.18).
mio.addInterface(pool.get("java.util.concurrent.ThreadFactory"))
F(mio, "public static volatile java.util.concurrent.ScheduledThreadPoolExecutor EX;")
F(mio, "public static volatile boolean STOPPED = false;")
F(mio, "public static final String NAME = \\"SkyyMenu-IO\\";")
F(mio, "public static final java.util.concurrent.atomic.AtomicLong TASKS = new java.util.concurrent.atomic.AtomicLong();")
C(mio, "public MenuIO() { }")
M(mio, r"""
public Thread newThread(Runnable r) {
  Thread t = new Thread(r, NAME);
  t.setDaemon(true);
  return t;
}""")
M(mio, r"""
public static synchronized java.util.concurrent.ScheduledThreadPoolExecutor ex0() {
  if (STOPPED) return null;
  if (EX == null) {
    java.util.concurrent.ScheduledThreadPoolExecutor e = new java.util.concurrent.ScheduledThreadPoolExecutor(1, new @PKG@.MenuIO());
    e.setRemoveOnCancelPolicy(true);
    EX = e;
  }
  return EX;
}""")
M(mio, r"""
public static java.util.concurrent.ScheduledThreadPoolExecutor ex() {
  java.util.concurrent.ScheduledThreadPoolExecutor e = EX;
  if (e != null && !STOPPED) return e;
  return ex0();
}""")
M(mio, r"""
public static boolean schedule(Runnable r, long ms) {
  if (r == null) return false;
  java.util.concurrent.ScheduledThreadPoolExecutor e = ex();
  if (e == null) return false;
  try {
    e.schedule(r, ms < 0L ? 0L : ms, java.util.concurrent.TimeUnit.MILLISECONDS);
    TASKS.incrementAndGet();
    return true;
  } catch (Throwable t) { return false; }
}""")
M(mio, r"""
public static java.util.concurrent.ScheduledFuture every(Runnable r, long firstMs, long periodMs) {
  java.util.concurrent.ScheduledThreadPoolExecutor e = ex();
  if (e == null || r == null) return null;
  try { return e.scheduleWithFixedDelay(r, firstMs, periodMs, java.util.concurrent.TimeUnit.MILLISECONDS); }
  catch (Throwable t) { return null; }
}""")
M(mio, r"""
public static boolean onIO() {
  return NAME.equals(Thread.currentThread().getName());
}""")
M(mio, r"""
public static synchronized java.util.concurrent.ScheduledThreadPoolExecutor take() {
  STOPPED = true;
  java.util.concurrent.ScheduledThreadPoolExecutor e = EX;
  EX = null;
  return e;
}""")
M(mio, r"""
public static synchronized void begin() {
  STOPPED = false;
}""")
M(mio, r"""
public static void stop(long waitMs) {
  java.util.concurrent.ScheduledThreadPoolExecutor e = take();
  if (e == null) return;
  e.shutdown();
  try { if (!e.awaitTermination(waitMs, java.util.concurrent.TimeUnit.MILLISECONDS)) e.shutdownNow(); }
  catch (InterruptedException ie) { e.shutdownNow(); }
}""")

# ================= 0.3.19 F: MenuIdx - the small index of the bridge keys the Settings / Server Setup pages need =================
# SET = every "settings:def:<key>" key, CFG = every <Mod> of a "config:def:<Mod>" key (sorted, published as new arrays - readers never
# lock). Built by scan() (one pass over a copy of the bridge's key set): at start (setup's drain does its own scan as before), at the
# first player's arrival (prime, on SkyyMenu-IO) and again on SkyyMenu-IO whenever a page asks and the bridge size changed or the index
# is older than MAX_AGE (never more than once per MIN_GAP). Only the very first page of a run with no index yet builds it in place.
midx.addInterface(pool.get("java.lang.Runnable"))
F(midx, "public static volatile String[] SET;")
F(midx, "public static volatile String[] CFG;")
F(midx, "public static volatile int SIZE = -1;")
F(midx, "public static volatile long AT = 0L;")
F(midx, "public static volatile long SCANS = 0L;")
F(midx, "public static final long MAX_AGE = 60000L;")
F(midx, "public static final long MIN_GAP = 2000L;")
F(midx, "public static final java.util.concurrent.atomic.AtomicBoolean BUSY = new java.util.concurrent.atomic.AtomicBoolean(false);")
C(midx, "public MenuIdx() { }")
M(midx, r"""
public static void scan() {
  java.util.Map br = @PKG@.MenuUtil.bridge();
  int n = br.size();
  java.util.ArrayList st = new java.util.ArrayList();
  java.util.ArrayList cf = new java.util.ArrayList();
  java.util.Iterator it = new java.util.ArrayList(br.keySet()).iterator();
  while (it.hasNext()) {
    Object k = it.next();
    if (!(k instanceof String)) continue;
    String ks = (String) k;
    if (ks.startsWith("settings:def:")) st.add(ks);
    else if (ks.startsWith("config:def:")) {
      String m = ks.substring(11);
      if (!cf.contains(m)) cf.add(m);
    }
  }
  java.util.Collections.sort(st);
  java.util.Collections.sort(cf);
  SET = (String[]) st.toArray(new String[0]);
  CFG = (String[]) cf.toArray(new String[0]);
  SIZE = n;
  AT = System.currentTimeMillis();
  SCANS = SCANS + 1L;
}""")
M(midx, r"""
public void run() {
  try { scan(); } catch (Throwable t) { @PKG@.MenuUtil.warn("settings / Server Setup index scan failed: " + t); }
  BUSY.set(false);
}""")
M(midx, r"""
public static void later() {
  if (!BUSY.compareAndSet(false, true)) return;
  if (@PKG@.MenuIO.schedule(new @PKG@.MenuIdx(), 0L)) return;
  try { scan(); } catch (Throwable t) { }
  BUSY.set(false);
}""")
M(midx, r"""
public static void prime() {
  later();
}""")
M(midx, r"""
public static void fresh() {
  if (SET == null || CFG == null) {
    try { scan(); } catch (Throwable t) { @PKG@.MenuUtil.warn("settings / Server Setup index scan failed: " + t); }
    return;
  }
  long now = System.currentTimeMillis();
  if (now - AT < MIN_GAP && now >= AT) return;
  if (@PKG@.MenuUtil.bridge().size() == SIZE && now - AT < MAX_AGE && now >= AT) return;
  later();
}""")
M(midx, r"""
public static String[] settingsKeys() {
  fresh();
  String[] a = SET;
  return a == null ? new String[0] : a;
}""")
M(midx, r"""
public static String[] configMods() {
  fresh();
  String[] a = CFG;
  return a == null ? new String[0] : a;
}""")

# ================= Given: persisted "already got the menu item" records + session guards =================''')

# ================================================================================================ D: Given.EPOCH (the profile watch)
rep('''F(giv, "public static final java.util.concurrent.ConcurrentHashMap PENDING = new java.util.concurrent.ConcurrentHashMap();")   # UUID -> Long: a GrantTask is scheduled''',
    '''F(giv, "public static final java.util.concurrent.ConcurrentHashMap PENDING = new java.util.concurrent.ConcurrentHashMap();")   # UUID -> Long: a GrantTask is scheduled
F(giv, "public static final java.util.concurrent.ConcurrentHashMap EPOCH = new java.util.concurrent.ConcurrentHashMap();")     # 0.3.19 D: UUID -> the last profile:epoch seen''')
rep('''    if (k instanceof String && ((String) k).startsWith(us)) SESSION.remove(k);
  }
  READY.remove(u);
}""")''', '''    if (k instanceof String && ((String) k).startsWith(us)) SESSION.remove(k);
  }
  READY.remove(u);
  EPOCH.remove(u);
}""")''')
rep('''  READY.keySet().retainAll(online);
}""")''', '''  READY.keySet().retainAll(online);
  EPOCH.keySet().retainAll(online);
}""")''')

# ================================================================================================ B: settings saves / preload on MenuIO
rep('''M(sst, r"""
public static void saveSoon(String k) {
  try { @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.SetSaveTask(k), 500L, java.util.concurrent.TimeUnit.MILLISECONDS); }
  catch (Throwable t) { saveNow(k); }
}""")''', '''# 0.3.19 B: on SkyyMenu-IO (0.3.18: HytaleServer.SCHEDULED_EXECUTOR); inline only when MenuIO cannot take it (stopped)
M(sst, r"""
public static void saveSoon(String k) {
  if (!@PKG@.MenuIO.schedule(new @PKG@.SetSaveTask(k), 500L)) saveNow(k);
}""")''')
rep('''    if (@PKG@.SetStore.VALS.containsKey(k) && Boolean.FALSE.equals(@PKG@.Tips.LEGACY.get(u))) return;
    @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.SetLoadTask(k, u), 0L, java.util.concurrent.TimeUnit.MILLISECONDS);''',
    '''    if (@PKG@.SetStore.VALS.containsKey(k) && Boolean.FALSE.equals(@PKG@.Tips.LEGACY.get(u))) return;
    if (!@PKG@.MenuIO.schedule(new @PKG@.SetLoadTask(k, u), 0L)) @PKG@.MenuUtil.warn("could not schedule the settings preload (SkyyMenu-IO stopped)");''')

# ================================================================================================ F: SetReg.drainIdx (the page's drain)
rep('''M(sreg, r"""
public static Object[] info(String key) {''', '''# 0.3.19 F: the Settings page's per-open drain reads the index (MenuIdx) instead of scanning the whole bridge; setup keeps drain()
M(sreg, r"""
public static void drainIdx() {
  try {
    String[] ks = @PKG@.MenuIdx.settingsKeys();
    java.util.Map br = @PKG@.MenuUtil.bridge();
    for (int i = 0; i < ks.length; i++) {
      Object v = br.get(ks[i]);
      if (v != null) register(v);
    }
  } catch (Throwable t) { @PKG@.MenuUtil.warn("settings drain failed: " + t); }
}""")
M(sreg, r"""
public static Object[] info(String key) {''')
rep('''  if (!this.drained) { this.drained = true; @PKG@.SetReg.drain(); }''', '''  if (!this.drained) { this.drained = true; @PKG@.SetReg.drainIdx(); }''')
rep('''# every mod that publishes a readable config:def:<Mod> (the pull model: scanned at every build, so load order never matters)
M(apg, r"""
public static String[] cfgMods() {
  java.util.ArrayList out = new java.util.ArrayList();
  try {
    java.util.Iterator it = new java.util.ArrayList(@MU@.bridge().keySet()).iterator();
    while (it.hasNext()) {
      Object k = it.next();
      if (!(k instanceof String) || !((String) k).startsWith("config:def:")) continue;
      String m = ((String) k).substring(11);
      if (hdr(m) != null && !out.contains(m)) out.add(m);
    }
  } catch (Throwable t) { }''', '''# every mod that publishes a readable config:def:<Mod> (the pull model; 0.3.19 F: the names come from the small index MenuIdx - kept fresh
# on SkyyMenu-IO - instead of a scan of the whole bridge at every build; each name is still checked here, hdr(m) reads its value)
M(apg, r"""
public static String[] cfgMods() {
  java.util.ArrayList out = new java.util.ArrayList();
  try {
    String[] ms = @PKG@.MenuIdx.configMods();
    for (int i = 0; i < ms.length; i++) {
      String m = ms[i];
      if (hdr(m) != null && !out.contains(m)) out.add(m);
    }
  } catch (Throwable t) { }''')

# ================================================================================================ B: layouts + Server Setup exports on MenuIO
rep('''    if (OWN.containsKey(k)) return;
    @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.LayoutSaveTask(k, true), 0L, java.util.concurrent.TimeUnit.MILLISECONDS);''',
    '''    if (OWN.containsKey(k)) return;
    if (!@PKG@.MenuIO.schedule(new @PKG@.LayoutSaveTask(k, true), 0L)) @PKG@.MenuUtil.warn("could not schedule the menu layout preload (SkyyMenu-IO stopped)");''')
rep('''public static void saveSoon(String k) {
  DIRTY.put(k, Boolean.TRUE);
  try { @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.LayoutSaveTask(k), 300L, java.util.concurrent.TimeUnit.MILLISECONDS); }
  catch (Throwable t) { saveNow(k); }
}""")''', '''public static void saveSoon(String k) {
  DIRTY.put(k, Boolean.TRUE);
  if (!@PKG@.MenuIO.schedule(new @PKG@.LayoutSaveTask(k), 300L)) saveNow(k);
}""")''')
rep('''public static void save(String name, String text) {
  try { @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.AdmSaveTask(name, text), 0L, java.util.concurrent.TimeUnit.MILLISECONDS); }
  catch (Throwable t) { new @PKG@.AdmSaveTask(name, text).run(); }
}""")''', '''public static void save(String name, String text) {
  if (!@PKG@.MenuIO.schedule(new @PKG@.AdmSaveTask(name, text), 0L)) new @PKG@.AdmSaveTask(name, text).run();
}""")''')

# ================================================================================================ B: the kit's own save task on MenuIO
rep('''assert KIT.info.get("kit", "1.0") == EXPECTED_KIT, "the emitted config kit is %s, SkyyMenu pins %s" % (KIT.info.get("kit", "1.0"), EXPECTED_KIT)''',
    '''assert KIT.info.get("kit", "1.0") == EXPECTED_KIT, "the emitted config kit is %s, SkyyMenu pins %s" % (KIT.info.get("kit", "1.0"), EXPECTED_KIT)
# 0.3.19 B: SkyyMenu's own Server Setup rows (config.properties, settings-defaults.properties) are saved by the kit's CfgSaveTask, which
# the kit schedules on HytaleServer.SCHEDULED_EXECUTOR (CfgFile.schedule). In THIS jar that one method hands the task to SkyyMenu-IO
# instead; the kit's own fallback (a daemon thread that sleeps first) stays for when MenuIO cannot take it. Same task, same delay.
_kcf = pool.get(PKG + ".CfgFile")
_ksm = [_m for _m in _kcf.getDeclaredMethods() if str(_m.getName()) == "schedule"]
assert len(_ksm) == 1 and str(_ksm[0].getSignature()) == "(IJ)V", "0.3.19: the kit's CfgFile.schedule(int, long)"
_ksm[0].setBody(jv(r"""{
  @PKG@.CfgSaveTask t = new @PKG@.CfgSaveTask($1, $2);
  if (@PKG@.MenuIO.schedule(t, $2)) return;
  t.sleepFirst = true;
  Thread th = new Thread(t, "SkyyCfg-" + @PKG@.CfgRows.MOD);
  th.setDaemon(true);
  th.start();
}"""))''')

# ================================================================================================ E: MenuWatch backs off
rep('''M(mwat, r"""
public static void schedule(@PKG@.MenuPage page) {
  if (@PKG@.PageGuard.STOP || page == null) return;
  java.util.concurrent.ScheduledExecutorService ex = @PKG@.PageGuard.EXEC;
  try {
    if (ex == null) throw new java.lang.IllegalStateException("no scheduler (SkyyMenu not set up)");
    ex.schedule(new @PKG@.MenuWatch(page, (@WLD@) null), PERIOD, java.util.concurrent.TimeUnit.MILLISECONDS);''', '''# 0.3.19 E: scheduleIn = schedule after ms (the backed-off delay of MenuPage.watchDelay); schedule = PERIOD as before
M(mwat, r"""
public static void scheduleIn(@PKG@.MenuPage page, long ms) {
  if (@PKG@.PageGuard.STOP || page == null) return;
  java.util.concurrent.ScheduledExecutorService ex = @PKG@.PageGuard.EXEC;
  try {
    if (ex == null) throw new java.lang.IllegalStateException("no scheduler (SkyyMenu not set up)");
    ex.schedule(new @PKG@.MenuWatch(page, (@WLD@) null), ms, java.util.concurrent.TimeUnit.MILLISECONDS);
  } catch (Throwable t) {
    @PKG@.PageGuard.warnOnce("the menu page check could not be scheduled (" + t + ") - the menu still works, a click the game drops is just not healed");
  }
}""")
M(mwat, r"""
public static void schedule(@PKG@.MenuPage page) {
  if (@PKG@.PageGuard.STOP || page == null) return;
  java.util.concurrent.ScheduledExecutorService ex = @PKG@.PageGuard.EXEC;
  try {
    if (ex == null) throw new java.lang.IllegalStateException("no scheduler (SkyyMenu not set up)");
    ex.schedule(new @PKG@.MenuWatch(page, (@WLD@) null), PERIOD, java.util.concurrent.TimeUnit.MILLISECONDS);''')
rep('''F(page, "public int watchFails;")
F(page, "public static final long SETTLE = 1000L;")''', '''F(page, "public int watchFails;")
# 0.3.19 E: healthy = test clicks that arrived in a row with nothing sent since (watchDelay backs off), seenSend = the lastSend those saw
F(page, "public int healthy;")
F(page, "public long seenSend;")
F(page, "public static final long SETTLE = 1000L;")''')
rep('''M(page, r"""
public boolean watchTick(@WLD@ now) {''', '''# 0.3.19 E: the next check's delay: 1 s, after 3 healthy checks in a row 2 s (any packet the menu sends starts over; FIX ROUND: 2 s at
# most, so a click the game drops is healed within 2 s)
M(page, r"""
public long watchDelay() {
  int h = this.healthy;
  if (h < 3) return @PKG@.MenuWatch.PERIOD;
  return 2L * @PKG@.MenuWatch.PERIOD;
}""")
M(page, r"""
public boolean watchTick(@WLD@ now) {''')
rep('''  long t = System.currentTimeMillis();
  if (t - this.lastSend < SETTLE) return true;
  this.probeNonce = Long.toHexString(System.nanoTime() ^ (((long) System.identityHashCode(this)) << 24));
  this.probeSeen = false;
  pm.handleLegacyCustomPageEvent(ref, st, new @CPE@(@CPT@.Data, "{\\"a\\":\\"skyymenucheck\\",\\"n\\":\\"" + this.probeNonce + "\\"}"));
  if (this.probeSeen) return true;
  if (pm.getCustomPage() != this) return false;
  this.heals = this.heals + 1;''', '''  long t = System.currentTimeMillis();
  long ls = this.lastSend;
  if (ls != this.seenSend) { this.seenSend = ls; this.healthy = 0; }
  if (t - ls < SETTLE) return true;
  this.probeNonce = Long.toHexString(System.nanoTime() ^ (((long) System.identityHashCode(this)) << 24));
  this.probeSeen = false;
  pm.handleLegacyCustomPageEvent(ref, st, new @CPE@(@CPT@.Data, "{\\"a\\":\\"skyymenucheck\\",\\"n\\":\\"" + this.probeNonce + "\\"}"));
  if (this.probeSeen) { this.healthy = this.healthy + 1; return true; }
  if (pm.getCustomPage() != this) return false;
  this.healthy = 0;
  this.heals = this.heals + 1;''')
rep('''  boolean again = false;
  try { again = this.page.watchTick(this.target); }
  catch (Throwable t) { again = this.page.watchFail(t); }
  if (again && !@PKG@.PageGuard.STOP) schedule(this.page);
}""")''', '''  boolean again = false;
  try { again = this.page.watchTick(this.target); }
  catch (Throwable t) { again = this.page.watchFail(t); }
  if (again && !@PKG@.PageGuard.STOP) scheduleIn(this.page, this.page.watchDelay());
}""")''')

# ================================================================================================ C: the grant - file checks off the world thread
rep('''# ================= Given.plan (0.3.4; after MenuCfg - it reads MenuCfg.GIVE_ITEM) =================
# what a grant does for player u whose ACTIVE profile has the storage key `key` and who holds `held` menu items (-1 = no player entity now):
#   1 = nothing to do: this session did it, the item is switched off, the profile already got it (record), or it holds one (recorded now)
#   2 = try again later: SkyyProfiles is busy with that player's inventory (profile:busy - checked BEFORE the inventory is trusted), or
#       no player entity
#   4 = give ONE now (the session mark is set first, so a full inventory is not retried on every world switch - next login)
M(giv, r"""
public static int plan(java.util.UUID u, String key, int held) {
  if (u == null || !validKey(key)) return 2;
  if (SESSION.containsKey(key)) return 1;
  if (!@PKG@.MenuCfg.GIVE_ITEM) { SESSION.put(key, Boolean.TRUE); return 1; }
  migrate(u, key);
  if (isGiven(key)) { SESSION.put(key, Boolean.TRUE); return 1; }
  if (@PKG@.MenuUtil.profileBusy(u)) return 2;
  if (held < 0) return 2;
  if (held > 0) { markGiven(key); SESSION.put(key, Boolean.TRUE); return 1; }
  SESSION.put(key, Boolean.TRUE);
  return 4;
}""")''', '''# ================= Given.plan (0.3.4; after MenuCfg - it reads MenuCfg.GIVE_ITEM) =================
# what a grant does for player u whose ACTIVE profile has the storage key `key` and who holds `held` menu items (-1 = no player entity now):
#   1 = nothing to do: this session did it, the item is switched off, the profile already got it (record), or it holds one (recorded now)
#   2 = try again later: SkyyProfiles is busy with that player's inventory (profile:busy - checked BEFORE the inventory is trusted), or
#       no player entity
#   4 = give ONE now (the session mark is set first, so a full inventory is not retried on every world switch - next login)
# 0.3.19 C: 0.3.4's plan in two halves, the same answers in the same order. planFiles = the FILE part (the legacy migration + the record),
# run on SkyyMenu-IO; planHeld = the INVENTORY part (busy, the count), run on the world thread with no file access - a held item's record
# is written back on SkyyMenu-IO (markLater; inline only when MenuIO is stopped).
gsv.addInterface(pool.get("java.lang.Runnable"))
F(gsv, "public String key;")
C(gsv, "public GivenSave(String key) { this.key = key; }")
M(gsv, r"""
public void run() {
  try { @PKG@.Given.markGiven(this.key); } catch (Throwable t) { @PKG@.MenuUtil.warn("could not save the menu-item record for " + this.key + ": " + t); }
}""")
M(giv, r"""
public static void markLater(String key) {
  if (!@PKG@.MenuIO.schedule(new @PKG@.GivenSave(key), 0L)) markGiven(key);
}""")
M(giv, r"""
public static int planFiles(java.util.UUID u, String key) {
  if (u == null || !validKey(key)) return 2;
  if (SESSION.containsKey(key)) return 1;
  if (!@PKG@.MenuCfg.GIVE_ITEM) { SESSION.put(key, Boolean.TRUE); return 1; }
  migrate(u, key);
  if (isGiven(key)) { SESSION.put(key, Boolean.TRUE); return 1; }
  return 4;
}""")
M(giv, r"""
public static int planHeld(java.util.UUID u, String key, int held) {
  if (u == null || !validKey(key)) return 2;
  if (SESSION.containsKey(key)) return 1;
  if (!@PKG@.MenuCfg.GIVE_ITEM) { SESSION.put(key, Boolean.TRUE); return 1; }
  if (@PKG@.MenuUtil.profileBusy(u)) return 2;
  if (held < 0) return 2;
  if (held > 0) { markLater(key); SESSION.put(key, Boolean.TRUE); return 1; }
  SESSION.put(key, Boolean.TRUE);
  return 4;
}""")''')
rep('''# ================= GrantTask: give the menu item once per profile (scheduler -> the player's world thread) =================
grt.addInterface(pool.get("java.lang.Runnable"))
F(grt, "public @PR@ pr;")
F(grt, "public @WLD@ expected;")
F(grt, "public int tries;")
C(grt, "public GrantTask(@PR@ pr) { this.pr = pr; this.expected = null; this.tries = 0; }")
M(grt, r"""
public void later(long ms) {
  this.expected = null;
  this.tries = this.tries + 1;
  if (this.tries < 30) @HSV@.SCHEDULED_EXECUTOR.schedule(this, ms, java.util.concurrent.TimeUnit.MILLISECONDS);
}""")
# 0 = given now, 1 = nothing to do, 2 = retry later, 3 = inventory full (retried next login) - the decision is Given.plan; ONE storage key
# for the whole grant (resolved here on the world thread, where a SkyyProfiles switch - one world task - can never be half done)
M(grt, r"""
public int grantNow(java.util.UUID u) {
  String key = @PKG@.Given.key(u);
  @PLA@ p = null;''', '''# ================= GrantTask: give the menu item once per profile (SkyyMenu-IO -> the player's world thread) =================
# 0.3.19 C: two steps. expected == null: on SkyyMenu-IO - the storage key + the file checks (Given.planFiles); nothing to do = done, else
# the key is kept and the task hops to the player's world thread. expected != null: on that world thread - the same key still active
# (else back to the file check), then count + give (Given.planHeld). Retries (1 s) go back to SkyyMenu-IO; 30 tries at most, as 0.3.18.
grt.addInterface(pool.get("java.lang.Runnable"))
F(grt, "public @PR@ pr;")
F(grt, "public @WLD@ expected;")
F(grt, "public int tries;")
F(grt, "public String key;")
C(grt, "public GrantTask(@PR@ pr) { this.pr = pr; this.expected = null; this.tries = 0; this.key = null; }")
M(grt, r"""
public boolean later(long ms) {
  this.expected = null;
  this.key = null;
  this.tries = this.tries + 1;
  if (this.tries >= 30) return false;
  return @PKG@.MenuIO.schedule(this, ms);
}""")
# 0 = given now, 1 = nothing to do, 2 = retry later, 3 = inventory full (retried next login) - the decision is Given.planHeld (the file part
# ran on SkyyMenu-IO for this.key); ONE storage key for the whole grant, compared here on the world thread, where a SkyyProfiles switch -
# one world task - can never be half done
M(grt, r"""
public int grantNow(java.util.UUID u) {
  String key = @PKG@.Given.key(u);
  if (this.key == null || !this.key.equals(key)) return 2;
  @PLA@ p = null;''')
rep('''  int held = p == null ? -1 : @PKG@.MenuUtil.count(p, @PKG@.MenuData.ITEM_ID);
  int d = @PKG@.Given.plan(u, key, held);
  if (d != 4) return d;
  if (@PKG@.MenuUtil.giveMenuItem(p)) {
    @PKG@.Given.markGiven(key);''', '''  int held = p == null ? -1 : @PKG@.MenuUtil.count(p, @PKG@.MenuData.ITEM_ID);
  int d = @PKG@.Given.planHeld(u, key, held);
  if (d != 4) return d;
  if (@PKG@.MenuUtil.giveMenuItem(p)) {
    @PKG@.Given.markLater(key);''')
rep('''M(grt, r"""
public boolean step(java.util.UUID u) {
  if (!@PKG@.Given.wants(u)) return false;
  if (this.expected == null) {
    java.util.UUID wu = this.pr.getWorldUuid();
    @WLD@ w = wu == null ? null : @UNI@.get().getWorld(wu);
    if (w == null) { later(1000L); return this.tries < 30; }
    this.expected = w;
    w.execute(this);
    return true;
  }
  java.util.UUID wu2 = this.pr.getWorldUuid();
  @WLD@ now = wu2 == null ? null : @UNI@.get().getWorld(wu2);
  if (now != this.expected) { later(1000L); return this.tries < 30; }
  if (@PKG@.Given.INFLIGHT.putIfAbsent(u, Boolean.TRUE) != null) return false;
  int res = 2;
  try { res = grantNow(u); } catch (Throwable t) { @PKG@.MenuUtil.warn("menu item grant failed for " + u + ": " + t); res = 3; }
  @PKG@.Given.INFLIGHT.remove(u);
  if (res == 2) { later(1000L); return this.tries < 30; }
  return false;
}""")''', '''M(grt, r"""
public boolean step(java.util.UUID u) {
  if (!@PKG@.Given.wants(u)) return false;
  if (this.expected == null) {
    String key = @PKG@.Given.key(u);
    int d = @PKG@.Given.planFiles(u, key);
    if (d == 1) return false;
    if (d != 4 || @PKG@.MenuUtil.profileBusy(u)) return later(1000L);
    java.util.UUID wu = this.pr.getWorldUuid();
    @WLD@ w = wu == null ? null : @UNI@.get().getWorld(wu);
    if (w == null) return later(1000L);
    this.key = key;
    this.expected = w;
    w.execute(this);
    return true;
  }
  java.util.UUID wu2 = this.pr.getWorldUuid();
  @WLD@ now = wu2 == null ? null : @UNI@.get().getWorld(wu2);
  if (now != this.expected) return later(1000L);
  if (@PKG@.Given.INFLIGHT.putIfAbsent(u, Boolean.TRUE) != null) return false;
  int res = 2;
  try { res = grantNow(u); } catch (Throwable t) { @PKG@.MenuUtil.warn("menu item grant failed for " + u + ": " + t); res = 3; }
  @PKG@.Given.INFLIGHT.remove(u);
  if (res == 2) return later(1000L);
  return false;
}""")''')
rep('''public static boolean schedule(@PR@ pr, long ms) {
  try {
    if (pr == null || !claim(pr.getUuid(), System.currentTimeMillis())) return false;
    @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.GrantTask(pr), ms, java.util.concurrent.TimeUnit.MILLISECONDS);
    return true;
  } catch (Throwable t) { @PKG@.MenuUtil.warn("could not schedule the menu item grant: " + t); return false; }
}""")''', '''public static boolean schedule(@PR@ pr, long ms) {
  try {
    if (pr == null || !claim(pr.getUuid(), System.currentTimeMillis())) return false;
    if (@PKG@.MenuIO.schedule(new @PKG@.GrantTask(pr), ms)) return true;
    PENDING.remove(pr.getUuid());
    return false;
  } catch (Throwable t) { @PKG@.MenuUtil.warn("could not schedule the menu item grant: " + t); return false; }
}""")''')

# ================================================================================================ F: prime the index at the first arrival
rep('''    if (@PKG@.MenuUtil.firstCheck()) { @PKG@.MenuUtil.checkAliases(); @PKG@.MenuUtil.checkSettingsCmd(); @PKG@.MenuUtil.checkAdminCmd(); }''',
    '''    if (@PKG@.MenuUtil.firstCheck()) { @PKG@.MenuUtil.checkAliases(); @PKG@.MenuUtil.checkSettingsCmd(); @PKG@.MenuUtil.checkAdminCmd(); @PKG@.MenuIdx.prime(); }''')

# ================================================================================================ D: the profile watch on profile:epoch
rep('''# ================= GivenTick (0.3.4): the profile watch - a profile switch or a new profile (SkyyProfiles flips profile:fn:key) needs no
# world switch to give that profile its menu item. Every 2 s, only while SkyyProfiles is loaded (without it the key never changes and
# PlayerReadyEvent covers everything), only for players past their first PlayerReadyEvent (the join path schedules those): a player whose
# CURRENT storage key has no session mark gets ONE GrantTask (Given.schedule / claim). Cheap: one bridge read + one map lookup each.
gtk.addInterface(pool.get("java.lang.Runnable"))
C(gtk, "public GivenTick() { }")
M(gtk, r"""
public void run() {
  try {
    if (!(@PKG@.MenuUtil.bridge().get("profile:fn:key") instanceof java.util.function.Function)) return;
    java.util.Iterator it = @UNI@.get().getPlayers().iterator();
    while (it.hasNext()) {
      @PR@ pr = (@PR@) it.next();
      if (pr == null || !pr.isValid()) continue;
      java.util.UUID u = pr.getUuid();
      if (!@PKG@.Given.READY.containsKey(u) || !@PKG@.Given.wants(u)) continue;
      @PKG@.Given.schedule(pr, 4000L);
    }
  } catch (Throwable t) { }
}""")''', '''# ================= GivenTick (0.3.4): the profile watch - a profile switch or a new profile (SkyyProfiles flips profile:fn:key) needs no
# world switch to give that profile its menu item. Every 2 s, only while SkyyProfiles is loaded (without it the key never changes and
# PlayerReadyEvent covers everything), only for players past their first PlayerReadyEvent (the join path schedules those): a player whose
# CURRENT storage key has no session mark gets ONE GrantTask (Given.schedule / claim).
# 0.3.19 D: SkyyProfiles bumps profile:epoch:<uuid> on every switch and every new profile (tools/PROFILES-CONTRACT.md rule 3), so the key
# function (wants) is asked only when that value changed since the last tick (Given.EPOCH; the first tick of a player counts as a change);
# no epoch published = 0.3.18's check every tick. Runs on SkyyMenu-IO (0.3.18: the shared scheduler). FIX ROUND: a schedule that is
# refused (a task still pending) forgets EPOCH[u], so the next tick looks again (GrantTask.run does the same when it ends unfinished).
gtk.addInterface(pool.get("java.lang.Runnable"))
C(gtk, "public GivenTick() { }")
M(gtk, r"""
public void run() {
  try {
    java.util.Map br = @PKG@.MenuUtil.bridge();
    if (!(br.get("profile:fn:key") instanceof java.util.function.Function)) return;
    java.util.Iterator it = @UNI@.get().getPlayers().iterator();
    while (it.hasNext()) {
      @PR@ pr = (@PR@) it.next();
      if (pr == null || !pr.isValid()) continue;
      java.util.UUID u = pr.getUuid();
      if (!@PKG@.Given.READY.containsKey(u)) continue;
      Object e = br.get("profile:epoch:" + u.toString());
      if (e != null) {
        Object was = @PKG@.Given.EPOCH.put(u, e);
        if (e.equals(was)) continue;
      }
      if (!@PKG@.Given.wants(u)) continue;
      if (!@PKG@.Given.schedule(pr, 4000L)) @PKG@.Given.EPOCH.remove(u);
    }
  } catch (Throwable t) { }
}""")''')

# ================================================================================================ G: the hub hotkey (before GrantTask)
rep('''# ================= GrantTask: give the menu item once per profile (SkyyMenu-IO -> the player's world thread) =================''',
    '''# ================= 0.3.19 G: THE HUB HOTKEY - double-tap crouch opens the SkyWynn Menu =================
# MenuHotkey: an EntityTickingSystem on every player (world thread, not parallel). Per player and tick: ONE MovementStatesComponent read
# (the server's copy of the client's movement states); a per-player state (long[3] { crouching last tick, the first press ms, the last open
# ms }) exists only after the player's first crouch (ST, keyed by the entity Ref; dead refs are dropped by SeenTick). step() = the gesture
# (pure: the harness drives it): a crouch PRESS (false -> true) on the ground with nothing else going on (still()) arms; a second press
# within MenuCfg.HOTKEY_GAP_MS fires once (MenuCfg.HOTKEY_COOLDOWN_MS between opens; both Server Setup rows, read live); a press while
# moving in another state disarms. The open itself is queued on the player's world thread (HotkeyOpen - never inside the system's tick):
# only with the player's switch on (menu.hotkey, ON by default), no other page open, NO open window (FIX ROUND: a chest / bench / vault
# window leaves getCustomPage() null) and SkyyProfiles not busy with the player, then exactly what /skymenu opens (the main view); a
# refusal is one INFO line. ON = false at shutdown.
F(mhk, "public static final java.util.concurrent.ConcurrentHashMap ST = new java.util.concurrent.ConcurrentHashMap();")
F(mhk, "public static volatile boolean ON = true;")
F(mhk, "public static volatile long FIRED = 0L;")
F(mhk, "public static volatile boolean FAILED_ONCE = false;")
C(mhk, "public MenuHotkey() { super(); }")
M(mhk, r"""
public @QRY@ getQuery() {
  return (@QRY@) @PLA@.getComponentType();
}""")
M(mhk, r"""
public static boolean still(@MVS@ m) {
  if (m == null) return false;
  return m.onGround && !m.sprinting && !m.sliding && !m.rolling && !m.mantling && !m.climbing && !m.flying && !m.gliding
      && !m.swimming && !m.inFluid && !m.mounting && !m.sitting && !m.sleeping;
}""")
M(mhk, r"""
public static boolean step(long[] s, boolean crouch, boolean ok, long now) {
  boolean was = s[0] != 0L;
  s[0] = crouch ? 1L : 0L;
  if (!crouch || was) return false;
  if (!ok) { s[1] = 0L; return false; }
  long gap = @PKG@.MenuCfg.HOTKEY_GAP_MS;
  long cd = @PKG@.MenuCfg.HOTKEY_COOLDOWN_MS;
  if (s[1] > 0L && now - s[1] >= 0L && now - s[1] <= gap && (s[2] == 0L || now - s[2] >= cd || now < s[2])) {
    s[1] = 0L;
    s[2] = now;
    return true;
  }
  s[1] = now;
  return false;
}""")
M(mhk, r"""
public static void prune() {
  java.util.Iterator it = new java.util.ArrayList(ST.keySet()).iterator();
  while (it.hasNext()) {
    Object k = it.next();
    try { if (!(k instanceof @REF@) || !((@REF@) k).isValid()) ST.remove(k); } catch (Throwable t) { ST.remove(k); }
  }
}""")
hko.addInterface(pool.get("java.lang.Runnable"))
F(hko, "public @PR@ pr;")
F(hko, "public static volatile long OPENED = 0L;")
F(hko, "public static volatile long REFUSED = 0L;")
C(hko, "public HotkeyOpen(@PR@ pr) { this.pr = pr; }")
M(hko, r"""
public static boolean wanted(java.util.UUID u) {
  if (u == null) return false;
  Boolean on = @PKG@.SetStore.get(u, @PKG@.MenuData.HOTKEY_KEY);
  return on == null || on.booleanValue();
}""")
M(hko, r"""
public static void refuse(@PR@ pr, String why) {
  REFUSED = REFUSED + 1L;
  String who = "?";
  try { who = pr.getUsername() + " (" + pr.getUuid() + ")"; } catch (Throwable t) { }
  @PKG@.MenuUtil.info("hub hotkey: " + who + " - " + why + ", not opened");
}""")
M(hko, r"""
public void run() {
  try {
    if (!@PKG@.MenuHotkey.ON || this.pr == null || !this.pr.isValid()) return;
    if (!wanted(this.pr.getUuid())) return;
    @REF@ r = this.pr.getReference();
    if (r == null || !r.isValid()) return;
    @ST@ st = r.getStore();
    if (st == null) return;
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (p == null) return;
    if (@PKG@.MenuUtil.profileBusy(this.pr.getUuid())) { refuse(this.pr, "a profile switch is running"); return; }
    @PGM@ pm = p.getPageManager();
    if (pm == null) return;
    Object cp = pm.getCustomPage();
    if (cp != null) { refuse(this.pr, "page " + cp.getClass().getSimpleName() + " is open"); return; }
    java.util.List ws = p.getWindowManager() == null ? null : p.getWindowManager().getWindows();
    if (ws != null && !ws.isEmpty()) { refuse(this.pr, ws.size() + " window(s) open (" + ws.get(0).getClass().getSimpleName() + ")"); return; }
    pm.openCustomPage(r, st, new @PKG@.MenuPage(this.pr, "main"));
    OPENED = OPENED + 1L;
  } catch (Throwable t) { @PKG@.MenuUtil.warn("the hub hotkey could not open the menu: " + t); }
}""")
M(mhk, r"""
public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {
  try {
    if (!ON) return;
    @REF@ ref = chunk.getReferenceTo(idx);
    if (ref == null) return;
    @MSC@ msc = (@MSC@) store.getComponent(ref, @MSC@.getComponentType());
    if (msc == null) return;
    @MVS@ ms = msc.getMovementStates();
    if (ms == null) return;
    long[] s = (long[]) ST.get(ref);
    if (s == null) {
      if (!ms.crouching) return;
      s = new long[3];
      ST.put(ref, s);
    }
    if (!step(s, ms.crouching, still(ms), System.currentTimeMillis())) return;
    @PR@ pr = (@PR@) store.getComponent(ref, @PR@.getComponentType());
    if (pr == null) return;
    Object ext = store.getExternalData();
    if (!(ext instanceof @EST@)) return;
    @WLD@ w = ((@EST@) ext).getWorld();
    if (w == null) return;
    FIRED = FIRED + 1L;
    w.execute(new @PKG@.HotkeyOpen(pr));
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.MenuUtil.warn("the hub hotkey check failed (logged once): " + t); }
  }
}""")

# ================= GrantTask: give the menu item once per profile (SkyyMenu-IO -> the player's world thread) =================''')

# ================================================================================================ SeenTick (on MenuIO) prunes the hotkey states
rep('''    @PKG@.MenuLayout.flushAll();
    @PKG@.MenuLayout.pruneOffline(onlineK);
    @PKG@.SetReg.loadAdmin(false);
  } catch (Throwable t) { @PKG@.MenuUtil.warn("settings upkeep failed: " + t); }
}""")''', '''    @PKG@.MenuLayout.flushAll();
    @PKG@.MenuLayout.pruneOffline(onlineK);
    @PKG@.SetReg.loadAdmin(false);
  } catch (Throwable t) { @PKG@.MenuUtil.warn("settings upkeep failed: " + t); }
  try { @PKG@.MenuHotkey.prune(); } catch (Throwable t) { }
}""")''')

# ================================================================================================ setup / shutdown
rep('''public void setup() {
  @PKG@.PageGuard.STOP = false;
  @PKG@.PageGuard.EXEC = @HSV@.SCHEDULED_EXECUTOR;''', '''public void setup() {
  @PKG@.PageGuard.STOP = false;
  @PKG@.PageGuard.EXEC = @HSV@.SCHEDULED_EXECUTOR;
  @PKG@.MenuIO.begin();
  @PKG@.MenuHotkey.ON = true;''')
rep('''  this.ticker = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.SeenTick(), 30L, 30L, java.util.concurrent.TimeUnit.SECONDS);
  this.watch = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.GivenTick(), 5L, 2L, java.util.concurrent.TimeUnit.SECONDS);''',
    '''  // 0.3.19: the 30 s upkeep (file writes) and the profile watch run on SkyyMenu-IO (0.3.18: the shared HytaleServer scheduler)
  this.ticker = @PKG@.MenuIO.every(new @PKG@.SeenTick(), 30000L, 30000L);
  this.watch = @PKG@.MenuIO.every(new @PKG@.GivenTick(), 5000L, 2000L);
  // 0.3.19 G: the hub hotkey (double-tap crouch) - a clash is logged and the menu still loads
  try { getEntityStoreRegistry().registerSystem(new @PKG@.MenuHotkey()); }
  catch (Throwable t) { @PKG@.MenuUtil.warn("could not register the hub hotkey (double-tap crouch) - the menu item and /skymenu still work: " + t); }''')
rep('''right-click the SkyWynn Menu item; the item is given once per profile;''', '''right-click the SkyWynn Menu item or double-tap crouch; the item is given once per profile;''')
rep('''protected void shutdown() {
  @PKG@.PageGuard.STOP = true;
  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  try { if (this.watch != null) this.watch.cancel(false); } catch (Throwable t) { }''', '''protected void shutdown() {
  @PKG@.PageGuard.STOP = true;
  @PKG@.MenuHotkey.ON = false;
  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  try { if (this.watch != null) this.watch.cancel(false); } catch (Throwable t) { }
  try { @PKG@.MenuIO.stop(2000L); } catch (Throwable t) { @PKG@.MenuUtil.warn("SkyyMenu-IO stop failed: " + t); }''')

# ================================================================================================ H (FIX ROUND): GrantTask.run forgets EPOCH
rep('''  if (!again && u != null) @PKG@.Given.PENDING.remove(u);
}""")''', '''  if (!again && u != null) {
    @PKG@.Given.PENDING.remove(u);
    // FIX ROUND: ended while the profile still wants its item (30 tries used up, no world, MenuIO refused): the profile watch looks again
    try { if (@PKG@.Given.wants(u)) @PKG@.Given.EPOCH.remove(u); } catch (Throwable t) { }
  }
}""")''')

# ================================================================================================ H (FIX ROUND): the hotkey timing in Server Setup
rep('''F(mcfg, "public static volatile boolean MODS_HELP = true;")''', '''F(mcfg, "public static volatile boolean MODS_HELP = true;")
F(mcfg, "public static volatile long HOTKEY_GAP_MS = %dL;" % HOTKEY_GAP_MS)            # FIX ROUND: Server Setup (menu.hotkeyGapMs)
F(mcfg, "public static volatile long HOTKEY_COOLDOWN_MS = %dL;" % HOTKEY_COOLDOWN_MS)  # FIX ROUND: Server Setup (menu.hotkeyCooldownMs)
M(mcfg, r"""
public static long num(java.util.Properties p, String k, long def, long lo, long hi) {
  String v = p.getProperty(k);
  if (v == null) return def;
  long x = def;
  try { x = Long.parseLong(v.trim()); }
  catch (Throwable t) { @PKG@.MenuUtil.warn("config.properties: " + k + "=" + v + " is not a whole number - using " + def); return def; }
  if (x < lo) { @PKG@.MenuUtil.warn("config.properties: " + k + "=" + x + " is below " + lo + " - using " + lo); return lo; }
  if (x > hi) { @PKG@.MenuUtil.warn("config.properties: " + k + "=" + x + " is above " + hi + " - using " + hi); return hi; }
  return x;
}""")''')
rep('''{ GIVE_ITEM = true; MODS_HELP = true; return; }''',
    '''{ GIVE_ITEM = true; MODS_HELP = true; HOTKEY_GAP_MS = 400L; HOTKEY_COOLDOWN_MS = 1500L; return; }''')
rep('''    MODS_HELP = flag(p, "modsHelp", true);''', '''    MODS_HELP = flag(p, "modsHelp", true);
    HOTKEY_GAP_MS = num(p, "hotkeyGapMs", 400L, 200L, 800L);
    HOTKEY_COOLDOWN_MS = num(p, "hotkeyCooldownMs", 1500L, 500L, 10000L);''')
rep('''     "field:MenuCfg.MODS_HELP@config.properties:modsHelp"),''', '''     "field:MenuCfg.MODS_HELP@config.properties:modsHelp"),
    # FIX ROUND: the hub hotkey's timing (MenuHotkey.step reads the fields live)
    ("menu.hotkeyGapMs", "Hub hotkey: double-tap gap", "menu", "int", str(HOTKEY_GAP_MS), "200", "800", "step=50", "ms", "live,adv",
     "Most time between the two crouch presses that open the SkyWynn Menu (double-tap crouch).",
     "field:MenuCfg.HOTKEY_GAP_MS@config.properties:hotkeyGapMs"),
    ("menu.hotkeyCooldownMs", "Hub hotkey: cooldown", "menu", "int", str(HOTKEY_COOLDOWN_MS), "500", "10000", "step=100", "ms", "live,adv",
     "Least time between two menu opens by double-tap crouch, per player.",
     "field:MenuCfg.HOTKEY_COOLDOWN_MS@config.properties:hotkeyCooldownMs"),''')
rep('''    "modsHelp=true",
]) + "\\n"''', '''    "modsHelp=true",
    "",
    "# hotkeyGapMs = the hub hotkey: most milliseconds between the two crouch presses (200-800). hotkeyCooldownMs = least milliseconds",
    "# between two opens per player (500-10000). Players switch the hotkey itself in /settings (Hub hotkey: double-tap crouch).",
    "hotkeyGapMs=%d" % HOTKEY_GAP_MS,
    "hotkeyCooldownMs=%d" % HOTKEY_COOLDOWN_MS,
]) + "\\n"''')

assert "HOTKEY_GAP_MS = 400 " in s and "HOTKEY_COOLDOWN_MS = 1500 " in s, "FIX ROUND: MenuCfg.load's Java defaults (400L / 1500L) are these"

# FIX ROUND 2 (critic: world-thread stall): Given.claim runs on the player's world thread (MenuReady -> Given.schedule), while the
# file helpers (isGiven / markGiven / hasAnyFor / migrate, static synchronized on Given.class) now run on SkyyMenu-IO. claim no longer
# takes that monitor: a lock-free putIfAbsent / replace loop on the ConcurrentHashMap PENDING gives the same answer (one claim per
# player, an entry older than 90 s is stale and may be taken over), so a join never waits for a record write or the legacy-flag scan.
rep('''public static synchronized boolean claim(java.util.UUID u, long now) {
  if (u == null) return false;
  Object o = PENDING.get(u);
  if (o instanceof Long && now - ((Long) o).longValue() < 90000L) return false;
  PENDING.put(u, Long.valueOf(now));
  return true;
}''', '''public static boolean claim(java.util.UUID u, long now) {
  if (u == null) return false;
  Long nv = Long.valueOf(now);
  for (int i = 0; i < 16; i++) {
    Object o = PENDING.get(u);
    if (o == null) {
      if (PENDING.putIfAbsent(u, nv) == null) return true;
    } else {
      if (o instanceof Long && now - ((Long) o).longValue() < 90000L) return false;
      if (PENDING.replace(u, o, nv)) return true;
    }
  }
  return false;
}''')

# ================================================================================================ checks on the result
_java = s[s.index("# ================= javassist ================="):]
assert "SCHEDULED_EXECUTOR.schedule(new @PKG@.SetSaveTask" not in s and "SCHEDULED_EXECUTOR.schedule(new @PKG@.LayoutSaveTask" not in s \
    and "SCHEDULED_EXECUTOR.schedule(new @PKG@.AdmSaveTask" not in s and "SCHEDULED_EXECUTOR.schedule(new @PKG@.GrantTask" not in s \
    and "SCHEDULED_EXECUTOR.schedule(new @PKG@.SetLoadTask" not in s and "SCHEDULED_EXECUTOR.schedule(this" not in s.split("# ================= GrantTask")[1].split("# ================= MenuReady")[0], \
    "0.3.19 B: no settings / layout / Server Setup / grant task on HytaleServer.SCHEDULED_EXECUTOR"
assert "scheduleAtFixedRate(new @PKG@.SeenTick()" not in s and "scheduleAtFixedRate(new @PKG@.GivenTick()" not in s, "0.3.19: the tickers on MenuIO"
assert _java.count("new java.util.ArrayList(br.keySet())") == 2 and _java.count("new java.util.ArrayList(@MU@.bridge().keySet())") == 0, \
    "0.3.19 F: the bridge key scans: setup's drain + MenuIdx.scan only"
assert "Given.plan(" not in s, "0.3.19 C: plan is split into planFiles / planHeld"
for _a, _b in (("public static boolean schedule(Runnable r, long ms)", "public static void saveSoon(String k) {\n  if (!@PKG@.MenuIO"),
               ("public static String[] settingsKeys()", "public static void drainIdx()"), ("public static String[] configMods()", "public static String[] cfgMods()"),
               ("public static void markLater(String key)", "public int grantNow("), ("public static int planFiles(", "public boolean step("),
               ("public long watchDelay()", "scheduleIn(this.page, this.page.watchDelay())"), ("public static void scheduleIn(", "public static void schedule(@PKG@.MenuPage page)"),
               ("public static boolean wanted(java.util.UUID u)", "public void tick(float dt"), ("public static void prune()", "@PKG@.MenuHotkey.prune();"),
               ("public static void prime()", "@PKG@.MenuIdx.prime();")):
    assert s.index(_a) < s.index(_b), "definitions before use: %s" % _a
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.3.18 outside the recorded changes"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(dst, ROOT), "(%d lines; 0.3.18 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
