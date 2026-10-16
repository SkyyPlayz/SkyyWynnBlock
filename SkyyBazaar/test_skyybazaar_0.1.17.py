"""Harness for SkyyBazaar 0.1.17 (round hubmkt: the MARKET MERGE, Bazaar + Auction House = one Market tab, one search;
tools/bazaar_0_1_17_patch.py; the other half is SkyyAuctions 0.1.9). Build first:
python tools/bazaar_0_1_17_patch.py && python SkyyBazaar/build_skyybazaar_0.1.17.py   (+ SkyyAuctions 0.1.9 for the MK phase)

    python SkyyBazaar/test_skyybazaar_0.1.17.py [--dir <folder inside tools/dev/scratch/>] [--keep] [--ah <SkyyAuctions jar>]

Phases (fresh child JVMs, tools/harness_kit.py + tools/hub_tab_harness.py; -Xverify:all everywhere):
  A    verify   every class loads + initialises
  C    compare  0.1.16 -> 0.1.17: exactly the listed members differ, BzMarket / BzMkSort / BzOpenFn added (the catalogue classes are
                unchanged: the Enchanted rows stay 0.1.16's 20, TABLE_20)
  HUB  tools/hub_tab_harness.py run_hub EXECUTED (REG with the label "Market", PAGE in the hub shell, every hub CLICK, DROP) + here:
       1094 x 979, the sub-view row without SkyyAuctions (no AUCTION HOUSE button, the empty slot, caption 2)
  MK   the merge EXECUTED with BOTH jars (this one + SkyyAuctions 0.1.9) over the engine stand-ins: the tab registry (Market shown, the
       Auctions tab hidden while bazaar:fn:open exists, shown again without it), the tier table (= tools/tier_tags.py) + level bands
       (= tier_for_level) + BzMkSort, ah:fn:find on generated listings (grouping, every word, lowest each, cheapest, ends soonest,
       expired / blocked left out, junk queries), BzMarket.ahFind's row guard (bad rows / unsafe ids skipped), the ONE search on the
       Bazaar page (Bazaar + AH cells sorted by tier then name, AH cells say "AH <n>", the header, an AH cell selects no product, a Buy
       click with an AH cell selected trades nothing), OPEN IN AUCTION HOUSE + AUCTION HOUSE (the AH page opens with the item id / the
       search), the AH page's BAZAAR (the Bazaar page opens with the AH search; both markets listed), the hub bar on both pages (Market
       active, no Auctions tab), both pages through hub_tab_harness.page_check, bazaar:fn:open / ah:fn:open junk
  D    live     a scratch COPY of the live Skyy_SkyyBazaar + Skyy_SkyyAuctions (NewBetaTest; read-only sources): started twice like
                setup() (the second start writes nothing), the merged page built + searched + switched both ways, no file written
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, json, shutil, types, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import hub_tab_harness as H
import skyyui as SUI
import tier_tags as TT

VERSION = "0.1.17"
PKG = "com.skyy.bazaar."
APKG = "com.skyy.auctions."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyBazaar-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyBazaar-0.1.16.jar")
AH_JAR = os.path.abspath(HK.arg("--ah", os.path.join(ROOT, "SkyyAuctions", "SkyyAuctions-0.1.9.jar")))
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "hubmkt", "bz")))
LIVE_SAVES = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods")
EXPECT = {
    "BzPage": ["+f ahCells", "+f ahSel", "+f ahRows", "+m marketFind", "~c ", "~m render", "~m handleDataEvent"],
    "BzHubOpen": ["~m register"],                                   # the label "Market"
    "SkyyBazaarPlugin": ["~m setup", "~m shutdown"],
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"],          # the version texts
}
ADDED = ["BzMarket", "BzMkSort", "BzOpenFn"]


def bz_prep(E, J, home):
    """the jar's data steps exactly as SkyyBazaarPlugin.setup() runs them (every one-time update, load, reprice, publish)"""
    from jpype import JClass
    J("BzUtil").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyBazaar")
    d = E.Paths.get(home) if hasattr(E, "Paths") else JClass("java.nio.file.Paths").get(home)
    os.makedirs(home, exist_ok=True)
    C = J("Catalog")
    C.FILE = d.resolve("products.properties")
    C.PFILE = d.resolve("pricing.properties")
    J("Market").FILE = d.resolve("market.properties")
    J("Market").LOGFILE = d.resolve("trades.log")
    J("BzCfg").load(d)
    for m in ("migrate", "migrate14", "migrate19", "migrate110", "migrate114", "migrate115", "migrate116"):
        getattr(C, m)()
    C.load()
    J("Market").load()
    C.reprice()
    J("Market").publishAll()
    C.flushIfDirty()
    J("BzConfirm").load(d)


