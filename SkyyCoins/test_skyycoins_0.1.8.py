"""Harness for SkyyCoins 0.1.8 (econ38: SAME-ACCOUNT TRANSFERS BLOCKED - the Server Setup switch + coins:fn:sameacct + /pay;
tools/coins_0_1_8_patch.py).
Build first: python tools/coins_0_1_8_patch.py && python SkyyCoins/build_skyycoins_0.1.8.py

    python SkyyCoins/test_skyycoins_0.1.8.py --dir <empty folder inside tools/dev/scratch/> [--keep]

Phases (each a fresh child JVM, the game's JRE, -Xverify:all, TEMP / TMP in scratch; tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.1.7 -> 0.1.8: exactly the listed members differ (+ CoinXfer and the 7 config kit classes)
  T  EXECUTED: CoinXfer.acct (UUID, <uuid>, <uuid>-p2, upper case, bad keys / paths / null), same, blocked (switch ON: own profiles TRUE,
     another player FALSE; switch OFF: FALSE), REFUSED counter; the bridge function coins:fn:sameacct through the REAL CoinFn("sameacct")
     (UUID / key mixes, bad arguments = null, never throws); load(): no file -> the default file written (exact text) and ON; a file
     saying false / off / 0 -> OFF; a bad word -> ON + one WARN; an unreadable file (a folder) -> unchanged + WARN; THE KIT: CfgPub.start
     publishes config:def:SkyyCoins (1 row blockSameAccount, bool, default true, live + danger, category Transfers), config:fn:SkyyCoins
     get = true; switching OFF without confirm asks (confirm), with confirm -> ok, CoinXfer.BLOCK_SAME false at once, the file says
     blockSameAccount=false after the kit's save, the change log has the line; a hand edit back to true + the kit's reload op -> ON;
     /pay (static): the self check, then CoinXfer.blocked on the two profile keys BEFORE CoinStore.transfer; setup publishes
     coins:fn:sameacct and starts the kit after CoinXfer.load; shutdown flushes the kit and removes the key
  0.1.7's phases on the 0.1.8 jar: RB rebirth participant, X exec, K crash at every flush step, KK kill the writer, R rollback +
     identity, S stress, F + G fix rounds, D start twice on a scratch COPY of the live Skyy_SkyyCoins
  DX live    the 0.1.8 start on the live copy TWICE (CoinXfer.load + the kit): the first writes ONLY transfers.properties (+ the kit's
     own empty history / log, if any) and reads ON; the second changes nothing; no balance file changes
  AA engine-access audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW

VERSION = "0.1.8"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyCoins-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyCoins-0.1.7.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "econ38", "coins")))
PKG = "com.skyy.coins."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyCoins")

EXPECT = {
    "CoinFn": ["~m apply"],
    "PayCmd": ["~m execute"],
    "SkyyCoinsPlugin": ["~m setup", "~m shutdown"],
}
ADDED = ["CoinXfer", "CfgRows", "CfgLog", "CfgHist", "CfgSaveTask", "CfgFile", "CfgFn", "CfgPub"]


def tmod(fn, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


T17 = tmod("test_skyycoins_0.1.7.py", "tc017")
T16 = T17.T16
uu = T16.uu
XFER_TEXT = ("# SkyyCoins - coin moves between profiles. Change it in game: SkyWynn Menu -> Server Setup -> Coins, or edit here and Reload there.\n"
             "# blockSameAccount = true (default): coins never move between the profiles of ONE player (/pay, Auction House buys of a listing\n"
             "# your other profile made, and every mod that asks SkyyCoins). false = allowed. Trading with other players is never affected.\n"
             "blockSameAccount=true\n")


def run_xfer(out, jar, scratch, _home):
    from jpype import JClass, JArray
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST], verify=True)
    UUID, Obj = JClass("java.util.UUID"), JClass("java.lang.Object")
    OA = lambda *xs: JArray(Obj)(list(xs))
    L = T16.loader_for(jar)
    J = lambda n: JClass(PKG + n, loader=L)
    CS, X, Fn = J("CoinStore"), J("CoinXfer"), J("CoinFn")
    CS.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyCoins")
    Paths = JClass("java.nio.file.Paths")
    P = lambda p_: Paths.get(p_, JArray(JClass("java.lang.String"))([]))
    a, b = uu(1), uu(2)
    ua, ub = UUID.fromString(a), UUID.fromString(b)
    # ---- acct / same / blocked
    K.check(str(X.acct(ua)) == a and str(X.acct(a)) == a and str(X.acct(a + "-p2")) == a and str(X.acct(a.upper() + "-p12")) == a,
            "T acct: a UUID, <uuid>, <uuid>-p2 and an upper-case key all name the player")
    K.check(all(X.acct(x) is None for x in (None, "", "x", "../" + a, a + "-p", a + "-px", a + "/x", a[:35], "zzzzzzzz-zzzz-zzzz-zzzz-zzzzzzzzzzzz", 5)),
            "T acct: bad keys / paths / non-keys are nobody")
    K.check(bool(X.same(a, a + "-p2")) and bool(X.same(ua, a + "-p3")) and not bool(X.same(a, b)) and not bool(X.same(a, None)), "T same: own profiles yes, another player no")
    K.check(bool(X.BLOCK_SAME), "T the switch defaults to ON")
    r0 = int(X.REFUSED.get())
    K.check(bool(X.blocked(a, a + "-p2")) and bool(X.blocked(ua, a)) and not bool(X.blocked(a, b)) and not bool(X.blocked(a + "-p2", b + "-p2")),
            "T blocked (ON): alt profiles of one player refused, other players allowed")
    K.eq(int(X.REFUSED.get()) - r0, 2, "T REFUSED counts the refusals")
    X.BLOCK_SAME = False
    K.check(not bool(X.blocked(a, a + "-p2")) and not bool(X.blocked(a, b)), "T blocked (OFF): everything allowed")
    X.BLOCK_SAME = True
    # ---- the bridge function through the REAL CoinFn
    f = Fn("sameacct")
    K.check(f.apply(OA(a, a + "-p2")).booleanValue() is True and f.apply(OA(ua, a + "-p2")).booleanValue() is True
            and f.apply(OA(a + "-p2", b)).booleanValue() is False and f.apply(OA(ua, ub)).booleanValue() is False,
            "T coins:fn:sameacct: TRUE for own profiles (UUID / key mixes), FALSE for another player")
    K.check(all(f.apply(x) is None for x in (None, OA(a), OA(a, "../x"), OA("x", "y"), "str", OA(None, None))), "T coins:fn:sameacct: bad arguments = null, never throws")
    X.BLOCK_SAME = False
    K.check(f.apply(OA(a, a + "-p2")).booleanValue() is False, "T coins:fn:sameacct OFF: FALSE")
    X.BLOCK_SAME = True
    # ---- load(): the default file, false words, a bad word, an unreadable file
    d = os.path.join(scratch, "xf", "Skyy_SkyyCoins")
    os.makedirs(d)
    fp = os.path.join(d, "transfers.properties")
    X.FILE = P(fp)
    t = str(X.load())
    K.check(os.path.isfile(fp) and open(fp, encoding="latin-1").read() == XFER_TEXT and bool(X.BLOCK_SAME) and "BLOCKED" in t and not os.path.exists(fp + ".tmp"),
            "T load(): no file -> the default file written exactly (atomic, no .tmp left), ON: %s" % t)
    for word, want in (("false", False), ("OFF", False), ("0", False), ("no", False), ("true", True), ("on", True), ("1", True), ("maybe", True)):
        X.BLOCK_SAME = not want
        open(fp, "w").write("blockSameAccount=%s\n" % word)
        X.load()
        K.check(bool(X.BLOCK_SAME) == want, "T load(): blockSameAccount=%s -> %s" % (word, want))
    open(fp, "w").write("other=1\n")
    X.BLOCK_SAME = False
    X.load()
    K.check(bool(X.BLOCK_SAME), "T load(): no blockSameAccount line -> ON (the default)")
    d2 = os.path.join(scratch, "xf2")
    os.makedirs(os.path.join(d2, "transfers.properties"))
    X.FILE = P(os.path.join(d2, "transfers.properties"))
    X.BLOCK_SAME = False
    X.load()
    K.check(not bool(X.BLOCK_SAME), "T load(): an unreadable file leaves the switch as it was (WARN)")
    # ---- THE KIT: Server Setup -> Coins
    open(fp, "w").write(XFER_TEXT)
    X.FILE = P(fp)
    X.load()
    CP, CF = J("CfgPub"), J("CfgFn")
    br = CS.bridge()
    mods = os.path.join(scratch, "xf")
    CP.start(P(mods), CS.LOG)
    hdr = br.get("config:def:SkyyCoins")
    rows = list(hdr[7]) if hdr is not None else []
    K.check(hdr is not None and str(hdr[1]) == "SkyyCoins" and str(hdr[2]) == "Coins" and str(hdr[3]) == VERSION and str(hdr[4]) == "skyycoins.admin"
            and list(hdr[5]) == ["transfers"] and len(rows) == 1, "T kit: config:def:SkyyCoins (title Coins, node skyycoins.admin, 1 category, 1 row)")
    if rows:
        r = [str(x) for x in rows[0]]
        K.check(r[0] == "blockSameAccount" and r[3] == "bool" and r[4] == "true" and "live" in r[9] and "danger" in r[9] and r[2] == "transfers",
                "T kit row: blockSameAccount bool default true live,danger: %s" % r[:10])
    op = br.get("config:fn:SkyyCoins")
    K.eq(str(op.apply(OA("get", "blockSameAccount"))), "true", "T kit get = true")
    R = op.apply(OA("set", "blockSameAccount", "false", None, "console", "", "console"))
    K.check(str(R[0]) == "confirm" and bool(X.BLOCK_SAME), "T kit: switching OFF asks first (danger, confirm=off) - nothing changed: %s" % str(R[2])[:120])
    msg = str(CF.cmdSetConsole("blockSameAccount", "false"))
    K.check(not bool(X.BLOCK_SAME) and not bool(X.blocked(a, a + "-p2")), "T kit: set false (confirmed) -> OFF at once: %s" % msg[:120])
    CP.flush()
    txt = open(fp, encoding="latin-1").read()
    K.check("blockSameAccount=false" in txt and "blockSameAccount=true" not in txt, "T kit: the file says blockSameAccount=false after the save")
    logf = os.path.join(d, "config-changes.log")
    K.check(os.path.isfile(logf) and "blockSameAccount" in open(logf, encoding="latin-1").read(), "T kit: the change log has the line (Undo-able)")
    open(fp, "w").write(txt.replace("blockSameAccount=false", "blockSameAccount=true"))
    R = op.apply(OA("reload", None, "console", "console"))
    K.check(bool(X.BLOCK_SAME), "T kit: a hand edit back to true + Reload -> ON: %s" % (str(R[2])[:120] if R is not None else None))
    CP.shutdown()
    # ---- static: /pay + the plugin
    g = PW.calls(jar)
    pe = g.get("PayCmd.execute", set())
    K.check(PKG + "CoinXfer.blocked" in pe and PKG + "CoinStore.transfer" in pe, "T static: /pay asks CoinXfer.blocked and transfers")
    gen = open(os.path.join(HERE, "build_skyycoins_%s.py" % VERSION), encoding="utf8").read()
    i_self = gen.index("You can't pay yourself.")
    i_blk = gen.index("{PKG}.CoinXfer.blocked({PKG}.CoinStore.pkey(pr.getUuid()), {PKG}.CoinStore.pkey(target.getUuid()))")
    i_tr = gen.index("{PKG}.CoinStore.transfer(pr.getUuid(), target.getUuid(), amount)")
    K.check(i_self < i_blk < i_tr, "T static: /pay order = self check, the same-account switch, THEN the transfer (nothing moves when refused)")
    su, sd = g.get("SkyyCoinsPlugin.setup", set()), g.get("SkyyCoinsPlugin.shutdown", set())
    K.check(PKG + "CoinXfer.load" in su and PKG + "CfgPub.start" in su and PKG + "CfgPub.shutdown" in sd, "T static: setup loads the switch + starts the kit, shutdown flushes it")
    K.check(gen.index("{PKG}.CoinXfer.load();") < gen.index("{PKG}.CfgPub.start(") and 'bridge().put("coins:fn:sameacct", new {PKG}.CoinFn("sameacct"))' in gen
            and 'remove("coins:fn:sameacct")' in gen, "T static: the file is read before the kit starts; coins:fn:sameacct published + removed at shutdown")
    K.save()


def run_live(out, jar, scratch, home):
    """0.1.6's live phase (D), then the 0.1.8 start twice on the same live copy (DX) in the same child JVM"""
    import json
    tmp = os.path.join(scratch, "live16.json")
    T16.run_live(tmp, jar, scratch, home)
    from jpype import JClass, JArray
    prev = json.load(open(tmp))
    K = HK.Child(out)
    K.ok, K.fails, K.notes = prev["ok"], list(prev["fails"]), list(prev["notes"])
    Paths = JClass("java.nio.file.Paths")
    P = lambda p_: Paths.get(p_, JArray(JClass("java.lang.String"))([]))
    mods = os.path.dirname(home)
    h0 = HK.tree_hash(home)
    bal0 = HK.tree_hash(os.path.join(home, "balances"))
    snaps = []
    for start in (1, 2):
        L = T16.loader_for(jar)
        J = lambda n: JClass(PKG + n, loader=L)
        CS, X, CP = J("CoinStore"), J("CoinXfer"), J("CfgPub")
        CS.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyCoins")
        CS.DIR = P(os.path.join(home, "balances"))
        CS.JOURNAL = P(os.path.join(home, "balances-journal.properties"))
        CS.recover()
        J("CoinConfig").FILE = P(os.path.join(home, "config.properties"))
        J("CoinConfig").load()
        X.FILE = P(os.path.join(home, "transfers.properties"))
        X.load()
        CP.start(P(mods), CS.LOG)
        K.check(bool(X.BLOCK_SAME), "DX%d: the live copy reads the switch ON" % start)
        CP.shutdown()
        snaps.append(HK.tree_hash(home))
    new = sorted(set(snaps[0]) - set(h0))
    changed = sorted(k for k in h0 if snaps[0].get(k) != h0[k])
    K.check(new and all(n_ == "transfers.properties" or n_.startswith(("config-history", "config-changes")) for n_ in new) and not changed,
            "DX: the first 0.1.8 start adds transfers.properties (and only kit files), no existing file changes: new %s changed %s" % (new, changed))
    K.check(snaps[0] == snaps[1], "DX: the second start changes nothing")
    K.check(HK.tree_hash(os.path.join(home, "balances")) == bal0, "DX: no balance file changed")
    K.check(open(os.path.join(home, "transfers.properties"), encoding="latin-1").read() == XFER_TEXT, "DX: transfers.properties = the default text")
    K.save()


