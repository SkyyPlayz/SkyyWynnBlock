"""SkyyMobs 0.1 harness - bare JVM, no game. Run: python SkyyMobs/test_skyymobs_0.1.py [--jar <jar>] [--dir <scratch>] [--keep]

-Xverify:all, -XX:-UsePerfData; HytaleServer.jar + tools/javassist.jar + the SkyyMobs jar on the classpath. Nothing is deployed and
nothing outside the scratch folder is written (default tools/dev/scratch/mobs01/harness, deleted at the end unless --keep; TEMP / TMP
and java.io.tmpdir point into it). Assets.zip and the two HytaleServer.jar files (release + 0.7 pre-release) are only read.
Sections:
  A  every class of the jar loads, verifies (-Xverify:all) and initialises; M  the manifest + the class list
  B  the default band tables (the jar's own default bands.properties through its real loader) = the refit, typed here independently
     from research/cloud/Mob-Levels-Refit.md (every biome / environment / zone row, zone floors + tops, the documented additions)
  R  the lookup chain (MobLevel.resolve) = a Python mirror for every region x biome of Assets.zip x a set of environments, every
     environment on a non-classic world, world rows, islands, the lava-cave rule (zone tops 18-20 / 28-30 / 43-45 / 58-60), passThrough
  C  difficulty presets (Easy 3/1.5, Normal 4/2, Hard 6/3, Custom); D  health / damage maths per level (float32 exact, caps)
  E  who gets a level: every vanilla role (attitude resolved from Assets.zip) through MobCfg.whyNot = the classification; named cases
     (hostile, neutral fighter, animal, player, trader, tamed, summon, boss, neutral switch off); review F1: other mods' roles that
     share a vanilla prefix (mounts, pets, NPCs, bosses) get no level, the extra row + its guard patterns, a blank extra row (F10), the
     exclude-all uninstall trick (F5), the neutral animals left out by default (F2); X: every role of the installed mods (read-only
     scan of UserData/Mods) that is not a vanilla role gets no level
  W  the worldgen cache (review F3) through a stand-in World / ChunkStore: no generator yet and a throwing ChunkGenerator are NOT
     cached, a non-classic generator is, one entry per exact block column
  N  the prune (review F6): pruneWith (removed / collected worlds, by name without a reference, the 60 s grace), pruneWorld through a
     stand-in EntityStore (gone and invalid refs), MobPruneTask without a Universe
  T  /mobs platetest (review F11): one claim per mob, a stale claim is taken over, every end path releases it
  G  nameplate text: colours off, each markup, the colour ladder, plain() / isOurs(), names without I18n
  F  persistence: the save-slot key, pick / forget / KEPT (chunk reload), the deterministic roll = a Python mirror, a stand-in stat map
     driving the jar's own setMult / apply / strip (spawn = full, reload = same key, curve change = health share kept), and the real
     EntityStatValue codec carrying the modifier key through BSON
  I  mob:fn:level contract (java.lang types, -1 cases, never throws, 8 threads)
  H  command permissions with the engine's own code (Adventurer: /mobs + /mobs info only; admin subs skyymobs.admin, empty groups)
  K  the config kit (Server Setup): header, every row, set / refuse, table ops through the real kit, the reload routine, hand edit
  S  start twice on a scratch folder (no churn: files byte-identical, no history version, no change log)
  L  link check: every engine member the jar references exists in the release AND the 0.7 pre-release HytaleServer.jar
  P  bytecode facts: the hook's query + ordering, the damage system's group + ordering, one registerSystem per class, no unordered
     hook fallback (review F4), the prune scheduled + cancelled (F6), the worldgen cache key (F3)
Exit code 1 on any FAIL.
"""
import os, sys, re, json, shutil, struct, zipfile, random, collections, time, threading

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION = "0.1"
PKG = "com.skyy.mobs."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "mobs01", "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyMobs-%s.jar" % VERSION)))
KEEP = "--keep" in sys.argv
# cleanup fix (2026-10-02, the 0.1.1 harness's fix + an own-folder marker): nothing is deleted unless main() validated --dir
SCRATCH_OK = [False]
MARKER = ".skyymobs01-harness"    # written into the scratch folder this harness made; only a folder holding it is ever deleted
FAILS, OKS = [], [0]
COUNT = collections.Counter()
HY = os.path.join(os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming"), "Hytale", "install")
AZ_PATH = os.path.join(HY, "release", "package", "game", "latest", "Assets.zip")
PRE_JAR = os.path.join(HY, "pre-release", "package", "game", "latest", "Server", "HytaleServer.jar")


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)
    return cond


def f32(x):
    return struct.unpack("f", struct.pack("f", x))[0]


# ================================================================= the refit, typed independently (research/cloud/Mob-Levels-Refit.md)
# section 3 (Zones 1-3) + plan 4.5 (Zone 4, unchanged). Exact biome rows: (region, biome) -> (lo, hi)
REFIT_BIOMES = {
    ("Zone1_Tier1", "Plains_Smooth"): (1, 3), ("Zone1_Tier1", "Plains_Birch"): (3, 5),
    ("Zone1_Tier1", "Forest_Birch"): (5, 7), ("Zone1_Tier1", "Forest_Flower"): (5, 7), ("Zone1_Tier1", "Mountain_Tier1"): (5, 7),
    ("Zone1_Tier2", "Plains_Gorge"): (7, 9), ("Zone1_Tier2", "Plains_Tallgrass"): (9, 11),
    ("Zone1_Tier2", "Forest_Aspen"): (10, 12), ("Zone1_Tier2", "Forest_Gully"): (10, 12), ("Zone1_Tier2", "Mountain_Tier2"): (10, 12),
    ("Zone1_Tier3", "Plains_Gorge"): (12, 14), ("Zone1_Tier3", "Forest_Swamp"): (16, 18), ("Zone1_Tier3", "Mountain_Tier3"): (16, 18),
    ("Zone1_Tier3", "Forest_Autumn"): (18, 20), ("Zone1_Tier3", "Forest_Moss"): (18, 20), ("Zone1_Tier3", "Forest_Azure"): (18, 20),
    ("Zone2_Tier1", "Savannah_Forest"): (20, 22), ("Zone2_Tier1", "Savannah_Plains"): (20, 22), ("Zone2_Tier1", "Savannah_Boab"): (20, 22),
    ("Zone2_Tier1", "Savannah_Rock"): (20, 22), ("Zone2_Tier1", "Savannah_Mudflats"): (20, 22), ("Zone2_Tier1", "Scrub_Bushland"): (22, 24),
    ("Zone2_Tier2", "Desert_Oasis"): (25, 27), ("Zone2_Tier2", "Desert_Rock"): (25, 27), ("Zone2_Tier2", "Desert_Springs"): (25, 27),
    ("Zone2_Tier2", "Desert_Red"): (25, 27),
    ("Zone2_Tier3", "Desert_Barren"): (27, 29), ("Zone2_Tier3", "Desert_Mushroom"): (27, 29),
    ("Zone2_Tier3", "Scrub_Tar_Pits"): (28, 30), ("Zone2_Tier3", "Desert_Mushroom_Foot"): (28, 30),
    ("Zone3_Tier1", "Forest_Redwood"): (30, 32), ("Zone3_Tier1", "Plains_Shire"): (30, 32), ("Zone3_Tier1", "Forest_Fir"): (32, 34),
    ("Zone3_Tier1", "Forest_Tundra"): (32, 34), ("Zone3_Tier1", "Plains_Hotsprings"): (32, 34),
    ("Zone3_Tier2", "Forest_Cedar"): (36, 38), ("Zone3_Tier2", "Plains_Frozen"): (37, 39), ("Zone3_Tier2", "Forest_Cedar_Mixed"): (37, 39),
    ("Zone3_Tier2", "Plains_Tundra"): (37, 39),
    ("Zone3_Tier3", "Forest_Frozen"): (41, 43), ("Zone3_Tier3", "Forest_Frozen_Light"): (41, 43), ("Zone3_Tier3", "Plains_Frozen_Frost"): (41, 43),
    ("Zone4_Tier4", "Wastes_Grasslands"): (45, 47), ("Zone4_Tier4", "Wastes_Geysers"): (48, 50), ("Zone4_Tier4", "Forest_Ghost"): (48, 50),
    ("Zone4_Tier4", "Desert_Dunes"): (48, 50), ("Zone4_Tier4", "Forest_Swamp"): (48, 50),
    ("Zone4_Tier5", "Desert_Ash"): (53, 55), ("Zone4_Tier5", "Wastes_Ash"): (53, 55), ("Zone4_Tier5", "Wastes_Lava"): (55, 57),
    ("Zone4_Tier5", "Forest_Burned"): (58, 60), ("Zone4_Tier5", "Forest_Roots"): (58, 60),
}
# patterned refit rows (Trork camps, plateaus, overlays by region tier) and the region fallbacks (refit "Fallback rows")
REFIT_PATTERNS = {
    "Zone1_Tier1.*_Trork": (5, 7), "Zone1_Tier2.*_Trork": (10, 12), "Zone1_Tier3.*_Trork": (16, 18),
    "Zone2_Tier1.Plateau_*": (21, 23), "Zone2_Tier3.Plateau_Desert_*": (28, 30), "Zone2_Tier3.Desert_Oasis_Hidden*": (28, 30),
    "Zone3_Tier1.Mountain_*": (32, 34), "Zone3_Tier2.Mountain_*": (37, 39), "Zone3_Tier3.Mountain_*": (43, 45),
    "Zone1_Tier1.*": (1, 7), "Zone1_Tier2.*": (7, 12), "Zone1_Tier3.*": (12, 20),
    "Zone2_Tier1.*": (20, 24), "Zone2_Tier2.*": (25, 27), "Zone2_Tier3.*": (27, 30),
    "Zone3_Tier1.*": (30, 34), "Zone3_Tier2.*": (36, 39), "Zone3_Tier3.*": (41, 45),
    "Zone1_Spawn.*": (1, 3),        # refit: Zone1_Spawn Plains_Spawn 1-3 (fixed start area)
}
# rows the build adds where the refit is silent (each a documented decision in the build script header)
ADDED = {
    "Zone1_Temple": (1, 3),                                                          # the start-area temple = like the spawn
    "Zone4_Tier4": (45, 50), "Zone4_Tier5": (53, 60),                                # plan 4.1 region bands
    "Zone1_Shore": (1, 3), "Zone2_Shore": (20, 22),                                  # plan 4.1: shores = lowest band of the land region
    "Zone3_Shore_Tier1": (30, 32), "Zone3_Shore_Tier2": (36, 38), "Zone3_Shore_Tier3": (41, 43),
    "Zone4_Shore_Tier4": (45, 47), "Zone4_Shore_Tier5": (53, 55),
}
# refit 4.2 (Zones 1-3) + plan 4.6 (Zone 4 + the 0.7 portal shards, unchanged): env -> (lo, hi, bonus)
REFIT_ENV = {
    "Env_Zone1_Plains": (1, 3, 0), "Env_Zone1_Shores": (1, 3, 0), "Env_Zone1_Kweebec": (1, 3, 0), "Env_Zone1_Forests": (5, 9, 0),
    "Env_Zone1_Mountains": (5, 14, 0), "Env_Zone1_Trork": (5, 16, 0), "Env_Zone1_Swamps": (14, 20, 0), "Env_Zone1_Autumn": (16, 20, 0),
    "Env_Zone1_Azure": (16, 20, 0), "Env_Zone1_Caves*": (5, 14, 0), "Env_Zone1_Caves_Volcanic_T1": (5, 9, 0),
    "Env_Zone1_Caves_Volcanic_T2": (9, 14, 0), "Env_Zone1_Caves_Volcanic_T3": (14, 18, 0), "Env_Zone1_Caves_Goblins": (5, 16, 1),
    "Env_Zone1_Mineshafts": (5, 16, 1), "Env_Zone1_Encounters": (9, 18, 2), "Env_Zone1_Graveyard": (9, 18, 2),
    "Env_Zone1_Mage_Towers": (9, 18, 2), "Env_Zone1_Dungeons": (14, 20, 2),
    "Env_Zone2_Savanna": (20, 22, 0), "Env_Zone2_Shores": (20, 22, 0), "Env_Zone2_Scrub": (22, 24, 0), "Env_Zone2_Plateaus": (21, 27, 0),
    "Env_Zone2_Deserts": (25, 29, 0), "Env_Zone2_Oasis": (25, 30, 0), "Env_Zone2_Feran": (23, 28, 1), "Env_Zone2_Scarak": (23, 28, 1),
    "Env_Zone2_Caves*": (21, 27, 0), "Env_Zone2_Caves_Volcanic_T1": (21, 23, 0), "Env_Zone2_Caves_Volcanic_T2": (25, 27, 0),
    "Env_Zone2_Caves_Volcanic_T3": (28, 30, 0), "Env_Zone2_Mineshafts": (23, 27, 1), "Env_Zone2_Caves_Goblins": (23, 27, 1),
    "Env_Zone2_Encounters": (25, 29, 2), "Env_Zone2_Mage_Towers": (25, 29, 2), "Env_Zone2_Dungeons": (27, 30, 2),
    "Env_Zone3_Tundra": (30, 35, 0), "Env_Zone3_Shores": (30, 33, 0), "Env_Zone3_Forests": (30, 38, 0), "Env_Zone3_Mountains": (35, 41, 0),
    "Env_Zone3_Glacial": (38, 45, 0), "Env_Zone3_Caves*": (32, 41, 0), "Env_Zone3_Trork": (35, 42, 1),
    "Env_Zone3_Outlander*": (39, 45, 2), "Env_Zone3_Encounters": (39, 45, 2),
    "Env_Zone4_Wastes": (45, 50, 0), "Env_Zone4_Shores": (45, 47, 0), "Env_Zone4_Crucible": (48, 50, 0), "Env_Zone4_Volcanoes": (48, 57, 0),
    "Env_Zone4_Forests": (48, 60, 0), "Env_Zone4_Jungles": (50, 58, 0), "Env_Zone4_Encounters*": (53, 60, 2),
    "Env_Zone4_Villages*": (55, 60, 2),
    "Env_Portal_Goblin_Surface": (5, 8, 0), "Env_Portal_Goblin_Cave": (7, 10, 0), "Env_Portal_Goblin_Cave_Deep": (9, 11, 0),
    "Env_Portal_Goblin_Cave_Void": (10, 12, 0),
}
REFIT_ZONE = {"Zone1": (1, 7), "Zone2": (20, 24), "Zone3": (30, 34), "Zone4": (45, 50)}
LOCKED = {1: (1, 20), 2: (20, 30), 3: (30, 45), 4: (45, 60)}          # OPEN-QUESTIONS LOCKED 2026-10-01
LAVA_TOPS = {1: (18, 20), 2: (28, 30), 3: (43, 45), 4: (58, 60)}      # Skyy R5: the zone's hardest biome (Zone 1 "about 17-20")
PASS = "River_*,Lake*,Dunes_*,*_Mudflats,*_Kweebec,Valley_*,Canyon_*,Caldera_*,Hills_*,Volcano_*,Village_*,*_Village,*_Town,Town_*"


