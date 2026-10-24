"""Harness for SkyyShards 0.4.8 (the starter archipelago round R1: shard doors + locks, level 20 grants off, one island per tier, Size + 3
sub-upgrades, the cheap-first ladder, manual first + Automation, Mining copper caves, the map migration; tools/shards_0_4_8_patch.py).
Build first:
    python tools/shards_0_4_8_patch.py && python SkyyShards/build_skyyshards_0.4.8.py
    python SkyyShards/test_skyyshards_0.4.8.py [--keep]

  S    static   the patch re-runs to identical bytes; no new registerSystem / registerCommand; ShMig048 + ShIsl + ShDoor written; setup order
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.4.7 -> 0.4.8: exactly the planned members differ (EXPECT)
  K    config   EXECUTED loadCfg: a fresh file (the new rows + the 0.4.8 marker, lv20 = 0, the ladder, storage on the ladder), hand edits + junk
                lists, the Server Setup rows
  M    mig      ShMig048 on a scratch COPY of the live config + a 0.4.7-default file: the 11 lines, History, change log, run twice = once,
                hand-edited lines kept, a fresh file untouched
  P    players  the map migration on real file copies: a 0.4.6 profile with 3 Farming islands (slots 0, 2, 3) + Mining Small / Medium + stored
                items -> Automated, wheat / lettuce / carrot, legacy items paid out as the OLD item at Collect, Mining Amount 2 / 1, Farming
                Amount 5; the History copy byte-equal; load twice = once; a refused copy / save = untouched
  X    exec     EVERY NEW CODE PATH on real SimpleItemContainers: shard:fn:door (+ / = / moved by a reset / kept beside a placed portal / bad
                calls), the starter door cannot be picked up, the LOCK (enter, collect, buy refused below level 5, open at 5, lock 0 = open,
                unknown level = open), the manual factor (0.4 / 0.7 / 1.0), the 2 h offline cap vs 3 days, seed use + the store, buy the next
                tier (T2 Lettuce 3,500 + 128 Lettuce + 32 seeds, in order only, refunds), the 3 sub-upgrades (40 / 80 / 120 / 200 / 280 + items,
                5/5 max), Grow only at 5/5/5 then 0/0/0 + output never lower, Automation (550 + 128 Wheat, once), seeds give / take back,
                the ladder costs at every tier = tools/balance_model.py, the page (Islands tab ladder boxes, buttons bound, lock card)
  G    geometry the region on a block map: the Farming starter (8 Eternal + tilled + manual farm cells), replant from the store + the scan
                saved, the Mining cave (27 .. 95 / 95 .. 250 / 250 .. 476 ore cells, opening, pads on the floor), the old flat Mining island
                rebuilt once (old nodes cleared, never fewer nodes), decorations / pools per level, a second paint touches nothing
  D    live     START TWICE on a scratch COPY of NewBetaTest's Skyy_SkyyShards: ShMig048 once, the real profile migrated once (its Mining
                island = a cave with 55 ore cells >= 16), a second start writes nothing
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util, subprocess, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import balance_model as BM

VERSION = "0.4.8"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "archi1", "h")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyShards-%s.jar" % VERSION)]
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyShards-0.4.7.jar")
GEN = os.path.join(HERE, "build_skyyshards_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyshards_0.4.7.py")
PATCH = os.path.join(ROOT, "tools", "shards_0_4_8_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.shards."
_argv = list(sys.argv)
_spec = importlib.util.spec_from_file_location("test_skyyshards_0_4_7", os.path.join(HERE, "test_skyyshards_0.4.7.py"))
T47 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T47)
sys.argv[:] = _argv
T46 = T47.T46
T46.JAR = JAR
T47.JAR = JAR
T42 = T46.T42
OWNER, MEMBER = T46.OWNER, T46.MEMBER
KINDS = ["Mining", "Foraging", "Farming", "Ranching", "Orchard", "Combat"]
KK = [k.lower() for k in KINDS]
MKD, FOK, FK, RK, OK_, CK = 0, 1, 2, 3, 4, 5
OLD_UP = "1:10,2:25,3:50,5:100"
NEW_UP = "1:4,2:16,4:40,8:100"
MIG = [("lv20.%s" % k, "20", "0") for k in KK] + [("totem.upCost", OLD_UP, NEW_UP)] + \
      [("storage.coins.%d" % n, o, w) for n, o, w in ((2, "43500", "14500"), (3, "305000", "105000"), (4, "1085000", "375000"), (5, "3880000", "1260000"))]
MK = "skyyshards-0.4.8-map"
NL_ = chr(10)
LADDER = [BM.p7_round(h * BM.p7_H_at(l)) for l, h in zip([3, 5, 8, 12, 15, 20, 28, 35, 45, 55], [0.05, 0.1, 0.2, 0.35, 0.5, 0.75, 1, 1.5, 2, 3])]
COIN_H = BM.p7_H_at(10)
LIVE = lambda lvl: BM.p7_curve_from_text(BM.P7_CURVE_TEXT, lvl)   # what the game reads (SkyyCoins coins.curve / the built-in copy)
LADDER_LIVE = [BM.p7_round(h * COIN_H * LIVE(l)) for l, h in zip([3, 5, 8, 12, 15, 20, 28, 35, 45, 55], [0.05, 0.1, 0.2, 0.35, 0.5, 0.75, 1, 1.5, 2, 3])]
SUBH = [[0.01, 0.02, 0.03, 0.05, 0.07], [0.08, 0.1, 0.13, 0.16, 0.2], [0.25, 0.3, 0.4, 0.5, 0.6]]


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyShards 0.4.8 - build script') and g.count('VERSION = "0.4.8"\n') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.check("ALLC = [cfg, smig, smig45, smig46, smig48, st, knd, isl48, lv," in g and "[admc, gfn, dfn, pl]" in g, "S ShMig048 + ShIsl + ShDoor written out")
    K.check('b.put("shard:fn:door", new @PKG@.ShDoor());' in g and 'b.remove("shard:fn:door");' in g, "S shard:fn:door registered + removed at shutdown")
    HK.jvm([B.SERVER_JAR, JAR, B.JAVASSIST], verify=False)
    calls = T42.setup_calls(jar)
    K.check(calls.index("ShMig046.run") < calls.index("ShMig048.run") < calls.index("ShCfg.loadCfg") < calls.index("CfgPub.start"),
            "S setup order: ShMig046, ShMig048, loadCfg, CfgPub.start")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def add_items(ids):
    """more ids into the fixture's bare Item store (T04.item_store's map)"""
    from jpype import JClass
    U = T46.T04.unsafe()
    ItemC = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    fs = ItemC.class_.getDeclaredField("ASSET_STORE")
    fs.setAccessible(True)
    store = fs.get(None)
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    fa = AS.class_.getDeclaredField("assetMap")
    fa.setAccessible(True)
    amap = fa.get(store)
    mf = amap.getClass().getDeclaredField("assetMap")
    mf.setAccessible(True)
    m = mf.get(amap)
    for iid, mx in ids:
        if m.get(iid) is not None:
            continue
        it_ = U.allocateInstance(ItemC.class_)
        T46.T04.setf(it_, ItemC.class_, "maxStack", JClass("java.lang.Integer")(mx).intValue())
        T46.T04.setf(it_, ItemC.class_, "id", iid)
        m.put(iid, it_)


def _setup(scratch, K):
    L = T46._fixture(scratch, K)
    from jpype import JClass
    for n in ("ShIsl", "ShDoor", "ShGeo", "ShFill", "ShMig048", "ShPageFn", "ShWorld2"):
        L[n] = JClass(PKG + n)
    Isl = L["ShIsl"]
    ids = set()
    for t in range(int(Isl.TN)):
        for a in (Isl.PROD, Isl.ENCH, Isl.SEED, Isl.ESEED, Isl.SMELT, Isl.SMELTE):
            if str(a[t]):
                ids.add(str(a[t]))
    ids |= {"Wood_Oak_Trunk", "Rock_Stone_Cobble", "Skyy_Ench_Oak", "Skyy_Ench_Cobblestone", "Ingredient_Water_Essence", "Tool_Capture_Crate", "Skyy_Ench_Wheat"}
    add_items([(i, 100) for i in sorted(ids)])
    return L


def _fill(L, cs, items):
    for iid, n in items:
        left = n
        while left > 0:
            q = min(100, left)
            for c in cs:
                tr = c.addItemStack(L["IS"](iid, q))
                if tr is not None:
                    break
            left -= q


def run_config(out, jar, scratch, _home):
    from jpype import JClass
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    K = HK.Child(out)
    home = os.path.join(scratch, "k1", "mods", "Skyy_SkyyShards")
    os.makedirs(home)
    Cfg, path = T42.kit_home(home)
    Cfg.loadCfg(True)
    t = open(os.path.join(home, "config.properties"), "rb").read().replace(b"\r\n", b"\n").decode("latin-1")
    lines = t.split("\n")
    K.check(t.count(MK) == 1 and all(("lv20.%s=0" % k) in lines for k in KK) and ("totem.upCost=" + NEW_UP) in lines
            and "storage.coins.2=14500" in lines and "storage.coins.5=1260000" in lines, "K a fresh file: marker, lv20 0, the new upCost, storage on the ladder")
    want = ["shard.lock.%s=5" % k for k in KK] + ["shard.lock.skill.farming=Farming", "shard.lock.skill.combat=class", "shard.lock.skill.ranching=Ranching",
            "shard.manualPct=50", "shard.manualOfflineSec=7200", "shard.seedStoreMax=640", "shard.seedReturnPct=50", "shard.itemsPerSapling=20",
            "up.levels=3,5,8,12,15,20,28,35,45,55", "up.hours=0.05,0.1,0.2,0.35,0.5,0.75,1,1.5,2,3", "up.auto.step=2",
            "up.auto.items.farming=Plant_Crop_Wheat_Item:128", "isl.buyHours=0.5", "isl.subHours.small=0.01,0.02,0.03,0.05,0.07",
            "isl.growHours.medium=0.15", "isl.buyItems.farming=raw:128,seed:32", "isl.amount.pct=60,68,76,84,92,100", "isl.deco.pct=0.5",
            "cave.amount.pct=8,12,16,20,24,28"]
    K.eq([w for w in want if w not in lines], [], "K a fresh file holds every 0.4.8 row")
    K.eq([int(x) for x in Cfg.LOCK], [5] * 6, "K LOCK read")
    K.eq([int(x) for x in Cfg.LV20], [0] * 6, "K LV20 = 0 (the level 20 grants are off)")
    K.eq(str(Cfg.UP_COST), NEW_UP, "K UP_COST")
    open(os.path.join(home, "config.properties"), "a", encoding="latin-1").write(
        "\nshard.lock.farming=0\nshard.lock.skill.mining=\nup.levels=1,2,junk\nisl.subHours.small=0.5\nisl.amount.pct=10,20\nshard.manualPct=900\n"
        "cave.amount.pct=1,2,3,4,5,6,7\nisl.mat.deco=Rock_Stone:1\n")
    Cfg.loadCfg(False)
    K.check(int(Cfg.LOCK[FK]) == 0 and str(Cfg.LOCK_SKILL[MKD]) == "Mining" and [int(x) for x in Cfg.UP_LV] == [3, 5, 8, 12, 15, 20, 28, 35, 45, 55]
            and [float(x) for x in Cfg.SUB_H][:5] == [0.5] * 5 and [int(x) for x in Cfg.AMT_PCT] == [10, 20, 20, 20, 20, 20]
            and int(Cfg.MAN_PCT) == 100 and [int(x) for x in Cfg.CAVE_PCT] == [8, 12, 16, 20, 24, 28] and str(Cfg.MAT_DECO) == "Rock_Stone:1",
            "K hand edits: lock 0, empty skill = default, a junk list = the default (+ WARN), one number repeats, short list repeats its last, clamp 100, 7 numbers = default")
    rows = dict((str(r[0]), [str(x) for x in list(r)]) for r in JClass(PKG + "CfgRows").header()[7])
    K.check(all(("shard.lock." + k) in rows and ("shard.lock.skill." + k) in rows and ("up.auto.items." + k) in rows and ("isl.buyItems." + k) in rows for k in KK)
            and all(x in rows for x in ("shard.manualPct", "up.levels", "up.hours", "isl.subHours.large", "isl.growHours.large", "isl.mat.grow", "cave.amount.pct", "isl.irrigation.pct")),
            "K the Server Setup rows exist")
    K.eq(rows["shard.lock.combat"][4], "5", "K a lock row's default")
    K.save()


def run_mig(out, jar, scratch, _home):
    from jpype import JClass
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    K = HK.Child(out)
    Mig = JClass(PKG + "ShMig048")
    live = os.path.join(T46.LIVE_SH, "config.properties")
    A_ = open(live, "rb").read() if os.path.isfile(live) else None
    K.check(A_ is not None, "M the live NewBetaTest config.properties exists (read only)")
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

    def props(b_):
        P_ = JClass("java.util.Properties")()
        P_.load(JClass("java.io.ByteArrayInputStream")(b_))
        return dict((str(k), str(P_.getProperty(k))) for k in P_.stringPropertyNames())

    def hist(home):
        hd = os.path.join(home, "config-history")
        return [open(os.path.join(hd, n), "rb").read() for n in sorted(os.listdir(hd)) if n.endswith(".bak")] if os.path.isdir(hd) else []

    def chg(home):
        f = os.path.join(home, "config-changes.log")
        return [l.split("\t") for l in open(f, encoding="utf8").read().splitlines()] if os.path.isfile(f) else []
    if A_ is not None:
        home, f, Cfg, path = world(A_)
        r = str(Mig.run(path(f)))
        b1 = open(f, "rb").read()
        pa, pb = props(A_), props(b1)
        moved = [k for k, o, w in MIG if pa.get(k) is not None and pa.get(k).replace(" ", "") == o]
        K.check(all(pb[k] == dict((x[0], x[2]) for x in MIG)[k] for k in moved) and all(pb[k] == pa[k] for k in pa if k not in moved) and len(pb) == len(pa),
                "M the live config: %d lines on their old default moved (%s), every other line the same: %s" % (len(moved), moved, r[:200]))
        K.check(b1.count(MK.encode()) == 1 and (b"\r\n" in A_) == (b"\r\n" in b1), "M the marker once, line endings kept")
        K.check(any(h == A_ for h in hist(home)) and len([c for c in chg(home) if len(c) > 6 and c[1] == "SkyyShards 0.4.8"]) == len(moved),
                "M History holds the old bytes, one change-log line per moved line")
        r2 = str(Mig.run(path(f)))
        K.check(r2 == "" and open(f, "rb").read() == b1, "M run twice = once (the marker)")
    # a 0.4.7-default file with hand edits
    old = "".join("%s=%s\n" % (k, o) for k, o, w in MIG).replace("lv20.combat=20", "lv20.combat=30").replace("storage.coins.3=305000", "storage.coins.3 = 305000")
    home, f, Cfg, path = world(old.encode("latin-1"))
    r = str(Mig.run(path(f)))
    p2 = props(open(f, "rb").read())
    K.check(p2["lv20.farming"] == "0" and p2["lv20.combat"] == "30" and p2["totem.upCost"] == NEW_UP and p2["storage.coins.3"] == "105000"
            and p2["storage.coins.5"] == "1260000" and "kept - an admin changed it" in r, "M hand-edited lv20.combat=30 kept (INFO), a spaced line still matched, the rest moved: %s" % r[-160:])
    home, f, Cfg, path = world(None)
    Cfg.loadCfg(True)
    b0 = open(f, "rb").read()
    K.check(str(Mig.run(path(f))) == "" and open(f, "rb").read() == b0, "M a fresh 0.4.8 file: nothing to do (its marker)")
    K.save()


def _prof(sd, k, lines):
    open(os.path.join(sd, k + ".properties"), "w", encoding="latin-1").write("".join("%s=%s\n" % kv for kv in lines))


def run_players(out, jar, scratch, _home):
    K = HK.Child(out)
    L = _setup(os.path.join(scratch, "p"), K)
    St, Isl, Mth, Core, inv, count, UUID = (L[n] for n in ("ShStore", "ShIsl", "ShMath", "ShCore", "inv", "count", "UUID"))
    sd = L["sd"]
    now = 1790000000000
    k = "0a0a0a0a-1111-2222-3333-000000000001"
    L["keys"][k] = k
    _prof(sd, k, [("v", "1"), ("forms", "1"), ("farming.storage", "1"), ("farming.placed", "skyy-island-%s|1|129|1" % k),
                  ("farming.i0.type", "wheat"), ("farming.i0.size", "2"), ("farming.i0.last", str(now)), ("farming.i0.stored", "40"), ("farming.i0.totems", "harvest_spirit:1"),
                  ("farming.i2.type", "wheat"), ("farming.i2.size", "1"), ("farming.i2.last", str(now)), ("farming.i2.stored", "30"),
                  ("farming.i3.type", "wheat"), ("farming.i3.size", "1"), ("farming.i3.last", str(now)), ("farming.i3.stored", "0"),
                  ("mining.i0.type", "copper"), ("mining.i0.size", "1"), ("mining.i0.last", str(now)), ("mining.i0.stored", "5"),
                  ("mining.i1.type", "copper"), ("mining.i1.size", "2"), ("mining.i1.last", str(now))])
    b0 = open(os.path.join(sd, k + ".properties"), "rb").read()
    p = St.get(k)
    g = lambda key: str(p.getProperty(key)) if p.getProperty(key) is not None else None
    K.check(g("map.done") == "1" and g("farming.auto") == "1" and g("mining.auto") == "1" and g("ranching.auto") is None, "P the shards with islands are Automated (grandfathered); the others not")
    K.eq([g("farming.i0.type"), g("farming.i2.type"), g("farming.i3.type")], ["wheat", "lettuce", "carrot"], "P 0.4.6's extra Wheat islands -> Lettuce, Carrot (slot order)")
    K.eq([g("farming.i2.legacy"), g("farming.i2.stored"), g("farming.i3.legacy"), g("farming.i0.legacy")], ["Plant_Crop_Wheat_Item:30", "0", None, None],
         "P the retyped island's stored wheat waits as legacy (no stock = no legacy); island 1 untouched")
    K.eq([g("mining.i1.type"), g("mining.i0.amt"), g("mining.i1.amt"), g("farming.i0.amt"), g("farming.i2.amt")], ["iron", "2", "1", "5", "5"],
         "P Mining slot 2 -> Iron; Mining Small -> Ore Amount 2, Medium -> 1; Farming Amount 5")
    snap = os.path.join(sd, "history", "map", k + ".pre-0.4.8.properties")
    K.check(os.path.isfile(snap) and open(snap, "rb").read() == b0, "P the History copy = the old file, byte for byte")
    K.check("map migration (SkyyShards 0.4.8) " + k in open(os.path.join(sd, "..", "collect.log"), encoding="utf8").read(), "P one collect.log line with the Undo")
    b1 = open(os.path.join(sd, k + ".properties"), "rb").read()
    St.CACHE.clear()
    p = St.get(k)
    K.check(open(os.path.join(sd, k + ".properties"), "rb").read() == b1 and str(p.getProperty("farming.i2.type")) == "lettuce", "P load twice = once")
    # the legacy wheat comes out as WHEAT at Collect, the lettuce island's own stock as lettuce
    u = UUID.fromString(k)
    cs = inv(18, 18)
    p.setProperty("farming.i2.stored", "7")
    r = str(Core.collect(u, k, FK, 2, cs))
    K.check(count(cs, "Plant_Crop_Wheat_Item") == 30 and count(cs, "Plant_Crop_Lettuce_Item") == 7 and p.getProperty("farming.i2.legacy") is None,
            "P Collect pays the legacy wheat as wheat (+ the island's lettuce): %s" % r)
    # a refused copy: the file + memory untouched
    k2 = "0a0a0a0a-1111-2222-3333-000000000002"
    _prof(sd, k2, [("v", "1"), ("forms", "1"), ("orchard.i0.type", "apple"), ("orchard.i0.size", "1"), ("orchard.i1.type", "apple"), ("orchard.i1.size", "1")])
    hd = os.path.join(sd, "history", "map")
    blk = os.path.join(hd, k2 + ".pre-0.4.8.properties.tmp")
    os.makedirs(blk)                                   # a folder where the copy's temp file goes = the copy fails
    b2 = open(os.path.join(sd, k2 + ".properties"), "rb").read()
    p2 = St.get(k2)
    K.check(p2.getProperty("map.done") is None and str(p2.getProperty("orchard.i1.type")) == "apple" and open(os.path.join(sd, k2 + ".properties"), "rb").read() == b2,
            "P a refused History copy: nothing migrated, the file untouched")
    os.rmdir(blk)
    St.CACHE.clear()
    St.FAIL_TEST = True
    p2 = St.get(k2)
    St.FAIL_TEST = False
    K.check(p2.getProperty("map.done") is None and str(p2.getProperty("orchard.i1.type")) == "apple", "P a refused save: memory put back (tried again next load)")
    St.CACHE.clear()
    p2 = St.get(k2)
    K.check(str(p2.getProperty("orchard.i1.type")) == "berries" and str(p2.getProperty("map.done")) == "1", "P ... and the next load migrates it")
    # a profile without islands: only the marker in memory, nothing written
    k3 = "0a0a0a0a-1111-2222-3333-000000000003"
    _prof(sd, k3, [("v", "1")])
    b3 = open(os.path.join(sd, k3 + ".properties"), "rb").read()
    p3 = St.get(k3)
    K.check(str(p3.getProperty("map.done")) == "1" and open(os.path.join(sd, k3 + ".properties"), "rb").read() == b3, "P no islands: the marker rides along, no write")
    K.save()


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JInt, JString, JArray, JObject
    K = HK.Child(out)
    L = _setup(os.path.join(scratch, "x"), K)
    St, Isl, Mth, Core, Door, Cfg, Tot, Page, Role = (L[n] for n in ("ShStore", "ShIsl", "ShMath", "ShCore", "ShDoor", "ShCfg", "ShTotem", "ShPage", "ShRole"))
    inv, count, UUID, coins, PyFn, levels = (L[n] for n in ("inv", "count", "UUID", "coins", "PyFn", "levels"))
    ou = UUID.fromString(OWNER)
    W = "skyy-island-" + OWNER
    now = 1790000000000
    Core.NOW_TEST = now
    # ---- shard:fn:door
    r = str(Door().apply(JArray(JObject)([ou, JString(OWNER), JString("farming"), JString(W), JInt(29), JInt(129), JInt(-31)])))
    p = St.get(OWNER)
    g = lambda key: str(p.getProperty(key)) if p.getProperty(key) is not None else None
    K.check(r == "+" and g("farming.placed") == W + "|29|129|-31" and g("farming.door.starter") == W + "|29|129|-31" and g("farming.i0.type") == "wheat"
            and g("farming.i0.eternal") == "8" and g("farming.auto") is None and g("farming.i0.totems") == "harvest_spirit:1", "X door: recorded as the placed portal, a manual T1 Wheat island with 8 Eternal cells: %s" % r)
    K.eq(str(Door.door(ou, OWNER, "farming", W, 29, 129, -31)), "=", "X door twice: '='")
    W2 = W + "-r1"
    Role.WORLD_TEST = PyFn(lambda w: L["Bool"].TRUE)
    wk = {"cur": W2}
    Role.WORLDKEY_TEST = PyFn(lambda key: JString(wk["cur"]) if str(key) == OWNER else None)
    Role.OWNER_TEST = PyFn(lambda w: JString(OWNER) if str(w).startswith("skyy-island-" + OWNER) else None)
    K.check(str(Door.door(ou, OWNER, "farming", W2, 29, 129, -31)) == "+" and g("farming.placed") == W2 + "|29|129|-31", "X an island reset (new world): the door moves")
    p.setProperty("mining.placed", W2 + "|13|128|15")
    p.setProperty("mining.i0.type", "copper"); p.setProperty("mining.i0.size", "1"); p.setProperty("mining.i0.last", str(now))
    K.check(str(Door.door(ou, OWNER, "mining", W2, -43, 124, 4)) == "+kept" and g("mining.placed") == W2 + "|13|128|15" and g("mining.door.starter") == W2 + "|-43|124|4",
            "X a portal the player placed on this island stays; the door is recorded beside it")
    bad = [str(Door().apply(x)) for x in (None, JString("x"), JArray(JObject)([ou, JString(OWNER), JString("nope"), JString(W2), JInt(1), JInt(1), JInt(1)]),
                                         JArray(JObject)([ou, JString("bad"), JString("farming"), JString(W2), JInt(1), JInt(1), JInt(1)]),
                                         JArray(JObject)([ou, JString(OWNER), JString("farming"), JString("skyy-shard-" + OWNER), JInt(1), JInt(1), JInt(1)]),
                                         JArray(JObject)([ou, JString(MEMBER), JString("farming"), JString(W2), JInt(1), JInt(1), JInt(1)]))]
    K.check(all(b.startswith("-") for b in bad), "X door: bad calls refused (no array, unknown shard, bad key, a shard world, another profile's island): %s" % bad)
    cs = inv(27, 27)
    r = str(Core.pickup(ou, OWNER, FK, None, cs))
    K.check(r.startswith("-This is your starter island's own Farming Shard door") and count(cs, "Skyy_Shard_Farming") == 0, "X the starter door cannot be picked up: %s" % r)
    # ---- LOCKS
    lv = {"Farming": 2}
    Isl.LEVEL_TEST = PyFn(lambda a: JInt(lv[str(a[2])]) if str(a[2]) in lv else JInt(-1))
    m = str(Isl.lockMsg(ou, FK))
    K.eq(m, "Farming Shard - locked. Reach Farming 5 to open it. You: Farming 2.", "X lock: the card text")
    L["br"].put("island:shardguard", "1")
    r1 = str(L["ShWorld2"].enter(None, None, ou, OWNER, FK, None))
    r2 = str(Core.collect(ou, OWNER, FK, -1, cs))
    r3 = str(Core.buyAuto(ou, OWNER, FK, cs))
    K.check(r1 == "-" + m and r2 == "-" + m and r3 == "-" + m, "X locked: Enter / Collect / Automation refused with the card line (no world load): %s / %s / %s" % (r1, r2, r3))
    lv["Farming"] = 5
    K.check(Isl.lockMsg(ou, FK) is None, "X Farming 5: open")
    lv.pop("Farming")
    K.check(Isl.lockMsg(ou, FK) is None, "X unknown level (no SkyySkills): open")
    # fix2 (critic): SkyySkills is there but the level does not read (a non-number answer / a throw) = LOCKED with a try-again line
    Isl.LEVEL_TEST = PyFn(lambda a: JString("?") if str(a[2]) == "Farming" else (JInt(lv[str(a[2])]) if str(a[2]) in lv else JInt(-1)))
    mu = Isl.lockMsg(ou, FK)
    ru = str(L["ShWorld2"].enter(None, None, ou, OWNER, FK, None))
    K.check(mu is not None and "could not be read right now" in str(mu) and ru == "-" + str(mu) and int(Isl.level(ou, FK)) == -2,
            "X fix2: SkyySkills there, level unreadable (-2) = locked, Enter refused: %s" % mu)
    def _boom(a):
        raise RuntimeError("skills broke")
    Isl.LEVEL_TEST = PyFn(_boom)
    K.check(int(Isl.level(ou, FK)) == -2 and Isl.lockMsg(ou, FK) is not None, "X fix2: a throwing level read = -2, locked")
    Isl.LEVEL_TEST = PyFn(lambda a: JInt(lv[str(a[2])]) if str(a[2]) in lv else JInt(-1))
    lv["Farming"] = 1
    Cfg.LOCK = JArray(JInt)([5, 5, 0, 5, 5, 5])
    K.check(Isl.lockMsg(ou, FK) is None, "X shard.lock.farming = 0: open")
    Cfg.LOCK = JArray(JInt)([5] * 6)
    lv["Combat"] = 3
    Cfg.LOCK_SKILL = JArray(JString)(["Mining", "Foraging", "Farming", "Ranching", "Orchard", "Combat"])
    K.check("Reach Combat 5" in str(Isl.lockMsg(ou, CK)), "X another lock skill row")
    Cfg.LOCK_SKILL = JArray(JString)(["Mining", "Foraging", "Farming", "Ranching", "Orchard", "class"])
    lv["Farming"] = 9
    # ---- the manual factor (spec 7 numbers) + the offline cap + the multiplier
    K.check(abs(float(Isl.mfac(FK, p, 0, 1, 3)) - 0.4) < 1e-9, "X manual: 8 Eternal / 20 tiles in a Totem I's range = 0.4")
    p.setProperty("farming.i0.pl", "0,0,4,8")
    K.check(abs(float(Isl.mfac(FK, p, 0, 1, 3)) - 0.7) < 1e-9, "X manual: + 12 planted x 50 % = 0.7")
    r0 = float(Mth.rate(FK, p, 0, now))
    p.setProperty("farming.auto", "1")
    ra = float(Mth.rate(FK, p, 0, now))
    p.remove("farming.auto")
    K.check(abs(r0 / ra - 0.7) < 1e-9 and abs(ra - float(Cfg.RATES[0])) < 1e-9, "X the island rate: manual 0.7 x the Automated rate (= today's Harvest Spirit I %g / min)" % ra)
    K.check(int(Isl.offMs(FK, p)) == 7200000 and int(Isl.offMs(MKD, p)) == 7200000, "X manual: 2 h offline")
    p.setProperty("farming.auto", "1")
    K.check(int(Isl.offMs(FK, p)) == 259200000, "X automated: 3 days")
    p.remove("farming.auto")
    K.check(abs(float(Isl.mult(FK, p, 0, 1)) - 1.0) < 1e-12, "X a fresh Small island: x1.00")
    p.setProperty("farming.i0.size", "3"); p.setProperty("farming.i0.amt", "5"); p.setProperty("farming.i0.deco", "5"); p.setProperty("farming.i0.irr", "5")
    mx = float(Isl.mult(FK, p, 0, 3))
    K.check(abs(mx - 1.075 ** 3) < 1e-9 and mx <= 1.25, "X a maxed Large: x%.4f <= the spec's 1.25" % mx)
    for kk_, vv in (("size", "1"), ("amt", "0"), ("deco", "0"), ("irr", "0")):
        p.setProperty("farming.i0." + kk_, vv)
    # seeds: the planted part uses half a seed an item; an empty store cuts it
    p.setProperty("farming.i0.seed", "3"); p.remove("farming.i0.sacc")
    kept = int(Isl.consume(FK, p, 0, 20))
    share = float(Isl.plantedShare(FK, p, 0, 1))
    K.check(abs(share - 6.0 / 14.0) < 1e-9, "X planted share = 6 / (8 + 6) of the manual output")
    need = 20 * share * 0.5
    K.check(int(p.getProperty("farming.i0.seed")) == 3 - min(3, int(math.floor(need))) and kept <= 20, "X seeds used: %.2f needed of 3 -> store %s, kept %d" % (need, p.getProperty("farming.i0.seed"), kept))
    # fix (critic): Skyy_TotemMod_Replant halves the seed use of its worker (spec 7) - consume's multiplier + ShTotem.replantMul
    p.setProperty("farming.i0.seed", "100"); p.setProperty("farming.i0.sacc", "0")
    Isl.consume(FK, p, 0, 200)
    full_use = 100 - int(p.getProperty("farming.i0.seed"))
    wk0 = str(p.getProperty("farming.i0.totems"))
    p.setProperty("farming.i0.totems", wk0 + ":replant")
    rm = float(Tot.replantMul(FK, p, 0))
    p.setProperty("farming.i0.totems", wk0 + ",harvest_spirit:1")
    rm2 = float(Tot.replantMul(FK, p, 0))
    p.setProperty("farming.i0.totems", wk0)
    rm0 = float(Tot.replantMul(FK, p, 0))
    p.setProperty("farming.i0.seed", "100"); p.setProperty("farming.i0.sacc", "0")
    Isl.consume(FK, p, 0, 200, rm)
    half_use = 100 - int(p.getProperty("farming.i0.seed"))
    K.check(rm == 0.5 and rm2 == 1.0 and rm0 == 1.0 and full_use > 0 and abs(half_use - full_use / 2.0) <= 1, "X fix: Auto-Replant on the worker = x%.2f seeds (no mod x%.2f): %d -> %d seeds for 200 items" % (rm, rm0, full_use, half_use))
    p.setProperty("farming.i0.totems", wk0 + ":replant")
    p.setProperty("farming.i0.seed", "100"); p.setProperty("farming.i0.sacc", "0"); p.setProperty("farming.i0.last", str(now - 3600000)); p.setProperty("farming.i0.stored", "0")
    Mth.settle(FK, p, 0, now)
    used_r = 100 - int(p.getProperty("farming.i0.seed"))
    p.setProperty("farming.i0.totems", wk0)
    p.setProperty("farming.i0.seed", "100"); p.setProperty("farming.i0.sacc", "0"); p.setProperty("farming.i0.last", str(now - 3600000)); p.setProperty("farming.i0.stored", "0")
    Mth.settle(FK, p, 0, now)
    used_n = 100 - int(p.getProperty("farming.i0.seed"))
    K.check(used_n > 0 and used_r < used_n, "X fix: settle (1 h, manual) with Auto-Replant uses %d seeds, without %d" % (used_r, used_n))
    p.setProperty("farming.i0.seed", "0"); p.setProperty("farming.i0.sacc", "0")
    K.check(int(Isl.consume(FK, p, 0, 100)) < 100, "X an empty store: the planted part is not made")
    p.remove("farming.i0.pl"); p.setProperty("farming.i0.seed", "0")
    # ---- the ladder costs (spec 13) at every tier = balance_model
    cv = lambda lvl: BM.p7_curve_from_text(BM.P7_CURVE_TEXT, lvl)
    bad = []
    for s_ in range(1, 11):
        if int(Isl.coins(float(Isl.stepH(s_)), float(Cfg.curveBuiltin(int(Isl.stepLv(s_)))))) != LADDER_LIVE[s_ - 1]:
            bad.append(s_)
    K.check(not bad and LADDER == [230, 550, 1400, 3400, 6300, 14500, 37000, 105000, 375000, 1260000]
            and all(abs(a / float(b) - 1) < 0.005 for a, b in zip(LADDER_LIVE, LADDER)),
            "X the shard ladder = spec 13.1 at the live curve text %s (the spec's formula numbers within 0.5 %%): %s" % (LADDER_LIVE, bad))
    bad = []
    for t in range(1, 16):
        lvl = BM.BAND[t - 1]
        for si in range(3):
            for l_ in range(5):
                a_ = int(Isl.coins(float(Isl.subH(si + 1, l_ + 1)), float(Cfg.curveBuiltin(int(Isl.band(t))))))
                if a_ != BM.p7_round(SUBH[si][l_] * COIN_H * LIVE(lvl)):
                    bad.append((t, si, l_))
    K.check(not bad, "X every tier's sub-upgrade prices = round7(hours x 8,333 x curve(band)): %s" % bad[:5])
    K.eq([int(Isl.coins(float(Isl.subH(1, l_)), float(Cfg.curveBuiltin(1)))) for l_ in range(1, 6)], [40, 80, 120, 200, 280], "X T1 Small subs 40 / 80 / 120 / 200 / 280 (the first click costs 40)")
    # ---- buy the next tier
    lv["Farming"] = 9
    coins["bal"] = 100000
    cs = inv(27, 27)
    r = str(Core.buyIsland(ou, OWNER, FK, 2, cs))
    K.check(r.startswith("-Buy the T2 Lettuce island first"), "X a tier out of order is refused: %s" % r)
    r = str(Core.buyIsland(ou, OWNER, FK, 1, cs))
    K.check(r.startswith("-You need 128 Lettuce") and coins["bal"] == 100000, "X no lettuce: refused, nothing taken: %s" % r)
    _fill(L, cs, [("Plant_Crop_Lettuce_Item", 130), ("Plant_Seeds_Lettuce", 40)])
    coins["fail"] = True
    r = str(Core.buyIsland(ou, OWNER, FK, 1, cs))
    coins["fail"] = False
    K.check(r.startswith("-The coins could not be taken") and count(cs, "Plant_Crop_Lettuce_Item") == 130 and count(cs, "Plant_Seeds_Lettuce") == 40, "X coins refused: the items are back")
    St.FAIL_TEST = True
    r = str(Core.buyIsland(ou, OWNER, FK, 1, cs))
    St.FAIL_TEST = False
    K.check(r.startswith("-It could not be saved") and count(cs, "Plant_Crop_Lettuce_Item") == 130 and coins["bal"] == 100000 and Isl.slotOf(FK, p, int(Isl.LAD0[FK]) + 1) < 0,
            "X a refused save: items + coins back, no island: %s" % r)
    r = str(Core.buyIsland(ou, OWNER, FK, 1, cs))
    sl = int(Isl.slotOf(FK, p, int(Isl.LAD0[FK]) + 1))
    K.check(r.startswith("+The T2 Lettuce island is yours") and coins["bal"] == 100000 - 3500 and count(cs, "Plant_Crop_Lettuce_Item") == 2
            and count(cs, "Plant_Seeds_Lettuce") == 8 and sl == 1 and g("farming.i1.size") == "1", "X T2 Lettuce bought: 3,500 coins + 128 Lettuce + 32 seeds, slot 2: %s" % r)
    K.check(str(Core.buyIsland(ou, OWNER, FK, 1, cs)).startswith("=You own the T2 Lettuce island already"), "X twice: '='")
    # ---- the 3 sub-upgrades (Small: 40 / 80 / 120 / 200 / 280 coins + 16 x level wheat)
    _fill(L, cs, [("Plant_Crop_Wheat_Item", 528), ("Wood_Oak_Trunk", 300), ("Rock_Stone_Cobble", 300), ("Ingredient_Water_Essence", 40)])
    b = coins["bal"]
    r = str(Core.buySub(ou, OWNER, FK, 0, 0, cs))
    K.check(r.startswith("+Crop Amount 1/5") and coins["bal"] == b - 40 and g("farming.i0.amt") == "1", "X Crop Amount 1: 40 coins + 16 Wheat: %s" % r)
    for l_ in range(2, 6):
        Core.buySub(ou, OWNER, FK, 0, 0, cs)
    K.check(g("farming.i0.amt") == "5" and coins["bal"] == b - 720 and str(Core.buySub(ou, OWNER, FK, 0, 0, cs)).startswith("=Crop Amount is 5/5 at this size"),
            "X Crop Amount 5/5 for 40 + 80 + 120 + 200 + 280 = 720 coins; a 6th is refused")
    K.check(count(cs, "Plant_Crop_Wheat_Item") == 528 - 16 * 15, "X Amount items = 16 x the level (240 Wheat)")
    r = str(Core.grow(ou, OWNER, FK, 0, cs))
    K.check(r.startswith("-Max all 3 upgrades first: Crop Amount 5/5, Decorations 0/5, Irrigation 0/5"), "X Grow before 5/5/5 refused: %s" % r)
    for w in (1, 2):
        for l_ in range(5):
            Core.buySub(ou, OWNER, FK, 0, w, cs)
    K.check(g("farming.i0.deco") == "5" and g("farming.i0.irr") == "5", "X Decorations + Irrigation to 5")
    rate0 = float(Mth.rate(FK, p, 0, now))
    _fill(L, cs, [("Skyy_Ench_Wheat", 10), ("Plant_Seeds_Wheat_Eternal", 20)])
    b = coins["bal"]
    r = str(Core.grow(ou, OWNER, FK, 0, cs))
    rate1 = float(Mth.rate(FK, p, 0, now))
    K.check(r.startswith("+The T1 Wheat island grew to Medium") and g("farming.i0.size") == "2" and [g("farming.i0." + x) for x in ("amt", "deco", "irr")] == ["0", "0", "0"]
            and coins["bal"] == b - 600 and count(cs, "Skyy_Ench_Wheat") == 6 and count(cs, "Plant_Seeds_Wheat_Eternal") == 12 and rate1 >= rate0,
            "X Grow at 5/5/5: Medium, 600 coins + 4 Enchanted Wheat + 8 Eternal seeds, the subs 0/0/0, output %.3f >= %.3f" % (rate1, rate0))
    # ---- seeds: Eternal seeds first (+1 Eternal cell each), plain seeds into the store, take back
    _fill(L, cs, [("Plant_Seeds_Wheat", 30)])
    e0 = int(Isl.eternal(FK, p, 0))
    r = str(Core.seedsGive(ou, OWNER, FK, 0, cs))
    K.check(int(Isl.eternal(FK, p, 0)) == e0 + 12 and int(Isl.seeds(FK, p, 0)) == 30 and count(cs, "Plant_Seeds_Wheat") == 0 and count(cs, "Plant_Seeds_Wheat_Eternal") == 0,
            "X Give seeds: 12 Eternal seeds -> 12 more Eternal cells, 30 seeds in the store: %s" % r)
    r = str(Core.seedsTake(ou, OWNER, FK, 0, cs))
    K.check(int(Isl.seeds(FK, p, 0)) == 0 and count(cs, "Plant_Seeds_Wheat") == 30, "X Take back: 30 seeds back: %s" % r)
    St.FAIL_TEST = True
    r = str(Core.seedsGive(ou, OWNER, FK, 0, cs))
    St.FAIL_TEST = False
    K.check(r.startswith("-The seed store could not be saved") and count(cs, "Plant_Seeds_Wheat") == 30, "X a refused save: nothing taken")
    # ---- Automation (once per shard)
    b = coins["bal"]
    r = str(Core.buyAuto(ou, OWNER, FK, cs))
    K.check(r.startswith("+Automation!") and g("farming.auto") == "1" and coins["bal"] == b - 550 and count(cs, "Plant_Crop_Wheat_Item") == 528 - 240 - 120 - 128,
            "X Automation: 550 coins + 128 Wheat: %s" % r)
    K.check(str(Core.buyAuto(ou, OWNER, FK, cs)).startswith("=This shard is automated already"), "X Automation twice: '='")
    K.check(str(Core.seedsGive(ou, OWNER, FK, 0, cs)).startswith("=This shard is automated"), "X an automated shard needs no seeds")
    # ---- the page: the ladder boxes, the selected island's panel + buttons, the lock card
    from jpype import JClass as _J
    pg = Page(ou, W2)
    pg.kind = FK
    pg.view = 0
    pg.tab = 2
    pg.sel = 0
    Page.TEST_INV = cs
    pg.fill(OWNER, cs)
    K.check(int(pg.nBox) == 15 and str(pg.sName[0]) == "T1 Wheat" and str(pg.sName[1]) == "T2 Lettuce" and str(pg.sSub[2]) == "Buy next" and str(pg.sSub[3]) == "Locked",
            "X page: 15 ladder boxes, T1 Wheat / T2 Lettuce owned, T3 Carrot = Buy next, T4 Locked: %s" % [str(x) for x in pg.sSub][:4])
    K.check(str(pg.iTitle) == "T1 Wheat Island - Medium" and "Automated" in str(pg.iTx[0]) and bool(pg.iCan) and not bool(pg.aCan), "X page: the T1 panel: %s / %s" % (pg.iTitle, pg.iTx[0]))
    bd = T47._build(pg)
    K.check(all(("#SkyySh" + x) in bd["datas"] for x in ("ISubA", "ISubD", "ISubI", "IGrow")) and "#SkyyShIAuto" not in bd["datas"], "X page: the sub-upgrade + Grow buttons bound (no Automation button now)")
    pg.sel = 2
    pg.fill(OWNER, cs)
    bd = T47._build(pg)
    K.check(bool(pg.bCan) and "#SkyyShIBuy" in bd["datas"] and "3" in str(pg.iTx[4]), "X page: the Buy view for T3 Carrot: %s" % [str(x) for x in pg.iTx])
    lv["Farming"] = 1
    pg.fill(OWNER, cs)
    K.check(str(pg.sum1) == "Farming Shard - locked" and str(pg.sum2).startswith("Reach Farming 5 to open it. You: Farming 1."), "X page: the lock card in the strip")
    r = str(pg.act("ibuy", None, None))
    K.check(r.startswith("-Farming Shard - locked"), "X a locked page's buttons refuse: %s" % r)
    lv["Farming"] = 9
    pg.sel = 0
    r = str(pg.act("isub1", None, None))
    K.check(r.startswith("=Decorations is 5/5") is False and (r.startswith("+Decorations 1/5") or r.startswith("-")), "X page click isub1 -> buySub: %s" % r)
    Page.TEST_INV = None
    # fix2 (critic): the island is reset again and the archipelago is not rebuilt there: the starter door's record is stale -> Pick up Shard
    # gives the shard back (as Enter tells the player), once
    p = St.get(OWNER)
    if p.getProperty("farming.paused") is not None:
        p.remove("farming.paused")
    K.check(str(p.getProperty("farming.placed")) == str(p.getProperty("farming.door.starter")), "X fix2 setup: the Farming record is the starter door")
    cs2 = inv(27, 27)
    K.check(str(Core.pickup(ou, OWNER, FK, None, cs2)).startswith("-This is your starter island's own"), "X fix2: a current starter door still cannot be picked up")
    wk["cur"] = W + "-r2"
    re_ = str(L["ShWorld2"].enter(None, None, ou, OWNER, FK, None))
    rp = str(Core.pickup(ou, OWNER, FK, None, cs2))
    rp2 = str(Core.pickup(ou, OWNER, FK, None, cs2))
    K.check("Pick up Shard" in re_ and rp.startswith("+") and count(cs2, "Skyy_Shard_Farming") == 1 and p.getProperty("farming.placed") is None and rp2.startswith("-"),
            "X fix2: a reset island's stale starter door: Enter says Pick up Shard, Pick up gives the shard once: %s / %s / %s" % (re_[:60], rp[:60], rp2[:50]))
    wk["cur"] = W2
    Isl.LEVEL_TEST = None
    K.save()


def run_geo(out, jar, scratch, _home):
    from jpype import JClass, JString, JArray, JInt
    K = HK.Child(out)
    L = _setup(os.path.join(scratch, "g"), K)
    St, Isl, Mth, Geo, Fill, Door, Cfg = (L[n] for n in ("ShStore", "ShIsl", "ShMath", "ShGeo", "ShFill", "ShDoor", "ShCfg"))
    UUID = L["UUID"]
    ou = UUID.fromString(OWNER)
    W = "skyy-island-" + OWNER
    Door.door(ou, OWNER, "farming", W, 29, 129, -31)
    p = St.get(OWNER)
    Y = int(Geo.Y)
    cx, cz = int(Geo.ox(FK) + Geo.SX[0]), int(Geo.OZ + Geo.SZ[0])
    reg = list(Geo.region(p, FK))
    kinds = {}
    for b in reg:
        kinds[int(b[3])] = kinds.get(int(b[3]), 0) + 1
    ERES = int(Isl.RES1[int(Isl.LAD0[FK])])
    et = [b for b in reg if int(b[3]) == ERES]
    farm = [b for b in reg if int(b[3]) == int(Geo.FARM)]
    fxs1, fzs1 = list(Isl.fx(1)), list(Isl.fz(1))
    man = [(int(fxs1[i]), int(fzs1[i])) for i in range(8, int(round(72 * 0.6)))]
    inr = [c for c in man if c[0] * c[0] + c[1] * c[1] <= 9]
    K.check(len(et) == 8 and all(max(abs(int(b[0]) - cx), abs(int(b[2]) - cz)) == 2 for b in et) and len(farm) == len(inr) == 12
            and all((int(b[0]) - cx) ** 2 + (int(b[2]) - cz) ** 2 <= 9 for b in farm),
            "G the Farming starter: 8 Eternal Wheat around the centre + %d manual farm cells the Harvest Spirit I (range 3) replants (Amount 0 = 60 %% of 72)" % len(farm))
    outr = [c for c in man if c[0] * c[0] + c[1] * c[1] > 9]
    tills = set((int(b[0]) - cx, int(b[2]) - cz) for b in reg if int(b[3]) == int(Geo.TILL) and int(b[1]) == Y)
    K.check(len(outr) == 23 and all(c in tills for c in outr), "G fix: the other %d manual cells are tilled soil the player plants by hand (no replant entry)" % len(outr))
    M = JClass("java.util.HashMap")()
    Fill.TEST_BLOCKS = M
    job = Fill(None, None, None)
    job.kind = FK
    job.prep(p)
    K.check(bool(job.scan[0]) and int(job.seedHave[0]) == 0, "G the scan counts the manual island (store empty)")
    n1 = int(Fill.paintY(None, Geo.region(p, FK), JClass("java.util.HashSet")(), job))
    K.check(n1 > 300 and str(M.get("%d,%d,%d" % (cx + 2, Y + 1, cz))) == str(Geo.IDS[ERES]) and M.get("%d,%d,%d" % (int(farm[0][0]), Y + 1, int(farm[0][2]))) is None
            and str(M.get("%d,%d,%d" % (int(farm[0][0]), Y, int(farm[0][2])))) == "Soil_Dirt_Tilled", "G painted: Eternal on the 8, tilled + empty farm cells (%d blocks)" % n1)
    fxs = JClass("java.util.HashSet")()
    n2 = int(Fill.paintY(None, Geo.region(p, FK), fxs, None))
    K.check(n2 == 0, "G a second paint touches nothing (%d)" % n2)
    Fill.markFixed("skyy-shard-" + OWNER, FK, fxs)
    K.check(not any(int(b[3]) in (int(Geo.FIX_BRICK), int(Geo.FIX_PAD)) for b in Geo.region(St.get(OWNER), FK)), "G no centre-fix entries once marked")
    # replant from the store: 5 seeds -> 5 planted, the scan saved, the store at 0
    p.setProperty("farming.i0.seed", "5")
    job = Fill(None, None, None)
    job.kind = FK
    job.prep(p)
    Fill.paintY(None, Geo.crops(p, FK), None, job)
    job.world = None
    planted = sum(1 for b in farm if M.get("%d,%d,%d" % (int(b[0]), int(b[1]), int(b[2]))) is not None)
    K.check(planted == 5 and int(job.seedUsed[0]) == 5 and sum(int(job.pl[j]) for j in range(21)) == 5, "G the regrow replants 5 cells from 5 seeds and counts them")
    # scanDone needs the world name: emulate it on the profile
    b_ = [0] * 21
    for j in range(21):
        b_[j] = int(job.pl[j])
    from jpype import JArray, JInt
    p.setProperty("farming.i0.pl", str(Isl.binsText(JArray(JInt)(b_))))
    K.check(abs(float(Isl.mfac(FK, p, 0, 1, 3)) - (8 + 0.5 * min(5, sum(b_[:4]))) / 20.0) < 1e-9, "G the scan feeds the manual factor")
    # fix (critic 1): the seeds come from the LIVE store cell by cell - a Take seeds between two paint slices gets only what is left
    clr = lambda: [M.remove("%d,%d,%d" % (int(b[0]), int(b[1]), int(b[2]))) for b in farm]
    clr()
    p.setProperty("farming.i0.seed", "10")
    job = Fill(None, None, None)
    job.kind = FK
    job.prep(p)
    crl = Geo.crops(p, FK)
    miss_, cnt_ = JClass("java.util.HashSet")(), JArray(JInt)(1)
    pos = int(Fill.paintZ(None, crl, None, job, miss_, 0, 1, cnt_))   # one slice (the deadline is long past: 16 entries)
    used1 = int(job.seedUsed[0])
    live1 = int(St.get(OWNER).getProperty("farming.i0.seed"))
    K.check(0 < pos < int(crl.size()) and used1 > 0 and live1 == 10 - used1, "G fix: slice 1 planted %d cells, the live store is %d (10 - %d) at once" % (used1, live1, used1))
    # fix2 (critic): the store is saved after a slice that took seeds (ShFill.run calls saveSeeds before queuing the next slice) - a stop
    # between two slices leaves the shard file at 10 - used, never the planted cells AND the seeds
    sv = int(job.saveSeeds())
    disk = open(os.path.join(L["sd"], OWNER + ".properties"), encoding="latin-1").read()
    K.check(sv == 1 and ("farming.i0.seed=%d" % (10 - used1)) in disk.splitlines() and not bool(job.seedDirty) and int(job.saveSeeds()) == 0,
            "G fix2: after slice 1 the shard file on disk holds %d seeds (saveSeeds = %d, then nothing more to save)" % (10 - used1, sv))
    St.LOCK.lock()
    try:
        taken = int(St.get(OWNER).getProperty("farming.i0.seed"))
        St.get(OWNER).setProperty("farming.i0.seed", "0")   # = seedsTake's change (under the lock)
    finally:
        St.LOCK.unlock()
    while pos < int(crl.size()):
        pos = int(Fill.paintZ(None, crl, None, job, miss_, pos, 1, cnt_))
    planted = sum(1 for b in farm if M.get("%d,%d,%d" % (int(b[0]), int(b[1]), int(b[2]))) is not None)
    K.check(planted == used1 and planted + taken == 10 and int(job.seedUsed[0]) == used1 and int(St.get(OWNER).getProperty("farming.i0.seed")) == 0,
            "G fix: Take seeds mid-paint took %d, the rest planted nothing - %d planted + %d taken = 10 seeds, never more" % (taken, planted, taken))
    p.setProperty("farming.i0.seed", "1")
    job.unseed(0)
    K.check(int(p.getProperty("farming.i0.seed")) == 2 and int(job.seedUsed[0]) == used1 - 1, "G fix: unseed puts the seed back into the live store")
    # fix (critic 3): the store replants only inside the worker totems' range: Wider Area (+2) = range 5; no worker = nothing
    wk = str(p.getProperty("farming.i0.totems"))
    p.setProperty("farming.i0.totems", wk + ":wider")
    f5 = [b for b in Geo.region(p, FK) if int(b[3]) == int(Geo.FARM)]
    p.setProperty("farming.i0.totems", "")
    f0 = [b for b in Geo.region(p, FK) if int(b[3]) == int(Geo.FARM)]
    p.setProperty("farming.i0.totems", wk)
    want5 = [c for c in man if c[0] * c[0] + c[1] * c[1] <= 25]
    K.check(len(f5) == len(want5) > 12 and all((int(b[0]) - cx) ** 2 + (int(b[2]) - cz) ** 2 <= 25 for b in f5) and not f0 and int(Geo.reach(FK, p, 0)) == 3,
            "G fix: Wider Area (range 5) replants %d cells; no worker totem = %d; a Harvest Spirit I reaches 3" % (len(f5), len(f0)))
    clr()
    p.setProperty("farming.i0.seed", "100")
    job = Fill(None, None, None)
    job.kind = FK
    job.prep(p)
    Fill.paintY(None, Geo.crops(p, FK), None, job)
    oc = [(cx + c[0], Y + 1, cz + c[1]) for c in outr]
    K.check(all(M.get("%d,%d,%d" % c) is None for c in oc) and int(p.getProperty("farming.i0.seed")) == 100 - 12,
            "G fix: the %d cells out of range stay empty; 12 seeds used of 100" % len(oc))
    p.setProperty("farming.i0.seed", "0")
    # fix (critic 3): the time-sliced paint = the same blocks as one whole paint
    MA, MB = JClass("java.util.HashMap")(), JClass("java.util.HashMap")()
    Fill.TEST_BLOCKS = MA
    Fill.paintY(None, Geo.region(p, FK), JClass("java.util.HashSet")(), None)
    Fill.TEST_BLOCKS = MB
    rg_ = Geo.region(p, FK)
    pos, calls, cnt_ = 0, 0, JArray(JInt)(1)
    while pos < int(rg_.size()):
        pos = int(Fill.paintZ(None, rg_, JClass("java.util.HashSet")(), None, JClass("java.util.HashSet")(), pos, 1, cnt_))
        calls += 1
    K.check(MA.equals(MB) and calls > 10 and int(cnt_[0]) == int(MB.size()), "G fix: %d slices paint exactly what one whole paint does (%d blocks)" % (calls, int(MB.size())))
    Fill.TEST_BLOCKS = M
    # decorations (fix: isl.deco.props a level, never on a walkway) + pools per level, never twice
    NP = int(Cfg.DECO_N)
    for lvl in (1, 3, 5):
        p.setProperty("farming.i0.deco", str(lvl)); p.setProperty("farming.i0.irr", str(lvl))
        rg = list(Geo.region(p, FK))
        dk = [b for b in rg if int(b[3]) == int(Geo.DECO_K)]
        nd = len(dk)
        nw = sum(1 for b in rg if int(b[3]) == int(Geo.WATER))
        K.check(NP == 5 and nd == NP * lvl and nw == 4 * lvl and not any(bool(Geo.gap(0, int(b[0]) - cx, int(b[2]) - cz)) for b in dk),
                "G Decorations %d: %d props (%d a level, none on a bridge walkway), Irrigation %d: %d water cells" % (lvl, nd, NP, lvl, nw))
    Fill.paintY(None, Geo.region(p, FK), JClass("java.util.HashSet")(), None)
    wet = [k for k in M.keySet() if str(k).startswith("f:")]
    K.check(len(wet) == 20, "G 5 pools = 20 water cells placed")
    K.check(int(Fill.paintY(None, Geo.region(p, FK), JClass("java.util.HashSet")(), None)) == 0, "G ... a second paint touches nothing (water, props, farm)")
    deco_ids = set(str(Geo.IDS[int(i)]) for i in Geo.DECOALL)
    def ndc():
        n_ = 0
        for k in M.keySet():
            c_ = [int(v) for v in str(k).split(",")] if not str(k).startswith("f:") else None
            if c_ and c_[1] == Y + 1 and max(abs(c_[0] - cx), abs(c_[2] - cz)) <= 6 and str(M.get(k)) in deco_ids:
                n_ += 1
        return n_
    nd5 = ndc()
    Cfg.DECO_N = 2
    Fill.paintY(None, Geo.region(p, FK), JClass("java.util.HashSet")(), None)
    nd2 = ndc()
    Cfg.DECO_N = NP
    Fill.paintY(None, Geo.region(p, FK), JClass("java.util.HashSet")(), None)
    nd5b = ndc()
    K.check(nd5 == 25 and nd2 == 10 and nd5b == 25, "G fix: isl.deco.props 5 -> 2 -> 5 on Decorations 5: %d -> %d -> %d props (the extra ones cleared)" % (nd5, nd2, nd5b))
    # the Mining cave: ore counts per size / Ore Amount (spec 9.3 table)
    K.eq([int(Isl.oreN(1, a)) for a in range(6)], [27, 41, 55, 68, 82, 95], "G Small cave ore 27 .. 95")
    K.eq([int(Isl.oreN(2, 0)), int(Isl.oreN(2, 5)), int(Isl.oreN(3, 0)), int(Isl.oreN(3, 5))], [95, 250, 250, 476], "G Medium 95 .. 250, Large 250 .. 476")
    pm = St.get(OWNER)
    Door.door(ou, OWNER, "mining", W, -43, 124, 4)
    for sz, am, want in ((1, 2, 55), (2, 1, 126), (3, 0, 250)):
        pm.setProperty("mining.i0.size", str(sz)); pm.setProperty("mining.i0.amt", str(am)); pm.setProperty("mining.i0.cave", "1")
        rg = list(Geo.region(pm, MKD))
        mcx, mcz = int(Geo.ox(MKD) + Geo.SX[0]), int(Geo.OZ + Geo.SZ[0])
        ore = [b for b in rg if int(b[3]) == int(Geo.ORECELL)]
        h = int(Geo.HALF[sz - 1])
        air = [b for b in rg if int(b[3]) == int(Geo.AIR) and int(b[1]) > Y and max(abs(int(b[0]) - mcx), abs(int(b[2]) - mcz)) == h]
        pads = [b for b in rg if int(b[3]) >= int(Geo.TOTEM) and int(b[3]) < int(Geo.XB) and int(b[1]) == Y + 1 and max(abs(int(b[0]) - mcx), abs(int(b[2]) - mcz)) <= 1]
        K.check(len(ore) == want and len(air) == 9 and len(pads) == 1 and all(max(abs(int(b[0]) - mcx), abs(int(b[2]) - mcz)) <= h for b in ore),
                "G cave size %d Amount %d: %d ore cells (>= the old %s), a 3 x 3 opening (%d), the totem on the floor (%d)" % (sz, am, len(ore), (16, 72, 160)[sz - 1], len(air), len(pads)))
    # the old flat Mining island -> a cave once: only exactly the old node is cleared
    pm.setProperty("mining.i0.size", "1"); pm.setProperty("mining.i0.amt", "2"); pm.remove("mining.i0.cave")
    M2 = JClass("java.util.HashMap")()
    Fill.TEST_BLOCKS = M2
    mcx, mcz = int(Geo.ox(MKD) + Geo.SX[0]), int(Geo.OZ + Geo.SZ[0])
    old = [(mcx + dx, Y + 1, mcz + dz) for dx in range(-5, 6) for dz in range(-5, 6) if dx % 2 == 0 and dz % 2 == 0 and not (abs(dx) <= 2 and abs(dz) <= 2)]
    for c in old:
        M2.put("%d,%d,%d" % c, "Ore_Copper_Stone")
    M2.put("%d,%d,%d" % old[0], "Furniture_Crude_Chest_Small")   # not ours: kept
    fx = JClass("java.util.HashSet")()
    Fill.paintY(None, Geo.region(pm, MKD), fx, None)
    left = [c for c in old[1:] if M2.get("%d,%d,%d" % c) is not None]
    K.check(not left and str(M2.get("%d,%d,%d" % old[0])) == "Furniture_Crude_Chest_Small" and fx.contains(JClass("java.lang.Integer")(100)),
            "G the old flat island's %d nodes cleared (a foreign block kept), the cave fix marked" % (len(old) - 1))
    Fill.TEST_BLOCKS = None
    K.save()


def _lines(text, width, size=13):
    """greedy word wrap with the client's glyph widths (skyyui.text_width) -> the number of lines"""
    import skyyui as SUI
    n, cur = 1, ""
    for wd in text.split(" "):
        t = wd if not cur else cur + " " + wd
        if SUI.text_width(t, size) <= width or not cur:
            cur = t
        else:
            n, cur = n + 1, wd
    return n


