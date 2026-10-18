"""Harness for SkyyBazaar 0.1.21 (round L1: the market tier sort on the 15-step metal ladder, prices UNCHANGED; tools/bazaar_0_1_21_patch.py).
Build first: python tools/bazaar_0_1_21_patch.py && python SkyyBazaar/build_skyybazaar_0.1.21.py   (+ SkyyAuctions 0.1.10 for MK)

    python SkyyBazaar/test_skyybazaar_0.1.21.py [--jar <0.1.21 jar>] [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py; -Xverify:all everywhere):
  A     verify   every class loads + initialises
  C     compare  0.1.20 -> 0.1.21: only BzMarket (tiers = the inlined TIER_SPEC, lvTier = the 15-step bands) + the version texts differ.
                 THE PRICE PROOF: Catalog (every default price, seed line, sell cap, processed-goods spec, migration table) and every other
                 class are byte-for-byte the same members - no price, no saved-data rule moved
  TT    table    BzMarket.TIER_SPEC of 0.1.21 = tools/tier_tags.py TT_VERSION 2 ROWS; 0.1.20's = TT_VERSION 1 rows (git 73014c2); every
                 row moved by renumber() except the rows at their OWN step (zone metals, mining armor, Bronze - named); lvTier / tier (real
                 class) = TT.tier_for_level for every level 0-119, Onyxium T16, untiered 99
  PRICE / ZONE / HUB / ETER   the 0.1.20 harness's phases on this jar (every price at demand 1.0, the zone metal prices + the Bronze sell
                 cap, the page, the Eternal seed lock) - unchanged behaviour
  AA    engine-access audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util, types as _types

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import tier_tags as TT

_argv = list(sys.argv)
_sp = importlib.util.spec_from_file_location("ah0113test", os.path.join(ROOT, "SkyyAuctions", "test_skyyauctions_0.1.13.py"))
AH13 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(AH13)       # tt_v1 (TT_VERSION 1 from git 73014c2), spec_in, table_proof
sys.argv = _argv
_sp = importlib.util.spec_from_file_location("bz0120test", os.path.join(HERE, "test_skyybazaar_0.1.20.py"))
T20 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T20)
sys.argv = _argv

VERSION = "0.1.21"
OLD_VERSION = "0.1.20"
PKG = "com.skyy.bazaar."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyBazaar-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyBazaar-%s.jar" % OLD_VERSION)          # the SET pin
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "l1", "bz")))
EXPECT = {"BzMarket": ["~m tiers", "~m lvTier"],                 # the re-baked TIER_SPEC (inlined into tiers) + the 15-step level bands
          "CfgFn": ["~m opExport"], "CfgRows": ["~m header"],    # the version texts
          "SkyyBazaarPlugin": ["~m setup"]}                      # the ready line's version
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = []


def run_tier(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    T1 = AH13.tt_v1(scratch)
    _new = AH13.spec_in(jar, "com/skyy/bazaar/BzMarket.class")
    _old = AH13.spec_in(OLD_JAR, "com/skyy/bazaar/BzMarket.class")
    # rows added to tools/tier_tags.py AFTER 0.1.20 outside TT_VERSION 1: SkyyGear 0.3.23 G2 tools + SkyyArmory 0.1.33 A1 weapons - accepted
    # by name, proved to be the ONLY such rows, each at its metal word's ladder step
    POST = set(TT.G2_FOREVER + TT.G2_HARVESTERS + TT.G2_CANS + TT.A1_WEAPONS)
    _late = set(i for i in set(_new) - set(_old) if i not in T1.ROWS)
    K.eq(sorted(_late), sorted(POST), "TT the rows added after 0.1.20 outside TT_VERSION 1 = exactly the G2 tools + A1 weapons (%d rows)" % len(POST))
    K.check(all(_new[i] == TT.metal_tier(i.split("_")[-2] if i.endswith(("_SkyWynn", "_Wynn")) else i.split("_")[-1]) for i in POST),
            "TT each G2 / A1 row sits at its metal's ladder step")
    AH13.table_proof(K, _new, _old, _types.SimpleNamespace(ROWS=set(T1.ROWS) | POST, tier=T1.tier), "TT")
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    M = JClass(PKG + "BzMarket")
    bad = [(l, x) for l in range(0, 120) for x in ("Weapon_Sword_Iron", "Armor_Onyxium_Chest", "Weapon_Sword_Lumen_SkyWynn", "Armor_Copper_Head")
           if int(M.lvTier(x, l)) != TT.tier_for_level(l, x)]
    K.eq(bad, [], "TT BzMarket.lvTier = tools/tier_tags.py tier_for_level for every level 0-119")
    K.eq([int(M.tier(x, l)) for x, l in (("Ore_Thorium", -1), ("Ore_Lead_SkyWynn", -1), ("Ingredient_Bar_Lumen_SkyWynn", -1), ("Weapon_Sword_Iron", 16),
                                          ("Weapon_Sword_Iron", 50), ("Armor_Onyxium_Chest", 5), ("Skyy_No_Such_Thing", -1), ("Ore_Copper", 99))],
         [4, 5, 15, 2, 15, 16, 99, 1], "TT BzMarket.tier: table rows, level bands, Onyxium, untiered last")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyBazaar", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("tier", run_tier), ("price", T20.run_price), ("zone", T20.run_zone), ("hub", T20.run_hub), ("eter", T20.run_eter)],
           script=__file__)
