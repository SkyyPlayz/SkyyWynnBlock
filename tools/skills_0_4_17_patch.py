"""Derive SkyySkills/build_skyyskills_0.4.17.py from the LIVE generated SkyySkills/build_skyyskills_0.4.16.py (= the tools/deploy_set.py SET
pin; 0.4.16 came from 0.4.15 by tools/skills_0_4_16_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). Same style as skills_0_4_16_patch.py: rep(old, new) with asserted single anchors, newline-agnostic;
0.4.16 stays untouched and its line endings are kept. Edit THIS file, never the generated script.
Run:  python tools/skills_0_4_17_patch.py   then   python SkyySkills/build_skyyskills_0.4.17.py   (NO --deploy: coordinated deploy)
Test: python SkyySkills/test_skyyskills_0.4.17.py   (bare JVM, -Xverify:all; scratch under tools/dev/scratch/mc-skills/, deleted afterwards)

0.4.17 = THE MOB CURVE'S SKYYSKILLS PART (research/Mob-Curve-Spec.md sections 2.4, 4.2, 6.3, 6.4, 7.2-7.4; every default accepted by Skyy
2026-10-05, docs/answered/mobs.md "Accept all defaults"). The spec was written as "SkyySkills 0.4.16"; 0.4.16 became Mining's own level list
(deployed 2026-10-05), so this content is 0.4.17 and keeps all of 0.4.16. Deploy and roll back TOGETHER with SkyyMobs 0.1.4 + SkyyGear 0.2.5
(spec 7.1 pairing; SkyySkills 0.4.17 alone is safe: without SkyyMobs' mob:fn:info it pays exactly 0.4.16's kill XP).

(1) KILL XP BY LEVEL (combat.xpFrom = level, the new default | health = 0.4.16 exactly). Level mode, when SkyyMobs publishes mob:fn:info:
    kill XP = one chance rounding (MobXp.payD, the pay rule) of
        clamp(xpBase x combat.perHealth, combat.min, combat.max) x multiplier x classSkill.xpMultiplier x levelCurve(L) x xpMult x gap(d)
    in double (no integer round / scaled step). xpBase = the mob's Lv 1 health (max(own base, SkyyMobs' floor)), xpMult = the difficulty
    share (Hard 1; Easy / Normal their old share; Custom never above Hard) - both from mob:fn:info. gap = MobXp.gapFactor (the LOCKED XP gap
    rows; combat.levelXp.enabled off -> 1 in level mode, the curve stays). levelCurve = the key-family table combat.levelCurve.<level>=<factor>
    (16 points, straight lines between, flat outside; default = (1 + 0.08 (L-1)) x (1 + 0.05 (L-1)) = today's Hard XP).
    - A role override (combat.role.<role>) keeps 0.4.16's maths: scaled(override) x class mult x levelFactor(L) x gap (never the curve).
    - mob:fn:info missing (SkyyMobs 0.1.3 or older / none) or combat.xpFrom=health -> 0.4.16 EXACTLY (MobXp.kill, mob:fn:level).
    - mob:fn:info present but null / malformed / throwing for this mob -> classXp(health-mode base): no level factor, no gap (<= combat.max).
    - The party share runs the same helper per member (PartyXp.share3 / one3: each member's own gap on the level-mode base).
    - The first-kill log line of a role gains "(Lv 1 health B)".
(2) MANA REGEN PER CLASS LEVEL (spec 2.4): mana.regen.perLevel (7 %) x max(0, class level - mana.regen.fromLevel (20)) is one more Mana
    Regen source inside ManaRegen.total (same MAX_PCT clamp; in combat x mana.regen.inCombat like every boost); "class level" in the
    source lists (Mana Regen: show mine, /skills mana, skill:fn:manaregen sources). Class level = the cached profile data of the player's
    current class skill (SkillClass.slot) - never a disk read from this path.
(3) ONE-TIME CONFIG UPDATE (KillXpMig, setup after SkillLvMig.run, BEFORE SkillCfg.load; PROJECT-RULES section 4): an existing
    xp.properties without a comment line holding the marker gets ONE block appended after its last line in its own line ending: the marker
    + only the lines it lacks - combat.xpFrom=level (+ ONE config-changes.log line "combat.xpFrom health -> level": Undo = 0.4.16's kill XP),
    the 16 combat.levelCurve.<L> lines generated from THE FILE's own combat.levelBonus (0 when combat.levelXp.enabled=false), and
    mana.regen.perLevel=7 / mana.regen.fromLevel=20, each part with its comment lines. No existing line changes (a Properties check proves
    it), the config-history copy first (HealMig.mgKit + CfgHist.snapshot + mgSaved), the kit's atomicWrite, one INFO line; a failure = WARN,
    file untouched, retried next start.
(4) Server Setup rows (spec 6.3): combat.xpFrom (choice), combat.levelCurve (table, check=MobXp.checkCurvePoint), mana.regen.perLevel,
    mana.regen.fromLevel; new label / help on combat.levelBonus, help on combat.levelXp.enabled and combat.perHealth.
NOT in this build: anything inside SkyyMobs / SkyyGear (their builders); the Stats page text (it never named the kill XP formula).
"""
import difflib
import math
import os
from decimal import Decimal

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.16.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.17.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.16"
s = raw.decode("utf8").replace("\r\n", "\n")
LF = "\n"
S0 = s
assert 'VERSION = "0.4.16"' in s and "derived from the generated 0.4.15 by tools/skills_0_4_16_patch.py" in s, "not the live generated 0.4.16"
assert s.count('DJ_L.append("acro.doubleJump.trigger=jump")') == 1, "not the edited lineage (Skyy's Double Jump trigger edit missing)"
for _x in ('".KillXpMig"', "combat.xpFrom", "combat.levelCurve", "mana.regen.perLevel", "mob:fn:info", "KXP_"):
    assert _x not in s, "0.4.16 already has " + _x
REG0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")
BIND0 = [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln]
OLDS = []


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:120]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:120])
    i = s.index(old)
    j = s.find(LF, i + len(old))
    OLDS.append(s[s.rfind(LF, 0, i) + 1:(j if j >= 0 else len(s))])
    s = s.replace(old, new)


def after(anchor, add):
    rep(anchor, anchor + add)


def before(anchor, add):
    rep(anchor, add + anchor)


def block(a, b):
    assert s.count(a) == 1 and s.count(b) == 1 and s.index(a) < s.index(b), (a[:60], b[:60])
    return s[s.index(a):s.index(b)]


# the default kill XP level curve (spec 4.2): (1 + 0.08 (L-1)) x (1 + B (L-1)), 2 decimals rounded half up, kit-canonical text (no trailing 0)
KXP_LEVELS = [1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100]


def kxp_fmt(f):
    c = int(math.floor(f * 100.0 + 0.5))
    c = 10 if c < 10 else (100000 if c > 100000 else c)
    return format(Decimal(c).scaleb(-2).normalize(), "f")


assert [kxp_fmt((1.0 + 0.08 * (L - 1)) * (1.0 + 0.05 * (L - 1))) for L in KXP_LEVELS] == [
    "1", "1.58", "2.49", "3.6", "4.91", "6.42", "8.13", "10.04", "12.15", "14.46", "16.97", "22.59", "29.01", "36.23", "44.25", "53.07"], "spec 4.2 table"

# blocks that must stay byte-identical (0.4.16 code this build does not touch)
KEEP = [block("# >>> SPELL GEN", "# <<< SPELL GEN"),
        block("# ================= Xbow part 1 (0.4.5)", "# ================= ClassCurve (0.4.12)"),
        block("# ================= 0.4.2 FELLED TREES", "# FellCredit (spec 2.6)"),
        block("# ================= skill:fn:addxp (0.4)", "# ================= leaderboard ================="),
        block("# ================= OverallPage (0.4.6)", "# ================= 0.4.3 ADMIN CONFIG"),
        block("# ---- 0.4.5 Xbow part 2", "# ================= ManaRegen (0.4.12)"),
        block("# ================= CombatDmgSys (0.3)", "# ================= PlacedStore"),
        block("# ================= RollSys (0.4.14)", "# ================= CombatDmgSys (0.3)"),
        block("# ================= Sickle (0.4.14, research/Tool-Levels-Spec.md question 3)", "# ================= Brew.extraPotion (0.4)"),
        block("# ================= SkillStore: per-player XP", "# ================= SkillClass (0.3)"),
        block("# ================= Overall (0.4.6)", "# ================= skill:fn:overall (0.4.6, spec 4.8)"),
        block("# ---- HealMig (0.4.11 point 5)", "# ---- DocMig (0.4.14, fix (5))"),
        block("# ================= ClassMana part 1 (0.4.15", "# ================= SkillLv (0.4.16)"),
        block("# ================= OwnCurve (0.4.16)", "# ================= GatherPace.apply (0.4.14)"),
        block("# ---- SkillLvMig (0.4.16)", "# ---- ManaGuard (point 3)"),
        block("# ================= SkillKit (0.4.3)", "# ================= commands =================")]

