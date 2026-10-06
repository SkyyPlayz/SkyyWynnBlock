"""Derive SkyySacks/build_skyysacks_0.7.13.py from the SET pin 0.7.12 (edit THIS file, then regenerate: python tools/sacks_0_7_13_patch.py).
0.7.13 = THE BAG TAKE BRIDGE for SkyyBazaar 0.1.5 (Skyy 2026-10-05, docs/answered/economy.md 'New answers': "i tried to sell all my sap to the
bizzar. but its in my bag. you should be able to sell from your bags."). Nothing else changes: item classification, the sweep, the refill,
the bench / pocket link, the pages, /craft, Furnace / Tannery, kept counts and every file stay 0.7.12's (asserted below + the harness I).

NEW class SackBridge (static logic) + SackFn (the java.util.function.Function objects), published in setup() on the shared skyy.bridge map
(plain java types only; never removed - a shutdown answers through the SackPool.CLOSED latch, like every other item move):
  sacks:fn:count  apply(Object[] { UUID player, String itemId })            -> Long   how many of itemId the player can take out of the
                  bags RIGHT NOW (the pool of the active profile, only when a bag of that item's home type - or the Omni - is carried,
                  the same rule as a /pd withdraw click); -1 = bag item moves are paused (profile loading / switching, pool file
                  unreadable, shutting down) or the player is not on this thread's world; 0 = none / no such bag carried.
  sacks:fn:all    apply(UUID player)                                         -> java.util.HashMap String itemId -> Long count of every
                  item the player can take now (carried bag types only), a fresh copy; null = paused (as -1 above).
  sacks:fn:take   apply(Object[] { UUID player, String itemId, Number qty }) -> Long   removes UP TO qty from the bags (same gates as
                  count) and returns how many really left the pool (0 .. qty); only the returned amount may be paid for.
  sacks:fn:put    apply(Object[] { UUID player, String itemId, Number qty }) -> Long   the REFUND path of a take (a sale whose payment
                  failed): puts back at most what sacks:fn:take removed for that profile + item and no commit has settled yet, in the
                  last 60 s (OWED ledger, memory only) - it can never create items; returns how many went back (the caller gives any rest
                  to the inventory). Review fix: it returns into the pool the take DEBITED (SackBridge.LASTKEY, "uuid|itemId" -> key),
                  not the key settledKey answers now - a profile switch / busy flag / settle window that starts between the take and the
                  put can no longer strand the items (only the shutdown latch and an unreadable pool refuse it).
  sacks:fn:commit apply(Object[] { UUID player, String itemId, Number qty }) -> Long   review fix: the caller PAID for qty of a take - those
                  leave the OWED ledger at once (a later put can no longer return them); returns how many were cleared. Every caller
                  ends a take with exactly one commit (paid) or put (refund) of the same amount.
Rules (every one the same as the /pd withdraw path, SweepTask.withdraw):
  - WORLD THREAD ONLY: the player is looked up through Universe.getPlayer(uuid) -> PlayerRef -> its Ref's Store, and the call is refused
    (count -1 / take 0) unless Store.isInThread() (a Bazaar page click runs on that thread). SackBridge.PLAYERS is the bare-JVM harness's
    UUID -> Player lookup (always null in the game).
  - PER PROFILE: the key is SackPool.settledKey(uuid) (tools/PROFILES-CONTRACT.md: pkey + settle window + profile:busy + pool readable +
    the shutdown latch); null = paused.
  - LIVE-MIRROR RULE: BagMirror.beforeTake(key) books what an open bench / pocket craft already took from the bag mirror BEFORE the pool is
    read, BagMirror.afterTake(key, id) trims the mirror to the pool right after (the same items can never be sold AND crafted).
  - ATOMIC: the read + debit run in one synchronized (SackPool.class) block (SackPool.add's own lock) - a pool never goes below zero and two
    takes in one tick can never both get the same items.
  - SAVED like every bag change: SackPool.add marks the key dirty and bumps the change counter; SackPool.saveSoon(key) runs the SackSaver
    on the scheduler thread (no disk I/O on the world thread); crafts.log gets one queued line per take / put (CraftLog.later):
    "BAG-TAKE <id> <n> (sacks:fn:take)" / "BAG-RETURN <id> <n> (sacks:fn:put)".
  - MAGIC BAGS ARE NEVER IN A BAG (SackDefs.homeOf(Skyy_Sack_*) = null) - a bag item id answers 0 everywhere (the locked rule: bags are
    never sold / traded).
  - review fix (2026-10-06): sacks:fn:commit (mode 4) clears paid takes from the ledger - before it, a put within 60 s of a PAID take
    could re-add those items for free (not reachable from SkyyBazaar, which only puts after a failed payment, but the bridge is shared).
  - a failure after the debit never hides it: each later step (mirror trim, ledger, log, save) is caught on its own, so take always returns
    what really left the pool.
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.7.12.py")
dst = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.7.13.py")
raw = open(src, encoding="utf8", newline="").read()
CR = chr(13)
LF = chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)


def rep(old, new, count=1):
    global s
    assert s.count(old) >= 1, "anchor missing: " + old[:90]
    assert count != 1 or s.count(old) == 1, "anchor not unique: " + old[:90]
    s = s.replace(old, new, count)


assert 'VERSION = "0.7.12"' in s and "BenchLink" in s and "MirrorGuard" in s and "SackBridge" not in s and "sacks:fn:" not in s, \
    "the source must be the generated 0.7.12 script"
REG0 = s.count("registerCommand(")
SYS0 = s.count("registerSystem(")
# every 0.7.12 block that must stay byte-identical: everything up to the plugin section (the new classes are inserted right before it)
_PLUG = "# ================= plugin =================" + LF
assert s.count(_PLUG) == 1
BODY012 = s[s.index('"""' + LF + "import sys, os"):s.index(_PLUG)]

