"""Harness for SkyyClasses 0.1.39 (BETA BUG 6, the Classes part: no ability hit through blocks; tools/classes_0_1_39_patch.py). Build first:
    python tools/classes_0_1_39_patch.py && python SkyyClasses/build_skyyclasses_0.1.39.py
    python SkyyClasses/test_skyyclasses_0.1.39.py [--keep]
Phases (tools/harness_kit.py, fresh child JVMs, -Xverify:all, TEMP / TMP in tools/dev/scratch/ac-bugs/cls):
  A   verify   every class loads + initialises
  C   compare  0.1.38 -> 0.1.39: exactly the planned members (EXPECT); non-class entries = manifest.json only
  R   repro    BUG 6 ON THE OLD 0.1.38 JAR, on the engine stand-ins of test_skyyclasses_0.1.25.py (its N0 set-up) + the Abil.SOLID block seam:
               an enemy behind a 2-high wall / under the floor IS hit by the Explosive Arrow blast, a Piercing-Shot ray and Frost Nova (the bug)
  X   exec     the same scenes on 0.1.39: behind the wall / under the floor = no hit, in the open = hit, a 1-high wall: the ray is seen over it,
               the ground-level blast is not; abil.lineOfSight off = the old behaviour; losOpen's rules (start / end block skipped, only SOLID
               closes, unreadable never); the row in a fresh config.properties; every listed site calls losOk (bytecode)
  ST1 / ST2  START TWICE on a scratch COPY of the live Skyy_SkyyClasses folder (setup's order): nothing written; the live folder only read
  AA  engine-access audit
Not executed here (UNVERIFIED until the game): the real world blocks (arcSolid's world read = Arcane Breach's, live since 0.1.32), the spin /
Cyclone Kick / Meteor / burst / lookMob sites in a running world (bytecode-checked only).
"""
import os, sys, json, shutil, zipfile, textwrap, time, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import deploy_set as DS

VERSION, OLD = "0.1.39", "0.1.38"
JAR = os.path.join(HERE, "SkyyClasses-%s.jar" % VERSION)
OLD_JAR = os.path.join(HERE, "SkyyClasses-%s.jar" % OLD)
PKG = "com.skyy.classes."
SCRATCH = os.path.join(TOOLS, "dev", "scratch", "ac-bugs", "cls")
LIVE = os.path.join(B.HYTALE, "UserData", "Saves", DS.WORLD, "mods", "Skyy_SkyyClasses")
T25 = os.path.join(HERE, "test_skyyclasses_0.1.25.py")
ADDED = []
EXPECT = {
    "Abil": ["+f LOS_MISS", "+m losOpen", "+m losOk", "~<clinit>", "~m spinTick", "~m blastAt", "~m nova", "~m meteorImpact", "~m burst",
             "~m kickRun", "~m rayHits", "~m lookMob", "~m starTick", "~m wakeTick", "~m shockRun", "~m wave", "~m splitRun", "~m rainTick",
             "~m sbCone", "~m sbLine", "~m pinRun", "~m netTick", "~m beamTick"],
    "AbilCfg": ["+f LOS_ON", "~<clinit>", "~m read"],                                    # the row
    "SkyyClassesPlugin": ["~m setup"],                                                   # the version text
    "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "KitMigrate": ["~m runOnce"],   # the version text (+ the row)
    "CfgFile": ["~<clinit>"], "CfgRows2": ["~<clinit>"], "ClassCfg": ["~<clinit>"],   # the new row in the kit tables + default file
}
SITES = {"spinTick": 1, "blastAt": 1, "nova": 1, "meteorImpact": 1, "burst": 1, "kickRun": 1, "rayHits": 1, "lookMob": 1,
         # review round: Starfall, the Frost Nova line, Shield Shockwave, Hundred Fists, Earthsplitter (+ Ground Pound = 2), Arrow Rain, the Spellblade
         # cone / line selectors (Shattering Arc, Imbue burst / crescent, Tempest), Rain Pin, Hunters' Net, Arcane Beam
         "starTick": 1, "wakeTick": 1, "shockRun": 1, "wave": 1, "splitRun": 2, "rainTick": 1, "sbCone": 1, "sbLine": 1, "pinRun": 1, "netTick": 1,
         "beamTick": 1}


