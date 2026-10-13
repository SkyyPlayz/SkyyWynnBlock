"""Derive SkyyAuctions/build_skyyauctions_0.1.4.py from the GENERATED 0.1.3 script (the SET pin; 0.1.3 and every older script stay untouched):
    python tools/auctions_0_1_4_patch.py
    python SkyyAuctions/build_skyyauctions_0.1.4.py          (must end 'assembled ...SkyyAuctions-0.1.4.jar')
    python SkyyAuctions/test_skyyauctions_0.1.4.py           (harness)
Edit THIS patch, never the generated script.

0.1.4 (2026-10-13) = LAG FIXES from the code audit (research/Code-Structure-Audit.md finding #15 + pack-wide pattern 1; Skyy 2026-10-13:
"During/ before we consolidate the mods together, lets audit the code structure, and make sure they are working together in the smoothest
easiest lag free way possible"). No listing / buy / claim / coin / page / file change:
 A. LOCK-FREE BRIDGE: AhUtil.bridge() caches the skyy.bridge map in the static volatile AhUtil.BRIDGE; only the first call takes the
    System.class monitor (bridge0 creates the map exactly as before).
 B. AhTick (every 10 s, the shared scheduler) no longer walks EVERY open listing (BSON reads) once per online player plus once for the
    count. A new index class AhIdx is updated wherever a record enters or leaves LIVE (AhStore.livePut / liveRemove / load's clear - i.e.
    inside commit / commitForced / swap0 and the other LIVE writers, all under the AhStore lock):
    - OWED: profile key -> claims owed = exactly owedFor(key)[0] (rowsFor's rules: a not-closed, not read-only record gives its seller
      key 1 for SOLD + sellerCoins OWED or sellerItem OWED, its buyer key 1 for buyerItem OWED, ONE row when seller key = buyer key).
      publishClaims (auction:claims:<uuid>) reads it: one map lookup per player.
    - ACTIVE (an AtomicInteger) + each active record's endsAt: countActive(now) (auction:count, /ahadmin) = ACTIVE while now is below the
      earliest end of any counted listing; past it (a listing just ended and the tick has not expired it yet, or an expiry write failed)
      one scan of the active ids (not of the BSON records) recomputes the count and the next earliest end - the same number active(now)
      gives (buyable: not read-only, state ACTIVE, now < endsAt).
    owedFor (claims + coins + items for the pages and the join notice) and active(now) (Browse) still scan on demand, as in 0.1.3.
 C. FIX ROUND (critic finding, 2026-10-13): SkyyCoins 0.1.6 writes purses behind (<= 1 s). Coins.take / Coins.add call coins:fn:flush
    (when SkyyCoins offers it) right after a SUCCESSFUL take / add, so a listing fee / purchase price is on disk in the purse file before
    the listing / SOLD record (seller's coins OWED) is written, and a claimed payout right after the claim. A hard crash can no longer
    leave a buyer's coins in the purse file AND the seller's owed coins in the record. A refused / thrown call is never flushed.
Rolling back to 0.1.3 is safe (no data change).
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyAuctions", "build_skyyauctions_0.1.3.py")
dst = os.path.join(ROOT, "SkyyAuctions", "build_skyyauctions_0.1.4.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
assert 'VERSION = "0.1.3"' in s and "AhIdx" not in s, "the source must be the generated 0.1.3 script"


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:160])
    s = s.replace(old, new)


rep('VERSION = "0.1.3"', 'VERSION = "0.1.4"')
s = ('"""0.1.4 (2026-10-13): lag fixes from the code audit - lock-free bridge(); an owed-claims index per profile key + an active-listing\n'
     '  counter (AhIdx, updated where records enter / leave LIVE) so the 10 s tick no longer scans every listing per online player.\n'
     '  Notes in tools/auctions_0_1_4_patch.py.\n' + s[3:])

# ---- A: lock-free bridge
rep('''M(utl, r"""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) { return bridge0(); }
}""")''', '''# 0.1.4 A: lock-free bridge (research/Code-Structure-Audit.md): BRIDGE caches the map; only the first call takes the System.class monitor
F(utl, "public static volatile java.util.Map BRIDGE;")
M(utl, r"""
public static java.util.Map bridge() {
  java.util.Map m = BRIDGE;
  if (m != null) return m;
  synchronized (java.lang.System.class) { m = bridge0(); }
  BRIDGE = m;
  return m;
}""")''')

