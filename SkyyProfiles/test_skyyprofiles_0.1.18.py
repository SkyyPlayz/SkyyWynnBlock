"""Harness for SkyyProfiles 0.1.18 (bigger Create Profile class cards + emblem / primary / secondary weapon per class;
tools/profiles_0_1_18_patch.py). Build first:
    python tools/profiles_0_1_18_patch.py && python SkyyProfiles/build_skyyprofiles_0.1.18.py
    python SkyyProfiles/test_skyyprofiles_0.1.18.py [--keep]
Phases (tools/harness_kit.py, fresh child JVMs, -Xverify:all, TEMP / TMP in tools/dev/scratch/prof18/prof):
  A   verify   every class loads + initialises
  C   compare  0.1.17 -> 0.1.18: exactly the planned members (EXPECT); non-class entries: manifest.json only
  X   exec     ProfRoster on a stand-in skyy.bridge:
               X1 no class:fn:emblem (no SkyyClasses 0.1.36) = today's look: iconOf = the first weapon / the Create-new orb; cardIcons = the weapons
               X2 with a stand-in class:fn:emblem: iconOf = the emblem (an alias goes through canon: Shaman -> Monk), no class = the orb,
                  an unknown class = the weapon fallback; cardIcons = emblem + 2 weapons (Locked while the class is not released); a
                  throwing / non-String answer = today's look
               X3 the Create Profile page calls cardIcons, the profile list iconOf (bytecode)
  Y   0.1.18 (exec): two weapons per class = Skyy's primary + secondary table; SkyyArmory's soul cage / gauntlets show their vanilla
               stand-in when their asset is not loaded (this JVM has no assets); vanilla ids pass through shownIcon unchanged;
               the Create Profile markup: 140 px cards, 108 px item frames, the 24 px name; the profile list keeps 92 / 64
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

VERSION = "0.1.18"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyProfiles-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyProfiles-0.1.17.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "prof18", "prof")))
PKG = "com.skyy.profiles."
EXPECT = {"ProfRoster": ["+f OUR_ALT", "+f OUR_IDS", "+m shownIcon", "~<clinit>", "~m cardIcons"],   # 0.1.18: primary + secondary, SkyyArmory stand-ins
          "ProfilePage": ["~<clinit>", "~m buildCreate"],               # the bigger Create Profile class cards (CREATE_HS)
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
    our = dict(zip([str(x) for x in R.OUR_IDS], [str(x) for x in R.OUR_ALT]))
    shown = [[our.get(x, x) for x in w] for w in icons]      # 0.1.18: no assets in this JVM = SkyyArmory's items show their stand-in
    # ---- X1 no bridge
    for n, w, sw in zip(names, icons, shown):
        K.eq(str(R.iconOf(n)), w[0], "X1: %s profile card without class:fn:emblem = its first weapon" % n)
        K.eq([str(x) for x in R.cardIcons(n, ",".join(w), True)], sw, "X1: %s Create card without the bridge = its weapons" % n)
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
    for n, w, sw in zip(names, icons, shown):
        K.eq(str(R.iconOf(n)), "SkyyClasses_Emblem_" + n, "X2: %s profile card = its emblem" % n)
        K.eq([str(x) for x in R.cardIcons(n, ",".join(w), True)], ["SkyyClasses_Emblem_" + n] + sw[:2], "X2: %s Create card = emblem + 2 weapons" % n)
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
    K.eq([str(x) for x in R.cardIcons(names[0], ",".join(icons[0]), True)], shown[0], "X2: ... and the Create card keeps its weapons")
    br.remove("class:fn:emblem")
    # ---- X3 bytecode
    gr = PW.calls(jar)
    K.check(PKG + "ProfRoster.cardIcons" in gr.get("ProfilePage.buildCreate", set()), "X3: the Create Profile cards use cardIcons (bytecode)")
    K.check(PKG + "ProfRoster.iconOf" in gr.get("ProfilePage.buildList", set()), "X3: the profile list still uses iconOf (bytecode)")
    K.check(PKG + "ProfRoster.emblem" in gr.get("ProfRoster.iconOf", set()), "X3: iconOf asks emblem first (bytecode)")
    # ---- Y 0.1.18: Skyy's primary + secondary table (2026-10-18; Warrior = "Sword + Spear (Recommended)")
    want = {"Archer": ["Weapon_Shortbow_Iron", "Weapon_Crossbow_Iron"], "Warrior": ["Weapon_Sword_Iron", "Weapon_Spear_Iron"],
            "Mage": ["Weapon_Staff_Iron", "Weapon_Spellbook_Frost"], "Berserker": ["Weapon_Battleaxe_Iron", "Weapon_Mace_Iron"],
            "Priest": ["Weapon_Wand_Wood", "Weapon_Wand_SoulCage_Copper"], "Assassin": ["Weapon_Daggers_Iron", "Weapon_Kunai"],
            "Monk": ["Weapon_Staff_Bo_Wood", "Weapon_Fist_Gauntlets_Copper"],
            "Spellblade": ["Weapon_Longsword_Spectral", "Weapon_Longsword_Flame"]}
    K.eq(dict(zip(names, icons)), want, "Y1: the fallback table = emblem + Skyy's primary + secondary weapon per class")
    K.eq(our, {"Weapon_Wand_SoulCage_Copper": "Weapon_Spellbook_Grimoire_Brown", "Weapon_Fist_Gauntlets_Copper": "Weapon_Staff_Bo_Bamboo"},
         "Y1: SkyyArmory's items + their vanilla stand-ins (0.1.17's icons)")
    K.eq(str(R.shownIcon("Weapon_Wand_SoulCage_Copper")), "Weapon_Spellbook_Grimoire_Brown", "Y2: no soul cage asset loaded = the stand-in")
    K.eq(str(R.shownIcon("Weapon_Fist_Gauntlets_Copper")), "Weapon_Staff_Bo_Bamboo", "Y2: no gauntlet asset loaded = the stand-in")
    K.eq(str(R.shownIcon("Weapon_Sword_Iron")), "Weapon_Sword_Iron", "Y2: a vanilla id as it is")
    K.eq(str(R.shownIcon(None)), "", "Y2: null = empty (never throws)")
    br.put("class:fn:emblem", Fn(em))
    K.eq([str(x) for x in R.cardIcons("Priest", R.ICONS[names.index("Priest")], True)],
         ["SkyyClasses_Emblem_Priest", "Weapon_Wand_Wood", "Weapon_Spellbook_Grimoire_Brown"], "Y2: Priest card without SkyyArmory = emblem + wand + stand-in")
    br.remove("class:fn:emblem")
    wt = dict(zip(names, [str(x) for x in R.WTEXT]))
    K.eq((wt["Priest"], wt["Mage"]), ("Wands / Soul Cages", "Staves / Spellbooks"), "Y1: the weapon texts match the icons")
    pd = str(R.DESCS[names.index("Priest")])
    K.check("Soul Cage" in pd and "spellbook" not in pd.lower(), "Y1: the Priest description names the Soul Cage, no spellbook")
    K.check(PKG + "ProfRoster.shownIcon" in gr.get("ProfRoster.cardIcons", set()), "Y2: cardIcons maps the weapons through shownIcon (bytecode)")
    import zipfile
    page = zipfile.ZipFile(jar).read("com/skyy/profiles/ProfilePage.class").decode("latin-1")
    K.check("Height: 140" in page and "Width: 108, Height: 108" in page and "FontSize: 24" in page,
            "Y3: the Create Profile markup has the 140 px cards, 108 px item frames and the 24 px class name")
    K.check("Height: 92" in page and "Width: 64, Height: 64" in page, "Y3: the profile list keeps the 92 px SKYY CARD with 64 px frames")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyProfiles", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("exec", run_exec)], script=__file__)
