"""Harness for SkyySacks 0.8.34 (Augments round A2 - tools/sacks_0_8_34_patch.py: SkyyGear's augments go to the Combat bag).
Build first:
    python tools/sacks_0_8_34_patch.py && python SkyySacks/build_skyysacks_0.8.34.py

    python SkyySacks/test_skyysacks_0.8.34.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  A / C   verify (-Xverify:all) + compare 0.8.33 -> 0.8.34 (only SackDefs.homeOf + the ready line + the kit's version strings + RecipeCmp's
          build-time tier table, re-baked from tools/tier_tags.py: the 120 augments sort by tier in /craft)
  CAT34   SackDefs.homeOf / catOf / intake EXECUTED on the 0.8.34 jar AND the 0.8.33 jar (each in its own JVM) for every Assets.zip item id, the
          120 SkyyGear augment ids and a sample of other Skyy_ ids: the 120 augments answer Combat now (null before), every other id answers
          exactly what 0.8.33 answered
  BC34    bytecode: homeOf tests "Skyy_Aug_" before the generic "Skyy_" rule
  D       start twice on a scratch COPY of NewBetaTest's Skyy_SkyySacks (0.8.27's + 0.8.10's live phases): no migration, no byte changed
Exit code 1 on any failure.
"""
import os, sys, json, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

_argv = list(sys.argv)
_RC = HK.run_compare
_sp = importlib.util.spec_from_file_location("test_skyysacks_0_8_33", os.path.join(HERE, "test_skyysacks_0.8.33.py"))
T33 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T33)
sys.argv = _argv
HK.run_compare = _RC
T30 = T33.T30

VERSION = "0.8.34"
OLD_VERSION = "0.8.33"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySacks-%s.jar" % OLD_VERSION)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "aug_a2", "sacks")))
PKG = "com.skyy.sacks."
BETA = T33.BETA
EXPECT = {"SackDefs": ["~m homeOf"], "SkyySacksPlugin": ["~m setup"], "CfgRows": ["~m header"], "CfgFn": ["~m opExport"],
          "RecipeCmp": ["~<clinit>"]}          # its /craft sort table is baked from tools/tier_tags.py (+ the 120 augment rows)
if "--expect-dump" in sys.argv:
    EXPECT = {}
sys.path.insert(0, os.path.join(ROOT, "tools"))
import tier_tags as TT
AUG = list(TT.AUG_IDS)
assert len(AUG) == 120 and "Skyy_Aug_Swift_1" in AUG and "Skyy_Aug_Sage_5" in AUG          # aug2b: Swift + Sage ship (SkyyGear 0.3.52 fix round 3)
OTHER_SKYY = ["Skyy_Sack_Mining_Small", "Skyy_Ench_Copper", "Skyy_Ench_Wheat", "Skyy_Sigil_Rare", "Skyy_Cook_Recipe_Bread", "Skyy_Accessory_Smelting_T1",
              "Skyy_Flask_Small", "SkyyFishing_Fish_Bass", "Skyy_Augment", "Skyy_Au", "Skyy_AugX_Fire_1"]


def ids_all():
    z = zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip"))          # read-only
    out = sorted(set(os.path.basename(n)[:-5] for n in z.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json")))
    return out + AUG + OTHER_SKYY


def cats(out, jar, which):
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    D = JClass(PKG + "SackDefs")
    UUID = JClass("java.util.UUID")
    u = UUID.fromString("00000000-0000-0000-0000-000000000834")
    res = {}
    for i in ids_all():
        h = D.homeOf(JString(i))
        c = D.catOf(JString(i))
        n = D.intake(u, JString(i))
        res[i] = [None if h is None else str(h), None if c is None else str(c), None if n is None else str(n)]
    json.dump(res, open(os.path.join(SCRATCH, "cats-%s.json" % which), "w"))
    K.check(len(res) > 1000, "CAT34 %s: homeOf / catOf / intake ran for %d ids" % (which, len(res)))
    K.save()


def run_cat_new(out, jar, scratch, _home):
    cats(out, jar, "new")


def run_cat_old(out, _jar, scratch, _home):
    cats(out, OLD_JAR, "old")


def run_cat_cmp(out, _jar, scratch, _home):
    K = HK.Child(out)
    a = json.load(open(os.path.join(SCRATCH, "cats-old.json")))
    b = json.load(open(os.path.join(SCRATCH, "cats-new.json")))
    K.eq(sorted(a), sorted(b), "CAT34 the same ids on both jars")
    K.check(all(b[i] == ["Combat", "Combat", "Combat"] for i in AUG), "CAT34 0.8.34: all 120 augments -> Combat (homeOf, catOf, intake): %s" % [i for i in AUG if b[i] != ["Combat"] * 3][:4])
    K.check(all(a[i] == [None, None, None] for i in AUG), "CAT34 0.8.33: the augments had no bag (null)")
    diff = [i for i in a if a[i] != b[i] and i not in AUG]
    K.check(not diff, "CAT34 every other id answers exactly what 0.8.33 answered (%d ids): %s" % (len(a) - len(AUG), diff[:5]))
    K.notes.append("CAT34 sample: Skyy_Aug_Fire_10 %s, Skyy_AugX_Fire_1 %s, Skyy_Ench_Copper %s, Ingredient_Sac_Venom %s" % (
        b["Skyy_Aug_Fire_10"], b.get("Skyy_AugX_Fire_1"), b.get("Skyy_Ench_Copper"), b.get("Ingredient_Sac_Venom")))
    K.save()


def run_bc34(out, jar, scratch, _home):
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=False)
    cp = JClass("javassist.ClassPool")(True)
    cp.appendClassPath(JString(jar))
    m = cp.get(PKG + "SackDefs").getDeclaredMethod("homeOf")
    ci = m.getMethodInfo().getCodeAttribute().iterator()
    cpool = m.getMethodInfo().getConstPool()
    Mn = JClass("javassist.bytecode.Mnemonic")
    strs = []
    while ci.hasNext():
        i = ci.next()
        op = str(Mn.OPCODE[ci.byteAt(i)])
        if op in ("ldc", "ldc_w"):
            idx = ci.byteAt(i + 1) if op == "ldc" else ci.u16bitAt(i + 1)
            try:
                strs.append(str(cpool.getStringInfo(idx)))
            except Exception:
                pass
    K.check("Skyy_Aug_" in strs and "Skyy_" in strs and strs.index("Skyy_Aug_") < strs.index("Skyy_"), "BC34 homeOf tests Skyy_Aug_ before the generic Skyy_ rule: %s" % strs[:12])
    K.save()


if __name__ == "__main__":
    os.makedirs(SCRATCH, exist_ok=True)
    HK.run("SkyySacks", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, [],
           [("catnew", run_cat_new), ("catold", run_cat_old), ("catcmp", run_cat_cmp), ("bc34", run_bc34),
            ("live", T30.T0827.run_live27), ("live2", T30.T0827.T0810.run_live10)],
           __file__, live=(BETA, "Skyy_SkyySacks"))
