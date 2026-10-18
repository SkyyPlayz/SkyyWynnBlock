"""Harness for SkyyMobs 0.1.11 (One hit at most ON by default (35 %) + elites out of the Boss roles + the one-time MobMig11 update;
tools/mobs_0_1_11_patch.py). Every 0.1.10 check (run from test_skyymobs_0.1.10.py's own code, which runs 0.1.9's and 0.1.8's) on the
0.1.11 jar - with 0.1.10's two Boss-roles expectations swapped for 0.1.11's (Skeleton_Elite* is no boss any more) - + B11.
Build first: python tools/mobs_0_1_11_patch.py && python SkyyMobs/build_skyymobs_0.1.11.py

    python SkyyMobs/test_skyymobs_0.1.11.py [--keep] [--dir <scratch>]
    python SkyyMobs/test_skyymobs_0.1.11.py --static      (no jars: the text checks only)

Phases (fresh child JVMs, tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.1.10 -> 0.1.11 (EXPECT below); added MobMig11
  X  exec     every 0.1.10 exec check, then EXECUTED B11:
              defaults: HIT_CAP 35 (useDefaults, a file without the line), hitCap=0 still means off; the fresh file carries
              strength.hitCap=35, the new Boss roles and the MobMig11 marker
              capHit on BOTH strength shapes (curve + linear): 80 of 100 max -> 35, 20 -> 20, unknown max / cap 0 -> unchanged;
              LevelDamage.handle calls MobCfg.capHit + hitNote (bytecode); hitNote at most once per 5 s
              bosses: Skeleton_Elite* no boss, Goblin_Duke / Dragon_* / *_Boss* still are
              MobMig11.update: an untouched hitCap 0 + 0.1.10 Boss roles move (value text only, marker above the comment run), admin
              values kept + noted, multi-line entries kept, CRLF kept, the marker = null, the fresh default file = null
              MobMig11.run on a scratch COPY of Skyy's live Skyy_SkyyMobs: hitCap 0 -> 35, nothing else changes (Properties), a
              config-history copy holds the old bytes, one config-changes.log line, a second run changes nothing
  D  live     the 0.1.8 live check (the live Skyy_SkyyMobs copy loads the same settings with 0.1.10 and 0.1.11, twice; bytes unchanged)
  AA engine-access audit
Scratch: tools/dev/scratch/mq-bugs/mobs (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, re, subprocess, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.1.11"
GEN = os.path.join(HERE, "build_skyymobs_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyymobs_0.1.10.py")
PATCH = os.path.join(ROOT, "tools", "mobs_0_1_11_patch.py")
SCRATCH_DEF = os.path.join(ROOT, "tools", "dev", "scratch", "mq-bugs", "mobs")
OLD_ROLES = "Goblin_Duke*, Trork_Chieftain, Dragon_*, Skeleton_Elite*, *_Boss*"
NEW_ROLES = "Goblin_Duke*, Trork_Chieftain, Dragon_*, *_Boss*"


def _arg(name, default=None):
    if name in sys.argv and sys.argv.index(name) + 1 < len(sys.argv):
        return sys.argv[sys.argv.index(name) + 1]
    return default


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
    check(g.startswith('"""SkyyMobs 0.1.11 - build script') and g.count('VERSION = "0.1.11"') == 1 and "0.1.10 (the base," in g,
          "S header + VERSION 0.1.11 (the 0.1.10 notes kept as the base)")
    check("ROLLBACK 0.1.11 -> 0.1.10: safe" in g and "MIGRATION MobMig11" in g, "S the 0.1.11 notes are in the generated docstring")
    try:
        compile(g, GEN, "exec")
        check(True, "")
    except SyntaxError as e:
        check(False, "S the generated script compiles as Python: %s" % e)
    for w in ("registerSystem(", "registerCommand(", "bridge().put(", "bridge().remove("):
        check(g.count(w) == o.count(w), "S no new %s vs 0.1.10" % w)
    check(g.count("makeClass(") == o.count("makeClass(") + 1 and ", bfn, m11]" in g, "S exactly one new class (MobMig11), in ALL")
    check('("strength.hitCap", "One hit at most", "strength", "int", str(HITCAP_DEF), "0", "100"' in g and "HITCAP_DEF = 35" in g,
          "S the One hit at most row defaults to 35")
    check('BOSS_ROLES_DEF == "%s"' % NEW_ROLES in g, "S the Boss roles default drops Skeleton_Elite*")
    hd = g[g.index("public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {\n  try {\n    if (@PKG@.MobLevel.MOBS.isEmpty()"):]
    hd = hd[:hd.index('}""")')]
    check("@PKG@.MobCfg.capHit(amt, vmax)" in hd and "CURVE_ON" not in hd and "hitNote(" in hd,
          "S LevelDamage caps through MobCfg.capHit with no strength-shape branch (both shapes)")
    su = g[g.index("public void setup() {"):]
    check(su.index("MobMig14.run(dir)") < su.index("MobMig11.run(dir)") < su.index("@PKG@.MobCfg.load();"), "S setup: MobMig14 -> MobMig11 -> MobCfg.load")
    sc = os.path.join(os.path.abspath(_arg("--dir", SCRATCH_DEF)), "static")
    shutil.rmtree(sc, ignore_errors=True)
    os.makedirs(sc)
    try:
        cp = os.path.join(sc, "build_skyymobs_0.1.11.py")
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

