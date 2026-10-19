"""Derive SkyyCooking/build_skyycooking_0.1.13.py from the LIVE SkyyCooking 0.1.12 (build_skyycooking_0.1.12.py = the tools/deploy_set.py SET
pin, DERIVED by tools/cooking_0_1_12_patch.py - never edit a generated script, edit this patch). Every anchor is asserted; at the end every
change is undone on a copy and compared with 0.1.12 (nothing else changed). Line endings kept.
Run:  python tools/cooking_0_1_13_patch.py   then   python SkyyCooking/build_skyycooking_0.1.13.py   (never --deploy)
Check: python SkyyCooking/test_skyycooking_0.1.13.py [--dir <folder inside tools/dev/scratch/>] [--keep]

0.1.13 = NO XP CAPS (lean round xpc). SKYY'S WORDS (docs/answered/skills.md 2026-10-18 'NO XP CAPS'): "is there a cap on acrobatics xp
 gain? or any other xp gain? if so remove all caps" -> every XP gain cap goes (0 = no cap); 2026-10-19: "work through the bugs one at a time
 until you run out". SkySkills 0.4.53 did its own caps; this is the Cooking part (RESUME: "XP caps in Cooking / Guilds / Exploration -> 0").
 1. THE ONE COOKING XP CAP: maxXpPerMinute (base Cooking XP per player per minute, bench dishes + Campfire accessory batches share it) -
    default 1,500,000 -> 0. 0 already meant "no cap" (Cook.allowXp / allowXpPart return at once, the row's help says "0 = no cap"), so no
    code path changes: only the default (row, loader fallback CookCfg.DEF_MAX_PER_MIN, field, the generated cooking.properties line).
    Nothing else in SkyyCooking caps XP (campfire.xpFactor is a share, not a cap; the Supplies / Grade / effect caps are not XP).
 2. ONE-TIME UPDATE of an existing cooking.properties (new class CookNcMig = CookXpMig's reviewed text step, same CookMig.kit / saved /
    logLine machinery; setup() runs CookMig -> CookXpMig -> CookTblMig -> CookIngMig -> CookNcMig -> CookCfg.load -> CfgPub.start): a
    one-line maxXpPerMinute entry still holding the old default 1500000 becomes 0 (value text only: key, separator, CR kept); a hand-set
    value is kept and logged (INFO "... kept (custom)"); no line = nothing (the default 0 applies). History copy "before the 0.1.13 no XP
    caps update" first, verified byte for byte (else WARN, file untouched, the next start tries again); one config-changes.log line
    (Server Setup -> Changes -> Undo); run-once marker NC_MARK above the entry's help comment (a fresh file carries it). Bytes and line
    endings kept (ISO-8859-1 in and out, CR per line as found).
 3. The build's own self-check of Cook.allowXpPart now sets the old 1.5M window for its test and checks that 0 pays a whole batch.
 ROLLBACK to 0.1.12: plain (redeploy SkyyCooking-0.1.12.jar). 0.1.12 reads maxXpPerMinute=0 as "no cap" too; to bring the old cap back
    Undo the 0.1.13 line in Server Setup -> Changes (or set XP cap per minute = 1500000). No saved-data change.
"""
import os, sys, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

P = G.Patch(os.path.join(ROOT, "SkyyCooking", "build_skyycooking_0.1.12.py"), os.path.join(ROOT, "SkyyCooking", "build_skyycooking_0.1.13.py"))
assert P.has('VERSION = "0.1.12"\n') and P.has("DERIVED from build_skyycooking_0.1.11.py by tools/cooking_0_1_12_patch.py") and not P.has("CookNcMig"), \
    "not the generated SkyyCooking 0.1.12 script"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.1.13 = NO XP CAPS"):].rstrip() + "\n\n"

