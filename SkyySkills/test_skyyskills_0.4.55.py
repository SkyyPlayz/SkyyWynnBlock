"""SkyySkills 0.4.55 - harness for THE LEVEL CAP STOPS AT 100 + the Skill Trees 3 texts (tools/skills_0_4_55_patch.py).
Build first: python tools/skills_0_4_55_patch.py && python SkyySkills/build_skyyskills_0.4.55.py

    python SkyySkills/test_skyyskills_0.4.55.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Phases (each a fresh child JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch; tools/harness_kit.py):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.4.54 -> 0.4.55: only the version / ready-line texts differ
  CAP every rebirth-reset skill slot (all 19 + Exploration's own rule) with a fake SkyyRebirth raising the cap 10 a rebirth: rebirth 0..5 =
      min(levels.runCap + 10 n, its cap) and EVERY rebirth from 6 to 1000 = 100 exactly (levels.capMax) - level, cap, need = 0 / MAX at 100;
      levels.capMax 0 = no clamp (an admin's choice); a profile's recorded floor is never lowered; the level coins at rebirth 1000 stay a number
  LC  0.4.53's level-cap phase re-run on this jar
  AA  engine-access audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK


def _mod(fn, name):
    s = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


T53 = _mod("test_skyyskills_0.4.53.py", "test_skyyskills_0_4_53")
VERSION = "0.4.55"
PKG = "com.skyy.skills."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySkills-0.4.54.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "st3r12", "sk")))
ADDED = []
EXPECT = {"SkyySkillsPlugin": ["~m setup"], "CfgRows": ["~<clinit>", "~m header"], "CfgFn": ["~m opExport"], "SkillCfg": ["~m load"],
          "ManaGuard": ["~m armReport2", "~m intReport", "~m packReport"]}
boot, fresh_load = T53.boot, T53.fresh_load


def run_cap(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J, Cfg = boot(K)
    fresh_load(J, Cfg, os.path.join(scratch, "cap"))
    SD, SC, ST = J("SkillDefs"), J("SkillCap"), J("SkillStore")
    N = int(SD.N)
    big = 10 ** 15
    NREB = {}

    @JImplements("java.util.function.Function")
    class FakeCap(object):
        @JOverride
        def apply(self, a):
            n = NREB.get(str(a[0]), 0)
            if str(a[1]) == "Exploration":
                return a[2]
            return JClass("java.lang.Integer").valueOf(int(a[2]) + 10 * n)
    ST.bridge().put("rebirth:fn:cap", FakeCap())
    K.check(int(SD.RUN_CAP) == 50 and int(SD.CAP_MAX) == 100, "CAP levels.runCap 50, levels.capMax 100 on a fresh file")
    slots = [s for s in range(N) if bool(SD.rebirthResets(s))]
    K.check(len(slots) == N - 1 and not bool(SD.rebirthResets(int(SD.EXPLORATION))), "CAP %d rebirth-reset slots (every skill but Exploration)" % len(slots))
    maxes = dict((s, int(SD.maxOf(s))) for s in range(N))
    K.notes.append("CAP table maxes: %s" % dict((str(SD.NAMES[s]), maxes[s]) for s in range(N)))
    bad = []
    for n in list(range(0, 31)) + [50, 100, 500, 1000]:
        NREB["p-r"] = n
        SC.CACHE.clear()
        for s in slots:
            base = min(50, maxes[s])
            want = min(100, base + 10 * n)
            got = (int(SC.cap("p-r", s)), int(SC.level("p-r", s, big)))
            if got != (want, want):
                bad.append((str(SD.NAMES[s]), n, got, want))
            if n >= 6 and (got[0] > 100 or got[1] > 100 or int(SC.need("p-r", s, big)) != 0):
                bad.append(("over 100", str(SD.NAMES[s]), n, got))
    K.check(not bad, "CAP every rebirth-reset slot: rebirth 0-5 = runCap + 10 n, rebirth 6 - 1000 = 100 (MAX, XP keeps counting) %s" % bad[:6])
    SD.CAP_MAX = 0
    SC.CACHE.clear()
    NREB["p-r"] = 6
    K.eq(int(SC.cap("p-r", int(SD.MINING))), 110, "CAP levels.capMax 0 = no clamp (an admin's choice: rebirth 6 -> 110)")
    SD.CAP_MAX = 100
    SC.CACHE.clear()
    K.check(int(J("SkillStore").rbCoins(1000, 1000)) >= 0 and int(J("SkillStore").rbCoins(1000, 0)) == 1000, "CAP the level coins at rebirth 1000 stay a number (x coinFactor ^ n)")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyySkills", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("cap", run_cap), ("lc", T53.run_lc)], script=__file__)
