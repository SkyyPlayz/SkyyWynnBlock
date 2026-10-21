"""Harness for SkyyAccessories 0.5.28 (tools/accessories_0_5_28_patch.py = Skill Trees 3 R3b: the accessory rows of the skill trees,
tools/trees_v3_effects.py). Build first:
    python tools/accessories_0_5_28_patch.py && python SkyyAccessories/build_skyyaccessories_0.5.28.py
    python SkyyAccessories/test_skyyaccessories_0.5.28.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.5.27 -> 0.5.28: AccV3 added; only the listed members differ; no asset / lang change (manifest only)
  V3   EXECUTED on AccPower.tick (the real 1 s path) with a fake SkyyTrees tree:fn:level: rank 0 = exactly 0.5.27's source; Trinket Seams
       rank 2 with 3 counting accessories = dd.mining + 0.06 (fixer 2: 1 a rank an accessory) added to the Mining Power's own dd.mining; the count = one per line group (a
       lower copy / duplicate / retired item / bench next to the Omni add 0, the Omni 1), capped at 5; clamped to the max; Accessory Boughs on
       its own (dd.foraging) with no Power stat; no SkyySkills (no Fortune reader) = nothing; profile:busy = the source goes (0.5.22 rule);
       a bad / throwing answer = 0; tree:reads:SkyyAccessories published / only our own value removed;
       PLATES (fixer 2) Combat Accessory Plates: rank 0 = the 0.5.27 Health sum, rank 2 x 3 = +12 max Health in tick's c[0], rank 3 x 5 (cap)
       = +30, a lowered ceiling cuts it, works with the Power off and without SkyySkills, never in the Fortune source
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

_sp = importlib.util.spec_from_file_location("acc_h527", os.path.join(HERE, "test_skyyaccessories_0.5.27.py"))
T27 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T27)
T22 = T27.T22
import skyyonce_harness as OH
HK.run_compare = OH.compare_allowing(lambda n: False)          # no asset may change 0.5.27 -> 0.5.28 (manifest.json is always allowed)

VERSION = "0.5.28"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyAccessories-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyAccessories-0.5.27.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "st3r3b", "acc")))
PKG = T22.PKG
EXPECT = {
    "AccPower": ["~m tick"],
    "CfgFn": ["~m opExport"], "SkyyAccessoriesPlugin": ["~m setup", "~m shutdown"],
    "CfgRows": sorted(["~m header", "+f DL3", "~<clinit>", "~m defLines"]), "CfgFile": sorted(["~<clinit>", "~m init"]),          # fixer: the kit's 4 new rows + trees.properties
    "AccCfg": ["~m reload"],          # fixer: + trees.properties on every reload
}
OMNI = "Skyy_Accessory_Omni"


def run_v3(out, jar, scratch, _home):
    from jpype import JClass, JArray, JString, JObject, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    Pw, V3 = JClass(PKG + "AccPower"), JClass(PKG + "AccV3")
    Paths, UUID = JClass("java.nio.file.Paths"), JClass("java.util.UUID")
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    home = os.path.join(scratch, "v3")
    os.makedirs(os.path.join(home, "power"), exist_ok=True)
    Pw.FILE = Paths.get(os.path.join(home, "power.properties"))
    Pw.DIR = Paths.get(os.path.join(home, "power"))
    Pw.load()
    S = lambda *ids: JArray(JString)([JString(i) for i in ids])
    rows = V3E.rows("SkyyAccessories")
    K.check([str(x) for x in V3.KEYS] == [V3E.key(e[0], e[1], e[2]) for e in rows] and [int(x) for x in V3.CAP] == [5, 5, 5]
            and str(V3.READS) == V3E.reads_csv("SkyyAccessories"), "TBL AccV3 = the trees_v3_effects rows (caps 5): %s" % V3.READS)
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
    u = UUID.fromString("00000000-0000-0000-0000-00000000a3b1")
    k = str(u)
    Pw.pick(u, k, "Mining", 1000000, False)

    def src():
        m = br.get("skill:bonus:" + k)
        s = m.get("accessories") if m is not None else None
        return dict((str(a), float(b)) for a, b in dict(s).items()) if s is not None else {}
    bag = S("Skyy_Talisman_Vitality_Epic", "Skyy_Talisman_Vitality_Common", "Skyy_Talisman_Speed_Rare", "Skyy_Accessory_Workbench_T3",
            "Skyy_Accessory_Workbench_T1", "Skyy_Accessory_Alchemybench_T1")
    K.eq(int(V3.count(bag)), 3, "CNT 3 counting: Vitality (the lower copy adds 0), Speed, Workbench (the lower one adds 0), the retired bench 0")
    K.eq(int(V3.count(S(OMNI, "Skyy_Accessory_Workbench_T3", "Skyy_Talisman_Speed_Rare"))), 2, "CNT the Omni = 1 (a bench next to it 0) + Speed")
    K.eq(int(V3.count(S())), 0, "CNT an empty bag = 0")
    Pw.tick(u, bag)
    s0 = src()
    K.check(set(s0) == {"dd.mining"}, "R0 rank 0: exactly the 0.5.27 source (the Mining Power's Fortune): %s" % s0)
    kt = V3E.key("Mining", 2, "r4a")
    RANK[kt] = 2
    Pw.tick(u, bag)
    s1 = src()
    K.check(abs(s1["dd.mining"] - (s0["dd.mining"] + 0.06)) < 1e-9, "TS Trinket Seams rank 2 x 3 accessories = +0.06 dd.mining on top of the Power's: %s -> %s" % (s0, s1))
    big = S(*["Skyy_Talisman_%s_Common" % f for f in ("Vitality", "Speed", "Lantern", "Strength", "Defense", "Crit", "MagicPower", "Feather")])
    nb = int(V3.count(big))
    RANK[kt] = 3
    Pw.tick(u, big)
    s2 = src()
    base2 = float(dict(Pw.LASTB.get(u)).get("dd.mining")) if False else None
    RANK[kt] = 0
    Pw.tick(u, big)
    s2b = src()
    K.check(nb > 5 and abs(s2["dd.mining"] - (s2b["dd.mining"] + 0.15)) < 1e-9,
            "CEIL (fixer 2) rank 3 x 5 counting accessories (of %d) = exactly the row's ceiling +15 Fortune - the top rank adds: %s vs %s" % (nb, s2, s2b))
    K.check(abs(float(V3.V3X0) - 15.0) < 1e-9 and abs(float(V3.V3P0) - 1.0) < 1e-9 and abs(float(V3.v3most(0)) - 0.15) < 1e-12,
            "CFG (fixer) the Server Setup numbers = the table: 1 %% a rank, at most 15 %%")
    V3.V3P0 = 2.0          # a server owner doubles the per-rank number: the ceiling holds it at 15
    RANK[kt] = 3
    Pw.tick(u, big)
    K.check(abs(src()["dd.mining"] - (s2b["dd.mining"] + 0.15)) < 1e-9, "CEIL a per-rank 2 (30 %%) stops at the ceiling 15: %s" % src())
    V3.V3X0 = 100.0          # ... and lifts the ceiling: the 5-accessory cap shows
    Pw.tick(u, big)
    K.check(abs(src()["dd.mining"] - (s2b["dd.mining"] + 0.30)) < 1e-9, "CAP %d counting accessories are capped at 5: rank 3 x 5 x 2 %% = +0.30 (ceiling 100): %s" % (nb, src()))
    V3.V3P0 = 1.0
    RANK[kt] = 99
    Pw.tick(u, bag)
    K.check(abs(src()["dd.mining"] - (s0["dd.mining"] + 0.09)) < 1e-9, "MAX a rank of 99 is clamped to Trinket Seams' max 3: %s" % src())
    V3.V3X0 = 15.0
    V3.V3P0 = 0.0
    Pw.tick(u, bag)
    K.check(abs(src()["dd.mining"] - s0["dd.mining"]) < 1e-9, "CFG (fixer) per rank 0 = the row gives nothing: %s" % src())
    V3.V3P0 = 1.0
    RANK[kt] = "boom"
    Pw.tick(u, bag)
    K.check(abs(src()["dd.mining"] - s0["dd.mining"]) < 1e-9, "BAD a throwing answer = rank 0")
    RANK[kt] = "two"
    Pw.tick(u, bag)
    K.check(abs(src()["dd.mining"] - s0["dd.mining"]) < 1e-9, "BAD a non-number = rank 0")
    RANK.clear()
    kb = V3E.key("Foraging", 3, "r4a")
    RANK[kb] = 1
    Pw.tick(u, bag)
    K.check(abs(src().get("dd.foraging", 0) - 0.03) < 1e-9 and abs(src()["dd.mining"] - s0["dd.mining"]) < 1e-9,
            "AB Accessory Boughs rank 1 x 3 = dd.foraging 0.03 with the Mining Power picked (no Power stat of its own): %s" % src())
    Pw.ON = False
    Pw.tick(u, bag)
    K.check(src() == {"dd.foraging": 0.03}, "AB ... power.enabled off: the tree row stays (the Power's Fortune goes): %s" % src())
    Pw.ON = True
    br.remove("skill:fn:level")
    Pw.tick(u, bag)
    K.check("dd.foraging" not in src(), "NOREADER no SkyySkills (no Fortune reader): no tree rows: %s" % src())
    br.put("skill:fn:level", Lv())
    br.put("profile:busy:" + k, JObject(True, "java.lang.Boolean"))
    r_busy = Pw.tick(u, bag)
    br.remove("profile:busy:" + k)
    K.check(not src(), "BUSY profile:busy: the source goes (0.5.22 rule) - tree rows included")
    Pw.tick(u, bag)
    K.check(abs(src().get("dd.foraging", 0) - 0.03) < 1e-9, "BUSY ... and comes back the next second")
    # fixer 2: Combat Accessory Plates - flat max Health into tick's c[0] (the skyyacc_health modifier AccEffects writes)
    RANK.clear()
    kp = V3E.key("Combat", 2, "r4a")
    ip = [i for i, e in enumerate(rows) if (e[0], e[2]) == ("Combat", "r4a")][0]
    K.check(str(V3.EFF[ip]) == "hp" and abs(float(getattr(V3, "V3P%d" % ip)) - 2.0) < 1e-9 and abs(float(getattr(V3, "V3X%d" % ip)) - 30.0) < 1e-9,
            "PLATES the row = hp, 2 a rank, at most 30 (the table)")
    h0 = float(Pw.tick(u, bag)[0])
    sp = src()
    RANK[kp] = 2
    h1 = float(Pw.tick(u, bag)[0])
    K.check(abs(h1 - h0 - 12.0) < 1e-9, "PLATES rank 2 x 3 counting accessories = +12 max Health in c[0] (%s -> %s)" % (h0, h1))
    K.check("hp" not in src() and src() == sp, "PLATES never in the Fortune source: %s" % src())
    RANK[kp] = 3
    h2 = float(Pw.tick(u, big)[0])
    RANK[kp] = 0
    h2b = float(Pw.tick(u, big)[0])
    K.check(abs(h2 - h2b - 30.0) < 1e-9, "PLATES rank 3 x 5 (cap, of %d) = +30 = the ceiling, the top rank adds (%s vs %s)" % (nb, h2, h2b))
    RANK[kp] = 3
    setattr(V3, "V3X%d" % ip, 20.0)
    K.check(abs(float(Pw.tick(u, big)[0]) - h2b - 20.0) < 1e-9, "PLATES a Server Setup ceiling of 20 cuts it to +20")
    setattr(V3, "V3X%d" % ip, 30.0)
    Pw.ON = False
    br.remove("skill:fn:level")
    hb = Pw.tick(u, bag)
    K.check(hb is not None and abs(float(hb[0]) - 18.0) < 1e-9, "PLATES Power off + no SkyySkills: still +18 (rank 3 x 3), no reader needed: %s" % (None if hb is None else float(hb[0])))
    Pw.ON = True
    br.put("skill:fn:level", Lv())
    RANK.clear()
    K.check(abs(float(Pw.tick(u, bag)[0]) - h0) < 1e-9, "PLATES rank 0 again = the 0.5.27 Health sum")
    V3.reads(True)
    K.check(str(br.get("tree:reads:SkyyAccessories")) == str(V3.READS), "READS published")
    br.put("tree:reads:SkyyAccessories", "x")
    V3.reads(False)
    K.check(str(br.get("tree:reads:SkyyAccessories")) == "x", "READS only our own value is removed")
    br.put("tree:reads:SkyyAccessories", V3.READS)
    V3.reads(False)
    K.check(br.get("tree:reads:SkyyAccessories") is None, "READS ours is removed")
    br.remove("tree:fn:level")
    K.eq(int(V3.rank(u, kb, 3)), 0, "NOTREES no tree:fn:level = rank 0")
    # fixer: trees.properties next to power.properties - seeded with the table's text, hand edits read, a bad line keeps the built-in number
    tf = os.path.join(home, "trees.properties")
    if os.path.exists(tf):
        os.remove(tf)
    res = str(V3.loadV3(Paths.get(home)))
    K.check(os.path.exists(tf) and open(tf, encoding="latin-1", newline="").read() == V3E.cfg_text("SkyyAccessories") and res == "trees.properties read",
            "LOAD a missing trees.properties is written with the table's defaults (%s)" % res)
    ck = V3E.ckey(rows[1])
    t_ = open(tf, encoding="latin-1", newline="").read().replace("%s.max=15\n" % ck, "%s.max=10\n" % ck).replace("%s.per=1\n" % ck, "%s.per=999\n" % ck)
    open(tf, "w", encoding="latin-1", newline="").write(t_)
    V3.loadV3(Paths.get(home))
    K.check(abs(float(V3.V3X1) - 10.0) < 1e-9 and abs(float(V3.V3P1) - 1.0) < 1e-9, "LOAD a hand edit (Boughs max 10) is read; an out-of-range line (per 999) keeps 1")
    res2 = str(V3.loadV3(Paths.get(home)))
    K.check(open(tf, encoding="latin-1", newline="").read() == t_ and res2 == "trees.properties read", "LOAD a second read writes nothing")
    V3.V3X1 = 15.0
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyAccessories", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=["AccV3"],
           phases=[("v3", run_v3), ("power", T22.run_power), ("live", T22.run_live)],
           script=__file__, live=(T22.LIVE_DIR, "Skyy_SkyyAccessories"))
