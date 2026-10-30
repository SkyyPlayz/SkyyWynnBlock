"""Harness for SkyyPets 0.4.22 (THE GEAR MANA % KEY: PetBuff.pctKey learns SkyyGear 0.3.52's skyygear_mana; tools/pets_0_4_22_patch.py).
Build first:
    python tools/pets_0_4_22_patch.py && python SkyyPets/build_skyypets_0.4.22.py
    python SkyyPets/test_skyypets_0.4.22.py [--keep]

  S     static   the patch re-runs to identical bytes; 0.4.21's patch still regenerates 0.4.21 byte for byte; no class / system / command
                 added; line endings kept; ONE "skyygear_mana" in the script (the pctKey line); the jar: no entry added / removed, the only
                 changed non-class entry = manifest.json
  A/C/AA          (tools/harness_kit.py, fresh child JVMs, -Xverify:all) verify, class compare 0.4.21 -> 0.4.22 (PetBuff.pctKey + the
                 version texts), engine-access audit
  PK    EXECUTED in a bare JVM with a stand-in stat store (SkyyAccessories 0.5.30's fake_stats): PetBuff.pctKey (skyygear_mana + every
                 old key skipped, a flat key not), PetBuff.flatOf on a modifier map, PetBuff.modPct on a REAL EntityStatMap - the pet Mana %
                 is a % of the FLAT max and stays steady with SkyyGear's skyygear_mana (and the other % layers) on the same stat
  rt    0.4.21's RT phase EXECUTED on this jar (the Hatchery tooltips / titles: unchanged)
  live  0.4.17's start-twice on a scratch COPY of the live Skyy_SkyyPets (no saved-data change)
NOT COVERED (UNVERIFIED in game): the Mana bar with a real pet + Swift / Sage armor on (the sum is executed here on a real EntityStatMap).
Exit code 1 on any failure.
"""
import os, sys, zipfile, importlib.util, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "aug2b", "pets")]
import skyybuild as B
import harness_kit as HK

_cmp0 = HK.run_compare
_eq00 = HK.Child.eq


def _mod(path, name):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    a = list(sys.argv)
    s.loader.exec_module(m)
    sys.argv[:] = a
    return m


T421 = _mod(os.path.join(HERE, "test_skyypets_0.4.21.py"), "test_skyypets_0_4_21")
TA30 = _mod(os.path.join(ROOT, "SkyyAccessories", "test_skyyaccessories_0.5.30.py"), "test_skyyaccessories_0_5_30")
HK.run_compare = _cmp0
HK.Child.eq = _eq00
T417 = T421.T417

