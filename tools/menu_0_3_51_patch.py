"""Derive SkyyMenu/build_skyymenu_0.3.51.py + SkyyMenu/test_skyymenu_0.3.51.py from the SET pin SkyyMenu 0.3.50 (generated - never re-run
its patch). Run:  python tools/menu_0_3_51_patch.py   then   python SkyyMenu/build_skyymenu_0.3.51.py   (never --deploy)
Check: python SkyyMenu/test_skyymenu_0.3.51.py
Edit THIS patch, never the generated files. Every anchor is asserted once; at the end every change is undone on a copy and compared with the
0.3.50 file (nothing else changed). Line endings kept. --out <build path> [--test-out <test path>] writes elsewhere (the harness re-run).

0.3.51 (2026-11-14) = ONE fix: the CLIENT CRASH on Craft (TEST 284). Skyy: "tab worked, i tried to click craft. and it crashed." Client log
2026-11-14_21-21-01_client.log: "Unhandled exception System.Reflection.TargetInvocationException ... System.IndexOutOfRangeException: Index
was outside the bounds of the array." right after Craft. Cause: InvState.vanilla() opened the vanilla screen FROM THE SERVER
(PageManager.setPageWithWindows(Page.Inventory, a new FieldCraftingWindow)) - the 0.7.6 client crashes on that. The same call served the
creative-mode Tab and the switch-off Tab, so those crashed the client too.
  RULE (0.3.51): the server NEVER opens the vanilla inventory screen. Only the CLIENT's own Tab does - the ClientOpenWindow(PocketCrafting)
  packet passes through to the game's own consumer untouched (decided in the packet hook, nothing else on the network thread):
  1. switch OFF (Server Setup menu.inventory.replace): every Tab passes (as 0.3.50).
  2. CREATIVE: a per-player flag (InvState.CREATIVE) kept current on the world thread - set at PlayerReadyEvent (every join / world
     change: an InvTask kind 4 re-reads the mode) and at every game-mode change (InvMode: an EntityEventSystem on ChangeGameModeEvent, the
     event's new mode at once + a kind 4 re-read after it applied, so a cancelled change heals). A Tab with the flag set passes (+ the same
     kind 4 re-check as 0.3.50). A Tab taken for a creative player whose flag was not known yet opens OUR page (the known-good answer to a
     taken press) with a chat line; the flag is set, so Tab closes it and the next Tab is the vanilla screen.
  3. CRAFT ("Crafting - Tab" button): closes our page (as the X), arms ONE pass (InvState.PASS, 30 s) and says in chat "Press Tab to open
     crafting (vanilla screen) - our own crafting comes in a later update." The player's NEXT Tab passes = the vanilla inventory +
     crafting screen; the one after is ours again.
  4. A Tab task that finds the switch off (race) opens our page too (it was taken) - never the server-opened screen.
  InvState.vanilla / VANILLA / VANILLA_FN are gone; the build no longer references setPageWithWindows or FieldCraftingWindow (the harness
  scans the built classes). A passed Tab also forgets the redirect stamp (the vanilla screen's own CloseWindow 0 is the game's).
  Texts: the button "Crafting - Tab" (proven inline characters), its note, the CRAFTING panel line, the read-only armour line.
  One new class (InvMode) + one registerSystem (ONE per class). No saved data, no command, no lang key, no setting.
  ROLLBACK to 0.3.50: NOT advised (the Craft crash is back); to 0.3.49: safe (vanilla Tab; nothing stored).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

MOD = os.path.join(ROOT, "SkyyMenu")
P = G.Patch(os.path.join(MOD, "build_skyymenu_0.3.50.py"), os.path.join(MOD, "build_skyymenu_0.3.51.py"))
T = G.Patch(os.path.join(MOD, "test_skyymenu_0.3.50.py"), os.path.join(MOD, "test_skyymenu_0.3.51.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
    T.dst = os.path.abspath(sys.argv[sys.argv.index("--test-out") + 1]) if "--test-out" in sys.argv else None
assert P.has('VERSION = "0.3.50"\n') and P.has("tools/menu_0_3_50_patch.py") and P.has("setPageWithWindows(ref, st, @PGE@.Inventory")
assert not P.has("InvMode"), "not the generated SkyyMenu 0.3.50 script"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")

# ======================================================================= the BUILD script
P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.51: the Craft CLIENT CRASH fix (TEST 284) - the server never opens the vanilla inventory screen any more; switch off / creative /
       "Crafting - Tab" let the CLIENT's own Tab through (InvMode keeps the creative flag current) (notes: tools/menu_0_3_51_patch.py).
       CHECKED: see SkyyMenu/test_skyymenu_0.3.51.py.
''')
P.rep('VERSION = "0.3.50"\n', 'VERSION = "0.3.51"\n')

# ---------- engine classes: the server-side vanilla hand-off goes; the game-mode watch comes
P.rep('''    "WIN":  "com.hypixel.hytale.server.core.entity.entities.player.windows.Window",
    "FCW":  "com.hypixel.hytale.builtin.crafting.window.FieldCraftingWindow",
''', '''    # 0.3.51: the game-mode watch (the creative flag); the server-side vanilla screen hand-off (Window / FieldCraftingWindow) is gone
    "EES":  "com.hypixel.hytale.component.system.EntityEventSystem",
    "EVT":  "com.hypixel.hytale.component.system.EcsEvent",
    "CGME": "com.hypixel.hytale.server.core.event.events.ecs.ChangeGameModeEvent",
''')
P.rep('''             (T["PGM"], "getCustomPage"), (T["PGM"], "openCustomPage"), (T["PGM"], "setPageWithWindows"), (T["PGE"], "Inventory"),
             (T["PR"], "getPacketHandler"),''', '''             (T["PGM"], "getCustomPage"), (T["PGM"], "openCustomPage"), (T["CGME"], "getGameMode"), (T["EES"], "handle"),
             (T["PR"], "getPacketHandler"), (T["PR"], "sendMessage"),''')
P.rep('''assert ("(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/protocol/packets/interface_/Page;Z"
        "[Lcom/hypixel/hytale/server/core/entity/entities/player/windows/Window;)Z") in _isig(T["PGM"], "setPageWithWindows"), "0.3.50: PageManager.setPageWithWindows changed"
''', '''# 0.3.51: no PageManager page-with-windows call any more - the server never opens the vanilla screen (it crashed the client, TEST 284)
''')
P.rep('''assert "()V" in _ictor(T["FCW"]) and pool.get(T["FCW"]).subclassOf(pool.get(T["WIN"])), "0.3.50: FieldCraftingWindow() is a Window (the vanilla Pocket Crafting)"
''', '''assert pool.get(T["CGME"]).subclassOf(pool.get(T["EVT"])) and "(Lcom/hypixel/hytale/protocol/GameMode;)V" in _ictor(T["CGME"]), "0.3.51: ChangeGameModeEvent is an EcsEvent"
assert "(Ljava/lang/Class;)V" in _ictor(T["EES"]), "0.3.51: EntityEventSystem(Class)"
''')
P.rep('''print("0.3.50 inventory screen: every engine member probed (hooks, adapter, grids, drop, sort, vanilla Pocket Crafting hand-off)")''',
      '''print("0.3.51 inventory screen: every engine member probed (hooks, adapter, grids, drop, sort, the game-mode watch)")''')

# ---------- the texts: the button says what it does now
P.rep('''    "craftB": "Until then, Craft opens the vanilla crafting screen with your inventory - every recipe is still there.",''',
      '''    "craftB": "Until then: click Crafting - Tab, then press Tab for the vanilla crafting screen (every recipe).",''')
P.rep('''    "charRo": "Armour and off-hand are shown here, read only for now. Equip them from Craft (the vanilla screen).",''',
      '''    "charRo": "Armour and off-hand are shown here, read only for now. Equip them in the vanilla screen (Crafting - Tab).",''')
P.rep('''G_.glass_button(IV + "CraftBtn", "Craft", "primary", w=220, h=44, size=17)))''',
      '''G_.glass_button(IV + "CraftBtn", "Crafting - Tab", "primary", w=220, h=44, size=17)))   # 0.3.51''')
P.rep('''lab(IV + "CfNote", "Opens the vanilla crafting and inventory screen", 14,''',
      '''lab(IV + "CfNote", "Closes this page - then press Tab for the vanilla crafting screen", 14,''')
P.rep('''"Armour and off-hand are read only here - use Craft for the vanilla screen");''',
      '''"Armour and off-hand are read only here - Crafting - Tab, then Tab, for the vanilla screen");''')

# ---------- the class list + the InvState fields
P.rep('''irdy = mk("InvReady")
''', '''irdy = mk("InvReady")
imod = mk("InvMode", T["EES"])   # 0.3.51: ChangeGameModeEvent -> the creative flag (the vanilla Tab for creative players)
''')
P.rep('''           "public static volatile int VANILLA = 0;", "public static volatile int PASSED = 0;",''',
      '''           "public static volatile int PASSED = 0;", "public static volatile int MODES = 0;",''')
P.rep('''           "public static java.util.function.Function DROPPER = null;",      # harness only: records drops instead of ItemUtils.dropItem
           "public static java.util.function.Function VANILLA_FN = null;"):  # harness only: records the vanilla hand-off''',
      '''           "public static java.util.function.Function DROPPER = null;"):     # harness only: records drops instead of ItemUtils.dropItem''')

# ---------- InvState part 2: no server-opened vanilla screen; the creative flag; Tab
P.rep('''# ---- InvState part 2: the vanilla screen hand-off (Craft, creative, the switch going off), opening our page
M(ist, r"""
public static boolean vanilla(@REF@ ref, @ST@ st, @PR@ pr, String why) {
  if (pr == null) return false;
  java.util.UUID u = pr.getUuid();
  VANILLA = VANILLA + 1;
  REDIR.remove(u);
  boolean ok = false;
  if (VANILLA_FN != null) ok = Boolean.TRUE.equals(VANILLA_FN.apply(why));
  else {
    try {
      @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
      if (p != null) ok = p.getPageManager().setPageWithWindows(ref, st, @PGE@.Inventory, true, new @WIN@[] { new @FCW@() });
    } catch (Throwable t) { @PKG@.MenuUtil.warn("inventory: the vanilla inventory screen could not open (" + why + "): " + t); ok = false; }
  }
  if (ok) {
    @PKG@.InvPage cur = (@PKG@.InvPage) PAGES.get(u);
    if (cur != null) cur.finish(why);
  }
  return ok;
}""")
''', '''# ---- InvState part 2 (0.3.51): the server NEVER opens the vanilla screen (setPageWithWindows crashed the client, TEST 284) - only the
# client's own Tab does, passed through by route(); the creative flag (kept current on the world thread), a chat line, opening our page
M(ist, r"""
public static void tell(@PR@ pr, String s) {
  try { if (pr != null) pr.sendMessage(@MSG@.raw("[SkyWynn] " + s)); } catch (Throwable t) { }
}""")
M(ist, r"""
public static void modeChanged(@PR@ pr, @GMD@ gm) {
  if (pr == null) return;
  java.util.UUID u = pr.getUuid();
  if (gm == @GMD@.Creative) CREATIVE.put(u, Boolean.TRUE); else CREATIVE.remove(u);
  MODES = MODES + 1;
  queue(pr, new @PKG@.InvTask(4, pr, "mode"));
}""")
''')
P.rep('''# the Tab key on the world thread: our page open = it closes; switch off / creative = the vanilla screen; else window 0 closed first
# (the CORE redirect step) and our page opens
M(ist, r"""
public static void tab(@REF@ ref, @ST@ st, @PR@ pr, @PLA@ p, String via) {
  java.util.UUID u = pr.getUuid();
  @PKG@.InvPage cur = (@PKG@.InvPage) PAGES.get(u);
  if (cur != null && !cur.closed && p.getPageManager().getCustomPage() == cur) { cur.shut(); return; }
  if (cur != null) cur.finish("stale");
  if (!on()) { vanilla(ref, st, pr, "switched off"); return; }
  if (p.getGameMode() == @GMD@.Creative) {
    CREATIVE.put(u, Boolean.TRUE);
    vanilla(ref, st, pr, "creative");
    return;
  }
  CREATIVE.remove(u);
  @WM@ wm = p.getWindowManager();
  if (wm != null && wm.getWindow(0) != null) wm.closeWindow(ref, 0, (@CAC@) st);
  openPage(ref, st, pr, "Tab (" + via + ")");
}""")
''', '''# the Tab key on the world thread (a press route() TOOK): our page open = it closes; else window 0 closed first (the CORE redirect step) and
# our page opens - also for a creative player whose flag was not known yet (the flag is set now: Tab closes, the next Tab passes) and when
# the switch went off in between (0.3.51: never a server-opened vanilla screen)
M(ist, r"""
public static void tab(@REF@ ref, @ST@ st, @PR@ pr, @PLA@ p, String via) {
  java.util.UUID u = pr.getUuid();
  @PKG@.InvPage cur = (@PKG@.InvPage) PAGES.get(u);
  if (cur != null && !cur.closed && p.getPageManager().getCustomPage() == cur) { cur.shut(); return; }
  if (cur != null) cur.finish("stale");
  boolean cr = p.getGameMode() == @GMD@.Creative;
  if (cr) CREATIVE.put(u, Boolean.TRUE); else CREATIVE.remove(u);
  @WM@ wm = p.getWindowManager();
  if (wm != null && wm.getWindow(0) != null) wm.closeWindow(ref, 0, (@CAC@) st);
  @PKG@.InvPage pg = openPage(ref, st, pr, "Tab (" + via + ")");
  if (pg != null && cr) tell(pr, "Creative mode: Tab closes this page, then Tab opens the vanilla inventory.");
}""")
''')

# ---------- Craft: close our page + ONE pass for the client's next Tab
P.rep('''public void craft(@REF@ ref, @ST@ st) {
  this.answered = true;
  java.util.UUID u = this.playerRef.getUuid();
  if (@PKG@.InvState.vanilla(ref, st, this.playerRef, "craft")) return;
  @PKG@.InvState.PASS.put(u, Long.valueOf(System.currentTimeMillis()));
  say("Press Tab twice for the vanilla crafting screen (it did not open from here)");
}""")''', '''public void craft(@REF@ ref, @ST@ st) {
  this.answered = true;
  java.util.UUID u = this.playerRef.getUuid();
  @PKG@.InvState.REDIR.remove(u);
  @PKG@.InvState.PASS.put(u, Long.valueOf(System.currentTimeMillis()));
  @PKG@.InvState.tell(this.playerRef, "Press Tab to open crafting (vanilla screen) - our own crafting comes in a later update.");
  shut();
}""")''')

# ---------- InvTask kind 4 = the creative flag re-read both ways (ready, a mode change, a passed creative Tab)
P.rep('''    if (this.kind == 4) { if (p.getGameMode() != @GMD@.Creative) @PKG@.InvState.CREATIVE.remove(this.pr.getUuid()); return; }''',
      '''    if (this.kind == 4) {   // 0.3.51: the creative flag, both ways
      if (p.getGameMode() == @GMD@.Creative) @PKG@.InvState.CREATIVE.put(this.pr.getUuid(), Boolean.TRUE);
      else @PKG@.InvState.CREATIVE.remove(this.pr.getUuid());
      return;
    }''')

# ---------- route: a passed Tab forgets the redirect stamp (the vanilla screen's own CloseWindow 0 is the game's)
P.rep('''      if (!@PKG@.MenuCfg.INV_REPLACE) return false;
      Object ps = PASS.remove(u);
      if (ps instanceof Long && nw - ((Long) ps).longValue() < 30000L) { PASSED = PASSED + 1; return false; }
      if (CREATIVE.containsKey(u)) { queue(pr, new @PKG@.InvTask(4, pr, via)); return false; }''',
      '''      if (!@PKG@.MenuCfg.INV_REPLACE) { REDIR.remove(u); return false; }
      Object ps = PASS.remove(u);
      if (ps instanceof Long && nw - ((Long) ps).longValue() < 30000L) { PASSED = PASSED + 1; REDIR.remove(u); return false; }
      if (CREATIVE.containsKey(u)) { REDIR.remove(u); queue(pr, new @PKG@.InvTask(4, pr, via)); return false; }''')

# ---------- InvReady: re-read the mode on the world thread at every join / world change; InvMode (after InvState, before the plugin)
P.rep('''    @PKG@.InvState.REDIR.remove(u);
    @PKG@.InvPage pg = (@PKG@.InvPage) @PKG@.InvState.PAGES.get(u);
    if (pg != null && (pg.pref != r || pg.pst != st)) pg.finish("world change");
  } catch (Throwable t) { @PKG@.MenuUtil.warn("inventory: world-change handling failed: " + t); }
}""")
''', '''    @PKG@.InvState.REDIR.remove(u);
    @PKG@.InvPage pg = (@PKG@.InvPage) @PKG@.InvState.PAGES.get(u);
    if (pg != null && (pg.pref != r || pg.pst != st)) pg.finish("world change");
    @PKG@.InvState.queue(pr, new @PKG@.InvTask(4, pr, "ready"));   // 0.3.51: the creative flag
  } catch (Throwable t) { @PKG@.MenuUtil.warn("inventory: world-change handling failed: " + t); }
}""")
# 0.3.51: InvMode - an EntityEventSystem on ChangeGameModeEvent (players only; the world thread): the new mode sets the creative flag at once,
# and a kind 4 task re-reads the mode after the change applied (a cancelled change heals). ONE registerSystem (the plugin's setup).
C(imod, "public InvMode() { super(@CGME@.class); }")
F(imod, "public static volatile boolean FAILED = false;")
M(imod, r"""
public @QRY@ getQuery() {
  return (@QRY@) @PLA@.getComponentType();
}""")
M(imod, r"""
public void handle(int idx, @ACH@ chunk, @ST@ store, @CB@ cb, @EVT@ ev) {
  try {
    @REF@ ref = chunk.getReferenceTo(idx);
    if (ref == null) return;
    @PR@ pr = (@PR@) store.getComponent(ref, @PR@.getComponentType());
    if (pr == null) return;
    @PKG@.InvState.modeChanged(pr, ((@CGME@) ev).getGameMode());
  } catch (Throwable t) {
    if (!FAILED) { FAILED = true; @PKG@.MenuUtil.warn("inventory: the game-mode watch failed (logged once; a creative player's Tab may open our page once): " + t); }
  }
}""")
''')
P.rep('''    @PKG@.InvState.install();
''', '''    @PKG@.InvState.install();
    try { getEntityStoreRegistry().registerSystem(new @PKG@.InvMode()); }   // 0.3.51: game-mode changes keep the creative flag current
    catch (Throwable t) { @PKG@.MenuUtil.warn("inventory screen: the game-mode watch could not register - a creative player's first Tab after a mode change opens our page: " + t); }
''')
P.rep('''         idat, ist, ipg, itk, irf, icl, ich, ihk, ihf, iwr, ifl, ibye, irdy, pl)   # 0.3.50: the inventory screen''',
      '''         idat, ist, ipg, itk, irf, icl, ich, ihk, ihf, iwr, ifl, ibye, irdy, imod, pl)   # 0.3.50: the inventory screen (0.3.51: + InvMode)''')

assert P.s.count("registerSystem(") == SYS0 + 1 and P.s.count("registerCommand(") == CMD0, "0.3.51 adds ONE system (InvMode), no command"
for _w in ("setPageWithWindows(ref", "@FCW@", "@WIN@", "VANILLA_FN", "InvState.vanilla("):
    assert _w not in P.s, "0.3.51: still in the build: " + _w
_i = P.s.index
assert _i("public static void modeChanged(") < _i("C(imod, ") < _i("# ================= plugin =================") < _i("new @PKG@.InvMode()")
P.finish()

# ======================================================================= the HARNESS (derived from the 0.3.50 harness: every 0.3.50 check
# kept except the server-opened vanilla screen ones, which become the 0.3.51 checks)
assert T.has('VERSION = "0.3.50"\nJAR') and T.has("ST.VANILLA_FN = Van(True)")


def cut(t, start, end, keep_end=True):
    """the exact text from start up to end (end itself kept outside the cut when keep_end) - each marker must occur once"""
    assert t.count(start) == 1 and t.count(end) == 1, (start, end)
    a = t.index(start)
    return t[a:t.index(end) + (0 if keep_end else len(end))]


T.rep('''"""Harness for SkyyMenu 0.3.50 (the inventory screen P1 shell + the Skyglass kit theme; tools/menu_0_3_50_patch.py). Build first:
    python tools/menu_0_3_50_patch.py && python SkyyMenu/build_skyymenu_0.3.50.py
    python SkyyMenu/test_skyymenu_0.3.50.py [--dir <folder inside tools/dev/scratch/>] [--keep]
