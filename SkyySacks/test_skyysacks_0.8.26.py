"""Harness for SkyySacks 0.8.26 (Balance P6 part A: the Furnace 4x faster + a 1,000-unit queue; tools/sacks_0_8_26_patch.py). Built from
the 0.8.24 pin (0.8.25's off-hand refill is parked and NOT in 0.8.26). Build first:
    python tools/sacks_0_8_26_patch.py && python SkyySacks/build_skyysacks_0.8.26.py

    python SkyySacks/test_skyysacks_0.8.26.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.8.24 -> 0.8.26: exactly the planned members (EXPECT) + the new class SackMig0826; no 0.8.25 member (utilCounts / offFill)
  FUR   the real ProcBench.unitMs on real CraftingRecipe objects: Copper bar 10 s -> 2.5 s in the Furnace, the Tannery unchanged (10 s), the
        Furnace Charm 50 % on top (charmMs -> 1.25 s), Thorium 18 s -> 4.5 s and a 1,000-unit Thorium queue = 1.25 h (ProcBench.addJob +
        the queue's own time sum), the row live (FURNACE_PCT 100 = vanilla, 50 = half, 0 / 500 clamped to 1 / 100); the bench tier
        reduction still applies first
  QUE   the queue cap: QUEUE_CAP defaults to 1000; a ProcStore bench with 1,000 queued units refuses one more through the real procQueue
        ("queue is full (1000 units)", nothing taken), 999 queued leave room
  CFG   SackCfg.reload on scratch files: bench.furnacePct read / clamped / missing = 25; bench.queueCap missing = 1000; the kit's console path
        (Server Setup) sets FURNACE_PCT live + the file line
  MIG   the real SackMig089 -> SackMig0824 -> SackMig0826 (what setup runs) on scratch files: the NewBetaTest file (CRLF, "#bench.queueCap=256"
        commented): only that comment refreshed + the 0.8.26 marker appended (CRLF), Properties identical, History = old bytes; a live
        bench.queueCap=256 line -> 1000 (change-log line), a hand edit kept + named, a doubled line kept, start 2 changes nothing, a fresh
        file carries the marker + #bench.queueCap=1000 + #bench.furnacePct=25; History blocked = untouched (next start updates)
  D     START TWICE on a scratch COPY of NewBetaTest's Skyy_SkyySacks: the setup chain (3 migrations + reload) twice - start 1 changes only
        comment lines + the marker, start 2 nothing; every processing file reads (queues with their stored unit times kept); then 0.8.10's
        run_live10 (pools + config read twice, no byte changed)
  AA    engine-access audit
Not testable without the game (UNVERIFIED): the Furnace page times in game; jobs queued before the update finish at their stored (old) speed.
Exit code 1 on any failure.
"""
import os, sys, shutil, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

_orig_compare = HK.run_compare
_argv = list(sys.argv)
_sp = importlib.util.spec_from_file_location("test_skyysacks_0_8_10", os.path.join(HERE, "test_skyysacks_0.8.10.py"))
T0810 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T0810)
sys.argv = _argv
HK.run_compare = _orig_compare

