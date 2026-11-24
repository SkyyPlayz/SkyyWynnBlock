"""Harness for SkyyBank 0.1.18 (round bank1: bank:fn:view + bank:fn:act for the new screen's Vault view; tools/bank_0_1_18_patch.py).
Build first: python tools/bank_0_1_18_patch.py && python SkyyBank/build_skyybank_0.1.18.py

    python SkyyBank/test_skyybank_0.1.18.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Every child JVM gets the pinned SkyyCore jar on its class path (SKYY_HARNESS_CP). OLD jar = the LIVE 0.1.17 (the SET pin).
  A      every class loads + initialises with -Xverify:all
  C      class compare 0.1.17 -> 0.1.18 (exactly: + BankActFn, SkyyBankPlugin setup / shutdown; BankPanelFn / BankPage / BankStore untouched)
  S      static: the patch re-runs to identical bytes; one class, no command / system; the page id unchanged
  X      exec (EXECUTES every new path; stand-in purses + profile keys = test_skyybank_0.1.9.World):
         VIEW   every line + field against the page's own statics and bank:fn:panel; locked; levels off; no SkyyCoins; top level
         ACT    deposit / withdraw / depall / wdall / upgrade / amount / refresh / state with every '+' / '-' / '=' answer; a used token;
                an older view's token; a wrong profile key; a profile switch (key and epoch); the shown purse / bank / level / price changed;
                null-safety (every malformed call); the shutdown flag; the catch path
         RACE   8 threads x one token = exactly one move; 6 threads x view + random op = no coin created or lost (purse + bank + spent)
         REG    register / unregister: only OUR objects removed, CLOSED set
  LIVE   START TWICE on a scratch COPY of the live NewBetaTest Skyy_SkyyBank: BankMig, BankMig2, BankConfig.load, every account read +
         bank:fn:view for every owner - nothing written by either start, every balance read the same as the REAL 0.1.17
  AA     engine-access audit
Exit code 1 on any failure.
"""
import os, sys, random, threading, subprocess, importlib.util, shutil, zipfile, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.1.18"
PKG = "com.skyy.bank."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyBank-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(os.path.join(HERE, "SkyyBank-0.1.17.jar"))
GEN = os.path.join(HERE, "build_skyybank_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyybank_0.1.17.py")
PATCH = os.path.join(ROOT, "tools", "bank_0_1_18_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "bank1", "bank")))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyBank")
COSTS = [25000, 75000, 150000, 300000, 600000, 1000000, 1500000, 2500000, 4000000]


