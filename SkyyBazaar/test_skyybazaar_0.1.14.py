"""Harness for SkyyBazaar 0.1.14 (round bz0114: the CONFIRM button + confirm amount, Eternal seed prices + sell caps, the minimum sell price,
prices by tier + their one-time update; tools/bazaar_0_1_14_patch.py). Build first:
python tools/bazaar_0_1_14_patch.py && python SkyyBazaar/build_skyybazaar_0.1.14.py

    python SkyyBazaar/test_skyybazaar_0.1.14.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.1.13 -> 0.1.14: exactly the listed members differ (+ BzConfirm, BzRevert)
  X   exec     -Xverify:all over the engine stand-ins (tools/hub_tab_harness.py boot: the REAL PageManager, a recording packet sink, real
               inventories) with a fake SkyyCoins bridge:
               PRICES  every sell-capped product sells at its cap, buys at its tier price; no product that takes the floor sells 1 for
                       less than the minimum (2), at demand 1 and 0.25; buy > sell for every product; minimum 0 = the 0.1.13 jar's quotes
                       for every product the tier update did not touch; maxBuyable agrees with quote; the bridge publishes quote(1)
               CONFIRM below the amount = bought on the first click; at / above = the button turns into gold 'CONFIRM - <total> coins'
                       and the second click buys; a double click buys ONCE; any other click turns it back; the price rising between the
                       clicks asks again at the new total (and then buys at it); an expired confirm asks again; the timeout task
                       (BzRevert -> the world thread) turns the button back and answers the page; a stale timeout does nothing; amount 0
                       = every buy asks; Set saves confirm.properties; a bad amount saves nothing; no line = the server default (and it
                       follows Server Setup); the Settings switch OFF = never asks; the custom Buy (direct / CONFIRM), the custom Sell
                       (always CONFIRM), Enter pricing, Sell inventory's gold 'Confirm sell'; every click is answered (a packet)
  M   migrate  0.1.13 jar then 0.1.14 jar on the same folder (LF and CRLF files): every 0.1.13 default of the tier table moves to its
               0.1.14 price (the price text only - every other byte and line ending stays), an admin's price is KEPT + logged, the
               config-history copy = the old bytes, the marker is written (and survives writeModes), a second start changes nothing;
               a fresh 0.1.14 install seeds the new prices and logs no KEPT line in migrate14 / migrate114
  D   live     the 0.1.14 start on a scratch COPY of the live Skyy_SkyyBazaar: what moved / was kept; a second start changes nothing
  AA  engine-access audit
Scratch: tools/dev/scratch/bz0114/harness (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, re, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.1.14"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyBazaar-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyBazaar-0.1.13.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "bz0114", "harness")))
PKG = "com.skyy.bazaar."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyBazaar")
ADDED = ["BzConfirm", "BzRevert"]
EXPECT = {
    "BzCfg": ["+f CONFIRM", "+f MINSELL", "+f MINSELL_MAX", "+f MINSELL_MIN", "+m floorChanged", "~<clinit>", "~m load"],
    "BzPage": ["+f armForce", "+f cfAct", "+f cfCost", "+f cfDraft", "+f cfId", "+f cfQ", "+f cfSeq", "+f cfShown", "+f cfUntil", "+m arm", "+m buyClick",
               "+m cfSet", "+m cfText", "+m revert", "+m schedRevert", "+m worldUuid", "~c ", "~m amountAction", "~m disarm", "~m evd",
               "~m handleDataEvent", "~m infoColor", "~m render"],
    "Catalog": ["+f BUYX", "+f BX_ID", "+f BX_V", "+f FLOORPUB", "+f M114_ID", "+f M114_LOG", "+f M114_NEW", "+f M114_OLD", "+f M114_OTXT",
                "+f M114_TXT", "+f MIGRATED114", "+f NF_ID", "+f NOFLOOR", "+f SCAP", "+f SC_ID", "+f SC_V", "+m buyFloor", "+m buyVal",
                "+m floorBase", "+m m114", "+m m114now", "+m migrate114", "+m sellBase", "+m sellVal", "~<clinit>", "~m edgeFuel", "~m init",
                "~m loadModes", "~m loopingEdges", "~m migrate14", "~m procLine", "~m tick", "~m writeModes"],
    "CfgFile": ["~<clinit>"],                      # the default config.properties text (2 new rows)
    "CfgFn": ["~m opExport"],                      # the version text
    "CfgRows": ["~<clinit>", "~m header"],         # the 2 new rows + the version text
    "Market": ["~m maxBuyable", "~m quote", "~m step", "~m unit"],
    "SkyyBazaarPlugin": ["~m setup"],
    "Trader": ["+m buyC", "+m buyC0", "~m buyN0", "~m sellN0"],
}


def loader_for(jar):
    from jpype import JClass, JArray
    URL = JClass("java.net.URL")
    arr = JArray(URL)(1)
    arr[0] = JClass("java.io.File")(jar).toURI().toURL()
    return JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getSystemClassLoader())


class Bz(object):
    """one jar's data classes in its own loader, started on folder d like SkyyBazaarPlugin.setup() (its data steps)"""

    def __init__(self, jar, d, new):
        from jpype import JClass
        self.L = loader_for(jar)
        g = lambda n: JClass(PKG + n, loader=self.L)
        self.M, self.C, self.Cfg, self.U = g("Market"), g("Catalog"), g("BzCfg"), g("BzUtil")
        self.U.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyBazaar")
        P = JClass("java.nio.file.Paths")
        dp = P.get(d)
        os.makedirs(d, exist_ok=True)
        self.C.FILE = dp.resolve("products.properties")
        self.C.PFILE = dp.resolve("pricing.properties")
        self.M.FILE = dp.resolve("market.properties")
        self.M.LOGFILE = dp.resolve("trades.log")
        self.Cfg.load(dp)
        self.mig = [self.C.migrate(), self.C.migrate14(), self.C.migrate19(), self.C.migrate110()]
        self.m14log = [str(x) for x in self.C.M14_LOG]
        self.m114 = self.C.migrate114() if new else None
        self.m114log = [str(x) for x in self.C.M114_LOG] if new else []
        self.n = int(self.C.load())
        self.M.load()
        self.C.reprice()
        self.M.publishAll()
        self.C.flushIfDirty()
        self.M.flush()
        self.ids = [str(p.id) for p in self.C.all()]

    def q(self, i, n=1, buy=True):
        return int(self.M.quote(i, n, buy))


