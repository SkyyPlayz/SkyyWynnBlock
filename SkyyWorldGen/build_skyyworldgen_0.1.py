"""SkyyWorldGen 0.1 - build script (javassist via jpype). NEW MOD: stage 1 of research/SkyyWorldGen-Plan.md (section 7.1) - the Zone 1
TEST island - built on the stage 0 proof report's asset recipe (all 23 offline checks passed) and Skyy's 2026-10-01 / 10-02 answers in
OPEN-QUESTIONS.md (zone bands Z1 1-20 ..., hub = the Zone 1 town, summit portal / temples / outposts later; "go for stage 0 + stage 1").
Run:   python SkyyWorldGen/build_skyyworldgen_0.1.py      -> SkyyWorldGen/SkyyWorldGen-0.1.jar
       (no --deploy on purpose: tools/deploy_set.py installs the whole set once Skyy says deploy)
Test:  python SkyyWorldGen/test_skyyworldgen_0.1.py       (bare JVM, -Xverify:all; scratch under tools/dev/scratch/wg01/)

WHAT IT DOES
  One World Gen V2 world, skywynn_z1: a floating island of radius 384 (the SMALL preset) centred on the world origin, with void all
  around it. Three rings, by (warped) distance from the centre: a meadow rim (Env_Zone1_Plains, no trees), a birch forest middle
  (Env_Zone1_Forests, vanilla Birch trees) and an azure-look core (Env_Zone1_Azure, vanilla Azure trees, blue grass tint #2F798A /
  #2F868A from the V1 Forest_Azure tile). Vanilla environments only, so vanilla's own Tier 1 / 2 / 3 mob lists and SkyyMobs' environment
  bands (rim 1-3, middle 5-9, core 16-20) apply with no new data. The island is assets only (generated into the jar at build time from
  ONE Python table, GEOMETRY below); the plugin code only opens, persists and reopens the world and moves players.
  - /zone 1        go to the island (first time: the island is generated - spawnInstance of the jar's instance template, ONCE)
  - /zone          the zone list + status;  /zone info  where you stand (ring, distance, landing point)
  - /zone leave    back to where you came from (InstancesPlugin.exitInstance); SkyyIslands' /hub works from the island unchanged
  - /zone setlanding   the landing point = where you stand (on the island);  /zone reload  re-read config.properties
  TEST VERSION: every /zone command is ADMIN-ONLY (requirePermission skyyworldgen.admin + setPermissionGroups(new String[0])), so
  normal players never see a difference. Ops (hytale:Admin = *) have the node.
  Landing: (0.5, 144, 344.5) on the south rim, yaw 0 = facing the core (Transform.getDirection(0, 0) = (0, 0, -1), checked in the
  engine), 1-2 blocks above the measured grass top (the harness re-measures it from the jar's own assets). Falling into the void kills
  at y -32 (engine); the respawn rule (HomeOrSpawnPoint) puts you at a bed set in that world, otherwise at the world's SpawnProvider =
  the landing.
  DEATHS KEEP ITEMS on the island (review 2026-10-03 finding 1, the safe option of a Skyy decision): the template carries the world
  config's own "Death" override {"ItemsLossMode": "None"} (WorldConfig "Inline death configuration overrides for this world"; the
  engine's World.getDeathConfig() takes it before the GameplayConfig, and DeathSystems$PlayerDropItemsConfig reads only that). Without
  it Default.json drops 50% of every stack where you die - in the void, gone for good (SkyyGear rolls included). Everything else in it
  = the engine defaults = what Default.json gives today: respawn HomeOrSpawnPoint, 10% durability loss on death (SkyyEssentials'
  durability switch still zeroes that), GameplayConfig stays "Default". The plan (2.2) wants void deaths to cost coins, not items;
  vanilla's own Portal / ForgottenTemple configs use ItemsLossMode None the same way. No new GameplayConfig asset (no boot risk).

PERSISTENCE (the engine facts behind it, bytecode of the release HytaleServer.jar 0.6.8, 2026-10-02)
  - spawnInstance(template, "skywynn_z1", from, ret) copies Server/Instances/SkyWynn_Zone1 into universe/worlds/skywynn_z1 and makes the
    world. It is called ONLY when the world is neither loaded nor on disk. A second call for an existing folder could not overwrite it
    anyway (the template copy uses Files.copy without REPLACE_EXISTING and fails), and InstancesPlugin.pendingSpawns + our CREATING mark
    stop two concurrent creations.
  - REOPEN = Universe.loadWorld(name), NOT addWorld: in this jar addWorld(name) throws "World <name> already exists on disk!" for a world
    whose folder exists (isWorldLoadable). (The plan and SkyyIslands' openSaved say addWorld; SkyyIslands' islands never take that branch
    because they never unload - see the next point.) Concurrent reopens share one future (WgOpen.LOADING).
  - The world does NOT unload when empty: the template sets Plugin.Instance.RemovalConditions = [] (codec version 4; the old top-level
    "Instance" key of the proof recipe is only read for versions 0-2, deprecated). Reasons: Universe.start loads every world folder at
    boot anyway; a WorldEmpty world that HadPlayer is removed on the first tick after it loads, which would race a player being sent to
    a freshly re-loaded world; and a player who logs out on the island logs back in on it (the engine only falls back to the default
    world when the saved world is not loaded). SkyyIslands' islands behave the same in practice (their saved configs show
    RemovalConditions [], loaded at boot, stopped only at shutdown - Skyy's server logs).
  - Skyy_SkyyWorldGen/worlds.properties records each world once, after its first successful creation (time, template, structure); /zone
    info shows it. A folder that exists without config.json/config.bson (a first creation that died half way) is never touched: /zone
    refuses and names the folder to delete. A recorded world whose folder is gone (deleted by an admin) is generated fresh, with a WARN.
  - Before any /zone trip the WorldStructure must be in the V2 generator's own asset map (HytaleGenerator.get().getAssetManager()
    .getWorldStructureAsset - the proof report's optional guard): if our assets did not load, /zone refuses instead of letting the
    generator fall back (FallbackGenerator returns EMPTY chunks) and save void chunks into the island for good.
  - Only OUR island counts (review finding 4): a loaded world named skywynn_z1 is used as the island only when its world generator is
    a HandleProvider with the WorldStructure SkyWynn_Z1_Small (WgZones.isIsland). WorldConfig.load gives a DEFAULT config when
    config.json is missing and Universe.start loads every folder, so a creation that died between the template copy and the first
    config write boots as a plain world with our name: /zone refuses it (code 11, names the folder to delete), WgApplyLanding /
    /zone setlanding / the landing action never touch it. (A saved-not-loaded foreign folder is not checked before Universe.loadWorld -
    every folder is loaded at boot, so that state needs a manual unload first.)
  - The island's OWN return point (spawnInstance's from + ret, used by exitInstance for anyone with no personal return point, e.g.
    after a restart) is never another instance (review finding 5): when /zone 1 first runs on an instance world (a SkyyIslands island,
    another zone), the default world and its spawn point are stored instead. The player's personal return point is still where they
    ran /zone 1 (teleportPlayerToLoadingInstance's 4th argument).
  - Every trip lands on the CURRENT landing point (review finding 3): an already loaded island is entered with
    teleportPlayerToLoadingInstance(CompletableFuture.completedFuture(world), ret, landing) - the same engine path as a load / create
    (Universe.transferPlayerAsync) - instead of teleportPlayerToInstance, which lands on the world's saved spawn point.
  - Found by the harness (the real engine builds the world offline): (1) a creation that is still running is checked BEFORE the disk
    checks - the engine writes config.json before it registers the world, and a loadWorld in that window would race the creation;
    (2) spawnInstance stores its 'ret' transform as the world's own return point, and a null one is saved without its transform, after
    which config.json can never be decoded again ("Failed to decode 'Plugin'") - startCreate never passes null (safeReturn: the
    player's position, else the spawn of the world they came from, else (0, 100, 0)).

SETTINGS  Server Setup > World Gen (tools/skyycfg.py kit 1.1, node skyyworldgen.admin), Skyy_SkyyWorldGen/config.properties:
  part.zones (Zone islands on/off), landing.point ("x y z yaw", checked: at most 360 blocks from the centre, yaw -360..360, and Y on
  the island's GROUND there - review finding 2: Y within -6 / +10 of the island's top curve at that distance, the curve baked into
  WgZones from GEOMETRY; without it "0 1 0" was accepted = arrive in the void, die, respawn there, forever. The harness measures the
  real terrain: no void column within 367 blocks, and within 360 the ground is the curve -4.7 .. +3.6, so every spot /zone setlanding
  can write (ground + 2) passes and a Y under the island never does; the world's spawn point = respawn point follows it on the
  world thread at once - after an in-game change, after /zone reload of a hand edit (WgCfg.reloadAll -> syncLanding) and on every
  arrival), landing.here (action: the landing = where the admin stands).
  READ-ONLY rows (fixed in the island files - a new size is a new world): island size, world name, rings. NOT editable at runtime: the
  geometry (radius, rings, heights, warp, seed) - V2 assets take no runtime parameters (proof report).

DECISIONS where the plan / proof left room
  - addWorld -> loadWorld, RemovalConditions [] and Version 4 "Plugin" form (above).
  - Landing yaw 0 (the recipe wrote 180 = facing the void).
  - DeleteOnUniverseStart false written explicitly (its default is false; never delete the island on a restart).
  - No new bridge keys yet (wg:fn:ring / wg:fn:zone / wg:fn:unlocked are stage 2), no /fly block, no unlock rules, no SkyyMenu tile.
  - /hub stays SkyyIslands' (we never register "hub" - duplicate command names are last-wins). /zone leave is our own way out for
    servers without SkyyIslands and returns the player to where they ran /zone 1.
  - /zone 1 from inside the island = back to the landing point (a quick "unstuck"); /zone alone always just lists.
  - Deaths on the island keep items (world config Death override, above) - Skyy decides later whether zone islands get a coin-loss
    death (plan 2.2) or the vanilla 50% item drop. No rim lip yet (a terrain change; with no item loss it can wait for stage 2).
  - Only /zone 1 makes the island. Vanilla `/instances spawn SkyWynn_Zone1` (group WorldEditor) would make extra
    skywynn_zone1-<uuid> copies that never unload or delete (the template has no removal conditions, on purpose) - do not use it.
NOT IN 0.1 (later stages, plan 7.1): medium preset, 6 rings, biome patches, terraces, summit, portals, temples / towns / outposts, chests
  and ores per ring, ring discovery, unlock chain, Zones 2-4, the player version of /zone, a rim lip, a nicer zone name on the SkyyHud
  widget (it shows the raw world name skywynn_z1 - a stage 2 bridge key). Other mods: SkyyIslands' /sethub refuses only island worlds,
  so /sethub on skywynn_z1 would make the test island the server hub - do not /sethub there (next SkyyIslands should refuse zone worlds).
UNVERIFIED (needs the game): how the island looks and how generation feels while running / gliding (bare-JVM numbers below), vanilla
  mobs actually spawning on the floating ground (environment per block + Soil block set are right), the teleports themselves (the
  engine calls SkyyIslands uses - offline they run up to the point where a live player entity is needed), void death -> respawn at the
  landing with every item kept (engine respawn rule, spawn provider and the Death override checked, not the death itself), logging in
  on the island after a restart (the engine loads every world folder at boot - bytecode), the landing yaw on the client camera,
  SkyyMobs levels on V2 mobs, no zone banner / compass name on V2 (proof T9), the loaded-island trip through
  teleportPlayerToLoadingInstance (the same engine path as the load / create trips, which are also unverified in game).

REVIEW 2026-10-03 (verdict SHIP; findings 1-5 fixed in this same 0.1, see the notes above): 1 deaths keep items (world config Death
  override), 2 landing.point Y must be on the island's ground, 3 every trip lands on the current landing + a reload moves the loaded
  island's spawn at once, 4 only a world with our generator counts as the island, 5 the island's own return point is never an
  instance. 6 / 7 / 9 are notes (no /instances spawn, no /sethub on the island, raw world name on the SkyyHud widget), 8 wording.
  Re-checked after the fixes: build 73 engine members probed, access audit 5575 references 0 refused, "assembled ...SkyyWorldGen-0.1.jar"
  (87,982 bytes, a clean rebuild in scratch = the same 36 entries by CRC); lint 0 fails (no SkyyWorldGen line), lint --perm 0 fails,
  skyycfg_test PASS, skyyui_test 10060 ok + the known stale WrapMaxLines fail; the harness 267 ok, 0 fail (G2: 108,416 rim-ring
  columns, no void within 367.5 blocks, 87,295 land columns within 360: ground = curve -4.2 .. +2.8 - a denser interior survey gave
  -4.7 .. +3.6 - so the -6 / +10 window holds); a jar built with all five fixes reverted fails 27 harness checks (J W R P O K G2 B).

CHECKED 2026-10-02 (re-run before a deploy - the harness is the source of truth, not this text):
  build: 9 assets (ids / exports / environments / blocks / prefab folders checked against Assets.zip), 68 engine members probed by exact
    signature, 26 classes (7 kit), access audit 5436 references 0 refused, "assembled ...SkyyWorldGen-0.1.jar" (85,774 bytes).
  python tools/ci/lint.py: 0 fails (no SkyyWorldGen warning; the 26 warnings are SkyySacks 0.7.12's); lint --perm: 0 fails (the six
    /zone constructors all "clears groups"). python tools/skyycfg_test.py: PASS (29 refused + 3 built). tools/skyyui_test.py: 10060 ok,
    1 known stale fail (base-gated WrapMaxLines - RESUME follow-up, not this mod).
  python SkyyWorldGen/test_skyyworldgen_0.1.py: 228 ok, 0 fail - A 26 classes -Xverify:all; M manifest + the 9 assets; J the JSON = the
    proof recipe typed independently; D the real HytaleAssetStores decode the jar (zip pack): 1 WorldStructure / 2 Density / 4 Biome,
    0 failed, both exports, the generator's AssetManager got the structure, no engine warning names a SkyWynn asset; V StagedChunk-
    Generator / Fallback for unknown names / the /zone guard; C 54 chunks, 3,456 columns: land everywhere within R-30, nothing from
    R+30, the ring environment on surface + underside, tints, heights inside the recipe's bounds (core 155-164 / underside 47-61, forest
    147-156 / 62-83, meadow 140-148 / 96-122), grass + 3 dirt + stone, Birch trees in the forest, Azure in the core, none in the meadow;
    first chunk 0.26 s incl. the structure build, then ~80 ms avg, ~270 ms max (2+2+2 threads, bare JVM); G landing ground 142-143,
    meadow, clear 3 blocks around; T determinism; W the template through WorldConfig.CODEC (+ vanilla Zone1_Plains1 control); R respawn
    facts + WgApplyLanding; P the real spawnInstance + Universe.makeWorld built skywynn_z1 from the template offline, WgDone recorded it,
    Universe.loadWorld reopened the same island, addWorld refuses a saved world, a second spawnInstance refuses the existing folder,
    half-made folder refused, fresh island after a delete; O every /zone path executed (refusals in chat; create / load / teleport up to
    the engine teleport call); H engine permission code (admin-only); K the config kit; S the plugin's real setup() twice = no churn +
    the PlayerReadyEvent listener through the real EventBus; E CommandManager.handleCommand for a plain player (refused) and an op
    (parsed, permitted, scheduled on the world); X MethodHandles.Lookup 0 refused; L release + 0.7 pre-release: 126 refs, 0 missing.
"""
import sys, os, re, json, zipfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B
import skyycfg as CFG
assert tuple(int(x) for x in getattr(CFG, "KIT_VERSION", "1.0").split(".")) >= (1, 1), "SkyyWorldGen needs config kit 1.1+"
import skyyui as SUI       # chat status colours (no pages in 0.1)
SUI.verify(quiet=True)
KIT_ID = SUI.kit_id()

