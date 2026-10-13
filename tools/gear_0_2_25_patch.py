"""Derive SkyyGear/build_skyygear_0.2.25.py from the LIVE 0.2.24 (build_skyygear_0.2.24.py = the tools/deploy_set.py SET pin, itself GENERATED
by tools/gear_0_2_24_patch.py). Edit THIS file, never the generated script; every anchor is asserted. Run:
    python tools/gear_0_2_25_patch.py      then      python SkyyGear/build_skyygear_0.2.25.py      (never --deploy)
Harness: python SkyyGear/test_skyygear_0.2.25.py --dir <empty folder inside tools/dev/scratch/>

0.2.25 = LAG FIXES ONLY (Skyy 2026-10-13: "During/ before we consolidate the mods together, lets audit the code structure, and make sure they
are working together in the smoothest easiest lag free way possible" + "work through your whole list, so everything is ready to play when
i get off work."; research/Code-Structure-Audit.md findings 5, 6, 7 + pack-wide pattern 1). No behaviour change for players, no saved data,
no setting, no command. (The planned Anvil tab becomes 0.2.26.)

1. THE STATS SNAPSHOT (finding 5: the same armor / weapon stacks re-walked 8-10x per player per second, totals rebuilt up to 3x per hit).
   New class GearSnap: per player ONE entry keyed on the IDENTITY of the worn armor stacks (an ItemStack never changes - getMetadata()
   hands out a clone, every change is a new stack: VERIFIED bytecode 2026-10-13) + GearCfg.cfgEpoch() + the GearGate entry (profile epoch
   + class skill) + GearGate.ver (bumped on every cached level change) + the skillsOn / classesOn flags + the GearCfg.STAB table; an entry
   is at most GearSnap.MAX_MS = 1000 ms old (so an asset reload / a hidden-armor-box change is picked up within a second, as before
   within the 1 s tick). The functions that walked the stacks keep their old bodies as <name>0 and their old names now read the entry
   (computed on first use, then reused): GearStats.totals (per weapon stack, up to 4 weapons; the gear:extra / pets part is still added
   on every call - it changes on its own), GearSet.counts, GearArmor.inactive / resDelta (Physical, Projectile) / hasInactive /
   hasResDelta / lockSums / fullSumsU (new: fullSums keyed per player), GearMine.compute, GearUtFx.sum. So GearTick, GearFx (armor pass,
   regen, the Untiered max Health / Mana regen), GearStats, GearUtFx, GearMine, GearArmor, GearSet and the damage path (GearHit.weaponHit,
   GearHitSys, GearArmorSys, GearUtFx.taken / onHit) all read the same snapshot. Every reader gets a COPY (int[] / double[] / HashMap)
   - the numbers are identical (the harness compares 0.2.24 and 0.2.25 on hundreds of random loadouts, levels and settings).
   GearSnap.ON (no setting; the harness flips it) = false gives the 0.2.24 path.
2. GearOpened (finding 6): load() reads the world's chest-record file with NO lock (was: inside the class monitor that put / kick wait
   on) and publishes with putIfAbsent (the first loader wins, the same maps for everyone). After a load that found more data lines than
   live positions (repeats, X lines, unreadable lines), a COMPACTION runs on the scheduler under the writer lock (WLOCK, the same lock the
   queued-line writer takes, so no line is lost): the file is rewritten atomically (tmp + fsync + ATOMIC_MOVE) with the leading comment
   lines + the LAST line of every position whose last state is not X, verbatim, in the order of those last lines - read back it gives
   exactly the same records (the harness checks it).
3. THE JOIN STAMP SCAN (finding 7): (a) our own stamp writes no longer re-trigger a scan - each setItemStackForSlot transaction the scan
   wrote is remembered per player (GearStamp.SELF, by identity) and GearInvSys skips the InventoryChangeEvent that carries it (the engine
   queues the very Transaction object setItemStackForSlot returned: ItemContainer.sendUpdate -> InventoryComponent.changeEvents ->
   InventorySystems$InventoryChangeEventSystem, VERIFIED bytecode 2026-10-13); (b) the background scans (GearStampTask, the join
   refresh) do at most GearStamp.SLOTS_PER_TASK = 12 gear slots per world task, hotbar first (the old order: hotbar, armor, tools,
   utility, storage, backpack), and continue where they stopped 250 ms later (a change during such a pass starts one more full pass);
   the commands / pages that scan before they open (/reforge, /identify, /upgrade, /smithing, /multitool, /gear migrate) still scan
   everything at once; (c) a slot holding neither gear nor a tool is skipped without reading its metadata (stampStack / lootable never
   touched those - the same result, two BSON clones less per slot); (d) the join refresh is staggered by 0-3 s (2-5 s after
   PlayerReady instead of 2 s).
4. (a) GearGate re-asks skill:fn:level only on a LEVEL SIGNAL: SkyySkills republishes skill:<uuid> (the level list) on every level up,
   class or profile change and live level-table change, and skill:overall:<uuid> (VERIFIED build_skyyskills_0.4.31.py publishNow /
   Overall.publish); GearGate.refresh polls when one of them (or the profile epoch / class skill) changed, and at the latest every 10 s
   (GearGate.POLL_MS - a level change SkyySkills does not announce is seen within 3 s instead of 1 s; fix round: was 10 s). (b) GearFx.locks / hasLock use
   a key array built once (GearFx.lockKey) instead of a string concat per stat per call. (c) Gear.bridge() is the lock-free kit form
   (tools/skyycfg.py BRIDGE_FIELD / BRIDGE_JAVA: the map cached in a static volatile field, synchronized(System.class) only on the very
   first call) - the config kit's CfgRows already had it.
FIX ROUND (critics, 2026-10-13): the chest-file compaction runs on its own daemon thread (not the engine's shared scheduler); a background
   stamp pass of several tasks sends ONE migration notice / MIGRATE line with the pass's total (was: the first batch's count); a paused /
   busy player's half-done pass retries every 2 s (was every 250 ms); GearGate.POLL_MS 10 s -> 3 s.
FIX ROUND 2 (second critics, 2026-10-13): a GearSnap ring slot is ONE pair { weapon, result } (a single reference write - a racing reader
   never pairs one weapon with another's result); GearOpened.load publishes W / PW / CH of one loader together (publish, under PUBL - a
   tiny lock, no file read); a fresh stamp pass (join refresh, scan) clears MIG (an abandoned pass's counts never reach the next notice).
ROLLBACK: 0.2.25 -> 0.2.24 is safe (no data, no setting; a compacted chests/<world>.txt is the same records in fewer lines).
"""
import os
import ast

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.2.24.py")
DST = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.2.25.py")
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.2.24"' in s and "GENERATED by tools/gear_0_2_24_patch.py" in s and "0.2.25" not in s[:400], "not the generated 0.2.24 script"
CHANGES = []


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:160])
    s = s.replace(old, new, 1)
    CHANGES.append((new, old))


def before(anchor, text):
    """insert text right before the (unique) anchor"""
    rep(anchor, text + anchor)


