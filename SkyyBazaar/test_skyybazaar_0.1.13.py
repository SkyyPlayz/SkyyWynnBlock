"""Harness for SkyyBazaar 0.1.13 (HUBS H3b: the Market > Bazaar tab; tools/bazaar_0_1_13_patch.py). Build first:
python tools/bazaar_0_1_13_patch.py && python SkyyBazaar/build_skyybazaar_0.1.13.py

    python SkyyBazaar/test_skyybazaar_0.1.13.py [--dir <folder inside tools/dev/scratch/>] [--keep]

The phases are tools/hub_tab_harness.py's (A verify, C compare 0.1.12 -> 0.1.13 + the kit bytes, HUB executed: REG / PAGE / CLICK / DROP,
D live: two opens on a scratch COPY of the live Skyy_SkyyBazaar (its catalogue + market loaded as setup() loads them), AA engine-access
audit), plus here:
  PAGE  the grid shows 3 rows of 13 = 39 products a page (0.1.12: 4 rows, 52): at most 39 cells, the pager says "of" pages for the
        catalogue; 1094 x 943 in the hub shell
  CLICK Next / Find (non-hub clicks) still act on the page
Exit code 1 on any failure.
"""
import os, sys, re, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK
import hub_tab_harness as H

VERSION = "0.1.13"
PKG = "com.skyy.bazaar."


def prep(E, J, home):
    from jpype import JClass
    J("BzUtil").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyBazaar")
    d = E.Paths.get(home)
    J("Catalog").FILE = d.resolve("products.properties")
    J("Catalog").PFILE = d.resolve("pricing.properties")
    J("Market").FILE = d.resolve("market.properties")
    J("Market").LOGFILE = d.resolve("trades.log")
    J("BzCfg").load(d)
    J("Catalog").migrate()
    J("Catalog").migrate14()
    J("Catalog").migrate19()
    J("Catalog").migrate110()
    J("Catalog").load()
    J("Market").load()
    J("Catalog").reprice()


def chk_next(K, E, J, P, before, after, f0):
    K.check(after is not None and str(after.getClass().getSimpleName()) == "BzPage" and len(E.sent(P)) > f0 and int(after.pageNo) >= 0,
            "CLICK: Next (not a hub click) acts on the bazaar page (page %s)" % (None if after is None else after.pageNo))


def chk_find(K, E, J, P, before, after, f0):
    K.check(after is not None and str(after.query) == "log", "CLICK: Find with a search (not a hub click) applies it (%s)" % (None if after is None else after.query))


def extra_hub(K, W, J):
    from jpype import JClass
    E = W.E
    J("BzHubOpen").register()
    X = W.O
    E.br.put("hub:last:" + str(X.pr.getUuid()), JClass("java.util.concurrent.ConcurrentHashMap")())
    J("HubBar").open(X.pr, X.pr.getUuid(), "market", "bazaar")
    E.pump(X)
    pg = X.pm.getCustomPage()
    b = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")()
    pg.build(X.ref, b, JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")(), X.st)
    cm = H.cmds_of(b)
    cells = [c for c in cm if c[2] and re.search(r"#SkyyBzCell\d+ ", c[2])]
    rows = [c for c in cm if c[2] and re.search(r"Group #SkyyBzRow\d+ ", c[2])]
    n = int(J("Catalog").categories().size()) if hasattr(J("Catalog"), "categories") else -1
    K.check(len(rows) == 3 and 0 < len(cells) <= 39, "PAGE: the grid is 3 rows, at most 39 products (%d rows, %d cells; %d tabs)" % (len(rows), len(cells), n))
    K.check("Width: 1094, Height: 943" in cm[0][2], "PAGE: 1094 x 943 (%s)" % cm[0][2][:60])
    J("HubBar").removeAll()


S = H.Spec(name="SkyyBazaar", version=VERSION, pkg=PKG, hub="market", tab="bazaar", mod="SkyyBazaar", open_cls="BzHubOpen", vis_cls=None,
           page_cls="BzPage", prefix="SkyyBzF", idp="SkyyBz", plugin_cls="SkyyBazaarPlugin", register_call="BzHubOpen.register",
           register=lambda J: J("BzHubOpen").register(), prep=prep, fail_text="could not open right now",
           clicks=[('{"a":"next"}', chk_next), ('{"a":"find","@BzFind":"log"}', chk_find)], extra_hub=extra_hub,
           jar=os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyBazaar-%s.jar" % VERSION))), old_jar=os.path.join(HERE, "SkyyBazaar-0.1.12.jar"),
           scratch=os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "hubsH3bcd", "bazaar"))), script=__file__,
           added=["HubBar", "BzHubOpen"],
           expect={"BzPage": ["+m hubAck", "+m hubClick", "~m render", "~m handleDataEvent"], "SkyyBazaarPlugin": ["~m setup", "~m shutdown"],
                   "CfgFn": ["~m opExport"], "CfgRows": ["~m header"]})

if __name__ == "__main__":
    H.run(S)
