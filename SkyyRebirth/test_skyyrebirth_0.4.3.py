"""SkyyRebirth 0.4.3 - harness (tools/rebirth_0_4_3_patch.py, the Balance P8c follow-up built in round P8d: Beastmastery counts for Void
Particles like the other skills).
Build first: python tools/rebirth_0_4_3_patch.py && python SkyyRebirth/build_skyyrebirth_0.4.3.py

    python SkyyRebirth/test_skyyrebirth_0.4.3.py [--dir <empty folder inside tools/dev/scratch/>]

  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.4.2 -> 0.4.3: exactly the planned members differ (EXPECT: RbMath.CAP_SKILLS + the version texts)
  V / P / F41 / F42 / L42   the WHOLE 0.4.0 - 0.4.2 harness against the 0.4.3 jar
  F43 P8d      EXECUTED: decide() from prepared facts - every counted skill at its cap with and without arm.beastmastery (54 -> 56 VP at
               rebirth 2), Beastmastery below its cap (no VP), an older SkyySkills without the line (= 0.4.2's number), the 11 cap; the page
               preview (RbCheck.gains through a stub skill:fn:run) counts Beastmastery at its cap
  L42 live     (0.4.2's) a scratch COPY of the live NewBetaTest Skyy_SkyyRebirth started TWICE in setup()'s order - 0.4.3 adds no update
  AA  engine-access audit
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


VERSION = "0.4.3"
RB = "com.skyy.rebirth."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyRebirth-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyRebirth-0.4.2.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "balp8d", "rb")))
T42 = _load("t_rb042", os.path.join(HERE, "test_skyyrebirth_0.4.2.py"))
T41, T40 = T42.T41, T42.T40
for _m in (T42, T41, T40, T40.T34):
    _m.VERSION, _m.JAR = VERSION, JAR
R = T40.R
EXPECT = {
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "SkyyRebirthPlugin": ["~m setup"],   # the version text
    "RbMig": ["~m migrate"], "RbStore": ["~m writeNow"],   # only the @VERSION@ text in the vp-migration.log line / the file comment
    "RbMath": ["~<clinit>"],   # CAP_SKILLS + "beastmastery"
}
SEVEN = ("mining", "foraging", "farming", "smithing", "alchemy", "fishing", "cooking")


def run_f43(out, jar, scratch, _home):
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    from jpype import JClass, JImplements, JOverride, JArray
    K = HK.Child(out)
    Cfg, Tx = R("RbCfg"), R("RbTx")
    home, pl, U, k = T40.world(scratch, "f43")
    K.eq([str(x) for x in R("RbMath").CAP_SKILLS], list(SEVEN) + ["beastmastery"], "F43 CAP_SKILLS = the 7 skills + Beastmastery")
    J_ = R("RbJ")

    def decide(newN, facts, mode="live"):
        j = J_()
        j.bad, j.k, j.newN, j.mode, j.tx = False, k, newN, mode, "tx0000000000000-abcdef"
        j.prepared.put("skills", facts)
        j.prepared.put("coins", "purse=0")
        j.prepared.put("bank", "bank=0")
        return [str(x) for x in Tx.decide(j)]
    cls = "arm.class=1000/1000/100/100;"
    allcap = ";".join("arm.%s=9/9/50/50" % s_ for s_ in SEVEN)
    d0 = decide(2, cls + allcap)
    K.check(d0[0] == "commit" and d0[1].startswith("vp=54;vpSkills=7;vpOver=0;"), "F43 no arm.beastmastery (SkyySkills older than 0.4.60) = 0.4.2's number 54: %s" % d0[1][:30])
    d1 = decide(2, cls + allcap + ";arm.beastmastery=9/9/50/50")
    K.check(d1[0] == "commit" and d1[1].startswith("vp=56;vpSkills=8;vpOver=0;"), "F43 Beastmastery at its cap = +2 VP (20 + 20 + 2 x 8 = 56): %s" % d1[1][:30])
    d2 = decide(2, cls + allcap + ";arm.beastmastery=8/9/49/50")
    K.check(d2[1].startswith("vp=54;vpSkills=7;"), "F43 Beastmastery below its cap: nothing (54): %s" % d2[1][:30])
    d3 = decide(1, cls + "arm.beastmastery=500/500/50/50")
    K.check(d3[1].startswith("vp=32;vpSkills=1;"), "F43 Beastmastery alone at its cap: 20 + 10 + 2 = 32: %s" % d3[1][:30])
    Cfg.VP_SKILL = 100
    d4 = decide(2, cls + allcap + ";arm.beastmastery=9/9/50/50")
    K.check(d4[1].startswith("vp=840;vpSkills=8;"), "F43 vp.perSkill 100 (Server Setup) x 8: %s" % d4[1][:30])
    Cfg.VP_SKILL = 2
    # the page preview: RbCheck.gains reads skill:fn:run per counted skill (Beastmastery through its own name)
    asked = []
    LVL = {}
    Long_, Int_ = JClass("java.lang.Long"), JClass("java.lang.Integer")

    @JImplements("java.util.function.Function")
    class Run(object):
        @JOverride
        def apply(self, a):
            s = str(a[1])
            asked.append(s)
            if s not in LVL:
                return None
            lv, cap, run, toCap = LVL[s]
            o = JArray(JClass("java.lang.Object"))(4)
            o[0], o[1], o[2], o[3] = Int_(lv), Int_(cap), Long_(run), Long_(toCap)
            return o
    Cfg.BRIDGE.put("skill:fn:run", Run())
    LVL.update({"class": (50, 50, 1000, 1000), "beastmastery": (50, 50, 900, 900)})
    gn = R("RbCheck").gains(U, 0)
    t = [str(x) for x in gn[0]]
    K.check("beastmastery" in asked and t[2] == "Skills at their cap 1: +2 VP" and t[0] == "Void Particles  +32 VP",
            "F43 the /rebirth preview counts Beastmastery at its cap (skill:fn:run 'beastmastery'): %s" % t[:3])
    LVL["beastmastery"] = (49, 50, 899, 900)
    t = [str(x) for x in R("RbCheck").gains(U, 0)[0]]
    K.check(t[2] == "Skills at their cap 0: +0 VP" and t[0] == "Void Particles  +30 VP", "F43 ... and not below it: %s" % t[:3])
    K.save()


if __name__ == "__main__":
    assert os.path.isfile(B.JAVASSIST), B.JAVASSIST
    HK.run(name="SkyyRebirth", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=RB, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("vp", T40.run_vp), ("page", T40.run_page), ("f41", T41.run_f41), ("f42", T42.run_f42), ("f43", run_f43), ("live42", T42.run_live42)],
           script=__file__, live=(T40.LIVE_RB, "Skyy_SkyyRebirth"))
