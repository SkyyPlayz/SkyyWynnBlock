"""Derive SkyyBazaar/build_skyybazaar_0.1.5.py from the LIVE 0.1.4 (build_skyybazaar_0.1.4.py = the tools/deploy_set.py SET pin; 0.1.4 and
every older script stay untouched).
Run:  python tools/bazaar_0_1_5_patch.py   then   python SkyyBazaar/build_skyybazaar_0.1.5.py   (never --deploy: coordinated deploy)
SkyyBazaar uses patch scripts (0.1.1 .. 0.1.4 came from tools/bazaar_0_1_1_patch.py .. tools/bazaar_0_1_4_patch.py): edit THIS file,
never the generated build script.

0.1.5 = three asks from Skyy (2026-10-05, docs/answered/economy.md 'New answers'):
 (A) "i tried to sell all my sap to the bizzar. but its in my bag. you should be able to sell from your bags." -> Sell 1 / Sell <stack> /
     Sell all / the custom Sell / Sell inventory also take matching items out of the Magic Bags the player carries, through SkyySacks 0.7.13's
     bag bridge (sacks:fn:count / all / take / put on skyy.bridge, plain java types, world thread only - tools/sacks_0_7_13_patch.py).
     ORDER: the inventory first, then the bags. Why: what you carry loose is what you are selling right now (a sale never reaches into the
     storage while loose items of that kind are on you), the bags are the reserve - and the SkyySacks sweep would put loose items of a bag
     type into the bag within 2 s anyway, so the order never strands anything. Coins are paid ONLY for what really left: the inventory part
     is measured by re-counting (0.1.4's rule), the bag part is what sacks:fn:take reports as removed from the pool; a partial take pays the
     quote of the real total. If the payment then fails, the bag part goes back through sacks:fn:put (it only returns what a take removed
     in the last 60 s - never a source of items) and anything it does not take goes to the inventory (0.1.4's give-back + alert + log).
     The bags are saved like every other bag change (SkyySacks marks the profile key dirty + saveSoon; per profile through
     SackPool.settledKey). Without SkyySacks, or with one older than 0.7.13 (no sacks:fn:take), every path is exactly 0.1.4's.
     LOCKED rule kept: Magic Bags themselves are never traded - any Skyy_Sack_* id is refused by buy0 / sell0 (an admin line in
     products.properties cannot make Sell inventory sell a bag), and SkyySacks never holds a bag inside a bag.
     The page counts the bags too: the grid cell number and the "You hold" line show inventory + bags ("You hold 120 (100 in your bags)"),
     the limits line / max / all / Sell all / Sell inventory use the total; Sell inventory's confirm says how many come from the bags.
 (B) "with how little seems to drop, id raise the price on sap" -> Tree Sap (Ingredient_Tree_Sap) DEFAULT 4 -> 12 (PRICE_015). Only the pack
     default (the seed line a fresh install or a missing line gets): products.properties is the price on a running server and is never
     rewritten for it - Skyy's live /bazaaradmin price Ingredient_Tree_Sap 12 (or any other saved price) stays as it is. The one exception is
     0.1.3's own one-time update for a server still on 0.1.2 data: it moves every line still holding its 0.1.2 default to the current seed
     line, so a 0.1.2 sap line at 4 becomes 12 there (hand-set values stay, as always). The money-loop checks re-run on the new table.
 (C) "in the bizzar, id use hytale stack numbers instead of Minecraft" -> Buy 64 / Sell 64 become Buy <stack> / Sell <stack>: the item's
     REAL max stack read at run time from the engine's Item asset (Item.getMaxStack - the engine already applied the Parent inheritance and
     Item.processConfig's default: no MaxStack and no tool / weapon / armor / builder tool -> 100, else 1); 0 / unknown -> 100 (the
     engine's plain-item default), never above the per-trade limit. The button label shows the number ("Buy 25"), drawn inline like the tab
     names (a sentinel in the kit markup replaced by the number); the "for 64" price lines use the same stack. Ids / payloads: #SkyyBzBuyStk
     / #SkyyBzSellStk, buystk / sellstk.
REVIEW FIXES (2026-10-06): (1) after a PAID sale the bag part is committed (sacks:fn:commit) so it leaves SkyySacks' refund ledger - a
later sacks:fn:put can never return paid items; (2) SkyySacks' put now returns into the pool the take debited (a pause that starts
mid-sale cannot strand bag items when the inventory is full); (3) a grid cell shows counts of 10,000,000+ as "12.3M" (the cell label
fits 7 digits; the "You hold" line keeps the exact number).
Unchanged and asserted byte-identical below: BzUtil, Coins, Product, Market, Inv, the Catalog Java (only its generated SEED table holds
the new sap line), the price model / loop checks, the admin commands, the tick.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyBazaar", "build_skyybazaar_0.1.4.py")
dst = os.path.join(ROOT, "SkyyBazaar", "build_skyybazaar_0.1.5.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
assert 'VERSION = "0.1.4"' in s and "Bags" not in s and "sacks:fn:" not in s, "the source must be the generated 0.1.4 script"
REG0 = s.count("registerCommand(")


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d != %d: %s" % (n, count, old[:120])
    s = s.replace(old, new)


def block(a, b):
    assert s.count(a) == 1 and s.count(b) == 1, (a[:60], b[:60])
    return s[s.index(a):s.index(b)]


def method(sig, cls="trd"):
    """the whole addMethod(...) statement of the Java method whose header line is sig"""
    i = s.index(sig)
    a = s.rindex("%s.addMethod(CtNewMethod.make(" % cls, 0, i)
    b = s.index('""", %s))' % cls, i) + len('""", %s))' % cls) + 1
    assert s.count(sig) == 1
    return s[a:b]


KEEP = [block("# ================= BzUtil =================", "# ================= Coins (SkyyCoins bridge; copied from SkyyBank) ================="),
        block("# ================= Coins (SkyyCoins bridge; copied from SkyyBank) =================", "# ================= Product ="),
        block("# ================= Product =", "# ================= Catalog (0.1.3"),
        block("# ================= Catalog (0.1.3", "# ================= Market (factors"),
        block("# ================= Market (factors", "# ================= 0.1.3 BzCfg (the premium)"),
        block("# ================= Inv (count-verified inventory moves; world thread only) =================", "# ================= TradeResult ="),
        block("def check_assets(products, spread):", "# ================= 0.1.3 build-time pipeline"),
        block("def asset_model(js, data, drops, recfiles):", "def bag_items(js, data, drops, M, lang):"),
        block("def processed_table(M, products):", "MODEL = asset_model(JS, DATA, DROPS, RECFILES)"),
        block("# ================= /bazaaradmin =================", "# ================= plugin =")]

# ================================================================================================================ docstring + version
rep('''"""SkyyBazaar 0.1.4 - build script (javassist via jpype). Hypixel-Bazaar-style commodity market, MVP = INSTANT buy/sell against a
server market maker.
Run:   python build_skyybazaar_0.1.4.py            -> SkyyBazaar/SkyyBazaar-0.1.4.jar   (build only; deploys go through
       tools/deploy_set.py --yes, never --deploy)
       (0.1.4 is GENERATED from build_skyybazaar_0.1.3.py by tools/bazaar_0_1_4_patch.py - edit the patch, not this file; 0.1.3 came
       from 0.1.2 by tools/bazaar_0_1_3_patch.py, 0.1.2 from 0.1.1, 0.1.1 from 0.1; every older script is kept as it was)
