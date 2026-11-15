"""Harness for SkyyVault 0.1.10 (round bank2: start with 1 page, more pages by bank level, Upgrade bank on the coin panel;
tools/vault_0_1_10_patch.py). Build first: python tools/vault_0_1_10_patch.py && python SkyyVault/build_skyyvault_0.1.10.py, and SkyyBank 0.1.17
(python tools/bank_0_1_17_patch.py && python SkyyBank/build_skyybank_0.1.17.py)

    python SkyyVault/test_skyyvault_0.1.10.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Every child JVM has the pinned SkyyCore + SkyyBank 0.1.17 on its class path (SKYY_HARNESS_CP), so the E2E phase runs the REAL bank code.
  A      every class loads + initialises with -Xverify:all
  C      class compare 0.1.9 -> 0.1.10 (+ VMigFree; exactly the classes / members the patch touches)
  S      static: the patch re-runs to identical bytes; one new class, no command / system; the gate sits before any coin moves
  X      exec: VCfg.load on a fresh file (freePages=1 + the marker + the two bank rows); VMigFree.update on texts (2 -> 1, CRLF / LF,
         comments kept, an owner's 3 kept, the marker = done) and .run on scratch homes (History copy, one change-log row, a second run
         changes nothing); the gate maths (pagesFor / needLv / needFor / bankGate / needText) with a stand-in bank:fn:level; no SkyyBank
         = no limit + one INFO line; buys through VStore.buy / intent with stand-in purses: pages 2-4 at Lv 1, page 5 refused BEFORE the
         purse is touched, bought after Lv 2; /vaultadmin setpages is not limited; a saved vault with pages=2 still loads 2 pages (kept);
         /vault info names the level
  E2E    the REAL SkyyBank 0.1.17 + the vault page through the engine's PageManager: the kit 1.7 page check (every b.set / binding names an
         element, Upgrade bank bound with the click token), the level line on top, Upgrade bank too poor = nothing, Lv 1 -> 2 (the same
         token again = nothing), the Buy button greyed "Page 5 needs Bank Lv 2" and its click refused (nothing charged), page 5 bought after
         the upgrade, the gate gone without SkyyBank's bank:fn:level
  LIVE   START TWICE on a scratch COPY of the live NewBetaTest Skyy_SkyyVault: the first start moves freePages 2 -> 1 (History + change
         log), the second changes nothing; no vault file touched; every live vault loads with the pages it had
  AA     engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, re, subprocess, importlib.util, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.1.10"
PKG = "com.skyy.vault."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyVault-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(os.path.join(HERE, "SkyyVault-0.1.9.jar"))
GEN = os.path.join(HERE, "build_skyyvault_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyvault_0.1.9.py")
PATCH = os.path.join(ROOT, "tools", "vault_0_1_10_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "bank2", "vault")))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyVault")
BANK_JAR = os.path.join(ROOT, "SkyyBank", "SkyyBank-0.1.17.jar")


def tmod(fn, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


T9V = tmod("test_skyyvault_0.1.9.py", "tv019_for10")
H = T9V.H
os.environ["SKYY_HARNESS_CP"] = os.pathsep.join([B.core_jar(), BANK_JAR])
EXPECT = {
    "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],   # the kit's version texts
    "SkyyVaultPlugin": ["~m setup"],
    "VBtn": ["~m row"],                         # the gold arrow names the bank level
    "VCfg": ["+f BANK_LV1", "+f BANK_PER", "~<clinit>", "~m load", "~m summary"],
    "VSessions": ["~m open2"],                  # the locked-page line names the bank level
    "VStore": ["+f NOBANK", "+m bankGate", "+m bankLevel", "+m needFor", "+m needLv", "+m needText", "+m pagesFor", "~<clinit>", "~m buy0",
               "~m infoLines", "~m intent", "~m toDoc"],   # toDoc: the version text in every saved file
    "VaultPage": ["+f bupLv", "~m bankClick", "~m build", "~m handleDataEvent"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = ["VMigFree"]


def P_(p):
    from jpype import JClass, JArray
    return JClass("java.nio.file.Paths").get(p, JArray(JClass("java.lang.String"))([]))


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read().replace("\r\n", "\n")
    o = open(GEN_OLD, encoding="utf8", newline="").read().replace("\r\n", "\n")
    K.check(g.startswith('"""SkyyVault 0.1.10 - build script') and g.count('VERSION = "0.1.10"\n') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.eq(g.count("pool.makeClass(") - o.count("pool.makeClass("), 1, "S one new class (VMigFree)")
    b0 = g[g.index("public static String buy0("):]
    K.check(b0.index("String bg = bankGate(u, next);") < b0.index('Object take = @PKG@.VCfg.bridge().get("coins:fn:take");'), "S buy0: the bank gate before any coin moves")
    it = g[g.index("public static String intent(java.util.UUID u, String name, int expect) {"):]
    K.check(it.index("String bg = bankGate(u, next);") < it.index("return buy(u, name, next);"), "S intent: the bank gate before the buy / confirm window")
    K.check(g.index("VMigFree.run(") > g.index("String cfg = @PKG@.VCfg.load();"), "S setup: VMigFree after the config load")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    m = re.search(r'VAULT_PAGE_CHECKED = "([0-9a-f]{12})"', g)
    K.check(m is not None and ("page " + m.group(1)).encode() in __import__("zipfile").ZipFile(JAR).read("com/skyy/vault/SkyyVaultPlugin.class"),
            "S the built page id = VAULT_PAGE_CHECKED %s" % (m and m.group(1)))
    K.save()


