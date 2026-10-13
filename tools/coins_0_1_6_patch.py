"""Derive SkyyCoins/build_skyycoins_0.1.6.py from the LIVE 0.1.5 (build_skyycoins_0.1.5.py = the tools/deploy_set.py SET pin; 0.1.5 and every
older script stay untouched; CRLF kept).
Run:  python tools/coins_0_1_6_patch.py   then   python SkyyCoins/build_skyycoins_0.1.6.py   then   python SkyyCoins/test_skyycoins_0.1.6.py
(never --deploy: coordinated deploy). Edit THIS patch, never the generated script.

0.1.6 (2026-10-13) = LAG FIXES from the code audit (research/Code-Structure-Audit.md finding #1 + pack-wide pattern 1; Skyy 2026-10-13:
"During/ before we consolidate the mods together, lets audit the code structure, and make sure they are working together in the smoothest
easiest lag free way possible"):
 A. LOCK-FREE BRIDGE: CoinStore.bridge() caches the skyy.bridge map in the static volatile CoinStore.BRIDGE; only the very first call takes
    synchronized(System.class) (to create the map exactly as before, same identity) - every later call is one volatile read.
 B. WRITE-BEHIND LEDGER: the in-memory balance (BAL) stays the authority, exactly as in 0.1.5. setK no longer writes the balance file on the
    caller's (world) thread inside the ledger lock (0.1.5: a whole tmp file + replace with up to 5 x 20 ms sleeps per balance change); it
    marks the key DIRTY. ONE private daemon thread "SkyyCoins-IO" (not HytaleServer.SCHEDULED_EXECUTOR) flushes every dirty key once a second
    (coalesced: 50 changes of one purse in that second = one write), right after a PlayerDisconnectEvent, and SYNCHRONOUSLY at shutdown
    (the writer is stopped first, then the shutdown thread flushes and retries once; a key it still cannot write is named in a WARN).
    No Thread.sleep anywhere (a failed write puts its keys back in DIRTY for the next second).
    DUPE / LOSS SAFETY - one batch = one consistent snapshot: CoinStore.takeBatch() copies every dirty key's balance UNDER THE LEDGER LOCK,
    the same lock transferK holds while it moves coins, so a /pay's debit and credit are always in the same batch (both or neither). Every
    batch is first written as ONE journal file (Skyy_SkyyCoins/balances-journal.properties: tmp + fsync + atomic rename), then each balance
    file (tmp + fsync + atomic rename, the 0.1.5 format byte for byte: Properties "balance" with the "SkyyCoins" comment), then the journal
    is deleted. A crash / kill at ANY step leaves either the old files (journal not yet in place = the previous consistent state) or a
    journal that CoinStore.recover() replays at the next start before anything is read (every balance of the batch rewritten from it =
    the new consistent state). The journal is always the newest batch whose files started to be written (each batch overwrites it first),
    so a replay never puts an older value over a newer one. A crash loses at most the last second of changes - the same window for both
    sides of a transfer, never one side only.
    FIRST READS off the world thread: a purse file is read at most once per server run (0.1.5 too). The read now happens OUTSIDE the
    ledger lock (loadK reads, then installs under the lock), and is prefetched on the IO thread when a player is ready in a world and when
    CoinTick sees a profile switch, so the world thread normally finds the purse already in memory. An unreadable file keeps 0.1.5's
    freeze exactly (never cached as loaded, retried on every use, nothing written over it - need() / starterK / publishK unchanged).
 C. Rollback: 0.1.5 reads every file 0.1.6 writes (same names, same format). The journal is a new file 0.1.5 ignores; a clean shutdown
    deletes it (it only survives a crash - start 0.1.6 once to replay it, or copy its v.<i> values into balances/<k.<i>>.properties).
 D. FIX ROUND (critic findings, 2026-10-13):
    - STALE JOURNAL: recover() replays a journal only if no balance file it names was written LATER with a DIFFERENT value (a 0.1.5 run
      after a rollback writes those; a file of the journal's own batch is newer but holds the journal's value). A stale journal is never
      replayed (that would bring back spent coins / remove earned ones): it is renamed balances-journal.stale-<millis>.properties (kept
      for an admin) and named in a WARN.
    - LATE CHANGES: once stopIO() ran (STOPPED), every public op flushes synchronously after it (recheck(), outside the ledger lock), so
      a coin change that arrives after the shutdown flush is still written.
    - coins:fn:flush (new bridge function, apply(anything) -> Integer: keys written, 0 = nothing dirty, -1 = failed and retried): writes
      every dirty purse NOW. A mod that writes its own side of a coin move to disk at once (guild bank, auction records) calls it right
      after coins:fn:take / add, so a hard crash can no longer leave the other mod's file credited while the purse file still holds the
      coins (SkyyGuilds 0.1.7 + SkyyAuctions 0.1.4 call it; a mod that does not stays on the 1 s window).
    - SECOND FIX ROUND (D2): a start-up journal that cannot be replayed (unreadable, a locked balance file, a failed stale move) is no
      longer overwritten by the first flush: RECOVER_PENDING freezes every purse load (refused like an unreadable file; no starter
      coins meanwhile) and blocks every flush; the SkyyCoins-IO thread retries each second; the 10th failure moves it aside
      (balances-journal.failed-<millis>.properties, loud WARN for an admin). A readable, non-stale journal is folded into memory
      (LOADED + DIRTY) and written by the normal writer (superset journal first), so a replay write that fails stays dirty and is
      retried - never half-applied. A batch of ONE purse with no journal on disk skips the journal (one atomic rename is enough; halves
      the cost of coins:fn:flush after a single take / add).
    - HUD WITHOUT SkyyProfiles: CoinTask publishes coins:<uuid> the first time it sees a profile key while the player is online
      (CoinStore.firstSeen - starter coins as before, else a publish), so a purse the IO thread prefetched (no publish) still reaches the
      HUD on join (0.1.5's first loadK published; with SkyyProfiles the epoch change did it).
Nothing else changes: the same commands, permissions, bridge keys (coins:<uuid>, coins:fn:get / add / take; + coins:fn:flush, D), messages, death penalty,
starter coins, profile handling, unreadable-file freeze.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyCoins", "build_skyycoins_0.1.5.py")
dst = os.path.join(ROOT, "SkyyCoins", "build_skyycoins_0.1.6.py")
raw = open(src, "rb").read()
assert raw.count(b"\r\n") == raw.count(b"\n"), "expected pure CRLF source"
s = raw.decode("utf8").replace("\r\n", "\n")
assert 'VERSION = "0.1.5"' in s and "balances-journal" not in s, "the source must be the generated 0.1.5 script"


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "expected %d occurrence(s), found %d of:\n%s" % (count, n, old[:300])
    s = s.replace(old, new)


HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.1.6 (2026-10-13)"):].rstrip() + "\n"

# ---------- docstring + version ----------
rep('"""SkyyCoins 0.1.5 - build script (javassist via jpype).\n'
    'Run:   python build_skyycoins_0.1.5.py            -> SkyyCoins/SkyyCoins-0.1.5.jar\n'
    '       python build_skyycoins_0.1.5.py --deploy   -> also copies to Mods/SkyyCoins.jar and enables it in the HUD mod world\n',
    '"""SkyyCoins 0.1.6 - build script (javassist via jpype). GENERATED by tools/coins_0_1_6_patch.py from the LIVE 0.1.5 - edit the patch.\n'
    'Run:   python build_skyycoins_0.1.6.py            -> SkyyCoins/SkyyCoins-0.1.6.jar\n'
    '       (no --deploy: tools/deploy_set.py installs the whole set)\n'
    + NOTE)