# ---- B: the index class (compiled before AhStore's LIVE writers)
rep('''sto  = pool.makeClass(PKG + ".AhStore")
''', '''sto  = pool.makeClass(PKG + ".AhStore")
idx  = pool.makeClass(PKG + ".AhIdx")         # 0.1.4: owed-claims per profile key + the active-listing count
''')
rep('''# swap the new version into memory. A closed record leaves LIVE''', '''# ================= 0.1.4 B: AhIdx - kept in step with LIVE by AhStore.livePut / liveRemove / liveClear (all under the AhStore lock).
# OWN: id -> String[] the profile keys this record gives one owed claim (rowsFor's rules); OWED: key -> Integer claims (lock-free reads);
# ACT: id -> Long endsAt of a record buyable() would count (ignoring the time); ACTIVE = ACT.size() as an AtomicInteger; MINEND = the
# earliest endsAt in ACT (Long.MIN_VALUE = some counted record already ended: scan until it leaves LIVE). Own monitor (AhIdx.class).
F(idx, "public static final java.util.HashMap OWN = new java.util.HashMap();")
F(idx, "public static final java.util.HashMap ACT = new java.util.HashMap();")
F(idx, "public static final java.util.concurrent.ConcurrentHashMap OWED = new java.util.concurrent.ConcurrentHashMap();")
F(idx, "public static final java.util.concurrent.atomic.AtomicInteger ACTIVE = new java.util.concurrent.atomic.AtomicInteger(0);")
F(idx, "public static long MINEND = Long.MAX_VALUE;")
F(idx, "public static long SCANS = 0L;")
# the keys a record gives one owed claim - owedFor(key)[0] counts exactly these (rowsFor: closed and read-only records give none)
M(idx, r"""
public static String[] keysOf(@BD@ r) {
  if (r == null || @PKG@.AhRec.bool(r, "closed", false) || @PKG@.AhRec.readOnly(r)) return new String[0];
  String sk = @PKG@.AhRec.subStr(r, "seller", "key", "");
  String bk = @PKG@.AhRec.subStr(r, "buyer", "key", "");
  boolean sRow = ("SOLD".equals(@PKG@.AhRec.state(r)) && "OWED".equals(@PKG@.AhRec.claim(r, "sellerCoins"))) || "OWED".equals(@PKG@.AhRec.claim(r, "sellerItem"));
  boolean bRow = "OWED".equals(@PKG@.AhRec.claim(r, "buyerItem"));
  if (sk.equals(bk)) return (sRow || bRow) ? new String[] { sk } : new String[0];
  if (sRow && bRow) return new String[] { sk, bk };
  if (sRow) return new String[] { sk };
  if (bRow) return new String[] { bk };
  return new String[0];
}""")
# buyable(r, now) without the time part: not read-only and state ACTIVE
M(idx, r"""
public static boolean actOf(@BD@ r) {
  return r != null && !@PKG@.AhRec.readOnly(r) && "ACTIVE".equals(@PKG@.AhRec.state(r));
}""")
M(idx, r"""
public static void bump(String k, int d) {
  Object v = OWED.get(k);
  int n = (v instanceof Integer ? ((Integer) v).intValue() : 0) + d;
  if (n <= 0) OWED.remove(k); else OWED.put(k, Integer.valueOf(n));
}""")
# r == null = the record left LIVE
M(idx, r"""
public static synchronized void put(String id, @BD@ r) {
  String[] old = (String[]) OWN.remove(id);
  if (old != null) { for (int i = 0; i < old.length; i++) bump(old[i], -1); }
  if (ACT.remove(id) != null) ACTIVE.decrementAndGet();
  if (r == null) return;
  String[] ks = keysOf(r);
  if (ks.length > 0) {
    OWN.put(id, ks);
    for (int i = 0; i < ks.length; i++) bump(ks[i], 1);
  }
  if (actOf(r)) {
    long e = @PKG@.AhRec.lng(r, "endsAt", 0L);
    ACT.put(id, Long.valueOf(e));
    ACTIVE.incrementAndGet();
    if (e < MINEND) MINEND = e;
  }
}""")
M(idx, r"""
public static synchronized void clear() {
  OWN.clear(); ACT.clear(); OWED.clear();
  ACTIVE.set(0);
  MINEND = Long.MAX_VALUE;
}""")
M(idx, r"""
public static int owed(String key) {
  if (key == null) return 0;
  Object v = OWED.get(key);
  return v instanceof Integer ? ((Integer) v).intValue() : 0;
}""")
# = active(now).size(): ACTIVE while now is below every counted end, else one scan of ACT (ids only, no BSON)
M(idx, r"""
public static synchronized int countActive(long now) {
  if (now < MINEND) return ACTIVE.get();
  SCANS = SCANS + 1L;
  int n = 0;
  long min = Long.MAX_VALUE;
  java.util.Iterator it = ACT.values().iterator();
  while (it.hasNext()) {
    long e = ((Long) it.next()).longValue();
    if (now < e) { n++; if (e < min) min = e; }
  }
  MINEND = n < ACT.size() ? Long.MIN_VALUE : min;
  return n;
}""")
# 0.1.4 B: every LIVE write goes through these (the index follows LIVE)
M(sto, r"""
public static void livePut(String id, @BD@ r) {
  LIVE.put(id, r);
  @PKG@.AhIdx.put(id, r);
}""")
M(sto, r"""
public static void liveRemove(String id) {
  LIVE.remove(id);
  @PKG@.AhIdx.put(id, null);
}""")
# swap the new version into memory. A closed record leaves LIVE''')
rep('''  if (@PKG@.AhRec.bool(r, "closed", false)) {
    LIVE.remove(id);
    if (onDisk) { if (archiveMove(r)) ARCH.remove(id); else ARCH.put(id, r); }
    else ARCH.put(id, r);
  } else LIVE.put(id, r);''', '''  if (@PKG@.AhRec.bool(r, "closed", false)) {
    liveRemove(id);
    if (onDisk) { if (archiveMove(r)) ARCH.remove(id); else ARCH.put(id, r); }
    else ARCH.put(id, r);
  } else livePut(id, r);''')
