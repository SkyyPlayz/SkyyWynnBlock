"""Harness for SkyyShards 0.4.24 (shard clicker 2: the Mining quarry + the Smithy - tools/shards_0_4_24_patch.py, on top of 0.4.23).
Build first:
    python tools/shards_0_4_24_patch.py && python SkyyShards/build_skyyshards_0.4.24.py
    python SkyyShards/test_skyyshards_0.4.24.py [--keep]

  S24  static   the patch re-runs to identical bytes; header / VERSION / ready line; no new registerSystem / registerCommand; line endings kept; the jar
                ships the 0.4.23 pictures + the 43 quarry pictures (our own, no vanilla UI file); no periodic page update; the alloy ratio = SkyyWorldGen's
  MN   mine     EXECUTED no pickaxe / a hatchet, the pickaxe tiers, the click cap, a node's hits (T1 / T2 pickaxe, the world's tier gate, 3 up refused),
                a break = EXACT blocks (a seeded Random replayed in Python: cobble each block, ore / Silver / Gold chances, Fortune extras) into
                mining.i0.drops (saved), the XP (25 % of xp.copper per base find that fit), the refill + Springs, spot -> ore (Copper / Iron), a
                non-base slot refused, storage full / room for some (finds first), a refused save (nothing added, the node stands again), switched off,
                a co-op member who may not collect; the spread table (zone weights: Silver most in zone 3; Lucky adds), no other key moved
  SM   smithy   EXECUTED the Auto-Smelt Pole = bars 1 : 1 (ore, Silver, Gold); Smithy II refused without the pole / without coins (nothing taken), bought
                (exact coins + Enchanted Copper, alloyPct 50), a stale double click buys once; the alloy: pct % of the new bars pair with the stock 1 + 1
                -> 2 (an exact replay of the accumulator), bars out = bars in, no partner = no alloy, 0 % = none; the slider < / > (step 10, 0 / 100
                ends, a stale value refused, a refused save unchanged, a member refused)
  MU   upgrade  EXECUTED Vein size (Tree size's costs; exact coins + Enchanted Copper; not enough coins; a stale double click; the highest level),
                Lucky finds (the Ore Amount cost of that level; exact; highest), the page rows ku0..ku7 (stale level refused; Spirit / no-pole Smithy
                -> the Totems tab)
  MZ   zones    EXECUTED Mining zone 1..5 open at Mining 0 / 20 / 40 / 60 / 80 (Onyxium in zone 5), a Zone 2 island refused at Mining 19 (buyIsland0 =
                the Map tab too), not at 20; an owned island in a locked zone keeps its quarry; Foraging's zones unchanged, Farming open
  MC   collect  EXECUTED the grid shows the mined blocks; Collect all / a cell pay them first; the collection credit: a bar = its ore, an alloy = its two
                ores half each, cobble = itself; no XP at Collect; a full inventory keeps the rest; a refused save takes nothing
  FB   fortune  EXECUTED both clickers ask skill:fn:fortune (Mining: the ore block, Foraging: the log) and use its total; a missing / broken answer =
                the 0.4.23 own sum (only.mining / only.foraging filters); the bridge is only read (no write through it)
  MP   page     the Mining footer has Shard clicker (Farming not), kopen -> view 5 quarry; every size walks clean (the node squares carry
                kt<spot>:<base slot>, Copper / Iron node pictures per spot, springs, smithy), the slider row variant walks clean, the quarry map (locked,
                Buy, Open), the title, the element count, the packet size, the quarry off = no button
  then 0.4.23's phases (click23, collect23, upgrade23, zones23, page23) and 0.4.22's / older ones on THIS jar, A verify, C compare, AA audit, live
  START TWICE on a scratch copy of the live data
Exit code 1 on any failure.
"""
import os, sys, importlib.util, subprocess, json, re, zipfile, glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK

VERSION = "0.4.24"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "mine1", "h")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyShards-%s.jar" % VERSION)]
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyShards-0.4.23.jar")
GEN = os.path.join(HERE, "build_skyyshards_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyshards_0.4.23.py")
PATCH = os.path.join(ROOT, "tools", "shards_0_4_24_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.shards."

# the 0.4.23 harness (it loads 0.4.22 and older): its version moves to this one in memory
_T23 = open(os.path.join(HERE, "test_skyyshards_0.4.23.py"), encoding="utf8").read()
_a23 = "_T22.replace('VERSION = \"0.4.22\"', 'VERSION = \"0.4.23\"')"
assert _T23.count(_a23) == 1, "the 0.4.23 harness changed"
_T23 = _T23.replace(_a23, "_T22.replace('VERSION = \"0.4.22\"', 'VERSION = \"0.4.24\"')")
assert _T23.count('VERSION = "0.4.23"' + chr(10)) == 1, "the 0.4.23 harness changed (VERSION)"   # its module line (its static check is not run here)
_T23 = _T23.replace('VERSION = "0.4.23"' + chr(10), 'VERSION = "0.4.24"' + chr(10))
assert _T23.count("""_T22.replace('"arena (SkyyShards 0.4.22) "', '"arena (SkyyShards 0.4.23) "')""") == 1
_T23 = _T23.replace("""_T22.replace('"arena (SkyyShards 0.4.22) "', '"arena (SkyyShards 0.4.23) "')""", """_T22.replace('"arena (SkyyShards 0.4.22) "', '"arena (SkyyShards 0.4.24) "')""")
_argv = list(sys.argv)
T423 = importlib.util.module_from_spec(importlib.util.spec_from_loader("test_skyyshards_0_4_23", loader=None))
T423.__dict__["__file__"] = os.path.join(HERE, "test_skyyshards_0.4.23.py")
exec(compile(_T23, T423.__file__, "exec"), T423.__dict__)
sys.argv[:] = _argv
T422, T421 = T423.T422, T423.T421
T420, T419, T411, T410, T49, T416, T415, T413 = T421.T420, T421.T419, T421.T411, T421.T410, T421.T49, T421.T416, T421.T415, T421.T413
T423.JAR = T422.JAR = T421.JAR = T420.JAR = T419.JAR = T420.T418.JAR = T419.T417.JAR = JAR
T423.SCRATCH = T422.SCRATCH = T421.SCRATCH = T420.SCRATCH = T419.SCRATCH = T420.T418.SCRATCH = T416.SCRATCH = T415.SCRATCH = T419.T417.SCRATCH = SCRATCH
OWNER, MEMBER = T420.OWNER, T420.MEMBER
MI, FO, FK = 0, 1, 2
T0 = 1790000000000
CU, FE, CB = "Ore_Copper", "Ore_Iron", "Rock_Stone_Cobble"
BCU, BFE, BRZ = "Ingredient_Bar_Copper", "Ingredient_Bar_Iron", "Ingredient_Bar_Bronze"
SIL, GOL, BSI, BGO = "Ore_Silver", "Ore_Gold", "Ingredient_Bar_Silver", "Ingredient_Bar_Gold"
ECU = "Skyy_Ench_Copper"


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyShards 0.4.24 - build script') and 'VERSION = "0.4.24"\n' in g, "S24 header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S24 no new %r" % w)
    K.check("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.24:" in g, "S24 the ready line names the round")
    blk = g[g.index("# ---- 0.4.24 THE MINING QUARRY (tools/shards_0_4_24_patch.py)"):g.index("# ================= 0.4.9 ShMap")]
    K.check("scheduleAtFixedRate" not in blk and "sendUpdate" not in blk, "S24 no periodic page update (HANDOFF section 2)")
    K.check("ALLC = ALLC + [ckc]" in g and g.count("ShClk") > o.count("ShClk"), "S24 ShClk carries the quarry")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S24 the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S24 line endings kept")
    K.check(os.path.getmtime(GEN) >= os.path.getmtime(PATCH) and os.path.getmtime(jar) >= os.path.getmtime(GEN), "S24 jar newer than the script, the script newer than the patch")
    # the alloy ratio + pairs = SkyyWorldGen's SkyyAlloy recipes (the SET pin's script)
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    pin = None
    for ln in open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf8"):
        m = re.search(r'\("SkyyWorldGen", "([0-9]+\.[0-9]+\.[0-9]+)"\)', ln)
        if m and pin is None:
            pin = m.group(1)
    wg = open(os.path.join(ROOT, "SkyyWorldGen", "build_skyyworldgen_%s.py" % pin), encoding="utf8").read()
    K.check('_nout = sum(x["Quantity"] for x in _in)' in wg and '_in = [{"ItemId": _a, "Quantity": 1}, {"ItemId": _bb, "Quantity": 1}]' in wg,
            "S24 SkyyWorldGen %s: an alloy = 1 + 1 bars -> 2 (bars out = bars in) - the quarry's ALLOY_OUT 2" % pin)
    for a_, x_, y_ in (("Bronze", "Copper", "Iron"), ("Dusk_SkyWynn", "Thorium", "Lead_SkyWynn"), ("Azurvane_SkyWynn", "Cobalt", "Chromium_SkyWynn"),
                       ("Cinder_SkyWynn", "Adamantite", "Slag_SkyWynn"), ("Lumen_SkyWynn", "Mithril", "Titanium_SkyWynn")):
        K.check(('("Ingredient_Bar_%s", "%s", "Ingredient_Bar_%s", "Ingredient_Bar_%s"' % (a_, a_.split("_")[0], x_, y_)) in wg, "S24 ... the %s pair = SkyyWorldGen's" % a_)
    with zipfile.ZipFile(jar) as z:
        names = z.namelist()
        clk = [n for n in names if n.startswith("Common/UI/Custom/SkyyShards/Map/Clk") and n.endswith("@2x.png")]
        q = [n for n in clk if "/ClkQ" in n or "/ClkUpQ" in n]
        K.check(len(clk) == 66 + 43 and len(q) == 43 and all(z.read(n)[:8] == b"\x89PNG\r\n\x1a\n" for n in clk), "S24 66 + 43 clicker pictures (%d, %d quarry)" % (len(clk), len(q)))
        K.check(all(("Clk%s@" % t) in " ".join(clk) for t in ["QIsl1", "QIsl3", "QNode0", "QNode10", "QRub10", "QMap10", "QSpring", "QSmithy", "UpQLuck", "UpQSmithy"]),
                "S24 ... 3 quarries, 11 nodes / rubble / map quarries, springs, smithy, icons")
        import serverjar as _SJ
        az = zipfile.ZipFile(_SJ.assets_zip())
        van = set(az.getinfo(n).CRC for n in az.namelist() if n.lower().endswith(".png"))
        K.check(not any(z.getinfo(n).CRC in van for n in q), "S24 no quarry picture is a vanilla file (CRC)")
    K.save()


def _mining(L, p, size=1, amt=5, irr=0, deco=0, stored=0, lim_tier=5, iron=True, pole=False, extra=()):
    St = L["ShStore"]
    St.LOCK.lock()
    try:
        for k_ in list(p.stringPropertyNames()):
            if str(k_).startswith("mining."):
                p.remove(k_)
        tot = "quarry_spirit:1:::0:mi0001" + (",autosmelt_pole:1:::1:mi0002" if pole else "")
        isl = [(0, "copper", size)] + ([(1, "iron", 1)] if iron else []) + list(extra)
        for s, ty, sz in isl:
            p.setProperty("mining.i%d.type" % s, ty); p.setProperty("mining.i%d.size" % s, str(sz)); p.setProperty("mining.i%d.last" % s, str(T0))
            p.setProperty("mining.i%d.stored" % s, "0")
        p.setProperty("mining.i0.stored", str(stored)); p.setProperty("mining.i0.amt", str(amt)); p.setProperty("mining.i0.irr", str(irr))
        p.setProperty("mining.i0.deco", str(deco)); p.setProperty("mining.auto", "1"); p.setProperty("mining.paused", "0")
        p.setProperty("mining.storage", str(lim_tier)); p.setProperty("mining.i0.totems", tot)
        p.setProperty("mining.placed", L["W_"] + "|1|2|3")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()


def _env(scratch, K, name):
    from jpype import JClass, JString, JInt
    L, ou, W_, p, lv = T420._W0(os.path.join(scratch, name), K)
    L["W_"] = W_
    L["ShClk"] = JClass(PKG + "ShClk")
    T411.T48.add_items([(CU, 100), (FE, 100), (CB, 100), (BCU, 100), (BFE, 100), (BRZ, 100), (SIL, 100), (GOL, 100), (BSI, 100), (BGO, 100),
                        (ECU, 64), ("Skyy_Ench_Iron", 64), ("Tool_Pickaxe_Copper", 1), ("Tool_Pickaxe_Iron", 1), ("Tool_Hatchet_Copper", 1),
                        ("Ore_Thorium", 100), ("Rock_Sandstone_Cobble", 100), ("Ingredient_Bar_Thorium", 100), ("Ingredient_Water_Essence", 100),
                        ("Wood_Oak_Trunk", 100), ("Skyy_Ench_Oak", 64), ("Ingredient_Fire_Essence", 100), ("Ingredient_Life_Essence", 100)])
    M, Core, Cfg = L["ShMath"], L["ShCore"], L["ShCfg"]
    M.ONLINE.put(OWNER, True)
    Core.NOW_TEST = T0
    Cfg.KEY_TEST = L["PyFn"](lambda u: JString(OWNER))
    lv["Mining"] = 30
    lv["Foraging"] = 30
    L["ShIsl"].LEVEL_TEST = L["PyFn"](lambda a: JInt(lv[str(a[2])]) if str(a[2]) in lv else JInt(-1))
    got = T420._kit(L, p, K)
    return L, ou, W_, p, lv, got


def _drops(p, slot=0):
    s = p.getProperty("mining.i%d.drops" % slot)
    if s is None:
        return {}
    out = {}
    for part in str(s).split(","):
        i, q = part.rsplit(":", 1)
        out[i] = out.get(i, 0) + int(q)
    return out


def _replay(Ck, seed, f, bl, po, ps, pg):
    """the quarry's roll of one broken node, replayed on a second java.util.Random with the same seed (exact)"""
    from jpype import JClass, JDouble
    r = JClass("java.util.Random")(seed)
    cob = ore = sil = gol = base = 0
    for _ in range(bl):
        cob += 1
        if float(r.nextDouble()) < po:
            ore += 1 + int(Ck.extras(JDouble(f), JDouble(float(r.nextDouble())))); base += 1
        if float(r.nextDouble()) < ps:
            sil += 1 + int(Ck.extras(JDouble(f), JDouble(float(r.nextDouble())))); base += 1
        if float(r.nextDouble()) < pg:
            gol += 1 + int(Ck.extras(JDouble(f), JDouble(float(r.nextDouble())))); base += 1
    return cob, ore, sil, gol, base


def run_mine(out, jar, scratch, _home):
    from jpype import JString, JDouble, JClass, JLong
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "mn")
    M, St, Core, Cfg, Ck, Isl = L["ShMath"], L["ShStore"], L["ShCore"], L["ShCfg"], L["ShClk"], L["ShIsl"]
    br = L["br"]
    _mining(L, p)
    now = [T0]

    def adv(ms):
        now[0] += ms
        Core.NOW_TEST = now[0]

    def mine(spot=0, hand="Tool_Pickaxe_Copper", slot=0):
        r = Ck.chop(ou, JString(OWNER), MI, slot, spot, JString(hand) if hand else None)
        return str(r[0]), str(r[1])

    snap = dict((str(k_), str(p.getProperty(k_))) for k_ in p.stringPropertyNames())
    K.eq(int(Ck.MK), MI, "MN ShClk.MK = the Mining kind")
    for h in (None, "Tool_Hatchet_Copper"):
        s, pp = mine(hand=h)
        K.check(s.startswith("-Hold a pickaxe") and pp == "", "MN no pickaxe (%s): %s" % (h, s))
    K.eq([int(Ck.pickTier(JString(x))) for x in ("Tool_Pickaxe_Copper", "Tool_Pickaxe_Iron", "Tool_Hatchet_Pickaxe_Multitool_Dusk_SkyWynn", "Mod_Multitool_Cobalt",
                                                 "Tool_Pickaxe_Weird", "Tool_Hatchet_Iron")], [1, 2, 6, 7, 1, 0], "MN the pickaxe tiers (tier_tags; a multitool counts; a hatchet = 0)")
    # the click cap
    c0, cap0 = int(Ck.CHOPS.get()), int(Ck.CAPPED.get())
    for _ in range(20):
        mine()
    K.eq((int(Ck.CHOPS.get()) - c0, int(Ck.CAPPED.get()) - cap0), (8, 12), "MN the click cap: 8 counted, 12 did nothing")
    K.eq(_drops(p), {}, "MN ... nothing broke yet")
    Cfg.CK_CPS = 1000
    adv(1000)
    # the 4 left break it - EXACT blocks with a seeded Random (no Fortune: no SkyySkills, no skill:bonus)
    seed = 424242
    Ck.RND_TEST = JClass("java.util.Random")(JLong(seed))
    xp0 = got["xp"]
    res = [mine() for _ in range(4)]
    Ck.RND_TEST = None
    po, ps, pg = float(Ck.oreP(0)), float(Ck.rareP(0, 1, False)), float(Ck.rareP(0, 1, True))
    K.eq((po, round(ps, 6), round(pg, 6)), (0.4, 0.01, 0.008), "MN Zone 1 at Lucky 0: ore 40 %, Silver 1 %, Gold 0.8 % a block")
    cob, ore, sil, gol, base = _replay(Ck, seed, 0.0, 3, po, ps, pg)
    want = {}
    for i_, q_ in ((CB, cob), (CU, ore), (SIL, sil), (GOL, gol)):
        if q_:
            want[i_] = q_
    K.check(res[2][1] == "11 / 12" and res[3][0].startswith("+Mined a T1 Copper node: ") and res[3][1] != "", "MN 12 hits break a Copper node: %s / %s" % (res[2], res[3]))
    K.eq(_drops(p), want, "MN ... EXACTLY the replayed blocks into mining.i0.drops (3 cobble + finds)")
    disk = open(os.path.join(str(St.DIR), OWNER + ".properties"), encoding="utf8").read().replace(chr(92) + ":", ":")
    K.check("mining.i0.drops=" in disk and CB in disk, "MN ... saved at once")
    xpw = int((base * 5 * 25) // 100)
    K.check(got["xp"] - xp0 == xpw, "MN ... XP = 25 %% of xp.copper (5) per base find (%d finds -> %d, fractions wait): %d" % (base, xpw, got["xp"] - xp0))
    # a run of breaks with fixed seeds: every break exact; Copper on even spots, Iron on odd spots (T1 pickaxe on T2 Iron = 0.4 a hit = 30 hits)
    tot = dict(_drops(p))
    for spot, seed_ in ((2, 7), (3, 8), (4, 9)):
        adv(1000)
        ore_id = CU if spot % 2 == 0 else FE
        hits = 12 if ore_id == CU else 30
        Ck.RND_TEST = JClass("java.util.Random")(JLong(seed_))
        for i in range(hits):
            s, pp = mine(spot=spot)
            if i == hits - 2:
                K.check(s == "" and pp.endswith(" / 12"), "MN spot %d (%s): still standing after %d hits (%s)" % (spot, ore_id, hits - 1, pp))
        Ck.RND_TEST = None
        K.check(s.startswith("+Mined a T%d " % (1 if ore_id == CU else 2)), "MN spot %d breaks after %d hits: %s" % (spot, hits, s))
        c_, o_, s_, g_, b_ = _replay(Ck, seed_, 0.0, 3, po, ps, pg)
        for i_, q_ in ((CB, c_), (ore_id, o_), (SIL, s_), (GOL, g_)):
            if q_:
                tot[i_] = tot.get(i_, 0) + q_
        K.eq(_drops(p), tot, "MN ... spot %d: exactly the replayed blocks (%s)" % (spot, ore_id))
    # the refill: the same node; Springs
    s, pp = mine(spot=2)
    K.check(s.startswith("=That ore node is refilling - ") and 0 < int(s.split(" - ")[1].split(" ")[0]) <= 10, "MN a broken node refills (10 s from the break): %s" % s)
    K.eq([int(Ck.refillMs(i)) for i in (0, 3, 5)], [10000, 7000, 5000], "MN refill 10 / 7 / 5 s at Springs 0 / 3 / 5")
    Cfg.MQ_RMIN = 8
    K.eq(int(Ck.refillMs(5)), 8000, "MN ... never below click.mine.minRefillSec")
    Cfg.MQ_RMIN = 3
    # a spot the quarry does not have; the Iron island's slot is not the quarry (the base = the zone's lowest island)
    n = int(Isl.treeN(1, 5))
    s, pp = mine(spot=n)
    K.check(s.startswith("=The page is up to date"), "MN spot %d is not on the quarry: %s" % (n, s))
    s, pp = mine(slot=1)
    K.check(s.startswith("=The page is up to date"), "MN the Iron island's slot is not a quarry (Zone 1's base = Copper): %s" % s)
    s, pp = mine(slot=5)
    K.check(s.startswith("-That island is not yours yet"), "MN an empty slot: %s" % s)
    # the tier gate: a Zone 2 quarry (Thorium T4) - 3 tiers above a Copper pickaxe = refused; Iron pickaxe (2 up) = 0.1 a hit
    _mining(L, p, extra=[(2, "thorium", 1)])
    St.LOCK.lock()
    try:
        p.setProperty("mining.i2.amt", "5")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    adv(1000)
    c2 = int(Ck.CHOPS.get())
    s, pp = mine(slot=2)
    K.check(s.startswith("-Your T1 pickaxe is too low a tier for T4 Thorium") and int(Ck.CHOPS.get()) == c2, "MN a Copper pickaxe on T4 Thorium (3 up): refused, no hit counted: %s" % s)
    s, pp = mine(slot=2, hand="Tool_Pickaxe_Iron")
    d1 = float(Ck.state(JString(OWNER + "|2"))[0][0])
    K.check(s == "" and pp.endswith(" / 12") and abs(d1 - 0.1) < 1e-9, "MN an Iron pickaxe on T4 (2 up): 0.1 a hit (10x the hits): %r %s" % (pp, d1))
    # Breaking Power (bp.mining; the gear source never counts) - 1.0 doubles the hit
    CHM, HM = JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.util.HashMap")
    m = CHM()
    acc = HM(); acc.put("bp.mining", JDouble(1.0)); m.put("acc", acc)
    gear = HM(); gear.put("bp.mining", JDouble(5.0)); m.put("gear", gear)
    br.put("skill:bonus:" + str(ou), m)
    for _ in range(3):
        s, pp = mine(spot=6)
    K.check(pp == "6 / 12", "MN Breaking Power 1.0 (the gear source never counts): 2 a hit (3 hits = 6): %s" % pp)
    m.clear()
    # storage full: nothing mined; room for 2: the finds first (a seed with an ore find), then cobble
    _mining(L, p)
    adv(20000)   # every node stands again
    St.LOCK.lock()
    try:
        lim = int(M.limOf(MI, p, 0))
        p.setProperty("mining.i0.stored", str(lim - int(M.heldN(MI, p, 0))))
        p.setProperty("mining.i0.last", str(now[0]))
    finally:
        St.LOCK.unlock()
    c1 = int(Ck.CHOPS.get())
    s, pp = mine(spot=0)
    K.check(s.startswith("-This island's storage is full") and int(Ck.CHOPS.get()) == c1, "MN storage full: the click does nothing: %s" % s)
    seed2 = None
    for sd in range(1, 400):   # a seed whose first block finds ore
        c_, o_, s_, g_, b_ = _replay(Ck, sd, 0.0, 3, po, ps, pg)
        if o_ >= 1 and s_ == 0 and g_ == 0:
            seed2 = sd
            break
    St.LOCK.lock()
    try:
        p.setProperty("mining.i0.stored", str(lim - int(M.heldN(MI, p, 0)) - 2))
    finally:
        St.LOCK.unlock()
    Ck.RND_TEST = JClass("java.util.Random")(JLong(seed2))
    for i in range(12):
        s, pp = mine(spot=0)
    Ck.RND_TEST = None
    c_, o_, s_, g_, b_ = _replay(Ck, seed2, 0.0, 3, po, ps, pg)
    gO_ = min(o_, 2)
    want2 = {CU: gO_}
    if 2 - gO_ > 0:
        want2[CB] = 2 - gO_
    K.check(s.startswith("+Mined a T1 Copper node") and "did not fit" in s and _drops(p) == want2, "MN room for 2: the ore first, then cobble (%s): %s" % (_drops(p), s))
    K.eq(int(M.usedOf(MI, p, 0)), lim, "MN ... the island is exactly full")
    St.LOCK.lock()
    try:
        p.setProperty("mining.i0.stored", "0")
        p.remove("mining.i0.drops")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    # a refused save: nothing added, the node stands again
    adv(1000)
    for i in range(11):
        mine(spot=2)
    before = _drops(p)
    St.FAIL_TEST = True
    s, pp = mine(spot=2)
    St.FAIL_TEST = False
    K.check(s.startswith("-The shard file could not be saved") and _drops(p) == before, "MN a refused save adds nothing: %s" % s)
    s, pp = mine(spot=2)
    K.check(s.startswith("+Mined"), "MN ... the node stood again: one hit breaks it: %s" % s)
    # the quarry switched off; a member who may not collect
    Cfg.MQ_ON = False
    s, pp = mine(spot=0)
    K.check(s.startswith("-The Mining quarry is switched off"), "MN switched off: %s" % s)
    Cfg.MQ_ON = True
    Cfg.COOP_COLLECT = False
    Cfg.KEY_TEST = L["PyFn"](lambda u: JString(OWNER if str(u) == str(ou) else str(u)))
    r = Ck.chop(L["UUID"].fromString(MEMBER), JString(OWNER), MI, 0, 0, JString("Tool_Pickaxe_Copper"))
    K.check(str(r[0]).startswith("-"), "MN a co-op member who may not collect: %s" % r[0])
    Cfg.COOP_COLLECT = True
    Cfg.KEY_TEST = L["PyFn"](lambda u: JString(OWNER))
    # the spread table: zone weights (Silver most in zone 3), Lucky finds adds
    sp = [(round(float(Ck.rareP(0, z, False)) * 100, 4), round(float(Ck.rareP(0, z, True)) * 100, 4)) for z in range(1, 6)]
    K.eq(sp, [(1.0, 0.8), (1.0, 0.8), (2.0, 1.5), (1.0, 0.3), (0.5, 0.3)], "MN Silver / Gold % a block by zone at Lucky 0 (zone 3 the most, Gold small in zones 4-5)")
    K.eq([round(float(Ck.oreP(l)) * 100, 4) for l in range(6)], [40.0, 48.0, 56.0, 64.0, 72.0, 80.0], "MN ore % a block at Lucky 0..5")
    K.eq(round(float(Ck.rareP(5, 3, False)) * 100, 4), 12.0, "MN ... Zone 3 Silver at Lucky 5: (1 + 5) % x 2 = 12 %")
    K.eq([int(Ck.blocksAt(i)) for i in (0, 1, 10)], [3, 4, 13], "MN blocks a node: 3 + Vein size")
    # no migration: the islands' keys are as they were (only production / the quarry's own keys move)
    Cfg.CK_CPS = 8
    _mining(L, p)
    snap2 = dict((str(k_), str(p.getProperty(k_))) for k_ in p.stringPropertyNames())
    K.check(not any(re.search(r"\.(nsize|luck|smithy|alloyPct)$", k_) for k_ in snap2), "MN ... mining keeps no new key but its drops")
    keep = dict((k_, v_) for k_, v_ in snap.items() if not k_.startswith("mining.") and not re.search(r"\.(last|stored|drops|offAt|sacc|seed)$", k_))
    K.eq(dict((k_, snap2.get(k_)) for k_ in keep), keep, "MN no migration: every other shard's keys untouched")
    K.save()


def run_smithy(out, jar, scratch, _home):
    from jpype import JString, JClass, JLong
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "sm")
    M, St, Core, Cfg, Ck, Isl = L["ShMath"], L["ShStore"], L["ShCore"], L["ShCfg"], L["ShClk"], L["ShIsl"]
    coins = L["coins"]
    _mining(L, p, pole=True)
    Cfg.CK_CPS = 1000
    now = [T0]

    def adv(ms):
        now[0] += ms
        Core.NOW_TEST = now[0]

    def brk(spot, seed, hits=None, hand="Tool_Pickaxe_Iron"):
        adv(11000)   # every node stands again
        Ck.RND_TEST = JClass("java.util.Random")(JLong(seed))
        for _ in range(hits or 12):
            s, pp = Ck.chop(ou, JString(OWNER), MI, 0, spot, JString(hand))
        Ck.RND_TEST = None
        return str(s)

    po, ps, pg = float(Ck.oreP(0)), float(Ck.rareP(0, 1, False)), float(Ck.rareP(0, 1, True))
    # the Auto-Smelt Pole: bars 1 : 1 (Copper, Silver, Gold); cobble stays cobble. An Iron pickaxe: Copper 1.25 a hit (10 hits), Iron 1 (12)
    seedS = None
    for sd in range(1, 4000):
        c_, o_, s_, g_, b_ = _replay(Ck, sd, 0.0, 3, po, ps, pg)
        if o_ >= 1 and (s_ >= 1 or g_ >= 1):
            seedS = sd
            break
    s = brk(0, seedS, hits=10)
    c_, o_, s_, g_, b_ = _replay(Ck, seedS, 0.0, 3, po, ps, pg)
    want = dict((i_, q_) for i_, q_ in ((CB, c_), (BCU, o_), (BSI, s_), (BGO, g_)) if q_)
    K.check(s.startswith("+Mined a T1 Copper node") and _drops(p) == want, "SM the pole: ore / Silver / Gold stored as bars 1 : 1, cobble as cobble %s: %s" % (_drops(p), s))
    K.check(not any(k_ in _drops(p) for k_ in (CU, SIL, GOL)), "SM ... no raw ore stored")
    # Smithy II: without the pole refused (nothing taken); not enough coins; bought exactly; a stale double click
    cs = L["inv"](10)
    cs[0].addItemStack(L["IS"](ECU, 40))
    _mining(L, p, pole=False)
    coins["bal"] = 10 ** 9
    r = str(Ck.buySmithy(ou, JString(OWNER), MI, 0, 0, cs))
    K.check(r.startswith("-Place an Auto-Smelt Pole") and coins["bal"] == 10 ** 9 and int(L["count"](cs, ECU)) == 40, "SM Smithy II without the pole: refused, nothing taken: %s" % r)
    _mining(L, p, pole=True)
    cv = float(Cfg.curve(int(Isl.band(1))))
    c1 = int(Ck.smithyCoins(cv))
    m1 = Ck.smithyMats(MI, int(Isl.LAD0[MI]))
    K.check(c1 > 0 and [str(x) for x in m1[0]] == [ECU] and [int(x) for x in m1[1]] == [16], "SM Smithy II costs %d coins (0.25 h of the T1 curve) + 16 Enchanted Copper" % c1)
    coins["bal"] = c1 - 1
    r = str(Ck.buySmithy(ou, JString(OWNER), MI, 0, 0, cs))
    K.check(r.startswith("-You need") and coins["bal"] == c1 - 1 and int(L["count"](cs, ECU)) == 40, "SM not enough coins: nothing taken: %s" % r)
    coins["bal"] = 10 ** 9
    r = str(Ck.buySmithy(ou, JString(OWNER), MI, 0, 0, cs))
    K.check(r.startswith("+Smithy II built: 50 % of the new Copper Ingot and Iron Ingot become Bronze Ingot") and coins["bal"] == 10 ** 9 - c1
            and int(L["count"](cs, ECU)) == 24 and p.getProperty("mining.i0.smithy") == "1" and p.getProperty("mining.i0.alloyPct") == "50", "SM bought: exact coins + 16 Enchanted Copper, slider at 50: %s" % r)
    r = str(Ck.buySmithy(ou, JString(OWNER), MI, 0, 0, cs))
    K.check(r.startswith("=") and coins["bal"] == 10 ** 9 - c1 and int(L["count"](cs, ECU)) == 24, "SM a stale double click buys once: %s" % r)
    # THE ALLOY: Copper (even spots) and Iron (odd spots) bars; each new bar adds 50 / 200 of a pair; pairs from the stock of both; 1 + 1 -> 2
    Ck.ALLOYACC.clear()
    acc = 0.0
    stock = {}
    for i_, (spot, sd) in enumerate(((1, 11), (0, 12), (3, 13), (2, 14), (5, 15), (4, 16), (7, 17), (6, 18))):
        ore_id, bar = (FE, BFE) if spot % 2 else (CU, BCU)
        s = brk(spot, sd, hits=12 if spot % 2 else 10)
        c_, o_, s_, g_, b_ = _replay(Ck, sd, 0.0, 3, po, ps, pg)
        for k_, q_ in ((CB, c_), (bar, o_), (BSI, s_), (BGO, g_)):
            stock[k_] = stock.get(k_, 0) + q_
        pairs = 0
        if o_ > 0:
            acc += o_ * 50 / 200.0
            want_ = int(acc + 1e-9)
            pairs = max(0, min(want_, stock.get(BCU, 0), stock.get(BFE, 0)))
            acc -= want_
            stock[BCU] = stock.get(BCU, 0) - pairs
            stock[BFE] = stock.get(BFE, 0) - pairs
            stock[BRZ] = stock.get(BRZ, 0) + 2 * pairs
        K.eq(_drops(p), dict((k_, v_) for k_, v_ in stock.items() if v_), "SM break %d (%s, %d bars): the stock = the exact replay (pairs %d)" % (i_ + 1, bar, o_, pairs))
    d = _drops(p)
    made = d.get(BRZ, 0)
    K.check(made > 0 and made % 2 == 0, "SM the slider at 50 %% made %d Bronze (2 a pair)" % made)
    K.eq(d.get(BCU, 0) + d.get(BFE, 0) + made, stock.get(BCU, 0) + stock.get(BFE, 0) + stock.get(BRZ, 0), "SM bars out = bars in (no free bar)")
    # no partner: only Copper bars - nothing alloyed
    St.LOCK.lock()
    try:
        p.setProperty("mining.i0.drops", BCU + ":40")
        p.setProperty("mining.i0.alloyPct", "100")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    Ck.ALLOYACC.clear()
    for sp_, sd in ((0, 21), (2, 22)):
        brk(sp_, sd, hits=10)
    K.check(BRZ not in _drops(p) and BFE not in _drops(p), "SM 100 %% but no Iron bar stored: no Bronze (%s)" % _drops(p))
    # 0 %: none
    St.LOCK.lock()
    try:
        p.setProperty("mining.i0.drops", BCU + ":40," + BFE + ":40")
        p.setProperty("mining.i0.alloyPct", "0")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    brk(4, 23, hits=10)
    K.check(BRZ not in _drops(p), "SM 0 %: no Bronze")
    # Smithy without Smithy II (pole only): no alloy whatever the key says
    St.LOCK.lock()
    try:
        p.setProperty("mining.i0.smithy", "0"); p.setProperty("mining.i0.alloyPct", "100")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    brk(6, 24, hits=10)
    K.check(BRZ not in _drops(p), "SM the pole alone (no Smithy II): bars only")
    St.LOCK.lock()
    try:
        p.setProperty("mining.i0.smithy", "1"); p.setProperty("mining.i0.alloyPct", "50")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    # a refused save keeps the accumulator (no half pair gained)
    Ck.ALLOYACC.clear()
    Ck.accSet(JString(OWNER + "|0"), 0.75)
    adv(11000)
    for _ in range(9):
        Ck.chop(ou, JString(OWNER), MI, 0, 0, JString("Tool_Pickaxe_Iron"))
    b4 = _drops(p)
    St.FAIL_TEST = True
    r = Ck.chop(ou, JString(OWNER), MI, 0, 0, JString("Tool_Pickaxe_Iron"))
    St.FAIL_TEST = False
    K.check(str(r[0]).startswith("-The shard file could not be saved") and _drops(p) == b4 and abs(float(Ck.accGet(JString(OWNER + "|0"))) - 0.75) < 1e-9,
            "SM a refused save: the store and the alloy share unchanged: %s" % r[0])
    # the slider: < / >, step 10, the ends, stale, a refused save, a member
    St.LOCK.lock()
    try:
        p.setProperty("mining.i0.alloyPct", "50"); St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    r = str(Ck.setAlloy(ou, JString(OWNER), MI, 0, 50, 1))
    K.check(r == "+Alloy share 60 %." and p.getProperty("mining.i0.alloyPct") == "60", "SM > : 50 -> 60: %s" % r)
    r = str(Ck.setAlloy(ou, JString(OWNER), MI, 0, 50, 1))
    K.check(r.startswith("=The page is up to date") and p.getProperty("mining.i0.alloyPct") == "60", "SM a stale value: refused: %s" % r)
    r = str(Ck.setAlloy(ou, JString(OWNER), MI, 0, 60, -1))
    K.check(p.getProperty("mining.i0.alloyPct") == "50", "SM < : 60 -> 50: %s" % r)
    St.LOCK.lock()
    try:
        p.setProperty("mining.i0.alloyPct", "100"); St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    r = str(Ck.setAlloy(ou, JString(OWNER), MI, 0, 100, 1))
    K.check(r.startswith("=The alloy share is at 100"), "SM the top end: %s" % r)
    St.FAIL_TEST = True
    r = str(Ck.setAlloy(ou, JString(OWNER), MI, 0, 100, -1))
    St.FAIL_TEST = False
    K.check(r.startswith("-The shard file could not be saved") and p.getProperty("mining.i0.alloyPct") == "100", "SM a refused save: unchanged: %s" % r)
    Cfg.KEY_TEST = L["PyFn"](lambda u: JString(OWNER if str(u) == str(ou) else str(u)))
    r = str(Ck.setAlloy(L["UUID"].fromString(MEMBER), JString(OWNER), MI, 0, 100, -1))
    K.check(r.startswith("-") and p.getProperty("mining.i0.alloyPct") == "100", "SM a co-op member cannot move the slider: %s" % r)
    Cfg.KEY_TEST = L["PyFn"](lambda u: JString(OWNER))
    St.LOCK.lock()
    try:
        p.setProperty("mining.i0.smithy", "0"); St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    r = str(Ck.setAlloy(ou, JString(OWNER), MI, 0, 100, -1))
    K.check(r.startswith("-Build Smithy II first"), "SM no slider without Smithy II: %s" % r)
    K.eq([int(Ck.alloyStep(JString("t|x"), JLong(3), 50, JLong(5), JLong(5))), int(Ck.alloyStep(JString("t|x"), JLong(1), 50, JLong(5), JLong(5)))], [0, 1],
         "SM alloyStep: 3 bars at 50 % = 0.75 of a pair (waits), +1 bar = 1.0 -> 1 pair")
    K.eq(int(Ck.alloyStep(JString("t|y"), JLong(8), 100, JLong(10), JLong(2))), 2, "SM ... 4 pairs wanted, 2 Iron bars = 2 pairs, the rest dropped")
    K.check(float(Ck.accGet(JString("t|y"))) < 1e-9, "SM ... no backlog kept")
    Cfg.CK_CPS = 8
    K.save()