rep('VERSION = "0.1.5"', 'VERSION = "0.1.6"')
rep('LOG = "com.hypixel.hytale.logger.HytaleLogger"\n',
    'LOG = "com.hypixel.hytale.logger.HytaleLogger"\n'
    'PDE = "com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent"\n'
    'PRE = "com.hypixel.hytale.server.core.event.events.player.PlayerReadyEvent"\n')
rep('             ("com.hypixel.hytale.server.core.plugin.PluginBase", "shutdown")):\n',
    '             ("com.hypixel.hytale.server.core.plugin.PluginBase", "shutdown"),\n'
    '             ("com.hypixel.hytale.server.core.plugin.PluginBase", "getEventRegistry"),\n'
    '             (PDE, "getPlayerRef"), (PRE, "getPlayerRef")):\n')

# ---------- classes ----------
rep('fn   = pool.makeClass(PKG + ".CoinFn")\n',
    'fn   = pool.makeClass(PKG + ".CoinFn")\n'
    'cio  = pool.makeClass(PKG + ".CoinIO")      # 0.1.6: the SkyyCoins-IO writer (flush / prefetch task + its thread factory)\n'
    'cev  = pool.makeClass(PKG + ".CoinEvents")  # 0.1.6: PlayerReadyEvent (prefetch) + PlayerDisconnectEvent (flush now)\n')

# ---------- A: lock-free bridge ----------
rep('''cs.addMethod(CtNewMethod.make("""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""", cs))''',
'''# 0.1.6 A: lock-free bridge - the map is cached in BRIDGE after the first call; only that first call takes the System.class monitor
# (created exactly as before: get, create if absent, put), so every later call is one volatile read (research/Code-Structure-Audit.md)
cs.addField(CtField.make("public static volatile java.util.Map BRIDGE;", cs))
cs.addMethod(CtNewMethod.make("""
public static java.util.Map bridge0() {
  Object o = System.getProperties().get("skyy.bridge");
  if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
  return (java.util.Map) o;
}""", cs))
cs.addMethod(CtNewMethod.make("""
public static java.util.Map bridge() {
  java.util.Map m = BRIDGE;
  if (m != null) return m;
  synchronized (java.lang.System.class) { m = bridge0(); }
  BRIDGE = m;
  return m;
}""", cs))''')

