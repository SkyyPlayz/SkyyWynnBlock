"""Derive SkyySacks/build_skyysacks_0.8.32.py from the SET pin 0.8.31 (the GENERATED build_skyysacks_0.8.31.py; edit THIS file, then
regenerate: python tools/sacks_0_8_32_patch.py; never re-run sacks_0_8_31_patch.py on top of it). Every anchor is asserted once; at the end
every change is undone on a copy and compared with 0.8.31 (nothing else changed). Line endings kept.
Run:  python tools/sacks_0_8_32_patch.py   then   python SkyySacks/build_skyysacks_0.8.32.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.8.32.py [--dir <folder inside tools/dev/scratch/>] [--keep]

0.8.32 (2026-10-27) = THREE QUEUE ITEMS (round sacks32; Skyy 2026-10-27 "sounds good" to the RESUME queue + "work through your whole que").
  1. GREATER ESSENCE OPENS LIKE AN ENCHANTED ITEM. 0.8.31 only COMPACTED Essence of Life -> Greater Essence of Life (the vanilla pair,
     tools/skyyench.py VANILLA_ENCH). Now the vanilla pair is in VoidCompact's id maps too (BI / EI: Ingredient_Life_Essence = pair 110,
     Ingredient_Life_Essence_Concentrated = its Enchanted item), so every OPENING path treats it like the 110 Enchanted rows: crafting
     (bench / pocket / /craft / Furnace + sacks:fn:craftHave / craftPay - BagMirror.virtuals offers 100 Essence of Life per Greater
     Essence, the craft opens the fewest, the change stays loose), the bag upgrade cost (VoidStore encHave / openFor / unopen), a refused
     craft packs back (repack), and the Pocket page's Unpack (select Greater Essence of Life -> Unpack -> 100 Essence each to the storage).
     The same per-recipe rules hold ("!nv:" a recipe using both, "!pocket"/"!e:" inventory crafting). Opening needs no unlock (as every
     Enchanted item). NO LOOP: 1 <-> 100 is the vanilla recipe's own ratio, the same as SkyyCollections 0.2.34's reverse recipe and
     SkyyBazaar 0.2.2's prices (Greater 50 = 100 x Essence 0.5; its E1 pack / unpack check covers the pair); no coins involved here.
     Known edge (net zero): at the Farmer's Workbench the vanilla 100 Essence -> 1 Greater recipe may be paid with Essence opened from a
     Greater Essence (1 opened, 1 made back) - nothing gained or lost.
  2. NEW BRIDGE sacks:fn:takeOpen {UUID player, String itemId, Long qty} -> Long = qty taken, or 0 = NOTHING taken (all or nothing).
     The Pocket Dimension part of a cost, like sacks:fn:take (the caller takes the inventory part itself, as SkyyShards payInvBags does -
     inventory stacks with data stay the caller's business): the loose items first, then the FEWEST Enchanted items of that id's pair
     opened (both bags carried / the Void reachable, bags.craftOpen on), the change (100 x opened - the rest) stays loose in the bag.
     Not enough loose + 100 x Enchanted = 0 and nothing moves. One SackPool lock for the read + debit + open. Same gates as sacks:fn:take
     (world thread only: off it = 0 and nothing moves, logged once; the settled profile key; the item's bag home; the live-mirror rule).
     Refund / commit: the SAME sacks:fn:put / sacks:fn:commit keys and the same 60 s ledger as sacks:fn:take (OWED, LASTKEY). NEW: a put of
     a takeOpen'd id packs the opened Enchanted items back (OPN ledger: all of them once nothing of that id is owed any more, else
     floor(returned / 100) of them) - so a refunded cost leaves the bag exactly as before; a put off the world thread returns the items
     loose (value kept, nothing packed). A commit clears the OPN ledger with the owed amount. Whole fish (SkyyFishing): checked count,
     then sacks:fn:take; a short take is put back and answers 0. crafts.log: BAG-TAKEOPEN / BAG-TAKEOPEN-UNDO lines.
     SkyyShards payInvBags adopts it in a later round (Shards is not edited here).
  3. THE SHARED-EXECUTOR BLOCKER. FOUND: CraftTick (every 300 ms) and ProcTick (every 1 s) were still on HytaleServer.SCHEDULED_EXECUTOR
     (the engine's ONE shared scheduler thread). Their cost is tiny and bounded - each run walks the online players and per player does
     ConcurrentHashMap lookups (BenchLink.needsLink: ACTIVE / RECS / MIRRORS; ProcTask.needs: LASTK / PAGEOPEN / EPOCH + the player's
     benches' synchronized queued() / xpList(), a few entries each) and, only for a player with work, one World.execute hop. No disk, no
     engine store, no lock held across a call (the ProcBench monitors are held by short in-memory methods only). So Sacks is NOT the task
     holding the shared thread (still UNVERIFIED which mod is - the SkyyShards ShTick idle-unload is the suspect). But they were its
     VICTIMS: while another mod holds that thread, the bench / pocket crafting link (bags at benches) and the Furnace / Tannery queue stop.
     FIX: a second private daemon thread SkyySacks-ticker (SackPool.TICKER, the SackThreads factory with a name) runs the three dispatchers
     (SackTick 2 s, CraftTick 300 ms, ProcTick 1 s) and the AccSettle 250 ms hop - so neither another mod's stuck task nor a slow pool
     write on SkyySacks-writer (antivirus, big save) can delay them. The writer keeps only the saves. The 0.8.31 SackBeat WARN stays as it
     was (its beat is still the one tiny task we put on the shared scheduler, on purpose). MEASURED: each dispatcher run times itself
     (SackBeat.took): the slowest run of each is in the shutdown line ("tick max: sweep N ms, craft link N ms, furnace N ms"), and one that
     takes 1 s or more WARNs (once a minute at most) - the bare harness measures them over 200 players x 8 benches.
  No saved-data change, no config row, no migration, no new system / command. ROLLBACK to 0.8.31: safe alone (Greater Essence of Life is
  a vanilla item and stays; sacks:fn:takeOpen disappears - SkyyShards does not call it yet; the dispatchers go back to their old threads).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G   # only its generic Patch helper (anchors asserted once, undo-compare, line endings kept)

P = G.Patch(os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.31.py"), os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.32.py"))
assert P.has('VERSION = "0.8.31"\n') and P.has("SackBeat") and not P.has("takeOpen("), "not the live generated SkyySacks 0.8.31"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.8.32 (2026-10-27)"):].rstrip() + "\n"

P.rep('''  row line stays in config.properties, unknown to 0.8.30; already made Greater Essence of Life stays - it is a vanilla item).
"""
''', '''  row line stays in config.properties, unknown to 0.8.30; already made Greater Essence of Life stays - it is a vanilla item).
''' + NOTE + '''"""
''')
P.rep('VERSION = "0.8.31"\n', 'VERSION = "0.8.32"\n')

# ================================================================ 1. the vanilla pair opens like an Enchanted item
P.rep(r'''  for (int i = 0; i < BASE.length; i++) { BI.put(BASE[i], Integer.valueOf(i)); EI.put(ENCH[i], Integer.valueOf(i)); }
''', r'''  for (int i = 0; i < BASE.length; i++) { BI.put(BASE[i], Integer.valueOf(i)); EI.put(ENCH[i], Integer.valueOf(i)); }
  // 0.8.32: + the vanilla pairs (combined index BASE.length + j, as np / baseAt / enchAt): every opening path finds them too
  for (int j = 0; j < VBASE.length; j++) { BI.put(VBASE[j], Integer.valueOf(BASE.length + j)); EI.put(VENCH[j], Integer.valueOf(BASE.length + j)); }
''')
P.rep(r'''    String b = BASE[x];
    s.add("!e:" + b);''', r'''    String b = x < BASE.length ? BASE[x] : VBASE[x - BASE.length];   // 0.8.32: combined index
    s.add("!e:" + b);''')
P.rep(r'''    long m = pack(k, b, ENCH[x], n);
    t += m;''', r'''    long m = pack(k, b, enchAt(x), n);   // 0.8.32: combined index
    t += m;''')
P.rep(r'''"CRAFT-OPEN-UNDO " + ENCH[x] + " "''', r'''"CRAFT-OPEN-UNDO " + enchAt(x) + " "''')
P.rep(r'''    if (x >= 0) h += @PKG@.VoidCompact.RATIO * @PKG@.SackPool.get($1, @PKG@.VoidCompact.ENCH[x]);''',
      r'''    if (x >= 0) h += @PKG@.VoidCompact.RATIO * @PKG@.SackPool.get($1, @PKG@.VoidCompact.enchAt(x));   // 0.8.32''')
P.rep(r'''  String e = @PKG@.VoidCompact.ENCH[x];
  long m = @PKG@.VoidCompact.split($1, e, $2, n);''', r'''  String e = @PKG@.VoidCompact.enchAt(x);   // 0.8.32
  long m = @PKG@.VoidCompact.split($1, e, $2, n);''')
P.rep(r'''    long m = @PKG@.VoidCompact.pack($1, b, @PKG@.VoidCompact.ENCH[x], n);
    if (m < n) @PKG@.SackPool.warn("bag upgrade rollback for " + $1 + ": only " + m + " of " + n + " " + @PKG@.VoidCompact.ENCH[x] + " packed back (the base items stay loose - nothing lost)");
    try { @PKG@.BagMirror.afterTake($1, b); } catch (Throwable t1) { }
    try { @PKG@.CraftLog.later($1, "VOID-UPGRADE-UNOPEN " + @PKG@.VoidCompact.ENCH[x] + " " + m + " of " + n + " packed back (the upgrade was refused)"); } catch (Throwable t2) { }''',
      r'''    String e = @PKG@.VoidCompact.enchAt(x);   // 0.8.32
    long m = @PKG@.VoidCompact.pack($1, b, e, n);
    if (m < n) @PKG@.SackPool.warn("bag upgrade rollback for " + $1 + ": only " + m + " of " + n + " " + e + " packed back (the base items stay loose - nothing lost)");
    try { @PKG@.BagMirror.afterTake($1, b); } catch (Throwable t1) { }
    try { @PKG@.CraftLog.later($1, "VOID-UPGRADE-UNOPEN " + e + " " + m + " of " + n + " packed back (the upgrade was refused)"); } catch (Throwable t2) { }''')
P.rep(r'''  if (x < 0) return "-That item does not unpack";
  String b = @PKG@.VoidCompact.BASE[x];''', r'''  if (x < 0) return "-That item does not unpack";
  String b = @PKG@.VoidCompact.baseAt(x);   // 0.8.32: + Greater Essence of Life -> 100 Essence of Life''')
P.rep(r'''  String[] bs = @PKG@.VoidCompact.BASE;
  String[] es = @PKG@.VoidCompact.ENCH;
  for (int i = 0; i < bs.length; i++) {''', r'''  int np = @PKG@.VoidCompact.np();   // 0.8.32: + the vanilla pairs (Greater Essence of Life backs Essence of Life)
  String[] bs = new String[np];
  String[] es = new String[np];
  for (int q = 0; q < np; q++) { bs[q] = @PKG@.VoidCompact.baseAt(q); es[q] = @PKG@.VoidCompact.enchAt(q); }
  for (int i = 0; i < bs.length; i++) {''')

# ================================================================ 2. sacks:fn:takeOpen
P.rep(r'''sbr.addMethod(CtNewMethod.make(jt(r"""
public static long take(java.util.UUID u, String id, long n) {''', r'''# 0.8.32 sacks:fn:takeOpen: OPN = "<key>|<itemId>" -> long[] { Enchanted items a takeOpen opened that a put may still pack back, time }
# (memory only, the same 60 s as OWED; guarded by SackBridge.class like OWED)
sbr.addField(CtField.make("public static final java.util.HashMap OPN = new java.util.HashMap();", sbr))
sbr.addField(CtField.make("public static final java.util.concurrent.atomic.AtomicLong TAKEOPENS = new java.util.concurrent.atomic.AtomicLong();", sbr))
sbr.addMethod(CtNewMethod.make(jt(r"""
public static synchronized void oweOpen(String k, String id, long m, long now) {
  if (m <= 0L) return;
  String key = k + "|" + id;
  long[] o = (long[]) OPN.get(key);
  if (o == null || now - o[1] > OWE_MS) o = new long[] { 0L, now };
  o[0] = o[0] + m;
  o[1] = now;
  OPN.put(key, o);
}"""), sbr))
# a put returned t of id (OWED already settled): how many opened Enchanted items to pack back - all once nothing of id is owed any more,
# else floor(t / RATIO); expired / none = 0
sbr.addMethod(CtNewMethod.make(jt(r"""
public static synchronized long unoweOpen(String k, String id, long t, long now) {
  String key = k + "|" + id;
  long[] o = (long[]) OPN.get(key);
  if (o == null) return 0L;
  if (now - o[1] > OWE_MS) { OPN.remove(key); return 0L; }
  boolean full = !OWED.containsKey(key);
  long p = full ? o[0] : Math.min(o[0], t / @PKG@.VoidCompact.RATIO);
  if (p < 0L) p = 0L;
  o[0] = o[0] - p;
  if (full || o[0] <= 0L) OPN.remove(key);
  return p;
}"""), sbr))
# a commit: once nothing of id is owed any more, nothing can be packed back either
sbr.addMethod(CtNewMethod.make(jt(r"""
public static synchronized void openDone(String k, String id) {
  String key = k + "|" + id;
  if (!OWED.containsKey(key)) OPN.remove(key);
}"""), sbr))
# is u's world thread this one (no warning: the put path may be called anywhere; the harness stand-in = PLAYERS answers a player)
sbr.addMethod(CtNewMethod.make(jt(r"""
public static boolean onThread(java.util.UUID u) {
  if (u == null) return false;
  java.util.function.Function f = PLAYERS;
  if (f != null) return f.apply(u) != null;
  try {
    @PR@ pr = @UNI@.get().getPlayer(u);
    if (pr == null) return false;
    @REF@ r = pr.getReference();
    if (r == null) return false;
    @ST@ st = r.getStore();
    return st != null && st.isInThread();
  } catch (Throwable t) { return false; }
}"""), sbr))
sbr.addMethod(CtNewMethod.make(jt(r"""
public static long take(java.util.UUID u, String id, long n) {''')
P.rep(r'''    return (long) ce.size();
  }
  return unowe(k, id, n, System.currentTimeMillis());
}"""), sbr))''', r'''    return (long) ce.size();
  }
  long cm = unowe(k, id, n, System.currentTimeMillis());
  openDone(k, id);   // 0.8.32: a paid takeOpen - its opened Enchanted items are final too
  return cm;
}"""), sbr))''')
P.rep(r'''    t = unowe(k, id, n, System.currentTimeMillis());
    if (t > 0L) @PKG@.SackPool.add(k, id, t);
  }''', r'''    long pn0 = System.currentTimeMillis();
    t = unowe(k, id, n, pn0);
    if (t > 0L) @PKG@.SackPool.add(k, id, t);
    if (t > 0L) packBack(u, k, id, t, pn0);   // 0.8.32: a refunded takeOpen packs its opened Enchanted items back
  }''')
# packBack + takeOpen: before put (its caller) / after take, count, keyFor, playerOf, debit, owe (their callees)
P.rep(r'''# review fix: the key a put / commit settles against = the pool the last take of this player + item debited (LASTKEY), else the settled
''', r'''# 0.8.32: the pack-back of a refunded takeOpen (put, after the base came back): on u's world thread only (the live-mirror rule needs it);
# elsewhere the base stays loose (value kept, nothing lost). Returns the Enchanted items packed back.
sbr.addMethod(CtNewMethod.make(jt(r"""
public static long packBack(java.util.UUID u, String k, String id, long t, long now) {
  long p = unoweOpen(k, id, t, now);
  if (p <= 0L) return 0L;
  int x = @PKG@.VoidCompact.idxBase(id);
  if (x < 0) return 0L;
  String e = @PKG@.VoidCompact.enchAt(x);
  if (!onThread(u)) {
    try { @PKG@.CraftLog.later(k, "BAG-TAKEOPEN-UNDO " + e + " 0 of " + p + " packed back - the put came off the world thread, the " + id + " stays loose (sacks:fn:put)"); } catch (Throwable t0) { }
    return 0L;
  }
  try { @PKG@.BagMirror.beforeTake(k); } catch (Throwable t1) { }
  long m = @PKG@.VoidCompact.pack(k, id, e, p);
  try { @PKG@.BagMirror.afterTake(k, id); } catch (Throwable t2) { }
  try { @PKG@.CraftLog.later(k, "BAG-TAKEOPEN-UNDO " + e + " " + m + " of " + p + " packed back (sacks:fn:put)"); } catch (Throwable t3) { }
  return m;
}"""), sbr))
# 0.8.32 takeOpen's pool step (one SackPool lock): enough = loose + RATIO x Enchanted (e null = loose only); out = { taken, opened }
sbr.addMethod(CtNewMethod.make(jt(r"""
public static long[] takeOpen0(String k, String id, String e, long n) {
  long l = @PKG@.SackPool.get(k, id);
  long h = e == null ? 0L : @PKG@.SackPool.get(k, e);
  if (l < 0L) l = 0L;
  if (h < 0L) h = 0L;
  if (h > 92233720368547L) h = 92233720368547L;
  if (l + h * @PKG@.VoidCompact.RATIO < n) return new long[] { 0L, 0L };
  if (e == null || n <= l) { @PKG@.SackPool.add(k, id, -n); return new long[] { n, 0L }; }
  long m = @PKG@.VoidCompact.open0(k, id, e, n);
  return new long[] { n, m };
}"""), sbr))
sbr.addMethod(CtNewMethod.make(jt(r"""
public static long[] takeOpenL(String k, String id, String e, long n) {
  synchronized (@PKG@.SackPool.class) { return takeOpen0(k, id, e, n); }
}"""), sbr))
# review fix: the key a put / commit settles against = the pool the last take of this player + item debited (LASTKEY), else the settled
''')
# takeOpen after put (it calls take / count / put: methods before callers)
P.rep('''# ================= 0.8.17 THE VOID'S WEIGHED FISH for SkyyFishing 0.1.10 (tools/sacks_0_8_17_patch.py A; world thread only) =================
''', r'''# 0.8.32 sacks:fn:takeOpen {UUID, itemId, qty} -> qty taken or 0 (nothing moved): loose first, then the fewest Enchanted opened, the change
# loose in the bag. The same gates as take (keyFor: world thread, settled key, the item's bag home); the Enchanted item needs its own bag
# home reachable and bags.craftOpen on, else loose only. Booked on the take ledger (put / commit) + OPN (the pack-back).
sbr.addMethod(CtNewMethod.make(jt(r"""
public static long takeOpen(java.util.UUID u, String id, long n) {
  if (u == null || id == null || n <= 0L) return 0L;
  int[] why = new int[1];
  String k = keyFor(u, id, why);
  if (k == null) return 0L;
  if (@PKG@.SackDefs.isCatch(id)) {   // whole fish carry their weight entries: the checked take + put of the fish keys' ledger
    if (count(u, id) < n) return 0L;
    long ft = take(u, id, n);
    if (ft == n) { TAKEOPENS.incrementAndGet(); return n; }
    if (ft > 0L) put(u, id, ft);
    return 0L;
  }
  String e = null;
  int x = @PKG@.VoidCompact.idxBase(id);
  if (x >= 0 && @PKG@.SackCfg.CRAFT_OPEN) {
    String e0 = @PKG@.VoidCompact.enchAt(x);
    String ce = @PKG@.SackDefs.homeOf(e0);
    @PLA@ p = playerOf(u);
    if (ce != null && p != null && @PKG@.SweepTask.caps(p.getInventory()).containsKey(ce)) e = e0;
  }
  @PKG@.BagMirror.beforeTake(k);   // live-mirror rule: book what a bench / pocket craft already took BEFORE the pool is read
  long[] r = takeOpenL(k, id, e, n);
  if (r[0] <= 0L) return 0L;
  // from here on the items are gone from the pool: every later step is caught on its own so the caller always learns the real amount
  try { @PKG@.BagMirror.afterTake(k, id); if (r[1] > 0L) @PKG@.BagMirror.afterTake(k, e); } catch (Throwable t1) { @PKG@.SackPool.warn("bag bridge: mirror trim failed after a takeOpen: " + t1); }
  long now = System.currentTimeMillis();
  try { LASTKEY.put(u.toString() + "|" + id, k); owe(k, id, r[0], now); oweOpen(k, id, r[1], now); } catch (Throwable t2) { }
  if (r[1] > 0L) @PKG@.VoidCompact.OPENED.addAndGet(r[1]);
  TAKEOPENS.incrementAndGet();
  try { @PKG@.CraftLog.later(k, "BAG-TAKEOPEN " + id + " " + r[0] + (r[1] > 0L ? " (opened " + r[1] + " " + e + ", the change stays loose)" : "") + " (sacks:fn:takeOpen)"); } catch (Throwable t3) { }
  try { @PKG@.SackPool.saveSoon(k); } catch (Throwable t4) { @PKG@.SackPool.DIRTY.put(k, Boolean.TRUE); }
  return r[0];
}"""), sbr))
# ================= 0.8.17 THE VOID'S WEIGHED FISH for SkyyFishing 0.1.10 (tools/sacks_0_8_17_patch.py A; world thread only) =================
''')
P.rep(r'''    if (this.mode == 18) return @PKG@.SackBridge.call2(this.mode, o);   // 0.8.28: sacks:fn:craftWhy (before the fish modes)
''', r'''    if (this.mode == 18) return @PKG@.SackBridge.call2(this.mode, o);   // 0.8.28: sacks:fn:craftWhy (before the fish modes)
    if (this.mode == 19) {   // 0.8.32 sacks:fn:takeOpen {UUID, itemId, qty} -> Long (qty or 0)
      if (!(o instanceof Object[])) return Long.valueOf(0L);
      Object[] a19 = (Object[]) o;
      if (a19.length < 3 || !(a19[0] instanceof java.util.UUID) || !(a19[1] instanceof String) || !(a19[2] instanceof Number)) return Long.valueOf(0L);
      return Long.valueOf(@PKG@.SackBridge.takeOpen((java.util.UUID) a19[0], (String) a19[1], ((Number) a19[2]).longValue()));
    }
''')
P.rep('''  sbr0.put("sacks:fn:craftWhy", new {PKG}.SackFn(18));   // 0.8.28: why craftList leaves a recipe out (SkyyGear's /smithing lock note)
''', '''  sbr0.put("sacks:fn:craftWhy", new {PKG}.SackFn(18));   // 0.8.28: why craftList leaves a recipe out (SkyyGear's /smithing lock note)
  sbr0.put("sacks:fn:takeOpen", new {PKG}.SackFn(19));   // 0.8.32: take N, loose first, the fewest Enchanted opened, all or nothing
''')

# ================================================================ 3. the dispatchers on our own ticker thread + their timing
P.rep('''sthr.addConstructor(CtNewConstructor.make("public SackThreads() { }", sthr))
sthr.addMethod(CtNewMethod.make("""
public Thread newThread(Runnable r) {
  Thread t = new Thread(r, "SkyySacks-writer");''', '''sthr.addField(CtField.make('public String nm = "SkyySacks-writer";', sthr))   # 0.8.32: + a name (SkyySacks-ticker)
sthr.addConstructor(CtNewConstructor.make("public SackThreads() { }", sthr))
sthr.addConstructor(CtNewConstructor.make("public SackThreads(String n) { if (n != null) this.nm = n; }", sthr))
sthr.addMethod(CtNewMethod.make("""
public Thread newThread(Runnable r) {
  Thread t = new Thread(r, this.nm);''')
P.rep('''sp.addField(CtField.make("public static volatile java.util.concurrent.ScheduledExecutorService WRITER;", sp))
''', '''sp.addField(CtField.make("public static volatile java.util.concurrent.ScheduledExecutorService WRITER;", sp))
# 0.8.32: the private dispatcher thread (daemon "SkyySacks-ticker"): SackTick / CraftTick / ProcTick + the AccSettle hop - never the shared
# HytaleServer.SCHEDULED_EXECUTOR (another mod's stuck task) nor the writer (a slow disk write)
sp.addField(CtField.make("public static volatile java.util.concurrent.ScheduledExecutorService TICKER;", sp))
''')
# SackBeat: the per-dispatcher timing (0 sweep SackTick, 1 craft link CraftTick, 2 furnace ProcTick)
P.rep(r'''           "public static final java.util.concurrent.atomic.AtomicLong RECHECKS = new java.util.concurrent.atomic.AtomicLong();"):
    sbeat.addField(CtField.make(_f, sbeat))
''', r'''           "public static final java.util.concurrent.atomic.AtomicLong RECHECKS = new java.util.concurrent.atomic.AtomicLong();",
           # 0.8.32: the slowest run of each dispatcher (ns), how many took SLOW_NS or more, the WARN clock
           "public static final long[] MAXNS = new long[3];", "public static final long[] RUNS = new long[3];",
           "public static final java.util.concurrent.atomic.AtomicLong SLOWS = new java.util.concurrent.atomic.AtomicLong();",
           "public static volatile long SLOW_NS = 1000000000L;", "public static volatile long LASTSLOW = 0L;"):
    sbeat.addField(CtField.make(_f, sbeat))
sbeat.addMethod(CtNewMethod.make(jt(r"""
public static synchronized void bump(int w, long ns) { RUNS[w] = RUNS[w] + 1L; if (ns > MAXNS[w]) MAXNS[w] = ns; }"""), sbeat))
sbeat.addMethod(CtNewMethod.make(jt(r"""
public static synchronized long maxAt(int w) { return MAXNS[w]; }"""), sbeat))
# 0.8.32: one dispatcher run took ns (w = 0 sweep, 1 craft link, 2 furnace): the max kept; SLOW_NS or more = one WARN a minute at most
sbeat.addMethod(CtNewMethod.make(jt(r"""
public static void took(int w, long ns) {
  if (w < 0 || w > 2) return;
  bump(w, ns);
  if (ns < SLOW_NS) return;
  SLOWS.incrementAndGet();
  long now = System.currentTimeMillis();
  if (now - LASTSLOW < 60000L) return;
  LASTSLOW = now;
  String[] nm = new String[] { "the 2 s sweep dispatcher", "the 300 ms crafting link dispatcher", "the 1 s Furnace / Tannery dispatcher" };
  @PKG@.SackPool.warn(nm[w] + " took " + (ns / 1000000L) + " ms in one run (SkyySacks-ticker; logged once a minute at most)");
}"""), sbeat))
sbeat.addMethod(CtNewMethod.make(jt(r"""
public static String maxText() {
  long a = maxAt(0); long b = maxAt(1); long c = maxAt(2);
  return "tick max: sweep " + (a / 1000000L) + " ms, craft link " + (b / 1000000L) + " ms, furnace " + (c / 1000000L) + " ms (runs " + RUNS[0] + " / " + RUNS[1] + " / " + RUNS[2] + ", 1 s+ " + SLOWS.get() + ")";
}"""), sbeat))
''')
P.rep('''public void run() {{
  try {{ {PKG}.PopupHide.tick(); }} catch (Throwable tp) {{ }}   // 0.8.16: the vanilla pickup popup switch (B1)
''', '''public void run() {{
  long tk0 = System.nanoTime();   // 0.8.32: SackBeat.took
  try {{ {PKG}.PopupHide.tick(); }} catch (Throwable tp) {{ }}   // 0.8.16: the vanilla pickup popup switch (B1)
''')
P.rep('''      w.execute(new {PKG}.SweepTask(pr, wu));
    }}
  }} catch (Throwable t) {{ }}
}}""", tick))''', '''      w.execute(new {PKG}.SweepTask(pr, wu));
    }}
  }} catch (Throwable t) {{ }}
  {PKG}.SackBeat.took(0, System.nanoTime() - tk0);   // 0.8.32
}}""", tick))''')
P.rep('''public void run() {{
  try {{ {PKG}.BenchLink.pocketCheck(); }} catch (Throwable t0) {{ }}   // 0.7.18: the bags.pocketCraft backstop, once per tick
''', '''public void run() {{
  long tk0 = System.nanoTime();   // 0.8.32: SackBeat.took
  try {{ {PKG}.BenchLink.pocketCheck(); }} catch (Throwable t0) {{ }}   // 0.7.18: the bags.pocketCraft backstop, once per tick
''')
P.rep('''      w.execute(new {PKG}.CraftLinkTask(pr, wu));
    }}
  }} catch (Throwable t) {{ }}
}}""", ctk))''', '''      w.execute(new {PKG}.CraftLinkTask(pr, wu));
    }}
  }} catch (Throwable t) {{ }}
  {PKG}.SackBeat.took(1, System.nanoTime() - tk0);   // 0.8.32
}}""", ctk))''')
P.rep('''ptick.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{''', '''ptick.addMethod(CtNewMethod.make(f"""
public void run() {{
  long tk0 = System.nanoTime();   // 0.8.32: SackBeat.took
  try {{''')
P.rep('''      w.execute(new {PKG}.ProcTask(pr, wu));
    }}
  }} catch (Throwable t) {{ }}
}}""", ptick))''', '''      w.execute(new {PKG}.ProcTask(pr, wu));
    }}
  }} catch (Throwable t) {{ }}
  {PKG}.SackBeat.took(2, System.nanoTime() - tk0);   // 0.8.32
}}""", ptick))''')
P.rep('''  try { @HSV@.SCHEDULED_EXECUTOR.schedule(as, 250L, java.util.concurrent.TimeUnit.MILLISECONDS); }
''', '''  try {
    java.util.concurrent.ScheduledExecutorService tx = @PKG@.SackPool.TICKER;   // 0.8.32: our ticker thread (the shared one without it)
    if (tx != null) tx.schedule(as, 250L, java.util.concurrent.TimeUnit.MILLISECONDS);
    else @HSV@.SCHEDULED_EXECUTOR.schedule(as, 250L, java.util.concurrent.TimeUnit.MILLISECONDS);
  }
