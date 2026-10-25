"""Harness for SkyyZones 0.3.1 (SkyyZones 0.3 step 2: scaffolding, skill gates, fair play, zones03 follow-ups; tools/zones_0_3_1_patch.py).
Build first:  python tools/zones_0_3_1_patch.py && python SkyyZones/build_skyyzones_0.3.1.py
    python SkyyZones/test_skyyzones_0.3.1.py [--keep]
Phases (fresh child JVMs, tools/harness_kit.py: -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch; scratch tools/dev/scratch/zones031/zh):
  S   static   the patch re-runs to identical bytes; line endings kept; no new system / command; the ready line '[SkyyZones] 0.3.1 ready';
               B3 the Skyy_Scaffold item json (vanilla look + recipe ids exist in Assets.zip) + its lang keys (both prefixes, kit colours)
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.3.0 -> 0.3.1: exactly ZScaf / ZPl / ZFair / ZScafs added; the members that differ (EXPECT)
  F2  fakes    the 0.2.0 harness's engine stand-ins into scratch/fake2
  X   exec     EVERY 0.3.0 check again on 0.3.1 (regression; the fair-play rules off meanwhile), then the 0.3.1 checks on the REAL classes
               with REAL engine events: B1 scaffold allow / deny matrix, B2 T line first / vanish / cap / restart / hand break / rate,
               B4 gates (type + region, max per skill, SkyySkills missing = off + one warning, cache, check hooks), B5 anti-AFK, rate cap with
               same-tick half weights + a felled tree = one break, turn limit only when contested, hit lock, bot flag; B6 /zones status / info /
               region gate / place add|remove / permissions / the regions table cell; builder + op bypass; F1 ZFell.verify in passBatch
               batches; F2 the search read cap + the section reader on a real BlockSection; FIXER checks (marked "(fixer)"): level 0 never
               cached / 1 s cache, a stopped player's hits refused (no lock), anti-AFK fresh anchor after 5 min away, a fresh T line for
               another placed id, scaffolds first in a full pass, the refused-tree memory, the rules[<region>] table + a long region;
               FIXER 2 checks (marked "(fixer 2)"): a locked player's HIT from afkMove away unlocks him, plain blocks only on place lists,
               the level cache keyed by profile epoch (a 0 cached, a switch fresh at once), SkyySkills -1 / -2, abuse.awaySec, a refused hit
               counted once a second, zones.on off keeps scaffolding timed, a zone reset keeps scaffolds' T lines + its undo clears them
  M   mig      Mig030 (unchanged since 0.3.0) on synthetic files
  D   live     start twice on a scratch COPY of the live mods folder: only Mig030's lines + the two new files, start 2 changes nothing
  AA  audit    engine-access audit
NOT COVERED (UNVERIFIED in game): standing on / climbing the scaffold, the engine placing the item's block id, World.getTick for a real
Vein Mine extra, the real time of a 60,000-read search, a 0.3.0 rollback with Skyy_Scaffold items in inventories.
"""
import os, sys, hashlib, importlib.util, subprocess, zipfile, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK
import skyybuild as B

VERSION, OLD = "0.3.1", "0.3.0"
PKG = "com.skyy.zones."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyZones-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyZones-%s.jar" % OLD)
GEN = os.path.join(HERE, "build_skyyzones_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyzones_%s.py" % OLD)
PATCH = os.path.join(ROOT, "tools", "zones_0_3_1_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "zones031", "zh")))
LIVE = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods")
ADDED = ["ZFair", "ZPl", "ZScaf", "ZScafs"]
EXPECT = {   # checked 2026-10-25 (the class compare 0.3.0 -> 0.3.1 of the first harness run, every member a planned change of tools/zones_0_3_1_patch.py;
 # CfgFile / CfgFn / CfgRows = the version text + the two new files / 22 rows; ZCmd1-5 = the usage text (place / gate); ZFell rd / verify = new signatures)
    'CfgFile': ['~<clinit>', '~m init'],
    'CfgFn': ['~m opExport'],
    'CfgRows': ['+f DL4', '+f DL5', '~<clinit>', '~m defLines', '~m header'],
    'SkyyZonesPlugin': ['~m paths', '~m setup', '~m shutdown'],
    'ZApi': ['+m tick'],
    'ZBox': ['~m drop', '~m restore'],   # fixer 2: the reset keeps scaffolds' T lines, the undo takes them back forced
    'ZCfg': ['+f ABUSE_ON', '+f AFK_MOVE', '+f AFK_RADIUS', '+f AFK_SEC', '+f AWAY_SEC', '+f BOT_FLAG', '+f BOT_GAP_MS', '+f BOT_SAMPLE', '+f CELL_CAP', '+f CELL_REST', '+f CELL_SIZE', '+f CELL_WINDOW', '+f CONTEST_SEC', '+f GATES', '+f GATES_ON', '+f GFILE', '+f GUARD_TEXT', '+f HITLOCK_SEC', '+f MAX_PER_MIN', '+f RATE_REST', '+f SCAF_IDS', '+f SCAF_LIFE', '+f SCAF_MAX', '+f SCAF_ON', '+f SCAF_REACH', '+f SCAF_TEXT', '+f SFILE', '+f SIARR', '+f SISRC', '+f SKILLS_TEXT', '+m checkGate', '+m checkOff', '+m checkScafIds', '+m gate', '+m gateList', '+m gateOf', '+m gateText', '+m loadGuard', '+m loadScaf', '+m offMin', '+m parseGates', '+m placeWhy', '+m plainWhy', '+m reloadGuard', '+m scafIds', '+m skillOf', '+m skills', '~<clinit>', '~m reloadFiles'],
    'ZCmd1': ['~c '],
    'ZCmd2': ['~c '],
    'ZCmd3': ['~c '],
    'ZCmd4': ['~c '],
    'ZCmd5': ['~c '],
    'ZCmds': ['+m place', '~m help', '~m info', '~m region', '~m run', '~m status'],
    'ZEng': ['+m fastAt', '+m idIn', '+m tick'],
    'ZFell': ['+f MAXR', '+f NEG', '+f NEG_MS', '+f READ_CAP', '+f READ_PER', '+f SPREAD', '+m rd', '+m seen', '+m verify', '-m rd', '-m verify', '~<clinit>', '~m search'],
    'ZFn': ['~m apply', '~m publish', '~m unpublish'],
    'ZGuard': ['+m dmg', '~m handle'],
    'ZGuardDamage': ['+m dmg'],
    'ZPass': ['~m pass'],
    'ZRegKit': ['+m rulesCell', '+m rulesSet', '~m customGet', '~m customSet'],
    'ZRegen': ['+m scafAt', '~m beat', '~m fell', '~m readInto', '~m restore', '~m start', '~m status'],
    'ZRegion': ['+f gl', '+f gsrc', '+m gateShown', '+m gates', '+m place', '+m placeShown', '~m summary'],
    'ZRw': ['+f scaf', '+m addScaf', '+m scafDone', '~c ', '~m snapshot'],
    'ZStore': ['~m applyField', '~m parseAll'],
    'ZTicker': ['~m run'],
}
WORLD = "skywynn_zones2"          # a whole-island gathering world
PLAIN = "skywynn_server"          # protected, not a gathering world
CARROT = "Plant_Crop_Carrot_Block"
C1 = "*Plant_Crop_Carrot_Block_State_Definitions_Stage1"
CF = "*Plant_Crop_Carrot_Block_State_Definitions_StageFinal"
CQ = ["*Plant_Crop_Carrot_Block_State_Definitions_%s" % q for q in ("Crude", "Best", "Epic")]   # finisher: DynamicSeasons' quality ripe states


def t20():
    spec = importlib.util.spec_from_file_location("zones_t20", os.path.join(HERE, "test_skyyzones_0.2.0.py"))
    m = importlib.util.module_from_spec(spec)
    a = list(sys.argv)
    spec.loader.exec_module(m)
    sys.argv[:] = a
    return m


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, "rb").read()
    o = open(GEN_OLD, "rb").read()
    K.check(g.startswith(b'"""SkyyZones 0.3.1') and g.count(b'VERSION = "0.3.1"') == 1, "S header + VERSION")
    for w in (b"registerSystem(", b"registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.check((b"\r\n" in g) == (b"\r\n" in o), "S line endings kept")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    src = open(PATCH, encoding="utf8").read().replace('os.path.join(ROOT, "SkyyZones", "build_skyyzones_0.3.1.py")', repr(os.path.join(d, "b.py")))
    open(os.path.join(d, "p.py"), "w", encoding="utf8").write(src.replace("ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))", "ROOT = %r" % ROOT))
    p = subprocess.run([sys.executable, os.path.join(d, "p.py")], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(os.path.join(d, "b.py"), "rb").read() == g, "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    with zipfile.ZipFile(jar) as z:
        pl = z.read("com/skyy/zones/SkyyZonesPlugin.class")
        names = z.namelist()
    K.check(b"[SkyyZones] 0.3.1 ready - " in pl, "S B7: the ready line '[SkyyZones] 0.3.1 ready' (smoke_test.py)")
    K.check(not any(n.lower().endswith(".ui") for n in names), "S no .ui file in the jar")
    K.check(b"tier_tags" in g and b"TT.LOGS" in g and b"open(" not in g.split(b"import tier_tags as TT")[1].split(b"\n")[0], "S tools/tier_tags.py is only imported (read)")
    # ---- 0.3.1 B3: the Scaffolding item (vanilla look BY PATH, recipe ids that exist), its lang keys (both prefixes), the kit's colours
    import json as _json
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import skyyui as _SUI
    import tier_tags as _TT
    with zipfile.ZipFile(jar) as z:
        it_ = _json.loads(z.read("Server/Item/Items/SkyyZones/Skyy_Scaffold.json").decode("utf8"))
        lang_ = z.read("Server/Languages/en-US/server.lang").decode("utf8")
    with zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")) as az:
        an_ = set(az.namelist())
        items_ = set(n.rsplit("/", 1)[1][:-5] for n in an_ if n.startswith("Server/Item/Items/") and n.endswith(".json"))
        camp_ = az.read("Server/Item/Items/Bench/Bench_Campfire.json").decode("utf-8-sig")
    bt_ = it_.get("BlockType", {})
    rc_ = it_.get("Recipe", {})
    K.check(bt_.get("DrawType") == "Cube" and bt_.get("Material") == "Solid" and ("Common/" + bt_["Textures"][0]["All"]) in an_ and ("Common/" + it_["Icon"]) in an_,
            "S B3: Skyy_Scaffold is a solid cube with the vanilla Village Crate texture + icon BY PATH (both in Assets.zip): %s" % bt_.get("Textures"))
    K.check(rc_.get("Input") == [{"ItemId": "Ingredient_Stick", "Quantity": 4}] and rc_.get("OutputQuantity") == 8 and "Ingredient_Stick" in items_
            and rc_["BenchRequirement"] == [{"Id": "Workbench", "Type": "Crafting", "Categories": ["Workbench_Survival"]}] and '"Workbench_Survival"' in camp_,
            "S B3 (Q2): Workbench (Survival tab) 4 sticks -> 8 Scaffolding; the stick + the tab exist in vanilla: %s" % rc_)
    K.check("Skyy_Scaffold" not in items_ and not any(("scaffold" in n.lower() or "lattice" in n.lower()) for n in an_ if n.startswith("Server/Item/Items/")),
            "S vanilla first: Assets.zip has no scaffold block (our own id is not a vanilla id)")
    K.check(it_.get("Quality") == "Common" and it_["TranslationProperties"] == {"Name": "server.items.Skyy_Scaffold.name", "Description": "server.items.Skyy_Scaffold.description"},
            "S B3: no rarity (Quality Common), name + description keys")
    lk_ = dict(l.split("=", 1) for l in lang_.splitlines() if "=" in l)
    desc_ = lk_.get("items.Skyy_Scaffold.description", "")
    K.check(lk_.get("items.Skyy_Scaffold.name") == "Scaffolding" and lk_.get("server.items.Skyy_Scaffold.name") == "Scaffolding"
            and desc_ == lk_.get("server.items.Skyy_Scaffold.description") and "Place:" in desc_ and "Vanishes after a few seconds. Gives nothing back." in desc_,
            "S B3: lang keys under both prefixes, the spec text: %r" % desc_[:200])
    K.check(all(('<color is="%s">' % _SUI.COLOR[c]) in desc_ for c in ("warning", "rowName", "rowSub")),
            "S B3: description colours = the kit's Style Guide section 15 colours (actions yellow, text soft white, minor dim grey)")
    _tagged = set()
    for _v in vars(_TT).values():
        if isinstance(_v, (list, tuple, set, dict)):
            try:
                _tagged |= set(str(x) for x in (_v.keys() if isinstance(_v, dict) else _v))
            except Exception:
                pass
    K.check("Skyy_Scaffold" not in _tagged and "Skyy_Scaffold" not in open(os.path.join(ROOT, "tools", "tier_tags.py"), encoding="utf8").read(),
            "S 3.4: Skyy_Scaffold has no tier (no tag, not in tools/tier_tags.py)")
    K.check(b"BlockHealthSection" in g and b"getTick" in g and b"Z4 desk probes" in g, "S the Z4 desk probes run at every build (shared block damage, the world tick)")
    K.save()


def run_fakes(out, jar, scratch, _home):
    T = t20()
    os.makedirs(os.path.join(scratch, "fake2"), exist_ok=True)
    T.run_mkfake(os.path.join(scratch, "fake2"))
    K = HK.Child(out)
    K.check(os.path.isdir(os.path.join(scratch, "fake2")), "F2: the stand-ins are written")
    K.save()


def engine(K, T, scratch):
    """t20().engine with the 0.3.0 blocks (+ real StateData on the carrot's states)."""
    from jpype import JClass, JArray, JString, JInt
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)

    def jfield(c, n):
        f = c.class_.getDeclaredField(n)
        f.setAccessible(True)
        return f
    JClass("com.hypixel.hytale.server.core.Options").parse(JArray(JString)(["--universe", os.path.join(scratch, "universe")]))
    HS = JClass("com.hypixel.hytale.server.core.HytaleServer")
    hs = U.allocateInstance(HS.class_)
    jfield(HS, "eventBus").set(hs, JClass("com.hypixel.hytale.event.EventBus")(False))
    jfield(HS, "instance").set(None, hs)
    CHM, COLL = JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.util.Collections")
    UNI = JClass("com.hypixel.hytale.server.core.universe.Universe")
    uni = U.allocateInstance(UNI.class_)
    pbu, wmap = CHM(), CHM()
    for n, v in (("playersByUuid", pbu), ("players", COLL.unmodifiableCollection(pbu.values())), ("worlds", wmap), ("worldsByUuid", CHM()),
                 ("unmodifiableWorlds", COLL.unmodifiableMap(wmap))):
        jfield(UNI, n).set(uni, v)
    jfield(UNI, "instance").set(None, uni)
    JClass("com.hypixel.hytale.server.core.asset.AssetRegistryLoader").init()
    AL = JClass("java.util.ArrayList")
    BT = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType")
    names = ["Rock_Stone", "Rock_Bedrock", "Ore_Copper_Stone", "Ore_Iron_Stone", "Soil_Grass", "Furniture_Crude_Chest", "Bench_Workbench",
             CARROT, C1, CF] + CQ + ["Wood_Oak_Trunk", "Wood_Oak_Trunk_Full", "Wood_Oak_Branch_Short", "Wood_Oak_Roots", "Wood_Birch_Trunk", "Wood_Pine_Trunk",
             "Wood_Gumboab_Trunk", "Wood_Redwood_Trunk", "Wood_Oak_Planks", "Plant_Leaves_Oak", "Plant_Leaves_Birch", "Plant_Leaves_Autumn",
             "Ore_Lead_Sandstone_SkyWynn", "Rock_Gem_Ruby", "Skyy_Scaffold"]
    l_ = AL()
    l_.add(BT.EMPTY)
    l_.add(BT.UNKNOWN)
    for n in names:
        l_.add(BT(n))
    r_ = BT.getAssetStore().loadAssets("Hytale:Hytale", l_)
    K.check(not r_.hasFailed(), "E: the BlockType store holds the %d test blocks" % len(names))
    # the carrot's growth states: real StateData objects (stateToBlock / blockToState) on its three block types
    SDc, HM = JClass(PKG.replace("com.skyy.zones.", "") + "com.hypixel.hytale.server.core.asset.type.blocktype.config.StateData"), JClass("java.util.HashMap")
    sd = U.allocateInstance(SDc.class_)
    s2b, b2s = HM(), HM()
    for st, key in [("default", CARROT), ("Stage1", C1), ("StageFinal", CF)] + list(zip(("Crude", "Best", "Epic"), CQ)):
        s2b.put(st, key)
        b2s.put(key, st)
    jfield(SDc, "stateToBlock").set(sd, s2b)
    jfield(SDc, "blockToState").set(sd, b2s)
    btm = BT.getAssetMap()
    Farm = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.farming.FarmingData")
    fd = U.allocateInstance(Farm.class_)
    jfield(Farm, "stages").set(fd, HM())
    for key in [CARROT, C1, CF] + CQ:   # a crop: growth states + farming stages (an F on it = a harvest = BREAK, ZRules.useAction)
        jfield(BT, "state").set(btm.getAsset(JInt(int(btm.getIndex(key)))), sd)
        jfield(BT, "farming").set(btm.getAsset(JInt(int(btm.getIndex(key)))), fd)
    BGA = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockGathering")
    HDT = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.HarvestingDropType")
    for key in CQ:   # finisher: DynamicSeasons' Crude / Best / Epic states carry their own Harvest drop list (StageFinal too in game)
        g_ = U.allocateInstance(BGA.class_)
        jfield(BGA, "harvest").set(g_, HDT(None, "Drops_" + key.split("_")[-1]))
        jfield(BT, "gathering").set(btm.getAsset(JInt(int(btm.getIndex(key)))), g_)
    CT = JClass("com.hypixel.hytale.component.ComponentType")
    RT = JClass("com.hypixel.hytale.component.ResourceType")
    SG = JClass("com.hypixel.hytale.component.SystemGroup")
    MOD = JClass("java.lang.reflect.Modifier")
    n_ = [0]

    def fill(cls, inst):
        for f in cls.class_.getDeclaredFields():
            if MOD.isStatic(f.getModifiers()):
                continue
            t = f.getType()
            v = None
            if t == CT.class_:
                v = U.allocateInstance(CT.class_)
                n_[0] += 1
                jfield(CT, "index").set(v, JInt(n_[0]))
            elif t == RT.class_:
                v = U.allocateInstance(RT.class_)
            elif t == SG.class_:
                v = U.allocateInstance(SG.class_)
            if v is not None:
                f.setAccessible(True)
                f.set(inst, v)
    EM = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
    em = U.allocateInstance(EM.class_)
    fill(EM, em)
    jfield(EM, "instance").set(None, em)
    upr = U.allocateInstance(CT.class_)
    n_[0] += 1
    jfield(CT, "index").set(upr, JInt(n_[0]))
    jfield(UNI, "playerRefComponentType").set(uni, upr)
    return {"U": U, "jfield": jfield, "BT": BT}


def run_exec(out, jar, scratch, _home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, os.path.join(scratch, "fake2")], verify=True)
    T = t20()
    T.SCRATCH = scratch
    try:
        E = engine(K, T, scratch)
        xrun(K, E, T, scratch)
    except Exception as e:
        import traceback
        traceback.print_exc()
        K.check(False, "X: run crashed: %s" % str(e)[:500])
    K.save()


