"""Derive SkyyHud/build_skyyhud_0.3.19.py from the generated 0.3.18 (the SET pin; 0.3.18 is left untouched; line endings preserved).
Run:  python tools/hud_0_3_19_patch.py   then   python SkyyHud/build_skyyhud_0.3.19.py   (never --deploy)
Harness: python SkyyHud/test_skyyhud_0.3.19.py [--dir <scratch>] [--keep]

0.3.19 = LAG FIXES ONLY (Skyy 2026-10-13: "During/ before we consolidate the mods together, lets audit the code structure, and make sure they
are working together in the smoothest easiest lag free way possible" + "work through your whole list, so everything is ready to play when
i get off work."; research/Code-Structure-Audit.md findings 4 + 8). No behaviour change for players, no setting, no saved-data change.
  5. OWN THREAD: the 1 s HUD tick (TickTask), the layout file writes and the attach delay run on SkyyHud's own single daemon thread
     "SkyyHud-Tick" (HudThreads.EXEC, a ScheduledThreadPool of one) - no longer on HytaleServer.SCHEDULED_EXECUTOR, the engine's ONE
     scheduler thread every mod and the engine share. A HUD with no shown widget does nothing in the tick (HudMain.tick returns at once).
     (Tried and left out: a hidden Abilities widget asking class:fn:abil only on a class:<uuid> change - a class that GAINS abilities
     without a class change (a SkyyClasses setting) would show up to 10 s late; the 0.3.18 harness W7 caught it. It stays once a second,
     now on SkyyHud's own thread.)
  6. WORLD TIME OFF THE WORLD THREAD (finding 4): Game Clock / Day Counter read the world's WorldTimeResource only ON the world thread:
     WTime.get(world) reads it directly when the caller IS that world's thread (attach, editor / Settings pages) and otherwise returns the
     value of the last world-thread read; the HUD tick queues ONE small world task per world per second (only for worlds where somebody
     shows a clock / day widget; never two at once per world). The shown text is the same ("HH:MM", "Day N"; "--:--" until known).
     Fix round: a queued read older than 5 s (its world stopped before running it) no longer blocks the next one.
  7. COMBAT / ABILITY VALUES: skill:fn:combat is CONFIRMED a pure map read (SkyySkills 0.4.31 CombatFn.apply -> ManaRegen.combatNow = one
     ConcurrentHashMap get + arithmetic, "any thread"); it stays. class:fn:abil is NOT a pure map read (SkyyClasses 0.1.19 AbilFn.apply:
     ClassStore.classIndex may load a player file once, AbilStore.load reads a cached file, Abil.level calls skill:fn:level) and SkyyClasses
     publishes no plain ability values - it is now called only from SkyyHud's own thread (item 5), never from the engine's shared
     scheduler. A plain bridge value needs a SkyyClasses change (reported, not this mod's).
  8. Zone / Party "Hub": hubWorld() reads the bridge key island:hubWorld (a String world name) when SkyyIslands publishes it; until then
     the hub.properties file is re-read at most every 15 s ONLY on SkyyHud's thread (HudThreads tick) and every other caller (world thread,
     pages) reads the cached volatile value - no file read and no class lock on a world thread any more. LayoutStore.save serialises on the
     caller's thread and writes (tmp + fsync + move) on SkyyHud's thread, in order (no executor = the old inline write).
     MINIMAP queue bounds: per player 20,000 packets (unchanged - fix round 2: 5,000 was undone, a packet past the bound is dropped for
     good) and 1,024 map pieces (was 2,048), plus GLOBAL bounds over all players:
     50,000 packets and 4,096 pieces (~45 MB of pictures at most; was 2,048 x every player); past a bound the same as before (a piece is
     queued as its chunk keys only - the engine cache serves it later - a packet is dropped and counted). The global counters are
     re-summed from the sessions once a second (no drift).
ROLLBACK: 0.3.19 -> 0.3.18 is safe (nothing saved differently).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyHud", "build_skyyhud_0.3.18.py")
dst = os.path.join(ROOT, "SkyyHud", "build_skyyhud_0.3.19.py")
raw = open(src, encoding="utf8", newline="").read()
CR = chr(13)
LF = chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.3.18"' in s and s.startswith('"""SkyyHud 0.3.18 - build script')
CHANGES = []


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:160])
    s = s.replace(old, new, 1)
    CHANGES.append((new, old))


