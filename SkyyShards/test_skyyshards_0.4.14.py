"""Harness for SkyyShards 0.4.14 (LOCK DISCIPLINE: no other mod is called while ShStore.LOCK is held; the Collect credits reserved before
they are paid; tools/shards_0_4_14_patch.py, on top of 0.4.13).
Build first:
    python tools/shards_0_4_14_patch.py && python SkyyShards/build_skyyshards_0.4.14.py
    python SkyyShards/test_skyyshards_0.4.14.py [--keep]

  S    static   the patch re-runs to identical bytes; header / VERSION / ready line; no new registerSystem / registerCommand; the STATIC
                lock audit: no call inside any ShStore.LOCK region reaches a bridge (the call graph of every method; moonBlade + essence
                read only their caches under the lock); nothing of ours on HytaleServer.SCHEDULED_EXECUTOR (queue item 4)
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.4.13 -> 0.4.14: exactly the planned members differ (EXPECT); every non-class file identical
  NL   no lock  EXECUTED: every action that talks to another mod - Storage / Compactor / Compressor, sub-upgrade, Grow, island, Automation,
                Offline Harvest, Add modifier, Add booster, a placed totem's Tier up, Bench upgrade, Craft (a totem + a shard), placing a
                shard (decide, incl. a stale record), shard:fn:door (incl. a stale record), Collect (owed / owedXp), grant, the Combat
                Totems tab (SkyyArmory's essence) - with EVERY bridge stand-in recording whether ShStore.LOCK was held: never; ShCfg.UNDER 0
  CB   commit   EXECUTED for purchase / purchaseM / Add modifier / Add booster / Tier up / Bench upgrade / Craft shard: (a) another thread
                takes the lock while we pay (inside the bag take) -> the commit meets a busy lock -> EVERYTHING back (inventory, bags,
                coins, the record) and the click says busy; (b) the profile / the totem changes while we pay -> everything back, "changed";
                (c) then it goes through
  OW   owed     EXECUTED (the re-review LOW): busy after paying + a RESTART -> the credit is paid exactly once; a refused credit + a busy
                write-back -> memory -> flushOwed moves it into the file -> a restart pays it once; a busy flush keeps it; a refused
                reserve save keeps the file part (paid later, once); memAdd from two threads at once adds up exactly; ShTick flushes
  EX   executor ShTick + the flush run on SkyyShards-tick (our own daemon thread), never the shared scheduler
  FX   fixer    EXECUTED (critics 10-27): the reserve writes RESERVED and the payment PAID to collect.log (an admin sees a crash's lost
                credit); flushOwed skips an unreadable collector file for a minute, then tries again; a Combat essence is asked from
                SkyyArmory once a minute per tier (a new bridge function / an old entry = asked again); Enter Shard's world-load callback
                (ShHop.accept) on a non-world thread with the shard lock HELD elsewhere returns at once - no profile read, no lock - and only
                queues the paint step on the SHARD world; that step (a world thread) reads the profile, paints, then queues the teleport on
                the player's world; a busy lock there = no teleport queued
  FX2  fixer 2  (re-critics 10-27) the paint step with the profile CACHED and the lock busy through ShFill.region = still no teleport
                (pressed again = paints + teleports); owed / owedXp with SkyyCollections / SkyySkills absent = no reserve, the file keeps
                its credit (one save, no RESERVED / PAID); once the mods are back the next Collect pays it exactly once
  413  every 0.4.13 harness phase on the 0.4.14 jar (and through it 0.4.12 ... 0.4.6) - the BZ checks 0.4.14 replaces on purpose are
       superseded (busy at the commit now = everything back + a "busy" answer instead of a thrown ShBusy; owed no longer keeps the file
       part on disk while paying it); after each in-process phase ShCfg.UNDER is checked (0 unless that phase holds the lock itself)
  D    live     START TWICE on a scratch COPY of NewBetaTest's Skyy_SkyyShards
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util, subprocess, json, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.4.14"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "shlockfix2", "h")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyShards-%s.jar" % VERSION)]
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyShards-0.4.13.jar")
GEN = os.path.join(HERE, "build_skyyshards_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyshards_0.4.13.py")
PATCH = os.path.join(ROOT, "tools", "shards_0_4_14_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.shards."
_argv = list(sys.argv)
_spec = importlib.util.spec_from_file_location("test_skyyshards_0_4_13", os.path.join(HERE, "test_skyyshards_0.4.13.py"))
T413 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T413)
sys.argv[:] = _argv
T413.JAR = JAR
T413.GEN = GEN           # its static string checks (BZ 7) read THIS generated script
T412 = T413.T412
T412.JAR = JAR
T411 = T413.T411
T410, T49, T48, T46 = T411.T410, T411.T49, T411.T48, T411.T46
for _m in (T411, T410, T49, T48, T46, T411.T47):
    _m.JAR = JAR
OWNER, MEMBER = T49.OWNER, T49.MEMBER
FK = 2
CK = 5
SUP = T49._superseded


# ---------------------------------------------------------------------------------------------------------- the static lock audit
def lock_audit(src):
    """[(method, line, [tainted callee chains])] for every ShStore.LOCK region of the generated script whose calls reach a bridge"""
    cls = dict(re.findall(r'^(\w+) = mk\("(\w+)"', src, re.M))
    meths = []
    for m in re.finditer(r'^M\((\w+), r"""(.*?)"""', src, re.M | re.S):
        meths.append((cls.get(m.group(1), m.group(1)), m.group(2), m.start()))
    for m in re.finditer(r'^M\((\w+), "(.*?)"\)', src, re.M):
        meths.append((cls.get(m.group(1), m.group(1)), m.group(2), m.start()))

    def mname(body):
        mm = re.search(r'(\w+)\s*\(', body.strip().split("{")[0])
        return mm.group(1) if mm else "?"
    M = {}
    for c, b, p in meths:
        M.setdefault((c, mname(b)), []).append((b, p))
    BR = re.compile(r'(ShCfg\.fn\(|\bfn\("|\bf\("|fnT\(|bridge\(\)\.get)')
    SAFE = ("fn", "f", "fnT", "under", "bridge", "bridge0", "moonBlade", "essence")   # moonBlade / essence: cache only under the lock
    taint = {}
    for k, v in M.items():
        if k[1] in SAFE:
            continue
        for b, p in v:
            if BR.search(b):
                taint[k] = "direct"
    callre = re.compile(r'(?:@PKG@\.(Sh\w+)\.)?(\w+)\s*\(')

    def calls(c, b):
        out = set()
        for mm in callre.finditer(b):
            cc = mm.group(1) or c
            if (cc, mm.group(2)) in M:
                out.add((cc, mm.group(2)))
        return out
    G = dict((k, set().union(*[calls(k[0], b) for b, p in v])) for k, v in M.items())
    ch = True
    while ch:
        ch = False
        for k, cs in G.items():
            if k in taint or k[1] in SAFE:
                continue
            for x in cs:
                if x in taint:
                    taint[k] = x
                    ch = True
                    break

    def chain(k):
        s = []
        while k in taint and taint[k] != "direct":
            s.append("%s.%s" % k)
            k = taint[k]
        s.append("%s.%s" % k)
        return " > ".join(s)
    bad, n = [], 0
    for k, v in M.items():
        for b, p in v:
            i = 0
            while True:
                j = b.find("LOCK.lock()", i)
                if j < 0:
                    break
                n += 1
                t = b.find("try {", j)
                if t < 0 or t - j > 80:
                    t = b.find("{", j)
                d, e = 0, t
                for e in range(t, len(b)):
                    if b[e] == "{":
                        d += 1
                    elif b[e] == "}":
                        d -= 1
                        if d == 0:
                            break
                hit = sorted(chain(x) for x in calls(k[0], b[t:e]) if x in taint)
                if hit:
                    bad.append(("%s.%s" % k, src.count("\n", 0, p) + 1 + b.count("\n", 0, j), hit))
                i = j + 5
    return bad, n


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyShards 0.4.14 - build script') and g.count('VERSION = "0.4.14"\n') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.check("0.4.14: no other mod is called while the shard data lock is held (pay outside, record under it; Collect credits reserved before they are paid); 0.4.13: the totem page" in g,
            "S the ready line names the round (and keeps 0.4.13's)")
    K.check("this.kShown = kShownSig(this.kZ)" in g and g.count("public static long[] payInvBags(") == 1 and "new @PKG@.ShLock()" in g,
            "S kept: the 0.4.10 hotfix, the 0.4.12 payment path, the 0.4.13 timed lock (the safety net)")
    bad, n = lock_audit(g.replace("\r\n", "\n"))
    K.check(n > 60 and not bad, "S the static lock audit: %d ShStore.LOCK regions, none reaches a bridge: %s" % (n, bad[:4]))
    bad0, n0 = lock_audit(o.replace("\r\n", "\n"))
    K.check(len(bad0) >= 15, "S ... (control) the same audit on 0.4.13 finds its %d regions with bridge calls (addMod, buy*, grow0, decide, door, ...)" % len(bad0))
    code = "\n".join(m.group(1) for m in re.finditer(r'^M\(\w+, r"""(.*?)"""', g, re.M | re.S))
    K.check("SCHEDULED_EXECUTOR" not in code and "newSingleThreadScheduledExecutor(new @PKG@.ShThreads())" in g,
            "S EX nothing of ours runs on HytaleServer.SCHEDULED_EXECUTOR (ShTick on its own SkyyShards-tick thread since 0.4.13)")
    K.check("try { @PKG@.ShCore.flushOwed(); }" in g and g.count("@PKG@.ShCore.flushOwed()") == 2, "S the tick + the plugin shutdown flush the waiting Collect credits")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


# ---------------------------------------------------------------------------------------------------------- shared fixture
class _Inf(dict):
    """a bag that holds 1,000,000 of anything not set"""
    def get(self, k, d=0):
        return dict.get(self, k, 1000000)


def _fx(scratch, K):
    """the BZ fixture (owner, Farming shard, bench I) + bags + every bridge stand-in recording a call made while holding ShStore.LOCK"""
    from jpype import JClass, JInt, JLong, JString
    L = T411._L(scratch, K)
    St, Isl, Core, Door, Cfg, Role, Tot = (L[n] for n in ("ShStore", "ShIsl", "ShCore", "ShDoor", "ShCfg", "ShRole", "ShTotem"))
    PyFn, br, fns, UUID = L["PyFn"], L["br"], L["fns"], L["UUID"]
    LOCK = St.LOCK
    held = []

    def wrap(name, f):
        def w(a):
            if bool(LOCK.isHeldByCurrentThread()):
                held.append(name)
            return f.apply(a)
        return PyFn(w)
    bags = T412._bags(L)
    for k_ in ("count", "take", "put", "commit", "all"):
        br.put("sacks:fn:" + k_, wrap("sacks:fn:" + k_, br.get("sacks:fn:" + k_)))
    got = {"coll": 0, "xp": 0, "ok": True, "hook": None}

    def coll_add(a):
        if got["hook"]:
            h, got["hook"] = got["hook"], None
            h()
        if not got["ok"]:
            return L["Bool"].FALSE
        got["coll"] += int(a[2])
        return L["Bool"].TRUE

    def xp_add(a):
        if got["hook"]:
            h, got["hook"] = got["hook"], None
            h()
        if not got["ok"]:
            return L["Bool"].FALSE
        got["xp"] += int(a[2])
        return L["Bool"].TRUE
    fns.put("coll:fn:add", PyFn(coll_add))
    fns.put("skill:fn:addxp", PyFn(xp_add))
    fns.put("rebirth:fn:count", PyFn(lambda k_: JInt(5)))
    it = fns.keySet().iterator()
    ks = []
    while it.hasNext():
        ks.append(str(it.next()))
    for k_ in ks:
        fns.put(k_, wrap(k_, fns.get(k_)))
    W = "skyy-island-" + OWNER
    for o_, nm in ((Role, "OWNER_TEST"), (Role, "ROLE_TEST"), (Role, "ROLEKEY_TEST"), (Role, "WORLD_TEST"), (Cfg, "KEY_TEST")):
        f0 = getattr(o_, nm)
        if f0 is not None:
            setattr(o_, nm, wrap(nm, f0))
    Role.WORLDKEY_TEST = wrap("island:world:key:fn", PyFn(lambda k_: JString(W) if str(k_) == OWNER else None))
    Role.STATE_TEST = wrap("profile:fn:state", PyFn(lambda k_: JString("active")))

    def soul(a):
        try:
            if len(a) == 2 and str(a[0]) == "essence":
                return JString("Ingredient_Test_Essence_T%d" % int(a[1]))
        except TypeError:
            pass
        return JInt(-1)
    Tot.SOUL_TEST = wrap("armory:fn:soulcage", PyFn(soul))
    Tot.MOON_TEST = wrap("gear:fn:moonblade", PyFn(lambda k_: JL(1.0)))
    Isl.LEVEL_TEST = wrap("skill:fn:level", PyFn(lambda a: JInt(99)))
    ou = UUID.fromString(OWNER)
    now = 1790000000000
    Core.NOW_TEST = now
    Door.door(ou, OWNER, "farming", W, 29, 129, -31)
    p = St.get(OWNER)
    T413._set(L, p, "farming.bench", "4")
    Cfg.UNDER.set(0)
    L.update(dict(held=held, bags=bags, got=got, ou=ou, W=W, p=p, now=now, LOCK=LOCK))
    return L


def JL(v):
    from jpype import JClass
    return JClass("java.lang.Double")(v)


def _grab(LOCK, hold):
    """another thread takes ShStore.LOCK and keeps it until _release(hold)"""
    import threading, time
    from jpype import JClass
    held, stop = threading.Event(), threading.Event()

    def h():
        JClass("java.lang.Thread").currentThread().setName("SkyyTest-cb-holder")
        while not LOCK.tryLock():
            time.sleep(0.002)
        held.set()
        try:
            stop.wait(15)
        finally:
            LOCK.unlock()
    t = threading.Thread(target=h)
    t.start()
    ok = held.wait(5)
    hold["stop"], hold["t"] = stop, t
    return ok


def _release(hold):
    if hold.get("stop") is not None:
        hold["stop"].set()
        hold["t"].join(10)
    hold["stop"] = hold["t"] = None


def _world(fn):
    """fn() on a thread named like a world thread (the 50 ms lock wait)"""
    from jpype import JClass
    T = JClass("java.lang.Thread").currentThread()
    me = str(T.getName())
    T.setName("WorldThread - skyy-island-test")
    try:
        return fn()
    finally:
        T.setName(me)


def _under(K, Cfg, tag):
    K.check(int(Cfg.UNDER.get()) == 0, "%s ShCfg.UNDER = 0 (the runtime guard saw no bridge lookup under the lock; last: '%s')" % (tag, Cfg.UNDER_LAST))


# ---------------------------------------------------------------------------------------------------------- NL: no bridge under the lock, every action
def run_nolock(out, jar, scratch, _home):
    from jpype import JClass, JLong, JInt
    K = HK.Child(out)
    L = _fx(os.path.join(scratch, "nl"), K)
    St, Isl, Core, Door, Cfg, Tot, Inv, Kind, Page, Lv = (L[n] for n in ("ShStore", "ShIsl", "ShCore", "ShDoor", "ShCfg", "ShTotem", "ShInv", "ShKind", "ShPage", "ShLv20"))
    inv, count, held, bags, got, ou, W, p, now = (L[n] for n in ("inv", "count", "held", "bags", "got", "ou", "W", "p", "now"))
    Pl = JClass(PKG + "ShPlace")
    bags["have"] = _Inf()
    cs = inv(27, 27, 9)
    Page.TEST_INV = cs
    res = []

    def act(tag, fn, want="+"):
        del held[:]
        u0 = int(Cfg.UNDER.get())
        r = _world(fn)
        r = "" if r is None else str(r)
        ok = r.startswith(want) if want else True
        K.check(ok and not held and int(Cfg.UNDER.get()) == u0, "NL %s: done (%s) and no bridge was called while holding the lock (held: %s)" % (tag, r[:90], held[:4]))
        res.append(tag)
        return r
    act("Storage II (purchase)", lambda: Core.buyStorage(ou, OWNER, FK, cs))
    T413._set(L, p, "farming.compactor", None)
    T413._set(L, p, "farming.compressor", None)
    act("Auto-Compactor I (purchase)", lambda: Core.buyCompactor(ou, OWNER, FK, cs))
    act("Time Compressor I (purchase)", lambda: Core.buyCompressor(ou, OWNER, FK, cs))
    act("sub-upgrade Crop Amount 1 (purchaseM)", lambda: Core.buySub(ou, OWNER, FK, 0, 0, cs))
    for f_, v_ in (("amt", "5"), ("deco", "5"), ("irr", "5"), ("size", "1")):
        T413._set(L, p, "farming.i0." + f_, v_)
    act("Grow to Medium (purchaseM + SkyyCollections' tier between two locks)", lambda: Core.grow(ou, OWNER, FK, 0, cs))
    nx = int(Isl.nextTier(FK, p))
    K.check(nx > 0, "NL fixture: the next island tier to buy is %d" % nx)
    act("buy the next island (purchaseM)", lambda: Core.buyIsland(ou, OWNER, FK, nx, cs))
    T413._set(L, p, "farming.auto", None)
    act("Automation (purchaseM)", lambda: Core.buyAuto(ou, OWNER, FK, cs))
    act("Offline Harvest 1 (purchaseM)", lambda: Core.buyOffline(ou, OWNER, FK, cs))
    T413._set(L, p, "farming.i0.totems", "harvest_spirit:1:::0:nl0001")
    act("Add modifier", lambda: Core.addMod(ou, OWNER, FK, 0, 0, 0, cs))
    act("Add booster", lambda: Core.addBooster(ou, OWNER, FK, 0, 0, cs))
    act("a placed totem's Tier up", lambda: Core.tierUpPlaced0(ou, OWNER, FK, 0, 0, 1, "harvest_spirit", "nl0001", cs))
    T413._set(L, p, "farming.bench", "1")
    T413._set(L, p, "farming.benchTo", None)
    T413._set(L, p, "farming.benchUpAt", None)
    act("Bench upgrade I -> II", lambda: Core.benchUp(ou, OWNER, FK, cs))
    rid = dict((str(x), i) for i, x in enumerate(Cfg.CRAFT_ID))
    act("Craft a Rain Totem", lambda: Core.craftAt(ou, OWNER, FK, rid["Skyy_Totem_Rain"], cs))
    ris = [(i, int(Kind.ofShard(x))) for i, x in enumerate(Cfg.CRAFT_ID) if int(Kind.ofShard(x)) >= 0 and not bool(Core.hasShard(OWNER, int(Kind.ofShard(x))))]
    if ris:
        ri, sk = ris[0]
        Cfg.CRAFT[ri] = "Plant_Crop_Wheat_Item:10;100"
        act("Craft a shard (%s: the crafted mark under the lock, SkyyProfiles' key before it)" % Kind.SHARD[sk], lambda: Core.craftAt(ou, OWNER, FK, ri, cs))
    else:
        K.check(False, "NL fixture: a shard recipe to craft")
    T413._set(L, p, "mining.placed", "skyy-island-old|1|2|3")
    r = act("place the Mining shard over a STALE record (decide asks SkyyIslands before the lock)", lambda: Pl.decide(ou, 0, W, 40, 129, 40, JLong(now)), want=None)
    K.check(r == "" and str(p.getProperty("mining.placed")) == W + "|40|129|40", "NL ... the stale record dropped, the new one written: %s / %s" % (r, p.getProperty("mining.placed")))
    T413._set(L, p, "foraging.placed", "skyy-island-old|5|6|7")
    r = act("shard:fn:door over a STALE record (SkyyIslands asked before the lock)", lambda: Door.door(ou, OWNER, "foraging", W, 10, 129, 10))
    K.check(str(p.getProperty("foraging.placed")) == W + "|10|129|10", "NL ... the door took the shard (stale record): %s" % p.getProperty("foraging.placed"))
    # the record changes while SkyyIslands is asked (between the two short locks): treated as NOT stale (the old, safe answer)
    Role = L["ShRole"]
    wk0 = Role.WORLDKEY_TEST
    PyFn = L["PyFn"]
    from jpype import JString

    def moved(key_, val_):
        def f(k_):
            T413._set(L, p, key_, val_)
            return JString(W)
        return PyFn(f)
    T413._set(L, p, "orchard.placed", "skyy-island-old|1|2|3")
    Role.WORLDKEY_TEST = moved("orchard.placed", W + "|9|129|9")
    r = act("place a shard while its record changes meanwhile (decide)", lambda: Pl.decide(ou, 4, W, 41, 129, 41, JLong(now)), want=None)
    Role.WORLDKEY_TEST = wk0
    K.check(r.startswith("Your Orchard Shard is already placed") and str(p.getProperty("orchard.placed")) == W + "|9|129|9",
            "NL ... changed meanwhile = not stale: refused, the newer record kept (%s / %s)" % (r[:70], p.getProperty("orchard.placed")))
    T413._set(L, p, "ranching.placed", "skyy-island-old|1|2|3")
    Role.WORLDKEY_TEST = moved("ranching.placed", W + "|8|129|8")
    r = act("shard:fn:door while the record changes meanwhile", lambda: Door.door(ou, OWNER, "ranching", W, 12, 129, 12))
    Role.WORLDKEY_TEST = wk0
    K.check(r == "+kept" and str(p.getProperty("ranching.placed")) == W + "|8|129|8", "NL ... changed meanwhile = not stale: the placed portal kept (%s / %s)" % (r, p.getProperty("ranching.placed")))
    # Grow: the island changes while SkyyCollections is asked (between the two locks) = refused, nothing paid
    for f_, v_ in (("amt", "5"), ("deco", "5"), ("irr", "5"), ("size", "2")):
        T413._set(L, p, "farming.i0." + f_, v_)
    t0_ = L["fns"].get("coll:fn:tier")

    def ct(a):
        T413._set(L, p, "farming.i0.size", "3")
        return t0_.apply(a)
    L["fns"].put("coll:fn:tier", PyFn(ct))
    b0 = dict(bags["committed"])
    r = act("Grow while the island grows meanwhile", lambda: Core.grow(ou, OWNER, FK, 0, cs), want="-That island changed meanwhile")
    L["fns"].put("coll:fn:tier", t0_)
    K.check(dict(bags["committed"]) == b0 and T412._owed(bags) == 0, "NL ... nothing taken, nothing committed")
    T413._set(L, p, "owed.coll.Plant_Crop_Wheat_Item", "30")
    act("owed (SkyyCollections paid with the lock released)", lambda: str(Core.owed(ou, "Plant_Crop_Wheat_Item", JLong(5))), want="0")
    act("owedXp (SkyySkills paid with the lock released)", lambda: str(Core.owedXp(ou, "Farming", JLong(7))), want="0")
    K.check(got["coll"] == 35 and got["xp"] == 7 and p.getProperty("owed.coll.Plant_Crop_Wheat_Item") is None, "NL ... paid 30 + 5 collection, 7 XP: %s" % got)
    T413._set(L, p, "farming.i0.stored", "200")
    act("Collect (owed + owedXp inside)", lambda: Core.collect(ou, OWNER, FK, 0, inv(27, 27, 9)), want="+Collected")
    Cfg.LV20[3] = 20   # Ranching: a free shard on this server
    r = act("grant a level 20 shard", lambda: Lv.grant(ou, OWNER, 3, inv(27, 27, 9)), want=None)
    K.check(r[:1] in ("+", "=", "~"), "NL ... grant answered: %s" % r[:80])
    # the Combat Totems tab: SkyyArmory's essence for the tier-up cost (fillTotems -> tierRows -> costAt, inside fill's lock)
    T411._prof(L, OWNER, [(0, 0, 1, (0, 0, 0))])
    Tot.ESS.clear()
    pg = Page(ou, W)
    pg.kind = CK
    pg.view = 0
    del held[:]
    u0 = int(Cfg.UNDER.get())
    _world(lambda: pg.fill(OWNER, cs))
    e1 = Tot.ESS.get(JInt(1))
    K.check(not held and int(Cfg.UNDER.get()) == u0 and str(e1) == "Ingredient_Test_Essence_T1",
            "NL the Combat Totems tab: the essence warmed BEFORE the lock (cache %s), no bridge under it (held %s)" % (e1, held[:3]))
    K.check("Test Essence" in str(pg.dTx[7]) or "Ingredient_Test_Essence_T1" in str(pg.dTx[7]), "NL ... its Tier up row names SkyyArmory's essence: %s" % pg.dTx[7])
    # the Farming Totems tab's Tier up rows count the bags from the page's ONE read (sacks:fn:all, before the lock) - never sacks:fn:count under it
    ent = "harvest_spirit:1:::0:nl0002"
    T413._set(L, p, "farming.i0.totems", ent)
    ti = [str(x) for x in Tot.KEYS].index("harvest_spirit")
    rc = Core.recipe(str(Tot.costAt(FK, Tot.ITEMS[ti], Tot.doc(Tot.onPad(ent), JLong(now)).toJson())))
    cid, cq = str(rc[0][0]), int(rc[1][0])
    bags["have"] = {cid: 5000}
    pg2 = Page(ou, W)
    pg2.kind = FK
    pg2.view = 0
    del held[:]
    _world(lambda: pg2.fill(OWNER, inv(9)))
    K.check(str(pg2.dTx[8]) == "%d %s (you have 5,000)" % (cq, str(Tot.pretty(cid))) and str(pg2.dCol[8]).lower() == T49.GOOD.lower() and not held,
            "NL the Totems tab's Tier up row counts the Pocket Dimension from the page's one bag read (%s, held %s)" % (pg2.dTx[8], held[:3]))
    bags["have"] = _Inf()
    # under the lock with no cache: the safe default, never the bridge
    Tot.ESS.clear()
    del held[:]
    St.LOCK.lock()
    try:
        es = str(Tot.essence(CK, 2))
    finally:
        St.LOCK.unlock()
    K.check(es == "Ingredient_Life_Essence" and not held, "NL essence under the lock with an empty cache: the default, SkyyArmory not called (%s, held %s)" % (es, held))
    # the runtime guard itself works (the control): a bridge lookup while holding the lock counts + WARNs once
    u0 = int(Cfg.UNDER.get())
    St.LOCK.lock()
    try:
        Cfg.fn("sacks:fn:count")
    finally:
        St.LOCK.unlock()
    K.check(int(Cfg.UNDER.get()) == u0 + 1 and str(Cfg.UNDER_LAST) == "sacks:fn:count", "NL the runtime guard (control): a lookup under the lock counts (%d, %s)" % (int(Cfg.UNDER.get()), Cfg.UNDER_LAST))
    Cfg.UNDER.set(u0)
    _under(K, Cfg, "NL")
    Isl.LEVEL_TEST = None
    Page.TEST_INV = None
    K.save()


# ---------------------------------------------------------------------------------------------------------- CB: a busy / changed commit = everything back
def run_commit(out, jar, scratch, _home):
    from jpype import JClass, JLong
    K = HK.Child(out)
    L = _fx(os.path.join(scratch, "cb"), K)
    St, Isl, Core, Cfg, Tot, Kind, Page, Cb = (L[n] for n in ("ShStore", "ShIsl", "ShCore", "ShCfg", "ShTotem", "ShKind", "ShPage", "ShCombat"))
    inv, count, held, bags, ou, W, p, now, coins, br, PyFn = (L[n] for n in ("inv", "count", "held", "bags", "ou", "W", "p", "now", "coins", "br", "PyFn"))
    LOCK = St.LOCK
    hook = {"f": None}
    take0 = br.get("sacks:fn:take")

    def take(a):
        if hook["f"] is not None:
            h, hook["f"] = hook["f"], None
            h()
        return take0.apply(a)
    br.put("sacks:fn:take", PyFn(take))
    hold = {}
    cs = inv(27, 27, 9)
    Page.TEST_INV = cs

    def snap(keys):
        return (dict(bags["have"]), T412._owed(bags), dict(bags["committed"]), coins["bal"], tuple(str(p.getProperty(k_)) for k_ in keys),
                sum(int(count(cs, i_)) for i_ in bags["have"]))

    def log_txt():
        t = ""
        for root, _d, fs in os.walk(os.path.join(scratch, "cb")):
            for f_ in fs:
                if f_ == "collect.log":
                    t += open(os.path.join(root, f_), encoding="utf-8").read()
        return t

    def bump():
        T413._set(L, p, "farming.cbtick", str(int(p.getProperty("farming.cbtick") or "0") + 1))

    def three(tag, fn, have, keys, change=bump, changed_word="changed"):
        """(a) busy at the commit, (b) changed meanwhile, (c) then done"""
        for what in ("busy", "changed"):
            bags["have"] = dict(have)
            s0 = snap(keys)
            del held[:]
            hook["f"] = (lambda: _grab(LOCK, hold)) if what == "busy" else change
            try:
                r = str(_world(fn))
            finally:
                hook["f"] = None
                _release(hold)
            word = "busy" if what == "busy" else changed_word
            s1 = snap(keys)
            if what == "changed" and change is not bump:   # the change itself rewrote the record: everything else as before
                s1, s0 = s1[:4] + s1[5:], s0[:4] + s0[5:]
            K.check(word in r.lower() and s1 == s0 and not held,
                    "CB %s, %s at the commit: EVERYTHING back (bags %s, nothing owed or committed, coins, record %s) - '%s'" % (tag, what, bags["have"], s0[4], r[:90]))
        bags["have"] = dict(have)
        s0 = snap(keys)
        r = str(_world(fn))
        K.check(r.startswith("+") and snap(keys)[4] != s0[4] and T412._owed(bags) == 0 and not held, "CB %s ... then (free lock) it goes through: %s" % (tag, r[:90]))
    upg = str(Kind.UPG[FK])
    three("Storage II (purchase)", lambda: Core.buyStorage(ou, OWNER, FK, cs), {upg: int(Cfg.storeEnch(2))}, ["farming.storage"])
    K.check("SHARD DATA BUSY" in log_txt() and "CHANGED MEANWHILE" in log_txt(), "CB ... collect.log names both refusals (SHARD DATA BUSY / CHANGED MEANWHILE) with the refund")
    t0 = int(Isl.LAD0[FK])
    m0 = Isl.mats(FK, t0, str(Cb.subMat(FK, 0)), 0, JLong(1))
    three("Crop Amount 1 (purchaseM)", lambda: Core.buySub(ou, OWNER, FK, 0, 0, cs), dict(zip([str(x) for x in m0[0]], [int(x) for x in m0[1]])), ["farming.i0.amt"])
    T413._set(L, p, "farming.auto", None)
    ma = Isl.mats(FK, t0, Cfg.AUTO_ITEMS[FK], 0, JLong(1))
    three("Automation (purchaseM)", lambda: Core.buyAuto(ou, OWNER, FK, cs), dict(zip([str(x) for x in ma[0]], [int(x) for x in ma[1]])), ["farming.auto"])
    ent = "harvest_spirit:1:::0:cb0001"
    T413._set(L, p, "farming.i0.totems", ent)
    mid = str(Tot.MOD_ITEMS[0])

    def touch():
        T413._set(L, p, "farming.i0.totems", "harvest_spirit:1:::1:cb0001")   # the booster field changed = another entry
    three("Add modifier", lambda: Core.addMod(ou, OWNER, FK, 0, 0, 0, cs), {mid: 1}, ["farming.i0.totems"], change=touch)
    T413._set(L, p, "farming.i0.totems", ent)
    bid = str(Tot.BOOSTERS[1])
    three("Add booster", lambda: Core.addBooster(ou, OWNER, FK, 0, 0, cs), {bid: 1}, ["farming.i0.totems"], change=touch)
    T413._set(L, p, "farming.i0.totems", ent)
    ti = [str(x) for x in Tot.KEYS].index("harvest_spirit")
    rc = Core.recipe(str(Tot.costAt(FK, Tot.ITEMS[ti], Tot.doc(Tot.onPad(ent), JLong(now)).toJson())))
    three("a placed totem's Tier up", lambda: Core.tierUpPlaced0(ou, OWNER, FK, 0, 0, 1, "harvest_spirit", "cb0001", cs),
          dict(zip([str(x) for x in rc[0]], [int(x) for x in rc[1]])), ["farming.i0.totems"], change=touch)
    T413._set(L, p, "farming.bench", "1")
    T413._set(L, p, "farming.benchTo", None)
    T413._set(L, p, "farming.benchUpAt", None)
    bt = Core.recipe(Cfg.benchItems(2, FK).strip())
    three("Bench upgrade", lambda: Core.benchUp(ou, OWNER, FK, cs), dict(zip([str(x) for x in bt[0]], [int(x) for x in bt[1]])), ["farming.bench", "farming.benchUpAt"])
    # craft a shard: busy = everything back, no mark, no shard; someone else's mark meanwhile = refused at the commit, everything back
    ris = [(i, int(Kind.ofShard(x))) for i, x in enumerate(Cfg.CRAFT_ID) if int(Kind.ofShard(x)) >= 0 and not bool(Core.hasShard(OWNER, int(Kind.ofShard(x))))]
    if ris:
        ri, sk = ris[0]
        Cfg.CRAFT[ri] = "Plant_Crop_Wheat_Item:10;100"
        mk = str(Kind.KEYS[sk]) + ".crafted"
        sid = str(Kind.SHARD[sk])

        def mark():
            T413._set(L, p, mk, "1")
        bags["have"] = {"Plant_Crop_Wheat_Item": 10}
        s0 = snap([])
        hook["f"] = lambda: _grab(LOCK, hold)
        try:
            r = str(_world(lambda: Core.craftAt(ou, OWNER, FK, ri, cs)))
        finally:
            hook["f"] = None
            _release(hold)
        K.check("busy" in r.lower() and snap([]) == s0 and p.getProperty(mk) is None and count(cs, sid) == 0, "CB Craft %s, busy at the commit: everything back, no mark, no shard: %s" % (sid, r))
        bags["have"] = {"Plant_Crop_Wheat_Item": 10}
        s0 = snap([])
        hook["f"] = mark
        r = str(_world(lambda: Core.craftAt(ou, OWNER, FK, ri, cs)))
        hook["f"] = None
        K.check("everything is back" in r.lower() and snap([]) == s0 and count(cs, sid) == 0, "CB Craft %s, the shard recorded meanwhile: refused at the commit, everything back: %s" % (sid, r))
        T413._set(L, p, mk, None)
        bags["have"] = {"Plant_Crop_Wheat_Item": 10}
        r = str(_world(lambda: Core.craftAt(ou, OWNER, FK, ri, cs)))
        K.check(r.startswith("+Crafted") and str(p.getProperty(mk)) == "1" and count(cs, sid) == 1 and bags["committed"].get("Plant_Crop_Wheat_Item", 0) >= 10,
                "CB Craft %s ... then it is crafted (mark, one shard, the bag part committed): %s" % (sid, r))
    # a coins refund that fails after a busy commit is named (the coins stand-in refuses the add once)
    bags["have"] = {upg: int(Cfg.storeEnch(3))}
    add0 = L["fns"].get("coins:fn:add")
    L["fns"].put("coins:fn:add", PyFn(lambda a: None))
    hook["f"] = lambda: _grab(LOCK, hold)
    try:
        r = str(_world(lambda: Core.buyStorage(ou, OWNER, FK, cs)))
    finally:
        hook["f"] = None
        _release(hold)
        L["fns"].put("coins:fn:add", add0)
    K.check("busy" in r.lower() and "ask an admin" in r.lower() and T412._owed(bags) == 0, "CB a busy commit whose coin refund fails says so (items back, the coins named): %s" % r)
    _under(K, Cfg, "CB")
    Page.TEST_INV = None
    K.save()


# ---------------------------------------------------------------------------------------------------------- OW: the Collect credits, exactly once
def run_owed(out, jar, scratch, _home):
    import threading
    from jpype import JClass, JLong
    K = HK.Child(out)
    L = _fx(os.path.join(scratch, "ow"), K)
    St, Core, Cfg = L["ShStore"], L["ShCore"], L["ShCfg"]
    got, ou, p, held = L["got"], L["ou"], L["p"], L["held"]
    LOCK = St.LOCK
    hold = {}
    IT = "Plant_Crop_Wheat_Item"
    key = "owed.coll." + IT
    mkey = OWNER + "|" + key
    xkey = OWNER + "|owed.xp"
    fpath = os.path.join(L["sd"], OWNER + ".properties")

    def disk(k_):
        for ln in open(fpath, encoding="latin-1").read().splitlines():
            if ln.startswith(k_ + "="):
                return ln.split("=", 1)[1]
        return None

    def mem(k_):
        v = Core.MEM_OWED.get(k_)
        return None if v is None else int(v)

    def restart():
        """a server restart: memory gone, the profile read from disk again"""
        Core.MEM_OWED.clear()
        St.CACHE.clear()
        St.VER.clear()
        return St.get(OWNER)
    Core.MEM_OWED.clear()
    # 1. Skyy's LOW: busy AFTER paying + a restart (0.4.13: the file kept 30 + memory -30 -> a restart paid the 30 again)
    T413._set(L, p, key, "30")
    got["hook"] = lambda: _grab(LOCK, hold)
    try:
        r1 = int(_world(lambda: Core.owed(ou, IT, JLong(50))))
    finally:
        _release(hold)
    c1 = got["coll"]
    K.check(r1 == 0 and c1 == 80 and disk(key) is None and mem(mkey) is None, "OW paid 80 (50 + the file's 30), the lock busy right after: the file no longer holds the 30 (disk %s, memory %s)" % (disk(key), mem(mkey)))
    p = restart()
    r2 = int(Core.owed(ou, IT, JLong(10)))
    K.check(r2 == 0 and got["coll"] - c1 == 10, "OW ... a RESTART, then the next Collect pays only its own 10 - the 30 was paid exactly once (paid %d)" % (got["coll"] - c1))
    # 2. refused + the write-back busy: memory, then the tick's flush puts it in the file, a restart pays it once
    T413._set(L, p, key, "30")
    got["ok"] = False
    got["hook"] = lambda: _grab(LOCK, hold)
    try:
        r1 = int(_world(lambda: Core.owed(ou, IT, JLong(50))))
    finally:
        _release(hold)
    got["ok"] = True
    K.check(r1 == 80 and disk(key) is None and mem(mkey) == 80, "OW refused + busy write-back: all 80 wait in memory, none on disk (the 30 reserved out of the file): disk %s, memory %s" % (disk(key), mem(mkey)))
    n = int(Core.flushOwed())
    K.check(n == 1 and disk(key) == "80" and mem(mkey) is None, "OW ... flushOwed (the tick) moves the 80 into the collector file (disk %s, memory %s)" % (disk(key), mem(mkey)))
    p = restart()
    c2 = got["coll"]
    r2 = int(Core.owed(ou, IT, JLong(0)))
    K.check(r2 == 0 and got["coll"] - c2 == 80 and disk(key) is None and mem(mkey) is None, "OW ... a RESTART, the next Collect pays the 80 exactly once, file + memory clean")
    # 3. a busy flush keeps the memory part (nothing written, nothing lost); the next flush moves it
    Core.memAdj(OWNER, key, JLong(12), ou)
    _grab(LOCK, hold)
    try:
        n = int(Core.flushOwed())   # this (non-world) thread waits WAIT_MS, then gives up
    finally:
        _release(hold)
    K.check(n == 0 and mem(mkey) == 12 and disk(key) is None, "OW a busy flush: the 12 stay in memory (memory %s, disk %s)" % (mem(mkey), disk(key)))
    K.check(int(Core.flushOwed()) == 1 and disk(key) == "12" and mem(mkey) is None, "OW ... the next flush writes it")
    T413._set(L, p, key, None)
    # 4. owedXp the same way: busy after paying + a restart = paid once
    T413._set(L, p, "owed.xp", "40")
    got["hook"] = lambda: _grab(LOCK, hold)
    try:
        r1 = int(_world(lambda: Core.owedXp(ou, "Farming", JLong(60))))
    finally:
        _release(hold)
    x1 = got["xp"]
    p = restart()
    Core.owedXp(ou, "Farming", JLong(5))
    K.check(r1 == 0 and got["xp"] - x1 == 5 and disk("owed.xp") is None, "OW owedXp: 100 paid, busy after, a RESTART -> only the next 5 (paid %d)" % (got["xp"] - x1))
    # 5. the reserve's save refused: the file part stays (memory + disk), only the new part is paid; later it is paid once
    T413._set(L, p, key, "30")
    St.FAIL_TEST = True
    c3 = got["coll"]
    try:
        r1 = int(Core.owed(ou, IT, JLong(4)))
    finally:
        St.FAIL_TEST = False
    K.check(r1 == 0 and got["coll"] - c3 == 4 and str(p.getProperty(key)) == "30" and disk(key) == "30", "OW a refused reserve save: only the new 4 paid, the 30 stay in the file (memory %s, disk %s)" % (p.getProperty(key), disk(key)))
    Core.owed(ou, IT, JLong(0))
    K.check(got["coll"] - c3 == 34 and disk(key) is None, "OW ... the next Collect pays the 30 once")
    # 6. a refused write-back save = memory, flushed later (never dropped)
    T413._set(L, p, key, "7")
    got["ok"] = False
    got["hook"] = lambda: setattr(St, "FAIL_TEST", True)
    try:
        r1 = int(Core.owed(ou, IT, JLong(3)))
    finally:
        St.FAIL_TEST = False
        got["ok"] = True
    K.check(r1 == 10 and mem(mkey) == 10, "OW a refused write-back save: the 10 wait in memory (%s)" % mem(mkey))
    K.check(int(Core.flushOwed()) == 1 and disk(key) == "10", "OW ... flushed into the file")
    T413._set(L, p, key, None)
    # 6b. a refused flush save keeps the credit in memory (nothing lost), the next flush writes it
    Core.memAdj(OWNER, key, JLong(6), ou)
    St.FAIL_TEST = True
    try:
        n = int(Core.flushOwed())
    finally:
        St.FAIL_TEST = False
    K.check(n == 0 and mem(mkey) == 6 and disk(key) is None, "OW a refused flush save: the 6 stay in memory, the file as it was (memory %s, disk %s)" % (mem(mkey), disk(key)))
    K.check(int(Core.flushOwed()) == 1 and disk(key) == "6" and mem(mkey) is None, "OW ... the next flush writes them")
    T413._set(L, p, key, None)
    # 7. memAdd from two threads at once adds up exactly (the tick flushes while world threads add)
    Core.MEM_OWED.clear()

    def adder():
        for _i in range(500):
            Core.memAdd(JClass("java.lang.String")("race|k"), JLong(1))
    ts = [threading.Thread(target=adder) for _i in range(2)]
    for t in ts:
        t.start()
    for t in ts:
        t.join(60)
    K.check(mem("race|k") == 1000, "OW memAdd from two threads at once: exactly 1,000 (%s)" % mem("race|k"))
    Core.MEM_OWED.clear()
    # 8. the tick runs the flush on its own thread
    Core.memAdj(OWNER, key, JLong(9), ou)
    Thr = JClass(PKG + "ShThreads")
    done = {}

    def tick():
        JClass(PKG + "ShTick")().run()
        done["name"] = str(JClass("java.lang.Thread").currentThread().getName())
    t = threading.Thread(target=tick)
    t.start()
    t.join(30)
    K.check(disk(key) == "9" and mem(mkey) is None, "OW ShTick.run moves the waiting 9 into the file (disk %s, memory %s)" % (disk(key), mem(mkey)))
    nt = Thr().newThread(None)
    K.check(str(nt.getName()) == "SkyyShards-tick" and bool(nt.isDaemon()), "EX ShTick's thread: SkyyShards-tick, a daemon (not the shared HytaleServer.SCHEDULED_EXECUTOR)")
    K.check(not held, "OW no bridge was called while holding the lock (held %s)" % held[:3])
    _under(K, Cfg, "OW")
    K.save()


# ---------------------------------------------------------------------------------------------------------- FX: the fixer's checks (critics 10-27)
def _fake_world(L):
    """a World subclass (javassist) whose execute() only records the Runnable, alive, named skyy-shard-fxtest; allocated without a constructor"""
    from jpype import JClass
    WC = JClass("com.hypixel.hytale.server.core.universe.world.World")
    CP = JClass("javassist.ClassPool")(True)
    CNM = JClass("javassist.CtNewMethod")
    CF = JClass("javassist.CtField")
    nm = "com.hypixel.hytale.server.core.universe.world.SkyyShFxWorld"
    c = CP.makeClass(nm, CP.get(WC.class_.getName()))
    c.addField(CF.make("public static final java.util.ArrayList Q = new java.util.ArrayList();", c))
    c.addMethod(CNM.make("public void execute(Runnable r) { Q.add(r); }", c))
    c.addMethod(CNM.make("public boolean isAlive() { return true; }", c))
    c.addMethod(CNM.make("public String getName() { return \"skyy-shard-fxtest\"; }", c))
    k = c.toClass(WC.class_)
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)
    return k, U.allocateInstance(k), U.allocateInstance(k)


def run_fixer(out, jar, scratch, _home):
    import time
    from jpype import JClass, JLong, JInt
    K = HK.Child(out)
    L = _fx(os.path.join(scratch, "fx"), K)
    St, Core, Cfg, Tot = L["ShStore"], L["ShCore"], L["ShCfg"], L["ShTotem"]
    got, ou, p, held, PyFn = L["got"], L["ou"], L["p"], L["held"], L["PyFn"]
    LOCK = St.LOCK
    hold = {}
    IT = "Plant_Crop_Wheat_Item"
    key = "owed.coll." + IT
    mkey = OWNER + "|" + key
    clog = os.path.join(os.path.dirname(L["sd"]), "collect.log")

    def logtxt():
        return open(clog, encoding="utf8").read() if os.path.exists(clog) else ""
    Core.MEM_OWED.clear()
    # 1. RESERVED + PAID in collect.log (at most once, but visible)
    T413._set(L, p, key, "30")
    l0 = len(logtxt())
    r1 = int(_world(lambda: Core.owed(ou, IT, JLong(5))))
    t = logtxt()[l0:]
    K.check(r1 == 0 and (OWNER + " " + key + " 30 RESERVED") in t and (OWNER + " " + key + " PAID 35 of 35 (30 reserved)") in t,
            "FX the reserve writes RESERVED and the payment PAID to collect.log: %r" % t[-260:])
    T413._set(L, p, "owed.xp", "11")
    l0 = len(logtxt())
    got["ok"] = False
    try:
        rx = int(_world(lambda: Core.owedXp(ou, "Farming", JLong(4))))
    finally:
        got["ok"] = True
    t = logtxt()[l0:]
    K.check(rx == 15 and (OWNER + " owed.xp 11 RESERVED") in t and (OWNER + " owed.xp PAID 0 of 15 (11 reserved) - 15 go back") in t,
            "FX owedXp refused: RESERVED, then PAID 0 of 15 - 15 go back (written back): %r" % t[-260:])
    Core.owedXp(ou, "Farming", JLong(0))
    T413._set(L, p, "owed.xp", None)
    l0 = len(logtxt())
    Core.owed(ou, IT, JLong(3))
    K.check("RESERVED" not in logtxt()[l0:], "FX a Collect with nothing waiting in the file writes no RESERVED line (no log spam)")
    # 2. flushOwed: an unreadable collector file (ShStore.BAD) is skipped for a minute, then tried again
    Core.MEM_OWED.clear()
    Core.memAdj(OWNER, key, JLong(8), ou)
    St.CACHE.clear()
    St.BAD.put(OWNER, L["Bool"].TRUE)
    Core.BAD_TRY = int(time.time() * 1000)
    n = int(Core.flushOwed())
    K.check(n == 0 and int(Core.MEM_OWED.get(mkey)) == 8 and St.CACHE.get(OWNER) is None and St.BAD.containsKey(OWNER),
            "FX flushOwed skips an unreadable collector file inside the minute (no re-read: cache %s, memory %s)" % (St.CACHE.get(OWNER) is not None, Core.MEM_OWED.get(mkey)))
    Core.BAD_TRY = 0
    n = int(Core.flushOwed())
    p = St.get(OWNER)
    K.check(n == 1 and Core.MEM_OWED.get(mkey) is None and not St.BAD.containsKey(OWNER) and str(p.getProperty(key)) == "8" and int(Core.BAD_TRY) > 0,
            "FX ... a minute later it tries again (the file reads now): the 8 move into it")
    Core.owed(ou, IT, JLong(0))
    # 3. the Combat essence: SkyyArmory asked once a minute per tier
    calls = []

    def soul(a):
        calls.append(int(a[1]))
        return JClass("java.lang.String")("Ingredient_Fx_Essence_T%d" % int(a[1]))
    old_soul = Tot.SOUL_TEST
    Tot.SOUL_TEST = PyFn(soul)
    try:
        Tot.ESS.clear()
        Tot.ESS_AT.clear()
        e1, e2 = str(Tot.essence(CK, 3)), str(Tot.essence(CK, 3))
        K.check(e1 == e2 == "Ingredient_Fx_Essence_T3" and calls == [3], "FX essence: two page fills in a minute ask SkyyArmory once (%s)" % calls)
        a = Tot.ESS_AT.get(JInt(3))
        a[1] = JClass("java.lang.Long")(int(a[1]) - 61000)
        Tot.essence(CK, 3)
        K.check(calls == [3, 3], "FX ... an entry older than a minute asks again (%s)" % calls)
        Tot.SOUL_TEST = PyFn(lambda a_: JClass("java.lang.String")("Ingredient_Other_Essence"))
        K.check(str(Tot.essence(CK, 3)) == "Ingredient_Other_Essence", "FX ... a new SkyyArmory function (reloaded mod) is asked at once")
        LOCK.lock()
        try:
            K.check(str(Tot.essence(CK, 3)) == "Ingredient_Other_Essence", "FX ... under the lock the cache answers (no bridge)")
        finally:
            LOCK.unlock()
    finally:
        Tot.SOUL_TEST = old_soul
        Tot.ESS.clear()
        Tot.ESS_AT.clear()
    # 4. Enter Shard's load callback: only hops (no profile read, no lock on the loader's thread)
    Hop = JClass(PKG + "ShHop")
    W2 = JClass(PKG + "ShWorld2")
    WK, wfrom, wto = _fake_world(L)
    Q = WK.getField("Q").get(None)
    Q.clear()
    hp = Hop(None, wfrom, W2.arrival(FK), ou, OWNER)
    hp.kind = FK
    St.CACHE.clear()
    _grab(LOCK, hold)
    try:
        t0 = time.time()
        hp.accept(wto, None)   # this (non-world) thread = 1.5 s if it waited for the lock
        dt = time.time() - t0
    finally:
        _release(hold)
    K.check(dt < 0.5 and Q.size() == 1 and Q.get(0).equals(hp) and bool(hp.paint) and St.CACHE.get(OWNER) is None and hp.key is not None,
            "FX ShHop.accept with the shard lock held elsewhere: returns at once (%.3f s), only queues the paint step (queued %d, paint %s), no profile read" % (dt, Q.size(), hp.paint))
    Q.clear()
    _world(lambda: hp.run())   # the shard world's thread: the profile read + the paint (the fake world has no chunks: the paint ends at once)
    K.check(St.CACHE.get(OWNER) is not None and hp.key is None and not bool(hp.paint) and Q.size() == 1 and Q.get(0).equals(hp),
            "FX ... the paint step on the shard world's thread read the profile, painted, then queued the teleport (queued %d, paint %s)" % (Q.size(), hp.paint))
    Q.clear()
    _world(lambda: hp.run())   # the teleport step (no player ref here): returns quietly, queues nothing
    K.check(Q.size() == 0, "FX ... the teleport step runs on the player's world (nothing re-queued)")
    hp2 = Hop(None, wfrom, W2.arrival(FK), ou, OWNER)
    hp2.kind = FK
    hp2.accept(wto, None)
    Q.clear()
    St.CACHE.clear()
    _grab(LOCK, hold)
    try:
        _world(lambda: hp2.run())   # a world thread: 50 ms, then ShBusy -> the player is told
    finally:
        _release(hold)
    K.check(Q.size() == 0 and hp2.key is not None, "FX ... the paint step meeting a busy lock: no teleport queued (the player is told to press Enter again)")
    # fixer 2: the profile already CACHED (the read needs no lock) - the busy lock is met by the paint prep (ShFill.region): still no teleport
    hp3 = Hop(None, wfrom, W2.arrival(FK), ou, OWNER)
    hp3.kind = FK
    hp3.accept(wto, None)
    Q.clear()
    St.get(OWNER)
    _grab(LOCK, hold)
    try:
        _world(lambda: hp3.run())
    finally:
        _release(hold)
    K.check(St.CACHE.get(OWNER) is not None and Q.size() == 0 and hp3.key is not None,
            "FX2 the paint step with the profile cached and the lock busy (held through the paint prep): no teleport into an unpainted region (queued %d)" % Q.size())
    Q.clear()
    hp3.paint = True   # Enter Shard pressed again (a new hop queues its paint step the same way)
    _world(lambda: hp3.run())
    K.check(hp3.key is None and Q.size() == 1 and Q.get(0).equals(hp3), "FX2 ... pressed again with the lock free: paints, then queues the teleport (queued %d)" % Q.size())
    Q.clear()
    # fixer 2: SkyyCollections / SkyySkills absent = no reserve: the file part stays put, one save, no RESERVED / PAID lines
    Core.MEM_OWED.clear()
    p = St.get(OWNER)   # the hop checks cleared the cache: the live profile object
    T413._set(L, p, key, "20")
    T413._set(L, p, "owed.xp", "9")
    c0, x0 = got["coll"], got["xp"]
    fns = L["fns"]
    ca, xa = fns.get("coll:fn:add"), fns.get("skill:fn:addxp")
    fns.remove("coll:fn:add")
    fns.remove("skill:fn:addxp")
    try:
        l0 = len(logtxt())
        w0 = int(St.WRITES.get())
        ra = int(_world(lambda: Core.owed(ou, IT, JLong(4))))
        rb = int(_world(lambda: Core.owedXp(ou, "Farming", JLong(0))))
        w1 = int(St.WRITES.get())
        t = logtxt()[l0:]
        p = St.get(OWNER)
        K.check(ra == 24 and rb == 9 and str(p.getProperty(key)) == "24" and str(p.getProperty("owed.xp")) == "9" and "RESERVED" not in t and "PAID" not in t
                and w1 - w0 == 1 and got["coll"] == c0 and got["xp"] == x0 and Core.MEM_OWED.isEmpty(),
                "FX2 SkyyCollections / SkyySkills absent: no reserve - the file keeps 24 / 9 (got %s / %s), %d save(s) (want 1: only the new 4), no RESERVED / PAID lines (%r)"
                % (p.getProperty(key), p.getProperty("owed.xp"), w1 - w0, t[-200:]))
    finally:
        fns.put("coll:fn:add", ca)
        fns.put("skill:fn:addxp", xa)
    l0 = len(logtxt())
    ra = int(_world(lambda: Core.owed(ou, IT, JLong(0))))
    rb = int(_world(lambda: Core.owedXp(ou, "Farming", JLong(0))))
    p = St.get(OWNER)
    K.check(ra == 0 and rb == 0 and got["coll"] - c0 == 24 and got["xp"] - x0 == 9 and p.getProperty(key) is None and p.getProperty("owed.xp") is None
            and "24 RESERVED" in logtxt()[l0:],
            "FX2 ... the mods back: the next Collect pays 24 / 9 exactly once (paid %d / %d)" % (got["coll"] - c0, got["xp"] - x0))
    St.get(OWNER)
    K.check(not held, "FX no bridge was called while holding the lock (held %s)" % held[:3])
    _under(K, Cfg, "FX")
    K.save()


# ---------------------------------------------------------------------------------------------------------- the 0.4.13 phases on the 0.4.14 jar
SUP_X47 = T413.SUP47 + ("X the bags count: '",)   # 0.4.14: the Tier up rows count the bags from the page's sacks:fn:all read (0.4.7's stand-in has no "all"; NL checks it)
SUP_BZ = ("BZ benchUp meets a busy lock at the payment", "BZ tierUpPlaced meets a busy lock at the payment", "BZ craft ",
          "BZ refused + busy on the write-back", "BZ paid 80 (50 + the file's 30)", "BZ grow0's re-lock tracks a held flag")
# 0.4.14 on purpose: a busy lock at the COMMIT gives everything back with a "busy" answer (CB checks it) instead of a thrown ShBusy before paying;
# owed reserves the file part before paying (OW checks it), so the file no longer keeps it while it is paid; grow0 has two short locks now


def run_players48(out, jar, scratch, home):
    """the map migration's collect.log line names the RUNNING version: 0.4.14 now"""
    SUP(("P one collect.log line with the Undo", "P the map migration's collect.log line"), lambda: T48.run_players(out, jar, os.path.join(scratch, "p48"), home))
    d_ = json.load(open(out))
    K = HK.Child(out)
    K.ok, K.fails, K.notes = d_["ok"], d_["fails"], d_["notes"]
    txt = ""
    for root, _d, fs in os.walk(os.path.join(scratch, "p48")):
        for f_ in fs:
            if f_ == "collect.log":
                txt += open(os.path.join(root, f_), encoding="utf8").read()
    K.check("map migration (SkyyShards 0.4.14) 0a0a0a0a-1111-2222-3333-000000000001" in txt and "Undo:" in txt,
            "P the map migration's collect.log line (running version 0.4.14) with the Undo")
    K.save()