def tmod(fn, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


T9 = tmod("test_skyybank_0.1.9.py", "tb0109_for18")
T9.OLD_JAR = OLD_JAR
CORE_JAR = B.core_jar()
os.environ["SKYY_HARNESS_CP"] = CORE_JAR
EXPECT = {
    "SkyyBankPlugin": ["~m setup", "~m shutdown"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read().replace("\r\n", "\n")
    o = open(GEN_OLD, encoding="utf8", newline="").read().replace("\r\n", "\n")
    K.check(g.startswith('"""SkyyBank 0.1.18 - build script') and g.count('VERSION = "0.1.18"\n') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.check(g.count("pool.makeClass(") == o.count("pool.makeClass(") + 1, "S one class added (BankActFn)")
    a = g[g.index("public static String act(String op, java.util.UUID u"):]
    a = a[:a.index('}""")')]
    K.check(a.index("TOK.remove(us, rec)") < a.index("BankStore.upgrade(u, k, rec[2], ex)") and a.index("TOK.remove(us, rec)") < a.index("BankCmd.move(u, dep,"),
            "S the token is used up (atomically) before any coin moves")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    m = re.search(r'BANK_PAGE_CHECKED = "([0-9a-f]{12})"', g)
    data = zipfile.ZipFile(JAR).read("com/skyy/bank/SkyyBankPlugin.class")
    K.check(m is not None and m.group(1) == "250c80711aad" and ("page " + m.group(1)).encode() in data, "S the page id = 0.1.17's checked page (BankPage unchanged)")
    K.check(b"bank:fn:view / bank:fn:act" in data, "S the ready line names bank:fn:view / bank:fn:act")
    K.save()


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    W = T9.World()
    Bool, Int, Long = JClass("java.lang.Boolean"), JClass("java.lang.Integer"), JClass("java.lang.Long")
    home = os.path.join(scratch, "x")
    N = T9.Bank(jar, home)
    S, C = N.S, N.C
    J = lambda n: JClass(PKG + n, loader=N.L)
    S.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyBank")
    C.load()
    A, BP, PG, CMD = J("BankActFn"), J("BankPanelFn"), J("BankPage"), J("BankCmd")
    K.eq(int(A.register()), 1, "REG register puts both")
    K.eq(int(BP.register()), 1, "REG the panel Functions too (unchanged)")
    V, X = W.BR.get("bank:fn:view"), W.BR.get("bank:fn:act")
    K.check(V is not None and X is not None and not bool(A.CLOSED), "REG bank:fn:view + bank:fn:act on the bridge, CLOSED off")

    def arr(xs):
        a = JClass("java.lang.reflect.Array").newInstance(JClass("java.lang.Object"), len(xs))
        for i, x in enumerate(xs):
            a[i] = x
        return a

    def view(u):
        t = str(V.apply(u))
        d = {"_": t}
        for ln in t.split("\n"):
            tag, _s, rest = ln.partition("|")
            d[tag] = rest
        d["H"] = d.get("h", "").split("|")
        return d

    def act(op, u, v, arg=None, pk=None, tok=None):
        return str(X.apply(arr([op, u, v["H"][1] if tok is None else tok, v["H"][2] if pk is None else pk, arg])))

    # ---------------- VIEW
    u = W.u(1)
    k = str(u)
    T9.write_acc(home, k, 10000)
    W.PURSE["new"][k] = 200000
    purse = lambda kk=k: W.PURSE["new"].get(kk, 0)
    bank = lambda kk=k: int(S.getKey(kk))
    v = view(u)
    H = v["H"]
    K.eq(len(H), 17, "VIEW h has 18 fields (h + 17)")
    K.eq(H[0:2] + H[2:3], ["ok", H[1], k], "VIEW state ok, the token, the profile key")
    K.check(re.match(r"^[0-9a-f]+$", H[1]) is not None, "VIEW the token is hex: %s" % H[1])
    K.eq([int(x) for x in H[3:15]], [1, 1, 200000, 10000, 1, 1, 10, 1, 25000, 50000, 40000, 1 if C.on() else 0],
         "VIEW readable coins purse bank levelsOn level max canUpgrade nextCost cap room interestOn")
    K.eq(int(H[15]), int(S.nextGain(u)), "VIEW gain = BankStore.nextGain")
    K.check(int(H[16]) >= 0 if C.on() else int(H[16]) == -1, "VIEW nextMs %s" % H[16])
    pan = W.BR.get("bank:fn:panel").apply(u)
    K.eq(v["f"], "200,000|10,000", "VIEW f = the page's numbers")
    K.eq(v["s"], str(PG.subLv(u)), "VIEW s = BankPage.subLv")
    K.eq(v["l"], str(S.levelLine(k)), "VIEW l = BankStore.levelLine")
    K.eq(v["r"], str(pan[4]), "VIEW r = the panel's rate line (BankPage.rateTextLv)")
    K.eq(v["n"], str(pan[5]), "VIEW n = the panel's next line (Refresh hint cut)")
    K.eq(v["g"].split("|", 1)[1], str(pan[6]), "VIEW g text = the panel's payout line (BankPage.gainText)")
    K.check(v["g"].split("|", 1)[0] in ("pay", "info"), "VIEW g kind %s" % v["g"])
    K.check("k" not in v, "VIEW no lock line when unlocked")
    K.eq(str(V.apply(k)).split("\n")[0].split("|")[4:9], ["1", "1", "200000", "10000", "1"], "VIEW apply(String uuid) works too")
    # a payout due -> kind pay; interest off -> nextMs -1
    T9.write_acc(home, str(W.u(2)), 40000)
    v2 = view(W.u(2))
    K.check(v2["g"].startswith("pay|Your next payout: +") if C.on() else True, "VIEW a balance that earns: kind pay (%s)" % v2["g"][:50])
    # ---------------- ACT: deposit / withdraw / the token
    v = view(u)
    r = act("deposit", u, v, "5000")
    K.check(r.startswith("+Deposited 5000 coins") and purse() == 195000 and bank() == 15000, "ACT deposit 5000: %s" % r)
    r = act("deposit", u, v, "5000")
    K.check(r == "=That click was for an older copy of this page, so nothing was moved. The page is up to date now - click again if you meant it." and bank() == 15000, "ACT the same token again (double click): nothing (%s)" % r)
    v = view(u)
    r = act("deposit", u, v, "")
    K.eq(r, "=Type an amount in the box first (500, 2k, 1.5m or all), then click Deposit.", "ACT deposit with an empty box")
    r = act("deposit", u, v, "1k")
    K.check(r.startswith("+Deposited 1000") and bank() == 16000, "ACT ... the token stayed alive: 1k goes in (%s)" % r)
    v = view(u)
    K.eq(act("withdraw", u, v, "  "), "=Type an amount in the box first (500, 2k, 1.5m or all), then click Withdraw.", "ACT withdraw with an empty box")
    r = act("withdraw", u, v, "2000")
    K.check(r.startswith("+Withdrew 2000") and bank() == 14000 and purse() == 196000, "ACT withdraw 2000: %s" % r)
    v = view(u)
    r = act("withdraw", u, v, "abc")
    K.check(r == "-That is not a number. Use e.g. 500, 2k, 1.5m or all." and bank() == 14000, "ACT a bad amount (the page's line): %s" % r)
    v = view(u)
    r = act("deposit", u, v, "12345678901234567890")
    K.check(bank() == 14000 and r.startswith("-"), "ACT a 20-digit amount is cut at 16 like the page's box -> refused, nothing moved (%s)" % r)
    v = view(u)
    r = act("withdraw", u, v, "999999")
    K.check(r.startswith("-Not enough coins in the bank (14000)") and bank() == 14000, "ACT withdraw too much: %s" % r)
    v = view(u)
    r = act("deposit", u, v, "100k")
    K.check(r.startswith("-Your bank has room for only 36,000 more coins") and bank() == 14000 and purse() == 196000, "ACT past the cap (the page's room line): %s" % r)
    K.eq(act("amount", u, v, ""), "=Type an amount (500, 2k, 1.5m or all), then click Deposit or Withdraw.", "ACT amount (empty) = the page's Enter note")
    K.eq(act("amount", u, v, "5k"), "=Click Deposit or Withdraw to move 5k coins. Enter alone never moves coins.", "ACT amount 5k = the page's Enter note")
    K.eq(act("refresh", u, v), "", "ACT refresh answers ''")
    st = act("state", u, v)
    K.check(st.startswith("h|ok|") and st.split("\n")[0].split("|")[2] != v["H"][1], "ACT state = a new view (new token)")
    r = act("deposit", u, v, "1000")
    K.check(r.startswith("=That click was for an older copy") and bank() == 14000, "ACT an OLDER view's token (a newer view was read): nothing (%s)" % r)
    v = view(u)
    v_new = view(u)
    r = act("DEPOSIT", u, v, "1000")
    K.check(r.startswith("=That click was for an older copy") and bank() == 14000, "ACT two views: the first one's token is dead")
    r = act("DEPOSIT", u, v_new, "1000")
    K.check(r.startswith("+Deposited 1000") and bank() == 15000, "ACT ... the newest works (op in capitals too): %s" % r)
    # ---------------- depall / wdall + the shown values
    v = view(u)
    W.PURSE["new"][k] += 7                      # a coin pickup after the view
    r = act("depall", u, v)
    K.check(r == "=Your purse changed since you looked (195,007 coins now) - look again. Nothing was moved." and bank() == 15000, "ACT depall after the purse changed: nothing (%s)" % r)
    t0 = purse() + bank()
    v = view(u)
    r = act("depall", u, v)
    K.check(r.startswith("+Deposited 35000 coins - the bank is full now") and bank() == 50000 and purse() + bank() == t0, "ACT depall fills the bank to the cap, the rest in the purse: %s" % r)
    v = view(u)
    r = act("depall", u, v)
    K.check(r.startswith("-Your bank is full: 50,000 of 50,000 coins (Bank Lv 1)") and bank() == 50000, "ACT depall on a full bank: %s" % r)
    v = view(u)
    S.creditK(k, 3)                             # a payout after the view
    r = act("wdall", u, v)
    K.check(r == "=Your bank changed since you looked (50,003 coins now) - look again. Nothing was moved." and bank() == 50003, "ACT wdall after the bank changed: nothing (%s)" % r)
    v = view(u)
    r = act("wdall", u, v)
    K.check(r.startswith("+Withdrew 50003") and bank() == 0 and purse() + bank() == t0 + 3, "ACT wdall: %s" % r)
    v = view(u)
    K.eq(act("wdall", u, v), "-Nothing to withdraw.", "ACT wdall on an empty bank")
    # ---------------- upgrade
    v = view(u)
    r = act("upgrade", u, v)
    K.check(r.startswith("-Bank Lv 2 costs 25,000 coins from your bank - it holds 0") and int(S.levelOf(k)) == 1, "ACT upgrade too poor: %s" % r)
    K.check(act("upgrade", u, v).startswith("=That click was for an older copy of this page, so nothing was charged."), "ACT ... the token was used: older copy (charged)")
    v = view(u)
    act("deposit", u, v, "30000")
    v = view(u)
    r = act("upgrade", u, v)
    K.check(r.startswith("+Bank upgraded to Lv 2 for 25,000 coins") and int(S.levelOf(k)) == 2 and bank() == 5000, "ACT upgrade Lv 1 -> 2: %s" % r)
    r = act("upgrade", u, v)
    K.check(r.startswith("=That click was for an older copy") and int(S.levelOf(k)) == 2 and bank() == 5000, "ACT the same upgrade press again: nothing")
    v = view(u)
    K.eq([int(x) for x in v["H"][7:14]], [1, 2, 10, 1, 75000, 100000, 95000], "VIEW Lv 2: level / max / can / cost / cap / room")
    S.creditK(k, 200000)
    v = view(u)
    S.LVL.put(k, Int.valueOf(3))                # the level changed after the view (another menu / the chat command)
    r = act("upgrade", u, v)
    K.check(r.startswith("=Your bank is already Lv 3 - nothing was charged.") and bank() == 205000, "ACT upgrade after the level changed: nothing (%s)" % r)
    S.LVL.put(k, Int.valueOf(2))
    v = view(u)
    C.LV_COST = "25000,99999,150000"
    r = act("upgrade", u, v)
    K.check(r == "=The upgrade price changed since you looked (Bank Lv 3 now costs 99,999 coins) - look again. Nothing was charged." and bank() == 205000 and int(S.levelOf(k)) == 2, "ACT the price changed after the view: nothing (%s)" % r)
    C.LV_COST = ",".join(str(x) for x in COSTS)
    r = act("upgrade", u, v)
    K.check(r.startswith("+Bank upgraded to Lv 3 for 75,000") and bank() == 130000, "ACT ... the price back as shown: the same token works (%s)" % r)
    S.LVL.put(k, Int.valueOf(10))
    v = view(u)
    K.eq([int(x) for x in v["H"][8:13]], [10, 10, 0, -1, 10000000], "VIEW top level: can 0, cost -1")
    K.check(act("upgrade", u, v).startswith("=Your bank is at the top level (Lv 10)") and bank() == 130000, "ACT upgrade at the top level: nothing")
    S.LVL.put(k, Int.valueOf(3))
    # levels off
    C.LV_ON = False
    v = view(u)
    K.eq([int(x) for x in v["H"][7:14]], [0, 0, 0, 0, -1, -1, -1], "VIEW levels off: levelsOn 0, level 0, max 0, no cost / cap / room")
    K.check("l" not in v and v["s"] == str(PG.subText(u)), "VIEW levels off: no l line, s = the 0.1.16 line")
    K.check(act("upgrade", u, v).startswith("=Bank levels are switched off on this server") and bank() == 130000, "ACT upgrade while levels are off: nothing")
    v = view(u)
    K.check(act("deposit", u, v, "150000").startswith("+Deposited 150000") and bank() == 280000, "ACT levels off: no cap")
    v = view(u)
    act("withdraw", u, v, "150000")
    C.LV_ON = True
    # ---------------- profile checks
    v = view(u)
    r = act("deposit", u, v, "1000", pk=k + "-p9")
    K.check(r == "=Your profile changed after this page opened, so nothing was moved. The page now shows your current profile - click again." and bank() == 130000, "ACT a wrong profile key: nothing (%s)" % r)
    r = act("upgrade", u, v, pk="")
    K.check(r.startswith("=Your profile changed after this page opened, so nothing was charged.") and int(S.levelOf(k)) == 3, "ACT upgrade with a wrong profile key: nothing (charged)")
    W.PROF[k] = 2
    r = act("deposit", u, v, "1000")
    K.check(r.startswith("=Your profile changed") and bank() == 130000 and W.PURSE["new"].get(k + "-p2", 0) == 0, "ACT a profile switch after the view: nothing (%s)" % r)
    W.PROF[k] = 1
    W.BR.put("profile:epoch:" + k, "e1")
    v = view(u)
    W.BR.put("profile:epoch:" + k, "e2")       # A -> B -> A: the same key, a new epoch
    r = act("withdraw", u, v, "1000")
    K.check(r.startswith("=Your profile changed") and bank() == 130000, "ACT a new profile epoch (A -> B -> A) after the view: nothing")
    v = view(u)
    K.check(act("withdraw", u, v, "1000").startswith("+Withdrew 1000") and bank() == 129000, "ACT ... a view on the new epoch works")
    W.BR.remove("profile:epoch:" + k)
    # a second profile has its own bank + token record
    W.PROF[k] = 2
    W.PURSE["new"][k + "-p2"] = 5000
    vp = view(u)
    K.check(vp["H"][2] == k + "-p2" and int(vp["H"][6]) == 0 and int(vp["H"][8]) == 1, "VIEW profile 2: its own key, bank 0, Lv 1")
    K.check(act("deposit", u, vp, "2k").startswith("+Deposited 2000") and bank(k + "-p2") == 2000 and bank() == 129000, "ACT profile 2's deposit lands on profile 2")
    W.PROF[k] = 1
    # ---------------- locked
    @JImplements("java.util.function.Function")
    class No:
        @JOverride
        def apply(self, x):
            return Bool.FALSE
    v = view(u)
    W.BR.put("bank:fn:unlocked", No())
    vl = view(u)
    K.eq(vl["_"], "h|locked|-|-|0|0|-1|-1|0|0|0|0|-1|-1|-1|0|0|-1\nk|" + str(J("BankActFn").LOCKTXT), "VIEW locked: only h + k")
    K.check(str(A.LOCKTXT).startswith("Your bank is still locked"), "VIEW the lock text is the panel's")
    K.eq(act("depall", u, v), "-Your bank is locked - nothing was moved.", "ACT locked: refused")
    W.BR.remove("bank:fn:unlocked")
    K.check(act("deposit", u, v, "1").startswith("=That click was for an older copy"), "ACT the locked view dropped the old token")
    # ---------------- unreadable account / no SkyyCoins
    u3 = W.u(3)
    k3 = str(u3)
    os.makedirs(os.path.join(home, "accounts", k3 + ".properties"), exist_ok=True)   # a folder where the file should be: unreadable
    W.PURSE["new"][k3] = 900
    v3 = view(u3)
    K.check(v3["H"][3] == "0" and v3["H"][6] == "-1" and v3["H"][13] == "-1" and v3["f"] == "900|unreadable" and v3["g"].startswith("bad|Your bank account cannot be read"),
            "VIEW an unreadable account: readable 0, bank -1, room -1, kind bad (%s | %s)" % (v3["h"], v3["g"][:40]))
    r = act("wdall", u3, v3)
    K.check(r.startswith("-Your bank account file cannot be read right now") and W.PURSE["new"][k3] == 900, "ACT wdall on an unreadable account: the page's line (%s)" % r)
    shutil.rmtree(os.path.join(home, "accounts", k3 + ".properties"))
    W.BR.remove("coins:fn:get")
    W.BR.remove("coins:fn:take")
    W.BR.remove("coins:fn:add")
    v = view(u)
    K.check(v["H"][4] == "0" and v["H"][5] == "-1" and v["f"].startswith("no SkyyCoins|"), "VIEW no SkyyCoins: coins 0, purse -1 (%s)" % v["f"])
    r = act("depall", u, v)
    K.eq(r, "-SkyyCoins is not loaded, the bank cannot move coins.", "ACT depall without SkyyCoins: the page's line")
    W.on()
    # ---------------- null-safety
    K.eq(str(V.apply(None)), "-Unknown player.", "NULL view(null)")
    K.eq(str(V.apply("garbage")), "-Unknown player.", "NULL view('garbage')")
    K.eq(str(V.apply(Int.valueOf(5))), "-Unknown player.", "NULL view(Integer)")
    for what, a in (("null", None), ("a String", "deposit"), ("an empty array", arr([])), ("one entry", arr(["deposit"])), ("a null op", arr([None, u]))):
        K.eq(str(X.apply(a)), "-Unknown bank action.", "NULL act(%s)" % what)
    K.eq(str(X.apply(arr(["deposit", "not-a-uuid", "x", "y", "1"]))), "-Unknown player.", "NULL act with a bad player")
    K.eq(str(X.apply(arr(["deposit", None, "x", "y", "1"]))), "-Unknown player.", "NULL act with a null player")
    v = view(u)
    K.eq(act("half", u, v, "1"), "-Unknown bank action.", "NULL 'half' is not a page button")
    K.eq(act("close", u, v), "-Unknown bank action.", "NULL unknown op")
    K.check(str(X.apply(arr(["deposit", u]))).startswith("=That click was for an older copy"), "NULL act without token / key: older copy")
    K.check(str(X.apply(arr(["deposit", str(u), v["H"][1], None, "5"]))).startswith("=Your profile changed"), "NULL act with a null profile key")
    K.check(str(X.apply(arr(["deposit", str(u), v["H"][1], v["H"][2]]))).startswith("=Type an amount in the box first"), "NULL act without arg (4 entries)")
    b0 = bank()
    K.check(str(X.apply(arr(["deposit", str(u), v["H"][1], v["H"][2], "5"]))).startswith("+Deposited 5") and bank() == b0 + 5, "ACT the player as a uuid String works")
    # the catch path: a broken token record (cannot happen from view) -> the page's 'went wrong' line, nothing moved
    v = view(u)
    rec = A.TOK.get(k)
    bad = arr([rec[0], rec[1], rec[2], "not an Integer", rec[4], rec[5], rec[6]])
    A.TOK.put(k, bad)
    b0 = bank()
    r = act("deposit", u, v, "5")
    K.check(r == "-Something went wrong - check your purse and bank above. The server log has the details." and bank() == b0, "ACT the catch path: %s" % r)
    # ---------------- CLOSED
    v = view(u)
    A.CLOSED = True
    K.eq(str(V.apply(u)), "-The bank is shutting down - try again in a moment.", "CLOSED view")
    K.eq(act("deposit", u, v, "5"), "-The bank is shutting down - nothing was moved.", "CLOSED act")
    K.eq(str(A.act("deposit", u, v["H"][1], v["H"][2], "5")), "-The bank is shutting down - nothing was moved.", "CLOSED act() itself")
    A.CLOSED = False
    # ---------------- RACE: one token, 8 threads
    u5 = W.u(5)
    k5 = str(u5)
    T9.write_acc(home, k5, 0)
    W.PURSE["new"][k5] = 30000
    v5 = view(u5)
    ths = [T9.run_bg(lambda: act("depall", u5, v5)) for _i in range(8)]
    rs = []
    for th, box in ths:
        th.join(30)
        rs.append(box.get("r") or box.get("e") or "")
    K.check(sum(1 for x in rs if x.startswith("+")) == 1 and all(x.startswith("+") or x.startswith("=") for x in rs) and bank(k5) == 30000 and purse(k5) == 0,
            "RACE 8 threads x one depall token: exactly one move (bank %d, purse %d, %s)" % (bank(k5), purse(k5), sorted(set(x[:30] for x in rs))))
    S.LVL.put(k5, Int.valueOf(1))
    T9.write_acc(home, k5, 60000)
    S.LOADED.remove(k5)
    S.BAL.remove(k5)
    S.LVL.remove(k5)
    v5 = view(u5)
    ths = [T9.run_bg(lambda: act("upgrade", u5, v5)) for _i in range(8)]
    rs = []
    for th, box in ths:
        th.join(30)
        rs.append(box.get("r") or "")
    K.check(sum(1 for x in rs if x.startswith("+")) == 1 and int(S.levelOf(k5)) == 2 and bank(k5) == 35000, "RACE 8 threads x one upgrade token: exactly one level (Lv %d, bank %d)" % (int(S.levelOf(k5)), bank(k5)))
    # 6 threads x (view + a random op): purse + bank + spent on levels = the start
    u6 = W.u(6)
    k6 = str(u6)
    T9.write_acc(home, k6, 20000)
    W.PURSE["new"][k6] = 3000000
    start = 3020000
    errs = []

    def worker(seed):
        rr = random.Random(seed)
        for _j in range(50):
            vv = view(u6)
            op = rr.choice(["deposit", "withdraw", "depall", "wdall", "upgrade", "deposit", "withdraw"])
            amt = rr.choice(["500", "2k", "15k", "1.5m", "all", ""])
            r_ = act(op, u6, vv, amt)
            if not (r_ == "" or r_[0] in "+-="):
                errs.append(r_)
            if rr.random() < 0.3:
                act(op, u6, vv, amt)            # a double click with the used token
    ths = [T9.run_bg(lambda s_=s_: worker(s_)) for s_ in range(6)]
    for th, box in ths:
        th.join(180)
        if "e" in box:
            errs.append(box["e"])
    lv6 = int(S.levelOf(k6))
    spent = sum(COSTS[:lv6 - 1])
    tot = bank(k6) + purse(k6) + spent
    K.check(not errs and tot == start and bank(k6) <= int(S.capK(k6)) + 0, "RACE 6 threads x 50 views + random ops (+ double clicks): purse + bank + spent = %d (start %d), Lv %d, bank %d (%s)" % (tot, start, lv6, bank(k6), errs[:2]))
    acc6 = open(os.path.join(home, "accounts", k6 + ".properties"), encoding="latin-1").read()
    K.check(("balance=%d" % bank(k6)) in acc6, "RACE the file holds the final balance")
    # ---------------- the old ops still work (unchanged class; one call each)
    pan = W.BR.get("bank:fn:panel").apply(u)
    r = str(W.BR.get("bank:fn:move").apply(arr([u, "deposit", "5", pan[8], pan[9]])))
    K.check(len(pan) == 13 and r.startswith("+Deposited 5"), "OLD bank:fn:panel / bank:fn:move unchanged: %s" % r)
    K.eq(int(W.BR.get("bank:fn:level").apply(u)), 3, "OLD bank:fn:level")
    # ---------------- REG
    @JImplements("java.util.function.Function")
    class Other:
        @JOverride
        def apply(self, x):
            return None
    oth = Other()
    W.BR.put("bank:fn:view", oth)
    A.unregister()
    K.check(W.BR.get("bank:fn:view") is not None and W.BR.get("bank:fn:act") is None and bool(A.CLOSED) and A.TOK.size() == 0,
            "REG unregister: another mod's bank:fn:view kept, ours removed, CLOSED set, tokens dropped")
    W.BR.remove("bank:fn:view")
    A.register()
    K.check(not bool(A.CLOSED) and W.BR.get("bank:fn:view") is not None, "REG register again: CLOSED off")
    A.unregister()
    BP.unregister()
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    W = T9.World()
    P = JClass("java.nio.file.Paths")
    dold = os.path.join(os.path.dirname(home), "liveold", "Skyy_SkyyBank")
    shutil.copytree(home, dold)
    res = {}
    for start in (1, 2):
        for tag, j, d in (("old", OLD_JAR, dold), ("new", jar, home)):
            b0 = HK.tree_hash(d)
            Jb = T9.Bank(j, d)
            Jb.S.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyBank")
            JClass(PKG + "BankMig", loader=Jb.L).run(P.get(d))
            JClass(PKG + "BankMig2", loader=Jb.L).run(P.get(d))
            Jb.C.load()
            ks = sorted(str(k) for k in Jb.S.allAccounts())
            bals = dict((k, [int(Jb.S.getKey(k)), bool(Jb.S.ready(k))]) for k in ks)
            views = []
            if tag == "new":
                A = JClass(PKG + "BankActFn", loader=Jb.L)
                for k in ks:
                    o = Jb.S.owner(k)
                    if o is not None:
                        views.append(str(A.view(o)).split("\n")[0])
                K.notes.append("LIVE start %d views: %s" % (start, "; ".join(x[:60] for x in views)))
                K.check(all(x.startswith("h|ok|") for x in views) and len(views) >= 1, "LIVE start %d: bank:fn:view answers for every owner (%d)" % (start, len(views)))
            a0 = HK.tree_hash(d)
            res[(start, tag)] = [sorted(k for k in set(b0) | set(a0) if b0.get(k) != a0.get(k)), bals]
        K.eq(res[(start, "new")][1], res[(start, "old")][1], "LIVE start %d: every account reads the same balance as the REAL 0.1.17 (%d accounts)" % (start, len(res[(start, "new")][1])))
        K.eq(res[(start, "new")][0], res[(start, "old")][0], "LIVE start %d: 0.1.18 (+ the views) changes exactly the files 0.1.17 changes (%s)" % (start, res[(start, "old")][0]))
    K.eq(res[(2, "new")][0], [], "LIVE the second start changes nothing")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyBank", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=["BankActFn"],
           phases=[("static", run_static), ("exec", run_exec), ("live", run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyBank"))
