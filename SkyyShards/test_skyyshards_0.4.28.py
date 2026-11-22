"""Harness for SkyyShards 0.4.28 (the Ranching + Orchard clickers - tools/shards_0_4_28_patch.py, on top of 0.4.27).
Build first:
    python tools/shards_0_4_28_patch.py && python SkyyShards/build_skyyshards_0.4.28.py
    python SkyyShards/test_skyyshards_0.4.28.py [--keep] [--only label,label] [--dir <scratch>]

  S28  static   the patch re-runs to identical bytes; header / VERSION / ready line; no new registerSystem / registerCommand; line endings kept; the jar
                ships the 25 new 1x pictures (110 x 140) and no Ranching / Orchard Map bases / element pictures; the Shards UI pictures go down
  RC28 ranch    EXECUTED the tend click: the vanilla products (Assets.zip read again here), the click cap, 6 clicks = EXACTLY the replayed rolls into
                ranching.i0.drops (saved at once), the other products at their chance, XP = 25 % of the world's Ranching XP, the rest + Water troughs,
                Fortune via skill:fn:fortune "Ranching", a full storage refused, switched off refused, a spot / slot the island lacks, own memory key
  OC28 orchard  EXECUTED the pick click the same way (Fortune via "Farming" on the fruit block), a bush type, the regrow + Irrigation
  PG28 page     EXECUTED the portals open the clickers (view 5) for every shard, both pages walk clean in the island view / map / upgrades view; the
                titles, the 6 rows, 8 cards in 3 zone clusters + 2 empty zones, the zone lock by Ranching / Orchard level, buy the next island on
                the map (coins + its product + Capture Crates from the world), Open, Feed quality / Fruit yield bought once on a double click,
                a stale page / profile switch refused, the spirit row on a fruit without an Enchanted form costs 100 x its fruit
  CO28 costs    EXECUTED every Ranching / Orchard island cost line (Feed quality / Fruit yield 1..10, Herd size / Fruit trees 1..5, Water troughs /
                Irrigation 1..5, Decorations 1..5, Grow 2..3, spirit I..V, a modifier) names only the island's own product / its Enchanted form;
                the cost table printed (the report's table)
  DU28 dupes    EXECUTED tend -> Collect pays exactly once (a second Collect nothing), a grid cell then Collect all, Sell all (2 clicks) once, a
                double click on a resting animal adds nothing
  MG28 migr.    EXECUTED the per-profile migration on a file: History copy first (byte-checked), the marker, an automated Orchard's sapling store ->
                storage, a manual one kept, every island / totem / item counted before = after, a second load changes nothing; a profile
                without Ranching / Orchard gets only the marker (no copy)
  then 0.4.27's phases (worlds27 .. mig27) and 0.4.26 .. older ones on THIS jar (checks retired on purpose listed below), A verify, C compare,
  AA audit, live28 START TWICE on a scratch copy of the live data (every island / totem / item before = after; second start = no change)
Exit code 1 on any failure.
"""
import os, sys, importlib.util, subprocess, json, re, zipfile, math, struct

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK

