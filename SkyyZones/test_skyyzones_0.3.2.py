"""Harness for SkyyZones 0.3.2 (the big-tree fix, the natural gather types + Mig032, town / safe zones with no monster spawns, the Zone
Wand outline; tools/zones_0_3_2_patch.py).
Build first:  python tools/zones_0_3_2_patch.py && python SkyyZones/build_skyyzones_0.3.2.py
    python SkyyZones/test_skyyzones_0.3.2.py [--keep]
Phases (fresh child JVMs, tools/harness_kit.py: -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch; scratch tools/dev/scratch/zones032/zh):
  S   static   the patch re-runs to identical bytes; line endings kept; ONE new system (ZNoSpawn), no new command; the ready line
               '[SkyyZones] 0.3.2 ready'; EVERY wood piece of EVERY vanilla tree prefab (Assets.zip Server/Prefabs/Trees, 1138 prefabs) is a
               logs block now (the big autumn tree: Wood_Oak_Trunk_Full); the replay of the tree search on the real prefabs fits 9000 / 60,000;
               the new type patterns match only natural vanilla blocks; the wand tooltip
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.3.1 -> 0.3.2: exactly ZMig2 + ZNoSpawn added; the members that differ (EXPECT)
  F2  fakes    the 0.2.0 harness's engine stand-ins
  X   exec     EVERY 0.3.1 check again on 0.3.2 (the 0.3.1 harness's xrun, unchanged code) - the checks that changed BY DESIGN are listed
               in CHANGED (each one re-checked the new way below); then the 0.3.2 checks with REAL events on the same stand-ins (X032):
               dirt / stone / plants / crystals break + regrow (bedrock or open), a player block is never overwritten, built blocks refused,
               the big tree (Trunk_Full hit) fells, a multi-block part refused, F-picked flowers regrow (a failed pick dropped), town / safe /
               skyblock kinds + aliases, no-spawn rule + zones:fn:noSpawn, the wand: edge math, preview, draw / colours / caps / stop
  M   mig      Mig030 (unchanged) on synthetic files (the 0.3.1 harness's run_mig)
  M2  mig2     Mig032 on synthetic files: defaults rewritten, hand edits kept + logged, absent gather.types untouched, History first,
               Changes lines, marker, second run a no-op, CRLF / LF kept, a fresh folder = marker only
  D   live     start twice on a scratch COPY of the live mods folder: only Mig032's lines (+ History / Changes / marker), start 2 changes
               nothing (regen snapshots: only grown-back V lines older than 30 min may age out between the starts - a clock effect)
  AA  audit    engine-access audit
NOT COVERED (UNVERIFIED in game): the particle colours, the RefSystem removal of a real world spawn, sand / gravel falling, plants on
dug-out dirt popping off by physics.
"""
import os, sys, hashlib, importlib.util, subprocess, zipfile, re, json, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK
import skyybuild as B

VERSION, OLD = "0.3.2", "0.3.1"
PKG = "com.skyy.zones."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyZones-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyZones-%s.jar" % OLD)
GEN = os.path.join(HERE, "build_skyyzones_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyzones_%s.py" % OLD)
PATCH = os.path.join(ROOT, "tools", "zones_0_3_2_patch.py")
T31 = os.path.join(HERE, "test_skyyzones_0.3.1.py")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "zones032", "zh")))
LIVE = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods")
ASSETS = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
ADDED = ["ZMig2", "ZNoSpawn"]
EXPECT = {   # checked 2026-10-25 (the class compare 0.3.1 -> 0.3.2 of the first harness run; every member a planned change of tools/zones_0_3_2_patch.py:
 # CfgFile / CfgFn / CfgRows = the version + the 3 new rows; ZCmd5 / ZCmds / ZRegKit / ZStore / ZWand = the town, safe or skyblock words; ZRegen fallback = the audit ids of the new types)
    'CfgFile': ['~<clinit>'],
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'SkyyZonesPlugin': ['~m paths', '~m setup', '~m shutdown'],
    'ZCfg': ['+f NOSPAWN', '+f SAFE_ROLES', '+f WAND_PS', '+f WAND_SHOW', '+f WPSRC', '+f WPVAL', '+m checkWandParticles', '+m wandParticles', '~<clinit>', '~m loadCfg', '~m loadRegen', '~m loadTrees', '~m loadTypes'],
    'ZCmd5': ['~c '],
    'ZCmds': ['~m help', '~m info', '~m list', '~m region', '~m wand'],
    'ZEng': ['+f HELD', '+m fail0', '+m heldId', '~<clinit>'],
    'ZFn': ['+f NOSPAWN', '~<clinit>', '~m apply', '~m publish', '~m unpublish'],
    'ZGuard': ['~m gwhy', '~m handle'],
    'ZIndex': ['+m noSpawn', '~m at', '~m top'],
    'ZRegKit': ['~m customSet', '~m rulesSet'],
    'ZRegen': ['+m picked', '~m broke', '~m fallback'],
    'ZRegion': ['+m kind', '~m modeName', '~m modeOf', '~m summary'],
    'ZRules': ['~m area'],
    'ZStore': ['~m applyField', '~m create', '~m load', '~m parseAll', '~m parseOne', '~m start', '~m text'],
    'ZTick': ['+f WAND', '+f WAND_BOXES', '+f WAND_BOX_PTS', '+f WAND_MS', '+f WAND_NEAR', '+f WAND_SEL_PTS', '+m edges', '+m emit', '+m mine', '+m wand', '+m wandDraw', '~<clinit>', '~m enter', '~m forget', '~m tick'],
    'ZWand': ['+m preview', '~m hitAt'],
}
# the 0.3.1 checks whose expectation changed BY DESIGN in 0.3.2 (each re-checked the new way in X032 / static)
CHANGED = {
    "C: trees.properties written once with 45 / 60 / 90 s, 6000 blocks": "tree.maxBlocks default 9000 (Oak Stage 8 = 8,466 blocks)",
    "C: config.properties has zones.gatherWorlds (empty) + gather.types": "gather.types now has stone + the 12 natural types",
    "C: the tree fields read": "TREE_MAX 9000",
    "X A0: gathering world, no region = gather.types only": "stone + dirt now break on the island (Skyy 2026-10-25)",
    "X A0: a skyblock mine region adds stone": "dirt (Soil_Grass) breaks everywhere on the island now",
    "X A0: zones:fn:check answers the same layers": "Soil_Grass is 'allow' on the island now",
    "X A0: dirt / leaves (no crack) / a place refused on the island": "dirt breaks now (leaves + place still refused: X032)",
    "X A0: an ore on the island breaks (one drop) and regrows on its bedrock placeholder": "the dirt break before it now adds its own journal lines (the ore's D line is no longer the last; X032 re-checks an ore)",
    "X: /zones info in the town - 'Town - protected'": "the words are now 'Town - protected, no monster spawns'",
    "X: /zones list names the gathering world": "the words list the new types + 'towns + safe zones: no monster spawns'",
}


