"""Derive SkyySkills/build_skyyskills_0.4.32.py from the LIVE generated SkyySkills/build_skyyskills_0.4.31.py (= the tools/deploy_set.py SET
pin; 0.4.31 came from 0.4.30 by tools/skills_0_4_31_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). rep(old, new) with asserted single anchors; 0.4.31 stays untouched, its line endings are kept.
Run:  python tools/skills_0_4_32_patch.py   then   python SkyySkills/build_skyyskills_0.4.32.py   (NO --deploy: coordinated deploy)
Test: python SkyySkills/test_skyyskills_0.4.32.py   (bare JVM, -Xverify:all)

0.4.32 (2026-10-13) = LAG FIXES from the code audit (research/Code-Structure-Audit.md findings 2, 9, 11 + pack-wide pattern 1; Skyy
2026-10-13: "During/ before we consolidate the mods together, lets audit the code structure, and make sure they are working together in
the smoothest easiest lag free way possible"):
  (A) LOCK-FREE BRIDGE: SkillStore.bridge() and MoveSync.bridge() cache the skyy.bridge map in a static volatile BRIDGE field (the
      tools/skyycfg.py kit snippet: bridge0 creates the map under synchronized(System.class) once, exactly as before). MoveSync's body
      comes from the shared tools/skyymove.py; this build swaps its bridge() body (setBody) - the shared file is unchanged.
  (B) LEADERBOARD INDEX (finding 2): SkillTop.all no longer reads every player file on the caller (the world thread of /skills Top 10,
      100-500 ms at 1000 profiles). SkillStore.TOPIDX (profile key -> { name, xp per slot }) is SEEDED at start on the private writer
      (seedTop: the same files, the same parse 0.4.31 used), kept current by install() (a loaded profile) and addK() (an XP gain), and
      refreshed from disk every 5 minutes on the writer (a profile file changed / deleted by hand or by another mod shows there; 0.4.31
      re-read every 30 s on the caller); all() builds the rows from it + the loaded profiles (DATA, unchanged). Until the first seed is
      done the list is built from what is known and not cached. IO not running (harness / before setup) = the seed runs on the caller.
  (C) PRIVATE WRITER "SkyySkills-IO" (finding 9; SkillIO, one daemon thread, not HytaleServer.SCHEDULED_EXECUTOR): the 10 s dirty-player
      save (flushDirty), the 60 s placed-blocks save, the class / own level curve record flushes and the leaderboard seed run there;
      one queued job per kind. OwnCurve's save of the new paid marker right after a payout STAYS synchronous on the world thread
      (0.4.31's write-ahead: a crash cannot pay the same level reward twice; rare and small - fix review 2026-10-13). SkillStore.moveRetry's
      20 ms retries therefore never sleep on a world thread or the shared scheduler. Shutdown stops the writer (up to 5 s) and then saves
      synchronously, as 0.4.31 did.
  (D) PLACED BLOCKS (finding 11): PlacedStore keeps each world's positions in a PlacedSet - primitive long arrays (an open-addressing hash
      table + an insertion-ordered linked list = the LinkedHashSet's LRU order, cap 400000) instead of 400k boxed Longs; the save copies a
      long[] under the lock and writes outside it (file format unchanged: count + longs in order). A world's file is read OFF the lock and
      off the world thread: SkillTick queues every loaded world's read on SkyySkills-IO (preload); a world first touched before that still
      reads on the caller, outside the lock.
  (E) FELLED TREES: FellWatch keeps ONE FellRead per watch (reset + section cache cleared each poll instead of a new reader + map), and the
      default poll is 500 ms (fell.pollMs: 200 -> 500). PollMig (PROJECT-RULES section 4) moves an existing xp.properties ONCE: a
      fell.pollMs line still on the old default 200 -> 500 (value text only, CR kept), any other value kept + logged; config-history copy
      first, one Undo-able change-log line, the run-once marker comment under the line; a file without the felled block gets it from
      FellCfg.ensureDefaults (marker included).
No behaviour change for players, no saved-data format change. Rolling back to 0.4.31 is safe (fell.pollMs=500 stays a valid value).
"""
import difflib
import os
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.31.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.32.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.31"
s = raw.decode("utf8").replace("\r\n", "\n")
LF = "\n"
S0 = s
assert 'VERSION = "0.4.31"' in s and "derived from the generated 0.4.30 by tools/skills_0_4_31_patch.py" in s, "not the live generated 0.4.31"
assert s.count('DJ_L.append("acro.doubleJump.trigger=jump")') == 1, "not the edited lineage (Skyy's Double Jump trigger edit missing)"
assert "SkyySkills-IO" not in s
OLDS = []


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "expected %d occurrence(s), found %d of:\n%s" % (count, n, old[:300])
    s = s.replace(old, new)
    OLDS.append(old)


HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.4.32 (2026-10-13)"):].rstrip() + "\n"

# ---------------------------------------------------------------- docstring + version
rep('''"""SkyySkills 0.4.31 - build script (derived from the generated 0.4.30 by tools/skills_0_4_31_patch.py - edit the patch, not this file;
''', '''"""SkyySkills 0.4.32 - build script (derived from the generated 0.4.31 by tools/skills_0_4_32_patch.py - edit the patch, not this file;
0.4.31 was derived from the generated 0.4.30 by tools/skills_0_4_31_patch.py;
''')
rep('''0.4.31: THE ACROBATICS XP LINE NO LONGER SPANS A LEVEL-UP''', NOTE.replace("\n", "\n  ").rstrip() + '''
  CHECKED: SkyySkills/test_skyyskills_0.4.32.py.
0.4.31: THE ACROBATICS XP LINE NO LONGER SPANS A LEVEL-UP''')
rep('VERSION = "0.4.31"', 'VERSION = "0.4.32"')

# ---------------------------------------------------------------- new classes
rep('''plc  = pool.makeClass(PKG + ".PlacedStore")
''', '''plc  = pool.makeClass(PKG + ".PlacedStore")
pset = pool.makeClass(PKG + ".PlacedSet")      # 0.4.32 D: one world's placed positions as primitive arrays (LRU order)
sio  = pool.makeClass(PKG + ".SkillIO")        # 0.4.32 C: the SkyySkills-IO writer job + its thread factory
polm = pool.makeClass(PKG + ".PollMig")        # 0.4.32 E: the one-time fell.pollMs 200 -> 500 update of an existing xp.properties
''')
rep('''          rbf):   # 0.4.30: + RegenBlockFn;''', '''          rbf, pset, sio, polm):   # 0.4.32: + PlacedSet, SkillIO, PollMig; 0.4.30: + RegenBlockFn;''')

