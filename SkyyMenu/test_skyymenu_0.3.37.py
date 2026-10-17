"""Harness for SkyyMenu 0.3.37 (round tp37: warps, island homes and homes on World > Teleport, Arrange, warp icons, the Void Charms icon;
tools/menu_0_3_37_patch.py). Build first:
    python tools/menu_0_3_37_patch.py && python SkyyMenu/build_skyymenu_0.3.37.py

    python SkyyMenu/test_skyymenu_0.3.37.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py - the 0.3.36 harness's way: -Xverify:all over the SkyyMenu 0.3.19 engine stand-ins):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.36 -> 0.3.37: exactly the listed members differ; the non-class entries = manifest, server.lang, the 11 warp icon
                items (JSON + PNG), the Void Charms icon item (JSON + new PNG, the old satchel PNG gone), the Character tab pair
  T    EXECUTED (stand-in TeleportPlugin with 4 warps; fake bridges island:fn:homes / gohome, essentials:fn:homes / gohome / warps):
       PAGES   every Teleport view passes the kit 1.7 rules + SUI.assert_menu_page (H.kit17_rules / H.menu17): all sources, Arrange,
               the + Add list, no bridges, a bridge that throws
       SOURCES the fixed spots (My Island | Hub | Spawn), then island homes, homes, warps (A-Z) in the free slots of rows 4 + 5; the tile
               icons (island home = My Island, home = WarpHome, a warp = its essentials:fn:warps theme's icon, no / unknown theme = the
               signpost); + Add lists island homes + homes; MenuLayout.okKey takes ihome: / zhome: (the name rule)
       CLICKS  an island home = island:fn:gohome {uuid, name} after the page closed; a home = essentials:fn:gohome -> "ok" closes the
               page, a refusal stays in the status line
       ARRANGE the foot button says Arrange; in Arrange the auto tiles are pick-up tiles; a click pins one where it is + picks it up, the
               next click moves it; saved per player (the layout file holds ihome:Farm) and restored by a new page; a new warp appears
               at the end; a deleted home's pinned tile hides
       DEGRADE no bridges = only the fixed spots + warps (signposts); a throwing bridge = the same, no exception
       ART     the jar's 11 warp icon PNGs = art/warp-icons (manifest sha256), the Void Charms icon item = art/void-charms-icon, the
               Character tab pair = art/void-charms-icon/hub-tab
  D    live     two starts on a scratch COPY of the live Skyy_SkyyMenu (the 0.3.35 harness's phase)
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, json, hashlib, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import skyyui as SUI
import hub_tab_harness as H

_s36 = importlib.util.spec_from_file_location("test_skyymenu_0_3_36", os.path.join(HERE, "test_skyymenu_0.3.36.py"))
T36 = importlib.util.module_from_spec(_s36)
_s36.loader.exec_module(T36)
T35 = T36.T35
T19 = T36.T19
jf = T36.jf

VERSION = "0.3.37"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.36.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "tp37", "menu")))
PKG = "com.skyy.menu."
LIVE_DIR = T35.LIVE_DIR
ADDED = []
EXPECT = {      # the class compare 0.3.36 -> 0.3.37
    'CfgFn': ['~m opExport'],   # the config kit's version text
    'CfgRows': ['~m header'],   # the config kit's version text
    'MenuData': ['+f ICON_IHOME', '+f ICON_ZHOME', '+f WI_ICON', '+f WI_THEME', '~<clinit>'],   # the warp icon table; Arrange + texts
    'MenuLayout': ['~m okTp'],   # ihome: / zhome: keys
    'MenuPage': ['+f autoAt', '+f ihs', '+f wth', '+f zhs', '+m addAuto', '+m goHome', '+m homesOf', '+m loadTp', '+m nameIn',
                 '+m themeIcon', '+m warpThemes', '~m candidates', '~m click', '~m dashEditClick', '~m fillAutoWarps', '~m fillDash',
                 '~m look', '~m warpTile', '~m buildDash'],   # buildDash: the Teleport hint text (Arrange) javassist inlines
    'OpsPage': ['~<clinit>'],   # the live SET versions the Admin page lists (tools/deploy_set.py moved on since 0.3.36 was built)
    'SkyyMenuPlugin': ['~m setup'],   # the ready line
}
WART = os.path.join(ROOT, "art", "warp-icons")
VART = os.path.join(ROOT, "art", "void-charms-icon")


def run_t(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JArray, JObject, JString, JImplements, JOverride
    K = HK.Child(out)
    hcls = os.path.join(scratch, "hcls_t")
    os.makedirs(hcls, exist_ok=True)
    os.chdir(scratch)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, hcls, jar], verify=True)
    E = T19.engine(scratch, hcls)
    JV = lambda n: JClass(PKG + n)
    Paths = E.Paths
    home = os.path.join(scratch, "home_t")
    os.makedirs(os.path.join(home, "layouts"), exist_ok=True)
    JV("PageGuard").STOP = False
    JV("PageGuard").EXEC = None
    ML = JV("MenuLayout")
    ML.DIR = Paths.get(os.path.join(home, "layouts"))
    ML.DEF_FILE = Paths.get(os.path.join(home, "layout-default.properties"))
    JV("SetStore").DIR = Paths.get(os.path.join(home, "settings"))
    JV("SetReg").ADMIN_FILE = Paths.get(os.path.join(home, "settings-defaults.properties"))
    JV("SetReg").registerOwn()
    JV("MenuIO").begin()
    MH, MD, MP = JV("MenuHub"), JV("MenuData"), JV("MenuPage")
    br = JV("MenuUtil").bridge()
    E.br = br
    UniC = JClass("com.hypixel.hytale.server.core.universe.Universe")
    byU = jf(UniC.class_, "playersByUuid").get(UniC.get())

    def mkp(uid, name):
        X = E.player(uid, name=name)
        byU.put(uid, X.pr)
        E.UniH.PL.add(X.pr)
        E.PLAYERS.add(X.pr)
        return X
    P = mkp(E.PLAIN, "SkyyPlain")
    u = P.pr.getUuid()
    PGM = lambda X: X.pm.getCustomPage()
    S_ = JClass("java.lang.String")
    SA = lambda xs: JArray(JString)([S_(x) for x in xs])
    MH.register()

    def openp(X, pg):
        X.pm.openCustomPage(X.ref, X.st, pg)
        E.pump(X)
        return pg

    def ev(X, pg, data):
        pg.handleDataEvent(X.ref, X.st, data)
        E.pump(X)
        return PGM(X)

    def slot(X, pg, i):
        return ev(X, pg, '{"a":"mslot","SlotIndex":%d}' % i)

    def foot(X, pg, w):
        return ev(X, pg, '{"a":"f%s"}' % w)

    def built(X, pg, what):
        _p, c, e = H.build_page(E, X, pg)
        apps = H.kit17_rules(K, c, e, what)
        H.menu17(K, apps, c, "world", what, subs=0, pager_ok=True)
        return c, e, apps

    ISc = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    AL = JClass("java.util.ArrayList")

    def icons(pg):
        """slot -> icon item id, drawn by fillDash on a fresh slot list (the same state build used)"""
        sl = AL()
        for _i in range(54):
            sl.add(None)
        pg.fillDash(sl)
        res = {}
        for i in range(54):
            gs = sl.get(i)
            if gs is None:
                continue
            st = [f.get(gs) for f in [jf(gs.getClass(), str(g.getName())) for g in gs.getClass().getDeclaredFields()]
                  if ISc.class_.isAssignableFrom(f.getType())]
            res[i] = str(st[0].getItemId()) if st and st[0] is not None else None
        return res

    same = lambda a_, b_: a_ is not None and b_ is not None and bool(a_.equals(b_))
    acts = lambda pg: dict((i, str(a)) for i, a in enumerate(list(pg.acts)) if a is not None)

    # ---------------- the stand-in TeleportPlugin (the SkyyEssentials 0.1.12 harness's way) with 4 warps
    TPP = JClass("com.hypixel.hytale.builtin.teleport.TeleportPlugin")
    Warp = JClass("com.hypixel.hytale.builtin.teleport.Warp")
    Mod = JClass("java.lang.reflect.Modifier")
    tp = E.U.allocateInstance(TPP.class_)
    fl = list(TPP.class_.getDeclaredFields())
    inst = [f for f in fl if Mod.isStatic(f.getModifiers()) and f.getType() == TPP.class_]
    wmap = [f for f in fl if not Mod.isStatic(f.getModifiers()) and JClass("java.util.Map").class_.isAssignableFrom(f.getType())]
    loadf = [f for f in fl if not Mod.isStatic(f.getModifiers()) and str(f.getType().getName()) in ("boolean", "java.util.concurrent.atomic.AtomicBoolean")]
    K.check(len(inst) == 1 and wmap and loadf, "SETUP: TeleportPlugin stand-in fields found")
    WARPS = JClass("java.util.concurrent.ConcurrentHashMap")()
    for f in inst:
        f.setAccessible(True)
        f.set(None, tp)
    for f in wmap:
        f.setAccessible(True)
        f.set(tp, WARPS)
    for f in loadf:
        f.setAccessible(True)
        if str(f.getType().getName()) == "boolean":
            f.setBoolean(tp, True)
        else:
            f.set(tp, JClass("java.util.concurrent.atomic.AtomicBoolean")(True))

    def mkwarp(name):
        w_ = Warp()
        for f in Warp.class_.getDeclaredFields():
            f.setAccessible(True)
            n_ = str(f.getName())
            if n_ == "id":
                f.set(w_, name)
            elif n_ == "world":
                f.set(w_, "default")
            elif n_ == "creator":
                f.set(w_, "Skyy")
        WARPS.put(name.lower(), w_)
    for n_ in ("mines", "dock", "hub", "plain"):
        mkwarp(n_)
    K.check(TPP.get() is not None and TPP.get().isWarpsLoaded() and WARPS.size() == 4, "SETUP: 4 warps loaded")

    # ---------------- fake bridges
    CALLS = []
    STATE = {"ih": ["Farm", "Mine"], "zh": ["home", "base"], "wt": ["dock|fishing", "hub|hub", "mines|mining", "plain|warp"], "zgo": "ok", "throw": False}

    @JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, kind):
            self.kind = kind

        @JOverride
        def apply(self, a):
            if STATE["throw"]:
                raise RuntimeError("bridge down")
            if self.kind in ("ih", "zh"):
                CALLS.append((self.kind, str(a)))
                return SA(STATE[self.kind])
            if self.kind == "wt":
                return SA(STATE["wt"])
            CALLS.append((self.kind, str(a[0]), str(a[1])))
            return S_("+Teleporting to your island home %s." % a[1]) if self.kind == "igo" else S_(STATE["zgo"])
    BR = {"island:fn:homes": Fn("ih"), "island:fn:gohome": Fn("igo"), "essentials:fn:homes": Fn("zh"),
          "essentials:fn:gohome": Fn("zgo"), "essentials:fn:warps": Fn("wt")}
    for k_, v_ in BR.items():
        br.put(k_, v_)

    auto = [int(x) for x in MD.TP_AUTO]
    WANT = ["ihome:Farm", "ihome:Mine", "zhome:home", "zhome:base", "warp:dock", "warp:hub", "warp:mines", "warp:plain"]

    # ---------------- SOURCES + PAGES
    pg = openp(P, MP(P.pr, "tp"))
    built(P, pg, "Teleport (fixed spots, island homes, homes, warps)")
    a0 = acts(pg)
    K.eq([a0.get(s) for s in (11, 12, 13)], ["cmdc:island", "cmdc:hub", "spawn"], "SOURCES: the fixed spots My Island | Hub | Spawn (row 3) as before")
    got = [a0.get(s) for s in auto if a0.get(s)]
    K.eq(got, WANT, "SOURCES: rows 4 + 5 = island homes, homes, then warps A-Z (in that order)")
    ic = icons(pg)
    want_ic = {"ihome:Farm": "Skyy_Menu_Icon_MyIsland", "zhome:home": "Skyy_Menu_Icon_WarpHome", "warp:dock": "Skyy_Menu_Icon_WarpFishing",
               "warp:hub": "Skyy_Menu_Icon_Hub", "warp:mines": "Skyy_Menu_Icon_WarpMining", "warp:plain": "Skyy_Menu_Icon_Warp"}
    byact = dict((a0[s], ic.get(s)) for s in auto if a0.get(s))
    K.eq(dict((k, byact.get(k)) for k in want_ic), want_ic, "SOURCES: tile icons (island home, home, warps by their essentials:fn:warps theme)")
    names = dict((str(a), str(n)) for a, n in zip(list(pg.acts), list(pg.names)) if a is not None)
    K.check(names.get("ihome:Farm") == "Island home Farm" and names.get("zhome:base") == "Home base", "SOURCES: tile names (%s, %s)" % (names.get("ihome:Farm"), names.get("zhome:base")))
    K.check(not [v for v in names.values() if v == "No warps yet"], "SOURCES: no 'No warps yet' while warps exist")
    K.check(bool(ML.okKey("ihome:Farm", True)) and bool(ML.okKey("zhome:base", True)) and not bool(ML.okKey("ihome:bad name", True))
            and not bool(ML.okKey("zhome:", True)), "SOURCES: MenuLayout.okKey takes ihome: / zhome: with the name rule")
    cands = [str(x) for x in pg.candidates(False, False)]
    K.check(all(k in cands for k in WANT[:4]) and cands.index("ihome:Farm") < cands.index("warp:dock"), "SOURCES: + Add lists island homes + homes (before the warps)")
    # theme fallbacks
    STATE["wt"] = ["dock|nosuchtheme", "mines|mining"]
    pg.refresh()
    E.pump(P)
    ic2 = icons(pg)
    a2 = acts(pg)
    K.check(dict((a2[s], ic2.get(s)) for s in auto if a2.get(s)).get("warp:dock") == "Skyy_Menu_Icon_Warp", "SOURCES: an unknown theme = the signpost")
    STATE["wt"] = ["dock|fishing", "hub|hub", "mines|mining", "plain|warp"]

    # ---------------- CLICKS
    si = [s for s in auto if a0.get(s) == "ihome:Farm"][0]
    del CALLS[:]
    after = slot(P, pg, si)
    K.check(("igo", str(u), "Farm") in CALLS, "CLICKS: an island home calls island:fn:gohome {uuid, Farm} (%s)" % CALLS)
    K.check(not same(after, pg), "CLICKS: the page closed first (like My Island)")
    pg = openp(P, MP(P.pr, "tp"))
    built(P, pg, "Teleport (reopened)")
    sz = [s for s, a in acts(pg).items() if a == "zhome:base"][0]
    del CALLS[:]
    after = slot(P, pg, sz)
    K.check(("zgo", str(u), "base") in CALLS and not same(after, pg), "CLICKS: a home calls essentials:fn:gohome; 'ok' closes the page")
    pg = openp(P, MP(P.pr, "tp"))
    built(P, pg, "Teleport (reopened 2)")
    STATE["zgo"] = "you have no home called base."
    after = slot(P, pg, [s for s, a in acts(pg).items() if a == "zhome:base"][0])
    K.check(same(after, pg) and "no home called base" in str(pg.status), "CLICKS: a refused home stays on the page with the reason (%r)" % str(pg.status))
    STATE["zgo"] = "ok"

    # ---------------- ARRANGE
    c0, _e0, _a0 = built(P, pg, "Teleport (before Arrange)")
    K.check(any('"Arrange"' in (t or "") for ty, s, t, d in c0) and not any('"Edit"' in (t or "") for ty, s, t, d in c0),
            "ARRANGE: the Teleport foot button says Arrange (was Edit)")
    foot(P, pg, "hedit")
    K.check(bool(pg.editing), "ARRANGE: the foot button opens Arrange")
    built(P, pg, "Teleport (Arrange)")
    aa = list(pg.autoAt)
    K.eq([aa[s] for s in auto if aa[s] is not None], WANT, "ARRANGE: the auto tiles are pick-up tiles in Arrange (autoAt)")
    K.check(all(str(pg.acts[s]) == "eslot" for s in auto if aa[s] is not None), "ARRANGE: each auto tile is clickable (eslot)")
    fs = [s for s in auto if aa[s] == "ihome:Farm"][0]
    slot(P, pg, fs)
    g1 = [None if x is None else str(x) for x in ML.grid(u, 1)]
    K.check(g1[fs] == "ihome:Farm" and int(pg.editSel) == fs, "ARRANGE: a click pins Farm where it is and picks it up (slot %d)" % fs)
    slot(P, pg, 0)
    g2 = [None if x is None else str(x) for x in ML.grid(u, 1)]
    K.check(g2[0] == "ihome:Farm" and g2[fs] is None and int(pg.editSel) == -1, "ARRANGE: the next click moves it to slot 0 (%s)" % g2[:5])
    pg.addSlot = 1
    built(P, pg, "Teleport (Arrange, + Add list)")
    pg.addSlot = -1
    foot(P, pg, "edone")
    K.check(not bool(pg.editing), "ARRANGE: Done leaves Arrange")
    pg2 = openp(P, MP(P.pr, "tp"))
    built(P, pg2, "Teleport (restored)")
    a3 = acts(pg2)
    K.check(a3.get(0) == "ihome:Farm" and "ihome:Farm" not in [a3.get(s) for s in auto], "ARRANGE: a new page shows Farm at slot 0, not in the auto rows")
    mkwarp("zzz")
    pg2.refresh()
    E.pump(P)
    a4 = acts(pg2)
    K.check([a4.get(s) for s in auto if a4.get(s)][-1] == "warp:zzz", "ARRANGE: a new warp appears at the end")
    STATE["ih"] = ["Mine"]
    pg2.refresh()
    E.pump(P)
    K.check(acts(pg2).get(0) is None, "ARRANGE: a deleted island home's pinned tile hides")
    STATE["ih"] = ["Farm", "Mine"]
    JV("MenuIO").stop(2000)
    lay = ""
    for root_, _d, fs_ in os.walk(os.path.join(home, "layouts")):
        for f_ in fs_:
            lay += open(os.path.join(root_, f_), encoding="utf8", errors="replace").read()
    K.check("ihome:Farm" in lay, "ARRANGE: the layout file holds ihome:Farm (saved per player)")
    JV("MenuIO").begin()

    # ---------------- DEGRADE
    for k_ in BR:
        br.remove(k_)
    pg3 = openp(P, MP(P.pr, "tp"))
    built(P, pg3, "Teleport (no bridges)")
    a5 = acts(pg3)
    i5 = icons(pg3)
    K.check([a5.get(s) for s in auto if a5.get(s) and not a5.get(s).startswith("warp:")] == [] and
            set(i5.get(s) for s in auto if (a5.get(s) or "").startswith("warp:")) == {"Skyy_Menu_Icon_Warp"},
            "DEGRADE: no bridges = no home tiles, every warp the signpost")
    for k_, v_ in BR.items():
        br.put(k_, v_)
    STATE["throw"] = True
    pg4 = openp(P, MP(P.pr, "tp"))
    built(P, pg4, "Teleport (bridges throw)")
    K.check([a for a in acts(pg4).values() if a.startswith("ihome:") or a.startswith("zhome:")] == [], "DEGRADE: throwing bridges = no home tiles, no exception")
    STATE["throw"] = False
    JV("MenuIO").stop(2000)
    MH.clearAll()

    # ---------------- ART
    z = zipfile.ZipFile(jar)
    wm = json.load(open(os.path.join(WART, "manifest.json"), encoding="utf8"))
    bad = []
    for i_ in wm["icons"]:
        data = z.read("Common/" + i_["file"][len("Common/"):])
        js = json.loads(z.read("Server/Item/Items/Utility/%s.json" % i_["id"]).decode("utf8"))
        if hashlib.sha256(data).hexdigest() != i_["sha256"] or js["Icon"] != i_["file"][len("Common/"):]:
            bad.append(i_["id"])
    K.check(not bad and len(wm["icons"]) == 11, "ART: the 11 warp icon items ship the art/warp-icons PNGs (%s)" % bad)
    vm = json.load(open(os.path.join(VART, "manifest.json"), encoding="utf8"))
    sha = dict((f["path"], f["sha256"]) for f in vm["files"])
    bag = json.loads(z.read("Server/Item/Items/Utility/Skyy_Menu_Icon_AccessoryBag.json").decode("utf8"))
    K.check(bag["Icon"] == "Icons/ItemsGenerated/Skyy_Menu_Icon_VoidCharms.png"
            and hashlib.sha256(z.read("Common/Icons/ItemsGenerated/Skyy_Menu_Icon_VoidCharms.png")).hexdigest() == sha["Common/Icons/ItemsGenerated/Skyy_Menu_Icon_VoidCharms.png"],
            "ART: the Void Charms icon item shows the approved amulet")
    K.check(all(hashlib.sha256(z.read("Common/UI/Custom/SkyyHubTabs/character_accessories%s@2x.png" % s_)).hexdigest() == sha["hub-tab/character_accessories%s.png" % s_]
                for s_ in ("", "_on")), "ART: the Character hub Void Charms tab pair = art/void-charms-icon/hub-tab")
    K.notes.append("T: auto rows %s; icons %s" % (got, dict((k, byact.get(k)) for k in want_ic)))
    K.save()


NONCLASS = None


def nonclass_want():
    wm = json.load(open(os.path.join(WART, "manifest.json"), encoding="utf8"))
    w = ["manifest.json", "Server/Languages/en-US/server.lang", "Server/Item/Items/Utility/Skyy_Menu_Icon_AccessoryBag.json",
         "Common/Icons/ItemsGenerated/Skyy_Menu_Icon_VoidCharms.png", "Common/Icons/ItemsGenerated/SkyyAccessories_Bag_Menu.png",
         "Common/UI/Custom/SkyyHubTabs/character_accessories@2x.png", "Common/UI/Custom/SkyyHubTabs/character_accessories_on@2x.png"]
    for i_ in wm["icons"]:
        w += [i_["file"], "Server/Item/Items/Utility/%s.json" % i_["id"]]
    return sorted(w)


if __name__ == "__main__":
    if HK.arg("--phase") == "compare":
        _eq0 = HK.Child.eq

        def _eq(self, got, want, what):
            if what == "C: non-class entries changed" and want == ["manifest.json"]:
                return _eq0(self, sorted(got), nonclass_want(), "C: non-class entries changed = manifest, server.lang, the warp icon items, the Void Charms item + tab pair")
            return _eq0(self, got, want, what)
        HK.Child.eq = _eq
    HK.run(name="SkyyMenu", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("t", run_t), ("live", T35.run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyMenu"))