def before(anchor, text):
    rep(anchor, text + anchor)


# ---------------- docstring + version ----------------
rep('''"""SkyyHud 0.3.18 - build script (javassist via jpype).
Run:   python build_skyyhud_0.3.18.py            -> SkyyHud/SkyyHud-0.3.18.jar
       (deploys only through tools/deploy_set.py - never pass --deploy here)
''', '''"""SkyyHud 0.3.19 - build script (javassist via jpype).
Run:   python build_skyyhud_0.3.19.py            -> SkyyHud/SkyyHud-0.3.19.jar
       (deploys only through tools/deploy_set.py - never pass --deploy here)
0.3.19 (generated by tools/hud_0_3_19_patch.py from 0.3.18): LAG FIXES ONLY (Skyy 2026-10-13 "lets audit the code structure ... lag free";
  research/Code-Structure-Audit.md findings 4 + 8; details in tools/hud_0_3_19_patch.py): the 1 s tick, layout writes and the attach
  delay on SkyyHud's own thread (not the engine's shared scheduler); Game Clock / Day read the world time only on the world thread (one
  world task per world per second, cached); hubWorld from the bridge key island:hubWorld (the hub.properties fallback read only on SkyyHud's thread); a smaller per-player map-piece bound + new
  global minimap queue bounds. No behaviour change, no setting, no data change.
''')
rep('VERSION = "0.3.18"\n', 'VERSION = "0.3.19"\n')

# ---------------- the two new classes ----------------
rep('''tick = pool.makeClass(PKG + ".TickTask")''', '''tick = pool.makeClass(PKG + ".TickTask")
hthr = pool.makeClass(PKG + ".HudThreads")                # 0.3.19: SkyyHud's own thread (tick, layout writes, attach delay)
wtime = pool.makeClass(PKG + ".WTime")                    # 0.3.19: world time read on the world thread, cached per world''')
rep('''       dslink, dsstate, dscheck, dsui)
for c in ALL:''', '''       dslink, dsstate, dscheck, dsui, hthr, wtime)
for c in ALL:''')