VERSION = "0.4.28"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "ranch1", "h")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyShards-%s.jar" % VERSION)]
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyShards-0.4.27.jar")
GEN = os.path.join(HERE, "build_skyyshards_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyshards_0.4.27.py")
PATCH = os.path.join(ROOT, "tools", "shards_0_4_28_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.shards."

# the 0.4.27 harness (it loads 0.4.26 -> ... older): its version moves to this one in memory
_T27 = open(os.path.join(HERE, "test_skyyshards_0.4.27.py"), encoding="utf8").read()
assert _T27.count('VERSION = "0.4.27"\n') == 1, "the 0.4.27 harness changed"
_T27 = _T27.replace('VERSION = "0.4.27"\n', 'VERSION = "%s"\n' % VERSION)
_argv = list(sys.argv)
T427 = importlib.util.module_from_spec(importlib.util.spec_from_loader("test_skyyshards_0_4_27", loader=None))
T427.__dict__["__file__"] = os.path.join(HERE, "test_skyyshards_0.4.27.py")
exec(compile(_T27, T427.__file__, "exec"), T427.__dict__)
sys.argv[:] = _argv
T426, T425, T424, T423, T422, T421 = T427.T426, T427.T425, T427.T424, T427.T423, T427.T422, T427.T421
T420, T419, T411, T410, T49, T416, T415, T413 = T427.T420, T427.T419, T427.T411, T427.T410, T427.T49, T427.T416, T427.T415, T427.T413
for _m in (T427, T426, T425, T424, T423, T422, T421, T420, T419, T420.T418, T419.T417):
    _m.JAR = JAR
for _m in (T427, T426, T425, T424, T423, T422, T421, T420, T419, T420.T418, T416, T415, T419.T417):
    _m.SCRATCH = SCRATCH
T427.OLD_JAR = OLD_JAR
OWNER, MEMBER = T420.OWNER, T420.MEMBER
MI, FO, FK, RA, OR, CK = 0, 1, 2, 3, 4, 5
T0 = 1790000000000
CHK, ECHK, BEEF = "Food_Chicken_Raw", "Skyy_Ench_RawChicken", "Food_Beef_Raw"
APL, EAPL, MANGO = "Plant_Fruit_Apple", "Skyy_Ench_Apple", "Plant_Fruit_Mango"
ANIMALS = ["Chicken", "Cow", "Pig", "Boar", "Sheep", "Turkey", "Goat", "Bison"]


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyShards 0.4.28 - build script') and 'VERSION = "0.4.28"\n' in g, "S28 header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S28 no new %r" % w)
    K.check("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.28:" in g, "S28 the ready line names the round")
    K.check("ROLLBACK 0.4.28 -> 0.4.27 alone" in g, "S28 the rollback note")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S28 the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S28 line endings kept")
    K.check(os.path.getmtime(GEN) >= os.path.getmtime(PATCH) and os.path.getmtime(jar) >= os.path.getmtime(GEN), "S28 jar newer than the script, the script newer than the patch")
    area = area0 = 0
    with zipfile.ZipFile(jar) as z, zipfile.ZipFile(OLD_JAR) as z0:
        names = z.namelist()
        for zz, acc in ((z, "a"), (z0, "b")):
            for n in zz.namelist():
                if n.startswith("Common/UI/Custom/") and n.endswith(".png"):
                    w_, h_ = struct.unpack(">II", zz.read(n)[16:24])
                    if acc == "a":
                        area += w_ * h_
                    else:
                        area0 += w_ * h_
        new = sorted(n for n in names if re.search(r"/Map/Clk(RAni\d|RRest|OTree\d|OPick\d)(@2x)?\.png$", n))
        K.eq(len(new), 25, "S28 the 25 new pictures")
        K.check(all("@2x" not in n and struct.unpack(">II", z.read(n)[16:24]) == (110, 140) for n in new), "S28 ... all 1x, 110 x 140")
        K.check(not any(re.search(r"/Map/(Base(Ranching|Orchard)|(Ranching|Orchard)E\d+)(@2x)?\.png$", n) for n in names), "S28 no Ranching / Orchard Map tab pictures (the old menu never opens)")
    K.check(area < area0, "S28 the Shards UI pictures go down: %.2f -> %.2f Mpx" % (area0 / 1e6, area / 1e6))
    print("S28 Shards UI pictures: %.2f -> %.2f Mpx" % (area0 / 1e6, area / 1e6))
    K.save()


def _env(scratch, K, name):
    from jpype import JClass, JString, JInt
    L, ou, W_, p, lv, got = T427._env(scratch, K, name)
    T411.T48.add_items([(CHK, 600), (ECHK, 300), (BEEF, 300), ("Skyy_Ench_RawBeef", 64), ("Ingredient_Hide_Light", 100), ("Ingredient_Feathers_Light", 100),
                        ("Food_Egg", 100), ("Ingredient_Hide_Medium", 100), ("Tool_Capture_Crate", 10), (APL, 600), (EAPL, 300), ("Plant_Sapling_Apple", 100),
                        (MANGO, 2000), ("Plant_Fruit_Berries_Red", 300), ("Skyy_Ench_Berries", 64), ("Plant_Fruit_Coconut", 300), ("Skyy_Ench_WildFruit", 64),
                        ("Plant_Sapling_Palm", 100), ("Plant_Sapling_Jungle", 100), ("Skyy_Ench_Wheat", 300)])
    lv["Ranching"] = 30
    lv["Orchard"] = 30
    return L, ou, W_, p, lv, got


def _isl(L, p, kind, rows, auto=True, amt=5, irr=0, deco=0, lim_tier=5):
    """a Ranching / Orchard shard: rows = [(slot, type, size)]"""
    St = L["ShStore"]
    St.LOCK.lock()
    try:
        for k_ in list(p.stringPropertyNames()):
            if str(k_).startswith(kind + "."):
                p.remove(k_)
        for s, ty, sz in rows:
            p.setProperty("%s.i%d.type" % (kind, s), ty); p.setProperty("%s.i%d.size" % (kind, s), str(sz)); p.setProperty("%s.i%d.last" % (kind, s), str(T0))
            p.setProperty("%s.i%d.stored" % (kind, s), "0"); p.setProperty("%s.i%d.amt" % (kind, s), str(amt)); p.setProperty("%s.i%d.irr" % (kind, s), str(irr))
            p.setProperty("%s.i%d.deco" % (kind, s), str(deco)); p.setProperty("%s.i%d.totems" % (kind, s), "harvest_spirit:1:::0:ro%04d" % s)
        p.setProperty(kind + ".auto", "1" if auto else "0"); p.setProperty(kind + ".paused", "0"); p.setProperty(kind + ".storage", str(lim_tier))
        p.setProperty(kind + ".placed", L["W_"] + "|%d|5|6" % (3 if kind == "ranching" else 4))
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()


def _ranch(L, p, **kw):
    _isl(L, p, "ranching", [(0, "chicken", kw.pop("size", 1))] + list(kw.pop("extra", [])), **kw)


def _orch(L, p, **kw):
    _isl(L, p, "orchard", [(0, kw.pop("ty", "apple"), kw.pop("size", 1))] + list(kw.pop("extra", [])), **kw)


def _vanilla_animals():
    """animal -> {item: (min, max)} of Drop_<A> + Drop_<A>_Harvest + Produce (Poop left out), read here on its own"""
    import serverjar as _SJ
    az = zipfile.ZipFile(_SJ.assets_zip())
    names = set(az.namelist())
    out = {}
    for a in ANIMALS:
        m = {}
        for n in ("Server/Drops/NPCs/Livestock/Drop_%s.json" % a, "Server/Drops/NPCs/Livestock/Drop_%s_Harvest.json" % a, "Server/Drops/NPCs/Livestock/Produce/Drop_%s_Produce.json" % a):
            if n not in names:
                continue
            stk = [json.loads(az.read(n).decode("utf-8-sig"))]
            while stk:
                x = stk.pop()
                if isinstance(x, dict):
                    it = x.get("Item")
                    if isinstance(it, dict) and it.get("ItemId") and it["ItemId"] != "Ingredient_Poop":
                        q0 = 1 if it.get("QuantityMin") is None else int(it["QuantityMin"])
                        q1 = q0 if it.get("QuantityMax") is None else int(it["QuantityMax"])
                        o = m.get(it["ItemId"])
                        m[it["ItemId"]] = (max(1, q0), q1) if o is None else (max(1, min(o[0], q0)), max(o[1], q1))
                    stk.extend(x.values())
                elif isinstance(x, list):
                    stk.extend(x)
        out[a] = m
    return out


def _replay(Ck, seed, f, rolls, q0, q1, ex, pe):
    """the tend / pick rolls on a second java.util.Random (exact): per roll [qty], Fortune, then per other product [chance, [qty]]"""
    from jpype import JClass, JDouble, JLong
    r = JClass("java.util.Random")(JLong(seed))

    def qr(a, b):
        if b <= a:
            return a
        return min(b, a + int(math.floor(float(r.nextDouble()) * (b - a + 1))))
    main = base = 0
    eq = [0] * len(ex)
    for _ in range(rolls):
        q = qr(q0, q1)
        base += q
        main += q * (1 + int(Ck.extras(JDouble(f), JDouble(float(r.nextDouble())))))
        for i, (eid, a, b) in enumerate(ex):
            if pe > 0 and float(r.nextDouble()) < pe:
                eq[i] += qr(a, b)
    return main, base, eq


def _ex(Ck, ci):
    s = str(Ck.R_EX[ci])
    return [(x.split(":")[0], int(x.split(":")[1]), int(x.split(":")[2])) for x in s.split(",") if x]


# ---------------------------------------------------------------------------------------------------------- RC28: the tend click
def run_ranch(out, jar, scratch, _home):
    from jpype import JString, JClass, JLong
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "rc")
    M, St, Core, Cfg, Ck, Isl = L["ShMath"], L["ShStore"], L["ShCore"], L["ShCfg"], L["ShClk"], L["ShIsl"]
    br, PyFn, tst = L["br"], L["PyFn"], L["tst"]
    _ranch(L, p)
    now = [T0]

    def adv(ms):
        now[0] += ms
        Core.NOW_TEST = now[0]

    def td(spot=0, slot=0):
        r = Ck.chop(ou, JString(OWNER), RA, slot, spot, None)
        return str(r[0]), str(r[1])

    K.eq((int(Ck.RNK), int(Ck.ORK)), (RA, OR), "RC ShClk.RNK / ORK = the Ranching / Orchard kinds")
    K.check(all(bool(Ck.clicker(k_)) for k_ in range(6)), "RC every shard is a clicker now")
    van = _vanilla_animals()
    for ci, a in enumerate(ANIMALS):
        prod = str(Isl.PROD[int(Isl.LAD0[RA]) + ci])
        m = dict(van[a])
        mq = m.pop(prod, (1, 2))
        K.eq((int(Ck.R_QMIN[ci]), int(Ck.R_QMAX[ci])), mq, "RC %s: %s %d-%d a roll (Assets.zip, or 1-2 when its drop list lacks it)" % (a, prod, mq[0], mq[1]))
        K.eq(sorted((x[0], (x[1], x[2])) for x in _ex(Ck, ci)), sorted(m.items()), "RC ... its other vanilla products %s" % sorted(m))
    # the click cap
    Cfg.RQ_HP = 100
    c0, cap0 = int(Ck.CHOPS.get()), int(Ck.CAPPED.get())
    for _ in range(20):
        td(spot=4)
    K.eq((int(Ck.CHOPS.get()) - c0, int(Ck.CAPPED.get()) - cap0), (8, 12), "RC the click cap: 8 counted, 12 did nothing")
    Cfg.RQ_HP = 6
    Cfg.CK_CPS = 1000
    adv(1000)
    # 6 clicks tend the Chicken: EXACTLY the replayed rolls (2 rolls x 1-2 Raw Chicken + each other product at 25 %)
    seed = 777
    Ck.RND_TEST = JClass("java.util.Random")(JLong(seed))
    xp0 = len(tst["xps"])
    res = [td() for _ in range(6)]
    Ck.RND_TEST = None
    ex = _ex(Ck, 0)
    main, base, eq = _replay(Ck, seed, 0.0, 2, 1, 2, ex, 0.25)
    want = {CHK: main}
    for (eid, a, b), q in zip(ex, eq):
        if q:
            want[eid] = want.get(eid, 0) + q
    K.check(res[4] == ("", "5 / 6") and res[5][0].startswith("+Tended a T1 Chicken: +%d Raw Chicken" % main) and res[5][1] == "+%d Raw Chicken" % main,
            "RC 6 clicks tend a Chicken by hand: %s / %s" % (res[4], res[5]))
    K.eq(T425._drops(p, 0, "ranching"), want, "RC ... EXACTLY the replayed products into ranching.i0.drops")
    disk = open(os.path.join(str(St.DIR), OWNER + ".properties"), encoding="utf8").read().replace(chr(92) + ":", ":")
    K.check("ranching.i0.drops=" in disk and CHK in disk, "RC ... saved at once")
    xpw = base * 20 + sum(q * int(Ck.exXp(JString(e[0]))) for e, q in zip(ex, eq))
    gx = [x for x in tst["xps"][xp0:]]
    K.check(sum(x[1] for x in gx) == int(xpw * 25 // 100) or abs(sum(x[1] for x in gx) - xpw * 0.25) < 1.0, "RC ... XP = 25 %% of the world's %d Ranching XP (%s)" % (xpw, gx))
    K.check(all(x[0] == "Ranching" for x in gx), "RC ... paid as Ranching XP")
    # rest + Water troughs
    s, pp = td()
    K.check(s.startswith("=That animal is resting - ") and 0 < int(s.split(" - ")[1].split(" ")[0]) <= 10, "RC a tended animal rests (10 s): %s" % s)
    K.eq([int(Ck.gatherRegrowMs(RA, i)) for i in (0, 3, 5)], [10000, 7000, 5000], "RC rest 10 / 7 / 5 s at Water troughs 0 / 3 / 5")
    Cfg.RQ_RMIN = 8
    K.eq(int(Ck.gatherRegrowMs(RA, 5)), 8000, "RC ... never below click.ranch.minRestSec")
    Cfg.RQ_RMIN = 3
    d0 = dict(T425._drops(p, 0, "ranching"))
    td(); td()
    K.eq(T425._drops(p, 0, "ranching"), d0, "RC ... clicks on a resting animal add nothing (a double click)")
    # a spot / slot the island lacks; the memory is the ranch's own
    n = int(Isl.treeN(1, 5))
    K.check(td(spot=n)[0].startswith("=The page is up to date"), "RC spot %d is not on the island" % n)
    K.check(td(slot=5)[0].startswith("-That island is not yours yet"), "RC an empty slot")
    K.check(float(Ck.state(JString(OWNER + "|3|0"))[0][4]) > 0 and float(Ck.state(JString(OWNER + "|2|0"))[0][4]) == 0.0, "RC the ranch's damage sits under <key>|3|<slot>")
    # Fortune: skill:fn:fortune "Ranching" with the product
    fcalls = []

    def fortune(a):
        fcalls.append((str(a[1]), str(a[2])))
        return JString("ok|2.0|0.0|1|1")
    br.put("skill:fn:fortune", PyFn(fortune))
    adv(20000)
    seed2 = 99
    Ck.RND_TEST = JClass("java.util.Random")(JLong(seed2))
    d0 = dict(T425._drops(p, 0, "ranching"))
    for _ in range(6):
        td(spot=1)
    Ck.RND_TEST = None
    main2, base2, eq2 = _replay(Ck, seed2, 2.0, 2, 1, 2, ex, 0.25)
    d1 = T425._drops(p, 0, "ranching")
    K.eq(d1.get(CHK, 0) - d0.get(CHK, 0), main2, "RC Fortune 2.0 (skill:fn:fortune) triples the product rolls: %d (base %d)" % (main2, base2))
    K.check(main2 == 3 * base2 and fcalls and fcalls[-1] == ("Ranching", CHK), "RC ... asked with Ranching + the product (%s)" % fcalls[-1:])
    br.remove("skill:fn:fortune")
    # Feed quality: more rolls
    St.LOCK.lock()
    try:
        p.setProperty("ranching.i0.nsize", "3"); St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    K.eq(int(Ck.rollsAt(RA, 3)), 5, "RC Feed quality 3: 2 + 3 = 5 rolls a tend")
    # a full storage: refused, nothing added
    lim = int(M.limOf(RA, p, 0))
    St.LOCK.lock()
    try:
        p.setProperty("ranching.i0.drops", "%s:%d" % (CHK, lim)); St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    adv(1000)
    s, pp = td(spot=2)
    K.check(s.startswith("-This island's storage is full") and T425._drops(p, 0, "ranching") == {CHK: lim}, "RC a full island refuses: %s" % s)
    # switched off
    Cfg.RQ_ON = False
    s, pp = td(spot=2)
    K.check(s.startswith("-The Ranching clicker is switched off"), "RC switched off: %s" % s)
    Cfg.RQ_ON = True
    K.save()


# ---------------------------------------------------------------------------------------------------------- OC28: the pick click
def run_orch(out, jar, scratch, _home):
    from jpype import JString, JClass, JLong
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "oc")
    M, St, Core, Cfg, Ck, Isl = L["ShMath"], L["ShStore"], L["ShCore"], L["ShCfg"], L["ShClk"], L["ShIsl"]
    br, PyFn, tst = L["br"], L["PyFn"], L["tst"]
    _orch(L, p, extra=[(1, "berries", 1)])
    Cfg.CK_CPS = 1000
    now = [T0]

    def adv(ms):
        now[0] += ms
        Core.NOW_TEST = now[0]

    def pk(spot=0, slot=0):
        r = Ck.chop(ou, JString(OWNER), OR, slot, spot, None)
        return str(r[0]), str(r[1])
    K.eq([(int(Ck.O_QMIN[i]), int(Ck.O_QMAX[i])) for i in range(8)], [(1, 1), (1, 2), (1, 1), (1, 1), (1, 2), (1, 1), (1, 1), (1, 1)],
         "OC fruit a roll: Apple 1, Berries / Pinkberry 1-2 (the vanilla bush), the tree fruits 1")
    K.eq([str(Ck.O_BLOCK[i]) for i in (0, 1, 3)], ["Plant_Crop_Apple_Block", "Plant_Crop_Berry_Block", MANGO], "OC the Fortune block = the fruit block (else the fruit)")
    adv(1000)
    seed = 4242
    Ck.RND_TEST = JClass("java.util.Random")(JLong(seed))
    xp0 = len(tst["xps"])
    res = [pk() for _ in range(8)]
    Ck.RND_TEST = None
    main, base, _e = _replay(Ck, seed, 0.0, 3, 1, 1, [], 0.0)
    K.check(res[7][0].startswith("+Picked a T1 Apple tree: +%d Apple" % main) and main == 3, "OC 8 clicks pick an Apple tree: 3 apples (%s)" % res[7][0][:80])
    K.eq(T425._drops(p, 0, "orchard"), {APL: 3}, "OC ... into orchard.i0.drops")
    gx = tst["xps"][xp0:]
    K.check(sum(x[1] for x in gx) == 30 and all(x[0] == "Orchard" for x in gx), "OC ... XP = 25 %% of 3 x 40 = 30 Orchard XP (%s)" % gx)
    s, pp = pk()
    K.check(s.startswith("=That tree is growing new fruit - ") and 0 < int(s.split(" - ")[1].split(" ")[0]) <= 12, "OC a picked tree grows new fruit (12 s): %s" % s)
    K.eq([int(Ck.gatherRegrowMs(OR, i)) for i in (0, 4, 5)], [12000, 8000, 7000], "OC new fruit 12 / 8 / 7 s at Irrigation 0 / 4 / 5")
    # Fortune via Farming on the fruit block; the bush island (Berries 1-2)
    fcalls = []

    def fortune(a):
        fcalls.append((str(a[1]), str(a[2])))
        return JString("ok|1.0|0.0|1|1")
    br.put("skill:fn:fortune", PyFn(fortune))
    adv(1000)
    seed2 = 5
    Ck.RND_TEST = JClass("java.util.Random")(JLong(seed2))
    for _ in range(8):
        pk(slot=1)
    Ck.RND_TEST = None
    main2, base2, _e = _replay(Ck, seed2, 1.0, 3, 1, 2, [], 0.0)
    K.eq(T425._drops(p, 1, "orchard"), {"Plant_Fruit_Berries_Red": main2}, "OC the Berries bush: EXACTLY the replayed 3 rolls x 1-2 x Fortune 1.0 (%d, base %d)" % (main2, base2))
    K.check(main2 == 2 * base2 and fcalls[-1] == ("Farming", "Plant_Crop_Berry_Block"), "OC ... Fortune asked with Farming + the berry bush block (%s)" % fcalls[-1:])
    br.remove("skill:fn:fortune")
    K.check(float(Ck.state(JString(OWNER + "|4|0"))[0][0]) == 0.0 and float(Ck.state(JString(OWNER + "|4|1"))[0][0]) == 0.0, "OC the orchard's memory is its own <key>|4|<slot>")
    Cfg.OQ_ON = False
    K.check(pk(spot=2)[0].startswith("-The Orchard clicker is switched off"), "OC switched off")
    Cfg.OQ_ON = True
    K.save()


# ---------------------------------------------------------------------------------------------------------- PG28: the pages
def run_page(out, jar, scratch, _home):
    from jpype import JString, JLong
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "pg")
    St, M, Core, Cfg, Isl, Tot, Ck, PFn = L["ShStore"], L["ShMath"], L["ShCore"], L["ShCfg"], L["ShIsl"], L["ShTotem"], L["ShClk"], L["ShPageFn"]
    T423._foraging(L, p); T424._mining(L, p); T425._farm(L, p); T426._town(L, p)
    _ranch(L, p); _orch(L, p)
    L["coins"]["bal"] = 900000000
    cs = T427._give(L, [(ECHK, 200), (CHK, 300), (BEEF, 200), ("Tool_Capture_Crate", 6), (EAPL, 100), (APL, 300), (MANGO, 1000)])
    for kd in range(6):
        pg = PFn(kd, 0).make(None, ou, JString(W_))
        K.check(pg is not None and int(pg.view) == 5, "PG the portal of kind %d opens its clicker (view 5)" % kd)
    for kd, title, rows, word in ((RA, "RANCHING SHARD", ["Feed quality", "Herd size", "Water troughs"], "PENS"), (OR, "ORCHARD SHARD", ["Fruit yield", "Fruit trees", "Irrigation"], "ORCHARDS")):
        pg = T427._page(L, ou, W_, kd)
        bd = T49._build(pg)
        r_ = T410.full(pg)
        K.check(not r_["miss"] and not r_["unbound"], "PG kind %d island view walks clean %s %s" % (kd, r_["miss"][:2], r_["unbound"][:2]))
        K.check(title in json.dumps(bd["sets"]) and all(w in bd["mk"] for w in rows), "PG ... the title + the rows %s" % rows)
        K.check(all(("#SkyyShKU%d" % r) in bd["mk"] for r in range(6)) and str(pg.ckUpL[2]).startswith("Tier I"), "PG ... 6 rows, the spirit row Tier I")
        K.check(int(pg.ckTn) > 0 and sum(1 for k_ in bd["datas"] if re.match(r"#SkyyShKH\d+$", k_)) == int(pg.ckTn), "PG ... one click square per animal / tree (%d)" % int(pg.ckTn))
        K.check(str(pg.ckTree) == str(L["ShPage"].R_ANI[0] if kd == RA else L["ShPage"].O_TREE[0]), "PG ... the picture of the island's type (%s)" % pg.ckTree)
        T427._ev(pg, "kmap")
        bd = T49._build(pg)
        r_ = T410.full(pg)
        K.check(int(pg.ckMode) == 1 and not r_["miss"] and not r_["unbound"], "PG ... the map walks clean %s %s" % (r_["miss"][:2], r_["unbound"][:2]))
        K.check(all(("#SkyyShKM%d" % i) in bd["mk"] for i in range(8)) and "#SkyyShKM8" not in bd["mk"] and ("ZONE 1 " + word) in bd["mk"], "PG ... 8 cards, 5 zone panels")
        K.check(str(pg.ckZS[3]).startswith("No ") and str(pg.ckZS[4]).startswith("No "), "PG ... Zones 4-5 empty: %s" % pg.ckZS[3])
        T427._ev(pg, "kup")
        T49._build(pg)
        r_ = T410.full(pg)
        K.check(int(pg.ckMode) == 2 and not r_["miss"] and not r_["unbound"], "PG ... the upgrades view walks clean %s %s" % (r_["miss"][:2], r_["unbound"][:2]))
        T427._ev(pg, "kisl")
    # the zone lock (Ranching level) + buying the next island on the map
    lv["Ranching"] = 5
    pg = T427._page(L, ou, W_, RA)
    T427._ev(pg, "kmap")
    T49._build(pg)
    K.check(bool(pg.ckMLock[3]) and "Ranching 20" in str(pg.ckMS[3]) and not bool(pg.ckMLock[1]), "PG Boar (Zone 2) locked below Ranching 20: %s" % pg.ckMS[3])
    K.check(int(pg.ckMB[1]) == 2 and str(pg.ckMS[1]).startswith("Buy:"), "PG ... the Cow is the next to buy: %s" % pg.ckMS[1])
    r = str(T427._ev(pg, "kb3"))
    K.check(not r.startswith("+") and int(Isl.slotOf(RA, p, int(Isl.LAD0[RA]) + 3)) < 0, "PG ... a locked Boar is refused: %s" % r[:90])
    b0, beef0, cr0 = L["coins"]["bal"], int(L["count"](cs, BEEF)), int(L["count"](cs, "Tool_Capture_Crate"))
    r = T427._ev(pg, "kb1")
    s1 = int(Isl.slotOf(RA, p, int(Isl.LAD0[RA]) + 1))
    K.check(s1 >= 0 and int(pg.ckSlot) == s1 and int(pg.ckMode) == 0, "PG ... the Cow bought on the map and shown: %s" % r[:90])
    K.check(beef0 - int(L["count"](cs, BEEF)) == 64 and cr0 - int(L["count"](cs, "Tool_Capture_Crate")) == 2 and b0 > L["coins"]["bal"],
            "PG ... paid 64 Raw Beef + 2 Capture Crates (from the world) + coins")
    T427._ev(pg, "kmap")
    T49._build(pg)
    K.check(int(pg.ckMB[0]) == 1, "PG ... the Chicken card offers Open")
    T427._ev(pg, "km0")
    K.eq(int(pg.ckSlot), 0, "PG ... Open shows the Chicken island")
    lv["Ranching"] = 30
    # Feed quality bought once on a double click; the costs = coins + the island's Enchanted Raw Chicken
    T49._build(pg)
    K.check(bool(pg.ckUpOk[0]) and str(pg.ckCL[1]).endswith("/ 1 Enchanted Raw Chicken") and str(pg.ckCL[0]).endswith(" coins"), "PG Feed quality: coins + 1 Enchanted Raw Chicken (%s / %s)" % (pg.ckCL[0], pg.ckCL[1]))
    e0 = int(L["count"](cs, ECHK))
    r = T427._ev(pg, "ku0:0")
    K.check(int(Ck.nsize(p, RA, 0)) == 1 and e0 - int(L["count"](cs, ECHK)) == int(Cfg.CK_NS_Q[0]), "PG ... Feed quality 1: %s" % r[:80])
    r = T427._ev(pg, "ku0:0")
    K.check(int(Ck.nsize(p, RA, 0)) == 1 and r.startswith("The page is up to date"), "PG ... a double click buys once: %s" % r[:60])
    # a profile switch since the page was drawn: nothing happens
    T49._build(pg)
    pg.key = "00000000-0000-0000-0000-000000000000-p9"
    r = str(pg.act("ku0:1", None, None))
    K.check(r.startswith("=The page is up to date") and int(Ck.nsize(p, RA, 0)) == 1, "PG a stale profile: refused (%s)" % r)
    r = str(pg.act("kt0:0", None, None))
    K.check(r.startswith("=The page is up to date") and int(Ck.CHOPS.get()) >= 0, "PG ... a click on an animal too (%s)" % r)
    # a stale island (another type in that slot since the page was drawn)
    pg = T427._page(L, ou, W_, RA)
    T49._build(pg)
    St.LOCK.lock()
    try:
        p.setProperty("ranching.i0.type", "pig"); St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    r = str(T427._ev(pg, "kt0:0"))
    K.check(r.startswith("The page is up to date"), "PG a stale island (Pig now in that slot): the click refused (%s)" % r)
    _ranch(L, p)
    # the orchard: Mango (no Enchanted form) - its spirit costs 2 x 100 Mango, not Enchanted Oak
    _orch(L, p, ty="mango")
    St.LOCK.lock()
    try:
        p.remove("orchard.i0.totems"); St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    pg = T427._page(L, ou, W_, OR)
    T49._build(pg)
    K.check(str(pg.ckCL[7]).endswith("/ 200 " + str(Tot.pretty(MANGO))) and "Oak" not in str(pg.ckCL[7]), "PG Mango's spirit: 200 Mango (no Enchanted Mango exists): %s" % pg.ckCL[7])
    m0 = int(L["count"](cs, MANGO))
    r = T427._ev(pg, "ku2:0")
    K.check(r.startswith("A spirit totem now works") and m0 - int(L["count"](cs, MANGO)) == 200, "PG ... bought with 200 Mango: %s" % r[:80])
    K.save()


