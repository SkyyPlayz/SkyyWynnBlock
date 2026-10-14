"""Harness for SkyyCoins 0.1.7 (REBIRTH R3: the participant rebirth:part:coins, rb.lastTx with the balance, spends wait while a rebirth
runs; tools/coins_0_1_7_patch.py).
Build first: python tools/coins_0_1_7_patch.py && python SkyyCoins/build_skyycoins_0.1.7.py

    python SkyyCoins/test_skyycoins_0.1.7.py --dir <empty folder inside tools/dev/scratch/> [--keep]

Phases (each a fresh child JVM, the game's JRE, -Xverify:all, TEMP / TMP in scratch; tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.1.6 -> 0.1.7: exactly the listed members differ (+ CoinRb)
  RB EXECUTED: rb.lastTx read (readK / installK), snapshotted with the balance (takeBatch), journaled (t.<i>), written (writeKey), replayed
     (recover / foldK; a bad t.<i> = the journal is NOT replayed, RECOVER_PENDING); A CRASH AT EVERY FLUSH STEP of a batch that holds a
     rebirth reset (rbResetK) + another purse, restarted in a FRESH class loader: the reset purse is always (old balance, no txid) or
     (new balance, the txid) - never one without the other; rbBusy (take / transfer refused, add lands; /pay says so - static);
     the participant CoinRb: every op and refusal, measure, prepare (backup, staged, stale staged file deleted / refused on a committed
     decision, last 3 backups), commit = purse now - purse at prepare (income after prepare kept), coins:<uuid> republished, FAIL_FLUSH =
     err then done, an unreadable purse = err, abort, status, a FRESH loader after the commit answers done (rb.lastTx from the file)
  0.1.6's phases on the 0.1.7 jar (no rebirth = 0.1.6 exactly): X exec, K crash at every flush step, KK kill the writer (5 rounds),
     R rollback + identity vs 0.1.5, S stress, F + G fix rounds, D start twice on a scratch COPY of the live Skyy_SkyyCoins
  AA engine-access audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW

VERSION = "0.1.7"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyCoins-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyCoins-0.1.6.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "rebirth3", "coins")))
PKG = "com.skyy.coins."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyCoins")

EXPECT = {
    # rb.lastTx with the balance (foldK / writeKey take the txid: - old + new signatures), rbBusy, rbResetK (the commit's reset)
    "CoinStore": ["+f RBTX", "+m foldK", "+m rbBusy", "+m rbResetK", "+m writeKey", "-m foldK", "-m writeKey", "~<clinit>", "~m flush0",
                  "~m installK", "~m readK", "~m recover", "~m take", "~m takeBatch", "~m transfer"],
    "PayCmd": ["~m execute"],
    "SkyyCoinsPlugin": ["~m setup", "~m shutdown"],
}
ADDED = ["CoinRb"]


def tmod(fn, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


T16 = tmod("test_skyycoins_0.1.6.py", "tc016")
uu = T16.uu


def fn_class():
    from jpype import JImplements, JOverride

    @JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def apply(self, o):
            return self.f(o)
    return Fn


def props(path):
    if not os.path.exists(path):
        return None
    out = {}
    for ln in open(path, encoding="latin-1").read().splitlines():
        if ln.startswith("#") or "=" not in ln:
            continue
        a, b = ln.split("=", 1)
        out[a.strip()] = b.strip()
    return out


def run_rb(out, jar, scratch, _home):
    from jpype import JClass, JArray
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST], verify=True)
    UUID, Long, Obj = JClass("java.util.UUID"), JClass("java.lang.Long"), JClass("java.lang.Object")
    OA = lambda *xs: JArray(Obj)(list(xs))
    Fn = fn_class()
    TX = "tx1760000000001-a1b2c3"

    # ---- rb.lastTx read / written / journaled / replayed
    d = os.path.join(scratch, "rb1")
    os.makedirs(os.path.join(d, "balances"))
    a, b = UUID.fromString(uu(1)), UUID.fromString(uu(2))
    open(os.path.join(d, "balances", uu(1) + ".properties"), "w").write("#SkyyCoins\nbalance=500\nrb.lastTx=%s\n" % TX)
    CS = T16.store_in(T16.loader_for(jar), d)
    K.eq(int(CS.get(a)), 500, "RB a purse file with rb.lastTx reads its balance")
    K.eq(str(CS.RBTX.get(uu(1))), TX, "RB readK / installK: rb.lastTx loaded")
    CS.add(a, 10)
    CS.set(b, 70)
    K.eq(int(CS.flushNow()), 2, "RB flush of 2 purses")
    K.check(props(os.path.join(d, "balances", uu(1) + ".properties")) == {"balance": "510", "rb.lastTx": TX}
            and props(os.path.join(d, "balances", uu(2) + ".properties")) == {"balance": "70"},
            "RB writeKey: rb.lastTx stays with its balance; a purse without one writes 0.1.6's file (balance only)")
    # a journal with t.<i> replays the txid; a bad t.<i> is never replayed
    jp = os.path.join(d, "balances-journal.properties")
    open(jp, "w").write("count=2\nk.0=%s\nv.0=0\nt.0=tx1760000000002-a1b2c3\nk.1=%s\nv.1=71\n" % (uu(1), uu(2)))
    CS2 = T16.store_in(T16.loader_for(jar), d)
    K.eq(int(CS2.recover()), 2, "RB recover: a journal with t.<i> replays")
    K.check(props(os.path.join(d, "balances", uu(1) + ".properties")) == {"balance": "0", "rb.lastTx": "tx1760000000002-a1b2c3"}
            and str(CS2.RBTX.get(uu(1))) == "tx1760000000002-a1b2c3" and not os.path.exists(jp), "RB foldK: the replay writes the balance WITH its txid")
    open(jp, "w").write("count=1\nk.0=%s\nv.0=5\nt.0=../evil\n" % uu(2))
    CS3 = T16.store_in(T16.loader_for(jar), d)
    K.check(int(CS3.recover()) == -1 and bool(CS3.RECOVER_PENDING) and os.path.exists(jp), "RB recover: a bad t.<i> = not replayed (RECOVER_PENDING, journal kept)")
    os.remove(jp)

    # ---- CRASH AT EVERY FLUSH STEP with a rebirth reset in the batch: (old, no tx) or (new, tx) - never split
    seen = set()
    for stop in range(1, 7):
        dd = os.path.join(scratch, "rbk%d" % stop)
        os.makedirs(os.path.join(dd, "balances"))
        open(os.path.join(dd, "balances", uu(5) + ".properties"), "w").write("#SkyyCoins\nbalance=900\n")
        open(os.path.join(dd, "balances", uu(6) + ".properties"), "w").write("#SkyyCoins\nbalance=40\n")
        S = T16.store_in(T16.loader_for(jar), dd)
        A_, B_ = UUID.fromString(uu(5)), UUID.fromString(uu(6))
        S.get(A_)
        S.get(B_)
        S.rbResetK(A_, uu(5), TX, 900)
        S.add(B_, 1)
        S.STEPS = 0
        S.STOP_AT = stop
        S.flushNow()
        S2 = T16.store_in(T16.loader_for(jar), dd)
        S2.recover()
        bal, tx_ = int(S2.get(A_)), S2.RBTX.get(uu(5))
        st = (bal, None if tx_ is None else str(tx_))
        seen.add(st)
        K.check(st in ((900, None), (0, TX)), "RBK%d: after a crash at flush step %d the reset purse is all-old or all-new: %r" % (stop, stop, st))
        K.check(int(S2.get(B_)) in (40, 41), "RBK%d: the other purse of the batch is old or new" % stop)
    K.check(seen == set([(900, None), (0, TX)]), "RBK both sides of the crash were seen: %s" % sorted(seen, key=str))

    # ---- rbBusy: spends wait, income lands
    d4 = os.path.join(scratch, "rb4")
    os.makedirs(os.path.join(d4, "balances"))
    S = T16.store_in(T16.loader_for(jar), d4)
    br = S.bridge()
    busy = {"k": None}
    br.put("rebirth:fn:busy", Fn(lambda o: JClass("java.lang.Boolean").valueOf(str(o) == busy["k"])))
    c1, c2 = UUID.fromString(uu(7)), UUID.fromString(uu(8))
    S.set(c1, 1000)
    S.set(c2, 1000)
    busy["k"] = uu(7)
    K.check(not S.take(c1, 10) and not S.transfer(c1, c2, 10) and int(S.get(c1)) == 1000, "RB rbBusy: take + transfer (the payer) refused while c1's profile is in a rebirth")
    K.check(int(S.add(c1, 5)) == 1005 and S.transfer(c2, c1, 5) and int(S.get(c1)) == 1010, "RB rbBusy: income lands (add, a transfer TO the busy profile)")
    busy["k"] = None
    K.check(S.take(c1, 10) and int(S.get(c1)) == 1000, "RB rbBusy cleared: take works again")
    br.remove("rebirth:fn:busy")
    g = PW.calls(jar)
    K.check(PKG + "CoinStore.rbBusy" in g.get("PayCmd.execute", set()) and PKG + "CoinStore.rbBusy" in g.get("CoinStore.take", set())
            and PKG + "CoinStore.rbBusy" in g.get("CoinStore.transfer", set()), "RB static: /pay, take and transfer ask rbBusy")
    su, sd = g.get("SkyyCoinsPlugin.setup", set()), g.get("SkyyCoinsPlugin.shutdown", set())
    K.check("java.util.Map.put" in su and "java.util.Map.remove" in sd, "RB static: the plugin puts / removes its keys")

    # ---- the participant
    d5 = os.path.join(scratch, "rb5", "Skyy_SkyyCoins")
    os.makedirs(os.path.join(d5, "balances"))
    L5 = T16.loader_for(jar)
    S = T16.store_in(L5, d5)
    RbC = JClass(PKG + "CoinRb", loader=L5)
    R = RbC()
    br = S.bridge()
    dec = {"v": "unknown"}
    br.put("rebirth:fn:decision", Fn(lambda o: dec["v"]))
    u = UUID.fromString(uu(9))
    k = uu(9)
    open(os.path.join(d5, "balances", k + ".properties"), "w").write("#SkyyCoins\nbalance=5000000\n")
    for bad, what in ((None, "null"), (OA("prepare"), "one element"), (OA("prepare", k, "tx1"), "bad txid"), (OA("prepare", "../x", TX), "bad key"),
                      (OA("fly", k, TX), "unknown op")):
        K.check(str(R.apply(bad)).startswith("err:"), "RB part refuses %s" % what)
    dsave = S.DIR
    S.DIR = None
    K.check(str(R.apply(OA("measure", k, TX))).startswith("err:SkyyCoins is not started"), "RB part: not started = err")
    S.DIR = dsave
    K.eq(str(R.apply(OA("measure", k, TX))), "ok:purse=5000000", "RB measure: the purse")
    K.check(not os.path.exists(os.path.join(d5, "rebirth")) and not os.path.exists(os.path.join(d5, "rebirth-backup")), "RB measure writes nothing")
    os.makedirs(os.path.join(d5, "rebirth"))
    stale = os.path.join(d5, "rebirth", k + ".rb-tx1760000000000-000001.properties")
    open(stale, "w").write("tx=tx1760000000000-000001\n")
    dec["v"] = "commit"
    K.check(str(R.apply(OA("prepare", k, TX))).startswith("err:an older rebirth"), "RB prepare refused while an older committed txid is unfinished")
    dec["v"] = "abort"
    K.eq(str(R.apply(OA("prepare", k, TX))), "ok:purse=5000000", "RB prepare")
    stg = os.path.join(d5, "rebirth", k + ".rb-" + TX + ".properties")
    K.check(os.path.exists(stg) and not os.path.exists(stale) and props(os.path.join(d5, "rebirth-backup", k, TX, k + ".properties")) == {"balance": "5000000"},
            "RB prepare: staged + backup, the stale staged file deleted")
    K.eq(str(R.apply(OA("status", k, TX))), "staged", "RB status staged")
    S.add(u, 777)   # income after prepare
    K.check(str(R.apply(OA("commit", k, "tx1760000000009-a1b2c3"))).startswith("err:no staged file"), "RB commit without a staged file = err")
    RbC.FAIL_FLUSH = 1
    r1 = str(R.apply(OA("commit", k, TX)))
    K.check(r1.startswith("err:could not save") and int(S.get(u)) == 777 and str(S.RBTX.get(k)) == TX and os.path.exists(stg),
            "RB commit whose flush fails: err, the reset in memory, staged kept: %s" % r1)
    K.eq(str(br.get("coins:" + k)), "777", "RB commit republished coins:<uuid>")
    r2 = str(R.apply(OA("commit", k, TX)))
    K.check(r2 == "done" and not os.path.exists(stg) and props(os.path.join(d5, "balances", k + ".properties")) == {"balance": "777", "rb.lastTx": TX},
            "RB the retried commit: done, purse = the income after prepare (777) WITH rb.lastTx, staged deleted")
    K.eq(str(R.apply(OA("commit", k, TX))), "done", "RB commit again = done")
    K.check(str(R.apply(OA("abort", k, TX))).startswith("err:already committed") and str(R.apply(OA("prepare", k, TX))).startswith("err:already committed"),
            "RB abort / prepare after the commit = err")
    K.eq(str(R.apply(OA("status", k, TX))), "committed", "RB status committed")
    TX2 = "tx1760000000002-a1b2c3"
    R.apply(OA("prepare", k, TX2))
    K.check(str(R.apply(OA("abort", k, TX2))) == "done" and not os.path.exists(os.path.join(d5, "rebirth", k + ".rb-" + TX2 + ".properties")), "RB abort deletes the staged file")
    K.eq(str(R.apply(OA("status", k, TX2))), "none", "RB status none")
    t2 = os.path.join(d5, "rebirth", k + ".rb-" + TX2 + ".properties.tmp")
    open(t2, "w").write("torn")
    K.check(str(R.apply(OA("abort", k, TX2))) == "done" and not os.path.exists(t2), "RB abort also deletes a staged write torn by a crash (.tmp)")
    old_tmp = os.path.join(d5, "rebirth", k + ".rb-tx1750000000000-000001.properties.tmp")
    open(old_tmp, "w").write("torn")
    R.apply(OA("prepare", k, "tx1760000000002-a1b2c4"))
    K.check(not os.path.exists(old_tmp), "RB prepare cleans an older torn staged write (.tmp)")
    R.apply(OA("abort", k, "tx1760000000002-a1b2c4"))
    for i in range(3, 8):
        R.apply(OA("prepare", k, "tx176000000000%d-a1b2c3" % i))
    K.eq(len(os.listdir(os.path.join(d5, "rebirth-backup", k))), 3, "RB backups: the last 3 kept")
    # an unreadable purse
    kb = uu(10)
    os.makedirs(os.path.join(d5, "balances", kb + ".properties"))
    K.check(str(R.apply(OA("prepare", kb, TX))).startswith("err:the purse file"), "RB prepare of an unreadable purse = err (nothing written)")
    # restart: a fresh loader answers done from the file
    L6 = T16.loader_for(jar)
    S6 = T16.store_in(L6, d5)
    K.eq(str(JClass(PKG + "CoinRb", loader=L6)().apply(OA("commit", k, TX))), "done", "RB restart: commit = done (rb.lastTx read from the file)")
    K.eq(int(RbC.APPLIED.get()), 0, "RB APPLIED: the err path did not count")
    K.save()


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


def run_live(out, jar, scratch, home):
    return T16.run_live(out, jar, scratch, home)


if __name__ == "__main__":
    HK.run(name="SkyyCoins", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("rb", run_rb), ("exec", run_exec), ("crash", run_crash), ("killrounds", run_killrounds), ("killcheck", run_killcheck),
                   ("identity", run_identity), ("stress", run_stress), ("fixes", run_fixes), ("fix2", run_fix2), ("live", run_live)],
           script=__file__, live=(LIVE_DIR, "Skyy_SkyyCoins"))
