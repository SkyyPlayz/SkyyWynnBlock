"""Harness for SkyyZones 0.3.3 (hotfix: chests + furnaces open outside regions of a whole-island gathering world; tools/zones_0_3_3_patch.py).
Build first:  python tools/zones_0_3_3_patch.py && python SkyyZones/build_skyyzones_0.3.3.py
    python SkyyZones/test_skyyzones_0.3.3.py [--keep]
Phases (fresh child JVMs, tools/harness_kit.py: -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch; scratch tools/dev/scratch/zones033/zh):
  S   static   the patch re-runs to identical bytes; line endings kept; no new system / command; the ready line '[SkyyZones] 0.3.3 ready';
               the two Server Setup rows + config lines are in the jar
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.3.2 -> 0.3.3: no class added; exactly the members in EXPECT differ
  F2  fakes    the 0.2.0 harness's engine stand-ins
  X   exec     EVERY 0.3.1 + 0.3.2 check again on 0.3.3 (the 0.3.2 harness's run_exec: the 0.3.1 xrun + X032, unchanged code; the checks
               that changed BY DESIGN are listed in CHANGED / CHANGED33), then X033 with REAL UseBlockEvent$Pre events on the same stand-ins:
               gathering world, no region: chest + furnace open; rows off = LOCKED as 0.3.2; a town without the containers flag still
               locks (with it: opens); skyblock region keeps its flags; a safe zone = the world's rows; a non-gathering protected world +
               a player island / shard world listed in zones.gatherWorlds stay LOCKED; a world locked FULL by a bad region line stays
               LOCKED; zones:fn:check answers the same; /zones info shows Chests + Furnaces
  M   mig      Mig030 (the 0.3.1 harness's run_mig)      M2  mig2  Mig032 (the 0.3.2 harness's run_mig2) - both unchanged
  D   live     start twice on a scratch COPY of the live mods folder: Skyy's config.properties untouched or only the two new keys appended,
               start 2 changes nothing; Skyy's world skywynn_zones2 (no regions) now answers chests + furnaces 'allowed'
  AA  audit    engine-access audit
"""
import os, sys, importlib.util, zipfile, subprocess, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK
import skyybuild as B

VERSION, OLD = "0.3.3", "0.3.2"
PKG = "com.skyy.zones."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyZones-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyZones-%s.jar" % OLD)
GEN = os.path.join(HERE, "build_skyyzones_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyzones_%s.py" % OLD)
PATCH = os.path.join(ROOT, "tools", "zones_0_3_3_patch.py")
T32F = os.path.join(HERE, "test_skyyzones_0.3.2.py")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "zones033", "zh")))
LIVE = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods")
ADDED = []
EXPECT = {   # checked 2026-10-27 (the class compare 0.3.2 -> 0.3.3 of the first harness run; every member a planned change of tools/zones_0_3_3_patch.py:
 # CfgFile / CfgFn / CfgRows = the version + the 2 new rows; SkyyZonesPlugin setup / ZFn publish + unpublish / ZStore parseAll = the version text)
    'CfgFile': ['~<clinit>'],
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'SkyyZonesPlugin': ['~m setup'],
    'ZCfg': ['+f GCONT', '+f GFURN', '+m gatherOpen', '~<clinit>', '~m loadCfg'],
    'ZCmds': ['~m info'],
    'ZFn': ['~m publish', '~m unpublish'],
    'ZRules': ['~m decide'],
    'ZStore': ['~m parseAll'],
}
# the 0.3.1 / 0.3.2 checks whose expectation changed BY DESIGN in 0.3.3 (each re-checked the new way in X033)
CHANGED33 = {
}


def t32():
    spec = importlib.util.spec_from_file_location("zones_t32", T32F)
    m = importlib.util.module_from_spec(spec)
    a = list(sys.argv)
    spec.loader.exec_module(m)
    sys.argv[:] = a
    return m


