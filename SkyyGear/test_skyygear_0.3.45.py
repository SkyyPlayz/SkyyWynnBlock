"""Harness for SkyyGear 0.3.45 (wc15: the five Weaponcraft rows x1.5 + the one-time trees.properties update - tools/gear_0_3_45_patch.py,
tools/wc15.py).
Build first:
    python tools/gear_0_3_45_patch.py && python SkyyGear/build_skyygear_0.3.45.py
    python SkyyGear/test_skyygear_0.3.45.py [--keep]

Phases (fresh child processes / JVMs, tools/harness_kit.py):
  S  static   the patch re-runs to identical bytes, line endings kept, no new class / command / system; the non-class jar entries = 0.3.44's
              except the manifest
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.3.44 -> 0.3.45 (EXPECT below)
  X  exec     EXECUTES in a bare JVM: the built-in numbers (GearCfg.V3P / V3X -> v3per / v3most) of the 5 Weaponcraft rows = x1.5, every
              other SkyyGear row unchanged; tools/wc15_harness.py exec_update (wcUpdate / wcSame on hand-made texts, the fresh V3_TEXT) +
              exec_migrate (migrateWc15 on a scratch folder: History copy first, change log, second run nothing, blocked History = untouched);
              loadV3 reads the migrated file (a custom value kept); THE APPLIER: GearV3.combat0 with ranks from a fake tree:fn:level and 4
              worn combat pieces (Hone Edge 5 + Gear Resonance 3 = +51 % damage, Weak Spot 3 = +9 % crit, Crit Mastery 3 = +14 % crit damage
              (13.5 rounded)), weaponInto with an Onyxium sword (Weapon Tempering 4 x 5 steps = +30 %), rank 0 = nothing
  D  live     start twice on a scratch COPY of Skyy's live NewBetaTest Skyy_SkyyGear: start 1 moves only the trees.properties lines on the
              0.3.44 Weaponcraft defaults (+ marker, History copy, change log), start 2 changes nothing; GearCfg.load reads the new numbers
  AA engine-access audit
NOT COVERED (UNVERIFIED in game): the real hit (GearStats.extra adds combat() into the player's stats on the world thread - unchanged code),
the /tree page text (SkyyTrees' own text still says the old numbers - a SkyyTrees round), Server Setup showing the new defaults (kit rows
generated from the same numbers; the kit itself unchanged).
Scratch: tools/dev/scratch/wc15/gear (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.3.45"
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "wc15", "gear")]
import skyybuild as B
import harness_kit as HK
import trees_v3_effects as V3E
import wc15 as WC
import wc15_harness as WH

GEN = os.path.join(HERE, "build_skyygear_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyygear_0.3.44.py")
PATCH = os.path.join(ROOT, "tools", "gear_0_3_45_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyGear-0.3.44.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.gear."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyGear")
ADDED = []
EXPECT = {
    "GearCfg": ["+f WC_KEY", "+f WC_MARK", "+f WC_MARK_ID", "+f WC_NEW", "+f WC_NEWN", "+f WC_OLD", "+f WC_OLDT", "+f WC_WHO",
                "+m migrateWc15", "+m wcEq", "+m wcFile", "+m wcKit", "+m wcLog", "+m wcNum", "+m wcSame", "+m wcSaved", "+m wcUpdate",
                "~<clinit>", "~m defaultsText", "~m loadV3"],
    "GearV3": ["~<clinit>"],
    "SkyyGearPlugin": ["~m setup"],
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "CfgRows2": ["~<clinit>"],          # the version + the 10 row defaults (holder 2)
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
U = "00000000-0000-0000-0000-000000000345"


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyGear 0.3.45 - build script') and g.count('VERSION = "0.3.45"') == 1, "S header + VERSION")
    K.eq((g.count("registerSystem(") - o.count("registerSystem("), g.count("registerCommand(") - o.count("registerCommand("), g.count('mk("') - o.count('mk("')),
         (0, 0, 0), "S no new system / command / class")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    K.eq((sorted(nb - na), sorted(na - nb)), ([], []), "S no jar entry added / removed")
    chg = sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n))
    K.eq(chg, ["manifest.json"], "S the only non-class change is the manifest")
    K.save()


def _idx():
    WC.apply(V3E, "SkyyGear")
    R = V3E.rows("SkyyGear")
    wk = set(r[:4] for r in WC.ROWS["SkyyGear"])
    return R, [i for i, e in enumerate(R) if (e[0], e[1], e[2], e[4]) in wk]


def run_exec(out, jar, scratch, home):
    import jpype
    from jpype import JClass, JString, JImplements, JOverride, JInt
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR, B.JAVASSIST], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    C, V, Defs = JClass(PKG + "GearCfg"), JClass(PKG + "GearV3"), JClass(PKG + "GearDefs")
    R, wi = _idx()
    K.eq(len(wi), 5, "X the 5 Weaponcraft rows are SkyyGear rows")
    old = dict((r[:4], r[4]) for r in WC.ROWS["SkyyGear"])
    for i, e in enumerate(R):
        u = V3E.unit(e[4])
        want = e[5]
        K.check(abs(float(C.v3per(i)) - want) < 1e-9 and abs(float(C.v3most(i)) - V3E.vmax(e)) < 1e-9,
                "X row %d %s %s: built-in per %s / most %s (%s)" % (i, e[0], e[2], float(C.v3per(i)) * u, float(C.v3most(i)) * u, "x1.5" if i in wi else "unchanged"))
        if i in wi:
            K.check(abs(want - 1.5 * old[(e[0], e[1], e[2], e[4])]) < 1e-12 and abs(float(V.PER[i]) - want) < 1e-12, "X ... = 1.5 x the 0.3.44 number")
    WH.exec_update(K, C, "SkyyGear")
    d = os.path.join(scratch, "mig", "Skyy_SkyyGear")
    WH.exec_migrate(K, C, "SkyyGear", d)
    # loadV3 reads the migrated file: the custom Hone Edge per (41) kept, the rest new
    st = str(C.loadV3(JClass("java.nio.file.Paths").get(d)))
    K.check(st.endswith("read") and abs(float(C.v3per(wi[0])) - 41.0) < 1e-9 and all(abs(float(C.v3per(i)) - R[i][5]) < 1e-9 for i in wi[1:]), "X loadV3 on the migrated file: %s" % st)
    # THE APPLIER: GearV3.combat0 / weaponInto with ranks from a fake SkyyTrees
    C.loadV3(JClass("java.nio.file.Paths").get(os.path.join(scratch, "fresh")))          # a fresh file = the built-in numbers again
    ranks = {}

    @JImplements("java.util.function.Function")
    class Lv(object):
        @JOverride
        def apply(self, a):
            return JInt(ranks.get(str(a[1]), 0))
    br.put("tree:fn:level", Lv())
    uu = JClass("java.util.UUID").fromString(U)
    V.PCS.put(uu, jpype.JArray(jpype.JInt)([0, 0, 0, 4]))
    sd, sc, scd = int(Defs.sIndex("dmg")), int(Defs.sIndex("cc")), int(Defs.sIndex("cd"))

    def combat():
        V.RK.clear()
        V.CMB.clear()
        t = V.combat0(uu)
        return None if t is None else (int(t[sd]), int(t[sc]), int(t[scd]))
    K.eq(combat(), None, "X no ranks = no combat stats")
    ranks.update({"Skill.Combat.b1.r1a": 5, "Skill.Combat.b1.r4b": 3, "Skill.Combat.b1.r1b": 3, "Skill.Combat.b1.r4a": 3})
    K.eq(combat(), (51, 9, 14), "X Hone Edge 5 + Gear Resonance 3 x 4 pieces = +51 % damage (was 34), Weak Spot 3 = +9 % crit (was 6), Crit Mastery 3 = +14 % crit damage (13.5 rounded; was 9)")
    ranks.update({"Skill.Combat.b1.r1a": 1, "Skill.Combat.b1.r4b": 1, "Skill.Combat.b1.r1b": 1, "Skill.Combat.b1.r4a": 1})
    V.PCS.put(uu, jpype.JArray(jpype.JInt)([0, 0, 0, 2]))
    K.eq(combat(), (9, 3, 5), "X rank 1 each, 2 pieces: 3 + 3 x 2 = +9 % damage, +3 % crit, +5 % crit damage (4.5 rounded)")
    V.PCS.put(uu, jpype.JArray(jpype.JInt)([0, 0, 0, 6]))
    ranks.update({"Skill.Combat.b1.r4b": 3})
    K.eq(combat()[0], 3 + 36, "X Gear Resonance caps at 4 pieces (36)")
    # weaponInto: Weapon Tempering x weapon steps over Iron (an Onyxium sword = 5)
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    Unsafe = JClass("sun.misc.Unsafe")
    fu = Unsafe.class_.getDeclaredField("theUnsafe")
    fu.setAccessible(True)
    un = fu.get(None)
    fl = dict((str(f.getName()), f) for f in IS.class_.getDeclaredFields())

    def stack(iid):
        s_ = un.allocateInstance(IS.class_)
        for n_, v_ in (("itemId", JString(iid)), ("quantity", JInt(1)), ("metadata", JClass("org.bson.BsonDocument")())):
            fl[n_].setAccessible(True)
            fl[n_].set(s_, v_)
        return s_

    def wpn(iid):
        V.RK.clear()
        t = jpype.JArray(jpype.JInt)([0] * int(Defs.NS))
        n = int(V.weaponInto(uu, stack(iid), t))
        return n, int(t[sd])
    K.eq([int(V.wsteps("Weapon_Sword_Onyxium")), int(V.wsteps("Weapon_Sword_Iron")), int(V.wsteps("Weapon_Sword_Thorium"))], [5, 0, 1], "X weapon steps over Iron")
    K.eq(wpn("Weapon_Sword_Onyxium"), (0, 0), "X Weapon Tempering rank 0 = nothing")
    ranks["Skill.Combat.b1.r5b"] = 4
    K.eq(wpn("Weapon_Sword_Onyxium"), (1, 30), "X Weapon Tempering 4 x Onyxium (5 steps) = +30 % damage (was 20)")
    K.eq(wpn("Weapon_Sword_Thorium"), (1, 6), "X ... x Thorium (1 step) = +6 % (was 4)")
    ranks["Skill.Combat.b1.r5b"] = 1
    K.eq(wpn("Weapon_Sword_Thorium"), (1, 2), "X ... rank 1 x 1 step = 1.5 -> +2 % (rounded; was 1)")
    K.eq(wpn("Weapon_Sword_Iron"), (0, 0), "X ... an Iron sword (0 steps) = nothing")
    br.remove("tree:fn:level")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR, B.JAVASSIST], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Cfg = JClass(PKG + "GearCfg")
    fc = os.path.join(home, "config.properties")
    Cfg.FILE = JClass("java.nio.file.Paths").get(fc)
    MIG = ["migrate0330", "migrateP4", "migrateP5", "migrateP6", "migrateP7", "migrate39"]
    hd = os.path.join(home, "config-history")
    b0 = set(x for x in os.listdir(hd) if "trees.properties." in x) if os.path.isdir(hd) else set()
    tb = open(os.path.join(home, "trees.properties"), "rb").read() if os.path.isfile(os.path.join(home, "trees.properties")) else None

    def load():
        m = "".join(str(getattr(Cfg, x)()) for x in MIG)
        K.check(m == "", "D the older one-time updates do nothing on the live copy (%r)" % m[:80])
        Cfg.load()
    moved, pb, pa = WH.live_twice(K, Cfg, "SkyyGear", home, load)
    R, wi = _idx()
    if tb is not None:
        b1 = set(x for x in os.listdir(hd) if "trees.properties." in x)
        new = sorted(b1 - b0)
        K.check(len(new) == 1 and open(os.path.join(hd, new[0]), "rb").read() == tb, "D History: the live trees.properties kept once, exact bytes (%s)" % new)
        lg = open(os.path.join(home, "config-changes.log"), encoding="utf8").read().splitlines()
        K.eq(sum(1 for l in lg if "\tSkyyGear 0.3.45 update (wc15)\t" in l), len(moved), "D change log: one Undo line per moved live line")
    for i in wi:
        e = R[i]
        k = V3E.ckey(e) + ".per"
        want = float(pa[k]) / V3E.unit(e[4]) if k in pa else e[5]
        K.check(abs(float(Cfg.v3per(i)) - want) < 1e-9, "D GearCfg after load: %s per %s" % (k, float(Cfg.v3per(i)) * V3E.unit(e[4])))
    K.notes.append("D live Weaponcraft per lines after start 1: %s" % dict((V3E.ckey(R[i]) + ".per", pa.get(V3E.ckey(R[i]) + ".per")) for i in wi))
    K.save()


HK.run("SkyyGear", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("static", run_static), ("exec", run_exec), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyGear"))
