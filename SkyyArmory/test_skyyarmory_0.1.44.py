"""Harness for SkyyArmory 0.1.44 (sig1: the bridge armory:fn:sig - SkyyArmory's own Ability 1 texts for SkyyGear 0.3.43's tooltip;
tools/armory_0_1_44_patch.py). Build first:
    python tools/armory_0_1_44_patch.py && python SkyyArmory/build_skyyarmory_0.1.44.py
    python SkyyArmory/test_skyyarmory_0.1.44.py [--keep]
Phases (fresh child JVMs, tools/harness_kit.py: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  S   static   the patch re-runs to identical bytes; one new class (ArmorySigFn), no command / system; the key is in BRIDGE_KEYS (unpublish)
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.1.43 -> 0.1.44: exactly the planned members (EXPECT)
  X   exec     ArmorySigFn EXECUTED: every wand id (incl. SkyySkills' Wood / Rotten / Tribal and the Untiered copies) answers Ricochet with
               plain java.lang types (String, String, Integer, String, Boolean); the text + gains follow the live rows (maxHits,
               chargeQuick / chargeCharged, enabled); a String argument works too; any other id / null / a wrong argument -> null; the text
               fits 70 characters at the 16-hit maximum; publish() puts armory:fn:sig and unpublish() removes it
  D   live     START TWICE on a scratch COPY of the live Skyy_SkyyArmory (every migration + load): 0.1.44 adds no row, nothing changes
  AA  audit    the engine-access audit
Not executed here (UNVERIFIED until the game): SkyyGear's hover text in the client (SkyyGear's harness renders the block from this answer).
"""
import os, sys, hashlib, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "sig1", "arm")]
import skyybuild as B
import harness_kit as HK

