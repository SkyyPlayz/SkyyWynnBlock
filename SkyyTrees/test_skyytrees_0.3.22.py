"""Harness for SkyyTrees 0.3.22 (round emblems: the class emblem on the class tree's ROOT node; tools/trees_0_3_22_patch.py; with SkyyClasses
0.1.36 + SkyyProfiles 0.1.17). Build first:
    python tools/trees_0_3_22_patch.py && python SkyyTrees/build_skyytrees_0.3.22.py
    python SkyyTrees/test_skyytrees_0.3.22.py [--keep]
Phases (tools/harness_kit.py, fresh child JVMs, -Xverify:all, TEMP / TMP in tools/dev/scratch/emblems/tr):
  A   verify   every class loads + initialises
  C   compare  0.3.21 -> 0.3.22: exactly the planned members (EXPECT); non-class entries: manifest.json only
  X   exec     TreePage.cicon / cemblem on a stand-in skyy.bridge:
               X1 no class:fn:emblem = every node's icon as 0.3.21 (TreeClass.icon; ability nodes = the panel's pictures)
               X2 a stand-in class:fn:emblem: ROOT = the emblem for every class, every other node unchanged, the ability nodes still
                  take the panel's picture first; an empty / non-String / throwing answer = the weapon; ci out of range = no call
               X3 buildClass draws the nodes through cicon (bytecode)
  AA  engine-access audit
"""
import os, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW

VERSION = "0.3.22"
PKG = "com.skyy.trees."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyTrees-0.3.21.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "emblems", "tr")))
EXPECT = {"TreePage": ["+m cemblem", "~m cicon"],                 # ROOT = the class emblem
          "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "SkyyTreesPlugin": ["~m setup"],
          "TreeCfg": ["~m load"]}   # the version texts (TreeCfg.load: only the default file's header line "# SkyyTrees 0.3.22 - ...")
ADDED = []


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JString, JArray
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    Pg, TC, St = JClass(PKG + "TreePage"), JClass(PKG + "TreeClass"), JClass(PKG + "TreeStore")
    br = St.bridge()
    br.remove("class:fn:emblem")

    @JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def apply(self, o):
            return self.f(o)
    classes = [str(x) for x in TC.CLASSES]
    nid = [str(x) for x in TC.NID]
    root = nid.index("ROOT")
    NN = int(TC.NN)
    abl = [int(x) for x in TC.ABLI]
    aic = JArray(JString)(["SkyyAbility_X_%d" % a for a in range(5)])
    base = dict(((ci, n), str(TC.icon(ci, n))) for ci in range(len(classes)) for n in range(NN))
    # ---- X1 no bridge = 0.3.21
    bad = [(ci, n) for ci in range(len(classes)) for n in range(NN) if str(Pg.cicon(ci, n, None)) != base[(ci, n)]]
    K.check(not bad, "X1: without class:fn:emblem every node's icon is TreeClass.icon (%s)" % bad[:4])
    K.eq([str(Pg.cicon(0, abl[a], aic)) for a in range(5)], ["SkyyAbility_X_%d" % a for a in range(5)], "X1: the ability nodes take the panel's pictures")
    K.eq(str(Pg.cemblem(0)), "", "X1: cemblem without the bridge = \"\"")
    # ---- X2 a stand-in bridge
    asked = []

    def em(o):
        asked.append(str(o))
        return JString("SkyyClasses_Emblem_" + str(o))
    br.put("class:fn:emblem", Fn(em))
    for ci, cn in enumerate(classes):
        K.eq(str(Pg.cicon(ci, root, aic)), "SkyyClasses_Emblem_" + cn, "X2: %s ROOT = its emblem" % cn)
    bad = [(ci, n) for ci in range(len(classes)) for n in range(NN) if n != root and n not in abl and str(Pg.cicon(ci, n, aic)) != base[(ci, n)]]
    K.check(not bad, "X2: every other node keeps its icon (%s)" % bad[:4])
    K.eq([str(Pg.cicon(1, abl[a], aic)) for a in range(5)], ["SkyyAbility_X_%d" % a for a in range(5)], "X2: the ability nodes still take the panel's pictures")
    del asked[:]
    K.eq(str(Pg.cemblem(-1)) + str(Pg.cemblem(len(classes))), "", "X2: a class index out of range = \"\" ...")
    K.eq(asked, [], "X2: ... without asking the bridge")
    br.put("class:fn:emblem", Fn(lambda o: JString("")))
    K.eq(str(Pg.cicon(0, root, None)), base[(0, root)], "X2: an empty answer (not loaded) = the weapon")
    br.put("class:fn:emblem", Fn(lambda o: 7))
    K.eq(str(Pg.cicon(0, root, None)), base[(0, root)], "X2: a non-String answer = the weapon")

    def boom(o):
        raise RuntimeError("boom")
    br.put("class:fn:emblem", Fn(boom))
    K.eq(str(Pg.cicon(0, root, None)), base[(0, root)], "X2: a throwing bridge = the weapon (never throws)")
    br.remove("class:fn:emblem")
    # ---- X3 bytecode
    gr = PW.calls(jar)
    K.check(PKG + "TreePage.cicon" in gr.get("TreePage.buildClass", set()), "X3: buildClass draws the class nodes through cicon (bytecode)")
    K.check(PKG + "TreePage.cemblem" in gr.get("TreePage.cicon", set()), "X3: cicon asks cemblem (bytecode)")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyTrees", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("exec", run_exec)], script=__file__)
