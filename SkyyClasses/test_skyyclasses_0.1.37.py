"""Harness for SkyyClasses 0.1.37 (lean round clsk: Breach + Mark stack fully; tools/classes_0_1_37_patch.py). Build first:
    python tools/classes_0_1_37_patch.py && python SkyyClasses/build_skyyclasses_0.1.37.py
    python SkyyClasses/test_skyyclasses_0.1.37.py [--keep]
Phases (tools/harness_kit.py, fresh child JVMs, -Xverify:all, TEMP / TMP in tools/dev/scratch/clsk/cls):
  A   verify   every class loads + initialises
  C   compare  0.1.36 -> 0.1.37: exactly the planned members (EXPECT); non-class entries = manifest.json only
  X   exec     on the engine stand-ins of test_skyyclasses_0.1.25.py (its N0 set-up):
               X1 Abil.outMult: Mark alone, Breach alone, both = (1 + Mark/100) x (1 + Breach/100); expired ones count nothing
               X2 the numbers: no AbilNum.EL_BREACHMARK, the default Element text has no breachMark key, an old text WITH breachMark=5 is
                  read without error (its other keys still apply)
  ST1 / ST2  START TWICE on a scratch COPY of the live Skyy_SkyyClasses folder (setup's order): nothing written; the live folder only read
  AA  engine-access audit
"""
import os, sys, json, shutil, zipfile, textwrap, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import deploy_set as DS

VERSION, OLD = "0.1.37", "0.1.36"
JAR = os.path.join(HERE, "SkyyClasses-%s.jar" % VERSION)
OLD_JAR = os.path.join(HERE, "SkyyClasses-%s.jar" % OLD)
PKG = "com.skyy.classes."
SCRATCH = os.path.join(TOOLS, "dev", "scratch", "clsk", "cls")
LIVE = os.path.join(B.HYTALE, "UserData", "Saves", DS.WORLD, "mods", "Skyy_SkyyClasses")
T25 = os.path.join(HERE, "test_skyyclasses_0.1.25.py")
ADDED = []
EXPECT = {
    "Abil": ["~m outMult"],                                    # Breach + Mark: both, multiplied
    "AbilNum": ["-f EL_BREACHMARK", "~<clinit>", "~m sync"],   # the "+5" number row is gone
    "AbilCfg": ["~<clinit>", "~m read"],                       # the ab.Elements.numbers default text
    "CfgRows2": ["~<clinit>"], "ClassCfg": ["~<clinit>"],      # ... the same text in the row table + the default file
    "SkyyClassesPlugin": ["~m setup"],                         # the version text
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "KitMigrate": ["~m runOnce"],   # the version text
}


