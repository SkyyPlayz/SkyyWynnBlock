"""Harness for SkyyAuctions 0.1.4 (owed-claims index + active counter, lock-free bridge; tools/auctions_0_1_4_patch.py).
Build first: python tools/auctions_0_1_4_patch.py && python SkyyAuctions/build_skyyauctions_0.1.4.py

    python SkyyAuctions/test_skyyauctions_0.1.4.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.1.3 -> 0.1.4: exactly the listed members differ (+ AhIdx)
  X  exec     EVERY NEW CODE PATH on generated listings (420 records: every state, every claim mix, read-only v2 / AUCTION / unknown
              state, seller = buyer key, other-profile keys, ended-but-not-expired, closed): AhUtil.bridge (cached, same map),
              AhIdx.keysOf / actOf / bump / put / clear / owed / countActive (fast path + scan + the stale-entry case),
              AhStore.livePut / liveRemove through load(), swap0 (commit, commitForced), list's LIVE.put path (via restoreFromLog's
              commitForced), regrant0, buy0, cancel0, claimCoins0 (real SkyyCoins 0.1.6 CoinFn on the bridge), expireDue0, adminRemove0,
              restoreFromLog0. After EVERY step: AhIdx.owed(key) = owedFor(key)[0] for every key, countActive(t) = active(t).size()
              for 6 times t around the ends, publishClaims puts the same number 0.1.3's scan gives.
              The same 600-step random session on 0.1.3 and 0.1.4 (each in its own loader on its own copy of the folder): identical
              results, identical listing files after every step, identical bridge numbers (auction:count, auction:claims:<uuid>).
  F  fix round C (inside X): Coins.take / Coins.add on the real SkyyCoins 0.1.6 ledger write the purse file AT ONCE after a success
              (coins:fn:flush), a refused take writes nothing, no flush function (SkyyCoins 0.1.5) = no error
  D  live     start twice on a scratch COPY of the live Skyy_SkyyAuctions: no file changes; index = scan
  AA engine-access audit
Scratch: tools/dev/scratch/perfecon/auctions (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, random, shutil, copy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.1.4"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyAuctions-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyAuctions-0.1.3.jar")
COINS_JAR = os.path.join(ROOT, "SkyyCoins", "SkyyCoins-0.1.6.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "perfecon", "auctions")))
PKG = "com.skyy.auctions."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyAuctions")
EXPECT = {
    "AhUtil": ["+f BRIDGE", "~m bridge"],
    "AhStore": ["+m livePut", "+m liveRemove", "~m swap0", "~m countActive", "~m load", "~m list0", "~m regrant0", "~m publishClaims"],
    "SkyyAuctionsPlugin": ["~m setup"],
    "AhCmds": ["~m status"],          # status: the "SkyyAuctions 0.1.4 - ..." version text
    "Coins": ["+m flush", "~m take", "~m add"],   # fix round C: coins:fn:flush after a successful take / add
}
ADDED = ["AhIdx"]
STATES = ["ACTIVE", "SOLD", "EXPIRED", "CANCELLED", "REMOVED"]
CL = ["NONE", "OWED", "CLAIMED"]


def uu(i):
    return "%08d-0000-4000-8000-%012d" % (i, i)


def template():
    for base, _d, fs in os.walk(os.path.join(LIVE_DIR, "archive")):
        for f in sorted(fs):
            if f.endswith(".json"):
                return json.load(open(os.path.join(base, f), encoding="utf8"))
    return {"v": {"$numberInt": "1"}, "type": "BIN", "item": {"id": "Weapon_Longsword_Copper", "qty": {"$numberInt": "1"}}}


def L(n):
    return {"$numberLong": str(int(n))}


def gen_records(n, now, seed):
    rnd = random.Random(seed)
    t = template()
    out = []
    for i in range(1, n + 1):
        r = copy.deepcopy(t)
        r["id"] = str(i)
        r["v"] = {"$numberInt": "2"} if rnd.random() < 0.03 else {"$numberInt": "1"}
        r["type"] = "AUCTION" if rnd.random() < 0.03 else "BIN"
        st = rnd.choice(STATES + ["ACTIVE", "ACTIVE", "SOLD"]) if rnd.random() > 0.02 else "WEIRD"
        r["state"] = st
        r["closed"] = False
        r["rev"] = L(rnd.randint(1, 6))
        s = rnd.randint(1, 12)
        sk = uu(s) + ("-p2" if rnd.random() < 0.1 else "")
        r["seller"] = {"uuid": uu(s), "key": sk, "name": "S%d" % s, "profile": "P"}
        if st == "SOLD" or (st not in ("ACTIVE",) and rnd.random() < 0.3):
            b = rnd.randint(1, 12)
            bk = sk if rnd.random() < 0.05 else uu(b) + ("-p3" if rnd.random() < 0.1 else "")
            r["buyer"] = {"uuid": uu(b), "key": bk, "name": "B%d" % b, "profile": "P", "at": L(now - 1000)}
            r["sale"] = {"gross": L(100 + i), "tax": L(1), "net": L(99 + i)}
        else:
            r["buyer"] = None
            r["sale"] = None
        sc = rnd.choice(CL) if st != "ACTIVE" else "NONE"
        si = rnd.choice(CL) if st != "ACTIVE" else "NONE"
        bi = rnd.choice(CL) if r["buyer"] else "NONE"
        r["claims"] = {"sellerCoins": sc, "sellerItem": si, "buyerItem": bi, "sellerItemQty": L(1), "buyerItemQty": L(1)}
        r["price"] = L(100 + i)
        r["endsAt"] = L(now + rnd.choice([-60000, -5000, 5000, 60000, 3600000, 86400000]) + rnd.randint(0, 999))
        r["graceUntil"] = L(now - 100000)
        r["createdAt"] = L(now - 200000)
        r["fee"] = {"listing": L(5), "duration": L(0), "refunded": False}
        r["noticed"] = {"seller": False}
        r["removed"] = None
        r["regrants"] = []
        r["closedAt"] = L(0)
        r["name"] = "Item %d" % i
        r["search"] = "item %d" % i
        r["category"] = "WEAPONS"
        out.append(r)
    return out


class Ah(object):
    def __init__(self, jar, home):
        from jpype import JClass
        self.L = HK_loader(jar)
        g = lambda n: JClass(PKG + n, loader=self.L)
        self.Cfg, self.Lg, self.S, self.U, self.Rec = g("AhCfg"), g("AhLog"), g("AhStore"), g("AhUtil"), g("AhRec")
        self.home = home
        P = JClass("java.nio.file.Paths")
        d = P.get(home)
        self.Cfg.DIR = d
        self.Cfg.FILE = d.resolve("config.properties")
        self.Cfg.BLOCKED = d.resolveSibling("Skyy_Market").resolve("blocked.txt")
        self.Lg.FILE = d.resolve("auctions.log")
        self.S.DIR = d
        self.S.LDIR = d.resolve("listings")
        self.S.ADIR = d.resolve("archive")
        self.S.BADDIR = d.resolve("listings").resolve("bad")
        self.S.STATE = d.resolve("state.properties")

    def start(self):
        self.Cfg.migrate()
        self.Cfg.load()
        self.Cfg.loadBlocked()
        self.Cfg.applyBuiltin()
        n = int(self.S.load())
        self.S.restoreFromLog()
        self.Lg.scanStarts()
        return n


def HK_loader(jar):
    from jpype import JClass, JArray
    URL = JClass("java.net.URL")
    arr = JArray(URL)(1)
    arr[0] = JClass("java.io.File")(jar).toURI().toURL()
    return JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getSystemClassLoader())


def coins_on_bridge(scratch):
    """the REAL SkyyCoins 0.1.6 ledger (own loader, scratch balances) as coins:fn:get / add / take"""
    from jpype import JClass
    from jpype import JClass as J
    Lc = HK_loader(COINS_JAR)
    CS = J("com.skyy.coins.CoinStore", loader=Lc)
    P = J("java.nio.file.Paths")
    CS.DIR = P.get(os.path.join(scratch, "coins", "balances"))
    CS.JOURNAL = P.get(os.path.join(scratch, "coins", "balances-journal.properties"))
    Fn = J("com.skyy.coins.CoinFn", loader=Lc)
    br = CS.bridge()
    for m in ("get", "add", "take", "flush"):
        br.put("coins:fn:" + m, Fn(m))
    return CS


def keys_of(S):
    ks = {""}
    it = S.LIVE.values().iterator()
    while it.hasNext():
        r = it.next()
        for side in ("seller", "buyer"):
            try:
                v = r.get(side)
                if v is not None and v.isDocument():
                    ks.add(str(v.asDocument().getString("key").getValue()))
            except Exception:
                pass
    return ks


def check_index(K, a, where, now):
    S = a.S
    Idx = HKJ(PKG + "AhIdx", a.L)
    bad = []
    for k in sorted(keys_of(S)):
        want = int(S.owedFor(k)[0])
        got = int(Idx.owed(k))
        if want != got:
            bad.append((k, want, got))
    K.check(not bad, "%s: AhIdx.owed = owedFor for every key (%s)" % (where, bad[:3]))
    ends = []
    it = S.LIVE.values().iterator()
    while it.hasNext():
        r = it.next()
        try:
            ends.append(int(a.Rec.lng(r, "endsAt", 0)))
        except Exception:
            pass
    ts = sorted(set([now, now - 70000, now + 6000, now + 4000000] + random.Random(len(ends)).sample(ends, min(2, len(ends)))))
    badc = []
    for t in ts + list(reversed(ts)):
        w, g = int(S.active(t).size()), int(S.countActive(t))
        if w != g:
            badc.append((t - now, w, g))
    K.check(not badc, "%s: countActive = active().size() at %d times (%s)" % (where, len(ts) * 2, badc[:3]))
    K.eq(int(Idx.ACTIVE.get()), int(Idx.ACT.size()), "%s: ACTIVE = the counted ids" % where)


def HKJ(name, loader):
    from jpype import JClass
    return JClass(name, loader=loader)


def write_records(home, recs):
    ld = os.path.join(home, "listings")
    os.makedirs(ld, exist_ok=True)
    for r in recs:
        json.dump(r, open(os.path.join(ld, r["id"] + ".json"), "w", encoding="utf8"), indent=1)
    open(os.path.join(home, "state.properties"), "w").write("nextId=%d\n" % (len(recs) + 1))


def strip(x):
    if isinstance(x, dict):
        return {k: strip(v) for k, v in x.items() if k not in ("at", "closedAt", "createdAt")}
    if isinstance(x, list):
        return [strip(v) for v in x]
    return x


def listings(home):
    out = {}
    ld = os.path.join(home, "listings")
    for f in sorted(os.listdir(ld)) if os.path.isdir(ld) else []:
        p = os.path.join(ld, f)
        if os.path.isfile(p):
            d = json.load(open(p, encoding="utf8"))
            out[f] = d
    return out


def run_exec(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    Sys, UUID = JClass("java.lang.System"), JClass("java.util.UUID")
    now = int(Sys.currentTimeMillis())
    recs = gen_records(420, now, 414)
    h3, h4 = os.path.join(scratch, "x3", "Skyy_SkyyAuctions"), os.path.join(scratch, "x4", "Skyy_SkyyAuctions")
    for h in (h3, h4):
        write_records(h, recs)
    CS = coins_on_bridge(scratch)
    for i in range(1, 13):
        CS.set(UUID.fromString(uu(i)), 10 ** 7)
    a3, a4 = Ah(OLD_JAR, h3), Ah(jar, h4)
    br = Sys.getProperties().get("skyy.bridge")
    K.eq(Sys.identityHashCode(a4.U.bridge()), Sys.identityHashCode(br), "X AhUtil.bridge = the System map")
    K.eq(Sys.identityHashCode(a4.U.BRIDGE), Sys.identityHashCode(br), "X AhUtil.BRIDGE caches it")
    n3, n4 = a3.start(), a4.start()
    K.eq(n4, n3, "X both load the same open records (%d)" % n3)
    Idx = HKJ(PKG + "AhIdx", a4.L)
    check_index(K, a4, "X after load", now)
    K.check(int(Idx.OWED.size()) > 5 and int(Idx.ACTIVE.get()) > 20, "X the generated set has owed claims (%d keys) and active listings (%d)" % (int(Idx.OWED.size()), int(Idx.ACTIVE.get())))
    # the stale case: listings that ended but were not expired yet are only counted by a scan (MINEND = MIN_VALUE)
    s0 = int(Idx.SCANS)
    a4.S.countActive(now)
    a4.S.countActive(now)
    K.check(int(Idx.SCANS) >= s0 + 2 and int(Idx.MINEND) == -2 ** 63, "X with ended-but-not-expired listings every count scans")
    a3.S.expireDue(now)
    a4.S.expireDue(now)
    check_index(K, a4, "X after expireDue", now)
    # the fast path vs the scan
    s0 = int(Idx.SCANS)
    t_far = now + 100 * 86400000
    a4.S.countActive(now)
    s1 = int(Idx.SCANS)
    a4.S.countActive(now)
    K.eq(int(Idx.SCANS), s1, "X countActive: the second call at the same time uses the fast path (no scan)")
    K.eq(int(a4.S.countActive(t_far)), 0, "X countActive far in the future = 0")
    K.check(s1 >= s0, "X scans counted")
    # publishClaims = the scan
    for i in range(1, 13):
        u = UUID.fromString(uu(i))
        a4.S.publishClaims(u)
        K.eq(int(br.get("auction:claims:" + str(u))), int(a4.S.owedFor(uu(i))[0]), "X publishClaims(%s) = owedFor" % i)
    a4.S.publishCount()
    K.eq(int(br.get("auction:count")), int(a4.S.active(int(Sys.currentTimeMillis())).size()), "X publishCount = active().size()")
    # ---- the same random session on 0.1.3 and 0.1.4
    rnd = random.Random(1304)
    ids = [r["id"] for r in recs]
    admin = UUID.fromString(uu(999))
    stats = {}

    def res_t(r):
        if r is None:
            return None
        try:
            return (bool(r.ok), str(r.msg))
        except Exception:
            return str(r)

    def on(a, fn):
        try:
            return fn(a)
        except Exception as e:
            return "EXC " + str(e)[:80]
    for step in range(600):
        op = rnd.choice(["buy", "buy", "cancel", "claimCoins", "claimCoins", "expire", "remove", "regrant", "restore"])
        i = rnd.choice(ids)
        who = rnd.randint(1, 12)
        u = UUID.fromString(uu(who))
        if op == "buy":
            def f(a):
                r = a.S.get(i)
                price = int(a.Rec.lng(r, "price", 0)) if r is not None else 0
                return res_t(a.S.buy(None, u, uu(who), "B", "P", i, price))
        elif op == "cancel":
            def f(a):
                r = a.S.get(i)
                sk = str(a.Rec.subStr(r, "seller", "key", "")) if r is not None else uu(who)
                su = UUID.fromString(sk[:36]) if len(sk) >= 36 else u
                return res_t(a.S.cancel(None, su, sk, i))
        elif op == "claimCoins":
            def f(a):
                r = a.S.get(i)
                sk = str(a.Rec.subStr(r, "seller", "key", "")) if r is not None else uu(who)
                su = UUID.fromString(sk[:36]) if len(sk) >= 36 else u
                return res_t(a.S.claimCoins(su, sk, i))
        elif op == "expire":
            def f(a):
                return int(a.S.expireDue(int(Sys.currentTimeMillis()) + rnd_shift).size())
            rnd_shift = rnd.choice([0, 10000, 70000, 4000000])
        elif op == "remove":
            def f(a):
                return res_t(a.S.adminRemove("t", i, "test"))
        elif op == "regrant":
            side = rnd.choice(["seller", "buyer"])

            def f(a):
                a.S.regrantPreview(admin, i, side)
                return res_t(a.S.regrant(admin, "t", i, side))
        else:
            def f(a):
                return int(a.S.restoreFromLog())
        r3, r4 = on(a3, f), on(a4, f)
        stats[op] = stats.get(op, 0) + 1
        if r3 != r4:
            K.check(False, "X step %d %s #%s: 0.1.3 %r vs 0.1.4 %r" % (step, op, i, r3, r4))
        if step % 25 == 0 or op in ("expire", "regrant", "restore"):
            check_index(K, a4, "X step %d (%s)" % (step, op), int(Sys.currentTimeMillis()))
            l3, l4 = listings(h3), listings(h4)
            K.eq(sorted(l4), sorted(l3), "X step %d: the same listing files" % step)
            difk = [k for k in set(l3) & set(l4) if strip(l3[k]) != strip(l4[k])]
            K.eq(difk[:3], [], "X step %d: the same listing contents (time stamps aside)" % step)
            t = int(Sys.currentTimeMillis())
            K.eq(int(a4.S.countActive(t)), int(a3.S.countActive(t)), "X step %d: auction:count = 0.1.3's" % step)
            for w in range(1, 13):
                K.eq(int(a4.S.owedFor(uu(w))[0]), int(a3.S.owedFor(uu(w))[0]), "X step %d: claims of %d = 0.1.3's" % (step, w))
    check_index(K, a4, "X end", int(Sys.currentTimeMillis()))
    K.notes.append("X: 600 steps %s; %d open records left, %d keys owed" % (stats, int(a4.S.LIVE.size()), int(Idx.OWED.size())))
    # restoreFromLog -> commitForced -> livePut: a WRITE-FAILED copy newer than the file
    lg = os.path.join(h4, "auctions.log")
    live_ids = []
    it = a4.S.LIVE.keySet().iterator()
    while it.hasNext():
        live_ids.append(str(it.next()))
    if live_ids:
        x = sorted(live_ids, key=int)[0]
        d = listings(h4)[x + ".json"]
        d["rev"] = L(int(d["rev"]["$numberLong"]) + 5 if isinstance(d["rev"], dict) else 99)
        d["claims"]["sellerItem"] = "OWED"
        if d["state"] == "ACTIVE":
            d["state"] = "EXPIRED"
        open(lg, "a", encoding="utf8").write("2026-10-13T00:00:00Z WRITE-FAILED #%s rev=1 doc=%s\n" % (x, json.dumps(d, separators=(",", ":"))))
        n = int(a4.S.restoreFromLog())
        K.check(n >= 1, "X restoreFromLog restored the newer copy (%d)" % n)
        check_index(K, a4, "X after restoreFromLog", int(Sys.currentTimeMillis()))
    # clear() on load
    a4.S.load()
    check_index(K, a4, "X after a reload", int(Sys.currentTimeMillis()))
    # ---- F (fix round C): the purse change is on disk right after a successful Coins.take / Coins.add
    from jpype import JClass as JC
    Co = JC(PKG + "Coins", loader=a4.L)
    fu = JC("java.util.UUID").fromString(uu(77))
    CS.set(fu, 1000)
    CS.flushNow()
    pf = os.path.join(scratch, "coins", "balances", uu(77) + ".properties")

    def onfile():
        return int([l for l in open(pf).read().splitlines() if l.startswith("balance=")][0].split("=")[1])
    K.eq(int(Co.take(fu, 300)), 1, "F: Coins.take")
    K.eq(onfile(), 700, "F: the purse file holds the take right after it (coins:fn:flush)")
    K.eq(int(Co.add(fu, 50)), 1, "F: Coins.add")
    K.eq(onfile(), 750, "F: ... and the add")
    w0 = int(CS.WRITES)
    K.eq(int(Co.take(fu, 10 ** 9)), 0, "F: a refused take")
    K.eq((int(CS.WRITES), onfile()), (w0, 750), "F: a refused take writes nothing")
    fl = CS.bridge().remove("coins:fn:flush")
    K.eq(int(Co.take(fu, 1)), 1, "F: no coins:fn:flush (SkyyCoins 0.1.5) - the take still works")
    CS.bridge().put("coins:fn:flush", fl)
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    Sys = JClass("java.lang.System")
    mk = os.path.join(os.path.dirname(LIVE_DIR), "Skyy_Market")
    if os.path.isdir(mk) and not os.path.isdir(os.path.join(os.path.dirname(home), "Skyy_Market")):
        shutil.copytree(mk, os.path.join(os.path.dirname(home), "Skyy_Market"))
    h0 = HK.tree_hash(home)
    for start in (1, 2):
        a = Ah(jar, home)
        n = a.start()
        K.eq(HK.tree_hash(home), h0, "D%d: no file changed" % start)
        check_index(K, a, "D%d" % start, int(Sys.currentTimeMillis()))
        K.notes.append("D%d: %d open records" % (start, n))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyAuctions", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("exec", run_exec), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyAuctions"))