# ---------------------------------------------------------------------------------------------------------- CO28: every cost line names only the island's own items
def run_costs(out, jar, scratch, _home):
    from jpype import JString, JLong
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "co")
    Isl, Ck, Core, Cfg = L["ShIsl"], L["ShClk"], L["ShCore"], L["ShCfg"]
    rows = []
    for kd in (RA, OR):
        for ci in range(8):
            t = int(Isl.LAD0[kd]) + ci
            own = {str(Isl.PROD[t]), str(Isl.ENCH[t]), str(Isl.SEED[t]), str(Isl.ESEED[t])} - {""}
            cv = float(Core.tierCv(t))
            lines = []
            for lv_ in range(1, 11):
                lines.append(("Feed quality" if kd == RA else "Fruit yield", lv_, int(Ck.nodeCoins(lv_, cv)), Ck.nodeMats(kd, t, lv_)))
            for w, tmpl in (("Herd size" if kd == RA else "Fruit trees", Cfg.MAT_AMT), ("Decorations", Cfg.MAT_DECO), ("Water troughs" if kd == RA else "Irrigation", Cfg.MAT_IRR)):
                for sz in (1, 2, 3):
                    for lv_ in range(1, 6):
                        lines.append((w, "%s %d" % ("SML"[sz - 1], lv_), int(Isl.coins(Isl.subH(sz, lv_), cv)), Isl.mats(kd, t, tmpl, sz - 1, JLong(lv_))))
            for sz in (2, 3):
                lines.append(("Island size", sz, int(Isl.coins(Isl.growH(sz), cv)), Isl.mats(kd, t, Cfg.MAT_GROW, sz - 2, JLong(1))))
            for tier in range(5):
                lines.append(("Spirit", tier + 1, int(Core.spiritCoins(tier, cv)), Core.spiritMats(kd, t, tier)))
            lines.append(("Modifier", 1, int(Core.modCoins(cv)), Core.modMats(kd, t)))
            bad = []
            for nm, lv_, c, mats in lines:
                ids = [str(x) for x in mats[0]]
                if any(i not in own for i in ids):
                    bad.append((nm, lv_, ids))
            K.check(not bad, "CO %s: every island cost names only its own %s (%s)" % (str(Isl.tname(t)), sorted(own), bad[:3]))
            # fix (critic ranch1): Island size never asks an Orchard island for a sapling (the clicker gives none) - its own fruit x click.orchard.saplingFruit
            if kd == OR:
                for sz, nsap in ((2, 8), (3, 24)):
                    gm = Isl.mats(kd, t, Cfg.MAT_GROW, sz - 2, JLong(1))
                    gi = [str(x) for x in gm[0]]
                    gq = dict(zip(gi, [int(x) for x in gm[1]]))
                    ench = (4 if sz == 2 else 16) * int(Isl.enchX(kd, t, JString("ench")))
                    want = {}
                    if str(Isl.ESEED[t]):
                        want[str(Isl.PROD[t])] = nsap * int(Cfg.OQ_SAPF)
                    eid = str(Isl.tok(kd, t, JString("ench")))
                    want[eid] = want.get(eid, 0) + ench
                    K.check(gq == want and not any(i.startswith("Plant_Sapling_") for i in gi),
                            "CO %s Island size %s = own fruit / Enchanted only, no sapling: %s (want %s)" % (str(Isl.tname(t)), "SML"[sz - 1], gq, want))
                if str(Isl.ESEED[t]):
                    bm = Isl.mats(kd, t, Cfg.BUY_ITEMS[kd], 0, JLong(1))
                    K.check(str(Isl.ESEED[t]) in [str(x) for x in bm[0]], "CO %s: a NEW island still asks for its sapling (find the tree type first)" % str(Isl.tname(t)))
                    _o = int(Cfg.OQ_SAPF)
                    Cfg.OQ_SAPF = 3
                    gm = Isl.mats(kd, t, Cfg.MAT_GROW, 0, JLong(1))
                    K.check(dict(zip([str(x) for x in gm[0]], [int(x) for x in gm[1]])).get(str(Isl.PROD[t]), 0) >= 24, "CO %s: click.orchard.saplingFruit is live" % str(Isl.tname(t)))
                    Cfg.OQ_SAPF = _o
            def fmt(m):
                return " + ".join("%d %s" % (int(q), str(i)) for i, q in zip(m[0], m[1]))
            rows.append((str(Isl.KEY[t]), fmt(lines[0][3]), fmt(lines[9][3]), fmt(lines[10][3]), fmt(lines[-6][3]), fmt(lines[-2][3]), fmt(lines[-1][3]),
                         str(Cfg.BUY_ITEMS[kd]), lines[0][2], lines[9][2]))
    print("CO cost table: type | Feed / Fruit 1 | ... 10 | Herd / Trees S1 | Spirit I | Spirit V | Modifier | buy items (from the world) | coins lv1 | coins lv10")
    for r in rows:
        print("CO  " + " | ".join(str(x) for x in r))
    K.notes.append("CO cost table: " + json.dumps(rows))
    K.save()


