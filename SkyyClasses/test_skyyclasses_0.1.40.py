"""Harness for SkyyClasses 0.1.40 (the /class cards show the primary + secondary weapon per class; the Priest's Soul Cage;
tools/classes_0_1_40_patch.py). Build first:
    python tools/classes_0_1_40_patch.py && python SkyyClasses/build_skyyclasses_0.1.40.py
    python SkyyClasses/test_skyyclasses_0.1.40.py [--keep]
Phases (tools/harness_kit.py, fresh child JVMs, -Xverify:all, TEMP / TMP in tools/dev/scratch/bcl/cls):
  A   verify   every class loads + initialises
  C   compare  0.1.39 -> 0.1.40: exactly the planned members (EXPECT); non-class entries = manifest.json only
  O   old      dumps every static field of ClassDefs on the OLD 0.1.39 jar (the baseline for X2)
  X   exec     X1 ClassDefs.ICONS = primary + secondary per class (Spellblade unchanged), the Priest / Mage words;
               X2 every other ClassDefs field (names, skills, kits, weapon rules, colours, roles, aliases ...) is identical to 0.1.39;
               X3 ClassArt.shownIcon: SkyyArmory loaded -> the Soul Cage / gauntlets, not loaded -> the vanilla stand-ins, vanilla ids as they
               are, null -> ""; cardIcons = emblem + the shown weapons (and without an emblem = the weapons)
  AA  engine-access audit
Not executed here (UNVERIFIED until the game): the real item asset map (Abil.runeLoaded's engine read, live since 0.1.36) and how the
icons look on the page.
"""
import os, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK

VERSION, OLD = "0.1.40", "0.1.39"
JAR = os.path.join(HERE, "SkyyClasses-%s.jar" % VERSION)
OLD_JAR = os.path.join(HERE, "SkyyClasses-%s.jar" % OLD)
PKG = "com.skyy.classes."
SCRATCH = os.path.join(TOOLS, "dev", "scratch", "bcl", "cls")
ADDED = []
EXPECT = {
    "ClassArt": ["+f OUR_IDS", "+f OUR_ALT", "+m shownIcon", "~m cardIcons", "~<clinit>"],
    "ClassDefs": ["~<clinit>"],                                                          # ICONS / DESCS / WTEXT
    "SkyyClassesPlugin": ["~m setup"],                                                   # the version text
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "KitMigrate": ["~m runOnce"],   # the version text
}
WANT_ICONS = ["Weapon_Shortbow_Iron,Weapon_Crossbow_Iron", "Weapon_Sword_Iron,Weapon_Spear_Iron", "Weapon_Staff_Iron,Weapon_Spellbook_Frost",
              "Weapon_Battleaxe_Iron,Weapon_Mace_Iron", "Weapon_Wand_Wood,Weapon_Wand_SoulCage_Copper", "Weapon_Daggers_Iron,Weapon_Kunai",
              "Weapon_Staff_Bo_Wood,Weapon_Fist_Gauntlets_Copper", "Weapon_Longsword_Iron,Weapon_Longsword_Spectral,Weapon_Longsword_Flame"]


def dump_defs():
    """every static field of ClassDefs as plain Python values"""
    from jpype import JClass
    C = JClass(PKG + "ClassDefs")
    Mod = JClass("java.lang.reflect.Modifier")
    Arr = JClass("java.lang.reflect.Array")
    out = {}
    for f in C.class_.getDeclaredFields():
        if not Mod.isStatic(f.getModifiers()):
            continue
        f.setAccessible(True)
        v = f.get(None)
        if v is not None and v.getClass().isArray():
            v = [str(Arr.get(v, i)) for i in range(Arr.getLength(v))]
        else:
            v = None if v is None else str(v)
        out[str(f.getName())] = v
    return out