def run_width(out, jar, scratch, _home):
    """fix (critic): every runtime price line of the Islands tab panel (the 3 sub-upgrades at every shard x tier x size x level, Grow,
    Automation, the totems row) wraps into at most 2 lines of the 328 px row (RW 352 - 24) at 13 px"""
    K = HK.Child(out)
    L = _setup(os.path.join(scratch, "w"), K)
    Isl, Cfg = L["ShIsl"], L["ShCfg"]
    W_ = 352 - 24
    worst, bad, n = (0, ""), [], 0
    num = lambda v: str(Cfg.num(v))
    for kd in range(6):
        for i in range(int(Isl.LADN[kd])):
            t = int(Isl.LAD0[kd]) + i
            cv = float(Cfg.curve(int(Isl.band(int(Isl.TIER[t])))))
            lines = []
            for sz in (1, 2, 3):
                for w in range(3):
                    tm = (Cfg.MAT_AMT, Cfg.MAT_DECO, Cfg.MAT_IRR)[w]
                    for lv in range(5):
                        sm = Isl.mats(kd, t, tm, sz - 1, lv + 1)
                        mt = str(Isl.matsText(sm))
                        lines.append("%s %d/5 - next: %s coins%s" % (Isl.subName(kd, w), lv, num(int(Isl.coins(float(Isl.subH(sz, lv + 1)), cv))), (" + " + mt) if mt else ""))
                if sz < 3:
                    gm = str(Isl.matsText(Isl.mats(kd, t, Cfg.MAT_GROW, sz - 1, 1)))
                    lines.append("Grow to %s: %s coins%s" % ("Medium" if sz == 1 else "Large", num(int(Isl.coins(float(Isl.growH(sz + 1)), cv))), (" + " + gm) if gm else ""))
            am = str(Isl.matsText(Isl.mats(kd, int(Isl.LAD0[kd]), Cfg.AUTO_ITEMS[kd], 0, 1)))
            lines.append("Automation (manual now): %s coins%s" % (num(int(Isl.coins(float(Isl.stepH(int(Cfg.AUTO_STEP))), cv))), (" + " + am) if am else ""))
            lines.append("Totems: 5 of 5 pads (Totems tab) - upgrades +24.2 %")
            for ln in lines:
                n += 1
                k = _lines(ln, W_)
                wd = L["SUI"].text_width(ln, 13) if "SUI" in L else 0
                if k > 2:
                    bad.append(ln)
                if len(ln) > len(worst[1]):
                    worst = (k, ln)
    K.check(not bad and n > 1000, "W fix: %d price lines, every one fits 2 lines of %d px (longest: %d lines '%s'): %s" % (n, W_, worst[0], worst[1], bad[:3]))
    K.save()


