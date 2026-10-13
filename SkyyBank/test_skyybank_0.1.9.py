"""Harness for SkyyBank 0.1.9 (lag fixes: lock-free bridge, a lock per account file, the payout in three steps, purse flush;
tools/bank_0_1_9_patch.py). Build first: python tools/bank_0_1_9_patch.py && python SkyyBank/build_skyybank_0.1.9.py

    python SkyyBank/test_skyybank_0.1.9.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py: the game's JRE, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.1.8 -> 0.1.9: exactly the listed members differ (no class added)
  X  exec     0.1.8 and 0.1.9 side by side (own class loaders over the 0.7.0 server jar, own accounts folders, own stand-in purses; a
              stand-in profile:fn:key gives some players 2-3 profiles):
              DIFF   800 random steps (deposit / withdraw incl. "not enough", a profile switch, a daily sweep with 1-3 due days, both
                     scopes, an unreadable account file) on both jars: the same answers, account files, purses and bank:<uuid> values
              LOCK   (a) a thread HOLDING account X's lock: a deposit / withdraw / balance on account Y runs at once, X's own waits;
                     (b) the REAL sweep (BankTick.sweep -> payAll) PAUSED on account X's lock in step 3: the snapshot is already over
                     (RW not write-held), a deposit on Y completes meanwhile, then the sweep finishes and X gets balance-of-the-moment +
                     its share; (c) RW held exclusive (= the snapshot): credit / debit / payout writes wait; planAll itself never waits
                     for an account lock (memory only); (d) CONTROL 0.1.8: a deposit waits while the BankStore class monitor is held;
                     (e) coins:fn:take / add run with no bank lock (Thread.holdsLock(BankStore.class) false, RW not held)
              SNAP   4 threads moving coins bank -> purse -> bank between 6 players while a sweep thread pays 40 payouts in a row
                     (scope account): coins conserved (banks + purses = start + the interest payAll reports), every payout's interest
                     = the brackets of one consistent cut (each account paid exactly once per payout: paidThrough), no exception
              CRASH  a payout over 9 accounts in 4 groups (3 compounding days, both scopes, one account with an unfinished .tmp): a crash
                     after EVERY account write (0..9 files written, the clock not saved) + a restart pays the rest - every case ends
                     with the same balance / paidThrough / lastGain in every file as the uninterrupted payout (no account paid twice, none skipped)
              COINS  the REAL SkyyCoins 0.1.6 ledger (write-behind) on the bridge, disk state after every step of a deposit and a
                     withdraw: 0.1.9 never has the coins in BOTH files (deposit: purse flushed BEFORE the bank file is credited; the only
                     window = the bank file write right after it, the SkyyCoins 0.1.5 order); CONTROL 0.1.8 + SkyyCoins 0.1.6: the
                     deposit leaves the coins in both files until SkyyCoins' next flush (the dupe 0.1.9 closes); flush order recorded
              FAILFLUSH (fix round) coins:fn:flush answering -1 / throwing: the deposit answers 5, the coins go back to the purse, the
                     bank file is not written, never more coins on disk than existed; a withdraw still works (logged)
              BRIDGE BankStore.bridge() = the System property map (same identity), cached; answers while System.class's monitor is held
                     (0.1.8 waits = CONTROL)
              PUB    8 threads: deposits on a player's active profile while its profile flips and publish(u) runs: bank:<uuid> ends = the
                     active profile's balance
  D  live     start twice on a scratch COPY of the live Skyy_SkyyBank with 0.1.8 and 0.1.9 (BankMig, BankMig2, BankConfig.load, every
              account read, the payout of a due day): no file changed by a start that 0.1.8 does not change, the same balances
  AA engine-access audit
Scratch: tools/dev/scratch/perfmenu/bank (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, random, shutil, threading, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.1.9"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyBank-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyBank-0.1.8.jar")
COINS_JAR = os.path.join(ROOT, "SkyyCoins", "SkyyCoins-0.1.6.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "perfmenu", "bank")))
PKG = "com.skyy.bank."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyBank")
DAY = 86400000
EXPECT = {
    "BankStore": ["+f BRIDGE", "+f KL", "+f RW", "+m bridge0", "~m bridge", "+m lockOf", "+m publishIfActive0", "~m publishIfActive",
                  "+m loadKey0", "~m loadKey", "~m ready", "~m getKey", "+m setKey0", "~m setKey", "~m get", "~m set", "~m readable",
                  "+m publish0", "~m publish", "+m creditK0", "~m creditK", "+m debitK0", "~m debitK", "+m coinsFlush", "~m deposit",
                  "~m withdraw", "~m allAccounts", "-m payKey", "+m payKey0", "-m payGroup", "+m planGroup", "+m planAll", "+m snapshot",
                  "+m applyKey0", "+m applyKey", "~m payAll", "~<clinit>"],
    "CfgRows": ["+f BRIDGE", "+m bridge0", "~m bridge", "~m header"],             # the kit's lock-free bridge (tools/skyycfg.py) + version text
    "CfgFn": ["~m opExport"],                                                     # the version text
    "SkyyBankPlugin": ["~m setup"],                                               # the ready line's version
}
ADDED = []
NP = 7


def loader_for(jar):
    from jpype import JClass, JArray
    URL = JClass("java.net.URL")
    arr = JArray(URL)([JClass("java.io.File")(jar).toURI().toURL()])
    return JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getSystemClassLoader())


class World(object):
    """the shared bridge + stand-in purses (one book per jar) + a stand-in profile:fn:key"""

    def __init__(self):
        from jpype import JClass, JImplements, JOverride
        self.UUID, self.Long, self.Bool = JClass("java.util.UUID"), JClass("java.lang.Long"), JClass("java.lang.Boolean")
        self.Sys = JClass("java.lang.System")
        self.BR = JClass("java.util.concurrent.ConcurrentHashMap")()
        self.Sys.getProperties().put("skyy.bridge", self.BR)
        self.PURSE = {"old": {}, "new": {}}
        self.CUR = ["new"]
        self.PROF = {}            # uuid text -> active profile number (1 = the uuid key)
        self.HOOK = [None]
        self.FAILADD = set()
        self.PL = threading.Lock()
        W = self

        def key(u):
            p = W.PROF.get(str(u), 1)
            return str(u) if p == 1 else "%s-p%d" % (u, p)
        self.key = key

        @JImplements("java.util.function.Function")
        class KeyFn:
            @JOverride
            def apply(self, u):
                return key(u)

        @JImplements("java.util.function.Function")
        class Get:
            @JOverride
            def apply(self, u):
                return W.Long.valueOf(W.PURSE[W.CUR[0]].get(key(u), 0))

        @JImplements("java.util.function.Function")
        class Add:
            @JOverride
            def apply(self, a):
                u, n = a[0], int(a[1])
                if W.HOOK[0] is not None:
                    W.HOOK[0]("add", u, n)
                if str(u) in W.FAILADD:
                    return None
                with W.PL:
                    P = W.PURSE[W.CUR[0]]
                    P[key(u)] = P.get(key(u), 0) + n
                    v = P[key(u)]
                return W.Long.valueOf(v)

        @JImplements("java.util.function.Function")
        class Take:
            @JOverride
            def apply(self, a):
                u, n = a[0], int(a[1])
                if W.HOOK[0] is not None:
                    W.HOOK[0]("take", u, n)
                with W.PL:
                    P = W.PURSE[W.CUR[0]]
                    if P.get(key(u), 0) < n:
                        return W.Bool.FALSE
                    P[key(u)] = P.get(key(u), 0) - n
                return W.Bool.TRUE
        self.fns = {"profile:fn:key": KeyFn(), "coins:fn:get": Get(), "coins:fn:add": Add(), "coins:fn:take": Take()}
        self.on()

    def on(self):
        for k, v in self.fns.items():
            self.BR.put(k, v)

    def u(self, i):
        return self.UUID(0x0B0A000000000000 + i * 7919, 0x1000 + i)


class Bank(object):
    """one jar in its own loader, pointed at its own folder"""

    def __init__(self, jar, home):
        from jpype import JClass
        self.L = loader_for(jar)
        c = lambda n: JClass(PKG + n, loader=self.L)
        self.S, self.C, self.T = c("BankStore"), c("BankConfig"), c("BankTick")
        self.home = home
        self.point(home)

    def point(self, home):
        from jpype import JClass
        P = JClass("java.nio.file.Paths")
        self.home = home
        os.makedirs(os.path.join(home, "accounts"), exist_ok=True)
        self.S.DIR = P.get(os.path.join(home, "accounts"))
        self.C.FILE = P.get(os.path.join(home, "config.properties"))
        self.C.STATE = P.get(os.path.join(home, "state.properties"))
        for mp in (self.S.BAL, self.S.LOADED, self.S.PAID, self.S.GAIN, self.S.EPOCH):
            mp.clear()
        try:
            self.S.KL.clear()
        except Exception:
            pass

    def files(self):
        d = os.path.join(self.home, "accounts")
        out = {}
        for f in sorted(os.listdir(d)):
            if f.endswith(".properties"):
                out[f] = dict(l.split("=", 1) for l in open(os.path.join(d, f), encoding="latin-1").read().splitlines() if "=" in l and not l.startswith("#"))
        return out


def write_acc(home, key, bal, extra=""):
    d = os.path.join(home, "accounts")
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, key + ".properties"), "w", encoding="ascii", newline="").write("#SkyyBank\r\nbalance=%s\r\n%s" % (bal, extra))


def run_bg(fn):
    box = {}

    def t():
        try:
            box["r"] = fn()
        except Exception as e:
            box["e"] = str(e)[:300]
    th = threading.Thread(target=t, daemon=True)
    th.start()
    return th, box


def run_exec(out, jar, scratch, _home):
    import jpype
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    W = World()
    Sys = W.Sys
    old = Bank(OLD_JAR, os.path.join(scratch, "x_old"))
    new = Bank(jar, os.path.join(scratch, "x_new"))
    U = [W.u(i) for i in range(NP)]
    for J in (old, new):
        J.C.load()

    def both(fn):
        res = []
        for tag, J in (("old", old), ("new", new)):
            W.CUR[0] = tag
            res.append(fn(J))
        W.CUR[0] = "new"
        return res

    # ------------------------------------------------------------------ DIFF
    rnd = random.Random(19)
    for i in range(NP):
        for tag in ("old", "new"):
            W.PURSE[tag][str(U[i])] = 50000 + i * 1000
            W.PURSE[tag]["%s-p2" % U[i]] = 20000
            W.PURSE[tag]["%s-p3" % U[i]] = 5000
    # one unreadable account (both jars): nothing may be written over it
    for J in (old, new):
        open(os.path.join(J.home, "accounts", "%s-p3.properties" % U[6]), "w").write("balance=notanumber\n")
    now0 = int(Sys.currentTimeMillis())
    for J in (old, new):
        J.C.LAST = now0 - DAY // 2
    clock = [0]
    for step in range(800):
        op = rnd.random()
        u = rnd.choice(U)
        if op < 0.35:
            n = rnd.choice([1, 50, 999, 5000, 20000, 80000])
            r = both(lambda J: int(J.S.deposit(u, n)))
            K.eq(r[1], r[0], "DIFF %d deposit %d: the same answer" % (step, n))
        elif op < 0.65:
            n = rnd.choice([1, 50, 999, 5000, 20000, 80000])
            r = both(lambda J: int(J.S.withdraw(u, n)))
            K.eq(r[1], r[0], "DIFF %d withdraw %d: the same answer" % (step, n))
        elif op < 0.75:
            W.PROF[str(u)] = rnd.choice([1, 1, 2, 3])
            both(lambda J: J.S.publish(u))
        elif op < 0.85:
            days = rnd.choice([1, 1, 2, 3])
            scope = rnd.choice(["account", "account", "profile"])
            cu = rnd.choice([1, 3])
            clock[0] += 1
            lastv = int(Sys.currentTimeMillis()) - days * DAY - 60000

            def sweep(J):
                J.C.SCOPE = scope
                J.C.CATCH_UP = cu
                J.C.LAST = lastv
                J.T.sweep()
                return int(J.C.LAST)
            both(sweep)
        else:
            r = both(lambda J: [int(J.S.get(u)), bool(J.S.readable(u)), int(J.S.nextGain(u))])
            K.eq(r[1], r[0], "DIFF %d balance / readable / nextGain" % step)
        if step % 20 == 0 or step == 799:
            K.eq(new.files(), old.files(), "DIFF %d: the account files" % step)
            K.eq(W.PURSE["new"], W.PURSE["old"], "DIFF %d: the purses" % step)
    K.check(open(os.path.join(new.home, "accounts", "%s-p3.properties" % U[6])).read() == "balance=notanumber\n", "DIFF: the unreadable account is never written")
    K.notes.append("DIFF: 800 steps, %d sweeps, %d account files" % (clock[0], len(new.files())))

    # ------------------------------------------------------------------ LOCK
    S = new.S
    W.PROF.clear()
    ux, uy = W.u(30), W.u(31)
    kx, ky = str(ux), str(uy)
    for uu in (ux, uy):
        W.PURSE["new"][str(uu)] = 100000
    S.deposit(ux, 1000)
    S.deposit(uy, 1000)
    with jpype.synchronized(S.lockOf(kx)):
        for name, fn in (("deposit", lambda: int(S.deposit(uy, 10))), ("withdraw", lambda: int(S.withdraw(uy, 5))),
                         ("balance", lambda: int(S.get(uy))), ("nextGain", lambda: int(S.nextGain(uy)))):
            th, box = run_bg(fn)
            th.join(5.0)
            K.check(not th.is_alive() and "e" not in box, "LOCK a: %s on account Y runs while account X's lock is held (%s)" % (name, box))
        th, box = run_bg(lambda: int(S.deposit(ux, 10)))
        th.join(0.6)
        K.check(th.is_alive(), "LOCK a: account X's own deposit waits for X's lock")
    th.join(5.0)
    K.check(not th.is_alive() and box.get("r") == 1, "LOCK a: and finishes after (%s)" % box)
    # (b) the real sweep paused on X in step 3
    new.C.SCOPE = "account"
    new.C.CATCH_UP = 1
    bx0 = int(S.get(ux))
    new.C.LAST = int(Sys.currentTimeMillis()) - DAY - 1000
    with jpype.synchronized(S.lockOf(kx)):
        ths, boxs = run_bg(lambda: new.T.sweep())
        time.sleep(1.5)
        paused = ths.is_alive()
        snap_over = not S.RW.isWriteLocked()
        thd, boxd = run_bg(lambda: int(S.deposit(uy, 7)))
        thd.join(5.0)
        K.check(paused and snap_over and not thd.is_alive() and boxd.get("r") == 1,
                "LOCK b: the sweep is paused on account X in step 3, the snapshot is over, a deposit on Y completes meanwhile (%s %s %s)" % (paused, snap_over, boxd))
        # a deposit on X waits behind the sweep's write of X? X's lock is held by us: deposit queued
        thx, boxx = run_bg(lambda: int(S.deposit(ux, 3)))
        thx.join(0.3)
        K.check(thx.is_alive(), "LOCK b: a deposit on X waits")
    ths.join(10.0)
    thx.join(10.0)
    K.check(not ths.is_alive() and not thx.is_alive() and "e" not in boxs, "LOCK b: the sweep and X's deposit finish (%s %s)" % (boxs, boxx))
    gain_x = int(S.GAIN.get(kx))
    K.eq(int(S.get(ux)), bx0 + gain_x + 3, "LOCK b: X = its balance + its share + the deposit made meanwhile (no coin written over)")
    K.check(gain_x > 0, "LOCK b: X got interest (%d)" % gain_x)
    # (c) RW exclusive = the snapshot
    S.RW.writeLock().lock()
    try:
        ths_ = [run_bg(fn) for fn in (lambda: bool(S.creditK(ky, 1)), lambda: int(S.debitK(ky, 1)), lambda: S.setKey(ky, int(S.getKey(ky))),
                                       lambda: bool(S.applyKey(ky, 0, 1, 0)))]
        time.sleep(0.5)
        K.check(all(t_.is_alive() for t_, _b in ths_), "LOCK c: credit / debit / setKey / applyKey wait while RW is held exclusive (the snapshot): %s" % [(t_.is_alive(), b_) for t_, b_ in ths_])
    finally:
        S.RW.writeLock().unlock()
    for t_, b_ in ths_:
        t_.join(5.0)
    K.check(not any(t_.is_alive() for t_, _b in ths_), "LOCK c: ... and run after")
    with jpype.synchronized(S.lockOf(kx)):
        from jpype import JArray, JString, JObject
        grp = JArray(JObject)([JArray(JString)([kx, ky])])
        thp, boxp = run_bg(lambda: S.planAll(grp, 0, 2 * DAY, DAY, 1))
        thp.join(5.0)
        K.check(not thp.is_alive() and "e" not in boxp, "LOCK c: planAll (the snapshot's work) never waits for an account lock (%s)" % boxp)
    # (d) CONTROL 0.1.8
    O = old.S
    W.CUR[0] = "old"
    W.PURSE["old"][str(uy)] = 100000
    with jpype.synchronized(O.class_):
        th, box = run_bg(lambda: int(O.deposit(uy, 10)))
        th.join(0.6)
        K.check(th.is_alive(), "LOCK d CONTROL: 0.1.8 - a deposit waits while the BankStore class monitor is held (a payout)")
    th.join(5.0)
    W.CUR[0] = "new"
    # (e) coins calls with no bank lock
    seen = {}

    def hook(what, u, n):
        seen[what] = [bool(JClass("java.lang.Thread").holdsLock(S.class_)), int(S.RW.getReadHoldCount()), bool(S.RW.isWriteLocked())]
    W.HOOK[0] = hook
    S.deposit(uy, 11)
    S.withdraw(uy, 11)
    W.HOOK[0] = None
    K.eq(seen, {"take": [False, 0, False], "add": [False, 0, False]}, "LOCK e: coins:fn:take / add run with no bank lock")

    # ------------------------------------------------------------------ SNAP: transfers during back-to-back payouts
    new.C.SCOPE = "account"
    new.C.CATCH_UP = 1
    su = [W.u(40 + i) for i in range(6)]
    for i, uu in enumerate(su):
        W.PURSE["new"][str(uu)] = 0
        write_acc(new.home, str(uu), 300000 + i * 250000)
        S.BAL.remove(str(uu))
        S.LOADED.remove(str(uu))
        S.PAID.remove(str(uu))
        S.GAIN.remove(str(uu))
    start_total = sum(int(S.get(uu)) for uu in su)
    stop = [False]
    errs = []

    def mover(seed):
        r = random.Random(seed)
        while not stop[0]:
            a, b = r.sample(su, 2)
            n = r.randint(1, 50000)
            try:
                if int(S.withdraw(a, n)) == 1:
                    # the coins sit in a's purse; hand them to b's purse (a stand-in trade) and deposit them
                    with W.PL:
                        W.PURSE["new"][str(a)] -= n
                        W.PURSE["new"][str(b)] = W.PURSE["new"].get(str(b), 0) + n
                    if int(S.deposit(b, n)) != 1:
                        errs.append("deposit refused")
            except Exception as e:
                errs.append(str(e)[:200])
    interest = [0]
    from jpype import JArray, JString, JObject

    def sweeper():
        base = int(Sys.currentTimeMillis()) - 100 * DAY
        for d in range(40):
            try:
                grp = JArray(JObject)([JArray(JString)(sorted(str(uu) for uu in su))])
                got = S.payAll(grp, base + d * DAY, base + (d + 1) * DAY, DAY, 1)
                interest[0] += sum(int(x) for x in got[0])
            except Exception as e:
                errs.append("sweep " + str(e)[:200])
    ths = [threading.Thread(target=mover, args=(s_,), daemon=True) for s_ in range(4)]
    for t_ in ths:
        t_.start()
    tsw = threading.Thread(target=sweeper, daemon=True)
    tsw.start()
    tsw.join(120)
    stop[0] = True
    for t_ in ths:
        t_.join(30)
    end_total = sum(int(S.get(uu)) for uu in su) + sum(W.PURSE["new"].get(str(uu), 0) for uu in su)
    K.eq(errs, [], "SNAP: no exception, no refused deposit")
    K.eq(end_total, start_total + interest[0], "SNAP: coins conserved - banks + purses = start + the interest payAll reported (%d over 40 payouts)" % interest[0])
    files = new.files()
    K.eq(sorted(set(files["%s.properties" % uu]["paidThrough"] for uu in su)), [str(int(S.PAID.get(str(su[0]))))],
         "SNAP: every account file carries the last payout as paidThrough")
    # a consistent cut: each payout's interest = interestOf(the sum at ONE moment) - check the last payout alone with no movers running
    tot_before = sum(int(S.get(uu)) for uu in su)
    base2 = int(S.PAID.get(str(su[0])))
    grp = JArray(JObject)([JArray(JString)(sorted(str(uu) for uu in su))])
    got = S.payAll(grp, base2, base2 + DAY, DAY, 1)
    K.eq(sum(int(x) for x in got[0]), int(new.C.interestOf(tot_before)), "SNAP: one payout = the brackets of the group's sum")
    got2 = S.payAll(grp, base2, base2 + DAY, DAY, 1)
    K.eq(sum(int(x) for x in got2[0]), 0, "SNAP: the same payout again pays nothing (paidThrough)")

    # ------------------------------------------------------------------ CRASH
    def crash_case(scope, label):
        keys = []
        grp_of = {}
        for gi in range(4):
            gu = W.u(60 + gi)
            n_ = [1, 2, 3, 3][gi]
            for p in range(1, n_ + 1):
                k = str(gu) if p == 1 else "%s-p%d" % (gu, p)
                keys.append(k)
                grp_of[k] = gi
        bal0 = dict((k, 120000 + i * 777777) for i, k in enumerate(keys))
        ref_home = os.path.join(scratch, "crash", label, "ref")
        for k in keys:
            write_acc(ref_home, k, bal0[k])
        open(os.path.join(ref_home, "accounts", keys[2] + ".properties.tmp"), "w").write("balance=1\n")
        last = int(Sys.currentTimeMillis()) - 3 * DAY - 5000

        def fresh(home):
            new.point(home)
            new.C.load()
            new.C.SCOPE = scope
            new.C.CATCH_UP = 3
            new.C.LAST = last
        before = os.path.join(scratch, "crash", label, "before")
        shutil.copytree(ref_home, before)
        fresh(ref_home)
        order = []
        mt = {}
        new.T.sweep()
        after = {}
        for k in keys:
            p = os.path.join(ref_home, "accounts", k + ".properties")
            after[k] = open(p, "rb").read()
            mt[k] = os.stat(p).st_mtime_ns
        order = sorted(keys, key=lambda k_: mt[k_])
        def parse(b_):
            return dict(l.split("=", 1) for l in b_.decode("latin-1").splitlines() if "=" in l and not l.startswith("#"))
        final_ref = dict((k, parse(after[k])) for k in keys)
        n_ok = 0
        for j in range(len(keys) + 1):
            h = os.path.join(scratch, "crash", label, "c%d" % j)
            shutil.copytree(before, h)
            for k in order[:j]:
                open(os.path.join(h, "accounts", k + ".properties"), "wb").write(after[k])
            fresh(h)
            new.T.sweep()
            res = dict((k, parse(open(os.path.join(h, "accounts", k + ".properties"), "rb").read())) for k in keys)
            if K.eq(res, final_ref, "CRASH %s: a crash after %d of %d account writes + a restart = the uninterrupted payout" % (label, j, len(keys))):
                n_ok += 1
            shutil.rmtree(h, ignore_errors=True)
        paid = sum(int(final_ref[k]["balance"]) - bal0[k] for k in keys)
        K.check(paid > 0, "CRASH %s: the payout paid %d coins" % (label, paid))
        K.notes.append("CRASH %s: %d crash points, %d coins paid" % (label, n_ok, paid))
    crash_case("account", "account")
    crash_case("profile", "profile")
    new.point(new.home)

    # ------------------------------------------------------------------ COINS: the real SkyyCoins 0.1.6 ledger
    from jpype import JImplements, JOverride
    Lc = loader_for(COINS_JAR)
    CS = JClass("com.skyy.coins.CoinStore", loader=Lc)
    Fn = JClass("com.skyy.coins.CoinFn", loader=Lc)
    P = JClass("java.nio.file.Paths")
    cdir = os.path.join(scratch, "coins", "balances")
    os.makedirs(cdir, exist_ok=True)
    CS.DIR = P.get(cdir)
    CS.JOURNAL = P.get(os.path.join(scratch, "coins", "balances-journal.properties"))
    real = dict((m, Fn(m)) for m in ("get", "add", "take", "flush"))
    events = []
    probes = []

    def disk(u, J):
        pf = os.path.join(cdir, str(u) + ".properties")
        purse = int([l for l in open(pf).read().splitlines() if l.startswith("balance=")][0].split("=")[1]) if os.path.isfile(pf) else 0
        bf = os.path.join(J.home, "accounts", str(u) + ".properties")
        bank = int([l for l in open(bf, encoding="latin-1").read().splitlines() if l.startswith("balance=")][0].split("=")[1]) if os.path.isfile(bf) else 0
        return purse + bank

    @JImplements("java.util.function.Function")
    class Wrap:
        def __init__(self, m, J, u):
            self.m, self.J, self.u = m, J, u

        @JOverride
        def apply(self, a):
            r = real[self.m].apply(a)
            events.append(self.m)
            probes.append((self.m, disk(self.u, self.J)))
            return r
    for tag, J in (("new", new), ("old", old)):
        uc = W.u(90 if tag == "new" else 91)
        CS.set(uc, 10000)
        CS.flushNow()
        J.S.setKey(str(uc), 5000)
        for m in ("get", "add", "take", "flush"):
            W.BR.put("coins:fn:" + m, Wrap(m, J, uc))
        t0 = disk(uc, J)
        del events[:]
        del probes[:]
        rd = int(J.S.deposit(uc, 2500))
        dep_events, dep_probes, dep_end = list(events), list(probes), disk(uc, J)
        del events[:]
        del probes[:]
        rw = int(J.S.withdraw(uc, 1000))
        wd_events, wd_probes, wd_end = list(events), list(probes), disk(uc, J)
        CS.flushNow()
        settled = disk(uc, J)
        if tag == "new":
            K.eq([rd, rw], [1, 1], "COINS: deposit + withdraw on the real ledger")
            K.eq([e for e in dep_events if e != "get"], ["take", "flush"], "COINS: deposit = take, then coins:fn:flush (before the bank file)")
            K.eq([e for e in wd_events if e != "get"], ["add", "flush"], "COINS: withdraw = add, then coins:fn:flush")
            K.check(all(t_ <= t0 for _m, t_ in dep_probes) and dep_end == t0, "COINS: deposit - never more coins on disk than existed at any "
                    "step (no dupe): %s end %d start %d" % (dep_probes, dep_end, t0))
            K.eq([t_ for m_, t_ in dep_probes if m_ == "flush"], [t0 - 2500], "COINS: the one window = after the purse flush, before the bank "
                 "file write (the SkyyCoins 0.1.5 order; milliseconds)")
            K.check(all(t_ <= t0 for _m, t_ in wd_probes) and wd_end == t0, "COINS: withdraw - never more coins on disk than existed (no dupe): "
                    "%s end %d" % (wd_probes, wd_end))
            K.eq([t_ for m_, t_ in wd_probes if m_ == "add"], [t0 - 1000], "COINS: the withdraw's one window = after the bank file debit, "
                 "before the purse flush (milliseconds; 0.1.8 + SkyyCoins 0.1.6: up to 1 s)")
            K.notes.append("COINS: deposit probes %s, withdraw probes %s (start %d)" % (dep_probes, wd_probes, t0))
            K.eq(settled, t0, "COINS: after SkyyCoins' own flush the coins on disk = the coins that existed")
        else:
            K.eq([e for e in dep_events if e != "get"], ["take"], "COINS CONTROL: 0.1.8 never flushes")
            K.eq(dep_end, t0 + 2500, "COINS CONTROL: 0.1.8 + SkyyCoins 0.1.6 - right after the deposit BOTH files hold the 2,500 (a crash "
                 "now = a dupe; 0.1.9 closes it)")
            K.eq(settled, t0, "COINS CONTROL: after SkyyCoins' own flush it is right again")
    # FIX ROUND (critic finding): a FAILED purse flush (-1 = SkyyCoins could not write, or a throw) stops the deposit BEFORE the bank file
    # moves: the coins go back to the purse (memory), answer 5, bank file unchanged, never more coins on disk than existed
    @JImplements("java.util.function.Function")
    class BadFlush:
        def __init__(self, mode):
            self.mode, self.calls = mode, 0

        @JOverride
        def apply(self, a):
            self.calls += 1
            if self.mode == "throw":
                raise JClass("java.lang.IllegalStateException")("disk full (harness)")
            return JClass("java.lang.Integer").valueOf(-1)
    for mode in ("minus1", "throw"):
        uc = W.u(92 if mode == "minus1" else 93)
        CS.set(uc, 10000)
        CS.flushNow()
        new.S.setKey(str(uc), 5000)
        for m in ("get", "add", "take"):
            W.BR.put("coins:fn:" + m, real[m])
        bf = BadFlush(mode)
        W.BR.put("coins:fn:flush", bf)
        t0 = disk(uc, new)
        bank_before = open(os.path.join(new.home, "accounts", str(uc) + ".properties"), "rb").read()
        rd = int(new.S.deposit(uc, 2500))
        K.eq(rd, 5, "FAILFLUSH %s: a deposit whose purse flush failed answers 5 (purse error, nothing moved)" % mode)
        K.eq(int(CS.get(uc)), 10000, "FAILFLUSH %s: the 2,500 went back to the purse" % mode)
        K.eq(int(new.S.getKey(str(uc))), 5000, "FAILFLUSH %s: the bank balance did not move" % mode)
        K.eq(open(os.path.join(new.home, "accounts", str(uc) + ".properties"), "rb").read(), bank_before,
             "FAILFLUSH %s: the bank file was not written" % mode)
        K.check(disk(uc, new) <= t0, "FAILFLUSH %s: never more coins on disk than existed (no dupe after a crash)" % mode)
        K.check(bf.calls >= 1, "FAILFLUSH %s: the flush was asked" % mode)
        rw = int(new.S.withdraw(uc, 1000))
        K.eq(rw, 1, "FAILFLUSH %s: a withdraw still works (the coins are in the purse; the failed flush is logged)" % mode)
        K.eq([int(CS.get(uc)), int(new.S.getKey(str(uc)))], [11000, 4000], "FAILFLUSH %s: withdraw moved 1,000 bank -> purse" % mode)
        W.BR.put("coins:fn:flush", real["flush"])
        CS.flushNow()
        K.eq(disk(uc, new), t0, "FAILFLUSH %s: after SkyyCoins' own flush the coins on disk = the coins that existed" % mode)
    W.on()
    W.BR.remove("coins:fn:flush")

    # ------------------------------------------------------------------ BRIDGE
    Sys.getProperties().remove("skyy.bridge")
    new.S.BRIDGE = None
    m1 = new.S.bridge()
    K.check(Sys.identityHashCode(Sys.getProperties().get("skyy.bridge")) == Sys.identityHashCode(m1), "BRIDGE: bridge() creates the System property map")
    K.check(Sys.identityHashCode(new.S.BRIDGE) == Sys.identityHashCode(m1), "BRIDGE: cached in BRIDGE")
    K.check(Sys.identityHashCode(old.S.bridge()) == Sys.identityHashCode(m1), "BRIDGE: 0.1.8 finds the same map")
    with jpype.synchronized(Sys.class_):
        th, box = run_bg(lambda: new.S.bridge())
        th.join(5.0)
        K.check(not th.is_alive() and Sys.identityHashCode(box.get("r")) == Sys.identityHashCode(m1), "BRIDGE: answers while System.class's monitor is held")
        th2, box2 = run_bg(lambda: old.S.bridge())
        th2.join(0.6)
        K.check(th2.is_alive(), "BRIDGE CONTROL: 0.1.8 waits for System.class's monitor")
    th2.join(5.0)
    for k, v in W.fns.items():
        m1.put(k, v)
    W.BR = m1

    # ------------------------------------------------------------------ PUB
    up = W.u(77)
    for p in (1, 2, 3):
        k = str(up) if p == 1 else "%s-p%d" % (up, p)
        write_acc(new.home, k, 1000 * p)
        W.PURSE["new"][k] = 10 ** 9
    stopp = [False]
    perr = []

    def flipper():
        r = random.Random(5)
        while not stopp[0]:
            W.PROF[str(up)] = r.choice([1, 2, 3])
            new.S.publish(up)

    def depos(seed):
        r = random.Random(seed)
        for _ in range(300):
            try:
                new.S.deposit(up, r.randint(1, 100)) if r.random() < 0.6 else new.S.withdraw(up, r.randint(1, 50))
            except Exception as e:
                perr.append(str(e)[:200])
    tf = threading.Thread(target=flipper, daemon=True)
    tf.start()
    tds = [threading.Thread(target=depos, args=(s_,), daemon=True) for s_ in range(7)]
    for t_ in tds:
        t_.start()
    for t_ in tds:
        t_.join(60)
    stopp[0] = True
    tf.join(10)
    new.S.publish(up)
    act = W.key(up)
    K.eq(perr, [], "PUB: no exception")
    K.eq(int(W.BR.get("bank:" + str(up))), int(new.S.getKey(act)), "PUB: bank:<uuid> = the active profile's balance after the storm")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    W = World()
    P = JClass("java.nio.file.Paths")
    d8 = os.path.join(os.path.dirname(home), "live8", "Skyy_SkyyBank")
    shutil.copytree(home, d8)
    res = {}
    for start in (1, 2):
        for tag, j, d in (("old", OLD_JAR, d8), ("new", jar, home)):
            W.CUR[0] = tag
            b0 = HK.tree_hash(d)
            J = Bank(j, d)
            M1 = JClass(PKG + "BankMig", loader=J.L)
            M2 = JClass(PKG + "BankMig2", loader=J.L)
            M1.run(P.get(d))
            M2.run(P.get(d))
            J.C.load()
            ks = sorted(str(k) for k in J.S.allAccounts())
            bals = dict((k, [int(J.S.getKey(k)), bool(J.S.ready(k))]) for k in ks)
            a0 = HK.tree_hash(d)
            res[(start, tag)] = [sorted(k for k in set(b0) | set(a0) if b0.get(k) != a0.get(k)), bals, int(J.C.CATCH_UP), str(J.C.SCOPE)]
        K.eq(res[(start, "new")][1:], res[(start, "old")][1:], "D%d: 0.1.9 reads the same accounts, balances and settings as 0.1.8" % start)
        K.eq(res[(start, "new")][0], res[(start, "old")][0], "D%d: 0.1.9 changes exactly the files 0.1.8 changes (%s)" % (start, res[(start, "old")][0]))
    K.eq(res[(2, "new")][0], [], "D2: the second start changes nothing")
    # a due payout on the live copies: the same files on both jars
    outs = {}
    last_fixed = int(W.Sys.currentTimeMillis()) - DAY - 60000
    for tag, j, d in (("old", OLD_JAR, d8), ("new", jar, home)):
        W.CUR[0] = tag
        J = Bank(j, d)
        J.C.load()
        J.C.LAST = last_fixed
        J.T.sweep()
        outs[tag] = J.files()
    K.eq(outs["new"], outs["old"], "D: a due payout on the live copy writes the same account files on both jars (%d accounts)" % len(outs["new"]))
    K.notes.append("D: %d live accounts" % len(res[(1, "new")][1]))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyBank", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("exec", run_exec), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyBank"))
