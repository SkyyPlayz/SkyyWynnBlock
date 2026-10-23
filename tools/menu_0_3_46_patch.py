"""Derive SkyyMenu/build_skyymenu_0.3.46.py from the LIVE SkyyMenu 0.3.45 (python tools/menu_0_3_46_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: ... -> menu_0_3_45_patch.py -> 0.3.45 (= the tools/deploy_set.py SET pin,
generated - never re-run its patch) -> this patch -> 0.3.46. Every anchor is asserted once; at the end every change is undone on a copy and
compared with 0.3.45 (nothing else changed). Line endings kept. The harness SkyyMenu/test_skyymenu_0.3.46.py is its own file.

0.3.46 (2026-10-23) = NO MORE MENU ITEM IN THE HOTBAR (LEAN round menu046). Skyy 2026-10-23: "now that the menu opens with Lalt, we dont
  need the item in the hot bar to open it." (Left Alt opening the SkyWynn Menu is VERIFIED live.)
  1. NO GIVE: Server Setup -> Menu -> "Give the menu item" (menu.giveItem / config.properties giveItem) now defaults OFF. Off = no profile
     gets the item at its first join, and /skymenu (/menu /sbmenu /menuitem) only opens the Menu - it no longer hands out a "lost" item.
     On (an admin's choice) = 0.3.45 exactly (once per profile, /skymenu gives a lost one back).
  2. ONE-TIME SETTING UPDATE (PROJECT-RULES 4): at start, ONCE (marker Skyy_SkyyMenu/menuitem-off/config-giveitem.done): a config.properties
     whose ONLY giveItem line is still the old default "giveItem=true" gets exactly that line rewritten to "giveItem=false" (every other
     byte and line ending kept) after a VERIFIED History copy (config-history/, read back + compared; a failed copy = no write, tried
     again at the next start) and a Server Setup -> Changes line menu.giveItem true -> false (status ok = Undo button). Any other giveItem
     line (hand-edited: false / on / " = true" / two lines) is kept and logged. No file yet = the new default file says giveItem=false.
  3. OLD COPIES TAKEN ONCE: while giveItem is OFF, a player's first join (the 0.3.4 grant path: PlayerReadyEvent / the profile watch ->
     GrantTask: files on SkyyMenu-IO, inventory on the world thread, waits out profile:busy) takes every stack of EXACTLY Skyy_Menu out of
     the live inventory (hotbar, storage, backpack, utility, tools - count before and after; Skyy_Menu_Icon_* and every other id
     untouched), logs the count (one INFO line, also for 0), tells the player once (only when something was taken) and writes the per-
     PLAYER run-once marker Skyy_SkyyMenu/menuitem-off/<uuid>.done (on SkyyMenu-IO). A second join (same run: memory; after a restart: the
     marker) takes nothing - a copy the player gets later stays. A copy left behind (removal refused) = no marker, tried again next login.
     SkyyProfiles' keepItems=Skyy_Menu keeps the item out of every profile file, so the live inventory holds every copy a player has.
  4. THE ITEM STAYS DEFINED (Server/Item/Items/Utility/Skyy_Menu.json unchanged: an old stack in a chest is never an unknown item) and
     harmless: right-click still opens the Menu; its tooltip now says Left Alt / /skymenu open the Menu too. The lifelong rules
     (menu.itemKeep, tools/skyyonce.py) are unchanged: they never give one out of nothing.
  5. THE LEFT-ALT PATH IS UNTOUCHED (MenuHotkey / HotkeyOpen byte-identical to 0.3.45 - the harness compare proves it).
  SAVED DATA: new folder Skyy_SkyyMenu/menuitem-off/ (markers only); config.properties giveItem line (2.). No new class / command / system.
  ROLLBACK to 0.3.45: safe alone - but 0.3.45 reads giveItem=false and gives nothing either; Undo the menu.giveItem line in Server Setup
  -> Changes (or set Give the menu item ON) first if players should get the item again. Taken copies are not given back by a rollback.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

P = G.Patch(os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.45.py"), os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.46.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.3.45"\n') and P.has("tools/menu_0_3_45_patch.py") and not P.has("menuitem-off"), "not the generated SkyyMenu 0.3.45 script"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")

P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.46: no more menu item in the hotbar - Left Alt opens the Menu (Skyy 2026-10-23): giveItem defaults OFF (one-time update of the old
       default line), /skymenu no longer gives one, old copies taken out once per player; the item stays defined + still opens the Menu
       (notes: tools/menu_0_3_46_patch.py).
  CHECKED: see SkyyMenu/test_skyymenu_0.3.46.py.
''')
P.rep('VERSION = "0.3.45"\n', 'VERSION = "0.3.46"\n')

# ---------- texts: the item's tooltip, the main view intro, the Mods line, the Server Setup rows, the default config file
P.rep('''"\\\\n\\\\nIt stays with you: it can't be dropped, stored or sold. Lost it anyway? Type /menuitem (or /skymenu) to get a new one.")''',
      '''"\\\\n\\\\nYou don't need it any more: Left Alt (your Walk key) or /skymenu opens the menu too.")          # 0.3.46''')
P.rep('''                                   "Lost your menu item? Type /skymenu to get a new one."]),''',
      '''                                   "Press Left Alt (your Walk key) or type /skymenu to open this menu."]),          # 0.3.46''')
P.rep('''     "commands": ["/skymenu%ALIASES% - open the menu or get the item back",   # 0.3.32: shorter (+ /menuitem fits 80)''',
      '''     "commands": ["/skymenu%ALIASES% - open the menu",   # 0.3.32: shorter (+ /menuitem fits 80); 0.3.46: no item handed out''')
P.rep('''    ("menu.giveItem", "Give the menu item", "menu", "bool", "true", "", "", "", "", "live",
     "Every profile gets the SkyWynn Menu item the first time it is used. Off: only /skymenu gives one.",''',
      '''    ("menu.giveItem", "Give the menu item", "menu", "bool", "false", "", "", "", "", "live",          # 0.3.46: OFF (Left Alt opens the Menu)
     "On: each profile gets the item once, /skymenu gives a lost one. Off: no item, old copies taken once.",''')
P.rep('''     "Never dropped, stored or sold; one per profile (extras removed); /menuitem brings it back.",''',
      '''     "Never dropped, stored or sold; one per profile (extras removed); /skymenu gives one if Give is on.",''')
P.rep('''    "# giveItem = give new players the SkyWynn Menu item at their first join (true or false). /skymenu always gives a lost one back.",
    "giveItem=true",''', '''    "# giveItem = give every profile the SkyWynn Menu item at its first join, and /skymenu gives a lost one back (true or false). Off:",
    "# no item (Left Alt opens the menu) and old copies are taken out of each player's inventory once.",
    "giveItem=false",''')
P.rep('''    "# are removed) and /menuitem gives it back (true or false).",''',
      '''    "# are removed) and /skymenu gives it back while giveItem is on (true or false).",''')

# ---------- MenuCfg: the default OFF
P.rep('F(mcfg, "public static volatile boolean GIVE_ITEM = true;")',
      'F(mcfg, "public static volatile boolean GIVE_ITEM = false;")          # 0.3.46: OFF (Server Setup menu.giveItem)')
P.rep("{ GIVE_ITEM = true; MODS_HELP = true; KEEP_ITEM = true;", "{ GIVE_ITEM = false; MODS_HELP = true; KEEP_ITEM = true;")
P.rep('    GIVE_ITEM = flag(p, "giveItem", true);\n', '    GIVE_ITEM = flag(p, "giveItem", false);   // 0.3.46\n')

# ---------- the engine member the removal uses
P.rep('''             (T["IC"], "getItemStack"), (T["IC"], "addItemStack"), (T["IC"], "addItemStackToSlot"), (T["IC"], "getCapacity"),''',
      '''             (T["IC"], "getItemStack"), (T["IC"], "addItemStack"), (T["IC"], "addItemStackToSlot"), (T["IC"], "getCapacity"),
             (T["IC"], "removeItemStackFromSlot"),          # 0.3.46: old menu items taken once''')

# ---------- MenuUtil.removeAll (world thread): every stack of exactly `id` out of the five sections; returns how many left (read back)
P.rep('''# 0.3.30: items whose id starts with a prefix (Right now: SkyyGear's mystery bags Skyy_Unid_Bag_<Rarity>) - world thread only''',
      '''# 0.3.46: take every stack of EXACTLY id out of one section (world thread only); returns how many it took (read back per slot)
M(utl, r"""
public static int removeIn(@IC@ c, String id) {
  if (c == null || id == null) return 0;
  int n = 0;
  short cap = c.getCapacity();
  for (short s = 0; s < cap; s++) {
    @IS@ it = c.getItemStack(s);
    if (it == null || it.isEmpty() || !id.equals(it.getItemId())) continue;
    int q = it.getQuantity();
    try { c.removeItemStackFromSlot(s, q); } catch (Throwable t) { warn("could not take " + id + " out of a slot: " + t); continue; }
    @IS@ after = c.getItemStack(s);
    if (after == null || after.isEmpty() || !id.equals(after.getItemId())) n += q;
    else n += q - after.getQuantity();
  }
  return n;
}""")
M(utl, r"""
public static int removeAll(@PLA@ p, String id) {
  @INV@ inv = p == null ? null : p.getInventory();
  if (inv == null) return 0;
  return removeIn(inv.getHotbar(), id) + removeIn(inv.getStorage(), id) + removeIn(inv.getBackpack(), id)
       + removeIn(inv.getUtility(), id) + removeIn(inv.getTools(), id);
}""")
# 0.3.30: items whose id starts with a prefix (Right now: SkyyGear's mystery bags Skyy_Unid_Bag_<Rarity>) - world thread only''')

# ---------- Given: the per-player run-once markers (OFF = Skyy_SkyyMenu/menuitem-off/<uuid>.done) + this run's memory
P.rep('''F(giv, "public static java.nio.file.Path LEGACY;")''',
      '''F(giv, "public static java.nio.file.Path LEGACY;")
F(giv, "public static java.nio.file.Path OFF;")          # 0.3.46: Skyy_SkyyMenu/menuitem-off/ (<uuid>.done = old menu items taken once)
F(giv, "public static final java.util.concurrent.ConcurrentHashMap REMOVED = new java.util.concurrent.ConcurrentHashMap();")   # 0.3.46: UUID -> TRUE: taken this run''')
P.rep('''# a per-profile record of ANY profile of this player (<uuid>.txt or <uuid>-p<N>.txt); a read error answers true (= migrate nothing)''',
      '''# 0.3.46: the per-PLAYER run-once marker of the old-menu-item removal (SkyyMenu-IO only; a read error answers true = take nothing)
M(giv, r"""
public static synchronized boolean isRemoved(java.util.UUID u) {
  if (u == null || OFF == null) return true;
  try { return java.nio.file.Files.exists(OFF.resolve(u.toString() + ".done"), new java.nio.file.LinkOption[0]); }
  catch (Throwable t) { return true; }
}""")
M(giv, r"""
public static synchronized boolean markRemoved(String us, int n) {
  try {
    if (OFF == null || us == null || !validKey(us)) return false;
    java.nio.file.Path f = OFF.resolve(us + ".done");
    if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return true;
    java.nio.file.Files.createDirectories(OFF, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = OFF.resolve(us + ".done.tmp");
    byte[] data = ("old SkyWynn Menu items taken: " + n + " at " + System.currentTimeMillis() + " (SkyyMenu 0.3.46, once)\\n").getBytes("UTF-8");
    java.nio.file.Files.write(tmp, data, new java.nio.file.OpenOption[0]);
    java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
    return true;
  } catch (Throwable t) { @PKG@.MenuUtil.warn("could not save the menu-item removal marker for " + us + ": " + t); return false; }
}""")
# a per-profile record of ANY profile of this player (<uuid>.txt or <uuid>-p<N>.txt); a read error answers true (= migrate nothing)''')

# ---------- GivenSave: also writes the removal marker (off != null)
P.rep('''F(gsv, "public String key;")
C(gsv, "public GivenSave(String key) { this.key = key; }")
M(gsv, r"""
public void run() {
  try { @PKG@.Given.markGiven(this.key); }''', '''F(gsv, "public String key;")
F(gsv, "public String off;")          # 0.3.46: non-null = the removal marker of player `off` (taken = n)
F(gsv, "public int n;")
C(gsv, "public GivenSave(String key) { this.key = key; this.off = null; this.n = 0; }")
C(gsv, "public GivenSave(String us, int n) { this.key = us; this.off = us; this.n = n; }")
M(gsv, r"""
public void run() {
  if (this.off != null) { @PKG@.Given.markRemoved(this.off, this.n); return; }
  try { @PKG@.Given.markGiven(this.key); }''')
P.rep('''M(giv, r"""
public static void markLater(String key) {
  if (!@PKG@.MenuIO.schedule(new @PKG@.GivenSave(key), 0L)) markGiven(key);
}""")''', '''M(giv, r"""
public static void markLater(String key) {
  if (!@PKG@.MenuIO.schedule(new @PKG@.GivenSave(key), 0L)) markGiven(key);
}""")
M(giv, r"""
public static void removedLater(java.util.UUID u, int n) {
  if (u == null) return;
  if (!@PKG@.MenuIO.schedule(new @PKG@.GivenSave(u.toString(), n), 0L)) markRemoved(u.toString(), n);
}""")''')

# ---------- the plan: OFF = 5 (take the old copies once) until this player's marker exists
P.rep('''  if (SESSION.containsKey(key)) return 1;
  if (!@PKG@.MenuCfg.GIVE_ITEM) { SESSION.put(key, Boolean.TRUE); return 1; }
  migrate(u, key);''', '''  if (SESSION.containsKey(key)) return 1;
  if (!@PKG@.MenuCfg.GIVE_ITEM) {          // 0.3.46: no item - the old copies are taken ONCE per player (5), then nothing
    if (REMOVED.containsKey(u) || isRemoved(u)) { REMOVED.put(u, Boolean.TRUE); SESSION.put(key, Boolean.TRUE); return 1; }
    return 5;
  }
  migrate(u, key);''')
P.rep('''  if (!@PKG@.MenuCfg.GIVE_ITEM) { SESSION.put(key, Boolean.TRUE); return 1; }
  if (@PKG@.MenuUtil.profileBusy(u)) return 2;''', '''  if (!@PKG@.MenuCfg.GIVE_ITEM) {          // 0.3.46: the IO step found no marker; the inventory is trusted only when not busy
    if (REMOVED.containsKey(u)) { SESSION.put(key, Boolean.TRUE); return 1; }
    if (@PKG@.MenuUtil.profileBusy(u)) return 2;
    if (held < 0) return 2;
    return 5;
  }
  if (@PKG@.MenuUtil.profileBusy(u)) return 2;''')

# ---------- GrantTask: the removal step (world thread) + the IO step hops for 5 too
P.rep('''# 0 = given now, 1 = nothing to do, 2 = retry later, 3 = inventory full (retried next login) - the decision is Given.planHeld (the file part''',
      '''# 0.3.46: Given.planHeld said 5 - take every Skyy_Menu out of the live inventory (count before + after), log the count, tell the player
# (only when something was taken), mark the PLAYER done (memory now, the marker file on SkyyMenu-IO). A copy left = no marker (next login).
M(grt, r"""
public int removeNow(java.util.UUID u, String key, @PLA@ p, int held) {
  String id = @PKG@.MenuData.ITEM_ID;
  int took = held > 0 ? @PKG@.MenuUtil.removeAll(p, id) : 0;
  int left = @PKG@.MenuUtil.count(p, id);
  @PKG@.Given.SESSION.put(key, Boolean.TRUE);
  if (left > 0) {
    @PKG@.MenuUtil.warn("menu item: " + left + " old SkyWynn Menu item(s) of " + this.pr.getUsername() + " (" + u + ") could not be taken (" + took + " taken) - tried again at their next join");
    return 1;
  }
  int n = held - left;
  @PKG@.Given.REMOVED.put(u, Boolean.TRUE);
  @PKG@.Given.removedLater(u, n);
  @PKG@.MenuUtil.info("menu item: took " + n + " old SkyWynn Menu item(s) from " + this.pr.getUsername() + " (" + u + ") - once per player (Server Setup giveItem is off; Left Alt / /skymenu open the Menu)");
  if (n > 0) this.pr.sendMessage(@MSG@.raw("[SkyWynn] You don't need the SkyWynn Menu item any more, so it was taken out of your inventory. Press Left Alt (your Walk key) or type /skymenu to open the menu."));
  return 1;
}""")
# 0 = given now, 1 = nothing to do, 2 = retry later, 3 = inventory full (retried next login) - the decision is Given.planHeld (the file part''')
P.rep('''  int d = @PKG@.Given.planHeld(u, key, held);
  if (d != 4) return d;''', '''  int d = @PKG@.Given.planHeld(u, key, held);
  if (d == 5) return removeNow(u, key, p, held);          // 0.3.46
  if (d != 4) return d;''')
P.rep('''    if (d != 4 || @PKG@.MenuUtil.profileBusy(u)) return later(1000L);''',
      '''    if ((d != 4 && d != 5) || @PKG@.MenuUtil.profileBusy(u)) return later(1000L);          // 0.3.46: 5 = take the old copies''')

# ---------- /skymenu: opens the Menu; gives a lost item only while giveItem is ON
P.rep('''  super("skymenu", "Open the SkyWynn menu (gives you a new menu item if you lost it)");''',
      '''  super("skymenu", "Open the SkyWynn menu (Left Alt opens it too)");          // 0.3.46''')
P.rep('''    boolean none = @PKG@.MenuUtil.count(player, @PKG@.MenuData.ITEM_ID) <= 0;''',
      '''    boolean none = @PKG@.MenuCfg.GIVE_ITEM && @PKG@.MenuUtil.count(player, @PKG@.MenuData.ITEM_ID) <= 0;          // 0.3.46: no give while OFF''')

# ---------- the one-time giveItem update (after MenuLayout.history: it uses the verified History copy)
P.rep('''# the History copy before the update's first write - ONCE per file (fix round): SNAPPED FALSE right after the copy is verified, so a''',
      '''# 0.3.46 THE ONE-TIME giveItem UPDATE (PROJECT-RULES 4) - setup(), before MenuCfg.init / load and the config kit: run-once marker
# menuitem-off/config-giveitem.done; ONLY a single giveItem line that still reads exactly "giveItem=true" (the old default) is rewritten
# to "giveItem=false" (the rest of the file byte for byte, line endings kept), after the VERIFIED History copy; one Changes line
# menu.giveItem true -> false, status ok (Undo). Anything else is kept + logged. A failure = nothing written, no marker (next start).
M(mcfg, r"""
public static String migrateGive() {
  java.nio.file.Path f = FILE;
  if (f == null) return "no file";
  java.nio.file.Path mk = f.resolveSibling("menuitem-off").resolve("config-giveitem.done");
  try {
    if (java.nio.file.Files.exists(mk, new java.nio.file.LinkOption[0])) return "done before";
    String res = null;
    if (!java.nio.file.Files.isRegularFile(f, new java.nio.file.LinkOption[0])) res = "no config.properties yet - the new default file says giveItem=false";
    else {
      byte[] b = java.nio.file.Files.readAllBytes(f);
      String s = new String(b, "ISO-8859-1");
      int at = -1;
      int hits = 0;
      String seen = null;
      int i = 0;
      while (i < s.length()) {
        int e = s.indexOf('\\n', i);
        int end = e < 0 ? s.length() : e;
        int le = end;
        if (le > i && s.charAt(le - 1) == '\\r') le = le - 1;
        String line = s.substring(i, le);
        String t = line.trim();
        if (t.length() > 0 && !t.startsWith("#") && !t.startsWith("!")) {
          int q = t.length();
          for (int k = 0; k < t.length(); k++) {
            char c = t.charAt(k);
            if (c == '=' || c == ':' || c == ' ' || c == '\\t') { q = k; break; }
          }
          if ("giveItem".equals(t.substring(0, q))) {
            hits = hits + 1;
            seen = t;
            if ("giveItem=true".equals(line)) at = i;
          }
        }
        if (e < 0) break;
        i = e + 1;
      }
      if (hits == 1 && at >= 0) {
        @PKG@.MenuLayout.history(f, "config.properties", "before the SkyyMenu 0.3.46 update (giveItem true -> false: Left Alt opens the Menu)");
        String ns = s.substring(0, at) + "giveItem=false" + s.substring(at + 13);
        @PKG@.MenuUtil.atomicWrite(f, ns.getBytes("ISO-8859-1"));
        @PKG@.CfgLog.add(null, "SkyyMenu update", "update", "menu.giveItem", "true", "false", "ok");
        res = "giveItem=true (the old default) -> giveItem=false (History copy made; Undo in Server Setup - Changes)";
      } else if (hits == 0) res = "no giveItem line - the new default (off) applies";
      else res = "giveItem kept as it was set (" + (hits > 1 ? hits + " giveItem lines" : seen) + ")";
    }
    @PKG@.MenuUtil.atomicWrite(mk, ("SkyyMenu 0.3.46 giveItem update: " + res + " - " + System.currentTimeMillis() + "\\n").getBytes("UTF-8"));
    @PKG@.MenuUtil.info("menu item update (once): " + res);
    return res;
  } catch (Throwable t) {
    @PKG@.MenuUtil.warn("the one-time giveItem update failed (" + t + ") - config.properties is unchanged; tried again at the next start");
    return "failed";
  }
}""")
# the History copy before the update's first write - ONCE per file (fix round): SNAPPED FALSE right after the copy is verified, so a''')

# ---------- setup: the marker folder + the update before MenuCfg.init; the ready line
P.rep('''  @PKG@.Given.LEGACY = getDataDirectory().resolveSibling("Skyy_SkyyMenu").resolve("given");
''', '''  @PKG@.Given.LEGACY = getDataDirectory().resolveSibling("Skyy_SkyyMenu").resolve("given");
  @PKG@.Given.OFF = getDataDirectory().resolveSibling("Skyy_SkyyMenu").resolve("menuitem-off");          // 0.3.46
''')
P.rep('''  @PKG@.MenuCfg.FILE = getDataDirectory().resolveSibling("Skyy_SkyyMenu").resolve("config.properties");
  @PKG@.MenuCfg.init();''', '''  @PKG@.MenuCfg.FILE = getDataDirectory().resolveSibling("Skyy_SkyyMenu").resolve("config.properties");
  @PKG@.MenuCfg.migrateGive();          // 0.3.46: giveItem's old default -> off, once
  @PKG@.MenuCfg.init();''')
P.rep('''right-click the SkyWynn Menu item, the Walk key (Alt) or double-tap crouch; the item is given once per profile; /settings''',
      '''the Walk key (Alt), double-tap crouch or the SkyWynn Menu item; menu item " + (@PKG@.MenuCfg.GIVE_ITEM ? "given once per profile" : "off (old copies taken once per player)") + "; /settings''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.3.46 adds no system / command"
_i = P.s.index
assert _i("public static int removeIn(") < _i("public static int removeAll(") < _i("public int removeNow(") < _i("public int grantNow(")
assert _i("public static synchronized boolean markRemoved(") < _i("public GivenSave(String us, int n)") < _i("public static void removedLater(") < _i("public int removeNow(")
assert _i("public static java.nio.file.Path history(") < _i("public static String migrateGive(")
P.finish()
