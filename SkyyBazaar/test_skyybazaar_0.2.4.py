"""Harness for SkyyBazaar 0.2.4 (bazaar:fn:sell, SkyyShards 0.4.19's Sell button; tools/bazaar_0_2_4_patch.py). Build first:
    python tools/bazaar_0_2_4_patch.py && python SkyyBazaar/build_skyybazaar_0.2.4.py --with SkyyCollections/SkyyCollections-0.2.36.jar
    python SkyyBazaar/test_skyybazaar_0.2.4.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, -Xverify:all, tools/harness_kit.py + the 0.1.20 / 0.2.0 stand-in engine):
  S     static   the patch re-runs to identical bytes; line endings kept; no new command / system / setting; the key is put in setup and
                 removed in shutdown before the last flush
  A     verify   every class loads + initialises
  C     compare  0.2.3 -> 0.2.4 (EXPECT below: only BzSellFn, the Trader sale methods, plugin setup / shutdown, the version texts)
  K     catalog  every Catalog constant = 0.2.3's (nothing priced changes)
  F     sell     EXECUTED on the stand-in engine through the real BzSellFn: a normal sale = the instant sale of the same items (coins, factor,
                 sold counter, bazaar:sell:<id>), big quantity with price impact, over MAXQ partial, unlisted / unusable / locked / walled, sell
                 cap prices + a cap that refuses, coin mod absent / refusing / throwing, full purse, offline / unknown, profile busy, bad arguments,
                 log + price-move + disk failure after the credit (no throw, coins kept, right answer), inventory + bags untouched, the
                 trades.log line, concurrent calls, the Market lock really held, the plugin's shutdown removing the key
  D     live     scratch COPIES of the live NewBetaTest Skyy_SkyyBazaar: the 0.2.4 start = the 0.2.3 start, a second 0.2.4 start writes nothing
  AA    audit    engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, subprocess, importlib.util, json, shutil, time, threading, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.2.4"
PKG = "com.skyy.bazaar."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyBazaar-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyBazaar-0.2.3.jar")
GEN = os.path.join(HERE, "build_skyybazaar_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyybazaar_0.2.3.py")
PATCH = os.path.join(ROOT, "tools", "bazaar_0_2_4_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "bz024", "bz")))
LIVE = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyBazaar")
# BzMarket.tiers inlines TIER_SPEC, built from tools/tier_tags.py, which gained the Gear 0.3.52 / 0.3.53 rows after 0.2.3 was built (static phase: only added rows)
EXPECT = {"BzMarket": ["~m tiers"], "Trader": ["+f CLOSED", "+m shardLanded", "+m shardPaid", "+m sellShard0", "+m shardWho", "+m sellShard"],
          "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "SkyyBazaarPlugin": ["~m setup", "~m shutdown"]}   # + the version texts
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = ["BzSellFn"]
U_NOBODY = "99999999-9999-4999-8999-999999999999"


def tmod(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    old = sys.argv
    sys.argv = [old[0]]
    try:
        spec.loader.exec_module(m)
    finally:
        sys.argv = old
    return m


# ------------------------------------------------------------------------------------------------------------------- S
def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.count('VERSION = "0.2.4"') == 1 and g.startswith('"""SkyyBazaar 0.2.4'), "S version + header")
    for w in ("registerSystem(", "registerCommand(", "CFG.row(", "Server Setup"):
        K.check(g.count(w) == o.count(w), "S no new %s (%d)" % (w, g.count(w)))
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    su = g[g.index("public void setup()"):]
    i_load, i_pub, i_put = su.index("@PKG@.Market.load();"), su.index("@PKG@.Market.publishAll();"), su.index('put("bazaar:fn:sell", new @PKG@.BzSellFn())')
    K.check(i_load < i_pub < i_put and g.count('put("bazaar:fn:sell"') == 1, "S setup puts the key once, after Market.load + publishAll")
    sd = g[g.index("protected void shutdown"):]
    K.check(g.count('remove("bazaar:fn:sell")') == 1 and sd.index('remove("bazaar:fn:sell")') < sd.index("@PKG@.Market.flush();"), "S shutdown removes the key before the last flush")
    K.check(sd.index("Trader.CLOSED = true;") < sd.index("@PKG@.Market.decay(") and su.index("Trader.CLOSED = false;") < su.index('put("bazaar:fn:sell"'), "S shutdown closes the sale before the last save; setup opens it before the key is published")
    z = zipfile.ZipFile(jar)
    pl = z.read("com/skyy/bazaar/SkyyBazaarPlugin.class")
    K.check(b"bazaar:fn:sell" in pl and "com/skyy/bazaar/BzSellFn.class" in z.namelist(), "S the built plugin class names the key; BzSellFn is in the jar")
    def spec(j):
        b = zipfile.ZipFile(j).read("com/skyy/bazaar/BzMarket.class")
        m = re.search(rb"Armor_Farming_Aubergine_Chest:[A-Za-z0-9_:|]+", b)
        return dict(x.split(":") for x in m.group(0).decode().split("|"))
    so, sn = spec(OLD_JAR), spec(jar)
    changed = [k for k in so if sn.get(k) != so[k]]
    K.check(not changed and len(sn) >= len(so), "S TIER_SPEC (tools/tier_tags.py): every 0.2.3 row kept with its tier (changed: %s)" % changed[:5])
    K.notes.append("S TIER_SPEC: %d -> %d rows; added since the 0.2.3 build: %s" % (len(so), len(sn), sorted(set(sn) - set(so))[:12]))
    K.save()


