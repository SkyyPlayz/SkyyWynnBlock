"""Harness for SkyyPets 0.4.26 (the mount card's Summon button: the bridge pets:fn:ride; tools/pets_0_4_26_patch.py). Build first:
    python tools/pets_0_4_26_patch.py && python SkyyPets/build_skyypets_0.4.26.py
    python SkyyPets/test_skyypets_0.4.26.py [--keep] [--expect-dump] [--dir <folder inside tools/dev/scratch/>]

  S     static   the patch re-runs to identical bytes; ONE class added (PetRideFn), no system / command; the bridge put in setup + taken off at stop
                 (only ours); the jar: only PetRideFn added, changed non-class entries = manifest.json
  A/C/AA          (tools/harness_kit.py, -Xverify:all) verify, class compare 0.4.25 -> 0.4.26, engine-access audit
  RIDEFN EXECUTED on 0.4.25's stand-in world (real PetViews / PetRide / PetRideFn): no mount out -> the reason; the summon-slot dragon below the
                 ride level -> the level reason, nothing queued; at the ride level -> "+Mounting", ONE PetRideJob queued, it runs = you ride it (the
                 rider stand-in); a second press while mounting / riding -> "=" (no second job); a world without riding -> the reason; Pets off ->
                 the reason; not a UUID -> null; the button and F take the SAME door (PetRide.request)
  IDLE/AGG/REAL/MIG/ECS/RIDE/PT/RD/live/live2  every 0.4.25 phase again on the 0.4.26 jar
NOT COVERED (only the game can prove it): the client's mount animation from a button press (it is the F path's PetRideJob, unchanged).
Exit code 1 on any failure.
"""
import os, sys, zipfile, importlib.util, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "inv4", "pets")]
import skyybuild as B
import harness_kit as HK

_cmp0 = HK.run_compare
_eq00 = HK.Child.eq


def _mod(path, name):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    a = list(sys.argv)
    s.loader.exec_module(m)
    sys.argv[:] = a
    return m


T425 = _mod(os.path.join(HERE, "test_skyypets_0.4.25.py"), "test_skyypets_0_4_25")
HK.run_compare = _cmp0
HK.Child.eq = _eq00
T424, T423, T417 = T425.T424, T425.T423, T425.T417

VERSION = "0.4.26"
PKG = "com.skyy.pets."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyPets-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyPets-0.4.25.jar")
GEN = os.path.join(HERE, "build_skyypets_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyypets_0.4.25.py")
PATCH = os.path.join(TOOLS, "pets_0_4_26_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
T425.JAR = T424.JAR = T423.JAR = JAR
ADDED = ["PetRideFn"]
EXPECT = {   # the version text baked into the config kit + the migration log lines, as every version; setup / shutdown = the bridge
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'PetsCfg': ['~m applyAll', '~m seed'],
    'PetsMigDrg': ['~m run'], 'PetsMigP5': ['~m mgLog', '~m run'], 'PetsMigS2': ['~m run'], 'PetsMigW15': ['~m run'],
    'SkyyPetsPlugin': ['~m setup', '~m shutdown'],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}

# 0.4.25's MIG phase names its own version in the Changes line it expects: the same phase, with this version
import inspect as _insp
_src = _insp.getsource(T425.run_mig)
assert _src.count(r"\tSkyyPets 0.4.25\t") == 1, "0.4.25's MIG phase changed"
exec(compile(_src.replace(r"\tSkyyPets 0.4.25\t", r"\tSkyyPets 0.4.26\t"), T425.__file__, "exec"), T425.__dict__)


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyPets 0.4.26 - build script') and g.count('VERSION = "0.4.26"') == 1, "S header + VERSION")
    K.check(g.count("registerCommand(") == o.count("registerCommand(") and g.count("registerSystem(") == o.count("registerSystem("), "S no system or command added")
    K.eq(g.count("= cls(") - o.count("= cls("), 1, "S one class added (PetRideFn)")
    K.check(("\r\n" in g) == ("\r\n" in o), "S line endings kept")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, os.path.basename(GEN))
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-generates the script byte for byte: %s" % p.stderr[-300:])
    su = g[g.index("public void setup()"):]
    K.check('bridge().put("pets:fn:ride", new @PKG@.PetRideFn());' in su, "S setup publishes pets:fn:ride")
    K.check('if (rf instanceof @PKG@.PetRideFn) br.remove("pets:fn:ride", rf);' in g, "S shutdown takes pets:fn:ride off (only while it holds ours)")
    zn, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    nn, on = set(zn.namelist()), set(zo.namelist())
    K.eq(sorted(nn - on), ["com/skyy/pets/PetRideFn.class"], "S the jar adds only PetRideFn")
    K.eq(sorted(on - nn), [], "S the jar removes nothing")
    K.eq(sorted(n for n in nn & on if not n.endswith(".class") and zn.read(n) != zo.read(n)), ["manifest.json"], "S changed non-class entries = manifest.json")
    K.save()


