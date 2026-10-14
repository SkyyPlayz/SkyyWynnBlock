"""SkyyRebirth 0.1 - harness (a NEW mod: no class compare; tools/harness_kit.py's verify + engine-access audit + our own phases).
Build first: python SkyyRebirth/build_skyyrebirth_0.1.py   (and SkyySkills 0.4.35: the cross-mod checks load both jars)

    python SkyyRebirth/test_skyyrebirth_0.1.py --dir <empty folder inside tools/dev/scratch/> [--keep]

Phases (each a fresh child JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch):
  A   verify   every class loads + initialises with -Xverify:all
  X   exec     EVERY CODE PATH: the config loader (first start writes the default file; clamps; bad values = defaults), the config kit
               (config:def:SkyyRebirth rows / defaults, cmdSetConsole -> the bound field + the file line); RbStore (validKey, a missing file
               = 0, read / cache, an unreadable file = 0 + never overwritten, save = atomic + cached, the SkyyRebirth-IO thread: first ask
               answers 0 and queues the read, the next ask has it); every RbFn mode (count / cap / node / dustmult / busy / decision, UUID
               via profile:fn:key, pkey, bad arguments never throw); RbMath (cap kinds, Dust, the spec 3.5 points curve, roman);
               RbCheck (every requirement met / not met: switched off, class below max, rebirths used up, in combat, elsewhere / own
               island / hub; gains per arm, Fishing without a skill); RbPub.tick (publish, a profile switch republishes, a leaver's key
               removed); /rebirth gate (off + player = refused, off + admin = page, on = page) + its permission group; RbPage.build in
               every state (the left panel texts, the Nexus tooltip, the Close binding) - and THE PROBE: the built page as a real
               CustomPage packet (computeSize vs CustomPage.MAX_SIZE); static: setup publishes the six functions, starts the IO thread and
               the 5 s tick, shutdown stops them; FIX ROUND: cap / node / dustmult = null while the profile's file is queued on the
               IO thread, then the real answer; the max state (no gain lines, no "Rebirth 11 of 10"); THE FIT: every left-panel text
               at the widest numbers (max 100, +100 levels, class 1000 / 1000, combat 9999 s) is one line (Extra two) of its row
  K   skills   CROSS-MOD with the real SkyySkills 0.4.35 jar: its SkillCap reads our rebirth:fn:cap (a profile file with n = 3 -> Mining /
               class caps +30, Exploration unchanged), its skill:fn:run feeds RbCheck / RbPage (class level vs cap)
  D   live     START TWICE on a scratch COPY of the live world's Skyy_SkyySkills (the profile keys) + no Skyy_SkyyRebirth yet: start 1
               writes only Skyy_SkyyRebirth/config.properties (+ the kit's own files there), start 2 changes nothing, the copied
               Skyy_SkyySkills is byte-identical, every live profile counts 0 rebirths
  AA  engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, shutil, subprocess, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW

VERSION = "0.1"
PKG = "com.skyy.rebirth."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyRebirth-%s.jar" % VERSION)))
SKILLS_JAR = os.path.join(ROOT, "SkyySkills", "SkyySkills-0.4.35.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "rebirth12", "rb")))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyySkills")


def path(p):
    from jpype import JClass
    return JClass("java.nio.file.Paths").get(p, JClass("java.lang.reflect.Array").newInstance(JClass("java.lang.String").class_, 0))


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


def snap(d):
    return dict((os.path.relpath(os.path.join(r, fn), d).replace(os.sep, "/"), hashlib.sha1(open(os.path.join(r, fn), "rb").read()).hexdigest())
                for r, ds, fs in os.walk(d) for fn in fs)


# ====================================================================================================== X: every code path
def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JArray
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    P = lambda n: JClass(PKG + n)
    Cfg, Sto, Fnc, Mth, Chk, Pub, Page, Cmd, Rows, CPub, CFn = (P("RbCfg"), P("RbStore"), P("RbFn"), P("RbMath"), P("RbCheck"), P("RbPub"),
                                                               P("RbPage"), P("RbCmd"), P("CfgRows"), P("CfgPub"), P("CfgFn"))
    UUID, Integer, Long, Bool, Obj = (JClass("java.util.UUID"), JClass("java.lang.Integer"), JClass("java.lang.Long"), JClass("java.lang.Boolean"),
                                      JClass("java.lang.Object"))
    OA = lambda *xs: JArray(Obj)(list(xs))
    Fn = fn_class()
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyRebirth")
    mods = os.path.join(scratch, "x", "mods")
    home = os.path.join(mods, "Skyy_SkyyRebirth")
    Cfg.DIR = path(home)
    Cfg.FILE = path(os.path.join(home, "config.properties"))
    bridge = Cfg.bridge()
    K.check(JClass("java.lang.System").identityHashCode(bridge) == JClass("java.lang.System").identityHashCode(Cfg.BRIDGE),
            "X bridge: cached in RbCfg.BRIDGE")

    # ---- config loader
    r = str(Cfg.loadCfg(True))
    txt = open(os.path.join(home, "config.properties"), encoding="utf8").read()
    K.check(r.startswith("default config.properties written") and txt == str(Cfg.DEFAULT_TEXT), "X loadCfg(first): the default file written: %s" % r)
    K.check((bool(Cfg.ON), int(Cfg.MAX), int(Cfg.LEVELS), int(Cfg.RANKS), float(Cfg.DUST_FIRST), float(Cfg.DUST_NODE)) == (False, 10, 10, 1, 2.0, 0.25),
            "X defaults: off, max 10, +10 levels, +1 rank, Dust x2, +0.25 per node")
    K.check(str(Cfg.loadCfg(True)).startswith("rebirth OFF"), "X loadCfg again: the existing file is never rewritten")
    open(os.path.join(home, "config.properties"), "w", encoding="utf8").write(
        "rebirth.on=yes\nrebirth.max=500\ncaps.levels=-3\ncaps.ranks=x\ndust.first=0.5\ndust.perNode=9\n")
    Cfg.loadCfg(False)
    K.check((bool(Cfg.ON), int(Cfg.MAX), int(Cfg.LEVELS), int(Cfg.RANKS), float(Cfg.DUST_FIRST), float(Cfg.DUST_NODE)) == (True, 100, 0, 1, 1.0, 5.0),
            "X hand-edited values: clamped to the row bounds, a bad number = the default")
    open(os.path.join(home, "config.properties"), "w", encoding="utf8").write(str(Cfg.DEFAULT_TEXT))
    Cfg.loadCfg(False)
    # ---- the config kit
    CPub.start(path(mods), Cfg.LOG)
    hdr = bridge.get("config:def:SkyyRebirth")
    rows = dict((str(rw[0]), [str(x) for x in rw]) for rw in hdr[7])
    K.check(hdr is not None and str(hdr[1]) == "SkyyRebirth" and str(hdr[3]) == VERSION and sorted(rows) == sorted(
        ["rebirth.on", "rebirth.max", "caps.levels", "caps.ranks", "dust.first", "dust.perNode"]), "X config:def:SkyyRebirth: the 6 rows")
    K.check(rows["rebirth.on"][4] == "false" and "danger" in rows["rebirth.on"][9] and rows["rebirth.max"][4] == "10", "X rebirth.on defaults to false (danger: confirms)")
    msg = str(CFn.cmdSetConsole("caps.levels", "12"))
    CPub.flush()
    K.check(int(Cfg.LEVELS) == 12 and "caps.levels=12" in open(os.path.join(home, "config.properties"), encoding="utf8").read(),
            "X kit set (console): the bound field + the file line: %s" % msg)
    CFn.cmdSetConsole("caps.levels", "10")
    CPub.flush()
    K.eq(str(CFn.cmdGet("rebirth.on")), "false", "X kit get rebirth.on")

    # ---- RbStore
    pd = os.path.join(home, "players")
    Sto.DIR = path(pd)
    u1 = UUID.fromString("00000000-0000-4000-8000-0000000000a1")
    k1 = str(u1)
    for k_, want in ((k1, True), (k1 + "-p2", True), (k1 + "-p9999", True), ("../" + k1, False), ("abc", False), (k1 + "-px", False),
                     (k1 + "-p12345", False), (None, False)):
        K.check(bool(Sto.validKey(k_)) == want, "X validKey %r = %s" % (k_, want))
    K.eq(int(Sto.n(k1)), 0, "X a profile without a file = 0 rebirths")
    K.check(not os.path.exists(pd), "X reading never creates the players folder")
    os.makedirs(pd)
    k2 = k1 + "-p2"
    open(os.path.join(pd, k2 + ".properties"), "w", encoding="latin-1").write("n=3\nnode.Mining.dust=2\npts.Mining=7\n")
    K.check(int(Sto.n(k2)) == 3 and int(Sto.node(k2, "Mining.dust")) == 2 and int(Sto.pts(k2, "Mining")) == 7, "X read: n / node / pts")
    open(os.path.join(pd, k2 + ".properties"), "w", encoding="latin-1").write("n=9\n")
    K.eq(int(Sto.n(k2)), 3, "X cached: a hand edit is not re-read while cached")
    open(os.path.join(pd, k2 + ".properties"), "w", encoding="latin-1").write("n=3\nnode.Mining.dust=2\npts.Mining=7\n")
    k3 = k1[:-2] + "b3"
    open(os.path.join(pd, k3 + ".properties"), "w", encoding="latin-1").write("n=-4\nnode.x=abc\npts.Mining=99999\n")
    K.check(int(Sto.n(k3)) == 0 and int(Sto.node(k3, "x")) == 0 and int(Sto.pts(k3, "Mining")) == 1000, "X odd numbers: negative 0, text 0, capped 1000")
    kb = k1[:-2] + "bb"
    os.makedirs(os.path.join(pd, kb + ".properties"))          # a folder where the file should be = unreadable
    K.check(int(Sto.n(kb)) == 0 and Sto.BAD.containsKey(kb), "X an unreadable file counts 0 rebirths and is marked")
    Props = JClass("java.util.Properties")
    pp = Props()
    pp.setProperty("n", "5")
    K.check(Sto.save(kb, pp) is not None and os.path.isdir(os.path.join(pd, kb + ".properties")), "X an unreadable file is never overwritten")
    ks = k1[:-2] + "c5"
    K.check(Sto.save(ks, pp) is None and int(Sto.n(ks)) == 5, "X save: written + cached")
    back = Props()
    back.load(JClass("java.io.FileInputStream")(os.path.join(pd, ks + ".properties")))
    K.check(str(back.getProperty("n")) == "5" and not os.path.exists(os.path.join(pd, ks + ".properties.tmp")), "X save: atomic (no tmp left), read back")
    K.check(Sto.save("../evil", pp) is not None and Sto.save(ks, None) is not None, "X save refuses a bad key / no data")
    # the IO thread
    Sto.start()
    ka = k1[:-2] + "d7"
    open(os.path.join(pd, ka + ".properties"), "w", encoding="latin-1").write("n=2\n")
    first = int(Sto.n(ka))
    ok = PW.wait_until(lambda: Sto.CACHE.containsKey(ka))
    K.check(first == 0 and ok and int(Sto.n(ka)) == 2 and str(Sto.LAST_THREAD) == "SkyyRebirth-IO",
            "X async: the first ask answers 0 and queues the read on SkyyRebirth-IO (%s), the next ask has n = 2" % str(Sto.LAST_THREAD))
    # fix round (critic: a 'no raise' answer while the file loads was cached 5 s by SkyySkills): cap / node / dustmult = null until read
    kz = k1[:-2] + "e9"
    open(os.path.join(pd, kz + ".properties"), "w", encoding="latin-1").write("n=4\nnode.Mining.dust=1\n")
    from jpype import JImplements, JOverride

    @JImplements("java.lang.Runnable")
    class Hold(object):
        @JOverride
        def run(self):
            JClass("java.lang.Thread").sleep(400)
    Sto.IO.execute(Hold())   # hold the IO thread: the read stays queued for a moment
    capf, nodef, dustf, cntf = Fnc(1), Fnc(2), Fnc(3), Fnc(0)
    uz = UUID.fromString(kz)
    bridge.put("rebirth:n:" + kz, Integer(7))          # fix 2: a stale value from the previous profile of this player
    Pub.PKEY.put(uz, kz[:-2] + "ff")
    Pub.publish(uz)
    early = (capf.apply(OA(kz, "Mining", Integer(100))), nodef.apply(OA(kz, "Mining.dust")), dustf.apply(OA(kz, "Mining")), cntf.apply(kz))
    K.check(early == (None, None, None, None) and not Sto.CACHE.containsKey(kz) and Sto.LOADING.containsKey(kz),
            "X loading: cap / node / dustmult / count answer null while the profile's file is queued (not a cached 'no raise', not a false 0): %s" % (early,))
    K.check(bridge.get("rebirth:n:" + kz) is None and not Pub.PKEY.containsKey(uz),
            "X loading (fix 2): rebirth:n:<uuid> is removed while a newly active profile's file is read (never 0, never the old profile's 7)")
    ok = PW.wait_until(lambda: Sto.CACHE.containsKey(kz))
    K.check(ok and int(capf.apply(OA(kz, "Mining", Integer(100)))) == 140 and int(nodef.apply(OA(kz, "Mining.dust"))) == 1
            and int(cntf.apply(kz)) == 4, "X loaded: the next ask answers (cap 140 at n = 4, node 1, count 4)")
    Pub.publish(uz)
    K.check(int(bridge.get("rebirth:n:" + kz)) == 4 and str(Pub.PKEY.get(uz)) == kz, "X loaded: the next publish puts rebirth:n:<uuid> = 4")
    Sto.CACHE.remove(kz)
    Sto.IO.execute(Hold())
    Pub.publish(uz)
    K.check(int(bridge.get("rebirth:n:" + kz)) == 4, "X a re-read of the SAME profile keeps the published value (no flicker)")
    PW.wait_until(lambda: Sto.CACHE.containsKey(kz))
    Pub.PUB.remove(uz)
    Pub.PKEY.remove(uz)
    bridge.remove("rebirth:n:" + kz)
    bridge.remove("rebirth:busy:" + kz)
    K.check(bool(Sto.ready(kz)) and bool(Sto.ready("../x")), "X ready: a read file / a bad key (nothing to read) = ready")
    Sto.stop()
    K.check(Sto.IO is None, "X stop: the IO thread is gone")

    # ---- RbFn: every mode
    F = [Fnc(i) for i in range(6)]
    bridge.put("profile:fn:key", Fn(lambda o: (str(o) + "-p2") if str(o) == k1 else None))
    K.eq(int(F[0].apply(u1)), 3, "X count(UUID): the ACTIVE profile via profile:fn:key")
    K.eq(int(F[0].apply(k2)), 3, "X count(pkey)")
    K.eq(int(F[0].apply(OA(k2))), 3, "X count(Object[] {pkey})")
    for bad_ in (None, Integer(5), "nope", "../x", OA(), OA(None)):
        K.check(F[0].apply(bad_) is None, "X count(%r) = null" % (bad_,))
    K.eq(int(F[1].apply(OA(k2, "Mining", Integer(100)))), 130, "X cap: Mining +10 x 3")
    K.eq(int(F[1].apply(OA(u1, "Combat.Archer", Integer(100)))), 130, "X cap: a class skill (UUID)")
    K.eq(int(F[1].apply(OA(k2, "Exploration", Integer(100)))), 100, "X cap: Exploration never rises")
    K.eq(int(F[1].apply(OA(k2, "collection", Integer(5)))), 8, "X cap: a collection rank +1 x 3")
    K.eq(int(F[1].apply(OA(k1, "Mining", Integer(100)))), 100, "X cap: 0 rebirths = the base")
    K.check(F[1].apply(OA(k2, "Mining")) is None and F[1].apply(OA(k2, "Mining", "100")) is None, "X cap: no / bad base = null")
    Cfg.LEVELS = 7
    K.eq(int(F[1].apply(OA(k2, "Mining", Integer(100)))), 121, "X cap follows the caps.levels setting live")
    Cfg.LEVELS = 10
    Cfg.MAX = 2
    K.eq(int(F[1].apply(OA(k2, "Mining", Integer(100)))), 120, "X cap (fix 2): n = 3 past rebirth.max 2 counts as 2 (+20, not +30)")
    K.eq(int(F[0].apply(k2)), 3, "X count still reports the saved n (3)")
    Cfg.MAX = 10
    K.eq(int(F[1].apply(OA(k2, "Mining", Integer(2000000000)))), 2000000000, "X cap: no overflow")
    K.eq(int(F[2].apply(OA(k2, "Mining.dust"))), 2, "X node")
    K.eq(int(F[2].apply(OA(k2, "nothing"))), 0, "X node not bought = 0")
    K.eq(float(F[3].apply(OA(k1, "Mining"))), 1.0, "X dustmult: 0 rebirths = 1")
    K.eq(float(F[3].apply(OA(k2, "Mining"))), 3.0, "X dustmult: rebirth 3, Mining Dust node 2 = 2 x 1.5")
    K.eq(float(F[3].apply(OA(k2, "Acrobatics"))), 2.0, "X dustmult: Acrobatics (no arm) = the first-rebirth 2x only")
    K.eq(float(F[3].apply(OA(k2, "Exploration"))), 2.0, "X dustmult: Exploration = 2x (all Dust, Q4)")
    K.check(F[4].apply(k2) == Bool.FALSE or bool(F[4].apply(k2)) is False, "X busy: false (0.1 never runs a rebirth)")
    Sto.BUSY.put(k2, Bool.TRUE)
    K.check(bool(F[4].apply(u1)) is True, "X busy: true while a transaction holds the profile")
    Sto.BUSY.clear()
    K.eq(str(F[5].apply("tx-1")), "unknown", "X decision: unknown (no journal in 0.1)")
    K.check(F[1].apply(Integer(3)) is None and F[2].apply(OA(k2, Integer(1))) is None and F[3].apply(OA(k2)) is None, "X odd arguments never throw")

    # ---- RbMath
    K.check([int(Mth.points(x, 100, 8)) for x in (0, 24, 25, 100, 400, 900, 1600, 10000)] == [0, 0, 4, 8, 16, 24, 32, 32]
            and int(Mth.points(100, 100, 12)) == 12 and int(Mth.points(5, 0, 8)) == 0,
            "X points: under 25 % = 0, r 1 = B, 4x = 2B, 16x cap = 4B (spec 3.5)")
    K.check([str(Mth.roman(i)) for i in (1, 4, 10, 11)] == ["I", "IV", "X", "11"], "X roman")
    K.check(Mth.dustArm("mining") == "Mining" and Mth.dustArm("Class") is None and Mth.dustArm("Acrobatics") is None, "X dustArm")

    # ---- RbCheck (stand-in SkyySkills / SkyyIslands answers)
    S = {"cls": (100, 100), "ms": 0, "role": "owner", "runs": {}}

    def f_run(o):
        sk = str(o[1])
        if sk == "class":
            if S["cls"] is None:
                return None
            return OA(Integer(S["cls"][0]), Integer(S["cls"][1]), Long(1000), Long(1000), Bool.TRUE, "Combat.Archer")
        v = S["runs"].get(sk)
        if v is None:
            return None
        return OA(Integer(1), Integer(100), Long(v[0]), Long(v[1]), Bool.TRUE, sk)
    bridge.put("skill:fn:run", Fn(f_run))
    bridge.put("skill:fn:combat", Fn(lambda o: Long(S["ms"])))
    bridge.put("island:role:fn", Fn(lambda o: S["role"]))
    Cfg.HUB_TEST = "default"
    Cfg.ON = True

    def reqs(world="island-x", n=0):
        rr = Chk.reqs(u1, world, n)
        return [str(t) for t in rr[0]], [str(c) for c in rr[1]], bool(rr[2])
    t, c, allm = reqs()
    K.check(allm and all(x.startswith("OK") for x in t[:5]) and t[5].startswith("--") and t[1].endswith("100 / 100"),
            "X reqs: every requirement met (%s)" % t)
    Cfg.ON = False
    t, c, allm = reqs()
    K.check(not allm and t[0].startswith("NO") and c[0] == "#ff6b6b", "X reqs: switched off = NO")
    Cfg.ON = True
    S["cls"] = (37, 100)
    t, c, allm = reqs()
    K.check(not allm and t[1] == "NO  Class level 37 / 100", "X reqs: class below max = NO: %s" % t[1])
    S["cls"] = None
    t, c, allm = reqs()
    K.check(not allm and t[1] == "NO  Choose a class first", "X reqs: no class = NO (choose a class)")
    S["cls"] = (100, 100)
    t, c, allm = reqs(n=10)
    K.check(not allm and t[2] == "NO  Rebirths done 10 / 10", "X reqs: rebirths used up = NO")
    S["ms"] = 2500
    t, c, allm = reqs()
    K.check(not allm and t[3] == "NO  In combat - wait 3 s", "X reqs: in combat = NO: %s" % t[3])
    S["ms"] = 0
    S["role"] = "visitor"
    t, c, allm = reqs()
    K.check(not allm and t[4] == "NO  Go to your island or hub", "X reqs: someone else's island = NO")
    t, c, allm = reqs(world="default")
    K.check(allm and t[4] == "OK  At the hub", "X reqs: the hub (default world) = OK")
    S["role"] = "member"
    t, c, allm = reqs()
    K.check(allm and t[4] == "OK  On your island", "X reqs: a co-op member's island = OK")
    bridge.remove("skill:fn:run")
    bridge.remove("skill:fn:combat")
    t, c, allm = reqs()
    K.check(not allm and t[1] == "NO  Needs SkyySkills 0.4.35+" and t[3].startswith("OK"), "X reqs without SkyySkills: class NO (needs SkyySkills), combat unknown = OK")
    bridge.put("skill:fn:run", Fn(f_run))
    S["runs"] = {"mining": (2400, 1000), "foraging": (100, 1000), "farming": (600, 1000)}
    g = Chk.gains(u1, 0)
    gt = [str(x) for x in g[0]]
    K.check(gt[0].startswith("Class  +12 points") and gt[2] == "Mining  +12 points" and gt[1] == "Foraging  +0 (under 25 %)"
            and gt[5] == "Farming  +6 points" and gt[6] == "Fishing  -  no skill yet" and int(g[3]) == 30
            and "Void-Touched I" in str(g[2]) and "Dust x2" in str(g[2]),
            "X gains: Class 12, Mining r 2.4 = 12, Foraging under 25 %% = 0, Farming 6, Fishing none, extra line: %s / %s" % (gt, str(g[2])))
    K.check("Dust" not in str(Chk.gains(u1, 1)[2]) and "Void-Touched II" in str(Chk.gains(u1, 1)[2]), "X gains at rebirth 1: title II, no first-rebirth Dust line")
    req_ = Chk.reqs(u1, "island-x", 0)
    tip = str(Chk.tip(0, req_, g))
    K.check(tip.startswith("NEXUS OF THE VOID\nRebirth 1 of 10") and "REQUIREMENTS" in tip and "WHAT YOU WOULD GET" in tip and "Mining  +12 points" in tip
            and "collections +1 rank" in tip and "Open Bazaar / AH orders are checked" in tip,
            "X the Nexus tooltip text (the full extra line + the Bazaar line)")
    # fix round (critic): at the max nothing more to gain - no "Rebirth 11 of 10", no "Void-Touched XI", no gain lines
    gm = Chk.gains(u1, 10)
    tipm = str(Chk.tip(10, Chk.reqs(u1, "island-x", 10), gm))
    K.check(all(str(x).endswith("-  max reached") for x in gm[0]) and str(gm[2]) == "Max rebirths reached" and int(gm[3]) == 0 and bool(gm[5])
            and "Max rebirths reached (10 of 10)" in tipm and "Rebirth 11" not in tipm and "WHAT YOU WOULD GET" not in tipm and "XI" not in tipm
            and "NO  Rebirths done 10 / 10" in tipm, "X at the max: 'Max rebirths reached', no gain lines, no rebirth 11: %s" % tipm.replace("\n", " | ")[:200])

    # ---- RbPub.tick
    AL = JClass("java.util.ArrayList")
    on = AL()
    on.add(u1)
    Cfg.TEST_ONLINE = on
    K.eq(int(Pub.tick()), 1, "X tick: one online player")
    K.eq(int(bridge.get("rebirth:n:" + k1)), 3, "X rebirth:n:<uuid> = the active profile's count (profile 2: 3)")
    K.check(bridge.get("rebirth:busy:" + k1) == Bool.FALSE, "X rebirth:busy:<uuid> = false (published with rebirth:n)")
    Sto.BUSY.put(k2, Bool.TRUE)
    Pub.tick()
    K.check(bridge.get("rebirth:busy:" + k1) == Bool.TRUE, "X rebirth:busy:<uuid> = true while the active profile is busy")
    Sto.BUSY.clear()
    Pub.tick()
    bridge.put("profile:fn:key", Fn(lambda o: str(o)))
    Pub.tick()
    K.eq(int(bridge.get("rebirth:n:" + k1)), 0, "X a profile switch: republished (profile 1: 0)")
    Cfg.TEST_ONLINE = AL()
    Pub.tick()
    K.check(bridge.get("rebirth:n:" + k1) is None and bridge.get("rebirth:busy:" + k1) is None and Pub.PUB.isEmpty(), "X a leaver's rebirth:n + rebirth:busy keys are removed")
    Cfg.TEST_ONLINE = on
    Pub.tick()
    Pub.clearAll()
    K.check(bridge.get("rebirth:n:" + k1) is None and bridge.get("rebirth:busy:" + k1) is None and Pub.PUB.isEmpty(), "X clearAll (shutdown) removes every published key")
    Cfg.TEST_ONLINE = AL()
    bridge.put("profile:fn:key", Fn(lambda o: (str(o) + "-p2") if str(o) == k1 else None))

    # ---- /rebirth gate + permission group
    Cfg.ON = False
    Cfg.PERM_TEST = Fn(lambda o: Bool.FALSE)
    K.check(Cmd.gate(u1) is not None and "not switched on" in str(Cmd.gate(u1)), "X /rebirth off + player = refused in chat")
    Cfg.PERM_TEST = Fn(lambda o: Bool.TRUE)
    K.check(Cmd.gate(u1) is None, "X /rebirth off + admin = the page (view only)")
    Cfg.PERM_TEST = Fn(lambda o: Bool.FALSE)
    Cfg.ON = True
    K.check(Cmd.gate(u1) is None, "X /rebirth on = the page for everyone")
    try:
        cm = Cmd()
        K.check(str(cm.getName()) == "rebirth" and [str(x) for x in cm.getPermissionGroups()] == ["hytale:Adventurer"],
                "X /rebirth: a player command (hytale:Adventurer)")
    except Exception as e:
        K.check(False, "X /rebirth constructor: %s" % e)

    # ---- RbPage.build in every state + THE PROBE (the built page as a real CustomPage packet)
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    CP = JClass("com.hypixel.hytale.protocol.packets.interface_.CustomPage")
    LIFE = JClass("com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime")

    def build(world, on_):
        Cfg.ON = on_
        pg = Page(u1, world)
        b, ev = UCB(), UEB()
        pg.build(None, b, ev, None)
        cmds = b.getCommands()
        sets = {}
        apps = 0
        for cmd in cmds:
            sel = None if cmd.selector is None else str(cmd.selector)
            if str(cmd.type) == "Append" or "Append" in str(cmd.type):
                apps += 1
            if sel and cmd.data is not None and str(cmd.type) == "Set":
                sets[sel] = str(cmd.data)
        return pg, b, ev, cmds, sets, apps
    S["cls"] = (100, 100)
    S["role"] = "owner"
    pg, b, ev, cmds, sets, apps = build("island-x", True)
    K.check(pg.awake and str(pg.state).startswith("Nexus awake") and [str(x)[:2] for x in pg.rt][:5] == ["OK"] * 5 and str(pg.off) == "",
            "X page: everything met -> the Nexus awake, every line OK, no OFF line")
    tipsets = [s for s in sets if s.endswith("TooltipText")]
    K.check(tipsets == ["#SkyyRbNexus.TooltipText"] and "REQUIREMENTS" in sets["#SkyyRbNexus.TooltipText"], "X page: the Nexus tooltip is set (%s)" % tipsets)
    K.check(any(s.startswith("#SkyyRbReq0") for s in sets) and any(s.startswith("#SkyyRbArm7") for s in sets) and any(s.startswith("#SkyyRbExtra") for s in sets),
            "X page: the requirement / gain / extra lines are set: %d set commands" % len(sets))
    evs = ev.getEvents()
    K.check(len(evs) == 1, "X page: one binding (Close)")
    pg.handleDataEvent(None, None, '{"a":"close"}')            # test mode: no close on the wire
    S["cls"] = (37, 100)
    S["role"] = "visitor"
    pg2, _b, _e, _c, sets2, apps2 = build("elsewhere", False)
    K.check(not pg2.awake and str(pg2.state) == "Nexus asleep" and str(pg.state) == "Nexus awake" and str(pg2.off) == "Rebirth is OFF (admin view)"
            and str(pg2.rt[0]).startswith("NO") and str(pg2.rt[4]).startswith("NO"), "X page: off + not met -> asleep, OFF line, NO lines: %s / %s" % (str(pg2.state), str(pg.state)))
    S["role"] = "owner"
    # ---- THE FIT (fix round): the real left-panel texts at the widest numbers, measured with the kit (skyyui.text_lines) at the panel's
    # inner width (260 - 2 x 12) in the row heights the page markup declares
    import re as _re
    import skyyui as SUI
    heights = {}
    for cmd in cmds:
        try:
            tx = None if cmd.text is None else str(cmd.text)
        except Exception:
            tx = None
        for m_ in _re.finditer(r"Label #(SkyyRb(?:State|Count|Off|Req\d|Arm\d|Extra|Note)) \{ Anchor: \(([^)]*)\)", tx or ""):
            hm = _re.search(r"Height: (\d+)", m_.group(2))
            if hm:
                heights[m_.group(1)] = int(hm.group(1))
    K.check(len(heights) == 19, "X fit: the 19 left-panel rows found in the page markup (%d: %s)" % (len(heights), sorted(heights)[:4]))
    sv = (int(Cfg.MAX), int(Cfg.LEVELS), float(Cfg.DUST_FIRST))
    Cfg.MAX, Cfg.LEVELS, Cfg.DUST_FIRST = 100, 100, 10.0
    texts = []
    for cls_, ms_, role_, world_, on_, n_ in (((1000, 1000), 9999000, "visitor", "elsewhere", False, 0), ((999, 1000), 0, "owner", "island-x", True, 99),
                                              (None, 0, "owner", "default", True, 100), ((5, 100), 0, "member", "island-x", False, 7)):
        S["cls"], S["ms"], S["role"] = cls_, ms_, role_
        Cfg.ON = on_
        rr_ = Chk.reqs(u1, world_, n_)
        gg_ = Chk.gains(u1, n_)
        pgx = Page(u1, world_)
        pgx.build(None, UCB(), UEB(), None)
        texts += [("SkyyRbReq%d" % i, str(x)) for i, x in enumerate(rr_[0])] + [("SkyyRbArm%d" % i, str(x)) for i, x in enumerate(gg_[0])]
        texts += [("SkyyRbExtra", str(gg_[2])), ("SkyyRbState", str(pgx.state)), ("SkyyRbCount", str(pgx.count)), ("SkyyRbOff", str(pgx.off))]
    runs_ = S["runs"]
    S["runs"] = {}
    gg_ = Chk.gains(u1, 0)
    texts += [("SkyyRbArm%d" % i, str(x)) for i, x in enumerate(gg_[0])]
    S["runs"] = {"mining": (2400, 1000), "foraging": (100, 1000), "farming": (600, 1000), "smithing": (1600000, 1000)}
    gg_ = Chk.gains(u1, 0)
    texts += [("SkyyRbArm%d" % i, str(x)) for i, x in enumerate(gg_[0])]
    S["runs"] = runs_
    Cfg.MAX, Cfg.LEVELS, Cfg.DUST_FIRST = sv
    over = []
    for rid, tx in texts:
        if not tx or rid not in heights:
            continue
        sz, bd = (14, True) if rid == "SkyyRbState" else ((14, False) if rid == "SkyyRbCount" else (13, False))
        lines = SUI.text_lines(tx, 260 - 24, SUI.fs(sz), bold=bd)
        need = lines * SUI.line_height(SUI.fs(sz), bold=bd)
        if need > heights[rid] + 0.5 or (rid != "SkyyRbExtra" and lines > 1):
            over.append((rid, tx, lines, heights[rid]))
    K.check(not over and len(texts) > 80, "X fit: %d real left-panel texts at the widest numbers each fit their row (1 line; Extra 2): %s" % (len(texts), over[:3]))
    S["cls"], S["ms"], S["role"] = (100, 100), 0, "owner"
    Cfg.ON = True
    pk = CP("SkyyRb", True, True, LIFE.CanDismiss, cmds, evs)
    size, mx = int(pk.computeSize()), int(CP.MAX_SIZE)
    K.check(size < mx, "X THE PROBE: the whole radiating-tree page is one CustomPage packet of %d bytes (max %d), %d commands, %d appends"
            % (size, mx, len(cmds), apps))
    per_node = None
    try:
        b3 = UCB()
        for i in range(100):
            b3.appendInline("#SkyyRbCanvas", "Group #SkyyRbX%d { Anchor: (Width: 28, Height: 28, Left: %d, Top: %d); Background: #121825; }" % (i, i, i))
        per_node = (int(CP("x", True, True, LIFE.CanDismiss, b3.getCommands(), UEB().getEvents()).computeSize()) - int(CP("x", True, True, LIFE.CanDismiss, UCB().getCommands(), UEB().getEvents()).computeSize())) / 100.0
    except Exception as e:
        K.notes.append("per-node size probe: %s" % e)
    K.notes.append("THE PROBE: page packet %d bytes of CustomPage.MAX_SIZE %d (IS_COMPRESSED %s); %d commands (%d appends); one more node disc = %s bytes -> room for about %s more"
                   % (size, mx, bool(CP.IS_COMPRESSED), len(cmds), apps, per_node, int((mx - size) / per_node) if per_node else "?"))

    # ---- static: the plugin wiring
    gr = PW.calls(jar)
    su, sd = gr.get("SkyyRebirthPlugin.setup", set()), gr.get("SkyyRebirthPlugin.shutdown", set())
    K.check(all(PKG + x in su for x in ("RbCfg.loadCfg", "RbStore.start", "CfgPub.start")) and "java.util.Map.put" in su
            and any("scheduleAtFixedRate" in x for x in su) and any("registerCommand" in x for x in su),
            "X static: setup loads the config, starts the IO thread + the kit + the 5 s tick, registers /rebirth, publishes the functions")
    K.check(all(PKG + x in sd for x in ("RbStore.stop", "CfgPub.shutdown")) and "java.util.Map.remove" in sd and PKG + "RbPub.clearAll" in sd, "X static: shutdown stops the IO thread, flushes the kit, removes the functions")
    K.check(PKG + "RbPub.tick" in gr.get("RbTick.run", set()), "X static: RbTick.run -> RbPub.tick")
    K.check(not any("Thread.sleep" in x for m, cs in gr.items() if not m.startswith("Cfg") for x in cs), "X static: no Thread.sleep outside the config kit")
    K.save()


# ====================================================================================================== K: with the real SkyySkills 0.4.35 jar
def run_skills(out, jar, scratch, _home):
    from jpype import JClass, JArray
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, SKILLS_JAR], verify=True)
    R = lambda n: JClass(PKG + n)
    S = lambda n: JClass("com.skyy.skills." + n)
    Cfg, Sto, Fnc, Chk, Page = R("RbCfg"), R("RbStore"), R("RbFn"), R("RbCheck"), R("RbPage")
    SDefs, SCfg, SSto, SCap, SRun = S("SkillDefs"), S("SkillCfg"), S("SkillStore"), S("SkillCap"), S("SkillRunFn")
    UUID, Obj = JClass("java.util.UUID"), JClass("java.lang.Object")
    OA = lambda *xs: JArray(Obj)(list(xs))
    LOG = JClass("com.hypixel.hytale.logger.HytaleLogger")
    Cfg.LOG, SCfg.LOG = LOG.get("SkyyRebirth"), LOG.get("SkyySkills")
    base = os.path.join(scratch, "k")
    os.makedirs(os.path.join(base, "rb", "players"))
    os.makedirs(os.path.join(base, "sk", "players"))
    SCfg.FILE = path(os.path.join(base, "sk", "xp.properties"))
    SCfg.load()
    SSto.DIR = path(os.path.join(base, "sk", "players"))
    Sto.DIR = path(os.path.join(base, "rb", "players"))
    u = UUID.fromString("00000000-0000-4000-8000-00000000c0de")
    k = str(u)
    open(os.path.join(base, "rb", "players", k + ".properties"), "w").write("n=3\n")
    br = Cfg.bridge()
    K.check(JClass("java.lang.System").identityHashCode(br) == JClass("java.lang.System").identityHashCode(SSto.bridge()), "K one shared skyy.bridge map")
    br.put("rebirth:fn:cap", Fnc(1))
    br.put("skill:fn:run", SRun())
    MIN, EXP = int(SDefs.MINING), int(SDefs.EXPLORATION)
    arch = int(SDefs.indexOf("archery"))
    K.eq(int(SCap.cap(k, MIN)), int(SDefs.maxOf(MIN)) + 30, "K SkyySkills Mining cap = table + 3 rebirths x 10 (our rebirth:fn:cap)")
    K.eq(int(SCap.cap(k, arch)), int(SDefs.maxOf(arch)) + 30, "K SkyySkills class skill cap + 30")
    K.eq(int(SCap.cap(k, EXP)), int(SDefs.maxOf(EXP)), "K SkyySkills Exploration cap unchanged")
    k0 = "00000000-0000-4000-8000-00000000c0df"
    K.eq(int(SCap.cap(k0, MIN)), int(SDefs.maxOf(MIN)), "K a profile with 0 rebirths: the table cap")
    br.put("class:" + k, "Archer")
    d = SSto.dataK(k, u)
    cc = [int(x) for x in SDefs.cumOf(arch)]
    SSto.wr(d, arch, cc[-1])
    a = SRun().apply(OA(u, "class"))
    K.check(a is not None and int(a[0]) == int(SDefs.maxOf(arch)) and int(a[1]) == int(SDefs.maxOf(arch)) + 30,
            "K skill:fn:run class: level %s of cap %s (the table max is no longer the cap)" % (a[0], a[1]))
    Cfg.ON = True
    Cfg.HUB_TEST = "hub"
    rq = Chk.reqs(u, "hub", int(Sto.n(k)))
    K.check(str(rq[0][1]).startswith("NO  Class level %d / %d" % (int(SDefs.maxOf(arch)), int(SDefs.maxOf(arch)) + 30)) and str(rq[0][2]) == "OK  Rebirths done 3 / 10",
            "K RbCheck with the real SkyySkills: class %s, %s" % (str(rq[0][1]), str(rq[0][2])))
    pg = Page(u, "hub")
    pg.build(None, JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")(), JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")(), None)
    K.check(int(pg.n) == 3 and "Rebirths 3 / 10" == str(pg.count) and str(pg.at[2]).startswith("Mining"), "K the page with both mods: %s / %s" % (str(pg.count), str(pg.at[2])))
    K.save()


# ====================================================================================================== D: start twice on a scratch copy
def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    P = lambda n: JClass(PKG + n)
    Cfg, Sto, CPub = P("RbCfg"), P("RbStore"), P("CfgPub")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyRebirth")
    mods = os.path.dirname(home)
    before = snap(mods)
    keys = sorted(fn[:-11] for fn in os.listdir(os.path.join(home, "players")) if fn.endswith(".properties")) if os.path.isdir(os.path.join(home, "players")) else []

    def start():
        rb = os.path.join(mods, "Skyy_SkyyRebirth")
        Cfg.DIR = path(rb)
        Cfg.FILE = path(os.path.join(rb, "config.properties"))
        r = str(Cfg.loadCfg(True))
        Sto.DIR = path(os.path.join(rb, "players"))
        Sto.CACHE.clear()
        CPub.start(path(mods), Cfg.LOG)
        ns = [int(Sto.n(k_)) for k_ in keys]
        CPub.flush()
        return r, ns
    r1, ns1 = start()
    s1 = snap(mods)
    r2, ns2 = start()
    s2 = snap(mods)
    added = sorted(set(s1) - set(before))
    K.check(all(a_.startswith("Skyy_SkyyRebirth/") for a_ in added) and "Skyy_SkyyRebirth/config.properties" in added,
            "D start 1 writes only into Skyy_SkyyRebirth/: %s" % added)
    K.check(all(before[f] == s1.get(f) for f in before), "D start 1: the copied Skyy_SkyySkills is byte-identical")
    K.check(s1 == s2, "D start 2 changes nothing (%s)" % sorted(f for f in set(s1) | set(s2) if s1.get(f) != s2.get(f)))
    K.check(len(keys) > 0 and set(ns1) == {0} and ns1 == ns2, "D every live profile (%d) counts 0 rebirths" % len(keys))
    K.check(r1.startswith("default config.properties written") and r2.startswith("rebirth OFF"), "D the first start writes the default file (rebirth OFF), the second reads it")
    K.save()


# ====================================================================================================== parent (harness_kit without the class compare: a new mod)
def main():
    phases = {"exec": run_exec, "skills": run_skills, "live": run_live}
    if "--phase" in sys.argv:
        ph = HK.arg("--phase")
        try:
            if ph == "mkfake":
                HK.run_mkfake(os.path.join(SCRATCH, "fake"), JAR)
            elif ph == "verify":
                HK.run_verify(HK.arg("--out"), JAR)
            elif ph == "audit":
                HK.run_audit(HK.arg("--out"), JAR, os.path.join(SCRATCH, "fake"))
            else:
                phases[ph](HK.arg("--out"), JAR, SCRATCH, HK.arg("--home"))
        except SystemExit:
            raise
        except Exception:
            import traceback
            traceback.print_exc()
            sys.exit(1)
        return
    assert os.path.isfile(JAR), JAR
    assert os.path.isfile(SKILLS_JAR), SKILLS_JAR
    sc = os.path.realpath(SCRATCH)
    assert sc.startswith(os.path.realpath(os.path.join(ROOT, "tools", "dev", "scratch")) + os.sep), "the scratch folder must be inside tools/dev/scratch/"
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(os.path.join(SCRATCH, "tmp"))
    os.makedirs(os.path.join(SCRATCH, "fake"))
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"

    def child(label, *extra):
        o = os.path.join(SCRATCH, "%s.json" % label)
        p = subprocess.run([sys.executable, os.path.abspath(__file__), "--phase", label, "--out", o, "--dir", SCRATCH, "--jar", JAR] + list(extra), env=env)
        HK.check(p.returncode == 0, "%s: the child exited cleanly (%s)" % (label, p.returncode))
        return o
    try:
        child("mkfake")
        HK.take(child("verify"), "verify")
        HK.take(child("exec"), "exec")
        HK.take(child("skills"), "skills")
        live_home = os.path.join(SCRATCH, "live", "mods", "Skyy_SkyySkills")
        if os.path.isdir(LIVE_DIR):
            shutil.copytree(LIVE_DIR, live_home)
            print("D. live Skyy_SkyySkills copied (read-only source %s)" % LIVE_DIR)
            HK.take(child("live", "--home", live_home), "live")
        else:
            HK.check(False, "D: no live folder %s" % LIVE_DIR)
        outa = child("audit")
        if os.path.isfile(outa):
            a = json.load(open(outa))
            HK.check(not a["refused"] and a["refs"] > 100, "AA: engine-access audit: %d references in %d classes, refused %s" % (a["refs"], a["classes"], a["refused"][:5]))
            HK.check(len(a["control"]) == 1 and "sendUpdate" in a["control"][0], "AA: the control is refused: %s" % a["control"])
            print("AA. engine-access audit: %d references in %d classes, %d refused, control refused" % (a["refs"], a["classes"], len(a["refused"])))
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyRebirth %s harness: %d ok, %d fail(s)" % (VERSION, HK.OKS[0], len(HK.FAILS)))
    for f in HK.FAILS:
        print("FAIL:", f)
    sys.exit(1 if HK.FAILS else 0)


if __name__ == "__main__":
    main()
