"""Derive SkyyShards/build_skyyshards_0.4.6.py from the GENERATED SkyyShards 0.4.5 (build_skyyshards_0.4.5.py = the tools/deploy_set.py SET
pin, made by tools/shards_0_4_5_patch.py - edit the patch, never the generated file). Every anchor is asserted once; at the end every change
is undone on a copy and compared with 0.4.5 (tools/soundpass_gen.Patch). Line endings kept.
Run:   python tools/shards_0_4_6_patch.py   then   python SkyyShards/build_skyyshards_0.4.6.py   (never --deploy)
Check: python SkyyShards/test_skyyshards_0.4.6.py

0.4.6 (2026-10-23) = SHARDS ARE A LEVEL 20 REWARD + BUYING ISLANDS 2-6 (docs/answered/world.md 2026-10-23 SHARDS = LEVEL 20 REWARD). Skyy:
  "lets make the shards be a lvl 20 reward. then have the upgrades cost, you you can get into them quickly and easily, but i costs a lot to
  start getting more faming or mining islands" + popups "Which level-20 unlocks which shard? -> Skill-matched (Recommended)" and
  "Expanding a shard (more islands per shard, slots 2-6): how expensive? -> Steep coin curve (Recommended)".
  1. LEVEL 20 REWARD (new class ShLv20): Mining 20 = the Mining Shard, Foraging 20 = the Foraging AND the Orchard Shard, Farming 20 = Farming,
     Beastmastery 20 = Ranching, CLASS level 20 (the profile's class skill) = Combat. Levels come from SkyySkills skill:fn:run
     {pkey, skill} (bound to the profile, no switch race; the class: {UUID, "class"} names the class skill, then {pkey, that skill});
     an older SkyySkills without skill:fn:run = skill:fn:level {UUID, skill / "Combat"}; no SkyySkills = nobody qualifies (never throws).
     ShTick asks every 5 s for every online player (so a player already past the level gets theirs within 5 s of joining, and a level-up
     within 5 s); a player with something due gets ONE task on their own world thread (ShAdmin.giveGate: same thread, not switching
     profile) that re-reads the levels and grants. ONE PER KIND PER PROFILE: the record lv20.<kind> in the profile's shard file
     (shards/<pkey>.properties; "given:<ms>" or "had:<ms>"). A profile that already HAD that shard (placed once, crafted, given by an admin
     or a quest = ShCore.hasShard, or one in the inventory) gets "had" and nothing (the never-a-second-shard-of-a-kind rule; Pick up Shard
     keeps working as before). Else <kind>.crafted = 1 + the record are SAVED FIRST, then the item is given (counted); inventory full = the
     record and the mark are taken back (saved) and the shard WAITS - a yellow chat line at most once a minute, given the moment there is
     room. Never two, never lost without a trace (a refused undo-save = WARN + collect.log line "LOST - /shardadmin give").
     Server Setup -> Shards -> Level 20 shards: lv20.<kind> = the level per kind (default 20, 0 = no free shard of that kind).
     The "No <Kind> Shard yet" lines now say which level gives it.
  2. THE OLD SHARD RECIPES ARE OFF: the six craft.Skyy_Shard_<Kind> defaults (Enchanted x32 + essences + 100,000 coins) become empty
     (= that recipe is off; the Totem Bench no longer lists an off shard recipe). One-time update ShMig046 (PROJECT-RULES 4; ShMig045's
     reviewed machinery copied): only a line that still holds the 0.4.5 default text becomes empty; a hand-edited / doubled line is kept +
     named in an INFO line; a verified config-history copy first; one config-changes.log line per changed line (Server Setup -> Shards ->
     Changes -> Undo); the run-once marker skyyshards-0.4.6-lv20 (a fresh 0.4.6 file carries it); every other byte and line ending kept.
  3. BUYING ISLANDS 2-6 (spec 9.4 "Buy a slot's island"; 0.1-0.4.5 only ever filled slot 1): the Islands tab shows an empty slot's price
     and a Buy island button (owner only; one packet per click like Grow). The Nth island of a shard (2..6, whatever slot it goes in) costs
     island.coins.base (8,300 = 1 h of income at Lv 10, tools/balance_model.py p7_target_h(1) p7_round) x the SkyyCoins coin curve
     (coins:fn:curve; its built-in copy when SkyyCoins is older / absent) at island.coins.level (20 = the level the shard comes at) x
     island.coins.step (3) ^ (N - 2), rounded like every P7 cost (10 / 100 / 500 / 5,000): 19,000 / 57,000 / 170,000 / 510,000 / 1,535,000
     (about 1 h of income at Lv 20 for island 2, then x3 each), PLUS island.items.N (8 / 16 / 32 / 64 / 128) of the shard's own Enchanted
     material (island.item.<kind>: Enchanted Copper / Oak / Wheat / Raw Chicken / Apple / Bone - SkyyCollections' ids). Items first
     (counted), then coins (items back if they fail), then the island is saved (a refused save gives both back). The new island = Small,
     the shard's island type, empty pads (place a worker totem from the Totems tab); the region is repainted at once when it is loaded.
  SAVED DATA: per profile lv20.<kind> + <kind>.crafted (as /shardadmin give already writes) + bought islands <kind>.i<n>.* (the 0.3 keys).
  ROLLBACK 0.4.6 -> 0.4.5: safe - 0.4.5 ignores lv20.* and reads bought islands as islands (it shows them, it just cannot sell more); a
  given shard stays given. The craft lines stay empty (0.4.5 reads them as off) - Undo the ShMig046 rows in Server Setup -> Changes first to
  get the 100,000-coin recipes back.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G
import balance_model as BM

ISL_BASE = BM.p7_round(BM.p7_target_h(1))
assert ISL_BASE == 8300, ISL_BASE
ISL_LV, ISL_STEP = 20, 3.0
ISL_QTY = [0, 0, 8, 16, 32, 64, 128]                      # index = the Nth island of the shard (2..6)
ISL_COINS = [0, 0] + [BM.p7_round(ISL_BASE * BM.p7_curve_from_text(BM.P7_CURVE_TEXT, ISL_LV) * ISL_STEP ** (n - 2)) for n in range(2, 7)]
assert ISL_COINS[2:] == [19000, 57000, 170000, 510000, 1535000], ISL_COINS
CURVE_PTS = [(int(a), float(b)) for a, b in (kv.split(":") for kv in BM.P7_CURVE_TEXT.split(","))]

HERE = os.path.join(ROOT, "SkyyShards")
P = G.Patch(os.path.join(HERE, "build_skyyshards_0.4.5.py"), os.path.join(HERE, "build_skyyshards_0.4.6.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.4.5"\n') and P.has("GENERATED by tools/shards_0_4_5_patch.py") and not P.has("ShMig046"), "not the generated SkyyShards 0.4.5"
REG0, SYS0 = P.s.count("registerCommand("), P.s.count("registerSystem(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.4.6 (2026-10-23)"):].rstrip() + "\n"

P.rep('''"""SkyyShards 0.4.5 - build script (javassist via jpype). GENERATED by tools/shards_0_4_5_patch.py from build_skyyshards_0.4.4.py
(generated by tools/shards_0_4_4_patch.py from 0.4.3, ... back to tools/shards_0_4_patch.py from 0.3.2; edit the patch, never this file).
Changes are marked "0.4.5" / "0.4.4" / "0.4.3" / "0.4.2" / "0.4.1" / "0.4".
Run:   python SkyyShards/build_skyyshards_0.4.5.py   -> SkyyShards/SkyyShards-0.4.5.jar   (never --deploy: tools/deploy_set.py installs the set)
Check: python SkyyShards/test_skyyshards_0.4.5.py
''', '''"""SkyyShards 0.4.6 - build script (javassist via jpype). GENERATED by tools/shards_0_4_6_patch.py from build_skyyshards_0.4.5.py
(generated by tools/shards_0_4_5_patch.py from 0.4.4, ... back to tools/shards_0_4_patch.py from 0.3.2; edit the patch, never this file).
Changes are marked "0.4.6" / "0.4.5" / "0.4.4" / "0.4.3" / "0.4.2" / "0.4.1" / "0.4".
Run:   python SkyyShards/build_skyyshards_0.4.6.py   -> SkyyShards/SkyyShards-0.4.6.jar   (never --deploy: tools/deploy_set.py installs the set)
Check: python SkyyShards/test_skyyshards_0.4.6.py
''' + NOTE + '''
0.4.5 notes:
''')
P.rep('VERSION = "0.4.5"\n', 'VERSION = "0.4.6"\n')

# ---- 2. the shard recipes: the 0.4.5 texts kept for the update, the defaults empty (= off)
P.rep('''NREC = len(RECIPES)
''', '''NREC = len(RECIPES)
# 0.4.6 (Skyy 2026-10-23 "lets make the shards be a lvl 20 reward"): the six shard recipes are OFF by default (empty = off); the 0.4.5 texts
# stay here for the one-time update ShMig046 (an untouched 0.4.5 line becomes empty; a hand-edited one is kept)
SHARD_REC_045 = dict((_r[0], _r[1]) for _r in RECIPES if _r[0] in SHARD_ITEMS)
assert sorted(SHARD_REC_045) == sorted(SHARD_ITEMS) and all(_v.endswith(";100000") for _v in SHARD_REC_045.values()), SHARD_REC_045
RECIPES = [(_r[0], "" if _r[0] in SHARD_ITEMS else _r[1]) for _r in RECIPES]
MIG046 = [("craft." + _i, SHARD_REC_045[_i], "", "t") for _i in SHARD_ITEMS]
MIG046_MK = "skyyshards-0.4.6-lv20"
MIG046_LINE = "# ---------- SkyyShards 0.4.6 (marker %%s, runs once): shards are level 20 rewards - the 100,000-coin shard recipes were switched off; only untouched old default lines were changed ----------" %% MIG046_MK
# 0.4.6 LEVEL 20 SHARDS (ShLv20): the skill whose level gives each shard (index = KINDS; "class" = the profile's class skill)
LV20_SKILL = ["Mining", "Foraging", "Farming", "Beastmastery", "Foraging", "class"]
LV20_DEF = 20
assert len(LV20_SKILL) == NK and KINDS[4] == "Orchard" and KINDS[5] == "Combat" and KINDS[3] == "Ranching"
# 0.4.6 BUYING ISLANDS 2-6: the Nth island = island.coins.base x curve(island.coins.level) x island.coins.step ^ (N - 2) + island.items.N of
# the shard's Enchanted material (tools/shards_0_4_6_patch.py; SkyyCollections' Enchanted ids)
ISL_BASE, ISL_LV, ISL_STEP = %d, %d, %r
ISL_QTY = %r
ISL_COINS = %r
ISL_ITEM = ["Skyy_Ench_Copper", "Skyy_Ench_Oak", "Skyy_Ench_Wheat", "Skyy_Ench_RawChicken", "Skyy_Ench_Apple", "Skyy_Ench_Bone"]
CURVE_PTS = %r          # the SkyyCoins 0.1.10 coins.curve default (tools/balance_model.py P7_CURVE_TEXT) - the built-in copy
print("0.4.6 level 20 shards: %%s; islands 2-6 cost %%s coins + %%s Enchanted (%%s)" %% (
    ", ".join("%%s %%s" %% (LV20_SKILL[_k], KINDS[_k]) for _k in range(NK)), ISL_COINS[2:], ISL_QTY[2:], ", ".join(ISL_ITEM)))
''' % (ISL_BASE, ISL_LV, ISL_STEP, ISL_QTY, ISL_COINS, CURVE_PTS))
P.rep('''for _rid, _rtxt in RECIPES:
    for _part in''', '''for _rid, _rtxt in RECIPES:
    if not _rtxt:   # 0.4.6: an off recipe (the shards) names nothing
        continue
    for _part in''')
P.rep('''for _iid in TOTEM_ITEM + TOTEM_BLOCK + MOD_ITEM + SHARD_ITEMS:
    assert _iid not in ITEMS''', '''for _iid in ISL_ITEM:   # 0.4.6: the island materials are SkyyCollections' Enchanted ids
    assert _iid in _SE.IDS, "island item %s is not an Enchanted id of tools/skyyench.py" % _iid
for _iid in TOTEM_ITEM + TOTEM_BLOCK + MOD_ITEM + SHARD_ITEMS:
    assert _iid not in ITEMS''')

# ---- the config text: the level 20 rows + the island rows + the marker (before the storage tiers)
P.rep('''    "# storage.tierN = stacks of 100 each island of the shard holds at storage tier N (0.4.4: 3 days of a full Large island at Totem N).",''',
      '''    "# lv20.<shard> = 0.4.6 LEVEL 20 SHARDS: the level that gives that shard for free, once per profile (mining / farming = Mining /",
    "# Farming level, foraging + orchard = Foraging level, ranching = Beastmastery level, combat = the class level). 0 = no free shard of that kind.",
] + ["lv20.%s=%d" % (KKEYS[_k], LV20_DEF) for _k in range(NK)] + [
    "# island.* = 0.4.6 BUYING ISLANDS 2-6 (Islands tab -> an empty slot -> Buy island). The Nth island of a shard (2..6) costs",
    "# island.coins.base x the coin curve (SkyyCoins coins.curve) at island.coins.level x island.coins.step ^ (N - 2) coins, rounded,",
    "# plus island.items.N of the shard's material island.item.<shard> (empty = coins only).",
    "island.coins.base=%d" % ISL_BASE, "island.coins.level=%d" % ISL_LV, "island.coins.step=%g" % ISL_STEP,
] + ["island.items.%d=%d" % (_n, ISL_QTY[_n]) for _n in range(2, 7)] + ["island.item.%s=%s" % (KKEYS[_k], ISL_ITEM[_k]) for _k in range(NK)] + [
    "# SkyyShards 0.4.6 defaults (marker %s): shards are level 20 rewards - the shard recipes are off - keep this line." % MIG046_MK,
    "# storage.tierN = stacks of 100 each island of the shard holds at storage tier N (0.4.4: 3 days of a full Large island at Totem N).",''')
P.rep('''     "Rebirths a profile needs before it can craft an extra shard (Skyy: after rebirth 2).", "reload@config.properties:craft.shardRebirth"),''',
      '''     "Only if an admin re-adds a shard recipe: rebirths before an extra one (0.4.6: level 20 rewards).", "reload@config.properties:craft.shardRebirth"),''')   # fix (critic shards046 #4)
P.rep('''    "# craft.shardRebirth = rebirths needed to craft an extra shard (Skyy: more can be crafted after rebirth 2).",''',
      '''    "# craft.shardRebirth = rebirths needed to craft an extra shard (0.4.6: the shard recipes are off - shards are level 20 rewards).",''')

# ---- ShCfg fields (after the 0.4 field loop)
P.rep('''    F(cfg, f)

CATS = [("shards", "Shards")''', '''    F(cfg, f)
# 0.4.6: level 20 shards (per kind; 0 = off) + buying islands 2-6 (arrays swapped whole by the loader) + the built-in coin curve copy
for f in ("public static volatile int[] LV20 = new int[] { %s };" % ", ".join(str(LV20_DEF) for _k in range(NK)),
          "public static volatile int ISL_BASE = %d;" % ISL_BASE, "public static volatile int ISL_LV = %d;" % ISL_LV,
          "public static volatile double ISL_STEP = %r;" % ISL_STEP,
          "public static volatile int[] ISL_QTY = new int[] { %s };" % ", ".join(str(x) for x in ISL_QTY),
          "public static volatile String[] ISL_ITEM = new String[] { %s };" % ", ".join(jlit(x) for x in ISL_ITEM),
          "public static final String[] DEF_ISL_ITEM = new String[] { %s };" % ", ".join(jlit(x) for x in ISL_ITEM),
          "public static final double[] CURVE_LV = new double[] { %s };" % ", ".join("%r" % float(a) for a, b in CURVE_PTS),
          "public static final double[] CURVE_X = new double[] { %s };" % ", ".join("%r" % b for a, b in CURVE_PTS)):
    F(cfg, f)

CATS = [("shards", "Shards")''')

# ---- Server Setup rows (2 new categories)
P.rep('''for _r in ROWS:
    assert len(_r[1]) <= 40''', '''# 0.4.6: Server Setup -> Shards -> Level 20 shards / Buying islands
CATS = CATS + [("lv20", "Level 20 shards"), ("islands", "Buying islands")]
ROWS += [("lv20.%s" % KKEYS[_k], "%s Shard at %s level" % (KINDS[_k], LV20_SKILL[_k] if LV20_SKILL[_k] != "class" else "class"), "lv20", "int",
          str(LV20_DEF), "0", "200", "", "", "live",
          "The %s level that gives the %s Shard free, once per profile. 0 = off." % (LV20_SKILL[_k] if LV20_SKILL[_k] != "class" else "class", KINDS[_k]),
          "reload@config.properties:lv20.%s" % KKEYS[_k]) for _k in range(NK)]
ROWS += [("island.coins.base", "Island price base (coins at Lv 10)", "islands", "int", str(ISL_BASE), "0", "1000000000", "", "", "live",
          "1 h of income at Lv 10. Island 2 = this x the coin curve at the price level.", "reload@config.properties:island.coins.base"),
         ("island.coins.level", "Island price level (coin curve)", "islands", "int", str(ISL_LV), "1", "100", "", "", "live",
          "The level whose coin curve prices islands (20 = when the shard is given).", "reload@config.properties:island.coins.level"),
         ("island.coins.step", "Each next island costs x", "islands", "dec", "%g" % ISL_STEP, "1", "100", "", "x", "live",
          "Island 3 = island 2 x this, island 4 = island 3 x this ... (Skyy: a steep curve).", "reload@config.properties:island.coins.step")]
ROWS += [("island.items.%d" % _n, "Island %d: Enchanted items" % _n, "islands", "int", str(ISL_QTY[_n]), "0", "100000", "", "", "live",
          "How many of the shard's Enchanted material island %d of a shard costs." % _n, "reload@config.properties:island.items.%d" % _n)
         for _n in range(2, 7)]
ROWS += [("island.item.%s" % KKEYS[_k], "Island material: %s" % KINDS[_k], "islands", "text", ISL_ITEM[_k], "", "120", "", "", "live",
          "%s Shard islands cost this (empty = coins only). Enchanted items need SkyyCollections." % KINDS[_k], "reload@config.properties:island.item.%s" % KKEYS[_k])
         for _k in range(NK)]
for _r in ROWS:
    assert len(_r[1]) <= 40''')

# ---- the loader
P.rep('''          "  CRAFT = cr;"]
''', '''          "  CRAFT = cr;"]
_load += ["  int[] lvq = new int[%d];" % NK] + ["  lvq[%d] = intOf(p.getProperty(\\"lv20.%s\\"), %d, 0, 200);" % (_k, KKEYS[_k], LV20_DEF) for _k in range(NK)] + [
    "  LV20 = lvq;",   # 0.4.6
    "  ISL_BASE = intOf(p.getProperty(\\"island.coins.base\\"), %d, 0, 1000000000);" % ISL_BASE,
    "  ISL_LV = intOf(p.getProperty(\\"island.coins.level\\"), %d, 1, 100);" % ISL_LV,
    "  ISL_STEP = decOf(p.getProperty(\\"island.coins.step\\"), %r, 1.0, 100.0);" % ISL_STEP,
    "  int[] isq = new int[7];"] + ["  isq[%d] = intOf(p.getProperty(\\"island.items.%d\\"), %d, 0, 100000);" % (_n, _n, ISL_QTY[_n]) for _n in range(2, 7)] + [
    "  ISL_QTY = isq;", "  String[] isi = new String[%d];" % NK] + [
    "  { String iv = p.getProperty(\\"island.item.%s\\"); isi[%d] = iv == null ? DEF_ISL_ITEM[%d] : iv.trim(); }" % (KKEYS[_k], _k, _k) for _k in range(NK)] + [
    "  ISL_ITEM = isi;"]
''')

# ---- ShCfg: the coin curve (SkyyCoins coins:fn:curve, else the built-in copy) + the island prices
P.rep('''# ================= ShStore: Skyy_SkyyShards/shards''', '''# ================= 0.4.6 the island prices (Balance P7 coin curve; tools/shards_0_4_6_patch.py) =================
M(cfg, r"""
public static double curveBuiltin(int lv) {
  double[] a = CURVE_LV;
  double[] b = CURVE_X;
  double x = lv < 1 ? 1.0 : (lv > 100 ? 100.0 : (double) lv);
  int i = 0;
  while (i < a.length - 2 && x > a[i + 1]) i++;
  double l0 = Math.log(b[i]);
  double l1 = Math.log(b[i + 1]);
  return Math.exp(l0 + (l1 - l0) * (x - a[i]) / (a[i + 1] - a[i]));
}""")
M(cfg, r"""
public static double curve(int lv) {
  try {
    java.util.function.Function g = fn("coins:fn:curve");
    if (g != null) {
      Object r = g.apply(new Object[] { Integer.valueOf(lv) });
      if (r instanceof Number) { double d = ((Number) r).doubleValue(); if (d > 0.0 && d < 1000000000.0) return d; }
    }
  } catch (Throwable t) { warnOnce("curve", "coins:fn:curve failed - the built-in coin curve is used (logged once): " + t); }
  return curveBuiltin(lv);
}""")
M(cfg, r"""
public static long round7(double x) {
  if (x <= 0.0) return 0L;
  double st = x < 1000.0 ? 10.0 : (x < 10000.0 ? 100.0 : (x < 100000.0 ? 500.0 : 5000.0));
  return (long) (st * Math.floor(x / st + 0.5));
}""")
# the price of the Nth island of a shard (2..6) at curve factor cv; 0 for the first
M(cfg, r"""
public static long islandCoinsAt(int n, double cv) {
  if (n < 2) return 0L;
  double x = (double) ISL_BASE * cv * Math.pow(ISL_STEP, (double) (n - 2));
  if (x > 1000000000000.0) x = 1000000000000.0;
  return round7(x);
}""")
M(cfg, "public static long islandCoins(int n) { return islandCoinsAt(n, curve(ISL_LV)); }")
M(cfg, r"""
public static int islandQty(int n) {
  int[] a = ISL_QTY;
  return n < 2 || n >= a.length ? 0 : a[n];
}""")
M(cfg, r"""
public static String islandItem(int kd) {
  String[] a = ISL_ITEM;
  String v = kd < 0 || kd >= a.length ? "" : a[kd];
  return v == null ? "" : v.trim();
}""")

# ================= ShStore: Skyy_SkyyShards/shards''')

# ---- ShMig046 = ShMig045's machinery with the shard recipe table (copied text, checked)
_a = P.s.index('''smig45 = mk("ShMig045")''')
_b = P.s.index('''M(cfg, r"""
public static int stacks(int tier) {''', _a)
_P46 = P.s[_a:_b]
for _x, _y in (('smig45 = mk("ShMig045")', 'smig46 = mk("ShMig046")'), ("F(smig45, _d)", "F(smig46, _d)"), ("M(smig45, r", "M(smig46, r"),
               ("jlit(MIG045_MK)", "jlit(MIG046_MK)"), ('"SkyyShards 0.4.5";', '"SkyyShards 0.4.6";'), ("jlit(MIG045_LINE)", "jlit(MIG046_LINE)"),
               ("for m in MIG045)", "for m in MIG046)"),
               ('" kept - the line is doubled or continues on the next line; the 0.4.5 default is " + NEWV[j] + " (Server Setup -> Shards -> Costs / Bench)"',
                '" kept - the line is doubled or continues on the next line; the 0.4.6 default is empty = off (Server Setup -> Shards -> Crafting)"'),
               ('" kept - an admin changed it (the 0.4.4 default was " + OLDV[j] + ", the 0.4.5 default is " + NEWV[j] + ")"',
                '" kept - an admin changed it (the old default was " + OLDV[j] + "; since 0.4.6 shards are level 20 rewards and the default is off)"'),
               ("NOT updated for SkyyShards 0.4.5 (Balance P7 coin costs)", "NOT updated for SkyyShards 0.4.6 (shard recipes off)"),
               ('"before the 0.4.5 coin costs update (Balance P7)"', '"before the 0.4.6 shard recipes update (level 20 shards)"'),
               ('"config.properties updated for SkyyShards 0.4.5 (Balance P7: shard upgrade coins = 1 h of the matching zone - storage 43,500 .. 3,880,000, compactor, compressor, grow, bench): "',
                '"config.properties updated for SkyyShards 0.4.6 (shards are level 20 rewards: the 100,000-coin shard recipes are switched off): "'),
               ("could not update config.properties for SkyyShards 0.4.5 (Balance P7 coin costs;", "could not update config.properties for SkyyShards 0.4.6 (shard recipes off;"),
               ("loadCfg writes the 0.4.5 default with the marker", "loadCfg writes the 0.4.6 default with the marker")):
    assert _P46.count(_x) >= 1, _x
    _P46 = _P46.replace(_x, _y)
assert "smig45" not in _P46 and "MIG045" not in _P46 and "0.4.5" not in _P46 and "0.4.4" not in _P46, [l for l in _P46.split("\n") if "0.4.5" in l or "0.4.4" in l or "MIG045" in l][:5]
P.rep('''M(cfg, r"""
public static int stacks(int tier) {''', '''# ================= 0.4.6 ShMig046 (PROJECT-RULES 4; ShMig045's reviewed machinery copied by tools/shards_0_4_6_patch.py): the six shard
# recipe lines, 0.4.5 default -> empty (off), only while they still hold it; setup() runs it right after ShMig045
for _k, _o, _n, _t in MIG046:
    assert ("\\n%s=%s\\n" % (_k, _n)) in "\\n" + CONFIG_TEXT + "\\n", _k            # the new default file holds the new (empty) value
assert CONFIG_TEXT.count(MIG046_MK) == 1
''' + _P46 + '''M(cfg, r"""
public static int stacks(int tier) {''')
P.rep('''  catch (Throwable t) { @PKG@.ShCfg.warn("the 0.4.5 coin costs update was skipped: " + t); }''',
      '''  catch (Throwable t) { @PKG@.ShCfg.warn("the 0.4.5 coin costs update was skipped: " + t); }
  try { @PKG@.ShMig046.run(@PKG@.ShCfg.FILE); }   // 0.4.6: untouched 0.4.5 shard recipes -> off (shards are level 20 rewards), once (History first; Undo)
  catch (Throwable t) { @PKG@.ShCfg.warn("the 0.4.6 shard recipes update was skipped: " + t); }''')

# ---- 1. ShLv20, part 1 (after ShKind: the class, its fields, how(); ShCore's texts call how())
P.rep('''# ================= 0.2 ShTotem: the totem table''', '''# ================= 0.4.6 ShLv20: the level 20 shards (Skyy 2026-10-23; tools/shards_0_4_6_patch.py). Part 1 = the class + its texts; the
# level reads / grant / scan follow after ShCore (part 2), the world-thread task after ShAdmin (part 3)
lv = mk("ShLv20", None, ("java.lang.Runnable",))
for f in ("public static final String[] SKILL = %s;" % _jarr(LV20_SKILL),
          "public static final java.util.concurrent.ConcurrentHashMap PENDING = new java.util.concurrent.ConcurrentHashMap();",   # UUID -> Long ms queued
          "public static final java.util.concurrent.ConcurrentHashMap NAG = new java.util.concurrent.ConcurrentHashMap();",       # "uuid|kind" -> Long ms
          "public static final java.util.concurrent.ConcurrentHashMap DONE = new java.util.concurrent.ConcurrentHashMap();",      # pkey -> TRUE (all six recorded)
          "public static final java.util.concurrent.atomic.AtomicLong GIVEN = new java.util.concurrent.atomic.AtomicLong();",
          "public static final java.util.concurrent.atomic.AtomicLong HELD = new java.util.concurrent.atomic.AtomicLong();",
          "public static final java.util.concurrent.atomic.AtomicLong HAD = new java.util.concurrent.atomic.AtomicLong();",
          "public static final java.util.concurrent.atomic.AtomicLong SCANS = new java.util.concurrent.atomic.AtomicLong();",
          "public static final java.util.concurrent.atomic.AtomicLong QUEUED = new java.util.concurrent.atomic.AtomicLong();",
          "public @PR@ pr;", "public java.util.UUID u;", "public String k;"):
    F(lv, f)
C(lv, "public ShLv20(@PR@ pr, java.util.UUID u, String k) { this.pr = pr; this.u = u; this.k = k; }")
# "Mining level 20" / "class level 20" / "an admin" (lv20.<kind> = 0)
M(lv, r"""
public static String how(int kd) {
  if (kd < 0 || kd >= SKILL.length) return "an admin";
  int[] a = @PKG@.ShCfg.LV20;
  int n = kd < a.length ? a[kd] : 0;
  if (n <= 0) return "an admin";
  return ("class".equals(SKILL[kd]) ? "class" : SKILL[kd]) + " level " + n;
}""")
# fix (critic shards046 #3): the whole clause, so lv20.<kind> = 0 reads right ("an admin can give you one" instead of naming an admin as the level)
M(lv, r"""
public static String src(int kd, boolean cap) {
  int[] a = @PKG@.ShCfg.LV20;
  int n = kd >= 0 && kd < a.length ? a[kd] : 0;
  if (kd < 0 || kd >= SKILL.length || n <= 0) return cap ? "An admin can give you one" : "an admin can give you one";
  return (cap ? "It is the reward for " : "it is the reward for ") + how(kd);
}""")
M(lv, "public static String rk(int kd) { return \\"lv20.\\" + @PKG@.ShKind.KEYS[kd]; }")

# ================= 0.2 ShTotem: the totem table''')
for _old, _new in (('''  if (!own) return "-No " + @PKG@.ShKind.NAMES[kd] + " Shard yet - it comes from the hub quest line.";
  return null;''', '''  if (!own) return "-No " + @PKG@.ShKind.NAMES[kd] + " Shard yet - " + @PKG@.ShLv20.src(kd, false) + ".";   // 0.4.6
  return null;'''),
                   ('''  if (!own) return "-No " + @PKG@.ShKind.NAMES[kd] + " Shard yet - it comes from the hub quest line.";
  out[0] = p;''', '''  if (!own) return "-No " + @PKG@.ShKind.NAMES[kd] + " Shard yet - " + @PKG@.ShLv20.src(kd, false) + ".";   // 0.4.6
  out[0] = p;'''),
                   ('''  if (!ownedNow) this.sum2 = "No " + nm + " Shard yet - it comes from the hub quest line.";''',
                    '''  if (!ownedNow) this.sum2 = "No " + nm + " Shard yet - " + @PKG@.ShLv20.src(kd, false) + ".";   // 0.4.6'''),
                   ('''Your first shards come from quests.";''', '''Your first shards are level 20 rewards.";''')):
    P.rep(_old, _new)

# ---- 3. buying islands 2-6 (ShCore, after Grow)
P.rep('''M(core, "public static String grow(java.util.UUID u, String k, int slot, @IC@[] cs) { return grow(u, k, FK, slot, cs); }")
''', '''M(core, "public static String grow(java.util.UUID u, String k, int slot, @IC@[] cs) { return grow(u, k, FK, slot, cs); }")
# 0.4.6: one purchase writing several keys (caller holds ShStore.LOCK) - purchase()'s order: `item` x qty taken first (counted; qty 0 = coins
# only), then coins (items back when they fail), then every key written (a refused save undoes it and refunds both). null = bought.
M(core, r"""
public static String purchaseN(java.util.UUID u, String k, int kd, java.util.Properties p, @IC@[] cs, String item, long qty, long coins, String[] keys, String[] vals, String tag, String what) {
  boolean items = qty > 0L && item != null && item.length() > 0;
  String nm = items ? @PKG@.ShTotem.pretty(item) : "";
  if (items) {
    long have = @PKG@.ShInv.count(cs, item);
    if (have < qty) return "-You need " + @PKG@.ShCfg.num(qty) + " " + nm + " (you have " + @PKG@.ShCfg.num(have) + ").";
  }
  long purse = @PKG@.ShPay.coins(u);
  if (coins > 0L && purse >= 0L && purse < coins) return "-You need " + @PKG@.ShCfg.num(coins) + " coins (you have " + @PKG@.ShCfg.num(purse) + ").";
  @PKG@.ShMath.settleAll(kd, p, now());   // production up to now at the old numbers
  java.util.ArrayList kept = new java.util.ArrayList();
  long got = 0L;
  if (items) {
    got = @PKG@.ShInv.take2(cs, item, qty, kept);
    if (got < qty) { @PKG@.ShInv.giveBack(cs, item, got, kept); return "-The " + nm + " could not be taken - nothing was bought."; }
  }
  if (!@PKG@.ShPay.takeCoins(u, coins)) {
    long r = items ? @PKG@.ShInv.giveBack(cs, item, got, kept) : 0L;
    @PKG@.ShStore.log(u + " " + k + " " + tag + " coins refused - refund " + r + " of " + got + " " + item);
    return items ? "-The coins could not be taken - your " + nm + " is back." : "-The coins could not be taken - nothing was bought.";
  }
  java.util.Properties old = new java.util.Properties();
  old.putAll(p);
  for (int i = 0; i < keys.length; i++) p.setProperty(keys[i], vals[i]);
  String e = @PKG@.ShStore.save(k, p);
  if (e != null) {
    p.clear(); p.putAll(old);
    long ri = items ? @PKG@.ShInv.giveBack(cs, item, got, kept) : 0L;
    boolean rc = @PKG@.ShPay.addCoins(u, coins);
    @PKG@.ShStore.log(u + " " + k + " " + what + " SAVE FAILED " + e + " - refund " + ri + " of " + got + " " + item + ", coins " + (rc ? coins : 0L) + " of " + coins);
    @PKG@.ShCfg.warn(tag + " not saved, refunded: " + e);
    return "-It could not be saved - your " + (items ? nm + (rc ? " and coins are" : " is") : (rc ? "coins are" : "purchase is")) + " back." + (rc ? "" : " Ask an admin about the " + @PKG@.ShCfg.num(coins) + " coins (collect.log).");
  }
  @PKG@.ShStore.log(u + " " + k + " " + what + " paid " + coins + " coins + " + got + " " + item + @PKG@.ShInv.keptText(kept));
  return null;
}""")
# 0.4.6: buy an island for an empty slot (spec 9.4; Skyy "costs a lot to start getting more"). The Nth island of the shard (2..6, whatever
# slot) = ShCfg.islandCoins(N) coins + islandQty(N) of islandItem(kd); the island = Small, the shard's type, no totems; repainted at once.
M(core, r"""
public static String buyIsland0(java.util.UUID u, String k, int kd, int slot, @IC@[] cs) {
  if (!@PKG@.ShCfg.ON) return "-Shards are switched off on this server.";
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "-This shard's file could not be read.";
  if (cs == null) return "-Your inventory could not be read - try again.";
  String no = gateOwn(u, k, kd, p);   // the owner only (as Grow)
  if (no != null) return no;
  if (slot < 0 || slot >= @PKG@.ShMath.SLOTS) return "-Pick a slot first.";
  String item = @PKG@.ShCfg.islandItem(kd);
  double cv = @PKG@.ShCfg.curve(@PKG@.ShCfg.ISL_LV);   // the bridge asked outside the lock
  String res;
  @PKG@.ShStore.LOCK.lock(); try {
    if (@PKG@.ShMath.hasIsland(kd, p, slot)) return "=That slot already has an island.";
    int n = 0;
    for (int i = 0; i < @PKG@.ShMath.SLOTS; i++) if (@PKG@.ShMath.hasIsland(kd, p, i)) n++;
    if (n >= @PKG@.ShMath.SLOTS) return "=Every slot of this shard has an island.";
    int nth = n + 1;
    long coins = @PKG@.ShCfg.islandCoinsAt(nth, cv);
    long qty = item.length() == 0 ? 0L : (long) @PKG@.ShCfg.islandQty(nth);
    long t = now();
    String[] keys = new String[] { @PKG@.ShMath.ik(kd, slot, "type"), @PKG@.ShMath.ik(kd, slot, "size"), @PKG@.ShMath.ik(kd, slot, "last"), @PKG@.ShMath.ik(kd, slot, "stored") };
    String[] vals = new String[] { @PKG@.ShKind.TYPE[kd], "1", String.valueOf(t), "0" };
    String r = purchaseN(u, k, kd, p, cs, item, qty, coins, keys, vals, "island", @PKG@.ShKind.KEYS[kd] + " buy island " + nth + " in slot " + (slot + 1));
    if (r != null) return r;
    res = "+Island " + nth + " bought: a Small " + @PKG@.ShKind.TNAME[kd] + " island in slot " + (slot + 1) + ". Put a worker totem on it (Totems tab) so it makes items.";
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  @PKG@.ShWorld2.repaint(k, kd);
  return res;
}""")
M(core, "public static String buyIsland(java.util.UUID u, String k, int kd, int slot, @IC@[] cs) { String r = buyIsland0(u, k, kd, slot, cs); @PKG@.ShSnd.ok(u, r, 2); return r; }")
''')

# ---- 1. ShLv20, part 2: levels, what is due, the grant, the catch-up, the scan (before ShTick.run, which calls scan)
P.rep('''M(tick, r"""
public void run() {
  try {
    this.n++;''', '''# ================= 0.4.6 ShLv20 part 2 =================
# the level of kind kd's skill for profile k (player u): SkyySkills skill:fn:run {pkey, skill} (the class: {UUID, "class"} names the class
# skill, then {pkey, it}); without skill:fn:run the older skill:fn:level {UUID, skill / "Combat"}; -1 = unknown (no SkyySkills, not loaded)
M(lv, r"""
public static int level(java.util.UUID u, String k, int kd) {
  try {
    String sk = SKILL[kd];
    java.util.function.Function run = @PKG@.ShPay.f("skill:fn:run");
    if (run != null) {
      String nm = sk;
      if ("class".equals(sk)) {
        Object c = run.apply(new Object[] { u, "class" });
        if (!(c instanceof Object[]) || ((Object[]) c).length < 6 || !(((Object[]) c)[5] instanceof String)) return -1;
        nm = (String) ((Object[]) c)[5];
      }
      Object r = run.apply(new Object[] { k, nm });
      if (r instanceof Object[] && ((Object[]) r).length > 0 && ((Object[]) r)[0] instanceof Number) return ((Number) ((Object[]) r)[0]).intValue();
      return -1;
    }
    java.util.function.Function lf = @PKG@.ShPay.f("skill:fn:level");
    if (lf == null) return -1;
    Object r = lf.apply(new Object[] { u, "class".equals(sk) ? "Combat" : sk });
    return r instanceof Number ? ((Number) r).intValue() : -1;
  } catch (Throwable t) { @PKG@.ShCfg.warnOnce("lv20level", "reading a skill level for the level 20 shards failed (logged once): " + t); return -1; }
}""")
# the kinds profile k (player u) may get now: not recorded yet, lv20.<kind> > 0, the level reached. Any thread; never writes.
M(lv, r"""
public static int[] due(java.util.UUID u, String k) {
  if (!@PKG@.ShCfg.ON || u == null || k == null || DONE.containsKey(k)) return new int[0];
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return new int[0];
  int n = @PKG@.ShKind.N;
  boolean[] open = new boolean[n];
  int left = 0;
  @PKG@.ShStore.LOCK.lock(); try {
    for (int kd = 0; kd < n; kd++) if (@PKG@.ShStore.str(p, rk(kd)).length() == 0) { open[kd] = true; left++; }
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (left == 0) { DONE.put(k, Boolean.TRUE); return new int[0]; }
  int[] a = @PKG@.ShCfg.LV20;
  int[] out = new int[n];
  int m = 0;
  for (int kd = 0; kd < n; kd++) {
    int need = kd < a.length ? a[kd] : 0;
    if (!open[kd] || need <= 0) continue;
    if (level(u, k, kd) >= need) { out[m] = kd; m++; }
  }
  int[] r = new int[m];
  System.arraycopy(out, 0, r, 0, m);
  return r;
}""")
# give profile k's free shard of kind kd into cs (the player's WORLD THREAD). "+..." given, "=..." recorded before / the profile had that
# shard (recorded "had", nothing given), "~..." inventory full (nothing recorded - it waits), "-..." refused (nothing changed).
# Order (never two, never silently lost): the record lv20.<kind> + <kind>.crafted = 1 SAVED first, then the item (counted); no room =
# both taken back (saved) before returning "~".
M(lv, r"""
public static String grant(java.util.UUID u, String k, int kd, @IC@[] cs) {
  if (!@PKG@.ShCfg.ON) return "-Shards are switched off on this server.";
  if (!@PKG@.ShKind.ok(kd)) return "-Unknown shard.";
  if (u == null || k == null || @PKG@.ShCore.busy(u) || !k.equals(@PKG@.ShCfg.pkey(u))) return "-The profile is switching - the shard waits.";
  if (cs == null) return "-The inventory could not be read - the shard waits.";
  int[] lva = @PKG@.ShCfg.LV20;
  if (kd >= lva.length || lva[kd] <= 0) return "-No free shard of this kind on this server.";   // fix (critic shards046 #3): switched off meanwhile
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "-The shard file could not be read - the shard waits.";
  String key = rk(kd);
  String ck = @PKG@.ShMath.kk(kd, "crafted");
  String id = @PKG@.ShKind.SHARD[kd];
  String nm = @PKG@.ShKind.NAMES[kd];
  long t = @PKG@.ShCore.now();
  String hadC = null;
  @PKG@.ShStore.LOCK.lock(); try {
    if (@PKG@.ShStore.str(p, key).length() > 0) return "=The " + nm + " Shard reward is recorded already (" + @PKG@.ShStore.str(p, key) + ").";
    if (@PKG@.ShCore.hasShard(k, kd) || @PKG@.ShInv.count(cs, id) > 0L) {   // the one-shard-of-a-kind rule: it had one, so nothing more
      p.setProperty(key, "had:" + t);
      String e = @PKG@.ShStore.save(k, p);
      if (e != null) { p.remove(key); return "-The shard file could not be saved - tried again later."; }
      HAD.incrementAndGet();
      @PKG@.ShStore.log(u + " " + k + " lv20 " + @PKG@.ShKind.KEYS[kd] + " already had that shard - nothing given");
      return "=You already have your " + nm + " Shard.";
    }
    if (!@PKG@.ShInv.hasRoom(cs)) {   // fix (critic shards046 #1): no free slot = nothing written at all (no disk churn, no crash window)
      HELD.incrementAndGet();
      return "~Your " + nm + " Shard (reward for " + how(kd) + ") is waiting - make room in your inventory for it.";
    }
    hadC = p.getProperty(ck);
    p.setProperty(ck, "1");
    p.setProperty(key, "given:" + t);
    String e = @PKG@.ShStore.save(k, p);
    if (e != null) {
      if (hadC == null) p.remove(ck); else p.setProperty(ck, hadC);
      p.remove(key);
      return "-The shard file could not be saved - the shard waits.";
    }
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (@PKG@.ShInv.give(cs, id, 1L) >= 1L) {
    GIVEN.incrementAndGet();
    @PKG@.ShStore.log(u + " " + k + " lv20 give " + id + " (" + how(kd) + ")");
    return "+Reward for " + how(kd) + ": your " + nm + " Shard! Place it on your island, then right-click it.";
  }
  String lost = null;
  @PKG@.ShStore.LOCK.lock(); try {
    if (hadC == null) p.remove(ck); else p.setProperty(ck, hadC);
    p.remove(key);
    lost = @PKG@.ShStore.save(k, p);
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (lost != null) {
    @PKG@.ShCfg.warn("the level 20 " + nm + " Shard of " + k + " did not fit and its record could not be taken back: " + lost + " - give it with /shardadmin give");
    @PKG@.ShStore.log(u + " " + k + " lv20 " + id + " LOST - no room and the undo was not saved - /shardadmin give");
    return "-Your " + nm + " Shard did not fit and could not be kept for later - ask an admin (/shardadmin give).";
  }
  HELD.incrementAndGet();
  return "~Your " + nm + " Shard (reward for " + how(kd) + ") is waiting - make room in your inventory for it.";
}""")
# the chat line of a grant result (a waiting shard says so at most once a minute)
M(lv, r"""
public static void say(@PR@ pr, java.util.UUID u, int kd, String r) {
  if (r == null || r.length() == 0 || pr == null) return;
  char c = r.charAt(0);
  if (c == '+') { @PKG@.ShSay.to(pr, "[Shards] " + r.substring(1), "#39f493"); return; }
  if (c != '~') return;
  String key = u + "|" + kd;
  long now = System.currentTimeMillis();
  Object l = NAG.get(key);
  if (l instanceof Long && now - ((Long) l).longValue() < 60000L) return;
  NAG.put(key, Long.valueOf(now));
  @PKG@.ShSay.to(pr, "[Shards] " + r.substring(1), "#ffcc00");
}""")
# the world-thread part: what is due now (levels read again), each granted + said. Returns "<kind> <result>" lines (the harness reads them).
M(lv, r"""
public static String catchUp(java.util.UUID u, String k, @IC@[] cs, @PR@ pr) {
  int[] d = due(u, k);
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < d.length; i++) {
    String r = grant(u, k, d[i], cs);
    say(pr, u, d[i], r);
    if (sb.length() > 0) sb.append('\\n');
    sb.append(@PKG@.ShKind.KEYS[d[i]]).append(' ').append(r);
  }
  return sb.toString();
}""")
# ShTick (every 5 s, scheduler thread): every online player with something due gets ONE task on their own world thread (not again while one
# waits, at most 30 s)
M(lv, r"""
public static int scan() {
  if (!@PKG@.ShCfg.ON) return 0;
  SCANS.incrementAndGet();
  int q = 0;
  try {
    long now = System.currentTimeMillis();
    java.util.Iterator it = @UNI@.get().getPlayers().iterator();
    while (it.hasNext()) {
      @PR@ pr = (@PR@) it.next();
      if (pr == null || !pr.isValid()) continue;
      java.util.UUID u = pr.getUuid();
      if (u == null || @PKG@.ShCore.busy(u)) continue;
      Object pv = PENDING.get(u);
      if (pv instanceof Long && now - ((Long) pv).longValue() < 30000L) continue;
      String k = @PKG@.ShCfg.pkey(u);
      if (due(u, k).length == 0) continue;
      if (@PKG@.ShCore.busy(u) || !k.equals(@PKG@.ShCfg.pkey(u))) continue;   // the profile moved while the levels were read
      java.util.UUID wu = pr.getWorldUuid();
      @WLD@ w = wu == null ? null : @UNI@.get().getWorld(wu);
      if (w == null || !w.isAlive()) continue;
      PENDING.put(u, Long.valueOf(now));
      try { w.execute(new @PKG@.ShLv20(pr, u, k)); q++; QUEUED.incrementAndGet(); } catch (Throwable t2) { PENDING.remove(u); }
    }
  } catch (Throwable t) { @PKG@.ShCfg.warnOnce("lv20scan", "the level 20 shard check failed (logged once): " + t); }
  return q;
}""")
M(tick, r"""
public void run() {
  try {
    this.n++;''')
P.rep('''    @PKG@.ShPlace.verify(now);
''', '''    @PKG@.ShPlace.verify(now);
    if (this.n % 5L == 0L) @PKG@.ShLv20.scan();   // 0.4.6: the level 20 shards (every 5 s; a join is caught within 5 s)
''')

# ---- 1. ShLv20, part 3: the world-thread task (after ShAdmin: giveGate = same thread + not switching profile)
P.rep('''# ================= shard:fn:give (fix2''', '''# ================= 0.4.6 ShLv20 part 3: the task on the player's world thread =================
M(lv, r"""
public void run() {
  try {
    if (this.pr == null || !this.pr.isValid()) return;
    @REF@ r = this.pr.getReference();
    if (r == null || !r.isValid()) return;
    if (@PKG@.ShAdmin.giveGate(this.u, this.pr.getUsername(), r) != null) return;   // another world now / switching profile: the next scan
    catchUp(this.u, this.k, @PKG@.ShInv.containers(r.getStore(), r), this.pr);
  } catch (Throwable t) { @PKG@.ShCfg.warnOnce("lv20run", "giving a level 20 shard failed (logged once): " + t); }
  finally { PENDING.remove(this.u); }
}""")

# ================= shard:fn:give (fix2''')
P.rep('''ALLC = [cfg, smig, smig45, st, knd,''', '''ALLC = [cfg, smig, smig45, smig46, st, knd, lv,''')   # 0.4.6: + ShMig046, ShLv20

# ---- fix (critic shards046 #1): ShInv.hasRoom = an empty slot in storage / hotbar / backpack (a shard never stacks onto one already held:
# grant() records "had" for that first)
P.rep('''# fix (critic shards03): a stack is PLAIN when it carries no metadata''', '''M(inv, r"""
public static boolean hasRoom(@IC@[] cs) {
  if (cs == null) return false;
  for (int i = 0; i < cs.length; i++) {
    if (cs[i] == null) continue;
    short cap = cs[i].getCapacity();
    for (short j = 0; j < cap; j++) {
      @IS@ it = cs[i].getItemStack(j);
      if (it == null || it.isEmpty()) return true;
    }
  }
  return false;
}""")
# fix (critic shards03): a stack is PLAIN when it carries no metadata''')

# ---- the bench lists no switched-off shard recipe
P.rep('''  for (int i = 0; i < n; i++) if (@PKG@.ShKind.ofShard(@PKG@.ShCfg.CRAFT_ID[i]) >= 0) { list[m] = i; m++; }''',
      '''  for (int i = 0; i < n; i++) if (@PKG@.ShKind.ofShard(@PKG@.ShCfg.CRAFT_ID[i]) >= 0 && @PKG@.ShCore.recipe(@PKG@.ShCfg.CRAFT[i]) != null) { list[m] = i; m++; }   // 0.4.6: an off shard recipe is not listed''')

# ---- 3. the Islands tab: an empty slot shows its price + Buy island (the owner)
P.rep('''"Pick a slot to see its island. Islands grow in place; more island types come in a later update."''',
      '''"Pick a slot to see its island, or an empty slot to buy one. Islands grow in place."''')
P.rep('''ig.append((IR, SUI.button(P + "IGrow", "Grow island", "secondary", w=RW - 24)))          # 0.4.2: Secondary
''', '''ig.append((IR, SUI.button(P + "IGrow", "Grow island", "secondary", w=RW - 24)))          # 0.4.2: Secondary
ibq = seg("ibuy")
ibq.append((IR, SUI.button(P + "IBuy", "Buy island", "secondary", w=RW - 24)))          # 0.4.6: an empty slot (the owner)
''')
P.rep('''            v.extend(SEG["iside"]); v.extend(SEG["igrow"])''', '''            v.extend(SEG["iside"]); v.extend(SEG["ibuy" if sel == 1 else "igrow"])   # 0.4.6: one variant with Buy island''')
P.rep('''binds([(P + "IGrow", "grow")]), "    }",''', '''binds([(P + "IGrow", "grow")]), "    }",
    "    if (this.bCan && this.mine) {", jseg("ibuy"), binds([(P + "IBuy", "ibuy")]), "    }",          # 0.4.6''')
P.rep('''"public boolean iCan;", "public int tN;",''', '''"public boolean iCan;", "public boolean bCan;", "public int tN;",''')
P.rep('''this.uCan = false; this.iCan = false;''', '''this.uCan = false; this.iCan = false; this.bCan = false;''')
P.rep('''  double xpP = 0.0;   // 0.4.4: the preview's XP before the percent (each island at its own totem tiers)
  long purse = @PKG@.ShPay.coins(this.me);''', '''  double xpP = 0.0;   // 0.4.4: the preview's XP before the percent (each island at its own totem tiers)
  long purse = @PKG@.ShPay.coins(this.me);
  double icv = @PKG@.ShCfg.curve(@PKG@.ShCfg.ISL_LV);   // 0.4.6: the island price curve (the bridge asked outside the lock)''')
P.rep('''      this.iTitle = "Slot " + (s + 1) + " - empty";
      this.iTx[0] = "Pick an island type for this slot.";
      this.iTx[1] = tn + " already has its island.";
      this.iTx[2] = "More island types come in a later update.";''', '''      this.iTitle = "Slot " + (s + 1) + " - empty";
      if (!ownedNow) {   // 0.4.6
        this.iTx[0] = "No " + nm + " Shard yet.";
        this.iTx[1] = @PKG@.ShLv20.src(kd, true) + ".";
      } else {   // 0.4.6: buy the next island here (the Nth of the shard, whatever slot)
        int nth = islands + 1;
        long bc = @PKG@.ShCfg.islandCoinsAt(nth, icv);
        String bi = @PKG@.ShCfg.islandItem(kd);
        long bq = bi.length() == 0 ? 0L : (long) @PKG@.ShCfg.islandQty(nth);
        long hb = bq > 0L ? @PKG@.ShInv.count(cs, bi) : 0L;
        this.iTx[0] = "Buy a Small " + tn + " island here.";
        this.iTx[1] = "Island " + nth + " of 6" + (nth < 6 ? " - each next one costs x" + @PKG@.ShCfg.dec(@PKG@.ShCfg.ISL_STEP) + "." : " - the last one.");
        this.iTx[2] = "It makes items once a worker totem stands on it.";
        this.iTx[5] = "Cost";
        this.iTx[6] = have(purse, bc, "coins");
        this.iCol[6] = (purse < 0L || purse >= bc) ? "@GOOD@" : "@BAD@";
        if (bq > 0L) {
          this.iTx[7] = have(cs == null ? -1L : hb, bq, @PKG@.ShTotem.pretty(bi));
          this.iCol[7] = (cs != null && hb >= bq) ? "@GOOD@" : "@BAD@";
        }
        this.bCan = true;
      }''')
P.rep('''    if (a.equals("grow")) return @PKG@.ShCore.grow(u, k, kd, this.sel, invOf(ref, st));''',
      '''    if (a.equals("grow")) return @PKG@.ShCore.grow(u, k, kd, this.sel, invOf(ref, st));
    if (a.equals("ibuy")) return @PKG@.ShCore.buyIsland(u, k, kd, this.sel, invOf(ref, st));   // 0.4.6''')

# ---- the ready line + the manifest
P.rep('''shard crafting from rebirth " + @PKG@.ShCfg.SHARD_RB + "; /shardadmin''',
      '''LEVEL 20 SHARDS (0.4.6: Mining / Foraging + Orchard / Farming / Beastmastery = Ranching / class = Combat, once per profile; the old shard recipes off), islands 2-6 bought on the coin curve (island 2 " + @PKG@.ShCfg.num(@PKG@.ShCfg.islandCoins(2)) + " coins); /shardadmin''')
P.rep('''and shard crafting from rebirth 2. Protected by''', '''shards are free at level 20 (0.4.6: Mining / Foraging + Orchard / Farming / Beastmastery = Ranching / class = Combat), islands 2-6 bought for coins + Enchanted materials. Protected by''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0
P.finish()