# ---------------------------------------------------------------------------------------------------------------- docstring + version
rep('''"""SkyySkills 0.4.16 - build script (derived from the generated 0.4.15 by tools/skills_0_4_16_patch.py - edit the patch, not this file;
0.4.15 was derived''', '''"""SkyySkills 0.4.17 - build script (derived from the generated 0.4.16 by tools/skills_0_4_17_patch.py - edit the patch, not this file;
0.4.16 was derived from the generated 0.4.15 by tools/skills_0_4_16_patch.py; 0.4.15 was derived''')
HEAD_0417 = '''0.4.17: THE MOB CURVE'S SKYYSKILLS PART (research/Mob-Curve-Spec.md 2.4 / 4.2 / 6.3 / 6.4; Skyy 2026-10-05 "accept all defaults"; full
  notes in tools/skills_0_4_17_patch.py). Deploy / roll back TOGETHER with SkyyMobs 0.1.4 + SkyyGear 0.2.5 (alone it pays 0.4.16's XP).
  KILL XP BY LEVEL: combat.xpFrom=level (default): with SkyyMobs' mob:fn:info a kill pays clamp(Lv 1 health x perHealth, min, max) x
     multiplier x class mult x the kill XP level curve (combat.levelCurve table, default = the old Hard XP) x the difficulty share x the gap
     rows, ONE chance rounding - SkyyMobs' bigger health never inflates XP. Role overrides keep 0.4.16's maths; no mob:fn:info or
     combat.xpFrom=health = 0.4.16 exactly; an info answer of null = no level factor / gap. Party members: the same helper, own gap.
  MANA REGEN PER CLASS LEVEL: +mana.regen.perLevel % (7) per class skill level above mana.regen.fromLevel (20), one more Mana Regen source.
  An existing xp.properties gets the new lines ONCE (KillXpMig: only the lines it lacks, the curve from its own levelBonus; History copy
     first; one change-log line combat.xpFrom health -> level with Undo; marker comment).
  CHECKED in a bare JVM (SkyySkills/test_skyyskills_0.4.17.py, -Xverify:all, scratch under tools/dev/scratch deleted afterwards).
'''
before("0.4.16: MINING'S OWN LEVEL LIST + LEADERBOARDS SKIP DELETED PROFILES (Skyy LOCKED 2026-10-04, OK 2026-10-05; full notes in\n", HEAD_0417)
rep('VERSION = "0.4.16"\n', 'VERSION = "0.4.17"\n')

# ---------------------------------------------------------------------------------------------------------------- default xp.properties block
KXP_PY = r'''# 0.4.17 (research/Mob-Curve-Spec.md 4.2 / 2.4 / 6.3-6.4, Skyy 2026-10-05 "accept all defaults"): kill XP by mob level + Mana regen per
# class level - ONE block at the end of a fresh file; KillXpMig appends it ONCE to an existing file (only the lines it lacks; the level
# curve generated from THAT file's combat.levelBonus). No comment line may look like a "#key=value" template line.
import math as _m17
from decimal import Decimal as _D17
KXP_MARK_ID = "SkyySkills 0.4.17 kill XP by level"
KXP_LEVELS = [1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100]
KXP_PER_DEF, KXP_FROM_DEF = "7", "20"


def kxp_fmt(f):
    c = int(_m17.floor(f * 100.0 + 0.5))
    c = 10 if c < 10 else (100000 if c > 100000 else c)
    return format(_D17(c).scaleb(-2).normalize(), "f")


def kxp_curve(b):
    return [(_L, kxp_fmt((1.0 + 0.08 * (_L - 1)) * (1.0 + b * (_L - 1)))) for _L in KXP_LEVELS]


KXP_DEF = kxp_curve(0.05)
assert [_v for _L, _v in KXP_DEF] == ["1", "1.58", "2.49", "3.6", "4.91", "6.42", "8.13", "10.04", "12.15", "14.46", "16.97", "22.59", "29.01",
                                      "36.23", "44.25", "53.07"], "spec 4.2 default table"
KXP_HEAD = ["# ---------- " + KXP_MARK_ID + " (+ Mana regen per class level) ----------",
            "# Comments must stay on their own lines."]
KXP_FROM = ["# KILL XP COMES FROM (Skyy 2026-10-05). level = with SkyyMobs 0.1.4+ a kill pays the mob's Lv 1 health x combat.perHealth (kept",
            "# between combat.min and combat.max) x the xp multiplier x the class skill XP multiplier x the kill XP level curve below x the",
            "# difficulty share (Easy and Normal pay their old share of Hard's XP, Custom never more than Hard) x the level gap rows, so bigger",
            "# mob health never inflates XP. health = SkyySkills 0.4.16: the mob's max health x (1 + combat.levelBonus x (level - 1)) x the gap.",
            "# A role with its own XP (combat.role) always pays the health way. Without SkyyMobs 0.1.4+ kills pay the health way.",
            "combat.xpFrom=level"]
KXP_CHEAD = ["# KILL XP LEVEL CURVE (one line per point: combat.levelCurve.<mob level> = factor, level 0 to 100, factor 0.1 to 1000): straight",
             "# lines between the points, flat outside them. Default = the old Hard XP (1 + 0.08 (L - 1)) x (1 + combat.levelBonus (L - 1)),",
             "# so a same-level kill pays within about 2 percent of SkyySkills 0.4.16 on Hard."]
KXP_MANA = ["# MANA REGEN PER CLASS LEVEL (Skyy 2026-10-05): Mana refills mana.regen.perLevel percent more per class skill level above",
            "# mana.regen.fromLevel (7 and 20: class level 30 = +70 percent, 40 = +140 percent). It is one more Mana Regen boost, in and",
            "# out of combat (in combat at mana.regen.inCombat percent, like every boost). 0 = off."]
KXP_PER_LINE = "mana.regen.perLevel=" + KXP_PER_DEF
KXP_FL_LINE = "mana.regen.fromLevel=" + KXP_FROM_DEF
KXP_L = KXP_HEAD + KXP_FROM + KXP_CHEAD + ["combat.levelCurve.%d=%s" % (_L, _v) for _L, _v in KXP_DEF] + KXP_MANA + [KXP_PER_LINE, KXP_FL_LINE]
L.append("")
L.extend(KXP_L)
KXP_DEFAULTS = "\n".join(KXP_L) + "\n"
assert all(ord(ch) < 128 for ch in KXP_DEFAULTS) and '"' not in KXP_DEFAULTS and "\\" not in KXP_DEFAULTS
assert not any(_cre.match(r"#\s*[A-Za-z][A-Za-z0-9._-]*\s*[=:]\s*\S+\s*$", _ln) for _ln in KXP_L), "a comment looks like a template line"
KXP_KEYS = [_ln.split("=", 1)[0] for _ln in KXP_L if not _ln.startswith("#")]
assert KXP_KEYS == ["combat.xpFrom"] + ["combat.levelCurve.%d" % _L for _L in KXP_LEVELS] + ["mana.regen.perLevel", "mana.regen.fromLevel"]
assert sum(1 for _ln in KXP_L if KXP_MARK_ID in _ln) == 1 and all(len(_ln) <= 140 for _ln in KXP_L)


def _kxp_lit(lines):
    return json.dumps("\n".join(lines) + "\n")


KXP_HEAD_LIT, KXP_FROM_LIT, KXP_CHEAD_LIT, KXP_MANA_LIT = _kxp_lit(KXP_HEAD), _kxp_lit(KXP_FROM), _kxp_lit(KXP_CHEAD), _kxp_lit(KXP_MANA)
assert KXP_DEFAULTS == json.loads(KXP_HEAD_LIT) + json.loads(KXP_FROM_LIT) + json.loads(KXP_CHEAD_LIT) + "".join(
    "combat.levelCurve.%d=%s\n" % (_L, _v) for _L, _v in KXP_DEF) + json.loads(KXP_MANA_LIT) + KXP_PER_LINE + "\n" + KXP_FL_LINE + "\n"
'''
after("SKL_HEAD_LIT = json.dumps(SKL_HEAD_TEXT)\n", KXP_PY)