def _g(fn, sup=(), lock_ok=False):
    """an older phase in this process, then the runtime guard's count (lock_ok: that phase holds ShStore.LOCK itself around an action)"""
    def r(out, jar, scratch, home):
        SUP(tuple(sup), lambda: fn(out, jar, scratch, home))
        import jpype
        if not jpype.isJVMStarted():
            return
        from jpype import JClass
        Cfg = JClass(PKG + "ShCfg")
        d_ = json.load(open(out))
        K = HK.Child(out)
        K.ok, K.fails, K.notes = d_["ok"], d_["fails"], d_["notes"]
        n = int(Cfg.UNDER.get())
        if lock_ok:
            K.notes.append("UNDER %d after this phase (the phase itself holds ShStore.LOCK around a call; last %s)" % (n, Cfg.UNDER_LAST))
        else:
            K.check(n == 0, "G after this older phase ShCfg.UNDER = 0 (last '%s')" % Cfg.UNDER_LAST)
        K.save()
    return r


def _p(fn, sup=(), lock_ok=False):
    return _g(lambda out, jar, scratch, home: fn(out, jar, os.path.join(scratch, "p413"), home), sup, lock_ok)


EXPECT = {   # 0.4.13 -> 0.4.14, checked by hand 2026-10-27: the version texts (CfgFn / CfgRows, ShStore migrate* log lines, the ready line in
    # SkyyShardsPlugin.setup); the guard (ShCfg under / fnT / fn, the fnT stand-ins in pkey / ShRole / ShTotem moonBlade + essence / ShCore soulGate,
    # ShPay.f); the save counter (ShStore VER / ver / save); pay outside + record under the lock (ShCore commitKeys + purchase / purchaseM with
    # the ver parameter + every caller, addMod / addBooster / tierUpPlaced0 / benchUp / craft); the Collect credits (memAdd / reserve / back /
    # flushOwed, owed / owedXp / memKeep / memAdj, ShTick.run + the plugin shutdown flush); islands before the lock (ShPlace.decide, ShDoor.door);
    # SkyyArmory after / cached (ShPage fill / fillTotemPage / tierRows, ShTotem ESS / warmEss / essence)
    # fixer: ShCore BAD_TRY (flushOwed), ShTotem ESS_AT (essence once a minute), ShHop paint / paintNow / run / accept (the load callback only hops)
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~m header'],
    'ShCfg': ['+f UNDER', '+f UNDER_LAST', '+m fnT', '+m under', '~<clinit>', '~m fn', '~m pkey'],
    'ShCore': ['+f BAD_TRY', '+m back', '+m commitKeys', '+m failTxt', '+m flushOwed', '+m lockish', '+m logTxt', '+m memAdd', '+m purchase', '+m purchaseM', '+m reserve',
               '-m purchase', '-m purchaseM', '~m addBooster', '~m addMod', '~m benchUp', '~m buyAuto0', '~m buyCompactor', '~m buyCompressor', '~m buyIsland0',
               '~m buyOffline0', '~m buyStorage', '~m buySub0', '~m craft', '~m grow0', '~m memAdj', '~m memKeep', '~m owed', '~m owedXp', '~m soulGate',
               '~m tierUpPlaced0'],
    'ShDoor': ['~m door'],
    'ShPage': ['~m fill', '~m fillTotemPage', '~m tierRows'],
    'ShPay': ['~m f'],
    'ShPlace': ['~m decide'],
    'ShRole': ['~m closed', '~m currentWorld', '~m islandOwner', '~m ofKey', '~m onIsland'],
    'ShStore': ['+f VER', '+m ver', '~<clinit>', '~m migrate', '~m migrate2', '~m save'],
    'ShTick': ['~m run'],
    'ShTotem': ['+f ESS', '+f ESS_AT', '+m warmEss', '~<clinit>', '~m essence', '~m moonBlade'],
    'ShHop': ['+f paint', '+m paintNow', '~m accept', '~m run'],
    'SkyyShardsPlugin': ['~m setup', '~m shutdown'],
}
_ORIG_COMPARE = T411._ORIG_COMPARE


