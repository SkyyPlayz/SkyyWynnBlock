"""Derive SkyySkills/build_skyyskills_0.4.59.py from the GENERATED SkyySkills 0.4.58 (build_skyyskills_0.4.58.py = the tools/deploy_set.py SET
pin, made by tools/skills_0_4_58_patch.py). Every anchor is asserted once; at the end every change is undone on a copy and compared with
0.4.58 (tools/soundpass_gen.Patch). Line endings kept. Edit THIS file, never the generated script.
Run:  python tools/skills_0_4_59_patch.py   then   python SkyySkills/build_skyyskills_0.4.59.py   (never --deploy)
      then  python SkyySkills/test_skyyskills_0.4.59.py
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G
import balance_rebirth as BR

P8_OLD = "1.2,1.45,1.8,2.25,2.8"                                  # SkyySkills 0.4.57 / 0.4.58 rebirth.pastLifeXp
P8_PAST = "1.1,1.35,1.6,2,2.45,2.15,2.25,2.4,2.55,2.7"            # research/Balance-P8-Rebirth-Spec.md 2.3
assert [float(x) for x in P8_PAST.split(",")] == BR.PAST_LIFE_P8 and [float(x) for x in P8_OLD.split(",")] == BR.PAST_LIFE_LIVE, "balance_rebirth"

NOTE = '''0.4.59 (2026-10-21) = BALANCE PASS P8a, the SkyySkills part (research/Balance-P8-Rebirth-Spec.md Part 2 + 5.1-5.4, round P8a; FULL round
  with SkyyRebirth 0.4.2 - pin and roll back TOGETHER). Skyy (2026-10-21): "keep going down the list. dont stop until the entire list is
  done" + "just go with the recommended on all of them. i need to go to bed." (every spec question takes its [bracketed] default) + the goals
  "first rebirth after like 40-50 hours ... then each rebirth after that gets a little shorter" / "15% shorter each (Rec.)" / keep "Flat +0.25%
  each" (no cap) / "allow rebirths past 5 so you can keep upgrading. but leave the lvl cap at 100".
  1. PAST-LIFE BOOST rebirth.pastLifeXp 1.2,1.45,1.8,2.25,2.8 -> 1.1,1.35,1.6,2,2.45,2.15,2.25,2.4,2.55,2.7 (entry n = rebirth n, past the
     end = the last; the ONE pacing knob - spec 2.3; tools/balance_rebirth.py --check: the greedy player's class runs 0.98-1.01 of "15 %
     shorter each" for rebirths 1-10). The constant P3_PAST itself moves, so a file P3Mig has not updated yet (the live world) gets the new
     list straight away; the code default (no line) is the new list.
  2. THE CLASS XP CLAMP: RbStat.fetch's class XP part (rebirth:fn:stat "classxp" = Insight + keep + Class Echo) clamps at the new
     CLASSXP_MAX +500 % (= SkillBonus' limit) instead of MAXPCT +200 % - the hidden cap that froze class runs from rebirth 9 (Skyy: keep has no
     cap). MAXPCT stays 200 for the Health / Mana / Stamina % stats; Combat Echo keeps 200.
  3. FASTEST-REBIRTH CEILING (new Server Setup row Skills -> Levels "Fastest rebirth: most rebirth XP", rebirth.xpMultMax, dec 0-100,
     0 = OFF = the default): when > 0, SkillBonus.xpBonus cuts the REBIRTH part rb (skill:bonus source "rebirth" for that skill + the class
     RbStat part) so that past-life x (1 + rb) <= the ceiling (rb' = ceiling / past-life - 1, never below 0); the tree / pet part is never
     cut; 0 / negative / NaN = no cut (and the code path is the 0.4.58 one). 9.3 = runs stop shrinking at rebirth 10 (row help).
     (xpBonus is compiled before P3Xp.pastLife exists, so its body is set afterwards to P3Xp.bonusP8 - the 0.4.53 Farm3.lvIn pattern.)
  4. THE STATS LINE (spec 2.5): "Past-life XP x2.45 below level 90" -> ONE combined line "Rebirth XP x4.9: past-life x2.45 below Lv 90,
     Void x2" (Void = 1 + the rebirth part after the ceiling); at the ceiling + ", at the server's fastest rebirth".
  5. ONE-TIME UPDATE PlMigP8 (PROJECT-RULES 4; P4Mig's reviewed machinery, copied): ONCE on an existing xp.properties, setup() right after
     P4Mig, BEFORE SkillCfg.load. rebirth.pastLifeXp whose LAST entry is a one-line entry holding exactly 1.2,1.45,1.8,2.25,2.8 -> the P8
     list (value text only); any other value kept (one INFO line); no line = nothing written (the new code default applies). Then ONE block
     in the file's own line ending: the comment + rebirth.xpMultMax=0 (if absent) + the run-once marker "Balance P8 rebirth (SkyySkills
     0.4.59)". config-history copy first (verified), one config-changes.log row per change (Undo), a Properties check (only the planned keys
     differ), atomicWrite. A fresh file carries the marker.
  6. Fix round 2: the past-life row's error message gives the P8 list as its example (was the old 0.4.57 list).
  SAVED DATA: none (player files untouched). New class PlMigP8; no new command or system.
  ROLLBACK to 0.4.58: only TOGETHER with SkyyRebirth 0.4.1; Undo the PlMigP8 row in Server Setup -> Changes first (0.4.58 keeps whatever list
  the file holds; the P8 list there = 0.4.58 with the P8 pace, harmless; rebirth.xpMultMax is ignored).
'''

P = G.Patch(os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.58.py"), os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.59.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.4.58"') and P.has("P4Mig") and not P.has("PlMigP8"), "not the generated SkyySkills 0.4.58 script"
REG0, SYS0 = P.s.count("registerCommand("), P.s.count("registerSystem(")

P.rep('''"""SkyySkills 0.4.58 - build script (derived from the generated 0.4.57 by tools/skills_0_4_58_patch.py - edit the patch, not this file;
0.4.58 (2026-10-20) = BALANCE PASS P4''', '''"""SkyySkills 0.4.59 - build script (derived from the generated 0.4.58 by tools/skills_0_4_59_patch.py - edit the patch, not this file;
''' + NOTE + '''0.4.58 was derived from the generated 0.4.57 by tools/skills_0_4_58_patch.py;
0.4.58 (2026-10-20) = BALANCE PASS P4''')
P.rep('VERSION = "0.4.58"', 'VERSION = "0.4.59"')

# ================================================================================================================ 1. the past-life list
P.rep('''P3_PAST = "1.2,1.45,1.8,2.25,2.8"''', '''P8_OLD = "%s"   # 0.4.59 Balance P8: the 0.4.57 / 0.4.58 list (PlMigP8 rewrites exactly this)
P8_PAST = "%s"   # 0.4.59 (research/Balance-P8-Rebirth-Spec.md 2.3; tools/balance_rebirth.py PAST_LIFE_P8)
P3_PAST = P8_PAST   # 0.4.59: was P8_OLD - P3Mig (a file not yet updated for P3) appends the P8 list straight away''' % (P8_OLD, P8_PAST))
P.rep('''"public static volatile double[] PAST = new double[] { 1.2, 1.45, 1.8, 2.25, 2.8 };",''',
      '''"public static volatile double[] PAST = new double[] { %s };" % ", ".join(repr(float(_x)) for _x in P8_PAST.split(",")),   # 0.4.59 Balance P8
             "public static volatile double XP_MULT_MAX = 0.0;",   # 0.4.59 rebirth.xpMultMax (0 = off)''')
P.rep('''  PAST = pv;
  PAST_TEXT = pl.trim();''', '''  PAST = pv;
  PAST_TEXT = pl.trim();
  XP_MULT_MAX = clamp(@PKG@.SkillCfg.dbl(p, "rebirth.xpMultMax", 0.0), 0.0, 100.0, 0.0);   // 0.4.59 Balance P8: the fastest-rebirth ceiling (0 = off)''')

# ================================================================================================================ 2. the class XP clamp 200 -> 500
P.rep('''             'public static final String KS = "skyyskill_rebirthstamina";', "public static final double MAXPCT = 200.0;"):''',
      '''             'public static final String KS = "skyyskill_rebirthstamina";', "public static final double MAXPCT = 200.0;",
             "public static final double CLASSXP_MAX = 500.0;"):   # 0.4.59 Balance P8: the class XP part's own limit (= SkillBonus' +500 %)''')
P.rep('''public static double clampPct(double v) {
  if (Double.isNaN(v) || Double.isInfinite(v) || !(v > 0.0)) return 0.0;
  return v > MAXPCT ? MAXPCT : v;
}"""), rbs39))''', '''public static double clampPct(double v) {
  if (Double.isNaN(v) || Double.isInfinite(v) || !(v > 0.0)) return 0.0;
  return v > MAXPCT ? MAXPCT : v;
}"""), rbs39))
# 0.4.59 Balance P8 (spec 2.2): the class XP rebirth part (Insight + keep + Class Echo) up to +500 % - Skyy "keep ... no cap" (MAXPCT stays 200 for the stats)
rbs39.addMethod(CtNewMethod.make(J14(r"""
public static double clampClass(double v) {
  if (Double.isNaN(v) || Double.isInfinite(v) || !(v > 0.0)) return 0.0;
  return v > CLASSXP_MAX ? CLASSXP_MAX : v;
}"""), rbs39))''')
P.rep('''    z[3] = clampPct(cx);''', '''    z[3] = clampClass(cx);   // 0.4.59 Balance P8: +500 % (was clampPct = +200 %)''')

# ================================================================================================================ 3 + 4. the ceiling + the Stats line
P.rep('''    double p = pastLife(u, s);
    if (p > 1.0 && out.size() < max) {
      String k = @PKG@.SkillStore.pkey(u);
      out.add("Past-life XP x" + @PKG@.DivCfg.num(p) + " below level " + prevCap(k, s, rebirths(k)));
    }''', '''    String rl = rbLine(u, s);   // 0.4.59 Balance P8: the combined rebirth XP line (was "Past-life XP x.. below level ..")
    if (rl != null && out.size() < max) out.add(rl);''')
P8XP = r'''# ================= 0.4.59 BALANCE P8 (research/Balance-P8-Rebirth-Spec.md 2.5): the fastest-rebirth ceiling + the combined Stats line =================
# cutRb = the rebirth part rb (a fraction) so that past-life x (1 + rb) <= ceil (ceil <= 0 / NaN = off: rb unchanged; never below 0)
p3x.addMethod(CtNewMethod.make(J14(r"""
public static double cutRb(double rb, double past, double ceil) {
  if (Double.isNaN(rb) || Double.isInfinite(rb) || !(rb > 0.0)) return 0.0;
  if (Double.isNaN(ceil) || Double.isInfinite(ceil) || !(ceil > 0.0)) return rb;
  double p = (Double.isNaN(past) || !(past > 1.0)) ? 1.0 : past;
  double m = ceil / p - 1.0;
  if (!(m > 0.0)) return 0.0;
  return rb < m ? rb : m;
}"""), p3x))
# the rebirth source of one slot's XP bonus: SkyyRebirth's skill:bonus "rebirth" xp.<skill> (+ the class part RbStat.classXp on a class slot)
p3x.addMethod(CtNewMethod.make(J14(r"""
public static double rbSrc(java.util.UUID u, int s) {
  if (u == null || s < 0 || s >= @PKG@.SkillDefs.N || !@PKG@.SkillDefs.boostable(s)) return 0.0;
  boolean cls = @PKG@.SkillDefs.isClass(s);
  boolean[] on = @PKG@.BridgeCfg.BONUS_XP;
  boolean lst = s < on.length && on[s];
  return (lst || !cls) ? @PKG@.SkillBonus.srcVal(u, "rebirth", "xp." + @PKG@.SkillBonus.key(s)) : 0.0;
}"""), p3x))
p3x.addMethod(CtNewMethod.make(J14(r"""
public static double rbRaw(java.util.UUID u, int s) {
  if (u == null || s < 0 || s >= @PKG@.SkillDefs.N || !@PKG@.SkillDefs.boostable(s)) return 0.0;
  double r = rbSrc(u, s) + (@PKG@.SkillDefs.isClass(s) ? @PKG@.RbStat.classXp(u) : 0.0);
  return (Double.isNaN(r) || Double.isInfinite(r) || !(r > 0.0)) ? 0.0 : r;
}"""), p3x))
# SkillBonus.xpBonus from 0.4.59: the 0.4.58 sum (bridge.bonus.xpSkills sources + the class part + the Combat tree), the rebirth part cut
# by the ceiling only while rebirth.xpMultMax > 0 (off = exactly the 0.4.58 arithmetic)
p3x.addMethod(CtNewMethod.make(J14(r"""
public static double bonusP8(java.util.UUID u, int slot) {
  if (slot < 0 || slot >= @PKG@.SkillDefs.N) return 0.0;
  if (!@PKG@.SkillDefs.boostable(slot)) return 0.0;
  boolean cls = @PKG@.SkillDefs.isClass(slot);
  double rb = cls ? @PKG@.RbStat.classXp(u) : 0.0;
  boolean[] on = @PKG@.BridgeCfg.BONUS_XP;
  String key = "xp." + @PKG@.SkillBonus.key(slot);
  double s = (slot < on.length && on[slot]) ? @PKG@.SkillBonus.sum(u, key) : (cls ? 0.0 : @PKG@.SkillBonus.srcVal(u, "rebirth", key));
  double c = XP_MULT_MAX;
  if (c > 0.0) {
    double rs = rbSrc(u, slot);
    double cut = cutRb(rs + rb, pastLife(u, slot), c);
    s = s - rs + cut;
    rb = 0.0;
  }
  s = s + rb;
  if (cls) s = s + @PKG@.SkillV3.classXp(u);
  if (Double.isNaN(s) || s <= 0.0) return 0.0;
  return s > 5.0 ? 5.0 : s;
}"""), p3x))
sbn.getDeclaredMethod("xpBonus").setBody(J14(r"""{
  return @PKG@.P3Xp.bonusP8($1, $2);   // 0.4.59 Balance P8: + the fastest-rebirth ceiling (P3Xp.pastLife is compiled after SkillBonus)
}"""))
# the Stats line: "Rebirth XP x4.9: past-life x2.45 below Lv 90, Void x2" (+ ", at the server's fastest rebirth"); null = no rebirth boost
p3x.addMethod(CtNewMethod.make(J14(r"""
public static String rbLine(java.util.UUID u, int s) {
  if (u == null || s < 0 || s >= @PKG@.SkillDefs.N || !@PKG@.SkillDefs.boostable(s)) return null;
  double p = pastLife(u, s);
  double raw = rbRaw(u, s);
  double rb = cutRb(raw, p, XP_MULT_MAX);
  if (!(p > 1.0) && !(rb > 0.0)) return null;
  double tot = p * (1.0 + rb);
  StringBuilder b = new StringBuilder("Rebirth XP x").append(@PKG@.DivCfg.num(Math.round(tot * 10.0) / 10.0)).append(':');
  if (p > 1.0) {
    String k = @PKG@.SkillStore.pkey(u);
    b.append(" past-life x").append(@PKG@.DivCfg.num(p)).append(" below Lv ").append(prevCap(k, s, rebirths(k)));
  }
  if (rb > 0.0) b.append(p > 1.0 ? "," : "").append(" Void x").append(@PKG@.DivCfg.num(Math.round((1.0 + rb) * 100.0) / 100.0));
  if (XP_MULT_MAX > 0.0 && rb < raw - 1.0E-9) b.append(", at the server's fastest rebirth");
  return b.toString();
}"""), p3x))
'''
P.rep('''p3x.addMethod(CtNewMethod.make(J14(r"""
public static double levelF(java.util.UUID u, int s) {''', P8XP + '''p3x.addMethod(CtNewMethod.make(J14(r"""
public static double levelF(java.util.UUID u, int s) {''')

# ================================================================================================================ the Server Setup row
P.rep('''     "An extra XP multiplier for one skill (Class = every class skill). No line = x1.", "reload;check=P3Xp.checkMult"),''',
      '''     "An extra XP multiplier for one skill (Class = every class skill). No line = x1.", "reload;check=P3Xp.checkMult"),
    # 0.4.59 (Balance P8 2.5, Skyy 2026-10-21 "just go with the recommended": OFF by default - the keep buff has no cap)
    ("rebirth.xpMultMax", "Fastest rebirth: most rebirth XP", "levels", "dec", "0", "0", "100", "", "x", "live",
     "Most past-life x Void XP (0 = off; tree XP never cut). 9.3 = runs stop shrinking at rebirth 10.", "reload"),''')
P.rep('''assert len(CFG_ROWS) == 285 + len(P4_ROWS_POWER) + len(P4_ROWS_MANA) + len(P4_ROWS_MOVE), ("0.4.58:''',
      '''assert len(CFG_ROWS) == 285 + len(P4_ROWS_POWER) + len(P4_ROWS_MANA) + len(P4_ROWS_MOVE) + 1, ("0.4.59: + rebirth.xpMultMax; 0.4.58:''')

# ================================================================================================================ 5. the fresh default file + PlMigP8
P8DATA = r'''# ================= 0.4.59 BALANCE P8 - the PlMigP8 plan and the fresh default file (tools/skills_0_4_59_patch.py) =================
P8_KEYS = [("rebirth.pastLifeXp", P8_OLD, P8_PAST, "rebirth.pastLifeXp")]          # (key, 0.4.58 default, 0.4.59 default, change-log row)
P8_ADD = [("rebirth.xpMultMax", "0", "rebirth.xpMultMax")]
P8_MARK_ID = "Balance P8 rebirth (SkyySkills 0.4.59)"
P8_MARK = "# %s: the past-life XP list for rebirths 1-10 and the fastest-rebirth ceiling (off)" % P8_MARK_ID
P8_HEAD = ["", "# ---------- Balance P8: rebirth pacing (SkyySkills 0.4.59) ----------",
           "# Comments must stay on their own lines. rebirth.pastLifeXp (above) moved to the P8 list: each rebirth about 15 percent shorter.",
           "# rebirth.xpMultMax = the most past-life x Void (rebirth) XP a player gets (0 = off; 9.3 = runs stop shrinking at rebirth 10)."]
for _t in P8_HEAD + [P8_MARK]:
    assert all(32 <= ord(_c) < 127 for _c in _t) and '"' not in _t and "\\" not in _t and (not _t or _t.startswith("# ")), _t
assert "=" not in P8_MARK and not any(_cre.match(r"#\s*[A-Za-z][A-Za-z0-9._-]*\s*[=:]\s*\S+\s*$", _ln) for _ln in P8_HEAD)
P8_BLOCK = "\n".join(P8_HEAD + ["%s=%s" % (_k, _v) for _k, _v, _r in P8_ADD] + [P8_MARK]) + "\n"
DEFAULTS_058 = DEFAULTS   # 0.4.59: the 0.4.58 default file (P3_PAST already = the P8 list there: P3's own block carries it)
assert ("\n" + DEFAULTS_058).count("\nrebirth.pastLifeXp=" + P8_PAST + "\n") == 1 and ("\nrebirth.pastLifeXp=" + P8_OLD) not in DEFAULTS_058
DEFAULTS = DEFAULTS_058 + ("" if DEFAULTS_058.endswith("\n") else "\n") + P8_BLOCK
assert all(ord(ch) < 128 for ch in DEFAULTS) and len(DEFAULTS.encode("utf-8")) < 65000 and DEFAULTS.count(P8_MARK_ID) == 1, len(DEFAULTS)
print("0.4.59: P8 update plan %d key(s), %d line(s) appended; default file %d bytes" % (len(P8_KEYS), len(P8_ADD), len(DEFAULTS)))
'''
P.rep('''DEFAULTS_LIT = json.dumps(DEFAULTS)   # valid Java string literal for ASCII text (\\n \\" \\\\ escapes)''',
      P8DATA + '''DEFAULTS_LIT = json.dumps(DEFAULTS)   # valid Java string literal for ASCII text (\\n \\" \\\\ escapes)''')
P.rep('''assert DEFAULTS.count(P3_MARK_ID) == 1 and DEFAULTS.endswith(P4_BLOCK) and DEFAULTS.count(P4_MARK_ID) == 1   # 0.4.58''',
      '''assert DEFAULTS_058.count(P3_MARK_ID) == 1 and DEFAULTS_058.endswith(P4_BLOCK) and DEFAULTS_058.count(P4_MARK_ID) == 1   # 0.4.58 (0.4.59: the 0.4.58 file)
assert DEFAULTS.count(P3_MARK_ID) == 1 and DEFAULTS.endswith(P8_BLOCK) and DEFAULTS.count(P8_MARK_ID) == 1 and _dp.get("rebirth.pastLifeXp") == P8_PAST and _dp.get("rebirth.xpMultMax") == "0"   # 0.4.59''')

P.rep('''p4m = pool.makeClass(PKG + ".P4Mig")           # 0.4.58: the one-time Balance P4 update of an existing xp.properties''',
      '''p4m = pool.makeClass(PKG + ".P4Mig")           # 0.4.58: the one-time Balance P4 update of an existing xp.properties
plm8 = pool.makeClass(PKG + ".PlMigP8")        # 0.4.59: the one-time Balance P8 update (rebirth.pastLifeXp + rebirth.xpMultMax)''')


def _p4m(name):
    a = P.s.index('p4m.addMethod(CtNewMethod.make(J14(r"""\npublic static ' + name)
    b = P.s.index('"""), p4m))', a)
    return P.s[a + len('p4m.addMethod(CtNewMethod.make(J14(r"""'):b]


_IDX, _OLDH, _PLAN, _SAME, _RUN = (_p4m("int idx("), _p4m("boolean oldHit("), _p4m("Object[] plan("), _p4m("boolean sameAfter("),
                                   _p4m("synchronized String run()"))
_PLAN = _PLAN.replace('''"the 0.4.58 default has no such line" : "the 0.4.58 (Balance P4) default is "''',
                      '''"the 0.4.59 default has no such line" : "the 0.4.59 (Balance P8) default is "''')
assert "0.4.58" not in _PLAN and "P4" not in _PLAN, _PLAN
for _a, _b in (("xp.properties NOT updated for 0.4.58 (Balance P4)", "xp.properties NOT updated for 0.4.59 (Balance P8)"),
               ('"before the 0.4.58 Balance P4 update"', '"before the 0.4.59 Balance P8 update"'),
               ('"xp.properties updated for 0.4.58 (Balance P4: class stats, speed, Stamina, Mana pools, regen + quick refill): "',
                '"xp.properties updated for 0.4.59 (Balance P8: past-life XP list, fastest-rebirth ceiling row): "'),
               ('"could not update xp.properties for 0.4.58 (Balance P4; the file is used as it is): "',
                '"could not update xp.properties for 0.4.59 (Balance P8; the file is used as it is): "')):
    assert _a in _RUN, _a
    _RUN = _RUN.replace(_a, _b)
assert "0.4.58" not in _RUN and "P4" not in _RUN, _RUN
PLM8 = r'''# ---- PlMigP8 (0.4.59, PROJECT-RULES section 4; P4Mig's reviewed machinery, copied): ONCE on an EXISTING xp.properties, setup() right after
# P4Mig, BEFORE SkillCfg.load. rebirth.pastLifeXp whose LAST entry is a one-line entry holding exactly the 0.4.58 default (OLDS) -> NEWS; any
# other value kept (INFO); no line = nothing written. Then ONE block in the file's own line ending: HEAD + rebirth.xpMultMax=0 (if absent)
# + the marker. config-history copy first (verified), one config-changes.log row per change (Undo), Properties check, atomicWrite. A
# failure = WARN, file untouched, retried next start.
plm8.addField(CtField.make("public static final String MARK_ID = %s;" % json.dumps(P8_MARK_ID), plm8))
plm8.addField(CtField.make("public static final String MARK = %s;" % json.dumps(P8_MARK), plm8))
plm8.addField(CtField.make("public static final String HEAD = %s;" % json.dumps("\n".join(P8_HEAD) + "\n"), plm8))
plm8.addField(CtField.make("public static final String[] KEYS = %s;" % jarr([_e[0] for _e in P8_KEYS]), plm8))
plm8.addField(CtField.make("public static final String[] OLDS = %s;" % jarr([_e[1] for _e in P8_KEYS]), plm8))
plm8.addField(CtField.make("public static final String[] NEWS = %s;" % jarr([_e[2] for _e in P8_KEYS]), plm8))
plm8.addField(CtField.make("public static final String[] ROWK = %s;" % jarr([_e[3] for _e in P8_KEYS]), plm8))
plm8.addField(CtField.make("public static final String[] ADDK = %s;" % jarr([_e[0] for _e in P8_ADD]), plm8))
plm8.addField(CtField.make("public static final String[] ADDV = %s;" % jarr([_e[1] for _e in P8_ADD]), plm8))
plm8.addField(CtField.make("public static final String[] ADDR = %s;" % jarr([_e[2] for _e in P8_ADD]), plm8))
plm8.addField(CtField.make('public static final String WHO = "SkyySkills 0.4.59";', plm8))
plm8.addMethod(CtNewMethod.make(J14(r"""''' + _IDX + r'''"""), plm8))
plm8.addMethod(CtNewMethod.make(J14(r"""''' + _OLDH + r'''"""), plm8))
plm8.addMethod(CtNewMethod.make(J14(r"""''' + _PLAN + r'''"""), plm8))
plm8.addMethod(CtNewMethod.make(J14(r"""''' + _SAME + r'''"""), plm8))
plm8.addMethod(CtNewMethod.make(J14(r"""''' + _RUN + r'''"""), plm8))

'''
P.rep('''# ---- CurveP3Mig (0.4.57, spec 6.2, PROJECT-RULES section 4): ONCE, setup() right after Xp56Mig.run, BEFORE P3Mig (which only runs once this''',
      PLM8 + '''# ---- CurveP3Mig (0.4.57, spec 6.2, PROJECT-RULES section 4): ONCE, setup() right after Xp56Mig.run, BEFORE P3Mig (which only runs once this''')
P.rep('''  {PKG}.P4Mig.run();          // 0.4.58 Balance P4: untouched class Mana / Stamina / regen defaults + the new P4 rows, once; History first''',
      '''  {PKG}.P4Mig.run();          // 0.4.58 Balance P4: untouched class Mana / Stamina / regen defaults + the new P4 rows, once; History first
  {PKG}.PlMigP8.run();        // 0.4.59 Balance P8: an untouched past-life XP list -> the P8 list + the fastest-rebirth row, once; History first''')
P.rep("rbcm, snd39, rbs39, pd44, fm48, zo49, fl50, mn52, nc53, fa53, en54, xp56, sv3, p3x, p3m, cp3, cst, p4m, lvf,",
      "rbcm, snd39, rbs39, pd44, fm48, zo49, fl50, mn52, nc53, fa53, en54, xp56, sv3, p3x, p3m, cp3, cst, p4m, plm8, lvf,")
# fix round 2 (critic): the past-life row's error message showed the old 0.4.57 list as its example - an owner copying it got the old pace
P.rep('''rebirth 1 first (1.2,1.45,1.8,2.25,2.8)." : null;''', '''rebirth 1 first (%s)." : null;''' % P8_PAST)
assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0
P.finish()