VERSION = "0.8.26"
OLD_VERSION = "0.8.24"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySacks-%s.jar" % OLD_VERSION)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "balp6a", "sacks")))
PKG = "com.skyy.sacks."
BETA = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyySacks")
EXPECT = {
    "ProcBench": ["+f FURNACE_PCT", "~m unitMs", "~<clinit>"],
    "SackCfg": ["~m reload"],
    "RecipeCmp": ["~<clinit>"],   # the /craft sort table is baked from tools/tier_tags.py at build time (tools/tier_tags.py gained rows after the 0.8.24 build - data only)
    "SkyySacksPlugin": ["~m setup"],
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header", "~<clinit>"], "CfgFile": ["~<clinit>"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = ["SackMig0826"]
MK = "skyysacks-0.8.26-bench"


def _recipe(J, rid, out_, ins, bench, secs):
    CRc = J("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
    MQ = J("com.hypixel.hytale.server.core.inventory.MaterialQuantity")
    BR = J("com.hypixel.hytale.protocol.BenchRequirement")
    from jpype import JArray, JString, JInt, JFloat
    b_ = BR()
    b_.id = JString(bench)
    b_.requiredTierLevel = 0
    mi = JArray(MQ)([MQ(JString(i), None, None, JInt(1), None) for i in ins])
    po = MQ(JString(out_), None, None, JInt(1), None)
    r = CRc(mi, po, JArray(MQ)([po]), JInt(1), JArray(BR)([b_]), JFloat(secs), False, JInt(0))
    f = CRc.class_.getDeclaredField("id")
    f.setAccessible(True)
    f.set(r, JString(rid))
    return r


# ======================================================================================================== FUR / QUE
def run_fur(out, jar, scratch, home):
    from jpype import JClass, JString, JLong
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    PB, PS, Pool, CP = JClass(PKG + "ProcBench"), JClass(PKG + "ProcStore"), JClass(PKG + "SackPool"), JClass(PKG + "CraftPage")
    Pool.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySacks")
    cu = _recipe(JClass, "Ingredient_Bar_Copper_Recipe_Generated_0", "Ingredient_Bar_Copper", ["Ore_Copper"], "Furnace", 10.0)
    th = _recipe(JClass, "Ingredient_Bar_Thorium_Recipe_Generated_0", "Ingredient_Bar_Thorium", ["Ore_Thorium"], "Furnace", 18.0)
    le = _recipe(JClass, "Ingredient_Leather_Light_Recipe_Generated_0", "Ingredient_Leather_Light", ["Ingredient_Hide_Light"], "Tannery", 10.0)
    K.eq(int(PB.FURNACE_PCT), 25, "FUR bench.furnacePct defaults to 25")
    K.eq(int(PB.QUEUE_CAP), 1000, "QUE bench.queueCap defaults to 1000 (was 256)")
    K.eq(int(PB.unitMs(cu, JString("Furnace"), 0)), 2500, "FUR a Copper bar (vanilla 10 s) takes 2.5 s in the Furnace")
    K.eq(int(PB.unitMs(cu, JString("furnace"), 0)), 2500, "FUR the bench name in any case")
    K.eq(int(PB.unitMs(le, JString("Tannery"), 0)), 10000, "FUR the Tannery is untouched (10 s)")
    K.eq(int(PB.charmMs(JLong(PB.unitMs(cu, JString("Furnace"), 0)), 50)), 1250, "FUR the Furnace Charm 50 % cuts the 2.5 s to 1.25 s (on top)")
    K.eq(int(PB.unitMs(th, JString("Furnace"), 0)), 4500, "FUR a Thorium bar (18 s) takes 4.5 s")
    for pct, want in ((100, 10000), (50, 5000), (0, 100), (500, 10000), (1, 100)):
        PB.FURNACE_PCT = pct
        K.eq(int(PB.unitMs(cu, JString("Furnace"), 0)), want, "FUR FURNACE_PCT %d -> a Copper bar %d ms (live; clamped 1..100)" % (pct, want))
    PB.FURNACE_PCT = 25
    # the bench tier reduction still first (vanilla's own config; none in a bare JVM = 0) -> the order is reduction, pct, charm
    red = float(PB.reduction(JString("Furnace"), 3))
    K.eq(int(PB.unitMs(cu, JString("Furnace"), 3)), int(round((10.0 - 10.0 * red) * 0.25 * 1000)), "FUR bench tier reduction (%.2f here) then x 0.25" % red)
    # a 1,000-unit Thorium queue = 1.25 h (the queue's own time sum, no charm)
    d = os.path.join(scratch, "fur", "processing")
    os.makedirs(d, exist_ok=True)
    PS.DIR = JClass("java.nio.file.Paths").get(d)
    k = "00000000-0000-0000-0000-0000000f0826"
    pb = PS.of(JString(k), JString("Furnace"))
    now = int(JClass("java.lang.System").currentTimeMillis())
    pb.addJob(JString("Ingredient_Bar_Thorium_Recipe_Generated_0"), 1000, JLong(PB.unitMs(th, JString("Furnace"), 0)), JString("Ore_Thorium*1"), JLong(now))
    K.eq(int(pb.queued()), 1000, "QUE 1,000 Thorium units fit in one queue")
    tot = 0
    for i in range(pb.queue.size()):
        j = pb.queue.get(i)
        tot += int(PB.charmMs(JLong(j.unitMs), 0)) * int(j.count)
    K.eq(tot, 4500000, "FUR the 1,000 Thorium bars take 1.25 h (4,500,000 ms; was 5 h at vanilla speed)")
    r = str(CP.procQueue(None, None, None, JString(k), JString("Furnace"), 0, cu, 1))
    K.check("queue is full (1000 units)" in r, "QUE one more unit is refused by the real procQueue: %s" % r)
    j0 = pb.queue.get(0)
    j0.count = 999
    K.eq(int(pb.queued()), 999, "QUE 999 queued")
    try:
        r2 = str(CP.procQueue(None, None, None, JString(k), JString("Furnace"), 0, cu, 1))
    except Exception as e:
        r2 = "threw %s" % e
    K.check("queue is full" not in r2, "QUE with 999 queued the cap check passes (it then needs a real player: %s)" % r2[:80])
    K.save()


# ======================================================================================================== CFG
def run_cfg(out, jar, scratch, home):
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    Paths = JClass("java.nio.file.Paths")
    Cfg, PB, Pool = JClass(PKG + "SackCfg"), JClass(PKG + "ProcBench"), JClass(PKG + "SackPool")
    Pool.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySacks")
    base = os.path.join(scratch, "cfg", "mods", "Skyy_SkyySacks")
    os.makedirs(base)
    f = os.path.join(base, "config.properties")

    def reload_with(text):
        if text is None:
            if os.path.exists(f):
                os.remove(f)
        else:
            open(f, "wb").write(text.encode("latin-1"))
        Cfg.FILE = Paths.get(f)
        Cfg.MTIME = -1
        Cfg.reload()
        return int(PB.FURNACE_PCT), int(PB.QUEUE_CAP)
    K.eq(reload_with("craftSearch=true\nbench.furnacePct=40\n"), (40, 1000), "CFG bench.furnacePct=40 read; no queueCap line = 1000")
    K.eq(reload_with("bench.furnacePct=0\nbench.queueCap=256\n"), (1, 256), "CFG furnacePct 0 clamped to 1; a kept queueCap=256 line is read")
    K.eq(reload_with("bench.furnacePct=900\n"), (100, 1000), "CFG furnacePct 900 clamped to 100")
    K.eq(reload_with("bench.furnacePct=abc\n"), (25, 1000), "CFG junk = the default 25")
    K.eq(reload_with(None), (25, 1000), "CFG no file: the default file is written, 25 / 1000")
    t = open(f, "rb").read().decode("latin-1")
    K.check("#bench.furnacePct=25" in t and "#bench.queueCap=1000" in t and MK in t, "CFG the default file holds #bench.furnacePct=25, #bench.queueCap=1000 and the 0.8.26 marker")
    CP, Fn = JClass(PKG + "CfgPub"), JClass(PKG + "CfgFn")
    CP.start(Paths.get(os.path.dirname(base)), Pool.LOG)
    r = str(Fn.cmdSetConsole(JString("bench.furnacePct"), JString("50")))
    r2 = str(Fn.cmdSetConsole(JString("bench.furnacePct"), JString("101")))
    CP.shutdown()
    t2 = open(f, "rb").read().decode("latin-1")
    K.check(int(PB.FURNACE_PCT) == 50 and "bench.furnacePct=50" in t2, "CFG Server Setup sets the Furnace time live + the file line: %s" % r)
    K.check(int(PB.FURNACE_PCT) == 50, "CFG 101 %% is refused by the row bounds (still 50): %s" % r2)
    K.save()


# ======================================================================================================== MIG
def run_mig(out, jar, scratch, home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    from jpype import JClass, JString
    Paths = JClass("java.nio.file.Paths")
    Pool, Cfg, PB = JClass(PKG + "SackPool"), JClass(PKG + "SackCfg"), JClass(PKG + "ProcBench")
    M89, M24, Mig = JClass(PKG + "SackMig089"), JClass(PKG + "SackMig0824"), JClass(PKG + "SackMig0826")
    Pool.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySacks")
    base = os.path.join(scratch, "mig")
    nfile = [0]

    def world(text_bytes):
        nfile[0] += 1
        d = os.path.join(base, "w%d" % nfile[0], "mods", "Skyy_SkyySacks")
        os.makedirs(d)
        f = os.path.join(d, "config.properties")
        if text_bytes is not None:
            open(f, "wb").write(text_bytes)
        return d, f

    def start(f):
        """what setup() runs: SackMig089, SackMig0824, SackMig0826"""
        return str(M89.run(Paths.get(f))), str(M24.run(Paths.get(f))), str(Mig.run(Paths.get(f)))

    def props(b):
        P_ = JClass("java.util.Properties")()
        P_.load(JClass("java.io.ByteArrayInputStream")(b))
        return dict((str(k), str(P_.getProperty(k))) for k in P_.stringPropertyNames())

    def hist(d):
        hd = os.path.join(d, "config-history")
        return sorted(os.path.join(hd, n) for n in os.listdir(hd) if "config.properties." in n and n.endswith(".bak")) if os.path.isdir(hd) else []

    def chlog(d):
        f = os.path.join(d, "config-changes.log")
        return [l.split("\t") for l in open(f, encoding="utf8").read().splitlines()] if os.path.isfile(f) else []

    # ---- the NewBetaTest file (CRLF; both older markers; "#bench.queueCap=256" commented)
    bcfg = os.path.join(BETA, "config.properties")
    if os.path.isfile(bcfg):
        b0 = open(bcfg, "rb").read()
        d, f = world(b0)
        r = start(f)
        b1 = open(f, "rb").read()
        l0, l1 = b0.split(b"\r\n"), b1.split(b"\r\n")
        diff = [(a, c) for a, c in zip(l0[:-1], l1) if a != c]
        K.check(r[0] == "" and r[1] == "" and diff == [(b"#bench.queueCap=256", b"#bench.queueCap=1000")],
                "MIG beta: 0.8.9 / 0.8.24 do nothing (markers); only the commented queue line gets the new default: %s" % diff[:3])
        K.check(len(l1) == len(l0) + 1 and l1[-2].startswith(b"# ---------- SkyySacks 0.8.26 (marker " + MK.encode()) and l1[-1] == b""
                and b1.count(b"\n") == b1.count(b"\r\n"), "MIG beta: the 0.8.26 marker line appended with the file's CRLF ending")
        K.check(props(b0) == props(b1), "MIG beta: the Properties are identical (only a comment changed)")
        h = hist(d)
        K.check(len(h) == 1 and open(h[0], "rb").read() == b0, "MIG beta: config-history holds the old bytes")
        K.check(chlog(d) == [] and "no setting line held the old default" in r[2] and "1 commented default line(s) refreshed" in r[2],
                "MIG beta: no change-log line; INFO: %s" % r[2][:200])
        K.check(start(f) == ("", "", "") and open(f, "rb").read() == b1 and len(hist(d)) == 1, "MIG beta: start 2 changes nothing (markers)")
    else:
        K.check(False, "MIG: no NewBetaTest config.properties to test on")
    # ---- synthetic LF file: a live 256 line moves, the doubled / hand-edited cases are kept
    d, f = world(b"# skyysacks-0.8.9-void\n# skyysacks-0.8.24-void\ncraftSearch=true\nbench.queueCap = 256\r\nbench.fuelCap=1000\nbench.outputCap=20000")
    r = start(f)
    t1 = open(f, "rb").read().decode("latin-1")
    K.check(t1.startswith("# skyysacks-0.8.9-void\n# skyysacks-0.8.24-void\ncraftSearch=true\nbench.queueCap = 1000\r\nbench.fuelCap=1000\nbench.outputCap=20000\n# ---------- SkyySacks 0.8.26")
            and t1.count("\r\n") == 1, "MIG syn: the spaced live line moved (its CRLF kept), final newline added, marker appended: %r" % t1[:200])
    cl = chlog(d)
    K.check([(x[1], x[3], x[4], x[5], x[6], x[7]) for x in cl] == [("SkyySacks 0.8.26", "update", "bench.queueCap", "256", "1000", "ok")],
            "MIG syn: one change-log line: %s" % [x[1:8] for x in cl])
    K.check(len(hist(d)) == 1, "MIG syn: one History copy")
    Cfg.FILE = Paths.get(f)
    Cfg.MTIME = -1
    Cfg.reload()
    K.eq(int(PB.QUEUE_CAP), 1000, "MIG syn: SackCfg.reload reads the moved 1000")
    K.check(start(f) == ("", "", "") and open(f, "rb").read().decode("latin-1") == t1, "MIG syn: start 2 changes nothing")
    d, f = world(b"# skyysacks-0.8.9-void\n# skyysacks-0.8.24-void\nbench.queueCap=300\n")
    r = start(f)
    t2 = open(f, "rb").read().decode("latin-1")
    K.check("bench.queueCap=300\n" in t2 and MK in t2 and chlog(d) == [] and "bench.queueCap=300 kept - an admin changed it" in r[2],
            "MIG hand edit 300 kept + named: %s" % r[2].replace("\n", " | ")[:200])
    d, f = world(b"# skyysacks-0.8.9-void\n# skyysacks-0.8.24-void\nbench.queueCap=256\nbench.queueCap=256\n")
    r = start(f)
    K.check(open(f, "rb").read().decode("latin-1").startswith("# skyysacks-0.8.9-void\n# skyysacks-0.8.24-void\nbench.queueCap=256\nbench.queueCap=256\n")
            and "doubled" in r[2], "MIG a doubled line is kept + named: %s" % r[2].replace("\n", " | ")[:200])
    # ---- Undo through the kit, then start again
    d, f = world(b"# skyysacks-0.8.9-void\n# skyysacks-0.8.24-void\nbench.queueCap=256\n")
    start(f)
    CP, Fn = JClass(PKG + "CfgPub"), JClass(PKG + "CfgFn")
    CP.start(Paths.get(os.path.dirname(d)), Pool.LOG)
    ru = str(Fn.cmdSetConsole(JString("bench.queueCap"), JString("256")))
    CP.shutdown()
    t3 = open(f, "rb").read().decode("latin-1")
    K.check("bench.queueCap=256" in t3 and int(PB.QUEUE_CAP) == 256, "MIG undo: the kit sets 256 back: %s" % ru)
    K.check(start(f) == ("", "", "") and open(f, "rb").read().decode("latin-1") == t3, "MIG undo: the next start keeps the undone value (marker)")
    # ---- fresh: no file -> reload writes the default (all three markers)
    d, f = world(None)
    K.check(start(f) == ("", "", "") and not os.path.exists(f), "MIG fresh: no file -> nothing done")
    Cfg.FILE = Paths.get(f)
    Cfg.MTIME = -1
    Cfg.reload()
    t4 = open(f, "rb").read()
    K.check(MK.encode() in t4 and b"skyysacks-0.8.24-void" in t4 and b"#bench.queueCap=1000" in t4 and b"#bench.furnacePct=25" in t4,
            "MIG fresh: the default file carries the markers, #bench.queueCap=1000 and #bench.furnacePct=25")
    K.check(start(f) == ("", "", "") and open(f, "rb").read() == t4 and hist(d) == [], "MIG fresh: the updates find the markers - nothing written")
    # ---- History cannot be written: untouched; the next start updates it
    d, f = world(b"# skyysacks-0.8.9-void\n# skyysacks-0.8.24-void\nbench.queueCap=256\n")
    open(os.path.join(d, "config-history"), "wb").write(b"not a folder")
    b0 = open(f, "rb").read()
    K.check(start(f)[2] == "" and open(f, "rb").read() == b0, "MIG nohist: config-history cannot be made -> the file is untouched")
    os.remove(os.path.join(d, "config-history"))
    K.check(start(f)[2] != "" and b"bench.queueCap=1000" in open(f, "rb").read(), "MIG nohist: the next start updates it")
    K.save()


# ======================================================================================================== D (start twice on the live copy)
def run_live26(out, jar, scratch, home):
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    Paths = JClass("java.nio.file.Paths")
    Pool, Cfg, PB, PS = JClass(PKG + "SackPool"), JClass(PKG + "SackCfg"), JClass(PKG + "ProcBench"), JClass(PKG + "ProcStore")
    M89, M24, Mig = JClass(PKG + "SackMig089"), JClass(PKG + "SackMig0824"), JClass(PKG + "SackMig0826")
    Pool.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySacks")
    f = os.path.join(home, "config.properties")
    snap = {}
    for root, _ds, fs in os.walk(home):
        for n in fs:
            p = os.path.join(root, n)
            snap[os.path.relpath(p, home)] = open(p, "rb").read()
    outs = []
    for s in (1, 2):
        outs.append((str(M89.run(Paths.get(f))), str(M24.run(Paths.get(f))), str(Mig.run(Paths.get(f)))))
        Cfg.FILE = Paths.get(f)
        Cfg.MTIME = -1
        Cfg.reload()
        K.check(int(PB.QUEUE_CAP) == 1000 and int(PB.FURNACE_PCT) == 25, "D start %d: queue 1000, Furnace 25 %%" % s)
    K.check(outs[1] == ("", "", ""), "D start 2: no migration does anything")
    changed = []
    for root, _ds, fs in os.walk(home):
        for n in fs:
            p = os.path.join(root, n)
            rel = os.path.relpath(p, home)
            if snap.get(rel) != open(p, "rb").read():
                changed.append(rel)
    K.check(all(c == "config.properties" or c.startswith("config-history") or c == "config-changes.log" for c in changed),
            "D: only config.properties (+ its History copy) changed: %s" % changed)
    a, b = snap["config.properties"].decode("latin-1"), open(f, "rb").read().decode("latin-1")
    da = [l for l in b.splitlines() if l not in a.splitlines()]
    K.check(all(l.startswith("#") for l in da) and any(MK in l for l in da), "D: the changed lines are comments only (refresh + marker): %s" % da)
    # every processing file reads; queues keep their stored unit times
    pdir = os.path.join(home, "processing")
    PS.DIR = Paths.get(pdir)
    n = 0
    for fn in sorted(os.listdir(pdir)) if os.path.isdir(pdir) else []:
        if not fn.endswith(".properties"):
            continue
        k = fn[:-11]
        txt = open(os.path.join(pdir, fn), encoding="latin-1").read()
        want = sum(int(l.split("=", 1)[1]) for l in txt.splitlines() if l.startswith("Furnace.q.") and l.split("=")[0].endswith(".count"))
        ums = sorted(set(int(l.split("=", 1)[1]) for l in txt.splitlines() if l.startswith("Furnace.q.") and ".unitMs=" in l))
        pb = PS.get(JString(k), JString("Furnace"))
        got = int(pb.queued()) if pb is not None else -1
        gums = sorted(set(int(pb.queue.get(i).unitMs) for i in range(pb.queue.size()))) if pb is not None else []
        K.check(got == want and gums == ums, "D processing %s: the Furnace queue reads (%d units, unit times %s kept)" % (k[:12], got, gums))
        n += 1
    K.check(n > 0, "D: the live copy has processing files (%d)" % n)
    K.save()


if __name__ == "__main__":
    HK.run("SkyySacks", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("fur", run_fur), ("cfg", run_cfg), ("mig", run_mig), ("live", run_live26), ("live2", T0810.run_live10)],
           __file__, live=(BETA, "Skyy_SkyySacks"))
