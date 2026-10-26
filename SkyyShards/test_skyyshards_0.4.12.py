"""Harness for SkyyShards 0.4.12 (HOTFIX: every shard + Totem Bench cost counts and pays from the Pocket Dimension; tools/shards_0_4_12_patch.py,
on top of 0.4.11).
Build first:
    python tools/shards_0_4_12_patch.py && python SkyyShards/build_skyyshards_0.4.12.py
    python SkyyShards/test_skyyshards_0.4.12.py [--keep]

  S    static   the patch re-runs to identical bytes; no new registerSystem / registerCommand; the ready line; the 0.4.10 hotfix kept
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.4.11 -> 0.4.12: exactly the planned members differ (EXPECT); every non-class file (page markup, maps, assets) identical
  411  every 0.4.11 harness phase on the 0.4.12 jar (and through it 0.4.10 ... 0.4.6), incl. PHASE O / O2 (the in-order selector walks),
       width (every Map text against its label) and F (the click flows)
  BG   bags     EXECUTED on the 0.4.6 fixture + a Magic Bags stub (sacks:fn:count / take / put / commit / all): the Map tab's 'you have N'
                = inventory + bags (green), paused = inventory only + the rail hint, no SkyySacks = inventory only; a sub-upgrade paid half
                from the inventory half from the bags (committed, collect.log names the bag part); refused coins / a refused save / a short
                bag take = EVERYTHING back (inventory + bags, nothing committed); paused = the refusal says so; purchase() (Storage) and
                purchaseN from the bags; the Totem Bench: Craft (kTx 'you:' + Ready), Make Pole (tierUp), Bench upgrade - counts + payments
                from the bags, refusals back; the totem page: Add booster + Add modifier from the bags; the texts' widths
  D    live     START TWICE on a scratch COPY of NewBetaTest's Skyy_SkyyShards (the 0.4.10 live phase)
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util, subprocess, json, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.4.12"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "shbags", "h")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyShards-%s.jar" % VERSION)]
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyShards-0.4.11.jar")
GEN = os.path.join(HERE, "build_skyyshards_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyshards_0.4.11.py")
PATCH = os.path.join(ROOT, "tools", "shards_0_4_12_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.shards."
_argv = list(sys.argv)
_spec = importlib.util.spec_from_file_location("test_skyyshards_0_4_11", os.path.join(HERE, "test_skyyshards_0.4.11.py"))
T411 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T411)
sys.argv[:] = _argv
T411.JAR = JAR
T410, T49, T48, T46 = T411.T410, T411.T49, T411.T48, T411.T46
for _m in (T410, T49, T48, T46, T411.T47):
    _m.JAR = JAR
OWNER = T46.OWNER
FK, CK = 2, 5
SUP = T49._superseded
GOOD, BAD = T49.GOOD, T49.BAD


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyShards 0.4.12 - build script') and g.count('VERSION = "0.4.12"\n') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.check("0.4.12: every shard + Totem Bench cost counts and pays from the Pocket Dimension too; 0.4.11: THE COMBAT SHARD" in g, "S the ready line names the round (and keeps 0.4.11's)")
    K.check("this.kShown = kShownSig(this.kZ)" in g and "if (this.kst != null) kSets(b); else stSets(b);" in g, "S the 0.4.10 hotfix is kept (kShown + status sets after base2)")
    K.check(g.count("takeAll(cs, ids, q, kept)") == 0 and g.count("@PKG@.ShInv.take2(cs, item, qty, kept)") == 0, "S no cost path takes from the inventory only any more")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


# ---------------------------------------------------------------------------------------------------------- the bag stub
def _bags(L):
    from jpype import JClass, JLong
    br, PyFn = L["br"], L["PyFn"]
    bags = {"have": {}, "ledger": {}, "committed": {}, "short": False, "paused": False, "calls": []}

    def b_count(a):
        bags["calls"].append(("count", str(a[1])))
        return JLong(-1 if bags["paused"] else bags["have"].get(str(a[1]), 0))

    def b_take(a):
        i_, n_ = str(a[1]), int(a[2])
        if bags["paused"]:
            return JLong(0)
        m = min(n_, bags["have"].get(i_, 0))
        if bags["short"]:
            m = max(0, m - 1)
        bags["have"][i_] = bags["have"].get(i_, 0) - m
        bags["ledger"][i_] = bags["ledger"].get(i_, 0) + m
        return JLong(m)

    def b_put(a):
        i_, n_ = str(a[1]), int(a[2])
        m = min(n_, bags["ledger"].get(i_, 0))
        bags["ledger"][i_] = bags["ledger"].get(i_, 0) - m
        bags["have"][i_] = bags["have"].get(i_, 0) + m
        return JLong(m)

    def b_commit(a):
        i_, n_ = str(a[1]), int(a[2])
        m = min(n_, bags["ledger"].get(i_, 0))
        bags["ledger"][i_] = bags["ledger"].get(i_, 0) - m
        bags["committed"][i_] = bags["committed"].get(i_, 0) + m
        return JLong(m)

    def b_all(u):
        bags["calls"].append(("all", ""))
        if bags["paused"]:
            return None
        m = JClass("java.util.HashMap")()
        for k_, v_ in bags["have"].items():
            if v_ > 0:
                m.put(k_, JLong(v_))
        return m
    FNS = (("count", b_count), ("take", b_take), ("put", b_put), ("commit", b_commit), ("all", b_all))

    def install():
        for k_, f_ in FNS:
            br.put("sacks:fn:" + k_, PyFn(f_))

    def remove():
        for k_, _f in FNS:
            br.remove("sacks:fn:" + k_)
    install()
    bags["install"], bags["remove"] = install, remove
    return bags


def _owed(bags):
    return sum(v for v in bags["ledger"].values())


# ---------------------------------------------------------------------------------------------------------- BG: the bags
def run_bags(out, jar, scratch, _home):
    from jpype import JClass, JInt, JLong
    import skyyui as SUI
    K = HK.Child(out)
    L = T411._L(os.path.join(scratch, "bg"), K)
    St, Isl, Mth, Core, Door, Cfg, Page, Cb, Inv, Tot = (L[n] for n in ("ShStore", "ShIsl", "ShMath", "ShCore", "ShDoor", "ShCfg", "ShPage", "ShCombat", "ShInv", "ShTotem"))
    inv, count, UUID, coins, PyFn = (L[n] for n in ("inv", "count", "UUID", "coins", "PyFn"))
    bags = _bags(L)
    ou = UUID.fromString(OWNER)
    W = "skyy-island-" + OWNER
    now = 1790000000000
    Core.NOW_TEST = now
    Isl.LEVEL_TEST = PyFn(lambda a: JInt(99))
    Door.door(ou, OWNER, "farming", W, 29, 129, -31)
    p = St.get(OWNER)
    S = dict((str(n), i) for i, n in enumerate(Page.SLOT_NAME))

    def collect_log():
        for root, _d, fs in os.walk(os.path.join(scratch, "bg")):
            for f_ in fs:
                if f_ == "collect.log":
                    return open(os.path.join(root, f_), encoding="utf-8").read()
        return ""
    t0 = int(Isl.LAD0[FK])
    tm0 = str(Cb.subMat(FK, 0))
    m0 = Isl.mats(FK, t0, tm0, 0, JLong(1))
    ids0, q0 = [str(x) for x in m0[0]], [int(x) for x in m0[1]]
    K.check(ids0[0] == "Plant_Crop_Wheat_Item" and q0[0] == 16, "BG fixture: T1 Wheat Small Crop Amount 1 costs %s" % list(zip(ids0, q0)))
    cs = inv(27, 27, 9)
    coins["bal"] = 10000000
    Page.TEST_INV = cs
    pg = Page(ou, W)
    pg.kind = FK
    pg.view = 0
    tx = lambda n: str(pg.mTx[S[n]])
    co = lambda n: str(pg.mCol[S[n]]).lower()
    pg.act("mn0", None, None)
    # ---- the Map tab counts: inventory + bags
    for i_, q_ in zip(ids0, q0):
        bags["have"][i_] = q_ * 3
    pg.fill(OWNER, cs)
    K.check(int(pg.mV) == 1 and tx("RU0I") == "%d Wheat (you have %d)" % (q0[0], q0[0] * 3) and co("RU0I") == GOOD.lower(),
            "BG Skyy's case: the island view counts the Pocket Dimension - '%s' green (was '(you have 0)')" % tx("RU0I"))
    hint0 = str(pg.mHint)
    K.check("paused" not in hint0, "BG ... the rail hint as before: %s" % hint0)
    K.check(bags["calls"].count(("all", "")) == 1, "BG ... ONE bag read for the whole fill (sacks:fn:all, before the store lock): %s" % bags["calls"][:5])
    bags["paused"] = True
    pg.fill(OWNER, cs)
    K.check(tx("RU0I") == "%d Wheat (you have 0)" % q0[0] and co("RU0I") == BAD.lower() and "paused" in str(pg.mHint),
            "BG bags paused: inventory only (red) and the rail says so: '%s' / %s" % (tx("RU0I"), pg.mHint))
    hl = T48._lines(str(pg.mHint), SUI.MAP_RAIL_W - 16 - 4, 15)
    K.check(hl <= T48._lines(hint0, SUI.MAP_RAIL_W - 16 - 4, 15) and hl <= 3, "BG ... the paused hint fits the rail hint box (%d lines)" % hl)
    bags["paused"] = False
    bags["remove"]()
    pg.fill(OWNER, cs)
    K.check(tx("RU0I") == "%d Wheat (you have 0)" % q0[0] and "paused" not in str(pg.mHint), "BG no SkyySacks: inventory only, nothing said: %s" % tx("RU0I"))
    bags["install"]()
    # ---- a sub-upgrade paid half from the inventory, half from the bags
    half = q0[0] // 2
    T48._fill(L, cs, [(ids0[0], half)])
    bags["have"] = {ids0[0]: 20}
    for i_, q_ in zip(ids0[1:], q0[1:]):
        bags["have"][i_] = q_
    b0 = coins["bal"]
    r = str(Core.buySub(ou, OWNER, FK, 0, 0, cs))
    K.check(r.startswith("+") and count(cs, ids0[0]) == 0 and bags["have"][ids0[0]] == 20 - (q0[0] - half) and _owed(bags) == 0
            and bags["committed"].get(ids0[0]) == q0[0] - half and str(p.getProperty("farming.i0.amt")) == "1" and coins["bal"] < b0,
            "BG Crop Amount 1 paid %d from the inventory + %d from the bags, the bag part COMMITTED: %s (bags %s)" % (half, q0[0] - half, r, bags["have"]))
    K.check(("(from bags: %d %s)" % (q0[0] - half, ids0[0])) in collect_log(), "BG ... collect.log names the bag part")
    # ---- refusals give everything back (inventory + bags, nothing committed)
    m1 = Isl.mats(FK, t0, tm0, 0, JLong(2))
    q1 = [int(x) for x in m1[1]]
    T48._fill(L, cs, [(ids0[0], 5)])
    bags["have"] = dict((i_, q_ * 2) for i_, q_ in zip(ids0, q1))
    snap = dict(bags["have"])
    com0 = dict(bags["committed"])

    def same(tag):
        return count(cs, ids0[0]) == 5 and bags["have"] == snap and _owed(bags) == 0 and bags["committed"] == com0 and str(p.getProperty("farming.i0.amt")) == "1"
    coins["fail"] = True
    r = str(Core.buySub(ou, OWNER, FK, 0, 0, cs))
    coins["fail"] = False
    K.check(r.startswith("-The coins could not be taken - your items are back") and same("coins"), "BG coins refused: inventory AND bag items back, nothing committed: %s / %s" % (r, bags["have"]))
    St.FAIL_TEST = True
    c1 = coins["bal"]
    r = str(Core.buySub(ou, OWNER, FK, 0, 0, cs))
    St.FAIL_TEST = False
    K.check(r.startswith("-It could not be saved - your items and coins are back") and same("save") and coins["bal"] == c1, "BG a refused save: everything back (inventory + bags + coins): %s" % r)
    bags["short"] = True
    r = str(Core.buySub(ou, OWNER, FK, 0, 0, cs))
    bags["short"] = False
    K.check(r.startswith("-The items could not be taken - nothing was bought") and same("short") and coins["bal"] == c1, "BG a short bag take: everything back: %s" % r)
    bags["paused"] = True
    r = str(Core.buySub(ou, OWNER, FK, 0, 0, cs))
    bags["paused"] = False
    K.check(r.startswith("-You need %d Wheat (you have 5 - your Pocket Dimension is paused, only your inventory counts)" % q1[0]) and same("paused"),
            "BG paused: refused, and it says why: %s" % r)
    K.check(SUI.text_width(r[1:], 15, True) <= 1566 - 4, "BG ... the paused refusal fits the status line (%d px)" % SUI.text_width(r[1:], 15, True))
    bags["remove"]()
    r = str(Core.buySub(ou, OWNER, FK, 0, 0, cs))
    K.check(r == "-You need %d Wheat (you have 5)." % q1[0] and same("absent"), "BG no SkyySacks: inventory only, as before: %s" % r)
    bags["install"]()
    r = str(Core.buySub(ou, OWNER, FK, 0, 0, cs))
    K.check(r.startswith("+") and count(cs, ids0[0]) == 0 and bags["have"][ids0[0]] == q1[0] * 2 - (q1[0] - 5) and _owed(bags) == 0, "BG ... then bought: inventory first, the rest from the bags: %s" % r)
    # ---- purchase(): Storage II from the bags only (the shard's upgrade item)
    upg = str(L["ShKind"].UPG[FK])
    ne = int(Cfg.storeEnch(2))
    bags["have"] = {upg: ne + 3}
    pg.act("mhub", None, None)
    pg.fill(OWNER, cs)
    K.check(tx("RStoreI").startswith("%d %s (you have %d)" % (ne, str(Tot.pretty(upg)), ne + 3)) or tx("RStoreI").startswith("%d %s (have %d)" % (ne, str(Tot.pretty(upg)), ne + 3)),
            "BG the shard view's Storage line counts the bags: %s" % tx("RStoreI"))
    r = str(Core.buyStorage(ou, OWNER, FK, cs))
    K.check(r.startswith("+Storage is now tier 2") and bags["have"][upg] == 3 and bags["committed"].get(upg) == ne and _owed(bags) == 0, "BG Storage II paid from the bags (purchase()): %s" % r)
    # purchaseN (no caller left in 0.4.12, kept bag-aware)
    bags["have"] = {upg: 7}
    St.LOCK.lock()
    try:
        r = Core.purchaseN(ou, OWNER, FK, p, cs, upg, JLong(5), JLong(10), ["farming.bgtest"], ["1"], "bgtest", "bg test")
    finally:
        St.LOCK.unlock()
    K.check(r is None and bags["have"][upg] == 2 and _owed(bags) == 0 and str(p.getProperty("farming.bgtest")) == "1", "BG purchaseN pays from the bags too: %s" % r)
    # ---- the Totem Bench: Craft, Make Pole, Bench upgrade
    rid = dict((str(x), i) for i, x in enumerate(Cfg.CRAFT_ID))
    ri = rid["Skyy_Totem_Rain"]
    rc = Core.recipe(Cfg.CRAFT[ri])
    rids, rq = [str(x) for x in rc[0]], [int(x) for x in rc[1]]
    TB = inv(9, 9)
    bags["have"] = dict((i_, q_) for i_, q_ in zip(rids, rq))
    Page.TEST_INV = TB
    pb = Page(ou, W)
    pb.kind = FK
    pb.kSel = ri
    pb.fillBench(OWNER, TB)
    row = [str(pb.kSt[i]) for i in range(int(pb.kN)) if int(pb.kIdx[i]) == ri]
    K.check(str(pb.kTx[0]) == "%d %s (you: %d)" % (rq[0], str(Tot.pretty(rids[0])), rq[0]) and str(pb.kCol[0]).lower() == GOOD.lower(),
            "BG bench Craft tab: '%s' counts the bags (was '(you: 0)')" % pb.kTx[0])
    pb.kSel = 0
    pb.fillBench(OWNER, TB)
    row = [str(pb.kSt[i]) for i in range(int(pb.kN)) if int(pb.kIdx[i]) == ri]
    K.check(row == ["Ready"], "BG ... the Rain Totem row says Ready (was 'Need items'): %s" % row)
    bags["paused"] = True
    pb.fillBench(OWNER, TB)
    bags["paused"] = False
    K.check("paused" in str(pb.bCap2) and SUI.text_width(str(pb.bCap2), 13, False) <= 410 - 4, "BG bench, bags paused: the caption says so and fits: %s" % pb.bCap2)
    coins["fail"] = True
    r = str(Core.craftAt(ou, OWNER, FK, ri, TB))
    coins["fail"] = False
    K.check(r.startswith("-The items or coins could not be taken - everything is back") and bags["have"] == dict(zip(rids, rq)) and _owed(bags) == 0,
            "BG bench craft, coins refused: the bag items back: %s" % r)
    full = inv(1)
    T48._fill(L, full, [("Rock_Stone", 100)])
    r = str(Core.craftAt(ou, OWNER, FK, ri, full))
    K.check(r.startswith("-Make room in your inventory first - everything is back") and bags["have"] == dict(zip(rids, rq)) and _owed(bags) == 0,
            "BG bench craft, no room for the totem: the bag items back: %s" % r)
    r = str(Core.craftAt(ou, OWNER, FK, ri, TB))
    rn = [list(x) for x in Inv.totems(TB) if str(x[2]) == "Skyy_Totem_Rain"]
    K.check(r.startswith("+Crafted Rain Totem I") and rn and all(bags["have"][i_] == 0 for i_ in rids) and _owed(bags) == 0, "BG bench craft paid from the bags: %s" % r)
    # Make Pole (tierUp): the Rain Totem I just crafted -> Pole II, the cost from the bags
    a = rn[0]
    st_ = TB[int(a[0])].getItemStack(int(a[1]))
    d_ = Tot.docOf(st_)
    cost = Tot.costAt(FK, "Skyy_Totem_Rain", d_.toJson())
    tc = Core.recipe(cost)
    tids, tq = [str(x) for x in tc[0]], [int(x) for x in tc[1]]
    bags["have"] = dict(zip(tids, tq))
    pb.bTab = 1
    pb.fillBench(OWNER, TB)
    rows = [str(pb.rTx[i]) for i in range(9)]
    K.check(any(r_.startswith("%d %s (you: %d)" % (tq[0], str(Tot.pretty(tids[0])), tq[0])) for r_ in rows), "BG bench Make Pole tab counts the bags: %s" % rows)
    uid = str(Tot.dstr(d_, "uid"))
    r = str(Core.tierUp(ou, OWNER, FK, int(a[0]), int(a[1]), uid, 1, TB))
    K.check(r.startswith("+Rain Totem I is now Rain Totem Pole II") and all(bags["have"][i_] == 0 for i_ in tids) and _owed(bags) == 0, "BG Make Pole paid from the bags: %s" % r)
    # Bench upgrade
    bt = Core.recipe(Cfg.benchItems(2, FK).strip())
    bids, bq = [str(x) for x in bt[0]], [int(x) for x in bt[1]]
    bags["have"] = dict(zip(bids, bq))
    pb.fillBench(OWNER, TB)
    ft = [str(pb.fTx[i]) for i in range(9)]
    K.check(any(f_.startswith("%d %s (you: %d)" % (bq[0], str(Tot.pretty(bids[0])), bq[0])) for f_ in ft), "BG bench Bench tab counts the bags: %s" % ft)
    St.FAIL_TEST = True
    c2 = coins["bal"]
    r = str(Core.benchUp(ou, OWNER, FK, TB))
    St.FAIL_TEST = False
    K.check(r.startswith("-The upgrade could not be saved") and bags["have"] == dict(zip(bids, bq)) and _owed(bags) == 0 and coins["bal"] == c2, "BG bench upgrade, a refused save: bag items + coins back: %s" % r)
    r = str(Core.benchUp(ou, OWNER, FK, TB))
    K.check(r.startswith("+Bench II") and all(bags["have"][i_] == 0 for i_ in bids) and _owed(bags) == 0, "BG bench upgrade paid from the bags: %s" % r)
    # ---- the totem page: Add booster + Add modifier from the bags
    St.LOCK.lock()
    try:
        p.setProperty("farming.i0.totems", "harvest_spirit:1:::0:bg0001")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    TT = inv(9)
    bid = str(Tot.BOOSTERS[1])
    mid = str(Tot.MOD_ITEMS[0])
    bags["have"] = {bid: 1, mid: 2}
    Page.TEST_INV = TT
    pt = Page(ou, W)
    pt.kind = FK
    pt.fill(OWNER, TT)
    K.check(str(pt.dTx[6]).endswith("(you: 2)") and str(pt.dCol[6]).lower() == GOOD.lower(), "BG the totem page's Add modifier line counts the bags: %s" % pt.dTx[6])
    r = str(Core.addBooster(ou, OWNER, FK, 0, 0, TT))
    K.check(r.startswith("+Booster burning") and bags["have"][bid] == 0 and _owed(bags) == 0, "BG Add booster: the essence from the bags: %s" % r)
    St.FAIL_TEST = True
    r = str(Core.addMod(ou, OWNER, FK, 0, 0, 0, TT))
    St.FAIL_TEST = False
    K.check(r.startswith("-Could not be saved - your modifier is back") and bags["have"][mid] == 2 and _owed(bags) == 0, "BG Add modifier, a refused save: back in the bags: %s" % r)
    r = str(Core.addMod(ou, OWNER, FK, 0, 0, 0, TT))
    K.check(r.startswith("+") and bags["have"][mid] == 1 and _owed(bags) == 0 and str(Core.at(FK, p, 0, 0)[2]) != "", "BG Add modifier from the bags: %s" % r)
    bags["paused"] = True
    r = str(Core.addBooster(ou, OWNER, FK, 0, 0, inv(9)))
    bags["paused"] = False
    K.check(r.startswith("-A booster is 1 Life, Water or Void Essence - you have none") and "paused" in r, "BG Add booster, bags paused: says so: %s" % r)
    # ---- widths: the Map requirement rows with Pocket Dimension sized counts
    pg.mapInit()
    names = [str(x) for x in Page.SLOT_NAME]
    ws = [int(x) for x in Page.SLOT_W]
    szs = [int(x) for x in Page.SLOT_SIZE]
    fl = [int(x) for x in Page.SLOT_FLAGS]
    rq_ = [i for i, nm_ in enumerate(names) if nm_.endswith(("C", "I", "J")) and nm_.startswith("R")] + [i for i, nm_ in enumerate(names) if nm_.startswith("V2R")]
    bad = []
    for nm2 in ("Rock Stone Cobble", "Enchanted Wheat", "Eternal Mushroom Spores", "Wheat", "Water Essence"):
        for si in rq_:
            pg.reqLine(si, JLong(9999999), JLong(640), nm2)
            t_ = str(pg.mTx[si])
            if SUI.text_width(t_, szs[si], bool(fl[si] & 1)) > ws[si] - 4:
                bad.append((names[si], t_))
    K.check(not bad, "BG a 9,999,999 Pocket Dimension count still fits every requirement row: %s" % bad[:3])
    out_ = []
    for h_, nm_ in ((9999999, "Wheat"), (9999999, "Eternal Mushroom Spores"), (250400, "Eternal Mushroom Spores"), (99999, "Eternal Mushroom Spores")):
        pg.reqLine(S["RU0I"], JLong(h_), JLong(640), nm_)
        out_.append(str(pg.mTx[S["RU0I"]]))
    K.eq(out_, ["640 Wheat (you have 9,999,999)", "640 Eternal Mushroom Spores (have 9.9M)", "640 Eternal Mushroom Spores (have 250K)",
                "640 Eternal Mushroom Spores (have 99,999)"], "BG ... only a row still too long shows 100,000+ short, rounded down")
    Isl.LEVEL_TEST = None
    Page.TEST_INV = None
    K.save()


# ---------------------------------------------------------------------------------------------------------- the 0.4.11 phases on the 0.4.12 jar
def run_players48(out, jar, scratch, home):
    """the map migration's collect.log line names the RUNNING version: 0.4.12 now"""
    SUP(("P one collect.log line with the Undo",), lambda: T48.run_players(out, jar, os.path.join(scratch, "p48"), home))
    d_ = json.load(open(out))
    K = HK.Child(out)
    K.ok, K.fails, K.notes = d_["ok"], d_["fails"], d_["notes"]
    txt = ""
    for root, _d, fs in os.walk(os.path.join(scratch, "p48")):
        for f_ in fs:
            if f_ == "collect.log":
                txt += open(os.path.join(root, f_), encoding="utf8").read()
    K.check("map migration (SkyyShards 0.4.12) 0a0a0a0a-1111-2222-3333-000000000001" in txt and "Undo:" in txt,
            "P the map migration's collect.log line (running version 0.4.12) with the Undo")
    K.save()


