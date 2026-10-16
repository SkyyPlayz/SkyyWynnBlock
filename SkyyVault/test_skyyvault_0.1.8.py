"""Harness for SkyyVault 0.1.8 (MENU MERGE: Bank + Vault = one Vault tab, coins on top; tools/vault_0_1_8_patch.py). Build first:
python tools/vault_0_1_8_patch.py && python SkyyVault/build_skyyvault_0.1.8.py, and SkyyBank 0.1.15 (python tools/bank_0_1_15_patch.py &&
python SkyyBank/build_skyybank_0.1.15.py; SkyyCore 1.0.0's jar must exist)

    python SkyyVault/test_skyyvault_0.1.8.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Every child JVM has SkyyCore 1.0.0 + SkyyBank 0.1.15 on its class path (SKYY_HARNESS_CP), so the E2E phase runs the REAL bank code.
The phases of test_skyyvault_0.1.7.py (A verify, C compare 0.1.7 -> 0.1.8 + the kit bytes, HUB executed: REG / PAGE / CLICK / DROP on the
merged page, FIND, D live: two opens on a scratch COPY of the live Skyy_SkyyVault, AA engine-access audit), plus:
  E2E  the merged tab with the REAL SkyyBank 0.1.15 over stand-in purses (coins:fn:get / add / take, profile:fn:key):
       - SkyyBank's Bank tab hides while vault:fn:openBank is on the bridge; /bank (BankCmd.openPage) and the Bank tab's open Function
         open the VAULT page (page mode, with its slots); the page is a Sky Window hub page (H.page_check) with the panel's texts set
         from bank:fn:panel (purse / bank numbers, rate, profile line) and the 4 coin buttons bound with the page's click token
       - Deposit 500 -> purse -500, bank +500, a green line; the SAME click again (the used-up token) moves nothing; Withdraw all ->
         bank 0, purse back; more than the purse -> refused, nothing moves; Enter in the box -> a hint, nothing moves; a profile switch
         after the page was drawn -> refused, nothing moves; the typed amount stays on a redraw and clears after a done move
       - a locked bank (bank:fn:unlocked FALSE): the lock text, no coin button bound, bank:fn:move refuses; no SkyyBank: the "not on this
         server" text and a click moves nothing
       - an unreadable vault file: vault:fn:openBank still opens the page (no slots, the refusal on its result line) and coins still move
       - review fixes: Refresh redraws (new numbers after a chat move, new token, nothing moves); a refusal with a live page-mode session
         releases that session first
       - junk / offline -> FALSE; unregister removes only OUR vault:fn:openBank; then the Bank tab shows again and /bank opens the bank page
Exit code 1 on any failure.
"""
import os, sys, json, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import hub_tab_harness as H

VERSION = "0.1.8"
PKG = "com.skyy.vault."
BANK_JAR = os.path.join(ROOT, "SkyyBank", "SkyyBank-0.1.15.jar")
CORE_JAR = os.path.join(ROOT, "SkyyCore", "SkyyCore-1.0.0.jar")
os.environ["SKYY_HARNESS_CP"] = os.pathsep.join([CORE_JAR, BANK_JAR])


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
           jar=os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyVault-%s.jar" % VERSION))), old_jar=os.path.join(HERE, "SkyyVault-0.1.7.jar"),
           scratch=os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "hubstore", "vault"))), script=__file__,
           added=["VBankOpen"],
           expect={"VaultPage": ["+f bamt", "+f bbase", "+f bepoch", "+f bkey", "+f bseq", "+f btok", "+m bankClick", "+m bankPanel", "+m bcol",
                                 "+m bstr", "~c ", "~m build", "~m handleDataEvent"],
                   "VaultHubOpen": ["~m register", "~m unregister"], "SkyyVaultPlugin": ["~m setup"],
                   "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "VStore": ["~m toDoc"]},     # the version text / the vault file stamp
           extra_phases=[("e2e", run_e2e)])

if __name__ == "__main__":
    if HK.arg("--phase") == "compare":
        # 0.1.7 -> 0.1.8: the kit art is byte-identical, so only manifest.json changes (the hub harness's compare expects the 0.1.7 kit add)
        HK.run(name=S.name, version=S.version, jar=S.jar, old_jar=S.old_jar, pkg=S.pkg, scratch=S.scratch, expect=S.expect, added=S.added,
               phases=[], script=S.script, removed=S.removed)
    else:
        H.run(S)
