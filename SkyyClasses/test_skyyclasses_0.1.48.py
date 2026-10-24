"""Harness for SkyyClasses 0.1.48 (wc15: Iron Will / Thick Skin / Reprisal x1.5 + the one-time trees.properties update -
tools/classes_0_1_48_patch.py, tools/wc15.py). Build first:
    python tools/classes_0_1_48_patch.py && python SkyyClasses/build_skyyclasses_0.1.48.py
    python SkyyClasses/test_skyyclasses_0.1.48.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  S     static   the patch re-runs to identical bytes; no new system / command / class; line endings kept; the non-class jar entries = 0.1.47's
                 except the manifest
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.1.47 -> 0.1.48 (EXPECT below)
  X46 / W46 / W47  the 0.1.46 EXEC + WIRE phases and the 0.1.47 WIRE phase on the 0.1.48 jar (unchanged behaviour; the 0.1.47 EXEC phase is
                 not re-run: it asserts the old Reprisal 9 % - its UpSk part is re-done below with the new numbers)
  X     exec     EXECUTES: UpSk's built-in numbers (Iron Will 4.5 / 13.5, Thick Skin 3 / 12, Reprisal 4.5 / 13.5; every other row unchanged - the
                 HELD hit rows and Second Wind too); THE APPLIER UpSk.compute with a fake tree:fn:level: vals [4] drAll, [5] kbRes, [6] thorns per
                 rank and at the ceiling, [7] Second Wind still 5 a rank; tools/wc15_harness.py exec_update + exec_migrate on ClassCfg
  LIVE  start twice on a scratch COPY of Skyy's live NewBetaTest Skyy_SkyyClasses (every update in setup's order + ClassCfg.load +
                 UpSk.loadV3 + CfgPub): start 1 moves only lines on the 0.1.47 default (History copy first), start 2 changes nothing; UpSk
                 then reads the new numbers; nothing but trees.properties + its History copy + the change log is written
  AA    engine-access audit
NOT COVERED (UNVERIFIED in game): Iron Will / Thick Skin / Reprisal on a real hit in the ECS (UpFx code unchanged - only the numbers).
Scratch: tools/dev/scratch/wc15fix2/cls (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "wc15fix2", "cls")]
import harness_kit as HK
import skyybuild as B
import trees_v3_effects as V3E
import wc15 as WC
import wc15_harness as WH

_s = importlib.util.spec_from_file_location("test_skyyclasses_0_1_47", os.path.join(HERE, "test_skyyclasses_0.1.47.py"))
T47 = importlib.util.module_from_spec(_s)
_argv = list(sys.argv)
_s.loader.exec_module(T47)
sys.argv[:] = _argv

VERSION, OLD = "0.1.48", "0.1.47"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyClasses-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyClasses-%s.jar" % OLD)
GEN = os.path.join(HERE, "build_skyyclasses_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyclasses_%s.py" % OLD)
PATCH = os.path.join(ROOT, "tools", "classes_0_1_48_patch.py")
PKG = "com.skyy.classes."
SCRATCH = os.path.abspath(HK.arg("--dir"))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyClasses")
EXPECT = {
    "ClassCfg": ["+f WC_KEY", "+f WC_MARK", "+f WC_MARK_ID", "+f WC_NEW", "+f WC_NEWN", "+f WC_OLD", "+f WC_OLDT", "+f WC_WHO",
                 "+m migrateWc15", "+m wcEq", "+m wcFile", "+m wcKit", "+m wcLog", "+m wcNum", "+m wcSame", "+m wcSaved", "+m wcUpdate",
                 "~<clinit>"],        # + the version in its default config text
    "KitMigrate": ["~m runOnce"],     # the version text
    "UpSk": ["~<clinit>", "~m loadV3"],
    "SkyyClassesPlugin": ["~m setup"],
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "CfgRows2": ["~<clinit>"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
ROWS = dict((V3E.key(r[0], r[1], r[2]), r) for r in WC.ROWS["SkyyClasses"])


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyClasses 0.1.48 - build script') and g.count('VERSION = "0.1.48"') == 1, "S header + VERSION")
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


def run_exec46(out, jar, scratch, home):
    T47.run_exec46(out, jar, scratch, home)


def run_wire46(out, jar, scratch, home):
    T47.run_wire46(out, jar, scratch, home)


def run_wire47(out, jar, scratch, home):
    T47.run_wire(out, jar, scratch, home)


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JObject, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    S, Cfg = JClass(PKG + "UpSk"), JClass(PKG + "ClassCfg")
    Paths, UUID, Sys = JClass("java.nio.file.Paths"), JClass("java.util.UUID"), JClass("java.lang.System")
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    Sys.getProperties().put("skyy.bridge", br)
    WC.apply(V3E, "SkyyClasses")
    R = V3E.rows("SkyyClasses")
    keys = [str(x) for x in S.KEY]
    K.eq(keys, [V3E.key(e[0], e[1], e[2]) for e in R], "X UpSk.KEY = the table's SkyyClasses rows (%d)" % len(R))
    old = dict((V3E.key(e[0], e[1], e[2]), e[5]) for e in R)
    for i, e in enumerate(R):
        k = keys[i]
        want = ROWS[k][5] if k in ROWS else e[5]
        K.check(abs(float(S.v3per(i)) - want) < 1e-12 and abs(float(S.v3most(i)) - V3E.vmax(e)) < 1e-12,
                "X row %s: per %s most %s (%s)" % (k, float(S.v3per(i)), float(S.v3most(i)), "x1.5" if k in ROWS else "unchanged"))
    held = [V3E.key(r[0], r[1], r[2]) for r in WC.HELD["SkyyClasses"]]
    K.eq([float(S.v3per(keys.index(k))) for k in held], [r[4] for r in WC.HELD["SkyyClasses"]], "X the HELD rows (hit rows, Second Wind) keep their 0.1.47 numbers")
    # THE APPLIER: UpSk.compute (vals [4] drAll, [5] kbRes, [6] thorns, [7] lowHeal) with ranks from a fake SkyyTrees
    RK = {}

    @JImplements("java.util.function.Function")
    class Tr(object):
        @JOverride
        def apply(self, a):
            return JObject(RK.get(str(a[1]), 0), "java.lang.Integer")
    br.put("tree:fn:level", Tr())
    u = UUID.fromString("00000000-0000-0000-0000-000000000148")
    kIW, kTS, kRP, kSW = "Skill.Combat.b2.r1b", "Skill.Combat.b2.r3a", "Skill.Combat.b2.r3b", "Skill.Combat.b2.r3c"

    def vals():
        S.C.clear()
        return [round(float(x), 6) for x in S.compute(u, Sys.currentTimeMillis())]
    v0 = vals()
    K.eq(v0[1:], [0.0] * 7, "X no ranks = nothing")
    RK.update({kIW: 1, kTS: 1, kRP: 1, kSW: 1})
    v = vals()
    K.eq([v[4], v[5], v[6], v[7]], [3.0, 4.5, 4.5, 5.0], "X rank 1: Thick Skin 3 % (was 2), Iron Will 4.5 % (was 3), Reprisal 4.5 % (was 3), Second Wind 5 % (held)")
    RK.update({kIW: 3, kTS: 4, kRP: 3, kSW: 3})
    v = vals()
    K.eq([v[4], v[5], v[6], v[7]], [12.0, 13.5, 13.5, 15.0], "X top ranks: Thick Skin 12 (was 8), Iron Will 13.5 (was 9), Reprisal 13.5 (was 9), Second Wind 15 (held)")
    RK.update({kIW: 50, kTS: 50, kRP: 50, kSW: 50})
    v = vals()
    K.eq([v[4], v[5], v[6], v[7]], [12.0, 13.5, 13.5, 15.0], "X ranks above the max: each row stops at its ceiling")
    K.check(abs(float(S.cut(u)) - 0.0) < 1e-12, "X UpSk.cut is 0 while UpSk.ON is off")
    S.ON = True
    S.C.clear()
    K.eq(round(float(S.cut(u)), 6), 12.0, "X UpSk.cut (Thick Skin, what UpFx subtracts inside drCap) = 12 %")
    S.ON = False
    br.remove("tree:fn:level")
    WH.exec_update(K, Cfg, "SkyyClasses", fresh_text=str(S.V3_TEXT))
    WH.exec_migrate(K, Cfg, "SkyyClasses", os.path.join(scratch, "mig", "Skyy_SkyyClasses"))
    fr = os.path.join(scratch, "fresh")
    os.makedirs(fr, exist_ok=True)
    S.loadV3(Paths.get(fr))
    ft = open(os.path.join(fr, "trees.properties"), "rb").read().decode("latin-1") if os.path.isfile(os.path.join(fr, "trees.properties")) else ""
    K.check(ft.count(WC.MARK_ID) == 1 and abs(float(S.v3per(keys.index(kTS))) - 3.0) < 1e-12, "X a fresh trees.properties is seeded with the marker and reads back Thick Skin 3")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Paths = JClass("java.nio.file.Paths")
    Cfg, Pub, AS, S = JClass(PKG + "ClassCfg"), JClass(PKG + "CfgPub"), JClass(PKG + "AbilStore"), JClass(PKG + "UpSk")
    h0 = WH._hash(home)
    starts = []

    def load():
        Cfg.FILE = Paths.get(os.path.join(home, "config.properties"))
        o = "".join(str(x) for x in (Cfg.migrate0110(), Cfg.migrate0129(), Cfg.migrate0132(), Cfg.migrate0141(), Cfg.migrateP4()))
        Cfg.load()
        starts.append(o)
        K.check("read" in str(S.loadV3(Paths.get(home))), "LIVE UpSk.loadV3 reads trees.properties")
    # wc15_harness.live_twice runs migrateWc15 BEFORE load(); setup() runs it after migrateP4 - both before ClassCfg.load / UpSk.loadV3
    moved, pb, pa = WH.live_twice(K, Cfg, "SkyyClasses", home, load)
    K.check(all(x == "" for x in starts), "LIVE the older one-time updates do nothing on the live copy (%r)" % [x[:60] for x in starts if x])
    AS.DIR = Paths.get(os.path.join(home, "abilities"))
    Pub.start(Paths.get(os.path.dirname(home)), None)
    Pub.flush()
    Pub.shutdown()
    h1 = WH._hash(home)
    ch = sorted(k for k in set(h0) | set(h1) if h0.get(k) != h1.get(k))
    allowed = [k for k in ch if k == "trees.properties" or k == "config-changes.log" or k.replace(os.sep, "/").startswith("config-history/")]
    K.eq(ch, allowed, "LIVE only trees.properties, its History copy and the change log were written (%s)" % ch)
    keys = [str(x) for x in S.KEY]
    for k, r in ROWS.items():
        e = [x for x in V3E.rows("SkyyClasses") if V3E.key(x[0], x[1], x[2]) == k][0]
        ck = V3E.ckey(e) + ".per"
        want = float(pa[ck]) if ck in pa else r[5]
        K.check(abs(float(S.v3per(keys.index(k))) - want) < 1e-9, "LIVE UpSk after load: %s per %s (%s)" % (k, float(S.v3per(keys.index(k))), "file line" if ck in pa else "no line = the new built-in number"))
    K.notes.append("DLIVE moved lines: %s" % moved)
    K.save()
    sys.stdout.flush()
    os._exit(0)


if __name__ == "__main__":
    HK.run(name="SkyyClasses", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("static", run_static), ("exec46", run_exec46), ("wire46", run_wire46), ("wire47", run_wire47), ("exec", run_exec), ("live", run_live)],
           script=__file__, live=(LIVE_DIR, "Skyy_SkyyClasses"))