def run_exec47(out, jar, scratch, home):
    """the 0.4.7 harness's EXEC phase (tier up on the totem's own page, the bench) on the 0.4.8 jar"""
    T47.run_exec(out, jar, os.path.join(scratch, "r47"), home)


def _superseded(sup, fn):
    """run an older harness phase; its checks whose text starts with one of `sup` are behaviour 0.4.8 replaces on purpose (kept as notes)"""
    old_child = HK.Child

    class Sup(old_child):
        def check(self, cond, what):
            if any(str(what).startswith(x) for x in sup):
                self.notes.append("superseded by 0.4.8: " + str(what)[:110])
                return True
            return old_child.check(self, cond, what)
    HK.Child = Sup
    try:
        fn()
    finally:
        HK.Child = old_child


def run_exec46(out, jar, scratch, home):
    """the 0.4.6 harness's EXEC phase on the 0.4.8 jar with the level 20 grants switched back ON (lv20.* = 20, an owner's choice) and the
    door locks off - the 0.4.6 grant machinery still works when a server wants it. Superseded: 0.4.6's islands 2-6 bought into any slot
    (X8 / X9 - one island per tier now, phase X) and the 'an admin can give you one' wording (FIX3)"""
    orig = T46._fixture

    def fx(scratch_, K_):
        L = orig(scratch_, K_)
        f = os.path.join(scratch_, "x", "config.properties")
        open(f, "a", encoding="latin-1").write(NL_ + "".join("lv20.%s=20" % k + NL_ for k in KK) + "".join("shard.lock.%s=0" % k + NL_ for k in KK))
        L["ShCfg"].loadCfg(False)
        return L
    T46._fixture = fx
    _superseded(("X8 ", "X9 ", "FIX3 src()"), lambda: T46.run_exec(out, jar, os.path.join(scratch, "r46"), home))


