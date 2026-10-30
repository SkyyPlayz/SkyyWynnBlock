"""Harness for SkyyAuctions 0.1.16 (PRICE TOOLTIPS R1: the in-memory sales index AhSales, bridge auction:fn:priceTable + auction:prices:version;
tools/auctions_0_1_16_patch.py; research/Price-Tooltips-Spec.md 5 R1 + its harness checks).
Build first: python tools/auctions_0_1_16_patch.py && python SkyyAuctions/build_skyyauctions_0.1.16.py

    python SkyyAuctions/test_skyyauctions_0.1.16.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, -Xverify:all, tools/harness_kit.py):
  A   verify   every class loads + initialises
  C   compare  the PINNED 0.1.15 jar -> 0.1.16: + AhSales, AhPriceFn; AhStore livePut / liveRemove / buy0, AhTick.run, AhCmds.status, the plugin
               setup only (+ AhItem ttMap / <clinit>: the build-time tools/tier_tags.py bake holds the rows added since the 0.1.15 build - sort only)
  X   exec     WINDOWS (a scratch AH folder at a fixed now = 2026-11-02 00:00 UTC, so the 2026-10 + 2026-11 archive folders are both read):
               median 1 d / 3 d = the Python reference (even count = the middle two rounded half up), one 100x outlier does not move it,
               the 24 h / 72 h cut-off to the millisecond, < 3 sales = -1 (n still given), apply(Integer 1) shows it, gear rarity rows
               ("<id>|rare"), blocked ids (Magic Bag, gathering pickaxe) and a newer-schema record give no row, an open SOLD listing and an
               archived copy of the same id count ONCE, the 2026-09 folder is never read, a file last written 5 days ago is skipped,
               lowest BIN = AhStore.lowestBin for every id (+ per rarity), an expired / read-only listing is not seen; AGE: tick at
               now + 24 h moves sales out of the 1 d window, bumps the version, NEXT_AGE = the reference
               LIVE (real time, the REAL AhStore.buy path, a stand-in coin ledger + gear:fn:rarity on the bridge): AhTick.run does the start
               rebuild once (BUILT), a sale added while no rebuild ran is carried over by merge; buys bump auction:prices:version and add
               the sale (each = ceil(price / qty)); a coin claim does NOT bump it; expire / admin remove do; AhPriceFn apply(null / 1 /
               junk); REBUILD EQUALS LIVE: the folder copied after the buys, a fresh loader rebuilt from the copy gives the same table
               COST: 3,000 listings over 400 ids + 6,000 archived sales: the rebuild once, then the table per call (first + average of 20)
               STATIC: no Metadata write in AhSales / AhPriceFn, no UpdateTranslations in the jar, the sale add sits after swap0 in buy0
  D   live     a scratch COPY of the live NewBetaTest Skyy_SkyyAuctions started TWICE (load + rebuild + table): no file changes
  AA  engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, time, shutil, zipfile, calendar, random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.1.16"
PKG = "com.skyy.auctions."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyAuctions-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyAuctions-0.1.15.jar")   # the PINNED 0.1.15 jar (copied from the main checkout)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "tip1", "ah")))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyAuctions")
EXPECT = {"AhStore": ["~m buy0", "~m liveRemove", "~m livePut"], "AhTick": ["~m run"], "AhCmds": ["~m status"], "SkyyAuctionsPlugin": ["~m setup"],
          "AhItem": ["~m ttMap"],            # the build-time tools/tier_tags.py bake (rows added since the 0.1.15 build; sort only)
          "CfgFn": ["~m opExport"], "CfgRows": ["~m header"]}   # the config kit's version text
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = ["AhSales", "AhSalesBuild", "AhPriceFn"]
WIN1, WIN3 = 86400000, 259200000
NOW0 = calendar.timegm((2026, 11, 2, 0, 0, 0)) * 1000


def L(n):
    return {"$numberLong": str(int(n))}


def uu(i):
    return "%08d-0000-4000-8000-%012d" % (i, i)


SAM, BOB, ZED = uu(77), uu(3), uu(5)


def mk(rid, iid, qty, price, state="ACTIVE", now=0, ends=3600000, at=None, seller=SAM, buyer=BOB, rar=None, closed=False, v=1, claims=None):
    r = {"v": {"$numberInt": str(v)}, "id": str(rid), "type": "BIN", "state": state, "closed": closed, "rev": L(3),
         "seller": {"uuid": seller, "key": seller, "name": "Sam", "profile": "P"},
         "buyer": None, "sale": None,
         "item": {"id": iid, "qty": L(qty), "quality": {"$numberInt": "0"}},
         "price": L(price), "endsAt": L(now + ends), "graceUntil": L(0), "createdAt": L(now - 200000),
         "fee": {"listing": L(5), "duration": L(0), "refunded": False}, "noticed": {"seller": False}, "removed": None, "regrants": [],
         "closedAt": L(0), "name": iid.replace("_", " "), "search": iid.lower(), "category": "MISC"}
    if rar:
        r["item"]["meta"] = {"R": rar}
    c = {"sellerCoins": "NONE", "sellerItem": "NONE", "buyerItem": "NONE", "sellerItemQty": L(qty), "buyerItemQty": L(qty)}
    if state == "SOLD":
        r["buyer"] = {"uuid": buyer, "key": buyer, "name": "Bob", "profile": "P", "at": L(at)}
        r["sale"] = {"gross": L(price), "tax": L(0), "net": L(price)}
        if closed:
            c.update({"sellerCoins": "CLAIMED", "buyerItem": "CLAIMED"})
            r["closedAt"] = L(at + 1000)
        else:
            c.update({"sellerCoins": "OWED", "buyerItem": "OWED"})
    c.update(claims or {})
    r["claims"] = c
    return r


def month(ms):
    return time.strftime("%Y-%m", time.gmtime(ms / 1000.0))


def write(home, rec, sub="listings", name=None):
    d = os.path.join(home, *sub.split("/"))
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name or (rec["id"] + ".json"))
    json.dump(rec, open(p, "w", encoding="utf8"))
    return p


def ceil_div(a, b):
    return -(-a // b)


def med(xs):
    xs = sorted(xs)
    n = len(xs)
    if n == 0:
        return -1
    if n % 2:
        return xs[n // 2]
    a, b = xs[n // 2 - 1], xs[n // 2]
    return (a + b + 1) // 2


def ref_row(sales, now, k=3):
    """sales: [(each, at)] -> (med1, n1, med3, n3) the Python reference of AhSales.salesRows"""
    s3 = [e for e, a in sales if now - a < WIN3]
    s1 = [e for e, a in sales if now - a < WIN1]
    return (med(s1) if len(s1) >= k else -1, len(s1), med(s3) if len(s3) >= k else -1, len(s3))


def parse(t):
    out = {}
    for ln in str(t).split("\n"):
        if not ln:
            continue
        p = ln.split("\t")
        assert len(p) == 6, ln
        out[p[0]] = tuple(int(x) for x in p[1:])
    return out


def loader(jar):
    from jpype import JClass, JArray
    arr = JArray(JClass("java.net.URL"))(1)
    arr[0] = JClass("java.io.File")(jar).toURI().toURL()
    return JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getSystemClassLoader())


class Ah(object):
    def __init__(self, jar, home):
        from jpype import JClass
        self.L = loader(jar)
        g = lambda n: JClass(PKG + n, loader=self.L)
        self.Cfg, self.Lg, self.S, self.U, self.Rec, self.Sal, self.Fn = g("AhCfg"), g("AhLog"), g("AhStore"), g("AhUtil"), g("AhRec"), g("AhSales"), g("AhPriceFn")
        self.g = g
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
        """the setup() data steps in their order"""
        self.Cfg.migrate()
        self.Cfg.load()
        self.Cfg.loadRules(self.S.DIR)
        self.Cfg.loadBlocked()
        self.Cfg.applyBuiltin()
        n = int(self.S.load())
        self.S.restoreFromLog()
        self.Lg.scanStarts()
        return n


def bridge_fakes():
    """a stand-in coin ledger (coins:fn:get / take / add / flush / sameacct) + gear:fn:rarity (meta field R) on the shared bridge"""
    from jpype import JClass, JImplements, JOverride
    Long, Bool, Int = JClass("java.lang.Long"), JClass("java.lang.Boolean"), JClass("java.lang.Integer")
    bal = {}

    @JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, op):
            self.op = op

        @JOverride
        def apply(self, o):
            if self.op == "get":
                return Long.valueOf(bal.get(str(o), 0))
            if self.op == "flush":
                return Int.valueOf(1)
            if self.op == "sameacct":
                return Bool.FALSE
            if self.op == "rarity":
                m = o[1]
                if m is None or not m.containsKey("R"):
                    return None
                return str(m.get("R").asString().getValue())
            u, n = str(o[0]), int(o[1])
            if self.op == "take":
                if bal.get(u, 0) < n:
                    return Bool.FALSE
                bal[u] = bal.get(u, 0) - n
                return Bool.TRUE
            bal[u] = bal.get(u, 0) + n
            return Long.valueOf(bal[u])
    Sys = JClass("java.lang.System")
    br = Sys.getProperties().get("skyy.bridge")
    if br is None:
        br = JClass("java.util.concurrent.ConcurrentHashMap")()
        Sys.getProperties().put("skyy.bridge", br)
    keep = []
    for k in ("get", "take", "add", "flush", "sameacct"):
        f = Fn(k)
        keep.append(f)
        br.put("coins:fn:" + k, f)
    f = Fn("rarity")
    keep.append(f)
    br.put("gear:fn:rarity", f)
    return br, bal, keep


# ---------------------------------------------------------------------------------------------------- X: exec
def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JObject
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    br, bal, keep = bridge_fakes()
    UUID = JClass("java.util.UUID")
    Paths = JClass("java.nio.file.Paths")

    # ================================================================ WINDOWS at NOW0 (2026-11-02 00:00 UTC)
    h1 = os.path.join(scratch, "win", "Skyy_SkyyAuctions")
    n0 = NOW0
    mA, mB, mOld = month(n0), month(n0 - WIN3), month(n0 - 40 * WIN1)
    K.check(mA == "2026-11" and mB == "2026-10", "WIN the fixed now spans two archive months (%s + %s)" % (mB, mA))
    ref = {}   # key -> [(each, at)]

    def sale(rid, iid, qty, price, at, rar=None, sub=None, name=None, v=1, counted=True, closed=True):
        r = mk(rid, iid, qty, price, "SOLD", now=n0, at=at, rar=rar, closed=closed, v=v)
        write(h1, r, sub or ("archive/" + month(at + 1000)), name)
        if counted:
            ref.setdefault(iid, []).append((ceil_div(price, qty), at))
            if rar:
                ref.setdefault(iid + "|" + rar, []).append((ceil_div(price, qty), at))
        return r
    I = "Ingredient_Bar_Iron"
    sale(101, I, 1, 100, n0 - 3600000)
    sale(102, I, 2, 200, n0 - 7200000)
    sale(103, I, 1, 10000, n0 - 10800000)              # the 100x outlier
    sale(104, I, 1, 130, n0 - WIN1)                    # exactly 24 h: 3 d only
    sale(105, I, 1, 120, n0 - WIN3 + 1)                # 1 ms inside the 3 days (archived in 2026-10)
    sale(106, I, 1, 1, n0 - WIN3, counted=False)       # exactly 72 h: out
    sale(107, I, 1, 101, n0 - WIN1 + 1)                # 1 ms inside the day
    sale(108, I, 3, 301, n0 - 4 * 3600000)             # each = ceil(301 / 3) = 101
    sale(109, I, 1, 7, n0 - 3600000, sub="archive/" + mOld, counted=False)   # an old month folder: never read
    os.utime(write(h1, mk(110, I, 1, 9, "SOLD", now=n0, at=n0 - 3600000, closed=True), "archive/" + mA), (n0 / 1000.0 - 5 * 86400, n0 / 1000.0 - 5 * 86400))
    # an OPEN sold listing (coins owed) + an archived copy of the same listing id: counted once
    sale(201, I, 1, 90, n0 - 1800000, sub="listings", closed=False)
    sale(201, I, 1, 90, n0 - 1800000, name="201.r9.json", counted=False)
    O = "Ore_Copper"
    sale(301, O, 1, 50, n0 - 1000)
    sale(302, O, 1, 50, n0 - 2000)
    sale(303, O, 1, 5000, n0 - 3000)                   # outlier with only 3 sales
    R = "Rock_Stone"
    sale(311, R, 1, 10, n0 - 1000)
    sale(312, R, 1, 20, n0 - 2000)                     # 2 sales: no median at 3
    W = "Weapon_Sword_Iron"
    sale(401, W, 1, 1000, n0 - 1000, rar="rare")
    sale(402, W, 1, 1100, n0 - 2000, rar="rare")
    sale(403, W, 1, 1200, n0 - 3000, rar="rare")
    sale(404, W, 1, 5000, n0 - 4000, rar="epic")
    sale(501, "Skyy_Sack_Small", 1, 500, n0 - 1000, counted=False)          # a Magic Bag: blocked, no row
    sale(502, "Tool_Pickaxe_Copper", 1, 500, n0 - 1000, counted=False)      # gathering gear: blocked
    sale(503, "Ore_Iron", 1, 500, n0 - 1000, v=2, counted=False)            # a newer schema: read-only, ignored
    # live listings (endsAt = now0 + 1 h)
    lst = [mk(601, I, 10, 950, now=n0), mk(602, I, 3, 301, now=n0), mk(603, I, 1, 10, now=n0, ends=-1), mk(604, W, 1, 3000, now=n0),
           mk(605, W, 1, 4000, now=n0, rar="rare"), mk(606, W, 1, 9000, now=n0, rar="epic"), mk(607, O, 1, 1, now=n0, v=2),
           mk(608, "Tool_Pickaxe_Copper", 1, 5, now=n0), mk(609, "Plant_Crop_Wheat_Item", 64, 640, now=n0)]
    for r in lst:
        write(h1, r)
    a = Ah(jar, h1)
    n_open = a.start()
    v0 = int(a.Sal.VER.get())
    s = str(a.Sal.rebuild(n0))
    print("   rebuild:", s)
    K.check("sales of the last 3 days" in s and ("archive files in %s + %s" % (mB, mA)) in s and "1 older files skipped" in s, "WIN the rebuild reads %s + %s and skips the old file: %s" % (mB, mA, s))
    K.check(int(a.Sal.VER.get()) > v0 and int(br.get("auction:prices:version")) == int(a.Sal.VER.get()), "WIN the rebuild bumps auction:prices:version (bridge = VER)")
    t = parse(a.Sal.table(n0, 3))
    want_keys = sorted(set(ref) | {I, W, W + "|rare", W + "|epic", "Plant_Crop_Wheat_Item"})
    K.eq(sorted(t), want_keys, "WIN the rows (blocked / read-only / old-month / skipped ids absent; gear rarity rows)")
    for k in sorted(ref):
        K.eq(t[k][1:], ref_row(ref[k], n0), "WIN %s medians + counts = the reference" % k)
    K.check(t[I][3] < 200 and t[I][1] < 200, "WIN the 100x outlier (10000) does not move the Iron medians: %s" % (t[I],))
    K.eq(t[O][1:], (50, 3, 50, 3), "WIN Ore_Copper 50 / 50 / 5000: median 50 (a plain average would be 1700)")
    K.eq(t[R][1:], (-1, 2, -1, 2), "WIN Rock_Stone with 2 sales: no median (n still 2)")
    t1 = parse(a.Sal.table(n0, 1))
    K.eq(t1[R][1:], (15, 2, 15, 2), "WIN with minSales 1 the 2-sale median shows (10 / 20 -> 15)")
    K.eq(t[W + "|rare"][1:], (1100, 3, 1100, 3), "WIN the rare row: median 1100")
    K.eq(t[W + "|epic"][1:], (-1, 1, -1, 1), "WIN the epic row: 1 sale, no median")
    K.eq(t[W][2], 4, "WIN the item row counts every rarity (4)")
    n_iron_1d = sum(1 for e, at in ref[I] if n0 - at < WIN1)
    K.eq(t[I][2], n_iron_1d, "WIN the 24 h cut-off: exactly 24 h old is out of the 1 d window, 1 ms younger is in (%d)" % n_iron_1d)
    K.check(sum(1 for e, at in ref[I] if at == n0 - 1800000) == 1, "WIN the open SOLD listing #201 + its archived copy count once")
    # lowest BIN = AhStore.lowestBin (the same rule), per rarity too
    for k in (I, W, O, "Plant_Crop_Wheat_Item"):
        lb = a.S.lowestBin(k, None, n0)
        K.eq(t.get(k, (-1,))[0], int(lb[0]), "LOW %s lowest BIN each = AhStore.lowestBin" % k)
    K.eq(t[I][0], 95, "LOW Iron: 950 / 10 = 95 beats 301 / 3 = 101; the expired 10-coin listing is not seen")
    K.eq((t[W][0], t[W + "|rare"][0], t[W + "|epic"][0]), (3000, 4000, 9000), "LOW the sword: any 3000, rare 4000, epic 9000")
    K.eq(t["Plant_Crop_Wheat_Item"], (10, -1, 0, -1, 0), "LOW a listed item with no sales: n 0, medians -1")
    K.check(O in t and t[O][0] == -1, "LOW a read-only (v2) listing is not seen (Ore_Copper has no lowest BIN)")
    # AGE: the tick at now0 + 24 h
    na = int(a.Sal.NEXT_AGE)
    want_na = min((at + WIN1) if at + WIN1 > n0 else (at + WIN3) for kk in ref for e, at in ref[kk] if "|" not in kk)
    K.eq(na, want_na, "AGE NEXT_AGE = the earliest window exit")
    a.Sal.BUILT = True
    v1 = int(a.Sal.VER.get())
    a.Sal.tick(na - 1)
    K.eq(int(a.Sal.VER.get()), v1, "AGE the tick before NEXT_AGE does nothing")
    n2 = n0 + WIN1
    a.Sal.tick(n2)
    K.check(int(a.Sal.VER.get()) == v1 + 1 and int(a.Sal.NEXT_AGE) > n2, "AGE the tick at +24 h bumps the version once and moves NEXT_AGE on")
    t2 = parse(a.Sal.table(n2, 3))
    for k in sorted(ref):
        K.eq(t2.get(k, (0, -1, 0, -1, 0))[1:], ref_row(ref[k], n2) if any(n2 - at < WIN3 for e, at in ref[k]) else (-1, 0, -1, 0), "AGE %s at +24 h = the reference" % k)
    st = str(a.Sal.statusLine())
    K.check("Price index" in st and "start rebuild" in st, "STATUS /ahadmin status line: %s" % st[:140])
    print("   status:", st)

    # ================================================================ LIVE (real time): AhTick, buys, version, rebuild equals live
    h2 = os.path.join(scratch, "rt", "Skyy_SkyyAuctions")
    now = int(time.time() * 1000)
    old = [mk(700 + i, I, 1, 100 + i, "SOLD", now=now, at=now - 3600000 * (i + 1), closed=True) for i in range(4)]
    for r in old:
        write(h2, r, "archive/" + month(int(r["closedAt"]["$numberLong"])))
    for r in [mk(801, I, 3, 301, now=now), mk(802, I, 1, 90, now=now), mk(803, W, 1, 2000, now=now, rar="rare"), mk(804, O, 2, 100, now=now),
              mk(805, O, 1, 70, now=now, ends=2500), mk(806, "Plant_Crop_Wheat_Item", 1, 7, now=now)]:
        write(h2, r)
    # MERGE: a sale that reaches the live path while no rebuild has run (not on disk) is carried over by the rebuild (own empty folder)
    m = Ah(jar, os.path.join(scratch, "merge", "Skyy_SkyyAuctions"))
    m.start()
    lone = m.Rec.parse(json.dumps(mk(9999, O, 1, 33, "SOLD", now=now, at=now - 1000)))
    K.check(bool(m.Sal.addLive("9999", m.Sal.entry(lone, now), now)) and not bool(m.Sal.addLive("9999", m.Sal.entry(lone, now), now)), "MERGE a live sale is added once (the same listing id again = refused)")
    sm = str(m.Sal.rebuild(now))
    K.check("1 sold while it ran" in sm and parse(m.Sal.table(now, 1)).get(O, (0, 0, 0, 0, 0))[1:] == (33, 1, 33, 1), "MERGE the rebuild carried the live sale over: %s" % sm)
    b = Ah(jar, h2)
    b.start()
    K.check(not bool(b.Sal.BUILT), "LIVE before the first tick no rebuild has run")
    tick = b.g("AhTick")()
    lb0 = str(b.Sal.LAST_BUILD)
    t_tick = time.time()
    tick.run()
    t_tick = time.time() - t_tick
    t_end = time.time() + 20
    while str(b.Sal.LAST_BUILD) == lb0 and time.time() < t_end:
        time.sleep(0.05)
    K.check(bool(b.Sal.BUILT) and "4 sales of the last 3 days" in str(b.Sal.LAST_BUILD), "LIVE AhTick.run did the start rebuild: %s" % b.Sal.LAST_BUILD)
    me = str(JClass("java.lang.Thread").currentThread().getName())
    K.check(str(b.Sal.BUILD_THREAD) == "SkyyAuctions price index" and str(b.Sal.BUILD_THREAD) != me,
            "FIX2 the start rebuild ran on its own daemon thread '%s' (the tick thread '%s' returned in %.0f ms)" % (b.Sal.BUILD_THREAD, me, t_tick * 1000))
    tb = parse(b.Sal.table(now, 1))
    K.eq(tb[I][2], 4, "LIVE the 4 archived Iron sales are in the index")
    b1 = str(b.Sal.LAST_BUILD)
    tick.run()
    K.eq(str(b.Sal.LAST_BUILD), b1, "LIVE a second tick does not rebuild again")
    ub, us_ = UUID.fromString(BOB), UUID.fromString(SAM)
    bal[BOB] = 10 ** 9

    def ver():
        return int(b.Sal.VER.get())
    v = ver()
    r = b.S.buy(None, ub, BOB, "Bob", "P1", "801", 301)
    K.check(bool(r.ok) and str(b.Rec.state(b.S.get("801"))) == "SOLD", "BUY Bob buys #801 (3 Iron for 301) through AhStore.buy: %s" % r.msg)
    K.check(ver() >= v + 1 and int(br.get("auction:prices:version")) == ver(), "BUY the version bumped (%d -> %d) and is on the bridge" % (v, ver()))
    tb = parse(b.Sal.table(int(time.time() * 1000), 1))
    K.eq(tb[I][2], 5, "BUY the sale joined the Iron row (5 sales)")
    K.eq(tb[I][0], 90, "BUY the Iron lowest BIN is now #802 (90 each)")
    r = b.S.buy(None, ub, BOB, "Bob", "P1", "803", 2000)
    K.check(bool(r.ok), "BUY Bob buys the rare sword #803: %s" % r.msg)
    tb = parse(b.Sal.table(int(time.time() * 1000), 1))
    K.check(tb.get(W + "|rare", (0, 0, 0, 0, 0))[2] == 1 and tb[W + "|rare"][1] == 2000, "BUY the sale has its gear rarity row (rare, 2000): %s" % (tb.get(W + "|rare"),))
    v = ver()
    r = b.S.buy(None, ub, BOB, "Bob", "P1", "802", 1)
    K.check(not bool(r.ok) and ver() == v, "BUY a refused buy (price moved) changes nothing: %s" % r.msg)
    v = ver()
    rc = b.S.claimCoins(us_, SAM, "801")
    K.check(bool(rc.ok) and ver() == v, "CLAIM Sam claims the coins of #801: no version bump (%s)" % rc.msg)
    while int(time.time() * 1000) < now + 2600:
        time.sleep(0.1)
    v = ver()
    notes = b.S.expireDue(int(time.time() * 1000))
    K.check(ver() > v and str(b.Rec.state(b.S.get("805"))) == "EXPIRED", "EXPIRE the ended listing #805 expires: version bumped")
    v = ver()
    ra = b.S.adminRemove("Admin", "806", "test")
    K.check(bool(ra.ok) and ver() > v, "REMOVE an admin removes #806: version bumped (%s)" % ra.msg)
    # FIX1: bumps from 4 threads at once (world thread + scheduler + rebuild in game) leave the bridge = the counter
    import threading
    def hammer():
        for _ in range(3000):
            b.Sal.bump()
    vs = ver()
    ths = [threading.Thread(target=hammer) for _ in range(4)]
    for th in ths:
        th.start()
    for th in ths:
        th.join()
    K.check(ver() == vs + 12000 and int(br.get("auction:prices:version")) == ver(), "FIX1 12000 bumps from 4 threads: VER %d, bridge %s (equal)" % (ver(), br.get("auction:prices:version")))
    # AhPriceFn
    fn = b.Fn()
    s_null = str(fn.apply(None))
    s_one = str(fn.apply(JClass("java.lang.Integer").valueOf(1)))
    s_junk = str(fn.apply("junk"))
    K.check(parse(s_null)[I][1] != -1 and parse(s_null) == parse(s_junk) and parse(s_one)[W + "|rare"][1] == 2000 and parse(s_null)[W + "|rare"][1] == -1,
            "FN apply(null) = apply(junk) = 3 sales needed; apply(1) shows the 1-sale rare median")
    # ---- REBUILD EQUALS LIVE: copy the folder now, rebuild it with a fresh loader at the same now
    h3 = os.path.join(scratch, "copy", "Skyy_SkyyAuctions")
    shutil.copytree(h2, h3)
    tnow = int(time.time() * 1000)
    live_t = parse(b.Sal.table(tnow, 1))
    c = Ah(jar, h3)
    c.start()
    s3 = str(c.Sal.rebuild(tnow))
    copy_t = parse(c.Sal.table(tnow, 1))
    K.eq(copy_t, live_t, "REBUILD the index rebuilt from a COPY of the folder = the live index (same now)")
    K.check(I in copy_t and copy_t[I][2] == 5 and W + "|rare" in copy_t, "REBUILD the copy holds the archived + the bought sales")
    print("   copy rebuild:", s3)

    # ================================================================ COST
    h4 = os.path.join(scratch, "cost", "Skyy_SkyyAuctions")
    rnd = random.Random(716)
    ids = ["Ingredient_Item_%03d" % i for i in range(360)] + ["Weapon_Cost_%02d" % i for i in range(40)]
    for i in range(3000):
        iid = rnd.choice(ids)
        write(h4, mk(20000 + i, iid, rnd.randint(1, 64), rnd.randint(10, 100000), now=now, rar=rnd.choice(["rare", "epic", "legendary"]) if iid.startswith("Weapon") else None))
    for i in range(6000):
        iid = rnd.choice(ids)
        at = now - rnd.randint(0, WIN3 + WIN1)
        r = mk(40000 + i, iid, rnd.randint(1, 64), rnd.randint(10, 100000), "SOLD", now=now, at=at, closed=True,
               rar=rnd.choice(["rare", "epic", "legendary"]) if iid.startswith("Weapon") else None)
        write(h4, r, "archive/" + month(at + 1000))
    d = Ah(jar, h4)
    t0 = time.time()
    d.start()
    t_load = time.time() - t0
    s4 = str(d.Sal.rebuild(now))
    first = time.time()
    tab = str(d.Sal.table(now, 3))
    first = time.time() - first
    t0 = time.time()
    for _ in range(20):
        d.Sal.table(now, 3)
    avg = (time.time() - t0) / 20
    rows = len(parse(tab))
    msg = "COST 3000 listings + 6000 archived sales: load %.0f ms; rebuild: %s; table %d rows, first call %.1f ms, then %.2f ms per call (%d chars)" % (t_load * 1000, s4, rows, first * 1000, avg * 1000, len(tab))
    print("  ", msg)
    K.notes.append(msg)
    K.check(rows >= 400 and avg < 0.25, msg)

    # ================================================================ STATIC
    z = zipfile.ZipFile(jar)
    for cn in ("AhSales", "AhPriceFn"):
        bts = z.read("com/skyy/auctions/%s.class" % cn)
        K.check(b"Metadata" not in bts and b"UpdateTranslations" not in bts, "STATIC %s never touches a stack's metadata or sends translations" % cn)
    K.check(not any(b"UpdateTranslations" in z.read(n) for n in z.namelist() if n.endswith(".class")), "STATIC no class names UpdateTranslations (runtime_lang_owner stays SkyyBazaar's)")
    gen = open(os.path.join(HERE, "build_skyyauctions_%s.py" % VERSION), encoding="utf8").read()
    bz = gen[gen.index("public static @RES@ buy0("):gen.index("public static @RES@ buy0(") + 9000]
    K.check(bz.index("  swap0(next, true);\n  @PKG@.AhSales.add(next);") > 0, "STATIC the sale add sits right after the SOLD commit's swap0 in buy0")
    K.check("synchronized (VLOCK) { v = bump0(); }" in gen and gen.count("bump0()") == 2, "FIX1 STATIC the increment + bridge put run under VLOCK (bump0 has one caller)")
    K.check("if (!BUILT) { BUILT = true; startBuild(); }" in gen and "rebuild(now)" not in gen[gen.index("public static void tick(long now)"):gen.index("public static void tick(long now)") + 400], "FIX2 STATIC the tick starts the rebuild thread, never rebuilds inline")
    K.check('b.put("auction:fn:priceTable", new @PKG@.AhPriceFn());' in gen and 'b.put("auction:prices:version"' in gen, "STATIC setup puts both bridge keys")
    K.save()


# ---------------------------------------------------------------------------------------------------- D: live copy
def run_live(out, jar, scratch, home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    h0 = HK.tree_hash(home)
    snaps = []
    now = int(time.time() * 1000)
    for start in (1, 2):
        a = Ah(jar, home)
        n = a.start()
        s = str(a.Sal.rebuild(now))
        t = str(a.Sal.table(now, 3))
        K.check("sales of the last 3 days" in s, "D%d start %d: %d open records, rebuild: %s, table %d rows" % (start, start, n, s, len([x for x in t.split("\n") if x])))
        print("   D%d: %s" % (start, s))
        snaps.append(HK.tree_hash(home))
    changed = sorted(k for k in set(h0) | set(snaps[0]) if h0.get(k) != snaps[0].get(k))
    K.check(not changed, "D the first start changes no file: %s" % changed)
    K.check(snaps[0] == snaps[1], "D the second start changes nothing")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyAuctions", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("exec", run_exec), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyAuctions"))
