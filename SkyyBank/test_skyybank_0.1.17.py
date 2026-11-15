"""Harness for SkyyBank 0.1.17 (round bank2: bank levels - capacity + interest, the upgrade; tools/bank_0_1_17_patch.py).
Build first: python tools/bank_0_1_17_patch.py && python SkyyBank/build_skyybank_0.1.17.py

    python SkyyBank/test_skyybank_0.1.17.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Every child JVM gets the pinned SkyyCore jar on its class path (SKYY_HARNESS_CP). OLD jar = the LIVE 0.1.16 (the SET pin).
  A      every class loads + initialises with -Xverify:all
  C      class compare 0.1.16 -> 0.1.17 (exactly the classes / members the patch touches)
  S      static: the patch re-runs to identical bytes; no new class / command / system; deposit() after the level maths
  X      exec (EXECUTES every new path, stand-in purses + profile keys = test_skyybank_0.1.9.World):
         CONFIG  a fresh config.properties lists the level rows; caps / mults / costs; checkLevels refuses junk / falling capacities;
                 a bad list in the file = one WARN + the default; levels.enabled off = no cap, 100 %
         CAP     a deposit past the cap refused BEFORE the purse is touched (8 = room left / 7 = full), Deposit all fills to the cap and
                 leaves the rest in the purse, a balance above the cap kept (withdraw works, no new deposit), the cap re-checked under
                 the lock (a credit that would pass it = 7, the coins back in the purse), 8 threads depositing at once never pass the cap
         UPG     the upgrade: cost from the bank, ONE file write (bank.level + balance), the levels/ mirror; the same expected level twice =
                 one level; not enough = nothing; top level = nothing; a profile switch = nothing; a rebirth running = nothing; a failed
                 write = nothing changed; 8 threads clicking the same upgrade = exactly one level; deposits + upgrades + withdraws on 6
                 threads = no coin created or lost (purse + bank + spent = the start)
         LOAD    a restart reads the level (account line); the REAL 0.1.16 writes the account (drops bank.level) -> 0.1.17 again reads
                 the level from the levels/ mirror (rollback + forward loses nothing); rbWrite0 keeps the line
         PAY     the payout: capped balances in the bracket sum + the split, x the level percent, the rebirth bonus on the capped part;
                 a Python reference on 400 random groups (planGroup = nextGain = payAll), interest past the cap kept; levels off =
                 0.1.16's numbers exactly (the REAL 0.1.16 jar on the same files)
         PANEL   bank:fn:panel [10] [11] [12], bank:fn:move "upgrade" (the panel's key / epoch / level), bank:fn:level = the best level
                 of all profiles (null while off); BankCmd.move texts (full, room, filled)
  PAGE17 the fallback /bank page through the engine's PageManager (tools/hub_tab_harness.py): the kit 1.7 page check (every b.set /
         binding names an element - the new Upgrade bank button too), Upgrade bank: too poor = nothing, Lv 1 -> 2 for 25,000, the same
         click again (used-up token) = nothing, the next click (new token, Lv 2) works
  LIVE   START TWICE on a scratch COPY of the live NewBetaTest Skyy_SkyyBank: BankMig, BankMig2, BankConfig.load, every account read -
         nothing written by either start, every balance read the same as the REAL 0.1.16, every account Lv 1
  AA     engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, json, zipfile, random, threading, subprocess, importlib.util, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.1.17"
PKG = "com.skyy.bank."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyBank-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(os.path.join(HERE, "SkyyBank-0.1.16.jar"))
GEN = os.path.join(HERE, "build_skyybank_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyybank_0.1.16.py")
PATCH = os.path.join(ROOT, "tools", "bank_0_1_17_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "bank2", "bank")))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyBank")
DAY = 86400000


def tmod(fn, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


T9 = tmod("test_skyybank_0.1.9.py", "tb0109_for17")
T9.OLD_JAR = OLD_JAR
CORE_JAR = B.core_jar()
os.environ["SKYY_HARNESS_CP"] = CORE_JAR
EXPECT = {
    "BankCmd": ["+m fullText", "+m roomText", "~c ", "~m move", "~m run", "~m status"],
    "BankActionCmd": ["~c "],
    "BankConfig": ["+f C_CAP", "+f C_CAP_S", "+f C_COST", "+f C_COST_S", "+f C_INT", "+f C_INT_S", "+f LV_CAP", "+f LV_COST", "+f LV_INT",
                   "+f LV_ON", "+f LV_WARNED", "+m bracketTextLv", "+m caps", "+m checkLevels", "+m clampLv", "+m costOver", "+m costWarn", "+m costs", "+m levelsText",
                   "+m lvCap", "+m lvCost", "+m lvMul", "+m lvWarn", "+m maxLevel", "+m mults", "+m parseList", "+m pctLv", "+m rising",
                   "~<clinit>", "~m check", "~m load"],
    "BankPage": ["+f builtLevel", "+m pname", "+m rateTextLv", "+m subLv", "~m build", "~m handleDataEvent"],
    "BankPanelFn": ["~m apply", "~m move", "~m panel", "~m register", "~m unregister"],
    "BankStore": ["+f LVL", "+m capK", "+m creditCapK", "+m creditCapK0", "+m effK", "+m levelLine", "+m levelOf", "+m lvFile", "+m lvLine",
                  "+m lvMem", "+m lvMirror", "+m lvRead", "+m lvWrite0", "+m maxLevelU", "+m mulK", "+m mulShare", "+m roomK", "+m roomU",
                  "+m upgrade", "+m upgrade0", "+m upgradeU", "~<clinit>", "~m deposit", "~m loadKey0", "~m nextGain", "~m planGroup",
                  "~m rbWrite0", "~m setKey0"],
    "CfgData": ["~<clinit>"],
    "SkyyBankPlugin": ["~m setup"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read().replace("\r\n", "\n")
    o = open(GEN_OLD, encoding="utf8", newline="").read().replace("\r\n", "\n")
    K.check(g.startswith('"""SkyyBank 0.1.17 - build script') and g.count('VERSION = "0.1.17"\n') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand(", "pool.makeClass("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.check(g.count("public static int deposit(java.util.UUID u, long n) {") == 1 and g.index("public static int deposit(java.util.UUID u, long n) {") > g.index("public static long[] caps() {"), "S one deposit(), after the level maths")
    up = g[g.index("public static String upgrade(java.util.UUID u, String k, Object e, int expect) {"):]
    up = up[:up.index('}""")')]
    K.check("RW.readLock().lock();" in up and "synchronized (l) { r = upgrade0(k, expect); }" in up, "S the upgrade holds RW shared + the account lock (one call in the synchronized block)")
    u0 = g[g.index("public static String upgrade0(String k, int expect) {"):]
    u0 = u0[:u0.index('}""")')]
    K.check(u0.index("lvWrite0(k, nb, lv + 1);") < u0.index("BAL.put(k, Long.valueOf(nb));") < u0.index("lvMirror(k, lv + 1);"), "S the file first, memory after, the mirror last")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    m = re.search(r'BANK_PAGE_CHECKED = "([0-9a-f]{12})"', g)
    data = zipfile.ZipFile(JAR).read("com/skyy/bank/SkyyBankPlugin.class")
    K.check(m is not None and ("page " + m.group(1)).encode() in data, "S the built page id = BANK_PAGE_CHECKED %s" % (m and m.group(1)))
    K.save()


