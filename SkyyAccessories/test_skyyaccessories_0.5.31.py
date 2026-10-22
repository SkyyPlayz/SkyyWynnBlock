"""Harness for SkyyAccessories 0.5.31 (the Normal accessory quality text #fefefe instead of #ffffff - The Armory's ScribingModule owns #ffffff;
tools/accessories_0_5_31_patch.py). Build first:
    python tools/accessories_0_5_31_patch.py && python SkyyAccessories/build_skyyaccessories_0.5.31.py
    python SkyyAccessories/test_skyyaccessories_0.5.31.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.5.30 -> 0.5.31: no class member differs except the version texts; non-class files: manifest.json + Skyy_Acc_Normal.json
  QUAL  the shipped quality assets: Skyy_Acc_Normal TextColor #fefefe, every other field and the other five qualities unchanged, no quality
        in #ffffff; AccDefs.RARITY_COLOR (page colours) unchanged
  0.5.30's phases on THIS jar (the code is identical): DEFS, POW, PCT, ITEM, MIG
  LIVE  START TWICE on a scratch COPY of the live Skyy_SkyyAccessories = 0.5.30's live phase (the P5 update has not run on the live world
        yet - its change-log identity stays "SkyyAccessories 0.5.30", MP5_WHO): only the planned keys change, the second start nothing
  AA    engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK
import skyybuild as B
import skyyonce_harness as OH

_argv = list(sys.argv)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "lean1022", "acc")]
_sp = importlib.util.spec_from_file_location("test_skyyaccessories_0_5_30", os.path.join(HERE, "test_skyyaccessories_0.5.30.py"))
T530 = importlib.util.module_from_spec(_sp)
_orig_compare = HK.run_compare
_sp.loader.exec_module(T530)
HK.run_compare = _orig_compare
SCRATCH = os.path.abspath(HK.arg("--dir"))
sys.argv = _argv

VERSION, OLD = "0.5.31", "0.5.30"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyAccessories-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyAccessories-%s.jar" % OLD)
PKG = T530.PKG
NORMAL = "Server/Item/Qualities/Skyy_Acc_Normal.json"
HK.run_compare = OH.compare_allowing(lambda n: n == NORMAL)
EXPECT = {"CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "SkyyAccessoriesPlugin": ["~m setup"]}   # the version texts (config kit + ready line)
if "--expect-dump" in sys.argv:
    EXPECT = {}


def run_qual(out, jar, scratch, _home):
    K = HK.Child(out)
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    qa = dict((n, za.read(n)) for n in za.namelist() if n.startswith("Server/Item/Qualities/"))
    qb = dict((n, zb.read(n)) for n in zb.namelist() if n.startswith("Server/Item/Qualities/"))
    K.eq(sorted(qb), sorted(qa), "QUAL: the same %d quality assets" % len(qa))
    a, b = json.loads(qa[NORMAL]), json.loads(qb[NORMAL])
    K.eq((a["TextColor"], b["TextColor"]), ("#ffffff", "#fefefe"), "QUAL: Skyy_Acc_Normal TextColor #ffffff -> #fefefe")
    a.pop("TextColor")
    b.pop("TextColor")
    K.eq(b, a, "QUAL: every other field of Skyy_Acc_Normal unchanged")
    K.check(all(qa[n] == qb[n] for n in qa if n != NORMAL), "QUAL: the other qualities byte-identical (%s)" % ", ".join(
        "%s %s" % (n.rsplit("/", 1)[1][:-5], json.loads(qb[n])["TextColor"]) for n in sorted(qb) if n != NORMAL))
    K.check(not [n for n in qb if json.loads(qb[n])["TextColor"].lower() == "#ffffff"], "QUAL: no quality draws its text in #ffffff")
    import jpype
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    D = jpype.JClass(PKG + "AccDefs")
    K.eq(str(D.RARITY_COLOR[0]), "#ffffff", "QUAL: AccDefs.RARITY_COLOR (page text) unchanged: %s" % [str(x) for x in D.RARITY_COLOR])
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyAccessories", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("qual", run_qual), ("defs", T530.run_defs), ("pow", T530.run_pow), ("pct", T530.run_pct), ("item", T530.run_item),
                   ("mig", T530.run_mig), ("live", T530.run_live)],
           script=__file__, live=(T530.LIVE_DIR, "Skyy_SkyyAccessories"))
