"""Derive SkyyTrees/build_skyytrees_0.4.9.py from SkyyTrees 0.4.8 (build_skyytrees_0.4.8.py = the tools/deploy_set.py SET pin, itself GENERATED
by tools/trees_0_4_8_patch.py). Edit THIS patch (and the numbers in tools/trees_v3_data.py / tools/trees_v3_effects.py), never the generated
script. Every anchor is asserted once; at the end every change is undone on a copy and compared with 0.4.8 (tools/soundpass_gen.Patch).
Run:
    python tools/trees_0_4_9_patch.py && python SkyyTrees/build_skyytrees_0.4.9.py && python SkyyTrees/test_skyytrees_0.4.9.py
Balance P7 economy, second group (P7b): pins with SkyyExploration 0.3.3 (the applier of Wanderer / Cartographer) + SkyySkills 0.4.61 +
SkyyShards 0.4.5. NOTE: tools/trees_v3_effects.py now holds the 2 SkyyExploration rows, so the OLD generated 0.4.8 script's own assert "the
gate keys = every upgrade key" no longer holds if it is re-run (its jar is built and pinned; the same as 0.4.7's script after P8d).
"""
import os, sys, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G
import trees_v3_data as V3D
import trees_v3_effects as V3E
import balance_model as BM

V3E.check()
P7B_ROWS = V3E.rows("SkyyExploration")
assert [(e[0], e[1], e[2], e[4]) for e in P7B_ROWS] == [("Exploration", 1, "r1a", "lg.coins"), ("Exploration", 1, "r3a", "lg.coin2")]
assert V3E.EFFECTS[-2:] == P7B_ROWS, "P7b: the 2 SkyyExploration rows are appended last"
CURVE_TEXT = BM.P7_CURVE_TEXT
_cn = open(os.path.join(ROOT, "SkyyCoins", "build_skyycoins_0.1.10.py"), encoding="utf8").read()
assert ("CURVE_TEXT = '%s'" % CURVE_TEXT) in _cn, "the built-in curve copy must equal SkyyCoins 0.1.10's coins.curve default"
RB10 = BM.p7_round(BM.P7_RESPEC_H * BM.p7_H_at(10))     # spec 6.2: a paid respec = 0.25 h of income at the tree's level, Lv-10 base
assert RB10 == 2100, RB10
RB_EX = dict((L, BM.p7_round(RB10 * BM.p7_curve_from_text(CURVE_TEXT, L))) for L in (1, 10, 20, 30, 50, 70, 90, 100))
assert RB_EX[10] == 2100 and RB_EX[50] == 77500 and RB_EX[90] == 980000, RB_EX

