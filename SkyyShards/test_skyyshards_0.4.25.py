"""Harness for SkyyShards 0.4.25 (shard clicker 3: Farming - tools/shards_0_4_25_patch.py, on top of 0.4.24).
Build first:
    python tools/shards_0_4_25_patch.py && python SkyyShards/build_skyyshards_0.4.25.py
    python SkyyShards/test_skyyshards_0.4.25.py [--keep]

  S25  static   the patch re-runs to identical bytes; header / VERSION / ready line; no new registerSystem / registerCommand; line endings kept; the jar
                ships the 0.4.23 + 0.4.24 pictures + the 34 farm pictures (our own, no vanilla file)
  FA   farm     EXECUTED the crop data = Assets.zip's ripe drops (quantities, the 0.5 % Eternal seed bag, the Mushroom none); the hoe tiers; bare
                hands harvest (no SkyyGear = not gated); the click cap; a plot's 8 clicks; a harvest = EXACT plants (a seeded Random replayed in
                Python: quantity, Fortune, Eternal seed) into farming.i0.drops (saved); the XP (25 % of the world's 40 a Wheat plant); the regrow +
                Irrigation; a wrong spot / an empty slot; THE WORLD GATE (gear:fn:farmTier asked with the crop block + the held item; 2 = refused,
                no hit counted; 1 = 0.4 a click, no Fortune asked, half XP); Fortune 2.0 (skill:fn:fortune "Farming") = each plant x3; the Eternal
                seed (permille 1000 = every plant) and storage room (seeds first); storage full; a refused save (nothing added, the plot stands
                again); switched off; a zone 2 crop (Corn 2-4); the plot memory is the farm's own (a Foraging tree in slot 0 is not touched)
  FU   upgrade  EXECUTED Plot size (Tree size's costs: exact coins + Enchanted Wheat; no Enchanted / not enough coins = nothing taken; a stale double
                click buys once; the highest level); the page rows ku0..ku5 (Plot count / Irrigation / Decorations bought with the level shown, a stale
                level refused, Spirit -> the Totems tab); a STALE ISLAND (another crop in the slot / another profile key) = no harvest, no buy
  FZ   zones    EXECUTED Farming zone 1..5 open at Farming 0 / 20 / 40 / 60 / 80 (3 crops a zone); a Zone 2 island refused at Farming 19 (buyIsland =
                the Map tab too), not at 20; an owned island in a locked zone stays open + harvestable; the farm map (locks, header, Open, Buy)
  FC   collect  EXECUTED the grid shows the harvested crops + seeds; a cell / Collect all pay them first (the collection credit), no XP at Collect; a full
                inventory keeps the rest
  FP   page     the Farming footer has Shard clicker; kopen -> view 5 farm; every size walks clean (the plot squares carry kt<spot>:<slot>, the crop
                pictures, the rain totem = Irrigation, the farm rows' names), the title, the element count, the packet; a harvest on the page (status +
                pop + the harvested picture); the farm map; the info line (hands / hoe); switched off = no button; Foraging + Mining unchanged
  then 0.4.24's phases (mine24 .. page24), 0.4.23's and the older ones on THIS jar (their "Farming has no clicker / no zone locks" lines now expect the
  farm), A verify, C compare, AA audit, live START TWICE on a scratch copy of the live data
Exit code 1 on any failure.
"""
import os, sys, importlib.util, subprocess, json, re, zipfile, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK

