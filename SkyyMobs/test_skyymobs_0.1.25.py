"""Harness for SkyyMobs 0.1.25 (augments round A3 = aug3, the SkyyMobs part: augment drops by zone / element / rank - MobAug, rolled by
SpoilsSys; the zone element for tougher versions - MobElem.zoneOwn; more element bodies incl. the Slime Mobs! roles; tools/mobs_0_1_25_patch.py).
Build first:
    python tools/mobs_0_1_25_patch.py && python SkyyMobs/build_skyymobs_0.1.25.py
    python SkyyMobs/test_skyymobs_0.1.25.py [--keep] [--expect-dump]

Phases (fresh child JVMs, tools/harness_kit.py):
  S     static   the patch re-runs to identical bytes (--out), line endings kept, ONE new class (MobAug), no new system / command; the jar adds
                 only MobAug.class and changes no role / model / spawn / lang file (only the manifest)
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.1.24 -> 0.1.25 (EXPECT below)
  X     exec     EXECUTES MobAug: the defaults (fields, default file lines, the 15 rows on the Augments tab + elem.zoneVariants), zoneOf
                 (environment first, then the level, capped at 5), zoneElem, weights, pick, addTo on 40,000 kills a case (an ordinary Zone 1
                 mob 2.4 %, a Zone 1 Earth mob 4.0 %, a Zone 3 Water slime 4.0 %, elite x3 + 2 % stat, mini x3 + 10 % stat, a full boss
                 1 stat + 1 element + 50 % one more, a tougher version = its zone element, unlevelled / no zone = nothing), tiers = the zone,
                 every id one of tools/tier_tags.py AUG_IDS (no Poison, no T6+), the cap at 100 %, off, a missing item, the null guards;
                 MobElem: zoneOwn / ownOf / mod / mob:fn:elemOf for tougher versions (+ a row keeps its element, elem.zoneVariants off,
                 a zone row edit), the new element rows (vanilla + Slime Mobs! roles); checkZoneElem; MobCfg.load from a REAL scratch file
                 (edits, clamps, a file without the lines = the defaults); the ready text
                 aug3fix: the zone mix (elem.zoneMix 60 / 0 / 100, every tougher version = the mix rule, Zone 1 has all 5 elements,
                 an Air one in Zone 1 by mod / elemOf, a zone row edit / none, an id not in the table, the file clamp)
  W     wire     bytecode: SpoilsSys.tick gates on MobAug.on() before the once-per-death check and calls MobLevel.envId + MobAug.addTo once,
                 after MobTheme.addTo and before MobSpoils.spawn (the same list the Spoils spawn at the mob)
                 aug3fix: MobAug.addTo sits in its OWN catch (exception table), so a throw never skips the egg / spawn / secret finds
  EX124 0.1.24's exec (set drops) + 0.1.23's exec + CreditSys phases EXECUTED on this jar
  D     live     start twice on a scratch COPY of Skyy's live Skyy_SkyyMobs: bytes untouched, no migration, the new rows read their defaults
  AA    engine-access audit
NOT COVERED (UNVERIFIED in game): SpoilsSys.tick inside the ECS death dispatch (its call is wired + executed here as MobAug.addTo, like the
0.1.18 eggs / 0.1.24 set drops); NPCEntity.getEnvironment() at the death spot; SkyySacks claiming the spawned augment for its owner.
Scratch: tools/dev/scratch/aug3/mobs (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.1.25"
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "aug3", "mobs")]
import skyybuild as B
import harness_kit as HK
import tier_tags as TT

_run0 = HK.run
HK.run = lambda *a, **k: None          # import 0.1.24's harness (and through it 0.1.23's / 0.1.22's) for its phases without running it
_s = importlib.util.spec_from_file_location("test_skyymobs_0_1_24", os.path.join(HERE, "test_skyymobs_0.1.24.py"))
T24 = importlib.util.module_from_spec(_s)
_s.loader.exec_module(T24)
HK.run = _run0
T23, T22 = T24.T23, T24.T22

GEN = os.path.join(HERE, "build_skyymobs_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyymobs_0.1.24.py")
PATCH = os.path.join(ROOT, "tools", "mobs_0_1_25_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMobs-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMobs-0.1.24.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.mobs."
STAT = [k for k in TT.AUG_KINDS if TT.AUG_TIERS[k] == 5 and k != "Poison"]
ELEM = ["Earth", "Thunder", "Water", "Fire", "Air"]
KEYS = ["aug.drop.on", "aug.drop.base", "aug.drop.elemMob", "aug.drop.primary", "aug.drop.eliteX", "aug.drop.statElite", "aug.drop.statMini",
        "aug.drop.bossStat", "aug.drop.bossElem", "aug.drop.bossBonus"] + ["aug.zoneElement.%d" % z for z in range(1, 6)] + ["elem.zoneVariants", "elem.zoneMix"]
DEFS = ["true", "0.4", "3", "2", "3", "2", "10", "1", "1", "50", "Earth", "Thunder", "Water", "Fire", "Air", "true", "60"]
EXPECT = {
    "MobCfg": ["+f AUG_BASE", "+f AUG_BBONUS", "+f AUG_BELEM", "+f AUG_BSTAT", "+f AUG_ELITE", "+f AUG_EMOB", "+f AUG_ON", "+f AUG_PRIM",
               "+f AUG_SELITE", "+f AUG_SMINI", "+f AUG_Z1", "+f AUG_Z2", "+f AUG_Z3", "+f AUG_Z4", "+f AUG_Z5", "+f ELEM_ZMIX", "+f ELEM_ZVAR",
               "~<clinit>", "~m apply", "~m derive", "~m load", "~m reloadAll", "~m useDefaults"],
    "MobElem": ["+f ZM_IDS", "+f ZM_O", "+f ZM_U", "+f ZOWN", "+m zoneOwn", "~<clinit>", "~m derive", "~m mod", "~m ownOf"],
    "MobEgg": ["~m text"],
    "MobHooks": ["+m checkZoneElem"],
    "SpoilsSys": ["~m tick"],
    "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "CfgFile": ["~<clinit>"],
    "SkyyMobsPlugin": ["~m setup"],
}
ADDED = ["MobAug"]
if "--expect-dump" in sys.argv:
    EXPECT = {}


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyMobs 0.1.25 - build script') and g.count('VERSION = "0.1.25"') == 1, "S header + VERSION")
    K.eq([g.count(w) - o.count(w) for w in ("registerSystem(", "registerCommand(", "makeClass(")], [0, 0, 1], "S one new class (MobAug), no system / command")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    K.eq((sorted(nb - na), sorted(na - nb)), (["com/skyy/mobs/MobAug.class"], []), "S the jar adds only MobAug.class, removes nothing")
    K.eq(sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n)), ["manifest.json"],
         "S every role / model / spawn / lang file byte-identical to 0.1.24 (only the manifest changes; spawn weights untouched)")
    K.check(all(("('%s', " % k) in g for k in KEYS) and '("aug", "Augments")' in g, "S the 17 rows + the Augments tab are in the build")
    K.check("AUG_STAT_KINDS = %r" % STAT in g and "Poison" not in repr(STAT), "S the stat kinds = tools/tier_tags.py's 13 (Poison stays craft-only)")
    K.save()


def run_exec(out, jar, scratch, home):
    from jpype import JClass, JImplements, JOverride, JString, JArray, JDouble
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    C, A, E, H, Egg = JClass(PKG + "MobCfg"), JClass(PKG + "MobAug"), JClass(PKG + "MobElem"), JClass(PKG + "MobHooks"), JClass(PKG + "MobEgg")
    AL, RND = JClass("java.util.ArrayList"), JClass("java.util.Random")
    C.useDefaults()
    d = str(C.DEF_CFG)
    K.check(all(("\n%s=%s\n" % (k, v)) in d for k, v in zip(KEYS, DEFS)), "X the default file carries the 17 new lines")

    def vals():
        return (bool(C.AUG_ON), float(C.AUG_BASE), float(C.AUG_EMOB), float(C.AUG_PRIM), float(C.AUG_ELITE), float(C.AUG_SELITE), float(C.AUG_SMINI),
                int(C.AUG_BSTAT), int(C.AUG_BELEM), float(C.AUG_BBONUS), str(C.AUG_Z1), str(C.AUG_Z2), str(C.AUG_Z3), str(C.AUG_Z4), str(C.AUG_Z5), bool(C.ELEM_ZVAR), int(C.ELEM_ZMIX))
    DEFV = (True, 0.4, 3.0, 2.0, 3.0, 2.0, 10.0, 1, 1, 50.0, "Earth", "Thunder", "Water", "Fire", "Air", True, 60)
    K.eq(vals(), DEFV, "X the field defaults (spec 2.4 / N3: Z1 Earth ... Z5 Air)")
    g = open(GEN, encoding="utf8").read()
    K.check("check=MobHooks.checkZoneElem" in g and "'field:MobCfg.ELEM_ZVAR;after=MobCfg.elemEdit'" in g, "X the zone rows are checked + re-derive the elements (live)")
    OK = {"on": True}
    IDS = set(TT.AUG_IDS)

    @JImplements("java.util.function.Predicate")
    class Items(object):
        @JOverride
        def test(self, i):
            return OK["on"] and str(i) in IDS
    A.ITEM_API = Items()
    # ---- zones
    zc = [(None, 5, 1), ("Env_Zone3_Tundra", 5, 3), ("Env_Zone1_Plains", 22, 1), (None, 25, 2), (None, 41, 3), (None, 79, 4), (None, 85, 5),
          (None, 120, 5), ("Env_Zone7_Test", 3, 5), (None, 0, 0), ("Env_Default_Void", 0, 0), ("Env_Default_Void", 33, 2)]
    got = [int(A.zoneOf(e, l)) for e, l, _w in zc]
    K.eq(got, [w for _e, _l, w in zc], "X zoneOf: the environment first (an Armored Zone 1 mob at Lv 22 stays Zone 1), else the level (20/40/60/80/100), capped at 5, none = 0")
    K.eq([int(A.zoneElem(z)) for z in range(0, 7)], [-1, 0, 1, 2, 3, 4, -1], "X zoneElem: Z1 Earth ... Z5 Air (MobElem order), no zone = -1")
    # ---- MobElem: the element of a role (rows, the new rows, tougher versions); elem.zoneMix 100 = every element-less tougher version takes it
    C.ELEM_ZMIX = 100
    own = dict((r, int(E.ownOf(r))) for r in ("Trork_Warrior", "Skeleton_Fighter_SkyyArmored1", "Skeleton_Fighter_SkyyVeteran3", "Skeleton_Sand_Soldier_SkyyArmored2",
                                             "Skeleton_Frost_Archer_SkyyArmored4", "Crocodile", "Bat", "Bat_Ice", "Lizard_Sand", "Green_Slime", "Yellow_Slime", "Water_Slime",
                                             "Ice_Slime", "Fire_Slime", "Bomb_Slime", "Ghost_Slime", "King_Slime", "Skeleton_Fighter"))
    K.eq(own, {"Trork_Warrior": -1, "Skeleton_Fighter_SkyyArmored1": 0, "Skeleton_Fighter_SkyyVeteran3": 2, "Skeleton_Sand_Soldier_SkyyArmored2": 0,
               "Skeleton_Frost_Archer_SkyyArmored4": 2, "Crocodile": 2, "Bat": 4, "Bat_Ice": 2, "Lizard_Sand": 0, "Green_Slime": 0, "Yellow_Slime": 1,
               "Water_Slime": 2, "Ice_Slime": 2, "Fire_Slime": 3, "Bomb_Slime": 3, "Ghost_Slime": 4, "King_Slime": -1, "Skeleton_Fighter": -1},
         "X ownOf: a tougher version without a row = its zone element (Z1 Earth, Z3 Water); a row wins (Sand = Earth in Zone 2, Frost = Water in Zone 4); new rows")
    K.eq([int(E.mod("Skeleton_Fighter_SkyyArmored1", e)) for e in range(5)], [-25, 0, 0, 0, 25], "X mod: a Zone 1 tougher version resists Earth, is weak to Air (the pure wheel)")
    K.eq([int(E.mod("Skeleton_Fighter", e)) for e in range(5)], [0, 0, 0, 0, 0], "X mod: its plain vanilla role stays element-less")
    eo = JClass(PKG + "MobElemOfFn")()
    K.eq((str(eo.apply(JString("Skeleton_Fighter_SkyyArmored1"))), eo.apply(JString("Skeleton_Fighter")), str(eo.apply(JString("Water_Slime")))),
         ("Earth", None, "Water"), "X mob:fn:elemOf (SkyyGear / SkyyClasses read it) agrees")
    K.check(str(E.word("Skeleton_Fighter_SkyyArmored1")) == "Earth" and bool(E.ANY), "X the plate word = Earth; MobElem.ANY on")
    C.AUG_Z1 = "Fire"
    C.elemEdit("aug.zoneElement.1")
    K.eq((int(E.ownOf("Skeleton_Fighter_SkyyArmored1")), int(A.zoneElem(1))), (3, 3), "X a zone row edit (Fire) re-derives at once (elemEdit)")
    C.ELEM_ZVAR = False
    C.elemEdit("elem.zoneVariants")
    K.eq((int(E.ownOf("Skeleton_Fighter_SkyyArmored1")), int(E.mod("Skeleton_Fighter_SkyyArmored1", 4)), int(E.ownOf("Skeleton_Sand_Soldier_SkyyArmored2"))), (-1, 0, 0),
         "X elem.zoneVariants off: tougher versions without a row have no element again (rows unchanged)")
    C.useDefaults()
    # ---- aug3fix: the zone mix (elem.zoneMix 60: the zone element for ~60 % of the element-less tougher versions' spawns, the rest the 4 others)
    zi, zu, zo = [str(x) for x in E.ZM_IDS], [float(x) for x in E.ZM_U], [int(x) for x in E.ZM_O]
    K.check(len(zi) == len(zu) == len(zo) > 40 and zi == sorted(zi) and all(0.0 < x < 1.0 for x in zu) and set(zo) <= {0, 1, 2, 3}
            and "Skeleton_Fighter_SkyyArmored1" in zi and not [x for x in zi if x.startswith("Skeleton_Sand")], "X FIX the zone-mix table: %d sorted ids (no Sand rows), u in (0,1), o 0-3" % len(zi))

    def mirror(role, prs, mix):
        i = zi.index(role)
        p_ = prs[int(role[-1])]
        if p_ < 0:
            return -1
        if zu[i] * 100.0 < mix:
            return p_
        return [e for e in range(5) if e != p_][zo[i]]
    PRS = [-1, 0, 1, 2, 3, 4]
    K.eq([int(E.ownOf(r)) for r in zi], [mirror(r, PRS, 60) for r in zi], "X FIX ownOf of every tougher version at the defaults = the mix rule (u < 60 % -> zone element, else the o-th other)")
    by = {}
    for r in zi:
        by.setdefault(int(r[-1]), {})
        e = int(E.ownOf(r))
        by[int(r[-1])][e] = by[int(r[-1])].get(e, 0) + 1
    K.notes.append("X FIX zone mix 60 per zone (element index: roles): %s" % by)
    K.check(all(sorted(by[z]) == [0, 1, 2, 3, 4] for z in (1, 3, 4)), "X FIX2 Zones 1, 3, 4 tougher versions: a role of EVERY element at the default: %s" % by)
    tail = {}
    for r in zi:          # aug3fix2: the coverage tail = the 4 roles of each zone at u in (0.60, 0.605] or naturally above; none of them is the zone element at 60
        if int(E.ownOf(r)) != PRS[int(r[-1])]:
            tail.setdefault(int(r[-1]), set()).add(int(E.ownOf(r)))
    K.check(all(len(tail[z]) == 4 for z in (1, 3, 4)), "X FIX2 the off-zone roles cover the 4 other elements in each zone: %s" % tail)
    C.ELEM_ZMIX = 61
    K.check(all(sorted(set(int(E.ownOf(r)) for r in zi if r.endswith(str(z)))) != [PRS[z]] for z in (1, 3, 4)), "X FIX2 at 61 % the mix still has other elements (the tail sits just above 60)")
    C.ELEM_ZMIX = 60
    EARTH1 = [r for r in zi if r.endswith("1") and mirror(r, PRS, 60) == 0][0]
    OFF1 = [r for r in zi if r.endswith("1") and mirror(r, PRS, 60) == 4][0]
    K.eq([int(E.mod(OFF1, e)) for e in range(5)], [0, 0, 0, 25, -25], "X FIX an Air one in Zone 1 (%s): resists Air, weak to Fire (the pure wheel)" % OFF1)
    K.eq(str(eo.apply(JString(OFF1))), "Air", "X FIX mob:fn:elemOf agrees (Air)")
    C.ELEM_ZMIX = 0
    K.check(all(int(E.ownOf(r)) != PRS[int(r[-1])] for r in zi), "X FIX elem.zoneMix 0 = no tougher version takes its zone element")
    C.ELEM_ZMIX = 100
    K.check(all(int(E.ownOf(r)) == PRS[int(r[-1])] for r in zi), "X FIX elem.zoneMix 100 = all take it (the 0.1.25 build-report rule)")
    C.ELEM_ZMIX = 60
    K.eq((int(E.ownOf("Foo_Bar_SkyyArmored1")), int(E.ownOf("Foo_Bar_SkyyVeteran3"))), (0, 2), "X FIX a tougher version not in the table (a newer build's) = its zone element")
    C.AUG_Z1 = "Fire"
    C.elemEdit("aug.zoneElement.1")
    K.eq([int(E.ownOf(r)) for r in zi], [mirror(r, [-1, 3, 1, 2, 3, 4], 60) for r in zi], "X FIX Zone 1 = Fire: the mix follows (Fire most, Earth now one of the others)")
    C.AUG_Z1 = "none"
    C.elemEdit("aug.zoneElement.1")
    K.check(all(int(E.ownOf(r)) == -1 for r in zi if r.endswith("1")), "X FIX Zone 1 element none = its element-less tougher versions have no element")
    C.useDefaults()
    K.eq((int(C.ELEM_ZMIX), int(E.ownOf(EARTH1))), (60, 0), "X back to the defaults (%s = Earth)" % EARTH1)
    # ---- the weights
    w = [round(float(x), 6) for x in A.weights("Trork_Warrior", 1, 1.0, 0.4)]
    K.eq(w, [0.8, 0.4, 0.4, 0.4, 0.4], "X weights: an element-less Zone 1 mob = Earth 0.8 % (zone x2), others 0.4 %")
    w = [round(float(x), 6) for x in A.weights(EARTH1, 1, 1.0, 0.4)]
    K.eq(w, [2.4, 0.4, 0.4, 0.4, 0.4], "X weights: a Zone 1 Earth mob = Earth 2.4 % (own x3 x zone x2)")
    w = [round(float(x), 6) for x in A.weights("Fire_Slime", 3, 1.0, 0.4)]
    K.eq(w, [0.4, 0.4, 0.8, 1.2, 0.4], "X weights: a Fire slime in Zone 3 = Fire 1.2 (own), Water 0.8 (zone)")
    # ---- addTo, many kills
    N = 40000

    def run(role, rw, env, lvl, n=N, seed=11):
        rng = RND(seed)
        cnt, kills, el_kills, st_kills, per = {}, 0, 0, 0, []
        for _ in range(n):
            lst = AL()
            k = int(A.addTo(lst, role, rw, env, lvl, rng))
            ids = [str(lst.get(i)[0]) for i in range(lst.size())]
            q = [int(lst.get(i)[1]) for i in range(lst.size())]
            assert k == len(ids) and all(x == 1 for x in q), (k, ids, q)
            per.append(len(ids))
            for x in ids:
                cnt[x] = cnt.get(x, 0) + 1
            kills += 1 if ids else 0
            el_kills += 1 if any(x.split("_")[2] in ELEM for x in ids) else 0
            st_kills += 1 if any(x.split("_")[2] in STAT for x in ids) else 0
        return cnt, 100.0 * el_kills / n, 100.0 * st_kills / n, per

    def near(v, want, tol):
        return abs(v - want) <= tol

    def share(cnt, kind):
        t = sum(v for k, v in cnt.items() if k.split("_")[2] in ELEM)
        return 100.0 * sum(v for k, v in cnt.items() if k.split("_")[2] == kind) / max(1, t)
    res = {}
    for name, role, rw, env, lvl in (("z1 plain", "Trork_Warrior", "", "Env_Zone1_Plains", 8), ("z1 earth", EARTH1, "", "Env_Zone1_Plains", 9),
                                     ("z3 water slime", "Water_Slime", "", "Env_Zone3_Shores", 45), ("z1 elite", "Trork_Warrior", "elite", "Env_Zone1_Plains", 11),
                                     ("z2 mini", "Goblin_Scrapper", "mini", None, 30), ("z1 boss", "Trork_Chieftain", "", "Env_Zone1_Forests", 18),
                                     ("z5 by level", "Trork_Warrior", "", None, 90), ("pack boss", "SLB_Nightlord", "", None, 38)):
        res[name] = run(role, rw, env, lvl, n=N if "boss" not in name else 4000)
    K.notes.append("X rates (element %%, stat %%) per kill: %s" % dict((k, (round(v[1], 2), round(v[2], 2))) for k, v in res.items()))
    allids = set()
    for v in res.values():
        allids |= set(v[0])
    K.check(allids <= IDS and not [i for i in allids if i.startswith("Skyy_Aug_Poison_") or int(i.rsplit("_", 1)[1]) > 5],
            "X every dropped id is one of tools/tier_tags.py AUG_IDS, never Poison, never T6+ (%d distinct)" % len(allids))
    c, e, s, _p = res["z1 plain"]
    K.check(near(e, 2.4, 0.3) and s == 0.0 and near(share(c, "Earth"), 33.3, 5.0) and all(i.endswith("_1") for i in c),
            "X an ordinary Zone 1 mob: %.2f %% (2.4) one element augment, Earth %.0f %% of them (1/3), all T1, no stat" % (e, share(c, "Earth")))
    c, e, s, _p = res["z1 earth"]
    K.check(near(e, 4.0, 0.4) and s == 0.0 and near(share(c, "Earth"), 60.0, 5.0), "X a Zone 1 tougher version (Earth): %.2f %% (4.0), Earth %.0f %% (60), no elite x" % (e, share(c, "Earth")))
    c, e, s, _p = res["z3 water slime"]
    K.check(near(e, 4.0, 0.4) and near(share(c, "Water"), 60.0, 5.0) and all(i.endswith("_3") for i in c), "X a Water slime in Zone 3: %.2f %% (4.0), Water %.0f %%, T3" % (e, share(c, "Water")))
    c, e, s, _p = res["z1 elite"]
    K.check(near(e, 7.2, 0.6) and near(s, 2.0, 0.35) and set(i.split("_")[2] for i in c if i.split("_")[2] in STAT) == set(STAT),
            "X an elite x3: %.2f %% element (7.2) + %.2f %% stat (2), every stat kind" % (e, s))
    c, e, s, _p = res["z2 mini"]
    K.check(near(e, 7.2, 0.6) and near(s, 10.0, 0.7) and all(i.endswith("_2") for i in c) and near(share(c, "Thunder"), 33.3, 5.0),
            "X a mini boss (Zone 2 by level 30): %.2f %% element, %.2f %% stat (10), T2, Thunder %.0f %%" % (e, s, share(c, "Thunder")))
    for nm in ("z1 boss", "pack boss"):
        c, e, s, per = res[nm]
        K.check(e == 100.0 and s == 100.0 and min(per) == 2 and max(per) == 3 and near(sum(per) / float(len(per)), 2.5, 0.05),
                "X %s: always 1 stat + 1 element, 50 %% one more (avg %.3f items)" % (nm, sum(per) / float(len(per))))
    c, e, s, _p = res["z5 by level"]
    K.check(all(i.endswith("_5") for i in c) and near(share(c, "Air"), 33.3, 6.0), "X Lv 90 without a zone environment = Zone 5: T5, Air %.0f %%" % share(c, "Air"))
    r0 = int(A.ROLLS)
    lst = AL()
    K.check(int(A.addTo(lst, "Trork_Warrior", "", "Env_Zone1_Plains", 0, RND(1))) == 0 and int(A.ROLLS) == r0, "X an unlevelled non-boss (animals, unlisted pack mobs) rolls nothing")
    K.check(int(A.addTo(AL(), "Trork_Chieftain", "", None, 0, RND(1))) == 0 and int(A.ROLLS) == r0, "X a boss with no zone (no environment, no level) rolls nothing")
    # the cap, off, missing item, the null guards
    C.AUG_BASE = 40.0
    c, e, s, _p = run("Trork_Warrior", "elite", "Env_Zone1_Plains", 5, n=500)
    K.check(e == 100.0, "X 40 %% x 5 elements x eliteX 3 is capped at 100 %% (one augment): %.1f" % e)
    C.useDefaults()
    C.AUG_ON = False
    K.check(not bool(A.on()) and int(A.addTo(AL(), "Trork_Chieftain", "", "Env_Zone1_Plains", 18, RND(1))) == 0, "X aug.drop.on off = on() false, no roll (SpoilsSys stays asleep for it)")
    C.useDefaults()
    C.AUG_BASE, C.AUG_SELITE, C.AUG_SMINI, C.AUG_BSTAT, C.AUG_BELEM, C.AUG_BBONUS = 0.0, 0.0, 0.0, 0, 0, 0.0
    K.check(not bool(A.on()), "X every chance 0 = on() false")
    C.useDefaults()
    OK["on"] = False
    m0 = int(A.MISSING)
    lst = AL()
    A.addTo(lst, "Trork_Chieftain", "", "Env_Zone1_Plains", 18, RND(1))
    K.check(lst.size() == 0 and int(A.MISSING) >= m0 + 2, "X items the server lacks (no SkyyGear) = counted MISSING, nothing added (one WARN for all ids)")
    OK["on"] = True
    K.check(int(A.addTo(None, "Trork_Warrior", "", None, 5, RND(1))) == 0 and int(A.addTo(AL(), None, "", None, 5, RND(1))) == 0
            and int(A.addTo(AL(), "Trork_Warrior", "", None, 5, None)) == 0 and int(A.pick(None, RND(1), True)) == -1, "X null list / role / random / weights = 0 / -1")
    K.eq(int(A.pick(JArray(JDouble)([0.0, 0.0, 0.0, 0.0, 0.0]), RND(1), True)), -1, "X pick with no weight = none")
    # the check hook
    ck = dict((v, H.checkZoneElem("aug.zoneElement.1", v)) for v in ("Earth", " water ", "none", "Lightning", "Ice", "", "Fire,Water"))
    K.check(ck["Earth"] is None and ck[" water "] is None and ck["none"] is None and ck["Lightning"] is None and ck[""] is None and ck["Ice"] is not None
            and ck["Fire,Water"] is not None and H.checkZoneElem("aug.zoneElement.1", None) is None,
            "X checkZoneElem: the 5 elements (any case) / none / blank ok; Ice, two elements refused: %s" % dict((k, None if v is None else str(v)) for k, v in ck.items()))
    # MobCfg.load from a real scratch file
    P_ = JClass("java.nio.file.Paths")
    sd = os.path.join(scratch, "cfg")
    os.makedirs(sd, exist_ok=True)
    fp = os.path.join(sd, "config.properties")
    base = (d.replace("\naug.drop.base=0.4\n", "\naug.drop.base=1.5\n").replace("\naug.drop.eliteX=3\n", "\naug.drop.eliteX=99\n")
            .replace("\naug.zoneElement.2=Thunder\n", "\naug.zoneElement.2=Water\n").replace("\naug.drop.bossStat=1\n", "\naug.drop.bossStat=9\n")
            .replace("\nelem.zoneVariants=true\n", "\nelem.zoneVariants=false\n").replace("\nelem.zoneMix=60\n", "\nelem.zoneMix=150\n"))
    open(fp, "w", encoding="latin-1", newline="").write(base)
    C.DIR = P_.get(sd)
    C.FILE = P_.get(fp)
    C.BANDS = P_.get(os.path.join(sd, "bands.properties"))
    C.load()
    K.eq((float(C.AUG_BASE), float(C.AUG_ELITE), str(C.AUG_Z2), int(C.AUG_BSTAT), bool(C.ELEM_ZVAR), int(A.zoneElem(2)), int(E.ownOf(EARTH1)), int(C.ELEM_ZMIX)),
         (1.5, 20.0, "Water", 5, False, 2, -1, 100), "X MobCfg.load reads the file: 1.5 %, eliteX 99 -> 20, Zone 2 Water, boss stats 9 -> 5, zone variants off (derived), zone mix 150 -> 100")
    strip = "\n".join(l for l in d.split("\n") if not l.startswith(("aug.", "elem.zoneVariants", "elem.zoneMix")))
    open(fp, "w", encoding="latin-1", newline="").write(strip)
    b0 = open(fp, "rb").read()
    C.load()
    K.eq(vals(), DEFV, "X a file without the 17 lines = the defaults (no migration)")
    K.check(open(fp, "rb").read() == b0, "X ... and the file is not rewritten")
    t = str(Egg.text())
    K.check("; augment drops on (element 0.4 % each, own x3.0, zone x2.0, elites x3.0; stat elite 2.0 % / mini 10.0 %; boss 1 stat + 1 element (+50.0 %); zones Earth/Thunder/Water/Fire/Air, tougher versions take it;" in t,
            "X the ready text (MobEgg.text) names the augment drops: %s" % t[-260:])
    K.check("elites x3.0 (rolled" in t, "X ... after the set drops (0.1.24 text kept)")
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
    K.check(seq.count("MobAug.on") == 1 and seq.index("MobAug.on") < seq.index("MobSpoils.first"), "W SpoilsSys.tick gates on MobAug.on() before the once-per-death check")
    K.check(seq.count("MobAug.addTo") == 1 and seq.index("MobTheme.addTo") < seq.index("MobAug.addTo") < seq.index("MobEgg.addTo") < seq.index("MobSpoils.spawn"),
            "W SpoilsSys.tick: MobTheme.addTo -> MobAug.addTo -> MobEgg.addTo -> MobSpoils.spawn (the same list): %s" % seq)
    K.check(seq.index("MobTheme.addTo") < seq.index("MobLevel.envId") < seq.index("MobAug.addTo"), "W the death's environment id is read for the zone (MobLevel.envId)")
    pos = {}
    ci = m[0].getMethodInfo().getCodeAttribute().iterator()
    while ci.hasNext():
        p_ = ci.next()
        if ci.byteAt(p_) == 0xb8:
            nm = str(cpl.getMethodrefClassName(ci.u16bitAt(p_ + 1))).rsplit(".", 1)[1] + "." + str(cpl.getMethodrefName(ci.u16bitAt(p_ + 1)))
            pos.setdefault(nm, p_)
    et = m[0].getMethodInfo().getCodeAttribute().getExceptionTable()
    cov = lambda q: [(int(et.startPc(i)), int(et.endPc(i)), int(et.handlerPc(i))) for i in range(et.size()) if et.startPc(i) <= q < et.endPc(i)]
    ca, ce = cov(pos["MobAug.addTo"]), cov(pos["MobEgg.addTo"])
    K.check(len(ca) == len(ce) + 1 and not [x for x in ca if x[0] <= pos["MobEgg.addTo"] < x[1] and x not in ce],
            "W FIX MobAug.addTo has its OWN catch (a throw no longer skips the egg / spawn / secret finds): aug %s, egg %s" % (ca, ce))
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Cfg, Sp, Sc, A = JClass(PKG + "MobCfg"), JClass(PKG + "MobSpoils"), JClass(PKG + "MobSecret"), JClass(PKG + "MobAug")
    P_ = JClass("java.nio.file.Paths")
    files = [f for f in ("config.properties", "bands.properties", "trees.properties") if os.path.isfile(os.path.join(home, f))]
    before = dict((f, open(os.path.join(home, f), "rb").read()) for f in files)
    cf = before.get("config.properties", b"")
    K.check("config.properties" in files and b"aug." not in cf and b"\nelem.mobs" not in cf and b"\nrank.pack.mobs" not in cf,
            "D the live copy has a config.properties without aug. / elem.mobs / rank.pack.mobs lines (the new defaults apply)")

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
        return (bool(Cfg.AUG_ON), float(Cfg.AUG_BASE), str(Cfg.AUG_Z1), bool(Cfg.ELEM_ZVAR), "Water_Slime=Water" in str(Cfg.ELEM_MOBS), "Water_Slime" in str(Cfg.PACK_MOBS) and "*_Slime" not in str(Cfg.PACK_MOBS),
                bool(A.on()))
    DEF = (True, 0.4, "Earth", True, True, True, True)
    o1 = start()
    K.eq(vals(), DEF, "D start 1: the live file -> the new defaults (drops on, Zone 1 Earth, slimes tagged + levelled)")
    K.eq(dict((f, open(os.path.join(home, f), "rb").read() == before[f]) for f in files), dict((f, True) for f in files),
         "D start 1: config / bands / trees bytes untouched (no migration; older updates said %r)" % o1[:60])
    o2 = start()
    K.eq((o2, vals()), ("", DEF), "D start 2: nothing migrates, the same values")
    K.eq(dict((f, open(os.path.join(home, f), "rb").read() == before[f]) for f in files), dict((f, True) for f in files), "D start 2: bytes still untouched")
    K.save()


HK.run_compare = T22._cmp
if __name__ == "__main__":
    HK.run("SkyyMobs", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("static", run_static), ("exec", run_exec), ("wire", run_wire), ("ex124", T24.run_exec), ("ex123", T23.run_exec), ("cs123", T23.run_cs),
            ("live", run_live)], __file__, live=(T22.LIVE_DIR, "Skyy_SkyyMobs"))
