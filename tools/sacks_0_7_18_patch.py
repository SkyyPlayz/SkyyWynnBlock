"""Derive SkyySacks/build_skyysacks_0.7.18.py from the SET pin 0.7.17 (the GENERATED build_skyysacks_0.7.17.py; edit THIS file, then
regenerate: python tools/sacks_0_7_18_patch.py; never re-run sacks_0_7_17_patch.py on top of it).
Run:  python tools/sacks_0_7_18_patch.py   then   python SkyySacks/build_skyysacks_0.7.18.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.7.18.py

0.7.18 = LAG + DATA-SAFETY FIXES from the code audit (research/Code-Structure-Audit.md findings 9b, 9c, 9e + "Data-safety fixes found";
Skyy 2026-10-13: "lets audit the code structure, and make sure they are working together in the smoothest easiest lag free way possible").
No behaviour change for players (what moves where and when a player can see it is 0.7.17's); saved files and bridge keys unchanged.

1. NO WORLD HOPS FOR IDLE PLAYERS (9b). The three timers queued a world-thread task for EVERY online player: SackTick (2 s sweep),
   CraftTick (300 ms bench link), ProcTick (1 s Furnace / Tannery) = ~4.8 hops a second per player even standing still. Now each timer
   decides on its own (scheduler) thread whether a player has anything to do and only then hops:
   - SWEEP (SackTick -> SweepTask): a player is swept when their inventory changed since the last sweep (SackInvSys = an ECS
     EntityEventSystem on the engine's InventoryChangeEvent - fired by InventorySystems for every container change: pickups, use,
     placing, crafting, moves - marks SweepTask.INVDIRTY), or when SweepTask.sigOf(u) changed: profile:epoch / profile:busy, coll:epoch +
     coll:recipes (bag recipe knowledge), requip:pocket / pocketN (Requip's reserved hotbar slots), the player's refill mode, the pool's
     change counter of their key (another mod / page / bench took or put), and the owner's settings (free recipes, refill switches, cooked
     food, the five bag caps). First sight (join, after a quit) always sweeps. A sweep that finds no settled key (profile settling / busy /
     unreadable pool) keeps the player dirty, so it is retried every 2 s exactly like before. If the event system cannot be registered
     (SweepTask.EVENTS_OK false) every player is swept as in 0.7.17.
     FIXER (review): a HEARTBEAT - a player not swept for SweepTask.HEARTBEAT_MS (20 s) is swept anyway (LASTSWEEP, BEATS counts them;
     ~0.05 hops / s per idle player instead of 0.5), so a container change the event misses only delays the sweep (<= 20 s), never
     stops it.
     DECISION: an admin's vanilla "/recipe learn" of a bag recipe is undone on the player's next inventory change or at the latest by
     the 20 s heartbeat (0.7.17: within 2 s; KnowSync.sync only runs in the sweep); every other sweep effect is driven by a trigger above.
   - BENCH LINK (CraftTick -> CraftLinkTask): only players with a crafting window: BenchLink.ACTIVE is set by the existing
     CraftPacketFilter for every OpenWindow / UpdateWindow sent to the player, by CraftInFilter on a craft click and when a window record
     is created (recOf); a player with link records or a live bag mirror is linked too. After a link pass that finds no bench / pocket
     window, no record and no mirror, the flag is cleared (remove(u, stamp) - a newer flag survives). No outbound filter (OUT == null) =
     every player as before. pocketCheck (the bags.pocketCraft backstop) also runs once per CraftTick on the scheduler.
   - FURNACE / TANNERY (ProcTick -> ProcTask): only players with a queued unit (ProcBench.queued() > 0) or unpaid Smithing XP (xpList),
     an open SacksPage / CraftPage (ProcTask.PAGEOPEN: set in their build(), cleared by ProcTask when no such page is open), a changed
     profile:epoch, or not seen yet (LASTK: first sight loads the benches = offline progress). An empty queue only moved its clock
     (addJob resets the clock when the queue is empty), so skipping it changes nothing.
   One caps() and one carried() scan per sweep (were up to 5 + 4): SweepTask.run computes caps once and passes it on; items() takes
   carried() once (before), derives the after-sweep counts from what the sweep removed (sweep reports every removal) and the SEENQ
   snapshot from what the refill / Requip top-up added (both report every gain); any exception in those steps falls back to a real scan.
2. THE PRIVATE POOL WRITER (9c). SackPool.saveSoon wrote the whole SackSaver run (every dirty pool, processing, logs, config reload) on
   the engine's ONE shared scheduler thread for every call (up to ~16 / s while crafting). Now: SackPool.WRITER = a private
   single-thread daemon ScheduledExecutorService (SackThreads, "SkyySacks-writer"; the SkyyVault VStore.SAVER pattern); saveSoon(k)
   marks k dirty and schedules ONE PoolSaveJob(k) (PENDING.putIfAbsent - every call while it is pending rides on it). FIXER (review):
   LEADING EDGE - the first save of a key after a quiet second runs AT ONCE (0.7.17's timing for a single bag page click, a bridge
   take / put by SkyyBazaar / SkyyGear / SkyyFishing, a craft pay - so another mod's payout and the pool file are never 1 s apart);
   only a save within DEBOUNCE_MS (1 s) of the previous one waits for the rest of that second (LASTSAVE = when the key's last job ran
   / runs). At most one write per key per second, plus the first.
   the job saves only that key, only when still dirty (DIRTY.remove first, so a change during the write re-arms a new job; a failed
   write stays dirty for the next job / the 10 s SackSaver). saveSoon(null) (a refill choice) runs the SackSaver on the writer at once.
   The 10 s SackSaver and every other "run the SackSaver now" (CraftPage.saveSoon for the Furnace / Tannery, ProcTask's profile switch)
   run on the writer too (runOnWriter; no writer = the shared scheduler, refused = inline - 0.7.17's fallbacks). KeptQuit (a player
   leaving) saves that key at once on the writer (saveAsap). shutdown: the writer stops (pending saves finish, 3 s max), then every
   dirty file is flushed inline as before.
3. THE CRASH WINDOW (data safety). A stack refill / Requip top-up moved items from the pool into the inventory and the pool file
   followed at the next 10 s save. Now a tick whose refill / top-up moved something (or failed half way) calls saveSoon(k): the pool
   file follows at once (leading edge) or within 1 s. The pool file is still written tmp + fsync + atomic move (a crash leaves the old
   or the new file, never half of one).
   FIXER (review): the player's inventory is saved by the ENGINE on its own 10 s player-save tick (tools/PROFILES-CONTRACT.md), so an
   early pool save cannot close the window - it only picks which way a hard crash goes. The SAFE direction per move (never a dupe):
   pool -> inventory (refill, top-up, page withdraw, bridge take): the pool's decrease is on disk first, so a crash before the engine's
   player save can only lose the moved items, never keep them twice. inventory -> pool (the sweep): NO early save - a tick whose sweep
   moved anything leaves the key dirty for the 10 s SackSaver exactly like 0.7.17 (an early pool save before the engine's inventory save
   would make a crash keep the items in both places). FIXER 2 (review): the pool file is written WHOLE, so an early save would also
   carry any sweep addition not on disk yet (the same tick's, or an earlier tick's). A refill / top-up tick now saves early only when
   (a) its own sweep moved, per item, no more than the refill / top-up moved back out (SweepTask.covered: net pool change <= 0 for
   every item), (b) no earlier unsaved sweep is pending (SackPool.SWEPTQ: set by a sweep that was not offset, cleared by saveNow
   right before its snapshot, put back when the write fails) and (c) the save runs at once (SackPool.quiet: no job pending, none in the
   last DEBOUNCE_MS - so no new sweep can join a waiting job). Otherwise the key just stays dirty (0.7.17's timing). A refill tick
   that also swept other items, or one right after a sweep, therefore behaves like 0.7.17.
   Other early saves (a bag page click, a bridge take / put, craft pay - all 0.7.17 behaviour) write the whole pool too and can carry a
   recent sweep's additions as in 0.7.17; since 0.7.18 a burst of them may wait up to 1 s (the debounce), so its trailing write can
   also carry a sweep from that second (UNVERIFIED: needs a sweep and a page / bridge save of the same player within 1 s + a crash).
   LIMIT (UNVERIFIED by design): two files can never be one atomic write; a hard crash can still lose up to ~10 s of refills, repeat a
   refill that fell back to 0.7.17's timing, or repeat / lose up to ~10 s of sweeps (the engine's player-save tick), as in 0.7.17.
4. KnowSync.collSet (9e): coll:recipes:<uuid> was split into a new HashSet on every sweep and page build. Now KnowSync.collShared(u)
   caches the parsed set per player, keyed by coll:epoch:<uuid> AND the published string (same object = no work; an equal string
   = one compare; anything new = one parse, PARSES counts them). collSet(u) returns a copy (callers may keep it); wanted() reads the
   shared set. Dropped at quit.
Classes added: SackThreads, PoolSaveJob, SackInvSys (+1 registerSystem). Changed: SackPool, SweepTask, SackTick, KnowSync, BenchLink,
CraftPacketFilter, CraftInFilter, CraftLinkTask, CraftTick, ProcTask, ProcTick, CraftPage, SacksPage, KeptQuit, SkyySacksPlugin.
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.7.17.py")
dst = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.7.18.py")
raw = open(src, encoding="utf8", newline="").read()
CR = chr(13)
LF = chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)


def rep(old, new, count=1):
    global s
    assert s.count(old) >= 1, "anchor missing: " + old[:90]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:90])
    s = s.replace(old, new)


assert 'VERSION = "0.7.17"' in s and "public static int pocketFill(" in s and "SackInvSys" not in s, "the source must be the generated 0.7.17 script"
REG0 = s.count("registerCommand(")
SYS0 = s.count("registerSystem(")
GLB0 = s.count("registerGlobal(")
MAKE0 = s.count("pool.makeClass(")
ASSETS0 = s[s.index("# ================= assets ================="):]

# ================= header + version =================
rep('''gear:fn:classShow says is not for your class. Assets, ids, recipes and saved data are 0.7.16's. Details: the patch docstring.
"""''', '''gear:fn:classShow says is not for your class. Assets, ids, recipes and saved data are 0.7.16's. Details: the patch docstring.
0.7.18 (derived from 0.7.17 by tools/sacks_0_7_18_patch.py - edit the patch, not this file; research/Code-Structure-Audit.md 9b / 9c / 9e +
the crash window): idle players cost no world hops (the 2 s sweep runs on an inventory change / a changed trigger only - SackInvSys on the
engine's InventoryChangeEvent; the 300 ms bench link only with a crafting window; the 1 s Furnace / Tannery only with a queue, unpaid XP or
an open page; a 20 s heartbeat); one caps / carried scan per sweep; pool saves on a private writer thread (SkyySacks-writer), at once
after a quiet second, else at most one per key per second, only dirty keys; a refill / Requip top-up saves the pool at once (a sweep keeps
the 10 s save - the never-dupe direction); the parsed coll:recipes set is cached by coll:epoch. No behaviour
change; saved data, bridge keys and assets are 0.7.17's. Details: the patch docstring.
"""''')
rep('VERSION = "0.7.17"', 'VERSION = "0.7.18"')

# ================= engine names + tokens =================
rep('''PR  = "com.hypixel.hytale.server.core.universe.PlayerRef"
''', '''PR  = "com.hypixel.hytale.server.core.universe.PlayerRef"
# 0.7.18: SackInvSys (the inventory-change dirty flag of the 2 s sweep) - the SkyyGear GearInvSys / SkyySkills SmeltSys pattern
EES = "com.hypixel.hytale.component.system.EntityEventSystem"
ICE = "com.hypixel.hytale.server.core.event.events.ecs.InventoryChangeEvent"
ACH = "com.hypixel.hytale.component.ArchetypeChunk"
CBF = "com.hypixel.hytale.component.CommandBuffer"
EVE = "com.hypixel.hytale.component.system.EcsEvent"
QRY = "com.hypixel.hytale.component.query.Query"
''')
rep('''       "UNI": UNI, "WLD": WLD}
def jt(src):''', '''       "UNI": UNI, "WLD": WLD,
       "EES": EES, "ICE": ICE, "ACH": ACH, "CBF": CBF, "EVE": EVE, "QRY": QRY}   # 0.7.18: SackInvSys
def jt(src):''')

# ================= the new classes + the early fields (javassist: fields before their first use) =================
rep('''pl   = pool.makeClass(PKG + ".SkyySacksPlugin", pool.get(JP))
''', '''pl   = pool.makeClass(PKG + ".SkyySacksPlugin", pool.get(JP))
# 0.7.18: SackThreads = the private pool writer's thread factory (daemon "SkyySacks-writer"); PoolSaveJob = one debounced pool save;
# SackInvSys = the InventoryChangeEvent listener that marks a player for the next sweep
sthr = pool.makeClass(PKG + ".SackThreads")
psj = pool.makeClass(PKG + ".PoolSaveJob")
sinv = pool.makeClass(PKG + ".SackInvSys", pool.get(EES))
# 0.7.18 fields used by methods compiled long before their classes' own sections (pages, filters, KnowSync)
swp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap INVDIRTY = new java.util.concurrent.ConcurrentHashMap();", swp))
swp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap SIG = new java.util.concurrent.ConcurrentHashMap();", swp))
swp.addField(CtField.make("public static volatile boolean EVENTS_OK = false;", swp))
# fixer: the heartbeat - LASTSWEEP = u -> System.nanoTime() of the last finished sweep; a player not swept for HEARTBEAT_MS is due anyway
swp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap LASTSWEEP = new java.util.concurrent.ConcurrentHashMap();", swp))
swp.addField(CtField.make("public static volatile long HEARTBEAT_MS = 20000L;", swp))
swp.addField(CtField.make("public static final java.util.concurrent.atomic.AtomicLong BEATS = new java.util.concurrent.atomic.AtomicLong();", swp))
for _f in ("HOPS", "SKIPS", "EVENTS", "EXACT", "RESCANS"):
    swp.addField(CtField.make("public static final java.util.concurrent.atomic.AtomicLong %s = new java.util.concurrent.atomic.AtomicLong();" % _f, swp))
ptk.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap LASTK = new java.util.concurrent.ConcurrentHashMap();", ptk))
ptk.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap PAGEOPEN = new java.util.concurrent.ConcurrentHashMap();", ptk))
for _f in ("PHOPS", "PSKIPS"):
    ptk.addField(CtField.make("public static final java.util.concurrent.atomic.AtomicLong %s = new java.util.concurrent.atomic.AtomicLong();" % _f, ptk))
ksync.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap COLLC = new java.util.concurrent.ConcurrentHashMap();", ksync))
ksync.addField(CtField.make("public static final java.util.concurrent.atomic.AtomicLong PARSES = new java.util.concurrent.atomic.AtomicLong();", ksync))
psj.addInterface(pool.get("java.lang.Runnable"))
psj.addField(CtField.make("public String k;", psj))
psj.addConstructor(CtNewConstructor.make("public PoolSaveJob(String k) { this.k = k; }", psj))
sthr.addInterface(pool.get("java.util.concurrent.ThreadFactory"))
sthr.addConstructor(CtNewConstructor.make("public SackThreads() { }", sthr))
sthr.addMethod(CtNewMethod.make("""
public Thread newThread(Runnable r) {
  Thread t = new Thread(r, "SkyySacks-writer");
  t.setDaemon(true);
  return t;
}""", sthr))
''')

# ================= SackPool: the writer fields, the save counter =================
rep('''sp.addField(CtField.make("public static final Object SAVELOCK = new Object();", sp))
''', '''sp.addField(CtField.make("public static final Object SAVELOCK = new Object();", sp))
# 0.7.18 (audit 9c): the PRIVATE pool writer (one daemon thread, SkyyVault's VStore.SAVER pattern) + the debounce: PENDING = keys with a
# PoolSaveJob scheduled; DEBOUNCE_MS = how long one save gathers changes; SAVES = pool files written, JOBS = PoolSaveJob / writer runs
sp.addField(CtField.make("public static volatile java.util.concurrent.ScheduledExecutorService WRITER;", sp))
sp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap PENDING = new java.util.concurrent.ConcurrentHashMap();", sp))
sp.addField(CtField.make("public static volatile long DEBOUNCE_MS = 1000L;", sp))
sp.addField(CtField.make("public static final java.util.concurrent.atomic.AtomicLong SAVES = new java.util.concurrent.atomic.AtomicLong();", sp))
sp.addField(CtField.make("public static final java.util.concurrent.atomic.AtomicLong JOBS = new java.util.concurrent.atomic.AtomicLong();", sp))
# fixer: LASTSAVE = key -> System.nanoTime() at which its last PoolSaveJob runs (the leading edge: a key quiet for DEBOUNCE_MS saves at once)
sp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap LASTSAVE = new java.util.concurrent.ConcurrentHashMap();", sp))
''')
rep('''    catch (Throwable am) { java.nio.file.Files.move(tmp, dst, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING }); }
  } catch (Throwable t) { DIRTY.put(k, Boolean.TRUE); warn("could not save pool for " + k + " (kept dirty - retried by the next save): " + t); }''',
    '''    catch (Throwable am) { java.nio.file.Files.move(tmp, dst, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING }); }
    SAVES.incrementAndGet();   // 0.7.18: pool files written (the harness counts the debounce)
  } catch (Throwable t) { DIRTY.put(k, Boolean.TRUE); warn("could not save pool for " + k + " (kept dirty - retried by the next save): " + t); }''')

# ================= SackPool: saveSoon on the private writer =================
rep('''# 0.7.2 review fix: pool saves from world-thread code (Sacks page clicks, bench link, instant craft, mirror retire/park) mark the
# key dirty and run the SackSaver on the scheduler thread right away (same pattern as CraftPage.saveSoon for processing); only
# when the scheduler refuses the task (server shutting down) is it run inline.
sp.addMethod(CtNewMethod.make(f"""
public static void saveSoon(String k) {{
  if (k != null) DIRTY.put(k, Boolean.TRUE);
  try {{ {HSV}.SCHEDULED_EXECUTOR.execute(new {PKG}.SackSaver()); }}
  catch (Throwable t) {{ new {PKG}.SackSaver().run(); }}
}}""", sp))''', '''# 0.7.18 (audit 9c) THE PRIVATE POOL WRITER. runOnWriter = run r on SackPool.WRITER (no writer yet / any more = the engine's scheduler,
# refused = inline - the 0.7.17 fallbacks). saveJob = one PoolSaveJob: k == null = a full SackSaver run; else that key only, only while
# dirty (DIRTY.remove before the write: a change during the write re-arms a new job; a failed write puts DIRTY back for the next one).
sp.addMethod(CtNewMethod.make(f"""
public static void runOnWriter(Runnable r) {{
  java.util.concurrent.ScheduledExecutorService ex = WRITER;
  if (ex != null) {{
    try {{ ex.execute(r); return; }} catch (Throwable t) {{ }}
  }}
  try {{ {HSV}.SCHEDULED_EXECUTOR.execute(r); }}
  catch (Throwable t2) {{ r.run(); }}
}}""", sp))
sp.addMethod(CtNewMethod.make(f"""
public static void saveJob(String k) {{
  JOBS.incrementAndGet();
  if (k == null) {{ new {PKG}.SackSaver().run(); return; }}
  PENDING.remove(k);
  if (DIRTY.remove(k) != null) save(k);
}}""", sp))
psj.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{ {PKG}.SackPool.saveJob(this.k); }} catch (Throwable t) {{ {PKG}.SackPool.warn("pool save failed (kept dirty): " + t); }}
}}""", psj))
# 0.7.2 review fix: pool saves from world-thread code (Sacks page clicks, bench link, instant craft, mirror retire/park) mark the key dirty and
# never write on the world thread. 0.7.18: ONE PoolSaveJob per key DEBOUNCE_MS later on the private writer (every call in that second rides
# on it, PENDING.putIfAbsent); saveSoon(null) (a refill choice) = a SackSaver run on the writer at once. No writer (before setup / after
# shutdown) = 0.7.17: the SackSaver on the engine's scheduler, inline when refused.
sp.addMethod(CtNewMethod.make(f"""
public static void saveSoon(String k) {{
  if (k != null) DIRTY.put(k, Boolean.TRUE);
  java.util.concurrent.ScheduledExecutorService ex = WRITER;
  if (ex == null) {{
    try {{ {HSV}.SCHEDULED_EXECUTOR.execute(new {PKG}.SackSaver()); }}
    catch (Throwable t) {{ new {PKG}.SackSaver().run(); }}
    return;
  }}
  if (k == null) {{ runOnWriter(new {PKG}.PoolSaveJob((String) null)); return; }}
  if (PENDING.putIfAbsent(k, Boolean.TRUE) != null) return;
  // fixer (review): LEADING EDGE - quiet for DEBOUNCE_MS = save at once; else the rest of that second (one write per key per second)
  long now = System.nanoTime();
  Long last = (Long) LASTSAVE.get(k);
  long gap = DEBOUNCE_MS * 1000000L;
  long delay = 0L;
  if (last != null && now - last.longValue() < gap) delay = (gap - (now - last.longValue())) / 1000000L + 1L;
  LASTSAVE.put(k, Long.valueOf(now + delay * 1000000L));
  try {{ ex.schedule(new {PKG}.PoolSaveJob(k), delay, java.util.concurrent.TimeUnit.MILLISECONDS); }}
  catch (Throwable t) {{ PENDING.remove(k); new {PKG}.SackSaver().run(); }}
}}""", sp))
# 0.7.18: a key saved at once on the writer (a player leaving - the engine saves their inventory now too)
sp.addMethod(CtNewMethod.make(f"""
public static void saveAsap(String k) {{
  if (k == null) return;
  DIRTY.put(k, Boolean.TRUE);
  runOnWriter(new {PKG}.PoolSaveJob(k));
}}""", sp))''')
# CraftPage.saveSoon (Furnace / Tannery) and ProcTask's profile switch: the SackSaver on the writer
rep('''public static void saveSoon(String k) {{
  {PKG}.ProcStore.markDirty(k);
  try {{ {HSV}.SCHEDULED_EXECUTOR.execute(new {PKG}.SackSaver()); }}
  catch (Throwable t) {{ new {PKG}.SackSaver().run(); }}
}}""", cpg))''', '''public static void saveSoon(String k) {{
  {PKG}.ProcStore.markDirty(k);
  {PKG}.SackPool.runOnWriter(new {PKG}.SackSaver());   // 0.7.18: the private writer (no file work on the engine's shared scheduler)
}}""", cpg))''')
rep('''  {PKG}.CraftLog.later(k, "PROFILE epoch " + last + " -> " + ep + " - bags, furnace and tannery now use this key");
  try {{ {HSV}.SCHEDULED_EXECUTOR.execute(new {PKG}.SackSaver()); }} catch (Throwable t) {{ }}''',
    '''  {PKG}.CraftLog.later(k, "PROFILE epoch " + last + " -> " + ep + " - bags, furnace and tannery now use this key");
  {PKG}.SackPool.runOnWriter(new {PKG}.SackSaver());   // 0.7.18: the private writer''')

