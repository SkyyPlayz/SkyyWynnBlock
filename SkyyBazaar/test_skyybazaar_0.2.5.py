"""Harness for SkyyBazaar 0.2.5 (simpler buy and sell: the four big buttons + one short step; the Enchanted metals in the Smithing tab;
tools/bazaar_0_2_5_patch.py). Build first:
    python tools/bazaar_0_2_5_patch.py && python SkyyBazaar/build_skyybazaar_0.2.5.py --with SkyyCollections/SkyyCollections-0.2.36.jar
    python SkyyBazaar/test_skyybazaar_0.2.5.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, -Xverify:all, tools/harness_kit.py + the 0.1.20 / 0.2.0 stand-in engine; every new code path is EXECUTED):
  S     static   the patch re-runs to identical bytes; line endings kept; no new command / system / setting / bridge key; the old panel's
                 ids and click paths are gone from the jar
  A     verify   every class loads + initialises
  C     compare  0.2.4 -> 0.2.5 (EXPECT below: BzPage + Catalog's MOVE / display tables + the version texts)
  K     catalog  every Catalog constant = 0.2.4's except MV_ID / MV_SPEC (+ the 18 metals Mining>Smithing) and DSP_KEY (the two tabs' order)
  M     metals   on the stand-in engine: the 18 Enchanted metals are in Smithing (right after their bar), not in Mining; their file category
                 stays Mining; SELL SMITHING sells them, SELL MINING does not
  P     page     the Market > Bazaar page built into REAL builders (kit 1.7 rules, the menu pattern) on every state, and EXECUTED through
                 the real click path: the four big buttons with their prices; BUY NOW / SELL NOW / BUY ORDER / SELL OFFER (defaults, chips,
                 typed amounts / prices, the price chips' clamps with their reasons, the totals, CONFIRM, Cancel); the Confirm-buys-from
                 gold CONFIRM; price moved up / down; not enough coins; full inventory; extra-data stacks; double clicks; a typed amount
                 never confirmed unseen; coins + items conserved over the whole session (purses + escrow + claims + the market's flow)
  D     live     scratch COPIES of the live NewBetaTest Skyy_SkyyBazaar: the 0.2.5 start = the 0.2.4 start, a second 0.2.5 start writes nothing
  AA    audit    engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, subprocess, importlib.util, json, shutil, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import hub_tab_harness as H

VERSION = "0.2.5"
PKG = "com.skyy.bazaar."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyBazaar-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyBazaar-0.2.4.jar")
GEN = os.path.join(HERE, "build_skyybazaar_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyybazaar_0.2.4.py")
PATCH = os.path.join(ROOT, "tools", "bazaar_0_2_5_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "bz1", "t")))
LIVE = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyBazaar")
EXPECT = {"BzPage": ["+f xDrawn", "+f xPF", "+f xSeen", "+f xSeenP", "+f xSeenQ", "+f xWhy", "+m bandEnd", "+m cap1", "+m holdText", "+m stepAct",
                     "+m stepAll", "+m stepBand", "+m stepDone", "+m stepPanel", "+m stepPrice", "+m stepQty", "+m stepWhy", "-m amountAction",
                     "-m arm", "-m buyClick", "-m buyWhy", "-m defPrice", "-m oqty", "-m ordAct", "-m ordEditor", "-m sellWhy", "~c ", "~m evd",
                     "~m handleDataEvent", "~m infoColor", "~m render"],
          "Catalog": ["~<clinit>"],                                    # MV_ID / MV_SPEC / DSP_KEY (phase K checks each)
          "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "SkyyBazaarPlugin": ["~m setup"]}   # + the version texts
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = []
METALS = ["Skyy_Ench_" + k for k in ("Adamantite", "Azurvane", "Bronze", "Chromium", "Cinder", "Cobalt", "Copper", "Dusk", "Electrum", "Gold",
                                     "Iron", "Lead", "Lumen", "Mithril", "Silver", "Slag", "Thorium", "Titanium")]


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


def grp(v):
    return "{:,}".format(int(v))


# ------------------------------------------------------------------------------------------------------------------- S
def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.count('VERSION = "0.2.5"') == 1 and g.startswith('"""SkyyBazaar 0.2.5'), "S version + header")
    for w in ("registerSystem(", "registerCommand(", "CFG.row(", "Server Setup", "bridge().put("):
        K.check(g.count(w) == o.count(w), "S no new %s (%d)" % (w, g.count(w)))
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    z = zipfile.ZipFile(jar)
    pg = z.read("com/skyy/bazaar/BzPage.class")
    gone = [x for x in (b"SkyyBzBuy1", b"SkyyBzBuyStk", b"SkyyBzSell1", b"SkyyBzSellStk", b"SkyyBzSellAll\"", b"SkyyBzAmtBox", b"SkyyBzABuy",
                        b"SkyyBzOBid", b"SkyyBzOAsk", b"SkyyBzOq0", b"SkyyBzOp0", b"SkyyBzOBest", b"SkyyBzOMkt", b"SkyyBzOPlace", b"SkyyBzODisc",
                        b"Best -1", b"Can't place") if x in pg]
    K.check(not gone, "S the old panel's ids / texts are gone from BzPage: %s" % gone)
    K.check(all(x in pg for x in (b"SkyyBzQBuy", b"SkyyBzQSell", b"SkyyBzQBid", b"SkyyBzQAsk", b"SkyyBzXOk", b"Beat best by 1", b"All you can afford")),
            "S the four big buttons + the step are in BzPage")
    K.check("METALS_SMITH" in g and g.count('MOVE_TAB.update((p, ("Mining", "Smithing")) for p in METALS_SMITH)') == 1, "S the metals move is in the build")
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
    K.eq(diff, ["DSP_KEY", "MV_ID", "MV_SPEC"], "K only the move + display tables differ from 0.2.4 (%d constants)" % len(a))
    mo, mn = dict(zip(a.get("MV_ID", []), a.get("MV_SPEC", []))), dict(zip(b.get("MV_ID", []), b.get("MV_SPEC", [])))
    K.check(all(mn.get(k) == v for k, v in mo.items()), "K every 0.2.4 move (the saplings) kept")
    K.eq(sorted(k for k in mn if k not in mo), METALS, "K the added moves = the 18 Enchanted metals")
    K.check(all(mn[k] == "Mining>Smithing" for k in METALS), "K each one Mining>Smithing")
    do, dn = a.get("DSP_KEY", []), b.get("DSP_KEY", [])
    K.check([x for x in do if not x.startswith(("Mining|", "Smithing|"))] == [x for x in dn if not x.startswith(("Mining|", "Smithing|"))],
            "K the other tabs' display order is unchanged")
    K.check(sorted(do) != sorted(dn) and all(("Smithing|" + m) in dn and ("Mining|" + m) not in dn for m in METALS),
            "K the display table lists each metal in Smithing, none in Mining")
    sm = [x.split("|")[1] for x in dn if x.startswith("Smithing|")]
    K.check(sm.index("Skyy_Ench_Iron") == sm.index("Ingredient_Bar_Iron") + 1 and sm.index("Skyy_Ench_Gold") == sm.index("Ingredient_Bar_Gold") + 1,
            "K an Enchanted ingot sits right after its bar (Iron, Gold)")
    K.save()