# ---------------------------------------------------------------- Python reference of the 0.1.17 payout (one day, one group)
def ref_interest(s, P1=2.0, E1=1000000, P2=1.0, E2=5000000, P3=0.5, M=10000000):
    ppm = lambda p: 0 if p <= 0 else (1000000 if p >= 100 else int(round(p * 10000)))
    e1 = min(E1, M); e2 = min(max(E2, e1), M)
    p1 = min(s, e1); p2 = 0 if s <= e1 else min(s, e2) - e1; p3 = 0 if s <= e2 else min(s, M) - e2
    return (p1 * ppm(P1) + p2 * ppm(P2) + p3 * ppm(P3)) // 1000000


def ref_split(g, b, s):
    n = len(b)
    sh, rem = [0] * n, [-1] * n
    if g <= 0 or s <= 0:
        return sh
    given = 0
    for i in range(n):
        if b[i] <= 0:
            continue
        sh[i], rem[i] = divmod(g * b[i], s)
        given += sh[i]
    left = g - given
    while left > 0:
        best = -1
        for i in range(n):
            if rem[i] >= 0 and (best < 0 or rem[i] > rem[best]):
                best = i
        if best < 0:
            break
        sh[best] += 1
        rem[best] = -1
        left -= 1
    return sh


CAPS = [50000, 100000, 250000, 500000, 1000000, 2000000, 3500000, 5000000, 7500000, 10000000]
MULS = [50, 55, 60, 66, 72, 78, 84, 90, 95, 100]
COSTS = [25000, 75000, 150000, 300000, 600000, 1000000, 1500000, 2500000, 4000000]


