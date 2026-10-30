"""SkyySkills 0.4.69 - harness for THE GEAR MANA % KEY (tools/skills_0_4_69_patch.py; RbStat.skip - and so ClassStat.skip - learns SkyyGear
0.3.52's skyygear_mana). Build first:
    python tools/skills_0_4_69_patch.py && python SkyySkills/build_skyyskills_0.4.69.py
    python SkyySkills/test_skyyskills_0.4.69.py [--keep]
Phases (each a fresh child JVM: -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch; tools/harness_kit.py):
  S     static   the patch re-runs to identical bytes, 0.4.68's patch still regenerates 0.4.68 byte for byte, line endings kept, 0 classes /
                 systems / commands added, VERSION, ONE "skyygear_mana" in the script (RbStat.skip), ClassStat.skip still asks RbStat.skip; the
                 jar: no entry added / removed, the only changed non-class entry = manifest.json
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.4.68 -> 0.4.69: exactly RbStat.skip + the version texts (EXPECT)
  PK    EXECUTED (a stand-in stat store: SkyyAccessories 0.5.30's fake_stats): RbStat.skip / ClassStat.skip (skyygear_mana + every old key
                 skipped, a flat key not), RbStat.flatMax + RbStat.put on a REAL EntityStatMap: the rebirth Mana % = a % of the FLAT max,
                 steady with SkyyGear's skyygear_mana on the stat; ClassStat.flatMax on Health unchanged
  X     the 0.4.68 X phase re-run on the 0.4.69 jar (the crop falloff: unchanged)
  LIVE  0.4.68's start twice on a scratch COPY of the live Skyy_SkyySkills (no file changes)
  AA    engine-access audit
NOT COVERED (UNVERIFIED in game): the Mana bar with a rebirth Mana boost + Swift / Sage armor on (the sum is executed on a real EntityStatMap).
"""
import os, sys, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK

if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "aug2b", "sk")]
_cmp0 = HK.run_compare
_eq00 = HK.Child.eq


def _mod(path, name):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    a = list(sys.argv)
    s.loader.exec_module(m)
    sys.argv[:] = a
    return m