NOTE = '''0.4.9 (2026-10-22) = BALANCE PASS P7 ECONOMY, the SkyyTrees part (research/Balance-P7-Economy-Spec.md 6.2 + 9; FULL round P7b with
  SkyySkills 0.4.61, SkyyExploration 0.3.3, SkyyShards 0.4.5). Skyy: "work through your whole list." + "keep going down the list. dont stop
  until the entire list is done" + popup "x10 targets (Recommended)" (spec Q10 default: tree respec costs follow the coin curve) + popup
  "Keep the no-boost rule (Recommended)" (Wanderer + Cartographer get a non-XP effect; Exploration XP gets no tree bonus).
  1. RESPEC ON THE COIN CURVE: the n-th PAID respec of a tree this run (the first each run stays free; n at most respec.maxSteps 5) costs
     n x round(respec.base 2,100 x the coin curve at the tree's level) (SkyyCoins' coins:fn:curve, 0.1.10+; the built-in copy of its default
     without it; rounded 10 / 100 / 500 / 5,000) = 0.25 h of income at that level: Lv 10 2,100, Lv 30 %s, Lv 50 %s, Lv 70 %s,
     Lv 90 %s (x n). Class trees use the same rule (their level = the class level). NEW ROWS (Server Setup -> Trees -> General):
     respec.curve "Respec follows the coin curve" (bool, default true; off = the old respec.perLevel x level x n) and respec.base "Respec
     cost at Lv 10" (int coins, default 2100). respec.perLevel's help says it counts only with the curve off.
  2. WANDERER + CARTOGRAPHER GO LIVE (Exploration b1 r1a / r3a; tools/trees_v3_data.py P7B_TEXT, tools/trees_v3_effects.py EFFECTS applier
     SkyyExploration): Wanderer "+4%% coins/rank from Loot Bags and supply drops" (coins only, never Exploration XP), Cartographer "+5%% chance/rank a Loot
     Bag or supply drop holds a second coin find" - sold while tree:reads:SkyyExploration lists them (SkyyExploration 0.3.3). Exploration XP
     stays pure (V3E.check: no xp. row in the Exploration tree). GATES (fixed at build time): only the Exploration tree's gates move (they
     rise: the 8 new ranks count); the live NewBetaTest files hold no Exploration rank, so nothing is grandfathered; ranks always count.
  3. ONE-TIME UPDATE TreeMigP7 (PROJECT-RULES 4; TreeMigP5's kit calls, Collections CollP7Mig's rule): ONCE on an existing trees.properties,
     setup() right after TreeMigP5: when respec.perLevel holds an admin's value (not 100) respec.curve=false is appended (their linear price
     keeps working) + one INFO line + one change-log row (Undo); otherwise nothing but the run-once marker (absent keys = the defaults).
     History copy first (verified), a Properties check (at most respec.curve added), bytes + line endings kept; a fresh file carries the
     marker and both new lines.
  Pocket Change (spec 2.3 pocket.coinsLv10): NOT built - Mining.MCoins / Foraging.FCoins are dead since 0.4.0 (V3_DEAD_042; no v3 upgrade
  aliases them), so there is no proc to re-price.
  SAVED DATA: none (player files, ranks, respec counters untouched). ROLLBACK to 0.4.8: safe (respec.base / respec.curve ignored -> 100 x
  level x n; Wanderer / Cartographer coming soon again, ranks stay saved and unused until a respec); with SkyyExploration 0.3.2.
''' % tuple("{:,}".format(RB_EX[L]) for L in (30, 50, 70, 90))

