"""Harness for SkyyMobs 0.1.20 (round eggs D5b-2: the secret dragon egg finds - Void / Blood / Light through SkyyPets' doors;
tools/mobs_0_1_20_patch.py).
Build first:
    python tools/mobs_0_1_20_patch.py && python SkyyMobs/build_skyymobs_0.1.20.py
    python SkyyMobs/test_skyymobs_0.1.20.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  S     static   the patch re-runs to identical bytes (--out), line endings kept, +3 classes / +1 system / no command; jar: only the 3 new
                 classes added, the only non-class change is the manifest
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.1.19 -> 0.1.20 (EXPECT below)
  X     exec     EXECUTES MobSecret in a bare JVM: the default patterns (Void mobs / places, islands' Env_Default_Void left out), -Pattern
                 exclusions, a live edit; night hours (21-5, 6-18, bad text refused by checkNight; nightAt by HOUR_TEST, no clock = never);
                 the Heart (HEART_API, "-" = none needed); no SkyyPets = no door (null, counted); onKill: a Void kill rolls "void" once
                 (secretRoll, the drop owner, never giveSecretEgg), a Void-born mob rolls it too, a plain kill nothing; Blood only for an
                 elite / boss of Zone 4+ at night with a Heart (day / Zone 3 / no Heart / plain mob = no roll); Light: Zone 1-4 bosses set
                 flags per profile (profile:fn:key), the 4th = giveSecretEgg "light" (no roll), OK clears, HAS_EGG keeps the flags, a party
                 member credited (MobCredit) gets flags too, a death clears (throttled), switch off = nothing; the flag file round-trips
                 (atomic write, profile keys with ':' kept); mob:fn:voidAt refuses bad args / no world; LightDeathSys constructs
  EX119 0.1.19's exec phase EXECUTED on this jar (Spoils x1.5 unchanged)
  D     live     start twice on a scratch COPY of Skyy's live NewBetaTest Skyy_SkyyMobs: config.properties / bands.properties /
                 trees.properties bytes untouched (no migration), the secret rows = their defaults, the flag file created only by a flag,
                 read back by start 2
  AA    engine-access audit
NOT COVERED (UNVERIFIED in game): SpoilsSys.tick inside the ECS death dispatch calling onKill (the call site), LightDeathSys inside the ECS
(Player + DeathComponent query), WorldTimeResource's hour on a live world, the Heart read from a live Player inventory, mob:fn:voidAt on a
loaded chunk.
Scratch: tools/dev/scratch/eggs/mobs (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.1.20"
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "eggs", "mobs")]
import skyybuild as B
import harness_kit as HK

_run0 = HK.run
HK.run = lambda *a, **k: None          # import 0.1.19's harness for its exec phase without running it
_s = importlib.util.spec_from_file_location("test_skyymobs_0_1_19", os.path.join(HERE, "test_skyymobs_0.1.19.py"))
T119 = importlib.util.module_from_spec(_s)
_s.loader.exec_module(T119)
HK.run = _run0

GEN = os.path.join(HERE, "build_skyymobs_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyymobs_0.1.19.py")
PATCH = os.path.join(ROOT, "tools", "mobs_0_1_20_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMobs-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMobs-0.1.19.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.mobs."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyMobs")
ADDED = ["LightDeathSys", "MobSecret", "MobVoidAtFn"]
EXPECT = {
    "MobCfg": ["+f SEC_BHEART", "+f SEC_BNIGHT", "+f SEC_BZONE", "+f SEC_LZONES", "+f SEC_ON", "+f SEC_VMOBS", "+f SEC_VPLACES",
               "~<clinit>", "~m apply", "~m load", "~m reloadAll", "~m useDefaults"],          # apply = the line parser; the rest = the default text
    "SpoilsSys": ["~m tick"],
    "SkyyMobsPlugin": ["~m setup", "~m shutdown", "~m systems"],
    "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "CfgFile": ["~<clinit>"],          # the kit: the 7 new rows + the default file text
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
T119.PKG = PKG
U1 = "00000000-0000-0000-0000-000000000121"
U2 = "00000000-0000-0000-0000-000000000122"


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyMobs 0.1.20 - build script') and g.count('VERSION = "0.1.20"') == 1, "S header + VERSION")
    K.eq((g.count("registerSystem(") - o.count("registerSystem("), g.count("registerCommand(") - o.count("registerCommand("),
          g.count("makeClass(") - o.count("makeClass(")), (1, 0, 3), "S +1 system (LightDeathSys), no command, +3 classes")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    K.eq((sorted(nb - na), sorted(na - nb)), (sorted("com/skyy/mobs/%s.class" % c for c in ADDED), []), "S only the 3 new classes added")
    K.eq(sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n)), ["manifest.json"], "S the only non-class change is the manifest")
    K.save()


def run_exec(out, jar, scratch, home):
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    C, S, CR = JClass(PKG + "MobCfg"), JClass(PKG + "MobSecret"), JClass(PKG + "MobCredit")
    UUID, Paths = JClass("java.util.UUID"), JClass("java.nio.file.Paths")
    u1, u2 = UUID.fromString(U1), UUID.fromString(U2)
    C.useDefaults()
    d = str(C.DEF_CFG)
    K.check("\nsecret.eggs=true\n" in d and "\nsecret.void.places=Env_Void, Env_Portal_Goblin_Cave_Void, Env_Dungeon_Goblin_Void\n" in d
            and "\nsecret.blood.night=21-5\n" in d and "\nsecret.light.zones=4\n" in d, "X the default file carries the secret rows")
    K.check(bool(C.SEC_ON) and int(C.SEC_BZONE) == 4 and int(C.SEC_LZONES) == 4 and str(C.SEC_BHEART) == "Ingredient_Voidheart", "X defaults in force")
    # 1. patterns
    vm = [bool(S.voidMob(r)) for r in ("Crawler_Void", "void_spectre", "Bear_Voidtaken", "Void_Anomaly_Crystal_Small", "Bear_Voidtaken_Tentacle_Marker", "Skeleton", None)]
    K.eq(vm, [True, True, True, False, False, False, False], "X Void mobs: *Void* (any case) minus the anomaly crystals / tentacle marker")
    vp = [bool(S.voidPlace(e)) for e in ("Env_Void", "env_portal_goblin_cave_void", "Env_Dungeon_Goblin_Void", "Env_Default_Void", "Env_Zone1_Plains", None)]
    K.eq(vp, [True, True, True, False, False, False], "X Void places: the 3 vanilla Void environments; NOT Env_Default_Void (every SkyyIslands island)")
    C.SEC_VMOBS = "Trork_*, -Trork_Chieftain, *"
    K.eq([bool(S.voidMob(r)) for r in ("Trork_Warrior", "Trork_Chieftain", "Skeleton")], [True, False, False], "X a live edit: Prefix* + -exclusion, a lone * skipped")
    C.useDefaults()
    # 2. night
    K.eq([bool(S.isNightHour(h, "21-5")) for h in (20, 21, 23, 0, 4, 5, 12)], [False, True, True, True, True, False, False], "X 21-5 wraps midnight")
    K.eq([bool(S.isNightHour(h, "6-18")) for h in (5, 6, 17, 18)], [False, True, True, False], "X 6-18 a plain range")
    K.eq([bool(S.isNightHour(h, "junk")) for h in (22, 12)], [True, False], "X a bad text = the built-in 21-5")
    K.check(S.checkNight("k", "21-5") is None and S.checkNight("k", None) is None and all(S.checkNight("k", v) is not None for v in ("21", "24-3", "5-5", "a-b", "-5")),
            "X checkNight takes 21-5 / a reset, refuses one hour, 24, equal hours, words")
    S.HOUR_TEST = 22
    n22 = int(S.nightAt(None))
    S.HOUR_TEST = 12
    n12 = int(S.nightAt(None))
    S.HOUR_TEST = -2
    nno = int(S.nightAt(None))
    S.HOUR_TEST = -1
    K.eq((n22, n12, nno, int(S.nightAt(None))), (1, 0, -1, -1), "X nightAt: hour 22 night, 12 day, no clock / no store = -1 (never night)")
    # 3. the Heart
    K.eq([str(x) for x in S.hearts()], ["Ingredient_Voidheart"], "X Heart ids = the default")
    K.check(not bool(S.heart(u1, None)), "X no SkyyPets seam + no live player = no Heart (never throws)")
    C.SEC_BHEART = "-"
    K.check(len(S.hearts()) == 0 and bool(S.heart(u1, None)), "X '-' = no Heart needed")
    C.useDefaults()
    HEART = {U1: True}

    @JImplements("java.util.function.Function")
    class Heart(object):
        @JOverride
        def apply(self, u):
            return JClass("java.lang.Boolean")(HEART.get(str(u), False))
    S.HEART_API = Heart()
    K.eq((bool(S.heart(u1, None)), bool(S.heart(u2, None))), (True, False), "X HEART_API seam answers per player")
    # 4. no door
    nd = int(S.NODOOR)
    K.check(S.ask(True, u1, "void", "t") is None and int(S.NODOOR) == nd + 1, "X no SkyyPets door = null (nothing happens, counted)")
    CALLS = []
    ANS = {"roll": "MISS", "give": "OK"}

    def mkdoor(kind):
        @JImplements("java.util.function.Function")
        class Door(object):
            @JOverride
            def apply(self, a):
                CALLS.append((kind, str(a[0]), str(a[1]), str(a[2])))
                return ANS[kind]
        return Door()
    br.put("pets:fn:secretRoll", mkdoor("roll"))
    br.put("pets:fn:giveSecretEgg", mkdoor("give"))
    PK = {U1: "p1:" + U1, U2: "p2=" + U2}          # profile keys with ':' and '=' (the file must keep them)

    @JImplements("java.util.function.Function")
    class Key(object):
        @JOverride
        def apply(self, u):
            return PK.get(str(u))
    br.put("profile:fn:key", Key())
    li = os.path.join(scratch, "lightdir")
    os.makedirs(li, exist_ok=True)
    S.load(Paths.get(li))
    # 5. onKill: Void
    mob = UUID.randomUUID()
    del CALLS[:]
    S.HOUR_TEST = 12
    tr = str(S.onKill(None, "Crawler_Void", "Env_Zone1_Plains", 10, "", mob, u1))
    K.eq(CALLS, [("roll", U1, "void", "SkyyMobs:void-kill Crawler_Void")], "X a Void mob kill = ONE secretRoll 'void' for the drop owner (%s)" % tr)
    del CALLS[:]
    S.onKill(None, "Trork_Warrior", "Env_Void", 10, "", mob, u1)
    K.eq([c[:3] for c in CALLS], [("roll", U1, "void")], "X a mob born in Env_Void rolls it too")
    del CALLS[:]
    S.onKill(None, "Trork_Warrior", "Env_Default_Void", 10, "", mob, u1)
    S.onKill(None, "Trork_Warrior", None, 70, "elite", mob, u1)
    K.eq(CALLS, [], "X an island mob / a daytime elite: nothing")
    # 6. Blood
    S.HOUR_TEST = 23
    lv4 = 70          # Zone 4 (61-80)
    for role, lvl, rw, who, want in (("Trork_Warrior", lv4, "elite", u1, 1), ("Trork_Warrior", lv4, "mini", u1, 1), ("Trork_Warrior", lv4, "", u1, 0),
                                     ("Trork_Warrior", 50, "elite", u1, 0), ("Trork_Warrior", lv4, "elite", u2, 0), ("Trork_Warrior", 95, "boss", u1, 1)):
        del CALLS[:]
        S.onKill(None, role, None, lvl, rw, UUID.randomUUID(), who)
        K.eq(len([c for c in CALLS if c[2] == "blood"]), want, "X Blood: %s Lv %d rank %r Heart %s at night -> %d roll" % (role, lvl, rw, HEART.get(str(who), False), want))
        K.check(all(c[0] == "roll" for c in CALLS if c[2] == "blood"), "X Blood goes through secretRoll (the chance in SkyyPets)")
    S.HOUR_TEST = 12
    del CALLS[:]
    S.onKill(None, "Trork_Warrior", None, lv4, "elite", UUID.randomUUID(), u1)
    K.eq(CALLS, [], "X Blood: the same elite by day = nothing")
    S.HOUR_TEST = -2
    S.onKill(None, "Trork_Warrior", None, lv4, "elite", UUID.randomUUID(), u1)
    K.eq(CALLS, [], "X Blood: no clock = never night = nothing")
    # 7. Light
    boss = None
    for r in ("Dragon_Fire", "Trork_Boss_Warlord", "Golem_Firesteel"):
        if bool(C.isBoss(r)):
            boss = r
            break
    K.check(boss is not None, "X a Boss roles default exists (%s)" % boss)
    S.HOUR_TEST = 12
    tops = [int(x) for x in C.BOSS_TOP]
    K.eq(tops[:4], [20, 40, 60, 80], "X zone tops 20 40 60 80")
    K.eq([int(S.zoneOf(x)) for x in (0, 1, 20, 21, 60, 80, 81, 150)], [0, 1, 1, 2, 3, 4, 5, 5], "X zoneOf = MobBossFn.zoneOf")
    del CALLS[:]
    ANS["give"] = "HAS_EGG"
    for lv in (10, 30, 50):
        S.onKill(None, boss, None, lv, "boss", UUID.randomUUID(), u1)
    K.eq((int(S.maskOf(PK[U1])), [c for c in CALLS if c[0] == "give"]), (7, []), "X Zones 1-3 guardians: flags 1+2+4, no egg yet")
    S.onKill(None, boss, None, 75, "boss", UUID.randomUUID(), u1)
    K.eq([c for c in CALLS if c[0] == "give"], [("give", U1, "light", "SkyyMobs:light-run")], "X the Zone 4 guardian with 3 flags = giveSecretEgg 'light' (no roll)")
    K.eq(int(S.maskOf(PK[U1])), 15, "X HAS_EGG = the flags are kept (the next guardian kill asks again)")
    ANS["give"] = "OK"
    del CALLS[:]
    S.onKill(None, boss, None, 15, "boss", UUID.randomUUID(), u1)
    K.eq(([c[:3] for c in CALLS if c[0] == "give"], int(S.maskOf(PK[U1]))), ([("give", U1, "light")], 0), "X a later guardian kill asks again; OK = run done, flags cleared")
    K.check(not [c for c in CALLS if c[0] == "roll" and c[2] == "light"], "X Light never through secretRoll")
    # the file round-trips (profile keys with ':' / '=')
    S.onKill(None, boss, None, 15, "boss", UUID.randomUUID(), u1)
    m2 = UUID.randomUUID()
    CR.hit(str(m2), U2, 50.0, 100.0, 0.0, 200.0, 1000)
    CR.hit(str(m2), U1, 10.0, 90.0, 0.0, 200.0, 1001)
    S.onKill(None, boss, None, 35, "boss", m2, u1)
    K.eq((int(S.maskOf(PK[U1])), int(S.maskOf(PK[U2]))), (3, 2), "X a party kill: every credited player gets the flag (owner Zones 1+2, the helper Zone 2)")
    f = os.path.join(li, "secret-light.properties")
    K.check(os.path.isfile(f) and not os.path.exists(f + ".tmp"), "X the flag file is written (atomic, no .tmp left)")
    S.load(Paths.get(li))
    K.eq((int(S.maskOf(PK[U1])), int(S.maskOf(PK[U2])), int(S.LIGHT.size())), (3, 2, 2), "X a restart reads the flags back (keys with ':' / '=' kept)")
    # death clears (throttled)
    cl = int(S.CLEARS)
    K.check(bool(S.died(u2, 100000)) and int(S.maskOf(PK[U2])) == 0 and int(S.CLEARS) == cl + 1, "X a death clears that profile's flags")
    K.check(bool(S.died(u1, 101000)), "X the throttle is per player: u1's death 1 s after u2's still runs")
    K.eq(int(S.maskOf(PK[U1])), 0, "X u1's death 1 s later still counts (a different player)")
    S.onKill(None, boss, None, 15, "boss", UUID.randomUUID(), u1)
    K.check(not bool(S.died(u1, 102000)) and int(S.maskOf(PK[U1])) == 1, "X the same player within 3 s: throttled (one check per death)")
    K.check(bool(S.died(u1, 105000)) and int(S.maskOf(PK[U1])) == 0, "X after 3 s the death check runs again")
    S.load(Paths.get(li))
    K.eq(int(S.LIGHT.size()), 0, "X the cleared flags are gone from the file")
    # Light zones row = 2
    C.SEC_LZONES = 2
    del CALLS[:]
    S.onKill(None, boss, None, 15, "boss", UUID.randomUUID(), u2)
    S.onKill(None, boss, None, 55, "boss", UUID.randomUUID(), u2)
    S.onKill(None, boss, None, 35, "boss", UUID.randomUUID(), u2)
    K.eq([c[:3] for c in CALLS if c[0] == "give"], [("give", U2, "light")], "X secret.light.zones 2: Zones 1 + 2 = the egg (a Zone 3 boss sets no flag)")
    C.useDefaults()
    # switch off
    C.SEC_ON = False
    del CALLS[:]
    K.eq((str(S.onKill(None, "Crawler_Void", "Env_Void", 70, "boss", UUID.randomUUID(), u1)), CALLS), ("", []), "X secret.eggs off = nothing at all")
    C.useDefaults()
    K.eq(str(S.onKill(None, "Crawler_Void", None, 10, "", UUID.randomUUID(), None)), "", "X no drop owner = nothing")
    # mob:fn:voidAt
    F = JClass(PKG + "MobVoidAtFn")()
    OA = JClass("java.lang.Object[]")
    D = JClass("java.lang.Double")
    K.eq([F.apply(x) for x in (None, "w", OA([]), OA(["nowhere", D(1.0), D(2.0), D(3.0)]), OA(["w", D(float("nan")), D(1.0), D(1.0)]))], [None] * 5,
         "X mob:fn:voidAt: bad args / no such world / NaN = null (never throws)")
    JClass(PKG + "LightDeathSys")()
    t = str(S.text())
    K.check("secret eggs on" in t and "found" in t and "Blood Zone 4+" in t and "mob:fn:voidAt" in t, "X ready-line text: %s" % t)
    S.HEART_API = None
    S.HOUR_TEST = -1
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    Cfg, S, Sp = JClass(PKG + "MobCfg"), JClass(PKG + "MobSecret"), JClass(PKG + "MobSpoils")
    P = JClass("java.nio.file.Paths")
    files = [f for f in ("config.properties", "bands.properties", "trees.properties") if os.path.isfile(os.path.join(home, f))]
    before = dict((f, open(os.path.join(home, f), "rb").read()) for f in files)
    K.check("config.properties" in files, "D the live copy has a config.properties (%s)" % files)
    lf = os.path.join(home, "secret-light.properties")
    had = os.path.isfile(lf)

    def start():
        Cfg.DIR = P.get(home)
        Cfg.FILE = P.get(os.path.join(home, "config.properties"))
        Cfg.BANDS = P.get(os.path.join(home, "bands.properties"))
        o = "".join(str(JClass(PKG + m).run(P.get(home))) for m in ("MobMig", "MobMig14", "MobMig11", "MobMig12", "MobMigP4"))
        o += str(Sp.migrateWc15(P.get(home)))
        Cfg.load()
        Sp.loadV3(P.get(home))
        S.load(P.get(home))
        return o
    o1 = start()
    K.check(bool(Cfg.SEC_ON) and str(Cfg.SEC_VPLACES) == "Env_Void, Env_Portal_Goblin_Cave_Void, Env_Dungeon_Goblin_Void" and int(Cfg.SEC_BZONE) == 4,
            "D start 1: the live file has no secret lines -> the defaults (%s / %s)" % (Cfg.SEC_ON, Cfg.SEC_VPLACES))
    K.eq(dict((f, open(os.path.join(home, f), "rb").read() == before[f]) for f in files), dict((f, True) for f in files),
         "D start 1: config / bands / trees bytes untouched (no migration; older updates %r)" % o1[:60])
    K.eq(os.path.isfile(lf), had, "D start 1: no flag file is made by a start")
    u = JClass("java.util.UUID").fromString(U1)
    S.HOUR_TEST = 12
    boss = "Dragon_Fire" if bool(Cfg.isBoss("Dragon_Fire")) else None
    K.check(boss is not None, "D Dragon_Fire is a live Boss roles mob")
    if boss:
        S.onKill(None, boss, None, 30, "boss", JClass("java.util.UUID").randomUUID(), u)          # no SkyyPets: a flag, no door
    K.check(os.path.isfile(lf) and int(S.maskOf(U1)) == 2, "D a Zone 2 guardian kill writes the flag file (no profiles mod: key = the UUID)")
    o2 = start()
    K.eq((o2, int(S.maskOf(U1))), ("", 2), "D start 2: nothing migrates, the flag reads back")
    K.eq(dict((f, open(os.path.join(home, f), "rb").read() == before[f]) for f in files), dict((f, True) for f in files), "D start 2: bytes still untouched")
    K.save()


HK.run("SkyyMobs", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("static", run_static), ("exec", run_exec), ("ex119", T119.run_exec), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyMobs"))
