"""Harness for SkyyAccessories 0.5.26 (tools/accessories_0_5_26_patch.py = Movement 2, the SkyyAccessories copy of the shared kit
tools/skyymove.py). Lean on purpose: no Java line of the script changes, only MoveSync (rebuilt from the kit) and the version texts. Build first:
    python tools/accessories_0_5_26_patch.py && python SkyyAccessories/build_skyyaccessories_0.5.26.py
    python SkyyAccessories/test_skyyaccessories_0.5.26.py
  P / J / K  tools/skyymove_test.applier_round: the patch re-runs byte-identical; the jar 0.5.25 -> 0.5.26 adds / removes nothing and changes only
       MoveSync, the plugin class, the kit's CfgRows / CfgFn + manifest; the kit checks on THIS jar's MoveSync
  NOT COVERED: a booted engine (run test_skyyaccessories_0.5.25.py for the older checks - unchanged code), the ride in game (Skyy's test).
Exit code 1 on any failure.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyymove_test as T

ALLOWED = ["manifest.json"] + ["com/skyy/accessories/%s.class" % c for c in ("MoveSync", "SkyyAccessoriesPlugin", "CfgRows", "CfgFn")]
sys.exit(T.applier_round("SkyyAccessories", os.path.join(ROOT, "tools", "accessories_0_5_26_patch.py"),
                         os.path.join(HERE, "build_skyyaccessories_0.5.26.py"), os.path.join(HERE, "SkyyAccessories-0.5.25.jar"),
                         os.path.join(HERE, "SkyyAccessories-0.5.26.jar"), "com.skyy.accessories.MoveSync", ALLOWED))