def pglob(p, s):
    return re.fullmatch(re.escape(p.lower()).replace(r"\*", ".*"), s.lower()) is not None


def spec(p):
    return sum(1 for c in p if c != "*")


class PyTable(object):
    """mirror of MobBands: keys sorted, exact (case-insensitive) first, else the highest literal count, ties = the first sorted key"""
    def __init__(self, rows):
        self.rows = sorted(rows.items(), key=lambda kv: kv[0])

    def find(self, key):
        if key is None:
            return None
        k = key.lower()
        for rk, v in self.rows:
            if "*" not in rk and rk.lower() == k:
                return rk, v
        best, bs = None, -1
        for rk, v in self.rows:
            if "*" in rk and spec(rk.lower()) > bs and pglob(rk, k):
                best, bs = (rk, v), spec(rk.lower())
        return best

    def find_prefix(self, key):
        hit = self.find(key)
        if hit or key is None:
            return hit
        best, bl = None, 0
        for rk, v in self.rows:
            if "*" not in rk and len(rk) > bl and key.lower().startswith(rk.lower()):
                best, bl = (rk, v), len(rk)
        return best


def zone_of_region(region):
    m = re.match(r"^Zone(\d+)(?:_|$)", region or "")
    return "Zone" + m.group(1) if m else None


def zone_of_env(env):
    return zone_of_region(env[4:]) if env and env.startswith("Env_Zone") else None


def volcanic_zone(env):
    z = zone_of_env(env)
    return int(z[4:]) if z and env.startswith("Env_%s_Caves_Volcanic" % z) else 0


def py_resolve(T, wn, island, classic, region, biome, tile, env, volcanic=True, isl=(0, 0), dflt=(0, 0)):
    w = T["world"].find_prefix(wn)
    if w:
        return (w[1][0], w[1][1], 0, "world", w[0])
    if island:
        return (isl[0], isl[1], 0, "island", "bands.islands")
    e = T["env"].find(env) if env else None
    eb = e[1][2] if e else 0
    vz = volcanic_zone(env)
    if volcanic and vz and T["tops"].get(vz):
        a, b, k = T["tops"][vz]
        return (a, b, eb, "lava", "Zone%d top %s" % (vz, k))
    if classic and region is not None:
        used = tile if (biome and tile and any(pglob(p, biome) for p in PASS.split(","))) else biome
        hit = T["biome"].find("%s.%s" % (region, used)) if used else None
        if hit is None and used != biome and biome:
            hit = T["biome"].find("%s.%s" % (region, biome))
        if hit is None:
            hit = T["biome"].find(region)
        if hit is None:
            hit = T["biome"].find(region + ".*")
        if hit:
            return (hit[1][0], hit[1][1], eb, "biome", hit[0])
    if e:
        return (e[1][0], e[1][1], 0, "env", e[0])
    z = zone_of_region(region) or zone_of_env(env)
    zz = T["zone"].find(z) if z else None
    if zz:
        return (zz[1][0], zz[1][1], 0, "zone", zz[0])
    return (dflt[0], dflt[1], 0, "default", "bands.default")


# Java's String.hashCode and the SplitMix64 roll (MobLevel.roll)
M64 = (1 << 64) - 1


def jhash(s):
    h = 0
    for ch in s:
        h = (31 * h + ord(ch)) & 0xFFFFFFFF
    return h - (1 << 32) if h >= (1 << 31) else h


def mix(z):
    z &= M64
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & M64
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & M64
    return z ^ (z >> 31)


def py_roll(seed, msb, lsb, role, a, b):
    if b <= a:
        return a
    h = mix((seed + 0x9E3779B97F4A7C15) & M64)
    h = mix(h ^ (msb & M64))
    h = mix(h ^ (lsb & M64))
    h = mix(h ^ (jhash(role or "") & M64))
    return a + h % (b - a + 1)


# vanilla role attitudes (the engine's default attitude is HOSTILE when a role sets none - SupportConfigBuilder bytecode)
def lenient(t):
    t = re.sub(r"//[^\n]*", "", t)
    t = re.sub(r"/\*.*?\*/", "", t, flags=re.S)
    t = re.sub(r",\s*([}\]])", r"\1", t)
    return json.loads(t)


def vanilla_roles():
    z = zipfile.ZipFile(AZ_PATH)
    roles, path = {}, {}
    for n in z.namelist():
        if n.startswith("Server/NPC/Roles/") and n.endswith(".json"):
            nm = n.rsplit("/", 1)[1][:-5]
            roles[nm] = lenient(z.read(n).decode("utf-8-sig", "replace"))
            path[nm] = n[len("Server/NPC/Roles/"):]

    def params(name, d=0):
        r = roles.get(name)
        if r is None or d > 12:
            return {}, None
        if r.get("Type") == "Variant":
            p, root = params(r.get("Reference"), d + 1)
            p = dict(p)
            p.update(r.get("Modify") or {})
            return p, root
        return dict((k, v["Value"]) for k, v in (r.get("Parameters") or {}).items() if isinstance(v, dict) and "Value" in v), name

    out = {}
    for nm, r in roles.items():
        if r.get("Type") in ("Abstract", "Component") or path[nm].startswith("_Core/") or nm == "Empty_Role":
            continue
        p, root = params(nm)
        rr = roles.get(root) or {}
        a = rr.get("DefaultPlayerAttitude")
        if isinstance(a, dict) and "Compute" in a:
            a = p.get(a["Compute"])
        if isinstance(a, dict):
            a = a.get("Value")
        if isinstance(p.get("DefaultPlayerAttitude"), str):
            a = p["DefaultPlayerAttitude"]
        out[nm] = ((a or "Hostile").upper(), root, path[nm])
    return out, z


PASSIVE_ROOTS = {"Template_Birds_Passive", "Template_Swimming_Passive", "Template_Beasts_Passive_Critter", "Template_Edible_Critter",
                 "Template_Placeholder", "Template_Livestock", "Template_Temple", "Template_Summoned_Ally", "Template_Animal_Neutral"}
NEUTRAL_OK = {"Boar", "Warthog", "Feran_Sharptooth", "Feran_Longtooth", "Feran_Burrower", "Feran_Windwalker"}
BOSS = ("Goblin_Duke", "Trork_Chieftain", "Dragon_", "Skeleton_Elite")


def expected_level(nm, att, root):
    if nm.startswith(BOSS):
        return False
    if att == "HOSTILE":
        return root not in PASSIVE_ROOTS
    if att == "NEUTRAL":
        return nm in NEUTRAL_OK or nm.startswith(("Scarak_", "Dungeon_Scarak_"))
    return False