def xrun(K, E, T, scratch):
    from jpype import JClass, JArray, JString, JInt, JLong, JFloat, JImplements, JOverride
    U, jfield, BT = E["U"], E["jfield"], E["BT"]
    FAKE = T.FAKE
    P = lambda n: JClass(PKG + n)
    Cfg, Sto, Eng, Msg, Bld, Plug, Rgn, Pass, Tkr, Dep, Fell, Rules, Tick, Box, Fn = (P(n) for n in (
        "ZCfg", "ZStore", "ZEng", "ZMsg", "ZBuild", "SkyyZonesPlugin", "ZRegen", "ZPass", "ZTicker", "ZDep", "ZFell", "ZRules", "ZTick", "ZBox", "ZFn"))
    AL, IHM, UUID, Paths, Bool = (JClass("java.util.ArrayList"), JClass("java.util.IdentityHashMap"), JClass("java.util.UUID"),
                                  JClass("java.nio.file.Paths"), JClass("java.lang.Boolean"))
    MS, MB, MCH, FW, FP = (JClass(FAKE + "." + n) for n in ("MapStore", "MapBuffer", "MapChunk", "FakeWorld", "FakePr"))
    WLD = JClass("com.hypixel.hytale.server.core.universe.world.World")
    EST = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore")
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    TC = JClass("com.hypixel.hytale.server.core.modules.entity.component.TransformComponent")
    V3D, V3I = JClass("org.joml.Vector3d"), JClass("org.joml.Vector3i")
    R3 = JClass("com.hypixel.hytale.math.vector.Rotation3f")
    REF = JClass("com.hypixel.hytale.component.Ref")
    ITY = JClass("com.hypixel.hytale.protocol.InteractionType")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    ICTX = JClass("com.hypixel.hytale.server.core.entity.InteractionContext")
    BBE = JClass("com.hypixel.hytale.server.core.event.events.ecs.BreakBlockEvent")
    DBE = JClass("com.hypixel.hytale.server.core.event.events.ecs.DamageBlockEvent")
    PLBE = JClass("com.hypixel.hytale.server.core.event.events.ecs.PlaceBlockEvent")
    UBP = JClass("com.hypixel.hytale.server.core.event.events.ecs.UseBlockEvent$Pre")
    btm = BT.getAssetMap()

    def bt(n):
        i = int(btm.getIndex(n))
        return btm.getAsset(JInt(i)) if i != -2147483648 else btm.getAsset(JInt(int(btm.getIndex("Rock_Stone"))))
    lines = AL()
    Cfg.LINES = lines

    def logged():
        r = [str(x) for x in lines]
        lines.clear()
        return r
    players = {}

    @JImplements(PKG + "ZApi")
    class Api(object):
        def __init__(self):
            self.notes, self.wb, self.state, self.occ, self.writes, self.loads, self.tasks, self.worlds, self.lat = [], {}, {}, set(), [], [], [], {}, []
            self.titles, self.breaks, self.unl, self.base = [], [], set(), "Soil_Grass"
            self.reads = []
            self.tk = -1

        @JOverride
        def tick(self, w):
            return self.tk

        @JOverride
        def notify(self, pr, text):
            self.notes.append((str(pr.getUsername()), str(text)))

        @JOverride
        def title(self, pr, t, sub):
            self.titles.append((str(pr.getUsername()), str(t), str(sub)))

        @JOverride
        def particle(self, id_, x, y, z, to, st):
            pass

        @JOverride
        def target(self, r, st):
            return None

        @JOverride
        def selection(self, r, st, pr):
            return None

        @JOverride
        def give(self, r, st, id_):
            return 0

        @JOverride
        def blockAt(self, w, x, y, z):
            k = (str(w.getName()), int(x), int(y), int(z))
            if k in self.unl:
                return None
            self.reads.append(1)
            return self.wb.get(k, "Empty" if int(y) > 100 else self.base)

        @JOverride
        def stateAt(self, w, x, y, z):
            return JArray(JInt)(self.state.get((str(w.getName()), int(x), int(y), int(z)), [0, 0]))

        @JOverride
        def put(self, w, x, y, z, id_, rot):
            k = (str(w.getName()), int(x), int(y), int(z))
            self.writes.append(k + (str(id_), int(rot)))
            self.wb[k] = str(id_)
            return True

        @JOverride
        def occupied(self, w, x, y, z):
            return (str(w.getName()), int(x), int(y), int(z)) in self.occ

        @JOverride
        def load(self, w, x, y, z, after):
            self.loads.append(after)

        @JOverride
        def world(self, name):
            return self.worlds.get(str(name))

        @JOverride
        def exec(self, w, r):
            self.tasks.append(r)
            return True

        @JOverride
        def later(self, r, ms):
            self.lat.append(r)

        @JOverride
        def scan(self, w, box, ids, stats):
            return AL()

        @JOverride
        def breakAs(self, pr, w, cells):
            # the engine's performBlockBreak: one REAL BreakBlockEvent per cell on the feller (our guard first), removed if not cancelled
            try:
                return self.breakAs0(pr, w, cells)
            except Exception:
                import traceback
                traceback.print_exc()
                raise

        def breakAs0(self, pr, w, cells):
            p = players.get(str(pr.getUsername()))
            got = []
            for v in cells:
                x, y, z = int(v.x()), int(v.y()), int(v.z())
                blk = self.wb.get((str(w.getName()), x, y, z), "Empty")
                e_ = BBE(item("Tool_Hatchet_Iron"), V3I(x, y, z), bt(blk))
                gB.handle(0, p["ch"], p["st"], cb, e_)
                c_ = bool(e_.isCancelled())
                got.append(c_)
                if not c_:
                    self.wb[(str(w.getName()), x, y, z)] = "Empty"
            self.breaks.append((str(pr.getUsername()), [(int(v.x()), int(v.y()), int(v.z())) for v in cells], got))
            return len(cells)
    api = Api()
    Eng.API = api
    perms = {}

    @JImplements("java.util.function.Function")
    class PermFn(object):
        @JOverride
        def apply(self, o):
            return Bool.valueOf(bool(perms.get((str(o[0]), str(o[1])), False)))
    Cfg.PERM_TEST = PermFn()

    # ---------------------------------------------------------------- C: default files (a new folder) + config
    home = os.path.join(scratch, "x", "Skyy_SkyyZones")
    os.makedirs(os.path.dirname(home), exist_ok=True)
    r = str(Plug.paths(Paths.get(home)))
    rd = lambda f: open(os.path.join(home, f), encoding="utf8").read()
    rtxt, ttxt, xtxt, ctxt = rd("regen.properties"), rd("types.properties"), rd("trees.properties"), rd("config.properties")
    K.check("regrow.logs=60,none\n" in rtxt and "regrow.crops=10,stage1\n" in rtxt and "regrow.lead=6,Rock_Bedrock\n" in rtxt and "regrow.chromium=8,Rock_Bedrock\n" in rtxt
            and "regrow.slag=10,Rock_Bedrock\n" in rtxt and "regrow.titanium=12,Rock_Bedrock\n" in rtxt, "C: new regen.properties: logs 60,none, crops 10,stage1, the zone ores 6 / 8 / 10 / 12 s (%s)" % r[:160])
    K.check("type.lead=Ore_Lead_Sandstone_SkyWynn\n" in ttxt and "type.chromium=Ore_Chromium_Shale_SkyWynn\n" in ttxt and "type.slag=Ore_Slag_Volcanic_SkyWynn\n" in ttxt
            and "type.titanium=Ore_Titanium_Basalt_SkyWynn\n" in ttxt, "C A9: the 4 zone ore types = the exact SkyyWorldGen ids (tools/tier_tags.py)")
    K.check(all(("%s=%d\n" % kv) in xtxt for kv in (("tree.sec1", 45), ("tree.sec2", 60), ("tree.sec3", 90), ("tree.maxBlocks", 6000), ("tree.clearSec", 3))) and xtxt == str(Cfg.TREES_TEXT),
            "C: trees.properties written once with 45 / 60 / 90 s, 6000 blocks (fixer: 600 refused 244 vanilla tree prefabs), 3 s")
    K.check("zones.gatherWorlds=\n" in ctxt and "gather.types=copper,iron,gold,silver,thorium,cobalt,adamantite,mithril,onyxium,lead,chromium,slag,titanium,gem,logs,crops\n" in ctxt,
            "C: config.properties has zones.gatherWorlds (empty) + gather.types (every ore, gem, logs, crops - no stone)")
    K.check(os.path.isfile(os.path.join(home, "migrate-0.3.0.done")) and "new folder" in rd("migrate-0.3.0.done"), "C A8: a NEW folder gets the Mig030 marker only (its default files carry the rows)")
    K.check((int(Cfg.TREE_SEC1), int(Cfg.TREE_SEC2), int(Cfg.TREE_SEC3), int(Cfg.TREE_MAX), int(Cfg.TREE_CLEAR)) == (45, 60, 90, 6000, 3), "C: the tree fields read")
    open(os.path.join(home, "trees.properties"), "a", encoding="utf8").write("tree.sec1=2\ntree.maxBlocks=99999\n")
    Cfg.loadTrees(False)
    K.check(int(Cfg.TREE_SEC1) == 5 and int(Cfg.TREE_MAX) == 12000, "C: hand edits are clamped (5-3600 s, 50-12000 blocks)")
    open(os.path.join(home, "trees.properties"), "w", encoding="utf8").write(xtxt)
    Cfg.loadTrees(False)
    ck = lambda f, v, k="k": (None if f(JString(k), v) is None else str(f(JString(k), v)))
    Cfg.WORLDS = ""
    K.check("Protected worlds" in ck(Cfg.checkGather, WORLD) and "island" in ck(Cfg.checkGather, "skyy-island-abc") and "shard" in ck(Cfg.checkGather, "skyy-shard-x")
            and ck(Cfg.checkGather, "bad/name") is not None and ck(Cfg.checkGather, "") is None, "C A0: checkGather refuses a world not in zones.worlds, islands, shards, bad names")
    Cfg.WORLDS = WORLD + "," + PLAIN
    K.check(ck(Cfg.checkGather, WORLD) is None, "C: ... and takes one that is in zones.worlds")
    Cfg.GATHERW = WORLD
    K.check("gathering world" in ck(Cfg.checkWorlds, PLAIN) and ck(Cfg.checkWorlds, WORLD + "," + PLAIN) is None, "C: zones.worlds refuses dropping a gathering world")
    K.check(ck(Cfg.checkGTypes, "copper,logs,crops") is None and "No resource type" in ck(Cfg.checkGTypes, "copper,nope"), "C: checkGTypes refuses unknown types")
    K.check("never" in ck(Cfg.checkPTypes, "copper,logs") and "never" in ck(Cfg.checkPTypes, "crops"), "C: prefix worlds never take logs / crops (the shards re-plant them)")
    K.check(ck(Cfg.checkRegrow, "60|none", "regrow[logs]") is None and "none" in ck(Cfg.checkRegrow, "60|Rock_Bedrock", "regrow[logs]")
            and ck(Cfg.checkRegrow, "10|stage1", "regrow[crops]") is None and "stage1" in ck(Cfg.checkRegrow, "10|Rock_Bedrock", "regrow[crops]")
            and "only for the crops" in ck(Cfg.checkRegrow, "3|stage1", "regrow[stone]") and ck(Cfg.checkRegrow, "0|none", "regrow[logs]") is None,
            "C A10: checkRegrow - logs need none, crops need stage1, stage1 nowhere else (Undo of Mig030 back to 0,none accepted)")
    Cfg.WORLDS = PLAIN
    logged()
    K.check(bool(Cfg.protectedWorld(WORLD)) and any("zones.gatherWorlds lists" in l for l in logged()), "C A0: FAIL CLOSED - a gathering world missing from zones.worlds is still protected (warned)")
    Cfg.WORLDS = WORLD + "," + PLAIN
    Cfg.GATHERW = WORLD + ",skyy-shard-abc"
    K.check(bool(Cfg.gatherWorld(WORLD)) and not bool(Cfg.gatherWorld("skyy-shard-abc")) and not bool(Cfg.gatherWorld(PLAIN)), "C: a hand-listed shard world is never a gathering world")
    Cfg.GATHERW = WORLD
    # A6 tree groups
    K.check([int(Cfg.group(w)) for w in ("Oak", "Maple", "Gumboab", "Redwood", "Crystal", "Pine")] == [1, 1, 2, 3, 3, 0]
            and [int(Cfg.treeSec(g)) for g in (1, 2, 3, 0)] == [45, 60, 90, 60], "C A6: tree groups Oak 1, Maple 1, Gumboab 2, Redwood 3, Crystal 3, a pack wood 0 -> the logs row (60 s)")
    # rules: families, tree pieces, zone ores
    K.check(str(Rules.fam(CF)) == CARROT and bool(Rules.typeHas("crops", CF)) and bool(Rules.typeHas("crops", C1)) and not bool(Rules.typeHas("crops", "Plant_Leaves_Oak")),
            "C FIX: a crop's STATE blocks are its type (0.2.x matched only the planted state)")
    K.check([None if Rules.woodFam(i) is None else str(Rules.woodFam(i)) for i in ("Wood_Oak_Trunk", "Wood_Oak_Trunk_Full", "Wood_Oak_Branch_Short", "Wood_Oak_Roots", "Wood_Oak_Planks", "Rock_Stone")]
            == ["Oak", "Oak", "Oak", "Oak", None, None], "C: woodFam")
    K.check([bool(Rules.leafOk(f, l)) for f, l in (("Oak", "Plant_Leaves_Oak"), ("Oak", "Plant_Leaves_Birch"), ("Oak", "Plant_Leaves_Autumn"), ("Oak", "Plant_Leaves_Jungle_Floor"),
                                                    ("Fir", "Plant_Leaves_Fire"), ("Fir", "Plant_Leaves_Fir_Snow"), ("Bottletree", "Plant_Leaves_Bottle"))]
            == [True, False, True, False, False, True, True], "C: leafOk - own leaves, the leaves no wood names, never another wood's / floor leaves (Fir != Fire)")
    K.check(str(Rules.listedAny("Ore_Lead_Sandstone_SkyWynn")) == "lead" and Rules.listedAny("Ore_Lead_Plate") is None and Rules.listedAny("Ore_Lead") is None,
            "C A9: the lead type takes only SkyyWorldGen's id - never another mod's Ore_Lead*")
    logged()

    # ---------------------------------------------------------------- worlds / players / events
    def mkworld(name):
        w = U.allocateInstance(FW.class_)
        jfield(WLD, "name").set(w, name)
        es = U.allocateInstance(EST.class_)
        jfield(EST, "world").set(es, w)
        st = U.allocateInstance(MS.class_)
        st.comps = IHM()
        st.ext = es
        return w, st
    wG, stG = mkworld(WORLD)
    wP, stP = mkworld(PLAIN)
    api.worlds = {WORLD: wG, PLAIN: wP}
    cb = U.allocateInstance(MB.class_)
    nref = [0]

    def mkref(st):
        nref[0] += 1
        r_ = REF(st, JInt(nref[0]))
        st.comps.put(r_, IHM())
        return r_

    def mkplayer(st, name, n, builder=False):
        r_ = mkref(st)
        pr_ = U.allocateInstance(FP.class_)
        jfield(PRc, "uuid").set(pr_, UUID.fromString("00000000-0000-4000-8000-%012x" % (0xd000 + n)))
        jfield(PRc, "username").set(pr_, name)
        pr_.msgs = AL()
        st.comps.get(r_).put(PRc.getComponentType(), pr_)
        st.comps.get(r_).put(TC.getComponentType(), TC(V3D(0.5, 101.0, 0.5), R3(0.0, 0.0, 0.0)))
        perms[(str(pr_.getUuid()), "skyyzones.build")] = builder
        ch = U.allocateInstance(MCH.class_)
        ch.ref = r_
        p = {"ch": ch, "st": st, "pr": pr_, "u": pr_.getUuid(), "ref": r_}
        players[name] = p
        return p
    Skyy = mkplayer(stG, "Skyy", 1)
    Coop = mkplayer(stG, "Coop", 2)
    Bd = mkplayer(stG, "Builder", 3, builder=True)
    mob = U.allocateInstance(MCH.class_)
    mob.ref = mkref(stG)
    gB, gD, gP, gU = (P(n)() for n in ("ZGuardBreak", "ZGuardDamage", "ZGuardPlace", "ZGuardUse"))

    def item(i):
        if i is None:
            return None
        try:
            return IS(i, 1)
        except Exception:
            s_ = U.allocateInstance(IS.class_)
            for fn_, v_ in (("itemId", i), ("quantity", JInt(1))):
                f_ = IS.class_.getDeclaredField(fn_)
                f_.setAccessible(True)
                f_.set(s_, v_)
            return s_

    def fire(p, kind, x, y, z, block="Ore_Copper_Stone", st=None):
        ch_, st_ = (p["ch"], p["st"]) if isinstance(p, dict) else (p, st)
        if kind == "break":
            g_, e_ = gB, BBE(item("Tool_Pickaxe_Iron"), V3I(x, y, z), bt(block))
        elif kind == "dig":
            g_, e_ = gD, DBE(item("Tool_Pickaxe_Iron"), V3I(x, y, z), bt(block), JFloat(1.0), JFloat(0.5))
        elif kind == "place":
            g_, e_ = gP, PLBE(item("Rock_Stone"), V3I(x, y, z), None)
        else:
            g_, e_ = gU, UBP(ITY.Use, U.allocateInstance(ICTX.class_), V3I(x, y, z), bt(block))
        Msg.LAST.clear()
        g_.handle(0, ch_, st_, cb, e_)
        return bool(e_.isCancelled())

    def mine(p, wn, x, y, z, block="Ore_Copper_Stone", st=None):
        api.wb[(wn, x, y, z)] = block
        c_ = fire(p, "break", x, y, z, block=block, st=st)
        if not c_:
            api.wb[(wn, x, y, z)] = "Empty"
        return c_

    def drain():
        n = 0
        while api.tasks:
            api.tasks.pop(0).run()
            n += 1
        return n

    def tick(at):
        Dep.CLOCK = JLong(at)
        P("ZTicker")().run()
        n = drain()
        for _i in range(50):   # a backlog pass runs 50 ms later from the scheduler (ZEng.later) - the same clock here
            if not api.lat:
                break
            while api.lat:
                api.lat.pop(0).run()
            n = n + drain()
        return n

    def waiting(wn, x, y, z):
        return bool(Rgn.depleted(wn, x, y, z))
    rdir = os.path.join(home, "regen")

    def jl(wn):
        f = os.path.join(rdir, wn + ".journal")
        return open(f, encoding="utf8").read().splitlines() if os.path.isfile(f) else []

    def notes():
        r_ = list(api.notes)
        del api.notes[:]
        return r_
    Cfg.REGEN_ON = True
    Cfg.JITTER = 0.0
    Cfg.ABUSE_ON = False   # 0.3.1: the fair-play rules stay off while the 0.3.0 checks run again (each rule is tested on its own below)
    Cfg.SPEED = 1.0
    T0 = 1800000000000
    Dep.CLOCK = JLong(T0)
    ix = Sto.INDEX
    BRK, PLC, ALLOW, DENY, NOT_RES, NO_PLACE = int(Rules.BREAK), int(Rules.PLACE), int(Rules.ALLOW), int(Rules.DENY), int(Rules.NOT_RES), int(Rules.NO_PLACE)
    dec = lambda w, x, y, z, a, i: int(Rules.decide(Sto.INDEX, w, bool(Cfg.protectedWorld(w)), x, y, z, a, i))

    # ---------------------------------------------------------------- A0: the island-wide layers
    K.check([dec(WORLD, 5, 90, 5, BRK, i) for i in ("Ore_Copper_Stone", "Ore_Lead_Sandstone_SkyWynn", "Rock_Gem_Ruby", "Wood_Oak_Trunk", CF, "Rock_Stone", "Soil_Grass", "Plant_Leaves_Oak", "Wood_Oak_Planks")]
            == [ALLOW, ALLOW, ALLOW, ALLOW, ALLOW, NOT_RES, NOT_RES, NOT_RES, NOT_RES] and dec(WORLD, 5, 90, 5, PLC, "Rock_Stone") == NO_PLACE,
            "X A0: gathering world, no region = gather.types only (ores, zone ores, gems, logs, crops); stone, dirt, leaves, planks refused; nothing placed")
    K.check(dec(PLAIN, 5, 90, 5, BRK, "Ore_Copper_Stone") == DENY, "X A0: a protected world that is not a gathering world stays FULL")
    Sto.create("town", WORLD, "full", JArray(JInt)([200, 60, 200, 240, 140, 240]), "Skyy")
    Sto.set("town", "title", "Emerald_Town", "Skyy")
    Sto.set("town", "priority", "-100", "Skyy")
    K.check(dec(WORLD, 210, 90, 210, BRK, "Ore_Copper_Stone") == DENY and dec(WORLD, 210, 90, 210, BRK, "Wood_Oak_Trunk") == DENY and dec(WORLD, 210, 90, 210, BRK, CF) == DENY,
            "X A0: a FULL town region refuses ores, logs + crops too - at priority -100 (any region beats the world layer)")
    Sto.create("mine1", WORLD, "skyblock", JArray(JInt)([300, 60, 300, 320, 99, 320]), "Skyy")
    Sto.set("mine1", "types", "stone", "Skyy")
    K.check(dec(WORLD, 310, 90, 310, BRK, "Rock_Stone") == ALLOW and dec(WORLD, 310, 90, 310, BRK, "Ore_Copper_Stone") == ALLOW and dec(WORLD, 310, 90, 310, BRK, "Soil_Grass") == NOT_RES,
            "X A0: a skyblock mine region adds stone (union with the island's types)")
    K.check(str(Rules.area(Sto.INDEX, WORLD, 5, 90, 5)) == "Gathering area (whole island)" and str(Rules.area(Sto.INDEX, WORLD, 210, 90, 210)).startswith("Town - protected")
            and str(Rules.area(Sto.INDEX, WORLD, 310, 90, 310)).startswith("Gathering area (region mine1"), "X A0: /zones info area words")
    fnc = Fn(0)
    K.check(str(fnc.apply(JArray(JClass("java.lang.Object"))([WORLD, JInt(5), JInt(90), JInt(5), "break", "Ore_Copper_Stone"]))) == "allow"
            and str(fnc.apply(JArray(JClass("java.lang.Object"))([WORLD, JInt(5), JInt(90), JInt(5), "harvest", CF]))) == "allow"
            and str(fnc.apply(JArray(JClass("java.lang.Object"))([WORLD, JInt(210), JInt(90), JInt(210), "break", "Ore_Copper_Stone"]))) == "deny"
            and str(fnc.apply(JArray(JClass("java.lang.Object"))([WORLD, JInt(5), JInt(90), JInt(5), "break", "Soil_Grass"]))) == "deny", "X A0: zones:fn:check answers the same layers (+ harvest)")
    notes()
    K.check(fire(Skyy, "break", 7, 90, 7, block="Soil_Grass") and fire(Skyy, "dig", 7, 91, 7, block="Plant_Leaves_Oak") and fire(Skyy, "place", 7, 92, 7)
            and notes()[0] == ("Skyy", "You can only gather the marked resource blocks here."), "X A0: dirt / leaves (no crack) / a place refused on the island")
    c_ = mine(Skyy, WORLD, 8, 90, 8)
    drain()
    K.check(not c_ and waiting(WORLD, 8, 90, 8) and api.wb[(WORLD, 8, 90, 8)] == "Rock_Bedrock" and jl(WORLD)[-1].startswith("D 8 90 8 Ore_Copper_Stone copper "),
            "X A0: an ore on the island breaks (one drop) and regrows on its bedrock placeholder")
    c_ = mine(Skyy, WORLD, 9, 90, 9, block="Ore_Lead_Sandstone_SkyWynn")
    drain()
    K.check(not c_ and str(Rgn.at(WORLD, 9, 90, 9).type) == "lead" and int(Rgn.at(WORLD, 9, 90, 9).due) == T0 + 6000, "X A9: a zone ore (lead) regrows after 6 s")
    tick(T0 + 6000)
    K.check(api.wb[(WORLD, 9, 90, 9)] == "Ore_Lead_Sandstone_SkyWynn" and api.wb[(WORLD, 8, 90, 8)] == "Ore_Copper_Stone", "X: ... both back on time")
    # walking out of the titled town into the gathering world: the event title "Gathering area"
    Tick.titles(Skyy["pr"], Skyy["u"], WORLD, 210, 90, 210, JLong(T0))
    Tick.titles(Skyy["pr"], Skyy["u"], WORLD, 5, 90, 5, JLong(T0 + 100))
    K.check(api.titles[-2][1] == "Emerald Town" and api.titles[-1] == ("Skyy", "Gathering area", "You left Emerald Town"), "X A0: leaving the town shows 'Gathering area': %s" % api.titles[-2:])
    notes()

    # ---------------------------------------------------------------- A1 / A2: the whole-tree search + the record
    def tree(wn, x, y, z, h=5, wood="Oak", leaves="Plant_Leaves_Oak", thick=False, extra=()):
        cells = {}
        for dy in range(h):
            for dx, dz in ([(0, 0), (1, 0), (0, 1), (1, 1)] if thick else [(0, 0)]):
                cells[(x + dx, y + dy, z + dz)] = "Wood_%s_Trunk" % wood
        for dx in range(-2, 3 if not thick else 4):
            for dz in range(-2, 3 if not thick else 4):
                for dy in (h - 1, h):
                    k = (x + dx, y + dy, z + dz)
                    if k not in cells:
                        cells[k] = leaves
        for k, v in extra:
            cells[k] = v
        for (cx, cy, cz), v in cells.items():
            api.wb[(wn, cx, cy, cz)] = v
        return cells

    def tr(wn, x, y, z):
        return Rgn.treeAt(wn, x, y, z)
    TA = T0 + 10000
    Dep.CLOCK = JLong(TA)
    oak = tree(WORLD, 20, 80, 20)
    c_ = mine(Skyy, WORLD, 20, 80, 20, block="Wood_Oak_Trunk")
    t_ = tr(WORLD, 20, 80, 20)
    j_ = jl(WORLD)
    shf = os.path.join(rdir, WORLD + ".shapes")
    sh_txt = open(shf, encoding="utf8").read() if os.path.isfile(shf) else ""
    K.check(not c_ and t_ is not None and int(t_.shape.n) == len(oak) and all(tr(WORLD, *k) == t_ for k in oak) and j_[-1].startswith("G 20 80 20 logs %d " % (TA + 45000)),
            "X A1: ONE cut of a 1-wide oak = the whole tree (5 trunks + %d leaves) waiting, G line (45 s, Zone 1 wood): %s" % (len(oak) - 5, j_[-1:]))
    sid = j_[-1].split()[6]
    K.check(("S %s %d\n" % (sid, len(oak))) in sh_txt and sh_txt.index("S " + sid) >= 0, "X A2: the shape block (S id count + lines) is in <world>.shapes, named by the G line")
    sl = sh_txt.split("S %s %d\n" % (sid, len(oak)))[1].splitlines()[:len(oak)]
    K.check(sl[0] == "0 0 0 Wood_Oak_Trunk 0" and [l.split()[3] for l in sl[:5]] == ["Wood_Oak_Trunk"] * 5 and [int(l.split()[1]) for l in sl[:5]] == [0, 1, 2, 3, 4]
            and all(l.split()[3] == "Plant_Leaves_Oak" for l in sl[5:]), "X A1: the shape: trunks bottom up, then leaves")
    K.check(int(Fell.FELLED.get()) == 1 and drain() == 1, "X: the fell queued a pass")
    # A5 the clearing pass: physics took the trunk + most leaves; two leaves stuck (deco) stay
    for k in oak:
        api.wb[(WORLD,) + k] = "Empty"
    stuck = [(19, 84, 20), (21, 85, 21)]
    for k in stuck:
        api.wb[(WORLD,) + k] = "Plant_Leaves_Oak"
    K.check(fire(Coop, "break", 19, 84, 20, block="Plant_Leaves_Oak") and notes()[-1] == ("Coop", "This tree is growing back.")
            and fire(Skyy, "break", 19, 84, 20, block="Plant_Leaves_Oak"), "X A5: another player's / the feller's own break of a waiting tree block is refused 'This tree is growing back.'")
    tick(TA + 2999)
    K.check(not api.breaks, "X A5: nothing is cleared before tree.clearSec")
    tick(TA + 3000)
    K.check(len(api.breaks) == 1 and api.breaks[0][0] == "Skyy" and sorted(api.breaks[0][1]) == sorted(stuck) and api.breaks[0][2] == [False, False]
            and all(api.wb[(WORLD,) + k] == "Empty" for k in stuck) and int(Fell.CLEARED.get()) == 2,
            "X A5: after 3 s the 2 stuck leaves (only those, air skipped) are broken AS THE FELLER - real BreakBlockEvents our guard let through inside the clearing call: %s" % api.breaks)
    K.check(fire(Skyy, "break", 19, 84, 20, block="Plant_Leaves_Oak"), "X A5: ... and outside that call the spot is refused again")
    # A3 restart mid-timer: the tree comes back from regen/ (shape + G) and stays protected
    before_ = (int(t_.due), int(t_.shape.n), str(t_.sid))
    Rgn.shutdown()
    r_ = str(Rgn.start(Paths.get(rdir)))
    t2_ = tr(WORLD, 20, 80, 20)
    K.check(t2_ is not None and (int(t2_.due), int(t2_.shape.n), str(t2_.sid)) == before_ and all(tr(WORLD, *k) == t2_ for k in oak),
            "X A3: RESTART mid-timer - the felled tree is back from regen/ (same shape + time), every block waiting: %s" % r_[:120])
    K.check(fire(Coop, "break", 20, 82, 20, block="Wood_Oak_Trunk"), "X A3: ... still protected after the restart")
    # A4 respawn: trunks bottom up, then leaves; a player in one cell = wait
    api.occ.add((WORLD, 20, 82, 20))
    nw0 = len(api.writes)
    tick(TA + 45000)
    K.check(tr(WORLD, 20, 80, 20) is not None and len(api.writes) == nw0 and int(tr(WORLD, 20, 80, 20).tries) == 1, "X A4: a player inside the tree - it waits (retry every 1 s)")
    api.occ.clear()
    tick(TA + 46000)
    ws = [w_ for w_ in api.writes[nw0:]]
    K.check(tr(WORLD, 20, 80, 20) is None and len(ws) == len(oak) and [w_[4] for w_ in ws[:5]] == ["Wood_Oak_Trunk"] * 5 and [w_[2] for w_ in ws[:5]] == [80, 81, 82, 83, 84]
            and all(w_[4] == "Plant_Leaves_Oak" for w_ in ws[5:]) and all(api.wb[(WORLD,) + k] == v for k, v in oak.items()) and jl(WORLD)[-1].startswith("W 20 80 20 logs "),
            "X A4: the player stepped out - the WHOLE tree is written in one pass, trunks bottom up then leaves, W line")
    K.check(not mine(Skyy, WORLD, 20, 80, 20, block="Wood_Oak_Trunk") and tr(WORLD, 20, 80, 20) is not None, "X A4: ... and can be felled again")
    drain()
    # occupied for 30 tries -> written without that cell, which follows as its own waiting block
    for k in oak:
        api.wb[(WORLD,) + k] = "Empty"
    api.occ.add((WORLD, 20, 83, 20))
    t3_ = tr(WORLD, 20, 80, 20)
    due3 = int(t3_.due)
    for i in range(31):
        tick(due3 + 1000 * i)
    K.check(tr(WORLD, 20, 80, 20) is None and api.wb[(WORLD, 20, 83, 20)] == "Empty" and waiting(WORLD, 20, 83, 20) and str(Rgn.at(WORLD, 20, 83, 20).orig) == "Wood_Oak_Trunk"
            and api.wb[(WORLD, 20, 84, 20)] == "Wood_Oak_Trunk", "X A4: after 30 tries the tree is written WITHOUT the occupied cell; that cell waits as its own block")
    api.occ.clear()
    tick(due3 + 40000)
    K.check(api.wb[(WORLD, 20, 83, 20)] == "Wood_Oak_Trunk" and not waiting(WORLD, 20, 83, 20), "X A4: ... and follows once free")
    # a cell changed by hand is left + logged; an unloaded cell = the whole tree waits (all or nothing)
    mine(Skyy, WORLD, 20, 80, 20, block="Wood_Oak_Trunk")
    drain()
    for k in oak:
        api.wb[(WORLD,) + k] = "Empty"
    api.wb[(WORLD, 18, 84, 18)] = "Rock_Stone"
    api.unl.add((WORLD, 20, 81, 20))   # fixer: a trunk cell (read early in the shape order)
    t4_ = tr(WORLD, 20, 80, 20)
    nw0 = len(api.writes)
    nr0 = len(api.reads)
    tick(int(t4_.due))
    K.check(tr(WORLD, 20, 80, 20) is not None and len(api.writes) == nw0, "X A4: one cell in an unloaded chunk - nothing is written (all or nothing)")
    nr1 = len(api.reads)
    K.check(int(t4_.next) == int(t4_.due) + 5000 and nr1 - nr0 < 10, "X fixer F2: an unloaded tree stops reading at the first unloaded cell (%d of %d reads) and waits 5 s" % (nr1 - nr0, len(oak)))
    tick(int(t4_.due) + 1000)
    K.check(len(api.reads) - nr1 < 5 and len(api.writes) == nw0, "X fixer F2: ... the next passes inside the 5 s read nothing of it (%d reads)" % (len(api.reads) - nr1))
    api.unl.clear()
    logged()
    tick(int(t4_.due) + 5000)
    K.check(tr(WORLD, 20, 80, 20) is None and api.wb[(WORLD, 18, 84, 18)] == "Rock_Stone" and any("hold something else" in l for l in logged()) and int(Fell.LEFT.get()) == 1,
            "X A4: loaded again - written; the cell an admin changed is left as it is (logged)")
    api.wb[(WORLD, 18, 84, 18)] = "Plant_Leaves_Oak"
    # A4 after an unclean stop: the tree grew back (W line) but the chunk was not saved -> written again at the next start
    Rgn.shutdown()
    for k in oak:
        api.wb[(WORLD,) + k] = "Empty"
    Rgn.start(Paths.get(rdir))
    K.check(Rgn.rw(WORLD, False) is not None and Rgn.rw(WORLD, False).tcheck.size() == 1, "X A4: a grown-back tree is re-checked after a start (W line)")
    tick(int(t4_.due) + 5000)
    K.check(all(api.wb[(WORLD,) + k] == v for k, v in oak.items()) and int(Fell.AGAIN.get()) == 1 and Rgn.rw(WORLD, False).tcheck.size() == 0,
            "X A4: its origin was still AIR - the tree is written again (V-line style re-check)")
    # A3 compaction: 30 min later the shape is no longer named -> dropped from <world>.shapes
    Dep.CLOCK = JLong(int(t4_.due) + 3600000)
    Rgn.rw(WORLD, False).snapshot(True)
    K.check(not os.path.isfile(shf) or ("S " + sid) not in open(shf, encoding="utf8").read(), "X A3: the 60 s snapshot drops a shape no tree names any more")
    T1 = int(t4_.due) + 3600000
    Dep.CLOCK = JLong(T1)
    # A1 shapes: 2x2 thick tree, branches + roots, two touching trees of different woods, leaves of another wood
    thick = tree(WORLD, 40, 80, 40, h=6, thick=True)
    c_ = mine(Skyy, WORLD, 40, 80, 40, block="Wood_Oak_Trunk")
    drain()
    K.check(not c_ and int(tr(WORLD, 40, 80, 40).shape.n) == len(thick) and tr(WORLD, 41, 80, 41) == tr(WORLD, 40, 80, 40), "X A1: a 2x2 thick tree - all 4 trunks (the other base logs too) + leaves")
    for k in thick:
        if k[1] > 80:
            api.wb[(WORLD,) + k] = "Empty"
    del api.breaks[:]
    tick(T1 + 3000)
    K.check(len(api.breaks) == 1 and sorted(api.breaks[0][1]) == [(40, 80, 41), (41, 80, 40), (41, 80, 41)] and api.breaks[0][2] == [False] * 3,
            "X A5: the 3 other base logs of the thick tree (they keep their support) are cleared as the feller: %s" % api.breaks)
    br = tree(WORLD, 60, 80, 60, extra=(((61, 82, 60), "Wood_Oak_Branch_Short"), ((60, 79, 60), "Wood_Oak_Roots"), ((61, 79, 61), "Wood_Oak_Roots")))
    api.wb[(WORLD, 60, 79, 60)] = "Wood_Oak_Roots"
    mine(Skyy, WORLD, 60, 81, 60, block="Wood_Oak_Trunk")
    drain()
    t5_ = tr(WORLD, 60, 81, 60)
    K.check(t5_ is not None and int(t5_.shape.n) == len(br) and tr(WORLD, 61, 82, 60) == t5_ and tr(WORLD, 60, 79, 60) == t5_ and tr(WORLD, 61, 79, 61) == t5_,
            "X A1: branches + roots (a mid-trunk cut takes the trunk BELOW too - the whole tree)")
    oakb = tree(WORLD, 80, 80, 80)
    birch = tree(WORLD, 83, 80, 80, wood="Birch", leaves="Plant_Leaves_Birch")
    api.wb[(WORLD, 82, 80, 80)] = "Wood_Birch_Trunk"
    mine(Skyy, WORLD, 80, 80, 80, block="Wood_Oak_Trunk")
    drain()
    t6_ = tr(WORLD, 80, 80, 80)
    K.check(t6_ is not None and all(tr(WORLD, *k) is None for k, v in birch.items() if v.startswith("Wood_Birch") or v == "Plant_Leaves_Birch")
            and tr(WORLD, 82, 80, 80) is None, "X A1: two touching trees of different woods stay separate (no birch log / birch leaf taken)")
    # cap: a tree bigger than tree.maxBlocks is refused (no drop), logged once; never a hole
    Cfg.TREE_MAX = 50
    big = tree(WORLD, 100, 80, 100, h=8, thick=True)
    notes()
    logged()
    c_ = fire(Skyy, "break", 100, 80, 100, block="Wood_Oak_Trunk")
    K.check(c_ and tr(WORLD, 100, 80, 100) is None and notes()[-1] == ("Skyy", "This tree is too big to regrow - tell an admin.")
            and any("bigger than tree.maxBlocks" in l for l in logged()) and int(Fell.BIG.get()) == 1, "X A1: %d blocks > tree.maxBlocks 50 - the cut is REFUSED (no drop), logged" % len(big))
    Cfg.TREE_MAX = 6000
    # fixer F3: a vanilla-giant-sized tree (Zone5 prefabs 4436 blocks, Redwood 84 high, Oak Stage8 43 wide) is felled and grows back whole
    gx, gy, gz = 400, 20, 400
    giant = {}
    for dy in range(90):
        for dx in range(7):
            for dz in range(7):
                giant[(gx + dx, gy + dy, gz + dz)] = "Wood_Oak_Trunk"
    for i in range(1, 23):
        giant[(gx + 6 + i, gy + 40, gz + 3)] = "Wood_Oak_Trunk"   # a branch reaching 28 out from the cut log
    for dx in range(-2, 9):
        for dz in range(-2, 9):
            for dy in (90, 91):
                giant[(gx + dx, gy + dy, gz + dz)] = "Plant_Leaves_Oak"
    for k, v in giant.items():
        api.wb[(WORLD,) + k] = v
    K.check(len(giant) > 4436, "X fixer F3: the giant test tree has %d blocks" % len(giant))
    c_ = mine(Skyy, WORLD, gx, gy, gz, block="Wood_Oak_Trunk")
    tg_ = tr(WORLD, gx, gy, gz)
    K.check(not c_ and tg_ is not None and int(tg_.shape.n) == len(giant) and int(Fell.BIG.get()) == 1,
            "X fixer F3: a %d-block tree, 90 high, a branch 28 out, is FELLED at the default 6000 (not refused)" % len(giant))
    drain()
    for k in giant:
        api.wb[(WORLD,) + k] = "Empty"
    # finisher (re-critic F1): the respawn writes at most regen.passBatch blocks per pass, the rest 50 ms later; the tree stays a waiting
    # spot until its last block; a player stepping into a not yet written cell between two passes -> that cell waits on its own
    nw0 = len(api.writes)
    Dep.CLOCK = JLong(int(tg_.due) + 1)
    P("ZTicker")().run()
    drain()
    per = [len(api.writes) - nw0]
    mid_ok = tr(WORLD, gx, gy, gz) is not None and int(tg_.cur) > 0 and tr(WORLD, gx + 8, gy + 91, gz + 8) is not None and len(api.lat) > 0
    lk = (gx + 8, gy + 91, gz + 8)   # a top leaf: written in the last pass
    api.occ.add((WORLD,) + lk)
    for _i in range(80):
        if not api.lat:
            break
        n1 = len(api.writes)
        while api.lat:
            api.lat.pop(0).run()
        drain()
        per.append(len(api.writes) - n1)
    api.occ.clear()
    K.check(mid_ok and max(per) <= int(Cfg.PASS) and sum(per) >= len(giant) - 1 and len(per) >= (len(giant) + int(Cfg.PASS) - 1) // int(Cfg.PASS),
            "X finisher F1: the %d-block tree is written over %d passes of at most regen.passBatch %d (%s...), still waiting mid-write" % (len(giant), len(per), int(Cfg.PASS), per[:4]))
    K.check(tr(WORLD, gx, gy, gz) is None and all(api.wb[(WORLD,) + k] == v for k, v in giant.items() if k != lk) and api.wb[(WORLD,) + lk] == "Empty"
            and waiting(WORLD, *lk) and int(tg_.cur) == 0, "X finisher F1: ... whole but the cell a player stepped into mid-write - that one waits on its own")
    tick(int(Dep.CLOCK) + 2000)
    K.check(api.wb[(WORLD,) + lk] == "Plant_Leaves_Oak" and not waiting(WORLD, *lk), "X finisher F1: ... and follows once free (the tree grows back whole)")
    jl_ = jl(WORLD)
    K.check(any(l.startswith("S ") and l.split()[2] == str(len(giant)) for l in open(os.path.join(rdir, WORLD + ".shapes"), encoding="utf8").read().splitlines()),
            "X fixer F3: its shape (more than 4000 lines) is in <world>.shapes")
    rwG_ = Rgn.rw(WORLD, False)
    sh_ = JClass(PKG + "ZShape")
    K.check(sh_.fromOneLine("x", "5000", ";".join(["0,0,0,Wood_Oak_Trunk,0"] * 5000)) is not None, "X fixer F3: a shape of 5000 blocks reads back (cap 12000)")
    # a tree that reaches into the town (FULL region) is refused whole
    edge = tree(WORLD, 198, 80, 205, h=5)
    c_ = fire(Skyy, "break", 198, 80, 205, block="Wood_Oak_Trunk")
    K.check(c_ and tr(WORLD, 198, 80, 205) is None and notes()[-1] == ("Skyy", "This area is protected.") and int(Fell.TOWN.get()) == 1,
            "X A0: a tree whose leaves reach into the town is refused WHOLE (never half a tree)")
    # A6 times by wood
    for x_, wood, sec in ((120, "Gumboab", 60), (130, "Redwood", 90), (140, "Pine", 60)):
        tree(WORLD, x_, 80, 20, wood=wood, leaves="Plant_Leaves_Autumn")
        tn_ = int(Dep.CLOCK)
        mine(Skyy, WORLD, x_, 80, 20, block="Wood_%s_Trunk" % wood)
        drain()
        K.check(tr(WORLD, x_, 80, 20) is not None and int(tr(WORLD, x_, 80, 20).due) == tn_ + 1000 * sec and int(tr(WORLD, x_, 80, 20).group) == (0 if wood == "Pine" else Cfg.group(wood)),
                "X A6: %s grows back after %d s" % (wood, sec))
    # finisher (re-critic F2): regrow.logs 0 switches off only woods with NO zone; a zone wood keeps its tree.sec row
    lg0 = Cfg.REGROW.get("logs")
    Cfg.REGROW.put("logs", JArray(JClass("java.lang.Object"))([JClass("java.lang.Integer")(0), "none"]))
    tree(WORLD, 170, 80, 20)
    tree(WORLD, 180, 80, 20, wood="Pine", leaves="Plant_Leaves_Autumn")
    tn_ = int(Dep.CLOCK)
    mine(Skyy, WORLD, 170, 80, 20, block="Wood_Oak_Trunk")
    mine(Skyy, WORLD, 180, 80, 20, block="Wood_Pine_Trunk")
    drain()
    K.check(tr(WORLD, 170, 81, 20) is not None and int(tr(WORLD, 170, 81, 20).due) == tn_ + 45000 and tr(WORLD, 180, 81, 20) is None,
            "X finisher F2: regrow.logs 0 - an Oak (Zone 1) still fells + grows back after tree.sec1 45 s; a Pine (no zone) breaks like vanilla")
    Cfg.REGROW.put("logs", lg0)
    tr(WORLD, 170, 81, 20).force = True   # back at once (the later crop checks count writes)
    tick(int(Dep.CLOCK))
    # builder mode: no fell; a mob fell clears to air
    tree(WORLD, 150, 80, 20)
    Bld.set(Bd["u"], "Builder", True)
    K.check(not mine(Bd, WORLD, 150, 80, 20, block="Wood_Oak_Trunk") and tr(WORLD, 150, 81, 20) is None, "X: builder mode - a cut starts no regrow")
    Bld.set(Bd["u"], "Builder", False)
    mt = tree(WORLD, 160, 80, 20)
    api.wb[(WORLD, 160, 80, 20)] = "Wood_Oak_Trunk"
    K.check(not fire(mob, "break", 160, 80, 20, block="Wood_Oak_Trunk", st=stG) and tr(WORLD, 160, 81, 20) is not None, "X: a mob's cut fells the tree too")
    api.wb[(WORLD, 160, 80, 20)] = "Empty"
    drain()
    nb0, nw0 = len(api.breaks), len(api.writes)
    tick(int(Dep.CLOCK) + 3000)
    K.check(not any(c[0] == 160 for b_ in api.breaks[nb0:] for c in b_[1]) and any(w_[:4] == (WORLD, 160, 81, 20) and w_[4] == "Empty" for w_ in api.writes[nw0:]), "X A5: no feller (a mob) - the leftovers are set to air (no drop)")
    # A2 write failures cancel the break: shapes file / journal blocked
    WF = "zone_fail"
    wF, stF = mkworld(WF)
    api.worlds[WF] = wF
    Cfg.WORLDS = WORLD + "," + PLAIN + "," + WF
    Cfg.GATHERW = WORLD + "," + WF
    Fp = mkplayer(stF, "Failer", 9)
    os.makedirs(os.path.join(rdir, WF + ".shapes"), exist_ok=True)
    tree(WF, 10, 80, 10)
    jf0 = len(jl(WF))
    c_ = fire(Fp, "break", 10, 80, 10, block="Wood_Oak_Trunk")
    K.check(c_ and tr(WF, 10, 80, 10) is None and len(jl(WF)) == jf0 and "could not save" in notes()[-1][1], "X A2: the shapes file cannot be written - the cut is CANCELLED (no drop), nothing journaled")
    os.rmdir(os.path.join(rdir, WF + ".shapes"))
    Rgn.rw(WF, False).close()
    os.makedirs(os.path.join(rdir, WF + ".journal"), exist_ok=True)
    c_ = fire(Fp, "break", 10, 80, 10, block="Wood_Oak_Trunk")
    K.check(c_ and tr(WF, 10, 80, 10) is None and not waiting(WF, 10, 81, 10), "X A2: the journal cannot be written - CANCELLED, no position left waiting")
    os.rmdir(os.path.join(rdir, WF + ".journal"))
    # a cut another mod cancelled: the trunk is still there at the first pass -> the tree is forgotten (R)
    tree(WF, 30, 80, 30)
    c_ = fire(Fp, "break", 30, 80, 30, block="Wood_Oak_Trunk")
    drain()
    K.check(not c_ and tr(WF, 30, 80, 30) is None and jl(WF)[-1] == "R 30 80 30", "X: another mod cancelled the cut (the trunk still stands) - the tree is forgotten, R line")
    # regen.maxDepleted: a felled tree is ONE entry
    rwG = Rgn.rw(WORLD, False)
    md0 = int(Cfg.MAXDEP)
    Cfg.MAXDEP = rwG.dep.size() + rwG.trees.size()
    oldest = min((t for t in rwG.trees.values()), key=lambda t: int(t.due))
    mine(Skyy, WORLD, 9, 90, 12)
    K.check(bool(oldest.force) and int(oldest.due) == 0, "X: regen.maxDepleted - a felled tree counts as one entry (the oldest, a tree, comes back early)")
    Cfg.MAXDEP = md0
    drain()

    # ---------------------------------------------------------------- A7 crops
    TC_ = int(Dep.CLOCK)
    api.wb[(WORLD, 50, 85, 50)] = C1
    K.check(fire(Skyy, "break", 50, 85, 50, block=C1) and notes()[-1] == ("Skyy", "Not ripe yet.") and fire(Skyy, "dig", 50, 85, 50, block=C1)
            and fire(Skyy, "use", 50, 85, 50, block=C1) and not waiting(WORLD, 50, 85, 50), "X A7: an UNRIPE crop - break, dig crack, F-harvest refused 'Not ripe yet.'")
    c_ = mine(Skyy, WORLD, 51, 85, 50, block=CF)
    d_ = Rgn.at(WORLD, 51, 85, 50)
    K.check(not c_ and d_ is not None and str(d_.type) == "crops" and str(d_.ph) == C1 and int(d_.due) == TC_ + 10000 and jl(WORLD)[-1].startswith("D 51 85 50 %s crops " % CF),
            "X A7: a RIPE crop breaks (drop / XP once) - D line, placeholder = its Stage1 block (BlockType state keys)")
    drain()
    K.check(api.wb[(WORLD, 51, 85, 50)] == C1, "X A7: ... back to its first stage")
    K.check(fire(Coop, "break", 51, 85, 50, block=C1) and notes()[-1] == ("Coop", "Not ripe yet."), "X A7: the waiting crop refuses 'Not ripe yet.'")
    api.wb[(WORLD, 51, 85, 50)] = CARROT   # vanilla growth ticked it to another state of the same crop
    tick(TC_ + 10000)
    K.check(api.wb[(WORLD, 51, 85, 50)] == CF and not waiting(WORLD, 51, 85, 50), "X A7: ... ripe again after 10 s (another stage of the same crop still counts)")
    api.wb[(WORLD, 52, 85, 50)] = CF
    nw0 = len(api.writes)
    K.check(not fire(Skyy, "use", 52, 85, 50, block=CF) and waiting(WORLD, 52, 85, 50) and int(Rgn.at(WORLD, 52, 85, 50).state) == 3 and drain() == 0 and len(api.writes) == nw0
            and int(Rgn.HARVESTED.get()) == 1, "X A7: an F-harvest of a ripe crop is allowed and registered (no placeholder write - the engine resets the stage)")
    api.wb[(WORLD, 52, 85, 50)] = C1   # the engine's harvest
    tick(TC_ + 20000)
    K.check(api.wb[(WORLD, 52, 85, 50)] == CF and not waiting(WORLD, 52, 85, 50), "X A7: ... ripe again at the timer")
    api.wb[(WORLD, 53, 85, 50)] = CF
    fire(Skyy, "use", 53, 85, 50, block=CF)   # the harvest fails in the engine: still ripe
    nw0 = len(api.writes)
    tick(TC_ + 40000)
    K.check(api.wb[(WORLD, 53, 85, 50)] == CF and not waiting(WORLD, 53, 85, 50) and len(api.writes) == nw0, "X A7: an entry whose crop is already ripe is dropped (no write)")
    # fixer F1: a FAILED F-harvest (full inventory, a tool's Use) no longer locks the ripe crop for the whole timer
    api.wb[(WORLD, 54, 85, 50)] = CF
    TH_ = TC_ + 50000
    Dep.CLOCK = JLong(TH_)
    fire(Skyy, "use", 54, 85, 50, block=CF)
    nw0 = len(api.writes)
    tick(TH_ + 300)
    K.check(waiting(WORLD, 54, 85, 50) and len(api.writes) == nw0, "X fixer F1: inside 1 s the harvest entry stays (an engine harvest a tick later is still caught)")
    tick(TH_ + 1300)
    K.check(not waiting(WORLD, 54, 85, 50) and api.wb[(WORLD, 54, 85, 50)] == CF and len(api.writes) == nw0
            and not fire(Coop, "break", 54, 85, 50, block=CF), "X fixer F1: ... after 1 s, still ripe = the harvest failed -> dropped; the crop breaks again (not locked 10 s)")
    api.wb[(WORLD, 54, 85, 50)] = CF
    # crops in the plain protected world (no region) stay protected
    api.wb[(PLAIN, 5, 85, 5)] = CF

    # ---------------------------------------------------------------- status / info / restore / zone reset / regen off / region delete
    st_ = [str(s) for s in Rgn.status()]
    K.check(any(s.startswith("Whole trees + crops: ") and "trees felled" in s for s in st_) and any(WORLD in s and "trees down" in s for s in st_)
            and any(s.startswith("Whole-island gathering worlds: " + WORLD) for s in st_), "X: /zones status - trees down, felled / grown back, crops, the gathering worlds: %s" % st_[:4])
    rwG = Rgn.rw(WORLD, False)
    td = [t for t in rwG.trees.values()]
    K.check(len(td) >= 3, "X: trees are down before the restore (%d)" % len(td))
    res = Rgn.restore(None)
    tick(int(Dep.CLOCK) + 1000)
    K.check(int(res[0]) >= len(td) and rwG.trees.size() == 0, "X: /zones restore all - every felled tree back at once (REQUIRED before a rollback)")
    # finisher (Skyy 2026-10-24 Farming XP test, SkyyCollections 0.2.33 rule): DynamicSeasons' quality ripe states Crude / Best / Epic
    K.check([str(Eng.cropState(bt(q))) for q in CQ] == ["StageFinal"] * 3 and str(Eng.cropState(bt(C1))) == "Stage1" and str(Eng.cropState(bt(CF))) == "StageFinal"
            and str(Eng.cropState(bt(CARROT))) == "default", "X finisher: Crude / Best / Epic (a Harvest drop on a crop with StageFinal) read ripe; Stage1 / planted do not")
    for i_, q in enumerate(CQ):
        TQ_ = int(Dep.CLOCK)
        c_ = mine(Skyy, WORLD, 60 + i_, 85, 50, block=q)
        d_ = Rgn.at(WORLD, 60 + i_, 85, 50)
        K.check(not c_ and d_ is not None and str(d_.orig) == q and str(d_.ph) == C1 and int(d_.due) == TQ_ + 10000,
                "X finisher: a ripe %s crop breaks (not 'Not ripe yet.') - waiting entry, placeholder Stage1" % q.split("_")[-1])
        drain()
        tick(TQ_ + 10000)
        K.check(api.wb[(WORLD, 60 + i_, 85, 50)] == q and not waiting(WORLD, 60 + i_, 85, 50), "X finisher: ... the %s crop is back ripe after 10 s" % q.split("_")[-1])
    api.wb[(WORLD, 64, 85, 50)] = CQ[0]
    h0 = int(Rgn.HARVESTED.get())
    K.check(not fire(Skyy, "use", 64, 85, 50, block=CQ[0]) and waiting(WORLD, 64, 85, 50) and int(Rgn.at(WORLD, 64, 85, 50).state) == 3 and int(Rgn.HARVESTED.get()) == h0 + 1,
            "X finisher: an F-harvest of a Crude crop is allowed and registered")
    api.wb[(WORLD, 64, 85, 50)] = C1
    tick(int(Dep.CLOCK) + 11000)
    K.check(api.wb[(WORLD, 64, 85, 50)] == CQ[0] and not waiting(WORLD, 64, 85, 50), "X finisher: ... ripe (Crude) again at the timer")
    # the zone reset bridge (SkyyWorldGen 0.7.10): a felled tree is dropped with its shape line and put back by the undo
    tree(WORLD, 20, 80, 20)
    mine(Skyy, WORLD, 20, 80, 20, block="Wood_Oak_Trunk")
    drain()

    @JImplements("java.util.function.IntBinaryOperator")
    class Own(object):
        @JOverride
        def applyAsInt(self, a, b):
            return 1
    sp = os.path.join(scratch, "x", "tied", "zones.spool")
    txt = str(Box.drop(WORLD, Own(), sp))
    K.check(tr(WORLD, 20, 80, 20) is None and "\nG 20 80 20 logs " in "\n" + txt and "\nS " in "\n" + txt and txt.index("\nG 20 80 20 ") > txt.index("S ") and os.path.isfile(sp), "X: zone reset drops the felled tree (shape line + G line, spooled first)")
    n_ = int(Box.restore(WORLD, txt))
    K.check(n_ >= 1 and tr(WORLD, 20, 80, 20) is not None and int(tr(WORLD, 20, 82, 20).shape.n) > 5, "X: ... the undo puts it back waiting")
    # /zones info + /zones list (the new lines)
    Cmds = P("ZCmds")

    def said(p_):
        r_ = [str(m.getRawText()) for m in p_["pr"].msgs]
        p_["pr"].msgs.clear()
        return r_

    def stand(p_, x, y, z):
        p_["st"].comps.get(p_["ref"]).put(TC.getComponentType(), TC(V3D(x + 0.5, y + 1.0, z + 0.5), R3(0.0, 0.0, 0.0)))
    said(Skyy)
    stand(Skyy, 20, 80, 20)
    Cmds.info(Skyy["ref"], stG, Skyy["pr"], wG)
    l_ = said(Skyy)
    K.check(any(x.startswith("Area: Gathering area (whole island) | world whole-island gathering") for x in l_) and any(x.startswith("Tree down: grows back in ") and "(shape " in x for x in l_),
            "X: /zones info on a felled tree - 'Area: Gathering area (whole island)' + 'Tree down: grows back in N s (shape M blocks)': %s" % l_)
    api.wb[(WORLD, 55, 85, 50)] = CF
    stand(Skyy, 55, 85, 50)
    Cmds.info(Skyy["ref"], stG, Skyy["pr"], wG)
    l_ = said(Skyy)
    K.check(any(x.startswith("Crop: ripe (hoes") for x in l_), "X: /zones info on a ripe crop - 'Crop: ripe' + the hoe / watering note: %s" % [x for x in l_ if "Crop" in x])
    mine(Skyy, WORLD, 55, 85, 50, block=CF)
    drain()
    Cmds.info(Skyy["ref"], stG, Skyy["pr"], wG)
    l_ = said(Skyy)
    K.check(any(x.startswith("Crop: not ripe - ripe again in ") for x in l_), "X: /zones info on a waiting crop: %s" % [x for x in l_ if "Crop" in x])
    stand(Skyy, 210, 90, 210)
    Cmds.info(Skyy["ref"], stG, Skyy["pr"], wG)
    l_ = said(Skyy)
    K.check(any(x.startswith("Area: Town - protected (region town)") for x in l_), "X: /zones info in the town - 'Town - protected': %s" % l_[:2])
    Cmds.list(Skyy["pr"], WORLD)
    l_ = said(Skyy)
    K.check(l_ and "whole-island gathering area (outside regions copper, iron" in l_[0], "X: /zones list names the gathering world: %s" % l_[:1])
    K.check(" (one cut fells the WHOLE tree" in str(Cmds.grows("logs")) and "only ripe crops" in str(Cmds.grows("crops")), "X: the region type notes for logs / crops")
    # A3: a 0.2.x journal (D / V / R + a torn last line) is read unchanged next to the 0.3.0 lines; a bad shape block = a bad G line, kept as .bad
    OW = "old_world"
    open(os.path.join(rdir, OW + ".journal"), "w", encoding="utf8").write(
        "D 1 90 1 Ore_Copper_Stone copper %d 0 Rock_Bedrock\nD 2 90 1 Ore_Iron_Stone iron %d 0 Rock_Bedrock\nR 2 90 1\nV 3 90 1 Ore_Copper_Stone copper %d 0 Rock_Bedrock\nD 4 90 1 Ore_Cop"
        % (T0 + 999999, T0 + 999999, T0))
    open(os.path.join(rdir, "bad_world.shapes"), "w", encoding="utf8").write("S abc 2\n0 0 0 Wood_Oak_Trunk 0\n")
    open(os.path.join(rdir, "bad_world.journal"), "w", encoding="utf8").write("G 5 80 5 logs %d abc 1\n" % (T0 + 99999))
    Rgn.shutdown()
    logged()
    r_ = str(Rgn.start(Paths.get(rdir)))
    rw_o = Rgn.rw(OW, False)
    lg_ = logged()
    K.check(rw_o is not None and rw_o.dep.size() == 1 and rw_o.check.size() == 1 and waiting(OW, 1, 90, 1) and not waiting(OW, 2, 90, 1) and any("cut off" in l for l in lg_),
            "X A3: a 0.2.x journal (D / R / V + a torn line) is read unchanged by 0.3.0: %s" % r_[:100])
    K.check((Rgn.rw("bad_world", False) is None or Rgn.rw("bad_world", False).trees.size() == 0) and any("unreadable tree shapes" in l for l in lg_)
            and any(f.startswith("bad_world.shapes.bad-") for f in os.listdir(rdir)), "X A3: a broken shape block is skipped (its G line counted bad), the file kept as .bad")
    K.check(Rgn.rw(WORLD, False).trees.size() >= 1 and tr(WORLD, 20, 80, 20) is not None, "X A3: ... the gathering world's felled trees came back too")
    # region delete: a tree in a skyblock logs region of the PLAIN world comes back at once
    Sto.create("grove", PLAIN, "skyblock", JArray(JInt)([0, 60, 0, 30, 120, 30]), "Skyy")
    Sto.set("grove", "types", "logs", "Skyy")
    pp = mkplayer(stP, "Plainer", 7)
    tree(PLAIN, 10, 80, 10)
    c_ = mine(pp, PLAIN, 10, 80, 10, block="Wood_Oak_Trunk")
    drain()
    K.check(not c_ and tr(PLAIN, 10, 80, 10) is not None, "X: a skyblock region with logs (not a gathering world) fells whole trees too")
    Sto.delete("grove", "Skyy")
    tick(int(Dep.CLOCK) + 1000)
    K.check(tr(PLAIN, 10, 80, 10) is None and api.wb[(PLAIN, 10, 80, 10)] == "Wood_Oak_Trunk", "X: the region deleted - its tree comes back at once")
    Cfg.REGEN_ON = False
    tick(int(Dep.CLOCK) + 1000)
    K.check(Rgn.rw(WORLD, False).trees.size() == 0, "X: regen.enabled off - every tree back at once")
    Cfg.REGEN_ON = True
    # ================================================================================================================ 0.3.1 (spec 7 B1-B7)
    Fair, Scafs, ScafC, RegKit = P("ZFair"), P("ZScafs"), P("ZScaf"), P("ZRegKit")
    SCAF = "Skyy_Scaffold"
    NOPE = "Scaffolding can't go here."
    TB = int(Dep.CLOCK) + 100000
    Dep.CLOCK = JLong(TB)
    Cfg.ABUSE_ON = False
    Cfg.GATES_ON = True
    Cfg.bridge().remove("skill:fn:level")
    perms[(str(Skyy["u"]), "skyyzones.admin")] = True
    notes()
    logged()
    said(Skyy)

    def place(p, x, y, z, it=SCAF):
        e_ = PLBE(item(it), V3I(x, y, z), None)
        Msg.LAST.clear()
        gP.handle(0, p["ch"], p["st"], cb, e_)
        return bool(e_.isCancelled())

    def put(p, x, y, z, it=SCAF, wn=WORLD):
        c_ = place(p, x, y, z, it)
        if not c_:
            api.wb[(wn, x, y, z)] = it   # the engine places it
        return c_

    def sc(wn, x, y, z):
        return Rgn.scafAt(wn, x, y, z)

    def cmd(p, *a):
        said(p)
        Cmds.run(p["ref"], p["st"], p["pr"], wG if p["st"] == stG else wP, JArray(JString)(list(a)))
        return said(p)
    U_S = str(Skyy["u"])

    # ---------------------------------------------------------------- B1 the allow / deny matrix
    stand(Skyy, 700, 118, 702)
    c_ = place(Skyy, 700, 120, 700)
    j_ = jl(WORLD)
    s_ = sc(WORLD, 700, 120, 700)
    K.check(not c_ and s_ is not None and int(s_.state) == 0 and int(s_.due) == TB + 8000 and j_[-1] == "T 700 120 700 %s %d %s" % (SCAF, TB + 8000, U_S)
            and api.wb.get((WORLD, 700, 120, 700), "Empty") == "Empty",
            "X B1/B2: Scaffolding in the gathering world is allowed; the T line is written BEFORE the engine places it (the cell still air): %s" % j_[-1:])
    api.wb[(WORLD, 700, 120, 700)] = SCAF
    drain()
    K.check(int(s_.state) == 1 and str(s_.id) == SCAF and int(ScafC.PLACED.get()) == 1, "X B2: the first pass reads the placed block (state 1)")
    api.wb[(WORLD, 701, 120, 700)] = "Rock_Stone"
    K.check(place(Skyy, 701, 120, 700) and notes()[-1] == ("Skyy", NOPE) and sc(WORLD, 701, 120, 700) is None, "X B1: the cell must be air")
    del api.wb[(WORLD, 701, 120, 700)]
    stand(Skyy, 197, 118, 212)
    K.check(place(Skyy, 199, 120, 210) and notes()[-1] == ("Skyy", NOPE), "X B1: next to the town (a neighbour is FULL) - refused (never touching a town)")
    K.check(place(Skyy, 201, 120, 210) and notes()[-1] == ("Skyy", NOPE), "X B1: inside the town - refused")
    stand(Skyy, 700, 118, 702)
    K.check(place(Skyy, 712, 120, 700) and notes()[-1] == ("Skyy", "Too far away."), "X B1: beyond scaffold.reach (6) of the eyes - 'Too far away.'")
    api.occ.add((WORLD, 702, 120, 700))
    K.check(place(Skyy, 702, 120, 700) and notes()[-1] == ("Skyy", NOPE), "X B1: a player inside the cell - refused")
    api.occ.clear()
    api.wb[(WORLD, 703, 119, 700)] = "Ore_Copper_Stone"
    mine(Skyy, WORLD, 703, 119, 700)
    K.check(place(Skyy, 703, 119, 700) and notes()[-1] == ("Skyy", "Growing back - wait a moment."), "X B1: a waiting (mined) spot - refused")
    drain()
    K.check(place(Skyy, 702, 120, 700, it="Rock_Stone") and notes()[-1] == ("Skyy", "You can't place blocks in this area."),
            "X B1: any other block in the gathering world - the 0.3.0 refusal")
    Cfg.SCAF_ON = False
    K.check(place(Skyy, 702, 120, 700) and notes()[-1] == ("Skyy", NOPE), "X B1: scaffold.on off - refused")
    Cfg.SCAF_ON = True
    # placeAllow: none / a list / default (the scaffold.ids row)
    Sto.create("quarry", WORLD, "skyblock", JArray(JInt)([760, 60, 700, 800, 140, 740]), "Skyy")
    Sto.set("quarry", "types", "copper", "Skyy")
    stand(Skyy, 770, 118, 722)
    K.check(not put(Skyy, 770, 120, 720), "X B1: a SKYBLOCK region with no placeAllow line - the scaffold.ids row (Skyy_Scaffold)")
    K.check(str(Sto.set("quarry", "placeAllow", "none", "Skyy")).startswith("Region quarry: placeAllow = none") and place(Skyy, 771, 120, 720)
            and notes()[-1] == ("Skyy", NOPE), "X B1: placeAllow none - nothing")
    l_ = cmd(Skyy, "place", "add", "quarry", "Wood_Oak_Planks")
    K.check(any("placeAllow = Wood_Oak_Planks" in x for x in l_) and place(Skyy, 771, 120, 720) and not put(Skyy, 772, 120, 720, it="Wood_Oak_Planks")
            and sc(WORLD, 772, 120, 720) is not None, "X B1: /zones place add quarry Wood_Oak_Planks - planks only (they vanish too): %s" % l_)
    l_ = cmd(Skyy, "place", "add", "quarry", SCAF)
    K.check(any("placeAllow = Wood_Oak_Planks,Skyy_Scaffold" in x for x in l_) and not put(Skyy, 773, 120, 720), "X B1: ... + Skyy_Scaffold: %s" % l_)
    l_ = cmd(Skyy, "place", "remove", "quarry", "Wood_Oak_Planks")
    K.check(any("placeAllow = Skyy_Scaffold" in x for x in l_) and place(Skyy, 774, 120, 720, it="Wood_Oak_Planks")
            and notes()[-1] == ("Skyy", "You can't place blocks in this area."), "X B1: /zones place remove - planks refused again: %s" % l_)
    l_ = cmd(Skyy, "place", "add", "quarry", "Ore_Copper_Stone")
    K.check(any("resource type copper" in x for x in l_) and "Ore_Copper" not in str(Sto.get("quarry").placeShown()), "X B1 (spec 7 X1): a resource block is never placeable: %s" % l_)
    l_ = cmd(Skyy, "place", "add", "quarry", "No_Such_Block")
    K.check(any("No block 'No_Such_Block'" in x for x in l_), "X B1: an unknown block id is refused: %s" % l_)
    # fixer 2 (critic: a chest / bench on a place list vanished WITH its contents): plain blocks only
    SDx = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.StateData")
    jfield(BT, "state").set(bt("Furniture_Crude_Chest"), U.allocateInstance(SDx.class_))
    l_ = cmd(Skyy, "place", "add", "quarry", "Furniture_Crude_Chest")
    K.check(any("plain blocks only" in x for x in l_) and "Chest" not in str(Sto.get("quarry").placeShown())
            and "plain blocks only" in str(ck(Cfg.checkScafIds, "Skyy_Scaffold,Furniture_Crude_Chest")) and ck(Cfg.checkScafIds, SCAF) is None
            and Cfg.plainWhy(bt(SCAF)) is None and Cfg.plainWhy(bt("Wood_Oak_Planks")) is None,
            "X B1 (fixer 2): a block with its own data / states (a chest, bench, door, crop) is never placeable - plain blocks only: %s" % l_)
    jfield(BT, "state").set(bt("Furniture_Crude_Chest"), None)
    K.check(ck(Cfg.checkScafIds, "Skyy_Scaffold,Wood_Oak_Planks") is None and "resource type" in ck(Cfg.checkScafIds, "Ore_Iron_Stone") and ck(Cfg.checkScafIds, "") is None,
            "X B1: Server Setup scaffold.ids check (no resource blocks; empty = nothing)")
    K.check(str(Sto.set("quarry", "placeAllow", "default", "Skyy")).startswith("Region quarry: placeAllow = default") and Sto.get("quarry").extra.get("placeAllow") is None,
            "X B1: placeAllow default = the line removed (the scaffold.ids row again)")
    # an unprotected world: our Scaffolding never goes there (it would never vanish); a vanilla block places as usual
    wF, stF = mkworld("free_world")
    api.worlds["free_world"] = wF
    Fr = mkplayer(stF, "Freer", 9)
    K.check(place(Fr, 5, 120, 5) and notes()[-1] == ("Freer", NOPE) and not place(Fr, 6, 120, 5, it="Rock_Stone"),
            "X B1: an unprotected world - Skyy_Scaffold refused, a vanilla block places as usual")
    stand(Bd, 205, 118, 212)
    Bld.set(Bd["u"], "Builder", True)
    K.check(not place(Bd, 205, 120, 210) and sc(WORLD, 205, 120, 210) is None, "X B6: builder mode places scaffolding anywhere (no timer: a normal block)")
    Bld.set(Bd["u"], "Builder", False)
    # ---------------------------------------------------------------- B2 vanish / changed / cap / cancelled / hand break / restart / restore / reset
    tick(TB + 7999)
    K.check(api.wb[(WORLD, 700, 120, 700)] == SCAF, "X B2: still there before scaffold.lifeSec")
    tick(TB + 8000)
    K.check(api.wb[(WORLD, 700, 120, 700)] == "Empty" and sc(WORLD, 700, 120, 700) is None and "R 700 120 700" in jl(WORLD) and int(ScafC.VANISHED.get()) >= 1,
            "X B2: gone after 8 s (air, R line) - no drop, no event")
    TB2 = TB + 20000
    Dep.CLOCK = JLong(TB2)
    stand(Skyy, 700, 118, 702)
    put(Skyy, 700, 121, 700)
    drain()
    api.wb[(WORLD, 700, 121, 700)] = "Rock_Stone"
    lf0 = int(ScafC.LEFT.get())
    tick(TB2 + 8000)
    K.check(api.wb[(WORLD, 700, 121, 700)] == "Rock_Stone" and sc(WORLD, 700, 121, 700) is None and int(ScafC.LEFT.get()) == lf0 + 1,
            "X B2: a cell that holds something else at vanish time is left as it is")
    del api.wb[(WORLD, 700, 121, 700)]
    Cfg.SCAF_MAX = 3
    for i_ in range(4):
        put(Skyy, 698 + i_, 120, 703)
    s0_, s1_ = sc(WORLD, 698, 120, 703), sc(WORLD, 699, 120, 703)
    K.check(s0_ is not None and s1_ is not None and bool(s0_.force) and not bool(s1_.force), "X B2: the 4th of a player over scaffold.maxPerPlayer (3) - his OLDEST is forced")
    drain()
    tick(TB2 + 9000)
    K.check(sc(WORLD, 698, 120, 703) is None and api.wb[(WORLD, 698, 120, 703)] == "Empty" and all(sc(WORLD, 699 + i_, 120, 703) is not None for i_ in range(3)),
            "X B2: ... the oldest vanished first, the other 3 stay")
    Cfg.SCAF_MAX = 24
    ca0 = int(ScafC.CANCELLED.get())
    K.check(not place(Skyy, 699, 120, 704), "X B2: a place another mod cancels (the cell stays air) ...")
    drain()
    K.check(sc(WORLD, 699, 120, 704) is None and int(ScafC.CANCELLED.get()) == ca0 + 1, "X B2: ... is forgotten at the first pass")
    put(Skyy, 701, 120, 704)
    drain()
    K.check(str(Fn(0).apply(JArray(JClass("java.lang.Object"))([WORLD, JInt(701), JInt(120), JInt(704), "break", SCAF]))) == "deny"
            and str(Fn(0).apply(JArray(JClass("java.lang.Object"))([WORLD, JInt(701), JInt(120), JInt(704), "place", SCAF]))) == "deny", "X: zones:fn:check - deny on a live scaffold")
    br0 = int(ScafC.BROKEN.get())
    K.check(not fire(Coop, "dig", 701, 120, 704, block=SCAF), "X B2: a hit on a scaffold may crack it")
    K.check(fire(Coop, "break", 701, 120, 704, block=SCAF) and api.wb[(WORLD, 701, 120, 704)] == SCAF, "X B2: a hand break is CANCELLED (no drop, no XP) ...")
    drain()
    K.check(api.wb[(WORLD, 701, 120, 704)] == "Empty" and sc(WORLD, 701, 120, 704) is None and int(ScafC.BROKEN.get()) == br0 + 1, "X B2: ... and the scaffold goes at once")
    # restart: the T lines come back, the scaffolds go at the first pass
    put(Skyy, 701, 122, 700)
    put(Skyy, 702, 122, 700)
    K.check(not place(Skyy, 703, 122, 700), "X B2 (fixer): a scaffold the engine places with another block id ...")
    api.wb[(WORLD, 703, 122, 700)] = "Wood_Oak_Planks"
    drain()
    s3_ = sc(WORLD, 703, 122, 700)
    j3_ = [l for l in jl(WORLD) if l.startswith("T 703 122 700 ")]
    K.check(s3_ is not None and str(s3_.id) == "Wood_Oak_Planks" and len(j3_) == 2 and j3_[0].split()[4] == SCAF and j3_[-1].split()[4] == "Wood_Oak_Planks",
            "X B2 (fixer): ... gets a fresh T line with the placed id at its first pass (a crash before the next snapshot still finds it): %s" % j3_)
    Rgn.shutdown()
    snp = open(os.path.join(rdir, WORLD + ".snap"), encoding="utf8").read()
    K.check(("T 701 122 700 %s " % SCAF) in snp, "X B2: the snapshot keeps the live scaffolds (T lines)")
    r_ = str(Rgn.start(Paths.get(rdir)))
    s2_ = sc(WORLD, 701, 122, 700)
    bl = ScafC.BY.get(U_S)
    K.check(s2_ is not None and int(s2_.state) == 1 and "scaffolds from before the stop" in r_ and bl is not None and bl.size() >= 2,
            "X B2: after a restart the scaffolds are back from regen/ (+ the player's list): %s" % r_[-120:])
    tick(TB2 + 60000)
    K.check(api.wb[(WORLD, 701, 122, 700)] == "Empty" and api.wb[(WORLD, 702, 122, 700)] == "Empty" and sc(WORLD, 701, 122, 700) is None,
            "X B2: ... and are removed (restart removes due T lines)")
    K.check(api.wb[(WORLD, 703, 122, 700)] == "Empty" and sc(WORLD, 703, 122, 700) is None, "X B2 (fixer): ... the other-id scaffold too")
    TB3 = TB2 + 100000
    Dep.CLOCK = JLong(TB3)
    put(Skyy, 701, 123, 700)
    drain()
    res = Rgn.restore(None)
    tick(TB3 + 1000)
    K.check(int(res[0]) >= 1 and api.wb[(WORLD, 701, 123, 700)] == "Empty", "X B7: /zones restore all removes every scaffold (REQUIRED before a rollback)")
    put(Skyy, 701, 124, 700)
    drain()
    txt2 = str(Box.drop(WORLD, Own(), os.path.join(scratch, "x", "tied", "zones2.spool")))
    spl_ = open(os.path.join(scratch, "x", "tied", "zones2.spool"), encoding="utf8").read()
    K.check(sc(WORLD, 701, 124, 700) is None and ("T 701 124 700 %s " % SCAF) in txt2 and ("T 701 124 700 %s " % SCAF) in spl_,
            "X (fixer 2): a zone reset forgets the zone's scaffolds but keeps their T lines in the reset backup (spool + returned rows)")
    nb_ = int(Box.restore(WORLD, txt2))
    s5_ = sc(WORLD, 701, 124, 700)
    f5_ = s5_ is not None and bool(s5_.force)
    tick(TB3 + 3000)
    K.check(nb_ >= 1 and f5_ and api.wb[(WORLD, 701, 124, 700)] == "Empty" and sc(WORLD, 701, 124, 700) is None,
            "X (fixer 2): the reset undo takes them back FORCED - the first pass clears the scaffold the restored land still holds (never a permanent block)")
    put(Skyy, 702, 124, 700)
    drain()
    txt3 = str(Box.drop(WORLD, Own(), os.path.join(scratch, "x", "tied", "zones3.spool")))
    api.wb[(WORLD, 702, 124, 700)] = "Rock_Stone"   # the restored land holds something else there
    Box.restore(WORLD, txt3)
    tick(TB3 + 4000)
    K.check(api.wb[(WORLD, 702, 124, 700)] == "Rock_Stone" and sc(WORLD, 702, 124, 700) is None,
            "X (fixer 2): ... a cell holding another block after the undo is left as it is (only the scaffold block is ever cleared)")
    # fixer 2 (critic: with zones.on off a scaffold place returned early - never timed, a permanent block anywhere)
    Cfg.ON = False
    stand(Skyy, 700, 118, 702)
    on1_ = not put(Skyy, 703, 124, 700) and sc(WORLD, 703, 124, 700) is not None
    stand(Skyy, 197, 118, 212)
    on2_ = place(Skyy, 199, 120, 210) and notes()[-1] == ("Skyy", NOPE)
    tick(TB3 + 20000)
    K.check(on1_ and on2_ and api.wb[(WORLD, 703, 124, 700)] == "Empty" and sc(WORLD, 703, 124, 700) is None,
            "X B1 (fixer 2): zones.on off - our Scaffolding still only goes into gathering areas and still vanishes (never a permanent block): %s %s" % (on1_, on2_))
    Cfg.ON = True
    stand(Skyy, 700, 118, 702)
    # the rate cap counts placements
    Cfg.ABUSE_ON = True
    Fair.PL.clear()
    Cfg.MAX_PER_MIN = 2
    K.check(not put(Skyy, 701, 125, 700) and not put(Skyy, 702, 125, 700) and place(Skyy, 703, 125, 700) and notes()[-1] == ("Skyy", "Slow down a little."),
            "X B2: each placement counts toward abuse.maxPerMin (2 here: the 3rd waits)")
    Cfg.MAX_PER_MIN = 300
    Cfg.ABUSE_ON = False
    Fair.PL.clear()
    tick(TB3 + 30000)

    # ---------------------------------------------------------------- B4 skill gates
    TG = TB3 + 100000
    Dep.CLOCK = JLong(TG)
    notes()
    logged()
    Cfg.WARNED.remove("noskills")   # (the 0.3.0 checks above already mined a gated lead ore once)
    for i_ in range(2):
        api.wb[(WORLD, 720 + i_, 95, 700)] = "Ore_Iron_Stone"
    K.check(not mine(Skyy, WORLD, 720, 95, 700, block="Ore_Iron_Stone") and not mine(Skyy, WORLD, 721, 95, 700, block="Ore_Iron_Stone"),
            "X B4: no SkyySkills (skill:fn:level missing) - the gates are off")
    K.check(sum(1 for l in logged() if "skill gates: SkyySkills" in l) == 1, "X B4: ... warned ONCE")
    lv = {}

    @JImplements("java.util.function.Function")
    class SkillFn(object):
        @JOverride
        def apply(self, o):
            return JInt(lv.get((str(o[0]), str(o[1])), 0))
    Cfg.bridge().put("skill:fn:level", SkillFn())
    lv[(U_S, "Mining")] = 7
    Fair.LV.clear()
    K.check(mine(Skyy, WORLD, 722, 95, 700, block="Ore_Iron_Stone") and notes()[-1] == ("Skyy", "Requires Mining 10 (you: 7).") and not waiting(WORLD, 722, 95, 700),
            "X B4: Mining 7 on Iron - 'Requires Mining 10 (you: 7).' (no drop, no regrow)")
    K.check(fire(Skyy, "dig", 722, 95, 700, block="Ore_Iron_Stone"), "X B4: ... and a hit gives no crack either")
    K.check(not mine(Skyy, WORLD, 723, 95, 700, block="Ore_Copper_Stone"), "X B4: copper has no gate")
    lv[(U_S, "Mining")] = 10
    K.check(mine(Skyy, WORLD, 724, 95, 700, block="Ore_Iron_Stone"), "X B4: the level is cached 1 s (a level-up shows after at most 1 s)")
    Dep.CLOCK = JLong(TG + 1001)
    K.check(not mine(Skyy, WORLD, 725, 95, 700, block="Ore_Iron_Stone"), "X B4: Mining 10 can (1 s later)")
    # fixer (critic: a profile switch / a join before SkyySkills loaded kept the old level 5 s): 1 s cache. Fixer 2 (critics): the cache
    # entry carries profile:epoch:<uuid> - a switch reads fresh at once - so a 0 is cached 1 s too (no bridge call per hit)
    calls_ = [0]

    @JImplements("java.util.function.Function")
    class SkillFn2(object):
        @JOverride
        def apply(self, o):
            calls_[0] += 1
            return JInt(lv.get((str(o[0]), str(o[1])), 0))
    Cfg.bridge().put("skill:fn:level", SkillFn2())
    lv[(U_S, "Mining")] = 0
    Fair.LV.clear()
    for y_ in (96, 97, 98):
        api.wb[(WORLD, 725, y_, 700)] = "Ore_Iron_Stone"
    r0_ = mine(Skyy, WORLD, 725, 96, 700, block="Ore_Iron_Stone") and notes()[-1] == ("Skyy", "Requires Mining 10 (you: 0).")
    c0_ = calls_[0]
    fire(Skyy, "dig", 725, 96, 700, block="Ore_Iron_Stone")
    fire(Skyy, "dig", 725, 96, 700, block="Ore_Iron_Stone")
    K.check(r0_ and calls_[0] == c0_ and int(Fair.LV_MS) == 1000, "X B4 (fixer 2): a level 0 is cached 1 s too - a held mouse makes no bridge call per hit (%d calls)" % (calls_[0] - c0_))
    lv[(U_S, "Mining")] = 10
    Cfg.bridge().put("profile:epoch:" + U_S, JLong(7))
    K.check(not mine(Skyy, WORLD, 725, 97, 700, block="Ore_Iron_Stone"),
            "X B4 (fixer 2): a profile switch (profile:epoch:<uuid> changed) reads the level fresh at once - the cached 0 never sticks")
    lv[(U_S, "Mining")] = 3
    Cfg.bridge().put("profile:epoch:" + U_S, JLong(8))
    K.check(mine(Skyy, WORLD, 725, 98, 700, block="Ore_Iron_Stone") and notes()[-1] == ("Skyy", "Requires Mining 10 (you: 3)."),
            "X B4 (fixer 2): ... switching to a low-Mining profile is refused at once (PROFILES-CONTRACT rule 2)")
    # fixer 2 (critic: a held mouse on gated ore counted every hit event): a refused HIT counts once a second per player + reason
    Dep.CLOCK = JLong(TG + 3001)   # a fresh second (the hits above were counted in theirs)
    g0_ = int(Fair.refused(0))
    for _i in range(5):
        fire(Skyy, "dig", 725, 98, 700, block="Ore_Iron_Stone")
    g1_ = int(Fair.refused(0))
    mine(Skyy, WORLD, 725, 98, 700, block="Ore_Iron_Stone")
    mine(Skyy, WORLD, 725, 98, 700, block="Ore_Iron_Stone")
    K.check(g1_ == g0_ + 1 and int(Fair.refused(0)) == g1_ + 2,
            "X B6 (fixer 2): 5 refused hits in one second count once on /zones status; each refused break counts (%d -> %d -> %d)" % (g0_, g1_, int(Fair.refused(0))))
    Cfg.bridge().remove("profile:epoch:" + U_S)
    # fixer 2 (critic: SkyySkills' -1 / -2 were clamped to 0 = refused for good): -1 = that skill's gate off (warned once), -2 = every gate off
    logged()
    lv[(U_S, "Mining")] = -1
    Fair.LV.clear()
    api.wb[(WORLD, 725, 99, 700)] = "Ore_Iron_Stone"
    K.check(not mine(Skyy, WORLD, 725, 99, 700, block="Ore_Iron_Stone") and any("does not know the skill 'Mining'" in l for l in logged()) and Fair.LV.get(U_S + "|Mining") is None,
            "X B4 (fixer 2): skill:fn:level answering -1 (SkyySkills does not know the name) = that gate OFF, warned once, never cached")
    lv[(U_S, "Mining")] = -2
    api.wb[(WORLD, 725, 100, 700)] = "Ore_Iron_Stone"
    K.check(not mine(Skyy, WORLD, 725, 100, 700, block="Ore_Iron_Stone") and any("answered -2" in l for l in logged()),
            "X B4 (fixer 2): ... answering -2 (SkyySkills not ready) = every gate lets through, warned once")
    Cfg.bridge().put("skill:fn:level", SkillFn())
    lv[(U_S, "Mining")] = 10
    Fair.LV.clear()
    # region gate: per skill the higher of region + type
    Sto.create("deep", WORLD, "skyblock", JArray(JInt)([730, 60, 690, 750, 99, 710]), "Skyy")
    Sto.set("deep", "types", "copper", "Skyy")
    l_ = cmd(Skyy, "region", "gate", "deep", "Mining:15")
    lv[(U_S, "Mining")] = 12
    Fair.LV.clear()
    K.check(any("gate = Mining:15" in x for x in l_) and mine(Skyy, WORLD, 735, 95, 700, block="Ore_Iron_Stone") and notes()[-1] == ("Skyy", "Requires Mining 15 (you: 12).")
            and mine(Skyy, WORLD, 736, 95, 700, block="Ore_Copper_Stone"), "X B4: /zones region gate deep Mining:15 - max(region 15, type 10) = 15, for copper too: %s" % l_)
    lv[(U_S, "Mining")] = 15
    Fair.LV.clear()
    K.check(not mine(Skyy, WORLD, 737, 95, 700, block="Ore_Iron_Stone"), "X B4: Mining 15 - allowed")
    K.check(any("A gate is" in x for x in cmd(Skyy, "region", "gate", "deep", "Nope:5")) and any("A gate is" in x for x in cmd(Skyy, "region", "gate", "deep", "Mining:101"))
            and str(Sto.get("deep").gateShown()) == "Mining:15", "X B4: an unknown skill / a level over 100 is refused (the gate unchanged)")
    K.check(any("gate = none" in x for x in cmd(Skyy, "region", "gate", "deep", "none")) and Sto.get("deep").extra.get("gate") is None, "X B4: none clears the region gate")
    K.check(any("Only zone admins" in x for x in cmd(Coop, "region", "gate", "deep", "Mining:5")) and Sto.get("deep").extra.get("gate") is None,
            "X B6: /zones region gate is admin-only (skyyzones.admin, checked in code)")
    # a Foraging gate over a forest: the tree trigger
    Sto.create("grove1", WORLD, "skyblock", JArray(JInt)([740, 60, 740, 790, 140, 790]), "Skyy")
    Sto.set("grove1", "types", "logs", "Skyy")
    cmd(Skyy, "region", "gate", "grove1", "Foraging:10")
    lv[(U_S, "Foraging")] = 3
    Fair.LV.clear()
    tree(WORLD, 760, 80, 760)
    K.check(mine(Skyy, WORLD, 760, 80, 760, block="Wood_Oak_Trunk") and notes()[-1] == ("Skyy", "Requires Foraging 10 (you: 3).") and tr(WORLD, 760, 81, 760) is None,
            "X B4: a low Foraging character can't fell in the gated grove")
    stand(Skyy, 761, 80, 765)
    Tick.titles(Skyy["pr"], Skyy["u"], WORLD, 761, 81, 765, JLong(TG + 6000))
    K.check(True, "X B4: walking into the grove is never stopped (no move hook)")
    lv[(U_S, "Foraging")] = 10
    Fair.LV.clear()
    K.check(not mine(Skyy, WORLD, 760, 80, 760, block="Wood_Oak_Trunk") and tr(WORLD, 760, 81, 760) is not None, "X B4: Foraging 10 fells it")
    drain()
    # the table hook + the file (a hand edit is read; a bad line skipped + warned)
    K.check(ck(Cfg.checkGate, "Mining|10", "gate[iron]") is None and "Skills:" in ck(Cfg.checkGate, "Nope|10", "gate[iron]") and ck(Cfg.checkGate, "Mining|101", "gate[iron]") is not None
            and "No resource type" in ck(Cfg.checkGate, "Mining|5", "gate[nope]") and ck(Cfg.checkGate, None, "gate[iron]") is None,
            "X B4: Server Setup gate table hook - known skills only, level 0-100, an existing type")
    gfile = os.path.join(home, "guard.properties")
    gtxt = open(gfile, encoding="utf8").read()
    K.check(all(("gate.%s=Mining,%d\n" % kv) in gtxt for kv in (("iron", 10), ("thorium", 20), ("cobalt", 20), ("lead", 20), ("chromium", 20), ("adamantite", 30), ("slag", 30),
                                                                 ("mithril", 40), ("titanium", 40), ("onyxium", 45))) and "abuse.afkSec=900\n" in gtxt and "abuse.maxPerMin=300\n" in gtxt,
            "X B4 (Q1): guard.properties seeded with the locked gates (Iron 10, Thorium / Cobalt 20, Adamantite 30, Mithril 40 + the zone ores, Onyxium 45) + the fair-play defaults")
    K.check("abuse.awaySec=300\n" in gtxt and int(Cfg.AWAY_SEC) == 300, "X B5 (fixer 2): the 5-minute 'away' gap is the row abuse.awaySec (300 s), seeded in guard.properties")
    open(gfile, "a", encoding="utf8").write("gate.crops=Farming,5\ngate.bad=Nope,1\n")
    logged()
    Cfg.loadGuard(False)
    K.check(list(Cfg.gate("crops")) == ["Farming", 5] and Cfg.gate("bad") is None and any("gate.bad=Nope,1" in l for l in logged()), "X B4: a hand-edited gate line is read; a bad one skipped + warned")
    api.wb[(WORLD, 726, 85, 700)] = CF
    lv[(U_S, "Farming")] = 2
    Fair.LV.clear()
    K.check(fire(Skyy, "use", 726, 85, 700, block=CF) and notes()[-1] == ("Skyy", "Requires Farming 5 (you: 2).") and not waiting(WORLD, 726, 85, 700),
            "X B4: the gate holds for an F-harvest too")
    open(gfile, "w", encoding="utf8").write(gtxt)
    Cfg.loadGuard(False)
    Cfg.ABUSE_ON = False
    # /zones info: Needs Mining 10 (you: 7)
    lv[(U_S, "Mining")] = 7
    Fair.LV.clear()
    api.wb[(WORLD, 727, 95, 700)] = "Ore_Iron_Stone"
    stand(Skyy, 727, 95, 700)
    Cmds.info(Skyy["ref"], stG, Skyy["pr"], wG)
    l_ = said(Skyy)
    K.check(any(x == "Needs Mining 10 (you: 7)." for x in l_), "X B6: /zones info - 'Needs Mining 10 (you: 7).': %s" % [x for x in l_ if "Needs" in x])
    Cfg.GATES_ON = False
    K.check(not mine(Skyy, WORLD, 727, 95, 700, block="Ore_Iron_Stone"), "X B4: gates.on off - no gate")
    Cfg.GATES_ON = True
    lv[(U_S, "Mining")] = 0
    Fair.LV.clear()
    Bld.set(Bd["u"], "Builder", True)
    K.check(not mine(Bd, WORLD, 728, 95, 700, block="Ore_Iron_Stone"), "X B6: builder mode skips the gates")
    Bld.set(Bd["u"], "Builder", False)
    K.check(mine(Bd, WORLD, 729, 95, 700, block="Ore_Iron_Stone"), "X B4: ... and the same player with builder mode off is gated (Mining 0)")

    # ---------------------------------------------------------------- B5 fair play
    Cfg.GATES_ON = False
    Cfg.ABUSE_ON = True
    Cfg.MAX_PER_MIN, Cfg.CELL_CAP, Cfg.HITLOCK_SEC, Cfg.BOT_FLAG = 0, 0, 0, False
    Fair.clear()
    TA_ = TG + 100000
    Dep.CLOCK = JLong(TA_)
    Cfg.AFK_SEC = 60
    stand(Skyy, 800, 95, 800)
    K.check(not mine(Skyy, WORLD, 801, 95, 800) and not mine(Skyy, WORLD, 801, 95, 801), "X B5 A1: breaks while standing still ...")
    Dep.CLOCK = JLong(TA_ + 30000)
    K.check(not mine(Skyy, WORLD, 801, 95, 802), "X B5 A1: ... 30 s later still fine")
    Dep.CLOCK = JLong(TA_ + 60000)
    K.check(mine(Skyy, WORLD, 801, 95, 803) and notes()[-1] == ("Skyy", "Stretch your legs - move a little to keep mining."), "X B5 A1: after abuse.afkSec in one place - 'Stretch your legs'")
    # fixer (critic: a stopped player could still lock a block against everyone): his HIT is refused - no crack, no hit mark
    Cfg.HITLOCK_SEC = 3
    api.wb[(WORLD, 802, 95, 800)] = "Ore_Copper_Stone"
    h1_ = fire(Skyy, "dig", 802, 95, 800) and notes()[-1] == ("Skyy", "Stretch your legs - move a little to keep mining.")
    K.check(h1_ and Fair.HIT.get(Fair.hitKey(WORLD, 802, 95, 800)) is None and not fire(Coop, "dig", 802, 95, 800),
            "X B5 C3 (fixer): a player stopped for standing still gets no crack and sets no hit lock - another player mines that block freely")
    Fair.HIT.clear()
    Cfg.HITLOCK_SEC = 0
    stand(Skyy, 805, 95, 800)
    K.check(mine(Skyy, WORLD, 806, 95, 800), "X B5 A1: 5 blocks away (more than afkRadius 4, less than afkMove 8) - still refused")
    stand(Skyy, 809, 95, 800)
    api.wb[(WORLD, 810, 96, 800)] = "Ore_Copper_Stone"
    K.check(not fire(Skyy, "dig", 810, 96, 800) and not bool(Fair.PL.get(Skyy["u"]).lock),
            "X B5 A1 (fixer 2): mining = a hit first - the HIT from 9 blocks away (afkMove 8) unlocks the player (no break needed)")
    K.check(not mine(Skyy, WORLD, 810, 95, 800) and not mine(Skyy, WORLD, 810, 95, 801), "X B5 A1: 9 blocks away (afkMove 8) - mining again")
    # fixer (critic: coming back to the same vein after a long break was refused): no break attempt for 5 min = away, not standing still
    Dep.CLOCK = JLong(TA_ + 60000 + 400000)
    K.check(not mine(Skyy, WORLD, 810, 95, 802), "X B5 A1 (fixer): back at the same spot after 6+ min away (AFK_GAP 300 s) - a fresh anchor, not refused")
    Dep.CLOCK = JLong(TA_ + 60000 + 400000 + 30000)
    K.check(not mine(Skyy, WORLD, 810, 95, 803), "X B5 A1 (fixer): ... still fine 30 s later")
    Dep.CLOCK = JLong(TA_ + 60000 + 400000 + 61000)
    K.check(mine(Skyy, WORLD, 810, 95, 804) and notes()[-1] == ("Skyy", "Stretch your legs - move a little to keep mining."),
            "X B5 A1 (fixer): ... and standing still mining there for abuse.afkSec still stops (the gap never resets a busy miner)")
    Dep.CLOCK = JLong(TA_ + 60000 + 400000 + 61000 + 200000)
    api.wb[(WORLD, 810, 96, 804)] = "Ore_Copper_Stone"
    K.check(fire(Skyy, "dig", 810, 96, 804) and mine(Skyy, WORLD, 810, 95, 805), "X B5 A1 (fixer): a locked player who keeps hitting stays locked (each refused hit = still there)")
    Cfg.AFK_SEC = 0
    # A2 the rate cap; same-tick extras count half
    Cfg.MAX_PER_MIN = 4
    Fair.clear()
    TR_ = TA_ + 100000
    Dep.CLOCK = JLong(TR_)
    logged()
    ok_ = []
    for i_ in range(5):
        api.tk = 1000 + i_
        ok_.append(not mine(Skyy, WORLD, 820 + i_, 95, 820))
    K.check(ok_ == [True, True, True, True, False] and notes()[-1] == ("Skyy", "Slow down a little.") and any("broke more than 4 blocks in a minute" in l for l in logged()),
            "X B5 A2: abuse.maxPerMin 4 - the 5th break in a minute is refused, one admin log line: %s" % ok_)
    Dep.CLOCK = JLong(TR_ + 5000)
    K.check(mine(Skyy, WORLD, 826, 95, 820), "X B5 A2: ... still pausing (abuse.rateRestSec 10)")
    Cfg.HITLOCK_SEC = 3
    api.wb[(WORLD, 826, 96, 820)] = "Ore_Copper_Stone"
    K.check(fire(Skyy, "dig", 826, 96, 820) and notes()[-1] == ("Skyy", "Slow down a little.") and Fair.HIT.get(Fair.hitKey(WORLD, 826, 96, 820)) is None,
            "X B5 C3 (fixer): a player pausing after the break cap gets no crack and sets no hit lock")
    Fair.HIT.clear()
    Cfg.HITLOCK_SEC = 0
    Dep.CLOCK = JLong(TR_ + 10000)
    api.tk = 2000
    K.check(not mine(Skyy, WORLD, 827, 95, 820), "X B5 A2: ... then a fresh minute")
    Fair.clear()
    Dep.CLOCK = JLong(TR_ + 100000)
    ok_ = []
    for i_, tk_ in enumerate((3000, 3000, 3000, 3000, 3001, 3002, 3003)):
        api.tk = tk_
        ok_.append(not mine(Skyy, WORLD, 830 + i_, 95, 820))
    K.check(ok_ == [True, True, True, True, True, True, False], "X B5 A2: a hand break + 3 extras in the SAME world tick count 2.5 - two more full breaks fit, the next waits: %s" % ok_)
    # a felled tree = ONE break (its clearing breaks are never counted)
    Cfg.MAX_PER_MIN = 2
    Fair.clear()
    TF_ = TR_ + 200000
    Dep.CLOCK = JLong(TF_)
    api.tk = 4000
    oak2 = tree(WORLD, 840, 80, 860)
    K.check(not mine(Skyy, WORLD, 840, 80, 860, block="Wood_Oak_Trunk") and tr(WORLD, 840, 81, 860) is not None, "X B5: a tree felled with one cut ...")
    drain()
    for k in oak2:
        api.wb[(WORLD,) + k] = "Empty"
    for k in ((839, 84, 860), (841, 85, 861)):
        api.wb[(WORLD,) + k] = "Plant_Leaves_Oak"
    del api.breaks[:]
    tick(TF_ + 3000)
    api.tk = 4001
    K.check(len(api.breaks) == 1 and api.breaks[0][2] == [False, False] and not mine(Skyy, WORLD, 845, 95, 860) and mine(Skyy, WORLD, 846, 95, 860),
            "X B5 (finisher): ... and its 2 clearing breaks = ONE break for the cap (2): one more ore fits, the next waits")
    # C2 the turn limit: solo never; contested -> refused after abuse.cellCap
    Cfg.MAX_PER_MIN = 0
    Cfg.CELL_CAP = 3
    Fair.clear()
    TT_ = TF_ + 100000
    Dep.CLOCK = JLong(TT_)
    solo = [not mine(Skyy, WORLD, 832 + i_, 85, 832) for i_ in range(8)]
    K.check(all(solo), "X B5 C2: alone in a patch - never limited (8 breaks, cap 3)")
    K.check(not mine(Coop, WORLD, 840, 86, 833), "X B5 C2: another player breaks in the same 16-block patch ...")
    K.check(mine(Skyy, WORLD, 841, 85, 832) and notes()[-1] == ("Skyy", "Let others have a turn - try another vein."), "X B5 C2: ... now it is contested - over the cap: 'Let others have a turn'")
    K.check(not mine(Skyy, WORLD, 860, 85, 832), "X B5 C2: ... another patch is fine")
    Cfg.HITLOCK_SEC = 3
    api.wb[(WORLD, 843, 85, 833)] = "Ore_Copper_Stone"
    K.check(fire(Skyy, "dig", 843, 85, 833) and notes()[-1] == ("Skyy", "Let others have a turn - try another vein.") and Fair.HIT.get(Fair.hitKey(WORLD, 843, 85, 833)) is None
            and not fire(Coop, "dig", 843, 85, 833), "X B5 C3 (fixer): over the turn limit in a patch - his hits there are refused too (no lock on the vein others queue at)")
    Fair.HIT.clear()
    Cfg.HITLOCK_SEC = 0
    K.check(not mine(Coop, WORLD, 840, 86, 834) and not mine(Coop, WORLD, 840, 86, 835), "X B5 C2: the other player has his own count")
    Dep.CLOCK = JLong(TT_ + 61000)
    K.check(not mine(Skyy, WORLD, 842, 85, 832), "X B5 C2: after abuse.cellRestSec + no other player there within abuse.contestSec - mining again")
    Cfg.CELL_CAP = 0
    # C3 the hit lock
    Cfg.HITLOCK_SEC = 3
    Fair.clear()
    TH_ = TT_ + 100000
    Dep.CLOCK = JLong(TH_)
    api.wb[(WORLD, 850, 85, 850)] = "Ore_Copper_Stone"
    K.check(not fire(Skyy, "dig", 850, 85, 850), "X B5 C3: Skyy hits a block ...")
    Dep.CLOCK = JLong(TH_ + 1000)
    K.check(fire(Coop, "dig", 850, 85, 850) and notes()[-1] == ("Coop", "Someone else is mining this block.") and fire(Coop, "break", 850, 85, 850),
            "X B5 C3: ... another player's hit / break within 3 s is refused (no crack, no drop)")
    K.check(not fire(Skyy, "dig", 850, 85, 850), "X B5 C3: the first player keeps mining it")
    Dep.CLOCK = JLong(TH_ + 4001)
    K.check(not fire(Coop, "dig", 850, 85, 850), "X B5 C3: 3 s after the last hit - free for others")
    Cfg.HITLOCK_SEC = 0
    Dep.CLOCK = JLong(TH_ + 4500)
    K.check(not fire(Skyy, "dig", 850, 85, 850), "X B5 C3: abuse.hitLockSec 0 = off")
    # A3 the bot flag (flag only)
    Cfg.BOT_FLAG, Cfg.BOT_SAMPLE, Cfg.BOT_GAP_MS = True, 50, 15
    Fair.clear()
    TQ = TH_ + 100000
    import random as _rnd
    _rnd.seed(7)
    okb, okc = [], []
    for i_ in range(60):
        Dep.CLOCK = JLong(TQ + 100 * i_)
        api.tk = 5000 + 2 * i_
        okb.append(not mine(Skyy, WORLD, 870 + (i_ % 20), 85, 870 + i_ // 20))
    t_ = TQ + 100000
    for i_ in range(60):
        t_ += _rnd.randint(100, 900)
        Dep.CLOCK = JLong(t_)
        api.tk = 9000 + 2 * i_
        okc.append(not mine(Coop, WORLD, 900 + (i_ % 20), 85, 870 + i_ // 20))
    fl_ = Fair.PL.get(Skyy["u"])
    fc_ = Fair.PL.get(Coop["u"])
    K.check(all(okb) and all(okc) and fl_ is not None and fl_.flag is not None and "rhythm spread 0 ms" in str(fl_.flag) and (fc_ is None or fc_.flag is None)
            and any("FLAGGED (no punishment)" in l for l in logged()), "X B5 A3: perfect 100 ms rhythm -> flagged (never refused); a human rhythm is not: %s" % (fl_.flag if fl_ else None))
    # builder mode + the op bypass skip every rule; abuse.on off = no rules
    Cfg.MAX_PER_MIN = 1
    Dep.CLOCK = JLong(TQ + 300000)
    Bld.set(Bd["u"], "Builder", True)
    K.check(not mine(Bd, WORLD, 930, 85, 870) and not mine(Bd, WORLD, 931, 85, 870) and not mine(Bd, WORLD, 932, 85, 870), "X B6: builder mode skips the fair-play rules")
    Bld.set(Bd["u"], "Builder", False)
    Cfg.OP_BYPASS = True
    perms[(str(Coop["u"]), "skyyzones.admin")] = True
    K.check(not mine(Coop, WORLD, 933, 85, 870) and not mine(Coop, WORLD, 934, 85, 870) and not mine(Coop, WORLD, 935, 85, 870), "X B6: zones.opBypass admins skip them too")
    Cfg.OP_BYPASS = False
    perms[(str(Coop["u"]), "skyyzones.admin")] = False
    Cfg.ABUSE_ON = False
    K.check(not mine(Coop, WORLD, 936, 85, 870) and not mine(Coop, WORLD, 937, 85, 870) and not mine(Coop, WORLD, 938, 85, 870), "X B5: abuse.on off - no rule")
    Cfg.ABUSE_ON = True
    Cfg.MAX_PER_MIN, Cfg.CELL_CAP, Cfg.HITLOCK_SEC, Cfg.AFK_SEC, Cfg.BOT_SAMPLE = 300, 120, 3, 900, 200
    K.check(ck(Cfg.checkOff, "30", "abuse.afkSec") is not None and ck(Cfg.checkOff, "0", "abuse.afkSec") is None and ck(Cfg.checkOff, "60", "abuse.afkSec") is None
            and ck(Cfg.checkOff, "20", "abuse.maxPerMin") is not None and ck(Cfg.checkOff, "5", "abuse.cellCap") is not None, "X: the 0 = off rows refuse values under their floor")
    # ---------------------------------------------------------------- B6 /zones status + info + the regions table cell
    stand(Skyy, 700, 118, 702)
    Cfg.GATES_ON = True
    Fair.LV.clear()
    put(Skyy, 700, 120, 700)
    drain()
    stand(Skyy, 700, 120, 700)
    Cmds.info(Skyy["ref"], stG, Skyy["pr"], wG)
    l_ = said(Skyy)
    K.check(any(x.startswith("Scaffold: vanishes in ") for x in l_), "X B6: /zones info on a scaffold - 'Scaffold: vanishes in N s': %s" % [x for x in l_ if "Scaffold" in x])
    Cmds.status(Skyy["pr"])
    l_ = said(Skyy)
    rl = [x for x in l_ if x.startswith("Refused in the last hour: ")]
    K.check(any(x.startswith("Gates + fair play: skill gates ON") for x in l_) and rl and all(("%s " % n) in rl[0] for n in ("skill gate", "standing still", "too fast", "turn limit", "hit lock"))
            and int(Fair.refused(0)) >= 1 and int(Fair.refused(1)) >= 1 and int(Fair.refused(2)) >= 1 and int(Fair.refused(3)) >= 1 and int(Fair.refused(4)) >= 1,
            "X B6: /zones status - the refused breaks of the last hour per reason: %s" % rl)
    K.check(any(x.startswith("Scaffolding: ON - 1 up now") for x in l_) and any(x.startswith("Flagged (perfect rhythm") and "Skyy (rhythm spread" in x for x in l_)
            and any(x.startswith("Tree cuts: the biggest search read ") for x in l_) and any((WORLD + ": 1 scaffolds up") in x for x in l_),
            "X B6: /zones status - scaffolds up, the flagged player (name + why), the biggest tree search: %s" % [x for x in l_ if x.startswith(("Scaffold", "Flagged", "Tree cuts"))])
    Dep.CLOCK = JLong(int(Dep.CLOCK) + 3600000 + 120000)
    K.check(int(Fair.refused(0)) == 0, "X B6: the refusal counters cover the last hour only")
    # fixer (critic: gate + place made an ordinary regions cell longer than 200 characters): their own table rules[<region>]
    cell = str(RegKit.customGet("rules[grove1]"))
    K.check(cell == "gate Foraging:10; place default" and "gate" not in str(RegKit.customGet("region[grove1]")) and list(RegKit.customKeys("rules")) == list(RegKit.customKeys("region")),
            "X B6 (fixer): the 'Region gates + placing' table shows gate + place; the regions cell is as in 0.3.0: %s" % cell)
    r_ = RegKit.customSet("rules[grove1]", "gate Foraging:20; place Skyy_Scaffold,Wood_Oak_Planks")
    K.check(str(r_[0]) == "ok" and str(r_[1]) == "gate Foraging:20; place Skyy_Scaffold,Wood_Oak_Planks" and str(Sto.get("grove1").gateShown()) == "Foraging:20"
            and str(Sto.get("grove1").placeShown()) == "Skyy_Scaffold,Wood_Oak_Planks", "X B6: ... gate + place are editable there (all or nothing, through ZStore): %s" % str(r_[2]))
    r_ = RegKit.customSet("rules[grove1]", "gate Nope:3; place default")
    K.check(str(r_[0]) == "bad" and str(Sto.get("grove1").gateShown()) == "Foraging:20" and str(Sto.get("grove1").placeShown()) == "Skyy_Scaffold,Wood_Oak_Planks",
            "X B6: ... a bad gate is refused there (nothing changes): %s" % str(r_[2]))
    K.check(str(RegKit.customSet("rules[grove1]", "flags none")[0]) == "bad" and str(RegKit.customSet("rules[nope_region]", "gate none")[0]) == "bad",
            "X B6 (fixer): ... only gate / place parts, only existing regions")
    # the long cell the critic counted: six types, a title, a two-skill gate, two place ids, two boxes
    Sto.create("longreg", WORLD, "skyblock", JArray(JInt)([600, 60, 900, 640, 140, 940]), "Skyy")
    Sto.addBox("longreg", WORLD, JArray(JInt)([650, 60, 900, 690, 140, 940]), "Skyy")
    Sto.set("longreg", "types", "copper,iron,lead,logs,crops,thorium", "Skyy")
    Sto.set("longreg", "title", "The Deep Copper Quarry", "Skyy")
    RegKit.customSet("rules[longreg]", "gate Mining:10,Foraging:5; place Skyy_Scaffold,Wood_Oak_Planks")
    lc_, lr_ = str(RegKit.customGet("region[longreg]")), str(RegKit.customGet("rules[longreg]"))
    K.check(len(lc_) <= 200 and "..." not in lc_ and str(RegKit.customSet("region[longreg]", lc_.replace("priority 0", "priority 2"))[0]) == "ok"
            and lr_ == "gate Mining:10,Foraging:5; place Skyy_Scaffold,Wood_Oak_Planks" and int(Sto.get("longreg").priority) == 2,
            "X B6 (fixer): a long region (%d + %d characters) stays editable in both tables: %s | %s" % (len(lc_), len(lr_), lc_, lr_))
    Sto.delete("longreg", "Skyy")
    Sto.flush()   # (region writes run on the scheduler; flush = the newest text now)
    rtxt2 = open(os.path.join(home, "regions.properties"), encoding="utf8").read()
    K.check("region.grove1.gate=Foraging:20\n" in rtxt2 and "region.grove1.placeAllow=Skyy_Scaffold,Wood_Oak_Planks\n" in rtxt2, "X B6: the region lines are saved (regions.properties)")
    K.check(", gate Foraging:20, place Skyy_Scaffold,Wood_Oak_Planks)" in str(Sto.get("grove1").summary()), "X B6: /zones list shows them")
    K.check(any("/zones place add" in x for x in cmd(Skyy, "help")) and any("/zones region gate" in x for x in cmd(Skyy, "help")), "X B6: /zones help names the new words")

    # ---------------------------------------------------------------- finisher follow-ups: verify in passBatch batches, the read cap, the section reader
    Cfg.ABUSE_ON = False
    Cfg.GATES_ON = False
    TV = int(Dep.CLOCK) + 100000
    Dep.CLOCK = JLong(TV)
    big2 = {}
    vx, vy, vz = 950, 20, 950
    for dy in range(30):
        for dx in range(9):
            for dz in range(9):
                big2[(vx + dx, vy + dy, vz + dz)] = "Wood_Oak_Trunk"
    for k, v in big2.items():
        api.wb[(WORLD,) + k] = v
    Fell.MAXR.set(0)
    K.check(not mine(Skyy, WORLD, vx, vy, vz, block="Wood_Oak_Trunk") and tr(WORLD, vx, vy, vz) is not None, "X F1: a %d-block tree felled" % len(big2))
    rpb = int(Fell.MAXR.get()) / float(len(big2))
    K.notes.append("X F1 (fixer): reads per tree block = %.2f (%d reads for the %d-block trunk) -> 60,000 reads serve about %d blocks" % (rpb, int(Fell.MAXR.get()), len(big2), int(60000 / rpb)))
    drain()
    tv_ = tr(WORLD, vx, vy, vz)
    for k in big2:
        api.wb[(WORLD,) + k] = "Empty"
    for _i in range(40):
        tick(int(tv_.due) + 1000 * _i)
        if tr(WORLD, vx, vy, vz) is None:
            break
    K.check(tr(WORLD, vx, vy, vz) is None and all(api.wb[(WORLD,) + k] == "Wood_Oak_Trunk" for k in big2), "X F1: ... it grew back (batched respawn)")
    Rgn.shutdown()
    for k in big2:
        api.wb[(WORLD,) + k] = "Empty"   # an unclean stop: the chunk was saved before the tree grew back
    Rgn.start(Paths.get(rdir))
    ag0 = int(Fell.AGAIN.get())
    rwv = Rgn.rw(WORLD, False)
    K.check(rwv is not None and any(int(t.x) == vx and int(t.z) == vz for t in rwv.tcheck.values()), "X F1: the grown-back tree is re-checked after the start (W line)")
    nw0 = len(api.writes)
    Dep.CLOCK = JLong(int(Dep.CLOCK) + 1000)
    P("ZTicker")().run()
    drain()
    per = [len(api.writes) - nw0]
    for _i in range(80):
        if not api.lat:
            break
        n1 = len(api.writes)
        while api.lat:
            api.lat.pop(0).run()
        drain()
        per.append(len(api.writes) - n1)
    K.check(max(per) <= int(Cfg.PASS) and sum(per) == len(big2) and len(per) >= (len(big2) + int(Cfg.PASS) - 1) // int(Cfg.PASS) and int(Fell.AGAIN.get()) == ag0 + 1
            and all(api.wb[(WORLD,) + k] == "Wood_Oak_Trunk" for k in big2) and rwv.tcheck.isEmpty(),
            "X F1 (zones03 finisher): ZFell.verify writes the %d blocks in %d passes of at most regen.passBatch %d (%s...) - no one-tick write" % (len(big2), len(per), int(Cfg.PASS), per[:4]))
    mr = int(Fell.MAXR.get())
    K.notes.append("X F2: the biggest tree search of the run read %d blocks (the 4,620-block giant of the 0.3.0 checks is felled under the new cap)" % mr)
    K.check(0 < mr <= 60000 and int(Fell.READ_CAP) == 60000 and int(Fell.READ_PER) == 10, "X F2: read cap = min(60,000, max(40,000, 10 x tree.maxBlocks)); the biggest search %d reads" % mr)
    Fell.READ_CAP = 300
    sp0 = int(Fell.SPREAD.get())
    tree(WORLD, 990, 80, 990, h=8, thick=True)
    logged()
    K.check(fire(Skyy, "break", 990, 80, 990, block="Wood_Oak_Trunk") and notes()[-1] == ("Skyy", "This tree is too big to regrow - tell an admin.")
            and int(Fell.SPREAD.get()) == sp0 + 1 and any("too spread out to search" in l for l in logged()) and tr(WORLD, 990, 80, 990) is None,
            "X F2: a search over the read cap is refused like a too-big tree (no drop), logged 'too spread out'")
    # fixer (critic: every retry re-ran the whole search): a refused tree is remembered NEG_MS 15 s - no new search per hit
    mr0 = int(Fell.MAXR.get())
    K.check(fire(Skyy, "break", 990, 80, 990, block="Wood_Oak_Trunk") and notes()[-1] == ("Skyy", "This tree is too big to regrow - tell an admin.")
            and int(Fell.SPREAD.get()) == sp0 + 1 and Fell.NEG.size() >= 1, "X F2 (fixer): a second cut within 15 s is refused WITHOUT a new search (SPREAD unchanged)")
    Dep.CLOCK = JLong(int(Dep.CLOCK) + int(Fell.NEG_MS) + 1)
    K.check(fire(Skyy, "break", 990, 80, 990, block="Wood_Oak_Trunk") and int(Fell.SPREAD.get()) == sp0 + 2, "X F2 (fixer): ... after 15 s the tree is searched again")
    Fair.prune(JLong(int(Dep.CLOCK) + int(Fell.NEG_MS) + 1))
    K.check(Fell.NEG.size() == 0, "X F2 (fixer): the minute prune drops old refused-tree entries")
    Fell.READ_CAP = 60000
    # the section reader on a real BlockSection (the engine path: API off for these calls)
    BS = JClass("com.hypixel.hytale.server.core.universe.world.chunk.section.BlockSection")
    HMp = JClass("java.util.HashMap")
    bs = BS()
    bs.set(JInt(5), JInt(70), JInt(7), JInt(int(btm.getIndex("Ore_Copper_Stone"))), JInt(0), JInt(0))   # set(x, y, z, id, rotation, filler)
    idc, secs = HMp(), HMp()
    skey = lambda x, y, z: ((((x >> 5) & 0x3FFFFFF) << 38) | (((y >> 5) & 0xFFF) << 26) | ((z >> 5) & 0x3FFFFFF)) - (1 << 64 if ((((x >> 5) & 0x3FFFFFF) << 38) >> 63) else 0)
    secs.put(JLong(skey(5, 70, 7)), bs)
    secs.put(JLong(skey(40, 70, 7)), Bool.FALSE)
    Eng.API = None
    try:
        a1 = Eng.fastAt(wG, secs, idc, 5, 70, 7)
        a2 = Eng.fastAt(wG, secs, idc, 6, 70, 7)
        a3 = Eng.fastAt(wG, secs, idc, 40, 70, 7)
        a4 = Eng.fastAt(wG, secs, idc, 5, 400, 7)
        a5 = Eng.idIn(bs, 5, 70, 7, idc)
    finally:
        Eng.API = api
    K.check(str(a1) == "Ore_Copper_Stone" and str(a2) == "Empty" and a3 is None and a4 is None and str(a5) == "Ore_Copper_Stone" and idc.size() == 2,
            "X F2: the section reader - a cached section's palette read (+ the id cache), an unloaded section / y out of range = null: %s" % [a1, a2, a3, a4, a5])
    K.check(int(Eng.tick(wG)) == int(api.tk), "X: ZEng.tick goes through the stand-in (the world tick in game)")
    # fixer (critic: scaffolds waited while a regrow backlog filled regen.passBatch): they vanish FIRST in every pass
    TP_ = int(Dep.CLOCK) + 100000
    Dep.CLOCK = JLong(TP_)
    tick(TP_)
    stand(Skyy, 700, 118, 702)
    K.check(not put(Skyy, 700, 120, 699), "X B2 (fixer): a scaffold ...")
    drain()
    for i_ in range(30):
        mine(Skyy, WORLD, 600 + i_, 95, 600)
    drain()
    rwb = Rgn.rw(WORLD, False)
    pb0 = Cfg.PASS
    Cfg.PASS = 10
    Dep.CLOCK = JLong(TP_ + 7200000)
    del api.lat[:]
    P("ZPass").pass_(rwb, wG) if hasattr(P("ZPass"), "pass_") else getattr(P("ZPass"), "pass")(rwb, wG)
    left_ = sum(1 for i_ in range(30) if waiting(WORLD, 600 + i_, 95, 600))
    K.check(api.wb[(WORLD, 700, 120, 699)] == "Empty" and sc(WORLD, 700, 120, 699) is None and left_ >= 15,
            "X B2 (fixer): ... is gone in the FIRST pass although %d mined blocks still wait (regen.passBatch 10 full)" % left_)
    Cfg.PASS = pb0
    tick(TP_ + 7200000)
    Cfg.bridge().remove("skill:fn:level")
    Cfg.ABUSE_ON = True
    Cfg.GATES_ON = True
    Rgn.shutdown()
    Eng.API = None


# ---------------------------------------------------------------------------------------------------------------- M: Mig030
def run_mig(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Mig, Cfg, Rows, Hist, Log = (JClass(PKG + n) for n in ("ZMig", "ZCfg", "CfgRows", "CfgHist", "CfgLog"))
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyZones")
    Paths = JClass("java.nio.file.Paths")
    gen = open(GEN, encoding="utf8").read()
    old_regen = ("# SkyyZones regrowing blocks\r\nregen.enabled=true\r\nregen.speedMult=1\r\nregrow.stone=3,Rock_Bedrock\r\nregrow.copper=4,Rock_Bedrock\r\n"
                 "regrow.logs=0,none\r\nregrow.crops=0,none\r\nregrow.gem=30,Rock_Bedrock\r\n")
    old_types = "# SkyyZones resource types\r\ntype.stone=Rock_Stone\r\ntype.copper=Ore_Copper*\r\ntype.logs=Wood_*_Trunk\r\n"

    def setup(name, regen, types):
        d = os.path.join(scratch, "m", name, "Skyy_SkyyZones")
        os.makedirs(d, exist_ok=True)
        if regen is not None:
            open(os.path.join(d, "regen.properties"), "wb").write(regen.encode("latin-1"))
        if types is not None:
            open(os.path.join(d, "types.properties"), "wb").write(types.encode("latin-1"))
        Rows.HOME = None
        Hist.DIR = None
        Log.FILE = None
        return d
    rb = lambda d, f: open(os.path.join(d, f), "rb").read()
    # 1: Skyy's 0.2.x files (CRLF, old defaults)
    d = setup("a", old_regen, old_types)
    r = str(Mig.run(Paths.get(d)))
    nr, nt = rb(d, "regen.properties").decode("latin-1"), rb(d, "types.properties").decode("latin-1")
    want_r = old_regen.replace("regrow.logs=0,none", "regrow.logs=60,none").replace("regrow.crops=0,none", "regrow.crops=10,stage1") + \
        str(Mig.HEAD) + "\r\nregrow.lead=6,Rock_Bedrock\r\nregrow.chromium=8,Rock_Bedrock\r\nregrow.slag=10,Rock_Bedrock\r\nregrow.titanium=12,Rock_Bedrock\r\n"
    want_t = old_types + str(Mig.HEAD) + "\r\ntype.lead=Ore_Lead_Sandstone_SkyWynn\r\ntype.chromium=Ore_Chromium_Shale_SkyWynn\r\ntype.slag=Ore_Slag_Volcanic_SkyWynn\r\ntype.titanium=Ore_Titanium_Basalt_SkyWynn\r\n"
    K.check(nr == want_r, "M A8: regen.properties - logs 0,none -> 60,none, crops 0,none -> 10,stage1, the 4 zone ore rows appended, CRLF kept, every other byte the same:\n%r" % nr)
    K.check(nt == want_t, "M A8: types.properties - the 4 zone ore types appended (CRLF): %r" % nt)
    hist = os.path.join(d, "config-history")
    baks = sorted(os.listdir(hist)) if os.path.isdir(hist) else []
    K.check(any(b.endswith(".bak") and "regen.properties" in b and open(os.path.join(hist, b), "rb").read() == old_regen.encode("latin-1") for b in baks)
            and any(b.endswith(".bak") and "types.properties" in b and open(os.path.join(hist, b), "rb").read() == old_types.encode("latin-1") for b in baks),
            "M A8: History copies of BOTH old files (byte for byte) in config-history: %s" % baks)
    lg = open(os.path.join(d, "config-changes.log"), encoding="utf8").read().splitlines()
    want = [("regrow[logs]", "0|none", "60|none"), ("regrow[crops]", "0|none", "10|stage1"), ("regrow[lead]", "(none)", "6|Rock_Bedrock"),
            ("regrow[titanium]", "(none)", "12|Rock_Bedrock"), ("type[lead]", "(none)", "Ore_Lead_Sandstone_SkyWynn"), ("type[titanium]", "(none)", "Ore_Titanium_Basalt_SkyWynn")]
    got = [tuple(l.split("\t")[4:7]) for l in lg]
    K.check(len(lg) == 10 and all(w in got for w in want) and all(l.split("\t")[1] == "SkyyZones 0.3.0" and l.split("\t")[3] == "migration" and l.endswith("\tok") for l in lg),
            "M A8: one Server Setup -> Changes line per key (via migration, table keys so Undo works): %s" % got)
    K.check(os.path.isfile(os.path.join(d, "migrate-0.3.0.done")) and "lines changed" in r, "M A8: the marker is written: %s" % r[:120])
    b1 = (rb(d, "regen.properties"), rb(d, "types.properties"), len(lg))
    K.check(str(Mig.run(Paths.get(d))) == "" and (rb(d, "regen.properties"), rb(d, "types.properties"), len(open(os.path.join(d, "config-changes.log")).read().splitlines())) == b1,
            "M A8: a second run is a no-op")
    os.remove(os.path.join(d, "migrate-0.3.0.done"))
    K.check(str(Mig.run(Paths.get(d))) != "" and (rb(d, "regen.properties"), rb(d, "types.properties")) == b1[:2], "M A8: without the marker it changes nothing twice (idempotent)")
    # 2: hand-edited (LF): logs 30 kept + logged, crops missing (no line added - the loader's default), a hand type.lead untouched
    lines = []
    Cfg.LINES = JClass("java.util.ArrayList")()
    d = setup("b", "regrow.logs=30,none\nregrow.copper=4,Rock_Bedrock\n", "type.lead=Ore_Lead_Something_Else\n")
    r = str(Mig.run(Paths.get(d)))
    nr, nt = rb(d, "regen.properties").decode("latin-1"), rb(d, "types.properties").decode("latin-1")
    K.check(nr.startswith("regrow.logs=30,none\nregrow.copper=4,Rock_Bedrock\n") and "regrow.crops" not in nr and nr.endswith("regrow.titanium=12,Rock_Bedrock\n") and "\r" not in nr,
            "M A8: a hand-edited logs line (30) is KEPT, LF kept: %r" % nr)
    K.check("regrow.logs=30,none" in r and any("keeps hand-edited" in str(l) for l in Cfg.LINES), "M A8: ... and logged as kept: %s" % r[:160])
    K.check(nt.startswith("type.lead=Ore_Lead_Something_Else\n") and "type.lead=Ore_Lead_Sandstone" not in nt and "type.chromium=" in nt, "M A8: a present type.lead line is never touched")
    Cfg.LINES = None
    # 3: the History copy fails -> nothing written, no marker
    d = setup("c", old_regen, old_types)
    open(os.path.join(d, "config-history"), "w").write("a file in the way")
    r = str(Mig.run(Paths.get(d)))
    K.check(r == "" and rb(d, "regen.properties") == old_regen.encode("latin-1") and not os.path.isfile(os.path.join(d, "migrate-0.3.0.done")),
            "M A8: no History copy -> NOTHING written, no marker (the next start tries again)")
    # 4: a fresh folder + 5: no final line break
    d = setup("d", None, None)
    K.check(str(Mig.run(Paths.get(d))) == "" and os.path.isfile(os.path.join(d, "migrate-0.3.0.done")) and not os.path.isfile(os.path.join(d, "regen.properties")),
            "M A8: a fresh folder - the marker only")
    d = setup("e", "regrow.logs=0,none", None)
    Mig.run(Paths.get(d))
    nr = rb(d, "regen.properties").decode("latin-1")
    K.check(nr == "regrow.logs=60,none\n" + str(Mig.HEAD) + "\nregrow.lead=6,Rock_Bedrock\nregrow.chromium=8,Rock_Bedrock\nregrow.slag=10,Rock_Bedrock\nregrow.titanium=12,Rock_Bedrock\n",
            "M A8: a file without a final line break gets one before the appended lines: %r" % nr)
    # fixer F4: the second file's write fails -> the first file's Changes lines are already logged; the retry logs the second's
    d = setup("f", old_regen, old_types)
    os.makedirs(os.path.join(d, "types.properties.tmp"))
    r = str(Mig.run(Paths.get(d)))
    lg = open(os.path.join(d, "config-changes.log"), encoding="utf8").read().splitlines() if os.path.isfile(os.path.join(d, "config-changes.log")) else []
    got = [l.split("	")[4] for l in lg]
    K.check(r == "" and rb(d, "types.properties") == old_types.encode("latin-1") and not os.path.isfile(os.path.join(d, "migrate-0.3.0.done"))
            and "regrow[logs]" in got and "regrow[crops]" in got and len(got) == 6, "X fixer F4: types.properties write fails - regen.properties' 6 Changes lines are logged anyway: %s" % got)
    os.rmdir(os.path.join(d, "types.properties.tmp"))
    r = str(Mig.run(Paths.get(d)))
    lg = open(os.path.join(d, "config-changes.log"), encoding="utf8").read().splitlines()
    got = [l.split("	")[4] for l in lg]
    K.check(r != "" and rb(d, "types.properties").decode("latin-1") == want_t and os.path.isfile(os.path.join(d, "migrate-0.3.0.done"))
            and len(got) == 10 and got.count("regrow[logs]") == 1 and "type[lead]" in got, "X fixer F4: ... the retry writes types.properties and logs its 4 lines (10 in all, none twice): %s" % got)
    K.save()


def snap(d):
    out = {}
    for base, _dirs, fs in os.walk(d):
        for f in fs:
            p_ = os.path.join(base, f)
            out[os.path.relpath(p_, d).replace(os.sep, "/")] = hashlib.sha1(open(p_, "rb").read()).hexdigest()
    return out


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Plug, CPub, Sto = (JClass(PKG + n) for n in ("SkyyZonesPlugin", "CfgPub", "ZStore"))
    Paths = JClass("java.nio.file.Paths")
    Sto.SYNC = True
    before = snap(home)
    sz = os.path.join(home, "Skyy_SkyyZones")
    old_r = open(os.path.join(sz, "regen.properties"), "rb").read() if os.path.isfile(os.path.join(sz, "regen.properties")) else None

    def start():
        r = str(Plug.paths(Paths.get(sz)))
        CPub.start(Paths.get(home), JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyZones"))
        CPub.flush()
        CPub.shutdown()
        return r
    r1 = start()
    s1 = snap(home)
    r2 = start()
    s2 = snap(home)
    ch = sorted(f for f in before if s1.get(f) != before[f] and not f.startswith("Skyy_SkyyZones/"))
    K.check(not ch, "D start 1: every file outside Skyy_SkyyZones byte-identical (%s)" % ch[:5])
    K.check(s1 == s2, "D start 2 changes nothing (%s)" % sorted(f for f in set(s1) | set(s2) if s1.get(f) != s2.get(f)))
    chz = sorted(f for f in set(s1) | set(before) if f.startswith("Skyy_SkyyZones/") and s1.get(f) != before.get(f))
    K.notes.append("D Skyy_SkyyZones changes: %s" % chz)
    K.check(all(f in ("Skyy_SkyyZones/regen.properties", "Skyy_SkyyZones/types.properties", "Skyy_SkyyZones/trees.properties", "Skyy_SkyyZones/migrate-0.3.0.done",
                      "Skyy_SkyyZones/scaffold.properties", "Skyy_SkyyZones/guard.properties",
                      "Skyy_SkyyZones/config-changes.log") or f.startswith("Skyy_SkyyZones/config-history/") for f in chz), "D only Mig030's files change: %s" % chz)
    if old_r is not None:
        new_r = open(os.path.join(sz, "regen.properties"), "rb").read().decode("latin-1")
        o = old_r.decode("latin-1")
        K.check(new_r.startswith(o.replace("regrow.logs=0,none", "regrow.logs=60,none").replace("regrow.crops=0,none", "regrow.crops=10,stage1"))
                and new_r.rstrip().endswith("regrow.titanium=12,Rock_Bedrock"), "D Skyy's regen.properties: only the logs / crops values + the appended zone ore rows")
    K.check(os.path.isfile(os.path.join(sz, "scaffold.properties")) and os.path.isfile(os.path.join(sz, "guard.properties"))
            and "scaffolding ON" in r1 and "skill gates ON" in r1, "D 0.3.1: scaffold.properties + guard.properties seeded once from the defaults (no migration): %s" % r1[-400:])
    K.notes.append("D: %s | %s" % (r1[:300], r2[:200]))
    K.save()


# 0.3.1: the jar gains two planned non-class entries (the Skyy_Scaffold item json + its lang lines in server.lang); harness_kit's compare
# allows only manifest.json there, so its one "non-class entries" line is re-checked here against exactly the planned list (tools/harness_kit.py
# is shared - not edited)
NONCLASS = ["Server/Item/Items/SkyyZones/Skyy_Scaffold.json", "Server/Languages/en-US/server.lang", "manifest.json"]
_cmp0 = HK.run_compare


def _cmp(out, jar, old_jar, pkg, expect, added, removed=()):
    import json as _j
    _cmp0(out, jar, old_jar, pkg, expect, added, removed)
    d = _j.load(open(out))
    want = "C: non-class entries changed: got %r, want ['manifest.json']" % NONCLASS
    if want in d["fails"]:
        d["fails"].remove(want)
        d["ok"] += 1
        d["notes"].append("C: non-class entries changed = exactly the planned %s" % NONCLASS)
    _j.dump(d, open(out, "w"), indent=1)


HK.run_compare = _cmp

if __name__ == "__main__":
    HK.run("SkyyZones", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("static", run_static), ("fakes", run_fakes), ("exec", run_exec), ("mig", run_mig), ("live", run_live)], __file__, live=(LIVE, "mods"))