def ah_prep(E, J, home):
    """SkyyAuctions' data statics on folder home, as its setup() points them (the 0.1.8 harness prep)"""
    from jpype import JClass
    J("AhUtil").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyAuctions")
    os.makedirs(home, exist_ok=True)
    d = JClass("java.nio.file.Paths").get(home)
    J("AhCfg").DIR = d
    J("AhCfg").FILE = d.resolve("config.properties")
    J("AhCfg").BLOCKED = d.resolveSibling("Skyy_Market").resolve("blocked.txt")
    J("AhLog").FILE = d.resolve("auctions.log")
    J("AhStore").DIR = d
    J("AhStore").LDIR = d.resolve("listings")
    J("AhStore").ADIR = d.resolve("archive")
    J("AhStore").BADDIR = d.resolve("listings").resolve("bad")
    J("AhStore").STATE = d.resolve("state.properties")
    J("AhCfg").load()
    J("AhStore").load()


def L(n):
    return {"$numberLong": str(int(n))}


def rec_json(i, item, qty, price, ends_in, now, name, seller="Seller", state="ACTIVE"):
    r = {"v": {"$numberInt": "1"}, "type": "BIN", "id": str(i), "state": state, "closed": False, "rev": L(1),
         "seller": {"uuid": "00000000-0000-4000-8000-0000000000%02d" % (i % 100), "key": "k%d" % i, "name": seller, "profile": "P"},
         "buyer": None, "sale": None,
         "claims": {"sellerCoins": "NONE", "sellerItem": "NONE", "buyerItem": "NONE", "sellerItemQty": L(qty), "buyerItemQty": L(qty)},
         "item": {"id": item, "qty": {"$numberInt": str(qty)}, "quality": {"$numberInt": "0"}},
         "price": L(price), "startBid": L(price), "topBid": L(0), "topBidder": None, "bids": [],
         "endsAt": L(now + ends_in), "graceUntil": L(now - 100000), "createdAt": L(now - 200000),
         "fee": {"listing": L(5), "duration": L(0), "refunded": False}, "noticed": {"seller": False}, "removed": None, "regrants": [],
         "closedAt": L(0), "name": name, "search": ("%s %s %s" % (name, item, seller)).lower(), "category": "MATERIALS"}
    return json.dumps(r)


def boot2(scratch, jars, label):
    """hub_tab_harness.boot with SEVERAL jars on the class path (Bazaar + Auctions, different packages, each with its own HubBar)"""
    from jpype import JClass
    hcls = os.path.join(scratch, "hcls_" + label)
    os.makedirs(hcls, exist_ok=True)
    os.chdir(scratch)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, hcls] + list(jars), verify=True)
    E = H.T19.engine(scratch, hcls)
    W = H.World()
    W.E = E
    UniC = JClass("com.hypixel.hytale.server.core.universe.Universe")
    byU = H.jf(UniC.class_, "playersByUuid").get(UniC.get())

    def mkp(uid, name):
        P = E.player(uid, name=name)
        byU.put(uid, P.pr)
        E.UniH.PL.add(P.pr)
        E.PLAYERS.add(P.pr)
        return P
    W.mkp = mkp
    W.P = mkp(E.PLAIN, "SkyyPlain")
    W.O = mkp(E.OP, "SkyyOp")
    E.Paths = JClass("java.nio.file.Paths")
    return W


def build_page(E, P):
    from jpype import JClass
    pg = P.pm.getCustomPage()
    b = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")()
    ev = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")()
    pg.build(P.ref, b, ev, P.st)
    return pg, H.cmds_of(b), H.events_of(ev)


def set_of(cm, sel):
    """the newest b.set value of a selector (the command's data is JSON {"0": value})"""
    v = [d for ty, s, t, d in cm if ty == "Set" and s == sel]
    if not v:
        return None
    try:
        return json.loads(v[-1]).get("0")
    except Exception:
        return v[-1]


def click(E, P, data):
    P.pm.handleLegacyCustomPageEvent(P.ref, P.st, E.CPE(E.CPT.Data, data))
    E.pump(P)
    return P.pm.getCustomPage()


def cls_of(o):
    return None if o is None else str(o.getClass().getName())


def spec_ns(**kw):
    return types.SimpleNamespace(**kw)


BZ_SPEC = spec_ns(hub="market", tab="bazaar", label="Market", prefix="SkyyBzF", idp="SkyyBz", legacy_texts=[])
AH_SPEC = spec_ns(hub="market", tab="bazaar", label="Market", prefix="SkyyAhF", idp="SkyyAh",
                  legacy_texts=["Search items or sellers...", "e.g. 12000 or 12k"])


