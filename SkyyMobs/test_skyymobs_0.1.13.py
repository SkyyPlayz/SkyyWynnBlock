"""Harness for SkyyMobs 0.1.13 (One hit at most for EVERY mob - beta bug 3; tools/mobs_0_1_13_patch.py). Every 0.1.12 check (run from
test_skyymobs_0.1.12.py's own code, which runs 0.1.11's, 0.1.10's, 0.1.9's and 0.1.8's) on the 0.1.13 jar + B13.
Build first: python tools/mobs_0_1_13_patch.py && python SkyyMobs/build_skyymobs_0.1.13.py

    python SkyyMobs/test_skyymobs_0.1.13.py [--keep] [--dir <scratch>]
    python SkyyMobs/test_skyymobs_0.1.13.py --static      (no jars: the text checks only)

Phases (fresh child JVMs, tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.1.12 -> 0.1.13 (EXPECT below); no class added
  X  exec     every 0.1.12 exec check, then EXECUTED B13: LevelDamage.handle (bytecode) - no early return on an empty MOBS map, the
              unlevelled branch (NPCEntity attacker + PlayerRef victim -> MobCfg.capHit + hitNote) BEFORE the level multiplier, capHit
              called on both branches; hitNote with an unlevelled mob (level 0) runs; capHit on a vanilla Golem_Crystal_Sand swing (47 +10 %)
              and a 1e6 boss hit vs a 210-HP player -> at most 35 % (73.5); cap 0 = off; the Server Setup hint says "Any mob's hit"
  D  live     the 0.1.8 live check (the live Skyy_SkyyMobs copy loads the same settings with 0.1.12 and 0.1.13, twice; bytes unchanged)
  AA engine-access audit
Scratch: tools/dev/scratch/mob3/mobs (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.1.13"
GEN = os.path.join(HERE, "build_skyymobs_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyymobs_0.1.12.py")
PATCH = os.path.join(ROOT, "tools", "mobs_0_1_13_patch.py")
SCRATCH_DEF = os.path.join(ROOT, "tools", "dev", "scratch", "mob3", "mobs")


def _arg(name, default=None):
    if name in sys.argv and sys.argv.index(name) + 1 < len(sys.argv):
        return sys.argv[sys.argv.index(name) + 1]
    return default


def _handle(g):
    return g[g.index("public LevelDamage(boolean ordered) {"):g.index('C(dmu, "public LevelDamageU() { super(false); }")')]


def run_static():
    fails, ok = [], [0]

    def check(c, what):
        if c:
            ok[0] += 1
        else:
            fails.append(what)
            print("FAIL", what)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    check(g.startswith('"""SkyyMobs 0.1.13 - build script') and g.count('VERSION = "0.1.13"') == 1 and "0.1.12 (the base," in g,
          "S header + VERSION 0.1.13 (the 0.1.12 notes kept as the base)")
    check("ROLLBACK 0.1.13 -> 0.1.12: safe" in g and "ONE HIT AT MOST FOR EVERY MOB" in g, "S the 0.1.13 notes are in the generated docstring")
    try:
        compile(g, GEN, "exec")
        check(True, "")
    except SyntaxError as e:
        check(False, "S the generated script compiles as Python: %s" % e)
    for w in ("registerSystem(", "registerCommand(", "bridge().put(", "bridge().remove(", "makeClass("):
        check(g.count(w) == o.count(w), "S no new %s vs 0.1.12" % w)
    h = _handle(g)
    check("MOBS.isEmpty() ||" not in h and "if (i == null || i.level <= 1) return;" not in h, "S LevelDamage: no early return before the cap")
    check(h.index("if (!lvd) {") < h.index("@NPCE@.getComponentType()") < h.index("@PKG@.MobCfg.capHit((double) a1, vmax1)")
          < h.index("@PKG@.MobCfg.dmgMult(i.level)") < h.index("@PKG@.MobCfg.capHit(amt, vmax)"),
          "S LevelDamage: the unlevelled-mob cap (NPC attacker) runs before the levelled path, which keeps its own cap")
    check(h.count("if (vp == null) return;") == 1 and "if (an == null) return;" in h, "S the unlevelled cap: player victims only, NPC attackers only")
    _cap = lambda x: x[x.index("public static double capHit("):x.index("}", x.index("public static double capHit(")) + 1]
    check(_cap(g) == _cap(o), "S MobCfg.capHit unchanged")
    check("\"Any mob's hit on a player (bosses too, before armor) is at most this % of their max Health. 0 = off.\"" in g,
          "S the Server Setup hint names every mob")
    check(g.count("strength.hitCap=%d") == o.count("strength.hitCap=%d") and "HITCAP_DEF = 35" in g, "S the setting + default unchanged (no migration)")
    sc = os.path.join(os.path.abspath(_arg("--dir", SCRATCH_DEF)), "static")
    shutil.rmtree(sc, ignore_errors=True)
    os.makedirs(sc)
    try:
        cp = os.path.join(sc, "build_skyymobs_0.1.13.py")
        p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
        check(p.returncode == 0 and "wrote" in p.stdout, "S the patch re-runs: %s %s" % (p.stdout.strip(), p.stderr.strip()[-300:]))
        check(os.path.isfile(cp) and open(cp, "rb").read() == open(GEN, "rb").read(), "S deterministic: the re-run gives identical bytes")
        check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(sc, ignore_errors=True)
    print("SkyyMobs %s static checks: %d ok, %d fail(s)" % (VERSION, ok[0], len(fails)))
    for f in fails:
        print("FAIL:", f)
    sys.exit(1 if fails else 0)


