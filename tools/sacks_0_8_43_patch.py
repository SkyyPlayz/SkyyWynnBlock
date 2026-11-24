"""Derive SkyySacks/build_skyysacks_0.8.43.py from the SET pin 0.8.42 (the GENERATED build_skyysacks_0.8.42.py; edit THIS file, then
regenerate: python tools/sacks_0_8_43_patch.py; never re-run sacks_0_8_42_patch.py on top of it). Every anchor is asserted once; at the end
every change is undone on a copy and compared with 0.8.42 (nothing else changed). Line endings kept.
Run:  python tools/sacks_0_8_43_patch.py   then   python SkyySacks/build_skyysacks_0.8.43.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.8.43.py [--dir <folder inside tools/dev/scratch/>] [--keep]

0.8.43 (2026-11-24, round oldmenu10) = THE POCKET UPGRADE SHOP BRIDGE for SkyyMenu 0.3.78's in-screen Upgrades view (the last SkyySacks door
  of the old menu: the pocket panel's Upgrades opened this mod's own /pd Void page). Skyy 2026-11-22 (docs/answered/ui.md, 'RETIRE THE OLD
  MENU'): "when everything is in the new system id like to disable the old menu compleatly, so instead of adding things like the full tree
  button, just build it all into the new system and remove the old "Full tree""; 2026-11-24: "keep building".
  SURVEY: what the Void page on one pocket can do that SkyyMenu's pocket panel (sacks:fn:pocketList / pocket: Withdraw / Deposit / Sell /
  Unpack / the Auto-compact toggle) cannot: the rarity Upgrade box (VoidStore.upgrade), the Auto-compact Buy box (VoidCompact.buyAt), the
  Shard Link box (VoidLink.buyAt / toggle), Pick up all, Deposit <pocket>, Deposit every bag, the Stack refill row (RefillPref). The Crafting
  page's Tannery tab (sacks:fn:openTannery) does NOTHING beyond the 0.8.40 bridge sacks:fn:furn (queue / fuel / collect / cancel / unload
  = CraftPage.handleProc's every branch; Refresh = a redraw) - no Tannery op is needed, SkyyMenu 0.3.78 simply drops its Full page.
  Two new keys on skyy.bridge (SackFn modes 26 / 27), java.lang types only, the player's WORLD THREAD only (playerOf: off it = null, nothing
  read, nothing done) - the bank:fn:view / bank:fn:act pattern (SkyyBank 0.1.18):
  1. sacks:fn:upView {UUID, String pocket} -> String (lines, '\\n' between, '|' between fields; the LAST field of a line is free text with
     '|' and line breaks blanked). Every read makes a NEW click token for that player (the old one dies - one view at a time, like the page):
       h|ok|<token>|<profile key>|<pocket>|<level>|<rank 0-4>|<rarity name>|<omni 0/1>|<used>|<space>|<coins, -1 unreadable>
       u|<state up / bad / top / omni>|<rarity now 0-3>|<its name>|<next rarity>|<its name>|<its multiplier>|<space after>|<ready 0/1>|<text>
       c|<cost id>|<name>|<have>|<need>          the upgrade's cost cells (the page's: Void + inventory + Enchanted, a group = its running sum)
       k|<state none / buy / on / paused>|<price>|<ready 0/1>|<server switch 0/1>|<text>     the Auto-compact box
       l|<state none / need / buy / on / paused>|<price>|<ready 0/1>|<server switch 0/1>|<text>   the Shard Link box
       li|<item id>|<name>|<have>|<need>         the Shard Link's item cost (state buy only)
       r|<choice 0 hotbar / 1 full / 2 off>|<server switch 0/1>|<help text>                    the Stack refill row
     "off|<reason>" = the Void paused (profile loading / switching), an unknown pocket, this profile's Void unreadable (no token then).
  2. sacks:fn:upAct Object[] {String op, UUID player, String token, String profileKey, String arg} -> String: the page's answer line ("+" done,
     "-" refused / nothing done, "=" nothing done: something changed since the view - the caller redraws (a new view) and the same press runs
     again); null = not on the player's world thread / bad arguments (nothing done).
       up <rarity the view showed>     = VoidStore.upgrade(p, u, key, pocket, that rarity) (the page's Upgrade -> Pay: items from the Void
                                         first, then plain inventory stacks, all or nothing) + the page's sound
       cmpbuy <price the view showed>  = VoidCompact.buyAt(u, key, pocket, that price) then runNow (the page's Auto-compact Pay)
       cmptog <state the view showed>  = VoidCompact.toggle then runNow on "+" (the page's Pause / Turn on; refused while Server Setup
                                         pd.compact.on is off, as sacks:fn:pocket cmp); a Pause answers '+' here (the page's '=' note)
       lnkbuy <price the view showed>  = VoidLink.buyAt(p, u, key, pocket, that price) (the page's Shard Link Pay)
       lnktog <state the view showed>  = VoidLink.toggle (the page's Shard Link Pause / Turn on; a Pause answers '+')
       refill <hotbar / full / off>    = RefillPref.set (the page's Stack refill row; the file saved by the writer)
       takeall                         = the page's Pick up all (every item of THIS pocket to the inventory, withdrawN, stops at a full one)
       depcat                          = the page's Deposit <pocket> (its kept counts cleared, one sweep of that pocket)
       depevery                        = the page's Deposit every bag (every kept count cleared, one sweep, each pocket up to its room)
     Safety, in this order (nothing moves on any refusal): an unknown op = "-Unknown pocket action"; not the player's world thread = null;
     a token that is not this player's LAST view token = "=That click was for an older copy ..."; the Void paused = "-..."; a profile key
     that is not the view's (or another profile settled since) = "=Your profile changed ..."; the shown-value checks: a rarity / price /
     state / refill choice that is not what the view showed = "=older copy"; the current rarity, the upgrade cost text (Server Setup), the
     Auto-compact / Shard Link price, the Shard Link item cost text, the box state or the refill choice changed since the view = "=... changed
     since you looked ..." (nothing taken); THEN the token is USED UP atomically (ConcurrentHashMap.remove(player, record): of two racing
     presses with one token exactly one runs, the other gets "=older copy") and the page's own code path runs (its own checks again: the
     rarity it was shown, the price it was shown, coins / items all or nothing with refunds, the pd line on disk before the coins).
     A throw = "-That did not finish ..." (the pool saved soon, a [SkyyVoid] WARN once). Never throws to the caller.
  Every existing sacks:fn:* op is untouched (pocketList / pocket / openPocket / openTannery / furnList / furn / link keep their bytes);
  the /pd page is untouched. Tokens live in memory only (SackBridge.UPTOK).
  No saved-data change, no config row, no class, no system / command. ROLLBACK to 0.8.42: safe alone (the two keys disappear; SkyyMenu 0.3.78's
  Upgrades view then says it needs SkyySacks 0.8.43 - the Void page is still /pd). SkyyMenu 0.3.78 needs this jar for its Upgrades view;
  everything else of 0.3.78 works with 0.8.42.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G   # only its generic Patch helper (anchors asserted once, undo-compare, line endings kept)

P = G.Patch(os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.42.py"), os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.43.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.8.42"\n') and P.has("VoidLink") and not P.has("sacks:fn:upView"), "not the live generated SkyySacks 0.8.42"
SYS0, CMD0, CLS0 = P.s.count("registerSystem("), P.s.count("registerCommand("), P.s.count("makeClass(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.8.43 (2026-11-24"):].rstrip() + "\n"

P.rep('''  rollback (the link works again when 0.8.42 returns). Switch pd.link.on off and wait one minute first, so no shard transfer is half way.
''', '''  rollback (the link works again when 0.8.42 returns). Switch pd.link.on off and wait one minute first, so no shard transfer is half way.
''' + NOTE)
P.rep('VERSION = "0.8.42"\n', 'VERSION = "0.8.43"\n')
P.rep('''; Furnace / Tannery bridges for the inventory panel (0.8.40)");''',
      '''; Furnace / Tannery bridges for the inventory panel (0.8.40); pocket upgrade shop bridges sacks:fn:upView / upAct (0.8.43)");''')

# ---- SackBridge: the token map (next to PLAYERS)
P.rep('''sbr.addField(CtField.make("public static volatile java.util.function.Function FRECIPES;", sbr))   # 0.8.40: harness only (null in the game)
''', '''sbr.addField(CtField.make("public static volatile java.util.function.Function FRECIPES;", sbr))   # 0.8.40: harness only (null in the game)
# 0.8.43: UPTOK = uuid text -> Object[] { token, profile key, Integer pocket, Integer rarity, upgrade cost text, Long compact price, compact
# state, Long link price, link cost text, link state, Integer refill choice } = what the LAST sacks:fn:upView showed (memory only)
sbr.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap UPTOK = new java.util.concurrent.ConcurrentHashMap();", sbr))
sbr.addField(CtField.make("public static final java.util.concurrent.atomic.AtomicLong UPSEQ = new java.util.concurrent.atomic.AtomicLong();", sbr))
sbr.addField(CtField.make("public static final long UPBASE = java.util.concurrent.ThreadLocalRandom.current().nextLong() & 0x3fffffffffffffffL;", sbr))
''')

# ---- SackBridge: the view + the actions (before fishCall: every VoidStore / VoidCompact / VoidLink / SacksPage / RefillPref / SweepTask
# member they use is compiled before)
UP_JAVA = [r"""
public static String cmpSt(String k, int ci) {
  if (@PKG@.VoidCompact.pairsIn(ci, (java.util.Set) null) <= 0) return "none";
  if (!@PKG@.VoidCompact.bought(k, ci)) return "buy";
  return @PKG@.VoidCompact.paused(k, ci) ? "paused" : "on";
}""", r"""
public static String lnkSt(String k, int ci) {
  if (!@PKG@.VoidLink.linkable(ci)) return "none";
  if (@PKG@.VoidLink.bought(k, ci)) return @PKG@.VoidLink.paused(k, ci) ? "paused" : "on";
  return @PKG@.VoidStore.rank(k, ci) < @PKG@.VoidLink.NEED ? "need" : "buy";
}""", r"""
public static String upCost(String k, int ci) {
  int cur = @PKG@.VoidStore.rarOf(k, ci);
  if (@PKG@.VoidStore.omni(k) || cur >= 3) return "";
  String t = @PKG@.SackCfg.cost(ci, cur + 1);
  return t == null ? "" : t;
}""", r"""
public static String upView(java.util.UUID u, String cat) {
  @PLA@ p = playerOf(u);
  if (p == null) return null;
  String us = u.toString();
  String k = @PKG@.SackPool.settledKey(u);
  if (k == null) { UPTOK.remove(us); return "off|The Void is paused (profile loading or switching) - try again in a moment"; }
  int ci = @PKG@.SackDefs.catIndex(cat);
  if (ci < 0) { UPTOK.remove(us); return "off|No such pocket"; }
  @PKG@.VoidState s = @PKG@.VoidStore.st(k);
  if (s == null) { UPTOK.remove(us); return "off|" + fclean(@PKG@.VoidStore.NOREAD); }
  String[] cats = @PKG@.SackDefs.CATS;
  String cn = cats[ci];
  @INV@ inv = p.getInventory();
  int lv = @PKG@.VoidStore.level(u, k, ci);
  int rk = @PKG@.VoidStore.rank(k, ci);
  long cap = @PKG@.VoidStore.capOf(lv, rk);
  long used = @PKG@.VoidStore.usedAll(k)[ci];
  boolean omni = @PKG@.VoidStore.omni(k);
  long coins = @PKG@.VoidCompact.coins(u);
  StringBuilder sb = new StringBuilder();
  // THE RARITY UPGRADE BOX (SacksPage.upgradeBox)
  int cur = @PKG@.VoidStore.rarOf(k, ci);
  int to = cur + 1;
  String ust;
  String ut;
  boolean ready = false;
  long capTo = -1L;
  java.util.LinkedHashMap cost = null;
  String ucost = upCost(k, ci);
  StringBuilder cl = new StringBuilder();
  if (omni) { ust = "omni"; ut = "Omni - the top of every category. Space x" + @PKG@.SacksPage.multTxt(4) + " in all six categories"; to = 4; }
  else if (cur >= 3) { ust = "top"; ut = "Legendary - the top rarity. Omni comes when all six categories are Legendary (" + @PKG@.VoidStore.legendCount(k) + " of " + cats.length + " now)"; to = cur; }
  else {
    capTo = @PKG@.VoidStore.capOf(lv, to);
    cost = @PKG@.SackCfg.parseCost(ucost);
    if (cost == null) { ust = "bad"; ut = "This step's cost is not set right (Server Setup)"; }
    else { ust = "up"; ready = true; ut = "Pay the items below to upgrade"; }
  }
  if (cost != null) {
    java.util.HashMap needU = new java.util.HashMap();
    java.util.Iterator it = cost.entrySet().iterator();
    while (it.hasNext()) {
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      String cid = (String) e.getKey();
      long need = ((Long) e.getValue()).longValue();
      long have = @PKG@.VoidStore.haveOf(k, inv, cid) + @PKG@.VoidStore.encHave(k, cid);
      String uk = @PKG@.SackDefs.unitKey(cid);
      Long pn = (Long) needU.get(uk);
      if (pn != null) need = need + pn.longValue();
      needU.put(uk, Long.valueOf(need));
      if (have < need) ready = false;
      String un = @PKG@.SackDefs.lineName(cid);
      cl.append("\nc|").append(fclean(cid)).append('|').append(fclean(un == null ? @PKG@.SacksPage.pretty(cid) : un)).append('|').append(have).append('|').append(need);
    }
  }
  // THE AUTO-COMPACT BOX (SacksPage.compactBox)
  String kst = cmpSt(k, ci);
  long kcost = @PKG@.VoidCompact.price(ci);
  boolean kready = false;
  String kt;
  if ("none".equals(kst)) kt = "Nothing in " + cn + " has an Enchanted form yet.";
  else if ("buy".equals(kst)) {
    kready = kcost <= 0L || coins < 0L || coins >= kcost;
    kt = kready ? "100 of an item -> 1 Enchanted once its recipe is unlocked in Collections." : ("You have " + @PKG@.SacksPage.num(coins) + " coins. 100 items -> 1 Enchanted once bought.");
    if (kready && "Mining".equals(cn)) kt = "100 -> 1 Enchanted once its recipe is unlocked. Not yet: Rubble, Sand, Crystal.";
  } else {
    java.util.HashSet coll = @PKG@.KnowSync.collShared(u);
    java.util.Set cs0 = new java.util.HashSet();
    if (coll != null) cs0 = coll;
    kt = "on".equals(kst) ? @PKG@.VoidCompact.names(u, ci, cs0, "Mining".equals(cn) ? 40 : 60) : "Bought - nothing compacts here until you turn it on.";
    if ("on".equals(kst) && "Mining".equals(cn)) kt = kt + " Not yet: Rubble, Sand, Crystal.";
    if (!@PKG@.SackCfg.CMP_ON) kt = "Switched off on this server for now (Server Setup).";
  }
  // THE SHARD LINK BOX (SacksPage.linkBox)
  String lst = lnkSt(k, ci);
  long lcost = @PKG@.VoidLink.price(ci);
  String lct = @PKG@.VoidLink.linkable(ci) ? @PKG@.VoidLink.costText(ci) : "";
  if (lct == null) lct = "";
  boolean lready = false;
  String lt;
  StringBuilder ll = new StringBuilder();
  if ("none".equals(lst)) lt = "No shard fills the " + cn + " pocket.";
  else if ("on".equals(lst) || "paused".equals(lst)) {
    lt = "on".equals(lst) ? ("Your shards send their " + cn + " items straight here. When it is full they wait in the shard (Collect all).")
                          : "Bought - shard items wait in the shard until you turn it on.";
    if (!@PKG@.SackCfg.LINK_ON) lt = "Switched off on this server for now (Server Setup).";
  } else if ("need".equals(lst)) lt = "Late game: shard items go straight into this pocket, no Collect. Needs this pocket at " + @PKG@.SackDefs.RNAME[@PKG@.VoidLink.NEED] + " first.";
  else {
    boolean ok = lcost <= 0L || coins < 0L || coins >= lcost;
    java.util.LinkedHashMap need = @PKG@.SackCfg.parseCost(lct);
    if (need == null) { ok = false; lt = "The item cost is not set correctly (Server Setup)."; }
    else {
      java.util.Iterator it2 = need.entrySet().iterator();
      while (it2.hasNext()) {
        java.util.Map.Entry e = (java.util.Map.Entry) it2.next();
        String id = (String) e.getKey();
        long n = ((Long) e.getValue()).longValue();
        long h = @PKG@.VoidStore.haveOf(k, inv, id);
        if (h < n) ok = false;
        ll.append("\nli|").append(fclean(id)).append('|').append(fclean(@PKG@.SacksPage.pretty(id))).append('|').append(h).append('|').append(n);
      }
      lt = "Shard items then go straight in.";
    }
    lready = ok && @PKG@.SackCfg.LINK_ON;
    if (!@PKG@.SackCfg.LINK_ON) lt = "Switched off on this server for now (Server Setup).";
  }
  // THE STACK REFILL ROW (SacksPage.refillRow)
  int rm = @PKG@.RefillPref.choice(u);
  int hm = rm < 0 || rm >= @PKG@.RefillPref.HELP.length ? 0 : rm;
  boolean pc = @PKG@.SackCfg.POCKET_CRAFT;
  String rh = @PKG@.SackCfg.REFILL_ON ? (pc ? @PKG@.RefillPref.HELP[hm] : @PKG@.RefillPref.HELPB[hm]) : (pc ? @PKG@.RefillPref.OFFSRV : @PKG@.RefillPref.OFFSRVB);
  String tok = Long.toHexString(UPBASE + UPSEQ.incrementAndGet());
  UPTOK.put(us, new Object[] { tok, k, Integer.valueOf(ci), Integer.valueOf(cur), ucost, Long.valueOf(kcost), kst, Long.valueOf(lcost), lct, lst, Integer.valueOf(rm) });
  sb.append("h|ok|").append(tok).append('|').append(fclean(k)).append('|').append(cn).append('|').append(lv).append('|').append(rk).append('|').append(@PKG@.SackDefs.RNAME[rk])
    .append('|').append(omni ? 1 : 0).append('|').append(used).append('|').append(cap).append('|').append(coins);
  sb.append("\nu|").append(ust).append('|').append(cur).append('|').append(@PKG@.SackDefs.RNAME[cur]).append('|').append(to).append('|').append(@PKG@.SackDefs.RNAME[to])
    .append('|').append(@PKG@.SacksPage.multTxt(to)).append('|').append(capTo).append('|').append(ready ? 1 : 0).append('|').append(fclean(ut));
  sb.append(cl);
  sb.append("\nk|").append(kst).append('|').append(kcost).append('|').append(kready ? 1 : 0).append('|').append(@PKG@.SackCfg.CMP_ON ? 1 : 0).append('|').append(fclean(kt));
  sb.append("\nl|").append(lst).append('|').append(lcost).append('|').append(lready ? 1 : 0).append('|').append(@PKG@.SackCfg.LINK_ON ? 1 : 0).append('|').append(fclean(lt));
  sb.append(ll);
  sb.append("\nr|").append(rm).append('|').append(@PKG@.SackCfg.REFILL_ON ? 1 : 0).append('|').append(fclean(rh));
  return sb.toString();
}""", r"""
public static String upTakeAll(@PLA@ p, String k, String cat) {
  long total = 0L;
  java.util.ArrayList ids = new java.util.ArrayList();
  java.util.Iterator it = @PKG@.SackPool.pool(k).entrySet().iterator();
  while (it.hasNext()) { java.util.Map.Entry e2 = (java.util.Map.Entry) it.next(); if (cat.equals(@PKG@.SackDefs.homeOf((String) e2.getKey()))) ids.add(e2.getKey()); }
  for (int i = 0; i < ids.size(); i++) {
    long got = @PKG@.SacksPage.withdrawN(p, k, (String) ids.get(i), 9223372036854775807L);
    total += got;
    if (got <= 0L && @PKG@.SackPool.get(k, (String) ids.get(i)) > 0L) break;
  }
  return total > 0L ? ("+Picked up " + @PKG@.SacksPage.num(total) + " items") : "-Nothing taken (your storage is full, or this category is empty)";
}""", r"""
public static String upDeposit(@PLA@ p, java.util.UUID u, String k, String cat) {
  if (cat == null) {
    String[] cats = @PKG@.SackDefs.CATS;
    for (int c = 0; c < cats.length; c++) @PKG@.SackPool.clearKeptCat(k, cats[c]);
    @PKG@.SackPool.forgetSeen(u);
    java.util.HashMap swept = new java.util.HashMap();
    int moved = @PKG@.SweepTask.sweep(p, k, (String) null, true, swept, @PKG@.VoidStore.capsK(u, k), (java.util.HashMap) null);
    java.util.HashSet into = new java.util.HashSet();
    java.util.Iterator si = swept.keySet().iterator();
    while (si.hasNext()) { String c0 = @PKG@.SackDefs.homeOf((String) si.next()); if (c0 != null) into.add(c0); }
    String r = moved > 0 ? ("+Deposited " + @PKG@.SacksPage.num((long) moved) + " items into " + into.size() + (into.size() == 1 ? " bag" : " bags")) : "-Nothing to deposit (or those bags are full)";
    if (!@PKG@.SackDefs.COOKED_FARM && @PKG@.SweepTask.cookedHeld(p.getInventory()) > 0) r = r + " - cooked food stays in your inventory";
    return r;
  }
  @PKG@.SackPool.clearKeptCat(k, cat);
  @PKG@.SackPool.forgetSeen(u);
  int moved2 = @PKG@.SweepTask.sweep(p, k, cat, true, (java.util.HashMap) null, @PKG@.VoidStore.capsK(u, k), (java.util.HashMap) null);
  String r2 = moved2 > 0 ? ("+Deposited " + @PKG@.SacksPage.num((long) moved2) + " items") : "-Nothing to deposit (or this category is full)";
  if ("Farming".equals(cat) && !@PKG@.SackDefs.COOKED_FARM && @PKG@.SweepTask.cookedHeld(p.getInventory()) > 0) r2 = r2 + " - cooked food stays in your inventory";
  return r2;
}""", r"""
public static long upNum(String a) {
  try { return Long.parseLong(a.trim()); } catch (Throwable t) { return -9L; }
}""", r"""
public static String upAct(String op, java.util.UUID u, String tok, String pk, String arg) {
  boolean up = "up".equals(op);
  boolean cb = "cmpbuy".equals(op);
  boolean ct = "cmptog".equals(op);
  boolean lb = "lnkbuy".equals(op);
  boolean lt = "lnktog".equals(op);
  boolean rf = "refill".equals(op);
  boolean ta = "takeall".equals(op);
  boolean dc = "depcat".equals(op);
  boolean de = "depevery".equals(op);
  if (!(up || cb || ct || lb || lt || rf || ta || dc || de)) return "-Unknown pocket action";
  @PLA@ p = playerOf(u);
  if (p == null) return null;
  String us = u.toString();
  String old = "=That click was for an older copy of this view - nothing was done. It is up to date now - click again if you meant it";
  Object o = UPTOK.get(us);
  Object[] rec = null;
  if (o instanceof Object[]) rec = (Object[]) o;
  if (rec == null || tok == null || !tok.equals(rec[0])) return old;
  String k = @PKG@.SackPool.settledKey(u);
  if (k == null) return "-The Void is paused (profile loading or switching) - try again in a moment";
  String vk = (String) rec[1];
  if (pk == null || !pk.equals(vk) || !k.equals(vk)) return "=Your profile changed - the view now shows it; nothing was done";
  int ci = ((Integer) rec[2]).intValue();
  String cn = @PKG@.SackDefs.CATS[ci];
  String a = arg == null ? "" : arg.trim();
  int from = -1;
  long shown = -9L;
  int rm = -1;
  if (up) {
    from = (int) upNum(a);
    if (from != ((Integer) rec[3]).intValue()) return old;
    int cur = @PKG@.VoidStore.rarOf(k, ci);
    if (cur != from) return "=Already upgraded - " + cn + " is " + @PKG@.SackDefs.RNAME[cur] + " now (nothing was taken)";
    if (!upCost(k, ci).equals(rec[4])) return "=The upgrade cost changed since you looked - check it, then Pay again (nothing was taken)";
  }
  if (cb || lb) {
    shown = upNum(a);
    int ri = 7;
    if (cb) ri = 5;
    if (shown != ((Long) rec[ri]).longValue()) return old;
    long now = @PKG@.VoidLink.price(ci);
    if (cb) now = @PKG@.VoidCompact.price(ci);
    if (now != shown) return "=The price is now " + @PKG@.SacksPage.num(now) + " coins - check it, then Pay again (nothing was taken)";
    if (lb) {
      String lc = "";
      if (@PKG@.VoidLink.linkable(ci)) lc = @PKG@.VoidLink.costText(ci);
      if (lc == null) lc = "";
      if (!lc.equals(rec[8])) return "=The Shard Link item cost changed since you looked - check it, then Pay again (nothing was taken)";
    }
    if (!"buy".equals(rec[ri == 5 ? 6 : 9])) return old;   // the view showed no Buy there (rec 6 = compact state, 9 = link state)
    String st = lnkSt(k, ci);
    if (cb) st = cmpSt(k, ci);
    if (!"buy".equals(st)) return "=" + (cb ? "Auto-compact" : "Shard Link") + " for " + cn + " changed since you looked - the view now shows it (nothing was taken)";
  }
  if (ct || lt) {
    int si = 9;
    if (ct) si = 6;
    if (!a.equals(rec[si]) || !("on".equals(a) || "paused".equals(a))) return old;
    String st2 = lnkSt(k, ci);
    if (ct) st2 = cmpSt(k, ci);
    if (!a.equals(st2)) return "=" + (ct ? "Auto-compact" : "Shard Link") + " for " + cn + " changed since you looked - the view now shows it (nothing changed)";
    if (ct && !@PKG@.SackCfg.CMP_ON) return "-Auto-compact is switched off on this server";
  }
  if (rf) {
    rm = @PKG@.RefillPref.parse(a);
    if (rm < 0) return "-Unknown stack refill choice";
    if (@PKG@.RefillPref.choice(u) != ((Integer) rec[10]).intValue()) return "=Your stack refill choice changed since you looked - the view now shows it (nothing changed)";
  }
  if (!UPTOK.remove(us, rec)) return old;
  String r = null;
  try {
    if (up) {
      r = @PKG@.VoidStore.upgrade(p, u, k, ci, from);
      @PKG@.SackSnd.ok(u, r, 1);
    } else if (cb) {
      r = @PKG@.VoidCompact.buyAt(u, k, ci, shown);
      if (r != null && r.startsWith("+")) {
        long cm = @PKG@.VoidCompact.runNow(u, k);
        if (cm > 0L) r = r + " - " + @PKG@.SacksPage.num(cm) + " Enchanted made now";
      }
      @PKG@.SackSnd.ok(u, r, 1);
    } else if (ct) {
      r = @PKG@.VoidCompact.toggle(u, k, ci);
      if (r != null && r.startsWith("+")) {
        long cm2 = @PKG@.VoidCompact.runNow(u, k);
        if (cm2 > 0L) r = r + " - " + @PKG@.SacksPage.num(cm2) + " Enchanted made now";
      }
    } else if (lb) {
      r = @PKG@.VoidLink.buyAt(p, u, k, ci, shown);
      @PKG@.SackSnd.ok(u, r, 1);
    } else if (lt) {
      r = @PKG@.VoidLink.toggle(u, k, ci);
    } else if (rf) {
      @PKG@.RefillPref.set(u, rm);
      r = "+Stack refill: " + @PKG@.RefillPref.LABELS[rm] + (@PKG@.SackCfg.REFILL_ON ? "" : " (turned off on this server for now)");
      @PKG@.SackPool.saveSoon((String) null);
    } else if (ta) {
      r = upTakeAll(p, k, cn);
      @PKG@.SackPool.saveSoon(k);
    } else {
      String dcat = null;
      if (dc) dcat = cn;
      r = upDeposit(p, u, k, dcat);
      @PKG@.SackPool.saveSoon(k);
    }
    // the page answers a Pause with '=' (a note); here '=' means "nothing was done" - a Pause that happened is '+'
    if ((ct || lt) && r != null && r.startsWith("=") && r.indexOf(" paused for ") > 0) r = "+" + r.substring(1);
  } catch (Throwable t) {
    @PKG@.SackPool.saveSoon(k);
    @PKG@.KnowSync.warnOnce("pocket upgrade action " + op + " failed: " + t);
    return "-That did not finish - check your bag, the Void and your coins (nothing more will move)";
  }
  return r == null ? "-That did not finish - nothing was done" : r;
}"""]
P.rep('''sbr.addMethod(CtNewMethod.make(jt(r"""
public static Object fishCall(int mode, Object o) {''', "# 0.8.43 (tools/sacks_0_8_43_patch.py): SkyyMenu 0.3.78's in-screen pocket UPGRADES view - sacks:fn:upView / upAct (the Void page's side panel)\n"
      + "".join('sbr.addMethod(CtNewMethod.make(jt(r"""%s"""), sbr))\n' % j for j in UP_JAVA) + '''sbr.addMethod(CtNewMethod.make(jt(r"""
public static Object fishCall(int mode, Object o) {''')

# ---- SackFn: modes 26 / 27 (before the 0.8.40 modes; bad arguments = null)
P.rep('''    if (this.mode == 23 || this.mode == 24) {   // 0.8.40 sacks:fn:furnList {UUID, bench, sel, search} / sacks:fn:furn {UUID, bench, op, arg, amount, token}''',
      '''    if (this.mode == 26) {   // 0.8.43 sacks:fn:upView {UUID, pocket} -> String / null
      if (!(o instanceof Object[])) return null;
      Object[] a26 = (Object[]) o;
      if (a26.length < 2 || !(a26[0] instanceof java.util.UUID) || !(a26[1] instanceof String)) return null;
      return @PKG@.SackBridge.upView((java.util.UUID) a26[0], (String) a26[1]);
    }
    if (this.mode == 27) {   // 0.8.43 sacks:fn:upAct {op, UUID, token, profile key, arg} -> String / null
      if (!(o instanceof Object[])) return null;
      Object[] a27 = (Object[]) o;
      if (a27.length < 2 || !(a27[0] instanceof String) || !(a27[1] instanceof java.util.UUID)) return null;
      for (int i27 = 2; i27 < a27.length && i27 < 5; i27++) { if (a27[i27] != null && !(a27[i27] instanceof String)) return null; }
      return @PKG@.SackBridge.upAct((String) a27[0], (java.util.UUID) a27[1], a27.length > 2 ? (String) a27[2] : (String) null,
          a27.length > 3 ? (String) a27[3] : (String) null, a27.length > 4 ? (String) a27[4] : (String) null);
    }
    if (this.mode == 23 || this.mode == 24) {   // 0.8.40 sacks:fn:furnList {UUID, bench, sel, search} / sacks:fn:furn {UUID, bench, op, arg, amount, token}''')
P.rep('''|| this.mode == 20 || this.mode == 21 || this.mode == 23 || this.mode == 24) ? null :''',
      '''|| this.mode == 20 || this.mode == 21 || this.mode == 23 || this.mode == 24 || this.mode == 26 || this.mode == 27) ? null :''')
P.rep('''  sbr0.put("sacks:fn:link", new {PKG}.SackFn(25));       // 0.8.42: Shard Link (state / room / put / done / ack; SkyyShards 0.4.33)
''', '''  sbr0.put("sacks:fn:link", new {PKG}.SackFn(25));       // 0.8.42: Shard Link (state / room / put / done / ack; SkyyShards 0.4.33)
  sbr0.put("sacks:fn:upView", new {PKG}.SackFn(26));     // 0.8.43: SkyyMenu's in-screen pocket Upgrades view (a new click token per read)
  sbr0.put("sacks:fn:upAct", new {PKG}.SackFn(27));      // 0.8.43: its buttons (the Void page's own code paths; token + profile key)
''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0 and P.s.count("makeClass(") == CLS0, "0.8.43: no class / system / command"
_i = P.s.index
assert _i("public static String fclean(String s)") < _i("public static String upView(java.util.UUID u, String cat)") < _i("public static String upAct(String op")\
    < _i("public static Object fishCall(int mode, Object o)") < _i("public Object apply(Object o) {\n  if (this.mode == 25)"), "0.8.43: methods before callers"
P.finish()
print("tools/sacks_0_8_43_patch.py: wrote", P.dst)