# ================= docstring + version =================
rep('"""SkyySacks 0.7.12 - build script (javassist via jpype).' + LF
    + 'Run:   python build_skyysacks_0.7.12.py           -> SkyySacks/SkyySacks-0.7.12.jar' + LF
    + '       python build_skyysacks_0.7.12.py --deploy  -> also copies to Mods/SkyySacks.jar and enables it in the HUD mod world' + LF,
    '"""SkyySacks 0.7.13 - build script (javassist via jpype).' + LF
    + 'Run:   python build_skyysacks_0.7.13.py           -> SkyySacks/SkyySacks-0.7.13.jar   (deploys go through tools/deploy_set.py --yes)' + LF
    + '       python build_skyysacks_0.7.13.py --deploy  -> also copies to Mods/SkyySacks.jar and enables it in the HUD mod world (never used)' + LF)
rep('before start(); a declined bench window gets its close hook too; rebuild never offers an id the Item asset map no longer knows.' + LF + '"""' + LF,
    'before start(); a declined bench window gets its close hook too; rebuild never offers an id the Item asset map no longer knows.' + LF
    + '0.7.13 (derived from 0.7.12 by tools/sacks_0_7_13_patch.py - edit the patch, not this file; Skyy 2026-10-05 "you should be able to sell' + LF
    + 'from your bags"): THE BAG TAKE BRIDGE for SkyyBazaar 0.1.5 - new SackBridge + SackFn, published in setup() on skyy.bridge (never removed):' + LF
    + 'sacks:fn:count {UUID, itemId} -> Long (takeable now; -1 = paused), sacks:fn:all UUID -> HashMap itemId -> Long (null = paused),' + LF
    + 'sacks:fn:take {UUID, itemId, qty} -> Long removed (0..qty), sacks:fn:put {UUID, itemId, qty} -> Long returned (only what a take removed' + LF
    + 'for that profile + item in the last 60 s and no commit cleared - the refund path, never a source of items; it returns into the pool the' + LF
    + 'take debited), sacks:fn:commit {UUID, itemId, qty} -> Long cleared (the caller paid: those can never be put back). Same gates as a /pd withdraw: world thread only' + LF
    + '(Store.isInThread), the settled profile key (SackPool.settledKey), a bag of the item\'s home type (or the Omni) carried, the live-mirror' + LF
    + 'rule (BagMirror.beforeTake / afterTake), the read + debit atomic under SackPool.class, saved through SackPool.saveSoon, one crafts.log' + LF
    + 'line per take / put. Magic Bags themselves are never in a bag (homeOf = null): a bag id answers 0. Everything else is 0.7.12\'s.' + LF
    + '"""' + LF)
