"""Harness for SkyyMobs 0.1.19 (wc15: the five Spoils (Weaponcraft) rows x1.5 + the one-time trees.properties update - tools/mobs_0_1_19_patch.py,
tools/wc15.py).
Build first:
    python tools/mobs_0_1_19_patch.py && python SkyyMobs/build_skyymobs_0.1.19.py
    python SkyyMobs/test_skyymobs_0.1.19.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  S     static   the patch re-runs to identical bytes (--out), line endings kept, no new class / command / system; only the manifest of the
                 non-class entries changes
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.1.18 -> 0.1.19 (EXPECT below)
  X     exec     EXECUTES in a bare JVM: MobSpoils' built-in numbers = x1.5 (3 / 4.5 / 1.5 / 4.5 / 3, ceilings 15 / 13.5 / 4.5 / 13.5 / 9);
                 tools/wc15_harness.py exec_update + exec_migrate; vals at max rank; THE RATE PROOF at the new numbers (20,000 kills + 4,000
                 boss kills, seeded, every row maxed, a drop list with gear in it): Scavenger ~15 %, Rare Drop ~4.5 %, Lucky Kill ~9 %, Coin Purse
                 ~13.5 %, Boss Hunter ~13.5 % on bosses / 0 on plain mobs, 0 gear stacks out (SkyyGear's UT / Mythic rolls untouched);
                 rank 1 each = 3 / 4.5 / 1.5 / 4.5 / 3
  EX118 0.1.18's exec phase EXECUTED on this jar (the dragon eggs unchanged)
  D     live     start twice on a scratch COPY of Skyy's live NewBetaTest Skyy_SkyyMobs: start 1 moves only the trees.properties lines on the
                 0.1.18 defaults (+ marker, History copy, change log), start 2 changes nothing; MobSpoils.loadV3 reads the new numbers
  AA    engine-access audit
NOT COVERED (UNVERIFIED in game): SpoilsSys.tick inside the ECS death dispatch (it calls MobSpoils.extra / coins, executed here - unchanged
code), the /tree page text (SkyyTrees' own text still says the old numbers - a SkyyTrees round).
Scratch: tools/dev/scratch/wc15/mobs (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.1.19"
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "wc15", "mobs")]
import skyybuild as B
import harness_kit as HK
import trees_v3_effects as V3E
import wc15 as WC
import wc15_harness as WH

_run0 = HK.run
HK.run = lambda *a, **k: None          # import 0.1.18's harness for its exec phase without running it
_s = importlib.util.spec_from_file_location("test_skyymobs_0_1_18", os.path.join(HERE, "test_skyymobs_0.1.18.py"))
T118 = importlib.util.module_from_spec(_s)
_s.loader.exec_module(T118)
HK.run = _run0

GEN = os.path.join(HERE, "build_skyymobs_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyymobs_0.1.18.py")
PATCH = os.path.join(ROOT, "tools", "mobs_0_1_19_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMobs-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMobs-0.1.18.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.mobs."
LIVE_DIR = T118.LIVE_DIR
ADDED = []
EXPECT = {
    "MobSpoils": ["+f WC_KEY", "+f WC_MARK", "+f WC_MARK_ID", "+f WC_NEW", "+f WC_NEWN", "+f WC_OLD", "+f WC_OLDT", "+f WC_WHO",
                  "+m migrateWc15", "+m wcEq", "+m wcFile", "+m wcKit", "+m wcLog", "+m wcNum", "+m wcSame", "+m wcSaved", "+m wcUpdate",
                  "~<clinit>", "~m loadV3"],
    "SkyyMobsPlugin": ["~m setup"],
    "MobCfg": ["~m load", "~m reloadAll", "~m useDefaults"],          # the version in the config.properties / bands.properties head text
    "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
T118.PKG = PKG
U = "00000000-0000-0000-0000-000000000119"


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyMobs 0.1.19 - build script') and g.count('VERSION = "0.1.19"') == 1, "S header + VERSION")
    K.eq((g.count("registerSystem(") - o.count("registerSystem("), g.count("registerCommand(") - o.count("registerCommand("),
          g.count("makeClass(") - o.count("makeClass(")), (0, 0, 0), "S no new system / command / class")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    K.eq((sorted(nb - na), sorted(na - nb)), ([], []), "S no jar entry added / removed")
    K.eq(sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n)), ["manifest.json"], "S the only non-class change is the manifest")
    K.save()


def run_exec(out, jar, scratch, home):
    from jpype import JClass, JImplements, JOverride, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    S = JClass(PKG + "MobSpoils")
    WC.apply(V3E, "SkyyMobs")
    rows = V3E.rows("SkyyMobs")
    K.eq([str(x) for x in S.KEY], [V3E.key(e[0], e[1], e[2]) for e in rows], "X MobSpoils.KEY unchanged (the 5 Spoils keys)")
    K.eq([float(S.v3per(i)) for i in range(5)], [3.0, 4.5, 1.5, 4.5, 3.0], "X per rank x1.5: Scavenger 3, Coin Purse 4.5, Rare Drop 1.5, Boss Hunter 4.5, Lucky Kill 3 (was 2 / 3 / 1 / 3 / 2)")
    K.eq([float(S.v3most(i)) for i in range(5)], [15.0, 13.5, 4.5, 13.5, 9.0], "X ceilings x1.5: 15 / 13.5 / 4.5 / 13.5 / 9 (was 10 / 9 / 3 / 9 / 6)")
    WH.exec_update(K, S, "SkyyMobs")
    WH.exec_migrate(K, S, "SkyyMobs", os.path.join(scratch, "mig", "Skyy_SkyyMobs"))
    S.loadV3(JClass("java.nio.file.Paths").get(os.path.join(scratch, "fresh")))          # a fresh file = the built-in numbers
    K.eq([float(S.v3per(i)) for i in range(5)], [3.0, 4.5, 1.5, 4.5, 3.0], "X a fresh trees.properties reads back the new numbers")
    uu = JClass("java.util.UUID").fromString(U)
    RK = {}
    CN = {"gear": 0, "coins": []}

    @JImplements("java.util.function.Function")
    class Lvl(object):
        @JOverride
        def apply(self, a):
            return JClass("java.lang.Integer")(RK.get(str(a[1]), 0))

    @JImplements("java.util.function.Function")
    class Spy(object):
        @JOverride
        def apply(self, a):
            CN["gear"] += 1
            return None

    @JImplements("java.util.function.Function")
    class Coins(object):
        @JOverride
        def apply(self, a):
            CN["coins"].append((str(a[0]), int(a[1])))
            return JClass("java.lang.Long")(1)
    OA = JClass("java.lang.Object[]")
    Int = JClass("java.lang.Integer")
    import random
    rr = random.Random(19)

    @JImplements("java.util.function.Function")
    class Rolls(object):
        @JOverride
        def apply(self, dl):
            l = JClass("java.util.ArrayList")()
            for it in [("Ingredient_Bone", 2), ("Ingredient_Hide_Light", 1), ("Weapon_Sword_Iron", 1), ("Armor_Iron_Head", 1), ("Tool_Pickaxe_Iron", 1),
                       ("Skyy_Unid_Bag_Rare", 1), ("Weapon_Shield_Iron", 1)] + ([("Rock_Gem_Ruby", 1)] if rr.random() < 0.1 else []):
                l.add(OA([JString(it[0]), Int(it[1])]))
            return l
    for g in ("gear:fn:box", "gear:fn:grant", "gear:fn:unid", "gear:fn:utdrop", "gear:fn:mythic"):
        br.put(g, Spy())
    S.ROLLS = Rolls()
    R = JClass("java.util.Random")
    S.C.clear()
    K.eq((int(S.extra(uu, "DL", True, R(1)).size()), int(S.coins(uu, 30, R(1)))), (0, 0), "X no SkyyTrees: no extra loot, no coins")
    br.put("tree:fn:level", Lvl())
    for e in rows:
        RK[V3E.key(e[0], e[1], e[2])] = 1
    S.C.clear()
    K.eq([round(float(x), 6) for x in list(S.vals(uu))[1:]], [3.0, 4.5, 1.5, 4.5, 3.0], "X vals at rank 1: drop 3, coins 4.5, rare 1.5, bossRoll 4.5, dbl 3")
    for e in rows:
        RK[V3E.key(e[0], e[1], e[2])] = V3E.maxrank(e[0], e[1], e[2])
    S.C.clear()
    K.eq([round(float(x), 6) for x in list(S.vals(uu))[1:]], [15.0, 13.5, 4.5, 13.5, 9.0], "X vals at max: drop 15, coins 13.5, rare 4.5, bossRoll 13.5, dbl 9 (was 10 / 9 / 3 / 9 / 6)")
    RK[V3E.key(rows[0][0], rows[0][1], rows[0][2])] = 99
    S.C.clear()
    K.eq(round(float(S.vals(uu)[1]), 6), 15.0, "X a rank above the max stops at the ceiling (15)")
    RK[V3E.key(rows[0][0], rows[0][1], rows[0][2])] = 5
    # THE RATE PROOF at the new numbers: 20,000 kills + 4,000 boss kills, every row maxed, a drop list with gear in it
    br.put("coins:fn:add", Coins())
    rnd = R(20261024)
    gear_out, items = 0, 0
    S.C.clear()
    n0 = dict((k, int(getattr(S, k))) for k in ("N_DROP", "N_RARE", "N_BOSS", "N_DBL", "N_GEAR", "N_KILLS"))
    for i in range(20000):
        l = S.extra(uu, "DL_Mob", False, rnd)
        S.coins(uu, 30, rnd)
        for j in range(int(l.size())):
            if bool(S.gear(str(S.pid(l.get(j))))):
                gear_out += 1
            items += int(S.pn(l.get(j)))
    d = dict((k, int(getattr(S, k)) - n0[k]) for k in n0)
    nb0 = int(S.N_BOSS)
    for i in range(4000):
        l = S.extra(uu, "DL_Boss", True, rnd)
        for j in range(int(l.size())):
            if bool(S.gear(str(S.pid(l.get(j))))):
                gear_out += 1
    nb = int(S.N_BOSS) - nb0
    K.check(abs(d["N_DROP"] / 200.0 - 15.0) < 1.0 and abs(d["N_RARE"] / 200.0 - 4.5) < 0.6 and abs(d["N_DBL"] / 200.0 - 9.0) < 0.8 and d["N_BOSS"] == 0,
            "X 20,000 kills: Scavenger %.2f %% (15), Rare Drop %.2f %% (4.5), Lucky Kill %.2f %% (9), Boss Hunter 0 on plain mobs" % (d["N_DROP"] / 200.0, d["N_RARE"] / 200.0, d["N_DBL"] / 200.0))
    K.check(abs(nb / 40.0 - 13.5) < 1.6, "X 4,000 boss / mini boss kills: Boss Hunter %.2f %% (13.5)" % (nb / 40.0))
    K.check(abs(len(CN["coins"]) / 200.0 - 13.5) < 0.9 and all(c == (U, 30) for c in CN["coins"]), "X Coin Purse %.2f %% (13.5) of 20,000 kills, each the mob's level (30) to the killer" % (len(CN["coins"]) / 200.0))
    K.eq((gear_out, CN["gear"]), (0, 0), "X 0 gear stacks out of %d extra items, 0 gear:fn:* calls (SkyyGear's UT meter + Mythic roll untouched)" % items)
    K.notes.append("X extra items a plain kill, every row maxed: %.3f (0.1.18 harness at the old numbers: ~2/3 of this)" % (items / 20000.0))
    br.remove("tree:fn:level")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    Cfg, S = JClass(PKG + "MobCfg"), JClass(PKG + "MobSpoils")
    P = JClass("java.nio.file.Paths")
    hd = os.path.join(home, "config-history")
    b0 = set(x for x in os.listdir(hd) if "trees.properties." in x) if os.path.isdir(hd) else set()
    tf = os.path.join(home, "trees.properties")
    tb = open(tf, "rb").read() if os.path.isfile(tf) else None
    Cfg.DIR = P.get(home)
    Cfg.FILE = P.get(os.path.join(home, "config.properties"))
    Cfg.BANDS = P.get(os.path.join(home, "bands.properties"))

    def load():
        o = "".join(str(JClass(PKG + m).run(P.get(home))) for m in ("MobMig", "MobMig14", "MobMig11", "MobMig12", "MobMigP4"))
        K.check(o == "", "D the older one-time updates do nothing on the live copy (%r)" % o[:80])
        Cfg.load()
        K.check(str(S.loadV3(P.get(home))).endswith("read"), "D MobSpoils.loadV3 reads trees.properties")
    moved, pb, pa = WH.live_twice(K, S, "SkyyMobs", home, load)
    if tb is not None:
        b1 = set(x for x in os.listdir(hd) if "trees.properties." in x)
        new = sorted(b1 - b0)
        K.check(len(new) == 1 and open(os.path.join(hd, new[0]), "rb").read() == tb, "D History: the live trees.properties kept once, exact bytes (%s)" % new)
        lg = open(os.path.join(home, "config-changes.log"), encoding="utf8").read().splitlines()
        K.eq(sum(1 for l in lg if "\tSkyyMobs 0.1.19 update (wc15)\t" in l), len(moved), "D change log: one Undo line per moved live line")
    WC.apply(V3E, "SkyyMobs")
    for i, e in enumerate(V3E.rows("SkyyMobs")):
        k = V3E.ckey(e) + ".per"
        want = float(pa[k]) if k in pa else e[5]
        K.check(abs(float(S.v3per(i)) - want) < 1e-9, "D MobSpoils after load: %s = %s" % (k, float(S.v3per(i))))
    K.save()


HK.run("SkyyMobs", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("static", run_static), ("exec", run_exec), ("ex118", T118.run_exec), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyMobs"))