# ---------- docstring + version
P.rep('''"""SkyyCooking 0.1.12 - build script (javassist via jpype). DERIVED from build_skyycooking_0.1.11.py by tools/cooking_0_1_12_patch.py
(0.1.11 / 0.1.10 / 0.1.9 / 0.1.8 / 0.1.7 / 0.1.6 / 0.1.5 / 0.1.4 / 0.1.3 / 0.1.2 / 0.1.1 are derived the same way by
tools/cooking_0_1_11_patch.py / _0_1_10_patch.py / _0_1_9_patch.py / _0_1_8_patch.py / _0_1_7_patch.py / _0_1_6_patch.py / _0_1_5_patch.py /
_0_1_4_patch.py / _0_1_3_patch.py / _0_1_2_patch.py / _0_1_1_patch.py): edit the patch and re-run it, not this file.
Run:   python build_skyycooking_0.1.12.py           -> SkyyCooking/SkyyCooking-0.1.12.jar
       (never --deploy: tools/deploy_set.py is the only deploy path - HANDOFF section 3)

''', '''"""SkyyCooking 0.1.13 - build script (javassist via jpype). DERIVED from build_skyycooking_0.1.12.py by tools/cooking_0_1_13_patch.py
(0.1.12 / 0.1.11 / 0.1.10 / 0.1.9 / 0.1.8 / 0.1.7 / 0.1.6 / 0.1.5 / 0.1.4 / 0.1.3 / 0.1.2 / 0.1.1 are derived the same way by
tools/cooking_0_1_12_patch.py / _0_1_11_patch.py / _0_1_10_patch.py / _0_1_9_patch.py / _0_1_8_patch.py / _0_1_7_patch.py / _0_1_6_patch.py /
_0_1_5_patch.py / _0_1_4_patch.py / _0_1_3_patch.py / _0_1_2_patch.py / _0_1_1_patch.py): edit the patch and re-run it, not this file.
Run:   python build_skyycooking_0.1.13.py           -> SkyyCooking/SkyyCooking-0.1.13.jar
       (never --deploy: tools/deploy_set.py is the only deploy path - HANDOFF section 3)

''' + NOTE)
P.rep('VERSION = "0.1.12"\n', 'VERSION = "0.1.13"\n')

# ---------- 1. the default 1,500,000 -> 0 (= no cap; every use of MAX_PER_MIN already reads <= 0 as "no cap")
P.rep('''MAX_PER_MIN = 1500000
assert max(XP.values()) <= 400000 and MAX_PER_MIN <= 3000000, "XP must stay under skill:fn:addxp's 500k/call and 3M/min caps"
''', '''MAX_PER_MIN = 1500000
assert max(XP.values()) <= 400000 and MAX_PER_MIN <= 3000000, "XP must stay under skill:fn:addxp's 500k/call and 3M/min caps"
MAX_PER_MIN_OLD = MAX_PER_MIN   # 0.1.13: the old default CookNcMig moves to 0 once
MAX_PER_MIN = 0                 # 0.1.13 NO XP CAPS (Skyy 2026-10-18: "if so remove all caps"): 0 = no cap
''')
# the run-once marker (a fresh file carries it, right above the entry's help comment - where CookNcMig puts it)
P.rep('''XP_MARK_ID = "SkyyCooking 0.1.4 Cooking XP"
''', '''XP_MARK_ID = "SkyyCooking 0.1.4 Cooking XP"
# 0.1.13 run-once marker of the no XP caps update (CookNcMig): own line, plain ASCII, no '=' (never a #key=value template line)
NC_MARK_ID = "SkyyCooking 0.1.13 no XP caps"
NC_MARK = "# SkyyCooking 0.1.13 no XP caps (Skyy 2026-10-18: remove all caps) - a maxXpPerMinute line still on the old default 1500000 was set to 0 once (0 means no cap)"
assert all(32 <= ord(_c) < 127 for _c in NC_MARK) and "=" not in NC_MARK and NC_MARK.startswith("# " + NC_MARK_ID)
''')
P.rep('''      "# safety net: base Cooking XP per player per minute (counted before xpMultiplier); 0 = off. The dish is always given.",
      "maxXpPerMinute=%d" % MAX_PER_MIN,''', '''      NC_MARK,   # 0.1.13
      "# safety net: base Cooking XP per player per minute (counted before xpMultiplier); 0 = off. The dish is always given.",
      "maxXpPerMinute=%d" % MAX_PER_MIN,''')

