"""Derive SkyySacks/build_skyysacks_0.8.38.py from the SET pin 0.8.37 (the GENERATED build_skyysacks_0.8.37.py; edit THIS file, then
regenerate: python tools/sacks_0_8_38_patch.py; never re-run sacks_0_8_37_patch.py on top of it). Every anchor is asserted once; at the end
every change is undone on a copy and compared with 0.8.37 (nothing else changed). Line endings kept.
Run:  python tools/sacks_0_8_38_patch.py   then   python SkyySacks/build_skyysacks_0.8.38.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.8.38.py [--dir <folder inside tools/dev/scratch/>] [--keep]

0.8.38 (2026-11-17, round inv4) = THE POCKET TABS + TANNING BRIDGES for SkyyMenu 0.3.53's inventory screen (Skyy 2026-11-14: "next to it
  have the pocket dimensions. make a new image showing what ittl look like when you pick the mining pocket." -> the approved
  inventory-mockup-mining.png: pocket tabs above the bag, each swapping the top panel for that pocket's grid; "furnace and tanning will have a
  custom look and work more like they do in our pack").
  Three new keys on skyy.bridge (SackFn modes 20 / 21 + a CraftHubOpen), java.lang types only, the player's WORLD THREAD only (playerOf: off
  it they refuse, nothing moves):
  1. sacks:fn:pocketList {UUID, String category} -> String: "ok|<cat>|<level>|<rarity name>|<used>|<space>|<sell open 0/1>|<profile token>"
     (fix pass: the token = the settled profile key, '|' / newline blanked - the caller hands it back to sacks:fn:pocket) then one line
     per item of that pocket "id|count|<unpack 0/1>|<Bazaar price for one, -1 none>" in the Void page's own order (CountCmp, most first;
     at most 400); "off|<reason>" when the Void is paused / the category is unknown; null off the world thread / not a UUID.
  2. sacks:fn:pocket {UUID, String op, String itemId, String amount[, String profile token]} -> the Void page's own result line ("+" done,
     "-" refused; fix pass: a token that is not the settled profile's = "-Your profile changed" and nothing moves - the Void page's own
     "your profile changed" check; a throw inside an action still saves the pool (saveSoon) and answers "-"): op wd =
     Withdraw (SacksPage.withdrawN, the amount box rule: empty = one stack, a number, all), dep = Deposit (VoidStore.depositInv: empty = all
     you carry), sell = Sell (SacksPage.sell: debit -> saved -> bazaar:fn:sell -> unsold back; empty = one stack; a dot refused), unpack =
     Unpack (SacksPage.unpack: Enchanted -> base to the inventory, the rest packed back). EXACTLY the Void page's click branches (same
     gates: the settled profile key, the live-mirror rule inside those methods), then SackPool.saveSoon. Nothing new moves an item or a coin.
  3. sacks:fn:openTannery (UUID -> Boolean; CraftHubOpen("Tannery"), world thread): opens the Tannery sub-tab of the Crafting page - the same
     gate as the sub-tab (a Tanning charm equipped, or the Tannery still holds work); FALSE = not shown (the caller keeps its fallback).
  No saved-data change, no config row, no system / command. ROLLBACK to 0.8.37: safe alone (the three keys disappear; SkyyMenu 0.3.53 then
  falls back to the Void button and the Crafting page).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G   # only its generic Patch helper (anchors asserted once, undo-compare, line endings kept)

P = G.Patch(os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.37.py"), os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.38.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.8.37"\n') and P.has("furnaceKey") and not P.has("pocketList"), "not the live generated SkyySacks 0.8.37"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.8.38 (2026-11-17"):].rstrip() + "\n"

P.rep('''  The Tannery, Crafting, Gear, Farming, Campfire, Collections and the search all still use sortKey / sortName.
  No saved-data change, no config row, no system / command, no bridge key. ROLLBACK to 0.8.36: safe alone (the Furnace list goes back to tier then name; nothing is stored).
''', '''  The Tannery, Crafting, Gear, Farming, Campfire, Collections and the search all still use sortKey / sortName.
  No saved-data change, no config row, no system / command, no bridge key. ROLLBACK to 0.8.36: safe alone (the Furnace list goes back to tier then name; nothing is stored).
''' + NOTE)
P.rep('VERSION = "0.8.37"\n', 'VERSION = "0.8.38"\n')
P.rep('''; Furnace ingots first (0.8.37)");''', '''; Furnace ingots first (0.8.37); pocket tabs + Tannery bridges for the inventory screen (0.8.38)");''')

# ---- SackBridge: the pocket list + the pocket actions (after fishCall: every SacksPage / VoidStore member they use is compiled before)
P.rep('''sbr.addMethod(CtNewMethod.make(jt(r"""
public static Object fishCall(int mode, Object o) {''', '''# 0.8.38 (tools/sacks_0_8_38_patch.py): SkyyMenu 0.3.53's POCKET TABS - the list of one pocket + the Void page's own click branches
sbr.addMethod(CtNewMethod.make(jt(r"""
public static String tok(String k) {
  return k == null ? "" : k.replace('|', ' ').replace('\\n', ' ');
}"""), sbr))
sbr.addMethod(CtNewMethod.make(jt(r"""
public static String pocketList(java.util.UUID u, String cat) {
  @PLA@ p = playerOf(u);
  if (p == null) return null;
  String k = @PKG@.SackPool.settledKey(u);
  if (k == null) return "off|The Void is paused (profile loading or switching) - try again in a moment";
  int ci = @PKG@.SackDefs.catIndex(cat);
  if (ci < 0) return "off|No such pocket";
  String[] cats = @PKG@.SackDefs.CATS;
  int lv = @PKG@.VoidStore.level(u, k, ci);
  int rk = @PKG@.VoidStore.rank(k, ci);
  long cap = @PKG@.VoidStore.capOf(lv, rk);
  long used = @PKG@.VoidStore.usedAll(k)[ci];
  java.util.ArrayList entries = new java.util.ArrayList();
  java.util.Iterator it = @PKG@.SackPool.pool(k).entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    if (cats[ci].equals(@PKG@.SackDefs.homeOf((String) e.getKey()))) entries.add(e);
  }
  java.util.Collections.sort(entries, new @PKG@.CountCmp());
  StringBuilder sb = new StringBuilder();
  sb.append("ok|").append(cats[ci]).append('|').append(lv).append('|').append(@PKG@.SackDefs.RNAME[rk]).append('|').append(used).append('|').append(cap).append('|').append(@PKG@.SacksPage.sellOpen() ? 1 : 0).append('|').append(tok(k));
  int shown = 0;
  for (int i = 0; i < entries.size() && shown < 400; i++) {
    java.util.Map.Entry e = (java.util.Map.Entry) entries.get(i);
    Object v = e.getValue();
    long n = v instanceof Number ? ((Number) v).longValue() : 0L;
    if (n <= 0L) continue;
    String id = (String) e.getKey();
    sb.append('\\n').append(id.replace('|', ' ')).append('|').append(n).append('|').append(@PKG@.VoidCompact.idxEnch(id) >= 0 ? 1 : 0).append('|').append(@PKG@.SacksPage.sellPrice(id));
    shown = shown + 1;
  }
  return sb.toString();
}"""), sbr))
sbr.addMethod(CtNewMethod.make(jt(r"""
public static String pocketAct(java.util.UUID u, String op, String id, String amt, String want) {
  @PLA@ p = playerOf(u);
  if (p == null) return null;
  String k = @PKG@.SackPool.settledKey(u);
  if (k == null) return "-The Void is paused (profile loading or switching) - try again in a moment";
  if (want != null && want.length() > 0 && !want.equals(tok(k))) return "-Your profile changed - the pocket now shows it; pick the item again";
  if (id == null || id.length() == 0) return "-Pick an item in the grid first";
  String r = null;
  try {
  if ("wd".equals(op)) {
    long n = @PKG@.SacksPage.parseAmt(amt, (long) @PKG@.SacksPage.stackOf(id));
    if (n == -2L) return "-Type a number (or leave it empty for one stack)";
    long got = @PKG@.SacksPage.withdrawN(p, k, id, n);
    r = got > 0L ? ("+Took " + @PKG@.SacksPage.num(got) + " " + @PKG@.SacksPage.pretty(id)) : (@PKG@.SackPool.get(k, id) <= 0L ? "-None of it left in the Void" : "-Your storage is full");
  } else if ("dep".equals(op)) {
    long n = @PKG@.SacksPage.parseAmt(amt, -1L);
    if (n == -2L) return "-Type a number (or leave it empty for all you carry)";
    long got = @PKG@.VoidStore.depositInv(p, u, k, id, n);
    r = got > 0L ? ("+Put " + @PKG@.SacksPage.num(got) + " " + @PKG@.SacksPage.pretty(id) + " into the Void") : (got == -1L ? "-That item does not go into the Void" : (got == -2L ? "-This category is full - level it up or upgrade its rarity" : "-You carry none of it (plain stacks only)"));
  } else if ("sell".equals(op)) {
    long sn = (amt != null && amt.indexOf('.') >= 0) ? -2L : @PKG@.SacksPage.parseAmt(amt, (long) @PKG@.SacksPage.stackOf(id));
    if (sn == -2L) return "-Type a number or all (or leave it empty for one stack)";
    r = @PKG@.SacksPage.sell(u, p, k, id, sn);
  } else if ("unpack".equals(op)) {
    if (@PKG@.VoidCompact.idxEnch(id) < 0) return "-Pick an Enchanted item in the grid first";
    long n = @PKG@.SacksPage.parseAmt(amt, 1L);
    if (n == -2L) return "-Type a number (or leave it empty for one)";
    r = @PKG@.SacksPage.unpack(p, k, id, n);
  } else return "-Unknown pocket action";
  } catch (Throwable t) {
    @PKG@.SackPool.saveSoon(k);
    @PKG@.KnowSync.warnOnce("pocket action " + op + " failed: " + t);
    return "-That did not finish - check your bag and the Void (nothing more will move)";
  }
  @PKG@.SackPool.saveSoon(k);
  return r;
}"""), sbr))
sbr.addMethod(CtNewMethod.make(jt(r"""
public static Object fishCall(int mode, Object o) {''')
# ---- SackFn: modes 20 / 21 BEFORE the fish modes (mode >= 14)
P.rep('''    if (this.mode >= 14) return @PKG@.SackBridge.fishCall(this.mode, o);   // 0.8.17: fishList / fishTake / fishPut / fishTaken''',
      '''    if (this.mode == 20 || this.mode == 21) {   // 0.8.38 sacks:fn:pocketList {UUID, cat} / sacks:fn:pocket {UUID, op, id, amount}
      if (!(o instanceof Object[])) return null;
      Object[] a20 = (Object[]) o;
      if (a20.length < 2 || !(a20[0] instanceof java.util.UUID) || !(a20[1] instanceof String)) return null;
      if (this.mode == 20) return @PKG@.SackBridge.pocketList((java.util.UUID) a20[0], (String) a20[1]);
      if (a20.length < 3 || !(a20[2] instanceof String)) return null;
      return @PKG@.SackBridge.pocketAct((java.util.UUID) a20[0], (String) a20[1], (String) a20[2], a20.length > 3 && a20[3] instanceof String ? (String) a20[3] : "",
          a20.length > 4 && a20[4] instanceof String ? (String) a20[4] : null);
    }
    if (this.mode >= 14) return @PKG@.SackBridge.fishCall(this.mode, o);   // 0.8.17: fishList / fishTake / fishPut / fishTaken''')
P.rep('''  return (this.mode == 3 || this.mode == 12 || this.mode == 13 || this.mode == 14 || this.mode == 17 || this.mode == 18) ? null : Long.valueOf(this.mode == 0 ? -1L : 0L);''',
      '''  return (this.mode == 3 || this.mode == 12 || this.mode == 13 || this.mode == 14 || this.mode == 17 || this.mode == 18 || this.mode == 20 || this.mode == 21) ? null : Long.valueOf(this.mode == 0 ? -1L : 0L);   // 0.8.38: the pocket modes answer null on a failure''')
P.rep('''  sbr0.put("sacks:fn:takeOpen", new {PKG}.SackFn(19));   // 0.8.32: take N, loose first, the fewest Enchanted opened, all or nothing
''', '''  sbr0.put("sacks:fn:takeOpen", new {PKG}.SackFn(19));   // 0.8.32: take N, loose first, the fewest Enchanted opened, all or nothing
  sbr0.put("sacks:fn:pocketList", new {PKG}.SackFn(20));   // 0.8.38: SkyyMenu's pocket tabs (one pocket's grid)
  sbr0.put("sacks:fn:pocket", new {PKG}.SackFn(21));       // 0.8.38: Withdraw / Deposit / Sell / Unpack = the Void page's own branches
  sbr0.put("sacks:fn:openTannery", new {PKG}.CraftHubOpen("Tannery"));   // 0.8.38: the inventory's Tanning tab (UUID -> Boolean; world thread)
''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.8.38 adds no system / command"
_i = P.s.index
assert _i("public static long withdrawN(") < _i("public static String sell(@PLA@ p") if "public static String sell(@PLA@ p" in P.s else True
assert _i("public static String tok(") < _i("public static String pocketList(") and _i("public static long withdrawN(") < _i("public static String pocketList(") and _i("public static String unpack(@PLA@ p") < _i("public static String pocketAct("), "0.8.38: methods before callers"
assert _i("public static String pocketAct(") < _i("public static Object fishCall(") < _i("if (this.mode == 20 || this.mode == 21)"), "0.8.38: the bridge methods before SackFn.apply"
P.finish()
