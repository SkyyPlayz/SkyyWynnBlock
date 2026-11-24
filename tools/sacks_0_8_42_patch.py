"""Derive SkyySacks/build_skyysacks_0.8.42.py from the SET pin 0.8.41 (the GENERATED build_skyysacks_0.8.41.py; edit THIS file, then
regenerate: python tools/sacks_0_8_42_patch.py; never re-run sacks_0_8_41_patch.py on top of it). Every anchor is asserted once; at the end
every change is undone on a copy and compared with 0.8.41 (nothing else changed). Line endings kept.
Run:  python tools/sacks_0_8_42_patch.py   then   python SkyySacks/build_skyysacks_0.8.42.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.8.42.py [--dir <folder inside tools/dev/scratch/>] [--keep]

0.8.42 (2026-11-24, round link1) = SHARD LINK, the late-game pocket upgrade (SkyyShards 0.4.33 is the other half). Skyy 2026-11-14: "i want an
  upgrade that allos the shards to go straight into the pocket dimension with no need to collect. should it be a late game shard upgrade? or a
  late game pocket dimension upgrade?" + popup "Make Shard Link a late-game pocket upgrade?": "Yes, pocket upgrade" (docs/answered/world.md
  'SHARD LINK = POCKET UPGRADE') + 2026-11-23 "looks better. go head and build everything on your list."
  SURVEY: vanilla has no pocket / shard; no pack mod moves items between two of our mods. Built on our own pieces: the Auto-compact purchase
  (0.8.30: the pd line on disk BEFORE the coins) and the bag upgrade's payment (VoidStore.upgrade: the Void first, then plain inventory stacks,
  all or nothing) for the purchase; the pool meta lines (0.8.0 "~v2paid", 0.8.17 "~fishtok": written in the SAME atomic pool write as the
  items) for the crash-safe transfer.
  1. THE UPGRADE (per pocket; Mining / Foraging / Farming / Combat / Smithing - Fishing has no shard): the step after the pocket's top
     rarity - it needs that pocket at Legendary (or Omni) and costs coins (pd.link.coins.<Pocket> x the shared coin curve at pd.link.level,
     rounded like Auto-compact) + that pocket's Enchanted items (pd.link.cost.<Pocket>, itemId:amount pairs; taken from the Void first, then
     plain inventory stacks). The Pay click sends the price it showed (lnkok:<ci>:<price>; another price = nothing taken). Order: items
     booked -> the link.<Pocket> line saved (pd/<key>.properties) -> coins:fn:take; any refusal puts every item back and removes the line;
     a throw after the coins refunds them. Pause / Turn on (link.off.<Pocket>) like Auto-compact. Server Setup: pd.link.on (master switch),
     pd.link.level, pd.link.coins.<Pocket>, pd.link.cost.<Pocket>.
  2. THE /pd VOID PAGE: a "Shard Link" box under the six category tabs (the side column is full) - price + every cost item with have / need,
     Buy -> Pay / Cancel; bought: On / Paused with Pause / Turn on. SkyyMenu's pocket panel links here (its Upgrades button opens this page).
  3. THE BRIDGE sacks:fn:link (SackFn mode 25; java.lang types only; NOT world-thread bound - it works by profile key, every write under the
     pool monitor; never throws) - SkyyShards 0.4.33 calls it:
       {"state", key}                    -> "Mining,Combat" = the pockets whose link is on ("" none; null = not readable now)
       {"room", UUID, key, "id,id,.."}   -> "<Pocket>:<room>,...|<id>=<Pocket>,..." (only linked pockets; "" = nothing can go in now: no link,
                                            another profile active, or an unsaved sweep in the pool; null = not readable now)
       {"put", UUID, key, token, "id:qty,.."} -> "id:accepted,..." - each id into its own pocket (SackDefs.catOf), never past the room
                                            (re-read under the pool monitor), the items AND the marker "~lk.<token>" = "<time>|<accepted>" in
                                            ONE atomic pool write (saved before it answers; a failed save puts the memory back = null); the
                                            same token again = the same answer, nothing added twice; another profile active / an unsaved
                                            sweep = "" (nothing put, no marker)
       {"done", key, token}              -> the accepted text when that put is on disk, "" = it never happened, null = cannot tell now
       {"ack", key, token}               -> TRUE: the marker removed (the shard has recorded the result)
     FIX (critics): the items + the marker change under the pool monitor AND SAVELOCK (the saver never snapshots one without the other); the
     fsync runs outside the pool monitor (a world-thread SackPool.add never waits for the disk); a failed / deferred save keeps the put in
     memory as UNSAVED - put / done answer null (cannot tell) until a save works; ack answers null while the pool cannot be read.
     A put refuses ("") while the pool holds sweep additions not saved yet (SackPool.SWEPTQ - the sweep's crash-window rule: an early pool
     save could keep inventory items in the Void AND the inventory after a crash). Markers are never pruned without an ack (a pruned
     marker would read "never happened" = a duplicate).
  SAVED DATA: new pd lines link.<Pocket> / link.off.<Pocket>; new pool meta lines ~lk.<token> (both kinds of file keep unknown lines).
  No migration. 13 new Server Setup rows (live).
  ROLLBACK 0.8.42 -> 0.8.41 alone: safe - the link.* pd lines and ~lk.* pool lines stay (unknown, kept), nothing transfers any more (SkyyShards
  0.4.33 sees no sacks:fn:link and keeps the items in the shard = Collect as before); coins / items paid for a link are not refunded by a
  rollback (the link works again when 0.8.42 returns). Switch pd.link.on off and wait one minute first, so no shard transfer is half way.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G   # only its generic Patch helper (anchors asserted once, undo-compare, line endings kept)

P = G.Patch(os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.41.py"), os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.42.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.8.41"\n') and P.has("_C841") and not P.has("VoidLink"), "not the live generated SkyySacks 0.8.41"
SYS0, CMD0, CLS0 = P.s.count("registerSystem("), P.s.count("registerCommand("), P.s.count("makeClass(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.8.42 (2026-11-24"):].rstrip() + "\n"

P.rep('''  ROLLBACK to 0.8.40: safe alone (plain texts again).
''', '''  ROLLBACK to 0.8.40: safe alone (plain texts again).
''' + NOTE)
P.rep('VERSION = "0.8.41"\n', 'VERSION = "0.8.42"\n')

# ---- 1. the defaults (Python side; tables checked here)
P.rep('''CMP_COINS_DEF, CMP_LEVEL_DEF = 2000, 10
''', '''CMP_COINS_DEF, CMP_LEVEL_DEF = 2000, 10
# 0.8.42 SHARD LINK (tools/sacks_0_8_42_patch.py): the pockets a shard fills, the price (coins x the coin curve at pd.link.level - Lv 50 =
# x36.8 on the P7 curve: 10,000 -> about 368,000 coins, about an hour of Lv 50 income) + that pocket's Enchanted items (late game: Zone 2-3)
LINK_CATS = ("Mining", "Foraging", "Farming", "Combat", "Smithing")
LINK_COINS_DEF, LINK_LEVEL_DEF = 10000, 50
LINK_NEED = 3            # the pocket's rarity before the link: Legendary (the step after the top upgrade; Omni counts)
LINK_COST = {
    "Mining": [("Skyy_Ench_Cobblestone", 64), ("Skyy_Ench_Sandstone", 32), ("Skyy_Ench_Shale", 16)],
    "Foraging": [("Skyy_Ench_Oak", 64), ("Skyy_Ench_Maple", 32), ("Skyy_Ench_Gumboab", 16)],
    "Farming": [("Skyy_Ench_Wheat", 64), ("Skyy_Ench_Carrot", 32), ("Skyy_Ench_Corn", 16)],
    "Combat": [("Skyy_Ench_Bone", 64), ("Skyy_Ench_Linen", 16), ("Skyy_Ench_Venom", 8)],
    "Smithing": [("Skyy_Ench_Iron", 32), ("Skyy_Ench_Thorium", 16), ("Skyy_Ench_HideMedium", 16)],   # Enchanted bars / hides live in Smithing
}
def link_cost_text(c):
    return ",".join("%s:%d" % x for x in LINK_COST[c])
assert sorted(LINK_COST) == sorted(LINK_CATS) and all(1 <= len(v) <= 6 for v in LINK_COST.values())
assert all(i.startswith(EN.PREFIX) and i[len(EN.PREFIX):] in [t[0] for t in EN.TABLE] for v in LINK_COST.values() for i, _q in v), "0.8.42: link costs = Enchanted items"
''')
P.rep('''    "#pd.compact.coins.%s=%d" % (c, CMP_COINS_DEF) for c in PD_CATS]
SACK_CFG_TEXT = ''', '''    "#pd.compact.coins.%s=%d" % (c, CMP_COINS_DEF) for c in PD_CATS] + [
    # 0.8.42 Shard Link
    "# Shard Link (a late-game upgrade each player buys per pocket): that pocket's shard items go straight in, no Collect (SkyyShards 0.4.33+).",
    "# Needs the pocket at Legendary. Price = pd.link.coins.<Pocket> x the coin curve at pd.link.level + pd.link.cost.<Pocket> (Enchanted items).",
    "#pd.link.on=true", "#pd.link.level=%d" % LINK_LEVEL_DEF] + ["#pd.link.coins.%s=%d" % (c, LINK_COINS_DEF) for c in LINK_CATS] + [
    "#pd.link.cost.%s=%s" % (c, link_cost_text(c)) for c in LINK_CATS]
SACK_CFG_TEXT = ''')
P.rep('''                           + ["CMP_RECHECK"])   # 0.8.31
''', '''                           + ["CMP_RECHECK"])   # 0.8.31
# 0.8.42 Shard Link: the switch, the price level, coins + the Enchanted cost line of each pocket (a bad cost line keeps the last good one)
_PD_CFG_FIELDS += (["public static volatile boolean LINK_ON = true;", "public static volatile int LINK_LEVEL = %d;" % LINK_LEVEL_DEF]
                   + ["public static volatile int LINK_COINS_%s = %d;" % (c.upper(), LINK_COINS_DEF) for c in LINK_CATS]
                   + ["public static volatile String LINK_COST_%s = %s;" % (c.upper(), jlit(link_cost_text(c))) for c in LINK_CATS])
_PD_LOAD += ['  LINK_ON = boolKey(p, "pd.link.on", true);', '  LINK_LEVEL = intKey(p, "pd.link.level", %d, 1, 100);' % LINK_LEVEL_DEF]
_PD_LOAD += ['  LINK_COINS_%s = intKey(p, "pd.link.coins.%s", %d, 0, 1000000000);' % (c.upper(), c, LINK_COINS_DEF) for c in LINK_CATS]
for _c in LINK_CATS:
    _PD_LOAD.append('  { String lv = p.getProperty("pd.link.cost.%s"); if (lv != null && lv.trim().length() > 0) { if (parseCost(lv) != null) LINK_COST_%s = lv.trim(); '
                    'else @PKG@.SackPool.warn("config.properties: pd.link.cost.%s is not itemId:amount pairs - keeping " + LINK_COST_%s); } else LINK_COST_%s = %s; }'
                    % (_c, _c.upper(), _c, _c.upper(), _c.upper(), jlit(link_cost_text(_c))))
_PD_SIG += ' + "," + ' + ' + "," + '.join(["LINK_ON", "LINK_LEVEL"] + ["LINK_COINS_" + c.upper() for c in LINK_CATS] + ["LINK_COST_" + c.upper() for c in LINK_CATS])
''')
P.rep('''] + [_pdrow("pd.compact.coins." + c, "Auto-compact price: %s" % c, "void", "int", str(CMP_COINS_DEF), "0", "1000000000", "", "live",
            "Coins for the %s bag's Auto-compact upgrade (x the coin curve). 0 = free." % c, "CMP_COINS_" + c.upper())
     for c in PD_CATS]
''', '''] + [_pdrow("pd.compact.coins." + c, "Auto-compact price: %s" % c, "void", "int", str(CMP_COINS_DEF), "0", "1000000000", "", "live",
            "Coins for the %s bag's Auto-compact upgrade (x the coin curve). 0 = free." % c, "CMP_COINS_" + c.upper())
     for c in PD_CATS]
# 0.8.42 Shard Link (all live: the next purchase / transfer reads the SackCfg fields)
SACK_CFG_ROWS += [
    _pdrow("pd.link.on", "Shard Link (master switch)", "void", "bool", "true", "", "", "", "live",
           "On: pockets with Shard Link take their shard items straight in. Off: shard items wait for Collect.", "LINK_ON"),
    _pdrow("pd.link.level", "Shard Link price level", "void", "int", str(LINK_LEVEL_DEF), "1", "100", "", "live,adv",
           "The coin price x the coin curve at this level (10 = x1, 50 = about x37). Higher = dearer.", "LINK_LEVEL"),
] + [_pdrow("pd.link.coins." + c, "Shard Link price: %s" % c, "void", "int", str(LINK_COINS_DEF), "0", "1000000000", "", "live",
            "Coins for the %s pocket's Shard Link (x the coin curve). 0 = no coins." % c, "LINK_COINS_" + c.upper())
     for c in LINK_CATS
] + [_pdrow("pd.link.cost." + c, "Shard Link items: %s" % c, "voidcost", "text", link_cost_text(c), "", "400", "", "live,adv",
            "Items the %s Shard Link takes: itemId:amount pairs, commas between." % c,
            "LINK_COST_" + c.upper(), ";check=SackCfg.checkCost")
     for c in LINK_CATS]
''')

# ---- 2. the new class (declared with the other Void classes; written with them)
P.rep('''vcm = pool.makeClass(PKG + ".VoidCompact")   # 0.8.30: auto-compact per bag + crafting opens Enchanted items
''', '''vcm = pool.makeClass(PKG + ".VoidCompact")   # 0.8.30: auto-compact per bag + crafting opens Enchanted items
vln = pool.makeClass(PKG + ".VoidLink")      # 0.8.42: Shard Link (the pocket upgrade + sacks:fn:link)
''')
P.rep('''          vcm,    # 0.8.30: VoidCompact
''', '''          vcm,    # 0.8.30: VoidCompact
          vln,    # 0.8.42: VoidLink
''')

# ---- 3. VoidLink (after VoidCompact - it uses its coin helpers; before the page and SackFn, which call it)
VLINK = r'''
# ================= 0.8.42 SHARD LINK: VoidLink (tools/sacks_0_8_42_patch.py docstring) =================
assert set(LINK_CATS) < set(PD_CATS) and "Fishing" not in LINK_CATS, "0.8.42: every pocket but Fishing"
_LCAT_IDX = "".join("  if (ci == %d) return @PKG@.SackCfg.LINK_COST_%s;\n" % (PD_CATS.index(c), c.upper()) for c in LINK_CATS)
_LCOIN_IDX = "".join("  if (ci == %d) return (long) @PKG@.SackCfg.LINK_COINS_%s;\n" % (PD_CATS.index(c), c.upper()) for c in LINK_CATS)
vln.addField(CtField.make("public static final int NEED = %d;" % LINK_NEED, vln))
vln.addField(CtField.make("public static final java.util.concurrent.atomic.AtomicLong PUTS = new java.util.concurrent.atomic.AtomicLong();", vln))
vln.addField(CtField.make("public static final java.util.concurrent.atomic.AtomicLong ITEMS = new java.util.concurrent.atomic.AtomicLong();", vln))
vln.addField(CtField.make("public static final java.util.concurrent.atomic.AtomicLong REFUSED = new java.util.concurrent.atomic.AtomicLong();", vln))
vln.addMethod(CtNewMethod.make(jt(r"""
public static boolean linkable(int ci) {
  return ci >= 0 && ci < @PKG@.SackDefs.CATS.length && !"Fishing".equals(@PKG@.SackDefs.CATS[ci]);
}"""), vln))
vln.addMethod(CtNewMethod.make(jt(r"""
public static String costText(int ci) {
@LCOST@  return "";
}""".replace("@LCOST@", _LCAT_IDX)), vln))
vln.addMethod(CtNewMethod.make(jt(r"""
public static long coinsRow(int ci) {
@LCOIN@  return 0L;
}""".replace("@LCOIN@", _LCOIN_IDX)), vln))
vln.addMethod(CtNewMethod.make(jt(r"""
public static long price(int ci) {
  long b = coinsRow(ci);
  if (b <= 0L) return 0L;
  double x = (double) b * @PKG@.VoidCompact.curve(@PKG@.SackCfg.LINK_LEVEL);
  if (x > 1000000000000.0) x = 1000000000000.0;
  long r = @PKG@.VoidCompact.round7(x);
  return r < 10L ? 10L : r;
}"""), vln))
vln.addMethod(CtNewMethod.make(jt(r"""
public static boolean bought(String k, int ci) {
  if (k == null || !linkable(ci)) return false;
  @PKG@.VoidState s = @PKG@.VoidStore.st(k);
  return s != null && "1".equals(s.extra.getProperty("link." + @PKG@.SackDefs.CATS[ci]));
}"""), vln))
vln.addMethod(CtNewMethod.make(jt(r"""
public static boolean paused(String k, int ci) {
  if (k == null || !linkable(ci)) return false;
  @PKG@.VoidState s = @PKG@.VoidStore.st(k);
  return s != null && "1".equals(s.extra.getProperty("link.off." + @PKG@.SackDefs.CATS[ci]));
}"""), vln))
vln.addMethod(CtNewMethod.make(jt(r"""
public static boolean active(String k, int ci) {
  return @PKG@.SackCfg.LINK_ON && bought(k, ci) && !paused(k, ci);
}"""), vln))
# the pockets whose link is on now ("" none, null = the Void of k cannot be read now)
vln.addMethod(CtNewMethod.make(jt(r"""
public static String state(String k) {
  if (k == null || !@PKG@.SackPool.ready(k)) return null;
  @PKG@.VoidState s = @PKG@.VoidStore.st(k);
  if (s == null) return null;
  if (!@PKG@.SackCfg.LINK_ON) return "";
  StringBuilder b = new StringBuilder();
  String[] cats = @PKG@.SackDefs.CATS;
  for (int i = 0; i < cats.length; i++) if (active(k, i)) { if (b.length() > 0) b.append(','); b.append(cats[i]); }
  return b.toString();
}"""), vln))
# the room of every pocket (capacity at the saved best level x the rarity - the used items); a linked pocket only
vln.addMethod(CtNewMethod.make(jt(r"""
public static long[] rooms(String k) {
  String[] cats = @PKG@.SackDefs.CATS;
  long[] used = @PKG@.VoidStore.usedAll(k);
  long[] r = new long[cats.length];
  for (int i = 0; i < cats.length; i++) {
    if (!active(k, i)) { r[i] = -1L; continue; }
    long c = @PKG@.VoidStore.capOf(@PKG@.VoidStore.levelBest(k, i), @PKG@.VoidStore.rank(k, i)) - used[i];
    r[i] = c < 0L ? 0L : c;
  }
  return r;
}"""), vln))
# "" = nothing may go in now (no link on, another profile active, an unsaved sweep in the pool), null = cannot tell now
vln.addMethod(CtNewMethod.make(jt(r"""
public static String gate(java.util.UUID u, String k) {
  if (u == null || k == null) return null;
  if (!k.equals(@PKG@.SackPool.pkey(u))) return "";
  if (!@PKG@.SackPool.ready(k)) return null;
  @PKG@.VoidState s = @PKG@.VoidStore.st(k);
  if (s == null || s.first <= 0L) return null;
  if (@PKG@.SackPool.SWEPTQ.containsKey(k)) { REFUSED.incrementAndGet(); return ""; }
  String a = state(k);
  if (a == null) return null;
  return a.length() == 0 ? "" : "ok";
}"""), vln))
vln.addMethod(CtNewMethod.make(jt(r"""
public static String room(java.util.UUID u, String k, String ids) {
  String g = gate(u, k);
  if (g == null || g.length() == 0) return g;
  String[] cats = @PKG@.SackDefs.CATS;
  long[] r = rooms(k);
  StringBuilder b = new StringBuilder();
  for (int i = 0; i < cats.length; i++) if (r[i] >= 0L) { if (b.length() > 0) b.append(','); b.append(cats[i]).append(':').append(r[i]); }
  b.append('|');
  String[] a = ids == null ? new String[0] : ids.split(",");
  boolean first = true;
  for (int j = 0; j < a.length; j++) {
    String id = a[j].trim();
    if (id.length() == 0) continue;
    String c = @PKG@.SackDefs.catOf(id);
    int ci = @PKG@.SackDefs.catIndex(c);
    if (ci < 0 || r[ci] < 0L) continue;
    if (!first) b.append(',');
    b.append(id).append('=').append(c);
    first = false;
  }
  return b.toString();
}"""), vln))
vln.addMethod(CtNewMethod.make(jt(r"""
public static String accOf(Object v) {
  String s = v == null ? "" : String.valueOf(v);
  int bar = s.indexOf('|');
  return bar < 0 ? s : s.substring(bar + 1);
}"""), vln))
# FIX (link1 critics): the pool change and the marker are made under the pool monitor AND SAVELOCK (mut0 - the debounced saver snapshots under
# SAVELOCK only, so it can never write the items without the marker or the marker without the items); the fsync then runs with only
# SAVELOCK (fin - a world-thread SackPool.add never waits for the disk). A failed save keeps the change in memory, marked UNSAVED: done answers
# null (cannot tell) until a save works (it tries one), so a crash before any save = neither on disk = "never happened"; never a half state.
# The harness crash point "lnkput" sits inside the change (undone), "lnkput1" before the save (UNSAVED), "lnkput2" after it.
vln.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap UNSAVED = new java.util.concurrent.ConcurrentHashMap();", vln))
vln.addField(CtField.make("public static volatile boolean MUTHELD;", vln))    # harness: the change ran holding both locks
vln.addField(CtField.make("public static volatile boolean SAVEHELD;", vln))   # harness: the fsync ran holding the pool monitor (must stay false)
vln.addMethod(CtNewMethod.make(jt(r"""
public static boolean mut0(String k, java.util.Map mt, String mk, java.util.LinkedHashMap acc, String txt) {
  java.util.ArrayList did = new java.util.ArrayList();
  try {
    java.util.Iterator it = acc.entrySet().iterator();
    while (it.hasNext()) {
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      long g = ((Long) e.getValue()).longValue();
      if (g > 0L) { @PKG@.SackPool.add(k, (String) e.getKey(), g); did.add(e); }
    }
    mt.put(mk, String.valueOf(System.currentTimeMillis()) + "|" + txt);
    MUTHELD = Thread.holdsLock(@PKG@.SackPool.SAVELOCK) && Thread.holdsLock(@PKG@.SackPool.class);
    @PKG@.VoidStore.crash("lnkput");
    return true;
  } catch (Throwable t) {
    for (int i = 0; i < did.size(); i++) {
      java.util.Map.Entry e = (java.util.Map.Entry) did.get(i);
      @PKG@.SackPool.add(k, (String) e.getKey(), -((Long) e.getValue()).longValue());
    }
    mt.remove(mk);
    @PKG@.SackPool.warn("Shard Link: a transfer into " + k + " failed and was undone (the items stay in the shard): " + t);
    return false;
  }
}"""), vln))
vln.addMethod(CtNewMethod.make(jt(r"""
public static boolean mutL(String k, java.util.Map mt, String mk, java.util.LinkedHashMap acc, String txt) {
  synchronized (@PKG@.SackPool.SAVELOCK) { return mut0(k, mt, mk, acc, txt); }
}"""), vln))
# the put itself, under the pool monitor (put1 holds it): the marker first checked (a repeat answers the same), every id into its own pocket
# up to the room (re-read here), then the change + the marker (mutL). Returns a String = the answer now (a repeat / "" / null), or
# String[] { accepted } = changed in memory, fin saves it.
vln.addMethod(CtNewMethod.make(jt(r"""
public static Object put0(java.util.UUID u, String k, String tok, String items) {
  String mk = "~lk." + tok;
  java.util.concurrent.ConcurrentHashMap mt = (java.util.concurrent.ConcurrentHashMap) @PKG@.SackPool.PMETA.get(k);
  if (mt != null && mt.get(mk) != null) return accOf(mt.get(mk));
  if (@PKG@.SackPool.SWEPTQ.containsKey(k)) { REFUSED.incrementAndGet(); return ""; }
  long[] r = rooms(k);
  String[] a = items == null ? new String[0] : items.split(",");
  java.util.LinkedHashMap acc = new java.util.LinkedHashMap();
  for (int j = 0; j < a.length; j++) {
    String x = a[j].trim();
    int c = x.lastIndexOf(':');
    if (c <= 0) continue;
    String id = x.substring(0, c).trim();
    long q = 0L;
    try { q = Long.parseLong(x.substring(c + 1).trim()); } catch (Throwable t) { q = 0L; }
    if (id.length() == 0 || q <= 0L || acc.containsKey(id) || id.indexOf('|') >= 0 || id.indexOf('=') >= 0) continue;
    int ci = @PKG@.SackDefs.catIndex(@PKG@.SackDefs.catOf(id));
    long g = (ci < 0 || r[ci] <= 0L) ? 0L : (q < r[ci] ? q : r[ci]);
    if (g > 0L) r[ci] = r[ci] - g;
    acc.put(id, Long.valueOf(g));
  }
  StringBuilder sb = new StringBuilder();
  java.util.Iterator it = acc.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    if (sb.length() > 0) sb.append(',');
    sb.append((String) e.getKey()).append(':').append(((Long) e.getValue()).longValue());
  }
  String txt = sb.toString();
  if (mt == null) { mt = new java.util.concurrent.ConcurrentHashMap(); @PKG@.SackPool.PMETA.put(k, mt); }
  if (!mutL(k, mt, mk, acc, txt)) {
    if (mt.isEmpty()) @PKG@.SackPool.PMETA.remove(k);
    @PKG@.SackPool.DIRTY.put(k, Boolean.TRUE);
    return null;
  }
  return new String[] { txt };
}"""), vln))
vln.addMethod(CtNewMethod.make(jt(r"""
public static Object put1(java.util.UUID u, String k, String tok, String items) {
  synchronized (@PKG@.SackPool.class) { return put0(u, k, tok, items); }
}"""), vln))
# after the put is on disk: the pocket's own-items count (as before, under the pool monitor), the counters, the 2 s sweep's compact, the log
vln.addMethod(CtNewMethod.make(jt(r"""
public static long noteAll(String k, String txt) {
  String[] a = txt == null ? new String[0] : txt.split(",");
  long tot = 0L;
  for (int j = 0; j < a.length; j++) {
    int c = a[j].lastIndexOf(':');
    if (c <= 0) continue;
    String id = a[j].substring(0, c);
    long g = 0L;
    try { g = Long.parseLong(a[j].substring(c + 1).trim()); } catch (Throwable t) { g = 0L; }
    if (g <= 0L) continue;
    tot += g;
    @PKG@.VoidStore.noteIntake(k, @PKG@.SackDefs.catIndex(@PKG@.SackDefs.catOf(id)), g);
  }
  return tot;
}"""), vln))
vln.addMethod(CtNewMethod.make(jt(r"""
public static long noteL(String k, String txt) {
  synchronized (@PKG@.SackPool.class) { return noteAll(k, txt); }
}"""), vln))
vln.addMethod(CtNewMethod.make(jt(r"""
public static void post(java.util.UUID u, String k, String tok, String txt) {
  long tot = noteL(k, txt);
  PUTS.incrementAndGet();
  ITEMS.addAndGet(tot);
  if (u != null && tot > 0L) @PKG@.SweepTask.INVDIRTY.put(u, Boolean.TRUE);   // the next 2 s sweep compacts (Auto-compact) at once
  try { @PKG@.CraftLog.later(k, "VOID-LINK-PUT " + tok + " " + txt); } catch (Throwable t2) { }
}"""), vln))
# the save of a put, OUTSIDE the pool monitor (SAVELOCK only, inside saveOk). Never while the pool holds an unsaved sweep (the crash-window
# rule): then the put waits UNSAVED for the SackSaver's own save. null = not on disk yet (done tells later), else the accepted text.
vln.addMethod(CtNewMethod.make(jt(r"""
public static String fin(java.util.UUID u, String k, String tok, String txt) {
  String uk = k + "|" + tok;
  UNSAVED.put(uk, txt);
  boolean ok = false;
  try {
    SAVEHELD = Thread.holdsLock(@PKG@.SackPool.class);
    @PKG@.VoidStore.crash("lnkput1");
    ok = !@PKG@.SackPool.SWEPTQ.containsKey(k) && @PKG@.SackPool.saveOk(k);
  } catch (Throwable t) { ok = false; }
  if (!ok) {
    @PKG@.SackPool.DIRTY.put(k, Boolean.TRUE);
    @PKG@.KnowSync.warnOnce("Shard Link: a pocket file was not saved yet - that transfer waits for the next save (logged once; nothing is lost)");
    return null;
  }
  if (UNSAVED.remove(uk) != null) post(u, k, tok, txt);
  @PKG@.VoidStore.crash("lnkput2");
  return txt;
}"""), vln))
vln.addMethod(CtNewMethod.make(jt(r"""
public static String done0(String k, String tok) {
  java.util.Map mt = (java.util.Map) @PKG@.SackPool.PMETA.get(k);
  Object v = mt == null ? null : mt.get("~lk." + tok);
  return v == null ? "" : accOf(v);
}"""), vln))
vln.addMethod(CtNewMethod.make(jt(r"""
public static String doneL(String k, String tok) {
  synchronized (@PKG@.SackPool.class) { return done0(k, tok); }
}"""), vln))
# a put still UNSAVED: one save tried now (not while an unsaved sweep is in the pool) - on disk = the answer, else null (cannot tell yet)
vln.addMethod(CtNewMethod.make(jt(r"""
public static String done(String k, String tok) {
  if (k == null || tok == null || !@PKG@.SackPool.ready(k)) return null;
  String uk = k + "|" + tok;
  Object pend = UNSAVED.get(uk);
  if (pend != null) {
    boolean ok = false;
    try { ok = !@PKG@.SackPool.SWEPTQ.containsKey(k) && @PKG@.SackPool.saveOk(k); } catch (Throwable t) { ok = false; }
    if (!ok) return null;
    if (UNSAVED.remove(uk) != null) post((java.util.UUID) null, k, tok, (String) pend);
  }
  return doneL(k, tok);
}"""), vln))
vln.addMethod(CtNewMethod.make(jt(r"""
public static boolean ack0(String k, String tok) {
  java.util.Map mt = (java.util.Map) @PKG@.SackPool.PMETA.get(k);
  if (mt == null || mt.remove("~lk." + tok) == null) return false;
  if (mt.isEmpty()) @PKG@.SackPool.PMETA.remove(k);
  @PKG@.SackPool.DIRTY.put(k, Boolean.TRUE);
  return true;
}"""), vln))
vln.addMethod(CtNewMethod.make(jt(r"""
public static boolean ack(String k, String tok) {
  if (k == null || tok == null || !@PKG@.SackPool.ready(k)) return false;
  UNSAVED.remove(k + "|" + tok);
  synchronized (@PKG@.SackPool.class) { return ack0(k, tok); }
}"""), vln))
vln.addMethod(CtNewMethod.make(jt(r"""
public static String put(java.util.UUID u, String k, String tok, String items) {
  if (!@PKG@.SackPool.tokOk(tok) || tok.indexOf('|') >= 0) return null;
  if (k != null && UNSAVED.containsKey(k + "|" + tok)) return done(k, tok);   // this put is made, not on disk yet: done tells
  String g = gate(u, k);
  if (g == null || g.length() == 0) {
    if (g != null && k != null) {   // nothing may go in now - unless this exact put already happened (a repeat answers the same)
      String d = done(k, tok);
      if (d != null && d.length() > 0) return d;
    }
    return g;
  }
  Object r = put1(u, k, tok, items);
  if (!(r instanceof String[])) return (String) r;
  return fin(u, k, tok, ((String[]) r)[0]);
}"""), vln))
# sacks:fn:link - never throws; bad arguments = null
vln.addMethod(CtNewMethod.make(jt(r"""
public static Object call(Object o) {
  try {
    if (!(o instanceof Object[])) return null;
    Object[] a = (Object[]) o;
    if (a.length < 2 || !(a[0] instanceof String)) return null;
    String op = (String) a[0];
    if ("state".equals(op)) return (a[1] instanceof String) ? state((String) a[1]) : null;
    if ("done".equals(op) || "ack".equals(op)) {
      if (a.length < 3 || !(a[1] instanceof String) || !(a[2] instanceof String)) return null;
      if ("done".equals(op)) return done((String) a[1], (String) a[2]);
      if (!@PKG@.SackPool.ready((String) a[1])) return null;   // FIX: cannot tell now (FALSE would make the shard forget a marker still here)
      return ack((String) a[1], (String) a[2]) ? Boolean.TRUE : Boolean.FALSE;
    }
    if (a.length < 4 || !(a[1] instanceof java.util.UUID) || !(a[2] instanceof String) || !(a[3] instanceof String)) return null;
    java.util.UUID u = (java.util.UUID) a[1];
    if ("room".equals(op)) return room(u, (String) a[2], (String) a[3]);
    if ("put".equals(op) && a.length >= 5 && a[4] instanceof String) return put(u, (String) a[2], (String) a[3], (String) a[4]);
  } catch (Throwable t) { @PKG@.KnowSync.warnOnce("sacks:fn:link failed (logged once; the items stay in the shard): " + t); }
  return null;
}"""), vln))
# ---- THE PURCHASE (world thread, the page's Pay click): the items booked (the Void first, then plain inventory stacks; all or nothing),
# then the pd line on disk, then the coins; a refusal anywhere puts every item back and removes the line; a throw after the coins refunds.
vln.addMethod(CtNewMethod.make(jt(r"""
public static void giveBack(String k, @IC@[] cs, java.util.ArrayList snap, java.util.LinkedHashMap fromPool) {
  if (cs != null && snap != null) @PKG@.VoidStore.slotRestore(cs, snap);
  java.util.Iterator bi = fromPool.entrySet().iterator();
  while (bi.hasNext()) { java.util.Map.Entry e = (java.util.Map.Entry) bi.next(); @PKG@.SackPool.add(k, (String) e.getKey(), ((Long) e.getValue()).longValue()); }
}"""), vln))
vln.addMethod(CtNewMethod.make(jt(r"""
public static boolean unbuy(@PKG@.VoidState s, String k, String cat) {
  s.extra.remove("link." + cat);
  @PKG@.VoidStore.markDirty(k);
  boolean ok = false;
  try { @PKG@.VoidStore.crash("lnkunbuy"); ok = @PKG@.VoidStore.saveNow(k); } catch (Throwable t) { ok = false; }
  if (!ok) {   // FIX (critic): never silent - kept dirty, the VoidStore saver retries (memory already says "not bought")
    @PKG@.VoidStore.markDirty(k);
    @PKG@.SackPool.warn("Shard Link: the purchase of the " + cat + " link for " + k + " was undone, but the Void file could not be saved yet - retried by the next save");
  }
  return ok;
}"""), vln))
vln.addMethod(CtNewMethod.make(jt(r"""
public static String buyAt(@PLA@ p, java.util.UUID u, String k, int ci, long shown) {
  String[] cats = @PKG@.SackDefs.CATS;
  if (u == null || k == null || ci < 0 || ci >= cats.length) return "-Unknown pocket";
  String cat = cats[ci];
  if (!linkable(ci)) return "=No shard fills the " + cat + " pocket - there is nothing to link";
  if (!@PKG@.SackCfg.LINK_ON) return "-Shard Link is switched off on this server - nothing was taken";
  @PKG@.VoidState s = @PKG@.VoidStore.st(k);
  if (s == null) return "-" + @PKG@.VoidStore.NOREAD + " - nothing was taken";
  if (s.first <= 0L) return "-The Void is still getting ready - try again in a moment";
  if (bought(k, ci)) return "=" + cat + " already has Shard Link";
  int rk = @PKG@.VoidStore.rank(k, ci);
  if (rk < NEED) return "-Shard Link needs the " + cat + " pocket at " + @PKG@.SackDefs.RNAME[NEED] + " first (" + @PKG@.SackDefs.RNAME[rk] + " now) - nothing was taken";
  long cost = price(ci);
  if (shown >= 0L && shown != cost) return "=The price is now " + @PKG@.SacksPage.num(cost) + " coins - check it, then Pay again (nothing was taken)";
  java.util.LinkedHashMap need = @PKG@.SackCfg.parseCost(costText(ci));
  if (need == null) return "-This upgrade's cost is not set correctly (Server Setup) - nothing was taken";
  java.util.function.Function g = null;
  if (cost > 0L) {
    g = @PKG@.VoidCompact.fn("coins:fn:take");
    if (g == null) return "-Coins are not available right now - nothing was taken";
    long have0 = @PKG@.VoidCompact.coins(u);
    if (have0 >= 0L && have0 < cost) return "-Not enough coins (" + @PKG@.SacksPage.num(have0) + " / " + @PKG@.SacksPage.num(cost) + ") - nothing was taken";
  }
  @INV@ inv = p == null ? null : p.getInventory();
  if (inv == null) return "-No inventory";
  @PKG@.BagMirror.beforeTake(k);
  java.util.Iterator it = need.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    String id = (String) e.getKey();
    long n = ((Long) e.getValue()).longValue();
    long h = @PKG@.VoidStore.haveOf(k, inv, id);
    if (h < n) return "-Not enough " + @PKG@.SacksPage.pretty(id) + " (" + @PKG@.SacksPage.num(h) + " / " + @PKG@.SacksPage.num(n) + ") - nothing was taken";
  }
  @IC@[] cs = @PKG@.VoidStore.conts(inv);
  java.util.ArrayList snap = @PKG@.VoidStore.slotSnap(cs);
  java.util.LinkedHashMap fromPool = new java.util.LinkedHashMap();
  java.util.LinkedHashMap fromInv = new java.util.LinkedHashMap();
  String bad = null;
  try {
    it = need.entrySet().iterator();
    while (it.hasNext() && bad == null) {
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      String id = (String) e.getKey();
      long rest = ((Long) e.getValue()).longValue();
      String[] ord = @PKG@.VoidStore.takeOrder(k, inv, id);
      for (int m = 0; m < ord.length && rest > 0L; m++) {
        String mid = ord[m];
        long pp = @PKG@.SackPool.get(k, mid);
        long tp = pp < rest ? pp : rest;
        if (tp > 0L) {
          @PKG@.SackPool.add(k, mid, -tp);
          Long pv = (Long) fromPool.get(mid);
          fromPool.put(mid, Long.valueOf(tp + (pv == null ? 0L : pv.longValue())));
          rest -= tp;
        }
        if (rest > 0L) {
          long ic = (long) @PKG@.VoidStore.countIn(inv, mid, true);
          long ti = ic < rest ? ic : rest;
          if (ti > 0L) {
            long got = @PKG@.VoidStore.takePlain(cs, mid, ti);
            if (got > 0L) {
              Long iv = (Long) fromInv.get(mid);
              fromInv.put(mid, Long.valueOf(got + (iv == null ? 0L : iv.longValue())));
              rest -= got;
            }
          }
        }
      }
      if (rest > 0L) bad = "-Not enough " + @PKG@.SacksPage.pretty(id) + " any more - nothing was taken";
    }
  } catch (Throwable t) { bad = "-Internal error - nothing was taken"; @PKG@.SackPool.warn("Shard Link purchase failed and was rolled back: " + t); }
  if (bad != null) { giveBack(k, cs, snap, fromPool); return bad; }
  s.extra.setProperty("link." + cat, "1");
  s.extra.remove("link.off." + cat);
  @PKG@.VoidStore.markDirty(k);
  boolean saved = false;
  try { @PKG@.VoidStore.crash("lnksave"); saved = @PKG@.VoidStore.saveNow(k); } catch (Throwable t) { saved = false; }
  if (!saved) {
    unbuy(s, k, cat);
    giveBack(k, cs, snap, fromPool);
    return "-The Void data could not be saved right now - nothing was taken";
  }
  if (cost > 0L) {
    boolean paid = false;
    try { paid = Boolean.TRUE.equals(g.apply(new Object[] { u, Long.valueOf(cost) })); } catch (Throwable t) { paid = false; @PKG@.SackPool.warn("Shard Link: coins:fn:take failed (nothing bought): " + t); }
    if (!paid) {
      unbuy(s, k, cat);
      giveBack(k, cs, snap, fromPool);
      long have = @PKG@.VoidCompact.coins(u);
      if (have >= cost) return "-Coins are busy right now (a rebirth running?) - nothing was taken, try again in a moment";
      return "-Not enough coins (" + (have < 0L ? "?" : @PKG@.SacksPage.num(have)) + " / " + @PKG@.SacksPage.num(cost) + ") - nothing was taken";
    }
  }
  try {
    @PKG@.VoidStore.crash("lnkbuy");   // the harness's crash point (nothing in the game)
  } catch (Throwable t) {
    unbuy(s, k, cat);
    giveBack(k, cs, snap, fromPool);
    boolean back = @PKG@.VoidCompact.refund(u, cost);
    try { @PKG@.CraftLog.later(k, (back ? "VOID-LINK-REFUND " : "VOID-LINK-REFUND-FAILED ") + cat + " " + cost + " coins (" + t + ")"); } catch (Throwable t2) { }
    if (!back) @PKG@.SackPool.warn("Shard Link: buying " + cat + " for " + k + " failed AND the " + cost + " coins could not be given back - give them back by hand: " + t);
    return "-Something went wrong - your items are back and " + (back ? "your coins were given back" : "your coins could not be given back, tell an admin");
  }
  @PKG@.SackPool.runOnWriter(new @PKG@.VoidJob(4, k, (java.util.UUID) null));   // the pd line (on disk already) + the pool debit
  @PKG@.SackPool.runOnWriter(new @PKG@.VoidJob(5, k, u));                      // then SkyyCoins writes the purse
  java.util.Iterator ai = fromPool.keySet().iterator();
  while (ai.hasNext()) { try { @PKG@.BagMirror.afterTake(k, (String) ai.next()); } catch (Throwable t) { } }
  try { @PKG@.CraftLog.later(k, "VOID-LINK-BUY " + cat + " paid " + cost + " coins, Void " + fromPool + " inventory " + fromInv); } catch (Throwable t3) { }
  return "+The " + cat + " pocket now has Shard Link - your shards send their " + cat + " items straight here";
}"""), vln))
vln.addMethod(CtNewMethod.make(jt(r"""
public static String toggle(java.util.UUID u, String k, int ci) {
  String[] cats = @PKG@.SackDefs.CATS;
  if (k == null || ci < 0 || ci >= cats.length) return "-Unknown pocket";
  @PKG@.VoidState s = @PKG@.VoidStore.st(k);
  if (s == null) return "-" + @PKG@.VoidStore.NOREAD;
  if (!bought(k, ci)) return "-Buy Shard Link for " + cats[ci] + " first";
  boolean wasOff = paused(k, ci);
  if (wasOff) s.extra.remove("link.off." + cats[ci]); else s.extra.setProperty("link.off." + cats[ci], "1");
  @PKG@.VoidStore.markDirty(k);
  @PKG@.SackPool.runOnWriter(new @PKG@.VoidJob(2, k, u));
  return wasOff ? ("+Shard Link is on again for " + cats[ci]) : ("=Shard Link paused for " + cats[ci] + " - shard items wait in the shard until you turn it on");
}"""), vln))
'''
P.rep('''# fixer 2: the bodies of VoidStore's Enchanted helpers for the bag's rarity upgrade (stubs there - VoidCompact exists now).
''', VLINK.lstrip("\n") + '''# fixer 2: the bodies of VoidStore's Enchanted helpers for the bag's rarity upgrade (stubs there - VoidCompact exists now).
''')

# ---- 4. the Void page: the Shard Link box under the six tabs
P.rep('''page.addField(CtField.make("public boolean cconfirm;", page))   # 0.8.30: the Auto-compact Buy -> Pay / Cancel step
''', '''page.addField(CtField.make("public boolean cconfirm;", page))   # 0.8.30: the Auto-compact Buy -> Pay / Cancel step
page.addField(CtField.make("public boolean lconfirm;", page))   # 0.8.42: the Shard Link Buy -> Pay / Cancel step
''')
P.rep('''assert 16 + RF_LABEL_W + 3 * RF_BTN_W + 2 * RF_GAP <= VIN_W
J_ = SUI.J
''', '''assert 16 + RF_LABEL_W + 3 * RF_BTN_W + 2 * RF_GAP <= VIN_W
# 0.8.42: the Shard Link box sits in the tabs column under the Omni line (the side column is full): pad, title, up to 6 text lines, two button
# rows (Pay over Cancel - the column is 220 wide), pad
V_LNK_H = 8 + 22 + 92 + 4 + 36 + 4 + 36 + 8
assert 6 * (34 + 18 + 5 + 6) + 44 + 8 + V_LNK_H <= V_MAIN_H, ("0.8.42: tabs column with the Shard Link box", V_MAIN_H, V_LNK_H)
J_ = SUI.J
''')
P.rep('''    "info": SUI.status_line("SkyySInfo", color_expr="colorOf(this.info)", h=V_INFO_H),
}''', '''    "info": SUI.status_line("SkyySInfo", color_expr="colorOf(this.info)", h=V_INFO_H),
    # 0.8.42 Shard Link (the Auto-compact box's look and buttons, tabs-column wide)
    "lnk": SUI.group("SkyyVLnk", "Top", w=V_TAB_W, h=V_LNK_H, anchor={"top": 8}, pad=8, bg="well"),
    "lnktitle": SUI.label("SkyyVLnkTitle", "", "strong", w=V_TAB_W - 16, h=22, size=15, col=J_("lcol", "#ffff55")),
    "lnksub": SUI.label("SkyyVLnkSub", "", "default", w=V_TAB_W - 16, h=92, size=13, wrap=True, col=J_("lscol", "#ffffff")),
    "lnkbtnrow": SUI.group("SkyyVLnkBtns", "Left", h=36, anchor={"top": 4}),
    "lnkbuy": SUI.choose("lready", SUI.button("SkyyVLnkBuy", "Buy", "primary", "small", w=V_TAB_W - 16),
                         SUI.button("SkyyVLnkBuy", "Buy", "primary", "small", w=V_TAB_W - 16, disabled=True)),
    "lnkyes": SUI.button("SkyyVLnkYes", "Pay", "primary", "small", w=V_TAB_W - 16),
    "lnkbtnrow2": SUI.group("SkyyVLnkBtns2", "Left", h=36, anchor={"top": 4}),
    "lnkno": SUI.button("SkyyVLnkNo", "Cancel", "secondary", "small", w=V_TAB_W - 16, sound="cancel"),
    "lnktog": SUI.choose("lon", SUI.button("SkyyVLnkTog", "Pause", "secondary", "small", w=V_TAB_W - 16),
                         SUI.button("SkyyVLnkTog", "Turn on", "primary", "small", w=V_TAB_W - 16)),
}
assert V_TAB_W - 16 >= 172''')
P.rep('''# 0.8.36 SELL: what the Bazaar pays for one (bazaar:sell:<id>, published for every product); -1 = no price
''', '''# 0.8.42: the Shard Link box of pocket ci (tabs column): not linkable / needs Legendary / price + items (have / need) -> Buy -> Pay / Cancel;
# bought: On / Paused with Pause / Turn on
page.addMethod(CtNewMethod.make(vpage(r\'\'\'
public void linkBox(@UCB@ b, @UEB@ ev, @INV@ inv, java.util.UUID u, String k, int ci) {
  String cat = @PKG@.SackDefs.CATS[ci];
  boolean can = @PKG@.VoidLink.linkable(ci);
  boolean bought = can && @PKG@.VoidLink.bought(k, ci);
  boolean lon = bought && !@PKG@.VoidLink.paused(k, ci);
  int rk = @PKG@.VoidStore.rank(k, ci);
  long cost = @PKG@.VoidLink.price(ci);
  boolean lready = false;
  String lcol = "@C:caption@";
  String lscol = "@C:text@";
  String t1 = "Shard Link";
  String t2;
  if (!can) {
    t2 = "No shard fills the " + cat + " pocket.";
    lscol = "@C:caption@";
  } else if (bought) {
    lcol = lon ? "@C:have@" : "@C:caption@";
    t1 = lon ? "Shard Link: On" : "Shard Link: Paused";
    t2 = lon ? ("Your shards send their " + cat + " items straight here. When it is full they wait in the shard (Collect all).")
             : "Bought - shard items wait in the shard until you turn it on.";
    if (!@PKG@.SackCfg.LINK_ON) t2 = "Switched off on this server for now (Server Setup).";
  } else if (rk < @PKG@.VoidLink.NEED) {
    t2 = "Late game: shard items go straight into this pocket, no Collect. Needs this pocket at " + @PKG@.SackDefs.RNAME[@PKG@.VoidLink.NEED] + " first.";
    lscol = "@C:caption@";
  } else {
    lcol = "@C:gold@";
    t1 = "Shard Link - " + (cost > 0L ? shortNum(cost) + " coins" : "items only");
    long have = @PKG@.VoidCompact.coins(u);
    boolean ok = cost <= 0L || have < 0L || have >= cost;
    StringBuilder sb = new StringBuilder();
    if (cost > 0L) sb.append("Coins ").append(have < 0L ? "?" : shortNum(have)).append(" / ").append(shortNum(cost));
    java.util.LinkedHashMap need = @PKG@.SackCfg.parseCost(@PKG@.VoidLink.costText(ci));
    if (need == null) { ok = false; sb.append(sb.length() > 0 ? ". " : "").append("The item cost is not set correctly (Server Setup)."); }
    else {
      java.util.Iterator it = need.entrySet().iterator();
      while (it.hasNext()) {
        java.util.Map.Entry e = (java.util.Map.Entry) it.next();
        String id = (String) e.getKey();
        long n = ((Long) e.getValue()).longValue();
        long h = inv == null ? @PKG@.SackPool.get(k, id) : @PKG@.VoidStore.haveOf(k, inv, id);
        if (h < n) ok = false;
        if (sb.length() > 0) sb.append(". ");
        sb.append(pretty(id)).append(' ').append(shortNum(h)).append(" / ").append(shortNum(n));
      }
    }
    lready = ok && @PKG@.SackCfg.LINK_ON;
    lscol = ok ? "@C:have@" : "@C:out@";
    t2 = sb.toString() + ". Shard items then go straight in.";
    if (!@PKG@.SackCfg.LINK_ON) { t2 = "Switched off on this server for now (Server Setup)."; lscol = "@C:caption@"; }
  }
  b.appendInline("#SkyyVTabs", @@lnk@@);
  b.appendInline("#SkyyVLnk", @@lnktitle@@);
  b.set("#SkyyVLnkTitle.Text", (this.lconfirm && lready) ? ("Pay " + shortNum(cost) + " coins + items?") : t1);
  b.appendInline("#SkyyVLnk", @@lnksub@@);
  b.set("#SkyyVLnkSub.Text", t2);
  b.appendInline("#SkyyVLnk", @@lnkbtnrow@@);
  if (!can || (!bought && rk < @PKG@.VoidLink.NEED)) {
    this.lconfirm = false;
  } else if (!bought) {
    if (this.lconfirm && lready) {
      b.appendInline("#SkyyVLnkBtns", @@lnkyes@@);
      b.appendInline("#SkyyVLnk", @@lnkbtnrow2@@);
      b.appendInline("#SkyyVLnkBtns2", @@lnkno@@);
      ev.addEventBinding(@BT@.Activating, "#SkyyVLnkYes", amtEvt("lnkok:" + ci + ":" + cost));   // + the price shown
      ev.addEventBinding(@BT@.Activating, "#SkyyVLnkNo", amtEvt("lnkno"));
    } else {
      this.lconfirm = false;
      b.appendInline("#SkyyVLnkBtns", @@lnkbuy@@);
      if (lready) ev.addEventBinding(@BT@.Activating, "#SkyyVLnkBuy", amtEvt("lnkbuy"));
    }
  } else {
    this.lconfirm = false;
    b.appendInline("#SkyyVLnkBtns", @@lnktog@@);
    ev.addEventBinding(@BT@.Activating, "#SkyyVLnkTog", amtEvt("lnktog:" + ci));
  }
}\'\'\'), page))
# 0.8.36 SELL: what the Bazaar pays for one (bazaar:sell:<id>, published for every product); -1 = no price
''')
P.rep('''  b.appendInline("#SkyyVTabs", @@omni@@);
  b.set("#SkyyVOmni.Text", omni ? ("OMNI - every category x" + multTxt(4)) : ("Omni: get all six categories to Legendary (" + @PKG@.VoidStore.legendCount(k) + " / " + nc + ")"));
''', '''  b.appendInline("#SkyyVTabs", @@omni@@);
  b.set("#SkyyVOmni.Text", omni ? ("OMNI - every category x" + multTxt(4)) : ("Omni: get all six categories to Legendary (" + @PKG@.VoidStore.legendCount(k) + " / " + nc + ")"));
  linkBox(b, ev, inv, u, k, ci);   // 0.8.42: Shard Link
''')
P.rep('''    if (a.equals("cmpbuy")) { this.cconfirm = true; this.info = "=Check the price, then Pay - or Cancel"; rebuild(); return; }
''', '''    if (a.equals("cmpbuy")) { this.cconfirm = true; this.info = "=Check the price, then Pay - or Cancel"; rebuild(); return; }
    if (a.equals("lnkno")) { this.lconfirm = false; this.info = ""; rebuild(); return; }   // 0.8.42
    if (a.equals("lnkbuy")) { this.lconfirm = true; this.info = "=Check the price and the items, then Pay - or Cancel"; rebuild(); return; }
''')
P.rep('''    // 0.8.30: Auto-compact Pay / Pause / Turn on, Unpack
    if (a.startsWith("cmpok:") || a.startsWith("cmptog:")) {
''', '''    // 0.8.42: Shard Link Pay (lnkok:<ci>:<the price the Pay button showed>) / Pause / Turn on
    if (a.startsWith("lnkok:") || a.startsWith("lnktog:")) {
      boolean buyL = a.startsWith("lnkok:");
      int lci = -1;
      long lshown = -1L;
      String lrest = a.substring(buyL ? 6 : 7).trim();
      int lsep = lrest.indexOf(':');
      if (lsep >= 0) {
        try { lshown = Long.parseLong(lrest.substring(lsep + 1).trim()); } catch (Throwable t5) { lshown = -1L; }
        lrest = lrest.substring(0, lsep);
      }
      try { lci = Integer.parseInt(lrest.trim()); } catch (Throwable t6) { lci = -1; }
      this.lconfirm = false;
      this.info = lci < 0 ? "-Bad click" : (buyL ? @PKG@.VoidLink.buyAt(player, u, k, lci, lshown) : @PKG@.VoidLink.toggle(u, k, lci));
      if (buyL) @PKG@.SackSnd.ok(u, this.info, 1);   // the Void upgrade sound ("+" = paid)
      rebuild();
      return;
    }
    // 0.8.30: Auto-compact Pay / Pause / Turn on, Unpack
    if (a.startsWith("cmpok:") || a.startsWith("cmptog:")) {
''')

# ---- 5. the bridge key
P.rep('''sfn.addMethod(CtNewMethod.make(jt(r"""
public Object apply(Object o) {
  try {
    if (this.mode == 12) return @PKG@.VoidStore.pdInfo(o);   // 0.8.0 sacks:fn:pd
''', '''sfn.addMethod(CtNewMethod.make(jt(r"""
public Object apply(Object o) {
  if (this.mode == 25) return @PKG@.VoidLink.call(o);   // 0.8.42 sacks:fn:link (never throws; null = bad arguments / cannot tell)
  try {
    if (this.mode == 12) return @PKG@.VoidStore.pdInfo(o);   // 0.8.0 sacks:fn:pd
''')
P.rep('''  sbr0.put("sacks:fn:furn", new {PKG}.SackFn(24));       // 0.8.40: its actions (queue / fuel / collect / cancel / unload; profile token)
''', '''  sbr0.put("sacks:fn:furn", new {PKG}.SackFn(24));       // 0.8.40: its actions (queue / fuel / collect / cancel / unload; profile token)
  sbr0.put("sacks:fn:link", new {PKG}.SackFn(25));       // 0.8.42: Shard Link (state / room / put / done / ack; SkyyShards 0.4.33)
''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0 and P.s.count("makeClass(") == CLS0 + 1, "0.8.42: one class (VoidLink), no system / command"
assert P.s.index("public static String buyAt(java.util.UUID u, String k, int ci, long shown)") < P.s.index("public static Object put0(java.util.UUID u") \
    < P.s.index("public void linkBox(") < P.s.index("linkBox(b, ev, inv, u, k, ci);") < P.s.index("public Object apply(Object o) {\n  if (this.mode == 25)"), \
    "0.8.42: VoidLink after VoidCompact, before the page and SackFn"
P.finish()