def run_upgrade(out, jar, scratch, _home):
    from jpype import JString
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "mu")
    M, St, Core, Cfg, Ck, Isl, Page = L["ShMath"], L["ShStore"], L["ShCore"], L["ShCfg"], L["ShClk"], L["ShIsl"], L["ShPage"]
    coins = L["coins"]
    _mining(L, p, amt=0)
    t0 = int(Isl.LAD0[MI])
    cv = float(Cfg.curve(int(Isl.band(1))))
    # Vein size = 0.4.23's Tree size purchase (same table), Enchanted Copper
    c1 = int(Ck.nodeCoins(1, cv))
    m1 = Ck.nodeMats(MI, t0, 1)
    K.check(c1 > 0 and [str(x) for x in m1[0]] == [ECU] and [int(x) for x in m1[1]] == [1], "MU Vein size 1 costs %d coins + 1 Enchanted Copper (Tree size's numbers)" % c1)
    cs = L["inv"](10)
    coins["bal"] = c1 - 1
    cs[0].addItemStack(L["IS"](ECU, 5))
    r = str(Ck.buyNode(ou, JString(OWNER), MI, 0, 0, cs))
    K.check(r.startswith("-You need") and int(L["count"](cs, ECU)) == 5, "MU not enough coins: nothing taken: %s" % r)
    coins["bal"] = 10 ** 9
    r = str(Ck.buyNode(ou, JString(OWNER), MI, 0, 0, cs))
    K.check(r.startswith("+Vein size 1/10 on the Zone 1 quarry: 4 blocks a mined node") and coins["bal"] == 10 ** 9 - c1 and int(L["count"](cs, ECU)) == 4
            and p.getProperty("mining.i0.nsize") == "1", "MU bought: exact coins + 1 Enchanted Copper: %s" % r)
    r = str(Ck.buyNode(ou, JString(OWNER), MI, 0, 0, cs))
    K.check(r.startswith("=The page is up to date") and coins["bal"] == 10 ** 9 - c1, "MU a stale double click buys once: %s" % r)
    St.LOCK.lock()
    try:
        p.setProperty("mining.i0.nsize", "10"); St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    r = str(Ck.buyNode(ou, JString(OWNER), MI, 0, 10, cs))
    K.check(r.startswith("=Vein size is at its highest"), "MU the highest Vein size: %s" % r)
    # Lucky finds = the Ore Amount cost of that level
    from jpype import JClass
    for q_ in ("Ingredient_Bar_Copper", "Ingredient_Water_Essence", "Rock_Stone_Cobble", "Ingredient_Fire_Essence", "Ingredient_Life_Essence", "Wood_Oak_Trunk"):
        cs[0].addItemStack(L["IS"](q_, 100))
    cl = int(Isl.coins(float(Isl.subH(1, 1)), cv))
    ml = Isl.mats(MI, t0, JClass(PKG + "ShCombat").subMat(MI, 0), 0, 1)
    before = dict((str(i_), int(L["count"](cs, str(i_)))) for i_ in ml[0])
    b0 = coins["bal"]
    r = str(Ck.buyLuck(ou, JString(OWNER), MI, 0, 0, cs))
    after = dict((str(i_), int(L["count"](cs, str(i_)))) for i_ in ml[0])
    K.check(r.startswith("+Lucky finds 1/5 on the Zone 1 quarry: ore 48 % a block") and b0 - coins["bal"] == cl
            and all(before[str(i_)] - after[str(i_)] == int(q_) for i_, q_ in zip(ml[0], ml[1])) and p.getProperty("mining.i0.luck") == "1",
            "MU Lucky finds 1: exact Ore Amount 1 cost (%d coins + %s): %s" % (cl, [(str(a), int(b)) for a, b in zip(ml[0], ml[1])], r))
    r = str(Ck.buyLuck(ou, JString(OWNER), MI, 0, 0, cs))
    K.check(r.startswith("=The page is up to date") and p.getProperty("mining.i0.luck") == "1", "MU ... a stale double click buys once: %s" % r)
    St.LOCK.lock()
    try:
        p.setProperty("mining.i0.luck", "5"); St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    r = str(Ck.buyLuck(ou, JString(OWNER), MI, 0, 5, cs))
    K.check(r.startswith("=Lucky finds is at its highest"), "MU the highest Lucky finds: %s" % r)
    Cfg.KEY_TEST = L["PyFn"](lambda u: JString(OWNER if str(u) == str(ou) else str(u)))
    r = str(Ck.buyLuck(L["UUID"].fromString(MEMBER), JString(OWNER), MI, 0, -1, cs))
    K.check(r.startswith("-"), "MU a co-op member cannot buy: %s" % r)
    Cfg.KEY_TEST = L["PyFn"](lambda u: JString(OWNER))
    # the page rows
    _mining(L, p, amt=0)
    Page.TEST_INV = cs
    pg = Page(ou, W_)
    pg.kind = MI
    pg.view = 0
    Ck.HAND_TEST = "Tool_Pickaxe_Copper"
    pg.handleDataEvent(None, None, json.dumps({"a": "kopen"}))
    T49._build(pg)
    K.check(int(pg.view) == 5 and bool(pg.ckMine) and len(pg.ckUpL) == 8 and bool(pg.ckUpOk[1]) and str(pg.ckUpE[1]) == "Nodes %d -> %d" % (int(Isl.treeN(1, 0)), int(Isl.treeN(1, 1))),
            "MU the Ore nodes row: %s / %s" % (pg.ckUpE[1], pg.ckUpC[1]))
    b0 = coins["bal"]
    pg.handleDataEvent(None, None, json.dumps({"a": "ku1:0"}))
    K.check(p.getProperty("mining.i0.amt") == "1" and coins["bal"] < b0, "MU Ore nodes bought through the page: %s" % pg.stText)
    b1 = coins["bal"]
    pg.handleDataEvent(None, None, json.dumps({"a": "ku1:0"}))
    K.check("up to date" in str(pg.stText) and coins["bal"] == b1, "MU ... the same click again buys nothing: %s" % pg.stText)
    pg.handleDataEvent(None, None, json.dumps({"a": "ku3:0"}))
    K.check(p.getProperty("mining.i0.irr") == "1", "MU Springs = Underground Springs 1: %s" % pg.stText)
    pg.handleDataEvent(None, None, json.dumps({"a": "ku5:0"}))
    K.check(p.getProperty("mining.i0.deco") == "1", "MU Decorations 1: %s" % pg.stText)
    pg.handleDataEvent(None, None, json.dumps({"a": "ku0:0"}))
    K.check(p.getProperty("mining.i0.nsize") == "1", "MU Vein size through the page: %s" % pg.stText)
    pg.handleDataEvent(None, None, json.dumps({"a": "ku6:0"}))
    K.check(p.getProperty("mining.i0.luck") == "1", "MU Lucky finds through the page: %s" % pg.stText)
    pg.handleDataEvent(None, None, json.dumps({"a": "ku4:1"}))
    K.check("Max all 3 upgrades first" in str(pg.stText) and p.getProperty("mining.i0.size") == "1", "MU Island size waits for 5 / 5 / 5: %s" % pg.stText)
    T49._build(pg)
    K.eq(int(pg.ckQSm), 0, "MU no pole = Smithy state 0")
    pg.handleDataEvent(None, None, json.dumps({"a": "ku7:0"}))
    K.check(int(pg.view) == 0 and int(pg.tab) == 3, "MU the Smithy row without a pole opens the Totems tab")
    pg.view = 5
    pg.handleDataEvent(None, None, json.dumps({"a": "ku2:1"}))
    K.check(int(pg.view) == 0 and int(pg.tab) == 3 and int(pg.sel) == 0, "MU the Miner spirits row opens the Totems tab on this quarry")
    # fix (critic 1): a stale slot (e.g. after a profile switch) that is not the zone's quarry (base) island never buys
    b0 = coins["bal"]
    r = str(Ck.buyLuck(ou, JString(OWNER), MI, 1, 0, cs))
    K.check(r.startswith("=The page is up to date") and p.getProperty("mining.i1.luck") is None and coins["bal"] == b0, "MU FIX Lucky finds on the Iron (non-base) slot: refused, nothing paid: %s" % r)
    r = str(Ck.buySmithy(ou, JString(OWNER), MI, 1, 0, cs))
    K.check(r.startswith("=The page is up to date") and p.getProperty("mining.i1.smithy") is None and coins["bal"] == b0, "MU FIX Smithy II on a non-base slot: refused: %s" % r)
    r = str(Ck.setAlloy(ou, JString(OWNER), MI, 1, 50, 1))
    K.check(r.startswith("=The page is up to date") and p.getProperty("mining.i1.alloyPct") is None, "MU FIX the slider on a non-base slot: refused: %s" % r)
    for row_ in (0, 1, 3, 5, 6):
        pg.view = 5
        pg.ckSlot = 1
        pg.handleDataEvent(None, None, json.dumps({"a": "ku%d:0" % row_}))
        K.check(coins["bal"] == b0 and all(p.getProperty("mining.i1." + k_) is None for k_ in ("nsize", "amt", "irr", "deco", "luck")),
                "MU FIX page row %d on a stale non-base slot buys nothing: %s" % (row_, pg.stText))
    K.check(p.getProperty("mining.i0.luck") == "1" and p.getProperty("mining.i0.amt") == "1", "MU FIX ... the quarry's own levels unchanged")
    K.save()