# ---------- B: write-behind fields ----------
rep('''cs.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap BADWARN = new java.util.concurrent.ConcurrentHashMap();", cs))
''',
'''cs.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap BADWARN = new java.util.concurrent.ConcurrentHashMap();", cs))
# 0.1.6 B (write-behind): DIRTY = keys whose balance changed since their last write (key -> Boolean); JOURNAL = the batch journal
# (Skyy_SkyyCoins/balances-journal.properties); IOLOCK = one flush at a time (the writer thread, or the shutdown thread after the
# writer stopped); IO = the SkyyCoins-IO executor (null = not started / stopped); STOP_AT / STEPS = test hook (0 = off): the harness
# stops a flush at step N to leave the disk exactly as a crash at that step would; IOWARN = last write warning (once a minute).
cs.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap DIRTY = new java.util.concurrent.ConcurrentHashMap();", cs))
cs.addField(CtField.make("public static java.nio.file.Path JOURNAL;", cs))
cs.addField(CtField.make("public static final Object IOLOCK = new Object();", cs))
cs.addField(CtField.make("public static volatile java.util.concurrent.ScheduledExecutorService IO;", cs))
cs.addField(CtField.make("public static volatile int STOP_AT = 0;", cs))
cs.addField(CtField.make("public static int STEPS = 0;", cs))
cs.addField(CtField.make("public static volatile long IOWARN = 0L;", cs))
cs.addField(CtField.make("public static volatile long WRITES = 0L;", cs))
# 0.1.6 D: STOPPED = stopIO() ran (every later public op flushes synchronously after itself)
cs.addField(CtField.make("public static volatile boolean STOPPED = false;", cs))
# 0.1.6 D2: RECOVER_PENDING = the start-up journal could not be read / checked / moved yet: every purse load waits (frozen, refused like
# an unreadable file) and no flush runs (nothing may overwrite that journal); the SkyyCoins-IO thread retries every second
# (RECOVER_TRIES; the 10th failure moves the journal aside as balances-journal.failed-<millis>.properties with a loud WARN)
cs.addField(CtField.make("public static volatile boolean RECOVER_PENDING = false;", cs))
cs.addField(CtField.make("public static int RECOVER_TRIES = 0;", cs))
''')

# ---------- B: loadK reads OUTSIDE the ledger lock, installs under it ----------
rep('''cs.addMethod(CtNewMethod.make("""
public static synchronized boolean loadK(java.util.UUID u, String k) {
  if (LOADED.containsKey(k)) return true;
  try {
    java.nio.file.Path f = DIR.resolve(k + ".properties");
    Long bal = null;
    if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {
      java.util.Properties p = new java.util.Properties();
      java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
      try { p.load(in); } finally { in.close(); }
      String v = p.getProperty("balance");
      if (v != null) bal = Long.valueOf(Long.parseLong(v.trim()));
    }
    if (bal != null) BAL.put(k, bal);
    LOADED.put(k, Boolean.TRUE);
    BADWARN.remove(k);
    Long cur = (Long) BAL.get(k);
    bridge().put("coins:" + u.toString(), cur == null ? Long.valueOf(0L) : cur);
    return true;
  } catch (Throwable t) {
    long now = System.currentTimeMillis();
    Object last = BADWARN.get(k);
    if (!(last instanceof Long) || now - ((Long) last).longValue() >= 60000L) {
      BADWARN.put(k, Long.valueOf(now));
      warn("balances/" + k + ".properties exists but cannot be read (" + t + ") - that purse is frozen (no starter coins, nothing added, taken or overwritten) until the file is fixed or removed; retried on every use");
    }
    return false;
  }
}""", cs))''',
'''# 0.1.6 B: the file is READ outside the ledger lock (readK: {Long balance or null = no file / no balance line} or the Throwable), then
# INSTALLED under it (installK; a key another thread installed meanwhile is kept - never overwritten by an older read). Same result as
# 0.1.5's loadK for every file: no file = no balance, a balance line = that balance, unreadable = frozen (never cached, retried, warned
# once a minute). pub = publish coins:<uuid> on the first install (0.1.5 always did; the IO thread's prefetch passes false, so a stale
# profile key can never show on the HUD).
cs.addMethod(CtNewMethod.make("""
public static Object readK(String k) {
  try {
    java.nio.file.Path f = DIR.resolve(k + ".properties");
    Long bal = null;
    if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {
      java.util.Properties p = new java.util.Properties();
      java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
      try { p.load(in); } finally { in.close(); }
      String v = p.getProperty("balance");
      if (v != null) bal = Long.valueOf(Long.parseLong(v.trim()));
    }
    return new Object[] { bal };
  } catch (Throwable t) { return t; }
}""", cs))
cs.addMethod(CtNewMethod.make("""
public static synchronized boolean installK(java.util.UUID u, String k, Object r, boolean pub) {
  if (LOADED.containsKey(k)) return true;
  if (!(r instanceof Object[])) {
    long now = System.currentTimeMillis();
    Object last = BADWARN.get(k);
    if (!(last instanceof Long) || now - ((Long) last).longValue() >= 60000L) {
      BADWARN.put(k, Long.valueOf(now));
      warn("balances/" + k + ".properties exists but cannot be read (" + r + ") - that purse is frozen (no starter coins, nothing added, taken or overwritten) until the file is fixed or removed; retried on every use");
    }
    return false;
  }
  Object bal = ((Object[]) r)[0];
  if (bal instanceof Long) BAL.put(k, bal);
  LOADED.put(k, Boolean.TRUE);
  BADWARN.remove(k);
  if (pub && u != null) {
    Long cur = (Long) BAL.get(k);
    bridge().put("coins:" + u.toString(), cur == null ? Long.valueOf(0L) : cur);
  }
  return true;
}""", cs))
cs.addMethod(CtNewMethod.make("""
public static boolean loadK0(java.util.UUID u, String k, boolean pub) {
  if (LOADED.containsKey(k)) return true;
  if (RECOVER_PENDING) {
    long now = System.currentTimeMillis();
    if (now - IOWARN >= 60000L) { IOWARN = now; warn("purses wait for balances-journal.properties (an unfinished save from before the last stop) to be replayed - coin changes are refused until then (retried every second)"); }
    return false;
  }
  return installK(u, k, readK(k), pub);
}""", cs))
cs.addMethod(CtNewMethod.make("""
public static boolean loadK(java.util.UUID u, String k) {
  return loadK0(u, k, true);
}""", cs))''')