# ------------------------------------------------------------------------------------------------------------------- shared world
def world(scratch, jar, label):
    from jpype import JClass
    T200 = tmod(os.path.join(HERE, "test_skyybazaar_0.2.0.py"), "tbz0200_" + label)
    T20 = T200.T20
    W = T20.boot2(scratch, [jar], label)
    W.E.br = JClass(PKG + "HubBar").map()
    E = W.E
    J = lambda n: JClass(PKG + n)
    home = os.path.join(scratch, "home_" + label)
    T200.prep(E, J, home)
    T20.fake_items(E, [str(p.id) for p in J("Catalog").all()])
    fx = T200.Fx(E, J)
    return T200, T20, W, E, J, fx, home


# ------------------------------------------------------------------------------------------------------------------- M
def run_metals(out, jar, scratch, _home):
    K = HK.Child(out)
    T200, T20, W, E, J, fx, home = world(scratch, jar, "metals")
    C, T = J("Catalog"), J("Trader")
    mining = [str(p.id) for p in C.inCat("Mining")]
    smith = [str(p.id) for p in C.inCat("Smithing")]
    K.check(not [m for m in METALS if m in mining], "M no Enchanted metal in the Mining tab (%d products there)" % len(mining))
    K.check(all(m in smith for m in METALS), "M all 18 in the Smithing tab (%d products there)" % len(smith))
    K.eq(sorted(set(str(x) for m in METALS for x in C.tabsOf(C.get(m)))), ["Smithing"], "M tabsOf = Smithing only")
    K.eq(sorted(set(str(C.get(m).cat) for m in METALS)), ["Mining"], "M the file category stays Mining (no saved-data change)")
    K.check(smith.index("Skyy_Ench_Copper") == smith.index("Ingredient_Bar_Copper") + 1, "M Enchanted Copper sits right after the Copper Bar")
    K.check("Ingredient_Bar_Iron" in smith and "Ore_Iron" in mining, "M the bars stay Smithing, the ores Mining")
    A, Bb, _C = T200.mkplayers(W)
    ua = A.pr.getUuid()
    fx.purse[str(ua)] = 1000
    T20.give(A, "Skyy_Ench_Iron", 3, 0)
    fx.bags[(str(ua), "Skyy_Ench_Copper")] = 2
    pm, ps = [int(x) for x in T.preview(A.pl, ua, "Mining")], [int(x) for x in T.preview(A.pl, ua, "Smithing")]
    K.check(pm[0] == 0 and ps[0] == 5 and ps[2] == 2, "M SELL MINING would sell none of them %s, SELL SMITHING sells all 5 (2 from the Void) %s" % (pm, ps))
    r = T.sellInventory(A.pl, ua, "Mining", "Mining")
    K.check(int(E.count(A, "Skyy_Ench_Iron")) == 3 and fx.bags[(str(ua), "Skyy_Ench_Copper")] == 2, "M SELL MINING leaves the metals (%s)" % r.msg)
    p0 = fx.purse[str(ua)]
    r = T.sellInventory(A.pl, ua, "Alice", "Smithing")
    K.check(int(E.count(A, "Skyy_Ench_Iron")) == 0 and fx.bags[(str(ua), "Skyy_Ench_Copper")] == 0 and fx.purse[str(ua)] > p0,
            "M SELL SMITHING sells them (%s)" % r.msg)
    K.save()