# ---------------------------------------------------------------- (A) SkillStore.bridge lock-free
rep('''sto.addMethod(CtNewMethod.make("""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""", sto))''', '''sto.addField(CtField.make("public static volatile java.util.Map BRIDGE;", sto))   # 0.4.32 A: lock-free bridge (the kit snippet)
sto.addMethod(CtNewMethod.make("""
public static java.util.Map bridge0() {
  Object o = System.getProperties().get("skyy.bridge");
  if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
  return (java.util.Map) o;
}""", sto))
sto.addMethod(CtNewMethod.make("""
public static java.util.Map bridge() {
  java.util.Map m = BRIDGE;
  if (m != null) return m;
  synchronized (java.lang.System.class) { m = bridge0(); }
  BRIDGE = m;
  return m;
}""", sto))''')
# MoveSync (tools/skyymove.py) - its bridge() body swapped here
rep('''MV.add_move_sync(mvs_, CtField, CtNewMethod, PKG + ".SkillCfg.warn")
''', '''MV.add_move_sync(mvs_, CtField, CtNewMethod, PKG + ".SkillCfg.warn")
# 0.4.32 A: MoveSync.bridge() lock-free (the shared tools/skyymove.py stays as it is; only this jar's copy is swapped)
mvs_.addField(CtField.make("public static volatile java.util.Map BRIDGE;", mvs_))
mvs_.addMethod(CtNewMethod.make("""
public static java.util.Map bridge0() {
  Object o = System.getProperties().get("skyy.bridge");
  if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
  return (java.util.Map) o;
}""", mvs_))
mvs_.getDeclaredMethod("bridge").setBody("{ java.util.Map m = BRIDGE; if (m != null) return m; synchronized (java.lang.System.class) { m = bridge0(); } BRIDGE = m; return m; }")
''')

# ---------------------------------------------------------------- (C) SkillIO fields / constructor / factory + (B) the index fields, early
rep('''sto.addField(CtField.make("public static final Object IO = new Object();", sto))
''', '''sto.addField(CtField.make("public static final Object IO = new Object();", sto))
# 0.4.32 C: the SkyySkills-IO writer. IO = its executor (null = not running: every job runs on its caller, as 0.4.31); Q[mode] = 1 while a
# job of that kind is queued (one at a time); LOADING = worlds whose placed file is being read
sio.addInterface(pool.get("java.lang.Runnable"))
sio.addInterface(pool.get("java.util.concurrent.ThreadFactory"))
sio.addField(CtField.make("public static volatile java.util.concurrent.ExecutorService IO = null;", sio))
sio.addField(CtField.make("public static volatile boolean STOPPING = false;", sio))
sio.addField(CtField.make("public static final java.util.concurrent.atomic.AtomicIntegerArray Q = new java.util.concurrent.atomic.AtomicIntegerArray(10);", sio))
sio.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap LOADING = new java.util.concurrent.ConcurrentHashMap();", sio))
sio.addField(CtField.make("public static final java.util.concurrent.atomic.AtomicLong RUNS = new java.util.concurrent.atomic.AtomicLong();", sio))
sio.addField(CtField.make("public static volatile String LAST = \\"\\";", sio))   # harness: the thread of the last job
sio.addField(CtField.make("public int mode;", sio))
sio.addField(CtField.make("public String a;", sio))
sio.addConstructor(CtNewConstructor.make("public SkillIO(int mode, String a) { this.mode = mode; this.a = a; }", sio))
sio.addMethod(CtNewMethod.make("""
public Thread newThread(Runnable r) {
  Thread t = new Thread(r, "SkyySkills-IO");
  t.setDaemon(true);
  return t;
}""", sio))
# 0.4.32 B: the leaderboard index (profile key -> Object[]{ String name or null, long[] xp per slot }); TOP_SEEDED = the start scan is done
sto.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap TOPIDX = new java.util.concurrent.ConcurrentHashMap();", sto))
sto.addField(CtField.make("public static volatile boolean TOP_SEEDED = false;", sto))
sto.addField(CtField.make("public static final java.util.concurrent.atomic.AtomicLong TOP_READS = new java.util.concurrent.atomic.AtomicLong();", sto))
# 0.4.32 C: queue a SkyySkills-IO job (mode, a = a world name or null); false = the writer is not running (the caller does the work, 0.4.31)
sto.addMethod(CtNewMethod.make(J14(r"""
public static boolean io(int mode, String a) {
  java.util.concurrent.ExecutorService e = @PKG@.SkillIO.IO;
  if (e == null || @PKG@.SkillIO.STOPPING) return false;
  if (a == null && !@PKG@.SkillIO.Q.compareAndSet(mode, 0, 1)) return true;
  try { e.execute(new @PKG@.SkillIO(mode, a)); return true; }
  catch (Throwable t) { if (a == null) @PKG@.SkillIO.Q.set(mode, 0); return false; }
}"""), sto))
sto.addMethod(CtNewMethod.make(J14(r"""
public static void stopIO() {
  java.util.concurrent.ExecutorService e = @PKG@.SkillIO.IO;
  @PKG@.SkillIO.IO = null;
  if (e == null) return;
  try { e.shutdown(); } catch (Throwable t) { }
  try { e.awaitTermination(5000L, java.util.concurrent.TimeUnit.MILLISECONDS); } catch (Throwable t) { }
}"""), sto))
# 0.4.32 B: one profile's entry in the leaderboard index (a copy of its XP slots; the name kept when none is given)
sto.addMethod(CtNewMethod.make(J14(r"""
public static void topPut(String k, String nm, long[] d) {
  if (k == null || d == null) return;
  int n = @PKG@.SkillDefs.N;
  long[] x = new long[n];
  for (int i = 0; i < n && i < d.length; i++) x[i] = d[i];
  Object o = TOPIDX.get(k);
  String name = nm != null ? nm : (o instanceof Object[] ? (String) ((Object[]) o)[0] : null);
  TOPIDX.put(k, new Object[] { name, x });
}"""), sto))
sto.addMethod(CtNewMethod.make(J14(r"""
public static void topXp(String k, String nm, int skill, long total) {
  Object o = TOPIDX.get(k);
  if (!(o instanceof Object[])) return;
  Object[] e = (Object[]) o;
  long[] x = (long[]) e[1];
  if (skill >= 0 && skill < x.length) x[skill] = total;
  if (nm != null && !nm.equals(e[0])) e[0] = nm;
}"""), sto))
''')