# ---------- B: setK marks dirty instead of writing; saveK replaced by the writer ----------
rep('''# tmp file + replace; the replace retries 5 x 20 ms on a FileSystemException (Windows refuses to replace a file another handle
# has open: AccessDeniedException - SkyyProfiles 0.1 pattern). A failed save keeps BAL (memory) for the next change to write.
cs.addMethod(CtNewMethod.make("""
public static synchronized void saveK(String k, long v) {
  java.nio.file.Path dst = null;
  java.nio.file.Path tmp = null;
  try {
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    dst = DIR.resolve(k + ".properties");
    tmp = DIR.resolve(k + ".properties.tmp");
    java.util.Properties p = new java.util.Properties();
    p.setProperty("balance", String.valueOf(v));
    java.io.OutputStream out = java.nio.file.Files.newOutputStream(tmp, new java.nio.file.OpenOption[0]);
    try { p.store(out, "SkyyCoins"); } finally { out.close(); }
  } catch (Throwable t) { warn("could not save balance for " + k + " (kept in memory, written with the next change): " + t); return; }
  Throwable last = null;
  int i = 0;
  while (i < 5) {
    try {
      java.nio.file.Files.move(tmp, dst, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
      return;
    } catch (java.nio.file.FileSystemException e) {
      last = e;
      i++;
    } catch (Throwable t) {
      last = t;
      i = 5;
    }
    if (i < 5) { try { Thread.sleep(20L); } catch (Throwable ie) { } }
  }
  warn("could not save balance for " + k + " (kept in memory, written with the next change): " + last);
}""", cs))
cs.addMethod(CtNewMethod.make("""
public static synchronized void setK(java.util.UUID u, String k, long v) {
  if (v < 0L) v = 0L;
  need(u, k);
  BAL.put(k, Long.valueOf(v));
  bridge().put("coins:" + u.toString(), Long.valueOf(v));
  saveK(k, v);
}""", cs))''',
'''# ---- 0.1.6 B: the writer (SkyyCoins-IO thread or the shutdown thread; never a world thread, never inside the ledger lock) ----
# test hook: a flush stops at step STOP_AT (0 = off) like a crash there - the harness then restarts on what is on disk
cs.addMethod(CtNewMethod.make("""
public static void step() {
  STEPS = STEPS + 1;
  if (STOP_AT > 0 && STEPS == STOP_AT) throw new java.lang.IllegalStateException("SkyyCoins test stop at step " + STEPS);
}""", cs))
# tmp + fsync + atomic rename (plain REPLACE_EXISTING where ATOMIC_MOVE is not supported); one try, no sleep - a failure throws and the
# caller puts the batch back in DIRTY for the next second
cs.addMethod(CtNewMethod.make("""
public static void writeProps(java.nio.file.Path dst, java.util.Properties p, String comment) throws java.io.IOException {
  java.nio.file.Path tmp = dst.resolveSibling(dst.getFileName().toString() + ".tmp");
  java.io.FileOutputStream out = new java.io.FileOutputStream(tmp.toFile());
  try {
    p.store(out, comment);
    out.flush();
    out.getFD().sync();
  } finally { out.close(); }
  try {
    java.nio.file.Files.move(tmp, dst, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING, java.nio.file.StandardCopyOption.ATOMIC_MOVE });
  } catch (java.nio.file.AtomicMoveNotSupportedException a) {
    java.nio.file.Files.move(tmp, dst, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
  }
}""", cs))
# a balance file in the 0.1.5 format (Properties "balance", comment "SkyyCoins") - 0.1.5 reads it unchanged
cs.addMethod(CtNewMethod.make("""
public static void writeKey(String k, long v) throws java.io.IOException {
  java.util.Properties p = new java.util.Properties();
  p.setProperty("balance", String.valueOf(v));
  writeProps(DIR.resolve(k + ".properties"), p, "SkyyCoins");
  WRITES = WRITES + 1L;
}""", cs))
# a profile storage key is a UUID, optionally with -p<N> (tools/PROFILES-CONTRACT.md): letters, digits and '-' only (journal replay
# never writes a path that is not a plain balance file of balances/)
cs.addMethod(CtNewMethod.make("""
public static boolean keyOk(String k) {
  if (k == null || k.length() == 0 || k.length() > 80) return false;
  for (int i = 0; i < k.length(); i++) {
    char c = k.charAt(i);
    if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || c == '-')) return false;
  }
  return true;
}""", cs))
# ONE consistent snapshot of every dirty key, taken under the ledger lock (transferK changes both sides under the same lock, so a
# transfer is always all in one batch). null = nothing dirty. {String[] keys, long[] balances}
cs.addMethod(CtNewMethod.make("""
public static synchronized Object[] takeBatch() {
  if (DIRTY.isEmpty()) return null;
  java.util.ArrayList ks = new java.util.ArrayList();
  java.util.ArrayList vs = new java.util.ArrayList();
  java.util.Iterator it = new java.util.ArrayList(DIRTY.keySet()).iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    DIRTY.remove(k);
    Object v = BAL.get(k);
    if (!(v instanceof Long)) continue;
    ks.add(k);
    vs.add(v);
  }
  if (ks.size() == 0) return null;
  String[] ka = new String[ks.size()];
  long[] va = new long[ks.size()];
  for (int i = 0; i < ka.length; i++) { ka[i] = (String) ks.get(i); va[i] = ((Long) vs.get(i)).longValue(); }
  return new Object[] { ka, va };
}""", cs))
cs.addMethod(CtNewMethod.make("""
public static void redirty(String[] ks) {
  for (int i = 0; i < ks.length; i++) DIRTY.put(ks[i], Boolean.TRUE);
}""", cs))
cs.addMethod(CtNewMethod.make("""
public static void ioWarn(String msg) {
  long now = System.currentTimeMillis();
  if (now - IOWARN < 60000L) return;
  IOWARN = now;
  warn(msg);
}""", cs))
# one flush (the caller holds IOLOCK): journal first, then every balance file, then the journal goes. 0.1.6 D2: a batch of ONE purse
# with no journal on disk skips the journal (one atomic rename is all-or-nothing on its own; an existing journal is always replaced by a
# superset first, so a replay never misses a key). No flush at all while RECOVER_PENDING (the start-up journal must stay). Returns the keys written,
# 0 = nothing dirty, -1 = failed (the batch is back in DIRTY; the journal, if written, stays until a later batch replaces it)
cs.addMethod(CtNewMethod.make("""
public static int flush0() {
  if (RECOVER_PENDING) return -1;
  Object[] b = takeBatch();
  if (b == null) return 0;
  String[] ks = (String[]) b[0];
  long[] vs = (long[]) b[1];
  try {
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    step();
    if (ks.length > 1 || java.nio.file.Files.exists(JOURNAL, new java.nio.file.LinkOption[0])) {
      java.util.Properties j = new java.util.Properties();
      j.setProperty("count", String.valueOf(ks.length));
      for (int i = 0; i < ks.length; i++) { j.setProperty("k." + i, ks[i]); j.setProperty("v." + i, String.valueOf(vs[i])); }
      writeProps(JOURNAL, j, "SkyyCoins unfinished save - replayed into balances/ at the next start (deleted once every balance below is written)");
    }
    step();
    for (int i = 0; i < ks.length; i++) { writeKey(ks[i], vs[i]); step(); }
    java.nio.file.Files.deleteIfExists(JOURNAL);
    return ks.length;
  } catch (Throwable t) {
    redirty(ks);
    ioWarn("could not save " + ks.length + " balance(s) (kept in memory, retried every second): " + t);
    return -1;
  }
}""", cs))
cs.addMethod(CtNewMethod.make("""
public static int flushNow() {
  synchronized (IOLOCK) { return flush0(); }
}""", cs))
# start (setup, before anything is read): an unfinished batch's journal is written back into balances/ (it is newer than or equal to
# every balance file it names), then deleted. A journal that cannot be read is kept and named in a WARN (never deleted). Returns the
# balances replayed (-1 = could not).
# 0.1.6 D2 (second fix round): the replay goes through the normal writer. foldK puts the journal's balances into memory as LOADED +
# DIRTY (under the ledger lock), then flushNow writes them: a new journal holding every key of the old one first (a superset - the old
# journal is only ever replaced by it), then the files. A replay write that fails (Avast, a locked file) leaves them DIRTY and retried
# every second like any change - never half-applied: the old or the superset journal stays on disk until every file is written.
# Only called while nothing it names is loaded (start-up, or RECOVER_PENDING where every load waits), so memory = the journal.
cs.addMethod(CtNewMethod.make("""
public static synchronized void foldK(String[] ks, long[] vs) {
  for (int i = 0; i < ks.length; i++) {
    BAL.put(ks[i], Long.valueOf(vs[i]));
    LOADED.put(ks[i], Boolean.TRUE);
    BADWARN.remove(ks[i]);
    DIRTY.put(ks[i], Boolean.TRUE);
  }
}""", cs))
# a journal that cannot be read / checked / moved aside (or is malformed): RECOVER_PENDING (every load waits, no flush overwrites it),
# retried every second by the IO thread; the 10th failure moves it aside (balances-journal.failed-<millis>.properties, loud WARN) and
# the purses go on from balances/ as they are. If even that move fails, everything stays frozen and is retried.
cs.addMethod(CtNewMethod.make("""
public static void recoverFail(Throwable t) {
  RECOVER_PENDING = true;
  RECOVER_TRIES = RECOVER_TRIES + 1;
  if (RECOVER_TRIES < 10) {
    if (RECOVER_TRIES == 1) warn("balances-journal.properties (an unfinished save from before the last stop) could not be replayed yet: " + t + " - every purse waits (coin changes refused) and nothing is saved over it; retried every second");
    return;
  }
  try {
    java.nio.file.Path keep = JOURNAL.resolveSibling("balances-journal.failed-" + System.currentTimeMillis() + ".properties");
    java.nio.file.Files.move(JOURNAL, keep, new java.nio.file.CopyOption[0]);
    RECOVER_PENDING = false;
    RECOVER_TRIES = 0;
    warn("!!! balances-journal.properties could not be replayed after 10 tries (" + t + ") - moved aside as " + keep.getFileName() + " and the purses go on from balances/ as they are. An ADMIN must check it: while the server is stopped, compare each k.<i> / v.<i> with balances/<k.<i>>.properties (a /pay in it may be only half on disk).");
  } catch (Throwable m) {
    ioWarn("balances-journal.properties still cannot be replayed or moved aside (" + t + " / " + m + ") - every purse stays frozen; retried every second");
  }
}""", cs))
# 0.1.6 D: a journal is STALE when a balance file it names was modified after the journal AND holds a different value (a file of the
# journal's own batch is written after it but holds exactly the journal's value). Returns that key, or null = safe to replay.
cs.addMethod(CtNewMethod.make("""
public static String staleKey(String[] ks, long[] vs) throws java.io.IOException {
  long jt = java.nio.file.Files.getLastModifiedTime(JOURNAL, new java.nio.file.LinkOption[0]).toMillis();
  for (int i = 0; i < ks.length; i++) {
    java.nio.file.Path f = DIR.resolve(ks[i] + ".properties");
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) continue;
    if (java.nio.file.Files.getLastModifiedTime(f, new java.nio.file.LinkOption[0]).toMillis() <= jt) continue;
    Object r = readK(ks[i]);
    if (!(r instanceof Object[])) continue;
    Object v = ((Object[]) r)[0];
    if (!(v instanceof Long) || ((Long) v).longValue() != vs[i]) return ks[i];
  }
  return null;
}""", cs))
cs.addMethod(CtNewMethod.make("""
public static int recover() {
  if (JOURNAL == null) return 0;
  try {
    if (!java.nio.file.Files.exists(JOURNAL, new java.nio.file.LinkOption[0])) { RECOVER_PENDING = false; RECOVER_TRIES = 0; return 0; }
    java.util.Properties j = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(JOURNAL, new java.nio.file.OpenOption[0]);
    try { j.load(in); } finally { in.close(); }
    int n = Integer.parseInt(j.getProperty("count", "").trim());
    String[] ks = new String[n];
    long[] vs = new long[n];
    for (int i = 0; i < n; i++) {
      ks[i] = j.getProperty("k." + i);
      if (!keyOk(ks[i])) throw new java.lang.IllegalStateException("bad key k." + i);
      vs[i] = Long.parseLong(j.getProperty("v." + i, "").trim());
      if (vs[i] < 0L) throw new java.lang.IllegalStateException("negative balance v." + i);
    }
    String stale = staleKey(ks, vs);
    if (stale != null) {
      java.nio.file.Path keep = JOURNAL.resolveSibling("balances-journal.stale-" + System.currentTimeMillis() + ".properties");
      java.nio.file.Files.move(JOURNAL, keep, new java.nio.file.CopyOption[0]);
      RECOVER_PENDING = false;
      RECOVER_TRIES = 0;
      warn("balances-journal.properties is OLDER than balances/" + stale + ".properties (another version wrote that purse after the journal - a rollback ran in between), so it was NOT replayed (that would undo newer coin changes). Kept as " + keep.getFileName() + " for an admin.");
      return 0;
    }
    foldK(ks, vs);
    RECOVER_PENDING = false;
    RECOVER_TRIES = 0;
    int w = flushNow();
    if (w >= 0) warn("the last save before the previous stop did not finish - " + n + " balance(s) written back from balances-journal.properties (no coin lost or doubled)");
    else warn("the last save before the previous stop did not finish - " + n + " balance(s) from balances-journal.properties are back in memory, but writing them failed; retried every second (the journal stays until they are written, so nothing is lost)");
    return n;
  } catch (Throwable t) {
    recoverFail(t);
    return -1;
  }
}""", cs))
# 0.1.6 D2: the IO thread's job: a pending start-up journal is retried first (under IOLOCK), then the normal flush
cs.addMethod(CtNewMethod.make("""
public static void ioTick() {
  if (RECOVER_PENDING) { synchronized (IOLOCK) { recover(); } }
  flushNow();
}""", cs))
# the IO thread's jobs (CoinIO): flush now (after a disconnect) and prefetch a purse before the world thread needs it
cs.addMethod(CtNewMethod.make("""
public static void ioRun(Runnable r) {
  java.util.concurrent.ScheduledExecutorService e = IO;
  if (e == null) return;
  try { e.execute(r); } catch (Throwable t) { }
}""", cs))
cs.addMethod(CtNewMethod.make("""
public static synchronized void setK(java.util.UUID u, String k, long v) {
  if (v < 0L) v = 0L;
  need(u, k);
  BAL.put(k, Long.valueOf(v));
  bridge().put("coins:" + u.toString(), Long.valueOf(v));
  DIRTY.put(k, Boolean.TRUE);
}""", cs))''')

