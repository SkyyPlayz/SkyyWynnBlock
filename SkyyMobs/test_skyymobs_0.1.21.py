"""Harness for SkyyMobs 0.1.21 (round spawn1: more mob spawns - A1 spawn tables in the jar, A2 density per zone, /mobs spawns;
tools/mobs_0_1_21_patch.py).
Build first:
    python tools/mobs_0_1_21_patch.py && python SkyyMobs/build_skyymobs_0.1.21.py
    python SkyyMobs/test_skyymobs_0.1.21.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  S     static   the patch re-runs to identical bytes (--out), line endings kept, +2 makeClass (+ 1 command class through cmd()), no system /
                 command; jar: only the 3 new classes + the generated spawn files added, the only other changed file is the manifest
                 (IncludesAssetPack true); the spawn files: every Wander list = vanilla x3 (skeletons) + its camp list (x1 more, the same
                 environments / hours), a monster entry x1.5, animals / predators / critters / fish files NOT shipped or unchanged, every id a
                 vanilla role / every environment real, no NPC + environment pair in two files (vanilla + ours), no vanilla-derived file in git
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.1.20 -> 0.1.21 (EXPECT below)
  X     exec     EXECUTES MobSpawn in a bare JVM with real engine objects: the defaults (125 % each zone, the default file lines), pct()
                 clamps a live edit (0-300), want(), set() on a real EnvironmentSpawnParameters (changes once, then no-op; restore), zoneOf,
                 base / index without an asset store (-1), tick() without a SpawningPlugin (-1, nothing thrown), refresh() without a Universe
                 (false, counted), changed() never throws, envLine on a real WorldEnvironmentSpawnData with WorldNPCSpawnStat entries, lines()
                 for no spawn data / an empty WorldSpawnData / a WorldSpawnData holding an environment, text(), MobSpawnTask.run, MobCmds.spawns
                 with no store / world, the Server Setup rows (live, after=MobSpawn.changed, help <= 100).
                 FIX round (spawn1fix): Sewers not managed; tick synchronized + STOPPING (a late run after the restore does nothing);
                 the restore re-applies to the worlds; pick() = where you stand + one line per zone + your environment first + only
                 environments with NPCs + "(N more)" (real WorldEnvironmentSpawnData objects for all 4 zones); counts(); the help texts
  EX120 0.1.20's exec phase EXECUTED on this jar (the secret egg finds unchanged)
  D     live     start twice on a scratch COPY of Skyy's live NewBetaTest Skyy_SkyyMobs: config / bands / trees bytes untouched (no migration),
                 the spawn rows = their defaults (no line in the live file), start 2 the same
  AA    engine-access audit
NOT COVERED (UNVERIFIED in game): the engine loading our files over vanilla's (asset pack order - proven pattern, SkyySkills / SkyyCooking /
SkyyArmory replace vanilla item files the same way), SpawningPlugin.getWorldEnvironmentSpawnParameters on a live server, onEnvironmentChanged
re-applying to the live worlds, the 30 s task on the server scheduler, /mobs spawns inside a live world (WorldSpawnData resource), tick time.
Scratch: tools/dev/scratch/spawn1/mobs (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, zipfile, json, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.1.21"
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "spawn1", "mobs")]
import skyybuild as B
import harness_kit as HK
import serverjar as SJ

_run0 = HK.run
HK.run = lambda *a, **k: None          # import 0.1.20's harness for its exec phase without running it
_s = importlib.util.spec_from_file_location("test_skyymobs_0_1_20", os.path.join(HERE, "test_skyymobs_0.1.20.py"))
T120 = importlib.util.module_from_spec(_s)
_s.loader.exec_module(T120)
HK.run = _run0

GEN = os.path.join(HERE, "build_skyymobs_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyymobs_0.1.20.py")
PATCH = os.path.join(ROOT, "tools", "mobs_0_1_21_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMobs-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMobs-0.1.20.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.mobs."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyMobs")
ADDED = ["MobSpawn", "MobSpawnTask", "MobsSpawnsCmd"]
SD = "Server/NPC/Spawn/World/"
EXPECT = {
    "MobCfg": ["+f SPAWN_Z1", "+f SPAWN_Z2", "+f SPAWN_Z3", "+f SPAWN_Z4", "~<clinit>", "~m apply", "~m load", "~m reloadAll", "~m useDefaults"],
    "MobCmds": ["+m spawns"],
    "MobsCmd": ["~c "],          # the constructor: + addSubCommand(new MobsSpawnsCmd())
    "SkyyMobsPlugin": ["~m setup", "~m shutdown"],
    "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "CfgFile": ["~<clinit>"],          # the kit: the 4 new rows + the default file text
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
T120.PKG = PKG


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyMobs 0.1.21 - build script') and g.count('VERSION = "0.1.21"') == 1, "S header + VERSION")
    K.eq((g.count("registerSystem(") - o.count("registerSystem("), g.count("registerCommand(") - o.count("registerCommand("),
          g.count("makeClass(") - o.count("makeClass(")), (0, 0, 2), "S no system, no command, +2 makeClass (the 3rd class = cmd() MobsSpawnsCmd)")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    newf = sorted(nb - na)
    spawn = [n for n in newf if n.startswith(SD)]
    K.eq((sorted(n for n in newf if not n.startswith(SD)), sorted(na - nb)), (sorted("com/skyy/mobs/%s.class" % c for c in ADDED), []),
         "S only the 3 new classes + spawn files added, nothing removed")
    K.eq(sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n)), ["manifest.json"], "S the only other changed file is the manifest")
    man = json.loads(zb.read("manifest.json"))
    K.check(man.get("IncludesAssetPack") is True and man.get("Version") == VERSION, "S manifest: IncludesAssetPack true (%s)" % man.get("IncludesAssetPack"))
    K.check(len(spawn) == 45, "S 45 spawn files in the jar (%d)" % len(spawn))
    K.check("public static synchronized int tick(boolean restore)" in g and 'if (STOPPING && !restore)' in g and "  if (changed > 0) refresh();" in g,
            "S fix: tick synchronized, STOPPING skips non-restore runs, the restore refreshes the worlds too")
    sd = g.index("@PKG@.MobSpawn.STOPPING = true;")
    K.check(sd < g.index("@PKG@.MobSpawn.tick(true);", sd) and g.count("@PKG@.MobSpawn.STOPPING = false;") == 1,
            "S fix: shutdown sets STOPPING before cancel + restore; setup clears it")
    K.check('"Sewers"))' in g and "shown < 14" not in g, "S fix: Sewers left out of the managed list; no 14-line cap")
    K.check("animals / critters / fish x" in g and "SPAWN_ANIMALS" in g, "S fix: the build prints the animal rate vs vanilla per environment")
    # the files against vanilla (the cached Assets.zip, read only)
    az = zipfile.ZipFile(SJ.assets_zip())
    an = set(az.namelist())
    V = dict((n, json.loads(az.read(n).decode("utf-8-sig"))) for n in an if n.startswith(SD) and n.endswith(".json"))
    J = dict((n, json.loads(zb.read(n).decode("utf-8"))) for n in spawn)
    roles = set(n.rsplit("/", 1)[1][:-5] for n in an if n.startswith("Server/NPC/Roles/") and n.endswith(".json"))
    envs = set(n.rsplit("/", 1)[1][:-5] for n in an if n.startswith("Server/Environments/") and n.endswith(".json"))
    for z in ("Zone1", "Zone2", "Zone3", "Zone4"):
        for t in ("Tier1", "Tier2", "Tier3"):
            w = SD + "%s/Wander_%s_%s.json" % (z, z, t)
            if w not in V:
                continue
            c = SD + "%s/SkyyMobs_Camp_%s_%s.json" % (z, z, t)
            K.check(w in J and c in J, "S %s replaced + its camp list shipped" % w.rsplit("/", 1)[1])
            if w not in J or c not in J:
                continue
            vw = sum(e["Weight"] for e in V[w]["NPCs"])
            K.eq([round(e["Weight"], 4) for e in J[w]["NPCs"]], [round(e["Weight"] * 3.0, 4) for e in V[w]["NPCs"]], "S %s: every skeleton weight x3" % w.rsplit("/", 1)[1])
            K.eq(round(sum(e["Weight"] for e in J[c]["NPCs"]), 2), round(vw, 2), "S %s: the camp types = x1 more (%.2f)" % (c.rsplit("/", 1)[1], vw))
            K.check(J[c]["Environments"] == V[w]["Environments"] and J[c]["DayTimeRange"] == V[w].get("DayTimeRange", [0, 24]),
                    "S %s: same environments + hours" % c.rsplit("/", 1)[1])
            K.check(all(e["Id"].startswith("Skeleton_") and "Gunner" not in e["Id"] and e["Id"] in roles for e in J[c]["NPCs"]),
                    "S %s: vanilla skeleton roles, no Gunner" % c.rsplit("/", 1)[1])
    vp = SD + "Zone4/Spawns_Zone4_Volcanoes_Predator.json"          # fix 2: "No guns" - the vanilla Burnt Gunner keeps its weight
    if vp in V and vp in J:
        jw = dict((e["Id"], e["Weight"]) for e in J[vp]["NPCs"])
        vw_ = dict((e["Id"], e["Weight"]) for e in V[vp]["NPCs"])
        K.eq(jw.get("Skeleton_Burnt_Gunner"), vw_.get("Skeleton_Burnt_Gunner"), "S fix 2: Skeleton_Burnt_Gunner at its vanilla weight")
        K.check(all(jw[k] == round(vw_[k] * 3.0, 4) for k in vw_ if k.startswith("Skeleton_") and "Gunner" not in k),
                "S fix 2: the other skeletons of Volcanoes_Predator still x3")
    K.check(not any("Gunner" in e["Id"] and e["Weight"] != dict((x["Id"], x["Weight"]) for x in V.get(n, {"NPCs": []})["NPCs"]).get(e["Id"])
                    for n, d_ in J.items() for e in d_["NPCs"]), "S fix 2: no gun user gains weight in any shipped file")
    g = SD + "Zone1/Spawns_Zone1_Caves_Goblins.json"
    gw = dict((e["Id"], e["Weight"]) for e in J[g]["NPCs"])
    gv = dict((e["Id"], e["Weight"]) for e in V[g]["NPCs"])
    K.eq((gw["Goblin_Scrapper"], gw["Rat"], gw["Bat"]), (gv["Goblin_Scrapper"] * 1.5, gv["Rat"], gv["Bat"]), "S goblins x1.5, rats / bats unchanged")
    for n in ("Zone1/Spawns_Zone1_Forests_Predator.json", "Zone1/Spawns_Zone1_Plains_Animal.json", "Zone1/Spawns_Zone1_Fish_Tier3.json",
              "Zone1/Spawns_Zone1_Forests_Critter.json"):
        K.check(SD + n not in J, "S %s (animals / predators / fish / critters) not shipped = vanilla" % n)
    for n, d_ in J.items():
        K.check(n in V or "/SkyyMobs_Camp_" in n, "S %s replaces a vanilla file or is a camp list" % n)
        if n in V:
            K.eq([e["Id"] for e in d_["NPCs"]], [e["Id"] for e in V[n]["NPCs"]], "S %s: same NPCs as vanilla" % n.rsplit("/", 1)[1])
            K.eq(dict((k, v) for k, v in d_.items() if k != "NPCs"), dict((k, v) for k, v in V[n].items() if k != "NPCs"), "S %s: same fields" % n.rsplit("/", 1)[1])
        K.check(all(e in envs for e in d_["Environments"]) and all(x["Id"] in roles for x in d_["NPCs"]), "S %s: real environments + roles" % n.rsplit("/", 1)[1])
    allf = dict(V)
    allf.update(J)
    pairs = {}
    for n, d_ in allf.items():
        for e in d_.get("Environments", []):
            for x in d_.get("NPCs", []):
                pairs.setdefault((x["Id"], e), []).append(n)
    K.eq([p for p, f in pairs.items() if len(f) > 1], [], "S no NPC + environment pair in two files (the engine would drop the second)")
    tracked = subprocess.run(["git", "-C", ROOT, "ls-files", "--", "*Spawn/World*"], capture_output=True, text=True).stdout.strip()
    K.eq(tracked, "", "S no vanilla-derived spawn file is tracked in git")
    K.save()


def run_exec(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    C, S = JClass(PKG + "MobCfg"), JClass(PKG + "MobSpawn")
    ESP = JClass("com.hypixel.hytale.server.spawning.world.manager.EnvironmentSpawnParameters")
    WESD = JClass("com.hypixel.hytale.server.spawning.world.WorldEnvironmentSpawnData")
    WSD = JClass("com.hypixel.hytale.server.spawning.world.component.WorldSpawnData")
    WNSS = JClass("com.hypixel.hytale.server.spawning.world.WorldNPCSpawnStat")
    C.useDefaults()
    d = str(C.DEF_CFG)
    K.check(all("\nspawn.density.z%d=125\n" % z in d for z in (1, 2, 3, 4)), "X the default file carries spawn.density.z1..z4=125")
    K.eq([int(S.pct(z)) for z in (0, 1, 2, 3, 4, 5)], [100, 125, 125, 125, 125, 100], "X pct: Zones 1-4 = 125, anything else 100 (vanilla)")
    C.SPAWN_Z1, C.SPAWN_Z2 = 350, -5
    K.eq((int(S.pct(1)), int(S.pct(2))), (300, 0), "X a live edit is clamped to 0-300")
    C.useDefaults()
    K.eq([round(float(S.want(b, p)), 6) for b, p in ((0.5, 125), (0.9, 100), (0.3, 0), (-1.0, 125), (float("nan"), 125))], [0.625, 0.9, 0.0, 0.0, 0.0],
         "X want = vanilla x %, bad base = 0")
    p = ESP(0.5)
    K.eq((bool(S.set(p, 0.625)), round(float(p.getSpawnDensity()), 6), bool(S.set(p, 0.625)), bool(S.set(None, 1.0)), bool(S.set(p, -1.0))),
         (True, 0.625, False, False, False), "X set(): a real EnvironmentSpawnParameters changes once, then no-op; null / negative refused")
    K.check(bool(S.set(p, 0.5)) and abs(float(p.getSpawnDensity()) - 0.5) < 1e-9, "X set back to vanilla (the restore path)")
    envs = [str(e) for e in S.ENVS]
    K.check(len(envs) == len(S.ZONES) and "Env_Zone1_Plains" in envs and not [e for e in envs if "Caves" in e], "X ENVS: %d surface environments, no caves" % len(envs))
    K.check("Env_Zone4_Sewers" not in envs and len(envs) == 51 and "Env_Zone4_Wastes" in envs, "X fix: Env_Zone4_Sewers not managed (%d environments)" % len(envs))
    K.eq([int(S.zoneOf(e)) for e in ("Env_Zone1_Plains", "Env_Zone2_Savanna", "Env_Zone3_Tundra", "Env_Zone4_Wastes", "Env_Zone1_Caves", "Env_Default_Void", None)],
         [1, 2, 3, 4, 0, 0, 0], "X zoneOf: the zone of a managed environment, 0 = not managed")
    K.eq((float(S.base(-1)), int(S.index(None))), (-1.0, -1), "X base / index refuse bad input")
    K.eq(int(S.index("Env_Zone1_Plains")), -1, "X no asset store in a bare JVM = index -1 (never throws)")
    t0 = int(S.TICKS)
    K.eq((int(S.tick(False)), int(S.FOUND), str(S.LAST), int(S.TICKS)), (-1, -1, "the spawner is not ready yet", t0 + 1), "X tick() without a SpawningPlugin = -1, nothing thrown")
    K.eq(int(S.tick(True)), -1, "X tick(restore) without a SpawningPlugin = -1")
    Mod = JClass("java.lang.reflect.Modifier")
    tm = S.class_.getMethod("tick", JClass("java.lang.Boolean").TYPE)
    K.check(bool(Mod.isSynchronized(tm.getModifiers())) and bool(Mod.isStatic(tm.getModifiers())), "X fix: tick is static synchronized (task vs shutdown)")
    S.STOPPING = True
    t1 = int(S.TICKS)
    K.eq((int(S.tick(False)), str(S.LAST), int(S.TICKS)), (0, "stopped (vanilla densities back)", t1 + 1), "X fix: STOPPING - a late 30 s run does nothing")
    JClass(PKG + "MobSpawnTask")().run()
    K.eq(str(S.LAST), "stopped (vanilla densities back)", "X fix: STOPPING - MobSpawnTask.run does nothing either")
    K.eq(int(S.tick(True)), -1, "X fix: STOPPING - the restore still runs (no spawner here = -1)")
    S.STOPPING = False
    f0 = int(S.FAILS)
    K.check(not bool(S.refresh()) and int(S.FAILS) == f0 + 1, "X refresh() without a Universe = false, counted (logged once)")
    S.changed("spawn.density.z1")
    K.check(True, "X changed() never throws")
    w = WESD(3, 0.625)
    ctor = WNSS.class_.getDeclaredConstructor(JClass("java.lang.Integer").TYPE)          # the engine's own count-only constructor (not public)
    ctor.setAccessible(True)
    OA, JI = JClass("java.lang.Object[]"), JClass("java.lang.Integer")
    s1, s2 = ctor.newInstance(OA([JI(11)])), ctor.newInstance(OA([JI(12)]))
    s1.adjustActual(2)
    s2.adjustActual(3)
    s1.setExpected(1.5)
    s2.setExpected(2.25)
    w.getNpcStatMap().put(JI(11), s1)          # the (Object, Object) put: the int overload is ambiguous from Python
    w.getNpcStatMap().put(JI(12), s2)
    ln = str(S.envLine("Env_Zone1_Plains", 0.625, 0.5, w))
    K.check(ln.startswith("=  Env_Zone1_Plains: density 0.63 (vanilla 0.5), NPCs 0 / 0") and ln.endswith("skeletons 0 / 0"),
            "X envLine on a real WorldEnvironmentSpawnData + stats (no NPCPlugin = names unknown, not counted): %s" % ln)
    from jpype import JImplements, JOverride
    NAMES = {11: "Skeleton_Fighter", 12: "Bunny"}

    @JImplements("java.util.function.Function")
    class Names(object):
        @JOverride
        def apply(self, i):
            return NAMES.get(int(i))
    S.NAME_API = Names()
    ln2 = str(S.envLine("Env_Zone1_Plains", 0.625, 0.5, w))
    K.check(ln2.endswith("skeletons 2 / 1.5"), "X envLine counts the Skeleton_* stats only (2 / 1.5, the Bunny left out): %s" % ln2)
    S.NAME_API = None
    ln0 = str(S.envLine("Env_Zone1_Plains", -1.0, -1.0, None))
    K.check("NPCs 0 / 0" in ln0, "X envLine without data: %s" % ln0)
    S.NAME_API = Names()
    K.eq([round(float(x), 4) for x in S.counts(w)], [0.0, 0.0, 2.0, 1.5], "X fix: counts() = NPCs 0 / 0, skeletons 2 / 1.5 (with names)")
    S.NAME_API = None
    K.eq([round(float(x), 4) for x in S.counts(None)], [0.0, 0.0, 0.0, 0.0], "X fix: counts(null) = zeros")
    a = [str(x) for x in S.lines(None, "w1", 500, None)]
    K.check(len(a) == 3 and "Zone 1 125 %" in a[0] and "skeletons x3" in a[1] and "no world spawns here" in a[2], "X lines(no spawn data): %s" % a)
    ws = WSD()
    b_ = [str(x) for x in S.lines(ws, "w2", 500, None)]
    K.check(len(b_) == 4 and "w2: 0 NPCs out of 0 expected (cap 500)" in b_[2] and "None of the Zone 1-4 land" in b_[3], "X lines(empty WorldSpawnData): %s" % b_)
    c_ = [str(x) for x in S.lines(ws, "w3", -1, None)]
    h_ = [str(x) for x in S.lines(ws, "w4", 500, "Env_Zone1_Caves")]
    K.check(len(h_) == 5 and "You stand in Env_Zone1_Caves (not a Zone 1-4 land environment" in h_[3], "X fix: lines() says where you stand: %s" % h_)
    # pick(): real WorldEnvironmentSpawnData for all 4 zones (alphabetical, as ENVS is), the admin in Zone 3
    ids = ["Env_Zone1", "Env_Zone1_Autumn", "Env_Zone1_Azure", "Env_Zone1_Forests", "Env_Zone1_Mountains", "Env_Zone1_Plains", "Env_Zone1_Swamps",
           "Env_Zone2_Savanna", "Env_Zone2_Scrub", "Env_Zone3_Forests", "Env_Zone3_Tundra", "Env_Zone4_Wastes"]
    WA = JClass("com.hypixel.hytale.server.spawning.world.WorldEnvironmentSpawnData[]")
    data = WA(len(ids))
    for i, e in enumerate(ids):
        d_ = WESD(i + 1, 0.5)
        if e != "Env_Zone1":          # Env_Zone1: no NPCs, none expected -> left out of the rows (still counted in the zone line)
            st = ctor.newInstance(OA([JI(11)]))
            st.adjustActual(1)
            st.setExpected(1.0)
            d_.getNpcStatMap().put(JI(11), st)
        data[i] = d_
    S.NAME_API = Names()
    DA = JClass("double[]")
    pk = [str(x) for x in S.pick(ids, data, DA([0.625] * len(ids)), DA([0.5] * len(ids)), "Env_Zone3_Tundra", 4)]
    S.NAME_API = None
    K.check(pk[0] == "=[Mobs] You stand in Env_Zone3_Tundra (Zone 3, 125 %).", "X fix: pick() line 1 = where you stand: %s" % pk[0])
    zl = [x for x in pk if x.startswith("=[Mobs] Zone ")]
    K.check(len(zl) == 4 and zl[0].startswith("=[Mobs] Zone 1 (7 environments here, 125 %): NPCs 0 / 0, skeletons 6 / 6")
            and zl[1].startswith("=[Mobs] Zone 2 (2 environments here") and zl[2].startswith("=[Mobs] Zone 3 (2 environments here, 125 %): NPCs 0 / 0, skeletons 2 / 2")
            and zl[3].startswith("=[Mobs] Zone 4 (1 environments here"), "X fix: pick() one summary line per zone, Zones 2-4 included: %s" % zl)
    el = [x for x in pk if x.startswith("=  Env_")]
    K.check(len(el) == 4 and el[0].startswith("=  Env_Zone3_Tundra:") and not [x for x in el if x.startswith("=  Env_Zone1:")],
            "X fix: pick() your environment first, empty ones skipped, at most 4 rows: %s" % el)
    K.check(pk[-1] == "=  (7 more environments with NPCs not shown)", "X fix: pick() says how many were cut: %s" % pk[-1])
    pk0 = [str(x) for x in S.pick(JClass("java.lang.String[]")(0), WA(0), DA(0), DA(0), None, 10)]
    K.eq(pk0, ["=[Mobs] None of the Zone 1-4 land environments is loaded in this world."], "X fix: pick() with nothing loaded")
    K.check("(cap none)" in c_[2], "X cap -1 = none")
    K.check("spawns Zone 1 125 %" in str(S.text()) and "45 spawn files" in str(S.text()), "X text(): %s" % S.text())
    JClass(PKG + "MobSpawnTask")().run()
    K.check(True, "X MobSpawnTask.run never throws")
    m = [str(x) for x in JClass(PKG + "MobCmds").spawns(None, None, None)]
    K.check(len(m) == 3 and "this world: no world spawns here" in m[2], "X MobCmds.spawns with no store / world: %s" % m)
    R = JClass(PKG + "CfgRows")
    keys = [str(k) for k in R.KEYS]
    for z in (1, 2, 3, 4):
        i = keys.index("spawn.density.z%d" % z)
        K.check(str(R.CATS[i]) == "spawn" and str(R.TYPES[i]) == "int" and str(R.DEFS[i]) == "125" and str(R.MAXS[i]) == "300" and "live" in str(R.FLAGS[i])
                and len(str(R.HELPS[i])) <= 100, "X row spawn.density.z%d: Spawns tab, int 125 (0-300), live" % z)
    hl = [str(R.HELPS[keys.index("spawn.density.z%d" % z)]) for z in (1, 2, 3, 4)]
    K.check("skeletons x3" in hl[0] and "sewers" in hl[1] and "sewers" in hl[2] and "mostly skeletons" in hl[3] and "animals thin out" in hl[3],
            "X fix: the help texts (sewers stay vanilla; Zone 4 is skeleton-heavy, animals thin out): %s" % hl)
    K.check(all("Above 125 may lag" in h for h in hl), "X fix 2: every Spawns row names the 125 %% perf hold: %s" % hl)
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    Cfg, S, Sp, Sc = JClass(PKG + "MobCfg"), JClass(PKG + "MobSpawn"), JClass(PKG + "MobSpoils"), JClass(PKG + "MobSecret")
    P = JClass("java.nio.file.Paths")
    files = [f for f in ("config.properties", "bands.properties", "trees.properties") if os.path.isfile(os.path.join(home, f))]
    before = dict((f, open(os.path.join(home, f), "rb").read()) for f in files)
    K.check("config.properties" in files, "D the live copy has a config.properties (%s)" % files)
    K.check(b"spawn.density" not in before.get("config.properties", b""), "D the live file has no spawn lines yet")

    def start():
        Cfg.DIR = P.get(home)
        Cfg.FILE = P.get(os.path.join(home, "config.properties"))
        Cfg.BANDS = P.get(os.path.join(home, "bands.properties"))
        o = "".join(str(JClass(PKG + m).run(P.get(home))) for m in ("MobMig", "MobMig14", "MobMig11", "MobMig12", "MobMigP4"))
        o += str(Sp.migrateWc15(P.get(home)))
        Cfg.load()
        Sp.loadV3(P.get(home))
        Sc.load(P.get(home))
        return o
    o1 = start()
    K.eq([int(S.pct(z)) for z in (1, 2, 3, 4)], [125, 125, 125, 125], "D start 1: no spawn lines in the live file -> the defaults (125 %)")
    K.eq(dict((f, open(os.path.join(home, f), "rb").read() == before[f]) for f in files), dict((f, True) for f in files),
         "D start 1: config / bands / trees bytes untouched (no migration; older updates %r)" % o1[:60])
    K.eq(int(S.tick(False)), -1, "D a tick before the spawner is up does nothing")
    o2 = start()
    K.eq((o2, [int(S.pct(z)) for z in (1, 2, 3, 4)]), ("", [125, 125, 125, 125]), "D start 2: nothing migrates, the same densities")
    K.eq(dict((f, open(os.path.join(home, f), "rb").read() == before[f]) for f in files), dict((f, True) for f in files), "D start 2: bytes still untouched")
    K.save()


# the kit's class compare allows only manifest.json among non-class entries: it compares a copy WITHOUT the generated spawn files (phase S
# checks those: only spawn files + the 3 classes are new, the manifest the only other change)
_cmp0 = HK.run_compare


def _cmp(out, jar, old_jar, pkg, expect, added, removed=()):
    d = os.path.join(SCRATCH, "cmpjar")
    os.makedirs(d, exist_ok=True)
    sj = os.path.join(d, os.path.basename(jar))
    with zipfile.ZipFile(jar) as zi, zipfile.ZipFile(sj, "w", zipfile.ZIP_DEFLATED) as zo:
        for n in zi.namelist():
            if not n.startswith(SD):
                zo.writestr(n, zi.read(n))
    return _cmp0(out, sj, old_jar, pkg, expect, added, removed)


HK.run_compare = _cmp
HK.run("SkyyMobs", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("static", run_static), ("exec", run_exec), ("ex120", T120.run_exec), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyMobs"))
