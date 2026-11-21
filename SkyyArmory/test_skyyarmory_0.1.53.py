"""Harness for SkyyArmory 0.1.53 (small fixes round fix1: the boot pack check remembers a WARN read and tries again up to PACK_MAX 18 times
before logging it - SkyySkills' 0.4.46 / 0.4.70 rule; tools/armory_0_1_53_patch.py).
Build first:
    python tools/armory_0_1_53_patch.py && python SkyyArmory/build_skyyarmory_0.1.53.py
    python SkyyArmory/test_skyyarmory_0.1.53.py [--keep] [--expect-dump]
Phases (fresh child JVMs, tools/harness_kit.py: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  S    static   the patch re-runs to identical bytes, line endings kept; no new class / system / command, one new method; the jar vs 0.1.52:
                nothing added or removed, the only changed non-class entry = manifest.json (every item / interaction / animation byte-equal)
  X    exec     EXECUTED in the JVM (System.out captured - ArmoryLog prints there without the game's logger): ArmoryCheck.packStep on plain
                reads: PACK_MAX 18, MANA_MAX 6; warn reads are only remembered (nothing logged, not done) up to try 17; an info read after
                warns logs INFO once, ends the check, no WARN ever; 18 warn reads log the NEWEST warn once at try 18; unreadable reads to the
                end log the old "gave up after 18 tries" text; a warn then unreadable reads log the remembered warn; packStep after done
                changes nothing; start() clears PACK_PEND. The REAL run(): ArmoryCheck.start() + 18 x new ArmoryCheck(GEN).run() in a bare
                JVM (the asset maps unreadable) -> not done after 17, "gave up after 18 tries" after 18; manaSettled gives up after MANA_MAX 6
  X52  exec52   the 0.1.52 harness's exec phase on the 0.1.53 jar (the fist animation set decodes through the engine codec, as in 0.1.52)
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.1.52 -> 0.1.53: exactly the planned members (ArmoryCheck: + packStep, + PACK_PEND, + MANA_MAX, run / start - manaSettled reads the inlined 6 as before;
                the version text in the usual places)
  D    live     START TWICE on a scratch COPY of the live Skyy_SkyyArmory: 0.1.53 writes nothing; start 2 = start 1
  AA   audit    the engine-access audit
Not executed here (UNVERIFIED until the game): how long a live world's packs really take to load (18 x 10 s after the 20 s start = ~3 min).
"""
import os, sys, json, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "fix1", "arm")]
import skyybuild as B
import harness_kit as HK

