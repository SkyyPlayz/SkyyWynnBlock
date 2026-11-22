"""Harness for SkyyBazaar 0.2.6 (bazaar:fn:tab / bazaar:fn:tabact for SkyyMenu 0.3.59's one-screen Market tab; tools/bazaar_0_2_6_patch.py).
Build first:
    python tools/bazaar_0_2_6_patch.py && python SkyyBazaar/build_skyybazaar_0.2.6.py --with SkyyCollections/SkyyCollections-0.2.36.jar
    python SkyyBazaar/test_skyybazaar_0.2.6.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, -Xverify:all, tools/harness_kit.py + the 0.2.0 stand-in engine; every new code path is EXECUTED):
  S     static   the patch re-runs to identical bytes; line endings kept; no new command / system / setting; exactly the two new bridge puts
  A     verify   every class loads + initialises
  C     compare  0.2.5 -> 0.2.6 (EXPECT below: the version texts + the plugin's setup / shutdown; added BzTabFn)
  K     catalog  every Catalog constant = 0.2.5's (no price / tab / product change)
  P     page     the 0.2.5 page phase re-run on the 0.2.6 jar (the Market > Bazaar page is unchanged)
  T     tab      the two keys EXECUTED on the stand-in engine: the read (header, tabs, the tier-sorted page, the selected product, the amount
                 chips priced, your orders + claims, a search), BUY NOW / SELL NOW exactly once at exactly the shown total, a double click
                 (350 ms), a stale / other profile key, profile:busy, a closing plugin, not enough coins, a full inventory, the price moved
                 up / down, the Confirm-buys-from two presses, Claim all, junk input, not the world thread; coins + items conserved
  D     live     scratch COPIES of the live NewBetaTest Skyy_SkyyBazaar: the 0.2.6 start = the 0.2.5 start, a second 0.2.6 start writes nothing
  AA    audit    engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, subprocess, importlib.util, json, shutil, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.2.6"
PKG = "com.skyy.bazaar."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyBazaar-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyBazaar-0.2.5.jar")
GEN = os.path.join(HERE, "build_skyybazaar_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyybazaar_0.2.5.py")
PATCH = os.path.join(ROOT, "tools", "bazaar_0_2_6_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "tab3", "bz")))
LIVE = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyBazaar")
EXPECT = {"CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "SkyyBazaarPlugin": ["~m setup", "~m shutdown"]}
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = ["BzTabFn"]


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


T25 = tmod(os.path.join(HERE, "test_skyybazaar_0.2.5.py"), "tbz025")


def grp(v):
    return "{:,}".format(int(v))


# ------------------------------------------------------------------------------------------------------------------- S
def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.count('VERSION = "0.2.6"') == 1 and g.startswith('"""SkyyBazaar 0.2.6'), "S version + header")
    for w in ("registerSystem(", "registerCommand(", "CFG.row(", "Server Setup"):
        K.check(g.count(w) == o.count(w), "S no new %s (%d)" % (w, g.count(w)))
    K.check(g.count("bridge().put(") == o.count("bridge().put(") + 2 and 'put("bazaar:fn:tab", new @PKG@.BzTabFn(0))' in g
            and 'put("bazaar:fn:tabact", new @PKG@.BzTabFn(1))' in g, "S exactly the two new bridge keys are put")
    K.check('bridge().remove("bazaar:fn:tab"); @PKG@.BzUtil.bridge().remove("bazaar:fn:tabact")' in g, "S ... and removed at shutdown")
    sd = g[g.index("protected void shutdown()"):]
    K.check(sd.index('remove("bazaar:fn:tabact")') < sd.index("Market.flush()"), "S the keys go BEFORE the last Market flush")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    tb = g[g.index("# ================= 0.2.6 BzTabFn"):g.index("# ================= 0.2.0 /bazaar orders (MY ORDERS)")]
    moves = re.findall(r"@PKG@\.(Trader\.\w+|BzClaim\.\w+|BzOrders\.\w+|Coins\.\w+|Inv\.\w+|Bags\.\w+)\(", tb)
    K.check(set(moves) <= {"Trader.buyN", "Trader.sellN", "Trader.room", "Trader.stack", "BzClaim.claimAll", "Coins.ready", "Coins.get", "Inv.count", "Bags.count"},
            "S BzTabFn moves coins / items ONLY through Trader.buyN / sellN + BzClaim.claimAll (its calls: %s)" % sorted(set(moves)))
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
    K.check(not diff and len(res["new"]) > 10, "K every Catalog constant = 0.2.5's (%d constants; differ: %s)" % (len(res["new"]), diff))
    K.save()