VERSION = "0.4.22"
PKG = "com.skyy.pets."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyPets-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyPets-0.4.21.jar")
GEN = os.path.join(HERE, "build_skyypets_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyypets_0.4.21.py")
PATCH = os.path.join(TOOLS, "pets_0_4_22_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
T421.JAR = T421.T420.JAR = T421.T419.JAR = JAR
EXPECT = {   # the class compare 0.4.21 -> 0.4.22: PetBuff.pctKey + the version texts (the patch's finish() proves nothing else changed)
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'PetBuff': ['~m pctKey'],
    'PetsCfg': ['~m applyAll', '~m seed'],
    'PetsMigP5': ['~m mgLog', '~m run'],
    'PetsMigS2': ['~m run'],
    'PetsMigW15': ['~m run'],
    'SkyyPetsPlugin': ['~m setup'],
}
OLD_KEYS = ["skyypet_health", "skyypet_mana", "skyygear_hp", "skyygear_ut_hp", "skyyacc_mana", "skyyacc_health", "skyyskill_classhp", "skyyskill_rebirthmana"]


# ======================================================================================================== S: static
def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyPets 0.4.22 - build script') and g.count('VERSION = "0.4.22"') == 1, "S header + VERSION")
    K.check(g.count("registerCommand(") == o.count("registerCommand(") and g.count("registerSystem(") == o.count("registerSystem(") and g.count("= cls(") == o.count("= cls("),
            "S no class, system or command added")
    K.check(("\r\n" in g) == ("\r\n" in o), "S line endings kept")
    K.eq(g.count('"skyygear_mana"'), 1, "S one skyygear_mana in the script (PetBuff.pctKey)")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    for patch, ref in ((PATCH, GEN), (os.path.join(TOOLS, "pets_0_4_21_patch.py"), GEN_OLD)):
        cp = os.path.join(d, os.path.basename(ref))
        p = subprocess.run([sys.executable, patch, "--out", cp], capture_output=True, text=True)
        K.check(p.returncode == 0 and open(cp, "rb").read() == open(ref, "rb").read(), "S %s re-generates its script byte for byte: %s" % (os.path.basename(patch), p.stderr[-300:]))
    zn, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    nn, on = set(zn.namelist()), set(zo.namelist())
    K.eq(sorted(nn - on), [], "S the jar adds no entry")
    K.eq(sorted(on - nn), [], "S the jar removes nothing")
    K.eq(sorted(n for n in nn & on if not n.endswith(".class") and zn.read(n) != zo.read(n)), ["manifest.json"], "S changed non-class entries = manifest.json")
    K.save()


# ======================================================================================================== PK: the percent-layer key EXECUTED
def run_pk(out, jar, scratch, _home):
    from jpype import JClass, JInt, JFloat, JDouble, JLong, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    TA30.fake_stats(JClass)
    Bf = JClass(PKG + "PetBuff")
    ESM = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap")
    DST = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes")
    ET = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType")
    SMO = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier")
    MTG = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier$ModifierTarget")
    CAL = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier$CalculationType")
    K.check(bool(Bf.pctKey(JString("skyygear_mana"))), "PK pctKey skips SkyyGear 0.3.52's skyygear_mana")
    K.check(all(bool(Bf.pctKey(JString(k))) for k in OLD_KEYS), "PK pctKey still skips every older %% layer")
    K.check(not bool(Bf.pctKey(JString("skyyskill_classmana"))) and not bool(Bf.pctKey(JString("Armor"))), "PK a flat source (class Mana, Armor) is not skipped")
    mm = JClass("java.util.HashMap")()
    for k_, v_ in (("Armor", 50.0), ("skyyskill_classmana", 20.0), ("skyygear_mana", 40.0), ("skyyacc_mana", 30.0), ("skyypet_mana", 20.0)):
        mm.put(k_, SMO(MTG.MAX, CAL.ADDITIVE, JFloat(v_)))
    K.eq(float(Bf.flatOf(JFloat(100.0), mm)), 170.0, "PK flatOf = type max 100 + Armor 50 + class Mana 20 (Gear / accessory / pet Mana %% skipped)")
    MI = int(DST.getMana())
    hf = ET.class_.getDeclaredField("max")
    hf.setAccessible(True)
    hf.setFloat(ET.getAssetMap().getAsset(JInt(MI)), JFloat(100.0))
    m = ESM()
    m.update()
    m.putModifier(JInt(MI), "skyyskill_classmana", SMO(MTG.MAX, CAL.ADDITIVE, JFloat(50.0)))          # flat: 150
    m.putModifier(JInt(MI), "skyygear_mana", SMO(MTG.MAX, CAL.ADDITIVE, JFloat(9.3)))                  # SkyyGear's Swift / Sage Mana % (6.2 % of 150)
    amt = lambda: (lambda c: None if c is None else round(float(c.getAmount()), 3))(m.getModifier(JInt(MI), "skyypet_mana"))
    seq = []
    for t_ in range(4):
        Bf.modPct(m, JInt(MI), "skyypet_mana", JDouble(10.0), JLong(1000 + 1000 * t_))
        seq.append(amt())
    K.eq(seq, [15.0] * 4, "PK modPct on a REAL EntityStatMap: the pet Mana 10 %% = 15 of the FLAT 150, steady with skyygear_mana 9.3 on the stat (0.4.21 took 15.93)")
    m.putModifier(JInt(MI), "skyygear_mana", SMO(MTG.MAX, CAL.ADDITIVE, JFloat(30.0)))
    Bf.modPct(m, JInt(MI), "skyypet_mana", JDouble(10.0), JLong(9000))
    K.eq(amt(), 15.0, "PK ... and unchanged when Gear's Mana % grows (the two %% layers never feed each other)")
    K.check(abs(float(m.get(JInt(MI)).getMax()) - (150.0 + 30.0 + 15.0)) < 0.05, "PK max Mana = flat 150 + Gear 30 + pet 15 (%.2f)" % float(m.get(JInt(MI)).getMax()))
    hf.setFloat(ET.getAssetMap().getAsset(JInt(MI)), JFloat(0.0))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyPets", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("static", run_static), ("pk", run_pk), ("rt", T421.run_rt), ("live", T417.run_live)],
           script=__file__, live=(T421.T41.LIVE, "Skyy_SkyyPets"))