VERSION, OLD = "0.1.53", "0.1.52"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyArmory-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyArmory-%s.jar" % OLD)
GEN = os.path.join(HERE, "build_skyyarmory_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyarmory_%s.py" % OLD)
PATCH = os.path.join(ROOT, "tools", "armory_0_1_53_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.armory."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyArmory")

_ORIG_COMPARE = HK.run_compare
_s = importlib.util.spec_from_file_location("test_skyyarmory_0_1_52", os.path.join(HERE, "test_skyyarmory_0.1.52.py"))
T52 = importlib.util.module_from_spec(_s)
_argv = list(sys.argv)
_s.loader.exec_module(T52)
sys.argv[:] = _argv
HK.run_compare = _ORIG_COMPARE          # the 0.1.52 harness swaps in its fist-set compare; 0.1.53 changes no asset (the kit's manifest-only check)
T52.JAR = JAR
T52.SCRATCH = SCRATCH

EXPECT = {
    # the version text (as every Armory round: SkyyArmoryPlugin / ArmoryCfg / CfgFn / CfgRows / CfgRows2 / ArmoryCheck packCheck + packOf)
    "SkyyArmoryPlugin": ["~m setup", "~m start"], "ArmoryCfg": ["~m load", "~m reloadAll", "~m useDefaults"],
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "CfgRows2": ["~<clinit>"],
    # 0.1.53: the pack check retry
    "ArmoryCheck": ["~m packCheck", "~m packOf", "+m packStep", "~m run", "~m start", "+f PACK_PEND", "+f MANA_MAX", "~<clinit>"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
MIGS = T52.MIGS


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyArmory 0.1.53 - build script') and g.count('VERSION = "0.1.53"') == 1 and 'VERSION = "0.1.52"' not in g, "S header + VERSION")
    K.eq((g.count("registerSystem(") - o.count("registerSystem("), g.count("registerCommand(") - o.count("registerCommand("), g.count("makeClass(") - o.count("makeClass("),
          g.count("\nM(") - o.count("\nM(")), (0, 0, 0, 1), "S no new system / command / class; one new method")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    K.eq((sorted(nb - na), sorted(na - nb)), ([], []), "S nothing added, nothing removed")
    nc = sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n))
    K.eq(nc, ["manifest.json"], "S changed non-class = manifest only (every item / interaction / animation / lang byte-identical)")
    ma, mb = json.loads(za.read("manifest.json")), json.loads(zb.read("manifest.json"))
    K.check(mb["Version"] == VERSION and dict(ma, Version=VERSION, Name=ma["Name"].replace(OLD, VERSION)) == mb, "S manifest: only the Version changed")
    K.save()


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JArray, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    Sys = JClass("java.lang.System")
    Sys.getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    BOS, PS = JClass("java.io.ByteArrayOutputStream"), JClass("java.io.PrintStream")
    out0 = Sys.out
    buf = BOS()
    Sys.setOut(PS(buf, True, "UTF-8"))
    C = JClass(PKG + "ArmoryCheck")
    JClass(PKG + "ArmoryLog").LOG = None

    def logged():
        s = str(buf.toString("UTF-8"))
        buf.reset()
        return [l for l in s.splitlines() if l.startswith("[SkyyArmory]")]

    def reset():
        C.STOP = True          # no scheduled run of an earlier start may act
        C.TRIES = 0
        C.PACK_DONE = False
        C.PACK_PEND = ""
        C.PACK_LAST = ""
        logged()

    def R(lvl, msg):
        return JArray(JString)([lvl, msg])

    try:
        K.eq((int(C.PACK_MAX), int(C.MANA_MAX), int(C.RETRY_S), int(C.START_S)), (18, 6, 10, 20), "X PACK_MAX 18, MANA_MAX 6, RETRY_S 10, START_S 20")
        # 1. warn reads are only remembered; an info read ends it with ONE INFO
        reset()
        lg = []
        for t in range(1, 6):
            C.TRIES = t
            done = bool(C.packStep(R("warn", "pack check: W%d; ANOTHER PACK WINS for 3: x (Hytale:Hytale)" % t)))
            K.check(not done and not bool(C.PACK_DONE), "X warn read %d: not done" % t)
            lg += logged()
        K.eq(lg, [], "X warn reads 1-5 log nothing")
        K.check(str(C.PACK_PEND).startswith("pack check: W5;") and str(C.PACK_LAST) == "", "X the newest warn is remembered (PACK_PEND), PACK_LAST still empty")
        C.TRIES = 6
        K.check(bool(C.packStep(R("info", "pack check: OK; live read-back OK"))) and bool(C.PACK_DONE), "X an info read after warns ends the check")
        lg = logged()
        K.eq(lg, ["[SkyyArmory] pack check: OK; live read-back OK"], "X exactly ONE INFO line, no WARN")
        K.check(str(C.PACK_LAST) == "pack check: OK; live read-back OK" and str(C.PACK_PEND) == "", "X PACK_LAST = the info text, PACK_PEND cleared")
        C.TRIES = 7
        K.check(bool(C.packStep(R("warn", "late warn"))) and logged() == [] and str(C.PACK_LAST) == "pack check: OK; live read-back OK",
                "X packStep after done changes nothing, logs nothing")
        # 2. 18 warn reads: the NEWEST warn logged once at try 18
        reset()
        for t in range(1, 19):
            C.TRIES = t
            done = bool(C.packStep(R("warn", "pack check: W%d; NOT LOADED: y" % t)))
            if t < 18:
                K.check(not done, "X 18 warns: try %d not done" % t) if t in (1, 17) else None
        lg = logged()
        K.eq(lg, ["[SkyyArmory] WARN pack check: W18; NOT LOADED: y"], "X 18 warn reads -> the newest warn logged ONCE at try 18 (WARN level)")
        K.check(bool(C.PACK_DONE) and str(C.PACK_LAST) == "pack check: W18; NOT LOADED: y", "X done, PACK_LAST = that warn")
        # 3. unreadable to the end: the old give-up text
        reset()
        for t in range(1, 19):
            C.TRIES = t
            C.packStep(R("", "the game's asset maps are not readable yet"))
        lg = logged()
        K.eq(lg, ["[SkyyArmory] WARN pack check gave up after 18 tries: the game's asset maps are not readable yet"], "X unreadable x18 -> the old give-up WARN, once")
        # 4. a warn, then unreadable reads: the remembered warn is logged at the end
        reset()
        C.TRIES = 1
        C.packStep(R("warn", "pack check: early warn"))
        for t in range(2, 19):
            C.TRIES = t
            C.packStep(R("", "the game's assets could not be read"))
        K.eq(logged(), ["[SkyyArmory] WARN pack check: early warn"], "X warn then unreadable x17 -> the remembered warn, once")
        # 5. junk reads never throw
        reset()
        C.TRIES = 1
        K.check(not bool(C.packStep(None)) and not bool(C.packStep(JArray(JString)(["warn"]))) and logged() == [], "X null / short reads: no throw, nothing logged")
        C.TRIES = 18
        K.check(bool(C.packStep(None)) and logged() == ["[SkyyArmory] WARN pack check gave up after 18 tries: no answer"], "X a null read at try 18 gives up cleanly")
        # 6. start() clears PACK_PEND (its schedule may fail in a bare JVM - it is caught)
        C.PACK_PEND = "stale"
        C.start()
        C.STOP = True
        K.check(str(C.PACK_PEND) == "" and not bool(C.PACK_DONE) and int(C.TRIES) == 0, "X start() clears PACK_PEND / PACK_DONE / TRIES")
        logged()
        # 7. the REAL run(): a bare JVM cannot read the asset maps -> 17 runs not done, the 18th gives up with the old text
        C.start()
        g = int(C.GEN)
        C.STOP = False
        lg = []
        for t in range(1, 19):
            C(g).run()
            if t == 17:
                K.check(not bool(C.PACK_DONE) and int(C.TRIES) == 17, "X run() x17: still trying (TRIES %d)" % int(C.TRIES))
            lg += logged()
        C.STOP = True
        K.check(bool(C.PACK_DONE) and int(C.TRIES) == 18 and str(C.PACK_LAST).startswith("pack check gave up after 18 tries: "),
                "X run() x18: gave up after 18 tries: %s" % C.PACK_LAST)
        gu = [l for l in lg if "pack check gave up" in l]
        K.check(len(gu) == 1, "X the give-up WARN logged once by run(): %s" % gu)
        K.notes.append("X run() logged: %s" % [l[:160] for l in lg][:6])
        # 8. manaSettled keeps the old 6 tries (MANA_MAX)
        Cfg = JClass(PKG + "ArmoryCfg")
        on0 = bool(Cfg.CHECK_ON)
        Cfg.CHECK_ON = True
        C.MANA_LVL = "skip"
        C.MANA_TRIES = 0
        r = [bool(C.manaSettled()) for _ in range(6)]
        K.eq(r, [False] * 5 + [True], "X manaSettled (SkyySkills not readable) gives up at try 6 = MANA_MAX (unchanged)")
        Cfg.CHECK_ON = on0
    finally:
        Sys.setOut(out0)
    K.save()
    sys.stdout.flush()
    os._exit(0)


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    JClass(PKG + "ArmoryLog").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyArmory")
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Cfg = JClass(PKG + "ArmoryCfg")
    Paths = JClass("java.nio.file.Paths")
    Cfg.DIR = Paths.get(home)
    Cfg.FILE = Paths.get(home).resolve("config.properties")
    fp = os.path.join(home, "config.properties")
    b0 = open(fp, "rb").read()
    hashes = [HK.tree_hash(home)]
    for start in (1, 2):
        rs = [str(getattr(Cfg, m)()) for m in MIGS]
        Cfg.load()
        hashes.append(HK.tree_hash(home))
        if start == 1:
            K.notes.append("D start 1 migrations: %s" % [x[:120] for x in rs if x])
    K.check(hashes[1] == hashes[2], "D start 2 changes nothing")
    K.check(hashes[0] == hashes[1], "D start 1 changes nothing either (0.1.53 has no row / migration)")
    t1 = open(fp, "rb").read()
    K.check(b"0.1.53" not in t1 and (b"\r\n" in b0) == (b"\r\n" in t1), "D 0.1.53 writes nothing of its own; line endings kept")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyArmory", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("static", run_static), ("exec", run_exec), ("exec52", T52.run_exec), ("live", run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyArmory"))