EXPECT = {   # 0.4.11 -> 0.4.12, checked by hand 2026-10-25: the version texts (CfgFn / CfgRows, ShStore log lines, the ready line) + the round
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "ShStore": ["~m migrate", "~m migrate2", "~m save"], "SkyyShardsPlugin": ["~m setup"],
    # the payments (the moved 0.4.7 bag helpers are byte-identical except refundPaid's log line)
    "ShCore": ["+m bagHave", "+m commitBags", "+m needTxt", "+m pausedTxt", "+m sumOf", "~m addBooster", "~m addMod", "~m benchUp", "~m craft",
               "~m purchase", "~m purchaseM", "~m purchaseN", "~m refundPaid", "~m tierUp"],
    # the counts (one bag read per fill) + the short big counts
    "ShPage": ["+f bagM", "+f bagSt", "+m bagLoad", "+m hav", "+m haveB", "~m fill", "~m fillBench", "~m fillBenchCraft", "~m fillBenchTier",
               "~m fillBenchUp", "~m fillMap", "~m fillTotems", "~m reqLine", "~m reqMats"]}
_ORIG_COMPARE = T411._ORIG_COMPARE


def _compare(out, jar, old_jar, pkg, expect, added, removed=()):
    """every non-class file identical (no markup / map / asset change); the classes as EXPECT"""
    import zipfile as _zf
    with _zf.ZipFile(jar) as a, _zf.ZipFile(old_jar) as b:
        na = dict((n_, a.read(n_)) for n_ in a.namelist() if not n_.endswith(".class"))
        nb = dict((n_, b.read(n_)) for n_ in b.namelist() if not n_.endswith(".class"))
    ch = sorted(n_ for n_ in set(na) | set(nb) if na.get(n_) != nb.get(n_) and n_ != "manifest.json")
    assert not ch, "C non-class files differ: %s" % ch[:8]
    print("C. %d non-class files identical (manifest.json aside)" % len(na))
    cps = []
    for j, tag in ((jar, VERSION), (old_jar, "old")):
        cp = os.path.join(SCRATCH, "compare-%s.jar" % tag)
        with _zf.ZipFile(j) as zi, _zf.ZipFile(cp, "w", _zf.ZIP_DEFLATED) as zo:
            for n_ in zi.namelist():
                if not T49.MAP_ENTRY.match(n_):
                    zo.writestr(n_, zi.read(n_))
        cps.append(cp)
    _ORIG_COMPARE(out, cps[0], cps[1], pkg, expect, added, removed)