def setup(out, jar, scratch, _home):
    """test_skyyclasses_0.1.25.py's N0 engine stand-ins (as 0.1.38's harness) on the given jar"""
    stats_zip = os.path.join(scratch, "stats.zip")
    if not os.path.isfile(stats_zip):
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
    return ns


FLOOR = set((x, 63, z) for x in range(-4, 14) for z in range(-4, 5))
WALL2 = FLOOR | set((3, y, z) for y in (64, 65) for z in range(-4, 5))
WALL1 = FLOOR | set((3, 64, z) for z in range(-4, 5))
CAVE = FLOOR | set((x, 62, z) for x in range(-4, 14) for z in range(-4, 5))


def scenes(ns):
    """{scene: [blast hits, ray hits, nova count]} for a foe at (6.5, 64, 0.5) (below: at (1.5, 60, 0.5)), the Mage at (0.5, 64, 0.5)"""
    from jpype import JClass, JImplements, JOverride
    A, AJ, NEARL, npc = ns["A"], ns["C"]("AbilJob"), ns["NEARL"], ns["npc"]
    mu, mr, tbuf = ns["mu"], ns["mr"], ns["tbuf"]
    Bool = JClass("java.lang.Boolean")
    SOL = {"s": set()}

    @JImplements("java.util.function.Function")
    class Solid(object):
        @JOverride
        def apply(self, o):
            return Bool.valueOf((int(math.floor(o[0])), int(math.floor(o[1])), int(math.floor(o[2]))) in SOL["s"])
    A.SOLID = Solid()
    res = {}
    k = [700]
    for name, solid, fpos in (("open", FLOOR, (6.5, 64.0, 0.5)), ("wall2", WALL2, (6.5, 64.0, 0.5)), ("wall1", WALL1, (6.5, 64.0, 0.5)),
                              ("below", CAVE, (1.5, 60.0, 0.5))):
        SOL["s"] = solid
        out = []
        for what in ("blast", "ray", "nova"):
            k[0] += 1
            foe = npc(k[0], *fpos)
            del NEARL[:]
            NEARL.append(foe)
            now = int(time.time() * 1000)
            if what == "blast":
                out.append(int(A.blastAt(tbuf, mr, mu, 0.5, 64.0, 0.5, 8.0, 3.0, 0.0, None, None, True)))
            elif what == "ray":
                d = (1.0, 0.0, 0.0) if name != "below" else (0.2 / math.sqrt(1.04), -1.0 / math.sqrt(1.04), 0.0)
                out.append(int(A.rayHits(tbuf, mr, 0.5, 65.6, 0.5, d[0], d[1], d[2], 12.0, 0.5, None).size()))
            else:
                j = AJ(8, now, mu, "FrostNova", 0.5, 64.0, 0.5, 8.0, 3.0)
                out.append(int(A.nova(j, tbuf, mr, now)))
        res[name] = out
    del NEARL[:]
    A.SOLID = None
    return res


def run_repro(out, jar, scratch, _home):
    ns = setup(out, OLD_JAR, scratch, _home)
    K = ns["K"]
    r = scenes(ns)
    K.notes.append("R on 0.1.38: %s" % r)
    K.check(r["open"] == [1, 1, 1], "R: control - an enemy in the open is hit by blast / ray / nova on 0.1.38: %s" % r["open"])
    K.check(r["wall2"] == [1, 1, 1] and r["below"] == [1, 1, 1], "R: REPRO bug 6 on the old jar - behind a 2-high wall and under the floor the enemy IS hit: %s" % r)
    K.save()


