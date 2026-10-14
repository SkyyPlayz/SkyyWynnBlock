"""Derive SkyyAuctions/build_skyyauctions_0.1.5.py from the GENERATED 0.1.4 script (the SET pin; 0.1.4 and every older script stay untouched):
    python tools/auctions_0_1_5_patch.py
    python SkyyAuctions/build_skyyauctions_0.1.5.py          (must end 'assembled ...SkyyAuctions-0.1.5.jar')
    python SkyyAuctions/test_skyyauctions_0.1.5.py           (harness)
Edit THIS patch, never the generated script.

0.1.5 (2026-10-14) = REBIRTH R4, the Auction House side (research/cloud/Rebirth-Spec.md 2.1 / 2.4 / 4.3 / 6 R4; docs/answered/economy.md
2026-10-13 REBIRTH SPEC Q9, Skyy word for word: "all three. can auto close all if you click continue." -> the rebirth page lists what is
blocking and a Continue button auto-closes all open orders / listings (refund items + coins) before going on).
 A. ah:fn:closeall - cancels every open listing of ONE profile key through the Auction House's own cancel rules, inside the one AhStore
    lock (AhStore.closeAll0): each ACTIVE BIN listing of that seller key becomes CANCELLED (or EXPIRED when its end time already passed
    and the 10 s tick had not caught it yet - cancel0's rule) with sellerItem OWED (the full listed quantity) - ONE atomic record write
    per listing (AhStore.commit: tmp + fsync + ATOMIC_MOVE, then the memory swap; a failed write changes nothing). The item is NOT
    moved by closeall: it waits in the seller's claims (/ah > Manage > Claim item, /ah claim, the join notice), exactly where a cancel
    with a full inventory leaves it. So closeall needs no player, no world thread and no inventory (it can run from any thread, online or
    offline) and can never duplicate or lose an item: the item stays inside its record the whole time and only the record's state moves.
    One CLOSEALL line per listing in auctions.log. Fees: kept (Skyy LOCKED 2026-09-25 "cancelling keeps the fee"; closeall never refunds
    a fee, even with cancelRefundsFee=true - a coin refund would be a second, non-atomic step; DECISION, logged as fee-kept).
    BIDS: SkyyAuctions is Buy It Now only (Skyy 2026-09-24), so no listing can carry a bid. A record this version cannot act on (a newer
    schema v > 1, type AUCTION, an unknown state - shown read-only) that is still open for that seller is never touched and BLOCKS
    (the spec's "a listing WITH a bid cannot be pulled -> it stays a blocking line").
    IDEMPOTENT: a second call finds nothing ACTIVE and answers ok:0. CRASH-SAFE: each listing is one atomic file write; a crash before a
    write leaves that listing ACTIVE (still listed, nothing moved), after it leaves it CANCELLED + item owed; the next call closes what is
    left. Proven by the harness at every step (AhStore.CRASH_AT, a test-only hook, -1 = off).
 B. ah:fn:wouldclose - the read-only "what would close" query for the rebirth page (no lock-held write, nothing changes).
 C. /ahadmin closeall [confirm] - admin test command on the admin's OWN active profile: without confirm it prints the wouldclose answer
    in plain words; with confirm it calls the published ah:fn:closeall object (the exact path SkyyRebirth's Continue will use).
 D. The online seller gets one chat line after a closeall that closed something; auction:count + auction:claims:<uuid> are republished.

KEY CONTRACT (for SkyyRebirth's Continue button - built in a later Rebirth round; java.lang types only, through skyy.bridge):
  ah:fn:closeall    java.util.function.Function. apply(String pkey) -> String. Never throws, never calls another mod back.
                    pkey = the profile key (profile:fn:key(uuid), or uuid.toString() without SkyyProfiles) - the key the listings were
                    made under (seller.key). Any thread; takes the Auction House lock for a few ms per listing (one fsynced write each).
     "ok:<n>"                       every open listing of pkey is closed now; n = how many THIS call closed (0 = none were open).
     "err:bad-key"                  pkey null / empty / not a String.
     "err:blocked:<n>:<b>"          n closed now, b blocking rows stay (listings this version cannot touch - newer schema / auction
                                    type - plus unclaimed sales, see wouldclose). FIX 2 2026-10-14: when the profile has ANY unclaimed
                                    sale coins, closeall closes NOTHING and answers "err:blocked:0:<b>" (checked before the first
                                    write) - a rebirth that cannot go on never costs the player their listings or fees. Read-only
                                    listings alone do not stop the others closing (spec 2.4: "a listing WITH a bid ... stays a
                                    blocking line" while the rest are pulled).
     "err:write-failed:<n>:<f>"     n closed now, f could not be saved (still ACTIVE, nothing changed) -> call again later.
     "err:exception"                unexpected (logged as a WARN) - treat as not done.
  ah:fn:wouldclose  java.util.function.Function. apply(String pkey) -> String, read-only:
     line 1  "ok:<closable>:<blocking>:<claims>:<coins>"   closable = open listings closeall would cancel; blocking = open listings it
             cannot (see above); claims = rows already waiting in /ah Manage for pkey (coins after a sale, items back) and coins = the
             coins inside them. FIX 2026-10-14: UNCLAIMED SALE COINS BLOCK (each SOLD record whose coins wait in /ah Manage counts
             once in <blocking>): purse + bank go to 0 at rebirth ("you lose the money") and the balance at reset sets the bank
             bonus, so coins parked in /ah would dodge both - the player claims them first (/ah > Manage, /ah claim).
             Item claims (cancelled / expired / bought items) never block - items are kept through a rebirth.
     then one line per open listing, oldest id first: "<id>\t<1 closable | 0 blocking>\t<qty>\t<price>\t<endsAtMillis>\t<item name>",
     then one line per unclaimed sale: "<id>\t2\t<qty>\t<coins owed>\t0\t<item name>" (2 = sale coins waiting, blocks)
     (tabs / line breaks in the name become spaces). "err:bad-key" / "err:exception" as above.
     closeall's "err:blocked:<n>:<b>" counts the same blocking rows (b = listings it cannot touch + unclaimed sales).
  SkyyRebirth reads wouldclose for the page lines, calls closeall on Continue, then re-reads wouldclose: only "ok:0:0:..." means the
  Auction House check is met (spec 2.4 "Then the checks run again"). Removed from the bridge at shutdown.
  PAGE TEXT for SkyyRebirth (until Skyy answers the open question below): a kind-1 line = "<name> x<qty> - will be cancelled, the item
  waits in /ah > Manage"; kind-0 = "<name> x<qty> - can't be pulled yet"; kind-2 = "<name> x<qty> SOLD - claim your <coins> coins in
  /ah > Manage first". Continue should not call closeall while a kind-2 line shows (closeall would answer err:blocked:0:<b> anyway).
  OPEN QUESTION for Skyy (main session records it; this round may not edit OPEN-QUESTIONS.md): unclaimed AH sale coins BLOCK the
  rebirth (the player claims them -> purse -> lost with it). Alternative: Continue claims them into the purse automatically.
  BUSY ORDER for SkyyRebirth's commit step 0 (critic, 2026-10-14; resolves spec 2.1 "no rebirth in flight" vs 5.2 step 0): Continue
  (closeall) runs first, outside the transaction (spec 2.4). Then step 0 in this order: (a) the silent checks incl. "no rebirth in
  flight" - judged from the journal, never from rebirth:busy - (b) set rebirth:busy:<uuid> = TRUE, (c) the 2.1 re-check including
  ah:fn:wouldclose == "ok:0:0:..." (and the Bazaar's), (d) on a failed re-check clear busy and stop BEFORE writing BEGIN (nothing to
  abort). 0.1.5 refuses every AH action of that player (list, buy, cancel, claim) while busy is TRUE, so nothing new can be listed
  between that "ok:0:0:" and the reset (closeall leaves no open listing, so nothing of theirs can sell). Keep busy until DONE / ABORTED.
Rolling back to 0.1.4 is safe: closeall only writes ordinary CANCELLED / EXPIRED records (plus a "closeAll" field 0.1.4 ignores and keeps).
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyAuctions", "build_skyyauctions_0.1.4.py")
dst = os.path.join(ROOT, "SkyyAuctions", "build_skyyauctions_0.1.5.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
assert 'VERSION = "0.1.4"' in s and "closeAll0" not in s, "the source must be the generated 0.1.4 script"


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:160])
    s = s.replace(old, new)


rep('VERSION = "0.1.4"', 'VERSION = "0.1.5"')
s = ('"""0.1.5 (2026-10-14): REBIRTH R4 - ah:fn:closeall (cancel every open listing of one profile key, items wait in its claims, one\n'
     '  atomic write per listing, idempotent) + ah:fn:wouldclose (read-only) + /ahadmin closeall [confirm]. KEY CONTRACT and notes in\n'
     '  tools/auctions_0_1_5_patch.py.\n' + s[3:])