# ------------------------------------------------------------------------------------------------------------------- P
def run_page(out, jar, scratch, home):
    T25.run_page(out, jar, scratch, home)


# ------------------------------------------------------------------------------------------------------------------- T
def run_tab(out, jar, scratch, _home):
    from jpype import JClass, JString, JShort
    K = HK.Child(out)
    T200, T20, W, E, J, fx, home = T25.world(scratch, jar, "tab")
    C, M, Bk, Od, Fl, T, CF, TF, Mk = (J("Catalog"), J("Market"), J("BzBook"), J("BzOrders"), J("BzFill"), J("Trader"), J("BzConfirm"),
                                       J("BzTabFn"), J("BzMarket"))
    A, Bb, Cc = T200.mkplayers(W)
    ua, ub = A.pr.getUuid(), Bb.pr.getUuid()
    sa, sb = str(ua), str(ub)
    for u in (sa, sb):
        fx.purse[u] = 1000000
    iid, cheap = T200.pick(J)
    ids = [iid]
    filler = [str(p.id) for p in C.all() if str(p.id) not in (iid, cheap) and bool(C.usable(str(p.id)))][0]
    mm = T200.MMFlow(J)
    base = {}
    OA = JClass("java.lang.Object[]")

    def rebase():
        mm.drain()
        c1, i1 = T200.totals(J, fx, [A, Bb], ids)
        base["c"], base["i"] = c1 + mm.coins, i1[iid] - mm.items.get(iid, 0)

    def conserved(what):
        mm.drain()
        c1, i1 = T200.totals(J, fx, [A, Bb], ids)
        K.check(c1 + mm.coins == base["c"] and i1[iid] - mm.items.get(iid, 0) == base["i"],
                "T CONSERVED after %s: coins %d (+ market %d) vs %d, items %d (- market %d) vs %d" % (what, c1, mm.coins, base["c"], i1[iid], mm.items.get(iid, 0), base["i"]))
    CF.set(ua, 10 ** 12)
    CF.set(ub, 10 ** 12)
    TF.TEST_ANY_THREAD = False
    RD, AC = TF(0), TF(1)

    def args(*xs):
        a = OA(len(xs))
        for i, x in enumerate(xs):
            a[i] = x if not isinstance(x, int) or isinstance(x, bool) else JClass("java.lang.Integer").valueOf(x)
        return a

    def read(u, cat="", q="", sel="", page=0, per=8, amt=0):
        r = RD.apply(args(u, JString(cat), JString(q), JString(sel), page, per, amt))
        return None if r is None else str(r)

    def act(u, tok, op, arg):
        TF.LASTOP.clear()
        r = AC.apply(args(u, JString(tok), JString(op), JString(arg)))
        return None if r is None else str(r)

    def parse(s):
        L = s.split("\n")
        out_ = {"hd": L[0].split("|"), "k": [], "r": [], "o": [], "d": None, "q": None, "m": None}
        for ln in L[1:]:
            f = ln.split("|")
            if f[0] in ("k", "r", "o"):
                out_[f[0]].append(f)
            else:
                out_[f[0]] = f
        return out_
    # ---------------------------------------------------------------- not the world thread / junk
    K.check(read(ua) is None, "T NOT the player's world thread (the stand-in store is not in its thread) = null, nothing read")
    K.check(act(ua, sa, "buy", "x|1|1") is None, "T NOT the world thread: an action = null (the screen says it could not run)")
    TF.TEST_ANY_THREAD = True
    K.check(RD.apply(JString("junk")) is None and RD.apply(args(JClass("java.util.UUID").randomUUID())) is None and AC.apply(args(ua)) is None,
            "T junk / an offline player / an action without its arguments = null")
    # ---------------------------------------------------------------- READ
    cat = str(C.get(iid).cat)
    cats = [str(x) for x in C.categories()]
    if cat not in cats:
        cat = [str(x) for x in C.tabsOf(C.get(iid))][0]
    T200.give(A, iid, 7, 0)
    fx.bags[(sa, iid)] = 3
    s = read(ua, cat, "", iid, 0, 8, 0)
    R = parse(s)
    hd = R["hd"]
    K.check(hd[0] == "ok" and hd[1] == str(Bk.pkey(ua)) and hd[2] == cat and hd[7] == "1" and hd[8] == "1000000" and hd[11] == "0",
            "T READ header: ok, the profile key, the category, coins ready, the purse, book on (%s)" % hd)
    K.check(len(hd) == 13 and hd[12] == str(int(J("BzOrdCfg").bp())) and int(hd[12]) > 0,
            "T READ (fix tab3) the header ends with the seller tax on order fills = BzOrdCfg.bp() (%s), the screen's 'after tax' note" % hd[12:])
    K.eq([f[1] for f in R["k"]], cats, "T READ every Bazaar tab in the page's order")
    allin = [str(p.id) for p in C.inCat(cat) if bool(C.usable(str(p.id)))]
    K.check(int(hd[5]) == len(allin) and int(hd[4]) == (len(allin) + 7) // 8, "T READ count + pages of the tab (%s products, %s pages)" % (hd[5], hd[4]))
    def tkey(i_):
        p_ = C.get(i_)
        return (int(Mk.tier(i_, -1)), str(p_.name if p_.name is not None else i_).lower(), i_)
    want = sorted(allin, key=tkey)
    K.eq([f[1] for f in R["r"]], want[:8], "T READ the page = the tab's products SORTED BY TIER, then name (BzMkSort)")
    r0 = R["r"][0]
    K.check(r0[5] == str(int(Fl.quote(A.pl, ua, r0[1], 1, True))) and r0[6] == str(int(Fl.quote(A.pl, ua, r0[1], 1, False))) and r0[3] == str(int(Mk.rar(r0[1])))
            and r0[4] == str(Mk.tag(r0[1])), "T READ a row: rarity, tier tag, BUY NOW / SELL NOW each = BzFill.quote of 1 (%s)" % r0)
    d = R["d"]
    K.check(d is not None and d[1] == iid and d[7] == "10" and d[8] == "3" and d[9] == str(int(T.stack(iid))) and d[14] == "0",
            "T READ the selected product: you have 10 (3 in the Void), the stack (%s)" % (d,))
    q = R["q"]
    b1, s1 = int(Fl.quote(A.pl, ua, iid, 1, True)), int(Fl.quote(A.pl, ua, iid, 1, False))
    K.check(q[1:4] == ["1", str(b1), ""] and q[4:7] == ["1", str(s1), ""], "T READ chip 1: buy 1 for %d, sell 1 for %d (%s)" % (b1, s1, q))
    stk = int(T.stack(iid))
    R2 = parse(read(ua, cat, "", iid, 0, 8, 1))
    K.check(R2["q"][1] == str(stk) and R2["q"][2] == str(int(Fl.quote(A.pl, ua, iid, stk, True))) and R2["q"][6] == "You have 10 - pick All",
            "T READ chip stack: buy a stack priced, sell a stack = 'You have 10' (%s)" % R2["q"])
    R3 = parse(read(ua, cat, "", iid, 0, 8, 2))
    room = int(T.room(A.pl, iid))
    aff = int(M.maxBuyable(iid, 1000000, min(room, int(T.MAXQ))))
    K.check(R3["q"][1] == str(aff) and R3["q"][4] == "10" and R3["q"][5] == str(int(Fl.quote(A.pl, ua, iid, 10, False))),
            "T READ chip All: buy all you can afford (%d), sell all you have (10) (%s)" % (aff, R3["q"]))
    R4 = parse(read(ua, cat, "", "", 0, 8, 0))
    K.check(R4["d"] is not None and R4["d"][1] == want[0], "T READ no selection = the first row of the page")
    R5 = parse(read(ua, cat, "", "Not_An_Item", 99, 8, 0))
    K.check(R5["hd"][3] == str(int(R5["hd"][4]) - 1) and R5["d"][1] == want[(int(R5["hd"][4]) - 1) * 8], "T READ a page past the end = the last page; an unknown selection = its first row")
    nm = str(C.get(iid).name)
    Rs = parse(read(ua, cat, nm.split(" ")[0], "", 0, 8, 0))
    fm = [str(p.id) for p in J("BzPage").findAll(nm.split(" ")[0]) if bool(C.usable(str(p.id)))]
    K.check(Rs["hd"][6] == "1" and int(Rs["hd"][5]) == len(fm) and set(f[1] for f in Rs["r"]) <= set(fm) and len(fm) > 0,
            "T READ a search lists BzPage.findAll's matches across every tab (%d matches for %r)" % (len(fm), nm.split(" ")[0]))
    # ---------------------------------------------------------------- BUY NOW exactly once
    tok = str(Bk.pkey(ua))
    rebase()
    p0, n0 = fx.purse[sa], int(E.count(A, iid))
    r = act(ua, tok, "buy", "%s|1|%d" % (iid, b1))
    K.check(r.startswith("+") and fx.purse[sa] == p0 - b1 and int(E.count(A, iid)) == n0 + 1, "T BUY NOW 1 at the shown total: %s" % r)
    conserved("BUY NOW")
    # a double click: the same op + arg within 350 ms
    p0, n0 = fx.purse[sa], int(E.count(A, iid))
    b1 = int(Fl.quote(A.pl, ua, iid, 1, True))
    a_ = args(ua, JString(tok), JString("buy"), JString("%s|1|%d" % (iid, b1)))
    TF.LASTOP.clear()
    r1, r2 = str(AC.apply(a_)), str(AC.apply(a_))
    K.check(r1.startswith("+") and r2 == "=One moment." and fx.purse[sa] == p0 - b1 and int(E.count(A, iid)) == n0 + 1,
            "T a DOUBLE CLICK buys once (second = '=One moment.'): %s / %s" % (r1, r2))
    conserved("double click")
    # stale / other profile key, profile:busy, closing
    p0, n0 = fx.purse[sa], int(E.count(A, iid))
    b1 = int(Fl.quote(A.pl, ua, iid, 1, True))
    r = act(ua, "someone-else", "buy", "%s|1|%d" % (iid, b1))
    fx.prof[sa] = sa + "-p2"
    r2 = act(ua, tok, "buy", "%s|1|%d" % (iid, b1))
    del fx.prof[sa]
    K.check(r.startswith("=Your profile changed") and r2.startswith("=Your profile changed") and fx.purse[sa] == p0 and int(E.count(A, iid)) == n0,
            "T a stale page / a profile switch since the read = refused, nothing moved (%s)" % r2)
    E.br.put("profile:busy:" + sa, JClass("java.lang.Boolean").TRUE)
    r = act(ua, tok, "buy", "%s|1|%d" % (iid, b1))
    E.br.remove("profile:busy:" + sa)
    T.CLOSED = True
    r2 = act(ua, tok, "sell", "%s|1|1" % iid)
    T.CLOSED = False
    K.check(r.startswith("-Your profile is still loading") and r2.startswith("-The Bazaar is closing") and fx.purse[sa] == p0 and int(E.count(A, iid)) == n0,
            "T profile:busy / a closing plugin = refused, nothing moved")
    # junk actions
    r = act(ua, tok, "buy", "Not_An_Item|1|5")
    r2 = act(ua, tok, "buy", "%s|0|5" % iid)
    r3 = act(ua, tok, "steal", "x")
    r4 = act(ua, tok, "buy", "%s|abc|5" % iid)
    K.check(r.startswith("-That item is not") and r2.startswith("=Pick an amount") and r3 == "-Unknown Bazaar action." and r4.startswith("=Pick an amount")
            and fx.purse[sa] == p0, "T junk actions refused: %s / %s / %s" % (r, r2, r3))
    # the price went up between the read and the click
    b4 = int(Fl.quote(A.pl, ua, iid, 4, True))
    r = act(ua, tok, "buy", "%s|4|%d" % (iid, b4 - 1))
    K.check(r.startswith("=The price went up") and fx.purse[sa] == p0 and int(E.count(A, iid)) == n0, "T the price went up: nothing bought (%s)" % r)
    conserved("price up")
    # Confirm buys from: the first press asks, the second buys
    CF.set(ua, 1)
    r = act(ua, tok, "buy", "%s|2|%d" % (iid, int(Fl.quote(A.pl, ua, iid, 2, True))))
    K.check(r.startswith("=Buy 2 ") and "Press Buy now again" in r and fx.purse[sa] == p0, "T Confirm-buys-from: the first press asks (%s)" % r)
    fx.prof[sa] = sa + "-p2"
    tok2 = str(Bk.pkey(ua))
    np_ = int(E.count(A, iid))
    rp = act(ua, tok2, "buy", "%s|2|%d" % (iid, int(Fl.quote(A.pl, ua, iid, 2, True))))
    del fx.prof[sa]
    K.check(tok2 != tok and rp.startswith("=Buy 2 ") and fx.purse[sa] == p0 and int(E.count(A, iid)) == np_,
            "T (fix tab3) the ask belongs to the PROFILE it was made on: the same buy on another profile within 10 s asks again, nothing bought (%s)" % rp)
    r3 = act(ua, tok, "sell", "%s|1|%d" % (iid, int(Fl.quote(A.pl, ua, iid, 1, False))))
    rb = act(ua, tok, "buy", "%s|2|%d" % (iid, int(Fl.quote(A.pl, ua, iid, 2, True))))
    K.check(rb.startswith("=Buy 2 "), "T ... any other action in between cancels the ask (asked again: %s)" % rb)
    p1, n1 = fx.purse[sa], int(E.count(A, iid))
    c2 = int(Fl.quote(A.pl, ua, iid, 2, True))
    r = act(ua, tok, "buy", "%s|2|%d" % (iid, c2))
    K.check(r.startswith("+") and fx.purse[sa] == p1 - c2 and int(E.count(A, iid)) == n1 + 2, "T ... the second press of the same buy buys (%s)" % r)
    CF.set(ua, 10 ** 12)
    rebase()
    # not enough coins
    fx.purse[sa] = 3
    rebase()
    Rn = parse(read(ua, cat, "", iid, 0, 8, 0))
    K.check(Rn["q"][3] == "Not enough coins" or Rn["q"][3].startswith("You can afford"), "T READ not enough coins: said on the buy (%s)" % Rn["q"])
    n0 = int(E.count(A, iid))
    r = act(ua, tok, "buy", "%s|1|%d" % (iid, int(Fl.quote(A.pl, ua, iid, 1, True))))
    K.check(r.startswith("-") and fx.purse[sa] == 3 and int(E.count(A, iid)) == n0, "T not enough coins = Trader's refusal, nothing moved (%s)" % r)
    conserved("not enough coins")
    fx.purse[sa] = 1000000
    # a full inventory
    held = int(E.count(A, iid))
    T200.clear_inv(A)
    fx.bags[(sa, iid)] = 0
    for sl in range(int(A.inv.getStorage().getCapacity())):
        T200.give(A, filler, 1, sl)
    hb = A.inv.getHotbar()
    for sl in range(int(hb.getCapacity())):
        hb.setItemStackForSlot(JShort(sl), JClass("com.hypixel.hytale.server.core.inventory.ItemStack")(filler, 1))
    rebase()
    Rf = parse(read(ua, cat, "", iid, 0, 8, 0))
    K.check(Rf["q"][3] == "Your inventory is full" and Rf["q"][6] == "You have none to sell", "T READ a full inventory: said on the buy, nothing to sell (%s)" % Rf["q"])
    p0 = fx.purse[sa]
    r = act(ua, tok, "buy", "%s|1|%d" % (iid, int(Fl.quote(A.pl, ua, iid, 1, True))))
    K.check(r.startswith("-") and "full" in r and fx.purse[sa] == p0 and int(E.count(A, iid)) == 0, "T a full inventory = refused, nothing paid (%s)" % r)
    conserved("full inventory")
    T200.clear_inv(A)
    T200.give(A, iid, 12, 0)
    fx.bags[(sa, iid)] = 2
    rebase()
    # ---------------------------------------------------------------- SELL NOW
    Ra = parse(read(ua, cat, "", iid, 0, 8, 2))
    sq, sv = int(Ra["q"][4]), int(Ra["q"][5])
    K.check(sq == 14 and sv == int(Fl.quote(A.pl, ua, iid, 14, False)), "T READ sell All = 14 (12 + 2 in the Void) for %d" % sv)
    r = act(ua, tok, "sell", "%s|14|%d" % (iid, sv + 1))
    K.check(r.startswith("=The price dropped") and int(E.count(A, iid)) == 12 and fx.bags[(sa, iid)] == 2, "T the price dropped: nothing sold (%s)" % r)
    p0 = fx.purse[sa]
    r = act(ua, tok, "sell", "%s|14|%d" % (iid, sv))
    K.check(r.startswith("+") and fx.purse[sa] == p0 + sv and int(E.count(A, iid)) == 0 and fx.bags[(sa, iid)] == 0, "T SELL NOW all 14 at the shown pay (%s)" % r)
    conserved("SELL NOW")
    r = act(ua, tok, "sell", "%s|1|%d" % (iid, s1))
    K.check(r.startswith("-") and fx.purse[sa] == p0 + sv, "T selling with none left = refused (%s)" % r)
    # ---------------------------------------------------------------- your orders + Claim all (Bob's sell offer filled by Alice's BUY NOW)
    Bp, S_ = int(M.quote(iid, 1, True)), int(M.quote(iid, 1, False))
    T200.give(Bb, iid, 5, 0)
    rebase()
    ro = Od.place(Bb.pl, ub, "Bob", iid, 1, Bp - 1, 5)
    rbid = Od.place(Bb.pl, ub, "Bob", iid, 0, S_ + 1, 3)
    K.check(bool(ro.ok) and bool(rbid.ok), "T Bob places a sell offer + a buy order (%s / %s)" % (ro.msg, rbid.msg))
    tb = str(Bk.pkey(ub))
    Rb = parse(read(ub, cat, "", iid, 0, 8, 0))
    sides = sorted(f[1] for f in Rb["o"])
    K.check(Rb["hd"][9] == "2" and sides == ["0", "1"] and all(f[2] == iid and f[4] in ("5", "3") for f in Rb["o"]), "T READ your OPEN orders (%s)" % Rb["o"])
    c5 = int(Fl.quote(A.pl, ua, iid, 5, True))
    r = act(ua, tok, "buy", "%s|5|%d" % (iid, c5))
    K.check(r.startswith("+") and int(E.count(A, iid)) == 5, "T Alice's BUY NOW fills Bob's sell offer first (%s)" % r)
    Rb = parse(read(ub, cat, "", iid, 0, 8, 0))
    cw = int(Rb["m"][1])
    K.check(cw > 0 and Rb["hd"][10] == Rb["m"][3] and int(Rb["m"][3]) >= 1, "T READ Bob's coins waiting to claim: %s" % Rb["m"])
    pb = fx.purse[sb]
    r = act(ub, tb, "claim", "")
    K.check(r.startswith("+Claimed") and fx.purse[sb] == pb + cw, "T Claim all pays exactly the coins waiting (%s)" % r)
    r = act(ub, tb, "claim", "")
    K.check(r.startswith("-") and fx.purse[sb] == pb + cw, "T a second Claim all pays nothing (%s)" % r)
    conserved("orders + claim")
    K.notes.append("T BzTabFn: reads + actions on %s (tier %d), stack %d" % (iid, int(Mk.tier(iid, -1)), stk))
    TF.TEST_ANY_THREAD = False
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
    K.check(not da, "D the 0.2.6 start = the 0.2.5 start on the live data (files that differ: %s)" % da)
    K.check(hs["new1"] == hs["new2"], "D a second 0.2.6 start writes nothing (%s)" % sorted(k for k in set(hs["new1"]) | set(hs["new2"]) if hs["new1"].get(k) != hs["new2"].get(k))[:5])
    K.save()


if __name__ == "__main__":
    if "--dump-consts" in sys.argv:
        k = sys.argv.index("--dump-consts")
        T25._dump_consts(sys.argv[k + 1], sys.argv[k + 2])
        sys.exit(0)
    HK.run(name="SkyyBazaar", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("catalog", run_catalog), ("page", run_page), ("tab", run_tab), ("live", run_live)],
           live=(LIVE, "Skyy_SkyyBazaar"), script=__file__)
