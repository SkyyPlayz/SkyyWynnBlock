"""Derive SkyyShards/build_skyyshards_0.4.34.py from the SET pin 0.4.33 (the GENERATED build_skyyshards_0.4.33.py; edit THIS file, then
regenerate: python tools/shards_0_4_34_patch.py; never re-run shards_0_4_33_patch.py on top of it). Every anchor is asserted once; at the end
every change is undone on a copy and compared with 0.4.33 (nothing else changed). Line endings kept.
Run:  python tools/shards_0_4_34_patch.py   then   python SkyyShards/build_skyyshards_0.4.34.py   (never --deploy from an agent)
Test: python SkyyShards/test_skyyshards_0.4.34.py [--dir <folder inside tools/dev/scratch/>] [--keep]

0.4.34 (2026-11-24) = THE MINING QUARRY: SILVER / GOLD EVERYWHERE + THE ZONE'S STONE TYPES (round mzone2). Skyy 2026-11-14 docs/answered/world.md
  "MINING SHARD = QUARRY, ONE ISLAND PER ZONE": "silver and gold are found in all of them with upgrades to make them more common, but it follows vanilla
  trends, so silverr is most popular in zone 3. so you uprgade the miner spirits and the quarry to mine faster, and upgrade your chances of getting
  something good per block mined. (this way you get all the stone types too, not just ore.)" + 2026-11-23 "looks better. go head and build everything on
  your list." (rounds mzone1 0.4.30 = one quarry a zone + Add ore, clkart1 0.4.32 = the art, link1 0.4.33 = Shard Link.)
  SURVEY (vanilla first, read-only Assets.zip): Server/World/Default/Ores/Zone1..Zone4/<Ore>Placement.json + Zones/Zone3_Tier2/Cave/Ores/*:
    Silver = a thin vein in EVERY vanilla zone 1-4 (SilverPlacement Scale 0.0125, height 150-160, fillings Ore_Silver_Stone / _Sandstone / _Shale /
    _Volcanic) + Zone 3 alone has 8 extra cave Silver nodes (Zone3_Tier2/Cave/Ores/Silver/*) = most Silver in zone 3; Gold = zones 1-3 only
    (GoldPlacement Scale 0.03, height 102-110, Ore_Gold_Calcite) + Zone 3 cave Gold (8 nodes); NO Gold file in Ores/Zone4, no Ores/Zone5 at all.
    => the 0.4.24 weights stay (they were read from the same files): Silver 10,10,20,10,5 / Gold 8,8,15,3,3 (tenths; zone 4 / 5 keep a small
    chance: Skyy "found in all of them"). The STONES = the rocks the zone's vanilla ores sit in (the BlockMask of Ores/Zone<N>/*Placement.json) and
    what each drops (Server/Item/Items/Rock/<X>/Rock_<X>.json Gathering: Rock_Stone -> Rock_Stone_Cobble, Rock_Chalk -> itself; an ore block drops its ore
    + its host's cobble, e.g. Ore_Silver_Stone -> Ore_Silver + Rock_Stone_Cobble). Mods: nothing new (pie-clicker learn-only, 0.4.23). Nothing packed.
  1. SILVER / GOLD ON EVERY QUARRY: the click already rolled them per block (0.4.24); NEW: the quarry's SPIRITS find them too - every ore a spirit
    mines is one block: Silver / Gold at click.mine.spiritRarePercent (100) % of the click chance of that block (Lucky + Precious + the zone weight),
    whole items out of an exact running fraction (mining.i<n>.qsf, never a dice roll: settling twice never pays twice), into the quarry's storage
    (.drops) as Ore_Silver / Ore_Gold (their bars with the Smithy's Auto-Smelt), their Mining XP owed at once (ShMath.oweXp - as a spirit's other-ore
    share since 0.4.30: Collect pays no XP for .drops), collection credit when collected / linked (the bar = its ore). No Fortune on spirit finds
    (spirit ore has none either); clicks keep Fortune on every find.
  2. PRECIOUS FINDS = the quarry's 10th upgrade row (mining.i<n>.prec 0..click.mine.precMax (5)): + click.mine.precPermille (10 = 1 %) per level to the
    Silver / Gold chance ONLY (Lucky finds raises ore + Silver + Gold). Cost = what Lucky finds costs at that level (= Ore Amount's: coins of the coin
    curve x the island-size hours + the quarry's own Enchanted bar - self-sustaining, docs/answered/world.md 2026-11-21). A button carries the level the
    page showed (double click = once), a stale page / another profile buys nothing (ShPage.ckFresh + isBase), not enough = nothing paid
    (ShCore.purchaseM). The Lucky row and its message show the chance WITH Precious.
  3. THE ZONE'S STONE TYPES: every block still gives exactly 1 stone (storage use unchanged a block); it is the node's host cobble with
    click.mine.hostPercent (50) %, else one of the zone's other vanilla stones (equal shares):
      Zone 1  host Rock_Stone_Cobble   + Rock_Basalt_Cobble, Rock_Marble_Cobble     (Ores/Zone1 masks: Stone, Basalt, Marble, Chalk; fixer: Chalk left out -
              no SkyyCollections collection tracks Rock_Chalk, so it could never be credited)
      Zone 2  host Rock_Sandstone_Cobble + Rock_Sandstone_White_Cobble, Rock_Sandstone_Red_Cobble, Rock_Volcanic_Cobble (Ores/Zone2 masks)
      Zone 3  host Rock_Shale_Cobble   + Rock_Slate_Cobble, Rock_Basalt_Cobble, Rock_Stone_Cobble   (Ores/Zone3 masks: Shale, Slate, Basalt, Stone)
      Zone 4  host Rock_Magma_Cooled_Cobble / Rock_Volcanic_Cobble + Rock_Basalt_Cobble, Rock_Slate_Cobble, Rock_Quartzite_Cobble (Ores/Zone4 masks)
      Zone 5  host Rock_Stone_Cobble / Rock_Basalt_Cobble + Rock_Volcanic_Cobble, Rock_Magma_Cooled_Cobble, Rock_Basalt_Cobble (no vanilla Zone 5 ores:
              the volcanic rocks of Zone 4's mask)
    A click picks each block's stone on its own random stream (the ore / Silver / Gold rolls are 0.4.33's exactly); SPIRITS bring
    click.mine.spiritStonePercent (100) % of a stone per ore they mine (vanilla: an ore block drops ore + host cobble), split host / others by an
    exact rotation (mining.i<n>.qsf). The good finds take the storage room first, then ore, then stone (as 0.4.24); a spirit batch that fills the
    storage keeps room for its blocks' stone + finds (ShMath.qCap: ore = room / (1 + stone + Silver + Gold chance an ore)). Collection credit = the stone's
    own id (as the cobble since 0.4.24); no XP for stone (as the cobble).
  4. AUTO-COMPACTOR ON THE QUARRY'S STORAGE: with an Auto-Compactor (I+) every full 100 of a stone WITH an Enchanted form (SkyyCollections:
    Cobblestone, Sandstone, Shale, Slate, Basalt, Volcanic, Marble, Quartzite) and of Silver / Gold BARS (Enchanted Silver / Gold Ingot) in .drops
    becomes 1 Enchanted item; against the storage it counts 100 ALWAYS (fixer: a .drops item counts 1 against the plain cap and against the x 100
    compressing limit alike, so 1 Enchanted = 100 in both; with Smithy off the island does not compress, and an Enchanted stone counting 1 would have
    been free room), Collect / a grid cell /
    Shard Link give the Enchanted item and credit 100 of its base (a bar = its ore). White / Red Sandstone, Chalk, Cooled Magma, raw Silver / Gold
    ore and the quarry's own ore bars stay as they are (no Enchanted form / unchanged).
    CREDIT (fixer): ShCore.owedAs / ShLink.credAs turn ANY ShMath.DC_E id in .drops into 100 of its base - right for every writer (RATIO 100 is
    fixed, tools/skyyench.py; a legacy Enchanted item a Shard Link puts back into .drops is 100 base too); only ShMath.dcCompact writes DC_E ids
    today. Rock_Magma_Cooled_Cobble (the Zone 4 Adamantite host since 0.4.24, a Zone 5 stone) credits as Rock_Magma_Cooled - SkyyCollections 0.2.36
    Volcanic tracks the block, not the cobble (before: a refused credit that waited forever as owed.coll).
  5. Other shards and other clickers: unchanged (every new path asks kd == Mining). MQ34_OFF_TEST (harness only) = 0.4.33's quarry exactly.
  NUMBERS (new, Server Setup -> Shards -> Shard clicker; all editable, live):
    click.mine.precPermille 10 (1/1000 per Precious level), click.mine.precMax 5, click.mine.hostPercent 50 (%), click.mine.spiritStonePercent 100 (%),
    click.mine.spiritRarePercent 100 (%). Unchanged and reused: click.mine.rarePermille 10, click.mine.rareLuck 10, click.mine.silverWeight
    10,10,20,10,5, click.mine.goldWeight 8,8,15,3,3.
    Silver / Gold a block (rarePermille + 10 x Lucky + 10 x Precious) / 1000 x weight / 10:
      Zone            1      2      3      4      5
      Silver Lv 0     1 %    1 %    2 %    1 %    0.5 %
      Silver P5       6 %    6 %   12 %    6 %    3 %      (Precious 5, Lucky 0)
      Silver L5+P5   11 %   11 %   22 %   11 %    5.5 %
      Gold Lv 0       0.8 %  0.8 %  1.5 %  0.3 %  0.3 %
      Gold P5         4.8 %  4.8 %  9 %    1.8 %  1.8 %
      Gold L5+P5      8.8 %  8.8 % 16.5 %  3.3 %  3.3 %
    Precious finds cost (= Lucky finds = Ore Amount at that level): coins = ShIsl.coins(subH(size, level), the zone's coin curve) + ShIsl.mats(the
      quarry's Enchanted bar, size, level) - the exact numbers per quarry are on the row (have / need lines).
  SAVED DATA: mining.i<n>.prec (0-5; missing = 0), mining.i<n>.qsf ("silver fraction;gold fraction;stone hundredths;rotation" - the spirits' running
    counts), Enchanted stone / Silver / Gold ingot entries inside mining.i<n>.drops. No migration (old files load unchanged). The 0.4.30 zone fold knows
    both keys (prec = the higher, qsf dropped with the folded island).
  ROLLBACK 0.4.34 -> 0.4.33 alone: the jar. 0.4.33 ignores prec / qsf (kept in the file; Precious levels come back on roll-forward, nothing refunded);
    new stones, Silver / Gold and Enchanted stones already in storage stay and Collect / Shard Link pay them (an Enchanted stone then credits 1
    collection count instead of 100 and counts 1 against storage - Collect all on the Mining Shard first to keep the credit exact).
"""
import os, sys