VERSION = "0.1"
MOD = "SkyyWorldGen"
HERE = os.path.dirname(os.path.abspath(__file__))
NODE = "skyyworldgen.admin"

# ================================================================= ONE geometry table (proof report "Exact asset recipe"). If any
# geometry number, the seed or Base changes, re-measure the landing Y with the harness (test_skyyworldgen_0.1.py section G).
GEOMETRY = {
    "zone": "1", "name": "Emerald Wilds", "world": "skywynn_z1", "template": "SkyWynn_Zone1", "structure": "SkyWynn_Z1_Small",
    "preset": "Small", "R": 384, "base": 140, "water": 140, "bedrock": 0, "K": 12.0,
    # (biome id, min distance, max distance, environment, tint colour 1, tint colour 2, split, ring name, tree spacing, tree prefabs)
    "rings": [
        ("SkyWynn_Z1S_Core", -1, 128, "Env_Zone1_Azure", "#2F798A", "#2F868A", 0.3, "Azure core", 13,
         [("Trees/Azure/Stage_2", 50), ("Trees/Azure/Stage_3", 50)]),
        ("SkyWynn_Z1S_Forest", 128, 256, "Env_Zone1_Forests", "#7f9b1f", "#69970f", 0.4, "Birch forest", 11,
         [("Trees/Birch/Stage_1", 30), ("Trees/Birch/Stage_2", 45), ("Trees/Birch/Stage_3", 25)]),
        ("SkyWynn_Z1S_Meadow", 256, 400, "Env_Zone1_Plains", "#639726", "#3b8e32", 0.6, "Meadow rim", 0, []),
    ],
    "void_from": 400, "void_biome": "SkyWynn_Void", "void_env": "Env_Void", "void_tint": "#5b9e28",
    "warp": {"factor": 24, "scale": 250, "persistence": 0.5, "lacunarity": 2, "octaves": 1, "seed": "SkyWynn-Z1"},
    # distance -> blocks above / below Base
    "top": [(0, 24), (128, 16), (256, 8), (344, 4), (376, 1), (384, -3)],
    "depth": [(0, 90), (128, 80), (256, 56), (344, 24), (376, 6), (384, -3)],
    "hills": {"amp": 0.3, "scale": 70, "octaves": 2, "seed": "SkyWynn-Z1-Hills"},
    "under": {"amp": 0.6, "scale_xz": 40, "scale_y": 20, "octaves": 2, "seed": "SkyWynn-Z1-Under"},
    "tint_noise": {"scale": 14, "octaves": 3, "seed": "SkyWynn-Z1-Tint"},
    "tree_seed": "SkyWynn-Z1-Trees",
    "transition": 16, "edge": 16,
    "landing": (0.5, 144.0, 344.5, 0.0),        # x, y, z, yaw degrees (0 = facing -z = the core from the south rim)
    "seed": "SkyWynn-Z1",
    "dist_export": "SkyWynn-Z1S-Dist", "island_export": "SkyWynn-Z1S-Island",
    "dist_file": "SkyWynn_Z1S_Dist", "island_file": "SkyWynn_Z1S_Island",
}
G = GEOMETRY
R = G["R"]
K = G["K"]
LANDING_MAX_DIST = R - 24          # the landing check: hypot(x, z) at most this (the warped rim can sit about 16 blocks inside R)
# landing.point Y window (review finding 2): Y from ceil(top - BELOW) to floor(top + ABOVE), top = Base + the "top" curve at the plain
# distance. The harness measures the generated island: no void column within 367 blocks of the centre; within LANDING_MAX_DIST the
# ground is the curve -4.7 .. +3.6 and the underside at least 8.5 blocks under the curve, so ground + 2 (what /zone setlanding writes)
# always passes and a Y under the island (the void-death loop) never does. Re-measure (harness section G2) if the geometry changes.
LANDING_Y_BELOW, LANDING_Y_ABOVE = 6.0, 10.0
# grass tint colours = world data (V1 tile palettes), not page chrome - the lint's data-colour list (literal, checked against the table)
UI_DATA_COLORS = ["#2F798A", "#7f9b1f", "#639726", "#2F868A", "#69970f", "#3b8e32", "#5b9e28"]
assert UI_DATA_COLORS == [r[4] for r in G["rings"]] + [r[5] for r in G["rings"]] + [G["void_tint"]]


def interp(pts, d):
    if d <= pts[0][0]:
        return float(pts[0][1])
    for (a, va), (b, vb) in zip(pts, pts[1:]):
        if d <= b:
            return va + (vb - va) * (d - a) / float(b - a)
    return float(pts[-1][1])


def num(v):
    """JSON number the recipe's way: whole numbers as ints, others rounded to 4 decimals"""
    v = round(float(v), 4)
    return int(v) if v == int(v) else v


# sanity of the table (a typo here would make the island one biome or no island)
assert all(a[0] < b[0] for a, b in zip(G["top"], G["top"][1:])) and all(a[1] > b[1] for a, b in zip(G["top"], G["top"][1:]))
assert all(a[0] < b[0] for a, b in zip(G["depth"], G["depth"][1:])) and all(a[1] > b[1] for a, b in zip(G["depth"], G["depth"][1:]))
assert G["top"][-1][0] == R and G["depth"][-1][0] == R and G["top"][-1][1] < 0 and G["depth"][-1][1] < 0, "no land past R"
assert G["rings"][-1][2] == G["void_from"] and G["rings"][0][1] == -1
for _a, _b in zip(G["rings"], G["rings"][1:]):
    assert _a[2] == _b[1], "rings must touch"
_lx, _ly, _lz, _lyaw = G["landing"]
_ld = (_lx * _lx + _lz * _lz) ** 0.5
assert _ld <= LANDING_MAX_DIST, "landing must be on the island"
_ltop = G["base"] + interp(G["top"], _ld)
assert 0 <= _ly - _ltop <= 2.5, "landing Y %.2f vs the curve top %.2f at d %.1f" % (_ly, _ltop, _ld)
import math as _math
assert _math.ceil(_ltop - LANDING_Y_BELOW) <= _ly <= _math.floor(_ltop + LANDING_Y_ABOVE), "the default landing must pass its own Y window"
for _r in G["rings"]:
    if _r[1] <= _ld < _r[2]:
        LANDING_RING = _r[7]
assert LANDING_RING == "Meadow rim", "the landing must be in the treeless meadow"

# ================================================================= the V2 assets (generated here; vanilla only referenced by id)
def density_dist():
    w = G["warp"]
    return {"Type": "Exported", "ExportAs": G["dist_export"], "SingleInstance": True, "Inputs": [
        {"Type": "YOverride", "Value": 0, "Inputs": [
            {"Type": "Cache", "Capacity": 3, "Inputs": [
                {"Type": "FastGradientWarp", "WarpScale": w["scale"], "WarpPersistence": w["persistence"], "WarpLacunarity": w["lacunarity"],
                 "WarpOctaves": w["octaves"], "WarpFactor": w["factor"], "Seed": w["seed"], "Inputs": [
                     {"Type": "YOverride", "Value": 0, "Inputs": [
                         {"Type": "Distance", "Curve": {"Type": "Manual", "Points": [{"In": 0, "Out": 0}, {"In": 8000, "Out": 8000}]}}]}]}]}]}]}


def curve(points):
    return {"Type": "Manual", "Points": [{"In": num(a), "Out": num(b)} for a, b in points]}


def density_island():
    h = {"Type": "BaseHeight", "BaseHeightName": "Base", "Distance": True}
    d = {"Type": "Imported", "Name": G["dist_export"]}
    hm = round(400.0 / K, 3)
    hills, under = G["hills"], G["under"]
    top_sum = {"Type": "Sum", "Inputs": [
        {"Type": "CurveMapper", "Curve": curve([(-400, hm), (400, -hm)]), "Inputs": [h]},
        {"Type": "CurveMapper", "Curve": curve([(a, b / K) for a, b in G["top"]]), "Inputs": [d]},
        {"Type": "Normalizer", "FromMin": -1, "FromMax": 1, "ToMin": -hills["amp"], "ToMax": hills["amp"], "Inputs": [
            {"Type": "SimplexNoise2D", "Lacunarity": 2, "Persistence": 0.5, "Octaves": hills["octaves"], "Scale": hills["scale"],
             "Seed": hills["seed"]}]}]}
    bottom_sum = {"Type": "Sum", "Inputs": [
        {"Type": "CurveMapper", "Curve": curve([(-400, -hm), (400, hm)]), "Inputs": [h]},
        {"Type": "CurveMapper", "Curve": curve([(a, b / K) for a, b in G["depth"]]), "Inputs": [d]},
        {"Type": "Normalizer", "FromMin": -1, "FromMax": 1, "ToMin": -under["amp"], "ToMax": under["amp"], "Inputs": [
            {"Type": "SimplexNoise3D", "Lacunarity": 2, "Persistence": 0.5, "Octaves": under["octaves"], "ScaleXZ": under["scale_xz"],
             "ScaleY": under["scale_y"], "Seed": under["seed"]}]}]}
    return {"Type": "Exported", "ExportAs": G["island_export"], "SingleInstance": True, "Inputs": [
        {"Type": "Min", "Inputs": [top_sum, bottom_sum]}]}


def world_structure():
    biomes = [{"Biome": r[0], "Min": r[1], "Max": r[2]} for r in G["rings"]]
    biomes.append({"Biome": G["void_biome"], "Min": G["void_from"], "Max": 100000})
    lx, ly, lz, _yaw = G["landing"]
    return {"Type": "NoiseRange", "Biomes": biomes, "DefaultBiome": G["void_biome"], "DefaultTransitionDistance": G["transition"],
            "MaxBiomeEdgeDistance": G["edge"], "Density": {"Type": "Imported", "Name": G["dist_export"]},
            "SpawnPositions": {"Type": "List", "Positions": [{"X": lx, "Y": ly, "Z": lz}]},
            "Framework": [{"Type": "DecimalConstants", "Entries": [{"Name": "Base", "Value": G["base"]}, {"Name": "Water", "Value": G["water"]},
                                                                   {"Name": "Bedrock", "Value": G["bedrock"]}]}]}


def biome_void():
    return {"Name": G["void_biome"], "Terrain": {"Type": "DAOTerrain", "Density": {"Type": "Constant", "Value": 0}},
            "MaterialProvider": {"Type": "Constant", "Material": {"Solid": "Empty"}}, "Props": [],
            "EnvironmentProvider": {"Type": "Constant", "Environment": G["void_env"]},
            "TintProvider": {"Type": "Constant", "Color": G["void_tint"]}}