rep('VERSION = "0.7.12"', 'VERSION = "0.7.13"')

# ================= the two new classes (made with the others) =================
rep('psu = pool.makeClass(PKG + ".PocketSupplier")' + LF,
    'psu = pool.makeClass(PKG + ".PocketSupplier")' + LF
    + '# 0.7.13: SackBridge = the bag take bridge for SkyyBazaar (static logic); SackFn = its java.util.function.Function objects (mode 0-3)' + LF
    + 'sbr = pool.makeClass(PKG + ".SackBridge")' + LF
    + 'sfn = pool.makeClass(PKG + ".SackFn")' + LF)
# the engine members the bridge uses, probed like every other one (the build stops when one is gone)
rep('for c in (defs, sp, scfg, ksync, snot, rfp, kq, pjob, pben, pst, swp, tick, sav, cmp, page, cmd, fac, mgd, mir, lrec, blink, mcl, cpf, pct, cif,' + LF
    + '          pcw, psu, clt, ctk, rcmp, clog, cpg, ccmd, cfac, ptk, ptick, pl):' + LF,
    'for c in (defs, sp, scfg, ksync, snot, rfp, kq, pjob, pben, pst, swp, tick, sav, cmp, page, cmd, fac, mgd, mir, lrec, blink, mcl, cpf, pct, cif,' + LF
    + '          pcw, psu, clt, ctk, rcmp, clog, cpg, ccmd, cfac, ptk, ptick, sbr, sfn, pl):' + LF)