''')
P.rep('''  {PKG}.SackPool.WRITER = java.util.concurrent.Executors.newSingleThreadScheduledExecutor(new {PKG}.SackThreads());
''', '''  {PKG}.SackPool.WRITER = java.util.concurrent.Executors.newSingleThreadScheduledExecutor(new {PKG}.SackThreads());
  // 0.8.32: the private dispatcher thread (daemon "SkyySacks-ticker") - the 2 s sweep, the 300 ms crafting link, the 1 s Furnace / Tannery
  {PKG}.SackPool.TICKER = java.util.concurrent.Executors.newSingleThreadScheduledExecutor(new {PKG}.SackThreads("SkyySacks-ticker"));
''')
P.rep('''  // 0.8.31: the 2 s sweep dispatcher runs on OUR thread (the shared scheduler was held by another task for 12 minutes on 10-25: no sweep, no auto-compact)
  this.ticker = {PKG}.SackPool.WRITER.scheduleAtFixedRate(new {PKG}.SackTick(), 2L, 2L, java.util.concurrent.TimeUnit.SECONDS);
  this.saver = {PKG}.SackPool.WRITER.scheduleAtFixedRate(new {PKG}.SackSaver(), 10L, 10L, java.util.concurrent.TimeUnit.SECONDS);
  this.crafter = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.CraftTick(), 1000L, 300L, java.util.concurrent.TimeUnit.MILLISECONDS);
  this.procTicker = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.ProcTick(), 3L, 1L, java.util.concurrent.TimeUnit.SECONDS);