# ---------------------------------------------------------------------------------------------------------------- MobXp: mode + level curve
MXP_CFG = r'''# 0.4.17 (Mob-Curve-Spec 4.2): combat.xpFrom (LEVEL: true = Mob level mode, the default; false = Mob health mode = 0.4.16) and the kill XP
# level curve combat.levelCurve.<level>=<factor> (CURVE = {double[] levels ascending, double[] factors}, replaced whole; CURVE_N = the
# entries read from the file, 0 = the default points). eval = SkyyGear's GearBase.eval (straight lines, flat outside the first / last point).
mxp.addField(CtField.make("public static volatile boolean LEVEL = true;", mxp))
mxp.addField(CtField.make("public static volatile Object[] CURVE = null;", mxp))
mxp.addField(CtField.make("public static volatile int CURVE_N = 0;", mxp))
mxp.addField(CtField.make('public static volatile String CURVE_WARNED = "";', mxp))
mxp.addField(CtField.make("public static boolean INFO_FAILED_ONCE = false;", mxp))
mxp.addField(CtField.make('public static final String CURVE_PREFIX = "combat.levelCurve.";', mxp))
mxp.addField(CtField.make("public static final double[] DEF_LV = new double[] { %s };" % ", ".join("%d.0" % _L for _L, _v in KXP_DEF), mxp))
mxp.addField(CtField.make("public static final double[] DEF_F = new double[] { %s };" % ", ".join(repr(float(_v)) for _L, _v in KXP_DEF), mxp))
mxp.addMethod(CtNewMethod.make(J14(r"""
public static double eval(Object[] p, double x) {
  if (p == null) return 1.0;
  double[] ls = (double[]) p[0];
  double[] vs = (double[]) p[1];
  int n = ls.length;
  if (n == 0) return 1.0;
  if (x <= ls[0]) return vs[0];
  if (x >= ls[n - 1]) return vs[n - 1];
  for (int i = 1; i < n; i++) {
    if (x <= ls[i]) return vs[i - 1] + (vs[i] - vs[i - 1]) * (x - ls[i - 1]) / (ls[i] - ls[i - 1]);
  }
  return vs[n - 1];
}"""), mxp))
mxp.addMethod(CtNewMethod.make(J14(r"""
public static double curve(int L) {
  Object[] p = CURVE;
  if (p == null) p = new Object[] { DEF_LV, DEF_F };
  return eval(p, (double) L);
}"""), mxp))
# an entry text -> its mob level 0-100, -1 = not a whole number 0-100 (1-3 digits)
mxp.addMethod(CtNewMethod.make(J14(r"""
public static int curveLevel(String e) {
  if (e == null) return -1;
  String t = e.trim();
  if (t.length() == 0 || t.length() > 3) return -1;
  for (int i = 0; i < t.length(); i++) if (t.charAt(i) < '0' || t.charAt(i) > '9') return -1;
  int v = Integer.parseInt(t);
  return v <= 100 ? v : -1;
}"""), mxp))
# a factor text -> 0.1-1000, NaN = not a number in the row's bounds
mxp.addMethod(CtNewMethod.make(J14(r"""
public static double curveFactor(String v) {
  if (v == null) return Double.NaN;
  double d = Double.NaN;
  try { d = Double.parseDouble(v.trim()); } catch (Throwable t) { return Double.NaN; }
  if (Double.isNaN(d) || Double.isInfinite(d) || d < 0.1 || d > 1000.0) return Double.NaN;
  return d;
}"""), mxp))
# the table lines -> {Object[] points or null (no good entry), Integer good entries, String problems}; keys in sort order (of two spellings
# of one level - "05" and "5" - the first wins, the other is reported)
mxp.addMethod(CtNewMethod.make(J14(r"""
public static Object[] parseCurve(java.util.Properties p) {
  java.util.TreeMap pts = new java.util.TreeMap();
  StringBuilder bad = new StringBuilder();
  java.util.Iterator it = new java.util.TreeSet(p.stringPropertyNames()).iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    if (!k.startsWith(CURVE_PREFIX)) continue;
    String e = k.substring(CURVE_PREFIX.length());
    String shown = e.length() > 20 ? e.substring(0, 20) + "..." : e;
    int lv = curveLevel(e);
    if (lv < 0) { if (bad.length() > 0) bad.append("; "); bad.append(shown + " is not a mob level 0 to 100 (left out)"); continue; }
    Integer key = Integer.valueOf(lv);
    if (pts.containsKey(key)) { if (bad.length() > 0) bad.append("; "); bad.append("level " + lv + " is listed twice (" + shown + " left out)"); continue; }
    double f = curveFactor(p.getProperty(k));
    if (Double.isNaN(f)) { if (bad.length() > 0) bad.append("; "); bad.append("level " + shown + ": not a factor 0.1 to 1000 (left out)"); continue; }
    pts.put(key, Double.valueOf(f));
  }
  int n = pts.size();
  if (n == 0) return new Object[] { null, Integer.valueOf(0), bad.toString() };
  double[] ls = new double[n];
  double[] vs = new double[n];
  int i = 0;
  java.util.Iterator jt = pts.entrySet().iterator();
  while (jt.hasNext()) {
    java.util.Map.Entry en = (java.util.Map.Entry) jt.next();
    ls[i] = (double) ((Integer) en.getKey()).intValue();
    vs[i] = ((Double) en.getValue()).doubleValue();
    i++;
  }
  return new Object[] { new Object[] { ls, vs }, Integer.valueOf(n), bad.toString() };
}"""), mxp))
mxp.addMethod(CtNewMethod.make(J14(r"""
public static void readCurve(java.util.Properties p) {
  Object[] r = parseCurve(p);
  int n = ((Integer) r[1]).intValue();
  String w = (String) r[2];
  if (n == 0) w = (w.length() > 0 ? w + "; " : "") + "no usable entry - the default curve (the old Hard XP) is used";
  if (n == 0) CURVE = null;
  else CURVE = (Object[]) r[0];
  CURVE_N = n;
  String ww = w.length() > 0 ? "Kill XP level curve: " + w : "";
  if (ww.length() > 0 && !ww.equals(CURVE_WARNED) && LEVEL) @PKG@.SkillCfg.warn(ww);
  CURVE_WARNED = ww;
}"""), mxp))
# check= hook of the combat.levelCurve table (key "combat.levelCurve[<entry>]", value = the typed factor or null for a removal; also run for
# hand-edited lines): the entry must be a mob level 0-100; the last entry cannot be removed (the kit checks the factor's 0.1-1000 bounds)
mxp.addMethod(CtNewMethod.make(J14(r"""
public static String checkCurvePoint(String key, String value) {
  if (key == null) return null;
  String e = key;
  int a = key.indexOf('[');
  int b = key.lastIndexOf(']');
  if (a >= 0 && b > a) e = key.substring(a + 1, b);
  if (value == null) return CURVE_N <= 1 ? "Keep at least one point - the curve needs one (change its factor instead)." : null;
  if (curveLevel(e) < 0) return "Entry = a mob level, a whole number 0 to 100.";
  if (Double.isNaN(curveFactor(value))) return "Factor = a number from 0.1 to 1000.";
  return null;
}"""), mxp))
'''
before('''mxp.addMethod(CtNewMethod.make(J14(r"""
public static void read(java.util.Properties p) {
  ON = @PKG@.SkillCfg.bool(p, "combat.levelXp.enabled", true);''', MXP_CFG)
rep('''  MIN = @PKG@.AcroCfg.clampD(@PKG@.SkillCfg.dbl(p, "combat.gap.min", 0.1), 0.0, 1.0);
}"""), mxp))''', '''  MIN = @PKG@.AcroCfg.clampD(@PKG@.SkillCfg.dbl(p, "combat.gap.min", 0.1), 0.0, 1.0);
  // 0.4.17: combat.xpFrom (missing = level; anything but level / health = level + one WARN) and the kill XP level curve
  String xf = String.valueOf(p.getProperty("combat.xpFrom", "level")).trim();
  if (!xf.equalsIgnoreCase("level") && !xf.equalsIgnoreCase("health")) @PKG@.SkillCfg.warn("combat.xpFrom=" + xf + " is not level or health - using level");
  LEVEL = !xf.equalsIgnoreCase("health");
  readCurve(p);
}"""), mxp))''')
rep('''public static String text() {
  if (!ON) return "off";
  return "on (+" + @PKG@.DivCfg.num(BONUS * 100.0) + "% a mob level; more than " + FREE + " levels above your class skill +" + @PKG@.DivCfg.num(ABOVE * 100.0) + "% a level up to x" + @PKG@.DivCfg.num(MAX) + ", below -" + @PKG@.DivCfg.num(BELOW * 100.0) + "% a level down to x" + @PKG@.DivCfg.num(MIN) + "; SkyyMobs levels)";
}"""), mxp))''', '''public static String text() {
  String gap = "more than " + FREE + " levels above your class skill +" + @PKG@.DivCfg.num(ABOVE * 100.0) + "% a level up to x" + @PKG@.DivCfg.num(MAX) + ", below -" + @PKG@.DivCfg.num(BELOW * 100.0) + "% a level down to x" + @PKG@.DivCfg.num(MIN);
  if (LEVEL) return "from the mob level (Lv 1 health x the level curve: Lv 20 x" + @PKG@.DivCfg.num(curve(20)) + ", Lv 40 x" + @PKG@.DivCfg.num(curve(40)) + (CURVE_N == 0 ? " default" : ", " + CURVE_N + " points") + " x the difficulty share; SkyyMobs 0.1.4+, else from mob health)" + (ON ? "; gap " + gap : "; level gap off");
  if (!ON) return "from mob health, off";
  return "from mob health, on (+" + @PKG@.DivCfg.num(BONUS * 100.0) + "% a mob level; " + gap + "; SkyyMobs levels)";
}"""), mxp))''')

