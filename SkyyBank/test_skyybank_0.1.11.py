"""Harness for SkyyBank 0.1.11 (REBIRTH R3: the participant rebirth:part:bank, the rate bonus on top of the brackets, the bank waits while a
rebirth runs; tools/bank_0_1_11_patch.py).
Build first: python tools/bank_0_1_11_patch.py && python SkyyBank/build_skyybank_0.1.11.py

    python SkyyBank/test_skyybank_0.1.11.py --dir <empty folder inside tools/dev/scratch/> [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.1.10 -> 0.1.11: exactly the listed members differ (+ BankRb)
  RB EXECUTED: rb.* lines read (loadKey0) and kept by every write (setKey0 - a deposit keeps them); ppmOf / ppmText / rbBonus (none, 1 %,
     above maxPrincipal, bad lines, huge numbers); THE PAYOUT: planGroup / payAll with a bonus (one profile; an account-wide group of two -
     the other profile's share is unchanged, the bonus profile gets its share + floor(min(balance, maxPrincipal) x bonus)); 3 days of
     back-pay compound with the bonus; nextGain = the paid amount; 400 random groups WITHOUT a bonus = 0.1.10's payout to the coin (both
     jars, own loaders); rbBusy: deposit / withdraw = 6 and BankCmd.move says "A rebirth is finishing ..."; the participant BankRb: every
     op and refusal, measure, prepare (backup, staged, stale cleanup / refusal, last 3 backups), commit (bank = now - prep, an interest
     payout between prepare and commit is KEPT, rb.bonus = old + bonus capped at max and never lowered, rb.hist.<n>, rb.lastTx in ONE
     write), missing rewards / no rebirth number = err, FAIL_WRITE = err with NOTHING changed then ok, done twice, abort, status, a FRESH
     loader answers done; /bank status names the bonus (static)
  N           test_skyybank_0.1.10.py's name phase on the 0.1.11 jar (the profile line)
  X, D        every 0.1.9 exec + live check carried forward (test_skyybank_0.1.9.py's run_exec / run_live, run on the 0.1.11 jar against
              0.1.8 exactly as they ran on 0.1.9 / 0.1.10)
  AA engine-access audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util, random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW


def tmod(fn, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


T9 = tmod("test_skyybank_0.1.9.py", "tb019")
T10 = tmod("test_skyybank_0.1.10.py", "tb0110")

VERSION = "0.1.11"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyBank-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyBank-0.1.10.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "rebirth3", "bank")))
PKG = "com.skyy.bank."
LIVE_DIR = T9.LIVE_DIR
DAY = 86400000
EXPECT = {
    "BankStore": ["+f RBX", "+m ppmOf", "+m ppmText", "+m rbBonus", "+m rbBonus", "+m rbBusy", "+m rbWrite0", "~<clinit>", "~m deposit", "~m loadKey0",
                  "~m nextGain", "~m planGroup", "~m setKey0", "~m withdraw",
                  "+m applyKeyRb", "+m applyKeyRb0", "~m planAll", "~m payAll"],   # fix round: plan -> commit -> apply
    "BankCmd": ["~m move", "~m status"],          # code 6 text; the bonus in /bank status
    "CfgRows": ["~m header"],                     # the version text
    "CfgFn": ["~m opExport"],                     # the version text
    "SkyyBankPlugin": ["~m setup", "~m shutdown"],
}
ADDED = ["BankRb"]


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


def run_rb(out, jar, scratch, _home):
    from jpype import JClass, JArray
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST], verify=True)
    W = T9.World()
    Obj, Str = JClass("java.lang.Object"), JClass("java.lang.String")
    OA = lambda *xs: JArray(Obj)(list(xs))
    GS = lambda *groups: JArray(Obj)([JArray(Str)(list(g)) for g in groups])
    Fn = fn_class()
    TX = "tx1760000000001-a1b2c3"
    bk = T9.Bank(jar, os.path.join(scratch, "rb", "Skyy_SkyyBank"))
    S, C = bk.S, bk.C
    C.load()
    u = W.u(1)
    k = str(u)

    # ---- rb.* lines: read + kept by every write
    T9.write_acc(bk.home, k, 1000000, "rb.bonus=1.0000\r\nrb.hist.1=5000000\r\nrb.lastTx=%s\r\n" % TX)
    K.check(int(S.getKey(k)) == 1000000 and str(S.RBX.get(k).getProperty("rb.bonus")) == "1.0000", "RB loadKey0: rb.* lines read")
    K.eq(int(S.ppmOf(S.RBX.get(k))), 10000, "RB ppmOf 1 % = 10,000 ppm")
    W.PURSE["new"][k] = 5000
    K.eq(int(S.deposit(u, 100)), 1, "RB a deposit")
    f = bk.files()[k + ".properties"]
    K.check(f.get("balance") == "1000100" and f.get("rb.bonus") == "1.0000" and f.get("rb.lastTx") == TX and f.get("rb.hist.1") == "5000000",
            "RB setKey0: a deposit keeps the rb.* lines: %s" % f)
    k2 = W.key(W.u(2))
    T9.write_acc(bk.home, k2, 300)
    S.setKey(k2, 301)
    K.check("rb." not in open(os.path.join(bk.home, "accounts", k2 + ".properties"), encoding="latin-1").read(), "RB an account without a rebirth: no rb.* line")
    P = JClass("java.util.Properties")
    pp = P()
    for v, want in (("0.25", 2500), ("0.2603", 2603), ("abc", 0), ("-1", 0), ("500", 1000000), ("0", 0)):
        pp.setProperty("rb.bonus", v)
        K.eq(int(S.ppmOf(pp)), want, "RB ppmOf(%s)" % v)
    K.check(int(S.ppmOf(None)) == 0 and [str(S.ppmText(x)) for x in (0, 2603, 10000, 30000, 5)] == ["0.0000", "0.2603", "1.0000", "3.0000", "0.0005"],
            "RB ppmText")
    mp = int(C.MAX_PRINCIPAL)
    K.check(int(S.rbBonus(k, 500)) == 5 and int(S.rbBonus(k, 0)) == 0 and int(S.rbBonus(k2, 10 ** 6)) == 0 and int(S.rbBonus(k, mp * 50)) == mp // 100
            and int(S.rbBonus(None, 5)) == 0, "RB rbBonus: 1 %% of the balance, capped at maxPrincipal (%d), none without rb.bonus" % mp)

    # ---- the payout with a bonus
    hb = os.path.join(scratch, "pay")
    b2 = T9.Bank(jar, hb)
    b2.C.load()
    b2.C.SCOPE = "account"
    ua = W.u(3)
    ka, kb = str(ua), str(ua) + "-p2"
    T9.write_acc(hb, ka, 1000000, "rb.bonus=1.0000\r\n")
    T9.write_acc(hb, kb, 1000000)
    now = int(W.Sys.currentTimeMillis())
    got = b2.S.payAll(GS([ka, kb]), now - 2 * DAY, now - DAY, DAY, 1)
    g = [int(x) for x in got[0]]
    # brackets on the 2,000,000 sum: 2 % of 1M + 1 % of 1M = 30,000 split 15,000 / 15,000; + the bonus 1 % of 1,000,000 = 10,000 on ka
    K.check(g == [25000, 15000] and int(b2.S.getKey(ka)) == 1025000 and int(b2.S.getKey(kb)) == 1015000,
            "RB payAll account-wide: the other profile's share unchanged (15,000), the bonus profile 15,000 + 10,000: %s" % g)
    T9.write_acc(hb, ka, 1000000, "rb.bonus=1.0000\r\n")
    T9.write_acc(hb, kb, 1000000)
    b2.point(hb)
    b2.S.RBX.clear()
    now2 = now + 10 * DAY
    got = b2.S.payAll(GS([ka]), now2 - 3 * DAY, now2, DAY, 3)
    ex, sim = 0, 1000000
    for _d in range(3):
        add = int(b2.C.interestOf(sim)) + min(sim, mp) * 10000 // 1000000
        ex += add
        sim += add
    K.eq(int(got[0][0]), ex, "RB 3 days back-pay compound with the bonus (the brackets + 1 %% of the balance, day by day: %d)" % ex)
    b2.S.RBX.clear()
    T9.write_acc(hb, ka, 1000000, "rb.bonus=2.5000\r\n")
    b2.point(hb)
    W.PROF[str(ua)] = 1
    ng = int(b2.S.nextGain(ua))
    b2.S.ready(kb)
    K.check(ng > 0 and ng == int(b2.S.payAll(GS(sorted([ka, kb])), now + 20 * DAY, now + 21 * DAY, DAY, 1)[0][sorted([ka, kb]).index(ka)]),
            "RB nextGain = what the payout then pays (%d)" % ng)

    # ---- fix round: maxPrincipal is ACCOUNT-wide for the bonus too (8 rebirthed profiles x maxPrincipal = the bonus on maxPrincipal once)
    K.check(int(S.rbBonus(k, 500, 500)) == 5 and int(S.rbBonus(k, mp, 4 * mp)) == mp // 400 and int(S.rbBonus(k, mp * 50, mp * 50)) == mp // 100
            and int(S.rbBonus(k, 500, 1000)) == 5 and int(S.rbBonus(k, 500, 0)) == 5 and int(S.rbBonus(k2, mp, mp)) == 0,
            "FIX rbBonus(k, bal, sum): the profile's part of min(sum, maxPrincipal) (sum <= maxPrincipal = bal)")
    hc = os.path.join(scratch, "cap")
    bc = T9.Bank(jar, hc)
    bc.C.load()
    bc.C.SCOPE = "account"
    uc = W.u(7)
    kc = sorted([str(uc)] + [str(uc) + "-p%d" % j for j in range(2, 9)])
    for kk in kc:
        T9.write_acc(hc, kk, mp, "rb.bonus=1.0000\r\n")
    now3 = now + 30 * DAY
    g = [int(x) for x in bc.S.payAll(GS(kc), now3 - 2 * DAY, now3 - DAY, DAY, 1)[0]]
    base_i = int(bc.C.interestOf(8 * mp))
    K.check(sum(g) == base_i + mp // 100, "FIX 8 profiles x %d with +1 %%: the bonus is 1 %% of maxPrincipal ONCE (%d), not 8 x: paid %d = brackets %d + %d"
            % (mp, mp // 100, sum(g), base_i, sum(g) - base_i))

    # ---- fix round: a payout planned BEFORE a rebirth's commit is not applied AFTER it (the bank was just emptied)
    Rq = JClass(PKG + "BankRb", loader=bk.L)()
    kq = str(W.u(8))
    T9.write_acc(bk.home, kq, 1000000)
    S.ready(kq)
    nowq = now + 40 * DAY
    plan = S.snapshot(GS([kq]), nowq - 2 * DAY, nowq - DAY, DAY, 1)
    addq = int(plan[0][0][0])
    TXQ = "tx1760000000010-a1b2c3"
    K.check(str(Rq.apply(OA("prepare", kq, TXQ))).startswith("ok:") and str(Rq.apply(OA("commit", kq, TXQ, JClass("java.lang.Integer")(1), "bonus=0;max=30000;bal=1000000"))) == "ok"
            and int(S.getKey(kq)) == 0, "FIX plan -> commit: the bank is 0")
    okq = bool(S.applyKeyRb(kq, addq, nowq - DAY, 0, plan[3][0][0]))
    fq = bk.files()[kq + ".properties"]
    K.check(addq > 0 and not okq and int(S.getKey(kq)) == 0 and fq.get("balance") == "0" and fq.get("paidThrough") is None,
            "FIX the stale planned share (%d) is NOT added to the emptied bank" % addq)
    plan2 = S.snapshot(GS([kq]), nowq - 2 * DAY, nowq - DAY, DAY, 1)
    K.check(bool(S.applyKeyRb(kq, int(plan2[0][0][0]), nowq - DAY, 0, plan2[3][0][0])) and int(S.getKey(kq)) == int(plan2[0][0][0]),
            "FIX a plan made after the commit is applied (control)")
    g2 = PW.calls(jar)
    K.check(PKG + "BankStore.applyKeyRb" in g2.get("BankStore.payAll", set()) and PKG + "BankStore.applyKey" not in g2.get("BankStore.payAll", set()),
            "FIX static: payAll applies through applyKeyRb")

    # ---- no bonus: 400 random groups = 0.1.10's payout to the coin
    old = T9.Bank(OLD_JAR, os.path.join(scratch, "id_old"))
    new = T9.Bank(jar, os.path.join(scratch, "id_new"))
    for J in (old, new):
        J.C.load()
    rnd = random.Random(1011)
    diff = []
    for i in range(400):
        n = rnd.randint(1, 4)
        ks = ["%s%s" % (W.u(100 + i), "" if j == 0 else "-p%d" % (j + 1)) for j in range(n)]
        bals = [rnd.choice([0, 1, 999, 50000, 1000000, 4999999, 12000000, rnd.randint(0, 20000000)]) for _ in ks]
        days = rnd.choice([1, 1, 2, 3])
        res = []
        for J in (old, new):
            for kk, bb in zip(ks, bals):
                T9.write_acc(J.home, kk, bb)
            J.point(J.home)
            r = J.S.payAll(GS(ks), now - (days + 1) * DAY, now, DAY, days)
            res.append(([int(x) for x in r[0]], [int(J.S.getKey(kk)) for kk in ks]))
        if res[0] != res[1]:
            diff.append((ks, bals, res))
    K.check(not diff, "RB 400 random groups without a bonus: 0.1.11 pays exactly what 0.1.10 pays: %s" % diff[:2])

    # ---- rbBusy: code 6 + the message
    busy = {"k": None}
    W.BR.put("rebirth:fn:busy", Fn(lambda o: JClass("java.lang.Boolean").valueOf(str(o) == busy["k"])))
    busy["k"] = k
    W.PURSE["new"][k] = 5000
    K.check(int(S.deposit(u, 10)) == 6 and int(S.withdraw(u, 10)) == 6 and int(S.getKey(k)) == 1000100 and W.PURSE["new"][k] == 5000,
            "RB rbBusy: deposit / withdraw = 6, nothing moved")
    Cmd = JClass(PKG + "BankCmd", loader=bk.L)
    K.check(str(Cmd.move(u, True, "10")).startswith("-A rebirth is finishing on this profile"), "RB BankCmd.move code 6: the message")
    busy["k"] = None
    K.eq(int(S.deposit(u, 10)), 1, "RB not busy: deposit works")
    W.BR.remove("rebirth:fn:busy")
    gr = PW.calls(jar)
    K.check(PKG + "BankStore.ppmText" in gr.get("BankCmd.status", set()) and PKG + "BankStore.rbBonus" in gr.get("BankStore.nextGain", set())
            and PKG + "BankStore.rbBonus" in gr.get("BankStore.planGroup", set()), "RB static: /bank status names the bonus; nextGain + planGroup add it")
    K.check("java.util.Map.put" in gr.get("SkyyBankPlugin.setup", set()) and "java.util.Map.remove" in gr.get("SkyyBankPlugin.shutdown", set()),
            "RB static: the plugin puts / removes rebirth:part:bank")

    # ---- the participant
    Rb = JClass(PKG + "BankRb", loader=bk.L)
    R = Rb()
    dec = {"v": "unknown"}
    W.BR.put("rebirth:fn:decision", Fn(lambda o: dec["v"]))
    up = W.u(5)
    kp = str(up)
    T9.write_acc(bk.home, kp, 20000000, "rb.bonus=2.8000\r\n")
    for bad, what in ((None, "null"), (OA("prepare"), "one element"), (OA("prepare", kp, "tx1"), "bad txid"), (OA("prepare", "../x", TX), "bad key"),
                      (OA("fly", kp, TX), "unknown op")):
        K.check(str(R.apply(bad)).startswith("err:"), "RB part refuses %s" % what)
    K.eq(str(R.apply(OA("measure", kp, TX))), "ok:bank=20000000;bonus=28000", "RB measure")
    os.makedirs(os.path.join(bk.home, "rebirth"), exist_ok=True)
    stale = os.path.join(bk.home, "rebirth", kp + ".rb-tx1760000000000-000001.properties")
    open(stale, "w").write("tx=tx1760000000000-000001\n")
    dec["v"] = "commit"
    K.check(str(R.apply(OA("prepare", kp, TX))).startswith("err:an older rebirth"), "RB prepare refused while an older committed txid is unfinished")
    dec["v"] = "unknown"
    K.eq(str(R.apply(OA("prepare", kp, TX))), "ok:bank=20000000;bonus=28000", "RB prepare")
    stg = os.path.join(bk.home, "rebirth", kp + ".rb-" + TX + ".properties")
    K.check(os.path.exists(stg) and not os.path.exists(stale) and os.path.exists(os.path.join(bk.home, "rebirth-backup", kp, TX, kp + ".properties")),
            "RB prepare: staged + backup, the stale staged file deleted")
    # an interest payout between prepare and commit is kept (delta)
    paid = int(S.payAll(GS([kp]), now - 2 * DAY, now - DAY, DAY, 1)[0][0])
    K.check(paid > 0 and int(S.getKey(kp)) == 20000000 + paid, "RB a payout between prepare and commit: +%d" % paid)
    RW = "pts.Class=12;bonus=5011;max=30000;bal=25000000"
    K.check(str(R.apply(OA("commit", kp, TX, JClass("java.lang.Integer")(1), "pts.Class=1"))).startswith("err:the rewards"), "RB commit without bonus / max / bal = err")
    K.check(str(R.apply(OA("commit", kp, TX, JClass("java.lang.Integer")(0), RW))).startswith("err:no rebirth number"), "RB commit without a rebirth number = err")
    K.check(str(R.apply(OA("commit", kp, "tx1760000000009-a1b2c3", JClass("java.lang.Integer")(1), RW))).startswith("err:no staged file"), "RB commit without a staged file = err")
    before = open(os.path.join(bk.home, "accounts", kp + ".properties"), "rb").read()
    Rb.FAIL_WRITE = 1
    r1 = str(R.apply(OA("commit", kp, TX, JClass("java.lang.Integer")(1), RW)))
    K.check(r1.startswith("err:could not write") and open(os.path.join(bk.home, "accounts", kp + ".properties"), "rb").read() == before
            and int(S.getKey(kp)) == 20000000 + paid and os.path.exists(stg), "RB commit whose write fails: err, NOTHING changed (file first, memory after): %s" % r1)
    r2 = str(R.apply(OA("commit", kp, TX, JClass("java.lang.Integer")(1), RW)))
    f = bk.files()[kp + ".properties"]
    K.check(r2 == "ok" and f.get("balance") == str(paid) and f.get("rb.bonus") == "3.0000" and f.get("rb.hist.1") == "25000000" and f.get("rb.lastTx") == TX
            and not os.path.exists(stg) and int(S.getKey(kp)) == paid, "RB commit: bank = the payout after prepare (%d), bonus 2.8 + 0.5011 capped at 3, hist, lastTx: %s" % (paid, f))
    K.eq(str(R.apply(OA("commit", kp, TX, JClass("java.lang.Integer")(1), RW))), "done", "RB commit again = done (no double bonus)")
    K.eq(bk.files()[kp + ".properties"].get("rb.bonus"), "3.0000", "RB the bonus once")
    K.check(str(R.apply(OA("abort", kp, TX))).startswith("err:already committed") and str(R.apply(OA("prepare", kp, TX))).startswith("err:already committed"),
            "RB abort / prepare after the commit = err")
    K.eq(str(R.apply(OA("status", kp, TX))), "committed", "RB status committed")
    # never lowered: a later rebirth with a smaller max keeps what was earned
    TX2 = "tx1760000000002-a1b2c3"
    R.apply(OA("prepare", kp, TX2))
    K.eq(str(R.apply(OA("commit", kp, TX2, JClass("java.lang.Integer")(2), "bonus=100;max=10000;bal=5"))), "ok", "RB rebirth 2 commit")
    f = bk.files()[kp + ".properties"]
    K.check(f.get("rb.bonus") == "3.0000" and f.get("rb.hist.2") == "5" and f.get("rb.hist.1") == "25000000" and f.get("rb.lastTx") == TX2,
            "RB rebirth 2: the bonus is never lowered by a smaller max; hist.1 + hist.2 kept")
    TX3 = "tx1760000000003-a1b2c3"
    R.apply(OA("prepare", kp, TX3))
    K.check(os.path.exists(os.path.join(bk.home, "rebirth", kp + ".rb-" + TX3 + ".properties")) and str(R.apply(OA("abort", kp, TX3))) == "done"
            and not os.path.exists(os.path.join(bk.home, "rebirth", kp + ".rb-" + TX3 + ".properties")), "RB abort deletes the staged file")
    K.eq(str(R.apply(OA("status", kp, TX3))), "none", "RB status none")
    t3 = os.path.join(bk.home, "rebirth", kp + ".rb-" + TX3 + ".properties.tmp")
    open(t3, "w").write("torn")
    K.check(str(R.apply(OA("abort", kp, TX3))) == "done" and not os.path.exists(t3), "RB abort also deletes a staged write torn by a crash (.tmp)")
    old_tmp = os.path.join(bk.home, "rebirth", kp + ".rb-tx1750000000000-000001.properties.tmp")
    open(old_tmp, "w").write("torn")
    R.apply(OA("prepare", kp, "tx1760000000003-a1b2c4"))
    K.check(not os.path.exists(old_tmp), "RB prepare cleans an older torn staged write (.tmp)")
    R.apply(OA("abort", kp, "tx1760000000003-a1b2c4"))
    for i in range(4, 9):
        R.apply(OA("prepare", kp, "tx176000000000%d-a1b2c3" % i))
    K.eq(len(os.listdir(os.path.join(bk.home, "rebirth-backup", kp))), 3, "RB backups: the last 3 kept")
    kbad = str(W.u(6))
    os.makedirs(os.path.join(bk.home, "accounts", kbad + ".properties"))
    K.check(str(R.apply(OA("prepare", kbad, TX))).startswith("err:the account file"), "RB prepare of an unreadable account = err")
    b3 = T9.Bank(jar, bk.home)
    R3 = JClass(PKG + "BankRb", loader=b3.L)()
    K.eq(str(R3.apply(OA("commit", kp, TX2, JClass("java.lang.Integer")(2), "bonus=1;max=1;bal=1"))), "done", "RB restart: a fresh loader answers done (rb.lastTx from the file)")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyBank", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("rb", run_rb), ("name", T10.run_name), ("exec", T9.run_exec), ("live", T9.run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyBank"))