# ---- the new class (compiled before AhStore's callers? it only calls AhStore, so it is made with the others and filled after AhStore)
rep('''lfn  = pool.makeClass(PKG + ".AhLowestBinFn")
''', '''lfn  = pool.makeClass(PKG + ".AhLowestBinFn")
rbf  = pool.makeClass(PKG + ".AhRebirthFn")   # 0.1.5: ah:fn:closeall (op 0) / ah:fn:wouldclose (op 1)
''')

# ---- A + B: AhStore.openOf / closeAll0 / wouldClose0 + the locked wrappers (after the other wrappers, before claimAll)
rep('''# /ahadmin reload inside the one lock: every trade (also inside it) sees the whole old or the whole new config, never a mix''',
    '''# ---- 0.1.5 REBIRTH R4 (tools/auctions_0_1_5_patch.py): close every open listing of one profile key / what that would close.
# open = not closed, seller key = key, and ACTIVE (this version can cancel it) or read-only and not in a finished state (a newer
# schema / auction type: never touched, it BLOCKS). Oldest id first (a fixed order, so a crash test can stop at any listing).
F(sto, "public static volatile int CRASH_AT = -1;")   # TEST ONLY (the harness): closeAll0 throws at this step; -1 = off
M(sto, r"""
public static boolean openFor(@BD@ r, String key) {
  if (r == null || @PKG@.AhRec.bool(r, "closed", false)) return false;
  if (!key.equals(@PKG@.AhRec.subStr(r, "seller", "key", ""))) return false;
  String st = @PKG@.AhRec.state(r);
  if (!@PKG@.AhRec.readOnly(r)) return "ACTIVE".equals(st);
  return !("SOLD".equals(st) || "EXPIRED".equals(st) || "CANCELLED".equals(st) || "REMOVED".equals(st));
}""")
M(sto, r"""
public static java.util.ArrayList openOf(String key) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (key == null || key.length() == 0) return out;
  java.util.Iterator it = LIVE.values().iterator();
  while (it.hasNext()) {
    @BD@ r = (@BD@) it.next();
    if (!openFor(r, key)) continue;
    long n = @PKG@.AhRec.numId(r);
    int at = out.size();
    while (at > 0 && @PKG@.AhRec.numId((@BD@) out.get(at - 1)) > n) at--;
    out.add(at, r);
  }
  return out;
}""")
# FIX 2026-10-14 (critic): the ids of pkey's SOLD records whose sale coins are still unclaimed (rowsFor's "coins" rows).
# They BLOCK a rebirth: coins in /ah Manage are in neither purse nor bank, so claiming them after the reset would dodge Skyy's
# "you lose the money" (economy.md 2026-10-12) and skip the bank-bonus balance (Rebirth-Spec 2.4 / 3.3).
M(sto, r"""
public static java.util.ArrayList coinRows(String key) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (key == null || key.length() == 0) return out;
  java.util.ArrayList rows = rowsFor(key);
  for (int i = 0; i < rows.size(); i++) {
    String[] x = (String[]) rows.get(i);
    if (x[1].equals("coins")) out.add(x[0]);
  }
  return out;
}""")
M(sto, r"""
public static void crashPoint(int step) {
  if (CRASH_AT >= 0 && step == CRASH_AT) throw new IllegalStateException("closeall crash test at step " + step);
}""")
# inside the lock. uuids collects the seller uuids of what closed (chat + bridge republish happen AFTER the lock, R1).
# Steps per listing k (0-based among the closable ones): 2k = before its write, 2k+1 = after its write, before its log line.
M(sto, r"""
public static String closeAll0(String key, long now, java.util.ArrayList uuids) {
  if (key == null || key.trim().length() == 0) return "err:bad-key";
  java.util.ArrayList open = openOf(key);
  int closed = 0, blocked = 0, failed = 0, step = 0;
  int coins = coinRows(key).size();   // FIX 2026-10-14: unclaimed sale coins block (purse + bank go to 0 at rebirth)
  if (coins > 0) {
    // FIX 2 2026-10-14 (critic): checked BEFORE anything closes - a rebirth that cannot go on must not cost the player their
    // listings + fees. Nothing is written; the answer counts the same blocking rows wouldclose shows (read-only listings + sales).
    for (int i = 0; i < open.size(); i++) { if (@PKG@.AhRec.readOnly((@BD@) open.get(i))) blocked++; }
    return "err:blocked:0:" + (blocked + coins);
  }
  for (int i = 0; i < open.size(); i++) {
    @BD@ r = (@BD@) open.get(i);
    if (@PKG@.AhRec.readOnly(r)) { blocked++; continue; }
    String id = @PKG@.AhRec.id(r);
    boolean expired = now >= @PKG@.AhRec.lng(r, "endsAt", 0L);
    String su = @PKG@.AhRec.subStr(r, "seller", "uuid", "");
    @BD@ next = @PKG@.AhRec.next(r);
    next.put("state", new org.bson.BsonString(expired ? "EXPIRED" : "CANCELLED"));
    @PKG@.AhRec.setClaim(next, "sellerItem", "OWED");
    @PKG@.AhRec.subw(next, "claims").put("sellerItemQty", new org.bson.BsonInt64(@PKG@.AhRec.subLng(r, "item", "qty", 1L)));
    boolean on = online(su);
    @PKG@.AhRec.subw(next, "noticed").put("seller", org.bson.BsonBoolean.valueOf(on));
    next.put("closeAll", new org.bson.BsonInt64(now));
    crashPoint(step);
    step++;
    if (!commit(next)) { failed++; step++; continue; }
    crashPoint(step);
    step++;
    closed++;
    @PKG@.AhLog.log("CLOSEALL", id, "key=" + @PKG@.AhUtil.tok(key) + " state=" + (expired ? "EXPIRED" : "CANCELLED") + " seller=" + @PKG@.AhUtil.tok(@PKG@.AhRec.subStr(r, "seller", "name", "")) + " " + itemTok(r) + " fee-kept=" + (@PKG@.AhRec.subLng(r, "fee", "listing", 0L) + @PKG@.AhRec.subLng(r, "fee", "duration", 0L)));
    if (uuids != null && su.length() > 0 && !uuids.contains(su)) uuids.add(su);
  }
  if (failed > 0) return "err:write-failed:" + closed + ":" + failed;
  if (blocked > 0) return "err:blocked:" + closed + ":" + blocked;
  return "ok:" + closed;
}""")
M(sto, r"""
public static String cleanName(String s) {
  if (s == null) return "";
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < s.length() && i < 120; i++) {
    char c = s.charAt(i);
    sb.append(c == '\\t' || c == '\\n' || c == '\\r' ? ' ' : c);
  }
  return sb.toString();
}""")
M(sto, r"""
public static String wouldClose0(String key) {
  if (key == null || key.trim().length() == 0) return "err:bad-key";
  java.util.ArrayList open = openOf(key);
  int ok = 0, blocked = 0;
  StringBuilder lines = new StringBuilder();
  for (int i = 0; i < open.size(); i++) {
    @BD@ r = (@BD@) open.get(i);
    boolean can = !@PKG@.AhRec.readOnly(r);
    if (can) ok++; else blocked++;
    lines.append('\\n').append(@PKG@.AhRec.id(r)).append('\\t').append(can ? "1" : "0").append('\\t').append(@PKG@.AhRec.subLng(r, "item", "qty", 1L)).append('\\t').append(@PKG@.AhRec.lng(r, "price", 0L)).append('\\t').append(@PKG@.AhRec.lng(r, "endsAt", 0L)).append('\\t').append(cleanName(@PKG@.AhRec.str(r, "name", @PKG@.AhRec.subStr(r, "item", "id", "?"))));
  }
  java.util.ArrayList cr = coinRows(key);
  for (int i = 0; i < cr.size(); i++) {
    @BD@ r = get((String) cr.get(i));
    if (r == null) continue;
    blocked++;
    lines.append('\\n').append(@PKG@.AhRec.id(r)).append('\\t').append("2").append('\\t').append(@PKG@.AhRec.subLng(r, "item", "qty", 1L)).append('\\t').append(@PKG@.AhRec.subLng(r, "sale", "net", 0L)).append('\\t').append("0").append('\\t').append(cleanName(@PKG@.AhRec.str(r, "name", @PKG@.AhRec.subStr(r, "item", "id", "?"))));
  }
  long[] o = owedFor(key);
  return "ok:" + ok + ":" + blocked + ":" + o[0] + ":" + o[1] + lines.toString();
}""")
M(sto, r"""
public static String closeAll(String key, java.util.ArrayList uuids) {
  long now = System.currentTimeMillis();
  synchronized (@PKG@.AhStore.class) { return closeAll0(key, now, uuids); }
}""")
M(sto, r"""
public static String wouldClose(String key) {
  synchronized (@PKG@.AhStore.class) { return wouldClose0(key); }
}""")
# /ahadmin reload inside the one lock: every trade (also inside it) sees the whole old or the whole new config, never a mix''')

