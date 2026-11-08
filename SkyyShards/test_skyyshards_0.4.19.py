"""Harness for SkyyShards 0.4.19 (the offline limit + Sell from the store - tools/shards_0_4_19_patch.py, on top of 0.4.18).
Build first:
    python tools/shards_0_4_19_patch.py && python SkyyShards/build_skyyshards_0.4.19.py
    python SkyyShards/test_skyyshards_0.4.19.py [--keep]

  S19  static   the patch re-runs to identical bytes; header / VERSION / ready line; no new registerSystem / registerCommand; line endings kept
  OF   offline  every level's speed + hours through logout + login; no offAt (crash, 0.4.18 file, first login); a crash while online; a profile
                switch; online past the old hours limit; re-settling (a co-op member's menu while the owner is away) never pays twice; a booster
                ending inside the window; the manual ceiling + seeds; every shard kind; a full store; no <kind>.offline key; a refused save; sync
  MG   config   the row + defaults; the migration: live config copy, untouched CRLF file, hand-edited, spaced, run twice, fresh file
  SL   sell     every path with a fake bazaar:fn:sell (pays, pays 0, throws, absent, partial, price missing); XP + collection = what Collect pays;
                rounding, oversized, junk; debit before pay; a refused save; Collect during a sale; a busy lock on the way back; lock released
  PG   page     the Collect rows, the Sell view, the bindings, the preview, one answer per click, Combat + switch-off without Sell, full width amount
  then 0.4.18's older phases (everybody online = 0.4.18's production): open, LB bytecode, flows3, page49, live START TWICE; A verify, C compare, AA audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util, subprocess, json, math, re, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.4.19"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "shoff", "h")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyShards-%s.jar" % VERSION)]
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyShards-0.4.18.jar")
GEN = os.path.join(HERE, "build_skyyshards_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyshards_0.4.18.py")
PATCH = os.path.join(ROOT, "tools", "shards_0_4_19_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.shards."
_argv = list(sys.argv)
_spec = importlib.util.spec_from_file_location("test_skyyshards_0_4_18", os.path.join(HERE, "test_skyyshards_0.4.18.py"))
T418 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T418)
sys.argv[:] = _argv
T417 = T418.T417
T416, T415, T413, T411, T49 = T417.T416, T417.T415, T417.T413, T417.T411, T417.T49
T414 = T416.T414
T410 = T411.T410
T48 = T49.T48
T46 = T416.T46
T418.JAR = T417.JAR = JAR
T418.SCRATCH = T416.SCRATCH = T415.SCRATCH = T417.SCRATCH = SCRATCH
OWNER = T416.OWNER
MEMBER = T46.MEMBER
VISITOR = T46.VISITOR
HRS = [8, 10, 12, 16, 20, 24]
PCT = [25, 30, 35, 40, 45, 50]
H = 3600000
FK = 2

_FX0 = T46._fixture


def _fx_on(scratch, K):
    L = _FX0(scratch, K)
    from jpype import JClass
    JClass(PKG + "ShMath").ALL_ON_TEST = True      # the older phases: the owner counts as online (0.4.18's production maths)
    return L


T46._fixture = _fx_on


# ---------------------------------------------------------------------------------------------------------- S19: static
def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyShards 0.4.19 - build script') and g.count('VERSION = "0.4.19"\n') + g.count('VERSION = "0.4.19"\r\n') == 1, "S19 header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S19 no new %r (%d)" % (w, g.count(w)))
    K.check("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.19: offline harvest limit" in g, "S19 the ready line names the round")
    K.check('("sell.enabled", "Sell button on the Collect tab", "shards", "bool"' in g, "FIX the Sell switch sits in the Shards group")
    K.check("production never counts longer between visits" not in g and "production counts at most this long between" not in g and g.count("Also caps Offline Harvest hours") == 2, "FIX2 Server Setup no longer says the hours limit visits")
    K.check('(T["EVD"], "append")' in g and '(T["BT"], "Validating")' in g, "FIX2 the audit lists the new engine calls")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S19 the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S19 line endings kept")
    K.save()


def _world(scratch, K):
    L, ou, W, p, lv = T410._world(scratch, K)
    from jpype import JClass
    M = L["ShMath"]
    M.ALL_ON_TEST = False
    M.ONLINE.clear()
    return L, ou, W, p, lv


def _disk(L, k):
    from jpype import JClass
    q = JClass("java.util.Properties")()
    f = os.path.join(L["sd"], k + ".properties")
    b = open(f, "rb").read()
    q.load(JClass("java.io.ByteArrayInputStream")(b))
    return q


# ---------------------------------------------------------------------------------------------------------- OF: the offline window
def run_off(out, jar, scratch, _home):
    from jpype import JClass, JLong, JString
    K = HK.Child(out)
    L, ou, W, p, lv = _world(os.path.join(scratch, "of"), K)
    M, St, Isl, Core, Cfg, Kind = L["ShMath"], L["ShStore"], L["ShIsl"], L["ShCore"], L["ShCfg"], L["ShKind"]
    T0 = 1790000000000
    p.setProperty("farming.auto", "1")
    p.setProperty("farming.paused", "0")
    rt = float(M.rate(FK, p, 0, JLong(T0)))
    K.check(rt > 0, "OF the test island works (%.3f / min)" % rt)

    def reset(last, stored=0):
        p.setProperty("farming.i0.stored", str(stored))
        p.setProperty("farming.i0.last", str(last))
        p.remove("farming.offAt")
        p.remove("farming.i0.offAt")
        M.ONLINE.clear()

    def st():
        return int(M.stored(FK, p, 0))

    def near(a, b, what, tol=1):
        K.check(abs(a - b) <= tol, "%s: %d (want %d)" % (what, a, b))

    # every level: 30 h away = the level's hours at its speed
    for lv_ in range(6):
        p.setProperty("farming.offline", str(lv_))
        reset(T0)
        M.ONLINE.put(OWNER, JClass("java.lang.Boolean").TRUE)
        M.logOut(JString(OWNER), JLong(T0))
        K.check(str(_disk(L, OWNER).getProperty("farming.offAt")) == str(T0) and not bool(M.ONLINE.containsKey(OWNER)), "OF level %d: the logout wrote farming.offAt and left ONLINE" % lv_)
        t1 = T0 + 30 * H
        M.logIn(JString(OWNER), JLong(t1))
        near(st(), int(math.floor(HRS[lv_] * 60 * rt * PCT[lv_] / 100.0)), "OF level %d: 30 h away = %d h at %d %%" % (lv_, HRS[lv_], PCT[lv_]))
        K.check(_disk(L, OWNER).getProperty("farming.offAt") is None and bool(M.ONLINE.containsKey(OWNER)), "OF level %d: the login cleared offAt on disk" % lv_)
        K.check(t1 - 60000 <= int(p.getProperty("farming.i0.last")) <= t1, "OF level %d: last is at the login time" % lv_)
    # a short absence
    p.setProperty("farming.offline", "0")
    reset(T0)
    M.ONLINE.put(OWNER, True)
    M.logOut(JString(OWNER), JLong(T0))
    M.logIn(JString(OWNER), JLong(T0 + 2 * H))
    near(st(), int(math.floor(2 * 60 * rt * 0.25)), "OF 2 h away at level 0 = 2 h at 25 %")
    # no offAt: a crash / 0.4.18 file / first login: everything since last = offline
    reset(T0 - 30 * H)
    M.logIn(JString(OWNER), JLong(T0))
    near(st(), int(math.floor(8 * 60 * rt * 0.25)), "OF no offAt (first login after the update): since last = offline: 8 h at 25 %")
    K.check(p.getProperty("farming.i0.offAt") is None and _disk(L, OWNER).getProperty("farming.i0.offAt") is None, "FIX2 the login clears the island's own window start")
    # FIX2: no offAt = each island's OWN last: a long-idle island cannot use up the window of the others
    it0 = p.stringPropertyNames().iterator()
    i1k = []
    while it0.hasNext():
        kk0 = str(it0.next())
        if kk0.startswith("farming.i0."):
            i1k.append(kk0.replace("farming.i0.", "farming.i1."))
            p.setProperty(i1k[-1], p.getProperty(kk0))
    K.check(bool(M.hasIsland(FK, p, 1)) and abs(float(M.rate(FK, p, 1, JLong(T0))) - rt) < 1e-6, "FIX2 the second island works")

    def two(last0, last1):
        reset(last0)
        p.setProperty("farming.i1.stored", "0")
        p.setProperty("farming.i1.last", str(last1))
        p.remove("farming.i1.offAt")

    def st1():
        return int(M.stored(FK, p, 1))
    two(T0 - 120 * H, T0 - H)
    M.logIn(JString(OWNER), JLong(T0))
    near(st1(), int(math.floor(60 * rt * 0.25)), "FIX2 no offAt: island B (settled 1 h ago) gets its hour at 25 % though island A's last is 5 days old")
    near(st(), int(math.floor(8 * 60 * rt * 0.25)), "FIX2 ... island A gets its own window: 8 h at 25 %")
    K.check(p.getProperty("farming.offAt") is None and p.getProperty("farming.i0.offAt") is None and p.getProperty("farming.i1.offAt") is None, "FIX2 ... the login cleared every window start")
    two(T0, T0 - 2 * H)
    for h_ in range(1, 31):
        M.settleAll(FK, p, JLong(T0 + h_ * H))
    K.check(str(p.getProperty("farming.i0.offAt")) == str(T0) and str(p.getProperty("farming.i1.offAt")) == str(T0 - 2 * H), "FIX2 hourly settles while away keep each island's first start")
    near(st(), int(math.floor(8 * 60 * rt * 0.25)), "FIX2 ... re-settling cannot restart island A's window", 2)
    near(st1(), int(math.floor(8 * 60 * rt * 0.25)), "FIX2 ... nor island B's", 2)
    a2 = st()
    M.logIn(JString(OWNER), JLong(T0 + 30 * H))
    K.check(abs(st() - a2) <= 1, "FIX2 ... the login after them adds nothing")
    for k1 in i1k:
        p.remove(k1)
    # FIX2: logout + login warm the Moon Blade cache before the lock (settle reads only the cache there)
    Tot0 = L["ShTotem"]
    moon = {"held": False, "n": 0}

    def moon_fn(a_):
        moon["held"] = moon["held"] or bool(St.LOCK.isHeldByCurrentThread())
        moon["n"] += 1
        return JClass("java.lang.Double").valueOf(3.0)
    Tot0.MOON_TEST = L["PyFn"](moon_fn)
    Tot0.MOON_CACHE.clear()
    reset(T0)
    M.ONLINE.put(OWNER, True)
    M.logOut(JString(OWNER), JLong(T0))
    K.check(moon["n"] == 1 and not moon["held"] and bool(Tot0.MOON_CACHE.containsKey(OWNER)), "FIX2 the logout asks for the Moon Blade once, outside the lock")
    Tot0.MOON_CACHE.clear()
    M.logIn(JString(OWNER), JLong(T0 + H))
    K.check(moon["n"] == 2 and not moon["held"] and bool(Tot0.MOON_CACHE.containsKey(OWNER)), "FIX2 the login asks for the Moon Blade once, outside the lock")
    Tot0.MOON_TEST = None
    Tot0.MOON_CACHE.clear()
    # a crash while online: ONLINE is gone at the restart
    reset(T0)
    M.ONLINE.put(OWNER, True)
    M.settleAll(FK, p, JLong(T0 + 1000))
    M.ONLINE.clear()
    s0 = st()
    M.logIn(JString(OWNER), JLong(T0 + H))
    near(st() - s0, int(math.floor(60 * rt * 0.25)), "OF a crash while online: 1 h at 25 % - a crash never gives extra", 2)
    # online: full speed, the old hours limit does not clip
    reset(T0 - 40 * H)
    M.ONLINE.put(OWNER, True)
    M.settle(FK, p, 0, JLong(T0))
    near(st(), int(math.floor(40 * 60 * rt)), "OF online past Offline Harvest's hours: 40 h at full speed")
    Cfg.MAX_OFF_SEC = 36000
    reset(T0 - 20 * H)
    M.ONLINE.put(OWNER, True)
    M.settle(FK, p, 0, JLong(T0))
    near(st(), int(math.floor(10 * 60 * rt)), "OF online: shard.maxOfflineSec still the ceiling (set to 10 h: 20 h away counts 10 h)")
    Cfg.MAX_OFF_SEC = 259200
    p.setProperty("farming.auto", "0")
    rtm = float(M.rate(FK, p, 0, JLong(T0)))
    reset(T0 - 10 * H)
    M.ONLINE.put(OWNER, True)
    M.settle(FK, p, 0, JLong(T0))
    near(st(), int(math.floor(2 * 60 * rtm)), "OF before Automation, online: shard.manualOfflineSec 2 h as before")
    # before Automation, offline: the manual ceiling + the planted part uses seeds as before
    p.setProperty("farming.offline", "5")
    reset(T0)
    M.ONLINE.put(OWNER, True)
    M.logOut(JString(OWNER), JLong(T0))
    M.logIn(JString(OWNER), JLong(T0 + 30 * H))
    K.check(st() <= int(math.floor(2 * 60 * rtm * 0.5)) + 1 and st() >= 0, "OF before Automation, offline: at most 2 h at level 5's 50 %% (%d, seeds may cut it)" % st())
    p.setProperty("farming.auto", "1")
    p.setProperty("farming.offline", "0")
    # re-settling: a co-op member's menu / the particles while the owner is away: the same total, never a second payment
    reset(T0)
    M.ONLINE.put(OWNER, True)
    M.logOut(JString(OWNER), JLong(T0))
    for h_ in range(1, 31):
        M.settleAll(FK, p, JLong(T0 + h_ * H))
    M.settleAll(FK, p, JLong(T0 + 30 * H))
    near(st(), int(math.floor(8 * 60 * rt * 0.25)), "OF 30 hourly settles while away (a co-op member's menu) = one window: 8 h at 25 %", 2)
    a0 = st()
    M.logIn(JString(OWNER), JLong(T0 + 30 * H))
    K.check(abs(st() - a0) <= 1, "OF the login after them adds nothing more (%d -> %d)" % (a0, st()))
    M.settleAll(FK, p, JLong(T0 + 30 * H))
    a1 = st()
    M.settleAll(FK, p, JLong(T0 + 30 * H))
    K.check(st() == a1, "OF a settle at the same moment changes nothing")
    # a second login / logout = nothing (a world change is no logout)
    w0 = int(St.WRITES.get())
    M.logIn(JString(OWNER), JLong(T0 + 31 * H))
    keys = JClass("java.util.HashSet")()
    keys.add(OWNER)
    M.sync(keys, JLong(T0 + 31 * H))
    M.sync(keys, JLong(T0 + 31 * H))
    K.check(int(St.WRITES.get()) == w0, "OF the same player seen again (every second, world changes): no write")
    # the part of an item in progress carries over, neither lost nor multiplied
    reset(T0)
    M.ONLINE.put(OWNER, True)
    M.logOut(JString(OWNER), JLong(T0))
    frac_ms = int(30000 / (rt * 0.25))                       # half an item of offline time
    M.logIn(JString(OWNER), JLong(T0 + frac_ms))
    lst = int(p.getProperty("farming.i0.last"))
    now_ = T0 + frac_ms
    K.check(st() == 0 and abs((now_ - lst) * rt / 60000.0 - 0.5) < 0.02, "OF half an item in progress: carried over as half an item of full-speed time (%.3f)" % ((now_ - lst) * rt / 60000.0))
    # a booster that ends inside the window
    tot0 = str(p.getProperty("farming.i0.totems"))
    Tot = L["ShTotem"]
    bparts = tot0.split(",")
    f0 = bparts[0].split(":")
    f0[4] = str(T0 + H)
    p.setProperty("farming.i0.totems", ",".join([":".join(f0)] + bparts[1:]))
    rA, rB = float(M.rate(FK, p, 0, JLong(T0 + 1))), float(M.rate(FK, p, 0, JLong(T0 + 2 * H)))
    K.check(rA > rB, "OF the booster counts before its end (%.3f > %.3f)" % (rA, rB))
    reset(T0)
    M.ONLINE.put(OWNER, True)
    M.logOut(JString(OWNER), JLong(T0))
    M.logIn(JString(OWNER), JLong(T0 + 30 * H))
    near(st(), int(math.floor((60 * rA + 7 * 60 * rB) * 0.25)), "OF a booster ending 1 h into the window: 1 h boosted + 7 h plain, all at 25 %", 2)
    p.setProperty("farming.i0.totems", tot0)
    # no <kind>.offline key = level 5
    p.remove("farming.offline")
    reset(T0)
    M.ONLINE.put(OWNER, True)
    M.logOut(JString(OWNER), JLong(T0))
    M.logIn(JString(OWNER), JLong(T0 + 30 * H))
    near(st(), int(math.floor(24 * 60 * rt * 0.5)), "OF no farming.offline key (owned before 0.4.9) = level 5: 24 h at 50 %")
    p.setProperty("farming.offline", "0")
    # a full store stops production; items stored are never touched
    cap = int(M.capOf(FK, p, 0))
    reset(T0, cap)
    M.ONLINE.put(OWNER, True)
    M.logOut(JString(OWNER), JLong(T0))
    M.logIn(JString(OWNER), JLong(T0 + 8 * H))
    K.eq(st(), cap, "OF a full store stays exactly full")
    big = cap + 500
    reset(T0, big)
    M.logIn(JString(OWNER), JLong(T0 + H))
    K.eq(st(), big, "OF a store above its cap is never cut")
    # a profile switch away + back through sync (the tick's path)
    k2 = OWNER + "-p2"
    q = St.get(k2)
    it = p.stringPropertyNames().iterator()
    while it.hasNext():
        kk_ = it.next()
        if str(kk_).startswith("farming."):
            q.setProperty(kk_, p.getProperty(kk_))
    M.ONLINE.clear()
    M.ONLINE.put(OWNER, True)
    q.setProperty("farming.i0.stored", "0"); q.setProperty("farming.i0.last", str(T0)); q.remove("farming.offAt")
    p.setProperty("farming.i0.stored", "0"); p.setProperty("farming.i0.last", str(T0)); p.remove("farming.offAt")
    q.setProperty("farming.offAt", str(T0))
    keys = JClass("java.util.HashSet")()
    keys.add(k2)
    M.sync(keys, JLong(T0))                                  # the owner switched to profile 2
    K.check(not bool(M.ONLINE.containsKey(OWNER)) and bool(M.ONLINE.containsKey(k2)) and str(p.getProperty("farming.offAt")) == str(T0) and q.getProperty("farming.offAt") is None,
            "OF a profile switch: profile 1 offline (offAt), profile 2 online")
    M.settleAll(FK, q, JLong(T0 + 2 * H))
    K.check(abs(int(M.stored(FK, q, 0)) - int(math.floor(2 * 60 * rt))) <= 1, "OF ... profile 2 runs at full speed")
    keys2 = JClass("java.util.HashSet")()
    keys2.add(OWNER)
    M.sync(keys2, JLong(T0 + 2 * H))                         # and back
    near(st(), int(math.floor(2 * 60 * rt * 0.25)), "OF ... switching back: profile 1 made 2 h at 25 %")
    K.check(str(q.getProperty("farming.offAt")) == str(T0 + 2 * H), "OF ... profile 2 is the offline one now")
    M.ONLINE.remove(k2)
    # a refused save at logout: memory has the window, the numbers stay safe
    reset(T0)
    M.ONLINE.put(OWNER, True)
    St.FAIL_TEST = True
    M.logOut(JString(OWNER), JLong(T0))
    St.FAIL_TEST = False
    K.check(not bool(M.ONLINE.containsKey(OWNER)) and str(p.getProperty("farming.offAt")) == str(T0), "OF a refused save at logout: the window is open in memory, no crash")
    # the stop: everybody out
    reset(T0)
    M.ONLINE.put(OWNER, True)
    M.allOff(JLong(T0))
    K.check(int(M.ONLINE.size()) == 0 and str(_disk(L, OWNER).getProperty("farming.offAt")) == str(T0), "OF a graceful stop logs everybody out (offAt on disk)")
    # FIX: a busy lock at the stop is said once, nothing is written, the window stays the safe "no offAt"
    reset(T0)
    M.ONLINE.clear()
    M.ONLINE.put(OWNER, True)
    p.remove("farming.offAt")
    Cfg_ = JClass(PKG + "ShCfg")
    Cfg_.WARNED.remove("logoutstop")
    hold = {}
    T414._grab(St.LOCK, hold)
    Lk = JClass(PKG + "ShLock")
    sv_w = Lk.WAIT_MS
    Lk.WAIT_MS = 20
    M.allOff(JLong(T0))
    Lk.WAIT_MS = sv_w
    T414._release(hold)
    K.check(bool(Cfg_.WARNED.containsKey("logoutstop")) and p.getProperty("farming.offAt") is None and bool(M.ONLINE.containsKey(OWNER)), "FIX a stop against a busy lock warns once and writes no offAt")
    M.ONLINE.clear()
    # FIX: the file's pkey is the key it is read under; a missing key is offline
    k3 = OWNER + "-p3"
    q3 = St.get(k3)
    q3.setProperty("pkey", OWNER)
    K.check(St.save(JString(k3), q3) is None, "FIX ... the copied file is written")
    St.CACHE.remove(k3)
    q3 = St.get(k3)
    M.ONLINE.put(k3, True)
    K.check(str(q3.getProperty("pkey")) == k3 and bool(M.isOn(q3)), "FIX a file restored under another profile counts as that profile (online there)")
    M.ONLINE.remove(k3)
    K.check(not bool(M.isOn(JClass("java.util.Properties")())), "FIX no pkey at all = not online (the safe direction)")
    # every shard kind
    for kd in range(int(Kind.N)):
        name = str(Kind.KEYS[kd])
        pk = OWNER[:-12] + "%012d" % (kd + 77)
        pq = St.get(pk)
        St.LOCK.lock()
        try:
            M.starter(kd, pq, JLong(T0))
            pq.setProperty(name + ".auto", "1")
            pq.setProperty(name + ".offline", "2")
            pq.setProperty(name + ".placed", "skyy-island-x|1|2|3")
        finally:
            St.LOCK.unlock()
        wk = str(Kind.WORKER[kd])
        if not str(pq.getProperty(name + ".i0.totems") or ""):
            pq.setProperty(name + ".i0.totems", "%s:1:::0:tt%04d" % (wk, kd))
        r0 = float(M.rate(kd, pq, 0, JLong(T0)))
        if r0 <= 0:
            K.notes.append("OF kind %s has no worker rate in the fixture" % name)
            continue
        M.ONLINE.put(pk, True)
        pq.setProperty(name + ".i0.stored", "0")
        pq.setProperty(name + ".i0.last", str(T0))
        M.logOut(JString(pk), JLong(T0))
        M.logIn(JString(pk), JLong(T0 + 40 * H))
        near(int(M.stored(kd, pq, 0)), int(math.floor(12 * 60 * r0 * 0.35)), "OF %s Shard: 40 h away at level 2 = 12 h at 35 %%" % name, 2)
        M.ONLINE.remove(pk)
    K.save()


# ---------------------------------------------------------------------------------------------------------- MG: config + migration
def run_mig(out, jar, scratch, _home):
    from jpype import JClass
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    K = HK.Child(out)
    Mig = JClass(PKG + "ShMig0419")
    OLD, NEW = "12,18,24,36,48,72", "8,10,12,16,20,24"
    MK = "skyyshards-0.4.19-offline"
    nf = [0]

    def world(b_):
        nf[0] += 1
        home = os.path.join(scratch, "m%d" % nf[0], "mods", "Skyy_SkyyShards")
        os.makedirs(home)
        Cfg, path = T49.T42.kit_home(home)
        f = os.path.join(home, "config.properties")
        if b_ is not None:
            open(f, "wb").write(b_)
        return home, f, Cfg, path

    def props(b_):
        P_ = JClass("java.util.Properties")()
        P_.load(JClass("java.io.ByteArrayInputStream")(b_))
        return dict((str(k), str(P_.getProperty(k))) for k in P_.stringPropertyNames())

    def hist(home):
        hd = os.path.join(home, "config-history")
        return [open(os.path.join(hd, n), "rb").read() for n in sorted(os.listdir(hd)) if n.endswith(".bak")] if os.path.isdir(hd) else []

    def chg(home):
        f = os.path.join(home, "config-changes.log")
        return [l.split("\t") for l in open(f, encoding="utf8").read().splitlines()] if os.path.isfile(f) else []
    # a fresh file
    home, f, Cfg, path = world(None)
    Cfg.loadCfg(True)
    t = open(f, "rb").read().replace(b"\r\n", b"\n").decode("latin-1").split("\n")
    K.check("up.offline.hours=" + NEW in t and "up.offline.pct=25,30,35,40,45,50" in t and "sell.enabled=true" in t, "MG a fresh file holds the new rows")
    K.check([float(x) for x in Cfg.OFF_H] == [float(x) for x in HRS] and [int(x) for x in Cfg.OFF_PCT] == PCT and bool(Cfg.SELL_ON), "MG the fields read")
    b0 = open(f, "rb").read()
    K.check(b0.count(MK.encode()) == 1, "MG the marker once in a fresh file")
    K.check(str(Mig.run(path(f))) == "" and open(f, "rb").read() == b0, "MG a fresh file: nothing to do")
    open(f, "a", encoding="latin-1").write("\nup.offline.pct=10,junk\nsell.enabled=false\n")
    Cfg.loadCfg(False)
    K.check([int(x) for x in Cfg.OFF_PCT] == PCT and not bool(Cfg.SELL_ON), "MG a bad pct row: the defaults, a WARN; sell.enabled false read live")
    # the live config copy
    live = os.path.join(T46.LIVE_SH, "config.properties")
    A_ = open(live, "rb").read() if os.path.isfile(live) else None
    K.check(A_ is not None, "MG the live config.properties exists (read only, copied)")
    if A_ is not None:
        home, f, Cfg, path = world(A_)
        r = str(Mig.run(path(f)))
        b1 = open(f, "rb").read()
        pa, pb = props(A_), props(b1)
        was = pa.get("up.offline.hours")
        moved = was is not None and was.replace(" ", "") == OLD
        K.check((pb.get("up.offline.hours") == NEW) == bool(moved) or was == NEW, "MG the live config: %s -> %s: %s" % (was, pb.get("up.offline.hours"), r[:160]))
        K.check(all(pb[k] == pa[k] for k in pa if k != "up.offline.hours") and len(pb) == len(pa), "MG the live config: every other line the same")
        K.check(b1.count(MK.encode()) == 1 and (b"\r\n" in A_) == (b"\r\n" in b1), "MG the marker once, line endings kept")
        K.check(str(Mig.run(path(f))) == "" and open(f, "rb").read() == b1, "MG run twice = once")
    # an untouched CRLF file
    old = ("# keep me\r\nshard.on=true\r\nup.offline.hours=%s\r\nup.offline.steps=3,5,6,7,8\r\n" % OLD).encode("latin-1")
    home, f, Cfg, path = world(old)
    r = str(Mig.run(path(f)))
    b2 = open(f, "rb").read()
    K.check(props(b2)["up.offline.hours"] == NEW and b2.startswith(b"# keep me\r\nshard.on=true\r\n") and b"\n" not in b2.replace(b"\r\n", b""), "MG the old default moved, CRLF + every other byte kept: %s" % r[:120])
    K.check(any(h == old for h in hist(home)) and len([c for c in chg(home) if len(c) > 6 and c[1] == "SkyyShards 0.4.19"]) == 1, "MG History first, one change-log line (Undo)")
    # spaced default = still the default
    home, f, Cfg, path = world(("up.offline.hours = 12, 18, 24, 36, 48, 72\n").encode("latin-1"))
    Mig.run(path(f))
    K.check(props(open(f, "rb").read())["up.offline.hours"] == NEW, "MG a spaced old default still matched")
    # hand-edited: kept + logged
    home, f, Cfg, path = world(b"up.offline.hours=6,6,6,6,6,6\n")
    r = str(Mig.run(path(f)))
    b3 = open(f, "rb").read()
    K.check(props(b3)["up.offline.hours"] == "6,6,6,6,6,6" and "kept - an admin changed it" in r and b3.count(MK.encode()) == 1, "MG hand-edited kept + logged, the marker added: %s" % r[-120:])
    K.save()


# ---------------------------------------------------------------------------------------------------------- SL: sell
def run_sell(out, jar, scratch, _home):
    from jpype import JClass, JLong, JString, JArray, JObject, JDouble
    K = HK.Child(out)
    L, ou, W, p, lv = _world(os.path.join(scratch, "sl"), K)
    M, St, Isl, Core, Cfg, Kind, Tot = L["ShMath"], L["ShStore"], L["ShIsl"], L["ShCore"], L["ShCfg"], L["ShKind"], L["ShTotem"]
    fns, br, PyFn = L["fns"], L["br"], L["PyFn"]
    T0 = 1790000000000
    Core.NOW_TEST = T0
    M.ONLINE.put(OWNER, True)
    p.setProperty("farming.auto", "1")
    got = {"coll": {}, "xp": 0, "ok": True, "calls": [], "mode": "pay", "held": False, "hook": None}

    def coll_add(a):
        if not got["ok"]:
            return L["Bool"].FALSE
        got["coll"][str(a[1])] = got["coll"].get(str(a[1]), 0) + int(a[2])
        return L["Bool"].TRUE

    def xp_add(a):
        got["xp"] += int(a[2])
        return L["Bool"].TRUE
    fns.put("coll:fn:add", PyFn(coll_add))
    fns.put("skill:fn:addxp", PyFn(xp_add))
    PRICE = 5

    def sellfn(a):
        got["held"] = got["held"] or bool(St.LOCK.isHeldByCurrentThread())
        q = int(a[2])
        got["calls"].append((str(a[0]), str(a[1]), q))
        if got["hook"]:
            h, got["hook"] = got["hook"], None
            h()
        m = got["mode"]
        if m == "zero":
            return JLong(0)
        if m == "throw":
            raise RuntimeError("bazaar broke")
        if m == "partial":
            return JArray(JLong)([111, q // 2])
        return JLong(q * PRICE)
    item = str(Core.sellItem(FK, p, 0))
    br.put("bazaar:sell:" + item, JLong(PRICE))
    ci = str(Isl.PROD[int(Isl.ty(FK, p, 0))])

    def setup(s):
        p.setProperty("farming.i0.stored", str(s))
        p.setProperty("farming.i0.last", str(T0))
        p.remove("farming.i0.xpn"); p.remove("farming.i0.xpw")
        got["coll"].clear(); got["xp"] = 0; got["calls"][:] = []; got["mode"] = "pay"; got["held"] = False

    def st():
        return int(M.stored(FK, p, 0))

    def disk():
        return int(_disk(L, OWNER).getProperty("farming.i0.stored"))

    def sell(mode, txt=""):
        return str(Core.sell(ou, JString(OWNER), FK, 0, mode, JString(txt)))
    # absent / not sold
    setup(1000)
    K.check(sell(1).startswith("-The Bazaar cannot buy") and st() == 1000, "SL bazaar:fn:sell absent: says so, nothing moves")
    K.check(str(Core.sellOpenNo(JString(OWNER), FK, 0)).startswith("-The Bazaar cannot buy"), "SL ... the row's Sell says the same")
    fns.put("bazaar:fn:sell", PyFn(sellfn))
    br.remove("bazaar:sell:" + item)
    r = sell(1)
    K.check(r.startswith("-The Bazaar does not buy") and st() == 1000 and not got["calls"], "SL an item the Bazaar does not list: says so, nothing moves: %s" % r)
    br.put("bazaar:sell:" + item, JLong(PRICE))
    # pays: half of an odd amount rounds down, XP + collection for that amount, the file written before the Bazaar
    setup(1001)
    xi = float(M.xpAvg(FK, p, 0, JLong(T0)))
    seen = {}
    got["hook"] = lambda: seen.update(d=disk())
    r = sell(0)
    pct = int(Cfg.XP_PCT)
    wxp = int(math.floor(500 * xi * pct / 100.0 + 1e-9))
    K.check(st() == 501 and disk() == 501 and seen.get("d") == 501, "SL half of 1,001 = 500; the debit was on disk BEFORE the Bazaar was called (%s)" % seen)
    K.check(got["calls"] == [(OWNER, item, 500)], "SL the call: UUID, item id, Long 500: %s" % got["calls"])
    K.check(got["xp"] == wxp and got["coll"].get(ci) == 500, "SL XP %d (want %d) + collection %s" % (got["xp"], wxp, got["coll"]))
    K.check(r.startswith("+Sold 500") and "2,500 coins" in r and "XP" in r, "SL the status line: %s" % r)
    K.check(not got["held"], "SL the shard lock is released during the Bazaar call")
    log = open(os.path.join(os.path.dirname(L["sd"]), "collect.log"), encoding="utf8").read()
    K.check(" SELL debit 500 " in log and " SELL paid 2500 coins for 500 " in log, "SL collect.log has the sale")
    # the same amount through Collect pays exactly the same XP + collection (including recorded XP per item)
    setup(800)
    p.setProperty("farming.i0.xpn", "800"); p.setProperty("farming.i0.xpw", str(800 * xi * 2.0))
    xi2 = float(M.xpAvg(FK, p, 0, JLong(T0)))
    sell(1)
    xS, cS = got["xp"], dict(got["coll"])
    setup(800)
    p.setProperty("farming.i0.xpn", "800"); p.setProperty("farming.i0.xpw", str(800 * xi * 2.0))
    cs = L["inv"](45, 45)
    rc = str(Core.collect(ou, JString(OWNER), FK, 0, cs))
    K.check(got["xp"] == xS and got["coll"] == cS and rc.startswith("+"), "SL 800 sold pays what 800 Collected pays: XP %d = %d, collection %s = %s" % (xS, got["xp"], cS, got["coll"]))
    K.check(abs(xi2 - min(2.0 * xi, float(M.xpCapOf()))) < 1e-6, "SL ... at the recorded average XP per item (%.2f)" % xi2)
    # the average stays with what is left
    setup(800)
    p.setProperty("farming.i0.xpn", "800"); p.setProperty("farming.i0.xpw", str(800 * xi * 2.0))
    sell(2, "300")
    K.check(st() == 500 and abs(float(M.xpAvg(FK, p, 0, JLong(T0))) - xi2) < 1e-6, "SL after selling 300 the 500 left keep their XP per item")
    # pays 0, throws, partial: back
    setup(600)
    got["mode"] = "zero"
    r = sell(1)
    K.check(st() == 600 and disk() == 600 and got["xp"] == 0 and not got["coll"] and r.startswith("-The Bazaar bought nothing"), "SL pays 0: everything back, no XP: %s" % r)
    setup(600)
    got["mode"] = "throw"
    r = sell(1)
    K.check(st() == 600 and got["xp"] == 0 and r.startswith("-The Bazaar bought nothing"), "SL throws: everything back, no XP")
    setup(600)
    got["mode"] = "partial"
    r = sell(1)
    K.check(st() == 300 and disk() == 300 and got["coll"].get(ci) == 300 and "only part" in r and "111 coins" in r, "SL partial (half taken): only what was paid left the store; XP + collection for that part: %s" % r)
    # a refused save pays nothing
    setup(400)
    St.FAIL_TEST = True
    r = sell(1)
    St.FAIL_TEST = False
    K.check(st() == 400 and not got["calls"] and got["xp"] == 0 and r.startswith("-Sale failed"), "SL a refused save: nothing taken, the Bazaar not called: %s" % r)
    # amounts
    setup(1000)
    for bad in ("abc", "0", "-5", "1.5", "", "99999999999999999999"):
        r = sell(2, bad)
        K.check(r.startswith("-Type a whole number") and st() == 1000 and not got["calls"], "SL amount %r refused" % bad)
    r = sell(2, "1001")
    K.check(r.startswith("-Only 1,000 stored") and st() == 1000 and not got["calls"], "SL more than stored refused: %s" % r)
    r = sell(2, "1,000")
    K.check(st() == 0 and got["calls"][-1][2] == 1000, "SL an amount with a comma")
    r = sell(1)
    K.check(r.startswith("=Nothing is stored") and len(got["calls"]) == 1, "SL a second Sell all (double click): nothing there, nothing paid: %s" % r)
    setup(1)
    r = sell(0)
    K.check(r.startswith("-Half of 1") and st() == 1, "SL half of 1 refused: %s" % r)
    # settled first
    setup(0)
    p.setProperty("farming.i0.last", str(T0 - H))
    rt = float(M.rate(FK, p, 0, JLong(T0)))
    sell(1)
    K.check(abs(got["calls"][-1][2] - int(60 * rt)) <= 1, "SL settled first: sold the hour's %d items" % got["calls"][-1][2])
    # bonus finds + legacy stay
    setup(500)
    p.setProperty("farming.i0.ench", "40")
    p.setProperty("farming.i0.legacy", "Plant_Crop_Wheat_Item:7")
    sell(1)
    K.check(int(M.ench(FK, p, 0)) == 40 and str(p.getProperty("farming.i0.legacy")) == "Plant_Crop_Wheat_Item:7", "SL Enchanted / bonus finds + legacy stay for Collect")
    p.remove("farming.i0.ench"); p.remove("farming.i0.legacy")
    # Collect during the sale (two pages): the debit came first, nothing doubles
    setup(1000)
    cs = L["inv"](45, 45)
    got["hook"] = lambda: Core.collect(ou, JString(OWNER), FK, 0, cs)
    r = sell(2, "400")
    K.check(st() == 0 and int(L["count"](cs, ci)) + 0 == 600 and got["calls"][-1][2] == 400, "SL Collect during a sale of 400 of 1,000: 600 collected, nothing doubled (%d)" % int(L["count"](cs, ci)))
    # not sold + a busy lock: queued, the tick puts them back
    setup(700)
    got["mode"] = "zero"
    hold = {}

    def grab():
        T414._grab(St.LOCK, hold)
    got["hook"] = grab
    sv_w, sv_o = JClass(PKG + "ShLock").WAIT_MS, JClass(PKG + "ShLock").WORLD_MS
    JClass(PKG + "ShLock").WAIT_MS = 20
    r = sell(1)
    q0 = int(Core.SELLQ.size())
    T414._release(hold)
    JClass(PKG + "ShLock").WAIT_MS = sv_w
    K.check(q0 == 1 and st() == 0, "SL the lock busy on the way back: queued, not lost (%d queued)" % q0)
    Core.flushSell()
    K.check(st() == 700 and disk() == 700 and int(Core.SELLQ.size()) == 0, "SL ... the tick put all 700 back")
    # FIX: the island changed while the sale ran - the items wait as legacy (the old item), never in the new item's store
    t0 = str(p.getProperty("farming.i0.type"))
    t1 = None
    for t_ in range(int(Isl.LAD0[FK]), int(Isl.LAD0[FK]) + int(Isl.LADN[FK])):
        if str(Isl.PROD[t_]) != ci:
            t1 = str(Isl.KEY[t_])
            break
    K.check(t1 is not None, "FIX the farming ladder has another item (%s)" % t1)

    def retype():
        p.setProperty("farming.i0.type", t1)
    setup(700)
    got["mode"] = "zero"
    got["hook"] = retype
    r = sell(1)
    K.check(st() == 0 and str(p.getProperty("farming.i0.legacy")) == ci + ":700" and str(_disk(L, OWNER).getProperty("farming.i0.legacy")) == ci + ":700", "FIX retyped during the sale: 700 wait as the old item, the new store stays 0: %s" % r)
    p.remove("farming.i0.legacy"); p.setProperty("farming.i0.type", t0)
    # ... the same through the busy-lock queue
    setup(700)
    got["mode"] = "zero"
    hold = {}

    def retype_grab():
        retype()
        T414._grab(St.LOCK, hold)
    got["hook"] = retype_grab
    JClass(PKG + "ShLock").WAIT_MS = 20
    r = sell(1)
    q1 = int(Core.SELLQ.size())
    T414._release(hold)
    JClass(PKG + "ShLock").WAIT_MS = sv_w
    Core.flushSell()
    K.check(q1 == 1 and st() == 0 and str(p.getProperty("farming.i0.legacy")) == ci + ":700" and int(Core.SELLQ.size()) == 0, "FIX retyped + busy lock: queued with its item, then waits as the old item (%d queued)" % q1)
    p.remove("farming.i0.legacy"); p.setProperty("farming.i0.type", t0)
    # ... the island gone; legacy of the same item adds up; another item's legacy moves it to a free slot
    setup(700)
    got["mode"] = "zero"
    got["hook"] = lambda: p.remove("farming.i0.type")
    sell(1)
    K.check(str(p.getProperty("farming.i0.legacy")) == ci + ":700" and int(M.stored(FK, p, 0)) == 0, "FIX the island gone during the sale: the items wait for Collect all")
    p.remove("farming.i0.legacy"); p.setProperty("farming.i0.type", t0)
    setup(700)
    p.setProperty("farming.i0.legacy", ci + ":5")
    got["mode"] = "zero"
    got["hook"] = retype
    sell(1)
    K.check(str(p.getProperty("farming.i0.legacy")) == ci + ":705", "FIX ... adds to a waiting legacy of the same item")
    p.remove("farming.i0.legacy"); p.setProperty("farming.i0.type", t0)
    setup(700)
    p.setProperty("farming.i0.legacy", "Other_Item:9")
    got["mode"] = "zero"
    got["hook"] = retype
    sell(1)
    K.check(str(p.getProperty("farming.i0.legacy")) == "Other_Item:9" and str(p.getProperty("farming.i1.legacy")) == ci + ":700", "FIX ... another item waiting there: the next free slot")
    p.remove("farming.i0.legacy"); p.remove("farming.i1.legacy"); p.setProperty("farming.i0.type", t0)
    # FIX: what was made during the sale keeps its own XP per item
    setup(600)
    xi3 = float(M.xpAvg(FK, p, 0, JLong(T0)))
    aHi = min(2.0 * xi3, float(M.xpCapOf()))

    def made_meanwhile():
        p.setProperty("farming.i0.stored", "100"); p.setProperty("farming.i0.xpn", "100"); p.setProperty("farming.i0.xpw", str(100 * aHi))
    got["mode"] = "zero"
    got["hook"] = made_meanwhile
    sell(1)
    K.check(st() == 700 and str(p.getProperty("farming.i0.xpn")) == "700" and abs(float(p.getProperty("farming.i0.xpw")) - (100 * aHi + 600 * xi3)) < 1e-6, "FIX back into a store with newer items: XP weighted (%s)" % p.getProperty("farming.i0.xpw"))
    # FIX: an unreadable file is said once, the entry waits (items never dropped)
    Cfg.WARNED.remove("sellback")
    Core.sellBackQ(JString("bad/key"), FK, 0, JLong(5), JDouble(1.0), JString(ci))
    Core.flushSell()
    K.check(int(Core.SELLQ.size()) == 1 and bool(Cfg.WARNED.containsKey("sellback")), "FIX an unreadable file: warned once, still queued")
    K.check(int(Core.SELLQ.peek()[6]) == T0 + 60000, "FIX2 ... the next try is a minute away, the second's flush left it alone (%s)" % Core.SELLQ.peek()[6])
    Core.NOW_TEST = T0 + 60000
    Core.flushSell()
    K.check(int(Core.SELLQ.size()) == 1 and int(Core.SELLQ.peek()[6]) == T0 + 120000, "FIX2 ... tried again after the minute, still queued, never dropped")
    Core.flushSellAt(JLong(JClass("java.lang.Long").MAX_VALUE))
    K.check(int(Core.SELLQ.size()) == 1 and int(Core.SELLQ.peek()[6]) == T0 + 120000, "FIX2 ... the server stop tries it whatever the wait")
    Core.NOW_TEST = T0
    Core.SELLQ.clear()
    # the gates
    setup(500)
    Cfg.SELL_ON = False
    K.check(sell(1).startswith("-Selling from the store is switched off") and st() == 500, "SL sell.enabled off: refused")
    Cfg.SELL_ON = True
    br.put("profile:busy:" + OWNER, L["Bool"].TRUE)
    K.check(sell(1).startswith("-Your profile is still loading") and st() == 500, "SL a profile switch in progress: refused")
    br.remove("profile:busy:" + OWNER)
    vu = L["UUID"].fromString(VISITOR)
    r = str(Core.sell(vu, JString(OWNER), FK, 0, 1, JString("")))
    K.check(r.startswith("-") and st() == 500, "SL a visitor: refused: %s" % r)
    CK = int(JClass(PKG + "ShCombat").CK)
    r = str(Core.sell(ou, JString(OWNER), CK, 0, 1, JString("")))
    K.check(r.startswith("-Combat shards"), "SL Combat: refused: %s" % r)
    K.save()


# ---------------------------------------------------------------------------------------------------------- PG: page
def run_page(out, jar, scratch, _home):
    from jpype import JClass, JLong, JString
    K = HK.Child(out)
    L, ou, W, p, lv = _world(os.path.join(scratch, "pg"), K)
    M, St, Isl, Core, Cfg, Page = L["ShMath"], L["ShStore"], L["ShIsl"], L["ShCore"], L["ShCfg"], L["ShPage"]
    fns, br, PyFn = L["fns"], L["br"], L["PyFn"]
    T0 = 1790000000000
    Core.NOW_TEST = T0
    M.ONLINE.put(OWNER, True)
    p.setProperty("farming.auto", "1"); p.setProperty("farming.offline", "0")
    p.setProperty("farming.i0.stored", "48874"); p.setProperty("farming.i0.last", str(T0)); p.setProperty("farming.i0.ench", "40")
    item = str(Core.sellItem(FK, p, 0))
    br.put("bazaar:sell:" + item, JLong(5))
    fns.put("bazaar:fn:sell", PyFn(lambda a: JLong(int(a[2]) * 5)))
    fns.put("coll:fn:add", PyFn(lambda a: L["Bool"].TRUE))
    fns.put("skill:fn:addxp", PyFn(lambda a: L["Bool"].TRUE))
    pg = Page(ou, W)
    pg.kind = FK
    pg.view = 0

    def click(a, **extra):
        d = {"a": a}
        d.update(extra)
        pg.handleDataEvent(None, None, json.dumps(d))
        r = T410.full(pg)
        K.check(not r["miss"] and not r["unbound"], "PG %s: the page walks clean %s %s" % (a, r["miss"][:2], r["unbound"][:2]))
        return T49._build(pg)
    bd = click("tab0")
    K.check(bool(pg.cSell) and not bool(pg.svOn) and T49._act(bd["datas"], "#SkyyShCRow0Sell") == "sopen0" and T49._act(bd["datas"], "#SkyyShCRow0Btn") == "col0" and T49._act(bd["datas"], "#SkyyShCAll") == "colall",
            "PG the row has Sell (sopen0) next to Collect; Collect all still shows")
    K.check(str(pg.cCap) == "Rates below are online. Offline: 25 % speed for 8 hours, then it stops.", "PG the offline line: %s" % pg.cCap)
    K.check("Width: 220" in bd["mk"] and str(pg.cAmt[0]).startswith("48,874 / "), "PG the amount column is 220 wide: %s" % pg.cAmt[0])
    fns.remove("bazaar:fn:sell")
    bd = click("sopen0")
    K.check(not bool(pg.svOn) and int(pg.sellSlot) == -1 and str(pg.stText).startswith("The Bazaar cannot buy"), "PG no bazaar:fn:sell: the status line says so, no Sell view")
    fns.put("bazaar:fn:sell", PyFn(lambda a: JLong(int(a[2]) * 5)))
    bd = click("sopen0")
    K.check(bool(pg.svOn) and int(pg.sellSlot) == 0 and "SkyyShSHalf" in bd["mk"] and "SkyyShCAll" not in bd["binds"] and "#SkyyShCAll" not in bd["binds"], "PG Sell opens the Sell view instead of Collect all")
    K.check(T49._act(bd["datas"], "#SkyyShSHalf") == "shalf" and T49._act(bd["datas"], "#SkyyShSAll") == "sall" and T49._act(bd["datas"], "#SkyyShSBack") == "sback", "PG the buttons bound")
    K.check('"@SAmt"' in bd["datas"]["#SkyyShSSell"].replace(" ", "") and "#SkyyShSAmt.Value" in bd["datas"]["#SkyyShSSell"], "PG Sell amount carries the field's value: %s" % bd["datas"]["#SkyyShSSell"])
    K.check("Stored: 48,874" == str(pg.sv[2]) and str(pg.sv[3]).startswith("Coins each: 5") and "bonus finds stay" in str(pg.sv[4]), "PG the view: %s / %s / %s" % (pg.sv[2], pg.sv[3], pg.sv[4]))
    K.check(str(pg.sv[5]).startswith("Half (24,437): about 122,185 coins") and "collection +24,437" in str(pg.sv[6]) and "XP" in str(pg.sv[6]), "PG preview half: %s / %s" % (pg.sv[5], pg.sv[6]))
    K.check(str(pg.sv[7]).startswith("All (48,874): about 244,370 coins"), "PG preview all: %s" % pg.sv[7])
    bd = click("sprev", **{"@SAmt": "1000"})
    K.check(str(pg.sv[9]).startswith("Amount (1,000): about 5,000 coins") and str(pg.stText) == "" or str(pg.sv[9]).startswith("Amount (1,000)"), "PG Enter previews: %s" % pg.sv[9])
    K.check(bd["sets"].get("#SkyyShSAmt.Value") == "1000", "PG the typed number stays in the field")
    bd = click("sprev", **{"@SAmt": "99999999"})
    K.check("more than is stored" in str(pg.sv[9]), "PG a preview over the store says so")
    bd = click("samt", **{"@SAmt": "abc"})
    K.check(str(pg.stText) == "Type a whole number above 0." and int(M.stored(FK, p, 0)) == 48874 and bool(pg.svOn), "PG a bad amount: one plain line, the view stays")
    bd = click("samt", **{"@SAmt": "874"})
    K.check(str(pg.stText).startswith("Sold 874") and int(M.stored(FK, p, 0)) == 48000 and str(pg.sellTxt) == "", "PG Sell amount sells, clears the field: %s" % pg.stText)
    bd = click("shalf")
    K.check(int(M.stored(FK, p, 0)) == 24000, "PG Sell half")
    bd = click("sback")
    K.check(not bool(pg.svOn) and "#SkyyShCAll" in bd["binds"], "PG Done selling = Collect all again")
    bd = click("sopen0")
    bd = click("tab1")
    K.check(int(pg.sellSlot) == -1, "PG another tab closes the Sell view")
    bd = click("tab0")
    # the Offline tile words
    S = dict((str(n), i) for i, n in enumerate(Page.SLOT_NAME))
    bd = click("tab1")
    K.check(str(pg.mTx[S["ROffA"]]) == "Now 25 % speed for 8 h -> next 30 % for 10 h", "PG the map tile: %s" % pg.mTx[S["ROffA"]])
    p.setProperty("farming.offline", "5")
    bd = click("tab1")
    K.check(str(pg.mTx[S["ROffA"]]) == "50 % speed for 24 hours offline", "PG the map tile at 5: %s" % pg.mTx[S["ROffA"]])
    p.setProperty("farming.offline", "0")
    p.setProperty("farming.auto", "0")
    bd = click("tab1")
    K.check(str(pg.mTx[S["ROffA"]]) == "Manual: 25 % speed for 2 h (Automation: 8 h)", "PG the map tile before Automation: %s" % pg.mTx[S["ROffA"]])
    bd = click("tab0")
    K.check(str(pg.cCap) == "Rates below are online. Offline: 25 % speed for 2 hours, then it stops.", "PG the Collect line before Automation: %s" % pg.cCap)
    p.setProperty("farming.auto", "1")
    # FIX2: the long FULL advice only while nothing else shares the sub-line
    cap_ = int(M.capOf(FK, p, 0))
    p.setProperty("farming.i0.stored", str(cap_))
    p.setProperty("farming.i0.last", str(T0))
    p.setProperty("farming.i0.ench", "40")
    bd = click("tab0")
    K.check(" - FULL - +40 Enchanted" in str(pg.cSub[0]) and "collect to restart" not in str(pg.cSub[0]), "FIX2 a full row with bonus finds: short FULL: %s" % pg.cSub[0])
    p.remove("farming.i0.ench")
    bd = click("tab0")
    K.check("FULL - collect to restart it" in str(pg.cSub[0]), "FIX2 a full row alone keeps the advice: %s" % pg.cSub[0])
    p.setProperty("farming.i0.stored", "100")
    # switched off: gone; Combat: none
    Cfg.SELL_ON = False
    bd = click("tab0")
    K.check(not bool(pg.cSell) and "#SkyyShCRow0Sell" not in bd["binds"] and "#SkyyShCRow0Btn" in bd["binds"], "PG sell.enabled off hides the button")
    Cfg.SELL_ON = True
    # a co-op member without Collect sees no buttons
    mu = L["UUID"].fromString(VISITOR)
    pv = Page(mu, W)
    pv.kind = FK
    pv.view = 0
    pv.handleDataEvent(None, None, json.dumps({"a": "tab0"}))
    b2 = T49._build(pv)
    K.check("#SkyyShCRow0Sell" not in b2["binds"], "PG a visitor has no Sell button")
    K.save()


def run_live(out, jar, scratch, home):
    T411.run_live411(out, jar, scratch, home)


SUP49 = ("FIX3 shard view before Automation", "U the centre again")   # the Offline Harvest tile's words: 0.4.19 says speed + hours (PG checks them)


def run_page49(out, jar, scratch, home):
    T49._superseded(SUP49, lambda: T416._h(T416._p(T49.run_page))(out, jar, scratch, home))


EXPECT = {   # 0.4.18 -> 0.4.19, checked by hand 2026-11-08: the version texts (CfgFile / CfgFn / CfgRows, ShStore's and ShFill.markFixed's log lines, the ready line) + the round
    'CfgFile': ['~<clinit>'],
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'ShCfg': ['+f DEF_OFF_PCT', '+f OFF_PCT', '+f SELL_ON', '~<clinit>', '~m loadCfg', '~m writeDefaults'],
    'ShCore': ['+f SELLQ', '+m flushSell', '+m flushSellAt', '+m payCred', '+m priceOf', '+m sell', '+m sell0', '+m legIn', '+m sellBack', '+m sellBackQ', '+m sellItem', '+m sellNo', '+m sellOpenNo', '+m sellQty', '+m sellQtyWhy', '+m xpTotal', '~<clinit>', '~m buyOffline0', '~m collect0'],
    'ShFill': ['~m markFixed'],
    'ShIsl': ['+m offHrs', '+m offPct', '+m offSpd', '+m offWords', '+m onMs'],
    'ShMath': ['+<clinit>', '+f ALL_ON_TEST', '+f ONLINE', '+m allOff', '+m anyIsland', '+m brk', '+m closeOff', '+m inSafe', '+m isOn', '+m logIn', '+m logOut', '+m offStart', '+m outSafe', '+m rebase', '+m spd', '+m sync', '+m winAcc', '~m settle'],
    'ShPage': ['+f cCap', '+f cSell', '+f sPrev', '+f sellSlot', '+f sellTxt', '+f sv', '+f sv3c', '+f svOn', '+m fillSell', '+m jsonStr', '+m svTwo', '~c ', '~c ', '~m act', '~m buildFull', '~m fill', '~m fillMap', '~m handleDataEventIn'],
    'ShStore': ['~m get', '~m migrate', '~m migrate2', '~m save'],
    'ShTick': ['+m syncOn', '~m runIn'],
    'SkyyShardsPlugin': ['~m setup', '~m shutdown']
}


def _compare(out, jar, old_jar, pkg, expect, added, removed=()):
    """every non-class file identical (manifest.json aside); the classes as EXPECT"""
    with zipfile.ZipFile(jar) as a, zipfile.ZipFile(old_jar) as b:
        na = dict((n, a.read(n)) for n in a.namelist() if not n.endswith(".class"))
        nb = dict((n, b.read(n)) for n in b.namelist() if not n.endswith(".class"))
    ch = sorted(n for n in set(na) | set(nb) if na.get(n) != nb.get(n) and n != "manifest.json" and not n.startswith("Common/UI/Custom/Pages/SkyySh"))
    assert not ch, "C non-class files differ: %s" % ch[:8]
    print("C. %d non-class files identical" % len(nb))
    T49._ORIG_COMPARE(out, jar, old_jar, pkg, expect, added, removed)


HK.run_compare = _compare

if __name__ == "__main__":
    HK.run(name="SkyyShards", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=["ShMig0419"],
           phases=[("static", run_static), ("off", run_off), ("mig", run_mig), ("sell", run_sell), ("page", run_page),
                   ("open", T416._h(T416._g(T416.run_open), True)), ("bytecode", T415.run_bytecode),
                   ("flows3", T416._h(T416._g(T413.run_flows3))), ("page49", run_page49),
                   ("live", run_live)],
           script=__file__, live=(T416.T46.LIVE_SH, "mods/Skyy_SkyyShards"))
