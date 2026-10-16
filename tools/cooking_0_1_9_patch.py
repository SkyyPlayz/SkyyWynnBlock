"""Derive SkyyCooking/build_skyycooking_0.1.9.py from the LIVE SkyyCooking 0.1.8 (build_skyycooking_0.1.8.py = the tools/deploy_set.py SET pin,
DERIVED by tools/cooking_0_1_8_patch.py - never edit a generated script, edit this patch). Every anchor is asserted; at the end every change
is undone on a copy and compared with 0.1.8 (nothing else changed). Line endings kept.
Run:  python tools/cooking_0_1_9_patch.py   then   python SkyyCooking/build_skyycooking_0.1.9.py   (never --deploy)
Check: python SkyyCooking/test_skyycooking_0.1.9.py [--dir <folder inside tools/dev/scratch/>] [--keep]

0.1.9 = FOOD STRENGTH DURATION (lean round small01; docs/answered/skills.md 2026-10-16 "FOOD STRENGTH DURATION": popup Q "FOOD: mushroom
 dishes' Strength buff lasts a flat 6 min at every Grade, capped at +20% ..." -> Skyy: "scale with grade. 10 minuet cap").
 The Strength bar's over-time buff lasts 360 s x 2^(Grade/5) again (the same Grade rule as every other bar) but never longer than
 STRENGTH_DURATION_S = 600 s (10:00): G0 6:00, G1 6:54, G2 7:55, G3 9:05, G4+ 10:00. The +20 % Strength cap (OVER_CAP) stays. Build
 constants only (baked into the item assets like every food number); the tooltip's Strength line shows its own duration whenever the
 cap makes it shorter than the dish's "Duration:". No saved data, no id, no class logic changes (only the version texts).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

P = G.Patch(os.path.join(ROOT, "SkyyCooking", "build_skyycooking_0.1.8.py"), os.path.join(ROOT, "SkyyCooking", "build_skyycooking_0.1.9.py"))
assert P.has('VERSION = "0.1.8"\n') and P.has("DERIVED from build_skyycooking_0.1.7.py by tools/cooking_0_1_8_patch.py") and not P.has("FOOD STRENGTH DURATION"), \
    "not the generated SkyyCooking 0.1.8 script"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.1.9 = FOOD STRENGTH DURATION"):].rstrip() + "\n\n"

# ---------- docstring + version
P.rep('''"""SkyyCooking 0.1.8 - build script (javassist via jpype). DERIVED from build_skyycooking_0.1.7.py by tools/cooking_0_1_8_patch.py
(0.1.7 / 0.1.6 / 0.1.5 / 0.1.4 / 0.1.3 / 0.1.2 / 0.1.1 are derived the same way by tools/cooking_0_1_7_patch.py / _0_1_6_patch.py /
_0_1_5_patch.py / _0_1_4_patch.py / _0_1_3_patch.py / _0_1_2_patch.py / _0_1_1_patch.py): edit the patch and re-run it, not this file.
Run:   python build_skyycooking_0.1.8.py            -> SkyyCooking/SkyyCooking-0.1.8.jar
       (never --deploy: tools/deploy_set.py is the only deploy path - HANDOFF section 3)

''', '''"""SkyyCooking 0.1.9 - build script (javassist via jpype). DERIVED from build_skyycooking_0.1.8.py by tools/cooking_0_1_9_patch.py
(0.1.8 / 0.1.7 / 0.1.6 / 0.1.5 / 0.1.4 / 0.1.3 / 0.1.2 / 0.1.1 are derived the same way by tools/cooking_0_1_8_patch.py / _0_1_7_patch.py /
_0_1_6_patch.py / _0_1_5_patch.py / _0_1_4_patch.py / _0_1_3_patch.py / _0_1_2_patch.py / _0_1_1_patch.py): edit the patch and re-run it,
not this file.
Run:   python build_skyycooking_0.1.9.py            -> SkyyCooking/SkyyCooking-0.1.9.jar
       (never --deploy: tools/deploy_set.py is the only deploy path - HANDOFF section 3)

''' + NOTE)
P.rep('VERSION = "0.1.8"\n', 'VERSION = "0.1.9"\n')

# ---------- the Strength duration: Grade-scaled again, capped at 600 s
P.rep('''STRENGTH_DURATION_S = 360.0                            # critic 2 (open question for Skyy): Strength lasts a FLAT 360 s at every Grade -
STRENGTH_GRADE_DURATION = False                        #   no x2^(Grade/5) for the Strength bar (its strength still scales x(1 + 0.32 g))
''', '''STRENGTH_DURATION_S = 600.0                            # 0.1.9 (Skyy 2026-10-16: "scale with grade. 10 minuet cap"): Strength lasts
STRENGTH_GRADE_DURATION = True                         #   360 s x 2^(Grade/5) like every bar, but at most STRENGTH_DURATION_S (10:00)
''')
P.rep('''def bar_dur(bar, dur): return dur if (bar != "Strength" or STRENGTH_GRADE_DURATION) else STRENGTH_DURATION_S
''', '''def bar_dur(bar, dur):
    if bar != "Strength": return dur
    return min(dur, STRENGTH_DURATION_S) if STRENGTH_GRADE_DURATION else STRENGTH_DURATION_S   # 0.1.9: the 10 min cap
assert STRENGTH_GRADE_DURATION and STRENGTH_DURATION_S == 600.0, "0.1.9: Strength duration Grade-scaled, 10 min cap"
assert [bar_dur("Strength", 360.0), bar_dur("Strength", 360.0 * 2 ** 0.8), bar_dur("Health", 1900.0)] == [360.0, 600.0, 1900.0], "0.1.9 bar_dur"
''')
P.rep('''def fx_bullets(n):
''', '''def buff_dur(sn, dur):   # 0.1.9: the dish's "Duration:" = its longest buff (a Strength-only dish shows the 10 min cap)
    return max([bar_dur(b, dur) for b in sn] or [dur])
def fx_bullets(n):
''')
P.rep('''        body += " and grants:\\\\n\\\\n" + "\\\\n".join(bl) + "\\\\n\\\\nDuration: " + W % mmss(dur)
''', '''        body += " and grants:\\\\n\\\\n" + "\\\\n".join(bl) + "\\\\n\\\\nDuration: " + W % mmss(buff_dur(sn, dur))
''')
P.rep('''        out.append("• " + W % ("Strength +" + pct_s(v)) + " (%s%% more damage%s)" % (pct_s(v), "" if STRENGTH_GRADE_DURATION else ", for " + mmss(STRENGTH_DURATION_S)))
''', '''        sd = bar_dur("Strength", dur)   # 0.1.9: its own time only when the 10 min cap makes it shorter than the dish's Duration
        out.append("• " + W % ("Strength +" + pct_s(v)) + " (%s%% more damage%s)" % (pct_s(v), "" if abs(sd - buff_dur(sn, dur)) < 0.5 else ", for " + mmss(sd)))
''')
assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "no system / command added"
P.finish()