def biome_land(ring):
    bid, _a, _b, env, c1, c2, split, _name, spacing, paths = ring
    tn = G["tint_noise"]
    out = {"Name": bid, "Terrain": {"Type": "DAOTerrain", "Density": {"Type": "Imported", "Name": G["island_export"]}},
           "MaterialProvider": {"Type": "Solidity", "Solid": {"Type": "Queue", "Queue": [
               {"Type": "SpaceAndDepth", "LayerContext": "DEPTH_INTO_FLOOR", "MaxExpectedDepth": 4, "Layers": [
                   {"Type": "ConstantThickness", "Thickness": 1, "Material": {"Type": "Constant", "Material": {"Solid": "Soil_Grass"}}},
                   {"Type": "ConstantThickness", "Thickness": 3, "Material": {"Type": "Constant", "Material": {"Solid": "Soil_Dirt"}}}]},
               {"Type": "Constant", "Material": {"Solid": "Rock_Stone"}}]},
               "Empty": {"Type": "Queue", "Queue": [{"Type": "Constant", "Material": {"Solid": "Empty"}}]}},
           "Props": [],
           "EnvironmentProvider": {"Type": "Constant", "Environment": env},
           "TintProvider": {"Type": "DensityDelimited", "Density": {"Type": "Normalizer", "FromMin": -1, "FromMax": 1, "ToMin": 0, "ToMax": 1,
                                                                   "Inputs": [{"Type": "SimplexNoise2D", "Lacunarity": 2, "Persistence": 0.5,
                                                                               "Octaves": tn["octaves"], "Scale": tn["scale"],
                                                                               "Seed": tn["seed"]}]},
                            "Delimiters": [{"Tint": {"Type": "Constant", "Color": c1}, "Range": {"MinInclusive": 0, "MaxExclusive": split}},
                                           {"Tint": {"Type": "Constant", "Color": c2}, "Range": {"MinInclusive": split, "MaxExclusive": 1.0001}}]}}
    if paths:
        out["Props"] = [{"Runtime": 0, "Positions": {"Type": "Mesh2D", "PointsY": 0, "PointGenerator": {
            "Type": "Mesh", "Jitter": 0.4, "ScaleX": spacing, "ScaleY": spacing, "ScaleZ": spacing, "Seed": G["tree_seed"]}},
            "Assignments": {"Type": "Constant", "Prop": {
                "Type": "Prefab", "WeightedPrefabPaths": [{"Path": p, "Weight": w} for p, w in paths], "LegacyPath": False, "LoadEntities": True,
                "Directionality": {"Type": "Random", "Seed": G["tree_seed"], "Pattern": {
                    "Type": "Floor", "Origin": {"Type": "BlockSet", "BlockSet": {"Inclusive": True, "Materials": [{"Solid": "Empty"}]}},
                    "Floor": {"Type": "BlockSet", "BlockSet": {"Inclusive": True, "Materials": [{"Solid": "Soil_Grass"}]}}}},
                "Scanner": {"Type": "ColumnLinear", "MaxY": 40, "MinY": -8, "RelativeToPosition": False, "BaseHeightName": "Base",
                            "TopDownOrder": True, "ResultCap": 1},
                "MoldingDirection": "None", "MoldingChildren": False}}}]
    return out


def instance_template():
    lx, ly, lz, yaw = G["landing"]
    return {
        "$Comment": "SkyWynn Zone 1 test island (SkyyWorldGen %s): a World Gen V2 floating island from the WorldStructure %s. "
                    "Generated once by /zone 1, then kept (no removal conditions) - never use /instances spawn for it (permanent "
                    "extra copies). Deaths here keep items (Death override)." % (VERSION, G["structure"]),
        "RequiredPlugins": {},
        "ChunkStorage": {"Type": "Hytale"},
        "DisplayName": "Zone %s - %s" % (G["zone"], G["name"]),
        "GameMode": "Adventure",
        "IsPvpEnabled": False,
        "IsSpawningNPC": True,
        "GameTime": "0001-01-01T08:00:00Z",
        "UUID": {"$binary": "AAAAAAAAAAAAAAAAAAAAAA==", "$type": "04"},
        "GameplayConfig": "Default",
        # the world's own death rule (WorldConfig "Death" = MutableDeathConfig; World.getDeathConfig() prefers it over the
        # GameplayConfig): no item loss - a void death would otherwise drop half of every stack where nobody can reach it
        "Death": {"ItemsLossMode": "None"},
        "IsCompassUpdating": True,
        "IsTicking": True,
        "IsGameTimePaused": False,
        "IsObjectiveMarkersEnabled": True,
        "IsAllNPCFrozen": False,
        "IsSavingPlayers": True,
        "WorldGen": {"Type": "HytaleGenerator", "WorldStructure": G["structure"], "SeedOverride": G["seed"]},
        "SpawnProvider": {"Id": "Global", "SpawnPoint": {"X": lx, "Y": ly, "Z": lz, "Pitch": 0.0, "Yaw": yaw, "Roll": 0.0}},
        "IsSpawnMarkersEnabled": True,
        "DeleteOnRemove": False,
        "DeleteOnUniverseStart": False,
        "Plugin": {"Instance": {"RemovalConditions": []}},
        "Version": 4,
    }


def jdump(o):
    return json.dumps(o, indent=2) + "\n"


ASSETS = {
    "Server/HytaleGenerator/Density/%s.json" % G["dist_file"]: jdump(density_dist()),
    "Server/HytaleGenerator/Density/%s.json" % G["island_file"]: jdump(density_island()),
    "Server/HytaleGenerator/WorldStructures/%s.json" % G["structure"]: jdump(world_structure()),
    "Server/HytaleGenerator/Biomes/SkyWynn/%s.json" % G["void_biome"]: jdump(biome_void()),
}
for _r in G["rings"]:
    ASSETS["Server/HytaleGenerator/Biomes/SkyWynn/%s.json" % _r[0]] = jdump(biome_land(_r))
ASSETS["Server/Instances/%s/instance.bson" % G["template"]] = jdump(instance_template())
ASSETS["Server/Instances/%s/resources/InstanceData.json" % G["template"]] = '{\n  "HadPlayer": false\n}\n'
for _p, _t in ASSETS.items():
    assert all(ord(c) < 127 for c in _t), "assets must be plain ASCII: " + _p

# ---- build-time checks against Assets.zip (read-only): our ids never clash with vanilla, every vanilla id we reference exists
AZ_PATH = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
with zipfile.ZipFile(AZ_PATH) as _az:
    _names = _az.namelist()
    _base = set(n.rsplit("/", 1)[-1] for n in _names)
    _ids = [p.rsplit("/", 1)[1][:-5] for p in ASSETS if p.startswith("Server/HytaleGenerator/")]
    for _i in _ids:
        assert _i.startswith("SkyWynn_"), "every V2 file id starts SkyWynn_: " + _i
        assert _i + ".json" not in _base, "vanilla already has a file named %s.json" % _i
    _exports = set()
    for _n in _names:
        if _n.startswith("Server/HytaleGenerator/") and _n.endswith(".json"):
            for _m in re.finditer(r'"ExportAs"\s*:\s*"([^"]+)"', _az.read(_n).decode("utf-8", "replace")):
                _exports.add(_m.group(1))
    for _e in (G["dist_export"], G["island_export"]):
        assert _e.startswith("SkyWynn-") and _e not in _exports, "export name must be ours: " + _e
    assert not any(e.lower().startswith("skywynn") for e in _exports)
    assert not any(n.startswith("Server/Instances/%s/" % G["template"]) for n in _names), "vanilla instance name clash"
    for _blk in ("Soil_Grass", "Soil_Dirt", "Rock_Stone"):
        assert any(n.startswith("Server/Item/Items/") and n.endswith("/%s.json" % _blk) for n in _names), "block id " + _blk
    for _env in [r[3] for r in G["rings"]] + [G["void_env"]]:
        assert any(n.startswith("Server/Environments/") and n.endswith("/%s.json" % _env) for n in _names), "environment " + _env
    for _r in G["rings"]:
        for _pp, _w in _r[9]:
            assert any(n.startswith("Server/Prefabs/%s/" % _pp) and n.endswith(".prefab.json") for n in _names), "prefab folder " + _pp
    assert "Server/GameplayConfigs/Default.json" in _names
    # the Death override's spelling = vanilla's own (Portal.json / ForgottenTemple.json: "ItemsLossMode": "None")
    _dl = json.loads(_az.read("Server/GameplayConfigs/Portal.json").decode("utf-8")).get("Death", {})
    assert _dl.get("ItemsLossMode") == instance_template()["Death"]["ItemsLossMode"] == "None", "Death.ItemsLossMode spelling: %s" % _dl
print("assets: %d files (%s), %d vanilla export names checked, ids / environments / blocks / prefab folders exist in Assets.zip"
      % (len(ASSETS), ", ".join(sorted(p.rsplit("/", 1)[1] for p in ASSETS)), len(_exports)))

# ================================================================= JVM + engine classes (every member probed: a missing one fails the build)
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)
PKG = "com.skyy.worldgen"
T = {
    "PKG": PKG, "VERSION": VERSION, "KITID": KIT_ID, "NODE": NODE,
    "JP": "com.hypixel.hytale.server.core.plugin.JavaPlugin",
    "JPI": "com.hypixel.hytale.server.core.plugin.JavaPluginInit",
    "PR": "com.hypixel.hytale.server.core.universe.PlayerRef",
    "REF": "com.hypixel.hytale.component.Ref",
    "ST": "com.hypixel.hytale.component.Store",
    "CA": "com.hypixel.hytale.component.ComponentAccessor",
    "CTYPE": "com.hypixel.hytale.component.ComponentType",
    "COMP": "com.hypixel.hytale.component.Component",
    "WLD": "com.hypixel.hytale.server.core.universe.world.World",
    "WCFG": "com.hypixel.hytale.server.core.universe.world.WorldConfig",
    "EST": "com.hypixel.hytale.server.core.universe.world.storage.EntityStore",
    "UNI": "com.hypixel.hytale.server.core.universe.Universe",
    "INS": "com.hypixel.hytale.builtin.instances.InstancesPlugin",
    "TRF": "com.hypixel.hytale.math.vector.Transform",
    "R3F": "com.hypixel.hytale.math.vector.Rotation3f",
    "VEC": "org.joml.Vector3d",
    "TC": "com.hypixel.hytale.server.core.modules.entity.component.TransformComponent",
    "TP": "com.hypixel.hytale.server.core.modules.entity.teleport.Teleport",
    "ISP": "com.hypixel.hytale.server.core.universe.world.spawn.ISpawnProvider",
    "GSP": "com.hypixel.hytale.server.core.universe.world.spawn.GlobalSpawnProvider",
    "HG": "com.hypixel.hytale.builtin.hytalegenerator.plugin.HytaleGenerator",
    "HGAM": "com.hypixel.hytale.builtin.hytalegenerator.assets.AssetManager",
    "HP": "com.hypixel.hytale.builtin.hytalegenerator.plugin.HandleProvider",
    "IWC": "com.hypixel.hytale.builtin.instances.config.InstanceWorldConfig",
    "PRE": "com.hypixel.hytale.server.core.event.events.player.PlayerReadyEvent",
    "APC": "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand",
    "CTX": "com.hypixel.hytale.server.core.command.system.CommandContext",
    "MSG": "com.hypixel.hytale.server.core.Message",
    "ATY": "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes",
    "RA": "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg",
    "LOG": "com.hypixel.hytale.logger.HytaleLogger",
    "CF": "java.util.concurrent.CompletableFuture",
    # TEST VERSION: every /zone command, sub-command and usage variant is admin-only - its own node AND no permission groups (lint
    # perm_group_leaks; the engine adds a node to every group listed, so an empty list keeps it off hytale:Adventurer)
    "ADMIN": 'requirePermission("%s"); setPermissionGroups(new String[0]);' % NODE,
}
AC = "com.hypixel.hytale.server.core.command.system.AbstractCommand"
PB = "com.hypixel.hytale.server.core.plugin.PluginBase"


def jdesc(t):
    if t.endswith("[]"):
        return "[" + jdesc(t[:-2])
    prim = {"int": "I", "long": "J", "float": "F", "double": "D", "boolean": "Z", "void": "V", "char": "C", "byte": "B", "short": "S"}
    return prim[t] if t in prim else "L" + t.replace(".", "/") + ";"


PROBED = []


def probe_sig(cls, name, ret, args):
    """the exact member: cls.name(args) -> ret (own or inherited); a missing one stops the build"""
    desc = "(" + "".join(jdesc(a) for a in args) + ")" + jdesc(ret)
    c = pool.get(cls)
    try:
        if name == "<init>":
            c.getConstructor(desc)
        else:
            c.getMethod(name, desc)
    except Exception:
        raise SystemExit("API probe failed: %s.%s%s not found" % (cls, name, desc))
    PROBED.append("%s.%s%s" % (cls.rsplit(".", 1)[1], name, desc))


