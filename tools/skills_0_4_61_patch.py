"""Derive SkyySkills/build_skyyskills_0.4.61.py from the GENERATED SkyySkills 0.4.60 (build_skyyskills_0.4.60.py = the tools/deploy_set.py SET
pin, made by tools/skills_0_4_60_patch.py). Every anchor is asserted once; at the end every change is undone on a copy and compared with
0.4.60 (tools/soundpass_gen.Patch). Line endings kept. Edit THIS file, never the generated script.
Run:  python tools/skills_0_4_61_patch.py   then   python SkyySkills/build_skyyskills_0.4.61.py   (never --deploy)
      then  python SkyySkills/test_skyyskills_0.4.61.py
Balance P7 economy, second group (P7b): pins with SkyyTrees 0.4.9 + SkyyExploration 0.3.3 + SkyyShards 0.4.5 (and joins the P7a pair SkyyBazaar
0.2.1 + SkyyCollections 0.2.32 - the spec's "Bazaar + Collections + Skills pin together").
"""
import os, sys, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

# research/Balance-P7-Economy-Spec.md 2.1 (= tools/balance_model.py P7_LEVEL_COINS_TEXT) and 1.3 (= SkyyCoins 0.1.10 coins.curve default)
LC_TEXT = "1:30,10:60,20:150,21:190,30:390,40:1000,41:1200,50:2800,60:5200,61:6400,70:11500,80:21500,81:28500,90:50500,100:95000"
CURVE_TEXT = ("1:0.476,8:0.848,10:1,15:1.51,20:2.28,28:4.41,30:5.2,35:8.49,40:13.8,48:30.3,50:36.8,55:50.5,60:69.2,68:115,70:130,75:179,"
              "80:246,88:410,90:466,95:641,100:881")
import balance_model as BM
assert BM.P7_LEVEL_COINS_TEXT == LC_TEXT and BM.P7_CURVE_TEXT == CURVE_TEXT, "the spec tables moved - update this patch"
_cn = open(os.path.join(ROOT, "SkyyCoins", "build_skyycoins_0.1.10.py"), encoding="utf8").read()
assert ("CURVE_TEXT = '%s'" % CURVE_TEXT) in _cn, "the built-in curve copy must equal SkyyCoins 0.1.10's coins.curve default"
LC_LV = [int(kv.split(":")[0]) for kv in LC_TEXT.split(",")]
LC_C = [float(kv.split(":")[1]) for kv in LC_TEXT.split(",")]
assert LC_LV == sorted(set(LC_LV)) and LC_LV[0] == 1 and LC_LV[-1] == 100


def lc_at(L):   # the Java LvCoins.at() at the default curve (ratio 1) = the model's p7_level_coins + p7_round
    return BM.p7_round(BM.p7_level_coins(L))


assert (lc_at(10), lc_at(50), lc_at(90)) == (60, 2800, 50500), "spec 2.1: Lv 10 60, Lv 50 2,800, Lv 90 50,500"

