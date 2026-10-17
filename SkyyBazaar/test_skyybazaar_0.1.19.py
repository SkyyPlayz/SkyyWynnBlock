"""Harness for SkyyBazaar 0.1.19 (round coll24, the SkyyBazaar half: the C1 Enchanted products from the live tools/skyyench.py table, the
one-time update migrate119, the Eternal seed buy lock through SkyyCollections 0.2.24's coll:fn:eternal; tools/bazaar_0_1_19_patch.py).
Build first: python tools/bazaar_0_1_19_patch.py && python SkyyBazaar/build_skyybazaar_0.1.19.py   (+ SkyyAuctions 0.1.10 for MK / D)

    python SkyyBazaar/test_skyybazaar_0.1.19.py [--dir <folder inside tools/dev/scratch/>] [--keep] [--ah <SkyyAuctions jar>]

Phases (fresh child JVMs, tools/harness_kit.py + the engine stand-ins of tools/hub_tab_harness.py; -Xverify:all everywhere):
  A    verify   every class loads + initialises
  C    compare  0.1.18 -> 0.1.19: exactly the listed members differ (Catalog's NEW0119 / migrate119 / marker + its tables, Trader.eterWhy +
                buy0, the page's buyClick / amountAction pre-checks, the version texts)
  HUB  the 0.1.18 page phase unchanged (every state through SUI.assert_menu_page, the clicks, rule 7, the buy / sell smoke)
  ETER the Eternal seed lock with a stand-in coll:fn:eternal: locked -> Buy 1, Buy <stack>, the custom amount (price + Buy), the CONFIRM
       flow (never armed; an armed one refused) and Trader.buy0 / buy / buyC / buyN refuse BEFORE any coin or item moves (purse + inventory
       unchanged, the reason on the result line); "" -> buys; null -> the loading text; absent -> buys; a throwing Function -> refused, one
       WARN a minute; a normal seed never asks; selling an Eternal seed works while locked
  PRICE every listed Enchanted product at demand 1.0: instant sell <= RATIO x its base's instant sell x (1 + the max premium); buy 100 base
       -> sell 1 Enchanted loses coins (all of them); no un-compress recipe in any SET jar; every 0.1.18 seed line + processed-goods spec
       kept; the printed gift value table (Cobblestone, Iron, Mithril, Wheat, OakLog: the 0.2.21 gifts vs skyyench.gift_size)
  MK   both jars (this one + SkyyAuctions 0.1.10): the 0.1.18 merge paths
  D    live     a scratch COPY of the live Skyy_SkyyBazaar + Skyy_SkyyAuctions (NewBetaTest; read-only sources): started twice like
                setup(), the merged page built + searched + switched, every built page through assert_menu_page, start 2 writes nothing
  MIG  migrate119 on a scratch COPY of the live Skyy_SkyyBazaar, started TWICE like setup(): start 1 appends exactly the NEW0119 seed lines
       (every other byte + line ending kept; a hand-made line for one new id kept, not doubled), the history snapshot = the old bytes,
       the trades.log MIGRATE-0.1.19 lines with the undo, the marker; start 2 changes nothing
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, json, shutil, types

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import hub_tab_harness as H
import skyyui as SUI
import tier_tags as TT
import skyyench as EN
import ast, zipfile

VERSION = "0.1.19"
PKG = "com.skyy.bazaar."
APKG = "com.skyy.auctions."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyBazaar-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyBazaar-0.1.18.jar")
AH_JAR = os.path.abspath(HK.arg("--ah", os.path.join(ROOT, "SkyyAuctions", "SkyyAuctions-0.1.10.jar")))
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "coll24", "bz", "t")))
LIVE_SAVES = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods")
CELLS, COLS, SHOW = [74, 107, 148], [9, 6, 4], 180          # = the build's BZ_CELLS / BZ_GCOLS / BZ_SHOW
GRID_IH = 590 - 8
EXPECT = {
    "Catalog": ["+f NEW0119", "+f MIGRATED119", "+f M119_LOG", "+m migrate119", "~m writeModes", "~m loadModes", "~m init", "~<clinit>"],   # init: the inlined PROC_SPEC / SEED constants
    "Trader": ["+f ETER_WARN", "+m eterWhy", "~m buy0", "+<clinit>"],      # <clinit>: ETER_WARN = 0L
    "BzPage": ["~m buyClick", "~m amountAction"],
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"],          # the version texts
    "SkyyBazaarPlugin": ["~m setup"],                            # the ready line's version + migrate119
}
ADDED = []


def tier_of(n):
    """the build's tier rule (bz_pick): the biggest cell size whose rows all fit the list, else 0"""
    for k in (2, 1):
        if n > 0 and ((n + COLS[k] - 1) // COLS[k]) * (CELLS[k] + 4) <= GRID_IH:
            return k
    return 0


# ------------------------------------------------------------------------------------------------------------------- the data steps
def bz_prep(E, J, home):
    """the jar's data steps exactly as SkyyBazaarPlugin.setup() runs them (every one-time update, load, reprice, publish)"""
    from jpype import JClass
    J("BzUtil").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyBazaar")
    d = JClass("java.nio.file.Paths").get(home)
    os.makedirs(home, exist_ok=True)
    C = J("Catalog")
    C.FILE = d.resolve("products.properties")
    C.PFILE = d.resolve("pricing.properties")
    J("Market").FILE = d.resolve("market.properties")
    J("Market").LOGFILE = d.resolve("trades.log")
    J("BzCfg").load(d)
    for m in ("migrate", "migrate14", "migrate19", "migrate110", "migrate114", "migrate115", "migrate116", "migrate119"):
        getattr(C, m)()
    C.load()
    J("Market").load()
    C.reprice()
    J("Market").publishAll()
    C.flushIfDirty()
    J("BzConfirm").load(d)


def ah_prep(E, J, home):
    """SkyyAuctions' data statics on folder home, as its setup() points them"""
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


def rec_json(i, item, qty, price, ends_in, now, name, seller="Seller", state="ACTIVE", seller_uuid=None, seller_key=None):
    r = {"v": {"$numberInt": "1"}, "type": "BIN", "id": str(i), "state": state, "closed": False, "rev": L(1),
         "seller": {"uuid": seller_uuid or "00000000-0000-4000-8000-0000000000%02d" % (i % 100), "key": seller_key or "k%d" % i, "name": seller,
                    "profile": "P"},
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


_FAKE_N = [0]


def fake_items(E, ids):
    """an Item asset store that answers Item.UNKNOWN for every id given (the 0.1.5 / 0.1.14 harness stand-in): ItemStacks of those ids
    stack and fit in the stand-in inventories, so buys / sells / listings really move items. Returns the known-id set."""
    from jpype import JClass
    _FAKE_N[0] += 1
    sfx = "19n%d" % _FAKE_N[0]
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    us = uf.get(None)
    jp = JClass("javassist.ClassPool")(True)
    jp.appendClassPath(B.SERVER_JAR)
    CtF, CtM, CtC = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    fake = jp.makeClass("com.hypixel.hytale.assetstore.SkyyBzFakeStore" + sfx, jp.get("com.hypixel.hytale.assetstore.AssetStore"))
    fake.addConstructor(CtC.make("public SkyyBzFakeStore%s() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }" % sfx, fake))
    FAKEC = fake.toClass(AS.class_)
    store = us.allocateInstance(FAKEC)
    fm = AS.class_.getDeclaredField("assetMap")
    fm.setAccessible(True)
    DAMN = "com.hypixel.hytale.assetstore.map.DefaultAssetMap"
    ITMN = "com.hypixel.hytale.server.core.asset.type.item.config.Item"
    kmap = jp.makeClass("com.hypixel.hytale.assetstore.map.SkyyBzKnownMap" + sfx, jp.get(DAMN))
    kmap.addField(CtF.make("public static final java.util.HashSet KNOWN = new java.util.HashSet();", kmap))
    kmap.addConstructor(CtC.make("public SkyyBzKnownMap%s() { super(); }" % sfx, kmap))
    kmap.addMethod(CtM.make("public com.hypixel.hytale.assetstore.JsonAsset getAsset(Object key) { if (key != null && KNOWN.contains(key)) return "
                            "%s.UNKNOWN; return super.getAsset(key); }" % ITMN, kmap))
    KMap = JClass(kmap.toClass(JClass(DAMN).class_))
    fm.set(store, KMap())
    fi_ = JClass(ITMN).class_.getDeclaredField("ASSET_STORE")
    fi_.setAccessible(True)
    fi_.set(None, store)
    for i in ids:
        KMap.KNOWN.add(i)
    return KMap.KNOWN


def fake_coins(br, purse):
    """a SkyyCoins bridge (coins:fn:get / take / add) over the dict purse (uuid text -> coins)"""
    from jpype import JImplements, JOverride, JLong, JBoolean

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


def give(P, iid, qty, slot=0, sec="hotbar"):
    """put qty x iid into the player's real hotbar / storage slot (what the pages read: Inventory.getHotbar() / getStorage())"""
    from jpype import JClass, JShort
    ic = P.inv.getHotbar() if sec == "hotbar" else P.inv.getStorage()
    ic.setItemStackForSlot(JShort(slot), JClass("com.hypixel.hytale.server.core.inventory.ItemStack")(iid, qty))


# ------------------------------------------------------------------------------------------------------------------- page helpers
def build_page(E, P, pg=None):
    from jpype import JClass
    pg = pg if pg is not None else P.pm.getCustomPage()
    b = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")()
    ev = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")()
    pg.build(P.ref, b, ev, P.st)
    return pg, H.cmds_of(b), H.events_of(ev)


def unq(d):
    if d is None:
        return ""
    d = str(d)
    try:
        v = json.loads(d)
    except Exception:
        return d
    if isinstance(v, dict) and len(v) == 1:
        v = list(v.values())[0]
    return v if isinstance(v, str) else d


def set_of(cm, sel):
    """the newest b.set value of a selector"""
    v = [d for ty, s, t, d in cm if ty == "Set" and s == sel]
    return unq(v[-1]) if v else None


def apps_of(cm):
    return SUI.Appends([(None if s is None else s.lstrip("#"), t) for ty, s, t, d in cm if t is not None and ty and "Append" in ty])


def built(K, E, P, what, hub="market", pg=None, pager_ok=False, prefix_ok="Skyy", legacy=()):
    """build the open page into REAL builders and check it as a kit 1.7 hub page: the markup rules (check_page), the sky paths (the tab
    art hook allowed), every b.set / binding names an element, then SUI.assert_menu_page (1600 x 980, row 1 + row 2, ONE sub-tab row, no
    back button / < Menu text inline or b.set, no pager, the content fits). Returns (page, cmds, events, appends)."""
    pg, cm, ev = build_page(E, P, pg)
    apps = apps_of(cm)
    sets = [(s, unq(d)) for ty, s, t, d in cm if ty == "Set"]
    capps = apps
    if legacy:
        capps = SUI.Appends([(p, H._blank(SUI.render(mk), list(legacy))) for p, mk in apps])
    try:
        SUI.check_page(capps, prefix_ok)
        K.check(True, "%s: check_page (markup rules, parents, no duplicate id)" % what)
    except Exception as ex:
        K.check(False, "%s: check_page: %s" % (what, ex))
    try:
        SUI.check_sky_paths(apps, tab_icons=True)
        allp = [m.group(0) for mk in apps.markups() for m in SUI._SKY_PATH_RE.finditer(SUI.render(mk))]
        K.check(not [p for p in allp if p.startswith('"../')], "%s: no texture path leaves Common/UI/Custom (%d)" % (what, len(allp)))
    except Exception as ex:
        K.check(False, "%s: sky paths: %s" % (what, ex))
    ids = set()
    for _p, mk in apps:
        ids |= set(x.group(2) for x in H.DECL_RE.finditer(SUI.render(mk)))
    bs = [s for s, _t in ev]
    bad = [s for s, _d in sets if s.lstrip("#").split(".")[0] not in ids] + [s for s in bs if s.lstrip("#") not in ids]
    K.check(not bad, "%s: every b.set / binding names an element that exists (%d sets, %d bindings): %s" % (what, len(sets), len(bs), bad[:4]))
    try:
        info = SUI.assert_menu_page(apps, hub=hub, what=what, sets=sets, pager_ok=pager_ok)
        K.check(info["rows"] == 2 and info["subs"] == 1, "%s: assert_menu_page (1600 x 980, rows %d, sub rows %d, no back button, no pager)"
                % (what, info["rows"], info["subs"]))
    except Exception as ex:
        K.check(False, "%s: assert_menu_page: %s" % (what, ex))
    return pg, cm, ev, apps


def row2(cm, prefix):
    """row 2 as drawn: [(label, selected, tab id bound)]"""
    apps = apps_of(cm)
    out = []
    i = 0
    while True:
        bid = "%sBigT%d" % (prefix, i)
        btn = [mk for p, mk in apps if re.search(r"Button #%s \{" % bid, mk)]
        if not btn:
            break
        lab = [re.search(r'Text: "([^"]*)"', mk).group(1) for p, mk in apps if p == bid and mk.startswith("Label")]
        out.append((lab[0] if lab else None, "Tab_Selected" in btn[0]))
        i += 1
    return out


def subtabs(cm, prefix):
    """the sub-tab row as drawn: [(label after b.set, Primary?)] in order"""
    out = []
    for ty, s, t, d in cm:
        if t and s == "#%sSub" % prefix and t.startswith("TextButton"):
            m = re.match(r'TextButton #(\w+) \{', t)
            lab = re.search(r'Text: "([^"]*)"', t).group(1)
            bset = set_of(cm, "#%s.Text" % m.group(1))
            out.append((bset if bset is not None else lab, "Primary" in t))
    return out


def hub_defs(E):
    """what SkyyMenu publishes for row 1: hub:def:<hub> = Object[]{ title, command, icon item, default tab } for Home + every hub"""
    import jpype
    from jpype import JClass
    for h in SUI.HUB_ROW_IDS:
        t = "Home" if h == "home" else SUI.hub_title_now(h)
        cmd = "skymenu" if h == "home" else SUI.HUB_DEFS[h][1]
        E.br.put("hub:def:" + h, jpype.JArray(JClass("java.lang.Object"))([t, cmd, "Skyy_Menu", None]))


def cls_of(o):
    return None if o is None else str(o.getClass().getName())


def click(E, P, data):
    n0 = len(E.sent(P))
    P.pm.handleLegacyCustomPageEvent(P.ref, P.st, E.CPE(E.CPT.Data, data))
    E.pump(P)
    return P.pm.getCustomPage(), len(E.sent(P)) > n0


def same(a, b_):
    from jpype import JClass
    return a is not None and b_ is not None and int(JClass("java.lang.System").identityHashCode(a)) == int(JClass("java.lang.System").identityHashCode(b_))


# ------------------------------------------------------------------------------------------------------------------- HUB: the page alone
def run_hub(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    W = H.boot(scratch, jar, "hub")
    E = W.E
    J = lambda n: JClass(PKG + n)
    HB = J("HubBar")
    E.br = HB.map()
    home = os.path.join(scratch, "home_hub")
    bz_prep(E, J, home)
    C, M = J("Catalog"), J("Market")
    ids = [str(p.id) for p in C.all()]
    fake_items(E, ids)
    purse = {}
    fake_coins(E.br, purse)
    K.check(bool(J("Coins").ready()), "X: the fake SkyyCoins bridge is seen")
    TRUE = JClass("java.lang.Boolean").TRUE
    P, O = W.P, W.O
    u = P.pr.getUuid()
    purse[str(u)] = 10000000
    for X in (P, O):
        E.br.put("hub:last:" + str(X.pr.getUuid()), JClass("java.util.concurrent.ConcurrentHashMap")())
    # ---------------------------------------------------------------- REG
    K.eq(int(J("BzHubOpen").register()), 1, "REG: the Market tab is put")
    e = E.br.get("hub:tab:market:bazaar")
    K.check(e is not None and str(e[1]) == "Market" and int(e[2]) == 10 and str(e[3]) == "bazaar" and cls_of(e[4]) == PKG + "BzHubOpen",
            "REG: hub:tab:market:bazaar = {SkyyBazaar, Market, 10, bazaar, BzHubOpen}")
    # ---------------------------------------------------------------- PAGE (through the bar's open path)
    K.eq(str(HB.open(P.pr, u, "market", "bazaar")), "bridge", "PAGE: HubBar.open(market, bazaar) opens through the bridge Function")
    E.pump(P)
    pg = P.pm.getCustomPage()
    K.check(cls_of(pg) == PKG + "BzPage", "PAGE: the Bazaar page is open")
    pg, cm, ev, apps = built(K, E, P, "PAGE (no selection, no SkyyAuctions)")
    K.check(apps[0][1].startswith("Group #SkyyBzF { Anchor: (Width: 1600, Height: 980); }"), "PAGE: the root #SkyyBzF is 1600 x 980")
    K.check(any(t and "Group #SkyyBzFBigRow " in t for ty, s, t, d in cm) and any(t and "Group #SkyyBzFBigTabs " in t for ty, s, t, d in cm),
            "PAGE: row 1 (#SkyyBzFBigRow) + row 2 (#SkyyBzFBigTabs)")
    K.eq(row2(cm, "SkyyBzF"), [("Market", True)], "PAGE: row 2 = the Market hub's tabs (only Market loaded), Market selected")
    K.eq(subtabs(cm, "SkyyBzF"), [("Bazaar", True)], "PAGE: the ONE sub-tab row without SkyyAuctions = BAZAAR (selected)")
    K.check(str(set_of(cm, "#SkyyBzPurse.Text")).startswith("Purse  10000000 coins"), "PAGE: the purse sits in the sub-tab row (%s)" % set_of(cm, "#SkyyBzPurse.Text"))
    K.check(not any(t and ("SkyyBzPgPrev" in t or "SkyyBzPgNext" in t or "HubMenu" in t) for ty, s, t, d in cm), "PAGE: no pager, no < Menu")
    K.check(any(s == "#SkyyBzFHubClose" and "hub:close" in t for s, t in ev), "PAGE: the X = hub:close (%s)" % [x for x in ev if "Close" in x[0]][:2])
    K.check(not any("hub:h:" in t for s, t in ev), "PAGE: row 1 without SkyyMenu (no hub:def) = the hub title only, no buttons")
    # SkyyMenu's hub:def entries (Home + the 7 hubs): row 1 = Home + every hub, Market selected, each bound hub:h:<id>
    hub_defs(E)
    pg, cm, ev, apps = built(K, E, P, "PAGE (SkyyMenu's hub defs: row 1 drawn)")
    K.check(sum(1 for s, t in ev if "hub:h:" in t) == len(SUI.HUB_ROW_IDS), "PAGE: row 1 = Home + %d hubs, each bound hub:h:<id> (%s)"
            % (len(SUI.HUB_ROW_IDS) - 1, [t for s, t in ev if "hub:h:" in t][:3]))
    K.check(any(s == "#SkyyBzFBigT0" and "hub:bazaar" in t for s, t in ev), "PAGE: row 2 Market = hub:bazaar (%s)" % [x for x in ev if "BigT" in x[0]][:2])
    tabs = [t for ty, s, t, d in cm if t and s == "#SkyyBzTabs" and t.startswith("TextButton")]
    K.check(len(tabs) == len(list(pg.tabs)) and 1 <= len(tabs) <= 6 and "Primary" in tabs[0], "PAGE: the bag tabs are an in-page list (%d, the open one Primary)" % len(tabs))
    last = E.br.get("hub:last:" + str(u))
    K.check(last is not None and str(last.get("market")) == "bazaar", "PAGE: hub:last remembers market -> bazaar")
    K.check(str(set_of(cm, "#SkyyBzFSub0.Text") or "Bazaar") == "Bazaar" and not any(t and "#SkyyBzMkAh" in t for ty, s, t, d in cm),
            "PAGE: no 0.1.17 switch row any more (the sub-tabs are it)")
    # the full Market hub (Merchants registered): row 2 = Market + Merchants
    TRUEF = []

    @JImplements("java.util.function.Function")
    class Rec:
        def __init__(self, ans):
            self.calls, self.ans = [], ans

        @JOverride
        def apply(self, o):
            self.calls.append(str(o))
            return self.ans
    mrec = Rec(TRUE)
    E.br.put("hub:tab:market:merchants", jpype.JArray(JClass("java.lang.Object"))(["SkyyMerchants", "Merchants", JClass("java.lang.Integer")(30), "merchants", mrec, None]))
    pg, cm, ev, apps = built(K, E, P, "PAGE (full Market hub)")
    K.eq(row2(cm, "SkyyBzF"), [("Market", True), ("Merchants", False)], "PAGE: row 2 = Market (selected) + Merchants")
    # ---------------------------------------------------------------- CLICKS (rows 1 + 2, the X)
    mark = "#SkyyBzFTitle.Text"
    n0 = len(E.sent(P))
    p2, ok = click(E, P, '{"a":"hub:bazaar"}')
    K.check(same(p2, pg) and mark in E.strs_of(P, n0), "CLICK: row 2's own tab keeps the page and answers it")
    n0 = len(E.sent(P))
    p2, ok = click(E, P, '{"a":"hub:h:market"}')
    K.check(same(p2, pg) and mark in E.strs_of(P, n0), "CLICK: row 1's own hub (Market) keeps the page and answers it")
    n0 = len(E.sent(P))
    p2, ok = click(E, P, '{"a":"hub:merchants"}')
    K.check(mrec.calls == [str(u)] and same(p2, pg) and mark in E.strs_of(P, n0), "CLICK: Merchants opens through its Function (TRUE, no page) -> answered")
    p2, ok = click(E, P, '{"a":"hub:zzgone"}')
    K.check(same(p2, pg) and "could not open right now" in str(p2.info), "CLICK: a missing tab keeps the page and says so (%s)" % p2.info)
    # row 1: another hub (World, no tab registered -> its hub:def command runs as the player)
    E.CM.lines.clear()
    n0 = len(E.sent(P))
    p2, ok = click(E, P, '{"a":"hub:h:world"}')
    K.check("travel" in [str(x) for x in E.CM.lines] or len(E.sent(P)) > n0, "CLICK: row 1 World runs its hub command (%s)" % list(E.CM.lines))
    HB.open(P.pr, u, "market", "bazaar")
    E.pump(P)
    pg = P.pm.getCustomPage()
    for h in SUI.HUB_ROW_IDS:
        E.br.remove("hub:def:" + h)
    E.br.remove("config:def:SkyyMenu")
    p2, ok = click(E, P, '{"a":"hub:h:home"}')
    K.check(p2 is None, "CLICK: Home without SkyyMenu closes the page")
    HB.open(P.pr, u, "market", "bazaar")
    E.pump(P)
    pg = P.pm.getCustomPage()
    E.br.put("config:def:SkyyMenu", "x")
    E.CM.lines.clear()
    n0 = len(E.sent(P))
    p2, ok = click(E, P, '{"a":"hub:h:home"}')
    K.check("skymenu" in [str(x) for x in E.CM.lines] and same(p2, pg) and mark in E.strs_of(P, n0), "CLICK: Home with SkyyMenu runs /skymenu, the page is answered")
    E.br.remove("config:def:SkyyMenu")
    p2, ok = click(E, P, '{"a":"hub:close"}')
    K.check(p2 is None, "CLICK: the X closes the page")
    E.br.remove("hub:tab:market:merchants")
    # ---------------------------------------------------------------- FEATURES: tabs, the scroll list, rule 7, search, Show more
    HB.open(P.pr, u, "market", "bazaar")
    E.pump(P)
    pg = P.pm.getCustomPage()
    sizes = {}
    for i in range(len(list(pg.tabs))):
        p2, ok = click(E, P, '{"a":"tab:%d","@BzFind":"","@BzCf":""}' % i)
        K.check(ok and str(p2.cat) == str(p2.tabs[i]), "TAB %d: the bag tab click opens %s (answered)" % (i, p2.tabs[i]))
        p2, cm, ev, apps = built(K, E, P, "TAB %s" % p2.tabs[i])
        n = len(list(p2.cells))
        tot = len([q for q in C.inCat(p2.cat) if C.usable(q.id)])
        k = tier_of(n)
        cellmk = [t for ty, s, t, d in cm if t and t.startswith("Button #SkyyBzCell0 ")]
        K.check(n == min(tot, SHOW) and cellmk and ("Width: %d, Height: %d" % (CELLS[k], CELLS[k])) in cellmk[0],
                "TAB %s: ONE scroll list of %d cells (of %d), %d px cells (rule 7 tier %d)" % (p2.cat, n, tot, CELLS[k], k))
        rows = [t for ty, s, t, d in cm if t and s == "#SkyyBzGrid" and t.startswith("Group #SkyyBzRow")]
        K.eq(len(rows), (n + COLS[k] - 1) // COLS[k], "TAB %s: %d rows of %d" % (p2.cat, len(rows), COLS[k]))
        sizes[k] = sizes.get(k, 0) + 1
    K.notes.append("TAB: cell size tiers seen over the tabs: %s" % sizes)
    # every tier on real pages: a search narrows the list (1 cell = 148 px, 13+ = 107 px, 31+ = 74 px)
    for q, want in (("copper ore", None), ("ore", None), ("a", None)):
        p2, ok = click(E, P, json.dumps({"a": "find", "@BzFind": q, "@BzCf": ""}))
        p2, cm, ev, apps = built(K, E, P, "SEARCH '%s'" % q)
        n = len(list(p2.cells))
        total = len(list(p2.marketFind(q)))
        k = tier_of(n)
        cellmk = [t for ty, s, t, d in cm if t and t.startswith("Button #SkyyBzCell0 ")]
        K.check(n == min(total, SHOW) and (n == 0 or ("Width: %d, Height: %d" % (CELLS[k], CELLS[k])) in cellmk[0]),
                "SEARCH '%s': %d of %d cells, tier %d (%d px)" % (q, n, total, k, CELLS[k]))
        if total > SHOW:
            K.check(any(t and "#SkyyBzMore " in t for ty, s, t, d in cm) and str(set_of(cm, "#SkyyBzCount.Text")) == "showing %d of %d" % (SHOW, total),
                    "SEARCH '%s': a Show more row + 'showing %d of %d'" % (q, SHOW, total))
            p3, ok = click(E, P, json.dumps({"a": "more", "@BzFind": q, "@BzCf": ""}))
            p3, cm3, ev3, apps3 = built(K, E, P, "SEARCH '%s' (Show more)" % q)
            K.check(ok and len(list(p3.cells)) == min(total, 2 * SHOW), "SEARCH '%s': Show more -> %d cells" % (q, len(list(p3.cells))))
    p2, ok = click(E, P, json.dumps({"a": "find", "@BzFind": "zzqqxx", "@BzCf": ""}))
    p2, cm, ev, apps = built(K, E, P, "SEARCH no match")
    K.check(len(list(p2.cells)) == 0 and str(set_of(cm, "#SkyyBzEmpty.Text")).startswith("No matches"), "SEARCH: no match = the empty-state line in the list")
    p2, ok = click(E, P, json.dumps({"a": "fclear", "@BzFind": "zzqqxx", "@BzCf": ""}))
    K.check(ok and str(p2.query) == "" and int(p2.showN) == 0, "SEARCH: Clear goes back to the tab, the list starts again")
    p2, ok = click(E, P, '{"a":"prev"}')
    K.check(ok is not None, "OLD: a stale prev click (0.1.17 pager) is harmless")
    p2, ok = click(E, P, json.dumps({"a": "mk:bz", "@BzFind": "", "@BzCf": ""}))
    K.check(ok and cls_of(p2) == PKG + "BzPage", "SUB: BAZAAR (this sub-view) is answered in place")
    p2, ok = click(E, P, json.dumps({"a": "mk:create", "@BzFind": "", "@BzCf": ""}))
    K.check(ok and "not on this server" in str(p2.info), "SUB: CREATE BIN without SkyyAuctions says so (%s)" % p2.info)
    # ---------------------------------------------------------------- BUY / SELL smoke (real inventories, the fake coin bridge)
    pg = P.pm.getCustomPage()
    cheap = [i for i in ids if C.usable(i) and 0 < int(M.quote(i, 1, True)) < 500 and int(J("Trader").stack(i)) > 1]
    dear = [i for i in ids if C.usable(i) and int(M.quote(i, 1, True)) >= 3000 and int(M.quote(i, 1, True)) < 1000000]
    K.check(cheap and dear, "SMOKE: products to trade (%d cheap, %d dear)" % (len(cheap), len(dear)))
    c0 = cheap[0]
    pg.sel = c0
    pg.cat = C.get(c0).cat
    pg, cm, ev, apps = built(K, E, P, "PRODUCT %s selected" % c0)
    K.check(any(t and "#SkyyBzBuy1 " in t for ty, s, t, d in cm) and any(t and "#SkyyBzSellAll " in t for ty, s, t, d in cm)
            and any(t and "#SkyyBzAmtBox " in t for ty, s, t, d in cm) and set_of(cm, "#SkyyBzDName.Text") == str(C.get(c0).name),
            "PRODUCT: the detail well has the name, Buy / Sell buttons and the custom amount")
    cnt = lambda i: int(E.count(P, i))
    q1, p0, n0 = int(M.quote(c0, 1, True)), purse[str(u)], cnt(c0)
    p2, ok = click(E, P, json.dumps({"a": "buy1", "@BzFind": "", "@BzCf": "", "@BzAmount": ""}))
    K.check(ok and cnt(c0) == n0 + 1 and purse[str(u)] == p0 - q1 and str(p2.info).startswith("bought"), "SMOKE: Buy 1 %s: +1 item, -%d coins (%s)" % (c0, q1, p2.info))
    stk = int(J("Trader").stack(c0))
    qs, p0, n0 = int(M.quote(c0, stk, True)), purse[str(u)], cnt(c0)
    p2, ok = click(E, P, json.dumps({"a": "buystk", "@BzFind": "", "@BzCf": "", "@BzAmount": ""}))
    if qs >= 3000:
        p2, ok = click(E, P, json.dumps({"a": "buystk", "@BzFind": "", "@BzCf": "", "@BzAmount": ""}))
    K.check(cnt(c0) == n0 + stk and purse[str(u)] == p0 - qs, "SMOKE: Buy %d %s: +%d items, -%d coins (%s)" % (stk, c0, stk, qs, p2.info))
    s1, p0, n0 = int(M.quote(c0, 1, False)), purse[str(u)], cnt(c0)
    p2, ok = click(E, P, json.dumps({"a": "sell1", "@BzFind": "", "@BzCf": "", "@BzAmount": ""}))
    K.check(ok and cnt(c0) == n0 - 1 and purse[str(u)] == p0 + s1 and str(p2.info).startswith("sold"), "SMOKE: Sell 1: -1 item, +%d coins (%s)" % (s1, p2.info))
    built(K, E, P, "PRODUCT after trades")
    # the CONFIRM flow on a dear product: the gold CONFIRM button inside the page pattern, the 2nd click buys
    d0 = dear[0]
    pg = P.pm.getCustomPage()
    pg.sel = d0
    pg.disarm()
    qd, p0, n0 = int(M.quote(d0, 1, True)), purse[str(u)], cnt(d0)
    pg.cfShown = 0
    p2, ok = click(E, P, json.dumps({"a": "buy1", "@BzFind": "", "@BzCf": "", "@BzAmount": ""}))
    K.check(ok and cnt(d0) == n0 and str(p2.cfAct) == "buy1", "CONFIRM: a %d-coin Buy 1 arms first (%s)" % (qd, p2.info))
    p2, cm, ev, apps = built(K, E, P, "PRODUCT CONFIRM armed")
    K.check(str(set_of(cm, "#SkyyBzBuy1.Text") or "") == "" and any(t and "#SkyyBzBuy1 " in t and ("CONFIRM - %d coins" % qd) in t and SUI.COLOR["gold"] in t
                                                                   for ty, s, t, d in cm), "CONFIRM: the gold 'CONFIRM - %d coins' Buy 1" % qd)
    p2.cfShown = 0
    p2, ok = click(E, P, json.dumps({"a": "buy1", "@BzFind": "", "@BzCf": "", "@BzAmount": ""}))
    K.check(cnt(d0) == n0 + 1 and purse[str(u)] == p0 - qd, "CONFIRM: the second click buys (%s)" % p2.info)
    # Sell all tabs -> the gold Confirm sell (the left column), then a click elsewhere turns it back
    p2, ok = click(E, P, json.dumps({"a": "sellalltabs", "@BzFind": "", "@BzCf": "", "@BzAmount": ""}))
    p2, cm, ev, apps = built(K, E, P, "SELL ALL TABS armed")
    K.check(any(t and "#SkyyBzSellAllTabs " in t and "Confirm sell" in t for ty, s, t, d in cm), "SELL ALL TABS: the gold Confirm sell (%s)" % p2.info)
    p2, ok = click(E, P, json.dumps({"a": "tab:0", "@BzFind": "", "@BzCf": "", "@BzAmount": ""}))
    K.check(ok and int(p2.confirmUntil) == 0, "SELL ALL TABS: another click disarms it")
    p2, ok = click(E, P, json.dumps({"a": "cfset", "@BzFind": "", "@BzCf": "5000", "@BzAmount": ""}))
    K.check(ok and int(J("BzConfirm").get(u)) == 5000, "CONFIRM amount: Set (left column) saves 5000")
    # ---------------------------------------------------------------- DROP
    K.eq(int(HB.removeAll()), 1, "DROP: removeAll removed our tab")
    K.save()


# ------------------------------------------------------------------------------------------------------------------- MK: both jars
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
    P, O = W.P, W.O
    u = P.pr.getUuid()
    for X in (P, O):
        E.br.put("hub:last:" + str(X.pr.getUuid()), JClass("java.util.concurrent.ConcurrentHashMap")())
    M = JB("BzMarket")
    # ---------------------------------------------------------------- registry: Market shown, Auctions hidden while merged
    K.eq(int(JB("BzHubOpen").register()), 1, "MK REG: the Bazaar puts its tab")
    K.eq(int(JA("AhHubOpen").register()), 1, "MK REG: the Auction House puts its tab")
    K.eq([str(x[0]) for x in HBB.tabs("market", u)], ["bazaar", "auctions"], "MK VIS: without bazaar:fn:open (an older Bazaar) the Auctions tab shows")
    E.br.put("bazaar:fn:open", JB("BzOpenFn")())
    K.eq([str(x[0]) for x in HBB.tabs("market", u)], ["bazaar"], "MK VIS: with the merged Bazaar the hub bar shows ONE tab (Market)")
    K.check(str(JA("AhPage").myTab()) == "bazaar" and bool(JA("AhPage").merged()), "MK: the AH page's active tab is the Market tab")
    K.check(not bool(M.ahOn()) and not bool(M.ahViewOn()), "MK: ahOn / ahViewOn false before SkyyAuctions publishes its Functions")
    E.br.put("ah:fn:find", JA("AhMarketFn")(0))
    E.br.put("ah:fn:open", JA("AhMarketFn")(1))
    K.check(bool(M.ahOn()) and not bool(M.ahViewOn()), "MK: an AH 0.1.9 (find + open only): ahOn, no ahViewOn")
    # the Bazaar page with an AH 0.1.9: BAZAAR | AUCTION HOUSE
    K.eq(str(HBB.open(P.pr, u, "market", "bazaar")), "bridge", "MK: the Market tab opens the Bazaar page")
    E.pump(P)
    pg, cm, ev, apps = built(K, E, P, "MK Bazaar (AH 0.1.9)")
    K.eq(subtabs(cm, "SkyyBzF"), [("Bazaar", True), ("Auction House", False)], "MK: with an AH 0.1.9 the sub-tabs are BAZAAR | AUCTION HOUSE")
    E.br.put("ah:fn:view", JA("AhMarketFn")(2))
    K.check(bool(M.ahViewOn()), "MK: ah:fn:view published (SkyyAuctions 0.1.10)")
    pg, cm, ev, apps = built(K, E, P, "MK Bazaar (AH 0.1.10)")
    K.eq(subtabs(cm, "SkyyBzF"), [("Bazaar", True), ("Auction House", False), ("Create BIN", False), ("Manage", False)],
         "MK: the four sub-tabs BAZAAR (selected) | AUCTION HOUSE | CREATE BIN | MANAGE")
    K.eq(row2(cm, "SkyyBzF"), [("Market", True)], "MK: row 2 = ONE tab, Market, selected")
    for i_, a_ in ((1, "mk:ah"), (2, "mk:create"), (3, "mk:manage")):
        K.check(any(s == "#SkyyBzFSub%d" % i_ and a_ in t and "@BzFind" in t for s, t in ev), "MK: sub-tab %d is bound to %s (the search text comes along)" % (i_, a_))
    # ah:fn:view: junk, the count, the views
    view = E.br.get("ah:fn:view")
    K.check(view.apply("x") == FALSE and view.apply(jpype.JArray(JClass("java.lang.Object"))([u, "nope"])) == FALSE
            and view.apply(jpype.JArray(JClass("java.lang.Object"))([JClass("java.util.UUID").randomUUID(), "manage"])) == FALSE,
            "MK ah:fn:view: junk / an unknown view / an offline player = FALSE")
    K.check(int(view.apply(u)) == 0, "MK ah:fn:view: a UUID = the claims waiting (0)")
    p2, ok = click(E, P, json.dumps({"a": "mk:create", "@BzFind": "", "@BzCf": ""}))
    K.check(cls_of(p2) == APKG + "AhPage" and str(p2.view) == "create", "MK: CREATE BIN opens the Auction House on Create BIN (%s %s)" % (cls_of(p2), None if p2 is None else p2.view))
    K.check(str(HBB.open(P.pr, u, "market", "bazaar")) == "bridge", "MK: back to the Bazaar")
    E.pump(P)
    p2, ok = click(E, P, json.dumps({"a": "mk:manage", "@BzFind": "", "@BzCf": ""}))
    K.check(cls_of(p2) == APKG + "AhPage" and str(p2.view) == "manage", "MK: MANAGE opens the Auction House on Manage")
    # ---------------------------------------------------------------- listings + the one search (0.1.17 paths)
    now = int(JClass("java.lang.System").currentTimeMillis())
    Rec, Sto = JA("AhRec"), JA("AhStore")
    rows = [(1, "Ore_Iron", 10, 500, 3600000, "Iron Ore", "Ann"), (2, "Ore_Iron", 5, 250, 600000, "Iron Ore", "Bob"),
            (3, "Ingredient_Bar_Iron", 1, 120, 7200000, "Iron Bar", "Cid"), (4, "Weapon_Sword_Iron", 1, 900, 86400000, "Iron Sword", "Dee"),
            (5, "Ore_Iron", 1, 1, -5000, "Iron Ore", "Old"), (6, "Ore_Copper", 4, 40, 3600000, "Copper Ore", "Eve"),
            (7, "Ore_Iron", 2, 100, 1800000, "Iron Ore", "Fay")]
    for i, it, q, pr_, ends, nm, sel in rows:
        Sto.livePut(str(i), Rec.parse(rec_json(i, it, q, pr_, ends, now, nm, sel)))
    find = E.br.get("ah:fn:find")
    by = dict((str(x[0]), x) for x in find.apply("iron"))
    K.eq(sorted(by), ["Ingredient_Bar_Iron", "Ore_Iron", "Weapon_Sword_Iron"], "MK find: 'iron' = one row per item id (ah:fn:find unchanged)")
    HBB.open(P.pr, u, "market", "bazaar")
    E.pump(P)
    p2, ok = click(E, P, json.dumps({"a": "find", "@BzFind": "iron", "@BzCf": ""}))
    pg1, cm1, ev1, apps1 = built(K, E, P, "MK Bazaar search 'iron' (both markets)")
    order = []
    for k in range(len(list(pg1.cells))):
        cid = pg1.cells[k] if pg1.cells[k] is not None else pg1.ahCells[k]
        if cid is not None:
            order.append((str(cid), "bz" if pg1.cells[k] is not None else "ah"))
    K.check(("Ore_Iron", "ah") in order and ("Ore_Iron", "bz") in order and order.index(("Ore_Iron", "bz")) + 1 == order.index(("Ore_Iron", "ah")),
            "MK search: the AH items in the one scroll list, the Bazaar product right before its AH cell")
    ia = [k for k in range(len(order)) if order[k] == ("Ore_Iron", "ah")][0]
    K.eq(set_of(cm1, "#SkyyBzCell%dQty.Text" % ia), "AH 3", "MK search: the AH cell's corner says AH 3")
    K.check(str(set_of(cm1, "#SkyyBzSub.Text")).endswith("Bazaar + %d Auction House" % len([o for o in order if o[1] == "ah"])), "MK search: the header")
    p2, ok = click(E, P, json.dumps({"a": "cell:%d" % ia, "@BzFind": "iron", "@BzCf": ""}))
    pg2, cm2, ev2, apps2 = built(K, E, P, "MK Bazaar (an AH cell selected)")
    K.check(str(pg2.ahSel) == "Ore_Iron" and pg2.sel is None and any(t and "#SkyyBzAhOpen " in t for ty, s, t, d in cm2)
            and not any(t and re.search(r"#SkyyBz(Buy1|BuyStk|Sell1|SellStk|SellAll|ABuy|ASell) ", t) for ty, s, t, d in cm2),
            "MK cell: the AH detail + OPEN IN AUCTION HOUSE, no Bazaar trade button")
    pa, ok = click(E, P, json.dumps({"a": "ahopen", "@BzFind": "iron", "@BzCf": ""}))
    K.check(cls_of(pa) == APKG + "AhPage" and str(pa.view) == "browse" and str(pa.query) == "Ore_Iron", "MK OPEN: the AH page on Browse filtered to Ore_Iron")
    ah_views(K, E, P, JA, "MK", merged=True)
    # the AH page's BAZAAR with a typed search -> the Bazaar page with that search
    pa = P.pm.getCustomPage()
    if str(pa.view) != "browse":
        pa.view = "browse"
    pb, ok = click(E, P, '{"a":"mk:bz","@AhSearch":"sword"}')
    K.check(cls_of(pb) == PKG + "BzPage" and str(pb.query) == "sword", "MK BAZAAR: the Bazaar page opens with the AH search (%s)" % (None if pb is None else pb.query))
    pc, ok = click(E, P, json.dumps({"a": "mk:ah", "@BzFind": "sword", "@BzCf": ""}))
    K.check(cls_of(pc) == APKG + "AhPage" and str(pc.query) == "sword", "MK AUCTION HOUSE: the AH page opens with the Bazaar search")
    # Manage (n): a listing of P sold -> the coins wait -> both pages say Manage (1)
    key = str(JA("AhUtil").pkey(u))
    Sto.livePut("50", Rec.parse(rec_json(50, "Ore_Copper", 1, 77, 3600000, now, "Copper Ore", "SkyyPlain", seller_uuid=str(u), seller_key=key)))
    E.br.remove("ah:fn:open")       # (keep the AH 0.1.10 buy path honest: buy through AhStore as the page does)
    E.br.put("ah:fn:open", JA("AhMarketFn")(1))
    purse = {}
    fake_coins(E.br, purse)
    purse[str(O.pr.getUuid())] = 10000
    r = Sto.buy(None, O.pr.getUuid(), str(JA("AhUtil").pkey(O.pr.getUuid())), "SkyyOp", "", "50", 77)
    K.check(bool(r.ok), "MK Manage (n): the other player bought P's listing #50 (%s)" % r.msg)
    owed = int(view.apply(u))
    K.check(owed >= 1, "MK ah:fn:view: P has %d claim(s) waiting" % owed)
    HBB.open(P.pr, u, "market", "bazaar")
    E.pump(P)
    pg, cm, ev, apps = built(K, E, P, "MK Bazaar (claims waiting)")
    K.eq(subtabs(cm, "SkyyBzF")[3], ("Manage (%d)" % owed, False), "MK: the Bazaar's MANAGE sub-tab says Manage (%d)" % owed)
    pm, ok = click(E, P, json.dumps({"a": "mk:manage", "@BzFind": "", "@BzCf": ""}))
    pm, cmm, evm, appsm = built(K, E, P, "MK AH Manage (claims waiting)", legacy=AH_LEGACY)
    K.eq(subtabs(cmm, "SkyyAhF")[3], ("Manage (%d)" % owed, True), "MK: the AH page's MANAGE sub-tab says the same, selected")
    # without SkyyAuctions: the Bazaar page has BAZAAR only
    for k_ in ("ah:fn:find", "ah:fn:open", "ah:fn:view"):
        E.br.remove(k_)
    HBB.open(P.pr, u, "market", "bazaar")
    E.pump(P)
    pe, cme, eve, appse = built(K, E, P, "MK Bazaar (no AH)")
    K.eq(subtabs(cme, "SkyyBzF"), [("Bazaar", True)], "MK no AH: BAZAAR only")
    K.save()


AH_LEGACY = ()


def ah_views(K, E, P, JA, tag, merged):
    """every Auction House view through built() (assert_menu_page on the REAL page): Browse, an item, Create BIN, Manage; the sub-tabs;
    the item page has no back button and AUCTION HOUSE / the Market tab lead back to the list"""
    want0 = [("Bazaar", False)] if merged else []
    pa = P.pm.getCustomPage()
    pa.view = "browse"
    pa, cm, ev, apps = built(K, E, P, "%s AH Browse" % tag, legacy=AH_LEGACY)
    st = subtabs(cm, "SkyyAhF")
    K.eq([x[0].split(" (")[0] for x in st], [x[0] for x in want0] + ["Auction House", "Create BIN", "Manage"], "%s AH: the sub-tabs" % tag)
    K.check([x[1] for x in st] == [False] * len(want0) + [True, False, False], "%s AH Browse: AUCTION HOUSE is the selected sub-tab" % tag)
    K.eq(row2(cm, "SkyyAhF"), [("Market", True)] if merged else [("Auctions", True)], "%s AH: row 2 (the Market tab selected)" % tag)
    K.check(any(t and "#SkyyAhClose " in t for ty, s, t, d in cm) and not any(t and ("SkyyAhPrev" in t or "SkyyAhNext" in t) for ty, s, t, d in cm),
            "%s AH Browse: Close in the footer, no pager" % tag)
    if len(list(pa.rowIds)) > 0:
        p2, ok = click(E, P, '{"a":"view:0","@AhSearch":"%s"}' % (pa.query or ""))
        p2, cm2, ev2, apps2 = built(K, E, P, "%s AH item" % tag, legacy=AH_LEGACY)
        K.check(str(p2.view) == "item" and not any(t and "SkyyAhDBack" in t for ty, s, t, d in cm2), "%s AH item: the item page has no back button" % tag)
        K.check(subtabs(cm2, "SkyyAhF")[len(want0)][1], "%s AH item: AUCTION HOUSE stays selected on an item's page" % tag)
        own = "bazaar" if merged else "auctions"
        p3, ok = click(E, P, '{"a":"hub:%s"}' % own)
        K.check(ok and str(p3.view) == "browse", "%s AH item: the Market tab in row 2 leads back to the list" % tag)
        p3, ok = click(E, P, '{"a":"view:0"}')
        p3, ok = click(E, P, '{"a":"nav:browse"}')
        K.check(ok and str(p3.view) == "browse", "%s AH item: AUCTION HOUSE (the sub-tab) leads back to the list" % tag)
    for v in ("create", "manage"):
        p4, ok = click(E, P, '{"a":"nav:%s"}' % v)
        p4, cm4, ev4, apps4 = built(K, E, P, "%s AH %s" % (tag, v), legacy=AH_LEGACY)
        K.check(str(p4.view) == v and [x[1] for x in subtabs(cm4, "SkyyAhF")] == [False] * len(want0) + [False, v == "create", v == "manage"],
                "%s AH %s: its sub-tab selected" % (tag, v))
    p5, ok = click(E, P, '{"a":"nav:browse"}')


# ------------------------------------------------------------------------------------------------------------------- D: live
def run_live2(out, jar, scratch, home):
    """two starts on the scratch copy (the second writes nothing), the merged page built (assert_menu_page), searched, switched"""
    from jpype import JClass
    K = HK.Child(out)
    if not os.path.isfile(AH_JAR):
        K.check(False, "D: SkyyAuctions 0.1.10 jar missing (%s)" % AH_JAR)
        K.save()
        return
    ah_home = os.path.join(scratch, "live_ah", "Skyy_SkyyAuctions")
    src = os.path.join(LIVE_SAVES, "Skyy_SkyyAuctions")
    K.check(os.path.isdir(src), "D: the live Skyy_SkyyAuctions exists")
    shutil.copytree(src, ah_home)
    W = boot2(scratch, [jar, AH_JAR], "live")
    E = W.E
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
    P = W.P
    u = P.pr.getUuid()
    E.br.put("hub:last:" + str(u), JClass("java.util.concurrent.ConcurrentHashMap")())
    for start in (1, 2):
        JB("BzHubOpen").register()
        JA("AhHubOpen").register()
        E.br.put("bazaar:fn:open", JB("BzOpenFn")())
        E.br.put("ah:fn:find", JA("AhMarketFn")(0))
        E.br.put("ah:fn:open", JA("AhMarketFn")(1))
        E.br.put("ah:fn:view", JA("AhMarketFn")(2))
        K.eq(str(JB("HubBar").open(P.pr, u, "market", "bazaar")), "bridge", "D%d: Market opens" % start)
        E.pump(P)
        built(K, E, P, "D%d Bazaar (live)" % start)
        click(E, P, json.dumps({"a": "find", "@BzFind": "iron", "@BzCf": ""}))
        pg_, cm, ev, apps = built(K, E, P, "D%d Bazaar search (live)" % start)
        K.check(str(pg_.query) == "iron", "D%d: the live search (%s)" % (start, set_of(cm, "#SkyyBzSub.Text")))
        pa, ok = click(E, P, json.dumps({"a": "mk:ah", "@BzFind": "iron", "@BzCf": ""}))
        K.check(cls_of(pa) == APKG + "AhPage" and str(pa.query) == "iron", "D%d: AUCTION HOUSE opens the live AH page with the search" % start)
        ah_views(K, E, P, JA, "D%d" % start, merged=True)
        pb, ok = click(E, P, '{"a":"mk:bz","@AhSearch":"iron"}')
        K.check(cls_of(pb) == PKG + "BzPage", "D%d: BAZAAR opens the Bazaar page again" % start)
        click(E, P, '{"a":"hub:close"}')
        JB("HubBar").removeAll()
        JA("HubBar").removeAll()
        for k in ("bazaar:fn:open", "ah:fn:find", "ah:fn:open", "ah:fn:view"):
            E.br.remove(k)
        K.eq((HK.tree_hash(home), HK.tree_hash(ah_home)), (h0, a0), "D%d: no file written in either live copy" % start)
    K.save()


# ------------------------------------------------------------------------------------------------------------------- 0.1.19 helpers
ETER_ID = "Plant_Seeds_Wheat_Eternal"
REASON = "Wheat Seed Bag (Eternal) unlocks at Wheat collection IV (120 / 500)"
LOADING = "Collections are still loading - try again in a moment"
PREMIUM_MAX = 22          # = the build's PREMIUM_MAX (Server Setup row processed.premium, max)
NEW0119 = [i for i in [EN.PREFIX + t[0] for t in EN.TABLE] if i not in [EN.PREFIX + t[0] for t in EN.TABLE_20]]


def eter_fn(st):
    """a stand-in SkyyCollections 0.2.24 coll:fn:eternal: st["mode"] = a String (the answer), None (null) or "throw"; every call recorded"""
    from jpype import JImplements, JOverride, JClass, JString

    @JImplements("java.util.function.Function")
    class EF:
        @JOverride
        def apply(self, o):
            st["calls"].append((str(o[0]), str(o[1])))
            m = st["mode"]
            if m == "throw":
                raise JClass("java.lang.IllegalStateException")("stand-in failure")
            if m is None:
                return None
            if isinstance(m, int):
                return JClass("java.lang.Integer").valueOf(m)
            return JString(m)
    return EF()


def set_jars():
    """[(mod, version, jar)] of the tools/deploy_set.py SET (a literal, never imported) + a built SkyyCollections 0.2.24 when present"""
    t = ast.parse(open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf8").read())
    for n in t.body:
        if isinstance(n, ast.Assign) and any(getattr(x, "id", "") == "SET" for x in n.targets):
            out = [(m, v, os.path.join(ROOT, m, "%s-%s.jar" % (m, v))) for m, v in ast.literal_eval(n.value) if m != "SkyyBazaar"]
            c24 = os.path.join(ROOT, "SkyyCollections", "SkyyCollections-0.2.24.jar")
            if os.path.isfile(c24):
                out.append(("SkyyCollections", "0.2.24", c24))
            return [x for x in out if os.path.isfile(x[2])]
    return []


# ------------------------------------------------------------------------------------------------------------------- ETER: the lock
def run_eter(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    W = H.boot(scratch, jar, "eter")
    E = W.E
    J = lambda n: JClass(PKG + n)
    HB = J("HubBar")
    E.br = HB.map()
    home = os.path.join(scratch, "home_eter")
    bz_prep(E, J, home)
    C, M, T, CF = J("Catalog"), J("Market"), J("Trader"), J("BzConfirm")
    ids = [str(p.id) for p in C.all()]
    fake_items(E, ids)
    purse = {}
    fake_coins(E.br, purse)
    P = W.P
    u = P.pr.getUuid()
    purse[str(u)] = 100000000
    E.br.put("hub:last:" + str(u), JClass("java.util.concurrent.ConcurrentHashMap")())
    J("BzHubOpen").register()
    K.check(C.get(ETER_ID) is not None and bool(C.usable(ETER_ID)), "ETER: %s is a product" % ETER_ID)
    HB.open(P.pr, u, "market", "bazaar")
    E.pump(P)
    pg = P.pm.getCustomPage()
    st = {"mode": REASON, "calls": []}
    E.br.put("coll:fn:eternal", eter_fn(st))
    cnt = lambda i=ETER_ID: int(E.count(P, i))
    state = lambda: (purse[str(u)], cnt())

    def sel(i):
        pg_ = P.pm.getCustomPage()
        pg_.sel = i
        pg_.cat = C.get(i).cat
        pg_.disarm()
        pg_.cfShown = 0
        pg_.cfAct = None
        return pg_

    def act(a, amt=""):
        pg_ = P.pm.getCustomPage()
        pg_.cfShown = 0
        return click(E, P, json.dumps({"a": a, "@BzFind": "", "@BzCf": "", "@BzAmount": amt}))
    # ---------------------------------------------------------------- LOCKED: every buy path refuses before any coin / item moves
    CF.set(u, 1000000000)                       # a confirm amount no buy reaches = Buy 1 / stack go straight to buy0
    sel(ETER_ID)
    s0 = state()
    for a in ("buy1", "buystk"):
        p2, ok = act(a)
        K.check(state() == s0 and str(p2.info) == REASON, "ETER locked: %s refused, purse + inventory unchanged, the reason shown (%s)" % (a, p2.info))
    p2, ok = act("amt", "5")
    K.check(state() == s0 and REASON in str(p2.info) and int(p2.armBuy) <= 0, "ETER locked: the custom amount is not priced to buy (%s)" % p2.info)
    p2, ok = act("abuy", "5")
    K.check(state() == s0 and REASON in str(p2.info), "ETER locked: the custom amount Buy refused (%s)" % p2.info)
    CF.set(u, 0)                                # every buy asks CONFIRM: a locked seed is never armed
    sel(ETER_ID)
    p2, ok = act("buy1")
    K.check(state() == s0 and str(p2.info) == REASON and (p2.cfAct is None or str(p2.cfAct) == ""), "ETER locked: no CONFIRM armed (%s / %s)" % (p2.cfAct, p2.info))
    # the CONFIRM armed while it was still allowed, then locked before the second click
    st["mode"] = ""
    sel(ETER_ID)
    p2, ok = act("buy1")
    K.check(state() == s0 and str(p2.cfAct) == "buy1", "ETER: unlocked + every buy asks -> Buy 1 arms the CONFIRM (%s)" % p2.info)
    st["mode"] = REASON
    p2, ok = act("buy1")
    K.check(state() == s0 and str(p2.info) == REASON, "ETER locked: the armed CONFIRM click is refused, nothing moved (%s)" % p2.info)
    st["mode"] = ""
    sel(ETER_ID)
    p2, ok = act("amt", "3")
    st["mode"] = REASON
    p2, ok = act("abuy", "3")
    K.check(state() == s0 and REASON in str(p2.info), "ETER locked: an armed custom amount Buy is refused (%s)" % p2.info)
    # the trade core itself (every page path ends in buy0)
    pl = P.pl
    for nm, f in (("buy0", lambda: T.buy0(pl, u, "SkyyPlain", ETER_ID, 1)), ("buy", lambda: T.buy(pl, u, "SkyyPlain", ETER_ID, 1)),
                  ("buyC", lambda: T.buyC(pl, u, "SkyyPlain", ETER_ID, 1, 1000000000)), ("buyN", lambda: T.buyN(pl, u, "SkyyPlain", ETER_ID, 1, 1000000000))):
        r = f()
        K.check(not bool(r.ok) and str(r.msg) == REASON and state() == s0, "ETER locked: Trader.%s refused (%s)" % (nm, r.msg))
    K.check(st["calls"] and all(c == (str(u), ETER_ID) for c in st["calls"]), "ETER: coll:fn:eternal gets Object[]{ UUID, itemId } (%d calls)" % len(st["calls"]))
    # a normal seed never asks
    n_calls = len(st["calls"])
    CF.set(u, 1000000000)
    sel("Plant_Seeds_Wheat")
    q0, n0 = purse[str(u)], cnt("Plant_Seeds_Wheat")
    p2, ok = act("buy1")
    K.check(cnt("Plant_Seeds_Wheat") == n0 + 1 and purse[str(u)] < q0 and len(st["calls"]) == n_calls, "ETER: a normal seed buys and never asks (%s)" % p2.info)
    # ---------------------------------------------------------------- "" -> buys
    st["mode"] = ""
    sel(ETER_ID)
    q1 = int(M.quote(ETER_ID, 1, True))
    s1 = state()
    p2, ok = act("buy1")
    K.check(state() == (s1[0] - q1, s1[1] + 1) and str(p2.info).startswith("bought"), "ETER \"\": Buy 1 buys (-%d coins, +1) (%s)" % (q1, p2.info))
    p2, ok = act("amt", "2")
    p2, ok = act("abuy", "2")
    K.check(state()[1] == s1[1] + 3, "ETER \"\": the custom amount Buy 2 buys (%s)" % p2.info)
    # ---------------------------------------------------------------- selling while locked
    st["mode"] = REASON
    n_calls = len(st["calls"])
    sv, s2 = int(M.quote(ETER_ID, 1, False)), state()
    p2, ok = act("sell1")
    K.check(state() == (s2[0] + sv, s2[1] - 1) and str(p2.info).startswith("sold") and len(st["calls"]) == n_calls,
            "ETER locked: Sell 1 still sells (+%d coins) and never asks (%s)" % (sv, p2.info))
    # ---------------------------------------------------------------- null -> loading
    st["mode"] = None
    s3 = state()
    p2, ok = act("buy1")
    K.check(state() == s3 and str(p2.info) == LOADING, "ETER null: refused with the loading text (%s)" % p2.info)
    # ---------------------------------------------------------------- absent -> buys
    E.br.remove("coll:fn:eternal")
    s4 = state()
    p2, ok = act("buy1")
    K.check(state()[1] == s4[1] + 1 and str(p2.info).startswith("bought"), "ETER absent (SkyyCollections < 0.2.24): buys (%s)" % p2.info)
    # ---------------------------------------------------------------- a throwing Function -> refused, one WARN a minute
    E.br.put("coll:fn:eternal", eter_fn(st))
    st["mode"] = "throw"
    T.ETER_WARN = 0
    s5 = state()
    p2, ok = act("buy1")
    w1 = int(T.ETER_WARN)
    K.check(state() == s5 and "failed" in str(p2.info) and w1 > 0, "ETER throw: refused, warned (%s)" % p2.info)
    p2, ok = act("buy1")
    K.check(state() == s5 and int(T.ETER_WARN) == w1, "ETER throw: the second failure within a minute does not warn again")
    st["mode"] = 12345
    K.check(str(T.eterWhy(u, ETER_ID)) == "the Collections unlock check gave no answer - nothing bought, try again in a moment", "ETER: a non-String answer refuses")
    st["mode"] = REASON
    built(K, E, P, "ETER page with a locked seed selected")
    E.br.remove("coll:fn:eternal")
    K.save()


# ------------------------------------------------------------------------------------------------------------------- PRICE
def run_price(out, jar, scratch, _home):
    from jpype import JClass
    import jpype
    K = HK.Child(out)
    W = H.boot(scratch, jar, "price")
    E = W.E
    J = lambda n: JClass(PKG + n)
    E.br = J("HubBar").map()
    home = os.path.join(scratch, "home_price")
    bz_prep(E, J, home)
    C, M = J("Catalog"), J("Market")
    fake_items(E, [str(p.id) for p in C.all()])
    ench = [str(p.id) for p in C.all() if str(p.id).startswith(EN.PREFIX)]
    off = [EN.PREFIX + t[0] for t in EN.TABLE if EN.PREFIX + t[0] not in ench]
    K.eq(len(ench) + len(off), 102, "PRICE: %d Enchanted products listed, %d left off (%s)" % (len(ench), len(off), ", ".join(off)))
    K.check("Skyy_Ench_LifeEssence" not in ench and C.get("Ingredient_Life_Essence_Concentrated") is not None,
            "PRICE: the retired Enchanted Essence of Life is not listed; the vanilla Greater Essence of Life is")
    K.eq(sorted(i for i in ench if i not in [EN.PREFIX + t[0] for t in EN.TABLE_20]), sorted(i for i in NEW0119 if i in ench), "PRICE: NEW0119 = the listed C1 ids")
    K.eq(sorted(str(x) for x in C.NEW0119), sorted(i for i in NEW0119 if i in ench), "PRICE: Catalog.NEW0119 = every listed id after the frozen 20")
    K.check(all(str(C.get(i).cat) == EN.cat_of(i) for i in ench), "PRICE: every Enchanted product sits in its Void category tab (%s)"
            % [(i, str(C.get(i).cat), EN.cat_of(i)) for i in ench if str(C.get(i).cat) != EN.cat_of(i)][:4])
    bad, loops, rows = [], [], []
    for e in ench:
        pe = C.PROC_BY.get(e)
        if pe is None:
            bad.append((e, "not a processed good"))
            continue
        q = float(list(pe[4])[0])
        cands = [str(c) for c in list(pe[5][0]) if C.get(str(c)) is not None]
        sE = float(M.unit(e, False))
        bS = min(float(M.unit(c, False)) for c in cands)
        bound = EN.RATIO * bS * (1 + PREMIUM_MAX / 100.0)
        if q != EN.RATIO or sE > bound + 1e-6:
            bad.append((e, q, round(sE, 2), round(bound, 2)))
        sell1 = int(M.quote(e, 1, False))
        cost100 = min(int(M.quote(c, EN.RATIO, True)) for c in cands)
        if not sell1 < cost100:
            loops.append((e, cost100, sell1))
        rows.append((e, cands[0] if len(cands) == 1 else "%s (+%d)" % (min(cands, key=lambda c: float(M.unit(c, False))), len(cands) - 1),
                     bS, sE, sE / (EN.RATIO * bS), cost100, sell1))
    K.check(not bad, "PRICE: every Enchanted product's instant sell <= %d x its base's instant sell x (1 + %d%%) (%d checked): %s"
            % (EN.RATIO, PREMIUM_MAX, len(ench), bad[:5]))
    K.check(not loops, "PRICE: buy %d base -> craft -> sell 1 Enchanted loses coins for every one (%d): %s" % (EN.RATIO, len(ench), loops[:5]))
    print("PRICE sample (demand 1.0; unit sells; loop = buy 100 base vs sell 1):")
    for r in rows:
        if r[0][len(EN.PREFIX):] in ("Cobblestone", "Rubble", "Iron", "Mithril", "Wheat", "Corn", "Oak", "Ash", "Sand", "Crystal", "Silver", "Gold",
                                     "Bone", "HideHeavy", "Voidheart", "Stick", "Seeds", "RawBeef"):
            print("   %-24s base %-30s base sell %9.2f  Ench sell %11.2f  = %.3f x 100 base   buy 100 base %9d > sell 1 %9d"
                  % (r[0], r[1], r[2], r[3], r[4], r[5], r[6]))
    K.notes.append("PRICE: max Ench sell / (100 x base sell) = %.4f (bound %.2f)" % (max(r[4] for r in rows), 1 + PREMIUM_MAX / 100.0))
    # no un-compress recipe (Enchanted -> base) in any SET jar
    bases = dict((EN.PREFIX + t[0], t[2]) for t in EN.TABLE)
    rev = []
    for mod, ver, jp in set_jars():
        z = zipfile.ZipFile(jp)
        for n in z.namelist():
            if not (n.endswith(".json") and (n.startswith("Server/Item/Items/") or n.startswith("Server/Item/Recipes/"))):
                continue
            try:
                d = json.loads(z.read(n).decode("utf-8-sig"))
            except Exception:
                continue
            rs = [d.get("Recipe")] if n.startswith("Server/Item/Items/") else [d]
            for r in rs:
                if not isinstance(r, dict):
                    continue
                ins = [i.get("ItemId") for i in (r.get("Input") or []) if isinstance(i, dict)]
                outs = [o.get("ItemId") for o in (r.get("Output") or []) if isinstance(o, dict)] + ([n.rsplit("/", 1)[1][:-5]] if n.startswith("Server/Item/Items/") else [])
                if any(i in bases for i in ins if i) and any(o and not o.startswith(EN.PREFIX) for o in outs):
                    rev.append((mod, n, ins, outs))
    K.check(not rev, "PRICE: no SET jar has an un-compress recipe (an Enchanted item -> anything else) (%d jars): %s" % (len(set_jars()), rev[:3]))
    # every existing product unchanged: 0.1.18's seed lines + processed-goods specs are 0.1.19's minus the NEW0119 ones
    U = JClass("java.net.URLClassLoader")(jpype.JArray(JClass("java.net.URL"))([JClass("java.io.File")(OLD_JAR).toURI().toURL(),
                                                                              JClass("java.io.File")(B.SERVER_JAR).toURI().toURL()]),
                                          JClass("java.lang.ClassLoader").getPlatformClassLoader())
    OC = JClass(JClass("java.lang.Class").forName(PKG + "Catalog", True, U))
    old_seed, new_seed = [str(x) for x in OC.SEED], [str(x) for x in C.SEED]
    new_ids = set(i for i in NEW0119 if i in ench)
    K.eq([s for s in new_seed if s.split("=")[0] not in new_ids], old_seed, "PRICE: every 0.1.18 seed line is kept, byte for byte and in order (%d)" % len(old_seed))
    K.eq([s.split("=")[0] for s in new_seed if s.split("=")[0] in new_ids], [i for i in NEW0119 if i in new_ids], "PRICE: the new seed lines are NEW0119's, appended in table order")
    ospec = [l for l in str(OC.PROC_SPEC).split("\n") if l]
    nspec = [l for l in str(C.PROC_SPEC).split("\n") if l and l.split("/")[0] not in new_ids]
    K.eq(sorted(nspec), sorted(ospec), "PRICE: every 0.1.18 processed-goods spec line is kept (%d)" % len(ospec))
    for fld in ("FUEL_SPEC",):
        K.eq(str(getattr(C, fld)), str(getattr(OC, fld)), "PRICE: %s unchanged" % fld)
    # the gift value table (a report, not a gate): the 0.2.21 tier gifts (the live rewards.properties, read only) vs skyyench.gift_size
    CURVES = {"B": [50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000], "S": [50, 100, 250, 500, 1000, 2500, 5000, 10000, 20000],
              "R": [25, 50, 100, 250, 500, 1000, 2500, 5000], "E": [10, 25, 50, 100, 250, 500, 1000]}
    cdir = os.path.join(LIVE_SAVES, "Skyy_SkyyCollections")
    creg, rew = {}, {}
    try:
        for ln in open(os.path.join(cdir, "collections.properties"), encoding="latin-1").read().splitlines():
            m = re.match(r"coll\.(\w+)=([^|]*)\|([BSRE])\|[^|]*\|([^|]*)\|", ln)
            if m:
                creg[m.group(1)] = (m.group(3), m.group(4))
        for ln in open(os.path.join(cdir, "rewards.properties"), encoding="latin-1").read().splitlines():
            m = re.match(r"(\w+)\.(\d+)=(.*)", ln)
            if m:
                g = re.search(r"item:(Skyy_Ench_\w+):(\d+)", m.group(3))
                rew[(m.group(1), int(m.group(2)))] = int(g.group(2)) if g else 0
    except Exception as ex:
        K.notes.append("GIFT: the live Collections files could not be read (%s) - curve defaults used" % ex)
    samples = (("Cobblestone", "B", "Rock_Stone_Cobble", "Skyy_Ench_Cobblestone"), ("Iron", "S", "Ore_Iron", "Skyy_Ench_Iron"),
               ("Mithril", "E", "Ore_Mithril", "Skyy_Ench_Mithril"), ("Wheat", "S", "Plant_Crop_Wheat_Item", "Skyy_Ench_Wheat"),
               ("OakLog", "B", "Wood_Oak_Trunk", "Skyy_Ench_Oak"))
    print("GIFT table (instant sell at demand 1.0; old = the live 0.2.21+ rewards.properties gift, 0 = that tier unlocks something else;"
          " new = skyyench.gift_size(step) = %d %% of the step in base items / %d; '<n>b' = n base items when that rounds to 0):" % (EN.GIFT_SHARE, EN.RATIO))
    for cid, cv0, it0, eid in samples:
        cv, it = creg.get(cid, (cv0, it0))
        K.check(cv == cv0, "GIFT: %s is on curve %s (collections.properties says %s)" % (cid, cv0, cv))
        sE = int(M.quote(eid, 1, False))
        sB = float(M.unit(it, False)) if C.get(it) is not None else 0.0
        curve = CURVES[cv]
        to, tn, tg = 0, 0, 0.0
        print("  %s (curve %s, %s sells %d, %s sells %.2f):" % (cid, cv, eid, sE, it, sB))
        print("     tier   step  gathered   old n  old value   new n  new value")
        for t in range(1, len(curve) + 1):
            step = curve[t - 1] - (curve[t - 2] if t > 1 else 0)
            old = rew.get((cid, t), min(64, 2 * t)) if rew else min(64, 2 * t)
            new = min(old, EN.gift_size(step, 64)) if old else 0
            nb = EN.base_gift_size(step) if old and new == 0 else 0          # Skyy 2026-10-16 "Give base items there": the base item instead
            nv = new * sE + nb * sB
            K.check(nv <= EN.GIFT_SHARE / 100.0 * step * max(sB, sE / 100.0) * 1.25 + sB + 1e-6, "GIFT: %s tier %d new gift value %.0f <= ~%d %% of the step" % (cid, t, nv, EN.GIFT_SHARE))
            to, tn, tg = to + old * sE, tn + nv, tg + step * sB
            print("     %4d %6d %9.0f %7d %10d %7s %10.0f" % (t, step, step * sB, old, old * sE, ("%d" % new) if new else ("%db" % nb if nb else "0"), nv))
        print("     all  %6d %9.0f %7s %10d %7s %10d   (new = %.1f %% of the gathered value, old %.1f %%)"
              % (curve[-1], tg, "", to, "", tn, 100.0 * tn / tg if tg else 0, 100.0 * to / tg if tg else 0))
        K.notes.append("GIFT %s: old %d coins, new %d coins, gathered %.0f" % (cid, to, tn, tg))
    K.save()


# ------------------------------------------------------------------------------------------------------------------- MIG: migrate119 live
def run_mig(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    W = H.boot(scratch, jar, "mig")
    E = W.E
    J = lambda n: JClass(PKG + n)
    E.br = J("HubBar").map()
    C, M = J("Catalog"), J("Market")
    fp, pp, tl = (os.path.join(home, n) for n in ("products.properties", "pricing.properties", "trades.log"))
    hd = os.path.join(home, "config-history")
    raw0 = open(fp, "rb").read()
    nl = b"\r\n" if b"\r\n" in raw0 else b"\n"
    K.check(b"migrated.0.1.16=" in open(pp, "rb").read() and b"migrated.0.1.19=" not in open(pp, "rb").read(), "MIG: the live copy is a 0.1.18 folder")
    # an admin had already put one new id in by hand (another price): migrate119 keeps that line and does not add a second one
    hand = b"Skyy_Ench_Corn=Farming,999,Enchanted Corn"
    raw1 = raw0 + (b"" if raw0.endswith(b"\n") else nl) + hand + nl
    open(fp, "wb").write(raw1)
    praw = open(pp, "rb").read()
    tl0 = open(tl, "rb").read() if os.path.isfile(tl) else b""
    hist0 = set(os.listdir(hd)) if os.path.isdir(hd) else set()

    def start(n):
        """SkyyBazaarPlugin.setup()'s data steps in order, the migration lines logged to trades.log as setup() logs them"""
        J("BzUtil").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyBazaar")
        d = JClass("java.nio.file.Paths").get(home)
        C.FILE, C.PFILE = d.resolve("products.properties"), d.resolve("pricing.properties")
        M.FILE, M.LOGFILE = d.resolve("market.properties"), d.resolve("trades.log")
        J("BzCfg").load(d)
        res = {}
        for m in ("migrate", "migrate14", "migrate19", "migrate110", "migrate114", "migrate115", "migrate116"):
            res[m] = getattr(C, m)()
        res["migrate119"] = C.migrate119()
        log119 = [str(x) for x in C.M119_LOG]
        snap = open(fp, "rb").read()
        C.load()
        M.load()
        C.reprice()
        M.publishAll()
        C.flushIfDirty()
        if res["migrate119"] is not None:
            for x in log119:
                M.log(x)
            M.flushLog()          # the BzTick writes the queued trades.log lines; flushed here at once
        C.M119_LOG.clear()
        J("BzConfirm").load(d)
        return res, log119, snap
    res, log119, snap = start(1)
    K.check(all(res[m] is None for m in ("migrate", "migrate14", "migrate19", "migrate110", "migrate114", "migrate115", "migrate116")),
            "MIG 1: every older one-time update is already done on the live copy (no change)")
    K.check(res["migrate119"] is not None and str(res["migrate119"]).startswith("MIGRATE-0.1.19 added"), "MIG 1: migrate119 ran: %s" % res["migrate119"])
    K.check(snap.startswith(raw1), "MIG 1: every old byte + line ending of products.properties kept (the appended block only)")
    add = snap[len(raw1):]
    lines = add.split(nl)
    K.check(lines[-1] == b"" and (nl == b"\r\n" or not any(l.endswith(b"\r") for l in lines)), "MIG 1: the new lines use the file's line ending (%r)" % nl)
    want = [str(C.seedLine(i)).encode("utf8") for i in C.NEW0119 if str(i) != "Skyy_Ench_Corn"]
    K.eq(lines[:-1], want, "MIG 1: exactly the NEW0119 seed lines appended, in order (%d; the hand-made Corn line counted as listed)" % len(want))
    K.check(snap.count(hand + nl) == 1 and snap.count(b"\nSkyy_Ench_Corn=") == 1, "MIG 1: the hand-edited Skyy_Ench_Corn line kept byte for byte, not doubled")
    hist = sorted(set(os.listdir(hd)) - hist0)
    K.check(len(hist) == 1 and hist[0].startswith("Skyy_SkyyBazaar~products.properties.") and open(os.path.join(hd, hist[0]), "rb").read() == raw1,
            "MIG 1: the history snapshot (config-history/%s) = the old bytes" % (hist[0] if hist else None))
    p1 = open(pp, "rb").read()
    K.check(p1.startswith(praw) and b"# the one-time 0.1.19 Enchanted products update is done" in p1[len(praw):] and b"migrated.0.1.19=" in p1[len(praw):],
            "MIG 1: pricing.properties kept + the run-once marker migrated.0.1.19 (a later writeModes keeps it: %s)" % (str(C.MIGRATED119) != ""))
    t1 = open(tl, "rb").read()
    tadd = t1[len(tl0):].decode("utf8", "replace")
    K.check(t1.startswith(tl0) and ("MIGRATE-0.1.19 added %d already 1 backup config-history/%s" % (len(want), hist[0] if hist else "?")) in tadd
            and tadd.count("MIGRATE-0.1.19 ADDED ") == len(want) and "(undo: delete that line from products.properties, then /bazaaradmin reload)" in tadd,
            "MIG 1: trades.log = the head + %d ADDED lines with their undo" % len(want))
    K.eq(log119[0] if log119 else None, str(res["migrate119"]), "MIG 1: M119_LOG starts with the head line")
    K.check(all(C.get(str(i)) is not None and str(C.get(str(i)).cat) == EN.cat_of(str(i)) for i in C.NEW0119),
            "MIG 1: every NEW0119 product loaded in its Void tab")
    corn = [l for l in open(fp, "rb").read().split(nl) if l.startswith(b"Skyy_Ench_Corn=")]
    K.notes.append("MIG: after the first full start the hand-made Corn line reads %r (an AUTO good follows its recipe unless /bazaaradmin price fixes it)" % corn)
    h1 = HK.tree_hash(home)
    res2, log2, snap2 = start(2)
    K.check(res2["migrate119"] is None and not log2, "MIG 2: migrate119 is not run again (the marker)")
    K.eq(HK.tree_hash(home), h1, "MIG 2: the second start changes nothing in the folder")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyBazaar", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("hub", run_hub),
                   ("eter", run_eter),
                   ("price", run_price),
                   ("mk", lambda out, jar, scratch, home: run_mk(out, jar, AH_JAR, scratch)),
                   ("live", run_live2),
                   ("livemig", run_mig)],
           script=__file__, live=(os.path.join(LIVE_SAVES, "Skyy_SkyyBazaar"), "Skyy_SkyyBazaar"))