# ---- the bridge Function (after AhLowestBinFn; AhStore.publishCount / publishClaims / tell exist above it)
rep('''# ================= AhPage: the one inline page (Browse / Item / Create / Manage) =================''',
    '''# ================= 0.1.5 AhRebirthFn: ah:fn:closeall (op 0) / ah:fn:wouldclose (op 1) - KEY CONTRACT in tools/auctions_0_1_5_patch.py
rbf.addInterface(pool.get("java.util.function.Function"))
F(rbf, "public int op;")
C(rbf, "public AhRebirthFn(int op) { this.op = op; }")
M(rbf, r"""
public static void after(java.util.ArrayList uuids, String res) {
  @PKG@.AhStore.publishCount();
  int n = 0;
  if (res != null && res.startsWith("ok:")) { try { n = Integer.parseInt(res.substring(3)); } catch (Throwable t) { n = 0; } }
  else if (res != null && (res.startsWith("err:blocked:") || res.startsWith("err:write-failed:"))) {
    try { String[] p = res.split(":"); n = Integer.parseInt(p[2]); } catch (Throwable t) { n = 0; }
  }
  for (int i = 0; i < uuids.size(); i++) {
    java.util.UUID u = null;
    try { u = java.util.UUID.fromString((String) uuids.get(i)); } catch (Throwable t) { u = null; }
    if (u == null) continue;
    @PKG@.AhStore.publishClaims(u);
    if (n > 0) @PKG@.AhStore.tell(u, "[Auction House] " + n + (n == 1 ? " of your listings was" : " of your listings were") + " cancelled - the items wait in /ah > Manage (Claim item). Listing fees are not refunded.");
  }
}""")
M(rbf, r"""
public Object apply(Object o) {
  try {
    if (!(o instanceof String) || ((String) o).trim().length() == 0) return "err:bad-key";
    String key = ((String) o).trim();
    if (this.op == 1) return @PKG@.AhStore.wouldClose(key);
    java.util.ArrayList uuids = new java.util.ArrayList();
    String r = @PKG@.AhStore.closeAll(key, uuids);
    after(uuids, r);
    return r;
  } catch (Throwable t) {
    @PKG@.AhUtil.warn("ah:fn:" + (this.op == 1 ? "wouldclose" : "closeall") + " failed: " + t);
    return "err:exception";
  }
}""")

# ================= AhPage: the one inline page (Browse / Item / Create / Manage) =================''')