def run_rb(out, jar, scratch, home):
    return T17.run_rb(out, jar, scratch, home)


def run_exec(out, jar, scratch, home):
    return T16.run_exec(out, jar, scratch, home)


def run_crash(out, jar, scratch, home):
    return T16.run_crash(out, jar, scratch, home)


def run_killrounds(out, jar, scratch, home):
    return T16.run_killrounds(out, jar, scratch, home)


def run_killcheck(out, jar, scratch, home):
    return T16.run_killcheck(out, jar, scratch, home)


def run_identity(out, jar, scratch, home):
    return T16.run_identity(out, jar, scratch, home)


def run_stress(out, jar, scratch, home):
    return T16.run_stress(out, jar, scratch, home)


def run_fixes(out, jar, scratch, home):
    return T16.run_fixes(out, jar, scratch, home)


def run_fix2(out, jar, scratch, home):
    return T16.run_fix2(out, jar, scratch, home)


if __name__ == "__main__":
    HK.run(name="SkyyCoins", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("xfer", run_xfer), ("rb", run_rb), ("exec", run_exec), ("crash", run_crash), ("killrounds", run_killrounds),
                   ("killcheck", run_killcheck), ("identity", run_identity), ("stress", run_stress), ("fixes", run_fixes), ("fix2", run_fix2),
                   ("live", run_live)],
           script=__file__, live=(LIVE_DIR, "Skyy_SkyyCoins"))