def run_exec(out, jar, scratch, _home):
    stats_zip = os.path.join(scratch, "stats.zip")
    with zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")) as zi, \
            zipfile.ZipFile(stats_zip, "w") as zo:
        for n in zi.namelist():
            if n.startswith("Server/Entity/Stats/") and n.endswith(".json"):
                zo.writestr(n, zi.read(n))
    lines = open(T25, encoding="utf8").read().split("\n")
    a = lines.index("def run_exec(out, jar, scratch, _home):") + 1
    b = [i for i, l in enumerate(lines) if l.strip() == "# ---------------- X1 the pure rules"][0]
    ns = {"out": out, "jar": jar, "scratch": scratch, "_home": _home, "HK": HK, "B": B, "PKG": PKG, "ASSETS": stats_zip, "os": os, "sys": sys,
          "json": json, "shutil": shutil, "zipfile": zipfile, "time": time, "__name__": "t25setup"}
    exec(compile(textwrap.dedent("\n".join(lines[a:b])), T25 + " (N0 set-up)", "exec"), ns)
    g = lambda n: ns[n]
    K, C, ck = g("K"), g("C"), g("ck")
    from jpype import JArray, JDouble
    A, AS, AC = g("A"), g("AS"), g("AC")
    tst, mu, npc, now_ms = g("tst"), g("mu"), g("npc"), g("now_ms")
    AN = C("AbilNum")
    t1, t2 = npc(401, 20.5, 64.0, 0.5), npc(402, 22.5, 64.0, 0.5)
    uh, ul = float(mu.getMostSignificantBits()), float(mu.getLeastSignificantBits())

    def mark(t, pct, secs=6.0):
        AS.MARKD.put(t, JArray(JDouble)([float(now_ms() + int(secs * 1000)), pct, 1.0]))

    def breach(t, pct, secs=8.0):
        AS.BREACH.put(t, JArray(JDouble)([float(now_ms() + int(secs * 1000)), pct, uh, ul, 0.0]))

    def om(t):
        return float(A.outMult(tst, t, mu, now_ms()))

    # ---------------- X1 Breach + Mark stack fully (Skyy 2026-10-17)
    AS.MARKD.clear()
    AS.BREACH.clear()
    ck(abs(om(t1) - 1.0) < 1e-9, "X1: neither = x1.0")
    mark(t1, 15.0)
    ck(abs(om(t1) - 1.15) < 1e-9, "X1: Mark 15 alone = x1.15 (as 0.1.36): %s" % om(t1))
    AS.MARKD.clear()
    breach(t1, 19.0)
    ck(abs(om(t1) - 1.19) < 1e-9, "X1: Breach 19 alone = x1.19 (as 0.1.36): %s" % om(t1))
    mark(t1, 15.0)
    ck(abs(om(t1) - 1.15 * 1.19) < 1e-9, "X1: Breach 19 + Mark 15 = x1.15 x 1.19 = x1.3685 (0.1.36: the higher + 5 = x1.24): %s" % om(t1))
    breach(t1, 15.0)
    ck(abs(om(t1) - 1.3225) < 1e-9, "X1: Breach 15 + Mark 15 = x1.3225: %s" % om(t1))
    breach(t2, 30.0)
    mark(t2, 25.0)
    ck(abs(om(t2) - 1.3 * 1.25) < 1e-9, "X1: the caps Breach 30 + Mark 25 = x1.625: %s" % om(t2))
    AS.MARKD.put(t2, JArray(JDouble)([float(now_ms() - 10), 25.0, 1.0]))
    ck(abs(om(t2) - 1.3) < 1e-9, "X1: an expired Mark counts nothing (Breach 30 still on): %s" % om(t2))
    AS.BREACH.put(t2, JArray(JDouble)([float(now_ms() - 10), 30.0, uh, ul, 0.0]))
    ck(abs(om(t2) - 1.0) < 1e-9, "X1: both expired = x1.0: %s" % om(t2))
    ck(abs(om(t1) - 1.3225) < 1e-9, "X1: the other target is untouched: %s" % om(t1))
    ck(abs(float(A.outMult(tst, t1, None, now_ms())) - 1.3225) < 1e-9, "X1: from anyone (no caster uuid) too")
    AS.MARKD.clear()
    AS.BREACH.clear()

    # ---------------- X2 the numbers
    names = [str(f.getName()) for f in AN.class_.getDeclaredFields()]
    ck("EL_BREACHMARK" not in names and "EL_BOTHBONUS" in names, "X2: AbilNum has no EL_BREACHMARK (EL_BOTHBONUS kept)")
    dflt = str(AC.EL_NUMS)
    ck("breachMark" not in dflt and "bothBonus=10" in dflt and "bossCc=50" in dflt, "X2: the default ab.Elements.numbers text: %s" % dflt)
    old = dflt.replace("bossCc=50", "bossCc=40,breachMark=5")
    AC.EL_NUMS = old
    AN.sync()
    ck(abs(float(AN.EL_BOSSCC) - 40.0) < 1e-9 and abs(float(AN.EL_BOTHBONUS) - 10.0) < 1e-9,
       "X2: an old text WITH breachMark=5 is read fine (its other keys apply, bossCc 40)")
    AC.EL_NUMS = dflt
    AN.sync()
    ck(abs(float(AN.EL_BOSSCC) - 50.0) < 1e-9, "X2: back to the default")
    breach(t1, 15.0)
    mark(t1, 15.0)
    AC.EL_NUMS = old
    AN.sync()
    ck(abs(om(t1) - 1.3225) < 1e-9, "X2: an old breachMark=5 in the file adds nothing: %s" % om(t1))
    AC.EL_NUMS = dflt
    AN.sync()
    K.save()


def run_st(out, jar, scratch, step):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Cfg, Pub, AS = JClass(PKG + "ClassCfg"), JClass(PKG + "CfgPub"), JClass(PKG + "AbilStore")
    Paths = JClass("java.nio.file.Paths")
    home = os.path.join(scratch, "st", "mods")
    base = os.path.join(home, "Skyy_SkyyClasses")
    if step == "1":
        shutil.rmtree(os.path.join(scratch, "st"), ignore_errors=True)
        shutil.copytree(LIVE, base)
        json.dump(HK.tree_hash(LIVE), open(os.path.join(scratch, "st-live.json"), "w"))
    before = HK.tree_hash(base)
    Cfg.FILE = Paths.get(os.path.join(base, "config.properties"))
    o = {"m10": str(Cfg.migrate0110()), "m29": str(Cfg.migrate0129()), "m32": str(Cfg.migrate0132()), "load": str(Cfg.load())}
    AS.DIR = Paths.get(os.path.join(base, "abilities"))
    Pub.start(Paths.get(home), None)
    Pub.flush()
    Pub.shutdown()
    after = HK.tree_hash(base)
    ch = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    K.check(not ch and o["m32"] == "", "ST start %s on a scratch COPY of the live data: nothing written (%s)" % (step, ch))
    if step == "2":
        K.check(HK.tree_hash(LIVE) == json.load(open(os.path.join(scratch, "st-live.json"))), "ST: the live Skyy_SkyyClasses folder was only read")
    K.save()
    sys.stdout.flush()
    os._exit(0)


def run_st1(out, jar, scratch, _home):
    run_st(out, jar, scratch, "1")


def run_st2(out, jar, scratch, _home):
    run_st(out, jar, scratch, "2")


if __name__ == "__main__":
    HK.run(name="SkyyClasses", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("exec", run_exec), ("st1", run_st1), ("st2", run_st2)], script=__file__)