# ---------------- 6 WTime (before Widgets: Widgets.text calls it) ----------------
before('''# ================= Widgets =================''', '''# ================= 0.3.19 WTime: the world's game time, read ONLY on that world's thread =================
# T: world name -> String[] { "HH:MM", "Day N" } of the last world-thread read; Q: world name -> Long (when) while a read task is queued
# (never two). Fix round: a task queued in a world's last tick before it stopped never runs, so a Q entry older than Q_STALE_MS no longer
# blocks (a world re-created under the same name gets its clock back within a few seconds instead of '--:--' until a restart).
# get(w): on w's own thread = read now (and keep it); anywhere else = the kept value (null = not known yet -> "--:--").
wtime.addInterface(pool.get("java.lang.Runnable"))
wtime.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap T = new java.util.concurrent.ConcurrentHashMap();", wtime))
wtime.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap Q = new java.util.concurrent.ConcurrentHashMap();", wtime))
wtime.addField(CtField.make("public static final java.util.concurrent.atomic.AtomicLong HOPS = new java.util.concurrent.atomic.AtomicLong();", wtime))
wtime.addField(CtField.make("public static final long Q_STALE_MS = 5000L;", wtime))
wtime.addField(CtField.make(f"public {WLD} w;", wtime))
wtime.addConstructor(CtNewConstructor.make(f"public WTime({WLD} w) {{ this.w = w; }}", wtime))
wtime.addMethod(CtNewMethod.make(f"""
public static String[] read({WLD} w) {{
  {ST} st = w.getEntityStore().getStore();
  {WTR} tr = ({WTR}) st.getResource({WTR}.getResourceType());
  if (tr == null) return null;
  long days = java.time.temporal.ChronoUnit.DAYS.between({WTR}.ZERO_YEAR, tr.getGameTime()) + 1L;
  java.time.LocalDateTime dt = tr.getGameDateTime();
  int hh = dt.getHour(); int mm = dt.getMinute();
  return new String[] {{ (hh < 10 ? "0" : "") + hh + ":" + (mm < 10 ? "0" : "") + mm, "Day " + days }};
}}""", wtime))
wtime.addMethod(CtNewMethod.make(f"""
public static String[] get({WLD} w) {{
  if (w == null) return null;
  String k = w.getName();
  if (k == null) return null;
  try {{
    if (w.isInThread()) {{
      String[] v = read(w);
      if (v != null) T.put(k, v); else T.remove(k);
      return v;
    }}
  }} catch (Throwable t) {{ }}
  return (String[]) T.get(k);
}}""", wtime))
wtime.addMethod(CtNewMethod.make(f"""
public static void want({WLD} w) {{
  if (w == null) return;
  String k = w.getName();
  if (k == null) return;
  long now = System.currentTimeMillis();
  Long nv = Long.valueOf(now);
  Object o = Q.putIfAbsent(k, nv);
  if (o != null) {{
    if (o instanceof Long && now >= ((Long) o).longValue() && now - ((Long) o).longValue() < Q_STALE_MS) return;
    if (!Q.replace(k, o, nv)) return;       // fix round: a stale entry (its task never ran) no longer blocks
  }}
  try {{ w.execute(new {PKG}.WTime(w)); HOPS.incrementAndGet(); }} catch (Throwable t) {{ Q.remove(k, nv); }}
}}""", wtime))
wtime.addMethod(CtNewMethod.make("""
public void run() {
  String k = null;
  try {
    k = this.w.getName();
    String[] v = read(this.w);
    if (k != null) { if (v != null) T.put(k, v); else T.remove(k); }
  } catch (Throwable t) { }
  if (k != null) Q.remove(k);
}""", wtime))

''')
rep('''    if (id.equals("Gclock") || id.equals("Day")) {{
      java.util.UUID wu = pr.getWorldUuid();
      if (wu == null) return "--:--";
      {WLD} w = {UNI}.get().getWorld(wu);
      if (w == null) return "--:--";
      {ST} st = w.getEntityStore().getStore();
      {WTR} tr = ({WTR}) st.getResource({WTR}.getResourceType());
      if (tr == null) return "--:--";
      if (id.equals("Day")) {{
        long days = java.time.temporal.ChronoUnit.DAYS.between({WTR}.ZERO_YEAR, tr.getGameTime()) + 1L;
        return "Day " + days;
      }}
      java.time.LocalDateTime dt = tr.getGameDateTime();
      int hh = dt.getHour(); int mm = dt.getMinute();
      return (hh < 10 ? "0" : "") + hh + ":" + (mm < 10 ? "0" : "") + mm;
    }}''', '''    if (id.equals("Gclock") || id.equals("Day")) {{
      java.util.UUID wu = pr.getWorldUuid();
      if (wu == null) return "--:--";
      {WLD} w = {UNI}.get().getWorld(wu);
      if (w == null) return "--:--";
      // 0.3.19: the world time is read only on the world thread (WTime: now when this IS that thread, else the last world-thread read)
      String[] tv = {PKG}.WTime.get(w);
      if (tv == null) return "--:--";
      return id.equals("Day") ? tv[1] : tv[0];
    }}''')