# ---- C: /ahadmin closeall [confirm] (admin's own active profile)
rep('''  atell(pr, "/ahadmin list [player] | info <id> | remove <id> [reason] | reload | pause | resume | regrant <id> <seller|buyer> [confirm]");''',
    '''  atell(pr, "/ahadmin list [player] | info <id> | remove <id> [reason] | reload | pause | resume | regrant <id> <seller|buyer> [confirm] | closeall [confirm]");''')
rep('''M(cmds, r"""
public static void regrant(@PR@ pr, String id, String side, boolean confirm) {''', '''# 0.1.5: /ahadmin closeall [confirm] - the rebirth Continue path on the admin's OWN active profile, through the published bridge objects
M(cmds, r"""
public static void closeAll(@PR@ pr, boolean confirm) {
  String key = @PKG@.AhUtil.pkey(pr.getUuid());
  java.util.Map b = @PKG@.AhUtil.bridge();
  Object f = b.get(confirm ? "ah:fn:closeall" : "ah:fn:wouldclose");
  if (!(f instanceof java.util.function.Function)) { atell(pr, "ah:fn:closeall / wouldclose are not on the bridge (is SkyyAuctions 0.1.5 loaded?)."); return; }
  String r = String.valueOf(((java.util.function.Function) f).apply(key));
  if (confirm) {
    atell(pr, "closeall on profile " + key + " -> " + r);
    String w = String.valueOf(((java.util.function.Function) b.get("ah:fn:wouldclose")).apply(key));
    atell(pr, "now open: " + (w.indexOf('\\n') >= 0 ? w.substring(0, w.indexOf('\\n')) : w) + " (ok:<closable>:<blocking>:<claims>:<coins>)");
    return;
  }
  String[] lines = r.split("\\n");
  atell(pr, "wouldclose on profile " + key + " -> " + lines[0] + " (ok:<closable>:<blocking>:<claims>:<coins>)");
  for (int i = 1; i < lines.length && i <= 20; i++) {
    String[] x = lines[i].split("\\t");
    if (x.length < 6) { atell(pr, lines[i]); continue; }
    if ("2".equals(x[1])) { atell(pr, "#" + x[0] + " " + x[5] + " x" + x[2] + " SOLD - " + x[3] + " coins unclaimed - BLOCKS (claim them in /ah > Manage first)"); continue; }
    atell(pr, "#" + x[0] + " " + x[5] + " x" + x[2] + " for " + x[3] + " - " + ("1".equals(x[1]) ? "would be cancelled (item to your claims)" : "BLOCKS (this version cannot cancel it)"));
  }
  atell(pr, "Run /ahadmin closeall confirm to cancel them (the fee is kept, the items wait in /ah > Manage).");
}""")
M(cmds, r"""
public static void regrant(@PR@ pr, String id, String side, boolean confirm) {''')
rep('''c_adm = mk("AhAdminCmd")''', '''c_aco = mk("AhAdminCloseAllOkCmd")
F(c_aco, "public @RA@ okArg;")
C(c_aco, r"""
public AhAdminCloseAllOkCmd() {
  super("(admin) cancel every open listing of your own active profile (rebirth Continue test): /ahadmin closeall confirm");
  requirePermission("skyyauctions.admin");
  this.okArg = withRequiredArg("confirm", "the word confirm", @ATY@.STRING);
}""")
exe(c_aco, r"""String ok = String.valueOf(ctx.get(this.okArg)).trim();
    if (!ok.equalsIgnoreCase("confirm")) { @PKG@.AhCmds.atell(pr, "The word after closeall must be confirm: /ahadmin closeall confirm"); return; }
    @PKG@.AhCmds.closeAll(pr, true);""", "/ahadmin closeall")

c_ac = mk("AhAdminCloseAllCmd")
C(c_ac, r"""
public AhAdminCloseAllCmd() {
  super("closeall", "(admin) PREVIEW what the rebirth Continue button would cancel on your own profile: /ahadmin closeall [confirm]");
  requirePermission("skyyauctions.admin");
  addUsageVariant(new @PKG@.AhAdminCloseAllOkCmd());
}""")
exe(c_ac, "@PKG@.AhCmds.closeAll(pr, false);", "/ahadmin closeall")

c_adm = mk("AhAdminCmd")''')
rep('''  addSubCommand(new @PKG@.AhAdminRegrantCmd());''', '''  addSubCommand(new @PKG@.AhAdminRegrantCmd());
  addSubCommand(new @PKG@.AhAdminCloseAllCmd());''')