def run_old(out, jar, scratch, _home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, OLD_JAR], verify=True)
    d = dump_defs()
    json.dump(d, open(os.path.join(scratch, "old-defs.json"), "w"))
    K.check(len(d) > 10 and "ICONS" in d, "O: ClassDefs of 0.1.39 dumped (%d fields)" % len(d))
    K.save()


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    new = dump_defs()
    old = json.load(open(os.path.join(scratch, "old-defs.json")))
    names = new["NAMES"]
    K.eq(names, ["Archer", "Warrior", "Mage", "Berserker", "Priest", "Assassin", "Monk", "Spellblade"], "X1: the class roster")
    K.eq(new["ICONS"], WANT_ICONS, "X1: ICONS = primary + secondary per class (Spellblade unchanged)")
    K.eq(new["ICONS"][7], old["ICONS"][7], "X1: the Spellblade's icons as 0.1.39")
    K.check(all(n.split(",")[0] == o.split(",")[0] for n, o in zip(new["ICONS"], old["ICONS"])), "X1: every first icon (the Abilities page's fallback) unchanged")
    pi, mi = names.index("Priest"), names.index("Mage")
    K.eq(new["WTEXT"][pi], "Wands / Soul Cages", "X1: the Priest's weapon text")
    K.eq(new["WTEXT"][mi], "Staves / Spellbooks", "X1: the Mage's weapon text")
    K.check("Soul Cage" in new["DESCS"][pi] and "spellbook" not in new["DESCS"][pi].lower()
            and new["DESCS"][pi].replace("Wand and Soul Cage hits", "Wand hits") == old["DESCS"][pi],
            "X1: the Priest description names the Soul Cage, the rest as 0.1.39: %r" % new["DESCS"][pi])
    diff = sorted(k for k in set(old) | set(new) if old.get(k) != new.get(k))
    K.eq(diff, ["DESCS", "ICONS", "WTEXT"], "X2: only ICONS / DESCS / WTEXT changed in ClassDefs (kits, rules, names, skills ... identical)")
    K.check([i for i, (a, b) in enumerate(zip(old["WTEXT"], new["WTEXT"])) if a != b] == [pi]
            and [i for i, (a, b) in enumerate(zip(old["DESCS"], new["DESCS"])) if a != b] == [pi], "X2: only the Priest's texts changed")
    # X3 shownIcon / cardIcons: Abil.ITEMS = the item-asset seam runeLoaded asks first
    A, CA = JClass(PKG + "Abil"), JClass(PKG + "ClassArt")
    Bool = JClass("java.lang.Boolean")
    LOADED = {"s": set()}

    @JImplements("java.util.function.Function")
    class Items(object):
        @JOverride
        def apply(self, o):
            return Bool.valueOf(str(o) in LOADED["s"])
    A.ITEMS = Items()
    K.eq([str(x) for x in CA.OUR_IDS], ["Weapon_Fist_Gauntlets_Copper", "Weapon_Wand_SoulCage_Copper"], "X3: OUR_IDS")
    K.eq([str(x) for x in CA.OUR_ALT], ["Weapon_Staff_Bo_Bamboo", "Weapon_Wand_Tribal"], "X3: OUR_ALT")
    LOADED["s"] = set()
    K.eq(str(CA.shownIcon("Weapon_Wand_SoulCage_Copper")), "Weapon_Wand_Tribal", "X3: no SkyyArmory -> the Priest's vanilla stand-in")
    K.eq(str(CA.shownIcon("Weapon_Fist_Gauntlets_Copper")), "Weapon_Staff_Bo_Bamboo", "X3: no SkyyArmory -> the Monk's vanilla stand-in")
    K.eq(str(CA.shownIcon("Weapon_Sword_Iron")), "Weapon_Sword_Iron", "X3: a vanilla id as it is (never asked)")
    K.eq(str(CA.shownIcon(None)), "", "X3: null -> empty")
    no_emb = [str(x) for x in CA.cardIcons(pi, True)]
    K.eq(no_emb, ["Weapon_Wand_Wood", "Weapon_Wand_Tribal"], "X3: Priest card without SkyyArmory / emblem items = wand + stand-in")
    LOADED["s"] = {"Weapon_Wand_SoulCage_Copper", "Weapon_Fist_Gauntlets_Copper"}
    K.eq(str(CA.shownIcon("Weapon_Wand_SoulCage_Copper")), "Weapon_Wand_SoulCage_Copper", "X3: SkyyArmory loaded -> the Soul Cage")
    K.eq([str(x) for x in CA.cardIcons(names.index("Monk"), True)], ["Weapon_Staff_Bo_Wood", "Weapon_Fist_Gauntlets_Copper"],
         "X3: Monk card (no emblem loaded) = bo staff + gauntlets")
    emb_p, emb_l = str(CA.EMB[pi]), str(CA.EMBL[pi])
    LOADED["s"] = {"Weapon_Wand_SoulCage_Copper", emb_p, emb_l}
    K.eq([str(x) for x in CA.cardIcons(pi, True)], [emb_p, "Weapon_Wand_Wood", "Weapon_Wand_SoulCage_Copper"],
         "X3: Priest card = emblem + wand + Soul Cage")
    K.eq([str(x) for x in CA.cardIcons(pi, False)][0], emb_l, "X3: a locked class shows the Locked emblem first")
    LOADED["s"] = {str(CA.EMB[7])}
    K.eq([str(x) for x in CA.cardIcons(7, True)], [str(CA.EMB[7])] + WANT_ICONS[7].split(","), "X3: Spellblade card = emblem + 3 longswords (as 0.1.39)")
    K.eq(len(CA.cardIcons(99, True)), 0, "X3: an unknown class -> no icons, no throw")
    A.ITEMS = None
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyClasses", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("old", run_old), ("exec", run_exec)], script=__file__)