# ---------------------------------------------------------------- (B) install / addK keep the index current
rep('''  OWNER.put(k, u);
  DATA.put(k, d);
  return d;
}""", sto))''', '''  OWNER.put(k, u);
  DATA.put(k, d);
  topPut(k, (String) got[1], d);   // 0.4.32 B: the leaderboard index
  return d;
}""", sto))''')
rep('''  long[] ba = bump(d, skill, amount);
  if (name != null) NAMES.put(u, name);
  DIRTY.put(k, Boolean.TRUE);''', '''  long[] ba = bump(d, skill, amount);
  if (name != null) NAMES.put(u, name);
  DIRTY.put(k, Boolean.TRUE);
  topXp(k, name, skill, ba[1]);   // 0.4.32 B: the leaderboard index''')

# ---------------------------------------------------------------- (B) the seed + (C) save soon, after readLocked / save exist
rep('''sto.addMethod(CtNewMethod.make(f"""
public static int level(java.util.UUID u, int skill) {{''', '''# 0.4.32 B: the leaderboard index from every player file (0.4.31 SkillTop.all's read + parse, every slot at once). SkyySkills-IO at start and
# every 5 minutes (or the caller while the writer is not running). A LOADED profile (DATA) is never re-read (install / addK keep it current);
# the others are refreshed from their file, and an entry whose file is gone (and is not loaded) leaves the index - 0.4.31's 30 s rescan,
# every 5 minutes and off the world thread.
sto.addMethod(CtNewMethod.make(J14(r"""
public static int seedTop() {
  int n = 0;
  try {
    java.io.File[] fs = null;
    if (DIR != null) fs = DIR.toFile().listFiles();
    java.util.HashSet seen = new java.util.HashSet();
    if (fs != null) for (int i = 0; i < fs.length; i++) {
      String fn = fs[i].getName();
      if (!fn.endsWith(".properties")) continue;
      String us = fn.substring(0, fn.length() - 11);
      seen.add(us);
      if (DATA.containsKey(us)) continue;
      try {
        java.util.Properties p = readLocked(fs[i].toPath());
        TOP_READS.incrementAndGet();
        long[] x = new long[@PKG@.SkillDefs.N];
        for (int j = 0; j < x.length; j++) {
          try { x[j] = Long.parseLong(String.valueOf(p.getProperty(@PKG@.SkillDefs.NAMES[j], "0")).trim()); } catch (Throwable t) { x[j] = 0L; }
        }
        if (!DATA.containsKey(us)) TOPIDX.put(us, new Object[] { p.getProperty("name"), x });
        n++;
      } catch (Throwable t) { }
    }
    if (fs != null) {
      java.util.Iterator it = TOPIDX.keySet().iterator();
      while (it.hasNext()) {
        Object k = it.next();
        if (!seen.contains(k) && !DATA.containsKey(k)) it.remove();
      }
    }
  } catch (Throwable t) { @PKG@.SkillCfg.warn("leaderboard scan failed: " + t); }
  TOP_SEEDED = true;
  return n;
}"""), sto))
sto.addMethod(CtNewMethod.make(f"""
public static int level(java.util.UUID u, int skill) {{''')

# (C) OwnCurve.deliver's paid-marker save stays synchronous (0.4.31 review F1 write-ahead; fix review 2026-10-13: an async save could
# lose the marker in a crash after coins:fn:add and pay the same level reward twice)

# ---------------------------------------------------------------- (B) SkillTop.all from the index
rep('''  java.util.HashMap m = new java.util.HashMap();
  try {{
    java.io.File[] fs = {PKG}.SkillStore.DIR.toFile().listFiles();
    if (fs != null) for (int i = 0; i < fs.length; i++) {{
      String fn = fs[i].getName();
      if (!fn.endsWith(".properties")) continue;
      String us = fn.substring(0, fn.length() - 11);
      try {{
        java.util.Properties p = {PKG}.SkillStore.readLocked(fs[i].toPath());
        long x = 0L;
        try {{ x = Long.parseLong(String.valueOf(p.getProperty({PKG}.SkillDefs.NAMES[skill], "0")).trim()); }} catch (Throwable t) {{ }}
        String nm = p.getProperty("name");
        m.put(us, new Object[] {{ label(nm == null ? us.substring(0, 8) : nm, us), Long.valueOf(x), us }});
      }} catch (Throwable t) {{ }}
    }}
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("leaderboard scan failed: " + t); }}''', '''  java.util.HashMap m = new java.util.HashMap();
  // 0.4.32 B: the rows of every profile come from the leaderboard index (seeded once at start on SkyySkills-IO), never from the disk here
  if (!{PKG}.SkillStore.TOP_SEEDED && {PKG}.SkillIO.IO == null) {PKG}.SkillStore.seedTop();
  boolean seeded = {PKG}.SkillStore.TOP_SEEDED;
  java.util.Iterator ii = {PKG}.SkillStore.TOPIDX.entrySet().iterator();
  while (ii.hasNext()) {{
    java.util.Map.Entry e = (java.util.Map.Entry) ii.next();
    String us = (String) e.getKey();
    Object[] ent = (Object[]) e.getValue();
    long[] xs = (long[]) ent[1];
    long x = skill >= 0 && skill < xs.length ? xs[skill] : 0L;
    String nm = (String) ent[0];
    m.put(us, new Object[] {{ label(nm == null ? (us.length() > 8 ? us.substring(0, 8) : us) : nm, us), Long.valueOf(x), us }});
  }}''')
rep('''  java.util.Collections.sort(rows, new {PKG}.TopCmp());
  CACHE[skill] = rows; AT[skill] = now;
  return rows;''', '''  java.util.Collections.sort(rows, new {PKG}.TopCmp());
  if (seeded) {{ CACHE[skill] = rows; AT[skill] = now; }}   // 0.4.32 B: an unseeded list is not cached
  return rows;''')

