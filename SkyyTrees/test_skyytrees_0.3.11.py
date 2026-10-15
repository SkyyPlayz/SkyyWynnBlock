"""SkyyTrees 0.3.11 - harness for REPLANT FELLED TREES (tools/trees_0_3_11_patch.py), on top of every 0.3.10 section (test_skyytrees_0.3.10.py,
kept as the regression on the 0.3.11 jar). Child JVMs run the game's own JRE with the cached HytaleServer.jar copy, -Xverify:all,
-XX:-UsePerfData, TEMP / TMP in the scratch folder. The live save data is only READ and copied into scratch.

    python SkyyTrees/test_skyytrees_0.3.11.py --dir <empty folder inside tools/dev/scratch/> [--keep]

SECTIONS: A load + verify both jars; CC class compare 0.3.10 -> 0.3.11 (TreeReplant + TreeReplantTask added; structural changes only in the
classes the patch names); JT assets + manifest; AB every 0.3.10 scenario (real SkyyClasses 0.1.25); RP the replant EXECUTED on the real classes
(the TEST_BLOCKS seam stands in for the world's blocks; the real delayedExecutor timer runs): the sapling table (Oak, Birch, Fir -> Spruce,
Burnt none, variants), soil, the island role gate (owner / admin / member / trusted yes; visitor / banned / no island / no SkyyIslands / a
throwing bridge no), one pending replant per tree (logs within 6 blocks; another tree = its own), the timer restarts with every log and plants
only after the quiet delay, the spot (one below the lowest log, through air down to soil; a stump log / a placed block / stone = none),
the switch (off = nothing new, and a pending one is dropped), the config rows + apply (defaults, clamps), TreeFelledFn.apply -> note (static);
REVIEW FIXES: trees.replantWhere (all = everywhere, the default per Skyy's popup; island = the role gate), the sapling drop (trees.saplingDropPct:
100 % = once per tree, 0 % = never; with the replant off a drop still works), a stale pending replant (its world hop never ran) is pruned;
ST start twice on a scratch copy of the live Skyy_SkyyTrees (= 0.3.10's start); Z the engine-access audit.
"""
import os, sys, json, time, shutil, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, PREV_VERSION = "0.3.11", "0.3.10"
PKG = "com.skyy.trees."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "start033fix", "trees")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)))
PREV_JAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyyTrees-%s.jar" % PREV_VERSION)))
_saved = list(sys.argv)
sys.argv = [sys.argv[0], "--dir", SCRATCH, "--jar", JAR, "--prev", PREV_JAR]
_spec = importlib.util.spec_from_file_location("test_skyytrees_0_3_10", os.path.join(HERE, "test_skyytrees_0.3.10.py"))
T310 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T310)
sys.argv = _saved
T310.SCRATCH, T310.JAR, T310.PREV_JAR = SCRATCH, JAR, PREV_JAR
CL_JAR, LIVE = T310.CL_JAR, T310.LIVE
FAILS, OKS = [], [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


# ============================================================================================================ child: RP (the replant)
def run_rp(out):
    from jpype import JClass, JImplements, JOverride, JString
    import skyybuild as B
    import harness_kit as HK
    import perfworld_kit as PW
    import soundpass_kit as SK
    HK.jvm([B.SERVER_JAR, JAR, B.JAVASSIST], verify=True)
    R = {"checks": [], "notes": []}

    def ck(c, w):
        R["checks"].append([bool(c), w])
        if not c:
            print("FAIL", w)
    T = lambda n: JClass(PKG + n)
    RP, Task, Cfg, Store = T("TreeReplant"), T("TreeReplantTask"), T("TreeCfg"), T("TreeStore")
    UUID, HashMap = JClass("java.util.UUID"), JClass("java.util.concurrent.ConcurrentHashMap")
    br = Store.bridge()

    @JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, f):
            self.f = f
            self.calls = []

        @JOverride
        def apply(self, a):
            self.calls.append([str(x) for x in a])
            return self.f(a)
    # ---- the sapling table + soil
    for w, want in (("Wood_Oak_Trunk", "Plant_Sapling_Oak"), ("Wood_Birch_Trunk", "Plant_Sapling_Birch"), ("Wood_Fir_Trunk", "Plant_Sapling_Spruce"),
                    ("Wood_Fig_Blue_Trunk", "Plant_Sapling_Fig_Blue"), ("Wood_Oak_Trunk_Full", "Plant_Sapling_Oak"), ("Wood_Burnt_Trunk", None),
                    ("Wood_Oak_Planks", None), ("Plant_Leaves_Oak", None), ("", None), (None, None)):
        got = RP.sapOf(w)
        ck((None if got is None else str(got)) == want, "RP sapling of %s = %s (got %s)" % (w, want, got))
    ck(bool(RP.isSoil("Soil_Grass")) and bool(RP.isSoil("Soil_Dirt")) and bool(RP.isSoil("Soil_Dirt_Tilled")) and not bool(RP.isSoil("Rock_Stone"))
       and not bool(RP.isSoil("Wood_Oak_Trunk")) and not bool(RP.isSoil(None)), "RP soil = the Type=Soil blocks (grass, dirt, tilled yes; stone, logs no)")
    ck(bool(RP.isAir("")) and bool(RP.isAir("Empty")) and not bool(RP.isAir(None)) and not bool(RP.isAir("Soil_Grass")), "RP air = '' / Empty; null (not loaded) is not air")
    # ---- the island role gate
    me = UUID(0x7ee5, 311)
    W = "skyy-island-" + str(me)
    ck(not bool(Cfg.REPLANT_ISLAND), "RP FIX trees.replantWhere defaults to all (everywhere, Skyy's popup answer)")
    ck(bool(RP.allowed(me, W)) and bool(RP.allowed(me, "skyy-hub")), "RP FIX everywhere: allowed without SkyyIslands, in an island world and the hub")
    Cfg.REPLANT_ISLAND = True                    # the role gate below = trees.replantWhere=island
    ck(not bool(RP.allowed(me, W)), "RP no SkyyIslands (no island:role:fn) = never")
    role = ["owner"]
    rf = Fn(lambda a: None if role[0] is None else JString(role[0]))
    br.put("island:role:fn", rf)
    for r_, want in (("owner", True), ("admin", True), ("member", True), ("trusted", True), ("visitor", False), ("banned", False), (None, False)):
        role[0] = r_
        ck(bool(RP.allowed(me, W)) == want, "RP island role %s -> %s" % (r_, want))
    ck(rf.calls and rf.calls[-1] == [str(me), W], "RP island:role:fn asked with {UUID, world}: %s" % rf.calls[-1:])
    br.put("island:role:fn", Fn(lambda a: 1 / 0))
    ck(not bool(RP.allowed(me, W)), "RP a throwing island:role:fn = never (no throw)")
    br.put("island:role:fn", rf)
    role[0] = "owner"
    # ---- the config rows + apply
    rows = SK.kit_rows(T("CfgRows"))
    ck(rows.get("trees.replantWhere", [None] * 11)[1:10] == ["Replant + drops in", "abilities", "choice", "all", "", "", "all|Everywhere,island|Own island only", "", "live"]
       and rows.get("trees.saplingDropPct", [None] * 11)[1:10] == ["Sapling drop chance", "abilities", "int", "10", "0", "100", "", "%", "live"],
       "RP FIX Server Setup rows: Replant + drops in (Everywhere / Own island only, default Everywhere) + Sapling drop chance (10 %%, 0-100): %s / %s"
       % (rows.get("trees.replantWhere"), rows.get("trees.saplingDropPct")))
    ck("SkyySkills" in str(rows.get("trees.replant", [""] * 11)[10]), "RP FIX the Replant help names the SkyySkills felled-log dependency: %s" % (rows.get("trees.replant", [""] * 11)[10],))
    ck(rows.get("trees.replant", [None] * 11)[1:10] == ["Replant felled trees", "abilities", "bool", "true", "", "", "", "", "live"]
       and rows.get("trees.replantDelaySec", [None] * 11)[1:10] == ["Replant delay", "abilities", "int", "5", "1", "60", "", "s", "live"],
       "RP Server Setup -> Trees -> Abilities: Replant felled trees (on) + Replant delay (5 s, 1-60): %s / %s" % (rows.get("trees.replant"), rows.get("trees.replantDelaySec")))
    P = JClass("java.util.Properties")
    Cfg.apply(P())
    ck(bool(Cfg.REPLANT) and int(Cfg.REPLANT_MS) == 5000, "RP a file without the lines = on, 5 s")
    ck(not bool(Cfg.REPLANT_ISLAND) and int(Cfg.SAP_DROP_PCT) == 10, "RP FIX a file without the lines = everywhere, 10 % drop")
    p2 = P()
    p2.setProperty("trees.replantWhere", "Island")
    p2.setProperty("trees.saplingDropPct", "250")
    Cfg.apply(p2)
    ck(bool(Cfg.REPLANT_ISLAND) and int(Cfg.SAP_DROP_PCT) == 100, "RP FIX trees.replantWhere=island read (any case); the drop clamped to 100 %")
    p2.setProperty("trees.saplingDropPct", "-5")
    p2.setProperty("trees.replantWhere", "all")
    Cfg.apply(p2)
    ck(not bool(Cfg.REPLANT_ISLAND) and int(Cfg.SAP_DROP_PCT) == 0, "RP FIX all = everywhere; the drop clamped to 0")
    p_ = P()
    p_.setProperty("trees.replant", "false")
    p_.setProperty("trees.replantDelaySec", "99")
    Cfg.apply(p_)
    ck(not bool(Cfg.REPLANT) and int(Cfg.REPLANT_MS) == 60000, "RP trees.replant=false read; the delay clamped to 60 s")
    p_.setProperty("trees.replantDelaySec", "0")
    Cfg.apply(p_)
    ck(int(Cfg.REPLANT_MS) == 1000, "RP the delay clamped to at least 1 s")
    dflt = str(Cfg.DEFAULTS) if hasattr(Cfg, "DEFAULTS") else ""
    R["notes"].append("default file has the lines: %s" % ("trees.replant=true" in dflt and "trees.replantDelaySec=5" in dflt and "trees.replantWhere=all" in dflt and "trees.saplingDropPct=10" in dflt))
    # ---- the plant path (TEST_BLOCKS = the world's blocks; the real timer)
    tb = HashMap()
    RP.TEST_BLOCKS = tb
    Cfg.REPLANT = True
    Cfg.REPLANT_MS = 300
    Cfg.REPLANT_ISLAND = True
    Cfg.SAP_DROP_PCT = 0                         # the plant scenarios: no drop roll (1 = new, 2 = joined)
    put = lambda x, y, z, b: tb.put("%d|%d|%d" % (x, y, z), b)
    get = lambda x, y, z: None if tb.get("%d|%d|%d" % (x, y, z)) is None else str(tb.get("%d|%d|%d" % (x, y, z)))
    # tree A: grass at y 63, the cut base log at y 64 (now air), felled logs 65-70 + a branch
    put(5, 63, 5, "Soil_Grass")
    ck(int(RP.note2(None, W, me, "Wood_Oak_Trunk", 5, 67, 5)) == 1 and int(RP.pending()) == 1, "RP the first felled log = a new pending replant")
    for y in (66, 68, 69, 70, 65):
        ck(int(RP.note2(None, W, me, "Wood_Oak_Trunk", 5, y, 5)) == 2, "RP log y=%d joins the same tree" % y)
    ck(int(RP.note2(None, W, me, "Wood_Oak_Trunk", 7, 68, 6)) == 2 and int(RP.pending()) == 1, "RP a branch log 2 blocks away joins it (one replant per tree)")
    time.sleep(0.15)
    RP.note2(None, W, me, "Wood_Oak_Trunk", 6, 69, 5)
    time.sleep(0.2)
    ck(get(5, 64, 5) is None and int(RP.pending()) == 1, "RP 0.35 s after the first log (0.2 s after the last): nothing planted yet - the timer restarts with every log")
    time.sleep(0.5)
    ck(get(5, 64, 5) == "Plant_Sapling_Oak" and int(RP.pending()) == 0 and int(RP.PLANTED) == 1,
       "RP the quiet delay after the LAST log: Plant_Sapling_Oak planted on the stump spot (one below the lowest log), nothing pending")
    # another tree 20 blocks away while one is pending = its own replant; Fir -> Spruce; deeper air (the cut 3 above the ground)
    put(30, 63, 5, "Soil_Dirt")
    put(50, 63, 5, "Soil_Grass")
    RP.note2(None, W, me, "Wood_Oak_Trunk", 30, 65, 5)
    RP.note2(None, W, me, "Wood_Fir_Trunk", 50, 67, 5)
    ck(int(RP.pending()) == 2, "RP two trees = two pending replants")
    time.sleep(0.8)
    ck(get(30, 64, 5) == "Plant_Sapling_Oak" and get(50, 64, 5) == "Plant_Sapling_Spruce" and get(50, 66, 5) is None,
       "RP both planted; a Fir gets a Spruce sapling; the spot goes down through air to the soil (64, not 66)")
    # spots that must NOT get a sapling
    put(10, 63, 10, "Soil_Grass"); put(10, 64, 10, "Wood_Oak_Trunk")               # a mid-trunk cut: the stump log stays
    put(14, 63, 10, "Soil_Grass"); put(14, 64, 10, "Furniture_Crude_Chest_Small")   # something placed on the spot
    put(18, 63, 10, "Rock_Stone")                                                   # stone ground
    put(22, 58, 10, "Soil_Grass")                                                   # the ground more than 4 below the cut
    for x in (10, 14, 18):
        RP.note2(None, W, me, "Wood_Oak_Trunk", x, 66 if x == 10 else 65, 10)
    RP.note2(None, W, me, "Wood_Oak_Trunk", 22, 65, 10)
    time.sleep(0.8)
    ck(get(10, 65, 10) is None and get(10, 64, 10) == "Wood_Oak_Trunk", "RP a mid-trunk cut (a log below the spot): no sapling")
    ck(get(14, 64, 10) == "Furniture_Crude_Chest_Small", "RP a block someone put on the spot: no sapling, the block stays")
    ck(get(18, 64, 10) is None, "RP stone ground: no sapling")
    ck(not [k for k in tb.keySet() if str(tb.get(k)).startswith("Plant_Sapling") and str(k).startswith("22|")], "RP the ground more than 4 below: no sapling")
    ck(int(RP.pending()) == 0 and int(RP.PLANTED) == 3, "RP nothing left pending, 3 planted so far")
    # not their island / no island / not a natural trunk / the switch
    role[0] = "visitor"
    ck(int(RP.note2(None, W, me, "Wood_Oak_Trunk", 60, 65, 5)) == 0 and int(RP.pending()) == 0, "RP a VISITOR felling a tree: nothing")
    role[0] = None
    ck(int(RP.note2(None, "skyy-hub", me, "Wood_Oak_Trunk", 60, 65, 5)) == 0, "RP a non-island world (role null): nothing")
    role[0] = "member"
    ck(int(RP.note2(None, W, me, "Plant_Leaves_Oak", 60, 70, 5)) == 0 and int(RP.note2(None, W, me, "Wood_Burnt_Trunk", 60, 65, 5)) == 0,
       "RP leaves / a wood with no sapling: nothing")
    put(70, 63, 5, "Soil_Grass")
    ck(int(RP.note2(None, W, me, "Wood_Birch_Trunk", 70, 65, 5)) == 1, "RP a co-op MEMBER: pending")
    Cfg.REPLANT = False
    ck(int(RP.note2(None, W, me, "Wood_Oak_Trunk", 80, 65, 5)) == 0, "RP switched OFF: no new replant")
    time.sleep(0.8)
    ck(get(70, 64, 5) is None and int(RP.pending()) == 0, "RP switched off while one was pending: dropped, nothing planted")
    Cfg.REPLANT = True
    # FIX: the scope switch - everywhere (the default) plants for a visitor / in a non-island world too
    Cfg.REPLANT_ISLAND = False
    role[0] = None
    put(90, 63, 5, "Soil_Grass")
    ck(int(RP.note2(None, "skyy-hub", me, "Wood_Oak_Trunk", 90, 65, 5)) == 1, "RP FIX everywhere: a tree felled in the hub (role null) gets a pending replant")
    time.sleep(0.8)
    ck(get(90, 64, 5) == "Plant_Sapling_Oak", "RP FIX ... and its sapling is planted")
    # FIX: the sapling drop - 100 % = once per tree (3 on the first log, 2 for the rest), 0 % = never; the replant off + drops on still groups
    Cfg.SAP_DROP_PCT = 100
    ck(int(RP.note2(None, W, me, "Wood_Birch_Trunk", 100, 66, 5)) == 3 and int(RP.note2(None, W, me, "Wood_Birch_Trunk", 100, 67, 5)) == 2,
       "RP FIX drop 100 %%: the first log of a tree = 3 (the sapling drop), the next log of that tree = 2 (once per tree)")
    Cfg.SAP_DROP_PCT = 0
    ck(int(RP.note2(None, W, me, "Wood_Birch_Trunk", 120, 66, 5)) == 1, "RP FIX drop 0 %: a new tree = 1 (no drop)")
    Cfg.REPLANT = False
    ck(int(RP.note2(None, W, me, "Wood_Birch_Trunk", 140, 66, 5)) == 0, "RP FIX replant off + drop 0 %: nothing at all")
    Cfg.SAP_DROP_PCT = 100
    put(160, 63, 5, "Soil_Grass")
    ck(int(RP.note2(None, W, me, "Wood_Birch_Trunk", 160, 65, 5)) == 3, "RP FIX replant off + drop on: the tree still rolls its drop")
    time.sleep(0.8)
    ck(get(160, 64, 5) is None and int(RP.pending()) == 0, "RP FIX ... but no sapling is planted (the replant is off)")
    Cfg.REPLANT_ISLAND = True
    role[0] = "visitor"
    ck(int(RP.note2(None, W, me, "Wood_Birch_Trunk", 180, 65, 5)) == 0, "RP FIX own island only: a visitor gets no drop either")
    role[0] = "member"
    Cfg.REPLANT = True
    Cfg.SAP_DROP_PCT = 0
    Cfg.REPLANT_ISLAND = False
    # FIX: a stale pending replant (its world hop never ran) is pruned when a new one is kept - the list never fills up
    old = Task(None, W, me, 200, 65, 5, "Plant_Sapling_Oak")
    old.stage = 1
    ck(bool(RP.keep(old)) and int(RP.pending()) == 1, "RP FIX a replant stuck after its world hop sits in the pending list")
    old.last = 0
    nw = Task(None, W, me, 220, 65, 5, "Plant_Sapling_Oak")
    nw.stage = 1
    ck(bool(RP.keep(nw)) and int(RP.pending()) == 1 and not bool(RP.PEND.contains(old)) and bool(RP.PEND.contains(nw)),
       "RP FIX ... older than its delay + 60 s: dropped when the next replant is kept (the fresh one stays)")
    for i in range(300):
        t_ = Task(None, W, me, 300 + i * 20, 65, 5, "Plant_Sapling_Oak")
        t_.stage = 1
        t_.last = 0
        RP.keep(t_)
    ck(int(RP.pending()) <= 2, "RP FIX 300 stuck replants never fill the 256 list (%d pending)" % int(RP.pending()))
    RP.PEND.clear()
    # the timer's world hop: with a world the plant runs through World.execute (stage 1) - here a null world without the seam = no throw
    RP.TEST_BLOCKS = None
    t0 = Task(None, W, me, 1, 65, 1, "Plant_Sapling_Oak")
    t0.last = 0
    pl0 = int(RP.PLANTED)
    t0.run()
    ck(int(t0.stage) == 1 and int(RP.PLANTED) == pl0 == 4, "RP no world, no seam: the timer runs, nothing planted, no throw")
    # static: who calls what
    g = PW.calls(JAR)
    ck(PKG + "TreeReplant.note" in g.get("TreeFelledFn.apply", set()), "STATIC TreeFelledFn.apply (SkyySkills' skill:on:felled) -> TreeReplant.note")
    ck(PKG + "TreeReplant.note2" in g.get("TreeReplant.note", set()) and PKG + "TreeAbil.worldOf" in g.get("TreeReplant.note", set()), "STATIC note -> worldOf + note2")
    ck(PKG + "TreeGather.giveItem" in g.get("TreeReplant.note", set()) and PKG + "TreeStore.busy" in g.get("TreeReplant.note", set()),
       "STATIC FIX the sapling drop is given by note (world thread) through TreeGather.giveItem, never while the profile is busy")
    ck(PKG + "TreeReplant.plantNow" in g.get("TreeReplantTask.run", set()) and PKG + "TreeReplant.allowed" in g.get("TreeReplant.note2", set()),
       "STATIC the timer plants through plantNow; note2 asks the island gate")
    callers = sorted(k for k, v in g.items() if PKG + "TreeReplant.place" in v)
    ck(callers == ["TreeReplant.plant"], "STATIC only TreeReplant.plant places a block: %s" % callers)
    R["notes"].append("RP %d checks" % len(R["checks"]))
    json.dump(R, open(out, "w"), indent=1)
    sys.stdout.flush()
    os._exit(0)