T = t32()
M = T.M
T.EXTRA_BLOCKS = list(T.EXTRA_BLOCKS) + ["Bench_Furnace"]   # the engine stand-ins gain a processing bench (xns reads it at call time)
T.CHANGED.update(CHANGED33)


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, "rb").read()
    o = open(GEN_OLD, "rb").read()
    K.check(g.startswith(b'"""SkyyZones 0.3.3') and g.count(b'VERSION = "0.3.3"') == 1, "S header + VERSION")
    K.check(g.count(b"registerSystem(") == o.count(b"registerSystem(") and g.count(b"registerCommand(") == o.count(b"registerCommand("), "S no new system, no new command")
    K.check((b"\r\n" in g) == (b"\r\n" in o), "S line endings kept")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    src = open(PATCH, encoding="utf8").read().replace('os.path.join(ROOT, "SkyyZones", "build_skyyzones_0.3.3.py")', repr(os.path.join(d, "b.py")))
    open(os.path.join(d, "p.py"), "w", encoding="utf8").write(src.replace("ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))", "ROOT = %r" % ROOT))
    p = subprocess.run([sys.executable, os.path.join(d, "p.py")], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(os.path.join(d, "b.py"), "rb").read() == g, "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    with zipfile.ZipFile(jar) as z:
        pl = z.read("com/skyy/zones/SkyyZonesPlugin.class")
        allb = b"".join(z.read(n) for n in z.namelist() if n.endswith(".class"))
        names = z.namelist()
    with zipfile.ZipFile(OLD_JAR) as z:
        oldn = z.namelist()
    K.check(b"[SkyyZones] 0.3.3 ready - " in pl, "S the ready line '[SkyyZones] 0.3.3 ready' (smoke_test.py)")
    K.check(sorted(names) == sorted(oldn), "S the same jar entries as 0.3.2")
    K.check(b"gather.containers" in allb and b"gather.furnaces" in allb and b"Gathering world: chests open" in allb and b"Gathering world: furnaces open" in allb
            and b"gather.containers=true" in allb and b"gather.furnaces=true" in allb, "S the two Server Setup rows + default config lines are in the jar")
    K.save()


def X033(K, E, L):
    """0.3.3: chests / furnaces outside regions of a gathering world (L = xrun's locals)"""
    from jpype import JClass, JArray, JInt, JString, JBoolean
    P = lambda n: JClass(PKG + n)
    fire, Skyy, WORLD, notes, BT, U = L["fire"], L["Skyy"], M.WORLD, L["notes"], E["BT"], E["U"]
    Cfg, Sto, Rules, Fn = P("ZCfg"), P("ZStore"), P("ZRules"), P("ZFn")
    bt = lambda n: BT.getAssetMap().getAsset(n)
    ITY = JClass("com.hypixel.hytale.protocol.InteractionType")
    Bench = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.bench.Bench")
    BenchType = JClass("com.hypixel.hytale.protocol.BenchType")
    HM = JClass("java.util.HashMap")
    k0, f0 = K.ok, len(K.fails)

    def setf(cls, inst, name, v):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        f.set(inst, v)
    proc = U.allocateInstance(JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.bench.ProcessingBench").class_)
    setf(Bench, proc, "type", BenchType.Processing)
    setf(BT, bt("Bench_Furnace"), "bench", proc)
    im = HM()
    im.put(ITY.Use, "Open_Container")
    setf(BT, bt("Furniture_Crude_Chest"), "interactions", im)
    CON, FUR, ALLOW, LOCKED = int(Rules.CONTAINER), int(Rules.FURNACE), int(Rules.ALLOW), int(Rules.LOCKED)
    K.check(int(Rules.useAction(bt("Furniture_Crude_Chest"), ITY.Use, None)) == CON and int(Rules.useAction(bt("Bench_Furnace"), ITY.Use, None)) == FUR,
            "X033 the stand-ins: the chest counts as CONTAINER, the furnace as FURNACE")
    pw = lambda w: bool(Cfg.protectedWorld(w))
    dec = lambda w, x, y, z, a: int(Rules.decide(Sto.INDEX, w, pw(w), x, y, z, a, "Furniture_Crude_Chest"))
    K.check(bool(Cfg.gatherWorld(WORLD)) and pw(WORLD) and bool(Cfg.GCONT) and bool(Cfg.GFURN), "X033 the test world is a protected gathering world; both rows default ON")
    notes()
    x0, y0, z0 = 1500, 90, 1500
    K.check(Sto.INDEX.at(WORLD, x0, y0, z0).isEmpty(), "X033 no region at the test spot")
    c1 = fire(Skyy, "use", x0, y0, z0, block="Furniture_Crude_Chest")
    f1 = fire(Skyy, "use", x0, y0, z0, block="Bench_Furnace")
    K.check(not c1 and not f1 and notes() == [] and dec(WORLD, x0, y0, z0, CON) == ALLOW and dec(WORLD, x0, y0, z0, FUR) == ALLOW,
            "X033 Skyy's bug: gathering world, no region - a structure chest + a world furnace OPEN (no 'That is locked in this area.')")
    Cfg.GCONT = False
    c2 = fire(Skyy, "use", x0, y0, z0, block="Furniture_Crude_Chest")
    n2 = notes()
    f2 = fire(Skyy, "use", x0, y0, z0, block="Bench_Furnace")
    K.check(c2 and not f2 and n2 == [("Skyy", "That is locked in this area.")], "X033 gather.containers OFF: chests LOCKED as in 0.3.2, furnaces still open: %s" % n2)
    Cfg.GFURN = False
    K.check(fire(Skyy, "use", x0 + 3, y0, z0, block="Bench_Furnace") and dec(WORLD, x0, y0, z0, CON) == LOCKED and dec(WORLD, x0, y0, z0, FUR) == LOCKED,
            "X033 both rows OFF = exactly 0.3.2 (chest + furnace LOCKED)")
    Cfg.GCONT = True
    Cfg.GFURN = True
    notes()
    # regions keep their own flags
    Sto.create("town33", WORLD, "town", JArray(JInt)([1600, 60, 1600, 1620, 140, 1620]), "Skyy")
    Sto.create("tshop33", WORLD, "town", JArray(JInt)([1630, 60, 1600, 1640, 140, 1610]), "Skyy")
    Sto.set("tshop33", "flags", "containers", "Skyy")
    Sto.create("sky33", WORLD, "skyblock", JArray(JInt)([1650, 60, 1600, 1660, 140, 1610]), "Skyy")
    Sto.create("safe33", WORLD, "safe", JArray(JInt)([1670, 60, 1600, 1680, 140, 1610]), "Skyy")
    ct = fire(Skyy, "use", 1610, 90, 1610, block="Furniture_Crude_Chest")
    K.check(ct and notes() == [("Skyy", "That is locked in this area.")] and dec(WORLD, 1610, 90, 1610, FUR) == LOCKED,
            "X033 a TOWN without the containers flag still LOCKS its chests + furnaces")
    K.check(dec(WORLD, 1635, 90, 1605, CON) == ALLOW and dec(WORLD, 1635, 90, 1605, FUR) == LOCKED, "X033 a town with 'flags containers': chests open, furnaces locked")
    K.check(dec(WORLD, 1655, 90, 1605, CON) == LOCKED and dec(WORLD, 1655, 90, 1605, FUR) == LOCKED, "X033 a skyblock region keeps its own (empty) flags - locked")
    K.check(dec(WORLD, 1675, 90, 1605, CON) == ALLOW and dec(WORLD, 1675, 90, 1605, FUR) == ALLOW, "X033 a safe zone (not a protection layer): the world's rows - open")
    Cfg.GCONT = False
    K.check(dec(WORLD, 1675, 90, 1605, CON) == LOCKED and dec(WORLD, 1635, 90, 1605, CON) == ALLOW, "X033 ... row off: the safe zone locks, the flagged town still opens")
    Cfg.GCONT = True
    # other worlds: a protected non-gathering world, a player island / shard world in zones.gatherWorlds, a world locked FULL
    w0, g0 = str(Cfg.WORLDS), str(Cfg.GATHERW)
    Cfg.WORLDS = JString(w0 + ",prot33,skyy-island-abc,skyy-shard-abc")
    Cfg.GATHERW = JString(g0 + ",skyy-island-abc,skyy-shard-abc")
    K.check(dec("prot33", 5, 70, 5, CON) == LOCKED and dec("prot33", 5, 70, 5, FUR) == LOCKED, "X033 a protected world that is NOT a gathering world keeps the FULL default (locked)")
    K.check(not bool(Cfg.gatherWorld("skyy-island-abc")) and dec("skyy-island-abc", 5, 70, 5, CON) == LOCKED and dec("skyy-shard-abc", 5, 70, 5, CON) == LOCKED,
            "X033 player island / shard worlds are never gathering worlds - unaffected (even when listed)")
    K.check(dec("open33", 5, 70, 5, CON) == ALLOW and dec("skyy-island-xyz", 5, 70, 5, CON) == ALLOW, "X033 an unprotected world / an unlisted island: open as before")
    Cfg.WORLDS = JString(w0)
    Cfg.GATHERW = JString(g0)
    lk0 = Cfg.LOCKW
    hs = JClass("java.util.HashSet")()
    hs.add(WORLD.lower())
    Cfg.LOCKW = hs
    K.check(dec(WORLD, x0, y0, z0, CON) == LOCKED and dec(WORLD, x0, y0, z0, FUR) == LOCKED, "X033 a gathering world locked FULL by a broken region line (LOCKW): chests stay LOCKED (fail closed)")
    Cfg.LOCKW = lk0
    # the bridge answers the same
    chk = Fn(JInt(0))   # = zones:fn:check (ZFn.publish: CHECK = new ZFn(0))
    if True:
        O_ = lambda *a: JArray(JClass("java.lang.Object"))(list(a))
        K.check(str(chk.apply(O_(WORLD, JInt(x0), JInt(y0), JInt(z0), "container"))) == "allow" and str(chk.apply(O_(WORLD, JInt(x0), JInt(y0), JInt(z0), "furnace"))) == "allow"
                and str(chk.apply(O_(WORLD, JInt(1610), JInt(90), JInt(1610), "container"))) == "deny", "X033 zones:fn:check: container / furnace allow outside regions, deny in the town")
    for r_ in ("town33", "tshop33", "sky33", "safe33"):
        Sto.delete(r_, "Skyy")
    notes()
    K.notes.append("X033 ran: %d checks ok, %d failed" % (K.ok - k0, len(K.fails) - f0))


def _x32_and_33(K, E, L):
    X032_ORIG(K, E, L)
    X033(K, E, L)


X032_ORIG = T.X032
T.X032 = _x32_and_33


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Plug, CPub, Sto, Cfg, Rules = (JClass(PKG + n) for n in ("SkyyZonesPlugin", "CfgPub", "ZStore", "ZCfg", "ZRules"))
    Paths = JClass("java.nio.file.Paths")
    Sto.SYNC = True
    before = M.snap(home)
    sz = os.path.join(home, "Skyy_SkyyZones")
    rd = lambda f: open(os.path.join(sz, f), "rb").read().decode("latin-1") if os.path.isfile(os.path.join(sz, f)) else None
    oc = rd("config.properties")

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
    if diff2 == ["Skyy_SkyyZones/regen/skywynn_zones2.snap"] and snap1 and snap2:
        a_, b_ = set(snap1.splitlines()), set(snap2.splitlines())
        if not (b_ - a_) and all(l.startswith(("V ", "W ")) for l in a_ - b_):
            diff2 = []
    K.check(not diff2, "D start 2 changes nothing (%s)" % diff2)
    chz = sorted(f for f in set(s1) | set(before) if f.startswith("Skyy_SkyyZones/") and s1.get(f) != before.get(f))
    K.notes.append("D Skyy_SkyyZones changes: %s | %s | %s" % (chz, r1[:300], r2[:200]))
    nc = rd("config.properties")
    K.check(oc is None or nc == oc or (nc.startswith(oc) and set(l for l in nc[len(oc):].splitlines() if l.strip() and not l.startswith("#")) <= {"gather.containers=true", "gather.furnaces=true"}),
            "D Skyy's config.properties: untouched or only the two new keys appended (no line changed): %r" % (nc[len(oc):] if oc and nc and nc.startswith(oc) else "")[:200])
    # the regen journal / snapshot: a start folds a journal into the snapshot (0.3.2 does the same - a copy taken while the game runs has one)
    bad = [f for f in chz if not (f in ("Skyy_SkyyZones/config.properties", "Skyy_SkyyZones/regen/skywynn_zones2.snap", "Skyy_SkyyZones/regen/skywynn_zones2.journal",
                                        "Skyy_SkyyZones/config-changes.log")
                                  or f.startswith("Skyy_SkyyZones/config-history/"))]
    K.check(not bad, "D no other Skyy_SkyyZones file changes (no migration): %s" % bad)
    W = "skywynn_zones2"
    if bool(Cfg.gatherWorld(W)):
        at = Sto.INDEX.at(W, -4979, 70, 0)
        ix, pw = Sto.INDEX, bool(Cfg.protectedWorld(W))
        v = [int(Rules.decide(ix, W, pw, -4979, 70, 0, a, "Furniture_Crude_Chest")) for a in (Rules.CONTAINER, Rules.FURNACE)]
        K.check(at.isEmpty() and v == [int(Rules.ALLOW)] * 2 and bool(Cfg.GCONT) and bool(Cfg.GFURN),
                "D Skyy's zone world skywynn_zones2 (no region at x -4979): chests + furnaces now 'allowed' (0.3.2: locked): %s" % v)
    else:
        K.notes.append("D: the live copy has no gathering world skywynn_zones2 - Skyy's case not replayed")
    K.save()


if __name__ == "__main__":
    HK.run("SkyyZones", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("static", run_static), ("fakes", M.run_fakes), ("exec", T.run_exec), ("mig", M.run_mig), ("mig2", T.run_mig2), ("live", run_live)],
           __file__, live=(LIVE, "mods"))
