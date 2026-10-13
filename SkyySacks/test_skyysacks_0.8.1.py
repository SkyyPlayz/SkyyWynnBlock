"""Harness for SkyySacks 0.8.1 (the Enchanted materials go in the Void; tools/sacks_0_8_1_patch.py).
Build first: python tools/sacks_0_8_1_patch.py && python SkyySacks/build_skyysacks_0.8.1.py

    python SkyySacks/test_skyysacks_0.8.1.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.8.0 -> 0.8.1: exactly SackDefs (+ enchCat, ~ homeOf), BagMirror (+ addRecipe, ~ wantedFor) and the version constants
              differ; non-class files: manifest only
  X  exec     EXECUTED on the compiled classes: SackDefs.enchCat / homeOf / catOf of the 19 Enchanted ids = tools/skyyench.py's table
              (Python mirror cat_of); an unknown Skyy_Ench_ id, a near miss (lower case, prefix only, null) -> null; EVERY Assets.zip item
              id and the 22 bag ids get exactly 0.8.0's homeOf AND catOf (no other routing changed); catIndex of each Enchanted category
              is a Void tab; BagMirror.addRecipe (ench01fix2) on REAL engine CraftingRecipes: an Enchanted compress recipe adds nothing to
              a bench's wanted set, a vanilla-style recipe adds its item + resource type inputs, a non-recipe is ignored
  D  live     a scratch COPY of the live Skyy_SkyySacks: every pool file loads with 0.8.0 and 0.8.1 into the same map (SackPool.pool),
              twice (two starts); the folder bytes are unchanged afterwards
  AA engine-access audit
Scratch: tools/dev/scratch/ench01/sacks (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import skyyench as EN

VERSION = "0.8.1"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySacks-0.8.0.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "ench01", "sacks")))
PKG = "com.skyy.sacks."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyySacks")
EXPECT = {
    "SackDefs": ["+m enchCat", "~m homeOf"],
    "BagMirror": ["+m addRecipe", "~m wantedFor"],   # ench01fix2: Enchanted recipes do not widen a bench's wanted set
    "SkyySacksPlugin": ["~m setup"],          # the ready line's version text
    "CfgFn": ["~m opExport"],                 # the config kit's version text
    "CfgRows": ["~m header"],
}
ADDED = []


def loader_for(jar):
    from jpype import JClass, JArray
    URL = JClass("java.net.URL")
    arr = JArray(URL)(1)
    arr[0] = JClass("java.io.File")(jar).toURI().toURL()
    return JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getSystemClassLoader())


def assets_ids():
    with zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")) as z:
        return sorted(n.rsplit("/", 1)[1][:-5] for n in z.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))


def run_exec(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    N = JClass(PKG + "SackDefs", loader=loader_for(jar))
    O = JClass(PKG + "SackDefs", loader=loader_for(OLD_JAR))
    for eid in EN.IDS:
        want = EN.cat_of(eid)
        K.eq(str(N.enchCat(eid)), want, "X enchCat %s" % eid)
        K.eq(str(N.homeOf(eid)), want, "X homeOf %s" % eid)
        K.eq(str(N.catOf(eid)), want, "X catOf %s (new items are taken in)" % eid)
        K.check(O.homeOf(eid) is None, "X control: 0.8.0 stored no %s" % eid)
        K.check(int(N.catIndex(want)) >= 0, "X %s's category %s is a Void tab" % (eid, want))
    for bad in ("Skyy_Ench_Mithril", "Skyy_Ench_", "skyy_ench_iron", "Skyy_Ench_Iron_Block", "Skyy_EnchIron"):
        K.check(N.homeOf(bad) is None and N.catOf(bad) is None and N.enchCat(bad) is None, "X unknown %s -> never stored" % bad)
    K.check(N.enchCat(None) is None and N.homeOf(None) is None, "X null -> null")
    ids = assets_ids() + ["Skyy_Sack_%s_%s" % (c, t) for c in ("Mining", "Foraging", "Farming", "Combat", "Smithing")
                          for t in ("Small", "Medium", "Rare", "Large")] + ["Skyy_Sack_Omni", "Skyy_Sack_Pocket", "Skyy_Cook_Bread_Gold"]
    diff = [i for i in ids if (O.homeOf(i), O.catOf(i)) != (N.homeOf(i), N.catOf(i))]
    K.eq(diff, [], "X every other id routes exactly like 0.8.0 (%d ids)" % len(ids))
    # ---- ench01fix2: BagMirror.addRecipe on real engine recipes
    BM = JClass(PKG + "BagMirror", loader=loader_for(jar))
    MQ = JClass("com.hypixel.hytale.server.core.inventory.MaterialQuantity")
    CR = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
    BR = JClass("com.hypixel.hytale.protocol.BenchRequirement")
    from jpype import JArray
    def mq(item, rt, q):
        return MQ(item, rt, None, q, None)
    def recipe(ins, out):
        a = JArray(MQ)(len(ins))
        for i_, x in enumerate(ins):
            a[i_] = x
        return CR(a, mq(out, None, 1), JArray(MQ)(0), 1, JArray(BR)(0), 1.0, True, 0)
    HS = JClass("java.util.HashSet")
    for k_, t_ in enumerate(EN.TABLE):
        s_ = HS()
        inp = mq(t_[2], None, 100) if t_[1] == "I" else mq(None, t_[2], 100)
        K.check(not BM.addRecipe(s_, recipe([inp], EN.IDS[k_])) and s_.size() == 0, "X addRecipe: %s's compress recipe adds nothing to the wanted set" % EN.IDS[k_])
    s_ = HS()
    K.check(bool(BM.addRecipe(s_, recipe([mq("Plant_Crop_Wheat_Item", None, 3), mq(None, "Wood_Trunk", 2)], "Furniture_Crude_Chest")))
            and sorted(str(x) for x in s_) == ["Plant_Crop_Wheat_Item", "Wood_Trunk"], "X addRecipe: a normal recipe adds its item + resource type inputs (%s)" % sorted(str(x) for x in s_))
    s_ = HS()
    K.check(not BM.addRecipe(s_, JClass("java.lang.String")("x")) and not BM.addRecipe(s_, None) and s_.size() == 0, "X addRecipe: a non-recipe / null is ignored")
    s_ = HS()
    K.check(bool(BM.addRecipe(s_, recipe([mq("Ore_Iron", None, 1)], "Skyy_Enchanted_Lookalike"))) and s_.size() == 1, "X addRecipe: only the exact Skyy_Ench_ prefix is skipped")
    K.notes.append("X: 19 Enchanted ids -> %s; %d other ids unchanged" % (
        ", ".join("%s %d" % (c, sum(1 for t in EN.TABLE if t[5] == c)) for c in EN.CATS), len(ids)))
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    before = HK.tree_hash(home)
    pools = os.path.join(home, "pools")
    keys = sorted(f[:-11] for f in os.listdir(pools) if f.endswith(".properties")) if os.path.isdir(pools) else []
    P = JClass("java.nio.file.Paths")
    seen = None
    for start in (1, 2):
        for j in (OLD_JAR, jar):
            SP = JClass(PKG + "SackPool", loader=loader_for(j))
            SP.DIR = P.get(pools)
            got = {}
            for k in keys:
                m = SP.pool(k)
                got[k] = dict((str(e.getKey()), int(e.getValue().longValue())) for e in m.entrySet())
            if seen is None:
                seen = got
            K.check(got == seen, "D start %d %s: every pool loads the same items" % (start, os.path.basename(j)))
    K.eq(HK.tree_hash(home), before, "D the live copy's bytes are unchanged")
    K.notes.append("D: %d profile pools, %d stored item lines" % (len(keys), sum(len(v) for v in (seen or {}).values())))
    K.save()


HK.run("SkyySacks", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("exec", run_exec), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyySacks"))
