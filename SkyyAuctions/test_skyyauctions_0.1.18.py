"""Harness for SkyyAuctions 0.1.18 (the Auction House bridge ops ah:fn:tab / ah:fn:tabact for the new screen's Market tab;
tools/auctions_0_1_18_patch.py - the KEY CONTRACT is its header). Build first:
python tools/auctions_0_1_18_patch.py && python SkyyAuctions/build_skyyauctions_0.1.18.py

    python SkyyAuctions/test_skyyauctions_0.1.18.py [--dir <folder inside tools/dev/scratch/>] [--keep] [--expect-dump]

Phases (fresh child JVMs, -Xverify:all, tools/harness_kit.py):
  A     verify   every class loads + initialises
  C     compare  the PINNED 0.1.17 jar -> 0.1.18: AhPage (the shared pieces + clickAct; handleDataEvent / the renders / readFields / doPreview
                 now call them), AhQuit (forget), the plugin (the two keys), the new class AhTabFn + the version texts - nothing else
  S     static   the patch re-runs to identical bytes, line endings kept; one class added (AhTabFn), no system / command; the jar = 0.1.17's
                 entries + AhTabFn.class
  TAB   EXECUTED over the engine stand-ins (tools/hub_tab_harness.py + the SkyyBazaar 0.1.18 harness helpers, a fake SkyyCoins bridge,
        real inventories), TWIN players: every op is done by one player on the PAGE (real clicks) and by its twin through the BRIDGE; the
        answer text (names / listing numbers normalised), the purse change, the inventory and the record state must be the same:
        create (preview press, then create), buy (one press under confirmAbove; two presses at / above it), cancel (two presses), claim
        coins, claim item with a FULL inventory (kept) then with room, claim all (two presses at / above claimAllConfirmAbove), no.
        Every refusal: a stale price, sold, grace, not enough coins, paused, a bad price, a slot that changed, a bad duration, a listing
        that is not yours, nothing to claim, an expired confirm (asks again, nothing moves), a double click (=One moment., charged once),
        create pressed again after it listed (refused, nothing listed twice), a profile switch (refused; the arm never crosses profiles), a
        stale token, an unknown op, shutdown (CLOSED). Reads: Browse rows = the page's rows in the page's order (tier then name) with
        the rarity colour, filters, the item view's 9 fact lines = the page's labels, Manage rows / summary = the page's, Create cells /
        fee lines = the page's.
  CLAIM17 / X16 / HUB / RB   the 0.1.17, 0.1.16, 0.1.10 and 0.1.11 harness phases on this jar (the page's clicks now go through clickAct)
  D     live     the 0.1.16 harness's live phase: a scratch COPY of the live Skyy_SkyyAuctions started TWICE - no file changes
  DT    livetab  a second scratch COPY of the live data: loaded twice, every ah:fn:tab view read for two players each time - no file changes
  AA    engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, time, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION, OLD_VERSION = "0.1.18", "0.1.17"
PKG = "com.skyy.auctions."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyAuctions-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyAuctions-%s.jar" % OLD_VERSION)
GEN = os.path.join(HERE, "build_skyyauctions_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyauctions_%s.py" % OLD_VERSION)
PATCH = os.path.join(ROOT, "tools", "auctions_0_1_18_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "ah1", "ah")))

_cmp0 = HK.run_compare
_argv = list(sys.argv)
_sp = importlib.util.spec_from_file_location("ah0117test", os.path.join(HERE, "test_skyyauctions_0.1.17.py"))
T17 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T17)
sys.argv[:] = _argv
HK.run_compare = _cmp0
T16, T10, T11, TB, H = T17.T16, T17.T10, T17.T11, T17.TB, T17.H

EXPECT = {"AhPage": ["+m banner", "+m browseEmpty", "+m buyNote", "+m cellsOf", "+m clickAct", "+m factLines", "+m feeLines", "+m mState",
                     "+m mSum", "+m plainDesc", "+m priceWhy", "+m selHint", "+m sellerTag", "+m setLevels", "+m setQuery",     # the shared pieces
                     "~m doPreview", "~m handleDataEvent", "~m readFields", "~m renderBrowse", "~m renderCreate", "~m renderItem",
                     "~m renderManage", "~m renderTop"],                                  # now call them (behaviour: CLAIM17 / HUB / RB / TAB)
          "AhQuit": ["~m accept"],                                                       # AhTabFn.forget
          "SkyyAuctionsPlugin": ["~m setup", "~m shutdown"],                             # the two keys
          "AhCmds": ["~m status"], "CfgFn": ["~m opExport"], "CfgRows": ["~m header"]}   # the version texts
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = ["AhTabFn"]


# ------------------------------------------------------------------------------------------------------------------- static
def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyAuctions 0.1.18 - build script') and g.count('VERSION = "0.1.18"\n') + g.count('VERSION = "0.1.18"\r\n') == 1, "S header + VERSION")
    K.eq(tuple(g.count(x) - o.count(x) for x in ("registerSystem(", "registerCommand(", "makeClass(")), (0, 0, 1), "S one class added, no system / command")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    K.eq((sorted(nb - na), sorted(na - nb)), (["com/skyy/auctions/AhTabFn.class"], []), "S the jar = 0.1.17's entries + AhTabFn.class")
    for k in ("ah:fn:tab", "ah:fn:tabact"):
        K.check(g.count('"%s"' % k) >= 2, "S %s put in setup + removed in shutdown" % k)
    K.save()


# ------------------------------------------------------------------------------------------------------------------- TAB (twins)
def run_tab(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JImplements, JOverride, JArray, JObject, JString
    K = HK.Child(out)
    W = H.boot(scratch, jar, "tab")
    E = W.E
    J = lambda n: JClass(PKG + n)
    HB = J("HubBar")
    E.br = HB.map()
    home = os.path.join(scratch, "home_tab", "Skyy_SkyyAuctions")
    T10.prep(E, J, home)
    TB.fake_items(E, ["Ore_Iron", "Ore_Copper", "Ore_Gold", "Ore_Silver", "Ore_Cobalt"])
    purse = {}
    TB.fake_coins(E.br, purse)
    UUID = JClass("java.util.UUID")
    Integer = JClass("java.lang.Integer")
    SA, BA = W.P, W.O                       # sellers: SA on the page, BA through the bridge
    SB = W.mkp(UUID.fromString("00000000-0000-0000-0000-0000000000d1"), "TwinPageBuyer")
    BB = W.mkp(UUID.fromString("00000000-0000-0000-0000-0000000000d2"), "TwinBridgeBuyer")
    ALL = (SA, BA, SB, BB)
    # TEST ONLY (the 0.1.11 harness's stand-in): the stand-in Inventory has no ECS inventory components, so getCombinedStorageHotbarBackpack()
    # (the vanilla add a delivery uses) is null - a subclass answers it with the real storage + hotbar containers (what the engine combines)
    jp = JClass("javassist.ClassPool")(True)
    jp.appendClassPath(B.SERVER_JAR)
    INVN = "com.hypixel.hytale.server.core.inventory.Inventory"
    CICN, ICN = "com.hypixel.hytale.server.core.inventory.container.CombinedItemContainer", "com.hypixel.hytale.server.core.inventory.container.ItemContainer"
    ct = jp.makeClass("com.hypixel.hytale.server.core.inventory.SkyyAhTabTestInv", jp.get(INVN))
    ct.addMethod(JClass("javassist.CtNewMethod").make("public %s getCombinedStorageHotbarBackpack() { return new %s(new %s[] { getStorage(), getHotbar() }); }"
                                                      % (CICN, CICN, ICN), ct))
    TI = JClass(ct.toClass(JClass(INVN).class_))
    for X in ALL:
        ti = TI()
        for fld in ("storage", "hotbar", "backpack", "utility", "tools", "armor"):
            H.jf(JClass(INVN).class_, fld).set(ti, H.jf(JClass(INVN).class_, fld).get(X.inv))
        H.jf(X.pl.getClass(), "inventory").set(X.pl, ti)
        X.inv = ti
    NAMES = ["SkyyPlain", "SkyyOp", "TwinPageBuyer", "TwinBridgeBuyer"]
    for X in ALL:
        purse[str(X.pr.getUuid())] = 1000000
        E.br.put("hub:last:" + str(X.pr.getUuid()), JClass("java.util.concurrent.ConcurrentHashMap")())
    J("AhHubOpen").register()
    Cfg, Sto, Pg, Tab = J("AhCfg"), J("AhStore"), J("AhPage"), J("AhTabFn")
    Cfg.GRACE_MS = 0
    Tab.TEST_ANY_THREAD = True
    R, A = Tab(0), Tab(1)
    E.br.put("ah:fn:tab", R)
    E.br.put("ah:fn:tabact", A)
    LAST = {}
    PROF = {}

    @JImplements("java.util.function.Function")
    class ProfKey:
        @JOverride
        def apply(self, o):
            return PROF.get(str(o), str(o))
    E.br.put("profile:fn:key", ProfKey())

    def u(X):
        return X.pr.getUuid()

    def mon(X):
        return purse[str(u(X))]

    def jv(x):
        if isinstance(x, bool):
            return JClass("java.lang.Boolean")(x)
        if isinstance(x, int):
            return Integer(x)
        if isinstance(x, str):
            return JString(x)
        return x

    def read(X, view, cat=0, sort=0, rar=0, q="", lmin="", lmax="", mx=200, lid="", sec=-1, slot=-1, sig="", price="", dur=None):
        arr = JArray(JObject)([u(X), jv(view), jv(cat), jv(sort), jv(rar), jv(q), jv(lmin), jv(lmax), jv(mx), jv(lid), jv(sec), jv(slot),
                                jv(sig), jv(price), None if dur is None else jv(dur)])
        s = R.apply(arr)
        if s is None:
            return None
        lines = [ln.split("|") for ln in str(s).split("\n")]
        LAST[str(u(X))] = lines[0]
        return lines

    def act(X, op, arg="", pk=None, tok=None):
        h = LAST[str(u(X))]
        arr = JArray(JObject)([u(X), jv(pk if pk is not None else h[1]), jv(tok if tok is not None else h[2]), jv(op), jv(arg)])
        r = A.apply(arr)
        return None if r is None else str(r)

    def gap():
        time.sleep(0.37)          # past the 350 ms double-click guard (a real second press)

    def norm(s):
        s = str(s)
        for n in NAMES:
            s = s.replace(n, "<P>")
        return re.sub(r"#\d+", "#N", s)

    def ans_of(pg):
        st = str(pg.status)
        if not st:
            return "="
        return ("+" if int(pg.statusKind) == 1 else ("-" if int(pg.statusKind) == 2 else "=")) + st

    def twin(what, page_ans, br_ans):
        K.eq(norm(br_ans), norm(page_ans), "TWIN %s: the bridge answers the page's line" % what)

    def lines(L, tag):
        return [ln for ln in L if ln[0] == tag]

    def page_open(X, view="browse"):
        pg = Pg(X.pr, view)
        X.pm.openCustomPage(X.ref, X.st, pg)
        E.pump(X)
        TB.build_page(E, X)
        return X.pm.getCustomPage()

    def click(X, a, extra=""):
        pg, _ok = TB.click(E, X, '{"a":"%s"%s}' % (a, extra))
        return pg

    # ---------------------------------------------------------------- CREATE: page (SA) vs bridge (BA)
    def page_create(X, item, price, slot=0):
        TB.give(X, item, 10, slot=slot)
        page_open(X, "create")
        pg, cm, ev = TB.build_page(E, X)
        idx = [i for i in range(len(list(pg.cellSec))) if int(pg.cellSec[i]) == 0 and int(pg.cellSlot[i]) == slot]
        click(X, "pick:%d" % idx[0], ',"@AhPrice":""')
        a1 = ans_of(click(X, "create", ',"@AhPrice":"%s"' % price))     # Create BIN before a preview = the page's preview press
        before = set(str(k) for k in Sto.LIVE.keySet())
        pg = click(X, "create", ',"@AhPrice":"%s"' % price)
        new = [str(k) for k in Sto.LIVE.keySet() if str(k) not in before]
        return a1, ans_of(pg), new

    def br_cell(X, item):
        L = read(X, "create")
        cs = [c for c in lines(L, "c") if c[4] == item]
        return cs[0]

    def br_create(X, item, price, slot=0, dur=None):
        TB.give(X, item, 10, slot=slot)
        c = br_cell(X, item)
        d = int(Cfg.DEF_DUR) if dur is None else dur
        arg = "%s|%s|%s|%s|%d" % (c[1], c[2], c[3], price, d)
        a1 = act(X, "create", arg)
        L = read(X, "create", sec=int(c[1]), slot=int(c[2]), sig=c[3], price=str(price), dur=d)
        w = lines(L, "w")[0][1]
        gap()
        before = set(str(k) for k in Sto.LIVE.keySet())
        a2 = act(X, "create", arg)
        new = [str(k) for k in Sto.LIVE.keySet() if str(k) not in before]
        return a1, a2, new, w, arg, L

    m0a, m0b = mon(SA), mon(BA)
    p1, p2, newA = page_create(SA, "Ore_Iron", 500)
    b1, b2, newB, wB, argB, LB = br_create(BA, "Ore_Iron", 500)
    twin("create preview press", p1, b1)
    K.check(b1.startswith("=") and "Check the fee" in b1, "CREATE the first bridge press only previews: %r" % b1)
    K.eq(wB, "1", "CREATE the read says the next press lists (w|1)")
    twin("create", p2, b2)
    K.check(len(newA) == 1 and len(newB) == 1 and b2.startswith("+"), "CREATE one listing each (%s / %s): %r" % (newA, newB, b2))
    K.eq((m0a - mon(SA), int(E.count(SA, "Ore_Iron"))), (m0b - mon(BA), int(E.count(BA, "Ore_Iron"))), "CREATE the same fee taken + the stack left")
    K.check(m0b - mon(BA) > 0, "CREATE a listing fee was taken (%d)" % (m0b - mon(BA)))
    lidA, lidB = newA[0], newB[0]
    fz = lines(LB, "z")[0]
    K.eq(int(fz[3]), m0b - mon(BA), "CREATE the read's z| fee total = the fee taken")
    # the page's fee lines = the read's l| lines (same price / duration / stack)
    TB.give(SA, "Ore_Copper", 10, slot=1)
    page_open(SA, "create")
    pg, cm, ev = TB.build_page(E, SA)
    idx = [i for i in range(len(list(pg.cellSec))) if int(pg.cellSec[i]) == 0 and int(pg.cellSlot[i]) == 1]
    click(SA, "pick:%d" % idx[0], ',"@AhPrice":""')
    click(SA, "preview", ',"@AhPrice":"777"')
    pg, cm, ev = TB.build_page(E, SA)
    pfee = [str(TB.set_of(cm, "#SkyyAhFee%d.Text" % i)) for i in range(3)]
    L = read(SA, "create", sec=0, slot=1, sig=str(pg.pickSig), price="777", dur=int(pg.durIdx))
    K.eq([ln[1] for ln in lines(L, "l")], pfee, "READ create: the 3 fee lines = the page's")
    K.eq(len(lines(L, "c")), len(list(pg.cellSec)), "READ create: the cells = the page's (%d)" % len(lines(L, "c")))
    K.eq(lines(L, "p")[0][:2], ["p", "1"], "READ create: the picked stack is pickable")
    K.eq(str(TB.set_of(cm, "#SkyyAhSelHint.Text")), lines(L, "p")[0][4], "READ create: the lowest-BIN hint = the page's")
    # refusals: a bad price (twin), a changed slot, a bad duration, create pressed again after it listed
    gap()
    pr_ = ans_of(click(SA, "preview", ',"@AhPrice":"abc"'))
    TB.give(BA, "Ore_Copper", 10, slot=1)
    c = br_cell(BA, "Ore_Copper")
    gap()
    br_ = act(BA, "create", "%s|%s|%s|abc|%d" % (c[1], c[2], c[3], int(Cfg.DEF_DUR)))
    twin("a bad price", pr_, br_)
    gap()
    K.eq(act(BA, "create", "%s|%s|%s|500|99" % (c[1], c[2], c[3])), "-Pick a duration.", "REFUSE create: a bad duration")
    gap()
    K.eq(act(BA, "create", "%s|%s|WRONGSIG|500|%d" % (c[1], c[2], int(Cfg.DEF_DUR))), "-That slot changed - pick again.", "REFUSE create: a stack that changed")
    gap()
    K.eq(act(BA, "create", "%s|9999|%s|500|%d" % (c[1], c[3], int(Cfg.DEF_DUR))), "-That slot changed - pick again.", "REFUSE create: a slot past the section (no throw)")
    n0, m0 = Sto.LIVE.size(), mon(BA)
    gap()
    again = act(BA, "create", argB)
    K.check(again.startswith("-") and Sto.LIVE.size() == n0 and mon(BA) == m0, "REFUSE create pressed again after it listed: nothing listed twice, no fee (%r)" % again)
    # a different duration after a preview previews again
    gap()
    d2 = (int(Cfg.DEF_DUR) + 1) % len(list(Cfg.DUR_LABEL))
    k1 = act(BA, "create", "%s|%s|%s|900|%d" % (c[1], c[2], c[3], int(Cfg.DEF_DUR)))
    gap()
    k2 = act(BA, "create", "%s|%s|%s|900|%d" % (c[1], c[2], c[3], d2))
    K.check(k1.startswith("=") and k2.startswith("=") and Sto.LIVE.size() == n0, "CREATE a changed duration previews again (%r / %r)" % (k1, k2))
    # a double click of the listing press
    gap()
    argC = "%s|%s|%s|900|%d" % (c[1], c[2], c[3], d2)
    read(BA, "create")
    x1 = act(BA, "create", argC)
    x2 = act(BA, "create", argC)
    K.check(x1.startswith("+") and x2 == "=One moment." and Sto.LIVE.size() == n0 + 1, "DOUBLE create: one listing, the second press = One moment. (%r / %r)" % (x1, x2))
    lidC = [str(k) for k in Sto.LIVE.keySet() if str(J("AhRec").subStr(Sto.get(k), "item", "id", "")) == "Ore_Copper" and str(J("AhRec").subStr(Sto.get(k), "seller", "key", "")) == str(u(BA))][0]

    # ---------------------------------------------------------------- READ browse = the page's rows, order, colour
    pgb = page_open(SB, "browse")
    L = read(BB, "browse")
    rows = lines(L, "r")
    K.eq([r[1] for r in rows], [str(x) for x in list(pgb.rowIds)], "READ browse: the rows = the page's rows in the page's order (%d)" % len(rows))
    K.check(len(rows) > 0 and all(r[5] == str(J("AhItem").dispColor(Sto.get(r[1]))) for r in rows) and all(r[4].isdigit() for r in rows), "READ browse: each row has its rarity colour + tier")
    K.eq(lines(L, "f")[0][9], str(pgb.filterLine()), "READ browse: the summary line = the page's")
    own = [r for r in read(BA, "browse") if r[0] == "r" and r[1] == lidB]
    K.eq(own[0][10], "1", "READ browse: your own listing is tagged 1 (yours)")
    L = read(BB, "browse", q="zzznothing")
    K.check(len(lines(L, "r")) == 0 and lines(L, "e")[0][1] == "No match for 'zzznothing'", "READ browse: a search with no match = the page's empty text")
    L = read(BB, "browse", cat=99, sort=99, rar=999)
    K.eq(lines(L, "f")[0][1:4], ["0", "0", "0"], "READ browse: bad indexes = 0 (the page's rule)")
    K.check(len(lines(L, "k")) == len(list(J("AhItem").FCAT_LABEL)) and len(lines(L, "s")) == len(list(Pg.SORT_NAME)), "READ browse: k| / s| lists")

    # ---------------------------------------------------------------- BUY: page (SB buys SA's) vs bridge (BB buys BA's); under confirmAbove
    def page_buy(X, lid, confirm=True, price_override=None):
        pg = page_open(X, "browse")
        ri = [i for i in range(len(list(pg.rowIds))) if str(pg.rowIds[i]) == lid]
        pg = click(X, "view:%d" % ri[0], ',"@AhSearch":""')
        if price_override is not None:
            pg.detailPrice = price_override
        a1 = ans_of(click(X, "buy"))
        pg = X.pm.getCustomPage()
        if confirm and pg.armAct is not None:
            return a1, ans_of(click(X, "confirm"))
        return a1, None

    def price_of(lid):
        return int(J("AhRec").lng(Sto.get(lid), "price", 0))

    # the item view read = the page's 9 fact lines
    pg = page_open(SB, "browse")
    ri = [i for i in range(len(list(pg.rowIds))) if str(pg.rowIds[i]) == lidA][0]
    click(SB, "view:%d" % ri, ',"@AhSearch":""')
    pg, cm, ev = TB.build_page(E, SB)
    pf = [str(TB.set_of(cm, "#SkyyAhDFact%d.Text" % i)) for i in range(9)]
    L = read(SB, "item", lid=lidA)
    K.eq([g[2] for g in lines(L, "g")], pf, "READ item: the 9 fact lines = the page's labels")
    K.eq(lines(L, "b")[0][:2], ["b", "buy"], "READ item: Buy now offered")
    LB2 = read(BA, "item", lid=lidB)
    K.eq(lines(LB2, "b")[0][:2], ["b", "own"], "READ item: your own listing = b|own")
    # stale price (twin)
    pa = page_buy(SB, lidA, price_override=price_of(lidA) + 1)[0]
    read(BB, "item", lid=lidB)
    ba = act(BB, "buy", "%s|%d" % (lidB, price_of(lidB) + 1))
    twin("a stale price", pa, ba)
    K.check(ba.startswith("-") and mon(BB) == 1000000, "REFUSE buy: a stale price - nothing paid (%r)" % ba)
    # not enough coins (twin)
    purse[str(u(SB))] = 3
    purse[str(u(BB))] = 3
    gap()
    pa = page_buy(SB, lidA)[0]
    ba = act(BB, "buy", "%s|%d" % (lidB, price_of(lidB)))
    twin("not enough coins", pa, ba)
    purse[str(u(SB))] = 1000000
    purse[str(u(BB))] = 1000000
    # paused (twin)
    Cfg.PAUSED = True
    gap()
    pa = page_buy(SB, lidA)[0]
    read(BB, "browse")
    ba = act(BB, "buy", "%s|%d" % (lidB, price_of(lidB)))
    twin("paused", pa, ba)
    K.check(ba.startswith("-") and "paused" in ba, "REFUSE buy: paused (%r)" % ba)
    L = read(BB, "browse")
    K.check("paused" in lines(L, "B")[0][1], "READ the banner says paused")
    Cfg.PAUSED = False
    # own listing (bridge)
    read(BA, "browse")
    gap()
    oa = act(BA, "buy", "%s|%d" % (lidB, price_of(lidB)))
    K.check(oa.startswith("-") and int(E.count(BA, "Ore_Iron")) == 0, "REFUSE buy: your own listing (%r)" % oa)
    # the real buys (500 < confirmAbove: one press)
    ms, mb, msa, mba = mon(SB), mon(BB), mon(SA), mon(BA)
    pa1, pa2 = page_buy(SB, lidA)
    read(BB, "item", lid=lidB)
    gap()
    ba1 = act(BB, "buy", "%s|%d" % (lidB, price_of(lidB)))
    twin("buy now", pa1, ba1)
    K.check(ba1.startswith("+"), "BUY bought (%r)" % ba1)
    K.eq((ms - mon(SB), int(E.count(SB, "Ore_Iron")), str(J("AhRec").state(Sto.get(lidA)))),
         (mb - mon(BB), int(E.count(BB, "Ore_Iron")), str(J("AhRec").state(Sto.get(lidB)))), "BUY the same coins paid, items given, SOLD")
    K.eq((ms - mon(SB), int(E.count(BB, "Ore_Iron"))), (500, 10), "BUY 500 coins for 10 Ore_Iron")
    # sold (twin) + a double click never pays twice
    gap()
    pg = page_open(SB, "browse")
    pg.view = "item"
    pg.detailId = lidA
    pg.detailPrice = 500
    pa = ans_of(click(SB, "buy"))
    ba = act(BB, "buy", "%s|%d" % (lidB, 500))
    twin("already sold", pa, ba)
    K.eq(mb - mon(BB), 500, "DOUBLE buy: paid once")

    # ---------------------------------------------------------------- BUY at / above confirmAbove: two presses, expiry, profile switch
    Cfg.CONFIRM_ABOVE = 1
    _x, _y, newA2 = page_create(SA, "Ore_Gold", 600, slot=2)
    gap()
    _a, _b, newB2, _w, _arg, _L = br_create(BA, "Ore_Gold", 600, slot=2)
    lidA2, lidB2 = newA2[0], newB2[0]
    ms, mb = mon(SB), mon(BB)
    pa1, pa2 = page_buy(SB, lidA2)
    read(BB, "item", lid=lidB2)
    gap()
    ba1 = act(BB, "buy", "%s|600" % lidB2)
    twin("buy, the confirm press asks", pa1, ba1)
    K.check(ba1.startswith("=Confirm") and mon(BB) == mb, "CONFIRM the first press only asks - nothing paid (%r)" % ba1)
    K.eq(read(BB, "item", lid=lidB2)[-1][:5], ["b", "buy", "600", "1", "1"], "READ item: b|buy|price|needs confirm|ARMED")
    # expiry: the confirm ran out -> the press asks again, nothing paid
    Tab.SHADOW.get(u(BB)).armUntil = 0
    gap()
    bx = act(BB, "buy", "%s|600" % lidB2)
    K.check(bx.startswith("=Confirm") and mon(BB) == mb, "CONFIRM expired: the press asks again, nothing paid (%r)" % bx)
    # a different press drops the arm (as any other click on the page)
    gap()
    K.eq(act(BB, "no"), "=Nothing done.", "NO = the page's No")
    gap()
    by = act(BB, "buy", "%s|600" % lidB2)
    K.check(by.startswith("=Confirm") and mon(BB) == mb, "CONFIRM dropped by another press: asks again (%r)" % by)
    # profile switch between the two presses: refused, and the arm never crosses profiles
    PROF[str(u(BB))] = "otherprofile"
    gap()
    pz = act(BB, "buy", "%s|600" % lidB2)
    K.check(pz.startswith("=Your profile changed") and mon(BB) == mb, "REFUSE a profile switch: nothing moves (%r)" % pz)
    read(BB, "item", lid=lidB2)
    del PROF[str(u(BB))]
    read(BB, "item", lid=lidB2)
    gap()
    pz2 = act(BB, "buy", "%s|600" % lidB2)
    K.check(pz2.startswith("=Confirm") and mon(BB) == mb, "PROFILE back: the old arm is gone - the press asks again (%r)" % pz2)
    # stale token
    h_old = list(LAST[str(u(BB))])
    read(BB, "item", lid=lidB2)
    gap()
    st_ = act(BB, "buy", "%s|600" % lidB2, tok=h_old[2])
    K.check(st_.startswith("=The Auction House changed") and mon(BB) == mb, "REFUSE a stale token (%r)" % st_)
    # the armed press (pz2 armed it) buys (twin)
    gap()
    ba2 = act(BB, "buy", "%s|600" % lidB2)
    twin("buy, the second press buys", pa2, ba2)
    K.check(ba2.startswith("+") and mb - mon(BB) == 600 and ms - mon(SB) == 600, "CONFIRM the second press buys (%r)" % ba2)
    Cfg.CONFIRM_ABOVE = 10000

    # ---------------------------------------------------------------- grace (twin)
    Cfg.GRACE_MS = 60000
    _x, _y, newA3 = page_create(SA, "Ore_Silver", 400, slot=3)
    gap()
    _a, _b, newB3, _w, _arg, _L = br_create(BA, "Ore_Silver", 400, slot=3)
    pg = page_open(SB, "browse")
    ri = [i for i in range(len(list(pg.rowIds))) if str(pg.rowIds[i]) == newA3[0]][0]
    click(SB, "view:%d" % ri, ',"@AhSearch":""')
    pa = ans_of(click(SB, "buy"))
    L = read(BB, "item", lid=newB3[0])
    gap()
    ba = act(BB, "buy", "%s|400" % newB3[0])
    twin("grace", pa, ba)
    K.eq(lines(L, "b")[0][1], "grace", "READ item: b|grace while in grace")
    Cfg.GRACE_MS = 0

    # ---------------------------------------------------------------- MANAGE reads + CANCEL (two presses) twin
    pgm = page_open(SA, "manage")
    pg, cm, ev = TB.build_page(E, SA)
    L = read(SA, "manage")
    K.eq([m[1] for m in lines(L, "m")], [str(x) for x in list(pg.mIds)], "READ manage: the rows = the page's rows in order")
    K.eq([m[10] for m in lines(L, "m")], [str(TB.set_of(cm, "#SkyyAhMState%d.Text" % i)) for i in range(len(list(pg.mIds)))], "READ manage: the state lines = the page's")
    K.eq(lines(L, "g")[0][7], str(TB.set_of(cm, "#SkyyAhMSumTxt.Text")), "READ manage: the summary = the page's")
    i = [k for k in range(len(list(pg.mIds))) if str(pg.mIds[k]) == newA3[0]][0]
    ca1 = ans_of(click(SA, "mact:%d" % i))
    ca2 = ans_of(click(SA, "myes:%d" % i))
    read(BA, "manage")
    gap()
    cb1 = act(BA, "cancel", newB3[0])
    K.eq(lines(read(BA, "manage"), "m")[[m[1] for m in lines(read(BA, "manage"), "m")].index(newB3[0])][8], "1", "READ manage: the cancel is armed")
    gap()
    cb2 = act(BA, "cancel", newB3[0])
    twin("cancel asks", ca1, cb1)
    twin("cancel", ca2, cb2)
    K.check(cb2.startswith("+") and str(J("AhRec").state(Sto.readAny(newB3[0]))) == "CANCELLED" and Sto.get(newB3[0]) is None and int(E.count(BA, "Ore_Silver")) == 10, "CANCEL the item is back, the record CANCELLED + archived (%r)" % cb2)
    gap()
    K.eq(act(BA, "cancel", lidA), "-That listing is not yours or is gone.", "REFUSE cancel: not yours")
    gap()
    K.eq(act(BA, "claim", "999999"), "-Nothing to claim there.", "REFUSE claim: nothing there")

    # ---------------------------------------------------------------- CLAIM coins (twin)
    pg = page_open(SA, "manage")
    i = [k for k in range(len(list(pg.mIds))) if str(pg.mIds[k]) == lidA][0]
    m1 = mon(SA)
    pc = ans_of(click(SA, "mact:%d" % i))
    read(BA, "manage")
    m2 = mon(BA)
    gap()
    bc = act(BA, "claim", lidB)
    twin("claim coins", pc, bc)
    K.eq(mon(SA) - m1, mon(BA) - m2, "CLAIM the same coins paid (%d)" % (mon(BA) - m2))
    K.check(mon(BA) - m2 > 0, "CLAIM coins paid")

    # ---------------------------------------------------------------- CLAIM item with a FULL inventory (twin), then with room
    def fill(X):
        for sec, n in (("hotbar", 9), ("storage", 36)):
            for s in range(n):
                TB.give(X, "Ore_Cobalt", 1, slot=s, sec=sec)
    _x, _y, newA4 = page_create(SA, "Ore_Copper", 450, slot=4)
    gap()
    _a, _b, newB4, _w, _arg, _L = br_create(BA, "Ore_Copper", 450, slot=4)
    fill(SA)
    fill(BA)
    pg = page_open(SA, "manage")
    i = [k for k in range(len(list(pg.mIds))) if str(pg.mIds[k]) == newA4[0]][0]
    click(SA, "mact:%d" % i)
    pk1 = ans_of(click(SA, "myes:%d" % i))
    read(BA, "manage")
    gap()
    act(BA, "cancel", newB4[0])
    gap()
    bk1 = act(BA, "cancel", newB4[0])
    twin("cancel with a full inventory (kept)", pk1, bk1)
    pg = page_open(SA, "manage")
    i = [k for k in range(len(list(pg.mIds))) if str(pg.mIds[k]) == newA4[0]][0]
    pk2 = ans_of(click(SA, "mact:%d" % i))
    read(BA, "manage")
    gap()
    bk2 = act(BA, "claim", newB4[0])
    twin("claim item, inventory full", pk2, bk2)
    K.check(bk2.startswith("-") and "full" in bk2 and int(E.count(BA, "Ore_Copper")) == 0 and str(J("AhRec").claim(Sto.get(newB4[0]), "sellerItem")) == "OWED",
            "FULL nothing lost: the item still waits (%r)" % bk2)
    from jpype import JShort
    for X in (SA, BA):
        X.inv.getStorage().removeItemStackFromSlot(JShort(0))
    pg = page_open(SA, "manage")
    i = [k for k in range(len(list(pg.mIds))) if str(pg.mIds[k]) == newA4[0]][0]
    pk3 = ans_of(click(SA, "mact:%d" % i))
    read(BA, "manage")
    gap()
    bk3 = act(BA, "claim", newB4[0])
    twin("claim item with room", pk3, bk3)
    K.check(bk3.startswith("+") and int(E.count(BA, "Ore_Copper")) == 10, "CLAIM the item came back whole (%r)" % bk3)
    gap()
    bk4 = act(BA, "claim", newB4[0])
    K.check(bk4.startswith("-") and int(E.count(BA, "Ore_Copper")) == 10, "REFUSE claim twice: nothing given twice (%r)" % bk4)

    # ---------------------------------------------------------------- CLAIM ALL at / above claimAllConfirmAbove (twin)
    Cfg.CLAIMALL_ABOVE = 1
    read(BB, "browse")
    gap()
    act(BB, "buy", "%s|900" % lidC)                    # BA's Ore_Copper at 900 sells -> coins owed to BA
    _x, _y, newA5 = page_create(SA, "Ore_Copper", 900, slot=5)
    page_buy(SB, newA5[0])
    pg = page_open(SA, "manage")
    m1 = mon(SA)
    pa1 = ans_of(click(SA, "claimall"))
    pa2 = ans_of(click(SA, "claimyes"))
    read(BA, "manage")
    m2 = mon(BA)
    gap()
    ba1 = act(BA, "claimall")
    K.eq(lines(read(BA, "manage"), "g")[0][6], "1", "READ manage: claim all armed")
    gap()
    ba2 = act(BA, "claimall")
    twin("claim all asks", pa1, ba1)
    twin("claim all", pa2, ba2)
    K.check(mon(BA) - m2 == mon(SA) - m1 and mon(BA) - m2 > 0 and mon(BA) - m2 == 600 - int(Cfg.tax(600)) + 900 - int(Cfg.tax(900)), "CLAIMALL the same coins (%d)" % (mon(BA) - m2))
    Cfg.CLAIMALL_ABOVE = 100000

    # ---------------------------------------------------------------- the guards
    gap()
    K.eq(act(BB, "frobnicate"), "-Unknown Auction House action.", "REFUSE an unknown op")
    gap()
    K.eq(act(BB, "buy", "nonsense"), "-Unknown Auction House action.", "REFUSE a bad buy argument")
    Tab.CLOSED = True
    K.eq(act(BB, "buy", "%s|1" % lidA), "-The Auction House is closing - nothing changed.", "REFUSE shutdown started (CLOSED)")
    Tab.CLOSED = False
    Tab.TEST_ANY_THREAD = False
    r0 = R.apply(JArray(JObject)([u(BB), JString("browse")]))
    K.notes.append("off-thread read in the stand-ins (TEST_ANY_THREAD false) answered %s" % ("null" if r0 is None else "a read"))
    Tab.TEST_ANY_THREAD = True
    K.check(R.apply(JArray(JObject)([JString("x")])) is None, "READ without a UUID = null")
    # a player who leaves loses the bridge state
    K.check(Tab.SHADOW.containsKey(u(BB)), "QUIT the bridge state exists")
    Tab.forget(u(BB))
    K.check(not Tab.SHADOW.containsKey(u(BB)) and not Tab.TOK.containsKey(u(BB)), "QUIT forget drops it")
    # the coin books: every coin that left a purse is a fee, a tax, or in another purse
    K.save()
    sys.stdout.flush()
    os._exit(0)


# ------------------------------------------------------------------------------------------------------------------- live data reads
def run_livetab(out, jar, scratch, home):
    from jpype import JClass, JArray, JObject, JString
    K = HK.Child(out)
    W = H.boot(scratch, jar, "livetab")
    E = W.E
    J = lambda n: JClass(PKG + n)
    E.br = J("HubBar").map()
    TB.fake_coins(E.br, {})
    h0 = HK.tree_hash(home)
    Tab = J("AhTabFn")
    Tab.TEST_ANY_THREAD = True
    R = Tab(0)
    snaps = []
    for start in (1, 2):
        TB.ah_prep(E, J, home)
        n = int(J("AhStore").LIVE.size())
        tot = 0
        for X in (W.P, W.O):
            for v in ("browse", "item", "create", "manage"):
                lid = ""
                if v == "item" and n > 0:
                    lid = str(list(J("AhStore").LIVE.keySet())[0])
                s = R.apply(JArray(JObject)([X.pr.getUuid(), JString(v), None, None, None, None, None, None, None, JString(lid)]))
                K.check(s is not None and str(s).startswith("h|"), "DT%d %s read (%d lines)" % (start, v, 0 if s is None else len(str(s).split("\n"))))
                tot += 0 if s is None else len(str(s).split("\n"))
        print("   DT%d: %d open records, %d lines read" % (start, n, tot))
        snaps.append(HK.tree_hash(home))
    changed = sorted(k for k in set(h0) | set(snaps[0]) if h0.get(k) != snaps[0].get(k))
    K.check(not changed, "DT the first load + reads change no file: %s" % changed)
    K.check(snaps[0] == snaps[1], "DT the second load + reads change nothing")
    K.save()
    sys.stdout.flush()
    os._exit(0)


if __name__ == "__main__":
    ph = [("static", run_static), ("tab", run_tab), ("claim17", T17.run_claim), ("exec16", T16.run_exec), ("hub", T10.run_hub), ("rb", T11.run_rb),
          ("live", T16.run_live), ("livetab", run_livetab)]
    HK.run(name="SkyyAuctions", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=ph, script=__file__, live=(T16.LIVE_DIR, "Skyy_SkyyAuctions"))
