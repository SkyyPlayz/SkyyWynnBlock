"""Harness for SkyyMenu 0.3.28 (hubs H2: the hub registry, Menu's own tabs in the Sky Window hub shell, the hub commands, hub:last;
tools/menu_0_3_28_patch.py). Build first: python tools/menu_0_3_28_patch.py && python SkyyMenu/build_skyymenu_0.3.28.py

    python SkyyMenu/test_skyymenu_0.3.28.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py: the game's JRE, the cached HytaleServer.jar, -XX:-UsePerfData, TEMP / TMP in the scratch
folder; the hub phase runs with -Xverify:all over the SkyyMenu 0.3.19 harness's engine stand-ins: a recording packet sink, a component
store, worlds, the Universe, the REAL PageManager / WindowManager, a command manager that records lines, a permissions provider with a
plain player (hytale:Adventurer) and an op (hytale:Admin = "*")):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.27 -> 0.3.28: exactly the listed members differ, + HubBar, MenuHub, MenuHubOpen, MenuHubVis and the 5 hub commands;
                non-class entries: manifest.json + the 59 Sky Window kit files (Common/UI/Custom/SkyyKit/, = the kit's pinned bytes)
  HUB  EXECUTED:
       REG   MenuHub.register(): hub:def:<hub> for the 7 hubs = {title, command, icon item} (SUI.HUB_DEFS + our icon items), Menu's 7 tabs
             = Object[]{"SkyyMenu", label, Integer order, command or null, open Function, visible Function or null} with the contract's
             labels / orders (SUI.HUB_TABS); visibility: Mods (admins, or everyone while menu.modsHelp is on), Server Setup (admins)
       PAGE  every Menu tab opened through its open Function (HubBar.open -> "bridge") into the real PageManager, then built into a REAL
             UICommandBuilder / UIEventBuilder: markup rules + every parent exists + no duplicate id (SUI.check_page), every texture a
             kit SkyyKit element inside Common/UI/Custom or a verified vanilla path (no ../), the root <= 1600 x 980, assert_hub_page +
             assert_hub_fits for the hub, the body fits under the strip (used_height), the Header + HeaderOrnament crest + the hub's Frame
             mood, "< Menu" INSIDE the title bar, the close X, one tab per visible tab at hub_tab_width (>= 110, 16 px label that shrinks to
             12), the active tab selected, bindings hub:back / hub:close / hub:<tab>, every b.set / binding names an element that exists
             (a missing element disconnects the client), hub:last remembers the tab
       CLICK the hub bar on every page: the X closes, "< Menu" opens the SkyWynn Menu (the menu views: the main view in place), the active
             tab redraws (a player's page -> the players list), Mods <-> Menu layout switch in place on the same page, another Menu tab
             opens through its Function (the menu grid emptied first), a hidden tab (Server Setup for a plain player) says it could not
             open, the locked Server Setup page's bar works; an H3 tab of another mod (a bridge Function / a command fallback / hidden)
       CMD   /character (/char), /storage, /market, /travel, /social: hytale:Adventurer on each, the hub's first tab, then its last tab,
             a hub with no tab says coming soon (no page), a stale hub:last falls back to the first tab
       LAST  hub:last:<uuid> made at join (MenuReady / ensure), removed on disconnect (MenuQuit executed), by the 30 s upkeep for players
             gone (sweep) and at shutdown (clearAll: hub:def + Menu's tabs + hub:last gone, another mod's tab kept); the plugin's setup /
             shutdown call register / the 5 commands / clearAll (bytecode)
  D    live     two starts on a scratch COPY of the live Skyy_SkyyMenu: register, every Menu tab page opened + built, clearAll - no file
                written by either start
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, json, time, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import skyyui as SUI

_s19 = importlib.util.spec_from_file_location("test_skyymenu_0_3_19", os.path.join(HERE, "test_skyymenu_0.3.19.py"))
T19 = importlib.util.module_from_spec(_s19)
_s19.loader.exec_module(T19)

VERSION = "0.3.28"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.27.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "hubsH2", "menu")))
PKG = "com.skyy.menu."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyMenu")
ADDED = ["HubBar", "MenuHub", "MenuHubOpen", "MenuHubVis", "HubCharCmd", "HubStorageCmd", "HubMarketCmd", "HubTravelCmd", "HubSocialCmd"]
EXPECT = {
    "MenuData": ["~<clinit>", "+f ADM_SUBMAX", "+f HT_CMD", "+f HT_HUB", "+f HT_LABEL", "+f HT_ORDER", "+f HT_TAB", "+f HT_VIS",
                 "+f ADM_PREFIX", "+f HUB_CMD", "+f HUB_ICON", "+f HUB_ID", "+f HUB_INFO_LINES", "+f HUB_SOON", "+f HUB_TITLE", "+f HUB_TXT_FAIL",
                 "+f UI_HINTST", "+f UI_INFOBOXH", "+f UI_SHINTST", "+f UI_SGAP3", "-f UI_AACCENT", "-f UI_AROOT", "-f UI_ATITLE",
                 "-f UI_SACCENT", "-f UI_SGAP6", "-f UI_SROOT", "-f UI_SSTATUS", "-f UI_STITLE"],
    "MenuPage": ["+m hubMode", "+m hubName", "+m hubTab", "+m hubClick", "~m build", "~m handleDataEvent", "~m startEdit"],
    "StatsPage": ["~m build", "~m handleDataEvent"],
    "SettingsPage": ["~m build", "~m handleDataEvent"],
    "AdminPage": ["~m frame", "~m tail", "+m hubAfter", "~m handleDataEvent", "~m lockedClick"],
    "MenuReady": ["~m accept"],
    "MenuQuit": ["~m accept"],
    "SeenTick": ["~m run"],
    "SkyyMenuPlugin": ["~m setup", "~m shutdown"],
    "CfgFn": ["~m opExport"],          # the version texts
    "CfgRows": ["~m header"],
    "OpsPage": ["~<clinit>"],          # the mod versions the Admin page lists (read from the newest build scripts at build time)
}
KIT_FILES = sorted(SUI.SKY_JAR_DIR + f[0] for f in SUI.SKY_FILES)
if HK.arg("--phase") == "compare":
    _eq0 = HK.Child.eq

    def _eq(self, got, want, what):
        if what == "C: non-class entries changed" and want == ["manifest.json"]:
            return self.check(sorted(got) == sorted(["manifest.json"] + KIT_FILES),
                              "C: non-class entries changed = manifest.json + the 59 kit files (%d entries)" % len(got))
        if what.startswith("C: ") and what.endswith(" members") and isinstance(want, list):
            # members whose CODE did not change but whose order / constant moved are tolerated only when listed
            pass
        return _eq0(self, got, want, what)
    HK.Child.eq = _eq

OWN = [(h, t, o, l, c) for h, t, o, m, l, c in SUI.HUB_TABS if m == "SkyyMenu"]
OWN_VIS = ("mods", "setup")
ICONS = {"character": "Skyy_Menu_Icon_YourProfile", "storage": "Skyy_Menu_Icon_PocketDimension", "market": "Skyy_Menu_Icon_Bazaar",
         "smithing": "Skyy_Menu_Icon_Reforge", "world": "Skyy_Menu_Icon_Teleport", "social": "Skyy_Menu_Icon_Players",
         "settings": "Skyy_Menu_Icon_Settings"}
# tab -> (hub, page class, view, editing, page prefix (the shell), id prefix, strip width)
PAGES = {"stats": ("character", "StatsPage", None, None, "SkyyStatF", "SkyyStat", 1066),
         "teleport": ("world", "MenuPage", "tp", False, "SkyyMenuH", "SkyyM", 756),
         "players": ("social", "MenuPage", "players", False, "SkyyMenuH", "SkyyM", 756),
         "settings": ("settings", "SettingsPage", None, None, "SkyyStgH", "SkyyStg", 1080),
         "layout": ("settings", "MenuPage", "main", True, "SkyyMenuH", "SkyyM", 756),
         "mods": ("settings", "MenuPage", "mods", False, "SkyyMenuH", "SkyyM", 756),
         "setup": ("settings", "AdminPage", None, None, "SkyyAdmH", "SkyyAdm", 1080)}


def jf(c, name):
    while c is not None:
        try:
            f = c.getDeclaredField(name)
            f.setAccessible(True)
            return f
        except Exception:
            c = c.getSuperclass()
    raise KeyError(name)


def cmds_of(b):
    """the commands of a real UICommandBuilder: [(type, selector or None, text, data)]"""
    out = []
    for c in list(b.getCommands()):
        g = lambda n: (lambda v: None if v is None else str(v))(jf(c.getClass(), n).get(c))
        out.append((g("type"), g("selector"), g("text"), g("data")))
    return out


def events_of(ev):
    """every binding of a UIEventBuilder as (selector, the binding's text)"""
    from jpype import JClass
    out = []
    Coll = JClass("java.util.Collection")
    for f_ in ev.getClass().getDeclaredFields():
        f_.setAccessible(True)
        v_ = f_.get(ev)
        if v_ is None or not Coll.class_.isInstance(v_):
            continue
        for e in list(v_):
            sel, parts = None, []
            c = e.getClass()
            while c is not None and str(c.getName()) != "java.lang.Object":
                for g in c.getDeclaredFields():
                    try:
                        g.setAccessible(True)
                        x = g.get(e)
                        if x is None:
                            continue
                        if str(g.getName()) == "selector":
                            sel = str(x)
                        parts.append(str(x))
                        for h in x.getClass().getDeclaredFields():
                            try:
                                h.setAccessible(True)
                                y = h.get(x)
                                if y is not None:
                                    parts.append(str(y))
                            except Exception:
                                pass
                    except Exception:
                        pass
                c = c.getSuperclass()
            out.append((sel, " | ".join(parts)))
    return out


DECL_RE = re.compile(r"\b([A-Za-z]+) #([A-Za-z0-9]+) \{")
WH_RE = re.compile(r"Anchor: \(Width: (\d+), Height: (\d+)\)")


def page_check(K, E, P, page, tab, what):
    """build the page into REAL builders and check it as a hub page (see PAGE in the docstring); returns (cmds, events)"""
    from jpype import JClass
    hub, _cls, _v, _e, prefix, idp, strip = PAGES[tab]
    b = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")()
    ev = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")()
    page.build(P.ref, b, ev, P.st)
    cmds = cmds_of(b)
    evs = events_of(ev)
    apps = SUI.Appends([(None if s is None else s.lstrip("#"), t) for ty, s, t, d in cmds if t is not None and ty and "Append" in ty])
    sets = [(s, d) for ty, s, t, d in cmds if ty == "Set"]
    K.check(len(apps) > 10 and len(apps) + len(sets) == len(cmds), "%s: %d appends + %d sets (%s)" % (what, len(apps), len(sets),
            sorted(set(ty for ty, _s, _t, _d in cmds))))
    try:
        SUI.check_page(apps, idp)
        K.check(True, "%s: check_page (markup rules, parents, no duplicate id)" % what)
    except Exception as e:
        K.check(False, "%s: check_page: %s" % (what, e))
    try:
        els = SUI.check_sky_paths(apps)
        allp = [m.group(0) for mk in apps.markups() for m in SUI._SKY_PATH_RE.finditer(SUI.render(mk))]
        K.check(not [p for p in allp if p.startswith('"../')], "%s: no texture path leaves Common/UI/Custom (%d paths)" % (what, len(allp)))
        nvis = len(E.hubTabs(hub, P.pr.getUuid()))
        K.check({"Header", "HeaderOrnament", SUI.HUB_FRAME[hub], "Close", "Tertiary", "Tab_Selected"} | ({"Tab"} if nvis > 1 else set()) <= set(els),
                "%s: the Sky Window shell: Header + crest + %s + close X + < Menu + tabs (%s)" % (what, SUI.HUB_FRAME[hub], els))
    except Exception as e:
        K.check(False, "%s: sky paths: %s" % (what, e))
    root = apps[0][1]
    m = WH_RE.search(root)
    w, h = int(m.group(1)), int(m.group(2))
    K.check(apps[0][0] is None and root.startswith("Group #%s " % prefix), "%s: the root is the hub shell #%s" % (what, prefix))
    try:
        SUI.assert_page_size(w, h)
        K.eq(SUI.assert_hub_page(w, h - SUI.HUB_BAR_H, old_title_h=0, hub=hub, pad=24), (w, h), "%s: assert_hub_page %d x %d" % (what, w, h))
        K.check(SUI.assert_hub_fits(hub, strip) >= 110 and strip == w - 48, "%s: assert_hub_fits %s in %d px (every contract tab)" % (what, hub, strip))
    except Exception as e:
        K.check(False, "%s: page size: %s" % (what, e))
    body = [p for p, mk in apps if mk.startswith("Group #%sBody ") or (p == prefix and "Top: 38" in mk)]
    bid = [DECL_RE.search(mk).group(2) for p, mk in apps if p == prefix and "Anchor: (Top: 38)" in mk]
    K.check(len(bid) == 1, "%s: one body under the title bar (%s)" % (what, bid))
    if bid:
        try:
            used = SUI.used_height(apps, bid[0])
            K.check(used <= h - SUI.TITLE_H - 48, "%s: the body content fits under the strip (%d <= %d)" % (what, used, h - SUI.TITLE_H - 48))
        except Exception as e:
            K.check(False, "%s: used_height: %s" % (what, e))
    bar = [mk for p, mk in apps if p == prefix + "Bar"]
    K.check(any(("#%sHubMenu " % prefix) in mk and '"< Menu"' in mk for mk in bar), "%s: < Menu sits INSIDE the title bar #%sBar" % (what, prefix))
    K.check([p for p, mk in apps if ("#%sHubClose " % prefix) in mk] == [prefix], "%s: the close X in the root" % what)
    tabs = [mk for p, mk in apps if p == prefix + "HubTabs" and mk.startswith("TextButton")]
    vis = [str(r[0]) for r in E.hubTabs(hub, P.pr.getUuid())]
    K.eq(len(tabs), len(vis), "%s: one tab per visible tab %s" % (what, vis))
    tw = SUI.hub_tab_width(strip, max(1, len(vis)))
    K.check(all(("Width: %d, Height: 44" % tw) in mk and "ShrinkTextToFit: true" in mk and "MinShrinkTextToFitFontSize: 12" in mk
                and "FontSize: 16" in mk for mk in tabs) and tw >= 110, "%s: tabs %d px wide (>= 110), 16 px labels that shrink to 12" % (what, tw))
    sel = [mk for mk in tabs if "Tab_Selected" in mk]
    lab = dict((t, l) for h_, t, o, l, c in OWN)
    K.check(len(sel) == 1 and ('Text: "%s"' % lab.get(tab, tab)) in sel[0], "%s: the active tab %s is selected" % (what, tab))
    bs = [s for s, _t in evs]
    K.check(("#%sHubMenu" % prefix) in bs and ("#%sHubClose" % prefix) in bs, "%s: < Menu and the X are bound" % what)
    K.check(any("hub:back" in t for s, t in evs if s == "#%sHubMenu" % prefix) and any("hub:close" in t for s, t in evs if s == "#%sHubClose" % prefix),
            "%s: < Menu = hub:back, the X = hub:close" % what)
    for k, t in enumerate(vis):
        K.check(any(("hub:" + t) in tx for s, tx in evs if s == "#%sHubT%d" % (prefix, k)), "%s: tab %d bound to hub:%s" % (what, k, t))
    ids = set()
    for _p, mk in apps:
        ids |= set(x.group(2) for x in DECL_RE.finditer(SUI.render(mk)))
    bad = [s for s, _d in sets if s.lstrip("#").split(".")[0] not in ids] + [s for s in bs if s.lstrip("#") not in ids]
    K.check(not bad, "%s: every b.set and binding names an element that exists (%d sets, %d bindings): %s" % (what, len(sets), len(bs), bad[:4]))
    last = E.bridge().get("hub:last:" + str(P.pr.getUuid()))
    K.check(last is not None and str(last.get(hub)) == tab, "%s: hub:last remembers %s -> %s" % (what, hub, tab))
    return cmds, evs


def run_hub(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JArray, JObject, JImplements, JOverride
    K = HK.Child(out)
    hcls = os.path.join(scratch, "hcls_hub")
    os.makedirs(hcls, exist_ok=True)
    os.chdir(scratch)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, hcls, jar], verify=True)
    E = T19.engine(scratch, hcls)
    JV = lambda n: JClass(PKG + n)
    Paths = E.Paths
    home = os.path.join(scratch, "home_hub")
    os.makedirs(home, exist_ok=True)
    JV("PageGuard").STOP = False
    JV("PageGuard").EXEC = None
    JV("MenuLayout").DIR = Paths.get(os.path.join(home, "layouts"))
    JV("MenuLayout").DEF_FILE = Paths.get(os.path.join(home, "layout-default.properties"))
    JV("SetStore").DIR = Paths.get(os.path.join(home, "settings"))
    JV("SetReg").ADMIN_FILE = Paths.get(os.path.join(home, "settings-defaults.properties"))
    JV("SetReg").registerOwn()
    HB, MH, MD = JV("HubBar"), JV("MenuHub"), JV("MenuData")
    br = JV("MenuUtil").bridge()
    E.bridge = lambda: br
    E.hubTabs = lambda hub, u: [list(x) for x in HB.tabs(hub, u)]
    SysC = JClass("java.lang.System")

    def same(a, b_):
        if a is None or b_ is None:
            return a is None and b_ is None
        return int(SysC.identityHashCode(a)) == int(SysC.identityHashCode(b_))
    K.check(same(HB.map(), br), "the kit HubBar and MenuUtil share ONE bridge map (skyy.bridge)")
    UniC = JClass("com.hypixel.hytale.server.core.universe.Universe")
    uni = UniC.get()
    byU = jf(UniC.class_, "playersByUuid").get(uni)
    TRUE, FALSE = JClass("java.lang.Boolean").TRUE, JClass("java.lang.Boolean").FALSE
    Fn = JClass("java.util.function.Function")

    def mkp(uid, name):
        P = E.player(uid, name=name)
        byU.put(uid, P.pr)
        E.UniH.PL.add(P.pr)
        E.PLAYERS.add(P.pr)          # Universe.getPlayers() (the engine's own list: SoundSw.live, the upkeep's fresh online list)
        return P
    P = mkp(E.PLAIN, "SkyyPlain")
    O = mkp(E.OP, "SkyyOp")
    u, uo = P.pr.getUuid(), O.pr.getUuid()
    PGM = lambda X: X.pm.getCustomPage()

    # ---------------------------------------------------------------- REG
    n = int(MH.register())
    K.eq(n, 7, "REG: Menu's 7 own tabs put")
    for i, hub in enumerate(SUI.HUBS):
        d = br.get("hub:def:" + hub)
        K.check(d is not None and len(d) == 3 and [str(x) for x in d] == [SUI.HUB_DEFS[hub][0], SUI.HUB_DEFS[hub][1], ICONS[hub]],
                "REG: hub:def:%s = {title, command, icon} %s" % (hub, None if d is None else [str(x) for x in d]))
    for hub, tab, order, label, cmd in OWN:
        e = br.get("hub:tab:%s:%s" % (hub, tab))
        ok = e is not None and len(e) == 6 and str(e[0]) == "SkyyMenu" and str(e[1]) == label and JClass("java.lang.Integer").class_.isInstance(e[2]) \
            and int(e[2]) == order and (str(e[3]) if e[3] is not None else None) == cmd and Fn.class_.isInstance(e[4]) \
            and str(e[4].getClass().getName()) == PKG + "MenuHubOpen" \
            and ((e[5] is not None and str(e[5].getClass().getName()) == PKG + "MenuHubVis") if tab in OWN_VIS else e[5] is None)
        K.check(ok, "REG: hub:tab:%s:%s = {SkyyMenu, %s, %d, %s, open, %s}" % (hub, tab, label, order, cmd, "visible" if tab in OWN_VIS else "null"))
    K.eq([str(x[0]) for x in E.hubTabs("settings", u)], ["settings", "layout", "mods"], "VIS: a plain player sees Settings, Menu layout, Mods (modsHelp on)")
    JV("MenuCfg").MODS_HELP = False
    K.eq([str(x[0]) for x in E.hubTabs("settings", u)], ["settings", "layout"], "VIS: modsHelp off -> no Mods tab for a plain player")
    K.eq([str(x[0]) for x in E.hubTabs("settings", uo)], ["settings", "layout", "mods", "setup"], "VIS: an op sees all 4 Menu tabs")
    JV("MenuCfg").MODS_HELP = True
    vis = JV("MenuHubVis")("setup")
    K.check(vis.apply("not a uuid") == FALSE and vis.apply(E.UUID.randomUUID()) == FALSE and vis.apply(uo) == TRUE and vis.apply(u) == FALSE,
            "VIS: MenuHubVis(setup): op TRUE, plain FALSE, offline / not a UUID FALSE")
    K.check(JV("MenuHubOpen")("stats").apply("x") == FALSE and JV("MenuHubOpen")("stats").apply(E.UUID.randomUUID()) == FALSE
            and JV("MenuHubOpen")("nope").apply(u) == FALSE, "OPEN: not a UUID / an offline player / an unknown tab = FALSE (the bar then tries the command)")

    # ---------------------------------------------------------------- PAGE: every Menu tab through its open Function, built and checked
    pages = {}
    for tab in ("stats", "teleport", "players", "settings", "layout", "mods", "setup"):
        hub, cls, view, editing, prefix, idp, strip = PAGES[tab]
        X = O if tab == "setup" else P
        r = str(HB.open(X.pr, X.pr.getUuid(), hub, tab))
        E.pump(X)
        pg = PGM(X)
        ok = r == "bridge" and pg is not None and str(pg.getClass().getName()) == PKG + cls
        if ok and view is not None:
            ok = str(pg.view) == view and bool(pg.editing) == editing and bool(pg.hubMode()) and str(pg.hubName()) == hub and str(pg.hubTab()) == tab
        K.check(ok, "PAGE %s: HubBar.open(%s, %s) = %s -> %s%s" % (tab, hub, tab, r, None if pg is None else pg.getClass().getSimpleName(),
                                                                   "" if view is None else " view %s editing %s" % (view, editing)))
        if pg is not None:
            pages[tab] = page_check(K, E, X, pg, tab, "PAGE %s" % tab)
    # the plain player cannot open Server Setup through the bar
    K.eq(str(HB.open(P.pr, u, "settings", "setup")), "hidden", "PAGE setup: hidden for a plain player (no page)")
    # the menu view texts: the hub views show the status in the hint row, 8 info lines, no title / status label
    lv = pages.get("layout")
    if lv:
        _h = [d for ty, s_, t_, d in lv[0] if ty == "Set" and s_ == "#SkyyMHint.Text"]
        K.check(len(_h) == 1 and "Done to finish." in _h[0] and "no dragging" in _h[0],
                "FIX layout: the editor's status in the hint row ends 'Done to finish.' (%s)" % _h[:1])
    mv = pages.get("teleport")
    if mv:
        sets = dict((s, d) for ty, s, t, d in mv[0] if ty == "Set")
        K.check("#SkyyMTitle.Text" not in sets and "#SkyyMStatus.Text" not in sets and "#SkyyMInfo7.Text" in sets and "#SkyyMInfo8.Text" not in sets,
                "PAGE teleport: no title / status label in the hub shell, 8 info lines")
    # the MAIN view keeps 0.3.27's menu (no hub shell)
    mp = JV("MenuPage")(P.pr, "main")
    P.pm.openCustomPage(P.ref, P.st, mp)
    E.pump(P)
    b0 = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")()
    mp.build(P.ref, b0, JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")(), P.st)
    c0 = cmds_of(b0)
    K.check(not mp.hubMode() and c0[0][2].startswith("Group #SkyyMenu { Anchor: (Width: 800, Height: 952)") and not [c for c in c0 if c[2] and "SkyyKit" in c[2]]
            and any(c[1] == "#SkyyMTitle.Text" for c in c0), "PAGE main view: 0.3.27's menu (800 x 952, its title, no hub shell)")

    # ---------------------------------------------------------------- CLICK
    def openp(X, tab):
        hub = PAGES[tab][0]
        r = str(HB.open(X.pr, X.pr.getUuid(), hub, tab))
        E.pump(X)
        return PGM(X)

    def click(X, pg, a):
        pg.handleDataEvent(X.ref, X.st, '{"a":"%s"}' % a)
        E.pump(X)
        return PGM(X)
    st = openp(P, "stats")
    K.check(same(click(P, st, "hub:stats"), st) and str(st.status) == "", "CLICK stats: its own tab redraws the same page")
    K.check(same(click(P, st, "hub:nothere"), st) and str(st.status) == str(MD.HUB_TXT_FAIL), "CLICK stats: a missing tab says it could not open")
    m = click(P, st, "hub:back")
    K.check(m is not None and str(m.getClass().getSimpleName()) == "MenuPage" and str(m.view) == "main" and not m.editing,
            "CLICK stats: < Menu opens the SkyWynn Menu (main view)")
    st = openp(P, "stats")
    K.check(click(P, st, "hub:close") is None, "CLICK stats: the X closes the page")
    sp = openp(P, "settings")
    K.check(same(click(P, sp, "hub:settings"), sp), "CLICK settings: its own tab keeps the page")
    # FIX: a hub click disarms Reset all (as every other click does) and redraws to clear the "click again" state; with nothing to clear
    # the own tab draws nothing (the bar's click carries no field values - a redraw would drop a search being typed)
    sp.armedAt = int(JClass("java.lang.System").currentTimeMillis())
    sp.status = str(MD.SET_TXT_ARM)
    n0 = len(E.sent(P))
    K.check(same(click(P, sp, "hub:settings"), sp) and int(sp.armedAt) == 0 and str(sp.status) == "" and len(E.sent(P)) > n0,
            "FIX settings: the own tab while Reset all is armed -> disarmed (armedAt 0), status cleared, redrawn")
    sp.armedAt = int(JClass("java.lang.System").currentTimeMillis())
    sp.status = ""
    sp.handleDataEvent(P.ref, P.st, '{"a":"hub:nothere"}')
    E.pump(P)
    K.check(int(sp.armedAt) == 0, "FIX settings: a failed hub click disarms Reset all too")
    sp.status = ""
    n0 = len(E.sent(P))
    K.check(same(click(P, sp, "hub:settings"), sp) and len(E.sent(P)) == n0, "FIX settings: the own tab with nothing to clear sends nothing (a typed search stays)")
    sp.armedAt = int(JClass("java.lang.System").currentTimeMillis())
    sp.status = str(MD.SET_TXT_ARM)
    click(P, sp, "hub:settings")
    sp.handleDataEvent(P.ref, P.st, '{"a":"sreset"}')
    E.pump(P)
    K.check(str(sp.status) == str(MD.SET_TXT_ARM) and int(sp.armedAt) > 0,
            "FIX settings: Reset all, then the Settings tab, then Reset all = armed again, nothing reset (%s)" % sp.status)
    sp.armedAt = 0
    sp.status = ""
    K.check(same(click(P, sp, "hub:setup"), sp) and str(sp.status) == str(MD.HUB_TXT_FAIL), "CLICK settings: Server Setup (hidden for a plain player) says it could not open")
    lay = click(P, sp, "hub:layout")
    K.check(lay is not None and str(lay.getClass().getSimpleName()) == "MenuPage" and lay.editing and lay.hubMode() and str(lay.hubTab()) == "layout",
            "CLICK settings -> Menu layout: the layout editor (in the hub shell)")
    K.check(same(click(P, lay, "hub:mods"), lay) and str(lay.view) == "mods" and not lay.editing, "CLICK layout -> Mods: switched in place (same page)")
    K.check(same(click(P, lay, "hub:layout"), lay) and str(lay.view) == "main" and lay.editing, "CLICK Mods -> layout: switched in place, editing again")
    lay.cleared = False
    sp2 = click(P, lay, "hub:settings")
    K.check(sp2 is not None and str(sp2.getClass().getSimpleName()) == "SettingsPage" and lay.cleared,
            "CLICK layout -> Settings: the SettingsPage opens, the menu grid was emptied first (stuck-tooltip rule)")
    K.check(click(P, sp2, "hub:close") is None, "CLICK settings: the X closes")
    tp = openp(P, "teleport")
    m2 = click(P, tp, "hub:back")
    K.check(same(m2, tp) and str(tp.view) == "main" and not tp.hubMode(), "CLICK teleport: < Menu = the main view IN PLACE (no new page)")
    pl = openp(P, "players")
    pl.selU = uo
    pl.open("player")
    K.check(pl.hubMode() and str(pl.hubTab()) == "players", "CLICK players: a player's page is still Social > Players")
    K.check(same(click(P, pl, "hub:players"), pl) and str(pl.view) == "players", "CLICK players: the Players tab on a player's page -> the players list")
    K.check(click(P, pl, "hub:close") is None, "CLICK players: the X closes (closePage)")
    ap = openp(O, "setup")
    sp3 = click(O, ap, "hub:settings")
    K.check(sp3 is not None and str(sp3.getClass().getSimpleName()) == "SettingsPage", "CLICK server setup (op): the Settings tab opens Settings")
    ap = openp(O, "setup")
    n0 = len(E.sent(O))
    K.check(same(click(O, ap, "hub:setup"), ap) and len(E.sent(O)) == n0,
            "FIX server setup: its own tab keeps the page and sends nothing (typed values / an Import paste stay in their boxes)")
    # FIX: the one-line title drops "Server Setup - " (the tab says it) and shows a real long line whole (ADM_SUBMAX 140, measured)
    K.eq((int(MD.ADM_SUBMAX), str(MD.ADM_PREFIX)), (140, "Server Setup - "), "FIX server setup: ADM_SUBMAX 140, prefix 'Server Setup - '")
    for _t, _s, _want in (("Server Setup - Accessories (SkyyAccessories 0.5.11)", "View only - changing SkyyAccessories needs skyyaccessories.admin.",
                           "Accessories (SkyyAccessories 0.5.11)   -   View only - changing SkyyAccessories needs skyyaccessories.admin."),
                          ("Server Setup - Accessories (SkyyAccessories 0.5.11)", "SkyyAccessories is not running - its settings cannot be changed now.",
                           "Accessories (SkyyAccessories 0.5.11)   -   SkyyAccessories is not running - its settings cannot be changed now."),
                          ("Server Setup", "", "Server Setup"),
                          ("History - config.properties (SkyyAccessories)", "Each config file keeps its newest versions. Preview one, then Restore it - a restore can be undone the same way.",
                           None)):
        bF = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")()
        ap.frame(bF, _t, _s)
        _d = [d for ty, s_, t_, d in cmds_of(bF) if ty == "Set" and s_ == "#SkyyAdmSub.Text"]
        if _want is None:
            _ok = len(_d) == 1 and "..." in _d[0] and "History - config.properties" in _d[0]
            if _ok:
                _vis = _d[0][_d[0].index("History"):_d[0].index("...") + 3]
                _ok = len(_vis) == 140 and SUI.text_width(_vis, 16, bold=True) <= 1080
        else:
            _ok = len(_d) == 1 and _want in _d[0] and "Server Setup - " not in _d[0] and "..." not in _d[0]
        K.check(_ok, "FIX server setup: the title line %r (%s)" % (_want or "History ... cut at 140, fits 1080 px", _d[:1]))
    mm = click(O, ap, "hub:back")
    K.check(mm is not None and str(mm.getClass().getSimpleName()) == "MenuPage" and str(mm.view) == "main", "CLICK server setup: < Menu opens the menu")
    # the LOCKED Server Setup page (a plain player): the bar is drawn and works
    lk = JV("AdminPage")(P.pr, "list", None)
    P.pm.openCustomPage(P.ref, P.st, lk)
    E.pump(P)
    bL = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")()
    eL = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")()
    lk.build(P.ref, bL, eL, P.st)
    cl = cmds_of(bL)
    K.check(lk.locked and any(c[2] and "#SkyyAdmHHubMenu " in c[2] for c in cl) and any(c[1] == "#SkyyAdmHHubTabs" for c in cl),
            "CLICK locked server setup: the hub shell + tab strip are drawn")
    sp4 = click(P, lk, "hub:settings")
    K.check(sp4 is not None and str(sp4.getClass().getSimpleName()) == "SettingsPage", "CLICK locked server setup: the Settings tab still works")
    # H3: another mod's tabs (a bridge Function, a command fallback, a hidden one) on Menu's pages
    seen = []

    @JImplements("java.util.function.Function")
    class F(object):
        def __init__(self, r):
            self.r = r

        @JOverride
        def apply(self, x):
            seen.append(str(x))
            return self.r

    Obj = JClass("java.lang.Object")
    Int = JClass("java.lang.Integer")
    br.put("hub:tab:character:skills", JArray(Obj)(["SkyySkills", "Skills", Int(20), "skills", F(TRUE), None]))
    br.put("hub:tab:character:trees", JArray(Obj)(["SkyyTrees", "Trees", Int(30), "tree", None, None]))
    br.put("hub:tab:character:pets", JArray(Obj)(["SkyyPets", "Pets", Int(50), "pets", F(TRUE), F(FALSE)]))
    st = openp(P, "stats")
    cs, es = page_check(K, E, P, st, "stats", "H3 stats with Skills + Trees (+ a hidden Pets)")
    K.check(len([c for c in cs if c[1] == "#SkyyStatFHubTabs" and c[2] and c[2].startswith("TextButton")]) == 3, "H3: Stats, Skills, Trees drawn; Pets hidden")
    del seen[:]
    K.check(same(click(P, st, "hub:skills"), st) and seen == [str(u)], "H3: Skills -> SkyySkills' open Function gets the UUID (the page is theirs now)")
    E.CM.lines.clear()
    click(P, st, "hub:trees")
    K.check([str(x) for x in E.CM.lines] == ["tree"], "H3: Trees (no open Function) -> its command /tree as the player")
    tp = openp(P, "teleport")
    br.put("hub:tab:world:island", JArray(Obj)(["SkyyIslands", "Island", Int(20), "island menu", None, None]))
    E.CM.lines.clear()
    tp.cleared = False
    click(P, tp, "hub:island")
    K.check([str(x) for x in E.CM.lines] == ["island menu"] and tp.cleared, "H3: World > Island from the Teleport view: grid emptied, /island menu run")
    for k in ("hub:tab:character:skills", "hub:tab:character:trees", "hub:tab:character:pets", "hub:tab:world:island"):
        br.remove(k)

    # ---------------------------------------------------------------- CMD
    APC = JClass("com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand")
    ACM = JClass("com.hypixel.hytale.server.core.command.system.AbstractCommand")

    def groups(c):
        for f_ in ACM.class_.getDeclaredFields():
            f_.setAccessible(True)
            v = f_.get(c)
            if v is not None and JClass("java.util.Collection").class_.isInstance(v) and "hytale:Adventurer" in [str(x) for x in v]:
                return sorted(str(x) for x in v)
        return None

    def run(cmd, X):
        m_ = None
        for mm_ in cmd.getClass().getDeclaredMethods():
            if str(mm_.getName()) == "execute" and len(mm_.getParameterTypes()) == 5:
                m_ = mm_
        m_.setAccessible(True)
        m_.invoke(cmd, JArray(Obj)([None, X.st, X.ref, X.pr, E.W1]))
        E.pump(X)
        return PGM(X)
    cmds = {}
    for cn, word, al, hub in (("HubCharCmd", "character", ["char"], "character"), ("HubStorageCmd", "storage", [], "storage"),
                              ("HubMarketCmd", "market", [], "market"), ("HubTravelCmd", "travel", [], "world"), ("HubSocialCmd", "social", [], "social")):
        c = JV(cn)()
        cmds[word] = c
        K.check(str(c.getName()) == word and sorted(str(x) for x in c.getAliases()) == al and groups(c) == ["hytale:Adventurer"]
                and APC.class_.isInstance(c), "CMD /%s%s: a player command, permission group hytale:Adventurer" % (word, "".join(" /" + a for a in al)))
    Q = mkp(E.UUID.fromString("00000000-0000-0000-0000-0000000000c3"), "SkyyFresh")
    pg = run(cmds["character"], Q)
    K.check(pg is not None and str(pg.getClass().getSimpleName()) == "StatsPage", "CMD /character (no last tab): Character > Stats")
    pg = run(cmds["travel"], Q)
    K.check(pg is not None and str(pg.getClass().getSimpleName()) == "MenuPage" and str(pg.view) == "tp", "CMD /travel: World > Teleport")
    pg = run(cmds["social"], Q)
    K.check(pg is not None and str(pg.getClass().getSimpleName()) == "MenuPage" and str(pg.view) == "players", "CMD /social: Social > Players")
    n0 = len(E.sent(Q))
    pg2 = run(cmds["storage"], Q)
    txt = E.strs_of(Q, n0)
    K.check(same(pg2, pg) and "Storage hub is coming soon" in txt, "CMD /storage: no tab yet -> 'coming soon' in chat, no page")
    # FIX (bags.md LOCKED: players see "the Void", never "Pocket Dimension"): the Storage line and the /storage description
    _sd = ""
    for _mn in ("getDescription", "getDescriptionKey"):
        try:
            _sd = str(getattr(cmds["storage"], _mn)())
            break
        except Exception:
            pass
    K.check("the Void" in txt and "Pocket" not in txt and "the Void" in _sd and "Pocket" not in _sd,
            "FIX /storage: 'the Void' in the coming-soon line and the command description (%r)" % _sd)
    n0 = len(E.sent(Q))
    pg3 = run(cmds["market"], Q)
    K.check(same(pg3, pg) and "Market hub is coming soon" in E.strs_of(Q, n0), "CMD /market: 'coming soon' in chat")
    # last tab: Character > Skills (an H3 tab) remembered -> /character opens it; gone again -> the first tab
    br.put("hub:tab:character:skills", JArray(Obj)(["SkyySkills", "Skills", Int(20), "skills", F(TRUE), None]))
    br.get("hub:last:" + str(Q.pr.getUuid())).put("character", "skills")
    del seen[:]
    run(cmds["character"], Q)
    K.check(seen == [str(Q.pr.getUuid())], "CMD /character: the LAST tab (Skills, another mod's) opens through its Function")
    br.remove("hub:tab:character:skills")
    pg = run(cmds["character"], Q)
    K.check(pg is not None and str(pg.getClass().getSimpleName()) == "StatsPage", "CMD /character: a last tab that is gone -> the first tab (Stats)")
    lst = JV("MenuPage")(Q.pr, "main")
    Q.pm.openCustomPage(Q.ref, Q.st, lst)
    E.pump(Q)
    lt = openp(Q, "layout")
    pg = run(cmds["character"], Q)
    K.check(str(br.get("hub:last:" + str(Q.pr.getUuid())).get("settings")) == "layout", "CMD: hub:last keeps settings -> layout (the editor drew)")

    # ---------------------------------------------------------------- LAST
    R = mkp(E.UUID.fromString("00000000-0000-0000-0000-0000000000c4"), "SkyyLeaver")
    key = "hub:last:" + str(R.pr.getUuid())
    K.check(br.get(key) is None, "LAST: no hub:last before the join")
    try:
        PRE = JClass("com.hypixel.hytale.server.core.event.events.player.PlayerReadyEvent")
        ok_ready = False
        for ct in PRE.class_.getDeclaredConstructors():
            pt = [str(x.getName()) for x in ct.getParameterTypes()]
            if len(pt) == 3 and "Ref" in pt[0] and "Player" in pt[1]:
                ct.setAccessible(True)
                ev = ct.newInstance(JArray(Obj)([R.ref, R.pl, Int(0)]))
                JV("MenuReady")().accept(ev)
                ok_ready = True
        K.check(ok_ready and br.get(key) is not None and JClass("java.util.Map").class_.isInstance(br.get(key)), "LAST: MenuReady (join) makes hub:last:<uuid>")
    except Exception as e:
        MH.ensure(R.pr.getUuid())
        K.notes.append("PlayerReadyEvent not built (%s) - ensure() called instead" % e)
        K.check(br.get(key) is not None, "LAST: ensure makes hub:last:<uuid>")
    PDE = JClass("com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent")
    built = False
    for ct in PDE.class_.getDeclaredConstructors():
        if len(ct.getParameterTypes()) == 1:
            ct.setAccessible(True)
            JV("MenuQuit")().accept(ct.newInstance(JArray(Obj)([R.pr])))
            built = True
    K.check(built and br.get(key) is None and not MH.LAST.containsKey(R.pr.getUuid()), "LAST: MenuQuit (disconnect) removes hub:last:<uuid>")
    MH.ensure(R.pr.getUuid())
    E.UniH.PL.remove(R.pr)
    E.PLAYERS.remove(R.pr)
    online = JClass("java.util.HashSet")()
    for x in E.UniH.PL:
        online.add(x.getUuid())
    sw = int(MH.sweep(online))
    K.check(sw == 1 and br.get(key) is None and br.get("hub:last:" + str(u)) is not None,
            "LAST: the 30 s upkeep (sweep) removes the map of a player gone, keeps the online ones")
    foreign = JArray(Obj)(["SkyySkills", "Skills", Int(20), "skills", None, None])
    br.put("hub:tab:character:skills", foreign)
    other = JClass("java.util.concurrent.ConcurrentHashMap")()
    br.put("hub:last:00000000-0000-0000-0000-00000000dead", other)
    removed = int(MH.clearAll())
    K.check(removed == 14 and not [str(k) for k in br.keySet() if str(k).startswith("hub:def:") or (str(k).startswith("hub:tab:") and str(k) != "hub:tab:character:skills")]
            and same(br.get("hub:tab:character:skills"), foreign) and not [k for k in br.keySet() if str(k).startswith("hub:last:") and str(k) != "hub:last:00000000-0000-0000-0000-00000000dead"]
            and MH.LAST.isEmpty(), "LAST: shutdown (clearAll) removes hub:def x7 + Menu's 7 tabs (%d) and every hub:last we made; another mod's tab and a map we did not make stay" % removed)
    # the plugin's setup / shutdown and the upkeep call the hub pieces (bytecode: the plugin needs the server to construct)
    zj = zipfile.ZipFile(jar)
    sys.path.insert(0, os.path.join(ROOT, "tools"))

    def cps(n):
        import struct
        data = zj.read("com/skyy/menu/%s.class" % n)
        return data
    pb = cps("SkyyMenuPlugin")
    K.check(all(x.encode() in pb for x in ("com/skyy/menu/MenuHub", "register", "clearAll", "com/skyy/menu/HubCharCmd", "com/skyy/menu/HubStorageCmd",
                                           "com/skyy/menu/HubMarketCmd", "com/skyy/menu/HubTravelCmd", "com/skyy/menu/HubSocialCmd")),
            "LAST: the plugin registers the hub tabs + the 5 commands and clears them at shutdown (bytecode)")
    K.check(b"com/skyy/menu/MenuHub" in cps("SeenTick") and b"sweep" in cps("SeenTick"), "LAST: SeenTick sweeps hub:last (bytecode)")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    hcls = os.path.join(scratch, "hclasses_live")
    os.makedirs(hcls, exist_ok=True)
    os.chdir(scratch)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, hcls, jar], verify=True)
    E = T19.engine(scratch, hcls)
    JV = lambda n: JClass(PKG + n)
    Paths = E.Paths
    JV("PageGuard").STOP = False
    JV("PageGuard").EXEC = None
    ML = JV("MenuLayout")
    ML.DIR = Paths.get(os.path.join(home, "layouts"))
    ML.DEF_FILE = Paths.get(os.path.join(home, "layout-default.properties"))
    JV("SetStore").DIR = Paths.get(os.path.join(home, "settings"))
    JV("Given").DIR = Paths.get(os.path.join(home, "given-profile"))
    JV("Given").LEGACY = Paths.get(os.path.join(home, "given"))
    JV("SetReg").ADMIN_FILE = Paths.get(os.path.join(home, "settings-defaults.properties"))
    UniC = JClass("com.hypixel.hytale.server.core.universe.Universe")
    byU = jf(UniC.class_, "playersByUuid").get(UniC.get())
    b0 = T19.snap(home)
    res = []
    for n_ in range(2):
        JV("MenuIO").begin()
        ML.loadDefault()
        JV("SetReg").loadAdmin(True)
        JV("SetReg").registerOwn()
        JV("SetReg").drain()
        P = E.player(E.UUID.fromString("d8ddde89-98b2-4739-983e-a39773d582b6"))
        byU.put(P.pr.getUuid(), P.pr)
        JV("SetLoadTask").preload(P.pr)
        ML.preload(P.pr.getUuid())
        n = int(JV("MenuHub").register())
        got = []
        for hub, tab in (("character", "stats"), ("world", "teleport"), ("social", "players"), ("settings", "settings"), ("settings", "layout"),
                         ("settings", "mods")):
            r = str(JV("HubBar").open(P.pr, P.pr.getUuid(), hub, tab))
            E.pump(P)
            pg = P.pm.getCustomPage()
            b = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")()
            pg.build(P.ref, b, JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")(), P.st)
            got.append(r == "bridge" and int(b.getCommands().length if hasattr(b.getCommands(), "length") else len(list(b.getCommands()))) > 10)
        time.sleep(0.8)
        ML.flushAll()
        JV("SetStore").flushAll()
        JV("MenuIO").stop(2000)
        cleared = int(JV("MenuHub").clearAll())
        res.append([n == 7, all(got), cleared == 14, T19.snap(home) == b0])
    K.eq(res, [[True, True, True, True], [True, True, True, True]], "D: two starts on a COPY of the live Skyy_SkyyMenu (%d files): the hub registry, "
         "every Menu tab page opened + built, cleared at the end - no file written" % len(b0))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyMenu", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("hub", run_hub), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyMenu"))