# ================= KeptQuit: save at once on the writer + forget the 0.7.18 per-player state =================
rep('''    Object lk = u == null ? null : @PKG@.SackPool.KEPTKEY.get(u);
    @PKG@.SackPool.forgetKept(u);
    if (lk instanceof String && @PKG@.SackPool.DIRTY.containsKey(lk)) @PKG@.SackPool.saveSoon((String) lk);''',
    '''    Object lk = u == null ? null : @PKG@.SackPool.KEPTKEY.get(u);
    @PKG@.SackPool.forgetKept(u);
    if (lk instanceof String && @PKG@.SackPool.DIRTY.containsKey(lk)) @PKG@.SackPool.saveAsap((String) lk);   // 0.7.18: at once, on the writer
    if (u != null) {
      // 0.7.18: a relog is a first sight again (sweep, Furnace / Tannery catch-up); the cached coll:recipes set goes
      @PKG@.SweepTask.INVDIRTY.remove(u);
      @PKG@.SweepTask.SIG.remove(u);
      @PKG@.SweepTask.LASTSWEEP.remove(u);   // fixer: the heartbeat clock
      @PKG@.ProcTask.LASTK.remove(u);
      @PKG@.ProcTask.PAGEOPEN.remove(u);
      @PKG@.KnowSync.COLLC.remove(u);
    }''')