# ---------- B: public ops read the purse file (once per run) BEFORE taking the ledger lock ----------
for name, body_old, body_new in (
    ("known", "  String k = pkey(u);\n  boolean r = knownK(u, k);", "  String k = pkey(u);\n  loadK(u, k);\n  boolean r = knownK(u, k);"),
    ("get", "  String k = pkey(u);\n  long r = getK(u, k);", "  String k = pkey(u);\n  loadK(u, k);\n  long r = getK(u, k);"),
    ("set", "  String k = pkey(u);\n  setK(u, k, v);", "  String k = pkey(u);\n  loadK(u, k);\n  setK(u, k, v);"),
    ("add", "  String k = pkey(u);\n  long r = addK(u, k, d);", "  String k = pkey(u);\n  loadK(u, k);\n  long r = addK(u, k, d);"),
    ("take", "  String k = pkey(u);\n  boolean ok = takeK(u, k, amount);", "  String k = pkey(u);\n  loadK(u, k);\n  boolean ok = takeK(u, k, amount);"),
):
    rep(body_old, body_new)
rep("  String kf = pkey(from);\n  String kt = pkey(to);\n  boolean ok = transferK(from, kf, to, kt, amount);",
    "  String kf = pkey(from);\n  String kt = pkey(to);\n  loadK(from, kf);\n  loadK(to, kt);\n  boolean ok = transferK(from, kf, to, kt, amount);")
