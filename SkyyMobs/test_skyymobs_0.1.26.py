"""Harness for SkyyMobs 0.1.26 (round mobcoin1 = MOB KILL COINS: MobCoin, called once per death by SpoilsSys; the bridge mob:fn:killCoins;
MobRoute = tools/skyyroute.py; Server Setup > Mobs > Kill coins; tools/mobs_0_1_26_patch.py).
Build first:
    python tools/mobs_0_1_26_patch.py && python SkyyMobs/build_skyymobs_0.1.26.py
    python SkyyMobs/test_skyymobs_0.1.26.py [--keep] [--expect-dump]

Phases (fresh child JVMs, tools/harness_kit.py):
  S     static   the patch re-runs to identical bytes (--out), line endings kept, TWO new classes (MobCoin, MobRoute), no new system / command;
                 the jar adds only those two classes and changes no role / model / spawn / lang file (only the manifest); the 9 rows + the tab;
                 the coin math line (about half a gathering hour in every zone)
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.1.25 -> 0.1.26 (EXPECT below)
  X     exec     EXECUTES MobCoin: the defaults (fields, file lines), curveOwn = tools/balance_model.py's curve at every level, curve()
                 (SkyyCoins' live coins:fn:curve, bad answers -> the built-in copy), amount() per level x rank x animals (+ the Python
                 mirror at Lv 1..100), the bridge mob:fn:killCoins (good / bad arguments, boss role, clamp), once() / core(): an ordinary kill,
                 a DOUBLE death event (paid once), no player / Creative / pet / no level guards, unlevelled at the zone level, an elite / boss,
                 a busy profile, the hour cap (full, partial, the next hour, a failed payment gives the cap back), no SkyyCoins, the
                 messages (chat / feed / feed refused -> chat / off / the server switch off), partyCfg (SkyySkills' live share, cache,
                 off, junk), shareOne (+ its cap), members(), petOf(), name(), fmt(), the engine glue's null guards; MobCfg.load from a REAL
                 scratch file (edits, clamps, a file without the lines = the defaults, not rewritten); the ready text
                 mobcoin1fix: an unlevelled mob pays only when wild (tamed / bred Tamed_*, babies, FRIENDLY / REVERED / IGNORE,
                 merchants / NPCs / traders = nothing; a boss always pays; unread attitude = the lists decide); a bred pen at Zone 5
                 pays at most the default 5,000,000 hour cap; a corpse ticked past DONE_MS is never paid twice (seen() refresh + the
                 purge); a burst of mixed feed cards is gated (no chat overflow, coins still paid)
  W     wire     bytecode: SpoilsSys.tick gates on MobCoin.on() and calls MobCoin.onDeath ONCE, in its OWN catch, BEFORE the engine's drop
                 gate (Role.hasDroppedDeathItems) and MobSpoils.first; onDeath -> killerRef, creative, levelHere, petOf, once, shareAll;
                 once -> first -> core; setup puts mob:fn:killCoins, shutdown removes it
  EX125 0.1.25's exec + wire (augments) + 0.1.24's exec (set drops) + 0.1.23's exec + CreditSys phases EXECUTED on this jar
  D     live     start twice on a scratch COPY of Skyy's live Skyy_SkyyMobs: bytes untouched, no migration, the 9 new rows read their defaults
  AA    engine-access audit
NOT COVERED (UNVERIFIED in game): SpoilsSys.tick inside the ECS death dispatch with a real DeathComponent (its call is wired + the core
executed here); the real killer / Creative / position reads (killerRef, creative, levelHere, memberHere - null guards only); SkyyCoins'
real purse write (coins:fn:add faked); SkyyHud's real feed card.
Scratch: tools/dev/scratch/mobcoin1/mobs (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, zipfile, importlib.util, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.1.26"
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "mobcoin1", "mobs")]
import skyybuild as B
import harness_kit as HK
import balance_model as BM

_run0 = HK.run
HK.run = lambda *a, **k: None          # import 0.1.25's harness (and through it 0.1.24's ...) for its phases without running it
_s = importlib.util.spec_from_file_location("test_skyymobs_0_1_25", os.path.join(HERE, "test_skyymobs_0.1.25.py"))
T25 = importlib.util.module_from_spec(_s)
_s.loader.exec_module(T25)
HK.run = _run0
T24, T23, T22 = T25.T24, T25.T23, T25.T22

GEN = os.path.join(HERE, "build_skyymobs_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyymobs_0.1.25.py")
PATCH = os.path.join(ROOT, "tools", "mobs_0_1_26_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMobs-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMobs-0.1.25.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.mobs."
KEYS = ["coins.kill.on", "coins.kill.base", "coins.kill.eliteX", "coins.kill.miniX", "coins.kill.bossX", "coins.kill.animals",
        "coins.kill.capHour", "coins.kill.party", "coins.kill.message"]
DEFS = ["true", "25", "3", "10", "20", "50", "5000000", "true", "true"]
CURVE = BM.p7_curve_text()
EXPECT = {}          # filled from --expect-dump below
ADDED = ["MobCoin", "MobRoute"]


def jround(x):
    """java.lang.Math.round"""
    return int(math.floor(x + 0.5))


def py_amount(lv, mult=1.0, share=1.0, base=25.0):
    v = base * BM.p7_curve_from_text(CURVE, min(100, lv)) * mult * share
    return max(1, jround(v)) if v > 0 else 0


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyMobs 0.1.26 - build script') and g.count('VERSION = "0.1.26"') == 1, "S header + VERSION")
    K.eq([g.count(w) - o.count(w) for w in ("registerSystem(", "registerCommand(", "makeClass(")], [0, 0, 2], "S two new classes (MobCoin, MobRoute), no system / command")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    K.eq((sorted(nb - na), sorted(na - nb)), (["com/skyy/mobs/MobCoin.class", "com/skyy/mobs/MobRoute.class"], []), "S the jar adds only MobCoin + MobRoute, removes nothing")
    K.eq(sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n)), ["manifest.json"],
         "S every role / model / spawn / lang file byte-identical to 0.1.25 (only the manifest changes)")
    K.check(all(("(\"%s\", " % k) in g for k in KEYS) and '("coins", "Kill coins")' in g, "S the 9 rows + the Kill coins tab are in the build")
    K.check("import skyyroute as RT" in g and "RT.add_msg_route(mrte" in g, "S MobRoute = tools/skyyroute.py (the shared message route)")
    K.check("COIN_CURVE_TEXT = %r" % CURVE in g, "S the built-in coin curve = tools/balance_model.py p7_curve_text()")
    # the coin math (Skyy's default: about half a gathering hour, P7 G) - the same numbers the build prints
    rows = []
    for z, lv in zip(range(1, 6), (10, 30, 50, 70, 90)):
        a = py_amount(lv)
        ph = BM.KILLS_H * (1.0 + 0.03 * 2.0) * a
        rows.append((z, lv, a, ph / BM.p7_G_mid(z)))
    K.check(all(0.45 <= r[3] <= 0.55 for r in rows), "S kill coins per hour = about half a P7 gathering hour in every zone: %s" % ["Z%d Lv%d %d/kill %.2f G" % r for r in rows])
    K.save()


def run_exec(out, jar, scratch, home):
    from jpype import JClass, JImplements, JOverride, JString, JArray, JObject
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    C, Co, R, Egg = JClass(PKG + "MobCfg"), JClass(PKG + "MobCoin"), JClass(PKG + "MobRoute"), JClass(PKG + "MobEgg")
    UUID, Long, Integer, Boolean, Double = JClass("java.util.UUID"), JClass("java.lang.Long"), JClass("java.lang.Integer"), JClass("java.lang.Boolean"), JClass("java.lang.Double")
    OA = JArray(JClass("java.lang.Object"))
    C.useDefaults()
    d = str(C.DEF_CFG)
    K.check(all(("\n%s=%s\n" % (k, v)) in d for k, v in zip(KEYS, DEFS)), "X the default file carries the 9 new lines")

    def vals():
        return (bool(C.COIN_ON), float(C.COIN_BASE), float(C.COIN_ELITE), float(C.COIN_MINI), float(C.COIN_BOSS), float(C.COIN_ANIMAL),
                int(C.COIN_CAP), bool(C.COIN_PARTY), bool(C.COIN_MSG))
    DEFV = (True, 25.0, 3.0, 10.0, 20.0, 50.0, 5000000, True, True)
    K.eq(vals(), DEFV, "X the field defaults")
    K.check(bool(Co.on()), "X on() at the defaults")
    # ---- the curve
    bad = [(lv, float(Co.curveOwn(lv)), BM.p7_curve_from_text(CURVE, lv)) for lv in range(-2, 103) if abs(float(Co.curveOwn(lv)) - BM.p7_curve_from_text(CURVE, lv)) > 1e-9 * max(1.0, BM.p7_curve_from_text(CURVE, lv))]
    K.check(not bad, "X curveOwn = tools/balance_model.py's coin curve at Lv -2..102 (clamped 1..100): %s" % bad[:3])
    K.eq(float(Co.curve(10)), 1.0, "X curve() without SkyyCoins = the built-in copy (Lv 10 = 1.0)")
    ANS = {"v": None, "n": 0}

    @JImplements("java.util.function.Function")
    class CurveFn(object):
        @JOverride
        def apply(self, o):
            ANS["n"] += 1
            v = ANS["v"]
            if v == "throw":
                raise RuntimeError("boom")
            return v
    br.put("coins:fn:curve", CurveFn())
    ANS["v"] = Double(2.5)
    K.eq(float(Co.curve(10)), 2.5, "X curve() asks SkyyCoins' live coins:fn:curve first")
    got = []
    for v in (Double(0.0), Double(float("nan")), JString("x"), None, Double(-3.0), "throw"):
        ANS["v"] = v
        got.append(float(Co.curve(50)))
    K.check(all(abs(x - BM.p7_curve_from_text(CURVE, 50)) < 1e-9 for x in got), "X a bad / zero / NaN / thrown answer = the built-in copy: %s" % got)
    br.remove("coins:fn:curve")
    # ---- amount: level x rank x animals
    lvs = list(range(1, 101))
    mism = [(lv, int(Co.amount(lv, "", False, True)), py_amount(lv)) for lv in lvs if int(Co.amount(lv, "", False, True)) != py_amount(lv)]
    K.check(not mism, "X amount() = round(25 x curve) at Lv 1..100 (the Python mirror): %s" % mism[:3])
    tab = dict((lv, int(Co.amount(lv, "", False, True))) for lv in (1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100))
    K.eq(tab, dict((lv, py_amount(lv)) for lv in tab), "X per-level coins: %s" % tab)
    K.eq((int(Co.amount(10, "elite", False, True)), int(Co.amount(10, "mini", False, True)), int(Co.amount(10, "boss", False, True)),
          int(Co.amount(10, "", True, True)), int(Co.amount(10, "elite", True, True)), int(Co.amount(10, "", False, False)), int(Co.amount(30, "elite", False, False))),
         (75, 250, 500, 500, 500, 13, py_amount(30, 3.0, 0.5)), "X ranks: elite x3, mini x10, boss x20 (a boss role wins), animals 50 % (12.5 -> 13)")
    K.eq((int(Co.amount(0, "", False, True)), int(Co.amount(-5, "", False, True)), int(Co.amount(500, "", False, True))), (0, 0, py_amount(100)),
         "X no level = 0; above Lv 100 = the Lv 100 coins")
    C.COIN_BASE = 0.01
    K.eq(int(Co.amount(1, "", False, False)), 1, "X at least 1 coin while on")
    C.COIN_BASE = 0.0
    K.check(not bool(Co.on()) and int(Co.amount(50, "", False, True)) == 0, "X base 0 = off")
    C.useDefaults()
    C.COIN_ON = False
    K.check(not bool(Co.on()) and int(Co.amount(50, "", False, True)) == 0, "X coins.kill.on off = 0")
    C.useDefaults()
    # ---- the bridge mob:fn:killCoins
    fn = Co()
    br.put("mob:fn:killCoins", fn)

    def call(*a):
        r = fn.apply(OA(list(a)))
        return None if r is None else int(r)
    K.eq((call("Trork_Warrior", Integer(10)), call("Trork_Warrior", Integer(10), "Elite"), call(None, Integer(30), "mini"), call("Trork_Chieftain", Integer(10)),
          call("Trork_Warrior", Double(10.9)), call("Trork_Warrior", Integer(5000)), call("Trork_Warrior", Integer(0)), call("Trork_Warrior", Double(float("nan")))),
         (25, 75, py_amount(30, 10.0), 500, 25, py_amount(100), 0, 0), "X mob:fn:killCoins: plain / elite (any case) / mini (no role) / a Boss roles role x20 / 10.9 = Lv 10 / clamp / 0 / NaN")
    K.check(fn.apply(JString("x")) is None and fn.apply(OA(["Trork_Warrior"])) is None and fn.apply(OA(["Trork_Warrior", "10"])) is None
            and fn.apply(OA([Integer(3), Integer(10)])) is None and fn.apply(None) is None, "X bad arguments = null")
    C.COIN_ON = False
    K.eq(call("Trork_Warrior", Integer(10)), 0, "X the switch off = 0 from the bridge too")
    C.useDefaults()
    # ---- the fakes: SkyyCoins' purse, SkyyHud's route + feed, the chat
    PAY = []
    PAYMODE = {"m": "ok"}

    @JImplements("java.util.function.Function")
    class AddFn(object):
        @JOverride
        def apply(self, o):
            if PAYMODE["m"] == "null":
                return None
            if PAYMODE["m"] == "throw":
                raise RuntimeError("purse")
            PAY.append((str(o[0]), int(o[1])))
            return Long(1000 + int(o[1]))
    br.put("coins:fn:add", AddFn())
    ROUTE = {}
    FEED = []
    FEEDOK = {"v": True}

    @JImplements("java.util.function.Function")
    class RouteFn(object):
        @JOverride
        def apply(self, o):
            return JString(ROUTE.get(str(o[0]), "chat"))

    @JImplements("java.util.function.Function")
    class FeedFn(object):
        @JOverride
        def apply(self, o):
            FEED.append((str(o[0]), str(o[1]), str(o[3])))
            return Boolean(FEEDOK["v"])
    br.put("msgroute:fn:get", RouteFn())
    br.put("feed:fn:push", FeedFn())
    R.TTL = 0
    CHAT = []

    @JImplements("java.util.function.BiConsumer")
    class Tell(object):
        @JOverride
        def accept(self, u, t):
            CHAT.append((str(u), str(t)))
    Co.TELL_API = Tell()
    now = 1_000_000_000_000
    U = [UUID.randomUUID() for _ in range(12)]
    mob = lambda: UUID.randomUUID()

    def once(ku, role="Trork_Warrior", lvl=10, rw="", at=-1, cr=False, pet=False, m=None, t=now, att="HOSTILE"):
        return int(Co.once(m or mob(), ku, cr, pet, role, att, lvl, rw, at, t))
    del PAY[:]
    m1 = mob()
    a1 = once(U[0], m=m1)
    a2 = once(U[0], m=m1)
    a3 = int(Co.once(m1, U[0], False, False, "Trork_Warrior", "HOSTILE", 10, "", -1, now + 5))
    K.eq((a1, a2, a3, PAY), (25, 0, 0, [(str(U[0]), 25)]), "X an ordinary Lv 10 kill pays 25 once; the DOUBLE death event (same mob, every corpse tick) pays nothing more")
    K.eq(CHAT[-1], (str(U[0]), "[Mobs] +25 coins (Lv 10 Trork Warrior)"), "X ... the chat line (route chat)")
    del PAY[:]
    n0 = (int(Co.NOPLAYER.get()), int(Co.CREATIVE.get()), int(Co.PET.get()), int(Co.NOLEVEL.get()))
    r = (once(None), once(U[1], cr=True), once(U[1], pet=True), once(U[1], lvl=0, at=-1))
    K.eq((r, PAY, (int(Co.NOPLAYER.get()) - n0[0], int(Co.CREATIVE.get()) - n0[1], int(Co.PET.get()) - n0[2], int(Co.NOLEVEL.get()) - n0[3])),
         ((0, 0, 0, 0), [], (1, 1, 1, 1)), "X guards: no player killer (a pet's own kill / the world), Creative, a player's pet / summon, no level and no zone band = nothing")
    del PAY[:]
    r = (once(U[1], role="Cow", lvl=0, at=10), once(U[1], role="Trork_Chieftain", lvl=0, at=10), once(U[1], lvl=10, rw="elite"),
         once(U[1], lvl=30, rw="boss"), once(U[1], role="Skeleton_Fighter_SkyyArmored1", lvl=12))
    K.eq((r, [p[1] for p in PAY]), ((13, 500, 75, py_amount(30, 20.0), py_amount(12)), [13, 500, 75, py_amount(30, 20.0), py_amount(12)]),
         "X an animal at the zone level (50 %), a Boss roles role unlevelled = a full boss, an elite, a boss rank, a tougher version")
    K.check(CHAT[-1][1] == "[Mobs] +%d coins (Lv 12 Skeleton Fighter)" % py_amount(12), "X the tougher version's line names its base mob: %s" % CHAT[-1][1])
    # mobcoin1fix (critic 1 + note 4): unlevelled mobs pay only when wild
    del PAY[:]
    t0 = int(Co.TAME.get())
    wild_cases = [("Cow", "HOSTILE", True), ("Cow", "", True), ("Cow", "NEUTRAL", True), ("Tamed_Cow", "HOSTILE", False), ("Tamed_Sheep_Lamb", "", False),
                  ("Cow_Calf", "HOSTILE", False), ("Chicken_Chick", "", False), ("Goat_Kid", "", False), ("Feran_Cub", "", False), ("Horse_Foal", "", False),
                  ("Kweebec_Seedling", "FRIENDLY", False), ("Kweebec_Elder", "REVERED", False), ("Some_Summon", "IGNORE", False),
                  ("Temple_Klops", "", False), ("Klops_Merchant", "", False), ("Wraith_Trader", "HOSTILE", False), ("Village_NPC", "", False),
                  ("Bear_Grizzly_Mount", "", False), ("Wolf_Pet", "", False), ("Kidnapper", "HOSTILE", True), (None, "HOSTILE", False)]
    got = [(r_, a_, int(Co.once(mob(), U[1], False, False, r_, a_, 0, "", 90, now)) > 0) for r_, a_, _w in wild_cases]
    K.eq([g for g in got], [(r_, a_, w_) for r_, a_, w_ in wild_cases], "X unlevelled: wild animals pay; tamed / bred (Tamed_*), babies, villagers (FRIENDLY / REVERED), summons (IGNORE), temple NPCs, merchants, traders, NPCs, mounts, pets never")
    K.eq(int(Co.TAME.get()) - t0, sum(1 for c in wild_cases if not c[2]), "X ... each counted (TAME)")
    del PAY[:]
    K.eq((once(U[1], role="Trork_Chieftain", lvl=0, at=90, att="FRIENDLY"), once(U[1], role="Tamed_Cow", lvl=12, att="FRIENDLY"), once(U[1], role="Cow_Calf", lvl=0, at=-1)),
         (py_amount(90, 20.0), py_amount(12), 0), "X a boss always pays; a LEVELLED mob pays whatever its role / attitude; an island calf = nothing")
    # the bred-pen loop: even WILD unlevelled mobs at Zone 5 stop at the default hour cap
    C.useDefaults()
    PEN = UUID.randomUUID()
    del PAY[:]
    for i in range(1000):
        Co.once(mob(), PEN, False, False, "Cow", "HOSTILE", 0, "", 90, now + i)
    pen = sum(p[1] for p in PAY if p[0] == str(PEN))
    tam = UUID.randomUUID()
    del PAY[:]
    for i in range(200):
        Co.once(mob(), tam, False, False, "Tamed_Cow", "", 0, "", 90, now + i)
    K.eq((py_amount(90, 1.0, 0.5), pen, len(PAY)), (5825, 5000000, 0),
         "X a pen at Zone 5: a wild cow = 5,825; 1,000 kills stop at the default 5,000,000 / h cap; 200 bred Tamed_Cow kills pay nothing")
    # busy profile
    del PAY[:]
    br.put("profile:busy:" + str(U[2]), Boolean(True))
    b0 = int(Co.BUSY.get())
    K.check(once(U[2]) == 25 and PAY == [] and int(Co.BUSY.get()) == b0 + 1, "X a busy profile (switch in progress) gets nothing (never the wrong purse)")
    br.remove("profile:busy:" + str(U[2]))
    # the hour cap
    C.COIN_CAP = 100
    del PAY[:]
    c0 = int(Co.CAPPED.get())
    for i in range(5):
        once(U[3], t=now + i)
    K.eq(([p[1] for p in PAY], int(Co.CAPPED.get()) - c0), ([25, 25, 25, 25], 1), "X cap 100 / h: four 25s, the fifth kill pays nothing")
    del PAY[:]
    C.COIN_CAP = 110
    once(U[3], t=now + 10)
    once(U[3], t=now + 11)
    K.eq([p[1] for p in PAY], [10], "X cap 110: the next kill pays the 10 left, then nothing")
    del PAY[:]
    once(U[3], t=now + 3600000)
    K.eq([p[1] for p in PAY], [25], "X the next hour starts a new window")
    del PAY[:]
    PAYMODE["m"] = "null"
    f0 = int(Co.FAIL.get())
    h0 = list(Co.HOUR.get(U[3]))
    once(U[3], t=now + 3600001)
    K.check(int(Co.FAIL.get()) == f0 + 1 and list(Co.HOUR.get(U[3])) == h0, "X a failed payment (coins:fn:add answers null) gives the cap back: %s" % list(Co.HOUR.get(U[3])))
    PAYMODE["m"] = "throw"
    once(U[3], t=now + 3600002)
    K.check(int(Co.FAIL.get()) == f0 + 2 and list(Co.HOUR.get(U[3])) == h0, "X ... a thrown one too")
    PAYMODE["m"] = "ok"
    C.useDefaults()
    br.remove("coins:fn:add")
    f1 = int(Co.FAIL.get())
    K.check(once(U[4]) == 25 and int(Co.FAIL.get()) == f1 + 1, "X no SkyyCoins = nothing paid, counted (one WARN)")
    br.put("coins:fn:add", AddFn())
    for i in range(30):
        Co.capTake(UUID.randomUUID(), 1, now)
    Co.prune(now + 10 * 3600000)
    K.check(Co.HOUR.size() == 0, "X prune drops the ended windows")
    # messages
    del CHAT[:]
    del FEED[:]
    ROUTE[str(U[5])] = "feed"
    once(U[5])
    K.eq((FEED, CHAT), ([(str(U[5]), "coins", "+25 coins  Lv 10 Trork Warrior")], []), "X route feed: a Coins feed card, no chat")
    FEEDOK["v"] = False
    del FEED[:]
    once(U[5])
    K.check(len(FEED) == 1 and CHAT == [(str(U[5]), "[Mobs] +25 coins (Lv 10 Trork Warrior)")], "X a feed card SkyyHud refuses becomes the chat line")
    FEEDOK["v"] = True
    # mobcoin1fix (critic B): a burst of mixed kills - one new card text per 400 ms, the same text merges, never a chat overflow
    GU = UUID.randomUUID()
    ROUTE[str(GU)] = "feed"
    del CHAT[:]
    del FEED[:]
    del PAY[:]
    g0 = int(Co.GATED.get())
    once(GU, lvl=10)
    once(GU, lvl=12, role="Skeleton_Fighter")
    once(GU, lvl=30, role="Trork_Brute")
    once(GU, lvl=10)
    K.eq((len(FEED), CHAT, [p[1] for p in PAY], int(Co.GATED.get()) - g0),
         (2, [], [25, py_amount(12), py_amount(30), 25], 2),
         "X a burst of mixed kills: the first card + the same text again pass, the 2 new texts within 400 ms are held back (no chat line), every kill paid")
    del CHAT[:]
    del FEED[:]
    del PAY[:]
    ROUTE[str(U[6])] = "off"
    once(U[6])
    K.check(FEED == [] and CHAT == [] and PAY == [(str(U[6]), 25)], "X the player's Coins switch Off = no line, still paid")
    C.COIN_MSG = False
    del PAY[:]
    once(U[7])
    K.check(CHAT == [] and FEED == [] and PAY == [(str(U[7]), 25)], "X coins.kill.message off = no line for anyone, still paid")
    C.useDefaults()
    del PAY[:]
    C.COIN_ON = False
    K.check(once(U[8]) == 0 and PAY == [], "X off = nothing")
    m9 = mob()
    once(U[8], m=m9)
    C.useDefaults()
    K.check(once(U[8], m=m9) == 25, "X a death seen while off is not marked (no first() spent)")
    # mobcoin1fix (critic 3): a corpse still ticking after DONE_MS is never paid twice; a corpse gone that long is purged
    Sys = JClass("java.lang.System")
    rnow = int(Sys.currentTimeMillis())
    Co.DONE.clear()
    old = rnow - int(Co.DONE_MS) - 60000
    for i in range(600):
        Co.DONE.put(UUID.randomUUID(), Long(old))
    live, gone = mob(), mob()
    Co.DONE.put(live, Long(old))
    Co.DONE.put(gone, Long(old))
    K.check(bool(Co.seen(live, rnow)) and not bool(Co.seen(mob(), rnow)) and not bool(Co.seen(None, rnow)), "X seen(): a known corpse is refreshed (true), a new death / null is not")
    Co.PRUNED = 0
    K.check(bool(Co.first(mob())), "X ... a new death after the purge pays")
    K.eq((bool(Co.DONE.containsKey(live)), bool(Co.DONE.containsKey(gone)), int(Co.DONE.size())), (True, False, 2),
         "X the purge (map > 512) frees only corpses not ticked for DONE_MS; the refreshed corpse stays")
    K.check(not bool(Co.first(live)), "X ... so the 11-minute corpse can never be paid a second time")
    # party
    K.check(Co.partyCfg(now) is None, "X partyCfg: no SkyySkills = no share")
    CF = {"party.combatShare.enabled": "true", "party.combatShare.fraction": "0.5", "party.combatShare.radius": "48"}

    @JImplements("java.util.function.Function")
    class SkCfg(object):
        @JOverride
        def apply(self, o):
            if str(o[0]) != "get":
                return None
            v = CF.get(str(o[1]))
            return None if v is None else JString(v)
    br.put("config:fn:SkyySkills", SkCfg())
    K.check(Co.partyCfg(now) is None, "X ... cached 2 s")
    pc = Co.partyCfg(now + 2500)
    K.eq(list(pc) if pc is not None else None, [0.5, 48.0], "X SkyySkills' live fraction + radius")
    CF["party.combatShare.fraction"] = "0.25"
    K.eq(list(Co.partyCfg(now + 3000)), [0.5, 48.0], "X ... cached")
    K.eq(list(Co.partyCfg(now + 5000)), [0.25, 48.0], "X ... re-read after 2 s")
    for k, v in (("party.combatShare.enabled", "false"), ("party.combatShare.fraction", "abc"), ("party.combatShare.fraction", "0"), ("party.combatShare.radius", "-1")):
        old = CF[k]
        CF[k] = v
        Co.PCFG_AT = 0
        K.check(Co.partyCfg(now + 9000) is None, "X partyCfg %s=%s = no share" % (k, v))
        CF[k] = old
    del PAY[:]
    del CHAT[:]
    g1 = int(Co.shareOne(U[9], "Skyy", 25, 0.5, now))
    g2 = int(Co.shareOne(U[9], None, 25, 0.0, now))
    g3 = int(Co.shareOne(U[9], None, 1, 0.25, now))
    K.eq((g1, g2, g3, PAY, CHAT), (13, 0, 0, [(str(U[9]), 13)], [(str(U[9]), "[Mobs] +13 coins (party kill by Skyy)")]),
         "X shareOne: 25 x 0.5 = 13 into the member's purse + their line; fraction 0 / a share under 0.5 coin = nothing")
    C.COIN_CAP = 5
    del PAY[:]
    K.eq((int(Co.shareOne(U[10], None, 25, 0.5, now)), PAY), (5, [(str(U[10]), 5)]), "X a member's share counts against THEIR hour cap")
    C.useDefaults()

    @JImplements("java.util.function.Function")
    class Members(object):
        @JOverride
        def apply(self, o):
            return OA([JString(str(U[0])), JString(str(U[9]))])
    K.check(Co.members(U[0]) is None, "X members(): no SkyyParty = null")
    br.put("party:fn:members", Members())
    K.eq([str(x) for x in Co.members(U[0])], [str(U[0]), str(U[9])], "X members(): SkyyParty's list")
    PETM = UUID.randomUUID()

    @JImplements("java.util.function.Function")
    class Pets(object):
        @JOverride
        def apply(self, o):
            return U[0] if str(o) == str(PETM) else None
    K.check(not bool(Co.petOf(PETM)), "X petOf: no SkyyPets = not a pet")
    br.put("pets:fn:ownerOf", Pets())
    K.check(bool(Co.petOf(PETM)) and not bool(Co.petOf(mob())) and not bool(Co.petOf(None)), "X petOf: SkyyPets' owner answer")
    K.eq((str(Co.name("Skeleton_Fighter_SkyyVeteran3")), str(Co.name(None)), str(Co.fmt(1234567))), ("Skeleton Fighter", "mob", "1,234,567"), "X name / fmt")
    # the engine glue's guards (the ECS objects themselves are UNVERIFIED here)
    K.eq((int(Co.onDeath(None, None, None, 0, None, mob())), Co.killerRef(None, None), Co.killerRef(JString("x"), None), bool(Co.creative(None, None)),
          Co.pos(None, None), int(Co.shareAll(None, None, U[0], None, 25, now)), int(Co.levelHere(None, None, 0)), Co.memberHere(None, None, None, U[0], 1.0)),
         (0, None, None, False, None, 0, -1, None), "X the engine glue's null guards")
    # MobCfg.load from a real scratch file
    P_ = JClass("java.nio.file.Paths")
    sd = os.path.join(scratch, "cfg")
    os.makedirs(sd, exist_ok=True)
    fp = os.path.join(sd, "config.properties")
    base = (d.replace("\ncoins.kill.base=25\n", "\ncoins.kill.base=40\n").replace("\ncoins.kill.eliteX=3\n", "\ncoins.kill.eliteX=5000\n")
            .replace("\ncoins.kill.animals=50\n", "\ncoins.kill.animals=150\n").replace("\ncoins.kill.capHour=5000000\n", "\ncoins.kill.capHour=-5\n")
            .replace("\ncoins.kill.party=true\n", "\ncoins.kill.party=false\n").replace("\ncoins.kill.on=true\n", "\ncoins.kill.on=false\n"))
    open(fp, "w", encoding="latin-1", newline="").write(base)
    C.DIR = P_.get(sd)
    C.FILE = P_.get(fp)
    C.BANDS = P_.get(os.path.join(sd, "bands.properties"))
    C.load()
    K.eq(vals(), (False, 40.0, 1000.0, 10.0, 20.0, 100.0, 0, False, True), "X MobCfg.load reads the file: off, 40, eliteX 5000 -> 1000, animals 150 -> 100, cap -5 -> 0, party off")
    strip = "\n".join(l for l in d.split("\n") if not l.startswith("coins.kill."))
    open(fp, "w", encoding="latin-1", newline="").write(strip)
    b0 = open(fp, "rb").read()
    C.load()
    K.eq(vals(), DEFV, "X a file without the 9 lines = the defaults (no migration)")
    K.check(open(fp, "rb").read() == b0, "X ... and the file is not rewritten")
    t = str(Egg.text())
    K.check("; augment drops on (" in t and "; kill coins on (25.0 at Lv 10 x the coin curve (built-in); elite x3.0, mini x10.0, boss x20.0; animals 50.0 %; cap 5,000,000 / h; party share on; mob:fn:killCoins; paid " in t
            and t.index("augment drops") < t.index("kill coins"), "X the ready text names the kill coins after the augment drops: %s" % t[-330:])
    K.check(" kills, party " in t and "none: no player " in t and ", tame / baby / NPC " in t and ", cards held " in t, "X ... with the counters")
    K.check("chat " in str(R.stats()), "X MobRoute.stats")
    K.save()


def _ldcs(cp, m):
    out = []
    ci = m.getMethodInfo().getCodeAttribute().iterator()
    cpl = m.getMethodInfo().getConstPool()
    while ci.hasNext():
        pos = ci.next()
        op = ci.byteAt(pos)
        if op in (0x12, 0x13):
            idx = ci.byteAt(pos + 1) if op == 0x12 else ci.u16bitAt(pos + 1)
            try:
                if cpl.getTag(idx) == 8:
                    out.append(str(cpl.getStringInfo(idx)))
            except Exception:
                pass
    return out


def _calls(m, ops=(0xb8,)):
    seq = []
    ci = m.getMethodInfo().getCodeAttribute().iterator()
    cpl = m.getMethodInfo().getConstPool()
    while ci.hasNext():
        pos = ci.next()
        if ci.byteAt(pos) in ops:
            seq.append((pos, str(cpl.getMethodrefClassName(ci.u16bitAt(pos + 1))).rsplit(".", 1)[1] + "." + str(cpl.getMethodrefName(ci.u16bitAt(pos + 1)))))
    return seq


def run_wire(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.JAVASSIST], verify=False)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(jar)
    m = [x for x in cp.get(PKG + "SpoilsSys").getDeclaredMethods() if str(x.getName()) == "tick" and len(x.getParameterTypes()) == 5][0]
    seq = _calls(m, (0xb8, 0xb6))
    names = [n for _p, n in seq]
    pos = {}
    for p_, n in seq:
        pos.setdefault(n, p_)
    K.check(names.count("MobCoin.on") == 2 and names.count("MobCoin.onDeath") == 1, "W SpoilsSys.tick: MobCoin.on in the gate + before the call, onDeath ONCE: %s" % [n for n in names if "MobCoin" in n])
    K.check(pos["MobCoin.onDeath"] < pos["Role.hasDroppedDeathItems"] < pos["MobSpoils.first"], "W the kill coins come BEFORE the engine's drop gate and the Spoils' once-per-death check")
    et = m.getMethodInfo().getCodeAttribute().getExceptionTable()
    cov = lambda q: [(int(et.startPc(i)), int(et.endPc(i)), int(et.handlerPc(i))) for i in range(et.size()) if et.startPc(i) <= q < et.endPc(i)]
    cc, ch = cov(pos["MobCoin.onDeath"]), cov(pos["Role.hasDroppedDeathItems"])
    K.check(len(cc) == len(ch) + 1, "W MobCoin.onDeath sits in its OWN catch (a throw never skips the Spoils / augments / eggs): coins %s, drop gate %s" % (cc, ch))
    od = [x for x in cp.get(PKG + "MobCoin").getDeclaredMethods() if str(x.getName()) == "onDeath"][0]
    on = [n for _p, n in _calls(od)]
    OD = ["MobCoin.on", "MobCoin.seen", "MobCoin.killerRef", "MobCoin.creative", "MobCoin.levelHere", "MobCoin.attOf", "MobCoin.petOf", "MobCoin.once", "MobCoin.shareAll"]
    K.check([n for n in on if n in OD] == OD,
            "W onDeath: on -> seen (a corpse ticked again: refresh + stop) -> killer -> Creative -> zone level -> attitude -> pet -> once -> party share: %s" % on)
    tl = [n for _p, n in _calls([x for x in cp.get(PKG + "MobCoin").getDeclaredMethods() if str(x.getName()) == "tell"][0])]
    K.check(tl.index("MobRoute.gate") < tl.index("MobRoute.feed"), "W tell(): RT.gate before every feed card: %s" % tl)
    cr_ = [n for _p, n in _calls([x for x in cp.get(PKG + "MobCoin").getDeclaredMethods() if str(x.getName()) == "core"][0])]
    K.check(cr_.index("MobCoin.wild") < cr_.index("MobCoin.amount") < cr_.index("MobCoin.give"), "W core(): wild() before amount() + give(): %s" % cr_)
    oc = [n for _p, n in _calls([x for x in cp.get(PKG + "MobCoin").getDeclaredMethods() if str(x.getName()) == "once"][0])]
    K.check(oc.index("MobCoin.first") < oc.index("MobCoin.core"), "W once(): first() (once per death) before core(): %s" % oc)
    pl = cp.get(PKG + "SkyyMobsPlugin")
    st = [x for x in pl.getDeclaredMethods() if str(x.getName()) == "setup"][0]
    sd = [x for x in pl.getDeclaredMethods() if str(x.getName()) == "shutdown"][0]
    K.check("mob:fn:killCoins" in _ldcs(cp, st) and "mob:fn:killCoins" in _ldcs(cp, sd), "W setup puts mob:fn:killCoins, shutdown removes it")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Cfg, Sp, Sc, Co = JClass(PKG + "MobCfg"), JClass(PKG + "MobSpoils"), JClass(PKG + "MobSecret"), JClass(PKG + "MobCoin")
    P_ = JClass("java.nio.file.Paths")
    files = [f for f in ("config.properties", "bands.properties", "trees.properties") if os.path.isfile(os.path.join(home, f))]
    before = dict((f, open(os.path.join(home, f), "rb").read()) for f in files)
    cf = before.get("config.properties", b"")
    K.check("config.properties" in files and b"coins.kill." not in cf, "D the live copy has a config.properties without coins.kill. lines (the new defaults apply)")

    def start():
        Cfg.DIR = P_.get(home)
        Cfg.FILE = P_.get(os.path.join(home, "config.properties"))
        Cfg.BANDS = P_.get(os.path.join(home, "bands.properties"))
        o = "".join(str(JClass(PKG + m).run(P_.get(home))) for m in ("MobMig", "MobMig14", "MobMig11", "MobMig12", "MobMigP4"))
        o += str(Sp.migrateWc15(P_.get(home)))
        Cfg.load()
        Sp.loadV3(P_.get(home))
        Sc.load(P_.get(home))
        return o

    def vals():
        return (bool(Cfg.COIN_ON), float(Cfg.COIN_BASE), float(Cfg.COIN_BOSS), int(Cfg.COIN_CAP), bool(Co.on()), int(Co.amount(10, "", False, True)), bool(Cfg.AUG_ON))
    DEF = (True, 25.0, 20.0, 5000000, True, 25, True)
    o1 = start()
    K.eq(vals(), DEF, "D start 1: the live file -> the kill coin defaults (25 at Lv 10, boss x20, cap 5,000,000 / h); augments still on")
    K.eq(dict((f, open(os.path.join(home, f), "rb").read() == before[f]) for f in files), dict((f, True) for f in files),
         "D start 1: config / bands / trees bytes untouched (no migration; older updates said %r)" % o1[:60])
    o2 = start()
    K.eq((o2, vals()), ("", DEF), "D start 2: nothing migrates, the same values")
    K.eq(dict((f, open(os.path.join(home, f), "rb").read() == before[f]) for f in files), dict((f, True) for f in files), "D start 2: bytes still untouched")
    K.save()


EXPECT = {
    "MobCfg": ["+f COIN_ANIMAL", "+f COIN_BASE", "+f COIN_BOSS", "+f COIN_CAP", "+f COIN_ELITE", "+f COIN_MINI", "+f COIN_MSG", "+f COIN_ON", "+f COIN_PARTY",
               "~<clinit>", "~m apply", "~m load", "~m reloadAll", "~m useDefaults"],
    "MobEgg": ["~m text"],
    "SpoilsSys": ["~m tick"],
    "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "CfgFile": ["~<clinit>"],
    "SkyyMobsPlugin": ["~m setup", "~m shutdown"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
HK.run_compare = T22._cmp
if __name__ == "__main__":
    HK.run("SkyyMobs", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("static", run_static), ("exec", run_exec), ("wire", run_wire), ("ex125", T25.run_exec), ("wi125", T25.run_wire), ("ex124", T24.run_exec),
            ("ex123", T23.run_exec), ("cs123", T23.run_cs), ("live", run_live)], __file__, live=(T22.LIVE_DIR, "Skyy_SkyyMobs"))
