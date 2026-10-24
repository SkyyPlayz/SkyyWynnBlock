"""Harness for SkyyZones 0.3.0 (SkyyZones 0.3 step 1: whole-island gathering, whole trees, crops, zone ores, Mig030; tools/zones_0_3_0_patch.py).
Build first:  python tools/zones_0_3_0_patch.py && python SkyyZones/build_skyyzones_0.3.0.py
    python SkyyZones/test_skyyzones_0.3.0.py [--keep]
Phases (fresh child JVMs, tools/harness_kit.py: -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch; scratch tools/dev/scratch/zones03/zh):
  S   static   the patch re-runs to identical bytes; line endings kept; no new system / command; the ready line text in the jar
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.2.2 -> 0.3.0: exactly ZShape / ZTree / ZFell / ZMig added; the members that differ (EXPECT)
  F2  fakes    the 0.2.0 harness's engine stand-ins into scratch/fake2
  X   exec     the REAL ZGuard / ZRegen / ZPass / ZFell / ZCfg / ZRules / ZFn / ZBox / ZTick on stand-in worlds with REAL engine events and REAL
               BlockTypes (crop states = real StateData objects): A0 layers, A1 tree search, A2 write order + write failures, A3 replay +
               compaction, A4 respawn (order, occupied, changed, unloaded, after-crash re-check), A5 clearing pass (performBlockBreak stand-in
               that fires the real guard inside the CLR call), A6 tree groups, A7 crops (ripe / unripe / F-harvest / stages), A9 zone ores,
               A10 check hooks, status / info / restore / zone reset bridge / maxDepleted / builder / mob / regen off / region delete
  M   mig      Mig030 (A8) on synthetic files: old defaults rewritten (CRLF + LF kept), hand-edited kept + logged, appended lines, History
               copy BEFORE the write (verified), Changes lines (via migration, table keys for Undo), marker, second run no-op, a failed History
               copy = nothing written, a fresh folder = marker only, a file without a final line break
  D   live     start twice on a scratch COPY of the live mods folder: Mig030 changes only its lines in Skyy_SkyyZones, start 2 changes nothing
  AA  audit    engine-access audit
NOT COVERED (UNVERIFIED in game): the engine's physics fall timing, a real performBlockBreak from a world task, a respawned tree standing,
setBlock of a crop stage key, the event title on a real client.
"""
import os, sys, hashlib, importlib.util, subprocess, zipfile, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK
import skyybuild as B

