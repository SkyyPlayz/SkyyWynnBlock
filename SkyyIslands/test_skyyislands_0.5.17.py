"""Harness for SkyyIslands 0.5.17 (NO SECOND COPY FROM THE STARTER KIT; tools/islands_0_5_17_patch.py).
Build first:  python tools/islands_0_5_17_patch.py && python SkyyIslands/build_skyyislands_0.5.17.py

    python SkyyIslands/test_skyyislands_0.5.17.py [--dir <folder inside tools/dev/scratch/>] [--keep]

  A / C / AA  verify (-Xverify:all), class compare 0.5.16 -> 0.5.17 (FillTask + the version texts only), engine-access audit
  KIT   EXECUTED on the jar's FillTask.kitFor / kitSkip / toolKind with a stand-in bridge (the real tools/skyyonce.py contract):
        the DEFAULT kit + once:item:Skyy_Accessory_Bag = TRUE -> the bag is left out, the other 5 stacks stay in order (no 2nd Accessory
        Bag after /island reset); FALSE / absent -> 0.5.16's kit exactly; once:item for the Pocket Dimension / Menu item an admin added;
        a lifelong-kind tool (pickaxe / hatchet / hoe / sickle / rod / watering can) with gear:fn:lifelong naming a uid for the owner's
        ACTIVE profile -> left out; no uid, another profile's key, no SkyyGear -> kept; plain items never asked; a bridge function that
        throws keeps the stack; the bytecode: starterKit reads kitFor (not IslandCfg.kit) with the world's owner
  D     the live NewBetaTest Skyy_SkyyIslands config COPY: its starter.kit read twice through IslandCfg.kitOf -> kitFor leaves out only the
        Accessory Bag (while once:item says TRUE); no file of the copy changed
Exit code 1 on any failure.
"""
import os, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK

VERSION = "0.5.17"
PKG = "com.skyy.islands."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyIslands-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyIslands-0.5.16.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "life01", "isl")))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyIslands")
DEFAULT_KIT = "Bench_WorkBench:1,Wood_Oak_Trunk:10,Soil_Dirt:8,Ingredient_Stick:8,Food_Bread:5,Skyy_Accessory_Bag:1"
EXPECT = {
    "FillTask": ["+m toolKind", "+m kitSkip", "+m kitFor", "~m starterKit"],
    "IslandCfg": ["~m load"],                  # the version in the default file's first line
    "SkyyIslandsPlugin": ["~m setup"],         # the version (+ the committed kit's id) in the ready line
    "CfgRows": ["~<clinit>", "~m header"],
    "CfgFn": ["~m opExport"],
}