if "--static" in sys.argv:
    run_static()

# ================================================================================================================ the jar harness
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", SCRATCH_DEF]
import skyybuild as B
import harness_kit as HK

_T112 = os.path.join(HERE, "test_skyymobs_0.1.12.py")
_src = open(_T112, encoding="utf-8").read()
_src = _src[:_src.rindex("HK.run(")]
T112 = {"__file__": _T112, "__name__": "test_skyymobs_0_1_12"}
exec(compile(_src, _T112, "exec"), T112)

JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMobs-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMobs-0.1.12.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.mobs."
T18 = T112["T18"]
T18["OLD_JAR"] = OLD_JAR       # the 0.1.8 live phase compares the OLD jar (now 0.1.12) with this one
LIVE_DIR = T112["LIVE_DIR"]
# 0.1.12's B12 RUN NewBetaTest wants the PRE-0.1.12 files; since the 2026-10-18 deploy the live folder is already migrated (MobMig12 marker),
# so run it on the deploy backup taken just before that deploy (backups/deploy-20261018-1352, read only: the harness copies it to scratch)
_BK = os.path.join(ROOT, "backups", "deploy-20261018-1352", "data", "Skyy_SkyyMobs")
_lc = os.path.join(T112["LIVE_NEW"], "config.properties")
if os.path.isfile(_lc) and "SkyyMobs 0.1.12" in open(_lc, encoding="latin-1").read() and os.path.isdir(_BK):
    T112["LIVE_NEW"] = _BK
    print("B13 note: the live NewBetaTest SkyyMobs folder is already on 0.1.12 - B12 RUN NewBetaTest uses the pre-0.1.12 backup " + _BK)
EXPECT = {
    "LevelDamage": ["~m handle"],
    "MobCfg": ["~m hitNote", "~m load", "~m reloadAll", "~m useDefaults"],   # hitNote + the inlined row texts / version
    "CfgRows": ["~<clinit>", "~m header"],     # the One hit at most hint + the version in the file header
    "CfgFn": ["~m opExport"],                  # the version in the export text
    "SkyyMobsPlugin": ["~m setup"],            # the version in the ready line
}
ADDED = []


def run_exec(out, jar, scratch, home):
    T112["run_exec"](out, jar, scratch, home)        # starts the JVM; every 0.1.12 (+ 0.1.11 ... 0.1.8) exec check
    import json
    from jpype import JClass
    K = HK.Child(out + ".0113.json")
    Cfg = JClass(PKG + "MobCfg")
    Cfg.useDefaults()
    K.eq(int(Cfg.HIT_CAP), 35, "B13 CAP the default One hit at most = 35 %")
    # a 210-HP player (Skyy's beta character): a vanilla Golem_Crystal_Sand swing (47 +10 %), a 1e6 boss hit, a small hit
    K.eq([round(float(Cfg.capHit(x, 210.0)), 4) for x in (51.7, 1.0e6, 20.0)], [51.7, 73.5, 20.0],
         "B13 CAP vs 210 max Health: 51.7 stays, a 1e6 boss hit -> 73.5 (35 %), 20 stays")
    Cfg.HIT_CAP = 0
    K.eq(float(Cfg.capHit(1.0e6, 210.0)), 1.0e6, "B13 CAP 0 = off (unchanged)")
    Cfg.useDefaults()
    try:
        Cfg.HIT_NOTE_AT = 0
        Cfg.hitNote("Golem_Crystal_Sand", 0, 300.0, 73.5, 210.0)
        K.check(int(Cfg.HIT_NOTE_AT) > 0, "B13 NOTE hitNote for an unlevelled mob (level 0) runs")
    except Exception as e:
        K.check(False, "B13 NOTE hitNote level 0: %s" % e)
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
    hd = code("LevelDamage", "handle")
    npc = "com.hypixel.hytale.server.npc.entities.NPCEntity"
    K.check(hd.count("MobCfg.capHit") == 2 and hd.count("MobCfg.hitNote") == 2, "B13 BYTECODE LevelDamage.handle: capHit + hitNote on both branches")
    K.check(npc + ".getComponentType" in hd and npc + ".getRoleName" in hd
            and hd.index(npc + ".getComponentType") < hd.index("MobCfg.capHit") < hd.index("MobCfg.dmgMult"),
            "B13 BYTECODE the unlevelled branch (NPCEntity attacker -> capHit) comes before the level multiplier")
    K.check(hd.index("MobCfg.HIT_CAP") < hd.index("MobCfg.dmgMult") and hd.index("MobLevel.MOBS") < hd.index("MobCfg.HIT_CAP"),
            "B13 BYTECODE the MOBS lookup is optional (HIT_CAP decides before any level work)")
    K.save()
    dd = json.load(open(out + ".0113.json"))
    e = json.load(open(out))
    e["ok"] += dd["ok"]
    e["fails"] += dd["fails"]
    e["notes"] = e.get("notes", []) + dd.get("notes", [])
    json.dump(e, open(out, "w"), indent=1)


HK.run("SkyyMobs", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("exec", run_exec), ("live", T18["run_live"])], __file__, live=(LIVE_DIR, "Skyy_SkyyMobs"))