def run_ridefn(out, jar, scratch, _home):
    W = T425._idle_world(out, jar, scratch, "ridefn")
    K, Cfg, Views, Rd, JClass, uo = W["K"], W["Cfg"], W["Views"], W["Rd"], W["JClass"], W["uo"]
    Fn = JClass(PKG + "PetRideFn")
    fn = Fn()
    K.check(fn.apply("x") is None and fn.apply(None) is None, "RIDEFN not a UUID -> null")
    other = W["UUID"].fromString("00000000-0000-0000-0000-000000009902")
    K.check(str(fn.apply(other)).startswith("-Your mount is not out"), "RIDEFN nobody's mount out -> the reason (%s)" % fn.apply(other))
    dv = T425._dv(W)
    K.check(dv is not None and not bool(dv.riding), "RIDEFN the summon-slot dragon is out")
    lv0 = int(Cfg.DRAGON_RIDE_LV) if hasattr(Cfg, "DRAGON_RIDE_LV") else None
    j0 = len(W["jobs"])
    asked0 = int(Rd.ASKED.get())
    r = str(fn.apply(uo))
    queued = len(W["jobs"]) - j0
    K.check(r.startswith("+Mounting your") and queued == 1 and int(Rd.ASKED.get()) == asked0 + 1, "RIDEFN Summon: '+Mounting', ONE ride job queued (%s, %d jobs)" % (r, queued))
    r2 = str(fn.apply(uo))
    K.check(r2.startswith("=") and len(W["jobs"]) - j0 == 1, "RIDEFN a second press while it gets ready: '=' and no second job (%s)" % r2)
    while W["jobs"]:
        W["jobs"].pop(0).run()
    W["second"]()
    K.check(bool(dv.riding) and int(W["rider"]["mid"]) != 0, "RIDEFN the queued job ran: you ride it (the same mountNow as F)")
    r3 = str(fn.apply(uo))
    K.check(r3.startswith("=You are already riding it"), "RIDEFN pressed while riding: '=' (%s)" % r3)
    # ride off, then a world without riding
    W["rider"]["mid"] = 0
    W["rider"]["mount"].clear()
    dv.riding = False
    dv.rideAt = 0
    blk = None
    for f_ in ("DRAGON_RIDE_BLOCKED",):
        if hasattr(Cfg, f_):
            blk = f_
    if blk is not None:
        old_ = getattr(Cfg, blk)
        setattr(Cfg, blk, str(dv.world) if str(dv.world) else "default")
        rb = str(fn.apply(uo))
        setattr(Cfg, blk, old_)
        K.check(rb.startswith("-") and "riding" in rb.lower(), "RIDEFN a world without riding -> the reason (%s)" % rb)
    else:
        K.notes.append("RIDEFN: no ride-blocked-worlds row found on PetsCfg - that refusal is PetRide.canRide's own (covered by 0.4.24's RIDE phase)")
    Cfg.ON = False
    ro = str(fn.apply(uo))
    Cfg.ON = True
    K.check(ro.startswith("-Pets are switched off"), "RIDEFN Pets off -> the reason (%s)" % ro)
    # below the ride level: the dragon level from its file
    rr = W["r"]
    pid = W["pid"]
    lvk = "pet." + pid + ".level"
    old_lv = rr.get(lvk)
    try:
        rr.set(lvk, "1")
        j1 = len(W["jobs"])
        rl = str(fn.apply(uo))
        K.check((rl.startswith("-Your dragon can carry you from Lv") or rl.startswith("-Your")) and len(W["jobs"]) == j1,
                "RIDEFN a Lv 1 dragon: the level reason, nothing queued (%s)" % rl)
    finally:
        rr.set(lvk, old_lv)
    K.check(int(Fn.CALLS.get()) >= 7, "RIDEFN every press counted (%d)" % int(Fn.CALLS.get()))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyPets", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("ridefn", run_ridefn), ("idle", T425.run_idle), ("agg", T425.run_agg), ("real", T425.run_real), ("mig", T425.run_mig),
                   ("ecs", T424.run_ecs), ("ride", T425._old(T424.run_ride)), ("pt", T425._old(T423.run_pt)), ("rd", T425._old(T423.run_rd)),
                   ("live", T417.run_live), ("live2", T425.run_live2)],
           script=__file__, live=(T423.T422.T421.T41.LIVE, "Skyy_SkyyPets"))
