"""Derive SkyySkills/build_skyyskills_0.4.68.py from the GENERATED SkyySkills 0.4.67 (build_skyyskills_0.4.67.py = the tools/deploy_set.py SET
pin, made by tools/skills_0_4_67_patch.py). Every anchor is asserted once; at the end every change is undone on a copy and compared with
0.4.67 (tools/soundpass_gen.Patch). Line endings kept. Edit THIS file, never the generated script.
Run:  python tools/skills_0_4_68_patch.py   then   python SkyySkills/build_skyyskills_0.4.68.py   (never --deploy)
      then  python SkyySkills/test_skyyskills_0.4.68.py
Round farmxp = Farming XP balance (docs/answered/skills.md 2026-10-27 FARMING XP TOO FAST; Skyy picked "Low-tier falloff").
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G
import tier_tags as TT

NOTE = '''0.4.68 (2026-10-27) = LOW-TIER CROP FALLOFF (docs/answered/skills.md 2026-10-27 FARMING XP TOO FAST; Skyy: "farming levels really fast
  too"; popup "Farming XP is ~2x too fast, mostly from mass-harvesting low-tier crops (wheat/lettuce) at Lv 40. How should we fix it?" ->
  "Low-tier falloff (Recommended)" = "crops far below your level's tier give less XP (e.g. x0.5 at 4+ tiers below, x0.25 at 8+). Farming
  the right-tier crops stays full speed. Editable in Server Setup.").
  WHY: per-crop Farming XP is the crop's tier (Balance P3: Wheat 40, Lettuce 80, Carrot 135 ... Mushroom 1850) and every crop a Harvester
    sweep reaps pays a full award, so mass Wheat / Lettuce fields at Farming Lv 38-43 paid ~465-530k XP/h against the 234k Zone 3 target
    (research/balance/targets.md section 2). The existing farming.tierUpXpFactor only lowers crops ABOVE the tool's tier.
  THE RULE (FarmTier.low, every Farming crop award: Harvester / sickle sweeps per crop, breaking a ripe crop, F-harvest): your Farming level
    -> your FARMING TIER = the last entry of farming.lowTier.levels at or below it (default = the P3 crop tier bands, the level each crop tier
    starts at: 1,8,15,20,28,35,40,48,55,60,68,75,80,88,95 -> Lv 1-7 T1, 8-14 T2, 15-19 T3, 20-27 T4, 28-34 T5, 35-39 T6, 40-47 T7, 48-54 T8 ...).
    A crop (tools/tier_tags.py CROP_LADDER: Wheat T1, Lettuce T2, Carrot T3, Corn T4 ... Mushroom T15) farming.lowTier.gap1 (4) or more tiers
    below pays x farming.lowTier.mult1 (0.5), gap2 (8) or more x mult2 (0.25) - before the pace / Wisdom / pet share, so the pet copy and
    Beastmastery fall with it. A fraction is paid as a random whole XP with the exact average (FarmTier.scale). Crops outside the ladder
    (herbs, Orchard apples / berries, other mods' crops) and Orchard-routed XP are never lowered. farming.lowTier.enabled false = 0.4.67.
  THE MATH (base XP per crop; Skyy's measured 465-530k XP/h at Lv 38-43 of Wheat + Lettuce): Lv 38 = T6 (Wheat 5 below, Lettuce 4 below)
    and Lv 40-47 = T7 (6 / 5 below) -> both x0.5 -> ~233-265k XP/h vs the 234k target (x1.00-1.13). Right-tier crops (0-3 tiers below)
    stay x1.0 everywhere. Zone 1 (Farming Lv 1-15, model 20k vs 34k): no crop is 4 tiers below before Lv 28 -> unchanged. Zone 2 (Lv 15-35,
    model 92k vs 127k, its crops T3-T6): unchanged; only Wheat at Lv 28-34 halves (mass Wheat there ~330k XP/h -> ~165k, still above the
    127k target). x0.25: Wheat from Lv 55, Lettuce 60, Carrot 68, Corn 75 (Zone 4+). Only Farming: Mining Zone 3 is x1.11 and Foraging is
    slow (0.4.67), neither needs it.
  BEASTMASTERY (checked, no change): pet XP = the final Farming award x pets.xp.ownPercent 50 % / the P3 divisor (SkyyPets PetXp.give2),
    Beastmastery = that x beast.xpFactor 1.5 -> the falloff lowers both. Skyy's maxed Beastmastery (837k XP on profile 3, the Lv 50 total is
    487k) came from the Foraging flood (Foraging 1.54M XP before 0.4.67) + this Farming flood; at target pace the P9 model has Beastmastery
    slightly SLOW (Lv 43-45 at run end, targets.md section 10) - beast.xpFactor stays 1.5.
  SERVER SETUP (Skills -> Gathering, after "Farming XP one tier above your tool"): farming.lowTier.enabled / levels / gap1 / mult1 / gap2 /
    mult2. New keys only (a missing line = the code default) - no one-time update; a fresh xp.properties carries them.
  SKILLS PAGE: Farming's Stats page names your Farming tier and which crops pay less.
  SAVED DATA: none. ROLLBACK to 0.4.67: just the jar (0.4.67 ignores the farming.lowTier.* lines).
'''

P = G.Patch(os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.67.py"), os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.68.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.4.67"') and P.has("tools/skills_0_4_67_patch.py") and not P.has("0.4.68 (2026-10-27)"), "not the generated SkyySkills 0.4.67 script"
REG0, SYS0, CLS0 = P.s.count("registerCommand("), P.s.count("registerSystem("), P.s.count("makeClass(")

# the defaults (Python side; asserted against the code defaults below)
LT_LEVELS = [1, 8, 15, 20, 28, 35, 40, 48, 55, 60, 68, 75, 80, 88, 95]   # = the P3 band starts of crop tiers T1-T15
assert P.has("(1, 8, 15, 20, 28, 35, 40, 48, 55, 60, 68, 75, 80, 88, 95, 100)")   # the P3 F(T) band table the crop XP rests on
assert len(TT.CROP_LADDER) == 15 and TT.CROP_LADDER[:4] == ("Wheat", "Lettuce", "Carrot", "Corn") and TT.CROP_LADDER[-1] == "Mushroom"

P.rep('''"""SkyySkills 0.4.67 - GENERATED by tools/skills_0_4_67_patch.py from build_skyyskills_0.4.66.py (the SET pin) - edit the patch, not this file.
''', '''"""SkyySkills 0.4.68 - GENERATED by tools/skills_0_4_68_patch.py from build_skyyskills_0.4.67.py (the SET pin) - edit the patch, not this file.
''' + NOTE + '''
SkyySkills 0.4.67 - GENERATED by tools/skills_0_4_67_patch.py from build_skyyskills_0.4.66.py (the SET pin at that time).
''')
P.rep('VERSION = "0.4.67"', 'VERSION = "0.4.68"')

# ---- the fresh default file: one block of new keys (no one-time update: new keys, a missing line = the code default)
P.rep('''DEFAULTS_LIT = json.dumps(DEFAULTS)   # valid Java string literal for ASCII text (\\n \\" \\\\ escapes)
''', '''# ================= 0.4.68 LOW-TIER CROP FALLOFF - the new keys and the fresh default file (tools/skills_0_4_68_patch.py) =================
LT_LEVELS = %r   # farming.lowTier.levels: the level each Farming tier starts at (= the P3 crop tier bands)
assert LT_LEVELS == [_b for _b in (1, 8, 15, 20, 28, 35, 40, 48, 55, 60, 68, 75, 80, 88, 95, 100)][:15]
LT_KEYS = [("farming.lowTier.enabled", "true"), ("farming.lowTier.levels", ",".join(str(_x) for _x in LT_LEVELS)),
           ("farming.lowTier.gap1", "4"), ("farming.lowTier.mult1", "0.5"), ("farming.lowTier.gap2", "8"), ("farming.lowTier.mult2", "0.25")]
LT_DEF = dict(LT_KEYS)
LT_CROPS = list(_TT57.CROP_LADDER)   # index = crop tier - 1 (tools/tier_tags.py)
assert len(LT_CROPS) == 15 and LT_CROPS[0] == "Wheat" and all(P3_CROP_T[_c] == _i + 1 for _i, _c in enumerate(LT_CROPS))
for _c in LT_CROPS:
    must_prefix("Plant_Crop_" + _c)
LT_NAMES_J = "new String[] { " + ", ".join('"Plant_Crop_%%s"' %% _c for _c in LT_CROPS) + " }"
LT_LV_J = "new int[] { %%s }" %% ", ".join(str(_x) for _x in LT_LEVELS)
LT_LV_TXT = json.dumps(LT_DEF["farming.lowTier.levels"])
LT_HEAD = ["", "# ---------- Low-tier crop falloff - SkyySkills 0.4.68 ----------",
           "# Your Farming level gives you a Farming tier: the last entry of farming.lowTier.levels at or below your level (Lv 40 is T7).",
           "# A crop gap1 or more tiers below your Farming tier pays its Farming XP times mult1, gap2 or more times mult2 (Wheat T1,",
           "# Lettuce T2, Carrot T3 ... Mushroom T15). Right-tier crops pay full. Herbs, Orchard and other mods' crops are never lowered.",
           "# enabled false: every crop pays full (the 0.4.67 numbers). A gap of 0 turns that band off."]
for _t in LT_HEAD:
    assert all(32 <= ord(_c) < 127 for _c in _t) and '"' not in _t and "\\\\" not in _t and "=" not in _t and (not _t or _t.startswith("# ")), _t
LT_BLOCK = "\\n".join(LT_HEAD + ["%%s=%%s" %% _kv for _kv in LT_KEYS]) + "\\n"
DEFAULTS_067 = DEFAULTS   # 0.4.68: the 0.4.67 default file
assert all(("\\n%%s=" %% _k) not in ("\\n" + DEFAULTS_067) for _k, _v in LT_KEYS)
DEFAULTS = DEFAULTS_067 + ("" if DEFAULTS_067.endswith("\\n") else "\\n") + LT_BLOCK
assert all(ord(ch) < 128 for ch in DEFAULTS) and len(DEFAULTS.encode("utf-8")) < 65000, len(DEFAULTS)
print("0.4.68: low-tier crop falloff %%s; default file %%d bytes" %% (LT_DEF, len(DEFAULTS)))
DEFAULTS_LIT = json.dumps(DEFAULTS)   # valid Java string literal for ASCII text (\\n \\" \\\\ escapes)
''' % LT_LEVELS)

# ---- Sickle: the farming.lowTier.* fields (read with the other farming.* keys)
P.rep('''           "public static volatile double TIER_XP = 0.5;"):   # 0.4.35 fix round: farming.tierUpXpFactor (FarmTier.apply)
''', '''           "public static volatile double TIER_XP = 0.5;",   # 0.4.35 fix round: farming.tierUpXpFactor (FarmTier.apply)
           # 0.4.68: farming.lowTier.* (FarmTier.low) - the on switch, the Farming tier levels, the two bands; NAMES / TIERS = the crop ladder
           "public static volatile boolean LOW_ON = true;", "public static volatile int[] LOW_LV = %s;" % LT_LV_J,
           "public static volatile String LOW_LV_TEXT = %s;" % LT_LV_TXT, "public static final String LOW_LV_DEF = %s;" % LT_LV_TXT,
           "public static volatile int LOW_G1 = 4;", "public static volatile double LOW_M1 = 0.5;",
           "public static volatile int LOW_G2 = 8;", "public static volatile double LOW_M2 = 0.25;",
           "public static final String[] LOW_NAMES = %s;" % LT_NAMES_J, "public static volatile String LOW_WARNED = \\"\\";"):
''')
P.rep('''skl.addMethod(CtNewMethod.make(J14(r"""
public static void read(java.util.Properties p) {
  ON = @PKG@.SkillCfg.bool(p, "farming.sickle.enabled", true);
''', '''# 0.4.68: farming.lowTier.levels -> the level each Farming tier starts at (whole numbers 1-1000, rising; null = not a valid list)
skl.addMethod(CtNewMethod.make(J14(r"""
public static int[] lowLevels(String v) {
  if (v == null) return null;
  String[] ps = v.split(",");
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < ps.length; i++) {
    String t = ps[i].trim();
    if (t.length() == 0) continue;
    int x = -1;
    try { x = Integer.parseInt(t); } catch (Throwable e) { return null; }
    if (x < 1 || x > 1000) return null;
    if (l.size() > 0 && x <= ((Integer) l.get(l.size() - 1)).intValue()) return null;
    l.add(Integer.valueOf(x));
  }
  if (l.isEmpty() || l.size() > 64) return null;
  int[] a = new int[l.size()];
  for (int i = 0; i < a.length; i++) a[i] = ((Integer) l.get(i)).intValue();
  return a;
}"""), skl))
skl.addMethod(CtNewMethod.make(J14(r"""
public static String checkLowLevels(String key, String v) {
  if (v == null) return null;
  if (lowLevels(v) == null) return "Write rising whole levels (1-1000) separated by commas, like 1,8,15,20,28 - entry N is where Farming tier N starts.";
  return null;
}"""), skl))
skl.addMethod(CtNewMethod.make(J14(r"""
public static double lowMultOf(java.util.Properties p, String k, double d) {
  double m = @PKG@.SkillCfg.dbl(p, k, d);
  if (Double.isNaN(m) || Double.isInfinite(m)) return d;
  return m < 0.0 ? 0.0 : (m > 1.0 ? 1.0 : m);
}"""), skl))
skl.addMethod(CtNewMethod.make(J14(r"""
public static int lowGapOf(java.util.Properties p, String k, long d) {
  long g = @PKG@.SkillCfg.lng(p, k, d);
  return (int) (g < 0L ? 0L : (g > 64L ? 64L : g));
}"""), skl))
skl.addMethod(CtNewMethod.make(J14(r"""
public static void readLow(java.util.Properties p) {
  LOW_ON = @PKG@.SkillCfg.bool(p, "farming.lowTier.enabled", true);
  String lt = p.getProperty("farming.lowTier.levels", LOW_LV_DEF);
  int[] lv = lowLevels(lt);
  if (lv == null) {
    String w = "farming.lowTier.levels=" + lt + " is not a rising list of levels - using " + LOW_LV_DEF;
    if (!w.equals(LOW_WARNED)) { LOW_WARNED = w; @PKG@.SkillCfg.warn(w); }
    lt = LOW_LV_DEF;
    lv = lowLevels(lt);
  }
  LOW_LV = lv;
  LOW_LV_TEXT = lt.trim();
  LOW_G1 = lowGapOf(p, "farming.lowTier.gap1", 4L);
  LOW_M1 = lowMultOf(p, "farming.lowTier.mult1", 0.5);
  LOW_G2 = lowGapOf(p, "farming.lowTier.gap2", 8L);
  LOW_M2 = lowMultOf(p, "farming.lowTier.mult2", 0.25);
}"""), skl))
skl.addMethod(CtNewMethod.make(J14(r"""
public static void read(java.util.Properties p) {
  ON = @PKG@.SkillCfg.bool(p, "farming.sickle.enabled", true);
  readLow(p);   // 0.4.68: farming.lowTier.*
''')
assert LT_LEVELS == [1, 8, 15, 20, 28, 35, 40, 48, 55, 60, 68, 75, 80, 88, 95]   # the code defaults above: gap1 4 / mult1 0.5 / gap2 8 / mult2 0.25 / on

# ---- FarmTier.low (after scale + apply, which it sits next to)
P.rep('''# BreakTask: the broken block's type id + the item the breaker held (the event keeps both)
''', '''# ================= 0.4.68 LOW-TIER CROP FALLOFF (FarmTier.low): your Farming tier = the last Sickle.LOW_LV entry at or below your Farming
# level (at least T1); a crop's tier = its place in the crop ladder (block / item id Plant_Crop_<Name> then "_" or the end, a leading "*" of a
# state id ignored; not in the ladder = 0 = never lowered). gap = your tier - the crop's: the band with the biggest gap reached pays its mult
# (gap 0 = band off). Applied before SkillXp.gain (pace, Wisdom, the pet share and Beastmastery all follow). Orchard-routed ids never.
ftr.addField(CtField.make("public static final java.util.concurrent.atomic.AtomicLong LOWERED = new java.util.concurrent.atomic.AtomicLong();", ftr))
ftr.addMethod(CtNewMethod.make(J14(r"""
public static int lowTier(int lv) {
  int[] a = @PKG@.Sickle.LOW_LV;
  int t = 0;
  for (int i = 0; a != null && i < a.length; i++) {
    if (lv >= a[i]) t = i + 1;
    else break;
  }
  return t < 1 ? 1 : t;
}"""), ftr))
ftr.addMethod(CtNewMethod.make(J14(r"""
public static int cropTier(String id) {
  if (id == null) return 0;
  if (id.startsWith("*")) id = id.substring(1);
  if (!id.startsWith("Plant_Crop_")) return 0;
  String[] n = @PKG@.Sickle.LOW_NAMES;
  for (int i = 0; i < n.length; i++) {
    String c = n[i];
    if (id.startsWith(c) && (id.length() == c.length() || id.charAt(c.length()) == '_')) return i + 1;
  }
  return 0;
}"""), ftr))
ftr.addMethod(CtNewMethod.make(J14(r"""
public static double bandMult(int g) {
  int best = 0;
  double m = 1.0;
  int g1 = @PKG@.Sickle.LOW_G1;
  int g2 = @PKG@.Sickle.LOW_G2;
  if (g1 > 0 && g >= g1 && g1 > best) { best = g1; m = @PKG@.Sickle.LOW_M1; }
  if (g2 > 0 && g >= g2 && g2 > best) { best = g2; m = @PKG@.Sickle.LOW_M2; }
  return m;
}"""), ftr))
ftr.addMethod(CtNewMethod.make(J14(r"""
public static double lowMult(int lv, String id) {
  if (!@PKG@.Sickle.LOW_ON) return 1.0;
  int c = cropTier(id);
  if (c <= 0) return 1.0;
  return bandMult(lowTier(lv) - c);
}"""), ftr))
ftr.addMethod(CtNewMethod.make(J14(r"""
public static long lowAt(int lv, String id, long amt, double r) {
  if (amt <= 0L) return amt;
  double m = lowMult(lv, id);
  if (m >= 1.0) return amt;
  LOWERED.incrementAndGet();
  return scale(amt, m, r);
}"""), ftr))
ftr.addMethod(CtNewMethod.make(J14(r"""
public static long low(java.util.UUID u, String id, long amt) {
  if (amt <= 0L || u == null || !@PKG@.Sickle.LOW_ON) return amt;
  if (cropTier(id) <= 0) return amt;
  if (@PKG@.Farm3.route(@PKG@.SkillDefs.FARMING, id) != @PKG@.SkillDefs.FARMING) return amt;
  int lv = 0;
  try { lv = @PKG@.SkillStore.level(u, @PKG@.SkillDefs.FARMING); } catch (Throwable t) { return amt; }
  return lowAt(lv, id, amt, java.util.concurrent.ThreadLocalRandom.current().nextDouble());
}"""), ftr))
ftr.addMethod(CtNewMethod.make(J14(r"""
public static String cropName(int t) {
  String[] n = @PKG@.Sickle.LOW_NAMES;
  if (t < 1 || t > n.length) return "T" + t;
  return n[t - 1].substring("Plant_Crop_".length()) + " (T" + t + ")";
}"""), ftr))
# Farming's Stats page line (null = off): your Farming tier + each run of crops with the same lowered XP ("Wheat (T1) to Lettuce (T2) x0.5")
ftr.addMethod(CtNewMethod.make(J14(r"""
public static String statsLine(int lv) {
  if (!@PKG@.Sickle.LOW_ON) return null;
  int t = lowTier(lv);
  int n = @PKG@.Sickle.LOW_NAMES.length;
  StringBuilder b = null;
  int i = 1;
  while (i <= n) {
    double m = bandMult(t - i);
    if (m >= 1.0) { i++; continue; }
    int j = i;
    while (j + 1 <= n && bandMult(t - (j + 1)) == m) j++;
    if (b == null) b = new StringBuilder("Your Farming tier: T" + t + " - less XP for ");
    else b.append(", ");
    b.append(cropName(i));
    if (j > i) b.append(" to ").append(cropName(j));
    b.append(" x").append(@PKG@.DivCfg.num(m));
    i = j + 1;
  }
  if (b != null) return b.toString();
  int g = @PKG@.Sickle.LOW_G1 > 0 ? @PKG@.Sickle.LOW_G1 : @PKG@.Sickle.LOW_G2;
  if (g <= 0) return null;
  return "Your Farming tier: T" + t + " - every crop pays full XP (crops " + g + "+ tiers below your tier pay less)";
}"""), ftr))
ftr.addMethod(CtNewMethod.make(J14(r"""
public static String lowText() {
  if (!@PKG@.Sickle.LOW_ON) return "off";
  return "on (Farming tiers from levels " + @PKG@.Sickle.LOW_LV_TEXT + "; " + (@PKG@.Sickle.LOW_G1 > 0 ? @PKG@.Sickle.LOW_G1 + "+ tiers below x" + @PKG@.DivCfg.num(@PKG@.Sickle.LOW_M1) : "band 1 off")
       + ", " + (@PKG@.Sickle.LOW_G2 > 0 ? @PKG@.Sickle.LOW_G2 + "+ x" + @PKG@.DivCfg.num(@PKG@.Sickle.LOW_M2) : "band 2 off") + ")";
}"""), ftr))
# BreakTask: the broken block's type id + the item the breaker held (the event keeps both)
''')

# ---- the three Farming crop awards
P.rep('''    amt = @PKG@.FarmTier.apply(u, (String) info[2], (String) HELD.get(u), amt);   // 0.4.35: half XP one tier above the sickle
''', '''    amt = @PKG@.FarmTier.apply(u, (String) info[2], (String) HELD.get(u), amt);   // 0.4.35: half XP one tier above the sickle
    amt = @PKG@.FarmTier.low(u, (String) info[2], amt);   // 0.4.68: less XP for a crop far below your Farming tier (each crop of the sweep)
''')
P.rep('''    if ((int) this.rule[0] == {PKG}.SkillDefs.FARMING) bamt = {PKG}.FarmTier.breakXp(this.u, this.ev, bamt);   // 0.4.35: half XP one tier up
''', '''    if ((int) this.rule[0] == {PKG}.SkillDefs.FARMING) {{
      bamt = {PKG}.FarmTier.breakXp(this.u, this.ev, bamt);   // 0.4.35: half XP one tier up
      {BTY} lbt = this.ev.getBlockType();
      bamt = {PKG}.FarmTier.low(this.u, lbt == null ? null : lbt.getId(), bamt);   // 0.4.68: low-tier crop falloff
    }}
''')
P.rep('''      {PKG}.SkillXp.gain(pr, {PKG}.Farm3.route({PKG}.SkillDefs.FARMING, this.ripe), this.amount);   // 0.4.37: Orchard routing
''', '''      {PKG}.SkillXp.gain(pr, {PKG}.Farm3.route({PKG}.SkillDefs.FARMING, this.ripe), {PKG}.FarmTier.low(this.u, this.ripe, this.amount));   // 0.4.37: Orchard routing; 0.4.68: low-tier crop falloff
''')

# ---- Farming's Stats page + the ready line
P.rep('''  if (!next) {{ String gp = {PKG}.GatherPace.statsLine(s, lv); if (gp != null) out.add(gp); }}   // 0.4.14: the gathering pace
''', '''  if (!next) {{ String gp = {PKG}.GatherPace.statsLine(s, lv); if (gp != null) out.add(gp); }}   // 0.4.14: the gathering pace
  if (!next && s == {PKG}.SkillDefs.FARMING) {{ String fl = {PKG}.FarmTier.statsLine(lv); if (fl != null) out.add(fl); }}   // 0.4.68: low-tier crops
''')
P.rep('''+ "; Farming one or two tiers above your hoe / sickle pays x" + {PKG}.Sickle.TIER_XP''',
      '''+ "; low-tier crop falloff " + {PKG}.FarmTier.lowText() + "; Farming one or two tiers above your hoe / sickle pays x" + {PKG}.Sickle.TIER_XP''')

# ---- the default-file checks (the newest block now ends the file)
P.rep('''_k not in R66_DEF and _k not in FX_DEF) == sorted(_e[0] for _e in P9_KEYS)''', '''_k not in R66_DEF and _k not in FX_DEF and _k not in LT_DEF) == sorted(_e[0] for _e in P9_KEYS)''')
P.rep('''DEFAULTS_066.endswith(G66_BLOCK) and DEFAULTS.endswith(FX_BLOCK)   # 0.4.62''', '''DEFAULTS_066.endswith(G66_BLOCK) and DEFAULTS_067.endswith(FX_BLOCK) and DEFAULTS.endswith(LT_BLOCK)   # 0.4.68: + the LT block; 0.4.62''')
P.rep('''assert all(_dp.get(_k) == _v for _k, _v in R66_KEYS)   # 0.4.66
''', '''assert all(_dp.get(_k) == _v for _k, _v in R66_KEYS)   # 0.4.66
assert all(_dp.get(_k) == _v for _k, _v in LT_KEYS)   # 0.4.68
''')

# ---- Server Setup rows (Skills -> Gathering), right after "Farming XP one tier above your tool"
P.rep('''assert [_r[4] for _r in CFG_ROWS if _r[0] == "fell.leafXpFactor"] == [FX_LEAF]
''', '''assert [_r[4] for _r in CFG_ROWS if _r[0] == "fell.leafXpFactor"] == [FX_LEAF]
# 0.4.68 (farmxp): the low-tier crop falloff rows, right after the tool-tier row (defaults = the LT block = the Sickle.readLow code defaults)
_ix68 = [_r[0] for _r in CFG_ROWS].index("farming.tierUpXpFactor")
for _j68, _row68 in enumerate([
        ("farming.lowTier.enabled", "Less Farming XP for low-tier crops", "gathering", "bool", LT_DEF["farming.lowTier.enabled"], "", "", "", "", "live",
         "Crops far below your Farming tier pay less XP (the two bands below). Off = every crop pays full.", "reload"),
        ("farming.lowTier.levels", "Farming tier levels", "gathering", "text", LT_DEF["farming.lowTier.levels"], "", "300", "", "", "live,adv",
         "The Farming level where each Farming tier starts, comma separated. Default = the crop tiers' levels.", "reload;check=Sickle.checkLowLevels"),
        ("farming.lowTier.gap1", "Low-tier crops: tiers below (band 1)", "gathering", "int", LT_DEF["farming.lowTier.gap1"], "0", "64", "", "", "live",
         "A crop this many tiers below your Farming tier (or more) pays band 1's XP. 0 = band off.", "reload"),
        ("farming.lowTier.mult1", "Low-tier crops: XP (band 1)", "gathering", "dec", LT_DEF["farming.lowTier.mult1"], "0", "1", "", "x", "live",
         "Band 1 crops pay their Farming XP times this.", "reload"),
        ("farming.lowTier.gap2", "Low-tier crops: tiers below (band 2)", "gathering", "int", LT_DEF["farming.lowTier.gap2"], "0", "64", "", "", "live",
         "A crop this many tiers below (or more) pays band 2's XP instead. 0 = band off.", "reload"),
        ("farming.lowTier.mult2", "Low-tier crops: XP (band 2)", "gathering", "dec", LT_DEF["farming.lowTier.mult2"], "0", "1", "", "x", "live",
         "Band 2 crops pay their Farming XP times this.", "reload")]):
    CFG_ROWS.insert(_ix68 + 1 + _j68, _row68)
assert [_r[0] for _r in CFG_ROWS][_ix68:_ix68 + 7] == ["farming.tierUpXpFactor"] + [_k for _k, _v in LT_KEYS]
assert all([_r[0] for _r in CFG_ROWS].count(_k) == 1 and ("%s=%s" % (_k, _v)) in DEFAULTS.split(chr(10)) for _k, _v in LT_KEYS)
assert all(_r[4] == LT_DEF[_r[0]] for _r in CFG_ROWS if _r[0] in LT_DEF)
''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0 and P.s.count("makeClass(") == CLS0
P.finish()