# ---------- 2. CookNcMig = CookXpMig's text step + migrate for maxXpPerMinute (cloned from the script's own reviewed class)
_a = P.s.index("xmig = pool.makeClass(PKG + \".CookXpMig\")")
_b = P.s.index("# ================= CookTblMig (0.1.5)")
XB = P.s[_a:_b]
assert XB.count('Mk(xmig, r"""') == 3 and "public static synchronized String migrate()" in XB
NB = XB.replace("xmig", "nmig")
for _o, _n in (
        ('nmig = pool.makeClass(PKG + ".CookXpMig")', 'nmig = pool.makeClass(PKG + ".CookNcMig")'),
        ('F(nmig, "public static final String KEY = \\"xpMultiplier\\";")', 'F(nmig, "public static final String KEY = \\"maxXpPerMinute\\";")'),
        ('F(nmig, "public static final String OLD = %s;" % json.dumps(XP_MULT_OLD[0]))      # "1.0": every generated cooking.properties since 0.1',
         'F(nmig, "public static final String OLD = %s;" % json.dumps(str(MAX_PER_MIN_OLD)))   # "1500000": every generated cooking.properties up to 0.1.12'),
        ('F(nmig, "public static final String OLD2 = %s;" % json.dumps(XP_MULT_OLD[1]))     # "1": the kit\'s canonical write of the old default',
         'F(nmig, "public static final String OLD2 = %s;" % json.dumps(str(MAX_PER_MIN_OLD)))  # the kit writes a long the same way'),
        ('F(nmig, "public static final String NEW = %s;" % json.dumps(repr(XP_MULT_DEF)))', 'F(nmig, "public static final String NEW = %s;" % json.dumps(str(MAX_PER_MIN)))'),
        ('before the 0.1.4 Cooking XP update', 'before the 0.1.13 no XP caps update'),
        ('json.dumps(XP_MARK))', 'json.dumps(NC_MARK))'),
        ('json.dumps(XP_MARK_ID))', 'json.dumps(NC_MARK_ID))'),
        (' kept (custom) - the 0.1.4 default is " + NEW', ' kept (custom) - the 0.1.13 default is " + NEW + " (no cap)"'),
        ('"cooking.properties NOT updated to the 0.1.4 Cooking XP default: ', '"cooking.properties NOT updated for 0.1.13 (no XP caps): '),
        ('msg = "cooking.properties updated to the 0.1.4 Cooking XP default: " + chg + " (Skyy 2026-10-02: cooking levelled too fast - every Cooking XP award is halved; the old file is in config-history; Server Setup -> Changes can undo it)";',
         'msg = "cooking.properties updated for 0.1.13: " + chg + " (Skyy 2026-10-18: no XP caps - 0 means no cap; the old file is in config-history; Server Setup -> Changes can undo it)";'),
        ('msg = "cooking.properties: xpMultiplier was changed by hand - kept, nothing changed (0.1.4 Cooking XP marker added)";',
         'msg = "cooking.properties: maxXpPerMinute was changed by hand - kept, nothing changed (0.1.13 no XP caps marker added)";'),
        ('msg = "cooking.properties: no xpMultiplier line (the default " + NEW + " applies) - nothing changed (0.1.4 Cooking XP marker added)";',
         'msg = "cooking.properties: no maxXpPerMinute line (the default " + NEW + " = no cap applies) - nothing changed (0.1.13 no XP caps marker added)";'),
        ('msg = "cooking.properties: xpMultiplier is already " + NEW + " - kept, nothing changed (0.1.4 Cooking XP marker added)";',
         'msg = "cooking.properties: maxXpPerMinute is already " + NEW + " (no cap) - kept, nothing changed (0.1.13 no XP caps marker added)";'),
        ('"could not update cooking.properties to the 0.1.4 Cooking XP default (the file is used as it is): "',
         '"could not update cooking.properties for 0.1.13 (no XP caps; the file is used as it is): "')):
    assert NB.count(_o) == 1, "0.1.13 CookNcMig clone anchor: %s" % _o[:100]
    NB = NB.replace(_o, _n)
_code = "\n".join(ln for ln in NB.split("\n") if not ln.startswith("#"))
for _bad in ("xpMultiplier", "0.1.4", "XP_MULT", "XP_MARK"):
    assert _bad not in _code, "0.1.13 clone code still says " + _bad + ": " + str([l for l in _code.split("\n") if _bad in l])
NB = NB.replace("# (CookXpMig.migrate below; 0.1.5 CookTblMig follows it)", "# (CookNcMig.migrate below)")
P.rep("# ================= CookTblMig (0.1.5)", "# ================= CookNcMig (0.1.13): the one-time maxXpPerMinute 1500000 -> 0 update (no XP caps) - a clone of CookXpMig "
      "(the same text step and History / change-log path), see the header =================\n" + NB + "# ================= CookTblMig (0.1.5)")