def run_zones(out, jar, scratch, _home):
    from jpype import JString
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "mz")
    M, St, Core, Cfg, Ck, Isl, Page = L["ShMath"], L["ShStore"], L["ShCore"], L["ShCfg"], L["ShClk"], L["ShIsl"], L["ShPage"]
    coins = L["coins"]
    L0 = int(Isl.LAD0[MI])
    K.eq([int(Isl.zoneOf(L0 + i)) for i in range(11)], [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 5], "MZ two ores a zone (Onyxium T16 in zone 5)")
    K.eq([int(Isl.zoneNeed(MI, L0 + i)) for i in (0, 2, 4, 6, 8, 10)], [0, 20, 40, 60, 80, 80], "MZ the Mining zones open at 0 / 20 / 40 / 60 / 80")
    LF = int(Isl.LAD0[FO])
    K.eq([int(Isl.zoneNeed(FO, LF + i)) for i in (0, 3, 6, 9, 12)], [0, 20, 40, 60, 80], "MZ Foraging's zones unchanged")
    K.eq(int(Isl.zoneNeed(FK, int(Isl.LAD0[FK]) + 5)), 0, "MZ Farming open")
    _mining(L, p)   # Copper + Iron -> the next is Thorium (Zone 2)
    lv["Mining"] = 19
    cs = L["inv"](20)
    coins["bal"] = 10 ** 9
    r = str(Core.buyIsland(ou, JString(OWNER), MI, 2, cs))
    K.check(r.startswith("-Zone 2 is locked: the T4 Thorium island needs Mining 20 (you: 19)"), "MZ Mining 19: the Zone 2 island waits: %s" % r)
    K.eq(int(Isl.slotOf(MI, p, L0 + 2)), -1, "MZ ... nothing bought")
    lv["Mining"] = 20
    r = str(Core.buyIsland(ou, JString(OWNER), MI, 2, cs))
    K.check(not r.startswith("-Zone"), "MZ Mining 20: the lock opens (the cost decides now): %s" % r)
    # an owned island in a locked zone keeps its quarry; the map
    _mining(L, p, extra=[(4, "cobalt", 2)])
    lv["Mining"] = 10
    Ck.HAND_TEST = "Tool_Pickaxe_Copper"
    pg = Page(ou, W_)
    pg.kind = MI
    pg.view = 0
    pg.handleDataEvent(None, None, json.dumps({"a": "kopen"}))
    pg.handleDataEvent(None, None, json.dumps({"a": "kmap"}))
    bd = T49._build(pg)
    r_ = T410.full(pg)
    K.check(not r_["miss"] and not r_["unbound"], "MZ the quarry map walks clean %s %s" % (r_["miss"][:2], r_["unbound"][:2]))
    K.check(not bool(pg.ckMLock[6]) and str(pg.ckMS[6]) == "Yours - in the Zone 3 quarry" and int(pg.ckMB[6]) == 1, "MZ the owned Cobalt island in locked Zone 3: open (%s)" % pg.ckMS[6])
    K.check(bool(pg.ckMLock[7]) and str(pg.ckMS[7]).startswith("Locked: Mining 40") and "#SkyyShKM7Lk" in bd["mk"], "MZ Chromium not owned in Zone 3: locked + the lock picture")
    K.check(str(pg.ckZS[1]).startswith("Locked - Mining 20") and "(you: 10)" in str(pg.ckZS[1]), "MZ the Zone 2 header: %s" % pg.ckZS[1])
    K.check(int(pg.ckMB[0]) == 0 and str(pg.ckMS[0]).startswith("Shown now") and str(pg.ckMS[1]).startswith("Shown now"), "MZ Zone 1's two ores = the quarry shown: %s / %s" % (pg.ckMS[0], pg.ckMS[1]))
    K.check(int(pg.ckMB[3]) == 0 and "#SkyyShKM3X" not in bd["datas"], "MZ the next island (Thorium, card 3) locked at Mining 10: no Buy button")
    K.check(all(("#SkyyShKM%d " % c_) not in bd["mk"] and ("#SkyyShKM%dG" % c_) not in bd["mk"] for c_ in (2, 5, 8, 11)) and "#SkyyShKM14G" in bd["mk"] and "#SkyyShKM10G" in bd["mk"],
            "MZ the map: 2 cards a zone (no card 2 / 5 / 8 / 11), 3 in zone 5")
    pg.handleDataEvent(None, None, json.dumps({"a": "km6"}))
    K.check(int(pg.ckMode) == 0 and int(pg.ckSlot) == 4, "MZ Open = the Zone 3 quarry (slot %s)" % pg.ckSlot)
    T49._build(pg)
    K.check(int(pg.ckSz) == 2 and str(pg.ckChip) == "Zone 3 Quarry - Medium" and int(pg.ckZone) == 3, "MZ ... Medium Zone 3 shown: %s" % pg.ckChip)
    lv["Mining"] = 30
    pg.handleDataEvent(None, None, json.dumps({"a": "kmap"}))
    bd = T49._build(pg)
    K.check(int(pg.ckMB[3]) == 2 and '"kb3"' in bd["datas"].get("#SkyyShKM3X", ""), "MZ Mining 30: Thorium can be bought from the map (kb3)")
    K.save()


