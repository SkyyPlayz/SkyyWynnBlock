"""Derive SkyyCollections/build_skyycollections_0.2.9.py from the LIVE 0.2.8 (build_skyycollections_0.2.8.py = the tools/deploy_set.py
SET pin; 0.2.8 stays untouched; same style as tools/collections_0_2_8_patch.py: rep() with asserted single anchors, newline-agnostic,
the source's line endings kept). Edit THIS file, never the generated build script (it is overwritten on every run of this patch).
Run:  python tools/collections_0_2_9_patch.py   then   python SkyyCollections/build_skyycollections_0.2.9.py   (never --deploy)
Test: python SkyyCollections/test_skyycollections_0.2.9.py   (bare JVM, -Xverify:all; scratch under tools/dev/scratch/, deleted afterwards)

0.2.9 = BAGS v2 ROUND 0 (research/Bags-v2-Spec.md sections 2.1, 5 and 6 "Round 0"; Skyy 2026-10-10: "i have an idea for the bags! kina
a big change. still have it upgrade from collection, but its based on the total number of items in that category you have collected.").
Lean round, harmless without SkyySacks 0.8.0. The spec's 6 questions take their recommended defaults (question 4: Smithing counts hides +
fabric scraps + metal ores).
  1. NEW BRIDGE coll:fn:catTotal (spec 5): a java.util.function.Function, apply(Object[]{UUID player, String category}) -> Long = every
     item the player has collected in that bag category's collections, ACTIVE profile (CollUtil.pkey = profile:fn:key, the same
     counts/<pkey>.properties every other coll:fn reads). The two elements may come in either order; the player may also be the UUID
     as a String; the category is matched trimmed and case-insensitively. null = unknown (not an Object[], no player / category,
     an unknown category, no registry yet, a counts file that cannot be read). Never throws (everything inside one catch).
     Categories (spec 1.1 / 2.1, CollCat.BAG): Mining, Foraging, Farming, Fishing, Combat, Smithing. Per registry ITEM (counts are
     stored per item id, so this equals the sum of that category's collections):
       - the item's collection category (CollReg.CATS: Farming / Mining / Foraging / Combat / Fishing), except
       - Fish_* and Food_Fish_Raw* -> Fishing (the hidden Raw Fish collection; spec: fish move out of Farming),
       - Ingredient_Crystal_* -> Mining (the Crystal collection; already Mining in the default registry, kept there if an admin moves it),
       - Smithing ALSO (on top of the item's own category, spec 2.1 "adds up"): Ingredient_Hide_* (Light / Medium / Heavy Hide),
         Ingredient_Fabric_Scrap_* (Linen / Wool / Shadoweave / Cindercloth), Ore_* (Copper .. Mithril; the hidden Onyxium Ore too -
         it has no source yet, so it adds 0 today and is a metal ore when it gets one).
       Hidden collections count (Raw Fish is hidden until fishing ships; the spec counts "every item ... you have collected").
     CHEAP: per pkey CollCat.CACHE = {RegData, CollData, long[6]}, built once (CollStore.catTotal, synchronized with addLocked) and
     UPDATED ON COLLECT: CollStore.addLocked (the one path every counted item takes) adds the real delta to the cached totals under the
     same monitor. A registry reload (a new RegData), another CollData object or a negative delta drops the entry (rebuilt on the next
     call). Saturates at Long.MAX_VALUE. The item -> category mask table is built once per RegData.
  2. sacks:v2 (SkyySacks 0.8.0 will publish Boolean.TRUE; a String "true" counts too): while it is set
       - CollReg.recipesAt leaves out every Skyy_Sack_* recipe, so the collection pages (tier rows, the Next line, the CRAFT button
         words / chooser, the Unlocked and Locked recipes lists), the tier-up chat lines, coll:fn:where, the coin-unlock texts and
         offers no longer show or count a bag reward;
       - CollUnlocks.compute (0.2.8's body renamed compute0, unchanged) drops every Skyy_Sack_* id - the tier ladder, the 0.2.8 kept
         Mining bags (_keptbag.Mining) and the auto rule - so coll:recipes:<uuid> carries no bag and SkyySacks is taught none;
       - CollSaver.v2Tick (every second) notices the key appear / disappear, logs one INFO line and republishes every published
         player, so coll:recipes follows the switch at once (the epoch bumps because the list changed).
     No file is read or written for it (rewards.properties keeps its bag lines; no migration). Key absent = 0.2.8, call for call
     (recipesAt returns the same array, compute the same set; the harness compares 0.2.8 and 0.2.9 on Skyy's live data).
     sacks:freebags: with the bags filtered out it has nothing left to change (spec "no longer read").
     Server Setup > Collections > Magic Bags (read-only CollKit.bagLadder rows) say "none - bags now level up in the SkyySacks
     Pocket Dimension" and the setup-time "no collection tier unlocks these Magic Bags" warning is skipped (fixer, critic LOW 1).
No setting, command, page markup, saved data or ECS system changes. New class CollCat; changed methods: CollReg.recipesAt,
CollUnlocks.compute (+ compute0), CollStore.addLocked (+ catTotal), CollFn.apply (+ catTotal), CollSaver.run (+ v2Tick), the plugin's
setup / shutdown (the bridge key). Rollback to 0.2.8 is safe (nothing written).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyCollections", "build_skyycollections_0.2.8.py")
dst = os.path.join(ROOT, "SkyyCollections", "build_skyycollections_0.2.9.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.2.8"
LF = "\n"
s = raw.decode("utf8").replace("\r\n", LF)
OLD = s
assert 'VERSION = "0.2.8"' in s and "GENERATED by tools/collections_0_2_8_patch.py from the LIVE 0.2.7" in s, "not the live generated 0.2.8"
assert 'COLL_PAGE_CHECKED = "e3b045f3048d"' in s, "build_skyycollections_0.2.8.py is not the checked 0.2.8 page"
assert "CollCat" not in s and "catTotal" not in s and "sacks:v2" not in s

GONE_OK = set()


def rep(old, new, count=1):
    """replace an asserted anchor; the 0.2.8 lines it touches may disappear (the lost-lines guard below)"""
    global s
    n = s.count(old)
    assert n == count, "anchor count %d != %d: %s" % (n, count, old[:120])
    GONE_OK.update(ln for ln in s.split(LF) if any(len(p) > 8 and p in ln for p in old.split(LF)))
    s = s.replace(old, new)


# ---------------------------------------------------------------------------------------------------------------- header
rep('''"""SkyyCollections 0.2.8 - build script (javassist via jpype). GENERATED by tools/collections_0_2_8_patch.py from the LIVE 0.2.7
(build_skyycollections_0.2.7.py, the tools/deploy_set.py SET pin) - edit the patch, never this file. 0.2.7 was derived from 0.2.6 by
tools/coll_0_2_7_patch.py;''', '''"""SkyyCollections 0.2.9 - build script (javassist via jpype). GENERATED by tools/collections_0_2_9_patch.py from the LIVE 0.2.8
(build_skyycollections_0.2.8.py, the tools/deploy_set.py SET pin) - edit the patch, never this file. 0.2.8 was derived from 0.2.7 by
tools/collections_0_2_8_patch.py; 0.2.7 from 0.2.6 by tools/coll_0_2_7_patch.py;''')
rep('''0.2.8 (2026-10-09): UNLOCKED RECIPES OPEN IN THE CRAFTER''', '''0.2.9 (2026-10-10): BAGS v2 ROUND 0 (research/Bags-v2-Spec.md; Skyy 2026-10-10: "still have it upgrade from collection, but its
  based on the total number of items in that category you have collected."). New bridge coll:fn:catTotal {UUID, String category} ->
  Long: every item collected in that bag category's collections on the ACTIVE profile (Mining, Foraging, Farming, Fishing, Combat,
  Smithing; Fishing = Fish_* + Food_Fish_Raw*, Smithing = hides + fabric scraps + metal ores, crystals in Mining), null = unknown,
  never throws, cached per profile and updated on every collect. While skyy.bridge sacks:v2 is set (SkyySacks 0.8.0) the Magic Bag
  rewards are left out of every page, chat line and list and coll:recipes teaches no bag; rewards.properties is not touched. Without
  the key everything is 0.2.8. Full notes: tools/collections_0_2_9_patch.py. CHECKED with SkyyCollections/test_skyycollections_0.2.9.py.
0.2.8 (2026-10-09): UNLOCKED RECIPES OPEN IN THE CRAFTER''')
rep("Run:   python build_skyycollections_0.2.8.py          -> SkyyCollections/SkyyCollections-0.2.8.jar",
    "Run:   python build_skyycollections_0.2.9.py          -> SkyyCollections/SkyyCollections-0.2.9.jar")
rep('VERSION = "0.2.8"', 'VERSION = "0.2.9"')
rep('"[SkyyCollections] 0.2.8 ready (', '"[SkyyCollections] 0.2.9 ready (')
rep('''    0.2.7: coll:lantern = "TreeSap|n|u|r|l" while the Lantern recipes are managed (SkyyAccessories 0.5.6 locks them only then), else "off".''',
    '''    0.2.7: coll:lantern = "TreeSap|n|u|r|l" while the Lantern recipes are managed (SkyyAccessories 0.5.6 locks them only then), else "off".
    0.2.9: coll:fn:catTotal {UUID, String bag category} -> Long (Bags v2 storage levels); reads sacks:v2 (bag rewards hidden while set).''')

# ---------------------------------------------------------------------------------------------------------------- the new class
rep('''kraft = K("CollCraft")   # 0.2.8: the CRAFT button of a tier row -> /craft <words> as the player''',
    '''kraft = K("CollCraft")   # 0.2.8: the CRAFT button of a tier row -> /craft <words> as the player
ccat = K("CollCat")      # 0.2.9: coll:fn:catTotal (Bags v2 category totals, cached per profile) + the sacks:v2 bag switch''')
rep('''       plsy, ksy, tcmp, top, fnc, page, ckit, kraft, ulc, rlc, gvc, tpc, nmc, cmd, sav, pl)''',
    '''       plsy, ksy, tcmp, top, fnc, page, ckit, kraft, ccat, ulc, rlc, gvc, tpc, nmc, cmd, sav, pl)''')

CAT_JAVA = r'''# ================= 0.2.9 CollCat: coll:fn:catTotal (Bags v2 storage levels) + the sacks:v2 bag switch =================
# research/Bags-v2-Spec.md 2.1 + 5. Compiled right after CollUtil.bridge (javassist: before its callers CollReg.recipesAt, CollStore,
# CollUnlocks, CollFn, CollSaver). Fields only from the classes above (CollReg.CATS, RegData, CollData).
F(ccat, 'public static final String[] BAG = new String[] { "Mining", "Foraging", "Farming", "Fishing", "Combat", "Smithing" };')
# pkey -> Object[]{RegData, CollData, long[6]}: built by CollStore.catTotal, updated by CollStore.addLocked (both under CollStore's monitor)
F(ccat, "public static final java.util.concurrent.ConcurrentHashMap CACHE = new java.util.concurrent.ConcurrentHashMap();")
F(ccat, "public static volatile Object MR = null;")              # the RegData the mask table MK belongs to
F(ccat, "public static volatile java.util.HashMap MK = null;")   # registry item id -> Integer bit mask over BAG
F(ccat, "public static volatile int V2 = -1;")                   # the sacks:v2 state CollSaver.v2Tick last saw (-1 = not looked yet)
F(ccat, "public static volatile long BUILDS = 0L;")              # full total builds (the harness proves the cache with it)
M(ccat, r"""
public static int idx(String name) {
  if (name == null) return -1;
  String n = name.trim();
  for (int i = 0; i < BAG.length; i++) if (BAG[i].equalsIgnoreCase(n)) return i;
  return -1;
}""")
# SkyySacks 0.8.0 publishes sacks:v2 = Boolean.TRUE (spec 5); a String "true" counts too; anything else (or absent) = off
M(ccat, r"""
public static boolean v2() {
  try {
    Object o = @PKG@.CollUtil.bridge().get("sacks:v2");
    if (o instanceof Boolean) return ((Boolean) o).booleanValue();
    return o instanceof String && "true".equalsIgnoreCase(((String) o).trim());
  } catch (Throwable t) { return false; }
}""")
# the bag categories of one registry item (bits over BAG): its collection's category, fish -> Fishing, crystals -> Mining, and
# Smithing on top for hides, fabric scraps and metal ores (spec 1.1 / 2.1, question 4 default)
M(ccat, r"""
public static int maskOf(String item, String collCat) {
  if (item == null) return 0;
  int b = idx(collCat);
  if (item.startsWith("Fish_") || item.startsWith("Food_Fish_Raw")) b = 3;
  else if (item.startsWith("Ingredient_Crystal_")) b = 0;
  int m = b >= 0 ? (1 << b) : 0;
  if (item.startsWith("Ingredient_Hide_") || item.startsWith("Ingredient_Fabric_Scrap_") || item.startsWith("Ore_")) m = m | (1 << 5);
  return m;
}""")
M(ccat, r"""
public static synchronized java.util.HashMap masks(@PKG@.RegData R) {
  if (R == null) return new java.util.HashMap();
  if (MR == R && MK != null) return MK;
  java.util.HashMap m = new java.util.HashMap();
  for (int c = 0; c < R.n; c++) {
    String cn = R.cat[c] >= 0 && R.cat[c] < @PKG@.CollReg.CATS.length ? @PKG@.CollReg.CATS[R.cat[c]] : "";
    String[] its = (String[]) R.items[c];
    for (int j = 0; its != null && j < its.length; j++) {
      Object p = m.get(its[j]);
      int v = maskOf(its[j], cn) | (p instanceof Integer ? ((Integer) p).intValue() : 0);
      m.put(its[j], Integer.valueOf(v));
    }
  }
  MK = m;
  MR = R;
  return m;
}""")
M(ccat, r"""
public static long sat(long a, long b) {
  if (b > 0L && a > Long.MAX_VALUE - b) return Long.MAX_VALUE;
  return a + b;
}""")
# the six totals of one profile's counts, from scratch (CollStore.sumMap's value rules: Long, or a number String)
M(ccat, r"""
public static long[] compute(@PKG@.CollData d, @PKG@.RegData R) {
  long[] t = new long[6];
  BUILDS = BUILDS + 1L;
  if (d == null || R == null) return t;
  java.util.Iterator it = masks(R).entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    Object o = d.items.get(e.getKey());
    long v = 0L;
    if (o instanceof Long) v = ((Long) o).longValue();
    else if (o instanceof String) { try { v = Long.parseLong(((String) o).trim()); } catch (Throwable x) { v = 0L; } }
    if (v <= 0L) continue;
    int m = ((Integer) e.getValue()).intValue();
    for (int b = 0; b < 6; b++) if ((m & (1 << b)) != 0) t[b] = sat(t[b], v);
  }
  return t;
}""")
# CollStore.addLocked (holding CollStore's monitor, like CollStore.catTotal): dq = the real change of one item's count
M(ccat, r"""
public static void onAdd(String key, @PKG@.CollData d, @PKG@.RegData R, String item, long dq) {
  if (key == null) return;
  try {
    Object[] e = (Object[]) CACHE.get(key);
    if (e == null) return;
    if (e[0] != R || e[1] != d || dq < 0L) { CACHE.remove(key); return; }
    Object mo = masks(R).get(item);
    if (!(mo instanceof Integer)) return;
    int m = ((Integer) mo).intValue();
    long[] t = (long[]) e[2];
    for (int b = 0; b < 6; b++) if ((m & (1 << b)) != 0) t[b] = sat(t[b], dq);
  } catch (Throwable x) { CACHE.remove(key); }
}""")
# a tier's recipe ids without the Magic Bags (Skyy_Sack_*, CollUtil.isBag's rule); the same array when there is none
M(ccat, r"""
public static String[] noBags(String[] rs) {
  if (rs == null) return rs;
  int n = 0;
  for (int i = 0; i < rs.length; i++) if (rs[i] != null && rs[i].startsWith("Skyy_Sack_")) n++;
  if (n == 0) return rs;
  String[] out = new String[rs.length - n];
  int k = 0;
  for (int i = 0; i < rs.length; i++) {
    if (rs[i] != null && rs[i].startsWith("Skyy_Sack_")) continue;
    out[k] = rs[i];
    k++;
  }
  return out;
}""")

'''
rep('''# tools/PROFILES-CONTRACT.md storage-key helper, verbatim''', CAT_JAVA + '''# tools/PROFILES-CONTRACT.md storage-key helper, verbatim''')

# ---------------------------------------------------------------------------------------------------------------- recipesAt
rep('''public static String[] recipesAt(int c, int t) {
  Object o = RECIPES.get(c + "." + t);
  return o == null ? EMPTY : (String[]) o;
}""")''', '''public static String[] recipesAt(int c, int t) {
  Object o = RECIPES.get(c + "." + t);
  if (o == null) return EMPTY;
  return @PKG@.CollCat.v2() ? @PKG@.CollCat.noBags((String[]) o) : (String[]) o;   // 0.2.9: no Magic Bag while sacks:v2
}""")''')

# ---------------------------------------------------------------------------------------------------------------- CollStore
rep('''  d.items.put(item, Long.valueOf(nv));
  DIRTY.put(key, Boolean.TRUE);
  return new long[] { before, sum(d, R, c) };
}""")''', '''  d.items.put(item, Long.valueOf(nv));
  @PKG@.CollCat.onAdd(key, d, R, item, nv - (v == null ? 0L : v.longValue()));   // 0.2.9: the cached category totals follow
  DIRTY.put(key, Boolean.TRUE);
  return new long[] { before, sum(d, R, c) };
}""")
# 0.2.9: one bag category's total for coll:fn:catTotal - the cached six (built once per pkey / RegData / CollData), same monitor as addLocked
M(sto, r"""
public static synchronized long catTotal(String key, @PKG@.CollData d, @PKG@.RegData R, int i) {
  Object[] e = (Object[]) @PKG@.CollCat.CACHE.get(key);
  long[] t = null;
  if (e != null && e[0] == R && e[1] == d) t = (long[]) e[2];
  if (t == null) {
    t = @PKG@.CollCat.compute(d, R);
    @PKG@.CollCat.CACHE.put(key, new Object[] { R, d, t });
  }
  return i >= 0 && i < t.length ? t[i] : 0L;
}""")''')

# ---------------------------------------------------------------------------------------------------------------- CollUnlocks.compute
rep('''M(unl, r"""
public static java.util.TreeSet compute(@PKG@.CollData d) {
  java.util.TreeSet out = new java.util.TreeSet();''', '''M(unl, r"""
public static java.util.TreeSet compute0(@PKG@.CollData d) {
  java.util.TreeSet out = new java.util.TreeSet();''')
rep('''      if (anyTier && !blocked) { String rid = r.getId(); if (rid != null && !@PKG@.CollUtil.isLantern(rid)) out.add(rid); }
    }
  } catch (Throwable t) { @PKG@.CollUtil.warn("unlock compute failed: " + t); }
  return out;
}""")''', '''      if (anyTier && !blocked) { String rid = r.getId(); if (rid != null && !@PKG@.CollUtil.isLantern(rid)) out.add(rid); }
    }
  } catch (Throwable t) { @PKG@.CollUtil.warn("unlock compute failed: " + t); }
  return out;
}""")
# 0.2.9: while sacks:v2 (SkyySacks 0.8.0, one Pocket Dimension) no Magic Bag is unlocked - the tier ladder (recipesAt already leaves them
# out), the 0.2.8 kept Mining bags and the auto rule alike; compute0 = 0.2.8's compute, unchanged
M(unl, r"""
public static java.util.TreeSet compute(@PKG@.CollData d) {
  java.util.TreeSet out = compute0(d);
  if (!@PKG@.CollCat.v2()) return out;
  java.util.Iterator it = out.iterator();
  while (it.hasNext()) {
    String rid = (String) it.next();
    if (rid != null && rid.startsWith("Skyy_Sack_")) it.remove();
  }
  return out;
}""")''')

# ---------------------------------------------------------------------------------------------------------------- CollFn
rep('''M(fnc, r"""
public Object apply(Object arg) {
  try {
    if ("where".equals(this.mode)) return where((Object[]) arg);''', '''# 0.2.9 coll:fn:catTotal (Bags-v2-Spec 5): {UUID player, String category} (either order; the player may be its UUID String) -> Long
# = the items collected in that bag category on the ACTIVE profile; null = unknown. Never throws.
M(fnc, r"""
public static Object catTotal(Object arg) {
  try {
    if (!(arg instanceof Object[])) return null;
    Object[] a = (Object[]) arg;
    java.util.UUID u = null;
    int ci = -1;
    for (int i = 0; i < a.length && i < 2; i++) {
      Object o = a[i];
      if (o == null) continue;
      if (o instanceof java.util.UUID) { u = (java.util.UUID) o; continue; }
      if (!(o instanceof String)) continue;
      int k = @PKG@.CollCat.idx((String) o);
      if (k >= 0) { ci = k; continue; }
      try { u = java.util.UUID.fromString(((String) o).trim()); } catch (Throwable x) { }
    }
    if (u == null || ci < 0) return null;
    @PKG@.RegData R = @PKG@.CollReg.D;
    if (R == null) return null;
    String key = @PKG@.CollUtil.pkey(u);
    @PKG@.CollData d = @PKG@.CollStore.dataK(key);
    if (d == null) return null;
    return Long.valueOf(@PKG@.CollStore.catTotal(key, d, R, ci));
  } catch (Throwable t) { return null; }
}""")
M(fnc, r"""
public Object apply(Object arg) {
  try {
    if ("catTotal".equals(this.mode)) return catTotal(arg);   // 0.2.9
    if ("where".equals(this.mode)) return where((Object[]) arg);''')

# ---------------------------------------------------------------------------------------------------------------- CollSaver
rep('''M(sav, r"""
public void run() {
  this.ticks = this.ticks + 1L;
  try { @PKG@.CollUnlocks.checkEpochs(); } catch (Throwable t) { }''', '''# 0.2.9: sacks:v2 appeared / went away -> one INFO line + republish every published player (coll:recipes drops / regains the bags;
# the list changes, so the epoch bumps and SkyySacks re-reads it). The first look with the key absent changes nothing.
M(sav, r"""
public static void v2Tick() {
  int now = @PKG@.CollCat.v2() ? 1 : 0;
  int was = @PKG@.CollCat.V2;
  if (was == now) return;
  @PKG@.CollCat.V2 = now;
  if (was < 0 && now == 0) return;
  @PKG@.CollUtil.info(now == 1 ? "sacks:v2 is set (SkyySacks Pocket Dimension): Magic Bag rewards are hidden and unlock nothing; rewards.properties is unchanged" : "sacks:v2 is gone: Magic Bag rewards show and unlock again");
  @PKG@.CollUnlocks.republishAll();
}""")
M(sav, r"""
public void run() {
  this.ticks = this.ticks + 1L;
  try { v2Tick(); } catch (Throwable t) { }   // 0.2.9
  try { @PKG@.CollUnlocks.checkEpochs(); } catch (Throwable t) { }''')

# ---------------------------------------------------------------------------------------------------------------- plugin
rep('''  b.put("coll:fn:where", new @PKG@.CollFn("where"));''', '''  b.put("coll:fn:where", new @PKG@.CollFn("where"));
  b.put("coll:fn:catTotal", new @PKG@.CollFn("catTotal"));   // 0.2.9 (Bags-v2-Spec 5)''')
rep('''    b.remove("coll:lantern");   // 0.2.7''', '''    b.remove("coll:lantern");   // 0.2.7
    b.remove("coll:fn:catTotal");   // 0.2.9''')

# ---------------------------------------------------------------------------------------------------------------- Server Setup bag rows
# 0.2.9 fixer (critic LOW 1): the read-only Server Setup > Magic Bags rows and the setup-time "no collection tier unlocks these Magic
# Bags" warning read the raw rewards table, so with sacks:v2 set they still named tiers that no longer unlock anything. While the key
# is set the rows say so and the warning is skipped; key absent = 0.2.8 (same text, same warning).
rep('''public static String bagLadder(String type) {
  @PKG@.RegData R = @PKG@.CollReg.D;''', '''public static String bagLadder(String type) {
  if (@PKG@.CollCat.v2()) return "none - bags now level up in the SkyySacks Pocket Dimension";   // 0.2.9
  @PKG@.RegData R = @PKG@.CollReg.D;''')
rep('''  if (gp.length() > 0) @PKG@.CollUtil.warn("no collection tier unlocks these Magic Bags: "''',
    '''  if (gp.length() > 0 && !@PKG@.CollCat.v2()) @PKG@.CollUtil.warn("no collection tier unlocks these Magic Bags: "''')

# ---------------------------------------------------------------------------------------------------------------- the page check names the 0.2.9 harness
rep('''COLL_PAGE_CHECKED = "e3b045f3048d"   # 0.2.8: SkyyCollections/test_skyycollections_0.2.8.py (tools/collections_0_2_8_patch.py PAGE_CHECKED)''',
    '''COLL_PAGE_CHECKED = "e3b045f3048d"   # 0.2.8 page, unchanged in 0.2.9: SkyyCollections/test_skyycollections_0.2.9.py checks it''')
rep('''the page SkyyCollections/test_skyycollections_0.2.8.py last passed on''', '''the page SkyyCollections/test_skyycollections_0.2.9.py last passed on''', 3)
rep('''in tools/collections_0_2_8_patch.py and regenerate''', '''in tools/collections_0_2_9_patch.py and regenerate''', 2)

# ---------------------------------------------------------------------------------------------------------------- guards
assert s.index("public static int maskOf(") < s.index("public static String pkey(java.util.UUID u)") < s.index("public static String[] recipesAt(int c, int t)")
assert s.index("public static String[] noBags(") < s.index("public static String[] recipesAt(int c, int t)")
assert s.index("public static void onAdd(") < s.index("public static synchronized long[] addLocked(") < s.index("public static synchronized long catTotal(")
assert s.index("public static synchronized long catTotal(") < s.index("public static Object catTotal(Object arg)") < s.index("public Object apply(Object arg)")
assert s.index("public static java.util.TreeSet compute0(") < s.index("public static java.util.TreeSet compute(@PKG@.CollData d)")
assert s.index("public static void republishAll()") < s.index("public static void v2Tick()") < s.index("public void run() {\n  this.ticks")
assert s.index("public static boolean v2()") < s.index("public static String bagLadder(String type)")
assert s.count("CollCat.v2()") == 5 and s.count('"coll:fn:catTotal"') == 2
_gone = sorted(ln for ln in set(OLD.split(LF)) - set(s.split(LF)))
_bad = [ln for ln in _gone if ln not in GONE_OK]
assert not _bad, "0.2.8 lines lost by accident: %s" % _bad[:5]
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst, "(%d lines; 0.2.8 had %d)" % (s.count(LF), OLD.count(LF)))
