"""SkyyWorldGen 0.1 harness - bare JVM, no game. Run: python SkyyWorldGen/test_skyyworldgen_0.1.py [--jar <jar>] [--dir <scratch>] [--keep]

-Xverify:all, -XX:-UsePerfData; HytaleServer.jar + tools/javassist.jar + the SkyyWorldGen jar on the classpath. Nothing is deployed and
nothing outside the scratch folder is written (default tools/dev/scratch/wg01/harness, deleted at the end unless --keep; TEMP / TMP,
java.io.tmpdir and user.home point into it). Assets.zip and the two HytaleServer.jar files (release + 0.7 pre-release) are only read.
The real engine runs on stand-ins for the server singletons only (HytaleServer with an EventBus, Universe, AssetModule, LegacyModule,
BlockTypeModule, an allocated HytaleGenerator, InstancesPlugin, CommandManager) - the proof report's recipe.
Sections:
  A  every class of the jar loads, verifies (-Xverify:all) and initialises;  M  manifest, entries, the 9 asset files, no .ui
  J  the jar's V2 JSON = the stage 0 proof report's recipe, typed here independently (curves, ranges, warp, seeds, envs, tints, trees,
     landing) + the instance template (codec version 4, Plugin.Instance.RemovalConditions [], DeleteOnRemove / DeleteOnUniverseStart false,
     the world's own Death override {"ItemsLossMode": "None"} next to GameplayConfig Default)
  D  the assets decode through the REAL HytaleAssetStores from the jar mounted as a zip pack (1 WorldStructure, 2 Density, 4 Biome, 0
     failed), both exports in DensityAsset.exportedNodes, the generator's own AssetManager got the structure; log scan (HytaleLogger +
     java.util.logging): no WARN / SEVERE / Couldn't find / Unused key / Failed to validate naming a SkyWynn asset or our blocks
  V  getGenerator: our structure -> StagedChunkGenerator, an unknown one -> FallbackGenerator; WgCheck (the /zone guard) with the real
     generator, with no generator and with an asset map that lacks the structure
  C  generated chunks from the jar's own assets: land everywhere within R-30, not one block from R+30, the vanilla environment per ring on
     the surface AND the underside, heights inside the recipe's own bounds (curve +- warp +- noise), grass / 3 dirt / stone layers,
     Birch trees in the forest, Azure trees in the core, none in the meadow, grass tints per ring, generation time per chunk
  G  the landing point: 1-2 blocks above the measured ground, in the meadow, nothing above the ground around it
  G2 the landing.point check against the generated terrain (review finding 2): every column of the rim ring (LANDING_MAX - 40 ..
     LANDING_MAX + 10, all of them) - land under every column within LANDING_MAX + 4; for every land column within LANDING_MAX (the
     ring + section C's columns) ground + 2 (what /zone setlanding writes) passes the Y window and a Y under the island never does; the
     Java top curve = the recipe's; the extremes and a sample through the real WgCfg.landingCheck
  T  determinism: the same SeedOverride gives identical chunks from a fresh generator, another seed differs
  W  the instance template decodes through WorldConfig.CODEC (HandleProvider SkyWynn_Z1_Small / SkyWynn-Z1, GlobalSpawnProvider = the
     landing, Adventure, NPC spawning, GameplayConfig Default, no removal conditions, kept on remove / restart, the Death override =
     MutableDeathConfig NONE / HomeOrSpawnPoint / Default.json's durability loss); vanilla Zone1_Plains1 too (no override)
  R  void respawn: the spawn provider gives the landing; engine bytecode (getRespawnPosition -> getSpawnProvider when no bed, DeathConfig
     default HomeOrSpawnPoint, MIN_ENTITY_Y -32, the death drop rule = World.getDeathConfig() = the world's override first);
     World.getDeathConfig() on the island = NONE; WgApplyLanding on a World stand-in (no change -> no markChanged; a new landing -> the
     world spawn point follows, yaw included; again -> no change)
  P  persistence with the real Universe / InstancesPlugin / filesystem: the first open = the REAL spawnInstance copies the jar's template
     into the scratch universe AND the real Universe.makeWorld builds the world from it (our config, its own return point; its thread
     then dies in a bare JVM - no TimeModule), WgDone records it once; saved-not-loaded = Universe.loadWorld loads the SAME island
     (never addWorld, which refuses a saved world, never spawnInstance, which refuses an existing folder); one shared load future;
     loaded = teleport; a half-made folder is refused; a deleted folder = a fresh island with a WARN; busy marks before the disk checks;
     a creation without a player position never stores a null return point (that config would never decode again); the saved
     config.json keeps the Death override; first opened from an INSTANCE world (review finding 5) the island's own return point = the
     default world's spawn; a loaded world named skywynn_z1 that is not ours (review finding 4: a default config, another
     WorldStructure) = decide 11, never changed by WgApplyLanding / syncLanding / setlanding, named in /zone and /zone info
  O  /zone executed: every refusal line (captured chat), the create / load / teleport paths run up to the engine teleport call (it needs
     a live player) - the loaded island too through teleportPlayerToLoadingInstance (review finding 3); the foreign-world refusal + its
     one WARN; /zone leave off and on an island; /zone list / info texts; WgHereTask / landing action guards; the world-thread
     tasks run from the World stand-in's task queue
  H  commands with the engine's own permission code: /zone, its 4 sub-commands and the /zone <n> variant are admin-only (node + no
     groups); plain players refused, ops and node holders allowed; /zone 1 picks the variant, /zone leave the sub-command
  K  the config kit (Server Setup > World Gen): header, 6 rows, set / refuse (Y off the island's ground too) / read-only / action /
     reload, field + after hook; a hand-edited landing.point + reload moves the loaded island's spawn point at once (finding 3)
  S  the plugin's REAL setup() run twice on a scratch data folder (CommandManager / registries stand-ins): no churn; a PlayerReadyEvent
     through the real EventBus reaches the registered listener (an arrival on the island moves the world spawn to a changed landing)
  E  the REAL command dispatch (CommandManager.handleCommand): every /zone form refused for a plain player by the engine, parsed +
     permitted + scheduled on the player's world for an op (running it needs the live entity store - the offline limit)
  X  every class / member reference passes MethodHandles.Lookup in its own class (the JVM's access rules)
  L  link check: every engine member the jar references exists in the release jar (and, as a note, the 0.7 pre-release jar)
  B  bytecode facts: loadWorld (never addWorld), spawnInstance only in startCreate, no "hub" command, one registerCommand, the
     PlayerReadyEvent listener, the teleport / exit calls (never teleportPlayerToInstance), the island checks, reload -> syncLanding,
     startCreate -> returnWorld
Exit code 1 on any FAIL.
"""
import os, sys, re, json, shutil, zipfile, time, math, collections, functools

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION = "0.1"
PKG = "com.skyy.worldgen."
print = functools.partial(print, flush=True)


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "wg01", "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyWorldGen-%s.jar" % VERSION)))
KEEP = "--keep" in sys.argv
FAILS, OKS = [], [0]
NOTES = []
HY = os.path.join(os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming"), "Hytale", "install")
AZ_PATH = os.path.join(HY, "release", "package", "game", "latest", "Assets.zip")
PRE_JAR = os.path.join(HY, "pre-release", "package", "game", "latest", "Server", "HytaleServer.jar")
assert SCRATCH.lower().startswith(os.path.join(TOOLS, "dev", "scratch").lower() + os.sep), "scratch must be under tools/dev/scratch"


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)
    return cond


# ================================================================= the stage 0 proof report's recipe, typed here independently
R_ = 384
BASE = 140
K_ = 12.0
TOP = [(0, 24), (128, 16), (256, 8), (344, 4), (376, 1), (384, -3)]
DEPTH = [(0, 90), (128, 80), (256, 56), (344, 24), (376, 6), (384, -3)]
TOP_D = [(0, 2), (128, 1.3333), (256, 0.6667), (344, 0.3333), (376, 0.0833), (384, -0.25)]
DEPTH_D = [(0, 7.5), (128, 6.6667), (256, 4.6667), (344, 2), (376, 0.5), (384, -0.25)]
RINGS = {"SkyWynn_Z1S_Core": (-1, 128, "Env_Zone1_Azure", "#2F798A", "#2F868A", 0.3, 13, {"Trees/Azure/Stage_2": 50, "Trees/Azure/Stage_3": 50}),
         "SkyWynn_Z1S_Forest": (128, 256, "Env_Zone1_Forests", "#7f9b1f", "#69970f", 0.4, 11,
                                {"Trees/Birch/Stage_1": 30, "Trees/Birch/Stage_2": 45, "Trees/Birch/Stage_3": 25}),
         "SkyWynn_Z1S_Meadow": (256, 400, "Env_Zone1_Plains", "#639726", "#3b8e32", 0.6, 0, {})}
LANDING = (0.5, 144.0, 344.5)
LANDING_YAW = 0.0               # the recipe wrote 180 (facing the void); the build faces the core (Transform.getDirection(0, 0) = -z)
WORLD = "skywynn_z1"
TEMPLATE = "SkyWynn_Zone1"
STRUCT = "SkyWynn_Z1_Small"
NODE = "skyyworldgen.admin"
EXPECTED_ASSETS = ["Server/HytaleGenerator/Density/SkyWynn_Z1S_Dist.json", "Server/HytaleGenerator/Density/SkyWynn_Z1S_Island.json",
                   "Server/HytaleGenerator/WorldStructures/SkyWynn_Z1_Small.json", "Server/HytaleGenerator/Biomes/SkyWynn/SkyWynn_Void.json",
                   "Server/HytaleGenerator/Biomes/SkyWynn/SkyWynn_Z1S_Core.json", "Server/HytaleGenerator/Biomes/SkyWynn/SkyWynn_Z1S_Forest.json",
                   "Server/HytaleGenerator/Biomes/SkyWynn/SkyWynn_Z1S_Meadow.json", "Server/Instances/SkyWynn_Zone1/instance.bson",
                   "Server/Instances/SkyWynn_Zone1/resources/InstanceData.json"]


def interp(pts, d):
    if d <= pts[0][0]:
        return float(pts[0][1])
    for (a, va), (b, vb) in zip(pts, pts[1:]):
        if d <= b:
            return va + (vb - va) * (d - a) / float(b - a)
    return float(pts[-1][1])


def strip_meta(o):
    if isinstance(o, dict):
        return {k: strip_meta(v) for k, v in o.items() if not k.startswith("$") and k != "Skip"}
    if isinstance(o, list):
        return [strip_meta(x) for x in o]
    return o


def find_nodes(o, typ, out=None):
    out = [] if out is None else out
    if isinstance(o, dict):
        if o.get("Type") == typ:
            out.append(o)
        for v in o.values():
            find_nodes(v, typ, out)
    elif isinstance(o, list):
        for v in o:
            find_nodes(v, typ, out)
    return out


def points(curve):
    return [(p["In"], p["Out"]) for p in curve["Points"]]