# ---------------- 8 hubWorld: the bridge key first; the file only on SkyyHud's thread ----------------
rep('''wid.addField(CtField.make("public static String HUBW;", wid))
wid.addField(CtField.make("public static long HUBAT;", wid))''', '''wid.addField(CtField.make("public static volatile String HUBW;", wid))       # 0.3.19: volatile (read lock-free, written by hubRefresh)
wid.addField(CtField.make("public static volatile long HUBAT;", wid))''')
rep('''# static synchronized: the 1 s HUD tick (scheduler thread) and page builds (SettingsPage.previewText) call this concurrently;
# the Widgets.class monitor makes HUBW/HUBAT visible across threads and stops a caller from seeing HUBAT already refreshed while
# HUBW is still the old value. It only reads one small file and takes no other lock (lock order HudMain -> Widgets.class only).
wid.addMethod(CtNewMethod.make("""
public static synchronized String hubWorld() {
  long now = System.currentTimeMillis();
  if (HUBAT != 0L && now - HUBAT < 15000L) return HUBW;
  HUBAT = now;
  String w = null;''', '''# 0.3.19: hubRefresh = the hub.properties read, ONLY on SkyyHud's own thread (TickTask, at most every 15 s; HUBW / HUBAT volatile)
wid.addMethod(CtNewMethod.make("""
public static void hubRefresh() {
  long now = System.currentTimeMillis();
  if (HUBAT != 0L && now - HUBAT < 15000L) return;
  HUBAT = now;
  String w = null;''')
rep('''  } catch (Throwable t) { w = HUBW; }
  HUBW = w;
  return w;
}""", wid))''', '''  } catch (Throwable t) { w = HUBW; }
  HUBW = w;
}""", wid))
# 0.3.19: the hub world = SkyyIslands' bridge key island:hubWorld (a String world name) when it is published, else the last file read
# (hubRefresh) - any thread, no lock, no file read
wid.addMethod(CtNewMethod.make("""
public static String hubWorld() {
  try {
    java.util.Map b = bridge();
    Object o = b == null ? null : b.get("island:hubWorld");
    if (o instanceof String && ((String) o).trim().length() > 0) return ((String) o).trim();
  } catch (Throwable t) { }
  return HUBW;
}""", wid))''')

# ---------------- 8 LayoutStore.save writes on SkyyHud's thread; 5 HudThreads ----------------
before('''lst.addMethod(CtNewMethod.make(f"""
public static void save(java.util.UUID u) {{''', '''# ================= 0.3.19 HudThreads: SkyyHud's own single daemon thread "SkyyHud-Tick" =================
# EXEC = a ScheduledThreadPoolExecutor of one thread (the 1 s tick, layout writes, the attach delay - never HytaleServer.SCHEDULED_EXECUTOR,
# the engine's one shared scheduler thread). An instance is the ThreadFactory (no path) or one layout write (path + bytes).
hthr.addInterface(pool.get("java.util.concurrent.ThreadFactory"))
hthr.addInterface(pool.get("java.lang.Runnable"))
hthr.addField(CtField.make("public static volatile java.util.concurrent.ScheduledExecutorService EXEC;", hthr))
hthr.addField(CtField.make("public static final java.util.concurrent.atomic.AtomicLong WRITES = new java.util.concurrent.atomic.AtomicLong();", hthr))
hthr.addField(CtField.make("public java.nio.file.Path path;", hthr))
hthr.addField(CtField.make("public byte[] data;", hthr))
hthr.addConstructor(CtNewConstructor.make("public HudThreads() { this.path = null; this.data = null; }", hthr))
hthr.addConstructor(CtNewConstructor.make("public HudThreads(java.nio.file.Path p, byte[] d) { this.path = p; this.data = d; }", hthr))
hthr.addMethod(CtNewMethod.make("""
public Thread newThread(Runnable r) {
  Thread t = new Thread(r, "SkyyHud-Tick");
  t.setDaemon(true);
  return t;
}""", hthr))
hthr.addMethod(CtNewMethod.make(f"""
public void run() {{
  if (this.path == null) return;
  try {{ {PKG}.LayoutStore.atomicWrite(this.path, this.data); WRITES.incrementAndGet(); }}
  catch (Throwable t) {{ {PKG}.LayoutStore.debug("layout save failed for " + this.path.getFileName() + " (the change is live but not saved): " + t); }}
}}""", hthr))
hthr.addMethod(CtNewMethod.make("""
public static synchronized java.util.concurrent.ScheduledExecutorService start() {
  java.util.concurrent.ScheduledExecutorService e = EXEC;
  if (e != null && !e.isShutdown()) return e;
  e = java.util.concurrent.Executors.newSingleThreadScheduledExecutor(new com.skyy.hud.HudThreads());
  EXEC = e;
  return e;
}""", hthr))
# a layout write on SkyyHud's thread, in order; false = no thread (bare JVM / stopped) - the caller writes inline as before
hthr.addMethod(CtNewMethod.make("""
public static boolean write(java.nio.file.Path p, byte[] d) {
  java.util.concurrent.ScheduledExecutorService e = EXEC;
  if (e == null || e.isShutdown()) return false;
  try { e.execute(new com.skyy.hud.HudThreads(p, d)); return true; } catch (Throwable t) { return false; }
}""", hthr))
hthr.addMethod(CtNewMethod.make(f"""
public static void later(Runnable r, long ms) {{
  java.util.concurrent.ScheduledExecutorService e = EXEC;
  if (e != null && !e.isShutdown()) {{
    try {{ e.schedule(r, ms, java.util.concurrent.TimeUnit.MILLISECONDS); return; }} catch (Throwable t) {{ }}
  }}
  {HSV}.SCHEDULED_EXECUTOR.schedule(r, ms, java.util.concurrent.TimeUnit.MILLISECONDS);
}}""", hthr))
# shutdown: no new work; the queued layout writes finish (at most 3 s)
hthr.addMethod(CtNewMethod.make("""
public static void stop() {
  java.util.concurrent.ScheduledExecutorService e = EXEC;
  if (e == null) return;
  try { e.shutdown(); e.awaitTermination(3L, java.util.concurrent.TimeUnit.SECONDS); } catch (Throwable t) { }
}""", hthr))
''')
rep('''    java.io.ByteArrayOutputStream bo = new java.io.ByteArrayOutputStream();
    p.store(bo, "SkyyHud layout");
    atomicWrite(DIR.resolve(u.toString() + ".properties"), bo.toByteArray());''', '''    java.io.ByteArrayOutputStream bo = new java.io.ByteArrayOutputStream();
    p.store(bo, "SkyyHud layout");
    // 0.3.19: serialised here, written (tmp + fsync + move) on SkyyHud's thread in order; no thread = written here as before
    java.nio.file.Path lf = DIR.resolve(u.toString() + ".properties");
    byte[] ld = bo.toByteArray();
    if (!{PKG}.HudThreads.write(lf, ld)) atomicWrite(lf, ld);''')