BRIDGE = r'''# ================= SackBridge + SackFn (0.7.13): the bag take bridge for SkyyBazaar (tools/sacks_0_7_13_patch.py docstring) =================
for _c, _m in ((UNI, "get"), (UNI, "getPlayer"), (PR, "getReference"), (REF, "getStore"), (ST, "isInThread"), (ST, "getComponent"),
               (PLA, "getInventory"), (PLA, "getComponentType")):
    B.probe(pool, _c, _m)
# PLAYERS = the bare-JVM harness's UUID -> Player lookup (always null in the game: the player's own store, on its world thread only).
sbr.addField(CtField.make("public static volatile java.util.function.Function PLAYERS;", sbr))
# OWED = "<key>|<itemId>" -> long[] { amount a take removed and a put may still return, time of the last take } (memory only, 60 s)
sbr.addField(CtField.make("public static final java.util.HashMap OWED = new java.util.HashMap();", sbr))
sbr.addField(CtField.make("public static final long OWE_MS = 60000L;", sbr))
# review fix: LASTKEY = "<uuid>|<itemId>" -> the profile key the last take of that player + item DEBITED (put / commit settle against it)
sbr.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap LASTKEY = new java.util.concurrent.ConcurrentHashMap();", sbr))
sbr.addMethod(CtNewMethod.make(jt(r"""
public static @PLA@ playerOf(java.util.UUID u) {
  if (u == null) return null;
  java.util.function.Function f = PLAYERS;
  if (f != null) {
    Object o = f.apply(u);
    return (o instanceof @PLA@) ? (@PLA@) o : null;
  }
  @PR@ pr = null;
  try { pr = @UNI@.get().getPlayer(u); } catch (Throwable t) { pr = null; }
  if (pr == null) return null;
  @REF@ r = pr.getReference();
  if (r == null) return null;
  @ST@ st = r.getStore();
  if (st == null) return null;
  if (!st.isInThread()) {
    @PKG@.KnowSync.warnOnce("bag bridge: a call came off the player's world thread - refused (nothing moved; logged once)");
    return null;
  }
  return (@PLA@) st.getComponent(r, @PLA@.getComponentType());
}"""), sbr))
# the profile key whose bags this player can reach for itemId right now, or null (paused / no player on this thread / no such bag carried).
# out[0] = 1 when the answer is "paused" (count -1), 0 when it is "none" (count 0).
sbr.addMethod(CtNewMethod.make(jt(r"""
public static String keyFor(java.util.UUID u, String id, int[] out) {
  out[0] = 0;
  if (u == null || id == null || id.startsWith("Skyy_Sack_")) return null;
  String cat = @PKG@.SackDefs.homeOf(id);
  if (cat == null) return null;
  String k = @PKG@.SackPool.settledKey(u);
  if (k == null) { out[0] = 1; return null; }
  @PLA@ p = playerOf(u);
  if (p == null) { out[0] = 1; return null; }
  if (!@PKG@.SweepTask.caps(p.getInventory()).containsKey(cat)) return null;
  return k;
}"""), sbr))
sbr.addMethod(CtNewMethod.make(jt(r"""
public static long count(java.util.UUID u, String id) {
  int[] why = new int[1];
  String k = keyFor(u, id, why);
  if (k == null) return why[0] == 1 ? -1L : 0L;
  @PKG@.BagMirror.beforeTake(k);   // live-mirror rule: book an open bench's use first, else the pool reads too high
  long have = @PKG@.SackPool.get(k, id);
  return have < 0L ? 0L : have;
}"""), sbr))
sbr.addMethod(CtNewMethod.make(jt(r"""
public static java.util.HashMap all(java.util.UUID u) {
  java.util.HashMap out = new java.util.HashMap();
  if (u == null) return out;
  String k = @PKG@.SackPool.settledKey(u);
  if (k == null) return null;
  @PLA@ p = playerOf(u);
  if (p == null) return null;
  java.util.HashMap caps = @PKG@.SweepTask.caps(p.getInventory());
  if (caps.isEmpty()) return out;
  @PKG@.BagMirror.beforeTake(k);
  java.util.Iterator it = @PKG@.SackPool.pool(k).entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    String id = (String) e.getKey();
    long v = ((Long) e.getValue()).longValue();
    if (v <= 0L || id.startsWith("Skyy_Sack_")) continue;
    String cat = @PKG@.SackDefs.homeOf(id);
    if (cat != null && caps.containsKey(cat)) out.put(id, Long.valueOf(v));
  }
  return out;
}"""), sbr))
# the read + debit, atomic with every other pool writer (SackPool.add is static synchronized on SackPool.class; reentrant)
sbr.addMethod(CtNewMethod.make(jt(r"""
public static long debit0(String k, String id, long n) {
  long have = @PKG@.SackPool.get(k, id);
  long t = n < have ? n : have;
  if (t <= 0L) return 0L;
  @PKG@.SackPool.add(k, id, -t);
  return t;
}"""), sbr))
sbr.addMethod(CtNewMethod.make(jt(r"""
public static long debit(String k, String id, long n) {
  synchronized (@PKG@.SackPool.class) { return debit0(k, id, n); }
}"""), sbr))
sbr.addMethod(CtNewMethod.make(jt(r"""
public static synchronized void owe(String k, String id, long n, long now) {
  String key = k + "|" + id;
  long[] o = (long[]) OWED.get(key);
  if (o == null || now - o[1] > OWE_MS) o = new long[] { 0L, now };
  o[0] = o[0] + n;
  o[1] = now;
  OWED.put(key, o);
}"""), sbr))
# how much of n may go back (and is no longer owed): at most what takes of this key + item removed in the last OWE_MS
sbr.addMethod(CtNewMethod.make(jt(r"""
public static synchronized long unowe(String k, String id, long n, long now) {
  String key = k + "|" + id;
  long[] o = (long[]) OWED.get(key);
  if (o == null) return 0L;
  if (now - o[1] > OWE_MS) { OWED.remove(key); return 0L; }
  long t = n < o[0] ? n : o[0];
  if (t <= 0L) return 0L;
  o[0] = o[0] - t;
  if (o[0] <= 0L) OWED.remove(key);
  return t;
}"""), sbr))
sbr.addMethod(CtNewMethod.make(jt(r"""
public static long take(java.util.UUID u, String id, long n) {
  if (n <= 0L) return 0L;
  int[] why = new int[1];
  String k = keyFor(u, id, why);
  if (k == null) return 0L;
  @PKG@.BagMirror.beforeTake(k);   // live-mirror rule: book what a bench / pocket craft already took BEFORE the pool is read
  long t = debit(k, id, n);
  if (t <= 0L) return 0L;
  // from here on the items are gone from the pool: every later step is caught on its own so the caller always learns the real amount
  try { @PKG@.BagMirror.afterTake(k, id); } catch (Throwable t1) { @PKG@.SackPool.warn("bag bridge: mirror trim failed after a take: " + t1); }
  try { LASTKEY.put(u.toString() + "|" + id, k); owe(k, id, t, System.currentTimeMillis()); } catch (Throwable t2) { }
  try { @PKG@.CraftLog.later(k, "BAG-TAKE " + id + " " + t + " (sacks:fn:take)"); } catch (Throwable t3) { }
  try { @PKG@.SackPool.saveSoon(k); } catch (Throwable t4) { @PKG@.SackPool.DIRTY.put(k, Boolean.TRUE); }
  return t;
}"""), sbr))
# review fix: the key a put / commit settles against = the pool the last take of this player + item debited (LASTKEY), else the settled
# key; null while shutting down (SackPool.CLOSED: the pools are being flushed) or when that pool cannot be read. NOT the settle window /
# profile:busy: those pause moves between the INVENTORY and a pool; a put only returns ledger items to the exact pool they left.
sbr.addMethod(CtNewMethod.make(jt(r"""
public static String refundKey(java.util.UUID u, String id) {
  if (u == null || id == null || @PKG@.SackPool.CLOSED) return null;
  String k = (String) LASTKEY.get(u.toString() + "|" + id);
  if (k == null) k = @PKG@.SackPool.settledKey(u);
  if (k == null || !@PKG@.SackPool.ready(k)) return null;
  return k;
}"""), sbr))
sbr.addMethod(CtNewMethod.make(jt(r"""
public static long commit(java.util.UUID u, String id, long n) {
  if (u == null || id == null || n <= 0L) return 0L;
  String k = (String) LASTKEY.get(u.toString() + "|" + id);
  if (k == null) k = @PKG@.SackPool.settledKey(u);
  if (k == null) return 0L;
  return unowe(k, id, n, System.currentTimeMillis());
}"""), sbr))
sbr.addMethod(CtNewMethod.make(jt(r"""
public static long put(java.util.UUID u, String id, long n) {
  if (u == null || id == null || n <= 0L || id.startsWith("Skyy_Sack_")) return 0L;
  String k = refundKey(u, id);
  if (k == null) return 0L;
  long t = unowe(k, id, n, System.currentTimeMillis());
  if (t <= 0L) return 0L;
  @PKG@.SackPool.add(k, id, t);
  try { @PKG@.CraftLog.later(k, "BAG-RETURN " + id + " " + t + " (sacks:fn:put)"); } catch (Throwable t3) { }
  try { @PKG@.SackPool.saveSoon(k); } catch (Throwable t4) { @PKG@.SackPool.DIRTY.put(k, Boolean.TRUE); }
  return t;
}"""), sbr))
sfn.addInterface(pool.get("java.util.function.Function"))
sfn.addField(CtField.make("public int mode;", sfn))
sfn.addConstructor(CtNewConstructor.make("public SackFn(int mode) { this.mode = mode; }", sfn))
# mode 0 count, 1 take, 2 put, 3 all, 4 commit (review fix). Bad arguments answer 0 (count -1, all null); nothing here ever throws to the caller.
sfn.addMethod(CtNewMethod.make(jt(r"""
public Object apply(Object o) {
  try {
    if (this.mode == 3) return (o instanceof java.util.UUID) ? @PKG@.SackBridge.all((java.util.UUID) o) : null;
    if (!(o instanceof Object[])) return Long.valueOf(this.mode == 0 ? -1L : 0L);
    Object[] a = (Object[]) o;
    if (a.length < 2 || !(a[0] instanceof java.util.UUID) || !(a[1] instanceof String)) return Long.valueOf(this.mode == 0 ? -1L : 0L);
    java.util.UUID u = (java.util.UUID) a[0];
    String id = (String) a[1];
    if (this.mode == 0) return Long.valueOf(@PKG@.SackBridge.count(u, id));
    if (a.length < 3 || !(a[2] instanceof Number)) return Long.valueOf(0L);
    long n = ((Number) a[2]).longValue();
    if (this.mode == 1) return Long.valueOf(@PKG@.SackBridge.take(u, id, n));
    if (this.mode == 2) return Long.valueOf(@PKG@.SackBridge.put(u, id, n));
    if (this.mode == 4) return Long.valueOf(@PKG@.SackBridge.commit(u, id, n));
  } catch (Throwable t) {
    @PKG@.KnowSync.warnOnce("bag bridge call failed (mode " + this.mode + "): " + t);
  }
  return this.mode == 3 ? null : Long.valueOf(this.mode == 0 ? -1L : 0L);
}"""), sfn))

'''
rep(_PLUG, BRIDGE + _PLUG)

