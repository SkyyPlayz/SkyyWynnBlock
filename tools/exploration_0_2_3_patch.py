"""Derive SkyyExploration/build_skyyexploration_0.2.3.py from the LIVE 0.2.2 (build_skyyexploration_0.2.2.py = the tools/deploy_set.py SET
pin; 0.2.2 itself was made by COPY + EDIT from 0.2.1 - SkyyExploration had no patch script before this one). Edit THIS patch, never the
generated build script; 0.2.2's files stay untouched.
Run:  python tools/exploration_0_2_3_patch.py   then   python SkyyExploration/build_skyyexploration_0.2.3.py   (never --deploy)
      then  python SkyyExploration/test_skyyexploration_0.2.3.py   (needs SkyyExploration-0.2.2.jar too)

0.2.3 = THE PAGE GUARD (Skyy 2026-10-04 12:55: the /explore page showed the Zones tab, then the OVERVIEW tab click stayed on the
client's "Loading..." - no SkyyExploration line in the log; after many world changes during the minimap probe; closing the page and
reopening it with /explore fixed it).
TWO ways 0.2.2 leaves a click unanswered (the client waits for an answer to every click and shows "Loading..." until one comes):
  a) its OWN 1 s click guard: ExplorePage / AdminPage.handleDataEvent returned WITHOUT AN ANSWER for every click within 1 s of the page's
     last build (0.2 spec: "rebuilt only after a click, at most once a second"). A quick second click - Zones, then Overview - was
     dropped silently. This matches the report best: a re-opened page answers again, and the Zones click before it was answered.
     Every other silent end (an unknown / malformed click, a click while the admin's world is not known, a stale row, an error) also
     left the client waiting.
  b) the engine's stuck page acknowledgement (SkyyBank 0.1.6 / SkyyMenu 0.3.6 root cause, docs/log/2026-10.md 2026-10-03): a page left
     open on the server across a world change, then any page packet for it on the new world (a bench, a setPage(None), a redraw) = +1
     the client never acknowledges -> every page ignores clicks until the next world change. SkyyMenu 0.3.6's PageGuard already forgets
     every stale page at the world join while SkyyMenu is installed; 0.2.3 makes Exploration's own pages safe on their own too.
WHAT 0.2.3 CHANGES (Java; the page look, texts and bindings are 0.2.2's byte for byte - the harness compares every page state):
 1. EVERY CLICK IS ANSWERED. The tab buttons always act (the tab row never moves, so a quick second click cannot land on another
    button). Any other click within 1 s of the last build is answered WITHOUT acting (ExplorePage / AdminPage.answer: a short page
    update that sets the result line to what it already shows - nothing changes, the client stops waiting); the 1 s guard against
    double clicks (a second click landing on a button of the new layout, the admin page's "click again within 10 s" removes) stays.
    Unknown / malformed clicks, a click with no world, a stale row and an error (logged as before) are answered the same way. The one
    click that is not answered: the admin Teleport, which closes the page (an answer to a closed page is exactly the stray packet of b).
    answer() never sends to a page that is no longer the player's open page.
 2. ExGuard - the world-join guard for Exploration's two pages (SkyyMenu 0.3.6 PageGuard's pattern, limited to ExplorePage /
    AdminPage: SkyyMenu's PageGuard handles every other mod's page; doing it twice would only duplicate log lines): an
    AddPlayerToWorldEvent listener (registerGlobal). The page the player still has on the server when the engine adds them to a world
    is from before the world change (the client drops its page at JoinWorld): if it is an Exploration page it is forgotten right there
    (PageManager.handleEvent Dismiss with no ref / store - both pages keep the engine's empty onDismiss, so no page code runs; no
    packet; the counter untouched). It also counts world joins per player (JOINS) for changedWorld. JOINS is never trimmed (one small
    entry per player seen since the server start; a stale count only matters while a page is open).
 3. ExWatch - the safety net (SkyyMenu 0.3.6 MenuWatch / SkyyBank 0.1.6 BankWatch pattern) for both pages: every 1 s while an
    Exploration page is open (scheduler -> the player's world thread): closed / replaced -> done; the player changed world since the
    page's first build (another world, or a join counted since) -> forgotten on the server (no packet) -> done; 1 s after the page's
    last packet a test click through the engine's own gate (PageManager.handleEvent Data -> the page's handleDataEvent only while
    customPageRequiredAcknowledgments == 0); dropped -> PageManager.clearCustomPageAcknowledgements() (the public reset the engine runs
    at a world change) + an answer (the page redrawn with a "Clicks were stuck ... fixed" result line; at most HEAL_ANSWERS = 3 per page,
    later heals reset silently - never a periodic page update). A healthy page sends nothing.
 Plugin: setup() sets ExGuard.STOP = false + ExGuard.EXEC = HytaleServer.SCHEDULED_EXECUTOR and registers ExGuard; shutdown() sets
 ExGuard.STOP; the ready line says "page guard on".
NOT CHANGED: every other class, the page markup, ids, texts, bindings and colours, commands / permissions, files, bridge keys, config
rows. The DEPLOY GATE print (kit base look unseen) is reworded: 0.2.2 with the same look is live and was seen in game (2026-10-04).

Every change below is recorded (CHANGES) and undone at the end to prove the generated script is 0.2.2 outside them, byte for byte.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyExploration", "build_skyyexploration_0.2.2.py")
dst = os.path.join(ROOT, "SkyyExploration", "build_skyyexploration_0.2.3.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.2.2"' in s and s.startswith('"""SkyyExploration 0.2.2 - build script'), "not the 0.2.2 script"
assert "@@" not in s, "0.2.2 already holds a @@ token"
CHANGES = []            # (new text, old text) of every change, in order: undone at the end


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:120])
    s = s.replace(old, new, 1)
    CHANGES.append((new, old))