# ------------------------------------------------------------------------------------------------------------------- MK
def run_mk(out, bz_jar, ah_jar, scratch):
    import jpype
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    if not os.path.isfile(ah_jar) or not os.path.isfile(bz_jar):
        K.check(False, "MK: both jars are needed (%s, %s)" % (bz_jar, ah_jar))
        K.save()
        return
    W = boot2(scratch, [bz_jar, ah_jar], "mk")
    E = W.E
    JB = lambda n: JClass(PKG + n)
    JA = lambda n: JClass(APKG + n)
    TRUE, FALSE = JClass("java.lang.Boolean").TRUE, JClass("java.lang.Boolean").FALSE
    HBB, HBA = JB("HubBar"), JA("HubBar")
    E.br = HBB.map()
    K.check(int(JClass("java.lang.System").identityHashCode(E.br)) == int(JClass("java.lang.System").identityHashCode(HBA.map())),
            "MK: both jars' HubBar use the one skyy.bridge")
    bz_prep(E, JB, os.path.join(scratch, "mk_bz"))
    ah_prep(E, JA, os.path.join(scratch, "mk_ah", "Skyy_SkyyAuctions"))
    P = W.P
    u = P.pr.getUuid()
    E.br.put("hub:last:" + str(u), JClass("java.util.concurrent.ConcurrentHashMap")())

    # ---------------------------------------------------------------- the tier table + sort
    M = JB("BzMarket")
    bad = [i for i in TT.ROWS if int(M.tier(i, -1)) != TT.tier(i)]
    K.check(not bad and len(M.tiers()) == len(TT.ROWS), "MK tier: BzMarket.tier = tools/tier_tags.py for all %d rows (%s)" % (len(TT.ROWS), bad[:3]))
    lvbad = [(lv, x) for lv in range(0, 90) for x in ("Weapon_Sword_Iron", "Armor_Onyxium_Head", "Tool_Pickaxe_Iron")
             if TT.tier(x) is None and int(M.tier(x, lv)) != TT.tier_for_level(lv, x)]
    K.check(not lvbad, "MK tier: an untabled id with a level takes tier_for_level's band (%s)" % lvbad[:3])
    K.check(int(M.tier("Weapon_Sword_Iron", -1)) == 99 and int(M.tier(None, 5)) == 99, "MK tier: untiered without a level = 99 (last)")
    Obj = JClass("java.lang.Object")
    I_, S_ = JClass("java.lang.Integer"), JClass("java.lang.String")
    ent = lambda t, n, k, i: jpype.JArray(Obj)([I_(t), S_(n), I_(k), S_(i), S_(i)])
    lst = JClass("java.util.ArrayList")()
    for e in (ent(3, "iron ore", 1, "Ore_Iron"), ent(99, "apple", 0, "Apple"), ent(3, "iron ore", 0, "Ore_Iron"), ent(2, "copper", 0, "Ore_Copper"),
              ent(3, "bar", 0, "Bar")):
        lst.add(e)
    JClass("java.util.Collections").sort(lst, JB("BzMkSort")())
    K.eq([(int(x[0]), str(x[1]), int(x[2])) for x in lst], [(2, "copper", 0), (3, "bar", 0), (3, "iron ore", 0), (3, "iron ore", 1), (99, "apple", 0)],
         "MK sort: tier, then name, then Bazaar before AH")

    # ---------------------------------------------------------------- registry: Market shown, Auctions hidden while merged
    K.eq(int(JB("BzHubOpen").register()), 1, "MK REG: the Bazaar puts its tab")
    K.eq(int(JA("AhHubOpen").register()), 1, "MK REG: the Auction House puts its tab")
    e_bz, e_ah = E.br.get("hub:tab:market:bazaar"), E.br.get("hub:tab:market:auctions")
    K.check(str(e_bz[1]) == "Market" and int(e_bz[2]) == 10 and str(e_bz[3]) == "bazaar", "MK REG: hub:tab:market:bazaar = Market, 10, /bazaar")
    K.check(str(e_ah[1]) == "Auctions" and e_ah[5] is not None and cls_of(e_ah[5]) == APKG + "AhHubVis", "MK REG: the Auctions tab carries AhHubVis")
    K.eq([str(x[0]) for x in HBB.tabs("market", u)], ["bazaar", "auctions"], "MK VIS: without bazaar:fn:open (an older Bazaar) the Auctions tab shows")
    E.br.put("bazaar:fn:open", JB("BzOpenFn")())
    K.eq([str(x[0]) for x in HBB.tabs("market", u)], ["bazaar"], "MK VIS: with the merged Bazaar the hub bar shows ONE tab (Market)")
    K.check(str(JA("AhPage").myTab()) == "bazaar" and bool(JA("AhPage").merged()), "MK: the AH page's active tab is the Market tab")
    K.check(not bool(JB("BzMarket").ahOn()), "MK: ahOn false before SkyyAuctions publishes ah:fn:find / ah:fn:open")
    E.br.put("ah:fn:find", JA("AhMarketFn")(0))
    E.br.put("ah:fn:open", JA("AhMarketFn")(1))
    K.check(bool(JB("BzMarket").ahOn()), "MK: ahOn once both AH Functions are on the bridge")

    # ---------------------------------------------------------------- listings + ah:fn:find
    now = int(JClass("java.lang.System").currentTimeMillis())
    Rec, Sto = JA("AhRec"), JA("AhStore")
    rows = [(1, "Ore_Iron", 10, 500, 3600000, "Iron Ore", "Ann"), (2, "Ore_Iron", 5, 250, 600000, "Iron Ore", "Bob"),
            (3, "Ingredient_Bar_Iron", 1, 120, 7200000, "Iron Bar", "Cid"), (4, "Weapon_Sword_Iron", 1, 900, 86400000, "Iron Sword", "Dee"),
            (5, "Ore_Iron", 1, 1, -5000, "Iron Ore", "Old"), (6, "Ore_Copper", 4, 40, 3600000, "Copper Ore", "Eve"),
            (7, "Ore_Iron", 2, 100, 1800000, "Iron Ore", "Fay")]
    for i, it, q, pr_, ends, nm, sel in rows:
        Sto.livePut(str(i), Rec.parse(rec_json(i, it, q, pr_, ends, now, nm, sel)))
    find = E.br.get("ah:fn:find")
    r = list(find.apply("iron"))
    by = dict((str(x[0]), x) for x in r)
    K.eq(sorted(by), ["Ingredient_Bar_Iron", "Ore_Iron", "Weapon_Sword_Iron"], "MK find: 'iron' = one row per item id (expired #5 and Copper left out)")
    oi = by.get("Ore_Iron")
    K.check(oi is not None and len(oi) == 9 and int(oi[2]) == 3 and int(oi[3]) == 50 and int(oi[4]) == 500 and int(oi[5]) == 10,
            "MK find: Ore_Iron = 3 listings (#1 #2 #7, all 50 each), the tie goes to the lower listing number #1 -> 500 for 10 (%s)" % (None if oi is None else list(oi)))
    Sto.livePut("8", Rec.parse(rec_json(8, "Ore_Iron", 3, 120, 7200000, now, "Iron Ore", "Gus")))
    oi8 = dict((str(x[0]), x) for x in find.apply("iron")).get("Ore_Iron")
    K.check(oi8 is not None and int(oi8[2]) == 4 and int(oi8[3]) == 40 and int(oi8[4]) == 120 and int(oi8[5]) == 3,
            "MK find: a cheaper listing each (#8, 120 for 3 = 40 each) becomes the cheapest (%s)" % (None if oi8 is None else list(oi8)))
    K.check(oi is not None and (str(oi[6]).startswith("9m ") or str(oi[6]).startswith("10m ")),
            "MK find: endsIn = the soonest end (#2, 10 min) as text (%s)" % (None if oi is None else oi[6]))
    K.check(all(JClass("java.lang.String").class_.isInstance(x[0]) and JClass("java.lang.Integer").class_.isInstance(x[2])
                and JClass("java.lang.Long").class_.isInstance(x[3]) and JClass("java.lang.Integer").class_.isInstance(x[7]) for x in r),
            "MK find: the KEY CONTRACT types (String, String, Integer, Long, Long, Long, String, Integer, String)")
    K.eq(sorted(str(x[0]) for x in find.apply("iron ore")), ["Ore_Iron"], "MK find: every word must match ('iron ore')")
    K.eq(sorted(str(x[0]) for x in find.apply("fay")), ["Ore_Iron"], "MK find: the seller's name matches like the AH search")
    K.eq([len(list(find.apply(x))) for x in ("", "   ", "zzzz")], [0, 0, 0], "MK find: empty / blank / no match -> empty")
    K.eq(len(list(find.apply(None))), 0, "MK find: null -> empty")
    K.check(find.apply(jpype.JArray(Obj)([S_("copper")])).size() == 1, "MK find: Object[]{ query } also works")
    # a blocked item (the market wall) is left out
    blk = JClass("java.util.concurrent.ConcurrentHashMap")()
    blk.put("Ingredient_Bar_Iron", "test wall")
    old_blk = E.br.get("market:blocked")
    E.br.put("market:blocked", blk)
    K.check("Ingredient_Bar_Iron" not in [str(x[0]) for x in find.apply("iron")], "MK find: a blocked item (market:blocked) is left out")
    if old_blk is None:
        E.br.remove("market:blocked")
    else:
        E.br.put("market:blocked", old_blk)
    opn = E.br.get("ah:fn:open")
    K.check(opn.apply("x") == FALSE and opn.apply(jpype.JArray(Obj)([JClass("java.util.UUID").randomUUID(), S_("q")])) == FALSE,
            "MK open: junk / an offline player = FALSE")
    K.check(E.br.get("bazaar:fn:open").apply("x") == FALSE and E.br.get("bazaar:fn:open").apply(jpype.JArray(Obj)([S_("nouuid")])) == FALSE,
            "MK bazaar:fn:open: junk = FALSE")

    # ---------------------------------------------------------------- BzMarket.ahFind's row guard
    @JImplements("java.util.function.Function")
    class BadFind:
        @JOverride
        def apply(self, o):
            L_ = JClass("java.util.ArrayList")()
            Lg = JClass("java.lang.Long")
            good = jpype.JArray(Obj)([S_("Ore_Iron"), S_("Iron Ore"), I_(2), Lg(5), Lg(10), Lg(2), S_("1h 0m"), I_(-1), S_("#fff")])
            L_.add(good)
            L_.add(jpype.JArray(Obj)([S_('Bad"Id'), S_("x"), I_(1), Lg(5), Lg(10), Lg(2), S_("1h"), I_(-1), S_("")]))     # unsafe id
            L_.add(jpype.JArray(Obj)([S_("Ore_Gold"), S_("x"), S_("1"), Lg(5), Lg(10), Lg(2), S_("1h"), I_(-1), S_("")]))      # wrong type
            L_.add(jpype.JArray(Obj)([S_("Ore_Gold"), S_("x"), I_(0), Lg(5), Lg(10), Lg(2), S_("1h"), I_(-1), S_("")]))        # 0 listings
            L_.add(jpype.JArray(Obj)([S_("Ore_Gold")]))                                                                       # short
            L_.add(S_("not a row"))
            return L_
    real = E.br.get("ah:fn:find")
    E.br.put("ah:fn:find", BadFind())
    g = list(M.ahFind("iron"))
    K.eq([str(x[0]) for x in g], ["Ore_Iron"], "MK guard: BzMarket.ahFind keeps only well-typed rows with a markup-safe id")
    E.br.put("ah:fn:find", real)

    # ---------------------------------------------------------------- the ONE search on the Bazaar page
    K.eq(str(HBB.open(P.pr, u, "market", "bazaar")), "bridge", "MK: the Market tab opens the Bazaar page")
    E.pump(P)
    pg0, cm0, ev0 = build_page(E, P)
    K.check(cls_of(pg0) == PKG + "BzPage", "MK: the Bazaar page is open")
    H.page_check(K, E, BZ_SPEC, P, pg0, HBB, "MK PAGE Bazaar")
    tabs0 = [t for ty, s, t, d in cm0 if t and s == "#SkyyBzFHubTabs" and t.startswith("TextButton")]
    K.check(len(tabs0) == 1 and 'Text: "Market"' in tabs0[0], "MK: the hub bar = ONE tab, Market (%d)" % len(tabs0))
    K.check(any(t and "#SkyyBzMkAh " in t for ty, s, t, d in cm0) and any(t and "#SkyyBzMkBz " in t for ty, s, t, d in cm0),
            "MK: the sub-view row: BAZAAR + AUCTION HOUSE")
    K.check(any(s == "#SkyyBzMkAh" and "mk:ah" in tx for s, tx in ev0), "MK: AUCTION HOUSE is bound to mk:ah")
    K.check(str(set_of(cm0, "#SkyyBzMkHint.Text")).startswith("Bazaar: instant trades with the market.   Auction House"), "MK: caption 1 (both markets)")
    pg = click(E, P, '{"a":"find","@BzFind":"iron"}')
    pg1, cm1, ev1 = build_page(E, P)
    order = []
    for k in range(39):
        cid = pg1.cells[k] if pg1.cells[k] is not None else pg1.ahCells[k]
        if cid is None:
            continue
        order.append((str(cid), "bz" if pg1.cells[k] is not None else "ah"))
    K.check(("Ore_Iron", "ah") in order and ("Ingredient_Bar_Iron", "ah") in order and ("Weapon_Sword_Iron", "ah") in order,
            "MK search: the AH items are in the results (%s)" % [o for o in order if o[1] == "ah"])
    K.check(("Ore_Iron", "bz") in order, "MK search: the Bazaar product Iron Ore too")
    K.check(order.index(("Ore_Iron", "bz")) + 1 == order.index(("Ore_Iron", "ah")), "MK search: the same item - Bazaar first, the AH cell right after")
    rowsd = dict((str(k), pg1.ahRows.get(k)) for k in pg1.ahRows.keySet())

    def tkey(cid, kind):
        if kind == "bz":
            p_ = JB("Catalog").get(cid)
            return (int(M.tier(cid, -1)), str(p_.name if p_.name is not None else cid).lower(), 0)
        rw = rowsd[cid]
        return (int(M.tier(cid, int(rw[7]))), str(rw[1]).lower(), 1)
    keys = [tkey(c, k) for c, k in order]
    K.check(keys == sorted(keys), "MK search: sorted by tier, then name, then Bazaar before AH (%s)" % keys[:6])
    K.check(keys[0][0] <= keys[-1][0] and any(k[0] == 3 for k in keys), "MK search: tiers seen %s" % sorted(set(k[0] for k in keys)))
    ia = [k for k in range(39) if pg1.ahCells[k] is not None and str(pg1.ahCells[k]) == "Ore_Iron"][0]
    K.eq(set_of(cm1, "#SkyyBzCell%dQty.Text" % ia), "AH 4", "MK search: the AH cell's corner says AH 4 (4 listings)")
    nbz, nah = len([o for o in order if o[1] == "bz"]), len([o for o in order if o[1] == "ah"])
    K.check(str(set_of(cm1, "#SkyyBzSub.Text")).endswith("%d Bazaar + %d Auction House" % (nbz, nah)), "MK search: header %s" % set_of(cm1, "#SkyyBzSub.Text"))
    # an AH cell: the AH detail, no product selected, no Bazaar trade button
    log_before = HK.tree_hash(os.path.join(scratch, "mk_bz"))
    pg = click(E, P, '{"a":"cell:%d","@BzFind":"iron"}' % ia)
    pg2, cm2, ev2 = build_page(E, P)
    K.check(str(pg2.ahSel) == "Ore_Iron" and pg2.sel is None, "MK cell: an AH cell selects the AH item, never a product (sel null)")
    K.check(str(set_of(cm2, "#SkyyBzDName.Text")) == "Auction House - Iron Ore" and "Buy It Now from 40 coins each" in str(set_of(cm2, "#SkyyBzDBuy.Text")),
            "MK cell: the detail says Auction House + the lowest Buy It Now (%s)" % set_of(cm2, "#SkyyBzDBuy.Text"))
    K.check(any(t and "#SkyyBzAhOpen " in t for ty, s, t, d in cm2) and any(s == "#SkyyBzAhOpen" and "ahopen" in tx for s, tx in ev2),
            "MK cell: OPEN IN AUCTION HOUSE drawn + bound")
    K.check(not any(t and re.search(r"#SkyyBz(Buy1|BuyStk|Sell1|SellStk|SellAll|ABuy|ASell) ", t) for ty, s, t, d in cm2),
            "MK cell: no Bazaar Buy / Sell button with an AH cell selected")
    H.page_check(K, E, BZ_SPEC, P, pg2, HBB, "MK PAGE Bazaar (AH cell)")
    for a in ("buy1", "buystk", "sell1", "sellstk", "sellall", "abuy", "asell"):
        click(E, P, '{"a":"%s","@BzFind":"iron","@BzAmount":"5"}' % a)
    K.eq(HK.tree_hash(os.path.join(scratch, "mk_bz")), log_before, "MK cell: Buy / Sell clicks with an AH cell selected trade nothing (no Bazaar file written)")
    K.check(P.pm.getCustomPage().sel is None, "MK cell: still no product selected")
    # a Bazaar cell clears the AH selection
    ib = order.index(("Ore_Iron", "bz"))
    ibx = [k for k in range(39) if pg1.cells[k] is not None and str(pg1.cells[k]) == "Ore_Iron"][0]
    pgx = click(E, P, '{"a":"cell:%d","@BzFind":"iron"}' % ibx)
    K.check(str(pgx.sel) == "Ore_Iron" and pgx.ahSel is None, "MK cell: a Bazaar cell selects the product and clears the AH item (%s)" % ib)
    click(E, P, '{"a":"cell:%d","@BzFind":"iron"}' % ia)
    # OPEN IN AUCTION HOUSE -> the AH page filtered to that item
    pa = click(E, P, '{"a":"ahopen","@BzFind":"iron"}')
    K.check(cls_of(pa) == APKG + "AhPage" and str(pa.view) == "browse" and str(pa.query) == "Ore_Iron",
            "MK OPEN: the AH page opens on Browse filtered to Ore_Iron (%s %s)" % (cls_of(pa), None if pa is None else pa.query))
    pa_, cma, eva = build_page(E, P)
    K.check(sorted(str(x) for x in pa_.rowIds if x is not None) == ["1", "2", "7", "8"],
            "MK OPEN: the AH list = the 4 live Ore_Iron listings (%s)" % [str(x) for x in pa_.rowIds if x is not None])
    H.page_check(K, E, AH_SPEC, P, pa_, HBB, "MK PAGE Auction House")
    tabsa = [t for ty, s, t, d in cma if t and s == "#SkyyAhFHubTabs" and t.startswith("TextButton")]
    K.check(len(tabsa) == 1 and 'Text: "Market"' in tabsa[0] and "Tab_Selected" in tabsa[0], "MK AH: the hub bar = ONE tab, Market, active")
    K.check(any(t and "#SkyyAhMkBz " in t for ty, s, t, d in cma) and any(s == "#SkyyAhMkBz" and "mk:bz" in tx for s, tx in eva)
            and any(t and "#SkyyAhMkAh " in t for ty, s, t, d in cma), "MK AH: the sub-view row BAZAAR (bound mk:bz) + AUCTION HOUSE")
    K.check(any(t and "Group #SkyyAhTop " in t and "Height: 36" in t for ty, s, t, d in cma) and "Width: 1128, Height: 976" in cma[0][2],
            "MK AH: the 36 px row, 1128 x 976")
    n0 = len(E.sent(P))
    pself = click(E, P, '{"a":"hub:bazaar","@AhSearch":"Ore_Iron"}')
    K.check(pself is not None and cls_of(pself) == APKG + "AhPage" and "#SkyyAhFTitle.Text" in E.strs_of(P, n0), "MK AH: the Market tab = self (answered)")
    # the AH page's BAZAAR with a typed search -> the Bazaar page with that search, both markets
    pb = click(E, P, '{"a":"mk:bz","@AhSearch":"sword"}')
    K.check(cls_of(pb) == PKG + "BzPage" and str(pb.query) == "sword", "MK BAZAAR: the Bazaar page opens with the AH search (%s %s)" % (cls_of(pb), None if pb is None else pb.query))
    pb_, cmb, evb = build_page(E, P)
    K.check("Weapon_Sword_Iron" in [str(x) for x in pb_.ahCells if x is not None], "MK BAZAAR: the AH sword is in the Bazaar search results")
    # the Bazaar's AUCTION HOUSE with a search -> the AH page with that search
    pc = click(E, P, '{"a":"mk:ah","@BzFind":"sword"}')
    K.check(cls_of(pc) == APKG + "AhPage" and str(pc.query) == "sword", "MK AUCTION HOUSE: the AH page opens with the Bazaar search (%s)" % (None if pc is None else pc.query))
    # without the Bazaar's merge (an older Bazaar): the AH page shows its own tab, no BAZAAR button
    E.br.remove("bazaar:fn:open")
    pd_, cmd_, evd_ = build_page(E, P)
    K.check(not any(t and "#SkyyAhMkBz " in t for ty, s, t, d in cmd_) and str(JA("AhPage").myTab()) == "auctions", "MK AH old Bazaar: no BAZAAR button, own tab")
    K.eq(sorted(str(x[0]) for x in HBB.tabs("market", u)), ["auctions", "bazaar"], "MK AH old Bazaar: the Auctions tab is back")
    E.br.put("bazaar:fn:open", JB("BzOpenFn")())
    # without SkyyAuctions 0.1.9: the Bazaar page has no AUCTION HOUSE button and the old header
    E.br.remove("ah:fn:find")
    E.br.remove("ah:fn:open")
    K.eq(str(HBB.open(P.pr, u, "market", "bazaar")), "bridge", "MK: Market reopens")
    E.pump(P)
    click(E, P, '{"a":"find","@BzFind":"iron"}')
    pe, cme, eve = build_page(E, P)
    K.check(not any(t and "#SkyyBzMkAh " in t for ty, s, t, d in cme) and str(set_of(cme, "#SkyyBzMkHint.Text")).endswith("not on this server."),
            "MK no AH: no AUCTION HOUSE button, caption 2")
    K.check(str(set_of(cme, "#SkyyBzSub.Text")).endswith("in all tabs") and not [x for x in pe.ahCells if x is not None], "MK no AH: the Bazaar-only search")
    H.page_check(K, E, BZ_SPEC, P, pe, HBB, "MK PAGE Bazaar (no AH)")
    pf = click(E, P, '{"a":"mk:ah","@BzFind":"iron"}')
    K.check(cls_of(pf) == PKG + "BzPage" and ("ah" in [str(x) for x in E.CM.lines] or "not on this server" in str(pf.info)),
            "MK no AH: AUCTION HOUSE (stale click) falls back to /ah or says it is not there (%s / %s)" % (list(E.CM.lines)[-2:], pf.info))
    K.save()