# ---------------- 5 the tick: nothing shown = nothing to do; the world-time reads; the hub file; the minimap bounds ----------------
rep('''public synchronized void tick() {{
  try {{
    {UCB} b = new {UCB}();''', '''public synchronized void tick() {{
  try {{
    if (this.built.isEmpty() && this.shape.isEmpty() && this.confirmAt == 0L) return;     // 0.3.19: no widget shown = nothing to update
    {UCB} b = new {UCB}();''')
rep('''hudc.addMethod(CtNewMethod.make("""
public synchronized void rebuild() {''', '''# 0.3.19: does this HUD show the Game Clock or the Day Counter (the tick asks WTime for this world)?
hudc.addMethod(CtNewMethod.make("""
public synchronized boolean wantsTime() {
  return this.built.containsKey("Gclock") || this.built.containsKey("Day");
}""", hudc))
hudc.addMethod(CtNewMethod.make("""
public synchronized void rebuild() {''')
rep('''    if (pr == null || !pr.isValid()) {{ it.remove(); {PKG}.LayoutStore.CACHE.remove(e.getKey()); {PKG}.EditorPage.STEPS.remove(e.getKey()); continue; }}
    h.tick();''', '''    if (pr == null || !pr.isValid()) {{ it.remove(); {PKG}.LayoutStore.CACHE.remove(e.getKey()); {PKG}.EditorPage.STEPS.remove(e.getKey()); continue; }}
    // 0.3.19: one world-thread read of the game time per world per second, only where a clock / day widget is shown
    if (h.wantsTime()) {{
      try {{ java.util.UUID wu = pr.getWorldUuid(); if (wu != null) {PKG}.WTime.want({UNI}.get().getWorld(wu)); }} catch (Throwable tw) {{ }}
    }}
    h.tick();''')