# ---- FIX 2026-10-14 (critic, spec 5.4 busy window): every Auction House action (list, buy, cancel, claims) is refused while SkyyRebirth
# publishes rebirth:busy:<uuid> = Boolean.TRUE (a lock-free bridge read, safe inside the AhStore lock). closeall itself never asks.
rep('''M(utl, r\"\"\"
public static String deny(java.util.UUID u) {''', '''M(utl, r\"\"\"
public static boolean rebirthBusy(java.util.UUID u) {
  if (u == null) return false;
  try { return Boolean.TRUE.equals(bridge().get("rebirth:busy:" + u)); } catch (Throwable t) { return false; }
}\"\"\")
M(utl, r\"\"\"
public static String deny(java.util.UUID u) {''')
rep('''  if (@PKG@.AhUtil.busy(u)) return "Your profile is still loading - try again in a moment.";''',
    '''  if (@PKG@.AhUtil.busy(u)) return "Your profile is still loading - try again in a moment.";
  if (@PKG@.AhUtil.rebirthBusy(u)) return "A rebirth is running on your profile - the Auction House waits until it is done.";''')
# FIX 2026-10-14 (critic): say in the setting's own comment that the rebirth Continue closeall keeps the fee whatever this says
rep('''    "# cancelRefundsFee / adminRemoveRefundsFee = give the listing fee back on a cancel / an admin removal (Hypixel keeps it)",''',
    '''    "# cancelRefundsFee / adminRemoveRefundsFee = give the listing fee back on a cancel / an admin removal (Hypixel keeps it).",
    "#   The rebirth Continue button (ah:fn:closeall) always keeps the fee, even with cancelRefundsFee=true (Skyy LOCKED 2026-09-25).",''')

