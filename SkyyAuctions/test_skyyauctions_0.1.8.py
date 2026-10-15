"""Harness for SkyyAuctions 0.1.8 (HUBS H3b: the Market > Auctions tab; tools/auctions_0_1_8_patch.py). Build first:
python tools/auctions_0_1_8_patch.py && python SkyyAuctions/build_skyyauctions_0.1.8.py

    python SkyyAuctions/test_skyyauctions_0.1.8.py [--dir <folder inside tools/dev/scratch/>] [--keep]

The phases are tools/hub_tab_harness.py's (A verify, C compare 0.1.7 -> 0.1.8 + the kit bytes, HUB executed: REG / PAGE / CLICK / DROP,
D live: two opens on a scratch COPY of the live Skyy_SkyyAuctions (its listings loaded as setup() loads them), AA engine-access audit),
plus here:
  PAGE  every view in the hub shell (Browse, Create BIN, Manage): the full page_check each (fits 1080p, the body under the strip), the
        26 px purse line instead of the 0.1.7 title row (no #SkyyAhTitle; the purse text kept), 1128 x 966
  CLICK the Manage nav button (a non-hub click) switches the view on the same hub page
Exit code 1 on any failure.
"""
import os, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK
import hub_tab_harness as H

VERSION = "0.1.8"
PKG = "com.skyy.auctions."


def prep(E, J, home):
    from jpype import JClass
    J("AhUtil").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyAuctions")
    d = E.Paths.get(home)
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


def chk_manage(K, E, J, P, before, after, f0):
    K.check(after is not None and str(after.getClass().getSimpleName()) == "AhPage" and str(after.view) == "manage" and len(E.sent(P)) > f0,
            "CLICK: the Manage nav button (not a hub click) switches the view on the page (%s)" % (None if after is None else after.view))


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
        K.check(not [c for c in cm if (c[2] and "#SkyyAhTitle " in c[2]) or (c[1] and "SkyyAhTitle" in c[1])], "PAGE %s: no 0.1.7 title row label" % view)
        top = [c for c in cm if c[2] and c[2].startswith("Group #SkyyAhTop ")]
        purse = [c for c in cm if c[2] and "#SkyyAhPurse " in c[2]]
        K.check(len(top) == 1 and "Height: 26" in top[0][2] and len(purse) == 1, "PAGE %s: the purse line is 26 px, the purse kept" % view)
        K.check("Width: 1128, Height: 966" in cm[0][2], "PAGE %s: 1128 x 966" % view)
    J("HubBar").removeAll()


S = H.Spec(name="SkyyAuctions", version=VERSION, pkg=PKG, hub="market", tab="auctions", mod="SkyyAuctions", open_cls="AhHubOpen", vis_cls=None,
           page_cls="AhPage", prefix="SkyyAhF", idp="SkyyAh", plugin_cls="SkyyAuctionsPlugin", register_call="AhHubOpen.register",
           register=lambda J: J("AhHubOpen").register(), prep=prep,
           # the 0.1.7 page's own hand-made placeholders (live since 0.1.3, seen in game): only the kit's stricter inline-text rule refuses them
           legacy_texts=["Search items or sellers...", "e.g. 12000 or 12k"], clicks=[('{"a":"nav:manage"}', chk_manage)], extra_hub=extra_hub,
           jar=os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyAuctions-%s.jar" % VERSION))),
           old_jar=os.path.join(HERE, "SkyyAuctions-0.1.7.jar"),
           scratch=os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "hubsH3bcd", "auctions"))), script=__file__,
           added=["HubBar", "AhHubOpen"],
           expect={"AhPage": ["+m hubAck", "+m hubClick", "~m render", "~m renderTop", "~m handleDataEvent"], "SkyyAuctionsPlugin": ["~m setup", "~m shutdown"],
                   "AhCmds": ["~m status"],          # /ahadmin status names the version
                   "CfgFn": ["~m opExport"], "CfgRows": ["~m header"]})

if __name__ == "__main__":
    H.run(S)