TOKEN_RE = re.compile(r"@@[A-Z0-9]+@@")


def fill(template, values):
    """@@NAME@@ replacement: every token of `values` occurs exactly once, no value holds "@@", none is left over"""
    for name, value in values.items():
        tok = "@@%s@@" % name
        assert template.count(tok) == 1, "token %s occurs %d times" % (tok, template.count(tok))
        assert "@@" not in value, "the value for %s holds '@@'" % tok
        template = template.replace(tok, value)
    left = TOKEN_RE.findall(template)
    assert not left, "tokens left unfilled: %s" % left
    return template


# ================================================================================================ docstring + version
DOC_NEW = '''"""SkyyExploration 0.2.3 - build script (javassist via jpype, tools/skyybuild.py). GENERATED by tools/exploration_0_2_3_patch.py from
the LIVE 0.2.2 (build_skyyexploration_0.2.2.py, the tools/deploy_set.py SET pin) - edit the patch, never this file.
Owner: Skyy (they/them).

Run:   python build_skyyexploration_0.2.3.py          -> SkyyExploration/SkyyExploration-0.2.3.jar  (never --deploy from a workflow)

0.2.3 (2026-10-05): THE PAGE GUARD - Skyy 2026-10-04: the /explore Overview tab click stayed on the client's "Loading..." after many
      world changes; close + /explore fixed it. Notes: tools/exploration_0_2_3_patch.py.
  1. Every click is answered: the 0.2 "at most one click a second" guard returned WITHOUT AN ANSWER (a quick Zones -> Overview left the
     client waiting). Now tab clicks always act; any other click within 1 s is answered without acting (answer(): the result line set to
     what it shows); unknown / malformed clicks, no world, a stale row and errors are answered too. Only the admin Teleport (it closes
     the page) sends nothing. answer() never sends to a page that is no longer open.
  2. ExGuard (AddPlayerToWorldEvent, SkyyMenu 0.3.6 PageGuard's pattern for Exploration's own two pages): an Exploration page still
     open on the server when the engine adds the player to a world is forgotten there (PageManager.handleEvent Dismiss - no packet,
     the acknowledgement counter untouched), so no later setPage / bench / redraw on the new world can leave every page stuck.
  3. ExWatch, the safety net (MenuWatch / BankWatch pattern): every 1 s while an Exploration page is open - changed world -> forgotten
     (no packet); 1 s after the page's last packet a test click through the engine's gate; dropped -> clearCustomPageAcknowledgements
     + an answer ("Clicks were stuck ... fixed. Click again.", at most 3 per page). A healthy page sends nothing.
@@CHECKED@@
  UNVERIFIED (needs the game): the client dropping its page at JoinWorld (the SkyyBank 0.1.6 model); the short answer (a page update
    with only the result line) ending a "Loading..." box (the bank's short answer is the same kind of update); a remote client slower
    than 1 s to acknowledge can make a check reset early (the engine's harmless "unexpected acknowledgement" line follows).

0.2.2 notes (unchanged below):
'''
CHECKED = """  CHECKED 2026-10-05 with SkyyExploration/test_skyyexploration_0.2.3.py (re-run it; it needs SkyyExploration-0.2.2.jar): 18758
    checks, 0 fail. A 83 / 83 classes of 0.2.3 and 81 / 81 of 0.2.2 load + verify (-Xverify:all). B-D all 17 ExplorePage + 15
    AdminPage states send EXACTLY 0.2.2's page (every command + binding; the 0.2.2 harness's markup / layout / text-fit checks pass).
    E msgColor / stColor as 0.2.2. F only ExplorePage + AdminPage (build + handleDataEvent changed; answer / changedWorld / isOpen /
    watchTick + 9 guard fields new), SkyyExplorationPlugin (setup / shutdown) and manifest differ; CfgFn / CfgRows / ExpCfg by the
    version string only; new ExGuard + ExWatch. P on the engine's own PageManager with a model client, no SkyyMenu: 0.2.2 REPRODUCES
    Skyy's report (Zones, then Overview within 1 s: no packet, the client stays on Loading..., 0 acknowledgements pending; a re-opened
    /explore works) and the stuck counter (a page left open across a world change + a page close on the new world: 1 pending, the
    re-opened page drops clicks); 0.2.3 shows Overview at once, answers quick / unknown / empty clicks without acting, forgets the page
    at the world join (0 pending), heals a stray +1 (one WARNING, reset, answer; at most 3 answers), a healthy check sends nothing, the
    check forgets the page on a new world without the event (and a check run on the old world thread after a switch touches nothing - review F1), a foreign page is left to SkyyMenu, no answer to a closed page, the admin
    page the same; the real timer chain (a real scheduled executor -> World.execute -> watchTick) heals in ~1 s."""
