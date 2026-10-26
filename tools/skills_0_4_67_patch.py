"""Derive SkyySkills/build_skyyskills_0.4.67.py from the GENERATED SkyySkills 0.4.66 (build_skyyskills_0.4.66.py = the tools/deploy_set.py SET
pin, made by tools/skills_0_4_66_patch.py). Every anchor is asserted once; at the end every change is undone on a copy and compared with
0.4.66 (tools/soundpass_gen.Patch). Line endings kept. Edit THIS file, never the generated script.
Run:  python tools/skills_0_4_67_patch.py   then   python SkyySkills/build_skyyskills_0.4.67.py   (never --deploy)
      then  python SkyySkills/test_skyyskills_0.4.67.py
Round forxp = Foraging XP balance (docs/answered/skills.md 2026-10-25 FORAGING TOO FAST; the model: python tools/balance_model.py --forxp).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

NOTE = '''0.4.67 (2026-10-25) = FORAGING XP BY WOOD TIER + LESS FOR BIG TREES (docs/answered/skills.md 2026-10-25 FORAGING TOO FAST; Skyy: "i think
  foraging levels too fast. i just reached lvl 50 in zone 1" + "just chopping some maple" + "id fix this by setting the xp per log by the tier.
  and if that doesnt work, id do the less for big trees. and the steeper curve only if we need").
  WHY: since 0.4.57 (Balance P3) every log already paid by its wood tier (block.Wood_<wood>_Trunk rows, tier_tags LOGS: T1 Oak 35 ... T3
    Maple 120 ... T15 1600), tuned for 400 logs an hour. Real trees are far bigger (Assets.zip prefabs: a grown Maple = 250 trunks + 45
    branches + 1167 leaves; Amber / Redwood giants 1500-2000 trunks) and Tree Feller pays every log, so one Maple paid ~31k XP - Skyy's
    live log: Foraging 24 -> 50 in 32 minutes. Step 1 alone cannot fix it: a per-log value low enough for a 250-log Maple (~2 XP) makes a
    23-log Oak worthless. So step 1 + step 2 (tools/balance_model.py --forxp: Zone 1 end ~Lv 18-20; step 3 = a steeper curve NOT needed).
  1 LOG XP BY TIER (step 1): every wood tier's row = FX_PCT % of its P3 value, min 1: Zone 1 woods (T1-T3) 10 %, T4-T9 14 %, T10-T12
    19 %, T13-T15 31 % (fixer: a flat tenth left Zones 2-5 at 0.3-0.7x the XP/h their zone needs; now each zone's best tree ~1.0x):
    T1-T15 = 4,7,12,22,34,46,56,74,91,142,174,200,372,434,496 (Oak / Birch 4, Beech / Ash / Aspen / Apple 7, Maple / Azure 12 ...); the
    unknown-trunk fallback suffix._Trunk / _Trunk_Full 35 -> 4 (= T1). Chopped AND felled logs (both read the same table).
  2 BIG TREES (step 2, FellCfg.share): the k-th log of one felled tree (the chopped one = 1) pays its XP x (fell.bigTreeFrom / k) ^
    fell.bigTreeFalloff past fell.bigTreeFrom logs (defaults 30 and 2: a 23-log Oak pays every log, a 250-log Maple ~56 logs' worth, no
    tree ever more than 60). 0 in either row = every log full (the old way). Rows Skills -> Gathering.
  3 LEAVES: felled leaves x fell.leafXpFactor 1.0 -> 0.1 (a Maple's 1167 leaves paid 1167 XP - more than its new logs); a fraction is paid
    as a random whole XP with the exact average (XpEven.pay, like felled logs since 0.4.43; was Math.round). Hand-broken leaves unchanged.
  Per tree, base XP before Wisdom / catch-up: small Oak 926 -> 112, big Maple 31.2k -> 695, Gumboab 35k -> 1.8k, Redwood 112k -> 4.3k,
  Crystal 317k -> 23k (no gathering pace boost: gather.boost.skills is empty since 0.4.57; felled logs 100 % since 0.4.62).
  ONE-TIME UPDATE ForXpMig (PROJECT-RULES 4; P9Mig's reviewed machinery, copied): ONCE on an existing xp.properties, setup() right after the
    P9 updates, BEFORE SkillCfg.load, and only once the P3 + P9 updates have landed (else nothing, retried next start). Each key whose LAST
    entry is a one-line entry holding exactly the 0.4.66 default (block.Wood_*_Trunk[_Full] = the P3 tier value, suffix._Trunk[_Full]
    Foraging:35, fell.leafXpFactor 1.0) -> the 0.4.67 value (value text only); any other value kept (one INFO line); then ONE block in the
    file's own line ending: comment + fell.bigTreeFrom=30 + fell.bigTreeFalloff=2 (each only if absent) + the run-once marker "Foraging XP
    by tier (SkyySkills 0.4.67)". config-history copy first (verified), one config-changes.log row per change (Undo), Properties check,
    atomicWrite. A fresh file carries the new values + the marker.
  SAVED DATA: none (player XP untouched - Skyy keeps Foraging 50). ROLLBACK to 0.4.66: Server Setup -> Changes -> Undo the ForXpMig rows
  (or leave them: 0.4.66 reads the lower table and ignores the two big-tree keys), then the 0.4.66 jar.
'''

P = G.Patch(os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.66.py"), os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.67.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.4.66"') and P.has("tools/skills_0_4_66_patch.py") and not P.has("0.4.67 (2026-10-25)"), "not the generated SkyySkills 0.4.66 script"
REG0, SYS0, CLS0 = P.s.count("registerCommand("), P.s.count("registerSystem("), P.s.count("makeClass(")

P.rep('''"""SkyySkills 0.4.66 - GENERATED by tools/skills_0_4_66_patch.py from build_skyyskills_0.4.65.py (the SET pin) - edit the patch, not this file.
''', '''"""SkyySkills 0.4.67 - GENERATED by tools/skills_0_4_67_patch.py from build_skyyskills_0.4.66.py (the SET pin) - edit the patch, not this file.
''' + NOTE + '''
SkyySkills 0.4.66 - GENERATED by tools/skills_0_4_66_patch.py from build_skyyskills_0.4.65.py (the SET pin at that time).
''')
P.rep('VERSION = "0.4.66"', 'VERSION = "0.4.67"')

# ---- the class (made with the other one-time updates)
P.rep('''cp962 = pool.makeClass(PKG + ".CurveP9Mig")     # 0.4.62: the one-time saved-XP move to the P9 level list (Lv 61-100), levels kept
''', '''cp962 = pool.makeClass(PKG + ".CurveP9Mig")     # 0.4.62: the one-time saved-XP move to the P9 level list (Lv 61-100), levels kept
fx67 = pool.makeClass(PKG + ".ForXpMig")        # 0.4.67: the one-time Foraging XP by tier update of xp.properties (log rows, leaves, big trees)
''')

# ---- the plan + the fresh default file (Python twin of ForXpMig.plan for the default file's one-line entries)
P.rep('''DEFAULTS_LIT = json.dumps(DEFAULTS)   # valid Java string literal for ASCII text (\\n \\" \\\\ escapes)
''', '''# ================= 0.4.67 FORAGING XP BY TIER - the ForXpMig plan and the fresh default file (tools/skills_0_4_67_patch.py) =================
FX_PCT = [10] * 3 + [14] * 6 + [19] * 3 + [31] * 3   # each wood tier's log XP = this % of its P3 value (round half up, min 1) - tools/balance_model.py FX_PCT
FX_LOG = [max(1, (_x * _p + 50) // 100) for _x, _p in zip(P3_LOG, FX_PCT)]
assert FX_LOG == [4, 7, 12, 22, 34, 46, 56, 74, 91, 142, 174, 200, 372, 434, 496] and all(_a < _b for _a, _b in zip(FX_LOG, FX_LOG[1:])), FX_LOG
DEFAULTS_066 = DEFAULTS   # 0.4.67: the 0.4.66 default file
_dx67 = {}
for _ln in DEFAULTS_066.split("\\n"):
    _t = _ln.strip()
    if _t and not _t.startswith("#") and "=" in _t:
        assert _t.split("=", 1)[0].strip() not in _dx67 or not _t.startswith(("block.Wood_", "suffix._Trunk", "fell.leafXpFactor")), _t
        _dx67[_t.split("=", 1)[0].strip()] = _t.split("=", 1)[1].strip()
FX_KEYS = []   # (key, 0.4.66 default, 0.4.67 value, change-log row key)
for _t in sorted(_TT57.LOGS):
    for _w in _TT57.LOGS[_t]:
        for _suf in ("_Trunk", "_Trunk_Full"):
            _iid = "Wood_%s%s" % (_w, _suf)
            if _iid not in ITEM_IDS: continue
            assert _dx67.get("block." + _iid) == "Foraging:%d" % P3_LOG[_t - 1], (_iid, _dx67.get("block." + _iid))
            FX_KEYS.append(("block." + _iid, "Foraging:%d" % P3_LOG[_t - 1], "Foraging:%d" % FX_LOG[_t - 1], "block[%s]" % _iid))
for _suf in ("_Trunk", "_Trunk_Full"):
    assert _dx67.get("suffix." + _suf) == "Foraging:35", _suf
    FX_KEYS.append(("suffix." + _suf, "Foraging:35", "Foraging:%d" % FX_LOG[0], "suffix[%s]" % _suf))
assert _dx67.get("fell.leafXpFactor") == "1.0"
FX_LEAF = "0.1"
FX_KEYS.append(("fell.leafXpFactor", "1.0", FX_LEAF, "fell.leafXpFactor"))
FX_ADD = [("fell.bigTreeFrom", "30", "fell.bigTreeFrom"), ("fell.bigTreeFalloff", "2", "fell.bigTreeFalloff")]   # (key, value, row) - only if absent
FX_DEF = dict([(_k, _n) for _k, _o, _n, _r in FX_KEYS] + [(_k, _v) for _k, _v, _r in FX_ADD])
assert len(FX_KEYS) >= 2 * 30 and all(("\\n%s=" % _k) not in ("\\n" + DEFAULTS_066) for _k, _v, _r in FX_ADD)
FX_MARK_ID = "Foraging XP by tier (SkyySkills 0.4.67)"
FX_MARK = "# %s: log XP by wood tier, less for big trees, felled leaves x0.1" % FX_MARK_ID
FX_HEAD = ["", "# ---------- Foraging XP per log by wood tier, less for big trees - SkyySkills 0.4.67 ----------",
           "# Comments must stay on their own lines. Changed above (only lines still holding the 0.4.66 default): every wood tier's log XP",
           "# (block.Wood_*_Trunk) is lower: T1 Oak 4, T3 Maple 12, T6 46, T9 91, T12 200, T15 496; felled leaves pay fell.leafXpFactor 0.1.",
           "# Big trees: the first fell.bigTreeFrom logs of a felled tree pay full XP; each later log pays less (fell.bigTreeFalloff 2:",
           "# a tree pays at most about twice bigTreeFrom logs). 0 in either = every log full. All Foraging XP faster: xp.skillMult."]
for _t in FX_HEAD + [FX_MARK]:
    assert all(32 <= ord(_c) < 127 for _c in _t) and '"' not in _t and "\\\\" not in _t and (not _t or _t.startswith("# ")), _t
assert "=" not in FX_MARK and not any(_cre.match(r"#\\s*[A-Za-z][A-Za-z0-9._-]*\\s*[=:]\\s*\\S+\\s*$", _ln) for _ln in FX_HEAD)
FX_BLOCK = "\\n".join(FX_HEAD + ["%s=%s" % (_k, _v) for _k, _v, _r in FX_ADD] + [FX_MARK]) + "\\n"
_d67 = "\\n" + DEFAULTS_066
for _k, _o, _n, _r in FX_KEYS:
    assert _d67.count("\\n%s=%s\\n" % (_k, _o)) == 1 and _d67.count("\\n%s=" % _k) == 1, _k   # one line, the 0.4.66 default
    _d67 = _d67.replace("\\n%s=%s\\n" % (_k, _o), "\\n%s=%s\\n" % (_k, _n))
DEFAULTS = _d67[1:] + ("" if _d67.endswith("\\n") else "\\n") + FX_BLOCK
assert all(ord(ch) < 128 for ch in DEFAULTS) and len(DEFAULTS.encode("utf-8")) < 65000 and DEFAULTS.count(FX_MARK_ID) == 1, len(DEFAULTS)
# the Felled trees block a pre-0.4.2 file gets appended (FellCfg.ensureDefaults) carries the new leaf factor too
assert ("\\n" + FELL_DEFAULTS).count("\\nfell.leafXpFactor=1.0\\n") == 1
FELL_LIT = json.dumps(("\\n" + FELL_DEFAULTS).replace("\\nfell.leafXpFactor=1.0\\n", "\\nfell.leafXpFactor=" + FX_LEAF + "\\n")[1:])
print("0.4.67: Foraging XP update plan %d key(s) + %d line(s) appended; log XP by tier %s; default file %d bytes" % (len(FX_KEYS), len(FX_ADD), FX_LOG, len(DEFAULTS)))
DEFAULTS_LIT = json.dumps(DEFAULTS)   # valid Java string literal for ASCII text (\\n \\" \\\\ escapes)
''')

# ---- FellCfg: the big-tree fields + read + text; the new leaf default
P.rep('''for decl in ("boolean ENABLED = true", "boolean BROKEN = false", "double XP_FACTOR = 1.0", "boolean LEAVES = true", "double LEAF_XP_FACTOR = 1.0",
''', '''assert FX_LEAF == "0.1" and FX_DEF["fell.bigTreeFrom"] == "30" and FX_DEF["fell.bigTreeFalloff"] == "2"   # 0.4.67: the code defaults below
for decl in ("boolean ENABLED = true", "boolean BROKEN = false", "double XP_FACTOR = 1.0", "boolean LEAVES = true", "double LEAF_XP_FACTOR = 0.1",
             "int BIG_FROM = 30", "double BIG_FALLOFF = 2.0",   # 0.4.67: fell.bigTreeFrom / fell.bigTreeFalloff
''')
P.rep('''  LEAF_XP_FACTOR = clampD({PKG}.SkillCfg.dbl(p, "fell.leafXpFactor", 1.0), 0.0, 5.0);
''', '''  LEAF_XP_FACTOR = clampD({PKG}.SkillCfg.dbl(p, "fell.leafXpFactor", 0.1), 0.0, 5.0);   // 0.4.67: 1.0 -> 0.1
  BIG_FROM = (int) clampL({PKG}.SkillCfg.lng(p, "fell.bigTreeFrom", 30L), 0L, 1024L);   // 0.4.67: logs a felled tree pays in full
  BIG_FALLOFF = clampD({PKG}.SkillCfg.dbl(p, "fell.bigTreeFalloff", 2.0), 0.0, 4.0);   // 0.4.67: how fast later logs pay less
''')
P.rep('''  return "on (XP x" + XP_FACTOR + (LEAVES ? ", leaves x" + LEAF_XP_FACTOR : ", leaves not paid") + (DOUBLE_DROPS ? ", double drops" : "")''',
      '''  return "on (XP x" + XP_FACTOR + (LEAVES ? ", leaves x" + LEAF_XP_FACTOR : ", leaves not paid") + (BIG_FROM > 0 && BIG_FALLOFF > 0.0 ? ", big trees: " + BIG_FROM + " logs full, then (" + BIG_FROM + " / log)^" + BIG_FALLOFF : ", every log full") + (DOUBLE_DROPS ? ", double drops" : "")''')

# ---- FellCfg.share / creditR / credit (after XpEven, whose pay / FELL_PCT they use)
P.rep('''# ================= 0.4.39 SkSnd part 1 + RbStat part 1: fields, the xp.properties read, the pure helpers, the Server Setup check= hook
''', '''# ================= 0.4.67 FellCfg.share / creditR / credit: the Foraging XP of one felled block (FellCredit.one). k = the log's number in its
# tree (the chopped log = 1, so the first felled log is 2): past BIG_FROM logs a log pays (BIG_FROM / k) ^ BIG_FALLOFF of its XP (0 in either =
# full). Logs: table XP x fell.xpFactor x fell.otherLogsPercent (XpEven.FELL_PCT, as fellLog) x share; leaves: x fell.leafXpFactor. A fraction
# is paid as a random whole XP with the exact average (XpEven.pay; r in [0, 1) - ThreadLocalRandom in the game, fixed in the harness).
fcf.addMethod(CtNewMethod.make(J14(r"""
public static double share(int k) {
  int f = BIG_FROM;
  double p = BIG_FALLOFF;
  if (f <= 0 || !(p > 0.0) || k <= f) return 1.0;
  return Math.pow((double) f / (double) k, p);
}"""), fcf))
fcf.addMethod(CtNewMethod.make(J14(r"""
public static long creditR(long base, boolean leaf, int k, double r) {
  if (base <= 0L) return 0L;
  if (leaf) return @PKG@.XpEven.pay((double) base * LEAF_XP_FACTOR, r);
  double x = (double) base * XP_FACTOR;
  if (!(x > 0.0)) return 0L;
  @PKG@.XpEven.FELLED.incrementAndGet();
  return @PKG@.XpEven.pay(x * @PKG@.XpEven.FELL_PCT / 100.0 * share(k), r);
}"""), fcf))
fcf.addMethod(CtNewMethod.make(J14(r"""
public static long credit(long base, boolean leaf, int k) {
  return creditR(base, leaf, k, java.util.concurrent.ThreadLocalRandom.current().nextDouble());
}"""), fcf))
# ================= 0.4.39 SkSnd part 1 + RbStat part 1: fields, the xp.properties read, the pure helpers, the Server Setup check= hook
''')
P.rep('''      double fct = W.leaf[i] ? {PKG}.FellCfg.LEAF_XP_FACTOR : {PKG}.FellCfg.XP_FACTOR;
      long xp = W.leaf[i] ? Math.round((double) rule[1] * fct) : {PKG}.XpEven.fellLog((double) rule[1] * fct);   // 0.4.43: other logs x fell.otherLogsPercent
''', '''      long xp = {PKG}.FellCfg.credit(rule[1], W.leaf[i], W.cLogs + 2);   // 0.4.67: leaves x fell.leafXpFactor; logs x fell.xpFactor x fell.otherLogsPercent x the big-tree share (the chopped log = 1)
''')

# ---- ForXpMig = P9Mig's machinery (copied), its own constants + the P3 / P9 landed guard
_i0 = P.s.index("# ---- P9Mig (0.4.62, PROJECT-RULES section 4; BmMigP8c's reviewed machinery, copied)")
_i1 = P.s.index("# ---- CurveP9Mig (0.4.62, PROJECT-RULES section 4; CurveP3Mig's reviewed machinery, copied)")
_p9src = P.s[_i0:_i1]
_fx = _p9src
for _a, _b in (("p9m62", "fx67"), ("P9_MARK_ID", "FX_MARK_ID"), ("P9_MARK", "FX_MARK"), ("P9_HEAD", "FX_HEAD"),
               ('jarr([_e[0] for _e in P9_KEYS])', 'jarr([_e[0] for _e in FX_KEYS])'), ('jarr([_e[1] for _e in P9_KEYS])', 'jarr([_e[1] for _e in FX_KEYS])'),
               ('jarr([_e[2] for _e in P9_KEYS])', 'jarr([_e[2] for _e in FX_KEYS])'), ('jarr([_e[3] for _e in P9_KEYS])', 'jarr([_e[3] for _e in FX_KEYS])'),
               ('ADDK = %s;" % jarr([])', 'ADDK = %s;" % jarr([_e[0] for _e in FX_ADD])'), ('ADDV = %s;" % jarr([])', 'ADDV = %s;" % jarr([_e[1] for _e in FX_ADD])'),
               ('ADDR = %s;" % jarr([])', 'ADDR = %s;" % jarr([_e[2] for _e in FX_ADD])'),
               ('"SkyySkills 0.4.62"', '"SkyySkills 0.4.67"'), ("the 0.4.62 default has no such line", "the 0.4.67 default has no such line"),
               ('"the 0.4.62 (Balance P9) default is "', '"the 0.4.67 (Foraging XP by tier) default is "'),
               ("for 0.4.62 (Balance P9)", "for 0.4.67 (Foraging XP by tier)"), ("before the 0.4.62 Balance P9 update", "before the 0.4.67 Foraging XP update"),
               ("xp.properties updated for 0.4.62 (Balance P9: Beastmastery XP, Mining + felled log XP, catch-up, levels 61-100, past-life list): ",
                "xp.properties updated for 0.4.67 (Foraging XP by wood tier, less for big trees, felled leaves x0.1): ")):
    assert _a in _fx, _a
    _fx = _fx.replace(_a, _b)
_fx = _fx.replace("# ---- P9Mig (0.4.62, PROJECT-RULES section 4; BmMigP8c's reviewed machinery, copied): ONCE on an EXISTING xp.properties, setup() right after\n"
                  "# CurveP9Mig.run (which moved the saved XP first), BEFORE SkillCfg.load. Each P9 key whose LAST entry is a one-line entry holding exactly the\n"
                  "# 0.4.61 default (OLDS) -> NEWS; any other value kept (INFO); no line = nothing written (the 0.4.62 code default applies). Then ONE block in the\n"
                  "# file's own line ending: HEAD + the marker (no new keys).",
                  "# ---- ForXpMig (0.4.67, PROJECT-RULES section 4; P9Mig's reviewed machinery, copied): ONCE on an EXISTING xp.properties, setup() right after\n"
                  "# the P9 updates, BEFORE SkillCfg.load, only once the P3 + P9 updates have landed (P3PEND / P9PEND off, P3Mig.plan + P9Mig.plan null; else\n"
                  "# nothing, retried next start). Each key whose LAST entry is a one-line entry holding exactly the 0.4.66 default (OLDS) -> NEWS; any other\n"
                  "# value kept (INFO); no line = nothing written (the 0.4.67 code default applies). Then ONE block in the file's own line ending: HEAD + the\n"
                  "# big-tree lines (ADDK, each only if absent) + the marker.")
_fx = _fx.replace("for 0.4.62 (Balance P9;", "for 0.4.67 (Foraging XP by tier;").replace("0.4.62", "0.4.67").replace("Balance P9", "Foraging XP by tier")
assert _fx.startswith("# ---- ForXpMig (0.4.67") and "P9_" not in _fx and "p9m62" not in _fx
_g0 = '''    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = plan(new String(old, "ISO-8859-1"));
    if (r == null) return "";
'''
_g1 = '''    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = plan(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    if (@PKG@.SkillCfg.P3PEND || @PKG@.SkillCfg.P9PEND || @PKG@.P3Mig.plan(new String(old, "ISO-8859-1")) != null || @PKG@.P9Mig.plan(new String(old, "ISO-8859-1")) != null) {
      @PKG@.SkillCfg.warn("xp.properties NOT updated for 0.4.67 (Foraging XP by tier) yet: the Balance P3 / P9 updates of the file have not landed (the next start tries again)");
      return "";
    }
'''
assert _fx.count(_g0) == 1
_fx = _fx.replace(_g0, _g1)
P.rep(_p9src[-300:] + "# ---- CurveP9Mig (0.4.62, PROJECT-RULES section 4; CurveP3Mig's reviewed machinery, copied)",
      _p9src[-300:] + _fx + "# ---- CurveP9Mig (0.4.62, PROJECT-RULES section 4; CurveP3Mig's reviewed machinery, copied)")

# ---- setup: right after the P9 updates, before SkillCfg.load
P.rep('''  if ({PKG}.CurveP9Mig.run(base)) {{ {PKG}.P9Mig.run(); {PKG}.CurveP9Mig.after(base); }}   // 0.4.62 Balance P9: saved XP on Lv 61-100 (levels kept) FIRST, then the 6 xp.properties defaults; once each
''', '''  if ({PKG}.CurveP9Mig.run(base)) {{ {PKG}.P9Mig.run(); {PKG}.CurveP9Mig.after(base); }}   // 0.4.62 Balance P9: saved XP on Lv 61-100 (levels kept) FIRST, then the 6 xp.properties defaults; once each
  {PKG}.ForXpMig.run();       // 0.4.67: untouched wood-tier log XP rows / trunk fallback / felled leaf factor -> the 0.4.67 values + the big-tree rows, once; History first
''')

# ---- Server Setup rows: the leaf default + the two big-tree rows (Skills -> Gathering)
P.rep('''    ("fell.leafXpFactor", "Felled leaf XP", "gathering", "dec", "1.0", "0", "5", "", "x", "live",
     "A falling leaf pays its hand-break XP times this.", "reload"),
''', '''    ("fell.leafXpFactor", "Felled leaf XP", "gathering", "dec", "0.1", "0", "5", "", "x", "live",   # 0.4.67: 1.0 -> 0.1
     "A falling leaf pays its hand-break XP times this (0.1 = 1 XP for every 10 leaves on average).", "reload"),
''')
P.rep('''assert sorted(_k for _k in set(_dp) | set(_dp61) if _dp.get(_k) != _dp61.get(_k) and _k != "tree.rally" and _k not in R66_DEF) == sorted(_e[0] for _e in P9_KEYS), "0.4.62: only the P9 keys moved (0.4.64: + the new Rally line; 0.4.66: + the R6 lines)"
assert all(_dp.get(_k) == _n and _dp61.get(_k) == _o for _k, _o, _n, _r in P9_KEYS) and DEFAULTS_063.endswith(P9_BLOCK) and DEFAULTS_065.endswith(G64_BLOCK) and DEFAULTS.endswith(G66_BLOCK)   # 0.4.62; 0.4.64: + the Rally block; 0.4.66: + the R6 block
''', '''assert sorted(_k for _k in set(_dp) | set(_dp61) if _dp.get(_k) != _dp61.get(_k) and _k != "tree.rally" and _k not in R66_DEF and _k not in FX_DEF) == sorted(_e[0] for _e in P9_KEYS), "0.4.62: only the P9 keys moved (0.4.64: + the new Rally line; 0.4.66: + the R6 lines; 0.4.67: + the Foraging XP lines)"
assert all(_dp.get(_k) == _n and _dp61.get(_k) == _o for _k, _o, _n, _r in P9_KEYS) and DEFAULTS_063.endswith(P9_BLOCK) and DEFAULTS_065.endswith(G64_BLOCK) and DEFAULTS_066.endswith(G66_BLOCK) and DEFAULTS.endswith(FX_BLOCK)   # 0.4.62; 0.4.64: + the Rally block; 0.4.66: + the R6 block; 0.4.67: + the FX block
assert all(_dp.get(_k) == _v for _k, _v in FX_DEF.items()) and sorted(_k for _k in set(_dp) | set(_dp61) if _k in FX_DEF and _dp.get(_k) != _dp61.get(_k)) == sorted(FX_DEF)   # 0.4.67
''')
P.rep('''assert all([_r[0] for _r in CFG_ROWS].count(_k) == 1 and ("%s=%s" % (_k, _v)) in DEFAULTS.split(chr(10)) for _k, _v in R66_KEYS)
''', '''assert all([_r[0] for _r in CFG_ROWS].count(_k) == 1 and ("%s=%s" % (_k, _v)) in DEFAULTS.split(chr(10)) for _k, _v in R66_KEYS)
# 0.4.67 (forxp): the big-tree rows (Skills -> Gathering), defaults = the FX block = the FellCfg code defaults
# fixer: placed right after "Felled leaf XP" (not at the end, after Ranching), so the Gathering page shows them with the other felled-tree rows
_ix67 = [_r[0] for _r in CFG_ROWS].index("fell.leafXpFactor")
CFG_ROWS.insert(_ix67 + 1, ("fell.bigTreeFrom", "Big trees: logs at full XP", "gathering", "int", FX_DEF["fell.bigTreeFrom"], "0", "1024", "", "", "live",
                 "A felled tree pays full XP for this many logs; each extra log after that pays less. 0 = all full.", "reload"))
CFG_ROWS.insert(_ix67 + 2, ("fell.bigTreeFalloff", "Big trees: how fast later logs drop", "gathering", "dec", FX_DEF["fell.bigTreeFalloff"], "0", "4", "", "", "live",
                 "Higher = later logs drop faster. 2 = a big tree pays at most about 2x its full logs. 0 = all full.", "reload"))
assert [_r[0] for _r in CFG_ROWS][_ix67:_ix67 + 3] == ["fell.leafXpFactor", "fell.bigTreeFrom", "fell.bigTreeFalloff"]
assert all([_r[0] for _r in CFG_ROWS].count(_k) == 1 and ("%s=%s" % (_k, _v)) in DEFAULTS.split(chr(10)) for _k, _v, _r in FX_ADD)
assert [_r[4] for _r in CFG_ROWS if _r[0] == "fell.leafXpFactor"] == [FX_LEAF]
''')

# ---- the new class goes into the jar with the others
P.rep('''lvc61, skm61, p9m62, cp962, lvf,''', '''lvc61, skm61, p9m62, cp962, fx67, lvf,''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0 and P.s.count("makeClass(") == CLS0 + 1
P.finish()