def run():
    import jpype
    from jpype import JClass, JArray, JObject, JImplements, JOverride, JInt, JFloat, JLong, JString
    import skyybuild as B
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR, B.JAVASSIST, JAR], convertStrings=True)
    Cls = JClass("java.lang.Class")
    sysl = JClass("java.lang.ClassLoader").getSystemClassLoader()
    UUID = JClass("java.util.UUID")
    Paths = JClass("java.nio.file.Paths")
    HashMap = JClass("java.util.HashMap")

    # ---------------- A. load + verify + init
    z = zipfile.ZipFile(JAR)
    names = sorted(n[:-6].replace("/", ".") for n in z.namelist() if n.endswith(".class"))
    for n in names:
        try:
            Cls.forName(n, True, sysl)
            COUNT["A"] += 1
        except Exception as e:
            check(False, "A. load %s: %s" % (n, e))
    OKS[0] += COUNT["A"]
    print("A. loaded + verified + initialised (-Xverify:all): %d classes" % COUNT["A"])
    if FAILS:
        return
    # ---------------- M. manifest + class list
    man = json.loads(z.read("manifest.json").decode("utf-8"))
    check(man.get("Main") == PKG + "SkyyMobsPlugin" and man.get("Name") == "0.1 SkyyMobs" and man.get("Group") == "Skyy"
          and str(man.get("Version")) == VERSION and man.get("IncludesAssetPack") is False, "M. manifest: %s" % man)
    want = sorted(PKG + c for c in ("CfgFile", "CfgFn", "CfgHist", "CfgLog", "CfgPub", "CfgRows", "CfgSaveTask", "LevelDamage",
                                     "LevelDamageU", "LevelHook", "MobBands", "MobCfg", "MobCmds", "MobGlob", "MobHooks",
                                     "MobInfo", "MobLevel", "MobLevelFn", "MobLog", "MobPlateStep", "MobPruneTask", "MobScanTask", "MobsCmd",
                                     "MobsInfoCmd", "MobsInspectCmd", "MobsPlateCmd", "MobsReloadCmd", "MobsSetCmd", "SkyyMobsPlugin"))
    check(names == want, "M. exactly the 29 classes (no LevelHookU - review F4; MobPruneTask - F6): %s" % sorted(set(names) ^ set(want)))
    check(not [n for n in z.namelist() if n.endswith(".ui")], "M. no .ui file in the jar")

    Cfg, Lvl, Glob = JClass(PKG + "MobCfg"), JClass(PKG + "MobLevel"), JClass(PKG + "MobGlob")
    Cfg.useDefaults()

    # ---------------- B. default tables = the refit
    def table(t):
        return dict((str(t.raw[i]), (int(t.a[i]), int(t.b[i]), int(t.c[i]))) for i in range(int(t.n)))
    BI, EN, WO, ZO = table(Cfg.BIOME), table(Cfg.ENV), table(Cfg.WORLD), table(Cfg.ZONE)
    jb = dict((k, v[:2]) for k, v in BI.items())
    azb = zipfile.ZipFile(AZ_PATH)
    reg_bio = collections.defaultdict(set)
    for n_ in azb.namelist():
        m_ = re.match(r"^Server/World/Default/Zones/([^/]+)/(?:Tile|Custom)\.([^/]+)\.json$", n_)
        if m_:
            reg_bio[m_.group(1)].add(m_.group(2))
    env_all = set(n_.rsplit("/", 1)[1][:-5] for n_ in azb.namelist() if n_.startswith("Server/Environments/") and n_.endswith(".json"))
    exact_refit = set("%s.%s" % rb for rb in REFIT_BIOMES)
    want_b = dict(("%s.%s" % rb, band) for rb, band in REFIT_BIOMES.items())
    for k, band in REFIT_PATTERNS.items():
        reg, _, pat = k.partition(".")
        if pat == "*":
            want_b[reg] = band
        else:
            for b_ in reg_bio[reg]:
                if pglob(pat, b_) and "%s.%s" % (reg, b_) not in exact_refit:
                    want_b["%s.%s" % (reg, b_)] = band
    want_b.update(ADDED)
    want_e = dict((k, v) for k, v in REFIT_ENV.items() if "*" not in k)
    for k, v in REFIT_ENV.items():
        if "*" in k:
            for e_ in env_all:
                if pglob(k, e_) and e_ not in REFIT_ENV:
                    want_e[e_] = v
    for (reg, bio), band in sorted(REFIT_BIOMES.items()):
        check(jb.get("%s.%s" % (reg, bio)) == band, "B. biome %s.%s = %s (refit), jar %s" % (reg, bio, band, jb.get("%s.%s" % (reg, bio))))
    for k, band in sorted(want_b.items()):
        check(jb.get(k) == band, "B. biome %s = %s (refit, patterns expanded with Assets.zip), jar %s" % (k, band, jb.get(k)))
    check(set(jb) == set(want_b), "B. the biome rows are exactly the refit (expanded) + the documented additions: %s" % sorted(set(jb) ^ set(want_b)))
    check(not [k for k in list(jb) + list(EN) if "*" in k], "B. no * key in the shipped tables (the kit refuses it in Server Setup)")
    check(EN == want_e, "B. environment rows = the refit / plan 4.6 (patterns expanded): %s" % sorted(set(EN.items()) ^ set(want_e.items())))
    check(dict((k, v[:2]) for k, v in ZO.items()) == REFIT_ZONE and not WO, "B. zone rows %s, no world rows %s" % (ZO, WO))
    for zz, (lo, hi) in LOCKED.items():
        rows = [v for k, v in jb.items() if k.startswith("Zone%d_" % zz)]
        check(min(r[0] for r in rows) == lo and max(r[1] for r in rows) == hi, "B. Zone %d biome rows span the LOCKED %d-%d" % (zz, lo, hi))
        check((int(Cfg.ZTOP_A[zz]), int(Cfg.ZTOP_B[zz])) == LAVA_TOPS[zz], "B. Zone %d top (hardest biome) = %s: %s %d-%d" % (
            zz, LAVA_TOPS[zz], Cfg.ZTOP_KEY[zz], Cfg.ZTOP_A[zz], Cfg.ZTOP_B[zz]))
    check(str(Cfg.ZTOP_KEY[1]).startswith("Zone1_Tier3.Forest_"), "B. Zone 1 top is a Tier 3 forest (Autumn / Moss / Azure): %s" % Cfg.ZTOP_KEY[1])
    check(jb["Zone1_Tier3.Forest_Azure"] == (18, 20), "B. the blue forest is the top of Zone 1 (18-20)")
    print("B. tables = refit: %d biome rows (%d refit exact, %d refit patterns expanded, %d added), %d env rows (%d refit), %d zone rows; zone tops %s" % (
        len(jb), len(REFIT_BIOMES), len(REFIT_PATTERNS), len(ADDED), len(EN), len(REFIT_ENV), len(ZO),
        dict((zz, (int(Cfg.ZTOP_A[zz]), int(Cfg.ZTOP_B[zz]))) for zz in LAVA_TOPS)))

    # ---------------- R. the lookup chain = the Python mirror
    PT = {"biome": PyTable(jb), "env": PyTable(EN), "world": PyTable({}), "zone": PyTable(dict((k, v[:2]) for k, v in ZO.items())),
          "tops": dict((zz, (int(Cfg.ZTOP_A[zz]), int(Cfg.ZTOP_B[zz]), str(Cfg.ZTOP_KEY[zz]))) for zz in LAVA_TOPS)}
    azz = zipfile.ZipFile(AZ_PATH)
    regions = collections.defaultdict(set)
    for n in azz.namelist():
        m = re.match(r"^Server/World/Default/Zones/([^/]+)/(Tile|Custom)\.([^/]+)\.json$", n)
        if m:
            regions[m.group(1)].add((m.group(2), m.group(3)))
    env_ids = sorted(set(n.rsplit("/", 1)[1][:-5] for n in azz.namelist() if n.startswith("Server/Environments/") and n.endswith(".json")))
    tiles = dict((r, sorted(b for t, b in s if t == "Tile")) for r, s in regions.items())
    ENVS = [None, "Env_Zone1_Azure", "Env_Zone1_Encounters", "Env_Zone1_Caves_Volcanic_T2", "Env_Zone2_Feran", "Env_Zone2_Caves_Volcanic_T3",
            "Env_Zone3_Outlander_Village", "Env_Zone3_Caves_Volcanic_T1", "Env_Zone4_Villages_Swamp", "Env_Zone4_Caves_Volcanic",
            "Env_Default_Void", "Env_Zone0_Cold"]

    def jres(wn, isl, cls_, reg, bio, til, env):
        r = Lvl.resolve(wn, isl, cls_, reg, bio, til, env)
        return (int(r[0]), int(r[1]), int(r[2]), str(r[3]), str(r[4]))
    n_cmp = 0
    for reg in sorted(regions):
        for typ, bio in sorted(regions[reg]):
            til = tiles[reg][0] if (typ == "Custom" and tiles.get(reg)) else bio
            for env in ENVS:
                got = jres("default", False, True, reg, bio, til, env)
                exp = py_resolve(PT, "default", False, True, reg, bio, til, env)
                n_cmp += 1
                if got != exp:
                    check(False, "R. resolve(%s, %s, tile %s, env %s) = %s, mirror %s" % (reg, bio, til, env, got, exp))
    for env in env_ids + ["Env_Portal_Goblin_Cave", "Env_Unknown_Thing", None]:
        for cls_ in (False,):
            got = jres("islandchain", False, cls_, None, None, None, env)
            exp = py_resolve(PT, "islandchain", False, cls_, None, None, None, env)
            n_cmp += 1
            if got != exp:
                check(False, "R. non-classic resolve(env %s) = %s, mirror %s" % (env, got, exp))
    OKS[0] += n_cmp
    # named cases (the plan's / refit's in-game tests as lookups)
    NAMED = [
        (("default", False, True, "Zone1_Tier1", "Plains_Smooth", "Plains_Smooth", "Env_Zone1_Plains"), (1, 3, 0, "biome")),
        (("default", False, True, "Zone1_Tier3", "Forest_Azure", "Forest_Azure", "Env_Zone1_Azure"), (18, 20, 0, "biome")),
        (("default", False, True, "Zone1_Tier3", "Forest_Moss_Trork", "Forest_Moss", "Env_Zone1_Trork"), (16, 18, 0, "biome")),
        (("default", False, True, "Zone1_Tier1", "River_Plains_Smooth", "Plains_Smooth", None), (1, 3, 0, "biome")),
        (("default", False, True, "Zone1_Tier1", "Plains_Smooth_Kweebec", "Plains_Smooth", "Env_Zone1_Kweebec"), (1, 3, 0, "biome")),
        (("default", False, True, "Zone1_Tier3", "Forest_Azure", "Forest_Azure", "Env_Zone1_Caves_Goblins"), (18, 20, 1, "biome")),
        (("default", False, True, "Zone1_Tier3", "Forest_Azure", "Forest_Azure", "Env_Zone1_Caves_Spiders"), (18, 20, 0, "biome")),
        (("default", False, True, "Zone1_Tier1", "Plains_Smooth", "Plains_Smooth", "Env_Zone1_Caves_Volcanic_T1"), (18, 20, 0, "lava")),
        (("default", False, True, "Zone2_Tier1", "Savannah_Plains", "Savannah_Plains", "Env_Zone2_Caves_Volcanic_T2"), (28, 30, 0, "lava")),
        (("default", False, True, "Zone3_Tier1", "Forest_Fir", "Forest_Fir", "Env_Zone3_Caves_Volcanic_T3"), (43, 45, 0, "lava")),
        (("default", False, True, "Zone4_Tier4", "Wastes_Grasslands", "Wastes_Grasslands", "Env_Zone4_Caves_Volcanic"), (58, 60, 0, "lava")),
        (("default", False, True, "Zone2_Tier3", "Desert_Oasis_Hidden", "Desert_Barren", "Env_Zone2_Oasis"), (28, 30, 0, "biome")),
        (("default", False, True, "Zone3_Tier3", "Village_Outlander", "Forest_Frozen", "Env_Zone3_Outlander_Village"), (41, 43, 2, "biome")),
        (("default", False, True, "Zone4_Tier5", "Volcano_Wastes_Lava", "Wastes_Lava", "Env_Zone4_Volcanoes"), (55, 57, 0, "biome")),
        (("default", False, True, "Zone1_Shallow_Ocean", "Shore", "Shore", None), (1, 7, 0, "zone")),
        (("default", False, True, "Oceans", "Temperate_Kelp", "Temperate_Kelp", "Env_Zone0_Temperate"), (0, 0, 0, "default")),
        (("skywynn_z1", False, False, None, None, None, "Env_Zone1_Azure"), (16, 20, 0, "env")),
        (("skywynn_z1", False, False, None, None, None, "Env_Zone2_Somewhere"), (20, 24, 0, "zone")),
        (("island-abc", True, False, None, None, None, "Env_Default_Void"), (0, 0, 0, "island")),
        (("island-abc", False, False, None, None, None, "Env_Default_Void"), (0, 0, 0, "default")),
    ]
    for a, (lo, hi, bo, step) in NAMED:
        got = jres(*a)
        check(got[:4] == (lo, hi, bo, step), "R. %s -> %s, want %s" % (a, got, (lo, hi, bo, step)))
    Cfg.VOLCANIC = False
    got = jres("default", False, True, "Zone1_Tier1", "Plains_Smooth", "Plains_Smooth", "Env_Zone1_Caves_Volcanic_T1")
    check(got[:4] == (1, 3, 0, "biome"), "R. lava rule off -> the ground above (1-3): %s" % (got,))
    got = jres("skywynn_z1", False, False, None, None, None, "Env_Zone1_Caves_Volcanic_T3")
    check(got[:4] == (14, 18, 0, "env"), "R. lava rule off on a non-classic world -> the env row 14-18: %s" % (got,))
    Cfg.VOLCANIC = True
    print("R. lookup chain = Python mirror: %d cases (every region x biome x %d envs, %d envs non-classic) + %d named" % (
        n_cmp, len(ENVS), len(env_ids) + 3, len(NAMED)))

    # world rows + islands through the real loader (a hand-made bands file)
    P = JClass("java.util.Properties")
    cp, bp = Cfg.props(Cfg.DEF_CFG), Cfg.props(Cfg.DEF_BANDS)
    bp.setProperty("world.dungeon_", "20,23")
    bp.setProperty("world.hub", "0,0")
    bp.setProperty("world.bad", "abc")
    cp.setProperty("bands.islands", "1-3")
    Cfg.apply(cp, bp)
    check(jres("dungeon_1", False, True, "Zone1_Tier1", "Plains_Smooth", "Plains_Smooth", None)[:4] == (20, 23, 0, "world"), "R. world row dungeon_ (a name start) wins")
    check(jres("dungeon", False, True, "Zone1_Tier1", "Plains_Smooth", "Plains_Smooth", None)[:4] == (1, 3, 0, "biome"), "R. ... but not for the shorter name dungeon")
    check(jres("hub", False, True, "Zone1_Tier3", "Forest_Azure", "Forest_Azure", None)[:4] == (0, 0, 0, "world"), "R. world row 0,0 = no levels")
    check(jres("myisland", True, False, None, None, None, None)[:4] == (1, 3, 0, "island"), "R. bands.islands 1-3 on an island world")
    check("bad" not in [str(x) for x in Cfg.WORLD.raw], "R. a bad hand line (world.bad=abc) is skipped")
    bp2 = Cfg.props(Cfg.DEF_BANDS)
    bp2.setProperty("biome.Zone1_Tier1.*_Trork", "9,9")
    Cfg.apply(Cfg.props(Cfg.DEF_CFG), bp2)
    check(jres("default", False, True, "Zone1_Tier1", "Plains_Birch_Trork", "Plains_Birch", None)[:2] == (5, 7)
          and jres("default", False, True, "Zone1_Tier1", "Plains_Birch_Kweebec_Trork", "Plains_Birch", None)[:2] == (9, 9),
          "R. a hand-typed * key works at runtime; an exact row still beats it")
    Cfg.useDefaults()

    # ---------------- C. difficulty presets
    PRE = {"easy": (3.0, 1.5, "Easy 3% / 1.5%"), "normal": (4.0, 2.0, "Normal 4% / 2%"), "hard": (6.0, 3.0, "Hard 6% / 3%")}
    for d, (hp, dmg, txt) in PRE.items():
        Cfg.DIFFICULTY = d
        Cfg.derive(None)
        check(abs(float(Cfg.HP_STEP) - hp / 100) < 1e-12 and abs(float(Cfg.DMG_STEP) - dmg / 100) < 1e-12 and str(Cfg.difficultyText()) == txt,
              "C. %s = %s%% / %s%% (%s)" % (d, hp, dmg, Cfg.difficultyText()))
    Cfg.DIFFICULTY = "custom"
    Cfg.HP_PCT, Cfg.DMG_PCT = 5.5, 0.5
    Cfg.derive(None)
    check(abs(float(Cfg.HP_STEP) - 0.055) < 1e-12 and abs(float(Cfg.DMG_STEP) - 0.005) < 1e-12 and str(Cfg.difficultyText()) == "Custom 5.5% / 0.5%",
          "C. custom = the two rows (5.5 / 0.5): %s" % Cfg.difficultyText())
    Cfg.useDefaults()
    check(str(Cfg.DIFFICULTY) == "normal" and str(Cfg.difficultyText()) == "Normal 4% / 2%", "C. the default is Normal 4% / 2%")

    # ---------------- D. health / damage maths
    n = 0
    for d, (hp, dmg, _t) in list(PRE.items()) + [("custom", (12.0, 7.0, ""))]:
        Cfg.DIFFICULTY = d
        if d == "custom":
            Cfg.HP_PCT, Cfg.DMG_PCT = hp, dmg
        Cfg.derive(None)
        for L in range(0, 151):
            eh = 1.0 if L <= 1 else f32(min(5.0, max(1.0, 1.0 + (hp / 100) * (L - 1))))
            ed = 1.0 if L <= 1 else f32(min(3.0, max(1.0, 1.0 + (dmg / 100) * (L - 1))))
            if float(Cfg.hpMult(L)) != eh or float(Cfg.dmgMult(L)) != ed:
                check(False, "D. %s Lv %d: health x%s (want %s), damage x%s (want %s)" % (d, L, Cfg.hpMult(L), eh, Cfg.dmgMult(L), ed))
            n += 2
    OKS[0] += n
    Cfg.useDefaults()
    for L, h, dd in ((1, 1.0, 1.0), (10, 1.36, 1.18), (20, 1.76, 1.38), (30, 2.16, 1.58), (45, 2.76, 1.88), (60, 3.36, 2.18)):
        check(abs(float(Cfg.hpMult(L)) - h) < 1e-5 and abs(float(Cfg.dmgMult(L)) - dd) < 1e-5,
              "D. Normal Lv %d = health x%s, damage x%s (refit 4.3): %s / %s" % (L, h, dd, Cfg.hpMult(L), Cfg.dmgMult(L)))
    Cfg.DIFFICULTY = "hard"
    Cfg.derive(None)
    check(abs(float(Cfg.hpMult(60)) - 4.54) < 1e-5 and abs(float(Cfg.dmgMult(60)) - 2.77) < 1e-5, "D. Hard Lv 60 = x4.54 / x2.77 (caps x5 / x3 not hit)")
    check(float(Cfg.hpMult(100)) == 5.0 and float(Cfg.dmgMult(100)) == 3.0, "D. Hard Lv 100 is capped at x5 / x3")
    Cfg.HP_CAP = 2.0
    check(float(Cfg.hpMult(60)) == 2.0, "D. a lower cap clips (x2)")
    Cfg.useDefaults()
    print("D. maths: %d multipliers (4 difficulties x Lv 0-150, float32 exact) + the refit table + caps" % n)

    # ---------------- E. who gets a level
    roles, _z = vanilla_roles()
    nE = 0
    for nm, (att, root, path) in sorted(roles.items()):
        why = Cfg.whyNot(att, nm)
        got = why is None
        if got != expected_level(nm, att, root):
            check(False, "E. %s (%s, %s): whyNot = %s, expected %s" % (nm, att, root, why, "level" if expected_level(nm, att, root) else "none"))
        nE += 1
    OKS[0] += nE
    NAMED_E = [("HOSTILE", "Skeleton_Fighter", True), ("HOSTILE", "Trork_Warrior", True), ("NEUTRAL", "Boar", True),
               ("NEUTRAL", "Scarak_Defender", True), ("HOSTILE", "Scarak_Fighter", True), ("NEUTRAL", "Feran_Sharptooth", True),
               ("NEUTRAL", "Cow", False), ("NEUTRAL", "Sheep", False), ("HOSTILE", "Bluebird", False), ("HOSTILE", "Frog_Green", False),
               ("HOSTILE", "Mouse", False), ("NEUTRAL", "Kweebec_Merchant", False), ("NEUTRAL", "Klops_Merchant", False),
               ("NEUTRAL", "Kweebec_Razorleaf", False), ("NEUTRAL", "Feran_Civilian", False), ("REVERED", "Tamed_Boar", False),
               ("IGNORE", "Risen_Knight", False), ("HOSTILE", "Goblin_Duke", False), ("HOSTILE", "Trork_Chieftain", False),
               ("FRIENDLY", "Skeleton_Fighter", False), ("HOSTILE", "Floating_Pet_Blue", False), ("HOSTILE", "KazzyPets_Mount_Boar", False),
               ("HOSTILE", "KazzyPets_Mount_Cow_Undead", False), ("HOSTILE", "KazzyPets_Mount_Crawler_Void", False),
               ("HOSTILE", "Cow_Undead", True), ("HOSTILE", "Spectre_Void", True)]
    for att, nm, yes in NAMED_E:
        why = Cfg.whyNot(att, nm)
        check((why is None) == yes, "E. %s %s -> %s" % (att, nm, why))
    check(Cfg.whyNot("HOSTILE", None) is not None and Cfg.whyNot("HOSTILE", "") is not None, "E. no role (a player / not an NPC) -> no level")
    Cfg.NEUTRAL = False
    Cfg.derive(None)
    check(Cfg.whyNot("NEUTRAL", "Boar") is not None and Cfg.whyNot("HOSTILE", "Skeleton_Fighter") is None,
          "E. neutral fighters off: Boar refused, skeletons still levelled")
    Cfg.useDefaults()
    check(sum(1 for nm, v in roles.items() if expected_level(nm, v[0], v[1])) > 200, "E. (more than 200 vanilla roles get levels)")
    OTHER, LEFT = (), ()
    try:
        # review F1: other mods' roles that share a vanilla prefix (the old Bear_* / Wolf_* / Spider* / Wraith* / Dungeon_* patterns
        # levelled them in the reviewer's real-hook run and 193 roles of Skyy's Mods folder) - the built-in list is exact vanilla ids now
        OTHER = ("Bear_Grizzly_Mount", "Wolf_Pet", "Spider_Mount", "Wraith_Trader", "Dungeon_BlacksmithNPCRole", "Dungeon_Hub_NPC_Role",
                 "Dungeon_ArcaneNPCRole", "Dungeon_Crypt_Boss", "Skeleton_Pet_Knight", "Zombie_Mount", "Trork_Boss_Warlord", "Goblin_Trader")
        for nm in OTHER:
            check(nm not in roles, "E. (the sample %s is not a vanilla role)" % nm)
            for att in ("HOSTILE", "NEUTRAL"):
                check(Cfg.whyNot(att, nm) is not None, "E. F1: another mod's %s %s gets no level: %s" % (att, nm, Cfg.whyNot(att, nm)))
        check(str(Cfg.ROLES) == "" and len(Cfg.P_ROLES) == 0, "E. F1: Extra mobs that get levels is empty by default: %r" % str(Cfg.ROLES))
        built = set(str(x) for x in str(Cfg.VANILLA).split(","))
        want_built = set(nm for nm, v in roles.items() if expected_level(nm, v[0], v[1]))
        check(built == want_built, "E. F1: the built-in list = exactly the vanilla role ids that get levels (%d): %s" % (len(built), sorted(built ^ want_built)[:8]))
        check(not [x for x in built if "*" in x], "E. F1: the built-in list holds no * pattern")
        check(Cfg.whyNot("HOSTILE", "skeleton_FIGHTER") is None and Cfg.whyNot("HOSTILE", "Trork_Sentry") is None,
              "E. F1: built-in ids match in any case; Trork_Sentry stays levelled (no *_Sentry* guard)")
        # the extra row + its guard patterns (an admin pattern never catches other mods' mounts / pets / NPCs / bosses)
        Cfg.ROLES = "Mosshorn*, Bear_*, Dungeon_*"
        Cfg.derive(None)
        check(Cfg.whyNot("NEUTRAL", "Mosshorn") is None and Cfg.whyNot("NEUTRAL", "Mosshorn_Plain") is None and Cfg.whyNot("HOSTILE", "Dungeon_Ghoul") is None,
              "E. an extra pattern levels its mobs (Mosshorn*, Dungeon_Ghoul)")
        for nm in ("Bear_Grizzly_Mount", "Dungeon_Crypt_Boss", "Dungeon_Hub_NPC_Role", "Dungeon_BlacksmithNPCRole"):
            check(Cfg.whyNot("HOSTILE", nm) == "in Never level these", "E. F1: the guard patterns keep %s out under an extra pattern: %s" % (nm, Cfg.whyNot("HOSTILE", nm)))
        Cfg.NEUTRAL = False
        Cfg.derive(None)
        check(Cfg.whyNot("NEUTRAL", "Mosshorn") is not None, "E. an extra NEUTRAL mob also follows Neutral fighters get levels")
        Cfg.useDefaults()
        # review F10: a blank extra row no longer switches levelling off
        Cfg.ROLES = "  "
        Cfg.derive(None)
        check(Cfg.whyNot("HOSTILE", "Skeleton_Fighter") is None and Cfg.whyNot("NEUTRAL", "Boar") is None, "E. F10: a blank Extra mobs row keeps the vanilla mobs levelled")
        Cfg.useDefaults()
        # review F2 (question for Skyy, the safe default kept): the neutral animals with an attack stay unlevelled by default
        LEFT = ("Mosshorn", "Mosshorn_Plain", "Cow", "Horse", "Moose_Bull", "Moose_Cow", "Bison", "Ram", "Camel", "Antelope", "Goat", "Deer_Stag",
                "Horse_Skeleton", "Horse_Skeleton_Armored", "Kweebec_Razorleaf", "Kweebec_Razorleaf_Patrol")
        for nm in LEFT:
            check(roles.get(nm, ("",))[0] == "NEUTRAL" and Cfg.whyNot("NEUTRAL", nm) is not None, "E. F2: %s (neutral animal / guard) gets no level by default" % nm)
        # review F5: levels.exclude = * strips every level (the uninstall step)
        Cfg.EXCLUDE = "*"
        Cfg.derive(None)
        refused = [nm for nm, v in roles.items() if Cfg.whyNot(v[0], nm) is None]
        check(not refused and Cfg.whyNot("HOSTILE", "Skeleton_Fighter") == "in Never level these", "E. F5: Never level these = * -> no vanilla role gets a level: %s" % refused[:5])
        Cfg.useDefaults()
    except Exception as ex:
        check(False, "E. the review F1 / F2 / F5 / F10 checks could not run: %s" % ex)
        Cfg.useDefaults()
    print("E. who gets a level: %d vanilla roles = the classification, %d named cases; F1 %d other-mod roles, extras + guards, F10 blank "
          "extras, F2 %d neutral animals left out, F5 exclude *" % (nE, len(NAMED_E), len(OTHER), len(LEFT)))

    # ---------------- X. every role of the installed mods (read-only) that is not a vanilla role gets no level (review F1)
    mods_dir = B.MODS_DIR
    if os.path.isdir(mods_dir):
        other_roles, n_zip = set(), 0
        for fn_ in sorted(os.listdir(mods_dir)):
            if not fn_.lower().endswith((".jar", ".zip")):
                continue
            try:
                with zipfile.ZipFile(os.path.join(mods_dir, fn_)) as zz:
                    n_zip += 1
                    for e_ in zz.namelist():
                        m_ = re.search(r"(?:^|/)Server/NPC/Roles/(?:.*/)?([^/]+)\.json$", e_)
                        if m_ and m_.group(1) not in roles and not m_.group(1).startswith("_"):
                            other_roles.add(m_.group(1))
            except Exception:
                continue
        lev = sorted(nm for nm in other_roles if Cfg.whyNot("HOSTILE", nm) is None or Cfg.whyNot("NEUTRAL", nm) is None)
        check(not lev, "X. no role of another installed mod gets a level (%d roles in %d archives): %s" % (len(other_roles), n_zip, lev[:10]))
        print("X. installed mods: %d non-vanilla roles in %d archives, %d levelled" % (len(other_roles), n_zip, len(lev)))
    else:
        print("X. no Mods folder at %s - skipped" % mods_dir)

    # ---------------- G. nameplate text
    check(str(Lvl.plateText(9, "Trork Warrior")) == "[Lv 9] Trork Warrior", "G. colours off: [Lv 9] Trork Warrior")
    Cfg.COLOR_ON = True
    SEC = chr(167)
    exp = {"tag": "<color=#d6e4ee>[Lv 9] Trork Warrior</color>", "section": SEC + "f[Lv 9] Trork Warrior" + SEC + "r",
           "brace": "{#d6e4ee}[Lv 9] Trork Warrior"}
    for mk, e in exp.items():
        Cfg.MARKUP = mk
        got = str(Lvl.plateText(9, "Trork Warrior"))
        check(got == e, "G. %s markup: %r" % (mk, got))
        check(str(Lvl.plain(got)) == "[Lv 9] Trork Warrior" and bool(Lvl.isOurs(got)), "G. %s: plain() strips it back, isOurs" % mk)
    LAD = [(1, "#d6e4ee", "f"), (19, "#d6e4ee", "f"), (20, "#ffcc00", "6"), (29, "#ffcc00", "6"), (30, "#e8a93b", "6"),
           (45, "#ff6b6b", "c"), (60, "#ff6b6b", "c"), (61, "#cc66cc", "d"), (100, "#cc66cc", "d")]
    for L, hx, code in LAD:
        check(str(Lvl.hexFor(L)).lower() == hx and str(Lvl.legacy(hx)) == code, "G. Lv %d colour %s (section code %s): %s %s" % (
            L, hx, code, Lvl.hexFor(L), Lvl.legacy(hx)))
    Cfg.COLOR_ON = False
    Cfg.MARKUP = "tag"
    for t in ("1: <color=#ff6b6b>[Lv 9] Trork Warrior</color>", "2: " + SEC + "c[Lv 9] Trork Warrior" + SEC + "r", "3: {#ff6b6b}[Lv 9] Trork Warrior"):
        check(str(Lvl.plain(t)) == "[Lv 9] Trork Warrior" and bool(Lvl.isOurs(t)), "G. the platetest text %r is ours" % t[:12])
    check(not bool(Lvl.isOurs("Kweebec Merchant")) and not bool(Lvl.isOurs(None)), "G. a vanilla display name is not ours")
    for role, tk, nm in (("Skeleton_Fighter_Wander", None, "Skeleton Fighter"), ("Trork_Warrior", "server.npcRoles.Trork_Warrior.name", "Trork Warrior"),
                         ("Skeleton_Sand_Guard_Patrol", None, "Skeleton Sand Guard"), ("Boar", None, "Boar"), ("Bear_Grizzly_Sleep", None, "Bear Grizzly")):
        check(str(Lvl.nameOf(role, tk)) == nm, "G. name of %s without I18n = %r: %r" % (role, nm, Lvl.nameOf(role, tk)))
    Cfg.FORMAT = "{name} Lv.{level}"
    check(str(Lvl.plateText(12, "Hyena")) == "Hyena Lv.12" and bool(Lvl.isOurs("Hyena Lv.12")) and not bool(Lvl.isOurs("Hyena")),
          "G. a custom format {name} Lv.{level} renders and is recognised as ours")
    try:
        # review F7: after plate.format changes, a plate made with the default format or an earlier format of this run is still ours
        # (a mob that stops qualifying loses it); a vanilla / other mod's plate is not
        Cfg.useDefaults()
        Cfg.FORMAT = "<{level}> {name}"
        Cfg.derive(None)
        Cfg.FORMAT = "{name} Lv.{level}"
        Cfg.derive(None)
        check(bool(Lvl.isOurs("[Lv 9] Trork Warrior")), "G. F7: the default-format plate [Lv 9] Trork Warrior is still ours under {name} Lv.{level}")
        check(bool(Lvl.isOurs("<9> Boar")) and bool(Lvl.isOurs("Boar Lv.4")), "G. F7: a plate of a format used earlier this run is ours, and the current one")
        check(not bool(Lvl.isOurs("Kweebec Merchant")) and not bool(Lvl.isOurs("Bob")), "G. F7: a vanilla / hand-set name is still not ours")
        check(bool(Lvl.isOursFor("[Lv 9] Trork Warrior", "[Lv {level}] {name}")) and not bool(Lvl.isOursFor("[Lv 9] Trork Warrior", "{name} Lv.{level}"))
              and not bool(Lvl.isOursFor("x", None)), "G. F7: isOursFor checks one format")
        Cfg.useDefaults()
    except Exception as ex:
        check(False, "G. the review F7 checks could not run: %s" % ex)
        Cfg.useDefaults()
    print("G. nameplate: colours off, 3 markups, %d ladder colours, plain / isOurs, 5 names, F7 old formats" % len(LAD))

    # ---------------- F. persistence
    KP = str(Lvl.KEY_PREFIX)
    check(KP == "skyymobs_lv", "F. the save-slot key prefix is skyymobs_lv")
    for L in (1, 9, 17, 20, 60, 100, 999):
        check(int(Lvl.levelOfKey(str(Lvl.keyOf(L)))) == L, "F. key round trip %d" % L)
    for bad in ("NPC_Max", "skyymobs_lv", "skyymobs_lvx", "skyymobs_lv0", "skyymobs_lv12345", "Skyymobs_lv5", "skyymobs_level"):
        check(int(Lvl.levelOfKey(bad)) == -1, "F. %r is not a save slot" % bad)
    keys = JArray(JObject)(4)
    for i, k in enumerate(("NPC_Max", "Armor_Additive", "skyymobs_lv17", "junk")):
        keys[i] = JString(k)
    check(int(Lvl.savedFromKeys(keys)) == 17, "F. the saved level is read from the modifier keys (17)")
    check(Lvl.pick(-1, None) is None and str(Lvl.pick(17, JInt(5))[1]) == "saved" and int(Lvl.pick(-1, JInt(5))[0]) == 5
          and str(Lvl.pick(-1, JInt(5))[1]) == "kept", "F. pick: the save slot beats the session memory, else roll")
    MOBS, KEPT = Lvl.MOBS, Lvl.KEPT
    MI = JClass(PKG + "MobInfo")
    u1 = UUID.fromString("00000000-0000-0000-0000-0000000000a1")
    info = MI()
    info.level = 23
    info.world = "default"
    info.uuid = u1
    MOBS.put(u1, info)
    Lvl.forget(u1, True)
    check(MOBS.get(u1) is None and int(KEPT.get(u1)) == 23, "F. UNLOAD keeps the level in the session map (KEPT 23)")
    pk = Lvl.pick(-1, KEPT.remove(u1))
    check(int(pk[0]) == 23 and str(pk[1]) == "kept", "F. the reload (no save slot) gets 23 back from KEPT")
    MOBS.put(u1, info)
    Lvl.forget(u1, False)
    check(MOBS.get(u1) is None and KEPT.get(u1) is None, "F. REMOVE (death / despawn) forgets it everywhere")
    # deterministic roll = the Python mirror (layer 3)
    rnd = random.Random(7)
    nr = 0
    for _ in range(4000):
        seed = rnd.randrange(-(1 << 63), 1 << 63)
        msb, lsb = rnd.randrange(-(1 << 63), 1 << 63), rnd.randrange(-(1 << 63), 1 << 63)
        role = rnd.choice(["Skeleton_Fighter", "Trork_Warrior", "Boar", "", "Zombie_Aberrant_Big"])
        a = rnd.randrange(1, 60)
        b = a + rnd.randrange(0, 8)
        u = UUID(JLong(msb), JLong(lsb))
        got = int(Lvl.roll(JLong(seed), u, role, a, b))
        exp = py_roll(seed, msb, lsb, role, a, b)
        if got != exp:
            check(False, "F. roll(%d, %s, %s, %d, %d) = %d, mirror %d" % (seed, u, role, a, b, got, exp))
        if got != int(Lvl.roll(JLong(seed), u, role, a, b)):
            check(False, "F. roll is not deterministic")
        nr += 1
    OKS[0] += nr
    hist = collections.Counter(int(Lvl.roll(JLong(12345), UUID.randomUUID(), "Skeleton_Fighter", 18, 20)) for _ in range(3000))
    check(set(hist) == {18, 19, 20} and min(hist.values()) > 850, "F. the roll covers the band evenly (18-20: %s)" % dict(hist))
    res = Lvl.res(18, 20, 2, "biome", "Zone1_Tier3.Forest_Azure")
    check(20 <= int(Lvl.levelFor(res, JLong(1), u1, "Skeleton_Fighter")) <= 22, "F. levelFor adds the env bonus (18-20 +2)")
    Cfg.MAX_LEVEL = 21
    check(int(Lvl.levelFor(Lvl.res(30, 30, 0, "x", "y"), JLong(1), u1, "R")) == 21, "F. levelFor caps at levels.max")
    Cfg.useDefaults()
    check(int(Lvl.levelFor(Lvl.res(0, 0, 0, "default", "bands.default"), JLong(1), u1, "R")) == 0, "F. a 0-0 band = no level")
    for ov, om, nm_, want in ((50.0, 100.0, 164.0, 82.0), (100.0, 100.0, 164.0, 164.0), (0.0, 100.0, 164.0, 0.0), (150.0, 100.0, 50.0, 50.0)):
        check(abs(float(Lvl.share(ov, om, nm_)) - want) < 1e-4, "F. share(%s / %s -> max %s) = %s" % (ov, om, nm_, want))

    # a stand-in EntityStatMap / EntityStatValue (defined next to the engine classes, never in the jar) driving the jar's own code:
    # max = (100 + the additive sum) x the multiplicative SUM (EntityStatValue.computeModifiers, bytecode-checked)
    CP = JClass("javassist.ClassPool")(False)
    CP.appendSystemPath()
    CP.appendClassPath(B.SERVER_JAR)
    CtNewMethod, CtNewConstructor, CtField = JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor"), JClass("javassist.CtField")
    ESMN, ESVN = "com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap", "com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue"
    SMON = "com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier"
    MODN = "com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier"
    sv = CP.makeClass(ESVN.rsplit(".", 1)[0] + ".SkyyMobsTestValue", CP.get(ESVN))
    for f in ("public java.util.HashMap mods;", "public float[] cell;"):
        sv.addField(CtField.make(f, sv))
    sv.addConstructor(CtNewConstructor.make("public SkyyMobsTestValue(java.util.HashMap m, float[] c) { super(); this.mods = m; this.cell = c; }", sv))
    sv.addMethod(CtNewMethod.make(r"""
public static float maxOf(java.util.HashMap mods, float base) {
  float add = 0.0f, mul = 0.0f; boolean any = false;
  java.util.Iterator it = mods.values().iterator();
  while (it.hasNext()) {
    %s m = (%s) it.next();
    if (m.getCalculationType() == %s$CalculationType.ADDITIVE) add += m.getAmount(); else { mul += m.getAmount(); any = true; }
  }
  float mx = base + add;
  return any ? mx * mul : mx;
}""" % (SMON, SMON, SMON), sv))
    sv.addMethod(CtNewMethod.make("public float get() { return this.cell[0]; }", sv))
    sv.addMethod(CtNewMethod.make("public float getMax() { return maxOf(this.mods, this.cell[1]); }", sv))
    sv.addMethod(CtNewMethod.make("public java.util.Map getModifiers() { return this.mods; }", sv))
    sv.toClass(JClass(ESVN).class_)
    sm = CP.makeClass(ESMN.rsplit(".", 1)[0] + ".SkyyMobsTestMap", CP.get(ESMN))
    for f in ("public java.util.HashMap mods;", "public float[] cell;", "public int puts;"):
        sm.addField(CtField.make(f, sm))
    SVN = sv.getName()
    sm.addMethod(CtNewMethod.make("public void init() { if (this.mods == null) { this.mods = new java.util.HashMap(); this.cell = new float[] { 100.0f, 100.0f }; } }", sm))
    sm.addMethod(CtNewMethod.make("public float maxNow() { init(); return %s.maxOf(this.mods, this.cell[1]); }" % SVN, sm))
    sm.addMethod(CtNewMethod.make("public float val() { init(); return this.cell[0]; }", sm))
    sm.addMethod(CtNewMethod.make("public void setVal(float v) { init(); this.cell[0] = v; }", sm))
    sm.addMethod(CtNewMethod.make("public void clamp() { float mx = maxNow(); if (this.cell[0] > mx) this.cell[0] = mx; if (this.cell[0] < 0.0f) this.cell[0] = 0.0f; }", sm))
    sm.addMethod(CtNewMethod.make("public %s get(int i) { init(); return new %s(this.mods, this.cell); }" % (ESVN, SVN), sm))
    sm.addMethod(CtNewMethod.make("public %s putModifier(int i, String k, %s m) { init(); this.puts++; Object o = this.mods.put(k, m); clamp(); return (%s) o; }" % (MODN, MODN, MODN), sm))
    sm.addMethod(CtNewMethod.make("public %s getModifier(int i, String k) { init(); return (%s) this.mods.get(k); }" % (MODN, MODN), sm))
    sm.addMethod(CtNewMethod.make("public %s removeModifier(int i, String k) { init(); Object o = this.mods.remove(k); clamp(); return (%s) o; }" % (MODN, MODN), sm))
    sm.addMethod(CtNewMethod.make("public float maximizeStatValue(int i) { this.cell[0] = maxNow(); return this.cell[0]; }", sm))
    sm.addMethod(CtNewMethod.make("public float setStatValue(int i, float v) { init(); this.cell[0] = v; clamp(); return this.cell[0]; }", sm))
    ESMc = JClass(ESMN)
    TM = sm.toClass(ESMc.class_)
    TMc = JClass(TM.getName())
    fu = Cls.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
    fu.setAccessible(True)
    U = fu.get(None)

    def newmap():
        try:
            mm_ = TMc()
        except Exception:
            mm_ = U.allocateInstance(TM)
        mm_.init()
        return mm_
    SMOc, MTG = JClass(SMON), JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier$ModifierTarget")
    CAL = JClass(SMON + "$CalculationType")

    def fresh(npc_max=36.0):
        m = newmap()
        m.mods.put("NPC_Max", SMOc(MTG.MAX, CAL.ADDITIVE, JFloat(npc_max - 100.0)))
        m.setVal(JFloat(npc_max))
        return m
    m = fresh(36.0)
    u2 = UUID.fromString("00000000-0000-0000-0000-0000000000b2")
    i2 = Lvl.apply(None, None, None, None, m, u2, None, "default", "Skeleton_Fighter", 20, True, "biome", Lvl.res(18, 20, 0, "biome", "Zone1_Tier3.Forest_Azure"))
    mod = m.mods.get("skyymobs_lv20")
    check(mod is not None and abs(float(mod.getAmount()) - 1.76) < 1e-5 and abs(float(m.maxNow()) - 63.36) < 1e-3 and abs(float(m.val()) - 63.36) < 1e-3,
          "F. spawn: Skeleton Fighter (36 HP) Lv 20 -> modifier skyymobs_lv20 x1.76, 63 / 63 HP (refit 4.3: 63): %s / %s" % (m.val(), m.maxNow()))
    check(int(Lvl.savedLevel(m, 0)) == 20 and MOBS.get(u2) is not None and int(MOBS.get(u2).level) == 20 and str(i2.name) == "Skeleton Fighter",
          "F. the save slot reads 20; MOBS has the mob; name Skeleton Fighter")
    # the reload: a copy of the saved modifiers (what the entity codec stores) -> same key, nothing changes
    m2 = newmap()
    m2.mods.putAll(m.mods)
    m2.setVal(JFloat(40.0))
    saved = int(Lvl.savedLevel(m2, 0))
    puts = int(m2.puts)
    Lvl.apply(None, None, None, None, m2, u2, None, "default", "Skeleton_Fighter", saved, False, "saved", None)
    check(saved == 20 and int(m2.puts) == puts and abs(float(m2.val()) - 40.0) < 1e-4, "F. reload: level 20 from the save slot, modifier untouched, wounded 40 HP stays 40")
    # a curve change (Hard) before the reload: new amount, health share kept (40 / 63.36 -> same share of the new max)
    Cfg.DIFFICULTY = "hard"
    Cfg.derive(None)
    Lvl.apply(None, None, None, None, m2, u2, None, "default", "Skeleton_Fighter", saved, False, "saved", None)
    nm2 = 36.0 * f32(1.0 + 0.06 * 19)
    check(abs(float(m2.mods.get("skyymobs_lv20").getAmount()) - f32(2.14)) < 1e-5 and abs(float(m2.val()) - 40.0 / 63.36 * nm2) < 1e-2,
          "F. a curve change re-applies x2.14 and keeps the health share (%s HP of %s)" % (m2.val(), m2.maxNow()))
    Cfg.HEAL_ON_LOAD = True
    m2.setVal(JFloat(10.0))
    Cfg.DIFFICULTY = "normal"
    Cfg.derive(None)
    Lvl.apply(None, None, None, None, m2, u2, None, "default", "Skeleton_Fighter", saved, False, "saved", None)
    check(abs(float(m2.val()) - float(m2.maxNow())) < 1e-3, "F. healOnLoad on = full health after the reload")
    Cfg.useDefaults()
    # /mobs set 30 then strip
    Lvl.apply(None, None, None, None, m2, u2, None, "default", "Skeleton_Fighter", 30, False, "set", None)
    ks = sorted(str(k) for k in m2.mods.keySet())
    check(ks == ["NPC_Max", "skyymobs_lv30"] and int(MOBS.get(u2).level) == 30, "F. a new level replaces the old key (one save slot): %s" % ks)
    full = float(m2.val()) == float(m2.maxNow())
    Lvl.strip(None, None, None, m2, u2)
    ks = sorted(str(k) for k in m2.mods.keySet())
    check(ks == ["NPC_Max"] and MOBS.get(u2) is None and abs(float(m2.maxNow()) - 36.0) < 1e-4 and (not full or abs(float(m2.val()) - 36.0) < 1e-4),
          "F. strip: only NPC_Max left, 36 max, MOBS forgets the mob: %s" % ks)
    # the real EntityStatValue codec: the modifier key travels through BSON (the save path of every entity's stats)
    codec_note = ""
    try:
        ESV = JClass(ESVN)
        v = U.allocateInstance(ESV.class_)

        def setf(o, name, val):
            fld = ESV.class_.getDeclaredField(name)
            fld.setAccessible(True)
            fld.set(o, val)
        mods = HashMap()
        mods.put("skyymobs_lv17", SMOc(MTG.MAX, CAL.MULTIPLICATIVE, JFloat(1.64)))
        mods.put("NPC_Max", SMOc(MTG.MAX, CAL.ADDITIVE, JFloat(-64.0)))
        setf(v, "id", JString("Health"))
        setf(v, "value", JFloat(50.0))
        setf(v, "modifiers", mods)
        # what EntityStatsModule.setup registers; EntityStatMap.CODEC is codecVersion(5) + legacyVersioned, so its nested values are
        # written / read with a VersionedExtraInfo (the plain ExtraInfo.getVersion() is always Integer.MAX_VALUE and would skip the
        # version-ranged CalculationType field of StaticModifier.ENTITY_CODEC)
        MODc = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier")
        MODc.CODEC.register("Boost", SMOc.class_, SMOc.ENTITY_CODEC)
        MODc.CODEC.register("Static", SMOc.class_, SMOc.ENTITY_CODEC)
        VEI = JClass("com.hypixel.hytale.codec.VersionedExtraInfo")
        EMPTY = JClass("com.hypixel.hytale.codec.EmptyExtraInfo").EMPTY
        bson = ESV.CODEC.encode(v, VEI(5, EMPTY))
        v2 = ESV.CODEC.decode(bson, VEI(5, EMPTY))
        mm = v2.getModifiers()
        got = mm.get("skyymobs_lv17") if mm is not None else None
        ok = got is not None and abs(float(got.getAmount()) - 1.64) < 1e-5 and str(got.getCalculationType().name()) == "MULTIPLICATIVE" \
            and str(got.getTarget().name()) == "MAX"
        check(ok, "F. the entity stat codec (version 5) keeps skyymobs_lv17 = MAX MULTIPLICATIVE x1.64 through BSON: %s" % str(bson.toJson())[:300])
        check(int(Lvl.savedFromKeys(mm.keySet().toArray())) == 17, "F. ... and the jar reads level 17 back from the decoded map")
        codec_note = str(bson.toJson())
    except Exception as ex:
        check(False, "F. the EntityStatValue codec round trip could not run: %s" % ex)
    print("F. persistence: key round trip, pick / forget / KEPT, %d rolls = mirror, stand-in stat map (spawn 63 / 63 HP, reload untouched, "
          "curve change keeps the share, healOnLoad, set 30, strip), codec %s" % (nr, codec_note[:160]))

    # ---------------- I. mob:fn:level
    Fn = JClass(PKG + "MobLevelFn")()
    MOBS.clear()
    u3 = UUID.fromString("00000000-0000-0000-0000-0000000000c3")
    i3 = MI()
    i3.level, i3.world, i3.uuid = 14, "default", u3

    def call(*a):
        arr = JArray(JObject)(len(a))
        for k, x in enumerate(a):
            arr[k] = x
        return Fn.apply(arr)
    check(int(call("default", u3)) == -1, "I. unknown mob -> -1")
    MOBS.put(u3, i3)
    r = call("default", u3)
    check(str(r.getClass().getName()) == "java.lang.Integer" and int(r) == 14, "I. Object[]{world, uuid} -> Integer 14 (%s)" % r.getClass().getName())
    check(int(call("other_world", u3)) == -1 and int(call(None, u3)) == 14 and int(Fn.apply(u3)) == 14 and int(call(u3)) == 14,
          "I. wrong world -> -1; null world / bare UUID / Object[]{uuid} -> 14")
    for bad in (None, "x", JInt(5)):
        check(int(Fn.apply(bad)) == -1, "I. bad input %r -> -1" % (bad,))
    check(int(call()) == -1 and int(call("default", "not-a-uuid")) == -1 and int(call("default")) == -1, "I. short / wrong arrays -> -1")
    errs = []

    def hammer(k):
        try:
            for j in range(3000):
                uu = UUID(JLong(k), JLong(j))
                if j % 3 == 0:
                    ii = MI()
                    ii.level, ii.world, ii.uuid = j % 60 + 1, "default", uu
                    MOBS.put(uu, ii)
                rr = call("default", uu)
                if not (int(rr) == -1 or 1 <= int(rr) <= 60):
                    errs.append(int(rr))
                MOBS.remove(uu)
        except Exception as ex:
            errs.append(str(ex))
    ths = [threading.Thread(target=hammer, args=(k,)) for k in range(8)]
    for t in ths:
        t.start()
    for t in ths:
        t.join()
    check(not errs, "I. 8 threads x 3000 calls while the map changes: no error / bad value (%s)" % errs[:3])
    br = Lvl.bridge()
    SysC = JClass("java.lang.System")
    check(int(SysC.identityHashCode(br)) == int(SysC.identityHashCode(SysC.getProperties().get("skyy.bridge"))),
          "I. the bridge map is System.getProperties().get(skyy.bridge)")
    MOBS.clear()
    print("I. mob:fn:level: Integer level, -1 for unknown / wrong world / bad input, 24,000 threaded calls")

    # stand-in engine objects (Unsafe.allocateInstance + their real fields; plain getters, bytecode-checked: World.getName / getChunkStore /
    # getWorldConfig / getEntityStore, ChunkStore.getGenerator (generatorLock + generator), EntityStore.getRefFromUUID (entitiesByUuid),
    # Ref.isValid (index != MIN_VALUE)) - never a real world
    def setfield(o, cls_name, name, val):
        c_ = JClass(cls_name).class_
        while c_ is not None:
            try:
                f_ = c_.getDeclaredField(name)
            except Exception:
                c_ = c_.getSuperclass()
                continue
            f_.setAccessible(True)
            f_.set(o, val)
            return
        raise KeyError(name)
    WN = "com.hypixel.hytale.server.core.universe.world.World"
    CSN = "com.hypixel.hytale.server.core.universe.world.storage.ChunkStore"
    ESN = "com.hypixel.hytale.server.core.universe.world.storage.EntityStore"
    REFN = "com.hypixel.hytale.component.Ref"
    AL = JClass("java.util.ArrayList")
    SysJ = JClass("java.lang.System")

    # ---------------- W. the worldgen cache (review F3)
    try:
        # (no WorldConfig: its static init needs the asset stores, so the classic branch below throws at the seed read - the same
        # try / not-cached path as the generator cache that is not ready, which is checked to throw on its own)
        w_ = U.allocateInstance(JClass(WN).class_)
        cs_ = U.allocateInstance(JClass(CSN).class_)
        setfield(w_, WN, "name", "wgtest")
        setfield(w_, WN, "chunkStore", cs_)
        setfield(cs_, CSN, "generatorLock", JClass("java.util.concurrent.locks.StampedLock")())
        WGm = Lvl.WG
        WGm.clear()
        r_ = Lvl.worldgen(w_, 5, 9)
        check(str(r_[4]) == "0" and int(WGm.size()) == 0, "W. F3: no generator attached yet -> no classic data, NOT cached: %s" % sorted(str(k) for k in WGm.keySet()))
        setfield(cs_, CSN, "generator", U.allocateInstance(JClass("com.hypixel.hytale.server.worldgen.chunk.ChunkGenerator").class_))
        try:
            w_.getChunkStore().getGenerator().getZoneBiomeResultAt(1, 5, 9)
            threw = False
        except Exception:
            threw = True
        r_ = Lvl.worldgen(w_, 5, 9)
        check(threw and str(r_[4]) == "0" and int(WGm.size()) == 0,
              "W. F3: a ChunkGenerator world whose lookup throws (generator cache / world config not ready) -> the fallback rows, NOT cached: %s" % sorted(str(k) for k in WGm.keySet()))

        @JImplements("com.hypixel.hytale.server.core.universe.world.worldgen.IWorldGen")
        class FlatGen(object):
            @JOverride
            def shutdown(self): pass
            @JOverride
            def generate(self, *a): return None
            @JOverride
            def getTimings(self): return None
            @JOverride
            def getSpawnPoints(self, *a): return None
            @JOverride
            def getDefaultSpawnProvider(self, *a): return None
        setfield(cs_, CSN, "generator", FlatGen())
        r_ = Lvl.worldgen(w_, 5, 9)
        Lvl.worldgen(w_, 6, 9)
        Lvl.worldgen(w_, 5, 9)
        keys_ = sorted(str(k) for k in WGm.keySet())
        check(str(r_[4]) == "0" and keys_ == ["wgtest:5:9", "wgtest:6:9"],
              "W. F3: a non-classic generator (void / flat world) IS cached, one entry per exact block column (no 8x8 cell): %s" % keys_)
        check(int(Lvl.WG_MAX) == 10000, "W. the cache is bounded (WG_MAX 10000, cleared when full)")
        WGm.clear()
        print("W. worldgen cache: missing generator + throwing ChunkGenerator not cached, non-classic cached per exact column")
    except Exception as ex:
        check(False, "W. the worldgen cache section could not run: %s" % ex)

    # ---------------- N. the prune (review F6)
    try:
        WeakRef = JClass("java.lang.ref.WeakReference")
        now = int(SysJ.currentTimeMillis())
        wa, wb = JClass("java.lang.Object")(), JClass("java.lang.Object")()

        def mob(i, wref, world, age):
            ii = MI()
            ii.uuid = UUID.fromString("00000000-0000-0000-0002-%012d" % i)
            ii.wref, ii.world, ii.level, ii.at = wref, world, 5, JLong(now - age)
            MOBS.put(ii.uuid, ii)
            return ii.uuid
        MOBS.clear()
        ua = mob(1, WeakRef(wa), "a", 120000)          # its world is loaded -> kept
        mob(2, WeakRef(wb), "b", 120000)               # its world was removed -> pruned
        mob(3, WeakRef(None), "c", 120000)             # its world object was collected -> pruned
        ud = mob(4, None, "w1", 120000)                # no reference, a loaded world name -> kept
        mob(5, None, "gone", 120000)                   # no reference, no such world -> pruned
        uf = mob(6, WeakRef(wb), "b", 1000)            # removed world, but added 1 s ago (60 s grace) -> kept
        MOBS.put(UUID.fromString("00000000-0000-0000-0002-000000000007"), "junk")   # not a MobInfo -> pruned
        lw, ln = AL(), AL()
        lw.add(wa)
        ln.add("w1")
        ln.add("a")
        n_ = int(Lvl.pruneWith(lw, ln, JLong(now)))
        left = sorted(str(k) for k in MOBS.keySet())
        check(n_ == 4 and left == sorted(str(x) for x in (ua, ud, uf)), "N. F6: pruneWith forgets removed / collected worlds' mobs (4), keeps loaded, by-name and young ones: %d, %s" % (n_, left))
        uh = mob(8, None, "zzz", 120000)
        check(int(Lvl.pruneWith(lw, None, JLong(now))) == 0 and MOBS.get(uh) is not None, "N. names unknown -> a mob without a world reference is kept")
        # pruneWorld on a stand-in world: gone and invalid refs are forgotten, live / young / other-world entries stay
        es_ = U.allocateInstance(JClass(ESN).class_)
        byu = HashMap()
        setfield(es_, ESN, "entitiesByUuid", byu)
        wp = U.allocateInstance(JClass(WN).class_)
        setfield(wp, WN, "name", "prunetest")
        setfield(wp, WN, "entityStore", es_)
        good, bad = U.allocateInstance(JClass(REFN).class_), U.allocateInstance(JClass(REFN).class_)
        setfield(bad, REFN, "index", JInt(-2147483648))
        check(bool(good.isValid()) and not bool(bad.isValid()), "N. (stand-in refs: one valid, one invalid)")
        MOBS.clear()
        p1 = mob(11, WeakRef(wp), "prunetest", 120000)
        byu.put(p1, good)
        mob(12, WeakRef(wp), "prunetest", 120000)
        p3 = mob(13, WeakRef(wp), "prunetest", 120000)
        byu.put(p3, bad)
        p4 = mob(14, WeakRef(wp), "prunetest", 1000)
        p5 = mob(15, WeakRef(wa), "a", 120000)
        k_ = int(Lvl.pruneWorld(wp, JLong(now)))
        left = sorted(str(k) for k in MOBS.keySet())
        check(k_ == 2 and left == sorted(str(x) for x in (p1, p4, p5)), "N. F6: pruneWorld forgets the mobs whose entity is gone / invalid (2): %d, %s" % (k_, left))
        check(bool(Lvl.hasMobsIn(wp)) and not bool(Lvl.hasMobsIn(wb)), "N. hasMobsIn finds the world of a levelled mob by identity")
        p6 = mob(16, WeakRef(wp), "prunetest", 120000)
        PT_ = JClass(PKG + "MobPruneTask")
        PT_(wp).run()
        check(MOBS.get(p6) is None and MOBS.get(p1) is not None, "N. MobPruneTask(world) runs pruneWorld")
        before = int(MOBS.size())
        PT_(None).run()
        check(Lvl.liveWorlds() is None and int(MOBS.size()) == before, "N. MobPruneTask(null) without a Universe (bare JVM) changes nothing")
        # apply() keeps a WEAK reference to the mob's world
        m9 = fresh(36.0)
        u9 = UUID.fromString("00000000-0000-0000-0002-000000000099")
        i9 = Lvl.apply(None, None, None, None, m9, u9, wp, "prunetest", "Skeleton_Fighter", 5, True, "biome", None)
        check(i9.wref is not None and int(SysJ.identityHashCode(i9.wref.get())) == int(SysJ.identityHashCode(wp)) and str(i9.world) == "prunetest",
              "N. apply() stores a weak reference to the World")
        MOBS.clear()
        print("N. prune: pruneWith (removed, collected, by name, grace, junk), pruneWorld (gone / invalid refs), MobPruneTask both modes, apply wref")
    except Exception as ex:
        check(False, "N. the prune section could not run: %s" % ex)

    # ---------------- T. /mobs platetest: one test per mob (review F11)
    try:
        PSt = JClass(PKG + "MobPlateStep")
        RUN = PSt.RUNNING
        RUN.clear()
        ut = UUID.fromString("00000000-0000-0000-0003-000000000001")
        check(bool(PSt.claim(ut, JLong(1000))) and not bool(PSt.claim(ut, JLong(2000))), "T. F11: a second plate test on the same mob is refused while one runs")
        check(bool(PSt.claim(ut, JLong(40000))), "T. F11: a claim older than 30 s (the world stopped mid-test) is taken over")
        check(not bool(PSt.claim(None, JLong(1))), "T. no uuid -> no claim")
        tx = JArray(JString)(1)
        tx[0] = "1: x"
        PSt(None, ut, tx, None, None, "Boar").run()          # no world: the step fails at once -> the finally releases the claim
        check(RUN.get(ut) is None and bool(PSt.claim(ut, JLong(50000))), "T. F11: a plate test that stops releases its claim; the mob can be tested again")
        RUN.clear()
        print("T. platetest claims: one per mob, stale takeover, released on every end path")
    except Exception as ex:
        check(False, "T. the platetest section could not run: %s" % ex)

    # ---------------- H. permissions (the engine's own code)
    root = JClass(PKG + "MobsCmd")()
    subs = root.getSubCommands()
    SUBS = dict((str(k), subs.get(k)) for k in subs.keySet())
    check(sorted(SUBS) == ["info", "inspect", "platetest", "reload", "set"], "H. /mobs sub-commands: %s" % sorted(SUBS))
    check([str(x) for x in root.getPermissionGroups()] == ["hytale:Adventurer"], "H. /mobs gives its node to hytale:Adventurer")
    check([str(x) for x in SUBS["info"].getPermissionGroups()] == ["hytale:Adventurer"], "H. /mobs info gives its node to hytale:Adventurer")
    for k in ("inspect", "set", "platetest", "reload"):
        c = SUBS[k]
        g = c.getPermissionGroups()
        check(str(c.getPermission()) == "skyymobs.admin" and g is not None and len(g) == 0, "H. /mobs %s: requirePermission skyymobs.admin + no groups (%s, %s)" % (
            k, c.getPermission(), g))
    try:
        fu = Cls.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
        fu.setAccessible(True)
        U = fu.get(None)
        own = U.allocateInstance(JClass("com.hypixel.hytale.server.core.command.system.CommandManager").class_)
        root.setOwner(own)
    except Exception as ex:
        print("   no CommandManager owner (%s)" % ex)
    rec = root.getPermissionGroupsRecursive()
    grp = dict((str(k), sorted(str(x) for x in rec.get(k))) for k in rec.keySet())
    allnodes = [n for v in grp.values() for n in v]
    check(list(grp) == ["hytale:Adventurer"] and len(grp["hytale:Adventurer"]) == 2 and "skyymobs.admin" not in allnodes,
          "H. the virtual groups: only hytale:Adventurer, holding exactly the two player nodes (/mobs, /mobs info), never skyymobs.admin: %s" % grp)
    PM = JClass("com.hypixel.hytale.server.core.permissions.PermissionsModule")
    HashSet, ArrayList = JClass("java.util.HashSet"), JClass("java.util.ArrayList")

    def jset(*xs):
        s = HashSet()
        for x in xs:
            s.add(x)
        return s
    USERS = {"plain": ([], ["hytale:Adventurer"]), "op": ([], ["hytale:Admin"]), "holder": (["skyymobs.admin"], ["hytale:Adventurer"]),
             "skyystar": (["skyy.*"], ["hytale:Adventurer"])}
    IDS = dict((k, UUID.fromString("00000000-0000-0000-0001-%012d" % (i + 1))) for i, k in enumerate(sorted(USERS)))
    BY = dict((str(v), k) for k, v in IDS.items())
    GROUPS = {"hytale:Admin": ["*"], "hytale:Adventurer": []}

    @JImplements("com.hypixel.hytale.server.core.permissions.provider.PermissionProvider")
    class Prov:
        @JOverride
        def getName(self): return "mobs-test"
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

    def jfield(cls, name):
        c = cls.class_
        while c is not None:
            try:
                f = c.getDeclaredField(name)
                f.setAccessible(True)
                return f
            except Exception:
                c = c.getSuperclass()
        raise KeyError(name)
    perm_ok = True
    try:
        pm = U.allocateInstance(PM.class_)
        provs = ArrayList()
        provs.add(Prov())
        jfield(PM, "providers").set(pm, provs)
        virt = HashMap()
        for k in rec.keySet():
            virt.put(k, HashSet(rec.get(k)))
        jfield(PM, "virtualGroups").set(pm, virt)
        f_inst = jfield(PM, "instance")
        old_pm = f_inst.get(None)
        f_inst.set(None, pm)
    except Exception as ex:
        perm_ok = False
        check(False, "H. could not set up a PermissionsModule stand-in: %s" % ex)
    if perm_ok:
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
                s = Sender(who)
                check(bool(root.hasPermission(s)) and bool(SUBS["info"].hasPermission(s)), "H. %s may run /mobs and /mobs info" % who)
                for k in ("inspect", "set", "platetest", "reload"):
                    check(bool(SUBS[k].hasPermission(s)) == admin, "H. /mobs %s %s for %s" % (k, "allowed" if admin else "refused", who))
        finally:
            f_inst.set(None, old_pm)
    print("H. permissions: /mobs + /mobs info for every player; inspect / set / platetest / reload only with skyymobs.admin or op")

    # ---------------- K. the config kit (Server Setup > Mobs)
    mods = os.path.join(SCRATCH, "kit", "mods")
    home = os.path.join(mods, "Skyy_SkyyMobs")
    shutil.rmtree(os.path.dirname(mods), ignore_errors=True)
    os.makedirs(home)
    Cfg.DIR = Paths.get(home)
    Cfg.FILE = Paths.get(os.path.join(home, "config.properties"))
    Cfg.BANDS = Paths.get(os.path.join(home, "bands.properties"))
    Cfg.load()
    cfgf, bandf = os.path.join(home, "config.properties"), os.path.join(home, "bands.properties")
    check(os.path.isfile(cfgf) and os.path.isfile(bandf), "K. load() seeds config.properties + bands.properties")
    check(open(cfgf, "rb").read() == str(Cfg.DEF_CFG).encode("latin-1") and open(bandf, "rb").read() == str(Cfg.DEF_BANDS).encode("latin-1"),
          "K. the seeded files are exactly the default texts")
    Pub = JClass(PKG + "CfgPub")
    Pub.start(Paths.get(mods), None)
    BR = Lvl.bridge()
    hdr, fn = BR.get("config:def:SkyyMobs"), BR.get("config:fn:SkyyMobs")
    if not check(hdr is not None and fn is not None, "K. config:def + config:fn:SkyyMobs published"):
        return
    rows = [[str(x) for x in row] for row in hdr[7]]
    check(str(hdr[0]) == "1" and str(hdr[1]) == "SkyyMobs" and str(hdr[2]) == "Mobs" and str(hdr[3]) == VERSION and str(hdr[4]) == "skyymobs.admin"
          and [str(x) for x in hdr[5]] == ["levels", "strength", "bands", "plate"]
          and str(hdr[8]) == "Skyy_SkyyMobs/config.properties,Skyy_SkyyMobs/bands.properties", "K. header: %s" % [str(hdr[i]) for i in (0, 1, 2, 3, 4, 8)])
    keys = [r_[0] for r_ in rows]
    check(len(rows) == 25 and keys[0] == "part.levels", "K. 25 rows: %s" % keys)

    def op(*a):
        arr = JArray(JObject)(len(a))
        for k, x in enumerate(a):
            arr[k] = x
        return fn.apply(arr)

    def settle():
        Pub.flush()
        time.sleep(0.7)
        Pub.flush()
        time.sleep(0.3)
    dfl = dict((r_[0], r_[4]) for r_ in rows)
    for r_ in rows:
        if r_[3] not in ("table",):
            check(str(op("get", r_[0])) == r_[4], "K. get %s = its default %r" % (r_[0], r_[4]))
    r = op("set", "strength.difficulty", "hard", None, None, "yes", "console")
    check(str(r[0]) == "ok" and str(Cfg.DIFFICULTY) == "hard" and abs(float(Cfg.HP_STEP) - 0.06) < 1e-12, "K. Difficulty = Hard through the kit: live at once (after= derive): %s" % [str(x) for x in r])
    r = op("set", "strength.hp", "101", None, None, "yes", "console")
    check(str(r[0]) == "bad", "K. Custom health 101%% refused: %s" % [str(x) for x in r])
    r = op("set", "plate.format", "Lv {lvl} {name}", None, None, "yes", "console")
    check(str(r[0]) == "bad" and str(Cfg.FORMAT) == "[Lv {level}] {name}", "K. a plate format without {level} refused (check hook): %s" % [str(x) for x in r])
    r = op("set", "plate.format", "{name} [{level}]", None, None, "yes", "console")
    check(str(r[0]) == "ok" and str(Lvl.plateText(4, "Boar")) == "Boar [4]", "K. a new plate format applies: %s" % Lvl.plateText(4, "Boar"))
    try:
        check(bool(Cfg.FORMATS.containsKey("{name} [{level}]")) and bool(Lvl.isOurs("[Lv 4] Boar")) and bool(Lvl.isOurs("Boar [4]")),
              "K. F7: plate.format runs derive (after=): the new format is remembered, a default-format plate is still ours")
    except Exception as ex:
        check(False, "K. F7 check could not run: %s" % ex)
    # review F1 / F5 / F10 through the real kit: the extra row takes patterns and a blank, Never level these takes *
    check(str(op("get", "levels.roles")) == "", "K. F1: Extra mobs that get levels is empty by default")
    r = op("set", "levels.roles", "Mosshorn*", None, None, "yes", "console")
    check(str(r[0]) == "ok" and Cfg.whyNot("NEUTRAL", "Mosshorn") is None, "K. F1: levels.roles = Mosshorn* levels Mosshorn: %s" % [str(x) for x in r])
    r = op("set", "levels.roles", "", None, None, "yes", "console")
    check(str(r[0]) == "ok" and Cfg.whyNot("NEUTRAL", "Mosshorn") is not None and Cfg.whyNot("HOSTILE", "Skeleton_Fighter") is None,
          "K. F10: a blank levels.roles keeps the vanilla mobs levelled: %s" % [str(x) for x in r])
    r = op("set", "levels.exclude", "*", None, None, "yes", "console")
    check(str(r[0]) == "ok" and Cfg.whyNot("HOSTILE", "Skeleton_Fighter") == "in Never level these", "K. F5: levels.exclude = * (uninstall) is accepted and strips all: %s" % [str(x) for x in r])
    r = op("set", "levels.exclude", str(dfl["levels.exclude"]), None, None, "yes", "console")
    check(str(r[0]) == "ok" and Cfg.whyNot("HOSTILE", "Skeleton_Fighter") is None, "K. levels.exclude back to its default")
    r = op("set", "bands.islands", "1-3", None, None, "yes", "console")
    check(str(r[0]) == "ok" and int(Cfg.ISL_A) == 1 and int(Cfg.ISL_B) == 3, "K. Private islands 1-3 (range) live")
    r = op("set", "levels.max", "0", None, None, "yes", "console")
    check(str(r[0]) == "bad" and int(Cfg.MAX_LEVEL) == 100, "K. Highest mob level 0 refused")
    r = op("set", "part.levels", "false", None, None, "", "console")
    check(str(r[0]) == "confirm" and bool(Cfg.ON), "K. switching Mob levels OFF asks first (part, danger)")
    r = op("set", "part.levels", "false", None, None, "yes", "console")
    check(str(r[0]) == "ok" and not bool(Cfg.ON), "K. ... and applies after yes")
    op("set", "part.levels", "true", None, None, "yes", "console")
    settle()
    txt = open(cfgf, "rb").read().decode("latin-1")
    check("\nstrength.difficulty=hard\n" in txt and "\nplate.format={name} [{level}]\n" in txt and "\nbands.islands=1-3\n" in txt
          and txt.count("strength.difficulty=") == 1, "K. the file lines changed in place")
    ks = op("keys", "bands.biome", "")
    ents = [str(x) for x in ks[0]]
    vals = dict(zip(ents, [str(x) for x in ks[2]]))
    check(len(ents) == int(Cfg.BIOME.n) and vals.get("Zone1_Tier3.Forest_Azure") == "18|20" and vals.get("Zone1_Tier3") == "12|20",
          "K. bands.biome lists every row (%d), Forest_Azure 18|20, the region row Zone1_Tier3 12|20" % len(ents))
    r = op("tset", "bands.biome", "Zone1_Tier3.Forest_Azure", "17|20", None, None, "yes", "console")
    check(str(r[0]) == "ok", "K. tset Forest_Azure 17|20: %s" % [str(x) for x in r])
    r = op("tset", "bands.biome", "Zone1_Tier3.Forest_Azure", "21|20", None, None, "yes", "console")
    check(str(r[0]) == "bad", "K. Min above Max refused (checkBand): %s" % [str(x) for x in r])
    r = op("add", "bands.world", "dungeon_*", "20|23", None, None, "yes", "console")
    check(str(r[0]) == "bad", "K. a * in a table entry is refused by the kit (why the tables ship without patterns): %s" % [str(x) for x in r])
    r = op("add", "bands.world", "dungeon_", "20|23", None, None, "yes", "console")
    check(str(r[0]) == "ok", "K. add a world row dungeon_ 20|23: %s" % [str(x) for x in r])
    r = op("tset", "bands.biome", "Zone1_Tier3", "13|20", None, None, "yes", "console")
    check(str(r[0]) == "ok", "K. the region row Zone1_Tier3 is editable in game: %s" % [str(x) for x in r])
    r = op("add", "bands.env", "Env_Zone1_Test", "3|4|1", None, None, "yes", "console")
    check(str(r[0]) == "ok", "K. add an env row with a bonus: %s" % [str(x) for x in r])
    r = op("tset", "plate.colors", "20", "#123456", None, None, "yes", "console")
    check(str(r[0]) == "ok", "K. plate.colors 20 = #123456: %s" % [str(x) for x in r])
    for e_, v_ in (("20", "red"), ("abc", "#ffffff"), ("0", "#ffffff")):
        r = op("tset", "plate.colors", e_, v_, None, None, "yes", "console")
        check(str(r[0]) == "bad", "K. plate.colors %s = %s refused: %s" % (e_, v_, [str(x) for x in r]))
    settle()
    bt = open(bandf, "rb").read().decode("latin-1")
    check("\nbiome.Zone1_Tier3.Forest_Azure=17,20\n" in bt and "world.dungeon_=20,23" in bt and "env.Env_Zone1_Test=3,4,1" in bt
          and "\nbiome.Zone1_Tier3=13,20\n" in bt,
          "K. bands.properties lines written (17,20 in place; the new rows appended)")
    check(jres("default", False, True, "Zone1_Tier3", "Forest_Azure", "Forest_Azure", None)[:2] == (17, 20)
          and jres("dungeon_7", False, True, "Zone1_Tier1", "Plains_Smooth", "Plains_Smooth", None)[:4] == (20, 23, 0, "world")
          and str(Lvl.hexFor(25)) == "#123456", "K. the reload routine (MobCfg.reloadAll) applied the table changes: %s / %s / %s" % (
              jres("default", False, True, "Zone1_Tier3", "Forest_Azure", "Forest_Azure", None)[:2], jres("dungeon_7", False, True, None, None, None, None)[:4], Lvl.hexFor(25)))
    r = op("remove", "bands.world", "dungeon_", None, None, "yes", "console")
    check(str(r[0]) == "ok", "K. remove the world row: %s" % [str(x) for x in r])
    settle()
    check(int(Cfg.WORLD.n) == 0, "K. the world row is gone after the reload routine")
    # a hand edit + the reload op
    open(bandf, "ab").write(b"zone.Zone5=60,75\n")
    r = op("reload", None, None, "console")
    settle()
    check(str(r[0]) == "ok" and Cfg.ZONE.find("Zone5") >= 0, "K. a hand-edited line + reload -> zone.Zone5 60-75 in memory: %s" % [str(x) for x in r])
    r = op("set", "strength.difficulty", "normal", None, None, "yes", "console")
    Pub.shutdown()
    print("K. config kit: 25 rows (4 categories), get = defaults, set live + refused + confirm, 5 table ops through the real kit + the "
          "reload routine, hand edit + reload op")

    # ---------------- S. start twice (no churn)
    sd = os.path.join(SCRATCH, "twice", "mods")
    sh = os.path.join(sd, "Skyy_SkyyMobs")
    shutil.rmtree(os.path.dirname(sd), ignore_errors=True)
    os.makedirs(sh)

    def start():
        Cfg.DIR = Paths.get(sh)
        Cfg.FILE = Paths.get(os.path.join(sh, "config.properties"))
        Cfg.BANDS = Paths.get(os.path.join(sh, "bands.properties"))
        Cfg.load()
        Pub.start(Paths.get(sd), None)
        Pub.flush()
        time.sleep(0.6)
        Pub.shutdown()

    def snap():
        out = {}
        for dp, _dn, fns in os.walk(sd):
            for f_ in fns:
                p_ = os.path.join(dp, f_)
                out[os.path.relpath(p_, sd)] = (open(p_, "rb").read(), os.path.getmtime(p_))
        return out
    start()
    s1 = snap()
    time.sleep(1.1)
    start()
    s2 = snap()
    check(sorted(s1) == sorted(s2) and all(s1[k] == s2[k] for k in s1), "S. the second start changes nothing (files + mtimes): %s" % sorted(set(s1) ^ set(s2)))
    check(sorted(s1) == [os.path.join("Skyy_SkyyMobs", "bands.properties"), os.path.join("Skyy_SkyyMobs", "config.properties")],
          "S. only the two files exist (no history version, no change log): %s" % sorted(s1))
    # a scratch copy of the started folder, started again
    cp_ = os.path.join(SCRATCH, "twice-copy", "mods")
    shutil.copytree(sd, cp_)
    sd0 = sd
    sd = cp_
    sh = os.path.join(cp_, "Skyy_SkyyMobs")
    c1 = snap()
    time.sleep(1.1)
    start()
    c2 = snap()
    check(all(c1[k][0] == c2[k][0] for k in c1) and sorted(c1) == sorted(c2), "S. a copy started again: byte-identical")
    sd = sd0
    Cfg.useDefaults()
    print("S. start twice: no churn (fresh folder + a copy)")

    # ---------------- P. bytecode facts
    CPj = JClass("javassist.ClassPool")(False)
    CPj.appendSystemPath()
    CPj.appendClassPath(B.SERVER_JAR)
    CPj.appendClassPath(JAR)
    IP, PS, BOS = JClass("javassist.bytecode.InstructionPrinter"), JClass("java.io.PrintStream"), JClass("java.io.ByteArrayOutputStream")

    def code(cls, meth):
        out = ""
        cc = CPj.get(PKG + cls)
        for mm in list(cc.getDeclaredMethods()):
            if str(mm.getName()) == meth:
                bos = BOS()
                IP(PS(bos)).print_(mm)
                out += str(bos.toString())
        return out

    def ctor(cls):
        cc = CPj.get(PKG + cls)
        out = ""
        for k in cc.getDeclaredConstructors():
            mi = k.getMethodInfo()
            it = mi.getCodeAttribute().iterator()
            while it.hasNext():
                pos = it.next()
                out += str(IP.instructionString(it, pos, mi.getConstPool())) + "\n"
        return out
    q = code("LevelHook", "getQuery")
    check("NPCEntity.getComponentType" in q and "EntityStatMap.getComponentType" in q and "Query.and" in q,
          "P. the hook only sees NPCEntity + EntityStatMap holders (players never)")
    sys_ = code("SkyyMobsPlugin", "systems")
    check(all(x in sys_ for x in ("RoleBuilderSystem", "EntityStatsSystems$Setup", "BalancingInitialisationSystem", "DamageSystems$ArmorDamageReduction")),
          "P. the plugin resolves the 4 classes it orders against")
    hc = ctor("LevelHook")
    check(hc.count("Order.AFTER") == 3 and "BEFORE" not in hc, "P. the hook is ordered AFTER RoleBuilderSystem, Setup, BalancingInitialisationSystem")
    dc = ctor("LevelDamage")
    check("Order.BEFORE" in dc and "AFTER" not in dc and "getFilterDamageGroup" in code("LevelDamage", "getGroup"),
          "P. the damage system: Filter group, BEFORE ArmorDamageReduction")
    regs = re.findall(r"new #\d+ = Class (com\.skyy\.mobs\.\w+)", sys_)
    check(sorted(regs) == sorted(PKG + c for c in ("LevelHook", "LevelDamage", "LevelDamageU")) and len(set(regs)) == 3,
          "P. one registerSystem per class (the hook WITHOUT a fallback, the damage system + its unordered fallback): %s" % regs)
    # review F4: a refused hook registration logs an ERROR and leaves MobLevel.HOOK false (no unordered hook that could level nothing or
    # strip saved levels); /mobs inspect and /mobs info read the flag
    check("LevelHookU" not in sys_ and "MobLog.error" in sys_ and sys_.count("putstatic") >= 2 and "MobLevel.HOOK" in sys_,
          "P. F4: no unordered hook fallback; the hook registration sets MobLevel.HOOK, a failure logs an ERROR")
    check("MobLevel.HOOK" in code("MobCmds", "inspect") and "MobLevel.HOOK" in code("MobCmds", "infoLines"),
          "P. F4: /mobs inspect and /mobs info tell when the hook is not running")
    check(not bool(Lvl.HOOK), "P. F4: HOOK is false until the plugin registers the hook (bare JVM)")
    # review F6: the prune is scheduled every 5 minutes and cancelled on shutdown
    st_c, sd_c = code("SkyyMobsPlugin", "setup"), code("SkyyMobsPlugin", "shutdown")
    check("scheduleWithFixedDelay" in st_c and "MobPruneTask" in st_c and "MobLevel.PRUNE" in st_c and "cancel" in sd_c,
          "P. F6: setup schedules MobPruneTask (scheduleWithFixedDelay), shutdown cancels it")
    # review F3: the worldgen cache key has no >> 3 cell any more
    wgc = code("MobLevel", "worldgen")
    check("ishr" not in wgc and wgc.count("ConcurrentHashMap.put") == 1, "P. F3: the worldgen cache keys the exact column (no >> shift), one put")
    # every abstract engine method of the two system classes has a concrete implementation (an AbstractMethodError would only show
    # when the world ticks): HolderSystem.onEntityAdd / onEntityRemoved / QuerySystem.getQuery, EntityEventSystem.handle / getQuery
    RMod = JClass("java.lang.reflect.Modifier")
    for cname in ("LevelHook", "LevelDamage", "LevelDamageU", "MobLevelFn", "MobPlateStep", "MobScanTask", "MobPruneTask"):
        jc_ = Cls.forName(PKG + cname, False, sysl)
        abstract_left = []
        for mth in jc_.getMethods():
            if RMod.isAbstract(mth.getModifiers()):
                abstract_left.append(str(mth))
        check(not RMod.isAbstract(jc_.getModifiers()) and not abstract_left, "P. %s implements every abstract engine method: %s" % (cname, abstract_left))
    oa = code("MobLevel", "onAdd")
    check("savedLevel" in oa and "KEPT" in oa and "whyNot" in oa and "lookupMob" in oa and "levelFor" in oa and "apply" in oa,
          "P. onAdd: save slot, session memory, who-filter, lookup, roll, apply")
    print("P. bytecode facts done")

    # ---------------- L. link check (release + 0.7 pre-release)
    def link(server):
        cpl = JClass("javassist.ClassPool")(False)
        cpl.appendSystemPath()
        cpl.appendClassPath(server)
        cpl.appendClassPath(JAR)
        missing, n_ = [], 0
        for nm in names:
            cc = cpl.get(nm)
            cpool = cc.getClassFile().getConstPool()
            for i in range(1, cpool.getSize()):
                try:
                    tag = cpool.getTag(i)
                except Exception:
                    continue
                if tag not in (9, 10, 11):    # Fieldref, Methodref, InterfaceMethodref
                    continue
                if tag == 9:
                    owner, mn, desc = str(cpool.getFieldrefClassName(i)), str(cpool.getFieldrefName(i)), str(cpool.getFieldrefType(i))
                elif tag == 10:
                    owner, mn, desc = str(cpool.getMethodrefClassName(i)), str(cpool.getMethodrefName(i)), str(cpool.getMethodrefType(i))
                else:
                    owner, mn, desc = str(cpool.getInterfaceMethodrefClassName(i)), str(cpool.getInterfaceMethodrefName(i)), str(cpool.getInterfaceMethodrefType(i))
                if not owner.startswith(("com.hypixel.", "org.joml.")):
                    continue
                n_ += 1
                try:
                    oc = cpl.get(owner)
                    if tag == 9:
                        f_ = oc.getField(mn, desc)
                    elif mn == "<init>":
                        oc.getConstructor(desc)
                    else:
                        oc.getMethod(mn, desc)
                except Exception:
                    missing.append("%s.%s%s (from %s)" % (owner, mn, desc, nm.rsplit(".", 1)[1]))
        return n_, sorted(set(missing))
    n_rel, miss_rel = link(B.SERVER_JAR)
    check(not miss_rel, "L. release jar: every referenced engine member exists (%d refs): %s" % (n_rel, miss_rel[:8]))
    if os.path.isfile(PRE_JAR):
        n_pre, miss_pre = link(PRE_JAR)
        check(not miss_pre, "L. 0.7 pre-release jar: every referenced engine member exists (%d refs): %s" % (n_pre, miss_pre[:12]))
        print("L. link check: release %d refs, 0 missing; 0.7 pre-release %d refs, %d missing" % (n_rel, n_pre, len(miss_pre)))
    else:
        print("L. link check: release %d refs; no pre-release jar at %s" % (n_rel, PRE_JAR))