# ---------------------------------------------------------------------------------------------------------------- ManaRegen: class level perk
after('''mrg.addField(CtField.make("public static volatile int IN_COMBAT = " + MREG_DEF + ";", mrg))   # mana.regen.inCombat (0-100 %)\n''',
      '''mrg.addField(CtField.make("public static volatile double PER_LEVEL = " + KXP_PER_DEF + ".0;", mrg))   # 0.4.17: mana.regen.perLevel (0-100 %)
mrg.addField(CtField.make("public static volatile int FROM_LEVEL = " + KXP_FROM_DEF + ";", mrg))   # 0.4.17: mana.regen.fromLevel (0-100)
''')
before('''# the % that applies to this player: the sum of every source, below 0 = 0 (no drain), at most MAX_PCT; NaN / infinite entries skipped
mrg.addMethod(CtNewMethod.make("""
public static double total(java.util.UUID u) {''', r'''# 0.4.17 (Mob-Curve-Spec 2.4): Mana Regen % from the class level = PER_LEVEL x max(0, class level - FROM_LEVEL). Class level = the player's
# CURRENT class skill (SkillClass.slot: SkyyClasses' class:<uuid>) in the profile data already in memory (SkillStore.DATA, the profile
# key) - never a file read from here (the regen tick, the bridge and texts call it); no class / no data = 0. Any thread.
mrg.addMethod(CtNewMethod.make(J14(r"""
public static double classPct(java.util.UUID u) {
  try {
    double per = PER_LEVEL;
    if (u == null || !(per > 0.0)) return 0.0;
    int s = @PKG@.SkillClass.slot(u);
    if (s < 0 || s >= @PKG@.SkillDefs.N) return 0.0;
    long[] d = (long[]) @PKG@.SkillStore.DATA.get(@PKG@.SkillStore.pkey(u));
    if (d == null || s >= d.length) return 0.0;
    int over = @PKG@.SkillDefs.levelOf(s, @PKG@.SkillStore.rd(d, s)) - FROM_LEVEL;
    return over > 0 ? per * (double) over : 0.0;
  } catch (Throwable t) { return 0.0; }
}"""), mrg))
''')
rep('''  if (u == null) return 0.0;
  Object o = SRC.get(u);
  if (!(o instanceof java.util.Map)) return 0.0;
  double sum = 0.0;
''', '''  if (u == null) return 0.0;
  double sum = classPct(u);   // 0.4.17: + the class level perk (one more source, inside the same clamp)
  Object o = SRC.get(u);
  if (!(o instanceof java.util.Map)) return clampTotal(sum);
''')
rep('''  Object o = u == null ? null : SRC.get(u);
  if (!(o instanceof java.util.Map)) return new String[0];
  java.util.TreeMap t = new java.util.TreeMap((java.util.Map) o);
''', '''  Object o = u == null ? null : SRC.get(u);
  double cp = classPct(u);   // 0.4.17: the class level perk is listed as "class level"
  if (!(o instanceof java.util.Map) && !(cp > 0.0)) return new String[0];
  java.util.TreeMap t = o instanceof java.util.Map ? new java.util.TreeMap((java.util.Map) o) : new java.util.TreeMap();
  if (cp > 0.0) t.put("class level", Double.valueOf(cp));
''')

# ---------------------------------------------------------------------------------------------------------------- SkillCfg.load
rep('''    {PKG}.ManaRegen.IN_COMBAT = (int) (mrc < 0L ? 0L : (mrc > 100L ? 100L : mrc));
''', '''    {PKG}.ManaRegen.IN_COMBAT = (int) (mrc < 0L ? 0L : (mrc > 100L ? 100L : mrc));
    // 0.4.17: Mana regen per class level, clamped to the row bounds 0-100 (a bad number = the default)
    double mpl = dbl(p, "mana.regen.perLevel", {KXP_PER_DEF}.0);
    {PKG}.ManaRegen.PER_LEVEL = (Double.isNaN(mpl) || mpl < 0.0) ? 0.0 : (mpl > 100.0 ? 100.0 : mpl);
    long mfl = lng(p, "mana.regen.fromLevel", {KXP_FROM_DEF}L);
    {PKG}.ManaRegen.FROM_LEVEL = (int) (mfl < 0L ? 0L : (mfl > 100L ? 100L : mfl));
''')
rep('''", in-combat Mana regen " + {PKG}.ManaRegen.IN_COMBAT + "%" + ", kill XP by mob level " + {PKG}.MobXp.text()''',
    '''", in-combat Mana regen " + {PKG}.ManaRegen.IN_COMBAT + "%" + ", Mana regen +" + {PKG}.DivCfg.num({PKG}.ManaRegen.PER_LEVEL) + "% per class level above " + {PKG}.ManaRegen.FROM_LEVEL + ", kill XP " + {PKG}.MobXp.text()''')

# ---------------------------------------------------------------------------------------------------------------- SkillCfg.combatXp2
rep('''cfg.addMethod(CtNewMethod.make("""
public static long combatXp(String role, float maxHp) {
  if (role != null) {
    Long o = (Long) ROLE.get(role);
    if (o != null) return scaled(o.longValue());
    if (SEEN_ROLES.putIfAbsent(role, Boolean.TRUE) == null) info("combat: first kill of NPC role " + role + " (max health " + maxHp + ") - override with combat.role." + role + "=<xp>");
  }''', '''# 0.4.17: combatXp2 = 0.4.16's combatXp + the mob's Lv 1 health in the first-kill line (lv1 > 0: from SkyyMobs' mob:fn:info)
cfg.addMethod(CtNewMethod.make("""
public static long combatXp2(String role, float maxHp, double lv1) {
  if (role != null) {
    Long o = (Long) ROLE.get(role);
    if (o != null) return scaled(o.longValue());
    if (SEEN_ROLES.putIfAbsent(role, Boolean.TRUE) == null) info("combat: first kill of NPC role " + role + " (max health " + maxHp + ")" + (lv1 > 0.0 ? " (Lv 1 health " + {PKG}.DivCfg.num(lv1) + ")" : "") + " - override with combat.role." + role + "=<xp>");
  }''')
rep('''  if (x > C_MAX) x = C_MAX;
  return scaled(x);
}""", cfg))
''', '''  if (x > C_MAX) x = C_MAX;
  return scaled(x);
}""".replace("{PKG}", PKG), cfg))
cfg.addMethod(CtNewMethod.make("""
public static long combatXp(String role, float maxHp) {
  return combatXp2(role, maxHp, -1.0);
}""", cfg))
''')