S_ = "java.lang.String"
SIGS = [
    # worlds: open / persist / reopen (bytecode-checked behaviour in the header)
    (T["UNI"], "get", T["UNI"], []), (T["UNI"], "getWorld", T["WLD"], [S_]), (T["UNI"], "getWorld", T["WLD"], ["java.util.UUID"]),
    (T["UNI"], "isWorldLoadable", "boolean", [S_]), (T["UNI"], "loadWorld", T["CF"], [S_]),
    (T["UNI"], "getDefaultWorld", T["WLD"], []), (T["UNI"], "validateWorldPath", "java.nio.file.Path", [S_]),
    (T["UNI"], "getPlayer", T["PR"], ["java.util.UUID"]),
    (T["INS"], "get", T["INS"], []), (T["INS"], "spawnInstance", T["CF"], [S_, S_, T["WLD"], T["TRF"]]),
    (T["INS"], "doesInstanceAssetExist", "boolean", [S_]),
    # every trip (loaded, saved or new island) goes through the loading-instance call with the landing as the arrival point
    (T["INS"], "teleportPlayerToLoadingInstance", "void", [T["REF"], T["CA"], T["CF"], T["TRF"], T["TRF"]]),
    (T["INS"], "exitInstance", T["CF"], [T["REF"], T["CA"]]),
    ("java.util.concurrent.CompletableFuture", "completedFuture", T["CF"], ["java.lang.Object"]),
    (T["WLD"], "getName", S_, []), (T["WLD"], "isAlive", "boolean", []), (T["WLD"], "execute", "void", ["java.lang.Runnable"]),
    (T["WLD"], "getWorldConfig", T["WCFG"], []),
    (T["WCFG"], "getSpawnProvider", T["ISP"], []), (T["WCFG"], "setSpawnProvider", "void", [T["ISP"]]),
    (T["WCFG"], "markChanged", "void", []),
    # only OUR island counts (its generator = HandleProvider + our WorldStructure); the island's own return point is never an instance
    (T["WCFG"], "getWorldGenProvider", "com.hypixel.hytale.server.core.universe.world.worldgen.provider.IWorldGenProvider", []),
    (T["HP"], "getWorldStructureName", S_, []), (T["IWC"], "get", T["IWC"], [T["WCFG"]]),
    # the template's "Death" key = this engine field (World.getDeathConfig prefers it); probed so an engine without it stops the build
    (T["WCFG"], "getDeathConfigOverride", "com.hypixel.hytale.server.core.asset.type.gameplay.MutableDeathConfig", []),
    (T["WLD"], "getDeathConfig", "com.hypixel.hytale.server.core.asset.type.gameplay.DeathConfig", []),
    (T["ISP"], "getSpawnPoint", T["TRF"], [T["WLD"], "java.util.UUID"]), (T["ISP"], "getSpawnPoints", T["TRF"] + "[]", []),
    (T["GSP"], "<init>", "void", [T["TRF"]]),
    (T["TRF"], "<init>", "void", ["double", "double", "double", "float", "float", "float"]), (T["TRF"], "<init>", "void", [T["TRF"]]),
    (T["TRF"], "getPosition", T["VEC"], []), (T["TRF"], "getRotation", T["R3F"], []),
    (T["TP"], "createForPlayer", T["TP"], [T["WLD"], T["TRF"]]), (T["TP"], "getComponentType", T["CTYPE"], []),
    (T["CA"], "addComponent", "void", [T["REF"], T["CTYPE"], T["COMP"]]),
    (T["ST"], "getComponent", T["COMP"], [T["REF"], T["CTYPE"]]), (T["ST"], "getExternalData", "java.lang.Object", []),
    (T["TC"], "getComponentType", T["CTYPE"], []), (T["TC"], "getTransform", T["TRF"], []),
    (T["EST"], "getWorld", T["WLD"], []), (T["REF"], "getStore", T["ST"], []),
    (T["PR"], "getUuid", "java.util.UUID", []), (T["PR"], "getUsername", S_, []), (T["PR"], "getWorldUuid", "java.util.UUID", []),
    (T["PR"], "getReference", T["REF"], []), (T["PR"], "isValid", "boolean", []), (T["PR"], "sendMessage", "void", [T["MSG"]]),
    (T["PRE"], "getPlayerRef", T["REF"], []),
    (T["MSG"], "raw", T["MSG"], [S_]), (T["MSG"], "color", T["MSG"], [S_]),
    # the proof report's guard: our WorldStructure in the V2 generator's own asset map
    (T["HG"], "get", T["HG"], []), (T["HG"], "getAssetManager", T["HGAM"], []),
    (T["HGAM"], "getWorldStructureAsset", "com.hypixel.hytale.builtin.hytalegenerator.assets.worldstructures.WorldStructureAsset", [S_]),
    # plugin, commands, events, logging
    (PB, "getDataDirectory", "java.nio.file.Path", []), (PB, "getLogger", T["LOG"], []), (PB, "shutdown", "void", []),
    (PB, "getCommandRegistry", "com.hypixel.hytale.server.core.command.system.CommandRegistry", []),
    (PB, "getEventRegistry", "com.hypixel.hytale.event.EventRegistry", []),
    ("com.hypixel.hytale.event.EventRegistry", "registerGlobal", "com.hypixel.hytale.event.EventRegistration",
     ["java.lang.Class", "java.util.function.Consumer"]),
    ("com.hypixel.hytale.server.core.command.system.CommandRegistry", "registerCommand",
     "com.hypixel.hytale.server.core.command.system.CommandRegistration", [AC]),
    (AC, "setPermissionGroups", "void", ["java.lang.String[]"]), (AC, "requirePermission", "void", [S_]),
    (AC, "addSubCommand", "void", [AC]), (AC, "addUsageVariant", "void", [AC]),
    (AC, "withRequiredArg", T["RA"], [S_, S_, "com.hypixel.hytale.server.core.command.system.arguments.types.ArgumentType"]),
    (T["CTX"], "get", "java.lang.Object", ["com.hypixel.hytale.server.core.command.system.arguments.system.Argument"]),
    (T["LOG"], "at", "com.hypixel.hytale.logger.HytaleLogger$Api", ["java.util.logging.Level"]),
]
for _c, _m, _r, _a in SIGS:
    probe_sig(_c, _m, _r, _a)
for _c, _m in ((T["VEC"], "x"), (T["VEC"], "y"), (T["VEC"], "z"), (T["R3F"], "y"), (T["ATY"], "STRING")):
    B.probe(pool, _c, _m)
    PROBED.append("%s.%s" % (_c.rsplit(".", 1)[1], _m))
print("engine members probed: %d" % len(PROBED))

TOKEN = re.compile(r"@([A-Z0-9]{2,7})@")


def jv(src):
    def rep(m):
        k = m.group(1)
        if k not in T:
            raise SystemExit("unknown token @%s@ in:\n%s" % (k, src[:300]))
        return T[k]
    return TOKEN.sub(rep, src)


def F(cls, src):
    cls.addField(CtField.make(jv(src), cls))


