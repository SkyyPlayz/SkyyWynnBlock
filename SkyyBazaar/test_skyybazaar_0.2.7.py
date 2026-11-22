"""Harness for SkyyBazaar 0.2.7 (the Bazaar never takes augmented items; tools/bazaar_0_2_7_patch.py).
Build first:
    python tools/bazaar_0_2_7_patch.py && python SkyyBazaar/build_skyybazaar_0.2.7.py --with SkyyCollections/SkyyCollections-0.2.36.jar
    python SkyyBazaar/test_skyybazaar_0.2.7.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, -Xverify:all, tools/harness_kit.py + the 0.2.0 stand-in engine; every new code path is EXECUTED):
  S     static   the patch re-runs to identical bytes; line endings kept; no new command / system / class / bridge key / setting
  A     verify   every class loads + initialises
  C     compare  0.2.6 -> 0.2.7 (EXPECT below: Inv / Trader / BzOrders / BzTabFn + the version texts; no class added)
  K     catalog  every Catalog constant = 0.2.6's (no price / tab / product change)
  P     page     the 0.2.5 page phase re-run on the 0.2.7 jar (Market > Bazaar page: SELL NOW, sell offers, extra-data stacks)
  T     tab      the 0.2.6 Market-tab phase re-run on the 0.2.7 jar (bazaar:fn:tab / tabact; no SkyyGear key = 0.2.6 texts)
  G     augments a stand-in gear:fn:augCount: augmented stacks (storage, hotbar, backpack) kept by EVERY sell path - the Market tab's Sell
                 now, Trader.sellN / sell, Sell <tab> / Sell all tabs, an instant sell into buy orders, a sell offer - plain + metadata-
                 without-augments stacks still sell, coins = the quote of what really left, ONE note per action, a double click / stale
                 page, an unreadable answer / a throw = kept, the market wall still holds, no SkyyGear key = sold exactly as 0.2.6
  R     real     the REAL SkyyGear 0.3.59 jar's gear:fn:augCount (GearAugCntFn, its own class loader) in the same JVM: a gear document with 2
                 augments is kept by Trader.sell, an empty "aug" list sells (fix bzaug1: the stand-in contract checked against the real class)
  D     live     scratch COPIES of the live NewBetaTest Skyy_SkyyBazaar: the 0.2.7 start = the 0.2.6 start, a second 0.2.7 start writes nothing
  AA    audit    engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, subprocess, importlib.util, json, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.2.7"
PKG = "com.skyy.bazaar."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyBazaar-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyBazaar-0.2.6.jar")
GEN = os.path.join(HERE, "build_skyybazaar_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyybazaar_0.2.6.py")
PATCH = os.path.join(ROOT, "tools", "bazaar_0_2_7_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "bzaug1", "bz")))
GEAR_JAR = os.path.join(ROOT, "SkyyGear", "SkyyGear-0.3.59.jar")
LIVE = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyBazaar")
EXPECT = {"CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "Inv": ["+m augHeld", "+m augMap", "+m augOn", "+m augs", "~m walled"],
          "Trader": ["+m augIn", "+m augNote", "+m augText", "+m sellA", "+m sellNa", "~m sell", "~m sellInventory", "~m sellN0"],
          "BzOrders": ["~m place0"], "BzTabFn": ["~m read0"], "BzPage": ["~m stepWhy"], "SkyyBazaarPlugin": ["~m setup"]}
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = []


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


T26 = tmod(os.path.join(HERE, "test_skyybazaar_0.2.6.py"), "tbz026")
T25 = T26.T25
NOTE = "that carry augments (the Bazaar never takes augmented items)"


# ------------------------------------------------------------------------------------------------------------------- S
def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.count('VERSION = "0.2.7"') == 1 and g.startswith('"""SkyyBazaar 0.2.7'), "S version + header")
    for w in ("registerSystem(", "registerCommand(", "CFG.row(", "Server Setup", "pool.makeClass(", "bridge().put(", "bridge().remove("):
        K.check(g.count(w) == o.count(w), "S no new %s (%d)" % (w, g.count(w)))
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.check(g.count('get("gear:fn:augCount")') == 2 and o.count("gear:fn:augCount") == 0, "S gear:fn:augCount is only READ (augs + augOn), never put")
    K.check("augs(it) > 0" in g[g.index("public static boolean walled("):g.index("public static String wallId(")],
            "S Inv.walled (Inv.countIn / count / take) keeps augmented stacks")
    K.save()


