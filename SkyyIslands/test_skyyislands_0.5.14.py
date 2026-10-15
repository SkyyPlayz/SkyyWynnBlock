"""Harness for SkyyIslands 0.5.14 (HUBS H3c: the World > Island tab; tools/islands_0_5_14_patch.py). Build first:
python tools/islands_0_5_14_patch.py && python SkyyIslands/build_skyyislands_0.5.14.py

    python SkyyIslands/test_skyyislands_0.5.14.py [--jar <jar>] [--dir <folder inside tools/dev/scratch/>] [--keep]

The phases are tools/hub_tab_harness.py's (A verify, C compare 0.5.13 -> 0.5.14 + the kit bytes, HUB executed: REG / PAGE / CLICK / DROP,
D live: two opens on a scratch COPY of the live Skyy_SkyyIslands as one of its own island owners, AA engine-access audit), plus here:
  PAGE  an island owner's menu: all five tabs (Overview, Members, Permissions - the tallest -, Visitors, Island) in the hub shell, the full
        page_check each (1254 x 980 = the most; the body under the strip); the window title leads the role line ("<name>'s Island      Your
        role: ..."), no #SkyyIsL0, no footer (#SkyyIsBottom / #SkyyIsClose gone), Refresh (#SkyyIsRef, "refresh") at the end of the tab row
  CLICK an island tab button and Refresh (non-hub clicks) still act on the same page; the page id is the one the patch pins
Exit code 1 on any failure.
"""
import os, sys, re, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK
import hub_tab_harness as H

VERSION = "0.5.14"
PKG = "com.skyy.islands."


def prep(E, J, home):
    from jpype import JClass
    J("IslandStore").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyIslands")
    b = E.Paths.get(home)
    J("IslandStore").DIR = b.resolve("islands")
    J("IslandCfg").FILE = b.resolve("config.properties")
    J("IslandCfg").load("Cow,Sheep,Pig,Chicken")
    J("IslandStore").HUB_FILE = b.resolve("hub.properties")
    J("IslandStore").loadHub()
    J("IslandStore").loadIslandWorlds()
    J("IslandStore").STOPPING = False


def live_player(home):
    d = os.path.join(home, "islands")
    for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        if f.endswith(".properties") and len(f) == len("00000000-0000-0000-0000-000000000000.properties"):
            return f[:-len(".properties")], "SkyyLive"
    return None


def chk_tab(K, E, J, P, before, after, f0):
    K.check(after is not None and str(after.getClass().getSimpleName()) == "IslandMenuPage" and int(after.tab) == 2 and len(E.sent(P)) > f0,
            "CLICK: an island tab button (not a hub click) switches to Permissions on the same page")


def chk_refresh(K, E, J, P, before, after, f0):
    K.check(after is not None and str(after.getClass().getSimpleName()) == "IslandMenuPage" and len(E.sent(P)) > f0,
            "CLICK: Refresh (now in the tab row; not a hub click) redraws the island menu")


def sets_of(cm):
    out = {}
    for ty, s, t, d in cm:
        if ty == "Set":
            try:
                v = json.loads(d)
                out[s] = str(v.get("0", v)) if isinstance(v, dict) else str(v)
            except Exception:
                out[s] = str(d)
    return out


def extra_hub(K, W, J):
    import zipfile
    from jpype import JClass
    E = W.E
    J("IslandHubOpen").register()
    X = W.O
    u = X.pr.getUuid()
    E.br.put("hub:last:" + str(u), JClass("java.util.concurrent.ConcurrentHashMap")())
    IS = J("IslandStore")
    s = IS.settings(IS.homeKey(u))
    s.world = "skyy-island-harness"                     # in memory only: the menu shows the owner's full island
    for t, name in enumerate(("Overview", "Members", "Permissions", "Visitors", "Island")):
        pg = J("IslandMenuPage")(X.pr)
        pg.tab = t
        X.pm.openCustomPage(X.ref, X.st, pg)
        E.pump(X)
        cm, evs = H.page_check(K, E, S, X, pg, J("HubBar"), "PAGE %s" % name)
        st = sets_of(cm)
        role = st.get("#SkyyIsL1.Text", "")
        K.check(role.endswith("") and "'s Island      Your role: " in role, "PAGE %s: the window title leads the role line (%s)" % (name, role[:50]))
        K.check(not [c for c in cm if (c[1] and "SkyyIsL0" in c[1]) or (c[2] and "#SkyyIsL0 " in c[2])], "PAGE %s: no #SkyyIsL0" % name)
        K.check(not [c for c in cm if c[2] and ("#SkyyIsBottom " in c[2] or "#SkyyIsClose " in c[2])], "PAGE %s: no footer row" % name)
        K.check(any(c[1] == "#SkyyIsTabs" and c[2] and "#SkyyIsRef " in c[2] for c in cm) and any(sel == "#SkyyIsRef" and "refresh" in tx for sel, tx in evs),
                "PAGE %s: Refresh at the end of the tab row, bound to refresh" % name)
        K.check("Width: 1254, Height: 980" in cm[0][2], "PAGE %s: 1254 x 980" % name)
    gen = open(os.path.join(HERE, "build_skyyislands_%s.py" % VERSION), encoding="utf8").read()
    m = re.search(r'IS_PAGE_CHECKED = "([0-9a-f]{12})"', gen)
    data = zipfile.ZipFile(S.jar).read("com/skyy/islands/SkyyIslandsPlugin.class")
    K.check(m is not None and ("page " + m.group(1)).encode() in data, "PAGE: the built page id = IS_PAGE_CHECKED %s (the 0.5.4 page gate)" % (m and m.group(1)))
    J("HubBar").removeAll()


S = H.Spec(name="SkyyIslands", version=VERSION, pkg=PKG, hub="world", tab="island", mod="SkyyIslands", open_cls="IslandHubOpen", vis_cls=None,
           page_cls="IslandMenuPage", prefix="SkyyIsF", idp="SkyyIs", plugin_cls="SkyyIslandsPlugin", register_call="IslandHubOpen.register",
           register=lambda J: J("IslandHubOpen").register(), prep=prep, live_player=live_player,
           # 0.5.13's own button labels (kbtn: inline through safe(), live since 0.5.4 and seen in game): only the kit's stricter
           # inline-text rule refuses the brackets
           legacy_texts=["Trust (build only)", "Public (anyone)", "Closed (members only)", "Friends (members + trusted)", "+"],
           clicks=[('{"a":"tabperm"}', chk_tab), ('{"a":"refresh"}', chk_refresh)], extra_hub=extra_hub,
           jar=os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyIslands-%s.jar" % VERSION))), old_jar=os.path.join(HERE, "SkyyIslands-0.5.13.jar"),
           scratch=os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "hubsH3bcd", "islands"))), script=__file__,
           added=["HubBar", "IslandHubOpen"],
           expect={"IslandMenuPage": ["+m hubAck", "+m hubClick", "~m build", "~m buildTabs", "~m handleDataEvent"],
                   "SkyyIslandsPlugin": ["~m setup", "~m shutdown"], "CfgFn": ["~m opExport"],
                   # the config.properties header names the version (IslandCfg.load / CfgRows <clinit>)
                   "CfgRows": ["~<clinit>", "~m header"], "IslandCfg": ["~m load"]})

if __name__ == "__main__":
    H.run(S)