def run_exec(out, jar, scratch, _home):
    ns = setup(out, jar, scratch, _home)
    K, A, AC, C = ns["K"], ns["A"], ns["AC"], ns["C"]
    from jpype import JClass, JImplements, JOverride
    r = scenes(ns)
    K.notes.append("X on 0.1.39: %s" % r)
    K.check(r["open"] == [1, 1, 1], "X1: an enemy in the open is still hit by blast / ray / nova: %s" % r["open"])
    K.check(r["wall2"] == [0, 0, 0] and r["below"] == [0, 0, 0], "X1: FIX bug 6 - behind a 2-high wall / under the floor: no hit: %s %s" % (r["wall2"], r["below"]))
    K.check(r["wall1"] == [0, 1, 1], "X1: a 1-high wall: the eye-height ray and the chest-height nova see over it (the enemy's top), the ground-level blast does not: %s" % r["wall1"])
    m0 = int(A.LOS_MISS)
    K.check(m0 >= 7, "X1: LOS_MISS counted the stopped hits (%d)" % m0)
    AC.LOS_ON = False
    r2 = scenes(ns)
    AC.LOS_ON = True
    K.check(r2["wall2"] == [1, 1, 1] and r2["below"] == [1, 1, 1], "X2: abil.lineOfSight off = the 0.1.38 behaviour: %s" % r2)
    Bool = JClass("java.lang.Boolean")
    SOL = {"s": set(), "unk": False}

    @JImplements("java.util.function.Function")
    class Solid(object):
        @JOverride
        def apply(self, o):
            return Bool.valueOf((int(math.floor(o[0])), int(math.floor(o[1])), int(math.floor(o[2]))) in SOL["s"])
    A.SOLID = Solid()
    lo = lambda *a: bool(A.losOpen(ns["tbuf"], *a))
    SOL["s"] = {(0, 65, 0), (6, 64, 0)}
    own = lo(0.5, 65.5, 0.5, 6.5, 64.5, 0.5)
    SOL["s"] = {(3, 64, 0)}
    mid = lo(0.5, 64.5, 0.5, 6.5, 64.5, 0.5)
    short = lo(0.5, 64.5, 0.5, 0.5, 64.5, 0.5)
    A.SOLID = None
    K.check(own and not mid and short, "X3: losOpen skips the start and end blocks (yours / the enemy's), a solid block between closes it, a zero-length line is open")
    # no block seam and no world (a bare stand-in world): arcSolid reads -1 (unreadable) -> never blocks
    K.check(bool(A.losOpen(ns["tbuf"], 0.5, 64.5, 0.5, 6.5, 64.5, 0.5)), "X3: an unreadable world (-1) never costs a hit")
    # the row in a fresh file + the default
    cfg = open(os.path.join(scratch, "n-home", "config.properties"), encoding="latin-1").read()
    K.check("\nabil.lineOfSight=true" in cfg.replace("\r\n", "\n") and bool(AC.LOS_ON), "X4: a fresh config.properties carries abil.lineOfSight=true (default on)")
    # every listed site calls losOk (bytecode: invokestatic Abil.losOk)
    CP = JClass("javassist.ClassPool")(True)
    CP.appendClassPath(jar)
    cc = CP.get(PKG + "Abil")
    calls = {}
    for m in cc.getDeclaredMethods():
        nm = str(m.getName())
        if nm not in SITES:
            continue
        ca = m.getMethodInfo().getCodeAttribute()
        cp = m.getMethodInfo().getConstPool()
        it = ca.iterator()
        n = 0
        while it.hasNext():
            p = it.next()
            if it.byteAt(p) == 0xb8 and str(cp.getMethodrefName(it.u16bitAt(p + 1))) == "losOk":
                n += 1
        calls[nm] = calls.get(nm, 0) + n
    K.check(calls == SITES, "X4: every enemy-hit site calls losOk (spin, blast, nova, meteor, burst, Cyclone Kick, rays, lookMob + the review's 11): %s" % calls)
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
    K.check(bool(JClass(PKG + "AbilCfg").LOS_ON), "ST: the live file (no abil.lineOfSight line) reads the default on")
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
           phases=[("repro", run_repro), ("exec", run_exec), ("st1", run_st1), ("st2", run_st2)], script=__file__)