VERSION = "0.4.25"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "farm1", "h")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyShards-%s.jar" % VERSION)]
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyShards-0.4.24.jar")
GEN = os.path.join(HERE, "build_skyyshards_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyshards_0.4.24.py")
PATCH = os.path.join(ROOT, "tools", "shards_0_4_25_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.shards."

# the 0.4.24 harness (it loads 0.4.23 and older): its version moves to this one in memory; the lines that said "Farming has no clicker / no zone
# locks" now expect the farm (0.4.25)
_T24 = open(os.path.join(HERE, "test_skyyshards_0.4.24.py"), encoding="utf8").read()
_vl = 0
_out = []
for _ln in _T24.split("\n"):
    if _ln.startswith('VERSION = "0.4.24"') or ("'VERSION = \\\"0.4.24\\\"'" in _ln) or ("'VERSION = \"0.4.24\"' + chr(10)" in _ln) or ("arena (SkyyShards 0.4.24)" in _ln):
        _ln = _ln.replace("0.4.24", VERSION)
        _vl += 1
    _out.append(_ln)
_T24 = "\n".join(_out)
assert _vl == 4, "the 0.4.24 harness changed (version lines %d)" % _vl
FIX24 = [('K.eq(int(Isl.zoneNeed(FK, int(Isl.LAD0[FK]) + 5)), 0, "MZ Farming open")',
          'K.eq(int(Isl.zoneNeed(FK, int(Isl.LAD0[FK]) + 5)), 20, "MZ Farming zone 2 opens at Farming 20 (0.4.25)")'),
         ('K.check("#SkyyShClk" not in T49._build(pf)["mk"], "MP the Farming footer has no clicker")',
          'K.check("#SkyyShClk" in T49._build(pf)["mk"], "MP the Farming footer has the clicker (0.4.25)")')]
FIX23 = [('K.eq(int(Isl.zoneNeed(FK, int(Isl.LAD0[FK]) + 5)), 0, "CZ ... Foraging only this round (Farming open)")',
          'K.eq(int(Isl.zoneNeed(FK, int(Isl.LAD0[FK]) + 5)), 20, "CZ ... Farming zones too (0.4.25)")'),
         ('K.check("#SkyyShClk" not in T49._build(pf)["mk"], "PG23 the Farming footer has no clicker")',
          'K.check("#SkyyShClk" in T49._build(pf)["mk"], "PG23 the Farming footer has the clicker (0.4.25)")'),
         ('K.eq(int(pf.view), 0, "PG23 ... and kopen does nothing there")', 'K.eq(int(pf.view), 5, "PG23 ... kopen opens the farm (0.4.25)")')]
for _o, _n in FIX24:
    assert _T24.count(_o) == 1, _o
    _T24 = _T24.replace(_o, _n)
_inj = "for _o, _n in FIX23:\n    assert _T23.count(_o) == 1, _o\n    _T23 = _T23.replace(_o, _n)\n"
_anc = "_argv = list(sys.argv)\nT423 = "
assert _T24.count(_anc) == 1
_T24 = _T24.replace(_anc, _inj + _anc)
_argv = list(sys.argv)
T424 = importlib.util.module_from_spec(importlib.util.spec_from_loader("test_skyyshards_0_4_24", loader=None))
T424.__dict__["__file__"] = os.path.join(HERE, "test_skyyshards_0.4.24.py")
T424.__dict__["FIX23"] = FIX23
exec(compile(_T24, T424.__file__, "exec"), T424.__dict__)
sys.argv[:] = _argv
T423, T422, T421 = T424.T423, T424.T422, T424.T421
T420, T419, T411, T410, T49, T416, T415, T413 = T424.T420, T424.T419, T424.T411, T424.T410, T424.T49, T424.T416, T424.T415, T424.T413
T424.JAR = T423.JAR = T422.JAR = T421.JAR = T420.JAR = T419.JAR = T420.T418.JAR = T419.T417.JAR = JAR
T424.SCRATCH = T423.SCRATCH = T422.SCRATCH = T421.SCRATCH = T420.SCRATCH = T419.SCRATCH = T420.T418.SCRATCH = T416.SCRATCH = T415.SCRATCH = T419.T417.SCRATCH = SCRATCH
OWNER, MEMBER = T420.OWNER, T420.MEMBER
MI, FO, FK = 0, 1, 2
T0 = 1790000000000
WH, EWH, WSE = "Plant_Crop_Wheat_Item", "Skyy_Ench_Wheat", "Plant_Seeds_Wheat_Eternal"
CORN = "Plant_Crop_Corn_Item"
OAK = "Wood_Oak_Trunk"
CROPS = ("Wheat", "Lettuce", "Carrot", "Corn", "Cauliflower", "Turnip", "Pumpkin", "Aubergine", "Tomato", "Chilli", "Cotton", "Rice", "Potato", "Onion", "Mushroom")


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyShards 0.4.25 - build script') and 'VERSION = "0.4.25"\n' in g, "S25 header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S25 no new %r" % w)
    K.check("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.25:" in g, "S25 the ready line names the round")
    # fix (critic doc finding): the rollback note matches 0.4.24 - its collectHeld is generic (every non-Combat shard), so it pays farming .drops
    K.check("if (kd == @PKG@.ShCombat.CK || !@PKG@.ShCfg.ON || cs == null) return null;" in o[o.index("public static String collectHeld("):]
            and "never pays farming .drops" not in g and "harvested farming crops still show and pay out on 0.4.24" in g,
            "S25 rollback note: 0.4.24's Collect pays farming .drops (generic collectHeld) and the docstring says so")
    blk = g[g.index("# ---- 0.4.25 THE FARMING CLICKER (tools/shards_0_4_25_patch.py)"):g.index("# THE CLICK: Object[]{ status")]
    K.check("scheduleAtFixedRate" not in blk and "sendUpdate" not in blk, "S25 no periodic page update (HANDOFF section 2)")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S25 the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S25 line endings kept")
    K.check(os.path.getmtime(GEN) >= os.path.getmtime(PATCH) and os.path.getmtime(jar) >= os.path.getmtime(GEN), "S25 jar newer than the script, the script newer than the patch")
    with zipfile.ZipFile(jar) as z:
        names = z.namelist()
        clk = [n for n in names if n.startswith("Common/UI/Custom/SkyyShards/Map/Clk") and n.endswith("@2x.png")]
        f = [n for n in clk if "/ClkF" in n or "/ClkUpF" in n]
        K.check(len(clk) == 66 + 43 + 34 and len(f) == 34 and all(z.read(n)[:8] == b"\x89PNG\r\n\x1a\n" for n in clk), "S25 66 + 43 + 34 clicker pictures (%d, %d farm)" % (len(clk), len(f)))
        K.check(all(("Clk%s@" % t) in " ".join(clk) for t in ["FCrop0", "FCrop14", "FMap0", "FMap14", "FHarv", "UpFSize", "UpFCount", "UpFIrr"]),
                "S25 ... 15 crop plots, 15 map farms, the harvested plot, 3 icons")
        import serverjar as _SJ
        az = zipfile.ZipFile(_SJ.assets_zip())
        van = set(az.getinfo(n).CRC for n in az.namelist() if n.lower().endswith(".png"))
        K.check(not any(z.getinfo(n).CRC in van for n in f), "S25 no farm picture is a vanilla file (CRC)")
    K.save()


def _farm(L, p, size=1, amt=5, irr=0, deco=0, stored=0, lim_tier=5, extra=()):
    St = L["ShStore"]
    St.LOCK.lock()
    try:
        for k_ in list(p.stringPropertyNames()):
            if str(k_).startswith("farming."):
                p.remove(k_)
        for s, ty, sz in [(0, "wheat", size)] + list(extra):
            p.setProperty("farming.i%d.type" % s, ty); p.setProperty("farming.i%d.size" % s, str(sz)); p.setProperty("farming.i%d.last" % s, str(T0))
            p.setProperty("farming.i%d.stored" % s, "0"); p.setProperty("farming.i%d.amt" % s, str(amt))
        p.setProperty("farming.i0.stored", str(stored)); p.setProperty("farming.i0.amt", str(amt)); p.setProperty("farming.i0.irr", str(irr))
        p.setProperty("farming.i0.deco", str(deco)); p.setProperty("farming.auto", "1"); p.setProperty("farming.paused", "0")
        p.setProperty("farming.storage", str(lim_tier)); p.setProperty("farming.i0.totems", "harvest_spirit:1:::0:fa0001")
        p.setProperty("farming.placed", L["W_"] + "|1|2|3")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()


def _env(scratch, K, name):
    from jpype import JClass, JString, JInt
    L, ou, W_, p, lv = T420._W0(os.path.join(scratch, name), K)
    L["W_"] = W_
    L["ShClk"] = JClass(PKG + "ShClk")
    T411.T48.add_items([(WH, 100), (EWH, 64), (WSE, 64), ("Plant_Seeds_Wheat", 64), ("Plant_Crop_Lettuce_Item", 100), ("Skyy_Ench_Lettuce", 64),
                        ("Plant_Seeds_Lettuce_Eternal", 64), ("Plant_Crop_Carrot_Item", 100), ("Skyy_Ench_Carrot", 64), (CORN, 100), ("Skyy_Ench_Corn", 64),
                        ("Plant_Seeds_Corn_Eternal", 64), ("Plant_Crop_Pumpkin_Item", 100), ("Skyy_Ench_Pumpkin", 64), ("Tool_Hoe_Crude", 1), ("Tool_Hoe_Iron", 1),
                        ("Tool_Pickaxe_Copper", 1), ("Tool_Hatchet_Copper", 1), (OAK, 100), ("Skyy_Ench_Oak", 64), ("Ingredient_Water_Essence", 100),
                        ("Ingredient_Life_Essence", 100), ("Rock_Stone_Cobble", 100), ("Plant_Seeds_Wheat_Eternal", 64), ("Ingredient_Fire_Essence", 100)])
    M, Core, Cfg = L["ShMath"], L["ShCore"], L["ShCfg"]
    M.ONLINE.put(OWNER, True)
    Core.NOW_TEST = T0
    Cfg.KEY_TEST = L["PyFn"](lambda u: JString(OWNER))
    lv["Farming"] = 30
    lv["Foraging"] = 30
    lv["Mining"] = 30
    L["ShIsl"].LEVEL_TEST = L["PyFn"](lambda a: JInt(lv[str(a[2])]) if str(a[2]) in lv else JInt(-1))
    got = T420._kit(L, p, K)
    return L, ou, W_, p, lv, got


def _drops(p, slot=0, kind="farming"):
    s = p.getProperty("%s.i%d.drops" % (kind, slot))
    if s is None:
        return {}
    out = {}
    for part in str(s).split(","):
        i, q = part.rsplit(":", 1)
        out[i] = out.get(i, 0) + int(q)
    return out


def _replay(Ck, seed, f, plants, q0, q1, pe):
    """the harvest's rolls, replayed on a second java.util.Random with the same seed (exact): per plant [quantity], Fortune, [Eternal seed]"""
    from jpype import JClass, JDouble, JLong
    r = JClass("java.util.Random")(JLong(seed))
    crop = seed_ = base = 0
    for _ in range(plants):
        q = q0
        if q1 > q0:
            q = min(q1, q0 + int(math.floor(float(r.nextDouble()) * (q1 - q0 + 1))))
        base += q
        crop += q * (1 + int(Ck.extras(JDouble(f), JDouble(float(r.nextDouble())))))
        if pe > 0 and float(r.nextDouble()) < pe:
            seed_ += 1
    return crop, seed_, base


def _vanilla_crops():
    """crop -> (QuantityMin, QuantityMax, Eternal seed id or "", Weight) from Assets.zip's ripe drop lists (the Mushroom has none)"""
    import serverjar as _SJ
    az = zipfile.ZipFile(_SJ.assets_zip())
    names = set(az.namelist())
    out = {}
    for c in CROPS:
        n = "Server/Drops/Crop/%s/Drops_Plant_Crop_%s_StageFinal_Harvest.json" % (c, c)
        if n not in names:
            out[c] = (1, 1, "", None)
            continue
        q, e, w = None, "", None
        stk = [json.loads(az.read(n).decode("utf-8-sig"))]
        while stk:
            x = stk.pop()
            if isinstance(x, dict):
                it = x.get("Item")
                if isinstance(it, dict) and it.get("ItemId") == "Plant_Crop_%s_Item" % c:
                    q = (int(it.get("QuantityMin", 1)), int(it.get("QuantityMax", it.get("QuantityMin", 1))))
                if isinstance(it, dict) and str(it.get("ItemId", "")).endswith("_Eternal") and str(it.get("ItemId", "")).startswith("Plant_Seeds_"):
                    e, w = it["ItemId"], float(x.get("Weight", 100))
                stk.extend(x.values())
            elif isinstance(x, list):
                stk.extend(x)
        out[c] = (q[0], q[1], e, w)
    return out


def run_farm(out, jar, scratch, _home):
    from jpype import JString, JDouble, JClass, JLong, JInt
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "fa")
    M, St, Core, Cfg, Ck, Isl = L["ShMath"], L["ShStore"], L["ShCore"], L["ShCfg"], L["ShClk"], L["ShIsl"]
    br, PyFn = L["br"], L["PyFn"]
    _farm(L, p)
    now = [T0]

    def adv(ms):
        now[0] += ms
        Core.NOW_TEST = now[0]

    def hv(spot=0, hand=None, slot=0):
        r = Ck.chop(ou, JString(OWNER), FK, slot, spot, JString(hand) if hand else None)
        return str(r[0]), str(r[1])

    K.eq(int(Ck.CRK), FK, "FA ShClk.CRK = the Farming kind")
    # the crop data = Assets.zip's ripe drops (vanilla first)
    van = _vanilla_crops()
    K.eq([(int(Ck.F_QMIN[i]), int(Ck.F_QMAX[i]), str(Ck.F_ESEED[i])) for i in range(15)], [(van[c][0], van[c][1], van[c][2]) for c in CROPS],
         "FA the 15 crops' quantities + Eternal seed bags = Assets.zip's StageFinal_Harvest lists")
    K.check(set(van[c][3] for c in CROPS if van[c][2]) == {0.5} and int(Cfg.FQ_ETERNAL) == 5 and van["Mushroom"][2] == "",
            "FA ... vanilla's Eternal seed Weight 0.5 = 0.5 %% = click.farm.eternalPermille 5; the Mushroom has none (%s)" % str(van["Mushroom"]))
    K.eq([str(Ck.F_GROW[i]) for i in (0, 3, 14)], ["Plant_Crop_Wheat_Block", "Plant_Crop_Corn_Block", "Plant_Crop_Mushroom_Block"], "FA the gate / Fortune block = the crop's block")
    K.eq([int(Ck.hoeTier(JString(x))) if x else int(Ck.hoeTier(None)) for x in ("Tool_Hoe_Crude", "Tool_Hoe_Iron", "Tool_Sickle_Harvester_Thorium", "Tool_Sickle_Weird", "Tool_Pickaxe_Copper", None)],
         [1, 2, 4, 1, 0, 0], "FA the hoe / sickle tiers (tier_tags; a pickaxe / bare hands = 0)")
    # the click cap (plot 4, a high HP so nothing is harvested)
    Cfg.FQ_HP = 100
    c0, cap0 = int(Ck.CHOPS.get()), int(Ck.CAPPED.get())
    for _ in range(20):
        hv(spot=4)
    K.eq((int(Ck.CHOPS.get()) - c0, int(Ck.CAPPED.get()) - cap0), (8, 12), "FA the click cap: 8 counted, 12 did nothing")
    K.eq(_drops(p), {}, "FA ... nothing harvested yet")
    Cfg.FQ_HP = 8
    Cfg.CK_CPS = 1000
    adv(1000)
    # bare hands, no SkyyGear: not gated; 8 clicks = a harvest of 3 plants, EXACTLY the replayed rolls
    seed = 31337
    Ck.RND_TEST = JClass("java.util.Random")(JLong(seed))
    xp0 = got["xp"]
    res = [hv() for _ in range(8)]
    Ck.RND_TEST = None
    crop, sd, base = _replay(Ck, seed, 0.0, 3, 1, 2, 0.005)
    want = {WH: crop}
    if sd:
        want[WSE] = sd
    K.check(res[6] == ("", "7 / 8") and res[7][0].startswith("+Harvested a T1 Wheat plot: +%d Wheat" % crop) and res[7][1] == "+%d Wheat" % crop,
            "FA 8 clicks harvest a Wheat plot by hand: %s / %s" % (res[6], res[7]))
    K.eq(_drops(p), want, "FA ... EXACTLY the replayed plants into farming.i0.drops (3 plants x 1-2 Wheat)")
    disk = open(os.path.join(str(St.DIR), OWNER + ".properties"), encoding="utf8").read().replace(chr(92) + ":", ":")
    K.check("farming.i0.drops=" in disk and WH in disk, "FA ... saved at once")
    K.eq(got["xp"] - xp0, 30, "FA ... XP = 25 % of the world's 40 per Wheat plant x 3 = 30")
    K.check("+30 Farming XP" in res[7][0], "FA ... the status names the XP: %s" % res[7][0])
    # the regrow + Irrigation
    s, pp = hv()
    K.check(s.startswith("=That plot is growing back - ") and 0 < int(s.split(" - ")[1].split(" ")[0]) <= 10, "FA a harvested plot regrows (10 s): %s" % s)
    K.eq([int(Ck.farmRegrowMs(i)) for i in (0, 3, 5)], [10000, 7000, 5000], "FA regrow 10 / 7 / 5 s at Irrigation 0 / 3 / 5")
    Cfg.FQ_RMIN = 8
    K.eq(int(Ck.farmRegrowMs(5)), 8000, "FA ... never below click.farm.minRegrowSec")
    Cfg.FQ_RMIN = 3
    # a spot the island does not have; an empty slot
    n = int(Isl.treeN(1, 5))
    s, pp = hv(spot=n)
    K.check(s.startswith("=The page is up to date"), "FA spot %d is not on the island: %s" % (n, s))
    s, pp = hv(slot=5)
    K.check(s.startswith("-That island is not yours yet"), "FA an empty slot: %s" % s)
    # the plot memory is the farm's own: a Foraging tree in slot 0 is untouched; a Mining node too
    K.check(float(Ck.state(JString(OWNER + "|2|0"))[0][4]) > 0 and float(Ck.state(JString(OWNER + "|0"))[0][4]) == 0.0, "FA the farm's damage sits under <key>|2|<slot> (not a tree's / node's)")
    # THE WORLD GATE: gear:fn:farmTier with the crop block + the held item
    calls = []
    ans = [2]

    def gate(a):
        calls.append((str(a[0]), str(a[1]), None if a[2] is None else str(a[2])))
        return JClass("java.lang.Integer").valueOf(ans[0])
    fcalls = []

    def fortune(a):
        fcalls.append((str(a[1]), str(a[2])))
        return JString("ok|2.0|0.4|1|1")
    br.put("gear:fn:farmTier", PyFn(gate))
    br.put("skill:fn:fortune", PyFn(fortune))
    adv(1000)
    c1, g1 = int(Ck.CHOPS.get()), int(Ck.GATED.get())
    s, pp = hv(spot=1)
    K.check(s.startswith("-Bare hands (a Crude hoe) cannot harvest T1 Wheat") and int(Ck.CHOPS.get()) == c1 and int(Ck.GATED.get()) == g1 + 1,
            "FA gate 2 (two tiers up): refused, no hit counted: %s" % s)
    K.eq(calls[-1], (str(ou), "Plant_Crop_Wheat_Block", None), "FA ... SkyyGear is asked with the player, the crop block and bare hands (null)")
    s, pp = hv(spot=1, hand="Tool_Hoe_Iron")
    K.eq(calls[-1][2], "Tool_Hoe_Iron", "FA ... and with the held hoe")
    K.check(s.startswith("-Your ") and "cannot harvest" in s, "FA ... a hoe refused too: %s" % s)
    ans[0] = 1
    nf = len(fcalls)
    s, pp = hv(spot=1, hand="Tool_Hoe_Crude")
    d1 = float(Ck.state(JString(OWNER + "|2|0"))[0][1])
    K.check(s == "" and abs(d1 - 0.4) < 1e-9 and len(fcalls) == nf, "FA gate 1 (one tier up): 0.4 a click (2.5x the clicks), Fortune not asked: %r %s" % (pp, d1))
    seed1 = 4242
    Ck.RND_TEST = JClass("java.util.Random")(JLong(seed1))
    xp1 = got["xp"]
    for _ in range(19):
        s, pp = hv(spot=1, hand="Tool_Hoe_Crude")
    Ck.RND_TEST = None
    c_, s_, b_ = _replay(Ck, seed1, 0.0, 3, 1, 2, 0.005)
    K.check(s.startswith("+Harvested a T1 Wheat plot: +%d Wheat" % c_) and "no Fortune, 50 % XP" in s, "FA ... 20 clicks harvest, no Fortune: %s" % s)
    K.eq(got["xp"] - xp1, 15, "FA ... half XP (3 plants x 10 x 50 % = 15)")
    # gate 0 + Fortune 2.0 (skill:fn:fortune "Farming", the crop block): each plant x3
    ans[0] = 0
    adv(1000)
    _farm(L, p)
    seed2 = 777
    Ck.RND_TEST = JClass("java.util.Random")(JLong(seed2))
    for _ in range(8):
        s, pp = hv(spot=2, hand="Tool_Hoe_Crude")
    Ck.RND_TEST = None
    c_, s_, b_ = _replay(Ck, seed2, 2.0, 3, 1, 2, 0.005)
    K.check(fcalls[-1] == ("Farming", "Plant_Crop_Wheat_Block") and c_ == 3 * b_ and _drops(p).get(WH) == c_, "FA Fortune 2.0 (SkyySkills, Farming, the crop block): each plant x3 (%d of %d base): %s" % (c_, b_, s))
    br.remove("gear:fn:farmTier")
    br.remove("skill:fn:fortune")
    # the Eternal seed (1000 / 1000 = every plant) + storage room: the seeds first, then the crop
    Cfg.FQ_ETERNAL = 1000
    _farm(L, p)
    adv(20000)
    for _ in range(8):
        s, pp = hv(spot=0)
    K.check(_drops(p).get(WSE) == 3 and "Eternal Wheat Seeds" in s, "FA Eternal seed chance 100 %%: 3 plants = 3 Eternal seed bags: %s" % s)
    St.LOCK.lock()
    try:
        lim = int(M.limOf(FK, p, 0))
        p.setProperty("farming.i0.drops", WH + ":1")
        p.setProperty("farming.i0.stored", str(lim - 1 - 2))
        p.setProperty("farming.i0.last", str(now[0]))
    finally:
        St.LOCK.unlock()
    for _ in range(8):
        s, pp = hv(spot=1)
    K.eq(_drops(p), {WH: 1, WSE: 2}, "FA room for 2: the 2 Eternal seed bags first, the crop did not fit")
    K.check("did not fit" in s, "FA ... the status says so: %s" % s)
    Cfg.FQ_ETERNAL = 5
    # storage full: the click does nothing
    c2 = int(Ck.CHOPS.get())
    s, pp = hv(spot=2)
    K.check(s.startswith("-This island's storage is full") and int(Ck.CHOPS.get()) == c2, "FA storage full: nothing happens: %s" % s)
    # a refused save: nothing added, the plot stands again (one click finishes it)
    _farm(L, p)
    adv(20000)
    for _ in range(7):
        hv(spot=0)
    St.FAIL_TEST = True
    s, pp = hv(spot=0)
    St.FAIL_TEST = False
    K.check(s.startswith("-The shard file could not be saved") and _drops(p) == {}, "FA a refused save adds nothing: %s" % s)
    s, pp = hv(spot=0)
    K.check(s.startswith("+Harvested a T1 Wheat plot") and _drops(p).get(WH, 0) >= 3, "FA ... the plot stood again: one click harvests it: %s" % s)
    # switched off
    Cfg.FQ_ON = False
    s, pp = hv(spot=3)
    K.check(s.startswith("-The Farming clicker is switched off"), "FA click.farm.enabled false: %s" % s)
    Cfg.FQ_ON = True
    # a zone 2 crop: Corn (2-4 a plant, the world's 185 XP a plant)
    _farm(L, p, extra=[(3, "corn", 1)])
    adv(20000)
    seed3 = 99
    Ck.RND_TEST = JClass("java.util.Random")(JLong(seed3))
    xp3 = got["xp"]
    for _ in range(8):
        s, pp = hv(spot=0, slot=3)
    Ck.RND_TEST = None
    c_, s_, b_ = _replay(Ck, seed3, 0.0, 3, 2, 4, 0.005)
    K.check(s.startswith("+Harvested a T4 Corn plot: +%d Corn" % c_) and _drops(p, 3).get(CORN) == c_ and 6 <= c_ <= 12, "FA a Corn plot: 3 plants x 2-4 = %d: %s" % (c_, s))
    K.eq(got["xp"] - xp3, int(3 * 185 * 25 // 100), "FA ... XP 25 %% of 185 x 3 (fractions wait): %d" % (got["xp"] - xp3))
    Cfg.CK_CPS = 8
    K.save()


def run_upgrade(out, jar, scratch, _home):
    from jpype import JString
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "fu")
    M, St, Core, Cfg, Ck, Isl, Page = L["ShMath"], L["ShStore"], L["ShCore"], L["ShCfg"], L["ShClk"], L["ShIsl"], L["ShPage"]
    coins = L["coins"]
    _farm(L, p, amt=0)
    cv = float(Cfg.curve(int(Isl.band(1))))
    c1 = int(Ck.nodeCoins(1, cv))
    m1 = Ck.nodeMats(FK, int(Isl.LAD0[FK]), 1)
    K.check(c1 > 0 and [str(x) for x in m1[0]] == [EWH] and [int(x) for x in m1[1]] == [1], "FU Plot size 1 costs %d coins + 1 Enchanted Wheat (= Tree size's rows)" % c1)
    cs = L["inv"](10)
    coins["bal"] = c1 - 1
    r = str(Ck.buyNode(ou, JString(OWNER), FK, 0, 0, cs))
    K.check(r.startswith("-You need"), "FU no Enchanted Wheat: refused: %s" % r)
    cs[0].addItemStack(L["IS"](EWH, 5))
    r = str(Ck.buyNode(ou, JString(OWNER), FK, 0, 0, cs))
    K.check(r.startswith("-You need %s coins" % "{:,}".format(c1)) and int(L["count"](cs, EWH)) == 5, "FU not enough coins: nothing taken: %s" % r)
    coins["bal"] = 1000000
    r = str(Ck.buyNode(ou, JString(OWNER), FK, 0, 0, cs))
    K.check(r.startswith("+Plot size 1/10 on the T1 Wheat island: 4 plants a harvest") and coins["bal"] == 1000000 - c1 and int(L["count"](cs, EWH)) == 4
            and p.getProperty("farming.i0.nsize") == "1", "FU bought: exact coins + 1 Enchanted Wheat, nsize 1: %s" % r)
    r = str(Ck.buyNode(ou, JString(OWNER), FK, 0, 0, cs))
    K.check(r.startswith("=The page is up to date") and coins["bal"] == 1000000 - c1, "FU a stale double click buys once: %s" % r)
    K.eq(int(Ck.plantsAt(1)), 4, "FU ... 4 plants a harvest now")
    St.LOCK.lock()
    try:
        p.setProperty("farming.i0.nsize", "10")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    r = str(Ck.buyNode(ou, JString(OWNER), FK, 0, 10, cs))
    K.check(r.startswith("=Plot size is at its highest"), "FU the highest level: %s" % r)
    Cfg.FQ_ON = False
    r = str(Ck.buyNode(ou, JString(OWNER), FK, 0, 10, cs))
    K.check(r.startswith("-The Farming clicker is switched off"), "FU switched off: %s" % r)
    Cfg.FQ_ON = True
    St.LOCK.lock()
    try:
        p.setProperty("farming.i0.nsize", "0")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    # the page: the rows with the level shown; a stale level refused; Spirit -> the Totems tab
    Page.TEST_INV = cs
    for it_, q_ in ((WH, 100), ("Ingredient_Water_Essence", 64), ("Ingredient_Life_Essence", 64), ("Plant_Seeds_Wheat", 64), (WSE, 64), (EWH, 40), ("Rock_Stone_Cobble", 64), (OAK, 64)):
        cs[0].addItemStack(L["IS"](it_, q_))
    pg = Page(ou, W_)
    pg.kind = FK
    pg.view = 0
    Ck.HAND_TEST = None
    pg.handleDataEvent(None, None, json.dumps({"a": "kopen"}))
    T49._build(pg)
    K.check(int(pg.view) == 5 and bool(pg.ckFarm) and bool(pg.ckUpOk[1]) and str(pg.ckUpE[1]) == "Plots %d -> %d" % (int(Isl.treeN(1, 0)), int(Isl.treeN(1, 1))),
            "FU the Plot count row: %s / %s" % (pg.ckUpE[1], pg.ckUpC[1]))
    K.check(str(pg.ckUpE[0]) == "Plants a harvest 3 -> 4" and bool(pg.ckUpOk[0]), "FU the Plot size row: %s / %s" % (pg.ckUpE[0], pg.ckUpC[0]))
    b0 = coins["bal"]
    pg.handleDataEvent(None, None, json.dumps({"a": "ku1:0"}))
    K.check(p.getProperty("farming.i0.amt") == "1" and coins["bal"] < b0, "FU Plot count bought (= Tree Amount 1): %s" % pg.stText)
    b1 = coins["bal"]
    pg.handleDataEvent(None, None, json.dumps({"a": "ku1:0"}))
    K.check("up to date" in str(pg.stText) and coins["bal"] == b1 and p.getProperty("farming.i0.amt") == "1", "FU ... the same click again buys nothing: %s" % pg.stText)
    pg.handleDataEvent(None, None, json.dumps({"a": "ku3:0"}))
    K.check(p.getProperty("farming.i0.irr") == "1", "FU Irrigation 1 (regrow faster): %s" % pg.stText)
    T49._build(pg)
    K.check(str(pg.ckUpE[3]).startswith("Regrow 9 s -> 8 s"), "FU ... the row now: %s" % pg.ckUpE[3])
    pg.handleDataEvent(None, None, json.dumps({"a": "ku5:0"}))
    K.check(p.getProperty("farming.i0.deco") == "1", "FU Decorations 1: %s" % pg.stText)
    T49._build(pg)
    pg.handleDataEvent(None, None, json.dumps({"a": "ku0:0"}))
    K.check(p.getProperty("farming.i0.nsize") == "1" and str(pg.stText).startswith("Plot size 1/10"), "FU Plot size from the page: %s" % pg.stText)
    # A STALE ISLAND: the slot now holds another crop (another profile / a reset) - no buy, no harvest
    T49._build(pg)
    St.LOCK.lock()
    try:
        p.setProperty("farming.i0.type", "lettuce")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    b2 = coins["bal"]
    pg.handleDataEvent(None, None, json.dumps({"a": "ku0:1"}))
    K.check("up to date" in str(pg.stText) and coins["bal"] == b2 and p.getProperty("farming.i0.nsize") == "1", "FU a stale island (Lettuce in the slot now): no buy: %s" % pg.stText)
    c0 = int(Ck.CHOPS.get())
    pg.handleDataEvent(None, None, json.dumps({"a": "kt0:0"}))
    K.check("up to date" in str(pg.stText) and int(Ck.CHOPS.get()) == c0, "FU ... and no harvest: %s" % pg.stText)
    T49._build(pg)
    K.check(str(pg.ckChip).startswith("T2 Lettuce Island"), "FU ... the next build shows the Lettuce island: %s" % pg.ckChip)
    pg.key = "someone-else"
    pg.handleDataEvent(None, None, json.dumps({"a": "kt0:0"}))
    K.check("up to date" in str(pg.stText) and int(Ck.CHOPS.get()) == c0, "FU another profile key than the page showed: no harvest: %s" % pg.stText)
    T49._build(pg)
    pg.handleDataEvent(None, None, json.dumps({"a": "ku2:1"}))
    K.check(int(pg.view) == 0 and int(pg.tab) == 3 and int(pg.sel) == 1, "FU the Spirit row opens the Totems tab on this island (sel %s)" % pg.sel)
    # a co-op member cannot buy
    Cfg.KEY_TEST = L["PyFn"](lambda u: JString(OWNER if str(u) == str(ou) else str(u)))
    r = str(Ck.buyNode(L["UUID"].fromString(MEMBER), JString(OWNER), FK, 0, -1, cs))
    K.check(r.startswith("-"), "FU a co-op member cannot buy: %s" % r)
    Cfg.KEY_TEST = L["PyFn"](lambda u: JString(OWNER))
    K.save()


def run_zones(out, jar, scratch, _home):
    from jpype import JString
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "fz")
    M, St, Core, Cfg, Ck, Isl, Page = L["ShMath"], L["ShStore"], L["ShCore"], L["ShCfg"], L["ShClk"], L["ShIsl"], L["ShPage"]
    coins = L["coins"]
    L0 = int(Isl.LAD0[FK])
    K.eq([int(Isl.zoneOf(L0 + i)) for i in range(15)], [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5], "FZ three crops a zone")
    K.eq([int(Isl.zoneNeed(FK, L0 + i)) for i in (0, 3, 6, 9, 12)], [0, 20, 40, 60, 80], "FZ the Farming zones open at 0 / 20 / 40 / 60 / 80")
    K.eq([int(Isl.zoneNeed(FO, int(Isl.LAD0[FO]) + i)) for i in (0, 3, 6, 9, 12)], [0, 20, 40, 60, 80], "FZ Foraging's unchanged")
    K.eq([int(Isl.zoneNeed(MI, int(Isl.LAD0[MI]) + i)) for i in (0, 2, 4, 6, 8)], [0, 20, 40, 60, 80], "FZ Mining's unchanged")
    K.eq([int(Isl.zoneNeed(k_, int(Isl.LAD0[k_]) + 4)) for k_ in (3, 4, 5)], [0, 0, 0], "FZ Ranching / Orchard / Combat stay open")
    from jpype import JArray, JInt
    Cfg.FQ_ZLV = JArray(JInt)([0, 10, 40, 60, 80])
    K.eq(int(Isl.zoneNeed(FK, L0 + 3)), 10, "FZ the Server Setup row is live (click.farm.zoneLevel)")
    Cfg.FQ_ZLV = JArray(JInt)([0, 20, 40, 60, 80])
    _farm(L, p, extra=[(1, "lettuce", 1), (2, "carrot", 1)])   # Wheat, Lettuce, Carrot owned -> the next is Corn (Zone 2)
    lv["Farming"] = 19
    cs = L["inv"](20)
    coins["bal"] = 100000000
    r = str(Core.buyIsland(ou, JString(OWNER), FK, 3, cs))
    K.check(r.startswith("-Zone 2 is locked: the T4 Corn island needs Farming 20 (you: 19)"), "FZ Farming 19: the Zone 2 island waits: %s" % r)
    K.eq(int(Isl.slotOf(FK, p, L0 + 3)), -1, "FZ ... nothing bought")
    lv["Farming"] = 20
    r = str(Core.buyIsland(ou, JString(OWNER), FK, 3, cs))
    K.check(not r.startswith("-Zone"), "FZ Farming 20: the lock opens (the cost decides now): %s" % r)
    # an owned island in a locked zone stays open on the map and harvestable
    St.LOCK.lock()
    try:
        p.setProperty("farming.i5.type", str(Isl.KEY[L0 + 6])); p.setProperty("farming.i5.size", "2"); p.setProperty("farming.i5.last", str(T0))
        p.setProperty("farming.i5.stored", "0"); p.setProperty("farming.i5.amt", "5")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    lv["Farming"] = 10
    Ck.HAND_TEST = None
    pg = Page(ou, W_)
    pg.kind = FK
    pg.view = 0
    pg.handleDataEvent(None, None, json.dumps({"a": "kopen"}))
    pg.handleDataEvent(None, None, json.dumps({"a": "kmap"}))
    bd = T49._build(pg)
    r_ = T410.full(pg)
    K.check(not r_["miss"] and not r_["unbound"], "FZ the farm map walks clean %s %s" % (r_["miss"][:2], r_["unbound"][:2]))
    K.check("ZONE 1 FARMS" in bd["mk"] and "ClkFMap0.png" in bd["mk"] and "ClkFMap14.png" in bd["mk"] and "ClkMap1.png" not in bd["mk"], "FZ ... the farm clusters (not the woods)")
    K.check(not bool(pg.ckMLock[6]) and str(pg.ckMS[6]) == "Yours - Medium" and int(pg.ckMB[6]) == 1, "FZ the owned T7 Pumpkin island in locked Zone 3: open (%s)" % pg.ckMS[6])
    K.check(bool(pg.ckMLock[7]) and str(pg.ckMS[7]).startswith("Locked: Farming 40") and "#SkyyShKM7Lk" in bd["mk"], "FZ T8 Aubergine not owned in Zone 3: locked + the lock picture")
    K.check(str(pg.ckZS[1]).startswith("Locked - Farming 20") and "(you: 10)" in str(pg.ckZS[1]), "FZ the Zone 2 header: %s" % pg.ckZS[1])
    pg.handleDataEvent(None, None, json.dumps({"a": "km6"}))
    K.check(int(pg.ckMode) == 0 and int(pg.ckSlot) == 5, "FZ Open = that island in the farm (slot %s)" % pg.ckSlot)
    T49._build(pg)
    K.check(int(pg.ckSz) == 2 and str(pg.ckChip) == "T7 Pumpkin Island - Medium" and str(pg.ckTree).endswith("ClkFCrop6.png"), "FZ ... Medium T7 Pumpkin shown: %s %s" % (pg.ckChip, pg.ckTree))
    Cfg.CK_CPS = 1000
    for _ in range(8):
        pg.handleDataEvent(None, None, json.dumps({"a": "kt0:5"}))
    K.check(str(pg.stText).startswith("Harvested a T7 Pumpkin plot"), "FZ ... harvestable in the locked zone (nothing lost): %s" % pg.stText)
    lv["Farming"] = 30
    pg.handleDataEvent(None, None, json.dumps({"a": "kmap"}))
    bd = T49._build(pg)
    nx = int(pg.ckNext)
    K.check(nx in (3, 4) and int(pg.ckMB[nx]) == 2 and ('"kb%d"' % nx) in bd["datas"].get("#SkyyShKM%dX" % nx, ""), "FZ Farming 30: the next Zone 2 crop (card %d) can be bought from the map" % nx)
    Cfg.CK_CPS = 8
    K.save()