# publish (CoinTask, world thread): read first, outside the lock
rep('''public static void publish(java.util.UUID u) {
  try { publishK(u, pkey(u)); } catch (Throwable t) { warn("could not publish balance for " + u + ": " + t); }
}''', '''public static void publish(java.util.UUID u) {
  try { String k = pkey(u); loadK(u, k); publishK(u, k); } catch (Throwable t) { warn("could not publish balance for " + u + ": " + t); }
}''')
# 0.1.6 D: recheck() runs after every public op, outside the ledger lock: once stopIO() ran, it writes the change at once
rep('''public static void recheck(java.util.UUID u, String k) {
  try {
    String now = pkey(u);
    if (!now.equals(k)) publishK(u, now);
  } catch (Throwable t) { }
}''', '''public static void recheck(java.util.UUID u, String k) {
  try {
    String now = pkey(u);
    if (!now.equals(k)) publishK(u, now);
  } catch (Throwable t) { }
  if (STOPPED && !DIRTY.isEmpty()) flushNow();
}''')
# 0.1.6 D: CoinTask's first sight of a profile key while online: starter coins (as before) or a publish (a prefetched purse was loaded
# without one). true = starter coins granted.
rep('''cs.addMethod(CtNewMethod.make("""
public static boolean known(java.util.UUID u) {''', '''cs.addMethod(CtNewMethod.make("""
public static boolean firstSeen(java.util.UUID u, String k, long starter) {
  if (starterK(u, k, starter)) { recheck(u, k); return true; }
  publishK(u, k);
  recheck(u, k);
  return false;
}""", cs))
cs.addMethod(CtNewMethod.make("""
public static boolean known(java.util.UUID u) {''')
# prefetch (IO thread): read the ACTIVE purse into memory without publishing (a stale key never reaches the HUD)
rep('''# after an op on key k: if the active profile changed meanwhile''',
'''# 0.1.6 B: prefetch on the IO thread (PlayerReadyEvent, CoinTick's profile switch): reads the active purse so the world thread finds it
# in memory; never publishes, never writes
cs.addMethod(CtNewMethod.make("""
public static void prefetch(java.util.UUID u) {
  try { if (u != null && DIR != null) loadK0(u, pkey(u), false); } catch (Throwable t) { }
}""", cs))
# after an op on key k: if the active profile changed meanwhile''')