def vprep(J, home):
    from jpype import JClass
    J("VCfg").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyVault")
    J("VCfg").DIR = P_(home)
    J("VCfg").VDIR = P_(os.path.join(home, "vaults"))
    J("VCfg").FILE = P_(os.path.join(home, "config.properties"))
    J("VCfg").LOGF = P_(os.path.join(home, "vault.log"))
    J("VCfg").NAMESF = P_(os.path.join(home, "names.properties"))
    J("VStore").STOPPING = False
    J("VStore").SAVER = None


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    Long, Bool, Int = JClass("java.lang.Long"), JClass("java.lang.Boolean"), JClass("java.lang.Integer")
    BR = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", BR)
    home = os.path.join(scratch, "x", "Skyy_SkyyVault")
    os.makedirs(os.path.join(home, "vaults"), exist_ok=True)
    vprep(J, home)
    C, S, MG = J("VCfg"), J("VStore"), J("VMigFree")
    K.check(int(C.FREE_PAGES) == 1 and int(C.BANK_LV1) == 4 and int(C.BANK_PER) == 2, "X the fields: 1 free page, 4 pages at Lv 1, +2 per level")
    C.load()
    t = open(os.path.join(home, "config.properties"), encoding="utf8").read()
    K.check("\nfreePages=1\n" in t and "bankPagesLv1=4" in t and "bankPagesPerLevel=2" in t and "(SkyyVault 0.1.10)" in t, "X a fresh file: freePages=1, the bank rows, the marker")
    K.check(MG.update(t) is None, "X a fresh file needs no update")
    # VMigFree.update
    for nl in ("\r\n", "\n"):
        src = nl.join(["# SkyyVault config", "# freePages = vault pages", "freePages=2", "maxPages=10", "pagePrice=50000", ""])
        r = MG.update(src)
        K.check(r is not None and int(r[1]) == 1, "X update freePages=2 (%r): moves" % nl)
        nt = str(r[0])
        K.check(("freePages=1" + nl) in nt and nt.replace(str(MG.MARK) + nl, "").replace("freePages=1", "freePages=2") == src, "X only the marker + the value differ (%r)" % nl)
        K.check((nl == "\r\n") == ("\r\n" in nt), "X line endings kept (%r)" % nl)
    r = MG.update("freePages=3\n")
    K.check(r is not None and int(r[1]) == 0 and "freePages=3" in str(r[0]) and "freePages=3" in str(r[2]), "X an owner's freePages=3 is kept")
    K.check(MG.update("# " + str(MG.MARK_ID) + "\nfreePages=2\n") is None, "X the marker = done")
    # VMigFree.run on scratch homes (the kit's History + change log)
    for nm, body, want in (("two", "# c\r\nfreePages=2\r\nmaxPages=10\r\n", 1), ("three", "# c\nfreePages=3\nmaxPages=10\n", 3)):
        h2 = os.path.join(scratch, "m_" + nm, "Skyy_SkyyVault")
        os.makedirs(h2, exist_ok=True)
        f = os.path.join(h2, "config.properties")
        open(f, "w", encoding="utf8", newline="").write(body)
        old = open(f, "rb").read()
        vprep(J, h2)
        C.load()
        msg = str(MG.run(C.FILE))
        tt = open(f, "rb").read().decode("utf8")
        K.check(("freePages=%d" % want) in tt and int(C.FREE_PAGES) == want and ("\r\n" in body) == ("\r\n" in tt), "X run %s: freePages %d, the field follows, endings kept (%s)" % (nm, want, msg[:70]))
        hist = [open(os.path.join(r_, x), "rb").read() for r_, _d, fs in os.walk(os.path.join(h2, "config-history")) for x in fs if not x.endswith(".log")]
        K.check(old in hist, "X run %s: the old bytes are in config-history" % nm)
        lg = open(os.path.join(h2, "config-changes.log"), encoding="latin-1").read() if os.path.exists(os.path.join(h2, "config-changes.log")) else ""
        K.eq(len([l for l in lg.splitlines() if "SkyyVault 0.1.10" in l and "freePages" in l]), 1 if want == 1 else 0, "X run %s: change-log rows" % nm)
        b1 = open(f, "rb").read()
        K.check(str(MG.run(C.FILE)) == "" and open(f, "rb").read() == b1, "X run %s: a second run changes nothing" % nm)
    vprep(J, home)
    C.load()
    # the gate maths
    K.eq([int(S.pagesFor(x)) for x in (1, 2, 3, 4, 10)], [4, 6, 8, 10, 22], "X pagesFor: 4 + 2 per level")
    K.eq([int(S.needLv(x)) for x in (1, 4, 5, 6, 7, 10, 22)], [1, 1, 2, 2, 3, 4, 10], "X needLv")
    u = JClass("java.util.UUID").fromString("00000000-0000-0000-0000-0000000a0010")
    K.check(int(S.bankLevel(u)) == -1 and int(S.needFor(u, 9)) == 0 and S.bankGate(u, 9) is None and bool(S.NOBANK), "X no bank:fn:level: no limit (+ one INFO line)")
    LV = {"lv": 1}

    @JImplements("java.util.function.Function")
    class LvFn:
        @JOverride
        def apply(self, o):
            return None if LV["lv"] is None else Int.valueOf(LV["lv"])
    BR.put("bank:fn:level", LvFn())
    K.eq([int(S.needFor(u, x)) for x in (2, 4, 5, 7)], [0, 0, 2, 3], "X needFor at Lv 1")
    K.eq(str(S.bankGate(u, 5)), "-Vault page 5 needs Bank Lv 2 (your best bank: Lv 1). Upgrade the bank on the Vault tab first - nothing was charged.", "X the refusal line")
    K.eq(str(S.needText(u, 5)), "Page 5 needs Bank Lv 2", "X the Buy button text")
    C.BANK_PER = 0
    K.check(int(S.needFor(u, 5)) == -1 and "cannot be bought with any bank level" in str(S.bankGate(u, 5)), "X bankPagesPerLevel 0: page 5 never")
    C.BANK_PER = 2
    LV["lv"] = None
    K.check(S.bankGate(u, 50) is None, "X bank levels off (bank:fn:level null): no limit")
    LV["lv"] = 1
    # buys with stand-in purses
    PURSE = {"p": 1000000}

    @JImplements("java.util.function.Function")
    class Take:
        @JOverride
        def apply(self, a):
            n = int(a[1])
            if PURSE["p"] < n:
                return Bool.FALSE
            PURSE["p"] -= n
            return Bool.TRUE

    @JImplements("java.util.function.Function")
    class Add:
        @JOverride
        def apply(self, a):
            PURSE["p"] += int(a[1])
            return Long.valueOf(PURSE["p"])
    BR.put("coins:fn:take", Take())
    BR.put("coins:fn:add", Add())
    d = S.load(u)
    K.eq(int(d.unlocked), 1, "X a new player starts with 1 vault page")
    got = []
    for pg in (2, 3, 4):
        got.append(str(S.buy(u, "Tester", pg))[:30])
    K.check(int(S.load(u).unlocked) == 4 and PURSE["p"] == 1000000 - 50000 - 75000 - 100000, "X pages 2-4 bought at Lv 1 (50k + 75k + 100k): %s" % got)
    p0 = PURSE["p"]
    r = str(S.buy(u, "Tester", 5))
    K.check(r.startswith("-Vault page 5 needs Bank Lv 2") and PURSE["p"] == p0 and int(S.load(u).unlocked) == 4, "X page 5 at Lv 1: refused, nothing charged (%s)" % r)
    C.BUY_CONFIRM = 1000000000000
    r = str(S.intent(u, "Tester", 5))
    K.check(r.startswith("-Vault page 5 needs Bank Lv 2") and PURSE["p"] == p0, "X intent (gold arrow / Buy / /vault buy): the same refusal (%s)" % r)
    K.check(any("needs Bank Lv 2" in str(x) for x in S.infoLines(u, 1, False)), "X /vault info names the bank level")
    LV["lv"] = 2
    r = str(S.buy(u, "Tester", 5))
    K.check(r.startswith("+Bought vault page 5") and PURSE["p"] == p0 - 125000 and int(S.load(u).unlocked) == 5, "X page 5 after Bank Lv 2 (%s)" % r)
    r = str(S.setPages("admin", u, 9, 0))
    K.check(r.startswith("+") and int(S.load(u).unlocked) == 9, "X /vaultadmin setpages is not limited by the bank (%s)" % r)
    # a saved vault with pages=2 keeps 2 pages under freePages 1
    u2 = JClass("java.util.UUID").fromString("00000000-0000-0000-0000-0000000a0020")
    open(os.path.join(home, "vaults", str(u2) + ".json"), "w", encoding="utf8").write(json.dumps({"uuid": str(u2), "name": "Old", "pages": 2, "content": []}))
    K.eq(int(S.load(u2).unlocked), 2, "X a saved vault with 2 pages keeps both (pages already owned are kept)")
    K.save()


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
    vhome = os.path.join(scratch, "e2e_vault")
    bhome = os.path.join(scratch, "e2e_bank")
    os.makedirs(os.path.join(vhome, "vaults"), exist_ok=True)
    os.makedirs(os.path.join(bhome, "accounts"), exist_ok=True)
    T9V.prep(E, J, vhome)
    J("VCfg").load()
    J("VCfg").BUY_CONFIRM = 1000000000000
    BK("BankStore").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyBank")
    BK("BankStore").DIR = E.Paths.get(os.path.join(bhome, "accounts"))
    BK("BankConfig").FILE = E.Paths.get(os.path.join(bhome, "config.properties"))
    BK("BankConfig").STATE = E.Paths.get(os.path.join(bhome, "state.properties"))
    BK("BankWatch").STOP = False
    BK("BankWatch").EXEC = E.U.allocateInstance(E.RecEx.class_)
    BK("BankConfig").load()
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
    P = W.P
    u = P.pr.getUuid()
    PURSE[str(u)] = 500000
    E.br.put("hub:last:" + str(u), JClass("java.util.concurrent.ConcurrentHashMap")())
    K.eq(int(BK("BankPanelFn").register()), 1, "E2E SkyyBank 0.1.17 puts bank:fn:panel / move / level")
    K.eq(int(J("VaultHubOpen").register()), 1, "E2E SkyyVault puts its tab")
    J("VStore").setPages("admin", u, 4, 0)
    BK("BankCmd").openPage(P.ref, P.st, P.pr)
    E.pump(P)
    pg = P.pm.getCustomPage()
    K.check(pg is not None and str(pg.getClass().getName()) == PKG + "VaultPage", "E2E /bank opens the Vault tab")

    def build(page):
        b = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")()
        ev = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")()
        page.build(P.ref, b, ev, P.st)
        return H.cmds_of(b), H.events_of(ev)

    def sets(cm):
        o = {}
        for ty, s_, t_, d_ in cm:
            if ty == "Set":
                try:
                    o[s_] = json.loads(d_).get("0")
                except Exception:
                    o[s_] = d_
        return o
    cmds, evs = H.page_check(K, E, T9V.S, P, pg, HB, "E2E vault page (Lv 1)")
    st = sets(cmds)
    K.check("Bank Lv 1 of 10" in str(st.get("#SkyyVBSub.Text")) and "Upgrade to Lv 2" in str(st.get("#SkyyVBSub.Text")), "E2E the level line on top: %s" % st.get("#SkyyVBSub.Text"))
    K.check(any(str(pg.btok) in t and "bupgrade" in t for s_, t in evs if s_ == "#SkyyVBUpgrade"), "E2E Upgrade bank is bound with the click token")
    allm = " ".join(t for ty, s_, t, d_ in cmds if t)
    K.check("coins you carry" in allm and "lost in part when you die" not in allm, "E2E the purse caption no longer mentions a death loss")
    K.check("PAGE 5 NEEDS BANK LV 2" in allm.upper() and int(pg.offer) == 0, "E2E the Buy button reads 'Page 5 needs Bank Lv 2' (greyed, no offer)")

    def click(a, amt, tok):
        d = {"a": a, "@VBAmount": amt}
        if tok is not None:
            d["t"] = tok
        P.pm.handleLegacyCustomPageEvent(P.ref, P.st, E.CPE(E.CPT.Data, json.dumps(d)))
        E.pump(P)
        return P.pm.getCustomPage()
    bank = lambda: int(BK("BankStore").get(u))
    lv = lambda: int(BK("BankStore").levelOf(str(u)))
    p2 = click("bupgrade", "", str(pg.btok))
    K.check(str(p2.info).startswith("-Bank Lv 2 costs 25,000") and bank() == 0 and lv() == 1, "E2E Upgrade with an empty bank: nothing (%s)" % p2.info)
    p2 = click("bdep", "30000", str(p2.btok))
    tok = str(p2.btok)
    p2 = click("bupgrade", "", tok)
    K.check(str(p2.info).startswith("+Bank upgraded to Lv 2") and bank() == 5000 and lv() == 2, "E2E Upgrade: Lv 2 for 25,000 (%s)" % p2.info)
    p2 = click("bupgrade", "", tok)
    K.check("older copy" in str(p2.info) and bank() == 5000 and lv() == 2, "E2E the same token again: nothing (%s)" % p2.info)
    K.eq(int(p2.bupLv), 2, "E2E the redrawn panel knows Lv 2")
    p0 = PURSE[str(u)]
    J("VStore").LASTBUY.clear()
    # page 5 at Lv 2 (allowed up to 6): the footer Buy works
    cm3, ev3 = build(p2)
    K.eq(int(p2.offer), 5, "E2E at Lv 2 the Buy button offers page 5")
    p3 = click("buy", "", None)
    K.check(str(p3.info).startswith("+Bought vault page 5") and PURSE[str(u)] == p0 - 125000, "E2E Buy page 5 after the upgrade (%s)" % p3.info)
    # back to the gate: page 7 needs Lv 3
    J("VStore").setPages("admin", u, 6, 0)
    J("VStore").LASTBUY.clear()
    cm4, ev4 = build(p3)
    K.check("PAGE 7 NEEDS BANK LV 3" in " ".join(t for ty, s_, t, d_ in cm4 if t).upper() and int(p3.offer) == 0, "E2E page 7 shows 'needs Bank Lv 3'")
    p1 = PURSE[str(u)]
    r = str(J("VStore").intent(u, "x", 7))
    K.check(r.startswith("-Vault page 7 needs Bank Lv 3 (your best bank: Lv 2)") and PURSE[str(u)] == p1, "E2E /vault buy of page 7 at Lv 2: refused, nothing charged (%s)" % r)
    H.page_check(K, E, T9V.S, P, p3, HB, "E2E vault page (Lv 2, 6 pages)")
    # without SkyyBank's bank:fn:level: no gate
    lf = E.br.remove("bank:fn:level")
    K.check(J("VStore").bankGate(u, 7) is None, "E2E without bank:fn:level: no bank limit")
    E.br.put("bank:fn:level", lf)
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    BR = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", BR)
    cfg0 = open(os.path.join(home, "config.properties"), encoding="utf8").read()
    vd = os.path.join(home, "vaults")
    want = {}
    for f in sorted(os.listdir(vd)):
        if f.endswith(".json"):
            m = re.search(rb'"pages"\s*:\s*(\{\s*"\$numberInt"\s*:\s*"(\d+)"\s*\}|(\d+))', open(os.path.join(vd, f), "rb").read())
            want[f[:-5]] = int(m.group(2) or m.group(3)) if m else None
    h0 = HK.tree_hash(home)
    snaps, msgs = [], []
    for start in (1, 2):
        L = T9V_loader(jar)
        J = lambda n: JClass(PKG + n, loader=L)
        vprep(J, home)
        J("VCfg").load()
        msgs.append(str(J("VMigFree").run(J("VCfg").FILE)))
        J("CfgPub").start(P_(os.path.dirname(home)), J("VCfg").LOG)
        K.eq(int(J("VCfg").FREE_PAGES), 1, "LIVE start %d: 1 free page" % start)
        got = dict((k, int(J("VStore").load(JClass("java.util.UUID").fromString(k)).unlocked)) for k in want)
        K.check(all(want[k] is None or got[k] >= want[k] for k in want), "LIVE start %d: every live vault keeps its pages (saved %s, loaded %s)" % (start, want, got))
        J("CfgPub").shutdown()
        snaps.append(HK.tree_hash(home))
    new = sorted(set(snaps[0]) - set(h0))
    changed = sorted(k for k in h0 if snaps[0].get(k) != h0[k])
    K.check("config.properties" in changed and all(c in ("config.properties", "config-changes.log", os.path.join("config-history", "index.log")) for c in changed)
            and all(n.startswith(("config-history", "config-changes")) for n in new), "LIVE the first start changes only config.properties + kit history / change files: %s %s" % (changed, new))
    K.check(not [k for k in h0 if k.startswith("vaults") and snaps[0].get(k) != h0[k]], "LIVE no vault file touched")
    cfg1 = open(os.path.join(home, "config.properties"), encoding="utf8").read()
    K.check("freePages=2" in cfg0 and "\nfreePages=1" in cfg1 and cfg1.replace("freePages=1", "freePages=2").replace(str(J("VMigFree").MARK) + ("\r\n" if "\r\n" in cfg0 else "\n"), "") == cfg0, "LIVE only freePages + the marker changed")
    K.check(snaps[0] == snaps[1] and msgs[1] == "", "LIVE the second start changes nothing")
    K.notes.append("LIVE first start: %s" % msgs[0][:160])
    K.save()


def T9V_loader(jar):
    from jpype import JClass, JArray
    URL = JClass("java.net.URL")
    arr = JArray(URL)([JClass("java.io.File")(jar).toURI().toURL()])
    return JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getSystemClassLoader())


if __name__ == "__main__":
    HK.run(name="SkyyVault", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("exec", run_exec), ("e2e", run_e2e), ("live", run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyVault"))