rep('''"""SkyyExploration 0.2.2 - build script (javassist via jpype, tools/skyybuild.py). Derived by COPY + EDIT from the LIVE 0.2.1
(build_skyyexploration_0.2.1.py, the tools/deploy_set.py SET pin; SkyyExploration has no patch script, that file stays untouched).
Owner: Skyy (they/them).

Run:   python build_skyyexploration_0.2.2.py          -> SkyyExploration/SkyyExploration-0.2.2.jar  (never --deploy from a workflow)
''', fill(DOC_NEW, {"CHECKED": CHECKED}) + '''0.2.2 - derived by COPY + EDIT from the LIVE 0.2.1 (build_skyyexploration_0.2.1.py, then the SET pin; that file stays untouched).
Run:   python build_skyyexploration_0.2.2.py          -> SkyyExploration/SkyyExploration-0.2.2.jar  (never --deploy from a workflow)
''')
rep('VERSION = "0.2.2"', 'VERSION = "0.2.3"')

# ================================================================================================ engine types + probes
rep('''    "PGE": "com.hypixel.hytale.protocol.packets.interface_.Page",
}''', '''    "PGE": "com.hypixel.hytale.protocol.packets.interface_.Page",
    # 0.2.3: the page guard - the page event the engine itself handles (Dismiss / Data), the world-join event and its holder
    "CPE": "com.hypixel.hytale.protocol.packets.interface_.CustomPageEvent",
    "CPT": "com.hypixel.hytale.protocol.packets.interface_.CustomPageEventType",
    "ATW": "com.hypixel.hytale.server.core.event.events.player.AddPlayerToWorldEvent",
    "HLD": "com.hypixel.hytale.component.Holder",
}''')
rep('''             ("UNI", "getWorld"), ("V3D", "y"), ("CTX", "get"), ("WLD", "getName")):
    B.probe(pool, T.get(c, c), m)
''', '''             ("UNI", "getWorld"), ("V3D", "y"), ("CTX", "get"), ("WLD", "getName")):
    B.probe(pool, T.get(c, c), m)
# 0.2.3: every engine member the page guard uses (all public; rebuild / sendUpdate stay on 'this' inside the pages)
for c, m in (("PGM", "handleEvent"), ("PGM", "clearCustomPageAcknowledgements"), ("PGM", "getCustomPage"), ("PAGE", "onDismiss"),
             ("PAGE", "sendUpdate"), ("CPE", "type"), ("CPE", "data"), ("CPT", "Dismiss"), ("CPT", "Data"), ("EST", "getWorld"),
             ("ATW", "getHolder"), ("ATW", "getWorld"), ("HLD", "getComponent"), ("EREG", "registerGlobal"), ("HSV", "SCHEDULED_EXECUTOR")):
    B.probe(pool, T.get(c, c), m)
''')
rep('''pl = pool.makeClass(PKG + ".SkyyExplorationPlugin", pool.get(T["JP"]))
''', '''pl = pool.makeClass(PKG + ".SkyyExplorationPlugin", pool.get(T["JP"]))
guard = pool.makeClass(PKG + ".ExGuard")       # 0.2.3: the world-join guard for the two Exploration pages + forget / joins helpers
watch = pool.makeClass(PKG + ".ExWatch")       # 0.2.3: the pages' safety net (SkyyMenu MenuWatch / SkyyBank BankWatch pattern)
''')