# ---------------------------------------------------------------------------------------------------------------- MobXp maths: payD, infoOf, lvBase
MXP_MATH = r'''# 0.4.17: payD = pay with a double base (Mob level mode: ONE chance rounding of the whole product, spec 4.2)
mxp.addMethod(CtNewMethod.make(J14(r"""
public static long payD(int slot, double base, double factor) {
  if (!(base > 0.0) || !(factor > 0.0) || Double.isInfinite(base) || Double.isInfinite(factor)) return 0L;
  double m = @PKG@.SkillDefs.isClass(slot) ? @PKG@.SkillCfg.CLASS_MULT : 1.0;
  if (!(m > 0.0)) return 0L;
  double x = base * m * factor;
  if (x >= 9.0E15) return 9000000000000000L;
  double r = Math.rint(x);
  if (Math.abs(x - r) < 1.0E-9) x = r;
  long w = (long) Math.floor(x);
  double f = x - (double) w;
  if (f > 0.0 && java.util.concurrent.ThreadLocalRandom.current().nextDouble() < f) w++;
  return w;
}"""), mxp))
mxp.addMethod(CtNewMethod.make(J14(r"""
public static boolean infoFn() {
  try { return @PKG@.SkillStore.bridge().get("mob:fn:info") instanceof java.util.function.Function; } catch (Throwable t) { return false; }
}"""), mxp))
# the dead mob's SkyyMobs mob:fn:info answer (spec 7.3: Object[]{String world, UUID npc} -> Object[]{Integer level, Double base, Double xpBase,
# Double hpMult, Double dmgMult, Double xpMult} or null; it still answers at the DeathComponent like mob:fn:level) -> double[]{level, xpBase,
# xpMult} or null (no function, no answer, level < 1, xpBase not above 0, anything malformed or throwing). xpMult missing / not a finite
# number = 1 (Hard's share); clamped 0-100 (an elite build may multiply its own factor in later).
mxp.addMethod(CtNewMethod.make(J14(r"""
public static double[] infoOf(@ST@ s, @REF@ r) {
  try {
    if (s == null || r == null) return null;
    Object f = @PKG@.SkillStore.bridge().get("mob:fn:info");
    if (!(f instanceof java.util.function.Function)) return null;
    @UUC@ uc = (@UUC@) s.getComponent(r, @UUC@.getComponentType());
    if (uc == null || uc.getUuid() == null) return null;
    String wn = null;
    Object ext = s.getExternalData();
    if (ext instanceof @EST@) {
      @WLD@ w = ((@EST@) ext).getWorld();
      if (w != null) wn = w.getName();
    }
    Object o = ((java.util.function.Function) f).apply(new Object[] { wn, uc.getUuid() });
    if (!(o instanceof Object[])) return null;
    Object[] a = (Object[]) o;
    if (a.length < 3 || !(a[0] instanceof Number) || !(a[2] instanceof Number)) return null;
    int L = ((Number) a[0]).intValue();
    double xb = ((Number) a[2]).doubleValue();
    if (L < 1 || !(xb > 0.0) || Double.isInfinite(xb)) return null;
    double xm = 1.0;
    if (a.length >= 6 && a[5] instanceof Number) {
      xm = ((Number) a[5]).doubleValue();
      if (Double.isNaN(xm) || Double.isInfinite(xm)) xm = 1.0;
    }
    if (xm < 0.0) xm = 0.0;
    if (xm > 100.0) xm = 100.0;
    return new double[] { (double) L, xb, xm };
  } catch (Throwable t) {
    if (!INFO_FAILED_ONCE) { INFO_FAILED_ONCE = true; @PKG@.SkillCfg.warn("mob info lookup (mob:fn:info) failed (logged once; that kill pays without a level): " + t); }
    return null;
  }
}"""), mxp))
# Mob level mode: the kill XP before the class skill XP multiplier and the gap = clamp(xpBase x perHealth, min, max) x multiplier x
# levelCurve(L) x xpMult (doubles; the clamp in the 0.4.16 order: an inverted min / max pays the max)
mxp.addMethod(CtNewMethod.make(J14(r"""
public static double lvBase(double xpBase, int L, double xpMult) {
  double x = xpBase * @PKG@.SkillCfg.C_PER_HP;
  if (Double.isNaN(x) || x < 0.0) x = 0.0;
  if (x < (double) @PKG@.SkillCfg.C_MIN) x = (double) @PKG@.SkillCfg.C_MIN;
  if (x > (double) @PKG@.SkillCfg.C_MAX) x = (double) @PKG@.SkillCfg.C_MAX;
  double m = @PKG@.SkillCfg.MULT;
  if (!(m > 0.0) || !(xpMult > 0.0)) return 0.0;
  double v = x * m * curve(L) * xpMult;
  return v > 0.0 && !Double.isInfinite(v) ? v : 0.0;
}"""), mxp))
'''
after('''    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.SkillCfg.warn("mob level lookup (mob:fn:level) failed (logged once): " + t); }
    return -1;
  }
}"""), mxp))
''', MXP_MATH)

# ---------------------------------------------------------------------------------------------------------------- PartyXp: one3 / share3
rep('''public static long one2(java.util.UUID ku, String kn, {V3D} kpos, {ST} s, String mid, long base, double fr, double r2, int ks, long raw, int ml) {{''',
    '''public static long one3(java.util.UUID ku, String kn, {V3D} kpos, {ST} s, String mid, long base, double fr, double r2, int ks, long raw, int ml, double lvb) {{''')
rep('''  if (ml >= 1) b = {PKG}.MobXp.pay(ks, raw, {PKG}.MobXp.factor(ml, {PKG}.SkillStore.level(mu, slot)));   // 0.4.14
''', '''  if (ml >= 1 && lvb >= 0.0) b = {PKG}.MobXp.payD(ks, lvb, {PKG}.MobXp.gapFactor(ml, {PKG}.SkillStore.level(mu, slot)));   // 0.4.17: Mob level mode, this member's own gap
  else if (ml >= 1) b = {PKG}.MobXp.pay(ks, raw, {PKG}.MobXp.factor(ml, {PKG}.SkillStore.level(mu, slot)));   // 0.4.14
''')
rep('''  return amt;
}}""", pxp))
# 0.4.13's one (no mob level), kept for any caller of the old signature
''', '''  return amt;
}}""", pxp))
# 0.4.17: 0.4.14's one2 (no level-mode base), kept for any caller of the old signature
pxp.addMethod(CtNewMethod.make(f"""
public static long one2(java.util.UUID ku, String kn, {V3D} kpos, {ST} s, String mid, long base, double fr, double r2, int ks, long raw, int ml) {{
  return one3(ku, kn, kpos, s, mid, base, fr, r2, ks, raw, ml, -1.0);
}}""", pxp))
# 0.4.13's one (no mob level), kept for any caller of the old signature
''')
rep('''public static void share2({PR} kp, {REF} kr, {ST} s, long base, int ks, long raw, int ml) {{
  if (!{PKG}.PartyCfg.on() || (ml >= 1 ? raw <= 0L : base <= 0L) || kp == null || kr == null || s == null) return;''',
    '''public static void share3({PR} kp, {REF} kr, {ST} s, long base, int ks, long raw, int ml, double lvb) {{
  if (!{PKG}.PartyCfg.on() || (ml >= 1 && lvb >= 0.0 ? !(lvb > 0.0) : (ml >= 1 ? raw <= 0L : base <= 0L)) || kp == null || kr == null || s == null) return;''')
rep('''      one2(ku, kn, kpos, s, ms[i], base, fr, r2, ks, raw, ml);
''', '''      one3(ku, kn, kpos, s, ms[i], base, fr, r2, ks, raw, ml, lvb);
''')
rep('''}}""", pxp))
# 0.4.13's share (no mob level), kept for any caller of the old signature
''', '''}}""", pxp))
# 0.4.17: 0.4.14's share2 (no level-mode base; lvb -1 = not Mob level mode), kept for any caller of the old signature
pxp.addMethod(CtNewMethod.make(f"""
public static void share2({PR} kp, {REF} kr, {ST} s, long base, int ks, long raw, int ml) {{
  share3(kp, kr, s, base, ks, raw, ml, -1.0);
}}""", pxp))
# 0.4.13's share (no mob level), kept for any caller of the old signature
''')

# ---------------------------------------------------------------------------------------------------------------- MobXp.kill2 + KillSys
KILL2 = r'''# 0.4.17 (Mob-Curve-Spec 4.2): THE kill XP entry (world thread, KillSys). Mob health mode, or no mob:fn:info (SkyyMobs 0.1.3 or older / none)
# -> kill(... combatXp(role, maxHp) ...) = 0.4.16 EXACTLY. Mob level mode with mob:fn:info: info null -> classXp(the health-mode base) (no level
# factor, no gap, bounded by combat.max); a role override -> 0.4.16's maths (levelFactor x gap); else payD(lvBase x the gap against the
# killer's class skill before this kill) and the party share on the same level-mode base (each member's own gap).
mxp.addMethod(CtNewMethod.make(J14(r"""
public static long kill2(@PR@ pr, @REF@ k, @ST@ s, int slot, String role, float maxHp, @REF@ npc) {
  if (!LEVEL || !infoFn()) return kill(pr, k, s, slot, @PKG@.SkillCfg.combatXp(role, maxHp), npc);
  double[] in = infoOf(s, npc);
  long base = @PKG@.SkillCfg.combatXp2(role, maxHp, in == null ? -1.0 : in[1]);
  long cx;
  if (in == null) {
    cx = @PKG@.SkillCfg.classXp(slot, base);
    @PKG@.SkillXp.gain(pr, slot, cx);
    @PKG@.PartyXp.share2(pr, k, s, cx, slot, base, -1);
    return cx;
  }
  int L = (int) in[0];
  if (role != null && @PKG@.SkillCfg.ROLE.get(role) != null) {
    if (ON) cx = pay(slot, base, factor(L, @PKG@.SkillStore.level(pr.getUuid(), slot)));
    else cx = @PKG@.SkillCfg.classXp(slot, base);
    @PKG@.SkillXp.gain(pr, slot, cx);
    @PKG@.PartyXp.share2(pr, k, s, cx, slot, base, ON ? L : -1);
    return cx;
  }
  double lb = lvBase(in[1], L, in[2]);
  cx = payD(slot, lb, gapFactor(L, @PKG@.SkillStore.level(pr.getUuid(), slot)));
  @PKG@.SkillXp.gain(pr, slot, cx);
  @PKG@.PartyXp.share3(pr, k, s, cx, slot, base, L, lb);
  return cx;
}"""), mxp))
'''
after('''  @PKG@.PartyXp.share2(pr, k, s, cx, slot, base, ON ? L : -1);
  return cx;
}"""), mxp))
''', KILL2)
rep('''    {PKG}.MobXp.kill(pr, k, s, slot, {PKG}.SkillCfg.combatXp(role, maxHp), r);   // 0.4.14: x the mob level bonus and the level gap (SkyyMobs)''',
    '''    {PKG}.MobXp.kill2(pr, k, s, slot, role, maxHp, r);   // 0.4.17: Mob level mode (SkyyMobs mob:fn:info) or 0.4.14's level bonus + gap''')

