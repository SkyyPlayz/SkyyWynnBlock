"""Harness for SkyyExploration 0.2.10 (HUBS H3c: the World > Explore tab; tools/exploration_0_2_10_patch.py). Build first:
python tools/exploration_0_2_10_patch.py && python SkyyExploration/build_skyyexploration_0.2.10.py

    python SkyyExploration/test_skyyexploration_0.2.10.py [--dir <folder inside tools/dev/scratch/>] [--keep]

The phases are tools/hub_tab_harness.py's (A verify, C compare 0.2.9 -> 0.2.10 + the kit bytes, HUB executed: REG / PAGE / CLICK / DROP,
D live: two opens on a scratch COPY of the live Skyy_SkyyExploration as one of its own players, AA engine-access audit), plus here:
  PAGE  all four explore tabs (Overview, Zones, Titles, Checklist) in the hub shell: the full page_check each (fits 1080p: 1134 x 972,
        the body under the strip); the explore page's own tab row is still there
  CLICK an explore tab button (a non-hub click) still switches the tab on the same page; a hub click within 1 s of a build is still a
        hub click (the bar is asked FIRST, before the page's 1 s click guard)
Exit code 1 on any failure.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK
import hub_tab_harness as H

VERSION = "0.2.10"
PKG = "com.skyy.explore."


def prep(E, J, home):
    from jpype import JClass
    J("ExGuard").STOP = False
    J("ExGuard").EXEC = E.U.allocateInstance(E.RecEx.class_)      # a recording scheduler: the page check is queued, never run
    J("ExpCfg").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyExploration")
    b = E.Paths.get(home)
    J("ExpCfg").FILE = b.resolve("config.properties")
    J("ExpStore").DIR = b.resolve("players")
    J("ChestReg").DIR = b.resolve("chests")
    J("SpotReg").DIR = b.resolve("worlds")
    J("ExpIO").ADMIN = b.resolve("admin.log")
    J("LgReg").DIR = b.resolve("luggage")
    J("ExpCfg").load()
    J("ChestReg").loadAll()
    J("SpotReg").loadAll()


def live_player(home):
    d = os.path.join(home, "players")
    for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        if f.endswith(".properties") and len(f) == len("00000000-0000-0000-0000-000000000000.properties"):
            return f[:-len(".properties")], "SkyyLive"
    return None


def chk_tab(K, E, J, P, before, after, f0):
    K.check(after is not None and str(after.getClass().getSimpleName()) == "ExplorePage" and int(after.tab) == 2 and len(E.sent(P)) > f0,
            "CLICK: an explore tab button (not a hub click) switches to Titles on the same page")


def chk_hubfast(K, E, J, P, before, after, f0):
    K.check(after is None, "CLICK: a hub click right after a build (inside the page's 1 s guard) is still a hub click (the X closed the page)")


def extra_hub(K, W, J):
    from jpype import JClass
    E = W.E
    J("ExpHubOpen").register()
    X = W.O
    E.br.put("hub:last:" + str(X.pr.getUuid()), JClass("java.util.concurrent.ConcurrentHashMap")())
    for t, name in enumerate(("Overview", "Zones", "Titles", "Checklist")):
        pg = J("ExplorePage")(X.pr, t)
        X.pm.openCustomPage(X.ref, X.st, pg)
        E.pump(X)
        cm, _ev = H.page_check(K, E, S, X, pg, J("HubBar"), "PAGE %s" % name)
        K.check("Width: 1134, Height: 972" in cm[0][2] and any(c[2] and "#SkyyExTab3 " in c[2] for c in cm),
                "PAGE %s: 1134 x 972 with the explore page's own tab row" % name)
    J("HubBar").removeAll()


S = H.Spec(name="SkyyExploration", version=VERSION, pkg=PKG, hub="world", tab="explore", mod="SkyyExploration", open_cls="ExpHubOpen",
           vis_cls=None, page_cls="ExplorePage", prefix="SkyyExF", idp="SkyyEx", plugin_cls="SkyyExplorationPlugin",
           register_call="ExpHubOpen.register", register=lambda J: J("ExpHubOpen").register(), prep=prep, live_player=live_player,
           ack_mark="#SkyyExMsg.Text",   # review fix: a handled hub click is answered by answer() (the result line set to itself)
           clicks=[('{"a":"extab2"}', chk_tab), ('{"a":"hub:close"}', chk_hubfast)], extra_hub=extra_hub,
           jar=os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyExploration-%s.jar" % VERSION))),
           old_jar=os.path.join(HERE, "SkyyExploration-0.2.9.jar"),
           scratch=os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "hubsH3bcd", "explore"))), script=__file__,
           added=["HubBar", "ExpHubOpen"],
           expect={"ExplorePage": ["+m hubClick", "~m build", "~m handleDataEvent"], "SkyyExplorationPlugin": ["~m setup", "~m shutdown"],
                   "CfgFn": ["~m opExport"],
                   # the version texts: the config.properties header (ExpCfg.load / CfgRows <clinit>) and ExpLgMig.WHO (inlined, its log line)
                   "CfgRows": ["~<clinit>", "~m header"], "ExpCfg": ["~m load"], "ExpLgMig": ["~m logLine", "~m migrate"]})

if __name__ == "__main__":
    H.run(S)
