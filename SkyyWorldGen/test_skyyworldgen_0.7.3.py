"""SkyyWorldGen 0.7.3 - harness for ZONE ORES + ALLOYS (tools/worldgen_0_7_3_patch.py, round ores01, research/Zone-Ores-Alloys-Spec.md) =
the 0.7.2 harness (/SPAWN FOR PLAYERS - every S / W / ST check still runs unchanged: 0.7.3 changes no spawn code) with: CC / JT against
0.7.2 (no class added; only WgZ2Isles (ore table, live chances, ORE_NT, orep / oreText / ores), WgCfg (decProp, oreCfgText, apply) and
WgZones (ZONES2_TEXT) + the config kit change; the jar = 0.7.2's entries + exactly the metal assets), M (python, the jar's metal assets
against Assets.zip: 16 items = the spec ids = tools/tier_tags.py WG_IDS, each JSON = its vanilla source with ONLY the listed keys
changed, every referenced model / texture / icon / item exists in the jar or Assets.zip, the 4 Furnace + 5 SkyyAlloy recipes, the lang file
+ tier tags first, the PNGs = recolours of the vanilla pixels (same size, alpha kept, colour changed)), OV (EXECUTED in the child JVM: the
real WgZ2Isles.ores() on synthetic 32 x 32 chunks of stone / sandstone for every zone - each new ore only on its own island, Lead also in
sandstone, Chromium never; Onyxium / Mithril counts = 0.7.2's jar on the same chunks (bit-identical veins); orep() live; the Server Setup
rows through the config kit's console path (field + file line); WgCfg.apply clamps / keeps junk; the real CraftingRecipe codec decodes
the 5 alloy recipes + the 4 ingot recipes with no unknown key), AA's tree diff vs the baseline = none. 0.7.2 header follows.
--- 0.7.2 ---
SkyyWorldGen 0.7.2 - harness for /SPAWN FOR PLAYERS (tools/worldgen_0_7_2_patch.py, lean round small01) = the 0.7.1 harness
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
VERSION, PREV_VERSION = "0.7.3", "0.7.2"
PKG = "com.skyy.worldgen."
NEW_CLASSES = []
FROZEN = ["WgIsle", "WgIsleGen", "WgMaskFn", "WgMaskHop", "WgIsleProvider", "WgIsleSupplier", "WgSpawnTask", "WgDone", "WgApplyLanding",
          "WgReady", "WgStore", "WgLog", "WgZoneLayout", "WgZoneIsles", "WgZoneGen", "WgZoneFn", "WgZoneHop", "WgZoneProvider", "WgZoneSupplier",
          "WgZoneSampler", "WgZ2Fn", "WgZ2Gen", "WgZ2Hop", "WgZ2Layout", "WgZ2Provider", "WgZ2River", "WgZ2Supplier", "WgOpen",
          "WgZoneArrive", "WgCheck", "WgSpawnHome", "WgSpawnCmd", "WgSpawnReady", "WgWeather"]
ALLOWED = {"WgZ2Isles", "WgCfg", "WgCmds", "SkyyWorldGenPlugin"}   # 0.7.3: structural (+ the kit's Cfg* classes); WgCmds.infoLines + the plugin's
# ready line inline the changed static final texts (ZONES2_TEXT ...) - javac-style constant folding shows up as an instruction change
ALLOWED_CONST = {"WgZones", "SkyyWorldGenPlugin"}   # 0.7.3: text-only (ZONES2_TEXT; the manifest / ready texts)
METAL_IDS = sorted(["Ore_Lead_Sandstone_SkyWynn", "Ore_Lead_SkyWynn", "Ingredient_Bar_Lead_SkyWynn",
                    "Ore_Chromium_Shale_SkyWynn", "Ore_Chromium_SkyWynn", "Ingredient_Bar_Chromium_SkyWynn",
                    "Ore_Slag_Volcanic_SkyWynn", "Ore_Slag_SkyWynn", "Ingredient_Bar_Slag_SkyWynn",
                    "Ore_Titanium_Basalt_SkyWynn", "Ore_Titanium_SkyWynn", "Ingredient_Bar_Titanium_SkyWynn",
                    "Ingredient_Bar_Dusk_SkyWynn", "Ingredient_Bar_Azurvane_SkyWynn", "Ingredient_Bar_Cinder_SkyWynn",
                    "Ingredient_Bar_Lumen_SkyWynn", "Ingredient_Bar_Electrum_SkyWynn"])
# spec 2.3 / 3: metal -> (zone, partner, host word, host cobble, smelt s); alloy -> (A, B, s)
ZM = {"Lead": (2, "Thorium", "Sandstone", "Rock_Sandstone_Cobble", 18, "Ore_Thorium_Sandstone"),
      "Chromium": (3, "Cobalt", "Shale", "Rock_Shale_Cobble", 18, "Ore_Cobalt_Shale"),
      "Slag": (4, "Adamantite", "Volcanic", "Rock_Volcanic_Cobble", 20, "Ore_Adamantite_Magma"),
      "Titanium": (5, "Mithril", "Basalt", "Rock_Basalt_Cobble", 30, "Ore_Mithril_Stone")}
AL = {"Bronze": ("Ingredient_Bar_Copper", "Ingredient_Bar_Iron", 24, "Ingredient_Bar_Bronze"),
      "Dusk": ("Ingredient_Bar_Thorium", "Ingredient_Bar_Lead_SkyWynn", 36, "Ingredient_Bar_Dusk_SkyWynn"),
      "Azurvane": ("Ingredient_Bar_Cobalt", "Ingredient_Bar_Chromium_SkyWynn", 36, "Ingredient_Bar_Azurvane_SkyWynn"),
      "Cinder": ("Ingredient_Bar_Adamantite", "Ingredient_Bar_Slag_SkyWynn", 40, "Ingredient_Bar_Cinder_SkyWynn"),
      "Lumen": ("Ingredient_Bar_Mithril", "Ingredient_Bar_Titanium_SkyWynn", 60, "Ingredient_Bar_Lumen_SkyWynn"),
      "Electrum": ("Ingredient_Bar_Gold", "Ingredient_Bar_Silver", 14, "Ingredient_Bar_Electrum_SkyWynn")}


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "ores01", "wg")))
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
        # ================================================================================ OV (0.7.3): the zone ore veins EXECUTED
        ov = {}
        ov["names"] = [str(x) for x in Isl.ORE_NAMES]
        ov["mask"] = [int(x) for x in Isl.ORE_MASK]
        ov["live"] = [int(x) for x in Isl.ORE_LIVE]
        ov["hx"] = [int(x) for x in Isl.ORE_HX]
        ov["p0"] = [float(Isl.orep(t_)) for t_ in range(len(ov["names"]))]
        ov["any"] = int(Isl.ORE_ANY)
        ov["mr"] = [[str(Isl.MR_NAME[r_]), int(Isl.MR_ISL[r_]), str(Isl.MR_O1_NAMES[r_]), str(Isl.MR_O2_NAMES[r_]),
                     [str(x) for x in Isl.MR_SRC_NAMES[int(Isl.MR_SRC_AT[r_]):int(Isl.MR_SRC_AT[r_ + 1])]],
                     [str(x) for x in Isl.MR_HOST_NAMES[int(Isl.MR_HOST_AT[r_]):int(Isl.MR_HOST_AT[r_ + 1])]]] for r_ in range(int(Isl.MR_N))]
        FACT = ["B_THORIUM", "B_COBALT", "B_ADAMANTITE", "F_LEAD", "F_CHROMIUM", "F_SLAG", "F_MITHRIL5", "F_TITANIUM", "X_SILVER", "X_GOLD", "P_GOLD45"]
        ov["fact0"] = [float(getattr(Isl, f_)) for f_ in FACT]
        ov["mw0"] = [[round(float(Isl.mw(r_, o_)), 6) for o_ in range(3)] for r_ in range(int(Isl.MR_N))]
        # Server Setup through the kit's console path (CfgFn.cmdSetConsole = an in-game edit: check, field, file line)
        Fn = jc("new", "CfgFn")
        ov["set"] = [str(Fn.cmdSetConsole("ores.lead", "1.0")), str(Fn.cmdSetConsole("ores.thoriumBoost", "3")), str(Fn.cmdSetConsole("ores.gold45", "abc")),
                     str(Fn.cmdSetConsole("ores.cobaltBoost", "0.5"))]
        ov["after_set"] = [float(Isl.F_LEAD), float(Isl.B_THORIUM), float(Isl.P_GOLD45), round(float(Isl.mw(0, 1)), 6), float(Isl.B_COBALT)]
        Pub.flush()
        time.sleep(0.4)
        Pub.flush()
        try:
            ov["file"] = sorted(l_ for l_ in open(os.path.join(kit_home, "config.properties"), encoding="latin-1").read().splitlines() if l_.startswith("ores."))
        except OSError as e_:
            ov["file"] = ["no file: %s" % e_]
        Fn.cmdSetConsole("ores.lead", "0.85")
        # WgCfg.apply: a hand-edited file (clamp, junk keeps the running value, missing line keeps it)
        RECS.clear()
        apply("ores.lead=5\nores.cobaltBoost=xyz\nores.slag=-1\nores.adamantiteBoost=0.5\n")
        ov["apply"] = [float(Isl.F_LEAD), float(Isl.B_COBALT), float(Isl.F_SLAG), float(Isl.F_CHROMIUM), float(Isl.B_ADAMANTITE)]
        ov["apply_warn"] = [x for x in logs() if "ores." in x][:4]
        ov["loaded"] = str(Cfg.LOADED)
        for f_, v_ in zip(FACT, ov["fact0"]):
            setattr(Isl, f_, v_)
        ov["p1"] = [float(Isl.orep(t_)) for t_ in range(len(ov["names"]))]
        # the real ores() on synthetic chunks: ids 101.. = the ores, 7 = a host rock (stone), 8 = a sandstone, 9 = anything else
        Ctm2 = JClass("javassist.CtNewMethod")
        nsc = HPool.makeClass("skyywg073.NoStateChunk", HPool.get("com.hypixel.hytale.server.core.universe.world.worldgen.GeneratedChunk"))
        nsc.addConstructor(Ctc.make("public NoStateChunk() { super(); }", nsc))
        nsc.addMethod(Ctm2.make("public com.hypixel.hytale.component.Holder getState(int x, int y, int z) { return null; }", nsc))
        nsc.writeFile(hcls)
        NSC = JClass("skyywg073.NoStateChunk")

        def vein_run(kls, fill, zone, spots):
            n_ = len(kls.ORE_NAMES)
            kls.HOST = JArray(JInt)([7])
            try:
                kls.HOSTX = JArray(JInt)([8])
            except Exception:
                pass
            kls.ORE = JArray(JInt)([101 + k_ for k_ in range(n_)])
            g_ = NSC()
            b_ = g_.getBlockChunk()
            bot_ = JArray(JInt)([0] * (34 * 34))
            tb_ = JArray(JInt)([140] * (32 * 32))
            isl_ = JArray(JInt)([zone] * (34 * 34))
            tot_ = [0] * n_
            for bx_, bz_ in spots:
                for y_ in range(0, 141):
                    for x_ in range(32):
                        for z_ in range(32):
                            b_.setBlock(x_, y_, z_, fill(x_, y_, z_), 0, 0)
                kls.ores(g_, b_, bx_, bz_, bot_, tb_, isl_)
                for y_ in range(0, 141):
                    for x_ in range(32):
                        for z_ in range(32):
                            v_ = int(b_.getBlock(x_, y_, z_))
                            if v_ > 100 and v_ < 200:
                                tot_[v_ - 101] += 1
            return tot_
        SPOTS = [(0, 0), (32, 0), (0, 32), (512, 96), (-64, -64), (1024, 2048), (96, -320), (-640, 288)]
        mix = lambda x_, y_, z_: 8 if (x_ + z_) % 2 else 7
        ov["veins"] = dict((str(zi_ + 1), vein_run(Isl, mix, zi_, SPOTS)) for zi_ in range(5))
        IslP = JClass(PKG + "WgZ2Isles", loader=L["prev"])
        ov["prev_veins"] = dict((str(zi_ + 1), vein_run(IslP, mix, zi_, SPOTS)) for zi_ in (3, 4))
        GSPOTS = [(64 * i_ - 1280, 96 * (i_ % 7) - 320) for i_ in range(40)]
        ov["gold"] = dict((str(zi_ + 1), vein_run(Isl, mix, zi_, GSPOTS)[2]) for zi_ in (2, 3, 4))
        Isl.P_GOLD45 = 0.0
        ov["gold_off"] = vein_run(Isl, mix, 3, GSPOTS)
        Isl.P_GOLD45 = 0.04
        ov["nt"] = [int(Isl.ORE_NT.get(t_)) for t_ in range(len(ov["names"]))]
        ov["ore_text"] = str(Isl.oreText())
        # the real mirror() on synthetic chunks: rule r's sources = 500 + r, its new blocks 600 + r / 700 + r, every host = 8; one source voxel
        # per 8^3 cell in the quadrant lx, lz < 16 (64 cells a chunk), so the three reflections land in the other quadrants
        nr = int(Isl.MR_N)
        o1 = [600 + r_ if str(Isl.MR_O1_NAMES[r_]) else -1 for r_ in range(nr)]
        o2 = [700 + r_ if str(Isl.MR_O2_NAMES[r_]) else -1 for r_ in range(nr)]
        IA = JArray(JInt)
        Isl.MR_SRC = JArray(IA)([IA([500 + r_]) for r_ in range(nr)])
        Isl.MR_HOST = JArray(IA)([IA([8]) for r_ in range(nr)])
        Isl.MR_O1 = IA(o1)
        Isl.MR_O2 = IA(o2)
        sm_ = [0] * 800
        for r_ in range(nr):
            sm_[500 + r_] = 1
        Isl.SRCMAP = JArray(jpype.JByte)(sm_)
        MSPOTS = [(0, 0), (32, 0), (0, 32), (512, 96), (-64, -64), (1024, 2048), (96, -320), (-640, 288), (4096, 32), (-32, 4096), (160, 160), (-2048, -1024)]

        def mirror_run(r, zone, fill=lambda x_, y_, z_: 8, isl_fn=None, spots=MSPOTS, tb_fn=None):
            g_ = NSC()
            b_ = g_.getBlockChunk()
            bot_ = JArray(JInt)([0] * (34 * 34))
            tb_ = JArray(JInt)([(140 if tb_fn is None else tb_fn(c_ // 32, c_ % 32)) for c_ in range(32 * 32)])
            isl_ = JArray(JInt)([(zone if isl_fn is None else isl_fn(i_ // 34 - 1, i_ % 34 - 1)) for i_ in range(34 * 34)])
            res_ = {"src": 0, "boost": 0, "o1": 0, "o2": 0, "bad_pos": 0, "src_after": 0, "ymax": -1}
            for bx_, bz_ in spots:
                for y_ in range(0, 141):
                    for x_ in range(32):
                        for z_ in range(32):
                            b_.setBlock(x_, y_, z_, fill(x_, y_, z_), 0, 0)
                srcs_ = set()
                for cx_ in (0, 1):
                    for cz_ in (0, 1):
                        for cy_ in range(1, 17):
                            x_, y_, z_ = cx_ * 8 + 3, cy_ * 8 + 4, cz_ * 8 + 5
                            b_.setBlock(x_, y_, z_, 500 + r, 0, 0)
                            srcs_.add((x_, y_, z_))
                res_["src"] += len(srcs_)
                Isl.mirror(g_, b_, bx_, bz_, bot_, tb_, isl_)
                refl_ = set()
                for (x_, y_, z_) in srcs_:
                    refl_ |= {(31 - x_, y_, z_), (x_, y_, 31 - z_), (31 - x_, y_, 31 - z_)}
                for y_ in range(0, 141):
                    for x_ in range(32):
                        for z_ in range(32):
                            v_ = int(b_.getBlock(x_, y_, z_))
                            if v_ == 500 + r:
                                if (x_, y_, z_) in srcs_:
                                    res_["src_after"] += 1
                                else:
                                    res_["boost"] += 1
                                    res_["ymax"] = max(res_["ymax"], y_)
                                    res_["bad_pos"] += 0 if (x_, y_, z_) in refl_ else 1
                            elif v_ == 600 + r or v_ == 700 + r:
                                res_["o1" if v_ == 600 + r else "o2"] += 1
                                res_["ymax"] = max(res_["ymax"], y_)
                                res_["bad_pos"] += 0 if (x_, y_, z_) in refl_ else 1
            return res_
        MRN = [str(x) for x in Isl.MR_NAME]
        for k_ in range(3 * nr):
            Isl.MR_PUT.set(k_, 0)
        ov["mir"] = dict((MRN[r_], mirror_run(r_, int(Isl.MR_ISL[r_]))) for r_ in (0, 1, 2, 3))
        ov["mir_silver0"] = mirror_run(MRN.index("silver1"), 0)
        Isl.X_SILVER = 0.3
        ov["mir_silver3"] = mirror_run(MRN.index("silver1"), 0)
        Isl.X_SILVER = 0.0
        ov["mir_wrong_zone"] = mirror_run(0, 0)
        ov["mir_no_host"] = mirror_run(0, 1, fill=lambda x_, y_, z_: 9)
        ov["mir_other_isle"] = mirror_run(0, 1, isl_fn=lambda x_, z_: 1 if (x_ < 16 and z_ < 16) else 2)
        Isl.F_LEAD = 0.0
        Isl.B_THORIUM = 1.0
        ov["mir_off"] = mirror_run(0, 1)
        Isl.F_LEAD, Isl.B_THORIUM = 0.85, 1.15
        # critic M1: the cover band - island tops at y 100 -> no source above 94 is copied, no copy above 94; a target column off the island
        ov["mir_cover"] = mirror_run(0, 1, tb_fn=lambda x_, z_: 100)
        ov["mir_tb_off"] = mirror_run(0, 1, tb_fn=lambda x_, z_: 140 if (x_ < 16 and z_ < 16) else -1)
        # critic M2: the early-out (active islands) + the live chunk gate oreMask()
        ov["active"] = [int(Isl.mrActive()), int(Isl.oreMask())]
        Isl.X_SILVER = 0.3
        ov["active_silver"] = [int(Isl.mrActive()), int(Isl.oreMask())]
        Isl.X_SILVER = 0.0
        for f_ in ("F_LEAD", "F_CHROMIUM", "F_SLAG", "F_MITHRIL5"):
            setattr(Isl, f_, 0.0)
        for f_ in ("B_THORIUM", "B_COBALT", "B_ADAMANTITE"):
            setattr(Isl, f_, 1.0)
        ov["active_off"] = [int(Isl.mrActive()), int(Isl.oreMask())]
        for f_, v_ in zip(FACT, ov["fact0"]):
            setattr(Isl, f_, v_)
        # ms per chunk (the synthetic 64-source chunk, y 0-140 rock): an active island (Zone 2) and an inactive one (Zone 1 at the defaults)
        gT = NSC()
        bT = gT.getBlockChunk()
        for y_ in range(0, 141):
            for x_ in range(32):
                for z_ in range(32):
                    bT.setBlock(x_, y_, z_, 8, 0, 0)
        for cx_ in (0, 1):
            for cz_ in (0, 1):
                for cy_ in range(1, 17):
                    bT.setBlock(cx_ * 8 + 3, cy_ * 8 + 4, cz_ * 8 + 5, 500, 0, 0)
        botT, tbT = JArray(JInt)([0] * 1156), JArray(JInt)([140] * 1024)
        ms_ = {}
        for zt_ in (1, 0):
            islT = JArray(JInt)([zt_] * 1156)
            for k_ in range(30):
                Isl.mirror(gT, bT, 0, 0, botT, tbT, islT)
            t0_ = time.perf_counter()
            for k_ in range(200):
                Isl.mirror(gT, bT, 0, 0, botT, tbT, islT)
            ms_[str(zt_ + 1)] = round((time.perf_counter() - t0_) * 1000.0 / 200, 3)
        ov["ms"] = ms_
        ov["mir_text"] = str(Isl.mirText())
        Isl.SRCMAP = JArray(jpype.JByte)([])
        # the real CraftingRecipe codec on the jar's recipes (5 standalone alloys + the 4 embedded ingot recipes)
        CRc = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
        AEI = JClass("com.hypixel.hytale.assetstore.AssetExtraInfo")
        ADT = JClass("com.hypixel.hytale.assetstore.AssetExtraInfo$Data")
        RJR = JClass("com.hypixel.hytale.codec.util.RawJsonReader")
        zj_ = zipfile.ZipFile(JAR)
        rec = {}
        for n_ in sorted(zj_.namelist()):
            txt_, key_ = None, None
            if n_.startswith("Server/Item/Recipes/SkyWynn/"):
                txt_, key_ = zj_.read(n_).decode("utf-8"), n_.rsplit("/", 1)[1][:-5]
            elif n_.startswith("Server/Item/Items/SkyWynn/Ingredient_Bar_") and "Recipe" in json.loads(zj_.read(n_)):
                txt_, key_ = json.dumps(json.loads(zj_.read(n_))["Recipe"]), n_.rsplit("/", 1)[1][:-5] + "_Recipe_Generated_0"
            if txt_ is None:
                continue
            ei_ = AEI(Paths.get(key_ + ".json"), ADT(CRc.class_, key_, None))
            try:
                o_ = CRc.CODEC.decodeJson(RJR.fromJsonString(txt_), ei_)
                vr_ = ei_.getValidationResults()
                rec[key_] = dict(inp=[[str(m_.getItemId()), int(m_.getQuantity())] for m_ in o_.getInput()],
                                 out=None if o_.getPrimaryOutput() is None else [str(o_.getPrimaryOutput().getItemId()), int(o_.getPrimaryOutput().getQuantity())],
                                 bench=[[str(b_.type), str(b_.id)] for b_ in (o_.getBenchRequirement() or [])], t=float(o_.getTimeSeconds()),
                                 know=bool(o_.isKnowledgeRequired()), unknown=[str(x) for x in ei_.getUnknownKeys()],
                                 failed=bool(vr_ is not None and vr_.hasFailed()))
            except Exception as e_:
                rec[key_] = dict(error=str(e_)[:300])
        ov["recipes"] = rec
        E["ov"] = ov
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
    ov = E["ov"]
    print("OV. %s" % json.dumps(dict((k_, v_) for k_, v_ in ov.items() if k_ not in ("recipes", "mr")))[:3000])
    check(ov["names"] == ["Ore_Onyxium_SkyWynn", "Ore_Mithril_Stone", "Ore_Gold_Volcanic"], "OV: the sphere rows = Onyxium, Mithril (same index), + Gold: %s" % ov["names"])
    check(ov["mask"] == [24, 8, 24] and ov["live"] == [0, 0, 1] and ov["hx"] == [0, 0, 0] and ov["any"] == 31,
          "OV: Onyxium Zones 4+5, Mithril Zone 4 only, Gold Zones 4+5 (live), mirrors on every zone: %s %s %s %s" % (ov["mask"], ov["live"], ov["hx"], ov["any"]))
    check(ov["p0"] == [0.016, 0.017, 0.04] and ov["p1"] == ov["p0"], "OV: orep(): Onyxium / Mithril from the table, Gold live 0.04: %s" % ov["p0"])
    mr = dict((m_[0], m_) for m_ in ov["mr"])
    print("OV rules. %s" % json.dumps(ov["mr"])[:2500])
    want_mr = {"thorium": (1, "Ore_Lead_Sandstone_SkyWynn", ""), "cobalt": (2, "Ore_Chromium_Shale_SkyWynn", ""), "adamantite": (3, "Ore_Slag_Volcanic_SkyWynn", ""),
               "adamantite5": (4, "Ore_Mithril_Stone", "Ore_Titanium_Basalt_SkyWynn")}
    for n_, (i_, a_, b_) in want_mr.items():
        m_ = mr.get(n_, [None] * 6)
        check(m_[1] == i_ and m_[2] == a_ and m_[3] == b_, "OV: mirror rule %s: island %s -> %s / %s: %s" % (n_, i_, a_, b_, m_[:4]))
    check(mr["thorium"][4] == ["Ore_Thorium_Mud", "Ore_Thorium_Mud_Cracked", "Ore_Thorium_Sandstone"] and
          mr["thorium"][5] == sorted(["Rock_Sandstone", "Rock_Sandstone_White", "Rock_Sandstone_Red", "Rock_Volcanic", "Soil_Dirt_Dry", "Soil_Mud_Dry"]),
          "OV: Thorium's sources = every vanilla Thorium ore block, hosts = vanilla ThoriumPlacement's BlockMask: %s" % mr["thorium"][4:])
    check("Rock_Magma_Cooled" in mr["adamantite"][5] and mr["adamantite"][4] == ["Ore_Adamantite_Magma", "Ore_Adamantite_Magma_Cracked"]
          and mr["adamantite5"][4:] == mr["adamantite"][4:], "OV: Zone 5 copies Zone 4's Adamantite placement: %s" % mr["adamantite5"][4:])
    check(sorted(m_[1] for m_ in ov["mr"] if m_[0].startswith("silver")) == [0, 1, 3, 4] and sorted(m_[1] for m_ in ov["mr"] if m_[0].startswith("gold")) == [0, 1, 3, 4],
          "OV: Silver / Gold extra copies on every zone but Zone 3 (the best one)")
    check(ov["fact0"] == [1.15, 1.15, 1.15, 0.85, 0.85, 0.85, 0.85, 0.85, 0.0, 0.0, 0.04], "OV: the default factors: %s" % ov["fact0"])
    mw = dict(zip([m_[0] for m_ in ov["mr"]], ov["mw0"]))
    check(mw["thorium"] == [0.15, 0.9775, 0.0] and mw["cobalt"] == mw["thorium"] and mw["adamantite"] == mw["thorium"] and mw["adamantite5"] == [0.0, 0.85, 0.7225]
          and mw["silver1"] == [0.0, 0.0, 0.0], "OV: weights: base +15 %%, new = 0.85 x 1.15 = 0.9775, Zone 5 Mithril 0.85 / Titanium 0.7225, Silver 0: %s" % mw)
    check(ov["after_set"][4] == 1.15 and "1" in ov["set"][3], "OV: a boost below 1 is refused (row min 1): %s %s" % (ov["after_set"], ov["set"][3][:80]))
    check(ov["after_set"][:2] == [1.0, 1.15] and ov["after_set"][2] == 0.04 and ov["after_set"][3] == 1.15,
          "OV: Server Setup ores.lead 1.0 live (Lead weight 1.0 x 1.15), 3 refused (max 2), 'abc' refused: %s %s" % (ov["after_set"], [x[:60] for x in ov["set"]]))
    want_file = sorted(["ores.thoriumBoost=1.15", "ores.cobaltBoost=1.15", "ores.adamantiteBoost=1.15", "ores.lead=1", "ores.chromium=0.85", "ores.slag=0.85",
                        "ores.mithril5=0.85", "ores.titanium=0.85", "ores.silverExtra=0.0", "ores.goldExtra=0.0", "ores.gold45=0.04"])
    check(ov["file"] == want_file, "OV: the kit wrote ores.lead=1.0 into config.properties (the other ore lines = their defaults): %s" % ov["file"])
    check(ov["apply"] == [1.5, 1.15, 0.0, 0.85, 1.0] and len(ov["apply_warn"]) >= 3, "OV: WgCfg.apply: 5 -> 1.5 (WARN), junk keeps the running value (WARN), -1 -> 0, missing line keeps: %s %s" % (ov["apply"], ov["apply_warn"]))
    check("ore veins thoriumBoost 1.15" in ov["loaded"] and "gold45 0.04" in ov["loaded"], "OV: LOADED names the ore factors: %s" % ov["loaded"][:500])
    v = ov["veins"]
    check(v["1"] == [0] * 3 and v["2"] == [0] * 3 and v["3"] == [0] * 3, "OV: Zones 1-3 get no sphere ore: %s" % v)
    check(v["4"][0] > 0 and v["4"][1] > 0 and v["5"][0] == v["4"][0] and v["5"][1] == 0,
          "OV: Zone 4 Onyxium + Mithril, Zone 5 Onyxium (no sphere Mithril): %s %s" % (v["4"], v["5"]))
    check(ov["gold"]["3"] == 0 and ov["gold"]["4"] > 0 and ov["gold"]["5"] > 0, "OV: Gold veins (40 chunks) in Zones 4 + 5 only: %s" % ov["gold"])
    check(ov["prev_veins"]["4"][:2] == v["4"][:2] and ov["prev_veins"]["5"][0] == v["5"][0],
          "OV: Onyxium (Zones 4 + 5) and Zone 4 Mithril = 0.7.2's jar block for block on the same chunks: new %s / %s, 0.7.2 %s" % (v["4"][:2], v["5"][:2], ov["prev_veins"]))
    check(ov["gold_off"][2] == 0, "OV: ores.gold45 = 0 -> no Gold: %s" % ov["gold_off"])
    check(ov["ore_text"].startswith("Onyxium ") and "Gold " in ov["ore_text"], "OV: oreText: %s" % ov["ore_text"])
    mi = ov["mir"]
    print("OV mirror. %s" % json.dumps(mi))

    def near(got, want, tol=0.2):
        return abs(got - want) <= tol * max(want, 1.0)
    for n_ in ("thorium", "cobalt", "adamantite"):
        r_ = mi[n_]
        check(r_["src"] == 768 and r_["src_after"] == 768 and r_["bad_pos"] == 0 and near(r_["boost"], 768 * 0.15) and near(r_["o1"], 768 * 0.9775) and r_["o2"] == 0,
              "OV: mirror %s on 768 vanilla vein cells: sources kept, +%d base copies (want ~%d = +15 %%), %d new-ore copies (want ~%d = 0.85 x 1.15), all at the "
              "reflected spot, same height: %s" % (n_, r_["boost"], 768 * 0.15, r_["o1"], 768 * 0.9775, r_))
    r_ = mi["adamantite5"]
    check(r_["boost"] == 0 and near(r_["o1"], 768 * 0.85) and near(r_["o2"], 768 * 0.7225) and r_["bad_pos"] == 0,
          "OV: Zone 5: Mithril copies ~%d (0.85 x Adamantite), Titanium ~%d (0.85 x that Mithril), Adamantite itself not boosted: %s" % (768 * 0.85, 768 * 0.7225, r_))
    check(mi_ok := (ov["mir_silver0"]["boost"] == 0 and near(ov["mir_silver3"]["boost"], 768 * 0.3)), "OV: Silver extra 0 -> no copies, 0.3 -> ~230: %s %s" % (ov["mir_silver0"], ov["mir_silver3"]))
    check(ov["mir_wrong_zone"]["boost"] + ov["mir_wrong_zone"]["o1"] == 0, "OV: Thorium copies only on Zone 2: %s" % ov["mir_wrong_zone"])
    check(ov["mir_no_host"]["boost"] + ov["mir_no_host"]["o1"] == 0, "OV: never into a block outside the vanilla host mask: %s" % ov["mir_no_host"])
    check(ov["mir_other_isle"]["boost"] + ov["mir_other_isle"]["o1"] == 0, "OV: never onto another island's column: %s" % ov["mir_other_isle"])
    check(ov["mir_off"]["boost"] + ov["mir_off"]["o1"] == 0 and ov["mir_off"]["src_after"] == 768, "OV: boost 1 + Lead 0 -> vanilla exactly: %s" % ov["mir_off"])
    mc = ov["mir_cover"]
    check(mc["ymax"] <= 94 and mc["src"] == 768 and near(mc["boost"] + mc["o1"], (mi["thorium"]["boost"] + mi["thorium"]["o1"]) * 11.0 / 16.0, 0.25) and mc["bad_pos"] == 0,
          "OV (critic M1): island tops at y 100 -> copies only in the cover band (highest %d <= 94), only of the 11 / 16 source cells under it: %s" % (mc["ymax"], mc))
    check(ov["mir_tb_off"]["boost"] + ov["mir_tb_off"]["o1"] == 0, "OV (critic M1): never into a column without an island top: %s" % ov["mir_tb_off"])
    check(ov["active"] == [30, 30] and ov["active_silver"] == [31, 31] and ov["active_off"] == [0, 24],
          "OV (critic M2): active mirror islands / chunk gate - defaults Zones 2-5 (no Zone 1 work), Silver extra on -> + Zone 1, every factor off -> no mirror island (only the sphere rows' Zones 4-5): %s %s %s" % (ov["active"], ov["active_silver"], ov["active_off"]))
    check(ov["ms"]["1"] < 0.1 and ov["ms"]["2"] < 2.0, "OV (critic M2): mirror() %.3f ms per chunk on an active island (Zone 2), %.3f ms on an inactive one (Zone 1)" % (ov["ms"]["2"], ov["ms"]["1"]))
    NOTES.append("OV mirror() ms per chunk (synthetic 64-source chunk, y 0-140 rock, this JVM): Zone 2 %.3f, Zone 1 (defaults, early-out) %.3f; "
                 "before the critic fix (same chunk, scratch probe on the earlier 0.7.3 jar): Zone 2 2.290, Zone 1 2.389" % (ov["ms"]["2"], ov["ms"]["1"]))
    check(ov["mir_text"].startswith("thorium ") and "adamantite5 " in ov["mir_text"], "OV: mirText for the run report: %s" % ov["mir_text"][:200])
    NOTES.append("OV mirror counts on 768 synthetic vanilla vein cells (every reflected spot in host rock): %s" % "; ".join(
        "%s +%d base / %d / %d" % (n_, mi[n_]["boost"], mi[n_]["o1"], mi[n_]["o2"]) for n_ in ("thorium", "cobalt", "adamantite", "adamantite5")))
    NOTES.append("OV sphere ores on 8 synthetic chunks (half stone / half sandstone): Zone 4 %s, Zone 5 %s (Onyxium, Mithril, Gold); Gold on 40 chunks %s" % (v["4"], v["5"], ov["gold"]))
    rec = ov["recipes"]
    print("OV recipes. %s" % json.dumps(rec)[:1800])
    for w_, (a_, b_, s_, out_) in AL.items():
        r_ = rec.get("Alloy_" + w_, {})
        check(r_.get("inp") == [[a_, 1], [b_, 1]] and r_.get("out") == [out_, 1] and r_.get("bench") == [["Processing", "SkyyAlloy"]] and r_.get("t") == float(s_)
              and not r_.get("unknown") and not r_.get("failed") and r_.get("know") is False,
              "OV: Alloy_%s decodes through the engine's CraftingRecipe codec: %s + %s -> %s, bench SkyyAlloy, %d s, no unknown key: %s" % (w_, a_, b_, out_, s_, r_))
    for m_, (z_, pt_, h_, cob_, s_, pb_) in ZM.items():
        r_ = rec.get("Ingredient_Bar_%s_SkyWynn_Recipe_Generated_0" % m_, {})
        check(r_.get("inp") == [["Ore_%s_SkyWynn" % m_, 1]] and r_.get("bench") == [["Processing", "Furnace"]] and r_.get("t") == float(s_) and not r_.get("unknown"),
              "OV: the %s ingot recipe = Furnace, 1 Ore_%s_SkyWynn, %d s: %s" % (m_, m_, s_, r_))
    st = E["st"]
    print("ST. %s" % json.dumps(st)[:700])
    check(st[2], "ST: the live Skyy_SkyyWorldGen folder exists (copied into scratch): %s" % st[2])
    check(all(not s_[0] for s_ in st[0]), "ST: two starts on the copy change no file: %s" % [s_[0] for s_ in st[0]])
    check(all(s_[2] is True for s_ in st[0]), "ST: the copy -> server spawn on: %s" % [s_[2:4] for s_ in st[0]])
    check(all("server spawn ON" in s_[4] for s_ in st[0]), "ST: LOADED names the server spawn state: %s" % st[0][0][4][-120:])


WN3 = "skywynn_zones2"


def fmt(v):
    r = round(float(v) * 100.0) / 100.0
    return str(int(r)) if r == int(r) else ("%s" % r)


# ================================================================= M (0.7.3): the jar's metal assets against Assets.zip
def section_m():
    import tier_tags as TT
    import skyyart as SA
    import serverjar
    zj = zipfile.ZipFile(JAR)
    az = zipfile.ZipFile(serverjar.assets_zip())
    an = set(az.namelist())
    jn = set(zj.namelist())
    items = dict((n.rsplit("/", 1)[1][:-5], n) for n in an if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    mine = dict((n.rsplit("/", 1)[1][:-5], json.loads(zj.read(n))) for n in jn if n.startswith("Server/Item/Items/SkyWynn/") and n.endswith(".json"))
    new = sorted(k for k in mine if k != "Ore_Onyxium_SkyWynn")
    check(new == METAL_IDS == sorted(TT.WG_IDS), "M: the jar's new items = the spec's 17 ids = tier_tags WG_IDS: %s" % new)
    check(not [k for k in new if k in items], "M: no new id exists in Assets.zip")
    check("Server/Item/Items/SkyWynn/Ingredient_Bar_Bronze.json" not in jn and not [n for n in jn if n.endswith("/Ingredient_Bar_Bronze.json")], "M: vanilla Bronze's item JSON is not overridden")

    def van(i):
        return json.loads(az.read(items[i]).decode("utf-8-sig"))

    def refs_ok(d):
        bad = []
        for key in ("Icon", "Texture", "Model"):
            if key in d and ("Common/" + d[key]) not in an and ("Common/" + d[key]) not in jn:
                bad.append(d[key])
        bt = d.get("BlockType") or {}
        for t_ in [x["Texture"] for x in bt.get("CustomModelTexture", [])] + [x.get("All") for x in bt.get("Textures", [])] + [bt.get("CustomModel")]:
            if t_ and ("Common/" + t_) not in an and ("Common/" + t_) not in jn:
                bad.append(t_)
        for c_ in ((bt.get("Gathering") or {}).get("Breaking") or {}).get("DropList", {}).get("Container", {}).get("Containers", []):
            i_ = c_["Item"]["ItemId"]
            if i_ not in items and i_ not in mine:
                bad.append(i_)
        return bad
    lang = dict(l.split("=", 1) for l in zj.read("Server/Languages/en-US/server.lang").decode("ascii").splitlines() if "=" in l and not l.startswith("#"))
    vlang = az.read("Server/Languages/en-US/server.lang").decode("utf-8")
    for m_, (z_, pt_, h_, cob_, s_, pb_) in ZM.items():
        blk, raw, bar = "Ore_%s_%s_SkyWynn" % (m_, h_), "Ore_%s_SkyWynn" % m_, "Ingredient_Bar_%s_SkyWynn" % m_
        b, vb = mine[blk], van(pb_)
        diff = sorted(k for k in set(b) | set(vb) if b.get(k) != vb.get(k))
        check(set(diff) <= {"TranslationProperties", "Icon", "BlockType", "Tags"}, "M: %s = vanilla %s but names / icon / block / tags: %s" % (blk, pb_, diff))
        bt, vbt = b["BlockType"], vb["BlockType"]
        bd = sorted(k for k in set(bt) | set(vbt) if bt.get(k) != vbt.get(k))
        check(set(bd) <= {"CustomModelTexture", "Textures", "Gathering", "ParticleColor", "TextureComputedColor"}, "M: %s BlockType differs only in texture / host / drops / colours: %s" % (blk, bd))
        brk, vbrk = bt["Gathering"]["Breaking"], vbt["Gathering"]["Breaking"]
        check(brk.get("GatherType") == vbrk.get("GatherType") and brk.get("Quality") == vbrk.get("Quality"),
              "M: %s mines like %s (GatherType %s, Quality %s)" % (blk, pb_, brk.get("GatherType"), brk.get("Quality")))
        drops = [c_["Item"]["ItemId"] for c_ in brk["DropList"]["Container"]["Containers"]]
        check(drops == [raw, cob_], "M: %s drops 1 %s + 1 %s: %s" % (blk, raw, cob_, drops))
        check(bt["Textures"] == [{"Weight": 1, "All": "BlockTextures/Rock_%s%s.png" % (h_, "_Side" if h_ == "Sandstone" else "")}], "M: %s host texture: %s" % (blk, bt["Textures"]))
        r, vr = mine[raw], van("Ore_" + pt_)
        diff = sorted(k for k in set(r) | set(vr) if r.get(k) != vr.get(k))
        check(set(diff) == {"TranslationProperties", "Icon", "Texture", "Recipe"} and "Recipe" not in r, "M: %s = vanilla Ore_%s minus its Salvagebench recipe, own texture / icon / names: %s" % (raw, pt_, diff))
        i, vi = mine[bar], van("Ingredient_Bar_" + pt_)
        diff = sorted(k for k in set(i) | set(vi) if i.get(k) != vi.get(k))
        check(set(diff) == {"TranslationProperties", "Icon", "Texture", "Recipe"} and i["Recipe"]["TimeSeconds"] == s_ == vi["Recipe"]["TimeSeconds"]
              and i["Recipe"]["Input"] == [{"ItemId": raw, "Quantity": 1}] and i.get("ResourceTypes") == [{"Id": "Metal_Bars"}],
              "M: %s = vanilla Ingredient_Bar_%s (Metal_Bars, %d s Furnace) with input %s: %s" % (bar, pt_, s_, raw, diff))
        for k in (blk, raw, bar):
            check(not refs_ok(mine[k]), "M: every file / item %s references exists: %s" % (k, refs_ok(mine[k])))
    for w_, (a_, b_, s_, out_) in AL.items():
        n_ = "Server/Item/Recipes/SkyWynn/Alloy_%s.json" % w_
        check(n_ in jn, "M: the alloy recipe file %s" % n_)
        r_ = json.loads(zj.read(n_)) if n_ in jn else {}
        check(r_ == {"Input": [{"ItemId": a_, "Quantity": 1}, {"ItemId": b_, "Quantity": 1}], "PrimaryOutput": {"ItemId": out_, "Quantity": 1},
                     "Output": [{"ItemId": out_, "Quantity": 1}], "BenchRequirement": [{"Type": "Processing", "Id": "SkyyAlloy"}], "TimeSeconds": s_},
              "M: Alloy_%s = %s + %s -> 1 %s at SkyyAlloy, %d s (spec 3): %s" % (w_, a_, b_, out_, s_, r_))
        check(all(x in items or x in mine for x in (a_, b_, out_)), "M: Alloy_%s inputs / output exist" % w_)
        if w_ != "Bronze":
            al, va = mine[out_], van(a_)
            diff = sorted(k for k in set(al) | set(va) if al.get(k) != va.get(k))
            check(set(diff) == {"TranslationProperties", "Icon", "Texture", "Recipe", "ResourceTypes"} and "Recipe" not in al and "ResourceTypes" not in al,
                  "M: %s = vanilla %s without recipe / ResourceTypes (like vanilla Bronze): %s" % (out_, a_, diff))
            check(not refs_ok(al), "M: %s references exist: %s" % (out_, refs_ok(al)))
    check(not [n for n in an if n.startswith("Server/Item/Recipes/") and n.rsplit("/", 1)[1].startswith("Alloy_")], "M: no vanilla recipe id Alloy_*")
    # lang: name + description per id, both key forms, the tag first, no vanilla key
    for k in METAL_IDS:
        for pre in ("items.", "server.items."):
            d_ = lang.get(pre + k + ".description", "")
            check(lang.get(pre + k + ".name") and d_.startswith(TT.tag_for(k) + " - "), "M: lang %s%s name + description starting '%s': %r" % (pre, k, TT.tag_for(k), d_[:60]))
        check(("items.%s." % k) not in vlang, "M: vanilla lang has no key for %s" % k)
    check(len(lang) == 68 and all(k_.split(".")[-2] in METAL_IDS or k_.split(".")[-2] == "" for k_ in lang), "M: the lang file holds only our 68 keys: %d" % len(lang))
    check(TT.tag_for("Ore_Lead_SkyWynn") == "T4 Lead" and TT.tag_for("Ingredient_Bar_Lumen_SkyWynn") == "T7 Lumen" and TT.tag_for("Ore_Slag_Volcanic_SkyWynn") == "T6 Slag",
          "M: tags T4 Lead / T7 Lumen / T6 Slag (spec Q6)")
    # PNGs: recolours of the vanilla pixels - same size, the same alpha mask, the colour changed
    pngs = sorted(n for n in jn if n.endswith(".png"))
    check(len(pngs) == 26, "M: 26 PNGs (4 ore + 9 ingot textures, 13 icons): %d" % len(pngs))
    src = {}
    for m_, (z_, pt_, h_, cob_, s_, pb_) in ZM.items():
        src["Common/Items/SkyyWorldGen/Ores/%s.png" % m_] = "Common/Resources/Ores/Ore_Textures/%s.png" % pt_
        src["Common/Items/SkyyWorldGen/Ingots/%s.png" % m_] = "Common/Resources/Materials/Ingot_Textures/%s.png" % pt_
        src["Common/Icons/ItemsGenerated/SkyyWorldGen_Ore_%s_SkyWynn.png" % m_] = "Common/Icons/ItemsGenerated/Ore_%s.png" % pt_
        src["Common/Icons/ItemsGenerated/SkyyWorldGen_Ingredient_Bar_%s_SkyWynn.png" % m_] = "Common/Icons/ItemsGenerated/Ingredient_Bar_%s.png" % pt_
    for w_, (a_, b_, s_, out_) in AL.items():
        if w_ != "Bronze":
            pt_ = a_.split("_")[2]
            src["Common/Items/SkyyWorldGen/Ingots/%s.png" % w_] = "Common/Resources/Materials/Ingot_Textures/%s.png" % pt_
            src["Common/Icons/ItemsGenerated/SkyyWorldGen_%s.png" % out_] = "Common/Icons/ItemsGenerated/Ingredient_Bar_%s.png" % pt_
    check(sorted(src) == pngs, "M: every PNG has its vanilla source: %s" % sorted(set(pngs) ^ set(src)))
    for p_, v_ in sorted(src.items()):
        if p_ not in jn:
            continue
        a, b = SA.png_decode(zj.read(p_)), SA.png_decode(az.read(v_))
        same_a = all(a.px[q * 4 + 3] == b.px[q * 4 + 3] for q in range(a.w * a.h)) if (a.w, a.h) == (b.w, b.h) else False
        chg = sum(1 for q in range(a.w * a.h) if a.px[q * 4 + 3] and a.px[q * 4:q * 4 + 3] != b.px[q * 4:q * 4 + 3])
        check((a.w, a.h) == (b.w, b.h) and same_a and chg > 0.5 * sum(1 for q in range(a.w * a.h) if a.px[q * 4 + 3]),
              "M: %s = a recolour of %s (%dx%d, alpha kept, %d texels recoloured)" % (p_.rsplit("/", 1)[1], v_.rsplit("/", 1)[1], a.w, a.h, chg))
    # no vanilla file is shipped: every jar entry outside our own paths is not an Assets.zip path (but the new lang file name)
    clash = sorted(n for n in jn if n in an and not n.endswith(".class") and n != "manifest.json" and n != "Server/Languages/en-US/server.lang")
    check(not clash, "M: the jar ships no file at a vanilla path: %s" % clash[:5])


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
        rules = [[r"worldgen_0_7_3_patch", "worldgen_0_7_2_patch"]]
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
            check(set(const) <= ALLOWED | ALLOWED_CONST | set(c for c in cls_ if c.startswith("Cfg")), "CC: text-only changes only where expected: %s" % sorted(const))
        # ---- JT
        zj, zp = zipfile.ZipFile(JAR), zipfile.ZipFile(PREV_JAR)
        cn, cp_ = set(n for n in zj.namelist() if n.endswith(".class")), set(n for n in zp.namelist() if n.endswith(".class"))
        check(sorted(cn - cp_) == ["com/skyy/worldgen/%s.class" % c for c in NEW_CLASSES] and not (cp_ - cn), "JT: the same class files as 0.7.1: %s %s"
              % (sorted(cn - cp_), sorted(cp_ - cn)))
        nn = set(n for n in zj.namelist() if not n.endswith(".class"))
        np_ = set(n for n in zp.namelist() if not n.endswith(".class"))
        want_new = set(["Server/Item/Items/SkyWynn/%s.json" % i_ for i_ in METAL_IDS] + ["Server/Item/Recipes/SkyWynn/Alloy_%s.json" % w_ for w_ in AL]
                       + ["Server/Languages/en-US/server.lang"])
        png_new = set(n for n in nn - np_ if n.endswith(".png"))
        check(not (np_ - nn) and (nn - np_ - png_new) == want_new and len(png_new) == 26,
              "JT: the non-class entries = 0.7.2's + exactly the 17 items, 6 recipes, the lang file and 26 PNGs: %s %s" % (sorted((nn - np_ - png_new) ^ want_new), sorted(np_ - nn)))
        norm = lambda b_: b_.replace(b"(SkyyWorldGen %s)" % VERSION.encode(), b"(SkyyWorldGen %s)" % PREV_VERSION.encode())
        diff = sorted(n for n in np_ if n != "manifest.json" and norm(zj.read(n)) != zp.read(n))
        print("JT. changed old entries: %s" % diff)
        check(not diff, "JT: every non-class entry byte-identical but the version in a template comment: %s" % diff[:4])
        man = json.loads(zj.read("manifest.json"))
        check(man.get("Version") == VERSION and "zone ores" in man.get("Description", "") and man.get("IncludesAssetPack") is True,
              "JT: manifest %s (asset pack): %s" % (man.get("Version"), man.get("Description", "")[-200:]))
        # ---- M
        try:
            section_m()
        except Exception as e:
            import traceback
            traceback.print_exc()
            check(False, "M crashed: %s" % e)
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
        check("READY" in aa and not mine, "AA: crosscheck --jar 0.7.3 READY, no FAIL for SkyyWorldGen: %s" % (mine[:3] or aa[-300:]))
        bl = [ln.strip() for ln in aa.splitlines() if ln.strip().startswith(("+ ", "- ")) or "baseline SkyyWorldGen" in ln]
        print("AA. %s" % bl)
        plus = [ln for ln in bl if ln.startswith("+ ")]
        check(not [ln for ln in bl if ln.startswith(("+ ", "- "))], "AA: no command / permission tree change vs the baseline: %s" % bl)
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