P = G.Patch(os.path.join(ROOT, "SkyyTrees", "build_skyytrees_0.4.8.py"), os.path.join(ROOT, "SkyyTrees", "build_skyytrees_0.4.9.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.4.8"') and P.has("0.4.8 (2026-10-22)") and not P.has("0.4.9 (2026-10-22)"), "not the generated SkyyTrees 0.4.8 script"
REG0, SYS0, CLS0 = P.s.count("registerCommand("), P.s.count("registerSystem("), P.s.count("makeClass(")

P.rep('''"""SkyyTrees 0.4.8 - build script (javassist via jpype, tools/skyybuild.py). Owner: Skyy (they/them).
GENERATED by tools/trees_0_4_8_patch.py from build_skyytrees_0.4.7.py (the SET pin) - edit the patch, not this file.
''', '''"""SkyyTrees 0.4.9 - build script (javassist via jpype, tools/skyybuild.py). Owner: Skyy (they/them).
GENERATED by tools/trees_0_4_9_patch.py from build_skyytrees_0.4.8.py (the SET pin) - edit the patch, not this file.
''' + NOTE + '''
SkyyTrees 0.4.8 - GENERATED by tools/trees_0_4_8_patch.py from build_skyytrees_0.4.7.py:
''')
P.rep('VERSION = "0.4.8"', 'VERSION = "0.4.9"')

# ---------- 1. the gate keys: + the SkyyExploration rows (P7b)
P.rep('''V3_R3B_KEYS = V3_R3B_KEYS_047 | V3_P8D_KEYS
assert len(V3_R3B_KEYS_042) == 23''', '''V3_R3B_KEYS_048 = V3_R3B_KEYS_047 | V3_P8D_KEYS
# 0.4.9 (Balance P7b): Wanderer + Cartographer, applied by SkyyExploration 0.3.3 (coins only)
V3_P7B_KEYS = set(V3E.key(_e[0], _e[1], _e[2]) for _e in V3E.EFFECTS if _e[3] == "SkyyExploration")
V3_R3B_KEYS = V3_R3B_KEYS_048 | V3_P7B_KEYS
assert V3_P7B_KEYS == set(["Skill.Exploration.b1.r1a", "Skill.Exploration.b1.r3a"]) and not V3_P7B_KEYS & V3_R3B_KEYS_048
assert len(V3_R3B_KEYS_042) == 23''')
P.rep('''assert V3_R3B_KEYS == set(V3E.key(_e[0], _e[1], _e[2]) for _e in V3E.EFFECTS if not V3E.is_free(_e[2])), "0.4.8: the gate keys = every upgrade key of tools/trees_v3_effects.py (23 R3b + 4 R3c + 25 P8b + 18 P8c + 13 P8d)"''',
      '''assert V3_R3B_KEYS == set(V3E.key(_e[0], _e[1], _e[2]) for _e in V3E.EFFECTS if not V3E.is_free(_e[2])), "0.4.9: the gate keys = every upgrade key of tools/trees_v3_effects.py (23 R3b + 4 R3c + 25 P8b + 18 P8c + 13 P8d + 2 P7b)"''')
P.rep('''V3_R3B_MODS = ["SkyyGear", "SkyyPets", "SkyyAccessories", "SkyySkills", "SkyyCooking", "SkyyFishing"]
V3_R3B_MODS += ["SkyyTrees", "SkyyClasses", "SkyyMobs"]   # 0.4.6 P8b: SkyyTrees' own TreeSk rows + the Combat fight / loot rows''',
      '''# 0.4.9 P7b: V3_GATES above = the 0.4.8 table; the shipped table = the 0.4.8 rule + Wanderer / Cartographer (SkyyExploration 0.3.3)
V3_GATES_048 = list(V3_GATES)


def _v3_hooked_049(_u):
    return (_u["hk"] == 0 and _u["key"] in V3_P7B_KEYS) or _v3_hooked_048(_u)


V3_GATES = []
for _tv in range(NV3):
    _cap = [0] * 8
    for _u in V3_UP:
        if _u["tv"] == _tv and _v3_hooked_049(_u):
            _cap[V3_RW[_u["row"]]["num"]] += _u["max"] * _u["cost"]
    _g, _below = [0] * 8, 0
    for _n in range(1, 8):
        _g[_n] = min(V3D.GATE_STEP * (_n - 1), _below)
        _below += _cap[_n]
    V3_GATES.extend(_g)
_MOVED_049 = [(V3T[_tv]["name"], _n, V3_GATES_048[_tv * 8 + _n], V3_GATES[_tv * 8 + _n]) for _tv in range(NV3) for _n in range(1, V3_ROWS_N[_tv] + 1)
              if V3_GATES[_tv * 8 + _n] != V3_GATES_048[_tv * 8 + _n]]
assert _MOVED_049 and set(_m[0] for _m in _MOVED_049) == {"Exploration"}, "0.4.9: only the Exploration gates move: %s" % _MOVED_049
assert all(V3_GATES[_i] >= V3_GATES_048[_i] for _i in range(len(V3_GATES))), "0.4.9: a gate only rises"
assert all(V3_GATES[_r["tv"] * 8 + _r["num"]] == V3_GATES_048[_r["tv"] * 8 + _r["num"]] for _r in V3_RW if _r["fk"] != 0), "0.4.9: a live free perk would move"
_EX_TV = [_tv for _tv in range(NV3) if V3T[_tv]["name"] == "Exploration"][0]
_below = 0
for _n in range(1, V3_ROWS_N[_EX_TV] + 1):
    assert V3_GATES[_EX_TV * 8 + _n] <= _below, ("0.4.9: an Exploration row needs more points than its rows below can take", _n)
    _below += sum(_u["max"] * _u["cost"] for _u in V3_UP if _u["tv"] == _EX_TV and V3_RW[_u["row"]]["num"] == _n and _v3_hooked_049(_u))
_P7B_RANKS = sum(_u["max"] for _u in V3_UP if _u["key"] in V3_P7B_KEYS)
assert _P7B_RANKS == 8, _P7B_RANKS
print("0.4.9 P7b Exploration gates (0.4.8 -> 0.4.9): %s -> %s; + %d ranks (Wanderer 5, Cartographer 3)" % (
      "/".join(str(V3_GATES_048[_EX_TV * 8 + _n]) for _n in range(1, V3_ROWS_N[_EX_TV] + 1)),
      "/".join(str(V3_GATES[_EX_TV * 8 + _n]) for _n in range(1, V3_ROWS_N[_EX_TV] + 1)), _P7B_RANKS))
V3_R3B_MODS = ["SkyyGear", "SkyyPets", "SkyyAccessories", "SkyySkills", "SkyyCooking", "SkyyFishing"]
V3_R3B_MODS += ["SkyyTrees", "SkyyClasses", "SkyyMobs"]   # 0.4.6 P8b: SkyyTrees' own TreeSk rows + the Combat fight / loot rows
V3_R3B_MODS += ["SkyyExploration"]   # 0.4.9 P7b: Wanderer + Cartographer (Loot Bag / supply drop coins)''')

# ---------- 2. the respec price on the coin curve: TreeCurve + TreeCfg fields / load + TreeV3.price
P.rep('''cfg = pool.makeClass(PKG + ".TreeCfg")''', '''cfg = pool.makeClass(PKG + ".TreeCfg")
tcur = pool.makeClass(PKG + ".TreeCurve")       # 0.4.9 Balance P7: the coin curve (coins:fn:curve + the built-in copy) for the respec price''')
P.rep('''             "long V3_RBASE = 100L", "int V3_RSTEPS = 5", "long V3_DDIV = 1000L", "long V3_DCAP = 5000L"):''',
      '''             "long V3_RBASE = 100L", "int V3_RSTEPS = 5", "long V3_DDIV = 1000L", "long V3_DCAP = 5000L",
             # 0.4.9 Balance P7: respec.base (the Lv-10 price of one paid respec) + respec.curve (on = x the coin curve; off = respec.perLevel x level)
             "long V3_RB10 = %dL" % RB10_049, "boolean V3_RCURVE = true"):''')
P.rep('''  V3_RSTEPS = (int) clampL(lng(p, "respec.maxSteps", 5L), 1L, 100L);''',
      '''  V3_RSTEPS = (int) clampL(lng(p, "respec.maxSteps", 5L), 1L, 100L);
  V3_RB10 = clampL(lng(p, "respec.base", ''' + str(RB10) + '''L), 0L, 1000000000L);                       // 0.4.9 Balance P7: one paid respec at Lv 10
  V3_RCURVE = bool(p, "respec.curve", true);                                               // 0.4.9: x the coin curve (off = perLevel x level)''')
TCUR = r'''# 0.4.9 Balance P7 (research/Balance-P7-Economy-Spec.md 6.2): TreeCurve = SkyyCoins' coins:fn:curve (0.1.10+) or the built-in copy of its
# default (asserted = its text), rounded like every P7 cost (10 / 100 / 500 / 5,000). cost(base, level) = round(base x curve(level)).
CV049 = %r
F(tcur, "public static final int[] CV_LV = new int[] { %%s };" %% ", ".join(kv.split(":")[0] for kv in CV049.split(",")))
F(tcur, "public static final double[] CV_F = new double[] { %%s };" %% ", ".join(repr(float(kv.split(":")[1])) for kv in CV049.split(",")))
M(tcur, r"""
public static double curveOwn(int level) {
  int x = level < 1 ? 1 : (level > 100 ? 100 : level);
  int i = 0;
  if (x >= CV_LV[CV_LV.length - 1]) i = CV_LV.length - 2;
  else { while (i < CV_LV.length - 2 && x > CV_LV[i + 1]) i++; }
  double a = Math.log(CV_F[i]);
  double b = Math.log(CV_F[i + 1]);
  return Math.exp(a + (b - a) * (double) (x - CV_LV[i]) / (double) (CV_LV[i + 1] - CV_LV[i]));
}""")
M(tcur, r"""
public static double curve(int level) {
  try {
    Object o = System.getProperties().get("skyy.bridge");
    Object f = o instanceof java.util.Map ? ((java.util.Map) o).get("coins:fn:curve") : null;
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(Integer.valueOf(level));
      if (r instanceof Number && ((Number) r).doubleValue() > 0.0 && !Double.isInfinite(((Number) r).doubleValue())) return ((Number) r).doubleValue();
    }
  } catch (Throwable t) { }
  return curveOwn(level);
}""")
M(tcur, r"""
public static long round(double x) {
  if (!(x > 0.0)) return 0L;
  if (x >= 1.0E15) return 1000000000000000L;
  double st = x < 1000.0 ? 10.0 : (x < 10000.0 ? 100.0 : (x < 100000.0 ? 500.0 : 5000.0));
  return (long) (st * Math.floor(x / st + 0.5));
}""")
M(tcur, "public static long cost(long base, int level) { return base <= 0L ? 0L : round((double) base * curve(level)); }")
M(tcur, r"""
public static long times(long a, long n) {
  if (a <= 0L || n <= 0L) return 0L;
  if (a > 1000000000000000L / n) return 1000000000000000L;
  return a * n;
}""")
''' % CURVE_TEXT
P.rep('''# the respec price (spec 2.6 + Skyy's answer): the first respec of a tree each run is free; then respec.perLevel x level x min(n, steps)''',
      TCUR + '''# the respec price (spec 2.6 + Skyy's answer): the first respec of a tree each run is free; then respec.perLevel x level x min(n, steps)
# (0.4.9 Balance P7: with respec.curve on, min(n, steps) x round(respec.base x the coin curve at the tree's level))''')
P.rep('''  long l = lvl < 1 ? 1L : (long) lvl;
  return @PKG@.TreeCfg.V3_RBASE * l * n;''', '''  long l = lvl < 1 ? 1L : (long) lvl;
  if (@PKG@.TreeCfg.V3_RCURVE) return @PKG@.TreeCurve.times(@PKG@.TreeCurve.cost(@PKG@.TreeCfg.V3_RB10, (int) (l > 1000L ? 1000L : l)), n);   // 0.4.9 Balance P7
  return @PKG@.TreeCfg.V3_RBASE * l * n;''')
P.rep('''+ " upgrades, 1 point a level, respec " + @PKG@.TreeCfg.V3_RBASE + " x level x n (max " + @PKG@.TreeCfg.V3_RSTEPS + ")''',
      '''+ " upgrades, 1 point a level, respec " + (@PKG@.TreeCfg.V3_RCURVE ? @PKG@.TreeCfg.V3_RB10 + " x the coin curve x n (Lv 10 / 50 / 90: " + @PKG@.TreeCurve.cost(@PKG@.TreeCfg.V3_RB10, 10) + " / " + @PKG@.TreeCurve.cost(@PKG@.TreeCfg.V3_RB10, 50) + " / " + @PKG@.TreeCurve.cost(@PKG@.TreeCfg.V3_RB10, 90) + ")" : @PKG@.TreeCfg.V3_RBASE + " x level x n") + " (max " + @PKG@.TreeCfg.V3_RSTEPS + ")''')

# ---------- 3. the fresh default file + the Server Setup rows
P.rep('''                "respec.perLevel=100", "respec.maxSteps=5",''', '''                "respec.perLevel=100", "respec.maxSteps=5",
                # 0.4.9 Balance P7 (TreeMigP7's marker: a fresh file needs no update)
                "# " + MKP7_ID + ": respec.curve true - a paid respec costs respec.base (the price at Lv 10) x the SkyyCoins coin curve at",
                "# the tree's level x n (Lv 50 about 77,500, Lv 90 about 980,000); false - the old respec.perLevel x level x n.",
                "respec.curve=true", "respec.base=%d" % RB10_049,''')
P.rep('''MKP5_ID = "Balance P5 power (SkyyTrees 0.4.5)"   # 0.4.5: TreeMigP5's run-once marker (a new default file carries it: nothing to move)''',
      '''MKP5_ID = "Balance P5 power (SkyyTrees 0.4.5)"   # 0.4.5: TreeMigP5's run-once marker (a new default file carries it: nothing to move)
MKP7_ID = "Balance P7 economy (SkyyTrees 0.4.9)"   # 0.4.9: TreeMigP7's run-once marker (a new default file carries it)
RB10_049 = %d   # 0.4.9 Balance P7: respec.base default = tools/balance_model.py p7_round(0.25 h x the Lv 10 hour) (tools/trees_0_4_9_patch.py asserts it)''' % RB10)
P.rep('''    ("respec.perLevel", "Respec price per level", "general", "int", "100", "0", "1000000000", "", "coins", "live",
     "Price = tree level x this x the paid respecs of that tree this run. The first respec a run is free.", "reload"),''',
      '''    ("respec.perLevel", "Respec price per level", "general", "int", "100", "0", "1000000000", "", "coins", "live",
     "Only with the coin curve off: price = tree level x this x the paid respecs of that tree this run.", "reload"),
    # 0.4.9 Balance P7 (research/Balance-P7-Economy-Spec.md 6.2 / 9.2)
    ("respec.curve", "Respec follows the coin curve", "general", "bool", "true", "", "", "", "", "live",
     "On: Respec cost at Lv 10 x the coin curve at the tree's level x n. Off: the per-level price.", "reload"),
    ("respec.base", "Respec cost at Lv 10", "general", "int", str(RB10_049), "0", "1000000000", "step=100", "coins", "live",
     "One paid respec at Lv 10 (x n for the n-th this run); grows with the coin curve. First a run: free.", "reload"),''')
P.rep('''assert len(CFG_ROWS) == 4 + 1 + 16 + len(TREES) + 1, len(CFG_ROWS)''',
      '''assert len(CFG_ROWS) == 4 + 1 + 16 + len(TREES) + 1 + 2, len(CFG_ROWS)   # 0.4.9: + respec.curve, respec.base''')

# ---------- 4. TreeMigP7 (after TreeMigP5: its kit calls)
MIGP7 = r'''
# ================= 0.4.9 TreeMigP7: the ONE-TIME Balance P7 respec update of an existing trees.properties =========
# setup() only, right AFTER TreeMigP5 (PROJECT-RULES 4; TreeMigP5's kit calls + SkyyCollections CollP7Mig's text rule, copied by
# tools/trees_0_4_9_patch.py): respec.perLevel holding an admin's value (a number other than 100; a doubled / continued line counts as one)
# -> respec.curve=false appended (their linear price keeps working; INFO + one change-log row, Undo); a missing / default line -> nothing
# but the marker (the new keys' absent = the defaults: curve on, base 2100). A file that already has respec.curve keeps it. The marker LAST.
# Properties check (at most respec.curve added); History copy verified (mgSaved) first. A failure = WARN, file untouched, next start again.
MARKP7_LINE = "# ---------- SkyyTrees 0.4.9 (marker %s, runs once): respec costs follow the coin curve (respec.base x the curve at the tree's level); an admin's respec.perLevel keeps its linear price (respec.curve false) ----------" % MKP7_ID
assert all(ord(_c) < 128 for _c in MARKP7_LINE) and "=" not in MARKP7_LINE
assert DEFAULTS_V3.count(MKP7_ID) == 1 and [l for l in DEFAULTS_V3.splitlines() if MKP7_ID in l][0].startswith("# ")
assert ("\nrespec.curve=true\nrespec.base=%d\n" % RB10_049) in DEFAULTS_V3
migP7 = pool.makeClass(PKG + ".TreeMigP7")
for _d in ("public static final String MK = %s;" % json.dumps(MKP7_ID),
           'public static final String WHO = "SkyyTrees 0.4.9";',
           "public static final String MARK_LINE = %s;" % json.dumps(MARKP7_LINE)):
    F(migP7, _d)
M(migP7, r"""
public static boolean marked(java.util.ArrayList l) {
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) { if (s.indexOf(MK) >= 0) return true; k++; continue; }
    k = @PKG@.CfgFile.end(l, k) + 1;
  }
  return false;
}""")
M(migP7, r"""
public static boolean isDef(String v) {
  if (v == null) return true;
  String t = v.trim();
  if (t.equals("100")) return true;
  try { return Double.parseDouble(t) == 100.0; } catch (Throwable e) { return false; }
}""")
# pure text step. null = the marker is there or the text cannot be read; else { new text, Boolean added, String note, String[] rows }
M(migP7, r"""
public static Object[] update(String text) {
  try {
    java.util.ArrayList l = @PKG@.CfgFile.split(text);
    if (marked(l)) return null;
    java.util.Properties p = new java.util.Properties();
    p.load(new java.io.StringReader(text));
    String per = p.getProperty("respec.perLevel");
    boolean has = p.getProperty("respec.curve") != null;
    boolean add = !has && !isDef(per);
    String eol = text.indexOf("\r\n") >= 0 ? "\r\n" : "\n";
    StringBuilder sb = new StringBuilder(text.length() + MARK_LINE.length() + 64);
    sb.append(text);
    if (text.length() > 0 && !text.endsWith("\n")) sb.append(eol);
    String last = text.endsWith("\n") ? text.substring(0, text.length() - 1) : text;
    if (last.endsWith("\r")) last = last.substring(0, last.length() - 1);
    int bs = 0;
    for (int i = last.length() - 1; i >= 0 && last.charAt(i) == '\\'; i--) bs++;
    if (bs % 2 == 1) sb.append(eol);   // the file ends inside a continued entry: a blank line first, so nothing joins it
    if (add) sb.append("respec.curve=false").append(eol);
    sb.append(MARK_LINE).append(eol);
    String note = add ? "respec.perLevel=" + @PKG@.CfgRows.oneLine(per.trim()) + " kept (an admin's value) - respec.curve=false keeps the linear price perLevel x level x n (the 0.4.9 default is respec.base 2100 x the coin curve)"
                      : (has ? "respec.curve already in the file - kept" : "");
    String[] rows = add ? new String[] { "respec.curve", "true", "false" } : new String[0];
    return new Object[] { sb.toString(), Boolean.valueOf(add), note, rows };
  } catch (Throwable t) { return null; }
}""")
M(migP7, r"""
public static boolean sameAfter(byte[] old, byte[] nb, boolean add) {
  try {
    java.util.Properties a = new java.util.Properties();
    java.util.Properties b = new java.util.Properties();
    a.load(new java.io.ByteArrayInputStream(old));
    b.load(new java.io.ByteArrayInputStream(nb));
    if (b.size() != a.size() + (add ? 1 : 0)) return false;
    java.util.Iterator it = a.stringPropertyNames().iterator();
    while (it.hasNext()) {
      String k = (String) it.next();
      if (!a.getProperty(k).equals(b.getProperty(k))) return false;
    }
    return !add || "false".equals(b.getProperty("respec.curve"));
  } catch (Throwable t) { return false; }
}""")
M(migP7, r"""
public static synchronized String run(java.nio.file.Path base) {
  if (base == null) return "";
  java.nio.file.Path f = base.resolve("trees.properties");
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";   // a new file is written with the marker
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = update(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    boolean add = ((Boolean) r[1]).booleanValue();
    if (!sameAfter(old, data, add)) {
      @PKG@.TreeCfg.warn("trees.properties NOT updated for SkyyTrees 0.4.9 (Balance P7 respec): the update would change more than it should (the file is used as it is; the next start tries again)");
      return "";
    }
    int fi = @PKG@.TreeMig.fileIdx();
    if (fi < 0) return "";
    @PKG@.TreeMig.mgKit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(fi, old, @PKG@.CfgHist.stamp(), WHO, "before the 0.4.9 Balance P7 update");
    if (!@PKG@.TreeMig.mgSaved(fi, old)) {
      @PKG@.TreeCfg.warn("trees.properties NOT updated for SkyyTrees 0.4.9 (Balance P7 respec): the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the file is used as it is; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] rows = (String[]) r[3];
    for (int i = 0; i + 2 < rows.length; i += 3) @PKG@.CfgLog.enqueue(@PKG@.CfgLog.now() + "\t" + WHO + "\t-\tupdate\t" + rows[i] + "\t" + rows[i + 1] + "\t" + rows[i + 2] + "\tok");
    if (rows.length > 0) @PKG@.CfgLog.flush();
    @PKG@.TreeCfg.load();
    String note = (String) r[2];
    String msg = "trees.properties updated for SkyyTrees 0.4.9 (Balance P7: respec costs follow the coin curve - respec.base " + @PKG@.TreeCfg.V3_RB10 + " at Lv 10)" + (note.length() > 0 ? "; " + note : "") + " [marker " + MK + " added, runs once; Server Setup -> Trees -> Changes can undo a changed line]";
    @PKG@.TreeCfg.info(msg);
    return msg;
  } catch (Throwable t) {
    @PKG@.TreeCfg.warn("could not update trees.properties for SkyyTrees 0.4.9 (Balance P7 respec; the file is used as it is): " + t);
    return "";
  }
}""")
'''
P.rep('''
# ================= commands (HANDOFF command rules) =================
def open_body(tree_expr):''', MIGP7 + '''
# ================= commands (HANDOFF command rules) =================
def open_body(tree_expr):''')
P.rep('''  @PKG@.TreeMigP5.run(base);   // 0.4.5: Balance P5 - Rich Seams Mining.MFortune per 0.1 -> 0.025, once, only while untouched (History first; Undo)''',
      '''  @PKG@.TreeMigP5.run(base);   // 0.4.5: Balance P5 - Rich Seams Mining.MFortune per 0.1 -> 0.025, once, only while untouched (History first; Undo)
  @PKG@.TreeMigP7.run(base);   // 0.4.9: Balance P7 - respec on the coin curve; an admin's respec.perLevel keeps its linear price (History first; Undo)''')
P.rep('''       migP5,         # 0.4.5: + the Balance P5 Rich Seams update''', '''       migP5,         # 0.4.5: + the Balance P5 Rich Seams update
       tcur, migP7,   # 0.4.9: + TreeCurve (the coin curve) + the Balance P7 respec update''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0 and P.s.count("makeClass(") == CLS0 + 2
_i = P.s.index
assert _i("public static long cost(long base, int level)") < _i("public static long price(@PKG@.TreeData d, int tv, int lvl)")
assert _i("RB10_049 = ") < _i('"long V3_RB10 = %dL" % RB10_049') and _i("MKP7_ID = ") < _i('"# " + MKP7_ID + ": respec.curve true')
P.finish()
