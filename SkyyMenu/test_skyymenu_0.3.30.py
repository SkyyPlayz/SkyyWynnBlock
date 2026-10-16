"""Harness for SkyyMenu 0.3.30 (round menu0330: no duplicate icons / pages, the 5 x 5 grid + its one-time update, Home + Teleport scaled
up with big row 1 / row 2, the Right now panel, stand-in hub tabs (Smithing opens /smithing), hub tab icons, Invite to Guild, Stats Health
Regen; tools/menu_0_3_30_patch.py). Build first:
    python tools/menu_0_3_30_patch.py && python SkyyMenu/build_skyymenu_0.3.30.py

    python SkyyMenu/test_skyymenu_0.3.30.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py: the game's JRE, the cached HytaleServer.jar, -XX:-UsePerfData, TEMP / TMP in the scratch
folder; -Xverify:all over the SkyyMenu 0.3.19 harness's engine stand-ins: a recording packet sink, a component store, worlds, the
Universe, the REAL PageManager / WindowManager, a command manager that records lines, a plain player and an op):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.29 -> 0.3.30: exactly the listed members differ, + MenuVtOpen / MenuVtVis; non-class entries: the new icon items,
                the SkyyHubTabs art, manifest.json
  N    EXECUTED (the 0.3.30 phase):
       ICONS  the jar: 17 wave-3 icon items (item JSON + a 64 x 64 PNG, all different), the 64 tab icon files = art/hub-tab-icons byte for
              byte; THE NO-DUPLICATE CHECK at run time: every entry Home's + Add can list (hubs, tabs, old tiles, teleports) + row 1 ->
              one icon item each (fails if any icon id is shared); no page listed twice
       REG    Menu's 7 tabs carry their tab icon; stand-in tabs for every contract tab nobody put (an owner's tab put before is kept, one
              put after replaces ours; clearAll removes only ours); visible only while the command exists; hub:def world -> teleport
       SMITH  the Smithing hub (Home tile, row 1, /smithing via MenuHub.run, another mod's row via the kit goHub) opens SkyyGear's page:
              gear:fn:smithing {uuid, "craft"}, else the /smithing command - never "coming soon"; nothing at all = one chat line
       HOME   1600 x 926, 120 px slots, 5 x 5 grid (centre 12 = Teleport, no World tile), the big row 1 (8 buttons, icons), You / Right
              now / the foot, every b.set / binding names an element; the centre slot's screen spot recomputed from the built markup
       TP     1300 x 962, big row 1 + row 2 (World tabs with their icons, Teleport active), the same centre spot; tab / row clicks route
       NOW    Right now: quest:fn:hud -> "Quest: ..." (click = World > Quests -> /quests), mystery bags in the inventory -> Identify
              (gear:fn:smithing identify), home:alert:<mod> lines, "Nothing waiting" when empty
       FOLD   the one-time 5 x 5 update on COPIES of saved grids: Skyy's live 0.3.29 file (fits: nothing written), columns 0 / 6 moved,
              a page held twice merged (tab kept), > 25 pins (first 25 kept, the rest named once in chat + the info line + a Right now
              line), a CRLF file, a 0.3.28 file (one History copy, both updates), the server default; History copy = the old bytes,
              the appended lines only, _g5=1, a 0.3.29 parse of the new file = the same 5 x 5 grid (rollback), no second write
       MISC   Invite to Guild (/guild invite <name>), Stats Main > Health Regen (skill:fn:hpregen row / "-"), + Add / edit on 25 slots
  D    live     two starts on a scratch COPY of the live Skyy_SkyyMenu (NewBetaTest): Home + every Menu tab page built both times;
                start 1 and 2 write nothing for Skyy's grid (it fits the 5 x 5 grid)
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, json, time, zipfile, hashlib, importlib.util, struct

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import skyyui as SUI

_s29 = importlib.util.spec_from_file_location("test_skyymenu_0_3_29", os.path.join(HERE, "test_skyymenu_0.3.29.py"))
T29 = importlib.util.module_from_spec(_s29)
_s29.loader.exec_module(T29)
T19 = T29.T19

VERSION = "0.3.30"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.29.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "menu0330", "harness")))
PKG = "com.skyy.menu."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyMenu")
SKYY = "d8ddde89-98b2-4739-983e-a39773d582b6"
ADDED = ["MenuVtOpen", "MenuVtVis"]
# 0.3.29 -> 0.3.30: exactly these members differ (MenuLayout: the 5 x 5 fold + canon; MenuPage: the big rows, Right now, + Add once;
# MenuData: the 0.3.30 tables; the version texts of CfgFn / CfgRows / OpsPage; StatsCalc: Health Regen + the class roster)
EXPECT = {
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~m header'],
    'MenuAlert': ['~m apply'],
    'MenuData': ['+f AL_SPILL', '+f BR_GAP', '+f BR_H', '+f BR_ICON', '+f BR_ICON_GAP', '+f BR_ICON_MIN', '+f BR_LABN', '+f BR_LABSEL', '+f BR_PAD',
                 '+f BR_PADV', '+f BT_GAP', '+f BT_H', '+f BT_ICON', '+f BT_ICON_TOP', '+f BT_LAB', '+f BT_MIN', '+f BT_PAD', '+f G7_CC', '+f G7_COLS',
                 '+f G7_CR', '+f G7_N', '+f G7_OFF', '+f G7_ROWS', '+f HOME_ROW_W', '+f TAB_ART', '+f TAB_ART_DIR', '+f TAB_ICON', '+f TAB_KEY',
                 '+f TP_ROW_W', '+f UI_BROW', '+f UI_BTABS', '+f UI_HNOWNONE', '+f UI_TGAP', '+f VT_ARG', '+f VT_CMD', '+f VT_FN', '+f VT_HUB',
                 '+f VT_LABEL', '+f VT_ORDER', '+f VT_TAB', '-f UI_HNOWE', '-f UI_TGAP3', '-f UI_THINT', '~<clinit>'],
    'MenuHub': ['+f PROXIES', '~m register'],
    'MenuLayout': ['+f FOLDS', '+f SPILL', '+m addOnce', '+m appendTo', '+m blank7', '+m bytesFor', '+m canon', '+m diff', '+m el', '+m finishMig',
                   '+m fold', '+m foldTail', '+m joinSpill', '+m logFold', '+m migrate7', '+m rank', '+m to7', '-m bytesFor', '-m finishMig', '-m twin', '~<clinit>',
                   '~m blank', '~m clearDefault', '~m hasNewLines', '~m hasSame', '~m lines', '~m loadDefault', '~m migrate', '~m own', '~m parse',
                   '~m pruneOffline', '~m put', '~m saveDefault', '~m settleDef', '~m slotLines', '~m snapFirst', '~m tail', '~m writeDef',
                   '~m writeOwn'],
    'MenuPage': ['+m bigRow', '+m bigTabs', '+m hasTabArt', '+m nowPanel', '+m nowRows', '+m questLine', '+m spillNote', '+m unidBags', '-m nowPanel',
                 '~m build', '~m buildDash', '~m candidates', '~m dashEditClick', '~m fillAdd', '~m foot', '~m look', '~m shortcut', '~m startEdit',
                 '~m tabIcon', '~m youPanel'],
    'MenuUtil': ['+m countInPrefix', '+m countPrefix'],
    'OpsPage': ['~<clinit>'],
    'SkyyMenuPlugin': ['~m setup'],
    'StatsCalc': ['+m hpRegen', '~<clinit>', '~m mainTab'],
}
W3 = ["HubCharacter", "HubStorage", "HubMarket", "HubSmithing", "HubWorld", "HubSocial", "HubSettings", "Trees", "Class", "Profiles", "Requip",
      "Gear", "Upgrade", "Explore", "Quests", "Merchants", "Layout"]
# the non-class entries this round changes: the wave-3 icon items, the 64 tab icon files, the names (server.lang), manifest.json
_TAB_STEMS = sorted("%s_%s" % (h, t) for h, t, *_r in SUI.HUB_TABS if (h, t) != ("smithing", "multitool"))
NONCLASS = sorted(["Common/Icons/ItemsGenerated/Skyy_Menu_Icon_%s.png" % n for n in W3] + ["Server/Item/Items/Utility/Skyy_Menu_Icon_%s.json" % n for n in W3]
                  + ["Common/UI/Custom/SkyyHubTabs/%s%s@2x.png" % (st, o) for st in _TAB_STEMS for o in ("", "_on")]
                  + ["Server/Languages/en-US/server.lang", "manifest.json"])


def run_compare30(out, jar, old_jar, pkg, expect, added, removed=()):
    """harness_kit.run_compare with this round's non-class entries (it only allows manifest.json): the class part is the kit's own"""
    _eq = HK.Child.eq

    def eq(self, got, want, what):
        if what == "C: non-class entries changed":
            want = NONCLASS
        return _eq(self, got, want, what)
    HK.Child.eq = eq
    try:
        return _orig_compare(out, jar, old_jar, pkg, expect, added, removed)
    finally:
        HK.Child.eq = _eq


_orig_compare = HK.run_compare
HK.run_compare = run_compare30

WH_RE, H_RE, DECL_RE = T29.WH_RE, T29.H_RE, T29.DECL_RE
build_page, props, jf = T29.build_page, T29.props, T29.jf

# ---- the independent references (NOT read from the jar)
HOME_DEF = {12: "tab:world:teleport", 7: "hub:character", 17: "hub:market", 11: "hub:storage", 13: "hub:smithing", 6: "hub:social", 8: "hub:settings"}
TP_DEF = {11: "tp:island", 12: "tp:hub", 13: "tp:spawn"}
TILE_TAB = {"yourprofile": "character:stats", "pets": "character:pets", "skills": "character:skills", "accessorybag": "character:accessories",
            "collections": "character:collections", "islandmenu": "world:island", "crafting": "smithing:recipes", "reforge": "smithing:reforge",
            "identify": "smithing:identify", "bank": "storage:bank", "vault": "storage:vault", "pocketdimension": "storage:pocket",
            "wardrobe": "storage:requip", "bazaar": "market:bazaar", "auctionhouse": "market:auctions", "players": "social:players",
            "party": "social:party", "guild": "social:guild", "settings": "settings:settings", "hudeditor": "settings:hud",
            "mods": "settings:mods", "serversetup": "settings:setup", "teleport": "world:teleport"}
DEFTAB = {"character": "skills", "world": "teleport"}


def canon(k):
    if k.startswith("tile:") and k[5:] in TILE_TAB:
        return "tab:" + TILE_TAB[k[5:]]
    if k.startswith("hub:") and k[4:] in DEFTAB:
        return "tab:%s:%s" % (k[4:], DEFTAB[k[4:]])
    return k


def rank(k):
    return 0 if canon(k) == k else (1 if k.startswith("tile:") else 2)


def ref_fold(g7, tp=False):
    """{7x5 slot: key} -> ({5x5 slot: key}, changed, spilled keys) - the rule as written in the patch notes"""
    g = {}
    over = []
    for s in sorted(g7):
        r, c = s // 7, s % 7 - 1
        if 0 <= c < 5:
            g[r * 5 + c] = g7[s]
        else:
            over.append(s)
    ch = False
    if not tp:
        for i in sorted(list(g)):
            if i not in g:
                continue
            for j in sorted(g):
                if j != i and canon(g[j]) == canon(g[i]) and (rank(g[j]) < rank(g[i]) or (rank(g[j]) == rank(g[i]) and j < i)):
                    del g[i]
                    ch = True
                    break
    spill = []
    for s in over:
        key = g7[s]
        ch = True
        if (key in g.values()) if tp else any(canon(v) == canon(key) for v in g.values()):
            if not tp:
                for j in list(g):
                    if canon(g[j]) == canon(key) and rank(key) < rank(g[j]):
                        g[j] = key
            continue
        r, c = min(s // 7, 4), min(max(s % 7 - 1, 0), 4)
        free = [x for x in range(25) if x not in g]
        if not free:
            spill.append(key)
            continue
        best = min(free, key=lambda x: ((x // 5 - r) ** 2 + (x % 5 - c) ** 2, x))
        g[best] = key
    return g, ch, spill


def to7(s):
    return (s // 5) * 7 + s % 5 + 1


def read29(path, pre="g."):
    """what 0.3.29 (a rollback) reads from a layout file: the LAST g.<slot> line wins (java.util.Properties), empty = none"""
    out = {}
    for ln in open(path, encoding="utf-8").read().splitlines():
        if ln.startswith(pre) and "=" in ln:
            k, v = ln.split("=", 1)
            try:
                s = int(k[len(pre):])
            except ValueError:
                continue
            if v.strip():
                out[s] = v.strip()
            else:
                out.pop(s, None)
    return out


def page_rules(K, cmds, evs, what, prefix_ok="Skyy"):
    """T29.page_rules + the tab icon hook path (SkyyHubTabs/) allowed"""
    apps = SUI.Appends([(None if s is None else s.lstrip("#"), t) for ty, s, t, d in cmds if t is not None and ty and "Append" in ty])
    sets = [(s, d) for ty, s, t, d in cmds if ty == "Set"]
    try:
        SUI.check_page(apps, prefix_ok)
        K.check(True, "%s: check_page (markup rules, parents, no duplicate id)" % what)
    except Exception as e:
        K.check(False, "%s: check_page: %s" % (what, e))
    try:
        els = SUI.check_sky_paths(apps, tab_icons=True)
        allp = [m.group(0) for mk in apps.markups() for m in SUI._SKY_PATH_RE.finditer(SUI.render(mk))]
        K.check(not [p for p in allp if p.startswith('"../')], "%s: no texture path leaves Common/UI/Custom (%d)" % (what, len(allp)))
    except Exception as e:
        els = []
        K.check(False, "%s: sky paths: %s" % (what, e))
    try:
        SUI.assert_proven(apps, what=what)
        K.check(True, "%s: proven properties only" % what)
    except Exception as e:
        K.check(False, "%s: assert_proven: %s" % (what, e))
    ids = set()
    for _p, mk in apps:
        ids |= set(x.group(2) for x in DECL_RE.finditer(SUI.render(mk)))
    bs = [s for s, _t in evs]
    bad = [s for s, _d in sets if s.lstrip("#").split(".")[0] not in ids] + [s for s in bs if s.lstrip("#") not in ids]
    K.check(not bad, "%s: every b.set / binding names an element that exists (%d sets, %d bindings): %s" % (what, len(sets), len(bs), bad[:4]))
    return apps, els


def run_n30(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JArray, JImplements, JOverride
    K = HK.Child(out)
    hcls = os.path.join(scratch, "hcls_n")
    os.makedirs(hcls, exist_ok=True)
    os.chdir(scratch)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, hcls, jar], verify=True)
    E = T19.engine(scratch, hcls)
    JV = lambda n: JClass(PKG + n)
    Paths = E.Paths
    home = os.path.join(scratch, "home_n")
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
    Obj, Int, Dbl = JClass("java.lang.Object"), JClass("java.lang.Integer"), JClass("java.lang.Double")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    SysC = JClass("java.lang.System")
    same = lambda a, b_: (a is None and b_ is None) or (a is not None and b_ is not None and int(SysC.identityHashCode(a)) == int(SysC.identityHashCode(b_)))
    calls = []

    @JImplements("java.util.function.Function")
    class F(object):
        def __init__(self, r, tag=""):
            self.r, self.tag = r, tag

        @JOverride
        def apply(self, x):
            try:
                calls.append((self.tag, [str(v) for v in x] if hasattr(x, "__len__") and not isinstance(x, str) else str(x)))
            except Exception:
                calls.append((self.tag, str(x)))
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

    def cmd_on(*names):
        for n_ in names:
            E.CM.cmds.put(n_, E.U.allocateInstance(JClass("skyymenu19.Cmd").class_))

    def cmd_off(*names):
        for n_ in names:
            E.CM.cmds.remove(n_)

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

    def flush():
        time.sleep(0.6)
        ML.flushAll()

    def lines():
        return [str(x) for x in E.CM.lines]

    # ================================================================ ICONS (the jar)
    z = zipfile.ZipFile(jar)
    names = set(z.namelist())
    w3 = ["HubCharacter", "HubStorage", "HubMarket", "HubSmithing", "HubWorld", "HubSocial", "HubSettings", "Trees", "Class", "Profiles", "Requip",
          "Gear", "Upgrade", "Explore", "Quests", "Merchants", "Layout"]
    pngs = {}
    for n_ in w3:
        js = "Server/Item/Items/Utility/Skyy_Menu_Icon_%s.json" % n_
        pp = "Common/Icons/ItemsGenerated/Skyy_Menu_Icon_%s.png" % n_
        ok = js in names and pp in names
        if ok:
            d = z.read(pp)
            j = json.loads(z.read(js).decode("utf-8"))
            ok = d[:8] == b"\x89PNG\r\n\x1a\n" and struct.unpack(">II", d[16:24]) == (64, 64) and d[24:26] == b"\x08\x06" and j["Icon"] == pp[7:] \
                and j.get("Variant") is True and "Categories" not in j
            pngs[n_] = d
        K.check(ok, "ICONS: wave-3 item %s ships (JSON + 64 x 64 RGBA PNG, hidden)" % n_)
    allpng = [z.read(n_) for n_ in names if n_.startswith("Common/Icons/ItemsGenerated/") and n_.endswith(".png")]
    K.check(all(allpng.count(d) == 1 for d in pngs.values()), "ICONS: every wave-3 picture differs from every other icon picture in the jar")
    man = json.load(open(os.path.join(ROOT, "art", "hub-tab-icons", "manifest.json"), encoding="utf8"))
    tart = [n_ for n_ in names if n_.startswith("Common/UI/Custom/SkyyHubTabs/")]
    good = 0
    for f_ in man["files"]:
        if f_["path"].startswith("hubrow_") or not f_["path"].endswith(".png"):
            continue
        jp = "Common/UI/Custom/SkyyHubTabs/" + f_["path"][:-4] + "@2x.png"
        if jp in names and hashlib.sha256(z.read(jp)).hexdigest() == f_["sha256"]:
            good += 1
    K.check(len(tart) == 64 and good == 64, "ICONS: the 32 tab icons (+ _on) = art/hub-tab-icons byte for byte at SkyyHubTabs/<hub>_<tab>@2x.png (%d / %d)" % (len(tart), good))
    K.check(not [n_ for n_ in names if "SkyyHubTabs" in n_ and not n_.startswith("Common/UI/Custom/")], "ICONS: no tab art outside Common/UI/Custom")

    # ================================================================ REG
    cmd_on("smithing", "reforge", "upgrade", "identify", "craft", "quests", "merchants", "explore", "requip", "vault", "ah", "bazaar", "pets",
           "party", "guild", "tree", "class", "collections", "profiles", "skyyhud", "multitool")
    # an owner that put its tab BEFORE SkyyMenu (SkyyBank): kept
    bankTab = HB.put("storage", "bank", "SkyyBank", "Bank", 40, "bank", None, None)
    HB.mine().remove("hub:tab:storage:bank")    # it is the other jar's array, not ours
    n = int(MH.register())
    K.eq(n, 7, "REG: Menu's 7 own tabs put")
    own = ["character:stats", "world:teleport", "social:players", "settings:settings", "settings:layout", "settings:mods", "settings:setup"]
    K.check(all(br.get("hub:tab:" + t) is not None and len(br.get("hub:tab:" + t)) == 7 and str(br.get("hub:tab:" + t)[6]) == t.replace(":", "_") for t in own),
            "REG: Menu's own tabs carry their tab icon (putIcon, element 6 = <hub>_<tab>)")
    vt = [(h, t) for h, t, o, m, l, c in SUI.HUB_TABS if m != "SkyyMenu" and c and (h, t) != ("smithing", "multitool")]
    K.check(int(MH.PROXIES) == len(vt) - 1, "REG: a stand-in tab for every contract tab nobody put (%d of %d; Bank kept)" % (int(MH.PROXIES), len(vt)))
    K.check(same(br.get("hub:tab:storage:bank"), bankTab), "REG: an owner's tab put BEFORE SkyyMenu is never replaced")
    K.check(br.get("hub:tab:smithing:multitool") is None, "REG: no Multitool tab (Skyy: 'we scrapped the multitool menu')")
    sg = br.get("hub:tab:smithing:gear")
    K.check(sg is not None and str(sg[1]) == "Gear" and str(sg[3]) == "smithing" and str(sg[6]) == "smithing_gear" and sg[4] is not None,
            "REG: Smithing > Gear = a stand-in running gear:fn:smithing, else /smithing (icon smithing_gear)")
    K.check([str(t[0]) for t in HB.tabs("smithing", u)] == ["gear", "recipes", "reforge", "upgrade", "identify"], "REG: the Smithing hub has its 5 pages")
    cmd_off("upgrade")
    K.check([str(t[0]) for t in HB.tabs("smithing", u)] == ["gear", "recipes", "reforge", "identify"], "REG: a stand-in hides while its command is missing")
    cmd_on("upgrade")
    dw = br.get("hub:def:world")
    K.check(dw is not None and str(dw[3]) == "teleport" and str(dw[2]) == "Skyy_Menu_Icon_HubWorld", "REG: hub:def:world = {World, travel, HubWorld icon, default tab teleport}")
    K.check(len(set(str(br.get("hub:def:" + h)[2]) for h in SUI.HUBS)) == 7, "REG: the 7 hubs wear 7 different icons")
    # an owner that puts its tab AFTER SkyyMenu replaces the stand-in; clearAll then leaves it alone
    late = JArray(Obj)(["SkyyQuests", "Quests", Int(40), "quests", None, None])
    br.put("hub:tab:world:quests", late)

    # ================================================================ RUN-TIME NO-DUPLICATE CHECK (every entry + Add lists + row 1)
    hm = openm(P)
    cand = [str(k) for k in hm.candidates(True, True)]
    looks = dict((k, hm.look(k, True)) for k in cand)
    icons = [(k, str(looks[k][0])) for k in cand if looks[k] is not None and str(looks[k][5]) in ("ok", "dim") and not k.startswith("warp:")]
    dupi = sorted(set(i for k, i in icons if [j for _k, j in icons].count(i) > 1))
    K.check(not dupi, "NODUP: every + Add entry wears its own icon item (%d entries): shared %s" % (len(icons), [(i, [k for k, j in icons if j == i]) for i in dupi]))
    pages = [canon(k) for k in cand]
    K.check(len(pages) == len(set(pages)), "NODUP: + Add lists every page once (%d)" % len(cand))
    K.check("hub:world" not in cand and "tab:world:teleport" in cand and "hub:character" not in cand and "tab:character:skills" in cand,
            "NODUP: World and Teleport are one entry (Teleport); Character opens on Skills (one entry)")
    rowicons = [str(x[2]) for x in HB.hubs()]
    K.check(len(rowicons) == 8 and len(set(rowicons)) == 8 and not set(rowicons) & set(i for k, i in icons if not k.startswith("hub:")),
            "NODUP: row 1 icons differ from each other and from every page icon")
    K.check(looks.get("tab:storage:pocket") is not None and str(looks["tab:storage:pocket"][0]) == "Skyy_Menu_Icon_PocketDimension"
            and str(hm.look("hub:storage", True)[0]) == "Skyy_Menu_Icon_HubStorage", "NODUP: Storage and Pocket Dimension look different")
    K.check(str(hm.look("tab:character:class", True)[0]) == "Skyy_Menu_Icon_Class" and str(hm.look("tab:character:profiles", True)[0]) == "Skyy_Menu_Icon_Profiles",
            "NODUP: Class and Profiles have their own icons")

    # ================================================================ SMITH
    del calls[:]
    br.put("gear:fn:smithing", F(TRUE, "gear"))
    hm = openm(P)
    pg, sent = slot(P, hm, 13)
    K.check(("gear", [str(u), "craft"]) in calls and "coming soon" not in str(hm.status).lower(),
            "SMITH: the Home Smithing tile opens SkyyGear's page (gear:fn:smithing {uuid, craft}) %s" % calls)
    del calls[:]
    E.CM.lines.clear()
    r = str(MH.run(P.pr, "smithing"))
    K.check(r == "bridge" and calls and calls[0][0] == "gear", "SMITH: MenuHub.run(smithing) = the bridge (%s)" % r)
    br.remove("gear:fn:smithing")
    E.CM.lines.clear()
    r = str(MH.run(P.pr, "smithing"))
    K.check(r == "command" and lines() == ["smithing"], "SMITH: without the bridge -> /smithing as the player (%s %s)" % (r, lines()))
    E.CM.lines.clear()
    r = str(HB.goHub(P.pr, "smithing"))
    K.check(r == "command" and lines() == ["smithing"], "SMITH: another mod's row 1 (kit goHub) -> /smithing too (%s)" % r)
    body = str(hm.look("hub:smithing", True)[2])
    K.check("coming soon" not in body.lower() and "Gear" in body, "SMITH: the Smithing tile's text lists its pages (%s)" % body.replace("\n", " | "))
    cmd_off("smithing", "reforge", "upgrade", "identify", "craft")
    n0 = len(E.sent(P))
    r = str(MH.run(P.pr, "smithing"))
    K.check(r == "soon" and "coming soon" not in E.strs_of(P, n0).lower(), "SMITH: no Smithing page at all = one plain chat line (%s)" % r)
    cmd_on("smithing", "reforge", "upgrade", "identify", "craft")

    # ================================================================ HOME
    hm = openm(P)
    c, ev = build_page(hm, P)
    apps, els = page_rules(K, c, ev, "HOME", "SkyyM")
    root = apps[0][1]
    K.check(root.startswith("Group #SkyyMHm ") and tuple(map(int, WH_RE.search(root).groups())) == (1600, 926), "HOME: root 1600 x 926 (%s)" % root[:50])
    gmk = [mk for p_, mk in apps if mk.startswith("ItemGrid #SkyyMGrid")][0]
    K.check("SlotSize: 120" in gmk and "SlotIconSize: 88" in gmk and "SlotsPerRow: 5" in gmk and "AreItemsDraggable: false" in gmk, "HOME: 5 x 5 grid of 120 px slots, 88 px icons")
    K.check(hm.gridN == 25 and len(hm.grid) == 25 and dict((i, str(k)) for i, k in enumerate(hm.grid) if k is not None) == HOME_DEF,
            "HOME: the default grid = Teleport in the centre (12) + 6 hubs, no World tile")
    rowb = [mk for p_, mk in apps if p_ == "SkyyMBRow" and mk.startswith("Button")]
    K.check(len(rowb) == 8 and "Height: 48" in rowb[0] and "SkyyKit/Primary.png" in rowb[0] and all("SkyyKit/Tertiary.png" in mk for mk in rowb[1:]),
            "HOME: big row 1 = 8 buttons of 48 px, Home active")
    ricons = [mk for p_, mk in apps if (p_ or "").startswith("SkyyMBR") and mk.startswith("ItemIcon")]
    K.check(len(ricons) == 8 and all("Width: 32" in mk for mk in ricons), "HOME: row 1 shows 8 icons of 32 px")
    K.check(not any(p_ and p_.endswith("HubRow") for p_, mk in apps) and any("SkyyMHmTitle" in mk for p_, mk in apps) and "HeaderOrnament" in els,
            "HOME: the title bar = crest + title (row 1 moved into the body)")
    K.check(any(s_ == "#SkyyMHmHubClose" and "hub:close" in t for s_, t in ev), "HOME: the close X is bound")
    you = [mk for p_, mk in apps if mk.startswith("Button #SkyyMHmYou")]
    K.check(you and "Width: 456" in you[0], "HOME: You is 456 px wide")
    K.check(any(p_ == "SkyyMHmNow" and "SkyyMHmNowE" in mk for p_, mk in apps), "NOW: empty = 'Nothing waiting' (the panel always shows)")

    def hpx(sel, kind="Height"):
        mk = [mk for p_, mk in apps if ("#%s " % sel) in mk][0]
        return int(re.search(kind + r": (\d+)", mk).group(1))
    gtop = int(re.search(r"Top: (\d+)", gmk).group(1))
    gap5 = [mk for p_, mk in apps if p_ == "SkyyMHmMid" and mk.startswith("Group { Anchor: (Height:")]
    brow = [mk for p_, mk in apps if mk.startswith("Group #SkyyMBRow")][0]
    cy = 38 + 24 + int(re.search(r"Height: (\d+)", brow).group(1)) + int(re.search(r"Bottom: (\d+)", brow).group(1)) + hpx("SkyyMHmMidT") \
        + int(H_RE.search(gap5[0]).group(1)) + gtop + 2 * 120 + 60 - 926 // 2
    gapw = [mk for p_, mk in apps if p_ == "SkyyMHmMain" and mk.startswith("Group { Anchor: (Width:")]
    cx = 24 + hpx("SkyyMHmYou", "Width") + int(re.search(r"Width: (\d+)", gapw[0]).group(1)) + 2 * 120 + 60 - 1600 // 2
    K.eq((cx, cy), (0, 4), "HOME: the centre slot sits at the page centre + (0, +4) = the 0.3.28 slot 13 spot (from the built markup)")
    # CLICK the centre -> Teleport in place
    pg, sent = slot(P, hm, 12)
    K.check(same(pg, hm) and str(hm.view) == "tp" and sent, "CLICK: Home centre -> Teleport in place")
    c, ev = build_page(hm, P)
    apps, els = page_rules(K, c, ev, "TELEPORT", "SkyyM")
    K.check(tuple(map(int, WH_RE.search(apps[0][1]).groups())) == (1300, 962), "TP: root 1300 x 962")
    tabs = [mk for p_, mk in apps if p_ == "SkyyMBTabs" and mk.startswith("Button")]
    tic = [mk for p_, mk in apps if (p_ or "").startswith("SkyyMBT") and "SkyyHubTabs/" in mk]
    K.check(len(tabs) >= 3 and "Tab_Selected" in tabs[0] and "Height: 56" in tabs[0] and any("SkyyHubTabs/world_teleport_on.png" in mk for mk in tic),
            "TP: big row 2 = the World tabs (Teleport active, 56 px, its icon _on)")
    K.check(len(tic) == len(tabs), "TP: every World tab shows its icon behind the word (%d / %d)" % (len(tic), len(tabs)))
    lead = [mk for p_, mk in apps if p_ == "SkyyMTpRow" and mk.startswith("Group { Anchor: (Width:")]
    gmk = [mk for p_, mk in apps if mk.startswith("ItemGrid #SkyyMGrid")][0]
    btab = [mk for p_, mk in apps if mk.startswith("Group #SkyyMBTabs")][0]
    cx = 24 + int(re.search(r"Width: (\d+)", lead[0]).group(1)) + 2 * 120 + 60 - 1300 // 2
    cy = 38 + 24 + 48 + 8 + int(re.search(r"Height: (\d+)", btab).group(1)) + int(re.search(r"Bottom: (\d+)", btab).group(1)) \
        + int(re.search(r"Top: (\d+)", gmk).group(1)) + 2 * 120 + 60 - 962 // 2
    K.eq((cx, cy), (0, 4), "TP: its centre slot is the same screen spot as Home's (from the built markup)")
    K.check(dict((i, str(k)) for i, k in enumerate(hm.grid) if k is not None) == TP_DEF and str(hm.acts[12]) == "cmdc:hub", "TP: default My Island | Hub (centre) | Spawn")
    E.CM.lines.clear()
    hm2 = openm(P)
    slot(P, hm2, 12)
    slot(P, hm2, 12)
    K.check(lines() == ["hub"], "FLOW: open -> centre (Teleport) -> centre (Hub) runs /hub (%s)" % lines())
    hm = openm(P, "tp")
    E.CM.lines.clear()
    pg, sent = click(P, hm, "hub:island")
    K.check(lines() == ["island menu"], "TP: a row-2 tab click opens that page (Island -> /island menu) %s" % lines())
    hm = openm(P, "tp")
    pg, sent = click(P, hm, "hub:h:home")
    K.check(same(pg, hm) and str(hm.view) == "main", "TP: row 1 Home -> Home in place")
    pg, sent = click(P, hm, "hub:close")
    K.check(PGM(P) is None, "HOME: the close X closes")

    # ================================================================ NOW
    def hud(x):
        return JArray(Obj)(["Tutorial", "1 / 3", "Chop 5 logs", "5/5", Dbl(1.0), "", Int(-1), TRUE, "Mine 10 iron", "3/10", Dbl(0.3), "", Int(-1), FALSE])
    br.put("quest:fn:hud", F(hud, "hud"))
    br.put("gear:fn:smithing", F(TRUE, "gear"))
    br.put("home:alert:Test", F("Your shard is ready|world:island", "alert"))
    _hb = P.slots["hotbar"].getInventory()
    _c = _hb.getClass()
    _m = None
    while _c is not None and _m is None:
        for _mm in _c.getDeclaredMethods():
            if str(_mm.getName()) == "internal_setSlot":
                _m = _mm
        _c = _c.getSuperclass()
    _m.setAccessible(True)
    _m.invoke(_hb, JArray(Obj)([JClass("java.lang.Short")(2), IS("Skyy_Unid_Bag_Rare", 2)]))   # the test stub item refuses addItemStack
    K.check(E.count(P, "Skyy_Unid_Bag_Rare") == 2 and int(JV("MenuUtil").countPrefix(P.pl, "Skyy_Unid_Bag_")) == 2,
            "NOW: 2 mystery bags in the hotbar (E.count %d, MenuUtil.countPrefix = %d, count %d)" % (E.count(P, "Skyy_Unid_Bag_Rare"), int(JV("MenuUtil").countPrefix(P.pl, "Skyy_Unid_Bag_")), int(JV("MenuUtil").count(P.pl, "Skyy_Unid_Bag_Rare"))))
    hm = openm(P)
    c, ev = build_page(hm, P)
    sets = dict((s_, d) for ty, s_, t, d in c if ty == "Set")
    rows = [str(sets.get("#SkyyMHmA%d.Text" % i, "")) for i in range(8)]
    K.check('Quest: Mine 10 iron 3/10  >' in rows[0] and "2 mystery bags to identify  >" in rows[1] and "Your shard is ready  >" in rows[2],
            "NOW: quest (first undone task) / mystery bags / a mod alert, each a row with > (%s)" % rows[:3])
    E.CM.lines.clear()
    pg, sent = click(P, hm, "halert0")
    K.check(lines() == ["quests"], "NOW: the quest row opens World > Quests (/quests) %s" % lines())
    del calls[:]
    hm = openm(P)
    build_page(hm, P)
    pg, sent = click(P, hm, "halert1")
    K.check(("gear", [str(u), "identify"]) in calls, "NOW: the mystery bag row opens Smithing > Identify (gear:fn:smithing identify) %s" % calls)
    br.remove("quest:fn:hud")
    br.remove("home:alert:Test")

    # ================================================================ MISC: Invite to Guild, Health Regen, + Add on 25 slots
    pv = openm(P, "players")
    slot(P, pv, 10)     # the first online player (the op) -> their page
    i32 = [i for i in range(54) if pv.names[i] is not None and str(pv.names[i]).startswith("Invite to Guild")]
    K.check(i32 == [32], "MISC: a player's page has Invite to Guild at slot 32 (%s)" % i32)
    E.CM.lines.clear()
    slot(P, pv, 32)
    K.check(lines() == ["guild invite SkyyOp"], "MISC: Invite to Guild runs /guild invite <name> (%s)" % lines())
    SC = JV("StatsCalc")
    rows_ = JClass("java.util.ArrayList")()
    SC.mainTab(rows_, u, None)
    hr = [list(map(str, r_)) for r_ in rows_ if str(r_[0]) == "Health Regen"]
    K.check(hr and hr[0][1] == "-", "MISC: Stats Main > Health Regen without SkyySkills = '-' (%s)" % hr)
    br.put("skill:fn:hpregen", F(lambda x: JArray(JClass("java.lang.String"))(["3.5/s", "1.2/s in combat"]), "hp"))
    rows_ = JClass("java.util.ArrayList")()
    SC.mainTab(rows_, u, None)
    hr = [list(map(str, r_)) for r_ in rows_ if str(r_[0]) == "Health Regen"]
    K.check(hr and hr[0][1:3] == ["3.5/s", "1.2/s in combat"] and len(rows_) <= int(SC.ROWS), "MISC: Health Regen = skill:fn:hpregen row (%s, %d rows)" % (hr, len(rows_)))
    hm = openm(P)
    click(P, hm, "fhedit")
    slot(P, hm, 0)
    K.check(int(hm.addSlot) == 0 and len(hm.addKeys) == 25, "EDIT: an empty slot opens + Add (25 per page)")
    k_tp = [i for i, k in enumerate(hm.addKeys) if k is not None and str(k) == "hub:world"]
    K.check(not k_tp, "EDIT: + Add never offers World while Teleport is on the grid")
    click(P, hm, "acancel")
    click(P, hm, "fedone")
    # FIX (ui.md 2026-10-16 HUD SHORTCUT OPENS THE EDITOR): the Settings > HUD shortcut runs /skyyhud straight away; no /skyyhud = the page path
    hm = openm(P)
    E.CM.lines.clear()
    hm.shortcut(P.ref, P.st, "tab:settings:hud")
    E.pump(P)
    K.check(lines() == ["skyyhud"], "FIX HUD: the Home shortcut Settings > HUD runs /skyyhud (the HUD editor) directly (%s)" % lines())
    K.check(str(hm.look("tab:settings:hud", True)[4]) == "sc:tab:settings:hud", "FIX HUD: the Home tile's click is the shortcut path (sc:tab:settings:hud)")
    hm = openm(P)
    E.CM.lines.clear()
    _ix = [i for i in range(int(hm.gridN)) if hm.acts is not None and hm.acts[i] is not None and str(hm.acts[i]) == "sc:tab:settings:hud"]
    if _ix:
        slot(P, hm, _ix[0])   # the tile on the grid, clicked like the player does (mslot -> acts -> click -> shortcut)
    else:
        hm.click(P.ref, P.st, 0, "sc:tab:settings:hud")   # not on this layout: the same click dispatch a placed tile uses
        E.pump(P)
    K.check(lines() == ["skyyhud"], "FIX HUD: clicking the Home tile itself (%s) runs /skyyhud, not the tab page (%s)" % ("slot %d" % _ix[0] if _ix else "click sc:", lines()))
    cmd_off("skyyhud")
    hm = openm(P)
    E.CM.lines.clear()
    n0 = len(E.sent(P))
    hm.shortcut(P.ref, P.st, "tab:settings:hud")
    E.pump(P)
    _t = E.strs_of(P, n0)
    K.check("skyyhud" not in lines() and "HUD editor is not on this server" in _t and _t.count("HUD editor is not on this server") == 1 and PGM(P) is not None and same(PGM(P), hm),
            "FIX HUD: without SkyyHud (/skyyhud) the shortcut says so in ONE chat line and the menu stays (%s)" % lines())
    cmd_on("skyyhud")

    # ================================================================ FOLD (the one-time 5 x 5 update on COPIES)
    live = os.path.join(LIVE_DIR, "layouts", SKYY + ".properties")
    cases = {}
    if os.path.isfile(live):
        cases["skyy"] = open(live, "rb").read()
    else:
        K.check(True, "FOLD: (no live layout of Skyy to copy)")
    hdr = "_name=X\n_v=1\nteleport=13\n_home=1\n_tp=1\n"
    cases["edges"] = (hdr + "g.7=hub:social\ng.14=tile:pocketdimension\ng.17=tab:world:teleport\ng.24=hub:world\ng.20=tab:character:skills\n"
                      "g.10=hub:character\ng.13=tile:skills\ng.6=tab:storage:bank\nt.17=tp:hub\nt.21=tp:island\n").encode()
    many = "".join("g.%d=warp:w%02d\n" % (s, s) for s in range(35))
    cases["many"] = (hdr + many).encode()
    # FIX 2: BOTH grids over-full - the Teleport pins that found no slot are named too (were dropped)
    cases["both"] = (hdr + many + "".join("t.%d=warp:t%02d\n" % (s, s) for s in range(35))).encode()
    cases["crlf"] = (hdr + "g.0=hub:market\ng.17=tab:world:teleport\n").replace("\n", "\r\n").encode()
    cases["bogus"] = (hdr + "g.28=bogus:x\ng.0=hub:market\n").encode()   # FIX: an unknown key's line is never blanked
    cases["old28"] = b"_v=1\nteleport=13\nbank=21\nvault=29\nplayers=0\nsettings=17\nmods=35\n"
    E.CM.cmds.put("warp", E.U.allocateInstance(JClass("skyymenu19.Cmd").class_))
    uids = {}
    for i, (nm, data) in enumerate(sorted(cases.items())):
        uid = E.UUID.fromString(SKYY) if nm == "skyy" else E.UUID.fromString("00000000-0000-0000-0000-0000000001%02d" % i)
        uids[nm] = uid
        open(os.path.join(lay_dir, str(uid) + ".properties"), "wb").write(data)
    ML.OWN.clear()
    hist = os.path.join(home, "config-history")
    before = set(os.listdir(hist)) if os.path.isdir(hist) else set()
    for nm, uid in sorted(uids.items()):
        g = ML.grid(uid, 0)
        got = dict((i, str(k)) for i, k in enumerate(g) if k is not None)
        if nm == "old28":
            K.check(got.get(12) == "tab:world:teleport", "FOLD old28: the 0.3.28 layout -> hubs + Teleport in the centre (%s)" % got)
            continue
        g7 = read29(os.path.join(lay_dir, str(uid) + ".properties"))
        if nm == "bogus":
            g7.pop(28, None)     # not a key: the reader skips it
        exp, ch, sp = ref_fold(g7)
        K.eq(got, exp, "FOLD %s: the 5 x 5 grid = the independent rule" % nm)
        if nm == "many":
            K.check(len(got) == 25 and len(sp) == 10 and ML.SPILL.containsKey(str(uid)), "FOLD many: 25 kept, 10 wait in + Add (SPILL)")
        if nm == "both":
            tsp = ref_fold(read29(os.path.join(lay_dir, str(uid) + ".properties"), "t."), True)[2]
            sv = str(ML.SPILL.get(str(uid)))
            K.check(len(tsp) == 10 and sv.startswith("20|") and all(k in sv for k in sp + tsp),
                    "FIX2 FOLD both: Home + Teleport spills are both kept (20, %s)" % sv[:60])
        if nm == "edges":
            K.check("hub:world" not in got.values() and got.get(12) == "tab:world:teleport" and "tile:skills" not in got.values()
                    and "hub:character" not in got.values() and "tab:character:skills" in got.values(),
                    "FOLD edges: World + Teleport -> Teleport; Character + Skills tile + Skills tab -> the Skills tab (%s)" % got)
            tg = dict((i, str(k)) for i, k in enumerate(ML.grid(uid, 1)) if k is not None)
            K.eq(tg, ref_fold(read29(os.path.join(lay_dir, str(uid) + ".properties"), "t."), True)[0], "FOLD edges: the Teleport grid folds too")
    flush()
    after = set(os.listdir(hist)) if os.path.isdir(hist) else set()
    newh = sorted(after - before)
    for nm, uid in sorted(uids.items()):
        f_ = os.path.join(lay_dir, str(uid) + ".properties")
        now_ = open(f_, "rb").read()
        old_ = cases[nm]
        hs = [h for h in newh if str(uid) in h]
        if nm == "skyy":
            K.check(now_ == old_ and not hs, "FOLD skyy: Skyy's live grid fits the 5 x 5 grid - the file is not written, no History copy")
            continue
        K.check(len(hs) == 1 and open(os.path.join(hist, hs[0]), "rb").read() == old_, "FOLD %s: ONE verified History copy = the old bytes" % nm)
        K.check(now_.startswith(old_) and b"_g5=1" in now_[len(old_):], "FOLD %s: the old bytes kept, the update appended with the run-once marker" % nm)
        if nm == "crlf":
            K.check(b"\r\n" in now_[len(old_):] and b"\n" not in now_[len(old_):].replace(b"\r\n", b""), "FOLD crlf: the appended lines keep CRLF")
        if nm == "bogus":
            K.check(b"g.28=" not in now_[len(old_):] and read29(f_).get(28) == "bogus:x",
                    "FIX FOLD bogus: the update never blanks a line the reader skipped (g.28=bogus:x stays as it was)")
        if nm != "old28":
            g7 = read29(f_)
            if nm == "bogus":
                g7.pop(28, None)
            exp5 = dict((i, str(k)) for i, k in enumerate(ML.grid(uid, 0)) if k is not None)
            K.eq(g7, dict((to7(s), k) for s, k in exp5.items()), "FOLD %s: a 0.3.29 parse of the new file = the same 5 x 5 grid (rollback)" % nm)
    # no second update: re-read from disk, flush, nothing changes
    snap = dict((f_, open(os.path.join(lay_dir, f_), "rb").read()) for f_ in os.listdir(lay_dir))
    ML.OWN.clear()
    for nm, uid in sorted(uids.items()):
        ML.grid(uid, 0)
    flush()
    K.check(snap == dict((f_, open(os.path.join(lay_dir, f_), "rb").read()) for f_ in os.listdir(lay_dir)) and set(os.listdir(hist)) == after,
            "FOLD: a second read writes nothing (the update ran once)")
    # the spill is told once (chat + the info line), Right now says so before
    Pm = mkp(uids["many"], "SkyyMany")
    ML.OWN.clear()
    ML.SPILL.clear()
    open(os.path.join(lay_dir, str(uids["many"]) + ".properties"), "wb").write(cases["many"])
    ML.grid(uids["many"], 0)
    al = br.get("home:alert:SkyyMenu").apply(uids["many"])
    K.check(al is not None and "did not fit|edit" in str(al), "FOLD many: Right now says 'Some shortcuts did not fit' (%s)" % al)
    n0 = len(E.sent(Pm))
    hm = openm(Pm)
    c, ev = build_page(hm, Pm)
    info = [d for ty, s_, t, d in c if ty == "Set" and s_ == "#SkyyMHmInfo.Text"]
    txt_ = E.strs_of(Pm, n0)
    K.check(txt_.count("10 shortcuts did not fit the 5 x 5 grid") >= 2 and "[SkyWynn Menu] 10 shortcuts did not fit" in txt_,
            "FOLD many: told in chat + the info line when Home opens")
    K.check(info and "did not fit" not in str(info[0]), "FOLD many: told once (the next draw shows the usual hint)")
    sets = dict((s_, d) for ty, s_, t, d in c if ty == "Set")
    rows = [str(sets.get("#SkyyMHmA%d.Text" % i, "")) for i in range(8)]
    K.check(any("Some shortcuts did not fit  >" in r_ for r_ in rows) and len(E.strs_of(Pm, n0).split("[SkyWynn Menu] 10 shortcuts")) == 2,
            "FIX FOLD many: Right now shows 'Some shortcuts did not fit' on Home after the one-time chat note (%s)" % rows[:3])
    click(Pm, hm, "fhedit")
    K.check(not ML.SPILL.containsKey(str(uids["many"])), "FIX FOLD many: opening Edit shortcuts clears the note")
    click(Pm, hm, "fedone")
    c, ev = build_page(hm, Pm)
    sets = dict((s_, d) for ty, s_, t, d in c if ty == "Set")
    K.check(not [i for i in range(8) if "did not fit" in str(sets.get("#SkyyMHmA%d.Text" % i, ""))], "FIX FOLD many: the Right now row is gone after Edit shortcuts")
    cl = " ".join(str(x) for x in JV("CfgLog").snap() if ("menu.layout[%s]" % uids["many"]) in str(x))
    K.check("no free slot" in cl and "warp:w" in cl.split("no free slot", 1)[-1] and "undo:" in cl,
            "FIX FOLD many: config-changes.log names the pins that found no slot + the undo")
    cb = " ".join(str(x) for x in JV("CfgLog").snap() if ("menu.layout[%s]" % uids["both"]) in str(x))
    K.check("warp:w34" in cb and "warp:t34" in cb, "FIX2 FOLD both: config-changes.log names the Home AND the Teleport pins that found no slot")
    K.eq(str(ML.joinSpill(None, "2|a,b")), "2|a,b", "FIX2 joinSpill: Teleport only")
    K.eq(str(ML.joinSpill("1|x", "2|a,b")), "3|x,a,b", "FIX2 joinSpill: Home + Teleport")
    # the server default: a column-6 pin folded + written once
    dfile = os.path.join(home, "layout-default.properties")
    dold = (hdr + "g.13=hub:bazaar\ng.20=hub:market\ng.17=tab:world:teleport\n").encode()
    open(dfile, "wb").write(dold)
    ML.loadDefault()
    flush()
    dnow = open(dfile, "rb").read()
    K.check(dnow.startswith(dold) and b"_g5=1" in dnow[len(dold):] and dict((i, str(k)) for i, k in enumerate(ML.grid(E.UUID.fromString("00000000-0000-0000-0000-00000000ffff"), 0)) if k is not None).get(14) == "hub:market",
            "FOLD default: the server default's column-6 pin moves in (row 2, column 4), written once by appending")
    # shutdown
    removed = int(MH.clearAll())
    K.check(br.get("hub:tab:world:quests") is not None and same(br.get("hub:tab:world:quests"), late) and same(br.get("hub:tab:storage:bank"), bankTab)
            and br.get("hub:tab:smithing:gear") is None and br.get("hub:def:world") is None,
            "REG: clearAll removes our tabs, defs and stand-ins - never an owner's (%d removed)" % removed)
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
        got.append(len(c) > 30 and mp.gridN == 25)
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
        res.append([n == 7, all(got), cleared >= 16])
    K.eq(res, [[True, True, True], [True, True, True]], "D: two starts on a COPY of the live Skyy_SkyyMenu: registry, Home + every Menu tab page built, cleared")
    a, b1, b2 = snaps
    ch1 = sorted(set(k for k in set(a) | set(b1) if a.get(k) != b1.get(k)))
    K.check(not [k for k in ch1 if "layouts" in k.replace("\\", "/") or "config-history" in k.replace("\\", "/")],
            "D: start 1 did not touch Skyy's layout (it fits the 5 x 5 grid) - changed: %s" % ch1)
    K.check(b1 == b2, "D: start 2 wrote nothing")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyMenu", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("n30", run_n30), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyMenu"))
