"""Derive SkyyShards/build_skyyshards_0.4.33.py from the SET pin 0.4.32 (the GENERATED build_skyyshards_0.4.32.py; edit THIS file, then
regenerate: python tools/shards_0_4_33_patch.py; never re-run shards_0_4_32_patch.py on top of it). Every anchor is asserted once; at the end
every change is undone on a copy and compared with 0.4.32 (nothing else changed). Line endings kept.
Run:  python tools/shards_0_4_33_patch.py   then   python SkyyShards/build_skyyshards_0.4.33.py   (never --deploy from an agent)
Test: python SkyyShards/test_skyyshards_0.4.33.py [--dir <folder inside tools/dev/scratch/>] [--keep]

0.4.33 (2026-11-24) = SHARD LINK - shard items straight into the pocket (round link1, with SkyySacks 0.8.42). Skyy 2026-11-14: "i want an upgrade
  that allos the shards to go straight into the pocket dimension with no need to collect. should it be a late game shard upgrade? or a late game
  pocket dimension upgrade?" + popup "Make Shard Link a late-game pocket upgrade?": "Yes, pocket upgrade" (docs/answered/world.md 'SHARD LINK =
  POCKET UPGRADE': collection credit + XP paid as if collected; when the pocket is full the rest waits in the shard, Collect all still works)
  + 2026-11-23 "looks better. go head and build everything on your list."
  The upgrade itself is bought on the pocket (SkyySacks 0.8.42, the /pd page: one per pocket). This jar moves the items:
  1. WHEN: lazy, at the moments production is settled - the clicker page opening / redrawing, our tick (every ShLink.TICK_SEC = 30 s for every
     online player), and Collect all (the link first, then the Collect takes the rest). Only the island OWNER on the profile that owns the
     shard (k = their active profile key; co-op members / visitors never move anything) and only an unlocked shard. Offline harvest, the Time
     Compressor and the Auto-Compactor work as before: they decide what is stored; the link moves what is stored.
  2. WHAT: exactly what Collect all would give - stored stock (the Auto-Compactor's Enchanted items + the rest, smelted bars with Smithy I),
     bonus finds, legacy stock, the clicked drops, the Combat town's rolled drops (the same roll as Collect). NOT: unidentified bags and
     town coins (they need Collect all), items no linked pocket takes (each item goes into ITS pocket: SkyySacks catOf - ores Mining, bars /
     hides Smithing, raw meat / fruit Farming, bones Combat ...; only pockets whose Shard Link is on).
  3. HOW (crash-safe, nothing lost or doubled): (a) under the shard lock: settle, plan every item against the room the pocket reported, take
     the planned items out of the shard AND write the journal line <kind>.linkpend = "<token>|<what each item came from>" - ONE save; (b) lock
     released: sacks:fn:link put (SkyySacks writes the items + the token in one atomic pool save, never past the room); (c) under the lock:
     what the pocket did not take goes back exactly where it came from, the collection credit + XP of what it took is written as the usual
     owed.coll.<item> / owed.xp.<Skill> lines and the journal line removed - ONE save; then the marker is acked and the owed lines are paid
     through the same ShCore.owed / owedXp a Collect uses (lock released). A restart after (a) asks sacks:fn:link done: "never happened" =
     everything back, accepted = (c). The XP fraction a small batch rounds away is kept (<kind>.linkxpf) so many small transfers pay exactly
     the XP of one big Collect.
  4. CREDIT = Collect's: the island's own collection for its stock (Enchanted / compacted = 100 each), bars = their ore, alloys = their two
     ores in turns (owedAs), bonus finds as Collect (the alias rule), XP = ShCore.xpTotal's formula on the moved items (Combat: none, as
     Collect). Clicked drops: collection only (the click paid the XP), as Collect.
  5. THE PAGE: the store line says "Linked to pocket (<pockets>): new items go straight there." (or "... - it is full: the rest waits here")
     while a link is on for that shard's items.
  FIX (critics): ids holding , ; = | are never taken (Collect all pays them); "nothing to move" puts the shard back key by key (never an
     empty file for a lock-free reader); the Moon Blade cache is warmed before take() settles; no SkyySacks = no page line; every ack is kept in
     <kind>.linkack (written in the settle save) until SkyySacks answers TRUE / FALSE, asked again on the next run (a lost ack / a restart).
  SAVED DATA: new keys <kind>.linkpend (only between (a) and (c)), <kind>.linkxpf and <kind>.linkack. No migration, no Server Setup row (the switch and prices
  are SkyySacks' pd.link.* rows).
  ROLLBACK 0.4.33 -> 0.4.32 alone: switch Shard Link off first (Server Setup -> Sacks -> pd.link.on) and wait one minute (no <kind>.linkpend left:
  0.4.32 ignores that key, so items in a half-done transfer would wait unseen until 0.4.33 returns). Then safe: Collect works as before.
"""
import os, sys

HERE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "SkyyShards")
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "tools"))
import soundpass_gen as G