# ---------------------------------------------------------------- (D) PlacedSet + PlacedStore on it
PSET = r'''
# ================= PlacedSet (0.4.32 D): one world's placed positions - an open-addressing long hash table (tab: node + 1, 0 = empty;
# backward-shift deletion, no tombstones) over nodes in insertion order (np / nn = a doubly linked list = LinkedHashSet's order, head =
# the oldest). addLast = 0.4.31's remove + add (moves a known key to the newest end); addIfAbsent = a file load (a duplicate keeps its
# first place); removeFirst = the LRU eviction. No boxing; grows by doubling (the table stays at most half full).
for _f in ("long[] nk", "int[] np", "int[] nn", "int[] tab", "int mask", "int size", "int head", "int tail", "int nodes", "int free"):
    pset.addField(CtField.make("public " + _f + ";", pset))
pset.addMethod(CtNewMethod.make("""
public void init(int cap) {
  this.nk = new long[cap]; this.np = new int[cap]; this.nn = new int[cap];
  this.nodes = 0; this.free = -1; this.head = -1; this.tail = -1; this.size = 0;
  int t = 128;
  while (t < cap * 2) t = t << 1;
  this.tab = new int[t];
  this.mask = t - 1;
}""", pset))
pset.addConstructor(CtNewConstructor.make("public PlacedSet() { init(64); }", pset))
pset.addMethod(CtNewMethod.make("""
public static int mix(long k) {
  long h = k * -7046029254386353131L;
  return (int) (h ^ (h >>> 32));
}""", pset))
pset.addMethod(CtNewMethod.make("""
public int find(long k) {
  int i = mix(k) & this.mask;
  while (true) {
    int e = this.tab[i];
    if (e == 0) return -1;
    if (this.nk[e - 1] == k) return e - 1;
    i = (i + 1) & this.mask;
  }
}""", pset))
pset.addMethod(CtNewMethod.make("public boolean contains(long k) { return find(k) >= 0; }", pset))
pset.addMethod(CtNewMethod.make("""
public void tabPut(long k, int n) {
  int i = mix(k) & this.mask;
  while (this.tab[i] != 0) i = (i + 1) & this.mask;
  this.tab[i] = n + 1;
}""", pset))
pset.addMethod(CtNewMethod.make("""
public void tabDel(long k) {
  int i = mix(k) & this.mask;
  while (this.tab[i] != 0 && this.nk[this.tab[i] - 1] != k) i = (i + 1) & this.mask;
  if (this.tab[i] == 0) return;
  this.tab[i] = 0;
  int j = i;
  while (true) {
    j = (j + 1) & this.mask;
    int e = this.tab[j];
    if (e == 0) return;
    int h = mix(this.nk[e - 1]) & this.mask;
    boolean stay = i <= j ? (i < h && h <= j) : (i < h || h <= j);
    if (stay) continue;
    this.tab[i] = e;
    this.tab[j] = 0;
    i = j;
  }
}""", pset))
pset.addMethod(CtNewMethod.make("""
public void grow() {
  int cap = this.nk.length * 2;
  long[] k2 = new long[cap]; int[] p2 = new int[cap]; int[] n2 = new int[cap];
  System.arraycopy(this.nk, 0, k2, 0, this.nodes);
  System.arraycopy(this.np, 0, p2, 0, this.nodes);
  System.arraycopy(this.nn, 0, n2, 0, this.nodes);
  this.nk = k2; this.np = p2; this.nn = n2;
  int t = this.tab.length;
  while (t < cap * 2) t = t << 1;
  this.tab = new int[t];
  this.mask = t - 1;
  for (int n = this.head; n >= 0; n = this.nn[n]) tabPut(this.nk[n], n);
}""", pset))
pset.addMethod(CtNewMethod.make("""
public void link(int n) {
  this.np[n] = this.tail;
  this.nn[n] = -1;
  if (this.tail >= 0) this.nn[this.tail] = n; else this.head = n;
  this.tail = n;
}""", pset))
pset.addMethod(CtNewMethod.make("""
public void unlink(int n) {
  int p = this.np[n], q = this.nn[n];
  if (p >= 0) this.nn[p] = q; else this.head = q;
  if (q >= 0) this.np[q] = p; else this.tail = p;
}""", pset))
pset.addMethod(CtNewMethod.make("""
public int alloc(long k) {
  int n;
  if (this.free >= 0) { n = this.free; this.free = this.nn[n]; }
  else {
    if (this.nodes == this.nk.length) grow();
    n = this.nodes;
    this.nodes = this.nodes + 1;
  }
  this.nk[n] = k;
  return n;
}""", pset))
pset.addMethod(CtNewMethod.make("""
public void addLast(long k) {
  int n = find(k);
  if (n >= 0) { unlink(n); link(n); return; }
  n = alloc(k);
  tabPut(k, n);
  link(n);
  this.size = this.size + 1;
}""", pset))
pset.addMethod(CtNewMethod.make("""
public boolean addIfAbsent(long k) {
  if (find(k) >= 0) return false;
  int n = alloc(k);
  tabPut(k, n);
  link(n);
  this.size = this.size + 1;
  return true;
}""", pset))
pset.addMethod(CtNewMethod.make("""
public boolean remove(long k) {
  int n = find(k);
  if (n < 0) return false;
  tabDel(k);
  unlink(n);
  this.nn[n] = this.free;
  this.free = n;
  this.size = this.size - 1;
  return true;
}""", pset))
pset.addMethod(CtNewMethod.make("""
public void removeFirst() {
  if (this.head >= 0) remove(this.nk[this.head]);
}""", pset))
pset.addMethod(CtNewMethod.make("""
public long[] toArray() {
  long[] a = new long[this.size];
  int i = 0;
  for (int n = this.head; n >= 0 && i < a.length; n = this.nn[n]) { a[i] = this.nk[n]; i++; }
  return a;
}""", pset))
'''
rep('''# ================= PlacedStore: positions of player-placed blocks, per world =================
plc.addField(CtField.make("public static java.nio.file.Path DIR;", plc))''', PSET.lstrip("\n") + '''
# ================= PlacedStore: positions of player-placed blocks, per world =================
plc.addField(CtField.make("public static java.nio.file.Path DIR;", plc))''')
rep('''plc.addMethod(CtNewMethod.make(f"""
public static synchronized java.util.LinkedHashSet set(String w) {{
  java.util.LinkedHashSet s = (java.util.LinkedHashSet) WORLDS.get(w);
  if (s != null) return s;
  s = new java.util.LinkedHashSet();
  try {{
    java.nio.file.Path f = DIR.resolve(fileName(w));
    if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {{
      java.io.DataInputStream in = new java.io.DataInputStream(new java.io.BufferedInputStream(java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0])));
      try {{
        int n = in.readInt();
        for (int i = 0; i < n; i++) s.add(Long.valueOf(in.readLong()));
      }} finally {{ in.close(); }}
    }}
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not load placed blocks for " + w + ": " + t); }}
  WORLDS.put(w, s);
  return s;
}}""", plc))
plc.addMethod(CtNewMethod.make("""
public static synchronized void add(String w, long k) {
  java.util.LinkedHashSet s = set(w);
  Long v = Long.valueOf(k);
  s.remove(v);
  s.add(v);
  if (s.size() > CAP) { java.util.Iterator it = s.iterator(); it.next(); it.remove(); }
  DIRTY.add(w);
}""", plc))
plc.addMethod(CtNewMethod.make("""
public static synchronized boolean remove(String w, long k) {
  boolean r = set(w).remove(Long.valueOf(k));
  if (r) DIRTY.add(w);
  return r;
}""", plc))''', '''# 0.4.32 D: a world's file -> a PlacedSet, read with NO lock held (the 0.4.31 read: count + longs, a duplicate keeps its first place)
plc.addMethod(CtNewMethod.make(f"""
public static {PKG}.PlacedSet read(String w) {{
  {PKG}.PlacedSet s = new {PKG}.PlacedSet();
  try {{
    java.nio.file.Path f = DIR.resolve(fileName(w));
    if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {{
      java.io.DataInputStream in = new java.io.DataInputStream(new java.io.BufferedInputStream(java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0])));
      try {{
        int n = in.readInt();
        for (int i = 0; i < n; i++) s.addIfAbsent(in.readLong());
      }} finally {{ in.close(); }}
    }}
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not load placed blocks for " + w + ": " + t); }}
  return s;
}}""", plc))
plc.addMethod(CtNewMethod.make(f"""
public static synchronized {PKG}.PlacedSet get0(String w) {{
  return ({PKG}.PlacedSet) WORLDS.get(w);
}}""", plc))
plc.addMethod(CtNewMethod.make(f"""
public static synchronized {PKG}.PlacedSet put0(String w, {PKG}.PlacedSet n) {{
  {PKG}.PlacedSet s = ({PKG}.PlacedSet) WORLDS.get(w);
  if (s != null) return s;
  WORLDS.put(w, n);
  return n;
}}""", plc))
# the world's set: preloaded by SkyySkills-IO, else read here OUTSIDE the lock (a second reader's copy is dropped)
plc.addMethod(CtNewMethod.make(f"""
public static {PKG}.PlacedSet set(String w) {{
  {PKG}.PlacedSet s = get0(w);
  if (s != null) return s;
  return put0(w, read(w));
}}""", plc))
# SkyySkills-IO: a world's file read before the world thread needs it
plc.addMethod(CtNewMethod.make(f"""
public static void preload(String w) {{
  try {{ if (w != null && get0(w) == null) put0(w, read(w)); }}
  finally {{ if (w != null) {PKG}.SkillIO.LOADING.remove(w); }}
}}""", plc))
# SkillTick (every second, scheduler, memory only): every loaded world whose placed file is not in memory yet -> its read is queued
plc.addMethod(CtNewMethod.make(f"""
public static int preloadWorlds() {{
  if ({PKG}.SkillIO.IO == null || DIR == null) return 0;
  int n = 0;
  try {{
    java.util.Iterator it = {UNI}.get().getWorlds().values().iterator();
    while (it.hasNext()) {{
      {WLD} w = ({WLD}) it.next();
      String wn = w == null ? null : w.getName();
      if (wn == null || get0(wn) != null) continue;
      if ({PKG}.SkillIO.LOADING.putIfAbsent(wn, Boolean.TRUE) != null) continue;
      if ({PKG}.SkillStore.io(6, wn)) n++;
      else {PKG}.SkillIO.LOADING.remove(wn);
    }}
  }} catch (Throwable t) {{ }}
  return n;
}}""", plc))
plc.addMethod(CtNewMethod.make(f"""
public static synchronized void add0(String w, {PKG}.PlacedSet s, long k) {{
  s.addLast(k);
  if (s.size > CAP) s.removeFirst();
  DIRTY.add(w);
}}""", plc))
plc.addMethod(CtNewMethod.make("""
public static void add(String w, long k) {
  add0(w, set(w), k);
}""", plc))
plc.addMethod(CtNewMethod.make(f"""
public static synchronized boolean remove0(String w, {PKG}.PlacedSet s, long k) {{
  boolean r = s.remove(k);
  if (r) DIRTY.add(w);
  return r;
}}""", plc))
plc.addMethod(CtNewMethod.make("""
public static boolean remove(String w, long k) {
  return remove0(w, set(w), k);
}""", plc))''')
rep('''plc.addMethod(CtNewMethod.make("""
public static synchronized boolean contains(String w, long k) {
  return set(w).contains(Long.valueOf(k));
}""", plc))
plc.addMethod(CtNewMethod.make("""
public static synchronized void snapshot(java.util.ArrayList names, java.util.ArrayList snaps) {
  java.util.Iterator it = DIRTY.iterator();
  while (it.hasNext()) {
    String w = (String) it.next();
    java.util.LinkedHashSet s = (java.util.LinkedHashSet) WORLDS.get(w);
    if (s != null) {
      long[] a = new long[s.size()];
      int i = 0;
      java.util.Iterator si = s.iterator();
      while (si.hasNext() && i < a.length) { a[i] = ((Long) si.next()).longValue(); i++; }
      names.add(w); snaps.add(a);
    }
  }
  DIRTY.clear();
}""", plc))''', '''plc.addMethod(CtNewMethod.make(f"""
public static synchronized boolean contains0({PKG}.PlacedSet s, long k) {{
  return s.contains(k);
}}""", plc))
plc.addMethod(CtNewMethod.make("""
public static boolean contains(String w, long k) {
  return contains0(set(w), k);
}""", plc))
# the dirty worlds' positions copied (primitive arrays, in order) under the lock; flush writes them outside it
plc.addMethod(CtNewMethod.make(f"""
public static synchronized void snapshot(java.util.ArrayList names, java.util.ArrayList snaps) {{
  java.util.Iterator it = DIRTY.iterator();
  while (it.hasNext()) {{
    String w = (String) it.next();
    {PKG}.PlacedSet s = ({PKG}.PlacedSet) WORLDS.get(w);
    if (s != null) {{ names.add(w); snaps.add(s.toArray()); }}
  }}
  DIRTY.clear();
}}""", plc))''')

