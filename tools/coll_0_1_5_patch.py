"""Derive SkyyCollections/build_skyycollections_0.1.5.py from 0.1.4 (0.1.4 is left untouched; CRLF line endings preserved).
Regenerate after editing this file: delete SkyyCollections/build_skyycollections_0.1.5.py, run python tools/coll_0_1_5_patch.py.
0.1.5 = per-profile storage, tools/PROFILES-CONTRACT.md (v1 + "Semantics of SkyyProfiles 0.1", 2026-09-23):
  rule 1  counts/<pkey>.properties instead of counts/<uuid>.properties. pkey() is the contract helper, embedded verbatim in
          CollStore (with its own bridge(); CollUnlocks.bridge() now delegates to it). Profile 1 = uuid = every existing file.
  rule 2  CollStore.DATA (count cache) and CollStore.DIRTY (flush set) are keyed by the pkey String. New countsKey(key) /
          save(key) / bumpKey(key, ...); counts(UUID) resolves pkey(u) and delegates, so the page and the unlock compute read
          the ACTIVE profile. A switch just resolves to another entry; the old profile's unsaved counts stay in DIRTY under
          their own key and are flushed to their own file (never moved to the new key).
  rule 3  coll:recipes:<uuid> stays keyed by UUID. publish() remembers the profile:epoch:<uuid> it saw (EPOCH) and the pkey it
          computed for (PUBKEY); syncEpoch(u) republishes when either differs. publish() re-reads pkey() after writing and
          recomputes (max 3 passes) if it moved meanwhile.
  rule 4  nothing applied to the live player.   rule 5  inventory never touched (profile:busy not needed).   rule 6  n/a.
Integration check against the pinned SkyyProfiles 0.1 semantics (same day, fixed in place, version kept):
  - CollSystem counted every BreakBlockEvent, also CANCELLED ones: SkyyIslands 0.3+ cancels breaks by island visitors, so a
    visitor could farm collections + recipe unlocks on someone else's island without the block ever breaking. Now the break is
    handed to the world thread (World.execute always queues, so every other system has seen the event) as a CollBreakTask
    that counts only when isCancelled() is still false (SkyySkills 0.1+ BreakTask pattern). The profile key is resolved when
    the block breaks and used for the whole count (contract 4.1: one key per operation); if a switch ran in between, the break
    still counts for the profile that broke it, silently.
  - First sight = baseline: the first counted break of a session publishes the baseline before counting, so a milestone's
    "+N recipe(s) unlocked" no longer counts every earlier unlock as new. No other first-sight action (nothing switch-like).
  - Saver tick 1 s (was 5 s): epoch/key check AND publishOnline (first publish of players who just joined) every tick, flush
    every 10th tick (10 s as before). coll:recipes:<uuid> (read by the SkyySacks Collections craft tab and the SkyyMenu
    tooltip) now follows a switch within ~1 s instead of up to 5 s, and appears ~1 s after a join instead of up to 10 s.
    Both checks are two map reads + a string concat per online player.
  - The fast-recheck chain (CollRecheck, RECHECK) is removed: it existed for "epoch bumped before the key function flips",
    which SkyyProfiles 0.1 never does (it commits the key first, then publishes the epoch). The pkey comparison in
    syncEpoch still covers the one-call window where the key already flipped and the epoch has not.
  - Unreadable counts file: 0.1.4 cached an EMPTY map, and the next flush overwrote the file = every count of that profile
    lost. Now a failed read is not cached (CollStore.BROKEN, retried at most every 2 s, warned once), breaks for that key
    are not counted meanwhile, save() never writes a key it could not load, and publish() removes coll:recipes:<uuid>
    instead of leaving another profile's list there; publishOnline retries until the file reads.
  - Saves: a failed save is put back into DIRTY after the flush loop (0.1.4 dropped it: lost until that profile's next break
    or forever on shutdown). All counts-file reads and writes hold CollIO.class (leaf lock): the shutdown flush can no longer
    race a still-running saver flush on the same .tmp file, and on Windows a reader can no longer fail a replace. The
    replace is retried 5x 20 ms (sharing violations) before the save counts as failed.
  - Lock order: the counts file is loaded BEFORE the publish (CollUnlocks.class) and bump (CollStore.class) monitors, so the
    world thread never waits on disk I/O inside them. pkey() may take SkyyProfiles' store lock on a cache miss; SkyyProfiles
    never calls out while holding it, and CollIO.class / System.class (bridge()) are leaf locks, so no cycle is possible.
Without SkyyProfiles: pkey = uuid, epoch absent (-1 every time) -> same files, same bridge output as 0.1.4 (plus the fixes).
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyCollections", "build_skyycollections_0.1.4.py")
dst = os.path.join(ROOT, "SkyyCollections", "build_skyycollections_0.1.5.py")
assert not os.path.exists(dst), "refusing to overwrite " + dst
raw = open(src, encoding="utf8", newline="").read()
CRLF = "\r\n" in raw
s = raw.replace("\r\n", "\n")

def rep(old, new, count=1):
    global s
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:80])
    s = s.replace(old, new)

# ---------------- docstring + version ----------------
rep('''"""SkyyCollections 0.1.4 - build script
0.1.4: command rules''', '''"""SkyyCollections 0.1.5 - build script
0.1.5: per-profile storage (tools/PROFILES-CONTRACT.md). Counts are kept per SkyyProfiles profile: counts/<pkey>.properties,
       pkey = the contract helper (profile 1 = <uuid> = every existing file, profile N = <uuid>-pN); the count cache and the
       dirty set are keyed by that pkey String, so a switch just resolves to another entry and the old profile's unsaved
       counts are flushed under their own key. coll:recipes:<uuid> stays keyed by UUID (it describes the ACTIVE profile) and
       is republished when profile:epoch:<uuid> or the active pkey differs from the last publish. Without SkyyProfiles:
       pkey = uuid, no epoch -> same files and bridge output as 0.1.4.
       Integration check against the pinned SkyyProfiles 0.1 semantics (end of PROFILES-CONTRACT.md), fixed in place:
       - Breaks are counted in a World.execute task and only when BreakBlockEvent.isCancelled() is still false (SkyySkills
         pattern). Before, breaks cancelled by SkyyIslands' island protection still counted: visitors could farm collections
         and recipe unlocks on someone else's island. The profile key is resolved when the block breaks.
       - Saver tick 1 s (was 5 s): epoch/key check + first publish of players who just joined; flush every 10 s as before.
         coll:recipes:<uuid> (SkyySacks Collections craft tab, SkyyMenu tooltip) follows a switch within ~1 s and appears
         ~1 s after a join. The first publish of a session is the baseline; the first counted break publishes it first, so a
         milestone's "+N recipe(s)" counts only new unlocks. The CollRecheck fast rechecks are gone (SkyyProfiles flips its
         key function before it bumps the epoch, so a new epoch always comes with the new key).
       - An unreadable counts file is no longer cached as empty (the next flush overwrote it = all counts of that profile
         lost): retried every 2 s while needed, breaks meanwhile not counted, file left untouched, coll:recipes:<uuid>
         removed until it reads. A failed save is retried at the next flush. Reads and writes share one lock (CollIO) and the
         replace is retried 5x 20 ms. No disk I/O inside the publish or bump monitors.
       Derived by tools/coll_0_1_5_patch.py.
0.1.4: command rules''')
rep('''Run:   python build_skyycollections_0.1.4.py            -> SkyyCollections/SkyyCollections-0.1.4.jar
       python build_skyycollections_0.1.4.py --deploy   -> also''', '''Run:   python build_skyycollections_0.1.5.py            -> SkyyCollections/SkyyCollections-0.1.5.jar
       python build_skyycollections_0.1.5.py --deploy   -> also''')
rep('VERSION = "0.1.4"', 'VERSION = "0.1.5"')
# CollIO = counts-file lock (read + write); CollBreakTask = deferred, cancel-checked break count (top-level classes: javassist has
# no inner/anonymous classes)
rep('''sav   = pool.makeClass(PKG + ".CollSaver")
''', '''sav   = pool.makeClass(PKG + ".CollSaver")
cio   = pool.makeClass(PKG + ".CollIO")
brk   = pool.makeClass(PKG + ".CollBreakTask")
''')
rep('''for c in (store, unl, sysc, sav, ccmp, page, ulc, rlc, cmd, pl):''',
    '''for c in (cio, store, unl, brk, sysc, sav, ccmp, page, ulc, rlc, cmd, pl):''')
# deferred break counting (SkyySkills 0.1+ BreakTask pattern): Store.getExternalData -> EntityStore.getWorld, World.execute,
# CancellableEcsEvent.isCancelled (BreakBlockEvent extends it; SkyyIslands' GuardBreak calls setCancelled)
rep('''LOG = "com.hypixel.hytale.logger.HytaleLogger"
''', '''LOG = "com.hypixel.hytale.logger.HytaleLogger"
EST = "com.hypixel.hytale.server.core.universe.world.storage.EntityStore"
CEV = "com.hypixel.hytale.component.system.CancellableEcsEvent"
''')
rep('''(AC, "requirePermission"), (AC, "addAliases")):''', '''(AC, "requirePermission"), (AC, "addAliases"),
             (ST, "getExternalData"), (EST, "getWorld"), (WLD, "execute"), (CEV, "isCancelled"), (PR, "isValid")):''')

# ---------------- CollStore: bridge() + contract pkey() (before every caller) ----------------
rep('''public static void warn(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyCollections] " + msg); } catch (Throwable t) { }
}""", store))
''', '''public static void warn(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyCollections] " + msg); } catch (Throwable t) { }
}""", store))
store.addMethod(CtNewMethod.make("""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""", store))
# tools/PROFILES-CONTRACT.md storage-key helper, verbatim: active profile's key, uuid.toString() (= profile 1) without SkyyProfiles
store.addMethod(CtNewMethod.make("""
public static String pkey(java.util.UUID u) {
  try {
    Object f = bridge().get("profile:fn:key");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(u);
      if (r instanceof String && ((String) r).length() > 0) return (String) r;
    }
  } catch (Throwable t) { }
  return u.toString();
}""", store))
# per pkey: when its counts file last failed to read (Long millis). A failed read is never cached as empty; retried at most every 2 s
store.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap BROKEN = new java.util.concurrent.ConcurrentHashMap();", store))
# Every counts-file read and write holds CollIO.class (a leaf lock: nothing else is taken inside it). On Windows an open reader
# makes a concurrent replace fail, and the shutdown flush can overlap a saver flush that is still running (same .tmp file).
# The replace is retried 5x 20 ms (sharing violations from scanners/indexers) before the save counts as failed.
cio.addMethod(CtNewMethod.make("""
public static synchronized java.util.Properties read(java.nio.file.Path f) throws java.io.IOException {
  java.util.Properties p = new java.util.Properties();
  if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {
    java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
  }
  return p;
}""", cio))
cio.addMethod(CtNewMethod.make("""
public static synchronized void write(java.nio.file.Path dir, String key, java.util.Properties p) throws java.io.IOException {
  java.nio.file.Files.createDirectories(dir, new java.nio.file.attribute.FileAttribute[0]);
  java.nio.file.Path tmp = dir.resolve(key + ".properties.tmp");
  java.io.OutputStream out = java.nio.file.Files.newOutputStream(tmp, new java.nio.file.OpenOption[0]);
  try { p.store(out, "SkyyCollections"); } finally { out.close(); }
  java.nio.file.Path f = dir.resolve(key + ".properties");
  java.io.IOException last = null;
  for (int i = 0; i < 5; i++) {
    try {
      java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
      return;
    } catch (java.nio.file.FileSystemException e) {
      last = e;
    }
    try { Thread.sleep(20L); } catch (InterruptedException ie) { }
  }
  throw last;
}""", cio))
''')

# ---------------- CollStore: cache + files keyed by pkey (rules 1 + 2) ----------------
rep('''public static java.util.Map counts(java.util.UUID u) {
  java.util.Map m = (java.util.Map) DATA.get(u);
  if (m != null) return m;
  m = new java.util.concurrent.ConcurrentHashMap();
  try {
    java.nio.file.Path f = DIR.resolve(u.toString() + ".properties");
    if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {
      java.util.Properties p = new java.util.Properties();
      java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
      try { p.load(in); } finally { in.close(); }
      java.util.Enumeration en = p.propertyNames();
      while (en.hasMoreElements()) {
        String k = (String) en.nextElement();
        try { m.put(k, Long.valueOf(Long.parseLong(p.getProperty(k).trim()))); } catch (Throwable t) { }
      }
    }
  } catch (Throwable t) { warn("could not load counts for " + u + ": " + t); }
  java.util.Map prev = (java.util.Map) DATA.putIfAbsent(u, m);
  return prev != null ? prev : m;
}""", store))
''', '''public static java.util.Map countsKey(String key) {
  java.util.Map m = (java.util.Map) DATA.get(key);
  if (m != null) return m;
  m = new java.util.concurrent.ConcurrentHashMap();
  Long bad = (Long) BROKEN.get(key);
  if (bad != null && System.currentTimeMillis() - bad.longValue() < 2000L) return m;
  try {
    java.util.Properties p = com.skyy.collections.CollIO.read(DIR.resolve(key + ".properties"));
    java.util.Enumeration en = p.propertyNames();
    while (en.hasMoreElements()) {
      String k = (String) en.nextElement();
      try { m.put(k, Long.valueOf(Long.parseLong(p.getProperty(k).trim()))); } catch (Throwable t) { }
    }
  } catch (Throwable t) {
    if (BROKEN.put(key, Long.valueOf(System.currentTimeMillis())) == null) warn("could not read counts/" + key + ".properties - breaks for that profile are not counted and the file is left untouched until it reads again (retried every 2 s while needed): " + t);
    return new java.util.concurrent.ConcurrentHashMap();
  }
  if (BROKEN.remove(key) != null) warn("counts/" + key + ".properties reads again");
  java.util.Map prev = (java.util.Map) DATA.putIfAbsent(key, m);
  return prev != null ? prev : m;
}""", store))
store.addMethod(CtNewMethod.make("""
public static java.util.Map counts(java.util.UUID u) {
  return countsKey(pkey(u));
}""", store))
''')
# a key that could not be loaded is not in DATA -> nothing to write (true); a failed write returns false (flushDirty re-queues it)
rep('''public static void save(java.util.UUID u) {
  try {
    java.util.Map m = (java.util.Map) DATA.get(u);
    if (m == null) return;
    java.util.Properties p = new java.util.Properties();
    java.util.Iterator it = m.entrySet().iterator();
    while (it.hasNext()) {
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      p.setProperty((String) e.getKey(), String.valueOf(((Long) e.getValue()).longValue()));
    }
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = DIR.resolve(u.toString() + ".properties.tmp");
    java.io.OutputStream out = java.nio.file.Files.newOutputStream(tmp, new java.nio.file.OpenOption[0]);
    try { p.store(out, "SkyyCollections"); } finally { out.close(); }
    java.nio.file.Files.move(tmp, DIR.resolve(u.toString() + ".properties"), new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
  } catch (Throwable t) { warn("could not save counts for " + u + ": " + t); }
}""", store))
''', '''public static boolean save(String key) {
  try {
    java.util.Map m = (java.util.Map) DATA.get(key);
    if (m == null) return true;
    java.util.Properties p = new java.util.Properties();
    java.util.Iterator it = m.entrySet().iterator();
    while (it.hasNext()) {
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      p.setProperty((String) e.getKey(), String.valueOf(((Long) e.getValue()).longValue()));
    }
    com.skyy.collections.CollIO.write(DIR, key, p);
    return true;
  } catch (Throwable t) { warn("could not save counts/" + key + ".properties (retried at the next flush): " + t); return false; }
}""", store))
''')
# failed saves go back into DIRTY only AFTER the loop (re-adding inside it could make the weakly consistent iterator see the key
# again and spin while the file stays unwritable)
rep('''public static void flushDirty() {
  java.util.Iterator it = DIRTY.keySet().iterator();
  while (it.hasNext()) {
    java.util.UUID u = (java.util.UUID) it.next();
    it.remove();
    save(u);
  }
}""", store))
''', '''public static void flushDirty() {
  java.util.ArrayList failed = new java.util.ArrayList();
  java.util.Iterator it = DIRTY.keySet().iterator();
  while (it.hasNext()) {
    String key = (String) it.next();
    it.remove();
    if (!save(key)) failed.add(key);
  }
  for (int i = 0; i < failed.size(); i++) DIRTY.put(failed.get(i), Boolean.TRUE);
}""", store))
''')
rep('''public static synchronized int bump(java.util.UUID u, String id, long n) {
  java.util.Map m = counts(u);
  Long v = (Long) m.get(id);
  long oldv = v == null ? 0L : v.longValue();
  long newv = oldv + n;
  m.put(id, Long.valueOf(newv));
  DIRTY.put(u, Boolean.TRUE);
  int ot = tierOf(oldv); int nt = tierOf(newv);
  return nt > ot ? nt : 0;
}""", store))
''', '''public static synchronized int bumpLocked(String key, String id, long n) {
  java.util.Map m = countsKey(key);
  Long v = (Long) m.get(id);
  long oldv = v == null ? 0L : v.longValue();
  long newv = oldv + n;
  m.put(id, Long.valueOf(newv));
  DIRTY.put(key, Boolean.TRUE);
  int ot = tierOf(oldv); int nt = tierOf(newv);
  return nt > ot ? nt : 0;
}""", store))
# the counts file is loaded BEFORE the bump monitor (the world thread never waits on disk I/O while holding it)
store.addMethod(CtNewMethod.make("""
public static int bumpKey(String key, String id, long n) {
  countsKey(key);
  return bumpLocked(key, id, n);
}""", store))
''')

# ---------------- CollUnlocks: epoch-aware publishing (rule 3) ----------------
rep('''unl.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap PUBLISHED = new java.util.concurrent.ConcurrentHashMap();", unl))
unl.addMethod(CtNewMethod.make("""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""", unl))
''', '''unl.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap PUBLISHED = new java.util.concurrent.ConcurrentHashMap();", unl))
# per UUID: profile:epoch value (Long, -1 = absent) and pkey (String) the last publish was computed for
unl.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap EPOCH = new java.util.concurrent.ConcurrentHashMap();", unl))
unl.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap PUBKEY = new java.util.concurrent.ConcurrentHashMap();", unl))
unl.addMethod(CtNewMethod.make(f"""
public static java.util.Map bridge() {{
  return {PKG}.CollStore.bridge();
}}""", unl))
unl.addMethod(CtNewMethod.make("""
public static long epochOf(java.util.UUID u) {
  try {
    Object o = bridge().get("profile:epoch:" + u.toString());
    if (o instanceof Number) return ((Number) o).longValue();
    if (o != null) return Long.parseLong(String.valueOf(o).trim());
  } catch (Throwable t) { }
  return -1L;
}""", unl))
''')
rep('''public static int publish(java.util.UUID u) {{
  try {{
    java.util.TreeSet ids = compute({PKG}.CollStore.counts(u));
    StringBuilder sb = new StringBuilder();
    java.util.Iterator it = ids.iterator();
    while (it.hasNext()) {{ if (sb.length() > 0) sb.append(','); sb.append((String) it.next()); }}
    bridge().put("coll:recipes:" + u.toString(), sb.toString());
    PUBLISHED.put(u, Integer.valueOf(ids.size()));
    return ids.size();
  }} catch (Throwable t) {{ {PKG}.CollStore.warn("publish failed for " + u + ": " + t); return 0; }}
}}""", unl))
''', '''public static synchronized int publishLocked(java.util.UUID u) {{
  try {{
    int n = 0;
    for (int pass = 0; pass < 3; pass++) {{
      long ep = epochOf(u);
      String key = {PKG}.CollStore.pkey(u);
      java.util.Map counts = {PKG}.CollStore.countsKey(key);
      if (!{PKG}.CollStore.DATA.containsKey(key)) {{
        bridge().remove("coll:recipes:" + u.toString());
        PUBLISHED.remove(u);
        EPOCH.remove(u);
        PUBKEY.remove(u);
        return 0;
      }}
      java.util.TreeSet ids = compute(counts);
      StringBuilder sb = new StringBuilder();
      java.util.Iterator it = ids.iterator();
      while (it.hasNext()) {{ if (sb.length() > 0) sb.append(','); sb.append((String) it.next()); }}
      bridge().put("coll:recipes:" + u.toString(), sb.toString());
      PUBLISHED.put(u, Integer.valueOf(ids.size()));
      EPOCH.put(u, Long.valueOf(ep));
      PUBKEY.put(u, key);
      n = ids.size();
      if (key.equals({PKG}.CollStore.pkey(u))) break;
    }}
    return n;
  }} catch (Throwable t) {{ {PKG}.CollStore.warn("publish failed for " + u + ": " + t); return 0; }}
}}""", unl))
# The counts file is loaded BEFORE the publish monitor, so the monitor never waits on disk I/O (safe from the world thread).
# A key whose counts file cannot be read publishes nothing: coll:recipes:<uuid> is removed (never another profile's list) and the
# player is dropped from PUBLISHED, so publishOnline retries every tick until it reads.
unl.addMethod(CtNewMethod.make(f"""
public static int publish(java.util.UUID u) {{
  try {{ {PKG}.CollStore.countsKey({PKG}.CollStore.pkey(u)); }} catch (Throwable t) {{ }}
  return publishLocked(u);
}}""", unl))
# Republish an already-published player when the active profile changed since the last publish: profile:epoch:<uuid> moved or
# pkey() now differs from the key publish computed for. SkyyProfiles 0.1 commits its key function BEFORE it bumps the epoch
# (PROFILES-CONTRACT.md "Key flip timing"), so a moved epoch always comes with the new key; the pkey comparison covers the
# one-call window where the key already flipped and the epoch has not. Epoch bumps that keep the key (first profile, a new
# profile before its switch, setclass) republish the same list: harmless. Never-published players are left to baseline() /
# publishOnline(): their first publish is the baseline (absent -> value is not a change), nothing switch-like happens.
unl.addMethod(CtNewMethod.make(f"""
public static boolean syncEpoch(java.util.UUID u) {{
  try {{
    if (u == null || !PUBLISHED.containsKey(u)) return false;
    Long seen = (Long) EPOCH.get(u);
    String key = (String) PUBKEY.get(u);
    if (seen != null && seen.longValue() == epochOf(u) && key != null && key.equals({PKG}.CollStore.pkey(u))) return false;
    publish(u);
    return true;
  }} catch (Throwable t) {{ return false; }}
}}""", unl))
# first sight of a player in this session publishes the baseline; after that only a changed epoch/key republishes
unl.addMethod(CtNewMethod.make("""
public static void baseline(java.util.UUID u) {
  if (u == null) return;
  if (!PUBLISHED.containsKey(u)) publish(u); else syncEpoch(u);
}""", unl))
unl.addMethod(CtNewMethod.make("""
public static void checkEpochs() {
  try {
    java.util.Iterator it = new java.util.ArrayList(PUBLISHED.keySet()).iterator();
    while (it.hasNext()) syncEpoch((java.util.UUID) it.next());
  } catch (Throwable t) { }
}""", unl))
''')
rep('''    PUBLISHED.keySet().retainAll(online);''', '''    PUBLISHED.keySet().retainAll(online);
    EPOCH.keySet().retainAll(online);
    PUBKEY.keySet().retainAll(online);''')

# ---------------- CollBreakTask: count on the world thread AFTER every system saw the event, only if it was not cancelled ----------------
# (SkyyIslands cancels visitors' breaks; 0.1.4 counted them anyway.) Key resolved at break time, used for the whole count.
rep('''# ================= CollSystem (BreakBlockEvent listener) =================
''', '''# ================= CollBreakTask (deferred count, SkyySkills BreakTask pattern) =================
# World.execute always queues, so when run() starts every other system (SkyyIslands' GuardBreak, whose order relative to ours is
# unknown) has handled the event. The engine creates a new BreakBlockEvent per break, so holding it is safe.
brk.addInterface(pool.get("java.lang.Runnable"))
brk.addField(CtField.make(f"public {BBE} ev;", brk))
brk.addField(CtField.make(f"public {PR} pr;", brk))
brk.addField(CtField.make("public java.util.UUID u;", brk))
brk.addField(CtField.make("public String key;", brk))
brk.addField(CtField.make("public String id;", brk))
brk.addConstructor(CtNewConstructor.make(f"""
public CollBreakTask({BBE} ev, {PR} pr, java.util.UUID u, String key, String id) {{
  this.ev = ev; this.pr = pr; this.u = u; this.key = key; this.id = id;
}}""", brk))
# key = the profile that broke the block. If a switch ran between the break and this task (both world-thread tasks), the break
# still counts for that profile, silently (no milestone line, no publish: coll:recipes describes the ACTIVE profile).
brk.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    if (this.ev.isCancelled()) return;
    boolean active = this.key.equals({PKG}.CollStore.pkey(this.u));
    if (active) {PKG}.CollUnlocks.baseline(this.u);
    int newTier = {PKG}.CollStore.bumpKey(this.key, this.id, 1L);
    if (newTier <= 0 || !active) return;
    Object was = {PKG}.CollUnlocks.PUBLISHED.get(this.u);
    int before = was instanceof Integer ? ((Integer) was).intValue() : 0;
    int now = {PKG}.CollUnlocks.publish(this.u);
    if (this.pr != null && this.pr.isValid()) this.pr.sendMessage({MSG}.raw("Collection milestone! " + {PKG}.CollStore.pretty(this.id) + " " + {PKG}.CollStore.roman(newTier) + (now > before ? "  +" + (now - before) + " recipe(s) unlocked - /craft" : "")));
  }} catch (Throwable t) {{ {PKG}.CollStore.warn("break count failed: " + t); }}
}}""", brk))