# ------------------------------------------------------------------------------------------------------------------- K
def run_catalog(out, jar, scratch, home):
    K = HK.Child(out)
    res = {}
    for tag, jp in (("old", OLD_JAR), ("new", jar)):
        dst = os.path.join(scratch, "consts_%s.json" % tag)
        p = subprocess.run([sys.executable, os.path.abspath(__file__), "--dump-consts", jp, dst], capture_output=True, text=True)
        K.check(p.returncode == 0, "K constants of %s dumped: %s" % (tag, p.stderr[-300:]))
        res[tag] = json.load(open(dst)) if os.path.isfile(dst) else {}
    diff = sorted(k for k in set(res["old"]) | set(res["new"]) if res["old"].get(k) != res["new"].get(k))
    K.check(not diff and len(res["new"]) > 10, "K every Catalog constant = 0.2.6's (%d constants; differ: %s)" % (len(res["new"]), diff))
    K.save()


def run_page(out, jar, scratch, home):
    T25.run_page(out, jar, scratch, home)


def run_tab(out, jar, scratch, home):
    T26.run_tab(out, jar, scratch, home)


# ------------------------------------------------------------------------------------------------------------------- G
def run_aug(out, jar, scratch, _home):
    from jpype import JClass, JString, JShort, JImplements, JOverride
    K = HK.Child(out)
    T200, T20, W, E, J, fx, home = T25.world(scratch, jar, "aug")
    C, M, Bk, Od, Fl, T, CF, TF, Inv = (J("Catalog"), J("Market"), J("BzBook"), J("BzOrders"), J("BzFill"), J("Trader"), J("BzConfirm"),
                                        J("BzTabFn"), J("Inv"))
    A, Bb, Cc = T200.mkplayers(W)
    ua, ub = A.pr.getUuid(), Bb.pr.getUuid()
    sa, sb = str(ua), str(ub)
    for u in (sa, sb):
        fx.purse[u] = 1000000
    CF.set(ua, 10 ** 12)
    CF.set(ub, 10 ** 12)
    iid, cheap = T200.pick(J)
    nm = str(C.get(iid).name)
    cat = str(C.get(iid).cat)
    if cat not in [str(x) for x in C.categories()]:
        cat = [str(x) for x in C.tabsOf(C.get(iid))][0]
    other = [str(p.id) for p in C.inCat(cat) if str(p.id) != iid and bool(C.usable(str(p.id))) and not bool(T.locked(str(p.id)))
             and int(M.quote(str(p.id), 3, False)) > 0][0]
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    BD, BI, BS = JClass("org.bson.BsonDocument"), JClass("org.bson.BsonInt32"), JClass("org.bson.BsonString")
    Int = JClass("java.lang.Integer")
    asked = {"n": 0}

    # the SkyyGear 0.3.57 gear:fn:augCount stand-in: metadata key SkyyAugN = the count; -9 = an unreadable answer (null); -8 = a throw
    @JImplements("java.util.function.Function")
    class AugCnt:
        @JOverride
        def apply(self, o):
            asked["n"] += 1
            md = o.getMetadata()
            if md is None or not md.containsKey("SkyyAugN"):
                return Int.valueOf(0)
            n = int(md.get("SkyyAugN").asInt32().getValue())
            if n == -9:
                return None
            if n == -8:
                raise RuntimeError("stand-in augCount throws")
            return Int.valueOf(n)
    GEAR = AugCnt()
    E.br.put("gear:fn:augCount", GEAR)

    def aug(i, q, n):
        return IS(i, q).withMetadata(BD("SkyyAugN", BI(n)))

    BPK = A.inv.getBackpack() is not None and int(A.inv.getBackpack().getCapacity()) > 0

    def put(P, cont, slot, st):
        if cont == "b" and not BPK:          # the stand-in backpack has no slots: the hotbar's last slot stands in for it
            cont, slot = "h", int(P.inv.getHotbar().getCapacity()) - 1
        c = {"s": P.inv.getStorage(), "h": P.inv.getHotbar(), "b": P.inv.getBackpack()}[cont]
        c.setItemStackForSlot(JShort(slot), st)

    def clear(P):
        for c in (P.inv.getStorage(), P.inv.getHotbar(), P.inv.getBackpack()):
            if c is None:
                continue
            for s in range(int(c.getCapacity())):
                c.setItemStackForSlot(JShort(s), None)

    def scan(P, i):
        """(plain quantity, [(augment count or None, quantity), ...] of the metadata stacks of id i)"""
        pl, md = 0, []
        for c in (P.inv.getStorage(), P.inv.getHotbar(), P.inv.getBackpack()):
            if c is None:
                continue
            for s in range(int(c.getCapacity())):
                st = c.getItemStack(JShort(s))
                if st is None or bool(st.isEmpty()) or str(st.getItemId()) != i:
                    continue
                m = st.getMetadata()
                if m is None:
                    pl += int(st.getQuantity())
                else:
                    md.append((int(m.get("SkyyAugN").asInt32().getValue()) if m.containsKey("SkyyAugN") else None, int(st.getQuantity())))
        return pl, sorted(md, key=lambda x: (x[0] is None, x[0], x[1]))

    def reset(P=A, i=iid):
        clear(P)
        fx.bags.clear()
        TF.LASTOP.clear()
        TF.ARM.clear()
    TF.TEST_ANY_THREAD = True
    tok = str(Bk.pkey(ua))
    OA = JClass("java.lang.Object[]")

    def args(*xs):
        a = OA(len(xs))
        for k, x in enumerate(xs):
            a[k] = x if not isinstance(x, int) or isinstance(x, bool) else Int.valueOf(x)
        return a

    def read(u, sel, amt=2):
        s = str(TF(0).apply(args(u, JString(cat), JString(""), JString(sel), 0, 8, amt)))
        L = dict((ln.split("|")[0], ln.split("|")) for ln in s.split("\n") if ln.split("|")[0] in ("d", "q"))
        return L["d"], L["q"]

    def act(op, arg, u=ua, t=None, clear_=True):
        if clear_:
            TF.LASTOP.clear()
        return str(TF(1).apply(args(u, JString(t if t is not None else tok), JString(op), JString(arg))))

    # ---------------------------------------------------------------- 1. counting: augmented stacks are not "held"
    reset()
    put(A, "s", 0, IS(iid, 6))
    put(A, "s", 1, aug(iid, 2, 2))            # augmented (2 augments) - KEPT
    put(A, "s", 2, aug(iid, 3, 0))            # metadata without augments - sells as before
    put(A, "h", 0, aug(iid, 1, 1))            # augmented in the hotbar
    put(A, "b", 0, aug(iid, 1, 3))            # augmented in the backpack
    K.check(int(Inv.count(A.pl, iid)) == 9 and int(Inv.augHeld(A.pl, iid)) == 4 and int(Inv.augs(aug(iid, 1, 2))) == 2 and int(Inv.augs(IS(iid, 1))) == 0,
            "G1 Inv.count = 9 (6 plain + 3 metadata without augments), Inv.augHeld = 4 (storage 2 + hotbar 1 + backpack 1)")
    hm = Inv.augMap(A.pl)
    K.check(int(hm.get(iid)) == 4 and int(hm.size()) == 1, "G1 Inv.augMap: one pass, {%s: 4}" % iid)
    n0 = asked["n"]
    int(Inv.count(A.pl, iid))
    K.check(asked["n"] - n0 == 4, "G1 only the 4 metadata stacks of the id are asked (plain stacks never): %d" % (asked["n"] - n0))
    d, q = read(ua, iid)
    K.check(d[7] == "9" and q[4] == "9" and q[5] == str(int(Fl.quote(A.pl, ua, iid, 9, False))), "G1 bazaar:fn:tab: you have 9, sell All = 9 priced (%s / %s)" % (d[7], q[4:7]))
    # ---------------------------------------------------------------- 2. the Market tab's Sell now (Trader.sellN)
    sv = int(q[5])
    p0 = fx.purse[sa]
    r = act("sell", "%s|9|%d" % (iid, sv))
    pl, md = scan(A, iid)
    K.check(r.startswith("+") and fx.purse[sa] == p0 + sv and pl == 0 and md == [(1, 1), (2, 2), (3, 1)],
            "G2 Market tab SELL NOW all: 9 sold for exactly the shown %d, the 4 augmented kept with their augments (%s / %s)" % (sv, r, md))
    K.check(r.count("kept 4 " + nm + " " + NOTE) == 1, "G2 ... ONE note says so: %s" % r)
    # only augmented left
    d, q = read(ua, iid)
    K.check(d[7] == "0" and q[6] == "Yours carry augments - the Bazaar keeps them out", "G2 READ with only augmented ones: the sell 'why not' says so (%s)" % q[4:])
    p0 = fx.purse[sa]
    r = act("sell", "%s|1|%d" % (iid, int(M.quote(iid, 1, False))))
    K.check(r.startswith("-") and NOTE in r and fx.purse[sa] == p0 and scan(A, iid) == (0, [(1, 1), (2, 2), (3, 1)]),
            "G2 SELL NOW with only augmented ones = refused + the note, nothing moved (%s)" % r)
    PG = J("BzPage")(A.pr, JString(iid))
    lim = PG.limits(A.pl, ua, iid)
    now = int(JClass("java.lang.System").currentTimeMillis())
    w1 = str(PG.stepWhy(ua, A.pl, iid, 1, 1, -2, lim, now))
    w3 = str(PG.stepWhy(ua, A.pl, iid, 3, 1, int(M.quote(iid, 1, True)), lim, now))
    K.check(int(lim[2]) == 0 and w1 == "Yours carry augments - the Bazaar keeps them out", "G2 fix: the Bazaar page's SELL NOW reason line says so (%s)" % w1)
    K.check(w3 == "Yours carry augments - the Bazaar keeps them out", "G2 fix: the Bazaar page's sell offer reason line says so (%s)" % w3)
    # ---------------------------------------------------------------- 3. double click + stale page
    put(A, "s", 0, IS(iid, 5))
    s1 = int(Fl.quote(A.pl, ua, iid, 1, False))
    p0 = fx.purse[sa]
    TF.LASTOP.clear()
    r1 = act("sell", "%s|1|%d" % (iid, s1), clear_=False)
    r2 = act("sell", "%s|1|%d" % (iid, s1), clear_=False)
    K.check(r1.startswith("+") and r2 == "=One moment." and fx.purse[sa] == p0 + s1 and scan(A, iid) == (4, [(1, 1), (2, 2), (3, 1)]),
            "G3 a DOUBLE CLICK sells once, augmented kept (%s / %s)" % (r1, r2))
    K.check(NOTE not in r1, "G3 fix: selling 1 of 5 plain (augmented held) carries NO kept-augments note: %s" % r1)
    r = act("sell", "%s|4|%d" % (iid, int(Fl.quote(A.pl, ua, iid, 4, False))), t="someone-else")
    K.check(r.startswith("=Your profile changed") and fx.purse[sa] == p0 + s1 and scan(A, iid)[0] == 4, "G3 a stale page = nothing moved (%s)" % r)
    # ---------------------------------------------------------------- 4. Trader.sellN / Trader.sell (want 0 = all)
    p0 = fx.purse[sa]
    w4 = int(Fl.quote(A.pl, ua, iid, 4, False))
    r = T.sellN(A.pl, ua, "Alice", iid, 5, w4)
    K.check(not bool(r.ok) and "only hold 4" in str(r.msg) and NOTE in str(r.msg) and fx.purse[sa] == p0, "G4 sellN of 5 with 4 plain = refused + note (%s)" % r.msg)
    w1 = int(Fl.quote(A.pl, ua, iid, 1, False))
    r = T.sell(A.pl, ua, "Alice", iid, 1)
    K.check(bool(r.ok) and int(r.qty) == 1 and fx.purse[sa] == p0 + w1 and NOTE not in str(r.msg), "G4 fix: Trader.sell of 1 (3 plain left) = no note (%s)" % r.msg)
    p0 = fx.purse[sa]
    w3 = int(Fl.quote(A.pl, ua, iid, 3, False))
    r = T.sell(A.pl, ua, "Alice", iid, 0)
    K.check(bool(r.ok) and int(r.qty) == 3 and int(r.coins) == w3 and fx.purse[sa] == p0 + w3 and scan(A, iid) == (0, [(1, 1), (2, 2), (3, 1)])
            and str(r.msg).count(NOTE) == 1, "G4 Trader.sell (all): 3 sold for %d, augmented kept, one note (%s)" % (w3, r.msg))
    # ---------------------------------------------------------------- 5. Sell <tab> / Sell all tabs: one note for the whole button
    put(A, "s", 0, IS(iid, 5))
    put(A, "s", 3, IS(other, 3))
    put(A, "s", 4, aug(other, 1, 1))
    exp = int(M.quote(iid, 5, False)) + int(M.quote(other, 3, False))
    pre = T.preview(A.pl, ua, JString(cat))
    K.check(int(pre[0]) == 8, "G5 the Sell <tab> preview counts 8 (augmented left out): %s" % list(pre))
    p0 = fx.purse[sa]
    r = T.sellInventory(A.pl, ua, "Alice", JString(cat))
    K.check(bool(r.ok) and int(r.qty) == 8 and fx.purse[sa] == p0 + int(r.coins) and scan(A, iid) == (0, [(1, 1), (2, 2), (3, 1)])
            and scan(A, other) == (0, [(1, 1)]), "G5 Sell %s: 8 sold, the 5 augmented (2 ids) kept (%s)" % (cat, r.msg))
    K.check(str(r.msg).count("kept 5 items " + NOTE) == 1 and str(r.msg).count("kept") == 1, "G5 ... ONE note for the whole button: %s" % r.msg)
    p0 = fx.purse[sa]
    r = T.sellInventory(A.pl, ua, "Alice", None)
    K.check(not bool(r.ok) and "kept 5 items " + NOTE in str(r.msg) and fx.purse[sa] == p0, "G5 Sell all tabs with only augmented = nothing sold + the note (%s)" % r.msg)
    clear(A)
    put(A, "s", 0, IS(iid, 2))
    r = T.sellInventory(A.pl, ua, "Alice", None)
    K.check(bool(r.ok) and "augments" not in str(r.msg), "G5 no augmented held = no note (%s)" % r.msg)
    # ---------------------------------------------------------------- 6. an instant sell into buy orders + a sell offer (order book)
    reset()
    S_, Bp = int(M.quote(iid, 1, False)), int(M.quote(iid, 1, True))
    rb = Od.place(Bb.pl, ub, "Bob", iid, 0, S_ + 1, 3)
    K.check(bool(rb.ok), "G6 Bob places a buy order for 3 at %d (%s)" % (S_ + 1, rb.msg))
    put(A, "s", 0, IS(iid, 2))
    put(A, "s", 1, aug(iid, 2, 2))
    p0 = fx.purse[sa]
    q2 = int(Fl.quote(A.pl, ua, iid, 2, False))
    r = T.sellN(A.pl, ua, "Alice", iid, 2, q2)
    K.check(bool(r.ok) and "buy orders" in str(r.msg) and fx.purse[sa] == p0 + int(r.coins) and scan(A, iid) == (0, [(2, 2)]) and NOTE in str(r.msg),
            "G6 SELL NOW fills Bob's buy order with the 2 plain ones, the augmented kept (%s)" % r.msg)
    put(A, "s", 0, IS(iid, 4))
    r1o = Od.place(A.pl, ua, "Alice", iid, 1, Bp - 1, 1)
    K.check(bool(r1o.ok) and int(r1o.qty) == 1 and NOTE not in str(r1o.msg) and scan(A, iid) == (3, [(2, 2)]),
            "G6 fix: a sell offer of 1 (3 plain left) = no note (%s)" % r1o.msg)
    ro = Od.place(A.pl, ua, "Alice", iid, 1, Bp - 1, 3)
    K.check(bool(ro.ok) and int(ro.qty) == 3 and scan(A, iid) == (0, [(2, 2)]) and NOTE in str(ro.msg), "G6 a SELL OFFER takes the 3 plain ones only + the note (%s)" % ro.msg)
    rx = Od.place(A.pl, ua, "Alice", iid, 1, Bp - 1, 2)
    K.check(not bool(rx.ok) and scan(A, iid) == (0, [(2, 2)]), "G6 a sell offer with only augmented ones is refused, nothing taken (%s)" % rx.msg)
    # ---------------------------------------------------------------- 7. unreadable answers are kept; 0 augments sells; the wall holds
    reset()
    put(A, "s", 0, aug(iid, 1, -9))
    put(A, "s", 1, aug(iid, 1, -8))
    put(A, "s", 2, aug(iid, 1, -1))
    put(A, "s", 3, aug(iid, 2, 0))
    stamp = IS(iid, 1).withMetadata(BD("SkyyStamp", BS("h")))
    put(A, "s", 4, stamp)

    @JImplements("java.util.function.Function")
    class Wall:
        @JOverride
        def apply(self, s):
            m = s.getMetadata()
            return "stamped" if (m is not None and m.containsKey("SkyyStamp")) else None
    vm = JClass("java.util.HashMap")()
    vm.put("t", Wall())
    E.br.put("market:veto", vm)
    K.check(int(Inv.augs(aug(iid, 1, -9))) == 1 and int(Inv.augs(aug(iid, 1, -8))) == 1 and int(Inv.augs(aug(iid, 1, -1))) == 1,
            "G7 an unreadable answer (null), a throw and a negative count = treated as carrying augments")
    p0 = fx.purse[sa]
    e2 = int(Fl.quote(A.pl, ua, iid, 2, False))
    r = T.sell(A.pl, ua, "Alice", iid, 0)
    pl, md = scan(A, iid)
    K.check(bool(r.ok) and int(r.qty) == 2 and int(r.coins) == e2 and fx.purse[sa] == p0 + e2 and pl == 0,
            "G7 the 2 with 0 augments sell for exactly their quote %d (%s)" % (e2, r.msg))
    K.check(md == [(-9, 1), (-8, 1), (-1, 1), (None, 1)], "G7 the unreadable / throwing / negative ones + the stamped (market wall) one stay: %s" % md)
    E.br.remove("market:veto")
    # ---------------------------------------------------------------- 8. NO SkyyGear key = exactly 0.2.6 (augmented stacks sell)
    reset()
    E.br.remove("gear:fn:augCount")
    put(A, "s", 0, IS(iid, 2))
    put(A, "s", 1, aug(iid, 2, 2))
    K.check(int(Inv.count(A.pl, iid)) == 4 and int(Inv.augHeld(A.pl, iid)) == 0 and int(Inv.augMap(A.pl).size()) == 0 and int(Inv.augs(aug(iid, 1, 2))) == 0,
            "G8 no gear:fn:augCount: every stack counts (4), nothing augmented")
    d, q = read(ua, iid)
    K.check(d[7] == "4", "G8 bazaar:fn:tab: you have 4 (as 0.2.6)")
    p0 = fx.purse[sa]
    w = int(Fl.quote(A.pl, ua, iid, 4, False))
    r = act("sell", "%s|4|%d" % (iid, w))
    K.check(r.startswith("+") and "augments" not in r and fx.purse[sa] == p0 + w and scan(A, iid) == (0, []), "G8 ... all 4 sell, no note (0.2.6 behaviour): %s" % r)
    E.br.put("gear:fn:augCount", JString("not a function"))
    put(A, "s", 1, aug(iid, 1, 2))
    K.check(int(Inv.count(A.pl, iid)) == 1 and int(Inv.augHeld(A.pl, iid)) == 0, "G8 a bridge value that is not a Function = no SkyyGear")
    E.br.remove("gear:fn:augCount")
    TF.TEST_ANY_THREAD = False
    K.notes.append("G augments on %s (%s) + %s, tab %s; augCount asked %d times; backpack %s" % (iid, nm, other, cat, asked["n"],
                   "tested" if BPK else "has 0 slots on the stand-in (Inv.conts reads it like storage / hotbar; the hotbar's last slot stood in)"))
    K.save()