T68 = _mod(os.path.join(HERE, "test_skyyskills_0.4.68.py"), "test_skyyskills_0_4_68")
TA30 = _mod(os.path.join(ROOT, "SkyyAccessories", "test_skyyaccessories_0.5.30.py"), "test_skyyaccessories_0_5_30")
HK.run_compare = _cmp0
HK.Child.eq = _eq00
T67 = T68.T67
VERSION = "0.4.69"
PKG = "com.skyy.skills."
GEN = os.path.join(HERE, "build_skyyskills_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyskills_0.4.68.py")
PATCH = os.path.join(TOOLS, "skills_0_4_69_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySkills-0.4.68.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
LIVE_DIR = T68.LIVE_DIR
EXPECT = {   # RbStat.skip = THE change; the rest = the version / ready-line texts (the same set 0.4.68 changed for its version)
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'CurveP9Mig': ['~m run'],
    'ManaGuard': ['~m armReport2', '~m intReport', '~m packReport'],
    'RbStat': ['~m skip'],
    'SkillCfg': ['~m load'],
    'SkyySkillsPlugin': ['~m setup'],
}
OLD_KEYS = ["skyyskill_rebirthhp", "skyyskill_rebirthmana", "skyyskill_rebirthstamina", "skyyacc_mana", "skyyskill_classhp", "skyygear_hp", "skyypet_health", "skyypet_mana"]


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyySkills 0.4.69') and g.count('VERSION = "0.4.69"') == 1, "S header + VERSION")
    K.check(g.count("registerCommand(") == o.count("registerCommand(") and g.count("registerSystem(") == o.count("registerSystem(")
            and g.count("makeClass(") == o.count("makeClass("), "S no new command / system / class")
    K.eq(g.count('"skyygear_mana"'), 1, "S one skyygear_mana in the script (RbStat.skip)")
    K.check('return s.equals(KEY_HP) || s.startsWith("skyyacc_") || @PKG@.RbStat.skip(k);' in g, "S ClassStat.skip still asks RbStat.skip")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    for patch, ref in ((PATCH, GEN), (os.path.join(TOOLS, "skills_0_4_68_patch.py"), GEN_OLD)):
        cp = os.path.join(d, os.path.basename(ref))
        p = subprocess.run([sys.executable, patch, "--out", cp], capture_output=True, text=True)
        K.check(p.returncode == 0 and open(cp, "rb").read() == open(ref, "rb").read(), "S %s re-generates its script byte for byte: %s" % (os.path.basename(patch), p.stderr[-300:]))
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    zn, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    nn, on = set(zn.namelist()), set(zo.namelist())
    K.eq(sorted(nn ^ on), [], "S the jar adds / removes no entry")
    K.eq(sorted(n for n in nn & on if not n.endswith(".class") and zn.read(n) != zo.read(n)), ["manifest.json"], "S changed non-class entries = manifest.json")
    K.save()


def run_pk(out, jar, scratch, _home):
    from jpype import JClass, JInt, JFloat, JDouble, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST], verify=True)          # = T67._cls + javassist (fake_stats builds its stand-in store with it)
    L = T68.T48.loader_for(jar)
    J = lambda n: JClass(PKG + n, loader=L)
    J("SkillCfg").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    TA30.fake_stats(JClass)
    Rb, Cs = J("RbStat"), J("ClassStat")
    ESM = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap")
    DST = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes")
    ET = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType")
    SMO = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier")
    MTG = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier$ModifierTarget")
    CAL = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier$CalculationType")
    K.check(bool(Rb.skip(JString("skyygear_mana"))) and bool(Cs.skip(JString("skyygear_mana"))), "PK RbStat.skip + ClassStat.skip skip SkyyGear 0.3.52's skyygear_mana")
    K.check(all(bool(Rb.skip(JString(k))) for k in OLD_KEYS), "PK RbStat.skip still skips every older %% layer")
    K.check(not bool(Rb.skip(JString("skyyskill_classmana"))) and not bool(Rb.skip(JString("Armor"))), "PK a flat source (class Mana, Armor) is not skipped")
    MI, HI = int(DST.getMana()), int(DST.getHealth())
    hf = ET.class_.getDeclaredField("max")
    hf.setAccessible(True)
    hf.setFloat(ET.getAssetMap().getAsset(JInt(MI)), JFloat(100.0))
    hf.setFloat(ET.getAssetMap().getAsset(JInt(HI)), JFloat(100.0))
    try:
        m = ESM()
        m.update()
        m.putModifier(JInt(MI), "skyyskill_classmana", SMO(MTG.MAX, CAL.ADDITIVE, JFloat(50.0)))          # flat: 150
        m.putModifier(JInt(MI), "skyygear_mana", SMO(MTG.MAX, CAL.ADDITIVE, JFloat(9.3)))                  # SkyyGear's Swift / Sage Mana %
        m.putModifier(JInt(MI), "skyypet_mana", SMO(MTG.MAX, CAL.ADDITIVE, JFloat(15.0)))
        K.eq(round(float(Rb.flatMax(m.get(JInt(MI)), JInt(MI))), 3), 150.0, "PK RbStat.flatMax = type max 100 + class Mana 50 (Gear / pet Mana %% skipped; 0.4.68 gave 159.3)")
        km = str(Rb.KM)
        amt = lambda: (lambda c: None if c is None else round(float(c.getAmount()), 3))(m.getModifier(JInt(MI), km))
        seq = []
        for _ in range(3):
            Rb.put(m, JInt(MI), km, JDouble(10.0))
            seq.append(amt())
        m.putModifier(JInt(MI), "skyygear_mana", SMO(MTG.MAX, CAL.ADDITIVE, JFloat(30.0)))
        Rb.put(m, JInt(MI), km, JDouble(10.0))
        seq.append(amt())
        K.eq(seq, [15.0] * 4, "PK RbStat.put on a REAL EntityStatMap: rebirth Mana 10 %% = 15 of the FLAT 150, steady, unchanged when Gear's Mana %% grows")
        h = ESM()
        h.update()
        for k_, v_ in (("Armor", 50.0), ("skyygear_hp", 40.0), ("skyygear_mana", 20.0)):
            h.putModifier(JInt(HI), k_, SMO(MTG.MAX, CAL.ADDITIVE, JFloat(v_)))
        K.eq(round(float(Cs.flatMax(h.get(JInt(HI)), JInt(HI))), 3), 150.0, "PK ClassStat.flatMax (Health) = type max 100 + Armor 50 (Gear's %% layers skipped)")
    finally:
        hf.setFloat(ET.getAssetMap().getAsset(JInt(MI)), JFloat(0.0))
        hf.setFloat(ET.getAssetMap().getAsset(JInt(HI)), JFloat(0.0))
    K.save()


def run_live(out, jar, scratch, home):
    T68.run_live(out, jar, scratch, home)


if __name__ == "__main__":
    phases = [("static", run_static), ("pk", run_pk), ("x", T68.run_x), ("live", run_live)]
    HK.run(name="SkyySkills", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=phases, script=__file__, live=(LIVE_DIR, "Skyy_SkyySkills"))