# ---------- B: CoinIO (the writer's Runnable + ThreadFactory) and CoinEvents ----------
rep('''# ================= CoinConfig =================''',
'''# ================= 0.1.6 B: CoinIO - mode 0 = flush, 1 = prefetch(u); also the SkyyCoins-IO thread factory (one daemon thread) =================
cio.addInterface(pool.get("java.lang.Runnable"))
cio.addInterface(pool.get("java.util.concurrent.ThreadFactory"))
cio.addField(CtField.make("public int mode;", cio))
cio.addField(CtField.make("public java.util.UUID u;", cio))
cio.addConstructor(CtNewConstructor.make("public CoinIO(int mode, java.util.UUID u) { this.mode = mode; this.u = u; }", cio))
cio.addMethod(CtNewMethod.make("""
public Thread newThread(Runnable r) {
  Thread t = new Thread(r, "SkyyCoins-IO");
  t.setDaemon(true);
  return t;
}""", cio))
cio.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    if (this.mode == 1) {PKG}.CoinStore.prefetch(this.u);
    else {PKG}.CoinStore.ioTick();
  }} catch (Throwable t) {{ {PKG}.CoinStore.ioWarn("SkyyCoins-IO job failed: " + t); }}
}}""", cio))
# PlayerReadyEvent (world thread; fires on every world switch - a prefetch of a loaded purse is a map lookup) / PlayerDisconnectEvent
cev.addInterface(pool.get("java.util.function.Consumer"))
cev.addField(CtField.make("public boolean quit;", cev))
cev.addConstructor(CtNewConstructor.make("public CoinEvents(boolean quit) { this.quit = quit; }", cev))
cev.addMethod(CtNewMethod.make(f"""
public void accept(Object ev) {{
  try {{
    if (this.quit) {{
      {PKG}.CoinStore.ioRun(new {PKG}.CoinIO(0, null));
      return;
    }}
    {REF} r = (({PRE}) ev).getPlayerRef();
    if (r == null) return;
    {ST} st = r.getStore();
    if (st == null) return;
    {PR} pr = ({PR}) st.getComponent(r, {PR}.getComponentType());
    if (pr == null) return;
    {PKG}.CoinStore.ioRun(new {PKG}.CoinIO(1, pr.getUuid()));
  }} catch (Throwable t) {{ }}
}}""", cev))

# ================= CoinConfig =================''')

# CoinTick: a profile switch also prefetches the new purse on the IO thread (the flagged CoinTask then finds it in memory)
rep('''    {PKG}.CoinTask ct = new {PKG}.CoinTask(pr, wu);
    ct.republish = changed;''',
'''    if (changed) {PKG}.CoinStore.ioRun(new {PKG}.CoinIO(1, u));
    {PKG}.CoinTask ct = new {PKG}.CoinTask(pr, wu);
    ct.republish = changed;''')

# ---------- plugin: journal path, recover, writer start, events, shutdown flush ----------
rep('''  {PKG}.CoinConfig.FILE = getDataDirectory().resolveSibling("Skyy_SkyyCoins").resolve("config.properties");
  {PKG}.CoinConfig.load();''',
'''  {PKG}.CoinConfig.FILE = getDataDirectory().resolveSibling("Skyy_SkyyCoins").resolve("config.properties");
  {PKG}.CoinStore.JOURNAL = getDataDirectory().resolveSibling("Skyy_SkyyCoins").resolve("balances-journal.properties");
  {PKG}.CoinStore.recover();
  {PKG}.CoinConfig.load();''')
