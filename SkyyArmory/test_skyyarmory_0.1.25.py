"""Harness for SkyyArmory 0.1.25 (THE SOUL CAGE LINK for SkyyShards' totems; tools/armory_0_1_25_patch.py). Build first:
    python tools/armory_0_1_25_patch.py && python SkyyArmory/build_skyyarmory_0.1.25.py

    python SkyyArmory/test_skyyarmory_0.1.25.py [--jar <SkyyArmory-0.1.25.jar>] [--dir <scratch>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.1.24 -> 0.1.25: exactly the listed members differ (the version texts + setup / unpublish), SoulCageFn added; non-class: manifest only
  X   exec     EVERY NEW CODE PATH: armory:fn:soulcage for every Soul Orb / Cage id, an unknown id, "ladder" / null, {"essence", tier} for every
               tier + bad ones, bad arguments (never throws); the key is in the shutdown list
  D   live     START TWICE on a scratch COPY of the live Skyy_SkyyArmory (every migration + load): the 2nd start changes nothing, the file
               is not rewritten by 0.1.25 (no config change)
  AA  audit    the engine-access audit
Exit code 1 on any failure.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION, OLD = "0.1.25", "0.1.24"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyArmory-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyArmory-%s.jar" % OLD)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "shards02", "armory")))
PKG = "com.skyy.armory."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyArmory")
SOUL_IDS = ["Weapon_Wand_SoulOrb"] + ["Weapon_Wand_SoulCage_" + m for m in ("Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium")]
# the members 0.1.25 changes: the version texts (as 0.1.24's list: ArmoryCheck pack name, ArmoryCfg / CfgFile / CfgRows default file line,
# CfgFn / CfgRows header, the ready lines) + SkyyArmoryPlugin publish / unpublish (the new key)
EXPECT = {"ArmoryCfg": ["~m load", "~m reloadAll", "~m useDefaults"], "ArmoryCheck": ["~m packCheck", "~m packOf"], "CfgFn": ["~m opExport"],
          "CfgRows": ["~<clinit>", "~m header"], "SkyyArmoryPlugin": ["~m publish", "~m setup", "~m unpublish"]}
ADDED = ["SoulCageFn"]


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JArray, JObject, JString, JInt
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Fn = JClass(PKG + "SoulCageFn")
    f = Fn()
    got = [int(f.apply(i)) for i in SOUL_IDS]
    K.eq(got, list(range(8)), "X1: armory:fn:soulcage: the Soul Orb = 0, Copper .. Onyxium Soul Cage = 1 .. 7")
    K.eq([int(f.apply(x)) for x in ("Weapon_Wand_Copper", "", " Weapon_Wand_SoulOrb ")], [-1, -1, 0], "X1: not a soul item = -1 (the id is trimmed)")
    lad = ",".join("%s:%d" % (x, i) for i, x in enumerate(SOUL_IDS))
    K.eq((str(f.apply("ladder")), str(f.apply(None))), (lad, lad), "X1: ladder / null = every id with its place")
    ess = [f.apply(JArray(JObject)([JString("essence"), JInt(t)])) for t in range(-1, 9)]
    ess = [None if e is None else str(e) for e in ess]
    K.check(ess[0] is None and ess[-1] is None and ess[1] == "Ingredient_Life_Essence" and ess[8] == "Ingredient_Life_Essence_Concentrated"
            and all(e and e.startswith("Ingredient_") for e in ess[1:9]), "X1: {essence, tier} = the cage's essence (0 Life .. 7 Concentrated Life), bad tier = null: %s" % ess)
    K.check(f.apply(JArray(JObject)([JString("other"), JInt(1)])) is None and f.apply(JInt(3)) is None and f.apply(JArray(JObject)([])) is None,
            "X1: other arguments = null, never a throw")
    import zipfile
    with zipfile.ZipFile(jar) as z_:
        pl_ = z_.read("com/skyy/armory/SkyyArmoryPlugin.class")
    K.check(b"armory:fn:soulcage" in pl_ and b"SoulCageFn" in pl_, "X1: SkyyArmoryPlugin publishes armory:fn:soulcage (SoulCageFn) and lists it for the shutdown removal")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Cfg = JClass(PKG + "ArmoryCfg")
    Paths = JClass("java.nio.file.Paths")
    Cfg.DIR = Paths.get(home)
    Cfg.FILE = Paths.get(home).resolve("config.properties")
    f = os.path.join(home, "config.properties")
    before = open(f, "rb").read() if os.path.isfile(f) else None
    snaps = []
    for start in (1, 2):
        for m in ("migrate012", "migrate013", "migrate014", "migrate016", "migrate017", "migrate018", "migrate021"):
            getattr(Cfg, m)()
        Cfg.load()
        snaps.append(open(f, "rb").read() if os.path.isfile(f) else None)
    K.check(snaps[0] == snaps[1], "D: the 2nd start changes nothing")
    K.check(before is None or snaps[0] == before, "D: the live copy's config.properties is not rewritten by 0.1.25 (no config change): %s" % (before is not None))
    K.notes.append("D: live config.properties %s bytes" % (len(before) if before else 0))
    K.save()


if __name__ == "__main__":
    HK.run("SkyyArmory", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("exec", run_exec), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyArmory"))