def run_kit(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    CHM, System = JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.lang.System")
    bridge = CHM()
    System.getProperties().put("skyy.bridge", bridge)
    Fill, Cfg, Store = JClass(PKG + "FillTask"), JClass(PKG + "IslandCfg"), JClass(PKG + "IslandStore")
    try:
        Store.BRIDGE = bridge
    except Exception:
        pass
    Bool = JClass("java.lang.Boolean")
    OWNER = "00000000-0000-0000-0000-0000000015a1"
    OWNER2 = OWNER + "-p2"
    ASKED = []

    @JImplements("java.util.function.Function")
    class Once(object):
        def __init__(self, v):
            self.v = v

        @JOverride
        def apply(self, o):
            ASKED.append(("once", str(o[1]) if o is not None and len(o) > 1 else None))
            if self.v == "throw":
                raise RuntimeError("boom")
            return Bool.TRUE if self.v else Bool.FALSE

    LL = {}

    @JImplements("java.util.function.Function")
    class Life(object):
        @JOverride
        def apply(self, o):
            ASKED.append(("gear", str(o[1])))
            return LL.get(str(o[1]))

    KEY = {"k": OWNER}

    @JImplements("java.util.function.Function")
    class KeyFn(object):
        @JOverride
        def apply(self, u):
            return KEY["k"]
    bridge.put("profile:fn:key", KeyFn())

    def kit_of(owner):
        r = Fill.kitFor(owner)
        return [(str(i), int(q)) for i, q in zip(r[0], r[1])]
    Cfg.STARTER_KIT = DEFAULT_KIT
    full = [(e.split(":")[0], int(e.split(":")[1])) for e in DEFAULT_KIT.split(",")]
    K.eq(kit_of(OWNER), full, "KIT no once:item on the bridge -> the default kit exactly (0.5.16)")
    bridge.put("once:item:Skyy_Accessory_Bag", Once(True))
    del ASKED[:]
    K.eq(kit_of(OWNER), full[:-1], "KIT once:item:Skyy_Accessory_Bag = TRUE -> the Accessory Bag is left out, the other 5 stacks stay in order")
    K.check([a for a in ASKED if a[0] == "once"] == [("once", OWNER)], "KIT ... only the bag's once:item was asked (with the owner key): %s" % ASKED)
    bridge.put("once:item:Skyy_Accessory_Bag", Once(False))
    K.eq(kit_of(OWNER), full, "KIT once:item = FALSE (the owner's switch off) -> the bag stays in the kit")
    bridge.put("once:item:Skyy_Accessory_Bag", Once("throw"))
    K.eq(kit_of(OWNER), full, "KIT a once:item that throws -> the stack stays (never lost)")
    bridge.put("once:item:Skyy_Accessory_Bag", Once(True))
    bridge.put("once:item:Skyy_Sack_Pocket", Once(True))
    bridge.put("once:item:Skyy_Menu", Once(True))
    Cfg.STARTER_KIT = DEFAULT_KIT + ",Skyy_Sack_Pocket:1,Skyy_Menu:1,Tool_Pickaxe_Crude:1,Tool_Hatchet_Crude:1,Tool_Shovel_Crude:1,SkyyFishing_Rod_Bamboo:1,Tool_WaterCan_Crude:1,Tool_Hoe_Copper:1,Tool_Sickle_Crude:1"
    K.eq(kit_of(OWNER), full[:-1] + [("Tool_Pickaxe_Crude", 1), ("Tool_Hatchet_Crude", 1), ("Tool_Shovel_Crude", 1), ("SkyyFishing_Rod_Bamboo", 1),
                                     ("Tool_WaterCan_Crude", 1), ("Tool_Hoe_Copper", 1), ("Tool_Sickle_Crude", 1)],
         "KIT an admin kit with the Pocket Dimension + the Menu item: both left out (once:item); no SkyyGear -> every tool kept")
    bridge.put("gear:fn:lifelong", Life())
    LL.update({"pickaxe": "uid-p", "pole": "uid-r", "can": "uid-c", "hoe": "uid-h"})
    del ASKED[:]
    got = kit_of(OWNER)
    K.eq(got, full[:-1] + [("Tool_Hatchet_Crude", 1), ("Tool_Shovel_Crude", 1), ("Tool_Sickle_Crude", 1)],
         "KIT SkyyGear names lifelong pickaxe / rod / can / hoe uids for the owner's profile -> those kit tools are left out; hatchet + sickle "
         "(no uid) and the shovel (no lifelong kind) stay")
    K.check(sorted(a[1] for a in ASKED if a[0] == "gear") == sorted(["pickaxe", "hatchet", "pole", "can", "hoe", "sickle"]),
            "KIT ... gear:fn:lifelong asked once per tool kind, never for a plain item: %s" % [a for a in ASKED if a[0] == "gear"])
    KEY["k"] = OWNER2
    K.eq(kit_of(OWNER), full[:-1] + [("Tool_Pickaxe_Crude", 1), ("Tool_Hatchet_Crude", 1), ("Tool_Shovel_Crude", 1), ("SkyyFishing_Rod_Bamboo", 1),
                                     ("Tool_WaterCan_Crude", 1), ("Tool_Hoe_Copper", 1), ("Tool_Sickle_Crude", 1)],
         "KIT the owner's ACTIVE profile is another one (key mismatch) -> gear's answer is not about this island: every tool kept")
    KEY["k"] = OWNER
    K.eq(kit_of(None), full[:-1] + [("Tool_Pickaxe_Crude", 1), ("Tool_Hatchet_Crude", 1), ("Tool_Shovel_Crude", 1), ("SkyyFishing_Rod_Bamboo", 1),
                                    ("Tool_WaterCan_Crude", 1), ("Tool_Hoe_Copper", 1), ("Tool_Sickle_Crude", 1)],
         "KIT no owner known -> once:item still applies, tools kept")
    K.check([str(Fill.toolKind(x)) if Fill.toolKind(x) is not None else None for x in ("Tool_Pickaxe_Iron", "Tool_Hatchet_Iron", "Tool_Hoe_Iron", "Tool_Sickle_Iron", "SkyyFishing_Rod_Iron", "Tool_WaterCan_Iron", "Tool_Shovel_Iron", "Skyy_Accessory_Bag")]
            == ["pickaxe", "hatchet", "hoe", "sickle", "pole", "can", None, None], "KIT toolKind maps the six lifelong kinds only")
    Cfg.STARTER_KIT = ""
    K.eq(kit_of(OWNER), [], "KIT an empty kit stays empty")
    # bytecode: starterKit reads kitFor with the world's owner, never IslandCfg.kit() directly
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(jar)
    IP = JClass("javassist.bytecode.InstructionPrinter")
    m = [x for x in cp.get(PKG + "FillTask").getDeclaredMethods() if str(x.getName()) == "starterKit"][0]
    it = m.getMethodInfo().getCodeAttribute().iterator()
    cpl = m.getMethodInfo().getConstPool()
    code = []
    while it.hasNext():
        code.append(str(IP.instructionString(it, it.next(), cpl)))
    code = "\n".join(code)
    K.check("FillTask.kitFor" in code and "IslandStore.ownerOf" in code and "IslandCfg.kit(" not in code,
            "KIT starterKit (new island, /island reset, 3-island fill, late kit) takes its stacks from kitFor(ownerOf(world))")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    h0 = HK.tree_hash(home)
    f = os.path.join(home, "config.properties")
    kit = None
    if os.path.isfile(f):
        for ln in open(f, encoding="latin-1").read().splitlines():
            if ln.startswith("starter.kit="):
                kit = ln.split("=", 1)[1].strip()
    K.notes.append("D live starter.kit = %r" % kit)
    kit = kit if kit else DEFAULT_KIT
    CHM, System = JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.lang.System")
    bridge = CHM()
    System.getProperties().put("skyy.bridge", bridge)

    @JImplements("java.util.function.Function")
    class Once(object):
        @JOverride
        def apply(self, o):
            return JClass("java.lang.Boolean").TRUE
    bridge.put("once:item:Skyy_Accessory_Bag", Once())
    Fill, Cfg = JClass(PKG + "FillTask"), JClass(PKG + "IslandCfg")
    res = []
    for start in (1, 2):
        Cfg.STARTER_KIT = kit
        r = Fill.kitFor("00000000-0000-0000-0000-0000000015a2")
        res.append([str(i) for i in r[0]])
    want = [e.split(":")[0].strip() for e in kit.split(",") if e.strip() and e.split(":")[0].strip() != "Skyy_Accessory_Bag"]
    K.check(res[0] == res[1] == want, "D the live kit twice: only the Accessory Bag left out: %s" % res[0])
    K.check(HK.tree_hash(home) == h0, "D no file of the copy changed")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyIslands", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("kit", run_kit), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyIslands"))