rep('''  this.ticker = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.CoinTick(), 1L, 1L, java.util.concurrent.TimeUnit.SECONDS);''',
'''  java.util.concurrent.ScheduledExecutorService io = java.util.concurrent.Executors.newSingleThreadScheduledExecutor(new {PKG}.CoinIO(0, null));
  io.scheduleWithFixedDelay(new {PKG}.CoinIO(0, null), 1000L, 1000L, java.util.concurrent.TimeUnit.MILLISECONDS);
  {PKG}.CoinStore.IO = io;
  getEventRegistry().registerGlobal({PRE}.class, new {PKG}.CoinEvents(false));
  getEventRegistry().registerGlobal({PDE}.class, new {PKG}.CoinEvents(true));
  this.ticker = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.CoinTick(), 1L, 1L, java.util.concurrent.TimeUnit.SECONDS);''')
rep('''pl.addMethod(CtNewMethod.make("""
protected void shutdown() {
  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }''',
'''# 0.1.6 B: the writer is stopped (its running flush finishes), then every dirty balance is written HERE, synchronously (one retry);
# a balance that still cannot be written is named in a WARN (memory had it - the file keeps the last written value)
cs.addMethod(CtNewMethod.make("""
public static void stopIO() {
  java.util.concurrent.ScheduledExecutorService e = IO;
  IO = null;
  if (e != null) {
    try { e.shutdown(); e.awaitTermination(10L, java.util.concurrent.TimeUnit.SECONDS); } catch (Throwable t) { }
  }
  STOPPED = true;
  flushNow();
  if (!DIRTY.isEmpty()) flushNow();
  if (!DIRTY.isEmpty()) warn("SHUTDOWN: " + DIRTY.size() + " balance(s) could not be written (" + DIRTY.keySet() + ") - their files keep the last saved value");
}""", cs))
pl.addMethod(CtNewMethod.make("""
protected void shutdown() {
  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  try { com.skyy.coins.CoinStore.stopIO(); } catch (Throwable t) { com.skyy.coins.CoinStore.warn("shutdown save failed: " + t); }''')
rep("for c in (cs, cfg, fn, task, tick, bal, pay, give, dp, dps, pl):",
    "for c in (cs, cfg, fn, cio, cev, task, tick, bal, pay, give, dp, dps, pl):")
# the build script's own --deploy branch is dropped (deploys go through tools/deploy_set.py only)
rep('''if "--deploy" in sys.argv:
    B.deploy(jar, "SkyyCoins.jar")
    B.enable_in_world("HUD mod", "Skyy:%s SkyyCoins" % VERSION, disable_prefix="Skyy:")''',
'''if "--deploy" in sys.argv:
    sys.exit("no --deploy: tools/deploy_set.py installs the whole set")''')

# ---------- 0.1.6 D (fix round): CoinTask first sight publishes; coins:fn:flush; docs ----------
rep("""    if (GRANTED.putIfAbsent(k, u) == null && {PKG}.CoinStore.starterK(u, k, 10000L)) {{
      {PKG}.CoinStore.recheck(u, k);
      if (k.equals(u.toString()))""", """    boolean first = GRANTED.putIfAbsent(k, u) == null;
    if (first && {PKG}.CoinStore.RECOVER_PENDING) {{ GRANTED.remove(k); first = false; }}
    if (first && {PKG}.CoinStore.firstSeen(u, k, 10000L)) {{
      if (k.equals(u.toString()))""")
rep("""    Object[] a = (Object[]) arg;
    java.util.UUID u = (java.util.UUID) a[0];""", """    if ("flush".equals(mode)) return Integer.valueOf({PKG}.CoinStore.flushNow());
    Object[] a = (Object[]) arg;
    java.util.UUID u = (java.util.UUID) a[0];""")
rep("""  {PKG}.CoinStore.bridge().put("coins:fn:take", new {PKG}.CoinFn("take"));
""", """  {PKG}.CoinStore.bridge().put("coins:fn:take", new {PKG}.CoinFn("take"));
  {PKG}.CoinStore.bridge().put("coins:fn:flush", new {PKG}.CoinFn("flush"));
""")
rep("""com.skyy.coins.CoinStore.bridge().remove("coins:fn:take"); } catch""",
    """com.skyy.coins.CoinStore.bridge().remove("coins:fn:take"); com.skyy.coins.CoinStore.bridge().remove("coins:fn:flush"); } catch""")
rep("""  "coins:fn:take" apply(Object[]{UUID, Long amount}) -> Boolean (false = not enough, nothing taken)
""", """  "coins:fn:take" apply(Object[]{UUID, Long amount}) -> Boolean (false = not enough, nothing taken)
  "coins:fn:flush" (0.1.6) apply(anything) -> Integer: writes every changed purse NOW (keys written; 0 = none; -1 = failed, retried
                  every second). Call it right after take / add when your own side of the move is written to disk at once.
""")

assert "saveK(" not in s.split('"""', 2)[2], "saveK is gone"
assert "Thread.sleep" not in s.split('"""', 2)[2], "no sleeps left in the code"
assert not os.path.exists(dst), dst + " already exists - delete it first (it is generated)"
open(dst, "wb").write(s.replace("\n", "\r\n").encode("utf8"))
print("wrote", dst)
