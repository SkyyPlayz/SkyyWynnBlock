"""Harness for SkyyVault 0.1.9 (MENU PATTERN sweep S2: the Vault page + the buy confirm window on the kit 1.7 hub_page, 1600 x 980, rows 1 + 2;
tools/vault_0_1_9_patch.py). Build first: python tools/vault_0_1_9_patch.py && python SkyyVault/build_skyyvault_0.1.9.py, and SkyyBank 0.1.16
(python tools/bank_0_1_16_patch.py && python SkyyBank/build_skyybank_0.1.16.py; SkyyCore 1.0.0's jar must exist)

    python SkyyVault/test_skyyvault_0.1.9.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Every child JVM has SkyyCore 1.0.0 + SkyyBank 0.1.16 on its class path (SKYY_HARNESS_CP), so the E2E phase runs the REAL bank code.
The phases of test_skyyvault_0.1.8.py (A verify, C compare 0.1.8 -> 0.1.9, HUB executed: REG / PAGE / CLICK / DROP, FIND, D live: two
opens on a scratch COPY of the live Skyy_SkyyVault, AA engine-access audit, E2E with the real SkyyBank: deposit / withdraw, tokens, locked /
missing bank, unreadable vault, Refresh, the merged-tab behaviour), with the kit 1.5 page check replaced by the KIT 1.7 one (page17):
  PAGE17  every built page (real UICommandBuilder / UIEventBuilder from the Java build): check_page, kit textures only, the root 1600 x 980,
          SUI.assert_menu_page on the REAL commands (row 1 #...BigRow 48 high, row 2 #...BigTabs 56 high, no sub row, no kit 1.5 / 1.6
          bar pieces, no back / < Menu text inline or in a b.set; Prev / Next allowed only on the vault page - its slot pages), the X bound
          to hub:close, one row-2 tab per visible Storage tab bound to hub:<tab>, every b.set / binding names an element, hub:last.
          Run on: the page-mode page, the full hub, the chest-mode page, the unreadable-vault view, a locked bank, no SkyyBank, and the
          buy confirm window.
  ROW1    row 1 with SkyyMenu's hub:def entries: one button per hub + Home; clicks: another hub without a tab runs its command (answered),
          the page's own hub answers, Home runs /skymenu (answered)
  DLG     the buy confirm window: the page17 check; row 1's Storage answers; the X closes it (nothing bought, said in chat); row 2's
          Vault tab opens the vault (the window goes the Esc way); Cancel still returns to the vault (dlgBack); Buy buys exactly once
          (the purse pays once, the page count goes up once; a second Buy on the same window does nothing)
  ITEMS   a vault item put / take smoke in page mode: an item put into the live vault window lands in the vault page (syncView), taking it
          out empties the slot again
Exit code 1 on any failure.
"""
import os, sys, json, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import hub_tab_harness as H

VERSION = "0.1.9"
PKG = "com.skyy.vault."
BANK_JAR = os.path.join(ROOT, "SkyyBank", "SkyyBank-0.1.16.jar")
CORE_JAR = os.path.join(ROOT, "SkyyCore", "SkyyCore-1.0.0.jar")
os.environ["SKYY_HARNESS_CP"] = os.pathsep.join([CORE_JAR, BANK_JAR])
import skyyui as SUI

DECL_RE = re.compile(r"\b([A-Za-z]+) #([A-Za-z0-9]+) \{")


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


def page_check17(K, E, S, P, page, hb, what, prefix=None, idp=None, pager_ok=None, tab=None):
    """the KIT 1.7 page check (replaces hub_tab_harness.page_check, which checks the kit 1.5 bar): build the page into REAL builders, then
    check_page, kit textures, 1600 x 980, assert_menu_page on the real commands, the X / row 2 bindings, every b.set / binding names an
    element, hub:last. Returns (cmds, events)."""
    from jpype import JClass
    prefix = prefix or S.prefix
    idp = idp or S.idp
    tab = tab or S.tab
    pager_ok = (prefix == "SkyyVF") if pager_ok is None else pager_ok
    b = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")()
    ev = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")()
    page.build(P.ref, b, ev, P.st)
    cmds = H.cmds_of(b)
    evs = H.events_of(ev)
    apps = SUI.Appends([(None if s is None else s.lstrip("#"), t) for ty, s, t, d in cmds if t is not None and ty and "Append" in ty])
    sets = [(s, d) for ty, s, t, d in cmds if ty == "Set"]
    K.check(len(apps) > 5 and len(apps) + len(sets) == len(cmds), "%s: %d appends + %d sets" % (what, len(apps), len(sets)))
    try:
        SUI.check_page(apps, idp)
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
    K.check(apps[0][0] is None and root.startswith("Group #%s { Anchor: (Width: 1600, Height: 980); }" % prefix), "%s: the root #%s is 1600 x 980" % (what, prefix))
    try:
        info = SUI.assert_menu_page(apps, hub=S.hub, what=what, sets=[(s, unq(d)) for s, d in sets], pager_ok=pager_ok)
        K.check(info["rows"] == 2 and info["subs"] == 0, "%s: assert_menu_page (1600 x 980, rows 1 + 2, %d sub rows, no back / < Menu%s)"
                % (what, info["subs"], ", slot-page Prev / Next allowed" if pager_ok else ", no pager"))
    except Exception as ex:
        K.check(False, "%s: assert_menu_page: %s" % (what, ex))
    K.check(not [mk for p, mk in apps if "HubMenu" in mk or "HubTabs" in mk or '"< Menu"' in mk], "%s: no kit 1.5 bar (no < Menu, no small tab strip)" % what)
    K.check(any("hub:close" in t for s, t in evs if s == "#%sHubClose" % prefix), "%s: the X = hub:close" % what)
    vis = [str(r[0]) for r in hb.tabs(S.hub, P.pr.getUuid())]
    tabs = [mk for p, mk in apps if p == prefix + "BigTabs" and mk.startswith("Button")]
    K.eq(len(tabs), len(vis), "%s: row 2 = one tab per visible Storage tab %s" % (what, vis))
    for k, t in enumerate(vis):
        K.check(any(("hub:" + t) in tx for s, tx in evs if s == "#%sBigT%d" % (prefix, k)), "%s: row 2 tab %d bound to hub:%s" % (what, k, t))
    ids = set()
    for _p, mk in apps:
        ids |= set(x.group(2) for x in DECL_RE.finditer(SUI.render(mk)))
    bs = [s for s, _t in evs]
    bad = [s for s, _d in sets if s.lstrip("#").split(".")[0] not in ids] + [s for s in bs if s.lstrip("#") not in ids]
    K.check(not bad, "%s: every b.set and binding names an element that exists (%d sets, %d bindings): %s" % (what, len(sets), len(bs), bad[:4]))
    last = E.br.get("hub:last:" + str(P.pr.getUuid()))
    K.check(last is not None and str(last.get(S.hub)) == tab, "%s: hub:last remembers %s -> %s" % (what, S.hub, tab))
    return cmds, evs


