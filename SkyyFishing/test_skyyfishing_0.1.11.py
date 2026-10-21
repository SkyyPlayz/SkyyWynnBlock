"""Harness for SkyyFishing 0.1.11 (Skill Trees 3 R3b, LIGHT: the Fishing tree's Sharp Hook / Fish Fortune / Salvage Hook through the 0.3 node
aliases; tools/fishing_0_1_11_patch.py). Build first: python tools/fishing_0_1_11_patch.py && python SkyyFishing/build_skyyfishing_0.1.11.py

    python SkyyFishing/test_skyyfishing_0.1.11.py [--dir <folder inside tools/dev/scratch/>] [--keep]

  A / C / AA  verify (-Xverify:all), class compare 0.1.10 -> 0.1.11 (exactly the planned members), engine-access audit
  TREE  EXECUTED: FishBridge.accx (what every cast calls) with a fake SkyyTrees tree:fn:bonus: no SkyyTrees / rank 0 = exactly 0.1.10's
        accessory numbers; Fishing.NBite 0.09 (Sharp Hook rank 3) -> +9 % speed, Fishing.NTreasure 0.015 -> +1.5 % treasure,
        Fishing.NFortune 0.04 -> +4 % double, ADDED to the accessories' (8 / 1 / 2 %); negatives / NaN / text / a throw = 0; the sum stays
        within 1000; the node asked = exactly the three keys with the player's UUID; FishRig.withAcc + addGear keep the fish.cap.* caps;
        questInit publishes tree:reads:SkyyFishing (= the three nodes SkyyTrees 0.4.0 waits for), shutdown removes only ours
  ACC   0.1.10's ACC phase on this jar (the accessories path unchanged)
  X / Q / ST  0.1.5's exec + quest phases and the LIVE phase (start twice on a scratch COPY of the live Skyy_SkyyFishing) on this jar
Exit code 1 on any failure.
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.1.11"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "st3r3b", "fish")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyFishing-%s.jar" % VERSION)]
_spec = importlib.util.spec_from_file_location("test_skyyfishing_0_1_10", os.path.join(HERE, "test_skyyfishing_0.1.10.py"))
T110 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T110)
T15 = T110.T15
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyFishing-0.1.10.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.fishing."
EXPECT = {
    "FishBridge": sorted(["+f TREE_NODES", "+f TREE_READS", "+m treeNum", "+m treex", "+m treeReads", "+m accx0", "~m accx", "~m questInit", "+<clinit>"]),
    "FishCmds": ["~m admin"],          # the /fishadmin stats line names the version
    "CfgRows": ["~<clinit>", "~m header"], "CfgFn": ["~m opExport"], "SkyyFishingPlugin": ["~m setup", "~m shutdown"],
    "FishCfg": ["~m applyAll", "~m seed"],
}
ADDED = []
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyFishing")   # the deploy world (read-only; copied)


def run_tree(out, jar, scratch, _home):
    from jpype import JClass, JArray, JDouble, JImplements, JOverride, JObject, JString
    K = HK.Child(out)
    P, mods = T110.setup(K, JAR, scratch, "tree")
    Brg, Rig, Cfg = P("FishBridge"), P("FishRig"), P("FishCfg")
    UUID, HM, CHM, D = JClass("java.util.UUID"), JClass("java.util.HashMap"), JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.lang.Double")
    u = UUID.fromString(T110.U1S)
    br = Brg.bridge()
    K.eq([str(x) for x in Brg.TREE_NODES], ["Fishing.NBite", "Fishing.NFortune", "Fishing.NTreasure"], "TREE the three nodes")
    K.eq([float(x) for x in Brg.accx(u)], [0.0, 0.0, 0.0], "TREE no SkyyTrees, no accessories = nothing (0.1.10)")
    m = HM()
    m.put("fspd.fishing", D(0.08)); m.put("dd.fishing", D(0.02)); m.put("treasure.fishing", D(0.01))
    src = CHM()
    src.put("accessories", m)
    br.put("skill:bonus:" + str(u), src)
    K.eq([round(float(x), 6) for x in Brg.accx(u)], [8.0, 1.0, 2.0], "TREE no SkyyTrees: exactly 0.1.10's accessory numbers")
    NODE = {}
    ASKED = []

    @JImplements("java.util.function.Function")
    class Bonus(object):
        @JOverride
        def apply(self, a):
            ASKED.append((str(a[0]), str(a[1])))
            v = NODE.get(str(a[1]), 0.0)
            if v == "boom":
                raise RuntimeError("boom")
            if isinstance(v, str):
                return JString(v)
            return JObject(v, "java.lang.Double")
    br.put("tree:fn:bonus", Bonus())
    K.eq([round(float(x), 6) for x in Brg.accx(u)], [8.0, 1.0, 2.0], "TREE rank 0 everywhere (SkyyTrees answers 0.0) = 0.1.10's numbers")
    K.check(sorted(set(n for _u, n in ASKED)) == ["Fishing.NBite", "Fishing.NFortune", "Fishing.NTreasure"] and all(x == str(u) for x, _n in ASKED),
            "TREE asks exactly the three nodes with the player's UUID: %s" % sorted(set(ASKED)))
    NODE.update({"Fishing.NBite": 0.09, "Fishing.NTreasure": 0.015, "Fishing.NFortune": 0.04})
    K.eq([round(float(x), 6) for x in Brg.accx(u)], [17.0, 2.5, 6.0], "TREE Sharp Hook +9 %, Salvage Hook +1.5 %, Fish Fortune +4 % ADDED to the accessories'")
    src.remove("accessories")
    K.eq([round(float(x), 6) for x in Brg.accx(u)], [9.0, 1.5, 4.0], "TREE the tree alone (no accessories)")
    NODE.update({"Fishing.NBite": -0.5, "Fishing.NTreasure": float("nan"), "Fishing.NFortune": "x"})
    K.eq([float(x) for x in Brg.accx(u)], [0.0, 0.0, 0.0], "TREE BAD: negative / NaN / text = 0")
    NODE.update({"Fishing.NBite": "boom", "Fishing.NTreasure": 0.0, "Fishing.NFortune": 0.0})
    K.eq([float(x) for x in Brg.accx(u)], [0.0, 0.0, 0.0], "TREE a throwing SkyyTrees = 0 (the cast goes on)")
    NODE.update({"Fishing.NBite": 50.0})
    m3 = HM(); m3.put("fspd.fishing", D(9.0))
    src.put("accessories", m3)
    K.eq(float(Brg.accx(u)[0]), 1000.0, "TREE the sum stays within 1000")
    caps = [float(x) for x in Cfg.CAP]
    capst = [int(x) for x in Cfg.CAP_STAT]
    st = JArray(JDouble)(12)
    Rig.addGear(st, Rig.withAcc(JArray(JDouble)([0.0, 0.0, 0.0, 0.0, 0.0]), Brg.accx(u)))
    for cp, si in zip(caps, capst):
        if si == int(Rig.ST_SPEED):
            K.check(float(st[si]) <= cp, "TREE CAP: Fishing Speed stays at its fish.cap row (%s <= %s)" % (float(st[si]), cp))
    Brg.questInit()
    K.eq(str(br.get("tree:reads:SkyyFishing")), "Fishing.NBite,Fishing.NFortune,Fishing.NTreasure", "TREE questInit publishes tree:reads:SkyyFishing")
    br.put("tree:reads:SkyyFishing", "other")
    Brg.treeReads(False)
    K.eq(str(br.get("tree:reads:SkyyFishing")), "other", "TREE shutdown removes only our own value")
    br.put("tree:reads:SkyyFishing", Brg.TREE_READS)
    Brg.treeReads(False)
    K.check(br.get("tree:reads:SkyyFishing") is None, "TREE ... ours goes")
    # SkyyTrees 0.4.0's own reader list: these three nodes name SkyyFishing in READ_BY (so the listing makes them live)
    tsrc = open(os.path.join(ROOT, "SkyyTrees", "build_skyytrees_0.4.0.py"), encoding="utf8").read()
    K.check(all(('"%s": ("SkyyFishing",)' % n) in tsrc for n in ("NBite", "NFortune", "NTreasure")), "TREE SkyyTrees 0.4.0 READ_BY names SkyyFishing for the three nodes")
    P("FishStore").stopIO()
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyFishing", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("tree", run_tree), ("acc", T110.run_acc), ("exec", T15.run_exec), ("quest", T15.run_quest), ("live", T15.run_live)],
           script=__file__, live=(LIVE_DIR, "Skyy_SkyyFishing"))