# ---------------------------------------------------------------- (E) FellRead.reset + FellWatch keeps one reader; poll 500
rep('''frd.addMethod(CtNewMethod.make(f"""
public Object[] sec(int x, int y, int z) {{''', '''# 0.4.32 E: ready for the next poll of the same watch (the section cache is emptied: every poll reads fresh sections, as 0.4.31)
frd.addMethod(CtNewMethod.make("""
public void reset() {
  this.reads = 0;
  this.over = false;
  this.err = null;
  this.secs.clear();
}""", frd))
frd.addMethod(CtNewMethod.make(f"""
public Object[] sec(int x, int y, int z) {{''')
rep('''             "int collNo", "long xp", "int row"):
    fwt.addField(CtField.make("public " + decl + ";", fwt))''', '''             "int collNo", "long xp", "int row", "Object rd"):   # 0.4.32 E: rd = this watch's one FellRead
    fwt.addField(CtField.make("public " + decl + ";", fwt))''')
rep('''    {PKG}.FellRead R = new {PKG}.FellRead(this.w, 2147483647);
    java.util.concurrent.ConcurrentHashMap cm = {PKG}.Fell.claims(this.wn);''', '''    {PKG}.FellRead R = ({PKG}.FellRead) this.rd;   // 0.4.32 E: one reader per watch, reset each poll
    if (R == null) {{ R = new {PKG}.FellRead(this.w, 2147483647); this.rd = R; }}
    else R.reset();
    java.util.concurrent.ConcurrentHashMap cm = {PKG}.Fell.claims(this.wn);''')
