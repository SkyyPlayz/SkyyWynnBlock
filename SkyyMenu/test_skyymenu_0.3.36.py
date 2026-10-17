"""Harness for SkyyMenu 0.3.36 (round menu36, the MENU PATTERN leftovers: the Admin page on the kit 1.7 hub page under Settings, Server
Setup's row pages as scroll lists with grow rows, a mod's categories in the sub-tab row, in-page pickers, fitted crumb texts, the crumb id
fix; tools/menu_0_3_36_patch.py). Build first:
    python tools/menu_0_3_36_patch.py && python SkyyMenu/build_skyymenu_0.3.36.py

    python SkyyMenu/test_skyymenu_0.3.36.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py - the 0.3.35 harness's way: -Xverify:all over the SkyyMenu 0.3.19 engine stand-ins; the
kit 1.7 checks from tools/hub_tab_harness.py's shared helpers):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.35 -> 0.3.36: exactly the listed members differ
  M    EXECUTED:
       PAGES   EVERY Menu page built through the real builders and checked as a kit 1.7 hub page (H.kit17_rules: check_page, kit paths,
               every b.set / binding has its element; H.menu17 = SUI.assert_menu_page: 1600 x 980, rows 1 + 2, the sub-row count, no back
               button / < Menu, no pager but the grids' slot pages): Home, Teleport, Players, a player, Mods, Settings, Your Stats, the
               Admin page (admin + not admin), Server Setup: list, locked, a mod (SkyyMenu, a test mod: 2 categories, a 16-category mod),
               the file-only page, a table, the confirm, the change log, the history (+ preview), Export / Import
       OPS     the sub-tabs (All mods + 4 tabs, the active one Primary, every click carries the Text box), the visible buttons all in ONE
               list (no pages), a short tab grows its buttons, a tab click keeps the typed Text, a button runs its command, All mods / row
               2's Server Setup open Server Setup, Close closes, not an admin: no tab / button, the no-access line
       SETUP   one scroll list in every row view (all rows drawn, more than the old pages), grow tiers (short list = bigger rows, long
               list = normal), the categories in the sub-tab row (bound with every text box; the chosen one unbound), the crumbs All mods
               | <mod> | <view>, the Admin crumb on the list (not when locked), the pickers (change log mod / history file) cycle, the
               editable-table cap + its head line, the confirm binds nothing but Confirm / Cancel
       DRAFTS  a value typed in row 9 / 12 (past the old 6-row page) survives a category switch and back, a crumb-free footer click and
               a rebuild; table boxes past the old page are captured
       FIT     crumb / category texts: AdminPage.fit = the Python twin, every SET mod name and the test labels fit their button (or end
               in ...), the 16-category row fits the sub row
       IDS     a long choice row on row 0 draws its > button (SkyyAdmCr0) and the crumbs (SkyyAdmCrumb0..) without a duplicate id
  D    live     two starts on a scratch COPY of the live Skyy_SkyyMenu (the 0.3.35 harness's phase): the registry, Home built both times
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, json, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import skyyui as SUI
import hub_tab_harness as H

_s35 = importlib.util.spec_from_file_location("test_skyymenu_0_3_35", os.path.join(HERE, "test_skyymenu_0.3.35.py"))
T35 = importlib.util.module_from_spec(_s35)
_s35.loader.exec_module(T35)
T19 = T35.T19
jf = T35.jf

VERSION = "0.3.36"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.35.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "menu36", "menu")))
PKG = "com.skyy.menu."
LIVE_DIR = T35.LIVE_DIR
ADDED = []
EXPECT = {      # the class compare 0.3.35 -> 0.3.36
    'AdminPage': ['+f boxRows', '+f rowSz', '+m bindEnterR', '+m bindR', '+m catFit', '+m crumbBtn', '+m cw', '+m evdRow', '+m fit', '+m picker', '-m tabRow', '~m clickHist', '~m clickLog', '~m clickMod', '~m crumbs', '~m drawConfirm', '~m drawFileOnly', '~m drawHist', '~m drawIo', '~m drawList', '~m drawLog', '~m drawMod', '~m drawRow', '~m drawTable', '~m frame', '~m preview', '~m tail'],   # scroll lists, crumbs + categories (+ the category picker), fit, pickers, row-only box bindings
    'CfgFn': ['~m opExport'],   # the config kit's version text
    'CfgRows': ['~m header'],   # the config kit's version text
    'MenuData': ['+f ADM_CATMIN', '+f ADM_CRPAD', '+f ADM_CW', '+f ADM_CWMAX', '+f ADM_FMAX', '+f ADM_GMAX', '+f ADM_IN_FILES', '+f ADM_IN_HIST', '+f ADM_IN_HISTPREV', '+f ADM_IN_LIST', '+f ADM_IN_LOG', '+f ADM_IN_MOD', '+f ADM_IN_MODP', '+f ADM_IN_TABLE', '+f ADM_IN_TABLEADD', '+f ADM_MFIELDS', '+f ADM_RH_G', '+f ADM_RH_H', '+f ADM_RH_L', '+f ADM_RH_M', '+f ADM_RH_T', '+f ADM_SUBH', '+f ADM_TFIELDS', '+f ADM_TMAX', '+f UI_ACHVA', '+f UI_ACHVB', '+f UI_ADESCA', '+f UI_ADESCB', '+f UI_AFROWA', '+f UI_AFROWB', '+f UI_AFTXTA', '+f UI_AFTXTB', '+f UI_AGROWB', '+f UI_AGTXTA', '+f UI_AGTXTB', '+f UI_AHELPA', '+f UI_AHELPB', '+f UI_AHROWB', '+f UI_AHROWS', '+f UI_AHROWSP', '+f UI_AHTXTA', '+f UI_AHTXTB', '+f UI_ALDESCA', '+f UI_ALDESCB', '+f UI_ALDESCREDA', '+f UI_ALDESCREDB', '+f UI_ALINEA', '+f UI_ALINEB', '+f UI_ALNAMEA', '+f UI_ALNAMEB', '+f UI_ALROWB', '+f UI_ALTXTA', '+f UI_ALTXTB', '+f UI_ANAMEA', '+f UI_ANAMEB', '+f UI_APICK', '+f UI_APICKL', '+f UI_APICKV', '+f UI_AROA', '+f UI_AROB', '+f UI_AROWB', '+f UI_AROWSP', '+f UI_ATCELLSA', '+f UI_ATCELLSB', '+f UI_ATKEYA', '+f UI_ATKEYB', '+f UI_ATROWB', '+f UI_ATROWSA', '+f UI_ATROWSB', '+f UI_AWA', '+f UI_AWB', '-f UI_ACHV', '-f UI_ADESC', '-f UI_AFOOT', '-f UI_AFROW', '-f UI_AFTXT', '-f UI_AGROW', '-f UI_AGTXT', '-f UI_AHELP', '-f UI_AHROW', '-f UI_AHROWS4', '-f UI_AHROWS8', '-f UI_AHTXT', '-f UI_ALDESC', '-f UI_ALDESCRED', '-f UI_ALINE', '-f UI_ALNAME', '-f UI_ALROW', '-f UI_ALTXT', '-f UI_ANAME', '-f UI_ARO', '-f UI_AROW', '-f UI_ASTATUS', '-f UI_ATABS0', '-f UI_ATABS1', '-f UI_ATCELLS', '-f UI_ATKEY', '-f UI_ATROW', '-f UI_ATROWS', '-f UI_AW', '~<clinit>'],   # row tiers / pieces / caps / glyph widths; Void Charms texts; old per-row arrays + tab rows went
    'MenuPage': ['~m profileBody'],   # Void Charms (the profile line)
    'OpsPage': ['+f LIST_IN', '+f O_ROWH', '+f O_SUBGAP', '+f O_SUBN', '+f O_SUBS', '+f ROW_GAP', '+m hubAfter', '+m me', '-f O_MK', '-f O_MKA', '-f PER', '-f ROW_H', '-f WELL_H', '~<clinit>', '~m build', '~m handleDataEvent'],   # the kit 1.7 hub page
    'SkyyMenuPlugin': ['~m setup'],   # the ready line
    'StatsCalc': ['~m profileTab'],   # Void Charms (the Profile row)
}
TEST_MOD, WIDE_MOD, BIG_MOD, MANY_MOD = "SkyyTestCfg", "SkyyTestWide", "SkyyTestBig", "SkyyTestMany"
PAYLOAD_MAX, BINDING_MAX = 64 * 1024, 4096     # critic 1: a whole page's bindings / the largest one binding (wire bytes)


def adm_fit(s, room, cw, cwmax):
    """the Python twin of AdminPage.fit"""
    w = lambda c: cw[ord(c.upper()) - 32] if 0 <= ord(c.upper()) - 32 < len(cw) else cwmax
    if sum(w(c) for c in s) <= room * 100:
        return s
    dots, acc, out = 3 * w("."), 0, ""
    for c in s:
        if acc + w(c) + dots > room * 100:
            break
        acc += w(c)
        out += c
    return out.strip() + "..."


def run_m(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JArray, JObject, JString, JImplements, JOverride
    K = HK.Child(out)
    hcls = os.path.join(scratch, "hcls_m")
    os.makedirs(hcls, exist_ok=True)
    os.chdir(scratch)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, hcls, jar], verify=True)
    # the seam (research/Server-Setup-Spec.md: the bare-JVM harness swaps alive): a test mod has no plugin in this JVM
    CP = JClass("javassist.ClassPool")(False)
    CP.appendSystemPath()
    CP.appendClassPath(B.SERVER_JAR)
    CP.appendClassPath(jar)
    cc = CP.makeClass("skyymenu36.AdmT", CP.get(PKG + "AdminPage"))
    cc.addConstructor(JClass("javassist.CtNewConstructor").make(
        "public AdmT(com.hypixel.hytale.server.core.universe.PlayerRef pr, String v, String m) { super(pr, v, m); }", cc))
    cc.addMethod(JClass("javassist.CtNewMethod").make("public boolean alive(String m) { return m != null; }", cc))
    cc.writeFile(hcls)
    E = T19.engine(scratch, hcls)
    JV = lambda n: JClass(PKG + n)
    Paths = E.Paths
    home = os.path.join(scratch, "home_m")
    os.makedirs(os.path.join(home, "layouts"), exist_ok=True)
    os.makedirs(os.path.join(home, "imports"), exist_ok=True)
    for i in range(8):
        open(os.path.join(home, "imports", "code%d.txt" % i), "w").write("x")
    JV("PageGuard").STOP = False
    JV("PageGuard").EXEC = None
    ML = JV("MenuLayout")
    ML.DIR = Paths.get(os.path.join(home, "layouts"))
    ML.DEF_FILE = Paths.get(os.path.join(home, "layout-default.properties"))
    JV("SetStore").DIR = Paths.get(os.path.join(home, "settings"))
    JV("SetReg").ADMIN_FILE = Paths.get(os.path.join(home, "settings-defaults.properties"))
    JV("AdmSaveTask").BASE = Paths.get(home)
    JV("SetReg").registerOwn()
    JV("MenuIO").begin()
    HB, MH, MD, AP, OP = JV("HubBar"), JV("MenuHub"), JV("MenuData"), JV("AdminPage"), JV("OpsPage")
    AdmT = JClass("skyymenu36.AdmT")
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
    O = mkp(E.OP, "SkyyOp")
    Q = mkp(JClass("java.util.UUID").fromString("00000000-0000-0000-0000-0000000000c3"), "SkyyFriend")
    u = P.pr.getUuid()
    PGM = lambda X: X.pm.getCustomPage()

    def openp(X, pg):
        X.pm.openCustomPage(X.ref, X.st, pg)
        E.pump(X)
        return pg

    def click(X, pg, a, extra=""):
        pg.handleDataEvent(X.ref, X.st, '{"a":"%s"%s}' % (a, extra))
        E.pump(X)
        return PGM(X)

    def built(X, pg, what, hub, subs=1, pager_ok=False):
        _p, c, e = H.build_page(E, X, pg)
        apps = H.kit17_rules(K, c, e, what)
        H.menu17(K, apps, c, hub, what, subs=subs, pager_ok=pager_ok)
        return c, e, apps

    def bound(e):
        return dict((s, t) for s, t in e)
    crumbs = lambda c: H.subtabs(c, "SkyyAdmH")
    S_ = JClass("java.lang.String")
    SA = lambda xs: JArray(JString)([S_(x) for x in xs])
    OA = lambda xs: JArray(JObject)(xs)
    # ================================================================ the test mods (config contract 1 over the bridge)
    VAL = {}
    LOG, VER = [], []
    for i in range(25):
        LOG.append("2026-10-16 10:%02d:00\tSkyy\tx\tmenu\tt.n%d\t%d\t%d\tok" % (i, i % 12, i, i + 1))
    for i in range(12):
        VER.append("v%d\tSkyy_SkyyTestCfg/%s.properties\t2026-10-16 09:%02d:00\tx\tsaved by Skyy" % (i, "config" if i % 2 else "extra", i))
    TAB = [("entry%02d" % i, str(i)) for i in range(50)]

    @JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, mod):
            self.mod = mod

        @JOverride
        def apply(self, a):
            op = str(a[0])
            if op == "get":
                return S_(VAL.get((self.mod, str(a[1])), "5"))
            if op == "status":
                return SA(["ok", ""])
            if op == "keys":
                flt = str(a[2]) if len(a) > 2 and a[2] is not None else ""
                ks = [k for k, v in TAB if flt.lower() in k]
                return OA([SA(ks), SA([]), SA([v for k, v in TAB if flt.lower() in k])])
            if op == "log":
                return SA(LOG if self.mod == TEST_MOD else [])
            if op == "versions":
                return SA(VER if self.mod == TEST_MOD else [])
            if op == "export":
                return S_("SKYY1-test")
            return None

    def row(key, label, cat, typ, opts="", flags="live", help_="a test row"):
        return OA([S_(key), S_(label), S_(cat), S_(typ), S_("5"), S_("0"), S_("100"), S_(opts), S_(""), S_(flags), S_(help_)])
    rows = [row("t.ch", "A choice", "main", "choice", "a|One,b|Two,c|Three,d|Four,e|Five")]
    rows += [row("t.n%d" % i, "Number %d" % i, "main", "int", "step=1") for i in range(12)]
    rows += [row("t.b%d" % i, "Switch %d" % i, "more", "bool") for i in range(2)]
    rows += [row("t.tab", "A table", "extra", "table", "text;type;Value")]
    hdr = OA([S_("1"), S_(TEST_MOD), S_("Test Config"), S_("1.0"), S_("skyytestcfg.admin"), SA(["main", "more", "extra"]),
              SA(["Main", "More settings", "A very long category"]), OA(rows),
              S_("Skyy_SkyyTestCfg/config.properties,Skyy_SkyyTestCfg/extra.properties"), S_("a test mod")])
    br.put("config:def:" + TEST_MOD, hdr)
    br.put("config:fn:" + TEST_MOD, Fn(TEST_MOD))
    wcats = ["c%d" % i for i in range(16)]
    whdr = OA([S_("1"), S_(WIDE_MOD), S_("Wide"), S_("1.0"), S_("skyytestwide.admin"), SA(wcats), SA(["Category %d" % i for i in range(16)]),
               OA([row("w.%d" % i, "Wide %d" % i, wcats[i], "bool") for i in range(16)]), S_("Skyy_SkyyTestWide/config.properties"), S_("")])
    br.put("config:def:" + WIDE_MOD, whdr)
    br.put("config:fn:" + WIDE_MOD, Fn(WIDE_MOD))
    # critic 1: a 120-row category of typed boxes; critic 2: 20 categories (more than the sub row holds at 60 px)
    br.put("config:def:" + BIG_MOD, OA([S_("1"), S_(BIG_MOD), S_("Big"), S_("1.0"), S_("skyytestbig.admin"), SA(["main"]), SA(["Main"]),
                                        OA([row("b.%d" % i, "Big %d" % i, "main", "int", "step=1") for i in range(120)]), S_("Skyy_SkyyTestBig/config.properties"), S_("")]))
    br.put("config:fn:" + BIG_MOD, Fn(BIG_MOD))
    mcats = ["m%d" % i for i in range(20)]
    br.put("config:def:" + MANY_MOD, OA([S_("1"), S_(MANY_MOD), S_("Many"), S_("1.0"), S_("skyytestmany.admin"), SA(mcats), SA(["Category %d" % i for i in range(20)]),
                                         OA([row("x.%d" % i, "Many %d" % i, mcats[i], "bool") for i in range(20)]), S_("Skyy_SkyyTestMany/config.properties"), S_("")]))
    br.put("config:fn:" + MANY_MOD, Fn(MANY_MOD))
    JV("MenuIdx").scan()

    def payload(pg, X):
        ls = H.binding_sizes(E, X, pg)            # the wire size of each binding (CustomUIEventBinding.computeSize)
        return sum(ls), max(ls) if ls else 0
    # ================================================================ REG + the other Menu pages (0.3.35's set, re-checked)
    n = int(MH.register())
    K.eq(n, 6, "REG: Menu puts its 6 own tabs")
    for n_ in ("profiles", "smithing", "reforge", "upgrade", "identify", "bazaar", "vault"):
        E.CM.cmds.put(n_, E.U.allocateInstance(JClass("skyymenu19.Cmd").class_))
    built(P, openp(P, JV("MenuPage")(P.pr, "main")), "Home", "home", subs=0, pager_ok=True)
    built(P, openp(P, JV("MenuPage")(P.pr, "tp")), "Teleport", "world", subs=0, pager_ok=True)
    pl = openp(P, JV("MenuPage")(P.pr, "players"))
    built(P, pl, "Players", "social", subs=0, pager_ok=True)
    pl.selU = Q.pr.getUuid()
    pl.open("player")
    pl.selU = Q.pr.getUuid()
    built(P, pl, "a player's page", "social", subs=0, pager_ok=True)
    built(O, openp(O, JV("MenuPage")(O.pr, "mods")), "Mods", "settings", subs=0, pager_ok=True)
    built(P, openp(P, JV("SettingsPage")(P.pr, -1)), "Settings", "settings")
    built(P, openp(P, JV("StatsPage")(P.pr, 0)), "Your Stats", "character")
    # ================================================================ OPS (the Admin page)
    roots = ("modconfig", "sethub", "warpadmin", "deathpenalty", "bankconfig", "who", "version")
    for n_ in roots:
        E.CM.cmds.put(n_, JClass("skyymenu19.Cmd")())
    labels = [str(x) for x in OP.O_LABEL]
    lines = [str(x) for x in OP.O_LINE]
    tabs = [int(x) for x in OP.O_TAB]
    want0 = [i for i in range(len(lines)) if tabs[i] == 0 and lines[i] in roots]
    K.check("charms reload" in lines and not [l for l in lines if l.startswith("accessories")], "CHARMS: the Admin page's reload row runs /charms reload (SkyyAccessories 0.5.22)")
    ek = [str(x) for x in MD.E_KEY]
    K.check("accessorybag" in ek and "voidcharms" not in ek, "CHARMS: the renamed Void Charms tile keeps its saved key accessorybag (saved shortcuts stay)")
    op = openp(O, OP(O.pr, 0))
    oc, oe, oa = built(O, op, "Admin page (Server tab)", "settings")
    K.eq(H.subtabs(oc, "SkyyOpsF"), [("All mods", False), ("Server", True), ("Economy", False), ("Players", False), ("Diagnostics", False)],
         "OPS: the sub-tab row = All mods + the 4 tabs, Server active")
    ob = bound(oe)
    K.check(all("@OpsArg" in ob.get("#SkyyOpsFSub%d" % k, "") for k in range(5)) and "setup" in ob.get("#SkyyOpsFSub0", "")
            and "ot2" in ob.get("#SkyyOpsFSub3", ""), "OPS: every sub-tab is bound with the Text box (All mods = setup, Players = ot2)")
    r2 = H.row2(oc, "SkyyOpsF")
    K.check([lab for lab, sel in r2 if sel] == [SUI.hub_tab_label("settings", "setup")], "OPS: row 2 = the Settings tabs, Server Setup selected (the Admin page is its sub view): %s" % r2)
    btns = [re.match(r"TextButton #SkyyOpsA(\d+) ", t) for ty, s, t, d in oc if t and (s or "").startswith("#SkyyOpsC")]
    got = sorted(int(m.group(1)) for m in btns if m)
    K.eq(got, sorted(want0), "OPS: every visible Server button drawn in ONE list (%d; no pages)" % len(want0))
    hs_ = [int(re.search(r"Height: (\d+)", t).group(1)) for ty, s, t, d in oc if t and re.match(r"TextButton #SkyyOpsA\d+ ", t)]
    rowh = [int(x) for x in OP.O_ROWH]
    K.check(hs_ and set(hs_) == {rowh[int(HB.growSize((len(want0) + 1) // 2, int(OP.LIST_IN), OP.O_ROWH, int(OP.ROW_GAP)))]} and hs_[0] > rowh[0],
            "OPS: a short tab grows its buttons (%s of %s)" % (sorted(set(hs_)), rowh))
    K.check(int(HB.growSize(30, int(OP.LIST_IN), OP.O_ROWH, int(OP.ROW_GAP))) == 0, "OPS: a long tab (30 rows) keeps the normal size and scrolls")
    K.check(H.set_of(oc, "#SkyyOpsA%d.Text" % want0[0]) == labels[want0[0]], "OPS: the button label is set (%s)" % labels[want0[0]])
    K.check(not any(re.search(r'"(< ?Prev|Next ?>|< ?SkyWynn Menu)"', t or "") for ty, s, t, d in oc), "OPS: no page buttons, no menu button")
    click(O, op, "ot3", ',"@OpsArg":"abc"')
    K.check(int(op.tab) == 3 and str(op.arg) == "abc", "OPS: a sub-tab click switches the tab and keeps the typed Text (%s, %s)" % (op.tab, op.arg))
    dc, de, _da = built(O, op, "Admin page (Diagnostics)", "settings")
    K.check(H.set_of(dc, "#SkyyOpsArg.Value") == "abc" and any((s or "") == "#SkyyOpsI0.Text" for ty, s, t, d in dc),
            "OPS: Diagnostics draws its info lines and keeps the Text box")
    wi = lines.index("who")
    E.CM.lines.clear()
    click(O, op, "op%d" % wi)
    K.check("who" in [str(x) for x in E.CM.lines], "OPS: Who is online runs /who (%s)" % [str(x) for x in E.CM.lines])
    pg2 = click(O, op, "setup")
    K.check(pg2 is not None and "AdminPage" in str(pg2.getClass().getName()), "OPS: All mods opens Server Setup (%s)" % (None if pg2 is None else pg2.getClass().getName()))
    op2 = openp(O, OP(O.pr, 1))
    pg3 = click(O, op2, "hub:setup")
    K.check(pg3 is not None and "AdminPage" in str(pg3.getClass().getName()), "OPS: row 2's Server Setup opens Server Setup")
    op3 = openp(O, OP(O.pr, 0))
    click(O, op3, "hub:close")
    K.check(PGM(O) is None or PGM(O) is not op3, "OPS: the X closes the page")
    opn = openp(P, OP(P.pr, 0))
    nc, ne, na = built(P, opn, "Admin page (not an admin)", "settings")
    K.check(H.subtabs(nc, "SkyyOpsF") == [] and not any(re.match(r"TextButton #SkyyOpsA\d+", t or "") for ty, s, t, d in nc)
            and "skyymenu.modconfig" in (H.set_of(nc, "#SkyyOpsSub.Text") or ""), "OPS: not an admin - no sub-tab, no button, the no-access line")
    # ================================================================ SETUP: the list, locked, a mod, categories, drafts
    ad = openp(O, AdmT(O.pr, "list", None))
    lc, le, la = built(O, ad, "Server Setup (list)", "settings")
    K.eq(crumbs(lc), [("All mods", True), ("Admin", False)], "SETUP: the list's crumbs = All mods | Admin")
    lb = bound(le)
    K.check("aops" in lb.get("#SkyyAdmCrumb1", "") and "#SkyyAdmCrumb0" not in lb and "#SkyyAdmOps" not in lb, "SETUP: the Admin crumb is bound (aops), the search row has no Admin button")
    nlr = len([1 for ty, s, t, d in lc if t and re.match(r"Group #SkyyAdmLRow\d+ ", t)])
    K.check(nlr == len(list(ad.listMods)) and nlr >= 2 and any("TopScrolling" in (t or "") and "#SkyyAdmLRows " in (t or "") for ty, s, t, d in lc),
            "SETUP: the list = ONE scroll list, every mod drawn (%d rows)" % nlr)
    pg4 = click(O, ad, "aops")
    K.check(pg4 is not None and "OpsPage" in str(pg4.getClass().getName()), "SETUP: the Admin crumb opens the Admin page")
    lk = openp(P, AdmT(P.pr, "list", None))
    kc, ke, ka = built(P, lk, "Server Setup (locked)", "settings")
    K.eq(crumbs(kc), [("All mods", True)], "SETUP: locked - the crumbs are All mods only (no Admin)")
    K.check(not [s for s, t in ke if (s or "").startswith("#SkyyAdmCrumb")], "SETUP: locked - no crumb is bound")
    built(O, openp(O, AdmT(O.pr, "mod", "SkyyMenu")), "Server Setup (SkyyMenu)", "settings")
    am = openp(O, AdmT(O.pr, "mod", TEST_MOD))
    mc, me_, ma = built(O, am, "Server Setup (test mod, Main)", "settings")
    cr = crumbs(mc)
    K.check([c[0] for c in cr[:3]] == ["All mods", "TestCfg", "Main"] and cr[1][1] and cr[2][1] and not cr[3][1] and len(cr) == 5,
            "SETUP: a mod's sub row = All mods | TestCfg | its 3 categories, the path (mod + category) Primary (%s)" % cr)
    long_ = cr[4][0]
    room = 150 - 2 * int(MD.ADM_CRPAD) - 2
    K.check(long_.endswith("...") and SUI.text_width(long_, 12, bold=True, upper=True) <= room, "FIT: a long category is cut to fit its button (%r)" % long_)
    mb = bound(me_)
    K.check("atab1" in mb.get("#SkyyAdmCrumb3", "") and "#SkyyAdmCrumb2" not in mb and "amods" in mb.get("#SkyyAdmCrumb0", ""),
            "SETUP: the other categories are bound, the chosen one is not, All mods leads to the list")
    K.check(all(("SkyyAdmVal%d.Value" % r) in mb.get("#SkyyAdmCrumb3", "") for r in (1, 9, 12)), "DRAFTS: a category click carries every text box (rows 1, 9, 12)")
    K.check(H.set_of(mc, "#SkyyAdmSub.Text") is not None and any((t or "").startswith("Label #SkyyAdmSub ") and (s or "") == "#SkyyAdmBody" for ty, s, t, d in mc),
            "SETUP: with categories in the sub row, the title line is the body's first line")
    nrow = [t for ty, s, t, d in mc if t and re.match(r"Group #SkyyAdmRow\d+ ", t)]
    K.check(len(nrow) == 13 and len(list(am.rowKeys)) == 13, "SETUP: all 13 Main rows in ONE scroll list (old page: 6)")
    rh = sorted(set(int(re.search(r"Height: (\d+)", t).group(1)) for t in nrow))
    K.eq(rh, [list(MD.ADM_RH_M)[0]], "SETUP: 13 rows = the normal row size (the list scrolls)")
    ids = [m.group(1) for ty, s, t, d in mc if t for m in [re.match(r"\w+ #(\w+) \{", t)] if m]
    K.check("SkyyAdmCr0" in ids and "SkyyAdmCrumb0" in ids and len(ids) == len(set(ids)), "IDS: the choice row's > (SkyyAdmCr0) and the crumbs (SkyyAdmCrumb0) - no duplicate id")
    K.check(not any(re.search(r'"(< ?Prev|Next ?>|< ?Back|< ?Mods|< ?SkyWynn Menu)"', t or "") for ty, s, t, d in mc), "SETUP: no page / back buttons on a mod")
    # DRAFTS: type into rows 9 and 12, switch category and back
    k9, k12 = str(am.rowKeys[9]), str(am.rowKeys[12])
    click(O, am, "atab1", ',"@V9":"77","@V12":"88"')
    K.check(int(am.cat) == 1 and str(am.drafts.get(k9)) == "77" and str(am.drafts.get(k12)) == "88", "DRAFTS: rows 9 + 12 captured on the category click (%s)" % am.drafts)
    m1c, _m1e, _m1a = built(O, am, "Server Setup (test mod, More settings)", "settings")
    rh1 = sorted(set(int(re.search(r"Height: (\d+)", t).group(1)) for ty, s, t, d in m1c if t and re.match(r"Group #SkyyAdmRow\d+ ", t)))
    K.eq(rh1, [list(MD.ADM_RH_M)[2]], "SETUP: a 2-row category grows its rows to the biggest tier (rule 7)")
    click(O, am, "atab0")
    m0c, _m0e, _m0a = built(O, am, "Server Setup (test mod, back on Main)", "settings")
    K.check(H.set_of(m0c, "#SkyyAdmVal9.Value") == "77" and H.set_of(m0c, "#SkyyAdmVal12.Value") == "88" and "*" in (H.set_of(m0c, "#SkyyAdmName12.Text") or ""),
            "DRAFTS: back on Main, rows 9 + 12 still show the typed values (marked *)")
    click(O, am, "aadv", ',"@V9":"79"')
    K.check(str(am.drafts.get(k9)) == "79" and str(am.drafts.get(k12)) == "88", "DRAFTS: a footer click (Advanced) keeps every typed value")
    aw = openp(O, AdmT(O.pr, "mod", WIDE_MOD))
    wc, we, wa = built(O, aw, "Server Setup (16 categories)", "settings")
    wcr = crumbs(wc)
    subw = [int(re.search(r"Width: (\d+)", t).group(1)) for ty, s, t, d in wc if (s or "") == "#SkyyAdmHSub" and t]
    K.check(len(wcr) == 18 and sum(subw) <= SUI.HUB_PAGE_IW and all(SUI.text_width(c[0], 12, bold=True, upper=True) <= int(re.search(r"Width: (\d+)", t).group(1)) - 18
                                                                   for c, t in zip(wcr, [t for ty, s, t, d in wc if (s or "") == "#SkyyAdmHSub" and (t or "").startswith("TextButton")])),
            "FIT: 16 categories fit the sub row (%d px of %d) and every text fits its tab" % (sum(subw), SUI.HUB_PAGE_IW))
    # PAYLOAD (critic 1): a row's own buttons carry only its box; crumbs / footer at most ADM_MFIELDS boxes
    big = openp(O, AdmT(O.pr, "mod", BIG_MOD))
    bc, be, _ba = built(O, big, "Server Setup (120 typed rows)", "settings")
    bt, bm = payload(big, O)
    sm_ = openp(O, AdmT(O.pr, "mod", "SkyyMenu"))
    _sc, se, _sa = built(O, sm_, "Server Setup (SkyyMenu)", "settings")
    st_, sm2 = payload(sm_, O)
    K.check(bt < PAYLOAD_MAX and bm < BINDING_MAX and st_ < PAYLOAD_MAX and sm2 < BINDING_MAX,
            "PAYLOAD: 120 typed rows %d B (largest binding %d B), SkyyMenu %d B (largest %d B) - under %d / %d" % (bt, bm, st_, sm2, PAYLOAD_MAX, BINDING_MAX))
    bb = bound(be)
    K.check("SkyyAdmVal100.Value" in bb.get("#SkyyAdmSet100", "") and "SkyyAdmVal5.Value" not in bb.get("#SkyyAdmSet100", "")
            and "SkyyAdmVal100.Value" in bb.get("#SkyyAdmVal100", ""), "PAYLOAD: row 100's Set / Enter carry ONLY its own box")
    fb_ = [t for s_, t in be if (s_ or "").startswith("#SkyyAdmF")]
    K.check(fb_ and all("SkyyAdmVal39.Value" in t and "SkyyAdmVal40.Value" not in t for t in fb_), "PAYLOAD: the footer carries the first %d boxes only" % int(MD.ADM_MFIELDS))
    K.check("press its Set" in (H.set_of(bc, "#SkyyAdmHead.Text") or ""), "PAYLOAD: the head line says boxes past %d keep a typed value by their own Set" % int(MD.ADM_MFIELDS))
    click(O, big, "aset100", ',"@V100":"42"')
    K.check(str(big.drafts.get("b.100")) == "42" or str(big.status) != "", "DRAFTS: row 100's own Set sends its typed value (draft %s, status %r)" % (big.drafts.get("b.100"), str(big.status)))
    many = openp(O, AdmT(O.pr, "mod", MANY_MOD))
    yc, ye, _ya = built(O, many, "Server Setup (20 categories)", "settings")
    K.check(len(crumbs(yc)) == 2 and (H.set_of(yc, "#SkyyAdmPickV.Text") or "").startswith("Category 0"),
            "CATS: more categories than fit at %d px -> the sub row keeps the crumbs, the in-page picker picks the category" % int(MD.ADM_CATMIN))
    click(O, many, "cfnext")
    K.check(int(many.cat) == 1, "CATS: the picker's > picks the next category")
    click(O, many, "cfprev")
    click(O, many, "cfprev")
    K.check(int(many.cat) == 19, "CATS: the picker's < wraps around (%s)" % many.cat)
    K.check(min(int(re.search(r"Width: (\d+)", t).group(1)) for ty, s_, t, d in wc if (s_ or "") == "#SkyyAdmHSub" and (t or "").startswith("TextButton")) >= int(MD.ADM_CATMIN),
            "CATS: no category tab narrower than %d px (16 categories)" % int(MD.ADM_CATMIN))
    # FIT: the Java fit = the Python twin; every SET mod name fits a crumb
    cw, cwmax = [int(x) for x in MD.ADM_CW], int(MD.ADM_CWMAX)
    samples = [str(x)[4:] if str(x).startswith("Skyy") else str(x) for x in MD.MOD_NAME] + ["A very long category", "Enchantments and more", "W" * 30, "Accessories"]
    bad = [s for s in samples if str(AP.fit(s, room)) != adm_fit(s, room, cw, cwmax) or SUI.text_width(str(AP.fit(s, room)), 12, bold=True, upper=True) > room]
    K.check(not bad, "FIT: AdminPage.fit = its Python twin and fits %d px for %d names (%s)" % (room, len(samples), bad[:3]))
    # ================================================================ SETUP: the file-only page, a table, the confirm
    built(O, openp(O, AdmT(O.pr, "mod", "SkyyIslands")), "Server Setup (file only)", "settings")
    at_ = openp(O, AdmT(O.pr, "mod", TEST_MOD))
    at_.cat = 2
    click(O, at_, "arefresh")
    click(O, at_, "aedit0")
    tc, te, ta = built(O, at_, "Server Setup (a table)", "settings")
    K.eq([c[0] for c in crumbs(tc)], ["All mods", "TestCfg", "Table"], "SETUP: a table's crumbs = All mods | TestCfg | Table")
    trs = [t for ty, s, t, d in tc if t and re.match(r"Group #SkyyAdmTRow\d+ ", t)]
    cap = int(MD.ADM_TFIELDS)
    K.check(len(trs) == cap == len(list(at_.tKeys)) and "40 shown" in (H.set_of(tc, "#SkyyAdmHead.Text") or ""),
            "SETUP: an editable 1-column table draws %d of 50 entries (one box each) and says so (%s)" % (len(trs), H.set_of(tc, "#SkyyAdmHead.Text")))
    K.check((H.set_of(tc, "#SkyyAdmStatus.Text") or "").startswith("Showing 40 of 50"), "SETUP: the status line says the table shows 40 of 50 (%r)" % H.set_of(tc, "#SkyyAdmStatus.Text"))
    tb = bound(te)
    K.check("SkyyAdmCol35x0.Value" in tb.get("#SkyyAdmCrumb1", "") and "aback" in tb.get("#SkyyAdmCrumb1", ""), "DRAFTS: the TestCfg crumb carries the table's boxes (row 35)")
    click(O, at_, "tfind", ',"@C35x0":"999","@TF":""')
    K.check(str(at_.tDrafts.get("entry35\t0")) == "999", "DRAFTS: a table box past the old 6-row page is captured (row 35)")
    click(O, at_, "trem3")
    K.check(str(at_.view) == "confirm", "SETUP: Remove asks first (confirm)")
    cc_, ce, ca = built(O, at_, "Server Setup (confirm)", "settings")
    K.eq([c[0] for c in crumbs(cc_)][-1:], ["Confirm"], "SETUP: the confirm's last crumb")
    K.check(sorted(s for s, t in ce if not (s or "").startswith("#SkyyAdmH")) == ["#SkyyAdmNo", "#SkyyAdmYes"],
            "SETUP: the confirm binds nothing but Confirm / Cancel (%s)" % sorted(s for s, t in ce if not (s or "").startswith("#SkyyAdmH")))
    click(O, at_, "ano")
    # ================================================================ SETUP: the change log, the history, Export / Import
    lg = openp(O, AdmT(O.pr, "log", None))
    gc, ge, ga = built(O, lg, "Server Setup (change log)", "settings")
    K.eq([c[0] for c in crumbs(gc)], ["All mods", "Changes"], "SETUP: the change log's crumbs")
    grs = len([1 for ty, s, t, d in gc if t and re.match(r"Group #SkyyAdmGRow\d+ ", t)])
    K.check(grs >= 25 and (H.set_of(gc, "#SkyyAdmPickV.Text") or "").startswith("All mods"), "SETUP: the change log = ONE scroll list (25 rows; old page 10) + the mod picker on All mods")
    K.check(not any(re.match(r"(Group #SkyyAdmTabs|TextButton #SkyyAdmTab)\d*", t or "") for ty, s, t, d in gc), "SETUP: no in-body tab row on the change log")
    click(O, lg, "lfnext")
    K.check(str(lg.logMod) in [str(x) for x in lg.logTabs][1:] and len(list(lg.logTabs)) >= 2, "SETUP: the picker's > shows one mod's changes (%s)" % lg.logMod)
    click(O, lg, "lfprev")
    K.check(str(lg.logMod) == "", "SETUP: the picker's < goes back to All mods")
    hi = openp(O, AdmT(O.pr, "hist", TEST_MOD))
    hc, he, ha = built(O, hi, "Server Setup (history)", "settings")
    hrs = [t for ty, s, t, d in hc if t and re.match(r"Group #SkyyAdmHRow\d+ ", t)]
    K.check(len(hrs) == 12 and (H.set_of(hc, "#SkyyAdmPickV.Text") or "").startswith("All files"), "SETUP: the history = ONE scroll list (12 versions; old page 8) + the file picker")
    click(O, hi, "hfnext")
    K.check(str(hi.histFile) == "Skyy_SkyyTestCfg/config.properties", "SETUP: the file picker's > picks the first file (%s)" % hi.histFile)
    hi.histPreview = "a line\nanother line"
    built(O, hi, "Server Setup (history + preview)", "settings")
    io_ = openp(O, AdmT(O.pr, "mod", TEST_MOD))
    click(O, io_, "aio")
    ic, ie, ia = built(O, io_, "Server Setup (Export / Import)", "settings")
    K.check(len([1 for ty, s, t, d in ic if t and re.match(r"Group #SkyyAdmFRow\d+ ", t)]) == 8, "SETUP: Export / Import lists all 8 import files (old: 3)")
    K.notes.append("M: Admin buttons %s px (tiers %s); test mod crumbs %s; 16 categories %d px; table head %r; log rows %d, history rows %d; payload 120 rows %d B (max %d), SkyyMenu %d B (max %d)" % (
        sorted(set(hs_)), rowh, cr, sum(subw), H.set_of(tc, "#SkyyAdmHead.Text"), grs, len(hrs), bt, bm, st_, sm2))
    JV("MenuIO").stop(2000)
    MH.clearAll()
    K.save()


def lang_diff():
    """the server.lang lines that differ 0.3.35 -> 0.3.36 (only the bag icon item's name may: Accessory Bag -> Void Charms)"""
    import zipfile
    a_, b_ = [set(zipfile.ZipFile(j).read("Server/Languages/en-US/server.lang").decode("utf8").splitlines()) for j in (OLD_JAR, JAR)]
    return sorted(a_ - b_), sorted(b_ - a_)


if __name__ == "__main__":
    if HK.arg("--phase") == "compare":
        _eq0 = HK.Child.eq

        def _eq(self, got, want, what):
            if what == "C: non-class entries changed" and want == ["manifest.json"]:
                gone, new = lang_diff()
                return self.check(sorted(got) == ["Server/Languages/en-US/server.lang", "manifest.json"] and len(gone) == len(new) == 2
                                  and all("Accessory Bag" in g_ and "Void Charms" in n_ and g_.split("=")[0] == n_.split("=")[0] for g_, n_ in zip(gone, new)),
                                  "C: non-class entries changed = manifest.json + server.lang (only the bag icon item's name: %s -> %s)" % (gone, new))
            return _eq0(self, got, want, what)
        HK.Child.eq = _eq
    HK.run(name="SkyyMenu", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("m", run_m), ("live", T35.run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyMenu"))