def guard_scratch():
    """None when --dir may be used (and deleted afterwards): a folder INSIDE a task folder of tools/dev/scratch
    (tools/dev/scratch/<task>/<sub>) - never the scratch root or a top-level task folder (other agents' live work sits there) - that is
    missing, empty or this harness's own (its MARKER file). Else the reason it is refused (nothing is deleted then)."""
    root_ = os.path.normcase(os.path.realpath(os.path.join(TOOLS, "dev", "scratch")))
    s_ = os.path.normcase(os.path.realpath(SCRATCH))
    try:
        rel = os.path.relpath(s_, root_)
    except ValueError:
        return "not on the drive of tools/dev/scratch"
    parts = [p for p in rel.replace("\\", "/").split("/") if p]
    if os.path.isabs(rel) or not parts or parts[0] in (".", ".."):
        return "outside tools/dev/scratch (or the scratch root itself)"
    if len(parts) < 2:
        return "a top-level folder of tools/dev/scratch - use tools/dev/scratch/<task>/<sub>"
    if os.path.lexists(SCRATCH):
        if os.path.islink(SCRATCH) or not os.path.isdir(SCRATCH):
            return "exists and is not a plain folder"
        if os.listdir(SCRATCH) and not os.path.isfile(os.path.join(SCRATCH, MARKER)):
            return "exists, is not empty and is not this harness's folder (no %s)" % MARKER
    return None