POLL_MARK_ID = "SkyySkills 0.4.32 falling tree check every 500 ms"
POLL_MARK = "# " + POLL_MARK_ID + ": a falling tree is checked every fell.pollMs ms (a lag fix; the old default was 200)."
rep('FELL_L.append("fell.pollMs=200")' + LF,
    'POLL_MARK_ID = %s   # 0.4.32 E: the run-once marker of PollMig' % json.dumps(POLL_MARK_ID) + LF
    + 'POLL_MARK = %s' % json.dumps(POLL_MARK) + LF
    + 'FELL_L.append("fell.pollMs=500")' + LF
    + 'FELL_L.append(POLL_MARK)' + LF)
rep('"int MAX_READS = 8000", "int MAX_SNAPS = 10", "int MAX_PER_PLAYER = 4", "int MAX_WATCHES = 64", "long POLL_MS = 200L",',
    '"int MAX_READS = 8000", "int MAX_SNAPS = 10", "int MAX_PER_PLAYER = 4", "int MAX_WATCHES = 64", "long POLL_MS = 500L",')
rep('  POLL_MS = clampL({PKG}.SkillCfg.lng(p, "fell.pollMs", 200L), 50L, 1000L);', '  POLL_MS = clampL({PKG}.SkillCfg.lng(p, "fell.pollMs", 500L), 50L, 1000L);')
rep('''    ("fell.pollMs", "Falling tree checked every", "gathering", "int", "200", "50", "1000", "", "ms", "live,adv",''',
    '''    ("fell.pollMs", "Falling tree checked every", "gathering", "int", "500", "50", "1000", "", "ms", "live,adv",''')

