"""Harness for SkyyMobs 0.1.9 (mob:fn:setLevel - a level + plate name for a mob another mod spawns: SkyyIslands 0.5.12's camp skeletons and
Shardkeeper; tools/mobs_0_1_9_patch.py). Every 0.1.8 check (the kill credit + pet path, run from test_skyymobs_0.1.8.py's own code) + 0.1.9.
Build first: python tools/mobs_0_1_9_patch.py && python SkyyMobs/build_skyymobs_0.1.9.py

    python SkyyMobs/test_skyymobs_0.1.9.py [--keep] [--dir <scratch>]

Phases (fresh child JVMs, tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.1.8 -> 0.1.9: MobLevel (+ NAMEFIX, + nameFor, ~ apply, ~ forget), the plugin (setup / shutdown: the bridge key + the ready
              line), the version texts; added MobSetLevelFn; non-class: manifest only
  X  exec     every 0.1.8 exec check, then EXECUTED 0.1.9: mob:fn:setLevel refuses bad arguments (not an array, too short, no UUID, no
              number, level 0 / above levels.max), levels off, no Universe / world (FALSE, never throws); nameArg (trim, 40 chars, blank =
              none); nameFor (the given name wins, else the role name); forget drops the name on death / removal, keeps it on unload; the
              2000-name cap; the setup / shutdown code puts / removes mob:fn:setLevel
  D  live     the 0.1.8 live check (the live Skyy_SkyyMobs copy loads the same settings with 0.1.8 and 0.1.9, twice; bytes unchanged)
  AA engine-access audit
Scratch: tools/dev/scratch/isle2/mobs (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "isle2", "mobs")]
import skyybuild as B
import harness_kit as HK

# the 0.1.8 harness's own phase code (its file runs HK.run at the end - executed here without that last call)
_T18 = os.path.join(HERE, "test_skyymobs_0.1.8.py")
_src = open(_T18, encoding="utf-8").read()
_src = _src[:_src.rindex("HK.run(")]
T18 = {"__file__": _T18, "__name__": "test_skyymobs_0_1_8"}
exec(compile(_src, _T18, "exec"), T18)

VERSION = "0.1.9"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMobs-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMobs-0.1.8.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.mobs."
T18["OLD_JAR"] = OLD_JAR       # the 0.1.8 live phase compares the OLD jar with this one
EXPECT = {
    "MobLevel": ["+f NAMEFIX", "+m nameFor", "~<clinit>", "~m apply", "~m forget"],
    "SkyyMobsPlugin": ["~m setup", "~m shutdown"],
    "MobCfg": ["~m load", "~m reloadAll", "~m useDefaults"],
    "CfgFn": ["~m opExport"],
    "CfgRows": ["~<clinit>", "~m header"],
}
ADDED = ["MobSetLevelFn"]


def run_exec(out, jar, scratch, home):
    T18["run_exec"](out, jar, scratch, home)        # starts the JVM; every 0.1.8 exec check
    import json
    from jpype import JClass, JArray, JObject, JString, JInt
    K = HK.Child(out + ".019.json")
    Fn, Lv, Cfg = JClass(PKG + "MobSetLevelFn"), JClass(PKG + "MobLevel"), JClass(PKG + "MobCfg")
    UUID, Integer = JClass("java.util.UUID"), JClass("java.lang.Integer")
    f = Fn()
    u = UUID.fromString("00000000-0000-4000-8000-000000000519")
    A = lambda *xs: JArray(JObject)(list(xs))
    Cfg.ON = True
    Cfg.MAX_LEVEL = 100
    for what, arg in (("a String", JString("x")), ("null", None), ("too short", A(JString("w"), u)), ("no UUID", A(JString("w"), JString("u"), Integer(3))),
                      ("no number", A(JString("w"), u, JString("3"))), ("level 0", A(JString("w"), u, Integer(0))),
                      ("level above levels.max", A(JString("w"), u, Integer(101))), ("no world name", A(None, u, Integer(3)))):
        r_ = f.apply(arg)
        K.check(r_ is not None and not bool(r_), "SET refuses %s -> FALSE" % what)
    K.eq(int(Fn.levelArg(A(JString("w"), u, Integer(10), JString("Shardkeeper")))), 10, "SET levelArg: a good call -> 10")
    r_ = f.apply(A(JString("w"), u, Integer(10), JString("Shardkeeper")))
    K.check(r_ is not None and not bool(r_), "SET a good call with no Universe / world (bare JVM) -> FALSE, no throw")
    Cfg.ON = False
    K.eq(int(Fn.levelArg(A(JString("w"), u, Integer(3)))), 3, "SET levelArg does not look at the switch")
    r_ = f.apply(A(JString("w"), u, Integer(3)))
    K.check(r_ is not None and not bool(r_), "SET levels off (part.levels) -> FALSE")
    Cfg.ON = True
    K.eq(str(Fn.nameArg(A(JString("w"), u, Integer(3), JString("  Shardkeeper ")))), "Shardkeeper", "NAME trimmed")
    K.eq(len(str(Fn.nameArg(A(JString("w"), u, Integer(3), JString("x" * 60))))), 40, "NAME at most 40 characters")
    K.check(Fn.nameArg(A(JString("w"), u, Integer(3), JString("   "))) is None and Fn.nameArg(A(JString("w"), u, Integer(3))) is None
            and Fn.nameArg(A(JString("w"), u, Integer(3), Integer(5))) is None, "NAME blank / missing / not a String -> none")
    Lv.NAMEFIX.clear()
    base = str(Lv.nameFor(u, JString("Golem_Crystal_Earth"), None))
    K.eq(base, str(Lv.nameOf(JString("Golem_Crystal_Earth"), None)), "NAMEFOR no given name -> the role name (0.1.8 nameOf): %s" % base)
    Lv.NAMEFIX.put(u, JString("Shardkeeper"))
    K.eq(str(Lv.nameFor(u, JString("Golem_Crystal_Earth"), None)), "Shardkeeper", "NAMEFOR the given name wins")
    K.eq(str(Lv.nameFor(None, JString("Golem_Crystal_Earth"), None)), base, "NAMEFOR no UUID -> the role name")
    Lv.forget(u, True)
    K.check(str(Lv.NAMEFIX.get(u)) == "Shardkeeper", "FORGET an unload keeps the name (the mob comes back with its chunk)")
    Lv.forget(u, False)
    K.check(Lv.NAMEFIX.get(u) is None, "FORGET death / removal drops the name")
    pool = JClass("javassist.ClassPool")(True)
    pool.appendClassPath(jar)
    pool.appendClassPath(B.SERVER_JAR)
    IP, PS, BOS = JClass("javassist.bytecode.InstructionPrinter"), JClass("java.io.PrintStream"), JClass("java.io.ByteArrayOutputStream")

    def code(cn, mn):
        bos = BOS()
        for mm in pool.get(PKG + cn).getDeclaredMethods():
            if str(mm.getName()) == mn:
                IP(PS(bos)).print_(mm)
        return str(bos.toString())
    ap = code("MobSetLevelFn", "apply")
    K.check(0 <= ap.find("TickingThread.isInThread") < ap.find("getRefFromUUID") < ap.find("MobLevel.apply") and "NAMEFIX" in ap and '"set"' in ap,
            "SHAPE apply: world thread only -> the loaded entity -> MobLevel.apply (step set), the name kept in NAMEFIX")
    K.check(ap.find("2000") >= 0 or ap.find("sipush 2000") >= 0 or "2000" in ap, "SHAPE NAMEFIX is capped (2000)")
    K.check("MobLevel.nameFor" in code("MobLevel", "apply") and "MobLevel.nameOf" not in code("MobLevel", "apply"), "SHAPE MobLevel.apply puts nameFor on the plate")
    K.check("mob:fn:setLevel" in code("SkyyMobsPlugin", "setup") and "mob:fn:setLevel" in code("SkyyMobsPlugin", "shutdown"),
            "SHAPE setup puts mob:fn:setLevel on the bridge, shutdown removes it")
    K.save()
    d = json.load(open(out + ".019.json"))
    e = json.load(open(out))
    e["ok"] += d["ok"]
    e["fails"] += d["fails"]
    json.dump(e, open(out, "w"), indent=1)


HK.run("SkyyMobs", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("exec", run_exec), ("live", T18["run_live"])], __file__, live=(T18["LIVE_DIR"], "Skyy_SkyyMobs"))