# ================= KnowSync: the cached coll:recipes set (audit 9e) =================
rep('''ksync.addMethod(CtNewMethod.make(jt(r\'\'\'
public static java.util.HashSet collSet(java.util.UUID u) {
  if (u == null) return null;
  try {
    Object v = @PKG@.SackPool.bridge().get("coll:recipes:" + u.toString());
    if (v == null) return null;
    java.util.HashSet out = new java.util.HashSet();
    String[] parts = String.valueOf(v).split(",");
    for (int i = 0; i < parts.length; i++) { String x = parts[i].trim(); if (x.length() > 0) out.add(x); }
    return out;
  } catch (Throwable t) { return null; }
}\'\'\'), ksync))''', '''# 0.7.18 (audit 9e): the parsed set is cached per player, keyed by coll:epoch:<uuid> AND the published string (the same object = no work,
# an equal string = one compare, anything else = one parse); collShared is read-only for its callers, collSet hands out a copy
ksync.addMethod(CtNewMethod.make(jt(r\'\'\'
public static java.util.HashSet collShared(java.util.UUID u) {
  if (u == null) return null;
  try {
    java.util.Map b = @PKG@.SackPool.bridge();
    Object v = b.get("coll:recipes:" + u.toString());
    if (v == null) { COLLC.remove(u); return null; }
    Object ep = b.get("coll:epoch:" + u.toString());
    String raw = String.valueOf(v);
    Object[] c = (Object[]) COLLC.get(u);
    if (c != null) {
      boolean se = c[0] == null ? ep == null : c[0].equals(ep);
      if (se && (c[1] == raw || ((String) c[1]).equals(raw))) return (java.util.HashSet) c[2];
    }
    java.util.HashSet out = new java.util.HashSet();
    String[] parts = raw.split(",");
    for (int i = 0; i < parts.length; i++) { String x = parts[i].trim(); if (x.length() > 0) out.add(x); }
    PARSES.incrementAndGet();
    COLLC.put(u, new Object[] { ep, raw, out });
    return out;
  } catch (Throwable t) { return null; }
}\'\'\'), ksync))
ksync.addMethod(CtNewMethod.make(jt(r\'\'\'
public static java.util.HashSet collSet(java.util.UUID u) {
  java.util.HashSet c = collShared(u);
  return c == null ? null : new java.util.HashSet(c);
}\'\'\'), ksync))''')
rep('''  java.util.HashSet c = collSet(u);
  if (c == null) return null;
  java.util.Iterator it = c.iterator();''', '''  java.util.HashSet c = collShared(u);   // 0.7.18: the cached set (read only here)
  if (c == null) return null;
  java.util.Iterator it = c.iterator();''')