# ---- plugin: publish after the listings are loaded; shutdown removes the ah: keys too
rep('''  b.put("auction:version", "@VERSION@");
''', '''  b.put("auction:version", "@VERSION@");
  b.put("ah:fn:closeall", new @PKG@.AhRebirthFn(0));     // 0.1.5 rebirth R4 (KEY CONTRACT: tools/auctions_0_1_5_patch.py)
  b.put("ah:fn:wouldclose", new @PKG@.AhRebirthFn(1));
''')
rep('''    while (it.hasNext()) { Object k = it.next(); if (k instanceof String && ((String) k).startsWith("auction:")) b.remove(k); }''',
    '''    while (it.hasNext()) { Object k = it.next(); if (k instanceof String && ((String) k).startsWith("auction:")) b.remove(k); }
    b.remove("ah:fn:closeall");
    b.remove("ah:fn:wouldclose");''')
rep('''ALL = [utl, cfg, lg, coin, rec, itm, res, srt, idx, sto, lfn, page, fac, cmds]''',
    '''ALL = [utl, cfg, lg, coin, rec, itm, res, srt, idx, sto, lfn, rbf, page, fac, cmds]''')

assert s.index("public static String closeAll0(") < s.index("public static String closeAll(String key")
assert s.index("public static String closeAll(String key") < s.index("@PKG@.AhStore.closeAll(key, uuids)")
assert s.index('c_aco = mk("AhAdminCloseAllOkCmd")') < s.index('c_ac = mk("AhAdminCloseAllCmd")') < s.index('c_adm = mk("AhAdminCmd")')
assert not os.path.exists(dst), dst + " already exists - delete it first (it is generated)"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