def _compare(out, jar, old_jar, pkg, expect, added, removed=()):
    """every non-class file identical (manifest.json aside); the classes as EXPECT"""
    import zipfile as _zf
    with _zf.ZipFile(jar) as a, _zf.ZipFile(old_jar) as b:
        na = dict((n_, a.read(n_)) for n_ in a.namelist() if not n_.endswith(".class"))
        nb = dict((n_, b.read(n_)) for n_ in b.namelist() if not n_.endswith(".class"))
    ch = sorted(n_ for n_ in set(na) | set(nb) if na.get(n_) != nb.get(n_) and n_ != "manifest.json")
    assert not ch, "C non-class files differ: %s" % ch[:8]
    print("C. %d non-class files identical (manifest.json aside)" % len(nb))
    cps = []
    for j, tag in ((jar, VERSION), (old_jar, "old")):
        cp = os.path.join(SCRATCH, "compare-%s.jar" % tag)
        with _zf.ZipFile(j) as zi, _zf.ZipFile(cp, "w", _zf.ZIP_DEFLATED) as zo:
            for n_ in zi.namelist():
                if not T49.MAP_ENTRY.match(n_):
                    zo.writestr(n_, zi.read(n_))
        cps.append(cp)
    _ORIG_COMPARE(out, cps[0], cps[1], pkg, expect, added, removed)