def main():
    if not os.path.isfile(JAR):
        print("no jar at", JAR, "- build it first")
        return 1
    why = guard_scratch()
    if why:
        print("--dir refused (%s): %s - nothing was deleted" % (why, SCRATCH))
        return 1
    SCRATCH_OK[0] = True
    os.makedirs(SCRATCH, exist_ok=True)
    open(os.path.join(SCRATCH, MARKER), "w").write("SkyyMobs %s harness scratch - deleted at the end of the run (unless --keep)\n" % VERSION)
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    os.environ["TEMP"] = tmp
    os.environ["TMP"] = tmp
    try:
        run()
    except Exception as e:
        import traceback
        traceback.print_exc()
        FAILS.append("harness error: %s" % e)
    print("SkyyMobs %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS[:60]:
        print("  FAIL", f[:600])
    return 1 if FAILS else 0


if __name__ == "__main__":
    code_ = main()
    # cleanup fix (2026-10-02): only the folder main() validated AND marked is deleted - this harness used to delete --dir even after
    # refusing it, and its old guard let the scratch ROOT through, so a --dir naming tools/dev/scratch wiped every builder's folder
    if not KEEP and SCRATCH_OK[0] and os.path.isfile(os.path.join(SCRATCH, MARKER)):
        shutil.rmtree(SCRATCH, ignore_errors=True)
    sys.stdout.flush()
    os._exit(code_)
