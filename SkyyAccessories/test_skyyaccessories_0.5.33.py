"""Harness for SkyyAccessories 0.5.33 (wc15: Accessory Plates x1.5 + the one-time trees.properties update - tools/accessories_0_5_33_patch.py,
tools/wc15.py). Build first:
    python tools/accessories_0_5_33_patch.py && python SkyyAccessories/build_skyyaccessories_0.5.33.py
    python SkyyAccessories/test_skyyaccessories_0.5.33.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  S     static   the patch re-runs to identical bytes; no new system / command / class; line endings kept; the non-class jar entries = 0.5.32's
                 except the manifest (no lang / item file changed)
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.5.32 -> 0.5.33 (EXPECT below)
  X     exec     EXECUTES in a bare JVM: AccV3's built-in numbers (Plates 0.75 % a rank, ceiling 11.25 %; every other row unchanged);
                 tools/wc15_harness.py exec_update + exec_migrate; THE APPLIER: AccPower.tick c[0] (the max Health % AccEffects applies) with
                 Plates from a fake tree:fn:level: rank 3 x 5 counting accessories = +11.25 % (was 7.5), rank 1 x 2 = +1.5 %, the cap at 5
                 accessories, rank 0 = nothing
  LIVE  start twice on a scratch COPY of Skyy's live NewBetaTest Skyy_SkyyAccessories (every update in setup's order + the loaders): start 1
                 moves only Plates lines on the 0.5.32 default (the live file has none - it still holds the pre-0.5.30 flat "hp" lines - so
                 only the marker is added, History copy first), start 2 changes nothing; AccV3 then reads Plates 0.75 / 11.25
  AA    engine-access audit
NOT COVERED (UNVERIFIED in game): AccEffects writing the Health modifier on the world thread (unchanged code; it reads AccPower.tick's c[0]),
the /tree page text (SkyyTrees' own text still says +2% max Health/rank - a SkyyTrees round).
Scratch: tools/dev/scratch/wc15/acc (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "wc15", "acc")]
import harness_kit as HK
import skyybuild as B
import trees_v3_effects as V3E
import wc15 as WC
import wc15_harness as WH

VERSION, OLD = "0.5.33", "0.5.32"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyAccessories-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyAccessories-%s.jar" % OLD)
GEN = os.path.join(HERE, "build_skyyaccessories_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyaccessories_%s.py" % OLD)
PATCH = os.path.join(ROOT, "tools", "accessories_0_5_33_patch.py")
PKG = "com.skyy.accessories."
SCRATCH = os.path.abspath(HK.arg("--dir"))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyAccessories")
EXPECT = {
    "AccCfg": ["+f WC_KEY", "+f WC_MARK", "+f WC_MARK_ID", "+f WC_NEW", "+f WC_NEWN", "+f WC_OLD", "+f WC_OLDT", "+f WC_WHO",
               "+m migrateWc15", "+m wcEq", "+m wcFile", "+m wcKit", "+m wcLog", "+m wcNum", "+m wcSame", "+m wcSaved", "+m wcUpdate",
               "~<clinit>"],          # + the version in its default config text
    "AccV3": ["~<clinit>", "~m loadV3"],
    "SkyyAccessoriesPlugin": ["~m setup"],
    "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],          # the version + the 2 Plates row defaults
}
if "--expect-dump" in sys.argv:
    EXPECT = {}


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyAccessories 0.5.33 - build script') and g.count('VERSION = "0.5.33"') == 1, "S header + VERSION")
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
    K.eq(sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n)), ["manifest.json"], "S the only non-class change is the manifest (no lang / item file)")
    K.save()


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JArray, JString, JObject, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    Pw, V3, Cfg = JClass(PKG + "AccPower"), JClass(PKG + "AccV3"), JClass(PKG + "AccCfg")
    Paths, UUID = JClass("java.nio.file.Paths"), JClass("java.util.UUID")
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    WC.apply(V3E, "SkyyAccessories")
    R = V3E.rows("SkyyAccessories")
    ip = [i for i, e in enumerate(R) if e[0] == "Combat"]
    K.eq(len(ip), 1, "X one Weaponcraft row (Accessory Plates)")
    for i, e in enumerate(R):
        K.check(abs(float(V3.v3per(i)) - e[5]) < 1e-12 and abs(float(V3.v3most(i)) - V3E.vmax(e)) < 1e-12 and abs(float(V3.PER[i]) - e[5]) < 1e-12,
                "X row %d %s %s: per %s most %s (%s)" % (i, e[0], e[2], float(V3.v3per(i)), float(V3.v3most(i)), "x1.5" if i in ip else "unchanged"))
    K.eq((float(V3.v3per(ip[0])), float(V3.v3most(ip[0]))), (0.0075, 0.1125), "X Plates 0.75 % a rank, ceiling 11.25 % (was 0.5 / 7.5)")
    WH.exec_update(K, Cfg, "SkyyAccessories", fresh_text=str(V3.V3_TEXT))
    WH.exec_migrate(K, Cfg, "SkyyAccessories", os.path.join(scratch, "mig", "Skyy_SkyyAccessories"))
    V3.loadV3(Paths.get(os.path.join(scratch, "fresh")))
    K.eq(float(V3.v3per(ip[0])), 0.0075, "X a fresh trees.properties reads back 0.75 %")
    # THE APPLIER: AccPower.tick c[0] (max Health %) with Plates ranks from a fake SkyyTrees
    home = os.path.join(scratch, "pow")
    os.makedirs(os.path.join(home, "power"), exist_ok=True)
    Pw.FILE = Paths.get(os.path.join(home, "power.properties"))
    Pw.DIR = Paths.get(os.path.join(home, "power"))
    Pw.load()
    S = lambda *ids: JArray(JString)([JString(i) for i in ids])
    RANK = {}

    @JImplements("java.util.function.Function")
    class Lv(object):
        @JOverride
        def apply(self, a):
            return JObject({"Combat": 30}.get(str(a[1]), 0), "java.lang.Integer")

    @JImplements("java.util.function.Function")
    class Tr(object):
        @JOverride
        def apply(self, a):
            return JObject(RANK.get(str(a[1]), 0), "java.lang.Integer")
    br.put("skill:fn:level", Lv())
    br.put("tree:fn:level", Tr())
    u = UUID.fromString("00000000-0000-0000-0000-00000000c533")
    Pw.pick(u, str(u), "Balance", 1000000, False)
    kp = V3E.key("Combat", 2, "r4a")
    six = S(*["Skyy_Talisman_%s_Common" % f for f in ("Vitality", "Speed", "Endurance", "Intelligence", "Regeneration", "Strength")])
    two = S("Skyy_Talisman_Vitality_Common", "Skyy_Talisman_Speed_Common")

    def c0(bag, rank):
        RANK[kp] = rank
        return float(Pw.tick(u, bag)[0])
    base6, base2 = c0(six, 0), c0(two, 0)
    K.eq(int(V3.count(six)), 6, "X six counting accessories")
    K.check(abs(c0(six, 3) - base6 - 11.25) < 1e-6, "X Plates rank 3 x 5 (of 6) accessories = +11.25 %% max Health on c[0] (was 7.5): %.2f -> %.2f" % (base6, c0(six, 3)))
    K.check(abs(c0(two, 1) - base2 - 1.5) < 1e-6, "X Plates rank 1 x 2 accessories = +1.5 %% (was 1.0)")
    K.check(abs(c0(two, 3) - base2 - 4.5) < 1e-6, "X Plates rank 3 x 2 accessories = +4.5 %% (was 3.0)")
    K.check(abs(float(V3.hp(u, six)) - 0.1125) < 1e-12, "X AccV3.hp = 0.1125 (the fraction AccPower adds as %)")
    K.eq(c0(six, 0), base6, "X rank 0 = nothing")
    br.remove("tree:fn:level")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Paths = JClass("java.nio.file.Paths")
    J = lambda n: JClass(PKG + n)
    fc, fp = os.path.join(home, "config.properties"), os.path.join(home, "power.properties")
    hd = os.path.join(home, "config-history")
    b0 = set(x for x in os.listdir(hd) if "trees.properties." in x) if os.path.isdir(hd) else set()
    tf = os.path.join(home, "trees.properties")
    tb = open(tf, "rb").read() if os.path.isfile(tf) else None
    others0 = dict((n, open(os.path.join(home, n), "rb").read()) for n in ("config.properties", "power.properties", "sounds.properties") if os.path.isfile(os.path.join(home, n)))
    starts = []

    def load():
        J("AccStore").DIR = Paths.get(os.path.join(home, "bags"))
        J("AccCfg").FILE = Paths.get(fc)
        o = "".join(str(getattr(J("AccCfg"), m)()) for m in ("migrate051", "migrate055", "migrate0518")) + str(J("AccCfg").migrateP5(J("AccCfg").FILE, False))
        J("AccCfg").load(True)
        J("AccPower").FILE = Paths.get(fp)
        J("AccPower").DIR = Paths.get(os.path.join(home, "power"))
        o += str(J("AccCfg").migrateP5(J("AccPower").FILE, True))
        J("AccPower").load()
        starts.append(o)
        K.check(str(J("AccV3").loadV3(Paths.get(home))).endswith("read"), "LIVE AccV3.loadV3 reads trees.properties")
    # wc15_harness.live_twice runs migrateWc15 BEFORE load(); setup() runs it after AccPower.load - both before AccV3.loadV3 (what matters)
    moved, pb, pa = WH.live_twice(K, J("AccCfg"), "SkyyAccessories", home, load)
    K.check(all(x == "" for x in starts), "LIVE the older one-time updates do nothing on the live copy (%r)" % [x[:60] for x in starts if x])
    others1 = dict((n, open(os.path.join(home, n), "rb").read()) for n in others0)
    K.eq(sorted(n for n in others0 if others0[n] != others1[n]), [], "LIVE no other settings file changed")
    if tb is not None:
        b1 = set(x for x in os.listdir(hd) if "trees.properties." in x)
        new = sorted(b1 - b0)
        K.check(len(new) == 1 and open(os.path.join(hd, new[0]), "rb").read() == tb, "LIVE History: the live trees.properties kept once, exact bytes (%s)" % new)
    WC.apply(V3E, "SkyyAccessories")
    ip = [i for i, e in enumerate(V3E.rows("SkyyAccessories")) if e[0] == "Combat"][0]
    k = V3E.ckey(V3E.rows("SkyyAccessories")[ip]) + ".per"
    want = float(pa[k]) / 100.0 if k in pa else 0.0075
    K.check(abs(float(J("AccV3").v3per(ip)) - want) < 1e-12, "LIVE AccV3 after load: Plates per %s (%s)" % (float(J("AccV3").v3per(ip)), "file line" if k in pa else "no line in the live file = the new built-in 0.75 %"))
    K.save()


HK.run(name="SkyyAccessories", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
       phases=[("static", run_static), ("exec", run_exec), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyAccessories"))