H.page_check = page_check17      # run_hub / the E2E phase call H.page_check: the kit 1.7 check from now on


def prep(E, J, home):
    from jpype import JClass
    J("VCfg").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyVault")
    P = lambda *a: E.Paths.get(os.path.join(home, *a))
    J("VCfg").DIR = P()
    J("VCfg").VDIR = P("vaults")
    J("VCfg").FILE = P("config.properties")
    J("VCfg").LOGF = P("vault.log")
    J("VCfg").NAMESF = P("names.properties")
    J("VStore").STOPPING = False
    J("VStore").SAVER = None


def live_prep(E, J, home):
    J("VCfg").PAGE_MODE = False
    J("VCfg").OPEN_MODE = "chest"
    J("VStore").loadNames()


def replace_prep(J, on):
    J("VCfg").PAGE_MODE = not on
    J("VCfg").OPEN_MODE = "chest" if on else "page"


def live_player(home):
    d = os.path.join(home, "vaults")
    fs = sorted(f for f in os.listdir(d) if f.endswith(".json")) if os.path.isdir(d) else []
    if not fs:
        return None
    j = json.load(open(os.path.join(d, fs[0]), encoding="utf8"))
    return j["uuid"], j.get("name") or "SkyyLive"


def after_open(K, E, J, P, pg):
    s = J("VSessions").current(P.pr.getUuid())
    K.check(s is not None and pg.sess is not None and int(s.mode) == 1, "PAGE: page mode = the vault page WITH its window (a live VSession, mode 1)")


def chk_next(K, E, J, P, before, after, f0):
    K.check(after is not None and str(after.getClass().getSimpleName()) == "VaultPage", "CLICK: Next (not a hub click) keeps the vault page")
    K.check(int(after.sel) == 2 or "locked" in str(after.info) or len(E.sent(P)) > f0, "CLICK: Next acts on the vault (page %s, %s)" % (after.sel, after.info))


