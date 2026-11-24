"""Derive SkyyShards/build_skyyshards_0.4.30.py from the GENERATED SkyyShards 0.4.29 (build_skyyshards_0.4.29.py = the tools/deploy_set.py SET
pin, made by tools/shards_0_4_29_patch.py - edit the patch, never the generated file). Every anchor is asserted once; at the end every change
is undone on a copy and compared with 0.4.29 (tools/soundpass_gen.Patch). Line endings kept.
Run:   python tools/shards_0_4_30_patch.py   then   python SkyyShards/build_skyyshards_0.4.30.py   (never --deploy)
Check: python SkyyShards/test_skyyshards_0.4.30.py

0.4.30 (2026-11-22) = THE MINING QUARRY: ONE ISLAND PER ZONE (round mzone1; Skyy 2026-11-22 docs/answered/world.md "MINING SHARD ZONE ISLANDS", on a
  screenshot of the Mining islands map where the Iron card said "Shown now - in the Zone 1 quarry": "i cant go into my iron island. (lets do an island per
  zone, instead of per ore. so iron becomes an upgrade in the zone 1 island instead of its own island."; Skyy 2026-11-14 "MINING SHARD = QUARRY, ONE
  ISLAND PER ZONE": "the mine one is a big quarry that also has an island per zone instead of by ore. so the zone 1 island gives copper, iron with an
  upgrade"; Skyy 2026-11-22 "keep building").
  - SURVEY. Vanilla (Assets.zip): no quarry / clicker page (0.4.23-0.4.29 surveys); mods: nothing new (0.4.23's pie-clicker, learn only). Nothing packed.
  - 1. THE MAP = ONE CARD A ZONE. The quarry map (view 5, Islands) shows five cards, ZONE 1..5 QUARRY (Onyxium stays in Zone 5 as since 0.4.24). A card
    names the zone's ores ("Copper + Iron") and says Yours (n / m ores; "add Iron inside") / Locked: Mining N / Buy: <cost> / what to add first. BUY =
    the zone's FIRST ore's island (its 0.4.29 cost and zone lock: isl.buyHours + isl.buyItems, click.mine.zoneLevel); OPEN enters that zone's quarry -
    every owned zone, the one shown now included (the 0.4.29 card for a 2nd ore could not be entered: Skyy's bug).
  - 2. EVERY FURTHER ORE OF A ZONE IS AN UPGRADE of that zone's quarry: the quarry's new 9th row ORES ("n / m ores", the next ore, have / need cost
    lines, button "Add ore"). Cost = exactly what that ore's own island cost in 0.4.29 (isl.buyHours of the coin curve at the ore's tier + isl.buyItems
    "raw:128,..." of that ore = its bars - Skyy's "find the type first" exception, as a NEW island; no new number). Bought = the key mining.i<quarry>.ores
    (comma list of ore keys, e.g. "iron"); its nodes join the quarry exactly as an owned ore island's did (spot i mines ore i mod the zone's ores, its
    pictures, its tier gate) - ShIsl.owns(kd, p, t) = an island of type t OR an ore listed on that zone's quarry (ShIsl.zoneSlot = the zone's lowest-tier
    island). Tier order stays (ShIsl.nextTier counts ore upgrades as owned): Iron before the Zone 2 quarry, as islands came in tier order. A double
    click buys once (the button carries the ore the page showed; a bought ore says "mines Iron already"); a stale page (another quarry / profile:
    ShPage.ckFresh + the quarry check) buys nothing; not enough coins / items = refused, nothing paid (ShCore.purchaseM: pay outside the lock, commit
    while nothing was saved since, else refund). Buying a 2nd ore AS AN ISLAND is refused once the zone has a quarry (ShCore.buyIsland0).
    FIXER 2: the marker never skips the check - any 2nd Mining island of a zone found at a load (e.g. re-bought under a 0.4.29 rollback) folds the
    same way (a duplicate ore stays listed once; the journal says it was bought twice; a new timestamped History copy).
  - 3. ONE-TIME JOURNALED MIGRATION PER PROFILE (ShStore.migrate5, marker mzone.done=1; the 0.4.27 migrate3 / 0.4.28 migrate4 pattern): for each zone with
    more than one Mining island, the lowest-tier island stays (the zone QUARRY - an Iron island alone in Zone 1 becomes the quarry itself) and every
    other one FOLDS INTO IT: its ore -> the quarry's ores list; Island size = the larger one, and each of Ore Amount / Decorations / Springs keeps the
    HIGHER effective level (5 x (size - 1) + level - what the output bonus counts; e.g. a Medium 5/5/3 Copper + a Medium 1/2/0 Iron -> Medium 5/5/3);
    Vein size / Lucky finds / Smithy II = the higher; the alloy slider = the quarry's (else the folded one's); EVERY totem entry is appended (tiers,
    modifiers, boosters, uids kept; nothing is a "slot" in the clicker - modifier slots belong to each totem; the quarry's first worker stays its
    Spirit row, the folded island's spirit is listed "Also on this island (kept, still working)"; more poles than the size's pads = all keep working,
    "Place one" waits for room); its items move into the quarry's storage (.drops) in base units so Collect pays the same XP + collection credit:
    stored stock = that many of its ore (its bar when it smelted), an Enchanted legacy line = 100 of its base each, its own .drops, rare-find count
    (.ench) added, a seed store (none on Mining) as items. Then the folded island's keys go (geometry / clock keys of the retired walkable world too).
    Before anything: production settled; after: the totals are CHECKED (every item in base units = an Enchanted is 100, a bar its ore; totems; owned
    ores; islands = before - folded) - any difference, an unknown island key, a refused History copy or save = nothing changes (memory restored, a
    warning once, tried again at the next load). History copy shards/history/clicker/<pkey>.pre-0.4.30.properties first (byte-checked), ONE save with
    the marker, a collect.log journal line naming every fold + the Undo. A profile with at most one Mining island a zone has nothing to do: no marker,
    nothing written (checked at each load). Storage: the merged stock may be over the quarry's limit - nothing is lost; clicks / spirits pause until
    Collect (as with any full island).
  - 4. Other clickers unchanged (Foraging / Farming / Ranching / Orchard / Combat: ShIsl.owns = their island, nextTier as before).
  - FIXER (round mzone1 critics): 5. THE QUARRY'S SPIRITS MINE EVERY ORE ON IT IN TURN (critics: a folded Iron island's spirit made Copper = its Iron
    income lost; Skyy 2026-11-14 "the zone 1 island gives copper, iron with an upgrade"): ShMath.oreShare - what the quarry's totems make (the same count
    as before) is shared round-robin over the quarry's own ore + every ore on its Ores row (mining.i<n>.orr = whose turn is next): the quarry's own share
    stays its stock as before, every other ore's share goes into its storage (.drops) as that ore (its bar with an Auto-Smelt Pole), like a click's.
    A quarry with no ore upgrade makes exactly what it made in 0.4.29 (nothing written). The spirit row then says "ore a minute".
    6. NO XP LOST (found by the fixer): Collect pays NO XP for .drops (a click paid it already) - so the stock / Enchanted stock a fold moves into
    .drops, and a spirit's share of another ore, owe their Mining XP at once: ShMath.oweXp adds Collect's exact XP (shard.xpPercent included; the
    fraction carried in mining.i<n>.xpr) to the profile file's owed.xp.Mining, paid with the next mined node or Collect (the 0.4.13 owed-XP path).
  NUMBERS: none new (the ore upgrade = the 0.4.29 island price). Changed rows: none.
  SAVED DATA: mining.i<n>.ores (the quarry's ore upgrades; missing = none), mining.i<n>.orr (the spirits' next ore), mining.i<n>.xpr (an XP fraction,
    0-99 hundredths), mzone.done=1 (marker, only on a profile that was folded), owed.xp.Mining (the existing owed-XP key; it grows).
  ROLLBACK 0.4.30 -> 0.4.29 alone: the jar. 0.4.29 ignores mining.i<n>.ores / orr / xpr + mzone.done (kept in the file): EVERY ore owned through the Ores
    row - folded by the migration OR bought as an upgrade on 0.4.30 - is NOT owned there: its card shows "Buy" again (the full island price), the Zone
    quarry mines its base ore only, and tier order makes the player buy that ore again before the next zone. Everything merged stays on the quarry
    (storage items, totems, size, upgrades - Collect all pays the .drops); owed.xp.Mining is paid by 0.4.29 too. Do NOT re-buy an ore under 0.4.29
    (it would be paid twice; back on 0.4.30 that second island folds into the quarry at the next load - its items, totems and upgrades kept, the
    journal names it - but the second price is not refunded). Advice: make 0.4.30 the Shards rollback floor once a profile has bought an ore upgrade. Full Undo of the fold: stop the server, copy
    shards/history/clicker/<pkey>.pre-0.4.30.properties back over shards/<pkey>.properties (= the last save before the fold: production after that
    save and before the fold is not in it).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

HERE = os.path.join(ROOT, "SkyyShards")
P = G.Patch(os.path.join(HERE, "build_skyyshards_0.4.29.py"), os.path.join(HERE, "build_skyyshards_0.4.30.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.4.29"\n') and P.has("GENERATED by tools/shards_0_4_29_patch.py") and P.has("CK_SAPL") and not P.has("migrate5"), \
    "not the generated SkyyShards 0.4.29"
REG0, SYS0 = P.s.count("registerCommand("), P.s.count("registerSystem(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.4.30 (2026-11-22)"):].rstrip() + "\n"


def cut(a, b):
    """the text from anchor a (included) up to anchor b (excluded); both unique"""
    assert P.s.count(a) == 1 and P.s.count(b) >= 1, (a[:80], b[:80])
    i = P.s.index(a)
    j = P.s.index(b, i)
    return P.s[i:j]


# ---------------------------------------------------------------------------------------------------- 0. header + version
P.rep('''"""SkyyShards 0.4.29 - build script (javassist via jpype). GENERATED by tools/shards_0_4_29_patch.py from build_skyyshards_0.4.28.py
(generated by tools/shards_0_4_28_patch.py from 0.4.27, ... back to tools/shards_0_4_patch.py from 0.3.2; edit the patch, never this file).
Changes are marked "0.4.29" /''', '''"""SkyyShards 0.4.30 - build script (javassist via jpype). GENERATED by tools/shards_0_4_30_patch.py from build_skyyshards_0.4.29.py
(generated by tools/shards_0_4_29_patch.py from 0.4.28, ... back to tools/shards_0_4_patch.py from 0.3.2; edit the patch, never this file).
Changes are marked "0.4.30" / "0.4.29" /''')
P.rep('''Run:   python SkyyShards/build_skyyshards_0.4.29.py   -> SkyyShards/SkyyShards-0.4.29.jar   (never --deploy: tools/deploy_set.py installs the set)
Check: python SkyyShards/test_skyyshards_0.4.29.py
''', '''Run:   python SkyyShards/build_skyyshards_0.4.30.py   -> SkyyShards/SkyyShards-0.4.30.jar   (never --deploy: tools/deploy_set.py installs the set)
Check: python SkyyShards/test_skyyshards_0.4.30.py
''' + NOTE)
P.rep('VERSION = "0.4.29"\n', 'VERSION = "0.4.30"\n')

# ---------------------------------------------------------------------------------------------------- 1. ShStore: the migration's stub + its call in get()
P.rep('''M(st, "public static void migrate4(String k, java.util.Properties p) { }")   # 0.4.28: the body is set below (after ShMath) - the Ranching + Orchard clicker migration
''', '''M(st, "public static void migrate4(String k, java.util.Properties p) { }")   # 0.4.28: the body is set below (after ShMath) - the Ranching + Orchard clicker migration
M(st, "public static void migrate5(String k, java.util.Properties p) { }")   # 0.4.30: the body is set below (after ShClk) - the Mining zone migration
F(st, "public static final java.util.concurrent.atomic.AtomicLong MZMIG = new java.util.concurrent.atomic.AtomicLong();")   # 0.4.30: files folded
F(st, "public static final java.util.concurrent.atomic.AtomicLong MZCHK = new java.util.concurrent.atomic.AtomicLong();")   # 0.4.30: loads with nothing to fold
F(st, "public static final java.util.concurrent.atomic.AtomicLong MZWAIT = new java.util.concurrent.atomic.AtomicLong();")   # 0.4.30: folds refused (nothing changed)
''')
P.rep('''    migrate4(k, p);   // 0.4.28: the Ranching + Orchard clicker migration - History copy, journal, automated stores -> storage (marker clk2.done=1)
''', '''    migrate4(k, p);   // 0.4.28: the Ranching + Orchard clicker migration - History copy, journal, automated stores -> storage (marker clk2.done=1)
    migrate5(k, p);   // 0.4.30: the Mining zone migration - every 2nd ore island of a zone folds into the zone's quarry (marker mzone.done=1)
''')

# ---------------------------------------------------------------------------------------------------- 1b. ShMath.settle: a quarry's spirits share their output over its ores (fixer 5)
P.rep('''# settle one island at `now` (ms): returns the items made.''', '''M(mth, "public static long oreShare(int kd, java.util.Properties p, int slot, long made) { return 0L; }")   # 0.4.30 fixer: the body is set below (after ShClk) - a quarry's spirits share their output over its ores
# settle one island at `now` (ms): returns the items made.''')
P.rep('''    stored += made;
  }
  p.setProperty(ik(kd, slot, "last"), String.valueOf(last));''', '''    stored += made - oreShare(kd, p, slot, made);   // 0.4.30 fixer: a Mining quarry's other ores' share goes to its storage (.drops) as that ore
  }
  p.setProperty(ik(kd, slot, "last"), String.valueOf(last));''')

# ---------------------------------------------------------------------------------------------------- 2. ShIsl: owned = an island OR an ore upgrade of the zone's quarry
P.rep('''M(isl48, r"""
public static int nextTier(int kd, java.util.Properties p) {
  for (int i = 0; i < LADN[kd]; i++) if (slotOf(kd, p, LAD0[kd] + i) < 0) return i;
  return -1;
}""")''', '''# 0.4.30 (tools/shards_0_4_30_patch.py) ONE MINING ISLAND PER ZONE: a zone's quarry = its lowest-tier Mining island; its other ores are upgrades
# listed on it (mining.i<quarry>.ores = "iron,..."). owns = an island of that type, or (Mining) that ore on its zone's quarry. Under ShStore.LOCK.
M(isl48, "public static boolean mineKd(int kd) { return kd == @MQK@; }".replace("@MQK@", str(MQ_K)))
M(isl48, r"""
public static boolean oreListed(String s, String key) {
  if (s == null || key == null || s.length() == 0 || key.length() == 0) return false;
  String[] a = s.split(",");
  for (int i = 0; i < a.length; i++) if (a[i].trim().equals(key)) return true;
  return false;
}""")
M(isl48, r"""
public static int zoneSlot(int kd, java.util.Properties p, int z) {
  if (p == null) return -1;
  int best = -1; int bt = 0;
  for (int s = 0; s < @PKG@.ShMath.SLOTS; s++) {
    if (!@PKG@.ShMath.hasIsland(kd, p, s)) continue;
    int t = ty(kd, p, s);
    if (zoneOf(t) != z) continue;
    if (best < 0 || t < bt) { best = s; bt = t; }
  }
  return best;
}""")
M(isl48, r"""
public static boolean owns(int kd, java.util.Properties p, int t) {
  if (p == null || t < 0 || t >= TN) return false;
  if (slotOf(kd, p, t) >= 0) return true;
  if (!mineKd(kd)) return false;
  int s = zoneSlot(kd, p, zoneOf(t));
  return s >= 0 && oreListed(@PKG@.ShStore.str(p, ik(kd, s, "ores")), KEY[t]);
}""")
M(isl48, r"""
public static int nextTier(int kd, java.util.Properties p) {
  for (int i = 0; i < LADN[kd]; i++) if (!owns(kd, p, LAD0[kd] + i)) return i;   // 0.4.30: a Mining ore upgrade counts as owned
  return -1;
}""")''')

# ---------------------------------------------------------------------------------------------------- 3. ShCore.buyIsland0: owned via owns; no 2nd island in a quarry's zone
P.rep('''    if (@PKG@.ShIsl.slotOf(kd, p, t) >= 0) return "=You own the " + @PKG@.ShIsl.tname(t) + " island already.";
''', '''    if (@PKG@.ShIsl.owns(kd, p, t)) return "=You own the " + @PKG@.ShIsl.tname(t) + " island already.";   // 0.4.30: or that ore on its zone's quarry
    if (@PKG@.ShIsl.mineKd(kd) && @PKG@.ShIsl.zoneSlot(kd, p, @PKG@.ShIsl.zoneOf(t)) >= 0) return "-" + @PKG@.ShIsl.NAME[t] + " is an upgrade of your Zone " + @PKG@.ShIsl.zoneOf(t) + " quarry now - add it on the quarry's Ores row.";   // 0.4.30: one island a zone
''')

# ---------------------------------------------------------------------------------------------------- 4. ShClk: the zone's ores + quarry from owns / zoneSlot; the click checks
P.rep('''    if (@PKG@.ShIsl.zoneOf(t) != z || @PKG@.ShIsl.slotOf(MK, p, t) < 0) continue;''',
      '''    if (@PKG@.ShIsl.zoneOf(t) != z || !@PKG@.ShIsl.owns(MK, p, t)) continue;   // 0.4.30: an island or an ore upgrade''')
P.rep('''  int[] o = zoneOwned(p, z);
  return o.length == 0 ? -1 : @PKG@.ShIsl.slotOf(MK, p, o[0]);''',
      '''  return @PKG@.ShIsl.zoneSlot(MK, p, z);   // 0.4.30: the zone's lowest-tier island (= 0.4.24's while every ore was an island)''')
P.rep('''    if (ores.length == 0 || @PKG@.ShIsl.slotOf(kd, p, ores[0]) != slot) return res("=The page is up to date now.", "");''',
      '''    if (ores.length == 0 || baseSlot(p, z) != slot) return res("=The page is up to date now.", "");   // 0.4.30: the zone's quarry''')
P.rep('''    if (!@PKG@.ShMath.hasIsland(kd, p, slot) || @PKG@.ShIsl.slotOf(kd, p, ot) < 0 || @PKG@.ShIsl.slotOf(kd, p, ores[0]) != slot) { unfell(key, spot, hpMax); return res("-That quarry changed meanwhile - the page is up to date now.", ""); }''',
      '''    if (!@PKG@.ShMath.hasIsland(kd, p, slot) || !@PKG@.ShIsl.owns(kd, p, ot) || baseSlot(p, z) != slot) { unfell(key, spot, hpMax); return res("-That quarry changed meanwhile - the page is up to date now.", ""); }   // 0.4.30''')

# the ore upgrade purchase (after Lucky finds): the 0.4.29 island price of that ore, tier order, the zone lock, a stale quarry refused
P.rep('''M(ckc, r"""
public static long smithyCoins(double cv) { return @PKG@.ShIsl.coins(@PKG@.ShCfg.MQ_SM_H, cv); }""")''', '''# ---- 0.4.30 THE ORE UPGRADE (Skyy 2026-11-22 "iron becomes an upgrade in the zone 1 island instead of its own island"): the zone's next ore joins its
# quarry (mining.i<quarry>.ores) at the price its own island had (isl.buyHours at the ore's tier + isl.buyItems of that ore); li = the ore the page showed
M(ckc, r"""
public static String buyOre0(java.util.UUID u, String k, int kd, int slot, int li, @IC@[] cs) {
  if (!@PKG@.ShCfg.ON || !@PKG@.ShCfg.CK_ON || !@PKG@.ShCfg.MQ_ON) return "-The Mining quarry is switched off on this server.";
  if (kd != MK) return "-Ores are a Mining quarry upgrade.";
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
    if (!isBase(p, kd, slot) || @PKG@.ShIsl.zoneOf(@PKG@.ShIsl.ty(kd, p, slot)) != z) return "=The page is up to date now - open the quarry again.";
    if (@PKG@.ShIsl.owns(kd, p, t)) return "=Your Zone " + z + " quarry mines " + @PKG@.ShIsl.NAME[t] + " already.";
    int nx = @PKG@.ShIsl.nextTier(kd, p);
    if (nx != li) return nx < 0 ? "=Your quarries mine every ore already." : "-Add " + @PKG@.ShIsl.NAME[@PKG@.ShIsl.LAD0[kd] + nx] + " first (ores and quarries come in tier order).";
    cur = @PKG@.ShStore.str(p, @PKG@.ShMath.ik(kd, slot, "ores"));
    ver = @PKG@.ShStore.ver(k);   // purchaseM commits only while nothing was saved since
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  long coins = @PKG@.ShIsl.coins(@PKG@.ShCfg.BUY_H, cv);
  Object[] mats = @PKG@.ShIsl.mats(kd, t, @PKG@.ShCfg.BUY_ITEMS[kd], 0, 1L);
  String nv = cur.length() == 0 ? @PKG@.ShIsl.KEY[t] : cur + "," + @PKG@.ShIsl.KEY[t];
  String r = @PKG@.ShCore.purchaseM(u, k, kd, p, cs, mats, coins, new String[] { @PKG@.ShMath.ik(kd, slot, "ores") }, new String[] { nv }, "ore",
                                    @PKG@.ShKind.KEYS[kd] + " add ore " + @PKG@.ShIsl.KEY[t] + " to the Zone " + z + " quarry (slot " + slot + ")", ver);
  if (r != null) return r;
  return "+" + @PKG@.ShIsl.NAME[t] + " added to your Zone " + z + " quarry - its ore nodes join the others.";
}""")
M(ckc, "public static String buyOre(java.util.UUID u, String k, int kd, int slot, int li, @IC@[] cs) { String r = buyOre0(u, k, kd, slot, li, cs); @PKG@.ShSnd.ok(u, r, 2); return r; }")
M(ckc, r"""
public static long smithyCoins(double cv) { return @PKG@.ShIsl.coins(@PKG@.ShCfg.MQ_SM_H, cv); }""")''')

# ---------------------------------------------------------------------------------------------------- 5. ShStore.migrate5 = THE MINING ZONE MIGRATION (after ShClk.isBase)
P.rep('''M(ckc, "public static boolean isBase(java.util.Properties p, int kd, int slot) { return kd != MK || (slot >= 0 && baseSlot(p, @PKG@.ShIsl.zoneOf(@PKG@.ShIsl.ty(kd, p, slot))) == slot); }")   # fix: under ShStore.LOCK
''', '''M(ckc, "public static boolean isBase(java.util.Properties p, int kd, int slot) { return kd != MK || (slot >= 0 && baseSlot(p, @PKG@.ShIsl.zoneOf(@PKG@.ShIsl.ty(kd, p, slot))) == slot); }")   # fix: under ShStore.LOCK
# ================= 0.4.30 FIXER: items that reach a quarry's storage (.drops) without a click owe their Mining XP at once (Collect pays none for .drops):
# Collect's exact XP (xpOf x shard.xpPercent; the fraction carried in <kind>.i<n>.xpr, hundredths) -> the profile file's owed.xp.<Skill> (paid with the
# next mined node / Collect: ShCore.owedXp). Under ShStore.LOCK.
M(mth, r"""
public static long oweXp(int kd, java.util.Properties p, int slot, long units) {
  if (p == null || units <= 0L) return 0L;
  long per = (long) @PKG@.ShCfg.xpOf(kd);
  if (per <= 0L) return 0L;
  String rk = ik(kd, slot, "xpr");
  long c = @PKG@.ShStore.lng(p, rk, 0L);
  if (c < 0L || c > 99L) c = 0L;
  long h = units * per * (long) @PKG@.ShCfg.XP_PCT + c;
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
# the ores a Mining quarry's spirits share (tier order): its own ore + every ore on its Ores row; length < 2 = no sharing (every other island / kind)
M(mth, r"""
public static int[] shareOres(int kd, java.util.Properties p, int slot) {
  if (p == null || kd != @PKG@.ShClk.MK || !hasIsland(kd, p, slot)) return new int[0];
  String ol = @PKG@.ShStore.str(p, ik(kd, slot, "ores"));
  if (ol.length() == 0) return new int[0];
  int t = @PKG@.ShIsl.ty(kd, p, slot);
  if (t < 0) return new int[0];
  int z = @PKG@.ShIsl.zoneOf(t);
  if (@PKG@.ShClk.baseSlot(p, z) != slot) return new int[0];
  int[] o = @PKG@.ShClk.zoneOwned(p, z);
  int[] w = new int[o.length];
  int n = 0;
  for (int i = 0; i < o.length; i++) if (o[i] == t || @PKG@.ShIsl.oreListed(ol, @PKG@.ShIsl.KEY[o[i]])) { w[n] = o[i]; n++; }
  int[] r = new int[n];
  for (int i = 0; i < n; i++) r[i] = w[i];
  return r;
}""")
# settle's `made` shared round-robin over the quarry's ores (mining.i<n>.orr = the next ore's turn): returns what went to .drops (the rest stays stock)
mth.getDeclaredMethod("oreShare").setBody(jv(r"""{
  int kd = $1;
  java.util.Properties p = $2;
  int slot = $3;
  long made = $4;
  if (made <= 0L) return 0L;
  int[] w = shareOres(kd, p, slot);
  int n = w.length;
  if (n < 2) return 0L;
  int t = @PKG@.ShIsl.ty(kd, p, slot);
  String rk = ik(kd, slot, "orr");
  long r = @PKG@.ShStore.lng(p, rk, 0L);
  if (r < 0L || r >= (long) n) r = 0L;
  boolean sm = @PKG@.ShTotem.smelts(kd, p, slot);
  java.util.LinkedHashMap m = held(kd, p, slot);
  long q = made / (long) n;
  long rm = made % (long) n;
  long out = 0L;
  for (int j = 0; j < n; j++) {
    if (w[j] == t) continue;
    long d = (((long) j - r) % (long) n + (long) n) % (long) n;
    long c = q + (d < rm ? 1L : 0L);
    if (c <= 0L) continue;
    String id = sm && @PKG@.ShIsl.SMELT[w[j]].length() > 0 ? @PKG@.ShIsl.SMELT[w[j]] : @PKG@.ShIsl.PROD[w[j]];
    Object v = m.get(id);
    m.put(id, Long.valueOf((v instanceof Long ? ((Long) v).longValue() : 0L) + c));
    out += c;
  }
  if (out > 0L) { heldSet(kd, p, slot, m); oweXp(kd, p, slot, out); }
  p.setProperty(rk, String.valueOf((r + rm) % (long) n));
  return out;
}"""))
# ================= 0.4.30 ShStore.migrate5 = THE MINING ZONE MIGRATION (tools/shards_0_4_30_patch.py; PROJECT-RULES 4): once per profile file, marker
# mzone.done=1. Each zone's 2nd / 3rd Mining island folds into the zone's quarry (its lowest-tier island): ore -> the quarry's ores list, the higher
# size / effective sub levels / Vein size / Lucky / Smithy, every totem, every item in base units (Collect pays the same XP + collection credit).
# Checked before = after (items in base units, totems, owned ores, islands - folded); History copy first; ONE save; a collect.log journal line.
M(st, r"""
public static String snapZone(String k) {   // 0.4.30: = snapClk, the .pre-0.4.30 copy
  try {
    java.nio.file.Path f = DIR.resolve(k + ".properties");
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "-";
    java.nio.file.Path h = DIR.resolve("history").resolve("clicker");
    java.nio.file.Files.createDirectories(h, new java.nio.file.attribute.FileAttribute[0]);
    byte[] src = java.nio.file.Files.readAllBytes(f);
    String name = k + ".pre-0.4.30.properties";
    java.nio.file.Path t = h.resolve(name);
    if (java.nio.file.Files.exists(t, new java.nio.file.LinkOption[0]) && !java.util.Arrays.equals(src, java.nio.file.Files.readAllBytes(t))) {
      name = k + ".pre-0.4.30." + System.currentTimeMillis() + ".properties";
      t = h.resolve(name);
    }
    if (!java.nio.file.Files.exists(t, new java.nio.file.LinkOption[0])) {
      java.nio.file.Path tmp = h.resolve(name + ".tmp");
      java.nio.file.Files.write(tmp, src, new java.nio.file.OpenOption[0]);
      moveInto(tmp, t);
    }
    if (!java.util.Arrays.equals(src, java.nio.file.Files.readAllBytes(t))) { @PKG@.ShCfg.warnOnce("mzsnap:" + k, "the 0.4.30 Mining zone migration copy of " + k + " does not match the file - not migrated"); return null; }
    return "shards/history/clicker/" + name;
  } catch (Throwable x) {
    @PKG@.ShCfg.warnOnce("mzsnapx:" + k, "the 0.4.30 Mining zone migration of " + k + " is waiting: its History copy could not be written (" + x + ")");
    return null;
  }
}""")
F(st, "public static volatile boolean MZ_FAIL_TEST = false;")   # harness: the totals check fails (nothing may change)
# the island keys a fold knows: handled (merged into the quarry) or dropped (the walkable world's geometry / clocks - the History copy keeps them)
F(st, 'public static final String[] MZ_KEEP = new String[] { "size", "amt", "deco", "irr", "nsize", "luck", "smithy", "alloyPct", "totems", "stored", "legacy", "drops", "seed", "ench", "ores" };')
F(st, 'public static final String[] MZ_DROP = new String[] { "type", "last", "offAt", "sacc", "cave", "centre", "pl", "tp", "seeded", "arena", "xpn", "xpw", "orr", "xpr" };')
M(st, r"""
public static boolean mzKnown(String f) {
  for (int i = 0; i < MZ_KEEP.length; i++) if (MZ_KEEP[i].equals(f)) return true;
  for (int i = 0; i < MZ_DROP.length; i++) if (MZ_DROP[i].equals(f)) return true;
  return false;
}""")
M(st, r"""
public static void mzPut(java.util.Map m, String id, long n) {
  if (id == null || id.length() == 0 || n == 0L) return;
  Object o = m.get(id);
  m.put(id, Long.valueOf((o instanceof Long ? ((Long) o).longValue() : 0L) + n));
}""")
# every item of the shard in base units (what Collect all pays, gridOf): an Enchanted = 100 of its base, a bar = its ore
M(st, r"""
public static java.util.HashMap mzUnits(int kd, java.util.Properties p) {
  java.util.HashMap u = new java.util.HashMap();
  Object[] g = @PKG@.ShCore.gridOf(kd, p);
  String[] ids = (String[]) g[0];
  long[] q = (long[]) g[1];
  for (int i = 0; i < ids.length && i < q.length; i++) {
    String id = ids[i];
    long n = q[i];
    String b = @PKG@.ShIsl.enchBase(id);
    if (b != null) { id = b; n = n * 100L; }
    String o = @PKG@.ShCore.oreOfBar(id);
    if (o != null) id = o;
    mzPut(u, id, n);
  }
  return u;
}""")
M(st, r"""
public static int mzIsl(int kd, java.util.Properties p) {
  int n = 0;
  for (int s = 0; s < @PKG@.ShMath.SLOTS; s++) if (@PKG@.ShMath.hasIsland(kd, p, s)) n++;
  return n;
}""")
M(st, r"""
public static int mzTot(int kd, java.util.Properties p) {
  int n = 0;
  for (int s = 0; s < @PKG@.ShMath.SLOTS; s++) if (@PKG@.ShMath.hasIsland(kd, p, s)) n += @PKG@.ShTotem.entries(kd, p, s).length;
  return n;
}""")
M(st, r"""
public static String mzOwn(int kd, java.util.Properties p) {
  StringBuilder b = new StringBuilder();
  for (int i = 0; i < @PKG@.ShIsl.LADN[kd]; i++) b.append(@PKG@.ShIsl.owns(kd, p, @PKG@.ShIsl.LAD0[kd] + i) ? '1' : '0');
  return b.toString();
}""")
M(st, r"""
public static String mzAdd(String list, String key) {
  if (key == null || key.length() == 0 || @PKG@.ShIsl.oreListed(list, key)) return list;
  return list == null || list.length() == 0 ? key : list + "," + key;
}""")
# an Enchanted legacy id -> its exact base: what the island compressed (sm = it smelts: an Enchanted bar -> the bar, else an Enchanted ore -> the ore;
# some types share one Enchanted id for both); null = not an Enchanted id
M(st, r"""
public static String mzBase(String id, boolean sm) {
  if (id == null || id.length() == 0) return null;
  for (int pass = 0; pass < 2; pass++) {
    boolean bars = (pass == 0) == sm;
    for (int t = 0; t < @PKG@.ShIsl.PROD.length; t++) {
      if (bars && @PKG@.ShIsl.SMELTE[t].length() > 0 && id.equals(@PKG@.ShIsl.SMELTE[t]) && @PKG@.ShIsl.SMELT[t].length() > 0) return @PKG@.ShIsl.SMELT[t];
      if (!bars && @PKG@.ShIsl.ENCH[t].length() > 0 && id.equals(@PKG@.ShIsl.ENCH[t])) return @PKG@.ShIsl.PROD[t];
    }
  }
  return null;
}""")
M(st, r"""
public static int mzLv(java.util.Properties p, int kd, int slot, String f) {
  return @PKG@.ShStore.intv(p, @PKG@.ShMath.ik(kd, slot, f), 0, 0, 1000000);
}""")
# fold island o into the zone's quarry b (under LOCK, production settled); null = done, else why not (nothing of it changed yet)
M(st, r"""
public static String mzFold(int kd, java.util.Properties p, int o, int b, StringBuilder ch) {
  String pre = @PKG@.ShMath.ik(kd, o, "");
  java.util.ArrayList keys = new java.util.ArrayList();
  java.util.Iterator it = p.stringPropertyNames().iterator();
  while (it.hasNext()) { String q = (String) it.next(); if (q.startsWith(pre)) keys.add(q); }
  for (int i = 0; i < keys.size(); i++) {
    String f = ((String) keys.get(i)).substring(pre.length());
    if (!mzKnown(f)) return "an unknown island key " + keys.get(i);
  }
  int to = @PKG@.ShIsl.ty(kd, p, o);
  int tb = @PKG@.ShIsl.ty(kd, p, b);
  // the ore (and any the folded island listed) -> the quarry's ores
  boolean dup = @PKG@.ShIsl.oreListed(@PKG@.ShStore.str(p, @PKG@.ShMath.ik(kd, b, "ores")), @PKG@.ShIsl.KEY[to]);   // fixer 2: re-bought under 0.4.29
  String ol = mzAdd(@PKG@.ShStore.str(p, @PKG@.ShMath.ik(kd, b, "ores")), @PKG@.ShIsl.KEY[to]);
  String[] oo = @PKG@.ShStore.str(p, @PKG@.ShMath.ik(kd, o, "ores")).split(",");
  for (int i = 0; i < oo.length; i++) ol = mzAdd(ol, oo[i].trim());
  p.setProperty(@PKG@.ShMath.ik(kd, b, "ores"), ol);
  // size = the larger; each sub-upgrade = the higher effective level (5 x (size - 1) + level: what the output bonus counts)
  int sb = @PKG@.ShMath.size(kd, p, b); int so = @PKG@.ShMath.size(kd, p, o);
  int sn = sb > so ? sb : so;
  StringBuilder sc = new StringBuilder();
  sc.append("size ").append(sb).append('/').append(so).append("->").append(sn);
  int[] nl = new int[3];
  for (int w = 0; w < 3; w++) {
    int lb = @PKG@.ShIsl.sub(p, kd, b, w); int lo = @PKG@.ShIsl.sub(p, kd, o, w);
    int eb = @PKG@.ShIsl.lt(sb, lb); int eo = @PKG@.ShIsl.lt(so, lo);
    int e = eb > eo ? eb : eo;
    int l = e - 5 * (sn - 1);
    nl[w] = l < 0 ? 0 : (l > 5 ? 5 : l);
    sc.append(", ").append(@PKG@.ShIsl.SUBK[w]).append(' ').append(lb).append('/').append(lo).append("->").append(nl[w]);
  }
  p.setProperty(@PKG@.ShMath.ik(kd, b, "size"), String.valueOf(sn));
  for (int w = 0; w < 3; w++) p.setProperty(@PKG@.ShIsl.ik(kd, b, @PKG@.ShIsl.SUBK[w]), String.valueOf(nl[w]));
  String[] mx = new String[] { "nsize", "luck", "smithy" };
  for (int i = 0; i < mx.length; i++) {
    int vb = mzLv(p, kd, b, mx[i]); int vo = mzLv(p, kd, o, mx[i]);
    if (vo > vb) p.setProperty(@PKG@.ShMath.ik(kd, b, mx[i]), String.valueOf(vo));
    if (vb > 0 || vo > 0) sc.append(", ").append(mx[i]).append(' ').append(vb).append('/').append(vo).append("->").append(vo > vb ? vo : vb);
  }
  String ap = @PKG@.ShMath.ik(kd, b, "alloyPct");
  String apo = @PKG@.ShStore.str(p, @PKG@.ShMath.ik(kd, o, "alloyPct"));
  if (@PKG@.ShStore.str(p, ap).length() == 0 && apo.length() > 0) p.setProperty(ap, apo);
  // every totem entry, the quarry's first
  String[] eb2 = @PKG@.ShTotem.entries(kd, p, b);
  String[] eo2 = @PKG@.ShTotem.entries(kd, p, o);
  String[] all = new String[eb2.length + eo2.length];
  for (int i = 0; i < eb2.length; i++) all[i] = eb2[i];
  for (int i = 0; i < eo2.length; i++) all[eb2.length + i] = eo2[i];
  if (eo2.length > 0) @PKG@.ShTotem.setEntries(kd, p, b, all);
  // every item, in base units, into the quarry's storage (.drops)
  java.util.LinkedHashMap m = @PKG@.ShMath.held(kd, p, b);
  long moved = 0L;
  long xu = 0L;   // fixer: the base units Collect would have paid XP for (stock + Enchanted stock); .drops pay none
  long st0 = @PKG@.ShMath.stored(kd, p, o);
  boolean sm = @PKG@.ShTotem.smelts(kd, p, o) && @PKG@.ShIsl.SMELT[to].length() > 0;
  if (st0 > 0L) {
    mzPut(m, sm ? @PKG@.ShIsl.SMELT[to] : @PKG@.ShIsl.PROD[to], st0);
    moved += st0; xu += st0;
  }
  String lg = @PKG@.ShStore.str(p, @PKG@.ShIsl.ik(kd, o, "legacy"));
  int lc = lg.lastIndexOf(':');
  if (lc > 0) {
    long ln = 0L;
    try { ln = Long.parseLong(lg.substring(lc + 1).trim()); } catch (Throwable x) { ln = 0L; }
    String lid = lg.substring(0, lc).trim();
    if (ln > 0L && lid.length() > 0) {
      String lb2 = mzBase(lid, sm);
      if (lb2 != null) { mzPut(m, lb2, ln * 100L); moved += ln * 100L; xu += ln * 100L; } else { mzPut(m, lid, ln); moved += ln; xu += ln; }
    }
  }
  java.util.Iterator hi = @PKG@.ShMath.held(kd, p, o).entrySet().iterator();
  while (hi.hasNext()) { java.util.Map.Entry he = (java.util.Map.Entry) hi.next(); long hn = ((Long) he.getValue()).longValue(); mzPut(m, (String) he.getKey(), hn); moved += hn; }
  long sd = @PKG@.ShIsl.seeds(kd, p, o);
  String sid = @PKG@.ShIsl.SEED[to];
  if (sd > 0L && sid != null && sid.length() > 0) { mzPut(m, sid, sd); moved += sd; }
  @PKG@.ShMath.heldSet(kd, p, b, m);
  long xo = @PKG@.ShMath.oweXp(kd, p, b, xu);   // fixer: no XP lost - Collect would have paid it for the stock; the .drops pay none
  long en = @PKG@.ShMath.ench(kd, p, o);
  if (en > 0L) p.setProperty(@PKG@.ShMath.ik(kd, b, "ench"), String.valueOf(@PKG@.ShMath.ench(kd, p, b) + en));
  for (int i = 0; i < keys.size(); i++) p.remove((String) keys.get(i));
  ch.append(", Zone ").append(@PKG@.ShIsl.zoneOf(to)).append(": ").append(@PKG@.ShIsl.NAME[to]).append(" (slot ").append(o).append(") -> the ").append(@PKG@.ShIsl.NAME[tb])
    .append(" quarry (slot ").append(b).append("): ").append(sc.toString()).append(", totems ").append(eb2.length).append('+').append(eo2.length)
    .append(", ").append(moved).append(" items + ").append(en).append(" rare finds -> its storage, ").append(xo).append(" ").append(@PKG@.ShKind.SKILL[kd]).append(" XP owed");
  if (dup) ch.append(" (").append(@PKG@.ShIsl.NAME[to]).append(" was already on its Ores row - bought again under 0.4.29; nothing refunded)");
  return null;
}""")
st.getDeclaredMethod("migrate5").setBody(jv(r"""{
  String k = $1;
  java.util.Properties p = $2;
  if (p == null || k == null) return;   // fixer 2: NOT skipped on mzone.done - a Mining island made after the fold (0.4.29 rollback re-buy) folds too
  LOCK.lock();
  try {
    int kd = @PKG@.ShClk.MK;
    int nf = 0;
    for (int s = 0; s < @PKG@.ShMath.SLOTS; s++) {
      if (!@PKG@.ShMath.hasIsland(kd, p, s)) continue;
      if (@PKG@.ShClk.baseSlot(p, @PKG@.ShIsl.zoneOf(@PKG@.ShIsl.ty(kd, p, s))) != s) nf++;
    }
    if (nf == 0) { MZCHK.incrementAndGet(); return; }   // one island a zone at most: nothing to do, nothing written
    java.util.Properties old = new java.util.Properties();
    old.putAll(p);
    long now = @PKG@.ShCore.now();
    @PKG@.ShMath.settleAll(kd, p, now);   // production up to now at the old numbers
    java.util.HashMap g0 = mzUnits(kd, p);
    int i0 = mzIsl(kd, p); int t0 = mzTot(kd, p); String o0 = mzOwn(kd, p);
    StringBuilder ch = new StringBuilder();
    String bad = null;
    for (int z = 1; z <= 5 && bad == null; z++) {
      int b = @PKG@.ShClk.baseSlot(p, z);
      if (b < 0) continue;
      for (int s = 0; s < @PKG@.ShMath.SLOTS && bad == null; s++) {
        if (s == b || !@PKG@.ShMath.hasIsland(kd, p, s) || @PKG@.ShIsl.zoneOf(@PKG@.ShIsl.ty(kd, p, s)) != z) continue;
        bad = mzFold(kd, p, s, b, ch);
      }
    }
    if (bad == null) {
      java.util.HashMap g1 = mzUnits(kd, p);
      if (MZ_FAIL_TEST || !g0.equals(g1)) bad = "the items do not add up (" + g0 + " -> " + g1 + ")";
      else if (mzTot(kd, p) != t0) bad = "the totems do not add up (" + t0 + " -> " + mzTot(kd, p) + ")";
      else if (!o0.equals(mzOwn(kd, p))) bad = "the ores owned changed (" + o0 + " -> " + mzOwn(kd, p) + ")";
      else if (mzIsl(kd, p) != i0 - nf) bad = "the island count is off (" + i0 + " - " + nf + " -> " + mzIsl(kd, p) + ")";
    }
    if (bad != null) {
      p.clear(); p.putAll(old);
      MZWAIT.incrementAndGet();
      @PKG@.ShCfg.warnOnce("mzbad:" + k, "the 0.4.30 Mining zone migration of " + k + " is waiting - nothing changed: " + bad);
      return;
    }
    String snap = snapZone(k);
    if (snap == null) { p.clear(); p.putAll(old); MZWAIT.incrementAndGet(); return; }
    p.setProperty("mzone.done", "1");
    String err = save(k, p);
    if (err != null) { p.clear(); p.putAll(old); MZWAIT.incrementAndGet(); @PKG@.ShCfg.warnOnce("mzsave:" + k, "the 0.4.30 Mining zone migration of " + k + " is waiting (the file could not be saved: " + err + ")"); return; }
    MZMIG.incrementAndGet();
    log("mining zone migration (SkyyShards @VERSION@) " + k + ": one Mining island a zone" + ch.toString() + " (" + i0 + " Mining islands -> " + (i0 - nf) + " zone quarries; " + t0 + " totems, every item and every owned ore kept) - History copy " + snap + " (the last save before the fold) - Undo: stop the server, copy it back over shards/" + k + ".properties and put SkyyShards 0.4.29 back");
    @PKG@.ShCfg.info("0.4.30 Mining zone migration: " + k + " - " + nf + " ore island(s) folded into their zone quarry" + ch.toString() + " (collect.log has the Undo)");
  } finally { LOCK.unlock(); }
}"""))
''')

# ---------------------------------------------------------------------------------------------------- 6. the quarry page: owns, the map = one card a zone, the Ores row (9th)
P.rep('''  this.ckMine = true;
  this.ckFarm = false;   // 0.4.25
  this.ckTown = false;   // 0.4.26
  this.ckUpL = new String[8]; this.ckUpE = new String[8]; this.ckUpC = new String[8]; this.ckUpOk = new boolean[8]; this.ckUpSeen = new int[8];
  for (int i = 0; i < 8; i++) { this.ckUpL[i] = ""; this.ckUpE[i] = ""; this.ckUpC[i] = ""; this.ckUpOk[i] = false; this.ckUpSeen[i] = 0; }''',
      '''  this.ckMine = true;
  this.ckFarm = false;   // 0.4.25
  this.ckTown = false;   // 0.4.26
  this.ckUpL = new String[9]; this.ckUpE = new String[9]; this.ckUpC = new String[9]; this.ckUpOk = new boolean[9]; this.ckUpSeen = new int[9];   // 0.4.30: + row 8 Ores
  for (int i = 0; i < 9; i++) { this.ckUpL[i] = ""; this.ckUpE[i] = ""; this.ckUpC[i] = ""; this.ckUpOk[i] = false; this.ckUpSeen[i] = 0; }''')
P.rep('''  int[] ores = new int[0];
''', '''  int[] ores = new int[0];
  int[] zq = new int[] { -1, -1, -1, -1, -1 };   // 0.4.30: each zone's quarry slot
''')
P.rep('''    for (int i = 0; i < LN; i++) own[i] = @PKG@.ShIsl.slotOf(kd, p, L0 + i);
''', '''    for (int i = 0; i < LN; i++) own[i] = @PKG@.ShIsl.owns(kd, p, L0 + i) ? 1 : -1;   // 0.4.30: an island or an ore upgrade
    for (int zz = 0; zz < 5; zz++) zq[zz] = @PKG@.ShClk.baseSlot(p, zz + 1);
''')
P.rep('''      nx = " Add " + @PKG@.ShIsl.NAME[L0 + i] + ": buy its island on Islands" + (nd > 0 ? " (" + @PKG@.ShIsl.skillWord(kd) + " " + nd + ")" : "") + ".";''',
      '''      nx = " Add " + @PKG@.ShIsl.NAME[L0 + i] + " on the Ores row" + (nd > 0 ? " (" + @PKG@.ShIsl.skillWord(kd) + " " + nd + ")" : "") + ".";   // 0.4.30: an upgrade, not an island''')
P.rep('''    this.ckUpCap = this.mine ? "coins + " + @PKG@.ShTotem.pretty(@PKG@.ShIsl.tok(kd, t, "ench")) : "the island owner buys upgrades";
  } else this.ckCap = "No Mining island yet - open Islands to buy the first one.";''',
      '''    // 8 Ores (0.4.30): the zone's next ore joins this quarry at the price its own island had (tier order, the zone lock)
    int zn8 = 0; int zh8 = 0; int nx8 = -1;
    for (int i = 0; i < LN; i++) {
      if (@PKG@.ShIsl.zoneOf(L0 + i) != z) continue;
      zn8++;
      if (own[i] >= 0) zh8++;
      else if (nx8 < 0) nx8 = i;
    }
    this.ckUpL[8] = zh8 + " / " + zn8 + " ores"; this.ckUpSeen[8] = nx8;
    if (nx8 < 0) { this.ckUpE[8] = "Mines " + on.toString(); ckTextR(8, "Every ore of Zone " + z + " is in this quarry."); }
    else {
      int t8 = L0 + nx8;
      int nd8 = @PKG@.ShIsl.zoneNeed(kd, t8);
      this.ckUpE[8] = "Add " + @PKG@.ShIsl.NAME[t8] + ": more ore nodes";
      if (nd8 > 0 && lv != -1 && lv < nd8) ckTextR(8, "Needs " + @PKG@.ShIsl.skillWord(kd) + " " + nd8 + (lv >= 0 ? " (you: " + lv + ")." : "."));
      else if (this.ckNext >= 0 && this.ckNext != nx8) ckTextR(8, "Add " + @PKG@.ShIsl.NAME[L0 + this.ckNext] + " first - ores and quarries come in tier order.");
      else { ckCostR(8, @PKG@.ShIsl.coins(@PKG@.ShCfg.BUY_H, tcv[nx8]), @PKG@.ShIsl.mats(kd, t8, @PKG@.ShCfg.BUY_ITEMS[kd], 0, 1L)); this.ckUpOk[8] = this.mine; }
    }
    this.ckUpCap = this.mine ? "coins + " + @PKG@.ShTotem.pretty(@PKG@.ShIsl.tok(kd, t, "ench")) : "the island owner buys upgrades";
  } else this.ckCap = "No Mining quarry yet - open Islands to buy the Zone 1 quarry.";''')
_OLD_MAP = cut('''  // the quarry map: five zones of their ores (QCARD: card -> ladder rank)
''', '''  for (int zz = 0; zz < 5; zz++) {
    int li0 = QCARD[3 * zz];''')
P.rep(_OLD_MAP, '''  // the quarry map (0.4.30): ONE card a zone = its quarry (QCARD[3 x zone] = the zone's first ore); its other ores are upgrades inside it
  for (int zz = 0; zz < 5; zz++) {
    int c = 3 * zz;
    if (c >= QCARD.length) break;
    int li = QCARD[c];
    if (li < 0 || li >= LN) continue;
    int tt = L0 + li;
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
    this.ckMN[c] = nm.length() <= 24 ? nm : @PKG@.ShIsl.NAME[tt] + " + " + (zn - 1) + " more ores";
    boolean have = zq[zz] >= 0;
    this.ckMCur[c] = have && t >= 0 && z == zz + 1;
    this.ckMLock[c] = !open && !have;
    if (have) { this.ckMS[c] = (this.ckMCur[c] ? "Shown now" : "Yours") + " - " + zh + " / " + zn + " ores" + (add.length() > 0 ? "; add " + add + " inside" : ""); this.ckMB[c] = 1; }
    else if (!open) this.ckMS[c] = "Locked: " + @PKG@.ShIsl.skillWord(kd) + " " + need;
    else if (li == this.ckNext) {
      this.ckMS[c] = "Buy: " + ckCost(@PKG@.ShIsl.coins(@PKG@.ShCfg.BUY_H, tcv[li]), @PKG@.ShIsl.mats(kd, tt, @PKG@.ShCfg.BUY_ITEMS[kd], 0, 1L));
      this.ckMB[c] = this.mine ? 2 : 0;
    }
    else if (this.ckNext >= 0) {
      int tq = L0 + this.ckNext;
      int zq2 = @PKG@.ShIsl.zoneOf(tq);
      this.ckMS[c] = "First add " + @PKG@.ShIsl.NAME[tq] + (zq2 >= 1 && zq2 <= 5 && zq[zq2 - 1] >= 0 ? " in the Zone " + zq2 + " quarry" : " (Zone " + zq2 + ")");
    }
    else this.ckMS[c] = "Buy the quarries before it first";
  }
''')
# the map clicks: Open = that zone's quarry; Buy = the zone's quarry (its first ore's island, as 0.4.29)
P.rep('''      int tt = @PKG@.ShIsl.LAD0[kd] + li;
      s = @PKG@.ShIsl.slotOf(kd, p, tt) < 0 ? -1 : @PKG@.ShClk.baseSlot(p, @PKG@.ShIsl.zoneOf(tt));
    } finally { @PKG@.ShStore.LOCK.unlock(); }
    if (s < 0) return "-That island is not yours yet.";''', '''      int tt = @PKG@.ShIsl.LAD0[kd] + li;
      s = @PKG@.ShClk.baseSlot(p, @PKG@.ShIsl.zoneOf(tt));   // 0.4.30: the zone's quarry
    } finally { @PKG@.ShStore.LOCK.unlock(); }
    if (s < 0) return "-That quarry is not yours yet.";''')
P.rep('''{ int tt = @PKG@.ShIsl.LAD0[kd] + li; s = @PKG@.ShIsl.slotOf(kd, p, tt) < 0 ? -1 : @PKG@.ShClk.baseSlot(p, @PKG@.ShIsl.zoneOf(tt)); }''',
      '''{ int tt = @PKG@.ShIsl.LAD0[kd] + li; s = @PKG@.ShClk.baseSlot(p, @PKG@.ShIsl.zoneOf(tt)); }''')
P.rep('''    if (row < 0 || row > 7) return "";''', '''    if (row < 0 || row > 8) return "";   // 0.4.30: + row 8 Ores''')
P.rep('''    if (row == 2) return @PKG@.ShCore.buySpirit(u, k, kd, s, seen, cs);   // 0.4.27: the spirit row buys / tiers up here
    if (row == 7 && seen == 0 && this.ckQSm == 0)''', '''    if (row == 8) return ckFresh(k, kd, s) ? @PKG@.ShClk.buyOre(u, k, kd, s, seen, cs) : "=The page is up to date now - click Add ore again.";   // 0.4.30: the zone's next ore
    if (row == 2) return @PKG@.ShCore.buySpirit(u, k, kd, s, seen, cs);   // 0.4.27: the spirit row buys / tiers up here
    if (row == 7 && seen == 0 && this.ckQSm == 0)''')
P.rep('''this.ckCL = new String[60]; this.ckCG = new int[60]; this.ckUpBtn = new int[8];''',
      '''this.ckCL = new String[60]; this.ckCG = new int[60]; this.ckUpBtn = new int[9];   // 0.4.30: 9 rows (the quarry's Ores)''')

# the spirit row (fixer 5): a quarry whose spirits share several ores says "ore a minute" (the row stays short)
P.rep('''  int cur = 0; double r0 = 0.0; double r1 = 0.0; String[] f = null; StringBuilder also = new StringBuilder(); int n = 0;
''', '''  int cur = 0; double r0 = 0.0; double r1 = 0.0; String[] f = null; StringBuilder also = new StringBuilder(); int n = 0;
  int shN = 0;   // 0.4.30 fixer: the ores this quarry's spirits share
''')
P.rep('''    if (!@PKG@.ShMath.hasIsland(kd, p, s) || @PKG@.ShIsl.ty(kd, p, s) != this.ckT) return;
''', '''    if (!@PKG@.ShMath.hasIsland(kd, p, s) || @PKG@.ShIsl.ty(kd, p, s) != this.ckT) return;
    shN = @PKG@.ShMath.shareOres(kd, p, s).length;
''')
P.rep('''  String nm = @PKG@.ShTotem.pretty(@PKG@.ShIsl.PROD[this.ckT]);''',
      '''  String nm = shN > 1 ? "ore" : @PKG@.ShTotem.pretty(@PKG@.ShIsl.PROD[this.ckT]);   // 0.4.30 fixer: shared over the quarry's ores''')

# ---------------------------------------------------------------------------------------------------- 7. the page markup: one map card a zone, the 9th row
P.rep('''for _z, _ids in enumerate(MQ_ZT):
    for _q, _li in enumerate(_ids):
        MQ_CARD[3 * _z + _q] = _li''', '''for _z, _ids in enumerate(MQ_ZT):
    for _q, _li in enumerate(_ids[:1]):   # 0.4.30: one card a zone (its quarry = the zone's first ore); its other ores are upgrades inside
        MQ_CARD[3 * _z + _q] = _li''')
P.rep('''    for _q, _li in enumerate(MQ_ZT[_z]):
        M_ = CKP + "M%d" % (3 * _z + _q)''', '''    for _q, _li in enumerate(MQ_ZT[_z][:1]):   # 0.4.30: the zone's quarry card only
        M_ = CKP + "M%d" % (3 * _z + _q)''')
P.rep('''             "Q": (Q_UP_NAMES[:2] + ["Miner spirit"] + Q_UP_NAMES[3:], Q_UP_ICON),''',
      '''             "Q": (Q_UP_NAMES[:2] + ["Miner spirit"] + Q_UP_NAMES[3:] + ["Ores"], Q_UP_ICON + ["UpQNodes"]),   # 0.4.30: + the zone's ore upgrades''')
P.rep('''        _lab = ["Tier up", "Buy"] if _r == 2 else (["Upgrade", "Buy"] if (_K == "Q" and _r == 7) else ["Upgrade"])''',
      '''        _lab = ["Tier up", "Buy"] if _r == 2 else (["Upgrade", "Buy"] if (_K == "Q" and _r == 7) else (["Add ore"] if (_K == "Q" and _r == 8) else ["Upgrade"]))   # 0.4.30''')

# ---------------------------------------------------------------------------------------------------- 8. the ready line
P.rep(r'''log("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.29:''', r'''log("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.30: the Mining quarry is one island a zone (its other ores are upgrades on its Ores row; Zone migration mzone.done); 0.4.29:''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0, "command / system registrations changed"
P.finish()
