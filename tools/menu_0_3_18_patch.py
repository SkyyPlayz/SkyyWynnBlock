"""Derive SkyyMenu/build_skyymenu_0.3.18.py from the LIVE SkyyMenu 0.3.17 (python tools/menu_0_3_18_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: ... -> menu_0_3_17_patch.py -> 0.3.17 (= the tools/deploy_set.py SET pin,
generated - never re-run its patch, never re-build it) -> this patch -> 0.3.18. 0.3.17's files stay untouched. The harness
SkyyMenu/test_skyymenu_0.3.18.py is its own file.

0.3.18 = THE HYTALE 0.7.0 PORT (Skyy 2026-10-13: "hytale 0.7.0  is out!" + "work through your whole list, so everything is ready to play
when i get off work."; research/Hytale-0.7-Port.md). `python tools/ci/crosscheck.py` against the 0.7.0 release jar: 4 FAILs in SkyyMenu
(the engine methods no longer exist; the classes still load, the line throws NoSuchMethodError when it runs):
  1. PageManager.handleEvent(Ref, Store, CustomPageEvent)      -> handleLegacyCustomPageEvent(Ref, Store, CustomPageEvent)
     (MenuPage.watchTick's test click + PageGuard.forget's Dismiss). Same body in 0.7 (bytecode read 2026-10-13): Dismiss -> the page's
     onDismiss + no current page; Data -> handleDataEvent only while customPageRequiredAcknowledgments == 0; Acknowledge -> counter - 1.
     (New in 0.7: a Data event with NO current page goes to AnchorActionModule.tryHandle - the menu only sends its test click while it
     is the current page, so that branch is never reached from here.)
  2. PageManager.clearCustomPageAcknowledgements()             -> clearLegacyCustomPageAcknowledgements() (same body: counter = 0)
  3. ISpawnProvider.getSpawnPoint(World, UUID) (MenuPage.doSpawn, the Spawn tile) -> getSpawnPointAsync(World, UUID), a
     CompletableFuture<Transform>. Never waited for: doSpawn asks for the future and hands it a new SpawnTask (whenComplete); the task
     hops to the player's world thread (World.execute - what vanilla SpawnUtil.teleportWhenResolved does with thenAcceptAsync(.., world))
     and MenuPage.spawnResolved finishes there: still the same world (else nothing), the menu still open -> teleport() exactly as 0.3.17
     (history, close, chat line); the menu closed meanwhile -> the same teleport without touching any page (moveTo, the part of
     teleport() 0.3.17 already had); no spawn point / an error -> the 0.3.17 status line on the open menu, else one chat line.
     The global / individual spawn providers answer at once (a finished future): the teleport is one world tick later than 0.3.17.
No other behaviour change, no saved data, no setting; ROUND_PINS = {} (every port build works on its own with 0.7.0).
Every change below is recorded (CHANGES) and undone at the end to prove the generated script is 0.3.17 outside them, byte for byte.
"""
import os
import ast

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.17.py")
dst = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.18.py")
CR, LF = chr(13), chr(10)


def load(p):
    raw = open(p, encoding="utf8", newline="").read()
    return raw.replace(CR + LF, LF), (CR + LF if (CR + LF) in raw else LF)


s, NL = load(src)
OLD = s
assert 'VERSION = "0.3.17"' in s and "0.3.17: THE MENU LAYOUT EDITOR" in s and "SpawnTask" not in s, "not the generated 0.3.17 script"
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
if _set is not None and _set.get("SkyyMenu") != "0.3.17":
    print("NOTE: tools/deploy_set.py SET pins SkyyMenu %s, this patch derives from 0.3.17" % _set.get("SkyyMenu"))