def run_collect(out, jar, scratch, _home):
    from jpype import JString
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "mc")
    M, St, Core, Cfg, Ck = L["ShMath"], L["ShStore"], L["ShCore"], L["ShCfg"], L["ShClk"]
    _mining(L, p, stored=0)
    St.LOCK.lock()
    try:
        p.setProperty("mining.i0.drops", "%s:10,%s:7,%s:6,%s:5,%s:2" % (CB, BCU, BRZ, BFE, BSI))
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    g = dict((str(i), int(q)) for i, q in zip(*Core.gridOf(MI, p)))
    K.eq(g, {CB: 10, BCU: 7, BRZ: 6, BFE: 5, BSI: 2}, "MC the grid shows the mined blocks")
    K.eq(int(M.usedOf(MI, p, 0)), 30, "MC ... they use the quarry's storage")
    cs = L["inv"](10)
    got["coll"].clear(); got["xp"] = 0
    r = str(Core.collect(ou, JString(OWNER), MI, -1, cs))
    K.check(r.startswith("+Collected ") and "(chopped)" in r, "MC Collect all pays them: %s" % r[:160])
    K.eq(dict((i_, int(L["count"](cs, i_))) for i_ in (CB, BCU, BRZ, BFE, BSI)), {CB: 10, BCU: 7, BRZ: 6, BFE: 5, BSI: 2}, "MC ... every item in the inventory")
    K.eq(dict((k_, v_) for k_, v_ in got["coll"].items() if v_), {CB: 10, CU: 7 + 3, FE: 5 + 3, SIL: 2},
         "MC the collection credit: a bar = its ore, 6 Bronze = 3 Copper + 3 Iron, cobble = itself, a Silver bar = Silver Ore")
    K.eq(got["xp"], 0, "MC ... no XP at Collect (the click paid it)")
    K.check(p.getProperty("mining.i0.drops") is None, "MC ... the store is empty")
    St.LOCK.lock()
    try:
        p.setProperty("mining.i0.drops", "%s:150" % BCU)
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    r = str(Core.collect(ou, JString(OWNER), MI, -1, L["inv"](1)))
    K.check(r.startswith("+Collected 100 Copper Ingot (chopped). 50 did not fit") and _drops(p) == {BCU: 50}, "MC one free slot: 100 out, 50 stay: %s" % r)
    St.FAIL_TEST = True
    r = str(Core.collect(ou, JString(OWNER), MI, -1, L["inv"](5)))
    St.FAIL_TEST = False
    K.check(r.startswith("-Collect failed") and _drops(p) == {BCU: 50}, "MC a refused save takes nothing: %s" % r)
    cs2 = L["inv"](5)
    got["coll"].clear()
    r = str(Core.collectKind(ou, JString(OWNER), MI, BCU, cs2))
    K.check(int(L["count"](cs2, BCU)) == 50 and p.getProperty("mining.i0.drops") is None and got["coll"].get(CU) == 50, "MC a cell pays its kind, credited as Copper Ore: %s" % r)
    K.eq([int(Core.owedAs(L["UUID"].fromString(OWNER), JString(x), 0)) for x in (BRZ,)], [0], "MC owedAs of nothing = 0")
    # fix (critic 2): one alloy bar at a time credits the two ores in turn (A, B, A, B), never always A
    got["coll"].clear()
    for _n in range(4):
        Core.owedAs(L["UUID"].fromString(OWNER), JString(BRZ), 1)
    K.eq(dict((k_, v_) for k_, v_ in got["coll"].items() if v_), {CU: 2, FE: 2}, "MC FIX 4 Bronze one at a time = 2 Copper + 2 Iron")
    got["coll"].clear()
    Core.owedAs(L["UUID"].fromString(OWNER), JString(BRZ), 3)
    Core.owedAs(L["UUID"].fromString(OWNER), JString(BRZ), 1)
    K.eq(dict((k_, v_) for k_, v_ in got["coll"].items() if v_), {CU: 2, FE: 2}, "MC FIX 3 then 1 Bronze = 2 Copper + 2 Iron (the turn carries over)")
    K.eq(str(Core.oreOfBar(JString("Ingredient_Bar_Dusk_SkyWynn"))) if Core.oreOfBar(JString("Ingredient_Bar_Dusk_SkyWynn")) else None, None, "MC an alloy is no bar of one ore")
    K.eq([str(Core.oreOfBar(JString(x))) for x in (BCU, "Ingredient_Bar_Lead_SkyWynn", BGO)], [CU, "Ore_Lead_SkyWynn", GOL], "MC bar -> ore (ladder, zone metal, Gold)")
    K.save()