# ------------------------------------------------------------------------------------------------------------------- K
def _dump_consts(jar_path, dst):
    from jpype import JClass
    HK.jvm([jar_path, B.SERVER_JAR], verify=True)
    Mod = JClass("java.lang.reflect.Modifier")
    C = JClass(PKG + "Catalog")
    out = {}
    for f in C.class_.getDeclaredFields():
        m = f.getModifiers()
        if not (Mod.isStatic(m) and Mod.isFinal(m)):
            continue
        f.setAccessible(True)
        v = f.get(None)
        t = str(f.getType().getName())
        if t == "[Ljava.lang.String;":
            out[str(f.getName())] = [str(x) for x in v]
        elif t == "[D":
            out[str(f.getName())] = [float(x) for x in v]
        elif t in ("java.lang.String", "int", "long", "double", "boolean"):
            out[str(f.getName())] = str(v)
    json.dump(out, open(dst, "w"))


def run_catalog(out, jar, scratch, home):
    K = HK.Child(out)
    res = {}
    for tag, jp in (("old", OLD_JAR), ("new", jar)):
        dst = os.path.join(scratch, "consts_%s.json" % tag)
        p = subprocess.run([sys.executable, os.path.abspath(__file__), "--dump-consts", jp, dst], capture_output=True, text=True)
        K.check(p.returncode == 0 and os.path.isfile(dst), "K constants of %s read: %s" % (os.path.basename(jp), p.stderr[-300:]))
        res[tag] = json.load(open(dst)) if os.path.isfile(dst) else {}
    a, b = res["old"], res["new"]
    diff = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
    K.check(not diff and len(a) > 10, "K every Catalog constant (%d) = 0.2.3's (differ: %s)" % (len(a), diff))
    K.save()