# ------------------------------------------------------------------------------------------------------------------- HUB extra
def extra_hub(K, W, J):
    from jpype import JClass
    E = W.E
    J("BzHubOpen").register()
    X = W.O
    E.br.put("hub:last:" + str(X.pr.getUuid()), JClass("java.util.concurrent.ConcurrentHashMap")())
    J("HubBar").open(X.pr, X.pr.getUuid(), "market", "bazaar")
    E.pump(X)
    pg, cm, ev = build_page(E, X)
    K.check("Width: 1094, Height: 979" in cm[0][2], "PAGE: 1094 x 979 (%s)" % cm[0][2][:60])
    K.check(any(t and "#SkyyBzMkBz " in t for ty, s, t, d in cm) and not any(t and "#SkyyBzMkAh " in t for ty, s, t, d in cm),
            "PAGE: without SkyyAuctions the sub-view row has BAZAAR only (the AH slot is empty)")
    K.check(str(set_of(cm, "#SkyyBzMkHint.Text")).endswith("The Auction House is not on this server."), "PAGE: caption 2 without SkyyAuctions")
    rows = [c for c in cm if c[2] and re.search(r"Group #SkyyBzRow\d+ ", c[2])]
    K.check(len(rows) == 3, "PAGE: the grid is still 3 rows")
    J("HubBar").removeAll()