def run_collect(out, jar, scratch, _home):
    from jpype import JString
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "fc")
    M, St, Core, Cfg, Ck = L["ShMath"], L["ShStore"], L["ShCore"], L["ShCfg"], L["ShClk"]
    _farm(L, p, stored=40)
    St.LOCK.lock()
    try:
        p.setProperty("farming.i0.drops", WH + ":25," + WSE + ":2")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    g = dict((str(i), int(q)) for i, q in zip(*Core.gridOf(FK, p)))
    K.check(g.get(WH) == 65 and g.get(WSE) == 2, "FC the grid: the harvested Wheat merged with the stock (25 + 40) + 2 Eternal seed bags: %s" % g)
    K.eq(int(M.usedOf(FK, p, 0)), 67, "FC ... all use the island's storage")
    cs = L["inv"](5)
    got["coll"].clear(); got["xp"] = 0
    r = str(Core.collectKind(ou, JString(OWNER), FK, WH, cs))
    K.check(r.startswith("+Collected 25 Wheat"), "FC a cell click pays the harvested Wheat first, then the stock: %s" % r[:140])
    K.eq(int(L["count"](cs, WH)), 65, "FC ... 65 Wheat in the inventory")
    K.eq(got["coll"].get(WH, 0), 65, "FC ... the Wheat collection +65")
    K.eq(got["xp"], int(40 * int(Cfg.xpOf(FK)) * int(Cfg.XP_PCT) // 100), "FC ... XP only for the stock (the harvested crop paid at the click)")
    r = str(Core.collect(ou, JString(OWNER), FK, -1, cs))
    K.check(int(L["count"](cs, WSE)) == 2 and p.getProperty("farming.i0.drops") is None, "FC Collect all pays the Eternal seed bags: %s" % r[:120])
    St.LOCK.lock()
    try:
        p.setProperty("farming.i0.drops", WH + ":150")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    cs2 = L["inv"](1)
    r = str(Core.collect(ou, JString(OWNER), FK, -1, cs2))
    K.check(r.startswith("+Collected 100 Wheat") and _drops(p) == {WH: 50}, "FC one free slot: 100 out, 50 stay: %s" % r)
    K.save()


def run_page(out, jar, scratch, _home):
    from jpype import JString
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "fp")
    M, St, Core, Cfg, Ck, Isl, Page = L["ShMath"], L["ShStore"], L["ShCore"], L["ShCfg"], L["ShClk"], L["ShIsl"], L["ShPage"]
    _farm(L, p, stored=12)
    Page.TEST_INV = L["inv"](20)
    Ck.HAND_TEST = None
    pf = Page(ou, W_)
    pf.kind = FK
    pf.view = 0
    pf.handleDataEvent(None, None, json.dumps({"a": "tab0"}))
    bm = T49._build(pf)
    K.check("#SkyyShClk" in bm["mk"] and bm["datas"].get("#SkyyShClk", "").find('"kopen"') >= 0, "FP the Farming footer: Shard clicker -> kopen")
    pf.handleDataEvent(None, None, json.dumps({"a": "kopen"}))
    K.eq(int(pf.view), 5, "FP kopen -> the farm (view 5)")
    for sz in (1, 2, 3):
        St.LOCK.lock()
        try:
            p.setProperty("farming.i0.size", str(sz)); p.setProperty("farming.i0.amt", "5"); p.setProperty("farming.i0.deco", "5"); p.setProperty("farming.i0.irr", "5")
            St.save(OWNER, p)
        finally:
            St.LOCK.unlock()
        bd = T49._build(pf)
        r_ = T410.full(pf)
        K.check(not r_["miss"] and not r_["unbound"], "FP size %d walks clean %s %s" % (sz, r_["miss"][:2], r_["unbound"][:2]))
        n = int(Isl.treeN(sz, 5))
        hits = [s_ for s_ in bd["datas"] if s_.startswith("#SkyyShKH")]
        K.eq(len(hits), n, "FP size %d: %d plot squares" % (sz, n))
        K.check(all(('"kt%s:0"' % s_[len("#SkyyShKH"):]) in bd["datas"][s_] for s_ in hits), "FP ... each names its spot + the island slot")
        K.check("ClkFCrop0.png" in bd["mk"] and "ClkTree1.png" not in bd["mk"] and "ClkIsl%d.png" % sz in bd["mk"] and "#SkyyShKWx" in bd["mk"] and "#SkyyShKD4" in bd["mk"],
                "FP ... the Wheat plots, the island, the rain totem (Irrigation), the decorations")
        K.check(bd["sets"].get("#SkyyShKTitle.Text") == "FARMING SHARD" and "Plot size" in bd["mk"] and "Irrigation" in bd["mk"] and "Tree size" not in bd["mk"],
                "FP ... the title + the farm's row names")
        els = bd["mk"].count("{") - bd["mk"].count('"{')
        K.check(els < 1000, "FP ... %d elements (well under ~1,600)" % els)
        K.check(bd["size"] < 1000000, "FP ... the packet stays small (%d bytes)" % bd["size"])
    K.check(str(pf.ckInfo).startswith("Harvesting by hand (a Crude hoe)"), "FP the info line by hand: %s" % pf.ckInfo)
    # a harvest on the page: status, pop, the harvested plot picture
    Cfg.CK_CPS = 1000
    for i in range(8):
        pf.handleDataEvent(None, None, json.dumps({"a": "kt0:0"}))
    bd = T49._build(pf)
    K.check(str(pf.stText).startswith("Harvested a T1 Wheat plot: +") and str(pf.ckPop).startswith("+") and str(pf.ckPop).endswith(" Wheat"), "FP a plot is harvested: %s / %s" % (pf.stText, pf.ckPop))
    K.check("#SkyyShKPop" in bd["mk"] and "ClkFHarv.png" in bd["mk"], "FP ... the gold pop + the harvested plot (sprouts) while it regrows")
    K.check(any(str(x) == WH for x in pf.sgId) and '"gc:%s"' % WH in bd["datas"].get("#SkyyShKC0B", "") + bd["datas"].get("#SkyyShKC1B", ""), "FP the store cell: click = collect Wheat")
    # the map, back, the hoe info line
    pf.handleDataEvent(None, None, json.dumps({"a": "kmap"}))
    bd = T49._build(pf)
    r_ = T410.full(pf)
    K.check(not r_["miss"] and not r_["unbound"] and "ClkFMap0.png" in bd["mk"] and "ZONE 1 FARMS" in bd["mk"], "FP the farm map walks clean")
    pf.handleDataEvent(None, None, json.dumps({"a": "kisl"}))
    Ck.HAND_TEST = "Tool_Hoe_Iron"
    T49._build(pf)
    K.check(str(pf.ckInfo).startswith("Harvesting with your ") and "(T2)" in str(pf.ckInfo), "FP the info line with a hoe: %s" % pf.ckInfo)
    pf.handleDataEvent(None, None, json.dumps({"a": "kback"}))
    K.check(int(pf.view) == 0 and int(pf.tab) == 1, "FP Shard menu -> the menu's Map tab")
    # switched off: no button, kopen refused; the Foraging + Mining clickers untouched
    Cfg.FQ_ON = False
    bm = T49._build(pf)
    pf.handleDataEvent(None, None, json.dumps({"a": "kopen"}))
    K.check("#SkyyShClk" not in bm["mk"] and int(pf.view) == 0 and "switched off" in str(pf.stText), "FP the farm off: no button, kopen refused")
    Cfg.FQ_ON = True
    pfo = Page(ou, W_)
    pfo.kind = FO
    pfo.view = 0
    Ck.HAND_TEST = "Tool_Hatchet_Copper"
    T423._foraging(L, p)
    pfo.handleDataEvent(None, None, json.dumps({"a": "kopen"}))
    bf = T49._build(pfo)
    K.check(int(pfo.view) == 5 and not bool(pfo.ckFarm) and "ClkTree1.png" in bf["mk"] and "ClkFCrop" not in bf["mk"] and bf["sets"].get("#SkyyShKTitle.Text") == "FORAGING SHARD"
            and "Tree size" in bf["mk"], "FP the Foraging clicker still shows its trees + rows")
    pmi = Page(ou, W_)
    pmi.kind = MI
    pmi.view = 0
    Ck.HAND_TEST = "Tool_Pickaxe_Copper"
    T424._mining(L, p)
    pmi.handleDataEvent(None, None, json.dumps({"a": "kopen"}))
    bq = T49._build(pmi)
    K.check(int(pmi.view) == 5 and bool(pmi.ckMine) and not bool(pmi.ckFarm) and "ClkQNode0.png" in bq["mk"] and bq["sets"].get("#SkyyShKTitle.Text") == "MINING SHARD",
            "FP the Mining quarry still shows its nodes")
    Cfg.CK_CPS = 8
    K.save()


EXPECT = {   # 0.4.24 -> 0.4.25: the version texts (CfgFile / CfgFn / CfgRows / ShFill.markFixed / ShStore / the ready line) + the round
    'CfgFile': ['~<clinit>'],
    'CfgFn': ['~m opExport'],
    'CfgRows': ['+m jI', '+m jL', '+m jS', '~<clinit>', '~m header'],   # the kit's ROW HOLDERS joiners (HOLDERS=2: CfgRows1 / CfgRows2 added)
    'ShCfg': ['+f DEF_FQ_XP', '+f DEF_FQ_ZLV', '+f FQ_ETERNAL', '+f FQ_HP', '+f FQ_IRR', '+f FQ_NS_MAX', '+f FQ_NS_PER', '+f FQ_ON', '+f FQ_PLANTS', '+f FQ_REGROW',
              '+f FQ_RMIN', '+f FQ_UP1', '+f FQ_UPXP', '+f FQ_XP', '+f FQ_ZLV', '~<clinit>', '~m loadCfg'],
    'ShClk': ['+f CRK', '+f F_ESEED', '+f F_GROW', '+f F_QMAX', '+f F_QMIN', '+f GATED', '+f GATE_BR', '+f HARVESTED', '+f HOE_ID', '+f HOE_T', '+m eternalP',
              '+m farmGate', '+m farmRegrowMs', '+m farmXp', '+m harvest', '+m hoeTier', '+m plantsAt', '+m toolWord', '~<clinit>', '~m buyNode', '~m chop'],
    'ShFill': ['~m markFixed'],
    'ShIsl': ['~m zoneNeed'],
    'ShPage': ['+f F_CROP', '+f F_HARV', '+f ckFarm', '+m farmFresh', '+m fillFarm', '~<clinit>', '~m act', '~m actClick', '~m build0', '~m buildClick', '~m buildFull',
               '~m fillClick', '~m fillQuarry'],
    'ShStore': ['~m migrate', '~m migrate2', '~m save'],
    'SkyyShardsPlugin': ['~m setup'],
}


def _compare25(out, jar, old_jar, pkg, expect, added, removed=()):
    """the farm's NEW pictures (Map/ClkF*, Map/ClkUpF*) are new only; every other non-class file (the 0.4.23 / 0.4.24 pictures + the Skyglass theme
    included) identical; the kit's class compare runs on a copy of the new jar without the new pictures"""
    NEWP = ("Common/UI/Custom/SkyyShards/Map/ClkF", "Common/UI/Custom/SkyyShards/Map/ClkUpF")
    with zipfile.ZipFile(jar) as a, zipfile.ZipFile(old_jar) as b:
        na, nb = set(a.namelist()), set(b.namelist())
        new = sorted(n for n in na - nb if not n.endswith(".class"))
        assert all(n.startswith(NEWP) for n in new) and len(new) == 34 and not any(n.startswith(NEWP) for n in nb), "C new non-class files: %s" % new[:8]
        gone = sorted(n for n in nb - na if not n.endswith(".class"))
        assert not gone, "C non-class files gone: %s" % gone[:8]
        chg = sorted(n for n in na & nb if not n.endswith(".class") and a.read(n) != b.read(n))
        assert chg == ["manifest.json"], "C changed non-class files: %s" % chg[:8]
    print("C. %d new non-class files (the farm pictures); the 0.4.23 / 0.4.24 pictures + theme unchanged; manifest.json changed" % len(new))
    cp = os.path.join(SCRATCH, "compare-%s.jar" % VERSION)
    with zipfile.ZipFile(jar) as zi, zipfile.ZipFile(cp, "w", zipfile.ZIP_DEFLATED) as zo:
        for n in zi.namelist():
            if not n.startswith(NEWP):
                zo.writestr(n, zi.read(n))
    T419._compare(out, cp, old_jar, pkg, expect, added, removed)


def run_live(out, jar, scratch, home):
    T421.run_live(out, jar, scratch, home)


if __name__ == "__main__":
    HK.run_compare = _compare25
    HK.run(name="SkyyShards", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=["CfgRows1", "CfgRows2"],
           phases=[("static", run_static), ("farm25", run_farm), ("upgrade25", run_upgrade), ("zones25", run_zones), ("collect25", run_collect), ("page25", run_page),
                   ("mine24", T424.run_mine), ("smithy24", T424.run_smithy), ("upgrade24", T424.run_upgrade), ("zones24", T424.run_zones),
                   ("collect24", T424.run_collect), ("fortune24", T424.run_fortune), ("page24", T424.run_page),
                   ("click23", T423.run_click), ("collect23", T423.run_collect), ("upgrade23", T423.run_upgrade), ("zones23", T423.run_zones),
                   ("page23", T423.run_page23),
                   ("combat22", T422.run_combat), ("farm22", T422.run_farm), ("page22", T422.run_page22),
                   ("geo", T421.run_geo), ("rebuild", T421.run_rebuild), ("level", T421.run_level), ("bags", T421.run_bags), ("page21", T421.run_page21),
                   ("comp", T420.run_comp), ("sell20", T420.run_sell), ("mig20", T420.run_mig20), ("ore", T420.run_ore), ("deb", T420.run_deb), ("page20", T420.run_page20), ("livecomp", T420.run_livecomp),
                   ("off", T419.run_off), ("mig", T419.run_mig), ("sell", T419.run_sell), ("page", T419.run_page),
                   ("open", T416._h(T416._g(T416.run_open), True)), ("bytecode", T423.run_bytecode23),
                   ("flows3", T416._h(T416._g(T413.run_flows3))), ("page49", T419.run_page49),
                   ("live", run_live)],
           script=__file__, live=(T416.T46.LIVE_SH, "mods/Skyy_SkyyShards"))