P.rep('''  @PKG@.CookIngMig.migrate();
  String s = @PKG@.CookCfg.load();''', '''  @PKG@.CookIngMig.migrate();
  @PKG@.CookNcMig.migrate();   // 0.1.13: an untouched maxXpPerMinute 1500000 -> 0 (no cap), once; History first
  String s = @PKG@.CookCfg.load();''')
P.rep("for c in (cfg, hk, mig, xmig, tmig, imig, ck,", "for c in (cfg, hk, mig, xmig, tmig, imig, nmig, ck,")

# ---------- 3. the build's self-check of the per-minute window: test it at the old 1.5M, then 0 = the whole batch
P.rep('''_cap = int(_JCfg.MAX_PER_MIN)
_uu = jpype.JClass("java.util.UUID").randomUUID()''', '''_cap = MAX_PER_MIN_OLD               # 0.1.13: the default is 0 (no cap) - the window logic is checked at the old 1.5M
_JCfg.MAX_PER_MIN = _cap
_uu = jpype.JClass("java.util.UUID").randomUUID()''')
P.rep('''    raise SystemExit("self-check 0.1.1: compiled Cook.allowXpPart drops a whole batch that is bigger than the window")
''', '''    raise SystemExit("self-check 0.1.1: compiled Cook.allowXpPart drops a whole batch that is bigger than the window")
_JCfg.MAX_PER_MIN = MAX_PER_MIN
_uu = jpype.JClass("java.util.UUID").randomUUID()
if MAX_PER_MIN != 0 or int(_JCfg.DEF_MAX_PER_MIN) != 0 or int(_JCook.allowXpPart(_uu, 50000000)) != 50000000 or not bool(_JCook.allowXp(_uu, 90000000)):
    raise SystemExit("self-check 0.1.13: maxXpPerMinute default 0 must pay every batch / dish (no cap)")
''')
# a self-check of the compiled CookNcMig text step on the shapes it meets (the harness runs migrate() on real files)
P.rep('''_sdl = [str(_JCook.sd(g)) for g in _G13]''', '''_JNm = jpype.JClass(PKG + ".CookNcMig", loader=_ld)
def _nm(t):
    r = _JNm.update(t)
    return None if r is None else (str(r[0]), str(r[1]), None if r[2] is None else str(r[2]), [str(x) for x in r[3]], None if r[4] is None else str(r[4]))
_NCN, _NCO = "maxXpPerMinute=0\\n", "maxXpPerMinute=1500000\\n"
if DEFAULTS_TEXT.count(_NCN) != 1 or DEFAULTS_TEXT.count(NC_MARK + "\\n# safety net:") != 1 or _JNm.update(DEFAULTS_TEXT) is not None:
    raise SystemExit("self-check 0.1.13: the default text must carry maxXpPerMinute=0 with the marker above its help line (and stay untouched)")
_f012 = DEFAULTS_TEXT.replace(NC_MARK + "\\n", "").replace(_NCN, _NCO)
for _nl in ("\\n", "\\r\\n"):
    if _nm(_f012.replace("\\n", _nl)) != (DEFAULTS_TEXT.replace("\\n", _nl), "maxXpPerMinute 1500000 -> 0", None, ["maxXpPerMinute", "1500000", "0"], "1500000"):
        raise SystemExit("self-check 0.1.13: CookNcMig.update of a 0.1.12 file (%r) is not the 0.1.13 default text" % _nl)
for _v in ("2000000", "0", "750000"):
    _note = None if _v == "0" else "maxXpPerMinute=%s kept (custom) - the 0.1.13 default is 0 (no cap)" % _v
    if _nm(_f012.replace(_NCO, "maxXpPerMinute=%s\\n" % _v)) != (DEFAULTS_TEXT.replace(_NCN, "maxXpPerMinute=%s\\n" % _v), "", _note, [], _v):
        raise SystemExit("self-check 0.1.13: a hand-set maxXpPerMinute=%s must be kept (marker only)" % _v)
print("0.1.13 checks: maxXpPerMinute default 0 (no cap); CookNcMig.update: 0.1.12 file LF / CRLF -> the 0.1.13 default text, hand-set kept, marked file untouched")
_sdl = [str(_JCook.sd(g)) for g in _G13]''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.1.13: no system / command added"
P.finish()
