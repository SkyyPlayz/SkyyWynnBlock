"""Derive SkyySacks/build_skyysacks_0.8.17.py from the SET pin 0.8.16 (the GENERATED build_skyysacks_0.8.16.py; edit THIS file, then
regenerate: python tools/sacks_0_8_17_patch.py; never re-run sacks_0_8_16_patch.py on top of it). The chain: ... -> sacks_0_8_16_patch.py ->
0.8.16 (generated, the SET pin) -> this patch -> 0.8.17. Every anchor is asserted once; at the end every change is undone on a copy and
compared with 0.8.16 (nothing else changed). Line endings kept.
Run:  python tools/sacks_0_8_17_patch.py   then   python SkyySacks/build_skyysacks_0.8.17.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.8.17.py [--dir <folder inside tools/dev/scratch/>] [--keep]

0.8.17 = round sacks0817 (2026-10-16). Skyy (Fishing Bench screenshot: FILLET AND SELL says 'You carry no whole fish' while the fish are
in the Void): "it cant pull from the void" (docs/answered/skills.md). SkyyFishing 0.1.10 lists / sells / fillets the Void's weighed fish
through four new bridge keys; the contract is header PART A of tools/fishing_0_1_10_patch.py (+ the fishvoid critic's token round,
coordinator 2026-10-16) and is implemented here exactly:
  A. THE FISH KEYS (SackFn modes 14 / 15 / 16 / 17; world thread only - the same gates as sacks:fn:take: SackBridge.keyFor = the settled
     profile key (profile switch / busy / unreadable pool = paused), the player on this world thread, the Fishing category reachable):
     sacks:fn:fishList  {UUID u, String id} -> String[] the ACTIVE profile's Void fish of that id, oldest first, one per stored fish: the
                        weight entries ("grams,mm,catcher", oldest first) then "" for each plain fish (no weight). String[0] ONLY when the
                        Void is readable and truly holds none of that id; null whenever it cannot be read for that player now (paused,
                        no player on this thread, no Fishing category reachable, bad arguments, an id that is not a SkyyFishing whole fish).
     sacks:fn:fishTake  {UUID u, String id, String entry, String token} -> Long 1 = ONE fish with exactly that entry left the Void: count - 1,
                        that entry AND the token (the caller's op id) in ONE SackPool lock (SackPool.fishPickTok), owed on the refund
                        ledger like sacks:fn:take (OWED + LASTKEY, 60 s), and the pool file WRITTEN - the token in the same atomic write
                        (pool meta line "~fishtok" = "token@takeTime ...", kept 24 h, then pruned; "~fishcut" = t<newest pruned take time>)
                        - BEFORE it answers 1 (SackPool.saveOk = SackPool.save on this thread under SAVELOCK, true only when the file
                        really landed). A token already stored = 0 (idempotent: a replayed take never takes a second fish). The write
                        failed = undone in memory (fish + entry back at their place, token gone, nothing owed), answer 0. "" entry = a
                        plain fish. 0 = no such fish / paused / a bad entry (";") / a bad token. Token = 1..120 chars, no white space,
                        no '@' or ';'. The 3-argument form (no token) still works (no token stored).
     sacks:fn:fishTaken {UUID u, String token [, Long opTime]} -> Boolean TRUE = that take is on disk in the active profile's pool; FALSE =
                        definitely not (no such token, and opTime is newer than every pruned token - or no token was ever pruned when
                        opTime is not given); null = cannot tell now (paused / profile switching / no player on this thread / pool
                        unreadable / bad token / opTime at or before the prune cut). Ask only about the ACTIVE profile's ops (the
                        caller's op file names its profile key).
     sacks:fn:fishPut   {UUID u, String id, String entry, String token} -> Long 1 = that fish is back (count + 1 and the entry, at the
                        oldest end) AND its token cleared (so fishTaken reads FALSE afterwards) in the same write, only while a take of
                        that id still owes exactly that entry (FOWE, 60 s, like sacks:fn:put) and - with a token - that very take carried
                        it (FTOK); a put can never create a fish or change its weight. Written before it answers 1, back into the exact
                        pool the take left (refundKey / LASTKEY). Without the token argument the token of that entry's newest owed take is
                        cleared. The write failed = taken out again (token stored again) and still owed, answer 0 (the caller gives the
                        fish another way - SkyyFishing rebuilds it into the inventory + commits: no dupe).
     sacks:fn:commit    (unchanged key) {UUID, id, 1L} finalises: the entry leaves the ledger with the count (oldest owed first); the
                        token stays on disk (the take stands) until the 24 h prune.
  B. THE 0.8.10 GAP CLOSED: a plain sacks:fn:take of a SkyyFishing fish (SackBridge.take -> SackPool.fishDebit) now takes the weight
     entries WITH the count in the same lock - one entry per fish taken, oldest first, then plain fish once the entries run out - and
     books them on the ledger (FOWE); sacks:fn:put gives exactly those entries back (newest-taken first, each at the oldest end = the list
     is as before the take); sacks:fn:commit drops them. So the count and the entries never drift (was: the entries stayed behind until
     the next move trimmed the oldest - SackBridge.debit is no longer used for fish). Other items: take / put / commit unchanged.
  C. CRASH WINDOWS (memory ledger, like 0.7.13): the pool file (fish, entry, token) is written before fishTake / fishPut answer 1, so after
     any crash fishTaken(token) tells the caller's replay exactly whether its take reached the disk (TRUE = pay, FALSE = nothing left the
     Void), and a replayed fishTake with that token answers 0. A plain take keeps 0.7.13's rule (saveSoon; the Bazaar's own pattern).
  Saved data: two new pool meta lines ("~fishtok", "~fishcut"; 0.8.10+ keeps every "~" line) next to the 0.8.10 "~fish:<id>" line; no
  command / system / class added; four bridge keys added (never removed, like every sacks:fn key). ROLLBACK to 0.8.16: safe (the keys vanish = SkyyFishing 0.1.10's bench lists the inventory only again and its
  hint counts the Void fish; same pool files).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G   # only its generic Patch helper (anchors asserted once, undo-compare, line endings kept)

P = G.Patch(os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.16.py"), os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.17.py"))
assert P.has('VERSION = "0.8.16"\n') and P.has("PopupHide") and not P.has("fishPick"), "not the live generated SkyySacks 0.8.16"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.8.17 = round sacks0817"):].rstrip() + "\n"

# ================================================================================================ header, version
P.rep('''popup shows again after the next server start - the GameplayConfig field is only changed in memory).
"""
''', '''popup shows again after the next server start - the GameplayConfig field is only changed in memory).
''' + NOTE + '''"""
''')
P.rep('VERSION = "0.8.16"\n', 'VERSION = "0.8.17"\n')

# ================================================================================================ SackPool: one-lock fish moves + a checked write
P.rep('''public static synchronized void fishBack(String k, String id, String e) {
  java.util.ArrayList l = fishFit(k, id);
  add(k, id, 1L);
  if (e == null || e.length() == 0) return;
  l.add(e);
  fishSet(k, id, l);
}\'\'\'), sp))
''', '''public static synchronized void fishBack(String k, String id, String e) {
  java.util.ArrayList l = fishFit(k, id);
  add(k, id, 1L);
  if (e == null || e.length() == 0) return;
  l.add(e);
  fishSet(k, id, l);
}\'\'\'), sp))
# 0.8.17 (tools/sacks_0_8_17_patch.py A / B): a fish back at entry position `at` (a failed write's undo: exactly where it was);
# fishFront = position 0, the OLDEST end - where the bridge takes found it (a refund)
sp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static synchronized void fishAt(String k, String id, String e, int at) {
  java.util.ArrayList l = fishFit(k, id);
  add(k, id, 1L);
  if (e == null || e.length() == 0) return;
  int i = at < 0 ? 0 : (at > l.size() ? l.size() : at);
  l.add(i, e);
  fishSet(k, id, l);
}\'\'\'), sp))
sp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static void fishFront(String k, String id, String e) { fishAt(k, id, e, 0); }\'\'\'), sp))
# sacks:fn:fishList's view: the entries oldest first, then "" for each plain fish (count beyond the entries)
sp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static synchronized String[] fishView(String k, String id) {
  java.util.ArrayList l = fishFit(k, id);
  long c = get(k, id);
  if (c < (long) l.size()) c = (long) l.size();
  if (c > 100000L) c = 100000L;
  String[] o = new String[(int) c];
  for (int i = 0; i < o.length; i++) o[i] = i < l.size() ? (String) l.get(i) : "";
  return o;
}\'\'\'), sp))
# sacks:fn:fishTake's move: exactly that fish (count - 1 and that entry, one lock); "" = a plain fish; false = none such
sp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static synchronized boolean fishPick(String k, String id, String e) {
  if (e == null || get(k, id) <= 0L) return false;
  java.util.ArrayList l = fishFit(k, id);
  if (e.length() == 0) {
    if (get(k, id) <= (long) l.size()) return false;
    add(k, id, -1L);
    return true;
  }
  int i = l.indexOf(e);
  if (i < 0) return false;
  l.remove(i);
  fishSet(k, id, l);
  add(k, id, -1L);
  return true;
}\'\'\'), sp))
# a plain sacks:fn:take of whole fish: up to n leave WITH their entries (oldest first, "" once the entries run out) -> out; one lock
sp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static synchronized long fishDebit(String k, String id, long n, java.util.ArrayList out) {
  long have = get(k, id);
  long t = n < have ? n : have;
  if (t <= 0L) return 0L;
  java.util.ArrayList l = fishFit(k, id);
  int m = 0;
  for (long i = 0L; i < t; i++) {
    if (!l.isEmpty()) { out.add(l.remove(0)); m++; }
    else out.add("");
  }
  if (m > 0) fishSet(k, id, l);
  add(k, id, -t);
  return t;
}\'\'\'), sp))
# the pool file of k written NOW on this thread; true only when it really was (saveNow counts SAVES only after the atomic move)
sp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static boolean saveOk0(String k) {
  long b = SAVES.get();
  saveNow(k);
  return SAVES.get() > b;
}\'\'\'), sp))
sp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static boolean saveOk(String k) {
  synchronized (SAVELOCK) { return saveOk0(k); }
}\'\'\'), sp))
# 0.8.17 token round (coordinator 2026-10-16): "~fishtok" = "token@takeTime ..." (the fishTake op ids of this pool, kept TOK_MS, written in
# the SAME atomic pool write as the take), "~fishcut" = "t<newest pruned take time>" (fishTaken can say FALSE only for ops after it)
sp.addField(CtField.make("public static final long TOK_MS = 86400000L;", sp))
sp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static boolean tokOk(String t) {
  if (t == null || t.length() == 0 || t.length() > 120) return false;
  for (int i = 0; i < t.length(); i++) {
    char c = t.charAt(i);
    if (c <= ' ' || c == '@' || c == ';' || c == (char) 127) return false;
  }
  return true;
}\'\'\'), sp))
sp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static synchronized String tokRaw(String k) {
  pool(k);
  java.util.Map mt = (java.util.Map) PMETA.get(k);
  Object v = mt == null ? null : mt.get("~fishtok");
  return v == null ? "" : String.valueOf(v).trim();
}\'\'\'), sp))
sp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static synchronized boolean tokHas(String k, String t) {
  if (t == null || t.length() == 0) return false;
  String[] a = tokRaw(k).split(" ");
  for (int i = 0; i < a.length; i++) {
    int at = a[i].lastIndexOf('@');
    String n = at < 0 ? a[i] : a[i].substring(0, at);
    if (n.length() > 0 && n.equals(t)) return true;
  }
  return false;
}\'\'\'), sp))
# unreadable cut = Long.MAX_VALUE (an unknown token is then never "definitely not taken")
sp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static synchronized long tokCut(String k) {
  pool(k);
  java.util.Map mt = (java.util.Map) PMETA.get(k);
  Object v = mt == null ? null : mt.get("~fishcut");
  if (v == null) return 0L;
  String c = String.valueOf(v).trim();
  if (c.startsWith("t")) c = c.substring(1);
  try { return Long.parseLong(c); } catch (Throwable x) { return Long.MAX_VALUE; }
}\'\'\'), sp))
# rewrite the token list: drop one `del` (null = none), add `add` at `now` (null = none), prune those older than TOK_MS (the cut grows;
# an unreadable time = pruned with cut MAX - never a wrong FALSE)
sp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static synchronized void tokSet(String k, String del, String add, long now) {
  String[] a = tokRaw(k).split(" ");
  StringBuilder sb = new StringBuilder();
  long cut = tokCut(k);
  boolean cutCh = false;
  boolean dropped = false;
  for (int i = 0; i < a.length; i++) {
    if (a[i].length() == 0) continue;
    int at = a[i].lastIndexOf('@');
    String n = at < 0 ? a[i] : a[i].substring(0, at);
    long tm = -1L;
    try { if (at >= 0) tm = Long.parseLong(a[i].substring(at + 1)); } catch (Throwable x) { tm = -1L; }
    if (del != null && !dropped && n.equals(del)) { dropped = true; continue; }
    if (tm < 0L) { cut = Long.MAX_VALUE; cutCh = true; continue; }
    if (now - tm > TOK_MS) {
      if (tm > cut) { cut = tm; cutCh = true; }
      continue;
    }
    if (sb.length() > 0) sb.append(' ');
    sb.append(n).append('@').append(tm);
  }
  if (add != null) {
    if (sb.length() > 0) sb.append(' ');
    sb.append(add).append('@').append(now);
  }
  java.util.concurrent.ConcurrentHashMap mt = (java.util.concurrent.ConcurrentHashMap) PMETA.get(k);
  if (mt == null) { mt = new java.util.concurrent.ConcurrentHashMap(); PMETA.put(k, mt); }
  if (sb.length() == 0) mt.remove("~fishtok"); else mt.put("~fishtok", sb.toString());
  if (cutCh) mt.put("~fishcut", "t" + cut);
  if (mt.isEmpty()) PMETA.remove(k);
  DIRTY.put(k, Boolean.TRUE);
}\'\'\'), sp))
# fishTake's move with its token, one lock: a token already stored = false (idempotent); tok null = no token
sp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static synchronized boolean fishPickTok(String k, String id, String e, String tok, long now) {
  if (tok != null && tokHas(k, tok)) return false;
  if (!fishPick(k, id, e)) return false;
  if (tok != null) tokSet(k, (String) null, tok, now);
  return true;
}\'\'\'), sp))
# a fish back at `at` and its token cleared, one lock (fishPut, a failed take's undo, a plain put of a tokened take)
sp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static synchronized void fishAtTok(String k, String id, String e, int at, String tok, long now) {
  fishAt(k, id, e, at);
  if (tok != null) tokSet(k, tok, (String) null, now);
}\'\'\'), sp))
''')

# ================================================================================================ SackBridge: the entry ledger
P.rep('''sbr.addField(CtField.make("public static final long OWE_MS = 60000L;", sbr))
''', '''sbr.addField(CtField.make("public static final long OWE_MS = 60000L;", sbr))
# 0.8.17: FOWE = "<key>|<fishId>" -> ArrayList of the entries the owed fish took (take order; "" = a plain fish) - always as long as OWED's
# amount for that key (SkyyFishing whole fish only; memory only, the same 60 s as OWED)
sbr.addField(CtField.make("public static final java.util.HashMap FOWE = new java.util.HashMap();", sbr))
# 0.8.17 token round: FTOK = "<key>|<fishId>|<entry>" -> ArrayList of the tokens of that entry's owed fishTakes (take order; memory only)
sbr.addField(CtField.make("public static final java.util.HashMap FTOK = new java.util.HashMap();", sbr))
''')
P.rep('''  if (o[0] <= 0L) OWED.remove(key);
  return t;
}"""), sbr))
sbr.addMethod(CtNewMethod.make(jt(r"""
public static long take(java.util.UUID u, String id, long n) {''', '''  if (o[0] <= 0L) OWED.remove(key);
  return t;
}"""), sbr))
# 0.8.17 token round: the FTOK helpers (all on SackBridge.class like OWED / FOWE)
sbr.addMethod(CtNewMethod.make(jt(r"""
public static synchronized void ftokClear(String kid) {
  java.util.ArrayList ks = new java.util.ArrayList(FTOK.keySet());
  for (int i = 0; i < ks.size(); i++) {
    String s = (String) ks.get(i);
    if (s.startsWith(kid + "|")) FTOK.remove(s);
  }
}"""), sbr))
sbr.addMethod(CtNewMethod.make(jt(r"""
public static synchronized void ftokPush(String fk, String tok) {
  if (tok == null) return;
  java.util.ArrayList l = (java.util.ArrayList) FTOK.get(fk);
  if (l == null) { l = new java.util.ArrayList(); FTOK.put(fk, l); }
  l.add(tok);
}"""), sbr))
# the token a put clears: tok given = it, only while an owed take of that entry carried it (else null = refuse); none given = the newest
# owed take's token ("" = that take had none)
sbr.addMethod(CtNewMethod.make(jt(r"""
public static synchronized String ftokFind(String fk, String tok) {
  java.util.ArrayList l = (java.util.ArrayList) FTOK.get(fk);
  if (tok != null) return (l != null && l.contains(tok)) ? tok : (String) null;
  if (l == null || l.isEmpty()) return "";
  return (String) l.get(l.size() - 1);
}"""), sbr))
sbr.addMethod(CtNewMethod.make(jt(r"""
public static synchronized void ftokDrop(String fk, String tok) {
  if (tok == null) return;
  java.util.ArrayList l = (java.util.ArrayList) FTOK.get(fk);
  if (l == null) return;
  l.remove((Object) tok);
  if (l.isEmpty()) FTOK.remove(fk);
}"""), sbr))
sbr.addMethod(CtNewMethod.make(jt(r"""
public static synchronized void ftokTidy(String kid) { if (!OWED.containsKey(kid)) ftokClear(kid); }"""), sbr))
# a commit: the oldest owed take of that entry is final (its token stays on disk until the 24 h prune)
sbr.addMethod(CtNewMethod.make(jt(r"""
public static synchronized void ftokPopOld(String fk) {
  java.util.ArrayList l = (java.util.ArrayList) FTOK.get(fk);
  if (l == null) return;
  if (!l.isEmpty()) l.remove(0);
  if (l.isEmpty()) FTOK.remove(fk);
}"""), sbr))
# 0.8.17: owe t of id; a whole fish also books the entries it took (es, padded with "" to t). Other items = owe.
sbr.addMethod(CtNewMethod.make(jt(r"""
public static synchronized void oweE(String k, String id, long t, java.util.ArrayList es, long now) {
  if (t <= 0L) return;
  if (!@PKG@.SackDefs.isCatch(id)) { owe(k, id, t, now); return; }
  String key = k + "|" + id;
  long[] o = (long[]) OWED.get(key);
  java.util.ArrayList l = (java.util.ArrayList) FOWE.get(key);
  boolean live = o != null && now - o[1] <= OWE_MS;
  if (!live || l == null) {
    if (!live) ftokClear(key);
    l = new java.util.ArrayList();
    long pad = live ? o[0] : 0L;
    for (long i = 0L; i < pad; i++) l.add("");
  }
  int m = es == null ? 0 : es.size();
  for (int i = 0; i < m && (long) i < t; i++) l.add(es.get(i));
  for (long i = (long) m; i < t; i++) l.add("");
  FOWE.put(key, l);
  owe(k, id, t, now);
}"""), sbr))
# 0.8.17: un-owe up to n of a whole fish -> the entries (lifo = a put: the newest taken first; else a commit: the oldest owed first)
sbr.addMethod(CtNewMethod.make(jt(r"""
public static synchronized java.util.ArrayList unoweE(String k, String id, long n, long now, boolean lifo) {
  java.util.ArrayList out = new java.util.ArrayList();
  String key = k + "|" + id;
  long t = unowe(k, id, n, now);
  java.util.ArrayList l = (java.util.ArrayList) FOWE.get(key);
  for (long i = 0L; i < t; i++) {
    if (l == null || l.isEmpty()) out.add("");
    else if (lifo) out.add(l.remove(l.size() - 1));
    else out.add(l.remove(0));
  }
  if (!OWED.containsKey(key)) FOWE.remove(key);   // FTOK: the caller reads the tokens first, then ftokTidy
  return out;
}"""), sbr))
# 0.8.17: sacks:fn:fishPut's ledger check - exactly that entry is still owed (taken in the last OWE_MS, not committed / put back)
sbr.addMethod(CtNewMethod.make(jt(r"""
public static synchronized boolean fishUnowe(String k, String id, String e, long now) {
  String key = k + "|" + id;
  long[] o = (long[]) OWED.get(key);
  if (o == null) { FOWE.remove(key); ftokClear(key); return false; }
  if (now - o[1] > OWE_MS) { OWED.remove(key); FOWE.remove(key); ftokClear(key); return false; }
  java.util.ArrayList l = (java.util.ArrayList) FOWE.get(key);
  if (l == null || o[0] <= 0L) return false;
  int i = l.lastIndexOf(e);
  if (i < 0) return false;
  l.remove(i);
  o[0] = o[0] - 1L;
  if (o[0] <= 0L) { OWED.remove(key); FOWE.remove(key); ftokClear(key); }
  return true;
}"""), sbr))
sbr.addMethod(CtNewMethod.make(jt(r"""
public static long take(java.util.UUID u, String id, long n) {''')
# take: a whole fish leaves WITH its entries (B)
P.rep('''  @PKG@.BagMirror.beforeTake(k);   // live-mirror rule: book what a bench / pocket craft already took BEFORE the pool is read
  long t = debit(k, id, n);
  if (t <= 0L) return 0L;
  // from here on the items are gone from the pool: every later step is caught on its own so the caller always learns the real amount
  try { @PKG@.BagMirror.afterTake(k, id); } catch (Throwable t1) { @PKG@.SackPool.warn("bag bridge: mirror trim failed after a take: " + t1); }
  try { LASTKEY.put(u.toString() + "|" + id, k); owe(k, id, t, System.currentTimeMillis()); } catch (Throwable t2) { }''',
      '''  @PKG@.BagMirror.beforeTake(k);   // live-mirror rule: book what a bench / pocket craft already took BEFORE the pool is read
  java.util.ArrayList fe = new java.util.ArrayList();   // 0.8.17 (B): a whole fish takes its weight entries with it, in the same lock
  long t = @PKG@.SackDefs.isCatch(id) ? @PKG@.SackPool.fishDebit(k, id, n, fe) : debit(k, id, n);
  if (t <= 0L) return 0L;
  // from here on the items are gone from the pool: every later step is caught on its own so the caller always learns the real amount
  try { @PKG@.BagMirror.afterTake(k, id); } catch (Throwable t1) { @PKG@.SackPool.warn("bag bridge: mirror trim failed after a take: " + t1); }
  try { LASTKEY.put(u.toString() + "|" + id, k); oweE(k, id, t, fe, System.currentTimeMillis()); } catch (Throwable t2) { }''')
# commit: the fish entries leave the ledger with the count
P.rep('''  String k = (String) LASTKEY.get(u.toString() + "|" + id);
  if (k == null) k = @PKG@.SackPool.settledKey(u);
  if (k == null) return 0L;
  return unowe(k, id, n, System.currentTimeMillis());
}"""), sbr))''', '''  String k = (String) LASTKEY.get(u.toString() + "|" + id);
  if (k == null) k = @PKG@.SackPool.settledKey(u);
  if (k == null) return 0L;
  if (@PKG@.SackDefs.isCatch(id)) {   // 0.8.17: the entries (and their fishTake tokens, oldest first) leave the ledger
    java.util.ArrayList ce = unoweE(k, id, n, System.currentTimeMillis(), false);
    for (int i = 0; i < ce.size(); i++) ftokPopOld(k + "|" + id + "|" + (String) ce.get(i));
    ftokTidy(k + "|" + id);
    return (long) ce.size();
  }
  return unowe(k, id, n, System.currentTimeMillis());
}"""), sbr))''')
# put: a whole fish comes back with exactly the entries its take took
P.rep('''  long t = unowe(k, id, n, System.currentTimeMillis());
  if (t <= 0L) return 0L;
  @PKG@.SackPool.add(k, id, t);
  try { @PKG@.CraftLog.later(k, "BAG-RETURN " + id + " " + t + " (sacks:fn:put)"); } catch (Throwable t3) { }
  try { @PKG@.SackPool.saveSoon(k); } catch (Throwable t4) { @PKG@.SackPool.DIRTY.put(k, Boolean.TRUE); }
  return t;
}"""), sbr))
''', '''  long t = 0L;
  if (@PKG@.SackDefs.isCatch(id)) {   // 0.8.17 (B): the entries the take took go back with the count (newest taken first, at the oldest end)
    long pn = System.currentTimeMillis();
    java.util.ArrayList fe = unoweE(k, id, n, pn, true);
    for (int i = 0; i < fe.size(); i++) {   // a fish a fishTake took comes back with its token cleared (fishTaken reads FALSE again)
      String pe = (String) fe.get(i);
      String pt = ftokFind(k + "|" + id + "|" + pe, (String) null);
      String ptn = pt.length() == 0 ? (String) null : pt;
      @PKG@.SackPool.fishAtTok(k, id, pe, 0, ptn, pn);
      ftokDrop(k + "|" + id + "|" + pe, ptn);
    }
    ftokTidy(k + "|" + id);
    t = (long) fe.size();
  } else {
    t = unowe(k, id, n, System.currentTimeMillis());
    if (t > 0L) @PKG@.SackPool.add(k, id, t);
  }
  if (t <= 0L) return 0L;
  try { @PKG@.CraftLog.later(k, "BAG-RETURN " + id + " " + t + " (sacks:fn:put)"); } catch (Throwable t3) { }
  try { @PKG@.SackPool.saveSoon(k); } catch (Throwable t4) { @PKG@.SackPool.DIRTY.put(k, Boolean.TRUE); }
  return t;
}"""), sbr))
# ================= 0.8.17 THE VOID'S WEIGHED FISH for SkyyFishing 0.1.10 (tools/sacks_0_8_17_patch.py A; world thread only) =================
sbr.addMethod(CtNewMethod.make(jt(r"""
public static String[] fishList(java.util.UUID u, String id) {
  // token round: null whenever the Void cannot be read for this player now; String[0] only when it is readable and holds none
  if (u == null || id == null || !@PKG@.SackDefs.isCatch(id)) return (String[]) null;
  int[] why = new int[1];
  String k = keyFor(u, id, why);
  if (k == null) return (String[]) null;
  @PKG@.BagMirror.beforeTake(k);
  return @PKG@.SackPool.fishView(k, id);
}"""), sbr))
sbr.addMethod(CtNewMethod.make(jt(r"""
public static long fishTake(java.util.UUID u, String id, String e, String tok) {
  if (u == null || id == null || e == null || !@PKG@.SackDefs.isCatch(id) || e.indexOf(';') >= 0) return 0L;
  if (tok != null && !@PKG@.SackPool.tokOk(tok)) return 0L;
  int[] why = new int[1];
  String k = keyFor(u, id, why);
  if (k == null) return 0L;
  @PKG@.BagMirror.beforeTake(k);
  int at = @PKG@.SackPool.fishList(k, id).indexOf(e);   // where it sits (a failed write puts it back exactly there)
  long now = System.currentTimeMillis();
  if (!@PKG@.SackPool.fishPickTok(k, id, e, tok, now)) return 0L;   // token round: fish + entry + token in one lock; a known token = 0
  String fk = k + "|" + id + "|" + e;
  java.util.ArrayList es = new java.util.ArrayList();
  es.add(e);
  try { @PKG@.BagMirror.afterTake(k, id); } catch (Throwable t1) { @PKG@.SackPool.warn("bag bridge: mirror trim failed after a fish take: " + t1); }
  LASTKEY.put(u.toString() + "|" + id, k);
  oweE(k, id, 1L, es, now);
  ftokPush(fk, tok);
  if (!@PKG@.SackPool.saveOk(k)) {
    // not on disk: undo in memory (the fish + entry back at their place, the token gone, nothing owed) - the caller pays nothing
    if (fishUnowe(k, id, e, now)) @PKG@.SackPool.fishAtTok(k, id, e, at, tok, now);
    ftokDrop(fk, tok);
    @PKG@.SackPool.warn("fish take " + id + " (" + e + ") of " + k + " refused - the pool file could not be written (nothing moved)");
    return 0L;
  }
  try { @PKG@.CraftLog.later(k, "BAG-FISH-TAKE " + id + " (" + e + ")" + (tok == null ? "" : " token " + tok) + " (sacks:fn:fishTake)"); } catch (Throwable t3) { }
  return 1L;
}"""), sbr))
sbr.addMethod(CtNewMethod.make(jt(r"""
public static long fishPut(java.util.UUID u, String id, String e, String tok) {
  if (u == null || id == null || e == null || !@PKG@.SackDefs.isCatch(id)) return 0L;
  if (tok != null && !@PKG@.SackPool.tokOk(tok)) return 0L;
  String k = refundKey(u, id);
  if (k == null) return 0L;
  long now = System.currentTimeMillis();
  String fk = k + "|" + id + "|" + e;
  String ct = ftokFind(fk, tok);          // token round: the token this put clears (a token no owed take of that entry carried = refused)
  if (ct == null) return 0L;
  String ctn = ct.length() == 0 ? (String) null : ct;
  if (!fishUnowe(k, id, e, now)) return 0L;
  @PKG@.SackPool.fishAtTok(k, id, e, 0, ctn, now);   // the fish back at the oldest end + its token cleared, one lock, one write
  ftokDrop(fk, ctn);
  if (!@PKG@.SackPool.saveOk(k)) {
    // not on disk: out again (token stored again) and still owed - the caller gets 0 and gives the fish another way (never twice)
    if (@PKG@.SackPool.fishPickTok(k, id, e, ctn, now)) {
      java.util.ArrayList es = new java.util.ArrayList();
      es.add(e);
      oweE(k, id, 1L, es, now);
      ftokPush(fk, ctn);
    } else @PKG@.SackPool.warn("fish put " + id + " (" + e + ") of " + k + ": could not take it out again after a failed write");
    @PKG@.SackPool.warn("fish put " + id + " (" + e + ") of " + k + " refused - the pool file could not be written");
    return 0L;
  }
  try { @PKG@.CraftLog.later(k, "BAG-FISH-RETURN " + id + " (" + e + ") (sacks:fn:fishPut)"); } catch (Throwable t3) { }
  return 1L;
}"""), sbr))
# token round: sacks:fn:fishTaken - TRUE = that take is on disk in the active profile's pool, FALSE = definitely not, null = cannot tell now
# (since = the caller's op time, -1 = not given: FALSE needs since after the prune cut, or no prune ever)
sbr.addMethod(CtNewMethod.make(jt(r"""
public static Boolean fishTaken(java.util.UUID u, String tok, long since) {
  if (u == null || !@PKG@.SackPool.tokOk(tok)) return (Boolean) null;
  String k = @PKG@.SackPool.settledKey(u);
  if (k == null || playerOf(u) == null) return (Boolean) null;
  if (@PKG@.SackPool.tokHas(k, tok)) return Boolean.TRUE;
  long cut = @PKG@.SackPool.tokCut(k);
  if (since < 0L) { if (cut > 0L) return (Boolean) null; }
  else if (since <= cut) return (Boolean) null;
  return Boolean.FALSE;
}"""), sbr))
# SackFn modes 14 fishList + 17 fishTaken (bad arguments = null), 15 fishTake, 16 fishPut (bad arguments = 0); never throws to the caller
sbr.addMethod(CtNewMethod.make(jt(r"""
public static Object fishCall(int mode, Object o) {
  try {
    if (!(o instanceof Object[])) return (mode == 14 || mode == 17) ? null : Long.valueOf(0L);
    Object[] a = (Object[]) o;
    if (a.length < 2 || !(a[0] instanceof java.util.UUID) || !(a[1] instanceof String)) return (mode == 14 || mode == 17) ? null : Long.valueOf(0L);
    java.util.UUID u = (java.util.UUID) a[0];
    String id = (String) a[1];
    if (mode == 14) return fishList(u, id);
    if (mode == 17) {
      if (a.length > 2 && a[2] != null && !(a[2] instanceof Number)) return null;
      long since = (a.length > 2 && a[2] instanceof Number) ? ((Number) a[2]).longValue() : -1L;
      return fishTaken(u, id, since);
    }
    if (a.length < 3 || !(a[2] instanceof String)) return Long.valueOf(0L);
    if (a.length > 3 && a[3] != null && !(a[3] instanceof String)) return Long.valueOf(0L);
    String tok = (a.length > 3 && a[3] instanceof String) ? (String) a[3] : (String) null;
    if (mode == 15) return Long.valueOf(fishTake(u, id, (String) a[2], tok));
    if (mode == 16) return Long.valueOf(fishPut(u, id, (String) a[2], tok));
  } catch (Throwable t) {
    @PKG@.KnowSync.warnOnce("bag bridge fish call failed (mode " + mode + "): " + t);
  }
  return (mode == 14 || mode == 17) ? null : Long.valueOf(0L);
}"""), sbr))
''')
P.rep('''    if (this.mode >= 5) return @PKG@.SackBridge.call2(this.mode, o);   // 0.7.17: deposit, pocketFill, the craft bridges
''', '''    if (this.mode >= 14) return @PKG@.SackBridge.fishCall(this.mode, o);   // 0.8.17: fishList / fishTake / fishPut / fishTaken
    if (this.mode >= 5) return @PKG@.SackBridge.call2(this.mode, o);   // 0.7.17: deposit, pocketFill, the craft bridges
''')
P.rep('''  return (this.mode == 3 || this.mode == 12 || this.mode == 13) ? null : Long.valueOf(this.mode == 0 ? -1L : 0L);''',
      '''  return (this.mode == 3 || this.mode == 12 || this.mode == 13 || this.mode == 14 || this.mode == 17) ? null : Long.valueOf(this.mode == 0 ? -1L : 0L);''')
P.rep('''  sbr0.put("sacks:fn:catOf", new {PKG}.SackFn(13));
''', '''  sbr0.put("sacks:fn:catOf", new {PKG}.SackFn(13));
  // 0.8.17 (SkyyFishing 0.1.10's Fishing Bench sells / fillets the Void's weighed fish): the contract of tools/fishing_0_1_10_patch.py A
  sbr0.put("sacks:fn:fishList", new {PKG}.SackFn(14));
  sbr0.put("sacks:fn:fishTake", new {PKG}.SackFn(15));
  sbr0.put("sacks:fn:fishPut", new {PKG}.SackFn(16));
  sbr0.put("sacks:fn:fishTaken", new {PKG}.SackFn(17));   // token round: did that take reach the disk
''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.8.17 adds no system / command"
P.finish()