# ---------------------------------------------------------------------------------------------------------- DU28: no dupes
def run_dupe(out, jar, scratch, _home):
    from jpype import JString, JClass, JLong
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "du")
    St, M, Core, Cfg, Ck = L["ShStore"], L["ShMath"], L["ShCore"], L["ShCfg"], L["ShClk"]
    _ranch(L, p)
    Cfg.CK_CPS = 1000
    Cfg.RQ_EXTRA = 0
    cs = T427._give(L, [(ECHK, 1)])
    c0 = int(L["count"](cs, CHK))
    for _ in range(6):
        Ck.chop(ou, JString(OWNER), RA, 0, 0, None)
    d = T425._drops(p, 0, "ranching")
    n = d.get(CHK, 0)
    K.check(n >= 2, "DU a tend put %d Raw Chicken in storage" % n)
    pg = T427._page(L, ou, W_, RA)
    T49._build(pg)
    r = T427._ev(pg, "colall")
    K.check(int(L["count"](cs, CHK)) - c0 == n and T425._drops(p, 0, "ranching").get(CHK, 0) == 0, "DU Collect all pays them once: %s" % r[:80])
    r = T427._ev(pg, "colall")
    K.eq(int(L["count"](cs, CHK)) - c0, n, "DU ... a second Collect pays nothing more")
    # a grid cell, then Collect all
    for _ in range(6):
        Ck.chop(ou, JString(OWNER), RA, 0, 1, None)
    n2 = T425._drops(p, 0, "ranching").get(CHK, 0)
    T49._build(pg)
    T427._ev(pg, "gc:" + CHK)
    T427._ev(pg, "colall")
    K.eq(int(L["count"](cs, CHK)) - c0, n + n2, "DU a grid cell then Collect all: paid once (%d + %d)" % (n, n2))
    # Sell all (2 clicks) sells the stored stock once
    St.LOCK.lock()
    try:
        p.setProperty("ranching.i0.stored", "300"); St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    L["br"].put("bazaar:sell:" + CHK, JLong(4))   # the Bazaar buys Raw Chicken at 4
    pg = T427._page(L, ou, W_, RA)
    T427._ev(pg, "kup")
    T49._build(pg)
    r1 = T427._ev(pg, "k2sell")
    r2 = T427._ev(pg, "k2sell")
    s_ = int(M.stored(RA, p, 0))
    r3 = T427._ev(pg, "k2sell")
    K.check(r1.startswith("Click Sell all again") and s_ < 300 and int(M.stored(RA, p, 0)) == s_ and r3.startswith("Click Sell all again"),
            "DU Sell all: 2 clicks sell once (%s / %s)" % (r2[:60], r3[:40]))
    K.save()