# ------------------------------------------------------------------------------------------------------------------- R
def run_real(out, jar, scratch, _home):
    from jpype import JClass, JShort, JArray
    K = HK.Child(out)
    T200, T20, W, E, J, fx, home = T25.world(scratch, jar, "real")
    T, Inv, Fl = J("Trader"), J("Inv"), J("BzFill")
    A, Bb, Cc = T200.mkplayers(W)
    ua = A.pr.getUuid()
    sa = str(ua)
    fx.purse[sa] = 1000000
    J("BzConfirm").set(ua, 10 ** 12)
    iid, cheap = T200.pick(J)
    URL = JClass("java.net.URL")
    ucl = JClass("java.net.URLClassLoader")(JArray(URL)([JClass("java.io.File")(GEAR_JAR).toURI().toURL()]),
                                            JClass("java.lang.ClassLoader").getSystemClassLoader())
    fn = JClass("java.lang.Class").forName("com.skyy.gear.GearAugCntFn", True, ucl).getConstructor().newInstance()
    K.check(isinstance(fn, JClass("java.util.function.Function")), "R the real SkyyGear 0.3.59 GearAugCntFn loads (%s)" % os.path.basename(GEAR_JAR))
    E.br.put("gear:fn:augCount", fn)
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    BD, BA, BS = JClass("org.bson.BsonDocument"), JClass("org.bson.BsonArray"), JClass("org.bson.BsonString")

    def gear(q, *codes):
        a = BA()
        for c in codes:
            a.add(BS(c))
        return IS(iid, q).withMetadata(BD("SkyyGear", BD("aug", a)))
    two, none = gear(1, "Tempo:2", "", "Guard:1"), gear(1, "", "")
    K.check(int(fn.apply(two)) == 2 and int(fn.apply(none)) == 0 and int(fn.apply(IS(iid, 1))) == 0,
            "R the real augCount: 2 occupied entries = 2, an empty list = 0, a plain stack = 0")
    K.check(int(Inv.augs(two)) == 2 and int(Inv.augs(none)) == 0, "R Inv.augs through the bridge = the real answers")
    st = A.inv.getStorage()
    for k in range(int(st.getCapacity())):
        st.setItemStackForSlot(JShort(k), None)
    st.setItemStackForSlot(JShort(0), IS(iid, 3))
    st.setItemStackForSlot(JShort(1), two)
    st.setItemStackForSlot(JShort(2), none)
    K.check(int(Inv.count(A.pl, iid)) == 4 and int(Inv.augHeld(A.pl, iid)) == 1, "R held 4 sellable (3 plain + 1 empty-aug), 1 augmented")
    p0 = fx.purse[sa]
    w = int(Fl.quote(A.pl, ua, iid, 4, False))
    r = T.sell(A.pl, ua, "Alice", iid, 0)
    left = st.getItemStack(JShort(1))
    K.check(bool(r.ok) and int(r.qty) == 4 and int(r.coins) == w and fx.purse[sa] == p0 + w and left is not None and not bool(left.isEmpty())
            and int(fn.apply(left)) == 2 and int(Inv.count(A.pl, iid)) == 0,
            "R Trader.sell all with the REAL Gear answer: 4 sold for %d, the augmented piece kept with its 2 augments (%s)" % (w, r.msg))
    K.check(str(r.msg).count(NOTE) == 1, "R ... one note: %s" % r.msg)
    E.br.remove("gear:fn:augCount")
    K.save()


