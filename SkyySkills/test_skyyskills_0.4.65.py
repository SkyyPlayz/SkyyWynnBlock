"""SkyySkills 0.4.65 - harness for "SkyyZones builder-mode places are not placed" (tools/skills_0_4_65_patch.py; research/cloud/SkyyZones-0.3-Spec.md
step 3, Builder C). Build first:
    python tools/skills_0_4_65_patch.py && python SkyySkills/build_skyyskills_0.4.65.py
    python SkyySkills/test_skyyskills_0.4.65.py [--keep]
Phases (each a fresh child JVM: -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch; tools/harness_kit.py):
  S     static   the patch re-runs to identical bytes, line endings kept, no new class / system / command, VERSION
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.4.64 -> 0.4.65: exactly the planned members (EXPECT)
  F2    fakes    the SkyyZones 0.2.0 harness's engine stand-ins (Store / ArchetypeChunk / World / PlayerRef subclasses)
  X     EXECUTED PlaceSys.handle with a REAL PlaceBlockEvent on a stand-in world whose REAL World.execute queues the task: a player in
                 SkyyZones builder mode (bridge zones:build:<uuid> = TRUE) -> NO PlaceTask (no PlacedStore mark); key missing / FALSE / another
                 player / a mob place -> the PlaceTask as in 0.4.64; ignorePlaced off -> nothing either way
  R     EXECUTED SkillCfg.ripe + classifyBreak on engine BlockType objects (Unsafe-made like SkyyCollections 0.2.33's harness): a crop's
                 StageFinal, Crude, Best, Epic states are ripe + pay Farming XP on a break; Stage1 / Stage2 / planted (no Harvest) are not; a
                 stateless plant with a Harvest drop and a harvestable state of a block WITHOUT StageFinal are not; farmingNeedsRipe off = as 0.4.64.
                 Static: HarvestSys (F-harvest) and Sickle.addCrop (sickle swing crop map) call SkillCfg.ripe, no StageFinal-only check is left
  LIVE  start twice on a scratch COPY of the live Skyy_SkyySkills (every one-time update + load, the 0.4.64 harness's live phase): nothing
        written, start 2 changes nothing
  AA    engine-access audit
NOT COVERED (UNVERIFIED in game): a real builder placing an ore in a zone world, then a normal player's first break paying Mining XP; a real
DynamicSeasons Crude / Best crop paying Farming XP on break, F-harvest and a sickle swing (the per-state rule is executed here on fakes).
"""
import os, sys, subprocess, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK

if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "zones03", "sk")]


def _mod(path, name):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    a = list(sys.argv)
    s.loader.exec_module(m)
    sys.argv[:] = a
    return m