''', '''"""SkyyBazaar 0.1.5 - build script (javassist via jpype). Hypixel-Bazaar-style commodity market, MVP = INSTANT buy/sell against a
server market maker.
Run:   python build_skyybazaar_0.1.5.py            -> SkyyBazaar/SkyyBazaar-0.1.5.jar   (build only; deploys go through
       tools/deploy_set.py --yes, never --deploy)
       (0.1.5 is GENERATED from build_skyybazaar_0.1.4.py by tools/bazaar_0_1_5_patch.py - edit the patch, not this file; 0.1.4 came
       from 0.1.3 by tools/bazaar_0_1_4_patch.py, 0.1.3 from 0.1.2, 0.1.2 from 0.1.1, 0.1.1 from 0.1; every older script is kept as it was)

0.1.5 (2026-10-06) - SELL FROM THE BAGS, HYTALE STACKS, SAP 12 (Skyy 2026-10-05, docs/answered/economy.md 'New answers'; details in the
tools/bazaar_0_1_5_patch.py docstring):
 - (A) "you should be able to sell from your bags": Sell 1 / Sell <stack> / Sell all / the custom Sell / Sell inventory take the inventory
   first, then the Magic Bags the player carries, through SkyySacks 0.7.13's bridge (sacks:fn:count / all / take / put; world thread,
   per profile, live-mirror rule, saved like any bag change). Coins only for what really left (inventory re-counted, bags = what
   sacks:fn:take reports); a failed payment puts the bag part back through sacks:fn:put (only what a take removed) and the rest into the
   inventory. No SkyySacks / an older one = 0.1.4 behaviour. Magic Bags (Skyy_Sack_*) are refused by buy0 / sell0 (locked rule). The page
   counts inventory + bags (cells, "You hold N (M in your bags)", limits, max / all); trades.log SELL lines end " bags=<n>" when bags paid.
 - (B) Tree Sap default 4 -> 12 (PRICE_015): the pack default only; saved prices (Skyy's live /bazaaradmin price ... 12, any hand edit) stay.
 - (C) Buy 64 / Sell 64 -> Buy <stack> / Sell <stack> = the item's real Hytale max stack (Item.getMaxStack at run time: ores 25, most
   blocks 100, food 25 ...; 0 / unknown -> 100, the engine's plain-item default), shown on the button and in the price lines.
''')
rep('VERSION = "0.1.4"', 'VERSION = "0.1.5"')

# ================================================================================================================ (B) sap 4 -> 12
rep('''    ("Ingredient_Tree_Sap", 4, "Tree Sap"),''', '''    ("Ingredient_Tree_Sap", 12, "Tree Sap"),     # 0.1.5 (Skyy 2026-10-05): 4 -> 12 (PRICE_015)''')
rep('''}
# the vanilla farming path (Farmingbench RequiredTierLevel of the normal seed recipe''', '''}
# 0.1.5: default prices that moved in 0.1.5: id -> (0.1.4 default, 0.1.5 default). NO one-time update: products.properties keeps every
# saved price (Skyy set Tree Sap 12 live already); only the seed line of a fresh install / a missing line changes. The 0.1.2 -> 0.1.3
# update (servers still on 0.1.2 data) moves a 0.1.2 default line to the current seed line, as it does for every product.
PRICE_015 = {
    "Ingredient_Tree_Sap": (4, 12),     # Skyy: "with how little seems to drop, id raise the price on sap"
}
# the vanilla farming path (Farmingbench RequiredTierLevel of the normal seed recipe''')
rep('''    if p not in PROC and p not in PRICE_014 and abs(float(_new[p][1]) - b) > 1e-9:''',
    '''    if p not in PROC and p not in PRICE_014 and p not in PRICE_015 and abs(float(_new[p][1]) - b) > 1e-9:''')
rep('''for _i, (_o, _n) in PRICE_014.items():
    assert _i in _new and _new[_i][1] is not AUTO and abs(float(_new[_i][1]) - _n) < 1e-9, "PRICE_014 %s: row %s" % (_i, _new.get(_i))''',
    '''for _i, (_o, _n) in PRICE_014.items():
    assert _i in _new and _new[_i][1] is not AUTO and abs(float(_new[_i][1]) - _n) < 1e-9, "PRICE_014 %s: row %s" % (_i, _new.get(_i))
for _i, (_o, _n) in PRICE_015.items():   # 0.1.5: the rows carry the 0.1.5 default; the 0.1.4 default was the 0.1.2 one (never in PRICE_014)
    assert _i in _new and _new[_i][1] is not AUTO and abs(float(_new[_i][1]) - _n) < 1e-9 and _i not in PRICE_014 and _i not in PROC, _i
    assert abs(_old[_i][1] - _o) < 1e-9, "PRICE_015 %s: the 0.1.2 / 0.1.3 / 0.1.4 default was %s" % (_i, _old[_i][1])''')
# the 0.1.3 seed lines (isDefault / the 0.1.3 update re-run) keep sap at its 0.1.3 default 4
rep('''_fb013.update((_i, float(_o)) for _i, (_o, _n) in PRICE_014.items())
''', '''_fb013.update((_i, float(_o)) for _i, (_o, _n) in PRICE_014.items())
_fb013.update((_i, float(_o)) for _i, (_o, _n) in PRICE_015.items())   # 0.1.5: sap was 4 in 0.1.3 (and 0.1.4)
''')

# ================================================================================================================ classes
rep('''cfgc = pool.makeClass(PKG + ".BzCfg")          # 0.1.3: the processed goods premium (Server Setup row processed.premium)
''', '''cfgc = pool.makeClass(PKG + ".BzCfg")          # 0.1.3: the processed goods premium (Server Setup row processed.premium)
bags = pool.makeClass(PKG + ".Bags")           # 0.1.5: SkyySacks' bag bridge (sell from the bags)
''')
rep('''ALL = (utl, coin, prod, cat_, mkt, inv_, res, trd, page, fac, cmd, aprv, aprc, arlc, arsc, ainc, adm, tick, pl, cfgc)''',
    '''ALL = (utl, coin, prod, cat_, mkt, inv_, bags, res, trd, page, fac, cmd, aprv, aprc, arlc, arsc, ainc, adm, tick, pl, cfgc)''')

# ================================================================================================================ (A) the Bags class
BAGS = r'''# ================= Bags (0.1.5): SkyySacks 0.7.13's bag bridge - sell from the Magic Bags the player carries =================
# sacks:fn:count {UUID, id} -> Long (-1 paused), sacks:fn:all UUID -> Map id -> Long (null paused), sacks:fn:take {UUID, id, Long} -> Long
# removed, sacks:fn:put {UUID, id, Long} -> Long returned (only what a take removed). World thread only (the page click thread). No SkyySacks /
# one older than 0.7.13 (no sacks:fn:take) = no bags: every count 0, every take 0 - 0.1.4 behaviour.
bags.addField(CtField.make("public static final int CAP = 1000000000;", bags))
bags.addMethod(CtNewMethod.make(jt(r"""
public static boolean on() {
  try {
    java.util.Map b = @PKG@.BzUtil.bridge();
    return (b.get("sacks:fn:take") instanceof java.util.function.Function) && (b.get("sacks:fn:count") instanceof java.util.function.Function);
  } catch (Throwable t) { return false; }
}"""), bags))
# one bridge call -> its Long answer; -2 = absent / failed / not a number
bags.addMethod(CtNewMethod.make(jt(r"""
public static long call(String key, Object arg) {
  try {
    Object f = @PKG@.BzUtil.bridge().get(key);
    if (!(f instanceof java.util.function.Function)) return -2L;
    Object r = ((java.util.function.Function) f).apply(arg);
    if (r instanceof Number) return ((Number) r).longValue();
  } catch (Throwable t) { @PKG@.BzUtil.warn("bag bridge " + key + " failed: " + t); }
  return -2L;
}"""), bags))
bags.addMethod(CtNewMethod.make(jt(r"""
public static int count(java.util.UUID u, String id) {
  if (u == null || id == null || !on()) return 0;
  long r = call("sacks:fn:count", new Object[] { u, id });
  if (r <= 0L) return 0;
  return r > (long) CAP ? CAP : (int) r;
}"""), bags))
# every item the player can take from the bags now: an empty map when there are no bags (or they are paused); null only when SkyySacks
# has count + take but no sacks:fn:all - then held() asks count per item
bags.addMethod(CtNewMethod.make(jt(r"""
public static java.util.HashMap all(java.util.UUID u) {
  java.util.HashMap out = new java.util.HashMap();
  if (u == null || !on()) return out;
  try {
    Object f = @PKG@.BzUtil.bridge().get("sacks:fn:all");
    if (!(f instanceof java.util.function.Function)) return null;
    Object r = ((java.util.function.Function) f).apply(u);
    if (!(r instanceof java.util.Map)) return out;
    java.util.Iterator it = ((java.util.Map) r).entrySet().iterator();
    while (it.hasNext()) {
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      if (!(e.getKey() instanceof String) || !(e.getValue() instanceof Number)) continue;
      long v = ((Number) e.getValue()).longValue();
      if (v > 0L) out.put(e.getKey(), Long.valueOf(v > (long) CAP ? (long) CAP : v));
    }
  } catch (Throwable t) { @PKG@.BzUtil.warn("bag bridge sacks:fn:all failed: " + t); }
  return out;
}"""), bags))
bags.addMethod(CtNewMethod.make(jt(r"""
public static int held(java.util.HashMap m, java.util.UUID u, String id) {
  if (m == null) return count(u, id);
  Long v = (Long) m.get(id);
  return v == null ? 0 : (int) v.longValue();
}"""), bags))
# take up to n out of the bags; the answer is what really left the pool (only that may be paid for)
bags.addMethod(CtNewMethod.make(jt(r"""
public static int take(java.util.UUID u, String id, int n) {
  if (u == null || id == null || n <= 0 || !on()) return 0;
  long r = call("sacks:fn:take", new Object[] { u, id, Long.valueOf((long) n) });
  if (r <= 0L) return 0;
  if (r > (long) n) @PKG@.BzUtil.warn("SkyySacks removed " + r + " " + id + " when " + n + " were asked - paying for what left the bags");
  return r > (long) CAP ? CAP : (int) r;
}"""), bags))
# review fix: the sale PAID for n of its take - they leave SkyySacks' refund ledger (a later put can never return them); 0 when absent
bags.addMethod(CtNewMethod.make(jt(r"""
public static int commit(java.util.UUID u, String id, int n) {
  if (u == null || id == null || n <= 0) return 0;
  long r = call("sacks:fn:commit", new Object[] { u, id, Long.valueOf((long) n) });
  if (r <= 0L) return 0;
  return r > (long) n ? n : (int) r;
}"""), bags))
# the refund path: put back up to n (SkyySacks only returns what a take removed); the caller gives the rest to the inventory
bags.addMethod(CtNewMethod.make(jt(r"""
public static int put(java.util.UUID u, String id, int n) {
  if (u == null || id == null || n <= 0) return 0;
  long r = call("sacks:fn:put", new Object[] { u, id, Long.valueOf((long) n) });
  if (r <= 0L) return 0;
  return r > (long) n ? n : (int) r;
}"""), bags))

'''
rep("# ================= TradeResult =================\n", BAGS + "# ================= TradeResult =================\n")
rep('''res.addField(CtField.make("public long price;", res))''', '''res.addField(CtField.make("public long price;", res))
# 0.1.5: how many of the sold items came out of the bags (Sell inventory sums it for its line)
res.addField(CtField.make("public int fromBags;", res))''')

# ================================================================================================================ Trader
TRD_NEW = '''# 0.1.5: Magic Bags are never traded (Skyy's lock: /trade + the AH block them; the Bazaar never lists them - this holds even if an admin
# adds a Skyy_Sack_* line to products.properties)
trd.addMethod(CtNewMethod.make("""
public static boolean locked(String id) {
  return id != null && id.startsWith("Skyy_Sack_");
}""", trd))
# 0.1.5 (Skyy: "use hytale stack numbers"): the item's real max stack - Item.getMaxStack after the engine's Parent inheritance and
# Item.processConfig (no MaxStack: tool / weapon / armor / builder tool 1, else 100); 0 / unknown -> 100 (the plain-item default)
trd.addField(CtField.make("public static final int DEF_STACK = 100;", trd))
trd.addMethod(CtNewMethod.make(f"""
public static int stack(String id) {{
  int max = 0;
  try {{
    {ITM} it = id == null ? null : ({ITM}) {ITM}.getAssetMap().getAsset(id);
    if (it != null) max = it.getMaxStack();
  }} catch (Throwable t) {{ max = 0; }}
  if (max <= 0) max = DEF_STACK;
  if (max > MAXQ) max = MAXQ;
  return max;
}}""", trd))
# 0.1.5: a cancelled sale returns its items: the bag part through sacks:fn:put first, whatever it does not take into the inventory
trd.addMethod(CtNewMethod.make(f"""
public static int giveBack({PLA} p, java.util.UUID u, String id, int inv, int bag) {{
  int back = 0;
  if (bag > 0) back = {PKG}.Bags.put(u, id, bag);
  if (bag - back > 0) {PKG}.Bags.commit(u, id, bag - back);   // review fix: the part the bags did not take back leaves the refund ledger
  int rest = inv + (bag - back);
  if (rest > 0) back += {PKG}.Inv.give(p, id, rest);
  return back;
}}""", trd))
'''
rep('''trd.addMethod(CtNewMethod.make(f"""
public static {TR} buy0(''', TRD_NEW + '''trd.addMethod(CtNewMethod.make(f"""
public static {TR} buy0(''')
rep('''  if (p == null || qty <= 0 || qty > MAXQ) return new {TR}(false, 0, 0L, "bad amount");''',
    '''  if (p == null || qty <= 0 || qty > MAXQ) return new {TR}(false, 0, 0L, "bad amount");
  if (locked(id)) return new {TR}(false, 0, 0L, "Magic Bags can never be bought or sold");''')
OLD_SELL0 = method("public static {TR} sell0({PLA} p, java.util.UUID u, String who, String id, int want) {{")
NEW_SELL0 = '''# 0.1.5: the inventory first (count-verified, 0.1.4's rule), then the bags (sacks:fn:take - what it reports is what left); coins only for
# what really left; a failed payment returns the bag part to the bags (sacks:fn:put) and the rest to the inventory
trd.addMethod(CtNewMethod.make(f"""
public static {TR} sell0({PLA} p, java.util.UUID u, String who, String id, int want) {{
  if (id == null) return new {TR}(false, 0, 0L, "click a product first");
  if (locked(id)) return new {TR}(false, 0, 0L, "Magic Bags can never be bought or sold");
  {PKG}.Product pr = {PKG}.Catalog.get(id);
  if (pr == null || !{PKG}.Catalog.usable(id)) return new {TR}(false, 0, 0L, "that item is not on the bazaar");
  if (!{PKG}.Coins.ready()) return new {TR}(false, 0, 0L, "SkyyCoins is not loaded - the bazaar cannot pay coins");
  if (p == null) return new {TR}(false, 0, 0L, "player not found");
  if (busy(u)) return new {TR}(false, 0, 0L, "your profile is still loading - try again in a moment");
  int inv = {PKG}.Inv.count(p, id);
  int bag = {PKG}.Bags.count(u, id);
  long hl = (long) inv + (long) bag;
  int held = hl > 2000000000L ? 2000000000 : (int) hl;
  if (held <= 0) return new {TR}(false, 0, 0L, "you have no " + pr.name);
  int n = (want <= 0 || want > held) ? held : want;
  if (n > MAXQ) n = MAXQ;
  long quote = {PKG}.Market.quote(id, n, false);
  if (quote < 0L) return new {TR}(false, 0, 0L, "price error - tell an admin");
  if (quote == 0L) return new {TR}(false, 0, 0L, n + " " + pr.name + " is worth 0 coins right now - sell more at once");
  long purse = {PKG}.Coins.get(u);
  if (purse < 0L) return new {TR}(false, 0, 0L, "the coin bank did not answer - nothing sold, try again");
  if (purse > Long.MAX_VALUE - 2L * quote) return new {TR}(false, 0, 0L, "your purse is full");
  int fromInv = n < inv ? n : inv;
  int invTaken = 0;
  if (fromInv > 0) {{
    {PKG}.Inv.take(p, id, fromInv);
    invTaken = inv - {PKG}.Inv.count(p, id);
    if (invTaken < 0) invTaken = 0;
  }}
  int bagTaken = 0;
  if (n - invTaken > 0 && bag > 0) bagTaken = {PKG}.Bags.take(u, id, n - invTaken);
  int removed = invTaken + bagTaken;
  if (removed <= 0) return new {TR}(false, 0, 0L, "could not remove the items - nothing sold");
  long pay = removed == n ? quote : {PKG}.Market.quote(id, removed, false);
  if (pay <= 0L || purse > Long.MAX_VALUE - pay) {{
    int back1 = giveBack(p, u, id, invTaken, bagTaken);
    {PKG}.BzUtil.warn("sell cancelled for " + u + " " + id + " removed " + removed + " (bags " + bagTaken + ") returned " + back1);
    {PKG}.Market.log("SELL-CANCELLED " + who + " " + u + " " + id + " removed " + removed + " returned " + back1 + " bags=" + bagTaken);
    if (back1 >= removed) return new {TR}(false, 0, 0L, "sale cancelled - your items were returned");
    {TR} rc = new {TR}(false, 0, 0L, "sale cancelled but only " + back1 + " of " + removed + " " + pr.name + " fit back - tell an admin - it is logged");
    rc.alert = true;
    return rc;
  }}
  int ad = {PKG}.Coins.add(u, pay);
  if (ad != 1) {{
    int back2 = giveBack(p, u, id, invTaken, bagTaken);
    {PKG}.BzUtil.warn("PAY FAILED for " + who + " " + u + " " + id + " x" + removed + " (" + pay + " coins, coins:fn:add " + (ad < 0 ? "threw - it may or may not have paid" : "refused or missing") + ") - returned " + back2 + " items (bags " + bagTaken + ")");
    {PKG}.Market.log((ad < 0 ? "PAY-ERROR " : "PAY-FAILED ") + who + " " + u + " " + id + " " + removed + " " + pay + " returned " + back2 + " bags=" + bagTaken);
    if (back2 >= removed) return new {TR}(false, 0, 0L, "could not pay - your items were returned");
    {TR} rp = new {TR}(false, 0, 0L, "could not pay and only " + back2 + " of " + removed + " " + pr.name + " fit back - tell an admin - it is logged");
    rp.alert = true;
    return rp;
  }}
  if (bagTaken > 0) {PKG}.Bags.commit(u, id, bagTaken);   // review fix: paid - those can never be put back
  {PKG}.Market.apply(id, removed, false);
  {PKG}.Market.log("SELL " + who + " " + u + " " + id + " " + removed + " " + pay + " f=" + {PKG}.BzUtil.num({PKG}.Market.factor(id)) + (bagTaken > 0 ? " bags=" + bagTaken : ""));
  {TR} ok = new {TR}(true, removed, pay, "sold " + removed + " " + pr.name + " for " + pay + " coins" + (bagTaken > 0 ? " (" + bagTaken + " from your bags)" : ""));
  ok.fromBags = bagTaken;
  return ok;
}}""", trd))
'''
assert OLD_SELL0.startswith('trd.addMethod(CtNewMethod.make(f"""\npublic static {TR} sell0(') and OLD_SELL0.count("Inv.take(p, id, n)") == 1
rep(OLD_SELL0, NEW_SELL0)
rep('''  int held = {PKG}.Inv.count(p, id);
  if (held <= 0) return new {TR}(false, 0, 0L, "you have no " + pr.name);
  if (qty > held) return''', '''  long hl0 = (long) {PKG}.Inv.count(p, id) + (long) {PKG}.Bags.count(u, id);   // 0.1.5: + the bags
  int held = hl0 > 2000000000L ? 2000000000 : (int) hl0;
  if (held <= 0) return new {TR}(false, 0, 0L, "you have no " + pr.name);
  if (qty > held) return''')
OLD_PREVIEW = method("public static long[] preview({PLA} p) {{")
rep(OLD_PREVIEW, '''# {{items, coins, from the bags}} that Sell inventory would move right now (0.1.5: inventory + bags, each capped at the per-trade limit)
trd.addMethod(CtNewMethod.make(f"""
public static long[] preview0({PLA} p, java.util.UUID u) {{
  java.util.ArrayList all = {PKG}.Catalog.all();
  java.util.HashMap bm = {PKG}.Bags.all(u);
  long items = 0L, coins = 0L, fromBags = 0L;
  for (int i = 0; i < all.size(); i++) {{
    String id = (({PKG}.Product) all.get(i)).id;
    if (locked(id) || !{PKG}.Catalog.usable(id)) continue;
    int inv = {PKG}.Inv.count(p, id);
    int bg = {PKG}.Bags.held(bm, u, id);
    long h = (long) inv + (long) bg;
    if (h <= 0L) continue;
    int q = h > (long) MAXQ ? MAXQ : (int) h;
    long c = {PKG}.Market.quote(id, q, false);
    if (c <= 0L) continue;
    items += (long) q; coins += c;
    if (q > inv) fromBags += (long) (q - inv);
  }}
  return new long[] {{ items, coins, fromBags }};
}}""", trd))
trd.addMethod(CtNewMethod.make(f"""
public static long[] preview({PLA} p, java.util.UUID u) {{
  synchronized ({PKG}.Market.class) {{ return preview0(p, u); }}
}}""", trd))
''')
rep('''    java.util.ArrayList all = {PKG}.Catalog.all();
    int items = 0, kinds = 0; long coins = 0L;
    String warnMsg = null, lastFail = null;
    for (int i = 0; i < all.size(); i++) {{
      String id = (({PKG}.Product) all.get(i)).id;
      if ({PKG}.Inv.count(p, id) <= 0) continue;
      {TR} r = sell0(p, u, who, id, 0);
      if (r.ok) {{ items += r.qty; coins += r.coins; kinds++; }} else lastFail = r.msg;''', '''    java.util.ArrayList all = {PKG}.Catalog.all();
    java.util.HashMap bm = {PKG}.Bags.all(u);
    int items = 0, kinds = 0, fromBags = 0; long coins = 0L;
    String warnMsg = null, lastFail = null;
    for (int i = 0; i < all.size(); i++) {{
      String id = (({PKG}.Product) all.get(i)).id;
      if (locked(id)) continue;
      if ({PKG}.Inv.count(p, id) <= 0 && {PKG}.Bags.held(bm, u, id) <= 0) continue;
      {TR} r = sell0(p, u, who, id, 0);
      if (r.ok) {{ items += r.qty; coins += r.coins; kinds++; fromBags += r.fromBags; }} else lastFail = r.msg;''')
rep('''"nothing to sell - no bazaar items in your inventory"));''', '''"nothing to sell - no bazaar items in your inventory or bags"));''')
rep('''    {TR} rs = new {TR}(true, items, coins, "sold " + items + " items of " + kinds + " kinds for " + coins + " coins" + (warnMsg != null ? " - but " + warnMsg : ""));''',
    '''    {TR} rs = new {TR}(true, items, coins, "sold " + items + " items of " + kinds + " kinds for " + coins + " coins" + (fromBags > 0 ? " (" + fromBags + " from your bags)" : "") + (warnMsg != null ? " - but " + warnMsg : ""));
    rs.fromBags = fromBags;''')

# ================================================================================================================ (C) + (A) the page
rep('''BZ_ACTS = [SUI.button("SkyyBzBuy1", "Buy 1", "primary", w=BZ_ACT_W),
           SUI.button("SkyyBzBuy64", "Buy 64", "primary", w=BZ_ACT_W, anchor={"left": BZ_ACT_GAP}),''',
    '''# 0.1.5: Buy / Sell <stack> = the item's real Hytale max stack; the number is drawn inline (BZ_STK replaced in Java, like the tab names)
BZ_STK = "QzStkQz"
BZ_ACTS = [SUI.button("SkyyBzBuy1", "Buy 1", "primary", w=BZ_ACT_W),
           SUI.button("SkyyBzBuyStk", "Buy " + BZ_STK, "primary", w=BZ_ACT_W, anchor={"left": BZ_ACT_GAP}),''')
rep('''           SUI.button("SkyyBzSell64", "Sell 64", "destructive", w=BZ_ACT_W, anchor={"left": BZ_ACT_GAP}),''',
    '''           SUI.button("SkyyBzSellStk", "Sell " + BZ_STK, "destructive", w=BZ_ACT_W, anchor={"left": BZ_ACT_GAP}),''')
rep('''assert not any("@" in v for v in BZ_J.values())
''', '''assert not any("@" in v for v in BZ_J.values())
# 0.1.5: the stack number on the two stack buttons - the sentinel inside the Java string literal becomes " + stk + " (int stk in render)
assert BZ_J["ACTS"].count(BZ_STK) == 2 and sum(v.count(BZ_STK) for v in BZ_J.values()) == 2
BZ_J["ACTS"] = BZ_J["ACTS"].replace(BZ_STK, '" + stk + "')
''')
rep('''    ("contains", "inventory is full", "-"), ("startsWith", "you have no", "-"), ("startsWith", "you only hold", "-"),''',
    '''    ("contains", "inventory is full", "-"), ("startsWith", "you have no", "-"), ("startsWith", "you only hold", "-"),
    ("startsWith", "Magic Bags", "-"),''')
# limits: + the bags (lim[2] = inventory + bags, lim[3] = the bag part)
rep('''public int[] limits({PLA} p, java.util.UUID u, String id) {{
  int held = {PKG}.Inv.count(p, id);''', '''public int[] limits({PLA} p, java.util.UUID u, String id) {{
  int bagH = {PKG}.Bags.count(u, id);
  long hl = (long) {PKG}.Inv.count(p, id) + (long) bagH;
  int held = hl > 2000000000L ? 2000000000 : (int) hl;''')
rep('''  return new int[] {{ afford, room, held }};''', '''  return new int[] {{ afford, room, held, bagH }};''')
# grid cells: the held number counts the bags too (one sacks:fn:all per render)
rep('''  this.cells = new String[@PER@];
  for (int r = 0; r < @ROWS@; r++) {''', '''  this.cells = new String[@PER@];
  java.util.HashMap bagm = player == null ? new java.util.HashMap() : @PKG@.Bags.all(u);
  for (int r = 0; r < @ROWS@; r++) {''')
rep('''        int held = player == null ? 0 : @PKG@.Inv.count(player, p.id);
        if (held > 0) b.set("#SkyyBzCell" + idx + "Qty.Text", String.valueOf(held));''',
    '''        int held = player == null ? 0 : @PKG@.Inv.count(player, p.id) + @PKG@.Bags.held(bagm, u, p.id);
        // review fix: the cell label fits 7 digits - 10,000,000+ (a raised bag cap) shows as 12.3M; "You hold" keeps the exact number
        if (held > 0) b.set("#SkyyBzCell" + idx + "Qty.Text", held >= 10000000 ? (held / 1000000) + "." + ((held / 100000) % 10) + "M" : String.valueOf(held));''')
rep('''    long b1 = @PKG@.Market.quote(id, 1, true), b64 = @PKG@.Market.quote(id, 64, true);
    long s1 = @PKG@.Market.quote(id, 1, false), s64 = @PKG@.Market.quote(id, 64, false);''',
    '''    int stk = @PKG@.Trader.stack(id);
    long b1 = @PKG@.Market.quote(id, 1, true), bS = @PKG@.Market.quote(id, stk, true);
    long s1 = @PKG@.Market.quote(id, 1, false), sS = @PKG@.Market.quote(id, stk, false);''')
rep('''" coins for 1   -   " + b64 + " for 64   -   about "''', '''" coins for 1   -   " + bS + " for " + stk + "   -   about "''')
rep('''" coins for 1   -   " + s64 + " for 64   -   about "''', '''" coins for 1   -   " + sS + " for " + stk + "   -   about "''')
rep('''    b.set("#SkyyBzDHold.Text", "You hold " + held + (held > 0 ? "   -   selling all pays " + sAll + " coins" : ""));''',
    '''    b.set("#SkyyBzDHold.Text", "You hold " + held + (lim[3] > 0 ? " (" + lim[3] + " in your bags)" : "") + (held > 0 ? "   -   selling all pays " + sAll + " coins" : ""));''')
rep('''    ev.addEventBinding(@BT@.Activating, "#SkyyBzBuy64", evd("buy64", true));''',
    '''    ev.addEventBinding(@BT@.Activating, "#SkyyBzBuyStk", evd("buystk", true));''')
rep('''    ev.addEventBinding(@BT@.Activating, "#SkyyBzSell64", evd("sell64", true));''',
    '''    ev.addEventBinding(@BT@.Activating, "#SkyyBzSellStk", evd("sellstk", true));''')
rep('''    else if (a.equals("buy64")) r = {PKG}.Trader.buy(p, u, who, this.sel, 64);''',
    '''    else if (a.equals("buystk")) r = {PKG}.Trader.buy(p, u, who, this.sel, {PKG}.Trader.stack(this.sel));''')
rep('''    else if (a.equals("sell64")) r = {PKG}.Trader.sell(p, u, who, this.sel, 64);''',
    '''    else if (a.equals("sellstk")) r = {PKG}.Trader.sell(p, u, who, this.sel, {PKG}.Trader.stack(this.sel));''')
rep('''        long[] pv = {PKG}.Trader.preview(p);
        if (pv[0] <= 0L) {{ this.info = "nothing to sell - no bazaar items in your inventory"; this.confirmUntil = 0L; }}
        else {{ this.info = "sell " + pv[0] + " items for about " + pv[1] + " coins - click Confirm sell within 10 seconds"; this.confirmUntil = now + 10000L; }}''',
    '''        long[] pv = {PKG}.Trader.preview(p, u);
        if (pv[0] <= 0L) {{ this.info = "nothing to sell - no bazaar items in your inventory or bags"; this.confirmUntil = 0L; }}
        else {{ this.info = "sell " + pv[0] + " items" + (pv[2] > 0L ? " (" + pv[2] + " from your bags)" : "") + " for about " + pv[1] + " coins - click Confirm sell within 10 seconds"; this.confirmUntil = now + 10000L; }}''')

# ================================================================================================================ checks on the result
for kb in KEEP:
    assert kb in s, "a block that must stay 0.1.4's changed: %s" % kb[:90]
assert s.count("registerCommand(") == REG0, "command registrations changed"
assert "@@" not in s and "buy64" not in s and "sell64" not in s and "SkyyBzBuy64" not in s and "SkyyBzSell64" not in s
assert s.count('VERSION = "0.1.5"') == 1
for _a, _b in (("# ================= Bags (0.1.5)", "# ================= TradeResult ="), ("public static boolean locked(String id)", "public static {TR} buy0("),
               ("public static int giveBack(", "public static {TR} sell0("), ("public static int stack(String id)", "# ================= BzPage"),
               ("public static long[] preview0(", "public static long[] preview({PLA} p, java.util.UUID u)"),
               ("public static int held(java.util.HashMap m", "public static {TR} sell0("),
               ("public static int commit(java.util.UUID u", "public static {TR} sell0("),
               ("public static int commit(java.util.UUID u", "public static int giveBack("), ("bags = pool.makeClass(", "# ================= Bags (0.1.5)")):
    assert 0 <= s.find(_a) < s.find(_b), "order: %s before %s" % (_a[:60], _b[:60])
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst, len(s.split(LF)), "lines")