# ---------------------------------------------------------------------------------------------------------------- KillXpMig
KXMIG = r'''# ---- KillXpMig (0.4.17, Mob-Curve-Spec 6.4): kill XP by level + Mana regen per class level reach an EXISTING xp.properties ONCE. setup()
# only, after SkillLvMig.run, BEFORE SkillCfg.load and CfgPub.start. Nothing to do = no file (load() writes the 0.4.17 default) or a comment
# line holding MARK_ID (done before). Else ONE block appended after the last line in the file's own line ending: the marker + only the lines
# the file lacks - combat.xpFrom=level (+ ONE config-changes.log line combat.xpFrom health -> level: Undo = 0.4.16's kill XP), the 16
# combat.levelCurve.<L> lines generated from THE FILE's combat.levelBonus (0 when combat.levelXp.enabled=false: a hand-set bonus or a
# switched-off part keeps its effect), mana.regen.perLevel / mana.regen.fromLevel - each part with its comment lines. No existing line
# changes (Properties check), config-history copy first (HealMig.mgKit + CfgHist.snapshot + mgSaved), the kit's atomicWrite, one INFO line.
# A failure = WARN, file untouched, retried next start.
kxm.addField(CtField.make("public static final String MARK_ID = %s;" % json.dumps(KXP_MARK_ID), kxm))
kxm.addField(CtField.make("public static final String HEAD = " + KXP_HEAD_LIT + ";", kxm))
kxm.addField(CtField.make("public static final String FROM_TXT = " + KXP_FROM_LIT + ";", kxm))
kxm.addField(CtField.make("public static final String CURVE_HEAD = " + KXP_CHEAD_LIT + ";", kxm))
kxm.addField(CtField.make("public static final String MANA_HEAD = " + KXP_MANA_LIT + ";", kxm))
kxm.addField(CtField.make("public static final int[] LEVELS = new int[] { %s };" % ", ".join(str(_L) for _L in KXP_LEVELS), kxm))
kxm.addField(CtField.make('public static final String FROM_KEY = "combat.xpFrom";', kxm))
kxm.addField(CtField.make('public static final String PER_KEY = "mana.regen.perLevel";', kxm))
kxm.addField(CtField.make('public static final String FL_KEY = "mana.regen.fromLevel";', kxm))
kxm.addField(CtField.make('public static final String PER_DEF = "%s";' % KXP_PER_DEF, kxm))
kxm.addField(CtField.make('public static final String FL_DEF = "%s";' % KXP_FROM_DEF, kxm))
kxm.addField(CtField.make('public static final String WHO = "SkyySkills 0.4.17";', kxm))
# (1 + 0.08 (L - 1)) x (1 + b (L - 1)) -> 2 decimals rounded half up, clamped to the row bounds 0.1-1000, kit-canonical text ("1", "3.6")
kxm.addMethod(CtNewMethod.make(J14(r"""
public static String fmt(double f) {
  long c = Math.round(f * 100.0);
  if (c < 10L) c = 10L;
  if (c > 100000L) c = 100000L;
  return java.math.BigDecimal.valueOf(c, 2).stripTrailingZeros().toPlainString();
}"""), kxm))
kxm.addMethod(CtNewMethod.make(J14(r"""
public static String factorText(int L, double b) {
  return fmt((1.0 + 0.08 * (double) (L - 1)) * (1.0 + b * (double) (L - 1)));
}"""), kxm))
kxm.addMethod(CtNewMethod.make(J14(r"""
public static String curveLines(double b) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < LEVELS.length; i++) sb.append(@PKG@.MobXp.CURVE_PREFIX).append(LEVELS[i]).append('=').append(factorText(LEVELS[i], b)).append('\n');
  return sb.toString();
}"""), kxm))
# the level bonus the file's own 0.4.16 kill XP used: combat.levelBonus (MobXp.read's clamp) while combat.levelXp.enabled, else 0
kxm.addMethod(CtNewMethod.make(J14(r"""
public static double bonusOf(java.util.Properties p) {
  if (!@PKG@.SkillCfg.bool(p, "combat.levelXp.enabled", true)) return 0.0;
  return @PKG@.AcroCfg.clampD(@PKG@.SkillCfg.dbl(p, "combat.levelBonus", 0.05), 0.0, 10.0);
}"""), kxm))
kxm.addMethod(CtNewMethod.make(J14(r"""
public static boolean hasCurve(java.util.Properties p) {
  java.util.Iterator it = p.stringPropertyNames().iterator();
  while (it.hasNext()) if (((String) it.next()).startsWith(@PKG@.MobXp.CURVE_PREFIX)) return true;
  return false;
}"""), kxm))
# pure text step (ISO-8859-1 chars in and out; lines read with the kit's own parser): null = nothing to do (the marker is in a comment line,
# or the text cannot be read as Properties); else { new text, String[] { key, old, new }* (the change-log rows), Boolean xpFrom added,
# Boolean curve added, Boolean perLevel added, Boolean fromLevel added, Double the bonus the curve was made from }. Never throws for any text.
kxm.addMethod(CtNewMethod.make(J14(r"""
public static Object[] plan(String text) {
  if (text == null) return null;
  java.util.Properties p = new java.util.Properties();
  try { p.load(new java.io.StringReader(text)); } catch (Throwable t) { return null; }
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) {
      if (s.indexOf(MARK_ID) >= 0) return null;
      k++;
      continue;
    }
    k = @PKG@.CfgFile.end(l, k) + 1;
  }
  boolean addFrom = p.getProperty(FROM_KEY) == null;
  boolean addCurve = !hasCurve(p);
  boolean addPer = p.getProperty(PER_KEY) == null;
  boolean addFl = p.getProperty(FL_KEY) == null;
  double bon = bonusOf(p);
  StringBuilder blk = new StringBuilder(HEAD);
  if (addFrom) blk.append(FROM_TXT);
  if (addCurve) blk.append(CURVE_HEAD).append(curveLines(bon));
  if (addPer || addFl) {
    blk.append(MANA_HEAD);
    if (addPer) blk.append(PER_KEY).append('=').append(PER_DEF).append('\n');
    if (addFl) blk.append(FL_KEY).append('=').append(FL_DEF).append('\n');
  }
  String body = text;
  boolean crlf = text.indexOf("\r\n") >= 0;
  String nl = crlf ? "\r\n" : "\n";
  String b = blk.toString();
  if (crlf) b = b.replace("\n", "\r\n");
  String pre = (body.length() == 0 || body.endsWith("\n")) ? nl : nl + nl;
  String last = body.endsWith("\n") ? body.substring(0, body.length() - 1) : body;
  if (last.endsWith("\r")) last = last.substring(0, last.length() - 1);
  int bs = 0;
  for (int i = last.length() - 1; i >= 0 && last.charAt(i) == '\\'; i--) bs++;
  if (bs % 2 == 1 && body.endsWith("\n")) pre = pre + nl;
  java.util.ArrayList rows = new java.util.ArrayList();
  if (addFrom) { rows.add(FROM_KEY); rows.add("health"); rows.add("level"); }
  return new Object[] { body + pre + b, (String[]) rows.toArray(new String[0]), Boolean.valueOf(addFrom), Boolean.valueOf(addCurve),
                        Boolean.valueOf(addPer), Boolean.valueOf(addFl), Double.valueOf(bon) };
}"""), kxm))
# only the planned keys may be new, every old key keeps its value, every new key holds exactly the planned value
kxm.addMethod(CtNewMethod.make(J14(r"""
public static boolean sameAfter(byte[] old, byte[] nb, boolean addFrom, boolean addCurve, boolean addPer, boolean addFl, double bon) {
  try {
    java.util.Properties a = new java.util.Properties();
    java.util.Properties n = new java.util.Properties();
    a.load(new java.io.ByteArrayInputStream(old));
    n.load(new java.io.ByteArrayInputStream(nb));
    int add = (addFrom ? 1 : 0) + (addCurve ? LEVELS.length : 0) + (addPer ? 1 : 0) + (addFl ? 1 : 0);
    if (n.size() != a.size() + add) return false;
    java.util.Iterator it = a.stringPropertyNames().iterator();
    while (it.hasNext()) {
      String k = (String) it.next();
      String got = n.getProperty(k);
      if (got == null || !got.equals(a.getProperty(k))) return false;
    }
    if (addFrom && (a.getProperty(FROM_KEY) != null || !"level".equals(n.getProperty(FROM_KEY)))) return false;
    if (addPer && (a.getProperty(PER_KEY) != null || !PER_DEF.equals(n.getProperty(PER_KEY)))) return false;
    if (addFl && (a.getProperty(FL_KEY) != null || !FL_DEF.equals(n.getProperty(FL_KEY)))) return false;
    if (addCurve) for (int i = 0; i < LEVELS.length; i++) {
      String ck = @PKG@.MobXp.CURVE_PREFIX + LEVELS[i];
      if (a.getProperty(ck) != null || !factorText(LEVELS[i], bon).equals(n.getProperty(ck))) return false;
    }
    return true;
  } catch (Throwable t) { return false; }
}"""), kxm))
kxm.addMethod(CtNewMethod.make(J14(r"""
public static String logLine(String k, String o, String n) {
  return @PKG@.CfgLog.now() + "\t" + WHO + "\t-\tupdate\t" + @PKG@.CfgRows.oneLine(k) + "\t" + o + "\t" + n + "\tok";
}"""), kxm))
kxm.addMethod(CtNewMethod.make(J14(r"""
public static synchronized String run() {
  java.nio.file.Path f = @PKG@.SkillCfg.FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = plan(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    boolean addFrom = ((Boolean) r[2]).booleanValue();
    boolean addCurve = ((Boolean) r[3]).booleanValue();
    boolean addPer = ((Boolean) r[4]).booleanValue();
    boolean addFl = ((Boolean) r[5]).booleanValue();
    double bon = ((Double) r[6]).doubleValue();
    if (!sameAfter(old, data, addFrom, addCurve, addPer, addFl, bon)) {
      @PKG@.SkillCfg.warn("xp.properties NOT updated for 0.4.17 (kill XP by level): the update would change another setting (the file is used as it is; the next start tries again)");
      return "";
    }
    int fi = @PKG@.HealMig.fileIdx();
    if (fi < 0) return "";
    @PKG@.HealMig.mgKit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(fi, old, @PKG@.CfgHist.stamp(), WHO, "before the 0.4.17 kill XP by level update");
    if (!@PKG@.HealMig.mgSaved(fi, old)) {
      @PKG@.SkillCfg.warn("xp.properties NOT updated for 0.4.17 (kill XP by level): the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] rows = (String[]) r[1];
    for (int i = 0; i + 2 < rows.length; i += 3) @PKG@.CfgLog.enqueue(logLine(rows[i], rows[i + 1], rows[i + 2]));
    if (rows.length > 0) @PKG@.CfgLog.flush();
    StringBuilder what = new StringBuilder();
    if (addFrom) what.append("combat.xpFrom=level (kills pay from the mob's Lv 1 health x the level curve with SkyyMobs 0.1.4+; Server Setup -> Changes -> Undo = the 0.4.16 kill XP)");
    if (addCurve) { if (what.length() > 0) what.append("; "); what.append("the kill XP level curve (" + LEVELS.length + " points from level bonus " + @PKG@.DivCfg.num(bon) + ": Lv 20 x" + factorText(20, bon) + ", Lv 40 x" + factorText(40, bon) + ")"); }
    if (addPer || addFl) { if (what.length() > 0) what.append("; "); what.append("Mana regen per class level (" + (addPer ? PER_KEY + "=" + PER_DEF : "") + (addPer && addFl ? ", " : "") + (addFl ? FL_KEY + "=" + FL_DEF : "") + ")"); }
    if (what.length() == 0) what.append("no setting added (every line was already there) - 0.4.17 marker added");
    String msg = "xp.properties updated for 0.4.17: added " + what.toString() + " - nothing else changed; the old file is in config-history";
    @PKG@.SkillCfg.info(msg);
    return msg;
  } catch (Throwable t) {
    @PKG@.SkillCfg.warn("could not update xp.properties for 0.4.17 (kill XP by level; the file is used as it is): " + t);
    return "";
  }
}"""), kxm))

'''
before("# ---- ManaGuard (point 3): WARN once per class whose base Mana is below the Mana cost of a weapon in its class kit. Scheduler thread\n", KXMIG)