# ------------------------------------------------------------------------------------------------------------------- F
def run_sell(out, jar, scratch, _home):
    from jpype import JClass, JArray, JObject, JLong, JString, JImplements, JOverride, synchronized
    K = HK.Child(out)
    T200 = tmod(os.path.join(HERE, "test_skyybazaar_0.2.0.py"), "tbz0200")
    T20 = T200.T20
    W = T20.boot2(scratch, [jar], "sell")
    W.E.br = JClass(PKG + "HubBar").map()
    E = W.E
    J = lambda n: JClass(PKG + n)
    home = os.path.join(scratch, "home_sell")
    T200.prep(E, J, home)
    C, M, T, Bk, Cfg = J("Catalog"), J("Market"), J("Trader"), J("BzBook"), J("BzCfg")
    ids = [str(p.id) for p in C.all()]
    fx = T200.Fx(E, J)
    A, Bb, _C = T200.mkplayers(W)
    ua, ub = A.pr.getUuid(), Bb.pr.getUuid()
    sa = str(ua)
    fx.purse[sa] = 1000
    iid, _ch = T200.pick(J)
    gone = [i for i in ids if i != iid and not i.startswith("Plant_Seeds_")][-1]
    T20.fake_items(E, [i for i in ids if i != gone])
    MAXQ = int(T.MAXQ)
    LongC, ObjA = JClass("java.lang.Long"), JArray(JObject)
    fn = J("BzSellFn")()

    def args(u, i, q):
        return ObjA([u, None if i is None else JString(i), LongC.valueOf(q)])

    def call(u, i, q):
        r = fn.apply(args(u, i, q))
        K.check(type(r).__name__.endswith("long[]") or str(r.getClass().getName()) == "[J", "F the answer is a long[]: %r" % r)
        return (int(r[0]), int(r[1]))

    def reset():
        M.reset(iid)
        fx.purse[sa] = 1000

    def lines():
        M.flushLog()
        p = os.path.join(home, "trades.log")
        return open(p, encoding="utf8").read().splitlines() if os.path.isfile(p) else []

    def price(i):
        return int(E.br.get("bazaar:sell:" + i))

    # --- 1. a normal sale = the instant sale of the same items (Book empty, so Trader.sell is the market maker)
    reset()
    T20.give(A, iid, 50, 0)
    fx.purse[sa] = 1000
    s0 = int(M.getSold(iid))
    q50, p0 = int(M.quote(iid, 50, False)), price(iid)
    r = T.sell(A.pl, ua, "Alice", iid, 50)
    K.check(bool(r.ok) and int(r.qty) == 50 and int(E.count(A, iid)) == 0, "F the twin: the real instant Sell ran (%s)" % r.msg)
    c_i, f_i, s_i, p_i = fx.purse[sa] - 1000, float(M.factor(iid)), int(M.getSold(iid)) - s0, price(iid)
    K.eq(c_i, q50, "F the instant sale paid quote(50)")
    reset()
    s0 = int(M.getSold(iid))
    K.eq(call(ua, iid, 50), (c_i, 50), "F normal sale: the same coins as the instant sale, all 50 sold")
    K.eq(fx.purse[sa] - 1000, c_i, "F normal sale: credited to the wallet")
    K.eq((float(M.factor(iid)), int(M.getSold(iid)) - s0, price(iid)), (f_i, s_i, p_i), "F normal sale: the same demand factor, sold counter and bazaar:sell price")
    K.check(price(iid) < p0 or c_i == 50 * p0, "F normal sale: the published price moved down (%d -> %d)" % (p0, price(iid)))
    ln = [x for x in lines() if " src=shard" in x]
    K.check(len(ln) == 1 and re.search(r" SELL Alice %s %s 50 %d f=\S+ src=shard$" % (sa, iid, c_i), ln[0]) is not None, "F trades.log: the SELL line with the shard mark: %s" % ln[:2])
    # --- 2. the caller's items: inventory + bags untouched
    reset()
    T20.give(A, iid, 7, 1)
    fx.bags[(sa, iid)] = 9
    K.check(call(ua, iid, 5)[1] == 5, "F sale with items held")
    K.eq((int(E.count(A, iid)), fx.bags[(sa, iid)]), (7, 9), "F the inventory and the bags are not touched")
    # --- 3. big quantity
    reset()
    big = 5000
    qb = int(M.quote(iid, big, False))
    p1 = price(iid)
    K.eq(call(ua, iid, big), (qb, big), "F big quantity: quote(5000)")
    K.check(qb < big * p1 and price(iid) < p1, "F big quantity: the price walks down as it sells (%d coins < %d x %d; now %d)" % (qb, big, p1, price(iid)))
    K.eq(fx.purse[sa] - 1000, qb, "F big quantity: credited")
    # --- 4. over MAXQ
    for ask in (MAXQ, MAXQ + 1, 2 ** 63 - 1):
        reset()
        qm = int(M.quote(iid, MAXQ, False))
        K.eq(call(ua, iid, ask), (qm, MAXQ), "F %d asked sells MAXQ %d and says so" % (ask, MAXQ))
    # --- 5. refused items: no credit, no market move, no line
    reset()
    n0 = len(lines())
    f0, g0 = float(M.factor(iid)), fx.purse[sa]

    def still(what):
        K.eq((float(M.factor(iid)), fx.purse[sa], len(lines())), (f0, g0, n0), "F %s: no credit, no price move, no trades.log line" % what)

    K.eq(call(ua, "No_Such_Item_X", 5), (0, 0), "F unlisted item")
    K.check(C.get(gone) is not None and not bool(C.usable(gone)), "F listed but no such item in the game (%s)" % gone)
    K.eq(call(ua, gone, 5), (0, 0), "F a listed id the game does not know")
    K.eq(call(ua, "Skyy_Sack_Void", 5), (0, 0), "F a Void bag id")
    still("refused ids")

    @JImplements("java.util.function.Function")
    class Veto:
        @JOverride
        def apply(self, o):
            return JString("walled") if str(o.getItemId()) == iid else None
    vm = JClass("java.util.HashMap")()
    vm.put("t", Veto())
    E.br.put("market:veto", vm)
    K.eq(call(ua, iid, 5), (0, 0), "F an item behind the market wall")
    E.br.remove("market:veto")
    still("the market wall")
    # --- 6. sell caps
    Scap = C.SCAP
    capd = [(str(k), float(Scap.get(k))) for k in Scap.keySet() if str(k) in ids and str(k) != gone and float(Scap.get(k)) < float(C.get(str(k)).base)]
    K.check(len(capd) > 0, "F sell-capped products exist (%d)" % len(capd))
    cid, cv = capd[0]
    base = float(C.get(cid).base)
    M.reset(cid)
    qc = int(M.quote(cid, 5, False))
    K.eq(call(ua, cid, 5), (qc, 5), "F a capped item (%s, cap %g under base %g) sells at its capped quote" % (cid, cv, base))
    K.check(qc < 5 * base * (1 - float(M.SPREAD)), "F the cap really lowered the pay (%d)" % qc)
    M.reset(cid)
    M.reset(iid)
    f0, g0, n0 = float(M.factor(iid)), fx.purse[sa], len(lines())
    m0 = int(Cfg.MINSELL)
    oldc = Scap.get(iid)
    Cfg.MINSELL = 0
    Scap.put(iid, JClass("java.lang.Double").valueOf(0.1))
    K.eq(int(M.quote(iid, 1, False)), 0, "F the refusing cap: worth 0 for one")
    K.eq(call(ua, iid, 1), (0, 0), "F a sell cap that leaves it worth 0: nothing sold")
    still("the refusing cap")
    if oldc is None:
        Scap.remove(iid)
    else:
        Scap.put(iid, oldc)
    Cfg.MINSELL = m0
    # --- 7. the coin mod
    saved = dict((k, E.br.get(k)) for k in ("coins:fn:get", "coins:fn:add", "coins:fn:take"))
    E.br.remove("coins:fn:add")
    K.eq(call(ua, iid, 5), (0, 0), "F coin mod absent")
    still("coin mod absent")
    for k, v in saved.items():
        E.br.put(k, v)

    @JImplements("java.util.function.Function")
    class NoAns:
        @JOverride
        def apply(self, o):
            return None

    @JImplements("java.util.function.Function")
    class Boom:
        @JOverride
        def apply(self, o):
            raise JClass("java.lang.RuntimeException")("coin boom")
    E.br.put("coins:fn:add", NoAns())
    K.eq(call(ua, iid, 5), (0, 0), "F coins:fn:add refuses")
    ls = lines()
    K.check(len(ls) == n0 + 1 and " PAY-FAILED " in ls[-1] and ls[-1].endswith("src=shard"), "F PAY-FAILED logged: %s" % ls[-1:])
    E.br.put("coins:fn:add", Boom())
    K.eq(call(ua, iid, 5), (0, 0), "F coins:fn:add throws")
    ls = lines()
    K.check(len(ls) == n0 + 2 and " PAY-ERROR " in ls[-1], "F PAY-ERROR logged: %s" % ls[-1:])
    n0 = len(ls)
    E.br.put("coins:fn:add", saved["coins:fn:add"])
    E.br.put("coins:fn:get", Boom())
    K.eq(call(ua, iid, 5), (0, 0), "F coins:fn:get throws (the bank did not answer)")
    E.br.put("coins:fn:get", saved["coins:fn:get"])
    still("coin failures")
    fx.purse[sa] = 2 ** 63 - 2
    g0 = fx.purse[sa]
    K.eq(call(ua, iid, 5), (0, 0), "F a full purse")
    still("a full purse")
    reset()
    g0 = fx.purse[sa]
    # --- 7b. the add fails but the money arrived (fixer, finding 1): a paid sale, never coins AND the items back

    @JImplements("java.util.function.Function")
    class Landed:
        def __init__(self, extra, ans):
            self.extra, self.ans = extra, ans

        @JOverride
        def apply(self, o):
            fx.purse[sa] += int(o[1]) + self.extra
            if self.ans == "boom":
                raise JClass("java.lang.RuntimeException")("coin boom after the wallet write")
            return None

    @JImplements("java.util.function.Function")
    class OtherCredit:
        @JOverride
        def apply(self, o):
            fx.purse[sa] += int(o[1]) * 2 + 1      # NOT our pay: somebody else's credit, then the add fails
            raise JClass("java.lang.RuntimeException")("coin boom, ours never landed")
    for ans, what in (("boom", "throws after the wallet write"), ("null", "answers null after the wallet write (the real CoinFn's catch)")):
        reset()
        g1, n1, s1 = fx.purse[sa], len(lines()), int(M.getSold(iid))
        q = int(M.quote(iid, 5, False))
        E.br.put("coins:fn:add", Landed(0, ans))
        K.eq(call(ua, iid, 5), (q, 5), "F coins:fn:add %s: reported as sold" % what)
        E.br.put("coins:fn:add", saved["coins:fn:add"])
        ls = lines()
        K.eq(fx.purse[sa] - g1, q, "F coins:fn:add %s: paid once" % what)
        K.check(float(M.factor(iid)) < 1.0 and int(M.getSold(iid)) - s1 == 5, "F coins:fn:add %s: the market moved like a sale" % what)
        K.check(len(ls) == n1 + 1 and " SELL " in ls[-1] and ls[-1].endswith(" src=shard"), "F coins:fn:add %s: a normal SELL line, no PAY-ERROR: %s" % (what, ls[-1:]))
    reset()
    g1, n1 = fx.purse[sa], len(lines())
    q = int(M.quote(iid, 5, False))
    E.br.put("coins:fn:add", OtherCredit())
    K.eq(call(ua, iid, 5), (0, 0), "F the add fails while another credit lands: not mistaken for our pay, the items go back")
    E.br.put("coins:fn:add", saved["coins:fn:add"])
    K.eq(fx.purse[sa] - g1, q * 2 + 1, "F another credit: nothing of ours added")
    K.eq(float(M.factor(iid)), 1.0, "F another credit: no price move")
    K.check(" PAY-ERROR " in lines()[-1], "F another credit: PAY-ERROR logged")
    reset()
    g1 = fx.purse[sa]
    realget = E.br.get("coins:fn:get")
    gets = []

    @JImplements("java.util.function.Function")
    class GetOnceThenBoom:
        @JOverride
        def apply(self, o):
            gets.append(1)
            if len(gets) > 1:
                raise JClass("java.lang.RuntimeException")("bank gone")
            return JClass("java.lang.Long").valueOf(g1)
    E.br.put("coins:fn:get", GetOnceThenBoom())
    E.br.put("coins:fn:add", Boom())
    K.eq(call(ua, iid, 5), (0, 0), "F the add fails and the balance cannot be re-read: nothing sold, as before")
    K.check(len(gets) == 2, "F the balance really was re-read after the failed add (%d reads)" % len(gets))
    E.br.put("coins:fn:add", saved["coins:fn:add"])
    E.br.put("coins:fn:get", realget)
    reset()
    f0, g0, n0 = float(M.factor(iid)), fx.purse[sa], len(lines())
    # --- 8. the player
    UU = JClass("java.util.UUID")
    K.eq(call(UU.fromString(U_NOBODY), iid, 5), (0, 0), "F offline / unknown player")
    E.br.put("profile:busy:" + sa, JString("x"))
    K.eq(call(ua, iid, 5), (0, 0), "F profile busy")
    E.br.remove("profile:busy:" + sa)
    still("nobody paid")
    # --- 9. bad arguments never throw
    bad = [None, JString("x"), ObjA([ua, JString(iid)]), ObjA([JString(sa), JString(iid), LongC.valueOf(5)]), ObjA([ua, None, LongC.valueOf(5)]),
           ObjA([ua, JString(iid), JString("5")]), args(ua, iid, 0), args(ua, iid, -5), args(ua, "", 5)]
    res = []
    for b in bad:
        try:
            r = fn.apply(b)
            res.append((int(r[0]), int(r[1])))
        except Exception as ex:
            res.append(("THROW", str(ex)[:80]))
    K.check(all(x == (0, 0) for x in res), "F bad arguments answer 0, 0: %s" % res)
    still("bad arguments")
    r = fn.apply(ObjA([ua, JString(iid), JClass("java.lang.Integer").valueOf(3)]))
    K.eq(int(r[1]), 3, "F any Number works as qty")
    # --- 10. failure AFTER the credit: no throw, coins kept, the right answer
    reset()
    g0 = fx.purse[sa]
    n0 = len(lines())
    q = int(M.quote(iid, 10, False))
    Bk.CRASH_AT = 42
    K.eq(call(ua, iid, 10), (q, 10), "F the log step throws after the credit: no throw, the right answer")
    K.check(int(Bk.CRASH_AT) == -1, "F the log failure really fired")
    K.eq((fx.purse[sa] - g0, len(lines())), (q, n0), "F the log step threw: coins kept, no line")
    K.check(float(M.factor(iid)) < 1.0, "F the log step threw: the price still moved")
    reset()
    g0 = fx.purse[sa]
    n0 = len(lines())
    q = int(M.quote(iid, 10, False))
    Bk.CRASH_AT = 41
    K.eq(call(ua, iid, 10), (q, 10), "F the price move throws after the credit: no throw, the right answer")
    K.eq((fx.purse[sa] - g0, len(lines()), float(M.factor(iid))), (q, n0 + 1, 1.0), "F the price move threw: coins kept, line written, price unmoved")
    reset()
    g0 = fx.purse[sa]
    logf = M.LOGFILE
    blocker = os.path.join(scratch, "not_a_folder")
    open(blocker, "w").close()
    M.LOGFILE = JClass("java.nio.file.Paths").get(blocker).resolve("trades.log")
    q = int(M.quote(iid, 10, False))
    K.eq(call(ua, iid, 10), (q, 10), "F the disk cannot be written: the sale still answers right")
    try:
        M.flushLog()
        ok = True
    except Exception as ex:
        ok = str(ex)
    K.check(ok is True, "F the failing disk write does not throw (%s)" % ok)
    K.eq(fx.purse[sa] - g0, q, "F the disk failure keeps the coins")
    M.LOGFILE = logf
    # --- 11. concurrent calls
    reset()
    g0 = fx.purse[sa]
    n0 = len(lines())
    s0 = int(M.getSold(iid))
    got, errs = [], []
    lock = threading.Lock()

    def worker(u):
        try:
            for _i in range(25):
                r_ = fn.apply(args(u, iid, 7))
                with lock:
                    got.append((int(r_[0]), int(r_[1])))
        except Exception as ex:
            errs.append(str(ex))
    fx.purse[str(ub)] = 1000
    ts = [threading.Thread(target=worker, args=(ua if i % 2 == 0 else ub,)) for i in range(8)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    total = sum(c for c, _n in got)
    K.check(not errs and len(got) == 200 and all(n == 7 for _c, n in got), "F 8 threads x 25 calls: every call sold its 7 (%s)" % errs[:2])
    K.eq(fx.purse[sa] - g0 + fx.purse[str(ub)] - 1000, total, "F concurrent: the wallets rose by exactly what was reported")
    K.eq(int(M.getSold(iid)) - s0, 1400, "F concurrent: the sold counter = every unit")
    K.eq(len(lines()) - n0, 200, "F concurrent: one trades.log line per sale")
    fc = float(M.factor(iid))
    reset()
    serial = sum(call(ua, iid, 7)[0] for _i in range(200))
    K.eq(serial, total, "F concurrent: the same total coins as the same 200 sales one after another (nothing raced)")
    K.check(abs(float(M.factor(iid)) - fc) < 1e-9, "F concurrent: the same final factor as the serial run")
    # the lock: while another thread holds Market.class, a sale waits; then it finishes
    reset()
    g0 = fx.purse[sa]
    done = []

    def later():
        done.append(call(ua, iid, 5))
    th = threading.Thread(target=later)
    with synchronized(M.class_):
        th.start()
        time.sleep(0.5)
        K.check(not done and fx.purse[sa] == g0, "F the sale waits while the Market lock is held")
    th.join(20)
    K.check(len(done) == 1 and done[0][1] == 5 and fx.purse[sa] > g0, "F the sale finishes when the lock is free (%s)" % done)
    # --- 12. the bridge key: shutdown removes it (the real method on a plugin object made without its constructor)
    E.br.put("bazaar:fn:sell", fn)
    Field = JClass("java.lang.Class").forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
    Field.setAccessible(True)
    Pl = J("SkyyBazaarPlugin")
    plug = Field.get(None).allocateInstance(Pl.class_)
    sd = Pl.class_.getDeclaredMethod("shutdown", None)
    sd.setAccessible(True)
    # (fixer, finding 2) a Shards sale already holding the Function, waiting on the Market lock, while the REAL shutdown runs: it pays nothing
    reset()
    g0, n0 = fx.purse[sa], len(lines())
    K.check(not bool(T.CLOSED), "F open before the shutdown")
    late, whys = [], []

    def late_sale():
        late.append(call(ua, iid, 5))

    def stopper():
        try:
            sd.invoke(plug, None)
        except Exception as ex:
            whys.append(str(ex)[:200])
    t1, t2 = threading.Thread(target=late_sale), threading.Thread(target=stopper)
    with synchronized(M.class_):
        t1.start()
        time.sleep(0.5)
        K.check(not late, "F the late sale is waiting on the Market lock")
        t2.start()
        for _i in range(100):
            if bool(T.CLOSED):
                break
            time.sleep(0.05)
        K.check(bool(T.CLOSED), "F the real shutdown() closed the sale while the lock was held (before its last flush can run)")
    t1.join(20)
    t2.join(20)
    K.eq(late, [(0, 0)], "F a sale waiting through the shutdown sells nothing")
    K.eq((fx.purse[sa], float(M.factor(iid))), (g0, 1.0), "F a sale waiting through the shutdown: no coins, no price move")
    K.check(not [x for x in lines()[n0:] if " SELL " in x], "F a sale waiting through the shutdown: no SELL line")
    K.check(E.br.get("bazaar:fn:sell") is None, "F the real shutdown() removes bazaar:fn:sell (%s)" % whys)
    T.CLOSED = False
    K.eq(call(ua, iid, 5)[1], 5, "F open again after the flag clears (what setup does on a restart)")
    K.notes.append("F normal 50 x %s = %d coins, 5000 = %d coins, MAXQ %d; capped %s" % (iid, c_i, qb, MAXQ, cid))
    K.save()


# ------------------------------------------------------------------------------------------------------------------- D
def _start(jar_path, home, dst):
    from jpype import JClass
    HK.jvm([jar_path, B.SERVER_JAR], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    tmod(os.path.join(HERE, "test_skyybazaar_0.2.1.py"), "tbz021").bz_prep(lambda n: JClass(PKG + n), home)
    json.dump(dict((k, v) for k, v in HK.tree_hash(home).items()), open(dst, "w"))


def run_live(out, jar, scratch, home):
    K = HK.Child(out)
    other = home.rstrip("\\/") + "_old"
    shutil.copytree(home, other)
    hs = {}
    for tag, jp, h in (("old", OLD_JAR, other), ("new1", jar, home), ("new2", jar, home)):
        dst = os.path.join(scratch, "live_%s.json" % tag)
        p = subprocess.run([sys.executable, os.path.abspath(__file__), "--start", jp, h, dst], capture_output=True, text=True)
        K.check(p.returncode == 0, "D %s start ran: %s" % (tag, p.stderr[-300:]))
        hs[tag] = json.load(open(dst)) if os.path.isfile(dst) else {}
    strip = lambda t: dict((k, v) for k, v in t.items() if not k.startswith("config-history") and k != "trades.log")
    da = sorted(k for k in set(strip(hs["old"])) | set(strip(hs["new1"])) if strip(hs["old"]).get(k) != strip(hs["new1"]).get(k))
    K.check(not da, "D the 0.2.4 start = the 0.2.3 start on the live data (files that differ: %s)" % da)
    K.check(hs["new1"] == hs["new2"], "D a second 0.2.4 start writes nothing (%s)" % sorted(k for k in set(hs["new1"]) | set(hs["new2"]) if hs["new1"].get(k) != hs["new2"].get(k))[:5])
    K.save()


if __name__ == "__main__":
    if "--dump-consts" in sys.argv:
        k = sys.argv.index("--dump-consts")
        _dump_consts(sys.argv[k + 1], sys.argv[k + 2])
        sys.exit(0)
    if "--start" in sys.argv:
        k = sys.argv.index("--start")
        _start(sys.argv[k + 1], sys.argv[k + 2], sys.argv[k + 3])
        sys.exit(0)
    HK.run(name="SkyyBazaar", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("catalog", run_catalog), ("sell", run_sell), ("live", run_live)],
           live=(LIVE, "Skyy_SkyyBazaar"), script=__file__)
