"""Harness for SkyySacks 0.8.22 (round L1: the /craft recipe sort + row tags on the 15-step metal ladder, tools/tier_tags.py TT_VERSION 2;
tools/sacks_0_8_22_patch.py). Build first:
    python tools/sacks_0_8_22_patch.py && python SkyySacks/build_skyysacks_0.8.22.py

    python SkyySacks/test_skyysacks_0.8.22.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.8.21 -> 0.8.22: exactly the planned members (EXPECT: RecipeCmp + the version texts); non-class entries: manifest.json only
  TT    THE TABLE (real classes of both jars, -Xverify:all): 0.8.22 RecipeCmp TT_IDS / TT_TIER / TT_GRP / TT_RANK / LADDER / METAL_W / METAL_T =
        tools/tier_tags.py TT_VERSION 2; 0.8.21's = the TT_VERSION 1 table (git 73014c2); every tier moved by renumber() except exactly the
        54 rows at their OWN step (zone metals, their Enchanted ingots, mining armor, Bronze); the crop groups / ranks unchanged; the row
        tag (tierText) keeps every word 0.8.21 showed for the renumbered rows ("T1 Crude" for Crude / Wood); tierKey sorts by the new ladder
  ALLOY / SUP / TG / KEYS / D (live)   the 0.8.21 harness's phases on this jar - unchanged behaviour
  AA    engine-access audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import tier_tags as TT

_orig_compare = HK.run_compare
_argv = list(sys.argv)
_sp = importlib.util.spec_from_file_location("test_skyysacks_0_8_21", os.path.join(HERE, "test_skyysacks_0.8.21.py"))
T21 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T21)
sys.argv = _argv
HK.run_compare = _orig_compare
T18 = T21.T18
_sp = importlib.util.spec_from_file_location("ah0113test", os.path.join(ROOT, "SkyyAuctions", "test_skyyauctions_0.1.13.py"))
AH13 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(AH13)       # its tt_v1 (TT_VERSION 1 from git) + table_proof
sys.argv = _argv

VERSION = "0.8.22"
OLD_VERSION = "0.8.21"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySacks-%s.jar" % OLD_VERSION)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "l1", "sacks")))
PKG = "com.skyy.sacks."
EXPECT = {
    "RecipeCmp": ["+f TT_WORD", "+f METAL_WD", "+m metalWord", "~m tierText", "~<clinit>"],   # the re-baked table + the tag words
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"],                                       # the version text
    "SkyySacksPlugin": ["~m setup"],                                                          # the ready line
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = []


def run_tier(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    T1 = AH13.tt_v1(scratch)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    File, Str = JClass("java.io.File"), JClass("java.lang.String")
    ld = JClass("java.net.URLClassLoader")([File(OLD_JAR).toURI().toURL(), File(B.SERVER_JAR).toURI().toURL()], None)
    Cn = JClass(PKG + "RecipeCmp")
    Co = JClass("java.lang.Class").forName(PKG + "RecipeCmp", True, ld)
    K.check(Co.getClassLoader() is not None and str(Co.getProtectionDomain().getCodeSource().getLocation()).endswith("SkyySacks-%s.jar" % OLD_VERSION),
            "TT the 0.8.21 RecipeCmp comes from its own jar")

    def old(f):
        return [x for x in Co.getField(f).get(None)]

    def new(f):
        return [x for x in getattr(Cn, f)]
    n_ids, o_ids = [str(x) for x in new("TT_IDS")], [str(x) for x in old("TT_IDS")]
    ns, os_ = dict(zip(n_ids, [int(x) for x in new("TT_TIER")])), dict(zip(o_ids, [int(x) for x in old("TT_TIER")]))
    AH13.table_proof(K, ns, os_, T1, "TT")
    K.eq([str(x) for x in new("LADDER")], list(TT.LADDER), "TT LADDER = the 16 ladder nouns")
    K.eq(list(zip([str(x) for x in new("METAL_W")], [int(x) for x in new("METAL_T")])), [tuple(t) for t in TT.TOOL_METALS], "TT METAL_W / METAL_T = TT.TOOL_METALS")
    K.eq([str(x) for x in new("TT_WORD")], [TT.word(i) for i in n_ids], "TT TT_WORD = TT.word of every row")
    K.eq(list(zip(n_ids, [str(x) for x in new("TT_GRP")], [int(x) for x in new("TT_RANK")])),
         list(zip(o_ids, [str(x) for x in old("TT_GRP")], [int(x) for x in old("TT_RANK")])), "TT the crop groups / ranks unchanged")
    mo = Co.getMethod("tierText", Str.class_)
    keep, bad = 0, []
    for i in n_ids:
        nt, ot = str(Cn.tierText(i)), str(mo.invoke(None, i))
        want = "T%d %s" % (TT.tier(i), TT.word(i))
        if nt != want:
            bad.append((i, nt, want))
        if TT.renumber(T1.tier(i)) == TT.tier(i) and ot.split(" ", 1)[1] == nt.split(" ", 1)[1]:
            keep += 1
    K.eq(bad, [], "TT tierText of every table row = 'T<new tier> <tier_tags word>'")
    K.notes.append("TT %d of %d rows keep 0.8.21's word in the row tag (the rest: Bronze 'T3 Iron' -> 'T3 Bronze' and the zone metals' own steps)" % (keep, len(n_ids)))
    cases = [("Tool_Pickaxe_Wood", "T1 Crude"), ("Tool_Hatchet_Crude", "T1 Crude"), ("Ore_Copper", "T1 Copper"), ("Tool_Pickaxe_Copper", "T1 Copper"),
             ("Weapon_Sword_Steel", "T2 Iron"), ("Ingredient_Bar_Thorium", "T4 Thorium"), ("Ore_Lead_SkyWynn", "T5 Lead"),
             ("Weapon_Sword_Cobalt", "T7 Cobalt"), ("Ingredient_Bar_Lumen_SkyWynn", "T15 Lumen"), ("Weapon_Sword_Onyxium", "T16 Onyxium"),
             ("Skyy_Acc_Test_T3", "T3"), ("Rock_Stone", "")]
    K.eq([str(Cn.tierText(i)) for i, w in cases], [w for i, w in cases], "TT tierText cases (Crude / Wood keep 'Crude', Steel 'Iron', own suffix, untiered)")
    K.eq([str(mo.invoke(None, i)) for i in ("Tool_Pickaxe_Wood", "Ore_Copper", "Ingredient_Bar_Thorium")], ["T1 Crude", "T2 Copper", "T4 Thorium"],
         "TT control: 0.8.21 said T1 Crude / T2 Copper / T4 Thorium")
    srt = ["Ore_Lead_SkyWynn", "Ore_Mithril", "Ore_Thorium", "Ingredient_Bar_Dusk_SkyWynn", "Ore_Copper", "Ore_Iron", "Ingredient_Bar_Bronze", "Rock_Stone"]
    K.eq(sorted(srt, key=lambda i: (int(Cn.tierKey(i)), i)), ["Rock_Stone", "Ore_Copper", "Ore_Iron", "Ingredient_Bar_Bronze", "Ore_Thorium", "Ore_Lead_SkyWynn",
                                                               "Ingredient_Bar_Dusk_SkyWynn", "Ore_Mithril"], "TT tierKey sorts on the 15-step ladder")
    K.save()


if __name__ == "__main__":
    HK.run("SkyySacks", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("tier", run_tier), ("alloy", T21.run_alloy), ("sup", T21.run_sup), ("tg", T18.T16.run_tg), ("keys", T18.T17.run_keys),
            ("live", T18.T0810.run_live10)], __file__, live=(T18.T16.T15.BETA, "Skyy_SkyySacks"))