# ================= SweepTask: sweep / refill / pocketFill / sweepLeft take the sweep's caps + counts =================
rep('''swp.addMethod(CtNewMethod.make(f"""
public static int sweep({PLA} p, String k, String onlyCat, boolean allContainers, java.util.HashMap swept) {{
  {INV} inv = p.getInventory();
  if (inv == null) return 0;
  java.util.HashMap caps = caps(inv);
  if (caps.isEmpty()) return 0;
  java.util.HashMap left = null;
  if (!allContainers) {{
    java.util.concurrent.ConcurrentHashMap km = {PKG}.SackPool.keptMap(k, false);
    if (km != null && !km.isEmpty()) {{
      java.util.HashMap held = carried(inv);''', '''# 0.7.18: capsIn / heldIn = the sweep's own caps() and carried() (null = scan here, the 0.7.17 path of every other caller)
swp.addMethod(CtNewMethod.make(f"""
public static int sweep({PLA} p, String k, String onlyCat, boolean allContainers, java.util.HashMap swept, java.util.HashMap capsIn, java.util.HashMap heldIn) {{
  {INV} inv = p.getInventory();
  if (inv == null) return 0;
  java.util.HashMap caps = capsIn != null ? capsIn : caps(inv);
  if (caps.isEmpty()) return 0;
  java.util.HashMap left = null;
  if (!allContainers) {{
    java.util.concurrent.ConcurrentHashMap km = {PKG}.SackPool.keptMap(k, false);
    if (km != null && !km.isEmpty()) {{
      java.util.HashMap held = heldIn != null ? heldIn : carried(inv);''')
rep('''swp.addMethod(CtNewMethod.make(f"""
public static int sweep({PLA} p, String k, String onlyCat, boolean allContainers) {{
  return sweep(p, k, onlyCat, allContainers, (java.util.HashMap) null);
}}""", swp))''', '''swp.addMethod(CtNewMethod.make(f"""
public static int sweep({PLA} p, String k, String onlyCat, boolean allContainers, java.util.HashMap swept) {{
  return sweep(p, k, onlyCat, allContainers, swept, (java.util.HashMap) null, (java.util.HashMap) null);
}}""", swp))
swp.addMethod(CtNewMethod.make(f"""
public static int sweep({PLA} p, String k, String onlyCat, boolean allContainers) {{
  return sweep(p, k, onlyCat, allContainers, (java.util.HashMap) null);
}}""", swp))''')
rep('''public static java.util.HashSet sweepLeft(@INV@ inv, String k, java.util.HashMap caps) {
  java.util.HashSet out = new java.util.HashSet();
  if (inv == null || caps == null || caps.isEmpty()) return out;
  @IC@ stor = inv.getStorage();
  if (stor == null) return out;
  java.util.HashMap held = null;''', '''public static java.util.HashSet sweepLeft(@INV@ inv, String k, java.util.HashMap caps, java.util.HashMap heldIn) {
  java.util.HashSet out = new java.util.HashSet();
  if (inv == null || caps == null || caps.isEmpty()) return out;
  @IC@ stor = inv.getStorage();
  if (stor == null) return out;
  java.util.HashMap held = heldIn;   // 0.7.18: the sweep's after-sweep counts (null = scan when needed)''')
rep('''# 0.7.8 review fix: how many cooked items the inventory holds (storage, hotbar, backpack = what Deposit all sweeps); world thread. Deposit''',
    '''swp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static java.util.HashSet sweepLeft(@INV@ inv, String k, java.util.HashMap caps) {
  return sweepLeft(inv, k, caps, (java.util.HashMap) null);
}\'\'\'), swp))
# 0.7.8 review fix: how many cooked items the inventory holds (storage, hotbar, backpack = what Deposit all sweeps); world thread. Deposit''')
rep('''public static int refill(@PLA@ p, String k, int mode, java.util.Set inUse, java.util.Set skip, java.util.HashMap done) {
  if (p == null || k == null || mode < 0 || mode > 1 || inUse == null || inUse.isEmpty()) return 0;
  @INV@ inv = p.getInventory();
  if (inv == null) return 0;
  java.util.HashMap caps = caps(inv);''', '''public static int refill(@PLA@ p, String k, int mode, java.util.Set inUse, java.util.Set skip, java.util.HashMap done, java.util.HashMap capsIn) {
  if (p == null || k == null || mode < 0 || mode > 1 || inUse == null || inUse.isEmpty()) return 0;
  @INV@ inv = p.getInventory();
  if (inv == null) return 0;
  java.util.HashMap caps = capsIn != null ? capsIn : caps(inv);   // 0.7.18: the sweep's caps''')
rep('''# ================= 0.7.17 REQUIP POCKET BLOCK SLOTS (tools/sacks_0_7_17_patch.py docstring item 1) =================''',
    '''swp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static int refill(@PLA@ p, String k, int mode, java.util.Set inUse, java.util.Set skip, java.util.HashMap done) {
  return refill(p, k, mode, inUse, skip, done, (java.util.HashMap) null);
}\'\'\'), swp))
# ================= 0.7.17 REQUIP POCKET BLOCK SLOTS (tools/sacks_0_7_17_patch.py docstring item 1) =================''')
rep('''public static int pocketFill(@PLA@ p, String k, java.util.UUID u) {
  if (p == null || k == null || u == null || !@PKG@.SackCfg.REFILL_ON) return 0;''',
    '''public static int pocketFill(@PLA@ p, String k, java.util.UUID u, java.util.HashMap capsIn, java.util.HashMap done) {
  if (p == null || k == null || u == null || !@PKG@.SackCfg.REFILL_ON) return 0;''')
rep('''  @IC@ hb = inv.getHotbar();
  if (hb == null) return 0;
  java.util.HashMap caps = caps(inv);
  if (caps.isEmpty()) return 0;''', '''  @IC@ hb = inv.getHotbar();
  if (hb == null) return 0;
  java.util.HashMap caps = capsIn != null ? capsIn : caps(inv);   // 0.7.18: the sweep's caps
  if (caps.isEmpty()) return 0;''')
rep('''    @PKG@.SackPool.add(k, id, -(long) got);
    @PKG@.BagMirror.afterTake(k, id);   // live-mirror rule: the mirror never offers more than the pool now holds
    @PKG@.SackPool.keep(k, id, (long) got);
    total += got;
  }
  return total;
}\'\'\'), swp))''', '''    @PKG@.SackPool.add(k, id, -(long) got);
    @PKG@.BagMirror.afterTake(k, id);   // live-mirror rule: the mirror never offers more than the pool now holds
    @PKG@.SackPool.keep(k, id, (long) got);
    total += got;
    if (done != null) {   // 0.7.18: what the slot gained (the sweep's SEENQ snapshot is derived from it)
      Long dv = (Long) done.get(id);
      done.put(id, Long.valueOf((dv == null ? 0L : dv.longValue()) + (long) got));
    }
  }
  return total;
}\'\'\'), swp))
swp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static int pocketFill(@PLA@ p, String k, java.util.UUID u) {
  return pocketFill(p, k, u, (java.util.HashMap) null, (java.util.HashMap) null);
}\'\'\'), swp))''')

# ================= SweepTask.items: one carried() scan, derived counts, the crash-window save =================
rep('''swp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static int[] items(@PLA@ p, String k, java.util.UUID u) {
  int[] out = new int[] { 0, 0 };
  if (p == null || k == null) return out;
  @INV@ inv = p.getInventory();
  if (inv == null) return out;
  if (u != null) @PKG@.SackPool.KEPTKEY.put(u, k);''', '''# 0.7.18: a + sign (b < 0 = minus); entries at 0 or below go (carried() never holds them)
swp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static java.util.HashMap addCounts(java.util.HashMap a, java.util.HashMap b, long sign) {
  java.util.HashMap out = new java.util.HashMap(a);
  if (b == null) return out;
  java.util.Iterator it = b.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    Long av = (Long) out.get(e.getKey());
    long nv = (av == null ? 0L : av.longValue()) + sign * ((Long) e.getValue()).longValue();
    if (nv <= 0L) out.remove(e.getKey()); else out.put(e.getKey(), Long.valueOf(nv));
  }
  return out;
}\'\'\'), swp))
swp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static int[] items(@PLA@ p, String k, java.util.UUID u, java.util.HashMap capsIn) {
  int[] out = new int[] { 0, 0 };
  if (p == null || k == null) return out;
  @INV@ inv = p.getInventory();
  if (inv == null) return out;
  java.util.HashMap caps = capsIn != null ? capsIn : caps(inv);   // 0.7.18: ONE caps() per sweep (bags never move in it)
  if (u != null) @PKG@.SackPool.KEPTKEY.put(u, k);''')