# the 0.1.10 harness's own phase code (it loads 0.1.9's + 0.1.8's), its two 0.1.10 Boss-roles expectations swapped for 0.1.11's
_T110 = os.path.join(HERE, "test_skyymobs_0.1.10.py")
_src = open(_T110, encoding="utf-8").read()
_src = _src[:_src.rindex("HK.run(")]
for _o, _n in (('K.check("bosses.roles=%s\\n" in str(Cfg.DEF_CFG)' % OLD_ROLES, 'K.check("bosses.roles=%s\\n" in str(Cfg.DEF_CFG)' % NEW_ROLES),
               ('"Dragon_Fire", "Skeleton_Elite_Knight", "Dungeon_Crypt_Boss"', '"Dragon_Fire", "Dungeon_Crypt_Boss"'),
               ('"Goblin_Scrapper", "Cow"]', '"Goblin_Scrapper", "Cow", "Skeleton_Elite_Knight"]')):
    assert _src.count(_o) == 1, "0.1.10 harness anchor: " + _o
    _src = _src.replace(_o, _n)
T110 = {"__file__": _T110, "__name__": "test_skyymobs_0_1_10"}
exec(compile(_src, _T110, "exec"), T110)

JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMobs-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMobs-0.1.10.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.mobs."
T110["T19"]["T18"]["OLD_JAR"] = OLD_JAR   # the 0.1.8 live phase compares the OLD jar (now 0.1.10) with this one
LIVE_DIR = T110["T19"]["T18"]["LIVE_DIR"]
EXPECT = {
    "MobCfg": ["+f HIT_NOTE_AT", "+m capHit", "+m hitNote", "~<clinit>", "~m apply", "~m load", "~m reloadAll", "~m useDefaults"],
    "LevelDamage": ["~m handle"],
    "SkyyMobsPlugin": ["~m setup"],
    "CfgFn": ["~m opExport"],
    "CfgRows": ["~<clinit>", "~m header"],
}
ADDED = ["MobMig11"]


