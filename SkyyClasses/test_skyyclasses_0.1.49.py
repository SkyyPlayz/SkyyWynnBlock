"""Harness for SkyyClasses 0.1.49 (the A1 alts = a late-game either / or, the SkyyClasses part: abil.altPower + the tree path owns the pick -
tools/classes_0_1_49_patch.py; pairs with SkyyTrees 0.6.3, whose harness runs the two jars together). Build first:
    python tools/classes_0_1_49_patch.py && python SkyyClasses/build_skyyclasses_0.1.49.py
    python SkyyClasses/test_skyyclasses_0.1.49.py [--keep] [--expect-dump]

Phases (fresh child JVMs, tools/harness_kit.py):
  S     static   the patch re-runs to identical bytes; no new system / command / class; line endings kept; the non-class jar entries = 0.1.48's
                 except the manifest
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.1.48 -> 0.1.49 (EXPECT below)
  X46 / W46 / W47 / X48  the older EXEC + WIRE phases on the 0.1.49 jar (unchanged behaviour: wc15's numbers, the 0.1.46 / 0.1.47 wiring)
  ALT   exec     EXECUTES: the config row abil.altPower (default 50, a fresh config.properties, a hand value read back), AbilDefs.altMult for
                 every ability (x1.5 for the 15 A1-alts, x1 for the rest; 0 = off), the cast context's main effect (AbilCtx.main) and its
                 echo, class:fn:migInfo's cls= (fix round 2), treeOwnsPick / altSwitch with a "v5" tree list (no swap, the path text) and without it (0.1.48's rule), the growth text
  LIVE  start twice on a scratch COPY of Skyy's live Skyy_SkyyClasses (0.1.48's live phase: every update in setup's order + load + UpSk + CfgPub)
  AA    engine-access audit
NOT COVERED (UNVERIFIED in game): how much stronger the x1.5 alts FEEL in a fight (the numbers are the same lever as the ability level).
Scratch: tools/dev/scratch/tree063/cls (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "tree063", "cls")]
import harness_kit as HK
import skyybuild as B

_s = importlib.util.spec_from_file_location("test_skyyclasses_0_1_48", os.path.join(HERE, "test_skyyclasses_0.1.48.py"))
T48 = importlib.util.module_from_spec(_s)
_argv = list(sys.argv)
_s.loader.exec_module(T48)
sys.argv[:] = _argv

VERSION, OLD = "0.1.49", "0.1.48"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyClasses-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyClasses-%s.jar" % OLD)
GEN = os.path.join(HERE, "build_skyyclasses_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyclasses_%s.py" % OLD)
PATCH = os.path.join(ROOT, "tools", "classes_0_1_49_patch.py")
PKG = "com.skyy.classes."
SCRATCH = os.path.abspath(HK.arg("--dir"))
EXPECT = {   # checked 2026-10-24 (the class compare 0.1.48 -> 0.1.49; every member a change of tools/classes_0_1_49_patch.py - the Cfg* / KitMigrate /
    # SkyyClassesPlugin / ClassCfg ones are the version strings + the new config row)
    'Abil': ['~m altSwitch', '~m ctxFor', '~m migInfo', '~m treeOwnsPick'],
    'AbilCfg': ['+f ALT_POW', '~<clinit>', '~m read'],
    'AbilCtx': ['~m echoOf'],
    'AbilDefs': ['+m altMult'],
    'AbilDoes': ['~m grow'],
    'AbilPage': ['~m handleDataEvent'],
    'CfgFile': ['~<clinit>'],
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'CfgRows1': ['~<clinit>'],
    'CfgRows2': ['~<clinit>'],
    'ClassCfg': ['~<clinit>'],
    'KitMigrate': ['~m runOnce'],
    'SkyyClassesPlugin': ['~m setup'],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
ALTS = ["Challenge", "GuardiansOath", "BloodFrenzy", "WarlordsBanner", "RiftCleave", "ShatteringArc", "HundredFists", "StillWater", "VanishingAct",
        "ArrowRain", "HuntersNet", "Starfall", "ArcaneBeam", "Sanctuary", "MartyrsGrace"]


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyClasses 0.1.49 - build script') and g.count('VERSION = "0.1.49"') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand(", "makeClass("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    K.eq((sorted(nb - na), sorted(na - nb)), ([], []), "S no jar entry added / removed")
    K.eq(sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n)), ["manifest.json"], "S the only non-class change is the manifest")
    K.save()


def run_alt(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    Sys, Paths, UUID = JClass("java.lang.System"), JClass("java.nio.file.Paths"), JClass("java.util.UUID")
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    Sys.getProperties().put("skyy.bridge", br)
    Cfg, AC, AD, A, AS, Doe = (JClass(PKG + n) for n in ("ClassCfg", "AbilCfg", "AbilDefs", "Abil", "AbilStore", "AbilDoes"))
    d0 = os.path.join(scratch, "alt")
    os.makedirs(os.path.join(d0, "abilities"), exist_ok=True)
    Cfg.FILE = Paths.get(os.path.join(d0, "config.properties"))
    Cfg.load()
    K.eq(float(AC.ALT_POW), 50.0, "ALT abil.altPower default 50 % (a fresh config.properties)")
    t = open(os.path.join(d0, "config.properties"), "rb").read().decode("latin-1") if os.path.isfile(os.path.join(d0, "config.properties")) else str(Cfg.DEFAULTS) if hasattr(Cfg, "DEFAULTS") else ""
    K.check("abil.altPower=50" in t or "abil.altPower=50.0" in t, "ALT the default file lists abil.altPower")
    ids = [str(x) for x in AD.IDS]
    tiers = [int(x) for x in AD.TIER]
    K.eq(sorted(ids[i] for i in range(len(ids)) if tiers[i] >= 3), sorted(ALTS), "ALT the 15 A1-alts are tiers 3 / 4")
    bad = [ids[i] for i in range(len(ids)) if abs(float(AD.altMult(i)) - (1.5 if tiers[i] >= 3 else 1.0)) > 1e-12]
    K.eq(bad, [], "ALT altMult: x1.5 for every A1-alt, x1 for every other ability")
    AC.ALT_POW = 0.0
    K.check(all(abs(float(AD.altMult(i)) - 1.0) < 1e-12 for i in range(len(ids))), "ALT abil.altPower 0 = no bonus")
    AC.ALT_POW = 120.0
    K.check(abs(float(AD.altMult(ids.index("Sanctuary"))) - 2.2) < 1e-12, "ALT abil.altPower 120 -> x2.2 (a live Server Setup value)")
    AC.ALT_POW = 50.0
    open(os.path.join(d0, "config.properties"), "ab").write(b"abil.altPower=75\n")
    Cfg.load()
    K.eq(float(AC.ALT_POW), 75.0, "ALT a hand value in config.properties is read (75)")
    AC.ALT_POW = 50.0
    # the cast context (no class, no tree): an alt's main = its base x1.5; an echo keeps it
    AS.DIR = Paths.get(os.path.join(d0, "abilities"))
    for nm in ("SacredHeal", "Sanctuary", "Meteor", "Starfall", "Enrage", "BloodFrenzy"):
        ai = ids.index(nm)
        c = A.ctxFor(None, None, ai, 0, "")
        r = float(c.main) / (float(c.base) * float(c.treeMain))
        K.check(abs(r - (1.5 if nm in ALTS else 1.0)) < 1e-9, "ALT AbilCtx.main of %s = x%g over its level / tree" % (nm, r))
        e = c.echoOf(0.25)
        K.check(abs(float(e.main) - float(c.base) * float(c.treeMain) * 0.25 * (1.5 if nm in ALTS else 1.0)) < 1e-9, "ALT the echo of %s keeps the factor" % nm)
    # the tree owns the pick with SkyyTrees 0.6.3's "v5"
    CSV = {"csv": "v3,v4,v5,fold,A1,A2,A4a"}

    @JImplements("java.util.function.Function")
    class Tr(object):
        @JOverride
        def apply(self, a):
            return CSV["csv"]
    br.put("tree:fn:abil", Tr())
    u = UUID.fromString("00000000-0000-0000-0000-000000000149")
    br.put("profile:class:" + str(u), "Priest")
    br.put("class:" + str(u), "Priest")
    ci = int(JClass(PKG + "ClassStore").classIndex(u))
    K.check(ci >= 0, "ALT a Priest (class index %d)" % ci)
    K.check(bool(A.treeOwnsPick(u)), "ALT v5: the tree owns the Ability 1 alt")
    r = str(A.altSwitch(u, "B", CSV["csv"]))
    K.check(r.startswith("-Your Ability 1 alt is the end of the path you took in your class tree (Sanctuary or Martyr's Grace) - there is no swap"), "ALT alt switch refused with v5: %s" % r)
    CSV["csv"] = "v3,v4,fold,A1,A2,A4a"
    AS.TREEC.clear()
    K.check(bool(A.treeOwnsPick(u)), "ALT 0.6.2's list with one alt: the tree owns it (0.1.48's rule)")
    r = str(A.altSwitch(u, "B", CSV["csv"]))
    K.check(r.startswith("-Both Ability 1 alts come with row 2"), "ALT without v5 the 0.1.48 text stays: %s" % r[:60])
    CSV["csv"] = "v3,v4,fold,A1,A2,A4a,A4b"
    AS.TREEC.clear()
    K.check(not bool(A.treeOwnsPick(u)), "ALT 0.6.2's list with both alts: the pick is free again (0.1.48's rule unchanged)")
    g1 = str(Doe.grow(ids.index("Sanctuary")))
    g0 = str(Doe.grow(ids.index("SacredHeal")))
    K.check("Ability 1 alt: +50 %" in g1 and "keeps the levels" in g1 and "Ability 1 alt" not in g0 and "keeps the levels" in g0, "ALT growth texts: %s | %s" % (g1[-110:], g0[-60:]))
    # fix round 2: class:fn:migInfo names the profile's class (cls=) - SkyyTrees 0.6.3's alt063 applies the one pick to that class tree only
    pd, ad = os.path.join(d0, "mi-players"), os.path.join(d0, "mi-abilities")
    os.makedirs(pd, exist_ok=True)
    os.makedirs(ad, exist_ok=True)
    CS = JClass(PKG + "ClassStore")
    CS.DIR, AS.DIR = Paths.get(pd), Paths.get(ad)
    k1, k2 = "00000000-0000-0000-0000-000000000149-p2", "00000000-0000-0000-0000-000000000149-p3"
    open(os.path.join(pd, k1 + ".properties"), "w").write("class=Priest\n")
    open(os.path.join(ad, k1 + ".properties"), "w").write("alt=B\n")
    m1, m2 = A.migInfo(k1), A.migInfo(k2)
    K.check(m1 is not None and str(m1).startswith("alt=B;") and ";cls=Priest" in str(m1), "ALT migInfo names the class the pick belongs to: %s" % m1)
    K.check(m2 is not None and str(m2).startswith("alt=A") and "cls=" not in str(m2), "ALT migInfo without a class file: no cls= (SkyyTrees falls back): %s" % m2)
    K.save()
    sys.stdout.flush()
    os._exit(0)


if __name__ == "__main__":
    HK.run(name="SkyyClasses", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("static", run_static), ("exec46", T48.run_exec46), ("wire46", T48.run_wire46), ("wire47", T48.run_wire47), ("exec48", T48.run_exec),
                   ("alt", run_alt), ("live", T48.run_live)],
           script=__file__, live=(T48.LIVE_DIR, "Skyy_SkyyClasses"))
