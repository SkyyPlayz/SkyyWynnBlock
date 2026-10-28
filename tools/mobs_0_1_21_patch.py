"""Derive SkyyMobs/build_skyymobs_0.1.21.py from the GENERATED 0.1.20 (build_skyymobs_0.1.20.py = the tools/deploy_set.py SET pin, made by
tools/mobs_0_1_20_patch.py). Every anchor is asserted once; at the end every change is undone on a copy and compared with 0.1.20
(tools/soundpass_gen.Patch); line endings kept.
Run:  python tools/mobs_0_1_21_patch.py   then   python SkyyMobs/build_skyymobs_0.1.21.py   then   python SkyyMobs/test_skyymobs_0.1.21.py
Edit THIS file, never the generated script (never --deploy).

0.1.21 (2026-10-27) = MORE MOB SPAWNS, skeletons first (round spawn1 = research/Mob-Variety-Spec.md Proposal A; the tougher versions
  = Proposal B are the NEXT round variety1). Skyy 2026-10-27: "can you increase mob spawn rates, especially for the skeletons in the over
  world" + popup "Mob spawns: how many more?" -> "Skeletons 4x, others 1.5x (Recommended)" (docs/answered/mobs.md).
  1. A1 SPAWN TABLES (build time, Assets.zip -> the jar; never committed - PROJECT-RULES 2). Every vanilla Server/NPC/Spawn/World/
     Zone1-4 + Void file that holds a monster is shipped again under its OWN path (the same asset id = it replaces vanilla's file, the
     way SkyySkills / SkyyCooking / SkyyArmory already replace vanilla item files and NoCube Undead Warriors replaced the Wander files)
     with: every Skeleton_* weight x3; every other MONSTER (hostile roles under Undead/, Void/, Creature/Mythic/ and the Goblin / Trork /
     Outlander / Scarak factions) x1.5; animals, predators (wolves, bears, spiders, snakes, rats), critters and fish untouched. Plus one
     NEW file per vanilla Wander list (SkyyMobs_Camp_Zone<N>_Tier<N>.json, same environments / hours / flock / block set) with the
     vanilla skeleton types vanilla only puts in camps (Soldier, Archer, Scout, Knight, Ranger, Archmage; Sand / Frost / Burnt /
     Incandescent the same way, no Gunner - "No guns"; the vanilla Burnt Gunner keeps its vanilla weight too), worth one more x1 of that list's vanilla skeleton weight = skeleton weight x4
     in each Wander list. Engine facts (0.7 jar, tools/dev): each environment's share = weight / the sum of EVERY entry listing that
     environment (recalculateWeight ignores DayTimeRange - night-only entries count all day), so the build prints old -> new skeletons
     per chunk for every environment (Zone 1 plains ~x4, forests ~x3.7 with A2).
     Build asserts: every id a vanilla role, every environment real; no camp NPC + environment pair already in any other file (the engine
     drops the second: "Combination NPC %s with Environment %s defined before"); no SET jar ships a world spawn file; no ENABLED pack mod
     (Saves/NewBetaTest/config.json, read only) ships a file under one of our paths or one of our NPC + environment pairs (switched-off
     mods that would clash are printed - NoCube Undead Warriors overrides the same Wander files and must stay off).
  2. A2 DENSITY PER ZONE (live): Server Setup > Mobs > Spawns: spawn.density.z1 .. z4 (% of vanilla, default 125, 0-300; Zone 5 has
     no vanilla environments yet). MobSpawn sets the SERVER-WIDE EnvironmentSpawnParameters density (public setDensity(double)) of the
     surface environments of each zone (Env_ZoneN and Env_ZoneN_*, not caves / dungeons / mineshafts) to vanilla x %, then calls the
     public WorldSpawnManager.onEnvironmentChanged() (vanilla's own re-apply: world.execute per world -> setDensity + recalculateWeight).
     Why server-wide and not the per-world WorldEnvironmentSpawnData.setDensity the spec named: ChunkSpawningSystems.processStartedChunk
     gives every newly started chunk SpawningPlugin.getEnvironmentDensity (the server-wide value), so a per-world value would be undone
     chunk by chunk. Island worlds use Env_Default_Void (no spawns) and are unaffected. MobSpawnTask re-checks every 30 s (an asset
     reload puts vanilla back: SpawningPlugin.onEnvironmentChange -> updateSpawnParameters) and a Server Setup change applies at once
     (after=MobSpawn.changed). Shutdown puts vanilla back. Perf hold (spec 4): the default never goes above 125 (asserted).
  3. A3 PER-FAMILY ROWS: NOT built - the live weight change is not possible: WorldNPCSpawnStat copies RoleSpawnParameters.getWeight()
     into its own private field when it is made (no setter, no public re-read). The weights are build-time defaults; the Spawns tab says
     so in its help texts.
  4. /mobs spawns (admin: requirePermission skyymobs.admin + setPermissionGroups(new String[0])): the zone densities in force, the
     built-in weight rule, this world's environmental NPCs actual / expected / the engine cap (GameplayConfig.MaxEnvironmentalNPCSpawns,
     500 when a gameplay config does not set it - vanilla Default.json does not), and per environment of this world: density now
     (vanilla), NPCs actual / expected, skeletons actual / expected. Reads only (WorldSpawnData on the world thread).
  SAVED DATA: none (new config keys only; a missing line = the default; no migration). Classes MobSpawn, MobSpawnTask, MobsSpawnsCmd; no
  new system; no new bridge key; one new admin sub-command. The jar now carries an asset pack (IncludesAssetPack true).
  ROLLBACK to 0.1.20: safe alone - vanilla weights + densities come back at the next start; mobs already spawned despawn normally. No floor.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

P = G.Patch(os.path.join(ROOT, "SkyyMobs", "build_skyymobs_0.1.20.py"), os.path.join(ROOT, "SkyyMobs", "build_skyymobs_0.1.21.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.1.20"') and P.s.startswith('"""SkyyMobs 0.1.20 - build script') and P.has("MobSecret") and not P.has("MobSpawn"), "not the SET pin 0.1.20"
REG0, SYS0, CLS0 = P.s.count("registerCommand("), P.s.count("registerSystem("), P.s.count("makeClass(")
HEAD = open(os.path.abspath(__file__), encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.1.21 (2026-10-27)"):].rstrip() + "\n\n"

P.rep('''"""SkyyMobs 0.1.20 - build script (javassist via jpype). GENERATED by tools/mobs_0_1_20_patch.py from the SET pin 0.1.19 - edit the
patch, never this file. Run: python SkyyMobs/build_skyymobs_0.1.20.py -> SkyyMobs/SkyyMobs-0.1.20.jar (never --deploy).
Test: python SkyyMobs/test_skyymobs_0.1.20.py
''', '''"""SkyyMobs 0.1.21 - build script (javassist via jpype). GENERATED by tools/mobs_0_1_21_patch.py from the SET pin 0.1.20 - edit the
patch, never this file. Run: python SkyyMobs/build_skyymobs_0.1.21.py -> SkyyMobs/SkyyMobs-0.1.21.jar (never --deploy).
Test: python SkyyMobs/test_skyymobs_0.1.21.py
''' + NOTE)
P.rep('VERSION = "0.1.20"', 'VERSION = "0.1.21"')

# ---------- 1. A1: the spawn tables (Python, from Assets.zip) + the build checks + the A2 environment list
P.rep('''      % (len(_SEC_V), ", ".join(_SEC_V[:6]), SEC_VP_DEF, SEC_BZ_DEF, SEC_BN_DEF, SEC_BH_DEF, SEC_LZ_DEF))
''', r'''      % (len(_SEC_V), ", ".join(_SEC_V[:6]), SEC_VP_DEF, SEC_BZ_DEF, SEC_BN_DEF, SEC_BH_DEF, SEC_LZ_DEF))
# ================================================================= 0.1.21 (spawn1): A1 spawn tables + A2 environments (tools/mobs_0_1_21_patch.py)
SPAWN_DIR = "Server/NPC/Spawn/World/"
SPAWN_FOLDERS = ("Zone1", "Zone2", "Zone3", "Zone4", "Void")          # Zone0 = oceans (fish), Unique = portal / instance worlds: untouched
SPAWN_SKEL_X, SPAWN_MON_X = 3.0, 1.5          # Skyy 2026-10-27 "Skeletons 4x, others 1.5x": x3 here + the camp types (x1 more) + A2 125 %
SPAWN_DENS_DEF, SPAWN_DENS_MAX = 125, 300
assert SPAWN_DENS_DEF <= 125, "perf hold (spec 4): never default the density above 125 % until the scheduler stalls are read"
MONSTER_DIRS = ("Undead/", "Void/", "Creature/Mythic/", "Intelligent/Faction/Goblin/", "Intelligent/Faction/Trork/",
                "Intelligent/Faction/Outlander/", "Intelligent/Faction/Scarak/")
# the vanilla skeleton types vanilla only spawns from camp markers, per Wander list (relative shares; total = x1 of the list's skeleton weight)
SPAWN_CAMP = {
    "Zone1/Wander_Zone1_Tier1": [("Skeleton_Soldier", 2), ("Skeleton_Archer", 2), ("Skeleton_Scout", 2), ("Skeleton_Knight", 1)],
    "Zone1/Wander_Zone1_Tier2": [("Skeleton_Soldier", 3), ("Skeleton_Archer", 3), ("Skeleton_Scout", 2), ("Skeleton_Knight", 2)],
    "Zone1/Wander_Zone1_Tier3": [("Skeleton_Soldier", 3), ("Skeleton_Knight", 3), ("Skeleton_Archer", 3), ("Skeleton_Ranger", 2),
                                 ("Skeleton_Archmage", 2)],
    "Zone2/Wander_Zone2_Tier1": [("Skeleton_Sand_Soldier", 2), ("Skeleton_Sand_Archer", 2), ("Skeleton_Sand_Scout", 2)],
    "Zone2/Wander_Zone2_Tier2": [("Skeleton_Sand_Soldier", 3), ("Skeleton_Sand_Archer", 3), ("Skeleton_Sand_Scout", 2), ("Skeleton_Sand_Ranger", 2)],
    "Zone2/Wander_Zone2_Tier3": [("Skeleton_Sand_Soldier", 4), ("Skeleton_Sand_Archer", 4), ("Skeleton_Sand_Ranger", 3), ("Skeleton_Sand_Archmage", 2)],
    # Zone 3: only the Frost types DungeonBosses (pack, on) leaves alone - it gives Frost Archer / Archmage / Fighter / Knight / Mage / Ranger
    # (and their _Wander variants) StructureV2's Sv2_Magic in their FlockArray = flock members of a world spawn (FlockSpawnTypes)
    "Zone3/Wander_Zone3_Tier1": [("Skeleton_Frost_Scout", 2), ("Skeleton_Frost_Soldier", 2)],
    "Zone3/Wander_Zone3_Tier2": [("Skeleton_Frost_Soldier", 3), ("Skeleton_Frost_Scout", 2)],
    "Zone3/Wander_Zone3_Tier3": [("Skeleton_Frost_Scout", 3), ("Skeleton_Frost_Scout_Wander", 1)],
    "Zone4/Wander_Zone4_Tier1": [("Skeleton_Burnt_Knight", 2), ("Skeleton_Burnt_Archer", 2)],
    "Zone4/Wander_Zone4_Tier2": [("Skeleton_Burnt_Knight", 2), ("Skeleton_Burnt_Archer", 2), ("Skeleton_Burnt_Alchemist", 1),
                                 ("Skeleton_Burnt_Wizard", 1), ("Skeleton_Incandescent_Fighter", 1)],
}


def spawn_kind(role):
    """'skeleton' (x3), 'monster' (x1.5) or None (animals, predators, critters, fish: unchanged)"""
    if role.startswith("Skeleton_"):
        return None if "Gunner" in role else "skeleton"          # fix 2: "No guns" (docs/answered/mobs.md 2026-10-09) - the one vanilla gun
                                                                  # skeleton (Burnt Gunner, Zone 4 volcanoes) keeps its vanilla weight
    if ATT.get(role) == "HOSTILE" and ROLE_PATH.get(role, "").startswith(MONSTER_DIRS):
        return "monster"
    return None


def spawn_json(d):
    return json.dumps(d, indent=2) + "\n"


SPAWN_VAN = {}          # "Zone1/Wander_Zone1_Tier1" -> the parsed vanilla file
for _n in AZ_NAMES:
    if _n.startswith(SPAWN_DIR) and _n.endswith(".json"):
        SPAWN_VAN[_n[len(SPAWN_DIR):-5]] = lenient(AZ.read(_n).decode("utf-8-sig"))
assert all(_k in SPAWN_VAN for _k in SPAWN_CAMP), "0.1.21: a vanilla Wander list moved: %s" % [_k for _k in SPAWN_CAMP if _k not in SPAWN_VAN]
assert sorted(_k for _k in SPAWN_VAN if "/Wander_" in _k) == sorted(SPAWN_CAMP), "0.1.21: vanilla has a Wander list without camp types"
SPAWN_FILES = {}        # jar path -> text: the replaced vanilla files + our camp files (generated here, never committed)
SPAWN_NEW = {}          # key -> parsed file (ours)
SPAWN_X = {}            # role -> "skeleton" / "monster" / "camp"
for _k, _d in sorted(SPAWN_VAN.items()):
    if _k.split("/")[0] not in SPAWN_FOLDERS:
        continue
    _nd = json.loads(json.dumps(_d))
    _ch = False
    for _e in _nd.get("NPCs", []):
        _kd = spawn_kind(_e["Id"])
        if _kd:
            _e["Weight"] = round(float(_e["Weight"]) * (SPAWN_SKEL_X if _kd == "skeleton" else SPAWN_MON_X), 4)
            SPAWN_X[_e["Id"]] = _kd
            _ch = True
    if _ch:
        SPAWN_FILES[SPAWN_DIR + _k + ".json"] = spawn_json(_nd)
        SPAWN_NEW[_k] = _nd
for _k, _roles in sorted(SPAWN_CAMP.items()):
    _v = SPAWN_VAN[_k]
    _sk = sum(float(_e["Weight"]) for _e in _v["NPCs"] if _e["Id"].startswith("Skeleton_"))
    _tot = float(sum(_w for _r, _w in _roles))
    _first = _v["NPCs"][0]
    _ents = []
    for _r, _w in _roles:
        assert _r in ROLES and ROLES[_r].get("Type") not in ("Abstract", "Component") and ATT.get(_r) == "HOSTILE", "0.1.21: camp type %s" % _r
        assert "Gunner" not in _r, "No guns (docs/answered/mobs.md 2026-10-09)"
        _e = {"Weight": round(_sk * _w / _tot, 4), "Id": _r}
        if "SpawnBlockSet" in _first:
            _e["SpawnBlockSet"] = _first["SpawnBlockSet"]
        if "Flock" in _first:
            _e["Flock"] = _first["Flock"]
        _ents.append(_e)
        SPAWN_X[_r] = "camp"
    _ck = _k.split("/")[0] + "/SkyyMobs_Camp_" + _k.split("_", 1)[1]
    _cd = {"Environments": list(_v["Environments"]), "NPCs": _ents, "DayTimeRange": _v.get("DayTimeRange", [0, 24])}
    assert SPAWN_DIR + _ck + ".json" not in AZ_NAMES
    SPAWN_FILES[SPAWN_DIR + _ck + ".json"] = spawn_json(_cd)
    SPAWN_NEW[_ck] = _cd
# build checks: real ids / environments / flocks; the one-pair-per-file engine rule across vanilla + ours
_FLOCKS = set(_n.rsplit("/", 1)[1][:-5] for _n in AZ_NAMES if _n.startswith("Server/NPC/Flocks/") and _n.endswith(".json"))


def spawn_pairs(files):
    out = {}
    for _k, _d in files.items():
        for _env in _d.get("Environments", []):
            for _e in _d.get("NPCs", []):
                out.setdefault((_e["Id"], _env), []).append(_k)
    return out


_SP_ALL = dict(SPAWN_VAN)
_SP_ALL.update(SPAWN_NEW)
for _k, _d in SPAWN_NEW.items():
    for _env in _d["Environments"]:
        assert _env in ENV_IDS, "0.1.21: %s names environment %s (not in Assets.zip)" % (_k, _env)
    for _e in _d["NPCs"]:
        assert _e["Id"] in ROLES, "0.1.21: %s names role %s (not vanilla)" % (_k, _e["Id"])
        assert not isinstance(_e.get("Flock"), str) or _e["Flock"] in _FLOCKS, "0.1.21: flock %s" % _e.get("Flock")
_dup = [(_p, _f) for _p, _f in spawn_pairs(_SP_ALL).items() if len(_f) > 1]
assert not _dup, "0.1.21: an NPC + environment pair in two files (the engine drops the second): %s" % _dup[:4]
SPAWN_PAIRS = set(spawn_pairs(SPAWN_NEW))
# no SET jar ships a world spawn file (ours are the only overrides)
import importlib.util as _ilu
_dss = _ilu.spec_from_file_location("deploy_set_ro", SET_FILE)
_dsm = _ilu.module_from_spec(_dss)
_dss.loader.exec_module(_dsm)
for _m, _v in _dsm.SET:
    _j = os.path.join(ROOT, _m, "%s-%s.jar" % (_m, _v))
    if _m != MOD and os.path.isfile(_j):
        _bad = [_n for _n in zipfile.ZipFile(_j).namelist() if _n.startswith("Server/NPC/Spawn/World/")]
        assert not _bad, "0.1.21: SET jar %s %s ships world spawn files %s" % (_m, _v, _bad[:3])
# pack mods (Skyy's Mods folder + the test world's switches, read only): no enabled mod may ship our paths or our NPC + environment pairs
SPAWN_PACK = []         # report lines (off mods that would clash; enabled mods checked)
_MW = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "config.json")
if os.path.isdir(B.MODS_DIR) and os.path.isfile(_MW):
    _on = dict((_kk, bool((_vv or {}).get("Enabled"))) for _kk, _vv in (json.load(open(_MW, encoding="utf-8")).get("Mods") or {}).items())
    _ours = set(_p[len(SPAWN_DIR):] for _p in SPAWN_FILES)
    for _f in sorted(os.listdir(B.MODS_DIR)):
        try:
            _z = zipfile.ZipFile(os.path.join(B.MODS_DIR, _f))
            _names = _z.namelist()
        except Exception:
            continue
        _sp = [_n for _n in _names if SPAWN_DIR in _n and _n.endswith(".json")]
        if not _sp:
            continue
        _mf = sorted([_n for _n in _names if _n.lower().endswith("manifest.json")], key=len)
        try:
            _man = lenient(_z.read(_mf[0]).decode("utf-8-sig"))
            _key = "%s:%s" % (_man.get("Group"), _man.get("Name"))
        except Exception:
            _key = "?" + _f
        _same = sorted(_n[_n.index(SPAWN_DIR) + len(SPAWN_DIR):] for _n in _sp if _n[_n.index(SPAWN_DIR) + len(SPAWN_DIR):] in _ours)
        _pp = set()
        for _n in _sp:
            try:
                _pd = lenient(_z.read(_n).decode("utf-8-sig"))
            except Exception:
                continue
            for _env in _pd.get("Environments") or []:
                for _e in _pd.get("NPCs") or []:
                    if (_e.get("Id"), _env) in SPAWN_PAIRS and _n[_n.index(SPAWN_DIR) + len(SPAWN_DIR):] not in _ours:
                        _pp.add((_e.get("Id"), _env))
        _rov = set(_n.rsplit("/", 1)[1][:-5] for _n in _names if "Server/NPC/Roles/" in _n and _n.endswith(".json"))
        for _r in sorted(set(_r for _v in SPAWN_CAMP.values() for _r, _w in _v)):
            _chain, _x = [], _r
            while _x in ROLES and _x not in _chain and len(_chain) < 12:
                _chain.append(_x)
                _x = ROLES[_x].get("Reference") if ROLES[_x].get("Type") == "Variant" else None
            assert not (_on.get(_key) and _rov & set(_chain)), "0.1.21: ENABLED pack mod %s overrides camp type %s (%s) - its flock / stats would "                 "spread through our camp lists; take that type out of SPAWN_CAMP" % (_key, _r, sorted(_rov & set(_chain)))
        if _on.get(_key):
            assert not _same and not _pp, "0.1.21: ENABLED pack mod %s (%s) ships our spawn files %s / pairs %s - switch it off or drop ours" \
                % (_key, _f, _same[:4], sorted(_pp)[:4])
            SPAWN_PACK.append("on, no clash: %s" % _key)
        elif _same or _pp:
            SPAWN_PACK.append("OFF and must stay off (same files %s, pairs %d): %s" % (", ".join(_same[:3]) + (" ..." if len(_same) > 3 else ""), len(_pp), _key))
else:
    SPAWN_PACK.append("Mods folder / test world config not found - pack check skipped")
# the share table (engine: weight / sum of every entry of the environment; density = NPCs per loaded chunk of it)
_ENVJ = {}
for _n in AZ_NAMES:
    if _n.startswith("Server/Environments/") and _n.endswith(".json"):
        _ENVJ[_n.rsplit("/", 1)[1][:-5]] = (_n, lenient(AZ.read(_n).decode("utf-8-sig")))


def env_density(e, depth=0):
    if e not in _ENVJ or depth > 10:
        return 0.0
    d = _ENVJ[e][1]
    if "SpawnDensity" in d:
        return float(d["SpawnDensity"])
    return env_density(d["Parent"], depth + 1) if d.get("Parent") else 0.0


# A2: the surface environments of each zone (Server/Environments/ZoneN/), not caves / dungeons / mineshafts (spec 4: caves keep 100 %)
SPAWN_ENVS = []
for _e, (_n, _d) in sorted(_ENVJ.items()):
    _m = re.match(r"^Server/Environments/Zone([1-4])/", _n)
    if _m and not any(_x in _e for _x in ("Caves", "Dungeon", "Mineshaft", "Sewers")):          # fix: Env_Zone4_Sewers is underground too
        SPAWN_ENVS.append((_e, int(_m.group(1))))
for _e in ("Env_Zone1", "Env_Zone1_Plains", "Env_Zone1_Forests", "Env_Zone1_Azure", "Env_Zone2_Savanna", "Env_Zone3_Tundra", "Env_Zone4_Wastes"):
    assert _e in dict(SPAWN_ENVS), "0.1.21: %s is a managed surface environment" % _e
assert not [_e for _e, _z in SPAWN_ENVS if "Caves" in _e or "Sewers" in _e or _e == "Env_Default_Void"]
assert all(32 <= ord(_c) < 127 and _c not in '"\\' for _e, _z in SPAWN_ENVS for _c in _e)


def share_table(files):
    t = {}
    for _k, _d in files.items():
        for _env in _d.get("Environments", []):
            for _e in _d.get("NPCs", []):
                s = t.setdefault(_env, [0.0, 0.0, 0.0])
                w = float(_e["Weight"])
                s[0] += w
                if _e["Id"].startswith("Skeleton_"):
                    s[1] += w
                elif not spawn_kind(_e["Id"]):
                    s[2] += w          # fix: the entries the build leaves alone (animals, predators, critters, fish)
    return t


_SH0, _SH1 = share_table(SPAWN_VAN), share_table(_SP_ALL)
SPAWN_TABLE = []        # (env, density, old skeletons / chunk, new skeletons / chunk, non-monsters new / vanilla)
SPAWN_ANIMALS = {}      # fix: env -> the absolute rate of the untouched entries (animals, predators, critters, fish), new / vanilla
_ME = dict(SPAWN_ENVS)
for _env in sorted(_SH1):
    if not _env.startswith("Env_Zone") or _env not in _SH0:
        continue
    _d0 = env_density(_env)
    _d1 = _d0 * (SPAWN_DENS_DEF / 100.0 if _env in _ME else 1.0)
    if _SH0[_env][2] > 0 and _d0 > 0:
        SPAWN_ANIMALS[_env] = (_d1 * _SH1[_env][2] / _SH1[_env][0]) / (_d0 * _SH0[_env][2] / _SH0[_env][0])
    if _SH0[_env][1] <= 0:
        continue
    # fix 2: the ceiling (every NPC there a skeleton) and the gain if animals were held at vanilla (they take their vanilla absolute rate,
    # the monsters share the rest) - per environment, so approximate where one file feeds several environments (report numbers for Skyy)
    _sk0 = _d0 * _SH0[_env][1] / _SH0[_env][0]
    _rest = _d1 - _d0 * _SH0[_env][2] / _SH0[_env][0]
    _alt = max(0.0, _rest) * _SH1[_env][1] / max(1e-9, _SH1[_env][0] - _SH1[_env][2])
    SPAWN_TABLE.append((_env, _d0, _sk0, _d1 * _SH1[_env][1] / _SH1[_env][0], SPAWN_ANIMALS.get(_env), _d1 / _sk0, _alt / _sk0))
_ST = dict((_r[0], _r[3] / _r[2]) for _r in SPAWN_TABLE)
assert 3.5 <= _ST["Env_Zone1_Plains"] <= 5.0 and 3.0 <= _ST["Env_Zone1_Forests"] <= 5.0, "0.1.21: Zone 1 skeletons ~4x (%s)" % _ST
# Zone 4 is skeleton-heavy in vanilla already (Env_Zone4_Shores = skeletons only: only the density moves it, x1.25)
assert all(1.2 <= _x <= 5.0 for _x in _ST.values()), "0.1.21: every skeleton environment between x1.2 and x5: %s" % _ST
# fix: animals keep their own weights, but their SHARE drops where monsters grow (the 125 % density refills part of it): a regression guard
# (Zone 4 Forests ~0.54 / Wastes ~0.6 / Volcanoes ~0.63 = the lowest with Skyy's "Skeletons 4x, others 1.5x" under the 125 % perf hold; printed below, told to Skyy)
assert all(_x >= 0.5 for _x in SPAWN_ANIMALS.values()), "0.1.21: animals below 50 %% of vanilla: %s" % sorted((_x, _e) for _e, _x in SPAWN_ANIMALS.items())[:4]
print("0.1.21 spawns: %d spawn files in the jar (%d replaced vanilla, %d camp lists); x3 %d skeleton ids, x1.5 %d monster ids, %d camp types; "
      "density %d %% on %d surface environments of Zones 1-4" % (len(SPAWN_FILES), len(SPAWN_FILES) - len(SPAWN_CAMP), len(SPAWN_CAMP),
      len([1 for _v in SPAWN_X.values() if _v == "skeleton"]), len([1 for _v in SPAWN_X.values() if _v == "monster"]),
      len(set(_r for _v in SPAWN_CAMP.values() for _r, _w in _v)), SPAWN_DENS_DEF, len(SPAWN_ENVS)))
for _r in SPAWN_TABLE:
    print("   %-24s density %.2f: skeletons per chunk %.3f -> %.3f (x%.2f); animals / critters / fish x%s; ceiling x%.2f; animals held x%.2f"
          % (_r[0], _r[1], _r[2], _r[3], _r[3] / _r[2], "-" if _r[4] is None else "%.2f" % _r[4], _r[5], _r[6]))
print("   animals / critters / fish vs vanilla (all environments, lowest first): " + ", ".join("%s x%.2f" % (_e, _x) for _x, _e in sorted((_x, _e) for _e, _x in SPAWN_ANIMALS.items())[:8]))
print("   x1.5 monsters: " + ", ".join(sorted(_r for _r, _v in SPAWN_X.items() if _v == "monster")))
for _l in SPAWN_PACK:
    print("   pack: " + _l)
''')

# ---------- 2. the default file lines + the Spawns tab
P.rep('''              "secret.blood.night=" + SEC_BN_DEF, "secret.blood.heart=" + SEC_BH_DEF, "secret.light.zones=%d" % SEC_LZ_DEF]          # 0.1.20''',
      '''              "secret.blood.night=" + SEC_BN_DEF, "secret.blood.heart=" + SEC_BH_DEF, "secret.light.zones=%d" % SEC_LZ_DEF]          # 0.1.20
CFG_LINES += ["# Mob spawns (SkyyMobs 0.1.21): how many NPCs each zone's surface environments spawn, in % of vanilla (100 = vanilla; caves",
              "# and sewers stay vanilla). Which monsters and how often (skeletons x3 + the camp skeleton types, other monsters x1.5) is built",
              "# into the mod; animals keep their weights, so where monsters grow their share drops (Zone 4 ~55-65 % of vanilla at 125).",
              ] + ["spawn.density.z%d=%d" % (_z, SPAWN_DENS_DEF) for _z in (1, 2, 3, 4)]          # 0.1.21''')
P.rep('''CFG_CATS.insert(CFG_CATS.index(("elem", "Elements")) + 1, ("secret", "Secret eggs"))          # 0.1.20''',
      '''CFG_CATS.insert(CFG_CATS.index(("elem", "Elements")) + 1, ("secret", "Secret eggs"))          # 0.1.20
CFG_CATS.insert(CFG_CATS.index(("secret", "Secret eggs")) + 1, ("spawn", "Spawns"))          # 0.1.21''')
P.rep('''CFG_ROWS += SEC_ROWS
CFG_TITLE = "Mobs"
CFG_NOTE = "Chat: /mobs (players); /mobs inspect, set <level>, platetest, reload (admins)."''', '''CFG_ROWS += SEC_ROWS
# 0.1.21 (spawn1): the density per zone (live); the weights are built in (A3: no live weight change in this game version)
SPAWN_ROWS = [("spawn.density.z%d" % _z, "Zone %d mob spawns" % _z, "spawn", "int", str(SPAWN_DENS_DEF), "0", str(SPAWN_DENS_MAX), "", "%", "live",
               {1: "Zone 1 land NPCs, % of vanilla. Built in: skeletons x3, monsters x1.5. Above 125 may lag.",          # fix 2: perf hold
                4: "Zone 4 land NPCs, % of vanilla. Vanilla is mostly skeletons; animals thin out. Above 125 may lag."}.get(_z,
                "Zone %d land NPCs, %% of vanilla. Caves and sewers stay vanilla. Above 125 may lag." % _z),
               "field:MobCfg.SPAWN_Z%d;after=MobSpawn.changed" % _z) for _z in (1, 2, 3, 4)]
assert all(len(_r[1]) <= 40 and len(_r[10]) <= 100 for _r in SPAWN_ROWS), [(len(_r[1]), len(_r[10])) for _r in SPAWN_ROWS]
CFG_ROWS += SPAWN_ROWS
CFG_TITLE = "Mobs"
CFG_NOTE = "Chat: /mobs (players); /mobs inspect, set <level>, platetest, reload, spawns (admins)."''')

# ---------- 3. MobCfg fields + load
P.rep('''          "public static volatile int SEC_LZONES = %d;" % SEC_LZ_DEF):
    F(cfg, f)
''', '''          "public static volatile int SEC_LZONES = %d;" % SEC_LZ_DEF):
    F(cfg, f)
for _z in (1, 2, 3, 4):          # 0.1.21 (spawn1): the density per zone (% of vanilla)
    F(cfg, "public static volatile int SPAWN_Z%d = %d;" % (_z, SPAWN_DENS_DEF))
''')
P.rep('''  SEC_LZONES = intOf(c.getProperty("secret.light.zones"), @SECLZ@, 1, 5);''',
      '''  SEC_LZONES = intOf(c.getProperty("secret.light.zones"), @SECLZ@, 1, 5);
  SPAWN_Z1 = intOf(c.getProperty("spawn.density.z1"), @SPDEF@, 0, @SPMAX@);          // 0.1.21: the density per zone (a missing line = the default)
  SPAWN_Z2 = intOf(c.getProperty("spawn.density.z2"), @SPDEF@, 0, @SPMAX@);
  SPAWN_Z3 = intOf(c.getProperty("spawn.density.z3"), @SPDEF@, 0, @SPMAX@);
  SPAWN_Z4 = intOf(c.getProperty("spawn.density.z4"), @SPDEF@, 0, @SPMAX@);''')
P.rep('''   .replace("@SECBH@", jstr(SEC_BH_DEF)).replace("@SECLZ@", str(SEC_LZ_DEF))          # 0.1.17; 0.1.20''',
      '''   .replace("@SECBH@", jstr(SEC_BH_DEF)).replace("@SECLZ@", str(SEC_LZ_DEF)) \\
   .replace("@SPDEF@", str(SPAWN_DENS_DEF)).replace("@SPMAX@", str(SPAWN_DENS_MAX))          # 0.1.17; 0.1.20; 0.1.21''')

# ---------- 4. engine classes + probes
P.rep('''          "WTR": "com.hypixel.hytale.server.core.modules.time.WorldTimeResource"})          # the night check (the SkyyFishing / SkyyShards clock)''',
      '''          "WTR": "com.hypixel.hytale.server.core.modules.time.WorldTimeResource"})          # the night check (the SkyyFishing / SkyyShards clock)
T.update({"SPPL": "com.hypixel.hytale.server.spawning.SpawningPlugin",          # 0.1.21 (spawn1): the zone densities + /mobs spawns
          "ESPP": "com.hypixel.hytale.server.spawning.world.manager.EnvironmentSpawnParameters",
          "WSMG": "com.hypixel.hytale.server.spawning.world.manager.WorldSpawnManager",
          "WSPD": "com.hypixel.hytale.server.spawning.world.component.WorldSpawnData",
          "WESD": "com.hypixel.hytale.server.spawning.world.WorldEnvironmentSpawnData",
          "WNSS": "com.hypixel.hytale.server.spawning.world.WorldNPCSpawnStat",
          "GPCF": "com.hypixel.hytale.server.core.asset.type.gameplay.GameplayConfig",
          "NPCPL": "com.hypixel.hytale.server.npc.NPCPlugin"})''')
P.rep('''for _c, _m, _r, _a in SIGS:''', '''# 0.1.21 (spawn1): the server-wide environment density, vanilla's re-apply, the per-world readout (exact descriptors)
SIGS += [(G["SPPL"], "get", G["SPPL"], []), (G["SPPL"], "getWorldEnvironmentSpawnParameters", G["ESPP"], ["int"]),
         (G["ESPP"], "getSpawnDensity", "double", []), (G["ESPP"], "setDensity", "void", ["double"]),
         (G["WSMG"], "onEnvironmentChanged", "void", []), (G["ENVA"], "getAssetMap", G["ILT"], []), (G["ENVA"], "getSpawnDensity", "double", []),
         (G["ILT"], "getIndexOrDefault", "int", ["java.lang.Object", "int"]),
         (G["ILT"], "getAsset", "com.hypixel.hytale.assetstore.map.JsonAssetWithMap", ["int"]),
         (G["WSPD"], "getResourceType", "com.hypixel.hytale.component.ResourceType", []),
         (G["WSPD"], "getWorldEnvironmentSpawnData", G["WESD"], ["int"]), (G["WSPD"], "getActualNPCs", "int", []),
         (G["WSPD"], "getExpectedNPCs", "double", []), (G["WESD"], "getActualNPCs", "int", []), (G["WESD"], "getExpectedNPCs", "double", []),
         (G["WESD"], "getNpcStatMap", "it.unimi.dsi.fastutil.ints.Int2ObjectMap", []), (G["WNSS"], "getRoleIndex", "int", []),
         (G["WNSS"], "getActual", "int", []), (G["WNSS"], "getExpected", "double", []), (G["NPCPL"], "get", G["NPCPL"], []),
         (G["NPCPL"], "getName", "java.lang.String", ["int"]), (G["WLD"], "getGameplayConfig", G["GPCF"], []),
         (G["GPCF"], "getMaxEnvironmentalNPCSpawns", "int", [])]
for _c, _m, _r, _a in SIGS:''')

# ---------- 5. the classes
P.rep('''mvat = pool.makeClass(PKG + ".MobVoidAtFn")  # 0.1.20: mob:fn:voidAt (SkyyFishing's Void catches)''',
      '''mvat = pool.makeClass(PKG + ".MobVoidAtFn")  # 0.1.20: mob:fn:voidAt (SkyyFishing's Void catches)
mspw = pool.makeClass(PKG + ".MobSpawn")     # 0.1.21 (spawn1): the zone densities (server-wide environment density) + /mobs spawns lines
mspk = pool.makeClass(PKG + ".MobSpawnTask")  # 0.1.21: the 30 s re-check (an asset reload puts vanilla back)''')
P.rep('''msp, mss, mel, mef, meo, megg, msec, mlds, mvat]''', '''msp, mss, mel, mef, meo, megg, msec, mlds, mvat, mspw, mspk]''')

MSPW = r'''# ================================================================= 0.1.21 MobSpawn: the zone densities + the /mobs spawns lines (tools/mobs_0_1_21_patch.py
# docstring 2 + 4). ENVS / ZONES = the surface environments of Zones 1-4 (built from Assets.zip). The density is the SERVER-WIDE
# EnvironmentSpawnParameters value (new chunks read it: ChunkSpawningSystems.processStartedChunk); WorldSpawnManager.onEnvironmentChanged()
# is vanilla's own re-apply to every world (world.execute each). set() / want() / pct() / envLine() take
# engine objects the harness makes itself (EnvironmentSpawnParameters(double), WorldEnvironmentSpawnData(int, double), WorldSpawnData());
# NAME_API = the one seam (role names without an NPCPlugin).
for _f in ("public static final String[] ENVS = new String[] { %s };" % ", ".join(jstr(_e) for _e, _z in SPAWN_ENVS),
           "public static final int[] ZONES = new int[] { %s };" % ", ".join(str(_z) for _e, _z in SPAWN_ENVS),
           "public static volatile java.util.concurrent.ScheduledFuture TASK = null;",
           "public static volatile long TICKS = 0L;", "public static volatile long SETS = 0L;", "public static volatile long REFRESHES = 0L;",
           "public static volatile long FAILS = 0L;", "public static volatile int FOUND = -1;",
           "public static volatile boolean STOPPING = false;",          # fix: shutdown - a late 30 s run never re-applies after the restore
           "public static volatile java.util.function.Function NAME_API = null;",          # harness seam: role index -> name (null in the game = NPCPlugin)
           "public static volatile String LAST = \"not run yet\";"):
    F(mspw, _f)
M(mspw, r"""
public static int pct(int zone) {
  int p = 100;
  if (zone == 1) p = @PKG@.MobCfg.SPAWN_Z1;
  else if (zone == 2) p = @PKG@.MobCfg.SPAWN_Z2;
  else if (zone == 3) p = @PKG@.MobCfg.SPAWN_Z3;
  else if (zone == 4) p = @PKG@.MobCfg.SPAWN_Z4;
  if (p < 0) p = 0;
  if (p > @SPMAX@) p = @SPMAX@;
  return p;
}""".replace("@SPMAX@", str(SPAWN_DENS_MAX)))
M(mspw, r"""
public static double want(double base, int pct) {
  if (Double.isNaN(base) || base <= 0.0) return 0.0;
  return base * (double) pct / 100.0;
}""")
# set one environment's server-wide density; true = it changed
M(mspw, r"""
public static boolean set(@ESPP@ p, double d) {
  if (p == null || Double.isNaN(d) || d < 0.0) return false;
  if (Math.abs(p.getSpawnDensity() - d) < 1.0E-9) return false;
  p.setDensity(d);
  return true;
}""")
M(mspw, r"""
public static int zoneOf(String env) {
  if (env == null) return 0;
  for (int i = 0; i < ENVS.length; i++) if (ENVS[i].equals(env)) return ZONES[i];
  return 0;
}""")
# the environment's own (asset) density = vanilla's value, also after an asset reload; -1 = unknown
M(mspw, r"""
public static double base(int idx) {
  try {
    @ILT@ m = @ENVA@.getAssetMap();
    if (m == null || idx < 0) return -1.0;
    Object e = m.getAsset(idx);
    if (!(e instanceof @ENVA@)) return -1.0;
    return ((@ENVA@) e).getSpawnDensity();
  } catch (Throwable t) { return -1.0; }
}""")
M(mspw, r"""
public static int index(String id) {
  try {
    @ILT@ m = @ENVA@.getAssetMap();
    if (m == null || id == null) return -1;
    int i = m.getIndexOrDefault(id, -1);
    return i < 0 ? -1 : i;
  } catch (Throwable t) { return -1; }
}""")
M(mspw, r"""
public static boolean refresh() {
  try { @WSMG@.onEnvironmentChanged(); REFRESHES = REFRESHES + 1L; return true; }
  catch (Throwable t) { FAILS = FAILS + 1L; @PKG@.MobLog.warnOnce("spawnrefresh", "the spawn density re-apply failed (logged once): " + t); return false; }
}""")
# one pass over the managed environments: vanilla x % (restore = vanilla); -1 = the spawner is not ready (no SpawningPlugin yet).
# synchronized (fix): the 30 s task and the shutdown restore never interleave; STOPPING = only the restore runs any more
M(mspw, r"""
public static synchronized int tick(boolean restore) {
  TICKS = TICKS + 1L;
  if (STOPPING && !restore) { LAST = "stopped (vanilla densities back)"; return 0; }
  @SPPL@ sp = null;
  try { sp = @SPPL@.get(); } catch (Throwable t) { sp = null; }
  if (sp == null) { FOUND = -1; LAST = "the spawner is not ready yet"; return -1; }
  int found = 0, changed = 0;
  for (int i = 0; i < ENVS.length; i++) {
    int idx = index(ENVS[i]);
    if (idx < 0) continue;
    @ESPP@ p = null;
    try { p = sp.getWorldEnvironmentSpawnParameters(idx); } catch (Throwable t) { p = null; }
    if (p == null) continue;
    double b = base(idx);
    if (b < 0.0) continue;
    found++;
    if (set(p, restore ? b : want(b, pct(ZONES[i])))) changed++;
  }
  FOUND = found;
  SETS = SETS + (long) changed;
  if (changed > 0) refresh();          // fix: also after the restore (a plugin reload without a restart puts vanilla back in the worlds)
  LAST = (restore ? "vanilla put back on " : "set ") + changed + " of " + found + " environments";
  return changed;
}""")
M(mspw, r"""
public static void changed(String key) {
  try { tick(false); } catch (Throwable t) { @PKG@.MobLog.warnOnce("spawnchanged", "the new spawn density could not be applied now (logged once; the 30 s check retries): " + t); }
}""")
M(mspw, r"""
public static String zonesText() {
  return "Zone 1 " + pct(1) + " %, Zone 2 " + pct(2) + " %, Zone 3 " + pct(3) + " %, Zone 4 " + pct(4) + " %";
}""")
M(mspw, r"""
public static String text() {
  return "spawns " + zonesText() + " of vanilla (" + (FOUND < 0 ? "spawner not ready yet" : FOUND + " environments") + "; built in: skeletons x@SKX@ + @CAMP@ camp skeleton types, monsters x@MONX@, @FILES@ spawn files)";
}""".replace("@SKX@", "%g" % SPAWN_SKEL_X).replace("@MONX@", "%g" % SPAWN_MON_X).replace("@FILES@", str(len(SPAWN_FILES)))
   .replace("@CAMP@", str(len(set(_r for _v in SPAWN_CAMP.values() for _r, _w in _v)))))
# one environment of a world: density now (vanilla), NPCs actual / expected, skeletons actual / expected
M(mspw, r"""
public static double[] counts(@WESD@ d) {
  int a = 0, sa = 0;
  double e = 0.0, se = 0.0;
  if (d != null) {
    a = d.getActualNPCs();
    e = d.getExpectedNPCs();
    java.util.Iterator it = d.getNpcStatMap().values().iterator();
    while (it.hasNext()) {
      Object o = it.next();
      if (!(o instanceof @WNSS@)) continue;
      @WNSS@ s = (@WNSS@) o;
      String n = null;
      try {
        java.util.function.Function f = NAME_API;
        if (f != null) { Object x = f.apply(Integer.valueOf(s.getRoleIndex())); n = x instanceof String ? (String) x : null; }
        else n = @NPCPL@.get().getName(s.getRoleIndex());
      } catch (Throwable t) { n = null; }
      if (n != null && n.startsWith("Skeleton_")) { sa += s.getActual(); se += s.getExpected(); }
    }
  }
  return new double[] { (double) a, e, (double) sa, se };
}""")
M(mspw, r"""
public static String envLine(String id, double now, double van, @WESD@ d) {
  double[] c = counts(d);
  return "=  " + id + ": density " + @PKG@.MobCfg.num2(now) + " (vanilla " + @PKG@.MobCfg.num2(van) + "), NPCs " + (int) c[0] + " / " + @PKG@.MobCfg.num2(c[1])
      + ", skeletons " + (int) c[2] + " / " + @PKG@.MobCfg.num2(c[3]);
}""")
# fix (critics: the 14-line cap cut Zones 2-4): where you stand, one summary line per zone, then your environment first and only the
# environments with NPCs, at most max rows + "(N more)". ids / data / now / van = the loaded managed environments of this world (same order).
M(mspw, r"""
public static String[] pick(String[] ids, @WESD@[] data, double[] now, double[] van, String here, int max) {
  java.util.ArrayList l = new java.util.ArrayList();
  int hz = zoneOf(here);
  if (here != null) l.add("=[Mobs] You stand in " + here + (hz > 0 ? " (Zone " + hz + ", " + pct(hz) + " %)." : " (not a Zone 1-4 land environment: vanilla density)."));
  double[][] c = new double[ids.length][];
  for (int i = 0; i < ids.length; i++) c[i] = counts(data[i]);
  for (int z = 1; z <= 4; z++) {
    int n = 0;
    double a = 0.0, e = 0.0, sa = 0.0, se = 0.0;
    for (int i = 0; i < ids.length; i++) {
      if (zoneOf(ids[i]) != z) continue;
      n++; a += c[i][0]; e += c[i][1]; sa += c[i][2]; se += c[i][3];
    }
    if (n > 0) l.add("=[Mobs] Zone " + z + " (" + n + " environments here, " + pct(z) + " %): NPCs " + (int) a + " / " + @PKG@.MobCfg.num2(e)
        + ", skeletons " + (int) sa + " / " + @PKG@.MobCfg.num2(se) + ".");
  }
  int shown = 0, more = 0, hi = -1;
  for (int i = 0; i < ids.length; i++) if (ids[i].equals(here)) hi = i;
  if (hi >= 0) { l.add(envLine(ids[hi], now[hi], van[hi], data[hi])); shown++; }
  for (int i = 0; i < ids.length; i++) {
    if (i == hi || (c[i][0] <= 0.0 && c[i][1] < 0.005 && c[i][2] <= 0.0 && c[i][3] < 0.005)) continue;
    if (shown >= max) { more++; continue; }
    l.add(envLine(ids[i], now[i], van[i], data[i]));
    shown++;
  }
  if (more > 0) l.add("=  (" + more + " more environments with NPCs not shown)");
  if (ids.length == 0) l.add("=[Mobs] None of the Zone 1-4 land environments is loaded in this world.");
  String[] a = new String[l.size()];
  for (int i = 0; i < a.length; i++) a[i] = (String) l.get(i);
  return a;
}""")
# the whole readout (world thread: the command's own world); ws may be null (no spawner in this world)
M(mspw, r"""
public static String[] lines(@WSPD@ ws, String wn, int cap, String here) {
  java.util.ArrayList l = new java.util.ArrayList();
  l.add("=[Mobs] Spawns: " + zonesText() + " of vanilla (Server Setup > Mobs > Spawns). " + LAST + ".");
  l.add("=[Mobs] Built in: skeletons x@SKX@ + the camp skeleton types, other monsters x@MONX@; animals, critters and fish as vanilla.");
  if (ws == null) { l.add("=[Mobs] " + wn + ": no world spawns here (no spawn data)."); }
  else {
    l.add("=[Mobs] " + wn + ": " + ws.getActualNPCs() + " NPCs out of " + @PKG@.MobCfg.num2(ws.getExpectedNPCs()) + " expected (cap " + (cap > 0 ? String.valueOf(cap) : "none") + ").");
    @SPPL@ sp = null;
    try { sp = @SPPL@.get(); } catch (Throwable t) { sp = null; }
    int n = 0;
    String[] ids = new String[ENVS.length];
    @WESD@[] data = new @WESD@[ENVS.length];
    double[] now = new double[ENVS.length];
    double[] van = new double[ENVS.length];
    for (int i = 0; i < ENVS.length; i++) {
      int idx = index(ENVS[i]);
      if (idx < 0) continue;
      @WESD@ d = ws.getWorldEnvironmentSpawnData(idx);
      if (d == null) continue;
      double nw = -1.0;
      try { @ESPP@ p = sp == null ? null : sp.getWorldEnvironmentSpawnParameters(idx); if (p != null) nw = p.getSpawnDensity(); } catch (Throwable t) { nw = -1.0; }
      ids[n] = ENVS[i]; data[n] = d; now[n] = nw; van[n] = base(idx);
      n++;
    }
    String[] ids2 = new String[n];
    @WESD@[] data2 = new @WESD@[n];
    double[] now2 = new double[n];
    double[] van2 = new double[n];
    System.arraycopy(ids, 0, ids2, 0, n);
    System.arraycopy(data, 0, data2, 0, n);
    System.arraycopy(now, 0, now2, 0, n);
    System.arraycopy(van, 0, van2, 0, n);
    String[] p2 = pick(ids2, data2, now2, van2, here, 10);
    for (int i = 0; i < p2.length; i++) l.add(p2[i]);
  }
  String[] a = new String[l.size()];
  for (int i = 0; i < a.length; i++) a[i] = (String) l.get(i);
  return a;
}""".replace("@SKX@", "%g" % SPAWN_SKEL_X).replace("@MONX@", "%g" % SPAWN_MON_X))
mspk.addInterface(pool.get("java.lang.Runnable"))
C(mspk, "public MobSpawnTask() { }")
M(mspk, r"""
public void run() {
  try { @PKG@.MobSpawn.tick(false); }
  catch (Throwable t) { @PKG@.MobLog.warnOnce("spawntask", "the spawn density check failed (logged once): " + t); }
}""")

'''
P.rep('''# ---------------------------------------------------------------- MobCmds: the command bodies (world thread: AbstractPlayerCommand runs there)''',
      MSPW + '''# ---------------------------------------------------------------- MobCmds: the command bodies (world thread: AbstractPlayerCommand runs there)''')

# ---------- 6. /mobs spawns (admin)
P.rep('''M(mc, r"""
public static String spaced(String s) { return s == null ? "" : s.replace('_', ' '); }""")''', '''M(mc, r"""
public static String spaced(String s) { return s == null ? "" : s.replace('_', ' '); }""")
# 0.1.21 (spawn1): /mobs spawns - this world's spawn data (the world thread: the command runs there), reads only
M(mc, r"""
public static String[] spawns(@ST@ store, @REF@ ref, @WLD@ world) {
  @WSPD@ ws = null;
  String here = null;          // fix: the environment the admin stands in (block environment, world thread)
  try {
    @TC@ tc = (@TC@) store.getComponent(ref, @TC@.getComponentType());
    if (tc != null && tc.getPosition() != null) {
      @VEC@ p = tc.getPosition();
      here = @PKG@.MobLevel.envId(@PKG@.MobLevel.blockEnv(world, (int) Math.floor(p.x), (int) Math.floor(p.y), (int) Math.floor(p.z)));
    }
  } catch (Throwable t) { here = null; }
  try { Object r = store.getResource(@WSPD@.getResourceType()); if (r instanceof @WSPD@) ws = (@WSPD@) r; } catch (Throwable t) { ws = null; }
  int cap = -1;
  try { cap = world.getGameplayConfig().getMaxEnvironmentalNPCSpawns(); } catch (Throwable t) { cap = -1; }
  return @PKG@.MobSpawn.lines(ws, world == null ? "this world" : world.getName(), cap, here);
}""")''')
P.rep('''cmd("MobsCmd", "mobs", "Mob levels: /mobs shows the level band where you stand", [],''',
      '''cmd("MobsSpawnsCmd", "spawns", "Admin: mob spawn density per zone and this world's spawn counts", [],
    X + "tellAll(pr, " + X + "spawns(store, ref, world));", perm=A)          # 0.1.21 (spawn1)
cmd("MobsCmd", "mobs", "Mob levels: /mobs shows the level band where you stand", [],''')
P.rep('''subs=("MobsInfoCmd", "MobsInspectCmd", "MobsSetCmd", "MobsPlateCmd", "MobsReloadCmd"))''',
      '''subs=("MobsInfoCmd", "MobsInspectCmd", "MobsSetCmd", "MobsPlateCmd", "MobsReloadCmd", "MobsSpawnsCmd"))''')

# ---------- 7. plugin: the 30 s check, the ready line, shutdown (vanilla densities back)
P.rep('''  catch (Throwable t) { @PKG@.MobLog.warn("could not schedule the prune of gone mobs: " + t); }
''', '''  catch (Throwable t) { @PKG@.MobLog.warn("could not schedule the prune of gone mobs: " + t); }
  // 0.1.21 (spawn1): the zone densities - first after 20 s (the spawner + assets are up), then every 30 s (an asset reload puts vanilla back)
  @PKG@.MobSpawn.STOPPING = false;
  try { @PKG@.MobSpawn.TASK = @HSV@.SCHEDULED_EXECUTOR.scheduleWithFixedDelay(new @PKG@.MobSpawnTask(), 20L, 30L, java.util.concurrent.TimeUnit.SECONDS); }
  catch (Throwable t) { @PKG@.MobLog.warn("could not schedule the spawn density check (" + t + ") - zones spawn at vanilla density this start"); }
''')
P.rep('''"; " + @PKG@.MobSecret.text() + "; /mobs;''', '''"; " + @PKG@.MobSecret.text() + "; " + @PKG@.MobSpawn.text() + "; /mobs;''')
P.rep('''  try { @PKG@.MobCfg.ON_HEALTH = null; } catch (Throwable t) { }
''', '''  try { @PKG@.MobCfg.ON_HEALTH = null; } catch (Throwable t) { }
  @PKG@.MobSpawn.STOPPING = true;          // 0.1.21 (fix): a 30 s run still going finishes first (tick is synchronized), later ones do nothing
  try { java.util.concurrent.ScheduledFuture f = @PKG@.MobSpawn.TASK; if (f != null) f.cancel(false); @PKG@.MobSpawn.TASK = null; @PKG@.MobSpawn.tick(true); } catch (Throwable t) { }   // 0.1.21
''')

# ---------- 8. the jar: the generated spawn files (asset pack)
P.rep('''man["IncludesAssetPack"] = False
B.assemble(jar, man, OUT)''', '''man["IncludesAssetPack"] = True          # 0.1.21 (spawn1): the generated spawn files (Server/NPC/Spawn/World/...)
man["Description"] += " 0.1.21: more mob spawns (skeletons x3 + camp skeleton types, other monsters x1.5; density per zone in Server Setup > Mobs > Spawns; /mobs spawns)."
assert all(_p.startswith(SPAWN_DIR) and _p.endswith(".json") for _p in SPAWN_FILES)
B.assemble(jar, man, OUT, extra_files=SPAWN_FILES)''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0 and P.s.count("makeClass(") == CLS0 + 2, "0.1.21: 2 classes (+ 1 command class through cmd()), no system, no command"
_i = P.s.index
assert _i("public static double[] counts(") < _i("public static String envLine(") < _i("public static String[] pick(") < _i("public static String[] lines(@WSPD@ ws") < _i("public static String[] spawns(@ST@ store") < _i('cmd("MobsSpawnsCmd"') < _i('cmd("MobsCmd"'), "0.1.21: methods before callers"
assert _i("public static synchronized int tick(boolean restore)") < _i("public static void changed(String key)") < _i("@PKG@.MobSpawn.TASK = @HSV@")
assert _i("public static volatile int SPAWN_Z") < _i("public static int pct(int zone)") and _i("public static String num2(") < _i("public static String envLine(")
P.finish()
print("wrote", P.dst)
