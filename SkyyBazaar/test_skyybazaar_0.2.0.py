"""Harness for SkyyBazaar 0.2.0 = THE ORDER BOOK (research/Bazaar-Order-Book-Spec.md rounds R1 + R2; notes: tools/bazaar_0_2_0_patch.py).
Build first: python tools/bazaar_0_2_0_patch.py && python SkyyBazaar/build_skyybazaar_0.2.0.py

    python SkyyBazaar/test_skyybazaar_0.2.0.py [--jar <0.2.0 jar>] [--dir <folder inside tools/dev/scratch/>] [--keep] [--steps N]

Phases (fresh child JVMs, tools/harness_kit.py + tools/hub_tab_harness.py engine stand-ins; -Xverify:all everywhere; every new code path
is EXECUTED - nothing is only read):
  A     verify   every class loads + initialises
  C     compare  0.1.22 -> 0.2.0: exactly the expected classes / members differ, the 15 order book classes are added
  BOOK  the order book over stand-in players (real inventories), a stand-in SkyyCoins / SkySacks / SkyyProfiles bridge:
        setup files + keys; place bid / ask (inventory + the Void), every refusal (price band, too cheap, crossing, amount, min total,
        coins, items, switched off, profile busy, rebirth busy, open-order limit); instant buy / sell through the book (full, partial,
        book + market blended - the charge = BzFill.quote, the taker's own orders skipped, tax burned, demand untouched); claims (coins,
        items, full inventory -> the rest stays a row, twice = refused, the wrong profile refused); cancel (+ the page's cancel-claim),
        expiry by the tick, CLAIM ALL, the bridge keys, the join notice; two players; a profile switch; the admin book commands
  RB    the rebirth contract parsed by SkyyRebirth 0.3.6's OWN RbCheck (head / detail / closed / marketClear arithmetic): wouldclose
        before == closeall's work == wouldclose after "ok:0:0:<item claims>:0"; closeall twice (idempotent "ok:0"); the coin claims and the
        bid refunds paid into the purse; rebirthPayCoins OFF / the owner on another profile / no SkyyCoins -> err:blocked and nothing
        closed; bad keys; a broken book -> err:book / err:store
  CRASH a simulated crash at EVERY journal step (1-18 + the claim step 30), then a restart (BzBook.load = the replay): every coin and item
        accounted for, nothing duplicated; the one window the spec accepts (coins:fn:take answered yes, TAKEN not yet written: steps 2 /
        11) and the claim step 30 lose at most that amount and never create any
  FUZZ  conservation: N random steps (fixed seed; place / cancel / instant buy / sell with market legs / claim / claim all / expire /
        closeall / restart) - purses + bid escrow + open coin claims + tax burned + market-maker coin flow, and inventories + Void + ask
        escrow + open item claims + market-maker item flow, are CONSTANT after every step
  PAGE  the Market > Bazaar page built into REAL builders (kit 1.7 rules, the menu pattern): MY ORDERS (cards, CANCEL, CLAIM, CLAIM ALL,
        other profiles), the product detail with [BUY ORDER] [SELL OFFER] + "(N from offers)", the editor (steppers, BEST, MARKET, Enter,
        PLACE with the CONFIRM threshold, DISCARD), /bazaar orders + /bazaar claim
  LIVE  the jar on a scratch COPY of the live Skyy_SkyyBazaar (read-only source), started twice like setup(): book.properties + orders
        .properties created, pricing.properties only APPENDED (migrated.0.2.0), trades.log only appended (one MIGRATE-0.2.0 line),
        products / market / config / sounds / confirm byte-identical; the second start writes nothing
  AA    engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, random, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import hub_tab_harness as H

_argv = list(sys.argv)
_sp = importlib.util.spec_from_file_location("bz0120test", os.path.join(HERE, "test_skyybazaar_0.1.20.py"))
T20 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T20)       # LIVE_SAVES, fake_items, fake_coins, give
sys.argv = _argv

VERSION = "0.2.0"
OLD_VERSION = "0.1.22"
PKG = "com.skyy.bazaar."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyBazaar-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyBazaar-%s.jar" % OLD_VERSION)          # the SET pin
RB_JAR = os.path.join(ROOT, "SkyyRebirth", "SkyyRebirth-0.3.6.jar")       # the SET pin that parses the contract
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "bazaar02", "t")))
LIVE = os.path.join(T20.LIVE_SAVES, "Skyy_SkyyBazaar")
STEPS = int(HK.arg("--steps", "10000"))
ADDED = ["BzOrd", "BzClm", "BzOrdSort", "BzOrdCfg", "BzBook", "BzClaim", "BzOrders", "BzFill", "BzBookAdm", "BzOrdersCmd", "BzClaimCmd",
         "BzAdmBookCmd", "BzAdmBook1Cmd", "BzAdmBook2Cmd", "BzAdmBook3Cmd"]
EXPECT = {"BzAdminCmd": ["~c "], "BzCmd": ["~c "],                          # + the book / orders / claim subcommands
          "BzMarket": ["~m tiers"],                                          # TIER_SPEC re-baked from today's tools/tier_tags.py (sort only)
          "BzPage": ["+f amtF", "+f cellsC", "+f cellsO", "+f edF", "+f myTab", "+f oArmP", "+f oArmQ", "+f oArmShown", "+f oArmUntil",
                     "+f oPrice", "+f oQty", "+f oSide", "+m defPrice", "+m grp", "+m oqty", "+m ordAct", "+m ordEditor", "+m ordList", "+m ordRow", "+m tierSort",
                     "~c ", "~m amountAction", "~m buyClick", "~m evd", "~m handleDataEvent", "~m infoColor", "~m render"],
          "BzRebirthFn": ["~m apply"], "BzTick": ["~m run"],
          "CfgFile": ["~<clinit>", "~m init"], "CfgFn": ["~m opExport"], "CfgRows": ["+f DL2", "~<clinit>", "~m defLines", "~m header"],   # the kit: + orders.properties + 8 rows
          "SkyyBazaarPlugin": ["~m setup", "~m shutdown"],
          "Trader": ["+m merge", "+m mmBuy0", "+m mmSell0", "~m buy0", "~m buyC0", "~m buyN0", "~m sell0", "~m sellN0"]}
if "--expect-dump" in sys.argv:
    EXPECT = {}
U1, U2, U3 = "00000000-0000-4000-8000-0000000000b1", "00000000-0000-4000-8000-0000000000b2", "00000000-0000-4000-8000-0000000000b3"
CRASH_STEPS = list(range(1, 27)) + [30]      # 19-26 (review fix 2): a failed book write, then a crash around the refund / give-back


# ------------------------------------------------------------------------------------------------------------------- the world
def boot(scratch, label, jars):
    from jpype import JClass
    W = T20.boot2(scratch, [JAR] + list(jars), label)
    W.E.br = JClass(PKG + "HubBar").map()
    return W


class Fx(object):
    """the stand-in world: purses (SkyyCoins), bags (SkySacks), profiles (SkyyProfiles), busy flags - all on the real skyy.bridge"""

    def __init__(self, E, J):
        from jpype import JImplements, JOverride, JLong, JString
        self.E, self.J, self.purse, self.bags, self.prof = E, J, {}, {}, {}
        self.coins_mode = {"take": "ok", "add": "ok"}
        fx = self
        T20.fake_coins(E.br, self.purse)
        br = E.br

        @JImplements("java.util.function.Function")
        class SCount:
            @JOverride
            def apply(self, o):
                return JLong(fx.bags.get((str(o[0]), str(o[1])), 0))

        @JImplements("java.util.function.Function")
        class STake:
            @JOverride
            def apply(self, o):
                k, n = (str(o[0]), str(o[1])), int(o[2])
                h = fx.bags.get(k, 0)
                t = min(h, n)
                fx.bags[k] = h - t
                return JLong(t)

        @JImplements("java.util.function.Function")
        class SPut:
            @JOverride
            def apply(self, o):
                k, n = (str(o[0]), str(o[1])), int(o[2])
                fx.bags[k] = fx.bags.get(k, 0) + n
                return JLong(n)

        @JImplements("java.util.function.Function")
        class SCommit:
            @JOverride
            def apply(self, o):
                return JLong(int(o[2]))

        @JImplements("java.util.function.Function")
        class SAll:
            @JOverride
            def apply(self, o):
                m = JClass_("java.util.HashMap")()
                for (u, i), v in fx.bags.items():
                    if u == str(o) and v > 0:
                        m.put(i, JClass_("java.lang.Long").valueOf(v))
                return m

        @JImplements("java.util.function.Function")
        class PKey:
            @JOverride
            def apply(self, o):
                return JString(fx.prof.get(str(o), str(o)))
        from jpype import JClass as JClass_
        for k, f in (("sacks:fn:count", SCount()), ("sacks:fn:take", STake()), ("sacks:fn:put", SPut()), ("sacks:fn:commit", SCommit()),
                     ("sacks:fn:all", SAll()), ("profile:fn:key", PKey())):
            br.put(k, f)

    def key(self, u):
        return self.prof.get(str(u), str(u))


def prep(E, J, home, fresh_book=True):
    """setup() exactly: the 0.1 data steps (test 0.1.20's bz_prep), then 0.2.0's orders.properties + book + the one-time marker"""
    from jpype import JClass
    T20.bz_prep(E, J, home)
    for m in ("migrate122p", "migrate122"):
        getattr(J("Catalog"), m)()
    d = JClass("java.nio.file.Paths").get(home)
    book_new = not os.path.isfile(os.path.join(home, "book.properties"))
    ocfg = str(J("BzOrdCfg").load(d))
    book = str(J("BzBook").load(d))
    mig = J("BzOrders").migrate02(book_new, bool(J("BzOrdCfg").CREATED))
    if mig is not None:
        J("Market").log(mig)
    J("Market").flushLog()
    J("BzBook").publishAll(JClass("java.lang.System").currentTimeMillis())
    return ocfg, book, None if mig is None else str(mig)


def mkplayers(W, n=3):
    from jpype import JClass
    UU = JClass("java.util.UUID")
    out = [W.mkp(UU.fromString(u), nm) for u, nm in ((U1, "Alice"), (U2, "Bob"), (U3, "Cara"))[:n]]
    return out


def pick(J):
    """a product with room for orders (B - S >= 6, S >= 10) and one too cheap for them (B - S < 2)"""
    C, M = J("Catalog"), J("Market")
    good, cheap = None, None
    for p in C.all():
        i = str(p.id)
        if not bool(C.usable(i)) or i.startswith("Plant_Seeds_") or i.startswith("Skyy_Sack_"):
            continue
        s, b = int(M.quote(i, 1, False)), int(M.quote(i, 1, True))
        if good is None and s >= 10 and b - s >= 6 and b < 400:
            good = i
        if cheap is None and b - s < 2:
            cheap = i
    return good, cheap


# ------------------------------------------------------------------------------------------------------------------- accounting
def totals(J, fx, players, ids):
    """(coins: purses + bid escrow + open coin claims + tax burned, items {id: inventories + Void + ask escrow + open item claims})"""
    Bk = J("BzBook")
    coins = sum(fx.purse.values()) + int(Bk.TAXED)
    items = dict((i, 0) for i in ids)
    for o in Bk.ORDERS.values():
        if bool(o.open()):
            if int(o.side) == 0:
                coins += int(o.rest()) * int(o.price)
            elif str(o.item) in items:
                items[str(o.item)] += int(o.rest())
    for c in Bk.CLAIMS.values():
        if bool(c.open()):
            if int(c.kind) == 0:
                coins += int(c.amount)
            elif str(c.item) in items:
                items[str(c.item)] += int(c.amount)
    for P in players:
        for i in ids:
            items[i] += int(fx.E.count(P, i))
    for (u, i), v in fx.bags.items():
        if i in items:
            items[i] += v
    return coins, items


class MMFlow(object):
    """the market maker's flows read from the trades.log queue (BUY / SELL lines = market legs only; book fills log FILL)"""

    def __init__(self, J):
        self.J, self.coins, self.items, self.lines = J, 0, {}, []

    def drain(self):
        q = self.J("Market").LOGQ
        while True:
            o = q.poll()
            if o is None:
                break
            ln = str(o)
            self.lines.append(ln)
            f = ln.split(" ")
            if len(f) >= 7 and f[1] in ("BUY", "SELL"):
                iid, n, c = f[4], int(f[5]), int(f[6])
                if f[1] == "BUY":          # the market maker took c coins out of the game and made n items
                    self.coins += c
                    self.items[iid] = self.items.get(iid, 0) + n
                else:                      # the market maker made c coins and took n items out of the game
                    self.coins -= c
                    self.items[iid] = self.items.get(iid, 0) - n
        return self


def give(P, iid, qty, slot):
    from jpype import JClass, JShort
    c = P.inv.getStorage()
    c.setItemStackForSlot(JShort(slot), JClass("com.hypixel.hytale.server.core.inventory.ItemStack")(iid, qty))


def clear_inv(P):
    from jpype import JShort
    for c in (P.inv.getStorage(), P.inv.getHotbar()):
        for s in range(int(c.getCapacity())):
            c.setItemStackForSlot(JShort(s), None)


# ------------------------------------------------------------------------------------------------------------------- BOOK
def run_book(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JString
    K = HK.Child(out)
    W = boot(scratch, "book", [])
    E = W.E
    J = lambda n: JClass(PKG + n)
    home = os.path.join(scratch, "home_book")
    ocfg, book, mig = prep(E, J, home)
    C, M, Bk, Od, Fl, Cl, T, Cfg = (J("Catalog"), J("Market"), J("BzBook"), J("BzOrders"), J("BzFill"), J("BzClaim"), J("Trader"), J("BzOrdCfg"))
    T20.fake_items(E, [str(p.id) for p in C.all()])
    fx = Fx(E, J)
    A, Bb, Cc = mkplayers(W)
    ua, ub, uc = A.pr.getUuid(), Bb.pr.getUuid(), Cc.pr.getUuid()
    K.check(os.path.isfile(os.path.join(home, "book.properties")) and open(os.path.join(home, "book.properties")).read().startswith("# SkyyBazaar order book"),
            "BOOK: setup creates an empty book.properties with its header (%s)" % book)
    K.eq(open(os.path.join(home, "orders.properties"), "rb").read().decode("latin-1"), str(Cfg.DEFAULT_TEXT), "BOOK: orders.properties = the default text")
    K.check(mig is not None and mig.startswith("MIGRATE-0.2.0") and "undo" in mig, "BOOK: the one-time MIGRATE-0.2.0 line with its undo (%s)" % mig)
    K.check(open(os.path.join(home, "book.properties"), "rb").read().count(b"migrated.0.2.0=") == 1 and b"migrated.0.2.0" not in open(os.path.join(home, "pricing.properties"), "rb").read(),
            "BOOK: the run-once marker migrated.0.2.0 is in book.properties (review fix: never in pricing.properties, which Catalog.writeModes rebuilds)")
    K.eq(Od.migrate02(False, False), None, "BOOK: the one-time step runs once")
    iid, cheap = pick(J)
    K.check(iid is not None and cheap is not None, "BOOK: a product with room for orders (%s) and a too-cheap one (%s)" % (iid, cheap))
    S, Bp = int(M.quote(iid, 1, False)), int(M.quote(iid, 1, True))
    f0 = float(M.factor(iid))
    for u in (ua, ub, uc):
        fx.purse[str(u)] = 1000000
    W_ = lambda u: str(fx.key(u))
    br = E.br
    K.eq(str(Od.wouldClose(W_(ua))), "ok:0:0:0:0", "BOOK: an empty profile wouldclose = ok:0:0:0:0")
    # ---------------------------------------------------------------- refusals (nothing moves)
    def snap():
        return (dict(fx.purse), dict(fx.bags), int(E.count(A, iid)), int(E.count(Bb, iid)), str(Bk.text()))
    s0 = snap()
    give(Bb, iid, 30, 0)
    s0 = snap()
    ref = [("price at S", lambda: Od.place(A.pl, ua, "Alice", iid, 0, S, 5), "the price must"),
           ("price at B", lambda: Od.place(A.pl, ua, "Alice", iid, 0, Bp, 5), "the price must"),
           ("ask under S", lambda: Od.place(Bb.pl, ub, "Bob", iid, 1, S, 5), "the price must"),
           ("amount 0", lambda: Od.place(A.pl, ua, "Alice", iid, 0, S + 1, 0), "type an amount"),
           ("amount over maxQty", lambda: Od.place(A.pl, ua, "Alice", iid, 0, S + 1, 100001), "type an amount"),
           ("too cheap", lambda: Od.place(A.pl, ua, "Alice", cheap, 0, 1, 50), "too cheap"),
           ("ask without the items", lambda: Od.place(A.pl, ua, "Alice", iid, 1, Bp - 1, 5), "you only hold"),
           ("Magic Bag", lambda: Od.place(A.pl, ua, "Alice", "Skyy_Sack_Mining", 0, 50, 5), "")]
    for what, f, want in ref:
        r = f()
        K.check(not bool(r.ok) and want in str(r.msg) and snap() == s0, "BOOK refused (%s): %s - nothing moved" % (what, r.msg))
    fx.purse[str(ua)] = 10
    r = Od.place(A.pl, ua, "Alice", iid, 0, S + 1, 5)
    K.check(not bool(r.ok) and "you need" in str(r.msg) and fx.purse[str(ua)] == 10, "BOOK refused (insufficient coins): %s" % r.msg)
    fx.purse[str(ua)] = 1000000
    Cfg.MINTOTAL = 100000000
    r = Od.place(A.pl, ua, "Alice", iid, 0, S + 1, 5)
    K.check(not bool(r.ok) and "at least" in str(r.msg), "BOOK refused (minimum total): %s" % r.msg)
    Cfg.MINTOTAL = 10
    Cfg.ON = False
    r = Od.place(A.pl, ua, "Alice", iid, 0, S + 1, 5)
    K.check(not bool(r.ok) and "switched off" in str(r.msg), "BOOK refused (orders.enabled OFF): %s" % r.msg)
    Cfg.ON = True
    for k_, v_, w_ in (("profile:busy:", JClass("java.lang.Boolean").TRUE, "still loading"), ("rebirth:busy:", JClass("java.lang.Boolean").TRUE, "rebirth")):
        br.put(k_ + str(ua), v_)
        r = Od.place(A.pl, ua, "Alice", iid, 0, S + 1, 5)
        K.check(not bool(r.ok) and w_ in str(r.msg), "BOOK refused (%s): %s" % (k_, r.msg))
        r2 = Cl.claimAll(A.pl, ua, "Alice")
        K.check(not bool(r2.ok) and w_ in str(r2.msg), "BOOK claim refused (%s): %s" % (k_, r2.msg))
        br.remove(k_ + str(ua))
    K.eq(snap()[0], s0[0], "BOOK: every refusal moved no coin")
    # ---------------------------------------------------------------- place a bid (Alice) and an ask (Bob: inventory + the Void)
    p_bid, p_ask = S + 1, Bp - 1
    r = Od.place(A.pl, ua, "Alice", iid, 0, p_bid, 10)
    K.check(bool(r.ok) and fx.purse[str(ua)] == 1000000 - 10 * p_bid and str(r.msg).startswith("placed a buy order"), "BOOK: Alice places a buy order of 10 at %d (%s)" % (p_bid, r.msg))
    bid_id = [str(o.id) for o in Bk.ORDERS.values() if str(o.uuid) == U1][0]
    K.check(("o.%s=" % bid_id) in open(os.path.join(home, "book.properties")).read(), "BOOK: the order is in book.properties at once (one atomic write)")
    K.eq(int(br.get("bazaar:bid:" + iid)), p_bid, "BOOK: bazaar:bid:<item> = the best bid")
    K.eq(int(br.get("bazaar:orders:" + U1)), 1, "BOOK: bazaar:orders:<uuid> = 1")
    fx.bags[(U2, iid)] = 20
    r = Od.place(Bb.pl, ub, "Bob", iid, 1, p_bid, 5)
    K.check(not bool(r.ok) and "already at" in str(r.msg), "BOOK refused (an ask at / under the best bid - no crossing): %s" % r.msg)
    r = Od.place(Bb.pl, ub, "Bob", iid, 1, p_ask, 40)
    K.check(bool(r.ok) and int(E.count(Bb, iid)) == 0 and fx.bags[(U2, iid)] == 10 and int(r.fromBags) == 10, "BOOK: Bob offers 40 (30 from the inventory, 10 from the Void) at %d (%s)" % (p_ask, r.msg))
    ask_id = [str(o.id) for o in Bk.ORDERS.values() if str(o.uuid) == U2][0]
    r = Od.place(A.pl, ua, "Alice", iid, 0, p_ask, 1)
    K.check(not bool(r.ok) and "already at" in str(r.msg), "BOOK refused (a bid at the best ask - no crossing): %s" % r.msg)
    K.eq(int(br.get("bazaar:ask:" + iid)), p_ask, "BOOK: bazaar:ask:<item> = the best ask")
    # ---------------------------------------------------------------- open-order limit
    Cfg.MAXOPEN = 1
    r = Od.place(A.pl, ua, "Alice", iid, 0, p_bid, 2)
    K.check(not bool(r.ok) and "open orders on this profile" in str(r.msg), "BOOK refused (open orders per profile): %s" % r.msg)
    Cfg.MAXOPEN = 14
    # ---------------------------------------------------------------- INSTANT BUY through the book (Cara): full, then partial + market
    mm = MMFlow(J).drain()
    c0, i0 = totals(J, fx, [A, Bb, Cc], [iid])
    q4 = int(Fl.quote(Cc.pl, uc, iid, 4, True))
    K.eq(q4, 4 * p_ask, "BOOK: BzFill.quote(4) = 4 offers at %d" % p_ask)
    pc = fx.purse[str(uc)]
    r = T.buy(Cc.pl, uc, "Cara", iid, 4)
    K.check(bool(r.ok) and int(E.count(Cc, iid)) == 4 and pc - fx.purse[str(uc)] == q4, "BOOK: Cara buys 4 from the offer at the quoted %d (%s)" % (q4, r.msg))
    o = Bk.ORDERS.get(ask_id)
    K.check(int(o.filled) == 4 and str(o.status) == "OPEN", "BOOK: the offer is partly filled (4 of 40), still open")
    bp = int(Cfg.bp())
    tax4 = 4 * p_ask * bp // 10000
    cb = [c for c in Bk.CLAIMS.values() if str(c.uuid) == U2 and int(c.kind) == 0 and bool(c.open())]
    K.check(len(cb) == 1 and int(cb[0].amount) == 4 * p_ask - tax4 and int(Bk.TAXED) == tax4, "BOOK: Bob's coin claim = gross - tax %d (%s), tax burned %d" % (tax4, [int(c.amount) for c in cb], int(Bk.TAXED)))
    K.eq(float(M.factor(iid)), f0, "BOOK: an order fill does not move the demand factor (orders.factorMove OFF)")
    mm.drain()
    c1, i1 = totals(J, fx, [A, Bb, Cc], [iid])
    K.check(c1 + mm.coins == c0 and i1[iid] - mm.items.get(iid, 0) == i0[iid], "BOOK: conservation over the fill (coins %d -> %d, items %s -> %s)" % (c0, c1, i0, i1))
    q50 = int(Fl.quote(Cc.pl, uc, iid, 50, True))
    want50 = 36 * p_ask + int(M.quote(iid, 14, True))
    K.eq(q50, want50, "BOOK: BzFill.quote(50) = 36 offers + the market's 14")
    pc = fx.purse[str(uc)]
    r = T.buyN(Cc.pl, uc, "Cara", iid, 50, q50)
    K.check(bool(r.ok) and int(r.qty) == 50 and pc - fx.purse[str(uc)] == q50 and "36 from offers" in str(r.msg), "BOOK: Cara buys 50 = 36 from offers + 14 from the market at the quoted %d (%s)" % (q50, r.msg))
    K.eq(str(Bk.ORDERS.get(ask_id).status), "DONE", "BOOK: the offer is DONE")
    K.check(br.get("bazaar:ask:" + iid) is None, "BOOK: bazaar:ask:<item> removed when no offer is left")
    mm.drain()
    c2, i2 = totals(J, fx, [A, Bb, Cc], [iid])
    K.check(c2 + mm.coins == c0 and i2[iid] - mm.items.get(iid, 0) == i0[iid], "BOOK: conservation over book + market")
    # self-trade: Alice's own bid is skipped when Alice sells
    give(A, iid, 5, 0)
    K.eq(int(Fl.units(A.pl, ua, iid, 5, False)), 0, "BOOK: a player's own buy order is never filled by their own instant sell")
    # ---------------------------------------------------------------- INSTANT SELL into Alice's bid (Cara sells 4 of 10)
    clear_inv(A)
    qs = int(Fl.quote(Cc.pl, uc, iid, 4, False))
    tx = 4 * p_bid * bp // 10000
    K.eq(qs, 4 * p_bid - tx, "BOOK: BzFill.quote(sell 4) = 4 x the bid minus the tax")
    pc = fx.purse[str(uc)]
    r = T.sellN(Cc.pl, uc, "Cara", iid, 4, qs)
    K.check(bool(r.ok) and fx.purse[str(uc)] - pc == qs and int(E.count(Cc, iid)) == 50, "BOOK: Cara sells 4 into Alice's buy order for %d net (%s)" % (qs, r.msg))
    ia = [c for c in Bk.CLAIMS.values() if str(c.uuid) == U1 and int(c.kind) == 1 and bool(c.open())]
    K.check(len(ia) == 1 and int(ia[0].amount) == 4, "BOOK: Alice gets an item claim for 4")
    # ---------------------------------------------------------------- claims
    pb = fx.purse[str(ub)]
    r = Cl.claim(Bb.pl, ub, "Bob", str(cb[0].id))
    K.check(bool(r.ok) and fx.purse[str(ub)] - pb == int(cb[0].amount), "BOOK: Bob claims his coins (%s)" % r.msg)
    r = Cl.claim(Bb.pl, ub, "Bob", str(cb[0].id))
    K.check(not bool(r.ok) and fx.purse[str(ub)] - pb == int(cb[0].amount), "BOOK: the same claim twice is refused (paid once): %s" % r.msg)
    r = Cl.claim(Bb.pl, ub, "Bob", str(ia[0].id))
    K.check(not bool(r.ok) and "profile" in str(r.msg), "BOOK: a claim of another player / profile is refused: %s" % r.msg)
    # full inventory: the claim keeps every item
    filler = [str(p.id) for p in C.all() if str(p.id) != iid][:3]
    for c_ in (A.inv.getStorage(), A.inv.getHotbar()):
        for s in range(int(c_.getCapacity())):
            from jpype import JShort
            c_.setItemStackForSlot(JShort(s), JClass("com.hypixel.hytale.server.core.inventory.ItemStack")(filler[0], int(T.stack(filler[0]))))
    K.eq(int(T.room(A.pl, iid)), 0, "BOOK: Alice's inventory is full")
    r = Cl.claim(A.pl, ua, "Alice", str(ia[0].id))
    open_ia = [c for c in Bk.CLAIMS.values() if str(c.uuid) == U1 and int(c.kind) == 1 and bool(c.open())]
    K.check(not bool(r.ok) and "full" in str(r.msg) and len(open_ia) == 1 and int(open_ia[0].amount) == 4, "BOOK: a full inventory: nothing given, the 4 stay a claim row (%s)" % r.msg)
    # review fix: 50 clicks on a full inventory (claim, CLAIM ALL) write nothing - the row count, book.properties and journal.log stay
    bk_f, jl_f = os.path.join(home, "book.properties"), os.path.join(home, "journal.log")
    rows0, bk0, jl0 = int(Bk.CLAIMS.size()), open(bk_f, "rb").read(), os.path.getsize(jl_f)
    for _i in range(25):
        Cl.claim(A.pl, ua, "Alice", str(ia[0].id))
        Cl.claimAll(A.pl, ua, "Alice")
    K.check(int(Bk.CLAIMS.size()) == rows0 and open(bk_f, "rb").read() == bk0 and os.path.getsize(jl_f) == jl0 and bool(Bk.CLAIMS.get(str(ia[0].id)).open()),
            "BOOK: 50 full-inventory claim clicks: no new row, book.properties + journal.log untouched, the same row stays OPEN")
    # review fix: room for 3 of the 4 -> 3 given, the SAME row keeps 1 (OPEN), no new row
    clear_inv(A)
    for c_ in (A.inv.getStorage(), A.inv.getHotbar()):
        for s in range(int(c_.getCapacity())):
            c_.setItemStackForSlot(JShort(s), JClass("com.hypixel.hytale.server.core.inventory.ItemStack")(filler[0], int(T.stack(filler[0]))))
    st_ = int(T.stack(iid))
    A.inv.getHotbar().setItemStackForSlot(JShort(0), JClass("com.hypixel.hytale.server.core.inventory.ItemStack")(iid, st_ - 3))
    K.eq(int(T.room(A.pl, iid)), 3, "BOOK: Alice has room for 3")
    r = Cl.claim(A.pl, ua, "Alice", str(ia[0].id))
    c_ia = Bk.CLAIMS.get(str(ia[0].id))
    K.check(bool(r.ok) and int(r.qty) == 3 and int(Bk.CLAIMS.size()) == rows0 and bool(c_ia.open()) and int(c_ia.amount) == 1 and int(E.count(A, iid)) == st_,
            "BOOK: a partial claim gives 3 and shrinks the SAME row to 1, no new row (%s)" % r.msg)
    clear_inv(A)                      # the stand-in stack (st_ - 3) goes; the 3 claimed stay (conservation)
    give(A, iid, 3, 1)
    give(A, filler[0], 1, 0)
    r = Cl.claimAll(A.pl, ua, "Alice")
    K.check(bool(r.ok) and int(E.count(A, iid)) == 4 and not [c for c in Bk.CLAIMS.values() if str(c.uuid) == U1 and bool(c.open())], "BOOK: CLAIM ALL delivers the last 1 (4 in all) (%s)" % r.msg)
    # ---------------------------------------------------------------- cancel (+ the page's cancel-claim), someone else's order refused
    r = Od.cancel(ub, bid_id, False, "Bob")
    K.check(str(r).startswith("-"), "BOOK: Bob cannot cancel Alice's order: %s" % r)
    pa = fx.purse[str(ua)]
    r = Od.cancelClaim(A.pl, ua, "Alice", bid_id)
    K.check(bool(r.ok) and fx.purse[str(ua)] - pa == 6 * p_bid and str(Bk.ORDERS.get(bid_id).status) == "CANCELLED", "BOOK: Alice cancels - the 6 unfilled x %d come back at once (%s)" % (p_bid, r.msg))
    # ---------------------------------------------------------------- expiry by the tick
    r = Od.place(A.pl, ua, "Alice", iid, 0, p_bid, 3)
    eid = [str(o.id) for o in Bk.ORDERS.values() if bool(o.open())][0]
    Bk.ORDERS.get(eid).expires = 1
    Od.tick(JClass("java.lang.System").currentTimeMillis())
    ce = Bk.claimFrom(eid)
    K.check(str(Bk.ORDERS.get(eid).status) == "EXPIRED" and ce is not None and int(ce.amount) == 3 * p_bid, "BOOK: the tick expires an old order, its coins wait as a claim")
    K.eq(int(br.get("bazaar:claims:" + U1)), 1, "BOOK: bazaar:claims:<uuid> counts it")
    jl = os.path.join(home, "journal.log")
    K.check(os.path.getsize(jl) == 0, "BOOK: the tick trims journal.log once nothing is in flight")
    # the join notice (a new SEEN entry)
    Bk.SEEN.clear()
    Bk.JOINAT.clear()
    n0 = len(E.sent(A))
    Od.notices(1000)
    K.eq(len(E.sent(A)), n0, "BOOK: review fix - no notice in the tick a player first appears (the client may still be loading)")
    K.check(Bk.SEEN.get(U1) is not None and str(Bk.SEEN.get(U1)) == "", "BOOK: ... the player is not marked notified yet")
    Od.notices(5000)
    K.check("Bazaar claim" in E.strs_of(A, n0), "BOOK: the join notice tells Alice her claim waits (3 s or more after she appeared)")
    n1 = len(E.sent(A))
    Od.notices(15000)
    K.eq(len(E.sent(A)), n1, "BOOK: the notice is once per login / profile")
    # review fix: a player who left loses the per-player bridge keys at the next tick
    GONE = "00000000-0000-4000-8000-0000000000ff"
    Bk.publishUu(GONE)
    K.check(br.get("bazaar:orders:" + GONE) is not None and br.get("bazaar:claims:" + GONE) is not None, "BOOK: an owner's counts are published on a fill")
    Od.notices(0)
    K.check(br.get("bazaar:orders:" + GONE) is None and br.get("bazaar:claims:" + GONE) is None and not Bk.PUBU.contains(GONE) and br.get("bazaar:claims:" + U1) is not None,
            "BOOK: a player who is not online loses bazaar:orders: / bazaar:claims: at the tick; online players keep theirs")
    # review fix: MY ORDERS icons - only an item the game knows reaches the client
    K.check(str(Bk.icon(iid)) == iid and str(Bk.icon("Skyy_Removed_Pack_Item")) == "Ingredient_Bar_Gold" and str(Bk.icon("bad id!")) == "Ingredient_Bar_Gold",
            "BOOK: BzBook.icon keeps a known item, an unknown / bad id becomes the gold bar")
    # ---------------------------------------------------------------- a profile switch
    fx.prof[U1] = U1 + "-p2"
    r = Cl.claim(A.pl, ua, "Alice", str(ce.id))
    K.check(not bool(r.ok) and "profile" in str(r.msg), "BOOK: on profile 2 the profile-1 claim is refused: %s" % r.msg)
    K.eq(int(Bk.otherOpen(U1, U1 + "-p2")), 1, "BOOK: profile 2 sees 1 row on the other profile")
    r = Od.place(A.pl, ua, "Alice", iid, 0, p_bid, 2)
    K.check(bool(r.ok) and int(Bk.openOrders(U1 + "-p2")) == 1 and int(Bk.openOrders(U1)) == 0, "BOOK: an order on profile 2 belongs to profile 2")
    fx.prof[U1] = U1
    r = Cl.claim(A.pl, ua, "Alice", str(ce.id))
    K.check(bool(r.ok), "BOOK: back on profile 1 the claim pays (%s)" % r.msg)
    # ---------------------------------------------------------------- the admin book commands
    K.check("rollback to 0.1.x NOT safe" in str(J("BzBookAdm").checkText()), "BOOK: book check names the rollback gate while orders are open")
    K.check("would be cancelled" in str(Od.cancelAll(False, "admin")), "BOOK: book cancelall without confirm only previews")
    r = str(Od.cancelAll(True, "admin"))
    K.check("cancelled" in r and int(Bk.openOrdersAll()) == 0, "BOOK: book cancelall confirm closes every order: %s" % r)
    fx.prof[U1] = U1 + "-p2"
    r = Cl.claimAll(A.pl, ua, "Alice")
    fx.prof[U1] = U1
    K.check(bool(r.ok), "BOOK: profile 2 claims its refund (%s)" % r.msg)
    r = Cl.claimAll(Bb.pl, ub, "Bob")
    K.check(bool(r.ok) and str(r.msg).startswith("claimed"), "BOOK: Bob claims his offer's coins (%s)" % r.msg)
    K.check("SAFE" in str(J("BzBookAdm").checkText()), "BOOK: the check says rollback safe once every claim is paid: %s" % J("BzBookAdm").checkText())
    K.eq([int(x) for x in J("BzBookAdm").check0()][8], 0, "BOOK: no bad rows")
    mm.drain()
    cz, iz = totals(J, fx, [A, Bb, Cc], [iid])
    K.check(cz + mm.coins == c0 and iz[iid] - mm.items.get(iid, 0) == i0[iid], "BOOK: conservation over the whole sequence (coins %d+%d vs %d)" % (cz, mm.coins, c0))
    K.check(any(" FILL " in l for l in mm.lines) and any(" TAX " in l for l in mm.lines) and any(" ORDER-BID " in l for l in mm.lines) and any(" CANCEL " in l for l in mm.lines) and any(" EXPIRE " in l for l in mm.lines) and any(" CLAIM " in l for l in mm.lines),
            "BOOK: trades.log lines ORDER-BID / FILL / TAX / CANCEL / EXPIRE / CLAIM")
    # restart: the book reloads exactly
    t0 = str(Bk.text())
    Bk.load(JClass("java.nio.file.Paths").get(home))
    K.eq(str(Bk.text()), t0, "BOOK: a restart reads the book back exactly")
    # ---------------------------------------------------------------- review fixes: pruning, the archived-profile flag, the sort, the number format
    now = int(JClass("java.lang.System").currentTimeMillis())
    r = Od.place(A.pl, ua, "Alice", iid, 0, p_bid, 2)
    kid = [str(o.id) for o in Bk.ORDERS.values() if bool(o.open())][0]
    Od.cancel(ua, kid, False, "Alice")                    # CANCELLED + an OPEN refund claim that names it
    n_open = (int(Bk.openOrdersAll()), int(Bk.openClaimsAll()))
    for o in Bk.ORDERS.values():
        o.created = 1
    for c in Bk.CLAIMS.values():
        c.created = 1
    closed_ids = [str(o.id) for o in Bk.ORDERS.values() if not bool(o.open()) and str(o.id) != kid]
    K.check(len(closed_ids) > 0 and any(not bool(c.open()) for c in Bk.CLAIMS.values()), "BOOK: there are old closed orders and paid claims to prune")
    Od.tick(now)
    K.check(not any(not bool(c.open()) for c in Bk.CLAIMS.values()) and not any(Bk.ORDERS.containsKey(i) for i in closed_ids) and Bk.ORDERS.containsKey(kid),
            "BOOK: review fix - the tick prunes paid claims (1 h) and closed orders (2 d); a closed order an OPEN claim names stays")
    K.eq((int(Bk.openOrdersAll()), int(Bk.openClaimsAll())), n_open, "BOOK: pruning never touches an OPEN row")
    K.check(not any(l.startswith("c.") and l.rstrip().endswith("|CLAIMED") for l in open(os.path.join(home, "book.properties"), encoding="utf-8").read().splitlines()), "BOOK: the pruned book is written")
    # pruning waits while journal.log holds a line
    Bk.jlog("INTENT-BID harness-only")
    Bk.ORDERS.get(kid).created = 1
    for c in Bk.CLAIMS.values():
        c.status = "CLAIMED"
    K.eq(int(Od.prune0(now)), 0, "BOOK: nothing is pruned while journal.log is not empty")
    for c in Bk.CLAIMS.values():
        c.status = "OPEN"
    Bk.trim()
    # a deleted / archived profile with open rows is named by book check

    @JImplements("java.util.function.Function")
    class PState:
        @JOverride
        def apply(self, o):
            return JString("archived" if str(o) == U1 else "active")
    br.put("profile:fn:state", PState())
    ct = str(J("BzBookAdm").checkText())
    br.remove("profile:fn:state")
    K.check("deleted / archived: " + U1 + " (archived)" in ct and "restore the profile first" in ct, "BOOK: review fix - book check names an archived profile with open rows: %s" % ct)
    K.check("archived" not in str(J("BzBookAdm").checkText()), "BOOK: without profile:fn:state nothing is flagged")
    # MY ORDERS sorts by tier, then name, then oldest; coin claims first
    MK = J("BzMarket")
    tiered = sorted(((int(MK.tier(str(p.id), -1)), str(p.name).lower(), str(p.id)) for p in C.all() if int(MK.tier(str(p.id), -1)) < 99), key=lambda x: x[0])
    lo, hi = tiered[0], tiered[-1]
    un = [str(p.id) for p in C.all() if int(MK.tier(str(p.id), -1)) == 99][0]
    Ord, Clm, AL = J("BzOrd"), J("BzClm"), JClass("java.util.ArrayList")
    xs = AL()
    for oid_, it_ in (("0005", un), ("0004", hi[2]), ("0003", lo[2]), ("0002", lo[2])):
        xs.add(Ord(oid_, U1, U1, 0, it_, 10, 1, 0, 1, 2, "OPEN"))
    got = [str(o.id) for o in J("BzPage").tierSort(xs, True)]
    K.eq(got, ["0002", "0003", "0004", "0005"], "BOOK: review fix - MY ORDERS orders by tier (T%d before T%d, untiered last), the same item oldest first" % (lo[0], hi[0]))
    cs = AL()
    cs.add(Clm("0009", U1, U1, 1, hi[2], 1, "x", 1, "OPEN"))
    cs.add(Clm("0008", U1, U1, 1, lo[2], 1, "x", 1, "OPEN"))
    cs.add(Clm("0007", U1, U1, 0, None, 5, "x", 1, "OPEN"))
    K.eq([str(c.id) for c in J("BzPage").tierSort(cs, False)], ["0007", "0008", "0009"], "BOOK: claims - coins first, then items by tier")
    K.eq([str(J("BzPage").grp(v)) for v in (0, 999, 1000, 604800, 2592000)], ["0", "999", "1,000", "604,800", "2,592,000"], "BOOK: review fix - expires in 604,800 s (thousands separators)")
    K.save()


# ------------------------------------------------------------------------------------------------------------------- RB
def run_rb(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    W = boot(scratch, "rb", [RB_JAR])
    E = W.E
    J = lambda n: JClass(PKG + n)
    home = os.path.join(scratch, "home_rb")
    prep(E, J, home)
    C, M, Bk, Od, Fl, Cl, T, Cfg = (J("Catalog"), J("Market"), J("BzBook"), J("BzOrders"), J("BzFill"), J("BzClaim"), J("Trader"), J("BzOrdCfg"))
    RC = JClass("com.skyy.rebirth.RbCheck")
    T20.fake_items(E, [str(p.id) for p in C.all()])
    fx = Fx(E, J)
    A, Bb, Cc = mkplayers(W)
    ua, ub, uc = A.pr.getUuid(), Bb.pr.getUuid(), Cc.pr.getUuid()
    for u in (ua, ub, uc):
        fx.purse[str(u)] = 1000000
    iid, _ch = pick(J)
    S, Bp = int(M.quote(iid, 1, False)), int(M.quote(iid, 1, True))
    rb_fn = E.br.get("bazaar:fn:wouldclose")
    K.check(rb_fn is None, "RB: the keys are put by setup() only (not by prep)")
    E.br.put("bazaar:fn:closeall", J("BzRebirthFn")(0))
    E.br.put("bazaar:fn:wouldclose", J("BzRebirthFn")(1))
    wc = lambda k: str(E.br.get("bazaar:fn:wouldclose").apply(k))
    ca = lambda k: str(E.br.get("bazaar:fn:closeall").apply(k))
    # Alice: a buy order 10 @ S+1, a sell offer 5 @ B-1, and a coin claim from a fill (Bob buys 2 of her offer)
    Od.place(A.pl, ua, "Alice", iid, 0, S + 1, 10)
    give(A, iid, 5, 0)
    Od.place(A.pl, ua, "Alice", iid, 1, Bp - 1, 5)
    T.buy(Bb.pl, ub, "Bob", iid, 2)
    T20.give(Bb, iid, 3, 1)
    T.sell(Bb.pl, ub, "Bob", iid, 3)          # 3 into Alice's bid -> an item claim for Alice
    k = U1
    w = wc(k)
    h = RC.head(w)
    lines = JClass("java.util.ArrayList")()
    det = [int(x) for x in RC.detail(w, "Bazaar", lines)]
    coin_claims = [c for c in Bk.CLAIMS.values() if str(c.pkey) == k and int(c.kind) == 0 and bool(c.open())]
    item_claims = [c for c in Bk.CLAIMS.values() if str(c.pkey) == k and int(c.kind) == 1 and bool(c.open())]
    K.check(h is not None and [int(x) for x in h] == [2 + len(coin_claims), 0, len(coin_claims) + len(item_claims), sum(int(c.amount) for c in coin_claims)],
            "RB: RbCheck.head(wouldclose) = closable 2 orders + %d coin claim, blocking 0, claims, coins (%s)" % (len(coin_claims), w.split("\n")[0]))
    K.eq(det, [0, 2, 0], "RB: RbCheck.detail reads 2 closable order lines (kind 3 coin lines are skipped by Rebirth 0.3.6)")
    K.check(all("Bazaar order, will be cancelled" in str(x) for x in lines), "RB: Rebirth's page lines: %s" % [str(x) for x in lines])
    K.check(all(len(l.split("\t")) == 6 for l in w.split("\n")[1:]), "RB: every detail line has 6 tab-separated fields")
    pa = fx.purse[U1]
    held = 7 * (S + 1)
    owed = sum(int(c.amount) for c in coin_claims)
    r = ca(k)
    K.eq(int(RC.closed(r)), 2 + len(coin_claims) + 1, "RB: closeall = ok:<2 orders + %d coin claim + 1 bid refund> (%s)" % (len(coin_claims), r))
    K.eq(fx.purse[U1] - pa, owed + held, "RB: the coin claim + the unfilled bid (%d) went into the purse" % held)
    w2 = wc(k)
    h2 = [int(x) for x in RC.head(w2)]
    K.check(h2[0] == 0 and h2[1] == 0 and h2[3] == 0 and h2[2] == len([c for c in Bk.CLAIMS.values() if str(c.pkey) == k and bool(c.open())]) and h2[2] >= 2,
            "RB: wouldclose after = ok:0:0:<item claims only>:0 (%s) - Rebirth's marketClear passes" % w2.split("\n")[0])
    K.eq(ca(k), "ok:0", "RB: closeall again = ok:0 (idempotent)")
    K.check(any("CLOSEALL key=" + k in str(x) for x in list(M.LOGQ.toArray())), "RB: one CLOSEALL trades.log line per call")
    # rebirthPayCoins OFF: a buy order blocks, nothing closed
    Od.place(A.pl, ua, "Alice", iid, 0, S + 1, 2)
    Cfg.RBPAY = False
    s0 = str(Bk.text())
    r = ca(k)
    K.check(r.startswith("err:blocked:0:") and str(Bk.text()) == s0, "RB: rebirthPayCoins OFF + a buy order -> %s, nothing closed" % r)
    K.check(RC.head(wc(k))[1] >= 1, "RB: ... and wouldclose counts it blocking")
    Cfg.RBPAY = True
    # the owner on another profile: the refund cannot be paid -> blocked, nothing closed
    fx.prof[U1] = U1 + "-p2"
    r = ca(k)
    K.check(r.startswith("err:blocked:0:") and str(Bk.text()) == s0, "RB: the owner on another profile -> %s, nothing closed" % r)
    fx.prof[U1] = U1
    # no SkyyCoins: blocked
    f_ = E.br.remove("coins:fn:add")
    r = ca(k)
    K.check(r.startswith("err:blocked") and str(Bk.text()) == s0, "RB: no SkyyCoins -> %s, nothing closed" % r)
    E.br.put("coins:fn:add", f_)
    K.check(ca(k).startswith("ok:"), "RB: then it closes")
    for bad in (None, "", "   ", "a key with spaces", JClass("java.lang.Integer").valueOf(5)):
        K.check(str(E.br.get("bazaar:fn:wouldclose").apply(bad)) == "err:bad-key" and str(E.br.get("bazaar:fn:closeall").apply(bad)) == "err:bad-key", "RB: bad key %r -> err:bad-key" % (bad,))
    # an order in an unfinished journal step: blocking 0-kind line + err:busy
    Od.place(A.pl, ua, "Alice", iid, 0, S + 1, 2)
    oid = [str(o.id) for o in Bk.ORDERS.values() if bool(o.open())][0]
    Bk.PEND.put(oid, k)
    w3 = wc(k)
    K.check(RC.head(w3)[1] == 1 and ("\n%s\t0\t" % oid) in w3 and ca(k) == "err:busy", "RB: an order inside a journal step = blocking (kind 0) and closeall err:busy")
    Bk.PEND.clear()
    # a broken book
    Bk.BROKEN = True
    K.check(wc(k) == "err:book" and ca(k) == "err:store", "RB: a broken book -> err:book / err:store")
    Bk.BROKEN = False
    K.check(ca(k).startswith("ok:") and RC.head(wc(k))[0] == 0, "RB: clean again")
    K.save()


# ------------------------------------------------------------------------------------------------------------------- CRASH
def run_crash(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    W = boot(scratch, "crash", [])
    E = W.E
    J = lambda n: JClass(PKG + n)
    home = os.path.join(scratch, "home_crash")
    prep(E, J, home)
    C, M, Bk, Od, Fl, Cl, T, Cfg = (J("Catalog"), J("Market"), J("BzBook"), J("BzOrders"), J("BzFill"), J("BzClaim"), J("Trader"), J("BzOrdCfg"))
    T20.fake_items(E, [str(p.id) for p in C.all()])
    fx = Fx(E, J)
    A, Bb, Cc = mkplayers(W)
    ua, ub, uc = A.pr.getUuid(), Bb.pr.getUuid(), Cc.pr.getUuid()
    for u in (ua, ub, uc):
        fx.purse[str(u)] = 10000000
    iid, _ch = pick(J)
    S, Bp = int(M.quote(iid, 1, False)), int(M.quote(iid, 1, True))
    Paths = JClass("java.nio.file.Paths")
    players = [A, Bb, Cc]
    mm = MMFlow(J)
    for step in CRASH_STEPS:
        # a fresh situation: Bob holds 40, a resting ask (Bob, 20 @ B-1) and bid (Cara, 20 @ S+1), Alice holds 10 + a claim
        Od.cancelAll(True, "harness")
        for P_, u_ in ((A, ua), (Bb, ub), (Cc, uc)):
            Cl.claimAll(P_.pl, u_, "x")
        clear_inv(Bb)
        give(Bb, iid, 40, 0)
        clear_inv(A)
        give(A, iid, 10, 0)
        fx.bags[(U2, iid)] = 5
        Od.place(Bb.pl, ub, "Bob", iid, 1, Bp - 1, 20)
        Od.place(Cc.pl, uc, "Cara", iid, 0, S + 1, 20)
        mm.drain()
        c0, i0 = totals(J, fx, players, [iid])
        mm0c, mm0i = mm.coins, dict(mm.items)
        amt, ckind = None, 0
        if step == 30:
            if not [c for c in Bk.CLAIMS.values() if bool(c.open())]:
                T.sell(A.pl, ua, "Alice", iid, 2)                    # a claim for Cara (items) - Alice is paid at once
            mm.drain()
            c0, i0 = totals(J, fx, players, [iid])
            mm0c, mm0i = mm.coins, dict(mm.items)
        Bk.CRASH_AT = step
        Bk.FAIL_SAVES = 1 if 19 <= step <= 26 else 0          # 19-26: the book write fails first, then the crash hits the refund step
        try:
            if step in (19, 20):
                amt = 3 * (S + 2)
                Od.place(A.pl, ua, "Alice", iid, 0, S + 2, 3)
            elif step in (21, 22):
                amt = 3 * (Bp - 1)
                T.buy(A.pl, ua, "Alice", iid, 3)
            elif step in (23, 24):
                amt = 25
                Od.place(Bb.pl, ub, "Bob", iid, 1, Bp - 2, 25)
            elif step in (25, 26):
                amt = 3
                T.sell(A.pl, ua, "Alice", iid, 3)
            elif step <= 5:
                amt = 3 * (S + 2)
                Od.place(A.pl, ua, "Alice", iid, 0, S + 2, 3)
            elif step <= 9:
                Od.place(Bb.pl, ub, "Bob", iid, 1, Bp - 2, 25)       # 20 from the inventory, 5 from the Void
            elif step <= 14:
                amt = 3 * (Bp - 1)
                T.buy(A.pl, ua, "Alice", iid, 3)
            elif step <= 18:
                T.sell(A.pl, ua, "Alice", iid, 3)
            else:
                c_ = [c for c in Bk.CLAIMS.values() if bool(c.open())]
                amt = int(c_[0].amount)
                cid, ckind = str(c_[0].id), int(c_[0].kind)
                own = [P_ for P_, u_ in ((A, U1), (Bb, U2), (Cc, U3)) if u_ == str(c_[0].uuid)][0]
                Cl.claim(own.pl, own.pr.getUuid(), "x", cid)
            crashed = False
        except Exception as ex:
            crashed = "crash test at step %d" % step in str(ex)
        K.check(crashed and int(Bk.CRASH_AT) == -1 and int(Bk.FAIL_SAVES) == 0, "CRASH %d: the simulated crash fired" % step)
        # THE RESTART: memory from disk + the journal replay
        Bk.load(Paths.get(home))
        mm.drain()
        c1, i1 = totals(J, fx, players, [iid])
        dc = (c1 + (mm.coins - mm0c)) - c0
        di = (i1[iid] - (mm.items.get(iid, 0) - mm0i.get(iid, 0))) - i0[iid]
        if step in (19, 21):
            K.check(dc == -amt and di == 0, "CRASH %d (book write failed, REFUNDING marked, not paid yet): at most that refund (%d) lost, never paid twice (%d / %d)" % (step, amt, dc, di))
        elif step in (23, 25):
            K.check(dc == 0 and di == -amt, "CRASH %d (book write failed, RETURNING marked, not given back yet): at most those %d items lost, none duplicated (%d / %d)" % (step, amt, dc, di))
        elif step in (2, 11):
            K.check(dc == -amt and di == 0, "CRASH %d (the accepted window: coins taken, TAKEN not written): exactly %d coins lost, none created, items equal (%d / %d)" % (step, amt, dc, di))
        elif step == 30:
            K.check((dc == -amt and di == 0) if ckind == 0 else (dc == 0 and di == -amt), "CRASH 30 (claim marked, not paid): at most that claim (%d) lost, nothing duplicated (%d / %d)" % (amt, dc, di))
        else:
            K.check(dc == 0 and di == 0, "CRASH %d: after the restart every coin and item is accounted for (coins %+d, items %+d; recovered %d)" % (step, dc, di, int(Bk.RECOVERED)))
        K.check(not bool(Bk.BROKEN) and os.path.getsize(os.path.join(home, "journal.log")) == 0, "CRASH %d: the book loads, the journal is trimmed" % step)
        # nothing duplicated: claim everything and count again
        for P_, u_ in ((A, ua), (Bb, ub), (Cc, uc)):
            Cl.claimAll(P_.pl, u_, "x")
        mm.drain()
        c2, i2 = totals(J, fx, players, [iid])
        K.check(c2 + mm.coins == c1 + mm.coins and i2[iid] == i1[iid], "CRASH %d: claiming everything afterwards moves nothing out of thin air" % step)
    # review fix 2 without a crash: the book write fails AND the refund / give-back cannot be marked or is refused -> nothing is paid twice,
    # the next start pays exactly what is missing as a claim; the rollback gate says "restart first" while a step is in flight
    jl = os.path.join(home, "journal.log")
    from jpype import JImplements, JOverride

    @JImplements("java.util.function.Function")
    class Refuse:
        @JOverride
        def apply(self, o):
            return None
    cases = [("refund marked + paid", None, 0), ("REFUNDING not writable", "REFUNDING", 0), ("bank refuses the refund", "nobank", 0),
             ("RETURNING not writable", "RETURNING", 1), ("give-back marked", None, 1)]
    for what, how, side in cases:
        Od.cancelAll(True, "harness")
        for P_, u_ in ((A, ua), (Bb, ub), (Cc, uc)):
            Cl.claimAll(P_.pl, u_, "x")
        Bk.load(Paths.get(home))
        clear_inv(Bb)
        give(Bb, iid, 40, 0)
        mm.drain()
        c0, i0 = totals(J, fx, players, [iid])
        p0 = fx.purse[U1]
        addf = E.br.get("coins:fn:add")
        Bk.FAIL_SAVES = 1
        if how == "nobank":
            E.br.put("coins:fn:add", Refuse())     # the bank answers no (not a Number) -> Coins.add 0
        elif how is not None:
            Bk.FAIL_JLOG = how
        if side == 0:
            r = Od.place(A.pl, ua, "Alice", iid, 0, S + 2, 3)
        else:
            r = Od.place(Bb.pl, ub, "Bob", iid, 1, Bp - 2, 10)
        E.br.put("coins:fn:add", addf)
        Bk.FAIL_JLOG = None
        jt = open(jl, encoding="utf-8").read()
        K.check(not bool(r.ok) and int(Bk.FAIL_SAVES) == 0, "FAIL %s: the order is refused (%s)" % (what, r.msg))
        if how is None and side == 0:
            K.check(fx.purse[U1] == p0 and " REFUNDING " in jt and " REFUNDED " in jt, "FAIL %s: the refund is marked first, then paid at once" % what)
        if how == "nobank":
            K.check(" UNREFUNDED " in jt and fx.purse[U1] == p0 - 3 * (S + 2), "FAIL %s: a refused refund is re-opened for the replay" % what)
        if how is not None:
            K.check("restart the server first" in str(J("BzBookAdm").checkText()), "FAIL %s: book check says restart first while a step is in flight: %s" % (what, J("BzBookAdm").checkText()))
        Bk.load(Paths.get(home))
        want = 0 if how is None else 1
        K.eq(int(Bk.RECOVERED), want, "FAIL %s: the restart recovers %d claim(s)" % (what, want))
        mm.drain()
        c1, i1 = totals(J, fx, players, [iid])
        K.check(c1 + mm.coins == c0 + mm.coins and i1[iid] == i0[iid], "FAIL %s: every coin and item accounted for after the restart (%d / %d, %d / %d)" % (what, c1, c0, i1[iid], i0[iid]))
        for P_, u_ in ((A, ua), (Bb, ub), (Cc, uc)):
            Cl.claimAll(P_.pl, u_, "x")
        mm.drain()
        c2, i2 = totals(J, fx, players, [iid])
        K.check(c2 == c1 and i2[iid] == i1[iid] and int(Bk.openClaimsAll()) == 0, "FAIL %s: claiming it pays exactly once" % what)
    K.save()


# ------------------------------------------------------------------------------------------------------------------- FUZZ
def run_fuzz(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    W = boot(scratch, "fuzz", [])
    E = W.E
    J = lambda n: JClass(PKG + n)
    home = os.path.join(scratch, "home_fuzz")
    prep(E, J, home)
    C, M, Bk, Od, Fl, Cl, T, Cfg = (J("Catalog"), J("Market"), J("BzBook"), J("BzOrders"), J("BzFill"), J("BzClaim"), J("Trader"), J("BzOrdCfg"))
    T20.fake_items(E, [str(p.id) for p in C.all()])
    fx = Fx(E, J)
    Ps = mkplayers(W)
    us = [P.pr.getUuid() for P in Ps]
    iid, _ch = pick(J)
    ids = [iid]
    for u in us:
        fx.purse[str(u)] = 2000000
    for P in Ps:
        give(P, iid, 60, 0)
    for u in us:
        fx.bags[(str(u), iid)] = 30
    Paths = JClass("java.nio.file.Paths")
    rnd = random.Random(20261020)
    mm = MMFlow(J).drain()
    c0, i0 = totals(J, fx, Ps, ids)
    bad, counts = [], {}
    import time
    t0 = time.time()
    for step in range(STEPS):
        k = rnd.randrange(len(Ps))
        P, u = Ps[k], us[k]
        S, Bp = int(M.quote(iid, 1, False)), int(M.quote(iid, 1, True))
        op = rnd.choice(["bid", "ask", "buy", "sell", "cancel", "claim", "claimall", "expire", "closeall", "restart", "profile", "buy", "sell"])
        counts[op] = counts.get(op, 0) + 1
        if op == "bid" and Bp - S >= 2:
            Od.place(P.pl, u, "f", iid, 0, rnd.randint(S + 1, Bp - 1), rnd.randint(1, 30))
        elif op == "ask" and Bp - S >= 2:
            Od.place(P.pl, u, "f", iid, 1, rnd.randint(S + 1, Bp - 1), rnd.randint(1, 30))
        elif op == "buy":
            T.buy(P.pl, u, "f", iid, rnd.randint(1, 40))
        elif op == "sell":
            T.sell(P.pl, u, "f", iid, rnd.randint(0, 40))
        elif op == "cancel":
            os_ = [o for o in Bk.ORDERS.values() if bool(o.open()) and str(o.uuid) == str(u)]
            if os_:
                Od.cancelClaim(P.pl, u, "f", str(rnd.choice(os_).id))
        elif op == "claim":
            cs_ = [c for c in Bk.CLAIMS.values() if bool(c.open()) and str(c.uuid) == str(u)]
            if cs_:
                Cl.claim(P.pl, u, "f", str(rnd.choice(cs_).id))
        elif op == "claimall":
            Cl.claimAll(P.pl, u, "f")
        elif op == "expire":
            os_ = [o for o in Bk.ORDERS.values() if bool(o.open())]
            if os_:
                rnd.choice(os_).expires = 1
            Od.tick(JClass("java.lang.System").currentTimeMillis())
        elif op == "closeall":
            Od.closeAll(str(fx.key(u)), [0, 0, 0])
        elif op == "restart":
            Bk.load(Paths.get(home))
        elif op == "profile":
            fx.prof[str(u)] = str(u) if fx.key(u) != str(u) else str(u) + "-p2"
        mm.drain()
        c1, i1 = totals(J, fx, Ps, ids)
        dc = c1 + mm.coins - c0
        di = i1[iid] - mm.items.get(iid, 0) - i0[iid]
        if dc != 0 or di != 0:
            bad.append((step, op, dc, di))
            c0, i0 = c1 + mm.coins, dict((i, i1[i] - mm.items.get(i, 0)) for i in ids)
        if int(J("BzBookAdm").check0()[8]) != 0:
            bad.append((step, op, "bad rows"))
    K.eq(bad[:5], [], "FUZZ: %d random steps (seed 20261020; %s): coins (purses + bid escrow + coin claims + tax + the market's flow) and items (inventories + the Void + ask escrow + item claims + the market's flow) constant after EVERY step; %d fills, %d coins taxed, %.0f s"
         % (STEPS, ", ".join("%s %d" % kv for kv in sorted(counts.items())), sum(1 for l in mm.lines if " FILL " in l), int(Bk.TAXED), time.time() - t0))
    K.check(sum(1 for l in mm.lines if " FILL " in l) > 50, "FUZZ: the book really traded (fills > 50)")
    K.notes.append("FUZZ: %d steps %s, %d fills, %d market legs, %d coins taxed, %.0f s" % (STEPS, sorted(counts.items()), sum(1 for l in mm.lines if " FILL " in l),
                   sum(1 for l in mm.lines if l.split(" ")[1:2] in (["BUY"], ["SELL"])), int(Bk.TAXED), time.time() - t0))
    K.save()


# ------------------------------------------------------------------------------------------------------------------- PAGE
def run_page(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    W = boot(scratch, "page", [])
    E = W.E
    J = lambda n: JClass(PKG + n)
    home = os.path.join(scratch, "home_page")
    prep(E, J, home)
    C, M, Bk, Od, Fl, Cl, T, Cfg, CF = (J("Catalog"), J("Market"), J("BzBook"), J("BzOrders"), J("BzFill"), J("BzClaim"), J("Trader"), J("BzOrdCfg"), J("BzConfirm"))
    T20.fake_items(E, [str(p.id) for p in C.all()])
    fx = Fx(E, J)
    A, Bb, Cc = mkplayers(W)
    ua, ub = A.pr.getUuid(), Bb.pr.getUuid()
    for u in (ua, ub):
        fx.purse[str(u)] = 1000000
    iid, _ch = pick(J)
    S, Bp = int(M.quote(iid, 1, False)), int(M.quote(iid, 1, True))
    E.br.put("hub:last:" + U1, JClass("java.util.concurrent.ConcurrentHashMap")())
    J("BzHubOpen").register()
    J("HubBar").open(A.pr, ua, "market", "bazaar")
    E.pump(A)

    def click(a, **kw):
        pg_ = A.pm.getCustomPage()
        pg_.cfShown = 0
        d = {"a": a, "@BzFind": "", "@BzCf": ""}
        d.update(kw)
        A.pm.handleLegacyCustomPageEvent(A.ref, A.st, E.CPE(E.CPT.Data, json.dumps(d)))
        E.pump(A)
        return A.pm.getCustomPage()

    def built(what):
        return H.built(K, E, A, what)

    # the MY ORDERS tab - empty
    pg = click("tabO")
    pg, cm, ev, ap = built("PAGE MY ORDERS empty")
    K.check(bool(pg.myTab) and "No orders yet" in (H.set_of(cm, "#SkyyBzEmpty.Text") or ""), "PAGE: MY ORDERS opens empty: %s" % H.set_of(cm, "#SkyyBzEmpty.Text"))
    # a product -> the detail has [BUY ORDER] [SELL OFFER]
    pg.sel = iid
    pg.cat = C.get(iid).cat
    pg = click("tab:0")
    pg.sel = iid
    pg, cm, ev, ap = built("PAGE product detail")
    sels = [s for s, _t in ev]
    K.check("#SkyyBzOBid" in sels and "#SkyyBzOAsk" in sels, "PAGE: the product detail has BUY ORDER + SELL OFFER bound")
    # the editor: open, steppers, best / market, Enter, place a bid (CONFIRM threshold 0 = every buy order asks)
    CF.set(ua, 0)
    pg = click("obid", **{"@BzAmount": ""})
    pg, cm, ev, ap = built("PAGE editor (buy order)")
    K.check(int(pg.oSide) == 0 and H.set_of(cm, "#SkyyBzOEh.Text").startswith("New buy order") and "#SkyyBzOPlace" in [s for s, _t in ev], "PAGE: BUY ORDER opens the editor")
    K.check(all(any(s == "#SkyyBzOq%d" % i for s, _t in ev) for i in range(6)) and H.set_of(cm, "#SkyyBzOq3.Text") == "+1", "PAGE: the six amount steppers (+1 = %s)" % H.set_of(cm, "#SkyyBzOq3.Text"))
    pg = click("oq:4", **{"@BzOQ": "5", "@BzOP": str(S + 1)})
    K.eq(str(pg.oQty), "15", "PAGE: +10 on 5 = 15")
    pg = click("op:2", **{"@BzOQ": "15", "@BzOP": str(S + 1)})
    K.eq(str(pg.oPrice), str(S + 2), "PAGE: +1 on the price")
    pg = click("omkt", **{"@BzOQ": "15", "@BzOP": str(S + 2)})
    K.eq(int(str(pg.oPrice)), Bp - 1, "PAGE: MARKET = just under the instant buy price for a buy order")
    pg = click("oupd", **{"@BzOQ": "15", "@BzOP": str(S + 1)})
    pg, cm, ev, ap = built("PAGE editor typed")
    K.check(str(H.set_of(cm, "#SkyyBzOEt.Text")).startswith("Holds %d coins" % (15 * (S + 1))), "PAGE: Enter shows the total: %s" % H.set_of(cm, "#SkyyBzOEt.Text"))
    p0 = fx.purse[U1]
    pg = click("oplace", **{"@BzOQ": "15", "@BzOP": str(S + 1)})
    K.check(fx.purse[U1] == p0 and "CONFIRM" in str(pg.info) and int(pg.oArmUntil) > 0, "PAGE: PLACE ORDER asks CONFIRM first (%s)" % pg.info)
    pg, cm, ev, ap = built("PAGE editor armed")
    pg.oArmShown = 0
    pg = click("oplace", **{"@BzOQ": "15", "@BzOP": str(S + 1)})
    K.check(fx.purse[U1] == p0 - 15 * (S + 1) and str(pg.info).startswith("placed a buy order") and int(pg.oSide) == -1, "PAGE: CONFIRM places it (%s)" % pg.info)
    # a sell offer through the editor (no CONFIRM for offers)
    give(A, iid, 20, 3)
    pg = click("oask", **{"@BzAmount": ""})
    pg = click("obest", **{"@BzOQ": "8", "@BzOP": ""})
    K.eq(int(str(pg.oPrice)), S + 2, "PAGE: BEST -1 with no offer yet = MARKET for an offer = just over the best buy order (S+1), never crossing it")
    pg = click("oplace", **{"@BzOQ": "8", "@BzOP": str(Bp - 1)})
    K.check(str(pg.info).startswith("placed a sell offer") and int(E.count(A, iid)) == 12, "PAGE: PLACE ORDER places the offer (%s)" % pg.info)
    pg = click("obid", **{"@BzAmount": ""})
    pg = click("odisc", **{"@BzOQ": "1", "@BzOP": "1"})
    K.eq(int(pg.oSide), -1, "PAGE: DISCARD closes the editor")
    # Bob fills part of Alice's offer -> Alice has a coin claim; the detail line says "from offers"
    T.buy(Bb.pl, ub, "Bob", iid, 3)
    J("HubBar").open(Bb.pr, ub, "market", "bazaar")
    E.pump(Bb)
    pgb = Bb.pm.getCustomPage()
    pgb.sel = iid
    pgb.cat = C.get(iid).cat
    pgb2, cmb, evb = H.build_page(E, Bb, pgb)
    K.check("from offers" in str(H.set_of(cmb, "#SkyyBzDBuy.Text")), "PAGE: Bob's detail says how many come from offers: %s" % H.set_of(cmb, "#SkyyBzDBuy.Text"))
    # MY ORDERS with rows: cancel, claim, claim all, other profiles
    pg = click("tabO")
    pg, cm, ev, ap = built("PAGE MY ORDERS with rows")
    K.check(len(list(pg.cellsO)) == 2 and len(list(pg.cellsC)) == 1 and "#SkyyBzOca" in [s for s, _t in ev] and H.set_of(cm, "#SkyyBzTabO.Text") == "My orders (1)",
            "PAGE: 2 order cards, 1 claim card, CLAIM ALL, the tab badge (%s)" % H.set_of(cm, "#SkyyBzTabO.Text"))
    _ord = [str(x) for x in ap]
    _ix = lambda k: min([i for i, x in enumerate(_ord) if k in x] or [10 ** 9])
    K.check(_ix("SkyyBzOs1") < _ix("SkyyBzOcaRow") < _ix("SkyyBzOx0") < _ix("SkyyBzOs0") < _ix("SkyyBzOo0"),
            "PAGE: review fix - To claim first, CLAIM ALL right under its header, then the claim cards, then Open orders")
    pa = fx.purse[U1]
    pg = click("ocl:0")
    K.check(str(pg.info).startswith("claimed") and fx.purse[U1] > pa, "PAGE: CLAIM pays the row (%s)" % pg.info)
    pg = click("ocan:0")
    K.check(str(pg.info).startswith("cancelled"), "PAGE: CANCEL cancels + claims the rest (%s)" % pg.info)
    pg = click("ocan:7")
    K.check("moved" in str(pg.info), "PAGE: a stale row index is answered, nothing happens (%s)" % pg.info)
    fx.prof[U1] = U1 + "-p2"
    pg = click("tabO")
    pg, cm, ev, ap = built("PAGE MY ORDERS on profile 2")
    K.check("other profiles" in str(H.set_of(cm, "#SkyyBzEmpty.Text") or "") + str(H.set_of(cm, "#SkyyBzOoth.Text") or ""), "PAGE: profile 2 sees the rows on the other profile only as a line")
    fx.prof[U1] = U1
    pg = click("oclall")
    pg, cm, ev, ap = built("PAGE MY ORDERS after claim all")
    # /bazaar orders + /bazaar claim
    oc = J("BzOrdersCmd")()
    K.check(oc.getPermissionGroups() is not None and "hytale:Adventurer" in [str(x) for x in oc.getPermissionGroups()], "PAGE: /bazaar orders is for every player (hytale:Adventurer)")
    cc = J("BzClaimCmd")()
    K.check("hytale:Adventurer" in [str(x) for x in cc.getPermissionGroups()], "PAGE: /bazaar claim is for every player")
    K.save()


# ------------------------------------------------------------------------------------------------------------------- LIVE
def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    W = boot(scratch, "live", [])
    E = W.E
    J = lambda n: JClass(PKG + n)
    names = sorted(n for n in os.listdir(home) if os.path.isfile(os.path.join(home, n)))
    before = dict((n, open(os.path.join(home, n), "rb").read()) for n in names)
    K.check("book.properties" not in before and "orders.properties" not in before, "LIVE: the live copy is a 0.1.x folder (no book yet): %s" % names)
    ocfg, book, mig = prep(E, J, home)
    after = dict((n, open(os.path.join(home, n), "rb").read()) for n in os.listdir(home) if os.path.isfile(os.path.join(home, n)))
    for n in before:
        if n == "trades.log":
            K.check(after[n].startswith(before[n]), "LIVE: %s only appended to (%d -> %d bytes)" % (n, len(before[n]), len(after[n])))
        elif n != "products.properties":
            K.eq(after[n] == before[n], True, "LIVE: %s byte-identical" % n)
    K.check(b"migrated.0.2.0" not in after["pricing.properties"] and after["book.properties"].count(b"migrated.0.2.0=") == 1, "LIVE: the run-once marker is in book.properties (once), pricing.properties untouched")
    tl = after["trades.log"][len(before.get("trades.log", b"")):].decode("utf-8", "replace")
    K.check(tl.count("MIGRATE-0.2.0") == 1, "LIVE: one MIGRATE-0.2.0 trades.log line")
    K.check("book.properties" in after and "orders.properties" in after and after["orders.properties"].decode("latin-1") == str(J("BzOrdCfg").DEFAULT_TEXT),
            "LIVE: book.properties (empty) + orders.properties (defaults) created")
    K.check(not bool(J("BzBook").BROKEN) and "new empty order book" in book, "LIVE: %s" % book)
    h0 = HK.tree_hash(home)
    prep(E, J, home)
    h1 = HK.tree_hash(home)
    K.eq(sorted(k for k in set(h0) | set(h1) if h0.get(k) != h1.get(k)), [], "LIVE: a second start writes nothing")
    # review fix: a price / mode save (Catalog.writeModes rebuilds pricing.properties) never drops the marker -> no second MIGRATE-0.2.0
    J("Catalog").save()
    tl0 = open(os.path.join(home, "trades.log"), "rb").read()
    prep(E, J, home)
    tl1 = open(os.path.join(home, "trades.log"), "rb").read()
    K.check(b"MIGRATE-0.2.0" not in tl1[len(tl0):] and open(os.path.join(home, "book.properties"), "rb").read().count(b"migrated.0.2.0=") == 1,
            "LIVE: after a Catalog.save + restart the one-time line is NOT logged again")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyBazaar", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("book", run_book), ("rb", run_rb), ("crash", run_crash), ("fuzz", run_fuzz), ("page", run_page), ("live", run_live)],
           live=(LIVE, "Skyy_SkyyBazaar"), script=__file__)
