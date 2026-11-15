"""Derive SkyyShards/build_skyyshards_0.4.22.py from the GENERATED SkyyShards 0.4.21 (build_skyyshards_0.4.21.py = the tools/deploy_set.py SET
pin, made by tools/shards_0_4_21_patch.py - edit the patch, never the generated file). Every anchor is asserted once; at the end every change
is undone on a copy and compared with 0.4.21 (tools/soundpass_gen.Patch). Line endings kept.
Run:   python tools/shards_0_4_22_patch.py   then   python SkyyShards/build_skyyshards_0.4.22.py   (never --deploy)
Check: python SkyyShards/test_skyyshards_0.4.22.py

0.4.22 (2026-11-14) = THE STORE GRID: SEE WHAT IS INSIDE BEFORE YOU COLLECT (round shard1; Skyy 2026-11-14, screenshots of the Combat Shard COLLECT tab: "it shows
  me what all i got when i collected, but i couldnt see it before i collected. make all the shards work like skyblock, where it has grid like a chest showing what all
  is in it, (but without a stack limit like in the pocket dimension."; recorded docs/answered/world.md 2026-11-14). Every shard's Collect tab.
  1. THE GRID (right panel of the Collect tab, above Collect all; Menu-Pattern scroll list on the well, SkyySacks' Pocket Dimension cell look: kit icon_cell 80 x 74,
     6 a row, 4 rows show, the rest scrolls). ONE cell per item kind of the WHOLE shard (every island merged - the shard is the chest; the island rows on the left keep
     their own Collect / Sell / Bags buttons), its icon and the FULL count ("12,345": no stack limit; 10 million and up = "12M", out of reach of any store today),
     the item's rarity colour as the square behind the icon (SkyyBazaar 0.2.3's look: tools/tier_tags.py rarity rows, else Skyy_Ench_ = Epic, else the asset Quality
     following Parent; none = faint grey). Sorted by tier (tools/tier_tags.py; an Enchanted item takes its base item's tier and sits right after it; untiered last),
     then name. Unidentified bags (Combat) are their own cell at the end (only when SkyyGear answers gear:fn:box, so the icon id always exists).
     The cells are ItemIcons with an item id only (no ItemStack, no metadata: the HANDOFF section 2 disconnect rule). No hover tooltip: the kit's text tooltip is
     still UNVERIFIED (trial) - the status line names what a click collected.
  2. CLICK A CELL = COLLECT THAT KIND ONLY (from every island that holds it): the same ShCore.collect0 as Collect all (one code path, debit first + saved, inventory
     first, what does not fit stays in the shard, the same XP + collection credit), told which item to take. A Farming / Mining / ... island's stored count shows as
     what Collect pays: its Enchanted part (Auto-Compactor: every full 100) and the base / smelted rest are two cells, each collected on its own; the legacy line
     (compressed Enchanted stock, an old item) and the bonus finds are cells too (one item id = one cell, so Farming's Enchanted Wheat stock + Harvest Moon finds
     are one cell). The event names the ITEM ("gc:<id>"), never a place in the grid, so a grid that changed under the click still takes what was clicked. The bag
     cell collects bags from every Combat island (collectBags0 per island). Collect all and the rows' Bags buttons stay.
  3. COMBAT: STORE THE ROLLED DROPS. A Combat island stores one count that ShCombat.split turns into the pool's drops (deterministic, largest remainder): the grid
     shows exactly that split. To take ONE kind out, the count is rolled first: ShCore.roll writes the split into <kind>.i<n>.drops ("id:qty,id:qty") and sets
     stored to the part with no item (0 in practice); the kinds asked for leave drops, the rest stays there, exactly. Collect all rolls too, so a full inventory
     now keeps exactly the kinds that did not fit (was: "the mix of the largest count that fitted", ShCombat.fitFor - no longer called). The rolled drops count
     against the island's storage (ShMath.usedOf), so the Soul Cage stops at the same cap. Nothing changes rates, totals or bags.
  4. FIXES (critics): the roll is CUMULATIVE (ShCombat.cum / rollFor; <kind>.i<n>.rolled = the pool count rolled so far): kind i has had floor(rolled x its
     share) in all, so 100 Collects of 3 pay exactly what one Collect of 300 pays (largest remainder on small pools gave everything to the commonest kinds); the
     few units that make no whole item yet (fewer than the pool's kinds) wait in `stored`, still counted against storage, and the grid does not show them. A
     Collect that takes nothing puts back only the rolled keys (no clear() of the live profile). The bag cell goes on past an island that answers "-...". The
     build asserts every grid id is a real item (vanilla, SkyyCollections' Enchanted ids, the zone metals, the bag).
  SAVED DATA: <kind>.i<n>.drops + <kind>.i<n>.rolled (Combat only), written by a roll (any Collect on a Combat island). Old files load unchanged (no rolled =
     start from 0).
  ROLLBACK 0.4.22 -> 0.4.21 alone: no migration. 0.4.21 never reads <kind>.i<n>.rolled (harmless: back on 0.4.22 a count that no longer fits starts over,
     never paying more than the pool) nor <kind>.i<n>.drops: rolled drops left there are KEPT in the file (0.4.21 saves unknown keys)
     but neither shown nor paid nor counted against storage until 0.4.22 is back (then they come back, nothing lost; an island over its cap just pauses until
     collected). To have nothing waiting there: Collect all on every Combat island with room in the inventory before rolling back.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

HERE = os.path.join(ROOT, "SkyyShards")
P = G.Patch(os.path.join(HERE, "build_skyyshards_0.4.21.py"), os.path.join(HERE, "build_skyyshards_0.4.22.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.4.21"\n') and P.has("GENERATED by tools/shards_0_4_21_patch.py") and not P.has("gridOf"), "not the generated SkyyShards 0.4.21"
REG0, SYS0 = P.s.count("registerCommand("), P.s.count("registerSystem(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.4.22 (2026-11-14)"):].rstrip() + "\n"

# ---------------------------------------------------------------------------------------------------- 0. header + version
P.rep('''"""SkyyShards 0.4.21 - build script (javassist via jpype). GENERATED by tools/shards_0_4_21_patch.py from build_skyyshards_0.4.20.py
(generated by tools/shards_0_4_20_patch.py from 0.4.19, ... back to tools/shards_0_4_patch.py from 0.3.2; edit the patch, never this file).
Changes are marked "0.4.21" /''', '''"""SkyyShards 0.4.22 - build script (javassist via jpype). GENERATED by tools/shards_0_4_22_patch.py from build_skyyshards_0.4.21.py
(generated by tools/shards_0_4_21_patch.py from 0.4.20, ... back to tools/shards_0_4_patch.py from 0.3.2; edit the patch, never this file).
Changes are marked "0.4.22" / "0.4.21" /''')
P.rep('''Run:   python SkyyShards/build_skyyshards_0.4.21.py   -> SkyyShards/SkyyShards-0.4.21.jar   (never --deploy: tools/deploy_set.py installs the set)
Check: python SkyyShards/test_skyyshards_0.4.21.py
''', '''Run:   python SkyyShards/build_skyyshards_0.4.22.py   -> SkyyShards/SkyyShards-0.4.22.jar   (never --deploy: tools/deploy_set.py installs the set)
Check: python SkyyShards/test_skyyshards_0.4.22.py
''' + NOTE + '''
0.4.21 notes:
''')
P.rep('VERSION = "0.4.21"\n', 'VERSION = "0.4.22"\n')

# ---------------------------------------------------------------------------------------------------- 1. ShMath: the rolled drops (<kind>.i<n>.drops), counted in usedOf
P.rep('''# the limit + the use in the same unit''', '''# 0.4.22 THE ROLLED DROPS of a Combat island: <kind>.i<n>.drops = "id:qty,id:qty" (what a per-kind Collect or a short Collect left, exact kinds); only
# ShCore.roll / collect0 write it. A bad entry is skipped (never an error). They count against the island's storage (usedOf).
M(mth, r"""
public static java.util.LinkedHashMap held(int kd, java.util.Properties p, int slot) {
  java.util.LinkedHashMap m = new java.util.LinkedHashMap();
  String s = @PKG@.ShStore.str(p, ik(kd, slot, "drops"));
  if (s.length() == 0) return m;
  String[] a = s.split(",");
  for (int i = 0; i < a.length; i++) {
    String v = a[i].trim();
    int c = v.lastIndexOf(':');
    if (c <= 0) continue;
    long n = 0L;
    try { n = Long.parseLong(v.substring(c + 1).trim()); } catch (Throwable t) { n = 0L; }
    String id = v.substring(0, c).trim();
    if (n <= 0L || id.length() == 0) continue;
    Object o = m.get(id);
    m.put(id, Long.valueOf((o == null ? 0L : ((Long) o).longValue()) + n));
  }
  return m;
}""")
M(mth, r"""
public static long heldN(int kd, java.util.Properties p, int slot) {
  if (@PKG@.ShStore.str(p, ik(kd, slot, "drops")).length() == 0) return 0L;
  java.util.Iterator it = held(kd, p, slot).values().iterator();
  long t = 0L;
  while (it.hasNext()) t += ((Long) it.next()).longValue();
  return t;
}""")
M(mth, r"""
public static void heldSet(int kd, java.util.Properties p, int slot, java.util.LinkedHashMap m) {
  StringBuilder b = new StringBuilder();
  java.util.Iterator it = m.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    long n = ((Long) e.getValue()).longValue();
    if (n <= 0L) continue;
    if (b.length() > 0) b.append(',');
    b.append((String) e.getKey()).append(':').append(n);
  }
  if (b.length() == 0) p.remove(ik(kd, slot, "drops")); else p.setProperty(ik(kd, slot, "drops"), b.toString());
}""")
# the limit + the use in the same unit''')
P.rep('''public static long usedOf(int kd, java.util.Properties p, int slot) {
  long s = @PKG@.ShStore.lng(p, ik(kd, slot, "stored"), 0L);
  if (s < 0L) s = 0L;
''', '''public static long usedOf(int kd, java.util.Properties p, int slot) {
  long s = @PKG@.ShStore.lng(p, ik(kd, slot, "stored"), 0L);
  if (s < 0L) s = 0L;
  s += heldN(kd, p, slot);   // 0.4.22: a Combat island's rolled drops use its storage too
''')

# ---------------------------------------------------------------------------------------------------- 1b. ShCombat: the frequency-free roll (fix, critic 1)
# A roll of a small pool by largest remainder gives every item to the commonest kinds (a pool of 3 never makes a rare drop), so clicking often would change
# the mix. The roll is CUMULATIVE instead: <kind>.i<n>.rolled = the island's pool count rolled so far (C). Kind i has had floor(C * w_i) items in all, so a roll
# of the pool count s gives floor(C' * w_i) - floor(C * w_i) with C' = G(C) + s (G = what C made; the unrolled rest of the last roll is in s). Over time every
# kind gets exactly its share, however often anyone collects; the few units that do not make a whole item yet (fewer than the pool's kinds) stay in `stored`
# (still counted against storage). A count that no longer fits the saved C (the pool changed: island type / size, combat.cageSkip; a hand edit) starts over
# from C = 0. No known drops = all s as the fallback item (C = 0).
P.rep('''public static Object[] dropsFor(java.util.Properties p, int slot, long n) {
  int t = @PKG@.ShIsl.ty(CK, p, slot);
  return split(zoneOf(t), @PKG@.ShMath.size(CK, p, slot), n, @PKG@.ShIsl.PROD[t]);
}""")
''', '''public static Object[] dropsFor(java.util.Properties p, int slot, long n) {
  int t = @PKG@.ShIsl.ty(CK, p, slot);
  return split(zoneOf(t), @PKG@.ShMath.size(CK, p, slot), n, @PKG@.ShIsl.PROD[t]);
}""")
# 0.4.22 fix (critic): the cumulative roll -> Object[]{ String[] ids, long[] qty (adds up to at most s), Long C' (the new rolled count) }
M(cmb, r"""
public static Object[] cum(int z, int size, long last, long s, String fallback) {
  String[] rl = allRoles(z, size);
  java.util.ArrayList ids = new java.util.ArrayList();
  java.util.ArrayList ws = new java.util.ArrayList();
  for (int i = 0; i < rl.length; i++) {
    double rw = wt(z, rl[i]);
    String[] it = csv(dropsOf(rl[i]));
    for (int j = 0; j < it.length; j++) {
      int c = it[j].lastIndexOf(':');
      String id = c > 0 ? it[j].substring(0, c) : it[j];
      double w = 1.0;
      if (c > 0) { try { w = Double.parseDouble(it[j].substring(c + 1)); } catch (Throwable x) { w = 0.0; } }
      w = w * rw;
      if (!(w > 0.0) || id.length() == 0 || skip(id)) continue;
      int at = ids.indexOf(id);
      if (at < 0) { ids.add(id); ws.add(Double.valueOf(w)); }
      else ws.set(at, Double.valueOf(((Double) ws.get(at)).doubleValue() + w));
    }
  }
  long nn = s < 0L ? 0L : s;
  if (ids.isEmpty()) return new Object[] { new String[] { fallback }, new long[] { nn }, Long.valueOf(0L) };
  double tot = 0.0;
  for (int i = 0; i < ws.size(); i++) tot += ((Double) ws.get(i)).doubleValue();
  int m = ids.size();
  double[] fw = new double[m];
  for (int i = 0; i < m; i++) fw[i] = ((Double) ws.get(i)).doubleValue() / tot;
  long[] q = new long[m];
  long lst = last < 0L ? 0L : last;
  for (int pass = 0; pass < 2; pass++) {
    long g0 = 0L;
    long[] f0 = new long[m];
    for (int i = 0; i < m; i++) { f0[i] = (long) Math.floor((double) lst * fw[i] + 0.000000001); g0 += f0[i]; }
    long c1 = g0 + nn;
    long given = 0L;
    boolean ok = g0 <= lst;
    for (int i = 0; i < m; i++) {
      q[i] = (long) Math.floor((double) c1 * fw[i] + 0.000000001) - f0[i];
      if (q[i] < 0L) ok = false;
      given += q[i];
    }
    if (ok && given <= nn) return new Object[] { arr(ids), q, Long.valueOf(c1) };
    lst = 0L;   // the pool changed since the last roll: start over
  }
  return new Object[] { new String[] { fallback }, new long[] { nn }, Long.valueOf(0L) };
}""")
M(cmb, r"""
public static Object[] rollFor(java.util.Properties p, int slot, long s) {
  int t = @PKG@.ShIsl.ty(CK, p, slot);
  long last = @PKG@.ShStore.lng(p, @PKG@.ShMath.ik(CK, slot, "rolled"), 0L);
  return cum(zoneOf(t), @PKG@.ShMath.size(CK, p, slot), last, s, @PKG@.ShIsl.PROD[t]);
}""")
''')

# ---------------------------------------------------------------------------------------------------- 2. the grid's build-time tables: tier + rarity of every item a shard can hold
P.rep('''core = mk("ShCore")
''', '''# 0.4.22 THE STORE GRID (Skyy 2026-11-14: "make all the shards work like skyblock, where it has grid like a chest showing what all is in it"): every item a
# shard can hold (the island items, their Enchanted / smelted forms, the bonus finds, the old 0.4.6 items a legacy line can carry, every Combat pool drop, the
# bag) -> its tier (tools/tier_tags.py; an Enchanted item = its base item's tier) and its rarity (1 Common .. 6 Mythic: tier_tags rarity rows, Skyy_Ench_ = Epic,
# else the asset Quality following Parent - SkyyBazaar 0.2.3's rule). Display only: an id not in the table = untiered, no colour.
import tier_tags as _TT422
GRID_BAG = "Skyy_Unid_Bag_Normal"                    # SkyyGear's Normal bag (BAG_IDS[0]): the bag cell's icon
G422_IDS = set()
for _i in ISL:
    for _f in ("prod", "ench", "smelt", "smeltEnch", "bonus"):
        if _i.get(_f):
            G422_IDS.add(_i[_f])
for _k, _t in TY48:
    for _f in ("prod", "ench", "smelt", "smeltEnch"):
        if _t.get(_f):
            G422_IDS.add(_t[_f])
for _r in CZ_DROPS:
    for _i, _q in CZ_DROPS[_r]:
        G422_IDS.add(_i)
G422_IDS.add(GRID_BAG)
assert all(re.fullmatch(r"[A-Za-z0-9_]+", _i) for _i in G422_IDS), "0.4.22: every grid id is a plain item id"
_EBASE422 = dict((_v, _k) for _k, _v in _ENCHB48.items())
_ipath422 = dict((_n.rsplit("/", 1)[1][:-5], _n) for _n in AZ.namelist() if _n.startswith("Server/Item/Items/") and _n.endswith(".json"))
_G422_ZONE = set(_x for _m in _MO48 if _m[0] in [_z[0] for _z in _TT48.ZONE_METALS] for _x in (_m[1], _m[4]))   # the zone metals' ore + bar (the 0.4.8 mining ladder)
_G422_BAD = sorted(_i for _i in G422_IDS if _i not in _ipath422 and _i not in _SE.IDS and _i not in _G422_ZONE and _i != GRID_BAG)   # fix (critic): an ItemIcon id must be a real item
assert not _G422_BAD, "0.4.22: grid ids that are neither vanilla, SkyyCollections' Enchanted ids, the zone metals nor the bag: %s" % _G422_BAD


def _q422(i, depth=0):
    try:
        d = json.loads(AZ.read(_ipath422[i]).decode("utf-8-sig"))
    except Exception:
        return None
    if "Quality" in d or depth > 8 or not d.get("Parent") or d.get("Parent") not in _ipath422:
        return d.get("Quality")
    return _q422(d["Parent"], depth + 1)


G422_RNAMES = ("Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic")
G422_RCOLS = [SUI.QUALITY[_n] for _n in G422_RNAMES[:5]] + [SUI.RARITY["Mythic"]]
G422_TIER, G422_RAR = {}, {}
for _i in sorted(G422_IDS):
    _t = _TT422.tier(_i)
    if _t is None and _i in _EBASE422:
        _t = _TT422.tier(_EBASE422[_i])
    if _t:
        G422_TIER[_i] = int(_t)
    _rt = _TT422.rarity_tag_for(_i)
    if _rt:
        _q = _rt.split(" ")[0]
    elif _i.startswith(_SE.PREFIX):
        _q = "Epic"
    elif _i == GRID_BAG:
        _q = "Common"                                # SkyyGear's Normal bag = the Common quality (Skyy_Gear_Normal)
    else:
        _q = _q422(_i) if _i in _ipath422 else None
    if _q in G422_RNAMES:
        G422_RAR[_i] = G422_RNAMES.index(_q) + 1
assert G422_RAR.get(GRID_BAG) == 1 and all(1 <= _v <= 6 for _v in G422_RAR.values())
G422_TSPEC = "|".join("%s:%d" % (_i, G422_TIER[_i]) for _i in sorted(G422_TIER))
G422_RSPEC = "|".join("%s:%d" % (_i, G422_RAR[_i]) for _i in sorted(G422_RAR))
print("0.4.22 grid: %d item ids, %d tiered, %d with a rarity" % (len(G422_IDS), len(G422_TIER), len(G422_RAR)))
GRID_BG_NONE = SUI.COLOR["disabled"] + "(0.15)"     # = SkyyBazaar 0.2.3 / SkyyPets 0.4.18: no rarity = the faint grey
GRID_BG = [_c + "(0.4)" for _c in G422_RCOLS]

core = mk("ShCore")
''')

# ---------------------------------------------------------------------------------------------------- 3. ShCore: roll, collect0 with one kind, the grid, the bag cell
P.rep('''# Collect `slot` (-1 = every island) of shard kd for player u from profile k.''', '''# 0.4.22: a Combat island's pool count -> its rolled drops (ShCombat.rollFor, the cumulative mix Collect pays), under the lock; stored keeps the units that
# make no whole item yet (+ a part with no item id); <kind>.i<n>.rolled = the new rolled count
M(core, r"""
public static void roll(java.util.Properties p, int slot) {
  int kd = @PKG@.ShCombat.CK;
  long s = @PKG@.ShMath.stored(kd, p, slot);
  if (s <= 0L) return;
  Object[] dm = @PKG@.ShCombat.rollFor(p, slot, s);
  String[] di = (String[]) dm[0];
  long[] dq = (long[]) dm[1];
  java.util.LinkedHashMap m = @PKG@.ShMath.held(kd, p, slot);
  long put = 0L;
  long kept = 0L;
  for (int j = 0; j < di.length && j < dq.length; j++) {
    if (dq[j] <= 0L) continue;
    if (di[j] == null || di[j].length() == 0) { kept += dq[j]; continue; }
    Object o = m.get(di[j]);
    m.put(di[j], Long.valueOf((o == null ? 0L : ((Long) o).longValue()) + dq[j]));
    put += dq[j];
  }
  kept = s - put;
  if (kept < 0L) kept = 0L;
  @PKG@.ShMath.heldSet(kd, p, slot, m);
  p.setProperty(@PKG@.ShMath.ik(kd, slot, "stored"), String.valueOf(kept));
  long c1 = ((Long) dm[2]).longValue();
  if (c1 > 0L) p.setProperty(@PKG@.ShMath.ik(kd, slot, "rolled"), String.valueOf(c1)); else p.remove(@PKG@.ShMath.ik(kd, slot, "rolled"));
}""")
# 0.4.22 fix (critic): a Collect that took nothing puts back only what roll() wrote (stored / drops / rolled of each island), never clear() the live profile
M(core, r"""
public static void unroll(java.util.Properties p, java.util.Properties old, int slot) {
  String[] ks = new String[] { "stored", "drops", "rolled" };
  for (int j = 0; j < ks.length; j++) {
    String key = @PKG@.ShMath.ik(@PKG@.ShCombat.CK, slot, ks[j]);
    String v = old.getProperty(key);
    if (v == null) p.remove(key); else p.setProperty(key, v);
  }
}""")
# Collect `slot` (-1 = every island) of shard kd for player u from profile k.''')
P.rep('''public static String collect0(java.util.UUID u, String k, int kd, int slot, @IC@[] cs) {   // 0.3.1: the 0.3 collect, renamed (the wrapper plays the sting)''',
      '''public static String collect0(java.util.UUID u, String k, int kd, int slot, @IC@[] cs, String only) {   // 0.3.1: the 0.3 collect, renamed (the wrapper plays the sting); 0.4.22: only = one item kind (null = all)''')
P.rep('''    double[] xa = new double[n];   // 0.4.4 fix 2
    for (int i = 0; i < n; i++) {
      if (slot >= 0 && i != slot) continue;
      take[i] = @PKG@.ShMath.stored(kd, p, i);
      takeE[i] = bon.length() == 0 ? 0L : @PKG@.ShMath.ench(kd, p, i);
      String lg = @PKG@.ShStore.str(p, @PKG@.ShIsl.ik(kd, i, "legacy"));   // 0.4.8: "item:count" of a retyped 0.4.6 island
      int lc = lg.lastIndexOf(':');
      if (lc > 0) { try { takeL[i] = Long.parseLong(lg.substring(lc + 1).trim()); lid[i] = lg.substring(0, lc); } catch (Throwable t) { takeL[i] = 0L; } }
      if (takeL[i] < 0L) takeL[i] = 0L;
''', '''    double[] xa = new double[n];   // 0.4.4 fix 2
    boolean isC = kd == @PKG@.ShCombat.CK;   // 0.4.22
    Object[] tk = new Object[n];   // 0.4.22 combat: the kinds taken per island (id -> Long)
    boolean[] enOnly = new boolean[n];   // 0.4.22: only the Enchanted part of a stored count
    int cmp0 = @PKG@.ShMath.compactor(kd, p);
    java.util.Properties old = new java.util.Properties();   // 0.4.22: taken before the roll (nothing taken / a refused save puts it back)
    old.putAll(p);
    for (int i = 0; i < n; i++) {
      if (slot >= 0 && i != slot) continue;
      if (isC) {   // 0.4.22: the pool count -> its rolled drops (exactly what the grid showed), then the kinds asked for
        roll(p, i);
        java.util.LinkedHashMap tm = new java.util.LinkedHashMap();
        java.util.Iterator hi = @PKG@.ShMath.held(kd, p, i).entrySet().iterator();
        while (hi.hasNext()) {
          java.util.Map.Entry he = (java.util.Map.Entry) hi.next();
          if (only != null && !only.equals(he.getKey())) continue;
          tm.put(he.getKey(), he.getValue());
          take[i] += ((Long) he.getValue()).longValue();
        }
        tk[i] = tm;
      } else {
        long s0 = @PKG@.ShMath.stored(kd, p, i);
        take[i] = s0;
        if (only != null && s0 > 0L) {   // 0.4.22: one kind - the Enchanted part (every full 100 with an Auto-Compactor) or the base / smelted rest
          int t0 = @PKG@.ShIsl.ty(kd, p, i);
          boolean sm0 = @PKG@.ShTotem.smelts(kd, p, i) && @PKG@.ShIsl.SMELT[t0].length() > 0;
          String out0 = sm0 ? @PKG@.ShIsl.SMELT[t0] : @PKG@.ShIsl.PROD[t0];
          String en0 = sm0 ? @PKG@.ShIsl.SMELTE[t0] : @PKG@.ShIsl.ENCH[t0];
          boolean ce = cmp0 >= 1 && en0.length() > 0;
          if (ce && only.equals(en0)) { take[i] = (s0 / 100L) * 100L; enOnly[i] = true; }
          else if (only.equals(out0)) take[i] = ce ? s0 % 100L : s0;
          else take[i] = 0L;
        }
      }
      takeE[i] = bon.length() == 0 || (only != null && !only.equals(bon)) ? 0L : @PKG@.ShMath.ench(kd, p, i);
      String lg = @PKG@.ShStore.str(p, @PKG@.ShIsl.ik(kd, i, "legacy"));   // 0.4.8: "item:count" of a retyped 0.4.6 island
      int lc = lg.lastIndexOf(':');
      if (lc > 0) { try { takeL[i] = Long.parseLong(lg.substring(lc + 1).trim()); lid[i] = lg.substring(0, lc); } catch (Throwable t) { takeL[i] = 0L; } }
      if (takeL[i] < 0L) takeL[i] = 0L;
      if (only != null && (lid[i] == null || !only.equals(lid[i]))) takeL[i] = 0L;   // 0.4.22
''')
P.rep('''    if (want + wantE + wantL <= 0L) return "=Nothing is stored there yet.";
    java.util.Properties old = new java.util.Properties();
    old.putAll(p);
    for (int i = 0; i < n; i++) {
      if (take[i] > 0L) p.setProperty(@PKG@.ShMath.ik(kd, i, "stored"), String.valueOf(@PKG@.ShMath.stored(kd, p, i) - take[i]));
''', '''    if (want + wantE + wantL <= 0L) { if (isC) { for (int i = 0; i < n; i++) if (slot < 0 || i == slot) unroll(p, old, i); } return only != null ? "=None of that is stored any more - the page is up to date now." : "=Nothing is stored there yet."; }   // 0.4.22: the roll undone
    for (int i = 0; i < n; i++) {
      if (take[i] > 0L && isC) {   // 0.4.22: the rolled drops keep every kind (and part) not asked for
        java.util.LinkedHashMap rest = @PKG@.ShMath.held(kd, p, i);
        java.util.Iterator ti = ((java.util.LinkedHashMap) tk[i]).entrySet().iterator();
        while (ti.hasNext()) {
          java.util.Map.Entry te = (java.util.Map.Entry) ti.next();
          Object o = rest.get(te.getKey());
          long l0 = (o == null ? 0L : ((Long) o).longValue()) - ((Long) te.getValue()).longValue();
          if (l0 > 0L) rest.put(te.getKey(), Long.valueOf(l0)); else rest.remove(te.getKey());
        }
        @PKG@.ShMath.heldSet(kd, p, i, rest);
      } else if (take[i] > 0L) p.setProperty(@PKG@.ShMath.ik(kd, i, "stored"), String.valueOf(@PKG@.ShMath.stored(kd, p, i) - take[i]));
''')
P.rep('''    int cmp = @PKG@.ShMath.compactor(kd, p);
    long[] bm = new long[n];
''', '''    int cmp = @PKG@.ShMath.compactor(kd, p);
    Object[] tb = new Object[n];   // 0.4.22 combat: the kinds that did not fit, per island
    long[] bm = new long[n];
''')
# the combat give: the rolled kinds asked for, round-robin; what does not fit goes back AS THOSE KINDS (no fitFor re-mix any more)
_i0 = P.s.index('''      if (take[i] > 0L && kd == @PKG@.ShCombat.CK) {   // 0.4.11: a combat island's stored count = its mob pool's drops (ShCombat.split)''')
_i1 = P.s.index('''      } else if (take[i] > 0L) {
        int t = @PKG@.ShIsl.ty(kd, p, i);''', _i0)
_OLDC = P.s[_i0:_i1]
assert "fitFor" in _OLDC and _OLDC.count("bm[i] = take[i] - cdel;") == 1
P.rep(_OLDC, '''      if (take[i] > 0L && isC) {   // 0.4.22: the rolled kinds asked for (tk); round-robin, a stack of 100 at a time: one kind never takes every free slot
        java.util.LinkedHashMap tm = (java.util.LinkedHashMap) tk[i];
        int dn = tm.size();
        String[] di = new String[dn];
        long[] dq = new long[dn];
        java.util.Iterator ti = tm.entrySet().iterator();
        int dj = 0;
        while (ti.hasNext() && dj < dn) { java.util.Map.Entry te = (java.util.Map.Entry) ti.next(); di[dj] = (String) te.getKey(); dq[dj] = ((Long) te.getValue()).longValue(); dj++; }
        long[] dg = new long[dn];
        boolean prog = true;
        int pass = 0;
        while (prog && pass < 4000) {
          prog = false;
          pass++;
          for (int j = 0; j < dn; j++) {
            if (dq[j] <= dg[j]) continue;
            long g0 = @PKG@.ShInv.give(cs, di[j], Math.min(100L, dq[j] - dg[j]));
            if (g0 > 0L) { dg[j] += g0; prog = true; }
          }
        }
        long cdel = 0L;
        java.util.LinkedHashMap bk = new java.util.LinkedHashMap();
        for (int j = 0; j < dn; j++) {
          long g = dg[j];
          if (dq[j] > g) bk.put(di[j], Long.valueOf(dq[j] - g));   // 0.4.22: exactly the kinds that did not fit go back
          if (g <= 0L) continue;
          cdel += g;
          got.put(di[j], Long.valueOf((got.get(di[j]) == null ? 0L : ((Long) got.get(di[j])).longValue()) + g));
          cred.put(di[j], Long.valueOf((cred.get(di[j]) == null ? 0L : ((Long) cred.get(di[j])).longValue()) + g));
        }
        tb[i] = bk;
        baseGiven += cdel;
        xpD += (double) cdel * xi;
        bm[i] = take[i] - cdel;
        backM += bm[i];
''')
P.rep('''        long gr = rest > 0L ? @PKG@.ShInv.give(cs, out, rest) : 0L;''',
      '''        long gr = rest > 0L && !enOnly[i] ? @PKG@.ShInv.give(cs, out, rest) : 0L;   // 0.4.22: an Enchanted-only click leaves the rest stored''')
P.rep('''        if (bm[i] > 0L) p.setProperty(@PKG@.ShMath.ik(kd, i, "stored"), String.valueOf(@PKG@.ShMath.stored(kd, p, i) + bm[i]));''',
      '''        if (bm[i] > 0L && isC && tb[i] != null) {   // 0.4.22: back into the rolled drops, kind by kind
          java.util.LinkedHashMap hb = @PKG@.ShMath.held(kd, p, i);
          java.util.Iterator bi = ((java.util.LinkedHashMap) tb[i]).entrySet().iterator();
          while (bi.hasNext()) {
            java.util.Map.Entry be = (java.util.Map.Entry) bi.next();
            Object o = hb.get(be.getKey());
            hb.put(be.getKey(), Long.valueOf((o == null ? 0L : ((Long) o).longValue()) + ((Long) be.getValue()).longValue()));
          }
          @PKG@.ShMath.heldSet(kd, p, i, hb);
        } else if (bm[i] > 0L) p.setProperty(@PKG@.ShMath.ik(kd, i, "stored"), String.valueOf(@PKG@.ShMath.stored(kd, p, i) + bm[i]));''')
P.rep('''" compacted " + gEnch : "") + " " + got.toString());''', '''" compacted " + gEnch : "") + (only != null ? " only " + only : "") + " " + got.toString());''')
P.rep('''  if (baseGiven + gBonus <= 0L) return kd == @PKG@.ShCombat.CK ? "-Not enough room - a combat Collect gives every kind of drop together (a free slot each). Nothing was collected." : "-Your inventory is full - nothing was collected.";   // 0.4.11 fix''',
      '''  if (baseGiven + gBonus <= 0L) return "-Your inventory is full - nothing was collected.";   // 0.4.22: a combat Collect gives what fits, kind by kind''')
P.rep('''M(core, "public static String collect(java.util.UUID u, String k, int kd, int slot, @IC@[] cs) { String r = collect0(u, k, kd, slot, cs); @PKG@.ShSnd.ok(u, r, 0); return r; }")''',
      '''M(core, "public static String collect0(java.util.UUID u, String k, int kd, int slot, @IC@[] cs) { return collect0(u, k, kd, slot, cs, null); }")   # 0.4.22: every island, every kind
M(core, "public static String collect(java.util.UUID u, String k, int kd, int slot, @IC@[] cs) { String r = collect0(u, k, kd, slot, cs); @PKG@.ShSnd.ok(u, r, 0); return r; }")''')
P.rep('''M(core, "public static String collectBags(java.util.UUID u, String k, int kd, int slot, @IC@[] cs) { String r = collectBags0(u, k, kd, slot, cs); @PKG@.ShSnd.ok(u, r, 0); return r; }")
''', '''M(core, "public static String collectBags(java.util.UUID u, String k, int kd, int slot, @IC@[] cs) { String r = collectBags0(u, k, kd, slot, cs); @PKG@.ShSnd.ok(u, r, 0); return r; }")
# 0.4.22 THE GRID'S BAG CELL: the bags of every Combat island, island by island (collectBags0: gate, made outside the lock, debit first); stops when one comes back short
M(core, r"""
public static String collectBagsAll(java.util.UUID u, String k, int kd, @IC@[] cs) {
  if (kd != @PKG@.ShCombat.CK) return "-Only combat islands store bags.";
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "-This shard's file could not be read - ask an admin to look at the server log.";
  int n = @PKG@.ShMath.SLOTS;
  boolean[] has = new boolean[n];
  @PKG@.ShStore.LOCK.lock(); try {
    for (int i = 0; i < n; i++) has[i] = @PKG@.ShMath.hasIsland(kd, p, i) && @PKG@.ShMath.bags(p, i) > 0L;
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  long got = 0L;
  String last = null;
  for (int i = 0; i < n; i++) {
    if (!has[i]) continue;
    String r = collectBags0(u, k, kd, i, cs);
    if (r.startsWith("+Collected ")) {
      int sp = r.indexOf(' ', 11);
      long g = 0L;
      try { g = Long.parseLong(r.substring(11, sp)); } catch (Throwable t) { g = 0L; }
      got += g;
      if (r.indexOf("stay stored") >= 0) break;   // that island's bags did not all come out: the inventory (or one click's 36) is used up
    } else last = r;   // fix (critic): an island that answers "-..." (gone, full) never stops the others
  }
  if (got <= 0L) return last != null ? last : "=No unidentified bags stored yet.";
  long left = 0L;
  @PKG@.ShStore.LOCK.lock(); try {
    for (int i = 0; i < n; i++) if (@PKG@.ShMath.hasIsland(kd, p, i)) left += @PKG@.ShMath.bags(p, i);
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  return "+Collected " + @PKG@.ShCfg.num(got) + " unidentified bag" + (got == 1L ? "" : "s") + (left > 0L ? ". " + @PKG@.ShCfg.num(left) + " stay stored." : ".");
}""")
# 0.4.22: a grid cell's click = that item kind only, from every island (the bag cell "#bags" = every island's bags); the sting on a "+" result
M(core, r"""
public static String collectKind(java.util.UUID u, String k, int kd, String id, @IC@[] cs) {
  String r;
  if (id == null || id.length() == 0 || id.length() > 120) r = "-Pick an item first.";
  else if ("#bags".equals(id)) r = collectBagsAll(u, k, kd, cs);
  else r = collect0(u, k, kd, -1, cs, id);
  @PKG@.ShSnd.ok(u, r, 0);
  return r;
}""")
# 0.4.22 the grid's tables (build time): tier + rarity per item id
for f in ("public static final String TIER_SPEC = %s;" % jlit(G422_TSPEC), "public static final String RAR_SPEC = %s;" % jlit(G422_RSPEC),
          "public static final String[] RAR_BG = %s;" % _ja48(GRID_BG), "public static final String RAR_NONE = %s;" % jlit(GRID_BG_NONE),
          "public static final String BAG_ICON = %s;" % jlit(GRID_BAG),
          "public static volatile java.util.HashMap TIERS = null;", "public static volatile java.util.HashMap RARS = null;"):
    F(core, f)
M(core, r"""
public static java.util.HashMap specMap(String spec) {
  java.util.HashMap m = new java.util.HashMap();
  if (spec == null || spec.length() == 0) return m;
  String[] parts = spec.split("\\\\|");
  for (int i = 0; i < parts.length; i++) {
    int c = parts[i].indexOf(':');
    if (c <= 0) continue;
    try { m.put(parts[i].substring(0, c), Integer.valueOf(Integer.parseInt(parts[i].substring(c + 1)))); } catch (Throwable t) { }
  }
  return m;
}""")
M(core, r"""
public static int tierOf(String id) {
  if (id == null) return 0;
  java.util.HashMap m = TIERS;
  if (m == null) { m = specMap(TIER_SPEC); TIERS = m; }
  Object o = m.get(id);
  return o instanceof Integer ? ((Integer) o).intValue() : 0;
}""")
M(core, r"""
public static int rarOf(String id) {
  if (id == null) return 0;
  java.util.HashMap m = RARS;
  if (m == null) { m = specMap(RAR_SPEC); RARS = m; }
  Object o = m.get(id);
  int r = o instanceof Integer ? ((Integer) o).intValue() : 0;
  return r >= 1 && r <= 6 ? r : 0;
}""")
M(core, r"""
public static String rarBg(String id) {
  int r = rarOf(id);
  return r >= 1 && r <= RAR_BG.length ? RAR_BG[r - 1] : RAR_NONE;
}""")
# the sort key of a grid item: tier (untiered after every tier), its base item's name (an Enchanted item right after its base item), Enchanted last, the id
M(core, r"""
public static int gridCmp(String a, String b) {
  int ta = tierOf(a);
  int tb = tierOf(b);
  if (ta <= 0) ta = 1000;
  if (tb <= 0) tb = 1000;
  if (ta != tb) return ta < tb ? -1 : 1;
  String ba = @PKG@.ShIsl.enchBase(a);
  String bb = @PKG@.ShIsl.enchBase(b);
  int c = @PKG@.ShTotem.pretty(ba != null ? ba : a).compareToIgnoreCase(@PKG@.ShTotem.pretty(bb != null ? bb : b));
  if (c != 0) return c;
  if ((ba != null) != (bb != null)) return ba == null ? -1 : 1;
  return a.compareTo(b);
}""")
M(core, r"""
public static void gAdd(java.util.LinkedHashMap m, String id, long n) {
  if (id == null || n <= 0L) return;
  Object o = m.get(id);
  m.put(id, Long.valueOf((o == null ? 0L : ((Long) o).longValue()) + n));
}""")
# THE STORE GRID: what Collect all would pay right now, per item id, every island merged (the shard is the chest), sorted. Under the lock, after settle;
# the same parts and splits as collect0: the legacy line, a Combat island's rolled drops + the split of its pool count, another shard's stored count as
# its Enchanted part (Auto-Compactor, every full 100) + the base / smelted rest, the bonus finds. -> Object[]{ String[] ids, long[] qty }
M(core, r"""
public static Object[] gridOf(int kd, java.util.Properties p) {
  java.util.LinkedHashMap m = new java.util.LinkedHashMap();
  String bon = @PKG@.ShKind.BONUS[kd];
  int cmp = @PKG@.ShMath.compactor(kd, p);
  boolean isC = kd == @PKG@.ShCombat.CK;
  for (int i = 0; i < @PKG@.ShMath.SLOTS; i++) {
    String lg = @PKG@.ShStore.str(p, @PKG@.ShIsl.ik(kd, i, "legacy"));
    int lc = lg.lastIndexOf(':');
    if (lc > 0) { long ln = 0L; try { ln = Long.parseLong(lg.substring(lc + 1).trim()); } catch (Throwable t) { ln = 0L; } gAdd(m, lg.substring(0, lc), ln); }
    long s = @PKG@.ShMath.stored(kd, p, i);
    if (isC) {
      java.util.Iterator hi = @PKG@.ShMath.held(kd, p, i).entrySet().iterator();
      while (hi.hasNext()) { java.util.Map.Entry he = (java.util.Map.Entry) hi.next(); gAdd(m, (String) he.getKey(), ((Long) he.getValue()).longValue()); }
      if (s > 0L) {
        Object[] dm = @PKG@.ShCombat.rollFor(p, i, s);   // fix (critic): the same cumulative roll collect0 makes
        String[] di = (String[]) dm[0];
        long[] dq = (long[]) dm[1];
        for (int j = 0; j < di.length && j < dq.length; j++) if (di[j] != null && di[j].length() > 0) gAdd(m, di[j], dq[j]);
      }
    } else if (s > 0L) {
      int t = @PKG@.ShIsl.ty(kd, p, i);
      boolean sm = @PKG@.ShTotem.smelts(kd, p, i) && @PKG@.ShIsl.SMELT[t].length() > 0;
      String out = sm ? @PKG@.ShIsl.SMELT[t] : @PKG@.ShIsl.PROD[t];
      String en = sm ? @PKG@.ShIsl.SMELTE[t] : @PKG@.ShIsl.ENCH[t];
      long e = (cmp >= 1 && en.length() > 0) ? s / 100L : 0L;
      gAdd(m, en, e);
      gAdd(m, out, s - 100L * e);
    }
    if (bon.length() > 0) gAdd(m, bon, @PKG@.ShMath.ench(kd, p, i));
  }
  int n = m.size();
  String[] ids = new String[n];
  long[] q = new long[n];
  int c = 0;
  java.util.Iterator it = m.entrySet().iterator();
  while (it.hasNext() && c < n) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    String id = (String) e.getKey();
    if (id == null || !id.matches("[A-Za-z0-9_]+")) continue;   // only a plain item id goes into the markup
    ids[c] = id;
    q[c] = ((Long) e.getValue()).longValue();
    c++;
  }
  for (int a = 1; a < c; a++) {   // insertion sort (a handful of kinds)
    String x = ids[a];
    long y = q[a];
    int b = a - 1;
    while (b >= 0 && gridCmp(ids[b], x) > 0) { ids[b + 1] = ids[b]; q[b + 1] = q[b]; b--; }
    ids[b + 1] = x;
    q[b + 1] = y;
  }
  String[] oi = new String[c];
  long[] oq = new long[c];
  for (int a = 0; a < c; a++) { oi[a] = ids[a]; oq[a] = q[a]; }
  return new Object[] { oi, oq };
}""")
''')

# ---------------------------------------------------------------------------------------------------- 4. the Collect tab: the grid in the right panel, above Collect all
P.rep('''c1 = seg("c1")
''', '''c1 = seg("c1")
# 0.4.22 THE STORE GRID (Skyy 2026-11-14: "grid like a chest showing what all is in it, (but without a stack limit like in the pocket dimension."): the
# Pocket Dimension's cell look (kit icon_cell, a count label, the rarity square), GCOLS a row, GROWS rows show, the rest scrolls; filled at runtime (GRID_JAVA)
GCW, GCH, GGAP, GCOLS, GROWS, GROW_H = 80, 74, 2, 6, 4, 78
GMAX = 96
GLIST_H = GROWS * GROW_H + 2 * SUI.WELL_LIST_PAD
assert GCOLS * GCW + (GCOLS - 1) * GGAP <= (RW - 24) - 2 * SUI.WELL_LIST_PAD - 18, "0.4.22: a grid row fits the panel (scrollbar included)"
assert SUI.text_width("9,999,999", 15, bold=True) <= GCW - 8, "0.4.22: the full count fits the cell up to 9,999,999"
c1.append((R0, SUI.label(P + "GHead", "In this shard", "panelTitle", h=30)))
c1.text(R0, P + "GHint", J_("this.sgHint", "Click an item to collect just that kind."), "caption", size=13, h=24, w=RW - 24)
c1.append((R0, SUI.scroll_list(P + "GList", h=GLIST_H, w=RW - 24, well=True)))
c1.append((R0, SUI.spacer(h=8)))
assert 30 + 24 + GLIST_H + 8 + 30 + 3 * 30 + 4 * 26 + 14 + SUI.BTN_H <= CH - 24, "0.4.22: the grid + Collect all fit the right panel"
_gcell = lambda st: SUI.icon_cell(P + "GCell" + J_("gIx"), item=J_("this.sgIc[gIx]", "Ingredient_Bone_Fragment"), state=st, qty=True, w=GCW, h=GCH,
                                  icon_left=(GCW - (GCH - 10)) // 2, icon_bg=J_("this.sgBg[gIx]", "#2770b7(0.4)"))
GC_ROW = SUI.group(P + "GRow" + J_("gRr"), "Left", h=GROW_H, pad={"top": 2, "bottom": 2})
GC_CELL = SUI.choose("this.manage", _gcell("normal"), _gcell("static"))
GC_EMPTY = SUI.icon_cell(P + "GCell" + J_("gIx"), state="empty", w=GCW, h=GCH)
GC_GAP = SUI.spacer(w=GGAP)
cgs = seg("cgs")          # 0.4.22: a sample row of the grid for the build-time page checks (the Java fills it in GRID_JAVA)
cgs.append(("#" + P + "GList", GC_ROW))
cgs.append(("#" + P + "GRow" + J_("gRr"), _gcell("normal")))   # both looks of GC_CELL (the window check reads plain markup)
cgs.append(("#" + P + "GRow" + J_("gRr"), GC_GAP))
cgs.append(("#" + P + "GRow" + J_("gRr"), _gcell("static")))
cgs.append(("#" + P + "GRow" + J_("gRr"), GC_GAP))
cgs.append(("#" + P + "GRow" + J_("gRr"), GC_EMPTY))
GRID_JAVA = "\\n".join([
    "    int gRw = (this.sgN + %d) / %d;" % (GCOLS - 1, GCOLS),
    "    if (gRw < %d) gRw = %d;" % (GROWS, GROWS),
    "    for (int gRr = 0; gRr < gRw; gRr++) {",
    "    " + SUI.java_append("#" + P + "GList", GC_ROW),
    "    for (int gCc = 0; gCc < %d; gCc++) {" % GCOLS,
    "      int gIx = gRr * %d + gCc;" % GCOLS,
    "      if (gIx < this.sgN) {",
    "      " + SUI.java_append("#" + P + "GRow" + J_("gRr"), GC_CELL),
    '      b.set("#%sGCell" + gIx + "Qty.Text", this.sgQty[gIx]);' % P,
    '      if (this.manage) ev.addEventBinding(@BT@.Activating, "#%sGCell" + gIx, @EVD@.of("a", "gc:" + this.sgId[gIx]));' % P,
    "      } else {",
    "      " + SUI.java_append("#" + P + "GRow" + J_("gRr"), GC_EMPTY),
    "      }",
    "      if (gCc < %d) %s" % (GCOLS - 1, SUI.java_append("#" + P + "GRow" + J_("gRr"), GC_GAP)),
    "    }",
    "    }"])
''')
P.rep('''v = _menu("tabs3")
v.extend(SEG["t0"])
for i in range(5):''', '''v = _menu("tabs0")   # 0.4.22: the store grid's sample row (owner view)
for k_ in ["c0"] + [_n % (i, 0) for i in range(SLOTS) for _n in ("crowv%d_%d", "crowS%d_%d", "crowC%d_%d")] + ["c1", "cgs", "c1b"]:
    v.extend(SEG[k_])
VARIANTS.append(_foot(v))
v = _menu("tabs3")
v.extend(SEG["t0"])
for i in range(5):''')
P.rep('''    jseg("c1"), "    if (this.manage) {", jseg("c1b")''', '''    jseg("c1"), GRID_JAVA, "    if (this.manage) {", jseg("c1b")''')

# ---------------------------------------------------------------------------------------------------- 5. ShPage: the grid's data (fill), the click
P.rep('''          "public int sellSlot;", "public String sellTxt;",''', '''          "public int sgN;", "public String[] sgId;", "public String[] sgIc;", "public String[] sgQty;", "public String[] sgBg;", "public String sgHint;",   # 0.4.22 the store grid
          "public int sellSlot;", "public String sellTxt;",''')
P.rep('''M(page, r"""
public void fill(String k, @IC@[] cs) {''', '''# 0.4.22: a cell's count - the full number ("12,345": no stack limit), 10 million and up as "12M" (no store reaches it today)
M(page, r"""
public static String gQtyTxt(long n) {
  return n < 10000000L ? @PKG@.ShCfg.num(n) : (n / 1000000L) + "M";
}""")
# 0.4.22: the grid's cells from ShCore.gridOf (+ the bag cell when SkyyGear makes bags: its icon id then exists), outside the store lock
M(page, r"""
public void gridFill(Object[] gd, int kd) {
  String[] ids = gd == null ? new String[0] : (String[]) gd[0];
  long[] q = gd == null ? new long[0] : (long[]) gd[1];
  boolean bag = kd == @PKG@.ShCombat.CK && this.bagT > 0L && @PKG@.ShCfg.fn("gear:fn:box") != null;
  int all = ids.length + (bag ? 1 : 0);
  int n = all > @GMAX@ ? @GMAX@ : all;
  int room = bag ? n - 1 : n;
  this.sgId = new String[n]; this.sgIc = new String[n]; this.sgQty = new String[n]; this.sgBg = new String[n];
  int c = 0;
  for (int i = 0; i < ids.length && c < room; i++) { this.sgId[c] = ids[i]; this.sgIc[c] = ids[i]; this.sgQty[c] = gQtyTxt(q[i]); this.sgBg[c] = @PKG@.ShCore.rarBg(ids[i]); c++; }
  if (bag && c < n) { this.sgId[c] = "#bags"; this.sgIc[c] = @PKG@.ShCore.BAG_ICON; this.sgQty[c] = gQtyTxt(this.bagT); this.sgBg[c] = @PKG@.ShCore.rarBg(@PKG@.ShCore.BAG_ICON); c++; }
  this.sgN = c;
  int more = all - c;
  if (!this.manage) this.sgHint = c == 0 ? "Nothing is stored here yet." : "What is stored here now. The island owner collects it.";
  else if (c == 0) this.sgHint = "Nothing is stored here yet - your islands are growing.";
  else this.sgHint = more > 0 ? "Click an item to collect just that kind (" + more + " more kinds: use Collect all)." : "Click an item to collect just that kind.";
}""".replace("@GMAX@", str(GMAX)))
M(page, r"""
public void fill(String k, @IC@[] cs) {''')
P.rep('''  for (int sv0 = 0; sv0 < 11; sv0++) this.sv[sv0] = "";
''', '''  for (int sv0 = 0; sv0 < 11; sv0++) this.sv[sv0] = "";
  this.sgN = 0; this.sgId = new String[0]; this.sgIc = new String[0]; this.sgQty = new String[0]; this.sgBg = new String[0]; this.sgHint = "Nothing is stored here yet.";   // 0.4.22
''')
P.rep('''  @PKG@.ShTotem.warmEss(kd);   // 0.4.14''', '''  Object[] gd = null;   // 0.4.22: the store grid (read under the lock, drawn after it)
  @PKG@.ShTotem.warmEss(kd);   // 0.4.14''')
P.rep('''      long s = @PKG@.ShMath.stored(kd, p, i);
      long cn = @PKG@.ShMath.comp(kd, p, i);''', '''      long s = @PKG@.ShMath.stored(kd, p, i) + @PKG@.ShMath.heldN(kd, p, i);   // 0.4.22: + a Combat island's rolled drops
      long cn = @PKG@.ShMath.comp(kd, p, i);''')
P.rep('''    this.cCap = "Rates below are online. Offline: "''', '''    gd = @PKG@.ShCore.gridOf(kd, p);   // 0.4.22
    this.cCap = "Rates below are online. Offline: "''')
P.rep('''  } finally { @PKG@.ShStore.LOCK.unlock(); }
  long per = (long) @PKG@.ShCfg.xpOf(kd);
  long xp = total * per''', '''  } finally { @PKG@.ShStore.LOCK.unlock(); }
  gridFill(gd, kd);   // 0.4.22: after the lock (asks the gear bridge)
  long per = (long) @PKG@.ShCfg.xpOf(kd);
  long xp = total * per''')
P.rep('''    if (a.equals("colall")) return @PKG@.ShCore.collect(u, k, kd, -1, invOf(ref, st));
''', '''    if (a.startsWith("gc:")) {   // 0.4.22: a grid cell = that item kind only (the event names the item, never its place in the grid)
      fill(k, invOf(ref, st));
      if (!this.manage) return "-Only the island owner collects here.";
      return @PKG@.ShCore.collectKind(u, k, kd, a.substring(3), invOf(ref, st));
    }
    if (a.equals("colall")) return @PKG@.ShCore.collect(u, k, kd, -1, invOf(ref, st));
''')
# /shardadmin info names the rolled drops
P.rep('''", stored " + @PKG@.ShMath.stored(kd, p, i) + " + "''', '''", stored " + @PKG@.ShMath.stored(kd, p, i) + " + " + @PKG@.ShMath.heldN(kd, p, i) + " rolled drops + "''')

# ---------------------------------------------------------------------------------------------------- 6. the ready line
P.rep('''log("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.21:''', '''log("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.22: the Collect tab shows a grid of what is stored (click one = collect that kind); 0.4.21:''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0, "command / system registrations changed"
P.finish()
