"""Harness for SkyyMenu 0.3.41 (Skill Trees 3 in the Mods list; tools/menu_0_3_41_patch.py).
Build first:
    python tools/menu_0_3_41_patch.py && python SkyyMenu/build_skyymenu_0.3.41.py

    python SkyyMenu/test_skyymenu_0.3.41.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.40 -> 0.3.41: exactly the listed members differ (the Mods data + version texts)
  M41  the jar's SkyyTrees Mods entry: no Tokens / Dust / Ability Points, the Skill Trees 3 blurb, /tree combat, the Server Setup line;
       MODS_VERSIONS SkyyTrees 0.4.0 / SkyySkills 0.4.55 / SkyyClasses 0.1.42
  D    live     two starts on a scratch COPY of the live Skyy_SkyyMenu (the 0.3.35 harness's phase)
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "dev"))
import harness_kit as HK
import skyybuild as B

_s40 = importlib.util.spec_from_file_location("test_skyymenu_0_3_40", os.path.join(HERE, "test_skyymenu_0.3.40.py"))
T40 = importlib.util.module_from_spec(_s40)
_s40.loader.exec_module(T40)
T35 = T40.T35

VERSION = "0.3.41"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.40.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "st3r12", "menu")))
PKG = "com.skyy.menu."
ADDED = []
EXPECT = {'CfgFn': ['~m opExport'], 'CfgRows': ['~m header'], 'MenuData': ['~<clinit>'], 'OpsPage': ['~<clinit>'], 'SkyyMenuPlugin': ['~m setup']}


def run_m41(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    MD = JClass(PKG + "MenuData")
    texts = []
    for f in MD.class_.getDeclaredFields():
        try:
            f.setAccessible(True)
            v = f.get(None)
        except Exception:
            continue
        if v is None:
            continue
        try:
            for x in list(v):
                texts.append(str(x))
        except Exception:
            texts.append(str(v))
    blob = "\n".join(texts)
    K.check("Skill Trees 3: your class tree and one tree for each skill" in blob and "/tree [skill] - one tree, e.g. /tree mining or /tree combat" in blob,
            "M41 the SkyyTrees entry: the Skill Trees 3 blurb + /tree combat")
    K.check("Ability Points your class skill earns" not in blob and "nodes, Dust, Tree Feller" not in blob and "spend the points your skill levels earn on nodes" not in blob,
            "M41 the old Tokens / Dust / AP texts are gone")
    K.check("respec, Dust refund, nodes, Vein Burst, Feller, class trees" in blob, "M41 the Server Setup line")
    K.check("0.4.0" in blob and "0.4.55" in blob and "0.1.42" in blob, "M41 MODS_VERSIONS carry this round's versions")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyMenu", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("m41", run_m41), ("live", T35.run_live)], script=__file__, live=(T35.LIVE_DIR, "Skyy_SkyyMenu"))
