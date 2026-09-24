"""Derive SkyyCollections/build_skyycollections_0.1.5.py from 0.1.4 (0.1.4 is left untouched; CRLF line endings preserved).
0.1.5 = per-profile storage, tools/PROFILES-CONTRACT.md (v1, 2026-09-23):
  rule 1  counts/<pkey>.properties instead of counts/<uuid>.properties. pkey() is the contract helper, embedded verbatim in
          CollStore (with its own bridge(); CollUnlocks.bridge() now delegates to it). Profile 1 = uuid = every existing file.
  rule 2  CollStore.DATA (count cache) and CollStore.DIRTY (flush set) are keyed by the pkey String. New countsKey(key) /
          save(key) / bumpKey(key, ...); counts(UUID) and bump(UUID, ...) resolve pkey(u) and delegate, so the page, the
          break handler and the unlock compute all read the ACTIVE profile.
  rule 3  coll:recipes:<uuid> stays keyed by UUID. publish() remembers the profile:epoch:<uuid> it saw (EPOCH) and the pkey it
          computed for (PUBKEY); syncEpoch(u) republishes when either differs. Checked by the saver tick (period 10 s -> 5 s,
          flush + first publish of new players still every 2nd tick = 10 s as before) and before each counted block break
          (so a milestone right after a switch compares against the new profile's unlocks). The pkey comparison is a safety
          net if SkyyProfiles bumps the epoch before its key function returns the new key. publish() is now synchronized so
          the last publish always sees the newest counts (tick thread vs world thread).
  rule 4  nothing applied to the live player.   rule 5  inventory never touched.   rule 6  n/a.
Without SkyyProfiles: pkey = uuid, epoch absent (-1 every time) -> same files, same bridge output, same messages as 0.1.4.
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
       dirty set are keyed by that pkey String. coll:recipes:<uuid> stays keyed by UUID (it describes the ACTIVE profile) and is
       republished when profile:epoch:<uuid> changes (or the active pkey differs from the last published one): checked every
       5 s by the saver tick (was 10 s; flush + first publish still every 2nd tick = 10 s) and before each counted block break.
       publish() is synchronized. Without SkyyProfiles: pkey = uuid, no epoch -> behaviour identical to 0.1.4.
       Derived by tools/coll_0_1_5_patch.py.
0.1.4: command rules''')
rep('''Run:   python build_skyycollections_0.1.4.py            -> SkyyCollections/SkyyCollections-0.1.4.jar
       python build_skyycollections_0.1.4.py --deploy   -> also''', '''Run:   python build_skyycollections_0.1.5.py            -> SkyyCollections/SkyyCollections-0.1.5.jar
       python build_skyycollections_0.1.5.py --deploy   -> also''')
rep('VERSION = "0.1.4"', 'VERSION = "0.1.5"')

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
''')

# ---------------- CollStore: cache + files keyed by pkey (rules 1 + 2) ----------------
rep('''public static java.util.Map counts(java.util.UUID u) {
  java.util.Map m = (java.util.Map) DATA.get(u);
  if (m != null) return m;
  m = new java.util.concurrent.ConcurrentHashMap();
  try {
    java.nio.file.Path f = DIR.resolve(u.toString() + ".properties");''', '''public static java.util.Map countsKey(String key) {
  java.util.Map m = (java.util.Map) DATA.get(key);
  if (m != null) return m;
  m = new java.util.concurrent.ConcurrentHashMap();
  try {
    java.nio.file.Path f = DIR.resolve(key + ".properties");''')
rep('''  } catch (Throwable t) { warn("could not load counts for " + u + ": " + t); }
  java.util.Map prev = (java.util.Map) DATA.putIfAbsent(u, m);
  return prev != null ? prev : m;
}""", store))
''', '''  } catch (Throwable t) { warn("could not load counts for " + key + ": " + t); }
  java.util.Map prev = (java.util.Map) DATA.putIfAbsent(key, m);
  return prev != null ? prev : m;
}""", store))
store.addMethod(CtNewMethod.make("""
public static java.util.Map counts(java.util.UUID u) {
  return countsKey(pkey(u));
}""", store))
''')
rep('''public static void save(java.util.UUID u) {
  try {
    java.util.Map m = (java.util.Map) DATA.get(u);''', '''public static void save(String key) {
  try {
    java.util.Map m = (java.util.Map) DATA.get(key);''')
rep('''    java.nio.file.Path tmp = DIR.resolve(u.toString() + ".properties.tmp");''',
    '''    java.nio.file.Path tmp = DIR.resolve(key + ".properties.tmp");''')
rep('''    java.nio.file.Files.move(tmp, DIR.resolve(u.toString() + ".properties"), new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
  } catch (Throwable t) { warn("could not save counts for " + u + ": " + t); }''',
    '''    java.nio.file.Files.move(tmp, DIR.resolve(key + ".properties"), new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
  } catch (Throwable t) { warn("could not save counts for " + key + ": " + t); }''')
rep('''    java.util.UUID u = (java.util.UUID) it.next();
    it.remove();
    save(u);''', '''    String key = (String) it.next();
    it.remove();
    save(key);''')
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
''', '''public static synchronized int bumpKey(String key, String id, long n) {
  java.util.Map m = countsKey(key);
  Long v = (Long) m.get(id);
  long oldv = v == null ? 0L : v.longValue();
  long newv = oldv + n;
  m.put(id, Long.valueOf(newv));
  DIRTY.put(key, Boolean.TRUE);
  int ot = tierOf(oldv); int nt = tierOf(newv);
  return nt > ot ? nt : 0;
}""", store))
store.addMethod(CtNewMethod.make("""
public static int bump(java.util.UUID u, String id, long n) {
  return bumpKey(pkey(u), id, n);
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
''', '''public static synchronized int publish(java.util.UUID u) {{
  try {{
    long ep = epochOf(u);
    String key = {PKG}.CollStore.pkey(u);
    java.util.TreeSet ids = compute({PKG}.CollStore.countsKey(key));
    StringBuilder sb = new StringBuilder();
    java.util.Iterator it = ids.iterator();
    while (it.hasNext()) {{ if (sb.length() > 0) sb.append(','); sb.append((String) it.next()); }}
    bridge().put("coll:recipes:" + u.toString(), sb.toString());
    PUBLISHED.put(u, Integer.valueOf(ids.size()));
    EPOCH.put(u, Long.valueOf(ep));
    PUBKEY.put(u, key);
    return ids.size();
  }} catch (Throwable t) {{ {PKG}.CollStore.warn("publish failed for " + u + ": " + t); return 0; }}
}}""", unl))
# republish an already-published player when the active profile changed (epoch bump, or a different pkey) since the last publish
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

