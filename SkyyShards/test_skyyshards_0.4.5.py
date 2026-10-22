"""Harness for SkyyShards 0.4.5 (Balance P7 economy P7b: the 14 shard upgrade coin costs = 1 h of the matching zone's income; the P6 idle share
kept (Skyy "20-100%, 3 days"); ShMig045; tools/shards_0_4_5_patch.py). Build first:
    python tools/shards_0_4_5_patch.py && python SkyyShards/build_skyyshards_0.4.5.py
    python SkyyShards/test_skyyshards_0.4.5.py [--keep]

  S    static   the patch re-runs to identical bytes; one class added (ShMig045); setup order migCoop, ShMig044, ShMig045, loadCfg, CfgPub.start
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.4.4 -> 0.4.5: + ShMig045; exactly the planned members differ (EXPECT)
  K    costs    EXECUTED ShCfg.loadCfg (fresh file + a bare file): storage II-V 43,500 / 305,000 / 1,085,000 / 3,880,000 (storeCoins), compactor
                43,500 / 1,085,000, compressor 43,500 / 305,000 / 1,085,000, grow 8,300 / 43,500, bench II-IV 43,500 / 305,000 / 1,085,000 =
                tools/balance_model.py's zone hours; the Server Setup rows' defaults; the idle share UNCHANGED (totem speeds, caps, idle XP,
                storage stacks, shard.maxOfflineSec 259200 = the 0.4.4 jar's own values, read in its own class loader)
  M    mig      ShMig045 on scratch files: the NewBetaTest config (read only, copied): the 14 lines move 0.4.4 -> 0.4.5, the marker appended in
                the file's own ending, Properties differ only there, History = the old bytes, 14 change-log lines; loadCfg reads them; start 2
                nothing; hand edits / a doubled line / a spaced "5000.0" kept or moved by value; Undo through the kit; a fresh file = nothing;
                History blocked = untouched, the next start updates
  D    live     START TWICE on a scratch COPY of NewBetaTest's Skyy_SkyyShards: migCoop, ShMig044, ShMig045, loadCfg twice; then 0.4's run_live
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import balance_model as BM

VERSION = "0.4.5"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "balp7b", "shards")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyShards-%s.jar" % VERSION)]
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyShards-0.4.4.jar")
GEN = os.path.join(HERE, "build_skyyshards_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyshards_0.4.4.py")
PATCH = os.path.join(ROOT, "tools", "shards_0_4_5_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.shards."
_argv = list(sys.argv)
_spec = importlib.util.spec_from_file_location("test_skyyshards_0_4_4", os.path.join(HERE, "test_skyyshards_0.4.4.py"))
T44 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T44)
sys.argv[:] = _argv
T42, T04, LIVE_SH = T44.T42, T44.T04, T44.LIVE_SH
ZH = [BM.p7_round(BM.p7_target_h(z)) for z in range(1, 6)]
Z1, Z2, Z3, Z4, Z5 = ZH
MIG = ([("storage.coins.%d" % t, o, n) for t, o, n in ((2, 5000, Z2), (3, 25000, Z3), (4, 100000, Z4), (5, 400000, Z5))] +
       [("compactor.coins1", 50000, Z2), ("compactor.coins2", 250000, Z4)] +
       [("compressor.coins%d" % i, o, n) for i, o, n in ((1, 25000, Z2), (2, 100000, Z3), (3, 400000, Z4))] +
       [("grow.medium.coins", 5000, Z1), ("grow.large.coins", 20000, Z2)] +
       [("bench.up%d.coins" % i, o, n) for i, o, n in ((2, 25000, Z2), (3, 100000, Z3), (4, 400000, Z4))])
KEYS = [k for k, o, n in MIG]
MK = "skyyshards-0.4.5-p7"
IDLE = ("RATES", "WMAXS", "XPWS", "ST1", "ST2", "ST3", "ST4", "ST5")


def costs(Cfg):
    return ([int(Cfg.SC2), int(Cfg.SC3), int(Cfg.SC4), int(Cfg.SC5)], [int(x) for x in Cfg.CMP_COINS][1:], [int(x) for x in Cfg.TC_COINS][1:],
            [int(Cfg.GM_COINS), int(Cfg.GL_COINS)], [int(x) for x in Cfg.BENCH_COINS][2:])


WANT = ([Z2, Z3, Z4, Z5], [Z2, Z4], [Z2, Z3, Z4], [Z1, Z2], [Z2, Z3, Z4])


def idle(Cfg):
    o = {}
    for f in IDLE:
        v = getattr(Cfg, f)
        o[f] = [round(float(x), 6) for x in v] if hasattr(v, "__len__") else int(v)
    return o


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyShards 0.4.5 - build script') and g.count('VERSION = "0.4.5"\n') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.check("ALLC = [cfg, smig, smig45, st," in g, "S ShMig045 written out")
    HK.jvm([B.SERVER_JAR, JAR, B.JAVASSIST], verify=False)
    calls = T42.setup_calls(jar)
    K.check(calls.index("ShCfg.migCoop") < calls.index("ShMig044.run") < calls.index("ShMig045.run") < calls.index("ShCfg.loadCfg") < calls.index("CfgPub.start"),
            "S setup order: migCoop, ShMig044, ShMig045, loadCfg, CfgPub.start")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def _old_idle():
    from jpype import JClass, JArray
    arr = JArray(JClass("java.net.URL"))(2)
    arr[0] = JClass("java.io.File")(OLD_JAR).toURI().toURL()
    arr[1] = JClass("java.io.File")(B.SERVER_JAR).toURI().toURL()
    ld = JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getPlatformClassLoader())
    return idle(JClass(PKG + "ShCfg", loader=ld))


def run_costs(out, jar, scratch, _home):
    from jpype import JClass
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    K = HK.Child(out)
    K.eq(ZH, [8300, 43500, 305000, 1085000, 3880000], "K the zone hours (balance_model p7_target_h, p7_round)")
    oi = _old_idle()
    home = os.path.join(scratch, "k1", "mods", "Skyy_SkyyShards")
    os.makedirs(home)
    Cfg, path = T42.kit_home(home)
    Cfg.loadCfg(True)
    K.eq(costs(Cfg), WANT, "K a fresh file: storage / compactor / compressor / grow / bench coins = 1 h of the zone")
    K.eq([int(Cfg.storeCoins(t)) for t in (2, 3, 4, 5)], WANT[0], "K storeCoins(tier) = what a storage purchase charges")
    t = open(os.path.join(home, "config.properties"), "rb").read()
    K.check(MK.encode() in t and all(("\n%s=%d\n" % (k, n)).encode() in t.replace(b"\r\n", b"\n") for k, o, n in MIG), "K the fresh file holds the 14 new lines + the marker")
    K.eq(idle(Cfg), oi, "K the idle share is the 0.4.4 one (totem speeds, caps, idle XP, storage stacks: Skyy '20-100%, 3 days')")
    K.check("\nshard.maxOfflineSec=259200\n" in t.replace(b"\r\n", b"\n").decode("latin-1"), "K shard.maxOfflineSec stays 259200 (3 days)")
    home2 = os.path.join(scratch, "k2", "mods", "Skyy_SkyyShards")
    os.makedirs(home2)
    open(os.path.join(home2, "config.properties"), "w").write("shard.enabled=true\n")
    Cfg, path = T42.kit_home(home2)
    Cfg.loadCfg(True)
    K.eq(costs(Cfg), WANT, "K a file without the lines reads the new code defaults")
    rows = dict((str(r[0]), [str(x) for x in list(r)]) for r in JClass(PKG + "CfgRows").header()[7])
    K.eq([rows[k][4] for k in KEYS], [str(n) for k, o, n in MIG], "K the 14 Server Setup rows' defaults")
    K.save()


def run_mig(out, jar, scratch, _home):
    from jpype import JClass, JString
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    K = HK.Child(out)
    Mig = JClass(PKG + "ShMig045")
    nf = [0]

    def world(b_):
        nf[0] += 1
        home = os.path.join(scratch, "m%d" % nf[0], "mods", "Skyy_SkyyShards")
        os.makedirs(home)
        Cfg, path = T42.kit_home(home)
        f = os.path.join(home, "config.properties")
        if b_ is not None:
            open(f, "wb").write(b_)
        return home, f, Cfg, path

    def hist(home):
        hd = os.path.join(home, "config-history")
        return [open(os.path.join(hd, n), "rb").read() for n in sorted(os.listdir(hd)) if n.endswith(".bak")] if os.path.isdir(hd) else []

    def chg(home):
        f = os.path.join(home, "config-changes.log")
        return [l.split("\t") for l in open(f, encoding="utf8").read().splitlines()] if os.path.isfile(f) else []

    def props(b_):
        P_ = JClass("java.util.Properties")()
        P_.load(JClass("java.io.ByteArrayInputStream")(b_))
        return dict((str(k), str(P_.getProperty(k))) for k in P_.stringPropertyNames())
    live = os.path.join(LIVE_SH, "config.properties")
    A_ = open(live, "rb").read() if os.path.isfile(live) else None
    K.check(A_ is not None, "M the live NewBetaTest config.properties exists (read only)")
    if A_ is not None:
        home, f, Cfg, path = world(A_)
        r = str(Mig.run(path(f)))
        b1 = open(f, "rb").read()
        nl = b"\r\n" if b"\r\n" in A_ else b"\n"
        pa, pb = props(A_), props(b1)
        K.check(sorted(k for k in pb if pa.get(k) != pb.get(k)) == sorted(KEYS) and all(pb[k] == str(n) for k, o, n in MIG) and len(pa) == len(pb),
                "M live: exactly the 14 cost lines moved to the 0.4.5 defaults: %s" % [(k, pa.get(k), pb.get(k)) for k in KEYS if pb.get(k) != str(dict((a, c) for a, b, c in MIG)[k])])
        K.check(b1.endswith(("# ---------- SkyyShards 0.4.5 (marker %s" % MK).encode() + b1.split(MK.encode())[1].split(nl)[0] + nl), "M live: the marker line appended in the file's own ending")
        K.check(hist(home) == [A_], "M live: config-history holds the old bytes")
        cl = chg(home)
        K.check(sorted((x[4], x[5], x[6]) for x in cl) == sorted((k, str(o), str(n)) for k, o, n in MIG) and all(x[1] == "SkyyShards 0.4.5" and x[7] == "ok" for x in cl),
                "M live: one change-log line per moved value (14): %s" % [x[4:7] for x in cl][:4])
        Cfg.loadCfg(False)
        K.eq(costs(Cfg), WANT, "M live: loadCfg reads the moved costs")
        K.check(str(Mig.run(path(f))) == "" and open(f, "rb").read() == b1 and len(hist(home)) == 1, "M live: start 2 changes nothing (marker)")
        K.check("storage.coins.2 5000 -> 43500" in r and "runs once" in r, "M live: the INFO line names the changes: %s" % r[:160])
    syn = b"# head\nstorage.coins.2=5000.0\nstorage.coins.3=99\ncompactor.coins1=50000\ncompactor.coins1=50000\ngrow.medium.coins = 5000\r\nbench.up4.coins=400000\nx=1"
    home, f, Cfg, path = world(syn)
    r = str(Mig.run(path(f)))
    t = open(f, "rb").read().decode("latin-1")
    K.check(t.startswith("# head\nstorage.coins.2=43500\nstorage.coins.3=99\ncompactor.coins1=50000\ncompactor.coins1=50000\ngrow.medium.coins = 8300\r\nbench.up4.coins=1085000\nx=1\n# ---------- SkyyShards 0.4.5"),
            "M syn: 5000.0 moved by value, the admin's 99 and the doubled compactor line kept, the spaced grow line (its CRLF) moved: %r" % t[:260])
    K.check("storage.coins.3=99 kept - an admin changed it" in r and "compactor.coins1=50000 kept - the line is doubled" in r, "M syn: the kept lines are named: %s" % r.replace("\n", " | ")[:300])
    K.eq(len(chg(home)), 3, "M syn: 3 change-log lines")
    CP, Fn = JClass(PKG + "CfgPub"), JClass(PKG + "CfgFn")
    CP.start(path(os.path.dirname(home)), JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyShards"))
    ru = str(Fn.cmdSetConsole(JString("storage.coins.2"), JString("5000")))
    CP.shutdown()
    t2 = open(f, "rb").read().decode("latin-1")
    K.check("storage.coins.2=5000" in t2.splitlines() and int(Cfg.SC2) == 5000, "M undo: the kit sets storage.coins.2 back to 5000: %s" % ru)
    K.check(str(Mig.run(path(f))) == "" and open(f, "rb").read().decode("latin-1") == t2, "M undo: the next start keeps the undone value (marker)")
    home, f, Cfg, path = world(None)
    K.check(str(Mig.run(path(f))) == "" and not os.path.exists(f), "M fresh: no file -> nothing done")
    Cfg.loadCfg(True)
    t3 = open(f, "rb").read()
    K.check(str(Mig.run(path(f))) == "" and open(f, "rb").read() == t3 and hist(home) == [], "M fresh: the default file carries the marker - nothing written")
    home, f, Cfg, path = world(b"storage.coins.2=5000\n")
    open(os.path.join(home, "config-history"), "wb").write(b"not a folder")
    K.check(str(Mig.run(path(f))) == "" and open(f, "rb").read() == b"storage.coins.2=5000\n", "M nohist: config-history cannot be made -> the file is untouched")
    os.remove(os.path.join(home, "config-history"))
    T42.kit_home(home)
    K.check(str(Mig.run(path(f))) != "" and b"storage.coins.2=43500" in open(f, "rb").read(), "M nohist: the next start updates it")
    K.save()


def run_live45(out, jar, scratch, home):
    from jpype import JClass
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    K = HK.Child(out)
    Cfg, path = T42.kit_home(home)
    M4, M5 = JClass(PKG + "ShMig044"), JClass(PKG + "ShMig045")
    t0 = T42.tree(home)
    rs = []
    for s in (1, 2):
        T42.kit_home(home)
        rs.append((str(Cfg.migCoop(Cfg.FILE)), str(M4.run(Cfg.FILE)), str(M5.run(Cfg.FILE))))
        r = str(Cfg.loadCfg(True))
        K.check(not r.startswith("default"), "D start %d: the live config is read" % s)
        K.eq(costs(Cfg), WANT, "D start %d: the 0.4.5 costs" % s)
    t1 = T42.tree(home)
    ch = sorted(k for k in set(t0) | set(t1) if t0.get(k) != t1.get(k))
    K.check(all(k == "config.properties" or k.startswith("config-history/") or k == "config-changes.log" for k in ch) and "config.properties" in ch,
            "D start 1 changed only config.properties (+ History, change log): %s" % ch)
    K.check(rs[1] == ("", "", ""), "D start 2: no update ran")
    K.save()


EXPECT = {   # checked by hand 2026-10-22: the 14 code defaults + the default text (ShCfg clinit / loadCfg / writeDefaults), the version texts
            # (CfgFn, CfgRows, ShStore's file header in save / migrate), setup's ShMig045 call
    "ShCfg": ["~<clinit>", "~m loadCfg", "~m writeDefaults"], "ShStore": ["~m migrate", "~m save"], "SkyyShardsPlugin": ["~m setup"],
    "CfgRows": ["~<clinit>", "~m header"], "CfgFn": ["~m opExport"]}

if __name__ == "__main__":
    HK.run(name="SkyyShards", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=["ShMig045"],
           phases=[("static", run_static), ("costs", run_costs), ("mig", run_mig), ("live", run_live45), ("live2", T04.run_live)],
           script=__file__, live=(LIVE_SH, "mods/Skyy_SkyyShards"))