# ---------------------------------------------------------------- (E) PollMig + (C) SkillIO.run, before the ticker
POLLMIG = r'''
# ---- PollMig (0.4.32, PROJECT-RULES section 4): ONCE on an EXISTING xp.properties, setup() after PerkMig.run, BEFORE SkillCfg.load and
# CfgPub.start. Nothing to do = no file (load() writes the 0.4.32 default), no fell.enabled key (FellCfg.ensureDefaults appends the 0.4.32
# block, marker included) or a comment line holding MARK_ID (done before). Else, per logical line (the kit's own parser): fell.pollMs whose
# LAST entry is a one-line entry holding exactly 200 (the old default) -> every such one-line entry 500 (value text only; key, separator, CR
# kept) + a config-changes.log line (Undo = 200); any other value is kept (an INFO line). The marker goes right under the last fell.pollMs
# entry, or at the end in the file's own line ending. Properties check (only fell.pollMs differs), config-history copy first, atomicWrite.
# A failure = WARN, file untouched, retried at the next start. (AcroMig's reviewed machinery.)
polm.addField(CtField.make("public static final String MARK_ID = %s;" % json.dumps(POLL_MARK_ID), polm))
polm.addField(CtField.make("public static final String MARK = %s;" % json.dumps(POLL_MARK), polm))
polm.addField(CtField.make('public static final String KEY = "fell.pollMs";', polm))
polm.addField(CtField.make('public static final String OLD = "200";', polm))
polm.addField(CtField.make('public static final String NEW = "500";', polm))
polm.addField(CtField.make('public static final String WHO = "SkyySkills 0.4.32";', polm))
assert DEFAULTS.count(POLL_MARK_ID) == 1 and ("\n" + DEFAULTS).count("\nfell.pollMs=500\n" + POLL_MARK + "\n") == 1
# pure text step (ISO-8859-1 chars in and out). null = nothing to do; else { new text, String[] { key, old, new }* (the change-log rows),
# Boolean updated, String kept note ("" = none) }. Never throws for any text.
polm.addMethod(CtNewMethod.make(J14(r"""
public static Object[] plan(String text) {
  if (text == null) return null;
  java.util.Properties p = new java.util.Properties();
  try { p.load(new java.io.StringReader(text)); } catch (Throwable t) { return null; }
  if (p.getProperty("fell.enabled") == null) return null;
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  String eff = null;
  boolean multi = false;
  int lastEnd = -1;
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) {
      if (s.indexOf(MARK_ID) >= 0) return null;
      k++;
      continue;
    }
    int e = @PKG@.CfgFile.end(l, k);
    if (KEY.equals(@PKG@.CfgFile.key(s))) { eff = @PKG@.CfgFile.value(l, k).trim(); multi = e > k; lastEnd = e; }
    k = e + 1;
  }
  boolean mig = eff != null && !multi && eff.equals(OLD);
  String kept = eff != null && !mig ? KEY + "=" + @PKG@.CfgRows.oneLine(p.getProperty(KEY)) + " kept (an admin's value) - the 0.4.32 default is 500" : "";
  String cr = text.indexOf("\r\n") >= 0 ? "\r" : "";
  java.util.ArrayList out = new java.util.ArrayList();
  boolean placed = false;
  k = 0;
  while (k < l.size()) {
    String s2 = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s2)) { out.add(raw[k]); k++; continue; }
    int e2 = @PKG@.CfgFile.end(l, k);
    if (mig && KEY.equals(@PKG@.CfgFile.key(s2)) && e2 == k && @PKG@.CfgFile.value(l, k).trim().equals(OLD)) {
      out.add(s2.substring(0, @PKG@.CfgFile.valStart(s2)) + NEW + (raw[k].endsWith("\r") ? "\r" : ""));
    } else {
      for (int q = k; q <= e2; q++) out.add(raw[q]);
    }
    if (e2 == lastEnd && e2 + 1 < raw.length) {
      out.add(MARK + (raw[e2].endsWith("\r") ? "\r" : cr));
      placed = true;
    }
    k = e2 + 1;
  }
  StringBuilder sb = new StringBuilder(text.length() + 256);
  for (int i = 0; i < out.size(); i++) {
    if (i > 0) sb.append('\n');
    sb.append((String) out.get(i));
  }
  String body = sb.toString();
  if (!placed) {
    String nl = cr + "\n";
    String pre = (body.length() == 0 || body.endsWith("\n")) ? "" : nl;
    String last = body.endsWith("\n") ? body.substring(0, body.length() - 1) : body;
    if (last.endsWith("\r")) last = last.substring(0, last.length() - 1);
    int bs = 0;
    for (int i = last.length() - 1; i >= 0 && last.charAt(i) == '\\'; i--) bs++;
    if (bs % 2 == 1) pre = pre + nl;
    body = body + pre + MARK + nl;
  }
  String[] rows = mig ? new String[] { KEY, OLD, NEW } : new String[0];
  return new Object[] { body, rows, Boolean.valueOf(mig), kept };
}"""), polm))
# only fell.pollMs may differ (exactly 500 when updated); no key added or removed
polm.addMethod(CtNewMethod.make(J14(r"""
public static boolean sameAfter(byte[] old, byte[] nb, boolean mig) {
  try {
    java.util.Properties a = new java.util.Properties();
    java.util.Properties n = new java.util.Properties();
    a.load(new java.io.ByteArrayInputStream(old));
    n.load(new java.io.ByteArrayInputStream(nb));
    if (n.size() != a.size()) return false;
    java.util.Iterator it = a.stringPropertyNames().iterator();
    while (it.hasNext()) {
      String k = (String) it.next();
      String want = a.getProperty(k);
      if (mig && KEY.equals(k)) want = NEW;
      String got = n.getProperty(k);
      if (got == null || !got.equals(want)) return false;
    }
    return true;
  } catch (Throwable t) { return false; }
}"""), polm))
polm.addMethod(CtNewMethod.make(J14(r"""
public static String logLine(String k, String o, String n) {
  return @PKG@.CfgLog.now() + "\t" + WHO + "\t-\tupdate\t" + @PKG@.CfgRows.oneLine(k) + "\t" + o + "\t" + n + "\tok";
}"""), polm))
polm.addMethod(CtNewMethod.make(J14(r"""
public static synchronized String run() {
  java.nio.file.Path f = @PKG@.SkillCfg.FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = plan(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    boolean mig = ((Boolean) r[2]).booleanValue();
    if (!sameAfter(old, data, mig)) {
      @PKG@.SkillCfg.warn("xp.properties NOT updated for 0.4.32 (falling tree check every 500 ms): the update would change another setting (the file is used as it is; the next start tries again)");
      return "";
    }
    int fi = @PKG@.HealMig.fileIdx();
    if (fi < 0) return "";
    @PKG@.HealMig.mgKit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(fi, old, @PKG@.CfgHist.stamp(), WHO, "before the 0.4.32 falling tree check update");
    if (!@PKG@.HealMig.mgSaved(fi, old)) {
      @PKG@.SkillCfg.warn("xp.properties NOT updated for 0.4.32 (falling tree check every 500 ms): the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] rows = (String[]) r[1];
    for (int i = 0; i + 2 < rows.length; i += 3) @PKG@.CfgLog.enqueue(logLine(rows[i], rows[i + 1], rows[i + 2]));
    if (rows.length > 0) @PKG@.CfgLog.flush();
    String msg = "xp.properties updated for 0.4.32: " + (mig ? KEY + " 200 -> 500 (a falling tree is checked every 500 ms; Server Setup -> Changes -> Undo = 200)" : "no setting changed - 0.4.32 marker added") + " - the old file is in config-history";
    @PKG@.SkillCfg.info(msg);
    String kept = (String) r[3];
    if (kept.length() > 0) { @PKG@.SkillCfg.info(kept); return msg + "\n" + kept; }
    return msg;
  } catch (Throwable t) {
    @PKG@.SkillCfg.warn("could not update xp.properties for 0.4.32 (falling tree check every 500 ms; the file is used as it is): " + t);
    return "";
  }
}"""), polm))

# ================= SkillIO.run (0.4.32 C): the SkyySkills-IO jobs (1 dirty players, 2 placed blocks, 3 class curve, 4 own curve,
# 5 leaderboard seed, 6 a world's placed file) =================
sio.addMethod(CtNewMethod.make(J14(r"""
public void run() {
  if (this.a == null && this.mode >= 0 && this.mode < Q.length()) Q.set(this.mode, 0);
  RUNS.incrementAndGet();
  LAST = Thread.currentThread().getName();
  try {
    if (this.mode == 1) @PKG@.SkillStore.flushDirty();
    else if (this.mode == 2) @PKG@.PlacedStore.flush();
    else if (this.mode == 3) @PKG@.ClassCurve.flush();
    else if (this.mode == 4) @PKG@.OwnCurve.flush();
    else if (this.mode == 5) @PKG@.SkillStore.seedTop();
    else if (this.mode == 6) @PKG@.PlacedStore.preload(this.a);
  } catch (Throwable t) { @PKG@.SkillCfg.warn("a SkyySkills-IO job (" + this.mode + ") failed: " + t); }
}"""), sio))

'''
rep('''# ================= 1s ticker: feedback leftovers, bridge publish (5s), save (10s), placed blocks (60s) =================''',
    POLLMIG.lstrip("\n") + '''# ================= 1s ticker: feedback leftovers, bridge publish (5s), save (10s), placed blocks (60s) =================''')