# ---------------- CollSystem: sync before counting, so the milestone "+N recipes" compares against the new profile ----------------
rep('''    java.util.UUID u = pr.getUuid();
    int newTier = {PKG}.CollStore.bump(u, id, 1L);''', '''    java.util.UUID u = pr.getUuid();
    {PKG}.CollUnlocks.syncEpoch(u);
    int newTier = {PKG}.CollStore.bump(u, id, 1L);''')

# ---------------- CollSaver: 5 s tick = epoch check; flush + first publish every 2nd tick (10 s, as before) ----------------
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
  this.ticks = this.ticks + 1;
  if (this.ticks % 2 != 0) return;
  try {{ {PKG}.CollStore.flushDirty(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.CollUnlocks.publishOnline(); }} catch (Throwable t) {{ }}
}}""", sav))''')
rep('''scheduleAtFixedRate(new {PKG}.CollSaver(), 10L, 10L, java.util.concurrent.TimeUnit.SECONDS);''',
    '''scheduleAtFixedRate(new {PKG}.CollSaver(), 5L, 5L, java.util.concurrent.TimeUnit.SECONDS);''')
rep('''ready - break blocks, /collections to view, unlocks auto=''', '''ready - break blocks, /collections to view, per-profile counts, unlocks auto=''')

# ---------------- manifest ----------------
rep('''Collection tiers unlock recipes for the SkyySacks craft page (auto rule + unlocks.properties).",''',
    '''Collection tiers unlock recipes for the SkyySacks craft page (auto rule + unlocks.properties). Counts are per profile when SkyyProfiles is installed.",''')

out = s.replace("\n", "\r\n") if CRLF else s
open(dst, "w", encoding="utf8", newline="").write(out)
print("wrote", dst, "(CRLF)" if CRLF else "(LF)")