# ================================================================================================ ExGuard + ExWatch part 1
GUARD_SRC = r'''# ================= 0.2.3 ExGuard: THE WORLD-JOIN GUARD for ExplorePage / AdminPage (tools/exploration_0_2_3_patch.py) =================
# World.addPlayer - the one way into a world - dispatches AddPlayerToWorldEvent while the player is in no world store, BEFORE
# onSetupPlayerJoining clears the page acknowledgements (and keeps PageManager.customPage). The client drops its page at the world
# change, so an Exploration page the server still has here is stale: forgotten without a packet (both pages keep the engine's empty
# onDismiss, so no page code runs). Every other mod's page is SkyyMenu 0.3.6 PageGuard's (the same listener for every page).
# EXEC = HytaleServer.SCHEDULED_EXECUTOR (set in setup(); null = not set up: no checks, said once a minute). JOINS = world joins seen
# per player (changedWorld); never trimmed - one small entry per player seen since the server start.
guard.addInterface(pool.get("java.util.function.Consumer"))
F(guard, "public static volatile boolean STOP = false;")
F(guard, "public static volatile java.util.concurrent.ScheduledExecutorService EXEC;")
F(guard, "public static final java.util.concurrent.ConcurrentHashMap JOINS = new java.util.concurrent.ConcurrentHashMap();")
F(guard, "public static volatile long WARNED = 0L;")
F(guard, "public static volatile int FORGOT = 0;")
C(guard, "public ExGuard() { }")
M(guard, r"""
public static int joins(java.util.UUID u) {
  if (u == null) return 0;
  Object o = JOINS.get(u);
  return o instanceof Integer ? ((Integer) o).intValue() : 0;
}""")
M(guard, r"""
public static void bump(java.util.UUID u) {
  if (u == null) return;
  JOINS.put(u, Integer.valueOf(joins(u) + 1));
}""")
M(guard, r"""
public static boolean mine(Object page) {
  return page instanceof @PKG@.ExplorePage || page instanceof @PKG@.AdminPage;
}""")
M(guard, r"""
public static String who(@PR@ pr) {
  try {
    if (pr == null) return "?";
    String n = pr.getUsername();
    return n == null ? String.valueOf(pr.getUuid()) : n;
  } catch (Throwable t) { return "?"; }
}""")
M(guard, r"""
public static void warnOnce(String msg) {
  long now = System.currentTimeMillis();
  if (now - WARNED < 60000L) return;
  WARNED = now;
  @PKG@.ExpCfg.warn(msg);
}""")
# forget `page` on the server the way the client's Esc does: PageManager.handleEvent Dismiss = page.onDismiss(ref, st), then no current
# page - no packet, the acknowledgement counter untouched. Only while it is still the current page. true = it is gone now.
M(guard, r"""
public static boolean forget(@PGM@ pm, @REF@ ref, @ST@ st, @PAGE@ page) {
  if (pm == null || page == null || pm.getCustomPage() != page) return false;
  pm.handleEvent(ref, st, new @CPE@(@CPT@.Dismiss, (String) null));
  return pm.getCustomPage() != page;
}""")
M(guard, r"""
public void accept(Object ev) {
  try {
    if (STOP || !(ev instanceof @ATW@)) return;
    @ATW@ e = (@ATW@) ev;
    @HLD@ h = e.getHolder();
    if (h == null) return;
    @PR@ pr = (@PR@) h.getComponent(@PR@.getComponentType());
    if (pr != null) bump(pr.getUuid());
    @PLA@ p = (@PLA@) h.getComponent(@PLA@.getComponentType());
    if (p == null) return;
    @PGM@ pm = p.getPageManager();
    if (pm == null) return;
    @PAGE@ cp = pm.getCustomPage();
    if (cp == null || !mine(cp)) return;
    if (forget(pm, (@REF@) null, (@ST@) null, cp)) {
      FORGOT = FORGOT + 1;
      @PKG@.ExpCfg.info(who(pr) + " changed world with the " + (cp instanceof @PKG@.AdminPage ? "exploration admin" : "exploration") + " page still open on the server - forgot it there too (no packet; the game client closes every page at a world change)");
    }
  } catch (Throwable t) {
    warnOnce("the world-change page check failed: " + t);
  }
}""")

# ================= 0.2.3 ExWatch part 1: the pages' safety net (part 2 after AdminPage.watchTick) =================
# target == null: the scheduler-thread tick; target != null: the check on that world's thread (the page's watchTick does every
# PageManager call). One check per second per open Exploration page; it ends when the page is closed or replaced, the player leaves,
# after 30 failed checks, or at shutdown (STOP).
watch.addInterface(pool.get("java.lang.Runnable"))
F(watch, "public static final long PERIOD = 1000L;")
F(watch, "public @PAGE@ page;")
F(watch, "public @PR@ pr;")
F(watch, "public @WLD@ target;")
F(watch, "public int fails;")
C(watch, r"""
public ExWatch(@PAGE@ page, @PR@ pr, @WLD@ target, int fails) {
  this.page = page;
  this.pr = pr;
  this.target = target;
  this.fails = fails;
}""")
M(watch, r"""
public static void schedule(@PAGE@ page, @PR@ pr, int fails) {
  if (@PKG@.ExGuard.STOP || page == null || pr == null) return;
  java.util.concurrent.ScheduledExecutorService ex = @PKG@.ExGuard.EXEC;
  try {
    if (ex == null) throw new java.lang.IllegalStateException("no scheduler (SkyyExploration not set up)");
    ex.schedule(new @PKG@.ExWatch(page, pr, (@WLD@) null, fails), PERIOD, java.util.concurrent.TimeUnit.MILLISECONDS);
  } catch (Throwable t) {
    @PKG@.ExGuard.warnOnce("the exploration page check could not be scheduled (" + t + ") - the page still works, a click the game drops is just not healed");
  }
}""")

'''
rep('''# ================= ExplorePage: the inline /explore page.''', GUARD_SRC + '''# ================= ExplorePage: the inline /explore page.''')