_set = None
for _n in ast.parse(open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf-8").read()).body:
    if isinstance(_n, ast.Assign) and any(isinstance(_t, ast.Name) and _t.id == "SET" for _t in _n.targets):
        _set = dict(ast.literal_eval(_n.value))
if _set is not None and _set.get("SkyyGear") != "0.2.24":
    print("NOTE: tools/deploy_set.py SET pins SkyyGear %s, this patch derives from 0.2.24" % _set.get("SkyyGear"))

# ================================================================================================================ docstring + version
rep('''"""SkyyGear 0.2.24 - build script (javassist via jpype). GENERATED by tools/gear_0_2_24_patch.py from the LIVE 0.2.23 (itself GENERATED by
tools/gear_0_2_23_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.2.24.py -> SkyyGear/SkyyGear-0.2.24.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.2.24.py --dir <empty folder inside tools/dev/scratch/>
''', '''"""SkyyGear 0.2.25 - build script (javassist via jpype). GENERATED by tools/gear_0_2_25_patch.py from the LIVE 0.2.24 (itself GENERATED by
tools/gear_0_2_24_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.2.25.py -> SkyyGear/SkyyGear-0.2.25.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.2.25.py --dir <empty folder inside tools/dev/scratch/>

0.2.25 = LAG FIXES ONLY (Skyy 2026-10-13 "lets audit the code structure ... lag free"; research/Code-Structure-Audit.md findings 5-7; notes:
tools/gear_0_2_25_patch.py): ONE per-player stats snapshot (GearSnap: keyed on the worn stacks' identity + config / gate epochs, at most
1 s old) read by the tick, the armor pass and the damage path - identical numbers; GearOpened reads its file outside the lock and compacts
it; the join stamp scan skips its own writes, does 12 gear slots per world task and is staggered 0-3 s; GearGate polls skill levels only
on SkyySkills' level signal; GearFx lock keys built once; the lock-free bridge. No behaviour change, no data, no setting.

--- 0.2.24 notes ---
''')
rep('VERSION = "0.2.24"\n', 'VERSION = "0.2.25"\n')

# ================================================================================================================ 4c the lock-free bridge
rep('''M(gu, r"""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""")''', '''# 0.2.25: the lock-free kit form (tools/skyycfg.py BRIDGE_FIELD / BRIDGE_JAVA; research/Code-Structure-Audit.md pack-wide pattern 1): the
# map cached in a static volatile field; synchronized(System.class) only while it is still null (the very first call)
F(gu, CFG.BRIDGE_FIELD)
for _bj in CFG.BRIDGE_JAVA:
    M(gu, _bj)''')

# GearMove = the tools/skyymove.py protocol copy, whose bridge() takes synchronized(System.class) on every call (move:<uuid> every armor pass):
# in THIS jar its body delegates to the lock-free Gear.bridge() (the same map; the shared kit file itself is not this round's)
rep('''MV.add_move_sync(gmv, CtField, CtNewMethod, PKG + ".Gear.warn")''',
    '''MV.add_move_sync(gmv, CtField, CtNewMethod, PKG + ".Gear.warn")
gmv.getDeclaredMethod("bridge").setBody("{ return %s.Gear.bridge(); }" % PKG)     # 0.2.25: the lock-free bridge (tools/gear_0_2_25_patch.py)''')

# ================================================================================================================ the new class
rep('''gufx = mk("GearUtFx")           # the Untiered lines + tricks: table, totals, combat, max Health %, Mana regen, gear:fn:utfx
UB_CLASSES = [gufx]''', '''gufx = mk("GearUtFx")           # the Untiered lines + tricks: table, totals, combat, max Health %, Mana regen, gear:fn:utfx
UB_CLASSES = [gufx]
# 0.2.25 lag fixes (tools/gear_0_2_25_patch.py)
gsnap = mk("GearSnap")          # the per-player stats snapshot (worn stacks + config / gate epochs, <= 1 s old)
PERF_CLASSES = [gsnap]''')
rep(''' + G1_CLASSES + GM_CLASSES + UB_CLASSES + TOOL_MULTI_CLASSES''', ''' + G1_CLASSES + GM_CLASSES + UB_CLASSES + PERF_CLASSES + TOOL_MULTI_CLASSES''')

# ================================================================================================================ 4a GearGate: version + level signal
rep('''F(ggt, "public static final java.util.concurrent.ConcurrentHashMap POPPED = new java.util.concurrent.ConcurrentHashMap();")
M(ggt, r"""
public static String classSkillRaw(java.util.UUID u) {''', '''F(ggt, "public static final java.util.concurrent.ConcurrentHashMap POPPED = new java.util.concurrent.ConcurrentHashMap();")
# 0.2.25: VER = UUID -> long[1], bumped on every change of a player's cached gate data (a new entry, a level read into it, a level that
# changed) - part of the GearSnap key. SIG = UUID -> Object[] { skill:<uuid>, skill:overall:<uuid>, long[] { when } } = SkyySkills'
# level signal the last poll saw; refresh re-asks skill:fn:level only when it moved (or POLL_MS passed). POLLS counts those calls.
F(ggt, "public static final java.util.concurrent.ConcurrentHashMap VER = new java.util.concurrent.ConcurrentHashMap();")
F(ggt, "public static final java.util.concurrent.ConcurrentHashMap SIG = new java.util.concurrent.ConcurrentHashMap();")
F(ggt, "public static final long POLL_MS = 3000L;")        # fix round: 3 s (was 10 s) - closer to 0.2.24's 1 s for a level change SkyySkills does not announce
F(ggt, "public static final java.util.concurrent.atomic.AtomicLong POLLS = new java.util.concurrent.atomic.AtomicLong();")
M(ggt, r"""
public static void bump(java.util.UUID u) {
  if (u == null) return;
  long[] v = (long[]) VER.get(u);
  if (v == null) {
    v = new long[1];
    Object o = VER.putIfAbsent(u, v);
    if (o != null) v = (long[]) o;
  }
  v[0] = v[0] + 1L;
}""")
M(ggt, r"""
public static long ver(java.util.UUID u) {
  if (u == null) return 0L;
  Object o = VER.get(u);
  return o instanceof long[] ? ((long[]) o)[0] : 0L;
}""")
M(ggt, "public static boolean same(Object a, Object b) { return a == null ? b == null : a.equals(b); }")
# true = poll now: SkyySkills' level list (skill:<uuid>) or Overall level (skill:overall:<uuid>) is not what the last poll saw, or the
# last poll is POLL_MS old (a level change SkyySkills does not announce); the new state is remembered
M(ggt, r"""
public static boolean signal(java.util.UUID u) {
  if (u == null) return false;
  Object lv = @PKG@.Gear.bget("skill:" + u);
  Object ov = @PKG@.Gear.bget("skill:overall:" + u);
  long now = System.currentTimeMillis();
  Object[] s = (Object[]) SIG.get(u);
  if (s != null) {
    long at = ((long[]) s[2])[0];
    if (same(s[0], lv) && same(s[1], ov) && now >= at && now - at < POLL_MS) return false;
  }
  SIG.put(u, new Object[] { lv, ov, new long[] { now } });
  return true;
}""")
M(ggt, r"""
public static String classSkillRaw(java.util.UUID u) {''')
rep('''    e = new Object[] { ep, cs, new java.util.concurrent.ConcurrentHashMap() };
    CACHE.put(u, e);
  }
  return e;''', '''    e = new Object[] { ep, cs, new java.util.concurrent.ConcurrentHashMap() };
    CACHE.put(u, e);
    bump(u);                                   // 0.2.25: the GearSnap key
  }
  return e;''')
rep('''  int n = readLevel(u, skill);
  m.put(skill, Integer.valueOf(n));
  if (n == -1)''', '''  int n = readLevel(u, skill);
  m.put(skill, Integer.valueOf(n));
  bump(u);                                     // 0.2.25: the GearSnap key
  if (n == -1)''')
rep('''  String cs = gateSkill(u, "class");
  if (cs != null && !m.containsKey(cs)) { have(u, cs); changed = true; }
  java.util.Iterator it = m.keySet().iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    int n = readLevel(u, k);
    Object o = m.get(k);
    if (!(o instanceof Integer) || ((Integer) o).intValue() != n) { m.put(k, Integer.valueOf(n)); changed = true; }
  }
  return changed;''', '''  String cs = gateSkill(u, "class");
  if (cs != null && !m.containsKey(cs)) { have(u, cs); changed = true; }
  // 0.2.25: re-ask SkyySkills only on its level signal (or a new entry / class skill above, or every POLL_MS)
  boolean sig = signal(u);
  if (!changed && !sig) return false;
  java.util.Iterator it = m.keySet().iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    int n = readLevel(u, k);
    POLLS.incrementAndGet();
    Object o = m.get(k);
    if (!(o instanceof Integer) || ((Integer) o).intValue() != n) { m.put(k, Integer.valueOf(n)); changed = true; bump(u); }
  }
  return changed;''')
rep('''M(ggt, "public static void forget(java.util.UUID u) { if (u != null) { CACHE.remove(u); POPPED.remove(u); } }")''',
    '''M(ggt, "public static void forget(java.util.UUID u) { if (u != null) { CACHE.remove(u); POPPED.remove(u); VER.remove(u); SIG.remove(u); } }")   # 0.2.25: + VER / SIG''')

# ================================================================================================================ 1 GearSnap (after GearGate)
SNAP_JAVA = r'''
# ================================================================= 0.2.25 GearSnap: THE PER-PLAYER STATS SNAPSHOT (tools/gear_0_2_25_patch.py item 1)
# E: UUID -> Object[N] entry. [0] Object[] the worn armor stacks (identity; null = no container), [1] long[] { cfgEpoch, GearGate.ver,
# born ms, skillsOn / classesOn flags }, [2] the GearGate entry (identity: profile epoch + class skill), [4] GearCfg.STAB (identity).
# Cached results (filled on first use, every reader gets a copy): [5] totals per weapon (ring of 4 pairs { w, Object[] { int[] t, Boolean ok } })
# + [6] its next index, [7] GearUtFx.sum per weapon (ring of 4: w, Object[] { double[] or null }) + [8], [9] lockSums { Float f, HashMap },
# [10] fullSums { Float f, HashMap }, [11] GearMine.compute double[], [12] GearSet.counts int[], [13] Boolean[] inactive per armor slot,
# [14] Boolean hasInactive, [15] Boolean hasResDelta, [17] Float[] resDelta per armor slot x { Physical, Projectile }.
# Valid while the stacks are the same objects, the key holds and it is younger than MAX_MS. ON = false: every reader takes the old path.
F(gsnap, "public static final java.util.concurrent.ConcurrentHashMap E = new java.util.concurrent.ConcurrentHashMap();")
F(gsnap, "public static volatile boolean ON = true;")
F(gsnap, "public static final long MAX_MS = 1000L;")
F(gsnap, "public static final int N = 20;")
F(gsnap, "public static final java.util.concurrent.atomic.AtomicLong HITS = new java.util.concurrent.atomic.AtomicLong();")
F(gsnap, "public static final java.util.concurrent.atomic.AtomicLong BUILDS = new java.util.concurrent.atomic.AtomicLong();")
M(gsnap, r"""
public static Object[] stacks(@IC@ armor) {
  if (armor == null) return null;
  int n = armor.getCapacity();
  Object[] o = new Object[n];
  for (int i = 0; i < n; i++) o[i] = armor.getItemStack((short) i);
  return o;
}""")
M(gsnap, r"""
public static boolean same(Object[] st, @IC@ armor) {
  if (st == null || armor == null) return st == null && armor == null;
  if (st.length != armor.getCapacity()) return false;
  for (int i = 0; i < st.length; i++) if (st[i] != armor.getItemStack((short) i)) return false;
  return true;
}""")
M(gsnap, "public static long flags() { return (@PKG@.GearGate.skillsOn() ? 1L : 0L) | (@PKG@.GearGate.classesOn() ? 2L : 0L); }")
M(gsnap, r"""
public static boolean valid(Object[] e, java.util.UUID u, long now) {
  if (e == null) return false;
  long[] k = (long[]) e[1];
  if (now < k[2] || now - k[2] >= MAX_MS) return false;
  if (k[0] != @PKG@.GearCfg.cfgEpoch()) return false;
  if (e[2] != (Object) @PKG@.GearGate.entry(u)) return false;
  if (k[1] != @PKG@.GearGate.ver(u)) return false;
  if (k[3] != flags()) return false;
  return e[4] == (Object) @PKG@.GearCfg.STAB;
}""")
M(gsnap, r"""
public static Object[] make(java.util.UUID u, @IC@ armor, long now) {
  Object[] e = new Object[N];
  Object ge = @PKG@.GearGate.entry(u);
  Object[] st = stacks(armor);
  e[0] = st;
  e[1] = new long[] { @PKG@.GearCfg.cfgEpoch(), @PKG@.GearGate.ver(u), now, flags() };
  e[2] = ge;
  e[4] = @PKG@.GearCfg.STAB;
  int n = st == null ? 0 : st.length;
  e[13] = new Boolean[n];
  e[17] = new Float[n * 2];
  E.put(u, e);
  BUILDS.incrementAndGet();
  return e;
}""")
# the valid entry for this player and armor container (a new one when the stacks / key changed); null = no snapshot (no player, ON off)
M(gsnap, r"""
public static Object[] entry(java.util.UUID u, @IC@ armor) {
  if (u == null || !ON) return null;
  long now = System.currentTimeMillis();
  Object[] e = (Object[]) E.get(u);
  if (e != null && same((Object[]) e[0], armor) && valid(e, u, now)) { HITS.incrementAndGet(); return e; }
  return make(u, armor, now);
}""")
# the player's valid entry whatever the container (per-stack readers), or null
M(gsnap, r"""
public static Object[] peek(java.util.UUID u) {
  if (u == null || !ON) return null;
  Object[] e = (Object[]) E.get(u);
  if (e != null && valid(e, u, System.currentTimeMillis())) return e;
  return null;
}""")
M(gsnap, r"""
public static int slotOf(Object[] e, Object s) {
  if (e == null || s == null) return -1;
  Object[] st = (Object[]) e[0];
  if (st == null) return -1;
  for (int i = 0; i < st.length; i++) if (st[i] == s) return i;
  return -1;
}""")
# a ring of 4 results per weapon stack (identity; null = no weapon) in slot sl (+ its next index in sl + 1)
# fix round 2 (code critic 2): each ring slot holds ONE pair Object[] { w, r } written with a single reference store, so a reader never
# sees one weapon's key next to another weapon's result (two threads / a ring wrap at worst overwrite a pair = a cache miss, never a mix)
M(gsnap, r"""
public static Object[] find(Object[] e, int sl, Object w) {
  Object[] a = (Object[]) e[sl];
  if (a == null) return null;
  for (int i = 0; i < 4; i++) {
    Object[] pr = (Object[]) a[i];
    if (pr != null && pr[0] == w) return (Object[]) pr[1];
  }
  return null;
}""")
M(gsnap, r"""
public static void keep(Object[] e, int sl, Object w, Object[] r) {
  if (r == null) return;
  Object[] a = (Object[]) e[sl];
  if (a == null) { a = new Object[4]; e[sl] = a; }
  int[] nx = (int[]) e[sl + 1];
  if (nx == null) { nx = new int[1]; e[sl + 1] = nx; }
  int i = nx[0] & 3;
  nx[0] = i + 1;
  a[i] = new Object[] { w, r };
}""")
M(gsnap, "public static void forget(java.util.UUID u) { if (u != null) E.remove(u); }")
M(gsnap, "public static boolean sameF(float a, float b) { return Float.floatToIntBits(a) == Float.floatToIntBits(b); }")
M(gsnap, r"""
public static String statusText() {
  return "stats snapshot " + (ON ? "on" : "OFF") + " (" + E.size() + " players, " + BUILDS.get() + " builds, " + HITS.get() + " reuses)";
}""")
'''
before('''
# ####################################################################################################################################
# 0.1.2 CHARGED ATTACK DAMAGE (1/2)''', SNAP_JAVA)

# ================================================================================================================ 1 the readers
# ---- GearSet.counts
rep('''M(gset, r"""
public static int[] counts(Object[] t, java.util.UUID u, @IC@ armor) {''', '''M(gset, r"""
public static int[] counts0(Object[] t, java.util.UUID u, @IC@ armor) {''')
before('''M(gset, r"""
public static int[] note(java.util.UUID u, @IC@ armor) {''', '''# 0.2.25: counts = the snapshot's [12] (only for the live STAB table); counts0 = the walk
M(gset, r"""
public static int[] counts(Object[] t, java.util.UUID u, @IC@ armor) {
  if (t != @PKG@.GearCfg.STAB) return counts0(t, u, armor);
  Object[] e = @PKG@.GearSnap.entry(u, armor);
  if (e == null) return counts0(t, u, armor);
  Object o = e[12];
  if (o instanceof int[]) return (int[]) ((int[]) o).clone();
  int[] c = counts0(t, u, armor);
  e[12] = c.clone();
  return c;
}""")
''')
# ---- GearStats.totals
rep('''public static int[] totals(java.util.UUID u, @IS@ weapon, @IC@ armor, boolean[] ok, boolean withExtra) {''',
    '''public static int[] totals0(java.util.UUID u, @IS@ weapon, @IC@ armor, boolean[] ok, boolean withExtra) {''')
before('''M(gst, r"""
public static int[] totalsInv(''', '''# 0.2.25: totals = the snapshot's [5] (per weapon stack; the weapon + armor part, extra() added on every call exactly as totals0 adds it)
M(gst, r"""
public static int[] totals(java.util.UUID u, @IS@ weapon, @IC@ armor, boolean[] ok, boolean withExtra) {
  Object[] e = @PKG@.GearSnap.entry(u, armor);
  if (e == null) return totals0(u, weapon, armor, ok, withExtra);
  Object[] r = @PKG@.GearSnap.find(e, 5, weapon);
  if (r == null) {
    boolean[] k = new boolean[1];
    int[] t0 = totals0(u, weapon, armor, k, false);
    r = new Object[] { t0.clone(), Boolean.valueOf(k[0]) };
    @PKG@.GearSnap.keep(e, 5, weapon, r);
  }
  int[] t = (int[]) ((int[]) r[0]).clone();
  if (withExtra) {
    int[] x = extra(u);
    if (x != null) for (int i = 0; i < t.length && i < x.length; i++) t[i] = sat((long) t[i] + (long) x[i]);
  }
  if (ok != null && ok.length > 0) ok[0] = ((Boolean) r[1]).booleanValue();
  return t;
}""")
''')
# ---- GearMine.compute
rep('''M(gmine, r"""
public static double[] compute(java.util.UUID u, @IC@ armor) {''', '''M(gmine, r"""
public static double[] compute0(java.util.UUID u, @IC@ armor) {''')
before('''M(gmine, r"""
public static void postLamp(''', '''# 0.2.25: compute = the snapshot's [11]
M(gmine, r"""
public static double[] compute(java.util.UUID u, @IC@ armor) {
  Object[] e = @PKG@.GearSnap.entry(u, armor);
  if (e == null) return compute0(u, armor);
  Object o = e[11];
  if (o instanceof double[]) return (double[]) ((double[]) o).clone();
  double[] r = compute0(u, armor);
  e[11] = r.clone();
  return r;
}""")
''')
# ---- GearArmor.inactive
rep('''M(garm, r"""
public static boolean inactive(java.util.UUID u, @IS@ s) {''', '''M(garm, r"""
public static boolean inactive0(java.util.UUID u, @IS@ s) {''')
before('''# the gear.armorWarn line for an inactive piece''', '''# 0.2.25: inactive = the snapshot's [13] for a stack the player wears (identity), else the check
M(garm, r"""
public static boolean inactive(java.util.UUID u, @IS@ s) {
  if (s == null || s.isEmpty()) return false;
  Object[] e = @PKG@.GearSnap.peek(u);
  int i = @PKG@.GearSnap.slotOf(e, s);
  if (i < 0) return inactive0(u, s);
  Boolean[] b = (Boolean[]) e[13];
  Boolean v = b[i];
  if (v != null) return v.booleanValue();
  boolean r = inactive0(u, s);
  b[i] = Boolean.valueOf(r);
  return r;
}""")
''')
# ---- GearArmor.hasInactive
rep('''M(garm, r"""
public static boolean hasInactive(java.util.UUID u, @IC@ armor) {''', '''M(garm, r"""
public static boolean hasInactive0(java.util.UUID u, @IC@ armor) {''')
before('''# a temporary container with only the active pieces''', '''# 0.2.25: hasInactive = the snapshot's [14]
M(garm, r"""
public static boolean hasInactive(java.util.UUID u, @IC@ armor) {
  if (armor == null) return false;
  Object[] e = @PKG@.GearSnap.entry(u, armor);
  if (e == null) return hasInactive0(u, armor);
  Object o = e[14];
  if (o instanceof Boolean) return ((Boolean) o).booleanValue();
  boolean r = hasInactive0(u, armor);
  e[14] = Boolean.valueOf(r);
  return r;
}""")
''')
# ---- GearArmor.lockSums
rep('''public static java.util.HashMap lockSums(java.util.UUID u, @IC@ armor, float f) {''',
    '''public static java.util.HashMap lockSums0(java.util.UUID u, @IC@ armor, float f) {''')
before('''# every piece = what the engine's own "Armor" modifier holds''', '''# 0.2.25: lockSums = the snapshot's [9] (for the same broken factor f)
M(garm, r"""
public static java.util.HashMap lockSums(java.util.UUID u, @IC@ armor, float f) {
  Object[] e = @PKG@.GearSnap.entry(u, armor);
  if (e == null) return lockSums0(u, armor, f);
  Object[] c = (Object[]) e[9];
  if (c != null && @PKG@.GearSnap.sameF(((Float) c[0]).floatValue(), f)) return new java.util.HashMap((java.util.HashMap) c[1]);
  java.util.HashMap r = lockSums0(u, armor, f);
  e[9] = new Object[] { Float.valueOf(f), new java.util.HashMap(r) };
  return r;
}""")
''')
# ---- GearArmor.fullSumsU (new, keyed per player; fullSums stays the walk)
before('''# the world's BrokenPenalties armor factor''', '''# 0.2.25: fullSumsU = fullSums through the player's snapshot [10] (for the same broken factor f)
M(garm, r"""
public static java.util.HashMap fullSumsU(java.util.UUID u, @IC@ armor, float f) {
  Object[] e = @PKG@.GearSnap.entry(u, armor);
  if (e == null) return fullSums(armor, f);
  Object[] c = (Object[]) e[10];
  if (c != null && @PKG@.GearSnap.sameF(((Float) c[0]).floatValue(), f)) return new java.util.HashMap((java.util.HashMap) c[1]);
  java.util.HashMap r = fullSums(armor, f);
  e[10] = new Object[] { Float.valueOf(f), new java.util.HashMap(r) };
  return r;
}""")
''')
rep('''    locks(u, m, want, up ? @PKG@.GearArmor.fullSums(armor, f) : null, armor, up);''',
    '''    locks(u, m, want, up ? @PKG@.GearArmor.fullSumsU(u, armor, f) : null, armor, up);      // 0.2.25: the snapshot''')
rep('''    Object hfo = @PKG@.GearArmor.fullSums(inv.getArmor(), @PKG@.GearArmor.brokenFactor(cb.getExternalData())).get(Integer.valueOf(hix));''',
    '''    Object hfo = @PKG@.GearArmor.fullSumsU(u, inv.getArmor(), @PKG@.GearArmor.brokenFactor(cb.getExternalData())).get(Integer.valueOf(hix));      // 0.2.25: the snapshot''')
# ---- GearArmor.resDelta (Physical / Projectile of a worn stack)
rep('''M(garm, r"""
public static float resDelta(java.util.UUID u, @IS@ s, String cause) {''', '''M(garm, r"""
public static float resDelta0(java.util.UUID u, @IS@ s, String cause) {''')
before('''# GearHitSys keeps the pre-armor amount for a player victim when this is true''', '''# 0.2.25: resDelta = the snapshot's [17] for a worn stack and the causes the callers ask (Physical, Projectile), else the walk
M(garm, r"""
public static float resDelta(java.util.UUID u, @IS@ s, String cause) {
  if (s == null || s.isEmpty()) return 0.0f;
  int c = "Physical".equals(cause) ? 0 : ("Projectile".equals(cause) ? 1 : -1);
  if (c < 0) return resDelta0(u, s, cause);
  Object[] e = @PKG@.GearSnap.peek(u);
  int i = @PKG@.GearSnap.slotOf(e, s);
  if (i < 0) return resDelta0(u, s, cause);
  Float[] rd = (Float[]) e[17];
  Float v = rd[i * 2 + c];
  if (v != null) return v.floatValue();
  float r = resDelta0(u, s, cause);
  rd[i * 2 + c] = Float.valueOf(r);
  return r;
}""")
''')
# ---- GearArmor.hasResDelta
rep('''M(garm, r"""
public static boolean hasResDelta(java.util.UUID u, @IC@ armor) {''', '''M(garm, r"""
public static boolean hasResDelta0(java.util.UUID u, @IC@ armor) {''')
before('''# add a multiplier delta to the map entry of one cause id''', '''# 0.2.25: hasResDelta = the snapshot's [15]
M(garm, r"""
public static boolean hasResDelta(java.util.UUID u, @IC@ armor) {
  if (armor == null) return false;
  Object[] e = @PKG@.GearSnap.entry(u, armor);
  if (e == null) return hasResDelta0(u, armor);
  Object o = e[15];
  if (o instanceof Boolean) return ((Boolean) o).booleanValue();
  boolean r = hasResDelta0(u, armor);
  e[15] = Boolean.valueOf(r);
  return r;
}""")
''')
# ---- GearUtFx.sum
rep('''M(gufx, r"""
public static double[] sum(java.util.UUID u, @IS@ weapon, @IC@ armor) {''', '''M(gufx, r"""
public static double[] sum0(java.util.UUID u, @IS@ weapon, @IC@ armor) {''')
before('''# the max Health % as ONE additive MAX modifier skyygear_ut_hp''', '''# 0.2.25: sum = the snapshot's [7] (per weapon stack)
M(gufx, r"""
public static double[] sum(java.util.UUID u, @IS@ weapon, @IC@ armor) {
  Object[] e = @PKG@.GearSnap.entry(u, armor);
  if (e == null) return sum0(u, weapon, armor);
  Object[] r = @PKG@.GearSnap.find(e, 7, weapon);
  if (r == null) {
    double[] v = sum0(u, weapon, armor);
    Object vc = null;
    if (v != null) vc = v.clone();
    r = new Object[] { vc };
    @PKG@.GearSnap.keep(e, 7, weapon, r);
  }
  double[] o = (double[]) r[0];
  if (o == null) return null;
  return (double[]) o.clone();
}""")
''')
# ---- the snapshot leaves with the player (PART B cleanup)
rep('''  @PKG@.GearUtFx.forget(u);                   // 0.2.16: the Untiered Mana regen source
  try { @PKG@.GearMove.post(u, "@MOVESRC@", "flat", 0.0f, 0.0f, 0.0f); } catch (Throwable t) { }''',
    '''  @PKG@.GearUtFx.forget(u);                   // 0.2.16: the Untiered Mana regen source
  @PKG@.GearSnap.forget(u);                   // 0.2.25: the stats snapshot
  try { @PKG@.GearMove.post(u, "@MOVESRC@", "flat", 0.0f, 0.0f, 0.0f); } catch (Throwable t) { }''')

# ================================================================================================================ 4b GearFx lock keys
before('''# follow-up review 5: does this stat map carry any skyygear_lock_ modifier''', '''# 0.2.25: the lock modifier key of stat i (LOCK + the stat id), built once per index (copy-on-write array); a stat the asset map does not
# know yet ("Stat <i>", the GearView.statName fallback) is never kept
F(gfx, "public static volatile String[] LKEYS = null;")
M(gfx, r"""
public static String lockKey(int i) {
  String[] k = LKEYS;
  if (k != null && i >= 0 && i < k.length && k[i] != null) return k[i];
  String nm = @PKG@.GearView.statName(i);
  String key = LOCK + nm;
  if (i >= 0 && i < 1024 && !nm.startsWith("Stat ")) {
    int n = k == null ? 64 : k.length;
    if (n <= i) n = i + 1;
    String[] nk = new String[n];
    if (k != null) System.arraycopy(k, 0, nk, 0, k.length);
    nk[i] = key;
    LKEYS = nk;
  }
  return key;
}""")
''')
rep('''    try { if (m.get(i) != null && m.getModifier(i, LOCK + @PKG@.GearView.statName(i)) != null) return true; } catch (Throwable t) { }''',
    '''    try { if (m.get(i) != null && m.getModifier(i, lockKey(i)) != null) return true; } catch (Throwable t) { }''')
rep('''    String key = LOCK + @PKG@.GearView.statName(i);''', '''    String key = lockKey(i);''')

# ================================================================================================================ 2 GearOpened
rep('''F(gopn, "public String pre;")
C(gopn, "public GearOpened() { this.pre = null; }")
C(gopn, "public GearOpened(String k) { this.pre = k; }")''', '''F(gopn, "public String pre;")
F(gopn, "public String cmp;")       # 0.2.25: a compaction task (the world key)
F(gopn, "public static final java.util.concurrent.atomic.AtomicLong COMPACTED = new java.util.concurrent.atomic.AtomicLong();")
C(gopn, "public GearOpened() { this.pre = null; this.cmp = null; }")
C(gopn, "public GearOpened(String k) { this.pre = k; this.cmp = null; }")
C(gopn, "public GearOpened(String k, boolean compact) { this.pre = compact ? null : k; this.cmp = compact ? k : null; }")''')
rep('''M(gopn, r"""
public static void read(String k, java.util.concurrent.ConcurrentHashMap m, java.util.concurrent.ConcurrentHashMap pm, java.util.concurrent.ConcurrentHashMap ch) {
  java.nio.file.Path f = file(k);
  if (f == null || !java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return;
  try {
    java.util.List ls = java.nio.file.Files.readAllLines(f, java.nio.charset.StandardCharsets.UTF_8);
    for (int i = 0; i < ls.size(); i++) {
      String l = ((String) ls.get(i)).trim();
      if (l.length() == 0 || l.startsWith("#")) continue;
      String[] p = l.split("\\\\s+");''', '''# 0.2.25: read2 = read + the number of data lines (non-empty, not a comment) - load() compacts the file when that is more than the
# positions it kept
M(gopn, r"""
public static int read2(String k, java.util.concurrent.ConcurrentHashMap m, java.util.concurrent.ConcurrentHashMap pm, java.util.concurrent.ConcurrentHashMap ch) {
  java.nio.file.Path f = file(k);
  int data = 0;
  if (f == null || !java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return 0;
  try {
    java.util.List ls = java.nio.file.Files.readAllLines(f, java.nio.charset.StandardCharsets.UTF_8);
    for (int i = 0; i < ls.size(); i++) {
      String l = ((String) ls.get(i)).trim();
      if (l.length() == 0 || l.startsWith("#")) continue;
      data++;
      String[] p = l.split("\\\\s+");''')
rep('''        ch.put(Long.valueOf(ck(x, z)), Boolean.TRUE);
      } catch (Throwable t2) { }
    }
  } catch (Throwable t) { @PKG@.Gear.warn("could not read " + f + " - the containers listed there are decided again on their next open (only gear without a document is ever touched): " + t); }
}""")
M(gopn, r"""
public static synchronized java.util.concurrent.ConcurrentHashMap load(String k) {
  Object o = W.get(k);
  if (o != null) return (java.util.concurrent.ConcurrentHashMap) o;
  java.util.concurrent.ConcurrentHashMap m = new java.util.concurrent.ConcurrentHashMap();
  java.util.concurrent.ConcurrentHashMap pm = new java.util.concurrent.ConcurrentHashMap();
  java.util.concurrent.ConcurrentHashMap ch = new java.util.concurrent.ConcurrentHashMap();
  if (!TEMP.containsKey(k)) read(k, m, pm, ch);
  PW.put(k, pm);
  CH.put(k, ch);
  W.put(k, m);
  return m;
}""")''', '''        ch.put(Long.valueOf(ck(x, z)), Boolean.TRUE);
      } catch (Throwable t2) { }
    }
  } catch (Throwable t) { @PKG@.Gear.warn("could not read " + f + " - the containers listed there are decided again on their next open (only gear without a document is ever touched): " + t); }
  return data;
}""")
M(gopn, r"""
public static void read(String k, java.util.concurrent.ConcurrentHashMap m, java.util.concurrent.ConcurrentHashMap pm, java.util.concurrent.ConcurrentHashMap ch) {
  read2(k, m, pm, ch);
}""")
# 0.2.25 COMPACTION (scheduler, under WLOCK = no queued line is written meanwhile): the leading comment lines + the LAST line of every
# position whose last state is not X, verbatim (trimmed, as read() reads it), in the order of those last lines; unreadable lines go.
# Atomic: tmp + fsync + ATOMIC_MOVE (REPLACE_EXISTING when the file system has no atomic move). Returns the lines dropped (0 = nothing
# to do, -1 = no file / a temporary world / failed - the file stays as it was).
# fix round (engine critic 2): the compaction (file read + tmp write + fsync + move) runs on a short-lived daemon thread of its own
# "SkyyGear-Compact" (once per world per start, only when the file had repeated lines), after COMPACT_DELAY_MS - never on
# HytaleServer.SCHEDULED_EXECUTOR, the engine's one shared scheduler thread
F(gopn, "public static final long COMPACT_DELAY_MS = 2000L;")
M(gopn, r"""
public static int compact0(String k) {
  java.nio.file.Path f = file(k);
  if (f == null || k == null || TEMP.containsKey(k) || !java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return -1;
  java.nio.file.Path tmp = null;
  try {
    java.util.List ls = java.nio.file.Files.readAllLines(f, java.nio.charset.StandardCharsets.UTF_8);
    java.util.ArrayList head = new java.util.ArrayList();
    java.util.LinkedHashMap last = new java.util.LinkedHashMap();
    int data = 0;
    for (int i = 0; i < ls.size(); i++) {
      String l = ((String) ls.get(i)).trim();
      if (l.length() == 0) continue;
      if (l.startsWith("#")) { if (data == 0) head.add(l); continue; }
      data++;
      String[] p = l.split("\\\\s+");
      if (p.length < 3) continue;
      Long key = null;
      try { key = Long.valueOf(pack(Integer.parseInt(p[0]), Integer.parseInt(p[1]), Integer.parseInt(p[2]))); } catch (Throwable t2) { key = null; }
      if (key == null) continue;
      last.remove(key);
      char c = p.length > 3 && p[3].length() == 1 ? p[3].charAt(0) : 'W';
      if (c == 'X') continue;
      last.put(key, l);
    }
    if (data <= last.size()) return 0;
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < head.size(); i++) sb.append((String) head.get(i)).append('\\n');
    if (head.isEmpty()) sb.append("# SkyyGear - the containers of world " + k + " whose first open (or break) was decided: x y z state time [placer=<uuid>] note. W = world container, its gear was made unidentified; P = player storage, never touched; L = loot container not opened yet; T = loot container, tagged; X = forgotten (a new container or a regenerated chunk there). The last line of a position wins. Delete this file while the server is stopped to decide every container again.\\n");
    java.util.Iterator it = last.values().iterator();
    while (it.hasNext()) sb.append((String) it.next()).append('\\n');
    tmp = f.resolveSibling(f.getFileName().toString() + ".tmp");
    java.io.FileOutputStream out = new java.io.FileOutputStream(tmp.toFile());
    try {
      out.write(sb.toString().getBytes("UTF-8"));
      out.flush();
      out.getFD().sync();
    } finally { out.close(); }
    try {
      java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.ATOMIC_MOVE, java.nio.file.StandardCopyOption.REPLACE_EXISTING });
    } catch (java.nio.file.AtomicMoveNotSupportedException am) {
      java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
    }
    COMPACTED.incrementAndGet();
    return data - last.size();
  } catch (Throwable t) {
    try { if (tmp != null) java.nio.file.Files.deleteIfExists(tmp); } catch (Throwable t3) { }
    @PKG@.Gear.warnOnce("compact:" + k, "could not compact " + f + " (it stays as it was; nothing is lost): " + t);
    return -1;
  }
}""")
M(gopn, r"""
public static int compact(String k) {
  int r;
  synchronized (WLOCK) { r = compact0(k); }
  return r;
}""")
M(gopn, r"""
public static void compactLater(String k) {
  try {
    Thread th = new Thread(new @PKG@.GearOpened(k, true), "SkyyGear-Compact");
    th.setDaemon(true);
    th.start();
  } catch (Throwable t) { }
}""")
# fix round 2 (code critic 3): the three maps of ONE loader are published together under PUBL (no file read inside, never the class
# monitor): the winner's W / PW / CH, never W from one loader and PW / CH from another. null = this caller won.
F(gopn, "public static final Object PUBL = new Object();")
M(gopn, r"""
public static java.util.concurrent.ConcurrentHashMap publish0(String k, java.util.concurrent.ConcurrentHashMap m, java.util.concurrent.ConcurrentHashMap pm, java.util.concurrent.ConcurrentHashMap ch) {
  Object o = W.get(k);
  if (o != null) return (java.util.concurrent.ConcurrentHashMap) o;
  PW.put(k, pm);
  CH.put(k, ch);
  W.put(k, m);
  return null;
}""")
M(gopn, r"""
public static java.util.concurrent.ConcurrentHashMap publish(String k, java.util.concurrent.ConcurrentHashMap m, java.util.concurrent.ConcurrentHashMap pm, java.util.concurrent.ConcurrentHashMap ch) {
  java.util.concurrent.ConcurrentHashMap r;
  synchronized (PUBL) { r = publish0(k, m, pm, ch); }
  return r;
}""")
# 0.2.25: the file is read with NO lock (the class monitor is only take / kick now); the first loader's maps are published (publish:
# every caller gets the same W map and its PW / CH); more data lines than positions = compact later
M(gopn, r"""
public static java.util.concurrent.ConcurrentHashMap load(String k) {
  Object o = W.get(k);
  if (o != null) return (java.util.concurrent.ConcurrentHashMap) o;
  java.util.concurrent.ConcurrentHashMap m = new java.util.concurrent.ConcurrentHashMap();
  java.util.concurrent.ConcurrentHashMap pm = new java.util.concurrent.ConcurrentHashMap();
  java.util.concurrent.ConcurrentHashMap ch = new java.util.concurrent.ConcurrentHashMap();
  int data = 0;
  if (!TEMP.containsKey(k)) data = read2(k, m, pm, ch);
  java.util.concurrent.ConcurrentHashMap prev = publish(k, m, pm, ch);
  if (prev != null) return prev;
  if (data > m.size()) compactLater(k);
  return m;
}""")''')
rep('''public void run() {
  if (this.pre != null) {
    try { load(this.pre); } catch (Throwable t) { }
    return;
  }
  flush();
}""")''', '''public void run() {
  if (this.cmp != null) {
    try { Thread.sleep(COMPACT_DELAY_MS); compact(this.cmp); } catch (Throwable t) { }      // fix round: on its own thread (compactLater)
    return;
  }
  if (this.pre != null) {
    try { load(this.pre); } catch (Throwable t) { }
    return;
  }
  flush();
}""")''')

# ================================================================================================================ 3 the join stamp scan
rep('''F(gsp, "public static final java.util.concurrent.ConcurrentHashMap RATE = new java.util.concurrent.ConcurrentHashMap();")   # UUID -> long[]{windowStart, writes, pausedUntil}''',
    '''F(gsp, "public static final java.util.concurrent.ConcurrentHashMap RATE = new java.util.concurrent.ConcurrentHashMap();")   # UUID -> long[]{windowStart, writes, pausedUntil}
# 0.2.25: SELF = UUID -> Map (identity) of the transactions our own stamp writes returned (GearInvSys skips their InventoryChangeEvent);
# CUR = UUID -> int[] { section, slot } where a background pass goes on; AGAIN = UUID -> TRUE: a change came during a pass (one more
# full pass after it); SLOTS_PER_TASK = gear slots per background world task; SKIPPED = own events skipped (status / harness)
F(gsp, "public static final java.util.concurrent.ConcurrentHashMap SELF = new java.util.concurrent.ConcurrentHashMap();")
F(gsp, "public static final java.util.concurrent.ConcurrentHashMap CUR = new java.util.concurrent.ConcurrentHashMap();")
F(gsp, "public static final java.util.concurrent.ConcurrentHashMap AGAIN = new java.util.concurrent.ConcurrentHashMap();")
F(gsp, "public static final int SLOTS_PER_TASK = 12;")
F(gsp, "public static final java.util.concurrent.atomic.AtomicLong SKIPPED = new java.util.concurrent.atomic.AtomicLong();")
# fix round (engine critic off-lens): MIG = UUID -> int[] { stamped, migrated } added up over the tasks of one background pass; the
# migration notice + the MIGRATE log line come once, with the pass's total, when the pass ends (0.2.24: one scan = one notice)
F(gsp, "public static final java.util.concurrent.ConcurrentHashMap MIG = new java.util.concurrent.ConcurrentHashMap();")''')
before('''# one stack -> the stack it should be (same object = nothing to do). cnt: [0] stamped Normal, [1] migrated, [2] re-rendered''',
       '''# 0.2.25: our own stamp write (a transaction that succeeded) - its InventoryChangeEvent will not ask for another scan
M(gsp, r"""
public static void selfNote(java.util.UUID u, Object t) {
  if (u == null || t == null) return;
  if (t instanceof @TXN@ && !((@TXN@) t).succeeded()) return;
  java.util.Map m = (java.util.Map) SELF.get(u);
  if (m == null) {
    m = java.util.Collections.synchronizedMap(new java.util.IdentityHashMap());
    Object o = SELF.putIfAbsent(u, m);
    if (o != null) m = (java.util.Map) o;
  }
  if (m.size() > 512) m.clear();
  m.put(t, Boolean.TRUE);
}""")
M(gsp, r"""
public static boolean selfSeen(java.util.UUID u, Object t) {
  if (u == null || t == null) return false;
  java.util.Map m = (java.util.Map) SELF.get(u);
  if (m == null || m.remove(t) == null) return false;
  SKIPPED.incrementAndGet();
  return true;
}""")
''')
rep('''M(gsp, r"""
public static int[] scan(@PR@ pr, @INV@ inv) {
  int[] cnt = new int[4];
  if (pr == null || inv == null) return cnt;
  java.util.UUID u = pr.getUuid();
  LAST.put(u, Long.valueOf(System.currentTimeMillis()));
  if (@PKG@.Gear.busy(u) || paused(u, 0)) return cnt;
  boolean loot = @PKG@.GearChestOpen.looting(u);
  try { @PKG@.GearSet.note(u, inv.getArmor()); } catch (Throwable tsn) { }     // 0.2.14: the set tooltip's worn count, before any re-render
  for (int k = 0; k < SCAN.length; k++) {
    @IC@ c = section(inv, SCAN[k]);
    if (c == null) continue;
    int cap = c.getCapacity();
    for (int i = 0; i < cap; i++) {
      @IS@ s = c.getItemStack((short) i);
      if (s == null || s.isEmpty()) continue;
      if (@PKG@.GearData.state(s.getMetadata()) == 0 && held(u, s.getItemId())) continue;''', '''# 0.2.25: scanSome = at most max gear slots this task, from where the last background pass stopped (CUR); scan = everything at once
# (the commands / pages that scan before they open). A slot that holds neither gear nor a tool is skipped before any metadata read
# (stampStack / lootable never touch those). Our own writes are remembered (selfNote).
M(gsp, r"""
public static int[] scanSome(@PR@ pr, @INV@ inv, int max) {
  int[] cnt = new int[4];
  if (pr == null || inv == null) return cnt;
  java.util.UUID u = pr.getUuid();
  LAST.put(u, Long.valueOf(System.currentTimeMillis()));
  if (@PKG@.Gear.busy(u) || paused(u, 0)) return cnt;
  boolean loot = @PKG@.GearChestOpen.looting(u);
  java.util.Map sm = (java.util.Map) SELF.get(u);
  if (sm != null) sm.clear();
  try { @PKG@.GearSet.note(u, inv.getArmor()); } catch (Throwable tsn) { }     // 0.2.14: the set tooltip's worn count, before any re-render
  int[] cur = (int[]) CUR.remove(u);
  int k0 = cur == null ? 0 : cur[0];
  int i0 = cur == null ? 0 : cur[1];
  int budget = max;
  boolean more = false;
  for (int k = k0; k < SCAN.length && !more; k++) {
    @IC@ c = section(inv, SCAN[k]);
    if (c == null) continue;
    int cap = c.getCapacity();
    for (int i = (k == k0 ? i0 : 0); i < cap; i++) {
      @IS@ s = c.getItemStack((short) i);
      if (s == null || s.isEmpty()) continue;
      String sid = s.getItemId();
      if (!@PKG@.GearData.isGear(sid) && !@PKG@.GearData.isTool(sid)) continue;
      if (budget <= 0) { CUR.put(u, new int[] { k, i }); more = true; break; }
      budget--;
      if (@PKG@.GearData.state(s.getMetadata()) == 0 && held(u, s.getItemId())) continue;''')
rep('''      @IS@ ns = stampStack(s, u, cnt);
      if (ns == s) continue;
      try { c.setItemStackForSlot((short) i, ns); } catch (Throwable t) { @PKG@.Gear.warnOnce("scanset", "stamp write failed: " + t); }
    }
  }
  paused(u, cnt[0] + cnt[1] + cnt[2] + cnt[3]);
  if (cnt[1] > 0) {
    notice(pr, cnt[1]);
    @PKG@.GearLog.line("MIGRATE " + pr.getUsername() + " " + u + " migrated=" + cnt[1] + " stamped=" + cnt[0]);
  }
  return cnt;
}""")''', '''      @IS@ ns = stampStack(s, u, cnt);
      if (ns == s) continue;
      try { selfNote(u, c.setItemStackForSlot((short) i, ns)); } catch (Throwable t) { @PKG@.Gear.warnOnce("scanset", "stamp write failed: " + t); }
    }
  }
  paused(u, cnt[0] + cnt[1] + cnt[2] + cnt[3]);
  int stp = cnt[0];
  int mig = cnt[1];
  if (more || MIG.containsKey(u)) {                 // fix round: a pass of several tasks = ONE notice with the pass's total
    int[] acc = (int[]) MIG.get(u);
    if (acc == null) { acc = new int[2]; MIG.put(u, acc); }
    acc[0] = acc[0] + cnt[0];
    acc[1] = acc[1] + cnt[1];
    if (more) return cnt;
    MIG.remove(u);
    stp = acc[0];
    mig = acc[1];
  }
  if (mig > 0) {
    notice(pr, mig);
    @PKG@.GearLog.line("MIGRATE " + pr.getUsername() + " " + u + " migrated=" + mig + " stamped=" + stp);
  }
  return cnt;
}""")
M(gsp, r"""
public static int[] scan(@PR@ pr, @INV@ inv) {
  if (pr != null) { CUR.remove(pr.getUuid()); MIG.remove(pr.getUuid()); }     // fix round 2: a fresh pass (no counts of an abandoned one)
  return scanSome(pr, inv, 2147483647);
}""")''')
# dirty moves before GearStampTask.run (run calls follow, follow calls dirty; javassist: methods before callers) and learns AGAIN
rep('''    @PKG@.GearStamp.QUEUED.remove(u);
    java.util.UUID now = this.pr.getWorldUuid();
    if (this.hop != null && (now == null || !now.equals(this.hop))) return;
    @PKG@.GearStamp.scan(this.pr, @PKG@.GearStamp.invOf(this.pr));''', '''    @PKG@.GearStamp.QUEUED.remove(u);
    java.util.UUID now = this.pr.getWorldUuid();
    if (this.hop != null && (now == null || !now.equals(this.hop))) return;
    @PKG@.GearStamp.scanSome(this.pr, @PKG@.GearStamp.invOf(this.pr), @PKG@.GearStamp.SLOTS_PER_TASK);      // 0.2.25: 12 gear slots a task
    @PKG@.GearStamp.follow(this.pr);''')
rep('''M(gsp, r"""
public static void dirty(@PR@ pr, @WLD@ w) {
  if (pr == null) return;
  java.util.UUID u = pr.getUuid();
  if (QUEUED.putIfAbsent(u, Boolean.TRUE) != null) return;
  try {
    Object l = LAST.get(u);
    long wait = (l instanceof Long ? ((Long) l).longValue() : 0L) + @PKG@.GearDefs.SCAN_GAP_MS - System.currentTimeMillis();
    if (wait <= 0L && w != null) w.execute(new @PKG@.GearStampTask(pr, true, pr.getWorldUuid()));
    else @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.GearStampTask(pr, false, null), wait < 1L ? 1L : wait, java.util.concurrent.TimeUnit.MILLISECONDS);
  } catch (Throwable t) { QUEUED.remove(u); }
}""")
''', '''# 0.2.25: GearStamp.dirty moved up (right after the GearStampTask constructor: GearStampTask.run calls follow -> dirty0)
''')
rep('''C(gspt, "public GearStampTask(@PR@ pr, boolean onWorld, java.util.UUID hop) { this.pr = pr; this.onWorld = onWorld; this.hop = hop; }")''',
    '''C(gspt, "public GearStampTask(@PR@ pr, boolean onWorld, java.util.UUID hop) { this.pr = pr; this.onWorld = onWorld; this.hop = hop; }")
# 0.2.25: dirty0 = the 0.2.24 dirty (moved here: GearStampTask.run calls follow); dirty = a change from outside - while a background pass
# is under way it also asks for one more full pass after it (AGAIN); follow continues a pass through dirty0 (never AGAIN)
M(gsp, r"""
public static void dirty0(@PR@ pr, @WLD@ w) {
  if (pr == null) return;
  java.util.UUID u = pr.getUuid();
  if (QUEUED.putIfAbsent(u, Boolean.TRUE) != null) return;
  try {
    Object l = LAST.get(u);
    long wait = (l instanceof Long ? ((Long) l).longValue() : 0L) + @PKG@.GearDefs.SCAN_GAP_MS - System.currentTimeMillis();
    if (wait <= 0L && w != null) w.execute(new @PKG@.GearStampTask(pr, true, pr.getWorldUuid()));
    else @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.GearStampTask(pr, false, null), wait < 1L ? 1L : wait, java.util.concurrent.TimeUnit.MILLISECONDS);
  } catch (Throwable t) { QUEUED.remove(u); }
}""")
# fix round (code critic 1): a later background task (SkyyGear's scheduler hop, coalesced like dirty0); follow uses it while the player
# is paused / busy so a half-done pass waits PAUSE_RETRY_MS per retry instead of being re-queued every 250 ms
F(gsp, "public static final long PAUSE_RETRY_MS = 2000L;")
M(gsp, r"""
public static void dirtyIn(@PR@ pr, long ms) {
  if (pr == null) return;
  java.util.UUID u = pr.getUuid();
  if (QUEUED.putIfAbsent(u, Boolean.TRUE) != null) return;
  try { @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.GearStampTask(pr, false, null), ms < 1L ? 1L : ms, java.util.concurrent.TimeUnit.MILLISECONDS); }
  catch (Throwable t) { QUEUED.remove(u); }
}""")
M(gsp, r"""
public static void dirty(@PR@ pr, @WLD@ w) {
  if (pr == null) return;
  if (CUR.containsKey(pr.getUuid())) AGAIN.put(pr.getUuid(), Boolean.TRUE);
  dirty0(pr, w);
}""")
# 0.2.25: after a background task: the pass goes on (CUR), or one more full pass when a change came during it (AGAIN)
M(gsp, r"""
public static void follow(@PR@ pr) {
  if (pr == null) return;
  java.util.UUID u = pr.getUuid();
  if (CUR.containsKey(u)) {
    if (@PKG@.Gear.busy(u) || paused(u, 0)) { dirtyIn(pr, PAUSE_RETRY_MS); return; }      // fix round: no 250 ms loop while paused
    dirty0(pr, null);
    return;
  }
  if (AGAIN.remove(u) != null) dirty0(pr, null);
}""")''')
rep('''M(gsp, "public static void forget(java.util.UUID u) { if (u != null) { PENDING.remove(u); QUEUED.remove(u); LAST.remove(u); RATE.remove(u); } }")''',
    '''M(gsp, "public static void forget(java.util.UUID u) { if (u != null) { PENDING.remove(u); QUEUED.remove(u); LAST.remove(u); RATE.remove(u); SELF.remove(u); CUR.remove(u); AGAIN.remove(u); MIG.remove(u); } }")   # 0.2.25: + SELF / CUR / AGAIN (+ MIG, fix round)''')
# GearInvSys: our own write's event asks for nothing
assert 'B.probe(pool, ICE, "getTransaction")' not in s
rep('''event_system(ginv, "GearInvSys", ICE, PLAYER_Q, r"""
    @REF@ r = chunk.getReferenceTo(idx);
    if (r == null) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null) return;''', '''B.probe(pool, ICE, "getTransaction")     # 0.2.25: the transaction the event carries (the very object setItemStackForSlot returned)
event_system(ginv, "GearInvSys", ICE, PLAYER_Q, r"""
    @REF@ r = chunk.getReferenceTo(idx);
    if (r == null) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null) return;
    if (ev instanceof @ICE@ && @PKG@.GearStamp.selfSeen(pr.getUuid(), ((@ICE@) ev).getTransaction())) return;     // 0.2.25: our own stamp write''')
# the join refresh: a full background pass (from the hotbar), 12 gear slots a task, staggered 0-3 s
rep('''    @PKG@.GearGate.refresh(this.pr.getUuid());
    int[] cnt = @PKG@.GearStamp.scan(this.pr, inv);''', '''    @PKG@.GearGate.refresh(this.pr.getUuid());
    @PKG@.GearStamp.CUR.remove(this.pr.getUuid());       // 0.2.25: a fresh pass from the hotbar, 12 gear slots a task
    @PKG@.GearStamp.MIG.remove(this.pr.getUuid());       // fix round 2: no counts of an abandoned pass in this pass's notice
    int[] cnt = @PKG@.GearStamp.scanSome(this.pr, inv, @PKG@.GearStamp.SLOTS_PER_TASK);
    @PKG@.GearStamp.follow(this.pr);''')
rep('''    new @PKG@.GearRefreshTask(pr).later(2000L);''',
    '''    new @PKG@.GearRefreshTask(pr).later(2000L + java.util.concurrent.ThreadLocalRandom.current().nextLong(3001L));     // 0.2.25: staggered 0-3 s''')

# ================================================================================================================ checks on the result
_code = s[s.index('VERSION = "0.2.25"'):]
assert "synchronized (java.lang.System.class) {\n    Object o = System.getProperties().get(\"skyy.bridge\");" not in _code
assert _code.count("LOCK + @PKG@.GearView.statName(") == 0 and _code.count("lockKey(i)") == 2
assert "public static synchronized java.util.concurrent.ConcurrentHashMap load(String k)" not in _code
# javassist order: definitions before their callers
for a_, b_ in (("public static Object[] entry(java.util.UUID u, @IC@ armor)", "public static int[] counts(Object[] t"),
               ("public static int[] counts0(", "public static int[] counts(Object[] t"),
               ("public static int[] counts(Object[] t", "public static int[] note(java.util.UUID u, @IC@ armor)"),
               ("public static int[] totals0(", "public static int[] totals(java.util.UUID"),
               ("public static int[] totals(java.util.UUID", "public static int[] totalsInv("),
               ("public static double[] compute(java.util.UUID u, @IC@ armor)", "public static double[] note(java.util.UUID u, @IC@ armor)"),
               ("public static boolean inactive(java.util.UUID u, @IS@ s)", "public static String why(java.util.UUID u, @IS@ s)"),
               ("public static float resDelta(java.util.UUID", "public static boolean hasResDelta0("),
               ("public static java.util.HashMap fullSumsU(", "public static void armorPass("),
               ("public static double[] sum(java.util.UUID u, @IS@ weapon", "public static double taken("),
               ("public static String lockKey(", "public static boolean hasLock("),
               ("public static void dirty(@PR@ pr, @WLD@ w)", "@PKG@.GearStamp.follow(this.pr);\n  } catch (Throwable t) {\n    if (u != null)"),
               ("public static void follow(@PR@ pr)", "@PKG@.GearStamp.follow(this.pr);\n  } catch (Throwable t) {\n    if (u != null)"),
               ("public static int compact0(", "public static java.util.concurrent.ConcurrentHashMap load(String k)"),
               ("public static java.util.concurrent.ConcurrentHashMap publish(", "public static java.util.concurrent.ConcurrentHashMap load(String k)"),
               ("public static java.util.concurrent.ConcurrentHashMap publish0(", "public static java.util.concurrent.ConcurrentHashMap publish("),
               ("public static void bump(", "public static Object[] entry(java.util.UUID u) {"),
               ("public static boolean signal(", "public static boolean refresh(java.util.UUID u)")):
    assert s.index(a_) < s.index(b_), "javassist order: %s before %s" % (a_, b_)
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.2.24 outside the recorded changes"
compile(s, DST, "exec")
open(DST, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(DST, ROOT), "(%d lines; 0.2.24 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
