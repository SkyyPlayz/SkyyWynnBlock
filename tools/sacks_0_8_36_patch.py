"""Derive SkyySacks/build_skyysacks_0.8.36.py from the SET pin 0.8.35 (the GENERATED build_skyysacks_0.8.35.py; edit THIS file, then
regenerate: python tools/sacks_0_8_36_patch.py; never re-run sacks_0_8_35_patch.py on top of it). Every anchor is asserted once; at the end
every change is undone on a copy and compared with 0.8.35 (nothing else changed). Line endings kept.
Run:  python tools/sacks_0_8_36_patch.py   then   python SkyySacks/build_skyysacks_0.8.36.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.8.36.py [--dir <folder inside tools/dev/scratch/>] [--keep]

0.8.36 (2026-11-08) = ENCHANTED METALS IN THE SMITHING BAG + SELL ON THE POCKET PAGE + REAL NAMES (tag sk836; docs/answered/bags.md 2026-11-08, Skyy: "enchanted metals should go in
  the smithing bag too." + "add a sell button in here too,").
  1. ENCHANTED METALS -> SMITHING. SackDefs.enchCat: every row of tools/skyyench.py (TABLE + TABLE_ALLOYS) whose base is an Ingredient_Bar_* is Smithing here, where the plain bars
     live: Copper, Iron, Thorium, Cobalt, Adamantite, Silver, Gold, Mithril, Lead, Chromium, Slag, Titanium + the 6 alloys (18 ids). skyyench.py itself keeps its Mining column
     (SkyyCollections' page and SkyyBazaar read it). Enchanted Charcoal was Smithing already. No other row changes: every other Enchanted item already lives in its base's bag.
     NO DATA MOVES AND NO MIGRATION: the pool is ONE id -> count map per profile (pools/<key>.properties) and the bag is only SackDefs.homeOf(id), so held stock shows in Smithing the moment
     this jar runs, for every profile, online or not, once, by construction (as the hides 0.7.5, fabric 0.8.9 and saplings 0.8.16 moves). Nothing is written, so nothing can be lost or
     counted twice: bag levels come from coll:fn:catTotal / own.<Cat>, which only intake raises. Stock past Smithing's space stays held; the page shows its usual over-the-limit line and
     only NEW items wait (no code ever trims a pool). Auto-compact: pair and base were in one upgrade already (the base's bag); base and Enchanted now share a bag, so its room check is skipped.
  2. SELL (Storage -> Pocket, new row under Pick up all, Unpack beside it - shortened from "Unpack to inventory" to fit; the row is always drawn, so selecting an item no longer shifts the
     boxes below). SacksPage.sell: the selected item, the AMOUNT box (empty = one stack, a number = that many, all = everything; more than held sells what is held and says so). bazaar:fn:sell
     (apply(Object[]{UUID, itemId, Long qty}) -> Long coins or long[]{coins, sold}). DEBIT FIRST (read + debit under SackPool.class, BagMirror.beforeTake / afterTake), then pay; 0 / a throw / nothing sold =
     all back; part sold = only that part leaves. Whole fish (weights) are refused: they sell at the Fishing Bench. Bridge missing, no bazaar:sell:<id> price or a price of 0 = a status message and nothing moves.
     The status line shows the price for one (bazaar:sell:<id>) while it has nothing else to say (one item's price, not a total: the Bazaar's walk-the-book quote is not on the bridge). crafts.log: VOID-SELL / VOID-SELL-REFUSED. No Skills XP (only the shard Sell pays XP).
     Fixes: an amount with a dot (1.5) is refused here, because Sell cannot be undone (Withdraw / Deposit still ignore dots). The debit is ON DISK before the Bazaar pays (SackPool.saveOk, as sacks:fn:fishTake; it cannot be written = all back, nothing sold), and any items that come back are written at once too: a crash can no longer leave both the coins and the items.
     Unpack's result line now says the items went to your inventory (the shorter button label no longer does).
  3. REAL NAMES. SacksPage.pretty only tidied the id (it never asked for a translation; CraftPage.pretty does since 0.8.8), so the title, +Took and +Put read "Skyy Ench Lead". It now asks SackDefs.dname first.
  No saved-data change, no config row, no system / command, no new bridge key. ROLLBACK to 0.8.35: safe alone (the metals show in Mining again - same pool, nothing moved; the Sell button goes).
  BAZAAR: its next build reads this jar's homes (BAG_OF) and asserts BAG_OF == EN.cat_of for the frozen id lists, so a Bazaar round built on this pin must follow the move (its Mining tab -> Smithing).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G   # only its generic Patch helper (anchors asserted once, undo-compare, line endings kept)

P = G.Patch(os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.35.py"), os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.36.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.8.35"\n') and P.has("countMats") and not P.has("VOID-SELL"), "not the live generated SkyySacks 0.8.35"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.8.36 (2026-11-08)"):].rstrip() + "\n"

P.rep('''  stops drawing its Furnace button when the bridge key is missing).
"""
''', '''  stops drawing its Furnace button when the bridge key is missing).
''' + NOTE + '''"""
''')
P.rep('VERSION = "0.8.35"\n', 'VERSION = "0.8.36"\n')
P.rep('''; All really adds all, Furnace button bridge (0.8.35)");''', '''; All really adds all, Furnace button bridge (0.8.35); Enchanted metals in Smithing, Pocket Sell, real names (0.8.36)");''')

# ---- 1. Enchanted metals -> Smithing (tools/skyyench.py keeps its Mining column: Collections and the Bazaar read it)
P.rep('''_HOME_TABLE = list(EN.TABLE) + list(EN.TABLE_ALLOYS)
''', '''_HOME_TABLE = list(EN.TABLE) + list(EN.TABLE_ALLOYS)
# 0.8.36 (Skyy "enchanted metals should go in the smithing bag too."): an Enchanted row made from a bar lives where the bar lives; held stock simply shows there (one pool, keyed by id)
METAL_ENCH = [EN.PREFIX + _t[0] for _t in _HOME_TABLE if _t[2].startswith("Ingredient_Bar_")]
assert len(METAL_ENCH) == 18 and "Skyy_Ench_Lead" in METAL_ENCH and "Skyy_Ench_Electrum" in METAL_ENCH and "Skyy_Ench_Charcoal" not in METAL_ENCH, METAL_ENCH
assert all(_t[5] == "Mining" for _t in _HOME_TABLE if _t[2].startswith("Ingredient_Bar_")), "0.8.36: a metal row is no longer Mining in tools/skyyench.py - re-check this override"
_HOME_TABLE = [_t[:5] + ("Smithing",) + _t[6:] if _t[2].startswith("Ingredient_Bar_") else _t for _t in _HOME_TABLE]
''')
P.rep('''    print("Enchanted alloys -> Mining: %s (all in SkyyCollections 0.2.28)" % ", ".join(ALLOY_ENCH))
''', '''    print("Enchanted alloys -> Smithing: %s (all in SkyyCollections 0.2.28)" % ", ".join(ALLOY_ENCH))
''')

# ---- 3. the real names (every pretty() of this page: the title, +Took, +Put, Unpack's fallback)
P.rep("""public static String pretty(String id) {
  if (id == null) return "";
  String s = id;
  if (s.startsWith("Ingredient_")) s = s.substring(11);
  if (s.endsWith("_Item")) s = s.substring(0, s.length() - 5);
  return s.replace('_', ' ');
}'''), page))
# the first category with something stored, else Mining
""", """public static String pretty(String id) {
  if (id == null) return "";
  String dn = @PKG@.SackDefs.dname(id);   // 0.8.36: the item's real name (Enchanted Lead Ingot); the tidied id only when it has none
  if (dn != null) return dn;
  String s = id;
  if (s.startsWith("Ingredient_")) s = s.substring(11);
  if (s.endsWith("_Item")) s = s.substring(0, s.length() - 5);
  return s.replace('_', ' ');
}'''), page))
# the first category with something stored, else Mining
""")

# ---- 2. Sell: the button
P.rep('''    "unpack": SUI.button("SkyyVUnpack", "Unpack to inventory", "secondary", w=V_SIDE_W),
''', '''    # 0.8.36: Sell + Unpack share the third row, on the same 156 + 6 + 178 grid as the row above; the row is always there
    "sellb": SUI.choose("sel != null", SUI.button("SkyyVSell", "Sell", "secondary", w=156), SUI.button("SkyyVSell", "Sell", "secondary", w=156, disabled=True)),
    "unpack": SUI.button("SkyyVUnpack", "Unpack", "secondary", w=178, anchor={"left": 6}),
''')
P.rep('''  if (sel != null && @PKG@.VoidCompact.idxEnch(sel) >= 0) {   // 0.8.30: Unpack a selected Enchanted item
    b.appendInline("#SkyyVSide", @@btns3@@);
    b.appendInline("#SkyyVBtnsC", @@unpack@@);
''', '''  b.appendInline("#SkyyVSide", @@btns3@@);   // 0.8.36: always drawn - Sell (no item picked: greyed, no event)
  b.appendInline("#SkyyVBtnsC", @@sellb@@);
  if (sel != null) ev.addEventBinding(@BT@.Activating, "#SkyyVSell", amtEvt("sell"));
  if (sel != null && @PKG@.VoidCompact.idxEnch(sel) >= 0) {   // 0.8.30: Unpack a selected Enchanted item
    b.appendInline("#SkyyVBtnsC", @@unpack@@);
''')
P.rep('''"Click an item in the grid, type an amount, then Withdraw or Deposit."''', '''"Click an item in the grid, type an amount, then Withdraw, Deposit or Sell."''')
P.rep('''  b.appendInline("#SkyySBody", @@info@@);
  b.set("#SkyySInfo.Text", textOf(this.info));
  refillRow(b, ev, @PKG@.RefillPref.choice(u));
''', '''  String info0 = this.info;   // 0.8.36: an empty result line shows the selected item's price (this one build only)
  if ((info0 == null || info0.length() == 0) && sel != null) this.info = sellHint(sel);
  b.appendInline("#SkyySBody", @@info@@);
  b.set("#SkyySInfo.Text", textOf(this.info));
  this.info = info0;
  refillRow(b, ev, @PKG@.RefillPref.choice(u));
''')

# ---- 2. Sell: the sale (before render / onEvent, its callers)
P.rep('''# 0.8.30 UNPACK: n Enchanted items -> RATIO x n base items''', '''# 0.8.36 SELL: what the Bazaar pays for one (bazaar:sell:<id>, published for every product); -1 = no price
page.addMethod(CtNewMethod.make(jt(r\'\'\'
public static long sellPrice(String id) {
  try {
    Object o = id == null ? null : @PKG@.SackPool.bridge().get("bazaar:sell:" + id);
    return o instanceof Number ? ((Number) o).longValue() : -1L;
  } catch (Throwable t) { return -1L; }
}\'\'\'), page))
page.addMethod(CtNewMethod.make(jt(r\'\'\'
public static boolean sellOpen() {
  try { return @PKG@.SackPool.bridge().get("bazaar:fn:sell") instanceof java.util.function.Function; } catch (Throwable t) { return false; }
}\'\'\'), page))
# the result line while it has nothing else to say ("" = stay empty)
page.addMethod(CtNewMethod.make(jt(r\'\'\'
public static String sellHint(String id) {
  if (!sellOpen() || @PKG@.SackDefs.isCatch(id)) return "";
  long p = sellPrice(id);
  return p > 0L ? "=The Bazaar pays about " + num(p) + " coins each" : "";
}\'\'\'), page))
# the debit: one SackPool lock for the read + the take (a synchronized block holds one call: sellDebit0)
page.addMethod(CtNewMethod.make(jt(r\'\'\'
public static long sellDebit0(String k, String id, long want) {
  long h = @PKG@.SackPool.get(k, id);
  long n = h < want ? h : want;
  if (n <= 0L) return 0L;
  @PKG@.SackPool.add(k, id, -n);
  return n;
}\'\'\'), page))
page.addMethod(CtNewMethod.make(jt(r\'\'\'
public static long sellDebit(String k, String id, long want) {
  synchronized (@PKG@.SackPool.class) { return sellDebit0(k, id, want); }
}\'\'\'), page))
# THE SALE (world thread, the page's click): debit, then pay; whatever was not reported sold goes back to the pool it left. want = the amount box (Long.MAX_VALUE = all).
page.addMethod(CtNewMethod.make(jt(r\'\'\'
public static String sell(java.util.UUID u, @PLA@ p, String k, String id, long want) {
  String nm = pretty(id);
  if (@PKG@.SackDefs.isCatch(id)) return "-Whole fish sell at the Fishing Bench, by weight - nothing was sold";
  String cat = @PKG@.SackDefs.homeOf(id);
  if (cat == null || p == null || !@PKG@.SweepTask.caps(p.getInventory()).containsKey(cat)) return "-" + nm + " cannot be sold from here - nothing was sold";
  Object f0 = @PKG@.SackPool.bridge().get("bazaar:fn:sell");
  if (!(f0 instanceof java.util.function.Function)) return "-The Bazaar cannot buy from the Void yet - nothing was sold";
  if (sellPrice(id) <= 0L) return "-The Bazaar does not buy " + nm + " right now - nothing was sold";
  @PKG@.BagMirror.beforeTake(k);   // live-mirror rule: book an open bench's use first
  long n = sellDebit(k, id, want);
  if (n <= 0L) return "-None of it left in the Void";
  try { @PKG@.BagMirror.afterTake(k, id); } catch (Throwable t1) { @PKG@.SackPool.warn("Void sale: mirror trim failed: " + t1); }
  if (!@PKG@.SackPool.saveOk(k)) {   // the debit reaches the disk BEFORE the coins exist (a crash cannot leave both)
    @PKG@.SackPool.add(k, id, n);
    @PKG@.SackPool.warn("Void sale: the pool of " + k + " could not be written, " + n + " " + id + " stay in the Void");
    try { @PKG@.CraftLog.later(k, "VOID-SELL-REFUSED " + id + " sold 0 of " + n + " (pool file not written), " + n + " back in the Void"); } catch (Throwable t4) { }
    return "-The Void could not be saved right now - nothing was sold";
  }
  long coins = 0L;
  long sold = 0L;
  try {
    Object r = ((java.util.function.Function) f0).apply(new Object[] { u, id, Long.valueOf(n) });
    if (r instanceof Number) { coins = ((Number) r).longValue(); sold = n; }
    else if (r instanceof long[] && ((long[]) r).length >= 2) { coins = ((long[]) r)[0]; sold = ((long[]) r)[1]; }
  } catch (Throwable t2) { coins = 0L; sold = 0L; @PKG@.SackPool.warn("bazaar:fn:sell failed, " + n + " " + id + " go back to the Void: " + t2); }
  if (coins > 0L && sold <= 0L) @PKG@.SackPool.warn("bazaar:fn:sell paid " + coins + " coins for nothing sold (" + id + " x" + n + ") - the items stay in the Void");
  if (sold > n) { @PKG@.SackPool.warn("bazaar:fn:sell reported " + sold + " sold of " + n + " " + id); sold = n; }
  if (coins <= 0L || sold <= 0L) sold = 0L;
  long back = n - sold;
  if (back > 0L) { @PKG@.SackPool.add(k, id, back); @PKG@.SackPool.save(k); }   // what came back is on disk at once too
  try { @PKG@.CraftLog.later(k, (sold > 0L ? "VOID-SELL " : "VOID-SELL-REFUSED ") + id + " sold " + sold + " of " + n + " for " + coins + " coins, " + back + " back in the Void"); } catch (Throwable t3) { }
  if (sold <= 0L) return "-The Bazaar would not buy " + nm + " right now - nothing was sold";
  String msg = "+Sold " + num(sold) + " " + nm + " for " + num(coins) + " coins";
  if (sold < n) msg = msg + " - the Bazaar took only that many, " + num(back) + " stay in the Void";
  else if (want != 9223372036854775807L && want > n) msg = msg + " (you only had " + num(n) + ")";
  return msg;
}\'\'\'), page))
# 0.8.30 UNPACK: n Enchanted items -> RATIO x n base items''')
P.rep('''    boolean wd = a.equals("wd");
    boolean dep = a.equals("dep");
''', '''    if (a.equals("sell")) {   // 0.8.36: the amount box - empty = one stack, a number, all
      String samt = field(data, "@Amt");
      this.amount = samt;
      String sid = this.sel;
      if (sid == null) { this.info = "-Pick an item in the grid first"; rebuild(); return; }
      long sn = (samt != null && samt.indexOf('.') >= 0) ? -2L : parseAmt(samt, (long) stackOf(sid));   // parseAmt skips dots: 1.5 would sell 15, and a sale cannot be undone
      if (sn == -2L) { this.info = "-Type a number or all (or leave it empty for one stack)"; rebuild(); return; }
      this.info = sell(u, player, k, sid, sn);
      @PKG@.SackPool.saveSoon(k);
      rebuild();
      return;
    }
    boolean wd = a.equals("wd");
    boolean dep = a.equals("dep");
''')

P.rep('''  return "+Unpacked " + num(got) + " " + nm + (loose > 0L ?''', '''  return "+Unpacked " + num(got) + " " + nm + " to your inventory" + (loose > 0L ?''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.8.36 adds no system / command"
_i = P.s.index
assert _i("public static long sellPrice(") < _i("public static String sellHint(") < _i("public static long sellDebit(") < _i("public static String sell(java.util.UUID u") < _i("public void render(@UCB@ b") < _i("public void onEvent(@REF@ ref"), "0.8.36: methods before their callers"
P.finish()