def rb(p):
    return open(p, "rb").read() if os.path.exists(p) else None


# ------------------------------------------------------------------------------------------------------------------- X: exec
def run_exec(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JImplements, JOverride, JLong, JBoolean
    import hub_tab_harness as H
    K = HK.Child(out)
    W = H.boot(scratch, jar, "x")
    E = W.E
    J = lambda n: JClass(PKG + n)
    # an Item asset store that answers Item.UNKNOWN for every product id (the 0.1.5 harness stand-in): ItemStacks of products stack and
    # fit in the stand-in inventories, so buys / sells really move items
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    us = uf.get(None)
    jp = JClass("javassist.ClassPool")(True)
    jp.appendClassPath(B.SERVER_JAR)
    CtF, CtM, CtC = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    fake = jp.makeClass("com.hypixel.hytale.assetstore.SkyyBzFakeStore14", jp.get("com.hypixel.hytale.assetstore.AssetStore"))
    fake.addConstructor(CtC.make("public SkyyBzFakeStore14() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", fake))
    FAKEC = fake.toClass(AS.class_)
    store = us.allocateInstance(FAKEC)
    fm = AS.class_.getDeclaredField("assetMap")
    fm.setAccessible(True)
    DAMN = "com.hypixel.hytale.assetstore.map.DefaultAssetMap"
    ITMN = "com.hypixel.hytale.server.core.asset.type.item.config.Item"
    kmap = jp.makeClass("com.hypixel.hytale.assetstore.map.SkyyBzKnownMap14", jp.get(DAMN))
    kmap.addField(CtF.make("public static final java.util.HashSet KNOWN = new java.util.HashSet();", kmap))
    kmap.addConstructor(CtC.make("public SkyyBzKnownMap14() { super(); }", kmap))
    kmap.addMethod(CtM.make("public com.hypixel.hytale.assetstore.JsonAsset getAsset(Object key) { if (key != null && KNOWN.contains(key)) return "
                            "%s.UNKNOWN; return super.getAsset(key); }" % ITMN, kmap))
    KMap = JClass(kmap.toClass(JClass(DAMN).class_))
    fm.set(store, KMap())
    fi_ = JClass(ITMN).class_.getDeclaredField("ASSET_STORE")
    fi_.setAccessible(True)
    fi_.set(None, store)
    home = os.path.join(scratch, "home_x")
    os.makedirs(home, exist_ok=True)
    J("BzUtil").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyBazaar")
    d = E.Paths.get(home)
    C, M, Cfg, Cf, T = J("Catalog"), J("Market"), J("BzCfg"), J("BzConfirm"), J("Trader")
    C.FILE = d.resolve("products.properties")
    C.PFILE = d.resolve("pricing.properties")
    M.FILE = d.resolve("market.properties")
    M.LOGFILE = d.resolve("trades.log")
    Cfg.load(d)
    Cf.load(d)
    C.migrate()
    C.migrate14()
    C.migrate19()
    C.migrate110()
    C.migrate114()
    C.load()
    M.load()
    C.reprice()
    M.publishAll()
    br = J("BzUtil").bridge()
    purse = {}

    @JImplements("java.util.function.Function")
    class CGet:
        @JOverride
        def apply(self, o):
            return JLong(purse.get(str(o), 0))

    @JImplements("java.util.function.Function")
    class CTake:
        @JOverride
        def apply(self, o):
            u, n = str(o[0]), int(o[1])
            if purse.get(u, 0) < n:
                return JBoolean(False)
            purse[u] = purse.get(u, 0) - n
            return JBoolean(True)

    @JImplements("java.util.function.Function")
    class CAdd:
        @JOverride
        def apply(self, o):
            u, n = str(o[0]), int(o[1])
            purse[u] = purse.get(u, 0) + n
            return JLong(purse[u])
    br.put("coins:fn:get", CGet())
    br.put("coins:fn:take", CTake())
    br.put("coins:fn:add", CAdd())
    K.check(bool(J("Coins").ready()), "X: the fake SkyyCoins bridge is seen")

    # ---------------------------------------------------------------- PRICES
    MS = int(Cfg.MINSELL)
    K.eq(MS, 2, "PRICES: the minimum sell price defaults to 2")
    K.eq(int(Cfg.CONFIRM), 3000, "PRICES: the confirm amount defaults to 3000")
    sc = dict((str(i), float(v)) for i, v in zip(C.SC_ID, C.SC_V))
    nf = set(str(i) for i in C.NF_ID)
    m114 = dict((str(i), (float(o), float(n))) for i, o, n in zip(C.M114_ID, C.M114_OLD, C.M114_NEW))
    ids = [str(p.id) for p in C.all()]
    for i in ids:
        KMap.KNOWN.add(i)
    K.check(len(ids) > 400, "PRICES: %d products" % len(ids))
    sp = float(M.SPREAD)
    fb = MS / (1.0 - sp)
    bad_floor, bad_bs, bad_cap = [], [], []
    import math
    for i in ids:
        p = C.get(i)
        b = float(p.base)
        bu, se = int(M.quote(i, 1, True)), int(M.quote(i, 1, False))
        if bu <= se:
            bad_bs.append((i, bu, se))
        if i not in nf and se < MS:
            bad_floor.append((i, se))
        if i in sc:
            want_s = int(math.floor(max(min(b, sc[i]), fb if i not in nf else 0.0) * (1 - sp) + 1e-7))
            want_b = int(math.ceil(max(b, fb if i not in nf else 0.0) * (1 + sp) - 1e-7))
            if (bu, se) != (want_b, want_s):
                bad_cap.append((i, bu, se, want_b, want_s))
    K.eq(bad_bs, [], "PRICES: buy > sell for every product (1 unit, demand 1)")
    K.eq(bad_floor, [], "PRICES: no product that takes the floor sells 1 for less than %d" % MS)
    K.eq(bad_cap, [], "PRICES: every sell-capped product buys at its price and sells at its cap (%d capped)" % len(sc))
    we = "Plant_Seeds_Wheat_Eternal"
    K.eq((int(M.quote(we, 1, True)), int(M.quote(we, 1, False))), (880, int(math.floor(sc.get(we, 0) * 0.9 + 1e-7))),
         "PRICES: Wheat Seed Bag (Eternal) buys for 880 (800 base), sells for its crafting value (cap %s)" % sc.get(we))
    # the floor at demand 0.25 (a dumped product)
    cheap = [i for i in ids if i not in nf and float(C.get(i).base) < fb]
    K.check(len(cheap) > 0, "PRICES: %d products sit under the floor value %.3f (they take it)" % (len(cheap), fb))
    if cheap:
        c0 = cheap[0]
        M.F.put(c0, JClass("java.lang.Double")(0.25))
        K.check(int(M.quote(c0, 1, False)) >= MS and int(M.quote(c0, 10, False)) >= 10 * MS and int(M.quote(c0, 1, True)) > int(M.quote(c0, 1, False)),
                "PRICES: at demand 0.25 %s still sells 1 for >= %d and 10 for >= %d (%d / %d), buy %d" % (c0, MS, 10 * MS, int(M.quote(c0, 1, False)),
                                                                                            int(M.quote(c0, 10, False)), int(M.quote(c0, 1, True))))
        M.F.remove(c0)
    exs = sorted(nf)[:3]
    for i in exs:
        K.notes.append("PRICES: floor-exempt %s sells 1 for %d (base %g)" % (i, int(M.quote(i, 1, False)), float(C.get(i).base)))
    # the demand step cap: ONE buy then ONE sell back never pays (0.1.13: Enchanted Adamantite paid ~26,000 a round trip)
    rt = []
    for i in ids:
        b1 = int(M.quote(i, 1, True))
        M.apply(i, 1, True)
        s1 = int(M.quote(i, 1, False))
        M.apply(i, 1, False)
        if s1 >= b1:
            rt.append((i, b1, s1))
    K.eq(rt, [], "PRICES: buy 1 then sell 1 straight back never pays, for any of the %d products (demand step <= 1.2)" % len(ids))
    # maxBuyable agrees with quote (with the floor in the walk)
    ok_mb = True
    for i in ([cheap[0]] if cheap else []) + ["Ore_Onyxium", we, "Plant_Crop_Wheat_Item"]:
        for pv in (5, 100, 9999):
            k = int(M.maxBuyable(i, JLong(pv), 1000))
            if k > 0 and int(M.quote(i, k, True)) > pv:
                ok_mb = False
            if k < 1000 and int(M.quote(i, k + 1, True)) <= pv:
                ok_mb = False
    K.check(ok_mb, "PRICES: maxBuyable = the most quote() lets a purse buy (floor included)")
    K.check(int(br.get("bazaar:sell:" + we)) == int(M.quote(we, 1, False)) and int(br.get("bazaar:buy:" + we)) == 880,
            "PRICES: the bridge publishes the capped sell / tier buy price (%s / %s)" % (br.get("bazaar:sell:" + we), br.get("bazaar:buy:" + we)))
    # ---------------------------------------------------------------- CONFIRM
    P = W.P
    u = P.pr.getUuid()
    purse[str(u)] = 10000000
    page = J("BzPage")(P.pr, "Ore_Onyxium")
    P.pm.openCustomPage(P.ref, P.st, page)
    E.pump(P)
    unanswered = []

    def click(a, amt=None, cf=None, find="", soon=False):
        if not soon:
            page.cfShown = JLong(0)          # as if the CONFIRM had been on screen for a while (the 0.3 s rule has its own test)
        dd = {"a": a, "@BzFind": find}
        if amt is not None:
            dd["@BzAmount"] = amt
        dd["@BzCf"] = "" if cf is None else cf
        n0 = len(E.sent(P))
        P.pm.handleLegacyCustomPageEvent(P.ref, P.st, E.CPE(E.CPT.Data, json.dumps(dd)))
        E.pump(P)
        if len(E.sent(P)) <= n0:
            unanswered.append((a, str(page.info), None if page.cfAct is None else str(page.cfAct), len(E.sent(P)), n0))
        return E.strs_of(P, n0)

    def sel(i):
        page.sel = i
        page.disarm()

    cnt = lambda i: int(E.count(P, i))
    pu = lambda: purse[str(u)]
    GOLD = "#E8A93B"
    on = "Ore_Onyxium"
    # 1. below the amount
    sel("Plant_Crop_Wheat_Item")
    c0, p0, qw = cnt("Plant_Crop_Wheat_Item"), pu(), int(M.quote("Plant_Crop_Wheat_Item", 1, True))
    click("buy1")
    K.check(cnt("Plant_Crop_Wheat_Item") == c0 + 1 and pu() == p0 - qw and str(page.info).startswith("bought"),
            "CONFIRM: a %d-coin buy (below 3000) goes through on the FIRST click (%s)" % (qw, page.info))
    # 2. at / above: CONFIRM, second click buys
    sel(on)
    qo = int(M.quote(on, 1, True))
    c0, p0 = cnt(on), pu()
    txt = click("buy1")
    K.check(cnt(on) == c0 and pu() == p0 and str(page.cfAct) == "buy1" and "click CONFIRM" in str(page.info),
            "CONFIRM: a %d-coin buy (>= 3000) arms instead of buying (%s)" % (qo, page.info))
    K.check(("CONFIRM - %d coins" % qo) in txt and GOLD in txt and "#SkyyBzBuy1" in txt,
            "CONFIRM: the Buy 1 button is drawn as the gold 'CONFIRM - %d coins' button" % qo)
    txt = click("buy1")
    K.check(cnt(on) == c0 + 1 and pu() == p0 - qo and page.cfAct is None, "CONFIRM: the second click buys (%s)" % page.info)
    K.check(("CONFIRM - %d" % qo) not in txt, "CONFIRM: after the buy the button is back to Buy 1")
    # 3. double click = one buy; a third click asks again
    c0 = cnt(on)
    click("buy1"); click("buy1"); click("buy1")
    K.check(cnt(on) == c0 + 1 and str(page.cfAct) == "buy1", "CONFIRM: three fast clicks = ONE buy, then it asks again (%d bought)" % (cnt(on) - c0))
    # 3b. the 0.3 s rule: a click sooner than 0.3 s after the CONFIRM was drawn is answered but does not buy
    c0 = cnt(on)
    sel(on)
    click("buy1")
    n0s = len(E.sent(P))
    click("buy1", soon=True)
    K.check(cnt(on) == c0 and str(page.cfAct) == "buy1" and len(E.sent(P)) > n0s, "CONFIRM: a double-click (2nd click < 0.3 s after CONFIRM appeared) is answered, buys nothing, stays armed")
    click("buy1")
    K.check(cnt(on) == c0 + 1, "CONFIRM: ... the next click after 0.3 s buys")
    sel("Plant_Crop_Wheat_Item")
    click("asell", amt="1")
    c1 = cnt("Plant_Crop_Wheat_Item")
    click("asell", amt="1", soon=True)
    K.check(cnt("Plant_Crop_Wheat_Item") == c1 and page.armForce, "CONFIRM: the same 0.3 s rule on the custom Sell")
    click("next")
    # 4. any other click turns it back
    sel(on)
    click("buy1")
    t2 = click("next")
    K.check(page.cfAct is None and "CONFIRM - " not in t2, "CONFIRM: another click (Next) turns the button back")
    c0 = cnt(on)
    click("buy1")
    K.check(cnt(on) == c0 and str(page.cfAct) == "buy1", "CONFIRM: after that, Buy 1 asks again (no buy)")
    # 5. the price rises between the clicks -> asked again at the new total, then bought at it
    sel(on)
    click("buy1")
    seen = int(page.cfCost)
    M.apply(on, 3, True)
    new = int(M.quote(on, 1, True))
    c0, p0 = cnt(on), pu()
    click("buy1")
    K.check(new > seen and cnt(on) == c0 and pu() == p0 and int(page.cfCost) == new and "price moved" in str(page.info),
            "CONFIRM: the price rose %d -> %d between the clicks: nothing bought, asked again at %d (%s)" % (seen, new, new, page.info))
    click("buy1")
    K.check(cnt(on) == c0 + 1 and pu() == p0 - new, "CONFIRM: the next click buys at the new total %d" % new)
    # 6. timeout
    sel(on)
    click("buy1")
    page.cfUntil = JLong(int(JClass("java.lang.System").currentTimeMillis()) - 1)
    c0 = cnt(on)
    click("buy1")
    K.check(cnt(on) == c0 and str(page.cfAct) == "buy1", "CONFIRM: a click after the 10 s asks again (no buy)")
    page.cfUntil = JLong(int(JClass("java.lang.System").currentTimeMillis()) - 1)
    n0 = len(E.sent(P))
    J("BzRevert")(page, int(page.cfSeq), False).run()
    ran = int(E.run_world(E.W1))
    E.pump(P)          # the client acknowledges the redraw (the real PageManager ignores events until it does)
    tt = E.strs_of(P, n0)
    K.check(ran >= 1 and page.cfAct is None and "timed out" in str(page.info) and len(E.sent(P)) > n0 and "#SkyyBzInfo.Text" in tt
            and "#SkyyBzAmt.Value" not in tt and "#SkyyBzCf.Value" not in tt,
            "CONFIRM: the timeout task (world thread) cancels the confirm and updates ONLY the result line - typed field text is not touched (%d task, %s)" % (ran, page.info))
    c0 = cnt(on)
    click("buy1")
    K.check(cnt(on) == c0 and str(page.cfAct) == "buy1", "CONFIRM: a click on the stale CONFIRM after the timeout asks again (no buy)")
    sel(on)
    click("buy1")
    old_seq = int(page.cfSeq)
    click("buy1")      # bought -> nothing armed
    K.notes.append("stale: after the 2nd click cfAct=%s info=%s" % (page.cfAct, page.info))
    click("buy1")      # armed again, newer seq
    K.notes.append("stale: after the 3rd click cfAct=%s seq %d -> %d info=%s" % (page.cfAct, old_seq, int(page.cfSeq), page.info))
    page.cfUntil = JLong(int(JClass("java.lang.System").currentTimeMillis()) - 1)
    J("BzRevert")(page, old_seq, False).run()
    E.run_world(E.W1)
    E.pump(P)
    K.check(str(page.cfAct) == "buy1", "CONFIRM: a stale timeout (an older confirm) does nothing")
    page.revert(int(page.cfSeq))
    E.pump(P)
    K.check(page.cfAct is None, "CONFIRM: revert() of the current confirm after its time clears it")
    # 7. amount 0 = every buy asks; Set saves confirm.properties
    click("cfset", cf="0")
    K.eq(int(Cf.get(u)), 0, "CONFIRM: Set 0 saves 0")
    cp = os.path.join(home, "confirm.properties")
    K.check(os.path.exists(cp) and ("%s=0" % u) in open(cp).read(), "CONFIRM: confirm.properties holds the player's amount")
    sel("Plant_Crop_Wheat_Item")
    c0 = cnt("Plant_Crop_Wheat_Item")
    click("buy1")
    K.check(cnt("Plant_Crop_Wheat_Item") == c0 and str(page.cfAct) == "buy1", "CONFIRM: amount 0 -> even a %d-coin buy asks" % qw)
    click("buy1")
    K.check(cnt("Plant_Crop_Wheat_Item") == c0 + 1, "CONFIRM: ... and the second click buys")
    # 8. amount 5k: a 4k+ buy goes straight through
    qn = int(M.quote(on, 1, True))
    amt = (qn // 1000 + 2) * 1000
    click("cfset", cf="%dk" % (amt // 1000))
    K.eq(int(Cf.get(u)), amt, "CONFIRM: Set %dk saves %d" % (amt // 1000, amt))
    sel(on)
    c0 = cnt(on)
    click("buy1")
    K.check(qn < amt and cnt(on) == c0 + 1, "CONFIRM: amount %d -> a %d-coin buy goes through on the first click" % (amt, qn))
    # bad amount
    click("cfset", cf="abc")
    K.check(int(Cf.get(u)) == amt and "not an amount" in str(page.info), "CONFIRM: a bad amount saves nothing (%s)" % page.info)
    # reload from disk
    Cf.load(d)
    K.eq(int(Cf.get(u)), amt, "CONFIRM: confirm.properties reads back (%d)" % amt)
    # 9. no line = the server default (and it follows Server Setup)
    fresh = E.UUID.randomUUID()
    K.eq(int(Cf.get(fresh)), 3000, "CONFIRM: a player without a line gets the server default 3000")
    Cfg.CONFIRM = 7000
    K.eq(int(Cf.get(fresh)), 7000, "CONFIRM: ... which follows Server Setup (7000)")
    K.check(not bool(Cf.needs(fresh, JLong(6999))) and bool(Cf.needs(fresh, JLong(7000))), "CONFIRM: below the amount = no confirm, AT it = confirm")
    Cfg.CONFIRM = 3000
    # 10. the Settings switch OFF = never asks
    click("cfset", cf="0")

    @JImplements("java.util.function.Function")
    class SetOff:
        @JOverride
        def apply(self, o):
            return JBoolean(False) if str(o[1]) == "bazaar.confirm" else None
    br.put("settings:fn:get", SetOff())
    sel("Plant_Crop_Wheat_Item")
    c0 = cnt("Plant_Crop_Wheat_Item")
    t10 = click("buy1")
    K.check(cnt("Plant_Crop_Wheat_Item") == c0 + 1 and "asking is OFF" in t10, "CONFIRM: the Settings switch OFF -> no confirm even at amount 0 (footer says so)")
    br.remove("settings:fn:get")
    click("cfset", cf="3000")
    # settings registration
    J("BzConfirm").register()
    reg = br.get("settings:def:bazaar.confirm")
    K.check(reg is not None and str(reg[0]) == "SkyyBazaar" and str(reg[3]) == "coins" and bool(reg[4]) and len(str(reg[2])) <= 40,
            "CONFIRM: the Settings switch is registered (settings:def:bazaar.confirm, Coins & Bank, ON)")
    # 11. the custom Buy
    sel(on)
    c0 = cnt(on)
    t11 = click("abuy", amt="1")
    qn = int(M.quote(on, 1, True))
    K.check(cnt(on) == c0 and "#SkyyBzABuy" in t11 and ("CONFIRM - %d coins" % qn) in t11, "CONFIRM: the custom Buy of 1 Onyxium (%d) turns into CONFIRM" % qn)
    click("abuy", amt="1")
    K.check(cnt(on) == c0 + 1, "CONFIRM: ... and the second click buys")
    sel("Plant_Crop_Wheat_Item")
    c0 = cnt("Plant_Crop_Wheat_Item")
    click("abuy", amt="5")
    K.check(cnt("Plant_Crop_Wheat_Item") == c0 + 5, "CONFIRM: a custom Buy of 5 Wheat (below 3000) goes through on the first click (%s)" % page.info)
    # 12. the custom Sell (always two clicks, now CONFIRM)
    c0 = cnt("Plant_Crop_Wheat_Item")
    t12 = click("asell", amt="2")
    K.check(cnt("Plant_Crop_Wheat_Item") == c0 and "#SkyyBzASell" in t12 and "CONFIRM - " in t12, "CONFIRM: the custom Sell turns into CONFIRM")
    click("asell", amt="2")
    K.check(cnt("Plant_Crop_Wheat_Item") == c0 - 2, "CONFIRM: ... and the second click sells")
    # 13. Enter prices both sides; a buy side at / above the amount shows CONFIRM, the click buys
    sel(on)
    c0 = cnt(on)
    t13 = click("amt", amt="1")
    K.check(cnt(on) == c0 and "CONFIRM - " in t13, "CONFIRM: Enter on 1 Onyxium shows the buy side as CONFIRM")
    click("abuy", amt="1")
    K.check(cnt(on) == c0 + 1, "CONFIRM: ... one click on it buys")
    # 14. Sell inventory: gold Confirm sell
    t14 = click("sellinv")
    K.check(("Confirm sell" in t14 and GOLD in t14) or "nothing to sell" in str(page.info), "CONFIRM: Sell inventory arms the gold 'Confirm sell' (%s)" % page.info)
    click("next")
    K.eq(unanswered, [], "CONFIRM: every click was answered with a packet")
    K.check(not [x for x in E.sent(P) if "Error" in str(x.getClass().getSimpleName())], "CONFIRM: no error packet")
    K.save()


# ------------------------------------------------------------------------------------------------------------------- M: migrate
def run_mig(out, jar, scratch, _home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    for nl in ("\n", "\r\n"):
        tag = "crlf" if nl == "\r\n" else "lf"
        d = os.path.join(scratch, "mig_" + tag)
        b13 = Bz(OLD_JAR, d, False)
        pf = os.path.join(d, "products.properties")
        txt = open(pf, "rb").read().decode("utf8")
        lines = txt.replace("\r\n", "\n").split("\n")
        lines = [re.sub(r"^(Plant_Seeds_Wheat_Eternal=[^,]*,)[^,]*(,.*)$", r"\g<1>99\g<2>", ln) for ln in lines]
        open(pf, "wb").write(nl.join(lines).encode("utf8"))
        before = open(pf, "rb").read()
        b14 = Bz(jar, d, True)
        after = open(pf, "rb").read()
        m114 = dict((str(i), (float(o), float(n))) for i, o, n in zip(b14.C.M114_ID, b14.C.M114_OLD, b14.C.M114_NEW))
        K.check(b14.m114 is not None and str(b14.m114).startswith("MIGRATE-0.1.14 rewrote"), "M %s: migrate114 ran (%s)" % (tag, b14.m114))
        bl, al = before.split(b"\n"), after.split(b"\n")
        K.eq(len(bl), len(al), "M %s: same number of lines" % tag)
        bad, moved = [], 0
        for x, y in zip(bl, al):
            idm = re.match(rb"^([A-Za-z0-9_]+)=", x)
            i = idm.group(1).decode() if idm else None
            if i is not None and bool(b14.C.isProc(i)) and bool(b14.C.isAuto(i)):
                xp = re.sub(rb"^([^=]*=[^,]*,)[^,]*", rb"#", x)
                yp = re.sub(rb"^([^=]*=[^,]*,)[^,]*", rb"#", y)
                if xp != yp:
                    bad.append(i)        # a processed good follows its inputs (the reprice writes its new price) - nothing else moves
            elif i in m114 and i != "Plant_Seeds_Wheat_Eternal":
                xp = re.sub(rb"^([^=]*=[^,]*,)[^,]*", rb"\1#", x)
                yp = re.sub(rb"^([^=]*=[^,]*,)[^,]*", rb"\1#", y)
                yv = float(re.match(rb"^[^=]*=[^,]*,([^,]*)", y).group(1))
                if xp != yp or abs(yv - m114[i][1]) > 1e-9:
                    bad.append(i)
                moved += 1
            elif x != y:
                bad.append(i or x[:30])
        K.eq(bad, [], "M %s: %d lines moved to their 0.1.14 price (price text only); every other byte stays" % (tag, moved))
        K.check((b"\r\n" in after) == (nl == "\r\n"), "M %s: the file keeps its line endings" % tag)
        K.check(any("KEPT Plant_Seeds_Wheat_Eternal 99" in x for x in b14.m114log), "M %s: the admin's 99 for Wheat Eternal is KEPT + logged" % tag)
        K.check(any("PRICE Plant_Seeds_Lettuce_Eternal 37 -> 800 (undo: /bazaaradmin price Plant_Seeds_Lettuce_Eternal 37)" in x for x in b14.m114log),
                "M %s: a moved price logs its undo command" % tag)
        hd = os.path.join(d, "config-history")
        baks = [f for f in os.listdir(hd)] if os.path.isdir(hd) else []
        K.check(len(baks) == 1 and open(os.path.join(hd, baks[0]), "rb").read() == before, "M %s: the config-history copy = the old bytes" % tag)
        pr = open(os.path.join(d, "pricing.properties"), "rb").read()
        K.check(b"migrated.0.1.14=" in pr, "M %s: the marker is written" % tag)
        K.eq(float(b14.C.get("Plant_Seeds_Wheat_Eternal").base), 99.0, "M %s: the kept price is what the 0.1.14 catalogue uses" % tag)
        b14.C.writeModes(b14.C.MIGRATED)
        K.check(b"migrated.0.1.14=" in open(os.path.join(d, "pricing.properties"), "rb").read(), "M %s: writeModes keeps the marker" % tag)
        snap = (rb(pf), rb(os.path.join(d, "pricing.properties")))
        b2 = Bz(jar, d, True)
        K.check(b2.m114 is None and (rb(pf), rb(os.path.join(d, "pricing.properties")))[0] == snap[0], "M %s: a second start changes nothing" % tag)
    # a fresh install
    d = os.path.join(scratch, "mig_fresh")
    bf = Bz(jar, d, True)
    # PRICES vs 0.1.13 (both jars in their own loaders, fresh folders): minimum sell 0 = 0.1.13's quotes for every product the tier
    # update did not touch (the sell caps aside); minimum 2 touches exactly the products whose value sits under 2 / 0.9 (not exempt)
    bo = Bz(OLD_JAR, os.path.join(scratch, "mig_fresh13"), False)
    m114 = set(str(i) for i in bf.C.M114_ID)
    sc = set(str(i) for i in bf.C.SC_ID)
    nf = set(str(i) for i in bf.C.NF_ID)
    bf.Cfg.MINSELL = 0
    import math
    stepcap = lambda b: math.exp(math.log(1.10) * b / 10000.0) > 1.2          # 0.1.14 caps the demand step at 1.2 (Market.step)
    same = [i for i in bf.ids if i not in sc and bo.C.get(i) is not None and abs(float(bf.C.get(i).base) - float(bo.C.get(i).base)) < 1e-9
            and not stepcap(float(bf.C.get(i).base))]
    capped = [i for i in bf.ids if stepcap(float(bf.C.get(i).base))]
    K.notes.append("P: demand step capped at 1.2 (was up to 4) for %d products: %s" % (len(capped), ", ".join(capped)))
    diff0 = [(i, (bf.q(i), bf.q(i, 1, False), bf.q(i, 50)), (bo.q(i), bo.q(i, 1, False), bo.q(i, 50))) for i in same
             if (bf.q(i), bf.q(i, 1, False), bf.q(i, 50)) != (bo.q(i), bo.q(i, 1, False), bo.q(i, 50))]
    K.eq(diff0[:8], [], "P: minimum sell 0 -> all %d untouched products quote exactly as on 0.1.13 (1 / 50 buy, 1 sell)" % len(same))
    bf.Cfg.MINSELL = 2
    fbv = 2 / (1 - float(bf.M.SPREAD))
    touched = [i for i in same if (bf.q(i), bf.q(i, 1, False)) != (bo.q(i), bo.q(i, 1, False))]
    bx = dict((str(i), float(v)) for i, v in zip(bf.C.BX_ID, bf.C.BX_V))
    under = [i for i in same if float(bf.C.get(i).base) < fbv * bx.get(i, 1.0) and i not in nf]   # + a raised buy side (BUY_X)
    K.eq((sorted(set(touched) - set(under)), sorted((i, float(bf.C.get(i).base), bf.q(i), bf.q(i, 1, False)) for i in set(under) - set(touched))), ([], []),
         "P: the 2-coin floor changes exactly the %d untouched products under the floor value (and no other)" % len(under))
    K.check(all(bf.q(i, 1, False) >= 2 and bf.q(i) > bf.q(i, 1, False) for i in under), "P: each of them sells 1 for >= 2 and buys for more")
    K.notes.append("P: the floor touches %d products (%d more are tier-priced / capped); e.g. %s" % (len(under), len([i for i in bf.ids if i in m114 and float(bf.C.get(i).base) < fbv and i not in nf]),
                   ", ".join("%s %d->%d (buy %d->%d)" % (i, bo.q(i, 1, False), bf.q(i, 1, False), bo.q(i), bf.q(i)) for i in under[:8])))
    K.check(not [x for x in bf.m14log if "KEPT" in x], "M fresh: migrate14 logs no KEPT line on the new seed (%s)" % [x for x in bf.m14log if "KEPT" in x][:3])
    K.check(not [x for x in bf.m114log if "KEPT" in x or "PRICE" in x], "M fresh: migrate114 changes / keeps nothing (%s)" % bf.m114log[:2])
    K.eq(int(bf.M.quote("Plant_Seeds_Wheat_Eternal", 1, True)), 880, "M fresh: Wheat Eternal buys for 880")
    K.save()


# ------------------------------------------------------------------------------------------------------------------- D: live
def run_live(out, jar, scratch, home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    pf = os.path.join(home, "products.properties")
    before = rb(pf)
    b = Bz(jar, home, True)
    K.check(b.n > 400, "D: %d live products load" % b.n)
    head = str(b.m114)
    K.notes.append("D: %s" % head)
    kept = [x for x in b.m114log if " KEPT " in x]
    K.notes.append("D: kept (live prices that are not the 0.1.13 default): %s" % kept[:12])
    K.notes.append("D: Wheat Eternal buy %d sell %d; Ore_Copper %d/%d; cobble %d/%d" % (b.q("Plant_Seeds_Wheat_Eternal"), b.q("Plant_Seeds_Wheat_Eternal", 1, False),
                                                                                 b.q("Ore_Copper"), b.q("Ore_Copper", 1, False), b.q("Rock_Stone_Cobble"),
                                                                                 b.q("Rock_Stone_Cobble", 1, False)))
    snap = HK.tree_hash(home)
    b2 = Bz(jar, home, True)
    now = HK.tree_hash(home)
    K.eq([k for k in ("products.properties", "pricing.properties", "config.properties") if now.get(k) != snap.get(k)], [],
         "D2: the second start changes no products / pricing / config file")
    K.check(b2.m114 is None, "D2: the update does not run twice")
    K.save()


if __name__ == "__main__":
    if EXPECT is None and "--phase" not in sys.argv:
        EXPECT = {}
    HK.run(name="SkyyBazaar", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT or {}, added=ADDED,
           phases=[("exec", run_exec), ("mig", run_mig), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyBazaar"))
