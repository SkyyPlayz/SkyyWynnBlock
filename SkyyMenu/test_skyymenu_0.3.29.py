"""Harness for SkyyMenu 0.3.29 (UNIFIED MENU U1: Home + the shortcut grid + Edit shortcuts + the one-time layout update + the Teleport
grid + kit 1.6 row 1 on every Menu page; tools/menu_0_3_29_patch.py). Build first:
    python tools/menu_0_3_29_patch.py && python SkyyMenu/build_skyymenu_0.3.29.py

    python SkyyMenu/test_skyymenu_0.3.29.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py: the game's JRE, the cached HytaleServer.jar, -XX:-UsePerfData, TEMP / TMP in the scratch
folder; -Xverify:all over the SkyyMenu 0.3.19 harness's engine stand-ins: a recording packet sink, a component store, worlds, the
Universe, the REAL PageManager / WindowManager, a command manager that records lines, a plain player and an op):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.28 -> 0.3.29: exactly the listed members differ, + MenuAlert; non-class entries: manifest.json only
  U    EXECUTED (the "unified" phase):
       REG    hub:def:<hub> = {title, command, icon, default tab} (Character -> skills), hub:def:home, home:alert:SkyyMenu, Settings >
              Edit shortcuts; clearAll removes them
       HOME   the menu item / hotkey / /skymenu page = Home: built into REAL builders, check_page / check_sky_paths / assert_proven-safe
              markup, 1268 x 616, row 1 = 8 hubs (Home Primary, icons), YOU lines from the bridge, the 7 x 5 grid = Teleport in the centre
              + the 7 hubs around it, the foot row; the CENTRE SLOT's screen offset recomputed from the built markup = 0.3.28 slot 13's
              (0, +4) - for Home AND Teleport; every b.set / binding names an element that exists
       CLICK  every Home control answers (a page packet, a page change or a close - never silence): the centre (Teleport, in place),
              a hub (its default / first tab), YOU (Stats), an alert line, Edit shortcuts, Close, row 1 (Home / a hub), a tab
       EDIT   pick up / swap / move / Remove / + Add (paged, every kind) / Cancel / Reset (twice) / Server default + Standard (op, twice;
              a plain player refused) / Done; saved per account in the extended file; the Teleport grid's centre customised: Home ->
              click -> My Island -> click teleports (the island command runs) without any other click
       MIG    the ONE-TIME UPDATE on COPIES of real saved layouts (the live HUD mod layout of Skyy + synthetic 0.3.28 files: the stock
              layout D, a sparse one, the server default): the expected grids (an independent table here), the verified History copy
              (= the exact old bytes), the index.log line, the config-changes.log line (queued), the run-once marker (_home), _old, the
              0.3.28 lines kept (a 0.3.28 parse of the new file = the old layout: rollback), no second update on a re-read / restart,
              Old tiles back, a removed tile never comes back, ERR (unreadable) refuses edits, BAD keeps .bad
       ROW    kit 1.5 pages' "< Menu" (/skymenu) now opens Home; the Stats / Settings / Server Setup / Players / Mods pages draw row 1 in
              the title bar (no < Menu), the page sizes unchanged; row clicks route (Home in place, a hub, the own hub = self)
  D    live     two starts on a scratch COPY of the live Skyy_SkyyMenu: start 1 updates Skyy's layout once (the layout file + one
                History copy + index.log, nothing else); start 2 writes nothing; every Menu page opened + built both times
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, json, time, zipfile, importlib.util, glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import skyyui as SUI

_s19 = importlib.util.spec_from_file_location("test_skyymenu_0_3_19", os.path.join(HERE, "test_skyymenu_0.3.19.py"))
T19 = importlib.util.module_from_spec(_s19)
_s19.loader.exec_module(T19)

VERSION = "0.3.29"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.28.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "menuu1", "harness")))
PKG = "com.skyy.menu."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyMenu")
SKYY = "d8ddde89-98b2-4739-983e-a39773d582b6"
ADDED = ["MenuAlert"]
# 0.3.28 -> 0.3.29: exactly these members differ (MenuLayout: the new grid model + the one-time update; MenuPage: Home / Teleport /
# the editor / row 1; HubBar: the kit 1.6 members; MenuData: the 0.3.29 tables; the version texts of CfgFn / CfgRows / OpsPage).
# Simplify pass 1: the retired 9 x 6 view's code is gone (MenuData -f the 0.3.17 editor controls / texts; MenuPage -f lay / occ,
# -m editTile / editMarks / fillWarps / hubMode; MenuLayout -f READS / WRITES / WARNS) + small helpers (pageOf, saveGrid, slotOf, ...)
EXPECT = {
    'AdminPage': ['~m frame', '~m tail'],
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~m header'],
    'HubBar': ['+<clinit>', '+f ROW_IDS', '+f ROW_TITLES', '+m build2', '+m buildRow', '+m def4', '+m defOf', '+m defTab', '+m goHub', '+m hubs', '+m iconOf', '+m okIcon', '+m okItem', '+m pickTab', '+m putIcon', '+m route', '+m rowLab', '+m rowStyle', '+m rowWidth', '+m tabBStyle', '+m tabLab', '+m titleOf'],
    'LayoutSaveTask': ['~m run'],
    'MenuData': ['+f AL_MAX', '+f AL_MIG', '+f AL_SET', '+f AL_SHOW', '+f BH_KEY', '+f BH_SLOT', '+f BT_KEY', '+f BT_SLOT', '+f FB_GAP', '+f FB_TW', '+f FB_W', '+f FB_WORD', '+f HG_CC', '+f HG_COLS', '+f HG_CR', '+f HG_N', '+f HG_ROWS', '+f HOME_FOOT_W', '+f HOME_ICON', '+f HOME_TITLE', '+f HT_ADD', '+f HT_EDIT', '+f HT_EDIT_START', '+f HT_EMPTY_ADD', '+f HT_EMPTY_FOOT_ADD', '+f HT_EMPTY_FOOT_MOVE', '+f HT_EMPTY_MOVE', '+f HT_EMPTY_NAME', '+f HT_HINT', '+f HT_HINT_OFF', '+f HT_MID', '+f HT_MID_ADD', '+f HT_MID_EDIT', '+f HT_NONE_LEFT', '+f HT_PICK_FOOT', '+f HT_SEL_BODY', '+f HT_SEL_FOOT', '+f HT_SWAP_FOOT', '+f HT_TILE_BODY', '+f HT_TP_HINT', '+f HUB_BLURB', '+f HUB_DEFTAB', '+f MIG', '+f MIG_TAB', '+f OLD_CC', '+f OLD_COLS', '+f OLD_CR', '+f TPK_E', '+f TPK_KEY', '+f TP_AUTO', '+f TP_FOOT_W', '+f UI_FBH', '+f UI_FBT', '+f UI_FSP', '+f UI_HA', '+f UI_HFOOT', '+f UI_HGAP5', '+f UI_HGAP8', '+f UI_HGRID', '+f UI_HGRIDNT', '+f UI_HGW', '+f UI_HINFO0', '+f UI_HINFO1', '+f UI_HMAIN', '+f UI_HMID', '+f UI_HMIDT', '+f UI_HNOW', '+f UI_HNOWE', '+f UI_HNOWT', '+f UI_HSP16', '+f UI_HYBAR0', '+f UI_HYBAR1', '+f UI_HYH', '+f UI_HYL', '+f UI_HYN', '+f UI_HYOU', '+f UI_HYT', '+f UI_TFOOT', '+f UI_TGAP3', '+f UI_THINT', '+f UI_TID', '+f UI_TIN', '+f UI_TINFO', '+f UI_TLEAD', '+f UI_TROW', '+f YOU_BAR_W', '-f CTRL_DONE', '-f CTRL_RESET', '-f CTRL_SRVCLEAR', '-f CTRL_SRVSAVE', '-f DONE_BODY', '-f DONE_FOOT', '-f DONE_NAME', '-f EDIT_ARM', '-f EDIT_BODY', '-f EDIT_FOOT', '-f EDIT_HINT', '-f EDIT_INFO', '-f EDIT_INFO_ADMIN', '-f EDIT_INFO_NAME', '-f EDIT_MOVING', '-f EDIT_NAME', '-f EDIT_PICK_FOOT', '-f EDIT_SEL_BODY', '-f EDIT_SEL_FOOT', '-f EDIT_SLOT', '-f EDIT_SWAP_FOOT', '-f EDIT_TILE_BODY', '-f EDIT_TITLE', '-f EMPTY_BODY', '-f EMPTY_FOOT_MOVE', '-f EMPTY_FOOT_PICK', '-f EMPTY_NAME', '-f ICON_DONE', '-f ICON_EDIT', '-f ICON_RESET', '-f ICON_SRVCLEAR', '-f ICON_SRVSAVE', '-f RESET_BODY', '-f RESET_FOOT', '-f RESET_NAME', '-f SRVCLEAR_BODY', '-f SRVCLEAR_FOOT', '-f SRVCLEAR_NAME', '-f SRVSAVE_BODY', '-f SRVSAVE_FOOT', '-f SRVSAVE_NAME', '~<clinit>'],
    'MenuHub': ['~m click', '~m pick', '~m register'],
    'MenuLayout': ['+f DEF_PENDING', '+f HFAIL', '+f HIST_INDEX', '+f HIST_TRIES', '+f HUMAN', '+f MIGRATED', '+f MIGRATIONS', '+f SNAPPED', '+f STAMP', '+m blank', '+m builtin', '+m builtinOld', '+m bytesFor', '+m clearDefault', '+m compatText', '+m copy', '+m empty', '+m fileId', '+m finishMig', '+m grid', '+m has', '+m hasNewLines', '+m hasOldDefault', '+m hasSame', '+m history', '+m hubIdx', '+m keyIndex', '+m lines', '+m logMigration', '+m mapSlot', '+m migrate', '+m okKey', '+m okTp', '+m okWarp', '+m oldDefaultBack', '+m oldLine', '+m oldOf', '+m oldTilesBack', '+m parse', '+m parseOld', '+m parseOldLine', '+m placeOutside', '+m put', '+m readWas', '+m rec', '+m saveDefault', '+m settleDef', '+m slotLines', '+m slotOf', '+m snapFirst', '+m summary', '+m tabHere', '+m tail', '+m text', '+m twin', '-f READS', '-f WARNS', '-f WRITES', '-m builtin', '-m clearDefault', '-m hasOwn', '-m of', '-m parse', '-m reset', '-m resolve', '-m saveDefault', '-m sourceOf', '-m swap', '-m text', '~<clinit>', '~f DEF', '~m loadDefault', '~m own', '~m preload', '~m pruneOffline', '~m readFile', '~m saveNow', '~m warnOnce', '~m writeDef', '~m writeOwn'],
    'MenuPage': ['+f addKeys', '+f addPage', '+f addPages', '+f addSlot', '+f alertT', '+f grid', '+f gridN', '+m alertClick', '+m alerts', '+m buildDash', '+m candidates', '+m dashEditClick', '+m drawKey', '+m editTile2', '+m emptyMark', '+m fbIndex', '+m fillAdd', '+m fillAutoWarps', '+m fillDash', '+m foot', '+m footClick', '+m gone', '+m isDash', '+m kindOf', '+m leaveEdit', '+m look', '+m nameOf', '+m nowPanel', '+m openHub', '+m openTab', '+m pageOf', '+m part', '+m saveGrid', '+m shortcut', '+m tabIcon', '+m tileLook', '+m tpEntry', '+m vitMax', '+m warpTile', '+m youClick', '+m youLine', '+m youPanel', '-f lay', '-f occ', '-m editClick', '-m editInfo', '-m editMarks', '-m editTile', '-m fillWarps', '-m hubMode', '~c ', '~m build', '~m clearGrid', '~m click', '~m fill', '~m fillStatic', '~m handleDataEvent', '~m hubClick', '~m hubName', '~m hubTab', '~m nav', '~m put', '~m startEdit'],
    'OpsPage': ['~<clinit>'],
    'SettingsPage': ['~m build'],
    'SkyyMenuPlugin': ['~m setup'],
    'StatsPage': ['~m build'],
    'Tips': ['-m setOff'],
}

# ---- the independent reference of the one-time update (Hubs-Spec 1.3 + research/Unified-Menu-Plan.md section 0) - NOT read from the jar
COVER = {"yourprofile": "character", "pets": "character", "skills": "character", "accessorybag": "character", "collections": "character",
         "islandmenu": "world", "crafting": "smithing", "reforge": "smithing", "identify": "smithing", "bank": "storage", "vault": "storage",
         "pocketdimension": "storage", "wardrobe": "storage", "bazaar": "market", "auctionhouse": "market", "players": "social",
         "party": "social", "guild": "social", "settings": "settings", "hudeditor": "settings"}
D28 = {"pets": 3, "skills": 4, "accessorybag": 5, "islandmenu": 12, "teleport": 13, "crafting": 14, "bank": 21, "bazaar": 22, "auctionhouse": 23,
       "vault": 29, "reforge": 30, "identify": 31, "pocketdimension": 32, "yourprofile": 33, "collections": 40, "players": 0, "party": 9,
       "guild": 18, "wardrobe": 36, "hovertooltips": 8, "settings": 17, "hudeditor": 26, "mods": 35, "serversetup": 44}   # 0.3.28 layout D
# the page each covered tile IS (Hubs-Spec 1.3) - fix round: the hub replaces the tile only when this tab is published
TILE_TAB = {"yourprofile": "character:stats", "pets": "character:pets", "skills": "character:skills", "accessorybag": "character:accessories",
            "collections": "character:collections", "islandmenu": "world:island", "crafting": "smithing:recipes", "reforge": "smithing:reforge",
            "identify": "smithing:identify", "bank": "storage:bank", "vault": "storage:vault", "pocketdimension": "storage:pocket",
            "wardrobe": "storage:requip", "bazaar": "market:bazaar", "auctionhouse": "market:auctions", "players": "social:players",
            "party": "social:party", "guild": "social:guild", "settings": "settings:settings", "hudeditor": "settings:hud"}
ALL_TABS = set(TILE_TAB.values())
HOME_DEF = {17: "tab:world:teleport", 10: "hub:character", 24: "hub:market", 16: "hub:storage", 18: "hub:smithing", 9: "hub:social",
            11: "hub:settings", 23: "hub:world"}
TP_DEF = {16: "tp:island", 17: "tp:hub", 18: "tp:spawn"}


def ref_map(s):
    r, c = s // 9 - 1 + 2, s % 9 - 4 + 3
    return r * 7 + c if 0 <= r < 5 and 0 <= c < 7 else -1


def ref_migrate(old, hubs=True, have=None):
    """old = {tile key: 0.3.28 slot} -> {new slot: key}; have = the published hub tabs (None = all of them)"""
    have = ALL_TABS if have is None else have
    g = {}
    for k, s in sorted(old.items(), key=lambda kv: kv[1]):
        if k == "hovertooltips":
            continue
        ns = ref_map(s)
        if ns < 0 or ns in g:
            continue
        key = "tab:world:teleport" if k == "teleport" else ("hub:" + COVER[k] if hubs and k in COVER and TILE_TAB[k] in have else "tile:" + k)
        if key in g.values():
            continue
        g[ns] = key
    if hubs:
        # fix round 2: a hub whose covered (published) tiles all sat outside the 7 x 5 grid -> the free slot nearest to its first covered
        # tile's spot pulled inside the grid (squared distance, ties: the lower slot)
        for k, s in sorted(old.items(), key=lambda kv: kv[1]):
            if k not in COVER or TILE_TAB[k] not in have or ("hub:" + COVER[k]) in g.values():
                continue
            rr = min(max(s // 9 - 1 + 2, 0), 4)
            cc = min(max(s % 9 - 4 + 3, 0), 6)
            free = [x for x in range(35) if x not in g]
            if free:
                g[min(free, key=lambda x: ((x // 7 - rr) ** 2 + (x % 7 - cc) ** 2, x))] = "hub:" + COVER[k]
    return g


def props(path):
    out = {}
    for ln in open(path, encoding="utf-8").read().splitlines():
        if ln.startswith("#") or "=" not in ln:
            continue
        k, v = ln.split("=", 1)
        out[k.strip()] = v.strip()
    return out


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
    out = []
    for c in list(b.getCommands()):
        g = lambda n: (lambda v: None if v is None else str(v))(jf(c.getClass(), n).get(c))
        out.append((g("type"), g("selector"), g("text"), g("data")))
    return out


def events_of(ev):
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
H_RE = re.compile(r"Height: (\d+)")


def build_page(page, P):
    from jpype import JClass
    b = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")()
    ev = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")()
    page.build(P.ref, b, ev, P.st)
    return cmds_of(b), events_of(ev)


def page_rules(K, cmds, evs, what, prefix_ok="Skyy"):
    """markup rules on a built page: check_page, kit textures only (no ../), every b.set / binding names an element that exists"""
    apps = SUI.Appends([(None if s is None else s.lstrip("#"), t) for ty, s, t, d in cmds if t is not None and ty and "Append" in ty])
    sets = [(s, d) for ty, s, t, d in cmds if ty == "Set"]
    try:
        SUI.check_page(apps, prefix_ok)
        K.check(True, "%s: check_page (markup rules, parents, no duplicate id)" % what)
    except Exception as e:
        K.check(False, "%s: check_page: %s" % (what, e))
    try:
        els = SUI.check_sky_paths(apps)
        allp = [m.group(0) for mk in apps.markups() for m in SUI._SKY_PATH_RE.finditer(SUI.render(mk))]
        K.check(not [p for p in allp if p.startswith('"../')], "%s: no texture path leaves Common/UI/Custom (%d)" % (what, len(allp)))
    except Exception as e:
        els = []
        K.check(False, "%s: sky paths: %s" % (what, e))
    for _p, mk in apps:
        if re.search(r"(Vertical|Horizontal)Alignment\s*:\s*(Top|Bottom|Left|Right)\b", mk):
            K.check(False, "%s: a Top/Bottom/Left/Right alignment: %s" % (what, mk[:80]))
    ids = set()
    for _p, mk in apps:
        ids |= set(x.group(2) for x in DECL_RE.finditer(SUI.render(mk)))
    bs = [s for s, _t in evs]
    bad = [s for s, _d in sets if s.lstrip("#").split(".")[0] not in ids] + [s for s in bs if s.lstrip("#") not in ids]
    K.check(not bad, "%s: every b.set / binding names an element that exists (%d sets, %d bindings): %s" % (what, len(sets), len(bs), bad[:4]))
    return apps, els


def run_unified(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JArray, JImplements, JOverride
    K = HK.Child(out)
    hcls = os.path.join(scratch, "hcls_u")
    os.makedirs(hcls, exist_ok=True)
    os.chdir(scratch)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, hcls, jar], verify=True)
    E = T19.engine(scratch, hcls)
    JV = lambda n: JClass(PKG + n)
    Paths = E.Paths
    home = os.path.join(scratch, "home_u")
    lay_dir = os.path.join(home, "layouts")
    os.makedirs(lay_dir, exist_ok=True)
    JV("PageGuard").STOP = False
    JV("PageGuard").EXEC = None
    ML = JV("MenuLayout")
    ML.DIR = Paths.get(lay_dir)
    ML.DEF_FILE = Paths.get(os.path.join(home, "layout-default.properties"))
    JV("SetStore").DIR = Paths.get(os.path.join(home, "settings"))
    JV("SetReg").ADMIN_FILE = Paths.get(os.path.join(home, "settings-defaults.properties"))
    JV("SetReg").registerOwn()
    JV("MenuIO").begin()
    HB, MH, MD = JV("HubBar"), JV("MenuHub"), JV("MenuData")
    br = JV("MenuUtil").bridge()
    UniC = JClass("com.hypixel.hytale.server.core.universe.Universe")
    byU = jf(UniC.class_, "playersByUuid").get(UniC.get())
    TRUE, FALSE = JClass("java.lang.Boolean").TRUE, JClass("java.lang.Boolean").FALSE
    Obj, Int = JClass("java.lang.Object"), JClass("java.lang.Integer")
    SysC = JClass("java.lang.System")
    same = lambda a, b_: (a is None and b_ is None) or (a is not None and b_ is not None and int(SysC.identityHashCode(a)) == int(SysC.identityHashCode(b_)))
    seen = []

    @JImplements("java.util.function.Function")
    class F(object):
        def __init__(self, r):
            self.r = r

        @JOverride
        def apply(self, x):
            seen.append(str(x))
            return self.r(x) if callable(self.r) else self.r

    def mkp(uid, name):
        P = E.player(uid, name=name)
        byU.put(uid, P.pr)
        E.UniH.PL.add(P.pr)
        E.PLAYERS.add(P.pr)
        return P
    P = mkp(E.PLAIN, "SkyyPlain")
    O = mkp(E.OP, "SkyyOp")
    u, uo = P.pr.getUuid(), O.pr.getUuid()
    PGM = lambda X: X.pm.getCustomPage()

    def flush():
        time.sleep(0.5)
        ML.flushAll()

    def openm(X, view="main"):
        m = JV("MenuPage")(X.pr, view)
        X.pm.openCustomPage(X.ref, X.st, m)
        E.pump(X)
        return m

    def click(X, pg, a, extra=""):
        n0 = len(E.sent(X))
        pg.handleDataEvent(X.ref, X.st, '{"a":"%s"%s}' % (a, extra))
        E.pump(X)
        return PGM(X), len(E.sent(X)) > n0

    def slot(X, pg, i):
        n0 = len(E.sent(X))
        pg.handleDataEvent(X.ref, X.st, '{"a":"mslot","SlotIndex":%d}' % i)
        E.pump(X)
        return PGM(X), len(E.sent(X)) > n0

    def grid_items(cmds):
        """the Slots set of #SkyyMGrid: [(item id, name) or None]"""
        return None

    # ---------------------------------------------------------------- REG
    n = int(MH.register())
    K.eq(n, 7, "REG: Menu's 7 own tabs put")
    for i, hub in enumerate(SUI.HUBS):
        d = br.get("hub:def:" + hub)
        K.check(d is not None and len(d) == 4 and str(d[0]) == SUI.HUB_DEFS[hub][0] and str(d[1]) == SUI.HUB_DEFS[hub][1]
                and (str(d[3]) == "skills" if hub == "character" else d[3] is None),
                "REG: hub:def:%s = {title, command, icon, default tab} %s" % (hub, None if d is None else [None if x is None else str(x) for x in d]))
    dh = br.get("hub:def:home")
    K.check(dh is not None and [str(x) for x in dh[:3]] == ["Home", "skymenu", "Skyy_Menu"] and dh[3] is None, "REG: hub:def:home = {Home, skymenu, Skyy_Menu}")
    al = br.get("home:alert:SkyyMenu")
    K.check(al is not None and str(al.getClass().getName()) == PKG + "MenuAlert" and JClass("java.util.function.Function").class_.isInstance(al),
            "REG: home:alert:SkyyMenu = the MenuAlert Function")
    K.check(al.apply(u) is None and al.apply("x") is None, "REG: MenuAlert: nothing to say for a fresh player / not a UUID")
    lt = br.get("hub:tab:settings:layout")
    K.check(lt is not None and str(lt[1]) == "Edit shortcuts", "REG: Settings > Edit shortcuts (was Menu layout)")
    K.check([str(x[0]) for x in HB.hubs()] == list(SUI.HUB_ROW_IDS), "REG: row 1 = Home + the 7 hubs")

    # ---------------------------------------------------------------- HOME
    hm = openm(P)
    c, ev = build_page(hm, P)
    apps, els = page_rules(K, c, ev, "HOME", "SkyyM")
    root = apps[0][1]
    m = WH_RE.search(root)
    K.check(apps[0][0] is None and root.startswith("Group #SkyyMHm ") and (int(m.group(1)), int(m.group(2))) == (1268, 616),
            "HOME: the root #SkyyMHm 1268 x 616 (%s)" % root[:60])
    K.check({"Frame", "Header", "Panel", "Primary", "Tertiary", "Close"} <= set(els) and "HeaderOrnament" not in els, "HOME: the sky kit, row 1 in the bar (%s)" % els)
    row = [mk for p_, mk in apps if p_ == "SkyyMHmHubRow" and mk.startswith("Button")]
    K.check(len(row) == 8 and "SkyyKit/Primary.png" in row[0] and all("SkyyKit/Tertiary.png" in mk for mk in row[1:]),
            "HOME: row 1 = 8 buttons, Home (first) Primary, the hubs Tertiary")
    K.check(sum(1 for p_, mk in apps if (p_ or "").startswith("SkyyMHmHubR") and mk.startswith("ItemIcon")) == 8, "HOME: row 1 buttons show their icons")
    K.check(any(s_ == "#SkyyMHmYN.Text" and '"SkyyPlain"' in d for ty, s_, t, d in c if ty == "Set"), "HOME: YOU shows the player's name")
    K.check(any(s_ == "#SkyyMHmYou" for s_, _t in ev) and any("hyou" in t for s_, t in ev if s_ == "#SkyyMHmYou"), "HOME: YOU is a button (hyou)")
    K.check(not any(p_ == "SkyyMHmNow" for p_, mk in apps), "HOME: Right now hidden when there is nothing to say")
    # the grid: 35 slots, the centre = Teleport, the hubs one step around it (as built)
    K.check(hm.gridN == 35 and len(hm.grid) == 35 and dict((i, str(k)) for i, k in enumerate(hm.grid) if k is not None) == HOME_DEF,
            "HOME: the default grid = Teleport in the centre + the 7 hubs around it")
    K.check(str(hm.acts[17]) == "sc:tab:world:teleport" and str(hm.acts[10]) == "sc:hub:character", "HOME: slot actions (centre = Teleport)")
    fb = [s_ for s_, t in ev if s_.startswith("#SkyyMHmF")]
    K.check(fb == ["#SkyyMHmFhedit", "#SkyyMHmFclose"], "HOME: the foot = Edit shortcuts + Close (%s)" % fb)
    K.check(any(s_ == "#SkyyMHmInfo.Text" and "Edit shortcuts" in d for ty, s_, t, d in c if ty == "Set"), "HOME: the info line says what to do")
    # THE CENTRE SLOT under the mouse, recomputed from the BUILT markup: x = pad + YOU + gap + 3.5 slots, y = bar + pad + title + gap + grid top
    def hpx(sel, kind="Height"):
        mk = [mk for p_, mk in apps if ("#%s " % sel) in mk][0]
        return int(re.search(kind + r": (\d+)", mk).group(1))
    gmk = [mk for p_, mk in apps if mk.startswith("ItemGrid #SkyyMGrid")][0]
    gtop = int(re.search(r"Top: (\d+)", gmk).group(1))
    slot_px = int(re.search(r"SlotSize: (\d+)", gmk).group(1))
    gap5 = [mk for p_, mk in apps if p_ == "SkyyMHmMid" and mk.startswith("Group { Anchor: (Height:")]
    cy = 38 + 24 + hpx("SkyyMHmMidT") + int(H_RE.search(gap5[0]).group(1)) + gtop + 2 * slot_px + slot_px // 2 - 616 // 2
    cx = 24 + hpx("SkyyMHmYou", "Width") + 16 + 3 * slot_px + slot_px // 2 - 1268 // 2
    K.eq((cx, cy), (0, 4), "HOME: the centre slot sits at the page centre + (0, +4) = the 0.3.28 slot 13 spot (from the built markup)")
    K.check("SlotsPerRow: 7" in gmk and "AreItemsDraggable: false" in gmk, "HOME: the grid is 7 wide and not draggable")
    # the old 9 x 6 main view's slot 13, from the 0.3.28 constants in the jar (MenuData.UI_ROOT / UI_INFOBOX ...)
    old = (22 + 4 * 84 + 42 - 800 // 2, 14 + 3 + 38 + 22 + int(H_RE.search(str(MD.UI_INFOBOX)).group(1)) + 8 + 3 + 84 + 42 - 952 // 2)
    K.eq(old, (0, 4), "HOME: 0.3.28's slot 13 was at the page centre + (0, +4)")
    # the menu item / hotkey / /skymenu all open MenuPage(main) = Home
    K.check(str(JV("MenuPageFactory")().apply(P.pr).view) == "main", "HOME: the menu item opens Home (MenuPageFactory -> main)")

    # ---------------------------------------------------------------- CLICK: the centre -> Teleport in place, its centre slot at the same spot
    pg, sent = slot(P, hm, 17)
    K.check(same(pg, hm) and str(hm.view) == "tp" and sent, "CLICK Home centre: Teleport opens IN PLACE (same page, redrawn)")
    c, ev = build_page(hm, P)
    apps, els = page_rules(K, c, ev, "TELEPORT", "SkyyM")
    root = apps[0][1]
    K.check(root.startswith("Group #SkyyMTp ") and WH_RE.search(root).groups() == ("804", "704"), "TELEPORT: root 804 x 704")
    tabs = [mk for p_, mk in apps if p_ == "SkyyMTpHubTabs" and mk.startswith("TextButton")]
    K.check(len(tabs) == 1 and "Tab_Selected" in tabs[0] and '"Teleport"' in tabs[0], "TELEPORT: the World tab strip (Teleport selected)")
    K.check(sum(1 for p_, mk in apps if p_ == "SkyyMTpHubRow" and mk.startswith("Button")) == 8, "TELEPORT: row 1 in the bar")
    gmk = [mk for p_, mk in apps if mk.startswith("ItemGrid #SkyyMGrid")][0]
    lead = [mk for p_, mk in apps if p_ == "SkyyMTpRow" and mk.startswith("Group { Anchor: (Width:")]
    hint = [mk for p_, mk in apps if mk.startswith("Label #SkyyMTpHint ")]
    gap3 = [mk for p_, mk in apps if p_ == "SkyyMTpB" and mk.startswith("Group { Anchor: (Height: 3)")]
    cx = 24 + int(re.search(r"Width: (\d+)", lead[0]).group(1)) + 3 * 84 + 42 - 804 // 2
    cy = 38 + 24 + 52 + int(H_RE.search(hint[0]).group(1)) + int(H_RE.search(gap3[0]).group(1)) + int(re.search(r"Top: (\d+)", gmk).group(1)) + 2 * 84 + 42 - 704 // 2
    K.eq((cx, cy), (0, 4), "TELEPORT: its centre slot is the same screen spot as Home's (from the built markup)")
    K.check(dict((i, str(k)) for i, k in enumerate(hm.grid) if k is not None) == TP_DEF and str(hm.acts[17]) == "cmdc:hub",
            "TELEPORT: the default = My Island | Hub (centre) | Spawn")
    K.check([s_ for s_, t in ev if s_.startswith("#SkyyMTpF")] == ["#SkyyMTpFhedit", "#SkyyMTpFclose"], "TELEPORT: the foot = Edit + Close")
    # customise the Teleport centre: Edit -> pick My Island (16) -> click the centre (17) = swap -> Done
    pg, sent = click(P, hm, "fhedit")
    K.check(hm.editing and sent and str(hm.view) == "tp", "EDIT tp: Edit answers (editing)")
    pg, sent = slot(P, hm, 16)
    K.check(int(hm.editSel) == 16 and sent and "Picked up My Island" in str(hm.status), "EDIT tp: My Island picked up (%s)" % hm.status)
    pg, sent = slot(P, hm, 17)
    K.check(int(hm.editSel) == -1 and sent and "swapped" in str(hm.status), "EDIT tp: dropped on the centre = swapped with Hub (%s)" % hm.status)
    pg, sent = click(P, hm, "fedone")
    K.check(not hm.editing and sent, "EDIT tp: Done")
    flush()
    pf = os.path.join(lay_dir, str(u) + ".properties")
    pp = props(pf) if os.path.isfile(pf) else {}
    K.check(pp.get("_tp") == "1" and pp.get("t.17") == "tp:island" and pp.get("t.16") == "tp:hub" and pp.get("_home") == "0" and pp.get("_v") == "1"
            and pp.get("teleport") == "13", "EDIT tp: saved per account (_tp=1, t.17=tp:island, _home=0, the 0.3.28 compat line) %s" % pp)
    K.eq(dict((k, int(v)) for k, v in pp.items() if k in D28), D28, "FIX 5: a player with no 0.3.28 file gets the FULL 0.3.28 layout D as the rollback lines")
    # Skyy's flow: open the menu -> click (Teleport) -> click (My Island) - no other click, the same screen spot twice
    hm2 = openm(P)
    pg, _s = slot(P, hm2, 17)
    E.CM.lines.clear()
    pg, _s = slot(P, hm2, 17)
    K.check([str(x) for x in E.CM.lines] == ["island"], "FLOW: open -> click centre (Teleport) -> click centre (My Island) runs /island (%s)" % list(E.CM.lines))
    # ---------------------------------------------------------------- CLICK: every Home control answers
    hm = openm(P)
    pg, sent = click(P, hm, "fclose")
    K.check(pg is None, "CLICK Home: Close closes")
    hm = openm(P)
    pg, sent = click(P, hm, "hyou")
    K.check(pg is not None and str(pg.getClass().getSimpleName()) == "StatsPage", "CLICK Home: YOU opens Character > Stats")
    hm = openm(P)
    pg, sent = slot(P, hm, 10)
    K.check(pg is not None and str(pg.getClass().getSimpleName()) == "StatsPage", "CLICK Home: the Character hub opens its first tab (Stats; Skills not loaded)")
    br.put("hub:tab:character:skills", JArray(Obj)(["SkyySkills", "Skills", Int(20), "skills", F(TRUE), None]))
    K.check(str(br.get("hub:last:" + str(u)).get("character")) == "stats", "CLICK Home: the last Character tab was Stats (YOU + the hub opened it)")
    hm = openm(P)
    del seen[:]
    pg, sent = slot(P, hm, 10)
    K.check(seen == [str(u)], "FIX2 CLICK Home: the Character hub opens its DEFAULT tab Skills even after Stats was visited (Skyy: skills as the default)")
    hm = openm(P)
    pg, sent = slot(P, hm, 24)
    K.check(same(pg, hm) and sent and "coming soon" in str(hm.status).lower(), "CLICK Home: a hub with no tab yet answers 'coming soon' (%s)" % hm.status)
    pg, sent = slot(P, hm, 9)
    K.check(same(pg, hm) and str(hm.view) == "players", "CLICK Home: Social opens Players in place")
    pg, sent = click(P, hm, "hub:h:home")
    K.check(same(pg, hm) and str(hm.view) == "main" and sent, "ROW: Home (row 1) from Players = Home in place")
    pg, sent = click(P, hm, "hub:h:home")
    K.check(same(pg, hm) and sent, "ROW: Home on Home = redraw")
    pg, sent = click(P, hm, "hub:h:world")
    K.check(pg is not None and str(pg.view) == "tp", "ROW: World from Home = World > Teleport")
    pg, sent = click(P, pg, "hub:h:world")
    K.check(sent, "ROW: World on a World page = redraw (self)")
    pg, sent = click(P, pg, "hub:h:settings")
    K.check(pg is not None and str(pg.getClass().getSimpleName()) == "SettingsPage", "ROW: Settings from Teleport opens Settings")
    sp = pg
    c, ev = build_page(sp, P)
    a2, e2 = page_rules(K, c, ev, "SETTINGS", "SkyyStg")
    K.check(any(p_ == "SkyyStgHHubRow" for p_, mk in a2) and not any("HubMenu" in (mk or "") for p_, mk in a2), "ROW: Settings draws row 1, no < Menu")
    lay = [mk for p_, mk in a2 if p_ == "SkyyStgHHubTabs" and '"Edit shortcuts"' in mk]
    K.check(len(lay) == 1, "ROW: the Settings strip says Edit shortcuts")
    pg, sent = click(P, sp, "hub:layout")
    K.check(pg is not None and str(pg.getClass().getSimpleName()) == "MenuPage" and str(pg.view) == "main" and pg.editing,
            "ROW: Settings > Edit shortcuts = Home in edit mode")
    hm = pg
    pg, sent = click(P, hm, "fedone")
    pg, sent = click(P, hm, "hub:h:character")
    st = pg
    K.check(st is not None, "ROW: Character from Home")
    stp = JV("StatsPage")(P.pr, 0)
    P.pm.openCustomPage(P.ref, P.st, stp)
    E.pump(P)
    c, ev = build_page(stp, P)
    a3, e3 = page_rules(K, c, ev, "STATS", "SkyyStat")
    K.check(WH_RE.search(a3[0][1]).groups() == ("1114", "966") and any(p_ == "SkyyStatFHubRow" for p_, mk in a3), "ROW: Stats 1114 x 966 (unchanged), row 1 drawn")
    pg, sent = click(P, stp, "hub:h:home")
    K.check(pg is not None and str(pg.getClass().getSimpleName()) == "MenuPage" and str(pg.view) == "main", "ROW: Home from Stats opens Home")
    stp = JV("StatsPage")(P.pr, 0)
    P.pm.openCustomPage(P.ref, P.st, stp)
    E.pump(P)
    pg, sent = click(P, stp, "hub:h:character")
    K.check(same(pg, stp) and sent, "ROW: Character on a Character page = self (redraw)")
    # kit 1.5 pages: "< Menu" runs /skymenu, which opens Home
    E.CM.lines.clear()
    br.put("config:def:SkyyMenu", "x")
    r15 = str(HB.handle(P.pr, '{"a":"hub:back"}', "character", "skills"))
    K.check(r15 == "back" and [str(x) for x in E.CM.lines] == ["skymenu"], "ROW: a kit 1.5 page's < Menu runs /skymenu (%s, %s)" % (r15, list(E.CM.lines)))
    br.remove("config:def:SkyyMenu")
    APC = JClass("com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand")
    mc = JV("MenuCmd")()
    for mm_ in mc.getClass().getDeclaredMethods():
        if str(mm_.getName()) == "execute" and len(mm_.getParameterTypes()) == 5:
            mm_.setAccessible(True)
            mm_.invoke(mc, JArray(Obj)([None, P.st, P.ref, P.pr, E.W1]))
    E.pump(P)
    K.check(PGM(P) is not None and str(PGM(P).view) == "main" and str(PGM(P).getClass().getSimpleName()) == "MenuPage", "ROW: /skymenu opens Home")
    # Players / Mods (classic views) in the row shell
    for view, hub in (("players", "social"), ("mods", "settings")):
        mv = openm(O, view)
        c, ev = build_page(mv, O)
        a4, e4 = page_rules(K, c, ev, view.upper(), "SkyyM")
        K.check(a4[0][1].startswith("Group #SkyyMenuH ") and WH_RE.search(a4[0][1]).groups() == ("804", "980") and any(p_ == "SkyyMenuHHubRow" for p_, mk in a4)
                and not any("HubMenu" in mk for p_, mk in a4), "ROW: %s = the row shell 804 x 980 (no < Menu)" % view)
    ap = JV("AdminPage")(O.pr, "list", None)
    O.pm.openCustomPage(O.ref, O.st, ap)
    E.pump(O)
    c, ev = build_page(ap, O)
    a5, e5 = page_rules(K, c, ev, "SERVER SETUP", "SkyyAdm")
    K.check(any(p_ == "SkyyAdmHHubRow" for p_, mk in a5) and WH_RE.search(a5[0][1]).groups() == ("1128", "980"), "ROW: Server Setup row shell 1128 x 980")
    pg, sent = click(O, ap, "hub:h:home")
    K.check(pg is not None and str(pg.view) == "main", "ROW: Home from Server Setup")

    # ---------------------------------------------------------------- EDIT (Home)
    hm = openm(P)
    pg, sent = click(P, hm, "fhedit")
    K.check(hm.editing and sent and "no dragging" in str(hm.status).lower(), "EDIT: Edit shortcuts (the status says no dragging)")
    c, ev = build_page(hm, P)
    fb = [s_ for s_, t in ev if s_.startswith("#SkyyMHmF")]
    K.check(fb == ["#SkyyMHmFereset", "#SkyyMHmFedone"], "EDIT: the foot for a plain player = Reset + Done (%s)" % fb)
    K.check(str(hm.acts[0]) == "eslot" and str(hm.acts[10]) == "eslot", "EDIT: every slot is clickable (empty slots too)")
    pg, sent = slot(P, hm, 10)
    K.check(int(hm.editSel) == 10 and sent, "EDIT: Character picked up")
    c, ev = build_page(hm, P)
    K.check([s_ for s_, t in ev if s_.startswith("#SkyyMHmF")] == ["#SkyyMHmFeremove", "#SkyyMHmFereset", "#SkyyMHmFedone"], "EDIT: Remove shows while a tile is picked up")
    pg, sent = click(P, hm, "feremove")
    K.check(sent and hm.grid[10] is None and "removed" in str(hm.status), "EDIT: Remove (%s)" % hm.status)
    pg, sent = slot(P, hm, 16)
    pg, sent = slot(P, hm, 0)
    K.check(hm.grid[0] is not None and str(hm.grid[0]) == "hub:storage" and hm.grid[16] is None, "EDIT: Storage moved to an empty slot (0)")
    pg, sent = slot(P, hm, 0)
    pg, sent = slot(P, hm, 18)
    K.check(str(hm.grid[0]) == "hub:smithing" and str(hm.grid[18]) == "hub:storage", "EDIT: two tiles swap")
    for i_ in range(12):     # other mods' pages (from the registry) make the list long enough to page
        br.put("hub:tab:market:x%d" % i_, JArray(Obj)(["SkyyFake", "Fake %d" % i_, Int(40 + i_), "fake", F(TRUE), None]))
    pg, sent = slot(P, hm, 10)
    K.check(int(hm.addSlot) == 10 and sent, "EDIT: an empty slot opens + Add")
    c, ev = build_page(hm, P)
    keys = [None if k is None else str(k) for k in hm.addKeys]
    K.check("hub:character" in keys and "tab:world:teleport" not in keys and any(k and k.startswith("tab:") for k in keys)
            and any(k and k.startswith("tile:") for k in keys), "EDIT: + Add lists hubs, hub tabs and old tiles (not what is on the grid)")
    K.check("tile:hovertooltips" not in keys and int(hm.addPages) >= 2, "EDIT: + Add has no Hover Tooltips; it is paged (%d pages)" % hm.addPages)
    allk = set(k for k in keys if k)
    _pg = 0
    while int(hm.addPage) < int(hm.addPages) - 1 and _pg < 10:
        click(P, hm, "fanext")
        allk |= set(str(k) for k in hm.addKeys if k is not None)
        _pg += 1
    while int(hm.addPage) > 0:
        click(P, hm, "faprev")
    twins = dict(("tile:" + k_, "tab:" + v_) for k_, v_ in TILE_TAB.items())
    twins.update({"tile:teleport": "tab:world:teleport", "tile:mods": "tab:settings:mods", "tile:serversetup": "tab:settings:setup"})
    gridk = set(str(k) for k in hm.grid if k is not None)
    K.check("tab:world:teleport" in gridk and "tile:teleport" not in allk, "FIX2 ADD: Teleport is on the grid, so + Add does not offer the old Teleport tile")
    K.check(not any(t_ in allk and v_ in allk for t_, v_ in twins.items()) and "tab:social:players" in allk and "tile:players" not in allk,
            "FIX2 ADD: a page is listed once (an old tile and the hub tab it is are the same page)")
    K.check(not any((t_ in gridk and v_ in allk) or (v_ in gridk and t_ in allk) for t_, v_ in twins.items()), "FIX2 ADD: a page on the grid under either key is not offered")
    pg, sent = click(P, hm, "fanext")
    k2 = [None if k is None else str(k) for k in hm.addKeys]
    K.check(int(hm.addPage) == 1 and sent and any(k and (k.startswith("tp:") or k.startswith("tile:")) for k in k2), "EDIT: + Add page 2 (teleports / tiles)")
    pg, sent = click(P, hm, "faprev")
    K.check(int(hm.addPage) == 0 and sent, "EDIT: + Add back to page 1")
    bz = keys.index("tile:bazaar") if "tile:bazaar" in keys else -1
    K.check(bz >= 0, "EDIT: the old Bazaar tile is offered")
    pg, sent = slot(P, hm, bz)
    K.check(int(hm.addSlot) == -1 and str(hm.grid[10]) == "tile:bazaar" and "added" in str(hm.status), "EDIT: picking it fills the empty slot (%s)" % hm.status)
    pg, sent = slot(P, hm, 12)
    pg, sent = click(P, hm, "facancel")
    K.check(int(hm.addSlot) == -1 and sent, "EDIT: Cancel leaves + Add")
    for i_ in range(12):
        br.remove("hub:tab:market:x%d" % i_)
    flush()
    pp = props(pf)
    K.check(pp.get("_home") == "1" and pp.get("g.10") == "tile:bazaar" and pp.get("g.18") == "hub:storage" and pp.get("g.0") == "hub:smithing"
            and "g.16" not in pp and pp.get("t.17") == "tp:island", "EDIT: saved at once in the same file (g. lines; the Teleport grid kept)")
    pg, sent = click(P, hm, "fereset")
    K.check(sent and "again" in str(hm.status) and hm.grid[10] is not None, "EDIT: Reset asks for a second click")
    pg, sent = click(P, hm, "fereset")
    K.check(dict((i, str(k)) for i, k in enumerate(hm.grid) if k is not None) == HOME_DEF, "EDIT: Reset twice = the default grid")
    _r, _d = JV("MenuLayout").rec(u), JV("MenuLayout").DEF   # simplify: the dead sourceOf went - the same rule checked here
    K.check((_r is None or _r[0] is None) and (_d is None or _d[0] is None), "EDIT: the source is the standard shortcuts again")
    pg, sent = click(P, hm, "fesrv")
    K.check("Only admins" in str(hm.status), "EDIT: a plain player cannot save the server default")
    pg, sent = click(P, hm, "fedone")
    K.check(not hm.editing and sent, "EDIT: Done")
    ho = openm(O)
    click(O, ho, "fhedit")
    c, ev = build_page(ho, O)
    K.check([s_ for s_, t in ev if s_.startswith("#SkyyMHmF")] == ["#SkyyMHmFereset", "#SkyyMHmFesrv", "#SkyyMHmFestd", "#SkyyMHmFedone"], "EDIT op: + Server default + Standard")
    # FIX UI (critic 3): the NARROWEST foot (an admin, a tile picked up) - the admin buttons say what they do; the info line wraps to 2
    # lines and every edit text / the pick-up status fits them at 14 px (0.85 = the room a word wrap may waste)
    slot(O, ho, 23)
    c, ev = build_page(ho, O)
    apps_ = [(p_, SUI.render(mk)) for ty, p_, mk, d in c if mk is not None and ty and "Append" in ty]
    fmk = " ".join(mk for p_, mk in apps_ if "#SkyyMHmF" in mk)
    K.check('"Set default"' in fmk and '"Clear default"' in fmk and '"Server default"' not in fmk and '"Standard"' not in fmk,
            "FIX UI 6: the admin buttons read Set default / Clear default")
    imk = [mk for p_, mk in apps_ if "#SkyyMHmInfo" in mk]
    iw = int(re.search(r"#SkyyMHmInfo \{ Anchor: \(Width: (\d+)", imk[0]).group(1)) if imk else 0
    foot_ = [s_ for s_, t in ev if s_.startswith("#SkyyMHmF")]
    K.check(imk and re.search(r"Wrap: true", imk[0]) and "Height: 40" in imk[0] and len(foot_) == 5,
            "FIX UI 1: the info line is a 2-line wrapped label (%d px) beside 5 admin buttons %s" % (iw, foot_))
    room = 2 * (iw - 16) * 0.85
    for nm_, t_ in (("HT_EDIT", str(MD.HT_EDIT)), ("HT_EDIT_START", str(MD.HT_EDIT_START)), ("pick-up status", str(ho.status)),
                    ("HT_HINT", str(MD.HT_HINT)), ("HT_ADD", str(MD.HT_ADD))):
        K.check(SUI.text_width(t_, 14) <= room, "FIX UI 1: %s fits the 2 info lines (%d of %d px): %s" % (nm_, SUI.text_width(t_, 14), room, t_))
    click(O, ho, "fesrv")
    K.check(SUI.text_width(str(ho.status), 14) <= room and "again" in str(ho.status), "FIX UI 1: the Set default confirm fits (%s)" % ho.status)
    slot(O, ho, 23)
    K.check(int(ho.editSel) == -1, "FIX UI: the picked-up tile put back (clicked again)")
    slot(O, ho, 23)
    click(O, ho, "feremove")
    click(O, ho, "fesrv")
    click(O, ho, "fesrv")
    flush()
    dp = props(os.path.join(home, "layout-default.properties")) if os.path.isfile(os.path.join(home, "layout-default.properties")) else {}
    K.check(dp.get("_home") == "1" and "g.23" not in dp and dp.get("g.17") == "tab:world:teleport", "EDIT op: Server default saved (layout-default.properties) %s" % dp)
    K.check(dict((i, str(k)) for i, k in enumerate(ML.grid(E.UUID.randomUUID(), 0)) if k is not None) == dict((s_, k) for s_, k in HOME_DEF.items() if s_ != 23),
            "EDIT op: a player without their own shortcuts gets the server default")
    click(O, ho, "festd")
    click(O, ho, "festd")
    flush()
    K.check(not os.path.isfile(os.path.join(home, "layout-default.properties")), "EDIT op: Standard twice = the server default file is gone (standard again)")
    click(O, ho, "fedone")

    # ---------------------------------------------------------------- ALERTS (Right now)
    br.put("hub:tab:character:trees", JArray(Obj)(["SkyyTrees", "Trees", Int(30), "tree", None, None]))
    br.put("home:alert:SkyyTest", F(lambda x: "3 AP to spend|character:trees\nno target here\nedit me|edit\na fourth line|world"))
    br.put("home:alert:SkyyBoom", F(lambda x: (_ for _ in ()).throw(RuntimeError("boom"))))
    hm = openm(P)
    c, ev = build_page(hm, P)
    sets = dict((s_, d) for ty, s_, t, d in c if ty == "Set")
    K.check('"3 AP to spend  >"' in sets.get("#SkyyMHmA0.Text", "") and '"no target here"' in sets.get("#SkyyMHmA1.Text", "") and "#SkyyMHmA3.Text" not in sets,
            "ALERT: up to 3 lines per mod, a throwing Function skipped (%s)" % [v for k_, v in sets.items() if k_.startswith("#SkyyMHmA")])
    E.CM.lines.clear()
    pg, sent = click(P, hm, "halert0")
    K.check([str(x) for x in E.CM.lines] == ["tree"], "ALERT: a line opens its tab (Character > Trees through its command)")
    hm = openm(P)
    pg, sent = click(P, hm, "halert1")
    K.check(same(pg, hm) and sent and "no page" in str(hm.status), "ALERT: a line without a target answers")
    pg, sent = click(P, hm, "halert2")
    K.check(same(pg, hm) and hm.editing, "ALERT: 'edit' opens Edit shortcuts")
    pg, sent = click(P, hm, "halert9")
    K.check(sent, "ALERT: a stale alert click still answers (redraw)")
    for k in ("home:alert:SkyyTest", "home:alert:SkyyBoom", "hub:tab:character:trees", "hub:tab:character:skills"):
        br.remove(k)
    # FIX UI 3 (critic 3): a long alert line is clipped to AL_MAX and fits its 252 px button at the 11 px shrink floor; SkyyMenu's own fit
    br.put("home:alert:SkyyLong", F(lambda x: "Your Mining Skill Tree has 12 points waiting to be spent right now|world"))
    hm = openm(P)
    c, ev = build_page(hm, P)
    sets = dict((s_, d) for ty, s_, t, d in c if ty == "Set")
    try:
        a0 = str(list(json.loads(str(sets.get("#SkyyMHmA0.Text", "{}"))).values())[0])
    except Exception:
        a0 = re.sub(r'^"|"$', "", str(sets.get("#SkyyMHmA0.Text", "")))
    K.check(a0.endswith("  >") and len(a0) - 3 <= int(MD.AL_MAX) <= 40, "FIX UI 3: a long alert is clipped to %d characters (%s)" % (int(MD.AL_MAX), a0))
    K.check(SUI.text_width(a0, 11, bold=True) <= 300 - 2 * 14 - 2 * 10, "FIX UI 3: ... and fits its button at 11 px (%d px)" % SUI.text_width(a0, 11, bold=True))
    K.check(all(SUI.text_width(str(t_) + "  >", 11, bold=True) <= 252 for t_ in (MD.AL_MIG, MD.AL_SET)), "FIX UI 3: SkyyMenu's own alerts fit")
    br.remove("home:alert:SkyyLong")
    # FIX UI 2 (critic 3, LOCKED 2026-10-10): BEFORE Edit is clicked, the text beside it already says dragging does not work
    hm = openm(P)
    c, ev = build_page(hm, P)
    sets = dict((s_, d) for ty, s_, t, d in c if ty == "Set")
    K.check("settings, general" in str(MD.HT_HINT_OFF).lower(), "FIX2: the tooltips-off hint names where the switch is (Settings, General)")
    K.check("no dragging" in str(sets.get("#SkyyMHmInfo.Text", "")).lower() and all("no dragging" in str(t_).lower() for t_ in (MD.HT_HINT, MD.HT_HINT_OFF, MD.HT_TP_HINT)),
            "FIX UI 2: the Home info line (and the tooltips-off / Teleport hints) say 'no dragging' before Edit (%s)" % sets.get("#SkyyMHmInfo.Text"))

    # ---------------------------------------------------------------- MIG: the one-time update on COPIES of real saved layouts
    live = os.path.join(LIVE_DIR, "layouts", SKYY + ".properties")
    cases = []
    if os.path.isfile(live):
        cases.append(("live Skyy (HUD mod)", SKYY, open(live, "rb").read()))
    else:
        K.notes.append("MIG: no live layout at %s - only the synthetic files" % live)
    stock = "# a 0.3.28 file\n_name=Stock\n_v=1\n" + "".join("%s=%d\n" % kv for kv in sorted(D28.items()))
    cases.append(("stock layout D (CRLF)", "00000000-0000-0000-0000-00000000aa01", stock.replace("\n", "\r\n").encode()))
    sparse = "_v=1\nbazaar=13\nmods=12\nhovertooltips=14\nskills=0\nidentify=40\n"
    cases.append(("sparse", "00000000-0000-0000-0000-00000000aa02", sparse.encode()))
    menu_tabs = set(str(k)[8:] for k in br.keySet() if str(k).startswith("hub:tab:"))
    fakes = sorted(ALL_TABS - menu_tabs)

    def publish(on):
        for t_ in fakes:
            if on:
                br.put("hub:tab:" + t_, JArray(Obj)(["SkyyFake", "Fake " + t_, Int(50), "fake", F(TRUE), None]))
            else:
                br.remove("hub:tab:" + t_)
    publish(True)
    HIDX = str(ML.HIST_INDEX)
    for label, uid, data in cases:
        old = dict((k, int(v)) for k, v in (ln.split("=", 1) for ln in data.decode().replace("\r", "").split("\n") if "=" in ln and not ln.startswith("#") and not ln.startswith("_"))
                   if k in D28)
        f = os.path.join(lay_dir, uid + ".properties")
        open(f, "wb").write(data)
        U_ = E.UUID.fromString(uid)
        want = ref_migrate(old)
        g = ML.grid(U_, 0)
        got = dict((i, str(k)) for i, k in enumerate(g) if k is not None)
        K.eq(got, want, "MIG %s: the expected Home grid" % label)
        K.check(ML.MIGRATED.containsKey(uid) and str(ML.oldOf(U_)) == ",".join("%s=%d" % (k, s_) for k, s_ in sorted(old.items(), key=lambda kv: kv[1])),
                "MIG %s: marked migrated, _old = the old line" % label)
        flush()
        baks = glob.glob(os.path.join(home, "config-history", "Skyy_SkyyMenu~layouts~%s.properties.*.bak" % uid))
        K.check(len(baks) == 1 and open(baks[0], "rb").read() == data, "MIG %s: ONE History copy = the exact old bytes" % label)
        idx = open(os.path.join(home, "config-history", HIDX), encoding="utf-8").read()
        K.check(("Skyy_SkyyMenu/layouts/%s.properties" % uid) in idx and "before the 0.3.29 Home shortcuts update" in idx, "MIG %s: the History index line (%s)" % (label, HIDX))
        kidx = os.path.join(home, "config-history", "index.log")
        K.check(not os.path.isfile(kidx) or ("layouts/%s" % uid) not in open(kidx, encoding="utf-8").read(),
                "FIX 3: the line is NOT in the kit's index.log (its compaction drops foreign ids)")
        nb = open(f, "rb").read()
        crlf = b"\r\n" in data
        tailb = nb[len(data):]
        K.check(nb.startswith(data) and len(tailb) > 0 and (crlf == (b"\r\n" in tailb)) and (not crlf or b"\n" not in tailb.replace(b"\r\n", b"")),
                "FIX 4: the update kept the old file's EXACT bytes and appended in its own line ending (%s)" % ("CRLF" if crlf else "LF"))
        np_ = props(f)
        K.check(np_.get("_home") == "1" and np_.get("_v") == "1" and np_.get("_old") == str(ML.oldOf(U_))
                and all(np_.get(k) == str(v) for k, v in old.items()) and dict((int(k[2:]), v) for k, v in np_.items() if k.startswith("g.")) == want,
                "MIG %s: the new file = _home (run-once) + _old + the 0.3.28 lines + the g. grid" % label)
        # a 0.3.28 parse of the new file (rollback): the tile lines are exactly the old ones
        roll = dict((k, int(v)) for k, v in np_.items() if k in D28)
        K.eq(roll, old, "MIG %s: rollback - a 0.3.28 SkyyMenu reads the old layout from the new file" % label)
        q = list(JV("CfgLog").snap())
        K.check(any(("menu.layout[%s]" % uid) in str(x) and "\tdone" in str(x) for x in q), "MIG %s: a config-changes.log line (status done) is queued" % label)
        # re-read (cache dropped) and a restart: no second update
        ML.OWN.remove(uid)
        ML.MIGRATED.remove(uid)
        g2 = ML.grid(U_, 0)
        flush()
        K.check(dict((i, str(k)) for i, k in enumerate(g2) if k is not None) == want and not ML.MIGRATED.containsKey(uid)
                and len(glob.glob(os.path.join(home, "config-history", "Skyy_SkyyMenu~layouts~%s.properties.*.bak" % uid))) == 1,
                "MIG %s: re-read = no second update (no new History copy)" % label)
        # Old tiles back = the in-game Undo: every old tile on its mapped slot (no hubs, no Hover Tooltips)
        ob = ML.oldTilesBack(U_)
        K.eq(dict((i, str(k)) for i, k in enumerate(ob) if k is not None), ref_migrate(old, hubs=False), "MIG %s: Old tiles back" % label)
    # FIX2 (critic 2 #2): an admin restores the 0.3.28 .bak by hand while the player is offline; the player rejoins in the SAME session ->
    # a NEW update with its own History copy and the old bytes kept (not a full rewrite)
    Us = "00000000-0000-0000-0000-00000000aa02"
    fs = os.path.join(lay_dir, Us + ".properties")
    open(fs, "wb").write(sparse.encode())
    ML.OWN.remove(Us)
    ML.MIGRATED.remove(Us)
    ML.grid(E.UUID.fromString(Us), 0)
    flush()
    K.check(len(glob.glob(os.path.join(home, "config-history", "Skyy_SkyyMenu~layouts~%s.properties.*.bak" % Us))) == 2
            and open(fs, "rb").read().startswith(sparse.encode()) and props(fs).get("_home") == "1" and ML.SNAPPED.get(Us) == TRUE,
            "FIX2: a hand-restored 0.3.28 file read again in the same session = a second History copy + the old bytes kept")
    # FIX 1: the tab publishers are NOT on the server (e.g. Menu 0.3.29 deployed before SkyyGear / SkyySacks / ...): the covered tiles stay
    publish(False)
    Un = "00000000-0000-0000-0000-00000000aa03"
    open(os.path.join(lay_dir, Un + ".properties"), "wb").write(stock.encode())
    gn = dict((i, str(k)) for i, k in enumerate(ML.grid(E.UUID.fromString(Un), 0)) if k is not None)
    wn = ref_migrate(D28, have=menu_tabs)
    K.eq(gn, wn, "FIX 1: no tab publisher -> only hubs whose page is here (Menu's own: %s) replace tiles; the rest stay tiles" % sorted(menu_tabs))
    K.check("tile:crafting" in gn.values() and "tile:reforge" in gn.values() and "hub:smithing" not in gn.values(),
            "FIX 1: Crafting + Reforge stay working tiles - no 'coming soon' Smithing stub")
    flush()
    publish(True)
    # FIX 2: the History copy is made ONCE per file even when the write after it is retried
    Ur = "00000000-0000-0000-0000-00000000aa04"
    fr = os.path.join(lay_dir, Ur + ".properties")
    open(fr, "wb").write(sparse.encode())
    ML.snapFirst(Ur, Paths.get(fr), "layouts/%s.properties" % Ur)
    ML.snapFirst(Ur, Paths.get(fr), "layouts/%s.properties" % Ur)
    K.check(len(glob.glob(os.path.join(home, "config-history", "Skyy_SkyyMenu~layouts~%s.properties.*.bak" % Ur))) == 1 and ML.SNAPPED.get(Ur) == FALSE,
            "FIX 2: a retried write never makes a second History copy")
    ML.SNAPPED.remove(Ur)
    # FIX 2: a History copy that keeps failing (config-history is a FILE here) blocks the write HIST_TRIES - 1 times, then the update is
    # written anyway (with a warning) - the player's shortcuts are not stuck for good; the old bytes stay in the file
    home2 = os.path.join(scratch, "home_u2")
    lay2 = os.path.join(home2, "layouts")
    os.makedirs(lay2, exist_ok=True)
    open(os.path.join(home2, "config-history"), "w").write("not a folder")
    ML.DIR = Paths.get(lay2)
    Uh = "00000000-0000-0000-0000-00000000aa05"
    fh = os.path.join(lay2, Uh + ".properties")
    open(fh, "wb").write(sparse.encode())
    ML.grid(E.UUID.fromString(Uh), 0)
    # the update's own delayed save (300 ms, MenuIO) is the FIRST try; then the 30 s retries (saveNow) until the file is written.
    # Recorded per try: (failed History copies so far, the file still unchanged)
    time.sleep(0.8)
    tries = []
    _hf = ML.HFAIL.get(Uh)
    tries.append((int(_hf) if _hf is not None else 0, open(fh, "rb").read() == sparse.encode()))
    for _i in range(int(ML.HIST_TRIES) + 1):
        if open(fh, "rb").read() != sparse.encode():
            break
        ML.saveNow(Uh)
        _hf = ML.HFAIL.get(Uh)
        tries.append((int(_hf) if _hf is not None else int(ML.HIST_TRIES), open(fh, "rb").read() == sparse.encode()))
    _ht = int(ML.HIST_TRIES)
    K.eq(tries, [(c_, c_ < _ht) for c_ in range(1, _ht + 1)],
         "FIX 2: History failing: the file waits %d failed copies, the %d. try writes it" % (_ht - 1, _ht))
    K.check(open(fh, "rb").read().startswith(sparse.encode()) and props(fh).get("_home") == "1" and ML.SNAPPED.get(Uh) == TRUE and not ML.DIRTY.containsKey(Uh),
            "FIX 2: ... with the old bytes kept and the run-once marker set (no endless retry)")
    ML.DIR = Paths.get(lay_dir)
    # the live Skyy layout's exact expectation (worked out by hand from Hubs-Spec 1.3: Social + Settings + Mods + Server Setup fall outside)
    if os.path.isfile(live):
        K.eq(ref_migrate(dict((k, int(v)) for k, v in props(live).items() if k in D28)),
             {9: "hub:character", 16: "hub:storage", 17: "tab:world:teleport", 18: "hub:smithing", 29: "hub:world", 30: "hub:market",
              7: "hub:social", 20: "hub:settings"},
             "MIG live Skyy: the hand-checked result (fix round 2: Social + Settings sat outside -> the nearest free slot)")
    # the alert for a migrated player + Old tiles back in the editor (the foot shows it; twice = the tiles)
    Pm = mkp(E.UUID.fromString("00000000-0000-0000-0000-00000000aa01"), "Stock")
    ML.MIGRATED.put(str(Pm.pr.getUuid()), TRUE)
    K.check("hubs replaced" in str(al.apply(Pm.pr.getUuid())), "MIG: the Right now alert after the update")
    hm = openm(Pm)
    c, ev = build_page(hm, Pm)
    K.check(any(s_ == "#SkyyMHmA0.Text" and "hubs replaced" in d for ty, s_, t, d in c if ty == "Set"), "MIG: Home shows it in Right now")
    click(Pm, hm, "fhedit")
    c, ev = build_page(hm, Pm)
    K.check("#SkyyMHmFeold" in [s_ for s_, t in ev], "MIG: Edit shortcuts offers Old tiles back")
    click(Pm, hm, "feold")
    pg, sent = click(Pm, hm, "feold")
    K.eq(dict((i, str(k)) for i, k in enumerate(hm.grid) if k is not None), ref_migrate(D28, hubs=False), "MIG: Old tiles back twice = the old tiles")
    slot(Pm, hm, 17)
    click(Pm, hm, "feremove")
    click(Pm, hm, "fedone")
    K.check(not ML.MIGRATED.containsKey(str(Pm.pr.getUuid())) and al.apply(Pm.pr.getUuid()) is None, "MIG: Done clears the alert")
    flush()
    ML.OWN.remove(str(Pm.pr.getUuid()))
    K.check(ML.grid(Pm.pr.getUuid(), 0)[17] is None, "MIG: a removed tile never comes back by itself (after a re-read)")
    # the server default file (a 0.3.28 one) is updated once at start
    dfile = os.path.join(home, "layout-default.properties")
    dold = "# SkyyMenu: the SERVER DEFAULT\n_v=1\nteleport=13\nbank=4\nmods=5\nhudeditor=22\n"
    open(dfile, "w", encoding="utf-8", newline="").write(dold)
    publish(False)
    ML.loadDefault()
    time.sleep(0.5)
    K.check(bool(ML.DEF_PENDING.get()) and open(dfile, encoding="utf-8").read() == dold
            and not glob.glob(os.path.join(home, "config-history", "Skyy_SkyyMenu~layout-default.properties.*.bak")),
            "FIX 1: the server default's update waits for the first join (nothing written at setup)")
    publish(True)
    ML.preload(E.UUID.randomUUID())
    K.check(not bool(ML.DEF_PENDING.get()), "FIX 1: the first join settles it")
    dw = ref_migrate({"teleport": 13, "bank": 4, "mods": 5, "hudeditor": 22})
    K.eq(dict((i, str(k)) for i, k in enumerate(ML.grid(E.UUID.randomUUID(), 0)) if k is not None), dw, "MIG default: the server default updated (%s)" % dw)
    flush()
    db = glob.glob(os.path.join(home, "config-history", "Skyy_SkyyMenu~layout-default.properties.*.bak"))
    K.check(len(db) == 1 and open(db[0], "rb").read() == dold.encode() and props(dfile).get("_home") == "1" and props(dfile).get("_old") == "bank=4,mods=5,teleport=13,hudeditor=22",
            "MIG default: History copy, _home, _old")
    K.check(open(dfile, "rb").read().startswith(dold.encode()), "FIX 4: the server default kept its exact old bytes (lines appended)")
    # FIX2 (critic 2 #1): a player with NO 0.3.28 file on a server with a custom 0.3.28 default edits once -> their rollback lines are the
    # server default's tile lines (0.3.28 showed them the default), not layout D
    Unf = E.UUID.fromString("00000000-0000-0000-0000-00000000aa0d")
    ML.put(Unf, "NoFile", 1, ML.builtin(1))
    flush()
    pnf = props(os.path.join(lay_dir, str(Unf) + ".properties"))
    K.eq(dict((k, int(v)) for k, v in pnf.items() if k in D28), {"teleport": 13, "bank": 4, "mods": 5, "hudeditor": 22},
         "FIX2: no own 0.3.28 file + a custom 0.3.28 server default -> the rollback lines are the server default's")
    # FIX2 (critic 2 #3): the server default's in-game Undo - admins see Old default on Home edit (not while a tile is picked up; not players)
    hod = openm(O)
    click(O, hod, "fhedit")
    c, ev = build_page(hod, O)
    fo = [s_ for s_, t in ev if s_.startswith("#SkyyMHmF")]
    K.check("#SkyyMHmFedold" in fo, "FIX2: Home edit offers an admin Old default (%s)" % fo)
    apps_o = [SUI.render(mk) for ty, p_, mk, d in c if mk is not None and ty and "Append" in ty]
    imk_o = [mk for mk in apps_o if "#SkyyMHmInfo" in mk]
    iw_o = int(re.search(r"#SkyyMHmInfo \{ Anchor: \(Width: (\d+)", imk_o[0]).group(1)) if imk_o else 0
    K.check(iw_o >= 300, "FIX2: the info line keeps %d px beside Old default" % iw_o)
    slot(O, hod, 17)
    c, ev = build_page(hod, O)
    K.check("#SkyyMHmFedold" not in [s_ for s_, t in ev] and "#SkyyMHmFeremove" in [s_ for s_, t in ev], "FIX2: Old default hides while a tile is picked up")
    slot(O, hod, 17)
    hpd = openm(P)
    click(P, hpd, "fhedit")
    c, ev = build_page(hpd, P)
    K.check("#SkyyMHmFedold" not in [s_ for s_, t in ev], "FIX2: a plain player never sees Old default")
    pg, sent = click(P, hpd, "fedold")
    K.check(sent and "Only admins" in str(hpd.status), "FIX2: a forged Old default click from a player is refused")
    click(P, hpd, "fedone")
    ML.saveDefault(0, ML.builtin(0))
    pg, sent = click(O, hod, "fedold")
    K.check(sent and "again" in str(hod.status), "FIX2: Old default asks for a second click (%s)" % hod.status)
    pg, sent = click(O, hod, "fedold")
    wod = ref_migrate({"teleport": 13, "bank": 4, "mods": 5, "hudeditor": 22}, hubs=False)
    K.eq(dict((i, str(k)) for i, k in enumerate(ML.grid(E.UUID.randomUUID(), 0)) if k is not None), wod, "FIX2: Old default twice = the old default's tiles")
    K.check("old tiles back" in str(hod.status).lower(), "FIX2: Old default answers (%s)" % hod.status)
    flush()
    K.check(dict((int(k[2:]), v) for k, v in props(dfile).items() if k.startswith("g.")) == wod and props(dfile).get("_old") == "bank=4,mods=5,teleport=13,hudeditor=22",
            "FIX2: ... saved in layout-default.properties (the _old line kept)")
    click(O, hod, "fedone")
    ML.loadDefault()
    flush()
    K.check(len(glob.glob(os.path.join(home, "config-history", "Skyy_SkyyMenu~layout-default.properties.*.bak"))) == 1, "MIG default: no second update at the next start")
    os.remove(dfile)
    ML.loadDefault()
    publish(False)
    # ERR: a folder where the file should be = unreadable: the default shows, editing is refused, nothing is written
    Ue = "00000000-0000-0000-0000-00000000aa0e"
    os.makedirs(os.path.join(lay_dir, Ue + ".properties"), exist_ok=True)
    Pe = mkp(E.UUID.fromString(Ue), "Err")
    he = openm(Pe)
    K.check(dict((i, str(k)) for i, k in enumerate(he.grid) if k is not None) == HOME_DEF, "ERR: an unreadable layout shows the default")
    pg, sent = click(Pe, he, "fhedit")
    K.check(not he.editing and sent and str(he.status) == str(MD.EDIT_WAIT), "ERR: Edit shortcuts is refused with a clear line")
    # BAD: a file with no layout is kept as .bad on the first change
    Ub = "00000000-0000-0000-0000-00000000aa0b"
    open(os.path.join(lay_dir, Ub + ".properties"), "w").write("garbage=1\n")
    Pb = mkp(E.UUID.fromString(Ub), "Bad")
    hb = openm(Pb)
    click(Pb, hb, "fhedit")
    slot(Pb, hb, 10)
    click(Pb, hb, "feremove")
    flush()
    K.check(os.path.isfile(os.path.join(lay_dir, Ub + ".properties.bad")) and props(os.path.join(lay_dir, Ub + ".properties")).get("_home") == "1",
            "BAD: the unusable file is kept as .bad, the new shortcuts saved")

    # ---------------------------------------------------------------- shutdown
    removed = int(MH.clearAll())
    K.check(removed == 16 and br.get("home:alert:SkyyMenu") is None and br.get("hub:def:home") is None and not [k for k in br.keySet() if str(k).startswith("hub:def:")],
            "REG: clearAll removes hub:def x8 + Menu's 7 tabs + home:alert:SkyyMenu (%d)" % removed)
    JV("MenuIO").stop(2000)
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
    snaps = [T19.snap(home)]
    res = []
    for n_ in range(2):
        ML.OWN.clear()
        ML.MIGRATED.clear()
        JV("MenuIO").begin()
        ML.loadDefault()
        JV("SetReg").loadAdmin(True)
        JV("SetReg").registerOwn()
        JV("SetReg").drain()
        P = E.player(E.UUID.fromString(SKYY))
        byU.put(P.pr.getUuid(), P.pr)
        n = int(JV("MenuHub").register())
        JV("SetLoadTask").preload(P.pr)
        ML.preload(P.pr.getUuid())
        got = []
        mp = JV("MenuPage")(P.pr, "main")
        P.pm.openCustomPage(P.ref, P.st, mp)
        E.pump(P)
        c, _e = build_page(mp, P)
        got.append(len(c) > 30 and mp.gridN == 35)
        for hub, tab in (("character", "stats"), ("world", "teleport"), ("social", "players"), ("settings", "settings"), ("settings", "layout"),
                         ("settings", "mods")):
            r = str(JV("HubBar").open(P.pr, P.pr.getUuid(), hub, tab))
            E.pump(P)
            pg = P.pm.getCustomPage()
            c, _e = build_page(pg, P)
            got.append(r == "bridge" and len(c) > 10)
        time.sleep(0.8)
        ML.flushAll()
        JV("SetStore").flushAll()
        JV("MenuIO").stop(2000)
        cleared = int(JV("MenuHub").clearAll())
        snaps.append(T19.snap(home))
        res.append([n == 7, all(got), cleared == 16])
    K.eq(res, [[True, True, True], [True, True, True]], "D: two starts on a COPY of the live Skyy_SkyyMenu: registry, Home + every Menu tab page built, cleared")
    a, b1, b2 = snaps
    ch1 = sorted(set(k for k in set(a) | set(b1) if a.get(k) != b1.get(k)))
    lay_k = [k for k in a if k.replace("\\", "/").endswith("layouts/%s.properties" % SKYY)]
    had_old = bool(lay_k) and "_home" not in open(os.path.join(home, "layouts", SKYY + ".properties"), encoding="utf-8").read() if False else None
    exp = [k for k in ch1 if k.replace("\\", "/").endswith("layouts/%s.properties" % SKYY) or "config-history" in k.replace("\\", "/")]
    K.check(ch1 == exp and len(ch1) <= 3, "D: start 1 changed only Skyy's layout file + its History copy + index.log (%s)" % ch1)
    K.check(b1 == b2, "D: start 2 wrote nothing (the update ran once)")
    lp = os.path.join(home, "layouts", SKYY + ".properties")
    if os.path.isfile(lp):
        p_ = props(lp)
        K.check(p_.get("_home") in ("0", "1") and p_.get("_v") == "1", "D: Skyy's layout carries the run-once marker after start 1")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyMenu", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("unified", run_unified), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyMenu"))