HK.run_compare = _compare
S0 = ()

if __name__ == "__main__":
    HK.run(name="SkyyShards", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("static", run_static), ("nolock", run_nolock), ("commit", run_commit), ("owed", run_owed), ("fixer", run_fixer),
                   ("lock", _g(T413.run_lock)), ("busy", _g(T413.run_busy, SUP_BZ)), ("place", _g(T413.run_place)), ("walk3", _g(T413.run_walk3)),
                   ("flows3", _g(T413.run_flows3)), ("aura", _g(T413.run_aura)),
                   ("bags", _p(T412.run_bags, lock_ok=True)),
                   ("exec48", _p(T49.run_exec48)), ("exec47", _p(T49.run_exec47, SUP_X47)), ("exec46", _p(T49.run_exec46)),
                   ("centre47", _p(T49.run_centre47)), ("config48", _p(T49.run_config48)), ("mig48", _p(T410.run_mig48)),
                   ("players48", _p(run_players48)), ("geo48", _p(T49.run_geo48)), ("config49", _p(T49.run_config)),
                   ("mig49", _p(T49.run_mig)), ("exec49", _p(T49.run_exec)), ("page49", _p(T49.run_page)),
                   ("width", _p(T49.run_width)), ("order", _p(T410.run_order)), ("flows", _p(T410.run_flows)),
                   ("zones", _p(T411.run_zones)), ("balance", _p(T411.run_balance)), ("land", _p(T411.run_land)),
                   ("night", _p(T411.run_night)), ("spawn", _p(T411.run_spawn)), ("buy", _p(T411.run_buy)),
                   ("config", _p(T411.run_config)), ("gate", _p(T411.run_gate)), ("order2", _p(T411.run_order2)),
                   ("live", T411.run_live411)],
           script=__file__, live=(T46.LIVE_SH, "mods/Skyy_SkyyShards"))