# ---------------------------------------------------------------------------------------------------------- MG28: the migration
def _cnt(props, kinds=("ranching", "orchard")):
    isl = tot = items = 0
    for k_ in list(props):
        m = re.match(r"^(%s)\.i(\d+)\.type$" % "|".join(kinds), k_)
        if not m:
            continue
        isl += 1
        b = "%s.i%s." % (m.group(1), m.group(2))
        tot += len([x for x in props.get(b + "totems", "").split(",") if x.strip()])
        items += int(props.get(b + "stored", "0") or 0) + int(props.get(b + "seed", "0") or 0)
        lg = props.get(b + "legacy", "")
        if lg and ":" in lg:
            items += int(lg.rsplit(":", 1)[1]) * (100 if lg.startswith("Skyy_Ench") else 1)
        for part in props.get(b + "drops", "").split(","):
            if ":" in part:
                items += int(part.rsplit(":", 1)[1])
    return isl, tot, items


def run_mig(out, jar, scratch, _home):
    from jpype import JString
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "mg")
    St = L["ShStore"]
    sd = L["sd"]
    k2 = "00000000-0000-0000-0000-00000000abce-p1"
    f = os.path.join(sd, k2 + ".properties")
    body = ("v=1\npkey=%s\nmap.done=1\nclk.done=1\nforms=1\n"
            "orchard.auto=1\norchard.storage=5\norchard.offline=3\norchard.i0.type=apple\norchard.i0.size=2\norchard.i0.amt=4\norchard.i0.deco=2\norchard.i0.last=%d\n"
            "orchard.i0.stored=40\norchard.i0.seed=25\norchard.i0.legacy=Skyy_Ench_Apple\\:1\norchard.i0.totems=harvest_spirit\\:2\\:wider\\:faster\\:0\\:aa11,rain\\:1\n"
            "orchard.i0.drops=Plant_Fruit_Apple\\:7\norchard.i1.type=berries\norchard.i1.size=1\norchard.i1.last=%d\norchard.i1.stored=3\n"
            "ranching.auto=0\nranching.storage=2\nranching.i0.type=chicken\nranching.i0.size=1\nranching.i0.last=%d\nranching.i0.stored=11\n"
            "ranching.i0.totems=harvest_spirit\\:1,herd_pole\\:1\nranching.i0.nsize=2\n"
            "mining.i0.type=copper\nmining.i0.size=1\nmining.i0.last=%d\nmining.i0.stored=5\n") % (k2, T0, T0, T0, T0)
    open(f, "w", newline="\n").write(body)
    raw0 = open(f, "rb").read()
    b0 = T427._props(f)
    c_before = _cnt(b0)
    St.CACHE.remove(k2)
    m0 = int(St.CLK2MIG.get())
    q = St.get(JString(k2))
    K.check(q is not None and str(q.getProperty("clk2.done")) == "1", "MG28 the marker")
    K.eq(str(q.getProperty("orchard.i0.seed")), "0", "MG28 the automated Orchard's sapling store emptied")
    d = T425._drops(q, 0, "orchard")
    K.check(d.get("Plant_Sapling_Apple", 0) == 25 and d.get(APL, 0) == 7, "MG28 ... 25 Apple saplings in its storage, the old drops kept (%s)" % d)
    K.check(str(q.getProperty("orchard.i0.totems")) == "harvest_spirit:2:wider:faster:0:aa11,rain:1" and str(q.getProperty("ranching.i0.totems")) == "harvest_spirit:1,herd_pole:1",
            "MG28 every totem kept as it was (tiers, modifiers)")
    K.check(str(q.getProperty("ranching.i0.nsize")) == "2" and str(q.getProperty("orchard.i0.amt")) == "4" and str(q.getProperty("orchard.offline")) == "3",
            "MG28 the upgrades kept (Feed quality, Fruit trees, Offline Harvest)")
    hist = os.path.join(sd, "history", "clicker", k2 + ".pre-0.4.28.properties")
    K.check(os.path.isfile(hist) and open(hist, "rb").read() == raw0, "MG28 the History copy = the old file (byte-checked)")
    raw1 = open(f, "rb").read()
    a1 = T427._props(f)
    K.check(b"clk2.done=1" in raw1 and int(St.CLK2MIG.get()) == m0 + 1, "MG28 one save on disk, counted")
    c_after = _cnt(a1)
    K.check(c_before[:2] == c_after[:2] and c_after[2] >= c_before[2], "MG28 islands / totems before = after %s -> %s (items never fewer)" % (c_before, c_after))
    bad = sorted(k_ for k_ in set(b0) | set(a1) if b0.get(k_) != a1.get(k_) and k_ not in ("clk2.done", "orchard.i0.seed", "orchard.i0.drops", "orchard.i0.last", "orchard.i0.stored",
                                                                                          "orchard.i0.sacc", "orchard.i0.xpn", "orchard.i0.xpw", "orchard.i0.rolled", "orchard.offAt",
                                                                                          "orchard.i0.offAt"))   # the settle before the move writes its own bookkeeping
    K.check(not bad, "MG28 nothing else rewritten %s" % bad[:6])
    lg = ""
    for root_, dirs_, fs_ in os.walk(os.path.dirname(sd)):
        for fn_ in fs_:
            if fn_.startswith("collect") and fn_.endswith(".log"):
                lg += open(os.path.join(root_, fn_), encoding="utf8", errors="replace").read()
    K.check("ranching + orchard clicker migration" in lg and k2 in lg and "Undo" in lg, "MG28 the collect.log journal line with the Undo")
    St.CACHE.remove(k2)
    q = St.get(JString(k2))
    K.check(open(f, "rb").read() == raw1 and int(St.CLK2MIG.get()) == m0 + 1, "MG28 a second load changes nothing")
    # a profile without Ranching / Orchard: the marker only (no History copy, no save of its own)
    k3 = "00000000-0000-0000-0000-00000000abcf-p1"
    f3 = os.path.join(sd, k3 + ".properties")
    open(f3, "w", newline="\n").write("v=1\npkey=%s\nmap.done=1\nclk.done=1\nmining.i0.type=copper\nmining.i0.size=1\nmining.i0.last=%d\n" % (k3, T0))
    r3 = open(f3, "rb").read()
    c0 = int(St.CLK2CHK.get())
    St.CACHE.remove(k3)
    q3 = St.get(JString(k3))
    K.check(str(q3.getProperty("clk2.done")) == "1" and int(St.CLK2CHK.get()) == c0 + 1 and open(f3, "rb").read() == r3
            and not os.path.isfile(os.path.join(sd, "history", "clicker", k3 + ".pre-0.4.28.properties")), "MG28 no Ranching / Orchard: the marker rides along, nothing copied or saved")
    K.save()


