"""Derive SkyyMenu/build_skyymenu_0.3.42.py from the LIVE SkyyMenu 0.3.41 (python tools/menu_0_3_42_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: ... -> menu_0_3_41_patch.py -> 0.3.41 (= the tools/deploy_set.py SET pin,
generated - never re-run its patch) -> this patch -> 0.3.42. Every anchor is asserted once; at the end every change is undone on a copy and
compared with 0.3.41 (nothing else changed). Line endings kept. The harness SkyyMenu/test_skyymenu_0.3.42.py is its own file.

0.3.42 (2026-10-22) = THE WALK KEY (LEFT ALT) OPENS THE SKYWYNN MENU.
  Skyy (2026-10-22): "they were able to tie the menu to Left alt" and, asked which trigger, "just pressing Lalt is fine. i dont know anyone
  who actually uses a walk key". Study (read-only, ideas only): RPG Leveling 0.4.2 MenuHotkeyWalkSystem / WalkLatch - Alt is Hytale's
  default WALK key, the client reports it as protocol.MovementStates.walking (held: their code has onWalkPressed / onWalkReleased), the
  server keeps it in MovementStatesComponent (research/UI-Ideas.md 2026-10-22).
  HOW: the existing 0.3.19 hub hotkey system (MenuHotkey, one EntityTickingSystem on players - no second system) reads ms.walking in the
     SAME tick it already reads ms.crouching. Per-player state long[5] (0.3.19: long[3]) - [3] = walking last tick, [4] = the last Walk open
     (ms). walkStep() = the RISING edge (false -> true) only: holding Alt never repeats; MenuCfg.WALK_COOLDOWN_MS (default 400 ms, Server
     Setup) between two Walk opens; Server Setup row off (MenuCfg.WALK_KEY) = nothing. The open is queued on the player's world thread
     (HotkeyOpen(pr, true), never inside the tick) and checks there: the player's switch (menu.walkmenu, ON by default, per PLAYER like every
     Menu switch - PROFILES-CONTRACT rule 6), no custom page open (= ignored silently: no re-open, no flicker, never a close - HANDOFF 2),
     no open window, not dead (DeathComponent), SkyyProfiles not busy. Alt while the Menu is open: ignored (closing it is not proven safe).
     No ordering against InteractionSystems$TickInteractionManagerSystem: RPG Leveling orders before it only to strip the hotbar swap of
     its Walk + number combo; the bare Walk edge needs no ordering.
  Disconnect: MenuQuit drops the player's state at once (MenuHotkey.forget); prune() (30 s) still drops dead refs (world changes).
  Texts: the item grant line, the Mods list command line and the ready line name "your Walk key (Alt)" (players can remap Walk).
  BUILD FIX: the Stats page shows True Damage with "%" (the SET SkyyGear 0.3.35 made it a % line; the build cross-check stopped).
  CLASH: RPG Leveling (not in our worlds - disabled) opens ITS menu on Walk + a hotbar number; with both installed, Walk + number would
     open both. Our SkyySkills only READS ms.walking (Acrobatics XP rate) - no clash.
  New: player switch menu.walkmenu (General, ON), Server Setup rows menu.walkKey (bool, ON) + menu.walkKeyCooldownMs (int 200-5000 ms, adv);
  config.properties keys walkKey / walkKeyCooldownMs (missing = defaults; no migration). No new command, permission, page or bridge key.
  ROLLBACK to 0.3.41: safe (the Walk key does nothing again; the two config lines and the switch stay unread).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

P = G.Patch(os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.41.py"), os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.42.py"))
assert P.has('VERSION = "0.3.41"\n') and P.has("tools/menu_0_3_41_patch.py") and not P.has("walkStep"), "not the generated SkyyMenu 0.3.41 script"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")

P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.42: the WALK KEY (Left Alt) opens the SkyWynn Menu (notes: tools/menu_0_3_42_patch.py): MenuHotkey reads ms.walking next to crouching,
       the rising edge opens (cooldown 400 ms), player switch menu.walkmenu + Server Setup rows menu.walkKey / menu.walkKeyCooldownMs;
       MenuQuit drops the hotkey state at disconnect.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.42.py.
''')
P.rep('VERSION = "0.3.41"\n', 'VERSION = "0.3.42"\n')

# ---- build fix: the SET SkyyGear 0.3.35 made True Damage a % line (Balance P5 2.2.4, tools/gear_0_3_35_patch.py) - the Stats page's
# build cross-check against the SET SkyyGear script stops 0.3.41's text; the page now shows True Damage with its %
P.rep('''("tdmg", "True Damage", "True", ""),''', '''("tdmg", "True Damage", "True", "%"),''')

# ---- the Mods list line (8 command lines max - same count)
P.rep('''                  "Double-tap crouch while standing - open the menu (switch: /settings)",''',
      '''                  "Your Walk key (Alt) or double-tap crouch - open the menu (/settings)",   # 0.3.42''')

# ---- the player switch (General, right after the crouch hotkey)
P.rep('''    ("menu.hotkey",          "general",     "Hub hotkey: double-tap crouch", "Tap crouch twice quickly while standing on the ground to open the SkyWynn Menu", "SkyyMenu"),
''', '''    ("menu.hotkey",          "general",     "Hub hotkey: double-tap crouch", "Tap crouch twice quickly while standing on the ground to open the SkyWynn Menu", "SkyyMenu"),
    # 0.3.42: Skyy 2026-10-22 "just pressing Lalt is fine" - the Walk key (Alt by default) opens the SkyWynn Menu - ON by default
    ("menu.walkmenu",        "general",     "Open the Menu with the Walk key (Alt)", "Press your Walk key (Alt) to open the SkyWynn Menu - turn OFF if you walk with it", "SkyyMenu"),
''')
P.rep('''HOTKEY_KEY = "menu.hotkey"      # 0.3.19: the hub hotkey's player switch (MenuHotkey / HotkeyOpen)
''', '''HOTKEY_KEY = "menu.hotkey"      # 0.3.19: the hub hotkey's player switch (MenuHotkey / HotkeyOpen)
WALK_SW_KEY = "menu.walkmenu"   # 0.3.42: the Walk key (Alt) player switch (MenuHotkey.walkStep / HotkeyOpen)
WALK_COOLDOWN_MS = 400          # 0.3.42: at most one Walk-key open per this many ms per player (default; Server Setup)
''')

# ---- Server Setup rows + the config.properties template
P.rep('''    ("menu.tooltipsDefault", "Hover tooltips default", "settings", "bool", "true", "", "", "", "", "live",''',
      '''    # 0.3.42: the Walk key (Alt) opens the menu (MenuHotkey.walkStep reads the fields live)
    ("menu.walkKey", "Open the Menu with the Walk key (Alt)", "menu", "bool", "true", "", "", "", "", "live",
     "Players open the SkyWynn Menu with their Walk key (Alt by default). Each can turn it off: /settings",
     "field:MenuCfg.WALK_KEY@config.properties:walkKey"),
    ("menu.walkKeyCooldownMs", "Walk key (Alt): cooldown", "menu", "int", str(WALK_COOLDOWN_MS), "200", "5000", "step=50", "ms", "live,adv",
     "Least time between two menu opens by the Walk key (Alt), per player.",
     "field:MenuCfg.WALK_COOLDOWN_MS@config.properties:walkKeyCooldownMs"),
    ("menu.tooltipsDefault", "Hover tooltips default", "settings", "bool", "true", "", "", "", "", "live",''')
P.rep('''    "hotkeyCooldownMs=%d" % HOTKEY_COOLDOWN_MS,
]) + "\\n"''', '''    "hotkeyCooldownMs=%d" % HOTKEY_COOLDOWN_MS,
    "",
    "# walkKey = players open the SkyWynn Menu with their Walk key (Alt by default; true or false). walkKeyCooldownMs = least milliseconds",
    "# between two Walk-key opens per player (200-5000). Players switch it for themselves in /settings (Open the Menu with the Walk key).",
    "walkKey=true",
    "walkKeyCooldownMs=%d" % WALK_COOLDOWN_MS,
]) + "\\n"''')

# ---- engine members the Walk edge uses
P.rep('''             (T["MVS"], "crouching"), (T["MVS"], "onGround"),''', '''             (T["MVS"], "crouching"), (T["MVS"], "walking"), (T["MVS"], "onGround"),''')
P.rep('''             ("com.hypixel.hytale.server.core.entity.entities.player.windows.WindowManager", "getWindows")):''',
      '''             ("com.hypixel.hytale.server.core.entity.entities.player.windows.WindowManager", "getWindows"),
             ("com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent", "getComponentType"), (T["PR"], "getReference")):   # 0.3.42''')

# ---- MenuData: the switch key
P.rep('''F(dat, "public static final String HOTKEY_KEY = %s;" % jstr(HOTKEY_KEY))          # 0.3.19
''', '''F(dat, "public static final String HOTKEY_KEY = %s;" % jstr(HOTKEY_KEY))          # 0.3.19
F(dat, "public static final String WALK_SW_KEY = %s;" % jstr(WALK_SW_KEY))        # 0.3.42
assert WALK_SW_KEY in [k[0] for k in OWN_SETTINGS], "0.3.42: the Walk key switch is one of SkyyMenu's own settings (ON by default)"
''')

# ---- MenuCfg: two live fields
P.rep('''F(mcfg, "public static volatile long HOTKEY_COOLDOWN_MS = %dL;" % HOTKEY_COOLDOWN_MS)  # FIX ROUND: Server Setup (menu.hotkeyCooldownMs)
''', '''F(mcfg, "public static volatile long HOTKEY_COOLDOWN_MS = %dL;" % HOTKEY_COOLDOWN_MS)  # FIX ROUND: Server Setup (menu.hotkeyCooldownMs)
F(mcfg, "public static volatile boolean WALK_KEY = true;")                              # 0.3.42: Server Setup (menu.walkKey)
F(mcfg, "public static volatile long WALK_COOLDOWN_MS = %dL;" % WALK_COOLDOWN_MS)       # 0.3.42: Server Setup (menu.walkKeyCooldownMs)
''')
P.rep('''HOTKEY_GAP_MS = 400L; HOTKEY_COOLDOWN_MS = 1500L; return; }''',
      '''HOTKEY_GAP_MS = 400L; HOTKEY_COOLDOWN_MS = 1500L; WALK_KEY = true; WALK_COOLDOWN_MS = 400L; return; }''')
P.rep('''    HOTKEY_COOLDOWN_MS = num(p, "hotkeyCooldownMs", 1500L, 500L, 10000L);
''', '''    HOTKEY_COOLDOWN_MS = num(p, "hotkeyCooldownMs", 1500L, 500L, 10000L);
    WALK_KEY = flag(p, "walkKey", true);                                   // 0.3.42
    WALK_COOLDOWN_MS = num(p, "walkKeyCooldownMs", 400L, 200L, 5000L);    // 0.3.42
''')

# ---- MenuHotkey: the Walk edge in the same tick
P.rep('''# refusal is one INFO line. ON = false at shutdown.
''', '''# refusal is one INFO line. ON = false at shutdown.
# 0.3.42: the same tick reads ms.walking (the client's Walk key, Alt by default): the state is long[5] ([3] walking last tick, [4] the last
# Walk open ms) and exists once the player crouched OR walked; walkStep() fires on the RISING edge only (holding never repeats), not within
# MenuCfg.WALK_COOLDOWN_MS of the last Walk open, never with Server Setup's menu.walkKey off; HotkeyOpen(pr, true) then checks the
# player's menu.walkmenu switch, ignores the press SILENTLY over an open page (the Menu itself included - no flicker, no close), refuses
# over a window, while dead or profile-busy. forget() (MenuQuit) drops a leaving player's state at once.
''')
P.rep('''public static boolean step(long[] s, boolean crouch, boolean ok, long now) {''', '''public static boolean walkStep(long[] s, boolean walk, long now) {
  boolean was = s[3] != 0L;
  s[3] = walk ? 1L : 0L;
  if (!walk || was) return false;
  if (!@PKG@.MenuCfg.WALK_KEY) return false;
  long cd = @PKG@.MenuCfg.WALK_COOLDOWN_MS;
  if (s[4] != 0L && now >= s[4] && now - s[4] < cd) return false;
  s[4] = now;
  return true;
}""")
M(mhk, r"""
public static void forget(@PR@ pr) {
  if (pr == null) return;
  @REF@ r = pr.getReference();
  if (r != null) ST.remove(r);
}""")
M(mhk, r"""
public static boolean step(long[] s, boolean crouch, boolean ok, long now) {''')
P.rep('''    long[] s = (long[]) ST.get(ref);
    if (s == null) {
      if (!ms.crouching) return;
      s = new long[3];
      ST.put(ref, s);
    }
    if (!step(s, ms.crouching, still(ms), System.currentTimeMillis())) return;
    @PR@ pr = (@PR@) store.getComponent(ref, @PR@.getComponentType());''', '''    long[] s = (long[]) ST.get(ref);
    if (s == null) {
      if (!ms.crouching && !ms.walking) return;
      s = new long[5];
      ST.put(ref, s);
    }
    long now = System.currentTimeMillis();
    boolean crouchFire = step(s, ms.crouching, still(ms), now);
    boolean walkFire = walkStep(s, ms.walking, now);
    if (!crouchFire && !walkFire) return;
    @PR@ pr = (@PR@) store.getComponent(ref, @PR@.getComponentType());''')
P.rep('''    FIRED = FIRED + 1L;
    w.execute(new @PKG@.HotkeyOpen(pr));''', '''    FIRED = FIRED + 1L;
    w.execute(new @PKG@.HotkeyOpen(pr, walkFire && !crouchFire));''')

# ---- HotkeyOpen: the Walk variant
P.rep('''F(hko, "public static volatile long REFUSED = 0L;")
C(hko, "public HotkeyOpen(@PR@ pr) { this.pr = pr; }")''', '''F(hko, "public static volatile long REFUSED = 0L;")
F(hko, "public boolean walk;")                              # 0.3.42: opened by the Walk key (Alt)
F(hko, "public static volatile long WALK_OPENED = 0L;")     # 0.3.42
F(hko, "public static volatile long WALK_SKIPPED = 0L;")    # 0.3.42: a page was open - ignored silently
C(hko, "public HotkeyOpen(@PR@ pr) { this.pr = pr; this.walk = false; }")
C(hko, "public HotkeyOpen(@PR@ pr, boolean walk) { this.pr = pr; this.walk = walk; }")''')
P.rep('''M(hko, r"""
public static void refuse(@PR@ pr, String why) {''', '''M(hko, r"""
public static boolean wantedWalk(java.util.UUID u) {
  if (u == null || !@PKG@.MenuCfg.WALK_KEY) return false;
  Boolean on = @PKG@.SetStore.get(u, @PKG@.MenuData.WALK_SW_KEY);
  return on == null || on.booleanValue();
}""")
M(hko, r"""
public static boolean isDead(@ST@ st, @REF@ r) {
  try { return st.getComponent(r, com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent.getComponentType()) != null; }
  catch (Throwable t) { return false; }
}""")
M(hko, r"""
public static void refuse(@PR@ pr, String why) {''')
P.rep('''    if (!wanted(this.pr.getUuid())) return;
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
    if (cp != null) { refuse(this.pr, "page " + cp.getClass().getSimpleName() + " is open"); return; }''', '''    if (this.walk) { if (!wantedWalk(this.pr.getUuid())) return; }
    else if (!wanted(this.pr.getUuid())) return;
    @REF@ r = this.pr.getReference();
    if (r == null || !r.isValid()) return;
    @ST@ st = r.getStore();
    if (st == null) return;
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (p == null) return;
    @PGM@ pm = p.getPageManager();
    if (pm == null) return;
    Object cp = pm.getCustomPage();
    if (this.walk && cp != null) { WALK_SKIPPED = WALK_SKIPPED + 1L; return; }
    if (this.walk && isDead(st, r)) { refuse(this.pr, "dead"); return; }
    if (@PKG@.MenuUtil.profileBusy(this.pr.getUuid())) { refuse(this.pr, "a profile switch is running"); return; }
    if (cp != null) { refuse(this.pr, "page " + cp.getClass().getSimpleName() + " is open"); return; }''')
P.rep('''    pm.openCustomPage(r, st, new @PKG@.MenuPage(this.pr, "main"));
    OPENED = OPENED + 1L;''', '''    pm.openCustomPage(r, st, new @PKG@.MenuPage(this.pr, "main"));
    OPENED = OPENED + 1L;
    if (this.walk) WALK_OPENED = WALK_OPENED + 1L;''')

# ---- texts: the grant line, the register warning, the ready line
P.rep('''Right-click it (or double-tap crouch, if the Hub hotkey switch is on in /settings) to open''',
      '''Right-click it (or press your Walk key (Alt), or double-tap crouch - switches in /settings) to open''')
P.rep('''  catch (Throwable t) { @PKG@.MenuUtil.warn("could not register the hub hotkey (double-tap crouch) - the menu item and /skymenu still work: " + t); }''',
      '''  catch (Throwable t) { @PKG@.MenuUtil.warn("could not register the hub hotkey (Walk key / double-tap crouch) - the menu item and /skymenu still work: " + t); }''')
P.rep('''right-click the SkyWynn Menu item or double-tap crouch; the item''', '''right-click the SkyWynn Menu item, the Walk key (Alt) or double-tap crouch; the item''')

# ---- MenuQuit: drop the hotkey state at once
P.rep('''    @PKG@.MenuHub.forget(pr.getUuid());   // 0.3.28: hub:last:<uuid> goes with the player
  } catch (Throwable t) { }''', '''    @PKG@.MenuHub.forget(pr.getUuid());   // 0.3.28: hub:last:<uuid> goes with the player
    @PKG@.MenuHotkey.forget(pr);          // 0.3.42: the hotkey state (crouch + Walk edges) goes with the player
  } catch (Throwable t) { }''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.3.42 adds no system / command"
P.finish()
