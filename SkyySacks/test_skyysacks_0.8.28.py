"""Harness for SkyySacks 0.8.28 (sacks:fn:craftWhy + CraftPage.tierOk - tools/sacks_0_8_28_patch.py). Build first:
    python tools/sacks_0_8_28_patch.py && python SkyySacks/build_skyysacks_0.8.28.py

    python SkyySacks/test_skyysacks_0.8.28.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.8.27 -> 0.8.28: only CraftPage (+tierOk, ~benchRecipes), SackBridge (+benchNeed, +whyCode, ~dflt, ~call2), SackFn (~apply),
                 the plugin setup (the new bridge key + the version text) and the config kit version texts differ; non-class files: manifest
  ROOT  Skyy's 10-22 state, from the files: SkyyGear 0.3.36's SkyyGear_Recipe_Armor_Bronze_<Slot> = Armor_Bench (no tier = 1),
        KnowledgeRequired; SkyyCollections 0.2.31 grants it at Copper V + Iron V; the live profile p3 has Armor_Bench_T2 equipped and
        Copper / Iron below V (so the knowledge rule, not the accessory, keeps the recipe locked)
  BENCH the accessory rule on the real chain: SkyyAccessories 0.5.31 AccDefs.benchList(bag) -> acc:has:<uuid> -> SkyySacks
        CraftPage.accessories -> tierOk: Skyy's exact bag (Armor Bench II -> a tier-1 Armor_Bench recipe allowed), T1 -> allowed, none ->
        refused; EVERY active bench x every equipped tier x every need tier (allowed exactly when need <= equipped), the Omni = every bench
        at max, retired accessories unlock nothing; the bridge sacks:fn:craftWhy answers null on bad arguments (never throws)
  ARMB  (packprep) the 4 vanilla "ArmorBench" Utility recipes: Assets.zip has exactly those 4 with that bench id; every Crafting bench id of
        Assets.zip mapped through CraftPage.benchKey collides only ArmorBench / Armor_Bench; an Armor Bench charm (any tier) unlocks
        "ArmorBench" through accTier / tierOk, no charm / another bench's charm does not
  D     START TWICE on a scratch COPY of NewBetaTest's Skyy_SkyySacks (0.8.27's live phase: no migration changes a byte) + 0.8.10's
        run_live10 (pools + config read twice)
  AA    engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

_argv = list(sys.argv)
_RC = HK.run_compare   # 0.8.27's harness widens the compare for its quality file at import - this round changes no non-class file
_sp = importlib.util.spec_from_file_location("test_skyysacks_0_8_27", os.path.join(HERE, "test_skyysacks_0.8.27.py"))
T0827 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T0827)
sys.argv = _argv
HK.run_compare = _RC

VERSION = "0.8.28"
OLD_VERSION = "0.8.27"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySacks-%s.jar" % OLD_VERSION)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "packprep", "sacks")))
PKG = "com.skyy.sacks."
GEN = os.path.join(HERE, "build_skyysacks_%s.py" % VERSION)   # fixer: the generated script (static checks)
BETA = T0827.BETA
ACC_JAR = os.path.join(ROOT, "SkyyAccessories", "SkyyAccessories-0.5.31.jar")
GEAR_JAR = os.path.join(ROOT, "SkyyGear", "SkyyGear-0.3.38.jar")   # packprep: re-verified on the new pins (Gear 0.3.37 SET -> 0.3.38)
COLL_SCRIPT = os.path.join(ROOT, "SkyyCollections", "build_skyycollections_0.2.32.py")   # packprep: the SET pin
LIVE = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods")
SKYY = "d8ddde89-98b2-4739-983e-a39773d582b6"
EXPECT = {"CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "SkyySacksPlugin": ["~m setup"],
          "CraftPage": ["+m benchKey", "+m tierOk", "~m accTier", "~m benchRecipes"], "SackBridge": ["+f WHYM", "+m benchNeed", "+m whyCode", "+m whyPrune", "+m whySets", "~<clinit>", "~m call2", "~m dflt"],
          "SackFn": ["~m apply"]}
if "--expect-dump" in sys.argv:
    EXPECT = {}
SLOTS = ("Head", "Chest", "Hands", "Legs")


def props(path):
    d = {}
    for ln in open(path, encoding="latin-1"):
        ln = ln.strip()
        if ln and not ln.startswith("#") and "=" in ln:
            k, v = ln.split("=", 1)
            d[k] = v
    return d


def run_root(out, jar, scratch, _home):
    K = HK.Child(out)
    z = zipfile.ZipFile(GEAR_JAR)
    for s in SLOTS:
        r = json.loads(z.read("Server/Item/Recipes/SkyyGear/SkyyGear_Recipe_Armor_Bronze_%s.json" % s))
        br = r["BenchRequirement"]
        K.check(len(br) == 1 and br[0]["Id"] == "Armor_Bench" and br[0]["Type"] == "Crafting" and br[0].get("RequiredTierLevel", 0) <= 1,
                "ROOT: Bronze %s recipe = Armor_Bench tier %s (1)" % (s, br[0].get("RequiredTierLevel", "none")))
        K.check(r["KnowledgeRequired"] is True, "ROOT: Bronze %s recipe is KnowledgeRequired (SkyyCollections grants it)" % s)
    src = open(COLL_SCRIPT, encoding="utf8").read()
    K.check('GEARREC28 = {"Bronze": [("SkyyGear_Recipe_Armor_Bronze_%s"' in src and 'R28["recipe:" + _r] = [(_p, 5), (_q, 5)]' in src,
            "ROOT: SkyyCollections 0.2.32 (SET) grants the Bronze Mining recipes at BOTH input collections V")
    bag = props(os.path.join(LIVE, "Skyy_SkyyAccessories", "bags", SKYY + "-p3.properties"))
    K.check("Skyy_Accessory_Armor_Bench_T2" in bag.values(), "ROOT: Skyy's profile p3 has Armor Bench II equipped (%s)" % sorted(bag.values()))
    cnt = props(os.path.join(LIVE, "Skyy_SkyyCollections", "counts", SKYY + "-p3.properties"))
    paid = (int(cnt.get("_paid.Copper", 0)), int(cnt.get("_paid.Iron", 0)))
    K.check(max(paid) < 5, "ROOT: Skyy's Copper / Iron collections are tier %d / %d (< V) - Ore_Copper %s, Ore_Iron %s"
            % (paid[0], paid[1], cnt.get("Ore_Copper"), cnt.get("Ore_Iron")))
    K.save()


def run_bench(out, jar, scratch, _home):
    from jpype import JClass, JArray, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, ACC_JAR, B.JAVASSIST], verify=True)
    UUID = JClass("java.util.UUID")
    HM = JClass("java.util.HashMap")
    Sys = JClass("java.lang.System")
    CP, SFn, SB = JClass(PKG + "CraftPage"), JClass(PKG + "SackFn"), JClass(PKG + "SackBridge")
    AD = JClass("com.skyy.accessories.AccDefs")
    br = HM()
    Sys.getProperties().put("skyy.bridge", br)
    u = UUID.fromString(SKYY)

    def acc_of(bag):
        lst = AD.benchList(JArray(JString)(list(bag)))
        has = ",".join(str(lst.get(i)) for i in range(lst.size()))
        br.put("acc:has:" + str(u), has)
        return CP.accessories(None, u), has

    # Skyy's exact bag (NewBetaTest profile p3)
    bag = list(props(os.path.join(LIVE, "Skyy_SkyyAccessories", "bags", SKYY + "-p3.properties")).values())
    acc, has = acc_of(bag)
    K.eq(int(CP.accTier(acc, "Armor_Bench")), 2, "BENCH: Skyy's bag -> acc:has %s -> Armor_Bench tier 2" % has)
    K.check(bool(CP.tierOk(acc, "Armor_Bench", 0)) and bool(CP.tierOk(acc, "Armor_Bench", 1)) and bool(CP.tierOk(acc, "Armor_Bench", 2)),
            "BENCH: Skyy's bag -> a Bronze Helm recipe (Armor_Bench, tier none / 1) and a tier-2 one are allowed")
    K.check(not bool(CP.tierOk(acc, "Armor_Bench", 3)), "BENCH: Skyy's bag -> an Armor_Bench tier-3 recipe is refused")
    acc, _ = acc_of(["Skyy_Accessory_Armor_Bench_T1"])
    K.check(bool(CP.tierOk(acc, "Armor_Bench", 0)) and bool(CP.tierOk(acc, "Armor_Bench", 1)) and not bool(CP.tierOk(acc, "Armor_Bench", 2)),
            "BENCH: Armor Bench I -> tier 1 allowed, tier 2 refused")
    acc, _ = acc_of([])
    K.check(not bool(CP.tierOk(acc, "Armor_Bench", 1)), "BENCH: no accessory -> refused (the bench note)")
    acc, _ = acc_of(["Skyy_Talisman_Lantern_Uncommon", "Skyy_Accessory_Workbench_T3"])
    K.check(not bool(CP.tierOk(acc, "Armor_Bench", 1)) and bool(CP.tierOk(acc, "Workbench", 3)), "BENCH: another bench's accessory does not count")
    ids = [str(x) for x in AD.BENCH_IDS]
    mx = [int(x) for x in AD.BENCH_MAX]
    n = bad = 0
    camp = []
    for b, m in zip(ids, mx):
        if b == "Campfire":   # by design NOT a merged-tab bench (CraftPage.retiredBench): it only opens its own Campfire tab (campfireTier)
            for e in range(1, m + 1):
                acc, _ = acc_of(["Skyy_Accessory_Campfire_T%d" % e])
                camp.append(acc.isEmpty() and int(CP.campfireTier(u)) == e)
            continue
        for e in range(1, m + 1):
            acc, _ = acc_of(["Skyy_Accessory_%s_T%d" % (b, e)])
            for need in range(0, m + 1):
                n += 1
                want = max(need, 1) <= e
                if bool(CP.tierOk(acc, b, need)) != want or bool(CP.tierOk(acc, b.lower(), need)) != want:
                    bad += 1
                    K.check(False, "BENCH: %s T%d need %d -> %s" % (b, e, need, not want))
    K.check(bad == 0, "BENCH: every active bench x equipped tier x need tier: %d cases (%s), allowed exactly when need <= equipped"
            % (n, ", ".join("%s 1-%d" % (b, m) for b, m in zip(ids, mx) if b != "Campfire")))
    K.check(camp and all(camp), "BENCH: the Campfire accessory T1-T%d opens only the Campfire tab (campfireTier), never the merged tabs" % len(camp))
    acc, has = acc_of(["Skyy_Accessory_Omni"])
    K.check(all(bool(CP.tierOk(acc, b, m)) and not bool(CP.tierOk(acc, b, m + 1)) for b, m in zip(ids, mx) if b != "Campfire"),
            "BENCH: the Omni = every merged-tab bench at its max (%s)" % has)
    acc, has = acc_of(["Skyy_Accessory_Alchemybench_T4", "Skyy_Accessory_Cookingbench_T1"])
    K.check(acc.isEmpty(), "BENCH: retired accessories unlock nothing (acc:has '%s')" % has)
    f = SFn(18)
    K.check(f.apply(None) is None and f.apply(JArray(JClass("java.lang.Object"))([u])) is None and f.apply("x") is None
            and SB.whyCode(None, "x") is None, "BENCH: sacks:fn:craftWhy answers null on bad arguments")
    # fixer: the 1.5 s per-player cache of the two recipe sets (one /smithing page asks once per locked card)
    Obj, Lng, HS = JClass("java.lang.Object"), JClass("java.lang.Long"), JClass("java.util.HashSet")
    now = int(JClass("java.lang.System").currentTimeMillis())
    c1, c2 = HS(), JClass("java.util.TreeSet")()
    seed = JArray(Obj)([u, Lng.valueOf(now), c1, c2])
    SB.WHYM.clear()
    SB.WHYM.put(u, seed)
    u2 = JClass("java.util.UUID").randomUUID()
    d1, d2 = HS(), JClass("java.util.TreeSet")()
    seed2 = JArray(Obj)([u2, Lng.valueOf(now), d1, d2])
    SB.WHYM.put(u2, seed2)
    K.check(SB.whySets(u) is seed or SB.whySets(u).equals(seed), "BENCH: whySets: a fresh entry for the same player is reused (no recipe walk)")
    ok2 = True
    for _i in range(4):   # fixer 2: two players' calls interleave - each keeps its own entry (no thrash, no rebuild)
        ok2 = ok2 and SB.whySets(u)[2].equals(c1) and SB.whySets(u2)[2].equals(d1) and SB.whySets(u2)[3].equals(d2)
    K.check(ok2 and SB.WHYM.size() == 2, "BENCH: whySets: two players interleaving keep their own cached sets (per-player map)")
    hit = SB.whySets(u)
    K.check(hit[2] is c1 or hit[2].equals(c1), "BENCH: whySets returns the cached sets")
    K.check(SB.whyPrune(now) == 0 and SB.WHYM.size() == 2, "BENCH: whyPrune leaves a small map alone")
    for _i in range(40):
        SB.WHYM.put(JClass("java.util.UUID").randomUUID(), JArray(Obj)([u, Lng.valueOf(now - 5000), HS(), HS()]))
    SB.WHYM.put(JClass("java.util.UUID").randomUUID(), JArray(Obj)([u, Lng.valueOf(now + 60000), HS(), HS()]))
    pr = SB.whyPrune(now)
    K.check(pr == 41 and SB.WHYM.size() == 2 and SB.WHYM.containsKey(u), "BENCH: whyPrune past 32 drops the 41 stale / future entries, keeps the 2 fresh (%s, %d left)" % (pr, SB.WHYM.size()))
    SB.WHYM.clear()
    K.check(SB.WHYM.isEmpty(), "BENCH: cache cleared")
    src = open(GEN, encoding="utf8", newline="").read()
    wc = src[src.index("public static String whyCode("):]
    wc = wc[:wc.index("}\"\"\"")]
    K.check("whySets(u)" in wc and "craftSet(u)" not in wc and "collectionRecipes(u)" not in wc, "BENCH: whyCode reads the recipe sets only through whySets")
    ws = src[src.index("public static Object[] whySets("):]
    K.check("now - at < 1500L" in ws[:600] and "now >= at" in ws[:600], "BENCH: whySets keeps the sets 1.5 s (and never trusts a time in the future)")
    K.save()


def run_armb(out, jar, scratch, _home):
    from jpype import JClass, JArray, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, ACC_JAR, B.JAVASSIST], verify=True)
    CP = JClass(PKG + "CraftPage")
    AD = JClass("com.skyy.accessories.AccDefs")
    br = JClass("java.util.HashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    u = JClass("java.util.UUID").fromString(SKYY)
    az = zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip"))   # read-only (Python, no JVM)
    benches, armb = set(), []
    for n in az.namelist():
        if not (n.startswith("Server/Item/") and n.endswith(".json")):
            continue
        try:
            d = json.loads(az.read(n))
        except Exception:
            continue
        rs = [d.get("Recipe")] if isinstance(d.get("Recipe"), dict) else []
        rs += [x for x in (d.get("Recipes") or []) if isinstance(x, dict)] if isinstance(d.get("Recipes"), list) else []
        if isinstance(d.get("BenchRequirement"), list):
            rs.append(d)
        for r in rs:
            for b in r.get("BenchRequirement") or []:
                if isinstance(b, dict) and b.get("Id"):
                    benches.add(b["Id"])
                    if b["Id"] == "ArmorBench":
                        armb.append(n.rsplit("/", 1)[1][:-5])
    K.eq(sorted(armb), ["Utility_Helipack", "Utility_Leather_Backpack", "Utility_Leather_Medium_Backpack", "Utility_Leather_Quiver"],
         "ARMB: the 4 vanilla recipes with bench id ArmorBench")
    keys = {}
    for b in sorted(benches):
        keys.setdefault(str(CP.benchKey(b)), []).append(b)
    clash = sorted(v for v in keys.values() if len(v) > 1)
    K.eq(clash, [["ArmorBench", "Armor_Bench"]], "ARMB: benchKey joins only ArmorBench / Armor_Bench (%d bench ids in Assets.zip)" % len(benches))

    def acc_of(bag):
        lst = AD.benchList(JArray(JString)(list(bag)))
        br.put("acc:has:" + str(u), ",".join(str(lst.get(i)) for i in range(lst.size())))
        return CP.accessories(None, u)
    for t in (1, 2, 3):
        a = acc_of(["Skyy_Accessory_Armor_Bench_T%d" % t])
        K.check(int(CP.accTier(a, "ArmorBench")) == t and bool(CP.tierOk(a, "ArmorBench", 0)) and bool(CP.tierOk(a, "armorbench", 1)),
                "ARMB: Armor Bench %d charm -> ArmorBench tier %d, the Utility recipes (no tier) allowed" % (t, t))
    a = acc_of([])
    K.check(not bool(CP.tierOk(a, "ArmorBench", 0)), "ARMB: no charm -> ArmorBench refused")
    a = acc_of(["Skyy_Accessory_Weapon_Bench_T3", "Skyy_Accessory_Workbench_T3"])
    K.check(not bool(CP.tierOk(a, "ArmorBench", 0)) and bool(CP.tierOk(a, "Weapon_Bench", 3)), "ARMB: other benches' charms do not unlock ArmorBench")
    K.check(str(CP.benchKey(None)) == "" and str(CP.benchKey("Armor_Bench")) == "armorbench", "ARMB: benchKey")
    K.save()


if __name__ == "__main__":
    HK.run("SkyySacks", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, [],
           [("root", run_root), ("bench", run_bench), ("armb", run_armb), ("live", T0827.run_live27), ("live2", T0827.T0810.run_live10)],
           __file__, live=(BETA, "Skyy_SkyySacks"))