def m31():
    spec = importlib.util.spec_from_file_location("zones_t31", T31)
    m = importlib.util.module_from_spec(spec)
    a = list(sys.argv)
    spec.loader.exec_module(m)
    sys.argv[:] = a
    return m


M = m31()
# 0.3.2 changes one non-class entry besides the manifest: server.lang (the wand tooltip). harness_kit's compare allows only manifest.json
# there, so its one "non-class entries" line is re-checked against exactly this list (tools/harness_kit.py is shared - not edited)
NONCLASS = ["Server/Languages/en-US/server.lang", "manifest.json"]
_cmp0 = M._cmp0


def _cmp(out, jar, old_jar, pkg, expect, added, removed=()):
    _cmp0(out, jar, old_jar, pkg, expect, added, removed)
    d = json.load(open(out))
    want = "C: non-class entries changed: got %r, want ['manifest.json']" % NONCLASS
    if want in d["fails"]:
        d["fails"].remove(want)
        d["ok"] += 1
        d["notes"].append("C: non-class entries changed = exactly the planned %s" % NONCLASS)
    json.dump(d, open(out, "w"), indent=1)


HK.run_compare = _cmp
EXTRA_BLOCKS = ["Plant_Flower_Common_Red", "Rock_Crystal_Red_Medium", "Rubble_Stone", "Soil_Clay_Brick", "Rock_Stone_Brick", "Plant_Leaves_Autumn_X"]
EXTRA_BLOCKS = [b for b in EXTRA_BLOCKS if not b.endswith("_X")]


def logs_patterns():
    g = open(GEN, encoding="utf8").read()
    m = re.search(r'\("logs", "([^"]+)"\)', g)
    return m.group(1).split(",")


