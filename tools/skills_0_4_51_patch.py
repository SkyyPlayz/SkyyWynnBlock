"""Derive SkyySkills/build_skyyskills_0.4.51.py from the GENERATED SkyySkills 0.4.50 (build_skyyskills_0.4.50.py = the tools/deploy_set.py SET
pin; 0.4.50 came from 0.4.49 by tools/skills_0_4_50_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). rep(old, new) with asserted single anchors; at the end every change is undone on a copy and compared with
0.4.50 (nothing else changed); 0.4.50 stays untouched, its line endings are kept (tools/soundpass_gen.Patch).
Run:  python tools/skills_0_4_51_patch.py   then   python SkyySkills/build_skyyskills_0.4.51.py   (never --deploy)
      then  python SkyySkills/test_skyyskills_0.4.51.py   (+ python tools/skyymove_test.py for the movement kit)
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

NOTE = '''0.4.51 (2026-10-18) = MOVEMENT 2, the SkyySkills copy (research/Armory-Movement-Conflict.md; Skyy 2026-10-09 docs/answered/gear.md: "yes,
  lock the armory jump system. we can edit theirs to work with our mods instead of clashing." = absorbed at runtime, nothing of The Armory edited).
  No Java line of this script changes: MoveSync is rebuilt from the shared kit tools/skyymove.py, which now (A) counts strikes / pauses PER FIELD
  (The Armory's JumpHeightModifierSystem resets jumpForce every tick for every player - that no longer pauses the Acrobatics SPEED bonus) and
  (B) when The Armory's Jump_Height stat exists, puts the Acrobatics jump (plus every other source's) on that stat as ONE additive MAX modifier
  skyy_move_jump, solved so their own system writes default x their multiplier x ours (The Armory 1.23.0 bytecode verified,
  tools/skyymove_test.py); calibrated on the live value, 3 misses -> that player falls back to (A). The switch move.armoryJump (ride | yield)
  lives in SkyyGear 0.3.24's Server Setup (bridge move:cfg:armoryJump); this jar only reads it. Double jump reads the live jumpForce as before
  (The Armory's write now carries our bonus).
  ROLLBACK to 0.4.50: set SkyyGear's move.armoryJump = yield first; roll SkyyGear 0.3.24 + SkyyAccessories 0.5.26 back together (every applier
  must run the same rule, or the old copies pause speed again on a jump fight). No saved data of ours.
'''

P = G.Patch(os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.50.py"), os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.51.py"))
assert P.has('VERSION = "0.4.50"') and P.has("Fl50Mig") and not P.has("MOVEMENT 2"), "not the generated SkyySkills 0.4.50 script"
REG0, SYS0 = P.s.count("registerCommand("), P.s.count("registerSystem(")

P.rep('''"""SkyySkills 0.4.50 - build script (derived from the generated 0.4.49 by tools/skills_0_4_50_patch.py - edit the patch, not this file;
''', '''"""SkyySkills 0.4.51 - build script (derived from the generated 0.4.50 by tools/skills_0_4_51_patch.py - edit the patch, not this file;
''' + NOTE + '''  CHECKED: SkyySkills/test_skyyskills_0.4.51.py.
0.4.50 was derived from the generated 0.4.49 by tools/skills_0_4_50_patch.py;
''')
P.rep('VERSION = "0.4.50"', 'VERSION = "0.4.51"')
P.rep('''MV.add_move_sync(mvs_, CtField, CtNewMethod, PKG + ".SkillCfg.warn")
''', '''MV.add_move_sync(mvs_, CtField, CtNewMethod, PKG + ".SkillCfg.warn")
assert MV.RIDE_KEY == "skyy_move_jump" and MV.CFG_RIDE == "move:cfg:armoryJump"          # 0.4.51 Movement 2: the kit with the per-field rule + the ride
''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0, "command / system registrations changed"
P.finish()