NOTE = '''0.4.61 (2026-10-22) = BALANCE PASS P7 ECONOMY, the SkyySkills part (research/Balance-P7-Economy-Spec.md 2.1 + 9; FULL round P7b with
  SkyyTrees 0.4.9, SkyyExploration 0.3.3, SkyyShards 0.4.5). Skyy: "work through your whole list." + "keep going down the list. dont stop
  until the entire list is done" + popup "x10 targets (Recommended)" (the coin unit x10; spec Q5 default: level-up coins follow the coin curve).
  PIN TOGETHER with SkyyBazaar 0.2.1 + SkyyCollections 0.2.32 (spec 9: half of the new income without the other half misses the targets -
  tools/balance_model.py --econ GO-TOGETHER row).
  1. LEVEL-UP COINS ON THE COIN CURVE: reaching level L pays levelCoins(L) (new row, text "level:coins", log-linear between the points,
     clamped to 1..100) x coin curve(L) / the default curve(L) (SkyyCoins' coins:fn:curve, 0.1.10+; the built-in copy of its default without
     it -> x1, so the defaults pay exactly the table: Lv 10 60, Lv 20 150, Lv 30 390, Lv 50 2,800, Lv 70 11,500, Lv 90 50,500, Lv 100
     95,000; an admin's changed coins.curve moves the level coins with every other curve price), rounded like the other P7 costs (nearest
     10 / 100 / 500 / 5,000). Then x rebirth.coinFactor per rebirth as before (0.8). levelCoins EMPTY = the old rule coinsPerLevel x level.
     Every skill and the class use it (the same payLocked); the level-up chat line and the Stats page "+N coins when you reach level ..."
     show the same number.
  2. NEW ROW levelCoins (Server Setup -> Skills -> General, "Level-up coins by level", text, check= LvCoins.check: level:coins pairs, levels
     1-100 rising, coins >= 0; empty allowed = coinsPerLevel x level). coinsPerLevel's help says it only pays while levelCoins is empty.
  3. ONE-TIME UPDATE SkMigP7 (PROJECT-RULES 4; BmMigP8c's reviewed machinery, copied): ONCE on an existing xp.properties, setup() right after
     BmMigP8c, BEFORE SkillCfg.load: ONE block in the file's own line ending - the comment + levelCoins=<the table> (if absent) + the
     run-once marker "Balance P7 economy (SkyySkills 0.4.61)". When coinsPerLevel is NOT 100 (an admin's linear rule) the line is
     levelCoins= (empty = their coinsPerLevel x level keeps paying) + one INFO line. config-history copy first (verified), one
     config-changes.log row (Undo), a Properties check (only levelCoins added), atomicWrite. A fresh file carries the block.
  SAVED DATA: none rewritten - levels already paid stay paid (<Skill>.paid); only levels reached from now on pay the new numbers.
  ROLLBACK to 0.4.60: safe (levelCoins is ignored -> 100 x level again); together with SkyyBazaar 0.2.1 / SkyyCollections 0.2.32 only as the
  P7 income set (the model's GO-TOGETHER note). Undo the SkMigP7 row in Server Setup -> Changes first (or leave it: 0.4.60 ignores it).
'''