# ---------------------------------------------------------------- (C) the ticker hands the disk work to SkyySkills-IO
rep('''  if (this.n % 10L == 0L) {{ try {{ {PKG}.SkillStore.flushDirty(); }} catch (Throwable t) {{ }} }}
  if (this.n % 60L == 0L) {{ try {{ {PKG}.PlacedStore.flush(); }} catch (Throwable t) {{ }} }}''',
    '''  if (this.n % 10L == 0L) {{ try {{ if (!{PKG}.SkillStore.io(1, null)) {PKG}.SkillStore.flushDirty(); }} catch (Throwable t) {{ }} }}   // 0.4.32 C: on SkyySkills-IO
  if (this.n % 60L == 0L) {{ try {{ if (!{PKG}.SkillStore.io(2, null)) {PKG}.PlacedStore.flush(); }} catch (Throwable t) {{ }} }}
  try {{ {PKG}.PlacedStore.preloadWorlds(); }} catch (Throwable t) {{ }}   // 0.4.32 D: placed files read on SkyySkills-IO before a world needs them
  if (this.n % 300L == 0L) {{ try {{ {PKG}.SkillStore.io(5, null); }} catch (Throwable t) {{ }} }}   // 0.4.32 B: the leaderboard index refreshed off-thread''')
rep('''  try {{ {PKG}.ClassCurve.flush(); }} catch (Throwable t) {{ }}   // 0.4.12: the class skill curve record (only after a notice was told)
  try {{ {PKG}.OwnCurve.flush(); }} catch (Throwable t) {{ }}     // 0.4.16: the own level list record (only after a notice was told)
}}""", tick))''', '''  try {{ if ({PKG}.ClassCurve.DIRTY && !{PKG}.SkillStore.io(3, null)) {PKG}.ClassCurve.flush(); }} catch (Throwable t) {{ }}   // 0.4.12 (0.4.32: on SkyySkills-IO)
  try {{ if ({PKG}.OwnCurve.DIRTY && !{PKG}.SkillStore.io(4, null)) {PKG}.OwnCurve.flush(); }} catch (Throwable t) {{ }}     // 0.4.16 (0.4.32: on SkyySkills-IO)
}}""", tick))''')
# ---------------------------------------------------------------- setup: the writer + the seed; PollMig; shutdown: writer first
rep('''  {PKG}.PlacedStore.DIR = base.resolve("placed");
''', '''  {PKG}.PlacedStore.DIR = base.resolve("placed");
  {PKG}.SkillIO.STOPPING = false;
  {PKG}.SkillIO.IO = java.util.concurrent.Executors.newSingleThreadExecutor(new {PKG}.SkillIO(9, null));   // 0.4.32 C: SkyySkills-IO
  {PKG}.SkillStore.io(5, null);   // 0.4.32 B: the leaderboard index, read once off the world thread
''')
rep('''  {PKG}.PerkMig.run();        // 0.4.25: the class power split - untouched old defaults rewritten + missing lines added, once; History first
''', '''  {PKG}.PerkMig.run();        // 0.4.25: the class power split - untouched old defaults rewritten + missing lines added, once; History first
  {PKG}.PollMig.run();        // 0.4.32: untouched fell.pollMs 200 -> 500 in an existing xp.properties, once; History first
''')
rep('''protected void shutdown() {{
  try {{ if (this.ticker != null) this.ticker.cancel(false); }} catch (Throwable t) {{ }}
''', '''protected void shutdown() {{
  try {{ if (this.ticker != null) this.ticker.cancel(false); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SkillIO.STOPPING = true; {PKG}.SkillStore.stopIO(); }} catch (Throwable t) {{ }}   // 0.4.32 C: the writer's queue first, then the synchronous saves
''')

# ---------------------------------------------------------------- (B) the legacy Combat move rewrites XP slots directly: the index follows
# (fix review 2026-10-13: moveLegacy bypasses addK / install, so a loaded profile's index entry stayed stale until the next unload + seed)
rep('''  long x = {PKG}.SkillStore.moveLegacy({PKG}.SkillStore.dataK(k, u), slot);
  if (x <= 0L) return;
''', '''  long[] dd = {PKG}.SkillStore.dataK(k, u);
  long x = {PKG}.SkillStore.moveLegacy(dd, slot);
  if (x <= 0L) return;
  {PKG}.SkillStore.topPut(k, null, dd);   // 0.4.32 B: the leaderboard index (old Combat slot 0, the class slot set)
''')

# ---------------------------------------------------------------- checks
assert s.count("synchronized (java.lang.System.class) {\n    Object o") == 0, "a locked bridge() is left"
assert "SkillStore.readLocked(fs[i].toPath());\n        long x = 0L;" not in s, "SkillTop.all still reads files"
_a, _b = S0.split(LF), s.split(LF)
_hunks = [op for op in difflib.SequenceMatcher(None, _a, _b, autojunk=False).get_opcodes() if op[0] != "equal"]
_gone = [(i, _a[i]) for op in _hunks for i in range(op[1], op[2])]
_allowed = set()
for _o in OLDS:
    _allowed.update(_o.split(LF))
_bad = [(i, ln) for i, ln in _gone if ln not in _allowed and not any(_o in ln for _o in OLDS if LF not in _o)]
assert not _bad, "0.4.31 lines changed outside the planned places: %r" % _bad[:5]
compile(s, dst, "exec")
open(dst, "wb").write(s.replace(LF, NL).encode("utf8"))
print("wrote", dst, len(s), "chars;", len(_hunks), "diff hunks vs 0.4.31,", len(_gone), "0.4.31 lines replaced;", len(OLDS), "anchors")