def ref_day(bals, lvs):
    eff = [min(b, CAPS[l - 1]) for b, l in zip(bals, lvs)]
    s = sum(eff)
    sh = ref_split(ref_interest(s), eff, s)
    return [x * MULS[l - 1] // 100 for x, l in zip(sh, lvs)]


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    W = T9.World()
    Long, Bool, Int = JClass("java.lang.Long"), JClass("java.lang.Boolean"), JClass("java.lang.Integer")
    home = os.path.join(scratch, "x")
    N = T9.Bank(jar, home)
    S, C = N.S, N.C
    J = lambda n: JClass(PKG + n, loader=N.L)
    S.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyBank")
    # ---------------- CONFIG
    C.load()
    t = open(os.path.join(home, "config.properties"), encoding="latin-1").read()
    K.check("levels.enabled=true" in t and "level.capacity=50000,100000," in t and "level.interest=50,55," in t and "level.cost=25000,75000," in t, "CONFIG a fresh file lists the level rows")
    K.eq([int(x) for x in C.caps()], CAPS, "CONFIG caps")
    K.eq([int(x) for x in C.mults()], MULS, "CONFIG interest percents")
    K.eq([int(x) for x in C.costs()], COSTS, "CONFIG costs")
    K.eq(int(C.maxLevel()), 10, "CONFIG 10 levels")
    K.eq([int(C.lvCap(x)) for x in (0, 1, 10, 11)], [50000, 50000, 10000000, 10000000], "CONFIG lvCap clamps the level")
    K.eq([int(C.lvCost(x)) for x in (1, 9, 10)], [25000, 4000000, 4000000], "CONFIG lvCost")
    K.check(C.checkLevels("level.capacity", "100,50") is not None and C.checkLevels("level.capacity", "a,b") is not None and C.checkLevels("level.capacity", "100000,200000") is None, "CONFIG capacity must rise, numbers only")
    # fix (critic 1 #4): a cost above the capacity of the level that pays it is refused (both rows), the defaults fit, a bad file = one WARN
    K.eq(int(C.costOver(C.caps(), C.costs())), 0, "FIX4 the default costs fit every level's capacity")
    r4a = C.checkLevels("level.cost", "60000")
    r4b = C.checkLevels("level.capacity", "100,200")
    r4c = C.checkLevels("level.cost", "25000,100001")
    K.check(r4a is not None and "Bank Lv 1 holds only 50,000" in str(r4a) and r4b is not None and "Lv 1 must hold at least 25,000" in str(r4b)
            and r4c is not None and "Lv 3 would cost 100,001" in str(r4c), "FIX4 cost > capacity refused: %s | %s | %s" % (r4a, r4b, r4c))
    K.check(C.checkLevels("level.cost", "0,0") is None and C.checkLevels("level.cost", "50000,100000") is None, "FIX4 costs up to the capacity (and free levels) pass")
    _w0 = len([x for x in C.LV_WARNED.keySet() if str(x).startswith("costOver=")])
    C.LV_COST = "60000"
    C.costWarn(); C.costWarn()
    _w1 = len([x for x in C.LV_WARNED.keySet() if str(x).startswith("costOver=")])
    K.check(_w1 == _w0 + 1 and int(C.lvCost(1)) == 60000, "FIX4 a file cost above the capacity: used as typed + ONE warn (%d -> %d)" % (_w0, _w1))
    C.LV_COST = ",".join(str(x) for x in COSTS)
    K.check(C.check("level.capacity", ",".join(["5"] * 21)) is not None and C.check("level.interest", "50,2000") is not None and C.check("level.cost", "1,-2") is not None, "CONFIG check= refuses 21 levels / 2000 % / a negative cost")
    K.check(C.check("level.interest", "100") is None and C.check("bracket1Coins", "1000") is None, "CONFIG good values pass (and the old keys still go through)")
    K.eq(str(C.bracketTextLv(1)), "1% up to 50k", "CONFIG Lv 1 brackets: 2% x 50% up to the 50k capacity")
    K.eq(str(C.bracketTextLv(7)), "1.68% up to 1M, 0.84% up to 3.5M", "CONFIG Lv 7 brackets")
    K.eq(str(C.bracketTextLv(10)), "2% up to 1M, 1% up to 5M, 0.5% up to 10M", "CONFIG Lv 10 = the brackets as set")
    open(os.path.join(home, "config.properties"), "a", encoding="latin-1").write("level.capacity=10,5\n")
    C.load()
    K.eq([int(x) for x in C.caps()], CAPS, "CONFIG a falling capacity list in the file = the default (+ one WARN)")
    C.LV_CAP = "100,200,300"
    K.eq(int(C.maxLevel()), 3, "CONFIG a kit edit of the field is used at once (3 levels)")
    C.LV_CAP = ",".join(str(x) for x in CAPS)
    # ---------------- CAP
    u = W.u(1)
    k = str(u)
    W.PURSE["new"][k] = 200000
    T9.write_acc(home, k, 40000)
    S.LOADED.clear(); S.BAL.clear()
    purse = lambda: W.PURSE["new"].get(k, 0)
    K.eq(int(S.levelOf(k)), 1, "CAP a bank without a level line = Lv 1")
    K.eq(int(S.deposit(u, 20000)), 8, "CAP 20,000 into 40,000 / 50,000 = more than the room (8)")
    K.check(purse() == 200000 and int(S.getKey(k)) == 40000, "CAP ... refused before the purse was touched")
    K.eq(int(S.deposit(u, 10000)), 1, "CAP exactly the room (10,000) goes in")
    K.eq(int(S.deposit(u, 1)), 7, "CAP a full bank refuses 1 coin (7)")
    K.check(purse() == 190000 and int(S.getKey(k)) == 50000, "CAP purse 190,000, bank 50,000")
    r = str(J("BankCmd").move(u, True, "all"))
    K.check(r.startswith("-Your bank is full") and purse() == 190000, "CAP Deposit all on a full bank: %s" % r)
    K.eq(int(S.withdraw(u, 5000)), 1, "CAP withdraw 5,000")
    r = str(J("BankCmd").move(u, True, "all"))
    K.check(r.startswith("+Deposited 5000 coins - the bank is full now") and purse() == 190000 and int(S.getKey(k)) == 50000, "CAP Deposit all fills to the cap, the rest stays in the purse: %s" % r)
    r = str(J("BankCmd").move(u, True, "2k"))
    K.check(r.startswith("-Your bank is full"), "CAP a typed amount into a full bank: %s" % r)
    S.withdraw(u, 1000)
    r = str(J("BankCmd").move(u, True, "5k"))
    K.check(r.startswith("-Your bank has room for only 1,000 more coins (Bank Lv 1 holds 50,000)"), "CAP the room line: %s" % r)
    # above the cap (an old balance): kept, withdraws work, no deposit
    k2 = str(W.u(2))
    T9.write_acc(home, k2, 900000)
    W.PURSE["new"][k2] = 1000
    K.eq(int(S.deposit(W.u(2), 1)), 7, "CAP a balance above the cap (900,000 at Lv 1): no new deposit")
    K.check(int(S.getKey(k2)) == 900000 and int(S.withdraw(W.u(2), 100)) == 1 and int(S.getKey(k2)) == 899900, "CAP ... kept, and a withdraw works")
    # the cap re-checked under the lock: the room check passes, then another credit fills the bank before ours
    k3 = str(W.u(3))
    T9.write_acc(home, k3, 0)
    W.PURSE["new"][k3] = 100000
    fired = [False]

    def hook(op, uu, n):
        if op == "take" and str(uu) == k3 and not fired[0]:
            fired[0] = True
            S.creditK(k3, 45000)          # another path filled the bank meanwhile
    W.HOOK[0] = hook
    rc = int(S.deposit(W.u(3), 10000))
    W.HOOK[0] = None
    K.check(rc == 7 and int(S.getKey(k3)) == 45000 and W.PURSE["new"][k3] == 100000, "CAP the credit re-checks the cap under the lock: 7, the coins back in the purse (%d, bank %d, purse %d)" % (rc, int(S.getKey(k3)), W.PURSE["new"][k3]))
    # fix (critic 1 #2): the cap re-check fails AND the profile switched during the purse call -> booked on the START profile past the
    # cap (2), never refunded into the NEW profile's purse
    u7 = W.u(7)
    k7 = str(u7)
    T9.write_acc(home, k7, 45000)
    W.PURSE["new"][k7] = 100000
    W.PURSE["new"][k7 + "-p2"] = 10000
    ev7 = []

    def hook7(op, uu, n):
        if str(uu) != k7:
            return
        ev7.append(op)
        if op == "take" and ev7.count("take") == 1:
            S.creditK(k7, 3000)           # another path fills the bank (45,000 + 3,000: no room for 4,000 any more)
            W.PROF[k7] = 2                # ... and the profile switches during the purse call
    W.HOOK[0] = hook7
    rc7 = int(S.deposit(u7, 4000))
    W.HOOK[0] = None
    W.PROF[k7] = 1
    tot7 = int(S.getKey(k7)) + W.PURSE["new"][k7] + W.PURSE["new"][k7 + "-p2"]
    K.check(rc7 == 2 and int(S.getKey(k7)) == 52000 and "add" not in ev7 and tot7 == 45000 + 3000 + 100000 + 10000,
            "FIX2 cap race + profile switch: booked on the start profile past the cap, no refund into the new profile's purse (rc %d, bank %d, purses %d / %d, calls %s)" % (rc7, int(S.getKey(k7)), W.PURSE["new"][k7], W.PURSE["new"][k7 + "-p2"], ev7))
    K.eq(int(S.deposit(u7, 1)), 7, "FIX2 ... the bank above the cap takes no new deposit")
    # 8 threads depositing at once never pass the cap
    k4 = str(W.u(4))
    T9.write_acc(home, k4, 0)
    W.PURSE["new"][k4] = 1000000
    ths = [T9.run_bg(lambda: int(S.deposit(W.u(4), 7000))) for _i in range(8)]
    rs = []
    for th, box in ths:
        th.join(30)
        rs.append(box.get("r"))
    K.check(int(S.getKey(k4)) <= 50000 and int(S.getKey(k4)) + W.PURSE["new"][k4] == 1000000 and rs.count(1) == int(S.getKey(k4)) // 7000, "CAP 8 threads x 7,000: bank %d <= 50,000, no coin lost (%s)" % (int(S.getKey(k4)), rs))
    # levels off: no cap
    C.LV_ON = False
    K.eq(int(S.deposit(W.u(4), 100000)), 1, "CAP levels off: no cap (0.1.16)")
    S.withdraw(W.u(4), 100000)
    C.LV_ON = True
    # ---------------- UPG
    k5u = W.u(5)
    k5 = str(k5u)
    T9.write_acc(home, k5, 10000)
    W.PURSE["new"][k5] = 0
    e = S.epoch(k5u)
    r = str(S.upgrade(k5u, k5, e, 1))
    K.check(r.startswith("-Bank Lv 2 costs 25,000 coins from your bank - it holds 10,000") and int(S.getKey(k5)) == 10000 and int(S.levelOf(k5)) == 1, "UPG not enough in the bank: nothing (%s)" % r)
    S.creditK(k5, 40000)
    r = str(S.upgrade(k5u, k5, e, 1))
    K.check(r.startswith("+Bank upgraded to Lv 2 for 25,000 coins") and int(S.getKey(k5)) == 25000 and int(S.levelOf(k5)) == 2, "UPG Lv 1 -> 2: bank 50,000 -> 25,000 (%s)" % r)
    acc = open(os.path.join(home, "accounts", k5 + ".properties"), encoding="latin-1").read()
    mir = open(os.path.join(home, "levels", k5 + ".properties"), encoding="latin-1").read()
    K.check("bank.level=2" in acc and "balance=25000" in acc and "level=2" in mir, "UPG the account file has balance + bank.level, the mirror has level=2")
    r = str(S.upgrade(k5u, k5, e, 1))
    K.check(r.startswith("=Your bank is already Lv 2") and int(S.getKey(k5)) == 25000, "UPG the same expected level again (double click): nothing (%s)" % r)
    K.eq(int(S.capK(k5)), 100000, "UPG Lv 2 holds 100,000")
    W.PROF[k5] = 2
    r = str(S.upgrade(k5u, k5, e, 2))
    K.check(r.startswith("=Your profile changed") and int(S.getKey(k5)) == 25000, "UPG a profile switch since the page: nothing (%s)" % r)
    W.PROF[k5] = 1

    @JImplements("java.util.function.Function")
    class Busy:
        @JOverride
        def apply(self, kk):
            return Bool.TRUE
    W.BR.put("rebirth:fn:busy", Busy())
    r = str(S.upgrade(k5u, k5, e, 2))
    K.check(r.startswith("-A rebirth is finishing") and int(S.getKey(k5)) == 25000, "UPG refused while a rebirth runs (%s)" % r)
    W.BR.remove("rebirth:fn:busy")
    # a failed write changes nothing (the .tmp path is a folder)
    S.creditK(k5, 75000)
    tmpd = os.path.join(home, "accounts", k5 + ".properties.tmp")
    os.makedirs(tmpd)
    r = str(S.upgrade(k5u, k5, e, 2))
    K.check(r.startswith("-The bank could not be saved") and int(S.getKey(k5)) == 100000 and int(S.levelOf(k5)) == 2, "UPG a failed write: nothing changed (%s)" % r)
    os.rmdir(tmpd)
    # 8 threads, the same click: exactly one level
    ths = [T9.run_bg(lambda: str(S.upgrade(k5u, k5, e, 2))) for _i in range(8)]
    rs = []
    for th, box in ths:
        th.join(30)
        rs.append(box.get("r") or "")
    K.check(sum(1 for x in rs if x.startswith("+")) == 1 and int(S.levelOf(k5)) == 3 and int(S.getKey(k5)) == 25000, "UPG 8 threads x the same upgrade click: exactly one level (bank %d, Lv %d)" % (int(S.getKey(k5)), int(S.levelOf(k5))))
    S.LVL.put(k5, Int.valueOf(10))
    r = str(S.upgrade(k5u, k5, e, 10))
    K.check(r.startswith("=Your bank is at the top level") and int(S.getKey(k5)) == 25000, "UPG the top level: nothing (%s)" % r)
    S.LVL.put(k5, Int.valueOf(3))
    S.setKey(k5, 25000)
    # deposits + upgrades (any level) + withdraws on 6 threads: no coin created or lost
    k6u = W.u(6)
    k6 = str(k6u)
    T9.write_acc(home, k6, 50000)
    W.PURSE["new"][k6] = 3000000
    start_total = 3050000
    spent = [0]
    sl = threading.Lock()
    rnd = random.Random(17)

    def worker(seed):
        rr = random.Random(seed)
        for _j in range(60):
            op = rr.randint(0, 2)
            if op == 0:
                S.deposit(k6u, rr.randint(1, 120000))
            elif op == 1:
                S.withdraw(k6u, rr.randint(1, 60000))
            else:
                lv = int(S.levelOf(k6))
                cost = int(C.lvCost(lv)) if lv < 10 else 0
                res = str(S.upgrade(k6u, k6, S.epoch(k6u), lv))
                if res.startswith("+"):
                    with sl:
                        spent[0] += cost
    ths = [T9.run_bg(lambda s_=s_: worker(s_)) for s_ in range(6)]
    for th, _b in ths:
        th.join(120)
    tot = int(S.getKey(k6)) + W.PURSE["new"][k6] + spent[0]
    K.check(tot == start_total and int(S.getKey(k6)) <= int(S.capK(k6)), "UPG 6 threads of deposits / withdraws / upgrades: purse + bank + spent = %d (start %d), Lv %d, bank %d <= cap" % (tot, start_total, int(S.levelOf(k6)), int(S.getKey(k6))))
    acc6 = open(os.path.join(home, "accounts", k6 + ".properties"), encoding="latin-1").read()
    K.check(("balance=%d" % int(S.getKey(k6))) in acc6 and (int(S.levelOf(k6)) == 1 or ("bank.level=%d" % int(S.levelOf(k6))) in acc6), "UPG the file holds the final balance + level")
    # ---------------- LOAD (restart, the real 0.1.16, the mirror)
    N2 = T9.Bank(jar, home)
    N2.S.LOG = S.LOG
    N2.C.load()
    K.check(int(N2.S.levelOf(k5)) == 3 and int(N2.S.getKey(k5)) == 25000, "LOAD a restart reads Lv 3 + the balance")
    O = T9.Bank(OLD_JAR, home)
    O.C.load()
    O.S.creditK(k5, 1)                       # 0.1.16 rewrites the account file without bank.level
    acc = open(os.path.join(home, "accounts", k5 + ".properties"), encoding="latin-1").read()
    K.check("bank.level" not in acc and "balance=25001" in acc, "LOAD the REAL 0.1.16 writes the account without bank.level (rollback)")
    N3 = T9.Bank(jar, home)
    N3.S.LOG = S.LOG
    N3.C.load()
    K.check(int(N3.S.levelOf(k5)) == 3 and int(N3.S.getKey(k5)) == 25001, "LOAD 0.1.17 again: Lv 3 from the levels/ mirror, the coins 0.1.16 added kept")
    N3.S.creditK(k5, 1)
    K.check("bank.level=3" in open(os.path.join(home, "accounts", k5 + ".properties"), encoding="latin-1").read(), "LOAD ... and the next write puts bank.level back")
    # fix (critic 1 #3): the account file's own line wins over the mirror (an admin lowers a level); no account file = no level back
    accp = os.path.join(home, "accounts", k5 + ".properties")
    _save5 = open(accp, "rb").read()
    open(accp, "wb").write(_save5.replace(b"bank.level=3", b"bank.level=2"))
    N4 = T9.Bank(jar, home)
    N4.S.LOG = S.LOG
    N4.C.load()
    K.eq(int(N4.S.levelOf(k5)), 2, "FIX3 an admin lowers bank.level in the account file (3 -> 2): the file wins over the mirror (level=3)")
    open(accp, "wb").write(_save5.replace(b"bank.level=3", b"bank.level=1"))
    N4 = T9.Bank(jar, home)
    N4.S.LOG = S.LOG
    N4.C.load()
    K.eq(int(N4.S.levelOf(k5)), 1, "FIX3 bank.level=1 in the file = Lv 1 (the mirror ignored)")
    os.remove(accp)
    N4 = T9.Bank(jar, home)
    N4.S.LOG = S.LOG
    N4.C.load()
    K.check(int(N4.S.levelOf(k5)) == 1 and int(N4.S.getKey(k5)) == 0 and os.path.isfile(os.path.join(home, "levels", k5 + ".properties")),
            "FIX3 an account file deleted by an admin: Lv 1, 0 coins - the stale mirror gives no level back")
    open(accp, "wb").write(_save5)
    rx = JClass("java.util.Properties")()
    rx.setProperty("rb.bonus", "0.5")
    N3.S.rbWrite0(k5, 25002, rx)
    K.check("bank.level=3" in open(os.path.join(home, "accounts", k5 + ".properties"), encoding="latin-1").read(), "LOAD rbWrite0 (the rebirth commit) keeps bank.level")
    # ---------------- PAY: a reference on random groups
    ph = os.path.join(scratch, "pay")
    rnd = random.Random(1717)
    bad = []
    for trial in range(400):
        if os.path.isdir(ph):
            shutil.rmtree(ph)
        n = rnd.randint(1, 4)
        uu = W.u(100 + trial)
        keys = [str(uu)] + ["%s-p%d" % (uu, i) for i in range(2, n + 1)]
        bals = [rnd.choice([0, rnd.randint(0, 60000), rnd.randint(0, 3000000), rnd.randint(0, 12000000)]) for _i in range(n)]
        lvs = [rnd.randint(1, 10) for _i in range(n)]
        for kk, b, lv in zip(keys, bals, lvs):
            T9.write_acc(ph, kk, b, "bank.level=%d\r\n" % lv if lv > 1 else "")
        Bp = T9.Bank(jar, ph)
        Bp.C.load()
        want = ref_day(bals, lvs)
        ks = sorted(keys)
        order = [keys.index(x) for x in ks]
        gs = JClass("java.lang.Object[]")(1) if False else None
        arr = JClass("java.lang.reflect.Array").newInstance(JClass("java.lang.String"), len(ks))
        for i, x in enumerate(ks):
            arr[i] = x
        prev = JClass("java.lang.reflect.Array").newInstance(JClass("java.lang.Long").TYPE, len(ks))
        pays = JClass("java.lang.reflect.Array").newInstance(JClass("java.lang.Boolean").TYPE, len(ks))
        for x in ks:
            Bp.S.ready(x)
        last = 1000 * DAY
        got = [int(v) for v in Bp.S.planGroup(arr, last, last + DAY, DAY, 1, prev, pays)]
        wantk = [want[i] for i in order]
        if got != wantk:
            bad.append((bals, lvs, got, wantk))
        W.PROF[str(uu)] = 1
        ng = int(Bp.S.nextGain(uu))
        if ng != want[0]:
            bad.append(("nextGain", bals, lvs, ng, want[0]))
    K.check(not bad, "PAY planGroup + nextGain = the Python reference on 400 random groups (capped sum + split, x level %%): %s" % bad[:2])
    # payAll on one group, interest past the cap kept, paid once
    if os.path.isdir(ph):
        shutil.rmtree(ph)
    uu = W.u(900)
    T9.write_acc(ph, str(uu), 49900)
    Bp = T9.Bank(jar, ph)
    Bp.C.load()
    gs = JClass("java.lang.reflect.Array").newInstance(JClass("java.lang.Object"), 1)
    one = JClass("java.lang.reflect.Array").newInstance(JClass("java.lang.String"), 1)
    one[0] = str(uu)
    gs[0] = one
    Bp.S.payAll(gs, 1000 * DAY, 1001 * DAY, DAY, 1)
    K.eq(int(Bp.S.getKey(str(uu))), 49900 + 499, "PAY payAll: 49,900 at Lv 1 earns 1% = 499 -> 50,399 (past the cap, kept)")
    Bp.S.payAll(gs, 1000 * DAY, 1001 * DAY, DAY, 1)
    K.eq(int(Bp.S.getKey(str(uu))), 50399, "PAY the same payout again pays nothing")
    K.eq(int(Bp.S.nextGain(uu)), 500, "PAY next: only the 50,000 under the cap earns (500)")
    # levels off = the REAL 0.1.16 numbers on the same files
    if os.path.isdir(ph):
        shutil.rmtree(ph)
    same = True
    for trial in range(60):
        uu = W.u(2000 + trial)
        n = rnd.randint(1, 3)
        for i in range(n):
            T9.write_acc(ph, str(uu) if i == 0 else "%s-p%d" % (uu, i + 1), rnd.randint(0, 12000000), "bank.level=%d\r\n" % rnd.randint(2, 10))
    Bn = T9.Bank(jar, ph)
    Bn.C.load()
    Bn.C.LV_ON = False
    Bo = T9.Bank(OLD_JAR, ph)
    Bo.C.load()
    for trial in range(60):
        uu = W.u(2000 + trial)
        if int(Bn.S.nextGain(uu)) != int(Bo.S.nextGain(uu)):
            same = False
    K.check(same, "PAY levels off: nextGain = the REAL 0.1.16's on 60 accounts with levels in their files")
    # ---------------- PANEL + the bridge
    PF = J("BankPanelFn")
    PF.register()
    pan = W.BR.get("bank:fn:panel").apply(k5u)
    K.check(len(pan) == 13 and str(pan[0]) == "ok" and "Bank Lv 3 of 10: holds up to 250,000 coins, 1.2% interest. Upgrade to Lv 4: holds 500,000, 1.32%, costs 150,000 coins from the bank." in str(pan[10]) and int(pan[11]) == 3 and bool(pan[12]), "PANEL [10] level line / [11] Lv 3 / [12] more to buy: %s" % str(pan[10]))
    K.check("at Bank Lv 3: 1.2% up to 250k" in str(pan[4]), "PANEL [4] the rate line of the level: %s" % pan[4])
    S.creditK(k5, 200000)
    mv = W.BR.get("bank:fn:move")
    ObjA = lambda xs: JClass("java.lang.reflect.Array").newInstance(JClass("java.lang.Object"), 0) if not xs else _arr(xs)

    def _arr(xs):
        a = JClass("java.lang.reflect.Array").newInstance(JClass("java.lang.Object"), len(xs))
        for i, x in enumerate(xs):
            a[i] = x
        return a
    b0 = int(S.getKey(k5))
    r1 = str(mv.apply(_arr([k5u, "upgrade", "3", pan[8], pan[9]])))
    r2 = str(mv.apply(_arr([k5u, "upgrade", "3", pan[8], pan[9]])))
    K.check(r1.startswith("+Bank upgraded to Lv 4") and r2.startswith("=Your bank is already Lv 4") and int(S.getKey(k5)) == b0 - 150000, "PANEL bank:fn:move upgrade twice with the panel's level: one level (%s | %s)" % (r1[:40], r2[:40]))
    r3 = str(mv.apply(_arr([k5u, "upgrade", "", pan[8], pan[9]])))
    K.check(r3.startswith("=This page did not know your bank level") and int(S.getKey(k5)) == b0 - 150000, "PANEL an upgrade without the level: nothing (%s)" % r3[:50])
    lf = W.BR.get("bank:fn:level")
    k5p2 = k5 + "-p2"
    T9.write_acc(home, k5p2, 0, "bank.level=7\r\n")
    K.eq(int(lf.apply(k5u)), 7, "PANEL bank:fn:level = the best level of all profiles (p2 at Lv 7)")
    K.eq(int(lf.apply(W.u(77))), 1, "PANEL bank:fn:level of a player without a bank = 1")
    C.LV_ON = False
    K.check(lf.apply(k5u) is None and str(W.BR.get("bank:fn:panel").apply(k5u)[11]) == "None", "PANEL levels off: bank:fn:level null, no level in the panel")
    C.LV_ON = True
    K.eq(str(S.levelLine(str(W.u(77)))), "Bank Lv 1 of 10: holds up to 50,000 coins, 1% interest. Upgrade to Lv 2: holds 100,000, 1.1%, costs 25,000 coins from the bank.", "PANEL the Lv 1 line")
    PF.unregister()
    K.check(W.BR.get("bank:fn:level") is None and W.BR.get("bank:fn:panel") is None, "PANEL unregister removes our three Functions")
    K.save()


def run_page17(out, jar, scratch, _home):
    """the fallback /bank page through the engine (tools/hub_tab_harness.py + test_skyybank_0.1.16's kit 1.7 page check)"""
    import jpype
    from jpype import JClass, JImplements, JOverride
    T16 = tmod("test_skyybank_0.1.16.py", "tb0116_for17")
    os.environ["SKYY_HARNESS_CP"] = CORE_JAR
    H = T16.H
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
    T16.T14.prep(E, J, home)
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
    P = W.P
    E.br.put("hub:last:" + str(P.pr.getUuid()), JClass("java.util.concurrent.ConcurrentHashMap")())
    u = P.pr.getUuid()
    T9.write_acc(home, str(u), 10000)
    PURSE[str(u)] = 200000
    K.eq(int(J("BankHubOpen").register()), 1, "PAGE17 the Bank tab is put (no SkyyVault)")
    r = str(HB.open(P.pr, u, "storage", "bank"))
    E.pump(P)
    pg = P.pm.getCustomPage()
    K.check(pg is not None and str(pg.getClass().getSimpleName()) == "BankPage", "PAGE17 the bank page opens (%s)" % r)
    cm, ev = T16.page_check17(K, E, T16.S, P, pg, HB, "PAGE17 bank page (Lv 1)")
    K.check(any(s == "#SkyyBUpgrade" and "upgrade" in t for s, t in ev), "PAGE17 Upgrade bank is bound")
    strs = " ".join(str(d) for ty, s, t, d in cm if ty == "Set")
    K.check("Bank Lv 1 of 10" in strs and "Upgrade to Lv 2" in strs, "PAGE17 the level line is on the page")
    bank = lambda: int(J("BankStore").get(u))

    def click(a, amt, tok):
        d = {"a": a, "@BAmount": amt}
        if tok is not None:
            d["t"] = tok
        P.pm.handleLegacyCustomPageEvent(P.ref, P.st, E.CPE(E.CPT.Data, json.dumps(d)))
        E.pump(P)
        return P.pm.getCustomPage()
    p2 = click("upgrade", "", str(pg.tok))
    K.check(bank() == 10000 and str(p2.info).startswith("-Bank Lv 2 costs 25,000"), "PAGE17 Upgrade with 10,000 in the bank: nothing (%s)" % p2.info)
    p2 = click("deposit", "20000", str(p2.tok))
    tok = str(p2.tok)
    p2 = click("upgrade", "", tok)
    K.check(bank() == 5000 and int(J("BankStore").levelOf(str(u))) == 2 and str(p2.info).startswith("+Bank upgraded to Lv 2"), "PAGE17 Upgrade: Lv 2 for 25,000 (bank 30,000 -> 5,000): %s" % p2.info)
    p2 = click("upgrade", "", tok)
    K.check(bank() == 5000 and int(J("BankStore").levelOf(str(u))) == 2, "PAGE17 the same click again (used-up token): nothing (%s)" % p2.info)
    p2 = click("deposit", "90000", str(p2.tok))
    K.check(bank() == 95000 and str(p2.info).startswith("+"), "PAGE17 Lv 2 takes up to 100,000: %s" % p2.info)
    p2 = click("deposit", "10000", str(p2.tok))
    K.check(bank() == 95000 and str(p2.info).startswith("-Your bank has room for only 5,000"), "PAGE17 over the cap refused: %s" % p2.info)
    p2 = click("upgrade", "", str(p2.tok))
    K.check(bank() == 20000 and int(J("BankStore").levelOf(str(u))) == 3, "PAGE17 the next click (new token) buys Lv 3: %s" % p2.info)
    T16.page_check17(K, E, T16.S, P, p2, HB, "PAGE17 bank page (Lv 3)")
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
            lv = dict((k, int(Jb.S.levelOf(k))) for k in ks) if tag == "new" else {}
            a0 = HK.tree_hash(d)
            res[(start, tag)] = [sorted(k for k in set(b0) | set(a0) if b0.get(k) != a0.get(k)), bals, lv]
            if tag == "new":
                K.notes.append("LIVE start %d: %s" % (start, "; ".join("%s bank %d Lv %d next %d" % (k[-6:], bals[k][0], lv[k], int(Jb.S.nextGain(Jb.S.owner(k))) if Jb.S.owner(k) is not None and str(Jb.S.pkey(Jb.S.owner(k))) == k else -1) for k in ks)))
        K.eq(res[(start, "new")][1], res[(start, "old")][1], "LIVE start %d: every account reads the same balance as the REAL 0.1.16 (%d accounts)" % (start, len(res[(start, "new")][1])))
        K.eq(res[(start, "new")][0], res[(start, "old")][0], "LIVE start %d: 0.1.17 changes exactly the files 0.1.16 changes (%s)" % (start, res[(start, "old")][0]))
        K.check(all(v == 1 for v in res[(start, "new")][2].values()), "LIVE start %d: every live account is Lv 1" % start)
    K.eq(res[(2, "new")][0], [], "LIVE the second start changes nothing")
    K.check(all(v[0] <= 50000 for v in res[(1, "new")][1].values()), "LIVE every live balance fits the Lv 1 cap (50,000) - nobody is over it")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyBank", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("static", run_static), ("exec", run_exec), ("page17", run_page17), ("live", run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyBank"))