T64 = _mod(os.path.join(HERE, "test_skyyskills_0.4.64.py"), "test_skyyskills_0_4_64")
VERSION = "0.4.65"
PKG = "com.skyy.skills."
GEN = os.path.join(HERE, "build_skyyskills_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyskills_0.4.64.py")
PATCH = os.path.join(TOOLS, "skills_0_4_65_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySkills-0.4.64.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
LIVE_DIR = T64.LIVE_DIR
ADDED = []
EXPECT = {   # checked 2026-10-24 (the class compare vs 0.4.64 of the first harness run): PlaceSys.handle = THE change; the rest = the version text
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'CurveP9Mig': ['~m run'],
    'ManaGuard': ['~m armReport2', '~m intReport', '~m packReport'],
    'HarvestSys': ['~m handle'],
    'PlaceSys': ['~m handle'],
    'Sickle': ['~m addCrop'],
    'SkillCfg': ['+m ripe', '~m classifyBreak', '~m load'],
    'SkyySkillsPlugin': ['~m setup'],
}


def t20():
    return _mod(os.path.join(ROOT, "SkyyZones", "test_skyyzones_0.2.0.py"), "zones_t20")


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyySkills 0.4.65') and g.count('VERSION = "0.4.65"') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand(", "makeClass("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.check(g.count('get("zones:build:" + zp.getUuid())') == 1, "S PlaceSys reads the bridge key zones:build:<uuid>")
    K.check(g.count("if (!{PKG}.SkillCfg.ripe(bt)) return;") == 1 and g.count("if (!@PKG@.SkillCfg.ripe(bt)) return;") == 1 and g.count("NEED_RIPE && !ripe(bt)") == 1,
            "S every Farming-XP path uses SkillCfg.ripe: break (classifyBreak), F-harvest (HarvestSys), sickle swing (Sickle.addCrop)")
    K.check('"StageFinal".equals({PKG}.SkillCfg.stateOf' not in g and '"StageFinal".equals(@PKG@.SkillCfg.stateOf' not in g and '!"StageFinal".equals(stateOf(bt))' not in g,
            "S no StageFinal-only Farming check is left")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def run_fakes(out, jar, scratch, _home):
    T = t20()
    os.makedirs(os.path.join(scratch, "fake2"), exist_ok=True)
    T.run_mkfake(os.path.join(scratch, "fake2"))
    K = HK.Child(out)
    K.check(os.path.isdir(os.path.join(scratch, "fake2")), "F2: the stand-ins are written")
    K.save()


def run_x(out, jar, scratch, _home):
    from jpype import JClass, JInt
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, os.path.join(scratch, "fake2")], verify=True)
    T = t20()
    T.SCRATCH = scratch
    try:
        E = T.engine(K)
        U, jfield = E["U"], E["jfield"]
        FAKE = T.FAKE
        J = lambda n: JClass(PKG + n)
        Cfg, Sto, PS, PT, PST = J("SkillCfg"), J("SkillStore"), J("PlaceSys"), J("PlaceTask"), J("PlacedStore")
        Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
        MS, MB, MCH, FW, FP = (JClass(FAKE + "." + n) for n in ("MapStore", "MapBuffer", "MapChunk", "FakeWorld", "FakePr"))
        WLD = JClass("com.hypixel.hytale.server.core.universe.world.World")
        EST = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore")
        PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
        REF = JClass("com.hypixel.hytale.component.Ref")
        IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
        V3I = JClass("org.joml.Vector3i")
        PLBE = JClass("com.hypixel.hytale.server.core.event.events.ecs.PlaceBlockEvent")
        IHM, UUID, Bool = JClass("java.util.IdentityHashMap"), JClass("java.util.UUID"), JClass("java.lang.Boolean")
        w = U.allocateInstance(FW.class_)
        jfield(WLD, "name").set(w, "skywynn_zones2")
        jfield(WLD, "acceptingTasks").set(w, JClass("java.util.concurrent.atomic.AtomicBoolean")(True))
        q = JClass("java.util.concurrent.LinkedBlockingDeque")()
        jfield(WLD, "taskQueue").set(w, q)
        es = U.allocateInstance(EST.class_)
        jfield(EST, "world").set(es, w)
        st = U.allocateInstance(MS.class_)
        st.comps = IHM()
        st.ext = es
        cb = U.allocateInstance(MB.class_)
        n_ = [0]

        def player(name, k):
            n_[0] += 1
            r_ = REF(st, JInt(n_[0]))
            st.comps.put(r_, IHM())
            if name is None:
                ch_ = U.allocateInstance(MCH.class_)
                ch_.ref = r_
                return ch_, None
            pr_ = U.allocateInstance(FP.class_)
            jfield(PRc, "uuid").set(pr_, UUID.fromString("00000000-0000-4000-8000-%012x" % (0x6500 + k)))
            jfield(PRc, "username").set(pr_, name)
            st.comps.get(r_).put(PRc.getComponentType(), pr_)
            ch_ = U.allocateInstance(MCH.class_)
            ch_.ref = r_
            return ch_, pr_
        chB, prB = player("Builder", 1)
        chP, prP = player("Player", 2)
        chM, _ = player(None, 3)
        br = Sto.bridge()
        ps = PS()

        def place(ch_, x):
            e_ = PLBE(IS("Rock_Stone", 1), V3I(x, 64, 7), None)
            n0 = q.size()
            ps.handle(0, ch_, st, cb, e_)
            return q.size() - n0
        Cfg.IGNORE_PLACED = True
        key = "zones:build:" + str(prB.getUuid())
        br.put(key, Bool.TRUE)
        K.check(place(chB, 1) == 0, "X a place by a player in SkyyZones builder mode (zones:build:<uuid> TRUE) queues NO PlaceTask - never marked placed")
        K.check(place(chP, 2) == 1 and isinstance(q.peekLast(), PT), "X another player (not in builder mode) - the PlaceTask as in 0.4.64")
        K.check(place(chM, 3) == 1, "X a mob place (no player) - as in 0.4.64")
        br.put(key, Bool.FALSE)
        K.check(place(chB, 4) == 1, "X the key FALSE - as in 0.4.64")
        br.remove(key)
        K.check(place(chB, 5) == 1, "X the key missing (builder mode off / no SkyyZones) - as in 0.4.64")
        br.put(key, "true")
        K.check(place(chB, 6) == 1, "X only Boolean.TRUE counts (a String 'true' is not SkyyZones' key)")
        br.put(key, Bool.TRUE)
        Cfg.IGNORE_PLACED = False
        K.check(place(chB, 7) == 0 and place(chP, 8) == 0, "X ignorePlaced off - nothing is queued either way (unchanged)")
        Cfg.IGNORE_PLACED = True
        br.remove(key)
    except Exception as e:
        import traceback
        traceback.print_exc()
        K.check(False, "X: run crashed: %s" % str(e)[:400])
    K.save()


