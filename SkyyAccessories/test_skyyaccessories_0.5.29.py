"""Harness for SkyyAccessories 0.5.29 (tools/accessories_0_5_29_patch.py = Skill Trees 3 R3c: Accessory Compass (Speed) + Accessory Sprint
(Stamina), tools/trees_v3_effects.py). Build first:
    python tools/accessories_0_5_29_patch.py && python SkyyAccessories/build_skyyaccessories_0.5.29.py
    python SkyyAccessories/test_skyyaccessories_0.5.29.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.5.28 -> 0.5.29: no class added; only the listed members differ; no asset / lang change (manifest only)
  V3   0.5.28's V3 phase on this jar (Trinket Seams, Accessory Boughs, Plates, ceilings, trees.properties - the table now has 5 rows)
  R3C  EXECUTED with a fake SkyyTrees tree:fn:level:
       SPD  AccPower.tick (the real 1 s path): rank 0 = exactly 0.5.28's c[] (all 8 sums); Accessory Compass rank 2 x 3 counting accessories =
            c[7] +3.0 (Speed %), rank 3 x 5 (cap, of 8) = +7.5 = the ceiling, a lowered ceiling cuts it, a raised per-rank number stops at
            the ceiling, clamped to the max rank 3; with power.enabled off and no SkyySkills it still adds (no reader); never in the Fortune
            source; profile:busy = null (nothing written that second)
       STAM AccV3.sum(u, bag, "stam") = the number AccEffects.tick adds to the skyyacc_stamina modifier: rank 0 = 0, rank 2 x 3 = 1.2, rank 3
            x 5 = 3.0 (the ceiling), the Omni = 1; never in c[]; a throwing / non-number answer = 0
       READS tree:reads:SkyyAccessories = the 5 keys; trees.properties seeded with the new rows; an OLD (0.5.28) trees.properties without them
            keeps the built-in numbers for the new rows and is not rewritten
  0.5.22 POWER + LIVE (start twice on a scratch COPY of the live Skyy_SkyyAccessories folder) on this jar
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK
import skyybuild as B
import trees_v3_effects as V3E

# 0.5.28's harness as a library: its V3 phase with the table's row count (it pinned 3 caps)
_P28 = os.path.join(HERE, "test_skyyaccessories_0.5.28.py")
_T28 = open(_P28, encoding="utf-8").read()
assert _T28.count("[int(x) for x in V3.CAP] == [5, 5, 5]") == 1
_T28 = _T28.replace("[int(x) for x in V3.CAP] == [5, 5, 5]", "[int(x) for x in V3.CAP] == [5] * len(rows)")
_T28 = _T28[:_T28.rindex('if __name__ == "__main__":')]
T28 = {"__name__": "acc_h528", "__file__": _P28, "__builtins__": __builtins__}
exec(compile(_T28, _P28 + " (library, 0.5.29)", "exec"), T28)
T22 = T28["T22"]
import skyyonce_harness as OH
HK.run_compare = OH.compare_allowing(lambda n: False)          # no asset may change 0.5.28 -> 0.5.29 (manifest.json is always allowed)

VERSION = "0.5.29"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyAccessories-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyAccessories-0.5.28.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "st3r3c", "acc")))
PKG = T22.PKG



def run_r3c(out, jar, scratch, _home):
    from jpype import JClass, JArray, JString, JObject, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    Pw, V3 = JClass(PKG + "AccPower"), JClass(PKG + "AccV3")
    Paths, UUID = JClass("java.nio.file.Paths"), JClass("java.util.UUID")
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    home = os.path.join(scratch, "r3c")
    os.makedirs(os.path.join(home, "power"), exist_ok=True)
    Pw.FILE = Paths.get(os.path.join(home, "power.properties"))
    Pw.DIR = Paths.get(os.path.join(home, "power"))
    Pw.load()
    S = lambda *ids: JArray(JString)([JString(i) for i in ids])
    rows = V3E.rows("SkyyAccessories")
    iC = [i for i, e in enumerate(rows) if e[4] == "spd"][0]
    iS = [i for i, e in enumerate(rows) if e[4] == "stam"][0]
    K.check(len(rows) == 5 and [str(x) for x in V3.EFF] == [e[4] for e in rows] and int(V3.MAX[iC]) == 3 and int(V3.MAX[iS]) == 3
            and abs(float(getattr(V3, "V3P%d" % iC)) - 0.5) < 1e-9 and abs(float(getattr(V3, "V3X%d" % iC)) - 7.5) < 1e-9
            and abs(float(getattr(V3, "V3P%d" % iS)) - 0.2) < 1e-9 and abs(float(getattr(V3, "V3X%d" % iS)) - 3.0) < 1e-9,
            "TBL AccV3 = the 5 rows; Compass 0.5 %% a rank an accessory, at most 7.5; Sprint 0.2 Stamina, at most 3; max ranks 3")
    RANK = {}

    @JImplements("java.util.function.Function")
    class Lv(object):
        @JOverride
        def apply(self, a):
            return JObject(20, "java.lang.Integer")

    @JImplements("java.util.function.Function")
    class Tr(object):
        @JOverride
        def apply(self, a):
            v = RANK.get(str(a[1]), 0)
            if v == "boom":
                raise RuntimeError("boom")
            if isinstance(v, str):
                return JString(v)
            return JObject(v, "java.lang.Integer")
    br.put("skill:fn:level", Lv())
    br.put("tree:fn:level", Tr())
    u = UUID.fromString("00000000-0000-0000-0000-00000000a3c1")
    k = str(u)
    Pw.pick(u, k, "Balance", 1000000, False)          # a Power with its own Speed (Balance: spd 1)

    def src():
        m = br.get("skill:bonus:" + k)
        s = m.get("accessories") if m is not None else None
        return dict((str(a), float(b)) for a, b in dict(s).items()) if s is not None else {}
    bag = S("Skyy_Talisman_Vitality_Epic", "Skyy_Talisman_Vitality_Common", "Skyy_Talisman_Speed_Rare", "Skyy_Accessory_Workbench_T3",
            "Skyy_Accessory_Workbench_T1", "Skyy_Accessory_Alchemybench_T1")
    big = S(*["Skyy_Talisman_%s_Common" % f for f in ("Vitality", "Speed", "Lantern", "Strength", "Defense", "Crit", "MagicPower", "Feather")])
    K.eq(int(V3.count(bag)), 3, "CNT 3 counting accessories in the small bag")
    nb = int(V3.count(big))
    K.check(nb > 5, "CNT %d counting accessories in the big bag (above the cap 5)" % nb)
    kC, kS = V3E.key("Exploration", 2, "r3a"), V3E.key("Acrobatics", 2, "r3a")
    c0 = [float(x) for x in Pw.tick(u, bag)]
    s0 = src()
    K.check(abs(float(V3.sum(u, bag, "spd"))) < 1e-12 and abs(float(V3.sum(u, bag, "stam"))) < 1e-12, "R0 rank 0: both sums 0")
    # ---------------- SPD
    RANK[kC] = 2
    c1 = [float(x) for x in Pw.tick(u, bag)]
    K.check(abs(c1[7] - c0[7] - 3.0) < 1e-9 and all(abs(c1[j] - c0[j]) < 1e-9 for j in range(7)),
            "SPD Accessory Compass rank 2 x 3 = c[7] +3.0 %% Speed (%.2f -> %.2f), the other 7 sums unchanged" % (c0[7], c1[7]))
    K.check(src() == s0, "SPD never in the Fortune source: %s" % src())
    RANK[kC] = 3
    cb = [float(x) for x in Pw.tick(u, big)]
    RANK[kC] = 0
    cb0 = [float(x) for x in Pw.tick(u, big)]
    K.check(abs(cb[7] - cb0[7] - 7.5) < 1e-9, "SPD rank 3 x 5 (cap, of %d) = +7.5 = the ceiling - the top rank adds (%.2f vs %.2f)" % (nb, cb[7], cb0[7]))
    RANK[kC] = 99
    K.check(abs(float(Pw.tick(u, bag)[7]) - c0[7] - 4.5) < 1e-9, "SPD a rank of 99 is clamped to the max 3 (3 x 3 x 0.5 = 4.5)")
    RANK[kC] = 3
    setattr(V3, "V3X%d" % iC, 5.0)
    K.check(abs(float(Pw.tick(u, big)[7]) - cb0[7] - 5.0) < 1e-9, "SPD a Server Setup ceiling of 5 cuts it to +5")
    setattr(V3, "V3X%d" % iC, 7.5)
    setattr(V3, "V3P%d" % iC, 2.0)
    K.check(abs(float(Pw.tick(u, big)[7]) - cb0[7] - 7.5) < 1e-9, "SPD a per-rank 2 (the tree's own +30 %%) stops at the 7.5 ceiling")
    setattr(V3, "V3P%d" % iC, 0.0)
    K.check(abs(float(Pw.tick(u, big)[7]) - cb0[7]) < 1e-9, "SPD per rank 0 = the row gives nothing")
    setattr(V3, "V3P%d" % iC, 0.5)
    Pw.ON = False
    br.remove("skill:fn:level")
    co = Pw.tick(u, bag)
    K.check(co is not None and abs(float(co[7]) - 4.5) < 1e-9, "SPD power.enabled off + no SkyySkills: the tree row alone = 4.5 (no reader needed): %s" % (None if co is None else float(co[7])))
    Pw.ON = True
    br.put("skill:fn:level", Lv())
    br.put("profile:busy:" + k, JObject(True, "java.lang.Boolean"))
    K.check(Pw.tick(u, bag) is None, "SPD profile:busy: tick returns null (AccEffects writes no Speed that second)")
    br.remove("profile:busy:" + k)
    RANK[kC] = "boom"
    K.check(abs(float(Pw.tick(u, bag)[7]) - c0[7]) < 1e-9, "SPD a throwing answer = rank 0")
    RANK.clear()
    K.check([abs(float(x) - c0[j]) < 1e-9 for j, x in enumerate(Pw.tick(u, bag))] == [True] * 8, "SPD rank 0 again = exactly 0.5.28's 8 sums")
    # ---------------- STAM
    RANK[kS] = 2
    K.check(abs(float(V3.sum(u, bag, "stam")) - 1.2) < 1e-9, "STAM Accessory Sprint rank 2 x 3 = +1.2 max Stamina (%s)" % float(V3.sum(u, bag, "stam")))
    K.check([abs(float(x) - c0[j]) < 1e-9 for j, x in enumerate(Pw.tick(u, bag))] == [True] * 8 and src() == s0, "STAM never in c[] or the Fortune source")
    RANK[kS] = 3
    K.check(abs(float(V3.sum(u, big, "stam")) - 3.0) < 1e-9, "STAM rank 3 x 5 (cap) = +3 = the ceiling")
    K.check(abs(float(V3.sum(u, S("Skyy_Accessory_Omni"), "stam")) - 0.6) < 1e-9, "STAM the Omni alone counts 1 (3 x 1 x 0.2)")
    K.check(abs(float(V3.sum(u, S(), "stam"))) < 1e-12, "STAM an empty bag = 0")
    RANK[kS] = "x"
    K.check(abs(float(V3.sum(u, big, "stam"))) < 1e-12, "STAM a non-number answer = 0")
    RANK[kS] = 3
    RANK[kC] = 1
    K.check(abs(float(V3.sum(u, bag, "stam")) - 1.8) < 1e-9 and abs(float(V3.sum(u, bag, "spd")) - 1.5) < 1e-9 and abs(float(V3.sum(u, bag, "hp"))) < 1e-12,
            "STAM each effect sums only its own rows (stam 1.8, spd 1.5, hp 0 with Plates at rank 0)")
    K.check(abs(float(V3.sum(None, bag, "stam"))) < 1e-12 and abs(float(V3.sum(u, bag, None))) < 1e-12, "STAM null player / effect = 0")
    RANK.clear()
    # ---------------- READS + trees.properties
    V3.reads(True)
    K.check(str(br.get("tree:reads:SkyyAccessories")) == V3E.reads_csv("SkyyAccessories") and kC in str(V3.READS) and kS in str(V3.READS),
            "READS tree:reads:SkyyAccessories = the 5 keys: %s" % V3.READS)
    V3.reads(False)
    K.check(br.get("tree:reads:SkyyAccessories") is None, "READS ours is removed at shutdown")
    tf = os.path.join(home, "trees.properties")
    if os.path.exists(tf):
        os.remove(tf)
    V3.loadV3(Paths.get(home))
    t1 = open(tf, encoding="latin-1", newline="").read()
    K.check(t1 == V3E.cfg_text("SkyyAccessories") and "tree.Exploration.b2.r3a.spd.per=0.5" in t1 and "tree.Acrobatics.b2.r3a.stam.max=3" in t1,
            "LOAD a missing trees.properties is written with the 5 rows")
    old = "".join(l for l in t1.splitlines(True) if "Exploration" not in l and "Acrobatics" not in l).replace("Health / Stamina rows are in points", "Health rows are in Health points")
    old = old.replace("tree.Mining.b2.r4a.dd.max=15", "tree.Mining.b2.r4a.dd.max=12")
    open(tf, "w", encoding="latin-1", newline="").write(old)
    setattr(V3, "V3X%d" % iC, 1.0)
    setattr(V3, "V3P%d" % iS, 9.0)
    res = str(V3.loadV3(Paths.get(home)))
    K.check(res == "trees.properties read" and open(tf, encoding="latin-1", newline="").read() == old and abs(float(V3.V3X0) - 12.0) < 1e-9
            and abs(float(getattr(V3, "V3X%d" % iC)) - 7.5) < 1e-9 and abs(float(getattr(V3, "V3P%d" % iS)) - 0.2) < 1e-9,
            "LOAD an old 0.5.28 file (no R3c lines, a hand edit) is read, not rewritten; the new rows take the built-in numbers")
    V3.V3X0 = 15.0
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyAccessories", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH,
           expect={
               "AccPower": ["~m tick"], "AccEffects": ["~m tick"], "SkyyAccessoriesPlugin": ["~m setup"],          # setup: the version text
               "AccV3": sorted(["+m sum", "~<clinit>", "+f V3P3", "+f V3X3", "+f V3P4", "+f V3X4", "~m v3per", "~m v3most", "~m loadV3",
                                "~m reads"]),          # reads: the inlined READS constant (5 keys)
               "CfgFn": ["~m opExport"], "CfgRows": sorted(["~<clinit>", "~m header"]), "CfgFile": ["~<clinit>"],          # the kit: 4 new rows
           }, added=[],
           phases=[("v3", T28["run_v3"]), ("r3c", run_r3c), ("power", T22.run_power), ("live", T22.run_live)],
           script=__file__, live=(T22.LIVE_DIR, "Skyy_SkyyAccessories"))
