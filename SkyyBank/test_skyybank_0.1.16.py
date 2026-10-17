"""Harness for SkyyBank 0.1.16 (MENU PATTERN sweep S2: the bank page on the kit 1.7 hub_page, 1600 x 980, rows 1 + 2; tools/bank_0_1_16_patch.py).
Build first: python SkyyCore/build_skyycore_1.0.0.py (if its jar is missing), python tools/bank_0_1_16_patch.py && python SkyyBank/build_skyybank_0.1.16.py

    python SkyyBank/test_skyybank_0.1.16.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Every child JVM gets the SkyyCore jar on its class path (SKYY_HARNESS_CP). The OLD jar everywhere is the LIVE 0.1.15 (the SET pin).
The merged Vault tab WITH the real SkyyVault 0.1.9 page (the coin panel on top) is SkyyVault/test_skyyvault_0.1.9.py's E2E phase; this
harness proves the bank side (the phases of test_skyybank_0.1.15.py, with the kit 1.5 page check replaced by the KIT 1.7 one):
  A      every class loads + initialises with -Xverify:all (Core on the class path)
  C      class compare 0.1.15 -> 0.1.16: added HubBar (the page's own kit 1.7 copy); changed exactly BankPage.build / hubClick and the
         plugin's setup (the ready line's page id) - every other class byte-identical (BankStore, BankCmd, BankPanelFn, the migrations ...)
  KITBYTES  no kit art in the jar; manifest = stable name SkyyBank 0.1.16, no asset pack, Dependencies Skyy:SkyyCore >=1.0.0 <2.0.0
  HUB    tools/hub_tab_harness.py on SkyyCore's HubBar (owner SkyyBank): REG / PAGE / CLICK / DROP + VIS (bank:fn:unlocked, and the tab
         hidden while vault:fn:openBank is on the bridge) + Refresh + the page id = BANK_PAGE_CHECKED. PAGE = the KIT 1.7 check (page17):
         the real built page: check_page, kit textures only, the root 1600 x 980, SUI.assert_menu_page on the REAL commands (rows 1 + 2,
         no sub row, no kit 1.5 bar, no back / < Menu text, no pager), the X = hub:close, row 2 one tab per visible Storage tab, every
         b.set / binding names an element, hub:last
  D      two opens of the page on a scratch COPY of the live Skyy_SkyyBank (nothing written)
  MERGE  test_skyybank_0.1.15.py's bank:fn:panel / bank:fn:move phase, unchanged
  PAGE17 the bank page over stand-in purses: the page17 check for a player with an account and one without; coin smoke ON THE PAGE:
         Deposit 500 (purse -500, bank +500), the same click again (used-up token) moves nothing, Withdraw 200, Withdraw all, Deposit all,
         more than the purse refused; row 1 (with SkyyMenu's hub defs): one button per hub + Home, another hub runs its command (answered),
         the own hub answers, Home runs /skymenu (answered); the X closes
  X      test_skyybank_0.1.9.py's exec phase, 0.1.15 vs 0.1.16 side by side (800 random steps: the same answers and files)
  LIVE2  test_skyybank_0.1.9.py's live phase: START TWICE on a scratch COPY of the live data with 0.1.15 and 0.1.16
  AA     engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, json, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import hub_tab_harness as H
import skyyui as SUI

VERSION = "0.1.16"
PKG = "com.skyy.bank."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyBank-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyBank-0.1.15.jar")
CORE_JAR = os.path.join(ROOT, "SkyyCore", "SkyyCore-1.0.0.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "menuS2", "bank")))


def tmod(fn, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


T15 = tmod("test_skyybank_0.1.15.py", "tb0115")
os.environ["SKYY_HARNESS_CP"] = CORE_JAR
T14 = T15.T14
T9 = T15.T9
T9.OLD_JAR = OLD_JAR
T14.OLD_JAR = OLD_JAR
DECL_RE = re.compile(r"\b([A-Za-z]+) #([A-Za-z0-9]+) \{")

EXPECT = {      # the class compare 0.1.15 -> 0.1.16
    "BankPage": ["~m build", "~m hubClick"],     # the kit 1.7 hub page (page17) + HubBar.route (this jar's HubBar)
    "SkyyBankPlugin": ["~m setup"],              # the ready line (the page id)
}


def unq(d):
    if d is None:
        return ""
    d = str(d)
    try:
        v = json.loads(d)
    except Exception:
        return d
    if isinstance(v, dict) and len(v) == 1:
        v = list(v.values())[0]
    return v if isinstance(v, str) else d


def page_check17(K, E, S, P, page, hb, what):
    """the KIT 1.7 page check (replaces hub_tab_harness.page_check, which checks the kit 1.5 bar) - see the docstring (HUB / PAGE17)"""
    from jpype import JClass
    b = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")()
    ev = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")()
    page.build(P.ref, b, ev, P.st)
    cmds = H.cmds_of(b)
    evs = H.events_of(ev)
    apps = SUI.Appends([(None if s is None else s.lstrip("#"), t) for ty, s, t, d in cmds if t is not None and ty and "Append" in ty])
    sets = [(s, d) for ty, s, t, d in cmds if ty == "Set"]
    K.check(len(apps) > 5 and len(apps) + len(sets) == len(cmds), "%s: %d appends + %d sets" % (what, len(apps), len(sets)))
    try:
        SUI.check_page(apps, S.idp)
        K.check(True, "%s: check_page (markup rules, parents, no duplicate id)" % what)
    except Exception as e:
        K.check(False, "%s: check_page: %s" % (what, e))
    try:
        SUI.check_sky_paths(apps, tab_icons=True)
        allp = [m.group(0) for mk in apps.markups() for m in SUI._SKY_PATH_RE.finditer(SUI.render(mk))]
        K.check(not [p for p in allp if p.startswith('"../')], "%s: no texture path leaves Common/UI/Custom (%d paths)" % (what, len(allp)))
    except Exception as e:
        K.check(False, "%s: sky paths: %s" % (what, e))
    root = apps[0][1]
    K.check(apps[0][0] is None and root.startswith("Group #%s { Anchor: (Width: 1600, Height: 980); }" % S.prefix), "%s: the root #%s is 1600 x 980" % (what, S.prefix))
    try:
        info = SUI.assert_menu_page(apps, hub=S.hub, what=what, sets=[(s, unq(d)) for s, d in sets], pager_ok=False)
        K.check(info["rows"] == 2 and info["subs"] == 0, "%s: assert_menu_page (1600 x 980, rows 1 + 2, no sub row, no back / < Menu, no pager)" % what)
    except Exception as ex:
        K.check(False, "%s: assert_menu_page: %s" % (what, ex))
    K.check(not [mk for p, mk in apps if "HubMenu" in mk or "HubTabs" in mk or '"< Menu"' in mk], "%s: no kit 1.5 bar (no < Menu, no small tab strip)" % what)
    K.check(any("hub:close" in t for s, t in evs if s == "#%sHubClose" % S.prefix), "%s: the X = hub:close" % what)
    vis = [str(r[0]) for r in hb.tabs(S.hub, P.pr.getUuid())]
    tabs = [mk for p, mk in apps if p == S.prefix + "BigTabs" and mk.startswith("Button")]
    K.eq(len(tabs), len(vis), "%s: row 2 = one tab per visible Storage tab %s" % (what, vis))
    for k, t in enumerate(vis):
        K.check(any(("hub:" + t) in tx for s, tx in evs if s == "#%sBigT%d" % (S.prefix, k)), "%s: row 2 tab %d bound to hub:%s" % (what, k, t))
    ids = set()
    for _p, mk in apps:
        ids |= set(x.group(2) for x in DECL_RE.finditer(SUI.render(mk)))
    bs = [s for s, _t in evs]
    bad = [s for s, _d in sets if s.lstrip("#").split(".")[0] not in ids] + [s for s in bs if s.lstrip("#") not in ids]
    K.check(not bad, "%s: every b.set and binding names an element that exists (%d sets, %d bindings): %s" % (what, len(sets), len(bs), bad[:4]))
    last = E.br.get("hub:last:" + str(P.pr.getUuid()))
    K.check(last is not None and str(last.get(S.hub)) == S.tab, "%s: hub:last remembers %s -> %s" % (what, S.hub, S.tab))
    return cmds, evs


H.page_check = page_check17      # run_hub calls H.page_check: the kit 1.7 check from now on


def extra_hub(K, W, J):
    src = open(os.path.join(HERE, "build_skyybank_%s.py" % VERSION), encoding="utf8").read()
    m = re.search(r'BANK_PAGE_CHECKED = "([0-9a-f]{12})"', src)
    data = zipfile.ZipFile(JAR).read("com/skyy/bank/SkyyBankPlugin.class")
    K.check(m is not None and ("page " + m.group(1)).encode() in data,
            "PAGE: the built page id = BANK_PAGE_CHECKED %s (the ready line; the 0.1.7 page-check rule)" % (m and m.group(1)))
    K.check(b"SkyyCore " in data, "PAGE: the ready line names the SkyyCore version")
    K.check(b"Vault tab coin panel bank:fn:panel / bank:fn:move " in data, "PAGE: the ready line names the merge")


def run_page17(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    W = H.boot(scratch, jar, "page17")
    E = W.E
    J = lambda n: JClass(PKG + n)
    HB = JClass("com.skyy.core.ui.HubBar")
    E.br = HB.map()
    TRUE, FALSE = JClass("java.lang.Boolean").TRUE, JClass("java.lang.Boolean").FALSE
    Long = JClass("java.lang.Long")
    home = os.path.join(scratch, "page17_home")
    os.makedirs(os.path.join(home, "accounts"), exist_ok=True)
    T14.prep(E, J, home)
    J("BankConfig").load()
    PURSE = {}

    @JImplements("java.util.function.Function")
    class KeyFn:
        @JOverride
        def apply(self, u):
            return str(u)

    @JImplements("java.util.function.Function")
    class Get:
        @JOverride
        def apply(self, u):
            return Long.valueOf(PURSE.get(str(u), 0))

    @JImplements("java.util.function.Function")
    class Add:
        @JOverride
        def apply(self, a):
            PURSE[str(a[0])] = PURSE.get(str(a[0]), 0) + int(a[1])
            return Long.valueOf(PURSE[str(a[0])])

    @JImplements("java.util.function.Function")
    class Take:
        @JOverride
        def apply(self, a):
            if PURSE.get(str(a[0]), 0) < int(a[1]):
                return FALSE
            PURSE[str(a[0])] = PURSE.get(str(a[0]), 0) - int(a[1])
            return TRUE
    for k_, v_ in (("profile:fn:key", KeyFn()), ("coins:fn:get", Get()), ("coins:fn:add", Add()), ("coins:fn:take", Take())):
        E.br.put(k_, v_)
    P, O = W.P, W.O
    for X in (P, O):
        E.br.put("hub:last:" + str(X.pr.getUuid()), JClass("java.util.concurrent.ConcurrentHashMap")())
    u = P.pr.getUuid()
    T9.write_acc(home, str(u), 1000)
    PURSE[str(u)] = 5000
    K.eq(int(J("BankHubOpen").register()), 1, "PAGE17: the Bank tab is put (no SkyyVault: the tab shows)")
    S_ = S
    for nm, X in (("account", P), ("no account", O)):
        r = str(HB.open(X.pr, X.pr.getUuid(), "storage", "bank"))
        E.pump(X)
        pg = X.pm.getCustomPage()
        K.check(r == "bridge" and pg is not None and str(pg.getClass().getSimpleName()) == "BankPage", "PAGE17 %s: the bank page opens through the Bank tab (%s)" % (nm, r))
        if pg is not None:
            page_check17(K, E, S_, X, pg, HB, "PAGE17 bank page (%s)" % nm)
    pg = P.pm.getCustomPage()
    bank = lambda: int(J("BankStore").get(u))

    def click(a, amt, tok):
        d = {"a": a, "@BAmount": amt}
        if tok is not None:
            d["t"] = tok
        n0 = len(E.sent(P))
        P.pm.handleLegacyCustomPageEvent(P.ref, P.st, E.CPE(E.CPT.Data, json.dumps(d)))
        E.pump(P)
        return P.pm.getCustomPage(), n0
    pg = P.pm.getCustomPage()
    tok = str(pg.tok)
    p2, n = click("deposit", "500", tok)
    K.check(bank() == 1500 and PURSE[str(u)] == 4500 and str(p2.info).startswith("+"), "PAGE17 coins: Deposit 500 on the page -> bank 1,500, purse 4,500 (%s)" % p2.info)
    p2, n = click("deposit", "500", tok)
    K.check(bank() == 1500 and PURSE[str(u)] == 4500, "PAGE17 coins: the same click again (used-up token) moves nothing (%s)" % p2.info)
    p2, n = click("withdraw", "200", str(p2.tok))
    K.check(bank() == 1300 and PURSE[str(u)] == 4700, "PAGE17 coins: Withdraw 200 -> bank 1,300, purse 4,700 (%s)" % p2.info)
    p2, n = click("deposit", "999999", str(p2.tok))
    K.check(bank() == 1300 and PURSE[str(u)] == 4700 and str(p2.info).startswith("-"), "PAGE17 coins: more than the purse -> refused, nothing moves (%s)" % p2.info)
    p2, n = click("wdall", "", str(p2.tok))
    K.check(bank() == 0 and PURSE[str(u)] == 6000, "PAGE17 coins: Withdraw all -> bank 0, purse 6,000 (%s)" % p2.info)
    p2, n = click("depall", "", str(p2.tok))
    K.check(bank() == 6000 and PURSE[str(u)] == 0, "PAGE17 coins: Deposit all -> bank 6,000, purse 0 (%s)" % p2.info)
    page_check17(K, E, S_, P, p2, HB, "PAGE17 bank page after the moves")
    # ROW1: SkyyMenu's hub:def entries -> one row-1 button per hub + Home; clicks route through this jar's HubBar.route
    ObjA = lambda xs: jpype.JArray(JClass("java.lang.Object"))(xs)
    E.br.put("hub:def:home", ObjA(["Home", "skymenu", "Skyy_Menu", None]))
    for _h in SUI.HUBS:
        E.br.put("hub:def:" + _h, ObjA([SUI.hub_title_now(_h), "zz" + _h, "Skyy_Menu", None]))
    cm1, ev1 = page_check17(K, E, S_, P, p2, HB, "ROW1 bank page (with SkyyMenu's hub defs)")
    rowb = [s for s, t in ev1 if s and s.startswith("#SkyyBankFBig") and "hub:h:" in t]
    K.eq(len(rowb), 1 + len(SUI.HUBS), "ROW1: one row-1 button per hub + Home, each bound to hub:h:<id>")
    mark = "#SkyyBankFTitle.Text"
    same = lambda a, b_: a is not None and b_ is not None and int(JClass("java.lang.System").identityHashCode(a)) == int(JClass("java.lang.System").identityHashCode(b_))
    for a, cmd, what in (("hub:h:market", "zzmarket", "another hub (no tab loaded) runs its hub command"), ("hub:h:storage", None, "the page's own hub answers"),
                         ("hub:h:home", "skymenu", "Home runs /skymenu")):
        E.CM.lines.clear()
        p3, n = click(a, "", None)
        K.check(same(p3, p2) and mark in E.strs_of(P, n) and (cmd is None or cmd in [str(x) for x in E.CM.lines]) and bank() == 6000,
                "ROW1: %s, the page is answered, no coin moves (%s)" % (what, list(E.CM.lines)))
    p3, n = click("hub:close", "", None)
    K.check(p3 is None and bank() == 6000, "PAGE17: the X closes the bank page")
    K.save()


S = H.Spec(name="SkyyBank", version=VERSION, pkg=PKG, hub="storage", tab="bank", mod="SkyyBank", open_cls="BankHubOpen", vis_cls="BankHubVis",
           page_cls="BankPage", prefix="SkyyBankF", idp="SkyyB", plugin_cls="SkyyBankPlugin", register_call="BankHubOpen.register",
           register=lambda J: J("BankHubOpen").register(), prep=T14.prep, vis_cases=T15.vis_cases, clicks=[('{"a":"refresh","@BAmount":""}', T14.chk_refresh)],
           extra_hub=extra_hub, jar=JAR, old_jar=OLD_JAR, scratch=SCRATCH, script=__file__,
           hub_class="com.skyy.core.ui.HubBar", hub_owner="SkyyBank", kit_in_jar=False,
           added=["HubBar"], removed=[],
           expect=EXPECT,
           extra_phases=[("merge", T15.run_merge), ("page17", run_page17), ("exec", T14.controls_to_notes(T9.run_exec, "0.1.8")), ("live2", T9.run_live)])

if __name__ == "__main__":
    if HK.arg("--phase") == "compare":
        # 0.1.15 -> 0.1.16: neither jar ships kit art, so only manifest.json changes (the hub harness's compare expects the H3 kit add)
        HK.run(name=S.name, version=S.version, jar=S.jar, old_jar=S.old_jar, pkg=S.pkg, scratch=S.scratch, expect=S.expect, added=S.added,
               phases=[], script=S.script, removed=S.removed)
    else:
        H.run(S)
