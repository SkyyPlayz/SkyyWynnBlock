"""Harness for SkyySacks 0.8.27 (the Normal bag quality text #fefefe instead of #ffffff - The Armory's ScribingModule owns #ffffff;
tools/sacks_0_8_27_patch.py). Built from the 0.8.26 pin (0.8.25's off-hand refill is parked and NOT in it). Build first:
    python tools/sacks_0_8_27_patch.py && python SkyySacks/build_skyysacks_0.8.27.py

    python SkyySacks/test_skyysacks_0.8.27.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.8.26 -> 0.8.27: no class member differs except the version texts; non-class files: manifest.json + Skyy_Bag_Normal.json
  QUAL  the shipped quality assets: Skyy_Bag_Normal TextColor #fefefe, every other field of it and every other quality byte-identical to
        0.8.26, no quality draws in #ffffff; the Java tables (SackDefs.RAR_COLOR / RAR_PAGE) unchanged
  D     START TWICE on a scratch COPY of NewBetaTest's Skyy_SkyySacks: the setup chain (SackMig089 -> 0824 -> 0826 + SackCfg.reload) twice -
        neither start changes a byte (the live file already holds the 0.8.26 marker); then 0.8.10's run_live10 (pools + config read twice)
  AA    engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import skyyonce_harness as OH

_argv = list(sys.argv)
_sp = importlib.util.spec_from_file_location("test_skyysacks_0_8_26", os.path.join(HERE, "test_skyysacks_0.8.26.py"))
T0826 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T0826)
sys.argv = _argv
T0810 = T0826.T0810

VERSION = "0.8.27"
OLD_VERSION = "0.8.26"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySacks-%s.jar" % OLD_VERSION)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "lean1022", "sacks")))
PKG = "com.skyy.sacks."
BETA = T0826.BETA
NORMAL = "Server/Item/Qualities/Skyy_Bag_Normal.json"
HK.run_compare = OH.compare_allowing(lambda n: n == NORMAL)
EXPECT = {"CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "SkyySacksPlugin": ["~m setup"]}   # the version texts (config kit + ready line)
if "--expect-dump" in sys.argv:
    EXPECT = {}


def run_qual(out, jar, scratch, _home):
    K = HK.Child(out)
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    qa = dict((n, za.read(n)) for n in za.namelist() if n.startswith("Server/Item/Qualities/"))
    qb = dict((n, zb.read(n)) for n in zb.namelist() if n.startswith("Server/Item/Qualities/"))
    K.eq(sorted(qb), sorted(qa), "QUAL: the same %d quality assets" % len(qa))
    a, b = json.loads(qa[NORMAL]), json.loads(qb[NORMAL])
    K.eq((a["TextColor"], b["TextColor"]), ("#ffffff", "#fefefe"), "QUAL: Skyy_Bag_Normal TextColor #ffffff -> #fefefe")
    a.pop("TextColor")
    b.pop("TextColor")
    K.eq(b, a, "QUAL: every other field of Skyy_Bag_Normal unchanged")
    K.check(all(qa[n] == qb[n] for n in qa if n != NORMAL), "QUAL: the other qualities byte-identical (%s)" % ", ".join(
        "%s %s" % (n.rsplit("/", 1)[1][:-5], json.loads(qb[n])["TextColor"]) for n in sorted(qb) if n != NORMAL))
    K.check(not [n for n in qb if json.loads(qb[n])["TextColor"].lower() == "#ffffff"], "QUAL: no quality draws its text in #ffffff")
    import jpype
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    D = jpype.JClass(PKG + "SackDefs")
    K.eq([str(x) for x in D.RAR_COLOR], ["#ffffff", "#ffff55", "#ff55ff", "#55ffff", "#cc66cc"], "QUAL: SackDefs.RAR_COLOR (the rarity table) unchanged")
    K.eq([str(x) for x in D.RAR_PAGE], ["#ffffff", "#ffff55", "#ff55ff", "#55ffff", "#cc66cc"], "QUAL: SackDefs.RAR_PAGE (page colours) unchanged")
    K.save()


def run_live27(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    Paths = JClass("java.nio.file.Paths")
    Pool, Cfg, PB = JClass(PKG + "SackPool"), JClass(PKG + "SackCfg"), JClass(PKG + "ProcBench")
    M89, M24, M26 = JClass(PKG + "SackMig089"), JClass(PKG + "SackMig0824"), JClass(PKG + "SackMig0826")
    Pool.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySacks")
    f = os.path.join(home, "config.properties")

    def snap():
        d = {}
        for root, _ds, fs in os.walk(home):
            for n in fs:
                p = os.path.join(root, n)
                d[os.path.relpath(p, home)] = open(p, "rb").read()
        return d
    s0 = snap()
    K.check(T0826.MK in s0["config.properties"].decode("latin-1"), "D: (the live file already holds the 0.8.26 marker)")
    for s in (1, 2):
        got = (str(M89.run(Paths.get(f))), str(M24.run(Paths.get(f))), str(M26.run(Paths.get(f))))
        Cfg.FILE = Paths.get(f)
        Cfg.MTIME = -1
        Cfg.reload()
        K.eq(got, ("", "", ""), "D start %d: no migration does anything" % s)
        K.check(int(PB.QUEUE_CAP) == 1000 and int(PB.FURNACE_PCT) == 25, "D start %d: the config reads (queue 1000, Furnace 25 %%)" % s)
        K.check(snap() == s0, "D start %d: no byte changed in the live copy (%d files)" % (s, len(s0)))
    K.save()


if __name__ == "__main__":
    HK.run("SkyySacks", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, [],
           [("qual", run_qual), ("live", run_live27), ("live2", T0810.run_live10)],
           __file__, live=(BETA, "Skyy_SkyySacks"))