# ---------------------------------------------------------------------------------------------------------------- config rows
rep('''    ("combat.perHealth", "Combat XP per max health", "combat", "dec", "0.2", "0", "1000", "", "", "live",
     "Class XP per NPC kill = its max health x this, kept between the minimum and maximum below.", "reload"),''',
    '''    ("combat.perHealth", "Combat XP per max health", "combat", "dec", "0.2", "0", "1000", "", "", "live",
     "XP per Lv 1 health (Mob level mode) or per max health (Mob health mode), kept between min and max.", "reload"),''')
rep('''    ("combat.levelBonus", "Kill XP per mob level", "combat", "dec", "0.05", "0", "10", "", "", "live",
     "Kill XP x (1 + this x (mob level - 1)) with SkyyMobs levels. 0.05 = +5% a level.", "reload"),''',
    '''    ("combat.levelBonus", "Health mode: XP per mob level", "combat", "dec", "0.05", "0", "10", "", "", "live",
     "Mob health mode only: kill XP x (1 + this x (mob level - 1)). 0.05 = +5% a level.", "reload"),''')
rep('''     "Off: kills pay no mob level bonus or level gap (needs SkyyMobs levels). Levels are kept.", "reload"),''',
    '''     "Mob level mode: the level gap XP rows. Mob health mode: the level bonus + the gap rows.", "reload"),''')
rep('''    ("combat.gap.min", "Lower mob: least XP", "combat", "dec", "0.1", "0", "1", "", "x", "live",
     "The gap never pays less than this share (0.1 = 10%).", "reload"),
''', '''    ("combat.gap.min", "Lower mob: least XP", "combat", "dec", "0.1", "0", "1", "", "x", "live",
     "The gap never pays less than this share (0.1 = 10%).", "reload"),
    # 0.4.17 (Mob-Curve-Spec 4.2 / 6.3): kill XP from the mob level (SkyyMobs mob:fn:info) or from its health (0.4.16), + the level curve table
    ("combat.xpFrom", "Kill XP comes from", "combat", "choice", "level", "", "", "level|Mob level,health|Mob health", "", "live",
     "Mob level = Lv 1 health x the level curve x the difficulty share. Mob health = 0.4.16.", "reload"),
    ("combat.levelCurve", "Kill XP level curve", "combat", "table", "", "0.1", "1000", "dec;none;Factor", "", "live",
     "Kill XP x this at each mob level (entry = level; straight lines between). Default = old Hard XP.", "reload;check=MobXp.checkCurvePoint"),
''')
rep('''     "Mana refill for 6 s after you take damage, as % of the normal refill + boosts. 0 = vanilla (none).", "reload"),
''', '''     "Mana refill for 6 s after you take damage, as % of the normal refill + boosts. 0 = vanilla (none).", "reload"),
    # 0.4.17 (Mob-Curve-Spec 2.4): Mana regen + this % per class level above the start level (7 / 20: class 30 = +70 %)
    ("mana.regen.perLevel", "Mana regen per class level", "overall", "dec", KXP_PER_DEF, "0", "100", "", "%", "live",
     "Mana regen +this % of the vanilla refill per class level above the start level below.", "reload"),
    ("mana.regen.fromLevel", "Mana regen growth starts at", "overall", "int", KXP_FROM_DEF, "0", "100", "", "", "live",
     "The class level after which the Mana regen growth starts (21 = the first step).", "reload"),
''')
rep('''                 ("levels.skill", "levels.skill.")):   # 0.4.16: + the own level lists''',
    '''                 ("levels.skill", "levels.skill."), ("combat.levelCurve", "combat.levelCurve.")):   # 0.4.16: + the own level lists; 0.4.17: + the kill XP level curve''')
rep('''assert len(CFG_ROWS) == 197, (''', '''assert len(CFG_ROWS) == 201, (''')
rep('''"mana.classPerLevel table; 0.4.16: + the levels.skill table, got %d" % len(CFG_ROWS))''',
    '''"mana.classPerLevel table; 0.4.16: + the levels.skill table; 0.4.17: + combat.xpFrom, the combat.levelCurve table, mana.regen.perLevel / "
                              "fromLevel, got %d" % len(CFG_ROWS))''')