rep('''public void run() {
  try { plugin.tickAll(); } catch (Throwable t) { }
  try { com.skyy.hud.Minimap.watchdog(); } catch (Throwable t) { }''', '''public void run() {
  try { com.skyy.hud.Widgets.hubRefresh(); } catch (Throwable t) { }      // 0.3.19: the hub file only on this thread
  try { plugin.tickAll(); } catch (Throwable t) { }
  try { com.skyy.hud.Minimap.resync(); } catch (Throwable t) { }          // 0.3.19: the global minimap queue counters
  try { com.skyy.hud.Minimap.watchdog(); } catch (Throwable t) { }''')
rep('''public void later(long ms) {{
  this.onWorld = false;
  {HSV}.SCHEDULED_EXECUTOR.schedule(this, ms, java.util.concurrent.TimeUnit.MILLISECONDS);
}}""", att))''', '''public void later(long ms) {{
  this.onWorld = false;
  {PKG}.HudThreads.later(this, ms);      // 0.3.19: SkyyHud's own thread (the engine's scheduler when it is not running)
}}""", att))''')
rep('''  this.ticker = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.TickTask(this), 1L, 1L, java.util.concurrent.TimeUnit.SECONDS);''',
    '''  this.ticker = {PKG}.HudThreads.start().scheduleAtFixedRate(new {PKG}.TickTask(this), 1L, 1L, java.util.concurrent.TimeUnit.SECONDS);   // 0.3.19: own thread''')
rep('''  try {{ if (this.ticker != null) this.ticker.cancel(false); }} catch (Throwable t) {{ }}
  try {{ {PKG}.Minimap.shutdown(); }} catch (Throwable t) {{ }}''', '''  try {{ if (this.ticker != null) this.ticker.cancel(false); }} catch (Throwable t) {{ }}
  try {{ {PKG}.HudThreads.stop(); }} catch (Throwable t) {{ }}      // 0.3.19: the queued layout writes finish (at most 3 s)
  try {{ {PKG}.Minimap.shutdown(); }} catch (Throwable t) {{ }}''')

# ---------------- 8 the minimap queue bounds ----------------
rep('''MM_QMAX = 20000                   # packets queued per player between two drains (the probe's bound)
MM_QCHUNKS = 2048                 # map pieces (images) queued per player; past it a packet is queued as its chunk KEYS only (fix round:''',
    '''MM_QMAX = 20000                   # packets queued per player between two drains (the probe's bound; fix round 2: kept - a dropped packet is never re-sent)
MM_GQMAX = 50000                  # 0.3.19: packets queued over ALL players
MM_GQCHUNKS = 4096                # 0.3.19: map pieces queued over ALL players (~45 MB of pictures at most)
MM_QCHUNKS = 1024                 # map pieces (images) queued per player (0.3.19: was 2,048); past it a packet is queued as its chunk KEYS only (fix round:''')
rep('''"QMAX": str(MM_QMAX), "QTICK": str(MM_TICK_MS),''', '''"QMAX": str(MM_QMAX), "GQMAX": str(MM_GQMAX), "GQCHUNKS": str(MM_GQCHUNKS), "QTICK": str(MM_TICK_MS),''')
rep('''for _f in ("public static volatile java.util.concurrent.ScheduledExecutorService EXEC;",
           "public static volatile java.util.concurrent.ScheduledFuture FUT;",''', '''for _f in ("public static volatile java.util.concurrent.ScheduledExecutorService EXEC;",
           # 0.3.19: the queue over all players (packets / map pieces), re-summed from the sessions once a second (resync)
           "public static final java.util.concurrent.atomic.AtomicInteger GQN = new java.util.concurrent.atomic.AtomicInteger();",
           "public static final java.util.concurrent.atomic.AtomicInteger GQC = new java.util.concurrent.atomic.AtomicInteger();",
           "public static volatile java.util.concurrent.ScheduledFuture FUT;",''')
rep('''    s.qn.decrementAndGet();
    n = n + 1;''', '''    s.qn.decrementAndGet();
    GQN.decrementAndGet();
    n = n + 1;''')
rep('''      if (cs != null) {
        s.qc.addAndGet(-cs.length);''', '''      if (cs != null) {
        s.qc.addAndGet(-cs.length);
        GQC.addAndGet(-cs.length);''')
