"""Harness for SkyyBank 0.1.15 (MENU MERGE: the coin panel on SkyyVault 0.1.8's Vault tab; tools/bank_0_1_15_patch.py). Build first:
python SkyyCore/build_skyycore_1.0.0.py (if its jar is missing), python tools/bank_0_1_15_patch.py && python SkyyBank/build_skyybank_0.1.15.py

    python SkyyBank/test_skyybank_0.1.15.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Every child JVM gets the SkyyCore jar on its class path (SKYY_HARNESS_CP). The OLD jar everywhere is the LIVE 0.1.14 (the SET pin).
The end-to-end run WITH the real SkyyVault 0.1.8 page is SkyyVault/test_skyyvault_0.1.8.py's E2E phase; this harness proves the bank side:
  A      every class loads + initialises with -Xverify:all (Core on the class path)
  C      class compare 0.1.14 -> 0.1.15: added BankPanelFn; changed exactly BankCmd.openPage, BankHubOpen.apply, BankHubVis.apply and the
         plugin's setup / shutdown (EXPECT) - every other class byte-identical (BankPage, BankStore, BankTick, the migrations, the kit data)
  KITBYTES  no kit art in the jar; manifest = stable name SkyyBank 0.1.15, no asset pack, Dependencies Skyy:SkyyCore >=1.0.0 <2.0.0
  HUB    tools/hub_tab_harness.py on SkyyCore's HubBar (owner SkyyBank): REG / PAGE / CLICK / DROP + VIS (bank:fn:unlocked, and the tab
         hidden while vault:fn:openBank is on the bridge) + Refresh + the page id = BANK_PAGE_CHECKED (BankPage unchanged)
  D      two opens of the page on a scratch COPY of the live Skyy_SkyyBank (nothing written)
  MERGE  bank:fn:panel / bank:fn:move EXECUTED over stand-in purses: the panel = the bank page's own texts (subText / fmt / rateText /
         nextText minus "(Refresh to update)" / gainText / the payout colour) + the profile key / epoch; locked -> "locked" + the text;
         moves: deposit / withdraw an amount, all, empty -> the hint, not enough -> refused, a profile switch after the draw -> refused,
         a locked bank -> refused, junk / unknown action -> refused (never throws), every move = BankCmd.move's own answer (byte-equal to
         /bank deposit's result line for the same state); /bank + the Bank tab's open Function open vault:fn:openBank when it is there
         (answer TRUE = no bank page; FALSE / throws = the bank page as 0.1.14); register / unregister only OUR Functions
  X      test_skyybank_0.1.9.py's exec phase, 0.1.14 vs 0.1.15 side by side (800 random steps: the same answers and files)
  LIVE2  test_skyybank_0.1.9.py's live phase: START TWICE on a scratch COPY of the live data with 0.1.14 and 0.1.15
  PAGE   page parity: the real BankPage built through each jar's hub bar (account / no account / Refresh / own tab): the same UI commands
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

VERSION = "0.1.15"
PKG = "com.skyy.bank."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyBank-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyBank-0.1.14.jar")
CORE_JAR = os.path.join(ROOT, "SkyyCore", "SkyyCore-1.0.0.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "hubstore", "bank")))
os.environ["SKYY_HARNESS_CP"] = CORE_JAR


def tmod(fn, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


T14 = tmod("test_skyybank_0.1.14.py", "tb0114")
T9 = T14.T9
T9.OLD_JAR = OLD_JAR
T14.OLD_JAR = OLD_JAR

EXPECT = {      # the class compare 0.1.14 -> 0.1.15
    "BankCmd": ["~m openPage"],                                  # /bank: the merged Vault tab first
    "BankHubOpen": ["~m apply"], "BankHubVis": ["~m apply"],     # the Bank tab: opens the Vault tab / hidden while merged
    "SkyyBankPlugin": ["~m setup", "~m shutdown"],               # BankPanelFn register / unregister + the ready line
}


def vis_cases(K, E, J, vis, u):
    T14.vis_cases(K, E, J, vis, u)
    from jpype import JClass, JImplements, JOverride
    TRUE, FALSE = JClass("java.lang.Boolean").TRUE, JClass("java.lang.Boolean").FALSE

    @JImplements("java.util.function.Function")
    class VOpen:
        @JOverride
        def apply(self, o):
            return TRUE
    E.br.put("vault:fn:openBank", VOpen())
    K.check(vis.apply(u) == FALSE, "VIS: vault:fn:openBank on the bridge (SkyyVault 0.1.8+) -> the Bank tab is hidden (merged into the Vault tab)")
    K.check(len(list(JClass("com.skyy.core.ui.HubBar").tabs("storage", u))) == 0, "VIS: merged -> HubBar.tabs(storage) has no Bank tab")
    E.br.put("vault:fn:openBank", "not a Function")
    K.check(vis.apply(u) == TRUE, "VIS: a vault:fn:openBank that is not a Function -> the Bank tab shows")
    E.br.remove("vault:fn:openBank")
    K.check(vis.apply(u) == TRUE, "VIS: vault:fn:openBank gone -> shown")


def extra_hub(K, W, J):
    T14.extra_hub(K, W, J)
    data = zipfile.ZipFile(JAR).read("com/skyy/bank/SkyyBankPlugin.class")
    K.check(b"Vault tab coin panel bank:fn:panel / bank:fn:move " in data, "PAGE: the ready line names the merge")


def run_merge(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    W = H.boot(scratch, jar, "merge")
    E = W.E
    J = lambda n: JClass(PKG + n)
    HB = JClass("com.skyy.core.ui.HubBar")
    E.br = HB.map()
    TRUE, FALSE = JClass("java.lang.Boolean").TRUE, JClass("java.lang.Boolean").FALSE
    Long = JClass("java.lang.Long")
    Obj = JClass("java.lang.Object")
    home = os.path.join(scratch, "merge_home")
    os.makedirs(os.path.join(home, "accounts"), exist_ok=True)
    T14.prep(E, J, home)
    J("BankConfig").load()
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

    @JImplements("java.util.function.Function")
    class Fixed:
        def __init__(self, ans):
            self.ans, self.calls = ans, []

        @JOverride
        def apply(self, o):
            self.calls.append(str(o))
            if self.ans == "throw":
                raise RuntimeError("boom")
            return self.ans
    for k_, v_ in (("profile:fn:key", KeyFn()), ("coins:fn:get", Get()), ("coins:fn:add", Add()), ("coins:fn:take", Take())):
        E.br.put(k_, v_)
    P = W.P
    u = P.pr.getUuid()
    PURSE[str(u)] = 12345
    T9.write_acc(home, str(u), 6789)
    K.eq(int(J("BankPanelFn").register()), 1, "MERGE: register puts the two Functions")
    pf, mv = E.br.get("bank:fn:panel"), E.br.get("bank:fn:move")
    K.check(pf is not None and mv is not None and str(pf.getClass().getName()) == PKG + "BankPanelFn" and int(pf.op) == 1 and int(mv.op) == 2,
            "MERGE: bank:fn:panel = BankPanelFn(1), bank:fn:move = BankPanelFn(2)")
    BP = J("BankPage")
    # ---- the panel = the bank page's own texts
    r = pf.apply(u)
    K.check(r is not None and len(r) == 10 and str(r[0]) == "ok", "MERGE: panel -> Object[10] 'ok'")
    on = bool(J("BankConfig").on())
    gain = int(J("BankStore").nextGain(u))
    K.eq(str(r[1]), str(BP.subText(u)), "MERGE: panel[1] = BankPage.subText (the profile line)")
    K.eq([str(r[2]), str(r[3])], ["12,345", "6,789"], "MERGE: panel purse / bank = the page's fmt numbers")
    K.eq(str(r[4]), str(BP.rateText(on)), "MERGE: panel[4] = BankPage.rateText")
    K.check(str(r[5]).startswith("Next interest") and "Refresh" not in str(r[5]), "MERGE: panel[5] = nextText without '(Refresh to update)' (%s)" % r[5])
    K.eq(str(r[6]), str(BP.gainText(True, 6789, gain, on)), "MERGE: panel[6] = BankPage.gainText")
    import skyyui as SUI
    want_col = SUI.COLOR["success"] if bool(BP.payoutOn(True, gain, on)) else SUI.COLOR["text"]
    K.eq(str(r[7]), want_col, "MERGE: panel[7] = the bank page's payout colour")
    K.check(str(r[8]) == str(u) and r[9] is None, "MERGE: panel[8] / [9] = the profile key + epoch (no SkyyProfiles: null epoch)")
    E.br.put("profile:epoch:" + str(u), Long.valueOf(7))
    r = pf.apply(u)
    K.check(int(r[9]) == 7, "MERGE: panel[9] = profile:epoch")
    K.check(pf.apply("junk") is None and pf.apply(None) is None, "MERGE: panel junk -> null")
    # ---- moves (each = BankCmd.move's own answer)
    arr = lambda *a: jpype.JArray(Obj)(list(a))
    k0, e0 = str(r[8]), r[9]
    bal = lambda: int(J("BankStore").get(u))
    res = str(mv.apply(arr(u, "deposit", "345", k0, e0)))
    K.check(res.startswith("+Deposited 345") and bal() == 7134 and PURSE[str(u)] == 12000, "MERGE: deposit 345 (%s)" % res)
    res = str(mv.apply(arr(u, "withdraw", "1k", k0, e0)))
    K.check(res.startswith("+Withdrew 1000") and bal() == 6134 and PURSE[str(u)] == 13000, "MERGE: withdraw 1k (%s)" % res)
    # byte-equal to the chat path for the same state
    want = str(J("BankCmd").move(u, True, "100"))
    J("BankCmd").move(u, False, "100")
    got = str(mv.apply(arr(u, "deposit", "100", k0, e0)))
    K.eq(re.sub(r"\d", "#", got), re.sub(r"\d", "#", want), "MERGE: a move answers exactly like /bank deposit (BankCmd.move)")
    J("BankCmd").move(u, False, "100")
    res = str(mv.apply(arr(u, "depall", "ignored", k0, e0)))
    K.check(res.startswith("+Deposited 13000") and PURSE[str(u)] == 0, "MERGE: depall = the whole purse, the typed text ignored (%s)" % res)
    res = str(mv.apply(arr(u, "wdall", "", k0, e0)))
    K.check(res.startswith("+Withdrew") and bal() == 0, "MERGE: wdall = the whole bank (%s)" % res)
    res = str(mv.apply(arr(u, "deposit", "", k0, e0)))
    K.check(res.startswith("=Type an amount") and bal() == 0, "MERGE: an empty amount -> the hint, nothing moves")
    res = str(mv.apply(arr(u, "deposit", "99999999", k0, e0)))
    K.check(res.startswith("-Not enough coins in your purse") and bal() == 0, "MERGE: more than the purse -> refused (%s)" % res)
    res = str(mv.apply(arr(u, "deposit", "abc", k0, e0)))
    K.check(res.startswith("-That is not a number") and bal() == 0, "MERGE: not a number -> refused")
    res = str(mv.apply(arr(u, "deposit", "12345678901234567890", k0, e0)))
    K.check(res.startswith("-") and bal() == 0, "MERGE: an overlong amount is cut to 16 characters and refused (%s)" % res)
    # profile switch after the draw (key, then epoch)
    PROF[str(u)] = 2
    PURSE["%s-p2" % u] = 500
    res = str(mv.apply(arr(u, "deposit", "100", k0, e0)))
    K.check("profile changed" in res and PURSE["%s-p2" % u] == 500, "MERGE: another profile key since the draw -> nothing moves (%s)" % res)
    PROF[str(u)] = 1
    E.br.put("profile:epoch:" + str(u), Long.valueOf(8))
    res = str(mv.apply(arr(u, "deposit", "100", k0, e0)))
    K.check("profile changed" in res, "MERGE: the same key but a new profile epoch (A -> B -> A) -> nothing moves")
    E.br.put("profile:epoch:" + str(u), Long.valueOf(7))
    PURSE[str(u)] = 1000
    res = str(mv.apply(arr(u, "deposit", "100", None, None)))
    K.check(res.startswith("=This page did not know your profile") and PURSE[str(u)] == 1000 and bal() == 0,
            "MERGE FIX: no profile key -> refused, nothing moves (%s)" % res)
    res = str(mv.apply(arr(u, "deposit", "100", None, e0)))
    K.check(res.startswith("=") and PURSE[str(u)] == 1000 and bal() == 0, "MERGE FIX: no key but an epoch -> refused too")
    K.check(str(pf.apply(u)[8]) == str(u), "MERGE FIX: the panel always carries a key (Core.pkey falls back to the UUID)")
    res = str(mv.apply(arr(u, "deposit", "100", k0, e0)))
    K.check(res.startswith("+Deposited 100") and bal() == 100, "MERGE: the keyed move after it works (%s)" % res)
    # locked
    E.br.put("bank:fn:unlocked", Fixed(FALSE))
    r2 = pf.apply(u)
    K.check(str(r2[0]) == "locked" and "locked" in str(r2[1]) and r2[2] is None, "MERGE: a locked bank -> panel 'locked' + the lock text (%s)" % r2[1])
    res = str(mv.apply(arr(u, "deposit", "100", k0, e0)))
    K.check(res.startswith("-Your bank is locked") and bal() == 100, "MERGE: a locked bank refuses a move")
    E.br.put("bank:fn:unlocked", Fixed("throw"))
    K.check(str(pf.apply(u)[0]) == "locked", "MERGE: bank:fn:unlocked throws -> locked (the tab rule)")
    E.br.put("bank:fn:unlocked", Fixed(TRUE))
    K.check(str(pf.apply(u)[0]) == "ok", "MERGE: bank:fn:unlocked TRUE -> ok")
    E.br.remove("bank:fn:unlocked")
    # junk
    for junk, what in (("junk", "a String"), (None, "null"), (arr(u), "a short array"), (arr("x", "deposit", "1", None, None), "no UUID"),
                       (arr(u, "steal", "1", None, None), "an unknown action")):
        try:
            res = str(mv.apply(junk))
            K.check((res.startswith("-") or res.startswith("=")) and bal() == 100, "MERGE: move(%s) -> refused, nothing moves (%s)" % (what, res[:40]))
        except Exception as ex:
            K.check(False, "MERGE: move(%s) threw %s" % (what, ex))
    # ---- /bank and the Bank tab open the Vault tab while merged
    vo = Fixed(TRUE)
    E.br.put("vault:fn:openBank", vo)
    K.check(bool(J("BankPanelFn").merged()), "MERGE: merged() while vault:fn:openBank is a Function")
    J("BankCmd").openPage(P.ref, P.st, P.pr)
    E.pump(P)
    K.check(vo.calls == [str(u)] and P.pm.getCustomPage() is None, "MERGE: /bank calls vault:fn:openBank with the UUID and opens no bank page (%s)" % vo.calls)
    J("BankHubOpen").register()
    opn = E.br.get("hub:tab:storage:bank")[4]
    K.check(opn.apply(u) == TRUE and len(vo.calls) == 2 and P.pm.getCustomPage() is None, "MERGE: the Bank tab's open Function -> the Vault tab")
    for ans, what in ((FALSE, "FALSE"), ("throw", "throws")):
        E.br.put("vault:fn:openBank", Fixed(ans))
        J("BankCmd").openPage(P.ref, P.st, P.pr)
        E.pump(P)
        pg = P.pm.getCustomPage()
        K.check(pg is not None and str(pg.getClass().getName()) == PKG + "BankPage", "MERGE: vault:fn:openBank %s -> /bank opens the bank page as 0.1.14" % what)
        P.pm.handleLegacyCustomPageEvent(P.ref, P.st, E.CPE(E.CPT.Data, '{"a":"close"}'))
        E.pump(P)
        K.check(opn.apply(u) == TRUE and str(P.pm.getCustomPage().getClass().getName()) == PKG + "BankPage", "MERGE: ... and the Bank tab opens the bank page")
        P.pm.handleLegacyCustomPageEvent(P.ref, P.st, E.CPE(E.CPT.Data, '{"a":"close"}'))
        E.pump(P)
    E.br.remove("vault:fn:openBank")
    K.check(not bool(J("BankPanelFn").merged()), "MERGE: not merged without vault:fn:openBank")
    # ---- unregister: only OUR Functions
    J("BankPanelFn").unregister()
    K.check(E.br.get("bank:fn:panel") is None and E.br.get("bank:fn:move") is None, "MERGE: unregister removes both")
    E.br.put("bank:fn:panel", "other")
    E.br.put("bank:fn:move", "other")
    J("BankPanelFn").unregister()
    K.check(str(E.br.get("bank:fn:panel")) == "other" and str(E.br.get("bank:fn:move")) == "other", "MERGE: unregister leaves keys another jar put")
    E.br.remove("bank:fn:panel")
    E.br.remove("bank:fn:move")
    su = H.calls_of(jar, PKG + "SkyyBankPlugin", "setup")
    sd = H.calls_of(jar, PKG + "SkyyBankPlugin", "shutdown")
    K.check("BankPanelFn.register" in su and "BankPanelFn.unregister" in sd, "MERGE: setup registers, shutdown unregisters (bytecode)")
    K.save()


S = H.Spec(name="SkyyBank", version=VERSION, pkg=PKG, hub="storage", tab="bank", mod="SkyyBank", open_cls="BankHubOpen", vis_cls="BankHubVis",
           page_cls="BankPage", prefix="SkyyBankF", idp="SkyyB", plugin_cls="SkyyBankPlugin", register_call="BankHubOpen.register",
           register=lambda J: J("BankHubOpen").register(), prep=T14.prep, vis_cases=vis_cases, clicks=[('{"a":"refresh","@BAmount":""}', T14.chk_refresh)],
           extra_hub=extra_hub, jar=JAR, old_jar=OLD_JAR, scratch=SCRATCH, script=__file__,
           hub_class="com.skyy.core.ui.HubBar", hub_owner="SkyyBank", kit_in_jar=False,
           added=["BankPanelFn"], removed=[],
           expect=EXPECT,
           extra_phases=[("merge", run_merge), ("exec", T14.controls_to_notes(T9.run_exec, "0.1.8")), ("live2", T9.run_live),
                         ("pageold", lambda out, jar, scratch, home: T14.page_dump(out, S, OLD_JAR, scratch, "old", True, T14.bank_scenario)),
                         ("pagenew", lambda out, jar, scratch, home: T14.page_dump(out, S, jar, scratch, "new", True, T14.bank_scenario)),
                         ("pagecmp", lambda out, jar, scratch, home: T14.page_compare(out, scratch, "old", "new"))])

if __name__ == "__main__":
    if HK.arg("--phase") == "compare":
        # 0.1.14 -> 0.1.15: neither jar ships kit art, so only manifest.json changes (the hub harness's compare expects the H3 kit add)
        HK.run(name=S.name, version=S.version, jar=S.jar, old_jar=S.old_jar, pkg=S.pkg, scratch=S.scratch, expect=S.expect, added=S.added,
               phases=[], script=S.script, removed=S.removed)
    else:
        H.run(S)
