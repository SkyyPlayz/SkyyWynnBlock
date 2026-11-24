"""Harness for SkyyBazaar 0.2.8 (the Market tab's order ops: bid / ask / cancel + the opt-in read lines; tools/bazaar_0_2_8_patch.py).
Build first:
    python tools/bazaar_0_2_8_patch.py && python SkyyBazaar/build_skyybazaar_0.2.8.py --with SkyyCollections/SkyyCollections-0.2.36.jar
    python SkyyBazaar/test_skyybazaar_0.2.8.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, -Xverify:all, tools/harness_kit.py + the 0.2.0 stand-in engine; every new code path is EXECUTED):
  S     static   the patch re-runs to identical bytes; line endings kept; no new command / system / class / bridge key / setting
  A     verify   every class loads + initialises
  C     compare  0.2.7 -> 0.2.8 (EXPECT below: BzPage's 4 static checks + BzTabFn; no class added)
  K     catalog  every Catalog constant = 0.2.6's (no price / tab / product change)
  P     page     the 0.2.5 page phase re-run on the 0.2.8 jar (BUY ORDER / SELL OFFER steps now call the static checks - same results)
  T     tab      the 0.2.6 Market-tab phase re-run (a 7-argument read + buy / sell / claim unchanged)
  G / R augments the 0.2.7 phases re-run (augmented stacks kept by every sell path; the real SkyyGear augCount)
  O     orders   THE NEW OPS through bazaar:fn:tabact.apply on TWIN players: Alice by the bridge, Bob by the Bazaar page's own clicks (the step
                 CONFIRM / MY ORDERS cancel) - the same coins held / items held / order (side, qty, price) / refund and the same words; the
                 read's 8th argument (o| ids, n| chips = BzPage.price0 / stepBand / all0, w| = whyStep + the confirm flag), a 7-argument
                 read has none of them; EVERY refusal moves nothing (double click, total changed, price over / under the band, crossing the
                 other side, not enough coins, not enough items, extra-data stacks, min total, max open orders, book off, orders off, profile
                 switch, profile busy, closing, unknown item / op / junk, another profile's order, a cancelled order again); the
                 Confirm-buys-from ask (first press asks, the same press places, another price / profile / an expired ask asks again);
                 a cancel with a full inventory leaves the items as a claim (nothing lost); coins + items CONSERVED after every step
  X     crash    a simulated server stop at every journal step of a bid (1-5) and an ask (6-9) placed THROUGH THE BRIDGE, then a restart
                 (BzBook.load = the replay): every coin and item accounted for (step 2 = the 0.2.0 accepted window, as for the page)
  D     live     scratch COPIES of the live NewBetaTest Skyy_SkyyBazaar: the 0.2.8 start = the 0.2.7 start, a second 0.2.8 start writes nothing
  AA    audit    engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, subprocess, importlib.util, json, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.2.8"
PKG = "com.skyy.bazaar."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyBazaar-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyBazaar-0.2.7.jar")
GEN = os.path.join(HERE, "build_skyybazaar_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyybazaar_0.2.7.py")
PATCH = os.path.join(ROOT, "tools", "bazaar_0_2_8_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "mkt1", "bz")))
LIVE = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyBazaar")
EXPECT = {"CfgFn": ["~m opExport"], "CfgRows": ["~m header"],
          "BzPage": ["+m all0", "+m lim", "+m price0", "+m whyStep", "~m limits", "~m stepAll", "~m stepPrice", "~m stepWhy"],
          "BzTabFn": ["+m la", "+m no", "+m ordAct", "+m read", "+m read0", "-m read", "-m read0", "~m act", "~m apply"], "SkyyBazaarPlugin": ["~m setup"]}
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


T27 = tmod(os.path.join(HERE, "test_skyybazaar_0.2.7.py"), "tbz027")
T26, T25 = T27.T26, T27.T25


# ------------------------------------------------------------------------------------------------------------------- S
def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.count('VERSION = "0.2.8"') == 1 and g.startswith('"""SkyyBazaar 0.2.8'), "S version + header")
    for w in ("registerSystem(", "registerCommand(", "CFG.row(", "Server Setup", "pool.makeClass(", "bridge().put(", "bridge().remove("):
        K.check(g.count(w) == o.count(w), "S no new %s (%d)" % (w, g.count(w)))
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    sw = g[g.index("public String stepWhy("):g.index("public String stepWhy(") + 300]
    K.check("return whyStep(u, p, id, st, q, pr, lim, now, this.oQty, this.oPrice);" in sw, "S the page's stepWhy IS whyStep (one body)")
    K.check("return all0(u, p, id, this.oSide, price);" in g and "String[] r = price0(id, this.oSide == 2 ? 0 : 1, k, now);" in g and "  return lim(p, u, id);" in g,
            "S stepAll / stepPrice / limits call the static bodies")
    oa = g[g.index("public static String ordAct("):g.index("public static String act(")]
    K.check(oa.count("@PKG@.BzOrders.place(") == 1 and oa.count("@PKG@.BzOrders.cancelClaim(") == 1 and "Coins.take" not in oa and "Inv.take" not in oa
            and "takePlain" not in oa, "S ordAct moves coins / items ONLY through BzOrders.place / cancelClaim (no direct take)")
    K.save()


