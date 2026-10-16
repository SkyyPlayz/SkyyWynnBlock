"""Harness for SkyyClasses 0.1.31 (the great shield is a Spellblade weapon; tools/classes_0_1_31_patch.py; round armory0129 with SkyyArmory 0.1.29).
Build first:  python tools/classes_0_1_31_patch.py && python SkyyClasses/build_skyyclasses_0.1.31.py
              python SkyyClasses/test_skyyclasses_0.1.31.py [--keep]
Phases (tools/harness_kit.py, fresh child JVMs, -Xverify:all, TEMP / TMP in the scratch folder):
  A  verify   every class loads + initialises
  C  compare  0.1.30 -> 0.1.31: only ClassDefs' static tables differ (the Spellblade weapon rule + its card text); non-class: the manifest only
  X  exec     ClassDefs.ownerOf: every Weapon_GreatShield_<metal> -> Spellblade; vanilla shields stay the Warrior's; longswords stay the
              Spellblade's; an unknown Weapon_ id stays unassigned; the Spellblade card text names great shields; the bridge prefix list
              (class:weapons:Spellblade) carries Weapon_GreatShield_
  AA audit    the engine-access audit
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION, OLD = "0.1.31", "0.1.30"
JAR = os.path.join(HERE, "SkyyClasses-%s.jar" % VERSION)
OLD_JAR = os.path.join(HERE, "SkyyClasses-%s.jar" % OLD)
PKG = "com.skyy.classes."
SCRATCH = os.path.join(ROOT, "tools", "dev", "scratch", "armory0129", "classes")
EXPECT = {"ClassDefs": ["~<clinit>"],          # the rule + the card text
          "Abil": ["+m armoryLunge", "~m hitLanded3", "~m momTick", "~m momX"],          # fix round: lunge hits = no per-hit Momentum; keep half on a swap
          "SkyyClassesPlugin": ["~m setup", "~m shutdown"],          # + class:fn:momAdd (and the version text)
          "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "KitMigrate": ["~m runOnce"]}          # the version text only
ADDED = ["AbilMomAddFn"]


def run_exec(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    D = JClass(PKG + "ClassDefs")
    names = [str(x) for x in D.NAMES]
    sb, wa = names.index("Spellblade"), names.index("Warrior")
    gs = ["Weapon_GreatShield_" + m for m in ("Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium")]
    K.eq([int(D.ownerOf(i)) for i in gs], [sb] * 7, "X: every great shield -> Spellblade")
    K.eq([int(D.ownerOf(i)) for i in ("Weapon_Shield_Iron", "Weapon_Shield_Wood")], [wa, wa], "X: vanilla shields stay Warrior only")
    K.eq([int(D.ownerOf(i)) for i in ("Weapon_Longsword_Crude", "Zweihander", "Longsword_Iron_Red")], [sb] * 3, "X: the swords stay the Spellblade's")
    un = int(D.ownerOf("Weapon_Something_New"))
    K.check(un != sb and un != wa, "X: an unknown Weapon_ id is still unassigned (%d)" % un)
    K.check("Great Shields" in str(D.WTEXT[sb]), "X: the Spellblade card says it: %s" % D.WTEXT[sb])
    K.check("Weapon_GreatShield_" in str(D.prefixesOf(sb)).split(","), "X: class:weapons:Spellblade lists Weapon_GreatShield_")
    from jpype import JImplements, JOverride, JArray, JObject, JString
    A = JClass(PKG + "Abil")
    br = JClass(PKG + "ClassCfg").bridge()
    mine = JString("lunge-damage")

    @JImplements("java.util.function.Function")
    class Mine:
        @JOverride
        def apply(self, o):
            return JObject(str(o) == "lunge-damage", JClass("java.lang.Boolean"))
    K.check(not bool(A.armoryLunge(mine)), "X (fix 2): no SkyyArmory = an ordinary hit")
    br.put("armory:fn:mine", Mine())
    K.check(bool(A.armoryLunge(mine)) and not bool(A.armoryLunge(JString("sword-swing"))) and not bool(A.armoryLunge(None)),
            "X (fix 2): armory:fn:mine marks the lunge hits (no per-hit Momentum for them)")
    br.remove("armory:fn:mine")
    UUID = JClass("java.util.UUID")
    u = UUID.randomUUID()
    K.eq(len(A.momX(u)), 12, "X (fix 9): the Momentum state has the weapon-type slot (keep half on a sword <-> great shield swap)")
    F = JClass(PKG + "AbilMomAddFn")()
    OA = JArray(JClass("java.lang.Object"))
    I = JClass("java.lang.Integer")
    K.check(F.apply(None) is None and F.apply(OA([JString("x"), I(2)])) is None and F.apply(OA([u, I(0)])) is None and F.apply(OA([u, I(99)])) is None,
            "X (fix 2): class:fn:momAdd refuses junk (no UUID, 0, more than 10)")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyClasses", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("exec", run_exec)], script=__file__)