# ================================================================================================ the page pieces (both pages)
HEAL_TEXT = "Clicks were stuck (a game hiccup after a teleport) - fixed. Click again."
assert '"' not in HEAL_TEXT and "\\" not in HEAL_TEXT and "@" not in HEAL_TEXT and len(HEAL_TEXT) <= 80
PAGE_FIELDS = '''# 0.2.3: the world the page was first built in (openCustomPage) + the player's world joins then (ExGuard.JOINS), the send time of its last
# packet (the check waits SETTLE after it), the safety net's state. At most HEAL_ANSWERS heal answers per page.
F(@@CLS@@, "public @WLD@ world;")
F(@@CLS@@, "public int joinSeen;")
F(@@CLS@@, "public volatile long lastSend;")
F(@@CLS@@, "public boolean watching;")
F(@@CLS@@, "public String probeNonce;")
F(@@CLS@@, "public boolean probeSeen;")
F(@@CLS@@, "public int heals;")
F(@@CLS@@, "public static final long SETTLE = 1000L;")
F(@@CLS@@, "public static final int HEAL_ANSWERS = 3;")
'''
PAGE_METHODS = '''# 0.2.3: did the player change world since this page was opened? - the world of its first build differs from `now`, or ExGuard counted
# a world join of that player since (a re-join of the same world counts too). Without a first build only the join count.
M(@@CLS@@, r"""
public boolean changedWorld(@WLD@ now) {
  if (this.world != null && now != null && now != this.world) return true;
  return this.watching && this.joinSeen != @PKG@.ExGuard.joins(this.playerRef.getUuid());
}""")
# 0.2.3: is this page still the player's open page? (world thread) - an answer to a closed page is a packet the client never acknowledges
M(@@CLS@@, r"""
public boolean isOpen() {
  @REF@ ref = this.playerRef.getReference();
  if (ref == null || !ref.isValid()) return false;
  @ST@ st = ref.getStore();
  if (st == null) return false;
  @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
  if (p == null || p.getPageManager() == null) return false;
  return p.getPageManager().getCustomPage() == this;
}""")
# 0.2.3: the answer to a click that does not act (the 1 s guard, unknown / malformed, errors): a short page update that sets the result
# line to what it already shows - nothing changes on screen, the client's "Loading..." ends. Never to a page that is not open.
M(@@CLS@@, r"""
public void answer() {
  try {
    if (!isOpen()) return;
    @UCB@ b = new @UCB@();
    @@SETMSG@@
    sendUpdate(b, false);
    this.lastSend = System.currentTimeMillis();
  } catch (Throwable t) { @PKG@.ExpCfg.warn("@@WHAT@@ answer failed: " + t); }
}""")
'''
PAGE_BUILD = '''  this.lastSend = System.currentTimeMillis();
  if (!this.watching && ref != null && st != null) {
    this.watching = true;
    try {
      Object ex0 = st.getExternalData();
      if (ex0 instanceof @EST@) this.world = ((@EST@) ex0).getWorld();
    } catch (Throwable tw) { this.world = null; }
    this.joinSeen = @PKG@.ExGuard.joins(this.playerRef.getUuid());
    @PKG@.ExWatch.schedule(this, this.playerRef, 0);
  }
'''
PROBE_CLICK = '''    if (data.indexOf("\\"@@CHECK@@\\"") >= 0) {
      if (this.probeNonce != null && this.probeNonce.length() > 0 && data.indexOf("\\"" + this.probeNonce + "\\"") >= 0) this.probeSeen = true;
      return;
    }
'''
WATCH_TICK = '''# ================= 0.2.3 @@CLS2@@.watchTick: the page's check, on the player's world thread (ExWatch hands it here). true = again.
#  - the player's store is not the executing world's (switched world after the hop) -> touch nothing, check again later;
#  - the page is no longer the open page (closed / replaced) -> done;
#  - the player changed world since it opened -> the client dropped it: forget it on the server (ExGuard.forget, no packet) -> done;
#  - SETTLE after the page's last packet: a test click through the engine's own gate (PageManager.handleEvent Data -> this page's
#    handleDataEvent only while customPageRequiredAcknowledgments == 0). It arrives -> healthy, nothing is sent. It does not -> the game
#    is dropping this page's clicks: log, PageManager.clearCustomPageAcknowledgements() (what a world change runs) and, for the first
#    HEAL_ANSWERS heals of this page, an answer (the page redrawn with the heal line); later heals reset silently.
M(@@CLS@@, r"""
public boolean watchTick(@WLD@ now) {
  @REF@ ref = this.playerRef.getReference();
  if (ref == null || !ref.isValid()) return this.playerRef.isValid();
  @ST@ st = ref.getStore();
  if (st == null) return true;
  // review F1: only on the thread of the world the player's store belongs to (the player may have switched world after the hop)
  Object exw = st.getExternalData();
  if (!(exw instanceof @EST@) || ((@EST@) exw).getWorld() != now) return true;
  @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
  if (p == null) return true;
  @PGM@ pm = p.getPageManager();
  if (pm == null) return true;
  if (pm.getCustomPage() != this) return false;
  if (changedWorld(now)) {
    if (@PKG@.ExGuard.forget(pm, ref, st, this)) @PKG@.ExpCfg.info("the @@WHAT@@ of " + @PKG@.ExGuard.who(this.playerRef) + " was still open on the server after a world change - forgot it there too (no packet)");
    return false;
  }
  long t = System.currentTimeMillis();
  if (t - this.lastSend < SETTLE) return true;
  this.probeNonce = Long.toHexString(System.nanoTime() ^ (((long) System.identityHashCode(this)) << 24));
  this.probeSeen = false;
  pm.handleEvent(ref, st, new @CPE@(@CPT@.Data, "{\\"a\\":\\"@@CHECK@@\\",\\"n\\":\\"" + this.probeNonce + "\\"}"));
  if (this.probeSeen) return true;
  if (pm.getCustomPage() != this) return false;
  this.heals = this.heals + 1;
  boolean answer = this.heals <= HEAL_ANSWERS;
  if (this.heals <= 3 || this.heals % 60 == 0) @PKG@.ExpCfg.warn("the game was dropping " + @PKG@.ExGuard.who(this.playerRef) + "'s @@WHAT@@ clicks (it still waited for a page acknowledgement the client will never send - e.g. a page update or close sent to a page the client no longer shows); reset the page acknowledgements" + (answer ? " and answered the page" : "") + " (" + this.heals + ")");
  pm.clearCustomPageAcknowledgements();
  if (answer) {
    this.msg = "@@HEAL@@";
    rebuild();
  }
  return true;
}""")
'''
EX = {"CLS": "page", "CLS2": "ExplorePage", "WHAT": "exploration page", "CHECK": "skyyexcheck",
      "SETMSG": 'b.set("#SkyyExMsg.Text", this.msg == null ? "" : this.msg);', "HEAL": HEAL_TEXT}
