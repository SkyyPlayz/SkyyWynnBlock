"""Derive SkyySkills/build_skyyskills_0.4.62.py from the GENERATED SkyySkills 0.4.61 (build_skyyskills_0.4.61.py = the tools/deploy_set.py SET
pin, made by tools/skills_0_4_61_patch.py). Every anchor is asserted once; at the end every change is undone on a copy and compared with
0.4.61 (tools/soundpass_gen.Patch). Line endings kept. Edit THIS file, never the generated script.
Run:  python tools/skills_0_4_62_patch.py   then   python SkyySkills/build_skyyskills_0.4.62.py   (never --deploy)
      then  python SkyySkills/test_skyyskills_0.4.62.py
Balance P9 fixes F1-F4 (research/Balance-P9-Check.md ranked fix list; Skyy's popup answers docs/answered/skills.md 2026-10-22).
"""
import os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G
import balance_model as BM
import balance_rebirth as BR

# ---- the P9 numbers (research/Balance-P9-Check.md fix list = tools/balance_model.py P9_FIX; asserted against the model)
P9_PAST = "1.1,1.52,2.05,3.35,4.92,2.92,3.08,3.25,3.44,3.67"
assert [float(x) for x in P9_PAST.split(",")] == BR.PAST_LIFE_P8 == BM.P9_FIX["F4"]["past"] == BM.PAST_LIFE_LIVE, "balance_rebirth PAST_LIFE_P8"
assert (BM.P9_K4, BM.P9_K5) == (BM.P9_FIX["F4"]["k4"], BM.P9_FIX["F4"]["k5"]) == (1.5, 1.9)
assert BM.P9_FIX["F1"]["beast_x"] == 1.5 and BM.P9_FIX["F2"] == dict(mining_x=1.0, fell_pct=100.0) and BM.P9_FIX["F3"]["catchup_max"] == 0.20
assert BM.P9_BEAST_X[0] == 1.5 and BM.MINING_XP_X == 1.0 and BM.FELL_OTHER_PCT == 100.0 and BM.CATCHUP["max"] == 0.20, "the model's live numbers = 0.4.62"
P9_BASE, P9_LEVELS = list(BM.P9_BASE), list(BM.P9_LEVELS)
assert P9_LEVELS[:60] == BM.P3_LEVELS[:60] and P9_LEVELS[60] == int(BM.P3_BASE[60] * 1.5 * 1.2 + 0.5) and P9_LEVELS[99] == int(BM.P3_BASE[99] * 1.9 * 1.2 + 0.5)
assert round(sum(P9_LEVELS) * 100.0 / sum(P9_BASE)) == 120, "the curve-size row still reads 120 %"

NOTE = '''0.4.62 (2026-10-22) = BALANCE PASS P9 FIXES F1-F4, SkyySkills only (research/Balance-P9-Check.md ranked fix list; FULL round: saved
  data + a one-time migration). Skyy's popup answers (docs/answered/skills.md 2026-10-22): "Apply all 3 (Recommended)" (F1-F3), "Yes, fix it
  (Recommended)" (F4), "~36 h is fine (Recommended)" (F6: no levels.scale change; tools/balance_model.py marks that goal accepted) and
  "Feel-test first (Recommended)" (F5: caster Mana NOT touched) + "work through your whole list."
  1. NEW DEFAULTS (code default = the fresh xp.properties = the Server Setup row default): F1 beast.xpFactor 1 -> 1.5 (Beastmastery reaches
     the run-1 cap with the other skills); F2 mining.xpMultiplier 1.25 -> 1 and fell.otherLogsPercent 70 -> 100 (the 10-15 Mining-vs-Foraging
     leftovers on top of P3's XP); F3 catchup.max 100 -> 20 (%); F4 levels= = the P3 base list x1.5 for Lv 61-80 and x1.9 for Lv 81-100, x
     levels.scale 120 % (SkillDefs.DEFAULT_PER = that base, DEFAULT_RUN = the 120 % list; Lv 1-60 unchanged; tools/balance_model.py P9_BASE /
     P9_LEVELS) + rebirth.pastLifeXp 1.1,1.52,2.05,3.35,4.92,2.92,3.08,3.25,3.44,3.67 (tools/balance_rebirth.py PAST_LIFE_P8, --check 0.98-1.00).
     SkillDefs.DEFAULT_P3 = the 0.4.57 - 0.4.61 list (the old code default both curve moves read).
  2. CurveP9Mig (saved XP, KEEP LEVELS; CurveP3Mig's reviewed machinery, copied): ONCE, setup() right after SkMigP7, BEFORE P9Mig and
     SkillCfg.load, and only once the Balance P3 update of xp.properties has landed (P3Mig.plan = null, no P3PEND; else WARN, nothing, retried
     next start). OLD tables = xp.properties as it is (code default DEFAULT_P3), NEW = the same file after P9Mig.plan (an admin's own list
     stays -> that slot is not moved). History copy of players/ + rebirth/ staged files + level-floors.properties FIRST (read back), level Lo
     + progress kept (newCum(Lo) + round(p x newNeed(Lo))), XP at / past the profile's cap keeps its ratio to the cap total (rebirth:fn:cap);
     a level check per slot (the shown level never moves); .p9tmp + fsync + rename; curve-p9.properties = the run-once marker; one
     curve-p9.log line with the Undo. Levels 1-60 cost the same, so a profile below Lv 60 everywhere is left byte-identical.
  3. P9Mig (xp.properties; BmMigP8c's reviewed machinery, copied, PROJECT-RULES 4): every P9 key whose LAST entry is a one-line entry holding
     exactly the 0.4.61 default -> the 0.4.62 value (value text only); any other value kept (one INFO line); no line = nothing written (the new
     code default applies - the NewBetaTest file has no mining.xpMultiplier / fell.otherLogsPercent line); then ONE comment block + the
     run-once marker "Balance P9 first-run fixes (SkyySkills 0.4.62)" in the file's own line ending. config-history copy first (verified),
     one config-changes.log row per change (Undo), a Properties check, atomicWrite. A fresh file carries the marker.
     SkillCfg.P9PEND (CurveP9Mig.after): the saved XP moved but the file update failed -> this start loads the planned text from memory.
  4. CurveP3Mig (a pre-0.4.57 file) keeps moving to the P3 list: its new-table default is DEFAULT_P3 (was DEFAULT_RUN), and with no
     xp.properties its new tables are the 0.4.61 code defaults (props of "" with DEFAULT_P3 = the 0.4.61 default file's tables) - so a
     pre-P3 world moves 0.4.56 -> P3 -> P9 in one start, never twice.
  5. Fix round 2: SkillCfg.P9STALE (every SkillCfg.load) = the levels in effect are exactly the 0.4.61 list while curve-p9.properties says
     the XP was moved (the levels row Undone alone) -> SkillStore.payLocked pays no level-up coins (markers stay; WARN each load).
  SAVED DATA: player XP totals above Lv 60 move (levels kept); everything else untouched.
  ROLLBACK to 0.4.61: stop the server; copy history/curve-p9/<stamp>/players/* back over players/ (and rebirth/, level-floors.properties if
  there); Server Setup -> Changes -> Undo the P9Mig rows (never the levels row alone); delete curve-p9.properties. 0.4.61 on moved XP with the
  P9 list in the file is harmless (it reads the file's list); on its own P3 list a moved Lv 61-100 total would show a HIGHER level.
'''