rep('''  s.q.clear();
  s.qn.set(0);
  s.qc.set(0);''', '''  s.q.clear();
  GQN.addAndGet(-s.qn.getAndSet(0));
  GQC.addAndGet(-s.qc.getAndSet(0));''')
rep('''  if (s.qn.incrementAndGet() > @QMAX@) { s.qn.decrementAndGet(); s.dropped.incrementAndGet(); return; }
  if (up) {
    @UWM@ u = (@UWM@) p;
    @MCH@[] cs = u.chunks;
    int n = cs == null ? 0 : cs.length;
    if (n > 0 && s.qc.addAndGet(n) > @QCHUNKS@) {
      s.qc.addAndGet(-n);''', '''  int qa = s.qn.incrementAndGet();
  int qg = GQN.incrementAndGet();
  if (qa > @QMAX@ || qg > @GQMAX@) { s.qn.decrementAndGet(); GQN.decrementAndGet(); s.dropped.incrementAndGet(); return; }
  if (up) {
    @UWM@ u = (@UWM@) p;
    @MCH@[] cs = u.chunks;
    int n = cs == null ? 0 : cs.length;
    boolean over = false;
    if (n > 0) {
      int ca = s.qc.addAndGet(n);
      int cg = GQC.addAndGet(n);
      over = ca > @QCHUNKS@ || cg > @GQCHUNKS@;
    }
    if (over) {
      s.qc.addAndGet(-n);
      GQC.addAndGet(-n);''')
rep('''        if (s.qn.incrementAndGet() > @QMAX@) { s.qn.decrementAndGet(); s.dropped.incrementAndGet(); return; }
        s.q.add(new @UWM@((@MCH@[]) null, u.addedMarkers, u.removedMarkers));''', '''        int ma = s.qn.incrementAndGet();
        int mg = GQN.incrementAndGet();
        if (ma > @QMAX@ || mg > @GQMAX@) { s.qn.decrementAndGet(); GQN.decrementAndGet(); s.dropped.incrementAndGet(); return; }
        s.q.add(new @UWM@((@MCH@[]) null, u.addedMarkers, u.removedMarkers));''')
before('''MMM(mmmain, r"""
public static synchronized void watchdog() {''', '''# 0.3.19: the global counters = the sum over the live sessions (SkyyHud's thread, once a second: a counter a racing tap / drop moved is
# put right within a second)
MMM(mmmain, r"""
public static void resync() {
  int a = 0;
  int c = 0;
  java.util.Iterator it = SESS.values().iterator();
  while (it.hasNext()) {
    @PKG@.MmSess s = (@PKG@.MmSess) it.next();
    if (s == null) continue;
    a = a + s.qn.get();
    c = c + s.qc.get();
  }
  GQN.set(a);
  GQC.set(c);
}""")
''')

# ---------------- self-checks ----------------
assert "SCHEDULED_EXECUTOR.scheduleAtFixedRate" not in s
assert s.count("st.getResource({WTR}.getResourceType())") == 1, "the world store is read only in WTime.read"
assert "public static synchronized String hubWorld()" not in s
assert "KEEP=10" in s and "KEEP=20" not in s
for a_, b_ in (("public static String[] get({WLD} w)", "public static String text(String id, {PR} pr, long joinMs)"),
               ("public static void hubRefresh()", "public static String hubWorld()"),
               ("public static String hubWorld()", "public static String zoneText("), ("public static boolean write(java.nio.file.Path p", "public static void save(java.util.UUID u)"),
               ("public static void atomicWrite(", "if (this.path == null) return;"),
               ("public static void later(Runnable r, long ms)", "public void later(long ms) {{"), ("public synchronized boolean wantsTime()", "public void tickAll()"),
               ("public static void resync()", "try { com.skyy.hud.Minimap.resync(); }")):
    assert s.index(a_) < s.index(b_), "javassist order: %s before %s" % (a_, b_)
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.3.18 outside the recorded changes"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", os.path.relpath(dst, ROOT), "(%d lines, %d changes)" % (s.count(LF), len(CHANGES)))