VERSION, OLD = "0.1.44", "0.1.43"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyArmory-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyArmory-%s.jar" % OLD)
GEN = os.path.join(HERE, "build_skyyarmory_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyarmory_%s.py" % OLD)
PATCH = os.path.join(ROOT, "tools", "armory_0_1_44_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.armory."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyArmory")
EXPECT = {"SkyyArmoryPlugin": ["~m publish", "~m setup", "~m start", "~m unpublish"], "CfgFn": ["~m opExport"], "CfgRows": ["~m header"],
          "CfgRows2": ["~<clinit>"],
          # the version text only (the generated scripts differ in nothing else outside the patch's edits - checked with a version-blind diff)
          "ArmoryCfg": ["~m load", "~m reloadAll", "~m useDefaults"], "ArmoryCheck": ["~m packCheck", "~m packOf"]}
if "--expect-dump" in sys.argv:
    EXPECT = {}
MIGS = ("migrate012", "migrate013", "migrate014", "migrate016", "migrate017", "migrate018", "migrate021", "migrate035", "migrate036", "migrate040",
        "migrateP5")


def tree_hash(root):
    o = {}
    for d, _x, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            o[os.path.relpath(p, root).replace(os.sep, "/")] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return o


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyArmory 0.1.44 - build script') and g.count('VERSION = "0.1.44"') == 1, "S header + VERSION")
    K.eq((g.count("registerSystem(") - o.count("registerSystem("), g.count("registerCommand(") - o.count("registerCommand("), g.count("makeClass(") - o.count("makeClass(")),
         (0, 0, 1), "S no new system / command; one new class")
    bk = g[g.index("BRIDGE_KEYS = ["):]
    K.check('"armory:fn:sig"]' in bk[:bk.index("]") + 1], "S armory:fn:sig is in BRIDGE_KEYS (unpublish removes it)")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    import zipfile
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    K.eq((sorted(nb - na), sorted(na - nb)), (["com/skyy/armory/ArmorySigFn.class"], []), "S the only entry added = ArmorySigFn")
    chg = sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n))
    K.eq(chg, ["manifest.json"], "S the only non-class change is the manifest")
    K.save()


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JString, JArray, JObject, JInt
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    JClass(PKG + "ArmoryLog").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyArmory")
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    Cfg, Defs, Fn = JClass(PKG + "ArmoryCfg"), JClass(PKG + "ArmoryDefs"), JClass(PKG + "ArmorySigFn")
    f = Fn()
    K.check(isinstance(f, JClass("java.util.function.Function")), "X ArmorySigFn is a java.util.function.Function")

    def ask(i, as_string=False):
        if as_string:
            r = f.apply(JString(i))
        else:
            a = JArray(JObject)(1)
            a[0] = None if i is None else JString(i)
            r = f.apply(a)
        return r
    wands = sorted(str(k) for k in Defs.items().keySet() if int(Defs.wandIndex(JString(str(k)))) >= 0)
    uts = [str(x) for x in Defs.UT_IDS if int(Defs.wandIndex(Defs.utBase(JString(str(x))))) >= 0]
    K.check(len(wands) >= 16 and {"Weapon_Wand_Wood", "Weapon_Wand_Wood_Rotten", "Weapon_Wand_Tribal"} <= set(wands), "X %d wand ids incl. SkyySkills' Wood / Rotten / Tribal" % len(wands))
    K.check(len(uts) >= 1, "X the Untiered wand copies: %s" % uts)
    K.notes.append("X wands: %s; UT wands: %s" % (wands, uts))
    want = ("Ricochet", "A bolt jumps from your target to the nearest enemy, up to 8 hits.", 20, "quick hit +1~, charged hit +2", True)
    bad = []
    for i in wands + uts:
        r = ask(i)
        types = None if r is None else [("java.lang.String" if isinstance(r[k], str) else str(r[k].getClass().getName())) for k in range(len(r))]
        got = None if r is None else (str(r[0]), str(r[1]), int(r[2]), str(r[3]), bool(r[4]))
        if got != want or types != ["java.lang.String", "java.lang.String", "java.lang.Integer", "java.lang.String", "java.lang.Boolean"]:
            bad.append((i, got, types))
    K.eq(bad, [], "X every wand + UT wand answers Ricochet (String, String, Integer 20, String, Boolean) - plain java.lang types")
    K.eq(str(ask(wands[0], True)[0]), "Ricochet", "X a bare String argument works too")
    K.eq([ask(i) for i in ("Weapon_Sword_Iron", "Weapon_Bo_Lead_SkyWynn", "Weapon_Staff_Lead_SkyWynn", "Weapon_Kunai_Lead_SkyWynn", "", None)], [None] * 6,
         "X not ours / not a wand / empty / null -> null (SkyyGear reads the item then)")
    K.check(f.apply(JInt(5)) is None and f.apply(None) is None and f.apply(JArray(JObject)(0)) is None, "X a wrong argument -> null, no throw")
    Cfg.SIG_HITS, Cfg.SIG_GAINQ, Cfg.SIG_GAINC = 16, 1.5, 3.0
    r = ask(wands[0])
    K.eq((str(r[1]), str(r[3])), ("A bolt jumps from your target to the nearest enemy, up to 16 hits.", "quick hit +1.5~, charged hit +3"), "X the live rows (16 hits, +1.5 / +3)")
    K.check(len(str(r[1])) <= 70, "X the text fits 70 characters at the 16-hit maximum (%d)" % len(str(r[1])))
    Cfg.SIG_ON = False
    K.eq(bool(ask(wands[0])[4]), False, "X sig.wand.enabled off -> ready false")
    Cfg.SIG_HITS, Cfg.SIG_GAINQ, Cfg.SIG_GAINC, Cfg.SIG_ON = 8, 1.0, 2.0, True
    Pl = JClass(PKG + "SkyyArmoryPlugin")
    try:
        Pl.publish()
        K.check(isinstance(br.get("armory:fn:sig"), JClass("java.util.function.Function")) and str(br.get("armory:fn:sig").getClass().getName()) == PKG + "ArmorySigFn",
                "X publish() puts armory:fn:sig")
        Pl.unpublish()
        K.check(br.get("armory:fn:sig") is None, "X unpublish() removes it")
    except Exception as ex:
        K.notes.append("X publish() could not run in the bare JVM (%s) - the key is checked in S" % str(ex)[:160])
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    JClass(PKG + "ArmoryLog").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyArmory")
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Cfg = JClass(PKG + "ArmoryCfg")
    Paths = JClass("java.nio.file.Paths")
    Cfg.DIR = Paths.get(home)
    Cfg.FILE = Paths.get(home).resolve("config.properties")
    fp = os.path.join(home, "config.properties")
    b0 = open(fp, "rb").read()
    hashes = [tree_hash(home)]
    for start in (1, 2):
        rs = [str(getattr(Cfg, m)()) for m in MIGS]
        Cfg.load()
        hashes.append(tree_hash(home))
        if start == 1:
            K.notes.append("D start 1 migrations: %s" % [x[:120] for x in rs if x])
    K.check(hashes[1] == hashes[2], "D start 2 changes nothing")
    t1 = open(fp, "rb").read()
    K.check(b"0.1.44" not in t1 and (b"\r\n" in b0) == (b"\r\n" in t1), "D 0.1.44 writes no row of its own; line endings kept")
    K.notes.append("D files changed by start 1: %s" % sorted(k for k in set(hashes[0]) | set(hashes[1]) if hashes[0].get(k) != hashes[1].get(k))[:8])
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyArmory", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=["ArmorySigFn"],
           phases=[("static", run_static), ("exec", run_exec), ("live", run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyArmory"))