# ------------------------------------------------------------------------------------------------------------------- D
def run_live(out, jar, scratch, home):
    K = HK.Child(out)
    other = home.rstrip("\\/") + "_old"
    shutil.copytree(home, other)
    hs = {}
    for tag, jp, h in (("old", OLD_JAR, other), ("new1", jar, home), ("new2", jar, home)):
        dst = os.path.join(scratch, "live_%s.json" % tag)
        p = subprocess.run([sys.executable, T25.__file__, "--start", jp, h, dst], capture_output=True, text=True)
        K.check(p.returncode == 0, "D %s start ran: %s" % (tag, p.stderr[-300:]))
        hs[tag] = json.load(open(dst)) if os.path.isfile(dst) else {}
    strip = lambda t: dict((k, v) for k, v in t.items() if not k.startswith("config-history") and k != "trades.log")
    da = sorted(k for k in set(strip(hs["old"])) | set(strip(hs["new1"])) if strip(hs["old"]).get(k) != strip(hs["new1"]).get(k))
    K.check(not da, "D the 0.2.7 start = the 0.2.6 start on the live data (files that differ: %s)" % da)
    K.check(hs["new1"] == hs["new2"], "D a second 0.2.7 start writes nothing (%s)" % sorted(k for k in set(hs["new1"]) | set(hs["new2"]) if hs["new1"].get(k) != hs["new2"].get(k))[:5])
    K.save()


if __name__ == "__main__":
    if "--dump-consts" in sys.argv:
        k = sys.argv.index("--dump-consts")
        T25._dump_consts(sys.argv[k + 1], sys.argv[k + 2])
        sys.exit(0)
    HK.run(name="SkyyBazaar", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("catalog", run_catalog), ("page", run_page), ("tab", run_tab), ("aug", run_aug), ("real", run_real), ("live", run_live)],
           live=(LIVE, "Skyy_SkyyBazaar"), script=__file__)