''', '''"""Harness for SkyyMenu 0.3.51 (the Craft client-crash fix: the server never opens the vanilla screen; tools/menu_0_3_51_patch.py).
GENERATED by tools/menu_0_3_51_patch.py from the 0.3.50 harness (edit the patch, not this file): every 0.3.50 check runs again on the
0.3.51 jar except the server-opened vanilla screen ones (OFF race, CREATIVE, CRAFT), which are replaced by the 0.3.51 checks. Build first:
    python tools/menu_0_3_51_patch.py && python SkyyMenu/build_skyymenu_0.3.51.py
    python SkyyMenu/test_skyymenu_0.3.51.py [--dir <folder inside tools/dev/scratch/>] [--keep]
''')
T.rep('''  S    static   the patch re-runs to identical bytes; no new system / command; line endings kept; tools/skyyui.py = the committed file +
                an APPENDED block only (additive: every old builder byte-identical); non-class jar entries = manifest + the 34 Skyglass
                textures (= the kit's generated bytes, under Common/UI/Custom/SkyyGlass/ only); the page data (12 tabs, ids, element count)
''', '''  S    static   the patch re-runs to identical bytes (build + this harness); ONE new system (InvMode), no command; line endings kept;
                tools/skyyui.py unchanged; non-class jar entries = manifest only (the 34 Skyglass textures = the kit's bytes, as 0.3.50);
                NO built class references setPageWithWindows / FieldCraftingWindow (0.3.50's did); the page data (12 tabs)
''')
T.rep('''  C    compare  0.3.49 -> 0.3.50: exactly the listed members differ, the 13 Inv* classes added
''', '''  C    compare  0.3.50 -> 0.3.51: exactly the listed members differ, InvMode added; everything else byte-identical
''')
T.rep('''       CREATIVE the first Tab hands over to the vanilla screen, later presses pass through, back in adventure = ours again
       CRAFT   the vanilla hand-off (Page.Inventory + FieldCraftingWindow) - accepted: the page is done; refused: PASS = Tab twice
               gives the vanilla screen; the REAL setPageWithWindows call on the stand-in (opened or a logged refusal, never a throw)
''', '''       OFF race (0.3.51) a taken Tab whose task finds the switch off opens OUR page (never a server-opened screen)
       CREATIVE (0.3.51) PlayerReady -> the flag on the world thread; the FIRST Tab passes; a mode change (InvMode / modeChanged) at
               once + the re-read (a cancelled change heals); an unknown creative player: our page + chat, Tab closes, next Tab passes
       CRAFT   (0.3.51) the page closes, ONE pass armed + the chat line, no window / page packet; the next Tab passes once, the one
               after is ours; a pass over 30 s is dropped; InvState.vanilla / VANILLA_FN gone
       PASS    (0.3.51) on the REAL wrapper: switch off / creative / the Craft pass = the game's consumer gets the SAME packet object
''')
T.rep('''VERSION = "0.3.50"
JAR''', '''VERSION = "0.3.51"
JAR''')
T.rep('''OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.49.jar")
GEN = os.path.join(HERE, "build_skyymenu_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.49.py")
PATCH = os.path.join(ROOT, "tools", "menu_0_3_50_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "inv1", "menu")))''',
      '''OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.50.jar")
GEN = os.path.join(HERE, "build_skyymenu_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.50.py")
PATCH = os.path.join(ROOT, "tools", "menu_0_3_51_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "inv2", "menu")))''')
T.rep(cut(T.s, 'ADDED = ["InvData",', "if \"--expect-dump\" in sys.argv:"), '''ADDED = ["InvMode"]
EXPECT = {
    "InvState": ["+f MODES", "+m modeChanged", "+m tell", "-f VANILLA", "-f VANILLA_FN", "-m vanilla", "~<clinit>", "~m route", "~m tab"],   # clinit: the static fields
    "InvPage": ["~m craft", "~m move"],                  # craft: close + one pass; move: the read-only armour line
    "InvTask": ["~m run"], "InvReady": ["~m accept"],    # kind 4 both ways; the mode read at every ready
    "SkyyMenuPlugin": ["~m setup"],                      # registerSystem(new InvMode())
    "InvData": ["~<clinit>"],                            # the page texts (button, note, panel lines)
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "OpsPage": ["~<clinit>"], "MenuData": ["~<clinit>"],   # the version string
}
''')
T.rep(cut(T.s, "_RC = HK.run_compare\n", "HK.run_compare = _compare\n", keep_end=False),
      "# 0.3.51: 0.3.50 -> 0.3.51 changes manifest.json only among the non-class entries = the plain HK.run_compare\n")
T.rep('''    K.check(g.count('VERSION = "0.3.50"') == 1, "S VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)''', '''    K.check(g.count('VERSION = "0.3.51"') == 1, "S VERSION")
    K.check(g.count("registerSystem(") == o.count("registerSystem(") + 1 and g.count("registerSystem(new @PKG@.InvMode())") == 1,
            "S ONE new registerSystem: InvMode (one per class)")
    K.check(g.count("registerCommand(") == o.count("registerCommand("), "S no new registerCommand(")''')
T.rep('''    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])''',
      '''    ct = os.path.join(d, "test.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp, "--test-out", ct], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read() and open(ct, "rb").read() == open(os.path.abspath(__file__), "rb").read(),
            "S the patch re-runs to identical bytes (the build script AND this harness): %s" % p.stderr[-300:])''')
T.rep(cut(T.s, "    # the kit: additive only (the committed tools/skyyui.py", "    K.check(SUI.THEMES =="),
      '''    # the kit: unchanged (0.3.51 uses kit 1.10 as committed)
    head = subprocess.run(["git", "-C", ROOT, "show", "HEAD:tools/skyyui.py"], capture_output=True).stdout
    cur = open(os.path.join(ROOT, "tools", "skyyui.py"), "rb").read()
    K.check(len(head) > 400000 and cur.replace(b"\\r\\n", b"\\n") == head.replace(b"\\r\\n", b"\\n") and b"KIT 1.10 (2026-11-14): THE SKYGLASS THEME" in cur,
            "S tools/skyyui.py = the committed kit 1.10, unchanged")
''')
T.rep('''    K.eq(diff, sorted(["manifest.json"] + list(glass)), "S non-class jar entries changed = manifest + the Skyglass textures")''',
      '''    K.eq(diff, ["manifest.json"], "S non-class jar entries changed = manifest only (the Skyglass textures as 0.3.50)")''')
T.rep('''    K.check(not [n for n in zn.namelist() if n.lower().endswith(".ui")], "S inline pages only (no .ui file)")
''', '''    K.check(not [n for n in zn.namelist() if n.lower().endswith(".ui")], "S inline pages only (no .ui file)")
    # 0.3.51 (TEST 284 client crash): no built class may open the vanilla screen from the server
    _bad = lambda z_: sorted(n for n in z_.namelist() if n.endswith(".class") and (b"setPageWithWindows" in z_.read(n) or b"FieldCraftingWindow" in z_.read(n)))
    K.eq(_bad(zn), [], "S NO built class references setPageWithWindows / FieldCraftingWindow (the server never opens the vanilla screen)")
    K.eq(_bad(zo), ["com/skyy/menu/InvState.class"], "S ... (the scan works: 0.3.50's InvState had both)")
''')

# run_inv: the OFF race, CREATIVE and CRAFT blocks -> the 0.3.51 checks
T.rep(cut(T.s, "    # a Tab task that runs after the switch went off (race): the vanilla screen\n", "    # ---- TABS: the other 11 open the hub pages\n"),
      r'''    # a Tab task that runs after the switch went off (race): the press was TAKEN, so our page opens (0.3.51: never a server-opened screen)
    JV("InvTask")(1, PI.pr, "race").run()
    cur = PI.pm.getCustomPage()
    K.check(cur is not None and str(cur.getClass().getSimpleName()) == "InvPage", "OFF race (0.3.51): a queued Tab after the switch went off opens OUR page, never a server-opened vanilla screen")
    PI.pm.handleLegacyCustomPageEvent(PI.ref, PI.st, E.CPE(E.CPT.Dismiss, None))
    CFG.INV_REPLACE = True
    E.run_world(E.W1)
    SYSc, LONGc = JClass("java.lang.System"), JClass("java.lang.Long")
    PREc = JClass(PH + "server.core.event.events.player.PlayerReadyEvent")

    # ---- CREATIVE (0.3.51): the flag is kept current on the world thread; a Tab with the flag set PASSES (the client's own vanilla screen)
    PC = E.player(uid=UUIDc(0x51, 0x51), name="SkyyInvC")
    E.jf(PLAc.class_, "gameMode").set(PC.pl, GMDc.Creative)
    JV("InvReady")().accept(PREc(PC.ref, PC.pl, 0))
    K.check(E.queued(E.W1) == ["InvTask"] and not ST.CREATIVE.containsKey(PC.pr.getUuid()), "CREATIVE: PlayerReady queues the mode read on the world thread")
    E.run_world(E.W1)
    K.check(ST.CREATIVE.containsKey(PC.pr.getUuid()), "CREATIVE: ... the world thread sets the flag")
    s0 = int(ST.SUB)
    K.check(not bool(ST.route(PC.pr, COWc(WTc.PocketCrafting), "subhandler")) and int(ST.SUB) == s0 and E.queued(E.W1) == ["InvTask"],
            "CREATIVE: the FIRST Tab passes to the game (the client's own vanilla screen) + a mode re-check, nothing taken")
    E.run_world(E.W1)
    K.check(ST.CREATIVE.containsKey(PC.pr.getUuid()) and PC.pm.getCustomPage() is None, "CREATIVE: still creative = still remembered, no page of ours")
    E.jf(PLAc.class_, "gameMode").set(PC.pl, GMDc.Adventure)
    m0 = int(ST.MODES)
    ST.modeChanged(PC.pr, GMDc.Adventure)
    K.check(not ST.CREATIVE.containsKey(PC.pr.getUuid()) and int(ST.MODES) == m0 + 1 and E.queued(E.W1) == ["InvTask"], "MODE: to adventure = forgotten at once, a re-read queued")
    E.run_world(E.W1)
    K.check(not ST.CREATIVE.containsKey(PC.pr.getUuid()), "MODE: ... the re-read agrees")
    K.check(bool(ST.route(PC.pr, COWc(WTc.PocketCrafting), "subhandler")), "MODE: adventure -> the next Tab is ours")
    E.run_world(E.W1)
    K.check(PC.pm.getCustomPage() is not None and str(PC.pm.getCustomPage().getClass().getSimpleName()) == "InvPage", "MODE: adventure -> our page")
    PC.pm.handleLegacyCustomPageEvent(PC.ref, PC.st, E.CPE(E.CPT.Dismiss, None))
    ST.modeChanged(PC.pr, GMDc.Creative)                          # a CANCELLED change: the mode stays adventure
    K.check(ST.CREATIVE.containsKey(PC.pr.getUuid()), "MODE: to creative = remembered at once")
    E.run_world(E.W1)
    K.check(not ST.CREATIVE.containsKey(PC.pr.getUuid()), "MODE: a cancelled change heals at the re-read (still adventure = forgotten)")
    E.jf(PLAc.class_, "gameMode").set(PC.pl, GMDc.Creative)
    ST.modeChanged(PC.pr, GMDc.Creative)
    E.run_world(E.W1)
    K.check(ST.CREATIVE.containsKey(PC.pr.getUuid()) and not bool(ST.route(PC.pr, COWc(WTc.PocketCrafting), "subhandler")), "MODE: to creative -> the next Tab passes")
    E.run_world(E.W1)
    IM = JV("InvMode")()
    K.check(str(IM.getEventType().getName()) == PH + "server.core.event.events.ecs.ChangeGameModeEvent"
            and JClass(PH + "component.system.EntityEventSystem").class_.isInstance(IM), "MODE: InvMode = an EntityEventSystem on ChangeGameModeEvent")
    IM.handle(0, None, None, None, None)
    K.check(bool(JV("InvMode").FAILED) and PC.pm.getCustomPage() is None and E.queued(E.W1) == [], "MODE: a broken event is logged once, never thrown")
    JV("InvMode").FAILED = False
    # a creative player whose flag was NOT known (no ready / mode event seen): the taken Tab opens OUR page + a chat line; Tab closes; next passes
    PD = E.player(uid=UUIDc(0x52, 0x52), name="SkyyInvD")
    E.jf(PLAc.class_, "gameMode").set(PD.pl, GMDc.Creative)
    K.check(bool(ST.route(PD.pr, COWc(WTc.PocketCrafting), "subhandler")), "CREATIVE unknown: the Tab is taken (flag not known yet)")
    f0 = len(E.sent(PD))
    E.run_world(E.W1)
    cur = PD.pm.getCustomPage()
    K.check(cur is not None and str(cur.getClass().getSimpleName()) == "InvPage" and ST.CREATIVE.containsKey(PD.pr.getUuid())
            and "Creative mode: Tab closes this page, then Tab opens the vanilla inventory." in E.strs_of(PD, f0),
            "CREATIVE unknown: OUR page opens (the known-good answer to a taken press), the flag is set, a chat line")
    E.pump(PD)
    ST.route(PD.pr, COWc(WTc.PocketCrafting), "subhandler")
    E.run_world(E.W1)
    K.check(PD.pm.getCustomPage() is None, "CREATIVE unknown: Tab closes our page")
    K.check(not bool(ST.route(PD.pr, COWc(WTc.PocketCrafting), "subhandler")) and not ST.REDIR.containsKey(PD.pr.getUuid()),
            "CREATIVE unknown: ... the next Tab passes (the vanilla screen), the redirect stamp forgotten")
    E.run_world(E.W1)

    # ---- CRAFT (0.3.51; TEST 284 "i tried to click craft. and it crashed."): close our page + ONE pass for the client's next Tab
    pg = ST.openPage(PI.ref, PI.st, PI.pr, "test")
    E.pump(PI)
    ST.REDIR.put(PI.pr.getUuid(), LONGc(SYSc.currentTimeMillis()))
    f0 = len(E.sent(PI))
    pg.handleDataEvent(PI.ref, PI.st, '{"a":"craft"}')
    ks = E.kinds(PI, f0)
    K.notes.append("CRAFT sent: %s" % ks)
    K.check(bool(pg.closed) and PI.pm.getCustomPage() is None and ST.PAGES.get(PI.pr.getUuid()) is None, "CRAFT: our page closes (as the X)")
    K.check(ST.PASS.containsKey(PI.pr.getUuid()) and not ST.REDIR.containsKey(PI.pr.getUuid()), "CRAFT: ONE pass armed, the redirect stamp forgotten")
    K.check("Press Tab to open crafting (vanilla screen) - our own crafting comes in a later update." in E.strs_of(PI, f0), "CRAFT: the chat line")
    K.check(not [k_ for k_ in ks if "Window" in k_] and len(pages(PI, f0)) == 0, "CRAFT: no window packet, no page packet of ours (%s)" % ks)
    E.pump(PI)
    p0 = int(ST.PASSED)
    K.check(not bool(ST.route(PI.pr, COWc(WTc.PocketCrafting), "subhandler")) and int(ST.PASSED) == p0 + 1 and not ST.PASS.containsKey(PI.pr.getUuid())
            and E.queued(E.W1) == [], "CRAFT: the NEXT Tab passes to the game (the vanilla inventory + crafting screen), once, nothing queued")
    K.check(bool(ST.route(PI.pr, COWc(WTc.PocketCrafting), "subhandler")), "CRAFT: the Tab after that is ours again")
    E.run_world(E.W1)
    cur = PI.pm.getCustomPage()
    K.check(cur is not None and str(cur.getClass().getSimpleName()) == "InvPage", "CRAFT: ... our page opens")
    PI.pm.handleLegacyCustomPageEvent(PI.ref, PI.st, E.CPE(E.CPT.Dismiss, None))
    ST.PASS.put(PI.pr.getUuid(), LONGc(SYSc.currentTimeMillis() - 31000))
    K.check(bool(ST.route(PI.pr, COWc(WTc.PocketCrafting), "subhandler")) and not ST.PASS.containsKey(PI.pr.getUuid()), "CRAFT: a pass older than 30 s is dropped - the Tab is ours")
    E.run_world(E.W1)
    PI.pm.handleLegacyCustomPageEvent(PI.ref, PI.st, E.CPE(E.CPT.Dismiss, None))
    K.check(not hasattr(ST, "vanilla") and not hasattr(ST, "VANILLA_FN") and not hasattr(ST, "VANILLA"), "CRAFT: InvState.vanilla / VANILLA / VANILLA_FN are gone")
    ST.REDIR.clear()

''')
T.rep('''    # the adapter (a connection the hook missed) - never both
''', '''    # ---- 0.3.51 PASS-THROUGH on the REAL wrapper: the game's consumer gets the SAME packet object, untouched
    GOT = []

    @JImplements("java.util.function.Consumer")
    class Rec(object):
        @JOverride
        def accept(self, p):
            GOT.append(p)
    IDH = JClass("java.lang.System").identityHashCode
    W51 = JV("InvWrap")(G, Rec())

    def tab_through(PP):
        E.jf(GPHc.class_, "playerRef").set(G, PP.pr)
        pk_ = COWc(WTc.PocketCrafting)
        n_ = len(GOT)
        W51.accept(pk_)
        return len(GOT) == n_ + 1 and IDH(GOT[-1]) == IDH(pk_) and GOT[-1].type == WTc.PocketCrafting
    E.run_world(E.W1)
    CFG.INV_REPLACE = False
    K.check(tab_through(PI) and E.queued(E.W1) == [] and PI.pm.getCustomPage() is None, "PASS switch OFF: the Tab packet reaches the game's consumer UNCHANGED (same object), nothing queued")
    CFG.INV_REPLACE = True
    E.jf(PLAc.class_, "gameMode").set(PC.pl, GMDc.Creative)
    ST.CREATIVE.put(PC.pr.getUuid(), TRUE)
    K.check(tab_through(PC) and E.queued(E.W1) == ["InvTask"], "PASS creative: the Tab packet reaches the game's consumer UNCHANGED (+ the mode re-check)")
    E.run_world(E.W1)
    K.check(PC.pm.getCustomPage() is None and ST.CREATIVE.containsKey(PC.pr.getUuid()), "PASS creative: no page of ours")
    ST.PASS.put(PI.pr.getUuid(), JClass("java.lang.Long")(JClass("java.lang.System").currentTimeMillis()))
    K.check(tab_through(PI) and E.queued(E.W1) == [], "PASS Craft: the armed Tab reaches the game's consumer UNCHANGED")
    K.check(not tab_through(PI) and E.queued(E.W1) == ["InvTask"], "PASS Craft: ... once - the Tab after it is ours")
    E.run_world(E.W1)
    PI.pm.handleLegacyCustomPageEvent(PI.ref, PI.st, E.CPE(E.CPT.Dismiss, None))
    ST.REDIR.clear()
    E.jf(GPHc.class_, "playerRef").set(G, None)
    # the adapter (a connection the hook missed) - never both
''')
T.rep('''ORPH %d NATIVE %d VANILLA %d PASSED %d" % (int(ST.OPENS), int(ST.SUB), int(ST.ADP), int(ST.ORPH), int(ST.NATIVE), int(ST.VANILLA), int(ST.PASSED)))''',
      '''ORPH %d NATIVE %d MODES %d PASSED %d" % (int(ST.OPENS), int(ST.SUB), int(ST.ADP), int(ST.ORPH), int(ST.NATIVE), int(ST.MODES), int(ST.PASSED)))''')
for _w in ("ST.VANILLA_FN =", "Van(", "ST.vanilla(", "0.3.49.jar", "build_skyymenu_0.3.49"):
    assert _w not in T.s, "0.3.51 harness: still there: " + _w
if T.dst:
    T.finish()