# ================================================================================================ docstring + version
rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.17: THE MENU LAYOUT EDITOR''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.18: THE HYTALE 0.7.0 PORT (notes: tools/menu_0_3_18_patch.py; Skyy 2026-10-13 "hytale 0.7.0  is out!"; research/Hytale-0.7-Port.md):
       PageManager.handleEvent -> handleLegacyCustomPageEvent, clearCustomPageAcknowledgements -> clearLegacyCustomPageAcknowledgements
       (same engine bodies), the Spawn tile: ISpawnProvider.getSpawnPoint -> getSpawnPointAsync (a future, never waited for: SpawnTask
       finishes the teleport on the player's world thread - MenuPage.spawnResolved). Nothing else changed. ROUND_PINS = {}.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.18.py (CC 0.3.17 -> 0.3.18, A -Xverify:all on the 0.7.0 jar, E the page check + the Spawn
  tile executed through the 0.7.0 engine's own PageManager / spawn providers, ST two starts on a copy of the live data, AA the audit).
0.3.17: THE MENU LAYOUT EDITOR''')
rep('VERSION = "0.3.17"\n', 'VERSION = "0.3.18"\n')

# ================================================================================================ a vanilla item 0.7.0 removed
# the Mods list row of SkyyBank showed vanilla Furniture_Ancient_Chest_Large_Treasure, which Hytale 0.7.0 removed (the build's need_item
# stops on it; in game it would be an unknown item). Furniture_Ancient_Chest_Large is the same chest without the treasure (in 0.6 + 0.7;
# research/PreRelease-Compat-Report.md section 3).
rep('''    {"mod": "SkyyBank", "version": MODS_VERSIONS["SkyyBank"], "icon": "Furniture_Ancient_Chest_Large_Treasure", "check": "bank",''',
    '''    {"mod": "SkyyBank", "version": MODS_VERSIONS["SkyyBank"], "icon": "Furniture_Ancient_Chest_Large", "check": "bank",''')

# ================================================================================================ the build-time engine probes (0.7.0 names)
rep('''             ("com.hypixel.hytale.server.core.universe.world.spawn.ISpawnProvider", "getSpawnPoint"),''',
    '''             ("com.hypixel.hytale.server.core.universe.world.spawn.ISpawnProvider", "getSpawnPointAsync"),''')
rep('''for c, m in ((T["PGM"], "handleEvent"), (T["PGM"], "clearCustomPageAcknowledgements"), (T["PAGE"], "onDismiss"), (T["CPE"], "type"),''',
    '''for c, m in ((T["PGM"], "handleLegacyCustomPageEvent"), (T["PGM"], "clearLegacyCustomPageAcknowledgements"), (T["PAGE"], "onDismiss"), (T["CPE"], "type"),''')
# 0.3.18: the exact 0.7.0 signatures (B.probe checks names only) - a later engine that changes them stops the build here
rep('''# 0.3.10: every engine member the Stats page uses''', '''# 0.3.18 (Hytale 0.7.0): the exact signatures of the renamed page calls + the async spawn point
_PGM07 = pool.get(T["PGM"])
_PGM07.getMethod("handleLegacyCustomPageEvent", "(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/component/Store;L%s;)V" % T["CPE"].replace(".", "/"))
_PGM07.getMethod("clearLegacyCustomPageAcknowledgements", "()V")
pool.get("com.hypixel.hytale.server.core.universe.world.spawn.ISpawnProvider").getMethod(
    "getSpawnPointAsync", "(Lcom/hypixel/hytale/server/core/universe/world/World;Ljava/util/UUID;)Ljava/util/concurrent/CompletableFuture;")
# 0.3.10: every engine member the Stats page uses''')

# ================================================================================================ the new class
rep('''lsv  = mk("LayoutSaveTask") # 0.3.17: the 300 ms delayed layout save on the server scheduler (never on the world thread)
''', '''lsv  = mk("LayoutSaveTask") # 0.3.17: the 300 ms delayed layout save on the server scheduler (never on the world thread)
spt  = mk("SpawnTask")      # 0.3.18: the Spawn tile's async spawn point (Hytale 0.7.0) -> the player's world thread -> spawnResolved
''')
rep('''         scl, stp, sta, stc, pet, lay, lsv, pl)''', '''         scl, stp, sta, stc, pet, lay, lsv, spt, pl)''')

# ================================================================================================ PageGuard.forget + MenuPage.watchTick
rep('''# forget `page` on the server the way the client's Esc does: PageManager.handleEvent Dismiss = page.onDismiss(ref, st), then no current
# page - no packet, the acknowledgement counter untouched. Only while it is still the current page. true = it is gone now.
M(guard, r"""
public static boolean forget(@PGM@ pm, @REF@ ref, @ST@ st, @PAGE@ page) {
  if (pm == null || page == null || pm.getCustomPage() != page) return false;
  pm.handleEvent(ref, st, new @CPE@(@CPT@.Dismiss, (String) null));''', '''# forget `page` on the server the way the client's Esc does: PageManager.handleEvent Dismiss = page.onDismiss(ref, st), then no current
# page - no packet, the acknowledgement counter untouched. Only while it is still the current page. true = it is gone now.
# 0.3.18: Hytale 0.7.0 renamed it handleLegacyCustomPageEvent (same body)
M(guard, r"""
public static boolean forget(@PGM@ pm, @REF@ ref, @ST@ st, @PAGE@ page) {
  if (pm == null || page == null || pm.getCustomPage() != page) return false;
  pm.handleLegacyCustomPageEvent(ref, st, new @CPE@(@CPT@.Dismiss, (String) null));''')
rep('''  pm.handleEvent(ref, st, new @CPE@(@CPT@.Data, "{\\"a\\":\\"skyymenucheck\\",\\"n\\":\\"" + this.probeNonce + "\\"}"));''',
    '''  pm.handleLegacyCustomPageEvent(ref, st, new @CPE@(@CPT@.Data, "{\\"a\\":\\"skyymenucheck\\",\\"n\\":\\"" + this.probeNonce + "\\"}"));''')
rep('''  pm.clearCustomPageAcknowledgements();
  if (answer) {
    this.status = "Clicks were stuck''', '''  pm.clearLegacyCustomPageAcknowledgements();
  if (answer) {
    this.status = "Clicks were stuck''')

# ================================================================================================ the Spawn tile (async spawn point)
rep('''M(page, r"""
public boolean teleport(@REF@ ref, @ST@ st, @TP@ t, String label) {
  if (st.getComponent(ref, @TP@.getComponentType()) != null) { this.status = "You are already teleporting."; rebuild(); return false; }
  @WLD@ here = null;''', '''# 0.3.18: the teleport itself (Teleport component + the TeleportHistory entry) is moveTo, shared with spawnResolved when the menu was
# closed before the spawn point arrived; teleport() = moveTo + close + the chat line, exactly 0.3.17's steps in 0.3.17's order
M(page, r"""
public void moveTo(@REF@ ref, @ST@ st, @TP@ t, String label) {
  @WLD@ here = null;''')
rep('''  } catch (Throwable t2) { }
  closePage(ref, st);
  this.playerRef.sendMessage(@MSG@.raw("[Menu] Teleporting to " + label + "..."));
  return true;
}""")''', '''  } catch (Throwable t2) { }
}""")
M(page, r"""
public boolean teleport(@REF@ ref, @ST@ st, @TP@ t, String label) {
  if (st.getComponent(ref, @TP@.getComponentType()) != null) { this.status = "You are already teleporting."; rebuild(); return false; }
  moveTo(ref, st, t, label);
  closePage(ref, st);
  this.playerRef.sendMessage(@MSG@.raw("[Menu] Teleporting to " + label + "..."));
  return true;
}""")''')
rep('''M(page, r"""
public void doSpawn(@REF@ ref, @ST@ st) {
  @WLD@ target = @UNI@.get().getDefaultWorld();
  if (target == null) { this.status = "The main world is not loaded."; rebuild(); return; }
  @TRF@ where = target.getWorldConfig().getSpawnProvider().getSpawnPoint(target, this.playerRef.getUuid());
  if (where == null) { this.status = "The main world has no spawn point."; rebuild(); return; }
  teleport(ref, st, @TP@.createForPlayer(target, where), "Spawn");
}""")''', '''# 0.3.18 (Hytale 0.7.0): the spawn point is a CompletableFuture now (getSpawnPointAsync; the height-map provider loads a chunk first).
# Never waited for on the world thread: SpawnTask gets it (whenComplete), hops to the player's world thread and calls spawnResolved.
# There: the menu still open -> teleport() as 0.3.17; closed meanwhile -> moveTo + the chat line (no page touched); no spawn point / an
# error -> 0.3.17's status line on the open menu, else a chat line.
M(page, r"""
public void spawnResolved(@REF@ ref, @ST@ st, @WLD@ target, Object result, Throwable error) {
  @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
  boolean open = p != null && p.getPageManager() != null && p.getPageManager().getCustomPage() == this;
  if (error != null) @PKG@.MenuUtil.warn("the spawn point of the main world could not be found for " + @PKG@.PageGuard.who(this.playerRef) + ": " + error);
  if (error != null || !(result instanceof @TRF@)) {
    String why = error != null ? "The spawn point could not be found - try again." : "The main world has no spawn point.";
    if (open) { this.status = why; rebuild(); }
    else this.playerRef.sendMessage(@MSG@.raw("[Menu] " + why));
    return;
  }
  @TP@ t = @TP@.createForPlayer(target, (@TRF@) result);
  if (open) { teleport(ref, st, t, "Spawn"); return; }
  if (st.getComponent(ref, @TP@.getComponentType()) != null) return;
  moveTo(ref, st, t, "Spawn");
  this.playerRef.sendMessage(@MSG@.raw("[Menu] Teleporting to Spawn..."));
}""")
F(spt, "public @PKG@.MenuPage page;")
F(spt, "public @PR@ pr;")
F(spt, "public @WLD@ target;")
F(spt, "public @WLD@ home;")
F(spt, "public volatile Object result;")
F(spt, "public volatile Throwable error;")
spt.addInterface(pool.get("java.lang.Runnable"))
spt.addInterface(pool.get("java.util.function.BiConsumer"))
C(spt, r"""
public SpawnTask(@PKG@.MenuPage page, @PR@ pr, @WLD@ target, @WLD@ home) { this.page = page; this.pr = pr; this.target = target; this.home = home; }""")
# any thread (the future's): keep the answer, hop to the world the player clicked in
M(spt, r"""
public void accept(Object r, Object e) {
  this.result = r;
  this.error = e instanceof Throwable ? (Throwable) e : null;
  try { this.home.execute(this); }
  catch (Throwable t) { @PKG@.MenuUtil.warn("could not finish the Spawn teleport: " + t); }
}""")
# that world's thread: only while the player is still in it (a world change meanwhile = they went somewhere else - nothing to do)
M(spt, r"""
public void run() {
  try {
    if (this.pr == null || !this.pr.isValid()) return;
    java.util.UUID wu = this.pr.getWorldUuid();
    if (wu == null || @UNI@.get().getWorld(wu) != this.home) return;
    @REF@ r = this.pr.getReference();
    if (r == null || !r.isValid()) return;
    @ST@ st = r.getStore();
    if (st == null) return;
    this.page.spawnResolved(r, st, this.target, this.result, this.error);
  } catch (Throwable t) { @PKG@.MenuUtil.warn("the Spawn teleport failed: " + t); }
}""")
M(page, r"""
public void doSpawn(@REF@ ref, @ST@ st) {
  @WLD@ target = @UNI@.get().getDefaultWorld();
  if (target == null) { this.status = "The main world is not loaded."; rebuild(); return; }
  @WLD@ home = null;
  try { java.util.UUID wu = this.playerRef.getWorldUuid(); home = wu == null ? null : @UNI@.get().getWorld(wu); } catch (Throwable t0) { }
  if (home == null) { this.status = "The main world has no spawn point."; rebuild(); return; }
  java.util.concurrent.CompletableFuture f = target.getWorldConfig().getSpawnProvider().getSpawnPointAsync(target, this.playerRef.getUuid());
  if (f == null) { this.status = "The main world has no spawn point."; rebuild(); return; }
  f.whenComplete(new @PKG@.SpawnTask(this, this.playerRef, target, home));
}""")''')

# ================================================================================================ ROUND_PINS + the patch name
rep('''# 0.3.17: EMPTY - the layout editor, SkyyMenu's own files only.
ROUND_PINS = {}
''', '''# 0.3.17: EMPTY - the layout editor, SkyyMenu's own files only.
# 0.3.18: EMPTY - the Hytale 0.7.0 port (every port build works on its own with the 0.7.0 engine).
ROUND_PINS = {}
''')
rep('_PATCH = "tools/menu_0_3_17_patch.py"', '_PATCH = "tools/menu_0_3_18_patch.py"')

# ================================================================================================ checks on the result
assert "@@" not in s, "a @@ token is left in the generated script"
assert "pm.handleEvent(" not in s, "0.3.18: no call of the removed PageManager.handleEvent is left"
assert "pm.clearCustomPageAcknowledgements()" not in s and ".getSpawnPoint(" not in s, "0.3.18: no removed engine call is left"
assert s.index("public void moveTo(") < s.index("public boolean teleport(") < s.index("public void spawnResolved(") \
    < s.index("public SpawnTask(") < s.index("public void doSpawn("), "definitions before use"
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.3.17 outside the recorded changes"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(dst, ROOT), "(%d lines; 0.3.17 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
