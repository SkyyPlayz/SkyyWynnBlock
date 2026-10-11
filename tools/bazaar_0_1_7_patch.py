"""Derive SkyyBazaar/build_skyybazaar_0.1.7.py from the LIVE 0.1.6 (build_skyybazaar_0.1.6.py = the tools/deploy_set.py SET pin; 0.1.6 and every
older script stay untouched).
Run:  python tools/bazaar_0_1_7_patch.py   then   python SkyyBazaar/build_skyybazaar_0.1.7.py
(never --deploy: coordinated deploy). Tested by the SkyyGear 0.2.14 harness (SkyyGear/test_skyygear_0.2.14.py, section M: the market wall
in each partner mod) - this round's only SkyyBazaar change.

0.1.7 = THE MARKET WALL (docs/answered/economy.md 2026-10-08, Skyy's popup: MARKET WALL -> "Mythic + UT + Sets (Recommended)" - never bought
or sold on the Bazaar / Auctions; built in the UT/Mythic round with SkyyGear 0.2.14). The Bazaar trades by item id and used to take ANY stack
of a product id, whatever its metadata - so a Mythic / Untiered / Set copy of a product id (only possible when an admin lists a gear id as a
product; the default catalog has none) could have been sold. Now it asks the shared market:veto map (the Auction House's contract: owner ->
Function(ItemStack) -> null or a reason; SkyyGear 0.2.14 publishes "SkyyGear"):
 - Inv.veto(stack): every veto in turn, the first reason wins; a veto that throws = a refusal ("could not check this item"); no map = no wall.
 - Inv.countIn / Inv.take skip every stack WITH metadata that a veto refuses: a walled stack is never counted as held, never sold, never taken
   by Sell / Sell all / Sell inventory, and never counted by give()'s before / after measure (plain stacks are never asked - no cost for
   ordinary materials).
 - buy0 / sell0 refuse a product whose PLAIN stack a veto refuses (an Untiered-table id listed as a product): "Mythic, Untiered and Set gear
   never goes on the market - trade it directly with another player." (SkyyGear's reason text), before any coin or item moves.
Without SkyyGear 0.2.14 (no market:veto) everything is exactly 0.1.6. No price / page / saved-data change. Rolling back to 0.1.6 is safe.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyBazaar", "build_skyybazaar_0.1.6.py")
dst = os.path.join(ROOT, "SkyyBazaar", "build_skyybazaar_0.1.7.py")
CR, LF = chr(13), chr(10)
raw = open(src, encoding="utf8", newline="").read()
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
assert 'VERSION = "0.1.6"' in s and "SkyyBzFind" in s and "market:veto" not in s, "the source must be the generated 0.1.6 script"


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d != %d: %s" % (n, count, old[:120])
    s = s.replace(old, new)


HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
rep('''"""SkyyBazaar 0.1.6 - build script (javassist via jpype). Hypixel-Bazaar-style commodity market, MVP = INSTANT buy/sell against a
server market maker.
Run:   python build_skyybazaar_0.1.6.py            -> SkyyBazaar/SkyyBazaar-0.1.6.jar   (build only; deploys go through
       tools/deploy_set.py --yes, never --deploy)
       (0.1.6 is GENERATED from build_skyybazaar_0.1.5.py by tools/bazaar_0_1_6_patch.py - edit the patch, not this file; 0.1.5 came
       from 0.1.4 by tools/bazaar_0_1_5_patch.py, 0.1.4 from 0.1.3, 0.1.3 from 0.1.2, 0.1.2 from 0.1.1, 0.1.1 from 0.1; every older
       script is kept as it was)