XA = {"CLS": "apg", "CLS2": "AdminPage", "WHAT": "exploration admin page", "CHECK": "skyyxacheck",
      "SETMSG": 'b.set("#SkyyXaMsg.Text", nz(@PKG@.ExAdminOps.textOf(this.msg)));', "HEAL": "=" + HEAL_TEXT}


def tpl(text, vals):
    out = text
    for k, v in vals.items():
        out = out.replace("@@%s@@" % k, v)
    assert not TOKEN_RE.findall(out), "tokens left: %s" % TOKEN_RE.findall(out)
    return out


# the 0.2.2 build lines the page's own msg answer must match (the answer sets exactly what build sets)
assert s.count('b.set("#SkyyExMsg.Text", this.msg == null ? "" : this.msg);') == 1
assert s.count('jS("SkyyXaMsg", "@PKG@.ExAdminOps.textOf(this.msg)")') == 1

# ================================================================================================ ExplorePage
rep('''F(page, "public int ckIdx;")
''', '''F(page, "public int ckIdx;")
''' + tpl(PAGE_FIELDS, EX))
rep('''M(page, r"""
public static String nz(String s) {''', tpl(PAGE_METHODS, EX) + '''M(page, r"""
public static String nz(String s) {''')
rep('''public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.lastBuild = System.currentTimeMillis();
  java.util.UUID u = this.playerRef.getUuid();
  String k = @PKG@.ExpIO.pkey(u);''', '''public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.lastBuild = System.currentTimeMillis();
''' + PAGE_BUILD + '''  java.util.UUID u = this.playerRef.getUuid();
  String k = @PKG@.ExpIO.pkey(u);''')
rep('''    if (data == null) return;
    if (System.currentTimeMillis() - this.lastBuild < 1000L) return;
    if (data.indexOf("exskills\\"") >= 0) {''', '''    if (data == null) return;
''' + tpl(PROBE_CLICK, EX) + '''    // 0.2.3: the tabs always act (the tab row never moves: a quick second click cannot land on another button)
    for (int i = 0; i < 4; i++) {
      if (data.indexOf("extab" + i + "\\"") >= 0) { this.tab = i; this.msg = ""; this.ckPage = 0; rebuild(); return; }
    }
    // 0.2.3: any other click within 1 s of the last build is ANSWERED without acting (0.2.2 returned silently: "Loading..." stayed)
    if (System.currentTimeMillis() - this.lastBuild < 1000L) { answer(); return; }
    if (data.indexOf("exskills\\"") >= 0) {''')