# ================= publish in setup() (after the settings, before the config kit; never removed) =================
rep('''  {PKG}.SackPool.regSetting("sacks.benchFuel", "Furnace out of fuel", "sacks", true, "Your Furnace ran out of fuel - once until you add more");
''', '''  {PKG}.SackPool.regSetting("sacks.benchFuel", "Furnace out of fuel", "sacks", true, "Your Furnace ran out of fuel - once until you add more");
  // 0.7.13: the bag take bridge (SkyyBazaar 0.1.5 sells from the bags) - plain java types, world thread only, never removed
  java.util.Map sbr0 = {PKG}.SackPool.bridgeW();
  sbr0.put("sacks:fn:count", new {PKG}.SackFn(0));
  sbr0.put("sacks:fn:take", new {PKG}.SackFn(1));
  sbr0.put("sacks:fn:put", new {PKG}.SackFn(2));
  sbr0.put("sacks:fn:all", new {PKG}.SackFn(3));
  sbr0.put("sacks:fn:commit", new {PKG}.SackFn(4));   // review fix: a paid take leaves the refund ledger
''')
rep('''right-click a magic bag; benches and inventory crafting use the bags you carry''',
    '''right-click a magic bag; benches and inventory crafting use the bags you carry; the Bazaar sells from the bags you carry (sacks:fn:take)''')