rep('''  try { keptDrop(before, k); } catch (Throwable t1) { @PKG@.KnowSync.warnOnce("kept count update failed: " + t1); }
  try { out[0] = sweep(p, k, (String) null, false); } catch (Throwable t0) { @PKG@.SackPool.warn("sweep failed: " + t0); }
  int mode = @PKG@.RefillPref.mode(u);
  if (mode != 2 && !used.isEmpty()) {
    try { out[1] = refill(p, k, mode, used, sweepLeft(inv, k, caps(inv)), (java.util.HashMap) null); }
    catch (Throwable t2) { @PKG@.KnowSync.warnOnce("stack refill failed: " + t2); }
  }
  // 0.7.17: Requip's reserved hotbar block slots (requip:pocket:<uuid>) - empty ones too; before the SEENQ snapshot (never "used")
  try { int pf = pocketFill(p, k, u); out[1] = out[1] + pf; }
  catch (Throwable t3) { @PKG@.KnowSync.warnOnce("hotbar block refill (Requip) failed: " + t3); }
  if (u != null) @PKG@.SackPool.SEENQ.put(u, carried(inv));
  return out;
}\'\'\'), swp))''', '''  try { keptDrop(before, k); } catch (Throwable t1) { @PKG@.KnowSync.warnOnce("kept count update failed: " + t1); }
  // 0.7.18: ONE carried() scan: the sweep gets it (its kept rule) and reports every removal (swept), the refill / Requip top-up report every
  // gain (done) - the after-sweep counts and the SEENQ snapshot are derived; any failure in these steps falls back to a real scan
  boolean exact = true;
  boolean sfail = false;   // fixer 2: a sweep that failed half way may have moved items it never reported
  java.util.HashMap swept = new java.util.HashMap();
  try { out[0] = sweep(p, k, (String) null, false, swept, caps, before); } catch (Throwable t0) { exact = false; sfail = true; @PKG@.SackPool.warn("sweep failed: " + t0); }
  java.util.HashMap now = exact ? addCounts(before, swept, -1L) : carried(inv);
  java.util.HashMap done = new java.util.HashMap();
  boolean rfail = false;   // fixer: a refill / top-up that failed half way may have moved items it never reported
  int mode = @PKG@.RefillPref.mode(u);
  if (mode != 2 && !used.isEmpty()) {
    try { out[1] = refill(p, k, mode, used, sweepLeft(inv, k, caps, now), done, caps); }
    catch (Throwable t2) { exact = false; rfail = true; @PKG@.KnowSync.warnOnce("stack refill failed: " + t2); }
  }
  // 0.7.17: Requip's reserved hotbar block slots (requip:pocket:<uuid>) - empty ones too; before the SEENQ snapshot (never "used")
  try { int pf = pocketFill(p, k, u, caps, done); out[1] = out[1] + pf; }
  catch (Throwable t3) { exact = false; rfail = true; @PKG@.KnowSync.warnOnce("hotbar block refill (Requip) failed: " + t3); }
  if (exact) @PKG@.SweepTask.EXACT.incrementAndGet(); else @PKG@.SweepTask.RESCANS.incrementAndGet();
  if (u != null) @PKG@.SackPool.SEENQ.put(u, exact ? addCounts(now, done, 1L) : carried(inv));
  // 0.7.18 THE CRASH WINDOW, fixer (review): only pool -> inventory moves (refill / Requip top-up) save early - the pool's decrease on disk
  // first means a crash before the engine's player save can never keep the items twice; a tick whose SWEEP moved anything (inventory ->
  // pool; fixer 2: also when the same tick refilled - the save writes the whole pool, the sweep's additions included) stays dirty for
  // the 10 s SackSaver like 0.7.17 (an early save there would make a crash keep the swept items in both places)
  boolean swq = out[0] > 0 || !swept.isEmpty() || sfail;
  if ((out[1] > 0 || !done.isEmpty() || rfail) && !swq) @PKG@.SackPool.saveSoon(k);   // (also a refill step that failed half way)
  return out;
}\'\'\'), swp))
swp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static int[] items(@PLA@ p, String k, java.util.UUID u) {
  return items(p, k, u, (java.util.HashMap) null);
}\'\'\'), swp))''')

# ================= SweepTask.run: the dirty flag, one caps(), the signature after the sweep =================
rep('''    String k = {PKG}.SackPool.settledKey(pr.getUuid());
    if (k == null) return;
    // 0.7.7 (research/Bag-Restructure-Spec.md 5.2 / 5.6 / 5.8), settled key only, world thread: the bag recipe knowledge follows coll:recipes,
    // carried bags get their rarity look, the one-time notice - each step on its own, so one failure never stops the sweep
    java.util.UUID u = pr.getUuid();
    try {{ {PKG}.KnowSync.sync(r, st, p, u); }} catch (Throwable t1) {{ {PKG}.KnowSync.warnOnce("bag recipe knowledge sync failed: " + t1); }}
    try {{ restamp(p.getInventory()); }} catch (Throwable t2) {{ {PKG}.KnowSync.warnOnce("bag rarity restamp failed: " + t2); }}
    try {{ if (!{PKG}.SackNotice.seen(u)) {PKG}.SackNotice.check(pr, u, k, !caps(p.getInventory()).isEmpty()); }} catch (Throwable t3) {{ }}
    // 0.7.11: kept counts + the sweep + the stack refill (items above)
    items(p, k, u);''', '''    String k = {PKG}.SackPool.settledKey(pr.getUuid());
    if (k == null) return;   // 0.7.18: the player stays dirty (no SIG stored) - retried on the next 2 s tick like before
    // 0.7.7 (research/Bag-Restructure-Spec.md 5.2 / 5.6 / 5.8), settled key only, world thread: the bag recipe knowledge follows coll:recipes,
    // carried bags get their rarity look, the one-time notice - each step on its own, so one failure never stops the sweep
    java.util.UUID u = pr.getUuid();
    INVDIRTY.remove(u);   // 0.7.18: cleared BEFORE the work - a change from here on marks the player again
    java.util.HashMap caps0 = caps(p.getInventory());   // 0.7.18: ONE caps() for the whole sweep
    try {{ {PKG}.KnowSync.sync(r, st, p, u); }} catch (Throwable t1) {{ {PKG}.KnowSync.warnOnce("bag recipe knowledge sync failed: " + t1); }}
    try {{ restamp(p.getInventory()); }} catch (Throwable t2) {{ {PKG}.KnowSync.warnOnce("bag rarity restamp failed: " + t2); }}
    try {{ if (!{PKG}.SackNotice.seen(u)) {PKG}.SackNotice.check(pr, u, k, !caps0.isEmpty()); }} catch (Throwable t3) {{ }}
    // 0.7.11: kept counts + the sweep + the stack refill (items above)
    items(p, k, u, caps0);
    SIG.put(u, sigOf(u));   // 0.7.18: what this sweep saw (incl. its own pool changes) - the 2 s tick skips the player until it changes
    LASTSWEEP.put(u, Long.valueOf(System.nanoTime()));   // fixer: the heartbeat clock''')

