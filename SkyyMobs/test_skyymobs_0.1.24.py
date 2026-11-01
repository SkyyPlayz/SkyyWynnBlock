"""Harness for SkyyMobs 0.1.24 (gear lane round 2 = gl2, the SkyyMobs part: the Trork / Kweebec set drop rows - MobTheme, rolled by SpoilsSys;
tools/mobs_0_1_24_patch.py). Build first:
    python tools/mobs_0_1_24_patch.py && python SkyyMobs/build_skyymobs_0.1.24.py
    python SkyyMobs/test_skyymobs_0.1.24.py [--keep] [--expect-dump]

Phases (fresh child JVMs, tools/harness_kit.py):
  S     static   the patch re-runs to identical bytes (--out), line endings kept, ONE new class (MobTheme), no new system / command; the jar
                 changes only classes + the manifest (every role / model / spawn / lang file byte-identical to 0.1.23)
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.1.23 -> 0.1.24 (EXPECT below)
  X     exec     EXECUTES MobTheme: the defaults (fields + the default file lines + the 6 Server Setup rows on the "Set drops" tab), addTo on
                 20,000 kills a case (Trork normal 4 % armor / 3 % weapon, every id of its list and nothing else; elite / mini / boss rank word,
                 the Chieftain by Boss roles, an Armored version = x3; a Kweebec Razorleaf 3 % head / chest; the wolves, a Skeleton, a neutral
                 Kweebec Sapling = nothing), eliteX capped at 100 %, all chances 0 = on() false + no roll, a missing item = counted + nothing
                 added, checkSetMobs, MobCfg.load from a REAL scratch file (edited values, clamps, a file without the lines = the defaults),
                 the ready text (MobEgg.text + set drops)
  W     wire     bytecode: SpoilsSys.tick gates on MobTheme.on() and calls MobTheme.addTo once, after MobVariant.extra and before
                 MobSpoils.spawn (the same list the Spoils spawn at the mob)
  EX123 0.1.23's exec + CreditSys phases EXECUTED on this jar (element states unchanged)
  D     live     start twice on a scratch COPY of Skyy's live Skyy_SkyyMobs: bytes untouched, no migration, the six rows read their defaults
  AA    engine-access audit
NOT COVERED (UNVERIFIED in game): SpoilsSys.tick inside the ECS death dispatch (its call is wired + executed here as MobTheme.addTo, like the
0.1.18 eggs); SkyyGear's death-drop mark tagging the spawned piece in the same tick (SkyyGear 0.3.54's harness executes GearTag.unid on it).
Scratch: tools/dev/scratch/gl2/mobs (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.1.24"
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "gl2", "mobs")]
import skyybuild as B
import harness_kit as HK

_run0 = HK.run
HK.run = lambda *a, **k: None          # import 0.1.23's harness (and through it 0.1.22's) for its phases without running it
_s = importlib.util.spec_from_file_location("test_skyymobs_0_1_23", os.path.join(HERE, "test_skyymobs_0.1.23.py"))
T23 = importlib.util.module_from_spec(_s)
_s.loader.exec_module(T23)
HK.run = _run0
T22 = T23.T22

GEN = os.path.join(HERE, "build_skyymobs_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyymobs_0.1.23.py")
PATCH = os.path.join(ROOT, "tools", "mobs_0_1_24_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMobs-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMobs-0.1.23.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.mobs."
TA = ["Armor_Trork_Head", "Armor_Trork_Chest", "Armor_Trork_Hands", "Armor_Trork_Legs"]
TW = ["Weapon_%s_Stone_Trork" % f for f in ("Axe", "Battleaxe", "Club", "Daggers", "Longsword", "Mace", "Spear", "Sword")]
KA = ["Armor_Kweebec_Head", "Armor_Kweebec_Chest"]
KEYS = ["drops.trork.mobs", "drops.trork.armor", "drops.trork.weapon", "drops.kweebec.mobs", "drops.kweebec.armor", "drops.eliteX"]
DEFS = ["Trork_*", "4", "3", "Kweebec_Razorleaf*", "3", "3"]
EXPECT = {
    "MobCfg": ["+f TH_ELITE", "+f TH_KARM", "+f TH_KMOBS", "+f TH_TARM", "+f TH_TMOBS", "+f TH_TWEAP", "~<clinit>", "~m apply", "~m load", "~m reloadAll", "~m useDefaults"],
    "MobEgg": ["~m text"],
    "MobHooks": ["+m checkSetMobs"],
    "SpoilsSys": ["~m tick"],
    "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "CfgFile": ["~<clinit>"],
    "SkyyMobsPlugin": ["~m setup"],
}
ADDED = ["MobTheme"]
if "--expect-dump" in sys.argv:
    EXPECT = {}


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyMobs 0.1.24 - build script') and g.count('VERSION = "0.1.24"') == 1, "S header + VERSION")
    K.eq([g.count(w) - o.count(w) for w in ("registerSystem(", "registerCommand(", "makeClass(")], [0, 0, 1], "S one new class (MobTheme), no system / command")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    K.eq((sorted(nb - na), sorted(na - nb)), (["com/skyy/mobs/MobTheme.class"], []), "S the jar adds only MobTheme.class, removes nothing")
    K.eq(sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n)), ["manifest.json"],
         "S every role / model / spawn / lang file byte-identical to 0.1.23 (only the manifest changes)")
    K.check(all(("('%s', " % k) in g for k in KEYS) and '("theme", "Set drops")' in g, "S the six rows + the Set drops tab are in the build")
    K.save()


def run_exec(out, jar, scratch, home):
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    C, T, H, Egg = JClass(PKG + "MobCfg"), JClass(PKG + "MobTheme"), JClass(PKG + "MobHooks"), JClass(PKG + "MobEgg")
    AL, RND = JClass("java.util.ArrayList"), JClass("java.util.Random")
    C.useDefaults()
    d = str(C.DEF_CFG)
    K.check(all(("\n%s=%s\n" % (k, v)) in d for k, v in zip(KEYS, DEFS)), "X the default file carries the six set drop lines")
    K.eq((str(C.TH_TMOBS), float(C.TH_TARM), float(C.TH_TWEAP), str(C.TH_KMOBS), float(C.TH_KARM), float(C.TH_ELITE)),
         ("Trork_*", 4.0, 3.0, "Kweebec_Razorleaf*", 3.0, 3.0), "X the field defaults")
    g = open(GEN, encoding="utf8").read()
    K.check("('drops.trork.armor', 'Trork armor piece chance', 'dec', '4', '0', '100'" in g and '"field:MobCfg.%s%s" % (_r[9], ";check=MobHooks.checkSetMobs"' in g,
            "X the rows (Server Setup > Mobs > Set drops, live; the role lists checked by MobHooks.checkSetMobs)")
    OK = {"on": True}

    @JImplements("java.util.function.Predicate")
    class Items(object):
        @JOverride
        def test(self, i):
            return OK["on"] and str(i) in TA + TW + KA
    T.ITEM_API = Items()
    N = 20000

    def run(role, rw, n=N, seed=7):
        rng = RND(seed)
        cnt = {}
        kills_a = kills_w = 0
        for _ in range(n):
            lst = AL()
            T.addTo(lst, role, rw, rng)
            ids = [str(lst.get(i)[0]) for i in range(lst.size())]
            q = [int(lst.get(i)[1]) for i in range(lst.size())]
            if any(x != 1 for x in q):
                cnt["qty!=1"] = cnt.get("qty!=1", 0) + 1
            for x in ids:
                cnt[x] = cnt.get(x, 0) + 1
            kills_a += 1 if any(x in TA or x in KA for x in ids) else 0
            kills_w += 1 if any(x in TW for x in ids) else 0
        return cnt, 100.0 * kills_a / n, 100.0 * kills_w / n

    def near(v, want, tol):
        return abs(v - want) <= tol
    res = {}
    for name, role, rw in (("trork", "Trork_Warrior", ""), ("trork elite", "Trork_Warrior", "elite"), ("trork mini", "Trork_Mauler", "mini"),
                           ("chieftain (Boss roles)", "Trork_Chieftain", ""), ("armored", "Trork_Warrior_SkyyArmored1", ""),
                           ("razorleaf", "Kweebec_Razorleaf", ""), ("razorleaf patrol elite", "Kweebec_Razorleaf_Patrol", "elite"),
                           ("wolf", "Wolf_Trork_Hunter", ""), ("skeleton", "Skeleton_Fighter", "elite"), ("sapling", "Kweebec_Sapling", "")):
        res[name] = run(role, rw)
    K.notes.append("X rates (armor %%, weapon %%) per %d kills: %s" % (N, dict((k, (round(v[1], 2), round(v[2], 2))) for k, v in res.items())))
    c, a, w = res["trork"]
    K.check(near(a, 4.0, 0.6) and near(w, 3.0, 0.5) and set(c) == set(TA + TW) and "qty!=1" not in c,
            "X a Trork Warrior: ~4 %% armor, ~3 %% weapon, every Trork armor / weapon id and nothing else, one item each: %.2f / %.2f %s" % (a, w, sorted(c)))
    for k in ("trork elite", "trork mini", "chieftain (Boss roles)", "armored"):
        c, a, w = res[k]
        K.check(near(a, 12.0, 1.0) and near(w, 9.0, 0.9) and set(c) <= set(TA + TW), "X %s rolls x3: %.2f %% armor / %.2f %% weapon" % (k, a, w))
    c, a, w = res["razorleaf"]
    K.check(near(a, 3.0, 0.5) and w == 0.0 and set(c) == set(KA), "X a Kweebec Razorleaf: ~3 %% Kweebec head / chest only: %.2f %s" % (a, sorted(c)))
    c, a, w = res["razorleaf patrol elite"]
    K.check(near(a, 9.0, 0.9) and set(c) == set(KA), "X an elite Razorleaf patrol x3: %.2f" % a)
    for k in ("wolf", "skeleton", "sapling"):
        K.eq(res[k][0], {}, "X %s drops nothing from the set rows" % k)
    # the cap, off, missing item, the null guards
    C.TH_TARM, C.TH_ELITE = 40.0, 10.0
    c, a, w = run("Trork_Warrior", "elite", n=500)
    K.check(a == 100.0, "X 40 %% x eliteX 10 is capped at 100 %%: %.1f" % a)
    C.TH_TARM, C.TH_TWEAP, C.TH_KARM, C.TH_ELITE = 0.0, 0.0, 0.0, 3.0
    r0 = int(T.ROLLS)
    lst = AL()
    K.check(not bool(T.on()) and int(T.addTo(lst, "Trork_Warrior", "elite", RND(1))) == 0 and lst.size() == 0 and int(T.ROLLS) == r0,
            "X all three chances 0 = on() false, no roll (SpoilsSys stays asleep for it)")
    C.TH_TARM, C.TH_TWEAP, C.TH_KARM = 100.0, 0.0, 0.0
    OK["on"] = False
    m0 = int(T.MISSING)
    lst = AL()
    T.addTo(lst, "Trork_Warrior", "", RND(1))
    K.check(lst.size() == 0 and int(T.MISSING) == m0 + 1, "X an item the server lacks = counted MISSING, nothing added (one WARN)")
    OK["on"] = True
    K.check(int(T.addTo(None, "Trork_Warrior", "", RND(1))) == 0 and int(T.addTo(AL(), None, "", RND(1))) == 0 and int(T.addTo(AL(), "Trork_Warrior", "", None)) == 0,
            "X null list / role / random = 0")
    C.TH_TMOBS = "Goblin_*"
    lst = AL()
    T.addTo(lst, "Goblin_Scrapper", "", RND(1))
    K.check(lst.size() == 1 and str(lst.get(0)[0]) in TA, "X drops.trork.mobs is read live (Goblin_* now drops Trork armor)")
    C.useDefaults()
    # the check hook
    ck = dict((v, H.checkSetMobs("drops.trork.mobs", v)) for v in ("Trork_*", "Trork_*, Goblin_Duke", "*", "Trork_*=x", "Trork *", " , Trork_Warrior"))
    K.check(ck["Trork_*"] is None and ck["Trork_*, Goblin_Duke"] is None and ck[" , Trork_Warrior"] is None and ck["*"] is not None and ck["Trork_*=x"] is not None
            and ck["Trork *"] is not None and H.checkSetMobs("drops.trork.mobs", None) is None, "X checkSetMobs: roles / Prefix* ok; *, '=', spaces refused; null = default: %s" % dict((k, None if v is None else str(v)) for k, v in ck.items()))
    # MobCfg.load from a real scratch file
    P_ = JClass("java.nio.file.Paths")
    sd = os.path.join(scratch, "cfg")
    os.makedirs(sd, exist_ok=True)
    fp = os.path.join(sd, "config.properties")
    base = d.replace("\ndrops.trork.armor=4\n", "\ndrops.trork.armor=7.5\n").replace("\ndrops.eliteX=3\n", "\ndrops.eliteX=99\n").replace("\ndrops.kweebec.mobs=Kweebec_Razorleaf*\n", "\ndrops.kweebec.mobs=Kweebec_*\n")
    open(fp, "w", encoding="latin-1", newline="").write(base)
    C.DIR = P_.get(sd)
    C.FILE = P_.get(fp)
    C.BANDS = P_.get(os.path.join(sd, "bands.properties"))
    C.load()
    K.eq((float(C.TH_TARM), float(C.TH_ELITE), str(C.TH_KMOBS)), (7.5, 10.0, "Kweebec_*"), "X MobCfg.load reads the file: 7.5 %, eliteX 99 clamped to 10, a hand-edited list")
    strip = "\n".join(l for l in d.split("\n") if not l.startswith("drops."))
    open(fp, "w", encoding="latin-1", newline="").write(strip)
    b0 = open(fp, "rb").read()
    C.load()
    K.eq((str(C.TH_TMOBS), float(C.TH_TARM), float(C.TH_TWEAP), str(C.TH_KMOBS), float(C.TH_KARM), float(C.TH_ELITE)),
         ("Trork_*", 4.0, 3.0, "Kweebec_Razorleaf*", 3.0, 3.0), "X a file without the six lines = the defaults (no migration)")
    K.check(open(fp, "rb").read() == b0, "X ... and the file is not rewritten")
    t = str(Egg.text())
    K.check("; set drops: Trork armor 4.0 % / weapon 3.0 %, Kweebec 3.0 %, elites x3.0" in t, "X the ready text (MobEgg.text) names the set drops: %s" % t[-120:])
    K.save()


def run_wire(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.JAVASSIST], verify=False)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(jar)
    m = [x for x in cp.get(PKG + "SpoilsSys").getDeclaredMethods() if str(x.getName()) == "tick" and len(x.getParameterTypes()) == 5]
    seq = []
    ci = m[0].getMethodInfo().getCodeAttribute().iterator()
    cpl = m[0].getMethodInfo().getConstPool()
    while ci.hasNext():
        pos = ci.next()
        if ci.byteAt(pos) == 0xb8:
            seq.append(str(cpl.getMethodrefClassName(ci.u16bitAt(pos + 1))).rsplit(".", 1)[1] + "." + str(cpl.getMethodrefName(ci.u16bitAt(pos + 1))))
    K.check(seq.count("MobTheme.on") == 1 and seq.index("MobTheme.on") < seq.index("MobSpoils.first"), "W SpoilsSys.tick gates on MobTheme.on() before the once-per-death check")
    K.check(seq.count("MobTheme.addTo") == 1 and seq.index("MobVariant.extra") < seq.index("MobTheme.addTo") < seq.index("MobSpoils.spawn"),
            "W SpoilsSys.tick: MobVariant.extra -> MobTheme.addTo -> MobSpoils.spawn (the same list): %s" % seq)
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Cfg, Sp, Sc = JClass(PKG + "MobCfg"), JClass(PKG + "MobSpoils"), JClass(PKG + "MobSecret")
    P_ = JClass("java.nio.file.Paths")
    files = [f for f in ("config.properties", "bands.properties", "trees.properties") if os.path.isfile(os.path.join(home, f))]
    before = dict((f, open(os.path.join(home, f), "rb").read()) for f in files)
    K.check("config.properties" in files and b"drops.trork" not in before["config.properties"], "D the live copy has a config.properties without set drop lines")

    def start():
        Cfg.DIR = P_.get(home)
        Cfg.FILE = P_.get(os.path.join(home, "config.properties"))
        Cfg.BANDS = P_.get(os.path.join(home, "bands.properties"))
        o = "".join(str(JClass(PKG + m).run(P_.get(home))) for m in ("MobMig", "MobMig14", "MobMig11", "MobMig12", "MobMigP4"))
        o += str(Sp.migrateWc15(P_.get(home)))
        Cfg.load()
        Sp.loadV3(P_.get(home))
        Sc.load(P_.get(home))
        return o

    def vals():
        return (str(Cfg.TH_TMOBS), float(Cfg.TH_TARM), float(Cfg.TH_TWEAP), str(Cfg.TH_KMOBS), float(Cfg.TH_KARM), float(Cfg.TH_ELITE))
    DEF = ("Trork_*", 4.0, 3.0, "Kweebec_Razorleaf*", 3.0, 3.0)
    o1 = start()
    K.eq(vals(), DEF, "D start 1: no set drop lines in the live file -> the defaults")
    K.eq(dict((f, open(os.path.join(home, f), "rb").read() == before[f]) for f in files), dict((f, True) for f in files),
         "D start 1: config / bands / trees bytes untouched (no migration; older updates said %r)" % o1[:60])
    o2 = start()
    K.eq((o2, vals()), ("", DEF), "D start 2: nothing migrates, the same values")
    K.eq(dict((f, open(os.path.join(home, f), "rb").read() == before[f]) for f in files), dict((f, True) for f in files), "D start 2: bytes still untouched")
    K.save()


HK.run_compare = T22._cmp
if __name__ == "__main__":
    HK.run("SkyyMobs", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("static", run_static), ("exec", run_exec), ("wire", run_wire), ("ex123", T23.run_exec), ("cs123", T23.run_cs), ("live", run_live)], __file__,
           live=(T22.LIVE_DIR, "Skyy_SkyyMobs"))