def gmatch(pats, i):
    return any(re.match("^" + re.escape(p).replace(r"\*", ".*") + "$", i) for p in pats)


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, "rb").read()
    o = open(GEN_OLD, "rb").read()
    K.check(g.startswith(b'"""SkyyZones 0.3.2') and g.count(b'VERSION = "0.3.2"') == 1, "S header + VERSION")
    K.check(g.count(b"registerSystem(") == o.count(b"registerSystem(") + 1 and b"registerSystem(new @PKG@.ZNoSpawn())" in g, "S exactly one new system (ZNoSpawn)")
    K.check(g.count(b"registerCommand(") == o.count(b"registerCommand("), "S no new command")
    K.check((b"\r\n" in g) == (b"\r\n" in o), "S line endings kept")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    src = open(PATCH, encoding="utf8").read().replace('os.path.join(ROOT, "SkyyZones", "build_skyyzones_0.3.2.py")', repr(os.path.join(d, "b.py")))
    open(os.path.join(d, "p.py"), "w", encoding="utf8").write(src.replace("ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))", "ROOT = %r" % ROOT))
    p = subprocess.run([sys.executable, os.path.join(d, "p.py")], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(os.path.join(d, "b.py"), "rb").read() == g, "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    with zipfile.ZipFile(jar) as z:
        pl = z.read("com/skyy/zones/SkyyZonesPlugin.class")
        names = z.namelist()
        lang = z.read("Server/Languages/en-US/server.lang").decode("utf8")
    K.check(b"[SkyyZones] 0.3.2 ready - " in pl, "S the ready line '[SkyyZones] 0.3.2 ready' (smoke_test.py)")
    K.check(not any(n.lower().endswith(".ui") for n in names), "S no .ui file in the jar")
    lk = dict(l.split("=", 1) for l in lang.splitlines() if "=" in l)
    wd = lk.get("server.items.Skyy_Zones_Wand.description", "")
    K.check("Hold it:" in wd and "town (or safe)" in wd and wd == lk.get("items.Skyy_Zones_Wand.description"), "S the wand tooltip: hold it + town / safe (both prefixes): %r" % wd[:160])
    # ---- THE BIG TREE on the real vanilla prefabs: every wood block of every tree prefab is a logs block now; 0.3.1 missed Trunk_Full
    lp = logs_patterns()
    lp31 = "Wood_*_Trunk,Wood_*_Branch_Corner,Wood_*_Branch_Long,Wood_*_Branch_Short,Wood_*_Roots".split(",")
    miss, miss31, autumn = collections.Counter(), collections.Counter(), []
    with zipfile.ZipFile(ASSETS) as az:
        pre = [n for n in az.namelist() if n.startswith("Server/Prefabs/Trees/") and n.endswith(".prefab.json")]
        items = set(n.rsplit("/", 1)[1][:-5] for n in az.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
        for n in pre:
            bl = json.loads(az.read(n)).get("blocks", [])
            wood = [b_["name"] for b_ in bl if b_.get("name", "").startswith("Wood_")]
            for w_ in wood:
                if not gmatch(lp, w_):
                    miss[w_] += 1
                if not gmatch(lp31, w_):
                    miss31[w_] += 1
            if "/Autumn/" in n:
                autumn.append((n.rsplit("/", 1)[1], len(bl), sum(1 for w_ in wood if w_.endswith("_Trunk_Full")), len(wood)))
    K.check(len(pre) > 1000 and not miss, "S the big tree: every wood piece of the %d vanilla tree prefabs is a logs block (missing: %s)" % (len(pre), dict(miss.most_common(5))))
    K.check(miss31 and all(k.endswith("_Trunk_Full") for k in miss31), "S the root cause: 0.3.1's logs line missed exactly the Trunk_Full pieces (%d kinds, e.g. %s)" % (len(miss31), list(miss31)[:3]))
    K.check(autumn and all(f_ > 0 for _n, _b, f_, _w in autumn if "Stage3" in _n), "S the autumn trees (orange leaves) are oak wood with Trunk_Full trunks: %s" % autumn[:4])
    # ---- the tree-search replay (tools/dev/scratch/zones032/sim/treesim.py logic) at the new defaults
    sim = os.path.join(ROOT, "tools", "dev", "scratch", "zones032", "sim", "treesim.py")
    if os.path.isfile(sim):
        r = subprocess.run([sys.executable, "-I", sim, ASSETS, "9000"], capture_output=True, text=True)
        K.check(r.returncode == 0 and "refused 0" in r.stdout, "S replay of ZFell.search on every vanilla tree prefab at tree.maxBlocks 9000: none refused (%s)" % r.stdout.splitlines()[:1])
    else:
        K.notes.append("S: tree replay script not present (scratch gone) - covered by the build's TreeWood check")
    # ---- the new patterns only take natural vanilla blocks (the build asserts the same; here from the generated TYPES text)
    gs = open(GEN, encoding="utf8").read()
    pats = dict(re.findall(r'\(\'(rock|dirt|clay|clay2|sand|ice|rubble|crystals|cave|plants|coral|mushrooms)\', \'([^\']+)\'\)', gs))
    K.check(len(pats) == 12 and all(len(v) <= 200 for v in pats.values()), "S 12 new types, each line under the 200-character cell: %s" % sorted(pats))
    took = dict((t, sorted(i for i in items if gmatch(v.split(","), i))) for t, v in pats.items())
    bad = [(t, i) for t, l in took.items() for i in l if re.search(r"_(Half|Stairs|Brick|Smooth|Cobble|Roof|Pillar|Tilled)(_|$)|Mushroom_Block|Boomshroom|Planks", i)]
    K.check(not bad and all(took[t] for t in took), "S no new type takes a built block, each takes some: %s" % bad[:5])
    K.check("Rock_Crystal_Red_Medium" in took["crystals"] and "Soil_Grass" in took["dirt"] and "Plant_Flower_Common_Red" in took["plants"]
            and "Rubble_Stone" in took["rubble"] and "Plant_Crop_Mushroom_Glowing_Red" in took["mushrooms"], "S Skyy's blocks: crystals, grass, flowers, rubble, mushrooms are listed")
    K.notes.append("S type sizes: %s" % dict((t, len(l)) for t, l in took.items()))
    K.save()


def _src(fn_name, end_marker, edits):
    s = open(T31, encoding="utf8").read()
    a = s.index("def %s(" % fn_name)
    b = s.index(end_marker, a)
    f = s[a:b]
    for old, new in edits:
        assert f.count(old) == 1, (fn_name, old)
        f = f.replace(old, new)
    return f


def xns():
    g = dict(vars(M))
    g["X032"] = X032
    eng = _src("engine", "\ndef run_exec(", [('"Ore_Lead_Sandstone_SkyWynn", "Rock_Gem_Ruby", "Skyy_Scaffold"]',
                                               '"Ore_Lead_Sandstone_SkyWynn", "Rock_Gem_Ruby", "Skyy_Scaffold"] + %r' % EXTRA_BLOCKS)])
    xr = _src("xrun", "# ---------------------------------------------------------------------------------------------------------------- M: Mig030",
              [("    Cfg.GATES_ON = True\n    Rgn.shutdown()\n    Eng.API = None\n", "    Cfg.GATES_ON = True\n    X032(K, E, locals())\n    Rgn.shutdown()\n    Eng.API = None\n")])
    exec(compile(eng, T31 + ":engine", "exec"), g)
    exec(compile(xr, T31 + ":xrun", "exec"), g)
    return g


def run_exec(out, jar, scratch, _home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, os.path.join(scratch, "fake2")], verify=True)
    T = M.t20()
    T.SCRATCH = scratch
    g = xns()
    try:
        E = g["engine"](K, T, scratch)
        g["xrun"](K, E, T, scratch)
    except Exception as e:
        import traceback
        traceback.print_exc()
        K.check(False, "X: run crashed: %s" % str(e)[:500])
    # the 0.3.1 checks that changed by design -> notes (each must have failed: a check that still passes was mislabelled)
    keep, seen = [], set()
    for f in K.fails:
        hit = [k for k in CHANGED if f.startswith(k)]
        if hit:
            seen.add(hit[0])
            K.notes.append("X changed by design (%s): %s" % (CHANGED[hit[0]], f[:120]))
        else:
            keep.append(f)
    K.fails = keep
    K.ok += len(seen)
    K.check(seen == set(CHANGED), "X: exactly the planned 0.3.1 checks changed (%d): not seen %s" % (len(CHANGED), sorted(set(CHANGED) - seen)))
    K.save()


def X032(K, E, L):
    """the 0.3.2 checks on the 0.3.1 harness's stand-ins (L = xrun's locals: api, fire, mine, drain, tick, players, Sto, Rgn, ...)"""
    from jpype import JClass, JArray, JInt, JLong, JImplements, JOverride, JString
    P = lambda n: JClass(PKG + n)
    api, fire, mine, drain, tick, Skyy, WORLD = L["api"], L["fire"], L["mine"], L["drain"], L["tick"], L["Skyy"], M.WORLD
    Cfg, Sto, Rgn, Dep, Rules, Fn, Tick, Wnd, Eng = (P(n) for n in ("ZCfg", "ZStore", "ZRegen", "ZDep", "ZRules", "ZFn", "ZTick", "ZWand", "ZEng"))
    NS, Reg = P("ZNoSpawn"), P("ZRegion")
    notes, waiting, perms, jfield, BT, U = L["notes"], L["waiting"], L["perms"], E["jfield"], E["BT"], E["U"]
    Cfg.ABUSE_ON = False
    Cfg.GATES_ON = False
    Cfg.JITTER = 0.0
    Cfg.SPEED = 1.0
    tick(int(Dep.CLOCK) + 3600000)
    now = int(Dep.CLOCK) + 1000
    Dep.CLOCK = JLong(now)
    notes()
    dec = lambda x, y, z, i: int(Rules.decide(Sto.INDEX, WORLD, True, x, y, z, Rules.BREAK, i))
    ALLOW, NOT_RES, DENY = int(Rules.ALLOW), int(Rules.NOT_RES), int(Rules.DENY)
    # ---- the island layer: natural blocks break, built ones do not
    nat = ["Rock_Stone", "Soil_Grass", "Wood_Oak_Trunk_Full", "Plant_Flower_Common_Red", "Rubble_Stone", "Rock_Crystal_Red_Medium",
           "Plant_Crop_Mushroom_Glowing_Red", "Soil_Clay_Red", "Soil_Sand", "Rock_Ice", "Plant_Moss_Cave_Blue", "Plant_Coral_Bush_Red", "Rock_Sandstone_Red"]
    built = ["Rock_Stone_Brick", "Soil_Clay_Brick", "Wood_Oak_Planks", "Soil_Dirt_Tilled", "Plant_Leaves_Oak", "Plant_Crop_Mushroom_Block_Red", "Rock_Stone_Half"]
    K.check([dec(900, 90, 900, i) for i in nat] == [ALLOW] * len(nat) and [dec(900, 90, 900, i) for i in built] == [NOT_RES] * len(built),
            "X032 the island: stone, dirt, Trunk_Full, flowers, rubble, crystals, mushrooms, clay, sand, ice, moss, coral, red sandstone break; bricks, planks, tilled soil, leaves, giant mushroom parts, halves do not")
    want = ["stone", "dirt", "logs", "plants", "rubble", "crystals", "mushrooms", "clay2", "sand", "ice", "cave", "coral", "rock"]
    got = [str(Rules.resType(Sto.INDEX, WORLD, 900, 90, 900, i)) for i in nat]
    K.check(got == want, "X032 the type of each: %s" % got)
    # ---- dirt: bedrock placeholder, back after 8 s; a player block placed meanwhile is never overwritten
    c1 = mine(Skyy, WORLD, 900, 90, 900, block="Soil_Grass")
    drain()
    d1 = Rgn.at(WORLD, 900, 90, 900)
    K.check(not c1 and d1 is not None and str(d1.type) == "dirt" and int(d1.due) == now + 8000 and api.wb[(WORLD, 900, 90, 900)] == "Rock_Bedrock",
            "X032 dirt breaks (vanilla drop), Rock_Bedrock meanwhile, back after 8 s")
    c2 = mine(Skyy, WORLD, 901, 90, 900, block="Rock_Stone")
    drain()
    K.check(not c2 and str(Rgn.at(WORLD, 901, 90, 900).type) == "stone" and int(Rgn.at(WORLD, 901, 90, 900).due) == now + 3000, "X032 stone breaks on the island, back after 3 s")
    c3 = mine(Skyy, WORLD, 902, 90, 900, block="Plant_Flower_Common_Red")
    drain()
    d3 = Rgn.at(WORLD, 902, 90, 900)
    K.check(not c3 and d3 is not None and str(d3.ph) == "Empty" and api.wb[(WORLD, 902, 90, 900)] == "Empty" and int(d3.due) == now + 20000,
            "X032 a flower breaks; the spot stays OPEN (placeholder Empty, no bedrock), back after 20 s")
    c4 = mine(Skyy, WORLD, 903, 90, 900, block="Rock_Crystal_Red_Medium")
    drain()
    K.check(not c4 and str(Rgn.at(WORLD, 903, 90, 900).type) == "crystals" and int(Rgn.at(WORLD, 903, 90, 900).due) == now + 30000, "X032 Skyy's cave crystals break, back after 30 s (open spot)")
    c5 = mine(Skyy, WORLD, 905, 90, 900)
    drain()
    K.check(not c5 and Rgn.at(WORLD, 905, 90, 900) is not None and str(Rgn.at(WORLD, 905, 90, 900).type) == "copper" and api.wb[(WORLD, 905, 90, 900)] == "Rock_Bedrock" and L["jl"](WORLD)[-1].startswith("D 905 90 900 Ore_Copper_Stone copper "),
            "X032 an ore on the island still breaks (one drop) + regrows on bedrock (the 0.3.1 A0 check, re-done with its own journal line last)")
    mine(Skyy, WORLD, 904, 90, 900, block="Soil_Grass")
    drain()
    api.wb[(WORLD, 904, 90, 900)] = "Wood_Oak_Planks"   # someone's block in the spot meanwhile
    tick(now + 31000)
    K.check(api.wb[(WORLD, 900, 90, 900)] == "Soil_Grass" and api.wb[(WORLD, 901, 90, 900)] == "Rock_Stone" and api.wb[(WORLD, 902, 90, 900)] == "Plant_Flower_Common_Red"
            and api.wb[(WORLD, 903, 90, 900)] == "Rock_Crystal_Red_Medium" and not any(waiting(WORLD, 900 + i, 90, 900) for i in range(4)),
            "X032 all grow back (dirt, stone, flower, crystal)")
    K.check(api.wb[(WORLD, 904, 90, 900)] == "Wood_Oak_Planks", "X032 a regrow never overwrites a block put in the spot meanwhile (left, entry dropped)")
    now = now + 40000
    Dep.CLOCK = JLong(now)
    # ---- built blocks + a multi-block part refused
    notes()
    api.wb[(WORLD, 906, 90, 900)] = "Rock_Stone_Brick"
    K.check(fire(Skyy, "break", 906, 90, 900, block="Rock_Stone_Brick") and notes()[0] == ("Skyy", "You can only gather the marked resource blocks here."),
            "X032 a stone brick (built) is refused with the red note")
    api.wb[(WORLD, 907, 90, 900)] = "Soil_Grass"
    api.state[(WORLD, 907, 90, 900)] = [0, 1]
    cf = fire(Skyy, "break", 907, 90, 900, block="Soil_Grass")
    K.check(cf and not waiting(WORLD, 907, 90, 900) and notes()[0] == ("Skyy", "Break it at its base."),
            "X032 a part of a bigger block (filler) is refused 'Break it at its base.' (0.3.1: broke with NO regrow)")
    api.state.pop((WORLD, 907, 90, 900))
    # ---- THE BIG TREE: a giant autumn oak (Trunk_Full trunk + autumn leaves) fells from a Trunk_Full hit
    cells = {}
    for dy in range(8):
        for dx, dz in ((0, 0), (1, 0), (0, 1), (1, 1)):
            cells[(950 + dx, 91 + dy, 950 + dz)] = "Wood_Oak_Trunk_Full" if (dx + dz + dy) % 2 == 0 else "Wood_Oak_Trunk"
    for dx in range(-3, 5):
        for dz in range(-3, 5):
            for dy in (7, 8, 9):
                k_ = (950 + dx, 91 + dy, 950 + dz)
                if k_ not in cells:
                    cells[k_] = "Plant_Leaves_Autumn"
    for (x_, y_, z_), v_ in cells.items():
        api.wb[(WORLD, x_, y_, z_)] = v_
    ct = fire(Skyy, "break", 950, 91, 950, block="Wood_Oak_Trunk_Full")
    t_ = Rgn.treeAt(WORLD, 950, 91, 950)
    K.check(not ct and t_ is not None and int(t_.shape.n) == len(cells), "X032 THE BIG TREE: a hit on its Wood_Oak_Trunk_Full fells the whole autumn oak (%d of %d blocks in the shape; 0.3.1: red 'only the marked resource blocks')" % (int(t_.shape.n) if t_ is not None else -1, len(cells)))
    # ---- F-pick of a flower (vanilla Gathering Harvest): recorded like a break, regrows; a failed pick is dropped
    BGA = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockGathering")
    HDT = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.HarvestingDropType")
    btm = BT.getAssetMap()
    fb = btm.getAsset(JInt(int(btm.getIndex("Plant_Flower_Common_Red"))))
    g_ = U.allocateInstance(BGA.class_)
    jfield(BGA, "harvest").set(g_, HDT(None, "Drops_Flower"))
    jfield(BT, "gathering").set(fb, g_)
    api.wb[(WORLD, 910, 90, 900)] = "Plant_Flower_Common_Red"
    cp = fire(Skyy, "use", 910, 90, 900, block="Plant_Flower_Common_Red")
    dp = Rgn.at(WORLD, 910, 90, 900)
    K.check(not cp and dp is not None and int(dp.state) == 3 and str(dp.ph) == "Empty" and str(dp.type) == "plants", "X032 an F-pick of a flower is recorded (state 3, open spot)")
    api.wb[(WORLD, 910, 90, 900)] = "Empty"   # the engine's harvest removed it
    api.wb[(WORLD, 911, 90, 900)] = "Plant_Flower_Common_Red"
    fire(Skyy, "use", 911, 90, 900, block="Plant_Flower_Common_Red")   # this pick fails (full inventory): the flower stays
    tick(now + 1500)
    K.check(waiting(WORLD, 910, 90, 900) and not waiting(WORLD, 911, 90, 900) and api.wb[(WORLD, 911, 90, 900)] == "Plant_Flower_Common_Red",
            "X032 ... 1 s later: the picked one waits, the failed pick is dropped (the flower untouched)")
    tick(now + 21000)
    K.check(api.wb[(WORLD, 910, 90, 900)] == "Plant_Flower_Common_Red" and not waiting(WORLD, 910, 90, 900), "X032 ... the picked flower grows back after 20 s")
    now = now + 30000
    Dep.CLOCK = JLong(now)
    # ---- kinds: town / safe / skyblock, aliases, words
    K.check([int(Reg.modeOf(s_)) for s_ in ("full", "town", "TOWN", "skyblock", "safe", "nope")] == [0, 0, 0, 1, 2, -1], "X032 kinds: full = town 0, skyblock 1, safe 2")
    r1 = str(Sto.create("town32", WORLD, "town", JArray(JInt)([960, 60, 960, 980, 140, 980]), "Skyy"))
    r2 = str(Sto.create("camp", WORLD, "safe", JArray(JInt)([1000, 60, 1000, 1020, 140, 1020]), "Skyy"))
    K.check("(full)" in r1 and "no monsters spawn" in r1 and "(safe)" in r2 and "Gathering works there" in r2, "X032 /zones region create <n> town | safe: %s | %s" % (r1[:90], r2[:90]))
    tn, sf = Sto.get("town32"), Sto.get("camp")
    K.check(str(tn.modeName()) == "full" and str(sf.modeName()) == "safe" and str(tn.kind()) == "town" and "(safe," in str(sf.summary()),
            "X032 the file keeps 'full' for towns (a 0.3.1 rollback reads them) and 'safe'; summaries say town / safe")
    K.check(dec(970, 90, 970, "Rock_Stone") == DENY and dec(1010, 90, 1010, "Rock_Stone") == ALLOW and dec(1010, 90, 1010, "Rock_Stone_Brick") == NOT_RES
            and Sto.INDEX.top(WORLD, 1010, 90, 1010) is None and Sto.INDEX.at(WORLD, 1010, 90, 1010).isEmpty(),
            "X032 town: nothing breaks; safe: gathering as outside it (stone yes, bricks no) - not a protection layer")
    a_t, a_s = str(Rules.area(Sto.INDEX, WORLD, 970, 90, 970)), str(Rules.area(Sto.INDEX, WORLD, 1010, 90, 1010))
    K.check(a_t.startswith("Town - protected, no monster spawns") and a_s.startswith("Safe zone - gathering, no monster spawns"), "X032 /zones info area words: %s | %s" % (a_t, a_s))
    cs_ = mine(Skyy, WORLD, 1010, 90, 1010, block="Soil_Grass")
    drain()
    K.check(not cs_ and waiting(WORLD, 1010, 90, 1010), "X032 in a safe zone dirt breaks + regrows like outside")
    # ---- no monster spawns: the rule
    harm = str(Cfg.SAFE_ROLES).strip(",").split(",")[0]
    blk = lambda x, y, z, sp=True, env=3, role="Skeleton_Soldier", att="HOSTILE": NS.blocked(WORLD, float(x), float(y), float(z), sp, env, role, att)
    MINI = -2147483648
    b_t, b_s = blk(970, 90, 970), blk(1010.5, 90, 1010.5)
    K.check(b_t is not None and str(b_t.id) == "town32" and b_s is not None and str(b_s.id) == "camp", "X032 no-spawn: a natural hostile spawn in a town / safe zone is stopped")
    K.check(blk(900, 90, 900) is None and blk(310, 90, 310) is None, "X032 ... outside them (and in a skyblock mine region) it spawns")
    K.check(blk(970, 90, 970, sp=False) is None and blk(970, 90, 970, env=MINI) is None and blk(970, 90, 970, att="NEUTRAL") is None
            and blk(970, 90, 970, role=harm) is None and blk(970, 90, 970, role=harm.upper()) is None,
            "X032 ... never a chunk load (mobs that walked in stay), a code / marker spawn (no environment), a neutral mob, a harmless animal (%s)" % harm)
    Cfg.NOSPAWN = False
    off_ = blk(970, 90, 970)
    Cfg.NOSPAWN = True
    K.check(off_ is None, "X032 ... the Server Setup row off = nothing stopped")
    fn2 = Fn(2)
    oa = lambda x, z: fn2.apply(JArray(JClass("java.lang.Object"))([WORLD, JInt(x), JInt(90), JInt(z)]))
    Fn.publish()
    pub_ = Cfg.bridge().get("zones:fn:noSpawn")
    Fn.unpublish()
    K.check(bool(oa(970, 970)) is True and bool(oa(1010, 1010)) is True and bool(oa(900, 900)) is False and pub_ is not None and str(pub_.getClass().getName()).endswith("ZFn"),
            "X032 zones:fn:noSpawn {world, x, y, z} -> Boolean (published for SkyyMobs / WorldGen later)")
    # ---- the wand: edge math
    def corners(b):
        return set((x_, y_, z_) for x_ in (b[0], b[3]) for y_ in (b[1], b[4]) for z_ in (b[2], b[5]))
    ok_e = True
    for b in ([0, 0, 0, 1, 1, 1], [0, 0, 0, 10, 5, 3], [-5, 60, -5, 300, 140, 700], [0, 0, 0, 1000, 300, 1000], [7, 7, 7, 8, 30, 8]):
        for mx in (32, 40, 80, 160):
            pts = list(Tick.edges(JArray(JInt)(b), mx))
            tri = [(pts[i], pts[i + 1], pts[i + 2]) for i in range(0, len(pts), 3)]
            on = all(sum(1 for c_, lo, hi in ((t[0], b[0], b[3]), (t[1], b[1], b[4]), (t[2], b[2], b[5])) if c_ in (lo, hi)) >= 2
                     and b[0] <= t[0] <= b[3] and b[1] <= t[1] <= b[4] and b[2] <= t[2] <= b[5] for t in tri)
            if not (len(tri) <= mx and corners(b) <= set(tri) and on):
                ok_e = False
                K.notes.append("edges %s max %d: %d points, corners %s, on edges %s" % (b, mx, len(tri), corners(b) <= set(tri), on))
    K.check(ok_e, "X032 wand edge math: every corner, every point on one of the 12 edges, never more than the cap (5 boxes x 4 caps)")
    K.check(len(list(Tick.edges(JArray(JInt)([0, 0, 0, 1, 1, 1]), 20))) == 0, "X032 ... a cap under 32 draws nothing (no overflow)")
    # ---- the wand: preview
    u = Skyy["u"]
    Wnd.SEL.remove(u)
    K.check(Wnd.preview(u, WORLD) is None, "X032 no corner yet: nothing to outline")
    Wnd.hitAt(u, WORLD, 1000, 90, 1000, JLong(now))
    K.check(list(Wnd.preview(u, WORLD)) == [1000, 90, 1000, 1000, 90, 1000], "X032 corner A alone: that block")
    Wnd.hitAt(u, WORLD, 1004, 95, 1002, JLong(now + 1000))
    K.check(list(Wnd.preview(u, WORLD)) == [1000, 90, 1000, 1004, 95, 1002] and Wnd.preview(u, M.PLAIN) is None, "X032 A + B: the box (only in that world)")
    # ---- the wand: draw, colours, caps, every 1 s, stops when the wand leaves the hand
    held = {"id": "Skyy_Zones_Wand"}

    @JImplements("java.util.function.Function")
    class Held(object):
        @JOverride
        def apply(self, r):
            return held["id"]
    seen = []
    api.particle = lambda id_, x, y, z, to, st: seen.append((str(id_), float(x), float(y), float(z), to.size()))
    Eng.HELD = Held()
    perms[(str(u), "skyyzones.admin")] = True
    Sto.create("gath32", WORLD, "skyblock", JArray(JInt)([1030, 60, 1000, 1040, 99, 1010]), "Skyy")
    Sto.set("gath32", "types", "logs", "Skyy")
    Sto.create("mine32", WORLD, "skyblock", JArray(JInt)([1040, 60, 1030, 1045, 99, 1035]), "Skyy")
    Sto.set("mine32", "types", "stone,iron", "Skyy")
    Sto.create("far32", WORLD, "town", JArray(JInt)([2000, 60, 2000, 2010, 99, 2010]), "Skyy")
    Tick.WAND.clear()
    Cfg.WPSRC = Cfg.WAND_PS   # the test JVM has no particle assets: take the 5 ids as they are (in game checkParticle looks them up)
    Cfg.WPVAL = JArray(JString)(str(Cfg.WAND_PS).split(","))
    n1 = int(Tick.wand(None, u, Skyy["ref"], Skyy["st"], WORLD, 1005, 1005, JLong(now)))
    ids = collections.Counter(s_[0] for s_ in seen)
    K.check(n1 == len(seen) and n1 > 0 and all(s_[4] == 1 for s_ in seen), "X032 holding the wand draws %d particles, to that player only" % n1)
    K.check(ids["Alerted"] > 0 and ids["Beam_Heal_Green"] > 0 and ids["Potion_Signature_Burst"] > 0 and ids["Potion_Morph_Burst"] > 0 and ids["Beam_Heal_Red"] > 0,
            "X032 ... the selection yellow + each kind its own colour (town red, safe green, skyblock cyan, mine white): %s" % dict(ids))
    K.check(ids["Alerted"] <= 80 and n1 <= 80 + 4 * 40 and not any(s_[1] >= 2000 for s_ in seen), "X032 ... caps: selection <= 80, <= 4 region boxes x 40; a town 1000 blocks away is not drawn")
    del seen[:]
    K.check(int(Tick.wand(None, u, Skyy["ref"], Skyy["st"], WORLD, 1005, 1005, JLong(now + 500))) == 0 and not seen, "X032 ... at most once a second")
    K.check(int(Tick.wand(None, u, Skyy["ref"], Skyy["st"], WORLD, 1005, 1005, JLong(now + 1000))) > 0, "X032 ... again after 1 s")
    del seen[:]
    held["id"] = "Tool_Pickaxe_Iron"
    K.check(int(Tick.wand(None, u, Skyy["ref"], Skyy["st"], WORLD, 1005, 1005, JLong(now + 2000))) == -1 and not seen and not Tick.WAND.containsKey(u),
            "X032 STOP: the wand out of the hand - nothing more is drawn, the player is forgotten")
    held["id"] = None
    K.check(int(Tick.wand(None, u, Skyy["ref"], Skyy["st"], WORLD, 1005, 1005, JLong(now + 3000))) == -1 and not seen, "X032 ... an empty hand too")
    held["id"] = "Skyy_Zones_Wand"
    perms[(str(u), "skyyzones.admin")] = False
    K.check(int(Tick.wand(None, u, Skyy["ref"], Skyy["st"], WORLD, 1005, 1005, JLong(now + 4000))) == -2 and not seen, "X032 ... a non-admin holding a wand sees nothing")
    perms[(str(u), "skyyzones.admin")] = True
    Cfg.WAND_PS = "Alerted,No_Such_Particle_X"
    ps_ = [str(x) for x in Cfg.wandParticles()]
    K.check(len(ps_) == 5 and ps_[1] in ("No_Such_Particle_X", "Alerted") and ps_[2] == "Alerted", "X032 a short / bad wand.particles row falls back to Alerted per slot: %s" % ps_)
    K.check(Cfg.checkWandParticles(JString("wand.particles"), "a,b") is not None, "X032 Server Setup refuses a wand.particles row without 5 ids")
    Cfg.WAND_PS = "Alerted,Beam_Heal_Red,Beam_Heal_Green,Potion_Signature_Burst,Potion_Morph_Burst"
    Eng.HELD = None
    del api.particle
    for r_ in ("town32", "camp", "gath32", "mine32", "far32"):
        Sto.delete(r_, "Skyy")
    Cfg.ABUSE_ON = True
    Cfg.GATES_ON = True


def run_mig2(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Mig, Cfg, Rows, Hist, Log = (JClass(PKG + n) for n in ("ZMig2", "ZCfg", "CfgRows", "CfgHist", "CfgLog"))
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyZones")
    Paths = JClass("java.nio.file.Paths")
    gen = open(GEN, encoding="utf8").read()
    L31 = "Wood_*_Trunk,Wood_*_Branch_Corner,Wood_*_Branch_Long,Wood_*_Branch_Short,Wood_*_Roots"
    L32 = "Wood_*_Trunk,Wood_*_Trunk_Full,Wood_*_Branch_Corner,Wood_*_Branch_Long,Wood_*_Branch_Short,Wood_*_Roots"
    GT31 = "copper,iron,gold,silver,thorium,cobalt,adamantite,mithril,onyxium,lead,chromium,slag,titanium,gem,logs,crops"
    new_types = ["rock", "dirt", "clay", "clay2", "sand", "ice", "rubble", "crystals", "cave", "plants", "coral", "mushrooms"]
    t31 = "# types\r\ntype.stone=Rock_Stone\r\ntype.logs=%s\r\ntype.crops=Plant_Crop_*_Block\r\n" % L31
    r31 = "# regen\r\nregen.enabled=true\r\nregrow.stone=3,Rock_Bedrock\r\nregrow.logs=60,none\r\n"
    c31 = "zones.on=true\r\nzones.worlds=skywynn_zones2\r\n\r\nzones.gatherWorlds=skywynn_zones2\r\n"   # Skyy's file: NO gather.types line
    x31 = "tree.sec1=45\r\ntree.maxBlocks=6000\r\ntree.clearSec=3\r\n"

    def setup(name, files):
        d = os.path.join(scratch, "m2", name, "Skyy_SkyyZones")
        os.makedirs(d, exist_ok=True)
        for f, t in files.items():
            if t is not None:
                open(os.path.join(d, f), "wb").write(t.encode("latin-1"))
        Rows.HOME = None
        Hist.DIR = None
        Log.FILE = None
        return d
    rb = lambda d, f: open(os.path.join(d, f), "rb").read().decode("latin-1")
    # 1: Skyy's 0.3.1 files (CRLF): logs rewritten, 12 types + 12 regrow rows appended, no gather.types line -> untouched, tree 6000 -> 9000
    d = setup("a", {"types.properties": t31, "regen.properties": r31, "config.properties": c31, "trees.properties": x31})
    r = str(Mig.run(Paths.get(d)))
    nt, nr, nc, nx = (rb(d, f) for f in ("types.properties", "regen.properties", "config.properties", "trees.properties"))
    K.check(nt.startswith(t31.replace(L31, L32)) and all(("\r\ntype.%s=" % t) in nt for t in new_types) and "\r\ntype.crystals=Rock_Crystal_*\r\n" in nt
            and nt.count(str(Mig.HEAD)) == 1 and "\n" not in nt.replace("\r\n", ""), "M2 types.properties: logs 0.3.1 default -> + Trunk_Full, the 12 types appended under one comment, CRLF kept")
    K.check(nr.startswith(r31) and "\r\nregrow.dirt=8,Rock_Bedrock\r\n" in nr and "\r\nregrow.plants=20,Empty\r\n" in nr and "\r\nregrow.crystals=30,Empty\r\n" in nr
            and all(("\r\nregrow.%s=" % t) in nr for t in new_types), "M2 regen.properties: the 12 regrow rows appended (bedrock / Empty)")
    K.check(nc == c31, "M2 config.properties without a gather.types line is NOT touched (the new built-in default applies)")
    K.check(nx == x31.replace("tree.maxBlocks=6000", "tree.maxBlocks=9000"), "M2 trees.properties: tree.maxBlocks 6000 -> 9000, every other byte the same")
    hist = os.path.join(d, "config-history")
    baks = sorted(os.listdir(hist)) if os.path.isdir(hist) else []
    K.check(sum(1 for b in baks if b.endswith(".bak")) == 3 and not any("config.properties" in b for b in baks), "M2 History copies of the 3 changed files first (config not changed): %s" % baks)
    lg = open(os.path.join(d, "config-changes.log"), encoding="utf8").read().splitlines()
    keys = [l.split("\t")[4] for l in lg]
    K.check(len(lg) == 1 + 12 + 12 + 1 and "type[logs]" in keys and "type[crystals]" in keys and "regrow[plants]" in keys and "tree.maxBlocks" in keys
            and all(l.split("\t")[1] == "SkyyZones 0.3.2" and l.split("\t")[3] == "migration" and l.endswith("\tok") for l in lg),
            "M2 one Changes line per key (table keys + tree.maxBlocks, Undo): %d lines" % len(lg))
    K.check(os.path.isfile(os.path.join(d, "migrate-0.3.2.done")) and "26 lines" in r, "M2 the marker + the summary: %s" % r[:120])
    b1 = [rb(d, f) for f in ("types.properties", "regen.properties", "config.properties", "trees.properties")]
    K.check(str(Mig.run(Paths.get(d))) == "" and [rb(d, f) for f in ("types.properties", "regen.properties", "config.properties", "trees.properties")] == b1, "M2 a second run is a no-op")
    os.remove(os.path.join(d, "migrate-0.3.2.done"))
    r_again = str(Mig.run(Paths.get(d)))
    K.check([rb(d, f) for f in ("types.properties", "regen.properties", "config.properties", "trees.properties")] == b1, "M2 without the marker it changes nothing twice: %s" % r_again[:80])
    # 2: hand edits (LF): a hand logs line kept, a hand type.dirt kept, gather.types = the 0.3.1 default -> rewritten, tree 7000 kept
    d = setup("b", {"types.properties": "type.logs=Wood_*_Trunk\ntype.dirt=Soil_Dirt\n", "regen.properties": "regrow.dirt=2,Rock_Bedrock\n",
                    "config.properties": "zones.on=true\ngather.types=%s\n" % GT31, "trees.properties": "tree.maxBlocks=7000\n"})
    r = str(Mig.run(Paths.get(d)))
    nt, nr, nc, nx = (rb(d, f) for f in ("types.properties", "regen.properties", "config.properties", "trees.properties"))
    K.check(nt.startswith("type.logs=Wood_*_Trunk\ntype.dirt=Soil_Dirt\n") and nt.count("type.dirt=") == 1 and "type.rock=" in nt and "\r" not in nt,
            "M2 hand-edited logs + a hand type.dirt line kept, the others appended, LF kept")
    K.check(nr.startswith("regrow.dirt=2,Rock_Bedrock\n") and nr.count("regrow.dirt=") == 1, "M2 a hand regrow.dirt row kept")
    K.check(("gather.types=%s,stone,%s\n" % (GT31, ",".join(new_types))) in nc and nx == "tree.maxBlocks=7000\n", "M2 gather.types holding the 0.3.1 default -> + stone + the 12 types; tree 7000 kept")
    K.check("type.logs=Wood_*_Trunk" in r and "tree.maxBlocks=7000" in r, "M2 ... the kept lines are logged: %s" % r[-160:])
    # 3: History copy fails -> nothing written, no marker; 4: a fresh folder -> the marker only
    d = setup("c", {"types.properties": t31, "regen.properties": r31, "config.properties": c31, "trees.properties": x31})
    open(os.path.join(d, "config-history"), "w").write("in the way")
    K.check(str(Mig.run(Paths.get(d))) == "" and rb(d, "types.properties") == t31 and not os.path.isfile(os.path.join(d, "migrate-0.3.2.done")),
            "M2 no History copy -> NOTHING written, no marker (the next start tries again)")
    d = setup("d", {"config.properties": c31})
    K.check(str(Mig.run(Paths.get(d))) == "" and os.path.isfile(os.path.join(d, "migrate-0.3.2.done")) and not os.path.isfile(os.path.join(d, "types.properties")),
            "M2 a fresh folder - the marker only (the default files carry the rows)")
    # the migrated file reads the same as a fresh default (the patch asserts the values; here: Mig032's appended lines = the jar defaults)
    tt = str(Cfg.TYPES_TEXT)
    K.check(all(("type.%s=" % t) in tt for t in new_types) and ("type.logs=%s" % L32) in tt, "M2 the default types.properties carries the same lines")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Plug, CPub, Sto, Cfg = (JClass(PKG + n) for n in ("SkyyZonesPlugin", "CfgPub", "ZStore", "ZCfg"))
    Paths = JClass("java.nio.file.Paths")
    Sto.SYNC = True
    before = M.snap(home)
    sz = os.path.join(home, "Skyy_SkyyZones")
    rd = lambda f: open(os.path.join(sz, f), "rb").read().decode("latin-1") if os.path.isfile(os.path.join(sz, f)) else None
    old = dict((f, rd(f)) for f in ("types.properties", "regen.properties", "config.properties", "trees.properties", "regen/skywynn_zones2.snap"))

    def start():
        r = str(Plug.paths(Paths.get(sz)))
        CPub.start(Paths.get(home), JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyZones"))
        CPub.flush()
        CPub.shutdown()
        return r
    r1 = start()
    s1 = M.snap(home)
    snap1 = rd("regen/skywynn_zones2.snap")
    r2 = start()
    s2 = M.snap(home)
    snap2 = rd("regen/skywynn_zones2.snap")
    ch = sorted(f for f in before if s1.get(f) != before[f] and not f.startswith("Skyy_SkyyZones/"))
    K.check(not ch, "D start 1: every file outside Skyy_SkyyZones byte-identical (%s)" % ch[:5])
    diff2 = sorted(f for f in set(s1) | set(s2) if s1.get(f) != s2.get(f))
    snapnote = ""
    if diff2 == ["Skyy_SkyyZones/regen/skywynn_zones2.snap"] and snap1 and snap2:
        a_, b_ = set(snap1.splitlines()), set(snap2.splitlines())
        gone = a_ - b_
        if not (b_ - a_) and all(l.startswith(("V ", "W ")) for l in gone):
            diff2 = []
            snapnote = " (%d grown-back V / W lines older than 30 min aged out between the starts - a clock effect, the 0.3.1 harness shows it too)" % len(gone)
    K.check(not diff2, "D start 2 changes nothing%s (%s)" % (snapnote, diff2))
    chz = sorted(f for f in set(s1) | set(before) if f.startswith("Skyy_SkyyZones/") and s1.get(f) != before.get(f))
    K.notes.append("D Skyy_SkyyZones changes: %s" % chz)
    allowed = ("Skyy_SkyyZones/types.properties", "Skyy_SkyyZones/regen.properties", "Skyy_SkyyZones/trees.properties", "Skyy_SkyyZones/migrate-0.3.2.done",
               "Skyy_SkyyZones/config-changes.log", "Skyy_SkyyZones/regen/skywynn_zones2.snap")
    K.check(all(f in allowed or f.startswith("Skyy_SkyyZones/config-history/") for f in chz), "D only Mig032's files change: %s" % [f for f in chz if f not in allowed and not f.startswith("Skyy_SkyyZones/config-history/")])
    nt, nr, nc, nx = rd("types.properties"), rd("regen.properties"), rd("config.properties"), rd("trees.properties")
    L31 = "Wood_*_Trunk,Wood_*_Branch_Corner,Wood_*_Branch_Long,Wood_*_Branch_Short,Wood_*_Roots"
    if old["types.properties"] is not None:
        K.check(nt.startswith(old["types.properties"].replace("type.logs=" + L31, "type.logs=Wood_*_Trunk,Wood_*_Trunk_Full," + L31[len("Wood_*_Trunk,"):]))
                and "type.crystals=Rock_Crystal_*" in nt and "type.plants=" in nt, "D Skyy's types.properties: logs + Trunk_Full (it held the 0.3.1 default), the new types appended, the rest byte-identical")
    if old["regen.properties"] is not None:
        K.check(nr.startswith(old["regen.properties"]) and "regrow.dirt=8,Rock_Bedrock" in nr and "regrow.crystals=30,Empty" in nr, "D Skyy's regen.properties: only appended rows")
    K.check(nc == old["config.properties"], "D Skyy's config.properties untouched (it has no gather.types line - the new default applies)")
    if old["trees.properties"] is not None:
        K.check(nx == old["trees.properties"].replace("tree.maxBlocks=6000", "tree.maxBlocks=9000"), "D Skyy's trees.properties: tree.maxBlocks 6000 -> 9000 only")
    gt = [str(t) for t in Cfg.gatherTypes()]
    K.check("stone" in gt and "dirt" in gt and "crystals" in gt and "plants" in gt and "skywynn_zones2" in str(Cfg.GATHERW) and int(Cfg.TREE_MAX) == 9000,
            "D Skyy's world now gathers stone, dirt, crystals, plants ...; trees up to 9000 blocks: %s" % ",".join(gt))
    K.check("Mig032" in r1 and "Mig032" not in r2, "D the one-time update runs on start 1 only: %s" % r1[:200])
    K.notes.append("D: %s | %s" % (r1[:400], r2[:200]))
    K.save()


if __name__ == "__main__":
    HK.run("SkyyZones", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("static", run_static), ("fakes", M.run_fakes), ("exec", run_exec), ("mig", M.run_mig), ("mig2", run_mig2), ("live", run_live)],
           __file__, live=(LIVE, "mods"))