# ================= SackTick: hop only players with something to do =================
rep('''# ================= SackTick (scheduler thread -> dispatch to world threads) =================
tick.addInterface(pool.get("java.lang.Runnable"))''', '''# ================= 0.7.18 (audit 9b) WHO THE 2 s SWEEP VISITS =================
# cfgSig = the owner's settings a sweep depends on (free bag recipes, the refill switches, cooked food, the five bag caps).
swp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static String cfgSig() {
  return String.valueOf(@PKG@.SackCfg.effFree()) + "," + @PKG@.SackCfg.REFILL_ON + "," + @PKG@.SackCfg.REFILL_DEF + "," + @PKG@.SackDefs.COOKED_FARM + ","
    + @PKG@.SackDefs.CAP_SMALL + "," + @PKG@.SackDefs.CAP_MEDIUM + "," + @PKG@.SackDefs.CAP_RARE + "," + @PKG@.SackDefs.CAP_LARGE + "," + @PKG@.SackDefs.CAP_OMNI;
}\'\'\'), swp))
# sigOf(u) = everything besides an inventory change that can give a sweep something to do (plain bridge / map reads, any thread):
# the profile (epoch, busy), the bag recipe knowledge (coll:epoch + coll:recipes), Requip's reserved slots (requip:pocket / pocketN), the
# player's refill mode, the pool change counter of their key (another mod, a page or a bench took or put), the owner's settings
swp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static String sigOf(java.util.UUID u) {
  if (u == null) return "";
  java.util.Map b = @PKG@.SackPool.bridge();
  String us = u.toString();
  StringBuilder sb = new StringBuilder(128);
  sb.append(@PKG@.SackPool.epoch(u)).append('|');
  sb.append(b.get("profile:busy:" + us) != null).append('|');
  Object ce = b.get("coll:epoch:" + us);
  sb.append(ce == null ? "-" : String.valueOf(ce)).append('|');
  Object cr = b.get("coll:recipes:" + us);
  sb.append(cr == null ? 0 : cr.hashCode()).append('|');
  try { Object pm = b.get("requip:pocket:" + us); sb.append(pm == null ? 0 : pm.hashCode()); } catch (Throwable t) { sb.append('x'); }
  sb.append('|');
  try { Object pn = b.get("requip:pocketN:" + us); sb.append(pn == null ? 0 : pn.hashCode()); } catch (Throwable t2) { sb.append('x'); }
  sb.append('|').append(@PKG@.RefillPref.mode(u)).append('|');
  Object lk = @PKG@.SackPool.KEPTKEY.get(u);
  sb.append(lk instanceof String ? @PKG@.SackPool.chg((String) lk) : -1L).append('|');
  sb.append(cfgSig());
  return sb.toString();
}\'\'\'), swp))
# needs(u, sig): sweep this player now? The event system missing = everyone (0.7.17); an inventory change since the last sweep; a changed
# signature (first sight has none); fixer: the 20 s heartbeat
swp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static boolean needs(java.util.UUID u, String sig) {
  if (u == null) return false;
  if (!EVENTS_OK) return true;
  if (INVDIRTY.containsKey(u)) return true;
  Object last = SIG.get(u);
  if (last == null || !last.equals(sig)) return true;
  // fixer (review): the HEARTBEAT - not swept for HEARTBEAT_MS = due anyway (a change the event missed is only delayed, never lost)
  Long ls = (Long) LASTSWEEP.get(u);
  if (ls == null || System.nanoTime() - ls.longValue() >= HEARTBEAT_MS * 1000000L) { BEATS.incrementAndGet(); return true; }
  return false;
}\'\'\'), swp))

# ================= SackTick (scheduler thread -> dispatch to world threads) =================
tick.addInterface(pool.get("java.lang.Runnable"))''')
rep('''public void run() {{
  try {{
    java.util.Iterator it = {UNI}.get().getPlayers().iterator();
    while (it.hasNext()) {{
      {PR} pr = ({PR}) it.next();
      if (pr == null || !pr.isValid()) continue;
      java.util.UUID wu = pr.getWorldUuid();
      if (wu == null) continue;
      {WLD} w = {UNI}.get().getWorld(wu);
      if (w == null) continue;
      w.execute(new {PKG}.SweepTask(pr, wu));
    }}
  }} catch (Throwable t) {{ }}
}}""", tick))''', '''public void run() {{
  try {{
    java.util.Iterator it = {UNI}.get().getPlayers().iterator();
    while (it.hasNext()) {{
      {PR} pr = ({PR}) it.next();
      if (pr == null || !pr.isValid()) continue;
      // 0.7.18 (audit 9b): only a player with something to do costs a world hop
      java.util.UUID u0 = pr.getUuid();
      if (!{PKG}.SweepTask.needs(u0, {PKG}.SweepTask.sigOf(u0))) {{ {PKG}.SweepTask.SKIPS.incrementAndGet(); continue; }}
      java.util.UUID wu = pr.getWorldUuid();
      if (wu == null) continue;
      {WLD} w = {UNI}.get().getWorld(wu);
      if (w == null) continue;
      {PKG}.SweepTask.HOPS.incrementAndGet();
      w.execute(new {PKG}.SweepTask(pr, wu));
    }}
  }} catch (Throwable t) {{ }}
}}""", tick))''')

# ================= BenchLink: who the 300 ms link visits =================
rep('''blink.addField(CtField.make("public static final long REFRESH_MS = 1000L;", blink))
''', '''blink.addField(CtField.make("public static final long REFRESH_MS = 1000L;", blink))
# 0.7.18 (audit 9b): ACTIVE = players who may have a crafting window (u -> Long stamp): set for every OpenWindow / UpdateWindow the
# outbound filter sees, a craft click (inbound filter) and a new window record; cleared by the link pass that finds nothing left
blink.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap ACTIVE = new java.util.concurrent.ConcurrentHashMap();", blink))
for _f in ("LHOPS", "LSKIPS"):
    blink.addField(CtField.make("public static final java.util.concurrent.atomic.AtomicLong %s = new java.util.concurrent.atomic.AtomicLong();" % _f, blink))
blink.addMethod(CtNewMethod.make("""
public static void mark(java.util.UUID u) {
  if (u != null) ACTIVE.put(u, Long.valueOf(System.nanoTime()));
}""", blink))
''')
rep('''  if (!create) return null;
  @PKG@.LinkRec r = new @PKG@.LinkRec(w);
  l.add(r);
  return r;''', '''  if (!create) return null;
  @PKG@.LinkRec r = new @PKG@.LinkRec(w);
  l.add(r);
  mark(u);   // 0.7.18: a window record = the 300 ms link visits this player
  return r;''')
rep('''# ================= CraftPacketFilter (0.7.12, research doc A): the outbound filter (ALWAYS returns false - true drops the packet) =================''',
    '''# 0.7.18: should the 300 ms link visit u? No outbound filter = everyone (0.7.17); a flag (a window packet / click / record), a window record
# or a live mirror of the player's last key
blink.addMethod(CtNewMethod.make(jt(r\'\'\'
public static boolean needsLink(java.util.UUID u) {
  if (u == null) return false;
  if (OUT == null) return true;
  if (ACTIVE.containsKey(u) || RECS.containsKey(u)) return true;
  Object lk = @PKG@.BagMirror.LASTKEY.get(u);
  return lk != null && @PKG@.BagMirror.MIRRORS.containsKey(lk);
}\'\'\'), blink))
# 0.7.18: after a link pass - no bench / pocket window, no record, no mirror left -> the flag goes (only the stamp read before the pass:
# a packet that set a newer flag meanwhile keeps it)
blink.addMethod(CtNewMethod.make(jt(r\'\'\'
public static boolean idle(java.util.UUID u, java.util.List wins, Object stamp) {
  if (u == null || stamp == null) return false;
  for (int i = 0; wins != null && i < wins.size(); i++) {
    Object w = wins.get(i);
    if (isBench(w) || isPocket(w)) return false;
  }
  if (RECS.containsKey(u)) return false;
  Object lk = @PKG@.BagMirror.LASTKEY.get(u);
  if (lk != null && @PKG@.BagMirror.MIRRORS.containsKey(lk)) return false;
  return ACTIVE.remove(u, stamp);
}\'\'\'), blink))
# ================= CraftPacketFilter (0.7.12, research doc A): the outbound filter (ALWAYS returns false - true drops the packet) =================''')
rep('''    if (pkt instanceof @UW@ || pkt instanceof @OW@) @PKG@.BenchLink.outbound(pr, pkt);''',
    '''    if (pkt instanceof @UW@ || pkt instanceof @OW@) {
      if (pr != null) @PKG@.BenchLink.mark(pr.getUuid());   // 0.7.18: a window on screen -> the 300 ms link visits this player
      @PKG@.BenchLink.outbound(pr, pkt);
    }''')
rep('''    if (w == null) return false;
    w.execute(new @PKG@.PreCraftTask(pr, wu, a.id));''', '''    if (w == null) return false;
    @PKG@.BenchLink.mark(pr.getUuid());   // 0.7.18
    w.execute(new @PKG@.PreCraftTask(pr, wu, a.id));''')
rep('''    {WM} wm = p.getWindowManager();
    java.util.List wins = null;
    if (wm != null) wins = wm.getWindows();
    {PKG}.BenchLink.link(p, pr.getUuid(), wins, System.currentTimeMillis());''', '''    {WM} wm = p.getWindowManager();
    java.util.List wins = null;
    if (wm != null) wins = wm.getWindows();
    Object stamp = {PKG}.BenchLink.ACTIVE.get(pr.getUuid());   // 0.7.18
    {PKG}.BenchLink.link(p, pr.getUuid(), wins, System.currentTimeMillis());
    {PKG}.BenchLink.idle(pr.getUuid(), wins, stamp);   // 0.7.18: nothing open any more -> no more 300 ms visits''')
rep('''public void run() {{
  try {{
    java.util.Iterator it = {UNI}.get().getPlayers().iterator();
    while (it.hasNext()) {{
      {PR} pr = ({PR}) it.next();
      if (pr == null || !pr.isValid()) continue;
      java.util.UUID wu = pr.getWorldUuid();
      if (wu == null) continue;
      {WLD} w = {UNI}.get().getWorld(wu);
      if (w == null) continue;
      w.execute(new {PKG}.CraftLinkTask(pr, wu));
    }}
  }} catch (Throwable t) {{ }}
}}""", ctk))''', '''public void run() {{
  try {{ {PKG}.BenchLink.pocketCheck(); }} catch (Throwable t0) {{ }}   // 0.7.18: the bags.pocketCraft backstop, once per tick
  try {{
    java.util.Iterator it = {UNI}.get().getPlayers().iterator();
    while (it.hasNext()) {{
      {PR} pr = ({PR}) it.next();
      if (pr == null || !pr.isValid()) continue;
      if (!{PKG}.BenchLink.needsLink(pr.getUuid())) {{ {PKG}.BenchLink.LSKIPS.incrementAndGet(); continue; }}   // 0.7.18 (audit 9b)
      java.util.UUID wu = pr.getWorldUuid();
      if (wu == null) continue;
      {WLD} w = {UNI}.get().getWorld(wu);
      if (w == null) continue;
      {PKG}.BenchLink.LHOPS.incrementAndGet();
      w.execute(new {PKG}.CraftLinkTask(pr, wu));
    }}
  }} catch (Throwable t) {{ }}
}}""", ctk))''')