def run_ripe(out, jar, scratch, _home):
    from jpype import JClass, JArray, JLong
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Cfg = JClass(PKG + "SkillCfg")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U_ = uf.get(None)

    def findf(k, n):
        while k is not None:
            try:
                f = k.getDeclaredField(n)
                f.setAccessible(True)
                return f
            except Exception:
                k = k.getSuperclass()
        raise KeyError(n)

    def setany(o, n, v):
        findf(o.getClass(), n).set(o, v)
    BTY = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType")
    SDT = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.StateData")
    BGA = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockGathering")
    HDT = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.HarvestingDropType")
    HM = JClass("java.util.HashMap")

    def mkstates(item, names):
        sd = U_.allocateInstance(SDT.class_)
        s2b, b2s = HM(), HM()
        for nm in names:
            sid = "*%s_State_Definitions_%s" % (item, nm)
            s2b.put(nm, sid)
            b2s.put(sid, nm)
        setany(sd, "stateToBlock", s2b)
        setany(sd, "blockToState", b2s)
        return sd

    def mkbt(item, state, sd, harvest):
        bt = U_.allocateInstance(BTY.class_)
        setany(bt, "id", "*%s_State_Definitions_%s" % (item, state) if state else item)
        setany(bt, "state", sd)
        if harvest:
            g = U_.allocateInstance(BGA.class_)
            setany(g, "harvest", HDT(None, harvest))
            setany(bt, "gathering", g)
        return bt
    lt = "Plant_Crop_Lettuce_Block"
    sd = mkstates(lt, ["Stage1", "Stage2", "StageFinal", "Crude", "Best", "Epic"])
    K.check(str(Cfg.stateOf(mkbt(lt, "Crude", sd, "x"))) == "Crude" and str(Cfg.familyId(mkbt(lt, "Crude", sd, "x"))) == lt,
            "R the fake block reads its state + family like the engine")
    Cfg.EXACT.put(lt, JArray(JLong)([2, 7]))   # the block rule: Farming 7 XP (the live config names the crop blocks the same way)
    Cfg.CACHE.clear()
    Cfg.NEED_RIPE = True
    for st_, hv, want in (("StageFinal", "Drops_Plant_Crop_Lettuce_StageFinal_Harvest", True), ("Crude", "Drops_Plant_Crop_Lettuce_Eternal_Poor_Harvest", True),
                          ("Best", "Drops_Plant_Crop_Lettuce_Eternal_Best_Harvest", True), ("Epic", "Drops_X_Epic", True),
                          ("Stage1", None, False), ("Stage2", None, False)):
        b_ = mkbt(lt, st_, sd, hv)
        r_ = Cfg.classifyBreak(b_)
        K.eq(bool(Cfg.ripe(b_)), want, "R Lettuce %s ripe = %s" % (st_, want))
        K.check((r_ is not None and int(r_[0]) == 2 and int(r_[1]) > 0 and int(r_[2]) == 0) if want else r_ is None,
                "R Lettuce %s: a break %s" % (st_, "pays Farming XP (no placed check - it only gets ripe by growing)" if want else "pays NO Farming XP (not ripe)"))
    K.check(not bool(Cfg.ripe(mkbt(lt, None, sd, None))) and Cfg.classifyBreak(mkbt(lt, None, sd, None)) is None, "R the default (just planted) state is not ripe, no XP")
    hp = "Plant_Crop_Health1"
    K.check(not bool(Cfg.ripe(mkbt(hp, None, None, "Drops_Health1"))), "R a stateless Health plant with a Harvest drop is not ripe (placeable - no loop)")
    sd2 = mkstates("Plant_Crop_Wild_Grass_Block", ["Stage1", "Stage2", "Stage3"])
    K.check(not bool(Cfg.ripe(mkbt("Plant_Crop_Wild_Grass_Block", "Stage2", sd2, "Drops_Grass"))), "R a harvestable state of a block WITHOUT StageFinal is not ripe")
    K.check(not bool(Cfg.ripe(None)), "R null")
    Cfg.NEED_RIPE = False
    r_ = Cfg.classifyBreak(mkbt(lt, "Stage1", sd, None))
    K.check(r_ is not None and int(r_[0]) == 2, "R farmingNeedsRipe off - any stage pays (as 0.4.64)")
    Cfg.NEED_RIPE = True
    K.save()


def run_live(out, jar, scratch, home):
    T64.run_live(out, jar, scratch, home)


if __name__ == "__main__":
    phases = [("static", run_static), ("fakes", run_fakes), ("x", run_x), ("ripe", run_ripe), ("live", run_live)]
    HK.run(name="SkyySkills", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=phases, script=__file__, live=(LIVE_DIR, "Skyy_SkyySkills"))
