"""Harness for SkyyArmory 0.1.30 (ONE BOSS SIGIL ROLL; tools/armory_0_1_30_patch.py). Build first:
    python tools/armory_0_1_30_patch.py && python SkyyArmory/build_skyyarmory_0.1.30.py

    python SkyyArmory/test_skyyarmory_0.1.30.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.1.29 -> 0.1.30: exactly SoulDrop.sigil + its new counter GEARSKIP (+ the version texts) differ; non-class: the manifest
  X   exec     SoulDrop.sigil: the bridge key gear:sigil:drops TRUE (SkyyGear 0.3.14 rolls) = no Armory Sigil, counted; FALSE / absent = the
               0.1.29 roll exactly (the same Sigil at the same roll, the same zone rules); a plain mob never
  D   live     START TWICE on a scratch COPY of the live NewBetaTest Skyy_SkyyArmory: nothing rewritten
  AA  audit    the engine-access audit
Exit code 1 on any failure.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION, OLD = "0.1.30", "0.1.29"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyArmory-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyArmory-%s.jar" % OLD)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "farm01", "armory")))
PKG = "com.skyy.armory."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyArmory")
EXPECT = {"SoulDrop": ["~<clinit>", "+f GEARSKIP", "~m sigil"],
          # the version text "0.1.30" only (ldc strings in the loader / pack check / export / Server Setup header / ready line)
          "ArmoryCfg": ["~m load", "~m reloadAll", "~m useDefaults"], "ArmoryCheck": ["~m packCheck", "~m packOf"], "CfgFn": ["~m opExport"],
          "CfgRows": ["~<clinit>", "~m header"], "SkyyArmoryPlugin": ["~m setup", "~m start"]}


def run_exec(out, jar, scratch, home):
    from jpype import JClass, JObject, JBoolean, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    SD = JClass(PKG + "SoulDrop")
    Defs = JClass(PKG + "ArmoryDefs")
    Cfg = JClass(PKG + "ArmoryCfg")
    Bool_ = JClass("java.lang.Boolean")
    Cfg.useDefaults()

    @JImplements("java.util.function.Predicate")
    class AllItems(object):
        @JOverride
        def test(self, o):
            return True
    SD.ITEMOK = AllItems()
    br = Defs.bridge()
    br.remove("gear:sigil:drops")

    def roll(role, zone, x):
        SD.ROLL = float(x)
        r = SD.sigil(role, zone, False)
        return None if r is None else str(r)
    base = [(r_, z_, x_, roll(r_, z_, x_)) for r_ in ("Dragon_Fire", "Goblin_Duke", "Trork_Warrior") for z_ in (1, 2, 3, 4) for x_ in (0.1, 1.0, 2.0, 3.5, 50.0)]
    got_any = [b for b in base if b[3] is not None]
    K.check(got_any and all(b[0] != "Trork_Warrior" for b in got_any), "X: without SkyyGear's key the 0.1.29 boss roll runs (%d of %d rolls give a Sigil, never a plain mob)" % (len(got_any), len(base)))
    s0 = int(SD.GEARSKIP)
    br.put("gear:sigil:drops", JObject(JBoolean(True), Bool_))
    on = [roll(r_, z_, x_) for r_, z_, x_, _w in base]
    K.check(all(v is None for v in on) and int(SD.GEARSKIP) - s0 == len([b for b in base if b[0] != "Trork_Warrior"]),
            "X: gear:sigil:drops TRUE (SkyyGear 0.3.14 rolls) = no Armory boss Sigil ever, each boss kill counted in GEARSKIP (%d)" % (int(SD.GEARSKIP) - s0))
    br.put("gear:sigil:drops", JObject(JBoolean(False), Bool_))
    off = [(r_, z_, x_, roll(r_, z_, x_)) for r_, z_, x_, _w in base]
    K.eq(off, base, "X: gear:sigil:drops FALSE (Gear's row off) = exactly the 0.1.29 rolls")
    br.put("gear:sigil:drops", "yes")
    K.eq([(r_, z_, x_, roll(r_, z_, x_)) for r_, z_, x_, _w in base], base, "X: a non-Boolean value counts as absent")
    br.remove("gear:sigil:drops")
    SD.ROLL = -1.0
    SD.ITEMOK = None
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
    K.check(before is None or snaps[0] == before, "D: the live copy's config.properties is not rewritten by 0.1.30")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyArmory", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("exec", run_exec), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyArmory"))