P = G.Patch(os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.61.py"), os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.62.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.4.61"') and P.has("SkMigP7") and not P.has("CurveP9Mig"), "not the generated SkyySkills 0.4.61 script"
REG0, SYS0, CLS0 = P.s.count("registerCommand("), P.s.count("registerSystem("), P.s.count("makeClass(")
OLD = P.OLD

P.rep('''"""SkyySkills 0.4.61 - build script (derived from the generated 0.4.60 by tools/skills_0_4_61_patch.py - edit the patch, not this file;
''', '''"""SkyySkills 0.4.62 - build script (derived from the generated 0.4.61 by tools/skills_0_4_62_patch.py - edit the patch, not this file;
''' + NOTE + '''0.4.61 was derived from the generated 0.4.60 by tools/skills_0_4_61_patch.py;
''')
P.rep('VERSION = "0.4.61"', 'VERSION = "0.4.62"')

# ================================================================================================================ 1. the P9 numbers (Python)
P.rep('''P3_LEVELS_TEXT = ",".join(str(_x) for _x in P3_LEVELS)
''', '''P3_LEVELS_TEXT = ",".join(str(_x) for _x in P3_LEVELS)
# 0.4.62 BALANCE P9 (research/Balance-P9-Check.md F1-F4; tools/balance_model.py P9_BASE / P9_LEVELS, tools/balance_rebirth.py PAST_LIFE_P8):
# P9_BASE = the P3 base x1.5 for Lv 61-80, x1.9 for Lv 81-100 (SkillDefs.DEFAULT_PER); P9_LEVELS = x levels.scale 120 %% (DEFAULT_RUN, levels=)
P9_BASE = %r
P9_LEVELS = %r
assert P9_BASE == [int(round(_x * (1.5 if 61 <= _L <= 80 else (1.9 if _L >= 81 else 1.0)))) for _L, _x in zip(range(1, 101), P3_BASE)], "0.4.62: P9 F4 base"
assert P9_LEVELS == [int(_m57.floor(_x * (P3_SCALE / 100.0) + 0.5)) for _x in P9_BASE] and P9_LEVELS[:60] == P3_LEVELS[:60]
assert round(sum(P9_LEVELS) * 100.0 / sum(P9_BASE)) == P3_SCALE   # the curve-size row still reads 120
P9_LEVELS_TEXT = ",".join(str(_x) for _x in P9_LEVELS)
P9_PAST = "%s"   # rebirth.pastLifeXp (P9 F4)
EVEN_FELL9, EVEN_MINE9 = "100", "1"   # fell.otherLogsPercent / mining.xpMultiplier (P9 F2; 0.4.43 - 0.4.61: EVEN_FELL 70 / EVEN_MINE 1.25)
P9_CATCH_MAX, P9_BEAST = "20", "1.5"   # catchup.max (P9 F3; was 100) / beast.xpFactor (P9 F1; was 1)
''' % (P9_BASE, P9_LEVELS, P9_PAST))

# ================================================================================================================ 2. the Java code defaults
P.rep('''defs.addField(CtField.make("public static final long[] DEFAULT_PER = new long[] { %s };" % ", ".join("%dL" % x for x in P3_BASE), defs))   # 0.4.57: the P3 base = 100 %
defs.addField(CtField.make("public static final long[] DEFAULT_RUN = new long[] { %s };" % ", ".join("%dL" % x for x in P3_LEVELS), defs))   # 0.4.57: the default list (levels.scale 120 %)''',
      '''defs.addField(CtField.make("public static final long[] DEFAULT_PER = new long[] { %s };" % ", ".join("%dL" % x for x in P9_BASE), defs))   # 0.4.57: the P3 base = 100 % (0.4.62: the P9 base)
defs.addField(CtField.make("public static final long[] DEFAULT_RUN = new long[] { %s };" % ", ".join("%dL" % x for x in P9_LEVELS), defs))   # 0.4.57: the default list (levels.scale 120 %; 0.4.62: the P9 list)
defs.addField(CtField.make("public static final long[] DEFAULT_P3 = new long[] { %s };" % ", ".join("%dL" % x for x in P3_LEVELS), defs))   # 0.4.62: the 0.4.57 - 0.4.61 default list (the curve moves' old code default)''')
P.rep('''for _d43 in ("public static volatile double FELL_PCT = (double) @EVEN_FELL@;", "public static volatile double MINE = (double) @EVEN_MINE@;",''',
      '''for _d43 in ("public static volatile double FELL_PCT = (double) @EVEN_FELL9@;", "public static volatile double MINE = (double) @EVEN_MINE9@;",   # 0.4.62 P9 F2''')
P.rep('''  FELL_PCT = @PKG@.HpRegen.clampD(@PKG@.SkillCfg.dbl(p, "fell.otherLogsPercent", (double) @EVEN_FELL@), (double) @EVEN_FELL@, 0.0, 500.0);
  MINE = @PKG@.HpRegen.clampD(@PKG@.SkillCfg.dbl(p, "mining.xpMultiplier", (double) @EVEN_MINE@), (double) @EVEN_MINE@, 0.0, 10.0);''',
      '''  FELL_PCT = @PKG@.HpRegen.clampD(@PKG@.SkillCfg.dbl(p, "fell.otherLogsPercent", (double) @EVEN_FELL9@), (double) @EVEN_FELL9@, 0.0, 500.0);   // 0.4.62 P9 F2: 100 (was 70)
  MINE = @PKG@.HpRegen.clampD(@PKG@.SkillCfg.dbl(p, "mining.xpMultiplier", (double) @EVEN_MINE9@), (double) @EVEN_MINE9@, 0.0, 10.0);   // 0.4.62 P9 F2: 1 (was 1.25)''')
P.rep('''p3x.addField(CtField.make('public static final String DEF_PAST = "%s";' % P3_PAST, p3x))''',
      '''p3x.addField(CtField.make('public static final String DEF_PAST = "%s";' % P9_PAST, p3x))   # 0.4.62 P9 F4 (was P3_PAST = the P8 list)''')
P.rep('''             "public static volatile double CATCH_MAX = 1.0;", "public static volatile boolean[] CATCH''', '''             "public static volatile double CATCH_MAX = 0.2;", "public static volatile boolean[] CATCH''')   # 0.4.62 P9 F3 (was 1.0)
P.rep('''"public static volatile double[] PAST = new double[] { %s };" % ", ".join(repr(float(_x)) for _x in P8_PAST.split(",")),   # 0.4.59 Balance P8''',
      '''"public static volatile double[] PAST = new double[] { %s };" % ", ".join(repr(float(_x)) for _x in P9_PAST.split(",")),   # 0.4.59 Balance P8 (0.4.62: the P9 list)''')
P.rep('''             "public static volatile double BEAST_F = 1.0;",   # 0.4.60 beast.xpFactor (Beastmastery XP per pet XP)
             'public static volatile String PAST_TEXT = "%s";' % P3_PAST,''',
      '''             "public static volatile double BEAST_F = 1.5;",   # 0.4.60 beast.xpFactor (Beastmastery XP per pet XP; 0.4.62 P9 F1: 1.5)
             'public static volatile String PAST_TEXT = "%s";' % P9_PAST,''')
P.rep('''  CATCH_MAX = clamp(@PKG@.SkillCfg.dbl(p, "catchup.max", 100.0), 0.0, 500.0, 100.0) / 100.0;''',
      '''  CATCH_MAX = clamp(@PKG@.SkillCfg.dbl(p, "catchup.max", 20.0), 0.0, 500.0, 20.0) / 100.0;   // 0.4.62 P9 F3: 20 % (was 100)''')
P.rep('''  BEAST_F = clamp(@PKG@.SkillCfg.dbl(p, "beast.xpFactor", 1.0), 0.0, 10.0, 1.0);   // 0.4.60 Balance P8c: Beastmastery XP per pet XP''',
      '''  BEAST_F = clamp(@PKG@.SkillCfg.dbl(p, "beast.xpFactor", 1.5), 0.0, 10.0, 1.5);   // 0.4.60 Balance P8c: Beastmastery XP per pet XP (0.4.62 P9 F1: 1.5)''')
P.rep('''rebirth 1 first (1.1,1.35,1.6,2,2.45,2.15,2.25,2.4,2.55,2.7)." : null;''', '''rebirth 1 first (%s)." : null;''' % P9_PAST)

# ================================================================================================================ 3. the Server Setup rows
P.rep('''LEVELS_TEXT = P3_LEVELS_TEXT   # 0.4.57: the P3 list (was the 0.4.3 - 0.4.56 levels=)''',
      '''LEVELS_TEXT = P9_LEVELS_TEXT   # 0.4.57: the P3 list (was the 0.4.3 - 0.4.56 levels=); 0.4.62: the P9 list''')
P.rep('''     "XP every level needs as % of the P3 base curve (120 = Lv 50 at ~33 h). Rewrites the list above.", "custom:SkillKit"),''',
      '''     "XP every level needs as % of the base curve (120 = Lv 50 at ~33 h). Rewrites the list above.", "custom:SkillKit"),''')
P.rep('''    ("catchup.max", "Catch-up max", "levels", "int", "100", "0", "500", "", "%", "live",
     "The most catch-up XP (100 = at most double XP).", "reload"),''',
      '''    ("catchup.max", "Catch-up max", "levels", "int", P9_CATCH_MAX, "0", "500", "", "%", "live",
     "The most catch-up XP (20 = at most +20%; 100 = double XP).", "reload"),''')
P.rep('''    ("rebirth.pastLifeXp", "Past-life XP boost by rebirth", "levels", "text", P3_PAST, "", "200", "", "", "live",''',
      '''    ("rebirth.pastLifeXp", "Past-life XP boost by rebirth", "levels", "text", P9_PAST, "", "200", "", "", "live",''')
P.rep('''    ("beast.xpFactor", "Beastmastery XP per pet XP", "levels", "dec", "1", "0", "10", "", "x", "live",''',
      '''    ("beast.xpFactor", "Beastmastery XP per pet XP", "levels", "dec", P9_BEAST, "0", "10", "", "x", "live",''')
P.rep('''    ("fell.otherLogsPercent", "Other felled logs XP", "gathering", "dec", EVEN_FELL, "0", "500", "", "%", "live",''',
      '''    ("fell.otherLogsPercent", "Other felled logs XP", "gathering", "dec", EVEN_FELL9, "0", "500", "", "%", "live",''')
P.rep('''    ("mining.xpMultiplier", "Mining XP multiplier", "gathering", "dec", EVEN_MINE, "0", "10", "", "x", "live",''',
      '''    ("mining.xpMultiplier", "Mining XP multiplier", "gathering", "dec", EVEN_MINE9, "0", "10", "", "x", "live",''')

# ================================================================================================================ 4. the fresh default file + the P9Mig plan
P9DATA = r'''# ================= 0.4.62 BALANCE P9 - the P9Mig plan and the fresh default file (tools/skills_0_4_62_patch.py) =================
P9_KEYS = [("beast.xpFactor", "1", P9_BEAST, "beast.xpFactor"), ("mining.xpMultiplier", EVEN_MINE, EVEN_MINE9, "mining.xpMultiplier"),
           ("fell.otherLogsPercent", EVEN_FELL, EVEN_FELL9, "fell.otherLogsPercent"), ("catchup.max", "100", P9_CATCH_MAX, "catchup.max"),
           ("levels", P3_LEVELS_TEXT, P9_LEVELS_TEXT, "levels"), ("rebirth.pastLifeXp", P8_PAST, P9_PAST, "rebirth.pastLifeXp")]   # (key, 0.4.61 default, 0.4.62, row)
P9_MARK_ID = "Balance P9 first-run fixes (SkyySkills 0.4.62)"
P9_MARK = "# %s: Beastmastery XP, Mining and felled log XP, catch-up, levels 61-100 and the past-life list" % P9_MARK_ID
P9_HEAD = ["", "# ---------- Balance P9: whole first-run fixes (SkyySkills 0.4.62) ----------",
           "# Comments must stay on their own lines. Changed above (only lines still holding the 0.4.61 default): beast.xpFactor 1.5,",
           "# mining.xpMultiplier 1, fell.otherLogsPercent 100, catchup.max 20, levels (61-80 x1.5, 81-100 x1.9; players keep their levels)",
           "# and rebirth.pastLifeXp (the list that keeps every rebirth run about 15 percent shorter)."]
for _t in P9_HEAD + [P9_MARK]:
    assert all(32 <= ord(_c) < 127 for _c in _t) and '"' not in _t and "\\" not in _t and (not _t or _t.startswith("# ")), _t
assert "=" not in P9_MARK and not any(_cre.match(r"#\s*[A-Za-z][A-Za-z0-9._-]*\s*[=:]\s*\S+\s*$", _ln) for _ln in P9_HEAD)
P9_BLOCK = "\n".join(P9_HEAD + [P9_MARK]) + "\n"
DEFAULTS_061 = DEFAULTS   # 0.4.62: the 0.4.61 default file
_d62 = "\n" + DEFAULTS_061
for _k, _o, _n, _r in P9_KEYS:
    assert _d62.count("\n%s=%s\n" % (_k, _o)) == 1 and _d62.count("\n%s=" % _k) == 1, _k   # one line, the 0.4.61 default
    _d62 = _d62.replace("\n%s=%s\n" % (_k, _o), "\n%s=%s\n" % (_k, _n))
DEFAULTS = _d62[1:] + ("" if _d62.endswith("\n") else "\n") + P9_BLOCK
assert all(ord(ch) < 128 for ch in DEFAULTS) and len(DEFAULTS.encode("utf-8")) < 65000 and DEFAULTS.count(P9_MARK_ID) == 1, len(DEFAULTS)
print("0.4.62: P9 update plan %d key(s); default file %d bytes; Lv 61 / 80 / 100 need %d / %d / %d XP (was %d / %d / %d)" % (
    len(P9_KEYS), len(DEFAULTS), P9_LEVELS[60], P9_LEVELS[79], P9_LEVELS[99], P3_LEVELS[60], P3_LEVELS[79], P3_LEVELS[99]))
'''
P.rep('''DEFAULTS_LIT = json.dumps(DEFAULTS)   # valid Java string literal for ASCII text (\\n \\" \\\\ escapes)''',
      P9DATA + '''DEFAULTS_LIT = json.dumps(DEFAULTS)   # valid Java string literal for ASCII text (\\n \\" \\\\ escapes)''')
# the older blocks' default-file checks read the 0.4.61 file (_dp61) where P9 moved the value; the new values checked against _dp
P.rep('''_dp56 = {}   # 0.4.57: the 0.4.56 default file (the 0.4.56 blocks' own checks below read it)''',
      '''_dp61 = {}   # 0.4.62: the 0.4.61 default file (the older blocks' checks of the 6 keys P9 moved read it)
for _ln in DEFAULTS_061.split("\\n"):
    _t = _ln.strip()
    if _t and not _t.startswith("#") and "=" in _t:
        _dp61[_t.split("=", 1)[0].strip()] = _t.split("=", 1)[1].strip()
assert sorted(_k for _k in set(_dp) | set(_dp61) if _dp.get(_k) != _dp61.get(_k)) == sorted(_e[0] for _e in P9_KEYS), "0.4.62: only the P9 keys moved"
assert all(_dp.get(_k) == _n and _dp61.get(_k) == _o for _k, _o, _n, _r in P9_KEYS) and DEFAULTS.endswith(P9_BLOCK)   # 0.4.62
_dp56 = {}   # 0.4.57: the 0.4.56 default file (the 0.4.56 blocks' own checks below read it)''')
P.rep('''    assert len(_r43) == 1 and _dp.get(_k43) is not None and ("\\n" + _k43 + "=" + _dp[_k43] + "\\n") in ("\\n" + G43_DEFAULTS), _k43
    assert _r43[0][2] == ("gathering" if _k43 in ("fell.otherLogsPercent", "mining.xpMultiplier") else "overall") and (_r43[0][3] == "bool" or _Dec(_r43[0][4]) == _Dec(_dp[_k43])), _k43''',
      '''    assert len(_r43) == 1 and _dp61.get(_k43) is not None and ("\\n" + _k43 + "=" + _dp61[_k43] + "\\n") in ("\\n" + G43_DEFAULTS), _k43   # 0.4.62: the 0.4.61 file
    assert _r43[0][2] == ("gathering" if _k43 in ("fell.otherLogsPercent", "mining.xpMultiplier") else "overall") and (_r43[0][3] == "bool" or _Dec(_r43[0][4]) == _Dec(_dp[_k43])), _k43''')
P.rep('''_dp.get("rebirth.pastLifeXp") == P8_PAST and _dp.get("rebirth.xpMultMax") == "0"   # 0.4.59 (0.4.60: the 0.4.59 file)''',
      '''_dp61.get("rebirth.pastLifeXp") == P8_PAST and _dp.get("rebirth.xpMultMax") == "0"   # 0.4.59 (0.4.60: the 0.4.59 file; 0.4.62: _dp61)''')
P.rep('''_dp.get("catchup.skills") == P3_CATCH and _dp.get("beast.xpFactor") == "1"   # 0.4.60 (0.4.61: the 0.4.60 file)''',
      '''_dp.get("catchup.skills") == P3_CATCH and _dp61.get("beast.xpFactor") == "1"   # 0.4.60 (0.4.61: the 0.4.60 file; 0.4.62: _dp61)''')
P.rep('''assert DEFAULTS.endswith(SK_BLOCK) and DEFAULTS.count(SK_MARK_ID) == 1 and _dp.get("levelCoins") == LC61_TEXT''',
      '''assert DEFAULTS_061.endswith(SK_BLOCK) and DEFAULTS.count(SK_MARK_ID) == 1 and _dp.get("levelCoins") == LC61_TEXT''')
P.rep('''    assert _k57.count(_k) == 1 and _dp.get(_k) == _v and ("\\n%s=%s\\n" % (_k, _v)) in ("\\n" + P3_BLOCK) and _k not in _dp56, _k''',
      '''    assert _k57.count(_k) == 1 and _dp61.get(_k) == _v and ("\\n%s=%s\\n" % (_k, _v)) in ("\\n" + P3_BLOCK) and _k not in _dp56, _k   # 0.4.62: _dp61''')
P.rep('''assert all(_dp.get(_k) == _v and _k not in _dp56 for _k, _v, _r in P3_ADD)''', '''assert all(_dp61.get(_k) == _v and _k not in _dp56 for _k, _v, _r in P3_ADD)   # 0.4.62: _dp61''')
P.rep('''assert all(_dp.get(_k) == (_n if _n is not None else None) for _k, _o, _n, _r in P3_KEYS) and''',
      '''assert all(_dp61.get(_k) == (_n if _n is not None else None) for _k, _o, _n, _r in P3_KEYS) and''')

# ================================================================================================================ 5. CurveP3Mig keeps moving to the P3 list
P.rep('''  long[][] tn = tables(props((String) r[0]), @PKG@.SkillDefs.DEFAULT_RUN, true);''',
      '''  long[][] tn = tables(props((String) r[0]), @PKG@.SkillDefs.DEFAULT_P3, true);   // 0.4.62: the P3 list (CurveP9Mig moves on to P9)''')
P.rep('''    if (old == null) nt = @PKG@.SkillCfg.DEFAULTS;''',
      '''    if (old == null) nt = "";   // 0.4.62: no file = the 0.4.61 code defaults (DEFAULT_P3 below), never the P9 default file''')
P.rep('''    long[][] tn = tables(props(nt), @PKG@.SkillDefs.DEFAULT_RUN, true);''',
      '''    long[][] tn = tables(props(nt), @PKG@.SkillDefs.DEFAULT_P3, true);   // 0.4.62: the P3 list (CurveP9Mig moves on to P9)''')

# ================================================================================================================ 6. SkillCfg.P9PEND + p9pend
_P3PEND = OLD[OLD.index('cfg.addField(CtField.make("public static volatile boolean P3PEND = false;", cfg))'):]
_P3PEND = _P3PEND[:_P3PEND.index('}"""), cfg))') + len('}"""), cfg))')]
_P9PEND = _P3PEND
for _a, _b in (("P3PEND", "P9PEND"), ("p3pend", "p9pend"), ("@PKG@.P3Mig", "@PKG@.P9Mig"), ("the 0.4.57 settings", "the 0.4.62 settings")):
    assert _a in _P9PEND, _a
    _P9PEND = _P9PEND.replace(_a, _b)
assert "P3" not in _P9PEND and "0.4.57" not in _P9PEND
P.rep('''cfg.addField(CtField.make("public static volatile boolean P3PEND = false;", cfg))''',
      "# 0.4.62 (CurveP9Mig.after): the saved XP moved to the P9 list but P9Mig's xp.properties update failed -> load() reads P9Mig.plan's text\n"
      + _P9PEND + "\n" + '''cfg.addField(CtField.make("public static volatile boolean P3PEND = false;", cfg))''')
P.rep('''    p = p3pend(p);   // 0.4.57 fix 2: the saved XP moved but the xp.properties update failed -> the planned 0.4.57 text (CurveP3Mig.after)''',
      '''    p = p3pend(p);   // 0.4.57 fix 2: the saved XP moved but the xp.properties update failed -> the planned 0.4.57 text (CurveP3Mig.after)
    p = p9pend(p);   // 0.4.62: the same for the Balance P9 move (CurveP9Mig.after)''')
# fix round 2 (second critic MEDIUM: Server Setup -> Changes -> Undo of ONLY the levels row after the move = the moved Lv 61-100 totals read
# on the cheaper 0.4.61 list -> higher levels, and payLocked paid their level-up coins at once; a WARN alone did not stop that). Every
# SkillCfg.load (start + every Server Setup save / Undo) sets P9STALE = the levels in effect are exactly the 0.4.61 list while curve-p9.properties
# says the saved XP WAS moved (complete= + history=); while it is set SkillStore.payLocked pays NOTHING (the paid markers stay, so the coins
# are paid normally once the 0.4.62 list is back and the levels drop again). No XP is moved, no file is written.
P.rep('''cfg.addField(CtField.make("public static volatile boolean P3PEND = false;", cfg))''',
      '''cfg.addField(CtField.make("public static volatile boolean P9STALE = false;", cfg))   # 0.4.62 fix round 2: level-up coins held (p9stale)
cfg.addMethod(CtNewMethod.make(J14(r"""
public static boolean p9stale() {
  try {
    if (FILE == null || !java.util.Arrays.equals(@PKG@.SkillDefs.PER, @PKG@.SkillDefs.DEFAULT_P3)) return false;
    java.nio.file.Path par = FILE.toAbsolutePath().getParent();
    if (par == null) return false;
    java.nio.file.Path mk = par.resolve("curve-p9.properties");
    if (!java.nio.file.Files.exists(mk, new java.nio.file.LinkOption[0])) return false;
    java.util.Properties st = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(mk, new java.nio.file.OpenOption[0]);
    try { st.load(in); } finally { in.close(); }
    if (st.getProperty("complete") == null || st.getProperty("history") == null) return false;
    warn("Balance P9: the levels list is back on the 0.4.61 list, but the saved XP was moved to the 0.4.62 list (curve-p9.properties) - anyone above Lv 60 shows a HIGHER level, so level-up coins are HELD (nothing paid) until the 0.4.62 levels row is back (Server Setup -> Changes -> Undo that Undo) or SkyySkills is rolled back fully (curve-p9.log has the steps)");
    return true;
  } catch (Throwable t) {
    return false;
  }
}"""), cfg))
cfg.addField(CtField.make("public static volatile boolean P3PEND = false;", cfg))''')
P.rep('''    {PKG}.SkillDefs.setClassTable(cper, bool(p, "levels.class.sameAsOthers", true));   // 0.4.57: default true (P3 one curve)''',
      '''    {PKG}.SkillDefs.setClassTable(cper, bool(p, "levels.class.sameAsOthers", true));   // 0.4.57: default true (P3 one curve)
    P9STALE = p9stale();   // 0.4.62 fix round 2: the levels row undone alone after the P9 move -> level-up coins held''')
P.rep('''  if (rbn < 0) return new long[] {{ -1L, -1L, 0L, per, 0L, 0L }};''',
      '''  if (rbn < 0) return new long[] {{ -1L, -1L, 0L, per, 0L, 0L }};
  if ({PKG}.SkillCfg.P9STALE) return new long[] {{ -1L, -1L, 0L, per, 0L, (long) rbn }};   // 0.4.62 fix round 2: the levels row undone alone after the P9 move -> nothing paid, the marker stays''')

# ================================================================================================================ 7. P9Mig + CurveP9Mig
P.rep('''cp3 = pool.makeClass(PKG + ".CurveP3Mig")      # 0.4.57: the one-time saved-XP move to the P3 level list, levels kept (spec 6.2)''',
      '''cp3 = pool.makeClass(PKG + ".CurveP3Mig")      # 0.4.57: the one-time saved-XP move to the P3 level list, levels kept (spec 6.2)
p9m62 = pool.makeClass(PKG + ".P9Mig")          # 0.4.62: the one-time Balance P9 update of xp.properties (6 defaults)
cp962 = pool.makeClass(PKG + ".CurveP9Mig")     # 0.4.62: the one-time saved-XP move to the P9 level list (Lv 61-100), levels kept''')

_a = OLD.index('bm60.addMethod(CtNewMethod.make(J14(r"""\npublic static int idx(')
_BM = OLD[_a:OLD.index("\n\n# ---- CurveP3Mig (0.4.57", _a)]
for _x, _y in (('"the 0.4.60 default has no such line" : "the 0.4.60 (Balance P8c) default is "', '"the 0.4.62 default has no such line" : "the 0.4.62 (Balance P9) default is "'),
               ('"xp.properties updated for 0.4.60 (Balance P8c: Beastmastery in catch-up, Beastmastery XP per pet XP row): "',
                '"xp.properties updated for 0.4.62 (Balance P9: Beastmastery XP, Mining + felled log XP, catch-up, levels 61-100, past-life list): "'),
               ('"before the 0.4.60 Balance P8c update"', '"before the 0.4.62 Balance P9 update"'),
               ("xp.properties NOT updated for 0.4.60 (Balance P8c)", "xp.properties NOT updated for 0.4.62 (Balance P9)"),
               ('"could not update xp.properties for 0.4.60 (Balance P8c; the file is used as it is): "', '"could not update xp.properties for 0.4.62 (Balance P9; the file is used as it is): "')):
    assert _x in _BM, _x
    _BM = _BM.replace(_x, _y)
_BM = re.sub(r"\bbm60\b", "p9m62", _BM)
assert "0.4.60" not in _BM and "P8c" not in _BM and "bm60" not in _BM, _BM[:300]
P9M = r'''# ---- P9Mig (0.4.62, PROJECT-RULES section 4; BmMigP8c's reviewed machinery, copied): ONCE on an EXISTING xp.properties, setup() right after
# CurveP9Mig.run (which moved the saved XP first), BEFORE SkillCfg.load. Each P9 key whose LAST entry is a one-line entry holding exactly the
# 0.4.61 default (OLDS) -> NEWS; any other value kept (INFO); no line = nothing written (the 0.4.62 code default applies). Then ONE block in the
# file's own line ending: HEAD + the marker (no new keys). config-history copy first (verified), one config-changes.log row per change
# (Undo), Properties check, atomicWrite. A failure = WARN, file untouched, retried next start.
p9m62.addField(CtField.make("public static final String MARK_ID = %s;" % json.dumps(P9_MARK_ID), p9m62))
p9m62.addField(CtField.make("public static final String MARK = %s;" % json.dumps(P9_MARK), p9m62))
p9m62.addField(CtField.make("public static final String HEAD = %s;" % json.dumps("\n".join(P9_HEAD) + "\n"), p9m62))
p9m62.addField(CtField.make("public static final String[] KEYS = %s;" % jarr([_e[0] for _e in P9_KEYS]), p9m62))
p9m62.addField(CtField.make("public static final String[] OLDS = %s;" % jarr([_e[1] for _e in P9_KEYS]), p9m62))
p9m62.addField(CtField.make("public static final String[] NEWS = %s;" % jarr([_e[2] for _e in P9_KEYS]), p9m62))
p9m62.addField(CtField.make("public static final String[] ROWK = %s;" % jarr([_e[3] for _e in P9_KEYS]), p9m62))
p9m62.addField(CtField.make("public static final String[] ADDK = %s;" % jarr([]), p9m62))
p9m62.addField(CtField.make("public static final String[] ADDV = %s;" % jarr([]), p9m62))
p9m62.addField(CtField.make("public static final String[] ADDR = %s;" % jarr([]), p9m62))
p9m62.addField(CtField.make('public static final String WHO = "SkyySkills 0.4.62";', p9m62))
''' + _BM + "\n"

_a = OLD.index("cp3.addField(CtField.make('public static final String NAME")
_CP = OLD[_a:OLD.index("\n\n# ---- Zo49Mig (0.4.49", _a)]
for _x, _y, _n in (("@PKG@.SkillDefs.DEFAULT_056, false", "@PKG@.SkillDefs.DEFAULT_P3, true", 2),   # the OLD tables: the 0.4.61 code defaults
                   ("P3Mig", "P9Mig", 9), ("SkillCfg.P3PEND", "SkillCfg.P9PEND", 2), ("curve-p3", "curve-p9", 6), (".p3tmp", ".p9tmp", 2),
                   ("Undo the 0.4.57 rows or roll SkyySkills back to 0.4.56 (never Undo the levels rows alone)",
                    "Undo the 0.4.62 rows or roll SkyySkills back to 0.4.61 (never Undo the levels row alone)", 1),
                   ("0.4.57", "0.4.62", 11), ("Balance P3", "Balance P9", 11), ("_d57", "_d62", 2)):
    assert _CP.count(_x) == _n, (_x, _CP.count(_x))
    _CP = _CP.replace(_x, _y)
_CP = re.sub(r"\bcp3\b", "cp962", _CP)
for _x, _y in (("later pre-P3 xp.properties", "later pre-P9 xp.properties"), ("without the P3 update ->", "without the P9 update ->")):   # comments
    assert _CP.count(_x) == 1, _x
    _CP = _CP.replace(_x, _y)
# the precondition: only after the Balance P3 update of xp.properties landed (else a pre-P3 file's levels= would read as an admin's list)
_x = '''  if (base == null) return true;
  java.nio.file.Path par = base.toAbsolutePath().getParent();'''
assert _CP.count(_x) == 1
_CP = _CP.replace(_x, '''  if (base == null) return true;
  if (!p3ok()) return false;   // 0.4.62: the Balance P3 update of xp.properties first (nothing changed; the next start tries again)
  java.nio.file.Path par = base.toAbsolutePath().getParent();''')
_x = '''cp962.addMethod(CtNewMethod.make(J14(r"""
public static synchronized boolean run(java.nio.file.Path base) {'''
assert _CP.count(_x) == 1
_CP = _CP.replace(_x, '''# 0.4.62: true = xp.properties has had its Balance P3 update (or there is no file); false = WARN, this start moves nothing
cp962.addMethod(CtNewMethod.make(J14(r"""
public static boolean p3ok() {
  if (@PKG@.SkillCfg.P3PEND) {
    @PKG@.SkillCfg.warn("Balance P9 saved XP update waits: the Balance P3 update of xp.properties has not landed yet - nothing changed (the next start tries again)");
    return false;
  }
  try {
    java.nio.file.Path f = @PKG@.SkillCfg.FILE;
    if (f == null || !java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return true;
    if (@PKG@.P3Mig.plan(new String(java.nio.file.Files.readAllBytes(f), "ISO-8859-1")) == null) return true;
    @PKG@.SkillCfg.warn("Balance P9 saved XP update waits: xp.properties has not had its Balance P3 (0.4.57) update yet - nothing changed (the next start tries again)");
  } catch (Throwable t) {
    @PKG@.SkillCfg.warn("Balance P9 saved XP update NOT done: could not read xp.properties (" + t + ") - the next start tries again");
  }
  return false;
}"""), cp962))
''' + _x)
# fix round (critic LOW 1: Server Setup -> Changes -> Undo of ONLY the levels row after the move = the moved Lv 61-100 totals read on the
# cheaper 0.4.61 list -> higher levels + their level-up coins): the guard cannot tell it from an admin's choice and must not move XP or
# override the file on its own, so it WARNs loudly at every start while xp.properties' levels= is exactly the 0.4.61 list after the move
_x = '''  Object[] r = @PKG@.P9Mig.plan(txt);
  if (r == null) return 1;
  String hist = st.getProperty("history");'''
assert _CP.count(_x) == 1
_CP = _CP.replace(_x, '''  Object[] r = @PKG@.P9Mig.plan(txt);
  if (r == null) { levelsUndone(txt); return 1; }   // fix round: WARN while the levels row is back on the 0.4.61 list after the move
  String hist = st.getProperty("history");''')
_x = '''cp962.addMethod(CtNewMethod.make(J14(r"""
public static int guard('''
assert _CP.count(_x) == 1
_CP = _CP.replace(_x, '''# fix round (critic LOW 1): true + a WARN = the saved XP was moved (complete + xp= + history=) but xp.properties' levels= is exactly the 0.4.61
# list again (Server Setup -> Changes -> Undo of the levels row alone): anyone above Lv 60 now shows a higher level. Nothing is changed.
cp962.addMethod(CtNewMethod.make(J14(r"""
public static boolean levelsUndone(String txt) {
  try {
    String lv = props(txt).getProperty("levels");
    if (lv == null) return false;
    String old = null;
    for (int i = 0; i < @PKG@.P9Mig.KEYS.length; i++) if ("levels".equals(@PKG@.P9Mig.KEYS[i])) old = @PKG@.P9Mig.OLDS[i];
    if (old == null || !@PKG@.SkillCfg.squash(old).equals(@PKG@.SkillCfg.squash(lv))) return false;
    @PKG@.SkillCfg.warn("Balance P9: xp.properties' levels= is back on the 0.4.61 list, but the saved XP was moved to the 0.4.62 list (" + NAME + ") - anyone above Lv 60 now shows a HIGHER level (its level-up coins are held - nothing is paid). Put the 0.4.62 levels row back (Server Setup -> Changes -> Undo that Undo), or roll back fully (curve-p9.log has the steps)");
    return true;
  } catch (Throwable t) {
    return false;
  }
}"""), cp962))
''' + _x)
_ALLOW = ("@PKG@.P3Mig.plan(new String", "@PKG@.SkillCfg.P3PEND) {", "Balance P3 update of xp.properties", "Balance P3 (0.4.57) update", "its Balance P3 update", "DEFAULT_P3")
_left = _CP
for _w in _ALLOW:
    _left = _left.replace(_w, "")
assert "P3" not in _left, [m.group(0) for m in re.finditer(r".{0,50}P3.{0,30}", _left)]
assert "0.4.57" not in _CP.replace("Balance P3 (0.4.57)", "") and "0.4.56" not in _CP and "cp3" not in _CP
CP9 = r'''# ---- CurveP9Mig (0.4.62, PROJECT-RULES section 4; CurveP3Mig's reviewed machinery, copied): ONCE, setup() right after SkMigP7, BEFORE P9Mig
# (which only runs once this is done) and SkillCfg.load, and only after the Balance P3 update of xp.properties (p3ok). The OLD tables =
# xp.properties as it is (code default SkillDefs.DEFAULT_P3 = the 0.4.61 list); the NEW ones = the same file after P9Mig.plan (an admin's own
# list stays -> that slot is not moved). Every slot whose table changes: level Lo + progress p kept; XP at / past the profile's cap keeps its
# ratio to the cap total (rebirth:fn:cap); History copy of players/ + rebirth/ staged files + level-floors.properties FIRST (read back); a
# level check per slot; .p9tmp + fsync + rename; curve-p9.properties done.<pkey> after each. Only <Slot>= values change. Levels 1-60 cost the
# same in both lists, so a total below Lv 60 maps to itself.
''' + _CP + "\n"
_x = '''    @PKG@.SkillCfg.warn("Balance P3 saved XP update NOT done (" + t + ") - xp.properties not updated (the next start tries again)");
    return false;
  }
}"""), cp3))
'''
assert P.s.count(_x) == 1
P.rep(_x, _x + "\n" + P9M + CP9)

# ================================================================================================================ 8. setup() + the class list
P.rep('''  {PKG}.SkMigP7.run();        // 0.4.61 Balance P7: + the levelCoins row (empty while coinsPerLevel is an admin's), once; History first''',
      '''  {PKG}.SkMigP7.run();        // 0.4.61 Balance P7: + the levelCoins row (empty while coinsPerLevel is an admin's), once; History first
  if ({PKG}.CurveP9Mig.run(base)) {{ {PKG}.P9Mig.run(); {PKG}.CurveP9Mig.after(base); }}   // 0.4.62 Balance P9: saved XP on Lv 61-100 (levels kept) FIRST, then the 6 xp.properties defaults; once each''')
P.rep("cst, p4m, plm8, bm60, lvc61, skm61, lvf,", "cst, p4m, plm8, bm60, lvc61, skm61, p9m62, cp962, lvf,")

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0 and P.s.count("makeClass(") == CLS0 + 2
_i = P.s.index
assert _i("public static java.util.Properties p9pend(") < _i("public static synchronized String load() {{")
_c9 = _i("# ---- CurveP9Mig (0.4.62")
assert _i('p9m62.addMethod(CtNewMethod.make(J14(r"""\npublic static Object[] plan(') < _c9 < _i("public static void after(java.nio.file.Path base)", _c9) \
    < _i("public static boolean p3ok()") < _i("public static synchronized boolean run(java.nio.file.Path base)", _c9)   # methods before callers
assert _i("public static long[][] tables(", _c9) < _i("public static synchronized boolean run(java.nio.file.Path base)", _c9)
P.finish()
