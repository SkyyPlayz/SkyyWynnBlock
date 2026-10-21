"""Harness for SkyyPets 0.4.6 (the rebirth pet XP: x (1 + rebirth:fn:stat "petecho" / 100) + rebirth:reads:SkyyPets; tools/pets_0_4_6_patch.py).
Build first: python tools/pets_0_4_6_patch.py; python SkyyPets/build_skyypets_0.4.6.py

    python SkyyPets/test_skyypets_0.4.6.py [--dir <folder inside tools/dev/scratch/>] [--keep]

  A / C / AA  (tools/harness_kit.py, fresh child JVMs, -Xverify:all) verify, class compare 0.4.5 -> 0.4.6 (exactly the planned members),
              engine-access audit
  V3          0.4.5's V3 phase on the 0.4.6 jar (the skill-tree pet rows unchanged)
  RBX         (fix round: the stat asked is "petecho" = Beastmastery Echo alone - "petxp" carries Insight + keep, which the skill XP a pet
              follows already has; the fake answers 999 for "petxp" so any use of it shows)
  RBX         EXECUTED: PetXp.give (the one path every pet XP takes) on a scratch record with a real pet: no SkyyRebirth = x1; petxp 50 =
              x1.5 exactly (on top of the pet's own rebirth bonus); a null answer (SkyyRebirth still loading) keeps 50; NaN / negative = x1;
              5000 = capped at +1000 %; another profile key has its own cache; a pet of another skill (XP_OTHER) is multiplied too; no
              slotted pet = the rebirth function is not even asked; rebirth:reads:SkyyPets = petxp put + removed (only our value)
  LIVE        0.4.5's LIVE phase (start twice on a scratch COPY of the live Skyy_SkyyPets: start 1 = only trees.properties if missing)
Exit code 1 on any failure.
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK

_cmp0 = HK.run_compare
_s45 = importlib.util.spec_from_file_location("test_skyypets_0_4_5", os.path.join(HERE, "test_skyypets_0.4.5.py"))
T45 = importlib.util.module_from_spec(_s45)
_s45.loader.exec_module(T45)
T44, T41 = T45.T44, T45.T41
HK.run_compare = _cmp0

VERSION = "0.4.6"
PKG = "com.skyy.pets."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyPets-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyPets-0.4.5.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "st3fix", "pets")))
T45.VERSION, T45.JAR = VERSION, JAR
EXPECT = {
    "PetXp": sorted(["+f RBX", "+f RBX_MAX", "+f RB_READS", "+f RB_STAT", "+m rbPct", "+m rbPctOf", "+m rbReads", "~<clinit>", "~m give"]),
    "SkyyPetsPlugin": ["~m setup", "~m shutdown"],
    "PetsCfg": ["~m applyAll", "~m seed"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],   # the version text
}
ADDED = []


def run_rbx(out, jar, scratch, _home):
    W = T44._world(out, jar, scratch, "rbx")
    K, JClass, JProxy = W["K"], W["JClass"], W["JProxy"]
    P_ = lambda n: JClass(PKG + n)
    Xp, Cfg = P_("PetXp"), P_("PetsCfg")
    BR = W["BR"]
    Dbl = JClass("java.lang.Double")
    ANS = {}
    ASKED = []

    def stat(a):
        ASKED.append((str(a[0]), str(a[1])))
        if str(a[1]) != "petecho":   # fix round: "petxp" (Insight + keep + Echo) would count Insight twice - a loud wrong answer
            return Dbl.valueOf(999.0)
        v = ANS.get(str(a[0]))
        return None if v is None else Dbl.valueOf(float(v))
    fn = JProxy("java.util.function.Function", dict={"apply": stat})
    u, k, r = T44._mk(W, 801)
    us = str(u)
    for kk, vv in (("kind", "Goat"), ("rarity", "1"), ("level", "1"), ("rebirth", str(int(Cfg.REB_MAX)))):   # the highest max level
        r.set("pet.g1.%s" % kk, vv)
    r.set("active.1", "g1")
    sk = str(Cfg.kind("Goat").skill)
    pct_own = int(Cfg.XP_OWN)

    PM = P_("PetMath")

    def total():   # every XP the pet holds: the levels' needs + the XP into the next level
        return sum(int(PM.need(l)) for l in range(2, int(r.levelOf("g1")) + 1)) + int(r.xpOf("g1"))

    def gain(amount=100, skill=None):
        x0 = total()
        Xp.give(u, skill or sk, amount)
        return total() - x0
    prb = 1.0 + float(Cfg.REB_XP) * int(r.rebirthOf("g1")) / 100.0   # the pet's own rebirth bonus (0.3.0) stays
    base = gain()
    K.check(base > 0 and abs(base - 100 * pct_own / 100.0 * prb) <= 1, "RBX no SkyyRebirth: the pet gets its own share x its own rebirth bonus (%d of 100 at %d %% x %.2f)" % (base, pct_own, prb))
    BR.put("rebirth:fn:stat", fn)
    ANS[us] = 50
    g50 = gain()
    K.check(abs(g50 - base * 1.5) <= 1 and ASKED[-1] == (us, "petecho"), "RBX petecho 50 -> x1.5 (%d -> %d), asked { UUID, petecho }" % (base, g50))
    ANS[us] = None
    K.check(abs(gain() - base * 1.5) <= 1, "RBX SkyyRebirth still loading (null) keeps the last answer (x1.5)")
    ANS[us] = float("nan")
    K.check(abs(gain() - base) <= 1, "RBX NaN = 0 %")
    ANS[us] = -20
    K.check(abs(gain() - base) <= 1, "RBX a negative answer = 0 %")
    ANS[us] = 5000
    g = gain()
    K.check(abs(g - base * 11) <= 1 and float(Xp.rbPct(u)) == 1000.0, "RBX capped at +1000 %% (x11): %d" % g)
    ANS[us] = 20
    K.check(abs(gain() - base * 1.2) <= 1, "RBX read live: 20 -> x1.2")
    # another profile of the same player: its own cache (no SkyyRebirth answer yet -> 0, never the other profile's 20)
    W["keys"][us] = "otherprofile"
    ANS[us] = None
    K.check(float(Xp.rbPct(u)) == 0.0, "RBX another profile key starts from its own (empty) cache")
    W["keys"].pop(us, None)
    ANS[us] = 20
    # a pet of another skill (XP_OTHER share) is multiplied too
    other = "Combat" if sk != "Combat" else "Mining"
    pct_other = int(Cfg.XP_OTHER)
    if pct_other > 0:
        g_o = gain(100, other)
        K.check(abs(g_o - 100 * pct_other / 100.0 * prb * 1.2) <= 1, "RBX the other-skill share (%d %%) x1.2 too: %d" % (pct_other, g_o))
    else:
        K.notes.append("RBX XP_OTHER is 0 - the other-skill share gives nothing (not multiplied)")
    # no slotted pet: the rebirth function is not asked at all
    r.set("active.1", "")
    n0 = len(ASKED)
    Xp.give(u, sk, 1000)
    K.check(len(ASKED) == n0, "RBX no slotted pet = SkyyRebirth is not asked")
    K.check(ASKED and set(x[1] for x in ASKED) == set(["petecho"]), "RBX fix round: only petecho was ever asked (never petxp = no Insight twice): %s" % sorted(set(x[1] for x in ASKED)))
    # rebirth:reads:SkyyPets
    Xp.rbReads(True)
    K.eq(str(BR.get("rebirth:reads:SkyyPets")), "petxp", "RBX rebirth:reads:SkyyPets = petxp")
    BR.put("rebirth:reads:SkyyPets", "someone-else")
    Xp.rbReads(False)
    K.eq(str(BR.get("rebirth:reads:SkyyPets")), "someone-else", "RBX shutdown removes only our own value")
    BR.put("rebirth:reads:SkyyPets", "petxp")
    Xp.rbReads(False)
    K.check(BR.get("rebirth:reads:SkyyPets") is None, "RBX ... and does remove ours")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyPets", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("v3", T45.run_v3), ("rbx", run_rbx), ("live", T45.run_live)], script=__file__, live=(T41.LIVE, "Skyy_SkyyPets"))
