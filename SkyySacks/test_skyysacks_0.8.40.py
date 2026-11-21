"""Harness for SkyySacks 0.8.40 (round inv7 - tools/sacks_0_8_40_patch.py: the Furnace / Tannery bridges for SkyyMenu 0.3.56's inventory panel).
Build first:
    python tools/sacks_0_8_40_patch.py && python SkyySacks/build_skyysacks_0.8.40.py

    python SkyySacks/test_skyysacks_0.8.40.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  A / C   verify (-Xverify:all) + compare 0.8.39 -> 0.8.40 (SackBridge: the furnace methods + FRECIPES; SackFn.apply; the version lines only)
  P40     EXECUTED on the 0.8.0 Void stand-ins with the REAL SackPool / VoidStore / BagMirror / CraftPage / ProcStore / ProcBench / SackBridge /
          SackFn: every 0.8.39 P39 (and 0.8.38 P38) case first (regression), then
          LIST    sacks:fn:furnList: the header (bench, tier, queue used / cap, fuel, ready, the profile TOKEN), the recipe rows (can make =
                  inventory + Void), the selected recipe's inputs, the search, "off" without the accessory and nothing in the bench,
                  "sum" for Right now, no player on this thread = null
          QUEUE   sacks:fn:furn queue 10: exactly 10 ore leave (inventory first, then the Void), 10 units queued; ANOTHER profile's token /
                  no token = refused, NOTHING moves; a recipe not in the list refused; no accessory refused; bad amount refused; all =
                  every ore up to the queue room (no ore lost or doubled); a throw inside = "-", the pool saved, no ore lost
          COLLECT ready items into the inventory exactly ONCE (a second Collect = nothing, counts unchanged = the double click); a FULL
                  inventory = refused, everything stays in the bench; a nearly full one = what fits, the rest stays; a stale token =
                  refused, nothing moves
          CANCEL  every unfinished unit's ore back (to the output slot, then collected): ore totals restored exactly
          FUEL    load 20 of a fuel (counted, inventory first); not a fuel refused; a typed word refused; more than you own = what you own;
                  Unload = the unburned fuel back; the Tannery burns no fuel = refused
  F37 / S36 / BC36 / ALL35   the 0.8.37, 0.8.36 and 0.8.35 cases on THIS jar (regression)
  D       start twice on a scratch COPY of NewBetaTest's Skyy_SkyySacks: no migration, no byte changed
Exit code 1 on any failure.
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

_argv = list(sys.argv)
_RC = HK.run_compare
_sp = importlib.util.spec_from_file_location("test_skyysacks_0_8_39", os.path.join(HERE, "test_skyysacks_0.8.39.py"))
T39 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T39)
sys.argv = _argv
HK.run_compare = _RC
T38, T37 = T39.T38, T39.T37
T36, T35, T089, T30, BETA = T37.T36, T37.T35, T37.T089, T37.T30, T37.BETA

VERSION = "0.8.40"
OLD_VERSION = "0.8.39"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySacks-%s.jar" % OLD_VERSION)
T30.OLD_JAR = OLD_JAR
T39.OLD_JAR = OLD_JAR
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "inv7", "sacks")))
PKG = "com.skyy.sacks."
EXPECT = {"SkyySacksPlugin": ["~m setup"], "CfgRows": ["~m header"], "CfgFn": ["~m opExport"],
          "SackBridge": ["+f FRECIPES", "+m benchOf", "+m capFirst", "+m fclean", "+m furnAct", "+m furnList", "+m furnRS", "+m furnRecipes", "+m furnSum"],
          "SackFn": ["~m apply"]}
if "--expect-dump" in sys.argv:
    EXPECT = {}
OUT40 = "Skyy_Test_Bar40"
COP = "Ore_Copper"
OAK = "Wood_Oak_Trunk"
FILL = "Rock_Stone_Cobble"


def cases40(K, L, scratch):
    T39.cases39(K, L, scratch)   # every 0.8.39 (and 0.8.38) pocket case on this jar first
    import time
    from jpype import JClass, JString, JArray, JInt, JFloat, JImplements, JOverride
    Defs, Pool = L["Defs"], L["Pool"]
    fresh, write_pool, player, drain, custom_item, inv_counts, pc = (L[n] for n in ("fresh", "write_pool", "player", "drain", "custom_item", "inv_counts", "pc"))
    UUID, TPlayers, Bridge, bridge, jfield, ItemC = L["UUID"], L["TPlayers"], L["Bridge"], L["bridge"], L["jfield"], L["ItemC"]
    VS = L["VS"]
    J = lambda n: JClass(PKG + n)
    Fn, PB, PS, CP = J("SackFn"), J("ProcBench"), J("ProcStore"), J("CraftPage")
    Obj = JClass("java.lang.Object")
    MQ = JClass("com.hypixel.hytale.server.core.inventory.MaterialQuantity")
    CRc = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
    BR = JClass("com.hypixel.hytale.protocol.BenchRequirement")
    IRT = JClass("com.hypixel.hytale.protocol.ItemResourceType")
    Paths, AL = JClass("java.nio.file.Paths"), JClass("java.util.ArrayList")
    custom_item(OUT40, 100)
    custom_item(COP, 100)
    custom_item(FILL, 25)
    oak = custom_item(OAK, 100)
    jfield(ItemC.class_, "resourceTypes").set(oak, JArray(IRT)([IRT(JString("Fuel"), JInt(1))]))
    fq_ = jfield(ItemC.class_, "fuelQuality")
    if str(fq_.getType().getName()) == "float":
        fq_.setFloat(oak, 4.0)
    else:
        fq_.setDouble(oak, 4.0)
    K.check(float(PB.fuelQuality(JString(OAK))) > 0.0 and float(PB.fuelQuality(JString(COP))) == 0.0, "P40 stand-ins: Oak Log burns, Copper Ore does not")
    PB.FUELS = AL([JString(OAK)])

    def recipe(rid, ins, out=OUT40, qty=1):
        mi = JArray(MQ)([MQ(JString(i), None, None, JInt(q), None) for i, q in ins])
        po = MQ(JString(out), None, None, JInt(qty), None)
        r = CRc(mi, po, JArray(MQ)([po]), JInt(1), JArray(BR)(0), JFloat(30.0), False, JInt(0))
        jfield(CRc.class_, "id").set(r, JString(rid))
        return r
    rCu = recipe("Skyy_Test_Cu40", [(COP, 1)])
    RECS = {"Furnace": [rCu], "Tannery": []}
    THROW = {"on": False}

    @JImplements("java.util.function.Function")
    class Recs(object):
        @JOverride
        def apply(self, b):
            if THROW["on"]:
                raise RuntimeError("harness: the recipe list throws")
            return AL(RECS.get(str(b), []))

    base = os.path.join(scratch, "p40")
    d = os.path.join(scratch, "p40proc")
    os.makedirs(d, exist_ok=True)
    U = UUID.fromString("00000000-0000-0000-0000-0000000f0840")
    k = str(U)

    def call(mode, *a):
        r = Fn(mode).apply(JArray(Obj)([JString(x) if isinstance(x, str) else x for x in a]))
        drain()
        return None if r is None else str(r)

    def mk(pool, storage=(), hotbar=(), backpack=()):
        drain()
        fresh(base)
        PS.DIR = Paths.get(d)
        PS.STATES.clear()
        PS.BROKEN.clear()
        bridge.put(JString("coll:recipes:" + k), JString(""))
        write_pool(os.path.join(base, "pools"), k, pool)
        VS.st(k).first = 1
        p_ = player(storage=list(storage), hotbar=list(hotbar), backpack=list(backpack))
        TPlayers.P = p_
        return p_

    def ore(p_):
        return inv_counts(p_).get(COP, 0) + pc(k).get(COP, 0)

    def bench(b_="Furnace"):
        return PS.of(JString(k), JString(b_))
    try:
        Bridge.PLAYERS = TPlayers()
        Bridge.FRECIPES = Recs()
        bridge.put(JString("acc:has:" + k), JString("Skyy_Accessory_Furnace_T1,Skyy_Accessory_Tannery_T1"))
        # ---- LIST
        p = mk({COP: 70}, storage=[(COP, 30)])
        r = call(23, U, "Furnace", "", "")
        h = r.split("\n")[0].split("|") if r else []
        K.check(r is not None and h[:3] == ["ok", "Furnace", "1"] and len(h) == 16 and h[15] == k and h[6] == "0" and h[7] == str(int(PB.QUEUE_CAP)),
                "P40 LIST the header: bench, tier 1, nothing queued / the cap, the profile TOKEN last (%s)" % (h,))
        rows = [l_ for l_ in r.split("\n") if l_.startswith("r|")]
        K.check(rows and rows[0].split("|")[1:5] == ["Skyy_Test_Cu40", OUT40, "1", "100"], "P40 LIST the recipe row: can make 100 = 30 inventory + 70 Void (%s)" % rows)
        r = call(23, U, "Furnace", "Skyy_Test_Cu40", "")
        K.check([l_ for l_ in r.split("\n") if l_.startswith("i|")] == ["i|%s|%s|100|1" % (COP, str(PB.itemName(JString(COP))))], "P40 LIST the selected recipe's input: have 100 / 1 per unit")
        r = call(23, U, "Furnace", "", "zzz")
        K.check(not [l_ for l_ in r.split("\n") if l_.startswith("r|")], "P40 LIST a search that matches nothing = no rows")
        bridge.put(JString("acc:has:" + k), JString(""))
        K.check(str(call(23, U, "Furnace", "", "")).startswith("off|Equip a Furnace accessory"), "P40 LIST no accessory and nothing in the bench = off")
        bridge.put(JString("acc:has:" + k), JString("Skyy_Accessory_Furnace_T1,Skyy_Accessory_Tannery_T1"))
        K.check(str(call(23, U, "Nope", "", "")).startswith("off|No such bench"), "P40 LIST an unknown bench = off")
        Bridge.PLAYERS = None
        K.check(call(23, U, "Furnace", "", "") is None and call(24, U, "Furnace", "collect", "", "", k) is None, "P40 no player on this world thread -> null (nothing read, nothing moves)")
        Bridge.PLAYERS = TPlayers()
        # ---- QUEUE
        o0 = ore(p)
        r = call(24, U, "Furnace", "queue", "Skyy_Test_Cu40", "10", "someone-else")
        K.check(str(r).startswith("-Your profile changed") and ore(p) == o0 and int(bench().queued()) == 0, "P40 QUEUE another profile's token: refused, NOTHING moved (%s)" % r)
        r = call(24, U, "Furnace", "queue", "Skyy_Test_Cu40", "10", "")
        K.check(str(r).startswith("-Your profile changed") and ore(p) == o0 and int(bench().queued()) == 0, "P40 QUEUE no token: refused, nothing moved")
        r = call(24, U, "Furnace", "queue", "Skyy_Not_Listed", "10", k)
        K.check(str(r).startswith("-That recipe is not in your Furnace list") and ore(p) == o0, "P40 QUEUE a recipe not in the list: refused (%s)" % r)
        r = call(24, U, "Furnace", "queue", "Skyy_Test_Cu40", "ten", k)
        K.check(str(r).startswith("-Type a number") and ore(p) == o0, "P40 QUEUE a typed word: refused")
        r = call(24, U, "Furnace", "queue", "Skyy_Test_Cu40", "10", k)
        K.check(str(r).startswith("+Queued 10 x") and int(bench().queued()) == 10 and ore(p) == o0 - 10 and inv_counts(p).get(COP, 0) == 20,
                "P40 QUEUE 10: exactly 10 ore taken (inventory first: 30 -> 20), 10 queued (%s)" % r)
        r = call(23, U, "Furnace", "", "")
        K.check([l_.split("|")[3] for l_ in r.split("\n") if l_.startswith("q|")] == ["10"] and r.split("\n")[0].split("|")[6] == "10", "P40 LIST the queue row (10) + the used count")
        bridge.put(JString("acc:has:" + k), JString(""))
        r = call(24, U, "Furnace", "queue", "Skyy_Test_Cu40", "5", k)
        K.check(str(r).startswith("-Equip a Furnace accessory") and ore(p) == o0 - 10, "P40 QUEUE no accessory: refused, nothing taken")
        K.check(str(call(23, U, "Furnace", "", "")).startswith("ok|Furnace|0|"), "P40 LIST no accessory but work in the bench = still listed (the page's sub-tab rule)")
        bridge.put(JString("acc:has:" + k), JString("Skyy_Accessory_Furnace_T1,Skyy_Accessory_Tannery_T1"))
        r = call(24, U, "Furnace", "queue", "Skyy_Test_Cu40", "5000000000", k)
        K.check(int(bench().queued()) == 100 and ore(p) == 0, "P40 QUEUE a huge number (5,000,000,000 - no int overflow) = all: every ore (90 more) queued, no ore lost or doubled (%s)" % r)
        THROW["on"] = True
        r = call(24, U, "Furnace", "queue", "Skyy_Test_Cu40", "1", k)
        THROW["on"] = False
        K.check(str(r).startswith("-That did not finish") and int(bench().queued()) == 100, "P40 QUEUE a throw inside = '-', nothing more moved (%s)" % r)
        # ---- CANCEL (the inputs back, through the output slot + Collect)
        r = call(24, U, "Furnace", "cancel", "", "", k)
        K.check(str(r).startswith("+Cancelled 100 units") and int(bench().queued()) == 0 and inv_counts(p).get(COP, 0) == 100 and int(bench().outTotal()) == 0,
                "P40 CANCEL every unfinished unit's ore back into the inventory (100) (%s)" % r)
        # ---- COLLECT
        p = mk({}, storage=[])
        bench().addOut(JString(OUT40), JInt(30))
        r = call(24, U, "Furnace", "collect", "", "", "wrong")
        K.check(str(r).startswith("-Your profile changed") and int(bench().outTotal()) == 30 and inv_counts(p).get(OUT40, 0) == 0, "P40 COLLECT a stale token: refused, nothing moved")
        r = call(24, U, "Furnace", "collect", "", "", k)
        K.check(str(r).startswith("+Collected 30 items") and inv_counts(p).get(OUT40, 0) == 30 and int(bench().outTotal()) == 0, "P40 COLLECT 30 into the inventory (%s)" % r)
        r = call(24, U, "Furnace", "collect", "", "", k)
        K.check(str(r).startswith("-Nothing to collect") and inv_counts(p).get(OUT40, 0) == 30, "P40 COLLECT again (a double click): nothing more, exactly 30 (%s)" % r)
        p = mk({}, storage=[(FILL, 25)] * 36, hotbar=[(FILL, 25)] * 9, backpack=[(FILL, 25)] * 9)
        bench().addOut(JString(OUT40), JInt(50))
        r = call(24, U, "Furnace", "collect", "", "", k)
        K.check(str(r).startswith("-Your inventory is full") and int(bench().outTotal()) == 50 and inv_counts(p).get(OUT40, 0) == 0,
                "P40 COLLECT a FULL inventory (bag, hotbar and backpack): refused, all 50 stay in the bench (%s)" % r)
        p = mk({}, storage=[(FILL, 25)] * 35, hotbar=[(FILL, 25)] * 9, backpack=[(FILL, 25)] * 9)
        bench().addOut(JString(OUT40), JInt(150))
        r = call(24, U, "Furnace", "collect", "", "", k)
        K.check(inv_counts(p).get(OUT40, 0) + int(bench().outTotal()) == 200 and inv_counts(p).get(OUT40, 0) == 100 and "still waiting" in str(r),
                "P40 COLLECT a nearly full inventory: what fits (100), the rest stays (100 of 200) (%s)" % r)
        # ---- FUEL
        p = mk({OAK: 50}, storage=[(OAK, 30)])
        pb = bench()
        pb.needsFuel = True
        r = call(24, U, "Furnace", "fuel", OAK, "20", k)
        K.check(str(r).startswith("+Loaded 20") and int(pb.fuelCount()) == 20 and inv_counts(p).get(OAK, 0) + pc(k).get(OAK, 0) == 60 and inv_counts(p).get(OAK, 0) == 10,
                "P40 FUEL load 20: 20 taken (inventory first), 20 in the fuel slot (%s)" % r)
        K.check(str(call(24, U, "Furnace", "fuel", COP, "5", k)).startswith("-") and int(pb.fuelCount()) == 20, "P40 FUEL a non-fuel refused")
        K.check(str(call(24, U, "Furnace", "fuel", OAK, "lots", k)).startswith("-Type a number") and int(pb.fuelCount()) == 20, "P40 FUEL a typed word refused")
        r = call(24, U, "Furnace", "fuel", OAK, "1000", k)
        K.check(int(pb.fuelCount()) == 80 and inv_counts(p).get(OAK, 0) + pc(k).get(OAK, 0) == 0, "P40 FUEL more than you own = what you own (60 more) (%s)" % r)
        r = call(23, U, "Furnace", "", "")
        hd = r.split("\n")[0].split("|")
        K.check(hd[8] == "1" and hd[9] == "80" and [l_.split("|")[3] for l_ in r.split("\n") if l_.startswith("f|") and l_.split("|")[1] == OAK] == ["80"],
                "P40 LIST the fuel: burns fuel, 80 loaded, the fuel row")
        r = call(24, U, "Furnace", "unload", "", "", k)
        K.check(str(r).startswith("+Unloaded 80") and int(pb.fuelCount()) == 0 and inv_counts(p).get(OAK, 0) == 80, "P40 FUEL Unload: the 80 back in the inventory (%s)" % r)
        K.check(str(call(24, U, "Tannery", "fuel", OAK, "5", k)).startswith("-The Tannery burns no fuel"), "P40 FUEL the Tannery burns no fuel: refused")
        # ---- SUM (Right now)
        bench().addOut(JString(OUT40), JInt(7))
        r = call(23, U, "sum")
        K.check(r is not None and r.startswith("sum|Furnace|7|0|"), "P40 SUM the Furnace row: 7 ready (%s)" % r)
    finally:
        Bridge.PLAYERS = None
        Bridge.FRECIPES = None
        PB.FUELS = None


def run_p40(out, jar, scratch, home):
    T089.void_cases = cases40
    T089.run_void(out, jar, scratch, home)


def run_static(out, jar, scratch, home):
    import subprocess, zipfile
    K = HK.Child(out)
    gen = os.path.join(HERE, "build_skyysacks_%s.py" % VERSION)
    cp = os.path.join(scratch, "regen.py")
    p = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "sacks_0_8_40_patch.py"), "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(gen, "rb").read(), "S the patch re-generates the script byte for byte: %s" % p.stderr[-300:])
    g = open(gen, encoding="utf8").read()
    for key in ("sacks:fn:pocketList", "sacks:fn:pocket", "sacks:fn:openTannery", "sacks:fn:openPocket", "sacks:fn:furnList", "sacks:fn:furn"):
        K.check(g.count('sbr0.put("%s"' % key) == 1, "S setup publishes %s once" % key)
    K.check("this.mode == 20 || this.mode == 21 || this.mode == 23 || this.mode == 24) ? null" in g, "S the furnace modes 23 / 24 answer null when they fail")
    zn, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    K.eq(sorted(set(zn.namelist()) ^ set(zo.namelist())), [], "S no jar entry added or removed")
    K.eq(sorted(n for n in zn.namelist() if not n.endswith(".class") and zn.read(n) != zo.read(n)), ["manifest.json"], "S changed non-class entries = manifest.json")
    K.save()


if __name__ == "__main__":
    os.makedirs(SCRATCH, exist_ok=True)
    HK.run("SkyySacks", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, [],
           [("static", run_static), ("p40", run_p40), ("f37", T37.run_f37), ("s36", T36.run_s36), ("all35", T35.run_all35), ("bc36", T36.run_bc36),
            ("live", T30.T0827.run_live27), ("live2", T30.T0827.T0810.run_live10)],
           __file__, live=(BETA, "Skyy_SkyySacks"))
