"""Harness for SkyyShards 0.4.6 (shards = a level 20 reward, the old shard recipes off, buying islands 2-6 on the coin curve;
tools/shards_0_4_6_patch.py). Build first:
    python tools/shards_0_4_6_patch.py && python SkyyShards/build_skyyshards_0.4.6.py
    python SkyyShards/test_skyyshards_0.4.6.py [--keep]

  S    static   the patch re-runs to identical bytes; ShMig046 + ShLv20 added and written out; no new registerSystem / registerCommand;
                setup order migCoop, ShMig044, ShMig045, ShMig046, loadCfg, CfgPub.start
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.4.5 -> 0.4.6: + ShMig046, ShLv20; exactly the planned members differ (EXPECT)
  K    config   EXECUTED loadCfg: a fresh file (lv20.* 20, island.* rows, the six shard recipes EMPTY, the marker), a bare file, hand edits +
                clamps; the Server Setup rows' defaults; the built-in coin curve = tools/balance_model.py at every level 1..100; island
                prices 19,000 / 57,000 / 170,000 / 510,000 / 1,535,000 (built-in curve), with coins:fn:curve (stub) and when it throws
  M    mig      ShMig046 on scratch files: the NewBetaTest config (read only, copied): the 6 shard recipe lines -> empty, marker, History,
                6 change-log lines, start 2 nothing; hand-edited / doubled / spaced lines; Undo through the kit; fresh file; History blocked;
                then a shard recipe is switched off for crafting and not listed at the Totem Bench
  X    exec     EVERY NEW CODE PATH on real SimpleItemContainers: the level 20 grant for each kind (Farming / Mining / Foraging + Orchard /
                Beastmastery = Ranching / class = Combat), join catch-up (already past 20), twice = once, a level-up later, inventory
                full (waits, nothing recorded, given once there is room), a profile that already had the shard (placed / admin give / in
                the inventory) = recorded, nothing given, profile switch (each profile its own), switching / busy = refused, a refused
                save, lv20.<kind> = 0, no SkyySkills / only the old skill:fn:level, no class = no Combat shard, scan() without a server;
                BUYING ISLANDS 2-6: price + items per Nth island, atomic take, refunds (coins refused, save refused, no SkyyCoins), short
                items, the same slot twice, co-op / visitor refused, all six, coins only (empty item row); the page (Islands tab: empty
                slot = price + Buy island bound, island = Grow, co-op = no Buy) and the ibuy click
  D    live     START TWICE on a scratch COPY of NewBetaTest's Skyy_SkyyShards: migCoop, ShMig044, ShMig045, ShMig046, loadCfg twice
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import balance_model as BM

VERSION = "0.4.6"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "shards046", "h")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyShards-%s.jar" % VERSION)]
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyShards-0.4.5.jar")
GEN = os.path.join(HERE, "build_skyyshards_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyshards_0.4.5.py")
PATCH = os.path.join(ROOT, "tools", "shards_0_4_6_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.shards."
_argv = list(sys.argv)
_spec = importlib.util.spec_from_file_location("test_skyyshards_0_4_4", os.path.join(HERE, "test_skyyshards_0.4.4.py"))
T44 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T44)
sys.argv[:] = _argv
T42, T04, LIVE_SH = T44.T42, T44.T04, T44.LIVE_SH
KINDS = ["Mining", "Foraging", "Farming", "Ranching", "Orchard", "Combat"]
KK = [k.lower() for k in KINDS]
SHARDS = ["Skyy_Shard_" + k for k in KINDS]
OLD_REC = {"Skyy_Shard_Farming": "Skyy_Ench_Wheat:32,Ingredient_Life_Essence:64;100000",
           "Skyy_Shard_Mining": "Skyy_Ench_Cobblestone:32,Ingredient_Life_Essence:64;100000",
           "Skyy_Shard_Foraging": "Skyy_Ench_Oak:32,Ingredient_Life_Essence:64;100000",
           "Skyy_Shard_Ranching": "Skyy_Ench_Wheat:32,Food_Chicken_Raw:256;100000",
           "Skyy_Shard_Orchard": "Skyy_Ench_Oak:16,Plant_Fruit_Apple:256;100000",
           "Skyy_Shard_Combat": "Ingredient_Void_Essence:64,Ingredient_Bone_Fragment:512;100000"}
MIGK = ["craft." + s for s in SHARDS]
MK = "skyyshards-0.4.6-lv20"
ISL_ITEM = ["Skyy_Ench_Copper", "Skyy_Ench_Oak", "Skyy_Ench_Wheat", "Skyy_Ench_RawChicken", "Skyy_Ench_Apple", "Skyy_Ench_Bone"]
ISL_QTY = [0, 0, 8, 16, 32, 64, 128]
CV20 = BM.p7_curve_from_text(BM.P7_CURVE_TEXT, 20)
PRICES = [0, 0] + [BM.p7_round(8300 * CV20 * 3.0 ** (n - 2)) for n in range(2, 7)]
OWNER = T04.OWNER
MEMBER = T04.MEMBER
VISITOR = T04.VISITOR
ADMIN = T04.ADMIN
FK, MKD, FOK, RK, OK_, CK = 2, 0, 1, 3, 4, 5


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyShards 0.4.6 - build script') and g.count('VERSION = "0.4.6"\n') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.check("ALLC = [cfg, smig, smig45, smig46, st, knd, lv," in g, "S ShMig046 + ShLv20 written out")
    HK.jvm([B.SERVER_JAR, JAR, B.JAVASSIST], verify=False)
    calls = T42.setup_calls(jar)
    K.check(calls.index("ShCfg.migCoop") < calls.index("ShMig044.run") < calls.index("ShMig045.run") < calls.index("ShMig046.run")
            < calls.index("ShCfg.loadCfg") < calls.index("CfgPub.start"), "S setup order: migCoop, ShMig044, ShMig045, ShMig046, loadCfg, CfgPub.start")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def _fn():
    return T04.fn_class()


def run_config(out, jar, scratch, _home):
    from jpype import JClass, JDouble, JInt
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    K = HK.Child(out)
    PyFn = _fn()
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    home = os.path.join(scratch, "k1", "mods", "Skyy_SkyyShards")
    os.makedirs(home)
    Cfg, path = T42.kit_home(home)
    Cfg.loadCfg(True)
    t = open(os.path.join(home, "config.properties"), "rb").read().replace(b"\r\n", b"\n").decode("latin-1")
    lines = t.split("\n")
    K.check(all(("lv20.%s=20" % k) in lines for k in KK), "K a fresh file: lv20.<kind>=20 for all six")
    K.check(all(("craft.%s=" % s) in lines for s in SHARDS), "K a fresh file: the six shard recipes are EMPTY (off)")
    K.check("island.coins.base=8300" in lines and "island.coins.level=20" in lines and "island.coins.step=3" in lines
            and all(("island.items.%d=%d" % (n, ISL_QTY[n])) in lines for n in range(2, 7))
            and all(("island.item.%s=%s" % (KK[i], ISL_ITEM[i])) in lines for i in range(6)), "K a fresh file: the island rows")
    K.check(t.count(MK) == 1, "K a fresh file carries the 0.4.6 marker once")
    K.eq([int(x) for x in Cfg.LV20], [20] * 6, "K LV20 read")
    K.eq([int(Cfg.islandCoins(n)) for n in range(1, 8)], [0, PRICES[2], PRICES[3], PRICES[4], PRICES[5], PRICES[6], int(Cfg.islandCoins(7))],
         "K island prices, no SkyyCoins (built-in curve): %s" % PRICES[2:])
    K.eq(PRICES[2:], [19000, 57000, 170000, 510000, 1535000], "K the prices = 8,300 x curve(20) x 3^(N-2), p7_round")
    K.eq([int(Cfg.islandQty(n)) for n in range(0, 8)], [0, 0, 8, 16, 32, 64, 128, 0], "K island items per Nth island (out of range = 0)")
    K.eq([str(Cfg.islandItem(i)) for i in range(-1, 7)], [""] + ISL_ITEM + [""], "K island material per shard (out of range = empty)")
    bad = [L for L in range(-5, 106) if abs(float(Cfg.curveBuiltin(L)) / BM.p7_curve_from_text(BM.P7_CURVE_TEXT, L) - 1.0) > 1e-9]
    K.check(not bad, "K the built-in curve = SkyyCoins' default text at every level -5..105 (clamped 1..100): %s" % bad[:5])
    br.put("coins:fn:curve", PyFn(lambda a: JDouble(2.0) if int(a[0]) == 20 else JDouble(9.0)))
    K.eq([int(Cfg.islandCoins(n)) for n in (2, 3)], [BM.p7_round(16600.0), BM.p7_round(49800.0)], "K with coins:fn:curve (stub 2.0 at Lv 20) the bridge value is used")

    def boom(a):
        raise RuntimeError("curve down")
    br.put("coins:fn:curve", PyFn(boom))
    K.eq(int(Cfg.islandCoins(2)), PRICES[2], "K a coins:fn:curve that throws = the built-in curve")
    br.put("coins:fn:curve", PyFn(lambda a: JDouble(-1.0)))
    K.eq(int(Cfg.islandCoins(2)), PRICES[2], "K a nonsense curve value = the built-in curve")
    br.remove("coins:fn:curve")
    K.eq([int(Cfg.round7(x)) for x in (0, 994, 995, 18924.4, 56773, 170317, 1532850, -3)], [0, 990, 1000, 19000, 57000, 170000, 1535000, 0], "K round7 = p7_round")
    open(os.path.join(home, "config.properties"), "a", encoding="latin-1").write(
        "\nisland.coins.step=2\nisland.items.3=5\nisland.item.mining=\nlv20.combat=0\nlv20.farming=999\nisland.coins.level=30\nisland.coins.base=-4\n")
    Cfg.loadCfg(False)
    K.check(float(Cfg.ISL_STEP) == 2.0 and int(Cfg.islandQty(3)) == 5 and str(Cfg.islandItem(0)) == "" and int(Cfg.LV20[5]) == 0 and int(Cfg.LV20[2]) == 200
            and int(Cfg.ISL_LV) == 30 and int(Cfg.ISL_BASE) == 0 and int(Cfg.islandCoins(2)) == 0,
            "K hand edits read + clamped (step 2, items 5, empty item = coins only, combat 0 = off, 999 -> 200, base -4 -> 0)")
    home2 = os.path.join(scratch, "k2", "mods", "Skyy_SkyyShards")
    os.makedirs(home2)
    open(os.path.join(home2, "config.properties"), "w").write("shards.on=true\n")
    Cfg, path = T42.kit_home(home2)
    Cfg.loadCfg(True)
    K.check([int(x) for x in Cfg.LV20] == [20] * 6 and int(Cfg.islandCoins(2)) == PRICES[2] and all(str(Cfg.CRAFT[i]) == "" for i in range(len(Cfg.CRAFT_ID)) if str(Cfg.CRAFT_ID[i]) in SHARDS),
            "K a file without the lines reads the new code defaults (lv20 20, island 2 = 19,000, shard recipes off)")
    rows = dict((str(r[0]), [str(x) for x in list(r)]) for r in JClass(PKG + "CfgRows").header()[7])
    want = dict([("lv20." + k, "20") for k in KK] + [("island.coins.base", "8300"), ("island.coins.level", "20"), ("island.coins.step", "3")]
                + [("island.items.%d" % n, str(ISL_QTY[n])) for n in range(2, 7)] + [("island.item." + KK[i], ISL_ITEM[i]) for i in range(6)]
                + [(k, "") for k in MIGK])
    K.eq(dict((k, rows[k][4] if k in rows else None) for k in want), want, "K the Server Setup rows exist with their defaults (%d)" % len(want))
    K.check(rows["lv20.ranching"][1] == "Ranching Shard at Beastmastery level" and rows["lv20.combat"][1] == "Combat Shard at class level"
            and rows["lv20.orchard"][1] == "Orchard Shard at Foraging level", "K the level rows name the skill")
    K.save()


def run_mig(out, jar, scratch, _home):
    from jpype import JClass, JString, JArray
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    K = HK.Child(out)
    Mig = JClass(PKG + "ShMig046")
    nf = [0]

    def world(b_):
        nf[0] += 1
        home = os.path.join(scratch, "m%d" % nf[0], "mods", "Skyy_SkyyShards")
        os.makedirs(home)
        Cfg, path = T42.kit_home(home)
        f = os.path.join(home, "config.properties")
        if b_ is not None:
            open(f, "wb").write(b_)
        return home, f, Cfg, path

    def hist(home):
        hd = os.path.join(home, "config-history")
        return [open(os.path.join(hd, n), "rb").read() for n in sorted(os.listdir(hd)) if n.endswith(".bak")] if os.path.isdir(hd) else []

    def chg(home):
        f = os.path.join(home, "config-changes.log")
        return [l.split("\t") for l in open(f, encoding="utf8").read().splitlines()] if os.path.isfile(f) else []

    def props(b_):
        P_ = JClass("java.util.Properties")()
        P_.load(JClass("java.io.ByteArrayInputStream")(b_))
        return dict((str(k), str(P_.getProperty(k))) for k in P_.stringPropertyNames())

    def crafts(Cfg):
        return dict((str(Cfg.CRAFT_ID[i]), str(Cfg.CRAFT[i])) for i in range(len(Cfg.CRAFT_ID)) if str(Cfg.CRAFT_ID[i]) in SHARDS)
    live = os.path.join(LIVE_SH, "config.properties")
    A_ = open(live, "rb").read() if os.path.isfile(live) else None
    K.check(A_ is not None, "M the live NewBetaTest config.properties exists (read only)")
    if A_ is not None:
        home, f, Cfg, path = world(A_)
        r = str(Mig.run(path(f)))
        b1 = open(f, "rb").read()
        nl = b"\r\n" if b"\r\n" in A_ else b"\n"
        pa, pb = props(A_), props(b1)
        K.check(sorted(k for k in pb if pa.get(k) != pb.get(k)) == sorted(MIGK) and all(pb[k] == "" for k in MIGK) and len(pa) == len(pb),
                "M live: exactly the 6 shard recipe lines became empty: %s" % [(k, pa.get(k), pb.get(k)) for k in MIGK if pb.get(k) != ""])
        K.check(b1.endswith(("# ---------- SkyyShards 0.4.6 (marker %s" % MK).encode() + b1.split(MK.encode())[1].split(nl)[0] + nl), "M live: the marker line appended in the file's own ending")
        K.check(hist(home) == [A_], "M live: config-history holds the old bytes")
        cl = chg(home)
        K.check(sorted((x[4], x[5], x[6]) for x in cl) == sorted((k, OLD_REC[k[6:]], "") for k in MIGK) and all(x[1] == "SkyyShards 0.4.6" and x[7] == "ok" for x in cl),
                "M live: one change-log line per changed recipe (6): %s" % [x[4:7] for x in cl][:2])
        Cfg.loadCfg(False)
        K.eq(crafts(Cfg), dict((s, "") for s in SHARDS), "M live: loadCfg reads the six recipes as off")
        K.check(str(Mig.run(path(f))) == "" and open(f, "rb").read() == b1 and len(hist(home)) == 1, "M live: start 2 changes nothing (marker)")
        K.check("craft.Skyy_Shard_Farming" in r and "runs once" in r, "M live: the INFO line names the changes: %s" % r[:160])
    syn = ("# head\ncraft.Skyy_Shard_Farming=%s\ncraft.Skyy_Shard_Mining=Skyy_Ench_Cobblestone:10;5\ncraft.Skyy_Shard_Foraging=%s\ncraft.Skyy_Shard_Foraging=%s\n"
           "craft.Skyy_Shard_Orchard = Skyy_Ench_Oak:16, Plant_Fruit_Apple:256;100000\r\ncraft.Skyy_Shard_Combat=\nx=1") % (
        OLD_REC["Skyy_Shard_Farming"], OLD_REC["Skyy_Shard_Foraging"], OLD_REC["Skyy_Shard_Foraging"])
    home, f, Cfg, path = world(syn.encode("latin-1"))
    r = str(Mig.run(path(f)))
    t = open(f, "rb").read().decode("latin-1")
    K.check(t.startswith("# head\ncraft.Skyy_Shard_Farming=\ncraft.Skyy_Shard_Mining=Skyy_Ench_Cobblestone:10;5\ncraft.Skyy_Shard_Foraging=%s\ncraft.Skyy_Shard_Foraging=%s\n"
                         "craft.Skyy_Shard_Orchard = \r\ncraft.Skyy_Shard_Combat=\nx=1\n# ---------- SkyyShards 0.4.6" % (OLD_REC["Skyy_Shard_Foraging"], OLD_REC["Skyy_Shard_Foraging"])),
            "M syn: Farming emptied, the admin's Mining recipe and the doubled Foraging kept, the spaced Orchard (its CRLF) emptied, an empty Combat left: %r" % t[:330])
    K.check("craft.Skyy_Shard_Mining=Skyy_Ench_Cobblestone:10;5 kept - an admin changed it" in r and "craft.Skyy_Shard_Foraging=" in r and "doubled" in r,
            "M syn: the kept lines are named: %s" % r.replace("\n", " | ")[:300])
    K.eq(len(chg(home)), 2, "M syn: 2 change-log lines")
    CP, Fn = JClass(PKG + "CfgPub"), JClass(PKG + "CfgFn")
    CP.start(path(os.path.dirname(home)), JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyShards"))
    ru = str(Fn.cmdSetConsole(JString("craft.Skyy_Shard_Farming"), JString(OLD_REC["Skyy_Shard_Farming"])))
    CP.shutdown()
    t2 = open(f, "rb").read().decode("latin-1")
    K.check(("craft.Skyy_Shard_Farming=" + OLD_REC["Skyy_Shard_Farming"]) in t2.splitlines(), "M undo: the kit sets the Farming recipe back: %s" % ru)
    K.check(str(Mig.run(path(f))) == "" and open(f, "rb").read().decode("latin-1") == t2, "M undo: the next start keeps the undone value (marker)")
    home, f, Cfg, path = world(None)
    K.check(str(Mig.run(path(f))) == "" and not os.path.exists(f), "M fresh: no file -> nothing done")
    Cfg.loadCfg(True)
    t3 = open(f, "rb").read()
    K.check(str(Mig.run(path(f))) == "" and open(f, "rb").read() == t3 and hist(home) == [], "M fresh: the default file carries the marker - nothing written")
    home, f, Cfg, path = world(("craft.Skyy_Shard_Combat=%s\n" % OLD_REC["Skyy_Shard_Combat"]).encode())
    open(os.path.join(home, "config-history"), "wb").write(b"not a folder")
    K.check(str(Mig.run(path(f))) == "" and open(f, "rb").read() == ("craft.Skyy_Shard_Combat=%s\n" % OLD_REC["Skyy_Shard_Combat"]).encode(),
            "M nohist: config-history cannot be made -> the file is untouched")
    os.remove(os.path.join(home, "config-history"))
    T42.kit_home(home)
    K.check(str(Mig.run(path(f))) != "" and b"craft.Skyy_Shard_Combat=\n" in open(f, "rb").read(), "M nohist: the next start updates it")
    # crafting: an off shard recipe is refused + not listed at the bench; an admin's recipe is listed again
    Cfg.loadCfg(False)
    Core, Page = JClass(PKG + "ShCore"), JClass(PKG + "ShPage")
    UUID = JClass("java.util.UUID")
    ou = UUID.fromString(OWNER)
    ids = [str(x) for x in Cfg.CRAFT_ID]
    ri = ids.index("Skyy_Shard_Farming")
    K.check(str(Core.craftGate(ou, ri)).startswith("This recipe is switched off"), "M craftGate: the off Farming Shard recipe is switched off")
    pg = Page(ou, "skyy-island-" + OWNER)
    pg.view = 4
    pg.fillBenchCraft(None, FK, 4)
    listed = [ids[int(pg.kIdx[i])] for i in range(int(pg.kN))]
    K.check(not any(x in SHARDS for x in listed) and "Skyy_Totem_HarvestSpirit" in listed, "M the Totem Bench lists no off shard recipe (%d rows)" % len(listed))
    CR = list(Cfg.CRAFT)
    CR[ri] = OLD_REC["Skyy_Shard_Farming"]
    Cfg.CRAFT = JArray(JString)(CR)
    pg.fillBenchCraft(None, FK, 4)
    K.check("Skyy_Shard_Farming" in [ids[int(pg.kIdx[i])] for i in range(int(pg.kN))], "M an admin's own shard recipe is listed again")
    K.save()


# ====================================================================================================== X: the new code paths
def _fixture(scratch, K):
    from jpype import JClass, JArray, JLong, JInt, JString, JObject
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, JAR], verify=True)
    Sys = JClass("java.lang.System")
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    Sys.getProperties().put("skyy.bridge", br)
    P = lambda n: JClass(PKG + n)
    L = dict((n, P(n)) for n in ("ShCfg", "ShStore", "ShTotem", "ShMath", "ShRole", "ShInv", "ShPay", "ShCore", "ShPage", "ShKind", "ShLv20"))
    Paths, UUID = JClass("java.nio.file.Paths"), JClass("java.util.UUID")
    PyFn = _fn()
    base = os.path.join(scratch, "x")
    os.makedirs(base, exist_ok=True)
    Cfg, St = L["ShCfg"], L["ShStore"]
    Cfg.DIR = Paths.get(base)
    Cfg.FILE = Paths.get(os.path.join(base, "config.properties"))
    Cfg.loadCfg(True)
    sd = os.path.join(base, "shards")
    os.makedirs(sd, exist_ok=True)
    St.DIR = Paths.get(sd)
    keys = {}
    Cfg.KEY_TEST = PyFn(lambda u: JString(keys.get(str(u), str(u))))
    misc = [(x, 100) for x in ISL_ITEM + ["Rock_Stone", "Ore_Copper", "Plant_Crop_Wheat_Item", "Ingredient_Life_Essence", "Plant_Seeds_Wheat_Eternal"]]
    T04.item_store([(s, 1) for s in SHARDS] + [(str(x), 1) for x in L["ShTotem"].ITEMS] + misc)
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    IC = JClass("com.hypixel.hytale.server.core.inventory.container.ItemContainer")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    Short = JClass("java.lang.Short")

    def inv(*caps):
        return JArray(IC)([SIC(Short(c).shortValue()) for c in caps])

    def count(cs, iid):
        return int(L["ShInv"].count(cs, iid))
    Bool = JClass("java.lang.Boolean")
    Role = L["ShRole"]
    roles = {OWNER: "owner", MEMBER: "member", VISITOR: "visitor", ADMIN: "visitor"}
    Role.ROLEKEY_TEST = PyFn(lambda a: roles.get(str(a[0])) if str(a[1]) == OWNER else None)
    Role.ROLE_TEST = PyFn(lambda a: roles.get(str(a[0])) if str(a[1]) == "skyy-island-" + OWNER else None)
    Role.OWNER_TEST = PyFn(lambda w: OWNER if str(w) == "skyy-island-" + OWNER else None)
    Role.WORLD_TEST = PyFn(lambda w: Bool.TRUE)
    coins = {"bal": 10000000, "fail": False}

    def take_coins(a):
        n_ = int(a[1])
        if coins["fail"] or coins["bal"] < n_:
            return Bool.FALSE
        coins["bal"] -= n_
        return Bool.TRUE

    def add_coins(a):
        coins["bal"] += int(a[1])
        return JLong(coins["bal"])
    levels = {}     # pkey -> {skill: level}; "class" -> the class skill name per uuid

    def run_fn(a):
        who, sk = a[0], str(a[1])
        if isinstance(who, UUID):
            if sk != "class":
                return None
            cls = levels.get("class:" + str(who))
            if cls is None:
                return None
            return JArray(JObject)([JInt(0), JInt(100), JLong(0), JLong(0), Bool.FALSE, JString(cls)])
        lv = levels.get(str(who), {}).get(sk)
        if lv is None:
            return None
        return JArray(JObject)([JInt(lv), JInt(100), JLong(0), JLong(0), Bool.FALSE, JString(sk)])
    fns = JClass("java.util.HashMap")()
    fns.put("coins:fn:get", PyFn(lambda u: JLong(coins["bal"])))
    fns.put("coins:fn:take", PyFn(take_coins))
    fns.put("coins:fn:add", PyFn(add_coins))
    fns.put("coll:fn:tier", PyFn(lambda a: JInt(9)))
    fns.put("rebirth:fn:count", PyFn(lambda k: JInt(0)))
    fns.put("skill:fn:run", PyFn(run_fn))
    L["ShPay"].TEST_FNS = fns
    L["ShCore"].NOW_TEST = 1790000000000
    L.update(dict(K=K, br=br, PyFn=PyFn, inv=inv, count=count, keys=keys, coins=coins, levels=levels, fns=fns, roles=roles, IS=IS, Short=Short,
                  UUID=UUID, Bool=Bool, JString=JString, JInt=JInt, JLong=JLong, sd=sd))
    return L


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JString, JInt, JArray
    K = HK.Child(out)
    L = _fixture(scratch, K)
    Cfg, St, Lv, Core, Inv, Mth, Kind = (L[n] for n in ("ShCfg", "ShStore", "ShLv20", "ShCore", "ShInv", "ShMath", "ShKind"))
    inv, count, keys, levels, fns, UUID, br, Bool, PyFn = (L[n] for n in ("inv", "count", "keys", "levels", "fns", "UUID", "br", "Bool", "PyFn"))
    ou, mu, vu, au = (UUID.fromString(x) for x in (OWNER, MEMBER, VISITOR, ADMIN))

    def rec(k, kd):
        return str(St.get(k).getProperty("lv20." + KK[kd]) or "")

    def held(cs):
        return [count(cs, s) for s in SHARDS]

    def lines(r):
        return dict((l.split(" ", 1)[0], l.split(" ", 1)[1]) for l in str(r).split("\n") if l)
    K.eq(str(Lv.how(FK)), "Farming level 20", "X how(): Farming level 20")
    K.eq([str(Lv.how(k)) for k in (RK, OK_, CK)], ["Beastmastery level 20", "Foraging level 20", "class level 20"], "X how(): Ranching = Beastmastery, Orchard = Foraging, Combat = class")
    # ---- X1 join catch-up: a player already past 20 in some skills gets exactly those, once
    levels[OWNER] = {"Farming": 25, "Mining": 5, "Foraging": 20, "Beastmastery": 19, "Combat.Warrior": 30}
    levels["class:" + OWNER] = "Combat.Warrior"
    TI = inv(9, 9)
    K.eq(sorted(int(x) for x in Lv.due(ou, OWNER)), [FOK, FK, OK_, CK], "X1 due: Foraging, Farming, Orchard (Foraging 20), Combat (class 30); not Mining 5 / Beastmastery 19")
    r = lines(Lv.catchUp(ou, OWNER, TI, None))
    K.check(sorted(r) == ["combat", "farming", "foraging", "orchard"] and all(v.startswith("+") for v in r.values()), "X1 catch-up grants the four: %s" % r)
    K.eq(held(TI), [0, 1, 1, 0, 1, 1], "X1 the inventory holds Foraging, Farming, Orchard, Combat shards (one each)")
    K.check(all(rec(OWNER, kd).startswith("given:") for kd in (FOK, FK, OK_, CK)) and rec(OWNER, MKD) == "" and rec(OWNER, RK) == "",
            "X1 records lv20.<kind>=given:<ms> for the four only")
    K.check(all(str(St.get(OWNER).getProperty(KK[kd] + ".crafted")) == "1" for kd in (FOK, FK, OK_, CK)), "X1 <kind>.crafted = 1 (the one-shard rule sees them)")
    K.check("Reward for Farming level 20: your Farming Shard" in r["farming"] and "Reward for class level 20" in r["combat"], "X1 the chat text names the level: %s" % r["farming"])
    fb = open(os.path.join(L["sd"], OWNER + ".properties"), encoding="latin-1").read()
    K.check("lv20.farming=given\\:" in fb or "lv20.farming=given:" in fb, "X1 the record is on disk")
    # twice = once
    K.eq(str(Lv.catchUp(ou, OWNER, TI, None)), "", "X1 a second catch-up: nothing due")
    K.check(str(Lv.grant(ou, OWNER, FK, TI)).startswith("=The Farming Shard reward is recorded already") and held(TI) == [0, 1, 1, 0, 1, 1],
            "X1 grant() again directly: recorded already, nothing given")
    # a level-up later
    levels[OWNER]["Beastmastery"] = 20
    r = lines(Lv.catchUp(ou, OWNER, TI, None))
    K.check(list(r) == ["ranching"] and r["ranching"].startswith("+") and held(TI) == [0, 1, 1, 1, 1, 1], "X1 Beastmastery 20 later: the Ranching Shard: %s" % r)
    levels[OWNER]["Mining"] = 21
    r = lines(Lv.catchUp(ou, OWNER, TI, None))
    K.check(list(r) == ["mining"] and held(TI) == [1, 1, 1, 1, 1, 1] and len(Lv.due(ou, OWNER)) == 0 and bool(Lv.DONE.containsKey(OWNER)),
            "X1 Mining 21: the Mining Shard; all six recorded -> DONE (no more file reads)")
    # ---- X2 inventory full: waits (nothing recorded), given once there is room, never twice
    keys[MEMBER] = MEMBER
    levels[MEMBER] = {"Mining": 20}
    full = inv(1)
    full[0].addItemStack(L["IS"]("Rock_Stone", 1))
    # fix (critic shards046 #1): no free slot = nothing written at all - a save would be refused here, and the file stays absent / unchanged
    K.check(not bool(Inv.hasRoom(full)) and bool(Inv.hasRoom(inv(3))) and not bool(Inv.hasRoom(None)), "FIX1 hasRoom: full = no, empty slots = yes, null = no")
    mf = os.path.join(L["sd"], MEMBER + ".properties")
    b0 = open(mf, "rb").read() if os.path.exists(mf) else None
    St.FAIL_TEST = True
    r = str(Lv.grant(mu, MEMBER, MKD, full))
    St.FAIL_TEST = False
    b1 = open(mf, "rb").read() if os.path.exists(mf) else None
    K.check(r.startswith("~") and b0 == b1, "FIX1 full inventory: '~' without any save (saves refused, file unchanged): %s" % r)
    for _i in range(5):
        Lv.grant(mu, MEMBER, MKD, full)
    b2 = open(mf, "rb").read() if os.path.exists(mf) else None
    K.check(b2 == b0, "FIX1 five more full-inventory tries: the shard file is never written")
    r = str(Lv.grant(mu, MEMBER, MKD, full))
    K.check(r.startswith("~Your Mining Shard (reward for Mining level 20) is waiting") and count(full, "Skyy_Shard_Mining") == 0
            and rec(MEMBER, MKD) == "" and St.get(MEMBER).getProperty("mining.crafted") is None, "X2 full: waits, no record, no crafted mark: %s" % r)
    r = lines(Lv.catchUp(mu, MEMBER, full, None))
    K.check(r.get("mining", "").startswith("~") and count(full, "Skyy_Shard_Mining") == 0, "X2 every scan while full: still waiting")
    room = inv(3)
    r = lines(Lv.catchUp(mu, MEMBER, room, None))
    K.check(r.get("mining", "").startswith("+") and count(room, "Skyy_Shard_Mining") == 1 and rec(MEMBER, MKD).startswith("given:"), "X2 room: given once: %s" % r)
    K.check(str(Lv.catchUp(mu, MEMBER, room, None)) == "" and count(room, "Skyy_Shard_Mining") == 1, "X2 ... and never again")
    n0 = int(Lv.HELD.get())
    K.check(n0 >= 2, "X2 HELD counted (%d)" % n0)
    # ---- X3 a profile that already had the shard: recorded "had", nothing given
    k3 = VISITOR
    keys[VISITOR] = k3
    levels[k3] = {"Farming": 30, "Mining": 30, "Foraging": 30}
    St.LOCK.lock()
    try:
        p3 = St.get(k3)
        Mth.starter(FK, p3, L["JLong"](1790000000000))          # placed once = an island exists
        p3.setProperty("foraging.crafted", "1")                  # an admin's /shardadmin give
        St.save(k3, p3)
    finally:
        St.LOCK.unlock()
    T3 = inv(9)
    T3[0].addItemStack(L["IS"]("Skyy_Shard_Mining", 1))           # one in the inventory without a record
    r = lines(Lv.catchUp(vu, k3, T3, None))
    K.check(r.get("farming", "").startswith("=You already have") and r.get("foraging", "").startswith("=You already have")
            and r.get("mining", "").startswith("=You already have") and r.get("orchard", "").startswith("+"),
            "X3 placed / crafted / in the inventory = had (nothing given); Orchard (never had) given: %s" % r)
    K.eq(held(T3), [1, 0, 0, 0, 1, 0], "X3 the inventory: the old Mining shard + the new Orchard only")
    K.check(rec(k3, FK).startswith("had:") and rec(k3, MKD).startswith("had:") and rec(k3, FOK).startswith("had:"), "X3 recorded as had")
    # ---- X4 profile switch: each profile its own record; a switch in between = refused
    k2 = OWNER + "-p2"
    keys[OWNER] = k2
    levels[k2] = {"Farming": 20}
    r = str(Lv.grant(ou, OWNER, FK, TI))
    K.check(r.startswith("-The profile is switching") and rec(OWNER, FK).startswith("given:"), "X4 the player's active profile is p2: a grant for p1 is refused")
    T4 = inv(9)
    r = lines(Lv.catchUp(ou, k2, T4, None))
    K.check(list(r) == ["farming"] and r["farming"].startswith("+") and count(T4, "Skyy_Shard_Farming") == 1 and rec(k2, FK).startswith("given:"),
            "X4 profile p2 (Farming 20) gets its own Farming Shard: %s" % r)
    br.put("profile:busy:" + OWNER, Bool.TRUE)
    levels[k2]["Mining"] = 40
    K.check(str(Lv.grant(ou, k2, MKD, T4)).startswith("-The profile is switching") and count(T4, "Skyy_Shard_Mining") == 0 and rec(k2, MKD) == "",
            "X4 profile:busy = refused, nothing written")
    br.remove("profile:busy:" + OWNER)
    keys[OWNER] = OWNER
    # ---- X5 a refused save: nothing given, nothing recorded
    k5 = ADMIN
    keys[ADMIN] = k5
    levels[k5] = {"Farming": 20}
    T5 = inv(9)
    St.FAIL_TEST = True
    r = str(Lv.grant(au, k5, FK, T5))
    St.FAIL_TEST = False
    K.check(r.startswith("-The shard file could not be saved") and count(T5, "Skyy_Shard_Farming") == 0 and rec(k5, FK) == ""
            and St.get(k5).getProperty("farming.crafted") is None, "X5 a refused save: nothing given, memory unchanged: %s" % r)
    # ---- X6 settings / missing mods
    Cfg.LV20 = JArray(JInt)([20, 20, 0, 20, 20, 20])
    K.check(FK not in [int(x) for x in Lv.due(au, k5)], "X6 lv20.farming = 0: no free Farming Shard")
    K.check(str(Lv.how(FK)).startswith("an admin"), "X6 how() with 0 says an admin hands it out")
    # fix (critic shards046 #3): the whole clause reads right with 0, and a grant for a switched-off kind is refused
    K.eq((str(Lv.src(FK, False)), str(Lv.src(FK, True)), str(Lv.src(MKD, False)), str(Lv.src(MKD, True))),
         ("an admin can give you one", "An admin can give you one", "it is the reward for Mining level 20", "It is the reward for Mining level 20"),
         "FIX3 src(): lv20 0 = 'an admin can give you one', else 'it is the reward for <skill> level 20'")
    TF = inv(9)
    r = str(Lv.grant(au, k5, FK, TF))
    K.check(r.startswith("-No free shard of this kind") and count(TF, "Skyy_Shard_Farming") == 0 and rec(k5, FK) == "", "FIX3 grant with lv20.farming = 0: refused, nothing written: %s" % r)
    Cfg.LV20 = JArray(JInt)([20, 20, 15, 20, 20, 20])
    levels[k5]["Farming"] = 16
    K.check(FK in [int(x) for x in Lv.due(au, k5)], "X6 lv20.farming = 15: Farming 16 qualifies")
    Cfg.LV20 = JArray(JInt)([20] * 6)
    run = fns.remove("skill:fn:run")
    K.eq(len(Lv.due(au, k5)), 0, "X6 no SkyySkills (no skill:fn:run / level): nobody qualifies, no throw")
    fns.put("skill:fn:level", PyFn(lambda a: JInt(25) if str(a[1]) in ("Farming", "Combat") else JInt(1)))
    K.eq(sorted(int(x) for x in Lv.due(au, k5)), [FK, CK], "X6 an older SkyySkills (skill:fn:level only): Farming 25 + Combat (the class row) qualify")
    fns.remove("skill:fn:level")
    fns.put("skill:fn:run", run)
    levels[k5] = {"Combat.Mage": 40}
    K.check(CK not in [int(x) for x in Lv.due(au, k5)], "X6 no class picked (skill:fn:run class = null): no Combat Shard")
    levels["class:" + ADMIN] = "Combat.Mage"
    K.check(CK in [int(x) for x in Lv.due(au, k5)], "X6 with a class (Mage 40, read for that profile): the Combat Shard is due")
    fns.put("skill:fn:run", PyFn(lambda a: (_ for _ in ()).throw(RuntimeError("skills down"))))
    K.eq(len(Lv.due(au, k5)), 0, "X6 a throwing skill:fn:run = nothing due, no throw")
    fns.put("skill:fn:run", run)
    Cfg.ON = False
    K.check(len(Lv.due(au, k5)) == 0 and str(Lv.grant(au, k5, CK, T5)).startswith("-Shards are switched off") and int(Lv.scan()) == 0, "X6 shards off: nothing")
    Cfg.ON = True
    K.eq(int(Lv.scan()), 0, "X6 scan() without a running server: no throw, nothing queued")
    K.check(int(Lv.SCANS.get()) >= 1, "X6 scan() ran")
    g = open(GEN, encoding="utf8").read()
    K.check(g.count("Shard islands cost this (empty = coins only). Enchanted items need SkyyCollections.\" % KINDS[_k]") == 1, "FIX2 the island material rows (one per kind) say Enchanted items need SkyyCollections")
    K.check("Only if an admin re-adds a shard recipe: rebirths before an extra one" in g and "before it can craft an extra shard (Skyy: after rebirth 2)" not in g,
            "FIX4 craft.shardRebirth help says it only applies to a re-added recipe")
    K.check("reward for an admin" not in g and g.count("ShLv20.src(kd, ") == 4, "FIX3 every 'No X Shard yet' text uses src()")
    lvl = L["ShLv20"](None, ou, OWNER)
    lvl.run()
    K.check(not Lv.PENDING.containsKey(ou), "X6 the world task with no player: returns, PENDING cleared")
    # ---- X7 the "No shard yet" texts
    St.LOCK.lock()
    try:
        po = St.get(OWNER)
        for kk in list(po.stringPropertyNames()):
            if str(kk).startswith("mining.i"):
                po.remove(kk)
    finally:
        St.LOCK.unlock()
    K.check("it is the reward for Mining level 20" in str(Core.gate(ou, OWNER, MKD, St.get(OWNER))), "X7 gate(): no Mining shard yet - the reward for Mining level 20")

    # ---------------- X8 BUYING ISLANDS 2-6 (owner profile, Farming starter island)
    keys[OWNER] = OWNER
    St.LOCK.lock()
    try:
        po = St.get(OWNER)
        Mth.starter(FK, po, L["JLong"](1790000000000))
        St.save(OWNER, po)
    finally:
        St.LOCK.unlock()
    coins = L["coins"]
    TB = inv(9, 9, 9)

    def give(cs, iid, n):
        return int(Inv.give(cs, iid, n))
    give(TB, "Skyy_Ench_Wheat", 8)
    c0 = coins["bal"]
    r = str(Core.buyIsland(ou, OWNER, FK, 1, TB))
    po = St.get(OWNER)
    K.check(r.startswith("+Island 2 bought: a Small Wheat island in slot 2") and coins["bal"] == c0 - 19000 and count(TB, "Skyy_Ench_Wheat") == 0
            and str(po.getProperty("farming.i1.type")) == "wheat" and str(po.getProperty("farming.i1.size")) == "1" and str(po.getProperty("farming.i1.stored")) == "0"
            and str(po.getProperty("farming.i1.last")) == "1790000000000" and po.getProperty("farming.i1.totems") is None,
            "X8 island 2: 19,000 coins + 8 Enchanted Wheat taken, slot 2 = a Small Wheat island, no totems: %s" % r)
    fb = open(os.path.join(L["sd"], OWNER + ".properties"), encoding="latin-1").read()
    K.check("farming.i1.type=wheat" in fb, "X8 saved to disk")
    c1 = coins["bal"]
    K.check(str(Core.buyIsland(ou, OWNER, FK, 1, TB)).startswith("=That slot already has an island") and coins["bal"] == c1, "X8 the same slot twice: nothing taken (no dupes)")
    K.check(str(Core.buyIsland(ou, OWNER, FK, 0, TB)).startswith("=That slot already has"), "X8 the starter slot is not for sale")
    give(TB, "Skyy_Ench_Wheat", 10)
    r = str(Core.buyIsland(ou, OWNER, FK, 2, TB))
    K.check(r.startswith("-You need 16 Enchanted Wheat (you have 10)") and count(TB, "Skyy_Ench_Wheat") == 10 and coins["bal"] == c1 and not bool(Mth.hasIsland(FK, St.get(OWNER), 2)),
            "X8 island 3 needs 16 Enchanted: refused, nothing taken: %s" % r)
    give(TB, "Skyy_Ench_Wheat", 6)
    coins["fail"] = True
    r = str(Core.buyIsland(ou, OWNER, FK, 2, TB))
    coins["fail"] = False
    K.check(r.startswith("-The coins could not be taken - your Enchanted Wheat is back") and count(TB, "Skyy_Ench_Wheat") == 16 and coins["bal"] == c1
            and not bool(Mth.hasIsland(FK, St.get(OWNER), 2)), "X8 coins refused: the items come back, no island: %s" % r)
    St.FAIL_TEST = True
    r = str(Core.buyIsland(ou, OWNER, FK, 2, TB))
    St.FAIL_TEST = False
    K.check(r.startswith("-It could not be saved - your Enchanted Wheat and coins are back") and count(TB, "Skyy_Ench_Wheat") == 16 and coins["bal"] == c1
            and not bool(Mth.hasIsland(FK, St.get(OWNER), 2)), "X8 a refused save: items + coins back, no island (memory restored): %s" % r)
    nocoin = L["fns"].remove("coins:fn:take")
    r = str(Core.buyIsland(ou, OWNER, FK, 2, TB))
    L["fns"].put("coins:fn:take", nocoin)
    K.check(r.startswith("-The coins could not be taken") and count(TB, "Skyy_Ench_Wheat") == 16, "X8 no SkyyCoins: refused, items back")
    r = str(Core.buyIsland(mu, OWNER, FK, 2, TB))
    K.check(r.startswith("-Only the island owner") and count(TB, "Skyy_Ench_Wheat") == 16, "X8 a co-op member cannot buy: %s" % r)
    K.check(str(Core.buyIsland(vu, OWNER, FK, 2, TB)).startswith("-Only the island owner and co-op members"), "X8 a visitor cannot buy")
    K.check(str(Core.buyIsland(ou, OWNER, FK, 7, TB)).startswith("-Pick a slot first"), "X8 a bad slot is refused")
    paid = []
    for slot, nth in ((2, 3), (5, 4), (3, 5), (4, 6)):
        give(TB, "Skyy_Ench_Wheat", ISL_QTY[nth] - count(TB, "Skyy_Ench_Wheat") if count(TB, "Skyy_Ench_Wheat") < ISL_QTY[nth] else 0)
        cb, ib = coins["bal"], count(TB, "Skyy_Ench_Wheat")
        r = str(Core.buyIsland(ou, OWNER, FK, slot, TB))
        paid.append((nth, cb - coins["bal"], ib - count(TB, "Skyy_Ench_Wheat"), r.startswith("+Island %d bought" % nth)))
    K.eq(paid, [(3, 57000, 16, True), (4, 170000, 32, True), (5, 510000, 64, True), (6, 1535000, 128, True)],
         "X8 islands 3-6 in any slot: 57,000 / 170,000 / 510,000 / 1,535,000 coins + 16 / 32 / 64 / 128 Enchanted Wheat")
    K.eq([bool(Mth.hasIsland(FK, St.get(OWNER), i)) for i in range(6)], [True] * 6, "X8 all six slots filled")
    K.check(str(Core.buyIsland(ou, OWNER, FK, 3, TB)).startswith("=That slot already has"), "X8 nothing left to buy")
    clog = open(os.path.join(os.path.dirname(L["sd"]), "collect.log"), encoding="utf-8").read()
    K.check("farming buy island 2 in slot 2 paid 19000 coins + 8 Skyy_Ench_Wheat" in clog and "SAVE FAILED" in clog and "coins refused" in clog, "X8 collect.log names every purchase / refund")
    # Mining: coins only when the item row is empty; a member of another profile
    St.LOCK.lock()
    try:
        po = St.get(OWNER)
        Mth.starter(MKD, po, L["JLong"](1790000000000))
        St.save(OWNER, po)
    finally:
        St.LOCK.unlock()
    IT = list(Cfg.ISL_ITEM)
    IT[MKD] = ""
    Cfg.ISL_ITEM = JArray(JString)(IT)
    TC = inv(3)
    cb = coins["bal"]
    r = str(Core.buyIsland(ou, OWNER, MKD, 3, TC))
    K.check(r.startswith("+Island 2 bought: a Small Copper island in slot 4") and cb - coins["bal"] == 19000 and str(St.get(OWNER).getProperty("mining.i3.type")) == "copper",
            "X8 an empty island.item row = coins only (Mining island 2): %s" % r)
    Cfg.ISL_ITEM = JArray(JString)(ISL_ITEM)
    br.put("coins:fn:curve", PyFn(lambda a: JClass("java.lang.Double")(1.0)))
    K.eq(int(Cfg.islandCoins(2)), 8300, "X8 with SkyyCoins' curve (stub 1.0): island 2 = 8,300")
    br.remove("coins:fn:curve")

    # ---------------- X9 THE PAGE (Islands tab)
    Page = L["ShPage"]
    import json as _json
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    CPk = JClass("com.hypixel.hytale.protocol.packets.interface_.CustomPage")
    LIFE = JClass("com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime")
    ISL = "skyy-island-" + OWNER

    def build(pg):
        b, ev = UCB(), UEB()
        pg.build(None, b, ev, None)
        cmds, evs = b.getCommands(), ev.getEvents()
        appended, sets = [], {}
        for c in cmds:
            t_ = str(c.type)
            if "Append" in t_:
                appended.append(str(c.text) if c.text is not None else "")
            if c.selector is not None and c.data is not None and t_ == "Set":
                v_ = str(c.data)
                try:
                    v_ = str(_json.loads(v_).get("0", v_))
                except Exception:
                    pass
                sets[str(c.selector)] = v_
        mk = "\n".join(appended)
        binds = [str(e.selector) for e in evs]
        unbound = [x for x in binds if (x.lstrip("#") + " ") not in mk.replace("{", " ").replace(";", " ") and (x.lstrip("#") + " {") not in mk]
        size = int(CPk("SkyySh", True, True, LIFE.CanDismiss, cmds, evs).computeSize())
        return dict(binds=binds, mk=mk, sets=sets, unbound=unbound, size=size)
    # a fresh Orchard shard (starter only) for the page
    St.LOCK.lock()
    try:
        po = St.get(OWNER)
        for kk in list(po.stringPropertyNames()):
            if str(kk).startswith("orchard.i"):
                po.remove(kk)
        Mth.starter(OK_, po, L["JLong"](1790000000000))
        po.setProperty("orchard.placed", ISL + "|9|129|9")       # the portal stands on the owner's island (the page opens there)
        po.setProperty("combat.placed", ISL + "|12|129|12")
        St.save(OWNER, po)
    finally:
        St.LOCK.unlock()
    TP = inv(9, 9)
    give(TP, "Skyy_Ench_Apple", 8)
    Page.TEST_INV = TP
    pg = Page(ou, ISL)
    pg.kind = OK_
    pg.tab = 2
    pg.sel = 1
    res = build(pg)
    txt = " | ".join(str(x) for x in pg.iTx)
    K.check("#SkyyShIBuy" in res["binds"] and "#SkyyShIGrow" not in res["binds"] and not res["unbound"] and bool(pg.bCan),
            "X9 owner, an empty slot: Buy island bound (no Grow), every binding has its element")
    K.check("Buy a Small Apple island here." in txt and "Island 2 of 6 - each next one costs x3." in txt and "19,000 coins (you: " in txt
            and "8 Enchanted Apple (you: 8)" in txt, "X9 the side panel shows the price: %s" % txt)
    pg.sel = 0
    res0 = build(pg)
    K.check("#SkyyShIGrow" in res0["binds"] and "#SkyyShIBuy" not in res0["binds"], "X9 the starter slot: Grow, no Buy")
    pm = Page(mu, ISL)
    pm.kind = OK_
    pm.tab = 2
    pm.sel = 1
    K.check("#SkyyShIBuy" not in build(pm)["binds"], "X9 co-op: no Buy island")
    K.eq(res["sets"].get("#SkyyShIMapT.Text"), "Pick a slot to see its island, or an empty slot to buy one. Islands grow in place.", "X9 the map caption")
    pg.sel = 1
    cb = coins["bal"]
    r = str(pg.act("ibuy", None, None))
    K.check(r.startswith("+Island 2 bought: a Small Apple island in slot 2") and cb - coins["bal"] == 19000 and count(TP, "Skyy_Ench_Apple") == 0,
            "X9 the ibuy click buys it (one packet per click: act + rebuild): %s" % r)
    pg.sel = 2
    build(pg)
    txt = " | ".join(str(x) for x in pg.iTx)
    K.check("Island 3 of 6" in txt and "57,000 coins" in txt and "16 Enchanted Apple (you: 0)" in txt, "X9 the next empty slot shows island 3's price: %s" % txt)
    K.check("each next one costs x3." in txt, "X9 island 3 still names the next step: %s" % txt)
    St.LOCK.lock()
    try:
        po = St.get(OWNER)
        for s_ in (2, 3, 4):
            for f_ in ("type", "size", "stored", "last"):
                v_ = po.getProperty("orchard.i1." + f_)
                if v_ is not None:
                    po.setProperty("orchard.i%d.%s" % (s_, f_), str(v_))
    finally:
        St.LOCK.unlock()
    pg.sel = 5
    build(pg)
    txt6 = " | ".join(str(x) for x in pg.iTx)
    K.check("Island 6 of 6 - the last one." in txt6 and "each next one" not in txt6 and bool(pg.bCan),
            "X9 island 6: no 'each next one' clause (there is none): %s" % txt6)
    St.LOCK.lock()
    try:
        po = St.get(OWNER)
        for s_ in (2, 3, 4):
            for f_ in ("type", "size", "stored", "last", "totems"):
                po.remove("orchard.i%d.%s" % (s_, f_))
    finally:
        St.LOCK.unlock()
    K.check(res["size"] < 1500000, "X9 the packet size is sane (%d)" % res["size"])
    # no shard yet: the empty slot says how to get it
    keys[MEMBER] = MEMBER
    pn = Page(ou, ISL)
    pn.kind = CK
    pn.tab = 2
    pn.sel = 1
    St.LOCK.lock()
    try:
        po = St.get(OWNER)
        for kk in list(po.stringPropertyNames()):
            if str(kk).startswith("combat.i"):
                po.remove(kk)
    finally:
        St.LOCK.unlock()
    rn = build(pn)
    txtn = " | ".join(str(x) for x in pn.iTx)
    K.check("#SkyyShIBuy" not in rn["binds"] and "It is the reward for class level 20." in txtn and "class level 20" in str(pn.sum2),
            "X9 no Combat shard yet: no Buy, the panel + strip name class level 20: %s" % txtn)
    Page.TEST_INV = None
    K.save()


def run_live46(out, jar, scratch, home):
    from jpype import JClass
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    K = HK.Child(out)
    Cfg, path = T42.kit_home(home)
    M4, M5, M6 = JClass(PKG + "ShMig044"), JClass(PKG + "ShMig045"), JClass(PKG + "ShMig046")
    t0 = T42.tree(home)
    rs = []
    for s in (1, 2):
        T42.kit_home(home)
        rs.append((str(Cfg.migCoop(Cfg.FILE)), str(M4.run(Cfg.FILE)), str(M5.run(Cfg.FILE)), str(M6.run(Cfg.FILE))))
        r = str(Cfg.loadCfg(True))
        K.check(not r.startswith("default"), "D start %d: the live config is read" % s)
        K.check(all(str(Cfg.CRAFT[i]) == "" for i in range(len(Cfg.CRAFT_ID)) if str(Cfg.CRAFT_ID[i]) in SHARDS), "D start %d: the six shard recipes are off" % s)
        K.check([int(x) for x in Cfg.LV20] == [20] * 6 and int(Cfg.islandCoins(2)) == PRICES[2], "D start %d: lv20 20, island 2 = 19,000 (rows missing = defaults)" % s)
    t1 = T42.tree(home)
    ch = sorted(k for k in set(t0) | set(t1) if t0.get(k) != t1.get(k))
    K.check(all(k == "config.properties" or k.startswith("config-history/") or k == "config-changes.log" for k in ch) and "config.properties" in ch,
            "D start 1 changed only config.properties (+ History, change log): %s" % ch)
    K.check(rs[0][3] != "" and rs[1] == ("", "", "", ""), "D start 1 ran ShMig046, start 2: no update ran")
    K.save()


EXPECT = {   # checked by hand 2026-10-23: the version / default texts (CfgFile, CfgFn, CfgRows, ShStore's file header), the new ShCfg rows + island
            # prices, ShCore (buy island, the "reward for <skill> level 20" texts in gate / benchStart / craftGate), the page (Buy island,
            # the empty-slot panel, the bench's off shard recipes), ShTick (the 5 s level 20 scan), setup (ShMig046)
    "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],
    "ShCfg": ["+f CURVE_LV", "+f CURVE_X", "+f DEF_ISL_ITEM", "+f ISL_BASE", "+f ISL_ITEM", "+f ISL_LV", "+f ISL_QTY", "+f ISL_STEP", "+f LV20",
              "+m curve", "+m curveBuiltin", "+m islandCoins", "+m islandCoinsAt", "+m islandItem", "+m islandQty", "+m round7", "~<clinit>",
              "~m loadCfg", "~m writeDefaults"],
    "ShInv": ["+m hasRoom"],   # fix (critic shards046 #1)
    "ShCore": ["+m buyIsland", "+m buyIsland0", "+m purchaseN", "~m benchStart", "~m craftGate", "~m gate"],
    "ShPage": ["+f bCan", "~m act", "~m buildFull", "~m fill", "~m fillBenchCraft"],
    "ShStore": ["~m migrate", "~m save"], "ShTick": ["~m run"], "SkyyShardsPlugin": ["~m setup"]}

if __name__ == "__main__":
    HK.run(name="SkyyShards", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=["ShMig046", "ShLv20"],
           phases=[("static", run_static), ("config", run_config), ("mig", run_mig), ("exec", run_exec), ("live", run_live46)],
           script=__file__, live=(LIVE_SH, "mods/Skyy_SkyyShards"))