# ============================================================================================================ parent
def main():
    if "--ab" in sys.argv:
        return T310.run_ab(arg("--out"))
    if "--rp" in sys.argv:
        return run_rp(arg("--out"))
    T = T310.t36()
    if "--load" in sys.argv:
        return T.run_load(arg("--load"), arg("--out"))
    if "--cc" in sys.argv:
        return T.sk().run_cc(arg("--cc"), arg("--prevjar"), arg("--out"), arg("--repl"))
    if "--st" in sys.argv:
        return T.t34().run_start(arg("--st"), arg("--fake"), arg("--live"), arg("--out"), arg("--tag"))
    if "--mkfake" in sys.argv:
        T.t34().t33().H.run_mkfake(arg("--mkfake"))
        return
    if "--audit" in sys.argv:
        H = T.t34().t33().H
        H.SCRATCH = SCRATCH
        H.run_audit(arg("--audit"), arg("--fake"), arg("--out"))
        return
    for j in (JAR, PREV_JAR, CL_JAR):
        if not os.path.isfile(j):
            sys.exit("no jar at %s - build it first" % j)
    sroot = os.path.realpath(os.path.join(TOOLS, "dev", "scratch"))
    if not os.path.realpath(SCRATCH).startswith(sroot + os.sep):
        sys.exit("--dir must be inside tools/dev/scratch/ (deleted afterwards): %s" % SCRATCH)
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.makedirs(env["TEMP"], exist_ok=True)
    live_before = T310.snap(LIVE)
    me = os.path.abspath(__file__)

    def child(args_, out_):
        with open(out_ + ".log", "wb") as lf:
            subprocess.run([sys.executable, me] + args_ + ["--out", out_, "--dir", SCRATCH], env=env, stdout=lf, stderr=subprocess.STDOUT)
        if not os.path.isfile(out_):
            print(open(out_ + ".log", encoding="utf8", errors="replace").read()[-3000:])
            return None
        return json.load(open(out_))
    try:
        for tag, j in (("new", JAR), ("prev", PREV_JAR)):
            r = child(["--load", j], os.path.join(SCRATCH, "load-%s.json" % tag)) or {}
            check(r and not r.get("load_fails") and r.get("classes", 0) >= 30,
                  "A (%s): %s classes load, verify (-Xverify:all), initialise %s" % (tag, r.get("classes"), r.get("load_fails", [])[:3]))
        rules = [[r"storage\.ChunkGrid\.", "storage.ChunkStore."]]
        cc = child(["--cc", JAR, "--prevjar", PREV_JAR, "--repl", json.dumps({"versions": [VERSION, PREV_VERSION], "rules": rules})],
                   os.path.join(SCRATCH, "cc.json"))
        check(cc is not None, "CC: the compare child ran")
        if cc:
            cls_ = cc["classes"]
            KIT = {"CfgFn", "CfgRows", "CfgPub", "CfgKit", "CfgHist", "CfgImp", "CfgText"}
            check(sorted(cc["added"]) == ["TreeReplant", "TreeReplantTask"] and not cc["gone"], "CC: added exactly TreeReplant + TreeReplantTask, none removed: %s %s" % (cc["added"], cc["gone"]))
            gone = dict((c, v["fields_gone"]) for c, v in cls_.items() if v["fields_gone"])
            check(not gone, "CC: no field removed: %s" % gone)
            struct = dict((c, sorted(m.split("(")[0] for m in v["structural"])) for c, v in cls_.items() if v["structural"] and c not in KIT)
            print("CC. 0.3.10 -> 0.3.11 structural: %s" % struct)
            newf = dict((c, v["fields_new"]) for c, v in cls_.items() if v["fields_new"])
            print("CC. new fields: %s" % newf)
            # TreeFelledFn.apply -> note; TreeCfg: REPLANT / REPLANT_MS + apply + the default file (DEFAULTS); CfgFile = the version text
            allowed = {"TreeFelledFn", "TreeCfg", "CfgFile"}
            check(set(struct) <= allowed, "CC: structural changes only in %s: %s" % (sorted(allowed), sorted(set(struct) - allowed)))
            check(newf == {"TreeCfg": ["REPLANT:Z", "REPLANT_ISLAND:Z", "REPLANT_MS:J", "SAP_DROP_PCT:I"]} or
                  (list(newf) == ["TreeCfg"] and sorted(newf["TreeCfg"]) == ["REPLANT:Z", "REPLANT_ISLAND:Z", "REPLANT_MS:J", "SAP_DROP_PCT:I"]),
                  "CC: the only new fields of old classes are TreeCfg.REPLANT / REPLANT_MS / REPLANT_ISLAND / SAP_DROP_PCT: %s" % newf)
        zj, zp = zipfile.ZipFile(JAR), zipfile.ZipFile(PREV_JAR)
        nn = set(n for n in zj.namelist() if not n.endswith(".class"))
        np_ = set(n for n in zp.namelist() if not n.endswith(".class"))
        diff = sorted(n for n in (nn | np_) if n != "manifest.json" and (n not in nn or n not in np_ or zj.read(n) != zp.read(n)))
        check(not diff, "JT: every asset is byte for byte 0.3.10's: %s" % diff[:5])
        mn, mp = json.loads(zj.read("manifest.json")), json.loads(zp.read("manifest.json"))
        mnd, mpd = dict(mn), dict(mp)
        mnd.pop("Description", None)
        mpd.pop("Description", None)
        check(json.dumps(mnd, sort_keys=True) == json.dumps(mpd, sort_keys=True).replace(PREV_VERSION, VERSION), "JT: manifest = 0.3.10's but the version (+ description)")
        rp = child(["--rp"], os.path.join(SCRATCH, "rp.json"))
        check(rp is not None, "RP ran")
        if rp:
            for n in rp.get("notes", []):
                print("RP. " + n)
            for ok, what in rp.get("checks", []):
                check(ok, what)
            check(len(rp.get("checks", [])) >= 65, "RP: every replant scenario ran (%d checks)" % len(rp.get("checks", [])))
        ab = child(["--ab"], os.path.join(SCRATCH, "ab.json"))
        check(ab is not None, "AB ran")
        if ab:
            for ok, what in ab.get("checks", []):
                check(ok, what)
            print("AB. %d executed checks (the 0.3.10 scenarios on the 0.3.11 jar)" % len(ab.get("checks", [])))
            check(len(ab.get("checks", [])) >= 40, "AB: every scenario ran (%d checks)" % len(ab.get("checks", [])))
        fake = os.path.join(SCRATCH, "fake")
        subprocess.run([sys.executable, me, "--mkfake", fake, "--dir", SCRATCH], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        sts = {}
        for tag, j in (("new", JAR), ("prev", PREV_JAR)):
            sts[tag] = child(["--st", j, "--fake", fake, "--live", LIVE, "--tag", tag], os.path.join(SCRATCH, "st-%s.json" % tag))
            check(sts[tag] is not None and len(sts[tag].get("starts", [])) == 2, "ST (%s): two starts ran" % tag)
        if sts.get("new") and sts.get("prev"):
            T34 = T.t34()
            nz = lambda r: T34.norm_start(r).replace(VERSION, "0.3.X").replace(PREV_VERSION, "0.3.X")
            sn, sp = sts["new"]["starts"], sts["prev"]["starts"]
            check(nz(sn[0]) == nz(sp[0]), "ST: start 1 of 0.3.11 = 0.3.10's (the live file is not rewritten): %s / %s" % (sn[0]["changed"], sp[0]["changed"]))
            check(sn[1]["changed"] == [] and sn[1]["sum"] == sn[0]["sum"], "ST: start 2 changes nothing and reads the same: %s" % sn[1]["changed"])
            print("ST. start twice on the live copy: start 1 changed %s (same as 0.3.10), start 2 nothing" % sn[0]["changed"])
        au = child(["--audit", JAR, "--fake", fake], os.path.join(SCRATCH, "audit.json"))
        check(au is not None, "Z: the audit child ran")
        if au:
            check(not au.get("refused") and au.get("refs", 0) > 2000, "Z: engine-access audit: %s references, 0 refused: %s" % (au.get("refs"), str(au.get("refused"))[:400]))
            check(len(au.get("control") or []) >= 1, "Z: the audit's control is refused")
            print("Z. %s references, %d refused" % (au.get("refs"), len(au.get("refused") or [])))
        check(T310.snap(LIVE) == live_before, "the live Skyy_SkyyTrees folder was never written (only read + copied)")
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyTrees %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
