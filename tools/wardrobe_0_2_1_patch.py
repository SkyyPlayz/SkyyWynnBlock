"""Derive SkyyWardrobe/build_skyywardrobe_0.2.1.py from the SET pin 0.2 (build_skyywardrobe_0.2.py, a hand-written new-mod script; 0.2
stays untouched). Edit THIS file, never the generated script: python tools/wardrobe_0_2_1_patch.py, then
python SkyyWardrobe/build_skyywardrobe_0.2.1.py (never --deploy from an agent).
Test: python SkyyWardrobe/test_skyywardrobe_0.2.1.py

0.2.1 = LAG FIXES from the code audit (research/Code-Structure-Audit.md finding 9d; Skyy 2026-10-13: "lets audit the code structure,
and make sure they are working together in the smoothest easiest lag free way possible"). No behaviour change for players; files,
journal format, bridge keys and the write-ahead rule (the journal is durable on disk BEFORE any item moves) are 0.2's.
  1. JOIN WITHOUT A COLD DISK LOAD ON THE WORLD THREAD (the logged "WdRepairTask took 36 ms"). WdHop.run (the scheduler thread that hands
     a task to the player's world) now calls WdRepairTask.prewarm() first: unless the profile is busy, it loads the profile's Requip
     files (WdStore.get - the cache), learns whether a journal file exists (WdJournal.hasFile) and reads it (WdJournal.preRead) - all
     off the world thread. The world task then only compares what it finds with the inventory: WdStore.get answers from the cache, the
     "is there a journal" questions answer from the cache, and WdTx.repair takes the pre-read journal (WdJournal.takePre) when nothing
     wrote or deleted that journal since (a per-key generation counter; anything else = it reads the file as before).
  2. ONE JOURNAL LOCK PER PROFILE KEY. Every WdJournal method was static synchronized (one lock for every player in every world, held
     across the fsync'd journal write + its read-back). Now each method locks only its key (WdJournal.lockOf(k), one monitor per key);
     the bodies are 0.2's (*0 methods); sweep() and dropAll() lock key by key. Two players' equips never wait for each other's journal.
  3. THE "HAS A JOURNAL" PRE-CHECK FROM MEMORY. WdTx.run refused a change while an unrepaired journal file exists (fixer 1) by asking the
     disk (Files.exists) on the world thread for EVERY change. Now: !PENDING.containsKey(k) && WdJournal.hasFile(k), where hasFile is a
     cache (KNOWN) kept exact by every write / delete / read of the journal and the admin's move-aside, filled off the world thread by the
     pre-warm (or once, on its first question). The two other world-thread Files.exists(journal) checks (the repair, the register.txt
     clean-up) ask the same cache. The scheduler-side checks (timer, evict) still ask the disk.
  4. FIXER (review): the join pre-warm runs on a PRIVATE reader thread. WdHop.later hands every WdRepairTask hop to WdHop.READER (one
     daemon thread "SkyyWardrobe-reader", WdThreads) instead of the engine's shared scheduler, so a join storm after a restart loads its
     cold profiles there and never delays other mods' timers; every other hop and no reader / refused = the shared scheduler as in 0.2.
     setup makes the reader before the join listener; shutdown stops it (shutdownNow - an interrupted pre-warm only means the world
     task loads that profile itself).
  5. FIXER (review): a STALE "has a journal" answer is re-checked. A cached TRUE (KNOWN) can only go stale if an admin deletes / moves
     journal.json by hand while the server runs; WdTx.run would then refuse every change. Now the refusal path asks the disk once more
     (WdJournal.recheck: forget the cached answer, one Files.exists) - only when the cache says a journal exists, which is rare, and 0.2
     asked the disk on every change.
Classes changed: WdJournal (per-key locks, KNOWN / GEN / PRE caches, + recheck), WdTx (run pre-check, repair read), WdRepairTask (+prewarm),
WdHop (run calls prewarm; later -> READER for the join repair), WdOps (register clean-up check), WdPlugin (version, reader in setup /
shutdown); new WdThreads. Everything else = 0.2.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(ROOT, "SkyyWardrobe")
src = os.path.join(HERE, "build_skyywardrobe_0.2.py")
dst = os.path.join(HERE, "build_skyywardrobe_0.2.1.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.2"
s = raw.decode("utf8").replace("\r\n", "\n")
OLD = s
LF = "\n"
assert 'VERSION = "0.2"\n' in s and "lockOf" not in s, "the source must be build_skyywardrobe_0.2.py"
REG0, SYS0 = s.count("registerCommand("), s.count("registerSystem(")


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:90]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:90])
    s = s.replace(old, new)


# ---------------------------------------------------------------------------------------------------------------- header + version
rep('''"""SkyyWardrobe 0.2 "Requip" - build script (javassist via jpype, tools/skyybuild.py). Derived from build_skyywardrobe_0.1.py (the SET pin,''',
    '''"""SkyyWardrobe 0.2.1 "Requip" - build script GENERATED by tools/wardrobe_0_2_1_patch.py from build_skyywardrobe_0.2.py (edit the patch).
0.2.1 (2026-10-13, research/Code-Structure-Audit.md 9d; full notes: tools/wardrobe_0_2_1_patch.py): the join repair pre-warms the profile's
Requip files and its journal on the scheduler thread (the world task only compares the inventory); one journal lock per profile key instead
of one for everyone; the "is there an unrepaired journal" check answers from memory (no Files.exists on the world thread; a cached "yes"
is re-checked on disk before it refuses); the join pre-warm runs on a private reader thread (SkyyWardrobe-reader). Write-ahead
rule, files and behaviour = 0.2. Test: python SkyyWardrobe/test_skyywardrobe_0.2.1.py
0.2 = derived from build_skyywardrobe_0.1.py (the SET pin,''')
rep('''Run:   python SkyyWardrobe/build_skyywardrobe_0.2.py   -> SkyyWardrobe/SkyyWardrobe-0.2.jar   (no --deploy: tools/deploy_set.py deploys)
Test:  python SkyyWardrobe/test_skyywardrobe_0.2.py --dir tools/dev/scratch/<task>/test   (bare-JVM harness)''',
    '''Run:   python SkyyWardrobe/build_skyywardrobe_0.2.1.py   -> SkyyWardrobe/SkyyWardrobe-0.2.1.jar   (no --deploy: tools/deploy_set.py deploys)
Test:  python SkyyWardrobe/test_skyywardrobe_0.2.1.py --dir tools/dev/scratch/<task>/test   (bare-JVM harness)''')
rep('VERSION = "0.2"\n', 'VERSION = "0.2.1"\n')

# ---------------------------------------------------------------------------------------------------------------- WdJournal: per-key locks + caches
J0 = s.index('M(jr, "public static java.nio.file.Path fileOf(String k) { return @PKG@.WdStore.dirOf(k).resolve(\\"journal.json\\"); }")')
J1 = s.index('M(sto, r"""\npublic static @PKG@.WdData get(String k, java.util.UUID u) {')
old_j = s[J0:J1]
for _m in ("public static synchronized boolean write(", "public static synchronized org.bson.BsonDocument read(", "public static synchronized void delete(",
           "public static long epochOf(", "public static org.bson.BsonArray stepsOf(", "public static synchronized org.bson.BsonDocument begin(",
           "public static synchronized void saved(", "public static synchronized void abort(", "public static synchronized void failed(",
           "public static synchronized void sweep(", "public static synchronized int dropAll("):
    assert old_j.count(_m) == 1, _m
NEW_J = r'''M(jr, "public static java.nio.file.Path fileOf(String k) { return @PKG@.WdStore.dirOf(k).resolve(\"journal.json\"); }")
# 0.2.1 (audit 9d): ONE LOCK PER PROFILE KEY (0.2: every method locked the WdJournal class = one lock for every player in every world). LOCKS = key
# -> monitor; KNOWN = key -> Boolean "a journal file exists" (exact: every write / delete / read below updates it; unknown = ask the disk
# once); GEN = key -> Long, bumped by every write / delete (a pre-read journal is only used while its generation is current); PRE = key ->
# Object[]{Long gen, BsonDocument or null} the pre-warm's read (taken once by the repair on the world thread)
F(jr, "public static final java.util.concurrent.ConcurrentHashMap LOCKS = new java.util.concurrent.ConcurrentHashMap();")
F(jr, "public static final java.util.concurrent.ConcurrentHashMap KNOWN = new java.util.concurrent.ConcurrentHashMap();")
F(jr, "public static final java.util.concurrent.ConcurrentHashMap GEN = new java.util.concurrent.ConcurrentHashMap();")
F(jr, "public static final java.util.concurrent.ConcurrentHashMap PRE = new java.util.concurrent.ConcurrentHashMap();")
F(jr, "public static volatile long DISKCHECKS = 0L;")
F(jr, "public static volatile long PREUSED = 0L;")
F(jr, "public static volatile long READS = 0L;")
M(jr, r"""
public static Object lockOf(String k) {
  String kk = k == null ? "" : k;
  Object o = LOCKS.get(kk);
  if (o != null) return o;
  Object n = new Object();
  Object prev = LOCKS.putIfAbsent(kk, n);
  return prev != null ? prev : n;
}""")
M(jr, r"""
public static void bump(String k) {
  if (k == null) return;
  Object g = GEN.get(k);
  GEN.put(k, Long.valueOf(g instanceof Long ? ((Long) g).longValue() + 1L : 1L));
  PRE.remove(k);
}""")
M(jr, r"""
public static long gen(String k) {
  Object g = k == null ? null : GEN.get(k);
  return g instanceof Long ? ((Long) g).longValue() : 0L;
}""")
# does the journal FILE of k exist? From KNOWN when known (no disk); else one Files.exists, remembered
M(jr, r"""
public static boolean hasFile(String k) {
  if (k == null || @PKG@.WdStore.RQ == null) return false;
  Object b = KNOWN.get(k);
  if (b instanceof Boolean) return ((Boolean) b).booleanValue();
  DISKCHECKS = DISKCHECKS + 1L;
  boolean e = java.nio.file.Files.exists(fileOf(k), new java.nio.file.LinkOption[0]);
  KNOWN.put(k, Boolean.valueOf(e));
  return e;
}""")
M(jr, r"""
public static void forget(String k) {
  if (k == null) return;
  KNOWN.remove(k);
  bump(k);
}""")
M(jr, r"""
public static boolean write0(String k, org.bson.BsonDocument j) {
  bump(k);
  try {
    @PKG@.WdStore.atomicWrite(fileOf(k), @PKG@.WdCodec.toJson(j).getBytes("UTF-8"));
    KNOWN.put(k, Boolean.TRUE);
    org.bson.BsonDocument back = @PKG@.WdStore.readDoc(fileOf(k));
    if (!String.valueOf(@PKG@.WdCodec.strOf(back, "stage")).equals(String.valueOf(@PKG@.WdCodec.strOf(j, "stage")))) throw new java.io.IOException("read back a different stage");
    return true;
  } catch (Throwable t) { KNOWN.remove(k); @PKG@.WdLog.warn("could not write the Requip journal of " + k + ": " + t); return false; }
}""")
M(jr, r"""
public static boolean write(String k, org.bson.BsonDocument j) {
  Object lk = lockOf(k);
  synchronized (lk) { return write0(k, j); }
}""")
M(jr, r"""
public static org.bson.BsonDocument read0(String k) {
  READS = READS + 1L;
  try {
    if (@PKG@.WdStore.RQ == null) return null;
    java.nio.file.Path f = fileOf(k);
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) { KNOWN.put(k, Boolean.FALSE); return null; }
    KNOWN.put(k, Boolean.TRUE);
    return @PKG@.WdStore.readDoc(f);
  } catch (Throwable t) {
    @PKG@.WdLog.warnOnce("journal:" + k, "the Requip journal of " + k + " could not be read (" + t + ") - left in place for an admin");
    return null;
  }
}""")
M(jr, r"""
public static org.bson.BsonDocument read(String k) {
  Object lk = lockOf(k);
  synchronized (lk) { return read0(k); }
}""")
# 0.2.1: the pre-warm's read (scheduler thread): the document (or "no journal") with the generation it was read at
M(jr, r"""
public static void preRead0(String k) {
  long g = gen(k);
  org.bson.BsonDocument d = read0(k);
  PRE.put(k, new Object[] { Long.valueOf(g), d });
}""")
M(jr, r"""
public static void preRead(String k) {
  if (k == null) return;
  Object lk = lockOf(k);
  synchronized (lk) { preRead0(k); }
}""")
# the repair's question (world thread): the pre-read journal when nothing wrote / deleted it since; null = read it as before
M(jr, r"""
public static Object[] takePre0(String k) {
  Object o = PRE.remove(k);
  if (!(o instanceof Object[])) return null;
  Object[] p = (Object[]) o;
  if (((Long) p[0]).longValue() != gen(k)) return null;
  PREUSED = PREUSED + 1L;
  return p;
}""")
M(jr, r"""
public static Object[] takePre(String k) {
  if (k == null) return null;
  Object lk = lockOf(k);
  synchronized (lk) { return takePre0(k); }
}""")
M(jr, r"""
public static void delete0(String k) {
  PENDING.remove(k);
  bump(k);
  try {
    if (@PKG@.WdStore.RQ != null) java.nio.file.Files.deleteIfExists(fileOf(k));
    KNOWN.put(k, Boolean.FALSE);
  } catch (Throwable t) { KNOWN.remove(k); @PKG@.WdLog.warn("could not delete the Requip journal of " + k + ": " + t); }
}""")
M(jr, r"""
public static void delete(String k) {
  Object lk = lockOf(k);
  synchronized (lk) { delete0(k); }
}""")
M(jr, r"""
public static long epochOf(String uuid) {
  if (uuid == null || uuid.length() == 0) return -1L;
  try { Object e = @PKG@.WdLog.bridge().get("profile:epoch:" + uuid); if (e instanceof Number) return ((Number) e).longValue(); } catch (Throwable t) { }
  return -1L;
}""")
M(jr, r"""
public static org.bson.BsonArray stepsOf(org.bson.BsonDocument j) {
  if (j == null) return new org.bson.BsonArray();
  org.bson.BsonValue v = (org.bson.BsonValue) j.get("steps");
  if (v != null && v.isArray()) return v.asArray();
  org.bson.BsonArray a = new org.bson.BsonArray();
  a.add(j);
  return a;
}""")
M(jr, r"""
public static org.bson.BsonDocument begin0(@PKG@.WdData d, org.bson.BsonDocument step, long now) {
  String k = d.key;
  Object prevAt = PENDING.get(k);
  org.bson.BsonArray steps = new org.bson.BsonArray();
  long keepMs = (long) @PKG@.WdCfg.JKEEP_S * 1000L;
  if (prevAt instanceof Long) {
    org.bson.BsonDocument prev = read0(k);
    if (prev != null && "saved".equals(@PKG@.WdCodec.strOf(prev, "stage"))) {
      org.bson.BsonArray ps = stepsOf(prev);
      for (int i = 0; i < ps.size(); i++) {
        org.bson.BsonValue v = (org.bson.BsonValue) ps.get(i);
        if (v == null || !v.isDocument()) continue;
        long sa = @PKG@.WdCodec.lngOf(v.asDocument(), "savedAt", 0L);
        if (sa > 0L && now - sa >= keepMs) continue;
        steps.add(v);
      }
    }
  }
  int prevN = steps.size();
  steps.add(step);
  org.bson.BsonDocument j = new org.bson.BsonDocument();
  j.put("format", new org.bson.BsonInt32(3));
  j.put("key", new org.bson.BsonString(k));
  j.put("uuid", new org.bson.BsonString(d.uuid == null ? "" : d.uuid));
  j.put("epoch", new org.bson.BsonInt64(epochOf(d.uuid)));
  j.put("stage", new org.bson.BsonString("moving"));
  j.put("at", new org.bson.BsonInt64(now));
  j.put("prevSteps", new org.bson.BsonInt32(prevN));
  j.put("prevSavedAt", new org.bson.BsonInt64(prevAt instanceof Long ? ((Long) prevAt).longValue() : 0L));
  j.put("steps", steps);
  PENDING.remove(k);
  if (write0(k, j)) return j;
  if (prevAt instanceof Long) PENDING.put(k, prevAt);
  return null;
}""")
M(jr, r"""
public static org.bson.BsonDocument begin(@PKG@.WdData d, org.bson.BsonDocument step, long now) {
  Object lk = lockOf(d.key);
  synchronized (lk) { return begin0(d, step, now); }
}""")
M(jr, r"""
public static void saved0(String k, org.bson.BsonDocument j, long now) {
  j.put("stage", new org.bson.BsonString("saved"));
  j.put("savedAt", new org.bson.BsonInt64(now));
  org.bson.BsonArray st = stepsOf(j);
  if (st.size() > 0) { org.bson.BsonValue v = (org.bson.BsonValue) st.get(st.size() - 1); if (v != null && v.isDocument()) v.asDocument().put("savedAt", new org.bson.BsonInt64(now)); }
  if (write0(k, j)) PENDING.put(k, Long.valueOf(now));
}""")
M(jr, r"""
public static void saved(String k, org.bson.BsonDocument j, long now) {
  Object lk = lockOf(k);
  synchronized (lk) { saved0(k, j, now); }
}""")
M(jr, r"""
public static void abort0(String k, org.bson.BsonDocument j) {
  if (j == null) return;
  int prevN = @PKG@.WdCodec.intOf(j, "prevSteps", 0);
  long at = @PKG@.WdCodec.lngOf(j, "prevSavedAt", 0L);
  if (prevN <= 0) { delete0(k); return; }
  org.bson.BsonArray all = stepsOf(j);
  org.bson.BsonArray keep = new org.bson.BsonArray();
  for (int i = 0; i < prevN && i < all.size(); i++) keep.add((org.bson.BsonValue) all.get(i));
  j.put("steps", keep);
  j.put("stage", new org.bson.BsonString("saved"));
  j.put("prevSteps", new org.bson.BsonInt32(0));
  if (write0(k, j)) PENDING.put(k, Long.valueOf(at > 0L ? at : System.currentTimeMillis()));
}""")
M(jr, r"""
public static void abort(String k, org.bson.BsonDocument j) {
  Object lk = lockOf(k);
  synchronized (lk) { abort0(k, j); }
}""")
M(jr, r"""
public static void failed0(String k, org.bson.BsonDocument j, String why) {
  PENDING.remove(k);
  if (j == null) return;
  j.put("stage", new org.bson.BsonString("failed"));
  j.put("why", new org.bson.BsonString(why));
  write0(k, j);
}""")
M(jr, r"""
public static void failed(String k, org.bson.BsonDocument j, String why) {
  Object lk = lockOf(k);
  synchronized (lk) { failed0(k, j, why); }
}""")
# 0.2.1: the keep-window sweep, key by key under that key's lock (the 0.2 body per key)
M(jr, r"""
public static void sweepOne0(String k, long now) {
  Object at = PENDING.get(k);
  if (!(at instanceof Long) || now - ((Long) at).longValue() < (long) @PKG@.WdCfg.JKEEP_S * 1000L) return;
  org.bson.BsonDocument j = read0(k);
  if (j != null && "saved".equals(@PKG@.WdCodec.strOf(j, "stage"))) delete0(k);
  else PENDING.remove(k);
}""")
M(jr, r"""
public static void sweepOne(String k, long now) {
  Object lk = lockOf(k);
  synchronized (lk) { sweepOne0(k, now); }
}""")
M(jr, r"""
public static void sweep(long now) {
  java.util.Iterator it = new java.util.ArrayList(PENDING.keySet()).iterator();
  while (it.hasNext()) sweepOne((String) it.next(), now);
}""")
M(jr, r"""
public static int dropAll() {
  int n = 0;
  java.util.Iterator it = new java.util.ArrayList(PENDING.keySet()).iterator();
  while (it.hasNext()) { delete((String) it.next()); n++; }
  return n;
}""")
'''
s = s[:J0] + NEW_J + s[J1:]

# ---------------------------------------------------------------------------------------------------------------- WdTx: the pre-check + the repair read
rep('''  if (!@PKG@.WdJournal.PENDING.containsKey(d.key) && @PKG@.WdStore.RQ != null && java.nio.file.Files.exists(@PKG@.WdJournal.fileOf(d.key), new java.nio.file.LinkOption[0]))
    return "-An interrupted Requip change is still being checked - try again in a moment.";''',
    '''  // 0.2.1: from memory (WdJournal.hasFile - kept exact by every journal write / delete / read; no disk question on the world thread)
  if (!@PKG@.WdJournal.PENDING.containsKey(d.key) && @PKG@.WdJournal.hasFile(d.key))
    return "-An interrupted Requip change is still being checked - try again in a moment.";''')
rep('''  org.bson.BsonDocument j = @PKG@.WdJournal.read(d.key);
  if (j == null) {''', '''  // 0.2.1: the journal the join pre-warm read off the world thread, when nothing wrote / deleted it since; else read it as before
  Object[] pj = @PKG@.WdJournal.takePre(d.key);
  org.bson.BsonDocument j = pj != null ? (org.bson.BsonDocument) pj[1] : (@PKG@.WdJournal.hasFile(d.key) ? @PKG@.WdJournal.read(d.key) : null);
  if (j == null) {''')
rep('''    if (@PKG@.WdStore.RQ == null || !java.nio.file.Files.exists(@PKG@.WdJournal.fileOf(d.key), new java.nio.file.LinkOption[0])) return null;''',
    '''    if (@PKG@.WdStore.RQ == null || !@PKG@.WdJournal.hasFile(d.key)) return null;   // 0.2.1: from memory''')
rep('''      java.nio.file.Files.move(@PKG@.WdJournal.fileOf(d.key), to, new java.nio.file.CopyOption[0]);
      @PKG@.WdJournal.PENDING.remove(d.key);''', '''      java.nio.file.Files.move(@PKG@.WdJournal.fileOf(d.key), to, new java.nio.file.CopyOption[0]);
      @PKG@.WdJournal.forget(d.key);   // 0.2.1: the journal file is gone (asked again on the next question)
      @PKG@.WdJournal.PENDING.remove(d.key);''')
rep('''    if (unk.size() > 0 && !@PKG@.WdJournal.PENDING.containsKey(d.key) && java.nio.file.Files.exists(mk, new java.nio.file.LinkOption[0])
        && !java.nio.file.Files.exists(@PKG@.WdJournal.fileOf(d.key), new java.nio.file.LinkOption[0])) {''',
    '''    if (unk.size() > 0 && !@PKG@.WdJournal.PENDING.containsKey(d.key) && java.nio.file.Files.exists(mk, new java.nio.file.LinkOption[0])
        && !@PKG@.WdJournal.hasFile(d.key)) {   // 0.2.1: the journal question from memory''')

# ---------------------------------------------------------------------------------------------------------------- WdRepairTask.prewarm + WdHop.run
rep('''M(hop, r"""
public void run() {
  try {
    @WLD@ w = @PKG@.WdEng.worldOf(this.u);
    if (w != null) w.execute(this.task);
  } catch (Throwable t) { @PKG@.WdLog.warnOnce("hop", "could not hand a Requip task to a world thread: " + t); }
}""")''', '''F(rtask, "public static volatile long PREWARMS = 0L;")
# 0.2.1 (audit 9d): the join repair's disk work off the world thread - WdHop.run (the scheduler thread) calls this before it hands the task
# to the world: the profile's Requip files (WdStore.get = the cache the world task then answers from), whether a journal file exists and
# the journal itself (taken by WdTx.repair while its generation is current). A busy profile (switch / crash recovery) is not touched -
# the task waits and comes back. Never throws.
M(rtask, r"""
public void prewarm() {
  try {
    if (this.u == null || @PKG@.WdStore.RQ == null || @PKG@.WdGate.busy(this.u)) return;
    String k = @PKG@.WdStore.pkey(this.u);
    @PKG@.WdStore.get(k, this.u);
    if (@PKG@.WdJournal.hasFile(k)) @PKG@.WdJournal.preRead(k);
    PREWARMS = PREWARMS + 1L;
  } catch (Throwable t) { @PKG@.WdLog.warnOnce("prewarm", "the Requip join pre-load failed (the world task loads it instead): " + t); }
}""")
M(hop, r"""
public void run() {
  try {
    if (this.task instanceof @PKG@.WdRepairTask) ((@PKG@.WdRepairTask) this.task).prewarm();   // 0.2.1: the disk work here, not on the world thread
    @WLD@ w = @PKG@.WdEng.worldOf(this.u);
    if (w != null) w.execute(this.task);
  } catch (Throwable t) { @PKG@.WdLog.warnOnce("hop", "could not hand a Requip task to a world thread: " + t); }
}""")''')

# ---------------------------------------------------------------------------------------------------------------- 4 + 5 (fixer)
rep('''scan = cls("WdScan")
''', '''scan = cls("WdScan")
wthr = cls("WdThreads")   # 0.2.1 fixer: the private join pre-warm reader's thread factory (daemon "SkyyWardrobe-reader")
''')
rep('''  KNOWN.put(k, Boolean.valueOf(e));
  return e;
}""")
''', '''  KNOWN.put(k, Boolean.valueOf(e));
  return e;
}""")
# 0.2.1 fixer: the refusal path's second look - forget the cached answer and ask the disk once (a journal deleted / moved by hand)
M(jr, r"""
public static boolean recheck(String k) {
  if (k == null) return false;
  KNOWN.remove(k);
  RECHECKS = RECHECKS + 1L;
  return hasFile(k);
}""")
''')
rep('''F(jr, "public static final java.util.concurrent.ConcurrentHashMap KNOWN = new java.util.concurrent.ConcurrentHashMap();")
''', '''F(jr, "public static final java.util.concurrent.ConcurrentHashMap KNOWN = new java.util.concurrent.ConcurrentHashMap();")
F(jr, "public static volatile long RECHECKS = 0L;")   # 0.2.1 fixer: refusal-path disk re-checks (the harness counts them)
''')
rep('''  if (!@PKG@.WdJournal.PENDING.containsKey(d.key) && @PKG@.WdJournal.hasFile(d.key))
    return "-An interrupted Requip change is still being checked - try again in a moment.";''',
    '''  // fixer: a cached "yes" is asked once more on disk before it refuses (only then - a journal removed by hand never blocks Requip)
  if (!@PKG@.WdJournal.PENDING.containsKey(d.key) && @PKG@.WdJournal.hasFile(d.key) && @PKG@.WdJournal.recheck(d.key))
    return "-An interrupted Requip change is still being checked - try again in a moment.";''')
rep('''F(rtask, "public static volatile long PREWARMS = 0L;")
''', '''F(rtask, "public static volatile long PREWARMS = 0L;")
# 0.2.1 fixer: READER = the private join pre-warm thread (WdHop.later hands WdRepairTask hops to it); WdThreads names it
F(hop, "public static volatile java.util.concurrent.ScheduledExecutorService READER;")
wthr.addInterface(pool.get("java.util.concurrent.ThreadFactory"))
C(wthr, "public WdThreads() { }")
M(wthr, r"""
public Thread newThread(Runnable r) {
  Thread t = new Thread(r, "SkyyWardrobe-reader");
  t.setDaemon(true);
  return t;
}""")
''')
rep('''public static void later(java.util.UUID u, Runnable task, long ms) {
  try { @HSV@.SCHEDULED_EXECUTOR.schedule(''', '''public static void later(java.util.UUID u, Runnable task, long ms) {
  java.util.concurrent.ScheduledExecutorService rd = READER;   // 0.2.1 fixer: the join repair's pre-warm on the private reader
  if (rd != null && task instanceof @PKG@.WdRepairTask) {
    try { rd.schedule(new @PKG@.WdHop(u, task), ms, java.util.concurrent.TimeUnit.MILLISECONDS); return; } catch (Throwable t0) { }
  }
  try { @HSV@.SCHEDULED_EXECUTOR.schedule(''')
rep('''  getEventRegistry().registerGlobal(@PRE@.class, new @PKG@.WdReady());
''', '''  @PKG@.WdHop.READER = java.util.concurrent.Executors.newSingleThreadScheduledExecutor(new @PKG@.WdThreads());   // 0.2.1 fixer: before the join listener
  getEventRegistry().registerGlobal(@PRE@.class, new @PKG@.WdReady());
''')
rep('''  try { if (TIMER instanceof java.util.concurrent.Future) ((java.util.concurrent.Future) TIMER).cancel(false); } catch (Throwable t) { }
''', '''  try { if (TIMER instanceof java.util.concurrent.Future) ((java.util.concurrent.Future) TIMER).cancel(false); } catch (Throwable t) { }
  try { java.util.concurrent.ScheduledExecutorService rd = @PKG@.WdHop.READER; @PKG@.WdHop.READER = null; if (rd != null) rd.shutdownNow(); } catch (Throwable t1) { }   // 0.2.1 fixer
''')

# ---------------------------------------------------------------------------------------------------------------- guards
assert s.count("registerCommand(") == REG0 and s.count("registerSystem(") == SYS0, "no new command or ECS system"
jsec = s[s.index("# WdJournal: the write-ahead journal"):s.index('M(sto, r"""\npublic static @PKG@.WdData get(String k, java.util.UUID u) {')]
assert "static synchronized" not in jsec, "no class-wide journal lock left"
assert s.index("public static boolean hasFile(") < s.index("public static String run(@PKG@.WdData d, String op, java.util.ArrayList mv")
assert s.index("public void prewarm()") < s.index("if (this.task instanceof @PKG@.WdRepairTask)")
assert s.count("java.nio.file.Files.exists(@PKG@.WdJournal.fileOf(") == 2, "only the scheduler-side checks (timer, evict) still ask the disk"
_gone = sorted(ln for ln in set(OLD.split(LF)) - set(s.split(LF)))
_OK = set(old_j.split(LF)) | {
    '"""SkyyWardrobe 0.2 "Requip" - build script (javassist via jpype, tools/skyybuild.py). Derived from build_skyywardrobe_0.1.py (the SET pin,',
    "Run:   python SkyyWardrobe/build_skyywardrobe_0.2.py   -> SkyyWardrobe/SkyyWardrobe-0.2.jar   (no --deploy: tools/deploy_set.py deploys)",
    "Test:  python SkyyWardrobe/test_skyywardrobe_0.2.py --dir tools/dev/scratch/<task>/test   (bare-JVM harness)",
    'VERSION = "0.2"',
    "  if (!@PKG@.WdJournal.PENDING.containsKey(d.key) && @PKG@.WdStore.RQ != null && java.nio.file.Files.exists(@PKG@.WdJournal.fileOf(d.key), new java.nio.file.LinkOption[0]))",
    "  org.bson.BsonDocument j = @PKG@.WdJournal.read(d.key);",
    "    if (@PKG@.WdStore.RQ == null || !java.nio.file.Files.exists(@PKG@.WdJournal.fileOf(d.key), new java.nio.file.LinkOption[0])) return null;",
    "        && !java.nio.file.Files.exists(@PKG@.WdJournal.fileOf(d.key), new java.nio.file.LinkOption[0])) {",
}
_bad = [ln for ln in _gone if ln not in _OK]
assert not _bad, "0.2 lines lost by accident: %s" % _bad[:5]
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst, "(%d lines; 0.2 had %d)" % (s.count(LF), OLD.count(LF)))