VERSION, OLD = "0.3.0", "0.2.2"
PKG = "com.skyy.zones."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyZones-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyZones-%s.jar" % OLD)
GEN = os.path.join(HERE, "build_skyyzones_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyzones_%s.py" % OLD)
PATCH = os.path.join(ROOT, "tools", "zones_0_3_0_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "zones03", "zh")))
LIVE = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods")
ADDED = ["ZShape", "ZTree", "ZFell", "ZMig"]
EXPECT = {   # checked 2026-10-24 (the class compare 0.2.2 -> 0.3.0 of the first harness run, every member a planned change of tools/zones_0_3_0_patch.py;
 # CfgFile / CfgFn / CfgRows / ZStore.parseAll / ZFn.publish = the version text, the new trees.properties file + rows)
    'CfgFile': ['~<clinit>', '~m init'],
    'CfgFn': ['~m opExport'],
    'CfgRows': ['+f DL3', '~<clinit>', '~m defLines', '~m header'],
    'SkyyZonesPlugin': ['~m paths', '~m setup'],
    'ZApi': ['+m breakAs'],
    'ZBox': ['~m drop', '~m restore'],
    'ZCfg': ['+f GATHERW', '+f GROUPS', '+f GROUP_TEXT', '+f GTARR', '+f GTSRC', '+f GTYPES', '+f GWSET', '+f GWSRC', '+f ORPHANS', '+f ORPHAN_TEXT', '+f TREES_TEXT', '+f TREE_CLEAR', '+f TREE_MAX', '+f TREE_SEC1', '+f TREE_SEC2', '+f TREE_SEC3', '+f XFILE', '+m checkGTypes', '+m checkGather', '+m gatherListed', '+m gatherTypes', '+m gatherWorld', '+m group', '+m groups', '+m inList', '+m loadTrees', '+m orphans', '+m treeSec', '~<clinit>', '~m checkPTypes', '~m checkRegrow', '~m checkWorlds', '~m loadCfg', '~m loadRegen', '~m loadTypes', '~m parseRegrow', '~m protectedWorld', '~m ptypes', '~m reloadFiles'],
    'ZCmds': ['~m grows', '~m help', '~m info', '~m list'],
    'ZEng': ['+m breakAs', '+m cropOf', '+m cropState', '+m known', '+m stageKey'],
    'ZFn': ['~m apply', '~m publish', '~m unpublish'],
    'ZGuard': ['+m crop', '+m gwhy', '+m harvest', '+m regrow', '+m unripe', '-m regrow', '~m handle'],
    'ZGuardBreak': ['+m crop'],
    'ZGuardDamage': ['+m crop'],
    'ZGuardUse': ['+m crop', '+m harvest'],
    'ZPass': ['~m pass'],
    'ZRegen': ['+f HARVESTED', '+m clearing', '+m delaySec', '+m dropTree', '+m fell', '+m harvested', '+m readShapes', '+m treeAt', '+m waitWhy', '~<clinit>', '~m audit', '~m beat', '~m broke', '~m delay', '~m depleted', '~m early', '~m readInto', '~m restore', '~m start', '~m status'],
    'ZRules': ['+m area', '+m fam', '+m gatherCell', '+m leafOk', '+m woodFam', '~m decide', '~m resType', '~m typeHas'],
    'ZRw': ['+f shapes', '+f shf', '+f sout', '+f tcheck', '+f tpos', '+f trecent', '+f trees', '+m addCheck', '+m addTree', '+m shapeOut', '+m treeDone', '+m treeDrop', '+m unmark', '~c ', '~m close', '~m snapshot'],
    'ZStore': ['~m parseAll'],
    'ZTick': ['+m gather', '~m titles'],
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
    K.check(g.startswith(b'"""SkyyZones 0.3.0') and g.count(b'VERSION = "0.3.0"') == 1, "S header + VERSION")
    for w in (b"registerSystem(", b"registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.check((b"\r\n" in g) == (b"\r\n" in o), "S line endings kept")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    src = open(PATCH, encoding="utf8").read().replace('os.path.join(ROOT, "SkyyZones", "build_skyyzones_0.3.0.py")', repr(os.path.join(d, "b.py")))
    open(os.path.join(d, "p.py"), "w", encoding="utf8").write(src.replace("ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))", "ROOT = %r" % ROOT))
    p = subprocess.run([sys.executable, os.path.join(d, "p.py")], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(os.path.join(d, "b.py"), "rb").read() == g, "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    with zipfile.ZipFile(jar) as z:
        pl = z.read("com/skyy/zones/SkyyZonesPlugin.class")
        names = z.namelist()
    K.check(b"[SkyyZones] 0.3.0 ready - " in pl, "S the ready line '[SkyyZones] 0.3.0 ready' (smoke_test.py)")
    K.check(not any(n.lower().endswith(".ui") for n in names), "S no .ui file in the jar")
    K.check(b"tier_tags" in g and b"TT.LOGS" in g and b"open(" not in g.split(b"import tier_tags as TT")[1].split(b"\n")[0], "S tools/tier_tags.py is only imported (read)")
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
             "Ore_Lead_Sandstone_SkyWynn", "Rock_Gem_Ruby"]
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
                      "Skyy_SkyyZones/config-changes.log") or f.startswith("Skyy_SkyyZones/config-history/") for f in chz), "D only Mig030's files change: %s" % chz)
    if old_r is not None:
        new_r = open(os.path.join(sz, "regen.properties"), "rb").read().decode("latin-1")
        o = old_r.decode("latin-1")
        K.check(new_r.startswith(o.replace("regrow.logs=0,none", "regrow.logs=60,none").replace("regrow.crops=0,none", "regrow.crops=10,stage1"))
                and new_r.rstrip().endswith("regrow.titanium=12,Rock_Bedrock"), "D Skyy's regen.properties: only the logs / crops values + the appended zone ore rows")
    K.notes.append("D: %s | %s" % (r1[:300], r2[:200]))
    K.save()


if __name__ == "__main__":
    HK.run("SkyyZones", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("static", run_static), ("fakes", run_fakes), ("exec", run_exec), ("mig", run_mig), ("live", run_live)], __file__, live=(LIVE, "mods"))