# ================= CollSystem (BreakBlockEvent listener) =================
''')
rep('''    java.util.UUID u = pr.getUuid();
    int newTier = {PKG}.CollStore.bump(u, id, 1L);
    if (newTier > 0) {{
      int before = {PKG}.CollUnlocks.PUBLISHED.containsKey(u) ? ((Integer) {PKG}.CollUnlocks.PUBLISHED.get(u)).intValue() : 0;
      int now = {PKG}.CollUnlocks.publish(u);
      pr.sendMessage({MSG}.raw("Collection milestone! " + {PKG}.CollStore.pretty(id) + " " + {PKG}.CollStore.roman(newTier) + (now > before ? "  +" + (now - before) + " recipe(s) unlocked - /craft" : "")));
    }}
''', '''    Object ext = st.getExternalData();
    if (!(ext instanceof {EST})) return;
    {WLD} w = (({EST}) ext).getWorld();
    if (w == null) return;
    java.util.UUID u = pr.getUuid();
    w.execute(new {PKG}.CollBreakTask(e, pr, u, {PKG}.CollStore.pkey(u), id));
''')

# ---------------- CollSaver: 1 s tick = epoch/key check + first publish of new players; flush every 10th tick (10 s, as before) ----------------
rep('''sav.addConstructor(CtNewConstructor.make("public CollSaver() { }", sav))
sav.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{ {PKG}.CollStore.flushDirty(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.CollUnlocks.publishOnline(); }} catch (Throwable t) {{ }}
}}""", sav))''', '''sav.addField(CtField.make("public int ticks;", sav))
sav.addConstructor(CtNewConstructor.make("public CollSaver() { }", sav))
sav.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{ {PKG}.CollUnlocks.checkEpochs(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.CollUnlocks.publishOnline(); }} catch (Throwable t) {{ }}
  this.ticks = this.ticks + 1;
  if (this.ticks % 10 != 0) return;
  try {{ {PKG}.CollStore.flushDirty(); }} catch (Throwable t) {{ }}
}}""", sav))''')
rep('''scheduleAtFixedRate(new {PKG}.CollSaver(), 10L, 10L, java.util.concurrent.TimeUnit.SECONDS);''',
    '''scheduleAtFixedRate(new {PKG}.CollSaver(), 1L, 1L, java.util.concurrent.TimeUnit.SECONDS);''')
rep('''ready - break blocks, /collections to view, unlocks auto=''', '''ready - break blocks, /collections to view, per-profile counts, unlocks auto=''')

# ---------------- manifest ----------------
rep('''Collection tiers unlock recipes for the SkyySacks craft page (auto rule + unlocks.properties).",''',
    '''Collection tiers unlock recipes for the SkyySacks craft page (auto rule + unlocks.properties). Counts are per profile when SkyyProfiles is installed.",''')

out = s.replace("\n", "\r\n") if CRLF else s
open(dst, "w", encoding="utf8", newline="").write(out)
print("wrote", dst, "(CRLF)" if CRLF else "(LF)")
