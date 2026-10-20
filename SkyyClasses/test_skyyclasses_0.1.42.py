"""Harness for SkyyClasses 0.1.42 (SKILL TREES 3, the SkyyClasses half; tools/classes_0_1_42_patch.py). Build first:
    python tools/classes_0_1_42_patch.py && python SkyyClasses/build_skyyclasses_0.1.42.py
    python SkyyClasses/test_skyyclasses_0.1.42.py [--keep]
Phases (tools/harness_kit.py, fresh child JVMs, -Xverify:all, TEMP / TMP in tools/dev/scratch/st3r12/cls):
  A   verify   every class loads + initialises
  C   compare  0.1.41 -> 0.1.42: exactly the planned members (EXPECT)
  X   exec     AbilDefs.v3 / unlock (the tree:v3 flag drops the level gate; no flag / no tree gate = the abil.unlock levels); AbilModDefs.treeRank
               ("v3" lists only, sums never parsed past 100); Abil.modOk (a tree rank unlocks a modifier below its ability level; other
               modifiers keep the level rule); Abil.mlvlT (max(use level, 1) + ranks - 1); Abil.treeOwnsPick through the real tree:fn:abil call
               (one alt owned = the tree decides; both owned in a v3 tree = the player's pick); the cast refusal text
  AA  engine-access audit
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK

VERSION, OLD = "0.1.42", "0.1.41"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyClasses-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyClasses-%s.jar" % OLD)
PKG = "com.skyy.classes."
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "st3r12", "cls")))
ADDED = []
EXPECT = {
    "AbilDefs": ["+m v3", "~m unlock"],
    "AbilModDefs": ["+m treeRank"],
    "Abil": ["+m mlvlT", "~m modOk", "~m equipped", "~m ctxFor", "~m panel", "~m modRows", "~m equipMod", "~m treeOwnsPick", "~m castAt0",
             "~m bubPick", "~m holdText", "~m placeRow"],   # fix round: the v3 texts (Elemental Bubble, "not unlocked yet")
    "CfgRows": ["~m header"], "CfgFn": ["~m opExport"], "SkyyClassesPlugin": ["~m setup"], "KitMigrate": ["~m runOnce"],   # the version text
}


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    AD, AM, AB, AC, CC = J("AbilDefs"), J("AbilModDefs"), J("Abil"), J("AbilCfg"), J("ClassCfg")
    br = CC.bridge()
    br.remove("tree:v3")
    K.check(bool(AC.TREE_GATE) and not bool(AD.v3()), "X no tree:v3 flag -> no v3 (abil.treeGate on by default)")
    lv = [int(AD.unlock(t)) for t in range(5)]
    K.eq(lv, [int(AC.UNLOCK_A1), int(AC.UNLOCK_A2), int(AC.UNLOCK_A2X), int(AC.UNLOCK_A1X), int(AC.UNLOCK_A1X)], "X without the flag: the abil.unlock levels")
    br.put("tree:v3", "1")
    K.check(bool(AD.v3()) and [int(AD.unlock(t)) for t in range(5)] == [1] * 5, "X tree:v3 = 1 -> every ability tier unlocks at 1 (the tree's rows decide)")
    AC.TREE_GATE = False
    K.check(not bool(AD.v3()) and int(AD.unlock(3)) == int(AC.UNLOCK_A1X), "X abil.treeGate off -> the levels again")
    AC.TREE_GATE = True
    ai = int(AD.find("Meteor"))
    mi_p, mi_e = int(AM.find("Power")), int(AM.find("Echo"))
    csv = "v3,A1,A2,m.Meteor.Power=3,m.Meteor.Echo=1"
    K.eq((int(AM.treeRank(csv, "Meteor", mi_p)), int(AM.treeRank(csv, "Meteor", mi_e)), int(AM.treeRank(csv, "Meteor", int(AM.find("Radius"))))), (3, 1, 0),
         "X treeRank reads m.<Ability>.<Mod>=<ranks>")
    K.eq(int(AM.treeRank("A1,A2,m.Meteor.Power=3", "Meteor", mi_p)), 0, "X a list without v3 (an older SkyyTrees) has no ranks")
    K.eq(int(AM.treeRank("v3,m.Meteor.Power=9999", "Meteor", mi_p)), 100, "X ranks are capped at 100")
    pos_e = int(AM.pos(ai, mi_e))
    K.check(int(AM.unlockAt(pos_e)) > 1, "X Echo is a late modifier on Meteor (unlocks at ability Lv %d)" % int(AM.unlockAt(pos_e)))
    K.check(bool(AB.modOk(csv, ai, pos_e, 1)) and not bool(AB.modOk("v3,A1", ai, pos_e, 1)) and bool(AB.modOk("v3,A1", ai, pos_e, int(AM.unlockAt(pos_e)))),
            "X modOk: a tree rank unlocks Echo at ability Lv 1; without a rank the ability level rule stays")
    P = JClass("java.util.Properties")()
    K.eq(int(AB.mlvlT(P, "Meteor", mi_p, csv)), 3, "X mlvlT: no uses, 3 ranks -> level 3 (rank 1 = level 1, +1 a rank)")
    steps = [int(x) for x in AM.steps()]
    P.setProperty("m.Meteor.Power", str(steps[1]))
    base = int(AB.mlvl(P, "Meteor", mi_p))
    K.eq((int(AB.mlvlT(P, "Meteor", mi_p, csv)), int(AB.mlvlT(P, "Meteor", mi_p, "v3,A1")), int(AB.mlvlT(P, "Meteor", mi_p, None))), (base + 2, base, base),
         "X mlvlT: use level %d + 3 ranks -> %d; no rank / no tree = the use level" % (base, base + 2))
    # treeOwnsPick through the real bridge call (tree:fn:abil -> treeCsv)
    u = JClass("java.util.UUID").fromString("12345678-2222-3333-4444-555555555555")
    br.put("profile:class:" + str(u), "Warrior")
    ANS = ["v3,A1,A4a"]

    @JImplements("java.util.function.Function")
    class Abil(object):
        @JOverride
        def apply(self, a):
            return ANS[0]
    br.put("tree:fn:abil", Abil())
    J("AbilStore").TREEC.clear()
    K.check(bool(AB.treeOwnsPick(u)), "X one A1-alt in the v3 tree -> the tree decides the pick (as before)")
    ANS[0] = "v3,A1,A4a,A4b"
    J("AbilStore").TREEC.clear()
    K.check(not bool(AB.treeOwnsPick(u)), "X both A1-alts in a v3 tree -> the pick is the player's")
    ANS[0] = "A1,A4a,A4b"
    J("AbilStore").TREEC.clear()
    K.check(bool(AB.treeOwnsPick(u)), "X an older (non-v3) list with both -> unchanged rule")
    ANS[0] = None
    J("AbilStore").TREEC.clear()
    K.check(not bool(AB.treeOwnsPick(u)), "X no tree list -> no tree pick")
    # ---- fix round: the reader contract key Class.v3mods (SkyyTrees 0.4.0 sells modifier ranks only while it is listed) + the v3 texts
    import zipfile
    with zipfile.ZipFile(jar) as z:
        pl = [n for n in z.namelist() if n.endswith("/SkyyClassesPlugin.class")]
        raw = z.read(pl[0]) if pl else b""
    K.check(b"Class.v3mods" in raw and b"Class.Mage.PC2" in raw, "FIX tree:reads:SkyyClasses lists Class.v3mods (setup's reader list)")
    br.put("tree:v3", "1")
    try:
        t = str(AB.bubPick(u, "v3,A1,A2"))
    except Exception as e:
        t = "threw %s" % e
    K.check("coming soon to the Skill Trees 3 class tree" in t and "PB2" not in t, "FIX the bubble text under v3 names the v3 tree, not node PB2: %s" % t)
    br.remove("tree:v3")
    try:
        t2 = str(AB.bubPick(u, "A1,A2"))
    except Exception as e:
        t2 = "threw %s" % e
    K.check("(Aegis path, PB2) in your class tree" in t2, "FIX without tree:v3 the old text stays: %s" % t2)
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyClasses", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("exec", run_exec)], script=__file__)