def extra_hub(K, W, J):
    import jpype
    from jpype import JClass
    E = W.E
    Fn = JClass("java.util.function.Function")
    f = E.br.get("storage:fn:find:vault")
    K.check(f is not None and Fn.class_.isInstance(f) and str(f.getClass().getName()) == PKG + "VFindFn", "FIND: storage:fn:find:vault is put by register")
    ob = E.br.get("vault:fn:openBank")
    K.check(ob is not None and Fn.class_.isInstance(ob) and str(ob.getClass().getName()) == PKG + "VBankOpen", "MERGE: vault:fn:openBank is put by register")
    u = W.O.pr.getUuid()
    d = J("VStore").load(u)
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    pg1 = d.page(1)
    pg1[0] = IS("Wood_Oak_Log", 64)
    pg1[3] = IS("Rock_Stone", 10)
    far = d.page(int(d.unlocked) + 1)
    far[0] = IS("Wood_Oak_Log", 5)
    Obj = JClass("java.lang.Object")
    q = lambda *a: f.apply(jpype.JArray(Obj)(list(a)))
    ans = lambda r: [(str(x[0]), int(x[1])) for x in r]
    for text, want in (("oak log", [("vault", 64)]), ("OAK_LOG", [("vault", 64)]), ("wood_oak", [("vault", 64)]), ("rock", [("vault", 10)]),
                       ("x", []), ("", []), ("diamond", [])):
        r = q(u, text)
        K.check(r is not None and ans(r) == want, "FIND: %r -> %s (%s)" % (text, want, None if r is None else ans(r)))
    K.check(len(f.apply("junk")) == 0 and len(q(None, "oak")) == 0 and len(f.apply(None)) == 0, "FIND: junk / no UUID / null -> empty, never null")
    J("VaultHubOpen").unregister()
    K.check(E.br.get("storage:fn:find:vault") is None and E.br.get("vault:fn:openBank") is None, "FIND / MERGE: unregister removes storage:fn:find:vault + vault:fn:openBank")
    other = JClass("java.util.HashMap")()
    E.br.put("storage:fn:find:vault", other)
    E.br.put("vault:fn:openBank", other)
    J("VaultHubOpen").unregister()
    K.check(E.br.get("storage:fn:find:vault") is not None and E.br.get("vault:fn:openBank") is not None, "FIND / MERGE: unregister leaves keys another jar put")
    E.br.remove("storage:fn:find:vault")
    E.br.remove("vault:fn:openBank")
    src = open(os.path.join(HERE, "build_skyyvault_%s.py" % VERSION), encoding="utf8").read()
    m = re.search(r'VAULT_PAGE_CHECKED = "([0-9a-f]{12})"', src)
    import zipfile
    data = zipfile.ZipFile(S.jar).read("com/skyy/vault/SkyyVaultPlugin.class")
    K.check(m is not None and ("page " + m.group(1)).encode() in data, "PAGE: the built page id = VAULT_PAGE_CHECKED %s (the ready line)" % (m and m.group(1)))
    J("VCfg").PAGE_MODE = False
    J("VCfg").OPEN_MODE = "chest"
    X = W.mkp(E.UUID.randomUUID(), "SkyyChest")
    E.br.put("hub:last:" + str(X.pr.getUuid()), JClass("java.util.concurrent.ConcurrentHashMap")())
    J("VaultHubOpen").register()
    r = str(J("HubBar").open(X.pr, X.pr.getUuid(), "storage", "vault"))
    E.pump(X)
    pg = X.pm.getCustomPage()
    K.check(r == "bridge" and pg is not None and str(pg.getClass().getSimpleName()) == "VaultPage" and pg.sess is None,
            "PAGE: chest mode = the vault page with the page buttons, no session (%s)" % r)
    # ---- PAGE17: the chest-mode page (the page buttons, no slots) on the kit 1.7 shell too
    HBv = J("HubBar")
    H.page_check(K, E, S, X, pg, HBv, "PAGE17 chest mode")
    # ---- ROW1: SkyyMenu's hub:def entries -> one row-1 button per hub + Home; clicks route through HubBar.route
    import jpype as _jp
    ObjA = lambda xs: _jp.JArray(JClass("java.lang.Object"))(xs)
    E.br.put("hub:def:home", ObjA(["Home", "skymenu", "Skyy_Menu", None]))
    for _h in SUI.HUBS:
        E.br.put("hub:def:" + _h, ObjA([SUI.hub_title_now(_h), "zz" + _h, "Skyy_Menu", None]))
    cm1, ev1 = H.page_check(K, E, S, X, pg, HBv, "ROW1 page (with SkyyMenu's hub defs)")
    rowb = [s for s, t in ev1 if s and s.startswith("#SkyyVFBig") and "hub:h:" in t]
    K.eq(len(rowb), 1 + len(SUI.HUBS), "ROW1: one row-1 button per hub + Home, each bound to hub:h:<id>")
    mark = "#SkyyVFTitle.Text"

    def clk(Y, a):
        n = len(E.sent(Y))
        E.CM.lines.clear()
        Y.pm.handleLegacyCustomPageEvent(Y.ref, Y.st, E.CPE(E.CPT.Data, '{"a":"%s"}' % a))
        E.pump(Y)
        return Y.pm.getCustomPage(), n
    same = lambda a, b_: a is not None and b_ is not None and int(JClass("java.lang.System").identityHashCode(a)) == int(JClass("java.lang.System").identityHashCode(b_))
    p1, n = clk(X, "hub:h:market")
    K.check("zzmarket" in [str(x) for x in E.CM.lines] and same(p1, pg) and mark in E.strs_of(X, n),
            "ROW1: another hub (no tab loaded) runs its hub command and the page is answered (%s)" % list(E.CM.lines))
    p1, n = clk(X, "hub:h:storage")
    K.check(same(p1, pg) and mark in E.strs_of(X, n), "ROW1: the page's own hub (Storage) answers, the page stays")
    p1, n = clk(X, "hub:h:home")
    K.check("skymenu" in [str(x) for x in E.CM.lines] and same(p1, pg) and mark in E.strs_of(X, n), "ROW1: Home runs /skymenu and the page is answered")
    # ---- DLG: the buy confirm window on the hub page; its rows lead away the Esc way, Cancel returns to the vault
    Long = JClass("java.lang.Long")

    def opend():
        dg = J("VBuyDlg")(X.pr, 3, Long(50000), 3, 1)
        X.pm.openCustomPage(X.ref, X.st, dg)
        E.pump(X)
        return X.pm.getCustomPage()
    d1 = opend()
    K.check(d1 is not None and str(d1.getClass().getSimpleName()) == "VBuyDlg", "DLG: the confirm window opens")
    H.page_check(K, E, S, X, d1, HBv, "PAGE17 buy confirm window", prefix="SkyyVDlg", idp="SkyyVDlg", pager_ok=False)
    for _h in ["home"] + list(SUI.HUBS):
        E.br.remove("hub:def:" + _h)
    p1, n = clk(X, "hub:h:storage")
    K.check(same(p1, d1) and "#SkyyVDlgTitle.Text" in E.strs_of(X, n) and not bool(d1.done), "DLG: row 1's Storage answers, the window stays open, nothing bought")
    p1, n = clk(X, "hub:close")
    K.check(p1 is None and "Nothing was bought" in E.strs_of(X, n) and bool(d1.done), "DLG: the X closes the window - nothing bought, said in chat")
    d1 = opend()
    p1, n = clk(X, "hub:vault")
    K.check(p1 is not None and str(p1.getClass().getSimpleName()) == "VaultPage" and "Nothing was bought" in E.strs_of(X, n),
            "DLG: row 2's Vault tab opens the vault, the window goes the Esc way (%s)" % (p1 and p1.getClass().getSimpleName()))
    d1 = opend()
    p1, n = clk(X, "dlgno")
    K.check(p1 is not None and str(p1.getClass().getSimpleName()) == "VaultPage" and bool(d1.done), "DLG: Cancel still returns to the vault (dlgBack)")
    J("VaultHubOpen").unregister()
    J("VCfg").PAGE_MODE = True
    J("VCfg").OPEN_MODE = "page"


