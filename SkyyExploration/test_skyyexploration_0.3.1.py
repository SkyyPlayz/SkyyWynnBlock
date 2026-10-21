"""Harness for SkyyExploration 0.3.1 (tools/exploration_0_3_1_patch.py): Skill Trees 3 R3b - the dead 0.3 node Scavenger (Exploration.EScav)
is removed cleanly. Build first: python tools/exploration_0_3_1_patch.py && python SkyyExploration/build_skyyexploration_0.3.1.py

    python SkyyExploration/test_skyyexploration_0.3.1.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.0 -> 0.3.1: ExpAward.scav removed, chestOpened changed, the Server Setup help + version texts; nothing else
  ES   the jar holds no "Exploration.EScav" string in any class (the grep proof on the bytes) and still asks "Exploration.ELuck"
       (ExpSkill.luckOf ... EXECUTED with a fake SkyyTrees tree:fn:bonus that records the keys: only ELuck is asked); ExpAward has no scav
  PC / LIVE  0.3.0's per-profile chest phase + its LIVE phase (start twice on a scratch COPY of the live Skyy_SkyyExploration) on this jar
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK
import skyybuild as B

_eq0 = HK.Child.eq
_s = importlib.util.spec_from_file_location("test_skyyexploration_0_3_0", os.path.join(HERE, "test_skyyexploration_0.3.0.py"))
T30 = importlib.util.module_from_spec(_s)
_s.loader.exec_module(T30)
HK.Child.eq = _eq0          # 0.3.0's compare allowed its new sparkle file; 0.3.0 -> 0.3.1 changes no asset (manifest.json only)

VERSION, OLD = "0.3.1", "0.3.0"
JAR = os.path.join(HERE, "SkyyExploration-%s.jar" % VERSION)
OLD_JAR = os.path.join(HERE, "SkyyExploration-%s.jar" % OLD)
PKG = T30.PKG
SCRATCH = HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "st3r3b", "expl"))
EXPECT = {
    "ExpAward": ["-m scav", "~m chestOpened"],
    "ExpCfg": ["~m load"],          # the default file text (version head)
    "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],
    "ExpLgMig": ["~m logLine", "~m migrate"], "ExpNcMig": ["~m logLine", "~m migrate"],
    "SkyyExplorationPlugin": ["~m setup"],
}


def run_es(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JObject
    K = HK.Child(out)
    z = zipfile.ZipFile(jar)
    hits = [n for n in z.namelist() if n.endswith(".class") and b"Exploration.EScav" in z.read(n)]
    luck = [n for n in z.namelist() if n.endswith(".class") and b"Exploration.ELuck" in z.read(n)]
    K.check(not hits, "ES no class holds the string Exploration.EScav (grep proof on the jar bytes): %s" % hits)
    K.check(luck, "ES Exploration.ELuck is still read (%s)" % luck)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Aw, Sk = JClass(PKG + "ExpAward"), JClass(PKG + "ExpSkill")
    K.check(not any(str(m.getName()) == "scav" for m in Aw.class_.getDeclaredMethods()), "ES ExpAward has no scav method")
    br = JClass("java.lang.System").getProperties().get("skyy.bridge")
    if br is None:
        br = JClass("java.util.concurrent.ConcurrentHashMap")()
        JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    ASK = []

    @JImplements("java.util.function.Function")
    class Bo(object):
        @JOverride
        def apply(self, a):
            ASK.append(str(a[1]))
            return JObject(0.01, "java.lang.Double")
    br.put("tree:fn:bonus", Bo())
    u = JClass("java.util.UUID").fromString("00000000-0000-0000-0000-0000000e0031")
    v = float(Sk.treeBonus(u, "Exploration.ELuck"))
    K.check(abs(v - 0.01) < 1e-12 and ASK == ["Exploration.ELuck"], "ES ExpSkill.treeBonus asks Exploration.ELuck (Chest Finder's alias): %s %s" % (v, ASK))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyExploration", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("es", run_es), ("pc", T30.run_pc), ("live", T30.run_live)], script=__file__, live=(T30.LIVE, "Skyy_SkyyExploration"))
