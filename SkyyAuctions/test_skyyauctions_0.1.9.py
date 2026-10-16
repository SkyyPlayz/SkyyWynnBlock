"""Harness for SkyyAuctions 0.1.9 (round hubmkt: the MARKET MERGE; tools/auctions_0_1_9_patch.py; the other half is SkyyBazaar 0.1.17).
Build first: python tools/auctions_0_1_9_patch.py && python SkyyAuctions/build_skyyauctions_0.1.9.py   (+ SkyyBazaar 0.1.17 for MK)

    python SkyyAuctions/test_skyyauctions_0.1.9.py [--dir <folder inside tools/dev/scratch/>] [--keep] [--bz <SkyyBazaar jar>]

Phases (fresh child JVMs, -Xverify:all):
  A    verify   every class loads + initialises
  C    compare  0.1.8 -> 0.1.9: exactly the listed members differ, AhHubVis + AhMarketFn added
  TIER (inside HUB) Browse sorted by tier then name by default (fix round hubmktfix): sortTier = tools/tier_tags.py + level bands,
       the Sort list, results() order on generated listings, the 4 old sorts unchanged, the Sort button cycles
  HUB  tools/hub_tab_harness.py run_hub EXECUTED (REG with the visible Function AhHubVis, PAGE, every hub CLICK, DROP) + VIS: the tab
       hides only while the merged Bazaar is there (hub:tab:market:bazaar AND bazaar:fn:open), shows with only one of them; every view
       (Browse, Create BIN, Manage) through page_check: the 36 px sub-view row (no BAZAAR button without the Bazaar), 1128 x 976
  MK   SkyyBazaar 0.1.17's MK phase (SkyyBazaar/test_skyybazaar_0.1.17.py run_mk) with this jar: both jars together, every merge path
  D    live     two opens on a scratch COPY of the live Skyy_SkyyAuctions (NewBetaTest; read-only source): nothing written
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import hub_tab_harness as H

VERSION = "0.1.9"
PKG = "com.skyy.auctions."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyAuctions-%s.jar" % VERSION)))
BZ_JAR = os.path.abspath(HK.arg("--bz", os.path.join(ROOT, "SkyyBazaar", "SkyyBazaar-0.1.17.jar")))
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "hubmkt", "ah")))
LIVE = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyAuctions")

_sp = importlib.util.spec_from_file_location("bz0117test", os.path.join(ROOT, "SkyyBazaar", "test_skyybazaar_0.1.17.py"))
TB = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(TB)


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


def chk_manage(K, E, J, P, before, after, f0):
    K.check(after is not None and str(after.getClass().getSimpleName()) == "AhPage" and str(after.view) == "manage" and len(E.sent(P)) > f0,
            "CLICK: the Manage nav button (not a hub click) switches the view on the page (%s)" % (None if after is None else after.view))


def chk_mkbz(K, E, J, P, before, after, f0):
    K.check(after is not None and str(after.getClass().getSimpleName()) == "AhPage" and "#SkyyAhFTitle.Text" in E.strs_of(P, f0),
            "CLICK: BAZAAR (mk:bz) through a bazaar tab Function that answered TRUE without a page -> this page is answered")


def extra_hub(K, W, J):
    from jpype import JClass
    E = W.E
    J("AhHubOpen").register()
    X = W.O
    E.br.put("hub:last:" + str(X.pr.getUuid()), JClass("java.util.concurrent.ConcurrentHashMap")())
    for view in ("browse", "create", "manage"):
        pg = J("AhPage")(X.pr, view)
        X.pm.openCustomPage(X.ref, X.st, pg)
        E.pump(X)
        cm, _ev = H.page_check(K, E, S, X, pg, J("HubBar"), "PAGE %s" % view)
        top = [c for c in cm if c[2] and c[2].startswith("Group #SkyyAhTop ")]
        K.check(len(top) == 1 and "Height: 36" in top[0][2], "PAGE %s: the sub-view row is 36 px" % view)
        K.check(any(c[2] and "#SkyyAhMkAh " in c[2] for c in cm) and not any(c[2] and "#SkyyAhMkBz " in c[2] for c in cm),
                "PAGE %s: AUCTION HOUSE drawn, no BAZAAR button without the Bazaar" % view)
        K.check(any(c[2] and "#SkyyAhPurse " in c[2] for c in cm), "PAGE %s: the purse kept" % view)
        K.check("Width: 1128, Height: 976" in cm[0][2], "PAGE %s: 1128 x 976" % view)
    # BAZAAR with no Bazaar at all (no bazaar:fn:open, no Market tab): the status line says so, the page stays
    pg = J("AhPage")(X.pr, "browse")
    X.pm.openCustomPage(X.ref, X.st, pg)
    E.pump(X)
    for k in [str(x) for x in E.br.keySet() if str(x).startswith("hub:tab:market:bazaar")] + ["bazaar:fn:open"]:
        E.br.remove(k)
    X.pm.handleLegacyCustomPageEvent(X.ref, X.st, E.CPE(E.CPT.Data, '{"a":"mk:bz","@AhSearch":"iron"}'))
    E.pump(X)
    pz = X.pm.getCustomPage()
    K.check(pz is not None and str(pz.getClass().getSimpleName()) == "AhPage" and "Bazaar is not on this server" in str(pz.status) and str(pz.query) == "iron",
            "CLICK: BAZAAR without any Bazaar says so on the status line, the search kept (%s)" % (None if pz is None else pz.status))
    browse_tier(K, E, J, X)
    J("HubBar").removeAll()


def browse_tier(K, E, J, X):
    """fix round hubmktfix: Browse sorted by tier then name by default (Skyy 2026-10-16 "sort everything by tier in all shops and crafting.")"""
    from jpype import JClass
    import tier_tags as TT
    It = J("AhItem")
    bad = [i for i in TT.ROWS if int(It.sortTier(i, -1)) != TT.tier(i)]
    K.check(not bad and len(It.ttMap()) == len(TT.ROWS), "TIER: AhItem.sortTier = tools/tier_tags.py for all %d rows (%s)" % (len(TT.ROWS), bad[:3]))
    lvbad = [(lv, x) for lv in range(0, 90) for x in ("Weapon_Sword_Iron", "Armor_Onyxium_Head")
             if TT.tier(x) is None and int(It.sortTier(x, lv)) != TT.tier_for_level(lv, x)]
    K.check(not lvbad, "TIER: an untabled id with a SkyyGear level takes tier_for_level's band (%s)" % lvbad[:3])
    K.check(int(It.sortTier("Weapon_Sword_Iron", -1)) == 99 and int(It.sortTier(None, 5)) == 99, "TIER: untiered without a level = 99 (last)")
    names = [str(x) for x in J("AhPage").SORT_NAME]
    K.eq(names, ["Tier then name", "Price low-high", "Price high-low", "Ending soonest", "Newest listed"], "TIER: the Sort list, tier first")
    K.eq([int(x) for x in J("AhPage").SORT_MODE], [5, 0, 1, 2, 3], "TIER: each Sort entry's AhSort mode (the 4 old sorts unchanged)")
    now = int(JClass("java.lang.System").currentTimeMillis())
    Rec, Sto = J("AhRec"), J("AhStore")
    rows = [(901, "Ore_Mithril", 1, 900, 3600000, "Mithril Ore"), (902, "Ore_Iron", 10, 500, 3600000, "Iron Ore"),
            (903, "Weapon_Sword_Iron", 1, 50, 3600000, "Iron Sword"), (904, "Ore_Copper", 4, 40, 3600000, "Copper Ore"),
            (905, "Ore_Iron", 2, 40, 7200000, "Iron Ore"), (906, "Ingredient_Bar_Iron", 1, 999, 3600000, "Iron Bar"),
            (907, "Ore_Iron", 5, 250, 600000, "Iron Ore")]
    for i, it, q, pr_, ends, nm in rows:
        Sto.livePut(str(i), Rec.parse(TB.rec_json(i, it, q, pr_, ends, now, nm, "Tess")))
    pg = J("AhPage")(X.pr, "browse")
    K.eq(int(pg.sort), 0, "TIER: a new Browse starts on sort 0 = Tier then name")
    mine = lambda lst: [int(str(Rec.id(r))) for r in lst if str(Rec.id(r)).startswith("90")]
    K.eq(mine(pg.results(now)), [904, 906, 905, 907, 902, 901, 903],
         "TIER: Copper T2, then T3 by name (Iron Bar, Iron Ore: 20 each, then 50 each ending soonest #907 before #902), Mithril T7, untiered sword last")
    pg.sort = 1
    K.eq(mine(pg.results(now)), [904, 905, 903, 907, 902, 901, 906], "TIER: sort 1 = Price low-high (total price, ties ending soonest) exactly as 0.1.8's mode 0")
    pg.sort = 4
    srt = mine(pg.results(now))
    K.check(len(srt) == 7, "TIER: Newest listed still lists all 7 (%s)" % srt)
    pg2 = J("AhPage")(X.pr, "browse")
    pg2.sort = 3
    X.pm.openCustomPage(X.ref, X.st, pg2)
    E.pump(X)
    X.pm.handleLegacyCustomPageEvent(X.ref, X.st, E.CPE(E.CPT.Data, '{"a":"sort"}'))
    E.pump(X)
    K.eq(int(pg2.sort), 4, "TIER: the Sort button cycles (3 -> 4)")
    X.pm.handleLegacyCustomPageEvent(X.ref, X.st, E.CPE(E.CPT.Data, '{"a":"sort"}'))
    E.pump(X)
    K.eq(int(pg2.sort), 0, "TIER: the Sort button wraps back to Tier then name (4 -> 0)")
    for i, *_r in rows:
        Sto.LIVE.remove(str(i))


S = H.Spec(name="SkyyAuctions", version=VERSION, pkg=PKG, hub="market", tab="auctions", mod="SkyyAuctions", open_cls="AhHubOpen", vis_cls="AhHubVis",
           vis_cases=vis_cases, page_cls="AhPage", prefix="SkyyAhF", idp="SkyyAh", plugin_cls="SkyyAuctionsPlugin", register_call="AhHubOpen.register",
           register=lambda J: J("AhHubOpen").register(), prep=prep,
           legacy_texts=["Search items or sellers...", "e.g. 12000 or 12k"], clicks=[('{"a":"nav:manage"}', chk_manage), ('{"a":"mk:bz"}', chk_mkbz)],
           extra_hub=extra_hub, jar=JAR, old_jar=os.path.join(HERE, "SkyyAuctions-0.1.8.jar"), scratch=SCRATCH, script=__file__,
           added=["AhHubVis", "AhMarketFn"],
           expect={"AhPage": ["+m merged", "+m myTab", "+m mkBazaar", "~m render", "~m renderTop", "~m hubClick", "~m handleDataEvent",
                              "+f SORT_MODE", "~<clinit>", "~m results"],          # hubmktfix: Browse sorted by tier
                   "AhItem": ["+f TT_MAP", "+f TT_SPEC", "+m lvTier", "+m sortKey", "+m sortTier", "+m ttMap", "~<clinit>"],
                   "AhSort": ["~m compare"],
                   "AhHubOpen": ["~m register"], "SkyyAuctionsPlugin": ["~m setup", "~m shutdown"],
                   "AhCmds": ["~m status"], "CfgFn": ["~m opExport"], "CfgRows": ["~m header"]})

if __name__ == "__main__":
    HK.run(name=S.name, version=S.version, jar=S.jar, old_jar=S.old_jar, pkg=S.pkg, scratch=S.scratch, expect=S.expect, added=S.added,
           phases=[("hub", lambda out, jar, scratch, home: H.run_hub(S, out, jar, scratch)),
                   ("mk", lambda out, jar, scratch, home: TB.run_mk(out, BZ_JAR, jar, scratch)),
                   ("live", lambda out, jar, scratch, home: H.run_live(S, out, jar, scratch, home))],
           script=__file__, live=(LIVE, "Skyy_SkyyAuctions"))