def run_centre47(out, jar, scratch, home):
    """the 0.4.7 harness's CENTRE phase on the 0.4.8 jar. Superseded: 'no entry below 0 at all' (0.4.8 paints special cells too - its own
    check is G 'no centre-fix entries once marked')"""
    _superseded(("G a fixed island carries no fix entries any more", "G the regrow list has no fix entries"),
                lambda: T47.run_centre(out, jar, os.path.join(scratch, "c47"), home))


def run_live48(out, jar, scratch, home):
    """D on a scratch COPY of NewBetaTest's Skyy_SkyyShards (0.4.7 deployed there): start 1 = ShMig048 once + the real profile's map migration,
    start 2 = nothing written; the real Mining island becomes a cave with at least its old nodes"""
    from jpype import JClass
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    K = HK.Child(out)
    Cfg, path = T42.kit_home(home)
    M4, M5, M6, M8 = (JClass(PKG + n) for n in ("ShMig044", "ShMig045", "ShMig046", "ShMig048"))
    St, Isl, Geo = JClass(PKG + "ShStore"), JClass(PKG + "ShIsl"), JClass(PKG + "ShGeo")
    sd = os.path.join(home, "shards")

    def start():
        T42.kit_home(home)
        rs = (str(Cfg.migCoop(Cfg.FILE)), str(M4.run(Cfg.FILE)), str(M5.run(Cfg.FILE)), str(M6.run(Cfg.FILE)), str(M8.run(Cfg.FILE)))
        Cfg.loadCfg(True)
        St.DIR = path(sd)
        St.CACHE.clear()
        keys = [f[:-11] for f in sorted(os.listdir(sd)) if f.endswith(".properties")] if os.path.isdir(sd) else []
        return rs, [(k, St.get(k)) for k in keys]
    rs, profs = start()
    K.check(rs[:4] == ("", "", "", "") and rs[4].startswith("config.properties updated for SkyyShards 0.4.8"), "D start 1: only ShMig048 runs: %s" % rs[4][:200])
    K.check(all(str(p.getProperty("map.done")) == "1" for k, p in profs) and len(profs) >= 1, "D start 1: every real profile migrated (%d)" % len(profs))
    for k, p in profs:
        if p.getProperty("mining.i0.type") is not None:
            K.check(str(p.getProperty("mining.auto")) == "1" and str(p.getProperty("mining.i0.amt")) == "2" and int(Isl.oreN(1, 2)) >= 16,
                    "D the real Mining island: Automated, Ore Amount 2 = %d ore cells (it had 16 nodes)" % int(Isl.oreN(1, 2)))
    t1 = T42.tree(home)
    rs2, profs2 = start()
    K.check(rs2 == ("", "", "", "", "") and T42.tree(home) == t1, "D start 2: nothing runs, no file changes")
    K.save()