rep('''      @CMGR@.get().handleCommand(this.playerRef, "tree exploration");
      return;
    }
    for (int i = 0; i < 4; i++) {
      if (data.indexOf("extab" + i + "\\"") >= 0) { this.tab = i; this.msg = ""; this.ckPage = 0; rebuild(); return; }
    }
''', '''      @CMGR@.get().handleCommand(this.playerRef, "tree exploration");
      return;
    }
''')
rep('''      if (data.indexOf("exuse" + i + "\\"") >= 0) { this.msg = @PKG@.ExpTitles.choose(this.playerRef, i); rebuild(); return; }
    }
  } catch (Throwable e) { @PKG@.ExpCfg.warn("explore page event failed: " + e); }
}""")
''', '''      if (data.indexOf("exuse" + i + "\\"") >= 0) { this.msg = @PKG@.ExpTitles.choose(this.playerRef, i); rebuild(); return; }
    }
    answer();
  } catch (Throwable e) { @PKG@.ExpCfg.warn("explore page event failed: " + e); answer(); }
}""")
''' + tpl(WATCH_TICK, EX))

# ================================================================================================ AdminPage
rep('''    F(apg, f)
# ---- layout (every height proven here;''', '''    F(apg, f)
''' + tpl(PAGE_FIELDS, XA) + '''# ---- layout (every height proven here;''')
rep('''_XATABA = {"right": SUI.TAB_GAP}
''', '''_XATABA = {"right": SUI.TAB_GAP}
''' + tpl(PAGE_METHODS, XA))
rep('''  this.lastBuild = System.currentTimeMillis();
  java.util.UUID u = this.playerRef.getUuid();
  @WLD@ w = @PKG@.ExAdminOps.worldOf(st);''', '''  this.lastBuild = System.currentTimeMillis();
''' + PAGE_BUILD + '''  java.util.UUID u = this.playerRef.getUuid();
  @WLD@ w = @PKG@.ExAdminOps.worldOf(st);''')
rep('''    if (data == null) return;
    long now = System.currentTimeMillis();
    if (now - this.lastBuild < 1000L) return;
    String a = jsonStr(data, "a");
    if (a.length() == 0) return;''', '''    if (data == null) return;
''' + tpl(PROBE_CLICK, XA) + '''    long now = System.currentTimeMillis();
    String a = jsonStr(data, "a");
    // 0.2.3: the tabs always act (the tab row never moves); any other click within 1 s is ANSWERED without acting (0.2.2: silent)
    boolean tabClick = a.equals("xtab0") || a.equals("xtab1") || a.equals("xtab2");
    if (!tabClick && now - this.lastBuild < 1000L) { answer(); return; }
    if (a.length() == 0) { answer(); return; }''')
rep('''    @WLD@ w = @PKG@.ExAdminOps.worldOf(st);
    if (w == null) return;
    String wf = @PKG@.ChestReg.wf(w.getName());
    @PKG@.WorldDef wd = @PKG@.SpotReg.byWf(wf);
    if (a.equals("xtab0")''', '''    @WLD@ w = @PKG@.ExAdminOps.worldOf(st);
    if (w == null) { answer(); return; }
    String wf = @PKG@.ChestReg.wf(w.getName());
    @PKG@.WorldDef wd = @PKG@.SpotReg.byWf(wf);
    if (a.equals("xtab0")''')
rep('''      if (i < 0 || i >= 8 || this.rowIds == null || this.rowIds[i] == null) return;''',
    '''      if (i < 0 || i >= 8 || this.rowIds == null || this.rowIds[i] == null) { answer(); return; }''')
