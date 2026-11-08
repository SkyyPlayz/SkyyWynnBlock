"""Derive SkyyShards/build_skyyshards_0.4.21.py from the GENERATED SkyyShards 0.4.20 (build_skyyshards_0.4.20.py = the tools/deploy_set.py SET
pin, made by tools/shards_0_4_20_patch.py - edit the patch, never the generated file). Every anchor is asserted once; at the end every change
is undone on a copy and compared with 0.4.20 (tools/soundpass_gen.Patch). Line endings kept.
Run:   python tools/shards_0_4_21_patch.py   then   python SkyyShards/build_skyyshards_0.4.21.py   (never --deploy)
Check: python SkyyShards/test_skyyshards_0.4.21.py

0.4.21 (2026-11-08) = THE COMBAT SHARD: BIGGER WALLED ARENAS, MOBS AT YOUR LEVEL, BAGS APART (round sh021; Skyy 2026-11-08: "make the combat island bigger, and put
  walls around it." + "and to make it easy, lets have the combat shard mobs level with you. and make sure this can hold all the drops from the mobs. (have unidentified bags
  collected separately.)"; recorded docs/answered/world.md 2026-11-08). Combat Shard only; the other five shards are unchanged.
  1. BIGGER ARENA + WALL. Combat islands have their own footprint: half combat.half.small / medium / large = 12 / 18 / 25 (25 x 25, 37 x 37, 51 x 51; rows 6..28, each at
     least the old size and at least the size below). The wall stands on the rim ring, combat.wallHeight (4, 0 = none) blocks of the zone's brick (the arena's existing rim block,
     CRIM: Rock_Stone_Brick_Mossy / Sandstone / Slate / Volcanic / Basalt brick, checked against Assets.zip at build time). It is placed only on AIR, so it never replaces a
     block, and it is repaired on every Enter / Grow. THE GAP: a 3-wide opening (gapK: cells within 1.5 blocks of the centre line; 3-4 cells on a slanted spoke) on the hub side, where the bridge meets the rim;
     the bridge needs it (players walk in and out) and it is the way out, so nobody is ever walled in. Mobs CAN walk through it, onto the bridge; the 0.4.11 leash removes one that goes 8 blocks past the rim.
  2. SPACING. A 51 x 51 island cannot fit on the old 48-block hexagon (its neighbours are 42 / 48 blocks apart), so the Combat Shard has its own slot centres (ShGeo.CSX / CSZ): slot 0
     stays at (0, -48) - every Combat island owned today - and slots 1..5 move out along their own spoke to 70 blocks. Asserted at build time for the rows' maximum (half 28): no two islands
     overlap, a bridge never crosses another island, the hub is clear. Combat has 5 islands (Zone 1..5) so only the 6 inner slots are ever used (asserted).
     An island bought on an older version in slots 1..5 moves with its totems (their positions are relative); its old floor is cleared (our floor ids only). Blocks a player put there stay at the old spot, beside the bridge,
     outside the island's region. It cannot stay where it was: 51 x 51 does not fit on the hexagon. Checked 2026-11-08: no live save has a Combat island in slots 1..5 (the only one is NewBetaTest p3, slot 0).
  3. ONE-TIME REBUILD: marker <kind>.i<n>.arena = "<half>:<wall height>" as PAINTED (the paint's tag carries both, so a row changed or a Grow during a sliced paint leaves a marker that does not match: the next Enter cleans up) (no marker = an island from before 0.4.21). A full paint whose marker differs clears the old
     footprint's left-overs first (FIX_ARENA, only exact ids: the old torch ring, the old wall ring, the top of a lowered wall, the old floor of a moved island), then paints the island. The marker
     is written after a whole paint, after a byte-checked History copy shards/history/arena/<pkey>.pre-0.4.21.properties (0.4.18's cave rebuild path; one file per profile, the first state: a Grow or a changed row adds none). Grow and a changed row use the same path:
     the old wall is cleared and the new one built. Soul Cages, totems and hand-placed poles are painted as before; nothing else is touched.
  4. MOBS LEVEL WITH YOU (row combat.levelWithPlayer, live, default on). The base is the OWNER's class level (ShCombat.ownerLv: skill:fn:run; the active class while the owner is online on
     this profile, else the highest class level on the profile; no class = the highest class level; visitors do not change it; read outside the shard lock, cached 5 s (30 s when it must ask all 8 classes: an offline profile is a file read per class); SkyySkills missing = the old table).
     The Mob level upgrade adds on top: the table's rise from Small level 0, kept (lo +LO[i]-LO[0], hi +HI[i]-HI[0]; Small 0 = your level, Small 5 = +4..+5, Large 5 = +15..+17: a Grow never lowers it).
     THE RISE IS THE LEVELS BOUGHT: Grow needs all 3 upgrades at 5/5 and sets them back to 0, and spec 10's ladder counts on (Medium level 0 = Small level 5), so with the default table a new Medium is your level +4..+5
     and a new Large +9..+10: exactly the Mob levels already bought. Taking the rise inside one size instead would drop a maxed Small's mobs by 4..5 levels at the Grow and throw away what was bought.
     The zone offset (combat.levelOffset) is not added while this is on. Capped at 100; if SkyyMobs still refuses the level (its levels.max set lower), that mob takes the zone table's level and the log says so once. No SkyyMobs change.
     ECONOMY, on purpose (Skyy's words; flagged to Skyy): kill coins / XP that scale with mob level now follow the owner's level on every zone's island; the combat.levelWithPlayer row switches it off.
     Soul Cage output and its drops are unchanged; the only thing that depends on Mob level is the old +3 % a level on the Cage, kept as it was.
  5. HOLDS ALL DROPS. Checked: Collect pays the whole pool mix, one store count, every kind, by ShCombat.split; nothing is dropped for want of a slot or a cap on the mix (a full inventory keeps the rest stored).
     The pool leaves out, on purpose, combat.cageSkip (Void Essence, Voidheart, ores, ingots, crystals, rock: Skyy's "new islands stay the same" balance) and armor / weapons / tools (they carry SkyyGear documents): those still come only from fighting.
  6. BAGS APART. A separate store <kind>.i<n>.bags per island. Each drop the Soul Cage makes adds combat.bagPct (2) % of a bag, up to combat.bagCap (64) on an island (a DERIVED default, not Skyy's number: 0.4.20's Soul Cage made no bags, 2 % = SkyyGear's 6 % extra bag per kill
     at about 3 drops a kill; 0 = none). A new Bags button on each Combat Collect row and its own line in the panel; Collect / Collect all never touch bags. Bags are made by gear:fn:box (level = the island's mob level) outside the lock,
     then debited first, saved, and given to the inventory; what does not fit stays stored. Bags carry a document so they cannot go in a Sacks bag.
  7. SMALL. SkyySkills 0.4.70 can pay less than asked: Collect / Sell lines say "up to +N XP".
  SAVED DATA: <kind>.i<n>.arena and <kind>.i<n>.bags (Combat only). 0.4.20 keeps but ignores both.
  ROLLBACK 0.4.21 -> 0.4.20 alone: no migration. 0.4.20 paints only its smaller island: the bigger floor and the walls stay as blocks and are not cleared. Stored bags are kept in the file and come back with 0.4.21. Mobs get the table
     levels again. A Combat island in slots 1..5 goes back to its old centre in 0.4.20 (the Soul Cages read as sitting there), and its 0.4.21 floor at 70 blocks out stays behind as orphan blocks; on roll-forward the marker still matches, so nothing is rebuilt. None exist today.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

HERE = os.path.join(ROOT, "SkyyShards")
P = G.Patch(os.path.join(HERE, "build_skyyshards_0.4.20.py"), os.path.join(HERE, "build_skyyshards_0.4.21.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.4.20"\n') and P.has("GENERATED by tools/shards_0_4_20_patch.py") and not P.has("FIX_ARENA"), "not the generated SkyyShards 0.4.20"
REG0, SYS0 = P.s.count("registerCommand("), P.s.count("registerSystem(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.4.21 (2026-11-08)"):].rstrip() + "\n"

# ---------------------------------------------------------------------------------------------------- 0. header + version
P.rep('''"""SkyyShards 0.4.20 - build script (javassist via jpype). GENERATED by tools/shards_0_4_20_patch.py from build_skyyshards_0.4.19.py
(generated by tools/shards_0_4_19_patch.py from 0.4.18, ... back to tools/shards_0_4_patch.py from 0.3.2; edit the patch, never this file).
Changes are marked "0.4.20" /''', '''"""SkyyShards 0.4.21 - build script (javassist via jpype). GENERATED by tools/shards_0_4_21_patch.py from build_skyyshards_0.4.20.py
(generated by tools/shards_0_4_20_patch.py from 0.4.19, ... back to tools/shards_0_4_patch.py from 0.3.2; edit the patch, never this file).
Changes are marked "0.4.21" / "0.4.20" /''')
P.rep('''Run:   python SkyyShards/build_skyyshards_0.4.20.py   -> SkyyShards/SkyyShards-0.4.20.jar   (never --deploy: tools/deploy_set.py installs the set)
Check: python SkyyShards/test_skyyshards_0.4.20.py
''', '''Run:   python SkyyShards/build_skyyshards_0.4.21.py   -> SkyyShards/SkyyShards-0.4.21.jar   (never --deploy: tools/deploy_set.py installs the set)
Check: python SkyyShards/test_skyyshards_0.4.21.py
''' + NOTE + '''
0.4.20 notes:
''')
P.rep('VERSION = "0.4.20"\n', 'VERSION = "0.4.21"\n')

# ---------------------------------------------------------------------------------------------------- 1. the python tables, build-time checks
P.rep('''assert RING - HALF[2] - HUB_HALF >= 8, "the hub and a Large island leave a bridge"
''', '''assert RING - HALF[2] - HUB_HALF >= 8, "the hub and a Large island leave a bridge"
# 0.4.21 THE COMBAT ARENAS (Skyy 2026-11-08: "make the combat island bigger, and put walls around it."): their own half widths (rows combat.half.*) and their own slot centres: slot 0 stays,
# slots 1..5 move out along their own spoke - a 51 x 51 island does not fit on the 48-block hexagon. Everything below holds at the rows' maximum half.
CB_HALF_DEF, CB_HALF_MIN, CB_HALF_MAX, CB_WALL_DEF, CB_RING = [12, 18, 25], list(HALF), 28, 4, 70
CB_SLOT_POS = [SLOT_POS[0]] + [(int(round(CB_RING * math.cos(math.radians(-90 + 60 * _i)))), int(round(CB_RING * math.sin(math.radians(-90 + 60 * _i))))) for _i in range(1, NINNER)]
assert all(_a <= _b <= CB_HALF_MAX for _a, _b in zip(CB_HALF_MIN, CB_HALF_DEF)) and CB_HALF_DEF == sorted(CB_HALF_DEF)
for _i in range(NINNER):
    for _j in range(_i + 1, NINNER):
        assert max(abs(CB_SLOT_POS[_i][0] - CB_SLOT_POS[_j][0]), abs(CB_SLOT_POS[_i][1] - CB_SLOT_POS[_j][1])) >= 2 * CB_HALF_MAX + 4, "0.4.21: combat slots %d / %d overlap" % (_i, _j)
    assert max(abs(CB_SLOT_POS[_i][0]), abs(CB_SLOT_POS[_i][1])) - CB_HALF_MAX - HUB_HALF >= 8, "0.4.21: combat slot %d leaves no bridge" % _i
    _ln, _t = math.hypot(*CB_SLOT_POS[_i]), float(HUB_HALF - 1)
    while _t <= _ln - CB_HALF_MAX:
        for _w in (-1, 0, 1):
            _x = int(round(CB_SLOT_POS[_i][0] / _ln * _t - CB_SLOT_POS[_i][1] / _ln * _w))
            _z = int(round(CB_SLOT_POS[_i][1] / _ln * _t + CB_SLOT_POS[_i][0] / _ln * _w))
            for _j in range(NINNER):
                assert _j == _i or max(abs(_x - CB_SLOT_POS[_j][0]), abs(_z - CB_SLOT_POS[_j][1])) > CB_HALF_MAX + 1, "0.4.21: the bridge of combat slot %d crosses slot %d" % (_i, _j)
        _t += 0.5
''')
P.rep('''EXT48 = RING2 + HALF[2] + 2
''', '''EXT48 = RING2 + HALF[2] + 2
assert CB_RING + CB_HALF_MAX + 1 <= EXT48, "0.4.21: the combat arenas stay inside the loaded region"
''')
P.rep('''TY48 = [(_k, _t) for _k in range(NK) for _t in LAD[_k]]
''', '''TY48 = [(_k, _t) for _k in range(NK) for _t in LAD[_k]]
assert len(LAD[KINDS.index("Combat")]) <= NINNER, "0.4.21: the Combat Shard uses only the inner slots (Zone 1..5)"
''')
P.rep('''CZ_ONE = ("Furniture_Crude_Torch", "Wood_Softwood_Fence", "Rock_Volcanic_Cracked_Lava")
''', '''CZ_ONE = ("Furniture_Crude_Torch", "Wood_Softwood_Fence", "Rock_Volcanic_Cracked_Lava")
assert all("Brick" in _row[1] for _row in CZ_PAL), "0.4.21: the arena wall = the zone's stone brick (the rim block)"
''')

# ---------------------------------------------------------------------------------------------------- 2. config, Server Setup rows
P.rep('''    "combat.nightHold=true", "combat.spawn=true",
''', '''    "# 0.4.21: combat.half.small / medium / large = the half width of a combat arena (12 = 25 x 25); wallHeight = its wall in blocks (0 = none);",
    "# levelWithPlayer = mobs take the owner's class level (the Mob level upgrade adds on top); bagPct = unidentified bags per 100 drops made; bagCap = bags an island stores.",
    "combat.half.small=%d" % CB_HALF_DEF[0], "combat.half.medium=%d" % CB_HALF_DEF[1], "combat.half.large=%d" % CB_HALF_DEF[2], "combat.wallHeight=%d" % CB_WALL_DEF,
    "combat.levelWithPlayer=true", "combat.bagPct=2", "combat.bagCap=64",
    "combat.nightHold=true", "combat.spawn=true",
''')
P.rep('''for f in ("public static volatile boolean CB_NIGHT = true;", "public static volatile boolean CB_SPAWN = true;",
''', '''for f in ("public static volatile boolean CB_LVP = true;", "public static volatile int[] CB_HALF = new int[] { %s };" % ", ".join(str(_x) for _x in CB_HALF_DEF),
          "public static volatile int CB_WALL = %d;" % CB_WALL_DEF, "public static volatile int CB_BAG_PCT = 2;", "public static volatile int CB_BAG_CAP = 64;",
          "public static volatile boolean CB_NIGHT = true;", "public static volatile boolean CB_SPAWN = true;",
''')
P.rep('''_load += ["  CB_NIGHT = bool(p.getProperty(\\"combat.nightHold\\"), true);", "  CB_SPAWN = bool(p.getProperty(\\"combat.spawn\\"), true);",
''', '''_load += ["  CB_LVP = bool(p.getProperty(\\"combat.levelWithPlayer\\"), true);",
          "  { int chs = intOf(p.getProperty(\\"combat.half.small\\"), %d, %d, %d); int chm = intOf(p.getProperty(\\"combat.half.medium\\"), %d, %d, %d); int chl = intOf(p.getProperty(\\"combat.half.large\\"), %d, %d, %d); if (chm < chs) chm = chs; if (chl < chm) chl = chm; CB_HALF = new int[] { chs, chm, chl }; }" % (
              CB_HALF_DEF[0], CB_HALF_MIN[0], CB_HALF_MAX, CB_HALF_DEF[1], CB_HALF_MIN[1], CB_HALF_MAX, CB_HALF_DEF[2], CB_HALF_MIN[2], CB_HALF_MAX),
          "  CB_WALL = intOf(p.getProperty(\\"combat.wallHeight\\"), %d, 0, 12);" % CB_WALL_DEF,
          "  CB_BAG_PCT = intOf(p.getProperty(\\"combat.bagPct\\"), 2, 0, 100);", "  CB_BAG_CAP = intOf(p.getProperty(\\"combat.bagCap\\"), 64, 0, 1000000);",
          "  CB_NIGHT = bool(p.getProperty(\\"combat.nightHold\\"), true);", "  CB_SPAWN = bool(p.getProperty(\\"combat.spawn\\"), true);",
''')
P.rep('''ROWS += [("combat.nightHold", "Always night on combat islands", "combat", "bool", "true", "", "", "", "", "live",
''', '''# 0.4.21 (Skyy: "make the combat island bigger, and put walls around it." + "lets have the combat shard mobs level with you.")
ROWS += [("combat.half.%s" % _sn, "%s arena: half width" % _sl, "combat", "int", str(CB_HALF_DEF[_i]), str(CB_HALF_MIN[_i]), str(CB_HALF_MAX), "", "", "live",
          "Blocks from the centre to the wall (%d = %d x %d). Applied at the next Enter or Grow." % (CB_HALF_DEF[_i], 2 * CB_HALF_DEF[_i] + 1, 2 * CB_HALF_DEF[_i] + 1), "reload@config.properties:combat.half.%s" % _sn)
         for _i, (_sn, _sl) in enumerate((("small", "Small"), ("medium", "Medium"), ("large", "Large")))]
ROWS += [("combat.wallHeight", "Arena wall height", "combat", "int", str(CB_WALL_DEF), "0", "12", "", "", "live",
          "Blocks of the zone's brick round the arena (0 = no wall). The bridge side stays open.", "reload@config.properties:combat.wallHeight"),
         ("combat.levelWithPlayer", "Mobs level with the owner", "combat", "bool", "true", "", "", "", "", "live",
          "Mobs take the owner's class level, plus the upgrade. Off (or above levels.max) = the zone table.", "reload@config.properties:combat.levelWithPlayer"),
         ("combat.bagPct", "Unidentified bags per 100 drops", "combat", "int", "2", "0", "100", "", "", "live",
          "Soul Cage: bags made per 100 drops, stored apart from the drops. 0 = none (this adds gear income).", "reload@config.properties:combat.bagPct"),
         ("combat.bagCap", "Unidentified bags an island stores", "combat", "int", "64", "0", "1000000", "", "", "live",
          "Past this the Soul Cage makes no more bags until some are collected.", "reload@config.properties:combat.bagCap")]
ROWS += [("combat.nightHold", "Always night on combat islands", "combat", "bool", "true", "", "", "", "", "live",
''')

# ---------------------------------------------------------------------------------------------------- 3. ShStore: the History copy; ShInv: free slots; ShMath: the bag store
P.rep('''# 0.4.8: the map migration's History copy: shards/history/map/<pkey>.pre-0.4.8.properties (a different older one = a stamped name), byte-checked
''', '''# 0.4.21: the arena rebuild's History copy: shards/history/arena/<pkey>.pre-0.4.21.properties (one per profile), byte-checked (null = refused)
M(st, r"""
public static String snapArena(String k) {
  try {
    java.nio.file.Path f = DIR.resolve(k + ".properties");
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "-";
    java.nio.file.Path h = DIR.resolve("history").resolve("arena");
    java.nio.file.Files.createDirectories(h, new java.nio.file.attribute.FileAttribute[0]);
    byte[] src = java.nio.file.Files.readAllBytes(f);
    String name = k + ".pre-0.4.21.properties";
    java.nio.file.Path t = h.resolve(name);
    if (java.nio.file.Files.exists(t, new java.nio.file.LinkOption[0])) return "shards/history/arena/" + name;   // fix (critic): one copy a profile, the first state (a Grow / changed row adds none)
    java.nio.file.Path tmp = h.resolve(name + ".tmp");
    java.nio.file.Files.write(tmp, src, new java.nio.file.OpenOption[0]);
    moveInto(tmp, t);
    if (!java.util.Arrays.equals(src, java.nio.file.Files.readAllBytes(t))) return null;
    return "shards/history/arena/" + name;
  } catch (Throwable x) {
    return null;
  }
}""")
# 0.4.8: the map migration's History copy: shards/history/map/<pkey>.pre-0.4.8.properties (a different older one = a stamped name), byte-checked
''')
P.rep('''M(inv, r"""
public static boolean hasRoom(@IC@[] cs) {''', '''# 0.4.21: how many stacks with their own document could still go in (empty slots)
M(inv, r"""
public static int freeSlots(@IC@[] cs) {
  if (cs == null) return 0;
  int n = 0;
  for (int i = 0; i < cs.length; i++) {
    if (cs[i] == null) continue;
    short cap = cs[i].getCapacity();
    for (short j = 0; j < cap; j++) {
      @IS@ it = cs[i].getItemStack(j);
      if (it == null || it.isEmpty()) n++;
    }
  }
  return n;
}""")
M(inv, r"""
public static boolean hasRoom(@IC@[] cs) {''')
P.rep('''M(mth, r"""
public static long settle(int kd, java.util.Properties p, int slot, long now) {
''', '''# 0.4.21 (Skyy: "have unidentified bags collected separately."): the Combat Shard's bag store <kind>.i<n>.bags: combat.bagPct % of a bag per drop made, up to combat.bagCap (kd 5 = Combat: ShCombat comes after this class)
M(mth, r"""
public static long bags(java.util.Properties p, int slot) {
  long b = @PKG@.ShStore.lng(p, ik(5, slot, "bags"), 0L);
  return b < 0L ? 0L : b;
}""")
M(mth, r"""
public static void bagAdd(java.util.Properties p, int slot, long made, long from) {
  int pct = @PKG@.ShCfg.CB_BAG_PCT;
  long cap = (long) @PKG@.ShCfg.CB_BAG_CAP;
  long have = bags(p, slot);
  if (pct <= 0 || made <= 0L || have >= cap) return;
  double exp = (double) made * (double) pct / 100.0;
  long add = (long) Math.floor(exp);
  String k = p.getProperty("pkey");
  java.util.Random rnd = new java.util.Random(((long) slot * 1000003L) ^ (from * 37L) ^ (k == null ? 0L : (long) k.hashCode()) ^ 7774777L);
  if (rnd.nextDouble() < exp - (double) add) add++;
  if (add <= 0L) return;
  long nv = have + add;
  p.setProperty(ik(5, slot, "bags"), String.valueOf(nv > cap ? cap : nv));
}""")
M(mth, r"""
public static long settle(int kd, java.util.Properties p, int slot, long now) {
''')
P.rep('''  if (made > 0L) {
    double c = @PKG@.ShTotem.enchChance(kd, p, slot);
''', '''  if (kd == 5 && made > 0L) bagAdd(p, slot, made, from);   // 0.4.21: the Soul Cage's bags, in their own store
  if (made > 0L) {
    double c = @PKG@.ShTotem.enchChance(kd, p, slot);
''')

# ---------------------------------------------------------------------------------------------------- 4. ShCombat: the owner's level, the level texts
P.rep('''F(cmb, f)
M(cmb, "public static boolean is(int kd) { return kd == CK; }")''', '''F(cmb, f)
# 0.4.21: the class skills (SkyySkills' SkillDefs.NAMES), 5 s cache of the owner's level per profile key, the most SkyyMobs accepts
F(cmb, 'public static final String[] CLASS_SK = new String[] { "Combat.Archer", "Combat.Warrior", "Combat.Assassin", "Combat.Shaman", "Combat.Mage", "Combat.Berserker", "Combat.Priest", "Combat.Spellblade" };')
F(cmb, "public static final java.util.concurrent.ConcurrentHashMap LVL = new java.util.concurrent.ConcurrentHashMap();")
F(cmb, "public static final int MAXLV = 100;")
F(cmb, "public static volatile long LV_MS = 5000L;")
M(cmb, "public static boolean is(int kd) { return kd == CK; }")''')
P.rep('''# texts (the Map tab): now / next of each sub-upgrade, the pool
M(cmb, r"""
public static String lvTxt(int z, int size, int lvl) {
  int lo = lvLo(z, size, lvl);
  int hi = lvHi(z, size, lvl);
  return lo == hi ? String.valueOf(lo) : lo + "-" + hi;
}""")
M(cmb, r"""
public static String nowTxt(int z, int size, int a, int d, int i) {
''', '''# 0.4.21 (Skyy: "lets have the combat shard mobs level with you."): the level of a skill:fn:run answer, -1 = none
M(cmb, r"""
public static int runLv(Object r) {
  if (r instanceof Object[] && ((Object[]) r).length > 0 && ((Object[]) r)[0] instanceof Number) return ((Number) ((Object[]) r)[0]).intValue();
  return -1;
}""")
# the OWNER's class level for profile key k: the active class while the owner plays this profile, else the highest class level on the profile (also: no class chosen); -1 = unreadable.
# Call OUTSIDE ShStore.LOCK (a bridge call, may read a file); the cached ownerLv is what the callers use
M(cmb, r"""
public static int ownerLv0(String k, boolean[] slow) {
  try {
    java.util.function.Function run = @PKG@.ShCfg.fn("skill:fn:run");
    if (run == null || k == null || k.length() < 36) return -1;
    java.util.UUID u = java.util.UUID.fromString(k.substring(0, 36));
    if (k.equals(@PKG@.ShCfg.pkey(u))) {
      Object c = run.apply(new Object[] { u, "class" });
      if (c instanceof Object[] && ((Object[]) c).length > 5 && ((Object[]) c)[5] instanceof String) {
        int v = runLv(run.apply(new Object[] { k, (String) ((Object[]) c)[5] }));
        if (v >= 0) return v < 1 ? 1 : v;
      }
    }
    slow[0] = true;   // fix (critic): up to 8 asks (a file read each for an offline profile): kept longer
    int best = -1;
    for (int i = 0; i < CLASS_SK.length; i++) {
      int v = runLv(run.apply(new Object[] { k, CLASS_SK[i] }));
      if (v > best) best = v;
    }
    return best < 0 ? -1 : (best < 1 ? 1 : best);
  } catch (Throwable t) { return -1; }
}""")
M(cmb, r"""
public static int ownerLv(String k) {
  if (!@PKG@.ShCfg.CB_LVP || k == null) return -1;
  long now = System.currentTimeMillis();
  Object c = LVL.get(k);
  if (c instanceof long[]) {
    long[] a = (long[]) c;
    if (now >= a[1] && now - a[1] < a[2]) return (int) a[0];
  }
  boolean[] slow = new boolean[1];
  int v = ownerLv0(k, slow);
  if (LVL.size() > 4096) LVL.clear();
  LVL.put(k, new long[] { (long) v, now, slow[0] ? LV_MS * 6L : LV_MS });
  return v;
}""")
M(cmb, "public static boolean withP(int own) { return @PKG@.ShCfg.CB_LVP && own >= 0; }")
# the mob level with the owner's level as the base: the upgrade's rise on top (the table from Small level 0, so a Grow never lowers it); off / unreadable = the zone table
M(cmb, r"""
public static int riseOf(int[] a, int i) {
  int d = i < a.length && a.length > 0 ? a[i] - a[0] : 0;
  return d < 0 ? 0 : d;
}""")
M(cmb, r"""
public static int lvLoP(int own, int z, int size, int lvl) {
  if (!withP(own)) return lvLo(z, size, lvl);
  int v = own + riseOf(@PKG@.ShCfg.CB_LO, ix(size, lvl));
  return v < 1 ? 1 : (v > MAXLV ? MAXLV : v);
}""")
M(cmb, r"""
public static int lvHiP(int own, int z, int size, int lvl) {
  if (!withP(own)) return lvHi(z, size, lvl);
  int lo = lvLoP(own, z, size, lvl);
  int v = own + riseOf(@PKG@.ShCfg.CB_HI, ix(size, lvl));
  if (v > MAXLV) v = MAXLV;
  return v < lo ? lo : v;
}""")
# texts (the Map tab): now / next of each sub-upgrade, the pool
M(cmb, r"""
public static String lvTxt(int z, int size, int lvl) {
  int lo = lvLo(z, size, lvl);
  int hi = lvHi(z, size, lvl);
  return lo == hi ? String.valueOf(lo) : lo + "-" + hi;
}""")
M(cmb, r"""
public static String lvTxtP(int own, int z, int size, int lvl) {
  int lo = lvLoP(own, z, size, lvl);
  int hi = lvHiP(own, z, size, lvl);
  return lo == hi ? String.valueOf(lo) : lo + "-" + hi;
}""")
M(cmb, r"""
public static String nowTxt(int own, int z, int size, int a, int d, int i) {
''')
P.rep('''" - Lv " + lvTxt(z, size, d) + " - every " + respawnSec(size, i) + " s";''', '''" - Lv " + lvTxtP(own, z, size, d) + " - every " + respawnSec(size, i) + " s";''')
P.rep('''public static String nextTxt(int z, int size, int w, int lv) {''', '''public static String nextTxt(int own, int z, int size, int w, int lv) {''')
P.rep('''if (w == 1) return "Lv " + lvTxt(z, size, lv) + " -> " + lvTxt(z, size, lv + 1);''', '''if (w == 1) return "Lv " + lvTxtP(own, z, size, lv) + " -> " + lvTxtP(own, z, size, lv + 1);''')

# ---------------------------------------------------------------------------------------------------- 5. ShGeo: the arena's size + place, the wall, the rebuild
P.rep('''F(geo, "public static final int[] HALF = new int[] { %s };" % ", ".join(str(h) for h in HALF))
F(geo, "public static final int HUB = %d;" % HUB_HALF)''', '''F(geo, "public static final int[] HALF = new int[] { %s };" % ", ".join(str(h) for h in HALF))
F(geo, "public static final int[] CSX = new int[] { %s };" % ", ".join(str(p[0]) for p in CB_SLOT_POS))   # 0.4.21: the Combat Shard's own slot centres (6 inner slots; slot 0 = the old place)
F(geo, "public static final int[] CSZ = new int[] { %s };" % ", ".join(str(p[1]) for p in CB_SLOT_POS))
F(geo, "public static final int HUB = %d;" % HUB_HALF)''')
P.rep('''F(geo, "public static final int OPX = %d;" % OLD_PAD0[0])''', '''F(geo, "public static final int FIX_ARENA = -16;")    # 0.4.21 the rebuild of a combat arena: b[4] = ShGeo.arenaTag; clear only while one of IDS[b[5..]] (an entry with no ids = only the marker)
F(geo, "public static final int OPX = %d;" % OLD_PAD0[0])''')
P.rep('''M(geo, "public static int chunkX(int kd, int i) { return CX[i] + 32 * (kd - FK); }")''', '''M(geo, "public static int chunkX(int kd, int i) { return CX[i] + 32 * (kd - FK); }")
# 0.4.21: a combat arena's half width (kd = another shard: the shared table) and island centres of any kind
M(geo, r"""
public static int half(int kd, int si) {
  int s = si < 1 ? 1 : (si > 3 ? 3 : si);
  return kd == @PKG@.ShCombat.CK ? @PKG@.ShCfg.CB_HALF[s - 1] : HALF[s - 1];
}""")
M(geo, "public static int sxk(int kd, int s) { return kd == @PKG@.ShCombat.CK && s >= 0 && s < CSX.length ? CSX[s] : SX[s]; }")
M(geo, "public static int szk(int kd, int s) { return kd == @PKG@.ShCombat.CK && s >= 0 && s < CSZ.length ? CSZ[s] : SZ[s]; }")''')
# the bridge: the kd-aware lane
P.rep('''M(geo, r"""
public static void lane(java.util.ArrayList out, int kd, int src, int slot, int s0, int s1) {
  double ax0 = src < 0 ? 0.0 : (double) SX[src];
  double az0 = src < 0 ? 0.0 : (double) SZ[src];
  double ln = laneLen(src, slot);
  if (ln < 1.0) return;
  double dx = ((double) SX[slot] - ax0) / ln;
  double dz = ((double) SZ[slot] - az0) / ln;
''', '''# 0.4.21: the length of a lane in kind kd (the combat slots have their own centres)
M(geo, r"""
public static double laneLenK(int kd, int src, int slot) {
  double ax0 = src < 0 ? 0.0 : (double) sxk(kd, src);
  double az0 = src < 0 ? 0.0 : (double) szk(kd, src);
  double bx = (double) sxk(kd, slot) - ax0;
  double bz = (double) szk(kd, slot) - az0;
  return Math.sqrt(bx * bx + bz * bz);
}""")
M(geo, r"""
public static void lane(java.util.ArrayList out, int kd, int src, int slot, int s0, int s1) {
  double ax0 = src < 0 ? 0.0 : (double) sxk(kd, src);
  double az0 = src < 0 ? 0.0 : (double) szk(kd, src);
  double ln = laneLenK(kd, src, slot);
  if (ln < 1.0) return;
  double dx = ((double) sxk(kd, slot) - ax0) / ln;
  double dz = ((double) szk(kd, slot) - az0) / ln;
''')
P.rep('''  double ln = laneLen(src, slot);
  if (ln < 1.0) return;
  double end = ln - (double) HALF[0];
''', '''  double ln = laneLenK(kd, src, slot);
  if (ln < 1.0) return;
  double end = ln - (double) HALF[0];
''')
# the wall gap + the marker + the old-footprint clean-up, before combat()
P.rep('''# A COMBAT ISLAND of zone z at size si (spec 10):''', '''# 0.4.21 the arena wall's gap: the bridge's side only (a 3-wide opening on the hub line, as wide as the bridge; combat islands never carry an outer bridge)
M(geo, r"""
public static boolean gapK(int kd, int slot, int dx, int dz) {
  double vx = (double) -sxk(kd, slot);
  double vz = (double) -szk(kd, slot);
  double len = Math.sqrt(vx * vx + vz * vz);
  if (len < 1.0 || (double) dx * vx + (double) dz * vz <= 0.0) return false;
  return Math.abs((double) dx * vz - (double) dz * vx) / len <= 1.5;
}""")
M(geo, "public static String arenaMark(int kd, int si) { return half(kd, si) + \\":\\" + @PKG@.ShCfg.CB_WALL; }")
# fix (critic): the tag of a rebuild = slot + the half + the wall height it PAINTS (a row changed during a sliced paint must not mark the blocks as if built at the new value)
M(geo, "public static int arenaTag(int slot, int h, int wall) { return 300 + slot + 1000 * (h + 100 * wall); }")
M(geo, "public static int arenaSlotOf(int tag) { return (tag - 300) % 1000; }")
M(geo, "public static String arenaMarkOf(int tag) { int v = (tag - 300) / 1000; return (v % 100) + \\":\\" + (v / 100); }")
# 0.4.21 THE ONE-TIME REBUILD: runs while <kind>.i<n>.arena is not this island's "<half>:<wall>". No marker = an island from before 0.4.21 (old half, no wall). Only exact ids are cleared
# (an entry whose ids are all ours; b[4] = arenaTag -> the marker at the end of a whole paint); the sentinel entry (no ids) is there so a freshly bought island gets its marker too.
M(geo, r"""
public static void arenaFix(java.util.ArrayList out, int kd, java.util.Properties p, int slot) {
  if (kd != @PKG@.ShCombat.CK) return;
  int si = @PKG@.ShMath.size(kd, p, slot);
  String now = arenaMark(kd, si);
  String m = @PKG@.ShStore.str(p, @PKG@.ShMath.ik(kd, slot, "arena"));
  if (now.equals(m)) return;
  int cx = ox(kd) + sxk(kd, slot);
  int cz = OZ + szk(kd, slot);
  int h = half(kd, si);
  int wh = @PKG@.ShCfg.CB_WALL;
  int tag = arenaTag(slot, h, wh);
  int z = @PKG@.ShCombat.zone(kd, p, slot);
  int oh = HALF[si - 1];
  int ow = 0;
  boolean fresh = m.length() == 0;
  if (!fresh) {
    int c = m.indexOf(':');
    try { oh = Integer.parseInt(m.substring(0, c)); ow = Integer.parseInt(m.substring(c + 1)); } catch (Throwable t) { oh = h; ow = 0; }
  }
  out.add(new int[] { cx, Y + 2, cz, FIX_ARENA, tag });
  if (oh != h && oh > 1) {
    for (int i = 0; i < 8 * (oh - 1); i++) { int[] q = ringPos(oh - 1, i); out.add(new int[] { cx + q[0], Y + 1, cz + q[1], FIX_ARENA, tag, CTORCH }); }
  }
  for (int y = 1; y <= ow; y++) {
    if (oh == h && y <= wh) continue;
    for (int i = 0; i < 8 * oh; i++) { int[] q = ringPos(oh, i); out.add(new int[] { cx + q[0], Y + y, cz + q[1], FIX_ARENA, tag, CRIM[z] }); }
  }
  if (fresh && slot > 0 && (SX[slot] != sxk(kd, slot) || SZ[slot] != szk(kd, slot))) {   // bought in slots 1..5 before 0.4.21: the old floor at the old centre (ours only; a repaint of the new island follows)
    int bx = ox(kd) + SX[slot];
    int bz = OZ + SZ[slot];
    for (int dx = -oh; dx <= oh; dx++) for (int dz = -oh; dz <= oh; dz++) {
      out.add(new int[] { bx + dx, Y, bz + dz, FIX_ARENA, tag, CFLOOR[z], CRIM[z], CCORN[z], BRICK });
      out.add(new int[] { bx + dx, Y + 1, bz + dz, FIX_ARENA, tag, CTORCH });
      out.add(new int[] { bx + dx, Y - 1, bz + dz, FIX_ARENA, tag, DIRT });
      out.add(new int[] { bx + dx, Y - 2, bz + dz, FIX_ARENA, tag, STONE });
      out.add(new int[] { bx + dx, Y - 3, bz + dz, FIX_ARENA, tag, STONE });
    }
  }
}""")
# A COMBAT ISLAND of zone z at size si (spec 10):''')
P.rep('''  int h = HALF[si - 1];
  int cx = ox(kd) + SX[slot];
  int cz = OZ + SZ[slot];
  int z = zone < 0 ? 0 : (zone > 4 ? 4 : zone);
''', '''  int h = half(kd, si);   // 0.4.21: the arena's own size + place
  int cx = ox(kd) + sxk(kd, slot);
  int cz = OZ + szk(kd, slot);
  int z = zone < 0 ? 0 : (zone > 4 ? 4 : zone);
''')
P.rep('''    cavern(out, cx, cz, z, qs[0]);
  }
}""")''', '''    cavern(out, cx, cz, z, qs[0]);
  }
  int wh = @PKG@.ShCfg.CB_WALL;   // 0.4.21 THE WALL (Skyy: "put walls around it."): the rim ring + the corners, the zone's brick, only on AIR, open toward the bridge
  if (wh > 0) for (int i = 0; i < 8 * h; i++) {
    int[] q = ringPos(h, i);
    if (gapK(kd, slot, q[0], q[1])) continue;
    for (int y = 1; y <= wh; y++) out.add(new int[] { cx + q[0], Y + y, cz + q[1], DECO_K, CRIM[z] });
  }
}""")''')
P.rep('''  String key = slot + "|" + size + "|" + part;
  Object c = CSPOT.get(key);
  if (c instanceof int[]) return (int[]) c;
  int si = size < 1 ? 1 : (size > 3 ? 3 : size);
  int h = HALF[si - 1];
''', '''  int si = size < 1 ? 1 : (size > 3 ? 3 : size);
  int h = half(@PKG@.ShCombat.CK, si);   // 0.4.21: the arena's own size (a changed row = other spots)
  String key = slot + "|" + size + "|" + part + "|" + h;
  Object c = CSPOT.get(key);
  if (c instanceof int[]) return (int[]) c;
''')
P.rep('''  return new int[] { ox(kd) + SX[slot] + @PKG@.ShTotem.PDX[k], Y + 1, OZ + SZ[slot] + @PKG@.ShTotem.PDZ[k] };''', '''  return new int[] { ox(kd) + sxk(kd, slot) + @PKG@.ShTotem.PDX[k], Y + 1, OZ + szk(kd, slot) + @PKG@.ShTotem.PDZ[k] };''')
P.rep('''    if (o != null) return new int[] { ox(kd) + SX[slot] + o[0], Y + 1, OZ + SZ[slot] + o[1] };''', '''    if (o != null) return new int[] { ox(kd) + sxk(kd, slot) + o[0], Y + 1, OZ + szk(kd, slot) + o[1] };''')
P.rep('''    add(out, ox(kd) + SX[slot] + o[0], Y + 1, OZ + SZ[slot] + o[1], TOTEM + ti);''', '''    add(out, ox(kd) + sxk(kd, slot) + o[0], Y + 1, OZ + szk(kd, slot) + o[1], TOTEM + ti);''')
P.rep('''  int cx = ox(kd) + SX[slot];
  int cz = OZ + SZ[slot];
  out.add(new int[] { cx, Y + 2, cz, FIX_BRICK, slot });''', '''  int cx = ox(kd) + sxk(kd, slot);
  int cz = OZ + szk(kd, slot);
  out.add(new int[] { cx, Y + 2, cz, FIX_BRICK, slot });''')
P.rep('''  for (int i = 0; i < SLOTS_N(); i++) if (@PKG@.ShMath.hasIsland(kd, p, i)) caveFix(out, kd, p, i);   // 0.4.8: the old nodes go first (a cave cell may stand there)
''', '''  for (int i = 0; i < SLOTS_N(); i++) if (@PKG@.ShMath.hasIsland(kd, p, i)) caveFix(out, kd, p, i);   // 0.4.8: the old nodes go first (a cave cell may stand there)
  for (int i = 0; i < SLOTS_N(); i++) if (@PKG@.ShMath.hasIsland(kd, p, i)) arenaFix(out, kd, p, i);   // 0.4.21: a combat island's old left-overs go first too
''')
P.rep('''  return new double[] { (double) (ox(kd) + SX[slot]) + 0.5, (double) (Y + 3) + 0.4, (double) (OZ + SZ[slot]) + 0.5 };''', '''  return new double[] { (double) (ox(kd) + sxk(kd, slot)) + 0.5, (double) (Y + 3) + 0.4, (double) (OZ + szk(kd, slot)) + 0.5 };''')

# ---------------------------------------------------------------------------------------------------- 6. ShFill: FIX_ARENA, its marker (History first)
P.rep('''M(fill, r"""
public static int paintZ(@WLD@ w, java.util.ArrayList want, java.util.HashSet fixed, @PKG@.ShFill job, java.util.HashSet miss, int from, long until, int[] cnt) {''', '''M(fill, r"""
public static boolean arenaIs(String cur, int[] b) {
  if (cur == null || cur.length() == 0) return false;
  for (int j = 5; j < b.length; j++) if (cur.equals(@PKG@.ShGeo.IDS[b[j]])) return true;
  return false;
}""")
M(fill, r"""
public static int paintZ(@WLD@ w, java.util.ArrayList want, java.util.HashSet fixed, @PKG@.ShFill job, java.util.HashSet miss, int from, long until, int[] cnt) {''')
P.rep('''    if (kq == @PKG@.ShGeo.FIX_BRICK || kq == @PKG@.ShGeo.FIX_PAD || kq == @PKG@.ShGeo.FIX_ORE || kq == @PKG@.ShGeo.FIX_CAVE) {   // 0.4.18: + the old box cave
''', '''    if (kq == @PKG@.ShGeo.FIX_BRICK || kq == @PKG@.ShGeo.FIX_PAD || kq == @PKG@.ShGeo.FIX_ORE || kq == @PKG@.ShGeo.FIX_CAVE || kq == @PKG@.ShGeo.FIX_ARENA) {   // 0.4.18: + the old box cave; 0.4.21: + the combat arena's left-overs
''')
P.rep('''      boolean ours = kq == @PKG@.ShGeo.FIX_BRICK ? cur0.equals(@PKG@.ShGeo.IDS[@PKG@.ShGeo.BRICK])
''', '''      boolean ours = kq == @PKG@.ShGeo.FIX_ARENA ? arenaIs(cur0, b) : kq == @PKG@.ShGeo.FIX_BRICK ? cur0.equals(@PKG@.ShGeo.IDS[@PKG@.ShGeo.BRICK])
''')
P.rep('''  String caves2 = "";   // 0.4.18: slot + 200 = the natural cave rebuild (marker 2)
  String snap = null;
''', '''  String caves2 = "";   // 0.4.18: slot + 200 = the natural cave rebuild (marker 2)
  String arenas = "";   // 0.4.21: arenaTag (>= 300) = the combat arena rebuild (marker <half>:<wall>)
  String snapA = null;
  boolean refusedA = false;
  String snap = null;
''')
P.rep('''      if (s >= 200) {   // 0.4.18: the old box cave is cleared - the island is the natural cave now
''', '''      if (s >= 300) {   // 0.4.21: the combat arena is rebuilt at its new size
        int cs = @PKG@.ShGeo.arenaSlotOf(s);
        if (!@PKG@.ShMath.hasIsland(kd, p, cs)) continue;
        String akey = @PKG@.ShMath.ik(kd, cs, "arena");
        String am = @PKG@.ShGeo.arenaMarkOf(s);   // fix (critic): what this paint built
        if (am.equals(p.getProperty(akey))) continue;
        if (refusedA) continue;
        if (snapA == null) { snapA = @PKG@.ShStore.snapArena(k); if (snapA == null) { refusedA = true; continue; } }   // History copy FIRST (byte-checked)
        p.setProperty(akey, am);
        arenas = arenas + " " + (cs + 1) + "=" + am;
        n++;
        continue;
      }
      if (s >= 200) {   // 0.4.18: the old box cave is cleared - the island is the natural cave now
''')
P.rep('''        if (done.length() > 0) @PKG@.ShStore.log("centre " + k + " "''', '''        if (arenas.length() > 0) @PKG@.ShStore.log("arena (SkyyShards @VERSION@) " + k + " " + @PKG@.ShKind.KEYS[kd] + " island(s)" + arenas + ": rebuilt once at the new size, our blocks only; copy " + snapA);
        if (done.length() > 0) @PKG@.ShStore.log("centre " + k + " "''')
P.rep('''  if (refused) @PKG@.ShCfg.warnOnce("cavesnap:" + k,''', '''  if (refusedA) @PKG@.ShCfg.warnOnce("arenasnap:" + k, "the 0.4.21 arena rebuild marker of " + k + " is waiting: its History copy could not be written (the arena is rebuilt; it is marked next time)");
  if (refused) @PKG@.ShCfg.warnOnce("cavesnap:" + k,''')

# ---------------------------------------------------------------------------------------------------- 7. the hand-placed totem spot, the spawner, the Collect / bag code
P.rep('''    int hh = @PKG@.ShGeo.HALF[sz - 1];
''', '''    int hh = @PKG@.ShGeo.half(kd, sz);   // 0.4.21: the combat arena's own size
''')
P.rep('''    int h = @PKG@.ShGeo.HALF[@PKG@.ShMath.size(kd, p, s) - 1];
    int dx = bx - (@PKG@.ShGeo.ox(kd) + @PKG@.ShGeo.SX[s]);
    int dz = bz - (@PKG@.ShGeo.OZ + @PKG@.ShGeo.SZ[s]);
''', '''    int h = @PKG@.ShGeo.half(kd, @PKG@.ShMath.size(kd, p, s));   // 0.4.21
    int dx = bx - (@PKG@.ShGeo.ox(kd) + @PKG@.ShGeo.sxk(kd, s));
    int dz = bz - (@PKG@.ShGeo.OZ + @PKG@.ShGeo.szk(kd, s));
''')
P.rep('''public static String spawnOne(@WLD@ w, int z, int size, int lvl, int part, int slot, int cx, int cz, java.util.ArrayList all, java.util.Random rnd) {''',
      '''public static String spawnOne(@WLD@ w, int z, int size, int lvl, int part, int slot, int cx, int cz, java.util.ArrayList all, java.util.Random rnd, int own) {''')
P.rep('''    int lo = @PKG@.ShCombat.lvLo(z, size, lvl);
    int hi = @PKG@.ShCombat.lvHi(z, size, lvl);
    eLevel(w, id, lo + (hi > lo ? rnd.nextInt(hi - lo + 1) : 0));
''', '''    int lo = @PKG@.ShCombat.lvLoP(own, z, size, lvl);   // 0.4.21: at the owner's level (the Mob level upgrade adds on top)
    int hi = @PKG@.ShCombat.lvHiP(own, z, size, lvl);
    int lv0 = lo + (hi > lo ? rnd.nextInt(hi - lo + 1) : 0);
    if (!eLevel(w, id, lv0) && own >= 0) {   // fix (critic): above SkyyMobs' levels.max = the zone table, not an unlevelled mob
      if (@PKG@.ShCfg.fn("mob:fn:setLevel") != null) @PKG@.ShCfg.warnOnce("combatlv", "SkyyMobs refused mob level " + lv0 + " (its levels.max is lower?) - that island's mobs take the zone table's level");
      int lt = @PKG@.ShCombat.lvLo(z, size, lvl);
      int ht = @PKG@.ShCombat.lvHi(z, size, lvl);
      eLevel(w, id, lt + (ht > lt ? rnd.nextInt(ht - lt + 1) : 0));
    }
''')
P.rep('''public static int island(@WLD@ w, String k, int slot, int t, int size, int[] lv, java.util.ArrayList mem, boolean[] act, java.util.ArrayList all, long now, java.util.Random rnd) {''',
      '''public static int island(@WLD@ w, String k, int slot, int t, int size, int[] lv, java.util.ArrayList mem, boolean[] act, java.util.ArrayList all, long now, java.util.Random rnd, int own) {''')
P.rep('''  int h = @PKG@.ShGeo.HALF[si - 1];
  int cx = @PKG@.ShGeo.ox(kd) + @PKG@.ShGeo.SX[slot];
  int cz = @PKG@.ShGeo.OZ + @PKG@.ShGeo.SZ[slot];
  int capAll = @PKG@.ShCombat.cap(si, lv[0]);
''', '''  int h = @PKG@.ShGeo.half(kd, si);   // 0.4.21
  int cx = @PKG@.ShGeo.ox(kd) + @PKG@.ShGeo.sxk(kd, slot);
  int cz = @PKG@.ShGeo.OZ + @PKG@.ShGeo.szk(kd, slot);
  int capAll = @PKG@.ShCombat.cap(si, lv[0]);
''')
P.rep('''    String id = spawnOne(w, z, si, lv[1], part, slot, cx, cz, all, rnd);
''', '''    String id = spawnOne(w, z, si, lv[1], part, slot, cx, cz, all, rnd, own);
''')
P.rep('''  int sp = 0;
  for (int s = 0; s < n; s++) {
    if (ty[s] < 0) continue;
    sp += island(w, k, s, ty[s], sz[s], new int[] { lv[3 * s], lv[3 * s + 1], lv[3 * s + 2] }, mem, act, all, now, rnd);
''', '''  int sp = 0;
  int own = @PKG@.ShCombat.ownerLv(k);   // 0.4.21: the owner's level, outside the lock (visitors do not change it)
  for (int s = 0; s < n; s++) {
    if (ty[s] < 0) continue;
    sp += island(w, k, s, ty[s], sz[s], new int[] { lv[3 * s], lv[3 * s + 1], lv[3 * s + 2] }, mem, act, all, now, rnd, own);
''')
# the range aura stays on the (bigger) combat floor
P.rep('''(double) (o == null ? 0 : o[0]), (double) (o == null ? 0 : o[1]) } });''', '''(double) (o == null ? 0 : o[0]), (double) (o == null ? 0 : o[1]), (double) @PKG@.ShGeo.half(kd, sz) } });''')
P.rep('''    int h = HALF[sz >= 3 ? 2 : (sz == 2 ? 1 : 0)];
''', '''    int h = this.c.length > 8 ? (int) this.c[8] : HALF[sz >= 3 ? 2 : (sz == 2 ? 1 : 0)];   // 0.4.21: the combat arena's own size
''')
# the bag Collect: after the Collect wrappers
P.rep('''M(core, "public static String collect(java.util.UUID u, String k, int slot, @IC@[] cs) { return collect(u, k, FK, slot, cs); }")
''', '''M(core, "public static String collect(java.util.UUID u, String k, int slot, @IC@[] cs) { return collect(u, k, FK, slot, cs); }")
# 0.4.21 THE BAG COLLECT (Skyy: "have unidentified bags collected separately."): only <kind>.i<n>.bags, never the drops. The bags are made (gear:fn:box, a bridge) with no lock held, then under the lock:
# re-read, debit, SAVE (refused = nothing given), give counted, back what did not arrive. Bags carry a document, so they go to the inventory (never a stack into a Magic Bag).
F(core, "public static final int BAGS_AT_ONCE = 36;")
M(core, r"""
public static String collectBags0(java.util.UUID u, String k, int kd, int slot, @IC@[] cs) {
  if (!@PKG@.ShCfg.ON) return "-Shards are switched off on this server.";
  if (kd != @PKG@.ShCombat.CK) return "-Only combat islands store bags.";
  if (cs == null) return "-Your inventory could not be read - try again.";
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "-This shard's file could not be read - ask an admin to look at the server log.";
  String no = gate(u, k, kd, p);
  if (no != null) return no;
  int own = @PKG@.ShCombat.ownerLv(k);
  long have = 0L;
  int level = 1;
  @PKG@.ShStore.LOCK.lock(); try {
    @PKG@.ShMath.settleAll(kd, p, now());
    if (!@PKG@.ShMath.hasIsland(kd, p, slot)) return "-That island is gone - the page is up to date now.";
    have = @PKG@.ShMath.bags(p, slot);
    level = @PKG@.ShCombat.lvLoP(own, @PKG@.ShCombat.zone(kd, p, slot), @PKG@.ShMath.size(kd, p, slot), @PKG@.ShIsl.sub(p, kd, slot, 1));
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (have <= 0L) return "=No unidentified bags stored on that island yet.";
  int free = @PKG@.ShInv.freeSlots(cs);
  if (free <= 0) return "-Your inventory is full - the bags stay stored. A bag needs an empty slot.";
  int m = (int) Math.min(have, (long) Math.min(free, BAGS_AT_ONCE));
  java.util.function.Function box = @PKG@.ShCfg.fn("gear:fn:box");
  if (box == null) return "-SkyyGear cannot make bags right now - they stay stored.";
  java.util.ArrayList made = new java.util.ArrayList();
  for (int i = 0; i < m; i++) {
    Object o = null;
    try { o = box.apply(new Object[] { null, Integer.valueOf(level), "shard", Integer.valueOf(0), u }); } catch (Throwable t) { o = null; }
    if (o instanceof @IS@ && !((@IS@) o).isEmpty()) made.add(o);
  }
  if (made.isEmpty()) return "-SkyyGear made no bags right now - they stay stored.";
  int given = 0;
  int n = 0;
  long left = 0L;
  @PKG@.ShStore.LOCK.lock(); try {
    if (!@PKG@.ShMath.hasIsland(kd, p, slot)) return "-That island is gone - the page is up to date now.";
    long h2 = @PKG@.ShMath.bags(p, slot);
    n = (int) Math.min((long) made.size(), h2);
    if (n <= 0) return "=No unidentified bags stored on that island yet.";
    String key = @PKG@.ShMath.ik(kd, slot, "bags");
    p.setProperty(key, String.valueOf(h2 - (long) n));
    String err = @PKG@.ShStore.save(k, p);
    if (err != null) { p.setProperty(key, String.valueOf(h2)); @PKG@.ShCfg.warn("Bag collect refused (debit not written): " + err); return "-Collect failed: the shard file could not be saved. Nothing was taken."; }
    for (int i = 0; i < n; i++) {
      if (!@PKG@.ShInv.giveStack(cs, (@IS@) made.get(i))) break;
      given++;
    }
    if (given < n) {
      p.setProperty(key, String.valueOf(@PKG@.ShMath.bags(p, slot) + (long) (n - given)));
      String e2 = @PKG@.ShStore.save(k, p);
      if (e2 != null) @PKG@.ShCfg.warn("Bag collect: " + (n - given) + " bags that did not fit are back in memory but not on disk yet: " + e2);
    }
    left = @PKG@.ShMath.bags(p, slot);
    @PKG@.ShStore.log(u + " " + k + " combat slot " + slot + " bags debit " + n + " given " + given + " left " + left);
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (given <= 0) return "-Your inventory is full - the bags stay stored. A bag needs an empty slot.";
  return "+Collected " + given + " unidentified bag" + (given == 1 ? "" : "s") + (left > 0L ? ". " + @PKG@.ShCfg.num(left) + " stay stored." : ".");
}""")
M(core, "public static String collectBags(java.util.UUID u, String k, int kd, int slot, @IC@[] cs) { String r = collectBags0(u, k, kd, slot, cs); @PKG@.ShSnd.ok(u, r, 0); return r; }")
''')

# ---------------------------------------------------------------------------------------------------- 8. the page: Bags button, lines, sizes, levels; the XP wording
P.rep('''            a_n = seg("crowN%d_%d" % (i, k_))
''', '''            a_b = seg("crowB%d_%d" % (i, k_))          # 0.4.21: Combat: the Bags button (no Sell there)
            a_b.append(("#" + rid, SUI.spacer(w=10)))
            a_b.append(("#" + rid, SUI.button(rid + "Bag", "Bags", "secondary", "small", w=CSEL_W, anchor={"top": (rh - SUI.BTN_SMALL_H) // 2})))
            a_n = seg("crowN%d_%d" % (i, k_))
''')
P.rep('''    if (this.manage) {\\n    if (this.cSell) {\\n%s\\n%s\\n    } else {\\n%s\\n    }\\n%s\\n%s\\n    }\\n    }" % (
    i, jseg("crowv%d_%d" % (i, k_)), jseg("crowS%d_%d" % (i, k_)), binds([(P + "CRow%dSell" % i, "sopen%d" % i)]), jseg("crowN%d_%d" % (i, k_)),
''', '''    if (this.manage) {\\n    if (this.cSell) {\\n%s\\n%s\\n    } else if (this.cBags) {\\n%s\\n%s\\n    } else {\\n%s\\n    }\\n%s\\n%s\\n    }\\n    }" % (
    i, jseg("crowv%d_%d" % (i, k_)), jseg("crowS%d_%d" % (i, k_)), binds([(P + "CRow%dSell" % i, "sopen%d" % i)]), jseg("crowB%d_%d" % (i, k_)), binds([(P + "CRow%dBag" % i, "cbag%d" % i)]), jseg("crowN%d_%d" % (i, k_)),
''')
P.rep('''F(page, "public boolean bagOpen;")''', '''F(page, "public int ownLv;")   # 0.4.21: the owner's level (read before the store lock, -1 = the table)
F(page, "public boolean cBags;")
F(page, "public long bagT;")
F(page, "public boolean bagOpen;")''')
P.rep('''assert _SUBW <= CTX_W, (_SUBW, CTX_W)
''', '''_SUBW = max(_SUBW, max(SUI.text_width((h_ + b_)[:60 - len(" - 888,888 bags")] + " - 888,888 bags", 14)   # 0.4.21: Combat's bag count always shows, the rest is cut for it
            for h_ in ("8888888 / hour - full in 888 d 88 h", "8888888 / hour - no worker totem here", "8888888 / hour - FULL - collect to restart it")
            for b_ in ("", " - +88888888 Enchanted", " - +88888888 Linen Scraps")))
assert _SUBW <= CTX_W, (_SUBW, CTX_W)
''')
P.rep('''v = _menu("tabs3")
v.extend(SEG["t0"])
''', '''v = _menu("tabs0")   # 0.4.21: a row with the Bags button (Combat)
for k_ in ["c0"] + [_n % (i, 0) for i in range(SLOTS) for _n in ("crowv%d_%d", "crowB%d_%d", "crowC%d_%d")] + ["c1", "c1b"]:
    v.extend(SEG[k_])
VARIANTS.append(_foot(v))
v = _menu("tabs3")
v.extend(SEG["t0"])
''')
P.rep('''for j, (samp, col) in enumerate((("1,200 items", None), ("+2,400 Farming XP", GOOD), ("Wheat collection +1,200", GOLD),
''', '''assert SUI.text_width("Unidentified bags: 888 stored - press Bags on a row to collect.", 13) <= RW - 24, "0.4.21: the bags' line stays on one line"   # the button can only say Bags: 80 wide (see the report)
for j, (samp, col) in enumerate((("1,200 items", None), ("Up to +2,400 Farming XP", GOOD), ("Wheat collection +1,200", GOLD),
''')
P.rep('''                                  ("XP and collections are paid when you collect.", None))):
''', '''                                  ("XP and collections are paid when you collect.", None), ("Unidentified bags: 888 stored - press Bags on a row to collect.", None))):   # 0.4.21: the bags' own line
''')
P.rep('''c1.append((R0, SUI.spacer(h=40)))
c1b = seg("c1b")''', '''c1.append((R0, SUI.spacer(h=14)))   # 0.4.21: 40 less the bags' line (26): the panel keeps its height
c1b = seg("c1b")''')
P.rep('''  this.cAll = new String[6]; this.uTx''', '''  this.cAll = new String[7]; this.cAll[6] = ""; this.uTx''')
P.rep('''M(page, r"""
public static String sizeName(int s) {
  return s >= 3 ? "Large (29 x 29)" : (s == 2 ? "Medium (21 x 21)" : "Small (13 x 13)");
}""")
''', '''M(page, r"""
public static String sizeName(int s) {
  return s >= 3 ? "Large (29 x 29)" : (s == 2 ? "Medium (21 x 21)" : "Small (13 x 13)");
}""")
M(page, r"""
public static String sizeName(int kd, int s) {
  if (kd != @PKG@.ShCombat.CK) return sizeName(s);
  int w = 2 * @PKG@.ShGeo.half(kd, s) + 1;
  return (s >= 3 ? "Large (" : (s == 2 ? "Medium (" : "Small (")) + w + " x " + w + ")";
}""")
''')
P.rep('''    this.mTx[@@V1Sb@@] = sizeName(sz) + " - "''', '''    this.mTx[@@V1Sb@@] = sizeName(kd, sz) + " - "''')
P.rep('''@PKG@.ShCombat.nowTxt(@PKG@.ShCombat.zoneOf(ts), sz, a0, d0, i0)''', '''@PKG@.ShCombat.nowTxt(this.ownLv, @PKG@.ShCombat.zoneOf(ts), sz, a0, d0, i0)''')
P.rep('''"Next: " + @PKG@.ShCombat.nextTxt(@PKG@.ShCombat.zoneOf(ts), sz, w, lv);''', '''"Next: " + @PKG@.ShCombat.nextTxt(this.ownLv, @PKG@.ShCombat.zoneOf(ts), sz, w, lv);''')
P.rep('''" arena, always night, Lv " + @PKG@.ShCombat.lvTxt(@PKG@.ShCombat.zoneOf(ts), 1, 0) + ": "''', '''" arena, always night, Lv " + @PKG@.ShCombat.lvTxtP(this.ownLv, @PKG@.ShCombat.zoneOf(ts), 1, 0) + ": "''')
P.rep('''  mapInit();   // 0.4.9: the Map tab's slots (every early return below leaves them filled)
  bagLoad();   // 0.4.12: the bags, once, before the store lock
''', '''  mapInit();   // 0.4.9: the Map tab's slots (every early return below leaves them filled)
  bagLoad();   // 0.4.12: the bags, once, before the store lock
  this.ownLv = kd == @PKG@.ShCombat.CK ? @PKG@.ShCombat.ownerLv(k) : -1;   // 0.4.21: before the store lock (a bridge call)
''')
P.rep('''  this.cSell = this.manage && @PKG@.ShCfg.SELL_ON && kd != @PKG@.ShCombat.CK;   // 0.4.19''', '''  this.cBags = this.manage && kd == @PKG@.ShCombat.CK; this.bagT = 0L;   // 0.4.21: the Bags button
  this.cSell = this.manage && @PKG@.ShCfg.SELL_ON && kd != @PKG@.ShCombat.CK;   // 0.4.19''')
P.rep('''      if (sb0.length() > 60) sb0 = sb0.substring(0, 60);   // 0.4.20''', '''      if (kd == @PKG@.ShCombat.CK) {   // 0.4.21: the bag store of this island, on its sub-line
        long bg0 = @PKG@.ShMath.bags(p, i);
        this.bagT += bg0;
        String bw = bg0 > 0L ? " - " + @PKG@.ShCfg.num(bg0) + " bags" : "";
        if (sb0.length() + bw.length() > 60) sb0 = sb0.substring(0, Math.max(0, 60 - bw.length()));   // fix (critic): the bag count always shows, the rest is cut for it
        sb0 = sb0 + bw;
      }
      if (sb0.length() > 60) sb0 = sb0.substring(0, 60);   // 0.4.20''')
P.rep('''  this.cAll[5] = per <= 0L ? "Collections are paid when you collect." : "XP and collections are paid when you collect.";''',
      '''  this.cAll[5] = per <= 0L ? "Collections are paid when you collect." : "XP and collections are paid when you collect.";
  this.cAll[6] = this.cBags ? "Unidentified bags: " + @PKG@.ShCfg.num(this.bagT) + " stored - press Bags on a row to collect." : "";   // 0.4.21: their own line (fix, critic: only with the button: not for visitors)''')
P.rep('''    if (a.equals("colall")) return @PKG@.ShCore.collect(u, k, kd, -1, invOf(ref, st));
''', '''    if (a.startsWith("cbag")) {   // 0.4.21: a row's Bags button - only the bag store
      int r = -1;
      try { r = Integer.parseInt(a.substring(4)); } catch (Throwable x) { r = -1; }
      fill(k, invOf(ref, st));
      if (r < 0 || r >= this.cN) return "-That island is gone - the page is up to date now.";
      return @PKG@.ShCore.collectBags(u, k, kd, this.cSlot[r], invOf(ref, st));
    }
    if (a.equals("colall")) return @PKG@.ShCore.collect(u, k, kd, -1, invOf(ref, st));
''')
# the XP wording (Skills 0.4.70's class limit can pay less)
P.rep('''      else if (xp > 0L) extra = extra + " +" + @PKG@.ShCfg.num(xp) + " " + skill + " XP";
''', '''      else if (xp > 0L) extra = extra + " up to +" + @PKG@.ShCfg.num(xp) + " " + skill + " XP";   // 0.4.21: SkyySkills 0.4.70 can pay less (the class level limit)
''')
P.rep('''  this.cAll[1] = per <= 0L ? "No XP - this shard pays drops only" : "+" + @PKG@.ShCfg.num(xp) + " " + @PKG@.ShKind.SKILL[kd] + " XP";''',
      '''  this.cAll[1] = per <= 0L ? "No XP - this shard pays drops only" : "Up to +" + @PKG@.ShCfg.num(xp) + " " + @PKG@.ShKind.SKILL[kd] + " XP";   // 0.4.21''')
P.rep('''  this.sv[at + 1] = (xp > 0L ? "+" + @PKG@.ShCfg.num(xp) + " " + @PKG@.ShKind.SKILL[kd] + " XP - " : "")''', '''  this.sv[at + 1] = (xp > 0L ? "Up to +" + @PKG@.ShCfg.num(xp) + " " + @PKG@.ShKind.SKILL[kd] + " XP - " : "")''')

# ---------------------------------------------------------------------------------------------------- 9. the ready line
P.rep('''log("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.20: smaller storage, true Auto-Compactor, 20 % XP, Mining ingots; 0.4.19:''', '''log("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.21: bigger walled Combat arenas, mobs level with the owner, bags apart; 0.4.20: smaller storage, true Auto-Compactor, 20 % XP, Mining ingots; 0.4.19:''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0, "command / system registrations changed"
P.finish()