def run_catalog(out, jar, scratch, home):
    T27.run_catalog(out, jar, scratch, home)


def run_page(out, jar, scratch, home):
    T25.run_page(out, jar, scratch, home)


def run_tab(out, jar, scratch, home):
    T26.run_tab(out, jar, scratch, home)


def run_aug(out, jar, scratch, home):
    T27.run_aug(out, jar, scratch, home)


def run_real(out, jar, scratch, home):
    T27.run_real(out, jar, scratch, home)


# ------------------------------------------------------------------------------------------------------------------- O
def run_orders(out, jar, scratch, _home):
    from jpype import JClass, JString, JShort, JArray
    K = HK.Child(out)
    T200, T20, W, E, J, fx, home = T25.world(scratch, jar, "ord")
    C, M, Bk, Od, Fl, T, CF, TF, OC, Pg, Cl = (J("Catalog"), J("Market"), J("BzBook"), J("BzOrders"), J("BzFill"), J("Trader"), J("BzConfirm"),
                                               J("BzTabFn"), J("BzOrdCfg"), J("BzPage"), J("BzClaim"))
    A, Bb, Cc = T200.mkplayers(W)
    ua, ub, uc = A.pr.getUuid(), Bb.pr.getUuid(), Cc.pr.getUuid()
    sa, sb, sc = str(ua), str(ub), str(uc)
    for u in (sa, sb, sc):
        fx.purse[u] = 1000000
    iid, cheap = T200.pick(J)
    ids = [iid]
    filler = [str(p.id) for p in C.all() if str(p.id) not in (iid, cheap) and bool(C.usable(str(p.id)))][0]
    mm = T200.MMFlow(J)
    base = {}
    OA = JClass("java.lang.Object[]")
    Int, Lng = JClass("java.lang.Integer"), JClass("java.lang.Long")
    now = lambda: int(JClass("java.lang.System").currentTimeMillis())

    def rebase():
        mm.drain()
        c1, i1 = T200.totals(J, fx, [A, Bb, Cc], ids)
        base["c"], base["i"] = c1 + mm.coins, i1[iid] - mm.items.get(iid, 0)

    def conserved(what):
        mm.drain()
        c1, i1 = T200.totals(J, fx, [A, Bb, Cc], ids)
        K.check(c1 + mm.coins == base["c"] and i1[iid] - mm.items.get(iid, 0) == base["i"],
                "O CONSERVED after %s: coins %d (+ market %d) vs %d, items %d (- market %d) vs %d" % (what, c1, mm.coins, base["c"], i1[iid], mm.items.get(iid, 0), base["i"]))

    def args(*xs):
        a = OA(len(xs))
        for i, x in enumerate(xs):
            if isinstance(x, bool) or type(x) is not int:
                a[i] = x
            elif abs(x) > 2000000000:
                a[i] = Lng.valueOf(x)
            else:
                a[i] = Int.valueOf(x)
        return a
    RD, AC = TF(0), TF(1)
    TF.TEST_ANY_THREAD = True

    def read(u, sel, omax=None, oside=None, oq=None, op=None, cat=""):
        xs = [u, JString(cat), JString(""), JString(sel), 0, 8, 0]
        if omax is not None:
            xs += [omax, -1 if oside is None else oside]
            xs += [Lng.valueOf(-1 if oq is None else oq), Lng.valueOf(-1 if op is None else op)]
        r = RD.apply(args(*xs))
        return None if r is None else str(r)

    def act(u, tok, op, arg, clear=True):
        if clear:
            TF.LASTOP.clear()
        r = AC.apply(args(u, JString(tok), JString(op), JString(arg)))
        return None if r is None else str(r)

    def lines(s, k):
        return [l.split("|") for l in s.split("\n") if l.startswith(k + "|")]

    def open_of(u, side=None):
        return [o for o in Bk.ORDERS.values() if bool(o.open()) and str(o.uuid) == str(u) and (side is None or int(o.side) == side)]

    CF.set(ua, 10 ** 12)
    CF.set(ub, 10 ** 12)
    CF.set(uc, 10 ** 12)
    mt = int(OC.minTotal())
    S, Bp = int(M.quote(iid, 1, False)), int(M.quote(iid, 1, True))
    stk = int(T.stack(iid))
    nm = str(C.get(iid).name)
    tokA, tokB = str(Bk.pkey(ua)), str(Bk.pkey(ub))
    # ---------------------------------------------------------------- Bob's page (the twin): the Market > Bazaar page, product selected
    E.br.put("hub:last:" + sb, JClass("java.util.concurrent.ConcurrentHashMap")())
    J("BzHubOpen").register()
    J("HubBar").open(Bb.pr, ub, "market", "bazaar")
    E.pump(Bb)

    def click(a, **kw):
        pg_ = Bb.pm.getCustomPage()
        pg_.cfShown = 0
        pg_.xDrawn = 0
        d = {"a": a, "@BzFind": "", "@BzCf": ""}
        d.update(kw)
        Bb.pm.handleLegacyCustomPageEvent(Bb.ref, Bb.st, E.CPE(E.CPT.Data, json.dumps(d)))
        E.pump(Bb)
        return Bb.pm.getCustomPage()
    pg = Bb.pm.getCustomPage()
    K.check(pg is not None and str(pg.getClass().getSimpleName()) == "BzPage", "O Bob's twin is the Bazaar page itself")
    pg.sel = iid
    pg.cat = C.get(iid).cat
    pg.oSide = -1

    def page_place(st, q, pr):
        click("qbid" if st == 2 else "qask")
        click("xupd", **{"@BzOQ": str(q), "@BzOP": str(pr)})
        return click("xok:%d" % st, **{"@BzOQ": str(q), "@BzOP": str(pr)})

    def same_words(bridge, page_info, ok):
        m = str(page_info)
        want = ("+" if ok else "-") + (m[:1].upper() + m[1:]) + ("" if m.endswith(".") else ".")
        return bridge == want

    # ---------------------------------------------------------------- READ: 7 args = 0.2.7's lines; the opt-in 8th argument
    rebase()
    r7 = read(ua, iid)
    K.check(r7 is not None and not lines(r7, "n") and not lines(r7, "w"), "O a 7-argument read has no n| / w| lines (= 0.2.7)")
    p1 = Od.place(Cc.pl, uc, "Cara", iid, 0, S + 1, max(2, mt // (S + 1) + 1))
    K.check(bool(p1.ok), "O Cara has a buy order at S+1 (%s)" % p1.msg)
    r7 = read(uc, iid)
    K.check(all(len(f) == 7 for f in lines(r7, "o")) and len(lines(r7, "o")) == 1, "O ... a 7-argument read: o| lines keep their 7 fields (SkyyMenu 0.3.70 splits by 7)")
    r8 = read(uc, iid, omax=10)
    o8 = lines(r8, "o")
    K.check(len(o8) == 1 and len(o8[0]) == 8 and o8[0][7] == str(open_of(uc)[0].id), "O the 8-argument read: o| + the ORDER ID (%s)" % o8)
    nl = dict((f[1], f) for f in lines(r8, "n"))
    tnow = now()
    for sd in (0, 1):
        bd = [int(x) for x in Pg.stepBand(iid, sd, tnow)]
        b0, b1 = [str(x) for x in Pg.price0(iid, sd, 0, tnow)], [str(x) for x in Pg.price0(iid, sd, 1, tnow)]
        allq = int(Pg.all0(uc, Cc.pl, iid, 2 if sd == 0 else 3, int(b0[0]) if b0[0] else 0))
        f = nl.get(str(sd))
        K.check(f is not None and f[2:4] == [str(bd[0]), str(bd[1])] and f[4] == (b0[0] or "-1") and f[5] == b0[1] and f[6] == (b1[0] or "-1")
                and f[7] == b1[1] and f[8] == str(allq), "O n|%d = stepBand %s, Best %s (%r), Beat %s (%r), all %d: %s" % (sd, bd[:2], b0[0], b0[1], b1[0], b1[1], allq, f))
    K.check(nl["0"][4] == str(S + 1) and nl["0"][6] == str(S + 2), "O ... buy side: Best = Cara's S+1, Beat by 1 = S+2")
    pg = click("qbid")
    K.check(str(pg.oPrice) == nl["0"][4], "O ... = what Bob's page sets on BUY ORDER (Best price %s)" % pg.oPrice)
    pg = click("xback")
    nb = max(2, mt // (S + 2) + 1)
    rw = read(ua, iid, omax=4, oside=0, oq=nb, op=S + 2)
    w = lines(rw, "w")[0]
    K.check(w[1:6] == ["0", str(nb), str(S + 2), str(nb * (S + 2)), ""] and w[6] == "0", "O w| a placeable buy order: no reason, total, no confirm (%s)" % w)
    rw = read(ua, iid, omax=4, oside=0, oq=nb, op=Bp + 5)
    w = lines(rw, "w")[0]
    wy = str(Pg.whyStep(ua, A.pl, iid, 2, nb, Bp + 5, Pg.lim(A.pl, ua, iid), now(), str(nb), str(Bp + 5)))
    K.check(w[5] == wy and w[5].startswith("Too high"), "O w| over the band = whyStep's words (%s)" % w[5])
    rw = read(ua, iid, omax=4, oside=1, oq=None, op=None)
    w = lines(rw, "w")[0]
    K.check(w[5] == "Type an amount - like 64 or 2k", "O w| no amount yet = the page's 'Type an amount' (%s)" % w[5])
    CF.set(ua, 1)
    w = lines(read(ua, iid, omax=4, oside=0, oq=nb, op=S + 2), "w")[0]
    K.check(w[6] == "1", "O w| the confirm flag follows Confirm-buys-from (%s)" % w)
    CF.set(ua, 10 ** 12)
    conserved("reads")
    # ---------------------------------------------------------------- BID twin: Alice by the bridge, Bob by his page
    rebase()
    pa0, pb0 = fx.purse[sa], fx.purse[sb]
    ra = act(ua, tokA, "bid", "%s|%d|%d|%d" % (iid, nb, S + 2, nb * (S + 2)))
    pg = page_place(2, nb, S + 2)
    oa_, ob_ = open_of(ua, 0), open_of(ub, 0)
    K.check(ra.startswith("+Placed a buy order") and fx.purse[sa] == pa0 - nb * (S + 2), "O BID through the bridge holds exactly %d coins: %s" % (nb * (S + 2), ra))
    K.check(fx.purse[sb] == pb0 - nb * (S + 2) and str(pg.info).startswith("placed a buy order"), "O ... the page twin holds the same: %s" % pg.info)
    K.check(len(oa_) == 1 and len(ob_) == 1 and (int(oa_[0].qty), int(oa_[0].price)) == (int(ob_[0].qty), int(ob_[0].price)) == (nb, S + 2),
            "O ... the same order (side 0, %d @ %d) on both" % (nb, S + 2))
    K.check(same_words(ra, pg.info, True), "O ... word for word the page's result line")
    conserved("bid twin")
    # ---------------------------------------------------------------- ASK twin
    for P_, u_ in ((A, sa), (Bb, sb)):
        T200.clear_inv(P_)
        T200.give(P_, iid, stk, 0)
        T200.give(P_, iid, 3, 1)
        fx.bags[(u_, iid)] = 2
    rebase()
    no_ = max(4, mt // (Bp - 1) + 1)
    assert no_ <= stk + 5, (no_, stk)
    ra = act(ua, tokA, "ask", "%s|%d|%d|%d" % (iid, no_, Bp - 1, no_ * (Bp - 1)))
    pg = page_place(3, no_, Bp - 1)
    ha = int(Od.countPlain(A.pl, iid)) + fx.bags[(sa, iid)]
    hb = int(Od.countPlain(Bb.pl, iid)) + fx.bags[(sb, iid)]
    oa_, ob_ = open_of(ua, 1), open_of(ub, 1)
    K.check(ra.startswith("+Placed a sell offer") and ha == stk + 5 - no_ and hb == ha and str(pg.info).startswith("placed a sell offer"),
            "O ASK through the bridge holds %d items, the page twin the same (left %d / %d): %s" % (no_, ha, hb, ra))
    K.check(len(oa_) == 1 and len(ob_) == 1 and (int(oa_[0].qty), int(oa_[0].price)) == (int(ob_[0].qty), int(ob_[0].price)) == (no_, Bp - 1)
            and same_words(ra, pg.info, True), "O ... the same offer (%d @ %d), word for word" % (no_, Bp - 1))
    conserved("ask twin")
    # ---------------------------------------------------------------- CANCEL twin (the bid: coins back; the ask: items back)
    for side in (0, 1):
        rebase()
        pa0, pb0 = fx.purse[sa], fx.purse[sb]
        ia0 = int(E.count(A, iid)) + fx.bags[(sa, iid)]
        ib0 = int(E.count(Bb, iid)) + fx.bags[(sb, iid)]
        oid_a = str(open_of(ua, side)[0].id)
        oid_b = str(open_of(ub, side)[0].id)
        r8 = read(ua, iid, omax=10)
        K.check(oid_a in [f[7] for f in lines(r8, "o")], "O the read lists the order id the cancel uses (%s)" % oid_a)
        ra = act(ua, tokA, "cancel", oid_a)
        pg = Bb.pm.getCustomPage()
        pg.cellsO = JArray(JString)([oid_b])
        pg.ordRow(Bb.pl, ub, "Bob", "ocan:0")
        da = (fx.purse[sa] - pa0, int(E.count(A, iid)) + fx.bags[(sa, iid)] - ia0)
        db = (fx.purse[sb] - pb0, int(E.count(Bb, iid)) + fx.bags[(sb, iid)] - ib0)
        K.check(ra.startswith("+Cancelled your") and da == db and (da[0] > 0 if side == 0 else da[1] > 0) and not open_of(ua, side) and not open_of(ub, side),
                "O CANCEL %s through the bridge = the page's MY ORDERS cancel: back %s vs %s: %s" % ("buy order" if side == 0 else "sell offer", da, db, ra))
        K.check(same_words(ra, pg.info, True), "O ... word for word (%s)" % pg.info)
        r2 = act(ua, tokA, "cancel", oid_a)
        K.check(r2 == "-That order is not open any more." and fx.purse[sa] - pa0 == da[0], "O ... the same cancel again = refused, nothing paid twice (%s)" % r2)
        conserved("cancel twin %d" % side)
    # ---------------------------------------------------------------- refusals: nothing moves
    rebase()
    pa0 = fx.purse[sa]
    n_open = len(open_of(ua))

    def nothing(what, r, prefix):
        K.check(r is not None and r.startswith(prefix) and fx.purse[sa] == pa0 and len(open_of(ua)) == n_open, "O %s = refused, nothing moved: %s" % (what, r))
    good = "%s|%d|%d|%d" % (iid, nb, S + 2, nb * (S + 2))
    nothing("a total that is not price x amount", act(ua, tokA, "bid", "%s|%d|%d|%d" % (iid, nb, S + 2, nb * (S + 2) - 1)), "=The total changed")
    r = act(ua, tokA, "bid", "%s|%d|%d|%d" % (iid, nb, Bp + 5, nb * (Bp + 5)))
    nothing("a price over the band (= the page's words)", r, "-Too high")
    r = act(ua, tokA, "bid", "%s|%d|%d|%d" % (iid, nb, S, nb * S))
    nothing("a price at / under the instant sell", r, "-Too low")
    r = act(ua, tokA, "ask", "%s|%d|%d|%d" % (iid, 2, Bp, 2 * Bp))
    nothing("an offer at the instant buy", r, "-Too high")
    nothing("an unknown item", act(ua, tokA, "bid", "Not_An_Item|1|5|5"), "-That item is not on the Bazaar")
    nothing("amount 0", act(ua, tokA, "bid", "%s|0|%d|0" % (iid, S + 2)), "=Pick an amount and a price")
    nothing("junk numbers", act(ua, tokA, "bid", "%s|x|y|z" % iid), "=Pick an amount and a price")
    nothing("3 fields", act(ua, tokA, "bid", "%s|1|5" % iid), "-Unknown Bazaar action")
    nothing("an empty cancel", act(ua, tokA, "cancel", ""), "-Pick one of your orders")
    nothing("a cancel of no order", act(ua, tokA, "cancel", "nope"), "-That order is not open any more")
    nothing("another op", act(ua, tokA, "steal", "x|1|1"), "-Unknown Bazaar action")
    nothing("a stale profile key", act(ua, "someone-else", "bid", good), "=Your profile changed")
    E.br.put("profile:busy:" + sa, JClass("java.lang.Boolean").TRUE)
    nothing("profile:busy", act(ua, tokA, "bid", good), "-Your profile is still loading")
    E.br.remove("profile:busy:" + sa)
    T.CLOSED = True
    nothing("a closing server", act(ua, tokA, "bid", good), "-The Bazaar is closing")
    nothing("a closing server (cancel)", act(ua, tokA, "cancel", "x"), "-The Bazaar is closing")
    T.CLOSED = False
    Bk.BROKEN = True
    nothing("the book off (BROKEN)", act(ua, tokA, "bid", good), "-The order book could not be read")
    Bk.BROKEN = False
    OC.ON = False
    nothing("player orders switched off", act(ua, tokA, "bid", good), "-Player orders are switched off")
    OC.ON = True
    small = max(1, (mt - 1) // (S + 2))
    if small * (S + 2) < mt:
        nothing("under the minimum total", act(ua, tokA, "bid", "%s|%d|%d|%d" % (iid, small, S + 2, small * (S + 2))), "-An order must be worth at least")
    else:
        K.notes.append("O the minimum-total refusal not reachable with this product (min %d < one at %d) - BzOrders.check's own rule, unchanged since 0.2.0" % (mt, S + 2))
    keep = fx.purse[sa]
    fx.purse[sa] = nb * (S + 2) - 1
    pa0 = fx.purse[sa]
    rebase()
    nothing("not enough coins", act(ua, tokA, "bid", good), "-You need ")
    fx.purse[sa] = keep
    pa0 = keep
    rebase()
    held = int(Od.countPlain(A.pl, iid)) + fx.bags[(sa, iid)]
    nothing("an offer of more than held", act(ua, tokA, "ask", "%s|%d|%d|%d" % (iid, held + 1, Bp - 1, (held + 1) * (Bp - 1))), "-You have %d to offer" % held)
    # crossing the other side: Cara offers at X, a bid at X is refused (the stale best price)
    T200.give(Cc, iid, max(no_, 4), 0)
    rx = Od.place(Cc.pl, uc, "Cara", iid, 1, S + 4, max(no_, 4))
    K.check(bool(rx.ok), "O Cara offers at S+4 (%s)" % rx.msg)
    rebase()
    nothing("a buy order at the lowest sell offer (the price moved)", act(ua, tokA, "bid", "%s|%d|%d|%d" % (iid, nb, S + 4, nb * (S + 4))), "-Too high")
    # a double click: the same press twice within 350 ms places ONE order
    a_ = args(ua, JString(tokA), JString("bid"), JString(good))
    TF.LASTOP.clear()
    r1, r2 = str(AC.apply(a_)), str(AC.apply(a_))
    K.check(r1.startswith("+Placed") and r2 == "=One moment." and fx.purse[sa] == pa0 - nb * (S + 2) and len(open_of(ua)) == n_open + 1,
            "O a DOUBLE CLICK places once (%s / %s)" % (r1[:40], r2))
    conserved("double click")
    # another profile's order: Bob's / Alice on another profile
    rebase()
    ob = Od.place(Bb.pl, ub, "Bob", iid, 0, S + 2, nb)
    oid_b = str(open_of(ub, 0)[0].id)
    pb0 = fx.purse[sb]
    r = act(ua, tokA, "cancel", oid_b)
    K.check(r.startswith("-That order belongs to another profile") and open_of(ub, 0) and fx.purse[sb] == pb0, "O cancelling SOMEONE ELSE's order = refused (%s)" % r)
    oid_a = str(open_of(ua, 0)[0].id)
    fx.prof[sa] = sa + "-p2"
    tokA2 = str(Bk.pkey(ua))
    r = act(ua, tokA2, "cancel", oid_a)
    r_old = act(ua, tokA, "cancel", oid_a)
    del fx.prof[sa]
    K.check(r.startswith("-That order belongs to another profile") and r_old.startswith("=Your profile changed") and open_of(ua, 0),
            "O on ANOTHER PROFILE the order cannot be cancelled; the old profile's key is stale (%s / %s)" % (r, r_old))
    r8 = read(ua, iid, omax=10)
    K.check(oid_a in [f[7] for f in lines(r8, "o")], "O ... back on the profile it is listed again")
    conserved("other profile")
    # max open orders
    mo = int(OC.maxOpen())
    rebase()
    placed = 0
    while len(open_of(ua)) < mo and placed < 60:
        rr = Od.place(A.pl, ua, "Alice", iid, 0, S + 2, nb)
        placed += 1
        if not bool(rr.ok):
            break
    pa0 = fx.purse[sa]
    n_open = len(open_of(ua))
    K.check(n_open >= mo, "O Alice reached the most open orders (%d of %d)" % (n_open, mo))
    nothing("the most open orders (%d)" % mo, act(ua, tokA, "bid", good), "-You have %d open orders" % mo)
    K.check(len(lines(read(ua, iid, omax=50), "o")) == min(mo, 50) and len(lines(read(ua, iid), "o")) == 4,
            "O the 8th argument lists up to its count (%d), the 7-argument read 4" % min(mo, 50))
    for o in open_of(ua):
        act(ua, tokA, "cancel", str(o.id))
    conserved("max open")
    # ---------------------------------------------------------------- Confirm-buys-from: the page's ask, two presses
    rebase()
    pa0 = fx.purse[sa]
    n_open = len(open_of(ua))
    CF.set(ua, 1)
    r1 = act(ua, tokA, "bid", good)
    K.check(r1.startswith("=Place a buy order holding") and "Press Buy order again within 10 s" in r1 and fx.purse[sa] == pa0, "O Confirm-buys-from: the first press asks (%s)" % r1)
    other = "%s|%d|%d|%d" % (iid, nb, S + 3, nb * (S + 3))
    r2 = act(ua, tokA, "bid", other)
    K.check(r2.startswith("=Place a buy order holding") and fx.purse[sa] == pa0, "O ... another price asks again, nothing placed")
    fx.prof[sa] = sa + "-p2"
    tokA2 = str(Bk.pkey(ua))
    r3 = act(ua, tokA2, "bid", other)
    del fx.prof[sa]
    r4 = act(ua, tokA, "bid", other)
    K.check(r3.startswith("=Place a buy order holding") and r4.startswith("=Place a buy order holding") and fx.purse[sa] == pa0,
            "O ... the ask belongs to the PROFILE it was made on (another profile asks again, and back asks again)")
    TF.ARM.put(ua, JString(str(TF.ARM.get(ua)).rsplit("#", 1)[0] + "#" + str(now() - 1)))
    r5 = act(ua, tokA, "bid", other)
    K.check(r5.startswith("=Place a buy order holding") and fx.purse[sa] == pa0, "O ... an EXPIRED ask (over 10 s) asks again")
    act(ua, tokA, "claim", "")
    r6 = act(ua, tokA, "bid", other)
    K.check(r6.startswith("=Place a buy order holding"), "O ... any other op in between drops the ask")
    r7_ = act(ua, tokA, "bid", other)
    K.check(r7_.startswith("+Placed a buy order") and fx.purse[sa] == pa0 - nb * (S + 3) and len(open_of(ua)) == n_open + 1,
            "O ... the SAME press again within 10 s places it (%s)" % r7_)
    CF.set(ua, 10 ** 12)
    Od.cancelAll(True, "harness")
    for P_, u_ in ((A, ua), (Bb, ub), (Cc, uc)):
        Cl.claimAll(P_.pl, u_, "x")
    # ---------------------------------------------------------------- a cancel with a FULL inventory: the items wait as a claim (nothing lost)
    T200.clear_inv(A)
    fx.bags[(sa, iid)] = 0
    T200.give(A, iid, no_, 0)
    rebase()
    r = act(ua, tokA, "ask", "%s|%d|%d|%d" % (iid, no_, Bp - 1, no_ * (Bp - 1)))
    K.check(r.startswith("+Placed a sell offer") and int(E.count(A, iid)) == 0, "O an offer of all %d (%s)" % (no_, r[:50]))
    for sl in range(int(A.inv.getStorage().getCapacity())):
        T200.give(A, filler, 1, sl)
    hbar = A.inv.getHotbar()
    for sl in range(int(hbar.getCapacity())):
        hbar.setItemStackForSlot(JShort(sl), JClass("com.hypixel.hytale.server.core.inventory.ItemStack")(filler, 1))
    oid = str(open_of(ua, 1)[0].id)
    r = act(ua, tokA, "cancel", oid)
    waiting = [c for c in Bk.CLAIMS.values() if bool(c.open()) and str(c.uuid) == sa and int(c.kind) == 1]
    K.check(r.startswith("+Cancelled your sell offer") and "waiting in MY ORDERS" in r and waiting and int(waiting[0].amount) == no_,
            "O a cancel with a FULL inventory: the %d items wait as a claim (%s)" % (no_, r))
    conserved("cancel, full inventory")
    T200.clear_inv(A)
    r = act(ua, tokA, "claim", "")
    K.check(r.startswith("+Claimed") and int(E.count(A, iid)) == no_, "O ... Claim all brings them back (%s)" % r)
    conserved("claim after full")
    TF.TEST_ANY_THREAD = False
    K.check(act(ua, tokA, "bid", good) is None and read(ua, iid, omax=4) is None, "O NOT the world thread: the new ops and the 8-argument read = null")
    K.notes.append("O %s (%s): S %d, B %d, bid %d x %d, ask %d x %d, min total %d, max open %d" % (iid, nm, S, Bp, nb, S + 2, no_, Bp - 1, mt, int(OC.maxOpen())))
    K.save()


# ------------------------------------------------------------------------------------------------------------------- X
def run_crash(out, jar, scratch, _home):
    from jpype import JClass, JString
    K = HK.Child(out)
    T200, T20, W, E, J, fx, home = T25.world(scratch, jar, "crash")
    C, M, Bk, Od, Cl, TF, CF, OC = J("Catalog"), J("Market"), J("BzBook"), J("BzOrders"), J("BzClaim"), J("BzTabFn"), J("BzConfirm"), J("BzOrdCfg")
    A, Bb, Cc = T200.mkplayers(W)
    ua, ub, uc = A.pr.getUuid(), Bb.pr.getUuid(), Cc.pr.getUuid()
    for u in (ua, ub, uc):
        fx.purse[str(u)] = 10000000
        CF.set(u, 10 ** 12)
    iid, _ch = T200.pick(J)
    S, Bp = int(M.quote(iid, 1, False)), int(M.quote(iid, 1, True))
    mt = int(OC.minTotal())
    Paths = JClass("java.nio.file.Paths")
    players = [A, Bb, Cc]
    mm = T200.MMFlow(J)
    OA = JClass("java.lang.Object[]")
    AC = TF(1)
    TF.TEST_ANY_THREAD = True

    def act(u, op, arg):
        TF.LASTOP.clear()
        a = OA(4)
        a[0], a[1], a[2], a[3] = u, JString(str(Bk.pkey(u))), JString(op), JString(arg)
        return str(AC.apply(a))
    qb = max(3, mt // (S + 2) + 1)
    qa = max(25, mt // (Bp - 2) + 1)
    for step in list(range(1, 10)):
        Od.cancelAll(True, "harness")
        for P_, u_ in ((A, ua), (Bb, ub), (Cc, uc)):
            Cl.claimAll(P_.pl, u_, "x")
        T200.clear_inv(Bb)
        T200.give(Bb, iid, 40, 0)
        fx.bags[(str(ub), iid)] = 5
        mm.drain()
        c0, i0 = T200.totals(J, fx, players, [iid])
        mm0c, mm0i = mm.coins, dict(mm.items)
        Bk.CRASH_AT = step
        if step <= 5:
            amt = qb * (S + 2)
            r = act(ua, "bid", "%s|%d|%d|%d" % (iid, qb, S + 2, amt))
        else:
            amt = qa
            r = act(ub, "ask", "%s|%d|%d|%d" % (iid, qa, Bp - 2, qa * (Bp - 2)))
        K.check(int(Bk.CRASH_AT) == -1 and r.startswith("-Something went wrong"), "CRASH %d through the bridge: the stop fired mid-order, the answer says so (%s)" % (step, r[:50]))
        Bk.load(Paths.get(home))          # THE RESTART: memory from disk + the journal replay
        mm.drain()
        c1, i1 = T200.totals(J, fx, players, [iid])
        dc = (c1 + (mm.coins - mm0c)) - c0
        di = (i1[iid] - (mm.items.get(iid, 0) - mm0i.get(iid, 0))) - i0[iid]
        if step == 2:
            K.check(dc == -amt and di == 0, "CRASH 2 (the 0.2.0 accepted window, as for the page: coins taken, TAKEN not written): exactly %d lost, none created (%d / %d)" % (amt, dc, di))
        else:
            K.check(dc == 0 and di == 0, "CRASH %d: after the restart every coin and item is accounted for (coins %+d, items %+d; recovered %d)" % (step, dc, di, int(Bk.RECOVERED)))
        K.check(not bool(Bk.BROKEN), "CRASH %d: the book loads" % step)
        for P_, u_ in ((A, ua), (Bb, ub), (Cc, uc)):
            Cl.claimAll(P_.pl, u_, "x")
        mm.drain()
        c2, i2 = T200.totals(J, fx, players, [iid])
        K.check(c2 + mm.coins == c1 + mm.coins and i2[iid] == i1[iid], "CRASH %d: claiming everything afterwards moves nothing out of thin air" % step)
    TF.TEST_ANY_THREAD = False
    K.save()


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
    K.check(not da, "D the 0.2.8 start = the 0.2.7 start on the live data (files that differ: %s)" % da)
    K.check(hs["new1"] == hs["new2"], "D a second 0.2.8 start writes nothing (%s)" % sorted(k for k in set(hs["new1"]) | set(hs["new2"]) if hs["new1"].get(k) != hs["new2"].get(k))[:5])
    K.save()


if __name__ == "__main__":
    if "--dump-consts" in sys.argv:
        k = sys.argv.index("--dump-consts")
        T25._dump_consts(sys.argv[k + 1], sys.argv[k + 2])
        sys.exit(0)
    HK.run(name="SkyyBazaar", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("catalog", run_catalog), ("page", run_page), ("tab", run_tab), ("aug", run_aug), ("real", run_real),
                   ("orders", run_orders), ("crash", run_crash), ("live", run_live)],
           live=(LIVE, "Skyy_SkyyBazaar"), script=__file__)