# ================= pages: PAGEOPEN (the 1 s Furnace / Tannery task keeps visiting while one is open) =================
rep('''public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.builtRef = ref;   // 0.7.15 page guard
  java.util.UUID u = this.playerRef.getUuid();''', '''public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.builtRef = ref;   // 0.7.15 page guard
  java.util.UUID u = this.playerRef.getUuid();
  if (u != null) @PKG@.ProcTask.PAGEOPEN.put(u, Boolean.TRUE);   // 0.7.18: the 1 s task keeps visiting (the profile notice)''')
rep('''public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  this.builtRef = ref;   // 0.7.15 page guard
  java.util.UUID u = this.playerRef.getUuid();''', '''public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  this.builtRef = ref;   // 0.7.15 page guard
  java.util.UUID u = this.playerRef.getUuid();
  if (u != null) {PKG}.ProcTask.PAGEOPEN.put(u, Boolean.TRUE);   // 0.7.18: the 1 s task keeps visiting (the profile notice)''')

# ================= ProcTask / ProcTick: who the 1 s Furnace / Tannery task visits =================
rep('''    java.util.UUID u = pr.getUuid();
    String k = {PKG}.SackPool.pkey(u);
    epochCheck(u, k);''', '''    java.util.UUID u = pr.getUuid();
    String k = {PKG}.SackPool.pkey(u);
    LASTK.put(u, k);   // 0.7.18: seen (the benches of k are loaded below)
    epochCheck(u, k);''')
rep('''    notice(p.getPageManager().getCustomPage(), k, r);   // 0.7.15: only a page built for this entity Ref (never one lost in a world move)''',
    '''    Object cp0 = p.getPageManager().getCustomPage();
    notice(cp0, k, r);   // 0.7.15: only a page built for this entity Ref (never one lost in a world move)
    if (!(cp0 instanceof {PKG}.CraftPage) && !(cp0 instanceof {PKG}.SacksPage)) PAGEOPEN.remove(u);   // 0.7.18''')
rep('''ptick.addInterface(pool.get("java.lang.Runnable"))
ptick.addConstructor(CtNewConstructor.make("public ProcTick() { }", ptick))''', '''# 0.7.18 (audit 9b): should the 1 s task visit u? Not seen yet (first sight loads the benches: offline progress), an open bag / craft page
# (the profile notice), a changed profile:epoch (epochCheck), a bench with a queued unit, or Smithing XP still to pay. An empty queue only
# moved its clock (addJob resets it), so skipping it changes nothing.
ptk.addMethod(CtNewMethod.make(f"""
public static boolean needs(java.util.UUID u) {{
  if (u == null) return false;
  Object ko = LASTK.get(u);
  if (!(ko instanceof String)) return true;
  if (PAGEOPEN.containsKey(u)) return true;
  long ep = {PKG}.SackPool.epoch(u);
  if (ep >= 0L) {{
    Long last = (Long) EPOCH.get(u);
    if (last == null || last.longValue() != ep) return true;
  }}
  String k = (String) ko;
  if ({PKG}.ProcStore.BROKEN.containsKey(k)) return false;
  java.util.Map m = (java.util.Map) {PKG}.ProcStore.STATES.get(k);
  if (m == null) return true;
  java.util.Iterator it = m.values().iterator();
  while (it.hasNext()) {{
    {PKG}.ProcBench pb = ({PKG}.ProcBench) it.next();
    if (pb.queued() > 0 || !pb.xpList().isEmpty()) return true;
  }}
  return false;
}}""", ptk))
ptick.addInterface(pool.get("java.lang.Runnable"))
ptick.addConstructor(CtNewConstructor.make("public ProcTick() { }", ptick))''')
rep('''      if (pr == null || !pr.isValid()) continue;
      java.util.UUID wu = pr.getWorldUuid();
      if (wu == null) continue;
      {WLD} w = {UNI}.get().getWorld(wu);
      if (w == null) continue;
      w.execute(new {PKG}.ProcTask(pr, wu));''', '''      if (pr == null || !pr.isValid()) continue;
      if (!{PKG}.ProcTask.needs(pr.getUuid())) {{ {PKG}.ProcTask.PSKIPS.incrementAndGet(); continue; }}   // 0.7.18 (audit 9b)
      java.util.UUID wu = pr.getWorldUuid();
      if (wu == null) continue;
      {WLD} w = {UNI}.get().getWorld(wu);
      if (w == null) continue;
      {PKG}.ProcTask.PHOPS.incrementAndGet();
      w.execute(new {PKG}.ProcTask(pr, wu));''')

# ================= SackInvSys: the inventory-change dirty flag =================
rep('''# ================= 0.7.6 admin config kit (research/Server-Setup-Spec.md 4.12, tools/CONFIG-CONTRACT.md) =================''',
    '''# ================= 0.7.18 SackInvSys: InventoryChangeEvent -> SweepTask.INVDIRTY (the 2 s sweep visits that player) =================
# The engine's InventorySystems$InventoryChangeEventSystem turns every ItemContainer change of an entity's inventory components into one
# InventoryChangeEvent on the entity (VERIFIED bytecode: InventoryComponent.getChangeEvents polled every tick, CommandBuffer.invoke); query
# = the Player component (the proven SkyyGear GearInvSys query), so only players; the PlayerRef is read from the same chunk. Only a map write here (world thread, cheap). ONE registerSystem in setup().
sinv.addConstructor(CtNewConstructor.make(jt("public SackInvSys() { super(@ICE@.class); }"), sinv))
sinv.addMethod(CtNewMethod.make(jt("public @QRY@ getQuery() { return (@QRY@) @PLA@.getComponentType(); }"), sinv))   # players (SkyyGear's GearInvSys query)
sinv.addMethod(CtNewMethod.make(jt(r\'\'\'
public void handle(int idx, @ACH@ chunk, @ST@ st, @CBF@ buf, @EVE@ ev) {
  try {
    @PR@ pr = (@PR@) chunk.getComponent(idx, @PR@.getComponentType());
    if (pr == null) return;
    java.util.UUID u = pr.getUuid();
    if (u == null) return;
    @PKG@.SweepTask.INVDIRTY.put(u, Boolean.TRUE);
    @PKG@.SweepTask.EVENTS.incrementAndGet();
  } catch (Throwable t) { }
}\'\'\'), sinv))

# ================= 0.7.6 admin config kit (research/Server-Setup-Spec.md 4.12, tools/CONFIG-CONTRACT.md) =================''')

# ================= plugin: the writer, the event system, the 10 s saver on the writer; shutdown =================
rep('''  this.ticker = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.SackTick(), 2L, 2L, java.util.concurrent.TimeUnit.SECONDS);
  this.saver = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.SackSaver(), 10L, 10L, java.util.concurrent.TimeUnit.SECONDS);''',
    '''  // 0.7.18 (audit 9c): the private pool writer (daemon "SkyySacks-writer") - pool saves, the 10 s SackSaver, Furnace / Tannery saves
  {PKG}.SackPool.WRITER = java.util.concurrent.Executors.newSingleThreadScheduledExecutor(new {PKG}.SackThreads());
  // 0.7.18 (audit 9b): the inventory-change flag of the 2 s sweep (ONE registerSystem); without it every player is swept as in 0.7.17
  try {{ getEntityStoreRegistry().registerSystem(new {PKG}.SackInvSys()); {PKG}.SweepTask.EVENTS_OK = true; }}
  catch (Throwable te) {{ {PKG}.SweepTask.EVENTS_OK = false; {PKG}.SackPool.warn("inventory-change listener not registered - every player is swept every 2 s (0.7.17): " + te); }}
  this.ticker = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.SackTick(), 2L, 2L, java.util.concurrent.TimeUnit.SECONDS);
  this.saver = {PKG}.SackPool.WRITER.scheduleAtFixedRate(new {PKG}.SackSaver(), 10L, 10L, java.util.concurrent.TimeUnit.SECONDS);''')