def run_fortune(out, jar, scratch, _home):
    from jpype import JString, JDouble, JClass, JLong
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "fb")
    M, St, Core, Cfg, Ck = L["ShMath"], L["ShStore"], L["ShCore"], L["ShCfg"], L["ShClk"]
    br, PyFn = L["br"], L["PyFn"]
    calls = []
    ans = ["ok|2.0|0.4|1|1"]

    def fortune(a):
        calls.append((str(a[0]), str(a[1]), str(a[2])))
        return JString(ans[0]) if ans[0] is not None else None
    br.put("skill:fn:fortune", PyFn(fortune))
    K.eq(float(Ck.fortuneOf(ou, "Mining", "Ore_Copper_Stone", "dd.mining", "only.mining")), 2.0, "FB the quarry asks SkyySkills: 2.0")
    K.eq(calls[-1], (str(ou), "Mining", "Ore_Copper_Stone"), "FB ... with the player, Mining and the ore block")
    K.eq(float(Ck.fortune(ou, JString("Wood_Oak_Trunk"))), 2.0, "FB the Foraging clicker too")
    K.eq(calls[-1][1:], ("Foraging", "Wood_Oak_Trunk"), "FB ... with Foraging and the log")
    # a break at Fortune 2.0: every find = 1 + exactly 2 extras (deterministic), cobble unchanged
    _mining(L, p)
    Cfg.CK_CPS = 1000
    Core.NOW_TEST = T0 + 5000
    seed = 99
    Ck.RND_TEST = JClass("java.util.Random")(JLong(seed))
    for _ in range(12):
        s, pp = Ck.chop(ou, JString(OWNER), MI, 0, 0, JString("Tool_Pickaxe_Copper"))
    Ck.RND_TEST = None
    po, ps_, pg_ = float(Ck.oreP(0)), float(Ck.rareP(0, 1, False)), float(Ck.rareP(0, 1, True))
    c_, o_, s_, g_, b_ = _replay(Ck, seed, 2.0, 3, po, ps_, pg_)
    want = dict((i_, q_) for i_, q_ in ((CB, c_), (CU, o_), (SIL, s_), (GOL, g_)) if q_)
    K.check(_drops(p) == want and o_ == 3 * (b_ - (s_ + g_) // 3), "FB a break at Fortune 2.0 = the exact replay, each find x3 (%s)" % want)
    # a broken / missing answer = the 0.4.23 own sum with the only.<skill> filter
    m = JClass("java.util.concurrent.ConcurrentHashMap")()
    gear = JClass("java.util.HashMap")(); gear.put("dd.mining", JDouble(1.0)); gear.put("only.mining", "Ore_"); m.put("gear", gear)
    tr = JClass("java.util.HashMap")(); tr.put("dd.mining", JDouble(0.5)); m.put("trees", tr)
    br.put("skill:bonus:" + str(ou), m)
    for a_ in ("garbage", "ok|NaN|0|1|1", None):
        ans[0] = a_
        K.eq(round(float(Ck.fortuneOf(ou, "Mining", "Ore_Copper_Stone", "dd.mining", "only.mining")), 6), 1.5, "FB answer %r: the own sum 1.5 (pickaxe on ore + tree)" % a_)
    K.eq(round(float(Ck.fortuneOf(ou, "Mining", "Rock_Stone", "dd.mining", "only.mining")), 6), 0.5, "FB ... the pickaxe's only.mining does not name stone (0.5)")
    br.remove("skill:fn:fortune")
    K.eq(round(float(Ck.fortuneOf(ou, "Mining", "Ore_Copper_Stone", "dd.mining", "only.mining")), 6), 1.5, "FB no SkyySkills 0.4.72: the own sum")
    K.check(br.get("skill:fn:fortune") is None and br.get("skill:bonus:" + str(ou)) is not None and int(br.get("skill:bonus:" + str(ou)).size()) == 2 and int(m.size()) == 2
            and int(gear.size()) == 2 and int(tr.size()) == 1, "FB the bridge is only read (nothing written through it)")
    ans[0] = "ok|-3|0|1|1"
    br.put("skill:fn:fortune", PyFn(fortune))
    K.eq(float(Ck.fortuneOf(ou, "Mining", "Ore_Copper_Stone", "dd.mining", "only.mining")), 0.0, "FB a negative answer = 0")
    br.remove("skill:fn:fortune")
    br.remove("skill:bonus:" + str(ou))
    Cfg.CK_CPS = 8
    K.save()


def run_page(out, jar, scratch, _home):
    from jpype import JString
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "mp")
    M, St, Core, Cfg, Ck, Isl, Page = L["ShMath"], L["ShStore"], L["ShCore"], L["ShCfg"], L["ShClk"], L["ShIsl"], L["ShPage"]
    _mining(L, p, stored=12)
    Page.TEST_INV = L["inv"](20)
    Ck.HAND_TEST = "Tool_Pickaxe_Copper"
    pg = Page(ou, W_)
    pg.kind = MI
    pg.view = 0
    pg.handleDataEvent(None, None, json.dumps({"a": "tab0"}))
    bm = T49._build(pg)
    K.check("#SkyyShClk" in bm["mk"] and bm["datas"].get("#SkyyShClk", "").find('"kopen"') >= 0, "MP the Mining footer: Shard clicker -> kopen")
    pf = Page(ou, W_)
    pf.kind = FK
    pf.view = 0
    K.check("#SkyyShClk" not in T49._build(pf)["mk"], "MP the Farming footer has no clicker")
    pg.handleDataEvent(None, None, json.dumps({"a": "kopen"}))
    K.eq(int(pg.view), 5, "MP kopen -> the quarry (view 5)")
    L0 = int(Isl.LAD0[MI])
    for sz in (1, 2, 3):
        for pole, smy in ((False, 0), (True, 0), (True, 1)):
            St.LOCK.lock()
            try:
                p.setProperty("mining.i0.size", str(sz)); p.setProperty("mining.i0.amt", "5"); p.setProperty("mining.i0.deco", "5"); p.setProperty("mining.i0.irr", "5")
                p.setProperty("mining.i0.totems", "quarry_spirit:1:::0:mi0001" + (",autosmelt_pole:1:::1:mi0002" if pole else ""))
                p.setProperty("mining.i0.smithy", str(smy))
                St.save(OWNER, p)
            finally:
                St.LOCK.unlock()
            bd = T49._build(pg)
            r_ = T410.full(pg)
            K.check(not r_["miss"] and not r_["unbound"], "MP size %d pole %s Smithy II %d walks clean %s %s" % (sz, pole, smy, r_["miss"][:2], r_["unbound"][:2]))
            n = int(Isl.treeN(sz, 5))
            hits = [s_ for s_ in bd["datas"] if s_.startswith("#SkyyShKH")]
            K.eq(len(hits), n, "MP ... %d node squares" % n)
            K.check(all(('"kt%s:0"' % s_[len("#SkyyShKH"):]) in bd["datas"][s_] for s_ in hits), "MP ... each names its spot + the quarry's base slot")
            K.check("ClkQIsl%d.png" % sz in bd["mk"] and "ClkQNode0.png" in bd["mk"] and "ClkQNode1.png" in bd["mk"] and "ClkTree" not in bd["mk"] and "#SkyyShKWx" in bd["mk"],
                    "MP ... the quarry picture, Copper + Iron nodes, the springs")
            K.check(("#SkyyShKSm" in bd["mk"]) == pole, "MP ... the smithy shows with the pole (%s)" % pole)
            K.check(bd["sets"].get("#SkyyShKTitle.Text") == "MINING SHARD", "MP ... the title")
            if pole and smy:
                K.check('"kq-:50"' in bd["datas"].get("#SkyyShKQ7M", "") and '"kq+:50"' in bd["datas"].get("#SkyyShKQ7U", "") and bd["sets"].get("#SkyyShKQ7V.Text") == "50 %",
                        "MP ... the slider row: < / > carry the value shown")
            elif pole:
                K.check('"ku7:0"' in bd["datas"].get("#SkyyShKQ7X", "") and int(pg.ckQSm) == 1, "MP ... Smithy II can be bought (ku7:0)")
            else:
                K.check('"ku7:0"' in bd["datas"].get("#SkyyShKQ7X", "") and int(pg.ckQSm) == 0, "MP ... no pole: the Totems button")
            long_ = [str(x) for x in list(pg.ckUpE) + list(pg.ckUpC) + list(pg.ckUpL) if x is not None and len(str(x)) > 38]
            K.check(not long_, "MP FIX ... every row line fits the 256 px column (<= 38 characters): %s" % long_)
            K.check(len(str(pg.ckCap)) <= 125 and "Spirits mine while you are away" in str(pg.ckCap), "MP FIX ... the caption fits (%d): %s" % (len(str(pg.ckCap)), pg.ckCap))
            els = bd["mk"].count("{") - bd["mk"].count('"{')
            K.check(els < 1000, "MP ... %d elements (well under ~1,600)" % els)
            K.check(bd["size"] < 1000000, "MP ... the packet stays small (%d bytes)" % bd["size"])
    # fix (critic 3.2): no Iron island yet -> the caption says how to add Iron
    _mining(L, p, iron=False)
    T49._build(pg)
    K.check("Add Iron: buy its island on Islands." in str(pg.ckCap) and len(str(pg.ckCap)) <= 125, "MP FIX the Iron hint: %s" % pg.ckCap)
    _mining(L, p, amt=5, irr=5, deco=5, pole=True)
    St.LOCK.lock()
    try:
        p.setProperty("mining.i0.size", "3"); p.setProperty("mining.i0.smithy", "1"); St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    T49._build(pg)
    # the node pictures alternate Copper / Iron (spot i -> ore i mod 2); a click pops; a broken node = rubble
    K.check(str(pg.ckTexA[0]).endswith("ClkQNode0.png") and str(pg.ckTexA[1]).endswith("ClkQNode1.png") and str(pg.ckTexB[1]).endswith("ClkQRub1.png"), "MP spot 0 Copper, spot 1 Iron")
    Cfg.CK_CPS = 1000
    for i in range(12):
        pg.handleDataEvent(None, None, json.dumps({"a": "kt0:0"}))
    bd = T49._build(pg)
    K.check(str(pg.stText).startswith("Mined a T1 Copper node: +") and str(pg.ckPop).startswith("+"), "MP a node breaks: %s / %s" % (pg.stText, pg.ckPop))
    K.check("#SkyyShKPop" in bd["mk"] and "ClkQRub0.png" in bd["mk"], "MP ... the pop + the rubble while it refills")
    K.check(any(str(x) == CB or str(x) == BCU for x in pg.sgId) and "#SkyyShKC0B" in bd["datas"], "MP the store cells show the mined blocks")
    pg.handleDataEvent(None, None, json.dumps({"a": "kt0:1"}))
    K.check("up to date" in str(pg.stText), "MP a stale quarry slot: %s" % pg.stText)
    # the slider through the page
    pg.handleDataEvent(None, None, json.dumps({"a": "kq+:50"}))
    K.check(p.getProperty("mining.i0.alloyPct") == "60", "MP > on the page: 60 (%s)" % pg.stText)
    pg.handleDataEvent(None, None, json.dumps({"a": "kq+:50"}))
    K.check(p.getProperty("mining.i0.alloyPct") == "60" and "up to date" in str(pg.stText), "MP ... a stale value: nothing (%s)" % pg.stText)
    # the map
    pg.handleDataEvent(None, None, json.dumps({"a": "kmap"}))
    bd = T49._build(pg)
    r_ = T410.full(pg)
    K.check(not r_["miss"] and not r_["unbound"] and "ClkQMap0.png" in bd["mk"] and "ZONE 1 QUARRY" in bd["mk"], "MP the quarry map walks clean")
    pg.handleDataEvent(None, None, json.dumps({"a": "kisl"}))
    pg.handleDataEvent(None, None, json.dumps({"a": "kback"}))
    K.check(int(pg.view) == 0 and int(pg.tab) == 1, "MP Shard menu -> the menu's Map tab")
    # the quarry off: no button, kopen refused; the Foraging clicker untouched
    Cfg.MQ_ON = False
    bm = T49._build(pg)
    pg.handleDataEvent(None, None, json.dumps({"a": "kopen"}))
    K.check("#SkyyShClk" not in bm["mk"] and int(pg.view) == 0 and "switched off" in str(pg.stText), "MP the quarry off: no button, kopen refused")
    Cfg.MQ_ON = True
    pfo = Page(ou, W_)
    pfo.kind = FO
    pfo.view = 0
    Ck.HAND_TEST = "Tool_Hatchet_Copper"
    T423._foraging(L, p)
    pfo.handleDataEvent(None, None, json.dumps({"a": "kopen"}))
    bf = T49._build(pfo)
    K.check(int(pfo.view) == 5 and not bool(pfo.ckMine) and "ClkTree1.png" in bf["mk"] and "ClkQ" not in bf["mk"] and bf["sets"].get("#SkyyShKTitle.Text") == "FORAGING SHARD",
            "MP the Foraging clicker still shows its trees")
    Cfg.CK_CPS = 8
    K.save()


EXPECT = {   # 0.4.23 -> 0.4.24, checked by hand 2026-11-21: the version texts (CfgFile / CfgFn / CfgRows / ShFill.markFixed / ShStore / the ready line) + the round
    'CfgFile': ['~<clinit>'],
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'ShCfg': ['+f DEF_MQ_GW', '+f DEF_MQ_SW', '+f DEF_MQ_ZLV', '+f MQ_ALLOY_DEF', '+f MQ_ALLOY_STEP', '+f MQ_BLOCKS', '+f MQ_GW', '+f MQ_HP', '+f MQ_LUCK_MAX', '+f MQ_NS_MAX', '+f MQ_NS_PER', '+f MQ_ON', '+f MQ_ORE', '+f MQ_ORE_LUCK', '+f MQ_RARE', '+f MQ_RARE_LUCK', '+f MQ_REFILL', '+f MQ_RMIN', '+f MQ_SM_H', '+f MQ_SM_Q', '+f MQ_SPRING', '+f MQ_SW', '+f MQ_ZLV', '~<clinit>', '~m loadCfg'],
    'ShClk': ['+f ALLOYACC', '+f ALLOYED', '+f ALLOY_OUT', '+f FORT_BR', '+f MINED', '+f MK', '+f PICK_ID', '+f PICK_T', '+f QA_A', '+f QA_B', '+f QA_ID', '+f Q_BAR', '+f Q_BLOCK', '+f Q_COB', '+f Q_ORE', '+f RND_TEST', '+f R_BAR', '+f R_ORE', '+m accGet', '+m accSet', '+m addTo', '+m alloyPct', '+m alloyStep', '+m baseSlot', '+m blocksAt', '+m bonusSumK', '+m buyLuck', '+m buySmithy', '+m fortuneOf', '+m heldOf', '+m isBase', '+m luck', '+m mine', '+m oreP', '+m part', '+m pickTier', '+m qName', '+m rareP', '+m refillMs', '+m rnd', '+m setAlloy', '+m smithy', '+m smithyCoins', '+m smithyMats', '+m zoneOwned', '~<clinit>', '~m bonusSum', '~m buyNode', '~m chop', '~m fortune'],
    'ShCore': ['+f AL_A', '+f AL_B', '+f AL_ID', '+f AL_PAR', '+f RB_BAR', '+f RB_ORE', '+m oreOfBar', '+m owedAs', '~<clinit>', '~m collectHeld'],
    'ShFill': ['~m markFixed'],
    'ShIsl': ['~m zoneNeed'],
    'ShPage': ['+f QCARD', '+f Q_NODE', '+f Q_RUB', '+f ckMine', '+f ckQPct', '+f ckQSm', '+f ckTexA', '+f ckTexB', '+f ckZone', '+m actQuarry', '+m fillQuarry', '~<clinit>', '~m act', '~m actClick', '~m build0', '~m buildClick', '~m buildFull', '~m fillClick'],
    'ShStore': ['~m migrate', '~m migrate2', '~m save'],
    'SkyyShardsPlugin': ['~m setup'],
}


def _compare24(out, jar, old_jar, pkg, expect, added, removed=()):
    """the quarry's NEW pictures (Map/ClkQ*, Map/ClkUpQ*) are new only; every other non-class file (the 0.4.23 clicker pictures + the Skyglass theme
    included) identical; the kit's class compare runs on a copy of the new jar without the new pictures"""
    NEWP = ("Common/UI/Custom/SkyyShards/Map/ClkQ", "Common/UI/Custom/SkyyShards/Map/ClkUpQ")
    with zipfile.ZipFile(jar) as a, zipfile.ZipFile(old_jar) as b:
        na, nb = set(a.namelist()), set(b.namelist())
        new = sorted(n for n in na - nb if not n.endswith(".class"))
        assert all(n.startswith(NEWP) for n in new) and len(new) == 43 and not any(n.startswith(NEWP) for n in nb), "C new non-class files: %s" % new[:8]
        gone = sorted(n for n in nb - na if not n.endswith(".class"))
        assert not gone, "C non-class files gone: %s" % gone[:8]
        chg = sorted(n for n in na & nb if not n.endswith(".class") and a.read(n) != b.read(n))
        assert chg == ["manifest.json"], "C changed non-class files: %s" % chg[:8]
    print("C. %d new non-class files (the quarry pictures); the 0.4.23 pictures + theme unchanged; manifest.json changed" % len(new))
    cp = os.path.join(SCRATCH, "compare-%s.jar" % VERSION)
    with zipfile.ZipFile(jar) as zi, zipfile.ZipFile(cp, "w", zipfile.ZIP_DEFLATED) as zo:
        for n in zi.namelist():
            if not n.startswith(NEWP):
                zo.writestr(n, zi.read(n))
    T419._compare(out, cp, old_jar, pkg, expect, added, removed)


def run_live(out, jar, scratch, home):
    T421.run_live(out, jar, scratch, home)


if __name__ == "__main__":
    HK.run_compare = _compare24
    HK.run(name="SkyyShards", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("static", run_static), ("mine24", run_mine), ("smithy24", run_smithy), ("upgrade24", run_upgrade), ("zones24", run_zones),
                   ("collect24", run_collect), ("fortune24", run_fortune), ("page24", run_page),
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