P = G.Patch(os.path.join(HERE, "build_skyyshards_0.4.32.py"), os.path.join(HERE, "build_skyyshards_0.4.33.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.4.32"\n') and P.has("GENERATED by tools/shards_0_4_32_patch.py") and P.has("CLK_HY_SRC") and not P.has("ShLink"), \
    "not the generated SkyyShards 0.4.32"
REG0, SYS0 = P.s.count("registerCommand("), P.s.count("registerSystem(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.4.33 (2026-11-24)"):].rstrip() + "\n"

# ---------------------------------------------------------------------------------------------------- 0. header + version
P.rep('''"""SkyyShards 0.4.32 - build script (javassist via jpype). GENERATED by tools/shards_0_4_32_patch.py from build_skyyshards_0.4.31.py
(generated by tools/shards_0_4_31_patch.py from 0.4.30, ... back to tools/shards_0_4_patch.py from 0.3.2; edit the patch, never this file).
Changes are marked "0.4.32" /''', '''"""SkyyShards 0.4.33 - build script (javassist via jpype). GENERATED by tools/shards_0_4_33_patch.py from build_skyyshards_0.4.32.py
(generated by tools/shards_0_4_32_patch.py from 0.4.31, ... back to tools/shards_0_4_patch.py from 0.3.2; edit the patch, never this file).
Changes are marked "0.4.33" / "0.4.32" /''')
P.rep('''Run:   python SkyyShards/build_skyyshards_0.4.32.py   -> SkyyShards/SkyyShards-0.4.32.jar   (never --deploy: tools/deploy_set.py installs the set)
Check: python SkyyShards/test_skyyshards_0.4.32.py
''', '''Run:   python SkyyShards/build_skyyshards_0.4.33.py   -> SkyyShards/SkyyShards-0.4.33.jar   (never --deploy: tools/deploy_set.py installs the set)
Check: python SkyyShards/test_skyyshards_0.4.33.py
''' + NOTE)
P.rep('VERSION = "0.4.32"\n', 'VERSION = "0.4.33"\n')

# ---------------------------------------------------------------------------------------------------- 1. ShLink (before collect0: Collect all calls it)
LINK = r'''# ================= 0.4.33 SHARD LINK: ShLink (tools/shards_0_4_33_patch.py docstring) =================
# An entry of a transfer = String[] { kind S stock / E bonus find / L legacy / H clicked drop / C town drop, island, item id, items, base units each,
# collection id, XP per base unit }; the journal line <kind>.linkpend = "<token>|<entry>;<entry>..." (fields joined by ",").
lnk = mk("ShLink")
for f in ("public static final java.util.concurrent.ConcurrentHashMap BUSY = new java.util.concurrent.ConcurrentHashMap();",   # "<key>|<kind>" while moving
          "public static final java.util.concurrent.ConcurrentHashMap LINE = new java.util.concurrent.ConcurrentHashMap();",   # "<key>|<kind>" -> the page line
          "public static final java.util.concurrent.atomic.AtomicLong SEQ = new java.util.concurrent.atomic.AtomicLong();",
          "public static final java.util.concurrent.atomic.AtomicLong RUNS = new java.util.concurrent.atomic.AtomicLong();",
          "public static final java.util.concurrent.atomic.AtomicLong MOVED = new java.util.concurrent.atomic.AtomicLong();",
          "public static final java.util.concurrent.atomic.AtomicLong BACK = new java.util.concurrent.atomic.AtomicLong();",
          "public static final java.util.concurrent.atomic.AtomicLong RESOLVED = new java.util.concurrent.atomic.AtomicLong();",
          "public static volatile java.util.function.Function FN_TEST;",   # the harness's SkyySacks (null in the game)
          "public static volatile int TICK_SEC = 30;",
          "public static final java.util.concurrent.ConcurrentHashMap LAST = new java.util.concurrent.ConcurrentHashMap();",   # "<key>|<kind>" -> the last page run (ms)
          "public static volatile long PAGE_MS = 5000L;"):
    F(lnk, f)
M(lnk, r"""
public static java.util.function.Function fn() {
  java.util.function.Function f = FN_TEST;
  if (f != null) return f;
  return @PKG@.ShCfg.fn("sacks:fn:link");
}""")
# a SkyySacks call - never under the shard lock (the 0.4.14 rule); a throw = null
M(lnk, r"""
public static Object ask(Object[] a) {
  java.util.function.Function f = fn();
  if (f == null) return null;
  if (@PKG@.ShStore.LOCK.isHeldByCurrentThread()) { @PKG@.ShCfg.warnOnce("linklock", "Shard Link: a SkyySacks call under the shard lock was skipped (logged once)"); return null; }
  try { return f.apply(a); } catch (Throwable t) { @PKG@.ShCfg.warnOnce("linkask", "sacks:fn:link failed (logged once; the items stay in the shard): " + t); return null; }
}""")
M(lnk, r"""
public static String pk(int kd) { return @PKG@.ShMath.kk(kd, "linkpend"); }""")
M(lnk, r"""
public static String xk(int kd) { return @PKG@.ShMath.kk(kd, "linkxpf"); }""")
M(lnk, r"""
public static String ak(int kd) { return @PKG@.ShMath.kk(kd, "linkack"); }""")
# FIX (critics): the tokens SkyySacks has not confirmed an ack for (<kind>.linkack = "tok,tok"; at most 20 - an older one only leaves a line
# in the pool file). Added in the settle save; dropped (memory, saved with the next shard save) when ack answers TRUE / FALSE; kept on null.
M(lnk, r"""
public static String dropTok(String q, String tk) {
  String[] a = q == null ? new String[0] : q.split(",");
  StringBuilder b = new StringBuilder();
  for (int i = 0; i < a.length; i++) { String t = a[i].trim(); if (t.length() == 0 || t.equals(tk)) continue; if (b.length() > 0) b.append(','); b.append(t); }
  return b.toString();
}""")
M(lnk, r"""
public static String addTok(String q, String tk) {
  String[] a = dropTok(q, tk).split(",");
  StringBuilder b = new StringBuilder();
  int from = a.length > 19 ? a.length - 19 : 0;
  for (int i = from; i < a.length; i++) { if (a[i].length() == 0) continue; if (b.length() > 0) b.append(','); b.append(a[i]); }
  if (b.length() > 0) b.append(',');
  return b.append(tk).toString();
}""")
M(lnk, r"""
public static void ackDone(int kd, java.util.Properties p, String tk, Object r) {
  if (!(r instanceof Boolean)) return;
  @PKG@.ShStore.LOCK.lock(); try {
    String q = dropTok(@PKG@.ShStore.str(p, ak(kd)), tk);
    if (q.length() == 0) p.remove(ak(kd)); else p.setProperty(ak(kd), q);
  } finally { @PKG@.ShStore.LOCK.unlock(); }
}""")
M(lnk, r"""
public static int reAck(String k, int kd, java.util.Properties p) {
  String q;
  @PKG@.ShStore.LOCK.lock(); try { q = @PKG@.ShStore.str(p, ak(kd)); } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (q.length() == 0) return 0;
  String[] a = q.split(",");
  int n = 0;
  for (int i = 0; i < a.length; i++) {
    String t = a[i].trim();
    if (t.length() == 0) continue;
    Object r = ask(new Object[] { "ack", k, t });
    ackDone(kd, p, t, r);
    if (r instanceof Boolean) n++;
  }
  return n;
}""")
M(lnk, r"""
public static String tok(int kd) {
  return "L" + kd + "x" + Long.toString(System.currentTimeMillis(), 36) + "x" + SEQ.incrementAndGet();
}""")
M(lnk, r"""
public static void addL(java.util.Map m, String id, long n) {
  if (id == null || id.length() == 0 || n == 0L) return;
  Object o = m.get(id);
  m.put(id, Long.valueOf((o == null ? 0L : ((Long) o).longValue()) + n));
}""")
# the ids the shard could hand out now (the room question): every island's own item / bar / Enchanted forms, the bonus find, legacy, drops, the town's roll
# FIX (critic): an id holding a journal / bridge separator (, ; = |) is never asked about and never taken (it waits for Collect all)
M(lnk, r"""
public static boolean idOk(String id) {
  return id != null && id.length() > 0 && id.indexOf(',') < 0 && id.indexOf(';') < 0 && id.indexOf('=') < 0 && id.indexOf('|') < 0;
}""")
M(lnk, r"""
public static String cands(int kd, java.util.Properties p) {
  java.util.LinkedHashMap m = new java.util.LinkedHashMap();
  int n = @PKG@.ShMath.SLOTS;
  boolean isC = kd == @PKG@.ShCombat.CK;
  for (int i = 0; i < n; i++) {
    boolean has = @PKG@.ShMath.hasIsland(kd, p, i);
    if (has) {
      int t = @PKG@.ShIsl.ty(kd, p, i);
      if (!isC) { addL(m, @PKG@.ShIsl.PROD[t], 1L); addL(m, @PKG@.ShIsl.SMELT[t], 1L); addL(m, @PKG@.ShIsl.ENCH[t], 1L); addL(m, @PKG@.ShIsl.SMELTE[t], 1L); }
      else {
        long s = @PKG@.ShMath.stored(kd, p, i);
        if (s > 0L) { String[] di = (String[]) @PKG@.ShCombat.rollFor(p, i, s)[0]; for (int j = 0; j < di.length; j++) addL(m, di[j], 1L); }
      }
    }
    java.util.Iterator hi = @PKG@.ShMath.held(kd, p, i).keySet().iterator();
    while (hi.hasNext()) addL(m, (String) hi.next(), 1L);
    String lg = @PKG@.ShStore.str(p, @PKG@.ShIsl.ik(kd, i, "legacy"));
    int lc = lg.lastIndexOf(':');
    if (lc > 0) addL(m, lg.substring(0, lc), 1L);
  }
  addL(m, @PKG@.ShKind.BONUS[kd], 1L);
  StringBuilder b = new StringBuilder();
  java.util.Iterator it = m.keySet().iterator();
  while (it.hasNext()) { String id = (String) it.next(); if (!idOk(id)) continue; if (b.length() > 0) b.append(','); b.append(id); }
  return b.toString();
}""")
M(lnk, r"""
public static String ent(String f, int i, String id, long q, long u, String c, double xi) {
  return f + "," + i + "," + id + "," + q + "," + u + "," + c + "," + xi;
}""")
# FIX (critic): p put back to old key by key (never clear() + putAll(): ShStore.get's readers take no lock and would see an empty file)
M(lnk, r"""
public static void restore(java.util.Properties p, java.util.Properties old) {
  java.util.ArrayList ks = new java.util.ArrayList(p.keySet());
  for (int i = 0; i < ks.size(); i++) { Object k0 = ks.get(i); if (!old.containsKey(k0)) p.remove(k0); }
  java.util.Iterator it = old.entrySet().iterator();
  while (it.hasNext()) { java.util.Map.Entry e = (java.util.Map.Entry) it.next(); if (!e.getValue().equals(p.get(e.getKey()))) p.put(e.getKey(), e.getValue()); }
}""")
# (a) under the shard lock: settle, plan against the room (cat -> Long, id -> cat), debit, the journal line, ONE save. Returns the journal
# line written, "" = nothing to move (nothing changed), null = refused (nothing changed). full[0] = a linked item met a full pocket.
M(lnk, r"""
public static String take(java.util.UUID u, String k, int kd, java.util.Properties p, java.util.HashMap room, java.util.HashMap idCat, String tk, boolean[] full) {
  @PKG@.ShStore.LOCK.lock(); try {
    if (@PKG@.ShStore.str(p, pk(kd)).length() > 0) return null;
    java.util.Properties old = new java.util.Properties();
    old.putAll(p);
    long now = @PKG@.ShCore.now();
    @PKG@.ShMath.settleAll(kd, p, now);
    int n = @PKG@.ShMath.SLOTS;
    boolean isC = kd == @PKG@.ShCombat.CK;
    int cmp = @PKG@.ShMath.compactor(kd, p);
    String bon = @PKG@.ShKind.BONUS[kd];
    java.util.ArrayList es = new java.util.ArrayList();
    double[] xa = new double[n];
    for (int i = 0; i < n; i++) {
      if (isC) @PKG@.ShCore.roll(p, i);
      boolean has = @PKG@.ShMath.hasIsland(kd, p, i);
      long s0 = isC ? 0L : @PKG@.ShMath.stored(kd, p, i);
      long e0 = bon.length() == 0 ? 0L : @PKG@.ShMath.ench(kd, p, i);
      String lg = @PKG@.ShStore.str(p, @PKG@.ShIsl.ik(kd, i, "legacy"));
      long l0 = 0L;
      String lid = null;
      int lc = lg.lastIndexOf(':');
      if (lc > 0) { try { l0 = Long.parseLong(lg.substring(lc + 1).trim()); lid = lg.substring(0, lc); } catch (Throwable t) { l0 = 0L; } }
      if (l0 < 0L) l0 = 0L;
      java.util.LinkedHashMap hm = @PKG@.ShMath.held(kd, p, i);
      if (s0 > 0L || e0 > 0L || (l0 > 0L && has) || (isC && !hm.isEmpty())) xa[i] = @PKG@.ShMath.xpAvg(kd, p, i, now);
      if (s0 > 0L && has) {
        int t = @PKG@.ShIsl.ty(kd, p, i);
        boolean sm = @PKG@.ShTotem.smelts(kd, p, i) && @PKG@.ShIsl.SMELT[t].length() > 0;
        String out = sm ? @PKG@.ShIsl.SMELT[t] : @PKG@.ShIsl.PROD[t];
        String en = sm ? @PKG@.ShIsl.SMELTE[t] : @PKG@.ShIsl.ENCH[t];
        boolean ce = cmp >= 1 && en.length() > 0;
        if (ce && s0 / 100L > 0L) es.add(new Object[] { "S", Integer.valueOf(i), en, Long.valueOf(s0 / 100L), Long.valueOf(100L), @PKG@.ShIsl.PROD[t] });
        long rest = ce ? s0 % 100L : s0;
        if (rest > 0L) es.add(new Object[] { "S", Integer.valueOf(i), out, Long.valueOf(rest), Long.valueOf(1L), @PKG@.ShIsl.PROD[t] });
      }
      if (e0 > 0L) es.add(new Object[] { "E", Integer.valueOf(i), bon, Long.valueOf(e0), Long.valueOf(1L), bon });
      if (l0 > 0L && lid != null) {
        String lb = @PKG@.ShIsl.enchBase(lid);
        es.add(new Object[] { "L", Integer.valueOf(i), lid, Long.valueOf(l0), Long.valueOf(lb != null ? 100L : 1L), lb != null ? lb : lid });
      }
      java.util.Iterator hi = hm.entrySet().iterator();
      while (hi.hasNext()) {
        java.util.Map.Entry he = (java.util.Map.Entry) hi.next();
        es.add(new Object[] { isC ? "C" : "H", Integer.valueOf(i), he.getKey(), he.getValue(), Long.valueOf(1L), he.getKey() });
      }
    }
    StringBuilder jb = new StringBuilder();
    long tot = 0L;
    boolean[] deb = new boolean[n];
    for (int x = 0; x < es.size(); x++) {
      Object[] e = (Object[]) es.get(x);
      String f = (String) e[0];
      int i = ((Integer) e[1]).intValue();
      String id = (String) e[2];
      long q = ((Long) e[3]).longValue();
      String cat = (String) idCat.get(id);
      if (cat == null || q <= 0L || !idOk(id) || !idOk((String) e[5])) continue;
      Long rl = (Long) room.get(cat);
      long r = rl == null ? 0L : rl.longValue();
      long a = q < r ? q : r;
      if (a < q) full[0] = true;
      if (a <= 0L) continue;
      room.put(cat, Long.valueOf(r - a));
      long un = ((Long) e[4]).longValue();
      if ("S".equals(f)) { p.setProperty(@PKG@.ShMath.ik(kd, i, "stored"), String.valueOf(@PKG@.ShMath.stored(kd, p, i) - a * un)); deb[i] = true; }
      else if ("E".equals(f)) p.setProperty(@PKG@.ShMath.ik(kd, i, "ench"), String.valueOf(@PKG@.ShMath.ench(kd, p, i) - a));
      else if ("L".equals(f)) {
        long left = q - a;
        if (left > 0L) p.setProperty(@PKG@.ShIsl.ik(kd, i, "legacy"), id + ":" + left); else p.remove(@PKG@.ShIsl.ik(kd, i, "legacy"));
        deb[i] = true;
      } else {
        java.util.LinkedHashMap hm2 = @PKG@.ShMath.held(kd, p, i);
        Object o = hm2.get(id);
        long l2 = (o == null ? 0L : ((Long) o).longValue()) - a;
        if (l2 > 0L) hm2.put(id, Long.valueOf(l2)); else hm2.remove(id);
        @PKG@.ShMath.heldSet(kd, p, i, hm2);
      }
      if (jb.length() > 0) jb.append(';');
      jb.append(ent(f, i, id, a, un, (String) e[5], "H".equals(f) ? 0.0 : xa[i]));
      tot += a;
    }
    if (tot <= 0L) { restore(p, old); return ""; }   // nothing moves: the town's roll and the settle undone (Collect's rule; FIX: key by key)
    for (int i = 0; i < n; i++) if (deb[i]) @PKG@.ShMath.xpRe(kd, p, i, xa[i]);
    String line = tk + "|" + jb.toString();
    p.setProperty(pk(kd), line);
    String err = @PKG@.ShStore.save(k, p);
    if (err != null) { p.clear(); p.putAll(old); @PKG@.ShCfg.warnOnce("linksave", "Shard Link: the shard file could not be saved - nothing moved (logged once): " + err); return null; }
    @PKG@.ShStore.log(u + " " + k + " " + @PKG@.ShKind.KEYS[kd] + " LINK out " + line);
    return line;
  } finally { @PKG@.ShStore.LOCK.unlock(); }
}""")
# the collection credit of a clicked drop, as ShCore.owedAs (a bar = its ore, an alloy = its two ores in turns) - into a map, not paid
M(lnk, r"""
public static void credAs(java.util.UUID u, String id, long c, java.util.LinkedHashMap m) {
  if (id == null || c <= 0L) return;
  for (int i = 0; i < @PKG@.ShCore.AL_ID.length; i++) {
    if (!id.equals(@PKG@.ShCore.AL_ID[i])) continue;
    String a = @PKG@.ShCore.oreOfBar(@PKG@.ShCore.AL_A[i]);
    String b = @PKG@.ShCore.oreOfBar(@PKG@.ShCore.AL_B[i]);
    String pkk = String.valueOf(u) + "|" + @PKG@.ShCore.AL_ID[i];
    java.util.concurrent.atomic.AtomicLong al = (java.util.concurrent.atomic.AtomicLong) @PKG@.ShCore.AL_PAR.get(pkk);
    if (al == null) { @PKG@.ShCore.AL_PAR.putIfAbsent(pkk, new java.util.concurrent.atomic.AtomicLong()); al = (java.util.concurrent.atomic.AtomicLong) @PKG@.ShCore.AL_PAR.get(pkk); }
    long st0 = al.getAndAdd(c);
    long ha = (st0 % 2L == 0L) ? (c + 1L) / 2L : c / 2L;
    long hb = c - ha;
    if (a != null && ha > 0L) addL(m, a, ha);
    if (b != null && hb > 0L) addL(m, b, hb);
    return;
  }
  String o = @PKG@.ShCore.oreOfBar(id);
  addL(m, o != null ? o : id, c);
}""")
# (c) the result: acc = SkyySacks' accepted text ("id:n,..."; "" = nothing). Under the lock: the journal line re-read (must be the same), each
# entry's accepted part credited, the rest back where it came from, the credit as owed.* lines, the journal line removed - ONE save.
# Returns the coll items + the XP skill to pay (Object[] { LinkedHashMap owedColl, String xpKey or null, Long moved }), null = not done.
M(lnk, r"""
public static Object[] settle(java.util.UUID u, String k, int kd, java.util.Properties p, String line, String acc) {
  java.util.HashMap left = new java.util.HashMap();
  String[] aa = acc == null ? new String[0] : acc.split(",");
  for (int j = 0; j < aa.length; j++) {
    String x = aa[j].trim();
    int c = x.lastIndexOf(':');
    if (c <= 0) continue;
    long v = 0L;
    try { v = Long.parseLong(x.substring(c + 1).trim()); } catch (Throwable t) { v = 0L; }
    if (v > 0L) addL(left, x.substring(0, c).trim(), v);
  }
  @PKG@.ShStore.LOCK.lock(); try {
    if (!line.equals(@PKG@.ShStore.str(p, pk(kd)))) return null;
    java.util.Properties old = new java.util.Properties();
    old.putAll(p);
    int bar = line.indexOf('|');
    String[] es = bar < 0 || bar + 1 >= line.length() ? new String[0] : line.substring(bar + 1).split(";");
    int n = @PKG@.ShMath.SLOTS;
    boolean[] back = new boolean[n];
    double[] xb = new double[n];
    long baseGiven = 0L; long gBonus = 0L; double xpD = 0.0; long moved = 0L; long backN = 0L;
    java.util.LinkedHashMap cred = new java.util.LinkedHashMap();
    java.util.LinkedHashMap credH = new java.util.LinkedHashMap();
    int bm = @PKG@.ShKind.BMULT[kd];
    for (int x = 0; x < es.length; x++) {
      String[] e = es[x].split(",");
      if (e.length < 7) continue;
      String f = e[0];
      int i = Integer.parseInt(e[1]);
      String id = e[2];
      long q = Long.parseLong(e[3]);
      long un = Long.parseLong(e[4]);
      String ci = e[5];
      double xi = Double.parseDouble(e[6]);
      if (i < 0 || i >= n || q <= 0L) continue;
      Long lv = (Long) left.get(id);
      long a = lv == null ? 0L : (lv.longValue() < q ? lv.longValue() : q);
      if (a > 0L) left.put(id, Long.valueOf(lv.longValue() - a));
      long r = q - a;
      moved += a;
      if (a > 0L) {
        if ("S".equals(f)) { baseGiven += a * un; xpD += (double) (a * un) * xi; addL(cred, ci, a * un); }
        else if ("L".equals(f)) { baseGiven += a * un; xpD += (double) (a * un) * (un == 100L && xi > 0.0 ? xi : (double) @PKG@.ShCfg.xpOf(kd)); addL(cred, ci, a * un); }
        else if ("C".equals(f)) { baseGiven += a; xpD += (double) a * xi; addL(cred, id, a); }
        else if ("E".equals(f)) { gBonus += a; xpD += (double) a * (bm > 1 ? (double) bm * xi : (double) @PKG@.ShKind.BXP[kd]); }
        else credAs(u, id, a, credH);
      }
      if (r > 0L) {
        backN += r;
        if ("S".equals(f)) { p.setProperty(@PKG@.ShMath.ik(kd, i, "stored"), String.valueOf(@PKG@.ShMath.stored(kd, p, i) + r * un)); back[i] = true; xb[i] = xi; }
        else if ("E".equals(f)) p.setProperty(@PKG@.ShMath.ik(kd, i, "ench"), String.valueOf(@PKG@.ShMath.ench(kd, p, i) + r));
        else if ("L".equals(f)) {
          String lg = @PKG@.ShStore.str(p, @PKG@.ShIsl.ik(kd, i, "legacy"));
          int lc = lg.lastIndexOf(':');
          long had = 0L;
          if (lc > 0 && lg.substring(0, lc).equals(id)) { try { had = Long.parseLong(lg.substring(lc + 1).trim()); } catch (Throwable t) { had = 0L; } }
          if (lc > 0 && !lg.substring(0, lc).equals(id)) {   // the island holds another legacy item now: the part goes to its drops (paid by Collect, never lost)
            java.util.LinkedHashMap hx = @PKG@.ShMath.held(kd, p, i);
            addL(hx, id, r);
            @PKG@.ShMath.heldSet(kd, p, i, hx);
          } else p.setProperty(@PKG@.ShIsl.ik(kd, i, "legacy"), id + ":" + (had + r));
          back[i] = true; xb[i] = xi;
        } else {
          java.util.LinkedHashMap hm = @PKG@.ShMath.held(kd, p, i);
          addL(hm, id, r);
          @PKG@.ShMath.heldSet(kd, p, i, hm);
        }
      }
    }
    for (int i = 0; i < n; i++) if (back[i]) @PKG@.ShMath.xpRe(kd, p, i, xb[i]);
    // the credit, exactly as ShCore.payCred: XP of the moved items (Combat: none), the alias / bonus rule, every collection line
    String skill = @PKG@.ShKind.SKILL[kd];
    long per = (long) @PKG@.ShCfg.xpOf(kd);
    long bxp = bm > 1 ? (long) bm * per : (long) @PKG@.ShKind.BXP[kd];
    boolean fx = kd == @PKG@.ShCore.FK;
    String xkey = null;
    if ((per > 0L || bxp > 0L || (fx && xpD > 0.0)) && (baseGiven > 0L || gBonus > 0L)) {
      long xp;
      if (fx) {
        double fr = 0.0;
        try { fr = Double.parseDouble(@PKG@.ShStore.str(p, xk(kd))); } catch (Throwable t) { fr = 0.0; }
        if (Double.isNaN(fr) || fr < 0.0 || fr >= 1.0) fr = 0.0;
        double xv = xpD * (double) @PKG@.ShCfg.XP_PCT / 100.0 + fr;
        xp = (long) Math.floor(xv + 0.000000001);
        double nf = xv - (double) xp;
        if (nf < 0.0000001) p.remove(xk(kd)); else p.setProperty(xk(kd), String.valueOf(nf));
      } else {
        long fl = @PKG@.ShStore.lng(p, xk(kd), 0L);
        if (fl < 0L || fl >= 100L) fl = 0L;
        long num = (baseGiven * per + gBonus * bxp) * (long) @PKG@.ShCfg.XP_PCT + fl;
        xp = num / 100L;
        if (num % 100L == 0L) p.remove(xk(kd)); else p.setProperty(xk(kd), String.valueOf(num % 100L));
      }
      if (xp > 0L) {
        xkey = "Farming".equals(skill) ? "owed.xp" : "owed.xp." + skill;
        p.setProperty(xkey, String.valueOf(@PKG@.ShStore.lng(p, xkey, 0L) + xp));
      }
    }
    String bon = @PKG@.ShKind.BONUS[kd];
    if (bm > 1 && gBonus > 0L) addL(cred, @PKG@.ShKind.PROD[kd], (long) bm * gBonus);
    if (bm <= 1 && gBonus > 0L) addL(cred, bon, gBonus);
    java.util.Iterator hi = credH.entrySet().iterator();
    while (hi.hasNext()) { java.util.Map.Entry he = (java.util.Map.Entry) hi.next(); addL(cred, (String) he.getKey(), ((Long) he.getValue()).longValue()); }
    java.util.Iterator ci2 = cred.entrySet().iterator();
    while (ci2.hasNext()) {
      java.util.Map.Entry ce = (java.util.Map.Entry) ci2.next();
      String ok = "owed.coll." + ce.getKey();
      p.setProperty(ok, String.valueOf(@PKG@.ShStore.lng(p, ok, 0L) + ((Long) ce.getValue()).longValue()));
    }
    p.setProperty(ak(kd), addTok(@PKG@.ShStore.str(p, ak(kd)), line.substring(0, bar < 0 ? line.length() : bar)));   // FIX: acked later
    p.remove(pk(kd));
    String err = @PKG@.ShStore.save(k, p);
    if (err != null) { p.clear(); p.putAll(old); @PKG@.ShCfg.warnOnce("linksave2", "Shard Link: the result could not be saved - retried (logged once): " + err); return null; }
    @PKG@.ShStore.log(u + " " + k + " " + @PKG@.ShKind.KEYS[kd] + " LINK done " + line.substring(0, bar < 0 ? line.length() : bar) + " moved " + moved + " back " + backN + " accepted " + acc + " credit " + cred + (xkey != null ? " xp to " + xkey : ""));
    MOVED.addAndGet(moved);
    BACK.addAndGet(backN);
    RESOLVED.incrementAndGet();
    return new Object[] { cred, xkey, Long.valueOf(moved) };
  } finally { @PKG@.ShStore.LOCK.unlock(); }
}""")
# a journal line left by an earlier (or just made) transfer: SkyySacks says what it took (put answer, else done) -> settle -> ack -> pay.
# Returns the items moved (>= 0), -1 = nothing pending, -2 = cannot tell yet (waits; tried again next time)
M(lnk, r"""
public static long resolve(java.util.UUID u, String k, int kd, java.util.Properties p, String acc) {
  String line;
  @PKG@.ShStore.LOCK.lock(); try { line = @PKG@.ShStore.str(p, pk(kd)); } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (line.length() == 0) return -1L;
  int bar = line.indexOf('|');
  String tk = bar < 0 ? line : line.substring(0, bar);
  String a = acc;
  if (a == null) {
    Object d = ask(new Object[] { "done", k, tk });
    if (!(d instanceof String)) return -2L;
    a = (String) d;
  }
  Object[] r = settle(u, k, kd, p, line, a);
  if (r == null) return -2L;
  ackDone(kd, p, tk, ask(new Object[] { "ack", k, tk }));   // FIX: kept in <kind>.linkack until SkyySacks answers
  java.util.Iterator it = ((java.util.LinkedHashMap) r[0]).keySet().iterator();
  while (it.hasNext()) { try { @PKG@.ShCore.owed(u, (String) it.next(), 0L); } catch (Throwable t) { } }   // the owed lines: paid now (or wait for the next Collect)
  if (r[1] != null) { try { @PKG@.ShCore.owedXp(u, @PKG@.ShKind.SKILL[kd], 0L); } catch (Throwable t) { } }
  return ((Long) r[2]).longValue();
}""")
M(lnk, r"""
public static String line(String k, int kd) {
  Object o = LINE.get(k + "|" + kd);
  return o == null ? null : (String) o;
}""")
# one shard of the OWNER (u on profile k): pending first, then a new transfer. Returns the items moved (0 = none). Never throws.
M(lnk, r"""
public static long run0(java.util.UUID u, String k, int kd) {
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return 0L;
  long r0 = resolve(u, k, kd, p, (String) null);
  if (r0 == -2L) return 0L;
  reAck(k, kd, p);   // FIX: acks SkyySacks did not confirm before (a lost answer / a restart)
  String ids;
  @PKG@.ShStore.LOCK.lock(); try {
    if (!@PKG@.ShMath.owned(kd, p) || @PKG@.ShStore.str(p, pk(kd)).length() > 0) return r0 > 0L ? r0 : 0L;
    ids = cands(kd, p);
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (@PKG@.ShIsl.lockMsg(u, kd) != null) return r0 > 0L ? r0 : 0L;
  Object ro = ask(new Object[] { "room", u, k, ids });
  String bk = k + "|" + kd;
  if (!(ro instanceof String)) return r0 > 0L ? r0 : 0L;
  String rs = (String) ro;
  int bar = rs.indexOf('|');
  if (rs.length() == 0 || bar < 0) { LINE.remove(bk); return r0 > 0L ? r0 : 0L; }
  java.util.HashMap room = new java.util.HashMap();
  java.util.HashMap idCat = new java.util.HashMap();
  String[] ra = rs.substring(0, bar).split(",");
  for (int j = 0; j < ra.length; j++) {
    int c = ra[j].lastIndexOf(':');
    if (c <= 0) continue;
    try { room.put(ra[j].substring(0, c), Long.valueOf(Long.parseLong(ra[j].substring(c + 1).trim()))); } catch (Throwable t) { }
  }
  java.util.TreeSet cats = new java.util.TreeSet();
  String[] ia = rs.substring(bar + 1).split(",");
  for (int j = 0; j < ia.length; j++) {
    int c = ia[j].indexOf('=');
    if (c <= 0) continue;
    idCat.put(ia[j].substring(0, c), ia[j].substring(c + 1));
    cats.add(ia[j].substring(c + 1));
  }
  if (cats.isEmpty()) { LINE.remove(bk); return r0 > 0L ? r0 : 0L; }
  StringBuilder cn = new StringBuilder();
  java.util.Iterator ci = cats.iterator();
  while (ci.hasNext()) { if (cn.length() > 0) cn.append(", "); cn.append((String) ci.next()); }
  RUNS.incrementAndGet();
  boolean[] full = new boolean[1];
  String tk = tok(kd);
  @PKG@.ShTotem.moonBlade(k);   // FIX (critic): warm the Moon Blade cache outside ShStore.LOCK (take settles; settle reads only the cache)
  String line = take(u, k, kd, p, room, idCat, tk, full);
  LINE.put(bk, "Linked to pocket (" + cn + ")" + (full[0] ? " - it is full: the rest waits here (Collect all)." : ": new items go straight there."));
  if (line == null || line.length() == 0) return r0 > 0L ? r0 : 0L;
  StringBuilder it = new StringBuilder();
  java.util.LinkedHashMap sum = new java.util.LinkedHashMap();
  String[] es = line.substring(line.indexOf('|') + 1).split(";");
  for (int x = 0; x < es.length; x++) {
    String[] e = es[x].split(",");
    if (e.length >= 4) addL(sum, e[2], Long.parseLong(e[3]));
  }
  java.util.Iterator si = sum.entrySet().iterator();
  while (si.hasNext()) { java.util.Map.Entry se = (java.util.Map.Entry) si.next(); if (it.length() > 0) it.append(','); it.append((String) se.getKey()).append(':').append(((Long) se.getValue()).longValue()); }
  Object pr = ask(new Object[] { "put", u, k, tk, it.toString() });
  long r1 = resolve(u, k, kd, p, (pr instanceof String) ? (String) pr : (String) null);
  return (r0 > 0L ? r0 : 0L) + (r1 > 0L ? r1 : 0L);
}""")
M(lnk, r"""
public static long run(java.util.UUID u, String k, int kd) {
  if (!@PKG@.ShCfg.ON || u == null || k == null || !@PKG@.ShKind.ok(kd)) return 0L;
  if (!k.equals(@PKG@.ShCfg.pkey(u)) || @PKG@.ShCore.busy(u)) return 0L;   // the owner, on the profile that owns the shard
  String bk = k + "|" + kd;
  if (fn() == null) { LINE.remove(bk); return 0L; }   // FIX (critic): SkyySacks gone - no "Linked to pocket" line
  if (BUSY.putIfAbsent(bk, Boolean.TRUE) != null) return 0L;
  try { return run0(u, k, kd); }
  catch (Throwable t) { if (!(t instanceof @PKG@.ShBusy)) @PKG@.ShCfg.warnOnce("linkrun", "Shard Link failed (logged once; the items stay in the shard): " + t); return 0L; }
  finally { BUSY.remove(bk); }
}""")
# the clicker page (every redraw - a chop redraws it): at most once per PAGE_MS a shard (the tick does the rest)
M(lnk, r"""
public static long page(java.util.UUID u, String k, int kd) {
  if (u == null || k == null) return 0L;
  long now = System.currentTimeMillis();
  String bk = k + "|" + kd;
  Object o = LAST.get(bk);
  if (o instanceof Long && now - ((Long) o).longValue() < PAGE_MS && now >= ((Long) o).longValue()) return 0L;
  LAST.put(bk, Long.valueOf(now));
  return run(u, k, kd);
}""")
# the tick: every online player, every shard they own - a profile with no link on is skipped after one cheap "state" question
M(lnk, r"""
public static long tickOne(java.util.UUID u) {
  if (u == null || fn() == null || @PKG@.ShCore.busy(u)) return 0L;
  String k = @PKG@.ShCfg.pkey(u);
  Object st = ask(new Object[] { "state", k });
  if (!(st instanceof String)) return 0L;
  if (((String) st).length() == 0) {   // no link on: only a transfer left half way is finished
    long z = 0L;
    for (int kd = 0; kd < @PKG@.ShKind.N; kd++) {
      LINE.remove(k + "|" + kd);
      java.util.Properties p = null;
      try { p = @PKG@.ShStore.get(k); } catch (Throwable t) { p = null; }
      if (p != null && (@PKG@.ShStore.str(p, pk(kd)).length() > 0 || @PKG@.ShStore.str(p, ak(kd)).length() > 0)) z += run(u, k, kd);
    }
    return z;
  }
  long m = 0L;
  for (int kd = 0; kd < @PKG@.ShKind.N; kd++) m += run(u, k, kd);
  return m;
}""")
M(lnk, r"""
public static void tickAll() {
  try {
    java.util.Iterator it = @UNI@.get().getPlayers().iterator();
    while (it.hasNext()) {
      @PR@ pr = (@PR@) it.next();
      if (pr == null || !pr.isValid()) continue;
      try { tickOne(pr.getUuid()); } catch (Throwable t) { }
    }
  } catch (Throwable t) { @PKG@.ShCfg.warnOnce("linktick", "the Shard Link tick failed (logged once): " + t); }
}""")
'''
P.rep('''M(core, r"""
public static String collect0(java.util.UUID u, String k, int kd, int slot, @IC@[] cs, String only) {   // 0.4.23: the chopped drops first, then the 0.4.22 Collect
  String h = collectHeld(u, k, kd, slot, cs, only);''', LINK + '''M(core, r"""
public static String collect0(java.util.UUID u, String k, int kd, int slot, @IC@[] cs, String only) {   // 0.4.23: the chopped drops first, then the 0.4.22 Collect
  if (slot < 0 && only == null) @PKG@.ShLink.run(u, k, kd);   // 0.4.33: Collect all - the Shard Link first (the pocket takes what fits), then the rest
  String h = collectHeld(u, k, kd, slot, cs, only);''')

# ---------------------------------------------------------------------------------------------------- 2. the tick + the page
P.rep('''    if (this.n % 5L == 0L) @PKG@.ShLv20.scan();   // 0.4.6: the level 20 shards (every 5 s; a join is caught within 5 s)
''', '''    if (this.n % 5L == 0L) @PKG@.ShLv20.scan();   // 0.4.6: the level 20 shards (every 5 s; a join is caught within 5 s)
    if (@PKG@.ShLink.TICK_SEC > 0 && this.n % (long) @PKG@.ShLink.TICK_SEC == 0L) @PKG@.ShLink.tickAll();   // 0.4.33: Shard Link (our thread)
''')
P.rep('''  else if (this.view == 5) {   // 0.4.27: ckPre (purse + bags, before any lock) / ckPost (the spirit, Smithy I, cost lines, coins, the upgrades view)
    ckPre(cs);
''', '''  else if (this.view == 5) {   // 0.4.27: ckPre (purse + bags, before any lock) / ckPost (the spirit, Smithy I, cost lines, coins, the upgrades view)
    if (k != null) @PKG@.ShLink.page(this.me, k, this.kind);   // 0.4.33: Shard Link - the page shows what is left (the owner only; at most every 5 s; never throws)
    ckPre(cs);
''')
P.rep('''  if (this.ckCoins > 0L) this.sgHint = @PKG@.ShCfg.num(this.ckCoins) + " coins waiting - Collect all pays them";
  else if (kd == @PKG@.ShClk.TK && @PKG@.ShCfg.TF_COINS && @PKG@.ShCfg.fn("mob:fn:killCoins") == null) this.sgHint = this.sgHint + " (no kill coins: needs SkyyMobs 0.1.26+)";
''', '''  if (this.ckCoins > 0L) this.sgHint = @PKG@.ShCfg.num(this.ckCoins) + " coins waiting - Collect all pays them";
  else if (kd == @PKG@.ShClk.TK && @PKG@.ShCfg.TF_COINS && @PKG@.ShCfg.fn("mob:fn:killCoins") == null) this.sgHint = this.sgHint + " (no kill coins: needs SkyyMobs 0.1.26+)";
  String lnk0 = k == null ? null : @PKG@.ShLink.line(k, kd);   // 0.4.33: Shard Link on for this shard's items
  if (lnk0 != null && this.manage) this.sgHint = this.ckCoins > 0L ? lnk0 + " " + @PKG@.ShCfg.num(this.ckCoins) + " coins wait for Collect all." : lnk0;
''')

# ---------------------------------------------------------------------------------------------------- 3. classes written + the ready line
P.rep('''ALLC = ALLC + [smig427]   # 0.4.27: ShMig0427
''', '''ALLC = ALLC + [smig427]   # 0.4.27: ShMig0427
ALLC = ALLC + [lnk]   # 0.4.33: ShLink
''')
P.rep(r'''log("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.32:''', r'''log("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.33: Shard Link (a pocket with the SkyySacks Shard Link upgrade takes this shard's items straight in, no Collect - " + (@PKG@.ShLink.fn() != null ? "SkyySacks sacks:fn:link seen" : "no sacks:fn:link yet: items wait for Collect") + "); 0.4.32:''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0, "command / system registrations changed"
assert P.s.index('lnk = mk("ShLink")') < P.s.index("public static String collect0(java.util.UUID u, String k, int kd, int slot, @IC@[] cs, String only)") \
    < P.s.index("@PKG@.ShLink.tickAll();") and P.s.index('lnk = mk("ShLink")') > P.s.index("public static String oreOfBar(String id)"), "0.4.33: ShLink after owedAs / oreOfBar, before collect0"
P.finish()
