"""Harness for SkyyShards 0.4.20 (smaller storage, true Auto-Compactor, shard XP 20 %, Mining ingots - tools/shards_0_4_20_patch.py, on top of 0.4.19).
Build first:
    python tools/shards_0_4_20_patch.py && python SkyyShards/build_skyyshards_0.4.20.py
    python SkyyShards/test_skyyshards_0.4.20.py [--keep]

  S20  static   the patch re-runs to identical bytes; header / VERSION / ready line; no new registerSystem / registerCommand; line endings kept
  CP   compress caps + over-cap stock kept; compression at settle (existing stock, 100 boundary, leftovers); limits; XP bookkeeping; Collect; every kind's rule;
                a pole removed; another item waiting; picked up; the map migration's retype
  SC   sell     Enchanted stock at its own price, then the leftover; half / all / amount; XP + collection x100; partial, zero, throw, retype on the way back; retries capped
  MG20 config   ShMig0420: fresh file, live config copy, every row untouched and hand-edited, CRLF, run twice
  OR   ingots   every Mining cost: tokens on all 11 ladder types, defaults file, recipe
  DB   debounce one tick of another profile key changes nothing, three do
  PG20 page     rows, hours to full, Compactor tiles, the Sell view on compressed + leftover stock
  then 0.4.19's phases (offline, migration, sell, page) + the older ones (open, bytecode, flows3, page49, live START TWICE); A verify, C compare, AA audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util, subprocess, json, math, re, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.4.20"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "sh020", "h")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyShards-%s.jar" % VERSION)]
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyShards-0.4.19.jar")
GEN = os.path.join(HERE, "build_skyyshards_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyshards_0.4.19.py")
PATCH = os.path.join(ROOT, "tools", "shards_0_4_20_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.shards."

# the 0.4.19 harness: its calls to changed signatures and the numbers this round moves on purpose are adjusted in memory
_T19 = open(os.path.join(HERE, "test_skyyshards_0.4.19.py"), encoding="utf8").read()
for _o, _n in ((', JDouble(1.0), JString(ci))', ', JDouble(1.0), JString(ci), False, 0)'),
               ('"Width: 220" in bd["mk"]', '"Width: 240" in bd["mk"]'),
               ('"PG the amount column is 220 wide', '"PG the amount column is 240 wide'),
               ('"Stored: 48,874" == str(pg.sv[2])', '"Stored: 48,874 " in str(pg.sv[2])'),
               ('"bonus finds stay" in str(pg.sv[4])', '"bonus finds" in str(pg.sv[4])'),
               ('K.check(rt > 0, "OF the test island works', 'p.setProperty("farming.storage", "5")   # 0.4.20: the phase counts more items than a tier 1 store holds\n    K.check(rt > 0, "OF the test island works'),
               ):
    assert _o in _T19, _o
    _T19 = _T19.replace(_o, _n)
_argv = list(sys.argv)
T419 = importlib.util.module_from_spec(importlib.util.spec_from_loader("test_skyyshards_0_4_19", loader=None))
T419.__dict__["__file__"] = os.path.join(HERE, "test_skyyshards_0.4.19.py")
exec(compile(_T19, T419.__file__, "exec"), T419.__dict__)
sys.argv[:] = _argv
T418, T46, T49, T410, T414, T415, T416, T411, T413 = T419.T418, T419.T46, T419.T49, T419.T410, T419.T414, T419.T415, T419.T416, T419.T411, T419.T413
T419.JAR = T418.JAR = T419.T417.JAR = JAR
T419.SCRATCH = T418.SCRATCH = T416.SCRATCH = T415.SCRATCH = T419.T417.SCRATCH = SCRATCH
OWNER, MEMBER, VISITOR = T419.OWNER, T419.MEMBER, T419.VISITOR
_W0 = T419._world
H = 3600000
FK = 2
MI, FO, RA = 0, 1, 3
T0 = 1790000000000
W, E = "Plant_Crop_Wheat_Item", "Skyy_Ench_Wheat"


def _world19(scratch, K):
    r = _W0(scratch, K)
    r[0]["ShMath"].SYNC_TICKS = 1                  # 0.4.19's phases: the login check acts at once
    return r


T419._world = _world19


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyShards 0.4.20 - build script') and g.count('VERSION = "0.4.20"\n') + g.count('VERSION = "0.4.20"\r\n') == 1, "S20 header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S20 no new %r" % w)
    K.check("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.20:" in g, "S20 the ready line names the round")
    K.check(g.count('"Longest production between visits"') == 0, "S20 the Server Setup label no longer says between visits")
    K.check("# shard.maxOfflineSec = the most time one catch-up" in g and "# shard.manualOfflineSec = before Automation, the most time one catch-up" in g and "stretch between visits" not in g, "S20 fix: no config comment still says between visits (online catch-up wording)")
    K.check('"shard.maxOfflineSec", "Longest online catch-up"' in g and "online gap" not in g, "S20 fix: the offline-limit rows say online catch-up")
    K.check("ROMAN[i], 5)" not in g and "Stacks of 100 before island bonus (%d = %s items). Auto-Compactor: counts Enchanted items." in g, "S20 fix: the storage row names items, no 'I of 5'")
    K.check("Online: most time one catch-up counts." in g and "Before Automation, online: most time one catch-up counts." in g, "S20 fix: both Server Setup help lines reworded, within the kit's 100 characters")
    K.check('" Ench + "' not in g, "S20 fix: the wide 'Ench + N / cap' amount is gone from the Collect row")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S20 the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S20 line endings kept")
    K.save()


def _kit(L, p, K):
    """the fakes for Collect / Sell: collections, XP, a Bazaar with a price per item"""
    from jpype import JArray, JLong
    fns, br, PyFn, St = L["fns"], L["br"], L["PyFn"], L["ShStore"]
    got = {"coll": {}, "xp": 0, "calls": [], "mode": "pay", "hook": None, "held": False}

    def coll_add(a):
        got["coll"][str(a[1])] = got["coll"].get(str(a[1]), 0) + int(a[2])
        return L["Bool"].TRUE

    def xp_add(a):
        got["xp"] += int(a[2])
        return L["Bool"].TRUE

    def sellfn(a):
        got["held"] = got["held"] or bool(St.LOCK.isHeldByCurrentThread())
        q = int(a[2])
        got["calls"].append((str(a[1]), q))
        if got["hook"]:
            h, got["hook"] = got["hook"], None
            h()
        m = got["mode"]
        if m == "zero":
            return JLong(0)
        if m == "throw":
            raise RuntimeError("bazaar broke")
        if m == "partial":
            return JArray(JLong)([111, q // 2])
        return JLong(q * (700 if str(a[1]).startswith("Skyy_Ench") else 5))
    fns.put("coll:fn:add", PyFn(coll_add))
    fns.put("skill:fn:addxp", PyFn(xp_add))
    fns.put("bazaar:fn:sell", PyFn(sellfn))
    br.put("bazaar:sell:" + W, JLong(5))
    br.put("bazaar:sell:" + E, JLong(700))
    return got


# ---------------------------------------------------------------------------------------------------------- CP: storage + compression
def run_comp(out, jar, scratch, _home):
    from jpype import JClass, JLong, JString
    K = HK.Child(out)
    L, ou, W_, p, lv = _W0(os.path.join(scratch, "cp"), K)
    M, St, Isl, Core, Cfg, Kind = L["ShMath"], L["ShStore"], L["ShIsl"], L["ShCore"], L["ShCfg"], L["ShKind"]
    M.ONLINE.put(OWNER, True)
    Core.NOW_TEST = T0
    got = _kit(L, p, K)
    lv["Mining"] = 9
    p.setProperty("farming.auto", "1"); p.setProperty("farming.paused", "0")
    rt = float(M.rate(FK, p, 0, JLong(T0)))
    K.check(rt > 0, "CP the test island works (%.3f / min)" % rt)
    item_ms = int(math.ceil(60000.0 / rt))

    def setst(s, cmp_=0, comp=None, last=T0):
        p.setProperty("farming.i0.stored", str(s))
        p.setProperty("farming.i0.last", str(last))
        p.setProperty("farming.compactor", str(cmp_))
        p.remove("farming.i0.xpn"); p.remove("farming.i0.xpw"); p.remove("farming.i0.ench"); p.remove("farming.i0.legacy")
        if comp is not None:
            p.setProperty("farming.i0.legacy", comp)
        got["coll"].clear(); got["xp"] = 0; got["calls"][:] = []

    def st():
        return int(M.stored(FK, p, 0))

    def cn():
        return int(M.comp(FK, p, 0))

    # 1. the caps
    K.check([int(Cfg.stacks(i)) for i in range(1, 6)] == [10, 30, 80, 200, 500], "CP storage tiers 10 / 30 / 80 / 200 / 500 stacks")
    for t, want in ((1, 1000), (2, 3000), (3, 8000), (4, 20000), (5, 50000)):
        p.setProperty("farming.storage", str(t))
        K.check(int(M.cap(FK, p)) == want, "CP tier %d = %d items an island" % (t, want))
    p.setProperty("farming.storage", "1")
    base_cap = int(M.capOf(FK, p, 0))
    K.check(base_cap >= 1000, "CP island cap at tier 1: %d (size / upgrades multiply it)" % base_cap)
    CAP = base_cap
    # 2. stock over the new cap is never cut, the island only stops
    setst(50 * CAP, last=T0 - H)
    n = int(M.settle(FK, p, 0, JLong(T0)))
    K.check(n == 0 and st() == 50 * CAP and int(p.getProperty("farming.i0.last")) == T0, "CP 50x the cap stored: nothing cut, nothing made, clock moved")
    setst(CAP + 100)
    cs = L["inv"](45, 45)
    r = str(Core.collect(ou, JString(OWNER), FK, 0, cs))
    K.check(int(L["count"](cs, W)) == CAP + 100 and st() == 0, "CP over-cap stock can still be collected: %s" % r)
    setst(CAP - 10, last=T0 - H)
    M.settle(FK, p, 0, JLong(T0))
    K.check(st() == CAP, "CP below the cap fills up to the cap and stops (%d)" % st())
    # 3. compression of the stock already there, leftover
    setst(12345, 1)
    n = int(M.settle(FK, p, 0, JLong(T0)))
    K.check(n == 0 and cn() == 123 and st() == 45 and str(p.getProperty("farming.i0.legacy")) == E + ":123", "CP first settle with a Compactor: 12,345 -> 123 Enchanted + 45 (%s)" % p.getProperty("farming.i0.legacy"))
    K.check(int(M.baseOf(FK, p, 0)) == 12345, "CP the base-item total did not change")
    n = int(M.settle(FK, p, 0, JLong(T0)))
    K.check(n == 0 and cn() == 123 and st() == 45, "CP settling again changes nothing")
    # 4. the 100 boundary
    setst(99, 1, last=T0 - item_ms)
    n = int(M.settle(FK, p, 0, JLong(T0)))
    K.check(n == 1 and st() == 0 and cn() == 1, "CP 99 + 1 made = 1 Enchanted, 0 loose (made %d, %d, %d)" % (n, st(), cn()))
    setst(60, 1, comp=E + ":7", last=T0 - 350 * item_ms)
    n = int(M.settle(FK, p, 0, JLong(T0)))
    K.check(n >= 350 and cn() == 7 + (60 + n) // 100 and st() == (60 + n) % 100, "CP 60 + %d made + 7 Enchanted (%d, %d)" % (n, st(), cn()))
    setst(99, 1, last=T0)
    M.settle(FK, p, 0, JLong(T0))
    K.check(st() == 99 and cn() == 0 and p.getProperty("farming.i0.legacy") is None, "CP 99 stays base items, no legacy line")
    # 5. the limit: 1 Enchanted = 1 space, so 100x in base items; Compactor II doubles it; hours to full
    setst(0, 1, comp=E + ":%d" % (CAP - 1), last=T0 - 200 * item_ms)
    n = int(M.settle(FK, p, 0, JLong(T0)))
    K.check(n == 100 and cn() == CAP and st() == 0 and int(p.getProperty("farming.i0.last")) == T0, "CP one space left: only 100 more made, then full (made %d, %d)" % (n, cn()))
    n = int(M.settle(FK, p, 0, JLong(T0 + H)))
    K.check(n == 0 and int(M.msToFull(FK, p, 0, JLong(T0 + H))) == -1, "CP a full island stays full, no hours to full")
    setst(0, 1)
    K.check(int(M.limOf(FK, p, 0)) == CAP * 100 and int(M.usedOf(FK, p, 0)) == 0 and abs(int(M.msToFull(FK, p, 0, JLong(T0))) - CAP * 100 * 60000.0 / rt) < 2, "CP full in = 100 x the cap in base items at the rate")
    setst(0, 2, comp=E + ":1500")
    cap2 = int(M.capOf(FK, p, 0))
    K.check(cap2 == 2 * CAP and int(M.limOf(FK, p, 0)) == cap2 * 100 and int(M.usedOf(FK, p, 0)) == 150000, "CP Compactor II: +100 %% storage counts in Enchanted items (%d)" % cap2)
    # over the cap after a change: kept, stops
    setst(250 * CAP, 1, last=T0 - H)
    n = int(M.settle(FK, p, 0, JLong(T0)))
    K.check(n == 0 and cn() == 2 * CAP + CAP // 2 and st() == 0, "CP a huge old stock compresses (over the cap: kept, nothing made): %d" % cn())
    # 6. XP bookkeeping and Collect
    setst(1000, 1)
    p.setProperty("farming.i0.xpn", "1000"); p.setProperty("farming.i0.xpw", "9000.0")
    M.settle(FK, p, 0, JLong(T0))
    K.check(cn() == 10 and st() == 0 and str(p.getProperty("farming.i0.xpn")) == "1000" and abs(float(M.xpAvg(FK, p, 0, JLong(T0))) - 9.0) < 1e-6, "CP XP bookkeeping counts base items: 9 per item survives (%s)" % p.getProperty("farming.i0.xpn"))
    cs = L["inv"](45, 45)
    r = str(Core.collect(ou, JString(OWNER), FK, 0, cs))
    pct = int(Cfg.XP_PCT)
    K.check(pct == 20, "CP shard.xpPercent default 20 (%d)" % pct)
    K.check(int(L["count"](cs, E)) == 10 and int(L["count"](cs, W)) == 0 and cn() == 0 and st() == 0, "CP Collect gives the 10 Enchanted: %s" % r)
    K.check(got["coll"].get(W) == 1000 and got["xp"] == 1000 * 9 * pct // 100, "CP a compressed item pays 100 base items of XP + collection: %s %d" % (got["coll"], got["xp"]))
    K.check(p.getProperty("farming.i0.legacy") is None, "CP the line is gone after a full Collect")
    # the same stock uncompressed pays the same
    setst(1000, 0)
    p.setProperty("farming.i0.xpn", "1000"); p.setProperty("farming.i0.xpw", "9000.0")
    cs = L["inv"](45, 45)
    Core.collect(ou, JString(OWNER), FK, 0, cs)
    K.check(got["coll"].get(W) == 1000 and got["xp"] == 1000 * 9 * pct // 100, "CP ... exactly what 1,000 loose items pay")
    # leftover + Enchanted; bonus finds keep their own way
    setst(245, 1)
    p.setProperty("farming.i0.ench", "3")
    cs = L["inv"](45, 45)
    r = str(Core.collect(ou, JString(OWNER), FK, 0, cs))
    K.check(int(L["count"](cs, E)) == 2 + 3 and int(L["count"](cs, W)) == 45 and got["coll"].get(W) == 245 + 300, "CP Enchanted + leftover + bonus finds: %s %s" % (r, got["coll"]))
    # a small inventory: nothing lost, the rest stays compressed
    setst(100000, 1)
    M.settle(FK, p, 0, JLong(T0))
    total0 = int(M.baseOf(FK, p, 0))
    cs = L["inv"](1, 1)
    r = str(Core.collect(ou, JString(OWNER), FK, 0, cs))
    gv = int(L["count"](cs, E))
    K.check(cn() == 1000 - gv and st() == 0 and (got["coll"].get(W) or 0) == 100 * gv and int(M.baseOf(FK, p, 0)) == total0 - 100 * gv, "CP a small inventory: %d given, the rest stays, credit only for what was given (%s)" % (gv, r))
    disk = T419._disk(L, OWNER)
    K.check(str(disk.getProperty("farming.i0.legacy")) == E + ":" + str(1000 - gv), "CP ... and it is on disk")
    # a refused save: nothing moves
    setst(500, 1)
    M.settle(FK, p, 0, JLong(T0))
    cs = L["inv"](45, 45)
    St.FAIL_TEST = True
    r = str(Core.collect(ou, JString(OWNER), FK, 0, cs))
    St.FAIL_TEST = False
    K.check(r.startswith("-Collect failed") and cn() == 5 and int(L["count"](cs, E)) == 0, "CP a refused save: nothing moves: %s" % r)
    # picked up
    setst(500, 1, last=T0 - H)
    p.setProperty("farming.paused", "1")
    n = int(M.settle(FK, p, 0, JLong(T0)))
    K.check(n == 0 and cn() == 5, "CP a picked-up shard: nothing made, the stock keeps (compressed) (%d)" % cn())
    cs = L["inv"](45, 45)
    Core.collect(ou, JString(OWNER), FK, 0, cs)
    K.check(int(L["count"](cs, E)) == 5, "CP ... and can be collected")
    p.setProperty("farming.paused", "0")
    # another item waiting: no compression, plain cap, the old item is paid at the next Collect
    setst(500, 1, comp="Plant_Crop_Carrot_Item:9")
    M.settle(FK, p, 0, JLong(T0))
    K.check(st() == 500 and cn() == 0 and str(p.getProperty("farming.i0.legacy")) == "Plant_Crop_Carrot_Item:9" and int(M.limOf(FK, p, 0)) == CAP, "CP another item waiting in the line: compression waits, plain cap")
    cs = L["inv"](45, 45)
    Core.collect(ou, JString(OWNER), FK, 0, cs)
    K.check(int(L["count"](cs, "Plant_Crop_Carrot_Item")) == 9 and st() == 0, "CP ... Collect pays the old line")
    setst(500, 1, comp="Other_Item:0")
    M.settle(FK, p, 0, JLong(T0))
    K.check(cn() == 5 and st() == 0, "CP a used-up line is free")
    # the map migration's uncompress
    setst(0, 1, comp=E + ":3")
    p.setProperty("farming.i0.stored", "12")
    M.uncompress(FK, p, 0)
    K.check(st() == 312 and cn() == 0 and p.getProperty("farming.i0.legacy") is None, "CP uncompress (only the 0.4.8 map migration's retype uses it)")
    # the other kinds
    for kd, name, worker, smelt_id in ((MI, "mining", "quarry_spirit:1", "Skyy_Ench_Copper"), (FO, "foraging", "lumber_spirit:1", "Skyy_Ench_Oak")):
        M.starter(kd, p, JLong(T0))
        p.setProperty(name + ".auto", "1")
        p.setProperty(name + ".compactor", "1")
        p.setProperty(name + ".i0.stored", "523")
        p.setProperty(name + ".i0.last", str(T0))
        p.setProperty(name + ".i0.totems", worker)
        M.settle(kd, p, 0, JLong(T0))
        if kd == MI:
            mcap = int(M.capOf(kd, p, 0))
            K.check(int(M.stored(kd, p, 0)) == 523 and int(M.comp(kd, p, 0)) == 0 and str(M.compForm(kd, p, 0)) == "" and int(M.limOf(kd, p, 0)) == mcap, "CP Mining without Auto-Smelt: no Enchanted form, stays ore, plain cap")
            K.check(str(Core.sellItem(kd, p, 0)) == "Ore_Copper", "CP ... sells ore")
            p.setProperty(name + ".i0.totems", worker + ",autosmelt_pole:1")
            M.settle(kd, p, 0, JLong(T0))
            K.check(int(M.comp(kd, p, 0)) == 5 and int(M.stored(kd, p, 0)) == 23 and str(M.compId(kd, p, 0)) == smelt_id, "CP Mining with the pole: 5 Enchanted Copper, 23 left (%s)" % p.getProperty("mining.i0.legacy"))
            cs = L["inv"](45, 45)
            got["coll"].clear()
            r = str(Core.collect(ou, JString(OWNER), kd, 0, cs))
            K.check(int(L["count"](cs, smelt_id)) == 5 and int(L["count"](cs, "Ingredient_Bar_Copper")) == 23 and got["coll"].get("Ore_Copper") == 523, "CP Mining Collect: Enchanted ingots + ingots, credited as 523 ore: %s %s" % (r, got["coll"]))
            # the pole taken away with Enchanted stock: it keeps its item, counts 1 each, plain cap
            p.setProperty(name + ".i0.legacy", smelt_id + ":40")
            p.setProperty(name + ".i0.totems", worker)
            p.setProperty(name + ".i0.stored", str(mcap - 35))
            p.setProperty(name + ".i0.last", str(T0))
            K.check(int(M.usedOf(kd, p, 0)) == mcap + 5 and int(M.limOf(kd, p, 0)) == mcap, "CP pole removed: ore + 40 Enchanted count 1 each against the cap")
            n = int(M.settle(kd, p, 0, JLong(T0 + H)))
            K.check(n == 0 and int(M.stored(kd, p, 0)) == mcap - 35 and int(M.comp(kd, p, 0)) == 40, "CP ... over that = kept, nothing made")
        else:
            K.check(int(M.comp(kd, p, 0)) == 5 and int(M.stored(kd, p, 0)) == 23 and str(M.compId(kd, p, 0)) == smelt_id, "CP Foraging: 5 Enchanted Oak, 23 left")
    M.starter(RA, p, JLong(T0))
    p.setProperty("ranching.compactor", "1"); p.setProperty("ranching.i0.stored", "523"); p.setProperty("ranching.i0.last", str(T0))
    M.settle(RA, p, 0, JLong(T0))
    K.check(int(M.stored(RA, p, 0)) == 523 and int(M.comp(RA, p, 0)) == 0 and str(M.compForm(RA, p, 0)) == "", "CP Ranching (nothing Enchanted at shard level): unchanged even with the key set")
    K.save()


# ---------------------------------------------------------------------------------------------------------- SC: Sell on compressed stock
def run_sell(out, jar, scratch, _home):
    from jpype import JClass, JLong, JString, JDouble
    K = HK.Child(out)
    L, ou, W_, p, lv = _W0(os.path.join(scratch, "sc"), K)
    M, St, Isl, Core, Cfg = L["ShMath"], L["ShStore"], L["ShIsl"], L["ShCore"], L["ShCfg"]
    M.ONLINE.put(OWNER, True)
    Core.NOW_TEST = T0
    got = _kit(L, p, K)
    p.setProperty("farming.auto", "1"); p.setProperty("farming.paused", "0"); p.setProperty("farming.compactor", "1")

    def setup(s):
        p.setProperty("farming.i0.stored", str(s))
        p.setProperty("farming.i0.last", str(T0))
        p.remove("farming.i0.legacy")
        p.setProperty("farming.i0.xpn", str(s)); p.setProperty("farming.i0.xpw", str(s * 6.0))
        M.settle(FK, p, 0, JLong(T0))
        got["coll"].clear(); got["xp"] = 0; got["calls"][:] = []; got["mode"] = "pay"; got["held"] = False

    def cn():
        return int(M.comp(FK, p, 0))

    def st():
        return int(M.stored(FK, p, 0))

    def sell(mode, txt=""):
        return str(Core.sell(ou, JString(OWNER), FK, 0, mode, JString(txt)))
    pct = int(Cfg.XP_PCT)
    setup(5045)
    K.check(str(Core.sellItem(FK, p, 0)) == E and int(Core.priceOf(JString(E))) == 700, "SC Enchanted stock is what is on sale, at its own Bazaar price")
    r = sell(0)
    K.check(got["calls"] == [(E, 25)] and cn() == 25 and st() == 45 and not got["held"], "SC half of 50 Enchanted = 25: %s" % r)
    K.check(got["coll"].get(W) == 2500 and got["xp"] == 2500 * 6 * pct // 100, "SC sold Enchanted pays 100 base items each: %s %d" % (got["coll"], got["xp"]))
    K.check("25 Enchanted Wheat" in r and "17,500 coins" in r, "SC the status line names the item: %s" % r)
    log = open(os.path.join(os.path.dirname(L["sd"]), "collect.log"), encoding="utf8").read()
    K.check("SELL debit 25 " + E in log, "SC collect.log: the debit names the Enchanted item")
    disk = T419._disk(L, OWNER)
    K.check(str(disk.getProperty("farming.i0.legacy")) == E + ":25" and str(disk.getProperty("farming.i0.xpn")) == "2545", "SC the file was written (base items 2,545)")
    r = sell(2, "26")
    K.check(r.startswith("-Only 25 stored") and cn() == 25, "SC an amount over the Enchanted count is refused: %s" % r)
    r = sell(2, "5")
    K.check(got["calls"][-1] == (E, 5) and cn() == 20, "SC typed amount counts Enchanted items")
    r = sell(1)
    K.check(got["calls"][-1] == (E, 20) and cn() == 0 and st() == 45 and p.getProperty("farming.i0.legacy") is None, "SC Sell all: the Enchanted stock; the loose 45 stay: %s" % r)
    K.check(str(Core.sellItem(FK, p, 0)) == W, "SC ... then base items are on sale")
    r = sell(1)
    K.check(got["calls"][-1] == (W, 45) and st() == 0, "SC ... and sell at their own price: %s" % r)
    # zero, throw, partial
    for mode, what in (("zero", "pays 0"), ("throw", "throws")):
        setup(5045)
        got["mode"] = mode
        r = sell(1)
        K.check(cn() == 50 and st() == 45 and got["xp"] == 0 and not got["coll"] and str(T419._disk(L, OWNER).getProperty("farming.i0.legacy")) == E + ":50", "SC %s: every Enchanted item back, on disk, no XP: %s" % (what, r))
        K.check(str(p.getProperty("farming.i0.xpn")) == "5045" and abs(float(M.xpAvg(FK, p, 0, JLong(T0))) - 6.0) < 1e-6, "SC ... XP bookkeeping back too (%s)" % p.getProperty("farming.i0.xpn"))
    setup(5045)
    got["mode"] = "partial"
    r = sell(1)
    K.check(cn() == 25 and got["coll"].get(W) == 2500 and "only part" in r, "SC partial: half of the Enchanted back: %s" % r)
    # a refused save
    setup(5045)
    St.FAIL_TEST = True
    r = sell(1)
    St.FAIL_TEST = False
    K.check(cn() == 50 and not got["calls"] and r.startswith("-Sale failed"), "SC a refused save: nothing taken, the Bazaar not called: %s" % r)
    # Collect during a sale
    setup(5045)
    cs = L["inv"](45, 45)
    got["hook"] = lambda: Core.collect(ou, JString(OWNER), FK, 0, cs)
    r = sell(2, "10")
    K.check(cn() == 0 and st() == 0 and int(L["count"](cs, E)) == 40 and int(L["count"](cs, W)) == 45 and got["calls"][-1] == (E, 10), "SC Collect during a sale: nothing doubled")
    # the island changed on the way back (type): waits in the line, never in the new item's store; Collect pays it as Enchanted
    setup(5045)
    t0 = str(p.getProperty("farming.i0.type"))

    def retype():
        p.setProperty("farming.i0.type", "potato" if t0 != "potato" else "carrot")
    got["mode"] = "zero"
    got["hook"] = retype
    r = sell(1)
    K.check(str(p.getProperty("farming.i0.legacy")) == E + ":50" and st() == 45, "SC retyped during the sale: the 50 wait as Enchanted Wheat: %s" % p.getProperty("farming.i0.legacy"))
    p.setProperty("farming.i0.type", t0)
    # busy lock on the way back
    setup(5045)
    got["mode"] = "zero"
    hold = {}
    got["hook"] = lambda: T414._grab(St.LOCK, hold)
    sv_w = int(JClass(PKG + "ShLock").WAIT_MS)
    JClass(PKG + "ShLock").WAIT_MS = 20
    r = sell(1)
    q1 = int(Core.SELLQ.size())
    T414._release(hold)
    JClass(PKG + "ShLock").WAIT_MS = sv_w
    Core.flushSell()
    K.check(q1 == 1 and int(Core.SELLQ.size()) == 0 and cn() == 50, "SC a busy lock: queued, the tick puts the Enchanted stock back (%d queued)" % q1)
    # retries capped
    Core.SELLQ.clear()
    Cfg.WARNED.remove("sellback")
    Core.sellBackQ(JString("bad/key"), FK, 0, JLong(5), JDouble(1.0), JString(E), True, 0)
    tries = 1
    while tries < 80 and int(Core.SELLQ.peek()[6]) < 9000000000000000000:
        Core.NOW_TEST = int(Core.SELLQ.peek()[6])
        Core.flushSell()
        tries += 1
    Core.NOW_TEST = T0
    K.check(tries == 60 and int(Core.SELLQ.size()) == 1, "SC a broken file: 60 tries a minute apart, then it stops being read (%d)" % tries)
    log = open(os.path.join(os.path.dirname(L["sd"]), "collect.log"), encoding="utf8").read()
    K.check("SELL back FAILED (retrying once more at the stop) 5 " + E in log, "SC ... the amount is in collect.log")
    Core.flushSell()
    K.check(int(Core.SELLQ.peek()[8]) == 60, "SC ... the second's flush leaves it alone")
    Core.flushSellAt(JLong(JClass("java.lang.Long").MAX_VALUE))
    K.check(int(Core.SELLQ.peek()[8]) == 61, "SC ... the server stop still tries it")
    Core.SELLQ.clear()
    # an Enchanted line pays x100 at Collect
    setup(0)
    p.setProperty("farming.i0.legacy", E + ":3")
    got["coll"].clear(); got["xp"] = 0
    cs = L["inv"](45, 45)
    Core.collect(ou, JString(OWNER), FK, 0, cs)
    K.check(int(L["count"](cs, E)) == 3 and got["coll"].get(W) == 300 and got["xp"] > 0, "SC Collect credits Enchanted from the line x100: %s" % got["coll"])
    K.save()


# ---------------------------------------------------------------------------------------------------------- MG20
def run_mig20(out, jar, scratch, _home):
    from jpype import JClass
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    K = HK.Child(out)
    Mig = JClass(PKG + "ShMig0420")
    MK = "skyyshards-0.4.20-storage"
    nf = [0]

    def world(b_):
        nf[0] += 1
        home = os.path.join(scratch, "m20%d" % nf[0], "mods", "Skyy_SkyyShards")
        os.makedirs(home)
        Cfg, path = T49.T42.kit_home(home)
        f = os.path.join(home, "config.properties")
        if b_ is not None:
            open(f, "wb").write(b_)
        return home, f, Cfg, path

    def props(b_):
        P_ = JClass("java.util.Properties")()
        P_.load(JClass("java.io.ByteArrayInputStream")(b_))
        return dict((str(k), str(P_.getProperty(k))) for k in P_.stringPropertyNames())

    KEY = [str(x) for x in Mig.KEY]
    OLD = [str(x) for x in Mig.OLDV]
    NEW = [str(x) for x in Mig.NEWV]
    K.check(len(KEY) == 8 and KEY[:6] == ["storage.tier1", "storage.tier2", "storage.tier3", "storage.tier4", "storage.tier5", "shard.xpPercent"] and KEY[7] == "up.auto.items.mining" and KEY[6].startswith("craft."), "MG20 the rows: %s" % KEY)
    K.check(OLD[:6] == ["243", "875", "1993", "3573", "5611", "50"] and NEW[:6] == ["10", "30", "80", "200", "500", "20"], "MG20 old -> new numbers")
    K.check(OLD[6].startswith("Ore_Copper:128") and NEW[6].startswith("Ingredient_Bar_Copper:128") and OLD[7] == "Ore_Copper:128" and NEW[7] == "Ingredient_Bar_Copper:128", "MG20 the ore rows")
    # fresh file
    home, f, Cfg, path = world(None)
    Cfg.loadCfg(True)
    b0 = open(f, "rb").read()
    txt = b0.replace(b"\r\n", b"\n").decode("latin-1").split("\n")
    K.check(all((KEY[i] + "=" + NEW[i]) in txt for i in range(len(KEY))), "MG20 a fresh file holds the new values")
    K.check(b0.count(MK.encode()) == 1 and str(Mig.run(path(f))) == "" and open(f, "rb").read() == b0, "MG20 a fresh file: marker, nothing to do")
    K.check(int(Cfg.XP_PCT) == 20 and int(Cfg.ST1) == 10 and int(Cfg.ST5) == 500, "MG20 the fields read")
    # live copy
    live = os.path.join(T46.LIVE_SH, "config.properties")
    A_ = open(live, "rb").read()
    home, f, Cfg, path = world(A_)
    r = str(Mig.run(path(f)))
    b1 = open(f, "rb").read()
    pa, pb = props(A_), props(b1)
    for i in range(len(KEY)):
        was = pa.get(KEY[i])
        K.check(pb.get(KEY[i]) == (NEW[i] if was is not None and was.replace(" ", "") == OLD[i].replace(" ", "") else was), "MG20 live config %s: %s -> %s" % (KEY[i], was, pb.get(KEY[i])))
    K.check(all(pb[k] == pa[k] for k in pa if k not in KEY) and len(pb) == len(pa), "MG20 live config: every other line the same")
    K.check(b1.count(MK.encode()) == 1 and (b"\r\n" in A_) == (b"\r\n" in b1), "MG20 live config: marker once, line endings kept")
    K.check(str(Mig.run(path(f))) == "" and open(f, "rb").read() == b1, "MG20 run twice = once")
    # every row: untouched and hand-edited (CRLF)
    body = "".join("%s=%s\r\n" % (KEY[i], OLD[i]) for i in range(len(KEY)))
    old = ("# keep me\r\nshard.on=true\r\n" + body).encode("latin-1")
    home, f, Cfg, path = world(old)
    r = str(Mig.run(path(f)))
    b2 = open(f, "rb").read()
    pb = props(b2)
    K.check(all(pb[KEY[i]] == NEW[i] for i in range(len(KEY))) and pb["shard.on"] == "true" and b2.count(b"\r\n") >= 10 and b2.startswith(b"# keep me\r\n"), "MG20 untouched CRLF file: all 8 rows moved, bytes + endings kept: %s" % r[:120])
    ch = open(os.path.join(home, "config-changes.log"), encoding="utf8").read()
    K.check(all(KEY[i] in ch for i in range(len(KEY))), "MG20 a change-log row each (Undo)")
    hs = [n for n in os.listdir(os.path.join(home, "config-history")) if n.endswith(".bak")]
    K.check(len(hs) == 1 and open(os.path.join(home, "config-history", hs[0]), "rb").read() == old, "MG20 History holds the old file byte for byte")
    for i in range(len(KEY)):
        hand = ("7777" if i < 6 else "Rock_Stone:1")
        body2 = "".join("%s=%s\n" % (KEY[j], hand if j == i else OLD[j]) for j in range(len(KEY)))
        home, f, Cfg, path = world(body2.encode("latin-1"))
        r = str(Mig.run(path(f)))
        pb = props(open(f, "rb").read())
        K.check(pb[KEY[i]] == hand and all(pb[KEY[j]] == NEW[j] for j in range(len(KEY)) if j != i) and "kept" in r, "MG20 %s hand-edited: kept and logged, the others moved" % KEY[i])
    home, f, Cfg, path = world(None)
    K.check(str(Mig.run(path(f))) == "", "MG20 no file: nothing")
    K.save()


# ---------------------------------------------------------------------------------------------------------- OR: ingots, not ore
def run_ore(out, jar, scratch, _home):
    from jpype import JClass, JString
    K = HK.Child(out)
    L, ou, W_, p, lv = _W0(os.path.join(scratch, "or"), K)
    Isl, Cfg = L["ShIsl"], L["ShCfg"]
    n0, nm = int(Isl.LAD0[0]), int(Isl.LADN[0])
    K.check(nm == 11, "OR 11 Mining types")
    for t in range(n0, n0 + nm):
        K.check(str(Isl.tok(0, t, "raw")) == str(Isl.SMELT[t]) and str(Isl.tok(0, t, "raw")).startswith("Ingredient_Bar_"), "OR %s raw = %s" % (Isl.KEY[t], Isl.tok(0, t, "raw")))
        for tmpl, part in ((str(Cfg.BUY_ITEMS[0]), 0), ("raw:16|ench:1|ench:2", 0), ("raw:8,Ingredient_Water_Essence:2|ench:1", 0)):
            ids = [str(x) for x in Isl.mats(0, t, JString(tmpl), part, 1)[0]]
            K.check(ids and not any(i.startswith("Ore_") for i in ids), "OR %s %s: %s" % (Isl.KEY[t], tmpl, ids))
    K.check(str(Isl.tok(1, int(Isl.LAD0[1]), "raw")).startswith("Wood_"), "OR other kinds keep their raw item")
    K.check(str(Cfg.AUTO_ITEMS[0]) == "Ingredient_Bar_Copper:128" and str(Cfg.DEF_AUTO_ITEMS[0]) == "Ingredient_Bar_Copper:128", "OR Automation: Copper Ingots")
    with zipfile.ZipFile(jar) as z:
        rows = z.read("skyyshards-config-rows.txt").decode("utf8") if "skyyshards-config-rows.txt" in z.namelist() else ""
    g = open(GEN, encoding="utf8", newline="").read()
    K.check('"Ingredient_Bar_Copper:128,Ingredient_Life_Essence:8;500"' in g, "OR the Quarry Spirit recipe takes ingots")
    K.save()


# ---------------------------------------------------------------------------------------------------------- DB: debounce
def run_deb(out, jar, scratch, _home):
    from jpype import JClass, JLong, JString
    K = HK.Child(out)
    L, ou, W_, p, lv = _W0(os.path.join(scratch, "db"), K)
    M = L["ShMath"]
    HS = JClass("java.util.HashSet")
    A, B_ = OWNER, OWNER + "-p2"
    M.ONLINE.clear(); M.SYNC_C.clear()
    M.ONLINE.put(A, True)
    p.setProperty("farming.auto", "1")

    def keys(*a):
        s = HS()
        for x in a:
            s.add(JString(x))
        return s
    M.sync(keys(A), JLong(T0))
    M.sync(keys(B_), JLong(T0 + 1000))
    M.sync(keys(A), JLong(T0 + 2000))
    K.check(bool(M.ONLINE.containsKey(A)) and not bool(M.ONLINE.containsKey(B_)) and int(M.SYNC_C.size()) == 0 and p.getProperty("farming.offAt") is None, "DB one tick of another key: nothing happens, nothing written")
    M.sync(keys(B_), JLong(T0 + 3000))
    M.sync(keys(B_), JLong(T0 + 4000))
    K.check(bool(M.ONLINE.containsKey(A)), "DB two ticks: still waiting")
    M.sync(keys(B_), JLong(T0 + 5000))
    K.check(not bool(M.ONLINE.containsKey(A)) and bool(M.ONLINE.containsKey(B_)), "DB three ticks: the switch happens")
    K.check(str(p.getProperty("farming.offAt")) == str(T0 + 5000), "DB ... the logout is stamped at that tick")
    M.ONLINE.clear(); M.SYNC_C.clear()
    K.save()


# ---------------------------------------------------------------------------------------------------------- PG20: the page
def run_page20(out, jar, scratch, _home):
    from jpype import JClass, JLong, JString
    K = HK.Child(out)
    L, ou, W_, p, lv = _W0(os.path.join(scratch, "pg20"), K)
    M, Core, Cfg, Page = L["ShMath"], L["ShCore"], L["ShCfg"], L["ShPage"]
    Core.NOW_TEST = T0
    M.ONLINE.put(OWNER, True)
    got = _kit(L, p, K)
    p.setProperty("farming.auto", "1"); p.setProperty("farming.offline", "0"); p.setProperty("farming.compactor", "1")
    p.setProperty("farming.i0.stored", "51245"); p.setProperty("farming.i0.last", str(T0))
    icap = "{:,}".format(int(M.capOf(FK, p, 0)))
    pg = Page(ou, W_)
    pg.kind = FK
    pg.view = 0

    def click(a, **extra):
        d = {"a": a}
        d.update(extra)
        pg.handleDataEvent(None, None, json.dumps(d))
        r = T410.full(pg)
        K.check(not r["miss"] and not r["unbound"], "PG20 %s: the page walks clean %s %s" % (a, r["miss"][:2], r["unbound"][:2]))
        return T49._build(pg)
    click("tab0")
    K.check(str(pg.cAmt[0]) == "512 Ench / " + icap, "PG20 the row: %s" % pg.cAmt[0])
    K.check("+45 loose" in str(pg.cSub[0]) and "full in" in str(pg.cSub[0]) and len(str(pg.cSub[0])) <= 60, "PG20 sub line: %s" % pg.cSub[0])
    K.check(str(pg.cAll[0]) == "512 Enchanted + 45 items" and "collection +51,245" in str(pg.cAll[2]), "PG20 Collect all counts base items, says Enchanted: %s / %s" % (pg.cAll[0], pg.cAll[2]))
    bd = click("sopen0")
    K.check(bool(pg.svOn) and str(pg.sv[0]) == "Enchanted Wheat" and str(pg.sv[2]) == "Stored: 512 Enchanted Wheat" and str(pg.sv[3]).startswith("Coins each: 700"), "PG20 the view names the item: %s / %s / %s" % (pg.sv[0], pg.sv[2], pg.sv[3]))
    K.check("45 " in str(pg.sv[4]) and "Then:" in str(pg.sv[4]), "PG20 the leftover: %s" % pg.sv[4])
    K.check(str(pg.sv[5]).startswith("Half (256): about 179,200 coins") and "collection +25,600" in str(pg.sv[6]), "PG20 preview half x100: %s / %s" % (pg.sv[5], pg.sv[6]))
    bd = click("sprev", **{"@SAmt": "10"})
    K.check(str(pg.sv[9]).startswith("Amount (10): about 7,000 coins") and "collection +1,000" in str(pg.sv[10]), "PG20 preview typed: %s / %s" % (pg.sv[9], pg.sv[10]))
    bd = click("samt", **{"@SAmt": "10"})
    K.check(int(M.comp(FK, p, 0)) == 502 and got["calls"][-1] == (E, 10), "PG20 Sell amount sells Enchanted")
    # full + other amount shapes
    p.setProperty("farming.i0.legacy", E + ":" + icap.replace(",", "")); p.setProperty("farming.i0.stored", "0")
    click("sback")
    K.check("FULL" in str(pg.cSub[0]) and str(pg.cAmt[0]) == icap + " Ench / " + icap, "PG20 full: %s / %s" % (pg.cSub[0], pg.cAmt[0]))
    p.setProperty("farming.compactor", "0"); p.setProperty("farming.i0.legacy", E + ":3"); p.setProperty("farming.i0.stored", "12")
    click("tab0")
    K.check(str(pg.cAmt[0]) == "3 Ench / " + icap and "+12 loose" in str(pg.cSub[0]), "PG20 fix: Enchanted waiting, no Compactor: amount stays one form, loose on the sub-line: %s / %s" % (pg.cAmt[0], pg.cSub[0]))
    _sui = __import__("skyyui")
    K.check(_sui.text_width("305,000 Ench / 305,000", 20, bold=True) <= 240 and len(str(pg.cSub[0])) <= 60, "PG20 fix: worst amount + this sub-line fit the row")
    p.remove("farming.i0.legacy")
    click("tab0")
    K.check(str(pg.cAmt[0]) == "12 / " + icap, "PG20 no Compactor: as before: %s" % pg.cAmt[0])
    # the tiles
    K.check(str(pg.cmTx[1]).startswith("Stores 1 Enchanted Wheat per 100 made") and "100 x the space" in str(pg.cmTx[1]), "PG20 Auto-Compactor tile: %s" % pg.cmTx[1])
    K.check(str(pg.uTx[3]).startswith("Each island"), "PG20 storage words without a Compactor")
    p.setProperty("farming.compactor", "1")
    click("tab0")
    K.check(str(pg.uTx[3]).startswith("With the Auto-Compactor"), "PG20 storage words with a Compactor: %s" % pg.uTx[3])
    # the sub-line budget, worst case
    p.setProperty("farming.i0.stored", "99"); p.setProperty("farming.i0.ench", "123456")
    click("tab0")
    K.check(len(str(pg.cSub[0])) <= 60, "PG20 worst sub line stays inside the budget (%d): %s" % (len(str(pg.cSub[0])), pg.cSub[0]))
    p.setProperty("farming.i0.ench", "9000000000000000000")   # a bonus count too long for the row: cut at the limit
    click("tab0")
    K.check(len(str(pg.cSub[0])) == 60, "PG20 fix 2: an over-long bonus text is cut at 60 (%d): %s" % (len(str(pg.cSub[0])), pg.cSub[0]))
    K.save()


EXPECT = {   # 0.4.19 -> 0.4.20, checked by hand 2026-11-08: the version texts (CfgFn / CfgRows / ShStore.migrate + save / ShFill.markFixed / ready line) + the round
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'ShAdmin': ['~m run'],
    'ShCfg': ['~<clinit>', '~m loadCfg', '~m writeDefaults'],
    'ShCore': ['+m baseItem', '+m sellBack', '+m sellBackQ', '-m sellBack', '-m sellBackQ', '~m buyCompactor', '~m collect0', '~m flushSellAt', '~m sell0', '~m sellItem'],
    'ShFill': ['~m markFixed'],
    'ShIsl': ['+m enchBase', '~m tok'],
    'ShMath': ['+f SYNC_C', '+f SYNC_TICKS', '+m baseOf', '+m comp', '+m compForm', '+m compId', '+m compOn', '+m compSet', '+m compress', '+m legId', '+m legN', '+m limOf', '+m syncDue', '+m uncompress', '+m usedOf', '+m xpRe', '~<clinit>', '~m msToFull', '~m settle', '~m sync', '~m xpAvg'],
    'ShPage': ['+m fillSell', '+m svTwo', '-m fillSell', '-m svTwo', '~m buildFull', '~m fill', '~m fillMap'],
    'ShParticles': ['~m runIn'],
    'ShStore': ['~m migrate', '~m migrate2', '~m save'],
    'SkyyShardsPlugin': ['~m setup']
}


def run_livecomp(out, jar, scratch, _home):
    """every island of a read-only COPY of the live shard files: compression changes no base-item total, only an untouched file keeps the counts"""
    import shutil, glob
    from jpype import JClass, JLong
    K = HK.Child(out)
    L, ou, W_, p0, lv = _W0(os.path.join(scratch, "lc"), K)
    M = L["ShMath"]
    M.ONLINE.clear()
    M.ALL_ON_TEST = True
    Pr = JClass("java.util.Properties")
    src = os.path.join(T46.LIVE_SH, "shards")
    d = os.path.join(scratch, "lc-copy")
    os.makedirs(d, exist_ok=True)
    fs = glob.glob(os.path.join(src, "*.properties"))
    K.check(len(fs) > 0, "LC live shard files found (%d)" % len(fs))
    nisl = ncomp = 0
    for f in fs:
        g = os.path.join(d, os.path.basename(f))
        shutil.copyfile(f, g)
        q = Pr()
        q.load(JClass("java.io.ByteArrayInputStream")(open(g, "rb").read()))
        for kd in range(int(L["ShKind"].N)):
            for i in range(int(M.SLOTS)):
                if not bool(M.hasIsland(kd, q, i)):
                    continue
                q.setProperty(str(M.ik(kd, i, "last")), str(T0))
                b0 = int(M.baseOf(kd, q, i))
                M.settle(kd, q, i, JLong(T0))
                nisl += 1
                ncomp += 1 if int(M.comp(kd, q, i)) > 0 else 0
                K.check(int(M.baseOf(kd, q, i)) == b0 and int(M.stored(kd, q, i)) >= 0, "LC %s kind %d island %d: base items kept (%d)" % (os.path.basename(f)[:12], kd, i, b0))
                K.check(not bool(M.compOn(kd, q, i)) or int(M.stored(kd, q, i)) < 100, "LC ... compressing leaves under 100 loose")
    K.check(nisl > 0, "LC %d live islands settled, %d now hold Enchanted stock" % (nisl, ncomp))
    K.save()


def run_live(out, jar, scratch, home):
    T419.run_live(out, jar, scratch, home)


if __name__ == "__main__":
    HK.run_compare = T419._compare
    HK.run(name="SkyyShards", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=["ShMig0420"],
           phases=[("static", run_static), ("comp", run_comp), ("sell20", run_sell), ("mig20", run_mig20), ("ore", run_ore), ("deb", run_deb), ("page20", run_page20), ("livecomp", run_livecomp),
                   ("off", T419.run_off), ("mig", T419.run_mig), ("sell", T419.run_sell), ("page", T419.run_page),
                   ("open", T416._h(T416._g(T416.run_open), True)), ("bytecode", T415.run_bytecode),
                   ("flows3", T416._h(T416._g(T413.run_flows3))), ("page49", T419.run_page49),
                   ("live", run_live)],
           script=__file__, live=(T416.T46.LIVE_SH, "mods/Skyy_SkyyShards"))