# =====================================================================================================================  E2E (REAL SkyyBank)
def run_e2e(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    W = H.boot(scratch, jar, "e2e")
    E = W.E
    J = lambda n: JClass(PKG + n)
    BK = lambda n: JClass("com.skyy.bank." + n)
    HB = J("HubBar")
    E.br = HB.map()
    TRUE, FALSE = JClass("java.lang.Boolean").TRUE, JClass("java.lang.Boolean").FALSE
    Long = JClass("java.lang.Long")
    Obj = JClass("java.lang.Object")
    K.check(int(JClass("java.lang.System").identityHashCode(E.br)) == int(JClass("java.lang.System").identityHashCode(JClass("com.skyy.core.ui.HubBar").map())),
            "E2E: the vault's HubBar, SkyyCore's HubBar and SkyyBank share skyy.bridge")
    vhome = os.path.join(scratch, "e2e_vault")
    bhome = os.path.join(scratch, "e2e_bank")
    os.makedirs(os.path.join(vhome, "vaults"), exist_ok=True)
    os.makedirs(os.path.join(bhome, "accounts"), exist_ok=True)
    prep(E, J, vhome)
    # the real bank, pointed at its own scratch folder (the SkyyBank harness prep)
    BK("BankStore").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyBank")
    BK("BankStore").DIR = E.Paths.get(os.path.join(bhome, "accounts"))
    BK("BankConfig").FILE = E.Paths.get(os.path.join(bhome, "config.properties"))
    BK("BankConfig").STATE = E.Paths.get(os.path.join(bhome, "state.properties"))
    BK("BankWatch").STOP = False
    BK("BankWatch").EXEC = E.U.allocateInstance(E.RecEx.class_)
    BK("BankConfig").load()
    # stand-in purses + profiles (the SkyyBank 0.1.9 harness World, on the shared bridge)
    PURSE, PROF = {}, {}

    def key(u):
        p = PROF.get(str(u), 1)
        return str(u) if p == 1 else "%s-p%d" % (u, p)

    @JImplements("java.util.function.Function")
    class KeyFn:
        @JOverride
        def apply(self, u):
            return key(u)

    @JImplements("java.util.function.Function")
    class Get:
        @JOverride
        def apply(self, u):
            return Long.valueOf(PURSE.get(key(u), 0))

    @JImplements("java.util.function.Function")
    class Add:
        @JOverride
        def apply(self, a):
            u, n = a[0], int(a[1])
            PURSE[key(u)] = PURSE.get(key(u), 0) + n
            return Long.valueOf(PURSE[key(u)])

    @JImplements("java.util.function.Function")
    class Take:
        @JOverride
        def apply(self, a):
            u, n = a[0], int(a[1])
            if PURSE.get(key(u), 0) < n:
                return FALSE
            PURSE[key(u)] = PURSE.get(key(u), 0) - n
            return TRUE
    for k_, v_ in (("profile:fn:key", KeyFn()), ("coins:fn:get", Get()), ("coins:fn:add", Add()), ("coins:fn:take", Take())):
        E.br.put(k_, v_)

    @JImplements("java.util.function.Function")
    class Unl:
        def __init__(self, ans):
            self.ans = ans

        @JOverride
        def apply(self, o):
            return self.ans

    P = W.P
    u = P.pr.getUuid()
    PURSE[str(u)] = 50000
    E.br.put("hub:last:" + str(u), JClass("java.util.concurrent.ConcurrentHashMap")())
    K.eq(int(BK("BankPanelFn").register()), 1, "E2E: SkyyBank puts bank:fn:panel + bank:fn:move")
    K.eq(int(BK("BankHubOpen").register()), 1, "E2E: SkyyBank puts its Bank tab")
    vis = E.br.get("hub:tab:storage:bank")[5]
    K.check(vis.apply(u) == TRUE, "E2E: without SkyyVault 0.1.8 the Bank tab shows")
    K.eq(int(J("VaultHubOpen").register()), 1, "E2E: SkyyVault puts its tab + vault:fn:openBank")
    K.check(vis.apply(u) == FALSE and bool(BK("BankPanelFn").merged()), "E2E: with vault:fn:openBank the Bank tab leaves the Storage bar")
    K.eq([str(x[0]) for x in HB.tabs("storage", u)], ["vault"], "E2E: the Storage bar = Vault only (Bank merged into it)")

    # /bank (no arguments) -> the Vault tab (page mode: the page WITH its slots)
    BK("BankCmd").openPage(P.ref, P.st, P.pr)
    E.pump(P)
    pg = P.pm.getCustomPage()
    K.check(pg is not None and str(pg.getClass().getName()) == PKG + "VaultPage" and pg.sess is not None, "E2E: /bank opens the Vault tab (the vault page with its slots)")
    cmds, evs = H.page_check(K, E, S, P, pg, HB, "E2E page")

    def build(page):
        b = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")()
        ev = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")()
        page.build(P.ref, b, ev, P.st)
        return H.cmds_of(b), H.events_of(ev)

    def sets(cm):
        # a Set command's data is {"0": value} (JSON): the plain value
        out = {}
        for ty, s_, t_, d_ in cm:
            if ty == "Set":
                try:
                    out[s_] = json.loads(d_).get("0")
                except Exception:
                    out[s_] = d_
        return out

    def bound(ev, sel):
        return [t for s_, t in ev if s_ == sel]
    st = sets(cmds)
    K.check("50,000" in str(st.get("#SkyyVBPurse.Text")) and re.sub(r"[^0-9a-z]", "", str(st.get("#SkyyVBBalance.Text"))) == "0",
            "E2E: the panel shows PURSE 50,000 and BANK 0 (%s / %s)" % (st.get("#SkyyVBPurse.Text"), st.get("#SkyyVBBalance.Text")))
    K.check("Interest" in str(st.get("#SkyyVBRate.Text")) and "Refresh" not in str(st.get("#SkyyVBNext.Text")), "E2E: the rate line + the next payout line (no 'Refresh to update')")
    K.check("bank" in str(st.get("#SkyyVBSub.Text")).lower() and "#SkyyVSub.Text" in st, "E2E: the bank profile line on top, the vault line below")
    order = [t for ty, s_, t, d_ in cmds if t]
    ib = [i for i, t in enumerate(order) if "#SkyyVBBal " in t]
    iv = [i for i, t in enumerate(order) if "#SkyyVBox " in t]
    K.check(ib and iv and ib[0] < iv[0], "E2E: coins on top, items below (the panel is appended before the vault well)")
    for sel in ("#SkyyVBDepAll", "#SkyyVBDep", "#SkyyVBWd", "#SkyyVBWdAll"):
        K.check(any(pg.btok in t for t in bound(evs, sel)), "E2E: %s carries the page's click token" % sel)
    K.check(bound(evs, "#SkyyVBAmount"), "E2E: Enter in the amount box is bound (Validating)")
    K.check(any("brefresh" in t for t in bound(evs, "#SkyyVBRefresh")), "FIX: Refresh is bound (brefresh)")

    def click(a, amt, tok):
        d = {"a": a, "@VBAmount": amt}
        if tok is not None:
            d["t"] = tok
        n0 = len(E.sent(P))
        P.pm.handleLegacyCustomPageEvent(P.ref, P.st, E.CPE(E.CPT.Data, json.dumps(d)))
        E.pump(P)
        return P.pm.getCustomPage(), len(E.sent(P)) > n0
    bank = lambda: int(BK("BankStore").get(u))
    tok = str(pg.btok)
    pg2, ans = click("bdep", "500", tok)
    K.check(ans and str(pg2.info).startswith("+Deposited 500") and bank() == 500 and PURSE[str(u)] == 49500,
            "E2E: Deposit 500 -> bank 500, purse 49,500, green line, answered (%s)" % pg2.info)
    pg2, ans = click("bdep", "500", tok)
    K.check(ans and "older copy" in str(pg2.info) and bank() == 500 and PURSE[str(u)] == 49500, "E2E: the same click again (used-up token) moves nothing (%s)" % pg2.info)
    pg2, ans = click("bdep", "500", "deadbeef")
    K.check("older copy" in str(pg2.info) and bank() == 500, "E2E: a wrong token moves nothing")
    pg2, ans = click("bdep", "999999", str(pg2.btok))
    K.check(str(pg2.info).startswith("-Not enough") and bank() == 500 and PURSE[str(u)] == 49500, "E2E: more than the purse -> refused, nothing moves (%s)" % pg2.info)
    K.eq(str(pg2.bamt), "999999", "E2E: the typed amount is kept after a refused move")
    cm2, ev2 = build(pg2)
    K.eq(sets(cm2).get("#SkyyVBAmount.Value"), "999999", "E2E: ... and drawn back into the box on the redraw")
    pg2, ans = click("bamount", "700", None)
    K.check(ans and str(pg2.info).startswith("=Click Deposit or Withdraw") and bank() == 500, "E2E: Enter in the box -> a hint, nothing moves")
    pg2, ans = click("bwdall", "", str(pg2.btok))
    K.check(str(pg2.info).startswith("+Withdrew 500") and bank() == 0 and PURSE[str(u)] == 50000, "E2E: Withdraw all -> bank 0, purse back to 50,000 (%s)" % pg2.info)
    pg2, ans = click("bdep", "", str(pg2.btok))
    K.check(str(pg2.info).startswith("=Type an amount") and bank() == 0, "E2E: Deposit with an empty box -> the hint, nothing moves")
    pg2, ans = click("bdepall", "", str(pg2.btok))
    K.check(str(pg2.info).startswith("+Deposited 50000") and bank() == 50000 and PURSE[str(u)] == 0 and str(pg2.bamt) == "", "E2E: Deposit all -> the whole purse, the box cleared (%s)" % pg2.info)
    # review fix: Refresh after a chat /bank withdraw shows the new numbers, moves nothing, mints a new token, keeps the typed amount
    BK("BankCmd").move(u, False, "1000")
    t_old = str(pg2.btok)
    pg2, ans = click("brefresh", "77", None)
    K.check(ans and str(pg2.info).startswith("=Coins up to date") and bank() == 49000 and PURSE[str(u)] == 1000,
            "FIX: Refresh answers, moves nothing (%s)" % pg2.info)
    K.check(str(pg2.btok) != t_old and str(pg2.bamt) == "77", "FIX: Refresh = a redraw: a new click token, the typed amount kept")
    cmr, evr = build(pg2)
    K.check("1,000" in str(sets(cmr).get("#SkyyVBPurse.Text")) and "49,000" in str(sets(cmr).get("#SkyyVBBalance.Text")),
            "FIX: the redrawn panel shows the chat move (purse %s / bank %s)" % (sets(cmr).get("#SkyyVBPurse.Text"), sets(cmr).get("#SkyyVBBalance.Text")))
    pg2, ans = click("bdep", "1", t_old)
    K.check("older copy" in str(pg2.info) and bank() == 49000, "FIX: a coin click from before the Refresh moves nothing")
    BK("BankCmd").move(u, True, "1000")
    K.check(bank() == 50000 and PURSE[str(u)] == 0, "FIX: state restored for the next steps")
    # a profile switch after the page was drawn: refused by SkyyBank's same-profile check
    PROF[str(u)] = 2
    PURSE["%s-p2" % u] = 1000
    pg2, ans = click("bdep", "100", str(pg2.btok))
    K.check("profile changed" in str(pg2.info) and PURSE["%s-p2" % u] == 1000 and bank() == 0, "E2E: a profile switch after the draw -> nothing moves (%s)" % pg2.info)
    pg2, ans = click("bdep", "100", str(pg2.btok))
    K.check(str(pg2.info).startswith("+Deposited 100") and PURSE["%s-p2" % u] == 900 and bank() == 100, "E2E: the redrawn page (profile 2) moves on profile 2 (%s)" % pg2.info)
    PROF[str(u)] = 1
    # a locked bank
    E.br.put("bank:fn:unlocked", Unl(FALSE))
    cm3, ev3 = build(pg2)
    K.check("still locked" in str(sets(cm3).get("#SkyyVBLockTxt.Text")) and not bound(ev3, "#SkyyVBDep") and "#SkyyVBPurse.Text" not in sets(cm3),
            "E2E: a locked bank -> the lock text, no coin button")
    mv = E.br.get("bank:fn:move")
    r = mv.apply(jpype.JArray(Obj)([u, "deposit", "1", key(u), None]))
    K.check(str(r).startswith("-Your bank is locked") and bank() == 50000, "E2E: bank:fn:move refuses a locked bank (%s)" % r)
    E.br.put("bank:fn:unlocked", Unl(TRUE))
    cm3, ev3 = build(pg2)
    K.check("#SkyyVBPurse.Text" in sets(cm3) and bound(ev3, "#SkyyVBDep"), "E2E: bank:fn:unlocked TRUE -> the panel again")
    E.br.remove("bank:fn:unlocked")
    # junk to bank:fn:move / bank:fn:panel
    K.check(str(mv.apply("junk")).startswith("-") and str(mv.apply(jpype.JArray(Obj)([u, "steal", "1", None, None]))).startswith("=") and bank() == 50000,
            "E2E: bank:fn:move junk / an unknown action -> refused, nothing moves")
    K.check(E.br.get("bank:fn:panel").apply("junk") is None, "E2E: bank:fn:panel junk -> null (the vault shows 'not on this server')")
    # no SkyyBank
    BK("BankPanelFn").unregister()
    K.check(E.br.get("bank:fn:panel") is None and E.br.get("bank:fn:move") is None, "E2E: SkyyBank's unregister removes its Functions")
    cm4, ev4 = build(pg2)
    K.check("not on this server" in str(sets(cm4).get("#SkyyVBLockTxt.Text")), "E2E: no SkyyBank -> 'The bank is not on this server right now'")
    pg2.btok = "abc"
    pg2b, ans = click("bdep", "1", "abc")
    K.check(str(pg2b.info).startswith("-The bank is not on this server") and bank() == 50000, "E2E: no SkyyBank -> a click moves nothing")
    BK("BankPanelFn").register()
    # an unreadable vault file: the coins still show and move
    X = W.O
    ux = X.pr.getUuid()
    PURSE[str(ux)] = 300
    open(os.path.join(vhome, "vaults", str(ux) + ".json"), "w").write("{ this is not json")
    ob = E.br.get("vault:fn:openBank")
    K.check(ob.apply(ux) == TRUE, "E2E: vault:fn:openBank with an unreadable vault file still answers TRUE")
    E.pump(X)
    px = X.pm.getCustomPage()
    K.check(px is not None and str(px.getClass().getName()) == PKG + "VaultPage" and px.sess is None and "cannot be read" in str(px.info),
            "E2E: ... the vault page without slots, the refusal on its result line (%s)" % (px and px.info))
    bx = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")()
    evx = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")()
    px.build(X.ref, bx, evx, X.st)
    sx = sets(H.cmds_of(bx))
    K.check("#SkyyVErr.Text" in sx and "300" in str(sx.get("#SkyyVBPurse.Text")), "E2E: the unreadable view still has the coin panel (purse 300)")
    n0 = len(E.sent(X))
    X.pm.handleLegacyCustomPageEvent(X.ref, X.st, E.CPE(E.CPT.Data, json.dumps({"a": "bdepall", "@VBAmount": "", "t": str(px.btok)})))
    E.pump(X)
    K.check(str(X.pm.getCustomPage().info).startswith("+Deposited 300") and int(BK("BankStore").get(ux)) == 300 and PURSE[str(ux)] == 0,
            "E2E: Deposit all works on the unreadable-vault view (%s)" % X.pm.getCustomPage().info)
    # review fix: a vault refusal (profile still loading) while a page-mode session is live -> the session is released first
    K.check(ob.apply(u) == TRUE, "FIX A1 setup: vault:fn:openBank on the live page")
    E.pump(P)
    s0 = J("VSessions").current(u)
    K.check(s0 is not None and P.pm.getCustomPage() is not None and P.pm.getCustomPage().sess is not None, "FIX A1 setup: a live page-mode vault session")
    E.br.put("profile:busy:" + str(u), TRUE)
    K.check(ob.apply(u) == TRUE, "FIX A1: a refusal still answers TRUE (the coins show)")
    E.pump(P)
    pb = P.pm.getCustomPage()
    K.check(pb is not None and str(pb.getClass().getName()) == PKG + "VaultPage" and pb.sess is None and "still loading" in str(pb.info),
            "FIX A1: the vault page without slots, the refusal on its line (%s)" % (pb and pb.info))
    K.check(J("VSessions").current(u) is None and bool(s0.closed), "FIX A1: the old live session was released (closed, not left under the page)")
    E.br.remove("profile:busy:" + str(u))
    J("VSessions").BUSYSEEN.remove(u)
    J("VSessions").SWITCHED.remove(u)
    # the Bank tab's own open Function -> the Vault tab too
    opn = E.br.get("hub:tab:storage:bank")[4]
    P.pm.handleLegacyCustomPageEvent(P.ref, P.st, E.CPE(E.CPT.Data, '{"a":"hub:close"}'))
    E.pump(P)
    K.check(opn.apply(u) == TRUE, "E2E: the Bank tab's open Function answers TRUE")
    E.pump(P)
    K.check(P.pm.getCustomPage() is not None and str(P.pm.getCustomPage().getClass().getName()) == PKG + "VaultPage", "E2E: ... and opens the Vault tab")
    K.check(ob.apply("junk") == FALSE and ob.apply(E.UUID.randomUUID()) == FALSE, "E2E: vault:fn:openBank junk / offline -> FALSE (SkyyBank opens its own page)")
    # ================================================ 0.1.9 PAGE17: every view the E2E draws, on the kit 1.7 shell
    pv = P.pm.getCustomPage()
    if pv is None or str(pv.getClass().getSimpleName()) != "VaultPage":
        ob.apply(u)
        E.pump(P)
        pv = P.pm.getCustomPage()
    H.page_check(K, E, S, P, pv, HB, "PAGE17 merged page (page mode)")
    xv = X.pm.getCustomPage()
    E.br.put("hub:last:" + str(X.pr.getUuid()), JClass("java.util.concurrent.ConcurrentHashMap")())   # (the stand-in world makes it for P only)
    if xv is not None and str(xv.getClass().getSimpleName()) == "VaultPage":
        cmx, _evx = H.page_check(K, E, S, X, xv, HB, "PAGE17 unreadable-vault view")
        K.check(any("#SkyyVErr.Text" == s_ for ty, s_, t_, d_ in cmx), "PAGE17: ... it is the unreadable view (the red line)")
    else:
        K.check(False, "PAGE17: the unreadable-vault view is no longer open (%s)" % xv)
    E.br.put("bank:fn:unlocked", Unl(FALSE))
    cml, _evl = H.page_check(K, E, S, P, pv, HB, "PAGE17 locked bank")
    K.check("#SkyyVBLockTxt.Text" in sets(cml), "PAGE17: ... the lock text instead of the coin panel")
    E.br.remove("bank:fn:unlocked")
    BK("BankPanelFn").unregister()
    cmn, _evn = H.page_check(K, E, S, P, pv, HB, "PAGE17 no SkyyBank")
    K.check("not on this server" in str(sets(cmn).get("#SkyyVBLockTxt.Text")), "PAGE17: ... the 'not on this server' text")
    BK("BankPanelFn").register()
    # ================================================ 0.1.9 ITEMS: a vault item put / take smoke (page mode, the live vault window)
    sv = J("VSessions").current(u)
    K.check(sv is not None and sv.view is not None and not bool(sv.closed), "ITEMS: a live page-mode vault window")
    if sv is not None and sv.view is not None:
        IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
        free = [i for i in range(int(sv.store)) if not bool(sv.ctrlLive(i)) and (sv.view.getItemStack(i) is None or bool(sv.view.getItemStack(i).isEmpty()))]
        K.check(len(free) > 0, "ITEMS: a free vault slot (%d free)" % len(free))
        if free:
            i0 = free[0]
            sv.view.setItemStackForSlot(i0, IS("Rock_Stone", 7))
            J("VSessions").syncView(sv)
            got = J("VStore").load(u).page(int(sv.page))[i0]
            K.check(got is not None and str(got.getItemId()) == "Rock_Stone" and int(got.getQuantity()) == 7,
                    "ITEMS: put 7 Rock_Stone into vault slot %d -> the vault page holds them (%s)" % (i0, got))
            sv.view.removeItemStackFromSlot(i0)
            J("VSessions").syncView(sv)
            got = J("VStore").load(u).page(int(sv.page))[i0]
            K.check(got is None or bool(got.isEmpty()), "ITEMS: took them out again -> the vault slot is empty (%s)" % got)
    # ================================================ 0.1.9 DLG: Buy on the hub-page confirm window buys exactly once
    PURSE[str(u)] = 10000000
    dd = J("VStore").load(u)
    nxt = int(dd.unlocked) + 1
    price = int(J("VStore").price(nxt))
    dg = J("VBuyDlg")(P.pr, nxt, Long(price), 3, 1)
    P.pm.openCustomPage(P.ref, P.st, dg)
    E.pump(P)
    H.page_check(K, E, S, P, dg, HB, "PAGE17 buy confirm window (E2E)", prefix="SkyyVDlg", idp="SkyyVDlg", pager_ok=False)
    P.pm.handleLegacyCustomPageEvent(P.ref, P.st, E.CPE(E.CPT.Data, '{"a":"dlgbuy"}'))
    E.pump(P)
    K.check(int(J("VStore").load(u).unlocked) == nxt and PURSE[str(u)] == 10000000 - price,
            "DLG: Buy on the confirm window bought page %d once (purse -%d)" % (nxt, price))
    dg.handleDataEvent(P.ref, P.st, '{"a":"dlgbuy"}')
    E.pump(P)
    K.check(int(J("VStore").load(u).unlocked) == nxt and PURSE[str(u)] == 10000000 - price, "DLG: a second Buy on the same window does nothing (one-shot)")
    # SkyyVault gone: the Bank tab is back and /bank opens the bank page
    J("VaultHubOpen").unregister()
    K.check(vis.apply(u) == TRUE and not bool(BK("BankPanelFn").merged()), "E2E: without vault:fn:openBank the Bank tab shows again")
    P.pm.handleLegacyCustomPageEvent(P.ref, P.st, E.CPE(E.CPT.Data, '{"a":"hub:close"}'))
    E.pump(P)
    BK("BankCmd").openPage(P.ref, P.st, P.pr)
    E.pump(P)
    K.check(P.pm.getCustomPage() is not None and str(P.pm.getCustomPage().getClass().getName()) == "com.skyy.bank.BankPage", "E2E: ... and /bank opens the bank page")
    K.save()


S = H.Spec(name="SkyyVault", version=VERSION, pkg=PKG, hub="storage", tab="vault", mod="SkyyVault", open_cls="VaultHubOpen", vis_cls=None,
           page_cls="VaultPage", prefix="SkyyVF", idp="SkyyV", plugin_cls="SkyyVaultPlugin", register_call="VaultHubOpen.register",
           drop_call="VaultHubOpen.unregister", register=lambda J: J("VaultHubOpen").register(), prep=prep, live_prep=live_prep, replace_prep=replace_prep,
           live_player=live_player, after_open=after_open, clicks=[('{"a":"next"}', chk_next)], extra_hub=extra_hub,
           jar=os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyVault-%s.jar" % VERSION))), old_jar=os.path.join(HERE, "SkyyVault-0.1.8.jar"),
           scratch=os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "hubstore", "vault"))), script=__file__,
           added=[],
           # 0.1.8 -> 0.1.9: the jar's HubBar only GAINS the kit 1.6 + 1.7 members (put / removeAll / handle / build byte-identical); the
           # two pages' build + hub click; the version text / the vault file stamp
           expect={"HubBar": ['+<clinit>', '+f ROW_IDS', '+f ROW_TITLES', '+m bigLab', '+m bigRow', '+m bigRowFill', '+m bigTabLab', '+m bigTabsFill', '+m build2', '+m buildRow', '+m def4', '+m defOf', '+m defTab', '+m goHub', '+m growSize', '+m hasArt', '+m hostOf', '+m hostShown', '+m hostTab', '+m hubs', '+m iconOf', '+m okIcon', '+m okItem', '+m openSub', '+m page17', '+m pickTab', '+m putIcon', '+m putSub', '+m route', '+m rowLab', '+m rowStyle', '+m rowWidth', '+m selOf', '+m subIcon', '+m subTab', '+m subTabs', '+m tabBStyle', '+m tabLab', '+m titleOf'],
                   "VaultPage": ["~m build", "~m hubClick"], "VBuyDlg": ["+m hubAck", "+m hubClick", "~m build", "~m handleDataEvent"],
                   "SkyyVaultPlugin": ["~m setup"], "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "VStore": ["~m toDoc"]},
           extra_phases=[("e2e", run_e2e)])

if __name__ == "__main__":
    if HK.arg("--phase") == "compare":
        # 0.1.8 -> 0.1.9: the kit art is byte-identical, so only manifest.json changes (the hub harness's compare expects the 0.1.7 kit add)
        HK.run(name=S.name, version=S.version, jar=S.jar, old_jar=S.old_jar, pkg=S.pkg, scratch=S.scratch, expect=S.expect, added=S.added,
               phases=[], script=S.script, removed=S.removed)
    else:
        H.run(S)