rep('''assert DEFAULTS.endswith("\\n" + SKL_DEFAULTS)
''', '''assert DEFAULTS.endswith("\\n" + SKL_DEFAULTS + "\\n" + KXP_DEFAULTS)   # 0.4.17: the KXP block follows the 0.4.16 block
# 0.4.17: the new rows once each, row default = file default = KXP block; the curve table's default entries = the KXP block's; places
_k17 = [_r[0] for _r in CFG_ROWS]
for _k in ("combat.xpFrom", "mana.regen.perLevel", "mana.regen.fromLevel"):
    _rw = [_r for _r in CFG_ROWS if _r[0] == _k]
    assert len(_rw) == 1 and _dp.get(_k) == _rw[0][4] and ("\\n" + _k + "=" + _rw[0][4] + "\\n") in ("\\n" + KXP_DEFAULTS), _k
assert sorted(_k for _k in _dp if _k.startswith("combat.levelCurve.")) == sorted("combat.levelCurve.%d" % _L for _L in KXP_LEVELS)
assert all(_dp["combat.levelCurve.%d" % _L] == _v for _L, _v in KXP_DEF)
assert _k17[_k17.index("combat.gap.min") + 1:_k17.index("combat.gap.min") + 3] == ["combat.xpFrom", "combat.levelCurve"]
assert _k17[_k17.index("mana.regen.inCombat") + 1:_k17.index("mana.regen.inCombat") + 4] == ["mana.regen.perLevel", "mana.regen.fromLevel", "mana.regen.show"]
assert _k17.count("combat.levelCurve") == 1 and not any(_k.startswith("combat.levelCurve") for _k in _k17 if _k != "combat.levelCurve")
''')

# ---------------------------------------------------------------------------------------------------------------- build fix
# tools/deploy_set.py's PACK_THIRD_PARTY list now spans two lines and holds "NoCube:[NoCube's] Orchard" (2026-10-06): the single-line regex
# found nothing and stopped the build. Read the list as a Python literal instead (the first "]" that closes a valid list).
rep('''_packs = _sre.findall(r'"([^"]+:[^"]+)"', _sre.search(r"PACK_THIRD_PARTY = \\[(.*?)\\]", _dst).group(1))
''', '''import ast as _ast17   # 0.4.17 build fix: the list spans lines and an entry holds "]" ("NoCube:[NoCube's] Orchard")
_pt17 = _dst[_dst.index("PACK_THIRD_PARTY = [") + len("PACK_THIRD_PARTY = "):]
_packs = None
for _e17 in range(1, min(len(_pt17), 8000)):
    if _pt17[_e17] != "]":
        continue
    try:
        _packs = _ast17.literal_eval(_pt17[:_e17 + 1])
        break
    except (SyntaxError, ValueError):
        continue
assert isinstance(_packs, list) and all(isinstance(_x, str) and ":" in _x for _x in _packs), "PACK_THIRD_PARTY not readable: %r" % (_packs,)
''')

# ---------------------------------------------------------------------------------------------------------------- classes + plugin
rep('''slm  = pool.makeClass(PKG + ".SkillLvMig")
''', '''slm  = pool.makeClass(PKG + ".SkillLvMig")
# 0.4.17: the one-time config update for kill XP by level + Mana regen per class level (KillXpMig)
kxm  = pool.makeClass(PKG + ".KillXpMig")
''')
rep('''          slv, own, slm):   # 0.4.16: + SkillLv, OwnCurve, SkillLvMig;''', '''          slv, own, slm,
          kxm):   # 0.4.17: + KillXpMig; 0.4.16: + SkillLv, OwnCurve, SkillLvMig;''')
after("  {PKG}.SkillLvMig.run();     // 0.4.16: Mining's own level list + Mining out of the gathering pace into an existing xp.properties, once; History first\n",
      "  {PKG}.KillXpMig.run();      // 0.4.17: kill XP by level + Mana regen per class level lines into an existing xp.properties, once; History first\n")
rep('''"; in-combat Mana regen " + {PKG}.ManaRegen.IN_COMBAT + "% of (vanilla + Mana Regen boosts)" + "; kill XP by mob level " + {PKG}.MobXp.text()''',
    '''"; in-combat Mana regen " + {PKG}.ManaRegen.IN_COMBAT + "% of (vanilla + Mana Regen boosts)" + "; Mana regen +" + {PKG}.DivCfg.num({PKG}.ManaRegen.PER_LEVEL) + "% per class level above " + {PKG}.ManaRegen.FROM_LEVEL + "; kill XP " + {PKG}.MobXp.text()''')
rep('''Kill XP grows with the SkyyMobs level and the level gap to your class skill (up to +250%; party members use their own class skill);''',
    '''Kill XP grows with the SkyyMobs level and the level gap to your class skill (up to +250%; party members use their own class skill) - with SkyyMobs 0.1.4+ it comes from the mob's Lv 1 health x a level curve (the old Hard XP) x the difficulty's share, so bigger mob health never inflates XP (Server Setup: Kill XP comes from); Mana regen grows +7% per class level above 20;''')

# ---------------------------------------------------------------------------------------------------------------- checks + write
for k in KEEP:
    assert s.count(k) == 1, "a block that must stay byte-identical changed: " + k[:100]
assert s.count("registerSystem(") == REG0 and s.count("registerCommand(") == CMD0, "systems / commands: 0.4.17 adds none"
assert [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln] == BIND0, "event bindings changed"
_ix = lambda t: s.index(t)
# methods before callers (javassist compiles each method body when it is added)
assert _ix("public static double eval(Object[] p, double x) {\n  if (p == null) return 1.0;") < _ix("public static double curve(int L) {")
assert _ix("public static double curve(int L) {") < _ix("public static void readCurve(java.util.Properties p)") < _ix("  readCurve(p);\n}")
assert _ix("public static Object[] parseCurve(java.util.Properties p)") < _ix("public static void readCurve(java.util.Properties p)")
assert _ix("public static String checkCurvePoint(String key, String value)") < _ix("  readCurve(p);\n}") < _ix('''  if (LEVEL) return "from the mob level''')
assert _ix("public static int curveLevel(String e)") < _ix("public static Object[] parseCurve(") and _ix("public static double curveFactor(String v)") < _ix("public static Object[] parseCurve(")
assert _ix("public static double classPct(java.util.UUID u)") < _ix("double sum = classPct(u);") < _ix("double cp = classPct(u);")
assert _ix("public static long combatXp2(String role, float maxHp, double lv1)") < _ix("public static long combatXp(String role, float maxHp) {\n  return combatXp2(")
assert _ix("public static long payD(int slot, double base, double factor)") < _ix("b = {PKG}.MobXp.payD(ks, lvb,") < _ix("public static long kill2(")
assert _ix("public static double[] infoOf(@ST@ s, @REF@ r)") < _ix("public static long kill2(") and _ix("public static double lvBase(") < _ix("public static long kill2(")
assert _ix("public static boolean infoFn()") < _ix("public static long kill2(")
assert _ix("public static long one3(") < _ix("public static long one2(") < _ix("public static void share3(") < _ix("public static void share2(") < _ix("public static long kill2(")
assert _ix("public static long kill(@PR@ pr, @REF@ k, @ST@ s, int slot, long base, @REF@ npc)") < _ix("public static long kill2(") < _ix("{PKG}.MobXp.kill2(pr, k, s, slot, role, maxHp, r);")
assert _ix("public static String fmt(double f)") < _ix("public static String factorText(int L, double b)") < _ix("public static String curveLines(double b)") < _ix("public static Object[] plan(String text) {\n  if (text == null) return null;\n  java.util.Properties p = new java.util.Properties();\n  try { p.load(new java.io.StringReader(text)); } catch (Throwable t) { return null; }\n  String[] raw = text.split(\"\\n\", -1);\n  java.util.ArrayList l = new java.util.ArrayList();\n  for (int i = 0; i < raw.length; i++) {\n    String s0 = raw[i];\n    if (s0.endsWith(\"\\r\")) s0 = s0.substring(0, s0.length() - 1);\n    l.add(s0);\n  }\n  int k = 0;")
assert _ix("public static double bonusOf(java.util.Properties p)") < _ix("public static boolean sameAfter(byte[] old, byte[] nb, boolean addFrom")
assert s.index("{PKG}.SkillLvMig.run();") < s.index("{PKG}.KillXpMig.run();") < s.index("String rules = {PKG}.SkillCfg.load();")
assert s.index('kxm  = pool.makeClass(PKG + ".KillXpMig")') < s.index("kxm.addField(")
assert s.count("{PKG}.MobXp.kill(pr, k, s, slot,") == 0 and s.count("MobXp.kill2(") == 1
_a, _b = S0.split(LF), s.split(LF)
_hunks = [op for op in difflib.SequenceMatcher(None, _a, _b, autojunk=False).get_opcodes() if op[0] != "equal"]
_gone = [(i, _a[i]) for op in _hunks for i in range(op[1], op[2])]
_allowed = set()
for _o in OLDS:
    _allowed.update(_o.split(LF))
_bad = [(i, ln) for i, ln in _gone if ln not in _allowed]
assert not _bad, "0.4.16 lines changed outside the planned places: %r" % _bad[:5]
open(dst, "wb").write(s.replace(LF, NL).encode("utf8"))
print("wrote", dst, len(s), "chars;", len(_hunks), "diff hunks vs 0.4.16,", len(_gone), "0.4.16 lines replaced,",
      sum(op[4] - op[3] for op in _hunks) - len(_gone), "lines added net;", len(OLDS), "anchors")
