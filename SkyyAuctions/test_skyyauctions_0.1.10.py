"""Harness for SkyyAuctions 0.1.10 (MENU PATTERN sweep S2, the Market tab: the kit 1.7 hub page; tools/auctions_0_1_10_patch.py; the other
half is SkyyBazaar 0.1.18). Build first:
python tools/auctions_0_1_10_patch.py && python SkyyAuctions/build_skyyauctions_0.1.10.py   (+ SkyyBazaar 0.1.18 for MK)

    python SkyyAuctions/test_skyyauctions_0.1.10.py [--dir <folder inside tools/dev/scratch/>] [--keep] [--bz <SkyyBazaar jar>]

Phases (fresh child JVMs, -Xverify:all):
  A    verify   every class loads + initialises
  C    compare  0.1.9 -> 0.1.10: exactly the listed members differ (the page, AhMarketFn's ah:fn:view, the kit 1.7 HubBar members)
  HUB  the page EXECUTED in REAL UICommandBuilders over the engine stand-ins: REG + VIS (the Auctions tab hides only while the merged
       Bazaar is there); EVERY view (Browse, an item, Create BIN, Manage, empty lists) through SUI.assert_menu_page (1600 x 980, row 1 +
       row 2, ONE sub-tab row, no back button / < Menu, no pager, the content fits) + the markup rules; the sub-tabs AUCTION HOUSE |
       CREATE BIN | MANAGE (+ BAZAAR when merged) with the open view selected; no "< Back to results" - AUCTION HOUSE / the own tab in
       row 2 lead back to the list; rule 7 (3 listings = 116 px rows, many = 58 px rows that scroll); Show more after 200 rows; the hub
       clicks (route: row 1, row 2, the X); the Browse sort by tier (0.1.9's TIER checks); a LIST / BUY / CLAIM smoke through the page
       clicks (pick an inventory slot, price, Preview, Create BIN; another player Views + Buys (+ Confirm); the seller claims the coins in
       Manage) with a fake SkyyCoins bridge and real inventories; ah:fn:view (junk, the claims count, the views)
  MK   SkyyBazaar/test_skyybazaar_0.1.18.py run_mk with this jar: both jars together, every merge path + the four sub-tabs on both pages
  D    live     two opens on a scratch COPY of the live Skyy_SkyyAuctions (NewBetaTest; read-only source): nothing written
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, json, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import hub_tab_harness as H
import skyyui as SUI

VERSION = "0.1.10"
PKG = "com.skyy.auctions."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyAuctions-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyAuctions-0.1.9.jar")
BZ_JAR = os.path.abspath(HK.arg("--bz", os.path.join(ROOT, "SkyyBazaar", "SkyyBazaar-0.1.18.jar")))
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "menuS2", "market", "ah")))
LIVE = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyAuctions")

_sp = importlib.util.spec_from_file_location("bz0118test", os.path.join(ROOT, "SkyyBazaar", "test_skyybazaar_0.1.18.py"))
TB = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(TB)
EXPECT = {"AhPage": ["+f showN", "~m render", "~m renderTop", "~m renderBrowse", "~m renderItem", "~m renderCreate", "~m renderManage",
                     "~m hubClick", "~m handleDataEvent", "~m browseAct", "~m readFields"],
          "AhMarketFn": ["+m view", "~m apply"],
          "SkyyAuctionsPlugin": ["~m setup", "~m shutdown"],
          "AhCmds": ["~m status"], "CfgFn": ["~m opExport"], "CfgRows": ["~m header"],
          "HubBar": TB.EXPECT["HubBar"]}          # the kit 1.7 HubBar: only additions (the same kit source as SkyyBazaar 0.1.18)
ADDED = []


def prep(E, J, home):
    TB.ah_prep(E, J, home)


def vis_cases(K, E, J, vis, u):
    import jpype
    from jpype import JClass, JImplements, JOverride
    TRUE, FALSE = JClass("java.lang.Boolean").TRUE, JClass("java.lang.Boolean").FALSE

    @JImplements("java.util.function.Function")
    class F:
        @JOverride
        def apply(self, o):
            return TRUE
    tab = jpype.JArray(JClass("java.lang.Object"))(["SkyyBazaar", "Market", JClass("java.lang.Integer")(10), "bazaar", F(), None])
    E.br.put("hub:tab:market:bazaar", tab)
    K.check(vis.apply(u) == TRUE and str(J("AhPage").myTab()) == "auctions", "VIS: the Bazaar tab alone (an older Bazaar, no bazaar:fn:open) -> Auctions shows")
    E.br.put("bazaar:fn:open", F())
    K.check(vis.apply(u) == FALSE and str(J("AhPage").myTab()) == "bazaar", "VIS: the merged Bazaar (tab + bazaar:fn:open) -> Auctions hidden, Market active")
    E.br.remove("hub:tab:market:bazaar")
    K.check(vis.apply(u) == TRUE and str(J("AhPage").myTab()) == "auctions", "VIS: bazaar:fn:open alone (no tab) -> Auctions shows")
    E.br.remove("bazaar:fn:open")


def run_hub(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    W = H.boot(scratch, jar, "hub")
    E = W.E
    J = lambda n: JClass(PKG + n)
    HB = J("HubBar")
    E.br = HB.map()
    home = os.path.join(scratch, "home_hub", "Skyy_SkyyAuctions")
    prep(E, J, home)
    TB.fake_items(E, ["Ore_Iron", "Ore_Copper", "Ingredient_Bar_Iron", "Ore_Mithril", "Weapon_Sword_Iron", "Plant_Crop_Wheat_Item"])
    purse = {}
    TB.fake_coins(E.br, purse)
    K.check(bool(J("Coins").ready()), "X: the fake SkyyCoins bridge is seen")
    TRUE, FALSE = JClass("java.lang.Boolean").TRUE, JClass("java.lang.Boolean").FALSE
    P, O = W.P, W.O
    u, uo = P.pr.getUuid(), O.pr.getUuid()
    purse[str(u)] = 1000000
    purse[str(uo)] = 1000000
    for X in (P, O):
        E.br.put("hub:last:" + str(X.pr.getUuid()), JClass("java.util.concurrent.ConcurrentHashMap")())
    # ---------------------------------------------------------------- REG + VIS
    K.eq(int(J("AhHubOpen").register()), 1, "REG: the Auctions tab is put")
    e = E.br.get("hub:tab:market:auctions")
    K.check(e is not None and str(e[1]) == "Auctions" and str(e[3]) == "ah" and cls_of(e[5]) == PKG + "AhHubVis", "REG: hub:tab:market:auctions + AhHubVis")
    K.check(e[5].apply(u) == TRUE, "VIS: AhHubVis shows the tab by default")
    vis_cases(K, E, J, e[5], u)
    # ---------------------------------------------------------------- PAGE: Browse with nothing listed (the empty state)
    K.eq(str(HB.open(P.pr, u, "market", "auctions")), "bridge", "PAGE: HubBar.open(market, auctions) opens through the bridge Function")
    E.pump(P)
    pg = P.pm.getCustomPage()
    K.check(cls_of(pg) == PKG + "AhPage" and str(pg.view) == "browse", "PAGE: the Auction House is open on Browse")
    pg, cm, ev, apps = TB.built(K, E, P, "PAGE Browse (empty)")
    K.check(apps[0][1].startswith("Group #SkyyAhF { Anchor: (Width: 1600, Height: 980); }"), "PAGE: the root #SkyyAhF is 1600 x 980")
    K.eq(TB.row2(cm, "SkyyAhF"), [("Auctions", True)], "PAGE: row 2 = the Market hub's tabs (only Auctions loaded), Auctions selected")
    K.eq(TB.subtabs(cm, "SkyyAhF"), [("Auction House", True), ("Create BIN", False), ("Manage", False)],
         "PAGE: the ONE sub-tab row without the Bazaar = AUCTION HOUSE (selected) | CREATE BIN | MANAGE")
    K.check(str(TB.set_of(cm, "#SkyyAhEmpty.Text")).startswith("Nothing listed here yet"), "PAGE: the empty list says how to fill it")
    K.check(str(TB.set_of(cm, "#SkyyAhPurse.Text")).startswith("Purse: 1,000,000 coins") or str(TB.set_of(cm, "#SkyyAhPurse.Text")).startswith("Purse: 1000000"),
            "PAGE: the purse in the sub-tab row (%s)" % TB.set_of(cm, "#SkyyAhPurse.Text"))
    K.check(any(s == "#SkyyAhFHubClose" and "hub:close" in t for s, t in ev), "PAGE: the X = hub:close")
    TB.hub_defs(E)                    # SkyyMenu's hub:def entries -> row 1 = Home + the 7 hubs
    pg, cm, ev, apps = TB.built(K, E, P, "PAGE Browse (SkyyMenu's hub defs: row 1 drawn)")
    K.check(sum(1 for s, t in ev if "hub:h:" in t) == len(SUI.HUB_ROW_IDS), "PAGE: row 1 = Home + the hubs, each bound hub:h:<id>")
    for h in SUI.HUB_ROW_IDS:
        E.br.remove("hub:def:" + h)
    for v in ("create", "manage"):
        p2, ok = TB.click(E, P, '{"a":"nav:%s"}' % v)
        TB.built(K, E, P, "PAGE %s (empty)" % v)
    TB.click(E, P, '{"a":"nav:browse"}')
    # ---------------------------------------------------------------- the hub clicks (route)
    mark = "#SkyyAhFTitle.Text"
    pg = P.pm.getCustomPage()
    n0 = len(E.sent(P))
    p2, ok = TB.click(E, P, '{"a":"hub:auctions"}')
    K.check(TB.same(p2, pg) and mark in E.strs_of(P, n0), "CLICK: row 2's own tab on Browse keeps the page and answers it")
    n0 = len(E.sent(P))
    p2, ok = TB.click(E, P, '{"a":"hub:h:market"}')
    K.check(TB.same(p2, pg) and mark in E.strs_of(P, n0), "CLICK: row 1's own hub keeps the page and answers it")
    p2, ok = TB.click(E, P, '{"a":"hub:zzgone"}')
    K.check(TB.same(p2, pg) and "could not open right now" in str(p2.status), "CLICK: a missing tab says so (%s)" % p2.status)
    E.br.remove("config:def:SkyyMenu")
    p2, ok = TB.click(E, P, '{"a":"hub:h:home"}')
    K.check(p2 is None, "CLICK: Home without SkyyMenu closes the page")
    HB.open(P.pr, u, "market", "auctions")
    E.pump(P)
    p2, ok = TB.click(E, P, '{"a":"close"}')
    K.check(p2 is None, "CLICK: the footer Close closes the page")
    # ---------------------------------------------------------------- rule 7 + Show more on Browse
    now = int(JClass("java.lang.System").currentTimeMillis())
    Rec, Sto = J("AhRec"), J("AhStore")
    for i, it in ((901, "Ore_Iron"), (902, "Ore_Copper"), (903, "Ingredient_Bar_Iron")):
        Sto.livePut(str(i), Rec.parse(TB.rec_json(i, it, 2, 100 + i, 3600000, now, it.replace("_", " "), "Tess")))
    HB.open(P.pr, u, "market", "auctions")
    E.pump(P)
    pg, cm, ev, apps = TB.built(K, E, P, "BROWSE 3 listings")
    rows = [t for ty, s, t, d in cm if t and s == "#SkyyAhList" and t.startswith("Group #SkyyAhRow")]
    K.check(len(rows) == 3 and all("Height: 116," in t for t in rows), "BROWSE: 3 listings = 3 rows of 116 px (rule 7: a short list fills its room)")
    K.eq(TB.set_of(cm, "#SkyyAhPageTxt.Text"), "3 listings", "BROWSE: the count line")
    TB.ah_views(K, E, P, J, "HUB", merged=False)
    for i in range(1000, 1230):
        Sto.livePut(str(i), Rec.parse(TB.rec_json(i, "Ore_Iron", 1, 10 + i, 3600000, now, "Iron Ore", "Many")))
    pg = P.pm.getCustomPage()
    pg.view = "browse"
    pg, cm, ev, apps = TB.built(K, E, P, "BROWSE 233 listings")
    rows = [t for ty, s, t, d in cm if t and s == "#SkyyAhList" and t.startswith("Group #SkyyAhRow")]
    K.check(len(rows) == 200 and all("Height: 58," in t for t in rows) and any(t and "#SkyyAhMore " in t for ty, s, t, d in cm),
            "BROWSE: 233 listings = the first 200 rows of 58 px (they scroll) + a Show more row")
    K.eq(TB.set_of(cm, "#SkyyAhPageTxt.Text"), "showing 200 of 233 listings", "BROWSE: the count says how many are shown")
    p2, ok = TB.click(E, P, '{"a":"more","@AhSearch":""}')
    p2, cm, ev, apps = TB.built(K, E, P, "BROWSE Show more")
    K.check(ok and len(list(p2.rowIds)) == 233 and not any(t and "#SkyyAhMore " in t for ty, s, t, d in cm), "BROWSE: Show more -> all 233 rows")
    p2, ok = TB.click(E, P, '{"a":"search","@AhSearch":"copper"}')
    K.check(ok and int(p2.showN) == 0 and len(list(p2.rowIds)) == 1, "BROWSE: a new search starts the list again (1 copper listing)")
    p2, ok = TB.click(E, P, '{"a":"prev"}')
    K.check(ok, "OLD: a stale prev click (0.1.9 pager) is answered")
    for i in list(range(1000, 1230)) + [901, 902, 903]:
        Sto.LIVE.remove(str(i))
    # ---------------------------------------------------------------- LIST / BUY / CLAIM smoke through the page clicks
    J("AhCfg").GRACE_MS = 0
    TB.give(P, "Ore_Iron", 10, slot=0)
    K.eq(int(E.count(P, "Ore_Iron")), 10, "SMOKE: the seller holds 10 Iron Ore")
    HB.open(P.pr, u, "market", "auctions")
    E.pump(P)
    p2, ok = TB.click(E, P, '{"a":"nav:create"}')
    p2, cm, ev, apps = TB.built(K, E, P, "CREATE (an inventory to pick from)")
    cells = [t for ty, s, t, d in cm if t and s and s.startswith("#SkyyAhInvRow") and t.startswith("Button #SkyyAhInv")]
    K.check(len(cells) >= 1 and "Width: 76, Height: 76" in cells[0] and not any(t and ("SkyyAhInvPrev" in t or "SkyyAhInvNext" in t) for ty, s, t, d in cm),
            "CREATE: the picker = kit cells in ONE scroll list (%d), no pager" % len(cells))
    idx = [i for i in range(len(list(p2.cellSec))) if int(p2.cellSec[i]) == 0 and int(p2.cellSlot[i]) == 0]
    K.check(len(idx) == 1, "CREATE: the hotbar slot 0 stack is a cell")
    p2, ok = TB.click(E, P, '{"a":"pick:%d","@AhPrice":""}' % idx[0])
    K.check(ok and int(p2.pickSec) == 0 and int(p2.pickSlot) == 0, "CREATE: pick the Iron Ore (%s)" % p2.status)
    p2, ok = TB.click(E, P, '{"a":"preview","@AhPrice":"500"}')
    TB.built(K, E, P, "CREATE (picked, previewed)")
    p0 = purse[str(u)]
    n_before = int(Sto.LIVE.size())
    p2, ok = TB.click(E, P, '{"a":"create","@AhPrice":"500"}')
    K.check(ok and int(Sto.LIVE.size()) == n_before + 1 and int(E.count(P, "Ore_Iron")) == 0 and str(p2.view) == "manage",
            "SMOKE LIST: Create BIN listed the 10 Iron Ore (the stack left the inventory, Manage opens; fee %d) - %s" % (p0 - purse[str(u)], p2.status))
    TB.built(K, E, P, "MANAGE (one listing)")
    lid = [str(k) for k in Sto.LIVE.keySet()][0]
    # the buyer: Browse -> View -> Buy (-> Confirm when dear)
    pgo = J("AhPage")(O.pr, "browse")
    O.pm.openCustomPage(O.ref, O.st, pgo)
    E.pump(O)
    po, cmo, evo, appso = TB.built(K, E, O, "BUYER Browse")
    ri = [i for i in range(len(list(po.rowIds))) if str(po.rowIds[i]) == lid]
    K.check(len(ri) == 1, "SMOKE BUY: the buyer sees listing #%s" % lid)
    po, ok = TB.click(E, O, '{"a":"view:%d","@AhSearch":""}' % ri[0])
    po, cmo, evo, appso = TB.built(K, E, O, "BUYER item page")
    K.check(any(t and "#SkyyAhDBuy " in t for ty, s, t, d in cmo) and not any(t and "SkyyAhDBack" in t for ty, s, t, d in cmo), "SMOKE BUY: Buy now, no back button")
    b0 = purse[str(uo)]
    po, ok = TB.click(E, O, '{"a":"buy"}')
    if po.armAct is not None:
        po, ok = TB.click(E, O, '{"a":"confirm"}')
    got = int(E.count(O, "Ore_Iron")) == 10
    K.check(purse[str(uo)] == b0 - 500 and (got or "waits in Manage" in str(po.status)),
            "SMOKE BUY: the buyer paid 500 and holds the 10 Iron Ore or it waits in Manage (the stand-in inventory: %s)" % po.status)
    K.eq(str(J("AhRec").state(Sto.get(lid))), "SOLD", "SMOKE BUY: the listing is SOLD")
    if not got:
        # the buyer's claim row in Manage (the 0.1.9 claim path through the page click)
        po, ok = TB.click(E, O, '{"a":"nav:manage"}')
        po, cmo, evo, appso = TB.built(K, E, O, "BUYER Manage (an item to claim)")
        bi = [i for i in range(len(list(po.mIds))) if str(po.mIds[i]) == lid]
        K.check(len(bi) == 1 and str(po.mKinds[bi[0]]) == "bitem", "SMOKE CLAIM: the bought item waits as a buyer claim")
        po, ok = TB.click(E, O, '{"a":"mact:%d"}' % bi[0])
        K.check(ok and len(str(po.status)) > 0, "SMOKE CLAIM: Claim item is answered (%s)" % po.status)
    # the seller claims the coins in Manage
    HB.open(P.pr, u, "market", "auctions")
    E.pump(P)
    p2, ok = TB.click(E, P, '{"a":"nav:manage"}')
    p2, cm, ev, apps = TB.built(K, E, P, "MANAGE (coins to claim)")
    K.check(TB.subtabs(cm, "SkyyAhF")[2] == ("Manage (1)", True), "MANAGE: the sub-tab says Manage (1), selected")
    mi = [i for i in range(len(list(p2.mIds))) if str(p2.mIds[i]) == lid]
    K.check(len(mi) == 1 and str(p2.mKinds[mi[0]]) == "coins", "SMOKE CLAIM: the sold listing waits as coins")
    s0 = purse[str(u)]
    p2, ok = TB.click(E, P, '{"a":"mact:%d"}' % mi[0])
    K.check(purse[str(u)] > s0, "SMOKE CLAIM: Claim coins paid %d coins into the purse (%s)" % (purse[str(u)] - s0, p2.status))
    p2, cm, ev, apps = TB.built(K, E, P, "MANAGE (claimed)")
    K.check(TB.subtabs(cm, "SkyyAhF")[2] == ("Manage", True), "MANAGE: nothing to claim any more")
    # ---------------------------------------------------------------- ah:fn:view
    vw = J("AhMarketFn")(2)
    K.check(vw.apply("x") == FALSE and vw.apply(jpype.JArray(JClass("java.lang.Object"))([u, "nope"])) == FALSE, "VIEW: junk / an unknown view = FALSE")
    K.check(int(vw.apply(u)) == 0, "VIEW: a UUID = the claims waiting (0 now)")
    K.check(vw.apply(jpype.JArray(JClass("java.lang.Object"))([u, "manage"])) == TRUE and str(P.pm.getCustomPage().view) == "manage", "VIEW: opens Manage")
    browse_tier(K, E, J, P)
    K.eq(int(HB.removeAll()), 1, "DROP: removeAll removed our tab")
    K.save()


def cls_of(o):
    return None if o is None else str(o.getClass().getName())


def browse_tier(K, E, J, X):
    """0.1.9 hubmktfix: Browse sorted by tier then name by default (Skyy 2026-10-16 "sort everything by tier in all shops and crafting.")"""
    from jpype import JClass
    import tier_tags as TT
    It = J("AhItem")
    bad = [i for i in TT.ROWS if int(It.sortTier(i, -1)) != TT.tier(i)]
    K.check(not bad and len(It.ttMap()) == len(TT.ROWS), "TIER: AhItem.sortTier = tools/tier_tags.py for all %d rows (%s)" % (len(TT.ROWS), bad[:3]))
    names = [str(x) for x in J("AhPage").SORT_NAME]
    K.eq(names, ["Tier then name", "Price low-high", "Price high-low", "Ending soonest", "Newest listed"], "TIER: the Sort list, tier first")
    now = int(JClass("java.lang.System").currentTimeMillis())
    Rec, Sto = J("AhRec"), J("AhStore")
    rows = [(9901, "Ore_Mithril", 1, 900, 3600000, "Mithril Ore"), (9902, "Ore_Iron", 10, 500, 3600000, "Iron Ore"),
            (9903, "Weapon_Sword_Iron", 1, 50, 3600000, "Iron Sword"), (9904, "Ore_Copper", 4, 40, 3600000, "Copper Ore"),
            (9905, "Ore_Iron", 2, 40, 7200000, "Iron Ore"), (9906, "Ingredient_Bar_Iron", 1, 999, 3600000, "Iron Bar"),
            (9907, "Ore_Iron", 5, 250, 600000, "Iron Ore")]
    for i, it, q, pr_, ends, nm in rows:
        Sto.livePut(str(i), Rec.parse(TB.rec_json(i, it, q, pr_, ends, now, nm, "Tess")))
    pg = J("AhPage")(X.pr, "browse")
    mine = lambda lst: [int(str(Rec.id(r))) for r in lst if str(Rec.id(r)).startswith("990")]
    K.eq(mine(pg.results(now)), [9904, 9906, 9905, 9907, 9902, 9901, 9903], "TIER: tier, then name, then coins each, ending soonest (0.1.9 order kept)")
    for i, *_r in rows:
        Sto.LIVE.remove(str(i))


S = H.Spec(name="SkyyAuctions", version=VERSION, pkg=PKG, hub="market", tab="auctions", mod="SkyyAuctions", open_cls="AhHubOpen", vis_cls="AhHubVis",
           vis_cases=vis_cases, page_cls="AhPage", prefix="SkyyAhF", idp="SkyyAh", plugin_cls="SkyyAuctionsPlugin", register_call="AhHubOpen.register",
           register=lambda J: J("AhHubOpen").register(), prep=prep, jar=JAR, old_jar=OLD_JAR, scratch=SCRATCH, script=__file__,
           added=ADDED, expect=EXPECT)

if __name__ == "__main__":
    HK.run(name=S.name, version=S.version, jar=S.jar, old_jar=S.old_jar, pkg=S.pkg, scratch=S.scratch, expect=S.expect, added=S.added,
           phases=[("hub", run_hub),
                   ("mk", lambda out, jar, scratch, home: TB.run_mk(out, BZ_JAR, jar, scratch)),
                   ("live", lambda out, jar, scratch, home: H.run_live(S, out, jar, scratch, home))],
           script=__file__, live=(LIVE, "Skyy_SkyyAuctions"))