def run_exec(out, jar, scratch, home):
    T110["run_exec"](out, jar, scratch, home)        # starts the JVM; every 0.1.10 (+ 0.1.9, 0.1.8) exec check
    import json, zipfile
    from jpype import JClass
    K = HK.Child(out + ".0111.json")
    Cfg, Mig, Mg = JClass(PKG + "MobCfg"), JClass(PKG + "MobMig11"), JClass(PKG + "MobMig")
    Cfg.useDefaults()
    # ---- defaults
    dc = str(Cfg.DEF_CFG)
    K.check("\nstrength.hitCap=35\n" in dc and "\nbosses.roles=%s\n" % NEW_ROLES in dc and dc.count(str(Mig.MARK_ID)) == 1,
            "B11 LOAD the fresh default file: strength.hitCap=35, the new Boss roles, the MobMig11 marker")
    K.eq(int(Cfg.HIT_CAP), 35, "B11 LOAD HIT_CAP after useDefaults")
    pc, pb = Cfg.props(Cfg.DEF_CFG), Cfg.props(Cfg.DEF_BANDS)
    pc.remove("strength.hitCap")
    Cfg.apply(pc, pb)
    K.eq(int(Cfg.HIT_CAP), 35, "B11 LOAD a file without the hitCap line = 35")
    pc.setProperty("strength.hitCap", "0")
    Cfg.apply(pc, pb)
    K.eq(int(Cfg.HIT_CAP), 0, "B11 LOAD an admin's hitCap=0 still means off")
    Cfg.useDefaults()
    # ---- capHit: both strength shapes
    got = []
    for curve in (True, False):
        Cfg.CURVE_ON = curve
        Cfg.HIT_CAP = 35
        got.append((float(Cfg.capHit(80.0, 100.0)), float(Cfg.capHit(20.0, 100.0)), float(Cfg.capHit(80.0, 0.0))))
        Cfg.HIT_CAP = 0
        got.append(float(Cfg.capHit(80.0, 100.0)))
    K.eq(got, [(35.0, 20.0, 80.0), 80.0, (35.0, 20.0, 80.0), 80.0], "B11 CAP 80 / 20 of max 100 -> 35 / 20; max unknown or cap 0 -> unchanged (curve + linear)")
    Cfg.useDefaults()
    Cfg.HIT_NOTE_AT = 0
    Cfg.hitNote("Golem_Crystal_Earth", 10, 80.0, 35.0, 100.0)
    a1 = int(Cfg.HIT_NOTE_AT)
    Cfg.hitNote("Golem_Crystal_Earth", 10, 90.0, 35.0, 100.0)
    K.check(a1 > 0 and int(Cfg.HIT_NOTE_AT) == a1, "B11 NOTE the clipped-hit INFO line at most once per 5 s")
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
    K.check("MobCfg.capHit" in hd and "MobCfg.hitNote" in hd and "CURVE_ON" not in hd, "B11 SHAPE LevelDamage.handle caps via capHit + hitNote, no shape branch")
    K.check("MobMig11.run" in code("SkyyMobsPlugin", "setup"), "B11 SETUP setup runs MobMig11")
    # ---- bosses
    K.check(not bool(Cfg.isBoss("Skeleton_Elite_Knight")) and not bool(Cfg.isBoss("Skeleton_Elite")) and bool(Cfg.isBoss("Goblin_Duke"))
            and bool(Cfg.isBoss("Dragon_Fire")) and bool(Cfg.isBoss("Dungeon_Crypt_Boss")), "B11 BOSS elites are no bosses; Duke / Dragon / *_Boss* still are")
    # ---- MobMig11.update (pure text)
    mark = str(Mig.MARK)
    doc = "# One hit at most: a levelled mob's hit on a player (before armour) is at most this % of the player's max Health; 0 is off."
    t1 = "a=1\n# c1\n" + doc + "\nstrength.hitCap=0\nbosses.roles=" + OLD_ROLES + "\nz=2\n"
    r = Mig.update(t1)
    K.eq(str(r[0]), "a=1\n" + mark + "\n# c1\n" + doc + "\nstrength.hitCap=35\nbosses.roles=" + NEW_ROLES + "\nz=2\n",
         "B11 MIG untouched lines move (value only), the marker above the comment run")
    K.eq(list(map(str, r[3])), ["strength.hitCap", "0", "35", "bosses.roles", OLD_ROLES, NEW_ROLES], "B11 MIG change rows")
    r = Mig.update("strength.hitCap=50\nbosses.roles=Goblin_Duke*, Skeleton_Elite*\n")
    K.check(str(r[0]) == mark + "\nstrength.hitCap=50\nbosses.roles=Goblin_Duke*, Skeleton_Elite*\n" and len(r[3]) == 0 and len(r[2]) == 2,
            "B11 MIG admin values kept + one note each")
    r = Mig.update("strength.hitCap=35\nx=1\n")
    K.check(len(r[2]) == 0 and len(r[3]) == 0 and str(r[1]) == "", "B11 MIG a line already at 35 = no note, no change")
    r = Mig.update("strength.hitCap=0\nstrength.hitCap=40\n")
    K.check(len(r[3]) == 0 and "strength.hitCap=0\nstrength.hitCap=40" in str(r[0]), "B11 MIG only the LAST entry counts (40 kept, the 0 untouched)")
    r = Mig.update("bosses.roles=Goblin_Duke*, \\\n  Skeleton_Elite*\nstrength.hitCap=0\n")
    K.check(list(map(str, r[3])) == ["strength.hitCap", "0", "35"] and "bosses.roles=Goblin_Duke*, \\\n  Skeleton_Elite*\n" in str(r[0]),
            "B11 MIG a continued (multi-line) entry is kept")
    r = Mig.update("x=1\r\n" + doc + "\r\nstrength.hitCap=0\r\n")
    K.eq(str(r[0]), "x=1\r\n" + mark + "\r\n" + doc + "\r\nstrength.hitCap=35\r\n", "B11 MIG CRLF kept")
    K.check(Mig.update(t1 + mark + "\n") is None and Mig.update(dc) is None, "B11 MIG the marker (or the fresh default file) = nothing to do")
    r = Mig.update("x=1\n")
    K.check(str(r[0]) == mark + "\nx=1\n" and len(r[3]) == 0, "B11 MIG no lines = only the marker (at the top)")
    # ---- MobMig11.run on a scratch COPY of the live folder
    if os.path.isdir(LIVE_DIR):
        d = os.path.join(scratch, "mig11", "Skyy_SkyyMobs")
        shutil.rmtree(os.path.dirname(d), ignore_errors=True)
        shutil.copytree(LIVE_DIR, d)
        f = os.path.join(d, "config.properties")
        old = open(f, "rb").read()
        P = JClass("java.nio.file.Paths")
        msg = str(Mig.run(P.get(d)))
        new = open(f, "rb").read()
        K.check("strength.hitCap 0 -> 35" in msg or b"strength.hitCap=0" not in old, "B11 RUN live copy: %s" % msg[:200])
        exp = old.replace(b"\nstrength.hitCap=0\n", b"\nstrength.hitCap=35\n") if b"\nstrength.hitCap=0\n" in old else old
        K.eq(new.replace((mark + "\n").encode("latin-1"), b"").replace((mark + "\r\n").encode("latin-1"), b""), exp,
             "B11 RUN live copy: only the hitCap value + the marker line differ (bytes)")
        hist = os.path.join(d, "config-history")
        found = False
        for root_, _ds, fs in os.walk(hist):
            for fn in fs:
                if open(os.path.join(root_, fn), "rb").read() == old:
                    found = True
        K.check(found, "B11 RUN a config-history copy holds the old bytes")
        lg = open(os.path.join(d, "config-changes.log"), encoding="latin-1").read()
        K.check(lg.count("SkyyMobs 0.1.11\t-\tupdate\tstrength.hitCap\t0\t35\tok") == (1 if b"\nstrength.hitCap=0\n" in old else 0),
                "B11 RUN one config-changes.log line (Undo)")
        msg2 = str(Mig.run(P.get(d)))
        K.check(msg2 == "" and open(f, "rb").read() == new, "B11 RUN a second run changes nothing")
        if "--keep" not in sys.argv:
            shutil.rmtree(os.path.dirname(d), ignore_errors=True)
    else:
        K.check(True, "B11 RUN skipped (no live folder)")
    K.save()
    dd = json.load(open(out + ".0111.json"))
    e = json.load(open(out))
    e["ok"] += dd["ok"]
    e["fails"] += dd["fails"]
    json.dump(e, open(out, "w"), indent=1)


HK.run("SkyyMobs", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("exec", run_exec), ("live", T110["T19"]["T18"]["run_live"])], __file__, live=(LIVE_DIR, "Skyy_SkyyMobs"))