''', '''  // 0.8.31: the 2 s sweep dispatcher runs on OUR thread (the shared scheduler was held by another task for 12 minutes on 10-25: no sweep, no auto-compact)
  // 0.8.32: all three dispatchers on SkyySacks-ticker (never the shared scheduler, never behind a pool write); the writer keeps the saves
  this.ticker = {PKG}.SackPool.TICKER.scheduleAtFixedRate(new {PKG}.SackTick(), 2L, 2L, java.util.concurrent.TimeUnit.SECONDS);
  this.saver = {PKG}.SackPool.WRITER.scheduleAtFixedRate(new {PKG}.SackSaver(), 10L, 10L, java.util.concurrent.TimeUnit.SECONDS);
  this.crafter = {PKG}.SackPool.TICKER.scheduleAtFixedRate(new {PKG}.CraftTick(), 1000L, 300L, java.util.concurrent.TimeUnit.MILLISECONDS);
  this.procTicker = {PKG}.SackPool.TICKER.scheduleAtFixedRate(new {PKG}.ProcTick(), 3L, 1L, java.util.concurrent.TimeUnit.SECONDS);
''')
P.rep('''  try {{ if (this.procTicker != null) this.procTicker.cancel(false); }} catch (Throwable t) {{ }}
''', '''  try {{ if (this.procTicker != null) this.procTicker.cancel(false); }} catch (Throwable t) {{ }}
  // 0.8.32: the ticker stops (a queued AccSettle hop still runs, 1 s at most - else that accessory simply stays in the inventory)
  try {{
    java.util.concurrent.ScheduledExecutorService tx = {PKG}.SackPool.TICKER;
    {PKG}.SackPool.TICKER = null;
    if (tx != null) {{ tx.shutdown(); tx.awaitTermination(1L, java.util.concurrent.TimeUnit.SECONDS); }}
  }} catch (Throwable t) {{ }}
''')
P.rep('''" re-checks; shared scheduler stalls seen: " + {PKG}.SackBeat.STALLS.get()); }} catch (Throwable t) {{ }}   // 0.8.30 / 0.8.31''',
      '''" re-checks; shared scheduler stalls seen: " + {PKG}.SackBeat.STALLS.get() + "; " + {PKG}.SackBeat.maxText() + "; takeOpen calls: " + {PKG}.SackBridge.TAKEOPENS.get()); }} catch (Throwable t) {{ }}   // 0.8.30 / 0.8.31 / 0.8.32''')
P.rep('''re-check every " + {PKG}.SackCfg.CMP_RECHECK + " s; the 2 s sweep on its own thread (0.8.31)");''',
      '''re-check every " + {PKG}.SackCfg.CMP_RECHECK + " s; the sweep / crafting link / Furnace dispatchers on SkyySacks-ticker (0.8.32); Greater Essence of Life opens like an Enchanted item; bridge sacks:fn:takeOpen");''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.8.32 adds no system / command"
assert "HytaleServer.SCHEDULED_EXECUTOR.scheduleAtFixedRate" not in P.s and "{HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate" not in P.s
P.finish()
