"""Harness for SkyyAccessories 0.5.35 (THE GEAR MANA % KEY: AccEffects.pctKey learns SkyyGear 0.3.52's skyygear_mana;
tools/accessories_0_5_35_patch.py). Build first:
    python tools/accessories_0_5_35_patch.py && python SkyyAccessories/build_skyyaccessories_0.5.35.py
    python SkyyAccessories/test_skyyaccessories_0.5.35.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  S     static   the patch re-runs to identical bytes; 0.5.34's patch still regenerates 0.5.34 byte for byte; no new system / command /
                 class; line endings kept; ONE "skyygear_mana" in the script (the pctKey line); the jar: no entry added / removed, the only
                 changed non-class entry = manifest.json
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.5.34 -> 0.5.35 (AccEffects.pctKey + the version texts)
  PK    EXECUTED in a bare JVM with a stand-in stat store (0.5.30's fake_stats): AccEffects.pctKey (skyygear_mana + every old key skipped,
                 a flat key not), AccEffects.flatOf on a modifier map, AccEffects.manaMod2 + manaMod on a REAL EntityStatMap (the accessory
                 Mana % = a % of the FLAT max, steady with SkyyGear's skyygear_mana on the stat), AccEffects.hpPct unchanged
  LIVE  0.5.34's start twice on a scratch COPY of Skyy's live NewBetaTest Skyy_SkyyAccessories (start 2 changes nothing)
  AA    engine-access audit
NOT COVERED (UNVERIFIED in game): the Mana bar with real accessories + Swift / Sage armor on (the sum is executed on a real EntityStatMap).
Scratch: tools/dev/scratch/aug2b/acc (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "aug2b", "acc")]
import harness_kit as HK
import skyybuild as B

_cmp0 = HK.run_compare
_eq00 = HK.Child.eq


def _mod(path, name):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    a = list(sys.argv)
    s.loader.exec_module(m)
    sys.argv[:] = a
    return m


T534 = _mod(os.path.join(HERE, "test_skyyaccessories_0.5.34.py"), "test_skyyaccessories_0_5_34")
TA30 = _mod(os.path.join(HERE, "test_skyyaccessories_0.5.30.py"), "test_skyyaccessories_0_5_30")
HK.run_compare = _cmp0          # back to the plain compare: 0.5.35 changes only manifest.json outside the classes
HK.Child.eq = _eq00

VERSION, OLD = "0.5.35", "0.5.34"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyAccessories-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyAccessories-%s.jar" % OLD)
GEN = os.path.join(HERE, "build_skyyaccessories_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyaccessories_%s.py" % OLD)
PATCH = os.path.join(ROOT, "tools", "accessories_0_5_35_patch.py")
PKG = "com.skyy.accessories."
SCRATCH = os.path.abspath(HK.arg("--dir"))
LIVE_DIR = T534.LIVE_DIR
EXPECT = {
    "AccEffects": ["~m pctKey"],          # THE change
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "SkyyAccessoriesPlugin": ["~m setup"],          # the version texts
}
OLD_KEYS = ["skyyacc_health", "skyyacc_mana", "skyygear_hp", "skyygear_ut_hp", "skyypet_health", "skyypet_mana", "skyyskill_classhp", "skyyskill_rebirthmana"]


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyAccessories 0.5.35 - build script') and g.count('VERSION = "0.5.35"') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand(", "makeClass("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.check(("\r\n" in g) == ("\r\n" in o), "S line endings kept")
    K.eq(g.count('"skyygear_mana"'), 1, "S one skyygear_mana in the script (AccEffects.pctKey)")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    for patch, ref in ((PATCH, GEN), (os.path.join(ROOT, "tools", "accessories_0_5_34_patch.py"), GEN_OLD)):
        cp = os.path.join(d, os.path.basename(ref))
        p = subprocess.run([sys.executable, patch, "--out", cp], capture_output=True, text=True)
        K.check(p.returncode == 0 and open(cp, "rb").read() == open(ref, "rb").read(), "S %s re-generates its script byte for byte: %s" % (os.path.basename(patch), p.stderr[-300:]))
    zn, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    nn, on = set(zn.namelist()), set(zo.namelist())
    K.eq(sorted(nn ^ on), [], "S the jar adds / removes no entry")
    K.eq(sorted(n for n in nn & on if not n.endswith(".class") and zn.read(n) != zo.read(n)), ["manifest.json"], "S changed non-class entries = manifest.json")
    K.save()


def run_pk(out, jar, scratch, _home):
    from jpype import JClass, JInt, JFloat, JDouble, JLong, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    TA30.fake_stats(JClass)
    E = JClass(PKG + "AccEffects")
    ESM = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap")
    DST = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes")
    ET = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType")
    SMO = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier")
    MTG = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier$ModifierTarget")
    CAL = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier$CalculationType")
    K.check(bool(E.pctKey(JString("skyygear_mana"))), "PK pctKey skips SkyyGear 0.3.52's skyygear_mana")
    K.check(all(bool(E.pctKey(JString(k))) for k in OLD_KEYS), "PK pctKey still skips every older %% layer")
    K.check(not bool(E.pctKey(JString("skyyskill_classmana"))) and not bool(E.pctKey(JString("Armor"))), "PK a flat source (class Mana, Armor) is not skipped")
    mm = JClass("java.util.HashMap")()
    for k_, v_ in (("Armor", 50.0), ("skyyskill_classmana", 20.0), ("skyygear_mana", 40.0), ("skyypet_mana", 20.0), ("skyyacc_mana", 30.0)):
        mm.put(k_, SMO(MTG.MAX, CAL.ADDITIVE, JFloat(v_)))
    K.eq(float(E.flatOf(JFloat(100.0), mm)), 170.0, "PK flatOf = type max 100 + Armor 50 + class Mana 20 (Gear / pet / accessory Mana %% skipped)")
    MI = int(DST.getMana())
    hf = ET.class_.getDeclaredField("max")
    hf.setAccessible(True)
    hf.setFloat(ET.getAssetMap().getAsset(JInt(MI)), JFloat(100.0))
    m = ESM()
    m.update()
    m.putModifier(JInt(MI), "skyyskill_classmana", SMO(MTG.MAX, CAL.ADDITIVE, JFloat(50.0)))          # flat: 150
    m.putModifier(JInt(MI), "skyygear_mana", SMO(MTG.MAX, CAL.ADDITIVE, JFloat(9.3)))                  # SkyyGear's Swift / Sage Mana %
    m.putModifier(JInt(MI), "skyypet_mana", SMO(MTG.MAX, CAL.ADDITIVE, JFloat(15.0)))
    amt = lambda: (lambda c: None if c is None else round(float(c.getAmount()), 3))(m.getModifier(JInt(MI), "skyyacc_mana"))
    seq = []
    for _ in range(3):
        E.manaMod(m, JInt(MI), "skyyacc_mana", JFloat(10.0), JFloat(0.0))
        seq.append(amt())
    for _ in range(3):
        E.manaMod2(m, JInt(MI), "skyyacc_mana", JFloat(10.0), JFloat(0.0), JFloat(2.0))
        seq.append(amt())
    K.eq(seq, [15.0, 15.0, 15.0, 17.0, 17.0, 17.0], "PK manaMod / manaMod2 on a REAL EntityStatMap: Mana 10 %% = 15 of the FLAT 150 with skyygear_mana 9.3 + "
         "skyypet_mana 15 on the stat (0.5.34 took 15.93), steady; + a Power's flat 2 = 17")
    m.putModifier(JInt(MI), "skyygear_mana", SMO(MTG.MAX, CAL.ADDITIVE, JFloat(30.0)))
    E.manaMod2(m, JInt(MI), "skyyacc_mana", JFloat(10.0), JFloat(0.0), JFloat(2.0))
    K.eq(amt(), 17.0, "PK ... unchanged when Gear's Mana % grows (the %% layers never feed each other)")
    hf.setFloat(ET.getAssetMap().getAsset(JInt(MI)), JFloat(0.0))
    HPI = int(DST.getHealth())
    m2 = ESM()
    m2.update()
    m2.putModifier(JInt(HPI), "acc535test", SMO(MTG.MAX, CAL.ADDITIVE, JFloat(150.0)))
    E.hpPct(m2, JInt(HPI), "skyyacc_health", JDouble(8.0), JLong(1000))
    K.check(abs(float(m2.getModifier(JInt(HPI), "skyyacc_health").getAmount()) - 12.0) < 0.02, "PK hpPct unchanged: +8 %% of 150 = 12")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyAccessories", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("static", run_static), ("pk", run_pk), ("live", T534.run_live)],
           script=__file__, live=(LIVE_DIR, "Skyy_SkyyAccessories"))