# ================= self-checks =================
assert 'VERSION = "0.7.13"' in s and s.count("registerCommand(") == REG0 and s.count("registerSystem(") == SYS0, "no new command or ECS system"
assert s[s.index('"""' + LF + "import sys, os"):s.index(BRIDGE)] == BODY012.replace('VERSION = "0.7.12"', 'VERSION = "0.7.13"').replace(
    'psu = pool.makeClass(PKG + ".PocketSupplier")' + LF, 'psu = pool.makeClass(PKG + ".PocketSupplier")' + LF
    + '# 0.7.13: SackBridge = the bag take bridge for SkyyBazaar (static logic); SackFn = its java.util.function.Function objects (mode 0-3)' + LF
    + 'sbr = pool.makeClass(PKG + ".SackBridge")' + LF + 'sfn = pool.makeClass(PKG + ".SackFn")' + LF), "everything before the plugin = 0.7.12's"
for _k in ("sacks:fn:count", "sacks:fn:take", "sacks:fn:put", "sacks:fn:all", "sacks:fn:commit"):
    assert s.count('"%s"' % _k) == 1, _k
for _a, _b in (("public static @PLA@ playerOf(java.util.UUID u)", "public static String keyFor("),
               ("public static String keyFor(", "public static long count(java.util.UUID u, String id)"),
               ("public static long debit0(", "public static long debit(String k"), ("public static long debit(String k", "public static long take("),
               ("public static synchronized void owe(", "public static long take("), ("public static synchronized long unowe(", "public static long put("),
               ("public static synchronized long unowe(", "public static long commit("), ("public static String refundKey(", "public static long put("),
               ("public static boolean ready(String k)", "public static String refundKey("),
               ("public static long put(", "    if (this.mode == 3) return (o instanceof"), ("_BEFORE_TAKE.setBody(", "public static long take("),
               ("public static void saveSoon(String k)", "public static long take("), ("public static void later(String k", "public static long take("),
               ("sbr = pool.makeClass(", "for c in (defs, sp, scfg"), ("    if (this.mode == 3) return (o instanceof", "sbr0.put(\"sacks:fn:count\"")):
    assert 0 <= s.find(_a) < s.find(_b), "order: %s before %s" % (_a[:60], _b[:60])
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
