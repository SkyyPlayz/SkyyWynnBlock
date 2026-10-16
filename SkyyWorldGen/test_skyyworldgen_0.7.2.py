"""SkyyWorldGen 0.7.2 - harness for /SPAWN FOR PLAYERS (tools/worldgen_0_7_2_patch.py, lean round small01) = the 0.7.1 harness
(ZONE 1 = THE SERVER SPAWN + the zone-world weather guard) with: CC / JT against 0.7.1 (no class added, only WgSpawnHome / WgSpawnCmd /
plugin / kit texts change), S7 + the top /spawn OPEN (no node, groups []) and the NON-ADMIN cases (a second stand-in player without
skyyworldgen.admin: plain /spawn and /spawn 2 -> the Zone 1 landing; switch off / no landing -> "No server spawn is set yet", never
vanilla's execute), AA's tree diff vs the baseline = /spawn's group only. 0.7.1 header follows. Bare child
JVMs: the game's own JRE, the installed HytaleServer.jar (read only), -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in the
scratch folder. Engine stand-ins (store, worlds with a task queue, Universe, players) from SkyyProfiles/test_skyyprofiles_0.1.10.py
(engine()), JVM helpers + the class compare from SkyySkills/test_skyyskills_0.4.27.py (both read only). The live Skyy_SkyyWorldGen folder
is only READ (copied into scratch) and checked afterwards. Plus ONE offline server start (section VP, tools/smoke_test.py - the only
allowed start) when no HytaleServer runs.

    python SkyyWorldGen/test_skyyworldgen_0.7.2.py --dir <empty folder inside tools/dev/scratch/> [--keep] [--no-smoke]

SECTIONS
  CC  class compare 0.7 -> 0.7.1: + exactly WgSpawnCmd / WgSpawnHome / WgSpawnReady / WgWeather; every generator class (0.5 / 0.6 / 0.7)
      and WgOpen / WgSpawnTask / WgDone / WgApplyLanding / WgReady / WgStore / WgLog / WgZoneArrive UNCHANGED; changes only in the
      config / commands / setlanding / hooks / plugin (+ the kit)
  JT  jar entries = 0.7's + the 4 classes; every other entry byte-identical (but the version in the template comments / manifest)
  A   every class of both jars loads, verifies (-Xverify:all) and initialises
  W   the weather guard EXECUTED: a real vanilla WeatherResource (its map answers MIN_VALUE for an unknown environment = the NPE input)
      -> fixMap -> vanilla's own getWeatherIndexForEnvironment answers 0 (SensorWeather: no match, no NPE); idempotent; a filled map;
      validWeather / forecastOf edge cases; fix() on a world without an entity store; tick() hands one task per loaded SkyyWorldGen world
      to that world (and skips others); start / stop
  S   the server spawn EXECUTED: the login decision table; plain /spawn parsing; the two config keys (apply, check hook, spawnText);
      /zone setlanding in the zone world (on Zone 1 = saved through the kit, on Zone 2 / the void / no layout = refused, the old test
      island + the 0.6 world unchanged); WgSpawnHome.send: no landing (vanilla + ONE WARN), switch off, zone world off, in the zone world
      (Teleport to the landing), from the default world (the loading-instance trip), the zone world never made (vanilla + WARN); /zone 1
      with and without a landing; the LOGIN ROUTING through the real scheduler: no SkyyIslands -> Zone 1; SkyyIslands lists an island ->
      stays; SkyyIslands lists none -> asked again 4 s later, then Zone 1; a second ready / another world -> nothing; disconnect ends the
      session; /spawn = WgSpawnCmd: vanilla's tree, /spawn + <player> admin-only, set / default vanilla's groups, plain /spawn -> Zone 1,
      /spawn 2 -> vanilla's execute
  ST  START TWICE on a scratch COPY of the live Skyy_SkyyWorldGen (WgCfg.load, WgStore.read, the config kit): no file changed, defaults
  VP  tools/smoke_test.py --jar <0.7.1>: PASS, the ready line, /spawn is ours, no SEVERE from SkyyWorldGen
  AA  python tools/ci/crosscheck.py --jar <0.7.1> --baseline: READY; the tree diff = + the /spawn nodes (no FAIL / WARN)
"""
import os, sys, re, json, shutil, subprocess, zipfile, importlib.util, time, glob, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, PREV_VERSION = "0.7.2", "0.7.1"
PKG = "com.skyy.worldgen."
NEW_CLASSES = []
FROZEN = ["WgIsle", "WgIsleGen", "WgMaskFn", "WgMaskHop", "WgIsleProvider", "WgIsleSupplier", "WgSpawnTask", "WgDone", "WgApplyLanding",
          "WgReady", "WgStore", "WgLog", "WgZoneLayout", "WgZoneIsles", "WgZoneGen", "WgZoneFn", "WgZoneHop", "WgZoneProvider", "WgZoneSupplier",
          "WgZoneSampler", "WgZ2Fn", "WgZ2Gen", "WgZ2Hop", "WgZ2Isles", "WgZ2Layout", "WgZ2Provider", "WgZ2River", "WgZ2Supplier", "WgOpen",
          "WgZoneArrive", "WgZones", "WgCheck"]
ALLOWED = {"WgSpawnHome", "WgSpawnCmd", "SkyyWorldGenPlugin"}   # 0.7.2


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "small01", "wg")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyWorldGen-%s.jar" % VERSION)))
PREV_JAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyyWorldGen-%s.jar" % PREV_VERSION)))
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
LIVE = os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyyWorldGen")
SKILLS_HARNESS = os.path.join(ROOT, "SkyySkills", "test_skyyskills_0.4.27.py")
PROF_HARNESS = os.path.join(ROOT, "SkyyProfiles", "test_skyyprofiles_0.1.10.py")
FAILS, OKS, NOTES = [], [0], []
FAKE_DISKS = [  # (cx, cz, r, class) - the 0.7 harness's synthetic zone map (first match wins)
    (300.0, 200.0, 120.0, 2), (-400.0, -300.0, 30.0, 0), (0.0, 0.0, 1500.0, 1), (4000.0, 0.0, 900.0, 2), (0.0, 4500.0, 1000.0, 3),
    (-4200.0, 0.0, 700.0, 4), (0.0, -4200.0, 600.0, 4), (-3000.0, 600.0, 150.0, 4)]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)
    return cond


