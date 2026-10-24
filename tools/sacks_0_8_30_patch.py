"""Derive SkyySacks/build_skyysacks_0.8.30.py from the SET pin 0.8.29 (the GENERATED build_skyysacks_0.8.29.py; edit THIS file, then
regenerate: python tools/sacks_0_8_30_patch.py; never re-run sacks_0_8_29_patch.py on top of it). Every anchor is asserted once; at the end
every change is undone on a copy and compared with 0.8.29 (nothing else changed). Line endings kept.
Run:  python tools/sacks_0_8_30_patch.py   then   python SkyySacks/build_skyysacks_0.8.30.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.8.30.py [--dir <folder inside tools/dev/scratch/>] [--keep]

0.8.30 (2026-10-24) = AUTO-COMPACT IS A PER-BAG COIN UPGRADE + CRAFTING OPENS ENCHANTED ITEMS. Skyy (docs/answered/bags.md 2026-10-24): "the
  pocket dimension is still auto compacting my stuff into the enchanted version. but its not supposed to. that needs to be an upgrade per bag.
  (available at any point, just make it cost coins.) (100 items= 1 enchanted.) ... it just auto compresses the moment you get 100 (when its
  unlocked.) (and make sure crafting can auto uncompact items. so if it costs 180 iron ingots, and my bag as 10 ingots, and 3 enchanted iron
  ingots, it will work to craft it, and just cost 2 enchanted iron ingots, and give me back 20 iron  ingots." (+ 2026-10-16 COMPACTOR LOCKS:
  nothing compacts before it is unlocked, and only items whose Enchanted recipe is unlocked in Collections).
  FOUND: no SET jar compacts the Void today (SkyySacks 0.8.29 has no compactor; Collections / Shards / Pets / Gear only gift, sell, cost or
  craft Enchanted items - Enchanted items reach the Void through the Workbench Compressing tab (the bench link offers bag items), Collections
  gifts and pickups). So nothing has to be switched off: every profile simply starts without the upgrade.
  1. THE UPGRADE (per bag = per Void category, per PROFILE - pd/<key>.properties line comp.<Category>=1, kept as an unknown key by older
     versions): the Void page's side panel gets an "Auto-compact" box under the rarity box: price in coins (Buy -> Pay / Cancel, the
     upgrade box's pattern), then On / Paused (Pause / Turn on - comp.off.<Category>=1). Bags with no Enchanted item (Fishing today) say so.
     Paid through SkyyCoins only (coins:fn:take; refused = nothing changes; anything failing after the take = coins:fn:add refund); saved by
     the writer at once (VoidJob 5: pd file, then coins:fn:flush). Price = Server Setup pd.compact.coins.<Category> (2,000 each = about 15
     minutes of Lv 10 income, cheap early) x the shared coin curve (coins:fn:curve) at pd.compact.level (10 = x1.0), rounded like SkyyShards.
  2. COMPACTING (VoidCompact.run, at the end of the 2 s sweep - which runs after every pool change): for each bag whose upgrade is bought and
     on, every item of tools/skyyench.py (TABLE item rows + TABLE_ALLOYS, 110 pairs; resource-type rows Rubble / Sand / Crystal are left out:
     their input is many ids) that lives in that bag, whose Enchanted recipe is in coll:recipes (unlocked in Collections), turns every 100 into
     1 Enchanted (fixed 100 = the Compressing recipe's ratio; a different rate would make or destroy items, so it is not a row). The Enchanted
     item's own bag needs room (Iron bars live in Smithing, Enchanted Iron in Mining). Server Setup pd.compact.on = master switch.
  3. CRAFTING OPENS ENCHANTED ITEMS (Server Setup bags.craftOpen, default on): the bag mirror (BagMirror - /craft, every bench, inventory
     crafting, the Furnace / Tannery queue, sacks:fn:craftHave / craftPay = SkyyGear's Smithing / Anvil crafts) also offers each Enchanted
     item's base as 100 per Enchanted item (virtual stacks, after the loose ones) when a recipe there uses the base. What a craft takes is
     booked loose first, then the fewest Enchanted items are opened and the change stays in the bag: Skyy's example 10 ingots + 3 Enchanted,
     a 180-ingot craft -> 1 Enchanted + 30 ingots left (2 Enchanted opened, 20 back + the 10). Never offered when ONE recipe uses both the
     base and its Enchanted item (per-recipe markers: /craft, craftPay, benches and inventory crafting alike - each bench craft syncs
     and rebuilds first; fixer). Fuel loading never opens anything (its mirror is not a recipe mirror). A refused /
     refunded craftPay packs the opened ones back (receipt slot 7). The live-mirror rule covers the virtual stacks (fit trims them to
     100 x the Enchanted count, and an Enchanted take trims them).
  4. MANUAL UNPACK (Skyy: "you can decompress enchanted items back"): no un-compress recipe exists in the SET yet, so the Void page gets
     "Unpack to inventory" for a selected Enchanted item: N (amount box, empty = 1) open into 100 x N base items withdrawn to the storage;
     what does not fit packs back (under 100 stays loose in the bag).
  5. MIGRATION: none needed (there was no compactor state to change): every profile reads "not bought" = OFF - no items move, Enchanted
     items already stored stay. Logged once at start: "[SkyySacks] auto-compact: a per-bag upgrade bought with coins, off until bought ...".
  ROLLBACK to 0.8.29: safe - the comp.* lines stay in pd/<key>.properties (unknown keys are kept), nothing compacts, crafting stops opening
  Enchanted items; coins paid for the upgrade are not refunded by a rollback (they come back into use when 0.8.30+ returns).
  Follow-ups (other mods, bridge only): sacks:fn:take callers that pay COSTS (SkyyShards upgrades, SkyyPets egg costs, SkyyGear anvil costs
  taken by take() rather than craftPay) do not open Enchanted items - a later round can add a sacks:fn:takeOpen key if wanted.
  FIXER (review, compact1fix): (a) benches use the per-recipe rule too ("!nv:<base>" only) - the SkyyAlloy bench (Alloy_Ench_Bronze uses
  Enchanted Iron, Alloy_Bronze uses Iron bars) now offers the virtual bars; after every booking sync() trims what the mirror offers of each
  opened / taken Enchanted item and of the bases it backs (BagMirror.trimV), so the next craft never sees more than the pool holds.
  (b) the purchase: the comp.<Category> line is on disk (VoidStore.saveNow) BEFORE coins:fn:take - a crash can no longer take the coins
  without the upgrade; a failed save = nothing taken; a refused take undoes the line; a throw after the take refunds. The Pay button sends
  the price it showed (cmpok:<ci>:<price>) - another price = "the price changed", nothing taken; a refused take with enough coins says
  "coins are busy". (c) the compactor no longer saves the pool early (the sweep's crash-window rule: only when no unsaved sweep + quiet).
  (d) open0's clamp also writes CRAFT-OPEN-SHORT to crafts.log. (e) Mining's box says Rubble, Sand and Crystal cannot compact yet; the
  purchase line says shop / upgrade costs still use loose items only.
  FIXER 2 (compact1fix2): (f) the bag's own rarity UPGRADE (VoidStore.upgrade + the page's upgrade box) counts and opens Enchanted items
  in the Void for a short line (loose Void + inventory first, then the fewest Enchanted, change loose in the bag; a refusal packs them back,
  VOID-UPGRADE-UNOPEN) - with Auto-compact bought, loose Wheat / Cobblestone never stays above 99, so a 2,000-Wheat upgrade was unpayable.
  bags.craftOpen covers it. Other mods' costs (sacks:fn:take - also the Bazaar's sell path) still take loose items only: follow-up key.
  (g) a priced row never rounds to free (price floor 10 coins; row 0 = free stays). (h) no purchase while coll:recipes is not published
  (SkyyCollections missing / not ready): the upgrade could never compact. (i) inventory crafting (the pocket window, no pre-craft sync per
  click) shares the mirror: while it is attached, a base whose Enchanted item ANY attached recipe uses gets no virtual stacks ("!pocket" +
  "!e:<base>" markers) - two crafts between syncs can no longer pay one Enchanted item twice. (j) the box text has room for 3 lines (46 px; the side column is full: 646 / 646)
  and the strings are shorter. ACCEPTED, not changed: the purchase saves the pd file (one fsync) on the world thread - once per Pay click,
  needed for "the line on disk before the coins"; a hard kill between that save and SkyyCoins' write-behind purse flush (VoidJob 5, at
  once on the writer) can leave the upgrade bought without the coins taken - the player-favouring direction, same trade-off as the shops.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G   # only its generic Patch helper (anchors asserted once, undo-compare, line endings kept)

P = G.Patch(os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.29.py"), os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.30.py"))
assert P.has('VERSION = "0.8.29"\n') and P.has("MOB029") and not P.has("VoidCompact"), "not the live generated SkyySacks 0.8.29"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.8.30 (2026-10-24)"):].rstrip() + "\n"

P.rep('''  new ids stored in Combat stay in the pool file, hidden from the tabs until 0.8.29+ again - nothing deleted; they no longer go in).
"""
''', '''  new ids stored in Combat stay in the pool file, hidden from the tabs until 0.8.29+ again - nothing deleted; they no longer go in).
''' + NOTE + '''"""
''')
P.rep('VERSION = "0.8.29"\n', 'VERSION = "0.8.30"\n')

# ---------------------------------------------------------------- the class
P.rep('''vho = pool.makeClass(PKG + ".VoidHubOpen")''', '''vcm = pool.makeClass(PKG + ".VoidCompact")   # 0.8.30: auto-compact per bag + crafting opens Enchanted items
vho = pool.makeClass(PKG + ".VoidHubOpen")''')
P.rep('''          vho,    # 0.8.15: VoidHubOpen (HubBar is kit 1.7 now)
''', '''          vho,    # 0.8.15: VoidHubOpen (HubBar is kit 1.7 now)
          vcm,    # 0.8.30: VoidCompact
''')

# ---------------------------------------------------------------- Server Setup rows + SackCfg fields
P.rep('''PD_CATS = ("Mining", "Foraging", "Farming", "Fishing", "Combat", "Smithing")
''', '''PD_CATS = ("Mining", "Foraging", "Farming", "Fishing", "Combat", "Smithing")
# 0.8.30 auto-compact (tools/sacks_0_8_30_patch.py): the price of the per-bag upgrade = pd.compact.coins.<Category> x the coin curve at
# pd.compact.level (10 = x1.0; 2,000 coins = about 15 minutes of Lv 10 income - cheap early); the pairs = tools/skyyench.py item rows
CMP_COINS_DEF, CMP_LEVEL_DEF = 2000, 10
CMP_PAIRS = ([(t[2], EN.PREFIX + t[0]) for t in EN.TABLE if t[1] == "I"]
             + [(t[2], EN.PREFIX + t[0]) for t in EN.TABLE_ALLOYS if t[1] == "I"])
assert len(set(b for b, _e in CMP_PAIRS)) == len(CMP_PAIRS) == len(set(e for _b, e in CMP_PAIRS)), "0.8.30: one Enchanted item per base"
assert EN.RATIO == 100 and ("Ingredient_Bar_Iron", "Skyy_Ench_Iron") in CMP_PAIRS and ("Ingredient_Bar_Bronze", "Skyy_Ench_Bronze") in CMP_PAIRS
assert not [b for b, _e in CMP_PAIRS if b.startswith(EN.PREFIX)] and len(CMP_PAIRS) >= 100, len(CMP_PAIRS)
print("0.8.30 auto-compact: %d base -> Enchanted pairs (skipped resource-type rows: %s)" % (
    len(CMP_PAIRS), ", ".join(t[0] for t in EN.TABLE if t[1] != "I")))
''')
P.rep('''                  + ["public static volatile boolean PD_OMNI_AUTO = true;"])
''', '''                  + ["public static volatile boolean PD_OMNI_AUTO = true;"]
                  # 0.8.30: auto-compact + crafting opens Enchanted items
                  + ["public static volatile boolean CMP_ON = true;", "public static volatile boolean CRAFT_OPEN = true;",
                     "public static volatile int CMP_LEVEL = %d;" % CMP_LEVEL_DEF]
                  + ["public static volatile int CMP_COINS_%s = %d;" % (c.upper(), CMP_COINS_DEF) for c in PD_CATS])
''')
P.rep('''_PD_LOAD.append('  PD_OMNI_AUTO = boolKey(p, "pd.omniAuto", true);')
''', '''_PD_LOAD.append('  PD_OMNI_AUTO = boolKey(p, "pd.omniAuto", true);')
_PD_LOAD += ['  CMP_ON = boolKey(p, "pd.compact.on", true);', '  CRAFT_OPEN = boolKey(p, "bags.craftOpen", true);',   # 0.8.30
             '  CMP_LEVEL = intKey(p, "pd.compact.level", %d, 1, 100);' % CMP_LEVEL_DEF]
_PD_LOAD += ['  CMP_COINS_%s = intKey(p, "pd.compact.coins.%s", %d, 0, 1000000000);' % (c.upper(), c, CMP_COINS_DEF) for c in PD_CATS]
''')
P.rep('''                           + ["PD_GATE_" + PD_RAR[i].upper() for i in (1, 2, 3)] + ["PD_OMNI_AUTO"])
''', '''                           + ["PD_GATE_" + PD_RAR[i].upper() for i in (1, 2, 3)] + ["PD_OMNI_AUTO"]
                           + ["CMP_ON", "CRAFT_OPEN", "CMP_LEVEL"] + ["CMP_COINS_" + c.upper() for c in PD_CATS])   # 0.8.30
''')
P.rep('''    "#smelt.fortune.enabled=true", "#smelt.fortune.alloys=true", "#smelt.fortune.minedOnly=true", "#smelt.fortune.guard=100"]
SACK_CFG_TEXT''', '''    "#smelt.fortune.enabled=true", "#smelt.fortune.alloys=true", "#smelt.fortune.minedOnly=true", "#smelt.fortune.guard=100",
    # 0.8.30 (Skyy 2026-10-24 "that needs to be an upgrade per bag ... just make it cost coins")
    "# Auto-compact (an upgrade each player buys per bag with coins): 100 of an item whose Enchanted recipe they unlocked = 1 Enchanted.",
    "# Price = pd.compact.coins.<Category> x the coin curve at pd.compact.level (10 = x1). pd.compact.on=false stops all compacting.",
    "# bags.craftOpen=true lets crafting and bag upgrades open Enchanted items from the Void when they need the base item (change goes back in).",
    "#pd.compact.on=true", "#bags.craftOpen=true", "#pd.compact.level=%d" % CMP_LEVEL_DEF] + [
    "#pd.compact.coins.%s=%d" % (c, CMP_COINS_DEF) for c in PD_CATS]
SACK_CFG_TEXT''')
P.rep('''     for c in PD_CATS for r in (1, 2, 3)]
# 0.8.3 auto-pickup''', '''     for c in PD_CATS for r in (1, 2, 3)]
# 0.8.30 auto-compact (all live: the next sweep / page / craft reads the SackCfg fields)
SACK_CFG_ROWS += [
    _pdrow("pd.compact.on", "Auto-compact (master switch)", "void", "bool", "true", "", "", "", "live",
           "On: bags with the Auto-compact upgrade turn each 100 items into 1 Enchanted. Off: nothing compacts.", "CMP_ON"),
    _pdrow("bags.craftOpen", "Crafting opens Enchanted items", "void", "bool", "true", "", "", "", "live",
           "On: crafts and bag upgrades short of an item open its Enchanted form in the Void (change goes back).", "CRAFT_OPEN"),
    _pdrow("pd.compact.level", "Auto-compact price level", "void", "int", str(CMP_LEVEL_DEF), "1", "100", "", "live,adv",
           "The price below x the coin curve at this level (10 = x1). Higher = dearer.", "CMP_LEVEL"),
] + [_pdrow("pd.compact.coins." + c, "Auto-compact price: %s" % c, "void", "int", str(CMP_COINS_DEF), "0", "1000000000", "", "live",
            "Coins for the %s bag's Auto-compact upgrade (x the coin curve). 0 = free." % c, "CMP_COINS_" + c.upper())
     for c in PD_CATS]
# 0.8.3 auto-pickup''')

# ---------------------------------------------------------------- VoidJob 5: the purchase save (pd file, then the coins)
P.rep('''    } else if (this.mode == 4) {   // fix round: the upgrade - the rarity, then the pool, both now
      @PKG@.VoidStore.saveNow(this.k);
      if (@PKG@.SackPool.DIRTY.remove(this.k) != null) @PKG@.SackPool.save(this.k);
    }''', '''    } else if (this.mode == 4) {   // fix round: the upgrade - the rarity, then the pool, both now
      @PKG@.VoidStore.saveNow(this.k);
      if (@PKG@.SackPool.DIRTY.remove(this.k) != null) @PKG@.SackPool.save(this.k);
    } else if (this.mode == 5) {   // 0.8.30: the Auto-compact purchase - our pd line first, then SkyyCoins writes the purse
      if (@PKG@.VoidStore.saveNow(this.k)) {
        Object f = @PKG@.SackPool.bridge().get("coins:fn:flush");
        if (f instanceof java.util.function.Function) ((java.util.function.Function) f).apply(this.k);
      }
    }''')

# ---------------------------------------------------------------- VoidCompact (before the Void page markup: the page + the mirror call it)
VC_JAVA = r'''
# ================= 0.8.30 VoidCompact: AUTO-COMPACT PER BAG + CRAFTING OPENS ENCHANTED ITEMS (tools/sacks_0_8_30_patch.py) =================
# BASE[i] -> ENCH[i] = tools/skyyench.py item rows (+ the alloys); RATIO = the Compressing recipe's 100 (never a row: another number would
# make or destroy items against the recipe / the Bazaar). Saved per profile in pd/<key>.properties (VoidState.extra, kept by every version):
# comp.<Category>=1 (bought), comp.off.<Category>=1 (paused).
vcm.addField(CtField.make("public static final String[] BASE = " + _jarr([b for b, _e in CMP_PAIRS]) + ";", vcm))
vcm.addField(CtField.make("public static final String[] ENCH = " + _jarr([e for _b, e in CMP_PAIRS]) + ";", vcm))
vcm.addField(CtField.make("public static final long RATIO = 100L;", vcm))
vcm.addField(CtField.make('public static final String RSUF = "_Recipe_Generated_0";', vcm))
vcm.addField(CtField.make("public static final java.util.HashMap BI = new java.util.HashMap();", vcm))
vcm.addField(CtField.make("public static final java.util.HashMap EI = new java.util.HashMap();", vcm))
vcm.addField(CtField.make("public static volatile boolean READY = false;", vcm))
vcm.addField(CtField.make("public static final java.util.concurrent.atomic.AtomicLong MADE = new java.util.concurrent.atomic.AtomicLong();", vcm))
vcm.addField(CtField.make("public static final java.util.concurrent.atomic.AtomicLong OPENED = new java.util.concurrent.atomic.AtomicLong();", vcm))
vcm.addMethod(CtNewMethod.make(jt(r"""
public static synchronized void init() {
  if (READY) return;
  for (int i = 0; i < BASE.length; i++) { BI.put(BASE[i], Integer.valueOf(i)); EI.put(ENCH[i], Integer.valueOf(i)); }
  READY = true;
}"""), vcm))
vcm.addMethod(CtNewMethod.make(jt(r"""
public static int idxBase(String id) {
  if (id == null) return -1;
  if (!READY) init();
  Integer v = (Integer) BI.get(id);
  return v == null ? -1 : v.intValue();
}"""), vcm))
vcm.addMethod(CtNewMethod.make(jt(r"""
public static int idxEnch(String id) {
  if (id == null) return -1;
  if (!READY) init();
  Integer v = (Integer) EI.get(id);
  return v == null ? -1 : v.intValue();
}"""), vcm))
# does item b carry resource type rt (the engine Item's own list)
vcm.addMethod(CtNewMethod.make(jt(r"""
public static boolean hasRt(String b, String rt) {
  if (b == null || rt == null) return false;
  try {
    @ITM@ it = @PKG@.ProcBench.item(b);
    if (it == null) return false;
    com.hypixel.hytale.protocol.ItemResourceType[] r = it.getResourceTypes();
    for (int i = 0; r != null && i < r.length; i++) if (r[i] != null && rt.equals(r[i].id)) return true;
  } catch (Throwable t) { }
  return false;
}"""), vcm))
# one recipe's inputs: "!nv:<base>" when it uses an Enchanted item AND that item's base (by id or a resource type the base has) - such a
# recipe never gets the base's virtual stacks (it could pay the same Enchanted item twice)
vcm.addMethod(CtNewMethod.make(jt(r"""
public static void markers(java.util.Set s, @MQ@[] in) {
  if (s == null || in == null) return;
  for (int i = 0; i < in.length; i++) {
    if (in[i] == null || in[i].getItemId() == null) continue;
    int x = idxEnch(in[i].getItemId());
    if (x < 0) continue;
    String b = BASE[x];
    s.add("!e:" + b);   // fixer 2: some recipe of this set uses b's Enchanted item (the pocket rule in BagMirror.virtuals)
    for (int j = 0; j < in.length; j++) {
      if (j == i || in[j] == null) continue;
      if (b.equals(in[j].getItemId()) || (in[j].getItemId() == null && hasRt(b, in[j].getResourceTypeId()))) s.add("!nv:" + b);
    }
  }
}"""), vcm))
vcm.addMethod(CtNewMethod.make(jt(r"""
public static java.util.function.Function fn(String key) {
  try { Object o = @PKG@.SackPool.bridge().get(key); return (o instanceof java.util.function.Function) ? (java.util.function.Function) o : null; }
  catch (Throwable t) { return null; }
}"""), vcm))
# the shared coin curve (SkyyCoins coins:fn:curve, 1.0 = Lv 10); without it x1.0
vcm.addMethod(CtNewMethod.make(jt(r"""
public static double curve(int lv) {
  try {
    java.util.function.Function g = fn("coins:fn:curve");
    if (g != null) {
      Object r = g.apply(new Object[] { Integer.valueOf(lv) });
      if (r instanceof Number) { double d = ((Number) r).doubleValue(); if (d > 0.0 && d < 1000000000.0) return d; }
    }
  } catch (Throwable t) { @PKG@.KnowSync.warnOnce("auto-compact: coins:fn:curve failed - price x1.0: " + t); }
  return 1.0;
}"""), vcm))
vcm.addMethod(CtNewMethod.make(jt(r"""
public static long round7(double x) {
  if (x <= 0.0) return 0L;
  double st = x < 1000.0 ? 10.0 : (x < 10000.0 ? 100.0 : (x < 100000.0 ? 500.0 : 5000.0));
  return (long) (st * Math.floor(x / st + 0.5));
}"""), vcm))
_CMP_SW = "".join("  if (ci == %d) return (long) @PKG@.SackCfg.CMP_COINS_%s;\n" % (_i, _c.upper()) for _i, _c in enumerate(PD_CATS)) + "  return 0L;\n"
vcm.addMethod(CtNewMethod.make(jt(r"""
public static long coinsRow(int ci) {
@CATSW@}""".replace("@CATSW@", _CMP_SW)), vcm))
vcm.addMethod(CtNewMethod.make(jt(r"""
public static long price(int ci) {
  long b = coinsRow(ci);
  if (b <= 0L) return 0L;
  double x = (double) b * curve(@PKG@.SackCfg.CMP_LEVEL);
  if (x > 1000000000000.0) x = 1000000000000.0;
  long r = round7(x);
  return r < 10L ? 10L : r;   // fixer 2: a priced row never rounds down to free (a row of 4, or a tiny curve value)
}"""), vcm))
vcm.addMethod(CtNewMethod.make(jt(r"""
public static long coins(java.util.UUID u) {
  try {
    java.util.function.Function g = fn("coins:fn:get");
    Object r = g == null ? null : g.apply(u);
    return r instanceof Number ? ((Number) r).longValue() : -1L;
  } catch (Throwable t) { return -1L; }
}"""), vcm))
vcm.addMethod(CtNewMethod.make(jt(r"""
public static boolean refund(java.util.UUID u, long n) {
  if (n <= 0L) return true;
  try {
    java.util.function.Function g = fn("coins:fn:add");
    if (g == null) return false;
    return g.apply(new Object[] { u, Long.valueOf(n) }) instanceof Number;
  } catch (Throwable t) { return false; }
}"""), vcm))
vcm.addMethod(CtNewMethod.make(jt(r"""
public static boolean bought(String k, int ci) {
  if (k == null || ci < 0 || ci >= @PKG@.SackDefs.CATS.length) return false;
  @PKG@.VoidState s = @PKG@.VoidStore.st(k);
  return s != null && "1".equals(s.extra.getProperty("comp." + @PKG@.SackDefs.CATS[ci]));
}"""), vcm))
vcm.addMethod(CtNewMethod.make(jt(r"""
public static boolean paused(String k, int ci) {
  if (k == null || ci < 0 || ci >= @PKG@.SackDefs.CATS.length) return false;
  @PKG@.VoidState s = @PKG@.VoidStore.st(k);
  return s != null && "1".equals(s.extra.getProperty("comp.off." + @PKG@.SackDefs.CATS[ci]));
}"""), vcm))
vcm.addMethod(CtNewMethod.make(jt(r"""
public static boolean active(String k, int ci) {
  return @PKG@.SackCfg.CMP_ON && bought(k, ci) && !paused(k, ci);
}"""), vcm))
# how many pairs live in bag ci (their base's home); coll != null: only those whose Enchanted recipe is unlocked
vcm.addMethod(CtNewMethod.make(jt(r"""
public static int pairsIn(int ci, java.util.Set coll) {
  if (ci < 0 || ci >= @PKG@.SackDefs.CATS.length) return 0;
  String cat = @PKG@.SackDefs.CATS[ci];
  int n = 0;
  for (int i = 0; i < BASE.length; i++) {
    if (!cat.equals(@PKG@.SackDefs.homeOf(BASE[i])) || @PKG@.SackDefs.homeOf(ENCH[i]) == null) continue;
    if (coll != null && !coll.contains(ENCH[i] + RSUF)) continue;
    n++;
  }
  return n;
}"""), vcm))
# the pool steps (one lock: SackPool.add's monitor, reentrant). pack0: up to n x (RATIO base -> 1 Enchanted); returns how many packed
vcm.addMethod(CtNewMethod.make(jt(r"""
public static long pack0(String k, String b, String e, long n) {
  long h = @PKG@.SackPool.get(k, b);
  long m = h / RATIO;
  if (m > n) m = n;
  if (m <= 0L) return 0L;
  @PKG@.SackPool.add(k, b, -(m * RATIO));
  @PKG@.SackPool.add(k, e, m);
  return m;
}"""), vcm))
vcm.addMethod(CtNewMethod.make(jt(r"""
public static long pack(String k, String b, String e, long n) {
  synchronized (@PKG@.SackPool.class) { return pack0(k, b, e, n); }
}"""), vcm))
# split0: up to n Enchanted -> RATIO base each; returns how many opened
vcm.addMethod(CtNewMethod.make(jt(r"""
public static long split0(String k, String e, String b, long n) {
  long h = @PKG@.SackPool.get(k, e);
  long m = h < n ? h : n;
  if (m <= 0L) return 0L;
  @PKG@.SackPool.add(k, e, -m);
  @PKG@.SackPool.add(k, b, m * RATIO);
  return m;
}"""), vcm))
vcm.addMethod(CtNewMethod.make(jt(r"""
public static long split(String k, String e, String b, long n) {
  synchronized (@PKG@.SackPool.class) { return split0(k, e, b, n); }
}"""), vcm))
# open0: a craft took d of base b (loose + virtual stacks): loose first, then the fewest Enchanted e; the change stays as loose b.
# Returns the Enchanted opened (the mirror never offers more than loose + RATIO x Enchanted, so a clamp here = an accounting error)
vcm.addMethod(CtNewMethod.make(jt(r"""
public static long open0(String k, String b, String e, long d) {
  if (d <= 0L) return 0L;
  long l = @PKG@.SackPool.get(k, b);
  if (d <= l) { @PKG@.SackPool.add(k, b, -d); return 0L; }
  long need = d - l;
  long n = (need + RATIO - 1L) / RATIO;
  long h = @PKG@.SackPool.get(k, e);
  if (n > h) {
    long shortBy = d - l - h * RATIO;
    @PKG@.SackPool.warn("auto-open for " + k + ": a craft used " + d + " " + b + " but only " + l + " + " + h + " Enchanted were there - clamped, " + shortBy + " short (accounting error, report this)");
    try { @PKG@.CraftLog.later(k, "CRAFT-OPEN-SHORT " + b + " used " + d + " had " + l + " loose + " + h + " " + e + " short " + shortBy + " (accounting error)"); } catch (Throwable t0) { }
    n = h;
  }
  @PKG@.SackPool.add(k, e, -n);
  @PKG@.SackPool.add(k, b, n * RATIO - d);
  return n;
}"""), vcm))
vcm.addMethod(CtNewMethod.make(jt(r"""
public static long openL(String k, String b, String e, long d) {
  synchronized (@PKG@.SackPool.class) { return open0(k, b, e, d); }
}"""), vcm))
vcm.addMethod(CtNewMethod.make(jt(r"""
public static long open(String k, String b, String e, long d) {
  long n = openL(k, b, e, d);
  if (n > 0L) {
    OPENED.addAndGet(n);
    try { @PKG@.CraftLog.later(k, "CRAFT-OPEN " + e + " " + n + " -> " + b + " " + (n * RATIO) + " (a craft used " + d + ", change back in the bag)"); } catch (Throwable t) { }
  }
  return n;
}"""), vcm))
# a refused / refunded craftPay: the Enchanted items its payment opened are packed back (base -> Enchanted, as many as the pool allows)
vcm.addMethod(CtNewMethod.make(jt(r"""
public static long repack(String k, java.util.Map brk) {
  if (k == null || brk == null || brk.isEmpty()) return 0L;
  @PKG@.BagMirror.beforeTake(k);
  long t = 0L;
  java.util.Iterator it = brk.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry en = (java.util.Map.Entry) it.next();
    String b = (String) en.getKey();
    int x = idxBase(b);
    if (x < 0) continue;
    long n = ((Long) en.getValue()).longValue();
    long m = pack(k, b, ENCH[x], n);
    t += m;
    try { @PKG@.BagMirror.afterTake(k, b); } catch (Throwable t1) { }
    try { @PKG@.CraftLog.later(k, "CRAFT-OPEN-UNDO " + ENCH[x] + " " + m + " of " + n + " packed back (the craft was refused / refunded)"); } catch (Throwable t2) { }
  }
  return t;
}"""), vcm))
# THE COMPACTOR (world thread, end of the 2 s sweep): every bag with the upgrade on, every unlocked pair, every full 100 -> 1 Enchanted
vcm.addMethod(CtNewMethod.make(jt(r"""
public static long run(java.util.UUID u, String k, java.util.HashMap caps) {
  if (u == null || k == null || !@PKG@.SackCfg.CMP_ON) return 0L;
  @PKG@.VoidState s = @PKG@.VoidStore.st(k);
  if (s == null || s.first <= 0L) return 0L;
  String[] cats = @PKG@.SackDefs.CATS;
  boolean any = false;
  for (int c = 0; c < cats.length; c++) if (active(k, c)) any = true;
  if (!any) return 0L;
  java.util.HashSet coll = @PKG@.KnowSync.collShared(u);
  if (coll == null) return 0L;
  if (!READY) init();
  long made = 0L;
  long[] used = null;
  boolean synced = false;
  for (int i = 0; i < BASE.length; i++) {
    String b = BASE[i];
    String e = ENCH[i];
    int ci = @PKG@.SackDefs.catIndex(@PKG@.SackDefs.homeOf(b));
    if (ci < 0 || !active(k, ci)) continue;
    String ce = @PKG@.SackDefs.homeOf(e);
    int ei = @PKG@.SackDefs.catIndex(ce);
    if (ei < 0 || !coll.contains(e + RSUF)) continue;
    if (@PKG@.SackPool.get(k, b) < RATIO) continue;
    if (!synced) { @PKG@.BagMirror.beforeTake(k); synced = true; }   // live-mirror rule: book an open bench's takes first
    long n = @PKG@.SackPool.get(k, b) / RATIO;
    if (ei != ci) {   // the Enchanted item lives in another bag: it needs room there
      if (used == null) used = @PKG@.VoidStore.usedAll(k);
      Integer cap = caps == null ? null : (Integer) caps.get(ce);
      long room = (cap == null ? 0L : cap.longValue()) - used[ei];
      if (room < n) n = room;
    }
    if (n <= 0L) continue;
    long m = pack(k, b, e, n);
    if (m <= 0L) continue;
    if (used != null) { used[ci] -= m * RATIO; used[ei] += m; }
    try { @PKG@.BagMirror.afterTake(k, b); } catch (Throwable t1) { }
    made += m;
    try { @PKG@.CraftLog.later(k, "VOID-COMPACT " + b + " -" + (m * RATIO) + " -> " + e + " +" + m); } catch (Throwable t2) { }
  }
  // fixer: the pool is dirty (SackPool.add) - the 10 s SackSaver saves it; an early save only under the sweep's crash-window rule (no
  // unsaved sweep in the pool, a save that runs at once), else a crash could keep this sweep's items in the inventory AND the Void
  if (made > 0L) { MADE.addAndGet(made); if (!@PKG@.SackPool.SWEPTQ.containsKey(k) && @PKG@.SackPool.quiet(k)) @PKG@.SackPool.saveSoon(k); }
  return made;
}"""), vcm))
# fixer: undo a not-paid purchase line (in memory + on disk now; a failed save stays dirty and the writer retries it)
vcm.addMethod(CtNewMethod.make(jt(r"""
public static void unbuy(@PKG@.VoidState s, String k, String cat) {
  s.extra.remove("comp." + cat);
  @PKG@.VoidStore.markDirty(k);
  try { @PKG@.VoidStore.saveNow(k); } catch (Throwable t) { }
}"""), vcm))
# THE PURCHASE (world thread, the page's Pay click). Fixer: the pd line FIRST, on disk now (a failed save = nothing taken), then the coins
# (refused = the line undone), a throw after the take = refund. So a crash never leaves the coins taken without the upgrade.
# shown = the price the Pay button showed (-1 = not checked): another price now = nothing taken
vcm.addMethod(CtNewMethod.make(jt(r"""
public static String buyAt(java.util.UUID u, String k, int ci, long shown) {
  String[] cats = @PKG@.SackDefs.CATS;
  if (u == null || k == null || ci < 0 || ci >= cats.length) return "-Unknown bag";
  String cat = cats[ci];
  if (pairsIn(ci, (java.util.Set) null) <= 0) return "=Nothing in " + cat + " has an Enchanted form yet - nothing was taken";
  @PKG@.VoidState s = @PKG@.VoidStore.st(k);
  if (s == null) return "-" + @PKG@.VoidStore.NOREAD + " - nothing was taken";
  if (s.first <= 0L) return "-The Void is still getting ready - try again in a moment";
  if (bought(k, ci)) return "=" + cat + " already has Auto-compact";
  // fixer 2: without SkyyCollections' unlocked recipes (coll:recipes) the compactor can never run - do not sell it then
  if (@PKG@.KnowSync.collShared(u) == null) return "-Collections is not ready yet (Auto-compact needs your unlocked Enchanted recipes) - nothing was taken";
  long cost = price(ci);
  if (shown >= 0L && shown != cost) return "=The price is now " + @PKG@.SacksPage.num(cost) + " coins - check it, then Pay again (nothing was taken)";
  java.util.function.Function g = null;
  if (cost > 0L) {
    g = fn("coins:fn:take");
    if (g == null) return "-Coins are not available right now - nothing was taken";
  }
  s.extra.setProperty("comp." + cat, "1");
  s.extra.remove("comp.off." + cat);
  @PKG@.VoidStore.markDirty(k);
  boolean saved = false;
  try { @PKG@.VoidStore.crash("cmpsave"); saved = @PKG@.VoidStore.saveNow(k); } catch (Throwable t) { saved = false; }
  if (!saved) {
    unbuy(s, k, cat);
    return "-The Void data could not be saved right now - nothing was taken";
  }
  if (cost > 0L) {
    boolean paid = false;
    try { paid = Boolean.TRUE.equals(g.apply(new Object[] { u, Long.valueOf(cost) })); } catch (Throwable t) { paid = false; @PKG@.SackPool.warn("auto-compact: coins:fn:take failed (nothing bought): " + t); }
    if (!paid) {
      unbuy(s, k, cat);
      long have = coins(u);
      if (have >= cost) return "-Coins are busy right now (a rebirth running?) - nothing was taken, try again in a moment";
      return "-Not enough coins (" + (have < 0L ? "?" : @PKG@.SacksPage.num(have)) + " / " + @PKG@.SacksPage.num(cost) + ") - nothing was taken";
    }
  }
  try {
    @PKG@.VoidStore.crash("cmpbuy");   // the harness's crash point (nothing in the game)
  } catch (Throwable t) {
    unbuy(s, k, cat);
    boolean back = refund(u, cost);
    try { @PKG@.CraftLog.later(k, (back ? "VOID-COMPACT-REFUND " : "VOID-COMPACT-REFUND-FAILED ") + cat + " " + cost + " coins (" + t + ")"); } catch (Throwable t2) { }
    if (!back) @PKG@.SackPool.warn("auto-compact: buying " + cat + " for " + k + " failed AND the " + cost + " coins could not be given back - give them back by hand: " + t);
    return "-Something went wrong - " + (back ? "your coins were given back" : "your coins could not be given back, tell an admin");
  }
  @PKG@.SackPool.runOnWriter(new @PKG@.VoidJob(5, k, u));   // the pd file is on disk already; then SkyyCoins writes the purse
  try { @PKG@.CraftLog.later(k, "VOID-COMPACT-BUY " + cat + " paid " + cost + " coins"); } catch (Throwable t3) { }
  @PKG@.SweepTask.INVDIRTY.put(u, Boolean.TRUE);   // the next 2 s sweep compacts at once
  return "+" + cat + " now has Auto-compact" + (cost > 0L ? " (" + @PKG@.SacksPage.num(cost) + " coins)" : "")
      + " - crafts and bag upgrades open Enchanted items; other mods' shop costs use loose items (Unpack)";
}"""), vcm))
vcm.addMethod(CtNewMethod.make(jt(r"""
public static String buy(java.util.UUID u, String k, int ci) {
  return buyAt(u, k, ci, -1L);
}"""), vcm))
vcm.addMethod(CtNewMethod.make(jt(r"""
public static String toggle(java.util.UUID u, String k, int ci) {
  String[] cats = @PKG@.SackDefs.CATS;
  if (k == null || ci < 0 || ci >= cats.length) return "-Unknown bag";
  @PKG@.VoidState s = @PKG@.VoidStore.st(k);
  if (s == null) return "-" + @PKG@.VoidStore.NOREAD;
  if (!bought(k, ci)) return "-Buy Auto-compact for " + cats[ci] + " first";
  boolean wasOff = paused(k, ci);
  if (wasOff) s.extra.remove("comp.off." + cats[ci]); else s.extra.setProperty("comp.off." + cats[ci], "1");
  @PKG@.VoidStore.markDirty(k);
  @PKG@.SackPool.runOnWriter(new @PKG@.VoidJob(2, k, u));
  if (u != null) @PKG@.SweepTask.INVDIRTY.put(u, Boolean.TRUE);
  return wasOff ? ("+Auto-compact is on again for " + cats[ci]) : ("=Auto-compact paused for " + cats[ci] + " - nothing compacts there until you turn it on");
}"""), vcm))
# fixer 2: the bodies of VoidStore's Enchanted helpers for the bag's rarity upgrade (stubs there - VoidCompact exists now).
# $1 = key, $2 = the cost line's id (encHave: every member of a tier line; openFor: one member), $3 = still needed, $4 = opened (base -> n)
vst.getDeclaredMethod("encHave").setBody(jt(r"""{
  if (!@PKG@.SackCfg.CRAFT_OPEN || $1 == null || $2 == null) return 0L;
  String[] mm = @PKG@.SackDefs.members($2);
  long h = 0L;
  for (int i = 0; mm != null && i < mm.length; i++) {
    int x = @PKG@.VoidCompact.idxBase(mm[i]);
    if (x >= 0) h += @PKG@.VoidCompact.RATIO * @PKG@.SackPool.get($1, @PKG@.VoidCompact.ENCH[x]);
  }
  return h;
}"""))
vst.getDeclaredMethod("openFor").setBody(jt(r"""{
  if (!@PKG@.SackCfg.CRAFT_OPEN || $1 == null || $2 == null || $3 <= 0L || $4 == null) return 0L;
  int x = @PKG@.VoidCompact.idxBase($2);
  if (x < 0) return 0L;
  long loose = @PKG@.SackPool.get($1, $2);
  if (loose >= $3) return 0L;
  long n = ($3 - loose + @PKG@.VoidCompact.RATIO - 1L) / @PKG@.VoidCompact.RATIO;
  String e = @PKG@.VoidCompact.ENCH[x];
  long m = @PKG@.VoidCompact.split($1, e, $2, n);
  if (m <= 0L) return 0L;
  Long pv = (Long) $4.get($2);
  $4.put($2, Long.valueOf(m + (pv == null ? 0L : pv.longValue())));
  @PKG@.VoidCompact.OPENED.addAndGet(m);
  try { @PKG@.BagMirror.afterTake($1, e); } catch (Throwable t) { }
  return m;
}"""))
vst.getDeclaredMethod("unopen").setBody(jt(r"""{
  if ($1 == null || $2 == null || $2.isEmpty()) return;
  java.util.Iterator it = $2.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry en = (java.util.Map.Entry) it.next();
    String b = (String) en.getKey();
    int x = @PKG@.VoidCompact.idxBase(b);
    if (x < 0) continue;
    long n = ((Long) en.getValue()).longValue();
    long m = @PKG@.VoidCompact.pack($1, b, @PKG@.VoidCompact.ENCH[x], n);
    if (m < n) @PKG@.SackPool.warn("bag upgrade rollback for " + $1 + ": only " + m + " of " + n + " " + @PKG@.VoidCompact.ENCH[x] + " packed back (the base items stay loose - nothing lost)");
    try { @PKG@.BagMirror.afterTake($1, b); } catch (Throwable t1) { }
    try { @PKG@.CraftLog.later($1, "VOID-UPGRADE-UNOPEN " + @PKG@.VoidCompact.ENCH[x] + " " + m + " of " + n + " packed back (the upgrade was refused)"); } catch (Throwable t2) { }
  }
}"""))
'''
P.rep('''# ---- the page markup (kit), sizes checked here
''', VC_JAVA.lstrip("\n") + '''# ---- the page markup (kit), sizes checked here
''')

# ---------------------------------------------------------------- the Void page: the Auto-compact box + Unpack
P.rep('''page.addField(CtField.make("public boolean confirm;", page))
''', '''page.addField(CtField.make("public boolean confirm;", page))
page.addField(CtField.make("public boolean cconfirm;", page))   # 0.8.30: the Auto-compact Buy -> Pay / Cancel step
''')
P.rep('''assert 16 + 24 + 20 + 20 + 3 * 34 + 44 <= V_UP_H, "upgrade box"
''', '''assert 16 + 24 + 20 + 20 + 3 * 34 + 44 <= V_UP_H, "upgrade box"
V_CMP_H = 8 + 24 + 46 + 4 + 36 + 8   # 0.8.30: the Auto-compact box (pad, title, text up to three lines - fixer 2, buttons, pad)
assert 70 + 22 + 38 + 6 + 44 + 4 + 44 + 4 + 44 + 10 + V_UP_H + 8 + V_CMP_H <= V_MAIN_H, ("0.8.30: side column with Unpack + the Auto-compact box", V_MAIN_H, V_CMP_H)
''')
P.rep('''    "info": SUI.status_line("SkyySInfo", color_expr="colorOf(this.info)", h=V_INFO_H),
}''', '''    # 0.8.30: Unpack (a selected Enchanted item) + the Auto-compact box (the upgrade box's look and buttons)
    "btns3": SUI.group("SkyyVBtnsC", "Left", h=44, anchor={"top": 4}),
    "unpack": SUI.button("SkyyVUnpack", "Unpack to inventory", "secondary", w=V_SIDE_W),
    "cmp": SUI.group("SkyyVCmp", "Top", w=V_SIDE_W, h=V_CMP_H, anchor={"top": 8}, pad=8, bg="well"),
    "cmptitle": SUI.label("SkyyVCmpTitle", "", "strong", w=V_SIDE_W - 16, h=24, size=16, col=J_("kcol", "#ffff55")),
    "cmpsub": SUI.label("SkyyVCmpSub", "", "default", w=V_SIDE_W - 16, h=46, size=13, wrap=True),   # fixer 2: room for 3 lines (3 x 15 px)
    "cmpbtnrow": SUI.group("SkyyVCmpBtns", "Left", h=36, anchor={"top": 4}),
    "cmpbuy": SUI.choose("kready", SUI.button("SkyyVCmpBuy", "Buy", "primary", "small", w=160),
                         SUI.button("SkyyVCmpBuy", "Buy", "primary", "small", w=160, disabled=True)),
    "cmpyes": SUI.button("SkyyVCmpYes", "Pay", "primary", "small", w=150),
    "cmpno": SUI.button("SkyyVCmpNo", "Cancel", "secondary", "small", w=150, anchor={"left": 8}, sound="cancel"),
    "cmptog": SUI.choose("kon", SUI.button("SkyyVCmpTog", "Pause", "secondary", "small", w=160),
                         SUI.button("SkyyVCmpTog", "Turn on", "primary", "small", w=160)),
    "info": SUI.status_line("SkyySInfo", color_expr="colorOf(this.info)", h=V_INFO_H),
}''')
P.rep('''page.addMethod(CtNewMethod.make(vpage(r\'\'\'
public void render(@UCB@ b, @UEB@ ev, @PLA@ player, String k, java.util.UUID u) {''', '''# 0.8.30: the Auto-compact box of bag ci (price -> Buy -> Pay / Cancel; bought: On / Paused with Pause / Turn on)
page.addMethod(CtNewMethod.make(vpage(r\'\'\'
public void compactBox(@UCB@ b, @UEB@ ev, java.util.UUID u, String k, int ci) {
  String cat = @PKG@.SackDefs.CATS[ci];
  int pairs = @PKG@.VoidCompact.pairsIn(ci, (java.util.Set) null);
  boolean bought = @PKG@.VoidCompact.bought(k, ci);
  boolean kon = bought && !@PKG@.VoidCompact.paused(k, ci);
  boolean kready = false;
  long cost = @PKG@.VoidCompact.price(ci);
  String kcol = "@C:caption@";
  String t1;
  String t2;
  if (pairs <= 0) {
    t1 = "Auto-compact";
    t2 = "Nothing in " + cat + " has an Enchanted form yet.";
  } else if (!bought) {
    kcol = "@C:gold@";
    t1 = "Auto-compact - " + (cost > 0L ? num(cost) + " coins" : "free");
    t2 = "100 of an item -> 1 Enchanted once its recipe is unlocked in Collections.";
    long have = @PKG@.VoidCompact.coins(u);
    kready = cost <= 0L || have < 0L || have >= cost;
    if (!kready) t2 = "You have " + num(have) + " coins. 100 items -> 1 Enchanted once bought.";
  } else {
    java.util.HashSet coll = @PKG@.KnowSync.collShared(u);
    java.util.Set cs0 = new java.util.HashSet();
    if (coll != null) cs0 = coll;
    int un = @PKG@.VoidCompact.pairsIn(ci, cs0);
    kcol = kon ? "@C:have@" : "@C:caption@";
    t1 = kon ? "Auto-compact: On" : "Auto-compact: Paused";
    t2 = kon ? (un + " of " + pairs + " items unlocked: each 100 -> 1 Enchanted. Crafting opens them.")
             : "Bought - nothing compacts here until you turn it on.";
    if (kon && "Mining".equals(cat)) t2 = un + " of " + pairs + " unlocked: 100 -> 1 Enchanted. Not yet: Rubble, Sand, Crystal.";   // fixer
    if (!@PKG@.SackCfg.CMP_ON) t2 = "Switched off on this server for now (Server Setup).";
  }
  if (!bought && pairs > 0 && kready && "Mining".equals(cat)) t2 = "100 -> 1 Enchanted once its recipe is unlocked. Not yet: Rubble, Sand, Crystal.";
  b.appendInline("#SkyyVSide", @@cmp@@);
  b.appendInline("#SkyyVCmp", @@cmptitle@@);
  b.set("#SkyyVCmpTitle.Text", (this.cconfirm && !bought && pairs > 0) ? ("Pay " + num(cost) + " coins for Auto-compact?") : t1);
  b.appendInline("#SkyyVCmp", @@cmpsub@@);
  b.set("#SkyyVCmpSub.Text", t2);
  b.appendInline("#SkyyVCmp", @@cmpbtnrow@@);
  if (pairs <= 0) {
    this.cconfirm = false;
  } else if (!bought) {
    if (this.cconfirm && kready) {
      b.appendInline("#SkyyVCmpBtns", @@cmpyes@@);
      b.appendInline("#SkyyVCmpBtns", @@cmpno@@);
      ev.addEventBinding(@BT@.Activating, "#SkyyVCmpYes", amtEvt("cmpok:" + ci + ":" + cost));   // fixer: + the price shown
      ev.addEventBinding(@BT@.Activating, "#SkyyVCmpNo", amtEvt("cmpno"));
    } else {
      this.cconfirm = false;
      b.appendInline("#SkyyVCmpBtns", @@cmpbuy@@);
      if (kready) ev.addEventBinding(@BT@.Activating, "#SkyyVCmpBuy", amtEvt("cmpbuy"));
    }
  } else {
    this.cconfirm = false;
    b.appendInline("#SkyyVCmpBtns", @@cmptog@@);
    ev.addEventBinding(@BT@.Activating, "#SkyyVCmpTog", amtEvt("cmptog:" + ci));
  }
}\'\'\'), page))
# 0.8.30 UNPACK: n Enchanted items -> RATIO x n base items, withdrawn to the storage (withdrawN: kept counts, the live-mirror rule); what
# did not fit packs back (under RATIO stays loose in the bag). Returns the result line.
page.addMethod(CtNewMethod.make(jt(r\'\'\'
public static String unpack(@PLA@ p, String k, String e, long n) {
  int x = @PKG@.VoidCompact.idxEnch(e);
  if (x < 0) return "-That item does not unpack";
  String b = @PKG@.VoidCompact.BASE[x];
  if (@PKG@.ProcBench.item(b) == null) return "-" + b + " is not a loaded item - nothing unpacked";
  if (p == null || p.getInventory() == null) return "-No inventory";
  @PKG@.BagMirror.beforeTake(k);
  long have = @PKG@.SackPool.get(k, e);
  if (have <= 0L) return "-None of it left in the Void";
  long want = n < have ? n : have;
  if (want > 640L) want = 640L;   // 64,000 items at most per click
  long m = @PKG@.VoidCompact.split(k, e, b, want);
  try { @PKG@.BagMirror.afterTake(k, e); } catch (Throwable t1) { }
  if (m <= 0L) return "-None of it left in the Void";
  long got = withdrawN(p, k, b, m * @PKG@.VoidCompact.RATIO);
  long left = m * @PKG@.VoidCompact.RATIO - got;
  long back = left >= @PKG@.VoidCompact.RATIO ? @PKG@.VoidCompact.pack(k, b, e, left / @PKG@.VoidCompact.RATIO) : 0L;
  try { @PKG@.BagMirror.afterTake(k, b); } catch (Throwable t2) { }
  long loose = left - back * @PKG@.VoidCompact.RATIO;
  try { @PKG@.CraftLog.later(k, "VOID-UNPACK " + e + " " + m + " -> " + b + " " + (m * @PKG@.VoidCompact.RATIO) + " (" + got + " to the inventory, " + back + " packed back, " + loose + " loose in the bag)"); } catch (Throwable t3) { }
  String nm = @PKG@.SackDefs.lineName(b);
  if (nm == null) nm = pretty(b);
  if (got <= 0L) return "-Your storage is full - nothing unpacked";
  return "+Unpacked " + num(got) + " " + nm + (loose > 0L ? " - " + num(loose) + " stay in the Void" : "");
}\'\'\'), page))
page.addMethod(CtNewMethod.make(vpage(r\'\'\'
public void render(@UCB@ b, @UEB@ ev, @PLA@ player, String k, java.util.UUID u) {''')
P.rep('''  if (sel != null) {
    b.set("#SkyyVSelName.Text", pretty(sel));
    b.set("#SkyyVSelCount.Text", "In the Void " + num(@PKG@.SackPool.get(k, sel)) + " - on you " + num((long) @PKG@.VoidStore.countIn(inv, sel, false)));''', '''  if (sel != null) {
    b.set("#SkyyVSelName.Text", pretty(sel));
    b.set("#SkyyVSelCount.Text", "In the Void " + num(@PKG@.SackPool.get(k, sel)) + " - on you " + num((long) @PKG@.VoidStore.countIn(inv, sel, false)));
    if (@PKG@.VoidCompact.idxEnch(sel) >= 0)   // 0.8.30: what one Enchanted item holds
      b.set("#SkyyVSelCount.Text", "In the Void " + num(@PKG@.SackPool.get(k, sel)) + " (100 each) - on you " + num((long) @PKG@.VoidStore.countIn(inv, sel, false)));''')
P.rep('''  ev.addEventBinding(@BT@.Activating, "#SkyyVDepAll", amtEvt("depall"));
  upgradeBox(b, ev, inv, k, u, ci, lv[ci], rk[ci], cap[ci], omni);
''', '''  ev.addEventBinding(@BT@.Activating, "#SkyyVDepAll", amtEvt("depall"));
  if (sel != null && @PKG@.VoidCompact.idxEnch(sel) >= 0) {   // 0.8.30: Unpack a selected Enchanted item
    b.appendInline("#SkyyVSide", @@btns3@@);
    b.appendInline("#SkyyVBtnsC", @@unpack@@);
    ev.addEventBinding(@BT@.Activating, "#SkyyVUnpack", amtEvt("unpack"));
  }
  upgradeBox(b, ev, inv, k, u, ci, lv[ci], rk[ci], cap[ci], omni);
  compactBox(b, ev, u, k, ci);   // 0.8.30
''')
P.rep('''      if (a.equals("tab:" + cats[c])) { this.cat = cats[c]; this.pageNo = 0; this.sel = null; this.confirm = false; this.info = ""; rebuild(); return; }''',
      '''      if (a.equals("tab:" + cats[c])) { this.cat = cats[c]; this.pageNo = 0; this.sel = null; this.confirm = false; this.cconfirm = false; this.info = ""; rebuild(); return; }''')
P.rep('''    if (a.equals("upg")) { this.confirm = true; this.info = "=Check the cost, then Pay - or Cancel"; rebuild(); return; }
''', '''    if (a.equals("upg")) { this.confirm = true; this.info = "=Check the cost, then Pay - or Cancel"; rebuild(); return; }
    if (a.equals("cmpno")) { this.cconfirm = false; this.info = ""; rebuild(); return; }   // 0.8.30
    if (a.equals("cmpbuy")) { this.cconfirm = true; this.info = "=Check the price, then Pay - or Cancel"; rebuild(); return; }
''')
P.rep('''    boolean wd = a.equals("wd");
    boolean dep = a.equals("dep");
''', '''    // 0.8.30: Auto-compact Pay / Pause / Turn on, Unpack
    if (a.startsWith("cmpok:") || a.startsWith("cmptog:")) {
      boolean buyIt = a.startsWith("cmpok:");
      int cci = -1;
      long shown = -1L;   // fixer: cmpok:<ci>:<the price the Pay button showed>
      String rest = a.substring(buyIt ? 6 : 7).trim();
      int sep = rest.indexOf(':');
      if (sep >= 0) {
        try { shown = Long.parseLong(rest.substring(sep + 1).trim()); } catch (Throwable t4) { shown = -1L; }
        rest = rest.substring(0, sep);
      }
      try { cci = Integer.parseInt(rest.trim()); } catch (Throwable t3) { cci = -1; }
      this.cconfirm = false;
      this.info = cci < 0 ? "-Bad click" : (buyIt ? @PKG@.VoidCompact.buyAt(u, k, cci, shown) : @PKG@.VoidCompact.toggle(u, k, cci));
      if (buyIt) @PKG@.SackSnd.ok(u, this.info, 1);   // the Void upgrade sound ("+" = paid)
      rebuild();
      return;
    }
    if (a.equals("unpack")) {
      String amt = field(data, "@Amt");
      this.amount = amt;
      if (this.sel == null || @PKG@.VoidCompact.idxEnch(this.sel) < 0) { this.info = "-Pick an Enchanted item in the grid first"; rebuild(); return; }
      long n = parseAmt(amt, 1L);
      if (n == -2L) { this.info = "-Type a number (or leave it empty for one)"; rebuild(); return; }
      this.info = unpack(player, k, this.sel, n);
      @PKG@.SackPool.saveSoon(k);
      rebuild();
      return;
    }
    boolean wd = a.equals("wd");
    boolean dep = a.equals("dep");
''')

# ---------------------------------------------------------------- BagMirror: virtual base stacks + the loose-first booking
P.rep('''mir.addField(CtField.make("public String key;", mir))
''', '''mir.addField(CtField.make("public String key;", mir))
# 0.8.30: vpair = base id -> its Enchanted id for the bases the last rebuild offered as virtual stacks (RATIO per Enchanted item);
# broke = base id -> Enchanted items opened by sync() since the last clear (craftPay clears it before its sync, a refused / refunded
# payment packs them back)
mir.addField(CtField.make("public java.util.HashMap vpair;", mir))
mir.addField(CtField.make("public java.util.HashMap broke;", mir))
''')
P.rep('''public BagMirror(String key) {{
  this.key = key;
''', '''public BagMirror(String key) {{
  this.key = key;
  this.vpair = new java.util.HashMap();   // 0.8.30
  this.broke = new java.util.HashMap();
''')
P.rep('''# apply consumption: anything missing from the mirror vs. what we put there left the pool (the bench took it)
mir.addMethod(CtNewMethod.make(f"""
public int sync() {{
  int consumed = 0;
  for (int i = 0; i < 36; i++) {{
    if (this.slotIds[i] == null) continue;
    {IS} it = this.cont.getItemStack((short) i);
    int actual = (it == null || it.isEmpty()) ? 0 : it.getQuantity();
    if (actual < this.slotQty[i]) {{ int d = this.slotQty[i] - actual; {PKG}.SackPool.add(this.key, this.slotIds[i], -(long) d); consumed += d; this.slotQty[i] = actual; }}
  }}
  return consumed;
}}""", mir))''', '''# 0.8.30: the consumption of the bases with virtual stacks (base -> Long), booked loose first, then the fewest Enchanted (VoidCompact.open)
mir.addMethod(CtNewMethod.make(jt(r\'\'\'
public void book(java.util.HashMap vd) {
  java.util.Iterator it = vd.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry en = (java.util.Map.Entry) it.next();
    String b = (String) en.getKey();
    String e = (String) this.vpair.get(b);
    long d = ((Long) en.getValue()).longValue();
    long n = e == null ? 0L : @PKG@.VoidCompact.open(this.key, b, e, d);
    if (e == null) @PKG@.SackPool.add(this.key, b, -d);
    if (n > 0L) { Long pv = (Long) this.broke.get(b); this.broke.put(b, Long.valueOf((pv == null ? 0L : pv.longValue()) + n)); }
  }
}\'\'\'), mir))
# fixer: trimV = after a booking, trim what the mirror offers of every Enchanted item backing virtual stacks and of those bases to what the
# pool holds now (body set below, after fit0 exists): the next craft never sees an opened / taken Enchanted item again
mir.addMethod(CtNewMethod.make("public int trimV() { return 0; }", mir))
# apply consumption: anything missing from the mirror vs. what we put there left the pool (the bench took it)
# 0.8.30: a base with virtual stacks is summed over ALL its slots and booked once (loose first, then Enchanted opened, change kept)
mir.addMethod(CtNewMethod.make(f"""
public int sync() {{
  int consumed = 0;
  java.util.HashMap vd = null;
  for (int i = 0; i < 36; i++) {{
    if (this.slotIds[i] == null) continue;
    {IS} it = this.cont.getItemStack((short) i);
    int actual = (it == null || it.isEmpty()) ? 0 : it.getQuantity();
    if (actual < this.slotQty[i]) {{
      int d = this.slotQty[i] - actual;
      if (this.vpair != null && this.vpair.containsKey(this.slotIds[i])) {{
        if (vd == null) vd = new java.util.HashMap();
        Long pv = (Long) vd.get(this.slotIds[i]);
        vd.put(this.slotIds[i], Long.valueOf((pv == null ? 0L : pv.longValue()) + (long) d));
      }} else {PKG}.SackPool.add(this.key, this.slotIds[i], -(long) d);
      consumed += d;
      this.slotQty[i] = actual;
    }}
  }}
  if (vd != null) book(vd);
  if (consumed > 0 && this.vpair != null && !this.vpair.isEmpty()) trimV();   // fixer
  return consumed;
}}""", mir))''')
P.rep('''public static void addInputs(java.util.Set s, {MQ}[] in) {{
  for (int i = 0; in != null && i < in.length; i++) {{
    if (in[i] == null) continue;
    if (in[i].getItemId() != null) s.add(in[i].getItemId());
    else if (in[i].getResourceTypeId() != null) s.add(in[i].getResourceTypeId());
  }}
}}""", mir))''', '''public static void addInputs(java.util.Set s, {MQ}[] in) {{
  for (int i = 0; in != null && i < in.length; i++) {{
    if (in[i] == null) continue;
    if (in[i].getItemId() != null) s.add(in[i].getItemId());
    else if (in[i].getResourceTypeId() != null) s.add(in[i].getResourceTypeId());
  }}
  // 0.8.30: a RECIPE set (not a fuel / single-id set) may get virtual base stacks; "!nv:<base>" = a recipe using a base and its Enchanted item
  if (in != null && in.length > 0) {{ s.add("!open"); {PKG}.VoidCompact.markers(s, in); }}
}}""", mir))''')
P.rep('''# rebuild the mirror from the pool: only categories the player carries a bag for; up to 4 stacks per item, 36 slots.
''', '''# 0.8.30 THE VIRTUAL BASE STACKS: Object[]{ base, Enchanted, Long RATIO x Enchanted count } for each Enchanted item in the pool whose base
# a recipe of this mirror uses. Only in a recipe set ("!open"; bags.craftOpen on); never for a base a single recipe pays with its Enchanted
# item too ("!nv:<base>"). Fixer: the same per-recipe rule at benches / inventory crafting (the SkyyAlloy bench: Alloy_Ench_Bronze takes
# Enchanted Iron, Alloy_Bronze Iron bars - both offered): every bench craft syncs + rebuilds first (BenchLink.preCraft) and sync() trims
# the offer after each booking (trimV), so a craft never sees more than loose + RATIO x the Enchanted count.
mir.addMethod(CtNewMethod.make(jt(r\'\'\'
public static java.util.ArrayList virtuals(String k, java.util.HashMap caps, java.util.Set wanted) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (!@PKG@.SackCfg.CRAFT_OPEN || k == null || caps == null || wanted == null || !wanted.contains("!open")) return out;
  String[] bs = @PKG@.VoidCompact.BASE;
  String[] es = @PKG@.VoidCompact.ENCH;
  for (int i = 0; i < bs.length; i++) {
    long e = @PKG@.SackPool.get(k, es[i]);
    if (e <= 0L) continue;
    String cb = @PKG@.SackDefs.homeOf(bs[i]);
    String ce = @PKG@.SackDefs.homeOf(es[i]);
    if (cb == null || ce == null || !caps.containsKey(cb) || !caps.containsKey(ce)) continue;
    if (!wants(wanted, bs[i])) continue;
    if (wanted.contains("!nv:" + bs[i])) continue;
    // fixer 2: inventory crafting (the pocket window) has no pre-craft sync per click - while it shares the mirror, a base whose
    // Enchanted item ANY attached recipe uses gets no virtual stacks (two crafts between syncs could pay one Enchanted item twice)
    if (wanted.contains("!pocket") && wanted.contains("!e:" + bs[i])) continue;
    if (@PKG@.ProcBench.item(bs[i]) == null) continue;
    out.add(new Object[] { bs[i], es[i], Long.valueOf(e * @PKG@.VoidCompact.RATIO) });
  }
  return out;
}\'\'\'), mir))
# rebuild the mirror from the pool: only categories the player carries a bag for; up to 4 stacks per item, 36 slots.
''')
P.rep('''  for (int i = 0; i < 36; i++) {{ this.slotIds[i] = null; this.slotQty[i] = 0; }}
  StringBuilder sb = new StringBuilder();
  java.util.ArrayList entries = new java.util.ArrayList({PKG}.SackPool.pool(this.key).entrySet());
  java.util.Collections.sort(entries, new {PKG}.CountCmp());
  int n = entries.size();
''', '''  for (int i = 0; i < 36; i++) {{ this.slotIds[i] = null; this.slotQty[i] = 0; }}
  StringBuilder sb = new StringBuilder();
  java.util.ArrayList entries = new java.util.ArrayList({PKG}.SackPool.pool(this.key).entrySet());
  java.util.Collections.sort(entries, new {PKG}.CountCmp());
  java.util.ArrayList virt = virtuals(this.key, caps, wanted);   // 0.8.30: + the virtual base stacks (after the loose ones)
  java.util.HashMap vp = new java.util.HashMap();
  int n0 = entries.size();
  int n = n0 + virt.size();
''')
P.rep('''  for (int e = 0; e < n; e++) {{
    java.util.Map.Entry en = (java.util.Map.Entry) entries.get(e);''', '''  for (int e = 0; e < n0; e++) {{
    java.util.Map.Entry en = (java.util.Map.Entry) entries.get(e);''')
P.rep('''    max[e] = mx;
    want[e] = wanted != null && wants(wanted, id);
  }}
  int slot = 0;''', '''    max[e] = mx;
    want[e] = wanted != null && wants(wanted, id);
  }}
  for (int v = 0; v < virt.size(); v++) {{   // 0.8.30
    Object[] vo = (Object[]) virt.get(v);
    int e = n0 + v;
    ids[e] = (String) vo[0];
    left[e] = ((Long) vo[2]).longValue();
    int mx = 64;
    try {{ {IS} probe = new {IS}(ids[e], 1); if (probe.getItem() != null && probe.getItem().getMaxStack() > 0) mx = probe.getItem().getMaxStack(); }} catch (Throwable t) {{ }}
    max[e] = mx;
    want[e] = true;
    vp.put(vo[0], vo[1]);
  }}
  this.vpair = vp;
  int slot = 0;''')
P.rep('''public void empty() {{
  try {{ this.cont.clear(); }} catch (Throwable t) {{ }}
''', '''public void empty() {{
  try {{ this.cont.clear(); }} catch (Throwable t) {{ }}
  this.vpair = new java.util.HashMap();   // 0.8.30
''')
P.rep('''mir.addMethod(CtNewMethod.make(jt(r\'\'\'
public int fit(String id) {
  if (id == null) return 0;
  sync();
  long inPool = @PKG@.SackPool.get(this.key, id);''', '''# 0.8.30: fit0 = the trim of one id (no sync); a base with virtual stacks may be offered up to loose + RATIO x its Enchanted count;
# fit(Enchanted) also trims the virtual stacks it backs
mir.addMethod(CtNewMethod.make(jt(r\'\'\'
public int fit0(String id) {
  if (id == null) return 0;
  long inPool = @PKG@.SackPool.get(this.key, id);
  String ve = this.vpair == null ? null : (String) this.vpair.get(id);
  if (ve != null) inPool += @PKG@.VoidCompact.RATIO * @PKG@.SackPool.get(this.key, ve);''')
P.rep('''  if (removed > 0) { this.ver++; this.sig = "fit:" + this.ver; }   // content changed: a new version, and the next rebuild differs from it
  return removed;
}\'\'\'), mir))''', '''  if (removed > 0) { this.ver++; this.sig = "fit:" + this.ver; }   // content changed: a new version, and the next rebuild differs from it
  return removed;
}\'\'\'), mir))
mir.addMethod(CtNewMethod.make(jt(r\'\'\'
public int fit(String id) {
  if (id == null) return 0;
  sync();
  int removed = fit0(id);
  if (this.vpair != null && this.vpair.containsValue(id)) {
    java.util.ArrayList bs = new java.util.ArrayList();
    java.util.Iterator it = this.vpair.entrySet().iterator();
    while (it.hasNext()) { java.util.Map.Entry en = (java.util.Map.Entry) it.next(); if (id.equals(en.getValue())) bs.add(en.getKey()); }
    for (int i = 0; i < bs.size(); i++) removed += fit0((String) bs.get(i));
  }
  return removed;
}\'\'\'), mir))
mir.getDeclaredMethod("trimV").setBody(jt(r\'\'\'{
  if (this.vpair == null || this.vpair.isEmpty()) return 0;
  java.util.ArrayList ids = new java.util.ArrayList();
  java.util.Iterator it = this.vpair.entrySet().iterator();
  while (it.hasNext()) { java.util.Map.Entry en = (java.util.Map.Entry) it.next(); ids.add(en.getValue()); ids.add(en.getKey()); }
  int r = 0;
  for (int i = 0; i < ids.size(); i++) r += fit0((String) ids.get(i));
  return r;
}\'\'\'))   # fixer''')

# ---------------------------------------------------------------- /craft + craftPay sets are per-recipe ("!view")
P.rep('''public static java.util.HashSet wantedOf(java.util.List recipes) {{
  java.util.HashSet s = new java.util.HashSet();
''', '''public static java.util.HashSet wantedOf(java.util.List recipes) {{
  java.util.HashSet s = new java.util.HashSet();
  s.add("!view");   // 0.8.30: /craft syncs after every craft - the per-recipe rule for virtual base stacks
''')
P.rep('''public static java.util.HashSet wantedOne({CRR} r) {{
  java.util.HashSet s = new java.util.HashSet();
''', '''public static java.util.HashSet wantedOne({CRR} r) {{
  java.util.HashSet s = new java.util.HashSet();
  s.add("!view");   // 0.8.30
''')
P.rep('''"Materials come from your inventory, the Void and your Void Charms - sorted by tier." : "Materials come from your inventory and the Void - sorted by tier.");''',
      '''"Materials come from your inventory, the Void and your Void Charms - Enchanted items open when a craft needs them. Sorted by tier." : "Materials come from your inventory and the Void - Enchanted items open when a craft needs them. Sorted by tier.");   // 0.8.30''')

# ---------------------------------------------------------------- craftPay: record what its sync opened; refuse / refund pack it back
P.rep('''  java.util.HashMap bagB = @PKG@.CraftPage.snapshot(m.cont);
  // review fix 4: anything thrown after the debit still rolls back (slots from the snapshot, the bag part credited back)
''', '''  java.util.HashMap bagB = @PKG@.CraftPage.snapshot(m.cont);
  m.broke.clear();   // 0.8.30: what THIS payment's sync opens (a refusal / refund packs it back)
  java.util.HashMap brk = new java.util.HashMap();
  // review fix 4: anything thrown after the debit still rolls back (slots from the snapshot, the bag part credited back)
''')
P.rep('''    m.sync();   // the /craft rule: what left the mirror leaves the pool now
    synced = true;
''', '''    m.sync();   // the /craft rule: what left the mirror leaves the pool now
    synced = true;
    brk = new java.util.HashMap(m.broke);   // 0.8.30
''')
P.rep('''      try { m.sync(); } catch (Throwable tz) { }
    }
    bad = "internal error - nothing was taken";''', '''      try { m.sync(); } catch (Throwable tz) { }
      brk = new java.util.HashMap(m.broke);   // 0.8.30
    }
    bad = "internal error - nothing was taken";''')
P.rep('''  if (bad != null) return refuse(k, rid, times, bad, cs, snap, bagT);
  long now = System.currentTimeMillis();''', '''  if (bad != null) { Object[] rf = refuse(k, rid, times, bad, cs, snap, bagT); @PKG@.VoidCompact.repack(k, brk); return rf; }   // 0.8.30: + pack back
  long now = System.currentTimeMillis();''')
P.rep('''  RECEIPTS.put(rc, new Object[] { u, k, invT, bagT, new long[] { now, 0L }, rid, metaT });   // 0.8.24: + [6] the rolled stacks
  try { @PKG@.CraftLog.later(k, "CRAFT-PAY " + rid + " x" + times + " inventory " + invT + " bags " + bagT + " receipt " + rc + " (sacks:fn:craftPay)"); } catch (Throwable t3) { }''',
      '''  RECEIPTS.put(rc, new Object[] { u, k, invT, bagT, new long[] { now, 0L }, rid, metaT, brk });   // 0.8.24: + [6] the rolled stacks; 0.8.30: + [7] opened
  try { @PKG@.CraftLog.later(k, "CRAFT-PAY " + rid + " x" + times + " inventory " + invT + " bags " + bagT + (brk.isEmpty() ? "" : " opened Enchanted " + brk) + " receipt " + rc + " (sacks:fn:craftPay)"); } catch (Throwable t3) { }''')
P.rep('''    @PKG@.SackPool.add(k, (String) be.getKey(), (long) v);
    total += (long) v;
  }
  @IC@ c = p.getInventory().getCombinedStorageHotbarBackpack();''', '''    @PKG@.SackPool.add(k, (String) be.getKey(), (long) v);
    total += (long) v;
  }
  if (e.length > 7 && e[7] instanceof java.util.HashMap) @PKG@.VoidCompact.repack(k, (java.util.HashMap) e[7]);   // 0.8.30: opened -> packed back
  @IC@ c = p.getInventory().getCombinedStorageHotbarBackpack();''')

# ---------------------------------------------------------------- the sweep runs the compactor (world thread, settled key)
P.rep('''    items(p, k, u, caps0);
    SIG.put(u, sigOf(u));''', '''    items(p, k, u, caps0);
    // 0.8.30: Auto-compact (bags with the bought upgrade; before SIG so this sweep's own compacting is in the signature)
    try {{ {PKG}.VoidCompact.run(u, k, caps0); }} catch (Throwable tc) {{ {PKG}.KnowSync.warnOnce("auto-compact failed (retried on the next sweep): " + tc); }}
    SIG.put(u, sigOf(u));''')
# the start line (no migration: nobody has the upgrade yet)
P.rep('''  try {{ {PKG}.SackPool.LOG.at(java.util.logging.Level.INFO).log("[SkyySacks] auto-pickup this run: " + {PKG}.PickBook.stats()); }} catch (Throwable t) {{ }}   // 0.8.3''',
      '''  try {{ {PKG}.SackPool.LOG.at(java.util.logging.Level.INFO).log("[SkyySacks] auto-pickup this run: " + {PKG}.PickBook.stats()); }} catch (Throwable t) {{ }}   // 0.8.3
  try {{ {PKG}.SackPool.LOG.at(java.util.logging.Level.INFO).log("[SkyySacks] auto-compact this run: " + {PKG}.VoidCompact.MADE.get() + " Enchanted made, " + {PKG}.VoidCompact.OPENED.get() + " opened by crafting"); }} catch (Throwable t) {{ }}   // 0.8.30''')

P.rep('''  // 0.7.6 player Settings (research/Settings-Spec.md 2.2 / 3.4): every switch registered here, default ON
''', '''  // 0.8.30: no migration - the Auto-compact upgrade is new, every profile starts without it (nothing compacts until bought)
  getLogger().at(java.util.logging.Level.INFO).log("[SkyySacks] auto-compact: a per-bag upgrade bought with coins, off until bought (" + {PKG}.VoidCompact.BASE.length + " Enchanted items); crafting opens Enchanted items: " + {PKG}.SackCfg.CRAFT_OPEN);
  // 0.7.6 player Settings (research/Settings-Spec.md 2.2 / 3.4): every switch registered here, default ON
''')
# fixer 2: the pocket window's wanted set carries "!pocket" (BagMirror.virtuals' pocket rule); an empty set (recipes not loaded) stays unmarked
P.rep("""  if (!s.isEmpty()) FIELD = s;
  return s;""", """  if (!s.isEmpty()) { s.add("!pocket"); FIELD = s; }   // 0.8.30 fixer 2
  return s;""")
# ---------------------------------------------------------------- fixer 2: the bag's own rarity UPGRADE opens Enchanted items too
# (critic: once Auto-compact is bought, loose Wheat / Cobblestone never stays above 99, so a 2,000-Wheat upgrade could never be paid).
# Stubs here (VoidStore is compiled before VoidCompact exists); their bodies are set at the end of the VoidCompact section.
P.rep("""vst.addMethod(CtNewMethod.make(jt(r'''
public static String upgrade(@PLA@ p, java.util.UUID u, String k, int ci, int from) {""", """# 0.8.30 fixer 2: encHave = what a cost line can still get by opening Enchanted items in the Void (RATIO each, bags.craftOpen on);
# openFor = open the fewest Enchanted items of one member id so the pool holds rest loose (opened: base -> count); unopen = pack them back
vst.addMethod(CtNewMethod.make("public static long encHave(String k, String id) { return 0L; }", vst))
vst.addMethod(CtNewMethod.make("public static long openFor(String k, String id, long rest, java.util.HashMap opened) { return 0L; }", vst))
vst.addMethod(CtNewMethod.make("public static void unopen(String k, java.util.HashMap opened) { }", vst))
vst.addMethod(CtNewMethod.make(jt(r'''
public static String upgrade(@PLA@ p, java.util.UUID u, String k, int ci, int from) {""")
P.rep("""    long have = haveOf(k, inv, id);
    String un = @PKG@.SackDefs.lineName(id);   // 0.8.9: the real name
    if (have < need)""", """    long have = haveOf(k, inv, id) + encHave(k, id);   // 0.8.30 fixer 2: + what its Enchanted items in the Void hold
    String un = @PKG@.SackDefs.lineName(id);   // 0.8.9: the real name
    if (have < need)""")
P.rep("""  java.util.LinkedHashMap fromInv = new java.util.LinkedHashMap();
  String bad = null;""", """  java.util.LinkedHashMap fromInv = new java.util.LinkedHashMap();
  java.util.HashMap opened = new java.util.HashMap();   // 0.8.30 fixer 2: base -> Enchanted items opened for this upgrade
  String bad = null;""")
P.rep("""      String un = @PKG@.SackDefs.lineName(id);   // 0.8.9: the real name
      if (rest > 0L) bad = "-Not enough " + (un == null ? id : un) + " any more - nothing was taken";""", """      // 0.8.30 fixer 2: still short after every loose item -> open the fewest Enchanted items in the Void, the change stays loose
      for (int m2 = 0; m2 < ord.length && rest > 0L; m2++) {
        String mid2 = ord[m2];
        if (openFor(k, mid2, rest, opened) <= 0L) continue;
        long pp2 = @PKG@.SackPool.get(k, mid2);
        long tp2 = pp2 < rest ? pp2 : rest;
        if (tp2 > 0L) {
          @PKG@.SackPool.add(k, mid2, -tp2);
          Long pv2 = (Long) fromPool.get(mid2);
          fromPool.put(mid2, Long.valueOf(tp2 + (pv2 == null ? 0L : pv2.longValue())));
          rest -= tp2;
        }
      }
      String un = @PKG@.SackDefs.lineName(id);   // 0.8.9: the real name
      if (rest > 0L) bad = "-Not enough " + (un == null ? id : un) + " any more - nothing was taken";""")
P.rep("""    while (bi.hasNext()) { java.util.Map.Entry e = (java.util.Map.Entry) bi.next(); @PKG@.SackPool.add(k, (String) e.getKey(), ((Long) e.getValue()).longValue()); }
    return bad;""", """    while (bi.hasNext()) { java.util.Map.Entry e = (java.util.Map.Entry) bi.next(); @PKG@.SackPool.add(k, (String) e.getKey(), ((Long) e.getValue()).longValue()); }
    unopen(k, opened);   // 0.8.30 fixer 2: the opened Enchanted items packed back (the pool exactly as before)
    return bad;""")
P.rep("""  while (ai.hasNext()) { try { @PKG@.BagMirror.afterTake(k, (String) ai.next()); } catch (Throwable t) { } }
  try { @PKG@.CraftLog.later(k, "VOID-UPGRADE " + cat + " " + @PKG@.SackDefs.RNAME[cur] + " -> " + @PKG@.SackDefs.RNAME[to] + " paid Void " + fromPool + " inventory " + fromInv + (nowOmni ? " -> OMNI" : "")); } catch (Throwable t) { }""",
      """  while (ai.hasNext()) { try { @PKG@.BagMirror.afterTake(k, (String) ai.next()); } catch (Throwable t) { } }
  try { @PKG@.CraftLog.later(k, "VOID-UPGRADE " + cat + " " + @PKG@.SackDefs.RNAME[cur] + " -> " + @PKG@.SackDefs.RNAME[to] + " paid Void " + fromPool + " inventory " + fromInv + (opened.isEmpty() ? "" : " opened Enchanted " + opened) + (nowOmni ? " -> OMNI" : "")); } catch (Throwable t) { }""")
# the Void page's upgrade box counts the same (its Pay button follows VoidStore.upgrade's rule)
P.rep("""      long have = @PKG@.VoidStore.haveOf(k, inv, cid2);   // 0.8.8: a tier log line counts every log of the tier""",
      """      long have = @PKG@.VoidStore.haveOf(k, inv, cid2) + @PKG@.VoidStore.encHave(k, cid2);   // 0.8.8: a tier log line counts every log of the tier; 0.8.30 fixer 2: + Enchanted""")
assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.8.30 adds no system / command"
P.finish()
