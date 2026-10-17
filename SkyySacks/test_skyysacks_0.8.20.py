"""Harness for SkyySacks 0.8.20 (ZONE ALLOYS + FURNACE CHARM in the /craft Furnace; tools/sacks_0_8_20_patch.py).
Build first:
    python tools/sacks_0_8_20_patch.py && python SkyySacks/build_skyysacks_0.8.20.py

    python SkyySacks/test_skyysacks_0.8.20.py [--keep] [--dir <folder inside tools/dev/scratch/>]

Phases (fresh child JVMs, tools/harness_kit.py):
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.8.19 -> 0.8.20: exactly the planned members (EXPECT); non-class entries: manifest.json only
  ALLOY NEW, on the REAL asset stores (the 0.7.14 harness's V loader as the 0.8.8 FUEL phase uses it: the vanilla pack of Assets.zip store
        by store + the bench codecs) and a scratch pack with STANDALONE recipe files Server/Item/Recipes/SkyWynn/Alloy_*.json whose bench
        is Processing "SkyyAlloy" (B1's format; the spec's UNVERIFIED point):
          the files load into CraftingRecipe's store with no failure and no WARN / SEVERE; CraftPage.alloyRecipes() lists exactly them;
          alloyNeed = the ladder (Bronze 1) / RequiredTierLevel (3) / 5; a vanilla recipe 0; tableOnly (never instant); unitMs = 24 s
          (tier 2 Furnace 30 percent faster); acc:smelt parsing (absent / malformed / tier 0 = none, clamps, Eternal = T5 no fuel %,
          inactive profile key = none); the charm's time cut (charmMs); FUEL RATE: one 10 s unit at +45 percent burns exactly 14.5 s of
          fuel, without the charm 10 s; a fuel remainder that cannot pay a step still moves the unit (no stall) and then pauses OUT OF
          FUEL; ETERNAL FLAME: units finish with no fuel, loaded fuel stays, no charcoal, no fuel warning, "Eternal Flame" + "needs no
          fuel"; CHARM REMOVED MID-JOB: the rate changes from then on, the unit finishes, inputs / outputs conserved; the lock state
          (cTier) follows the bridge; CHARCOAL LEDGER: every Furnace charcoal byproduct is ledgered (= the charcoal in the output slot),
          the Tannery never, saved / loaded as <bench>.collDone (absent when empty); drainColl0: TRUE drains (at most 256 per call),
          FALSE / null / no function / an exception keep it; the alloy unit pays Smithing XP like any Furnace unit
  SUP / TG / KEYS / D (live)   the 0.8.18 harness's phases on this jar - unchanged behaviour
  AA    engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

_orig_compare = HK.run_compare
_argv = list(sys.argv)
_sp = importlib.util.spec_from_file_location("test_skyysacks_0_8_19", os.path.join(HERE, "test_skyysacks_0.8.19.py"))
T19 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T19)
sys.argv = list(_argv)
_sp8 = importlib.util.spec_from_file_location("test_skyysacks_0_8_8", os.path.join(HERE, "test_skyysacks_0.8.8.py"))
T088 = importlib.util.module_from_spec(_sp8)
_sp8.loader.exec_module(T088)
sys.argv = _argv
HK.run_compare = _orig_compare
T18 = T19.T18

VERSION = "0.8.20"
OLD_VERSION = "0.8.19"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySacks-%s.jar" % OLD_VERSION)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "ores-b3", "sacks")))
PKG = "com.skyy.sacks."
EXPECT = {
    "ProcBench": ["+f key", "+f cTier", "+f cTime", "+f cFuel", "+f cEternal", "+f collDone", "+f COLL_CAP", "+f ALLOY_BENCH",
                  "+f ALLOY_IDS", "+f ALLOY_TIER", "+f ALLOY_WORD", "+f waitFrom", "+m holdFor", "~m queueMs", "+m smelt", "+m charmMs", "+m alloyTierOf", "+m alloyNeed", "+m advanceC",
                  "+m collList", "+m takeColl", "~m advance", "~m burnOne", "~m describe", "~m fuelWarnOnce", "~m toProps",
                  "~m fromProps", "~c ", "~<clinit>"],
    "ProcStore": ["~m load", "~m of"],
    "ProcTask": ["+f COLL_CALL", "+f COLLWARN", "+f COLLNEXT", "+m drainColl0", "+m drainColl", "~m run", "~<clinit>"],
    "CraftPage": ["+m alloyRecipes", "~m recipesFor", "~m procQueue", "~m buildProc"],
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"],   # the version text
    "SkyySacksPlugin": ["~m setup"],   # the ready line
    # the shared tables read at build time: tools/tier_tags.py (B1: the new ores / ingots / alloys sort by tier) and tools/skyyench.py
    # (B4: Enchanted Lead / Chromium / Slag / Titanium Ingot + Enchanted Charcoal home in the Void)
    "RecipeCmp": ["~<clinit>"], "SackDefs": ["~m enchCat"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = []
UUID0 = "6f1c2d3e-4b5a-4c7d-8e9f-0a1b2c3d4e5f"


def _recipe(inputs, out, secs, tier=None):
    br = {"Type": "Processing", "Id": "SkyyAlloy"}
    if tier is not None:
        br["RequiredTierLevel"] = tier
    return {"Input": [{"ItemId": i, "Quantity": 1} for i in inputs], "PrimaryOutput": {"ItemId": out, "Quantity": 1},
            "Output": [{"ItemId": out, "Quantity": 1}], "BenchRequirement": [br], "TimeSeconds": secs}


def run_alloy(out, jar, scratch, home):
    import serverjar
    K = HK.Child(out)
    os.makedirs(scratch, exist_ok=True)
    assets = serverjar.assets_zip()
    fake = os.path.join(scratch, "fakealloys.zip")
    with zipfile.ZipFile(fake, "w") as z:
        z.writestr("manifest.json", json.dumps({"Group": "Test", "Name": "FakeAlloys", "Version": "1.0.0"}))
        # B1's shape: 1 + 1 -> 1, time = both smelts added (Copper 10 + Iron 14); the two test files use vanilla outputs not on the ladder
        z.writestr("Server/Item/Recipes/SkyWynn/Alloy_Bronze.json", json.dumps(_recipe(["Ingredient_Bar_Copper", "Ingredient_Bar_Iron"], "Ingredient_Bar_Bronze", 24), indent=1))
        # Electrum (Skyy: "Gold + Silver, unlocked at the Bronze furnace tier") - B1's final output id is read at runtime (word match)
        z.writestr("Server/Item/Recipes/SkyWynn/Alloy_Electrum.json", json.dumps(_recipe(["Ingredient_Bar_Gold", "Ingredient_Bar_Silver"], "Ingredient_Bar_Electrum_SkyWynn", 24), indent=1))
        z.writestr("Server/Item/Recipes/SkyWynn/Alloy_TestT3.json", json.dumps(_recipe(["Ingredient_Bar_Cobalt", "Ingredient_Bar_Iron"], "Ingredient_Bar_Thorium", 36, 3), indent=1))
        z.writestr("Server/Item/Recipes/SkyWynn/Alloy_TestNoTier.json", json.dumps(_recipe(["Ingredient_Bar_Mithril", "Ingredient_Bar_Iron"], "Ingredient_Bar_Adamantite", 60), indent=1))
    src = open(T088.T0714, encoding="utf8").read()
    a = src.index("def run_v():")
    b = src.index('    ITEM = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")', a)
    t0 = "    t0 = time.time()\n"
    body = src[a:b].replace("def run_v():", "def run_alloy_fixture():", 1)
    assert body.count(t0) == 1
    body = body.replace(t0, T088.FUEL_PRE + t0, 1) + T088.FUEL_TAIL
    body = body.replace("classpath=[B.SERVER_JAR, B.JAVASSIST]", "classpath=[B.SERVER_JAR, JAR, B.JAVASSIST]", 1)
    assert "classpath=[B.SERVER_JAR, JAR, B.JAVASSIST]" in body
    ns = {"__file__": T088.T0714, "__name__": "t0714"}
    exec(compile(src[:src.index("def run():")], T088.T0714, "exec"), ns)
    ns.update(SCRATCH=os.path.join(scratch, "v"), ASSETS_ZIP=assets, JAR=jar, FAKE_PACK=fake, _FUEL=lambda L: alloy_cases(K, L))
    os.makedirs(ns["SCRATCH"], exist_ok=True)
    exec(compile(body, T088.T0714 + " (V loader slice)", "exec"), ns)
    ns["run_alloy_fixture"]()
    for f in ns["FAILS"]:
        K.check(False, "ALLOY loader: " + f)
    K.save()


def alloy_cases(K, L):
    from jpype import JClass, JString, JImplements, JOverride, JLong
    K.check(not L["_fail"], "ALLOY: the standalone SkyyAlloy recipe files load into the real stores: failed %s" % L["_fail"])
    bad = [m for lv, m in L["_rec"] if lv in ("WARNING", "SEVERE")]
    K.check(not bad, "ALLOY: loading them wrote no WARN / SEVERE line (an unknown Processing bench id is accepted): %s" % bad[:3])
    CRR = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
    PB = JClass(PKG + "ProcBench")
    CP = JClass(PKG + "CraftPage")
    PT = JClass(PKG + "ProcTask")
    Pool = JClass(PKG + "SackPool")
    Pool.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySacks")
    UUID = JClass("java.util.UUID")
    CHM = JClass("java.util.concurrent.ConcurrentHashMap")
    Props = JClass("java.util.Properties")
    br = CHM()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    u = UUID.fromString(UUID0)
    k = str(u)

    # ---- 1. the recipes
    rb = CRR.getAssetMap().getAsset(JString("Alloy_Bronze"))
    K.check(rb is not None, "ALLOY: Alloy_Bronze is in CraftingRecipe's asset map under its file name")
    if rb is None:
        return
    req = rb.getBenchRequirement()
    K.check(len(req) == 1 and str(req[0].id) == "SkyyAlloy" and str(req[0].type) == "Processing", "ALLOY: its bench = Processing SkyyAlloy")
    ids = sorted(str(x) for x in CP.alloyRecipes())
    K.eq(ids, ["Alloy_Bronze", "Alloy_Electrum", "Alloy_TestNoTier", "Alloy_TestT3"], "ALLOY: CraftPage.alloyRecipes() = exactly the SkyyAlloy files")
    rel = CRR.getAssetMap().getAsset(JString("Alloy_Electrum"))
    K.check(rel is not None and int(PB.alloyNeed(rel)) == 1, "ALLOY: Electrum (Gold + Silver) unlocks at Furnace Charm T1 like Bronze")
    K.eq([int(PB.alloyTierOf(JString(i))) for i in ("Ingredient_Bar_Electrum", "Ingredient_Bar_Electrum_Other", "Ingredient_Bar_Lumen_X", "Ingredient_Bar_Gold", "Plant_Electrum")],
         [1, 1, 5, 0, 0], "ALLOY: the metal word of the output id finds the tier whatever B1's final suffix is")
    rt3 = CRR.getAssetMap().getAsset(JString("Alloy_TestT3"))
    rnt = CRR.getAssetMap().getAsset(JString("Alloy_TestNoTier"))
    K.eq([int(PB.alloyNeed(rb)), int(PB.alloyNeed(rt3)), int(PB.alloyNeed(rnt))], [1, 3, 5], "ALLOY: alloyNeed = ladder / RequiredTierLevel / 5")
    van = None
    for e in CRR.getAssetMap().getAssetMap().entrySet():
        if not str(e.getKey()).startswith("Alloy_"):
            van = e.getValue()
            break
    K.check(van is not None and int(PB.alloyNeed(van)) == 0, "ALLOY: a vanilla recipe is no alloy (%s)" % (van and van.getId()))
    K.eq([int(PB.alloyTierOf(JString(i))) for i in ("Ingredient_Bar_Bronze", "Ingredient_Bar_Dusk_SkyWynn", "Ingredient_Bar_Azurvane_SkyWynn",
          "Ingredient_Bar_Cinder_SkyWynn", "Ingredient_Bar_Lumen_SkyWynn", "Ingredient_Bar_Iron")], [1, 2, 3, 4, 5, 0], "ALLOY: the ladder ids (spec 3)")
    K.check(bool(CP.tableOnly(rb)), "ALLOY: tableOnly(alloy) - never crafted instantly (instant tabs, search, sacks:fn craft)")
    K.eq(int(PB.unitMs(rb, JString("Furnace"), 1)), 24000, "ALLOY: unit time 24 s at Furnace I")
    K.eq(int(PB.unitMs(rb, JString("Furnace"), 2)), 16800, "ALLOY: Furnace II (30 percent faster, the vanilla tier) 16.8 s")

    # ---- 2. acc:smelt
    def sm(key):
        return [int(x) for x in PB.smelt(JString(key))]
    K.eq(sm(k), [0, 0, 0, 0], "CHARM: no acc:smelt key = none (0.8.19)")
    for v, want in (("3|30|45|0|K", [3, 30, 45, 0]), ("0|0|0|0|K", [0, 0, 0, 0]), ("x|y", [0, 0, 0, 0]), ("1|a|2|0|K", [0, 0, 0, 0]),
                    ("9|99|5000|0|K", [5, 90, 1000, 0]), ("2|20|30|1|K", [5, 20, 0, 1]), (" 1 | 10 | 15 | 0 | K ", [1, 10, 15, 0]),
                    ("3|30|45|0", [0, 0, 0, 0]), ("3|30|45|0|K-p2", [0, 0, 0, 0]), ("3|30|45|0|", [0, 0, 0, 0])):
        v = v.replace("K", k)
        br.put("acc:smelt:" + k, JString(v))
        K.eq(sm(k), want, "CHARM: acc:smelt %r (4 fields / another profile key = none)" % v)
    br.put("acc:smelt:" + k, JString("3|30|45|0|" + k))
    K.eq(sm(k + "-p2"), [0, 0, 0, 0], "CHARM: an inactive profile key gets no charm (no SkyyProfiles = profile 1)")
    K.eq(sm("not-a-key"), [0, 0, 0, 0], "CHARM: a bad key = none")

    @JImplements("java.util.function.Function")
    class KeyFn(object):
        def __init__(self, v):
            self.v = v

        @JOverride
        def apply(self, x):
            return JString(self.v)
    br.put("profile:fn:key", KeyFn(k + "-p2"))
    K.check(sm(k) == [0, 0, 0, 0] and sm(k + "-p2") == [0, 0, 0, 0], "CHARM: switched to profile 2, the value still names profile 1 - nobody gets it (the 5 s window)")
    br.put("acc:smelt:" + k, JString("3|30|45|0|" + k + "-p2"))
    K.check(sm(k) == [0, 0, 0, 0] and sm(k + "-p2") == [3, 30, 45, 0], "CHARM: republished for profile 2 - only profile 2's bench gets it")
    br.put("acc:smelt:" + k, JString("3|30|45|0|" + k))
    br.remove("profile:fn:key")
    K.eq([int(PB.charmMs(24000, 30)), int(PB.charmMs(24000, 0)), int(PB.charmMs(10000, 50)), int(PB.charmMs(0, 30))], [16800, 24000, 5000, 0],
         "CHARM: charmMs (time cut, fixed in the job)")

    IN = "Ingredient_Bar_Copper*1;Ingredient_Bar_Iron*1"
    T = 5000000

    def bench(key, fuel_ms, units=1, unit=10000, name="Furnace"):
        pb = PB(JString(name))
        pb.key = JString(key) if key else None
        pb.addJob(JString("Alloy_Bronze"), units, unit, JString(IN), T)
        pb.fuelMs = fuel_ms
        return pb

    def outd(pb):
        return dict((str(e[0]), int(e[1])) for e in pb.outList())

    # ---- 3. fuel rate
    br.put("acc:smelt:" + k, JString("3|30|45|0|" + k))
    p1 = bench(k, 10150)
    K.check(bool(p1.needsFuel), "FUEL: the Furnace needs fuel (real Bench_Furnace config)")
    d1 = int(p1.advance(T + 7000))
    K.check(d1 == 1 and int(p1.fuelMs) == 0 and outd(p1) == {"Ingredient_Bar_Bronze": 1} and int(p1.queued()) == 0,
            "FUEL: T3 charm - a 10 s (base) unit takes 7 s live and burns exactly 7 x 1.45 = 10.15 s of fuel, 1 Bronze: done %d fuelMs %d out %s" % (d1, int(p1.fuelMs), outd(p1)))
    p9 = bench(k, 10 ** 6, units=2)
    p9.advance(T)
    K.check(int(p9.queueMs()) == 14000 and int(p9.queue.get(0).unitMs) == 10000 and "7s left" in str(p9.describe(1, True)[1]),
            "TIME: the job keeps the base 10 s, the page shows the live 7 s per unit (queue %d ms): %s" % (int(p9.queueMs()), p9.describe(1, True)[1]))
    K.check(int(p1.cTier) == 3 and int(p1.cTime) == 30 and int(p1.cFuel) == 45 and not bool(p1.cEternal), "FUEL: the advance kept the charm state (lock tier 3)")
    xp = dict((str(e[0]), int(e[1])) for e in p1.xpList())
    K.eq(xp, {"Alloy_Bronze": 1}, "FUEL: the alloy unit pays Smithing XP like any Furnace unit (xpDone)")
    p0 = bench(None, 14500)
    p0.advance(T + 10000)
    K.check(int(p0.fuelMs) == 4500 and outd(p0) == {"Ingredient_Bar_Bronze": 1} and int(p0.cTier) == 0,
            "FUEL: control - no owner key = 0.8.19: 10 s of fuel, 4.5 s left (%d)" % int(p0.fuelMs))
    pt = bench(k, 14500, name="Tannery")
    pt.advance(T + 10000)
    K.check(int(pt.cTier) == 0 and int(pt.cFuel) == 0, "FUEL: the Tannery never reads the charm")
    # a remainder that cannot pay a step: 1 ms of fuel at +75 percent still moves the unit 1 ms, then OUT OF FUEL (nothing lost)
    br.put("acc:smelt:" + k, JString("1|10|75|0" + "|" + k))
    p2 = bench(k, 1, unit=6)
    d2 = int(p2.advance(T + 5))
    ds = [str(x) for x in p2.describe(1, True)]
    K.check(d2 == 0 and int(p2.progress) == 1 and int(p2.fuelMs) == 0 and int(p2.queued()) == 1 and outd(p2) == {},
            "FUEL: 1 ms left at +75 percent - progress 1 ms, fuel 0, unit kept: done %d progress %d" % (d2, int(p2.progress)))
    K.check("OUT OF FUEL" in ds[1] and "Furnace Charm T1 10 percent faster" in ds[0] and "burns 75 percent faster" in ds[0],
            "FUEL: the status names the charm and the burn rate, then OUT OF FUEL: %r / %r" % (ds[0], ds[1]))
    for c in ",:;{}\"":
        K.check(c not in ds[0] and c not in ds[1], "FUEL: the status line holds no %r (UI text rule)" % c)
    # big replay: many units over a long span at +60 percent, fuel from real items - fuel ms used = processed ms x 1.6 (within 1 ms per step)
    br.put("acc:smelt:" + k, JString("4|40|60|0" + "|" + k))
    fl = [str(x) for x in PB.fuels()]
    fid = "Wood_Oak_Trunk" if "Wood_Oak_Trunk" in fl else fl[0]
    fq = int(round(float(PB.fuelQuality(JString(fid))) * 1000))
    p3 = bench(k, 0, units=7, unit=3000)
    p3.addFuel(JString(fid), 40)
    tot0 = int(p3.fuelTotalMs())
    d3 = int(p3.advance(T + 10 ** 7))
    used = tot0 - int(p3.fuelTotalMs())
    o3 = outd(p3)
    K.check(d3 == 7 and o3.get("Ingredient_Bar_Bronze") == 7 and abs(used - 7 * 1800 * 1.6) <= 30,
            "FUEL: 7 x 3 s (1.8 s live at -40 percent) at +60 percent burn %d ms of fuel (want %d) - 7 Bronze (%s; fuel %s %d ms each)" % (used, 7 * 1800 * 1.6, o3, fid, fq))

    # ---- 4. Eternal Flame
    br.put("acc:smelt:" + k, JString("5|50|0|1" + "|" + k))
    p4 = bench(k, 0, units=3, unit=5000)
    p4.addFuel(JString(fid), 5)
    d4 = int(p4.advance(T + 15000))
    ds4 = [str(x) for x in p4.describe(1, True)]
    K.check(d4 == 3 and int(p4.fuelCount()) == 5 and int(p4.fuelMs) == 0 and outd(p4) == {"Ingredient_Bar_Bronze": 3} and p4.collList().isEmpty(),
            "ETERNAL: 3 units finish, the 5 loaded fuel stay, no charcoal, nothing ledgered: done %d fuel %d out %s" % (d4, int(p4.fuelCount()), outd(p4)))
    K.check("Eternal Flame 50 percent faster" in ds4[0] and "needs no fuel" in ds4[0] and int(p4.cTier) == 5 and bool(p4.cEternal),
            "ETERNAL: status %r, lock tier 5" % ds4[0])
    p4b = bench(k, 0, units=2, unit=5000)
    K.check(int(p4b.advance(T + 2500)) == 1 and int(p4b.queued()) == 1 and not bool(p4b.fuelWarnOnce()) and "OUT OF FUEL" not in str(p4b.describe(1, True)[1]),
            "ETERNAL: no fuel at all - still smelts, never OUT OF FUEL, no fuel warning")
    n4 = int(p4.unloadFuel())
    K.check(n4 == 5 and outd(p4).get(fid) == 5, "ETERNAL: the unused fuel unloads into the output slot (nothing lost)")

    # ---- 5. charm removed mid-job (and put back): the rate follows the bridge, the unit finishes, items conserved
    br.put("acc:smelt:" + k, JString("3|30|45|0|" + k))
    p5 = bench(k, 20000)
    p5.advance(T + 5000)
    f_a = int(p5.fuelMs)
    br.remove("acc:smelt:" + k)
    d5a = int(p5.advance(T + 7000))
    K.check(d5a == 0 and int(p5.progress) == 7000, "MIDJOB: charm gone - the unit that would finish at 7 s with it needs the full 10 s now (done %d, progress %d)" % (d5a, int(p5.progress)))
    d5 = int(p5.advance(T + 10000))
    f_b = int(p5.fuelMs)
    K.check(f_a == 20000 - 7250 and f_b == f_a - 5000 and d5 == 1 and outd(p5) == {"Ingredient_Bar_Bronze": 1} and int(p5.cTier) == 0,
            "MIDJOB: 5 s at +45 percent (7.25 s) then the charm is gone - 5 s at the plain rate, the unit finishes: %d -> %d, out %s" % (f_a, f_b, outd(p5)))
    K.check(int(p5.cTier) < int(PB.alloyNeed(rb)), "MIDJOB: with the charm gone the lock is back (cTier 0 < Bronze 1) - procQueue refuses new alloy jobs")
    # cancel after a partial unit: the inputs come back exactly (the charm changes no item)
    br.put("acc:smelt:" + k, JString("2|20|30|0" + "|" + k))
    p6 = bench(k, 3000, units=4)
    p6.advance(T + 2000)
    n6 = int(p6.cancel())
    K.check(n6 == 4 and outd(p6) == {"Ingredient_Bar_Copper": 4, "Ingredient_Bar_Iron": 4},
            "MIDJOB: cancel mid-unit returns every unit's inputs: %s" % outd(p6))

    # ---- 5b. join / restart: the replay waits for acc:smelt while the player is online (at most 10 s)
    ph = PB(JString("Furnace"))
    K.check(bool(ph.holdFor(True, True, T)) and bool(ph.holdFor(True, True, T + 9999)) and not bool(ph.holdFor(True, True, T + 10000)),
            "HOLD: acc:smelt absent + online - held for 10 s, then replays (Accessories missing = 0.8.19 after 10 s)")
    K.check(not bool(ph.holdFor(False, True, T + 10001)) and int(ph.waitFrom) == 0 and bool(ph.holdFor(True, True, T + 20000)),
            "HOLD: once published the wait resets (a later gap waits again)")
    K.check(not bool(ph.holdFor(True, False, T)) and int(ph.waitFrom) == 0, "HOLD: offline (no Universe player) - never held")

    # ---- 6. the Charcoal ledger
    br.remove("acc:smelt:" + k)
    p7 = bench(k, 0, units=40, unit=10000)
    p7.addFuel(JString(fid), 60)
    p7.advance(T + 10 ** 8)
    o7 = outd(p7)
    led = dict((str(e[0]), int(e[1])) for e in p7.collList())
    ch = o7.get("Ingredient_Charcoal", 0)
    K.check(ch > 0 and led == {"Ingredient_Charcoal": ch}, "CHARCOAL: the ledger = the charcoal the Furnace put in the output slot (%d): %s" % (ch, led))
    pt2 = bench(k, 0, units=5, name="Tannery")
    pt2.addFuel(JString(fid), 20)
    pt2.advance(T + 10 ** 8)
    K.check(pt2.collList().isEmpty(), "CHARCOAL: never for the Tannery")
    pr = Props()
    p7.toProps(pr)
    K.eq(str(pr.getProperty("Furnace.collDone")), "Ingredient_Charcoal*%d" % ch, "CHARCOAL: saved as Furnace.collDone")
    p7b = PB(JString("Furnace"))
    p7b.fromProps(pr)
    K.eq(dict((str(e[0]), int(e[1])) for e in p7b.collList()), led, "CHARCOAL: loaded back")
    pr2 = Props()
    p0.toProps(pr2)
    K.check(pr2.getProperty("Furnace.collDone") is None and pr2.getProperty("Furnace.xpDone") is not None, "CHARCOAL: an empty ledger writes no line")

    calls = []

    @JImplements("java.util.function.Function")
    class AddFn(object):
        def __init__(self, ans):
            self.ans = ans

        @JOverride
        def apply(self, a):
            calls.append([str(a[0]), str(a[1]), int(a[2]), str(a[3]), str(a[4])])
            if self.ans == "boom":
                raise RuntimeError("boom")
            return self.ans
    Bool = JClass("java.lang.Boolean")
    for ans, label in ((Bool.FALSE, "FALSE"), (None, "null"), ("boom", "an exception")):
        calls[:] = []
        r = int(PT.drainColl0(AddFn(ans), u, JString(k), p7))
        K.check(r == -1 and dict((str(e[0]), int(e[1])) for e in p7.collList()) == led, "CHARCOAL: coll:fn:add answers %s - ledger kept (%d)" % (label, r))
    K.check(int(PT.drainColl0(None, u, JString(k), p7)) == -1, "CHARCOAL: no coll:fn:add (SkyyCollections missing / older) - kept")
    calls[:] = []
    r = int(PT.drainColl0(AddFn(Bool.TRUE), u, JString(k), p7))
    K.check(r == min(ch, 256) and calls and calls[0] == [k, "Ingredient_Charcoal", min(ch, 256), "sacks:furnace", k],
            "CHARCOAL: TRUE - credited %d with {uuid, Ingredient_Charcoal, qty, sacks:furnace, pkey}: %s" % (r, calls[:1]))
    p8 = PB(JString("Furnace"))
    pr3 = Props()
    pr3.setProperty("Furnace.collDone", "Ingredient_Charcoal*600")
    p8.fromProps(pr3)
    calls[:] = []
    r8 = int(PT.drainColl0(AddFn(Bool.TRUE), u, JString(k), p8))
    left = dict((str(e[0]), int(e[1])) for e in p8.collList())
    K.check(r8 == 256 and left == {"Ingredient_Charcoal": 344} and calls[0][2] == 256, "CHARCOAL: at most 256 per call (%d, left %s)" % (r8, left))


def run_sup(out, jar, scratch, home):
    T18.run_sup(out, jar, scratch, home)


if __name__ == "__main__":
    HK.run("SkyySacks", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("alloy", run_alloy), ("sup", run_sup), ("tg", T18.T16.run_tg), ("keys", T18.T17.run_keys), ("live", T18.T0810.run_live10)],
           __file__, live=(T18.T16.T15.BETA, "Skyy_SkyySacks"))