WATCH2 = r'''# ================= 0.2.3 ExWatch part 2: the scheduler-thread tick -> the player's world thread -> the page's watchTick
M(watch, r"""
public static boolean tick(@PAGE@ p, @WLD@ w) {
  if (p instanceof @PKG@.ExplorePage) return ((@PKG@.ExplorePage) p).watchTick(w);
  if (p instanceof @PKG@.AdminPage) return ((@PKG@.AdminPage) p).watchTick(w);
  return false;
}""")
# one [SkyyExploration] line for the first failure of a page's check, then quiet retries; it gives up after 30 (the page still works)
M(watch, r"""
public boolean fail(Throwable t) {
  this.fails = this.fails + 1;
  if (this.fails == 1) @PKG@.ExpCfg.warn("the exploration page check for " + @PKG@.ExGuard.who(this.pr) + " failed (retried quietly): " + t);
  return this.fails < 30;
}""")
M(watch, r"""
public void hop() {
  if (@PKG@.ExGuard.STOP) return;
  if (this.pr == null || !this.pr.isValid()) return;
  java.util.UUID wu = this.pr.getWorldUuid();
  @UNI@ uni = @UNI@.get();
  @WLD@ w = null;
  if (wu != null && uni != null) w = uni.getWorld(wu);
  if (w == null) { schedule(this.page, this.pr, this.fails); return; }
  w.execute(new @PKG@.ExWatch(this.page, this.pr, w, this.fails));
}""")
M(watch, r"""
public void run() {
  if (this.target == null) {
    try { hop(); }
    catch (Throwable t) { if (fail(t)) schedule(this.page, this.pr, this.fails); }
    return;
  }
  boolean again = false;
  try { again = tick(this.page, this.target); }
  catch (Throwable t) { again = fail(t); }
  if (again && !@PKG@.ExGuard.STOP) schedule(this.page, this.pr, this.fails);
}""")

'''
rep('''    } else return;
    this.msg = res == null ? "" : res;
    rebuild();
  } catch (Throwable e) { @PKG@.ExpCfg.warn("exploration admin page click failed: " + e); }
}""")
''', '''    } else { answer(); return; }
    this.msg = res == null ? "" : res;
    rebuild();
  } catch (Throwable e) { @PKG@.ExpCfg.warn("exploration admin page click failed: " + e); answer(); }
}""")
''' + tpl(WATCH_TICK, XA) + WATCH2)

# ================================================================================================ plugin
rep('''public void setup() {
  @PKG@.ExpCfg.LOG = getLogger();''', '''public void setup() {
  @PKG@.ExGuard.STOP = false;
  @PKG@.ExGuard.EXEC = @HSV@.SCHEDULED_EXECUTOR;
  @PKG@.ExpCfg.LOG = getLogger();''')
rep('''  getCommandRegistry().registerCommand(new @PKG@.ExploreAdminCmd());
  String chat = ''', '''  getCommandRegistry().registerCommand(new @PKG@.ExploreAdminCmd());
  getEventRegistry().registerGlobal(@ATW@.class, new @PKG@.ExGuard());
  String chat = ''')
rep('''ready - /explore, /title, /exploreadmin (admin page); "''',
    '''ready - /explore, /title, /exploreadmin (admin page); page guard on; "''')
rep('''protected void shutdown() {
  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  try { @PKG@.SpotReg.flushDirty(); } catch (Throwable t) { }''', '''protected void shutdown() {
  @PKG@.ExGuard.STOP = true;
  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  try { @PKG@.SpotReg.flushDirty(); } catch (Throwable t) { }''')
rep('''acmd, pl) + tuple(CMDS)''', '''acmd, guard, watch, pl) + tuple(CMDS)''')
rep('''    print("DEPLOY GATE: SkyyExploration %s uses the unseen kit base look''',
    '''    print("NOTE (0.2.3): the same look as 0.2.2, which is live and was seen in game (2026-10-04) - the old gate below is history")
    print("DEPLOY GATE (0.2.2 history): SkyyExploration %s uses the unseen kit base look''')

# ================================================================================================ checks on the result
assert "@@" not in s, "a @@ token is left in the generated script"
# javassist order (methods before callers): ExGuard -> ExWatch.schedule -> page fields -> changedWorld / isOpen / answer -> build ->
# handleDataEvent -> watchTick (Explore) -> AdminPage the same -> ExWatch.tick / hop / run
_o = [s.index(x) for x in ("public static boolean forget(@PGM@ pm,", "public void accept(Object ev) {\n  try {\n    if (STOP || !(ev instanceof @ATW@))",
                           "public static void schedule(@PAGE@ page, @PR@ pr, int fails)", 'F(page, "public int joinSeen;")',
                           "public boolean changedWorld(@WLD@ now)", "  if (data.indexOf(\"exuse\" + i",
                           'F(apg, "public int joinSeen;")', "public static boolean tick(@PAGE@ p, @WLD@ w)", "public void run() {\n  if (this.target == null)")]
assert _o == sorted(_o), "javassist order of the 0.2.3 pieces: %s" % _o
assert s.count("public boolean watchTick(@WLD@ now)") == 2 and s.count("public void answer()") == 2 and s.count("public boolean isOpen()") == 2
assert "void onDismiss(" not in s, "an Exploration page overrides onDismiss - ExGuard's no-ref forget would then run page code"
assert s.count(".setPage(") == OLD.count(".setPage(") and s.count("rebuild();") == OLD.count("rebuild();") + 2, \
    "0.2.3 adds no setPage call and exactly two rebuilds (the heal answers; the ExplorePage tab line only moved)"
# nothing outside the recorded changes moved: undo them (newest first) and get 0.2.2 back, byte for byte
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.2.2 outside the recorded changes"
compile(s, dst, "exec")
out = s.replace(LF, NL) if NL != LF else s
open(dst, "w", encoding="utf8", newline="").write(out)
print("wrote", os.path.relpath(dst, ROOT), "(%d lines; 0.2.2 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