EXPECT = {   # checked by hand 2026-10-23: the version texts (CfgFile / CfgFn / CfgRows, ShStore.save); SLOTS 6 -> 16 inlined (ShAdmin.run,
            # ShCore.at / nearest / placeTotem0 / uidAt, ShMath.owned / settleAll, ShParticles.run); the rest = the round's planned changes
    "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "ShAdmin": ["~m run"],
    "ShCfg": ["+f AMT_BONUS", "+f AMT_PCT", "+f AUTO_ITEMS", "+f AUTO_STEP", "+f BAND", "+f BUY_H", "+f BUY_ITEMS", "+f CAVE_PCT", "+f COIN_H", "+f DECO_N", "+f DECO_PCT",
              "+f DEF_AMT_PCT", "+f DEF_AUTO_ITEMS", "+f DEF_BUY_ITEMS", "+f DEF_CAVE_PCT", "+f DEF_LOCK_SKILL", "+f DEF_SUB_H", "+f DEF_UP_H", "+f DEF_UP_LV",
              "+f GROW_H", "+f IRR_PCT", "+f LOCK", "+f LOCK_SKILL", "+f MAN_OFF_SEC", "+f MAN_PCT", "+f MAT_AMT", "+f MAT_DECO", "+f MAT_GROW", "+f MAT_IRR",
              "+f PER_SAP", "+f SEED_MAX", "+f SEED_RET", "+f SUB_H", "+f UP_H", "+f UP_LV", "+m decsOf", "+m intsOf", "~<clinit>", "~m loadCfg", "~m writeDefaults"],
    "ShCore": ["+m buyAuto", "+m buyAuto0", "+m buySub", "+m buySub0", "+m purchaseM", "+m seedsGive", "+m seedsTake", "~m at", "~m buyIsland0", "~m collect0",
               "~m gate", "~m grow0", "~m nearest", "~m pickup", "~m placeTotem0", "~m uidAt"],
    "ShFill": ["+f PLANTED", "+f SCANS", "+f SLICED", "+f SLICE_NS", "+f cnt", "+f cxs", "+f czs", "+f fxs", "+f miss", "+f pkey", "+f pl", "+f pos", "+f scan",
               "+f seedDirty", "+f seedHave", "+f seedMiss", "+f seedUsed", "+f seeding", "+f tp", "+m cell", "+m fluidAt", "+m paintY", "+m paintZ", "+m planted", "+m prep", "+m saveSeeds", "+m scanDone", "+m seed", "+m smiss", "+m tree", "+m unseed", "+m water", "~<clinit>",
               "~m markFixed", "~m paintAsync", "~m paintX", "~m region", "~m run"],
    "ShGate": ["+m plantable", "+m soil", "~m allowed"],
    "ShGeo": ["+f CLRCROP", "+f CLRDECO", "+f CLROURS", "+f DECO", "+f DECOALL", "+f DECO_K", "+f FARM", "+f FIX_ORE", "+f ORECELL", "+f RESX", "+f SRC",
              "+f TSEED", "+f TSPOT", "+f WATER", "+f XB", "+m cave", "+m caveFix", "+m ck", "+m decoGone", "+m decoSpots", "+m decoSpots0", "+m dedupe", "+m facing",
              "+m gap", "+m island", "+m mix", "+m opening", "+m pools", "+m reach", "+m ringPos", "+m tree", "~<clinit>", "~m bridge", "~m crops", "~m island", "~m region", "~m res"],
    "ShLv20": ["~m src"], "ShMath": ["~m owned", "~m settle", "~m settleAll", "~m starter"],
    "ShPage": ["+f aCan", "+f iHub", "+f locked", "+f nBox", "+f sCan", "+f sCol", "+f sSlot", "~m act", "~m buildFull", "~m fill", "~m fillTotems"],
    "ShPageFn": ["~m make"], "ShParticles": ["~m run"], "ShStore": ["+f MAPPED", "+m migrate2", "+m snapMap", "~<clinit>", "~m get", "~m migrate", "~m save"],
    "ShTotem": ["+m replantMul", "~m islandRate"], "ShWorld2": ["~m enter"], "SkyyShardsPlugin": ["~m setup", "~m shutdown"]}

if __name__ == "__main__":
    HK.run(name="SkyyShards", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=["ShDoor", "ShIsl", "ShMig048"],
           phases=[("static", run_static), ("exec47", run_exec47), ("exec46", run_exec46), ("centre47", run_centre47), ("config", run_config), ("mig", run_mig), ("players", run_players), ("exec", run_exec), ("width", run_width), ("geo", run_geo),
                   ("live", run_live48)],
           script=__file__, live=(T46.LIVE_SH, "mods/Skyy_SkyyShards"))
