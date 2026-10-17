"""Harness for SkyyProfiles 0.1.17 (round emblems: the class emblems on the profile cards; tools/profiles_0_1_17_patch.py; with SkyyClasses
0.1.36 + SkyyTrees 0.3.22). Build first:
    python tools/profiles_0_1_17_patch.py && python SkyyProfiles/build_skyyprofiles_0.1.17.py
    python SkyyProfiles/test_skyyprofiles_0.1.17.py [--keep]
Phases (tools/harness_kit.py, fresh child JVMs, -Xverify:all, TEMP / TMP in tools/dev/scratch/emblems/prof):
  A   verify   every class loads + initialises
  C   compare  0.1.16 -> 0.1.17: exactly the planned members (EXPECT); non-class entries: manifest.json only
  X   exec     ProfRoster on a stand-in skyy.bridge:
               X1 no class:fn:emblem (no SkyyClasses 0.1.36) = today's look: iconOf = the first weapon / the Create-new orb; cardIcons = the weapons
               X2 with a stand-in class:fn:emblem: iconOf = the emblem (an alias goes through canon: Shaman -> Monk), no class = the orb,
                  an unknown class = the weapon fallback; cardIcons = emblem + 2 weapons (Locked while the class is not released); a
                  throwing / non-String answer = today's look
               X3 the Create Profile page calls cardIcons, the profile list iconOf (bytecode)
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

VERSION = "0.1.17"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyProfiles-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyProfiles-0.1.16.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "emblems", "prof")))
PKG = "com.skyy.profiles."
EXPECT = {"ProfRoster": ["+m cardIcons", "+m emblem", "~m iconOf"],   # the emblem through class:fn:emblem
          "ProfilePage": ["~m buildCreate"],                            # the Create Profile class cards: cardIcons
          # the version texts only
          "SkyyProfilesPlugin": ["~m setup"], "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "ProfCfg": ["~m capMigrate"],
          "ProfDel": ["~m archiveLocked"]}
ADDED = []


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    R, Cfg = JClass(PKG + "ProfRoster"), JClass(PKG + "ProfCfg")
    br = Cfg.bridge()
    br.remove("class:fn:emblem")
    br.remove("class:list")

    @JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def apply(self, o):
            return self.f(o)
    names = [str(x) for x in R.NAMES]
    icons = [str(x).split(",") for x in R.ICONS]
    # ---- X1 no bridge
    for n, w in zip(names, icons):
        K.eq(str(R.iconOf(n)), w[0], "X1: %s profile card without class:fn:emblem = its first weapon" % n)
        K.eq([str(x) for x in R.cardIcons(n, ",".join(w), True)], w, "X1: %s Create card without the bridge = its weapons" % n)
    K.eq(str(R.iconOf("")), str(R.NEW_ICON), "X1: no class = the Create-new orb")
    K.eq(str(R.iconOf(None)), str(R.NEW_ICON), "X1: null class = the Create-new orb")
    # ---- X2 a stand-in bridge
    asked = []

    def em(o):
        s = str(o)
        asked.append(s)
        base, _, lk = s.partition(":")
        if base not in names:
            return JString("")
        return JString("SkyyClasses_Emblem_" + base + ("_Locked" if lk == "locked" else ""))
    br.put("class:fn:emblem", Fn(em))
    for n, w in zip(names, icons):
        K.eq(str(R.iconOf(n)), "SkyyClasses_Emblem_" + n, "X2: %s profile card = its emblem" % n)
        K.eq([str(x) for x in R.cardIcons(n, ",".join(w), True)], ["SkyyClasses_Emblem_" + n] + w[:2], "X2: %s Create card = emblem + 2 weapons" % n)
        K.eq([str(x) for x in R.cardIcons(n, ",".join(w), False)][0], "SkyyClasses_Emblem_%s_Locked" % n, "X2: %s not released = the Locked emblem" % n)
        K.check(len(R.cardIcons(n, ",".join(w), True)) <= 3, "X2: %s Create card stays within its 3 cells" % n)
    del asked[:]
    K.eq(str(R.iconOf("Shaman")), "SkyyClasses_Emblem_Monk", "X2: an old class name goes through canon (Shaman -> Monk)")
    K.eq(asked, ["Monk"], "X2: ... the bridge is asked for Monk")
    K.eq(str(R.iconOf("")), str(R.NEW_ICON), "X2: no class = still the Create-new orb (the bridge not asked)")
    K.eq(str(R.iconOf("Necromancer")), str(R.EXTRA_ICON), "X2: an unknown class = the weapon fallback")
    br.put("class:fn:emblem", Fn(lambda o: 5))
    K.eq(str(R.iconOf(names[0])), icons[0][0], "X2: a non-String answer = today's look")

    def boom(o):
        raise RuntimeError("boom")
    br.put("class:fn:emblem", Fn(boom))
    K.eq(str(R.iconOf(names[0])), icons[0][0], "X2: a throwing bridge = today's look (never throws)")
    K.eq([str(x) for x in R.cardIcons(names[0], ",".join(icons[0]), True)], icons[0], "X2: ... and the Create card keeps its weapons")
    br.remove("class:fn:emblem")
    # ---- X3 bytecode
    gr = PW.calls(jar)
    K.check(PKG + "ProfRoster.cardIcons" in gr.get("ProfilePage.buildCreate", set()), "X3: the Create Profile cards use cardIcons (bytecode)")
    K.check(PKG + "ProfRoster.iconOf" in gr.get("ProfilePage.buildList", set()), "X3: the profile list still uses iconOf (bytecode)")
    K.check(PKG + "ProfRoster.emblem" in gr.get("ProfRoster.iconOf", set()), "X3: iconOf asks emblem first (bytecode)")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyProfiles", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("exec", run_exec)], script=__file__)