def mod(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    saved = list(sys.argv)
    sys.argv = [sys.argv[0], "--dir", SCRATCH]
    try:
        spec.loader.exec_module(m)
    finally:
        sys.argv = saved
    m.SCRATCH = SCRATCH
    return m


def snap(d):
    return dict((os.path.relpath(os.path.join(r, f), d).replace(os.sep, "/"), open(os.path.join(r, f), "rb").read())
                for r, _ds, fs in os.walk(d) for f in fs) if os.path.isdir(d) else {}


# ============================================================================================ child (one JVM, -Xverify:all)
def run_e(out):
    import jpype
    from jpype import JClass, JArray, JInt
    import skyybuild as B
    S = mod(SKILLS_HARNESS, "ts0427")
    TP = mod(PROF_HARNESS, "tp0110")
    hcls = os.path.join(SCRATCH, "hclasses")
    os.makedirs(hcls, exist_ok=True)
    os.chdir(SCRATCH)
    S.jvm_start([hcls])
    R = {"load": {}}
    L = {}
    for tag, j in (("new", JAR), ("prev", PREV_JAR)):
        L[tag] = S.loader(j)
        R["load"][tag] = S.load_all(j, L[tag])
    E = {}
    try:
        N = TP.engine(S, B, hcls, "skyywg071")
        jf, U = N["jf"], N["U"]
        HPool = JClass("javassist.ClassPool")(False)
        HPool.appendSystemPath()
        Ctm, Ctc, Ctf = JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor"), JClass("javassist.CtField")
        fm = HPool.makeClass("skyywg071.FakeMap")
        fm.addInterface(HPool.get("java.util.function.IntBinaryOperator"))
        fm.addConstructor(Ctc.make("public FakeMap() { }", fm))
        body = "public int applyAsInt(int x, int z) {\n"
        for cx, cz, r, c in FAKE_DISKS:
            body += "  if (((double) x - %r) * ((double) x - %r) + ((double) z - %r) * ((double) z - %r) <= %r) return %d;\n" % (cx, cx, cz, cz, r * r, c)
        body += "  return 0;\n}"
        fm.addMethod(Ctm.make(body, fm))
        fh = HPool.makeClass("skyywg071.FlatH")
        fh.addInterface(HPool.get("java.util.function.IntBinaryOperator"))
        fh.addField(Ctf.make("public int h;", fh))
        fh.addConstructor(Ctc.make("public FlatH(int h) { this.h = h; }", fh))
        fh.addMethod(Ctm.make("public int applyAsInt(int x, int z) { return this.h; }", fh))
        for c_ in (fm, fh):
            c_.writeFile(hcls)
        FakeMap, FlatH = JClass("skyywg071.FakeMap"), JClass("skyywg071.FlatH")
        UUID, Paths, Thread = JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.lang.Thread")
        TRF = JClass("com.hypixel.hytale.math.vector.Transform")
        GSP = JClass("com.hypixel.hytale.server.core.universe.world.spawn.GlobalSpawnProvider")
        WLDc = JClass("com.hypixel.hytale.server.core.universe.world.World")
        WCFGc = JClass("com.hypixel.hytale.server.core.universe.world.WorldConfig")
        UniC = JClass("com.hypixel.hytale.server.core.universe.Universe")
        AB = JClass("java.util.concurrent.atomic.AtomicBoolean")
        HLB, HL = JClass("com.hypixel.hytale.logger.backend.HytaleLoggerBackend"), JClass("com.hypixel.hytale.logger.HytaleLogger")
        RECS = JClass("java.util.concurrent.CopyOnWriteArrayList")()
        HLB.subscribe(RECS)

        def logs():
            out_ = []
            for i in range(int(RECS.size())):
                r = RECS.get(i)
                try:
                    out_.append("%s %s" % (r.getLevel(), r.getMessage()))
                except Exception:
                    out_.append(str(r))
            return out_

        def jc(k, n):
            return JClass(PKG + n, loader=L[k])
        for k in ("new", "prev"):
            jc(k, "WgLog").LOG = HL.get("SkyyWorldGenHarness" + k)
        Isl, Gen = jc("new", "WgZ2Isles"), jc("new", "WgZ2Gen")
        Wx, Home, Rdy, SCmd = jc("new", "WgWeather"), jc("new", "WgSpawnHome"), jc("new", "WgSpawnReady"), jc("new", "WgSpawnCmd")
        Cfg, Cmds, Open, Zn, Hk, Here = (jc("new", "WgCfg"), jc("new", "WgCmds"), jc("new", "WgOpen"), jc("new", "WgZones"), jc("new", "WgHooks"),
                                         jc("new", "WgHereTask"))
        Chk, Lg = jc("new", "WgCheck"), jc("new", "WgLog")

        # ================================================================================ W: the weather guard
        WRES = JClass("com.hypixel.hytale.builtin.weather.resources.WeatherResource")
        MINV = -2147483648
        wr = WRES()
        m_ = wr.getEnvironmentWeather()
        before = [int(m_.defaultReturnValue()), int(wr.getWeatherIndexForEnvironment(77))]
        n1 = int(Wx.fixMap(m_, 12, "skywynn_zones2"))
        after = [int(m_.defaultReturnValue()), int(wr.getWeatherIndexForEnvironment(77)), int(wr.getEffectiveWeatherIndex(77))]
        n2 = int(Wx.fixMap(m_, 12, "skywynn_zones2"))
        m_.put(JInt(1), JInt(0))
        n3 = int(Wx.fixMap(m_, 13, "skywynn_zones2"))
        envn = 0
        try:
            envn = int(JClass("com.hypixel.hytale.server.core.asset.type.environment.config.Environment").getAssetMap().getAssetMap().size())
        except Exception as e_:
            envn = "error " + str(e_)[:100]
        E["w1"] = dict(before=before, n1=n1, after=after, n2=n2, n3=n3, envs=envn, nullmap=int(Wx.fixMap(None, 0, "x")),
                       valid=[bool(Wx.validWeather(v)) for v in (0, MINV, -5, 999999)], fc=int(Wx.forecastOf(None, 3, 4)),
                       defaults=int(Wx.DEFAULTS.get()))
        # ================================================================================ worlds + players (stand-ins)
        WN = [str(x) for x in Zn.WORLDS]
        uni = UniC.get()
        byname = jf(UniC.class_, "worlds").get(uni)

        def world(name, gen=None):
            w, wu, cfg = N["mkworld"](name)
            jf(WLDc.class_, "alive").set(w, AB(True))
            byname.put(name.lower(), w)
            if gen is not None:
                jf(WCFGc.class_, "worldGenProvider").set(cfg, gen)
            return w, wu, cfg
        HUB, HUBU, HUBC = world("harness_main")
        ZW, ZWU, ZWC = world(WN[3], U.allocateInstance(jc("new", "WgZ2Provider").class_))
        OW, OWU, OWC = world(WN[2], U.allocateInstance(jc("new", "WgZoneProvider").class_))
        ISL, ISLU, ISLC = world("skyy-island-harness")
        N["UniH"].DEF = HUB
        HUBC.setSpawnProvider(GSP(TRF(0.5, 120.0, 0.5, 0.0, 0.0, 0.0)))
        Lz = Isl.layout(FakeMap(), FlatH(125), 0.5, 0.5, 777, JArray(JInt)([6, 3, 3, 3, 3]))
        genA = U.allocateInstance(Gen.class_)
        genA.lay = Lz
        genA.laid = True
        genA.lseed = 0
        CSc = JClass("com.hypixel.hytale.server.core.universe.world.storage.ChunkStore")
        cs = U.allocateInstance(CSc.class_)
        jf(CSc.class_, "generatorLock").set(cs, JClass("java.util.concurrent.locks.StampedLock")())
        jf(CSc.class_, "generator").set(cs, genA)
        jf(WLDc.class_, "chunkStore").set(ZW, cs)
        Isl.REGISTERED = True
        jc("new", "WgZoneIsles").REGISTERED = True
        for i in range(4):
            Chk.OK[i] = True
        U1 = UUID.fromString("00000000-0000-0000-0000-0000000071e1")
        TCc = JClass("com.hypixel.hytale.server.core.modules.entity.component.TransformComponent")
        CT = N["CT"]

        def on(w, wu, x=0.5, y=130.0, z=0.5, yaw=0.0):
            P = N["player"](U1, w, wu)
            t = TRF(x, y, z, 0.0, float(yaw), 0.0)
            P.st.row(P.ref).put(CT["tc"], TCc(t.getPosition(), t.getRotation()))
            return P

        def tp(P):
            return N["tp_of"](P)
        # W4: fix() on a stand-in world (no entity store) + tick() over the loaded worlds
        try:
            fixw = int(Wx.fix(ZW))
        except Exception as e_:
            fixw = "threw " + str(e_)[:120]
        for w_ in (HUB, ZW, OW, ISL):
            N["run_world"](w_)
        nt = int(Wx.tick())
        queued = [0 if w_.tasks is None else int(w_.tasks.size()) for w_ in (HUB, ZW, OW, ISL)]
        errs = []
        for w_ in (ZW, OW):
            try:
                N["run_world"](w_)
            except Exception as e_:
                errs.append(str(e_)[:120])
        Wx.start()
        started = Wx.TASK is not None
        Wx.stop()
        E["w4"] = dict(fix=fixw, tick=nt, queued=queued, errs=errs, started=started, stopped=Wx.TASK is None)
        # ================================================================================ S1-S3: pure parts + config
        E["s1"] = [int(Home.loginDecide(on_, d_, i_, s_)) for on_, d_, i_, s_ in
                   ((False, True, -1, 0), (True, False, -1, 0), (True, True, -1, 0), (True, True, 1, 0), (True, True, 0, 0), (True, True, 0, 1),
                    (True, True, 1, 1), (True, True, 0, 2), (True, True, 1, 2))]
        E["s2"] = [bool(Home.plain(v)) for v in ("spawn", "/spawn", "spawn 2", "  spawn  ", None, "spawn Bob", "", "/spawn  3")]
        Props = JClass("java.util.Properties")

        def apply(txt):
            p_ = Props()
            p_.load(JClass("java.io.StringReader")(txt))
            Cfg.apply(p_)
            return [bool(Cfg.SPAWN_ON), str(Cfg.ZSPAWN), str(Cfg.spawnText())[:60]]
        RECS.clear()
        E["s3"] = dict(
            apply=[apply(""), apply("zones.serverSpawn=false\nzones.spawnPoint=10.5 140 -20.5 90\n"), apply("zones.serverSpawn=true\nzones.spawnPoint=1 999 2\n"),
                   apply("zones.spawnPoint= 3.5 141 4.5 \n")],
            warn=[x for x in logs() if "zones.spawnPoint" in x][:2],
            check=[None if Cfg.spawnCheck(Cfg.parseLanding(v)) is None else str(Cfg.spawnCheck(Cfg.parseLanding(v)))[:40]
                   for v in ("1 100 2", "1 100 2 400", "40000 100 2", "a b c", "1 0 2")],
            hook=[None if Hk.checkSpawn("zones.spawnPoint", v) is None else str(Hk.checkSpawn("zones.spawnPoint", v))[:30] for v in ("", "  ", "1 100 2 45", "x")],
            parse=[None if Cfg.parseSpawn(v) is None else [float(x) for x in Cfg.parseSpawn(v)] for v in ("", "1 100 2", "1 999 2", None)],
            texts=[str(Cfg.spawnText())])
        # ================================================================================ S4: /zone setlanding in the zone world
        # cfgSet goes through the config kit (CfgFn.cmdSet, PermissionsModule.hasPermission): U1 holds skyyworldgen.admin (as /zone's
        # own node); a scratch data folder for the kit
        from jpype import JImplements, JOverride
        PM = JClass("com.hypixel.hytale.server.core.permissions.PermissionsModule")
        HashSet, ArrayList, HashMap = JClass("java.util.HashSet"), JClass("java.util.ArrayList"), JClass("java.util.HashMap")

        def jset(*xs):
            s_ = HashSet()
            for x in xs:
                s_.add(x)
            return s_

        @JImplements("com.hypixel.hytale.server.core.permissions.provider.PermissionProvider")
        class Prov:
            @JOverride
            def getName(self): return "wg071-test"
            @JOverride
            def getUserPermissions(self, u): return jset("skyyworldgen.admin") if str(u) == "00000000-0000-0000-0000-0000000071e1" else HashSet()
            @JOverride
            def getGroupsForUser(self, u): return jset("hytale:Adventurer")
            @JOverride
            def getGroupPermissions(self, g): return HashSet()
            @JOverride
            def getEffectiveGroupPermissions(self, g): return HashSet()
            @JOverride
            def getGroupParent(self, g): return None
            @JOverride
            def getAllRegisteredGroups(self): return jset("hytale:Adventurer")
            @JOverride
            def getUsersWithPermission(self, n): return HashSet()
            @JOverride
            def removeUserPermissionFromAll(self, n): return HashSet()
            @JOverride
            def addUserPermissions(self, *a): return None
            @JOverride
            def removeUserPermissions(self, *a): return None
            @JOverride
            def addUserToGroup(self, *a): return None
            @JOverride
            def addGroupPermissions(self, *a): return None
            @JOverride
            def removeGroupPermissions(self, *a): return None
            @JOverride
            def removeUserFromGroup(self, *a): return None
            @JOverride
            def setUserGroup(self, *a): return None
        pm = U.allocateInstance(PM.class_)
        provs = ArrayList()
        provs.add(Prov())
        jf(PM.class_, "providers").set(pm, provs)
        jf(PM.class_, "virtualGroups").set(pm, HashMap())
        jf(PM.class_, "instance").set(None, pm)
        kit_home = os.path.join(SCRATCH, "kit", "mods", "Skyy_SkyyWorldGen")
        os.makedirs(kit_home, exist_ok=True)
        Cfg.DIR = Paths.get(kit_home)
        Cfg.FILE = Paths.get(os.path.join(kit_home, "config.properties"))
        jc("new", "WgStore").FILE = Paths.get(os.path.join(kit_home, "worlds.properties"))
        Cfg.load()
        Pub = jc("new", "CfgPub")
        Pub.start(Paths.get(os.path.dirname(kit_home)), None)
        Cfg.NEW06 = True
        Cfg.ON = True
        Cfg.SPAWN_ON = True
        Cfg.ZSPAWN = ""
        m1 = JArray(jpype.JDouble)(1)
        nm = int(Lz.nMain)
        z1x, z1z = float(Lz.lx[0]), float(Lz.lz[0])
        z2x, z2z = float(Lz.lx[1]), float(Lz.lz[1])
        mem = [int(Isl.member(Lz, z1x, z1z, m1)), int(Isl.member(Lz, z2x, z2z, m1)), int(Isl.member(Lz, 9000.0, 9000.0, m1))]
        P = on(ZW, ZWU, z1x, 131.0, z1z, 1.5708)
        r_ok = str(Here.setHere(P.st, P.ref, P.pr, ZW))
        Pub.flush()
        time.sleep(0.5)
        Pub.flush()
        filetxt = open(os.path.join(kit_home, "config.properties"), encoding="latin-1").read() if os.path.isfile(os.path.join(kit_home, "config.properties")) else ""
        sp_line = [ln for ln in filetxt.splitlines() if ln.startswith("zones.spawnPoint=")]
        z_after = str(Cfg.ZSPAWN)
        P = on(ZW, ZWU, z2x, 131.0, z2z)
        r_z2 = str(Here.setHere(P.st, P.ref, P.pr, ZW))
        P = on(ZW, ZWU, 9000.0, 131.0, 9000.0)
        r_void = str(Here.setHere(P.st, P.ref, P.pr, ZW))
        genA.laid = False
        P = on(ZW, ZWU, z1x, 131.0, z1z)
        r_nolay = str(Here.setHere(P.st, P.ref, P.pr, ZW))
        genA.laid = True
        P = on(OW, OWU)
        r_old6 = str(Here.setHere(P.st, P.ref, P.pr, OW))
        Cfg.SPAWN_ON = False
        saved = str(Cfg.ZSPAWN)
        P = on(ZW, ZWU, z1x + 2.0, 131.0, z1z)
        r_off = str(Here.setHere(P.st, P.ref, P.pr, ZW))
        Cfg.SPAWN_ON = True
        E["s4"] = dict(mem=mem, nm=nm, z1=[z1x, z1z], ok=r_ok, file=sp_line, zs=z_after, z2=r_z2, void=r_void, nolay=r_nolay, old6=r_old6, off=r_off,
                       zs_off=str(Cfg.ZSPAWN), before_off=saved)
        # ================================================================================ S5: WgSpawnHome.send / /zone 1
        Cfg.ZSPAWN = "%s 131 %s 90" % (z1x, z1z)
        landing = [round(z1x, 2), 131.0, round(z1z, 2)]
        RECS.clear()
        res = {}
        Lg.ONCE.clear()
        Cfg.ZSPAWN = ""
        P = on(HUB, HUBU)
        res["none"] = [bool(Home.send(P.st, P.ref, P.pr, HUB, "the harness")), tp(P)]
        P = on(HUB, HUBU)
        res["none2"] = [bool(Home.send(P.st, P.ref, P.pr, HUB, "the harness")), tp(P)]
        res["warn_none"] = len([x for x in logs() if "no Zone 1 landing is set yet" in x])
        Cfg.ZSPAWN = "%s 131 %s 90" % (z1x, z1z)
        Cfg.SPAWN_ON = False
        P = on(HUB, HUBU)
        res["off"] = [bool(Home.send(P.st, P.ref, P.pr, HUB, "x")), tp(P)]
        Cfg.SPAWN_ON = True
        Cfg.NEW06 = False
        P = on(HUB, HUBU)
        res["zoff"] = [bool(Home.send(P.st, P.ref, P.pr, HUB, "x")), tp(P), len([x for x in logs() if "switched off" in x])]
        Cfg.NEW06 = True
        P = on(ZW, ZWU, 100.0, 140.0, 100.0)
        s0 = int(Home.SENT.get())
        res["here"] = [bool(Home.send(P.st, P.ref, P.pr, ZW, "x")), tp(P), N["chat"](P)[-80:], int(Home.SENT.get()) - s0]
        # from the default world: decide 1 -> the engine's loading-instance trip (InstancesPlugin.teleportPlayerToLoadingInstance - its
        # plugin is not running in the stand-ins, so the call itself throws there; send() catches it -> vanilla + WARN). Record where.
        P = on(HUB, HUBU)
        fh = None
        try:
            Home.travel(P.st, P.ref, P.pr, HUB, Cfg.parseSpawn(Cfg.ZSPAWN), "=[Zone] harness trip")
        except Exception as e_:
            try:
                fh = [str(f_) for f_ in e_.getStackTrace()[:3]]
            except Exception:
                fh = [repr(e_)]
        res["from_hub"] = [int(Open.decide(3, HUB)), fh, N["chat"](P)[-40:]]
        Lg.ONCE.clear()
        RECS.clear()
        P = on(HUB, HUBU)
        res["from_hub_send"] = [bool(Home.send(P.st, P.ref, P.pr, HUB, "x")), N["chat"](P)[-60:], [x for x in logs() if "could not send" in x][:1]]
        Arr = jc("new", "WgZoneArrive")
        Arr.HOPS.put(str(U1), JArray(jpype.JLong)([3, int(JClass("java.lang.System").currentTimeMillis()) + 60000]))
        P = on(ZW, ZWU, 100.0, 140.0, 100.0)
        Cmds.goCmd(P.st, P.ref, P.pr, ZW, "1")
        res["zone1"] = [tp(P), int(Arr.HOPS.size())]
        Cfg.ZSPAWN = ""
        P = on(ZW, ZWU, 100.0, 140.0, 100.0)
        Cmds.goCmd(P.st, P.ref, P.pr, ZW, "1")
        t0 = genA.landingOf(0, 0)
        res["zone1_unset"] = [tp(P), None if t0 is None else [WN[3], round(float(t0.getPosition().x()), 2), round(float(t0.getPosition().y()), 2), round(float(t0.getPosition().z()), 2)]]
        Cfg.ZSPAWN = "%s 131 %s 90" % (z1x, z1z)
        Cfg.ZSPAWN = "%s 131 %s 0" % (float(Lz.lx[1]), float(Lz.lz[1]))      # typed on Zone 2
        Lg.ONCE.clear()
        RECS.clear()
        P = on(ZW, ZWU, 100.0, 140.0, 100.0)
        res["typed_z2"] = [int(Home.onZone1(Cfg.parseSpawn(Cfg.ZSPAWN))), bool(Home.send(P.st, P.ref, P.pr, ZW, "x")), tp(P),
                           [x for x in logs() if "not on the Zone 1 island" in x][:1]]
        P = on(ZW, ZWU, 100.0, 140.0, 100.0)
        Cmds.goCmd(P.st, P.ref, P.pr, ZW, "1")
        res["typed_z2_zone1"] = [tp(P), res["zone1_unset"][1]]
        Cfg.ZSPAWN = "9000 131 9000 0"
        res["typed_void"] = [int(Home.onZone1(Cfg.parseSpawn(Cfg.ZSPAWN))), bool(Home.send(P.st, P.ref, P.pr, ZW, "x"))]
        Cfg.ZSPAWN = "%s 131 %s 90" % (z1x, z1z)
        byname.remove(WN[3].lower())
        res["unloaded"] = int(Home.onZone1(Cfg.parseSpawn(Cfg.ZSPAWN)))
        P = on(HUB, HUBU)
        RECS.clear()
        Lg.ONCE.clear()
        try:
            d4 = int(Open.decide(3, HUB))
        except Exception as e_:
            d4 = "error " + str(e_)[:100]
        res["unmade"] = [d4, bool(Home.send(P.st, P.ref, P.pr, HUB, "the harness")), tp(P), [x for x in logs() if "could not send" in x][:1]]
        byname.put(WN[3].lower(), ZW)
        res["lines"] = [str(x) for x in Cmds.listLines()][-2:]
        res["landing"] = landing
        E["s5"] = res
        # ================================================================================ S6: the login routing (real scheduler, world queues)
        PREc = JClass("com.hypixel.hytale.server.core.event.events.player.PlayerReadyEvent")
        PDEc = JClass("com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent")
        PLYc = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
        PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
        Home.FIRST_MS = 300
        Home.AGAIN_MS = 500
        Home.LAST_MS = 500
        props = JClass("java.lang.System").getProperties()
        bridge = JClass("java.util.concurrent.ConcurrentHashMap")()
        props.put("skyy.bridge", bridge)

        def ready(P_):
            ply = U.allocateInstance(PLYc.class_)
            jf(PLYc.class_, "playerRef").set(ply, P_.pr)
            return PREc(P_.ref, ply, 1)

        def valid(P_):
            # PlayerRef.isValid() reads the entity ref: the stand-in Ref needs a valid flag
            try:
                jf(JClass("com.hypixel.hytale.component.Ref").class_, "index").setInt(P_.ref, 7)
            except Exception:
                pass
            return bool(P_.pr.isValid())

        def login(w, wu, wait):
            P_ = on(w, wu)
            vv = valid(P_)
            Rdy().accept(ready(P_))
            t_end = time.time() + wait
            ran = 0
            while time.time() < t_end:
                time.sleep(0.1)
                ran += N["run_world"](w)
            ran += N["run_world"](w)
            return P_, vv, ran
        lg_ = {}
        Home.SEEN.clear()
        P, vv, ran = login(HUB, HUBU, 1.2)
        lg_["no_islands"] = [vv, ran, "server spawn" in N["chat"](P), tp(P)]
        Rdy().accept(ready(P))
        time.sleep(0.6)
        lg_["second_ready"] = [N["run_world"](HUB), int(Home.SEEN.size())]
        Rdy().accept(PDEc(P.pr))
        lg_["disconnect"] = int(Home.SEEN.size())
        bridge.put("island:shardguard", "1")
        bridge.put("island:" + str(U1), "skyy-island-harness")
        P, vv, ran = login(HUB, HUBU, 1.5)
        lg_["has_island"] = [ran, "server spawn" in N["chat"](P)]
        Rdy().accept(PDEc(P.pr))
        bridge.remove("island:" + str(U1))
        r0 = int(Home.ROUTED.get())
        P, vv, ran = login(HUB, HUBU, 0.6)
        mid = "server spawn" in N["chat"](P)
        t_end = time.time() + 1.6
        while time.time() < t_end:
            time.sleep(0.1)
            ran += N["run_world"](HUB)
        lg_["no_island_yet"] = [mid, ran, "server spawn" in N["chat"](P)]
        Rdy().accept(PDEc(P.pr))
        P, vv, ran = login(HUB, HUBU, 0.6)
        bridge.put("island:" + str(U1), "skyy-island-harness")        # a fresh /island between the looks
        t_end = time.time() + 1.6
        while time.time() < t_end:
            time.sleep(0.1)
            ran += N["run_world"](HUB)
        lg_["fresh_island"] = [ran, "server spawn" in N["chat"](P)]
        bridge.remove("island:" + str(U1))
        Rdy().accept(PDEc(P.pr))
        P, vv, ran = login(ISL, ISLU, 1.5)
        lg_["other_world"] = [ran, "server spawn" in N["chat"](P), tp(P)]
        Rdy().accept(PDEc(P.pr))
        Cfg.SPAWN_ON = False
        P, vv, ran = login(HUB, HUBU, 1.0)
        lg_["switch_off"] = [ran, "server spawn" in N["chat"](P)]
        Rdy().accept(PDEc(P.pr))
        Cfg.SPAWN_ON = True
        bridge.clear()
        E["s6"] = lg_
        # ================================================================================ S7: /spawn = WgSpawnCmd
        sc = {}
        cmd = SCmd()
        ACc = JClass("com.hypixel.hytale.server.core.command.system.AbstractCommand")
        fG = jf(ACc.class_, "permissionGroups")
        fV = jf(ACc.class_, "variantCommands")

        def groups(c):
            g = fG.get(c)
            return None if g is None else [str(x) for x in g]
        subs = cmd.getSubCommands()
        sc["name"] = str(cmd.getName())
        sc["super"] = str(cmd.getClass().getSuperclass().getName())
        sc["top"] = groups(cmd)
        sc["subs"] = sorted([str(k), groups(subs.get(k))] for k in subs.keySet())
        vm = fV.get(cmd)
        sc["variants"] = [] if vm is None else [groups(vm.get(k)) for k in vm.keySet()]
        sc["nodes"] = int(SCmd.NODES)
        sc["perm"] = [None if cmd.getPermission() is None else str(cmd.getPermission()), bool(cmd.hasPermission(None))]
        sc["var_perm"] = [None if vm is None else [str(vm.get(k).getPermission()) for k in vm.keySet()]]
        sc["recursive_adv"] = None
        try:
            mrec = cmd.getPermissionGroupsRecursive()
            sc["recursive_adv"] = None if mrec.get("hytale:Adventurer") is None else int(mrec.get("hytale:Adventurer").size())
            sc["recursive_keys"] = sorted(str(k) for k in mrec.keySet())
        except Exception as e_:
            sc["recursive_err"] = str(e_)[:120]
        CTXc = JClass("com.hypixel.hytale.server.core.command.system.CommandContext")
        exm = None
        for mm in SCmd.class_.getDeclaredMethods():
            if str(mm.getName()) == "execute":
                exm = mm
        exm.setAccessible(True)
        ObjArr = JArray(JClass("java.lang.Object"))

        U2 = UUID.fromString("00000000-0000-0000-0000-0000000072e2")      # 0.7.2: a player WITHOUT skyyworldgen.admin

        def run_spawn(line, w, wu, uid=None):
            if uid is None:
                P_ = on(w, wu, 50.0, 140.0, 50.0)
            else:
                P_ = N["player"](uid, w, wu)
                t_ = TRF(50.0, 140.0, 50.0, 0.0, 0.0, 0.0)
                P_.st.row(P_.ref).put(CT["tc"], TCc(t_.getPosition(), t_.getRotation()))
            ctx = CTXc(cmd, None, line)
            try:
                exm.invoke(cmd, ObjArr([ctx, P_.st, P_.ref, P_.pr, w]))
                err = None
            except Exception as e_:
                c_ = e_
                try:
                    c_ = e_.getCause() or e_
                except Exception:
                    pass
                st_ = ""
                try:
                    st_ = " ".join(str(f_) for f_ in c_.getStackTrace()[:6])
                except Exception:
                    pass
                err = (str(c_.getClass().getName()) if hasattr(c_, "getClass") else repr(c_)) + " @ " + st_[:400]
            return [tp(P_), N["chat"](P_)[-70:], err]
        sc["plain_hub"] = run_spawn("spawn", HUB, HUBU)
        sc["plain_zone"] = run_spawn("/spawn", ZW, ZWU)
        sc["index"] = run_spawn("spawn 2", ZW, ZWU)
        Cfg.SPAWN_ON = False
        sc["off"] = run_spawn("spawn", ZW, ZWU)
        sc["n_off"] = run_spawn("spawn", ZW, ZWU, U2)
        Cfg.SPAWN_ON = True
        sc["admin"] = [bool(Home.admin(on(ZW, ZWU).pr)), bool(Home.admin(N["player"](U2, ZW, ZWU).pr)), bool(Home.admin(None))]
        sc["n_plain_zone"] = run_spawn("/spawn", ZW, ZWU, U2)
        sc["n_index"] = run_spawn("spawn 2", ZW, ZWU, U2)
        sc["n_plain_hub"] = run_spawn("spawn", HUB, HUBU, U2)
        zs_ = str(Cfg.ZSPAWN)
        Cfg.ZSPAWN = ""
        sc["n_none"] = run_spawn("spawn", ISL, ISLU, U2)
        sc["a_none"] = run_spawn("spawn", ISL, ISLU)
        Cfg.ZSPAWN = zs_
        E["s7"] = sc
        Pub.shutdown()
        # ================================================================================ ST: two starts on a COPY of the live data
        home = os.path.join(SCRATCH, "st", "mods", "Skyy_SkyyWorldGen")
        if os.path.isdir(LIVE):
            shutil.copytree(LIVE, home)
        else:
            os.makedirs(home)
        Store = jc("new", "WgStore")
        starts = []
        for n_ in range(2):
            b0 = snap(home)
            Cfg.DIR = Paths.get(home)
            Cfg.FILE = Paths.get(os.path.join(home, "config.properties"))
            Store.FILE = Paths.get(os.path.join(home, "worlds.properties"))
            Cfg.load()
            Store.read()
            Pub.start(Paths.get(os.path.dirname(home)), None)
            Pub.flush()
            time.sleep(0.4)
            Pub.flush()
            made = Store.createdText(Zn.WORLDS[3])
            Pub.shutdown()
            a0 = snap(home)
            starts.append([sorted(k for k in set(b0) | set(a0) if b0.get(k) != a0.get(k)), None if made is None else str(made),
                           bool(Cfg.SPAWN_ON), str(Cfg.ZSPAWN), str(Cfg.LOADED)[-200:]])
        E["st"] = [starts, len(snap(home)), os.path.isdir(LIVE)]
        R["E"] = E
    except Exception:
        import traceback
        R["error"] = traceback.format_exc()[-4000:]
        R["E"] = E
    json.dump(R, open(out, "w"), indent=1, default=str)
    os._exit(0)


def check_e(E):
    w = E["w1"]
    print("W. weather map: before %s -> fixMap %d -> after %s, again %d, filled map %d, env assets %s" % (w["before"], w["n1"], w["after"], w["n2"], w["n3"], w["envs"]))
    check(w["before"] == [-2147483648, -2147483648], "W1: a fresh vanilla WeatherResource answers MIN_VALUE for an unknown environment (the NPE input): %s" % w["before"])
    check(w["n1"] == 1 and w["after"] == [0, 0, 0], "W1: after fixMap vanilla's own getWeatherIndexForEnvironment / getEffectiveWeatherIndex answer 0 = 'no weather' (SensorWeather: no match, no NPE): %s" % w["after"])
    check(w["n2"] == 0, "W1: fixMap is idempotent (second run changes nothing): %s" % w["n2"])
    check(isinstance(w["n3"], int) and w["n3"] >= 0, "W1: a filled map + the (offline, empty) environment asset map: no error: %s" % w["n3"])
    check(w["nullmap"] == -1 and w["valid"] == [True, False, False, False] and w["fc"] == 0, "W1: no map -> -1; validWeather 0 yes / MIN / -5 / unknown no; forecastOf(null) = 0: %s %s %s" % (w["nullmap"], w["valid"], w["fc"]))
    w4 = E["w4"]
    print("W4. fix(stand-in world) %s, tick %s, queued %s, errs %s" % (w4["fix"], w4["tick"], w4["queued"], w4["errs"]))
    check(w4["fix"] == -1, "W4: fix() on a world without an entity store = -1, no throw: %s" % w4["fix"])
    check(w4["tick"] == 2 and w4["queued"] == [0, 1, 1, 0] and not w4["errs"], "W4: tick() hands one task to each loaded SkyyWorldGen world (zones2, zones), none to the default / an island world, the tasks run clean: %s %s %s" % (w4["tick"], w4["queued"], w4["errs"]))
    check(w4["started"] and w4["stopped"], "W4: the 5 s guard starts and stops")
    check(E["s1"] == [0, 0, 1, 0, 2, 2, 0, 1, 0], "S1: login decision (off / not default / no Islands -> go / island -> stay / none at 2 s and 6 s -> ask again / none at 12 s -> go / island later -> stay): %s" % E["s1"])
    check(E["s2"] == [True, True, False, True, True, False, True, False], "S2: plain /spawn parsing: %s" % E["s2"])
    s3 = E["s3"]
    print("S3. %s" % json.dumps(s3)[:900])
    a = s3["apply"]
    check(a[0][:2] == [True, ""] and a[1][:2] == [False, "10.5 140 -20.5 90"] and a[2][:2] == [True, ""] and a[3][:2] == [True, "3.5 141 4.5"],
          "S3: WgCfg.apply: defaults on + unset; off + a landing; a bad Y refused -> unset; trimmed: %s" % a)
    check(len(s3["warn"]) == 1, "S3: the refused hand edit is WARNed: %s" % s3["warn"])
    check(s3["check"][0] is None and all(x is not None for x in s3["check"][1:]), "S3: spawnCheck: ok / yaw 400 / x 40000 / letters / y 0: %s" % s3["check"])
    check(s3["hook"][:3] == [None, None, None] and s3["hook"][3] is not None, "S3: check hook: empty = fine (unset), a point = fine, junk refused: %s" % s3["hook"])
    check(s3["parse"][0] is None and s3["parse"][1] == [1.0, 100.0, 2.0, 0.0] and s3["parse"][2] is None and s3["parse"][3] is None, "S3: parseSpawn: %s" % s3["parse"])
    s4 = E["s4"]
    print("S4. setlanding: ok %r | z2 %r | void %r | nolay %r | old6 %r | off %r | file %s" % (s4["ok"][:90], s4["z2"][:90], s4["void"][:60], s4["nolay"][:60], s4["old6"][:60], s4["off"][-90:], s4["file"]))
    check(s4["mem"][0] == 0 and s4["mem"][1] == 1 and s4["mem"][2] < 0, "S4: the synthetic layout: Zone 1's landing spot is on island 0, Zone 2's on island 1: %s" % s4["mem"])
    exp = "%s 132 %s 90" % (fmt(math.floor(s4["z1"][0]) + 0.5), fmt(math.floor(s4["z1"][1]) + 0.5))
    check(not s4["ok"].startswith("-") and s4["zs"] == exp, "S4: /zone setlanding on Zone 1 -> zones.spawnPoint = the block centre, y + 1, yaw 90 (%s): %r -> %r" % (exp, s4["ok"][:120], s4["zs"]))
    check(s4["file"] == ["zones.spawnPoint=" + exp], "S4: saved in config.properties through the kit: %s" % s4["file"])
    check(s4["z2"].startswith("-") and "Zone 2" in s4["z2"], "S4: on Zone 2 refused (names it): %r" % s4["z2"])
    check(s4["void"].startswith("-") and "void" in s4["void"], "S4: over the void refused: %r" % s4["void"])
    check(s4["nolay"].startswith("-") and "still being picked" in s4["nolay"], "S4: no layout yet refused: %r" % s4["nolay"])
    check(s4["old6"].startswith("-") and "0.6" in s4["old6"], "S4: the 0.6 world still has no landing: %r" % s4["old6"])
    check("OFF" in s4["off"] and s4["zs_off"] != s4["before_off"], "S4: with the switch off it still saves + says the switch is off: %r" % s4["off"][-120:])
    s5 = E["s5"]
    print("S5. %s" % json.dumps(s5)[:1500])
    L = s5["landing"]
    check(s5["none"] == [False, None] and s5["none2"] == [False, None] and s5["warn_none"] == 1, "S5: no landing -> vanilla (false, no teleport) + exactly ONE WARN: %s %s %s" % (s5["none"], s5["none2"], s5["warn_none"]))
    check(s5["off"] == [False, None], "S5: switch off -> vanilla: %s" % s5["off"])
    check(s5["zoff"][:2] == [False, None] and s5["zoff"][2] == 1, "S5: zone world off -> vanilla + one WARN: %s" % s5["zoff"])
    check(s5["here"][0] is True and s5["here"][1] == [WN3, L[0], L[1], L[2]] and s5["here"][3] == 1, "S5: in the zone world -> Teleport to the landing: %s" % s5["here"])
    check(s5["from_hub"][0] == 1 and s5["from_hub"][1] and any("InstancesPlugin.teleportPlayerToLoadingInstance" in f_ or "InstanceEntityConfig" in f_ for f_ in s5["from_hub"][1])
          and "harness trip" in s5["from_hub"][2], "S5: from the default world (decide 1) -> told + up to the engine's loading-instance trip (InstancesPlugin is not running in the stand-ins): %s" % s5["from_hub"])
    check(s5["from_hub_send"][0] is False and len(s5["from_hub_send"][2]) == 1, "S5: send() never throws - an engine failure = vanilla + one WARN: %s" % s5["from_hub_send"])
    check(s5["zone1"][0] == [WN3, L[0], L[1], L[2]] and s5["zone1"][1] == 0, "S5: /zone 1 with a landing set -> the landing (a stale /zone 2-5 hop cleared): %s" % s5["zone1"])
    check(s5["zone1_unset"][0] is not None and s5["zone1_unset"][0] == s5["zone1_unset"][1], "S5: /zone 1 without a landing = 0.7's island spot (landingOf): %s" % s5["zone1_unset"])
    check(s5["typed_z2"][0] == 0 and s5["typed_z2"][1] is False and s5["typed_z2"][2] is None and len(s5["typed_z2"][3]) == 1,
          "S5: a typed landing on Zone 2 -> not sent (vanilla) + one WARN: %s" % s5["typed_z2"])
    check(s5["typed_z2_zone1"][0] == s5["typed_z2_zone1"][1], "S5: /zone 1 with an off-Zone-1 landing = the island's own spot: %s" % s5["typed_z2_zone1"])
    check(s5["typed_void"] == [0, False], "S5: a typed landing over the void -> not sent: %s" % s5["typed_void"])
    check(s5["unloaded"] == -1, "S5: zone world not loaded -> the landing cannot be checked (-1, not sent): %s" % s5["unloaded"])
    check(s5["unmade"][1] is False and s5["unmade"][2] is None and len(s5["unmade"][3]) == 1, "S5: zone world not loaded / never made (stand-in Universe has no world folder) -> vanilla + one WARN, no throw: %s" % s5["unmade"])
    check(any("Server spawn: ON = the Zone 1 landing" in x for x in s5["lines"]), "S5: /zone lists the server spawn: %s" % s5["lines"])
    s6 = E["s6"]
    print("S6. login routing %s" % json.dumps(s6))
    check(s6["no_islands"][0] and s6["no_islands"][1] >= 1 and s6["no_islands"][2] is True,
          "S6: first ready in the default world, no SkyyIslands -> the Zone 1 trip (real scheduler -> the world's queue -> told + the engine trip): %s" % s6["no_islands"])
    check(s6["second_ready"][0] == 0 and s6["second_ready"][1] == 1 and s6["disconnect"] == 0, "S6: a second ready routes nothing; a disconnect ends the session: %s %s" % (s6["second_ready"], s6["disconnect"]))
    check(s6["has_island"][1] is False, "S6: SkyyIslands lists an island -> stays (Islands routes): %s" % s6["has_island"])
    check(s6["no_island_yet"][0] is False and s6["no_island_yet"][1] >= 3 and s6["no_island_yet"][2] is True,
          "S6: SkyyIslands lists none yet -> nothing at the first look, the Zone 1 trip at the second (4 s later in game): %s" % s6["no_island_yet"])
    check(s6["fresh_island"][0] >= 2 and s6["fresh_island"][1] is False, "S6: an island made between the looks -> nothing sent: %s" % s6["fresh_island"])
    check(s6["other_world"][1] is False and s6["other_world"][2] is None, "S6: logged in on another world (an island) -> stays: %s" % s6["other_world"])
    check(s6["switch_off"][1] is False, "S6: switch off -> stays: %s" % s6["switch_off"])
    s7 = E["s7"]
    print("S7. /spawn %s" % json.dumps(s7)[:1600])
    check(s7["name"] == "spawn" and s7["super"].endswith("teleport.SpawnCommand"), "S7: /spawn = a subclass of vanilla's SpawnCommand: %s %s" % (s7["name"], s7["super"]))
    check(s7["top"] == [] and s7["variants"] == [[]] and s7["nodes"] == 2, "S7: groups cleared on /spawn + /spawn <player>: top %s variants %s nodes %s" % (s7["top"], s7["variants"], s7["nodes"]))
    check(s7["perm"] == [None, True] and s7["var_perm"] == [["hytale.command.spawn.other"]], "S7 (0.7.2): /spawn is OPEN (no node; hasPermission true for anyone), /spawn <player> keeps hytale.command.spawn.other: %s %s" % (s7["perm"], s7["var_perm"]))
    check(s7["subs"] == [["default", ["hytale:Admin"]], ["set", ["hytale:WorldEditor"]]], "S7: /spawn set (WorldEditor) + /spawn default (Admin) keep vanilla's groups: %s" % s7["subs"])
    check(s7.get("recursive_adv") in (None, 0), "S7: engine getPermissionGroupsRecursive gives hytale:Adventurer no node (open needs none): %s %s" % (s7.get("recursive_adv"), s7.get("recursive_keys")))
    NS = "No server spawn is set yet"
    check(s7["admin"] == [True, False, False], "S7 (0.7.2): WgSpawnHome.admin = skyyworldgen.admin (U1 yes, U2 no, null no): %s" % s7["admin"])
    check(s7["n_plain_zone"][0] == [WN3, L[0], L[1], L[2]] and s7["n_plain_zone"][2] is None, "S7 (0.7.2): a player's plain /spawn in the zone world -> the Zone 1 landing: %s" % s7["n_plain_zone"])
    check(s7["n_index"][0] == [WN3, L[0], L[1], L[2]] and s7["n_index"][2] is None, "S7 (0.7.2): a player's /spawn 2 -> the Zone 1 landing too (never vanilla's index spawn): %s" % s7["n_index"])
    check(s7["n_plain_hub"][2] is None and "server spawn" in s7["n_plain_hub"][1], "S7 (0.7.2): a player's /spawn in the default world -> told + the trip (stand-ins: the engine call fails -> NOT vanilla, no error): %s" % s7["n_plain_hub"])
    check(s7["n_off"][0] is None and s7["n_off"][2] is None and NS in s7["n_off"][1], "S7 (0.7.2): switch off, a player -> 'No server spawn is set yet', stays, vanilla never runs: %s" % s7["n_off"])
    check(s7["n_none"][0] is None and s7["n_none"][2] is None and NS in s7["n_none"][1], "S7 (0.7.2): no landing set, a player on an island -> 'No server spawn is set yet', stays: %s" % s7["n_none"])
    check(s7["a_none"][0] is None and s7["a_none"][2] is not None and "SpawnCommand" in s7["a_none"][2], "S7 (0.7.2): no landing set, an admin -> vanilla's execute (as 0.7.1): %s" % s7["a_none"])
    check(s7["plain_zone"][0] == [WN3, L[0], L[1], L[2]] and s7["plain_zone"][2] is None, "S7: plain /spawn in the zone world -> the Zone 1 landing: %s" % s7["plain_zone"])
    check(s7["plain_hub"][2] is None and "server spawn" in s7["plain_hub"][1], "S7: plain /spawn in the default world -> told + the engine trip (in the stand-ins that call fails -> vanilla /spawn, no error): %s" % s7["plain_hub"])
    check(s7["index"][0] is None and s7["index"][2] is not None and "SpawnCommand" in s7["index"][2], "S7: /spawn 2 -> vanilla's execute (reached, stand-ins lack its arguments): %s" % s7["index"])
    check(s7["off"][0] is None and s7["off"][2] is not None and "SpawnCommand" in s7["off"][2], "S7: switch off -> vanilla's execute: %s" % s7["off"])
    st = E["st"]
    print("ST. %s" % json.dumps(st)[:700])
    check(st[2], "ST: the live Skyy_SkyyWorldGen folder exists (copied into scratch): %s" % st[2])
    check(all(not s_[0] for s_ in st[0]), "ST: two starts on the copy change no file: %s" % [s_[0] for s_ in st[0]])
    check(all(s_[2] is True and s_[3] == "" for s_ in st[0]), "ST: the copy has no 0.7.1 keys -> defaults (on, no landing): %s" % [s_[2:4] for s_ in st[0]])
    check(all("server spawn ON, but no Zone 1 landing" in s_[4] for s_ in st[0]), "ST: LOADED names the server spawn state: %s" % st[0][0][4][-120:])


WN3 = "skywynn_zones2"


def fmt(v):
    r = round(float(v) * 100.0) / 100.0
    return str(int(r)) if r == int(r) else ("%s" % r)


# ================================================================= VP: one offline server start (tools/smoke_test.py)
def vp(env):
    if "--no-smoke" in sys.argv:
        NOTES.append("VP NOT RUN (--no-smoke)")
        return
    smoke = os.path.join(TOOLS, "dev", "scratch", "smoke")
    before = set(glob.glob(os.path.join(smoke, "*.log")))
    out_vp = os.path.join(SCRATCH, "vp.log")
    with open(out_vp, "wb") as lf:
        rc = subprocess.run([sys.executable, os.path.join(TOOLS, "smoke_test.py"), "--jar", os.path.relpath(JAR, ROOT), "--linger", "25", "--allow-pack-api"],
                            env=env, stdout=lf, stderr=subprocess.STDOUT, cwd=ROOT).returncode
    txt = open(out_vp, encoding="utf8", errors="replace").read()
    if rc == 2:
        NOTES.append("VP NOT RUN (smoke_test exit 2 - a server is running or setup failed): " + txt[-300:])
        return
    new = sorted(set(glob.glob(os.path.join(smoke, "*.log"))) - before)
    log = open(new[-1], encoding="utf8", errors="replace").read() if new else ""
    ready = [ln for ln in log.splitlines() if "[SkyyWorldGen] %s ready" % VERSION in ln]
    mine = [ln for ln in log.splitlines() if "/spawn = SkyyWorldGen's" in ln or "/spawn belongs to" in ln]
    sev = [ln for ln in log.splitlines() if ("SEVERE" in ln or "ERROR" in ln) and ("SkyyWorldGen" in ln or "com.skyy.worldgen" in ln)]
    wx = [ln for ln in log.splitlines() if "zone world weather" in ln]
    wnpe = [ln for ln in log.splitlines() if "Weather.getId()" in ln]
    print("VP. smoke exit %s; log %s; ready %d; /spawn %s; weather %s; SensorWeather NPE %d" % (rc, new[-1:] and os.path.basename(new[-1]), len(ready),
                                                                                                [m[-120:] for m in mine], [w_[-140:] for w_ in wx[:3]], len(wnpe)))
    check(rc == 0, "VP: smoke test PASS: %s" % txt[-400:])
    check(len(ready) == 1 and "SERVER SPAWN" in ready[0], "VP: one '[SkyyWorldGen] %s ready' line naming the server spawn: %s" % (VERSION, [r_[-200:] for r_ in ready]))
    check(len(mine) == 1 and "/spawn = SkyyWorldGen's" in mine[0], "VP: after every plugin's setup /spawn is SkyyWorldGen's: %s" % mine)
    check(not sev, "VP: no SEVERE / ERROR from SkyyWorldGen: %s" % sev[:3])
    check(not wnpe, "VP: no SensorWeather NPE in the boot log: %s" % wnpe[:2])
    NOTES.append("VP log kept: %s (pack: python tools/tidy_local.py --yes --scratch smoke)" % (new[-1] if new else "?"))


# ============================================================================================ parent
def main():
    if "--e" in sys.argv:
        return run_e(arg("--out"))
    for j in (JAR, PREV_JAR):
        if not os.path.isfile(j):
            sys.exit("no jar at %s - build it first" % j)
    sroot = os.path.realpath(os.path.join(TOOLS, "dev", "scratch"))
    if not os.path.realpath(SCRATCH).startswith(sroot + os.sep):
        sys.exit("--dir must be inside tools/dev/scratch/ (deleted afterwards): %s" % SCRATCH)
    if os.path.exists(SCRATCH) and os.listdir(SCRATCH):
        sys.exit("%s is not empty - pass an empty --dir" % SCRATCH)
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.makedirs(env["TEMP"], exist_ok=True)
    live_before = snap(LIVE)
    me = os.path.abspath(__file__)
    try:
        # ---- CC
        rules = [[r"worldgen_0_7_2_patch", "worldgen_0_7_1_patch"]]
        out_cc = os.path.join(SCRATCH, "cc.json")
        with open(out_cc + ".log", "wb") as lf:
            subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0, %r); import importlib.util as u; "
                            "s = u.spec_from_file_location('ts', %r); m = u.module_from_spec(s); sys.argv = ['x', '--dir', %r]; "
                            "s.loader.exec_module(m); m.SCRATCH = %r; m.run_cc(%r, %r, %r, %r)" % (
                                TOOLS, SKILLS_HARNESS, SCRATCH, SCRATCH, JAR, PREV_JAR, out_cc,
                                json.dumps({"versions": [VERSION, PREV_VERSION], "rules": rules}))],
                           env=env, stdout=lf, stderr=subprocess.STDOUT, cwd=SCRATCH)
        cc = json.load(open(out_cc)) if os.path.isfile(out_cc) else None
        if cc is None:
            print(open(out_cc + ".log", encoding="utf8", errors="replace").read()[-2000:])
        check(cc is not None, "CC: the compare child ran")
        if cc:
            cls_ = cc["classes"]
            check(sorted(cc["added"]) == NEW_CLASSES and cc["gone"] == [], "CC: + exactly %s, none gone: %s %s" % (NEW_CLASSES, cc["added"], cc["gone"]))
            struct_ = dict((c, sorted(x.split("(")[0] + (" (new)" if x.endswith("(new)") else "") for x in v["structural"])) for c, v in cls_.items() if v["structural"])
            const = dict((c, sorted(v["const_only"])) for c, v in cls_.items() if v["const_only"])
            fnew = dict((c, v["fields_new"]) for c, v in cls_.items() if v["fields_new"])
            fgone = dict((c, v["fields_gone"]) for c, v in cls_.items() if v["fields_gone"])
            print("CC. 0.7.1 -> 0.7.2 structural %s; constants only %s; fields new %s" % (struct_, const, fnew))
            frozen = [c for c in FROZEN if c in struct_ or c in const or c in fnew or c in fgone]
            check(not frozen, "CC: every generator class + WgOpen / spawn task / store / log / arrival hop / zone table UNCHANGED: %s" % frozen)
            check(not fgone and all(v["same_shape"] for v in cls_.values()), "CC: no field removed, same supers / interfaces: %s" % fgone)
            check(set(struct_) <= ALLOWED | set(c for c in cls_ if c.startswith("Cfg")), "CC: structural changes only in config / commands / "
                  "setlanding / hooks / plugin (+ the kit): %s" % sorted(struct_))
            check(set(const) <= ALLOWED | {"ZoneLandingCmd"} | set(c for c in cls_ if c.startswith("Cfg")), "CC: text-only changes only where expected: %s" % sorted(const))
        # ---- JT
        zj, zp = zipfile.ZipFile(JAR), zipfile.ZipFile(PREV_JAR)
        cn, cp_ = set(n for n in zj.namelist() if n.endswith(".class")), set(n for n in zp.namelist() if n.endswith(".class"))
        check(sorted(cn - cp_) == ["com/skyy/worldgen/%s.class" % c for c in NEW_CLASSES] and not (cp_ - cn), "JT: the same class files as 0.7.1: %s %s"
              % (sorted(cn - cp_), sorted(cp_ - cn)))
        nn = set(n for n in zj.namelist() if not n.endswith(".class"))
        np_ = set(n for n in zp.namelist() if not n.endswith(".class"))
        check(nn == np_, "JT: the same non-class entries: %s %s" % (sorted(nn - np_), sorted(np_ - nn)))
        norm = lambda b_: b_.replace(b"(SkyyWorldGen %s)" % VERSION.encode(), b"(SkyyWorldGen %s)" % PREV_VERSION.encode())
        diff = sorted(n for n in np_ if n != "manifest.json" and norm(zj.read(n)) != zp.read(n))
        check(not diff, "JT: every non-class entry byte-identical but the version in a template comment: %s" % diff[:4])
        man = json.loads(zj.read("manifest.json"))
        check(man.get("Version") == VERSION and "server spawn" in man.get("Description", ""), "JT: manifest %s: %s" % (man.get("Version"), man.get("Description", "")[-160:]))
        # ---- A + W + S + ST
        out_e = os.path.join(SCRATCH, "e.json")
        with open(out_e + ".log", "wb") as lf:
            subprocess.run([sys.executable, me, "--e", "--out", out_e, "--dir", SCRATCH, "--jar", JAR, "--prev", PREV_JAR],
                           env=env, stdout=lf, stderr=subprocess.STDOUT)
        r = json.load(open(out_e)) if os.path.isfile(out_e) else None
        if r is None or "error" in r:
            print(open(out_e + ".log", encoding="utf8", errors="replace").read()[-3000:])
        check(r is not None and "error" not in r, "E ran: %s" % (r or {}).get("error", "")[-3000:])
        if r:
            for tag, (n_, f_) in r["load"].items():
                check(not f_ and n_ >= 20, "A (%s): %d classes load, verify (-Xverify:all), initialise %s" % (tag, n_, f_[:3]))
        if r and "error" not in r:
            check_e(r["E"])
        elif r and r.get("E"):
            print("partial E:", json.dumps(r["E"])[:3000])
        # ---- VP
        try:
            vp(env)
        except Exception as e:
            check(False, "VP crashed: %s" % e)
        # ---- AA
        out_aa = os.path.join(SCRATCH, "aa.log")
        with open(out_aa, "wb") as lf:
            subprocess.run([sys.executable, os.path.join(TOOLS, "ci", "crosscheck.py"), "--jar", JAR, "--baseline"], env=env, stdout=lf,
                           stderr=subprocess.STDOUT, cwd=ROOT)
        aa = open(out_aa, encoding="utf8", errors="replace").read()
        mine = [ln for ln in aa.splitlines() if ln.startswith("FAIL") and "SkyyWorldGen" in ln]
        check("READY" in aa and not mine, "AA: crosscheck --jar 0.7.2 READY, no FAIL for SkyyWorldGen: %s" % (mine[:3] or aa[-300:]))
        bl = [ln.strip() for ln in aa.splitlines() if ln.strip().startswith(("+ ", "- ")) or "baseline SkyyWorldGen" in ln]
        print("AA. %s" % bl)
        plus = [ln for ln in bl if ln.startswith("+ ")]
        want = ["- /spawn top groups=[] perm=hytale.command.spawn.self", "+ /spawn top groups=[] perm=open"]
        check([" ".join(ln.split()) for ln in bl if ln.startswith(("+ ", "- "))] == want, "AA: the tree diff vs the baseline = /spawn's node -> open only: %s" % bl)
        after = snap(LIVE)
        chg = [k_ for k_ in sorted(set(live_before) | set(after)) if live_before.get(k_) != after.get(k_)]
        check(not chg, "the live Skyy_SkyyWorldGen folder is unchanged: %s" % chg[:5])
    finally:
        if "--keep" not in sys.argv:
            os.chdir(ROOT)
            shutil.rmtree(SCRATCH, ignore_errors=True)
    for n_ in NOTES:
        print("NOTE:", n_)
    print("SkyyWorldGen %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
