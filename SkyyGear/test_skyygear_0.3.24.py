"""Harness for SkyyGear 0.3.24 (tools/gear_0_3_24_patch.py = Movement 2 + the A2 weapons in the bags). Lean on purpose: 0.3.24 changes no
system / command / class, only GearMove (the shared kit tools/skyymove.py), the move.armoryJump row and the loot pool tables. Build first:
    python tools/gear_0_3_24_patch.py && python SkyyGear/build_skyygear_0.3.24.py
    python SkyyGear/test_skyygear_0.3.24.py
  P / J / K  tools/skyymove_test.applier_round: the patch re-runs byte-identical; the jar 0.3.23 -> 0.3.24 adds / removes nothing and changes only
       GearMove, GearCfg, GearPool, GearUt, the kit's CfgRows / CfgFn / CfgFile, the plugin class + manifest; the kit checks (The Armory's
       fromMaxima, the ride solve, the per-field strikes) on THIS jar's GearMove
  X  the row move.armoryJump (CfgRows) + GearCfg publishing move:cfg:armoryJump; the 72 A2 ids in GearPool, the 64 crafted ones in GearUt
       (CRAFTED) and not the 8 spears (drop-only); the 8 shields nowhere (not gear)
  NOT COVERED: a booted engine (the 0.3.23 harness chain is unchanged code - run it for the older checks), the ride in game (Skyy's test).
Exit code 1 on any failure.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyymove_test as T

METALS = ["Lead", "Dusk", "Chromium", "Azurvane", "Slag", "Cinder", "Titanium", "Lumen"]
FAMS = ["Sword", "Longsword", "Axe", "Battleaxe", "Mace", "Club", "Daggers", "Spear", "Shortbow"]
POOL = ["Weapon_%s_%s_SkyWynn" % (f, m) for f in FAMS for m in METALS]
SPEARS = [i for i in POOL if i.startswith("Weapon_Spear_")]
SHIELDS = ["Weapon_Shield_%s_SkyWynn" % m for m in METALS]


def extra(z, check):
    b = dict((n, z.read(n)) for n in ("com/skyy/gear/CfgRows.class", "com/skyy/gear/GearCfg.class", "com/skyy/gear/GearPool.class",
                                      "com/skyy/gear/GearUt.class"))
    check(b"move.armoryJump" in b["com/skyy/gear/CfgRows.class"], "X: Server Setup row move.armoryJump")
    check(b"move:cfg:armoryJump" in b["com/skyy/gear/GearCfg.class"], "X: GearCfg publishes move:cfg:armoryJump")
    check(all(i.encode() in b["com/skyy/gear/GearPool.class"] for i in POOL), "X: the 72 A2 ids are in the bag pool (GearPool)")
    check(all(i.encode() in b["com/skyy/gear/GearUt.class"] for i in POOL if i not in SPEARS), "X: the 64 crafted A2 ids are CRAFTED (GearUt)")
    check(not any(i.encode() in b["com/skyy/gear/GearUt.class"] for i in SPEARS), "X: the 8 spears are drop-only (not CRAFTED)")
    allb = b"".join(z.read(n) for n in z.namelist() if n.endswith(".class"))
    check(not any(i.encode() in allb for i in SHIELDS), "X: the 8 A2 shields are not gear (no class names them)")


ALLOWED = ["manifest.json"] + ["com/skyy/gear/%s.class" % c for c in ("GearMove", "GearCfg", "GearPool", "GearUt", "CfgRows", "CfgFn", "CfgFile",
                                                                      "SkyyGearPlugin")]
sys.exit(T.applier_round("SkyyGear", os.path.join(ROOT, "tools", "gear_0_3_24_patch.py"), os.path.join(HERE, "build_skyygear_0.3.24.py"),
                         os.path.join(HERE, "SkyyGear-0.3.23.jar"), os.path.join(HERE, "SkyyGear-0.3.24.jar"), "com.skyy.gear.GearMove",
                         ALLOWED, extra))