rep('''  try {{ if (this.procTicker != null) this.procTicker.cancel(false); }} catch (Throwable t) {{ }}
''', '''  try {{ if (this.procTicker != null) this.procTicker.cancel(false); }} catch (Throwable t) {{ }}
  // 0.7.18: the private writer stops (scheduled pool saves still run, 3 s at most); everything still dirty is flushed inline below
  try {{
    java.util.concurrent.ScheduledExecutorService ex = {PKG}.SackPool.WRITER;
    {PKG}.SackPool.WRITER = null;
    if (ex != null) {{ ex.shutdown(); ex.awaitTermination(3L, java.util.concurrent.TimeUnit.SECONDS); }}
  }} catch (Throwable t) {{ }}
  {PKG}.SackPool.PENDING.clear();
''')
rep('''          pcw, psu, clt, ctk, rcmp, clog, cpg, ccmd, cfac, ptk, ptick, sbr, sfn, pl):''',
    '''          pcw, psu, clt, ctk, rcmp, clog, cpg, ccmd, cfac, ptk, ptick, sbr, sfn, pl, sthr, psj, sinv):   # 0.7.18: + SackThreads, PoolSaveJob, SackInvSys''')

# ================= FIXER 2 (review): which tick may save the pool early - per item, never carrying an unsaved sweep =================
# The pool file is written WHOLE, so an early save carries every pool change not yet on disk. SWEPTQ = keys whose pool holds sweep
# additions (inventory -> pool) not yet written: set by a tick whose sweep was not fully offset, cleared by saveNow right BEFORE it
# snapshots the pool (a failed write puts it back). A refill / top-up tick saves early only when (1) its own sweep (if any) moved, per
# item, no more than the refill / top-up moved back out of the pool (net pool change <= 0 for every item = a crash before the engine's
# player save can only lose, never double), (2) no earlier unsaved sweep is pending (SWEPTQ), and (3) the key is quiet (quiet(k): no
# PoolSaveJob pending, none run within DEBOUNCE_MS - the save runs at once, it never waits a second in which a new sweep could join it).
# Otherwise the key just stays dirty: a pending job or the 10 s SackSaver writes it - 0.7.17's timing.
rep('''sp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap LASTSAVE = new java.util.concurrent.ConcurrentHashMap();", sp))
''', '''sp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap LASTSAVE = new java.util.concurrent.ConcurrentHashMap();", sp))
# fixer 2: SWEPTQ = key -> TRUE while the in-memory pool holds sweep additions the pool file does not have yet (cleared by saveNow)
sp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap SWEPTQ = new java.util.concurrent.ConcurrentHashMap();", sp))
''')
rep('''public static void saveNow(String k) {
  try {
    java.util.Map m = (java.util.Map) POOLS.get(k);
    if (m == null) return;
''', '''public static void saveNow(String k) {
  Object sq = null;   // fixer 2
  try {
    java.util.Map m = (java.util.Map) POOLS.get(k);
    if (m == null) return;
    sq = SWEPTQ.remove(k);   // fixer 2: BEFORE the snapshot - a sweep from here on marks the key again
''')
rep('''  } catch (Throwable t) { DIRTY.put(k, Boolean.TRUE); warn("could not save pool for " + k + " (kept dirty - retried by the next save): " + t); }''',
    '''  } catch (Throwable t) { if (sq != null) SWEPTQ.put(k, sq); DIRTY.put(k, Boolean.TRUE); warn("could not save pool for " + k + " (kept dirty - retried by the next save): " + t); }''')
rep('''# 0.7.18: a key saved at once on the writer (a player leaving - the engine saves their inventory now too)
''', '''# fixer 2: a key whose save would run AT ONCE (the leading edge): a writer, no job pending, none run within DEBOUNCE_MS
sp.addMethod(CtNewMethod.make("""
public static boolean quiet(String k) {
  if (k == null || WRITER == null || PENDING.containsKey(k)) return false;
  Long last = (Long) LASTSAVE.get(k);
  return last == null || System.nanoTime() - last.longValue() >= DEBOUNCE_MS * 1000000L;
}""", sp))
# 0.7.18: a key saved at once on the writer (a player leaving - the engine saves their inventory now too)
''')
rep("""swp.addMethod(CtNewMethod.make(jt(r'''
public static int[] items(@PLA@ p, String k, java.util.UUID u, java.util.HashMap capsIn) {""", """# fixer 2: true when every item the sweep moved into the pool went back out at least as many times in the same tick (refill / top-up)
swp.addMethod(CtNewMethod.make(jt(r'''
public static boolean covered(java.util.HashMap swept, java.util.HashMap done) {
  java.util.Iterator it = swept.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    Long d = (Long) done.get(e.getKey());
    if (d == null || d.longValue() < ((Long) e.getValue()).longValue()) return false;
  }
  return true;
}'''), swp))
swp.addMethod(CtNewMethod.make(jt(r'''
public static int[] items(@PLA@ p, String k, java.util.UUID u, java.util.HashMap capsIn) {""")
rep('''  // 0.7.18 THE CRASH WINDOW, fixer (review): only pool -> inventory moves (refill / Requip top-up) save early - the pool's decrease on disk
  // first means a crash before the engine's player save can never keep the items twice; a tick whose SWEEP moved anything (inventory ->
  // pool; fixer 2: also when the same tick refilled - the save writes the whole pool, the sweep's additions included) stays dirty for
  // the 10 s SackSaver like 0.7.17 (an early save there would make a crash keep the swept items in both places)
  boolean swq = out[0] > 0 || !swept.isEmpty() || sfail;
  if ((out[1] > 0 || !done.isEmpty() || rfail) && !swq) @PKG@.SackPool.saveSoon(k);   // (also a refill step that failed half way)''',
    '''  // 0.7.18 THE CRASH WINDOW, fixer (review): only pool -> inventory moves (refill / Requip top-up) save early - the pool's decrease on disk
  // first means a crash before the engine's player save can never keep the items twice; sweep additions (inventory -> pool) stay dirty for
  // the 10 s SackSaver like 0.7.17 (an early save would make a crash keep the swept items in both places). FIXER 2 (review): the save
  // writes the WHOLE pool, so it may run only when nothing in it is an unsaved sweep: this tick's sweep fully offset per item by its own
  // refill / top-up (covered), no earlier unsaved sweep (SWEPTQ), and a save that runs at once (quiet) - else 0.7.17's timing.
  boolean moved = out[0] > 0 || !swept.isEmpty() || sfail;
  boolean net = moved && (sfail || swept.isEmpty() || !covered(swept, done));   // a sweep the pool file must not get early
  if (net) @PKG@.SackPool.SWEPTQ.put(k, Boolean.TRUE);
  boolean refilled = out[1] > 0 || !done.isEmpty() || rfail;   // (also a refill step that failed half way)
  if (refilled && !net && !@PKG@.SackPool.SWEPTQ.containsKey(k) && @PKG@.SackPool.quiet(k)) @PKG@.SackPool.saveSoon(k);''')

# ================= self-checks =================
assert 'VERSION = "0.7.18"' in s and s.count("registerCommand(") == REG0 and s.count("registerGlobal(") == GLB0, "no new command or event"
assert s.count("registerSystem(") == SYS0 + 1, "exactly one new ECS system (SackInvSys)"
assert s.count("pool.makeClass(") == MAKE0 + 3, "three new classes"
assert s[s.index("# ================= assets ================="):] == ASSETS0, "0.7.18 changes nothing in the assets section"
assert s.index("public static void runOnWriter(") < s.index("public static void saveJob(") < s.index("public static void saveSoon(String k) {{\n  if (k != null) DIRTY.put")
assert s.index("public static java.util.HashSet collShared(") < s.index("public static java.util.HashSet collSet(") < s.index("public static java.util.HashSet wanted(")
assert s.index("public static int sweep({PLA} p, String k, String onlyCat, boolean allContainers, java.util.HashMap swept, java.util.HashMap capsIn")\
    < s.index("public static int sweep({PLA} p, String k, String onlyCat, boolean allContainers, java.util.HashMap swept) {{")
assert s.index("public static int pocketFill(@PLA@ p, String k, java.util.UUID u, java.util.HashMap capsIn") < s.index("public static int pocketFill(@PLA@ p, String k, java.util.UUID u) {")\
    < s.index("public static int[] items(@PLA@ p, String k, java.util.UUID u, java.util.HashMap capsIn)") < s.index("public static int[] items(@PLA@ p, String k, java.util.UUID u) {")
assert s.index("public static String sigOf(") < s.index("public static boolean needs(java.util.UUID u, String sig)") < s.index("public void run() {{\n  try {{\n    java.util.Iterator it = {UNI}.get().getPlayers().iterator();")
assert s.index("public static void mark(java.util.UUID u)") < s.index("public static @PKG@.LinkRec recOf(")
assert s.count("if (refilled && !net && !@PKG@.SackPool.SWEPTQ.containsKey(k) && @PKG@.SackPool.quiet(k)) @PKG@.SackPool.saveSoon(k);\n  return out;") == 1
assert s.index("public static void saveNow(String k) {") > s.index("ConcurrentHashMap SWEPTQ =") and s.index("public static boolean quiet(String k)") \
    < s.index("public static boolean covered(") < s.index("public static int[] items(@PLA@ p, String k, java.util.UUID u, java.util.HashMap capsIn)")
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst, "(%d lines)" % s.count(LF))