# ------------------------------------------------------------------------------------------------------------------- P
def run_page(out, jar, scratch, _home):
    from jpype import JClass, JShort
    K = HK.Child(out)
    T200, T20, W, E, J, fx, home = world(scratch, jar, "page")
    C, M, Bk, Od, Fl, T, OC, CF = (J("Catalog"), J("Market"), J("BzBook"), J("BzOrders"), J("BzFill"), J("Trader"), J("BzOrdCfg"), J("BzConfirm"))
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

    def rebase():
        """the conservation baseline now (call after the harness itself creates or removes items / coins)"""
        mm.drain()
        c1, i1 = T200.totals(J, fx, [A, Bb], ids)
        base["c"], base["i"] = c1 + mm.coins, i1[iid] - mm.items.get(iid, 0)

    def conserved(what):
        mm.drain()
        c1, i1 = T200.totals(J, fx, [A, Bb], ids)
        K.check(c1 + mm.coins == base["c"] and i1[iid] - mm.items.get(iid, 0) == base["i"],
                "P CONSERVED after %s: coins %d (+ market %d) vs %d, items %d (- market %d) vs %d" % (what, c1, mm.coins, base["c"], i1[iid], mm.items.get(iid, 0), base["i"]))
    mt = int(OC.minTotal())

    S, Bp = int(M.quote(iid, 1, False)), int(M.quote(iid, 1, True))
    stk = int(T.stack(iid))
    E.br.put("hub:last:" + sa, JClass("java.util.concurrent.ConcurrentHashMap")())
    J("BzHubOpen").register()
    J("HubBar").open(A.pr, ua, "market", "bazaar")
    E.pump(A)
    CF.set(ua, 10 ** 12)          # no gold CONFIRM unless a test asks for it

    def click(a, fresh=True, **kw):
        pg_ = A.pm.getCustomPage()
        pg_.cfShown = 0
        if fresh:
            pg_.xDrawn = 0
        d = {"a": a, "@BzFind": "", "@BzCf": ""}
        d.update(kw)
        A.pm.handleLegacyCustomPageEvent(A.ref, A.st, E.CPE(E.CPT.Data, json.dumps(d)))
        E.pump(A)
        return A.pm.getCustomPage()

    def built(what):
        return H.built(K, E, A, what)

    def st(pg):
        return int(pg.oSide)

    def sel(pg):
        pg.sel = iid
        pg.cat = C.get(iid).cat
        pg.oSide = -1

    pg = A.pm.getCustomPage()
    sel(pg)
    # ---------------------------------------------------------------- the four big buttons
    T20.give(A, iid, 7, 0)
    fx.bags[(sa, iid)] = 3
    rebase()
    pg, cm, ev, ap = built("P product panel")
    bs = [s for s, _t in ev]
    K.check(all(x in bs for x in ("#SkyyBzQBuy", "#SkyyBzQSell", "#SkyyBzQBid", "#SkyyBzQAsk")), "P the four big buttons are bound")
    K.check(not [x for x in bs if x in ("#SkyyBzBuy1", "#SkyyBzSell1", "#SkyyBzSellAll", "#SkyyBzABuy", "#SkyyBzOBid", "#SkyyBzAmt")], "P none of the old trade buttons")
    b1, s1 = int(Fl.quote(A.pl, ua, iid, 1, True)), int(Fl.quote(A.pl, ua, iid, 1, False))
    K.eq(H.set_of(cm, "#SkyyBzQp0.Text"), "%s coins each" % grp(b1), "P BUY NOW shows the instant buy price each")
    K.eq(H.set_of(cm, "#SkyyBzQp1.Text"), "%s coins each" % grp(s1), "P SELL NOW shows the instant sell price each")
    K.eq(H.set_of(cm, "#SkyyBzQp2.Text"), "No buy orders yet", "P BUY ORDER with an empty book")
    K.eq(H.set_of(cm, "#SkyyBzQp3.Text"), "No sell offers yet", "P SELL OFFER with an empty book")
    K.eq(H.set_of(cm, "#SkyyBzPHold.Text"), "You have 10   (3 in the Void)", "P You have = inventory + the Void")
    K.check(H.set_of(cm, "#SkyyBzQHint.Text", ).startswith("Buy now and Sell now trade at once"), "P the hint line")
    K.check(not any("@BzOQ" in t or "@BzOP" in t or "@BzAmount" in t for _s, t in ev), "P the main panel's bindings carry no step / amount field")
    # ---------------------------------------------------------------- BUY NOW
    pg = click("qbuy")
    K.check(st(pg) == 0 and str(pg.oQty) == "1", "P BUY NOW opens its step at amount 1 (%s, %s)" % (st(pg), pg.oQty))
    pg, cm, ev, ap = built("P BUY NOW step")
    K.eq(H.set_of(cm, "#SkyyBzXh.Text"), "Buy now", "P the step heading")
    K.eq(H.set_of(cm, "#SkyyBzXt.Text"), "You pay %s coins for 1" % grp(b1), "P the total line")
    K.eq(H.set_of(cm, "#SkyyBzXa1.Text"), str(stk), "P the stack chip")
    K.eq(H.set_of(cm, "#SkyyBzXa2.Text"), "All you can afford", "P the all chip says afford on a buy")
    K.check(not any("@BzOP" in t for _s, t in ev) and any("@BzOQ" in t for _s, t in ev), "P BUY NOW: the bindings carry the amount, never the (absent) price field")
    K.check(any(s == "#SkyyBzXOk" and "xok:0" in t for s, t in ev) and "#SkyyBzXBack" in [s for s, _t in ev], "P CONFIRM (xok:0) + Cancel bound")
    pg = click("xa:1", **{"@BzOQ": "1"})
    K.eq(str(pg.oQty), str(stk), "P the stack chip sets the amount")
    pg = click("xa:2", **{"@BzOQ": str(stk)})
    lim = [int(x) for x in pg.limits(A.pl, ua, iid)]
    K.eq(str(pg.oQty), str(lim[0]), "P All you can afford = the purse / room / per-trade cap (%s)" % lim[:2])
    pg = click("xa:0", **{"@BzOQ": "5"})
    K.eq(str(pg.oQty), "1", "P the 1 chip")
    pg = click("xupd", **{"@BzOQ": "5"})
    pg, cm, ev, ap = built("P BUY NOW typed 5")
    q5 = int(Fl.quote(A.pl, ua, iid, 5, True))
    K.eq(H.set_of(cm, "#SkyyBzXt.Text"), "You pay %s coins for 5" % grp(q5), "P Enter re-prices the typed amount")
    p0, n0 = fx.purse[sa], int(E.count(A, iid))
    pg.xDrawn = int(JClass("java.lang.System").currentTimeMillis())      # the step was JUST drawn (a double click's second half)
    pg = click("xok:0", fresh=False, **{"@BzOQ": "5"})
    K.check(fx.purse[sa] == p0 and int(E.count(A, iid)) == n0 and st(pg) == 0, "P a CONFIRM within 0.3 s of the step being drawn (a double click) does nothing")
    pg = click("xok:0", **{"@BzOQ": "5"})
    K.check(fx.purse[sa] == p0 - q5 and int(E.count(A, iid)) == n0 + 5 and st(pg) == -1 and str(pg.info).startswith("bought"),
            "P CONFIRM buys exactly the 5 shown for exactly the total shown and closes the step (%s)" % pg.info)
    pg = click("xok:0", **{"@BzOQ": "5"})
    K.check(fx.purse[sa] == p0 - q5 and int(E.count(A, iid)) == n0 + 5, "P a second CONFIRM after the step closed buys nothing (%s)" % pg.info)
    conserved("BUY NOW")
    # a typed amount is never confirmed unseen
    pg = click("qbuy")
    p0, n0 = fx.purse[sa], int(E.count(A, iid))
    pg = click("xok:0", **{"@BzOQ": "3"})
    K.check(fx.purse[sa] == p0 and int(E.count(A, iid)) == n0 and str(pg.info).startswith("Check the new total"), "P a typed amount not yet shown: re-priced, nothing bought (%s)" % pg.info)
    q3 = int(Fl.quote(A.pl, ua, iid, 3, True))
    pg = click("xok:0", **{"@BzOQ": "3"})
    K.check(fx.purse[sa] == p0 - q3 and int(E.count(A, iid)) == n0 + 3, "P the next CONFIRM buys the 3 now shown")
    # the Confirm-buys-from amount: gold CONFIRM first
    CF.set(ua, 0)
    pg = click("qbuy")
    pg = click("xupd", **{"@BzOQ": "2"})
    p0 = fx.purse[sa]
    pg = click("xok:0", **{"@BzOQ": "2"})
    K.check(fx.purse[sa] == p0 and "click CONFIRM" in str(pg.info) and int(pg.oArmUntil) > 0, "P a buy at / over Confirm-buys-from asks first (%s)" % pg.info)
    pg, cm, ev, ap = built("P BUY NOW armed")
    K.check(any("CONFIRM - " in (t or "") and "SkyyBzXOk" in (t or "") for ty, s, t, d in cm), "P the CONFIRM button is drawn gold with its total")
    pg = click("xok:0", **{"@BzOQ": "2"})
    K.check(fx.purse[sa] < p0 and str(pg.info).startswith("bought"), "P the gold CONFIRM buys (%s)" % pg.info)
    CF.set(ua, 10 ** 12)
    # the price went up between seeing and confirming
    pg = click("qbuy")
    pg = click("xupd", **{"@BzOQ": "4"})
    seen = int(pg.xSeen)
    M.apply(iid, 400, True)
    p0, n0 = fx.purse[sa], int(E.count(A, iid))
    pg = click("xok:0", **{"@BzOQ": "4"})
    K.check(fx.purse[sa] == p0 and int(E.count(A, iid)) == n0 and str(pg.info).startswith("The price went up") and int(pg.oArmP) > seen,
            "P the price went up: nothing bought, the gold CONFIRM at the new total (%s)" % pg.info)
    newp = int(pg.oArmP)
    pg = click("xok:0", **{"@BzOQ": "4"})
    K.check(fx.purse[sa] == p0 - newp and int(E.count(A, iid)) == n0 + 4, "P the next CONFIRM buys at the new total (%d)" % newp)
    M.reset(iid)
    conserved("BUY NOW (confirm amount, typed, price moved)")
    # not enough coins
    keep = fx.purse[sa]
    fx.purse[sa] = 1
    pg = click("qbuy")
    pg, cm, ev, ap = built("P BUY NOW broke")
    K.eq(H.set_of(cm, "#SkyyBzXw.Text"), "You cannot afford even 1", "P not enough coins: the plain reason")
    K.eq(H.set_of(cm, "#SkyyBzXt.Text"), "Total -", "P no total when it cannot go")
    n0 = int(E.count(A, iid))
    pg = click("xok:0", **{"@BzOQ": "1"})
    K.check(fx.purse[sa] == 1 and int(E.count(A, iid)) == n0 and str(pg.info) == "You cannot afford even 1", "P CONFIRM refuses (%s)" % pg.info)
    fx.purse[sa] = keep
    # full inventory
    saved = []
    for c in (A.inv.getStorage(), A.inv.getHotbar(), A.inv.getBackpack()):
        if c is None:
            continue
        for s_ in range(int(c.getCapacity())):
            saved.append((c, s_, c.getItemStack(JShort(s_))))
            if c.getItemStack(JShort(s_)) is None or c.getItemStack(JShort(s_)).isEmpty():
                c.setItemStackForSlot(JShort(s_), JClass("com.hypixel.hytale.server.core.inventory.ItemStack")(filler, 1))
    for c in (A.inv.getStorage(), A.inv.getHotbar(), A.inv.getBackpack()):
        if c is None:
            continue
        for s_ in range(int(c.getCapacity())):
            it = c.getItemStack(JShort(s_))
            if it is not None and str(it.getItemId()) == iid and int(it.getQuantity()) < stk:
                saved.append((c, s_, it))
                c.setItemStackForSlot(JShort(s_), JClass("com.hypixel.hytale.server.core.inventory.ItemStack")(iid, stk))
    pg = click("qbuy")
    pg, cm, ev, ap = built("P BUY NOW full inventory")
    K.eq(H.set_of(cm, "#SkyyBzXw.Text"), "Your inventory is full - make room first", "P full inventory: the plain reason")
    p0, n0 = fx.purse[sa], int(E.count(A, iid))
    pg = click("xok:0", **{"@BzOQ": "1"})
    K.check(fx.purse[sa] == p0 and int(E.count(A, iid)) == n0, "P full inventory: CONFIRM moves nothing (%s)" % pg.info)
    for c, s_, it in reversed(saved):
        c.setItemStackForSlot(JShort(s_), it)
    conserved("the full-inventory test (stacks put back)")
    pg = click("xback")
    K.eq(st(pg), -1, "P Cancel closes the step")
    # ---------------------------------------------------------------- SELL NOW
    held = int(E.count(A, iid)) + fx.bags.get((sa, iid), 0)
    pg = click("qsell")
    K.check(st(pg) == 1 and str(pg.oQty) == str(held), "P SELL NOW starts at all you hold (%s = %d)" % (pg.oQty, held))
    pg, cm, ev, ap = built("P SELL NOW step")
    qs = int(Fl.quote(A.pl, ua, iid, held, False))
    K.eq(H.set_of(cm, "#SkyyBzXt.Text"), "You get %s coins for %d" % (grp(qs), held), "P the sell total")
    K.eq(H.set_of(cm, "#SkyyBzXa2.Text"), "All you have", "P the all chip says have on a sell")
    pg = click("xupd", **{"@BzOQ": str(held + 5)})
    pg, cm, ev, ap = built("P SELL NOW too many")
    K.eq(H.set_of(cm, "#SkyyBzXw.Text"), "You have %d - lower the amount" % held, "P more than you have: the plain reason")
    p0 = fx.purse[sa]
    pg = click("xok:1", **{"@BzOQ": str(held + 5)})
    K.check(fx.purse[sa] == p0 and int(E.count(A, iid)) + fx.bags.get((sa, iid), 0) == held, "P CONFIRM refuses it, nothing sold (%s)" % pg.info)
    pg = click("xa:0", **{"@BzOQ": str(held + 5)})
    pg = click("xa:2", **{"@BzOQ": "1"})
    K.eq(str(pg.oQty), str(held), "P the All you have chip")
    # the price dropped
    seen = int(pg.xSeen)
    M.apply(iid, 300, False)
    pg = click("xok:1", **{"@BzOQ": str(held)})
    K.check(fx.purse[sa] == p0 and str(pg.info).startswith("The price dropped"), "P the price dropped: nothing sold, asks again (%s)" % pg.info)
    now_pay = int(Fl.quote(A.pl, ua, iid, held, False))
    pg = click("xok:1", **{"@BzOQ": str(held)})
    K.check(fx.purse[sa] == p0 + now_pay and int(E.count(A, iid)) == 0 and fx.bags.get((sa, iid), 0) == 0 and st(pg) == -1 and str(pg.info).startswith("sold"),
            "P CONFIRM sells all %d (inventory + the Void) for the total now shown (%s)" % (held, pg.info))
    pg = click("xok:1", **{"@BzOQ": str(held)})
    K.check(fx.purse[sa] == p0 + now_pay, "P a second CONFIRM after the step closed sells nothing")
    M.reset(iid)
    pg = click("qsell")
    pg, cm, ev, ap = built("P SELL NOW holding none")
    K.check(str(pg.oQty) == "0" and H.set_of(cm, "#SkyyBzXw.Text") == "You have none to sell", "P holding none: amount 0 + the plain reason (never more)")
    conserved("SELL NOW")
    # ---------------------------------------------------------------- BUY ORDER
    S, Bp = int(M.quote(iid, 1, False)), int(M.quote(iid, 1, True))
    pg = click("qbid")
    K.check(st(pg) == 2 and str(pg.oQty) == "1" and str(pg.oPrice) == str(S + 1), "P BUY ORDER: amount 1, Best price with no orders = 1 over the instant sell (%s @ %s)" % (pg.oQty, pg.oPrice))
    pg, cm, ev, ap = built("P BUY ORDER step")
    K.check(str(H.set_of(cm, "#SkyyBzXs.Text")).startswith("No buy orders yet"), "P the chip note sits in the grey line under the heading: %s" % H.set_of(cm, "#SkyyBzXs.Text"))
    K.eq(str(H.set_of(cm, "#SkyyBzXw.Text")), "", "FIX bz1 the 'no orders yet' note is info - not in the orange warning line")
    K.eq(sum(1 for ty, s, _t, _d in cm if ty == "Set" and s == "#SkyyBzXs.Text"), 1, "FIX bz1 the step line is set once per draw")
    K.check(any("@BzOP" in t for _s, t in ev) and "#SkyyBzXp0" in [s for s, _t in ev], "P the price chips + field are on the page and carried")
    pg = click("xp:1", **{"@BzOQ": "1", "@BzOP": str(S + 1)})
    K.eq(str(pg.oPrice), str(S + 1), "P Beat best by 1 with no orders = Best price")
    nb = max(2, mt // (S + 1) + 1)          # every order worth at least the minimum total
    r = Od.place(Bb.pl, ub, "Bob", iid, 0, S + 3, nb)
    K.check(bool(r.ok), "P Bob places a buy order at S+3 (%s)" % r.msg)
    pg = click("xp:0", **{"@BzOQ": "1", "@BzOP": ""})
    K.eq(str(pg.oPrice), str(S + 3), "P Best price = the best buy order")
    pg = click("xp:1", **{"@BzOQ": "1", "@BzOP": ""})
    K.eq(str(pg.oPrice), str(S + 4), "P Beat best by 1 = best buy order + 1")
    T20.give(Bb, iid, min(stk, nb + 5), 0)
    rebase()
    r = Od.place(Bb.pl, ub, "Bob", iid, 1, S + 4, nb)
    K.check(bool(r.ok), "P Bob offers at S+4 (%s)" % r.msg)
    pg = click("xp:1", **{"@BzOQ": "1", "@BzOP": ""})
    K.eq(str(pg.oPrice), str(S + 3), "P Beat best by 1 would cross Bob's sell offer at S+4 -> clamped to S+3")
    K.eq(str(pg.xWhy), "Capped at %d - a buy order must stay under the lowest sell offer, %d" % (S + 3, S + 4), "P the clamp says why in one line")
    pg, cm, ev, ap = built("FIX bz1 BUY ORDER clamped")
    K.eq(H.set_of(cm, "#SkyyBzXw.Text"), str(pg.xWhy), "FIX bz1 a clamp reason stays in the orange warning line")
    K.check(str(H.set_of(cm, "#SkyyBzXs.Text")).startswith("You name the price"), "FIX bz1 the grey line keeps the step text when the note is a clamp")
    pg = click("xupd", **{"@BzOQ": "1", "@BzOP": str(Bp + 5)})
    pg, cm, ev, ap = built("P BUY ORDER too high")
    K.check(str(H.set_of(cm, "#SkyyBzXw.Text")).startswith("Too high - a buy order must stay under the lowest sell offer"), "P a typed price over the band: %s" % H.set_of(cm, "#SkyyBzXw.Text"))
    p0 = fx.purse[sa]
    pg = click("xok:2", **{"@BzOQ": "1", "@BzOP": str(Bp + 5)})
    K.check(fx.purse[sa] == p0 and str(pg.info).startswith("Too high"), "P CONFIRM refuses it, no coins held (%s)" % pg.info)
    pg = click("xupd", **{"@BzOQ": str(nb), "@BzOP": str(S + 2)})
    pg, cm, ev, ap = built("P BUY ORDER nb at S+2")
    K.eq(H.set_of(cm, "#SkyyBzXt.Text"), "You pay %s coins now - held until it fills" % grp(nb * (S + 2)), "P the order total")
    pg = click("xok:2", **{"@BzOQ": str(nb), "@BzOP": str(S + 2)})
    K.check(fx.purse[sa] == p0 - nb * (S + 2) and str(pg.info).startswith("placed a buy order") and st(pg) == -1, "P CONFIRM places it, coins held (%s)" % pg.info)
    pg = click("xok:2", **{"@BzOQ": str(nb), "@BzOP": str(S + 2)})
    K.check(fx.purse[sa] == p0 - nb * (S + 2), "P a second CONFIRM places nothing more")
    # the Confirm-buys-from amount arms a buy order too
    CF.set(ua, 0)
    pg = click("qbid")
    pg = click("xupd", **{"@BzOQ": str(nb), "@BzOP": str(S + 1)})
    p0 = fx.purse[sa]
    pg = click("xok:2", **{"@BzOQ": str(nb), "@BzOP": str(S + 1)})
    K.check(fx.purse[sa] == p0 and "click CONFIRM" in str(pg.info), "P a buy order over Confirm-buys-from asks first (%s)" % pg.info)
    pg = click("xok:2", **{"@BzOQ": str(nb), "@BzOP": str(S + 1)})
    K.check(fx.purse[sa] == p0 - nb * (S + 1) and str(pg.info).startswith("placed"), "P the gold CONFIRM places it")
    CF.set(ua, 10 ** 12)
    keep = fx.purse[sa]
    fx.purse[sa] = 5
    pg = click("qbid")
    pg = click("xupd", **{"@BzOQ": "3", "@BzOP": str(S + 1)})
    pg, cm, ev, ap = built("P BUY ORDER broke")
    K.check(str(H.set_of(cm, "#SkyyBzXw.Text")).startswith("You need ") or str(H.set_of(cm, "#SkyyBzXw.Text")).startswith("An order must"), "P not enough coins: %s" % H.set_of(cm, "#SkyyBzXw.Text"))
    pg = click("xok:2", **{"@BzOQ": "3", "@BzOP": str(S + 1)})
    K.check(fx.purse[sa] == 5, "P CONFIRM holds no coins")
    fx.purse[sa] = keep
    pg = click("xback")
    conserved("BUY ORDER")
    # ---------------------------------------------------------------- SELL OFFER
    T20.give(A, iid, stk, 2)
    T20.give(A, iid, stk, 3)
    fx.bags[(sa, iid)] = 4
    no = max(6, mt // (Bp - 1) + 1)
    assert no + 3 <= 2 * stk + 4, (no, stk)
    md = None
    try:
        doc = JClass("org.bson.BsonDocument")("skyyTest", JClass("org.bson.BsonString")("x"))
        md = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")(iid, 3, doc)
        if md.getMetadata() is None:
            md = None
    except Exception as ex:
        K.notes.append("P an extra-data stack could not be made on the stand-in: %s" % ex)
    if md is not None:
        A.inv.getStorage().setItemStackForSlot(JShort(5), md)
    rebase()
    plain = int(Od.countPlain(A.pl, iid)) + 4
    pg = click("qask")
    K.check(st(pg) == 3 and str(pg.oQty) == str(plain), "P SELL OFFER starts at all you hold in plain stacks + the Void (%s = %d)" % (pg.oQty, plain))
    ba = int(Bk.bestL(iid, 1, JClass("java.lang.System").currentTimeMillis()))
    K.eq(str(pg.oPrice), str(ba), "P Best price = the lowest sell offer (Bob's)")
    pg = click("xp:1", **{"@BzOQ": str(plain), "@BzOP": ""})
    bb = int(Bk.bestL(iid, 0, JClass("java.lang.System").currentTimeMillis()))
    want = ba - 1
    if want <= bb:
        K.eq(str(pg.oPrice), str(bb + 1), "P Beat best by 1 would cross the best buy order -> raised over it")
        K.check(str(pg.xWhy).startswith("Raised to %d - a sell offer must stay over the best buy order, %d" % (bb + 1, bb)), "P the raise says why: %s" % pg.xWhy)
    else:
        K.eq(str(pg.oPrice), str(want), "P Beat best by 1 = lowest offer - 1")
    if md is not None:
        pg = click("xupd", **{"@BzOQ": str(plain + 3), "@BzOP": str(Bp - 1)})
        pg, cm, ev, ap = built("P SELL OFFER over plain")
        K.eq(H.set_of(cm, "#SkyyBzXw.Text"), "You have %d to offer - lower the amount (3 with extra data stay out)" % plain, "P extra-data stacks stay out, said plainly")
    pg = click("xupd", **{"@BzOQ": str(no), "@BzOP": str(Bp - 1)})
    pg, cm, ev, ap = built("P SELL OFFER no")
    tot = no * (Bp - 1)
    tax = tot * int(OC.bp()) // 10000
    K.eq(H.set_of(cm, "#SkyyBzXt.Text"), "You get %s coins when it sells (after %s tax)" % (grp(tot - tax), grp(tax)), "P the offer total after tax")
    n0 = int(Od.countPlain(A.pl, iid)) + fx.bags[(sa, iid)]
    pg = click("xok:3", **{"@BzOQ": str(no), "@BzOP": str(Bp - 1)})
    K.check(str(pg.info).startswith("placed a sell offer") and int(Od.countPlain(A.pl, iid)) + fx.bags[(sa, iid)] == n0 - no and st(pg) == -1,
            "P CONFIRM places the offer, its items held (%s)" % pg.info)
    if md is not None:
        K.check(A.inv.getStorage().getItemStack(JShort(5)) is not None and A.inv.getStorage().getItemStack(JShort(5)).getMetadata() is not None, "P the extra-data stack was not taken")
    pg = click("xok:3", **{"@BzOQ": str(no), "@BzOP": str(Bp - 1)})
    K.check(int(Od.countPlain(A.pl, iid)) + fx.bags[(sa, iid)] == n0 - no, "P a second CONFIRM offers nothing more")
    pg = click("qask")
    pg = click("xupd", **{"@BzOQ": "2", "@BzOP": "abc"})
    pg, cm, ev, ap = built("P SELL OFFER bad price")
    K.check(str(H.set_of(cm, "#SkyyBzXw.Text")).startswith("That is not a price"), "P a typed price that is not a number: %s" % H.set_of(cm, "#SkyyBzXw.Text"))
    # a tab click closes the step
    pg = click("tab:0")
    K.eq(st(pg), -1, "P a tab click closes the step")
    conserved("SELL OFFER")
    # ---------------------------------------------------------------- a product too cheap for orders
    if cheap is None:
        K.notes.append("P no product too cheap for orders in this catalog - that panel line not drawn")
        K.save()
        return
    pg = A.pm.getCustomPage()
    pg.sel = cheap
    pg.cat = C.get(cheap).cat
    pg.oSide = -1
    pg, cm, ev, ap = built("P cheap product")
    K.eq(H.set_of(cm, "#SkyyBzQp2.Text"), "Not for this item", "P a too-cheap product: orders say so on the button")
    pg = click("qbid")
    pg, cm, ev, ap = built("P cheap BUY ORDER")
    K.eq(H.set_of(cm, "#SkyyBzXw.Text"), "Too cheap for orders - use Buy now or Sell now", "P ... and the step says why")
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
    K.check(not da, "D the 0.2.5 start = the 0.2.4 start on the live data (files that differ: %s)" % da)
    K.check(hs["new1"] == hs["new2"], "D a second 0.2.5 start writes nothing (%s)" % sorted(k for k in set(hs["new1"]) | set(hs["new2"]) if hs["new1"].get(k) != hs["new2"].get(k))[:5])
    pp = open(os.path.join(home, "products.properties"), encoding="latin-1").read()
    K.check(all(re.search(r"(?m)^%s=Mining," % m, pp) for m in METALS if re.search(r"(?m)^%s=" % m, pp)),
            "D the live products.properties keeps the metals' Mining lines (no file rewrite; %d listed)" % sum(1 for m in METALS if re.search(r"(?m)^%s=" % m, pp)))
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
           phases=[("static", run_static), ("catalog", run_catalog), ("metals", run_metals), ("page", run_page), ("live", run_live)],
           live=(LIVE, "Skyy_SkyyBazaar"), script=__file__)