''', '''"""SkyyBazaar 0.1.7 - build script (javassist via jpype). Hypixel-Bazaar-style commodity market, MVP = INSTANT buy/sell against a
server market maker.
Run:   python build_skyybazaar_0.1.7.py            -> SkyyBazaar/SkyyBazaar-0.1.7.jar   (build only; deploys go through
       tools/deploy_set.py --yes, never --deploy)
       (0.1.7 is GENERATED from build_skyybazaar_0.1.6.py by tools/bazaar_0_1_7_patch.py - edit the patch, not this file; 0.1.6 came
       from 0.1.5 by tools/bazaar_0_1_6_patch.py, 0.1.5 from 0.1.4, 0.1.4 from 0.1.3, 0.1.3 from 0.1.2, 0.1.2 from 0.1.1, 0.1.1 from 0.1;
       every older script is kept as it was)

''' + HEAD[HEAD.index("0.1.7 = "):].strip() + '''
''')
rep('VERSION = "0.1.6"', 'VERSION = "0.1.7"')

# Inv: the veto + the walled-stack skip in countIn / take
rep('''inv_.addMethod(CtNewMethod.make(f"""
public static int countIn({IC} c, String id) {{
  if (c == null || id == null) return 0;
  int n = 0;
  short cap = c.getCapacity();
  for (short s = 0; s < cap; s++) {{
    {IS} it = c.getItemStack(s);
    if (it == null || it.isEmpty() || !id.equals(it.getItemId())) continue;''', '''# 0.1.7 THE MARKET WALL (tools/bazaar_0_1_7_patch.py): market:veto = owner -> Function(ItemStack) -> null or a reason (the Auction House's
# contract; SkyyGear 0.2.14 walls Mythic / Untiered / Set gear). The first reason wins; a veto that throws refuses; no map = nothing walled.
inv_.addMethod(CtNewMethod.make(f"""
public static String veto({IS} s) {{
  if (s == null || s.isEmpty()) return null;
  Object o = null;
  try {{ o = {PKG}.BzUtil.bridge().get("market:veto"); }} catch (Throwable t) {{ o = null; }}
  if (!(o instanceof java.util.Map)) return null;
  java.util.Iterator it = new java.util.ArrayList(((java.util.Map) o).values()).iterator();
  while (it.hasNext()) {{
    Object f = it.next();
    if (!(f instanceof java.util.function.Function)) continue;
    try {{
      Object r = ((java.util.function.Function) f).apply(s);
      if (r != null) return String.valueOf(r);
    }} catch (Throwable t) {{ return "could not check this item"; }}
  }}
  return null;
}}""", inv_))
# a stack WITH metadata that a veto refuses (plain stacks are never asked: ordinary materials cost nothing)
inv_.addMethod(CtNewMethod.make(f"""
public static boolean walled({IS} it) {{
  return it != null && !it.isEmpty() && it.getMetadata() != null && veto(it) != null;
}}""", inv_))
# a product whose PLAIN stack is walled (an Untiered-table id) - null = fine
inv_.addMethod(CtNewMethod.make(f"""
public static String wallId(String id) {{
  if (id == null) return null;
  try {{ return veto(new {IS}(id, 1)); }} catch (Throwable t) {{ return null; }}
}}""", inv_))
inv_.addMethod(CtNewMethod.make(f"""
public static int countIn({IC} c, String id) {{
  if (c == null || id == null) return 0;
  int n = 0;
  short cap = c.getCapacity();
  for (short s = 0; s < cap; s++) {{
    {IS} it = c.getItemStack(s);
    if (it == null || it.isEmpty() || !id.equals(it.getItemId()) || walled(it)) continue;''')
rep('''      {IS} it = cont.getItemStack(s);
      if (it == null || it.isEmpty() || !id.equals(it.getItemId())) continue;
      int q = it.getQuantity();''', '''      {IS} it = cont.getItemStack(s);
      if (it == null || it.isEmpty() || !id.equals(it.getItemId()) || walled(it)) continue;
      int q = it.getQuantity();''')
rep('''  if (locked(id)) return new {TR}(false, 0, 0L, "Magic Bags can never be bought or sold");
  long cost = {PKG}.Market.quote(id, qty, true);''', '''  if (locked(id)) return new {TR}(false, 0, 0L, "Magic Bags can never be bought or sold");
  String wv = {PKG}.Inv.wallId(id);      // 0.1.7 the market wall
  if (wv != null) return new {TR}(false, 0, 0L, wv);
  long cost = {PKG}.Market.quote(id, qty, true);''')
rep('''  if (locked(id)) return new {TR}(false, 0, 0L, "Magic Bags can never be bought or sold");
  {PKG}.Product pr = {PKG}.Catalog.get(id);
  if (pr == null || !{PKG}.Catalog.usable(id)) return new {TR}(false, 0, 0L, "that item is not on the bazaar");
  if (!{PKG}.Coins.ready()) return new {TR}(false, 0, 0L, "SkyyCoins is not loaded - the bazaar cannot pay coins");''',
    '''  if (locked(id)) return new {TR}(false, 0, 0L, "Magic Bags can never be bought or sold");
  String wv = {PKG}.Inv.wallId(id);      // 0.1.7 the market wall
  if (wv != null) return new {TR}(false, 0, 0L, wv);
  {PKG}.Product pr = {PKG}.Catalog.get(id);
  if (pr == null || !{PKG}.Catalog.usable(id)) return new {TR}(false, 0, 0L, "that item is not on the bazaar");
  if (!{PKG}.Coins.ready()) return new {TR}(false, 0, 0L, "SkyyCoins is not loaded - the bazaar cannot pay coins");''')

open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
