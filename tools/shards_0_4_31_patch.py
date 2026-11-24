"""Derive SkyyShards/build_skyyshards_0.4.31.py from the GENERATED SkyyShards 0.4.30 (build_skyyshards_0.4.30.py = the tools/deploy_set.py SET
pin, made by tools/shards_0_4_30_patch.py - edit the patch, never the generated file). Every anchor is asserted once; at the end every change
is undone on a copy and compared with 0.4.30 (tools/soundpass_gen.Patch). Line endings kept.
Run:   python tools/shards_0_4_31_patch.py   then   python SkyyShards/build_skyyshards_0.4.31.py   (never --deploy)
Check: python SkyyShards/test_skyyshards_0.4.31.py

0.4.31 (2026-11-23) = ONE ISLAND PER ZONE FOR EVERY GATHERING SHARD (round azone1; Skyy 2026-11-22 docs/answered/world.md "ISLAND PER ZONE FOR EVERY
  SHARD", on a screenshot of the Farming Shard islands map, one card per crop: "lets do island per zone for all of them instead of per crop"; Skyy
  2026-11-22 "i cant go into my iron island. (lets do an island per zone, instead of per ore. so iron becomes an upgrade in the zone 1 island instead of its
  own island."; Skyy 2026-11-23 "looks better. go head and build everything on your list.").
  - SURVEY. Vanilla (Assets.zip): no clicker / zone-island page (0.4.23-0.4.30 surveys); mods: nothing new to pack. Nothing packed. The round reuses
    mzone1's (0.4.30) code paths, generalised from Mining to every zoned kind (ShIsl.zoned = Mining, Foraging, Farming, Ranching, Orchard).
  - COMBAT is NOT changed: its ladder has been the five zones since 0.4.11 (one island = one zone, "Zone 1..5"; its monster kinds open with Town level
    inside the zone island since 0.4.26) - it already is one island a zone.
  - MINING is NOT changed (0.4.30 rules; the shared code gives the same answers for it - harness MZ31).
  - 1. THE MAP = ONE CARD A ZONE (Foraging, Farming, Ranching, Orchard). Card 3 x zone (= the zone's first type: 3 tiers a zone, asserted at build) names the
    zone's types ("Wheat + Lettuce + Carrot") and says Yours / Shown now (n / m crops; "add Lettuce inside") / Locked: <skill> N / Buy: <cost> / what to add
    first. BUY = the zone's first type's island at its 0.4.30 price (isl.buyHours + isl.buyItems; the zone lock = click.<kind>.zoneLevel as today); OPEN
    enters the zone's island (ShIsl.zoneSlot = the zone's lowest-tier island) - every owned zone, the one shown now too. Ranching / Orchard Zones 4-5 stay
    empty ("No pens / orchards in this zone yet").
  - 2. EVERY FURTHER TYPE OF A ZONE IS AN UPGRADE of the zone island: a 7th row (Foraging "Trees", Farming "Crops", Ranching "Animals", Orchard "Fruits";
    "n / m crops", the next type, have / need cost lines, button "Add crop" / "Add tree" / "Add animal" / "Add fruit"). Cost = exactly that type's own 0.4.30
    island price (isl.buyHours of the coin curve at its tier + isl.buyItems of that type - no new number; the harness prints the table). Bought = the key
    <kind>.i<zone island>.ores (the same key Mining uses: a comma list of type keys). Its plots / trees / animals join the island exactly as an owned type
    island's: spot i is type i mod the zone's owned types (tier order), with that type's picture, product, vanilla quantities, tool gate (hoe / hatchet
    tier), Fortune block and XP; the island's own upgrades (Plot size, Plot count, Irrigation, size ...) apply to every spot. Spirits: what the island's
    totems make (the same count as before) is shared round-robin over its types (ShMath.oreShare, generalised): the island's own type stays its stock,
    every other type's share goes into its storage (.drops) as that type, its Collect XP owed at once (Farming: at the spirits' own XP a crop). An island
    with no upgrade makes exactly what it made in 0.4.30 (nothing written). Tier order stays (owns counts upgrades); a double click buys once (the button
    carries the type the page showed); a stale page (another island / profile) buys nothing; too few coins / items = refused, nothing paid
    (ShCore.purchaseM). Buying a 2nd type AS AN ISLAND is refused once its zone has an island (ShCore.buyIsland0).
  - 3. ONE-TIME JOURNALED MIGRATION PER PROFILE (ShStore.migrate6, marker azone.done=1; after migrate5): for Foraging, Farming, Ranching and Orchard, each zone
    with more than one island keeps its lowest-tier island (the zone island; a lone non-base island IS the zone island) and folds every other one into it
    with the mzone1 rules (ShStore.mzFold, generalised): type -> its ores list; Island size = the larger; Amount / Decorations / Irrigation = the HIGHER
    effective level (5 x (size - 1) + level); Tree / Plot size (nsize) = the higher; EVERY totem appended (tiers, modifiers, boosters, uids); every item into
    the zone island's storage (.drops) in base units (stock as its product, an Enchanted legacy line = 100 of its base each, its own .drops, rare finds
    added); NEW for these kinds: the seed store (seeds / saplings) and the Eternal seeds a farm island was given (<kind>.i<n>.eternal) come back as those
    items in the storage; the stock's Collect XP is owed at once (owed.xp / owed.xp.<Skill>; Farming at the island's tracked XP a crop). Before: production
    settled; after: CHECKED per kind (items in base units incl. seed stores + Eternal seeds, totems, owned types, islands = before - folded) - any difference,
    an unknown island key, a refused History copy or save, an error mid-fold (fixer 2; migrate5 too) = nothing changes (memory restored, a warning once, tried again at the next load). History copy
    shards/history/clicker/<pkey>.pre-0.4.31.properties first (byte-checked), ONE save with the marker, one collect.log journal line naming every fold + the
    Undo. Nothing to fold = nothing written, no marker. The marker never skips the check (an island re-bought under a 0.4.30 rollback folds too).
  NUMBERS: none new (a type upgrade = the 0.4.30 island price of that type). Changed Server Setup rows: none.
  SAVED DATA: <kind>.i<n>.ores for foraging / farming / ranching / orchard (missing = none), <kind>.i<n>.orr (the spirits' next type), <kind>.i<n>.xpr (an XP
    fraction), azone.done=1 (marker, only on a profile that was folded), owed.xp / owed.xp.<Skill> (the existing owed-XP keys; they grow).
  ROLLBACK 0.4.31 -> 0.4.30 alone: the jar. 0.4.30 ignores the four kinds' .ores / .orr / .xpr + azone.done (kept in the file): EVERY type owned through the
    new row - folded by the migration OR bought on 0.4.31 - is NOT owned there: its card shows "Buy" again (the full island price), the zone island grows its
    own type only, and tier order makes the player buy that type again before the next zone. Everything merged stays on the zone island (storage items,
    seeds / Eternal seeds as items, totems, size, upgrades - Collect all pays them); owed XP is paid by 0.4.30 too. Do NOT re-buy a type under 0.4.30 (paid
    twice; back on 0.4.31 that island folds again at the next load - its items, totems and upgrades kept, the journal names it - the second price is not
    refunded). Advice: make 0.4.31 the Shards rollback floor once a profile has folded or bought a type upgrade. Full Undo of the fold: stop the server,
    copy shards/history/clicker/<pkey>.pre-0.4.31.properties back over shards/<pkey>.properties (= the last save before the fold).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

HERE = os.path.join(ROOT, "SkyyShards")
P = G.Patch(os.path.join(HERE, "build_skyyshards_0.4.30.py"), os.path.join(HERE, "build_skyyshards_0.4.31.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.4.30"\n') and P.has("GENERATED by tools/shards_0_4_30_patch.py") and P.has("migrate5") and not P.has("migrate6"), \
    "not the generated SkyyShards 0.4.30"
REG0, SYS0 = P.s.count("registerCommand("), P.s.count("registerSystem(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.4.31 (2026-11-23)"):].rstrip() + "\n"


def cut(a, b):
    """the text from anchor a (included) up to anchor b (excluded); a unique"""
    assert P.s.count(a) == 1 and P.s.count(b) >= 1, (a[:80], b[:80])
    i = P.s.index(a)
    j = P.s.index(b, i)
    return P.s[i:j]


def region(a, b, pairs):
    """inside the region a..b (a unique) replace each (old, new); every old exactly once in the region; recorded as ONE change"""
    r = cut(a, b)
    n = r
    for old, new in pairs:
        assert n.count(old) == 1, ("region %s: anchor count %d" % (a[:60], n.count(old)), old[:160])
        n = n.replace(old, new, 1)
    P.rep(r, n)


# ---------------------------------------------------------------------------------------------------- 0. header + version
P.rep('''"""SkyyShards 0.4.30 - build script (javassist via jpype). GENERATED by tools/shards_0_4_30_patch.py from build_skyyshards_0.4.29.py
(generated by tools/shards_0_4_29_patch.py from 0.4.28, ... back to tools/shards_0_4_patch.py from 0.3.2; edit the patch, never this file).
Changes are marked "0.4.30" /''', '''"""SkyyShards 0.4.31 - build script (javassist via jpype). GENERATED by tools/shards_0_4_31_patch.py from build_skyyshards_0.4.30.py
(generated by tools/shards_0_4_30_patch.py from 0.4.29, ... back to tools/shards_0_4_patch.py from 0.3.2; edit the patch, never this file).
Changes are marked "0.4.31" / "0.4.30" /''')
P.rep('''Run:   python SkyyShards/build_skyyshards_0.4.30.py   -> SkyyShards/SkyyShards-0.4.30.jar   (never --deploy: tools/deploy_set.py installs the set)
Check: python SkyyShards/test_skyyshards_0.4.30.py
''', '''Run:   python SkyyShards/build_skyyshards_0.4.31.py   -> SkyyShards/SkyyShards-0.4.31.jar   (never --deploy: tools/deploy_set.py installs the set)
Check: python SkyyShards/test_skyyshards_0.4.31.py
''' + NOTE)
P.rep('VERSION = "0.4.30"\n', 'VERSION = "0.4.31"\n')

# ---------------------------------------------------------------------------------------------------- 1. ShStore: migrate6's stub + its call in get()
P.rep('''M(st, "public static void migrate5(String k, java.util.Properties p) { }")   # 0.4.30: the body is set below (after ShClk) - the Mining zone migration
''', '''M(st, "public static void migrate5(String k, java.util.Properties p) { }")   # 0.4.30: the body is set below (after ShClk) - the Mining zone migration
M(st, "public static void migrate6(String k, java.util.Properties p) { }")   # 0.4.31: the body is set below (after ShClk) - the zone island migration (4 kinds)
F(st, "public static final java.util.concurrent.atomic.AtomicLong AZMIG = new java.util.concurrent.atomic.AtomicLong();")   # 0.4.31: files folded
F(st, "public static final java.util.concurrent.atomic.AtomicLong AZCHK = new java.util.concurrent.atomic.AtomicLong();")   # 0.4.31: loads with nothing to fold
F(st, "public static final java.util.concurrent.atomic.AtomicLong AZWAIT = new java.util.concurrent.atomic.AtomicLong();")   # 0.4.31: folds refused (nothing changed)
''')
P.rep('''    migrate5(k, p);   // 0.4.30: the Mining zone migration - every 2nd ore island of a zone folds into the zone's quarry (marker mzone.done=1)
''', '''    migrate5(k, p);   // 0.4.30: the Mining zone migration - every 2nd ore island of a zone folds into the zone's quarry (marker mzone.done=1)
    migrate6(k, p);   // 0.4.31: the zone island migration - Foraging / Farming / Ranching / Orchard: every 2nd island of a zone folds into its zone island (azone.done=1)
''')

# ---------------------------------------------------------------------------------------------------- 2. ShIsl: zoned kinds, their words; owns for every zoned kind
P.rep('''M(isl48, "public static boolean mineKd(int kd) { return kd == @MQK@; }".replace("@MQK@", str(MQ_K)))
''', '''M(isl48, "public static boolean mineKd(int kd) { return kd == @MQK@; }".replace("@MQK@", str(MQ_K)))
# 0.4.31 (tools/shards_0_4_31_patch.py) ONE ISLAND PER ZONE FOR EVERY GATHERING SHARD: Mining (0.4.30) + Foraging, Farming, Ranching, Orchard. Combat's ladder
# IS its zones since 0.4.11 (one island a zone already) - not zoned here. The words each kind's zone island uses (the page, the purchase, the journal)
AZ_KD = [MQ_K, CK_FK, FQ_K, RQ_K, OQ_K]
AZ_W = {MQ_K: ("quarry", "Quarry", "ore", "ores", "Ores", "ore nodes", "ore", "Ores"),
        CK_FK: ("grove", "Grove", "tree", "trees", "Trees", "trees", "logs", "Trees"),
        FQ_K: ("farm", "Farm", "crop", "crops", "Crops", "plots", "crops", "Crops"),
        RQ_K: ("ranch", "Ranch", "animal", "animals", "Animals", "animals", "goods", "Animals"),
        OQ_K: ("orchard", "Orchard", "fruit", "fruits", "Fruits", "fruit trees", "fruit", "Fruits")}
for _k in AZ_KD:   # the zone's first type = ladder index 3 x (zone - 1) (3 tiers a zone, tiers 1, 2, 3 ...): the map's card 3 x zone is that type
    assert all(LAD[_k][_i]["tier"] == _i + 1 for _i in range(len(LAD[_k]))) or _k == MQ_K, (KINDS[_k], [_t["tier"] for _t in LAD[_k]])
for _j, _fn in enumerate(("ZW", "ZWC", "TW", "TWS", "TWSC", "SPW", "SHW", "ROWN")):
    F(isl48, "public static final String[] %s = new String[] { %s };" % (_fn, ", ".join(jlit(AZ_W[_k][_j] if _k in AZ_W else "island") for _k in range(NK))))
M(isl48, "public static boolean zoned(int kd) { return %s; }" % " || ".join("kd == %d" % _k for _k in AZ_KD))
''')
P.rep('''  if (!mineKd(kd)) return false;
  int s = zoneSlot(kd, p, zoneOf(t));''', '''  if (!zoned(kd)) return false;   // 0.4.31: every gathering shard (was Mining only)
  int s = zoneSlot(kd, p, zoneOf(t));''')

# ---------------------------------------------------------------------------------------------------- 3. ShCore.buyIsland0: no 2nd island in a zone that has one (every zoned kind)
P.rep('''    if (@PKG@.ShIsl.mineKd(kd) && @PKG@.ShIsl.zoneSlot(kd, p, @PKG@.ShIsl.zoneOf(t)) >= 0) return "-" + @PKG@.ShIsl.NAME[t] + " is an upgrade of your Zone " + @PKG@.ShIsl.zoneOf(t) + " quarry now - add it on the quarry's Ores row.";   // 0.4.30: one island a zone''',
      '''    if (@PKG@.ShIsl.zoned(kd) && @PKG@.ShIsl.zoneSlot(kd, p, @PKG@.ShIsl.zoneOf(t)) >= 0) return @PKG@.ShIsl.mineKd(kd) ? "-" + @PKG@.ShIsl.NAME[t] + " is an upgrade of your Zone " + @PKG@.ShIsl.zoneOf(t) + " quarry now - add it on the quarry's Ores row."
        : "-" + @PKG@.ShIsl.NAME[t] + " is an upgrade of your Zone " + @PKG@.ShIsl.zoneOf(t) + " " + @PKG@.ShIsl.ZW[kd] + " now - add it on the island's " + @PKG@.ShIsl.ROWN[kd] + " row.";   // 0.4.30: one island a zone; 0.4.31: every zoned kind''')

# ---------------------------------------------------------------------------------------------------- 4. ShClk: a zoned kind's types in a zone + its island; isBase for every zoned kind
P.rep('''M(ckc, "public static boolean isBase(java.util.Properties p, int kd, int slot) { return kd != MK || (slot >= 0 && baseSlot(p, @PKG@.ShIsl.zoneOf(@PKG@.ShIsl.ty(kd, p, slot))) == slot); }")   # fix: under ShStore.LOCK
''', '''# 0.4.31: any zoned kind - the types this profile owns in zone z (an island or an upgrade on the zone island), tier order; the zone island's slot
M(ckc, r"""
public static int[] zoneOwnedK(int kd, java.util.Properties p, int z) {
  int L0 = @PKG@.ShIsl.LAD0[kd];
  int LN = @PKG@.ShIsl.LADN[kd];
  int[] a = new int[LN];
  int n = 0;
  for (int i = 0; i < LN; i++) {
    int t = L0 + i;
    if (@PKG@.ShIsl.zoneOf(t) != z || !@PKG@.ShIsl.owns(kd, p, t)) continue;
    a[n] = t; n++;
  }
  int[] r = new int[n];
  for (int i = 0; i < n; i++) r[i] = a[i];
  return r;
}""")
M(ckc, "public static int baseSlotK(int kd, java.util.Properties p, int z) { return @PKG@.ShIsl.zoneSlot(kd, p, z); }")
M(ckc, "public static boolean isBase(java.util.Properties p, int kd, int slot) { return !@PKG@.ShIsl.zoned(kd) || (slot >= 0 && baseSlotK(kd, p, @PKG@.ShIsl.zoneOf(@PKG@.ShIsl.ty(kd, p, slot))) == slot); }")   # fix: under ShStore.LOCK; 0.4.31: every zoned kind
''')

# the clicks (harvest / gather / chop): the zone island only; spot i = the zone's owned type i mod n (one type = exactly 0.4.30)
_SPOT_CHK = '''  if (spot < 0 || spot >= n || spot >= NSPOT) return res("=The page is up to date now.", "");
'''
_SPOT_NEW = '''  if (spot < 0 || spot >= n || spot >= NSPOT) return res("=The page is up to date now.", "");
  t = tys[spot % tys.length];   // 0.4.31: this spot's type (the zone island's own type, or a type added on it)
'''
_TY_OLD = '''    t = @PKG@.ShIsl.ty(kd, p, slot);
    n = @PKG@.ShIsl.treeN('''
_TY_NEW = '''    t = @PKG@.ShIsl.ty(kd, p, slot);
    tys = zoneOwnedK(kd, p, @PKG@.ShIsl.zoneOf(t));   // 0.4.31: the zone island's types
    if (tys.length == 0 || baseSlotK(kd, p, @PKG@.ShIsl.zoneOf(t)) != slot) return res("=The page is up to date now.", "");
    n = @PKG@.ShIsl.treeN('''
_DECL = "  int t; int n; int irr; long use; long lim;\n"
_DECL_NEW = "  int t; int n; int irr; long use; long lim; int[] tys;\n"
_CHG_OLD = "if (!@PKG@.ShMath.hasIsland(kd, p, slot) || @PKG@.ShIsl.ty(kd, p, slot) != t) { unfell(key, spot, hpMax); return res(\"-That island changed meanwhile - the page is up to date now.\", \"\"); }"
_CHG_NEW = "if (!@PKG@.ShMath.hasIsland(kd, p, slot) || !@PKG@.ShIsl.owns(kd, p, t) || baseSlotK(kd, p, @PKG@.ShIsl.zoneOf(t)) != slot) { unfell(key, spot, hpMax); return res(\"-That island changed meanwhile - the page is up to date now.\", \"\"); }   // 0.4.31"
for _fn, _end in (("public static Object[] harvest(", "# ---- 0.4.26 THE COMBAT TOWN"), ("public static Object[] gather(", "# THE CLICK: Object[]{ status"),
                  ("public static Object[] chop(", "# TREE SIZE: coins")):
    region(_fn, _end, [(_DECL, _DECL_NEW), (_TY_OLD, _TY_NEW), (_SPOT_CHK, _SPOT_NEW), (_CHG_OLD, _CHG_NEW)])

# the type upgrade (0.4.30's ore upgrade, every zoned kind): the zone's next type joins its island at the price its own island had
_BUY_OLD = cut('''public static String buyOre0(java.util.UUID u, String k, int kd, int slot, int li, @IC@[] cs) {''', '''M(ckc, "public static String buyOre(java.util.UUID u''')
P.rep(_BUY_OLD, r'''public static String buyOre0(java.util.UUID u, String k, int kd, int slot, int li, @IC@[] cs) {   // 0.4.31: every zoned kind (Mining's words kept)
  if (kd == MK && (!@PKG@.ShCfg.ON || !@PKG@.ShCfg.CK_ON || !@PKG@.ShCfg.MQ_ON)) return "-The Mining quarry is switched off on this server.";
  if (!@PKG@.ShIsl.zoned(kd)) return "-Ores are a Mining quarry upgrade.";
  if (!@PKG@.ShCfg.ON || !@PKG@.ShCfg.CK_ON) return "-The shard clicker is switched off on this server.";
  if (kd == CRK && !@PKG@.ShCfg.FQ_ON) return "-The Farming clicker is switched off on this server.";
  if ((kd == RNK || kd == ORK) && !gatherOn(kd)) return kd == RNK ? "-The Ranching clicker is switched off on this server." : "-The Orchard clicker is switched off on this server.";
  boolean mq = kd == MK;
  String zw = @PKG@.ShIsl.ZW[kd];
  if (li < 0 || li >= @PKG@.ShIsl.LADN[kd]) return "=The page is up to date now.";
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "-This shard's file could not be read.";
  if (cs == null) return "-Your inventory could not be read - try again.";
  String no = @PKG@.ShCore.gateOwn(u, k, kd, p);
  if (no != null) return no;
  int t = @PKG@.ShIsl.LAD0[kd] + li;
  int z = @PKG@.ShIsl.zoneOf(t);
  String zno = @PKG@.ShIsl.zoneNo(u, kd, t);   // the bridges before the lock
  if (zno != null) return zno;
  double cv = @PKG@.ShCore.tierCv(t);
  String cur; long ver;
  @PKG@.ShStore.LOCK.lock(); try {
    if (slot < 0 || slot >= @PKG@.ShMath.SLOTS || !@PKG@.ShMath.hasIsland(kd, p, slot)) return "-That island is not yours yet.";
    if (!isBase(p, kd, slot) || @PKG@.ShIsl.zoneOf(@PKG@.ShIsl.ty(kd, p, slot)) != z) return mq ? "=The page is up to date now - open the quarry again." : "=The page is up to date now - open the island again.";
    if (@PKG@.ShIsl.owns(kd, p, t)) return mq ? "=Your Zone " + z + " quarry mines " + @PKG@.ShIsl.NAME[t] + " already." : "=Your Zone " + z + " " + zw + " has " + @PKG@.ShIsl.NAME[t] + " already.";
    int nx = @PKG@.ShIsl.nextTier(kd, p);
    if (nx != li) return nx < 0 ? (mq ? "=Your quarries mine every ore already." : "=You have every " + @PKG@.ShIsl.TW[kd] + " of this shard already.")
        : "-Add " + @PKG@.ShIsl.NAME[@PKG@.ShIsl.LAD0[kd] + nx] + " first (" + (mq ? "ores and quarries" : @PKG@.ShIsl.TWS[kd] + " and islands") + " come in tier order).";
    cur = @PKG@.ShStore.str(p, @PKG@.ShMath.ik(kd, slot, "ores"));
    ver = @PKG@.ShStore.ver(k);   // purchaseM commits only while nothing was saved since
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  long coins = @PKG@.ShIsl.coins(@PKG@.ShCfg.BUY_H, cv);
  Object[] mats = @PKG@.ShIsl.mats(kd, t, @PKG@.ShCfg.BUY_ITEMS[kd], 0, 1L);
  String nv = cur.length() == 0 ? @PKG@.ShIsl.KEY[t] : cur + "," + @PKG@.ShIsl.KEY[t];
  String r = @PKG@.ShCore.purchaseM(u, k, kd, p, cs, mats, coins, new String[] { @PKG@.ShMath.ik(kd, slot, "ores") }, new String[] { nv }, @PKG@.ShIsl.TW[kd],
                                    @PKG@.ShKind.KEYS[kd] + " add " + @PKG@.ShIsl.TW[kd] + " " + @PKG@.ShIsl.KEY[t] + " to the Zone " + z + " " + zw + " (slot " + slot + ")", ver);
  if (r != null) return r;
  return "+" + @PKG@.ShIsl.NAME[t] + " added to your Zone " + z + " " + zw + " - its " + @PKG@.ShIsl.SPW[kd] + " join the others.";
}""")
''')

# ---------------------------------------------------------------------------------------------------- 5. ShMath: the spirits share over every zoned island's types; the XP
P.rep('''M(mth, r"""
public static int[] shareOres(int kd, java.util.Properties p, int slot) {
  if (p == null || kd != @PKG@.ShClk.MK || !hasIsland(kd, p, slot)) return new int[0];''', '''# 0.4.31: the same with a double XP total (Farming: the spirits' own XP a crop); Mining's oweXp = this with units x xpOf (the same integers)
M(mth, r"""
public static long oweXpD(int kd, java.util.Properties p, int slot, double xpUnits) {
  if (p == null || !(xpUnits > 0.0) || Double.isNaN(xpUnits) || Double.isInfinite(xpUnits)) return 0L;
  String rk = ik(kd, slot, "xpr");
  long c = @PKG@.ShStore.lng(p, rk, 0L);
  if (c < 0L || c > 99L) c = 0L;
  long h = (long) Math.floor(xpUnits * (double) @PKG@.ShCfg.XP_PCT + 0.000000001) + c;
  long xp = h / 100L;
  long r = h % 100L;
  if (r > 0L) p.setProperty(rk, String.valueOf(r)); else p.remove(rk);
  if (xp > 0L) {
    String sk = @PKG@.ShKind.SKILL[kd];
    String key = "Farming".equals(sk) ? "owed.xp" : "owed.xp." + sk;
    long o = @PKG@.ShStore.lng(p, key, 0L);
    p.setProperty(key, String.valueOf((o < 0L ? 0L : o) + xp));
  }
  return xp;
}""")
M(mth, r"""
public static int[] shareOres(int kd, java.util.Properties p, int slot) {
  if (p == null || !@PKG@.ShIsl.zoned(kd) || !hasIsland(kd, p, slot)) return new int[0];   // 0.4.31: every zoned kind''')
P.rep('''  int z = @PKG@.ShIsl.zoneOf(t);
  if (@PKG@.ShClk.baseSlot(p, z) != slot) return new int[0];
  int[] o = @PKG@.ShClk.zoneOwned(p, z);''', '''  int z = @PKG@.ShIsl.zoneOf(t);
  if (@PKG@.ShClk.baseSlotK(kd, p, z) != slot) return new int[0];   // 0.4.31
  int[] o = @PKG@.ShClk.zoneOwnedK(kd, p, z);''')
P.rep('''  if (out > 0L) { heldSet(kd, p, slot, m); oweXp(kd, p, slot, out); }''',
      '''  if (out > 0L) { heldSet(kd, p, slot, m); if (kd == FK) oweXpD(kd, p, slot, (double) out * @PKG@.ShTotem.xpPer(kd, p, slot, size(kd, p, slot), @PKG@.ShCore.now())); else oweXp(kd, p, slot, out); }   // 0.4.31: a farm's crops at the spirits' XP''')
# settle: the shared part is not stock (the farm's XP-of-stock tracking counts only what stayed)
region('''public static long settle(int kd, java.util.Properties p, int slot, long now) {''', '''M(mth, "public static long settle(java.util.Properties p, int slot, long now)''', [
    ("  long made = 0L;\n  long from = last;\n", "  long made = 0L;\n  long shr = 0L;   // 0.4.31: what the spirits made of the island's other types (its storage, not its stock)\n  long from = last;\n"),
    ("    stored += made - oreShare(kd, p, slot, made);", "    shr = oreShare(kd, p, slot, made);\n    stored += made - shr;"),
    ("xpSet(kd, p, slot, bs, xa0 * (double) (bs - made) + (made > 0L ? (double) made * @PKG@.ShTotem.xpPer(kd, p, slot, size(kd, p, slot), from) : 0.0));",
     "xpSet(kd, p, slot, bs, xa0 * (double) (bs - (made - shr)) + (made - shr > 0L ? (double) (made - shr) * @PKG@.ShTotem.xpPer(kd, p, slot, size(kd, p, slot), from) : 0.0));   // 0.4.31: the stock part only"),
])

# ---------------------------------------------------------------------------------------------------- 6. ShStore: mzFold generalised (seeds, Eternal seeds, the island's XP), migrate6
P.rep('''F(st, 'public static final String[] MZ_KEEP = new String[] { "size", "amt", "deco", "irr", "nsize", "luck", "smithy", "alloyPct", "totems", "stored", "legacy", "drops", "seed", "ench", "ores" };')''',
      '''F(st, 'public static final String[] MZ_KEEP = new String[] { "size", "amt", "deco", "irr", "nsize", "luck", "smithy", "alloyPct", "totems", "stored", "legacy", "drops", "seed", "ench", "ores", "eternal" };')   # 0.4.31: + a farm's Eternal seeds''')
region('''public static String mzFold(int kd, java.util.Properties p, int o, int b, StringBuilder ch) {''', '''st.getDeclaredMethod("migrate5").setBody(''', [
    ('''  int to = @PKG@.ShIsl.ty(kd, p, o);
  int tb = @PKG@.ShIsl.ty(kd, p, b);
''', '''  int to = @PKG@.ShIsl.ty(kd, p, o);
  int tb = @PKG@.ShIsl.ty(kd, p, b);
  if (to < 0 || tb < 0) return "an island of no known type (slot " + o + " / " + b + ")";   // 0.4.31
  if (@PKG@.ShIsl.seeds(kd, p, o) > 0L && @PKG@.ShIsl.SEED[to].length() == 0) return "a seed store with no seed item (" + pre + "seed)";   // 0.4.31: never dropped
  if (@PKG@.ShIsl.eternal(kd, p, o) > 0 && @PKG@.ShIsl.ESEED[to].length() == 0) return "Eternal seeds with no Eternal seed item (" + pre + "eternal)";
  double xi = @PKG@.ShMath.xpAvg(kd, p, o, @PKG@.ShCore.now());   // 0.4.31: what Collect pays a stocked item there (Mining = xpOf; a farm's tracked XP)
  double xd = 0.0;
'''),
    ('''    mzPut(m, sm ? @PKG@.ShIsl.SMELT[to] : @PKG@.ShIsl.PROD[to], st0);
    moved += st0; xu += st0;''', '''    mzPut(m, sm ? @PKG@.ShIsl.SMELT[to] : @PKG@.ShIsl.PROD[to], st0);
    moved += st0; xu += st0; xd += (double) st0 * xi;'''),
    ('''      if (lb2 != null) { mzPut(m, lb2, ln * 100L); moved += ln * 100L; xu += ln * 100L; } else { mzPut(m, lid, ln); moved += ln; xu += ln; }''',
     '''      if (lb2 != null) { mzPut(m, lb2, ln * 100L); moved += ln * 100L; xu += ln * 100L; xd += (double) (ln * 100L) * (xi > 0.0 ? xi : (double) @PKG@.ShCfg.xpOf(kd)); } else { mzPut(m, lid, ln); moved += ln; xu += ln; xd += (double) ln * (double) @PKG@.ShCfg.xpOf(kd); }   // 0.4.31: Collect's XP a legacy item'''),
    ('''  if (sd > 0L && sid != null && sid.length() > 0) { mzPut(m, sid, sd); moved += sd; }
''', '''  if (sd > 0L && sid != null && sid.length() > 0) { mzPut(m, sid, sd); moved += sd; }
  long et = (long) @PKG@.ShIsl.eternal(kd, p, o);   // 0.4.31: the Eternal seeds a farm island was given come back as items
  String eid = @PKG@.ShIsl.ESEED[to];
  if (et > 0L && eid != null && eid.length() > 0) { mzPut(m, eid, et); moved += et; }
'''),
    ('''  long xo = @PKG@.ShMath.oweXp(kd, p, b, xu);''', '''  long xo = @PKG@.ShMath.oweXpD(kd, p, b, xd);   // 0.4.31: = oweXp(xu) for Mining (xpOf a unit)'''),
    ('''.append(" quarry (slot ").append(b)''', '''.append(" ").append(@PKG@.ShIsl.ZW[kd]).append(" (slot ").append(b)'''),
    ('''  if (dup) ch.append(" (").append(@PKG@.ShIsl.NAME[to]).append(" was already on its Ores row - bought again under 0.4.29; nothing refunded)");''',
     '''  if (dup) ch.append(" (").append(@PKG@.ShIsl.NAME[to]).append(" was already on its ").append(@PKG@.ShIsl.ROWN[kd]).append(" row - bought again under ").append(@PKG@.ShIsl.mineKd(kd) ? "0.4.29" : "0.4.30").append("; nothing refunded)");'''),
])
_SNAP = cut('''M(st, r"""
public static String snapZone(String k) {''', '''F(st, "public static volatile boolean MZ_FAIL_TEST = false;")''')
_SNAP6 = _SNAP.replace("snapZone(String k) {   // 0.4.30: = snapClk, the .pre-0.4.30 copy", "snapAz(String k) {   // 0.4.31: = snapZone, the .pre-0.4.31 copy") \
              .replace("0.4.30", "0.4.31").replace("Mining zone migration", "zone island migration").replace('"mzsnap', '"azsnap')
assert _SNAP6.count("0.4.31") >= 4 and "snapAz" in _SNAP6 and "azsnapx:" in _SNAP6, _SNAP6[:300]
P.rep('''st.getDeclaredMethod("migrate5").setBody(jv(r"""{''', _SNAP6 + '''F(st, "public static volatile boolean AZ_FAIL_TEST = false;")   # 0.4.31 harness: the totals check fails (nothing may change)
F(st, "public static volatile boolean AZ_THROW_TEST = false;")   # 0.4.31 fixer 2 harness: an exception mid-fold (nothing may change)
F(st, "public static volatile boolean MZ_THROW_TEST = false;")   # 0.4.31 fixer 2 harness: the same for migrate5
F(st, "public static final int[] AZ_KINDS = new int[] { %d, %d, %d, %d };" % (CK_FK, FQ_K, RQ_K, OQ_K))   # 0.4.31: Foraging, Farming, Ranching, Orchard (Mining = migrate5)
# 0.4.31: the units the zone island check counts = mzUnits + every island's seed store + Eternal seeds as those items (a fold gives them back as items)
M(st, r"""
public static java.util.HashMap azUnits(int kd, java.util.Properties p) {
  java.util.HashMap u = mzUnits(kd, p);
  for (int s = 0; s < @PKG@.ShMath.SLOTS; s++) {
    if (!@PKG@.ShMath.hasIsland(kd, p, s)) continue;
    int t = @PKG@.ShIsl.ty(kd, p, s);
    if (t < 0) continue;
    long sd = @PKG@.ShIsl.seeds(kd, p, s);
    if (sd > 0L && @PKG@.ShIsl.SEED[t].length() > 0) mzPut(u, @PKG@.ShIsl.SEED[t], sd);
    long e = (long) @PKG@.ShIsl.eternal(kd, p, s);
    if (e > 0L && @PKG@.ShIsl.ESEED[t].length() > 0) mzPut(u, @PKG@.ShIsl.ESEED[t], e);
  }
  return u;
}""")
M(st, r"""
public static int azFolds(int kd, java.util.Properties p) {
  int nf = 0;
  for (int s = 0; s < @PKG@.ShMath.SLOTS; s++) {
    if (!@PKG@.ShMath.hasIsland(kd, p, s)) continue;
    int t = @PKG@.ShIsl.ty(kd, p, s);
    if (t >= 0 && @PKG@.ShIsl.zoneSlot(kd, p, @PKG@.ShIsl.zoneOf(t)) != s) nf++;
  }
  return nf;
}""")
# ================= 0.4.31 ShStore.migrate6 = THE ZONE ISLAND MIGRATION (tools/shards_0_4_31_patch.py; PROJECT-RULES 4): once per profile file, marker azone.done=1.
# Foraging, Farming, Ranching, Orchard: each zone's 2nd / 3rd island folds into the zone island (its lowest-tier island) with mzFold (the mzone1 rules + the seed
# stores and Eternal seeds as items). Checked per kind before = after; History copy .pre-0.4.31 first; ONE save; ONE collect.log journal line.
st.getDeclaredMethod("migrate6").setBody(jv(r"""{
  String k = $1;
  java.util.Properties p = $2;
  if (p == null || k == null) return;   // NOT skipped on azone.done - an island bought again under a 0.4.30 rollback folds too
  LOCK.lock();
  try {
    int nk = AZ_KINDS.length;
    int[] nf = new int[nk];
    int nt = 0;
    for (int j = 0; j < nk; j++) { nf[j] = azFolds(AZ_KINDS[j], p); nt += nf[j]; }
    if (nt == 0) { AZCHK.incrementAndGet(); return; }   // one island a zone at most: nothing to do, nothing written
    java.util.Properties old = new java.util.Properties();
    old.putAll(p);
    boolean saved = false;
    try {   // fixer 2 (azone1): an exception mid-fold restores the copy - the cache never keeps a half fold
    long now = @PKG@.ShCore.now();
    java.util.HashMap[] g0 = new java.util.HashMap[nk];
    int[] i0 = new int[nk]; int[] t0 = new int[nk]; String[] o0 = new String[nk];
    for (int j = 0; j < nk; j++) {
      if (nf[j] == 0) continue;
      int kd = AZ_KINDS[j];
      @PKG@.ShMath.settleAll(kd, p, now);   // production up to now at the old numbers
      g0[j] = azUnits(kd, p); i0[j] = mzIsl(kd, p); t0[j] = mzTot(kd, p); o0[j] = mzOwn(kd, p);
    }
    StringBuilder ch = new StringBuilder();
    String bad = null;
    for (int j = 0; j < nk && bad == null; j++) {
      if (nf[j] == 0) continue;
      int kd = AZ_KINDS[j];
      ch.append("; ").append(@PKG@.ShKind.NAMES[kd]);
      for (int z = 1; z <= 5 && bad == null; z++) {
        int b = @PKG@.ShIsl.zoneSlot(kd, p, z);
        if (b < 0) continue;
        for (int s = 0; s < @PKG@.ShMath.SLOTS && bad == null; s++) {
          if (s == b || !@PKG@.ShMath.hasIsland(kd, p, s) || @PKG@.ShIsl.zoneOf(@PKG@.ShIsl.ty(kd, p, s)) != z) continue;
          bad = mzFold(kd, p, s, b, ch);
        }
      }
    }
    if (AZ_THROW_TEST) throw new IllegalStateException("AZ_THROW_TEST");   // fixer 2 harness: after the folds, before the checks
    for (int j = 0; j < nk && bad == null; j++) {
      if (nf[j] == 0) continue;
      int kd = AZ_KINDS[j];
      String kn = @PKG@.ShKind.NAMES[kd];
      java.util.HashMap g1 = azUnits(kd, p);
      if (AZ_FAIL_TEST || !g0[j].equals(g1)) bad = kn + ": the items do not add up (" + g0[j] + " -> " + g1 + ")";
      else if (mzTot(kd, p) != t0[j]) bad = kn + ": the totems do not add up (" + t0[j] + " -> " + mzTot(kd, p) + ")";
      else if (!o0[j].equals(mzOwn(kd, p))) bad = kn + ": the types owned changed (" + o0[j] + " -> " + mzOwn(kd, p) + ")";
      else if (mzIsl(kd, p) != i0[j] - nf[j]) bad = kn + ": the island count is off (" + i0[j] + " - " + nf[j] + " -> " + mzIsl(kd, p) + ")";
    }
    if (bad != null) {
      p.clear(); p.putAll(old);
      AZWAIT.incrementAndGet();
      @PKG@.ShCfg.warnOnce("azbad:" + k, "the 0.4.31 zone island migration of " + k + " is waiting - nothing changed: " + bad);
      return;
    }
    String snap = snapAz(k);
    if (snap == null) { p.clear(); p.putAll(old); AZWAIT.incrementAndGet(); return; }
    p.setProperty("azone.done", "1");
    String err = save(k, p);
    if (err != null) { p.clear(); p.putAll(old); AZWAIT.incrementAndGet(); @PKG@.ShCfg.warnOnce("azsave:" + k, "the 0.4.31 zone island migration of " + k + " is waiting (the file could not be saved: " + err + ")"); return; }
    saved = true;
    AZMIG.incrementAndGet();
    log("zone island migration (SkyyShards @VERSION@) " + k + ": one island a zone" + ch.toString() + " (" + nt + " island(s) folded; every totem, every item, seed and Eternal seed and every owned type kept) - History copy " + snap + " (the last save before the fold) - Undo: stop the server, copy it back over shards/" + k + ".properties and put SkyyShards 0.4.30 back");
    @PKG@.ShCfg.info("0.4.31 zone island migration: " + k + " - " + nt + " island(s) folded into their zone island" + ch.toString() + " (collect.log has the Undo)");
    } catch (Throwable x) {
      if (!saved) { p.clear(); p.putAll(old); AZWAIT.incrementAndGet(); }   // not saved yet: nothing changed (tried again at the next load)
      @PKG@.ShCfg.warnOnce("azx:" + k, "the 0.4.31 zone island migration of " + k + (saved ? " was saved, its log line failed: " : " is waiting - nothing changed (an error: ") + x + ")");
    }
  } finally { LOCK.unlock(); }
}"""))
st.getDeclaredMethod("migrate5").setBody(jv(r"""{''')

# ---------------------------------------------------------------------------------------------------- 7. the page: the four fills (zone island, 7 rows), zonePost, the clicks
for _fill, _end in (("public void fillRanch(", "M(page, r\"\"\"\npublic void fillOrch("), ("public void fillOrch(", "M(page, r\"\"\"\npublic void fillFarm("),
                    ("public void fillFarm(", "M(page, r\"\"\"\npublic boolean farmFresh("), ("public void fillClick(", "M(page, r\"\"\"\npublic void buildClick(")):
    _fix = [('this.ckUpE[1] = "Fruit trees: " + this.ckTn + (sz < 3 ? " - grow the island for more" : " (highest)");',
             'this.ckUpE[1] = "Fruit trees: " + this.ckTn + (sz < 3 ? " - grow for more" : " (highest)");   // 0.4.31: fits the row (was 41 characters)')] \
        if _fill == "public void fillOrch(" else []
    region(_fill, _end, _fix + [
        ("  this.ckUpL = new String[6]; this.ckUpE = new String[6]; this.ckUpC = new String[6]; this.ckUpOk = new boolean[6]; this.ckUpSeen = new int[6];\n"
         "  for (int i = 0; i < 6; i++) {",
         "  this.ckUpL = new String[7]; this.ckUpE = new String[7]; this.ckUpC = new String[7]; this.ckUpOk = new boolean[7]; this.ckUpSeen = new int[7];   // 0.4.31: + row 6 (the zone's types)\n"
         "  for (int i = 0; i < 7; i++) {"),
        ("    if (this.ckSlot < 0 || this.ckSlot >= @PKG@.ShMath.SLOTS || !@PKG@.ShMath.hasIsland(kd, p, this.ckSlot)) {\n",
         "    if (this.ckSlot >= 0 && this.ckSlot < @PKG@.ShMath.SLOTS && @PKG@.ShMath.hasIsland(kd, p, this.ckSlot)) { int zb = @PKG@.ShIsl.zoneSlot(kd, p, @PKG@.ShIsl.zoneOf(@PKG@.ShIsl.ty(kd, p, this.ckSlot))); if (zb >= 0) this.ckSlot = zb; }   // 0.4.31: the zone's island\n"
         "    if (this.ckSlot < 0 || this.ckSlot >= @PKG@.ShMath.SLOTS || !@PKG@.ShMath.hasIsland(kd, p, this.ckSlot)) {\n"),
    ])
P.rep('''M(page, r"""
public void buildClick(@UCB@ b, @UEB@ ev) {''', r'''# 0.4.31 (tools/shards_0_4_31_patch.py) AFTER A ZONED FILL (Foraging / Farming / Ranching / Orchard; Mining's own fill does this itself): the spots' pictures
# per type, the 7th row (the zone's next type at its 0.4.30 island price), the map = one card a zone. Bridges before the store lock.
M(page, r"""
public void zonePost(String k) {
  int kd = this.kind;
  if (kd == @PKG@.ShClk.MK || !@PKG@.ShIsl.zoned(kd) || this.ckUpL == null || this.ckUpL.length < 7) return;
  java.util.Properties p = k == null ? null : @PKG@.ShStore.get(k);
  if (p == null) return;
  int LN = @PKG@.ShIsl.LADN[kd];
  int L0 = @PKG@.ShIsl.LAD0[kd];
  int lv = this.ckLv;
  double[] tcv = new double[LN];
  for (int i = 0; i < LN; i++) tcv[i] = @PKG@.ShCfg.curve(@PKG@.ShIsl.band(@PKG@.ShIsl.TIER[L0 + i]));   // the bridges before the store lock
  long now = @PKG@.ShCore.now();
  int[] own = new int[LN];
  int[] zq = new int[] { -1, -1, -1, -1, -1 };
  int[] tys = new int[0];
  int t = -1; int z = 0; double rate = 0.0;
  @PKG@.ShStore.LOCK.lock(); try {
    for (int i = 0; i < LN; i++) own[i] = @PKG@.ShIsl.owns(kd, p, L0 + i) ? 1 : -1;
    for (int zz = 0; zz < 5; zz++) zq[zz] = @PKG@.ShIsl.zoneSlot(kd, p, zz + 1);
    int s = this.ckSlot;
    if (this.ckT >= 0 && s >= 0 && s < @PKG@.ShMath.SLOTS && @PKG@.ShMath.hasIsland(kd, p, s) && @PKG@.ShIsl.ty(kd, p, s) == this.ckT) {
      t = this.ckT; z = @PKG@.ShIsl.zoneOf(t); tys = @PKG@.ShClk.zoneOwnedK(kd, p, z);
      rate = @PKG@.ShMath.rate(kd, p, s, now);
    }
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  String zw = @PKG@.ShIsl.ZW[kd]; String tw = @PKG@.ShIsl.TW[kd]; String tws = @PKG@.ShIsl.TWS[kd];
  if (t >= 0 && tys.length > 0) {
    StringBuilder on = new StringBuilder();
    for (int i = 0; i < tys.length; i++) { if (i > 0) on.append(", "); on.append(@PKG@.ShIsl.NAME[tys[i]]); }
    if (tys.length > 1) {   // spot i = type i mod n (= ShClk.harvest / gather / chop)
      this.ckTexA = new String[@PKG@.ShClk.NSPOT]; this.ckTexB = new String[@PKG@.ShClk.NSPOT];
      for (int i = 0; i < this.ckTn && i < @PKG@.ShClk.NSPOT; i++) {
        int ty = tys[i % tys.length];
        int ci = ty - L0;
        if (ci < 0) ci = 0;
        if (kd == @PKG@.ShClk.RNK) { if (ci >= R_ANI.length) ci = R_ANI.length - 1; this.ckTexA[i] = R_ANI[ci]; this.ckTexB[i] = R_REST[ci]; }
        else if (kd == @PKG@.ShClk.ORK) { if (ci >= O_TREE.length) ci = O_TREE.length - 1; this.ckTexA[i] = O_TREE[ci]; this.ckTexB[i] = O_PICK[ci]; }
        else if (kd == @PKG@.ShClk.CRK) { if (ci >= F_CROP.length) ci = F_CROP.length - 1; this.ckTexA[i] = F_CROP[ci]; this.ckTexB[i] = F_HARV; }
        else { int tr = @PKG@.ShIsl.TIER[ty]; int ti = tr < 1 ? 0 : (tr > CK_TREE.length ? CK_TREE.length - 1 : tr - 1); this.ckTexA[i] = CK_TREE[ti]; this.ckTexB[i] = CK_STUMP[ti]; }
      }
      this.ckChip = "Zone " + z + " " + @PKG@.ShIsl.ZWC[kd] + " - " + ckSize(this.ckSz);
      this.ckSto[0] = @PKG@.ShIsl.TWSC[kd] + ": " + on.toString();
      this.ckSto[1] = "Rate: " + @PKG@.ShCfg.dec(rate) + " " + @PKG@.ShIsl.SHW[kd] + " a minute, shared";
    }
    // 6 the zone's types: the next one joins this island at the price its own island had (tier order, the zone lock)
    int zn8 = 0; int zh8 = 0; int nx8 = -1;
    for (int i = 0; i < LN; i++) {
      if (@PKG@.ShIsl.zoneOf(L0 + i) != z) continue;
      zn8++;
      if (own[i] >= 0) zh8++;
      else if (nx8 < 0) nx8 = i;
    }
    this.ckUpL[6] = zh8 + " / " + zn8 + " " + tws; this.ckUpSeen[6] = nx8;
    if (nx8 < 0) { this.ckUpE[6] = @PKG@.ShIsl.TWSC[kd] + ": " + on.toString(); ckTextR(6, "Every " + tw + " of Zone " + z + " is on this island."); }
    else {
      int t8 = L0 + nx8;
      int nd8 = @PKG@.ShIsl.zoneNeed(kd, t8);
      this.ckUpE[6] = "Add " + @PKG@.ShIsl.NAME[t8] + ": more " + @PKG@.ShIsl.SPW[kd];
      if (nd8 > 0 && lv != -1 && lv < nd8) ckTextR(6, "Needs " + @PKG@.ShIsl.skillWord(kd) + " " + nd8 + (lv >= 0 ? " (you: " + lv + ")." : "."));
      else if (this.ckNext >= 0 && this.ckNext != nx8) ckTextR(6, "Add " + @PKG@.ShIsl.NAME[L0 + this.ckNext] + " first - " + tws + " and islands come in tier order.");
      else { ckCostR(6, @PKG@.ShIsl.coins(@PKG@.ShCfg.BUY_H, tcv[nx8]), @PKG@.ShIsl.mats(kd, t8, @PKG@.ShCfg.BUY_ITEMS[kd], 0, 1L)); this.ckUpOk[6] = this.mine; }
    }
  }
  // the map: ONE card a zone (card 3 x zone = the zone's first type: 3 tiers a zone); its other types are upgrades inside it
  for (int zz = 0; zz < 5; zz++) {
    int c = 3 * zz;
    for (int q = 0; q < 3 && c + q < 15; q++) { this.ckMN[c + q] = ""; this.ckMS[c + q] = ""; this.ckMB[c + q] = 0; this.ckMLock[c + q] = false; this.ckMCur[c + q] = false; }
    if (c >= LN) continue;   // no types in this zone (Ranching / Orchard Zones 4-5: the zone line says so)
    int tt = L0 + c;
    int need = @PKG@.ShIsl.zoneNeed(kd, tt);
    boolean open = need <= 0 || lv == -1 || lv >= need;
    StringBuilder all = new StringBuilder();
    int zn = 0; int zh = 0; String add = "";
    for (int i = 0; i < LN; i++) {
      if (@PKG@.ShIsl.zoneOf(L0 + i) != zz + 1) continue;
      zn++;
      if (all.length() > 0) all.append(" + ");
      all.append(@PKG@.ShIsl.NAME[L0 + i]);
      if (own[i] >= 0) zh++;
      else if (add.length() == 0) add = @PKG@.ShIsl.NAME[L0 + i];
    }
    String nm = all.toString();
    this.ckMN[c] = nm.length() <= 24 ? nm : @PKG@.ShIsl.NAME[tt] + " + " + (zn - 1) + " more " + tws;
    boolean have = zq[zz] >= 0;
    this.ckMCur[c] = have && t >= 0 && z == zz + 1;
    this.ckMLock[c] = !open && !have;
    if (have) { this.ckMS[c] = (this.ckMCur[c] ? "Shown now" : "Yours") + " - " + zh + " / " + zn + " " + tws + (add.length() > 0 ? "; add " + add + " inside" : ""); this.ckMB[c] = 1; }
    else if (!open) this.ckMS[c] = "Locked: " + @PKG@.ShIsl.skillWord(kd) + " " + need;
    else if (c == this.ckNext) {
      this.ckMS[c] = "Buy: " + ckCost(@PKG@.ShIsl.coins(@PKG@.ShCfg.BUY_H, tcv[c]), @PKG@.ShIsl.mats(kd, tt, @PKG@.ShCfg.BUY_ITEMS[kd], 0, 1L));
      this.ckMB[c] = this.mine ? 2 : 0;
    }
    else if (this.ckNext >= 0) {
      int tq = L0 + this.ckNext;
      int zq2 = @PKG@.ShIsl.zoneOf(tq);
      this.ckMS[c] = "First add " + @PKG@.ShIsl.NAME[tq] + (zq2 >= 1 && zq2 <= 5 && zq[zq2 - 1] >= 0 ? " in the Zone " + zq2 + " " + zw : " (Zone " + zq2 + ")");
    }
    else this.ckMS[c] = "Buy the islands before it first";
  }
}""")
M(page, r"""
public void buildClick(@UCB@ b, @UEB@ ev) {''')
P.rep('''    else fillClick(k, cs, ref, st);   // 0.4.23
    ckPost(k, cs);''', '''    else fillClick(k, cs, ref, st);   // 0.4.23
    zonePost(k);   // 0.4.31: a zoned island's types, its 7th row, the map = one card a zone
    ckPost(k, cs);''')
P.rep('''  String nm = shN > 1 ? "ore" : @PKG@.ShTotem.pretty(@PKG@.ShIsl.PROD[this.ckT]);   // 0.4.30 fixer: shared over the quarry's ores''',
      '''  String nm = shN > 1 ? @PKG@.ShIsl.SHW[kd] : @PKG@.ShTotem.pretty(@PKG@.ShIsl.PROD[this.ckT]);   // 0.4.30 fixer: shared over the quarry's ores; 0.4.31: any zone island''')
region('''public String actClick(String a, @REF@ ref, @ST@ st) {''', '''M(page, r"""
public void build0(''', [
    ("    @PKG@.ShStore.LOCK.lock(); try { s = @PKG@.ShIsl.slotOf(kd, p, @PKG@.ShIsl.LAD0[kd] + i); } finally { @PKG@.ShStore.LOCK.unlock(); }\n    if (s < 0) return \"-That island is not yours yet.\";",
     "    @PKG@.ShStore.LOCK.lock(); try { s = @PKG@.ShIsl.zoned(kd) ? @PKG@.ShIsl.zoneSlot(kd, p, @PKG@.ShIsl.zoneOf(@PKG@.ShIsl.LAD0[kd] + i)) : @PKG@.ShIsl.slotOf(kd, p, @PKG@.ShIsl.LAD0[kd] + i); } finally { @PKG@.ShStore.LOCK.unlock(); }   // 0.4.31: the zone's island\n    if (s < 0) return \"-That island is not yours yet.\";"),
    ("    if (row < 0 || row > 5) return \"\";", "    if (row < 0 || row > 6 || (row == 6 && !@PKG@.ShIsl.zoned(kd))) return \"\";   // 0.4.31: + row 6 (the zone's types)"),
    ("    if (row == 2) return @PKG@.ShCore.buySpirit(u, k, kd, s, seen, cs);   // 0.4.27: the spirit row buys / tiers up here\n",
     "    if (row == 6) return @PKG@.ShClk.buyOre(u, k, kd, s, seen, cs);   // 0.4.31: the zone's next type (the page's type rank)\n"
     "    if (row == 2) return @PKG@.ShCore.buySpirit(u, k, kd, s, seen, cs);   // 0.4.27: the spirit row buys / tiers up here\n"),
])

# ---------------------------------------------------------------------------------------------------- 8. the markup: the 7th row, the maps = one card a zone
P.rep('''NUP_KINDS = {"F": (CK_UP_NAMES[:2] + ["Spirit totem"] + CK_UP_NAMES[3:], CK_UP_ICON),''',
      '''NUP_KINDS = {"F": (CK_UP_NAMES[:2] + ["Spirit totem"] + CK_UP_NAMES[3:] + ["Trees"], CK_UP_ICON + ["UpNcount"]),   # 0.4.31: + the zone's trees''')
P.rep('''             "Fm": (FQ_UP_NAMES[:2] + ["Spirit totem"] + FQ_UP_NAMES[3:], FQ_UP_ICON),''',
      '''             "Fm": (FQ_UP_NAMES[:2] + ["Spirit totem"] + FQ_UP_NAMES[3:] + ["Crops"], FQ_UP_ICON + ["UpFCount"]),   # 0.4.31: + the zone's crops''')
P.rep('''             "R": (RQ_UP_NAMES, RQ_UP_ICON), "O": (OQ_UP_NAMES, OQ_UP_ICON)}   # 0.4.28: the ranch + the orchard''',
      '''             "R": (RQ_UP_NAMES + ["Animals"], RQ_UP_ICON + ["UpFCount"]), "O": (OQ_UP_NAMES + ["Fruits"], OQ_UP_ICON + ["UpNcount"])}   # 0.4.28: the ranch + the orchard; 0.4.31: + the zone's types
AZ_BTN = {"F": "Add tree", "Fm": "Add crop", "R": "Add animal", "O": "Add fruit"}   # 0.4.31: row 6's button''')
P.rep('''(["Add ore"] if (_K == "Q" and _r == 8) else ["Upgrade"]))   # 0.4.30''', '''(["Add ore"] if (_K == "Q" and _r == 8) else ([AZ_BTN[_K]] if (_K in AZ_BTN and _r == 6) else ["Upgrade"])))   # 0.4.30; 0.4.31''')
region('''# ---- mode 1: the island map - five zone clusters of three woods''', '''assert 30 + 24 + 3 * (CK_CARD_H + 6) <= CK_BODY_H - 20, "the three cards fit a zone panel"''', [
    ('''    Z_ = CKP + "Z%d" % _z
''', '''    Z_ = CKP + "Z%d" % _z
    a_ = CKA["map"]
'''),
    ('''        M_ = CKP + "M%d" % _i
''', '''        M_ = CKP + "M%d" % _i
        a_ = CKA["map"] if _q == 0 else SUI.Appends()   # 0.4.31: one card a zone (the zone island); cards 2 / 3 keep their segments, no markup
'''),
    ('''        b_.append(("#" + M_ + "G", SUI.map_pic(M_ + "Lk", (CK_CW - 12 - 40) // 2, 40, 40, 48, CK_TEX["Lock"])))
        a_ = CKA["map"]
''', '''        b_.append(("#" + M_ + "G", SUI.map_pic(M_ + "Lk", (CK_CW - 12 - 40) // 2, 40, 40, 48, CK_TEX["Lock"])))
        a_ = CKA["map"] if _q == 0 else SUI.Appends()
'''),
    ('''        b_.append(("#" + M_ + "B", G_.glass_button(M_ + "X", "Buy", "secondary", w=CK_CW - 12, h=30)))
        a_ = CKA["map"]
''', '''        b_.append(("#" + M_ + "B", G_.glass_button(M_ + "X", "Buy", "secondary", w=CK_CW - 12, h=30)))
        a_ = CKA["map"] if _q == 0 else SUI.Appends()
'''),
])
region('''a_ = _ck_seg("fmap")''', '''# ---- 0.4.26 THE TOWN PAGE PARTS''', [
    ("    for _q in range(3):\n", "    for _q in range(1):   # 0.4.31: one card a zone (the zone farm)\n"),
])
region('''RO_MAPS = {"rmap": (RQ_K, "PENS", "RAni%d"), "omap": (OQ_K, "ORCHARDS", "OTree%d")}''', '''# the run-time templates (checked with samples)''', [
    ("        for _q in range(3):\n", "        for _q in range(1):   # 0.4.31: one card a zone (the zone island)\n"),
    ("    for _i in range(_ln):\n", "    for _i in range(0, _ln, 3):   # 0.4.31: the zone cards\n"),
])
P.rep('''for _i in range(15):
    _ck_j += ["  if (this.ckMLock[%d]) {" % _i, _ckj("mlock%d" % _i), "  }",''', '''for _i in range(0, 15, 3):   # 0.4.31: the Foraging / Farming maps = one card a zone
    _ck_j += ["  if (this.ckMLock[%d]) {" % _i, _ckj("mlock%d" % _i), "  }",''')
P.rep('''for _n in ["frame", "mapb1", "frame2", "map"] + ["mlock%d" % _i for _i in range(15)] + ["mbuy%d" % _i for _i in range(15)] + ["foot"]:''',
      '''for _n in ["frame", "mapb1", "frame2", "map"] + ["mlock%d" % _i for _i in range(0, 15, 3)] + ["mbuy%d" % _i for _i in range(0, 15, 3)] + ["foot"]:   # 0.4.31: the zone cards''')
P.rep('''for _n in ["frame", "mapb1", "frame2", "fmap"] + ["mlock%d" % _i for _i in range(15)] + ["mbuy%d" % _i for _i in range(15)] + ["foot"]:''',
      '''for _n in ["frame", "mapb1", "frame2", "fmap"] + ["mlock%d" % _i for _i in range(0, 15, 3)] + ["mbuy%d" % _i for _i in range(0, 15, 3)] + ["foot"]:   # 0.4.31''')
P.rep('''for _n in ["frame", "mapb1", "frame2", "fmap"] + ["mopen%d" % _i for _i in range(15)] + ["foot"]:''',
      '''for _n in ["frame", "mapb1", "frame2", "fmap"] + ["mopen%d" % _i for _i in range(0, 15, 3)] + ["foot"]:   # 0.4.31''')
P.rep('''        _names = ["frame", "mapb1", "frame2", _seg] + (["mlock%d" % _i for _i in range(len(LAD[_kd]))] + ["mbuy%d" % _i for _i in range(len(LAD[_kd]))]
                                                         if _mode == "lb" else ["mopen%d" % _i for _i in range(len(LAD[_kd]))]) + ["foot"]''',
      '''        _names = ["frame", "mapb1", "frame2", _seg] + (["mlock%d" % _i for _i in range(0, len(LAD[_kd]), 3)] + ["mbuy%d" % _i for _i in range(0, len(LAD[_kd]), 3)]
                                                         if _mode == "lb" else ["mopen%d" % _i for _i in range(0, len(LAD[_kd]), 3)]) + ["foot"]   # 0.4.31: the zone cards''')

# fixer 2 (azone1): migrate5 (0.4.30 Mining fold) gets the same exception guard as migrate6 - a throw mid-fold restores the copy (never a half fold in the cache)
P.rep('''    if (nf == 0) { MZCHK.incrementAndGet(); return; }   // one island a zone at most: nothing to do, nothing written
    java.util.Properties old = new java.util.Properties();
    old.putAll(p);
''', '''    if (nf == 0) { MZCHK.incrementAndGet(); return; }   // one island a zone at most: nothing to do, nothing written
    java.util.Properties old = new java.util.Properties();
    old.putAll(p);
    boolean saved = false;
    try {   // 0.4.31 fixer 2: an exception mid-fold restores the copy
''')
P.rep('''    if (bad == null) {
      java.util.HashMap g1 = mzUnits(kd, p);''', '''    if (MZ_THROW_TEST) throw new IllegalStateException("MZ_THROW_TEST");   // 0.4.31 fixer 2 harness: after the folds, before the checks
    if (bad == null) {
      java.util.HashMap g1 = mzUnits(kd, p);''')
P.rep('''    if (err != null) { p.clear(); p.putAll(old); MZWAIT.incrementAndGet(); @PKG@.ShCfg.warnOnce("mzsave:" + k,''', '''    if (err == null) saved = true;   // 0.4.31 fixer 2
    if (err != null) { p.clear(); p.putAll(old); MZWAIT.incrementAndGet(); @PKG@.ShCfg.warnOnce("mzsave:" + k,''')
P.rep('''(collect.log has the Undo)");
  } finally { LOCK.unlock(); }
}"""))
M(ckc, "public static int luck(''', '''(collect.log has the Undo)");
    } catch (Throwable x) {   // 0.4.31 fixer 2
      if (!saved) { p.clear(); p.putAll(old); MZWAIT.incrementAndGet(); }
      @PKG@.ShCfg.warnOnce("mzx:" + k, "the 0.4.30 Mining zone migration of " + k + (saved ? " was saved, its log line failed: " : " is waiting - nothing changed (an error: ") + x + ")");
    }
  } finally { LOCK.unlock(); }
}"""))
M(ckc, "public static int luck(''')

# ---------------------------------------------------------------------------------------------------- 9. the ready line
P.rep(r'''log("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.30:''', r'''log("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.31: Foraging / Farming / Ranching / Orchard are one island a zone too (their other types are upgrades on the island's 7th row; migration azone.done); 0.4.30:''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0, "command / system registrations changed"
P.finish()