# ---------------------------------------------------------------------------------------------------------- live28: start twice on a scratch COPY of the live data
KEEP_RX28 = re.compile(r"^(mining|foraging|farming|ranching|orchard|combat)\.i\d+\.(last|stored|legacy|xpn|xpw|sacc|drops|seed|rolled|ench|bags|offAt)$|"
                       r"^(mining|foraging|farming|ranching|orchard|combat)\.(offAt|lastCollect)$|^clk2?\.done$")


def run_live_mig(out, jar, scratch, home):
    import jpype
    from jpype import JString, JClass
    K = HK.Child(out)
    sd = os.path.join(home, "shards")
    files = sorted(f for f in os.listdir(sd) if f.endswith(".properties"))
    pb = dict((f, T427._props(os.path.join(sd, f))) for f in files)
    raw0 = dict((f, open(os.path.join(sd, f), "rb").read()) for f in files)
    L, ou, W_, p, lv, got = _env(scratch, K, "lmenv")
    St = L["ShStore"]
    L["ShCore"].NOW_TEST = 0
    St.DIR = JClass("java.nio.file.Paths").get(JString(sd), jpype.JArray(JString)([]))
    St.CACHE.clear()
    for f in files:
        St.get(JString(f[:-len(".properties")]))
    pa = dict((f, T427._props(os.path.join(sd, f))) for f in files)
    raw1 = dict((f, open(os.path.join(sd, f), "rb").read()) for f in files)
    rows = {}
    for f in files:
        b, a = pb[f], pa[f]
        cb, ca = T427._count(b), T427._count(a)
        rb, ra = _cnt(b), _cnt(a)
        rows[f] = (cb, ca, rb, ra)
        K.check(cb[0] == ca[0] and cb[1] == ca[1], "L28 %s: %d islands / %d totems kept (%s)" % (f, cb[0], cb[1], ca[:2]))
        K.check(ca[2] >= cb[2], "L28 %s: items %d -> %d (never fewer; production since the last save settles)" % (f, cb[2], ca[2]))
        K.check(rb[:2] == ra[:2] and ra[2] >= rb[2], "L28 %s: Ranching + Orchard %s -> %s" % (f, rb, ra))
        bad = sorted(k_ for k_ in set(b) | set(a) if b.get(k_) != a.get(k_) and not KEEP_RX28.match(k_))
        K.check(not bad, "L28 %s: no other key rewritten %s" % (f, bad[:6]))
        K.check(a.get("clk2.done") == "1" or raw1[f] == raw0[f], "L28 %s: the marker (or nothing to do and nothing written)" % f)
        if rb[0] > 0:
            K.check(os.path.isfile(os.path.join(sd, "history", "clicker", f[:-len(".properties")] + ".pre-0.4.28.properties")), "L28 %s: the History copy (owns Ranching / Orchard)" % f)
    St.CACHE.clear()
    for f in files:
        St.get(JString(f[:-len(".properties")]))
    pc = dict((f, T427._props(os.path.join(sd, f))) for f in files)
    raw2 = dict((f, open(os.path.join(sd, f), "rb").read()) for f in files)
    K.check(all(pc[f].get("clk2.done") == pa[f].get("clk2.done") and pc[f].get("clk.done") == pa[f].get("clk.done") for f in files), "L28 the second start: the markers hold")
    K.check(all(T427._count(pc[f])[:2] == T427._count(pa[f])[:2] and _cnt(pc[f])[:2] == _cnt(pa[f])[:2] for f in files), "L28 the second start: every island + totem the same")
    K.check(all(dict((k_, v_) for k_, v_ in pc[f].items() if not KEEP_RX28.match(k_)) == dict((k_, v_) for k_, v_ in pa[f].items() if not KEEP_RX28.match(k_)) for f in files),
            "L28 the second start: nothing else changes")
    K.notes.append("L28 live copy: %d profile files; (all islands, totems, items) before / after + (Ranching+Orchard) before / after: %s" % (len(files), json.dumps(rows)))
    print("L28 live copy: %d profile files: %s" % (len(files), rows))
    K.save()