def chk_next(K, E, J, P, before, after, f0):
    K.check(after is not None and str(after.getClass().getSimpleName()) == "BzPage" and len(E.sent(P)) > f0, "CLICK: Next (not a hub click) acts on the page")


def chk_find(K, E, J, P, before, after, f0):
    K.check(after is not None and str(after.query) == "log", "CLICK: Find applies the search (%s)" % (None if after is None else after.query))


S = H.Spec(name="SkyyBazaar", version=VERSION, pkg=PKG, hub="market", tab="bazaar", mod="SkyyBazaar", open_cls="BzHubOpen", vis_cls=None,
           page_cls="BzPage", prefix="SkyyBzF", idp="SkyyBz", plugin_cls="SkyyBazaarPlugin", register_call="BzHubOpen.register",
           register=lambda J: J("BzHubOpen").register(), prep=bz_prep, fail_text="could not open right now",
           clicks=[('{"a":"next"}', chk_next), ('{"a":"find","@BzFind":"log"}', chk_find)], extra_hub=extra_hub,
           jar=JAR, old_jar=OLD_JAR, scratch=SCRATCH, script=__file__, added=ADDED, expect=EXPECT)
S.label = "Market"          # 0.1.17: the merged tab's label (the kit table HUB_TABS still says "Bazaar")


