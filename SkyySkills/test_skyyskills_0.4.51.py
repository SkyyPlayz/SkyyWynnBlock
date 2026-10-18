"""Harness for SkyySkills 0.4.51 (tools/skills_0_4_51_patch.py = Movement 2, the SkyySkills copy of the shared kit tools/skyymove.py). Lean on
purpose: no Java line of the script changes, only MoveSync (rebuilt from the kit) and the version texts. Build first:
    python tools/skills_0_4_51_patch.py && python SkyySkills/build_skyyskills_0.4.51.py
    python SkyySkills/test_skyyskills_0.4.51.py
  P / J / K  tools/skyymove_test.applier_round: the patch re-runs byte-identical; the jar 0.4.50 -> 0.4.51 adds / removes nothing and changes only
       MoveSync, the version-text classes (plugin, SkillCfg, ManaGuard, the kit's CfgRows / CfgFn) + manifest; the kit checks on THIS jar's MoveSync
  X  MoveSync keeps the 0.4.32 lock-free bridge (BRIDGE field + bridge0) next to the ride (skyy_move_jump)
  NOT COVERED: a booted engine (run test_skyyskills_0.4.50.py for the older checks - unchanged code), the ride in game (Skyy's test).
Exit code 1 on any failure.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyymove_test as T


def extra(z, check):
    b = z.read("com/skyy/skills/MoveSync.class")
    check(b"BRIDGE" in b and b"bridge0" in b and b"skyy_move_jump" in b and b"move:cfg:armoryJump" in b,
          "X: MoveSync = the 0.4.32 lock-free bridge + the Movement 2 ride")


ALLOWED = ["manifest.json"] + ["com/skyy/skills/%s.class" % c for c in ("MoveSync", "SkyySkillsPlugin", "SkillCfg", "ManaGuard", "CfgRows", "CfgFn")]
sys.exit(T.applier_round("SkyySkills", os.path.join(ROOT, "tools", "skills_0_4_51_patch.py"), os.path.join(HERE, "build_skyyskills_0.4.51.py"),
                         os.path.join(HERE, "SkyySkills-0.4.50.jar"), os.path.join(HERE, "SkyySkills-0.4.51.jar"), "com.skyy.skills.MoveSync",
                         ALLOWED, extra))