def M(cls, src):
    try:
        cls.addMethod(CtNewMethod.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("compile failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:2500]))


def C(cls, src):
    try:
        cls.addConstructor(CtNewConstructor.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("constructor failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:2500]))


def jstr(s):
    assert all(32 <= ord(c) < 127 for c in s), repr(s)
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def jtext(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def jarr(xs):
    return "new String[] { " + ", ".join(jstr(x) for x in xs) + " }"


def jints(xs):
    return "new int[] { " + ", ".join(str(int(x)) for x in xs) + " }"


def fmtnum(v):
    v = round(float(v), 2)
    return str(int(v)) if v == int(v) else ("%.2f" % v).rstrip("0").rstrip(".")


LANDING_TEXT = " ".join(fmtnum(v) for v in G["landing"])
RING_TEXT = ", ".join("%s %d-%d" % (r[7], max(0, r[1]), min(r[2], R)) for r in G["rings"])
SIZE_TEXT = "%s - radius %d blocks" % (G["preset"], R)

# ================================================================= classes (all top-level; methods before callers)
lg = pool.makeClass(PKG + ".WgLog")
zn = pool.makeClass(PKG + ".WgZones")
cfg = pool.makeClass(PKG + ".WgCfg")
sto = pool.makeClass(PKG + ".WgStore")
chk = pool.makeClass(PKG + ".WgCheck")
cmds = pool.makeClass(PKG + ".WgCmds")
apl = pool.makeClass(PKG + ".WgApplyLanding")
opn = pool.makeClass(PKG + ".WgOpen")
done = pool.makeClass(PKG + ".WgDone")
rdy = pool.makeClass(PKG + ".WgReady")
here = pool.makeClass(PKG + ".WgHereTask")
hooks = pool.makeClass(PKG + ".WgHooks")
pl = pool.makeClass(PKG + ".SkyyWorldGenPlugin", pool.get(T["JP"]))
ALL = [lg, zn, cfg, sto, chk, cmds, apl, opn, done, rdy, here, hooks]

# ---------------------------------------------------------------- WgLog: the server log (every class may call it)
F(lg, "public static @LOG@ LOG;")
F(lg, "public static final java.util.concurrent.ConcurrentHashMap ONCE = new java.util.concurrent.ConcurrentHashMap();")
for _lvl, _nm in (("INFO", "info"), ("WARNING", "warn"), ("SEVERE", "error")):
    M(lg, r"""
public static void %s(String msg) {
  try {
    if (LOG != null) LOG.at(java.util.logging.Level.%s).log("[SkyyWorldGen] " + msg);
    else System.out.println("[SkyyWorldGen] %s" + msg);
  } catch (Throwable t) { }
}""" % (_nm, _lvl, "" if _nm == "info" else _lvl + " "))
M(lg, "public static boolean once(String key) { return key != null && ONCE.putIfAbsent(key, Boolean.TRUE) == null; }")

# ---------------------------------------------------------------- WgZones: the zone table (generated from GEOMETRY; one zone in 0.1)
F(zn, "public static final String[] IDS = %s;" % jarr([G["zone"]]))
F(zn, "public static final String[] NAMES = %s;" % jarr([G["name"]]))
F(zn, "public static final String[] WORLDS = %s;" % jarr([G["world"]]))
F(zn, "public static final String[] TEMPLATES = %s;" % jarr([G["template"]]))
F(zn, "public static final String[] STRUCTURES = %s;" % jarr([G["structure"]]))
F(zn, "public static final int[] RADIUS = %s;" % jints([R]))
F(zn, "public static final int[] RING_MAX = %s;" % jints([r[2] for r in G["rings"]]))
F(zn, "public static final String[] RING_NAMES = %s;" % jarr([r[7] for r in G["rings"]]))
F(zn, "public static final String SIZE_TEXT = %s;" % jstr(SIZE_TEXT))
F(zn, "public static final String RING_TEXT = %s;" % jstr(RING_TEXT))
M(zn, r"""
public static int index(String arg) {
  if (arg == null) return -1;
  String a = arg.trim().toLowerCase();
  if (a.startsWith("zone")) a = a.substring(4).trim();
  else if (a.startsWith("z")) a = a.substring(1).trim();
  for (int i = 0; i < IDS.length; i++) {
    if (IDS[i].equals(a) || NAMES[i].toLowerCase().equals(arg.trim().toLowerCase()) || WORLDS[i].equals(arg.trim().toLowerCase())) return i;
  }
  return -1;
}""")
M(zn, r"""
public static int worldIndex(String world) {
  if (world == null) return -1;
  for (int i = 0; i < WORLDS.length; i++) if (WORLDS[i].equalsIgnoreCase(world)) return i;
  return -1;
}""")
M(zn, "public static String label(int zi) { return \"Zone \" + IDS[zi] + \" - \" + NAMES[zi]; }")
M(zn, "public static double dist(double x, double z) { return Math.sqrt(x * x + z * z); }")
# the island's top curve (Base + GEOMETRY "top", blocks; zone 1 = the only zone in 0.1) for the landing.point Y check (review finding 2)
F(zn, "public static final double BASE = %r;" % float(G["base"]))
F(zn, "public static final double[] TOP_D = new double[] { %s };" % ", ".join(repr(float(a)) for a, _b in G["top"]))
F(zn, "public static final double[] TOP_H = new double[] { %s };" % ", ".join(repr(float(b)) for _a, b in G["top"]))
M(zn, r"""
public static double topAt(double d) {
  if (d <= TOP_D[0]) return BASE + TOP_H[0];
  for (int i = 1; i < TOP_D.length; i++) {
    if (d <= TOP_D[i]) return BASE + TOP_H[i - 1] + (TOP_H[i] - TOP_H[i - 1]) * (d - TOP_D[i - 1]) / (TOP_D[i] - TOP_D[i - 1]);
  }
  return BASE + TOP_H[TOP_H.length - 1];
}""")
# a loaded world is THE island only when its generator is a HandleProvider with our WorldStructure (review finding 4): a creation that
# died before its first config write boots as a default-config world with our name (WorldConfig.load default + Universe.start)
M(zn, r"""
public static boolean isIsland(int zi, @WLD@ w) {
  if (w == null || zi < 0) return false;
  try {
    @WCFG@ c = w.getWorldConfig();
    if (c == null) return false;
    Object p = c.getWorldGenProvider();
    if (!(p instanceof @HP@)) return false;
    return STRUCTURES[zi].equals(((@HP@) p).getWorldStructureName());
  } catch (Throwable t) { return false; }
}""")
M(zn, r"""
public static int islandIndex(@WLD@ w) {
  if (w == null) return -1;
  int zi = worldIndex(w.getName());
  return zi >= 0 && isIsland(zi, w) ? zi : -1;
}""")
# the ring by plain distance from the centre (the terrain's ring border is warped by up to about 16 blocks - proof report T12)
M(zn, r"""
public static String ringAt(int zi, double x, double z) {
  double d = dist(x, z);
  if (d > RADIUS[zi] + 24) return "the void";
  if (d >= RADIUS[zi]) return "the rim edge";
  for (int i = 0; i < RING_MAX.length; i++) if (d < RING_MAX[i]) return RING_NAMES[i];
  return "the rim edge";
}""")

# ---------------------------------------------------------------- WgCfg: config.properties (the kit writes it; this class reads it)
CFG_TEXT = "\n".join([
    "# SkyyWorldGen %s - settings. Also in game: SkyWynn Menu > Server Setup > World Gen (admins). Hand edits: /zone reload." % VERSION,
    "# The island itself (size, rings, heights, seed) is fixed in the jar's World Gen V2 files - a new size means a new world.",
    "",
    "# Zone islands on / off. false = /zone refuses (players already on an island stay; /hub and /zone leave still work).",
    "part.zones=true",
    "",
    "# Zone 1 landing point 'x y z yaw' (blocks; yaw in degrees, 0 = facing the island core from the south rim).",
    "# /zone 1 lands you here and void deaths respawn here (unless you slept in a bed on the island). Must be on the island's",
    "# ground: at most %d blocks from the centre, Y near the ground there (easiest: stand on the spot and use /zone setlanding)." % LANDING_MAX_DIST,
    "landing.point=%s" % LANDING_TEXT,
    "",
])
assert all(ord(c) < 127 for c in CFG_TEXT)
F(cfg, "public static volatile boolean ON = true;")
F(cfg, "public static volatile String LANDING = %s;" % jstr(LANDING_TEXT))
F(cfg, "public static java.nio.file.Path DIR;")
F(cfg, "public static java.nio.file.Path FILE;")
F(cfg, "public static volatile String LOADED = \"\";")
F(cfg, "public static final String DEF_CFG = %s;" % jtext(CFG_TEXT))
F(cfg, "public static final double[] DEF_LANDING = new double[] { %s };" % ", ".join(repr(float(v)) for v in G["landing"]))
F(cfg, "public static final int LANDING_MAX = %d;" % LANDING_MAX_DIST)
F(cfg, "public static final double Y_BELOW = %r;" % LANDING_Y_BELOW)
F(cfg, "public static final double Y_ABOVE = %r;" % LANDING_Y_ABOVE)
M(cfg, r"""
public static String fmt(double v) {
  double r = Math.round(v * 100.0) / 100.0;
  if (r == Math.rint(r) && Math.abs(r) < 1.0E9) return String.valueOf((long) r);
  return java.math.BigDecimal.valueOf(r).stripTrailingZeros().toPlainString();
}""")
# "x y z [yaw]" (spaces and / or commas) -> {x, y, z, yaw}; null when it is not 3 or 4 finite numbers
M(cfg, r"""
public static double[] parseLanding(String s) {
  if (s == null) return null;
  String t = s.trim().replace(',', ' ');
  if (t.length() == 0 || t.length() > 60) return null;
  String[] p = t.split("\\s+");
  if (p.length < 3 || p.length > 4) return null;
  double[] r = new double[4];
  try {
    for (int i = 0; i < p.length; i++) {
      r[i] = Double.parseDouble(p[i]);
      if (Double.isNaN(r[i]) || Double.isInfinite(r[i])) return null;
    }
  } catch (Throwable e) { return null; }
  return r;
}""")
# the Y must be on the island's GROUND at that distance (review finding 2): a Y under the island = arrive in the void, die, respawn
# there again. Window = the island's top curve -Y_BELOW .. +Y_ABOVE (harness G2 measures it against the generated terrain)
M(cfg, r"""
public static String landingCheck(double[] p, int zi) {
  if (p == null) return "Type x y z (and optionally yaw), e.g. 0.5 144 344.5 0.";
  if (p[1] < 1.0 || p[1] > 318.0) return "Y must be from 1 to 318 (the world is 320 blocks high).";
  double d = Math.sqrt(p[0] * p[0] + p[2] * p[2]);
  if (d > LANDING_MAX) return "That is " + fmt(d) + " blocks from the island centre - the landing must be on the island (at most " + LANDING_MAX + ").";
  if (p[3] < -360.0 || p[3] > 360.0) return "Yaw is in degrees, -360 to 360 (0 = facing the core from the south rim).";
  double top = @PKG@.WgZones.topAt(d);
  double lo = Math.ceil(top - Y_BELOW);
  double hi = Math.floor(top + Y_ABOVE);
  if (p[1] < lo || p[1] > hi) return "Y " + fmt(p[1]) + " is not on the island's ground: " + fmt(d) + " blocks from the centre the ground is near y " + Math.round(top) + " - use a Y from " + fmt(lo) + " to " + fmt(hi) + " (or stand there and use /zone setlanding).";
  return null;
}""")
M(cfg, "public static String landingText(double[] p) { return fmt(p[0]) + \" \" + fmt(p[1]) + \" \" + fmt(p[2]) + \" \" + fmt(p[3]); }")
M(cfg, r"""
public static double[] landing(int zi) {
  double[] p = parseLanding(LANDING);
  if (p == null || landingCheck(p, zi) != null) {
    if (@PKG@.WgLog.once("badlanding:" + LANDING)) @PKG@.WgLog.warn("landing.point '" + LANDING + "' is not usable - using the default " + landingText(DEF_LANDING));
    return new double[] { DEF_LANDING[0], DEF_LANDING[1], DEF_LANDING[2], DEF_LANDING[3] };
  }
  return p;
}""")
M(cfg, r"""
public static java.util.Properties read(java.nio.file.Path f) {
  if (f == null) return null;
  java.io.InputStream in = null;
  try {
    if (!java.nio.file.Files.isRegularFile(f, new java.nio.file.LinkOption[0])) return null;
    in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
    java.util.Properties p = new java.util.Properties();
    p.load(in);
    return p;
  } catch (Throwable t) {
    @PKG@.WgLog.warn("could not read " + f + ": " + t + " - using the built-in defaults for it");
    return null;
  } finally {
    try { if (in != null) in.close(); } catch (Throwable t2) { }
  }
}""")
M(cfg, r"""
public static void seed(java.nio.file.Path f, String text) {
  if (f == null) return;
  try {
    if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return;
    java.nio.file.Path dir = f.getParent();
    if (dir != null) java.nio.file.Files.createDirectories(dir, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = f.resolveSibling(f.getFileName().toString() + ".tmp");
    java.nio.file.Files.write(tmp, text.getBytes("ISO-8859-1"), new java.nio.file.OpenOption[0]);
    java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
    @PKG@.WgLog.info("wrote the default " + f.getFileName());
  } catch (Throwable t) { @PKG@.WgLog.warn("could not write the default " + f + ": " + t); }
}""")
M(cfg, r"""
public static java.util.Properties props(String text) {
  java.util.Properties p = new java.util.Properties();
  try { p.load(new java.io.StringReader(text)); } catch (Throwable t) { }
  return p;
}""")
M(cfg, r"""
public static void apply(java.util.Properties p) {
  String on = p.getProperty("part.zones", "true").trim().toLowerCase();
  ON = !(on.equals("false") || on.equals("off") || on.equals("no") || on.equals("0"));
  String l = p.getProperty("landing.point", "").trim();
  double[] lp = parseLanding(l);
  String why = landingCheck(lp, 0);
  if (why == null) LANDING = l;
  else {
    LANDING = landingText(DEF_LANDING);
    if (l.length() > 0) @PKG@.WgLog.warn("landing.point '" + l + "' refused (" + why + ") - using the default " + LANDING);
  }
  LOADED = "zone islands " + (ON ? "on" : "OFF") + ", Zone 1 landing " + LANDING;
}""")
# (WgCfg.reloadAll / load come after WgApplyLanding: a reload moves the loaded island's spawn point at once - review finding 3)

# ---------------------------------------------------------------- WgStore: worlds.properties - one record per generated zone world
F(sto, "public static java.nio.file.Path FILE;")
F(sto, "public static java.util.Properties P = new java.util.Properties();")
M(sto, r"""
public static synchronized void read() {
  java.util.Properties p = @PKG@.WgCfg.read(FILE);
  P = p == null ? new java.util.Properties() : p;
}""")
M(sto, r"""
public static synchronized long created(String world) {
  try { return Long.parseLong(P.getProperty(world + ".createdMillis", "0").trim()); } catch (Throwable t) { return 0L; }
}""")
M(sto, r"""
public static synchronized String createdText(String world) {
  long c = created(world);
  if (c <= 0L) return null;
  return java.time.Instant.ofEpochMilli(c).toString().substring(0, 10) + " (SkyyWorldGen " + P.getProperty(world + ".by", "?") + ")";
}""")
M(sto, r"""
public static synchronized boolean markCreated(String world, String template, String structure) {
  P.setProperty(world + ".createdMillis", String.valueOf(System.currentTimeMillis()));
  P.setProperty(world + ".template", template);
  P.setProperty(world + ".structure", structure);
  P.setProperty(world + ".by", "@VERSION@");
  if (FILE == null) return false;
  try {
    java.nio.file.Path dir = FILE.getParent();
    if (dir != null) java.nio.file.Files.createDirectories(dir, new java.nio.file.attribute.FileAttribute[0]);
    java.util.TreeSet keys = new java.util.TreeSet(P.stringPropertyNames());
    StringBuilder sb = new StringBuilder("# SkyyWorldGen - the zone island worlds this server generated (one record per world, written once by /zone).\n");
    sb.append("# Delete a world's lines only together with its folder universe/worlds/<world> (server stopped).\n");
    java.util.Iterator it = keys.iterator();
    while (it.hasNext()) {
      String k = (String) it.next();
      sb.append(k).append('=').append(P.getProperty(k)).append('\n');
    }
    java.nio.file.Path tmp = FILE.resolveSibling(FILE.getFileName().toString() + ".tmp");
    java.nio.file.Files.write(tmp, sb.toString().getBytes("ISO-8859-1"), new java.nio.file.OpenOption[0]);
    try {
      java.nio.file.Files.move(tmp, FILE, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING, java.nio.file.StandardCopyOption.ATOMIC_MOVE });
    } catch (java.nio.file.AtomicMoveNotSupportedException e) {
      java.nio.file.Files.move(tmp, FILE, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
    }
    return true;
  } catch (Throwable t) {
    @PKG@.WgLog.warn("could not write " + FILE + ": " + t + " (the world itself is fine)");
    return false;
  }
}""")

# ---------------------------------------------------------------- WgCheck: our assets reached the generator; the template is in the jar
F(chk, "public static final boolean[] OK = new boolean[%d];" % 1)
M(chk, r"""
public static String structureProblem(int zi) {
  if (zi < 0) return "unknown zone";
  if (OK[zi]) return null;
  try {
    @HG@ hg = @HG@.get();
    if (hg == null) return "the World Gen V2 plugin (HytaleGenerator) is not running on this server";
    @HGAM@ am = hg.getAssetManager();
    if (am == null) return "the World Gen V2 assets are not loaded yet - try again in a moment";
    if (am.getWorldStructureAsset(@PKG@.WgZones.STRUCTURES[zi]) == null) {
      if (@PKG@.WgLog.once("nostruct" + zi)) @PKG@.WgLog.error("the island files did not reach the World Gen V2 generator (WorldStructure " + @PKG@.WgZones.STRUCTURES[zi] + " is not in HytaleGenerator's asset map) - /zone " + @PKG@.WgZones.IDS[zi] + " refuses, so the generator's fallback (empty chunks) never saves void chunks into the island. Look for SkyWynn lines (Couldn't find / Failed to validate) above.");
      return "the island files (WorldStructure " + @PKG@.WgZones.STRUCTURES[zi] + ") did not load - the server log says why";
    }
    OK[zi] = true;
    return null;
  } catch (Throwable t) { return "the World Gen V2 check failed: " + t; }
}""")
M(chk, r"""
public static boolean templateOk(int zi) {
  try { return @INS@.doesInstanceAssetExist(@PKG@.WgZones.TEMPLATES[zi]); } catch (Throwable t) { return false; }
}""")

# ---------------------------------------------------------------- WgCmds part 1: chat lines (+ success, - error, = info; kit colours)
for _s in SUI.java_status_methods():
    M(cmds, _s)
M(cmds, r"""
public static void tell(@PR@ p, String res) {
  if (p == null || res == null || res.length() == 0) return;
  try { p.sendMessage(@MSG@.raw(textOf(res)).color(colorOf(res))); } catch (Throwable t) { }
}""")
M(cmds, r"""
public static void tellAll(@PR@ p, String[] lines) {
  for (int i = 0; lines != null && i < lines.length; i++) tell(p, lines[i]);
}""")

# ---------------------------------------------------------------- WgApplyLanding: the world's spawn point (= void respawn) = the landing
apl.addInterface(pool.get("java.lang.Runnable"))
F(apl, "public @WLD@ w;")
F(apl, "public static volatile int APPLIED = 0;")
C(apl, "public WgApplyLanding(@WLD@ w) { this.w = w; }")
M(apl, r"""
public static boolean near(double a, double b) { return Math.abs(a - b) < 0.001; }""")
M(apl, r"""
public static boolean same(@ISP@ sp, double[] p) {
  if (!(sp instanceof @GSP@)) return false;
  @TRF@[] ts = sp.getSpawnPoints();
  if (ts == null || ts.length != 1 || ts[0] == null) return false;
  @VEC@ v = ts[0].getPosition();
  if (v == null || !near(v.x, p[0]) || !near(v.y, p[1]) || !near(v.z, p[2])) return false;
  @R3F@ r = ts[0].getRotation();
  double yaw = r == null ? 0.0 : (double) r.y;
  double want = Math.toRadians(p[3]);
  double diff = Math.abs(Math.IEEEremainder(yaw - want, Math.PI * 2.0));
  return diff < 0.001;
}""")
M(apl, r"""
public static @TRF@ transformOf(double[] p) {
  return new @TRF@(p[0], p[1], p[2], 0.0f, (float) Math.toRadians(p[3]), 0.0f);
}""")
# returns true when it changed the world config (only then: no churn on a world that already matches)
M(apl, r"""
public static boolean applyTo(@WLD@ w) {
  if (w == null) return false;
  int zi = @PKG@.WgZones.islandIndex(w);
  if (zi < 0) return false;
  double[] p = @PKG@.WgCfg.landing(zi);
  @WCFG@ c = w.getWorldConfig();
  if (c == null) return false;
  if (same(c.getSpawnProvider(), p)) return false;
  c.setSpawnProvider(new @GSP@(transformOf(p)));
  c.markChanged();
  APPLIED++;
  @PKG@.WgLog.info(@PKG@.WgZones.label(zi) + ": world spawn point (where void deaths respawn) set to the landing point " + @PKG@.WgCfg.landingText(p));
  return true;
}""")
M(apl, r"""
public void run() {
  try {
    if (this.w == null || !this.w.isAlive()) return;
    applyTo(this.w);
  } catch (Throwable t) { @PKG@.WgLog.warn("could not set the zone world's spawn point: " + t); }
}""")

# ---------------------------------------------------------------- WgCfg part 2: reload = re-read + the loaded island's spawn follows at once
# (review finding 3: after a hand edit + /zone reload the spawn point - where void deaths respawn - moved only on the next arrival)
M(cfg, r"""
public static int syncLanding() {
  int n = 0;
  try {
    @UNI@ u = @UNI@.get();
    if (u == null) return 0;
    for (int i = 0; i < @PKG@.WgZones.WORLDS.length; i++) {
      @WLD@ w = u.getWorld(@PKG@.WgZones.WORLDS[i]);
      if (w != null && w.isAlive() && @PKG@.WgZones.isIsland(i, w)) {
        w.execute(new @PKG@.WgApplyLanding(w));
        n++;
      }
    }
  } catch (Throwable t) { }
  return n;
}""")
M(cfg, r"""
public static void reloadAll() {
  java.util.Properties c = read(FILE);
  if (c == null) c = props(DEF_CFG);
  apply(c);
  syncLanding();
}""")
M(cfg, r"""
public static void load() {
  seed(FILE, DEF_CFG);
  reloadAll();
}""")

# ---------------------------------------------------------------- WgOpen fields + the load bookkeeping WgDone needs first
F(opn, "public static final java.util.concurrent.ConcurrentHashMap CREATING = new java.util.concurrent.ConcurrentHashMap();")
F(opn, "public static final java.util.HashMap LOADING = new java.util.HashMap();")
F(opn, "public static volatile int SPAWNS = 0;")
F(opn, "public static volatile int LOADS = 0;")
M(opn, r"""
public static synchronized void loadFinished(String name) {
  Object f = LOADING.get(name);
  if (f instanceof @CF@ && ((@CF@) f).isDone()) LOADING.remove(name);
}""")
M(opn, r"""
public static synchronized @CF@ loadingFor(String name) {
  Object f = LOADING.get(name);
  if (f instanceof @CF@ && !((@CF@) f).isDone()) return (@CF@) f;
  return null;
}""")

# ---------------------------------------------------------------- WgDone: completion of a creation / reopen future (any thread)
done.addInterface(pool.get("java.util.function.BiConsumer"))
F(done, "public String kind;")
F(done, "public int zi;")
F(done, "public Object mark;")
F(done, "public @PR@ pr;")
C(done, "public WgDone(String kind, int zi, Object mark, @PR@ pr) { this.kind = kind; this.zi = zi; this.mark = mark; this.pr = pr; }")
M(done, r"""
public void accept(Object result, Object err) {
  try {
    String name = @PKG@.WgZones.WORLDS[this.zi];
    if ("load".equals(this.kind)) {
      @PKG@.WgOpen.loadFinished(name);
      if (err != null) {
        @PKG@.WgLog.warn("loading the zone world '" + name + "' failed: " + err);
        @PKG@.WgCmds.tell(this.pr, "-[Zone] The island could not be loaded - the server log has the details.");
      } else @PKG@.WgLog.info(@PKG@.WgZones.label(this.zi) + ": world '" + name + "' loaded from disk");
      return;
    }
    if (this.mark != null) @PKG@.WgOpen.CREATING.remove(name, this.mark);
    if (err == null && result instanceof @WLD@) {
      @PKG@.WgStore.markCreated(name, @PKG@.WgZones.TEMPLATES[this.zi], @PKG@.WgZones.STRUCTURES[this.zi]);
      @PKG@.WgLog.info(@PKG@.WgZones.label(this.zi) + ": island world '" + name + "' created from the template " + @PKG@.WgZones.TEMPLATES[this.zi] + " (it is kept from now on; later trips load it)");
      return;
    }
    @PKG@.WgLog.warn("creating the zone world '" + name + "' failed: " + err);
    @PKG@.WgCmds.tell(this.pr, "-[Zone] The island could not be created - the server log has the details. Try /zone " + @PKG@.WgZones.IDS[this.zi] + " again in a moment.");
  } catch (Throwable t) { }
}""")

# ---------------------------------------------------------------- WgOpen: decide + open + move (world thread of the player)
# decision codes: 1 loaded (teleport), 2 already on that island (back to the landing), 3 load from disk, 4 create (first time), 5 busy,
# 6 broken folder, 7 template missing, 8 structure not loaded, 9 zone islands off, 10 a load is running (join it),
# 11 a loaded world with the island's name that is NOT the island (its generator is not our WorldStructure - review finding 4)
M(opn, r"""
public static java.nio.file.Path folderOf(String name) {
  try { return @UNI@.get().validateWorldPath(name); } catch (Throwable t) { return null; }
}""")
M(opn, r"""
public static boolean folderExists(String name) {
  java.nio.file.Path p = folderOf(name);
  return p != null && java.nio.file.Files.isDirectory(p, new java.nio.file.LinkOption[0]);
}""")
M(opn, r"""
public static int decide(int zi, @WLD@ from) {
  if (!@PKG@.WgCfg.ON) return 9;
  if (@PKG@.WgCheck.structureProblem(zi) != null) return 8;
  String name = @PKG@.WgZones.WORLDS[zi];
  @UNI@ uni = @UNI@.get();
  @WLD@ w = uni.getWorld(name);
  if (w != null) {
    if (!@PKG@.WgZones.isIsland(zi, w)) return 11;
    if (!w.isAlive()) return 5;
    return from == w ? 2 : 1;
  }
  if (loadingFor(name) != null) return 10;
  // a creation that is still running comes BEFORE the disk checks: the engine writes config.json before it registers the world, and
  // a loadWorld in that window would race the creation ("already exists but didn't before")
  Object since = CREATING.get(name);
  if (since instanceof Long && System.currentTimeMillis() - ((Long) since).longValue() < 120000L) return 5;
  if (uni.isWorldLoadable(name)) return 3;
  if (folderExists(name)) return 6;
  if (!@PKG@.WgCheck.templateOk(zi)) return 7;
  return 4;
}""")
# reopen a saved world: Universe.loadWorld (addWorld refuses a world that exists on disk); one shared future per world
M(opn, r"""
public static synchronized @CF@ openSaved(int zi, @PR@ pr) {
  String name = @PKG@.WgZones.WORLDS[zi];
  Object f = LOADING.get(name);
  if (f instanceof @CF@ && !((@CF@) f).isDone()) return (@CF@) f;
  @UNI@ uni = @UNI@.get();
  @WLD@ w = uni.getWorld(name);
  if (w != null) return @CF@.completedFuture(w);
  @CF@ nf = uni.loadWorld(name);
  LOADING.put(name, nf);
  LOADS++;
  nf.whenComplete(new @PKG@.WgDone("load", zi, null, pr));
  return nf;
}""")
# spawnInstance stores 'ret' as the world's own return point (Plugin.Instance.ReturnPoint in its config.json). A null transform there is
# saved without its "ReturnPoint" key and the config can then NEVER be decoded again ("Failed to decode 'Plugin'" - the harness made one)
# - so the creation never passes null: the player's position, else the spawn point of the world they came from, else (0, 100, 0)
M(opn, r"""
public static @TRF@ safeReturn(@WLD@ from, @PR@ pr, @TRF@ ret) {
  if (ret != null) return ret;
  try {
    if (from != null && from.getWorldConfig() != null && from.getWorldConfig().getSpawnProvider() != null) {
      @TRF@ t = from.getWorldConfig().getSpawnProvider().getSpawnPoint(from, pr == null ? null : pr.getUuid());
      if (t != null) return new @TRF@(t);
    }
  } catch (Throwable e) { }
  return new @TRF@(0.0, 100.0, 0.0);
}""")
# the island's OWN return point must not be another instance (review finding 5): spawnInstance stores from + ret in the island's
# config, and exitInstance uses it for anyone without a personal return point (after a restart) - from a SkyyIslands island that would
# send a later /zone leave into that private island. An instance 'from' -> the default world and its spawn point instead.
M(opn, r"""
public static boolean isInstance(@WLD@ w) {
  try { return w != null && w.getWorldConfig() != null && @IWC@.get(w.getWorldConfig()) != null; } catch (Throwable t) { return false; }
}""")
M(opn, r"""
public static @WLD@ returnWorld(@WLD@ from) {
  if (from != null && !isInstance(from)) return from;
  try {
    @WLD@ d = @UNI@.get().getDefaultWorld();
    if (d != null && d.isAlive() && !isInstance(d) && @PKG@.WgZones.worldIndex(d.getName()) < 0) return d;
  } catch (Throwable t) { }
  return from;
}""")
# the FIRST trip: copy the jar's template into universe/worlds/<name> and make the world (InstancesPlugin.spawnInstance); null = failed
M(opn, r"""
public static @CF@ startCreate(int zi, @WLD@ from, @TRF@ ret0, @PR@ pr) {
  String name = @PKG@.WgZones.WORLDS[zi];
  @WLD@ rw = returnWorld(from);
  @TRF@ ret = rw == from ? safeReturn(from, pr, ret0) : safeReturn(rw, pr, null);
  if (rw != from) @PKG@.WgLog.info(@PKG@.WgZones.label(zi) + ": first opened from the instance world '" + (from == null ? "?" : from.getName()) + "' - the island's own return point is the default world '" + rw.getName() + "' spawn instead");
  Long mark = Long.valueOf(System.currentTimeMillis());
  CREATING.put(name, mark);
  if (@PKG@.WgStore.created(name) > 0L) @PKG@.WgLog.warn(@PKG@.WgZones.label(zi) + ": the world folder '" + name + "' is gone although this server made it before - generating a fresh island (same seed)");
  try {
    @INS@ ins = @INS@.get();
    if (ins == null) { CREATING.remove(name, mark); @PKG@.WgLog.warn("the Instances plugin is not running - cannot create '" + name + "'"); return null; }
    @CF@ f = ins.spawnInstance(@PKG@.WgZones.TEMPLATES[zi], name, rw, ret);
    SPAWNS++;
    f.whenComplete(new @PKG@.WgDone("create", zi, mark, pr));
    return f;
  } catch (Throwable t) {
    CREATING.remove(name, mark);
    @PKG@.WgLog.warn("creating '" + name + "' failed at once: " + t);
    return null;
  }
}""")
M(opn, r"""
public static @TRF@ here(@ST@ store, @REF@ ref) {
  try {
    @TC@ tc = (@TC@) store.getComponent(ref, @TC@.getComponentType());
    if (tc != null && tc.getTransform() != null) return new @TRF@(tc.getTransform());
  } catch (Throwable t) { }
  return null;
}""")
M(opn, "public static @TRF@ landing(int zi) { return @PKG@.WgApplyLanding.transformOf(@PKG@.WgCfg.landing(zi)); }")
M(opn, r"""
public static String refusal(int d, int zi) {
  String z = "/zone " + @PKG@.WgZones.IDS[zi];
  if (d == 9) return "-[Zone] Zone islands are switched off (Server Setup > World Gen > Zone islands).";
  if (d == 8) return "-[Zone] " + @PKG@.WgZones.label(zi) + " can't open: " + @PKG@.WgCheck.structureProblem(zi) + ".";
  if (d == 7) return "-[Zone] The island template " + @PKG@.WgZones.TEMPLATES[zi] + " is missing from the SkyyWorldGen jar - nothing was created.";
  if (d == 11) return "-[Zone] A world named " + @PKG@.WgZones.WORLDS[zi] + " is loaded but it is not the zone island (its world generator is not " + @PKG@.WgZones.STRUCTURES[zi] + " - a first creation that did not finish?). Stop the server, delete the folder " + folderOf(@PKG@.WgZones.WORLDS[zi]) + ", then " + z + " makes the island again.";
  if (d == 6) return "-[Zone] The world folder " + folderOf(@PKG@.WgZones.WORLDS[zi]) + " exists but holds no world config (a first creation that did not finish). Stop the server, delete that folder, then " + z + " makes the island again.";
  if (d == 5) return "-[Zone] The island is being created or closed right now - try " + z + " again in a few seconds.";
  return null;
}""")
M(opn, r"""
public static void go(@ST@ store, @REF@ ref, @PR@ pr, @WLD@ from, int zi) {
  int d = decide(zi, from);
  String no = refusal(d, zi);
  if (d == 11 && @PKG@.WgLog.once("foreign" + zi)) @PKG@.WgLog.warn("the loaded world '" + @PKG@.WgZones.WORLDS[zi] + "' is not the " + @PKG@.WgZones.label(zi) + " island (its generator is not the WorldStructure " + @PKG@.WgZones.STRUCTURES[zi] + ") - /zone refuses it and never changes it. Stop the server and delete " + folderOf(@PKG@.WgZones.WORLDS[zi]) + " to make the island again.");
  if (no != null) { @PKG@.WgCmds.tell(pr, no); return; }
  String name = @PKG@.WgZones.WORLDS[zi];
  String label = @PKG@.WgZones.label(zi);
  @TRF@ land = landing(zi);
  if (d == 2) {
    ((@CA@) store).addComponent(ref, @TP@.getComponentType(), @TP@.createForPlayer(from, land));
    @PKG@.WgCmds.tell(pr, "=[Zone] Back to the landing point of " + label + ".");
    return;
  }
  @TRF@ ret = here(store, ref);
  if (d == 1) {
    @WLD@ w = @UNI@.get().getWorld(name);
    if (w == null || !w.isAlive()) { @PKG@.WgCmds.tell(pr, "-[Zone] The island just closed - try /zone " + @PKG@.WgZones.IDS[zi] + " again."); return; }
    @PKG@.WgCmds.tell(pr, "=[Zone] Teleporting to " + label + "...");
    // the loading-instance call with a finished future (review finding 3): the arrival is the CURRENT landing point, not the
    // world's saved spawn point (teleportPlayerToInstance), which a hand edit + /zone reload may not have moved yet
    @INS@.teleportPlayerToLoadingInstance(ref, (@CA@) store, @CF@.completedFuture(w), ret, land);
    return;
  }
  @CF@ f = null;
  if (d == 10) { f = loadingFor(name); @PKG@.WgCmds.tell(pr, "=[Zone] " + label + " is loading - you will arrive when it is ready..."); }
  if (d == 3) { f = openSaved(zi, pr); @PKG@.WgCmds.tell(pr, "=[Zone] Loading " + label + "..."); }
  if (d == 4) {
    f = startCreate(zi, from, ret, pr);
    if (f == null) { @PKG@.WgCmds.tell(pr, "-[Zone] The island could not be created - the server log has the details."); return; }
    @PKG@.WgCmds.tell(pr, "=[Zone] Creating " + label + " - the first trip generates the island (a few seconds)...");
  }
  if (f == null) { @PKG@.WgCmds.tell(pr, "-[Zone] Could not open the island just now - try again."); return; }
  @INS@.teleportPlayerToLoadingInstance(ref, (@CA@) store, f, ret, land);
}""")
M(opn, r"""
public static boolean sendDefault(@ST@ store, @REF@ ref, @PR@ pr) {
  @UNI@ uni = @UNI@.get();
  @WLD@ target = uni.getDefaultWorld();
  if (target == null || @PKG@.WgZones.worldIndex(target.getName()) >= 0) return false;
  @TRF@ where = target.getWorldConfig().getSpawnProvider().getSpawnPoint(target, pr.getUuid());
  if (where == null) return false;
  ((@CA@) store).addComponent(ref, @TP@.getComponentType(), @TP@.createForPlayer(target, where));
  return true;
}""")
# /zone leave: InstancesPlugin.exitInstance = back to where the player ran /zone (their return point), else the world's, else the
# default world spawn (the engine's own fallback); if it throws, our own default-world fallback
M(opn, r"""
public static void leave(@ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  if (world == null || @PKG@.WgZones.worldIndex(world.getName()) < 0) {
    @PKG@.WgCmds.tell(pr, "-[Zone] You are not on a zone island. (/hub takes you to the hub.)");
    return;
  }
  try {
    @INS@.exitInstance(ref, (@CA@) store);
    @PKG@.WgCmds.tell(pr, "=[Zone] Leaving the island...");
    return;
  } catch (Throwable t) {
    @PKG@.WgLog.warn("exitInstance failed for " + pr.getUsername() + " (" + t + ") - sending them to the default world spawn");
  }
  if (sendDefault(store, ref, pr)) @PKG@.WgCmds.tell(pr, "=[Zone] Leaving the island - to the main world spawn...");
  else @PKG@.WgCmds.tell(pr, "-[Zone] There is no world to send you to - try /hub.");
}""")

# ---------------------------------------------------------------- WgReady: every arrival on a zone island -> the spawn point follows the landing
rdy.addInterface(pool.get("java.util.function.Consumer"))
C(rdy, "public WgReady() { }")
M(rdy, r"""
public void accept(Object ev) {
  try {
    @PRE@ e = (@PRE@) ev;
    @REF@ r = e.getPlayerRef();
    if (r == null) return;
    @ST@ st = r.getStore();
    if (st == null) return;
    Object ext = st.getExternalData();
    if (!(ext instanceof @EST@)) return;
    @WLD@ w = ((@EST@) ext).getWorld();
    if (w == null || @PKG@.WgZones.worldIndex(w.getName()) < 0) return;
    w.execute(new @PKG@.WgApplyLanding(w));
  } catch (Throwable t) { }
}""")

# ================================================================= the config kit (Server Setup > World Gen)
CFG_FILE = "Skyy_SkyyWorldGen/config.properties"
CFG_CATS = [("zones", "Zone islands"), ("island", "Island (fixed)")]
CFG_ROWS = [  # (key, label, cat, type, default, min, max, opts, unit, flags, help, bind)
    ("part.zones", "Zone islands", "zones", "bool", "true", "", "", "", "", "live,part,danger",
     "Off = /zone refuses. Players already on an island stay; /hub and /zone leave still work.", "field:WgCfg.ON"),
    ("landing.point", "Zone 1 landing point", "zones", "text", LANDING_TEXT, "", "60", "", "", "live",
     "x y z yaw: where /zone 1 lands you and void deaths respawn. Must be on the island's ground.",
     "field:WgCfg.LANDING;check=WgHooks.checkLanding;after=WgHooks.afterLanding"),
    ("landing.here", "Landing = where I stand", "zones", "action", "", "", "", "Set here", "", "live",
     "Stand on the island's ground (skywynn_z1) and click: the landing point moves to your spot.", "action:WgHooks.landingHere"),
    ("info.size", "Island size", "island", "text", SIZE_TEXT, "", "", "", "", "ro",
     "Fixed in the World Gen V2 files in the jar - a new size needs a new world.", "custom:WgHooks"),
    ("info.world", "World name", "island", "text", G["world"], "", "", "", "", "ro",
     "The Zone 1 island world (universe/worlds/%s), made on the first /zone 1." % G["world"], "custom:WgHooks"),
    ("info.rings", "Rings (blocks from centre)", "island", "text", RING_TEXT, "", "", "", "", "ro",
     "Ring borders wobble by about 16 blocks (warped). Envs: Plains / Forests / Azure.", "custom:WgHooks"),
]
_bad = ["%s help %d" % (r[0], len(r[10])) for r in CFG_ROWS if len(r[10]) > 100] + \
       ["%s label %d" % (r[0], len(r[1])) for r in CFG_ROWS if len(r[1]) > 40]
assert not _bad, "config row text too long: %s" % _bad
_dp = CFG.parse_props(CFG_TEXT)
for _r in CFG_ROWS:
    if _r[3] in ("bool", "text") and _r[9] != "ro":
        assert _dp.get(_r[0]) == _r[4], "default file and row default differ: " + _r[0]
kit = CFG.emit(pool, PKG, MOD=MOD, TITLE="World Gen", VERSION=VERSION, NODE=NODE, CATS=CFG_CATS, ROWS=CFG_ROWS,
               FILES=[CFG_FILE], NOTE="Chat (admins, test version): /zone, /zone 1, info, leave, setlanding, reload.",
               RELOAD="WgCfg.reloadAll", KEEP=10, DEFAULTS={"config.properties": CFG_TEXT})

# ---------------------------------------------------------------- WgCmds part 2: the command bodies (world thread: AbstractPlayerCommand)
M(cmds, r"""
public static String cfgSet(String key, String value, @PR@ pr) {
  if (pr == null) return "-[Zone] Could not tell who did this - nothing was changed.";
  String r = @PKG@.CfgFn.cmdSet(key, value, pr.getUuid(), pr.getUsername());
  if (r == null) return "-[Zone] Nothing was changed.";
  return r.startsWith("-") || r.startsWith("+") || r.startsWith("=") ? r : "=[Zone] " + r;
}""")
M(cmds, r"""
public static String reload(java.util.UUID who, String name) {
  if (who == null) return "-[Zone] Could not tell who sent this command - nothing was changed.";
  Object o = null;
  try { o = new @PKG@.CfgFn().apply(new Object[] { "reload", who, name, "command" }); } catch (Throwable t) { o = null; }
  if (!(o instanceof Object[]) || ((Object[]) o).length < 3) return "-[Zone] The settings could not be re-read - see the server log.";
  Object[] r = (Object[]) o;
  if ("ok".equals(r[0])) return "+[Zone] config.properties: " + r[2];
  return "-[Zone] " + r[2];
}""")
M(cmds, r"""
public static String statusOf(int zi) {
  String name = @PKG@.WgZones.WORLDS[zi];
  try {
    @UNI@ uni = @UNI@.get();
    @WLD@ w = uni.getWorld(name);
    if (w != null) return @PKG@.WgZones.isIsland(zi, w) ? "open (world '" + name + "' loaded)" : "a world named '" + name + "' is loaded but it is NOT the island (see /zone " + @PKG@.WgZones.IDS[zi] + ")";
    if (@PKG@.WgOpen.loadingFor(name) != null) return "loading...";
    if (uni.isWorldLoadable(name)) return "saved, not loaded (the next trip loads it)";
    if (@PKG@.WgOpen.folderExists(name)) return "BROKEN folder (see /zone " + @PKG@.WgZones.IDS[zi] + ")";
  } catch (Throwable t) { return "unknown (" + t + ")"; }
  return "not created yet (the first /zone " + @PKG@.WgZones.IDS[zi] + " generates it)";
}""")
M(cmds, r"""
public static String[] listLines() {
  java.util.ArrayList l = new java.util.ArrayList();
  l.add("=[Zone] SkyWynn zone islands - TEST VERSION, admins only" + (@PKG@.WgCfg.ON ? "" : " - SWITCHED OFF in Server Setup") + ":");
  for (int i = 0; i < @PKG@.WgZones.IDS.length; i++) {
    String c = @PKG@.WgStore.createdText(@PKG@.WgZones.WORLDS[i]);
    l.add("=  /zone " + @PKG@.WgZones.IDS[i] + "  " + @PKG@.WgZones.label(i) + " (" + @PKG@.WgZones.SIZE_TEXT + "): " + statusOf(i) + (c == null ? "" : ", made " + c));
  }
  l.add("=  /zone info - where you stand  |  /zone leave - back where you came from (/hub works too)  |  /zone setlanding  |  /zone reload");
  String[] out = new String[l.size()];
  for (int i = 0; i < out.length; i++) out[i] = (String) l.get(i);
  return out;
}""")
M(cmds, r"""
public static String[] infoLines(@ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  int zi = @PKG@.WgZones.islandIndex(world);
  int wi = world == null ? -1 : @PKG@.WgZones.worldIndex(world.getName());
  if (zi < 0 && wi >= 0) return new String[] { "-[Zone] This world is named '" + world.getName() + "' but it is not the zone island (its generator is not " + @PKG@.WgZones.STRUCTURES[wi] + "). /zone leave or /hub takes you out; /zone " + @PKG@.WgZones.IDS[wi] + " says how to fix it." };
  if (zi < 0) return new String[] { "=[Zone] You are not on a zone island (world '" + (world == null ? "?" : world.getName()) + "'). /zone lists them." };
  @TRF@ t = @PKG@.WgOpen.here(store, ref);
  String where = "?";
  String ring = "?";
  if (t != null && t.getPosition() != null) {
    @VEC@ p = t.getPosition();
    where = (int) Math.floor(p.x) + " " + (int) Math.floor(p.y) + " " + (int) Math.floor(p.z) + ", " + (int) Math.round(@PKG@.WgZones.dist(p.x, p.z)) + " blocks from the centre";
    ring = @PKG@.WgZones.ringAt(zi, p.x, p.z);
  }
  return new String[] {
    "=[Zone] " + @PKG@.WgZones.label(zi) + " (world '" + world.getName() + "'): you are at " + where + " - " + ring + ".",
    "=  Rings: " + @PKG@.WgZones.RING_TEXT + " (borders wobble about 16 blocks). Landing point: " + @PKG@.WgCfg.landingText(@PKG@.WgCfg.landing(zi)) + "."
  };
}""")
M(cmds, r"""
public static void goCmd(@ST@ store, @REF@ ref, @PR@ pr, @WLD@ world, String arg) {
  int zi = @PKG@.WgZones.index(arg);
  if (zi < 0) { tell(pr, "-[Zone] There is no zone '" + arg + "' yet - zones: 1 (the Zone 1 test island). /zone lists them."); return; }
  @PKG@.WgOpen.go(store, ref, pr, world, zi);
}""")

# ---------------------------------------------------------------- WgHereTask: the landing point = where an admin stands (world thread)
here.addInterface(pool.get("java.lang.Runnable"))
F(here, "public @PR@ pr;")
F(here, "public String worldName;")
C(here, "public WgHereTask(@PR@ p, String wn) { this.pr = p; this.worldName = wn; }")
M(here, r"""
public static String setHere(@ST@ st, @REF@ ref, @PR@ pr, @WLD@ w) {
  int zi = @PKG@.WgZones.islandIndex(w);
  if (zi < 0) return "-[Zone] Stand on the zone island first (/zone 1), then set the landing point.";
  @TRF@ t = @PKG@.WgOpen.here(st, ref);
  if (t == null || t.getPosition() == null) return "-[Zone] Could not read your position.";
  @VEC@ p = t.getPosition();
  double y = Math.floor(p.y) + 1.0;
  @R3F@ r = t.getRotation();
  double yaw = r == null ? 0.0 : Math.toDegrees((double) r.y);
  yaw = Math.round(Math.IEEEremainder(yaw, 360.0));
  if (yaw <= -180.0) yaw += 360.0;
  double[] np = new double[] { Math.floor(p.x) + 0.5, y, Math.floor(p.z) + 0.5, yaw };
  String why = @PKG@.WgCfg.landingCheck(np, zi);
  if (why != null) return "-[Zone] " + why;
  return @PKG@.WgCmds.cfgSet("landing.point", @PKG@.WgCfg.landingText(np), pr);
}""")
M(here, r"""
public void run() {
  try {
    if (this.pr == null || !this.pr.isValid()) return;
    java.util.UUID wu = this.pr.getWorldUuid();
    @WLD@ w = wu == null ? null : @UNI@.get().getWorld(wu);
    if (w == null || !w.getName().equals(this.worldName)) { @PKG@.WgCmds.tell(this.pr, "-[Zone] You changed worlds before the landing point was set - nothing changed."); return; }
    @REF@ ref = this.pr.getReference();
    if (ref == null) return;
    @ST@ st = ref.getStore();
    if (st == null) return;
    @PKG@.WgCmds.tell(this.pr, setHere(st, ref, this.pr, w));
  } catch (Throwable t) {
    @PKG@.WgLog.warn("landing point action failed: " + t);
    @PKG@.WgCmds.tell(this.pr, "-[Zone] Could not set the landing point - the server log has the details.");
  }
}""")

# ---------------------------------------------------------------- WgHooks: the kit's hooks (check / after / custom ro rows / action)
M(hooks, r"""
public static String checkLanding(String key, String value) {
  return @PKG@.WgCfg.landingCheck(@PKG@.WgCfg.parseLanding(value), 0);
}""")
M(hooks, r"""
public static void afterLanding(String key) {
  @PKG@.WgCfg.syncLanding();
}""")
M(hooks, r"""
public static String customGet(String key) {
  if ("info.size".equals(key)) return @PKG@.WgZones.SIZE_TEXT;
  if ("info.world".equals(key)) return @PKG@.WgZones.WORLDS[0];
  if ("info.rings".equals(key)) return @PKG@.WgZones.RING_TEXT;
  return null;
}""")
M(hooks, r"""
public static Object[] customSet(String key, String value) {
  return new Object[] { "bad", null, "This is fixed in the island files in the jar - a new size or ring layout needs a new world (a later SkyyWorldGen)." };
}""")
M(hooks, r"""
public static Object[] landingHere(java.util.UUID who, String name) {
  try {
    @PR@ pr = who == null ? null : @UNI@.get().getPlayer(who);
    if (pr == null || !pr.isValid()) return new Object[] { "bad", null, "You must be in game, standing on the island, for this." };
    java.util.UUID wu = pr.getWorldUuid();
    @WLD@ w = wu == null ? null : @UNI@.get().getWorld(wu);
    if (w == null || @PKG@.WgZones.islandIndex(w) < 0) return new Object[] { "bad", null, "Stand on the zone island first (/zone 1)." };
    w.execute(new @PKG@.WgHereTask(pr, w.getName()));
    return new Object[] { "ok", "", "Working on it - the answer comes in chat." };
  } catch (Throwable t) {
    @PKG@.WgLog.warn("landing action failed: " + t);
    return new Object[] { "error", null, "internal error - see the server log" };
  }
}""")

# ================================================================= commands (every one admin-only in this test version)
EXEC = "protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world)"
CMDS = []


def cmd(clsname, name, desc, body, subs=()):
    """One admin-only AbstractPlayerCommand (a named sub-command of /zone, or /zone itself)."""
    c = pool.makeClass(PKG + "." + clsname, pool.get(T["APC"]))
    lines = ['super("%s", "%s");' % (name, desc), "@ADMIN@"]
    for s in subs:
        lines.append("addSubCommand(new @PKG@.%s());" % s)
    C(c, "public %s() {\n  %s\n}" % (clsname, "\n  ".join(lines)))
    M(c, EXEC + " {\n  try {\n    " + body + "\n  } catch (Throwable t) {\n"
      "    @PKG@.WgLog.warn(\"/zone " + name + " failed: \" + t);\n"
      "    @PKG@.WgCmds.tell(pr, \"-[Zone] Something went wrong - the server log has the details.\");\n  }\n}")
    CMDS.append(c)
    return c


X = "@PKG@.WgCmds."
cmd("ZoneLeaveCmd", "leave", "Leave the zone island: back to where you were when you went there", "@PKG@.WgOpen.leave(store, ref, pr, world);")
cmd("ZoneInfoCmd", "info", "Where you stand on the zone island: ring, distance from the centre, landing point",
    X + "tellAll(pr, " + X + "infoLines(store, ref, pr, world));")
cmd("ZoneLandingCmd", "setlanding", "Set the zone island's landing point to where you stand (on the island)",
    X + "tell(pr, @PKG@.WgHereTask.setHere(store, ref, pr, world));")
cmd("ZoneReloadCmd", "reload", "Re-read SkyyWorldGen's config.properties after a hand edit", X + "tell(pr, " + X + "reload(pr.getUuid(), pr.getUsername()));")
# /zone <n>: a usage variant (description-only constructor) with the required zone argument - the engine picks it by argument count
gocmd = pool.makeClass(PKG + ".ZoneGoCmd", pool.get(T["APC"]))
F(gocmd, "public @RA@ zoneArg;")
C(gocmd, r"""
public ZoneGoCmd() {
  super("Go to a zone island: /zone 1 = the Zone 1 test island");
  this.zoneArg = withRequiredArg("zone", "Zone number (1)", @ATY@.STRING);
  @ADMIN@
}""")
M(gocmd, EXEC + r""" {
  try {
    @PKG@.WgCmds.goCmd(store, ref, pr, world, String.valueOf(ctx.get(this.zoneArg)));
  } catch (Throwable t) {
    @PKG@.WgLog.warn("/zone <n> failed: " + t);
    @PKG@.WgCmds.tell(pr, "-[Zone] Something went wrong - the server log has the details.");
  }
}""")
CMDS.append(gocmd)
zcmd = pool.makeClass(PKG + ".ZoneCmd", pool.get(T["APC"]))
C(zcmd, r"""
public ZoneCmd() {
  super("zone", "SkyWynn zone islands (test version, admins): /zone 1 goes to the Zone 1 island");
  requirePermission("@NODE@");
  setPermissionGroups(new String[0]);
  addUsageVariant(new @PKG@.ZoneGoCmd());
  addSubCommand(new @PKG@.ZoneLeaveCmd());
  addSubCommand(new @PKG@.ZoneInfoCmd());
  addSubCommand(new @PKG@.ZoneLandingCmd());
  addSubCommand(new @PKG@.ZoneReloadCmd());
}""")
M(zcmd, EXEC + r""" {
  try {
    @PKG@.WgCmds.tellAll(pr, @PKG@.WgCmds.listLines());
  } catch (Throwable t) {
    @PKG@.WgLog.warn("/zone failed: " + t);
    @PKG@.WgCmds.tell(pr, "-[Zone] Something went wrong - the server log has the details.");
  }
}""")
CMDS.append(zcmd)

# ================================================================= plugin
C(pl, "public SkyyWorldGenPlugin(@JPI@ init) { super(init); }")
M(pl, r"""
public void setup() {
  @PKG@.WgLog.LOG = getLogger();
  java.nio.file.Path dir = getDataDirectory().resolveSibling("Skyy_SkyyWorldGen");
  @PKG@.WgCfg.DIR = dir;
  @PKG@.WgCfg.FILE = dir.resolve("config.properties");
  @PKG@.WgStore.FILE = dir.resolve("worlds.properties");
  @PKG@.WgCfg.load();
  @PKG@.WgStore.read();
  getCommandRegistry().registerCommand(new @PKG@.ZoneCmd());
  getEventRegistry().registerGlobal(@PRE@.class, new @PKG@.WgReady());
  String made = @PKG@.WgStore.createdText(@PKG@.WgZones.WORLDS[0]);
  @PKG@.WgLog.info("@VERSION@ ready (@KITID@) - TEST VERSION: /zone, /zone 1, /zone info | leave | setlanding | reload for admins only (@NODE@); " + @PKG@.WgCfg.LOADED + "; Zone 1 = world " + @PKG@.WgZones.WORLDS[0] + " (" + (made == null ? "not created yet" : "made " + made) + "), template " + @PKG@.WgZones.TEMPLATES[0] + " " + (@PKG@.WgCheck.templateOk(0) ? "found" : "NOT FOUND - check Server/Instances in the jar") + ", structure " + @PKG@.WgZones.STRUCTURES[0] + " (checked at the first /zone); settings in Server Setup > World Gen; data in " + dir);
  @PKG@.CfgPub.start(getDataDirectory().getParent(), getLogger());
}""")
M(pl, r"""
protected void shutdown() {
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { }
  super.shutdown();
}""")

for c in ALL + CMDS + [pl]:
    c.writeFile(OUT)
kit.write(OUT)
CLASSES = ALL + CMDS + [pl]
print("classes written:", len(CLASSES) + len(kit.classes), "(%d kit)" % len(kit.classes))

# ================================================================= ACCESS AUDIT (SkyyUiProbe 0.3.1 lesson): what the JVM would refuse at RUN
# time with IllegalAccessError - javassist compiles a call to a protected / package-private member from any class and -Xverify:all does
# not catch it (member access is checked when the instruction first runs). Every class / member reference in the final class bytes is
# resolved here with the JVM's rules; the harness checks the same references again with MethodHandles.Lookup.
import jpype
JMod, JConstPool = J["Modifier"], jpype.JClass("javassist.bytecode.ConstPool")
JClassFile, JDataIn, JByteIn = (jpype.JClass("javassist.bytecode.ClassFile"), jpype.JClass("java.io.DataInputStream"),
                                jpype.JClass("java.io.ByteArrayInputStream"))
AUDIT_OPS = {0xb2: "getstatic", 0xb3: "putstatic", 0xb4: "getfield", 0xb5: "putfield", 0xb6: "invokevirtual", 0xb7: "invokespecial",
             0xb8: "invokestatic", 0xb9: "invokeinterface", 0xba: "invokedynamic", 0xbb: "new", 0xbd: "anewarray", 0xc0: "checkcast",
             0xc1: "instanceof", 0xc5: "multianewarray", 0x12: "ldc", 0x13: "ldc_w"}


def class_file(data):
    return JClassFile(JDataIn(JByteIn(data)))


def audit_pkg(name):
    return name.rsplit(".", 1)[0] if "." in name else ""


def audit_elem(name):
    n = name.replace("/", ".").lstrip("[")
    if n.startswith("L") and n.endswith(";"):
        return n[1:-1]
    return None if len(n) == 1 and name.startswith("[") else n


def access_audit(items):
    refused, used, seen = [], set(), 0
    for D, cf in items:
        dn = str(D.getName())
        for mi in cf.getMethods():
            ca = mi.getCodeAttribute()
            if ca is None:
                continue
            cp, it = mi.getConstPool(), ca.iterator()
            while it.hasNext():
                pos = it.next()
                op = it.byteAt(pos)
                if op not in AUDIT_OPS:
                    continue
                where = "%s.%s @%d %s" % (dn.rsplit(".", 1)[-1], mi.getName(), pos, AUDIT_OPS[op])
                if op == 0xba:
                    refused.append(where + ": invokedynamic (javassist never writes one)")
                    continue
                idx = it.byteAt(pos + 1) if op == 0x12 else it.u16bitAt(pos + 1)
                tag = cp.getTag(idx)
                if op in (0x12, 0x13) and tag != JConstPool.CONST_Class:
                    continue
                if op in (0x12, 0x13, 0xbb, 0xbd, 0xc0, 0xc1, 0xc5):
                    cname, member = str(cp.getClassInfo(idx)), None
                elif op in (0xb2, 0xb3, 0xb4, 0xb5):
                    cname, member = str(cp.getFieldrefClassName(idx)), ("field", str(cp.getFieldrefName(idx)), str(cp.getFieldrefType(idx)))
                elif tag == JConstPool.CONST_InterfaceMethodref:
                    cname, member = str(cp.getInterfaceMethodrefClassName(idx)), ("method", str(cp.getInterfaceMethodrefName(idx)),
                                                                                  str(cp.getInterfaceMethodrefType(idx)))
                else:
                    cname, member = str(cp.getMethodrefClassName(idx)), ("method", str(cp.getMethodrefName(idx)), str(cp.getMethodrefType(idx)))
                seen += 1
                try:
                    en = audit_elem(cname)
                    if en is not None and audit_pkg(en) != audit_pkg(dn) and not JMod.isPublic(pool.get(en).getModifiers()):
                        refused.append("%s: class %s is not public - the JVM refuses it from %s (IllegalAccessError)" % (where, en, dn))
                    if member is None:
                        continue
                    kind, name, desc = member
                    Cc = pool.get("java.lang.Object" if cname.startswith("[") else cname)
                    if kind == "field":
                        x = Cc.getField(name, desc)
                    elif name == "<init>":
                        x = Cc.getConstructor(desc)
                    else:
                        x = Cc.getMethod(name, desc)
                    md, decl = x.getModifiers(), x.getDeclaringClass()
                    dcn = str(decl.getName())
                    if JMod.isPublic(md) or (audit_pkg(dcn) == audit_pkg(dn) and not JMod.isPrivate(md)):
                        continue
                    if JMod.isPrivate(md):
                        ok = dcn == dn
                    elif JMod.isProtected(md):
                        ok = bool(D.subclassOf(decl))
                    else:
                        ok = False
                    use = "%s %s.%s%s" % (JMod.toString(md), dcn, name, "" if kind == "field" else desc)
                    if ok:
                        used.add("%s.%s (from %s)" % (dcn.rsplit(".", 1)[-1], name, dn.rsplit(".", 1)[-1]))
                    else:
                        refused.append("%s: %s - the JVM refuses it from %s (IllegalAccessError)" % (where, use, dn))
                except Exception as e:
                    refused.append("%s: %s %s does not resolve: %s" % (where, cname, member, e))
    return refused, sorted(used), seen


# self-test first: a protected engine member called from a class that is not its subclass must be named
_st = pool.makeClass(PKG + ".AccessAuditSelfTest")
M(_st, "public static void bad(@JP@ p) { p.setup(); }")
_st_refused, _st_used, _st_n = access_audit([(_st, class_file(_st.toBytecode()))])
_st.detach()
assert len(_st_refused) == 1 and "setup" in _st_refused[0] and "IllegalAccessError" in _st_refused[0], \
    "access audit self-test: a protected JavaPlugin.setup() call from a non-subclass must be refused: %s" % _st_refused
_items = []
for _cn in [str(c.getName()) for c in CLASSES] + [str(c.getName()) for c in kit.classes]:
    with open(os.path.join(OUT, *_cn.split(".")) + ".class", "rb") as _f:
        _items.append((pool.get(_cn), class_file(_f.read())))
AUDIT_REFUSED, AUDIT_USED, AUDIT_N = access_audit(_items)
if AUDIT_REFUSED:
    raise SystemExit("ACCESS AUDIT: %d reference(s) the JVM would refuse at run time (IllegalAccessError):\n  %s"
                     % (len(AUDIT_REFUSED), "\n  ".join(AUDIT_REFUSED)))
print("access audit: %d class / member references in %d classes, 0 the JVM would refuse; non-public engine members used: %s"
      % (AUDIT_N, len(_items), ", ".join(AUDIT_USED) or "none"))

jar = os.path.join(HERE, "SkyyWorldGen-%s.jar" % VERSION)
man = B.manifest(MOD, VERSION, "SkyWynn zone islands (World Gen V2), TEST VERSION: the Zone 1 test island - a floating island (radius 384) with "
                 "a meadow rim, a birch forest and an azure core over the void, world skywynn_z1, generated once and kept. /zone 1 (admins "
                 "only for now), /zone leave, /zone info; /hub (SkyyIslands) works from it. Settings in game (Server Setup > World Gen). "
                 "Zero dependencies.", PKG + ".SkyyWorldGenPlugin")
man["IncludesAssetPack"] = True
B.assemble(jar, man, OUT, extra_files=ASSETS)
with zipfile.ZipFile(jar) as _jz:
    _bad = [n for n in _jz.namelist() if n.lower().endswith(".ui")]
    if _bad:
        raise SystemExit("SkyyWorldGen jar must not ship .ui files: %s" % _bad)
    for _p, _t in ASSETS.items():
        assert _jz.read(_p).decode("ascii") == _t, "asset in the jar differs: " + _p