HERE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "SkyyShards")
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "tools"))
import soundpass_gen as G

P = G.Patch(os.path.join(HERE, "build_skyyshards_0.4.33.py"), os.path.join(HERE, "build_skyyshards_0.4.34.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.4.33"\n') and P.has("GENERATED by tools/shards_0_4_33_patch.py") and P.has('lnk = mk("ShLink")') and not P.has("quarryExtra"), \
    "not the generated SkyyShards 0.4.33"
REG0, SYS0 = P.s.count("registerCommand("), P.s.count("registerSystem(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.4.34 (2026-11-24)"):].rstrip() + "\n"

# ---------------------------------------------------------------------------------------------------- 0. header + version
P.rep('''"""SkyyShards 0.4.33 - build script (javassist via jpype). GENERATED by tools/shards_0_4_33_patch.py from build_skyyshards_0.4.32.py
(generated by tools/shards_0_4_32_patch.py from 0.4.31, ... back to tools/shards_0_4_patch.py from 0.3.2; edit the patch, never this file).
Changes are marked "0.4.33" /''', '''"""SkyyShards 0.4.34 - build script (javassist via jpype). GENERATED by tools/shards_0_4_34_patch.py from build_skyyshards_0.4.33.py
(generated by tools/shards_0_4_33_patch.py from 0.4.32, ... back to tools/shards_0_4_patch.py from 0.3.2; edit the patch, never this file).
Changes are marked "0.4.34" / "0.4.33" /''')
P.rep('''Run:   python SkyyShards/build_skyyshards_0.4.33.py   -> SkyyShards/SkyyShards-0.4.33.jar   (never --deploy: tools/deploy_set.py installs the set)
Check: python SkyyShards/test_skyyshards_0.4.33.py
''', '''Run:   python SkyyShards/build_skyyshards_0.4.34.py   -> SkyyShards/SkyyShards-0.4.34.jar   (never --deploy: tools/deploy_set.py installs the set)
Check: python SkyyShards/test_skyyshards_0.4.34.py
''' + NOTE)
P.rep('VERSION = "0.4.33"\n', 'VERSION = "0.4.34"\n')

# ---------------------------------------------------------------------------------------------------- 1. ShCfg: the five new rows
P.rep('''          "public static volatile int MQ_ALLOY_DEF = 50;", "public static volatile int MQ_ALLOY_STEP = 10;",
''', '''          "public static volatile int MQ_ALLOY_DEF = 50;", "public static volatile int MQ_ALLOY_STEP = 10;",
          "public static volatile int MQ_PREC = 10;", "public static volatile int MQ_PREC_MAX = 5;", "public static volatile int MQ_HOST = 50;",   # 0.4.34
          "public static volatile int MQ_SP_STONE = 100;", "public static volatile int MQ_SP_RARE = 100;",   # 0.4.34: the spirits' stone + Silver / Gold
          "public static volatile boolean MQ34_OFF_TEST = false;",   # 0.4.34 harness only: true = the 0.4.33 quarry exactly (the older phases)
''')
P.rep('''          "  MQ_ALLOY_STEP = intOf(p.getProperty(\\"click.mine.alloyStep\\"), 10, 1, 100);",
''', '''          "  MQ_ALLOY_STEP = intOf(p.getProperty(\\"click.mine.alloyStep\\"), 10, 1, 100);",
          "  MQ_PREC = intOf(p.getProperty(\\"click.mine.precPermille\\"), 10, 0, 1000);",   # 0.4.34
          "  MQ_PREC_MAX = intOf(p.getProperty(\\"click.mine.precMax\\"), 5, 0, 5);",
          "  MQ_HOST = intOf(p.getProperty(\\"click.mine.hostPercent\\"), 50, 0, 100);",
          "  MQ_SP_STONE = intOf(p.getProperty(\\"click.mine.spiritStonePercent\\"), 100, 0, 100);",
          "  MQ_SP_RARE = intOf(p.getProperty(\\"click.mine.spiritRarePercent\\"), 100, 0, 100);",
''')
P.rep('''          "The highest Lucky finds level (each costs what Ore Amount costs at that level).", "reload@config.properties:click.mine.luckMax"),
''', '''          "The highest Lucky finds level (each costs what Ore Amount costs at that level).", "reload@config.properties:click.mine.luckMax"),
         ("click.mine.precPermille", "Quarry: Silver / Gold per Precious", "clicker", "int", "10", "0", "1000", "", "", "live",   # 0.4.34
          "More Silver / Gold chance (1/1000) per Precious finds level (ore stays).", "reload@config.properties:click.mine.precPermille"),
         ("click.mine.precMax", "Quarry: Precious finds levels", "clicker", "int", "5", "0", "5", "", "", "live",
          "The highest Precious finds level (each costs what Lucky finds costs at that level).", "reload@config.properties:click.mine.precMax"),
         ("click.mine.hostPercent", "Quarry: node's own stone share", "clicker", "int", "50", "0", "100", "", "%", "live",
          "Share of mined blocks that give the ore's own rock; the rest give the zone's other stones.", "reload@config.properties:click.mine.hostPercent"),
         ("click.mine.spiritStonePercent", "Quarry: spirit stone per ore", "clicker", "int", "100", "0", "100", "", "%", "live",
          "Stone a spirit brings per ore it mines (100 = 1 stone, like a vanilla ore block).", "reload@config.properties:click.mine.spiritStonePercent"),
         ("click.mine.spiritRarePercent", "Quarry: spirit Silver / Gold", "clicker", "int", "100", "0", "100", "", "%", "live",
          "Spirits find Silver / Gold at this % of a click's chance a block.", "reload@config.properties:click.mine.spiritRarePercent"),
''')

# ---------------------------------------------------------------------------------------------------- 2. ShMath: the quarry storage's Enchanted forms + the use
QZ_HOSTS = ["Rock_Stone_Cobble", "Rock_Sandstone_Cobble", "Rock_Shale_Cobble", "Rock_Magma_Cooled_Cobble", "Rock_Volcanic_Cobble", "Rock_Basalt_Cobble"]
P.rep('''# the limit + the use in the same unit: base items x 100 while compressing, else 1 Enchanted = 1 item against the plain cap
''', '''# 0.4.34 (tools/shards_0_4_34_patch.py) THE QUARRY'S STONES: each zone's other vanilla stones (the rocks its vanilla ores sit in: the BlockMask of
# Assets.zip Server/World/Default/Ores/Zone<N>/*Placement.json; what each drops: Server/Item/Items/Rock/<X>/Rock_<X>.json). Zone 5 has no vanilla
# ores file: the volcanic rocks. A block's stone = its node's host cobble (click.mine.hostPercent) or one of these.
QZ_EXTRA = [["Rock_Basalt_Cobble", "Rock_Marble_Cobble"],   # fixer: no Rock_Chalk (in the Zone 1 masks, but no SkyyCollections collection: never creditable)
            ["Rock_Sandstone_White_Cobble", "Rock_Sandstone_Red_Cobble", "Rock_Volcanic_Cobble"],
            ["Rock_Slate_Cobble", "Rock_Basalt_Cobble", "Rock_Stone_Cobble"],
            ["Rock_Basalt_Cobble", "Rock_Slate_Cobble", "Rock_Quartzite_Cobble"],
            ["Rock_Volcanic_Cobble", "Rock_Magma_Cooled_Cobble", "Rock_Basalt_Cobble"]]
QZ_HOSTS = %r
assert all(_s in ITEMS for _z in QZ_EXTRA for _s in _z) and all(_s in ITEMS for _s in QZ_HOSTS), "0.4.34: every quarry stone is a vanilla item"
assert all(1 <= len(_z) <= 6 and 60 %% len(_z) == 0 for _z in QZ_EXTRA), "0.4.34: the spirits' rotation (mod 6000) needs a zone list of 1..6 dividing 60"
# the quarry storage's Enchanted forms (SkyyCollections, tools/skyyench.py): the stones that have one + Silver / Gold bars (Enchanted ingots)
QDC = [(_b, _ENCHB48[_b]) for _b in sorted(set(QZ_HOSTS + sum(QZ_EXTRA, []))) + ["Ingredient_Bar_Silver", "Ingredient_Bar_Gold"] if _b in _ENCHB48]
assert sorted(_b for _b, _e in QDC) == sorted(["Rock_Basalt_Cobble", "Rock_Marble_Cobble", "Rock_Quartzite_Cobble", "Rock_Sandstone_Cobble", "Rock_Shale_Cobble",
                                               "Rock_Slate_Cobble", "Rock_Stone_Cobble", "Rock_Volcanic_Cobble", "Ingredient_Bar_Silver", "Ingredient_Bar_Gold"]), QDC
F(mth, "public static final String[] DC_B = new String[] { %%s };" %% ", ".join(jlit(_b) for _b, _e in QDC))
F(mth, "public static final String[] DC_E = new String[] { %%s };" %% ", ".join(jlit(_e) for _b, _e in QDC))
M(mth, r"""
public static String dcBase(String id) {
  if (id == null || id.length() == 0) return null;
  for (int i = 0; i < DC_E.length; i++) if (id.equals(DC_E[i])) return DC_B[i];
  return null;
}""")
# the Enchanted quarry items in an island's .drops (each counts 100 against the storage while it compresses, as compressed stock does)
M(mth, r"""
public static long dcHeld(int kd, java.util.Properties p, int slot) {
  if (@PKG@.ShStore.str(p, ik(kd, slot, "drops")).length() == 0) return 0L;
  java.util.LinkedHashMap m = held(kd, p, slot);
  long t = 0L;
  for (int i = 0; i < DC_E.length; i++) { Object o = m.get(DC_E[i]); if (o instanceof Long) t += ((Long) o).longValue(); }
  return t;
}""")
# every full 100 of a stone / Silver / Gold bar -> 1 Enchanted item (the map only; the caller saves); returns the Enchanted items made
M(mth, r"""
public static long dcCompact(java.util.LinkedHashMap m) {
  if (m == null) return 0L;
  long made = 0L;
  for (int i = 0; i < DC_B.length; i++) {
    Object o = m.get(DC_B[i]);
    long n = o instanceof Long ? ((Long) o).longValue() : 0L;
    if (n < 100L) continue;
    long e = n / 100L;
    long r = n %% 100L;
    if (r > 0L) m.put(DC_B[i], Long.valueOf(r)); else m.remove(DC_B[i]);
    Object q = m.get(DC_E[i]);
    m.put(DC_E[i], Long.valueOf((q instanceof Long ? ((Long) q).longValue() : 0L) + e));
    made += e;
  }
  return made;
}""")
# the limit + the use in the same unit: base items x 100 while compressing, else 1 Enchanted = 1 item against the plain cap
''' % QZ_HOSTS)
P.rep('''  s += heldN(kd, p, slot);   // 0.4.22: a Combat island's rolled drops use its storage too
''', '''  s += heldN(kd, p, slot);   // 0.4.22: a Combat island's rolled drops use its storage too
  s += 99L * dcHeld(kd, p, slot);   // 0.4.34 (+ fixer): an Enchanted stone / ingot in the quarry's storage = 100 in BOTH units (a .drops item counts 1 against cap or cap x 100 alike) - never free room
''')

# ---------------------------------------------------------------------------------------------------- 3. ShMath.settle: the spirits' stone + Silver / Gold
P.rep('''M(mth, "public static long oreShare(int kd, java.util.Properties p, int slot, long made) { return 0L; }")''',
      '''M(mth, "public static long oreShare(int kd, java.util.Properties p, int slot, long made) { return 0L; }")
M(mth, "public static long quarryExtra(int kd, java.util.Properties p, int slot, long made, long room) { return 0L; }")   # 0.4.34: the body is set below (after ShClk) - the spirits' stone + Silver / Gold
M(mth, "public static long qCap(int kd, java.util.Properties p, int slot, long room) { return room; }")   # 0.4.34: the body is set below - a full quarry keeps room for the spirits' stone + finds''')
P.rep('''      made = lim - use; last = now;
''', '''      made = qCap(kd, p, slot, lim - use); last = now;   // 0.4.34: a Mining quarry keeps the room its spirits' stone + Silver / Gold need
''')
P.rep('''    stored += made - shr;   // 0.4.30 fixer: a Mining quarry's other ores' share goes to its storage (.drops) as that ore
''', '''    stored += made - shr;   // 0.4.30 fixer: a Mining quarry's other ores' share goes to its storage (.drops) as that ore
    quarryExtra(kd, p, slot, made, lim - use - made);   // 0.4.34: a Mining quarry's spirits bring stone + Silver / Gold into what room is left
''')

# ---------------------------------------------------------------------------------------------------- 4. ShClk: Precious, the stones, the click
P.rep('''M(ckc, r"""
public static String qName(String id) {''', r'''# ---- 0.4.34 (tools/shards_0_4_34_patch.py) PRECIOUS FINDS + THE ZONE'S STONES
for f in ("public static final String[] ZS_ID = new String[] { %s };" % ", ".join(jlit(_s) for _z in QZ_EXTRA for _s in _z),
          "public static final int[] ZS_A = new int[] { %s };" % ", ".join(str(sum(len(_z) for _z in QZ_EXTRA[:_i])) for _i in range(len(QZ_EXTRA) + 1)),
          "public static volatile java.util.Random RND2_TEST = null;",
          "public static final java.util.concurrent.atomic.AtomicLong SPX = new java.util.concurrent.atomic.AtomicLong();",   # spirit stone + finds added
          "public static final java.util.concurrent.atomic.AtomicLong DCM = new java.util.concurrent.atomic.AtomicLong();"):   # Enchanted items compacted
    F(ckc, f)
M(ckc, r"""
public static double rnd2() {
  java.util.Random r = RND2_TEST;
  return r != null ? r.nextDouble() : Math.random();
}""")
M(ckc, "public static int prec(java.util.Properties p, int kd, int slot) { int m = @PKG@.ShCfg.MQ_PREC_MAX; return @PKG@.ShStore.intv(p, @PKG@.ShMath.ik(kd, slot, \"prec\"), 0, 0, m < 0 ? 0 : (m > 5 ? 5 : m)); }")
M(ckc, "public static int hostPct() { return @PKG@.ShCfg.MQ34_OFF_TEST ? 100 : @PKG@.ShCfg.MQ_HOST; }")
M(ckc, "public static boolean dcOn(int kd, java.util.Properties p, int slot) { return kd == MK && !@PKG@.ShCfg.MQ34_OFF_TEST && @PKG@.ShMath.compactor(kd, p) >= 1; }")   # any Auto-Compactor
# the Silver / Gold chance a block with Precious finds (pr levels; rareP = Precious 0)
M(ckc, r"""
public static double rareQ(int lk, int pr, int z, boolean gold) {
  int[] w = gold ? @PKG@.ShCfg.MQ_GW : @PKG@.ShCfg.MQ_SW;
  int zi = z < 1 ? 0 : z - 1;
  double wt = w == null || w.length == 0 ? 0.0 : (double) w[zi < w.length ? zi : w.length - 1] / 10.0;
  int pp = @PKG@.ShCfg.MQ34_OFF_TEST ? 0 : @PKG@.ShCfg.MQ_PREC;
  double c = ((double) @PKG@.ShCfg.MQ_RARE + (double) @PKG@.ShCfg.MQ_RARE_LUCK * (double) (lk < 0 ? 0 : lk) + (double) pp * (double) (pr < 0 ? 0 : pr)) / 1000.0 * wt;
  return c < 0.0 ? 0.0 : (c > 1.0 ? 1.0 : c);
}""")
M(ckc, "public static int zsN(int z) { int zi = z < 1 ? 0 : (z > 5 ? 4 : z - 1); return ZS_A[zi + 1] - ZS_A[zi]; }")
M(ckc, "public static String zsId(int z, int j) { int zi = z < 1 ? 0 : (z > 5 ? 4 : z - 1); return ZS_ID[ZS_A[zi] + j]; }")
# the exact rotation of the spirits' stones: of blocks [0, x) hostCnt are the host's; the others go to the zone's stones in turn
M(ckc, "public static long hostCnt(long x, int hp) { return (x / 100L) * (long) hp + (x % 100L < (long) hp ? x % 100L : (long) hp); }")
M(ckc, "public static long extCnt(long g, int e, int j) { return g / (long) e + ((g % (long) e) > (long) j ? 1L : 0L); }")
M(ckc, r"""
public static void addTo0(java.util.LinkedHashMap m, String id, long d) {
  if (id == null || id.length() == 0 || d <= 0L) return;
  Object o = m.get(id);
  m.put(id, Long.valueOf((o instanceof Long ? ((Long) o).longValue() : 0L) + d));
}""")
# a click's n stones: the host's share, the rest one of the zone's stones each - on the second random stream (the ore / Silver / Gold rolls stay 0.4.33's)
M(ckc, r"""
public static void stones(java.util.LinkedHashMap m, String host, int z, long n) {
  if (n <= 0L) return;
  int hp = hostPct();
  int e = zsN(z);
  if (hp >= 100 || e <= 0) { addTo0(m, host, n); return; }
  for (long b = 0L; b < n && b < 100000L; b++) {
    if (rnd2() * 100.0 < (double) hp) addTo0(m, host, 1L);
    else {
      int j = (int) (rnd2() * (double) e);
      if (j >= e) j = e - 1;
      if (j < 0) j = 0;
      addTo0(m, zsId(z, j), 1L);
    }
  }
}""")
# the spirits' stones (n of them, from the rotation c): into m; returns the next rotation (mod 6000 - every zone list of 1..6 divides 60)
M(ckc, r"""
public static long stonesAt(java.util.LinkedHashMap m, String host, int z, long n, long c) {
  if (n <= 0L) return c;
  int hp = hostPct();
  int e = zsN(z);
  if (hp >= 100 || e <= 0) { addTo0(m, host, n); return c; }
  long c1 = c + n;
  addTo0(m, host, hostCnt(c1, hp) - hostCnt(c, hp));
  long g0 = c - hostCnt(c, hp);
  long g1 = c1 - hostCnt(c1, hp);
  for (int j = 0; j < e; j++) addTo0(m, zsId(z, j), extCnt(g1, e, j) - extCnt(g0, e, j));
  return c1 % 6000L;
}""")
# 0.4.34 THE SPIRITS' STONE + SILVER / GOLD (settle, under ShStore.LOCK): every ore the quarry's spirits made = one mined block: stone
# (click.mine.spiritStonePercent of one, the exact rotation host / the zone's stones) + Silver / Gold at click.mine.spiritRarePercent of the click
# chance, whole items of an exact running fraction (mining.i<n>.qsf = "silver;gold;stone hundredths;rotation"), into what room is left (good finds
# first), their Mining XP owed at once (Collect pays none for .drops); the Auto-Compactor while it compresses. Returns the items added.
mth.getDeclaredMethod("quarryExtra").setBody(jv(r"""{
  int kd = $1;
  java.util.Properties p = $2;
  int slot = $3;
  long made = $4;
  long room = $5;
  if (kd != @PKG@.ShClk.MK || made <= 0L || @PKG@.ShCfg.MQ34_OFF_TEST || p == null) return 0L;
  int t = @PKG@.ShIsl.ty(kd, p, slot);
  if (t < 0 || !@PKG@.ShClk.isBase(p, kd, slot)) return 0L;
  int oi = t - @PKG@.ShIsl.LAD0[kd];
  if (oi < 0 || oi >= @PKG@.ShClk.Q_COB.length) return 0L;
  int z = @PKG@.ShIsl.zoneOf(t);
  int sp = @PKG@.ShCfg.MQ_SP_STONE;
  int sr = @PKG@.ShCfg.MQ_SP_RARE;
  int lk = @PKG@.ShClk.luck(p, kd, slot);
  int pr = @PKG@.ShClk.prec(p, kd, slot);
  double ps = @PKG@.ShClk.rareQ(lk, pr, z, false) * (double) sr / 100.0;
  double pg = @PKG@.ShClk.rareQ(lk, pr, z, true) * (double) sr / 100.0;
  String fk = ik(kd, slot, "qsf");
  String[] f = @PKG@.ShStore.str(p, fk).split(";");
  double fs = 0.0; double fg = 0.0; long cs = 0L; long cc = 0L;
  try { if (f.length >= 4) { fs = Double.parseDouble(f[0]); fg = Double.parseDouble(f[1]); cs = Long.parseLong(f[2]); cc = Long.parseLong(f[3]); } } catch (Throwable x) { fs = 0.0; fg = 0.0; cs = 0L; cc = 0L; }
  if (!(fs >= 0.0 && fs < 1.0)) fs = 0.0;
  if (!(fg >= 0.0 && fg < 1.0)) fg = 0.0;
  if (cs < 0L || cs > 99L) cs = 0L;
  if (cc < 0L || cc >= 6000L) cc = 0L;
  double xs = (double) made * ps + fs;
  long ns = (long) Math.floor(xs + 0.000000001);
  fs = xs - (double) ns;
  if (fs < 0.0) fs = 0.0;
  double xg = (double) made * pg + fg;
  long ng = (long) Math.floor(xg + 0.000000001);
  fg = xg - (double) ng;
  if (fg < 0.0) fg = 0.0;
  long sh = made * (long) (sp < 0 ? 0 : sp) + cs;
  long nst = sh / 100L;
  cs = sh % 100L;
  long rm = room < 0L ? 0L : room;
  long gG = ng < rm ? ng : rm; rm = rm - gG;
  long gS = ns < rm ? ns : rm; rm = rm - gS;
  long gC = nst < rm ? nst : rm;
  long add = gG + gS + gC;
  if (add > 0L) {
    boolean sm = @PKG@.ShTotem.smelts(kd, p, slot);
    java.util.LinkedHashMap m = held(kd, p, slot);
    @PKG@.ShClk.addTo0(m, sm ? @PKG@.ShClk.R_BAR[1] : @PKG@.ShClk.R_ORE[1], gG);
    @PKG@.ShClk.addTo0(m, sm ? @PKG@.ShClk.R_BAR[0] : @PKG@.ShClk.R_ORE[0], gS);
    cc = @PKG@.ShClk.stonesAt(m, @PKG@.ShClk.Q_COB[oi], z, gC, cc);
    if (@PKG@.ShClk.dcOn(kd, p, slot)) @PKG@.ShClk.DCM.addAndGet(dcCompact(m));
    heldSet(kd, p, slot, m);
    if (gS + gG > 0L) oweXp(kd, p, slot, gS + gG);
    @PKG@.ShClk.SPX.addAndGet(add);
  }
  p.setProperty(fk, String.valueOf(fs) + ";" + String.valueOf(fg) + ";" + cs + ";" + cc);
  return add;
}"""))
# a storage that fills: the ore part of the room left (room / (1 + stone + Silver + Gold an ore)) - the rest for what the ore's blocks bring
mth.getDeclaredMethod("qCap").setBody(jv(r"""{
  int kd = $1;
  java.util.Properties p = $2;
  int slot = $3;
  long room = $4;
  if (kd != @PKG@.ShClk.MK || room <= 0L || @PKG@.ShCfg.MQ34_OFF_TEST || p == null) return room;
  int t = @PKG@.ShIsl.ty(kd, p, slot);
  if (t < 0 || !@PKG@.ShClk.isBase(p, kd, slot)) return room;
  int z = @PKG@.ShIsl.zoneOf(t);
  int lk = @PKG@.ShClk.luck(p, kd, slot);
  int pr = @PKG@.ShClk.prec(p, kd, slot);
  double sr = (double) @PKG@.ShCfg.MQ_SP_RARE / 100.0;
  double per = 1.0 + (double) (@PKG@.ShCfg.MQ_SP_STONE < 0 ? 0 : @PKG@.ShCfg.MQ_SP_STONE) / 100.0 + (@PKG@.ShClk.rareQ(lk, pr, z, false) + @PKG@.ShClk.rareQ(lk, pr, z, true)) * sr;
  long m = (long) Math.floor((double) room / per + 0.000000001);
  return m < 0L ? 0L : (m > room ? room : m);
}"""))
M(ckc, r"""
public static String qName(String id) {''')
# the click: Precious in the chance, the zone's stones, the storage's Enchanted forms, the message
P.rep('''    double ps = rareP(lk, z, false);
    double pg = rareP(lk, z, true);
''', '''    int pr = prec(p, kd, slot);   // 0.4.34: Precious finds
    double ps = rareQ(lk, pr, z, false);
    double pg = rareQ(lk, pr, z, true);
''')
P.rep('''  String oreOut; String silOut; String golOut; String cobOut = Q_COB[oi]; String aId = ""; String aA = ""; String aB = "";
''', '''  String oreOut; String silOut; String golOut; String cobOut = Q_COB[oi]; String aId = ""; String aA = ""; String aB = "";
  java.util.LinkedHashMap stn = new java.util.LinkedHashMap();   // 0.4.34: the stones this node gave (host + the zone's)
''')
P.rep('''    addTo(m, oreOut, gO);
    addTo(m, cobOut, gC);
''', '''    addTo(m, oreOut, gO);
    stones(stn, cobOut, z, gC);   // 0.4.34: the host's share + the zone's other stones (gC in all)
    java.util.Iterator sti = stn.entrySet().iterator();
    while (sti.hasNext()) { java.util.Map.Entry se = (java.util.Map.Entry) sti.next(); addTo(m, (String) se.getKey(), ((Long) se.getValue()).longValue()); }
''')
P.rep('''        addTo(m, aId, (long) ALLOY_OUT * pairs);
      }
    }
    @PKG@.ShMath.heldSet(kd, p, slot, m);
''', '''        addTo(m, aId, (long) ALLOY_OUT * pairs);
      }
    }
    if (dcOn(kd, p, slot)) DCM.addAndGet(@PKG@.ShMath.dcCompact(m));   // 0.4.34: the Auto-Compactor on the quarry's stones / Silver / Gold bars
    @PKG@.ShMath.heldSet(kd, p, slot, m);
''')
P.rep('''  part(sb, gC, cobOut);
  String al = pairs > 0L''', '''  java.util.Iterator stj = stn.entrySet().iterator();   // 0.4.34: every stone kind
  while (stj.hasNext()) { java.util.Map.Entry se = (java.util.Map.Entry) stj.next(); part(sb, ((Long) se.getValue()).longValue(), (String) se.getKey()); }
  String al = pairs > 0L''')
P.rep(''' : "+" + @PKG@.ShCfg.num(gC) + " " + qName(cobOut)));
  @PKG@.ShSnd.ok(u, r, 0);''', ''' : "+" + @PKG@.ShCfg.num(gC) + " " + (stn.size() <= 1 ? qName(cobOut) : "stone")));   // 0.4.34
  @PKG@.ShSnd.ok(u, r, 0);''')
# Lucky's message shows the chance with Precious
P.rep('''      + @PKG@.ShCfg.dec(rareP(nl, z, false) * 100.0) + " %, Gold " + @PKG@.ShCfg.dec(rareP(nl, z, true) * 100.0) + " %.";''',
      '''      + @PKG@.ShCfg.dec(rareQ(nl, prec(p, kd, slot), z, false) * 100.0) + " %, Gold " + @PKG@.ShCfg.dec(rareQ(nl, prec(p, kd, slot), z, true) * 100.0) + " %.";   // 0.4.34: with Precious''')
# buyPrec: Lucky finds' pattern (the seen level, isBase, purchaseM), key mining.i<n>.prec, Lucky's cost at that level
P.rep('''# ---- 0.4.30 THE ORE UPGRADE (Skyy 2026-11-22''', '''# ---- 0.4.34 PRECIOUS FINDS (mining.i<n>.prec): + click.mine.precPermille Silver / Gold a level; costs what Lucky finds costs at that level
M(ckc, r"""
public static String buyPrec(java.util.UUID u, String k, int kd, int slot, int seen, @IC@[] cs) {
  if (!@PKG@.ShCfg.ON || !@PKG@.ShCfg.CK_ON || !@PKG@.ShCfg.MQ_ON) return "-The Mining quarry is switched off on this server.";
  if (kd != MK) return "-Precious finds is a Mining quarry upgrade.";
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "-This shard's file could not be read.";
  if (cs == null) return "-Your inventory could not be read - try again.";
  String no = @PKG@.ShCore.gateOwn(u, k, kd, p);
  if (no != null) return no;
  int t0; int lv; int sz; int lk; long ver;
  @PKG@.ShStore.LOCK.lock(); try {
    if (slot < 0 || slot >= @PKG@.ShMath.SLOTS || !@PKG@.ShMath.hasIsland(kd, p, slot)) return "-That island is not yours yet.";
    if (!isBase(p, kd, slot)) return "=The page is up to date now - open the quarry again.";
    t0 = @PKG@.ShIsl.ty(kd, p, slot);
    lv = prec(p, kd, slot);
    lk = luck(p, kd, slot);
    sz = @PKG@.ShMath.size(kd, p, slot);
    ver = @PKG@.ShStore.ver(k);
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (seen >= 0 && seen != lv) return "=The page is up to date now - click Upgrade again.";
  int mx = @PKG@.ShCfg.MQ_PREC_MAX;
  if (lv >= mx) return "=Precious finds is at its highest level.";
  double cv = @PKG@.ShCfg.curve(@PKG@.ShIsl.band(@PKG@.ShIsl.TIER[t0]));
  int nl = lv + 1;
  String r = @PKG@.ShCore.purchaseM(u, k, kd, p, cs, @PKG@.ShIsl.mats(kd, t0, @PKG@.ShCombat.subMat(kd, 0), sz - 1, (long) nl), @PKG@.ShIsl.coins(@PKG@.ShIsl.subH(sz, nl), cv),
                                    new String[] { @PKG@.ShMath.ik(kd, slot, "prec") }, new String[] { String.valueOf(nl) }, "prec",
                                    @PKG@.ShKind.KEYS[kd] + " prec slot " + slot + " " + @PKG@.ShIsl.KEY[t0] + " " + lv + " -> " + nl, ver);
  if (r != null) return r;
  int z = @PKG@.ShIsl.zoneOf(t0);
  String ok = "+Precious finds " + nl + "/" + mx + " on the Zone " + z + " quarry: Silver " + @PKG@.ShCfg.dec(rareQ(lk, nl, z, false) * 100.0)
      + " % a block, Gold " + @PKG@.ShCfg.dec(rareQ(lk, nl, z, true) * 100.0) + " %.";
  @PKG@.ShSnd.ok(u, ok, 2);
  return ok;
}""")
# ---- 0.4.30 THE ORE UPGRADE (Skyy 2026-11-22''')

# ---------------------------------------------------------------------------------------------------- 5. the 0.4.30 fold knows the new keys
P.rep('''F(st, 'public static final String[] MZ_KEEP = new String[] { "size", "amt", "deco", "irr", "nsize", "luck", "smithy", "alloyPct", "totems", "stored", "legacy", "drops", "seed", "ench", "ores", "eternal" };')''',
      '''F(st, 'public static final String[] MZ_KEEP = new String[] { "size", "amt", "deco", "irr", "nsize", "luck", "smithy", "alloyPct", "totems", "stored", "legacy", "drops", "seed", "ench", "ores", "eternal", "prec" };')   # 0.4.34: + Precious finds''')
P.rep('''"seeded", "arena", "xpn", "xpw", "orr", "xpr" };')''', '''"seeded", "arena", "xpn", "xpw", "orr", "xpr", "qsf" };')   # 0.4.34: + the spirits' running fractions''')
P.rep('''  String[] mx = new String[] { "nsize", "luck", "smithy" };''', '''  String[] mx = new String[] { "nsize", "luck", "smithy", "prec" };   // 0.4.34: + Precious finds''')

# ---------------------------------------------------------------------------------------------------- 6. the credit of an Enchanted stone / ingot = 100 of its base
P.rep('''public static long owedAs(java.util.UUID u, String id, long c) {
  if (id == null || c <= 0L) return 0L;
''', '''public static long owedAs(java.util.UUID u, String id, long c) {
  if (id == null || c <= 0L) return 0L;
  String db = @PKG@.ShMath.dcBase(id);   // 0.4.34: an Enchanted stone / Silver / Gold ingot from the quarry's storage = 100 of its base
  if (db != null) { id = db; c = c * 100L; }
  if ("Rock_Magma_Cooled_Cobble".equals(id)) id = "Rock_Magma_Cooled";   // fixer: SkyyCollections' Volcanic tracks the block, not its cobble
''')
P.rep('''public static void credAs(java.util.UUID u, String id, long c, java.util.LinkedHashMap m) {
  if (id == null || c <= 0L) return;
''', '''public static void credAs(java.util.UUID u, String id, long c, java.util.LinkedHashMap m) {
  if (id == null || c <= 0L) return;
  String db = @PKG@.ShMath.dcBase(id);   // 0.4.34: as ShCore.owedAs
  if (db != null) { id = db; c = c * 100L; }
  if ("Rock_Magma_Cooled_Cobble".equals(id)) id = "Rock_Magma_Cooled";   // fixer: SkyyCollections' Volcanic tracks the block, not its cobble
''')

# ---------------------------------------------------------------------------------------------------- 7. the quarry page: row 9 Precious finds
P.rep('''  this.ckUpL = new String[9]; this.ckUpE = new String[9]; this.ckUpC = new String[9]; this.ckUpOk = new boolean[9]; this.ckUpSeen = new int[9];   // 0.4.30: + row 8 Ores
  for (int i = 0; i < 9; i++) {''', '''  this.ckUpL = new String[10]; this.ckUpE = new String[10]; this.ckUpC = new String[10]; this.ckUpOk = new boolean[10]; this.ckUpSeen = new int[10];   // 0.4.30: + row 8 Ores; 0.4.34: + row 9 Precious finds
  for (int i = 0; i < 10; i++) {''')
P.rep('''  int t = -1; int z = 0; int sz = 0; int amt = 0; int deco = 0; int irr = 0; int ns = 0; int tot = 0; int lk = 0; int smy = 0; int pct = 0; boolean pole = false;
''', '''  int t = -1; int z = 0; int sz = 0; int amt = 0; int deco = 0; int irr = 0; int ns = 0; int tot = 0; int lk = 0; int smy = 0; int pct = 0; boolean pole = false;
  int pr = 0;   // 0.4.34: Precious finds
''')
P.rep('''      lk = @PKG@.ShClk.luck(p, kd, s0); smy = @PKG@.ShClk.smithy(p, kd, s0);''', '''      lk = @PKG@.ShClk.luck(p, kd, s0); pr = @PKG@.ShClk.prec(p, kd, s0); smy = @PKG@.ShClk.smithy(p, kd, s0);''')
P.rep('''    String ln = "Ore " + @PKG@.ShCfg.dec(@PKG@.ShClk.oreP(lk) * 100.0) + " %, Silver " + @PKG@.ShCfg.dec(@PKG@.ShClk.rareP(lk, z, false) * 100.0) + " %, Gold " + @PKG@.ShCfg.dec(@PKG@.ShClk.rareP(lk, z, true) * 100.0) + " %";''',
      '''    String ln = "Ore " + @PKG@.ShCfg.dec(@PKG@.ShClk.oreP(lk) * 100.0) + " %, Silver " + @PKG@.ShCfg.dec(@PKG@.ShClk.rareQ(lk, pr, z, false) * 100.0) + " %, Gold " + @PKG@.ShCfg.dec(@PKG@.ShClk.rareQ(lk, pr, z, true) * 100.0) + " %";   // 0.4.34: with Precious''')
P.rep('''+ " %, Silver " + @PKG@.ShCfg.dec(@PKG@.ShClk.rareP(lk, z, false) * 100.0) + " -> " + @PKG@.ShCfg.dec(@PKG@.ShClk.rareP(lk + 1, z, false) * 100.0) + " %";''',
      '''+ " %, Silver " + @PKG@.ShCfg.dec(@PKG@.ShClk.rareQ(lk, pr, z, false) * 100.0) + " -> " + @PKG@.ShCfg.dec(@PKG@.ShClk.rareQ(lk + 1, pr, z, false) * 100.0) + " %";''')
P.rep('''    this.ckUpCap = this.mine ? "coins + " + @PKG@.ShTotem.pretty(@PKG@.ShIsl.tok(kd, t, "ench")) : "the island owner buys upgrades";
  } else this.ckCap = "No Mining quarry yet''', '''    // 9 Precious finds (0.4.34): mining.i<n>.prec - Silver / Gold only; the Lucky finds cost of that level
    int pmx = @PKG@.ShCfg.MQ_PREC_MAX;
    this.ckUpL[9] = "Lv " + pr + " / " + pmx; this.ckUpSeen[9] = pr;
    if (pr >= pmx) this.ckUpE[9] = "Silver " + @PKG@.ShCfg.dec(@PKG@.ShClk.rareQ(lk, pr, z, false) * 100.0) + " %, Gold " + @PKG@.ShCfg.dec(@PKG@.ShClk.rareQ(lk, pr, z, true) * 100.0) + " %";
    else {
      this.ckUpE[9] = "Silver " + @PKG@.ShCfg.dec(@PKG@.ShClk.rareQ(lk, pr, z, false) * 100.0) + " -> " + @PKG@.ShCfg.dec(@PKG@.ShClk.rareQ(lk, pr + 1, z, false) * 100.0)
          + " %, Gold " + @PKG@.ShCfg.dec(@PKG@.ShClk.rareQ(lk, pr, z, true) * 100.0) + " -> " + @PKG@.ShCfg.dec(@PKG@.ShClk.rareQ(lk, pr + 1, z, true) * 100.0) + " %";
      this.ckUpC[9] = ckCostR(9, @PKG@.ShIsl.coins(@PKG@.ShIsl.subH(sz, pr + 1), cv), @PKG@.ShIsl.mats(kd, t, @PKG@.ShCombat.subMat(kd, 0), sz - 1, (long) (pr + 1)));
      this.ckUpOk[9] = this.mine;
    }
    this.ckUpCap = this.mine ? "coins + " + @PKG@.ShTotem.pretty(@PKG@.ShIsl.tok(kd, t, "ench")) : "the island owner buys upgrades";
  } else this.ckCap = "No Mining quarry yet''')
P.rep('''    if (row < 0 || row > 8) return "";   // 0.4.30: + row 8 Ores''', '''    if (row < 0 || row > 9) return "";   // 0.4.30: + row 8 Ores; 0.4.34: + row 9 Precious finds''')
P.rep('''    if (row == 8) return ckFresh(k, kd, s) ? @PKG@.ShClk.buyOre(u, k, kd, s, seen, cs) : "=The page is up to date now - click Add ore again.";   // 0.4.30: the zone's next ore
''', '''    if (row == 8) return ckFresh(k, kd, s) ? @PKG@.ShClk.buyOre(u, k, kd, s, seen, cs) : "=The page is up to date now - click Add ore again.";   // 0.4.30: the zone's next ore
    if (row == 9) return ckFresh(k, kd, s) ? @PKG@.ShClk.buyPrec(u, k, kd, s, seen, cs) : "=The page is up to date now - click Upgrade again.";   // 0.4.34: Precious finds
''')
P.rep('''this.ckCL = new String[60]; this.ckCG = new int[60]; this.ckUpBtn = new int[9];   // 0.4.30: 9 rows (the quarry's Ores)''',
      '''this.ckCL = new String[60]; this.ckCG = new int[60]; this.ckUpBtn = new int[10];   // 0.4.30: 9 rows (the quarry's Ores); 0.4.34: 10 (Precious finds)''')
P.rep('''             "Q": (Q_UP_NAMES[:2] + ["Miner spirit"] + Q_UP_NAMES[3:] + ["Ores"], Q_UP_ICON + ["UpQNodes"]),   # 0.4.30: + the zone's ore upgrades''',
      '''             "Q": (Q_UP_NAMES[:2] + ["Miner spirit"] + Q_UP_NAMES[3:] + ["Ores", "Precious finds"], Q_UP_ICON + ["UpQNodes", "UpQLuck"]),   # 0.4.30: + the zone's ore upgrades; 0.4.34: + Precious finds''')

# ---------------------------------------------------------------------------------------------------- 8. the ready line
P.rep(r'''log("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.33:''', r'''log("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.34: the Mining quarry finds Silver / Gold on every zone (spirits too), Precious finds row, the zone's stone types, Auto-Compactor on its stones; 0.4.33:''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0, "command / system registrations changed"
assert P.s.index("public static String dcBase(String id)") < P.s.index("public static long usedOf(") < P.s.index("public static long owedAs(") \
    < P.s.index("public static void credAs(") and P.s.index("public static long stonesAt(") < P.s.index('getDeclaredMethod("quarryExtra")') \
    < P.s.index("public static Object[] mine("), "0.4.34: the new methods come before their callers"
P.finish()