HK.run_compare = _compare


def _p(fn, sup=()):
    return lambda out, jar, scratch, home: SUP(tuple(sup), lambda: fn(out, jar, os.path.join(scratch, "p411"), home))


if __name__ == "__main__":
    HK.run(name="SkyyShards", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("static", run_static), ("bags", run_bags),
                   ("exec48", _p(T49.run_exec48)), ("exec47", _p(T49.run_exec47)), ("exec46", _p(T49.run_exec46)), ("centre47", _p(T49.run_centre47)),
                   ("config48", _p(T49.run_config48)), ("mig48", _p(T410.run_mig48)), ("players48", _p(run_players48)), ("geo48", _p(T49.run_geo48)),
                   ("config49", _p(T49.run_config)), ("mig49", _p(T49.run_mig)), ("exec49", _p(T49.run_exec)), ("page49", _p(T49.run_page)),
                   ("width", _p(T49.run_width)), ("order", _p(T410.run_order)), ("flows", _p(T410.run_flows)),
                   ("zones", T411.run_zones), ("balance", T411.run_balance), ("land", T411.run_land), ("night", T411.run_night), ("spawn", T411.run_spawn),
                   ("buy", T411.run_buy), ("config", T411.run_config), ("gate", T411.run_gate), ("order2", T411.run_order2), ("live", T411.run_live411)],
           script=__file__, live=(T46.LIVE_SH, "mods/Skyy_SkyyShards"))