P = G.Patch(os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.60.py"), os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.61.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.4.60"') and P.has("BmMigP8c") and not P.has("SkMigP7"), "not the generated SkyySkills 0.4.60 script"
REG0, SYS0, CLS0 = P.s.count("registerCommand("), P.s.count("registerSystem("), P.s.count("makeClass(")

P.rep('''"""SkyySkills 0.4.60 - build script (derived from the generated 0.4.59 by tools/skills_0_4_60_patch.py - edit the patch, not this file;
''', '''"""SkyySkills 0.4.61 - build script (derived from the generated 0.4.60 by tools/skills_0_4_61_patch.py - edit the patch, not this file;
''' + NOTE + '''0.4.60 was derived from the generated 0.4.59 by tools/skills_0_4_60_patch.py;
''')
P.rep('VERSION = "0.4.60"', 'VERSION = "0.4.61"')

# ================================================================================================================ the class
P.rep('''bm60 = pool.makeClass(PKG + ".BmMigP8c")        # 0.4.60: the one-time Balance P8c update (catchup.skills + beast.xpFactor)''',
      '''bm60 = pool.makeClass(PKG + ".BmMigP8c")        # 0.4.60: the one-time Balance P8c update (catchup.skills + beast.xpFactor)
lvc61 = pool.makeClass(PKG + ".LvCoins")        # 0.4.61: Balance P7 - level-up coins on the coin curve (levelCoins + coins:fn:curve)
skm61 = pool.makeClass(PKG + ".SkMigP7")        # 0.4.61: the one-time Balance P7 update (levelCoins appended)''')

LVC = r'''# ================= 0.4.61 LvCoins: level-up coins on the coin curve (Balance P7 2.1; tools/skills_0_4_61_patch.py) =================
# L / C = the levelCoins points (null = the old coinsPerLevel x level rule); CV_LV / CV_F = SkyyCoins 0.1.10's coins.curve default (the
# build asserts the text). at(level) = log-linear between the points (linear where a point is 0), clamped to 1..100, x curve / default
# curve (coins:fn:curve; missing -> x1), rounded 10 / 100 / 500 / 5,000. Any thread, never throws.
LC61_TEXT = %r
LC61_LV = %r
LC61_C = %r
LC61_CV = %r
lvc61.addField(CtField.make("public static final String DEF = %%s;" %% json.dumps(LC61_TEXT), lvc61))
lvc61.addField(CtField.make("public static volatile int[] L = new int[] { %%s };" %% ", ".join(str(x) for x in LC61_LV), lvc61))
lvc61.addField(CtField.make("public static volatile double[] C = new double[] { %%s };" %% ", ".join(repr(x) for x in LC61_C), lvc61))
# fix (second critic): T = { L, C } published as ONE volatile reference (null = the old linear rule); at() reads only T, so a reload on
# another thread can never pair new levels with old coins. L / C stay for the ready line + the harness.
lvc61.addField(CtField.make("public static volatile Object[] T = new Object[] { new int[] { %%s }, new double[] { %%s } };" %% (", ".join(str(x) for x in LC61_LV), ", ".join(repr(x) for x in LC61_C)), lvc61))
lvc61.addField(CtField.make("public static final int[] CV_LV = new int[] { %%s };" %% ", ".join(kv.split(":")[0] for kv in LC61_CV.split(",")), lvc61))
lvc61.addField(CtField.make("public static final double[] CV_F = new double[] { %%s };" %% ", ".join(repr(float(kv.split(":")[1])) for kv in LC61_CV.split(",")), lvc61))
lvc61.addMethod(CtNewMethod.make(J14(r"""
public static double curveOwn(int level) {
  int x = level < 1 ? 1 : (level > 100 ? 100 : level);
  int i = 0;
  if (x >= CV_LV[CV_LV.length - 1]) i = CV_LV.length - 2;
  else { while (i < CV_LV.length - 2 && x > CV_LV[i + 1]) i++; }
  double a = Math.log(CV_F[i]);
  double b = Math.log(CV_F[i + 1]);
  return Math.exp(a + (b - a) * (double) (x - CV_LV[i]) / (double) (CV_LV[i + 1] - CV_LV[i]));
}"""), lvc61))
lvc61.addMethod(CtNewMethod.make(J14(r"""
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
}"""), lvc61))
lvc61.addMethod(CtNewMethod.make(J14(r"""
public static long round(double x) {
  if (!(x > 0.0)) return 0L;
  if (x >= 9.0E18) return 9000000000000000000L;
  double st = x < 1000.0 ? 10.0 : (x < 10000.0 ? 100.0 : (x < 100000.0 ? 500.0 : 5000.0));
  return (long) (st * Math.floor(x / st + 0.5));
}"""), lvc61))
# "level:coins,level:coins,..." -> { int[] levels, double[] coins } (levels 1..100 strictly rising, coins 0..1e15, at least one point); null = bad
lvc61.addMethod(CtNewMethod.make(J14(r"""
public static Object[] parse(String s) {
  if (s == null) return null;
  String t = s.trim();
  if (t.length() == 0) return null;
  String[] parts = t.split(",");
  if (parts.length == 0) return null;   // "," alone: no point
  int[] l = new int[parts.length];
  double[] c = new double[parts.length];
  for (int i = 0; i < parts.length; i++) {
    String p = parts[i].trim();
    int k = p.indexOf(':');
    if (k <= 0 || k >= p.length() - 1) return null;
    try {
      l[i] = Integer.parseInt(p.substring(0, k).trim());
      c[i] = Double.parseDouble(p.substring(k + 1).trim());
    } catch (Throwable e) { return null; }
    if (l[i] < 1 || l[i] > 100 || Double.isNaN(c[i]) || c[i] < 0.0 || c[i] > 1.0E15) return null;
    if (i > 0 && l[i] <= l[i - 1]) return null;
  }
  return new Object[] { l, c };
}"""), lvc61))
# the Server Setup check= hook (key, value): null = fine; empty = the old linear rule (allowed)
lvc61.addMethod(CtNewMethod.make(J14(r"""
public static String check(String key, String v) {
  if (v == null || v.trim().length() == 0) return null;
  if (parse(v) != null) return null;
  return "Use level:coins pairs with rising levels 1-100, e.g. 1:30,10:60,50:2800,90:50500 (empty = coinsPerLevel x level)";
}"""), lvc61))
# the coins for REACHING level lv (before rebirth.coinFactor); 0 = the level counts as paid, no coins
lvc61.addMethod(CtNewMethod.make(J14(r"""
public static long at(long lv) {
  if (lv <= 0L) return 0L;
  Object[] t = T;
  int[] l = null;
  double[] c = null;
  if (t != null) { l = (int[]) t[0]; c = (double[]) t[1]; }
  if (l == null || c == null || l.length == 0 || c.length != l.length) {
    long per = @PKG@.SkillCfg.COINS_PER_LEVEL;
    if (per <= 0L) return 0L;
    long x = per * lv;
    if (x / lv != per) return 0L;
    return x;
  }
  int v = lv > 100L ? 100 : (int) lv;
  double y;
  if (v <= l[0]) y = c[0];
  else if (v >= l[l.length - 1]) y = c[c.length - 1];
  else {
    int i = 0;
    while (i < l.length - 2 && v > l[i + 1]) i++;
    double f = (double) (v - l[i]) / (double) (l[i + 1] - l[i]);
    if (c[i] > 0.0 && c[i + 1] > 0.0) y = Math.exp(Math.log(c[i]) + (Math.log(c[i + 1]) - Math.log(c[i])) * f);
    else y = c[i] + (c[i + 1] - c[i]) * f;
  }
  double own = curveOwn(v);
  if (own > 0.0) y = y * curve(v) / own;
  return round(y);
}"""), lvc61))
lvc61.addMethod(CtNewMethod.make(J14(r"""
public static String read(java.util.Properties p) {
  String s = p == null ? null : p.getProperty("levelCoins");
  if (s == null) {
    // fix (critic 1): no levelCoins line (the one-time update not run yet, or its row Undone) while coinsPerLevel holds an admin's
    // value (not 100) = keep their linear rule (same as the update's empty line), never the table
    String cp = p == null ? null : p.getProperty("coinsPerLevel");
    s = (cp != null && !cp.trim().equals("100")) ? "" : DEF;
  }
  if (s.trim().length() == 0) { T = null; L = null; C = null; return "level-up coins: coinsPerLevel x level (levelCoins empty)"; }
  Object[] r = parse(s);
  if (r == null) {
    @PKG@.SkillCfg.warn("levelCoins=" + s.trim() + " is not level:coins pairs with rising levels 1-100 - the default table is used");
    r = parse(DEF);
  }
  L = (int[]) r[0];
  C = (double[]) r[1];
  T = new Object[] { r[0], r[1] };   // one publish (fix, second critic)
  return "level-up coins by level (" + L.length + " points: Lv 10 " + at(10L) + ", Lv 50 " + at(50L) + ", Lv 90 " + at(90L) + ")";
}"""), lvc61))
''' % (LC_TEXT, LC_LV, LC_C, CURVE_TEXT)
P.rep('''cfg.addMethod(CtNewMethod.make(f"""
public static synchronized String load() {{
  int bad = 0;''', LVC + '''cfg.addMethod(CtNewMethod.make(f"""
public static synchronized String load() {{
  int bad = 0;''')
P.rep('''    COINS_PER_LEVEL = lng(p, "coinsPerLevel", 100L);''',
      '''    COINS_PER_LEVEL = lng(p, "coinsPerLevel", 100L);
    {PKG}.LvCoins.read(p);   // 0.4.61 Balance P7: levelCoins (the level-up coins on the coin curve; empty = coinsPerLevel x level)''')

# ================================================================================================================ the payments + the texts
P.rep('''    long coins = per * next;
    if (per <= 0L || coins / next != per) {{''', '''    long coins = {PKG}.LvCoins.at(next);   // 0.4.61 Balance P7: levelCoins x the coin curve (empty = coinsPerLevel x level)
    if (coins <= 0L) {{''')
P.rep('''        long coins = {PKG}.SkillStore.rbCoins(paid[3] * lv, paid.length > 5 ? (int) paid[5] : 0);   // 0.4.36: what was paid''',
      '''        long coins = {PKG}.SkillStore.rbCoins({PKG}.LvCoins.at(lv), paid.length > 5 ? (int) paid[5] : 0);   // 0.4.36: what was paid (0.4.61: LvCoins)''')
_OLDNEXT = '''if ({PKG}.SkillCfg.COINS_PER_LEVEL > 0L) out.add("+" + {PKG}.SkillDefs.fmt({PKG}.SkillStore.rbCoins({PKG}.SkillCfg.COINS_PER_LEVEL * (long) (lv + 1), {PKG}.SkillStore.rbN({PKG}.SkillStore.pkey(u)))) + " coins when you reach level " + (lv + 1));'''
_NEWNEXT = '''if ({PKG}.LvCoins.at((long) (lv + 1)) > 0L) out.add("+" + {PKG}.SkillDefs.fmt({PKG}.SkillStore.rbCoins({PKG}.LvCoins.at((long) (lv + 1)), {PKG}.SkillStore.rbN({PKG}.SkillStore.pkey(u)))) + " coins when you reach level " + (lv + 1));   // 0.4.61'''
P.rep('''  if (s == {PKG}.SkillDefs.FISHING || s == {PKG}.SkillDefs.RANCHING || s == {PKG}.SkillDefs.ORCHARD) {{   // 0.4.37: no perks yet
    if (next) {{
      ''' + _OLDNEXT, '''  if (s == {PKG}.SkillDefs.FISHING || s == {PKG}.SkillDefs.RANCHING || s == {PKG}.SkillDefs.ORCHARD) {{   // 0.4.37: no perks yet
    if (next) {{
      ''' + _NEWNEXT)
P.rep('''      out.add("+1 Beastmastery tree point at level " + (lv + 1));
      ''' + _OLDNEXT, '''      out.add("+1 Beastmastery tree point at level " + (lv + 1));
      ''' + _NEWNEXT)
P.rep('''  if (next && {PKG}.SkillCfg.COINS_PER_LEVEL > 0L) out.add("+" + {PKG}.SkillDefs.fmt({PKG}.SkillStore.rbCoins({PKG}.SkillCfg.COINS_PER_LEVEL * (long) b, {PKG}.SkillStore.rbN({PKG}.SkillStore.pkey(u)))) + " coins when you reach level " + b);   // 0.4.36: x rebirth.coinFactor ^ rebirths''',
      '''  if (next && {PKG}.LvCoins.at((long) b) > 0L) out.add("+" + {PKG}.SkillDefs.fmt({PKG}.SkillStore.rbCoins({PKG}.LvCoins.at((long) b), {PKG}.SkillStore.rbN({PKG}.SkillStore.pkey(u)))) + " coins when you reach level " + b);   // 0.4.36: x rebirth.coinFactor ^ rebirths (0.4.61: LvCoins)''')
assert _OLDNEXT not in P.s and "SkillCfg.COINS_PER_LEVEL * " not in P.s, "0.4.61: every level-coin text goes through LvCoins.at"

# ================================================================================================================ the Server Setup rows
P.rep('''    ("coinsPerLevel", "Coins per level up", "general", "int", "100", "0", "1000000000", "step=50", "coins", "live,danger",
     "A level up pays this x the new level in coins (needs SkyyCoins).", "reload"),''',
      '''    ("coinsPerLevel", "Coins per level up", "general", "int", "100", "0", "1000000000", "step=50", "coins", "live,danger",
     "Only while Level-up coins by level is empty: a level up pays this x the new level in coins.", "reload"),
    # 0.4.61 (Balance P7 2.1: "Level-up coins by level (levelCoins) text level:coins")
    ("levelCoins", "Level-up coins by level", "general", "text", LC61_TEXT, "", "500", "", "", "live",
     "level:coins x the coin curve (Lv 10 60, Lv 50 2,800, Lv 90 50,500). Empty = coinsPerLevel x level.", "reload;check=LvCoins.check"),''')
P.rep('''assert len(CFG_ROWS) == 285 + len(P4_ROWS_POWER) + len(P4_ROWS_MANA) + len(P4_ROWS_MOVE) + 2, ("0.4.60: + beast.xpFactor; 0.4.59: + rebirth.xpMultMax; 0.4.58:''',
      '''assert len(CFG_ROWS) == 285 + len(P4_ROWS_POWER) + len(P4_ROWS_MANA) + len(P4_ROWS_MOVE) + 3, ("0.4.61: + levelCoins; 0.4.60: + beast.xpFactor; 0.4.59: + rebirth.xpMultMax; 0.4.58:''')

# ================================================================================================================ the fresh default file + SkMigP7
SKDATA = r'''# ================= 0.4.61 BALANCE P7 - the SkMigP7 plan and the fresh default file (tools/skills_0_4_61_patch.py) =================
SK_ADD = [("levelCoins", LC61_TEXT, "levelCoins")]
SK_MARK_ID = "Balance P7 economy (SkyySkills 0.4.61)"
SK_MARK = "# %s: level-up coins follow the coin curve (levelCoins)" % SK_MARK_ID
SK_HEAD = ["", "# ---------- Balance P7: level-up coins on the coin curve (SkyySkills 0.4.61) ----------",
           "# Comments must stay on their own lines. levelCoins = level:coins points (log-linear between them, x the SkyyCoins coin curve),",
           "# paid once per level reached, x rebirth.coinFactor per rebirth. Empty = the old coinsPerLevel x level."]
for _t in SK_HEAD + [SK_MARK]:
    assert all(32 <= ord(_c) < 127 for _c in _t) and '"' not in _t and "\\" not in _t and (not _t or _t.startswith("# ")), _t
assert "=" not in SK_MARK and not any(_cre.match(r"#\s*[A-Za-z][A-Za-z0-9._-]*\s*[=:]\s*\S+\s*$", _ln) for _ln in SK_HEAD)
SK_BLOCK = "\n".join(SK_HEAD + ["%s=%s" % (_k, _v) for _k, _v, _r in SK_ADD] + [SK_MARK]) + "\n"
DEFAULTS_060 = DEFAULTS   # 0.4.61: the 0.4.60 default file
assert "\nlevelCoins=" not in DEFAULTS_060 and ("\ncoinsPerLevel=100\n") in ("\n" + DEFAULTS_060)
DEFAULTS = DEFAULTS_060 + ("" if DEFAULTS_060.endswith("\n") else "\n") + SK_BLOCK
assert all(ord(ch) < 128 for ch in DEFAULTS) and len(DEFAULTS.encode("utf-8")) < 65000 and DEFAULTS.count(SK_MARK_ID) == 1, len(DEFAULTS)
print("0.4.61: P7 update plan: %d line(s) appended; default file %d bytes; level coins Lv 10 / 50 / 90 = %s" % (len(SK_ADD), len(DEFAULTS), LC61_TEXT.split(",")[1]))
'''
P.rep('''DEFAULTS_LIT = json.dumps(DEFAULTS)   # valid Java string literal for ASCII text (\\n \\" \\\\ escapes)''',
      SKDATA + '''DEFAULTS_LIT = json.dumps(DEFAULTS)   # valid Java string literal for ASCII text (\\n \\" \\\\ escapes)''')
P.rep('''assert DEFAULTS.endswith(BM_BLOCK) and DEFAULTS.count(BM_MARK_ID) == 1 and _dp.get("catchup.skills") == P3_CATCH and _dp.get("beast.xpFactor") == "1"   # 0.4.60''',
      '''assert DEFAULTS_060.endswith(BM_BLOCK) and DEFAULTS.count(BM_MARK_ID) == 1 and _dp.get("catchup.skills") == P3_CATCH and _dp.get("beast.xpFactor") == "1"   # 0.4.60 (0.4.61: the 0.4.60 file)
assert DEFAULTS.endswith(SK_BLOCK) and DEFAULTS.count(SK_MARK_ID) == 1 and _dp.get("levelCoins") == LC61_TEXT and _dp.get("coinsPerLevel") == "100"   # 0.4.61''')
# the LVC block needs LC61_TEXT before SKDATA uses it: LVC sits before SkillCfg.load (far below DEFAULTS) - so define the text early too
P.rep('''DEFAULTS_059 = DEFAULTS   # 0.4.60: the 0.4.59 default file''',
      '''LC61_TEXT = %r   # 0.4.61 Balance P7: the levelCoins default (research/Balance-P7-Economy-Spec.md 2.1; set again with the LvCoins class)
DEFAULTS_059 = DEFAULTS   # 0.4.60: the 0.4.59 default file''' % LC_TEXT)


def _bmm(name):
    a = P.s.index('bm60.addMethod(CtNewMethod.make(J14(r"""\npublic static ' + name)
    b = P.s.index('"""), bm60))', a)
    return P.s[a + len('bm60.addMethod(CtNewMethod.make(J14(r"""'):b]


_IDX, _OLDH, _PLAN, _SAME, _RUN = (_bmm("int idx("), _bmm("boolean oldHit("), _bmm("Object[] plan("), _bmm("boolean sameAfter("),
                                   _bmm("synchronized String run()"))


def _sub(src, pairs, what):
    for a, b in pairs:
        assert src.count(a) == 1, (what, a)
        src = src.replace(a, b)
    return src


_PLAN = _sub(_PLAN, [('''"the 0.4.60 default has no such line" : "the 0.4.60 (Balance P8c) default is "''',
                      '''"the 0.4.61 default has no such line" : "the 0.4.61 (Balance P7) default is "'''),
                     ('''    add[i] = true;
    blk.append(ADDK[i]).append('=').append(ADDV[i]).append(nl);
    if (ADDR[i] != null) { rows.add(ADDR[i]); rows.add("(none)"); rows.add(ADDV[i]); }''',
                      '''    add[i] = true;
    String av = addv(i, p);
    blk.append(ADDK[i]).append('=').append(av).append(nl);
    if (ADDR[i] != null) { rows.add(ADDR[i]); rows.add("(none)"); rows.add(av); }
    if (!av.equals(ADDV[i])) kept.append(kept.length() > 0 ? "; " : "").append("coinsPerLevel=" + @PKG@.CfgRows.oneLine(p.getProperty("coinsPerLevel")) + " kept (an admin's value) - levelCoins= is written EMPTY so coinsPerLevel x level keeps paying (the 0.4.61 default is the coin-curve table)");''')],
               "plan")
_SAME = _sub(_SAME, [('''if (a.getProperty(ADDK[i]) != null || !ADDV[i].equals(n.getProperty(ADDK[i]))) return false;''',
                      '''if (a.getProperty(ADDK[i]) != null || !addv(i, a).equals(n.getProperty(ADDK[i]))) return false;''')], "sameAfter")
_RUN = _sub(_RUN, [("xp.properties NOT updated for 0.4.60 (Balance P8c): the update would change", "xp.properties NOT updated for 0.4.61 (Balance P7): the update would change"),
                   ("xp.properties NOT updated for 0.4.60 (Balance P8c): the old file could not", "xp.properties NOT updated for 0.4.61 (Balance P7): the old file could not"),
                   ('"before the 0.4.60 Balance P8c update"', '"before the 0.4.61 Balance P7 update"'),
                   ('"xp.properties updated for 0.4.60 (Balance P8c: Beastmastery in catch-up, Beastmastery XP per pet XP row): "',
                    '"xp.properties updated for 0.4.61 (Balance P7: level-up coins on the coin curve, the levelCoins row): "'),
                   ('"could not update xp.properties for 0.4.60 (Balance P8c; the file is used as it is): "',
                    '"could not update xp.properties for 0.4.61 (Balance P7; the file is used as it is): "')], "run")
for _src in (_PLAN, _RUN, _SAME):
    assert "0.4.60" not in _src and "P8c" not in _src, _src[:200]
SKMIG = r'''# ---- SkMigP7 (0.4.61, PROJECT-RULES section 4; BmMigP8c's reviewed machinery, copied): ONCE on an EXISTING xp.properties, setup() right after
# BmMigP8c, BEFORE SkillCfg.load. No line changes value; ONE block in the file's own line ending: HEAD + levelCoins=<the table> (if absent; EMPTY
# when coinsPerLevel is an admin's value, not 100 - their linear rule keeps paying, one INFO line) + the marker. config-history copy first
# (verified), one config-changes.log row (Undo), Properties check, atomicWrite. A failure = WARN, file untouched, retried next start.
skm61.addField(CtField.make("public static final String MARK_ID = %s;" % json.dumps(SK_MARK_ID), skm61))
skm61.addField(CtField.make("public static final String MARK = %s;" % json.dumps(SK_MARK), skm61))
skm61.addField(CtField.make("public static final String HEAD = %s;" % json.dumps("\n".join(SK_HEAD) + "\n"), skm61))
skm61.addField(CtField.make("public static final String[] KEYS = %s;" % jarr([]), skm61))
skm61.addField(CtField.make("public static final String[] OLDS = %s;" % jarr([]), skm61))
skm61.addField(CtField.make("public static final String[] NEWS = %s;" % jarr([]), skm61))
skm61.addField(CtField.make("public static final String[] ROWK = %s;" % jarr([]), skm61))
skm61.addField(CtField.make("public static final String[] ADDK = %s;" % jarr([_e[0] for _e in SK_ADD]), skm61))
skm61.addField(CtField.make("public static final String[] ADDV = %s;" % jarr([_e[1] for _e in SK_ADD]), skm61))
skm61.addField(CtField.make("public static final String[] ADDR = %s;" % jarr([_e[2] for _e in SK_ADD]), skm61))
skm61.addField(CtField.make('public static final String WHO = "SkyySkills 0.4.61";', skm61))
# the value appended for ADDK[i]: levelCoins = "" (the old linear rule) while coinsPerLevel holds an admin's number (not 100)
skm61.addMethod(CtNewMethod.make(J14(r"""
public static String addv(int i, java.util.Properties p) {
  if (i < 0 || i >= ADDV.length) return "";
  if ("levelCoins".equals(ADDK[i]) && p != null) {
    String c = p.getProperty("coinsPerLevel");
    if (c != null && !c.trim().equals("100")) return "";
  }
  return ADDV[i];
}"""), skm61))
skm61.addMethod(CtNewMethod.make(J14(r"""''' + _IDX + r'''"""), skm61))
skm61.addMethod(CtNewMethod.make(J14(r"""''' + _OLDH + r'''"""), skm61))
skm61.addMethod(CtNewMethod.make(J14(r"""''' + _PLAN + r'''"""), skm61))
skm61.addMethod(CtNewMethod.make(J14(r"""''' + _SAME + r'''"""), skm61))
skm61.addMethod(CtNewMethod.make(J14(r"""''' + _RUN + r'''"""), skm61))

'''
P.rep('''# ---- BmMigP8c (0.4.60, PROJECT-RULES section 4; PlMigP8's reviewed machinery, copied): ONCE on an EXISTING xp.properties, setup() right after''',
      SKMIG + '''# ---- BmMigP8c (0.4.60, PROJECT-RULES section 4; PlMigP8's reviewed machinery, copied): ONCE on an EXISTING xp.properties, setup() right after''')
P.rep('''  {PKG}.BmMigP8c.run();       // 0.4.60 Balance P8c: an untouched catchup.skills -> + Beastmastery + the Beastmastery XP row, once; History first''',
      '''  {PKG}.BmMigP8c.run();       // 0.4.60 Balance P8c: an untouched catchup.skills -> + Beastmastery + the Beastmastery XP row, once; History first
  {PKG}.SkMigP7.run();        // 0.4.61 Balance P7: + the levelCoins row (empty while coinsPerLevel is an admin's), once; History first''')
P.rep("cst, p4m, plm8, bm60, lvf,", "cst, p4m, plm8, bm60, lvc61, skm61, lvf,")

# ================================================================================================================ the ready line
P.rep('''+ "; Beastmastery from pet XP (skill:fn:addxp source pets, x" + {PKG}.DivCfg.num({PKG}.P3Xp.BEAST_F) + " per pet XP)"''',
      '''+ "; Beastmastery from pet XP (skill:fn:addxp source pets, x" + {PKG}.DivCfg.num({PKG}.P3Xp.BEAST_F) + " per pet XP)" + "; level-up coins Lv 10 / 50 / 90 = " + {PKG}.LvCoins.at(10L) + " / " + {PKG}.LvCoins.at(50L) + " / " + {PKG}.LvCoins.at(90L) + ({PKG}.LvCoins.L == null ? " (coinsPerLevel x level)" : " (levelCoins x the coin curve)")''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0 and P.s.count("makeClass(") == CLS0 + 2
_i = P.s.index
assert _i("public static long at(long lv)") < _i("public static synchronized String load() {{") < _i("public static long[] payLocked(")
_sk0 = _i("# ---- SkMigP7 (0.4.61")
assert _sk0 < _i("public static String addv(int i") < P.s.index('public static Object[] plan(String text) {', _sk0)   # methods before callers
P.finish()