# ------------------------------------------------------------------------------------------------------------------- D: live
def run_live2(out, jar, scratch, home):
    """two starts on the scratch copy (the second writes nothing), the merged page (with the live AH copy) built, searched, switched"""
    K = HK.Child(out)
    if not os.path.isfile(AH_JAR):
        K.check(False, "D: SkyyAuctions 0.1.9 jar missing (%s)" % AH_JAR)
        K.save()
        return
    ah_home = os.path.join(scratch, "live_ah", "Skyy_SkyyAuctions")
    src = os.path.join(LIVE_SAVES, "Skyy_SkyyAuctions")
    K.check(os.path.isdir(src), "D: the live Skyy_SkyyAuctions exists")
    shutil.copytree(src, ah_home)
    W = boot2(scratch, [jar, AH_JAR], "live")
    E = W.E
    from jpype import JClass
    JB = lambda n: JClass(PKG + n)
    JA = lambda n: JClass(APKG + n)
    E.br = JB("HubBar").map()
    bz_prep(E, JB, home)
    ah_prep(E, JA, ah_home)
    h0, a0 = HK.tree_hash(home), HK.tree_hash(ah_home)
    bz_prep(E, JB, home)
    ah_prep(E, JA, ah_home)
    K.eq((HK.tree_hash(home), HK.tree_hash(ah_home)), (h0, a0), "D: a second start writes nothing (Bazaar + Auctions copies)")
    K.check(int(JB("Catalog").all().size()) > 400, "D: %d live products" % int(JB("Catalog").all().size()))
    K.notes.append("D: live AH listings loaded %d (active %d)" % (int(JA("AhStore").LIVE.size()), int(JA("AhStore").active(int(JClass("java.lang.System").currentTimeMillis())).size())))
    P = W.P
    u = P.pr.getUuid()
    for start in (1, 2):
        JB("BzHubOpen").register()
        JA("AhHubOpen").register()
        E.br.put("bazaar:fn:open", JB("BzOpenFn")())
        E.br.put("ah:fn:find", JA("AhMarketFn")(0))
        E.br.put("ah:fn:open", JA("AhMarketFn")(1))
        K.eq([str(x[0]) for x in JB("HubBar").tabs("market", u)], ["bazaar"], "D%d: one Market tab" % start)
        K.eq(str(JB("HubBar").open(P.pr, u, "market", "bazaar")), "bridge", "D%d: Market opens" % start)
        E.pump(P)
        pg = click(E, P, '{"a":"find","@BzFind":"iron"}')
        pg_, cm, ev = build_page(E, P)
        K.check(len(cm) > 10 and str(pg_.query) == "iron" and str(set_of(cm, "#SkyyBzSub.Text")).find("Auction House") > 0,
                "D%d: the live search (%s)" % (start, set_of(cm, "#SkyyBzSub.Text")))
        pa = click(E, P, '{"a":"mk:ah","@BzFind":"iron"}')
        K.check(cls_of(pa) == APKG + "AhPage" and str(pa.query) == "iron", "D%d: AUCTION HOUSE opens the live AH page with the search" % start)
        build_page(E, P)
        pb = click(E, P, '{"a":"mk:bz","@AhSearch":"iron"}')
        K.check(cls_of(pb) == PKG + "BzPage", "D%d: BAZAAR opens the Bazaar page again" % start)
        click(E, P, '{"a":"hub:close"}')
        JB("HubBar").removeAll()
        JA("HubBar").removeAll()
        for k in ("bazaar:fn:open", "ah:fn:find", "ah:fn:open"):
            E.br.remove(k)
        K.eq((HK.tree_hash(home), HK.tree_hash(ah_home)), (h0, a0), "D%d: no file written in either live copy" % start)
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyBazaar", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("hub", lambda out, jar, scratch, home: H.run_hub(S, out, jar, scratch)),
                   ("mk", lambda out, jar, scratch, home: run_mk(out, jar, AH_JAR, scratch)),
                   ("live", run_live2)],
           script=__file__, live=(os.path.join(LIVE_SAVES, "Skyy_SkyyBazaar"), "Skyy_SkyyBazaar"))