EXPECT = {   # 0.4.27 -> 0.4.28
    'CfgFile': ['~<clinit>'], 'CfgFn': ['~m opExport'], 'CfgRows': ['~<clinit>', '~m header'], 'CfgRows1': ['~<clinit>'], 'CfgRows2': ['~<clinit>'],
    'ShCfg': ['+f DEF_OQ_XP', '+f DEF_OQ_ZLV', '+f DEF_RQ_XP', '+f DEF_RQ_ZLV', '+f OQ_FRUITS', '+f OQ_HP', '+f OQ_IRR', '+f OQ_NS_MAX', '+f OQ_NS_PER', '+f OQ_ON',
              '+f OQ_REGROW', '+f OQ_RMIN', '+f OQ_SAPF', '+f OQ_XP', '+f OQ_ZLV', '+f RQ_EXTRA', '+f RQ_HP', '+f RQ_NS_MAX', '+f RQ_NS_PER', '+f RQ_ON', '+f RQ_REST', '+f RQ_RMIN',
              '+f RQ_ROLLS', '+f RQ_TROUGH', '+f RQ_XP', '+f RQ_ZLV', '~<clinit>', '~m loadCfg'],
    'ShClk': ['+f GATHERED', '+f ORK', '+f O_BLOCK', '+f O_QMAX', '+f O_QMIN', '+f PICKED', '+f RNK', '+f RX_ID', '+f RX_XP', '+f R_EX', '+f R_QMAX', '+f R_QMIN',
              '+f TENDED', '+m exXp', '+m extraP', '+m gather', '+m gatherOn', '+m gatherRegrowMs', '+m gatherXp', '+m qroll', '+m rollsAt', '~<clinit>', '~m buyNode',
              '~m chop', '~m clicker'],
    'ShCore': ['~m modMats', '~m spiritMats'], 'ShFill': ['~m markFixed'], 'ShIsl': ['+m enchX', '+m ownSeed', '~m mats', '~m tok', '~m zoneNeed'],
    'ShPage': ['+f O_PICK', '+f O_TREE', '+f R_ANI', '+f R_REST', '+m fillOrch', '+m fillRanch', '~<clinit>', '~m actClick', '~m build0', '~m buildClick'],
    'ShStore': ['+f CLK2CHK', '+f CLK2MIG', '+m migrate4', '+m snapClk2', '~<clinit>', '~m get', '~m migrate', '~m migrate2', '~m migrate3', '~m save'],
    'ShTotem': ['+f EN_ID', '+f EN_NM', '~<clinit>', '~m pretty'], 'SkyyShardsPlugin': ['~m setup'],
}