def run():
    import jpype
    from jpype import JClass, JArray, JObject, JImplements, JOverride, JInt, JFloat, JLong, JString
    import skyybuild as B
    tmp = os.path.join(SCRATCH, "tmp")
    hcls = os.path.join(SCRATCH, "hclasses")
    os.makedirs(tmp, exist_ok=True)
    os.makedirs(hcls, exist_ok=True)
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   "-Duser.home=" + tmp, classpath=[B.SERVER_JAR, B.JAVASSIST, JAR, hcls], convertStrings=True)
    Cls = JClass("java.lang.Class")
    sysl = JClass("java.lang.ClassLoader").getSystemClassLoader()
    UUID = JClass("java.util.UUID")
    Paths = JClass("java.nio.file.Paths")
    Files = JClass("java.nio.file.Files")
    HashMap, ArrayList = JClass("java.util.HashMap"), JClass("java.util.ArrayList")
    CHM = JClass("java.util.concurrent.ConcurrentHashMap")
    Collections = JClass("java.util.Collections")
    NOLINK = JArray(JClass("java.nio.file.LinkOption"))(0)
    fu = Cls.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
    fu.setAccessible(True)
    U = fu.get(None)

    def jfield(cls, name):
        c = cls if isinstance(cls, Cls) else cls.class_
        while c is not None:
            try:
                f = c.getDeclaredField(name)
                f.setAccessible(True)
                return f
            except Exception:
                c = c.getSuperclass()
        raise KeyError(name)

    def setf(obj, cls, name, val):
        jfield(cls, name).set(obj, val)

    # ---------------- A. load + verify + init
    z = zipfile.ZipFile(JAR)
    names = sorted(n[:-6].replace("/", ".") for n in z.namelist() if n.endswith(".class"))
    na = 0
    for n in names:
        try:
            Cls.forName(n, True, sysl)
            na += 1
        except Exception as e:
            check(False, "A. load %s: %s" % (n, e))
    OKS[0] += na
    print("A. loaded + verified + initialised (-Xverify:all): %d classes" % na)
    if FAILS:
        return

    # ---------------- M. manifest + entries
    man = json.loads(z.read("manifest.json").decode("utf-8"))
    check(man.get("Name") == "%s SkyyWorldGen" % VERSION and man.get("Version") == VERSION and man.get("Main") == PKG + "SkyyWorldGenPlugin"
          and man.get("IncludesAssetPack") is True and man.get("Group") == "Skyy", "M. manifest: %s" % {k: man.get(k) for k in ("Name", "Main", "IncludesAssetPack")})
    entries = z.namelist()
    check(sorted(e for e in entries if e.startswith("Server/")) == sorted(EXPECTED_ASSETS), "M. exactly the 9 asset files: %s" %
          sorted(e for e in entries if e.startswith("Server/")))
    check(not [e for e in entries if e.lower().endswith(".ui")], "M. no .ui files")
    expect_classes = ["SkyyWorldGenPlugin", "WgLog", "WgZones", "WgCfg", "WgStore", "WgCheck", "WgCmds", "WgApplyLanding", "WgOpen", "WgDone",
                      "WgReady", "WgHereTask", "WgHooks", "ZoneCmd", "ZoneGoCmd", "ZoneLeaveCmd", "ZoneInfoCmd", "ZoneLandingCmd", "ZoneReloadCmd",
                      "CfgRows", "CfgLog", "CfgHist", "CfgSaveTask", "CfgFile", "CfgFn", "CfgPub"]
    check(sorted(names) == sorted(PKG + c for c in expect_classes), "M. the class list: %s" % sorted(set(names) ^ set(PKG + c for c in expect_classes)))
    print("M. manifest + %d entries (%d classes, %d assets)" % (len(entries), len(names), len(EXPECTED_ASSETS)))

    # ---------------- J. the recipe (pure JSON of the jar)
    A_ = {p: json.loads(z.read(p).decode("ascii")) for p in EXPECTED_ASSETS}
    dist = A_["Server/HytaleGenerator/Density/SkyWynn_Z1S_Dist.json"]
    check(dist["Type"] == "Exported" and dist["ExportAs"] == "SkyWynn-Z1S-Dist" and dist["SingleInstance"] is True, "J. Dist export")
    warp = find_nodes(dist, "FastGradientWarp")
    check(len(warp) == 1 and warp[0]["WarpFactor"] == 24 and warp[0]["WarpScale"] == 250 and warp[0]["Seed"] == "SkyWynn-Z1"
          and warp[0]["WarpOctaves"] == 1 and warp[0]["WarpPersistence"] == 0.5 and warp[0]["WarpLacunarity"] == 2, "J. warp 24 / 250 / SkyWynn-Z1")
    dn = find_nodes(dist, "Distance")
    check(len(dn) == 1 and points(dn[0]["Curve"]) == [(0, 0), (8000, 8000)], "J. Distance in blocks (identity curve)")
    check(len(find_nodes(dist, "YOverride")) == 2 and find_nodes(dist, "Cache")[0]["Capacity"] == 3, "J. YOverride 0 (2D) + Cache 3")
    isl = A_["Server/HytaleGenerator/Density/SkyWynn_Z1S_Island.json"]
    check(isl["ExportAs"] == "SkyWynn-Z1S-Island" and isl["Inputs"][0]["Type"] == "Min" and len(isl["Inputs"][0]["Inputs"]) == 2, "J. Island = Min(top, bottom)")
    top_sum, bot_sum = isl["Inputs"][0]["Inputs"]
    cm_t = [n for n in top_sum["Inputs"] if n["Type"] == "CurveMapper"]
    cm_b = [n for n in bot_sum["Inputs"] if n["Type"] == "CurveMapper"]
    check(points(cm_t[0]["Curve"]) == [(-400, 33.333), (400, -33.333)] and cm_t[0]["Inputs"][0] == {"Type": "BaseHeight", "BaseHeightName": "Base", "Distance": True},
          "J. top: h -> -h/12")
    check(points(cm_t[1]["Curve"]) == TOP_D and cm_t[1]["Inputs"][0] == {"Type": "Imported", "Name": "SkyWynn-Z1S-Dist"}, "J. top curve = TOP/12: %s" % points(cm_t[1]["Curve"]))
    check(points(cm_b[0]["Curve"]) == [(-400, -33.333), (400, 33.333)], "J. bottom: h -> h/12")
    check(points(cm_b[1]["Curve"]) == DEPTH_D, "J. bottom curve = DEPTH/12: %s" % points(cm_b[1]["Curve"]))
    check(all(abs(b - round(v / K_, 4)) < 1e-9 for (a, b), (_a, v) in zip(TOP_D, TOP)) and all(abs(b - round(v / K_, 4)) < 1e-9 for (a, b), (_a, v) in zip(DEPTH_D, DEPTH)),
          "J. the /12 curves are TOP / DEPTH in blocks (K 12)")
    hn = [n for n in top_sum["Inputs"] if n["Type"] == "Normalizer"][0]
    un = [n for n in bot_sum["Inputs"] if n["Type"] == "Normalizer"][0]
    check(hn["ToMin"] == -0.3 and hn["ToMax"] == 0.3 and hn["Inputs"][0]["Type"] == "SimplexNoise2D" and hn["Inputs"][0]["Scale"] == 70
          and hn["Inputs"][0]["Octaves"] == 2 and hn["Inputs"][0]["Seed"] == "SkyWynn-Z1-Hills", "J. hills noise +-0.3, scale 70")
    check(un["ToMin"] == -0.6 and un["ToMax"] == 0.6 and un["Inputs"][0]["Type"] == "SimplexNoise3D" and un["Inputs"][0]["ScaleXZ"] == 40
          and un["Inputs"][0]["ScaleY"] == 20 and un["Inputs"][0]["Seed"] == "SkyWynn-Z1-Under", "J. underside noise +-0.6, 40 / 20")
    ws = A_["Server/HytaleGenerator/WorldStructures/SkyWynn_Z1_Small.json"]
    check(ws["Type"] == "NoiseRange" and [(b["Biome"], b["Min"], b["Max"]) for b in ws["Biomes"]] ==
          [("SkyWynn_Z1S_Core", -1, 128), ("SkyWynn_Z1S_Forest", 128, 256), ("SkyWynn_Z1S_Meadow", 256, 400), ("SkyWynn_Void", 400, 100000)]
          and ws["DefaultBiome"] == "SkyWynn_Void" and ws["DefaultTransitionDistance"] == 16 and ws["MaxBiomeEdgeDistance"] == 16
          and ws["Density"] == {"Type": "Imported", "Name": "SkyWynn-Z1S-Dist"}, "J. the WorldStructure ranges")
    check(ws["SpawnPositions"] == {"Type": "List", "Positions": [{"X": 0.5, "Y": 144.0, "Z": 344.5}]}, "J. SpawnPositions = the landing")
    check(ws["Framework"] == [{"Type": "DecimalConstants", "Entries": [{"Name": "Base", "Value": 140}, {"Name": "Water", "Value": 140},
                                                                       {"Name": "Bedrock", "Value": 0}]}], "J. Base 140 / Water 140 / Bedrock 0")
    vo = A_["Server/HytaleGenerator/Biomes/SkyWynn/SkyWynn_Void.json"]
    check(vo["Name"] == "SkyWynn_Void" and vo["Terrain"]["Density"] == {"Type": "Constant", "Value": 0} and vo["EnvironmentProvider"]["Environment"] == "Env_Void"
          and vo["MaterialProvider"] == {"Type": "Constant", "Material": {"Solid": "Empty"}}, "J. the void biome")
    for bid, (a, b, env, c1, c2, split, spacing, trees) in RINGS.items():
        bj = A_["Server/HytaleGenerator/Biomes/SkyWynn/%s.json" % bid]
        ok = bj["Name"] == bid and bj["Terrain"]["Density"] == {"Type": "Imported", "Name": "SkyWynn-Z1S-Island"}
        ok = ok and bj["EnvironmentProvider"] == {"Type": "Constant", "Environment": env}
        dl = bj["TintProvider"]["Delimiters"]
        ok = ok and dl[0]["Tint"]["Color"] == c1 and dl[1]["Tint"]["Color"] == c2 and dl[0]["Range"]["MaxExclusive"] == split
        lay = bj["MaterialProvider"]["Solid"]["Queue"][0]["Layers"]
        ok = ok and [(l["Thickness"], l["Material"]["Material"]["Solid"]) for l in lay] == [(1, "Soil_Grass"), (3, "Soil_Dirt")]
        ok = ok and bj["MaterialProvider"]["Solid"]["Queue"][1]["Material"]["Solid"] == "Rock_Stone"
        if trees:
            pr_ = bj["Props"][0]
            ok = ok and pr_["Positions"]["PointGenerator"]["ScaleX"] == spacing and pr_["Assignments"]["Prop"]["Type"] == "Prefab"
            ok = ok and {w["Path"]: w["Weight"] for w in pr_["Assignments"]["Prop"]["WeightedPrefabPaths"]} == trees
        else:
            ok = ok and bj["Props"] == []
        check(ok, "J. biome %s: env %s, tints %s/%s, layers, trees %s" % (bid, env, c1, c2, sorted(trees)))
    inst = A_["Server/Instances/SkyWynn_Zone1/instance.bson"]
    check(inst["Version"] == 4 and inst["Plugin"] == {"Instance": {"RemovalConditions": []}} and "Instance" not in inst, "J. template: codec version 4, Plugin.Instance, no removal")
    check(inst["WorldGen"] == {"Type": "HytaleGenerator", "WorldStructure": STRUCT, "SeedOverride": "SkyWynn-Z1"}, "J. template WorldGen")
    check(inst["SpawnProvider"] == {"Id": "Global", "SpawnPoint": {"X": 0.5, "Y": 144.0, "Z": 344.5, "Pitch": 0.0, "Yaw": LANDING_YAW, "Roll": 0.0}},
          "J. template SpawnProvider = the landing, yaw 0")
    check(inst["DeleteOnRemove"] is False and inst["DeleteOnUniverseStart"] is False and inst["GameMode"] == "Adventure" and inst["IsSpawningNPC"] is True
          and inst["GameplayConfig"] == "Default" and inst["IsSpawnMarkersEnabled"] is True, "J. template flags")
    portal_death = json.loads(zipfile.ZipFile(AZ_PATH).read("Server/GameplayConfigs/Portal.json")).get("Death", {})
    check(inst.get("Death") == {"ItemsLossMode": "None"} and portal_death.get("ItemsLossMode") == "None",
          "J. template: the world's own Death override = no item loss (review finding 1), spelled like vanilla's Portal.json: %s" % inst.get("Death"))
    check(json.loads(z.read("Server/Instances/SkyWynn_Zone1/resources/InstanceData.json")) == {"HadPlayer": False}, "J. InstanceData.json")
    print("J. the recipe: every number, id, seed, env, tint and tree list matches the proof report (landing yaw 0 by decision)")

    # ================================================================= engine stand-ins (proof report: "How to rebuild the harness")
    WORK = os.path.join(SCRATCH, "engine")
    shutil.rmtree(WORK, ignore_errors=True)
    os.makedirs(WORK)
    Options = JClass("com.hypixel.hytale.server.core.Options")
    Options.parse(JArray(JString)(["--universe", os.path.join(WORK, "universe"), "--prefab-cache", os.path.join(WORK, "prefabcache")]))
    HS = JClass("com.hypixel.hytale.server.core.HytaleServer")
    hs = U.allocateInstance(HS.class_)
    bus = JClass("com.hypixel.hytale.event.EventBus")(False)
    setf(hs, HS, "eventBus", bus)
    setf(hs, HS, "shutdown", JClass("java.util.concurrent.atomic.AtomicReference")())
    setf(hs, HS, "booting", JClass("java.util.concurrent.atomic.AtomicBoolean")(False))
    setf(hs, HS, "booted", JClass("java.util.concurrent.atomic.AtomicBoolean")(True))
    jfield(HS, "instance").set(None, hs)
    UNI = JClass("com.hypixel.hytale.server.core.universe.Universe")
    uni = U.allocateInstance(UNI.class_)
    upath = Paths.get(os.path.join(WORK, "universe"))
    setf(uni, UNI, "path", upath)
    setf(uni, UNI, "worldsPath", upath.resolve("worlds"))
    setf(uni, UNI, "worldsDeletedPath", upath.resolve("worlds-deleted"))
    pbu = CHM()
    setf(uni, UNI, "playersByUuid", pbu)
    setf(uni, UNI, "players", Collections.unmodifiableCollection(pbu.values()))
    wmap, wbyu = CHM(), CHM()
    setf(uni, UNI, "worlds", wmap)
    setf(uni, UNI, "worldsByUuid", wbyu)
    setf(uni, UNI, "unmodifiableWorlds", Collections.unmodifiableMap(wmap))
    setf(uni, UNI, "worldConfigProvider", JClass("com.hypixel.hytale.server.core.universe.world.WorldConfigProvider$Default")())
    jfield(UNI, "instance").set(None, uni)
    # log capture: every HytaleLogger record (root subscriber list) + java.util.logging root records
    HLB = JClass("com.hypixel.hytale.logger.backend.HytaleLoggerBackend")
    CAPLOG = JClass("java.util.concurrent.CopyOnWriteArrayList")()
    HLB.subscribe(CAPLOG)
    JULR = []

    @JImplements("java.util.function.Consumer")
    class _Noop:
        @JOverride
        def accept(self, x): pass
    JUL = JClass("java.util.logging.Logger").getLogger("")
    JULH = JClass("java.util.logging.Handler")

    def records():
        out = []
        for r in list(CAPLOG):
            try:
                msg = str(r.getMessage())
                ps = r.getParameters()
                if ps is not None and len(ps) > 0:
                    try:
                        msg = str(JClass("java.lang.String").format(msg, ps))
                    except Exception:
                        msg = msg + " " + " ".join(str(p) for p in ps)
                out.append((str(r.getLevel()), msg))
            except Exception:
                pass
        return out
    JClass("com.hypixel.hytale.server.core.asset.AssetRegistryLoader").init()
    JClass(PKG + "WgLog").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyWorldGen")     # the mod's lines go through the captured logger

    @JImplements("java.util.function.BooleanSupplier")
    class TrueSup:
        @JOverride
        def getAsBoolean(self): return True
    ER = JClass("com.hypixel.hytale.event.EventRegistry")
    er = ER(ArrayList(), TrueSup(), "HG", bus)
    HL = JClass("com.hypixel.hytale.logger.HytaleLogger")
    AMc = JClass("com.hypixel.hytale.builtin.hytalegenerator.assets.AssetManager")
    am = AMc(er, HL.get("HytaleGenerator"))
    AR = JClass("com.hypixel.hytale.assetstore.AssetRegistry")
    sm = AR.getStoreMap()
    az = zipfile.ZipFile(AZ_PATH)
    PREF = os.path.join(WORK, "vanillaprefabs")
    blockids = set(["Soil_Grass", "Soil_Dirt", "Rock_Stone"])
    for n in az.namelist():
        if n.startswith(("Server/Prefabs/Trees/Birch/", "Server/Prefabs/Trees/Azure/")) and n.endswith(".prefab.json"):
            dst = os.path.join(PREF, *n.split("/"))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            data = az.read(n)
            with open(dst, "wb") as f_:
                f_.write(data)
            for b_ in json.loads(data).get("blocks", []):
                if "name" in b_:
                    blockids.add(b_["name"])
    envids = sorted(set(n.rsplit("/", 1)[1][:-5] for n in az.namelist() if n.startswith("Server/Environments/") and n.endswith(".json")))
    BT = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType")
    FL = JClass("com.hypixel.hytale.server.core.asset.type.fluid.Fluid")
    ENV = JClass("com.hypixel.hytale.server.core.asset.type.environment.config.Environment")
    I2O = JClass("it.unimi.dsi.fastutil.ints.Int2ObjectOpenHashMap")

    def load_into(store, items, pack="Hytale:Hytale"):
        l_ = ArrayList()
        for x in items:
            l_.add(x)
        return store.loadAssets(pack, l_)
    bts, fls, evs = BT.getAssetStore(), FL.getAssetStore(), ENV.getAssetStore()
    r1 = load_into(bts, list(bts.getPreAddedAssets()) + [BT(b_) for b_ in sorted(blockids)])
    r2 = load_into(fls, list(fls.getPreAddedAssets()))
    r3 = load_into(evs, list(evs.getPreAddedAssets()) + [ENV(e, None, HashMap(), I2O(), 0.5) for e in envids])
    check(not r1.hasFailed() and not r2.hasFailed() and not r3.hasFailed(), "D. stand-in BlockType (%d ids incl. the tree prefab blocks) / Fluid / "
          "Environment (%d vanilla ids) stores load" % (len(blockids), len(envids)))
    # LegacyModule + BlockTypeModule: the 12 chunk components and BlockPhysics registered on the real ChunkStore.REGISTRY
    CS = JClass("com.hypixel.hytale.server.core.universe.world.storage.ChunkStore")
    LM = JClass("com.hypixel.hytale.server.core.modules.LegacyModule")
    lm = U.allocateInstance(LM.class_)
    P_ = "com.hypixel.hytale.server.core.universe.world.chunk."
    for fld, cn, key in (("worldChunkComponentType", P_ + "WorldChunk", "WorldChunk"), ("blockChunkComponentType", P_ + "BlockChunk", "BlockChunk"),
                         ("entityChunkComponentType", P_ + "EntityChunk", "EntityChunk"),
                         ("blockComponentChunkComponentType", P_ + "BlockComponentChunk", "BlockComponentChunk"),
                         ("environmentChunkComponentType", P_ + "environment.EnvironmentChunk", "EnvironmentChunk"),
                         ("chunkColumnComponentType", P_ + "ChunkColumn", "ChunkColumn"), ("chunkSectionComponentType", P_ + "section.ChunkSection", "ChunkSection"),
                         ("blockSectionComponentType", P_ + "section.BlockSection", "Block"), ("fluidSectionComponentType", P_ + "section.FluidSection", "Fluid"),
                         ("entitySectionComponentType", P_ + "section.EntitySection", "Entity"),
                         ("blockComponentSectionComponentType", P_ + "section.BlockComponentSection", "BlockComponent")):
        C_ = JClass(cn)
        setf(lm, LM, fld, CS.REGISTRY.registerComponent(C_.class_, key, jfield(C_, "CODEC").get(None)))

    @JImplements("java.util.function.Supplier")
    class NullSup:
        @JOverride
        def get(self): return None
    setf(lm, LM, "blockPositionProviderComponentType", CS.REGISTRY.registerComponent(JClass(P_ + "section.blockpositions.BlockPositionProvider").class_, NullSup()))
    jfield(LM, "instance").set(None, lm)
    BTM = JClass("com.hypixel.hytale.server.core.blocktype.BlockTypeModule")
    btm = U.allocateInstance(BTM.class_)
    BPH = JClass("com.hypixel.hytale.server.core.blocktype.component.BlockPhysics")
    setf(btm, BTM, "blockPhysicsComponentType", CS.REGISTRY.registerComponent(BPH.class_, "BlockPhysics", jfield(BPH, "CODEC").get(None)))
    jfield(BTM, "instance").set(None, btm)
    # AssetModule: a vanilla pack (scratch copy of the tree prefab folders) + the mod jar mounted as a zip FileSystem
    FileSystems = JClass("java.nio.file.FileSystems")
    jarpath = Paths.get(JAR)
    zfs = FileSystems.newFileSystem(jarpath, JObject(None, JClass("java.lang.ClassLoader")))
    AP = JClass("com.hypixel.hytale.assetstore.AssetPack")
    PSRC = JClass("com.hypixel.hytale.assetstore.AssetPack$PackSource")
    vpack = AP(Paths.get(PREF), "Hytale:Hytale", Paths.get(PREF), FileSystems.getDefault(), True, None, PSRC.CLASSPATH)
    mpack = AP(jarpath, "Skyy:SkyyWorldGen", zfs.getPath("/"), zfs, True, None, PSRC.MODS)
    AMOD = JClass("com.hypixel.hytale.server.core.asset.AssetModule")
    amod = U.allocateInstance(AMOD.class_)
    packs = ArrayList()
    packs.add(vpack)
    packs.add(mpack)
    setf(amod, AMOD, "assetPacks", packs)
    jfield(AMOD, "instance").set(None, amod)

    # ---------------- D. decode through the real stores (AssetStoreIterator order, every pack)
    v2 = ArrayList()
    for k_ in sm.keySet():
        if "hytalegenerator" in str(k_.getName()):
            v2.add(sm.get(k_))
    it_ = JClass("com.hypixel.hytale.assetstore.iterator.AssetStoreIterator")(v2)
    loaded = {}
    while it_.hasNext():
        st = it_.next()
        if st is None:
            check(False, "D. the store iterator got stuck")
            break
        for pk in (vpack, mpack):
            d_ = pk.getRoot().resolve("Server").resolve(st.getPath())
            if Files.isDirectory(d_, NOLINK):
                res = st.loadAssetsFromDirectory(pk.getName(), d_)
                loaded[str(st.getAssetClass().getSimpleName())] = res
    HGA = "com.hypixel.hytale.builtin.hytalegenerator.assets."
    WSA, DA, BA = JClass(HGA + "worldstructures.WorldStructureAsset"), JClass(HGA + "density.DensityAsset"), JClass(HGA + "biomes.BiomeAsset")
    keys = {nm: sorted(str(x) for x in sm.get(c.class_).getAssetMap().getAssetMap().keySet()) for nm, c in (("WS", WSA), ("D", DA), ("B", BA))}
    check(sorted(loaded) == ["BiomeAsset", "DensityAsset", "WorldStructureAsset"] and not any(r.hasFailed() for r in loaded.values()),
          "D. 3 stores loaded from the jar, none failed: %s" % {k: v.hasFailed() for k, v in loaded.items()})
    check(keys == {"WS": [STRUCT], "D": ["SkyWynn_Z1S_Dist", "SkyWynn_Z1S_Island"], "B": ["SkyWynn_Void", "SkyWynn_Z1S_Core", "SkyWynn_Z1S_Forest", "SkyWynn_Z1S_Meadow"]},
          "D. 1 WorldStructure, 2 Density, 4 Biome assets: %s" % keys)
    exported = jfield(DA, "exportedNodes").get(None)
    check(exported.containsKey("SkyWynn-Z1S-Dist") and exported.containsKey("SkyWynn-Z1S-Island"), "D. both exports in DensityAsset.exportedNodes")
    check(am.getWorldStructureAsset(STRUCT) is not None, "D. the generator's own AssetManager got the structure (LoadedAssetsEvent on the bus)")
    print("D. decode: %s; exports in the static map; the generator's AssetManager holds %s" % (keys, STRUCT))

    # ---------------- V. the generator
    HGc = JClass("com.hypixel.hytale.builtin.hytalegenerator.plugin.HytaleGenerator")
    CONC = JClass("com.hypixel.hytale.builtin.hytalegenerator.plugin.HytaleGenerator$Concurrency")
    hg = U.allocateInstance(HGc.class_)
    setf(hg, HGc, "chunkGenerationSemaphore", JClass("java.util.concurrent.Semaphore")(1))
    setf(hg, HGc, "generators", HashMap())
    setf(hg, HGc, "isShutdown", JClass("java.util.concurrent.atomic.AtomicBoolean")(False))
    setf(hg, HGc, "concurrency", CONC(2, 2, 2))
    setf(hg, HGc, "concurrencyOverride", jfield(HGc, "AUTO_CONCURRENCY").get(None))
    setf(hg, HGc, "assetManager", am)
    jfield(HGc, "INSTANCE").set(None, hg)
    le = HGc.class_.getDeclaredMethod("loadExecutors", CONC.class_)
    le.setAccessible(True)
    le.invoke(hg, CONC(2, 2, 2))
    GP = JClass("com.hypixel.hytale.builtin.hytalegenerator.engine.chunkgenerator.ChunkRequest$GeneratorProfile")
    ggm = HGc.class_.getDeclaredMethod("getGenerator", GP.class_)
    ggm.setAccessible(True)
    SEED = JString("SkyWynn-Z1").hashCode()
    t0 = time.time()
    gen = ggm.invoke(hg, GP(STRUCT, SEED, 0))
    t_struct = time.time() - t0
    check(str(gen.getClass().getSimpleName()) == "StagedChunkGenerator", "V. getGenerator(SkyWynn_Z1_Small) = StagedChunkGenerator: %s" % gen.getClass().getName())
    gfb = ggm.invoke(hg, GP("SkyWynn_No_Such", SEED, 1))
    check(str(gfb.getClass().getSimpleName()) == "FallbackGenerator", "V. an unknown structure = FallbackGenerator (what /zone's guard prevents)")
    Chk = JClass(PKG + "WgCheck")
    check(Chk.structureProblem(0) is None and bool(Chk.OK[0]), "V. WgCheck: the real generator holds the structure -> /zone may open it")
    Chk.OK[0] = False
    jfield(HGc, "INSTANCE").set(None, None)
    sp = str(Chk.structureProblem(0))
    check("not running" in sp and not bool(Chk.OK[0]), "V. WgCheck with no generator: %s" % sp)
    am2 = AMc(ER(ArrayList(), TrueSup(), "HG2", JClass("com.hypixel.hytale.event.EventBus")(False)), HL.get("HytaleGenerator2"))
    hg2 = U.allocateInstance(HGc.class_)
    setf(hg2, HGc, "assetManager", am2)
    jfield(HGc, "INSTANCE").set(None, hg2)
    n_err0 = sum(1 for lv, m in records() if lv == "SEVERE" and "did not reach" in m)
    sp2 = str(Chk.structureProblem(0))
    sp3 = str(Chk.structureProblem(0))
    n_err1 = sum(1 for lv, m in records() if lv == "SEVERE" and "did not reach" in m)
    check("did not load" in sp2 and sp2 == sp3 and n_err1 - n_err0 == 1, "V. WgCheck with an asset map that lacks the structure: refuses, one SEVERE line (%d): %s"
          % (n_err1 - n_err0, sp2))
    jfield(HGc, "INSTANCE").set(None, hg)
    check(Chk.structureProblem(0) is None, "V. WgCheck back on the real generator")
    print("V. generator built in %.2fs; fallback for unknown names; the /zone guard answers all three cases" % t_struct)

    # ---------------- C. chunks
    ARGS = JClass("com.hypixel.hytale.builtin.hytalegenerator.engine.chunkgenerator.ChunkRequest$Arguments")
    CU = JClass("com.hypixel.hytale.math.util.ChunkUtil")

    @JImplements("java.util.function.LongPredicate")
    class AlwaysTrue:
        @JOverride
        def test(self, v): return True

    @JImplements("it.unimi.dsi.fastutil.longs.Long2FloatFunction")
    class Prio:
        @JOverride
        def get(self, k): return 1.0
    AT, PRIO = AlwaysTrue(), Prio()
    btmap, envmap = BT.getAssetMap(), ENV.getAssetMap()
    bcache = {}

    def bname(i):
        i = int(i)
        if i not in bcache:
            a = btmap.getAsset(JInt(i))
            bcache[i] = str(a.getId()) if a is not None else "#%d" % i
        return bcache[i]

    def ename(i):
        a = envmap.getAsset(JInt(int(i)))
        return str(a.getId()) if a is not None else "#%d" % int(i)
    times = []

    def gen_chunk(g, cx, cz, sd=SEED):
        t = time.time()
        c = g.generate(ARGS(sd, CU.indexChunk(cx, cz), cx, cz, AT, PRIO), "High")
        times.append(time.time() - t)
        return c.getBlockChunk()
    ISLAND = ("Soil_Grass", "Soil_Dirt", "Rock_Stone")

    def column(bc, lx, lz):
        """(top island y, bottom island y, block names bottom->top as runs, tree blocks above the top)"""
        top = bot = None
        runs, prev = [], None
        trees = []
        for y in range(0, 320):
            b = bname(bc.getBlock(lx, y, lz))
            if b != prev:
                runs.append((y, b))
                prev = b
            if b in ISLAND:
                if bot is None:
                    bot = y
                top = y
        if top is not None:
            for y in range(top + 1, min(320, top + 40)):
                b = bname(bc.getBlock(lx, y, lz))
                if b != "Empty":
                    trees.append(b)
        return top, bot, runs, trees
    chunks = set()
    for k in range(0, 14):
        chunks.add((0, k))
        chunks.add((-k, 0))
    for k in range(0, 10):
        chunks.add((k, k))
        chunks.add((-k, -k))
    for c_ in ((40, 40), (-25, 3), (13, 13), (0, -14), (-14, 5), (7, -12), (3, 9), (-6, 4), (5, -2)):
        chunks.add(c_)
    cols = []
    for (cx, cz) in sorted(chunks):
        bc = gen_chunk(gen, cx, cz)
        for lx in range(0, 32, 4):
            for lz in range(0, 32, 4):
                bx, bz = cx * 32 + lx, cz * 32 + lz
                d = math.hypot(bx + 0.5, bz + 0.5)
                top, bot, runs, trees = column(bc, lx, lz)
                envt = ename(bc.getEnvironment(lx, top, lz)) if top is not None else None
                envb = ename(bc.getEnvironment(lx, bot, lz)) if bot is not None else None
                tint = "#%06x" % (int(bc.getTint(lx, lz)) & 0xffffff)
                cols.append(dict(bx=bx, bz=bz, d=d, top=top, bot=bot, runs=runs, trees=trees, envt=envt, envb=envb, tint=tint))
    for c in cols:
        c["trunk"] = bool(c["trees"]) and c["trees"][0].startswith("Wood_")
    land_in = [c for c in cols if c["d"] <= R_ - 30]
    trunks = [c for c in land_in if c["trunk"]]
    void_out = [c for c in cols if c["d"] >= R_ + 30]
    check(land_in and all(c["top"] is not None for c in land_in), "C. land on every sampled column within R-30 (%d columns): %s" %
          (len(land_in), [(c["bx"], c["bz"]) for c in land_in if c["top"] is None][:5]))
    check(void_out and all(len(c["runs"]) == 1 and c["runs"][0][1] == "Empty" for c in void_out), "C. not one block on any column from R+30 (%d columns): %s"
          % (len(void_out), [(c["bx"], c["bz"], c["runs"]) for c in void_out if len(c["runs"]) != 1][:3]))
    BANDS = {"Core": (0, 94, "Env_Zone1_Azure", {"#2f798a", "#2f868a"}), "Forest": (162, 222, "Env_Zone1_Forests", {"#7f9b1f", "#69970f"}),
             "Meadow": (290, 350, "Env_Zone1_Plains", {"#639726", "#3b8e32"})}
    ring_stats = {}
    for ring, (lo, hi, env, tints) in BANDS.items():
        rc = [c for c in cols if lo <= c["d"] < hi and c["top"] is not None]
        bad_env = [(c["bx"], c["bz"], c["envt"], c["envb"]) for c in rc if c["envt"] != env or c["envb"] != env]
        check(rc and not bad_env, "C. %s ring: %s on the surface and the underside (%d columns): %s" % (ring, env, len(rc), bad_env[:4]))
        bad_tint = [(c["bx"], c["bz"], c["tint"]) for c in rc if c["tint"] not in tints]
        check(not bad_tint, "C. %s ring grass tints %s: %s" % (ring, sorted(tints), bad_tint[:4]))
        tops, bots = [c["top"] for c in rc], [c["bot"] for c in rc]
        ring_stats[ring] = (min(tops), max(tops), min(bots), max(bots), len(rc))
        tree_cols = [c for c in rc if c["trees"]]
        names_ = set(b for c in tree_cols for b in c["trees"])
        if ring == "Meadow":
            check(not tree_cols, "C. Meadow ring: no trees (%d columns with blocks above the ground)" % len(tree_cols))
        else:
            kind = "Azure" if ring == "Core" else "Birch"
            other = "Birch" if kind == "Azure" else "Azure"
            check(tree_cols and any(kind in b for b in names_) and not any(other in b for b in names_),
                  "C. %s ring: %s trees only (%d of %d columns under a tree; %s)" % (ring, kind, len(tree_cols), len(rc), sorted(names_)[:6]))
    # heights inside the recipe's own bounds: top = Base + TOP(d') + hills (+-0.3 x 12 = 3.6), bottom = Base - DEPTH(d') +- 7.2,
    # d' = the warped distance (within 24 blocks of d - the proof measured at most 15.6)
    bad_h = []
    for c in land_in:
        if c["d"] > 340 or c["trunk"]:
            continue
        span = [c["d"] + s for s in range(-24, 25, 2)]
        tmin = math.floor(BASE + min(interp(TOP, max(0.0, x)) for x in span) - 3.6) - 1
        tmax = math.ceil(BASE + max(interp(TOP, max(0.0, x)) for x in span) + 3.6) + 1
        bmin = math.floor(BASE - max(interp(DEPTH, max(0.0, x)) for x in span) - 7.2) - 1
        bmax = math.ceil(BASE - min(interp(DEPTH, max(0.0, x)) for x in span) + 7.2) + 1
        if not (tmin <= c["top"] <= tmax and bmin <= c["bot"] <= bmax):
            bad_h.append((c["bx"], c["bz"], round(c["d"]), c["top"], c["bot"], round(tmin), round(tmax), round(bmin), round(bmax)))
    check(not bad_h, "C. every island top / underside inside the recipe's bounds (curve +- warp +- noise): %s" % bad_h[:4])
    proof = {"Core": (154, 165, 47, 63), "Forest": (146, 156, 58, 91), "Meadow": (141, 150, 83, 125)}
    for ring, (a, b, c_, d_) in proof.items():
        s = ring_stats[ring]
        check(a - 2 <= s[0] and s[1] <= b + 2 and c_ - 3 <= s[2] and s[3] <= d_ + 3, "C. %s heights near the proof's (top %d-%d, underside %d-%d): top %d-%d, "
              "underside %d-%d" % (ring, a, b, c_, d_, s[0], s[1], s[2], s[3]))
    bad_l = []
    wood_in_soil = [0]
    for c in land_in:
        if c["top"] - c["bot"] < 6 or c["trunk"]:
            continue
        r_ = c["runs"]
        names_by_y = {}
        for i_, (y0, b) in enumerate(r_):
            y1 = r_[i_ + 1][0] if i_ + 1 < len(r_) else 320
            for y in range(y0, y1):
                names_by_y[y] = b
        t = c["top"]
        layer = [names_by_y.get(t - i) for i in range(0, 5)]
        soil = [b for b in layer if not b.startswith("Wood_")]
        if len(soil) == 5:
            ok_l = soil == ["Soil_Grass", "Soil_Dirt", "Soil_Dirt", "Soil_Dirt", "Rock_Stone"]
        else:
            n_d = sum(1 for b in soil if b == "Soil_Dirt")
            ok_l = soil[0] == "Soil_Grass" and soil == ["Soil_Grass"] + ["Soil_Dirt"] * n_d + ["Rock_Stone"] * (len(soil) - 1 - n_d) and n_d <= 3
            wood_in_soil[0] += 1
        if not ok_l:
            bad_l.append((c["bx"], c["bz"], layer))
    check(not bad_l, "C. layers: grass, 3 dirt, then stone (%d thick columns not under a trunk): %s" % (len([c for c in land_in if c["top"] - c["bot"] >= 6 and not c["trunk"]]), bad_l[:3]))
    rings_of_trunks = collections.Counter("Core" if c["d"] < 128 else "Forest" if c["d"] < 256 else "Meadow" for c in trunks)
    check(rings_of_trunks.get("Meadow", 0) == 0 or all(c["d"] < 272 for c in trunks if c["d"] >= 256),
          "C. trunk columns only in the tree rings (a trunk sinks into the ground and replaces the top grass / dirt there): %s" % dict(rings_of_trunks))
    t_first, t_rest = times[0], times[1:]
    print("C. %d chunks, %d columns (%d land, %d void): heights %s; time first %.2fs, then avg %.0f ms, max %.0f ms" % (
        len(chunks), len(cols), len(land_in), len(void_out), {k: v[:4] for k, v in ring_stats.items()}, t_first,
        1000 * sum(t_rest) / len(t_rest), 1000 * max(t_rest)))
    NOTES.append("chunk generation (bare JVM, 2+2+2 threads): first %.2fs incl. building the structure, then avg %.0f ms, max %.0f ms over %d chunks"
                 % (t_first, 1000 * sum(t_rest) / len(t_rest), 1000 * max(t_rest), len(t_rest)))

    # ---------------- G. the landing point
    gcache = {}

    def col_at(bx, bz):
        key = (bx >> 5, bz >> 5)
        if key not in gcache:
            gcache[key] = gen_chunk(gen, key[0], key[1])
        return column(gcache[key], bx & 31, bz & 31)
    tops = {}
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            tops[(dx, 344 + dz)] = col_at(dx, 344 + dz)[0]
    tmax, tmin = max(tops.values()), min(tops.values())
    ly = int(LANDING[1])
    check(tmax is not None and ly - (tmax + 1) >= 0 and ly - (tmin + 1) <= 2, "G. landing Y %d: ground tops %d-%d in the 3x3 -> 0-2 blocks of air under the feet" % (ly, tmin, tmax))
    clear = []
    for dx in range(-3, 4):
        for dz in range(-3, 4):
            t_ = col_at(dx, 344 + dz)
            if t_[3]:
                clear.append((dx, 344 + dz, t_[3][:2]))
    check(not clear, "G. nothing above the ground within 3 blocks of the landing: %s" % clear[:3])
    check(ename(gcache[(0, 10)].getEnvironment(0, tops[(0, 344)], 24)) == "Env_Zone1_Plains", "G. the landing stands in Env_Zone1_Plains (the meadow rim, Tier 1 mobs)")
    print("G. landing (0.5, 144, 344.5): ground %d-%d below it, meadow, clear" % (tmin, tmax))

    # ---------------- G2. the landing.point check against the generated terrain (review finding 2: "0 1 0" was accepted = a void-death loop)
    Zn = JClass(PKG + "WgZones")
    CfgG = JClass(PKG + "WgCfg")
    TD, TH, BS = [float(x) for x in Zn.TOP_D], [float(x) for x in Zn.TOP_H], float(Zn.BASE)
    YB, YA, LMAX = float(CfgG.Y_BELOW), float(CfgG.Y_ABOVE), int(CfgG.LANDING_MAX)
    JTOP = list(zip(TD, TH))
    check(JTOP == [(float(a), float(b)) for a, b in TOP] and BS == BASE and LMAX == R_ - 24
          and all(abs(float(Zn.topAt(d_)) - (BASE + interp(TOP, d_))) < 1e-9 for d_ in (0, 50, 128, 200.5, 300, 344.5, 360, 380, 384, 600)),
          "G2. the Java top curve (WgZones.TOP_D / TOP_H / BASE, topAt) = the recipe's TOP + Base; LANDING_MAX %d" % LMAX)

    def window(d_):
        t_ = BS + interp(JTOP, d_)
        return math.ceil(t_ - YB), math.floor(t_ + YA)
    CPs = JClass("javassist.ClassPool")(False)
    CPs.appendSystemPath()
    CPs.appendClassPath(B.SERVER_JAR)
    scan_c = CPs.makeClass("wgharness.Scan")
    scan_c.addMethod(JClass("javassist.CtNewMethod").make(
        "public static int[] tb(com.hypixel.hytale.server.core.universe.world.worldgen.GeneratedBlockChunk bc, int empty) {\n"
        "  int[] out = new int[2048];\n"
        "  for (int lx = 0; lx < 32; lx++) for (int lz = 0; lz < 32; lz++) {\n"
        "    int top = -1; int bot = -1;\n"
        "    for (int y = 0; y < 320; y++) { if (bc.getBlock(lx, y, lz) != empty) { if (bot < 0) bot = y; top = y; } }\n"
        "    out[(lx * 32 + lz) * 2] = top; out[(lx * 32 + lz) * 2 + 1] = bot;\n"
        "  }\n  return out;\n}", scan_c))
    scan_c.writeFile(hcls)
    Scan = JClass("wgharness.Scan")
    empty_id = int(btmap.getIndex("Empty"))
    r_lo, r_hi = LMAX - 40, LMAX + 10
    rchunks = set()
    for cx in range(-14, 14):
        for cz in range(-14, 14):
            ccx, ccz = abs(cx * 32 + 16), abs(cz * 32 + 16)
            if math.hypot(ccx + 16, ccz + 16) >= r_lo and math.hypot(max(0, ccx - 16), max(0, ccz - 16)) <= r_hi:
                rchunks.add((cx, cz))
    t_g2 = time.time()
    ring = []                    # (d, bx, bz, top, bottom) - every column of the ring; the rim is treeless meadow, so top = the grass
    for (cx, cz) in sorted(rchunks):
        tb_ = list(Scan.tb(gen_chunk(gen, cx, cz), empty_id))
        for lx in range(32):
            for lz in range(32):
                bx, bz = cx * 32 + lx, cz * 32 + lz
                d = math.hypot(bx + 0.5, bz + 0.5)
                if r_lo <= d <= r_hi:
                    ring.append((d, bx, bz, tb_[(lx * 32 + lz) * 2], tb_[(lx * 32 + lz) * 2 + 1]))
    t_g2 = time.time() - t_g2
    void_near = [r for r in ring if r[3] < 0 and r[0] <= LMAX + 4]
    min_void = min([r[0] for r in ring if r[3] < 0] or [9999.0])
    check(len(ring) > 50000 and not void_near, "G2. land under EVERY column within LANDING_MAX + 4 = %d (%d ring columns, %d chunks; the nearest void column is %.1f "
          "blocks out): %s" % (LMAX + 4, len(ring), len(rchunks), min_void, void_near[:3]))
    land_cols = [(r[0], r[1], r[2], r[3], r[4]) for r in ring if r[3] >= 0 and r[0] <= LMAX]
    land_cols += [(c["d"], c["bx"], c["bz"], c["top"], c["bot"]) for c in cols if c["top"] is not None and not c["trunk"] and not c["trees"] and c["d"] <= LMAX]
    devs = [r[3] - (BS + interp(JTOP, r[0])) for r in land_cols]
    bad_ok = [(r[1], r[2], round(r[0], 1), r[3], window(r[0])) for r in land_cols if not (window(r[0])[0] <= r[3] + 2 <= window(r[0])[1])]
    bad_void = [(r[1], r[2], round(r[0], 1), r[4], window(r[0])) for r in land_cols if r[4] - 1 >= window(r[0])[0]]
    check(land_cols and not bad_ok, "G2. every land column within LANDING_MAX (%d): ground + 2 (what /zone setlanding writes) is inside the Y window (ground = the "
          "curve %+.1f .. %+.1f; window -%g / +%g): %s" % (len(land_cols), min(devs), max(devs), YB, YA, bad_ok[:3]))
    check(not bad_void, "G2. ... and a Y just under the island (the void) is below the window everywhere: %s" % bad_void[:3])
    srt = sorted(land_cols, key=lambda r: r[3] - (BS + interp(JTOP, r[0])))
    sample = srt[:25] + srt[-25:] + land_cols[::40]
    jbad = []
    for r in sample:
        ok_ = CfgG.landingCheck(CfgG.parseLanding("%s %d %s 0" % (r[1] + 0.5, r[3] + 2, r[2] + 0.5)), 0)
        no_ = CfgG.landingCheck(CfgG.parseLanding("%s %d %s 0" % (r[1] + 0.5, r[4] - 1, r[2] + 0.5)), 0)
        if ok_ is not None or no_ is None or "not on the island's ground" not in str(no_):
            jbad.append((r[1], r[2], r[3], r[4], ok_, no_))
    check(not jbad, "G2. the real WgCfg.landingCheck agrees on %d columns (the 25 lowest + 25 highest ground and every 40th): %s" % (len(sample), jbad[:2]))
    under = min((BS + interp(JTOP, r[0])) - r[4] for r in land_cols)
    print("G2. landing check vs the terrain: %d ring columns (%.1fs), no void within %.1f blocks; %d land columns, ground = curve %+.2f .. %+.2f, "
          "underside at least %.1f under the curve; window -%g / +%g holds" % (len(ring), t_g2, min_void, len(land_cols), min(devs), max(devs), under, YB, YA))

    # ---------------- T. determinism
    b1 = gen_chunk(gen, 5, 5)
    gen_b = ggm.invoke(hg, GP(STRUCT, SEED, 7))
    b2 = gen_chunk(gen_b, 5, 5)
    gen_c = ggm.invoke(hg, GP(STRUCT, JString("SkyWynn-Other").hashCode(), 8))
    b3 = gen_chunk(gen_c, 5, 5, JString("SkyWynn-Other").hashCode())
    same, diff, n_ = True, 0, 0
    for lx in range(0, 32, 2):
        for lz in range(0, 32, 2):
            for y in range(40, 200):
                n_ += 1
                a1, a2, a3 = int(b1.getBlock(lx, y, lz)), int(b2.getBlock(lx, y, lz)), int(b3.getBlock(lx, y, lz))
                if a1 != a2:
                    same = False
                if a1 != a3:
                    diff += 1
    check(same, "T. the same SeedOverride gives identical blocks from a fresh generator (%d blocks compared)" % n_)
    check(diff > 0, "T. another seed gives different terrain (%d of %d blocks differ)" % (diff, n_))
    print("T. determinism: identical %d blocks; another seed differs in %d" % (n_, diff))

    # ---------------- W. the instance template through WorldConfig.CODEC
    ISP = JClass("com.hypixel.hytale.server.core.universe.world.spawn.ISpawnProvider")
    GSP = JClass("com.hypixel.hytale.server.core.universe.world.spawn.GlobalSpawnProvider")
    ISP.CODEC.register("Global", GSP.class_, GSP.CODEC)
    IWG = JClass("com.hypixel.hytale.server.core.universe.world.worldgen.provider.IWorldGenProvider")
    HP = JClass("com.hypixel.hytale.builtin.hytalegenerator.plugin.HandleProvider")
    BC = JClass("com.hypixel.hytale.codec.builder.BuilderCodec")
    KC = JClass("com.hypixel.hytale.codec.KeyedCodec")
    Codec = JClass("com.hypixel.hytale.codec.Codec")

    @JImplements("java.util.function.Supplier")
    class HPSup:
        @JOverride
        def get(self): return HP(hg, 0)

    @JImplements("java.util.function.BiConsumer")
    class SetWS:
        @JOverride
        def accept(self, o, v): o.setWorldStructureName(v)

    @JImplements("java.util.function.Function")
    class GetWS:
        @JOverride
        def apply(self, o): return o.getWorldStructureName()

    @JImplements("java.util.function.BiConsumer")
    class SetSeed:
        @JOverride
        def accept(self, o, v): o.setSeedOverride(v)

    @JImplements("java.util.function.Function")
    class GetSeed:
        @JOverride
        def apply(self, o): return o.getSeedOverride()
    hb = BC.builder(HP.class_, HPSup())
    hb = hb.append(KC("WorldStructure", Codec.STRING, False), SetWS(), GetWS()).add()
    hb = hb.append(KC("SeedOverride", Codec.STRING, False), SetSeed(), GetSeed()).add()
    IWG.CODEC.register("HytaleGenerator", HP.class_, hb.build())
    PRI = JClass("com.hypixel.hytale.codec.lookup.Priority")
    ICS = JClass("com.hypixel.hytale.server.core.universe.world.storage.provider.IChunkStorageProvider")
    DCS = JClass("com.hypixel.hytale.server.core.universe.world.storage.provider.DefaultChunkStorageProvider")
    ICS.CODEC.register(PRI.DEFAULT, "Hytale", DCS.class_, DCS.CODEC)
    IRS = JClass("com.hypixel.hytale.server.core.universe.world.storage.resources.IResourceStorageProvider")
    DRS = JClass("com.hypixel.hytale.server.core.universe.world.storage.resources.DefaultResourceStorageProvider")
    IRS.CODEC.register(PRI.DEFAULT, "Hytale", DRS.class_, DRS.CODEC)
    IWM = JClass("com.hypixel.hytale.server.core.universe.world.worldmap.provider.IWorldMapProvider")
    WGM = JClass("com.hypixel.hytale.server.core.universe.world.worldmap.provider.chunk.WorldGenWorldMapProvider")
    IWM.CODEC.register(PRI.DEFAULT, "WorldGen", WGM.class_, WGM.CODEC)
    # the two respawn controllers AssetModule.setup registers (the Death override encodes its RespawnController when config.json is saved)
    RSC = JClass("com.hypixel.hytale.server.core.asset.type.gameplay.respawn.RespawnController")
    for nm in ("HomeOrSpawnPoint", "WorldSpawnPoint"):
        C_ = JClass("com.hypixel.hytale.server.core.asset.type.gameplay.respawn." + nm)
        RSC.CODEC.register(nm, C_.class_, C_.CODEC)
    WC = JClass("com.hypixel.hytale.server.core.universe.world.WorldConfig")
    IWC = JClass("com.hypixel.hytale.builtin.instances.config.InstanceWorldConfig")
    WC.PLUGIN_CODEC.register(IWC.class_, "Instance", IWC.CODEC)
    RC = JClass("com.hypixel.hytale.builtin.instances.removal.RemovalCondition")
    for nm, cn in (("WorldEmpty", "WorldEmptyCondition"), ("IdleTimeout", "IdleTimeoutCondition"), ("Timeout", "TimeoutCondition")):
        C_ = JClass("com.hypixel.hytale.builtin.instances.removal." + cn)
        RC.CODEC.register(nm, C_.class_, C_.CODEC)
    GPC = JClass("com.hypixel.hytale.server.core.asset.type.gameplay.GameplayConfig")
    gpl = []
    for gid in ("Default", "Default_Instance", "Portal"):
        g_ = GPC()
        setf(g_, GPC, "id", gid)
        gpl.append(g_)
    check(not load_into(GPC.getAssetStore(), gpl).hasFailed(), "W. id-only GameplayConfig stand-ins (Default, Default_Instance, Portal) load")
    tdir = os.path.join(WORK, "templates")
    os.makedirs(tdir, exist_ok=True)
    tp = os.path.join(tdir, "instance.bson")
    with open(tp, "wb") as f_:
        f_.write(z.read("Server/Instances/SkyWynn_Zone1/instance.bson"))
    n_log0 = len(records())
    cfg = WC.load(Paths.get(tp)).join()
    wlog = [m for lv, m in records()[n_log0:] if lv in ("WARNING", "SEVERE")]
    hp_ = cfg.getWorldGenProvider()
    check(str(hp_.getClass().getSimpleName()) == "HandleProvider" and str(hp_.getWorldStructureName()) == STRUCT and str(hp_.getSeedOverride()) == "SkyWynn-Z1",
          "W. WorldGen = HandleProvider(%s, SeedOverride SkyWynn-Z1)" % STRUCT)
    spv = cfg.getSpawnProvider()
    ptf = spv.getSpawnPoint(JObject(None, JClass("com.hypixel.hytale.server.core.universe.world.World")), UUID.randomUUID())
    pos, rot = ptf.getPosition(), ptf.getRotation()
    check(str(spv.getClass().getSimpleName()) == "GlobalSpawnProvider" and (pos.x(), pos.y(), pos.z()) == LANDING and abs(rot.yaw()) < 1e-6 and abs(rot.pitch()) < 1e-6,
          "W. SpawnProvider = GlobalSpawnProvider at the landing, yaw 0: %s %s" % ((pos.x(), pos.y(), pos.z()), (rot.pitch(), rot.yaw(), rot.roll())))
    check(str(cfg.getGameMode()) == "Adventure" and bool(cfg.isSpawningNPC()) and str(cfg.getGameplayConfig()) == "Default"
          and not bool(cfg.isDeleteOnRemove()) and not bool(cfg.isDeleteOnUniverseStart()) and str(cfg.getDisplayName()) == "Zone 1 - Emerald Wilds",
          "W. Adventure, NPC spawning, GameplayConfig Default, kept on remove + universe start, display name")
    iw = IWC.get(cfg)
    check(iw is not None and len(iw.getRemovalConditions()) == 0, "W. Plugin.Instance decoded: RemovalConditions = [] (the world never unloads on its own)")
    check(not [m for m in wlog if "SkyWynn" in m or "nstance" in m or "eprecat" in m or "Death" in m or "Respawn" in m or "ItemsLoss" in m],
          "W. no warning while decoding the template: %s" % wlog[:3])
    dco = cfg.getDeathConfigOverride()
    d_def = json.loads(az.read("Server/GameplayConfigs/Default.json"))["Death"]
    check(dco is not None and str(dco.getClass().getSimpleName()) == "MutableDeathConfig" and str(dco.getItemsLossMode()) == "NONE"
          and str(dco.getRespawnController().getClass().getSimpleName()) == "HomeOrSpawnPoint"
          and float(dco.getItemsDurabilityLossPercentage()) == float(d_def["ItemsDurabilityLossPercentage"]) and dco.getGameModeTypeOnDeath() is None,
          "W. the template's Death override (finding 1): ItemsLossMode NONE, respawn HomeOrSpawnPoint (as before), durability loss %s%% = Default.json's, "
          "no death game mode: %s" % (d_def["ItemsDurabilityLossPercentage"], None if dco is None else (str(dco.getItemsLossMode()),
                                                                                                         str(dco.getRespawnController()), dco.getItemsDurabilityLossPercentage())))
    vp = os.path.join(tdir, "zone1plains.bson")
    with open(vp, "wb") as f_:
        f_.write(az.read("Server/Instances/Regions/Zone1_Plains1/instance.bson"))
    vcfg = WC.load(Paths.get(vp)).join()
    vsp = vcfg.getSpawnProvider().getSpawnPoint(JObject(None, JClass("com.hypixel.hytale.server.core.universe.world.World")), UUID.randomUUID()).getPosition()
    check(str(vcfg.getWorldGenProvider().getWorldStructureName()) == "Zone1_Plains1" and (vsp.x(), vsp.y(), vsp.z()) == (0.5, 200.0, 0.5),
          "W. control: vanilla Zone1_Plains1/instance.bson decodes the same way")
    check(vcfg.getDeathConfigOverride() is None, "W. control: vanilla Zone1_Plains1 has no Death override (its GameplayConfig decides)")
    print("W. template decodes: HandleProvider %s / SkyWynn-Z1, Global spawn %s yaw 0, no removal conditions" % (STRUCT, (pos.x(), pos.y(), pos.z())))

    # ---------------- R. void respawn = the landing
    CPj = JClass("javassist.ClassPool")(False)
    CPj.appendSystemPath()
    CPj.appendClassPath(B.SERVER_JAR)
    CPj.appendClassPath(JAR)
    IPr = JClass("javassist.bytecode.InstructionPrinter")

    def code_of(cls, meth, sig=None):
        out = ""
        cc = CPj.get(cls)
        ms = list(cc.getDeclaredMethods()) + (list(cc.getDeclaredConstructors()) if meth == "<init>" else [])
        for mm in ms:
            nm_ = "<init>" if meth == "<init>" and not hasattr(mm, "getReturnType") else str(mm.getName())
            if (str(mm.getName()) == meth or (meth == "<init>" and str(mm.getMethodInfo().getName()) == "<init>")) and (sig is None or sig in str(mm.getSignature())):
                mi = mm.getMethodInfo()
                it2 = mi.getCodeAttribute().iterator()
                while it2.hasNext():
                    p_ = it2.next()
                    out += str(IPr.instructionString(it2, p_, mi.getConstPool())) + "\n"
        return out
    grp = code_of("com.hypixel.hytale.server.core.entity.entities.Player", "getRespawnPosition")
    check("getRespawnPoints" in grp and "WorldConfig.getSpawnProvider" in grp and "ISpawnProvider.getSpawnPoint" in grp,
          "R. engine: Player.getRespawnPosition = a bed / respawn point in that world, else the world's spawn provider")
    check("HomeOrSpawnPoint.INSTANCE" in code_of("com.hypixel.hytale.server.core.asset.type.gameplay.DeathConfig", "<init>")
          and "Player.getRespawnPosition" in code_of("com.hypixel.hytale.server.core.asset.type.gameplay.respawn.HomeOrSpawnPoint", "respawnPlayer"),
          "R. engine: DeathConfig defaults to HomeOrSpawnPoint, which uses getRespawnPosition")
    dj = json.loads(az.read("Server/GameplayConfigs/Default.json"))
    check(set(dj.get("Death", {})) <= {"ItemsLossMode", "ItemsAmountLossPercentage", "ItemsDurabilityLossPercentage"},
          "R. GameplayConfigs/Default.json keeps the default respawn rule (Death sets only item loss: %s)" % dj.get("Death"))
    check(int(jfield(CU, "MIN_ENTITY_Y").get(None)) == -32, "R. engine: entities die below y -32 (the void)")
    WLD = JClass("com.hypixel.hytale.server.core.universe.world.World")
    AB = JClass("java.util.concurrent.atomic.AtomicBoolean")
    DEQ = JClass("java.util.concurrent.ConcurrentLinkedDeque")

    def world_stub(name, config, alive=True):
        w_ = U.allocateInstance(WLD.class_)
        setf(w_, WLD, "name", name)
        setf(w_, WLD, "worldConfig", config)
        setf(w_, WLD, "alive", AB(alive))
        setf(w_, WLD, "acceptingTasks", AB(True))
        setf(w_, WLD, "taskQueue", DEQ())
        return w_

    def drain(w_):
        q = jfield(WLD, "taskQueue").get(w_)
        n_r = 0
        while not q.isEmpty():
            q.poll().run()
            n_r += 1
        return n_r
    Cfg = JClass(PKG + "WgCfg")
    AL = JClass(PKG + "WgApplyLanding")
    zw = world_stub(WORLD, WC.load(Paths.get(tp)).join())
    zc = zw.getWorldConfig()
    zc.consumeHasChanged()
    ap0 = int(AL.APPLIED)
    check(not bool(AL.applyTo(zw)) and not bool(zc.consumeHasChanged()) and int(AL.APPLIED) == ap0,
          "R. WgApplyLanding: the template's spawn point already IS the landing -> nothing written (no markChanged)")
    Cfg.LANDING = "10.5 150 300.5 90"
    check(bool(AL.applyTo(zw)) and bool(zc.consumeHasChanged()) and int(AL.APPLIED) == ap0 + 1, "R. a new landing -> the world spawn point is replaced + markChanged")
    np_ = zc.getSpawnProvider().getSpawnPoint(zw, UUID.randomUUID())
    check(str(zc.getSpawnProvider().getClass().getSimpleName()) == "GlobalSpawnProvider" and (np_.getPosition().x(), np_.getPosition().y(), np_.getPosition().z())
          == (10.5, 150.0, 300.5) and abs(np_.getRotation().yaw() - math.pi / 2) < 1e-5, "R. ... at (10.5, 150, 300.5), yaw 90 degrees = pi/2 radians")
    check(not bool(AL.applyTo(zw)) and not bool(zc.consumeHasChanged()), "R. applying again changes nothing")
    other = world_stub("default", WC.load(Paths.get(vp)).join())
    check(not bool(AL.applyTo(other)), "R. WgApplyLanding never touches a world that is not a zone island")
    Cfg.LANDING = "0.5 144 344.5 0"
    AL(zw).run()
    p2 = zc.getSpawnProvider().getSpawnPoint(zw, UUID.randomUUID()).getPosition()
    check((p2.x(), p2.y(), p2.z()) == LANDING, "R. the task (run on the world thread) puts the default landing back")
    # deaths keep items (finding 1): the engine's own World.getDeathConfig() on the island = the override; the drop rule reads only that
    zdc = zw.getDeathConfig()
    check(zdc is not None and str(zdc.getItemsLossMode()) == "NONE" and zdc == zw.getWorldConfig().getDeathConfigOverride(),
          "R. engine: World.getDeathConfig() on the island = the template's override, ItemsLossMode NONE (a death drops nothing)")
    pdc = code_of("com.hypixel.hytale.server.core.modules.entity.damage.DeathSystems$PlayerDropItemsConfig", "onComponentAdded")
    wdc = code_of("com.hypixel.hytale.server.core.universe.world.World", "getDeathConfig")
    check("World.getDeathConfig" in pdc and "DeathComponent.setItemsLossMode" in pdc and "GameplayConfig" not in pdc
          and 0 <= wdc.find("getDeathConfigOverride") < wdc.find("GameplayConfig.getDeathConfig"),
          "R. engine: the death drop rule (DeathSystems$PlayerDropItemsConfig) comes only from World.getDeathConfig(), which takes the world's "
          "override before the GameplayConfig")
    dpd = code_of("com.hypixel.hytale.server.core.modules.entity.damage.DeathSystems$DropPlayerDeathItems", "onComponentAdded")
    check("InventoryUtils.dropAllItemStacks" in dpd and "getItemsAmountLossPercentage" in dpd and "DeathComponent.getItemsLossMode" in dpd,
          "R. engine: DropPlayerDeathItems drops by the death component's loss mode (All = everything, Configured = a share; None = nothing)")
    print("R. respawn: no bed -> the world's spawn provider = the landing; WgApplyLanding keeps it in step without churn; deaths keep items")

    # ---------------- chat capture: a PacketHandler subclass made here (javassist) that records every ServerMessage
    CPh = JClass("javassist.ClassPool")(False)
    CPh.appendSystemPath()
    CPh.appendClassPath(B.SERVER_JAR)
    CtNM = JClass("javassist.CtNewMethod")
    ph = CPh.makeClass("wgharness.CapturePH", CPh.get("com.hypixel.hytale.server.core.io.PacketHandler"))
    ph.addField(JClass("javassist.CtField").make("public static final java.util.List CAP = java.util.Collections.synchronizedList(new java.util.ArrayList());", ph))
    ph.addMethod(CtNM.make("public void accept(com.hypixel.hytale.protocol.ToServerPacket p) { }", ph))
    ph.addMethod(CtNM.make("public String getIdentifier() { return \"wg-harness\"; }", ph))
    ph.addMethod(CtNM.make("public void writeNoCache(com.hypixel.hytale.protocol.ToClientPacket p) { CAP.add(p); }", ph))
    ph.writeFile(hcls)
    lk = CPh.makeClass("wgharness.LookupIn")
    lk.addMethod(CtNM.make("public static java.lang.invoke.MethodHandles$Lookup lookupIn(java.lang.Class c) throws java.lang.Exception {\n"
                           "  return java.lang.invoke.MethodHandles.privateLookupIn(c, java.lang.invoke.MethodHandles.lookup());\n}", lk))
    lk.writeFile(hcls)
    CPHc = JClass("wgharness.CapturePH")
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")

    def player_stub(name, world_uuid=None):
        p_ = U.allocateInstance(PRc.class_)
        setf(p_, PRc, "uuid", UUID.nameUUIDFromBytes(name.encode("utf-8")))
        setf(p_, PRc, "username", name)
        setf(p_, PRc, "packetHandler", U.allocateInstance(CPHc.class_))
        if world_uuid is not None:
            setf(p_, PRc, "worldUuid", world_uuid)
        setf(p_, PRc, "holder", U.allocateInstance(JClass("com.hypixel.hytale.component.Holder").class_))
        return p_

    def chat():
        out = []
        cap = CPHc.CAP
        for p_ in list(cap):
            fm = p_.message
            out.append((str(fm.rawText) if fm.rawText is not None else (str(fm.messageId) if fm.messageId is not None else ""),
                        str(fm.color) if fm.color is not None else ""))
        cap.clear()
        return out
    pr = player_stub("WgAdmin")
    Cmds = JClass(PKG + "WgCmds")
    Cmds.tell(pr, "+[Zone] hello")
    cl = chat()
    check(cl == [("[Zone] hello", "#39f493")], "O. chat capture works (success colour from the kit): %s" % cl)

    # ---------------- P. persistence with the real Universe / InstancesPlugin / filesystem
    INS = JClass("com.hypixel.hytale.builtin.instances.InstancesPlugin")
    PBASE = JClass("com.hypixel.hytale.server.core.plugin.PluginBase")
    ins = U.allocateInstance(INS.class_)
    setf(ins, INS, "pendingSpawns", CHM())
    setf(ins, PBASE, "logger", HL.get("Instances"))
    setf(uni, PBASE, "logger", HL.get("Universe"))
    jfield(INS, "instance").set(None, ins)
    Open = JClass(PKG + "WgOpen")
    Store = JClass(PKG + "WgStore")
    wgdata = os.path.join(SCRATCH, "data", "mods", "Skyy_SkyyWorldGen")
    os.makedirs(wgdata, exist_ok=True)
    Cfg.DIR = Paths.get(wgdata)
    Cfg.FILE = Paths.get(os.path.join(wgdata, "config.properties"))
    Store.FILE = Paths.get(os.path.join(wgdata, "worlds.properties"))
    Cfg.load()
    Store.read()
    worlds_dir = os.path.join(WORK, "universe", "worlds")
    hub = world_stub("default", vcfg)
    check(INS.doesInstanceAssetExist(TEMPLATE) and bool(Chk.templateOk(0)), "P. the template resolves from the jar pack (InstancesPlugin.getInstanceAssetPath)")
    check(int(Open.decide(0, hub)) == 4, "P. first open, nothing on disk: decide = 4 (create)")
    Cfg.ON = False
    check(int(Open.decide(0, hub)) == 9, "P. Zone islands off: decide = 9 (refuse)")
    Cfg.ON = True
    TRF = JClass("com.hypixel.hytale.math.vector.Transform")
    TU = JClass("java.util.concurrent.TimeUnit")

    def files_of(world):
        root_ = os.path.join(worlds_dir, world)
        return sorted(os.path.relpath(os.path.join(dp, f_), root_).replace(os.sep, "/") for dp, _dn, fns in os.walk(root_) for f_ in fns)

    def settle(timeout=20):
        """the engine really builds the world (World + its thread); in a bare JVM that thread then dies (no TimeModule / EntityModule).
        Wait for our marks to clear and the engine world to stop, then forget it - the folder stays: the 'saved, not loaded' state"""
        t_end = time.time() + timeout
        while time.time() < t_end:
            w_ = uni.getWorld(WORLD)
            if not Open.CREATING.containsKey(WORLD) and Open.loadingFor(WORLD) is None and (w_ is None or not w_.isAlive()):
                break
            time.sleep(0.1)
        w_ = uni.getWorld(WORLD)
        if w_ is not None:
            wmap.remove(WORLD)
            try:
                wbyu.remove(w_.getWorldConfig().getUuid())
            except Exception:
                pass
        time.sleep(0.3)
        return w_

    def ours(cfg_):
        hp2 = cfg_.getWorldGenProvider()
        sp_ = cfg_.getSpawnProvider().getSpawnPoint(JObject(None, WLD), UUID.randomUUID()).getPosition()
        iw2 = IWC.get(cfg_)
        dco_ = cfg_.getDeathConfigOverride()
        return (str(hp2.getClass().getSimpleName()) == "HandleProvider" and str(hp2.getWorldStructureName()) == STRUCT and str(hp2.getSeedOverride()) == "SkyWynn-Z1"
                and (sp_.x(), sp_.y(), sp_.z()) == LANDING and iw2 is not None and len(iw2.getRemovalConditions()) == 0
                and dco_ is not None and str(dco_.getItemsLossMode()) == "NONE")

    # 1. the FIRST open: the real spawnInstance copies the jar's template and the real Universe.makeWorld builds the world
    sp0 = int(Open.SPAWNS)
    n_log0 = len(records())
    fut = Open.startCreate(0, hub, TRF(1.0, 100.0, 2.0), pr)
    check(fut is not None and int(Open.SPAWNS) == sp0 + 1 and Open.CREATING.containsKey(WORLD), "P. startCreate called the REAL InstancesPlugin.spawnInstance once; "
          "the CREATING mark is set while it runs")
    check(int(Open.decide(0, hub)) in (1, 5), "P. while it is being made: decide = busy (5) (or 1 once registered) - never a second create, never a load race")
    try:
        made = fut.get(60, TU.SECONDS)
    except Exception as ex_:
        made = None
        print("   (the creation future failed: %s)" % str(ex_)[:300])
    t_end = time.time() + 10
    while Open.CREATING.containsKey(WORLD) and time.time() < t_end:
        time.sleep(0.05)
    check(made is not None and str(made.getClass().getSimpleName()) == "World" and str(made.getName()) == WORLD,
          "P. the engine made the world from the template: World '%s'" % (made.getName() if made is not None else None))
    if made is not None:
        mc = made.getWorldConfig()
        rp = IWC.get(mc).getReturnPoint()
        check(ours(mc) and str(IWC.get(mc).getInstanceName()) == TEMPLATE, "P. ... with our config: HandleProvider %s / SkyWynn-Z1, spawn = the landing, instance %s, no removal" % (STRUCT, TEMPLATE))
        check(rp is not None and str(rp.getWorld()) == str(vcfg.getUuid()), "P. ... the world's own return point = where it was opened from (the engine's exit fallback)")
    cf_ = files_of(WORLD)
    check("instance.bson" in cf_ and "resources/InstanceData.json" in cf_ and "config.json" in cf_, "P. universe/worlds/%s holds the copied template + the engine's config.json: %s" % (WORLD, cf_))
    check(open(os.path.join(worlds_dir, WORLD, "instance.bson"), "rb").read() == z.read("Server/Instances/SkyWynn_Zone1/instance.bson"), "P. ... instance.bson byte-identical to the jar's")
    check(ours(WC.load(Paths.get(os.path.join(worlds_dir, WORLD, "config.json"))).join()), "P. ... and the saved config.json decodes back to our island")
    try:
        cj = json.loads(open(os.path.join(worlds_dir, WORLD, "config.json"), encoding="utf-8").read())
    except Exception as ex_:
        cj = {"error": str(ex_)}
    check(cj.get("Death", {}).get("ItemsLossMode") == "None" and cj.get("GameplayConfig") == "Default",
          "P. ... the engine wrote the Death override into config.json (no item loss, kept for good) next to GameplayConfig Default: %s" % cj.get("Death", cj.get("error")))
    wtxt = open(os.path.join(wgdata, "worlds.properties"), encoding="latin-1").read() if os.path.isfile(os.path.join(wgdata, "worlds.properties")) else ""
    check(not Open.CREATING.containsKey(WORLD) and Store.created(WORLD) > 0 and "skywynn_z1.template=SkyWynn_Zone1" in wtxt
          and "skywynn_z1.structure=SkyWynn_Z1_Small" in wtxt and "skywynn_z1.by=0.1" in wtxt, "P. WgDone (success path): CREATING cleared, the world recorded once in worlds.properties")
    check(len([m for lv, m in records()[n_log0:] if "Copying instance files for SkyWynn_Zone1 to world skywynn_z1" in m]) == 1, "P. the engine copied the template exactly once")
    check(uni.getWorld(WORLD) is not None, "P. the engine registered the world in the Universe (later trips find it loaded)")
    chat()
    settle()
    # 2. saved, not loaded (a restart / an unload): reopen = Universe.loadWorld, never spawnInstance, never addWorld
    check(bool(uni.isWorldLoadable(WORLD)) and int(Open.decide(0, hub)) == 3, "P. saved, not loaded: decide = 3 (load)")
    try:
        INS.get().spawnInstance(TEMPLATE, WORLD, hub, TRF(0.0, 0.0, 0.0)).get(30, TU.SECONDS)
        second = "made"
    except Exception as ex_:
        second = str(ex_)
    check("FileAlreadyExists" in second and uni.getWorld(WORLD) is None and open(os.path.join(worlds_dir, WORLD, "instance.bson"), "rb").read() == z.read(
          "Server/Instances/SkyWynn_Zone1/instance.bson"), "P. engine guard: a second spawnInstance into the existing folder fails, nothing overwritten: %s" % second[:80])
    try:
        uni.addWorld(WORLD)
        aw = "accepted?!"
    except Exception as ex_:
        aw = str(ex_)
    check("already exists on disk" in aw, "P. engine fact: Universe.addWorld refuses a saved world ('%s') - why SkyyWorldGen reopens with loadWorld" % aw[:60])
    lo0, sp2 = int(Open.LOADS), int(Open.SPAWNS)
    n_log0 = len(records())
    f1 = Open.openSaved(0, pr)
    check(int(Open.LOADS) == lo0 + 1 and int(Open.SPAWNS) == sp2, "P. openSaved = ONE Universe.loadWorld call, no spawnInstance")
    try:
        lw = f1.get(60, TU.SECONDS)
    except Exception as ex_:
        lw = None
        print("   (the load future failed: %s)" % str(ex_)[:300])
    t_end = time.time() + 10
    while Open.loadingFor(WORLD) is not None and time.time() < t_end:
        time.sleep(0.05)
    check(lw is not None and str(lw.getName()) == WORLD and ours(lw.getWorldConfig()) and Open.loadingFor(WORLD) is None,
          "P. the engine loaded the SAME island from disk (our config), WgDone cleared the load mark")
    check(any("loaded from disk" in m for lv, m in records()[n_log0:]), "P. ... and logged it")
    chat()
    settle()
    CFc = JClass("java.util.concurrent.CompletableFuture")
    pend = CFc()
    jfield(JClass(PKG + "WgOpen"), "LOADING").get(None).put(WORLD, pend)
    lo1 = int(Open.LOADS)
    check(int(Open.decide(0, hub)) == 10 and Open.openSaved(0, pr) == pend and Open.loadingFor(WORLD) == pend and int(Open.LOADS) == lo1,
          "P. a load already running: decide = 10, every opener shares that one future, no second loadWorld")
    pend.complete(None)
    Open.loadFinished(WORLD)
    check(Open.loadingFor(WORLD) is None, "P. a finished load leaves no mark")
    zone = world_stub(WORLD, WC.load(Paths.get(tp)).join())
    wmap.put(WORLD, zone)
    check(int(Open.decide(0, hub)) == 1 and int(Open.decide(0, zone)) == 2, "P. loaded: decide = 1 (teleport) from another world, 2 (back to the landing) on it")
    setf(zone, WLD, "alive", AB(False))
    check(int(Open.decide(0, hub)) == 5, "P. a world that is shutting down: decide = 5 (busy)")
    setf(zone, WLD, "alive", AB(True))
    wmap.remove(WORLD)
    Store.read()
    check(Store.created(WORLD) > 0 and "SkyyWorldGen 0.1" in str(Store.createdText(WORLD)), "P. the record reads back after a restart: %s" % Store.createdText(WORLD))
    # 3. a half-made folder (instance.bson only, no config): refused, never re-spawned
    for extra in ("config.json", "config.json.bak", "config.bson"):
        if os.path.exists(os.path.join(worlds_dir, WORLD, extra)):
            os.remove(os.path.join(worlds_dir, WORLD, extra))
    sp3 = int(Open.SPAWNS)
    check(not bool(uni.isWorldLoadable(WORLD)) and int(Open.decide(0, hub)) == 6 and int(Open.SPAWNS) == sp3, "P. a folder without config.json/bson: decide = 6 - refused")
    ref6 = str(Open.refusal(6, 0))
    check("exists but holds no world config" in ref6 and WORLD in ref6, "P. the refusal names the folder: %s" % ref6[:110])
    # 4. an admin deleted the folder: a fresh island, with a WARN
    shutil.rmtree(os.path.join(worlds_dir, WORLD))
    check(int(Open.decide(0, hub)) == 4, "P. the folder deleted: decide = 4 (a fresh island)")
    n_log0 = len(records())
    f3 = Open.startCreate(0, hub, None, pr)
    warn_ = [m for lv, m in records()[n_log0:] if lv == "WARNING" and "is gone although this server made it before" in m]
    check(f3 is not None and len(warn_) == 1, "P. ... generated fresh with a WARN line: %s" % warn_[:1])
    try:
        f3w = f3.get(60, TU.SECONDS)
    except Exception:
        f3w = None
    settle()
    chat()
    c3 = WC.load(Paths.get(os.path.join(worlds_dir, WORLD, "config.json"))).join()
    rp3 = IWC.get(c3).getReturnPoint().getReturnPoint()
    check(f3w is not None and ours(c3) and rp3 is not None and (rp3.getPosition().x(), rp3.getPosition().y(), rp3.getPosition().z()) == (0.5, 200.0, 0.5),
          "P. created without a player position: the world's return point falls back to the spawn of the world it was opened from (never null - "
          "a null one makes config.json undecodable for good)")
    # 4b. first opened from an INSTANCE world (a SkyyIslands island, review finding 5): the island's own return point = the default world
    shutil.rmtree(os.path.join(worlds_dir, WORLD), ignore_errors=True)
    HSC = JClass("com.hypixel.hytale.server.core.HytaleServerConfig")
    hsc = HSC()                                     # the real constructor (sane defaults for any engine code that reads it meanwhile)
    if hsc.getDefaults() is None:
        HSD = JClass("com.hypixel.hytale.server.core.HytaleServerConfig$Defaults")
        setf(hsc, HSC, "defaults", U.allocateInstance(HSD.class_))
    hsc.getDefaults().setWorld("wgdefault")
    setf(hs, HS, "hytaleServerConfig", hsc)
    dcfg = WC.load(Paths.get(vp)).join()
    dcfg.setUuid(UUID.randomUUID())
    dwld = world_stub("wgdefault", dcfg)
    wmap.put("wgdefault", dwld)
    icfg = WC.load(Paths.get(tp)).join()            # an instance config (Plugin.Instance) - what a SkyyIslands island world carries
    icfg.setUuid(UUID.randomUUID())
    iwld = world_stub("skyy-island-wgtest", icfg)
    try:
        check(uni.getDefaultWorld() == dwld and bool(Open.isInstance(iwld)) and not bool(Open.isInstance(hub)) and Open.returnWorld(iwld) == dwld
              and Open.returnWorld(hub) == hub, "P. returnWorld: from an instance world -> the default world; from a plain world -> that world")
        n_log0 = len(records())
        f5 = Open.startCreate(0, iwld, TRF(7.0, 80.0, 9.0), pr)
        try:
            f5w = f5.get(60, TU.SECONDS)
        except Exception as ex_:
            f5w = None
            print("   (the creation future failed: %s)" % str(ex_)[:300])
        settle()
        chat()
        c5 = WC.load(Paths.get(os.path.join(worlds_dir, WORLD, "config.json"))).join()
        rp5 = IWC.get(c5).getReturnPoint()
        p5 = rp5.getReturnPoint().getPosition() if rp5 is not None else None
        check(f5w is not None and ours(c5) and str(rp5.getWorld()) == str(dcfg.getUuid()) and (p5.x(), p5.y(), p5.z()) == (0.5, 200.0, 0.5),
              "P. first opened from an instance world: the island's own return point = the default world's spawn, not the island it was opened from: %s"
              % ((str(rp5.getWorld()), (p5.x(), p5.y(), p5.z())) if p5 is not None else None,))
        check(any("return point is the default world" in m for lv, m in records()[n_log0:]), "P. ... and that is logged")
    finally:
        wmap.remove("wgdefault")
        setf(hs, HS, "hytaleServerConfig", None)       # back to 'no default world' (the bare JVM's state) for the later sections
    check(uni.getDefaultWorld() is None, "P. (no default world again)")
    # 5. busy marks
    shutil.rmtree(os.path.join(worlds_dir, WORLD), ignore_errors=True)
    Open.CREATING.put(WORLD, JLong(int(time.time() * 1000)))
    check(int(Open.decide(0, hub)) == 5, "P. a fresh CREATING mark: decide = 5 (busy)")
    os.makedirs(os.path.join(worlds_dir, WORLD))
    with open(os.path.join(worlds_dir, WORLD, "config.json"), "w") as f_:
        f_.write("{}")
    check(int(Open.decide(0, hub)) == 5, "P. ... even when config.json already exists (the engine writes it before it registers the world)")
    shutil.rmtree(os.path.join(worlds_dir, WORLD))
    Open.CREATING.put(WORLD, JLong(int(time.time() * 1000) - 130000))
    check(int(Open.decide(0, hub)) == 4, "P. a mark older than 120 s no longer blocks: decide = 4")
    Open.CREATING.clear()
    # 6. a LOADED world named skywynn_z1 that is not our island (review finding 4): a creation that died between the template copy and
    #    the first config write boots with WorldConfig.load's DEFAULT config (no config.json); another WorldStructure is caught the same way
    HTc = JClass(PKG + "WgHereTask")
    dflt_cfg = WC.load(Paths.get(os.path.join(WORK, "no-such-world", "config.json"))).join()
    for tag, fcfg in (("a default config (no config.json)", dflt_cfg), ("another WorldStructure (Zone1_Plains1)", WC.load(Paths.get(vp)).join())):
        fw = world_stub(WORLD, fcfg)
        wmap.put(WORLD, fw)
        try:
            sp_before = fcfg.getSpawnProvider()
            fcfg.consumeHasChanged()
            check(int(Open.decide(0, hub)) == 11 and int(Open.decide(0, fw)) == 11 and not bool(Zn.isIsland(0, fw)) and int(Zn.islandIndex(fw)) == -1
                  and int(Zn.worldIndex(WORLD)) == 0, "P. a loaded world named %s with %s: decide = 11 (refused) from anywhere" % (WORLD, tag))
            check(not bool(AL.applyTo(fw)) and not bool(fcfg.consumeHasChanged()) and fcfg.getSpawnProvider() == sp_before and int(Cfg.syncLanding()) == 0
                  and drain(fw) == 0, "P. ... WgApplyLanding / syncLanding never touch its spawn point (%s)" % tag)
            check("Stand on the zone island first" in str(HTc.setHere(None, None, pr, fw)), "P. ... /zone setlanding refuses there (%s)" % tag)
            il_f = [str(x) for x in Cmds.infoLines(None, None, pr, fw)]
            st_f = str(Cmds.statusOf(0))
            check(len(il_f) == 1 and "not the zone island" in il_f[0] and STRUCT in il_f[0] and "NOT the island" in st_f,
                  "P. ... /zone info and the /zone list say it is not the island: %s | %s" % (il_f[:1], st_f))
        finally:
            wmap.remove(WORLD)
    r11 = str(Open.refusal(11, 0))
    check("not the zone island" in r11 and STRUCT in r11 and WORLD in r11 and "delete the folder" in r11, "P. the code-11 refusal names the folder: %s" % r11[:150])
    zw11 = world_stub(WORLD, WC.load(Paths.get(tp)).join())
    check(bool(Zn.isIsland(0, zw11)) and int(Zn.islandIndex(zw11)) == 0, "P. our own template config IS the island (HandleProvider %s)" % STRUCT)
    print("P. persistence: the engine built the island once from the template (recorded), reopened the same island with loadWorld (shared future), "
          "refused a half-made folder, made a fresh one after a delete")

    # ---------------- O. /zone executed (captured chat; the engine teleport calls need a live player - the offline limit)
    def run_go(world):
        chat()
        try:
            Open.go(JObject(None, JClass("com.hypixel.hytale.component.Store")), JObject(None, JClass("com.hypixel.hytale.component.Ref")), pr, world, 0)
            return None, chat()
        except Exception as ex_:
            return ex_, chat()

    def trace(ex_):
        return "".join(str(s_) for s_ in ex_.getStackTrace()) if ex_ is not None else ""
    Cfg.ON = False
    ex_, cl = run_go(hub)
    check(ex_ is None and len(cl) == 1 and "switched off" in cl[0][0] and cl[0][1] == "#ff6b6b", "O. /zone 1 while off: one red line: %s" % cl)
    Cfg.ON = True
    jfield(HGc, "INSTANCE").set(None, hg2)
    Chk.OK[0] = False
    ex_, cl = run_go(hub)
    check(ex_ is None and len(cl) == 1 and "can't open" in cl[0][0] and "did not load" in cl[0][0], "O. /zone 1 without our assets in the generator: refused: %s" % cl)
    jfield(HGc, "INSTANCE").set(None, hg)
    os.makedirs(os.path.join(worlds_dir, WORLD), exist_ok=True)
    ex_, cl = run_go(hub)
    check(ex_ is None and len(cl) == 1 and "holds no world config" in cl[0][0], "O. /zone 1 with a half-made folder: refused, names it: %s" % cl[:1])
    shutil.rmtree(os.path.join(worlds_dir, WORLD))
    sp4 = int(Open.SPAWNS)
    ex_, cl = run_go(hub)
    check(ex_ is not None and int(Open.SPAWNS) == sp4 + 1 and any("Creating Zone 1" in t for t, _c in cl) and "teleportPlayerToLoadingInstance" in trace(ex_),
          "O. /zone 1 the first time: spawnInstance, the 'Creating' line, then the engine teleport call (teleportPlayerToLoadingInstance) is reached: %s" % (cl,))
    settle()
    chat()
    lo2 = int(Open.LOADS)
    n_log0 = len(records())
    ex_, cl = run_go(hub)
    check(ex_ is not None and int(Open.LOADS) == lo2 + 1 and any("Loading Zone 1" in t for t, _c in cl) and "teleportPlayerToLoadingInstance" in trace(ex_),
          "O. /zone 1 to the saved island: loadWorld, the 'Loading' line, then the teleport call: %s" % (cl,))
    settle()
    chat()
    lg_ = [m for lv, m in records()[n_log0:] if "[SkyyWorldGen]" in m and ("loaded from disk" in m or "failed" in m)]
    check(any("loaded from disk" in m for m in lg_) and not any("failed" in m for m in lg_), "O. ... the island made by /zone (no player position offline) loads back: %s" % lg_)
    wmap.put(WORLD, zone)
    lo3, sp5 = int(Open.LOADS), int(Open.SPAWNS)
    ex_, cl = run_go(hub)
    check(ex_ is not None and any("Teleporting to Zone 1" in t for t, _c in cl) and "teleportPlayerToLoadingInstance" in trace(ex_)
          and "teleportPlayerToInstance" not in trace(ex_) and int(Open.LOADS) == lo3 and int(Open.SPAWNS) == sp5,
          "O. /zone 1 to the loaded island: the 'Teleporting' line, then InstancesPlugin.teleportPlayerToLoadingInstance with the finished world "
          "future and the landing (finding 3) - no load, no spawn: %s" % (cl,))
    fw_o = world_stub(WORLD, WC.load(Paths.get(vp)).join())
    wmap.put(WORLD, fw_o)
    n_log0 = len(records())
    ex_, cl = run_go(hub)
    ex2_, cl2 = run_go(hub)
    warn11 = [m for lv, m in records()[n_log0:] if lv == "WARNING" and "is not the Zone 1 - Emerald Wilds island" in m]
    check(ex_ is None and ex2_ is None and len(cl) == 1 and "not the zone island" in cl[0][0] and cl[0][1] == "#ff6b6b" and cl2 == cl and len(warn11) == 1,
          "O. /zone 1 with a foreign world named %s loaded: one red line each time, one WARN in the log (finding 4): %s" % (WORLD, cl[:1]))
    wmap.put(WORLD, zone)
    ex_, cl = run_go(zone)
    check(ex_ is not None and not cl, "O. /zone 1 on the island: the landing Teleport (Teleport.createForPlayer) needs the live entity store: %s" % str(ex_)[:80])
    wmap.remove(WORLD)
    chat()
    Open.leave(JObject(None, JClass("com.hypixel.hytale.component.Store")), JObject(None, JClass("com.hypixel.hytale.component.Ref")), pr, hub)
    cl = chat()
    check(len(cl) == 1 and "not on a zone island" in cl[0][0] and "/hub" in cl[0][0], "O. /zone leave off an island: %s" % cl)
    n_log0 = len(records())
    Open.leave(JObject(None, JClass("com.hypixel.hytale.component.Store")), JObject(None, JClass("com.hypixel.hytale.component.Ref")), pr, zone)
    cl = chat()
    check(len(cl) == 1 and "no world to send you to" in cl[0][0], "O. /zone leave on the island: exitInstance runs (no live player -> it throws), the fallback finds "
          "no default world in the bare JVM and says so: %s" % cl)
    check(any("exitInstance failed" in m for lv, m in records()[n_log0:]), "O. ... the exitInstance failure is logged before the fallback")
    lines = [str(x) for x in Cmds.listLines()]
    check(len(lines) == 3 and "TEST VERSION" in lines[0] and "/zone 1" in lines[1] and "Emerald Wilds" in lines[1] and "made 20" in lines[1], "O. /zone list: %s" % lines)
    il = [str(x) for x in Cmds.infoLines(None, None, pr, hub)]
    check(len(il) == 1 and "not on a zone island" in il[0], "O. /zone info off an island: %s" % il)
    il2 = [str(x) for x in Cmds.infoLines(None, None, pr, zone)]
    check(len(il2) == 2 and "Zone 1 - Emerald Wilds" in il2[0] and "Landing point: 0.5 144 344.5 0" in il2[1], "O. /zone info on the island: %s" % il2)
    Zn = JClass(PKG + "WgZones")
    check([str(Zn.ringAt(0, 0, 0)), str(Zn.ringAt(0, 200, 0)), str(Zn.ringAt(0, 0, 300)), str(Zn.ringAt(0, 0, 395)), str(Zn.ringAt(0, 0, 500))]
          == ["Azure core", "Birch forest", "Meadow rim", "the rim edge", "the void"], "O. ring names by distance")
    check([int(Zn.index(a)) for a in ("1", "z1", "Zone1", " zone 1 ", "emerald wilds", "skywynn_z1", "2", "", "x")] == [0, 0, 0, 0, 0, 0, -1, -1, -1], "O. /zone <n> parsing")
    Cmds.goCmd(None, None, pr, hub, "7")
    cl = chat()
    check(len(cl) == 1 and "no zone '7'" in cl[0][0], "O. /zone 7: %s" % cl)
    HT = JClass(PKG + "WgHereTask")
    check("Stand on the zone island first" in str(HT.setHere(None, None, pr, hub)) and "Could not read your position" in str(HT.setHere(None, None, pr, zone)),
          "O. /zone setlanding refuses off the island and without a position")
    Hooks = JClass(PKG + "WgHooks")
    r_ = Hooks.landingHere(UUID.randomUUID(), "Nobody")
    check(str(r_[0]) == "bad" and "in game" in str(r_[2]), "O. the landing action for a player who is not online: refused")
    pz = player_stub("WgAdmin2", UUID.randomUUID())
    pbu.put(pz.getUuid(), pz)
    r_ = Hooks.landingHere(pz.getUuid(), "WgAdmin2")
    check(str(r_[0]) == "bad" and "Stand on the zone island" in str(r_[2]), "O. the landing action off the island: refused")
    zu = UUID.randomUUID()
    setf(pz, PRc, "worldUuid", zu)
    wbyu.put(zu, zone)
    wmap.put(WORLD, zone)
    r_ = Hooks.landingHere(pz.getUuid(), "WgAdmin2")
    check(str(r_[0]) == "ok" and len(jfield(WLD, "taskQueue").get(zone)) == 1, "O. the landing action on the island: queued on the island's world thread")
    nrun = drain(zone)
    check(nrun == 1, "O. the queued WgHereTask runs (it stops quietly: a stand-in player has no entity)")
    Hooks.afterLanding("landing.point")
    check(drain(zone) == 1, "O. a landing.point change queues WgApplyLanding on the loaded island (after= hook)")
    wmap.remove(WORLD)
    wbyu.remove(zu)
    pbu.remove(pz.getUuid())
    chat()
    print("O. /zone + /zone leave executed: refusals in chat, create / load / teleport reach the engine teleport calls, guards and world-thread tasks")

    # ---------------- H. commands with the engine's own permission code
    root = JClass(PKG + "ZoneCmd")()
    subs = root.getSubCommands()
    SUBS = dict((str(k), subs.get(k)) for k in subs.keySet())
    check(sorted(SUBS) == ["info", "leave", "reload", "setlanding"], "H. /zone sub-commands: %s" % sorted(SUBS))
    var = root.getVariantByArgCount(1)
    check(var is not None and str(var.getClass().getSimpleName()) == "ZoneGoCmd" and len(var.getRequiredArguments()) == 1 and root.getSubCommand("1") is None,
          "H. /zone 1 = the usage variant with one required argument (no sub-command named 1)")
    check(root.getSubCommand("leave") is not None and str(root.getSubCommand("leave").getClass().getSimpleName()) == "ZoneLeaveCmd", "H. /zone leave = the sub-command")
    allc = [("zone", root), ("<n>", var)] + sorted(SUBS.items())
    for nm_, c_ in allc:
        g_ = c_.getPermissionGroups()
        check(str(c_.getPermission()) == NODE and g_ is not None and len(g_) == 0, "H. /zone %s: requirePermission %s + no groups (%s, %s)" % (nm_, NODE, c_.getPermission(), g_))
    try:
        own = U.allocateInstance(JClass("com.hypixel.hytale.server.core.command.system.CommandManager").class_)
        root.setOwner(own)
    except Exception:
        pass
    rec = root.getPermissionGroupsRecursive()
    grp = dict((str(k), sorted(str(x) for x in rec.get(k))) for k in rec.keySet())
    check(not [g for g, ns in grp.items() if NODE in ns or ns], "H. no permission group receives any /zone node (virtual groups: %s)" % grp)
    PM = JClass("com.hypixel.hytale.server.core.permissions.PermissionsModule")
    HashSet = JClass("java.util.HashSet")

    def jset(*xs):
        s = HashSet()
        for x in xs:
            s.add(x)
        return s
    USERS = {"plain": ([], ["hytale:Adventurer"]), "op": ([], ["hytale:Admin"]), "holder": ([NODE], ["hytale:Adventurer"]),
             "skyystar": (["skyy.*"], ["hytale:Adventurer"])}
    IDS = dict((k, UUID.fromString("00000000-0000-0000-0002-%012d" % (i + 1))) for i, k in enumerate(sorted(USERS)))
    BY = dict((str(v), k) for k, v in IDS.items())
    GROUPS = {"hytale:Admin": ["*"], "hytale:Adventurer": []}

    @JImplements("com.hypixel.hytale.server.core.permissions.provider.PermissionProvider")
    class Prov:
        @JOverride
        def getName(self): return "wg-test"
        @JOverride
        def getUserPermissions(self, u): return jset(*USERS.get(BY.get(str(u)), ([], []))[0])
        @JOverride
        def getGroupsForUser(self, u): return jset(*USERS.get(BY.get(str(u)), ([], []))[1])
        @JOverride
        def getGroupPermissions(self, g): return jset(*GROUPS.get(str(g), []))
        @JOverride
        def getEffectiveGroupPermissions(self, g): return jset(*GROUPS.get(str(g), []))
        @JOverride
        def getGroupParent(self, g): return None
        @JOverride
        def getAllRegisteredGroups(self): return jset(*GROUPS.keys())
        @JOverride
        def getUsersWithPermission(self, n): return HashSet()
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
    jfield(PM, "providers").set(pm, provs)
    virt = HashMap()
    for k_ in rec.keySet():
        virt.put(k_, HashSet(rec.get(k_)))
    jfield(PM, "virtualGroups").set(pm, virt)
    f_inst = jfield(PM, "instance")
    old_pm = f_inst.get(None)
    f_inst.set(None, pm)

    @JImplements("com.hypixel.hytale.server.core.command.system.CommandSender")
    class Sender(object):
        def __init__(self, who):
            self.who = who

        @JOverride
        def hasPermission(self, *a):
            q = a[0]
            nn = str(q) if isinstance(q, str) else str(q.getId())
            return bool(PM.get().hasPermission(IDS[self.who], nn))

        @JOverride
        def getUsername(self):
            return self.who

        @JOverride
        def getUuid(self):
            return IDS[self.who]

        @JOverride
        def sendMessage(self, msg):
            pass
    try:
        for who, admin in (("plain", False), ("skyystar", False), ("op", True), ("holder", True)):
            s_ = Sender(who)
            got = [bool(c_.hasPermission(s_)) for _n, c_ in allc]
            check(got == [admin] * len(allc), "H. %s: %s every /zone command (%s)" % (who, "may run" if admin else "refused", got))
    finally:
        f_inst.set(None, old_pm)
    print("H. permissions: every /zone command is admin-only (ops + %s holders), plain players and skyy.* holders refused" % NODE)

    # ---------------- K. the config kit (Server Setup > World Gen)
    Pub = JClass(PKG + "CfgPub")
    kmods = os.path.join(SCRATCH, "kit", "mods")
    khome = os.path.join(kmods, "Skyy_SkyyWorldGen")
    shutil.rmtree(os.path.dirname(kmods), ignore_errors=True)
    os.makedirs(khome)
    Cfg.DIR = Paths.get(khome)
    Cfg.FILE = Paths.get(os.path.join(khome, "config.properties"))
    Cfg.load()
    check(open(os.path.join(khome, "config.properties"), "rb").read() == str(Cfg.DEF_CFG).encode("latin-1"), "K. load() seeds config.properties = the default text")
    Pub.start(Paths.get(kmods), None)
    BR = System = JClass("java.lang.System").getProperties().get("skyy.bridge")
    hdr, fn = BR.get("config:def:SkyyWorldGen"), BR.get("config:fn:SkyyWorldGen")
    if not check(hdr is not None and fn is not None, "K. config:def + config:fn:SkyyWorldGen published"):
        return
    rows = [[str(x) for x in row] for row in hdr[7]]
    check(str(hdr[0]) == "1" and str(hdr[1]) == "SkyyWorldGen" and str(hdr[2]) == "World Gen" and str(hdr[3]) == VERSION and str(hdr[4]) == NODE
          and [str(x) for x in hdr[5]] == ["zones", "island"] and str(hdr[8]) == "Skyy_SkyyWorldGen/config.properties", "K. header: %s" % [str(hdr[i]) for i in (0, 1, 2, 3, 4, 8)])
    check([r[0] for r in rows] == ["part.zones", "landing.point", "landing.here", "info.size", "info.world", "info.rings"]
          and [r[3] for r in rows] == ["bool", "text", "action", "text", "text", "text"] and [r[9] for r in rows][3:] == ["ro", "ro", "ro"], "K. 6 rows: %s" % rows)

    def op(*a):
        arr = JArray(JObject)(len(a))
        for k_, x in enumerate(a):
            arr[k_] = x
        return fn.apply(arr)
    who = IDS["op"]
    f_inst.set(None, pm)
    try:
        r_ = op("set", "part.zones", "false", who, "op", "", "menu")
        check(str(r_[0]) == "confirm", "K. part.zones OFF asks to confirm first: %s" % [str(x) for x in r_])
        r_ = op("set", "part.zones", "false", who, "op", "yes", "menu")
        check(str(r_[0]) == "ok" and not bool(Cfg.ON) and int(Open.decide(0, hub)) == 9, "K. part.zones off -> WgCfg.ON false -> /zone refuses: %s" % str(r_[2]))
        r_ = op("set", "part.zones", "true", who, "op", "", "menu")
        check(str(r_[0]) == "ok" and bool(Cfg.ON), "K. part.zones on again (no confirm needed)")
        for bad, why in (("0.5 144", "Type x y z"), ("0.5 400 344.5", "Y must be"), ("500 144 0", "on the island"), ("0 144 0 999", "Yaw"), ("a b c", "Type x y z"),
                         ("0 1 0", "use a Y from 158 to 174"), ("200 5 100", "not on the island's ground"), ("0.5 130 344.5", "use a Y from 138 to 153"),
                         ("0.5 160 344.5", "not on the island's ground"), ("0 150 0 0", "not on the island's ground")):
            r_ = op("set", "landing.point", bad, who, "op", "", "menu")
            check(str(r_[0]) == "bad" and why in str(r_[2]) and str(Cfg.LANDING) == "0.5 144 344.5 0", "K. landing.point '%s' refused: %s" % (bad, str(r_[2])))
        edges = [(s_, Cfg.landingCheck(Cfg.parseLanding(s_), 0)) for s_ in ("0.5 138 344.5 0", "0.5 153 344.5 0", "0.5 137 344.5 0", "0.5 154 344.5 0",
                                                                             "0 158 0", "0 174 0", "0 157 0", "0 175 0")]
        check([e[1] is None for e in edges] == [True, True, False, False, True, True, False, False],
              "K. the Y window's edges (the curve top 143.95 at 344.5 and 164 at the centre, -6 / +10): %s" % [(e[0], None if e[1] is None else str(e[1])[:40]) for e in edges])
        wmap.put(WORLD, zone)
        r_ = op("set", "landing.point", "2.5 146 330.5 15", who, "op", "", "menu")
        check(str(r_[0]) == "ok" and str(Cfg.LANDING) == "2.5 146 330.5 15" and list(Cfg.landing(0)) == [2.5, 146.0, 330.5, 15.0], "K. landing.point set: %s" % str(r_[2]))
        check(drain(zone) == 1, "K. ... the after= hook queued WgApplyLanding on the loaded island")
        p3 = zone.getWorldConfig().getSpawnProvider().getSpawnPoint(zone, UUID.randomUUID()).getPosition()
        check((p3.x(), p3.y(), p3.z()) == (2.5, 146.0, 330.5), "K. ... and the island's spawn point (void respawn) moved with it")
        r_ = op("set", "info.size", "Big", who, "op", "", "menu")
        check(str(r_[0]) == "bad" and "read-only" in str(r_[2]), "K. a read-only row refuses: %s" % str(r_[2]))
        check(str(op("get", "info.size")) == "Small - radius 384 blocks" and str(op("get", "info.world")) == WORLD and "Meadow rim 256-384" in str(op("get", "info.rings")),
              "K. the read-only rows show the fixed island")
        r_ = op("action", "landing.here", who, "op", "", "menu")
        check(str(r_[0]) == "bad" and "in game" in str(r_[2]), "K. the landing action from someone not in game: %s" % str(r_[2]))
        r_ = op("set", "landing.point", None, who, "op", "", "menu")
        check(str(r_[0]) == "ok" and str(Cfg.LANDING) == "0.5 144 344.5 0", "K. landing.point back to the default")
        drain(zone)
        # finding 3: a HAND-EDITED landing.point + reload moves the loaded island's spawn point (= void respawn) at once, not on the next arrival
        Pub.flush()
        time.sleep(0.8)
        kcfg = os.path.join(khome, "config.properties")
        txt0 = open(kcfg, encoding="latin-1", newline="").read()
        txt1 = re.sub(r"(?m)^landing\.point=.*$", "landing.point=3.5 145 340.5 0", txt0)
        with open(kcfg, "w", encoding="latin-1", newline="") as f_:
            f_.write(txt1)
        r_ = op("reload", who, "op", "command")
        Pub.flush()
        time.sleep(0.8)
        nq3 = drain(zone)
        p6 = zone.getWorldConfig().getSpawnProvider().getSpawnPoint(zone, UUID.randomUUID()).getPosition()
        check(txt1 != txt0 and str(r_[0]) == "ok" and str(Cfg.LANDING) == "3.5 145 340.5 0" and nq3 >= 1 and (p6.x(), p6.y(), p6.z()) == (3.5, 145.0, 340.5),
              "K. a hand-edited landing.point + reload: WgCfg.reloadAll queues WgApplyLanding on the loaded island, its spawn point moves at once "
              "(%d task(s)): %s" % (nq3, str(r_[2])))
        r_ = op("set", "landing.point", None, who, "op", "", "menu")
        nq4 = drain(zone)
        p7 = zone.getWorldConfig().getSpawnProvider().getSpawnPoint(zone, UUID.randomUUID()).getPosition()
        check(str(r_[0]) == "ok" and str(Cfg.LANDING) == "0.5 144 344.5 0" and nq4 >= 1 and (p7.x(), p7.y(), p7.z()) == LANDING,
              "K. ... and back to the default in game (after= hook -> syncLanding)")
        wmap.remove(WORLD)
        Pub.flush()
        time.sleep(0.8)
        txt = open(os.path.join(khome, "config.properties"), encoding="latin-1").read()
        check("part.zones=true" in txt and "landing.point=0.5 144 344.5 0" in txt, "K. the file follows the changes")
        with open(os.path.join(khome, "config.properties"), "a", encoding="latin-1") as f_:
            f_.write("part.zones=false\n")
        r_ = op("reload", who, "op", "command")
        Pub.flush()
        time.sleep(0.8)                      # the kit's save task runs the mod's RELOAD routine (WgCfg.reloadAll) after the merge
        check(str(r_[0]) == "ok" and not bool(Cfg.ON), "K. a hand edit + reload: %s" % str(r_[2]))
        msg = str(Cmds.reload(who, "op"))
        check(msg.startswith("+[Zone]"), "K. /zone reload goes through the kit's reload op: %s" % msg)
        r_ = op("set", "part.zones", "true", who, "op", "", "menu")
        check(str(r_[0]) == "ok" and bool(Cfg.ON), "K. on again")
        r_ = op("set", "part.zones", "false", IDS["plain"], "plain", "yes", "menu")
        check(str(r_[0]) == "denied" and bool(Cfg.ON), "K. a plain player is denied")
    finally:
        f_inst.set(None, old_pm)
        Pub.shutdown()
    print("K. the kit: 6 rows (2 editable, 1 action, 3 read-only), set / confirm / refuse / reload / deny")

    # ---------------- S. the plugin's REAL setup() twice on a scratch data folder
    CMc = JClass("com.hypixel.hytale.server.core.command.system.CommandManager")
    cm = U.allocateInstance(CMc.class_)
    setf(cm, CMc, "commandRegistration", HashMap())
    setf(cm, CMc, "aliases", HashMap())
    setf(cm, CMc, "argTypeRegistry", HashMap())
    jfield(CMc, "instance").set(None, cm)
    PLc = JClass(PKG + "SkyyWorldGenPlugin")
    PB = JClass("com.hypixel.hytale.server.core.plugin.PluginBase")
    CR = JClass("com.hypixel.hytale.server.core.command.system.CommandRegistry")
    sroot = os.path.join(SCRATCH, "twice", "mods")
    shutil.rmtree(os.path.dirname(sroot), ignore_errors=True)
    os.makedirs(sroot)
    sbus = JClass("com.hypixel.hytale.event.EventBus")(False)
    regs = []

    def start_plugin():
        p_ = U.allocateInstance(PLc.class_)
        setf(p_, PB, "logger", HL.get("SkyyWorldGen"))
        setf(p_, PB, "dataDirectory", Paths.get(os.path.join(sroot, "Skyy_SkyyWorldGen-0.1")))
        setf(p_, PB, "commandRegistry", CR(ArrayList(), TrueSup(), "SkyyWorldGen", p_))
        setf(p_, PB, "eventRegistry", ER(ArrayList(), TrueSup(), "SkyyWorldGen", sbus))
        setf(p_, PB, "shutdownTasks", JClass("java.util.concurrent.CopyOnWriteArrayList")())
        m_ = PLc.class_.getDeclaredMethod("setup")
        m_.setAccessible(True)
        m_.invoke(p_)
        regs.append(cm.commandRegistration.keySet().toString() if False else str(jfield(CMc, "commandRegistration").get(cm).keySet()))
        Pub.flush()
        time.sleep(0.7)
        sd_ = PLc.class_.getDeclaredMethod("shutdown")
        sd_.setAccessible(True)
        try:
            sd_.invoke(p_)
        except Exception:
            Pub.shutdown()
        return p_

    def snap():
        out = {}
        for dp, _dn, fns in os.walk(sroot):
            for f_ in fns:
                p_ = os.path.join(dp, f_)
                out[os.path.relpath(p_, sroot)] = (open(p_, "rb").read(), os.path.getmtime(p_))
        return out
    n_log0 = len(records())
    start_plugin()
    s1 = snap()
    time.sleep(1.1)
    start_plugin()
    s2 = snap()
    ready = [m for lv, m in records()[n_log0:] if "[SkyyWorldGen] 0.1 ready" in m]
    check(len(ready) == 2 and "TEST VERSION" in ready[0] and "template SkyWynn_Zone1 found" in ready[0], "S. setup() ran twice, ready line: %s" % (ready[:1] or [None])[0])
    check(sorted(s1) == sorted(s2) and all(s1[k] == s2[k] for k in s1), "S. the second start changes nothing (files + mtimes): %s" % sorted(set(s1) ^ set(s2)))
    check(sorted(s1) == [os.path.join("Skyy_SkyyWorldGen", "config.properties")], "S. only config.properties exists (no record, no history, no change log): %s" % sorted(s1))
    check(regs and "zone" in regs[0] and "hub" not in regs[0], "S. the engine CommandManager registered /zone (and never /hub): %s" % regs[0])
    # the PlayerReadyEvent listener the real setup() registered, reached through the real EventBus (an arrival on the island)
    PREc = JClass("com.hypixel.hytale.server.core.event.events.player.PlayerReadyEvent")
    ESc = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore")
    STc = JClass("com.hypixel.hytale.component.Store")
    REFc = JClass("com.hypixel.hytale.component.Ref")

    def arrival(world_):
        es_ = U.allocateInstance(ESc.class_)
        setf(es_, ESc, "world", world_)
        st_ = U.allocateInstance(STc.class_)
        setf(st_, STc, "externalData", es_)
        rf_ = U.allocateInstance(REFc.class_)
        setf(rf_, REFc, "store", st_)
        ev_ = U.allocateInstance(PREc.class_)
        setf(ev_, JClass("com.hypixel.hytale.server.core.event.events.player.PlayerEvent"), "playerRef", rf_)
        sbus.dispatchFor(PREc.class_).dispatch(ev_)
    zw3 = world_stub(WORLD, WC.load(Paths.get(tp)).join())
    ow3 = world_stub("default", WC.load(Paths.get(vp)).join())
    Cfg.LANDING = "20.5 147 320.5 0"
    arrival(ow3)
    check(drain(ow3) == 0, "S. an arrival in another world queues nothing")
    arrival(zw3)
    nq = drain(zw3)
    p4 = zw3.getWorldConfig().getSpawnProvider().getSpawnPoint(zw3, UUID.randomUUID()).getPosition()
    check(nq >= 1 and (p4.x(), p4.y(), p4.z()) == (20.5, 147.0, 320.5), "S. an arrival on the island (PlayerReadyEvent through the real EventBus) queues WgApplyLanding on "
          "the island's thread, which moves the world spawn point to a changed landing (%d task(s) from the registered listener(s))" % nq)
    Cfg.LANDING = "0.5 144 344.5 0"
    print("S. start twice: the real setup() - command registered through CommandManager.register, listener, kit - no churn; the arrival listener works")

    # ---------------- E. the REAL command dispatch: CommandManager.handleCommand (parsing + the engine's permission check) -> the /zone tree
    # -> AbstractPlayerCommand schedules the command on the player's world executor (the World stand-in's queue = the world thread here).
    # Running it needs the player's live entity store (AbstractPlayerCommand reads the PlayerRef component first) - the offline limit;
    # the bodies themselves ran in section O.
    def sender(uuid_, world_):
        p_ = player_stub("Cmd" + str(uuid_)[-4:])
        setf(p_, PRc, "uuid", uuid_)
        es_ = U.allocateInstance(ESc.class_)
        setf(es_, ESc, "world", world_)
        st_ = U.allocateInstance(STc.class_)
        setf(st_, STc, "externalData", es_)
        setf(st_, STc, "thread", JClass("java.lang.Thread").currentThread())
        rf_ = U.allocateInstance(REFc.class_)
        setf(rf_, REFc, "store", st_)
        setf(rf_, REFc, "index", JInt(7))
        setf(p_, PRc, "entity", rf_)
        return p_

    def dispatch(p_, world_, line):
        chat()
        n0 = len(records())
        fut_ = cm.handleCommand(p_, line)
        q_ = jfield(WLD, "taskQueue").get(world_)
        t_end = time.time() + 5
        while q_.isEmpty() and not fut_.isDone() and time.time() < t_end:
            time.sleep(0.02)
        ran = drain(world_)
        try:
            fut_.get(10, TU.SECONDS)
        except Exception:
            pass
        return ran, chat(), [m for lv, m in records()[n0:] if lv in ("WARNING", "SEVERE")]
    f_inst.set(None, pm)
    try:
        hubw = world_stub("default", WC.load(Paths.get(vp)).join())
        p_op, p_plain = sender(IDS["op"], hubw), sender(IDS["plain"], hubw)
        for line in ("zone", "zone 1", "zone info", "zone leave", "zone setlanding", "zone reload"):
            ran, cl, wl = dispatch(p_plain, hubw, line)
            check(ran == 0 and cl and not any("[Zone]" in t for t, _c in cl), "E. a plain player's /%s: the engine refuses before anything is scheduled: %s" % (line, cl[:1]))
        for line in ("zone", "zone 1", "zone foo", "zone info", "zone leave", "zone setlanding", "zone reload"):
            ran, cl, wl = dispatch(p_op, hubw, line)
            ours_failed = [m for m in wl if "/zone" in m and "failed" in m]
            check(ran == 1 and not ours_failed and any("runtimeError" in t for t, _c in cl) and any("Exception while running that command" in m for m in wl),
                  "E. an op's /%s: parsed, permitted, scheduled on the player's world (1 task); it then stops in the engine's own player lookup "
                  "(no live entity store offline): %s" % (line, [t for t, _c in cl][:1]))
    finally:
        f_inst.set(None, old_pm)
    print("E. the real command dispatch: plain players refused by the engine, every /zone form parsed + permitted + scheduled for ops")

    # ---------------- X. MethodHandles.Lookup access audit (the JVM's own rules)
    LIN = JClass("wgharness.LookupIn")
    MTc = JClass("java.lang.invoke.MethodType")
    CPool = JClass("javassist.bytecode.ConstPool")
    JMod_ = JClass("java.lang.reflect.Modifier")
    XOPS = {0xb2, 0xb3, 0xb4, 0xb5, 0xb6, 0xb7, 0xb8, 0xb9, 0xba, 0xbb, 0xbd, 0xc0, 0xc1, 0xc5, 0x12, 0x13}

    def jvm_class(name):
        return Cls.forName(name.replace("/", "."), False, sysl)

    def lookup_audit(cn):
        D = jvm_class(cn)
        lk_ = LIN.lookupIn(D)
        cc = CPj.get(cn)
        sup = str(cc.getSuperclass().getName()) if cc.getSuperclass() is not None else None
        refused, n2 = [], 0
        for mi in cc.getClassFile2().getMethods():
            ca = mi.getCodeAttribute()
            if ca is None:
                continue
            cp, it3 = mi.getConstPool(), ca.iterator()
            in_ctor = str(mi.getName()) == "<init>"
            while it3.hasNext():
                p_ = it3.next()
                op_ = it3.byteAt(p_)
                if op_ not in XOPS:
                    continue
                where = "%s.%s @%d" % (cn.rsplit(".", 1)[-1], mi.getName(), p_)
                if op_ == 0xba:
                    refused.append(where + ": invokedynamic")
                    continue
                idx = it3.byteAt(p_ + 1) if op_ == 0x12 else it3.u16bitAt(p_ + 1)
                tag = cp.getTag(idx)
                if op_ in (0x12, 0x13) and tag != CPool.CONST_Class:
                    continue
                n2 += 1
                try:
                    if op_ in (0x12, 0x13, 0xbb, 0xbd, 0xc0, 0xc1, 0xc5):
                        lk_.accessClass(jvm_class(str(cp.getClassInfo(idx))))
                    elif op_ in (0xb2, 0xb3, 0xb4, 0xb5):
                        C_ = jvm_class(str(cp.getFieldrefClassName(idx)))
                        ft = MTc.fromMethodDescriptorString("(" + str(cp.getFieldrefType(idx)) + ")V", sysl).parameterType(0)
                        if op_ in (0xb2, 0xb3):
                            lk_.findStaticGetter(C_, str(cp.getFieldrefName(idx)), ft)
                        else:
                            lk_.findGetter(C_, str(cp.getFieldrefName(idx)), ft)
                    else:
                        if tag == CPool.CONST_InterfaceMethodref:
                            cname, name, desc = str(cp.getInterfaceMethodrefClassName(idx)), str(cp.getInterfaceMethodrefName(idx)), str(cp.getInterfaceMethodrefType(idx))
                        else:
                            cname, name, desc = str(cp.getMethodrefClassName(idx)), str(cp.getMethodrefName(idx)), str(cp.getMethodrefType(idx))
                        C_ = jvm_class(cname)
                        mt = MTc.fromMethodDescriptorString(desc, sysl)
                        if name == "<init>" and in_ctor and cname in (sup, cn):
                            md = int(C_.getDeclaredConstructor(mt.parameterArray()).getModifiers())
                            if not (JMod_.isPublic(md) or JMod_.isProtected(md) or cname == cn):
                                raise ValueError("constructor %s%s not accessible" % (cname, desc))
                        elif name == "<init>":
                            lk_.findConstructor(C_, mt)
                        elif op_ == 0xb8:
                            lk_.findStatic(C_, name, mt)
                        elif op_ == 0xb7:
                            lk_.findSpecial(C_, name, mt, D)
                        else:
                            lk_.findVirtual(C_, name, mt)
                except Exception as ex2:
                    if "caller-sensitive" in str(ex2):
                        cs_skip[0] += 1
                    else:
                        refused.append("%s: %s" % (where, ex2))
        return refused, n2
    xref, xn = [], 0
    cs_skip = [0]
    for cn in names:
        r2, n2 = lookup_audit(cn)
        xref += r2
        xn += n2
    check(not xref and xn > 1000, "X. all %d references in the %d classes pass MethodHandles.Lookup in their own class: refused %s" % (xn, len(names), xref[:5]))
    print("X. access: %d class / field / method references, %d refused by the JVM's rules (%d JDK caller-sensitive reflection calls skipped)" % (xn, len(xref), cs_skip[0]))

    # ---------------- L. link check (release, and the 0.7 pre-release as a note)
    def link(server):
        cpl = JClass("javassist.ClassPool")(False)
        cpl.appendSystemPath()
        cpl.appendClassPath(server)
        cpl.appendClassPath(JAR)
        missing, n3 = [], 0
        for nm in names:
            cpool = cpl.get(nm).getClassFile().getConstPool()
            for i in range(1, cpool.getSize()):
                try:
                    tag = cpool.getTag(i)
                except Exception:
                    continue
                if tag not in (9, 10, 11):
                    continue
                if tag == 9:
                    owner, mn, desc = str(cpool.getFieldrefClassName(i)), str(cpool.getFieldrefName(i)), str(cpool.getFieldrefType(i))
                elif tag == 10:
                    owner, mn, desc = str(cpool.getMethodrefClassName(i)), str(cpool.getMethodrefName(i)), str(cpool.getMethodrefType(i))
                else:
                    owner, mn, desc = str(cpool.getInterfaceMethodrefClassName(i)), str(cpool.getInterfaceMethodrefName(i)), str(cpool.getInterfaceMethodrefType(i))
                if not owner.startswith(("com.hypixel.", "org.joml.")):
                    continue
                n3 += 1
                try:
                    oc = cpl.get(owner)
                    if tag == 9:
                        oc.getField(mn, desc)
                    elif mn == "<init>":
                        oc.getConstructor(desc)
                    else:
                        oc.getMethod(mn, desc)
                except Exception:
                    missing.append("%s.%s%s" % (owner.rsplit(".", 1)[1], mn, desc))
        return n3, sorted(set(missing))
    n_rel, miss_rel = link(B.SERVER_JAR)
    check(not miss_rel, "L. release jar: every referenced engine member exists (%d refs): %s" % (n_rel, miss_rel[:8]))
    if os.path.isfile(PRE_JAR):
        n_pre, miss_pre = link(PRE_JAR)
        NOTES.append("0.7 pre-release link check: %d engine refs, %d missing%s" % (n_pre, len(miss_pre), (": " + "; ".join(miss_pre)) if miss_pre else ""))
        print("L. link check: release %d refs, 0 missing; 0.7 pre-release %d refs, %d missing %s" % (n_rel, n_pre, len(miss_pre), miss_pre[:6]))
    else:
        print("L. link check: release %d refs; no pre-release jar" % n_rel)

    # ---------------- B. bytecode facts of the mod
    def mcode(cls, meth):
        return code_of(PKG + cls, meth)
    all_code = "".join(mcode(c, m) for c in expect_classes[:19] for m in [str(x.getName()) for x in CPj.get(PKG + c).getDeclaredMethods()])
    check("Universe.loadWorld" in mcode("WgOpen", "openSaved") and "addWorld" not in all_code, "B. reopen = Universe.loadWorld; addWorld appears nowhere")
    sp_users = [c for c in expect_classes[:19] for m in [str(x.getName()) for x in CPj.get(PKG + c).getDeclaredMethods()] if "spawnInstance" in mcode(c, m)]
    check(sp_users == ["WgOpen"] and "spawnInstance" in mcode("WgOpen", "startCreate") and "spawnInstance" not in mcode("WgOpen", "go"),
          "B. spawnInstance only in WgOpen.startCreate: %s" % sp_users)
    gc_ = mcode("WgOpen", "go")
    check("teleportPlayerToInstance" not in all_code and gc_.count("InstancesPlugin.teleportPlayerToLoadingInstance") == 2 and "CompletableFuture.completedFuture" in gc_
          and "Teleport.createForPlayer" in gc_ and "WgOpen.decide" in gc_,
          "B. go(): decide, then teleportPlayerToLoadingInstance for every trip (a loaded island with a finished future - finding 3) or the "
          "landing Teleport on the island; teleportPlayerToInstance appears nowhere")
    check("WgZones.isIsland" in mcode("WgOpen", "decide") and "WgZones.islandIndex" in mcode("WgApplyLanding", "applyTo")
          and "WgZones.islandIndex" in mcode("WgHereTask", "setHere") and "WgZones.islandIndex" in mcode("WgHooks", "landingHere")
          and "HandleProvider.getWorldStructureName" in mcode("WgZones", "isIsland"),
          "B. only our island (finding 4): decide / WgApplyLanding / setlanding / the landing action check the world's generator")
    check("WgCfg.syncLanding" in mcode("WgCfg", "reloadAll") and "WgCfg.syncLanding" in mcode("WgHooks", "afterLanding")
          and "WgApplyLanding.<init>" in mcode("WgCfg", "syncLanding"), "B. a reload and an in-game change both queue WgApplyLanding (finding 3)")
    check("WgOpen.returnWorld" in mcode("WgOpen", "startCreate") and "InstanceWorldConfig.get" in mcode("WgOpen", "isInstance")
          and "Universe.getDefaultWorld" in mcode("WgOpen", "returnWorld"), "B. startCreate: the island's own return point world via returnWorld (finding 5)")
    check("WgZones.topAt" in mcode("WgCfg", "landingCheck"), "B. landingCheck uses the island's top curve (finding 2)")
    lv_ = mcode("WgOpen", "leave")
    check("InstancesPlugin.exitInstance" in lv_ and "WgOpen.sendDefault" in lv_, "B. leave(): exitInstance, then the default-world fallback")
    st_ = mcode("SkyyWorldGenPlugin", "setup")
    check(st_.count("registerCommand") == 1 and "ZoneCmd" in st_ and "registerGlobal" in st_ and "PlayerReadyEvent" in st_ and "registerSystem" not in st_
          and "CfgPub.start" in st_, "B. setup(): one registerCommand (/zone), the PlayerReadyEvent listener, no ECS systems, the kit")
    cmd_names = []
    for c in ("ZoneCmd", "ZoneLeaveCmd", "ZoneInfoCmd", "ZoneLandingCmd", "ZoneReloadCmd", "ZoneGoCmd"):
        m_ = re.search(r'ldc[_w]* #\d+ = "([^"]*)"', code_of(PKG + c, "<init>"))
        cmd_names.append(m_.group(1) if m_ else None)
    check(cmd_names[:5] == ["zone", "leave", "info", "setlanding", "reload"] and "hub" not in cmd_names and "lobby" not in all_code,
          "B. command names %s - no hub (SkyyIslands owns /hub), no lobby" % cmd_names)
    rd_ = mcode("WgReady", "accept")
    check("World.execute" in rd_ and "WgApplyLanding" in rd_, "B. WgReady: every arrival on a zone island queues WgApplyLanding on its world thread")
    print("B. bytecode facts done")
    # the log scan over the whole run: nothing names a SkyWynn asset or our blocks
    bad_log = [(lv, m) for lv, m in records() if lv in ("WARNING", "SEVERE") and not m.startswith("[SkyyWorldGen]") and "SkyWynn_No_Such" not in m and (
        "SkyWynn" in m or "Couldn't find" in m or "Unused key" in m or "Failed to validate" in m
        or "Duplicate export" in m or any(("invalid name %s" % b) in m for b in ("Soil_Grass", "Soil_Dirt", "Rock_Stone", "Empty")))]
    check(not bad_log, "D. log scan (%d records): no warning names a SkyWynn asset / a missing import / an unused key / our blocks: %s" % (len(records()), bad_log[:3]))


def main():
    if os.path.isdir(SCRATCH):
        shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(SCRATCH)
    os.environ["TEMP"] = os.environ["TMP"] = os.path.join(SCRATCH, "tmp")
    os.makedirs(os.environ["TEMP"], exist_ok=True)
    t0 = time.time()
    try:
        run()
    except SystemExit:
        raise
    except BaseException as e:
        import traceback
        traceback.print_exc()
        check(False, "harness crashed: %s" % e)
    for n_ in NOTES:
        print("NOTE", n_)
    print("%d ok, %d fail (%.0f s)" % (OKS[0], len(FAILS), time.time() - t0))
    code_ = 1 if FAILS else 0
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    sys.stdout.flush()
    os._exit(code_)


if __name__ == "__main__":
    main()
