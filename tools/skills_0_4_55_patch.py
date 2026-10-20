"""Derive SkyySkills/build_skyyskills_0.4.55.py from the GENERATED SkyySkills 0.4.54 (build_skyyskills_0.4.54.py = the tools/deploy_set.py SET
pin; 0.4.54 came from 0.4.53 by tools/skills_0_4_54_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). rep(old, new) with asserted single anchors; at the end every change is undone on a copy and compared with
0.4.54 (nothing else changed); 0.4.54 stays untouched, its line endings are kept (tools/soundpass_gen.Patch).
Run:  python tools/skills_0_4_55_patch.py   then   python SkyySkills/build_skyyskills_0.4.55.py   (never --deploy)
      then  python SkyySkills/test_skyyskills_0.4.55.py
Deploys TOGETHER with SkyyTrees 0.4.0 (Skill Trees 3), SkyyClasses 0.1.42 and SkyyMenu 0.3.41.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

NOTE = '''0.4.55 (2026-10-20) = SKILL TREES 3 + THE LEVEL CAP STOPS AT 100 (the SkyySkills part of the Skill Trees 3 round; with SkyyTrees 0.4.0).
  Skyy (2026-10-18): "allow rebirths past 5 so you can keep upgrading. but leave the lvl cap at 100 for now till we add more zones." + "drop
  the dust".
  1. LEVEL CAP: CHECKED, no code change needed - since 0.4.53 SkillCap.capT clamps every rebirth-reset skill's cap (levels.runCap 50 +
     SkyyRebirth's raise, 10 a rebirth) at levels.capMax (100), so rebirth 6, 7 ... 1000 stay at 100 (the "110 at rebirth 6" was the 0.4.53
     harness docstring's plan line written before levels.capMax; its LC check already proves 100). Rebirths are unlimited in SkyyRebirth
     0.3.6 (rebirth.max 0); nothing here counts or caps them (the level coins x rebirth.coinFactor ^ n only shrink). test_skyyskills_0.4.55.py
     proves 100 for every rebirth-reset slot at rebirth 6 - 1000 (+ the floor rule and the no-clamp setting) on this jar. The ready line now
     names the clamp.
  2. DUST: SkyySkills never had a Token / Dust function of its own - skill:fn:xp stays (SkyyPets reads it, SkyyTrees 0.4.0 reads it ONCE for
     its one-time Dust coin refund); its comment says so.
  No saved-data, config, command or bridge change. ROLLBACK to 0.4.54: identical behaviour.
'''

P = G.Patch(os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.54.py"), os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.55.py"))
assert P.has('VERSION = "0.4.54"') and P.has("En54Mig"), "not the generated SkyySkills 0.4.54 script"
REG0, SYS0 = P.s.count("registerCommand("), P.s.count("registerSystem(")

P.rep('''"""SkyySkills 0.4.54 - build script (derived from the generated 0.4.53 by tools/skills_0_4_54_patch.py - edit the patch, not this file;
''', '''"""SkyySkills 0.4.55 - build script (derived from the generated 0.4.54 by tools/skills_0_4_55_patch.py - edit the patch, not this file;
''' + NOTE + '''  CHECKED: SkyySkills/test_skyyskills_0.4.55.py.
0.4.54 was derived from the generated 0.4.53 by tools/skills_0_4_54_patch.py;
''')
P.rep('VERSION = "0.4.54"', 'VERSION = "0.4.55"')
P.rep('''# 3+ letter prefix names, "Combat" = the current class skill; unknown -> 0). SkyyTrees computes Dust from it. Any thread.''',
      '''# 3+ letter prefix names, "Combat" = the current class skill; unknown -> 0). SkyyPets reads it; SkyyTrees 0.4.0 (Skill Trees 3, no Dust any
# more) reads it ONCE per profile for its one-time Dust coin refund. Any thread.''')
P.rep('''", XP past max counts (skill:fn:run), Exploration never resets"''',
      '''" (never above levels.capMax " + {PKG}.SkillDefs.CAP_MAX + " - 0 = no clamp; rebirths unlimited), XP past max counts (skill:fn:run), Exploration never resets"''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0, "command / system registrations changed"
P.finish()
print("wrote SkyySkills/build_skyyskills_0.4.55.py (%d changes)" % len(P.changes))