def _compare28(out, jar, old_jar, pkg, expect, added, removed=()):
    """non-class files: the 25 new 1x pictures, the Ranching / Orchard Map tab pictures gone; every other non-class file identical"""
    with zipfile.ZipFile(jar) as a, zipfile.ZipFile(old_jar) as b:
        na, nb = set(a.namelist()), set(b.namelist())
        new = sorted(n for n in na - nb if not n.endswith(".class"))
        gone = sorted(n for n in nb - na if not n.endswith(".class"))
        rx_new = re.compile(r"^Common/UI/Custom/SkyyShards/Map/Clk(RAni\d|RRest|OTree\d|OPick\d)\.png$")
        rx_gone = re.compile(r"^Common/UI/Custom/SkyyShards/Map/(Base(Ranching|Orchard)\.png|(Ranching|Orchard)E\d+@2x\.png)$")
        assert all(rx_new.match(n) for n in new) and len(new) == 25, "C new non-class files: %s" % [n for n in new if not rx_new.match(n)][:8]
        assert all(rx_gone.match(n) for n in gone), "C gone non-class files: %s" % [n for n in gone if not rx_gone.match(n)][:8]
        chg = sorted(n for n in na & nb if not n.endswith(".class") and a.read(n) != b.read(n))
        assert chg == ["manifest.json"], "C changed non-class files: %s" % chg[:8]
    print("C. %d new 1x pictures, %d old pictures gone; every other non-class file unchanged; manifest.json changed" % (len(new), len(gone)))
    cp = os.path.join(SCRATCH, "compare-%s.jar" % VERSION)
    with zipfile.ZipFile(jar) as zi, zipfile.ZipFile(old_jar) as zo0, zipfile.ZipFile(cp, "w", zipfile.ZIP_DEFLATED) as zo:
        for n in zi.namelist():
            if not n.endswith(".class") and n != "manifest.json":
                continue
            zo.writestr(n, zi.read(n))
        for n in zo0.namelist():
            if not n.endswith(".class") and n != "manifest.json":
                zo.writestr(n, zo0.read(n))
    T419._compare(out, cp, old_jar, pkg, expect, added, removed)


# RETIRED 0.4.27 CHECKS: the behaviour they pinned is replaced on purpose (each reason is a 0.4.28 spec line; the new phases check the new behaviour).
T427.RETIRED += [
    (r"^W27 the portal of kind [34] opens view 0", "SPEC 4: the Ranching / Orchard portals open their clicker (PG28)"),
    (r"^W27 the Orchard menu's rail leads to the Foraging clicker", "SPEC 4: the Orchard portal opens the Orchard clicker - no old menu rail (PG28)"),
    (r"^FX27 fix2: the locked Orchard portal opens its old menu", "SPEC 4: a locked Orchard portal opens nothing, like every clicker shard (ShClk.clicker)"),
    (r"^FX27 fix2: the rail to the locked Foraging clicker stays shut", "SPEC 4: the old Orchard menu (and its rail) never opens"),
    (r"^FZ Ranching / Orchard / Combat stay open: got \[20, 20, 0\]", "SPEC 3: Ranching / Orchard zones now lock by their skill level (PG28 checks the Boar lock)"),
]

PHASES = [("static", run_static), ("ranch28", run_ranch), ("orch28", run_orch), ("page28", run_page), ("costs28", run_costs), ("dupe28", run_dupe), ("mig28", run_mig)] + \
         [x for x in T427.PHASES if x[0] not in ("static", "livemig")] + [("livemig28", run_live_mig)]


if __name__ == "__main__":
    HK.run_compare = _compare28
    ph = PHASES
    if "--only" in sys.argv and "--phase" not in sys.argv:
        want = set(HK.arg("--only").split(","))
        ph = [x for x in PHASES if x[0] in want]
    HK.run(name="SkyyShards", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=ph, script=__file__, live=(T416.T46.LIVE_SH, "mods/Skyy_SkyyShards"))