rep('''public static int countActive(long now) { return active(now).size(); }''',
    '''public static int countActive(long now) { return @PKG@.AhIdx.countActive(now); }''')
rep('''  LIVE.clear(); STACKS.clear(); DIRTY.clear(); ARCH.clear();''',
    '''  LIVE.clear(); STACKS.clear(); DIRTY.clear(); ARCH.clear();
  @PKG@.AhIdx.clear();''')
rep('''      if (@PKG@.AhRec.bool(r, "closed", false)) { if (!archiveMove(r)) ARCH.put(id, r); continue; }
      LIVE.put(id, r);''', '''      if (@PKG@.AhRec.bool(r, "closed", false)) { if (!archiveMove(r)) ARCH.put(id, r); continue; }
      livePut(id, r);''')
rep('''  LIVE.put(id, r);
  @PKG@.AhLog.log("LIST", id,''', '''  livePut(id, r);
  @PKG@.AhLog.log("LIST", id,''')
rep('''  if (!write(next)) return new @RES@(false, "Could not write #" + id + " - nothing changed.");
  LIVE.put(id, next);''', '''  if (!write(next)) return new @RES@(false, "Could not write #" + id + " - nothing changed.");
  livePut(id, next);''')
rep('''  try { long[] o = owedFor(@PKG@.AhUtil.pkey(u)); @PKG@.AhUtil.bridge().put("auction:claims:" + u, Integer.valueOf((int) o[0])); } catch (Throwable t) { }''',
    '''  try { @PKG@.AhUtil.bridge().put("auction:claims:" + u, Integer.valueOf(@PKG@.AhIdx.owed(@PKG@.AhUtil.pkey(u)))); } catch (Throwable t) { }''')
# ---- C: coins:fn:flush after a successful take / add (fix round)
rep('''M(coin, r"""
public static int take(java.util.UUID u, long n) {''', '''# 0.1.4 C: SkyyCoins 0.1.6 writes purses behind; coins:fn:flush writes them NOW (absent = SkyyCoins 0.1.5, which writes at once). A
# failure only logs - SkyyCoins retries every second.
M(coin, r"""
public static void flush() {
  Object f = @PKG@.AhUtil.bridge().get("coins:fn:flush");
  if (!(f instanceof java.util.function.Function)) return;
  try {
    Object r = ((java.util.function.Function) f).apply(null);
    if (r instanceof Number && ((Number) r).intValue() < 0) @PKG@.AhUtil.warn("coins:fn:flush could not write the purse yet (SkyyCoins retries every second)");
  } catch (Throwable t) { @PKG@.AhUtil.warn("coins:fn:flush threw: " + t); }
}""")
M(coin, r"""
public static int take(java.util.UUID u, long n) {''')
rep('''  catch (Throwable t) { @PKG@.AhUtil.warn("coins:fn:take threw for " + u + " (" + n + " coins): " + t); return -1; }
  return (r instanceof Boolean && ((Boolean) r).booleanValue()) ? 1 : 0;''', '''  catch (Throwable t) { @PKG@.AhUtil.warn("coins:fn:take threw for " + u + " (" + n + " coins): " + t); return -1; }
  if (r instanceof Boolean && ((Boolean) r).booleanValue()) { flush(); return 1; }
  return 0;''')
rep('''  catch (Throwable t) { @PKG@.AhUtil.warn("coins:fn:add threw for " + u + " (" + n + " coins): " + t); return -1; }
  return r instanceof Number ? 1 : 0;''', '''  catch (Throwable t) { @PKG@.AhUtil.warn("coins:fn:add threw for " + u + " (" + n + " coins): " + t); return -1; }
  if (r instanceof Number) { flush(); return 1; }
  return 0;''')
rep('''ALL = [utl, cfg, lg, coin, rec, itm, res, srt, sto, lfn, page, fac, cmds]''',
    '''ALL = [utl, cfg, lg, coin, rec, itm, res, srt, idx, sto, lfn, page, fac, cmds]''')

import re as _re
_code = s.split('"""', 2)[2]
assert not _re.search(r"[^.a-zA-Z]LIVE\.(put|remove)\(", _code.replace("  LIVE.put(id, r);\n  @PKG@.AhIdx.put(id, r);", "").replace("  LIVE.remove(id);\n  @PKG@.AhIdx.put(id, null);", "")), "a LIVE write outside livePut / liveRemove"
assert "synchronized (java.lang.System.class) { return bridge0(); }" not in s
assert not os.path.exists(dst), dst + " already exists - delete it first (it is generated)"
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
