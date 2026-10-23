"""Harness for SkyyMobs 0.1.18 (dragond1 D6: the boss dragon eggs - tools/mobs_0_1_18_patch.py).
Build first:
    python tools/mobs_0_1_18_patch.py && python SkyyMobs/build_skyymobs_0.1.18.py
    python SkyyMobs/test_skyymobs_0.1.18.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  S     static   the patch re-runs to identical bytes (--out), line endings kept, exactly 1 new class (MobEgg), no new command / system
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.1.17 -> 0.1.18 (EXPECT below)
  X     exec     EXECUTES MobEgg on the defaults: the default file lines, the table (Dragon_Fire = Fire / Thunder, Dragon_Frost = Air, the
                 most specific match wins, any case), the check= hook (Earth / Water = Aures' nests refused, unknown words, no =, a lone *),
                 ONE roll a boss death: 20,000 seeded rolls at 1 % (~1 %, both Fire-boss eggs seen), never for a non-boss in the table or a
                 boss not in the table, chance 0 = never, a hand-set 50 % clamped to 12 % (= the Mythic boss bag), a missing egg item = no
                 drop (counted, one WARN), addTo = the list SpoilsSys spawns + the owner's chat line, MobCfg.apply reads / clamps the rows,
                 the ready-line text; FIXER: the cap = SkyyGear's LIVE loot.boss.mythic through config:fn:SkyyGear "get" (5 % -> eggs at
                 most 5 %, 0 = none, junk / 40 / no Gear = 12 %), the drop line names one dragon per profile
  EL117 0.1.17's exec phase EXECUTED on this jar (the element side unchanged)
  D     live     start twice on a scratch COPY of Skyy's live NewBetaTest Skyy_SkyyMobs: 0.1.18 writes nothing, start 2 changes nothing,
                 the live file (no bosses.dragonEgg* lines) runs with the defaults
  AA    engine-access audit
NOT COVERED (UNVERIFIED in game): SpoilsSys.tick inside the ECS death dispatch (it calls MobEgg.addTo, executed here) - the egg landing on
the ground at the boss and SkyySacks picking it up for the top damager.
Scratch: tools/dev/scratch/dragond1fix/mobs (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.1.18"
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "dragond1fix", "mobs")]
import skyybuild as B
import harness_kit as HK

_run0 = HK.run
HK.run = lambda *a, **k: None          # import 0.1.17's harness for its phases without running it
_s = importlib.util.spec_from_file_location("test_skyymobs_0_1_17", os.path.join(HERE, "test_skyymobs_0.1.17.py"))
T117 = importlib.util.module_from_spec(_s)
_s.loader.exec_module(T117)
HK.run = _run0

GEN = os.path.join(HERE, "build_skyymobs_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyymobs_0.1.17.py")
PATCH = os.path.join(ROOT, "tools", "mobs_0_1_18_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMobs-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMobs-0.1.17.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.mobs."
LIVE_DIR = T117.LIVE_DIR
ADDED = ["MobEgg"]
EXPECT = {
    "MobCfg": ["+f DEGG_CHANCE", "+f DEGG_TXT", "~<clinit>", "~m apply", "~m load", "~m reloadAll", "~m useDefaults"],
    "MobHooks": ["+m checkDragonEggs"], "SpoilsSys": ["~m tick"],
    "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "CfgFile": ["~<clinit>"],
    "SkyyMobsPlugin": ["~m setup"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
T117.PKG = PKG
U = "00000000-0000-0000-0000-000000000118"
FIRE, THUNDER, AIR = "Skyy_PetEgg_Dragon_Fire", "Skyy_PetEgg_Dragon_Thunder", "Skyy_PetEgg_Dragon_Air"


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyMobs 0.1.18 - build script') and g.count('VERSION = "0.1.18"') == 1, "S header + VERSION")
    K.eq((g.count("registerSystem(") - o.count("registerSystem("), g.count("registerCommand(") - o.count("registerCommand("),
          g.count("makeClass(") - o.count("makeClass(")), (0, 0, 1), "S no new system / command, 1 new class")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def run_exec(out, jar, scratch, home):
    import jpype
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    C, E, H = JClass(PKG + "MobCfg"), JClass(PKG + "MobEgg"), JClass(PKG + "MobHooks")
    Random, AL, UUID = JClass("java.util.Random"), JClass("java.util.ArrayList"), JClass("java.util.UUID")
    C.useDefaults()
    d = str(C.DEF_CFG)
    K.check("\nbosses.dragonEggs=Dragon_Fire=Fire/Thunder, Dragon_Frost=Air" in d and "\nbosses.dragonEggChance=1" in d, "X the default file carries the two rows")
    K.check(str(C.DEGG_TXT) == "Dragon_Fire=Fire/Thunder, Dragon_Frost=Air" and abs(float(C.DEGG_CHANCE) - 1.0) < 1e-9, "X defaults in force: %s / %s" % (C.DEGG_TXT, C.DEGG_CHANCE))
    K.eq([str(E.eggsFor(r)) if E.eggsFor(r) is not None else None for r in ("Dragon_Fire", "dragon_frost", "DRAGON_FIRE", "Trork_Chieftain", "Dragon_Void", None)],
         [FIRE + "/" + THUNDER, AIR, FIRE + "/" + THUNDER, None, None, None], "X eggsFor: Fire boss = Fire / Thunder, Frost boss = Air (any case); others none")
    # the check= hook
    ok = [H.checkDragonEggs("k", v) is None for v in ("Dragon_Fire=Fire/Thunder, Dragon_Frost=Air", "-", "", "Ancient_Calamity*=Fire", "dragon_*=air")]
    bad = [str(H.checkDragonEggs("k", v)) for v in ("Dragon_Fire=Earth", "Dragon_Frost=Water", "Dragon_Fire=Ice", "Dragon_Fire", "*=Fire", "Dragon_Fire=Fire/Lava")]
    K.check(all(ok) and H.checkDragonEggs("k", None) is None, "X checkDragonEggs takes the default, -, a pack boss pattern: %s" % ok)
    K.check("Nestkeeper" in bad[0] and "Nestkeeper" in bad[1] and "not Fire, Thunder or Air" in bad[2] and "needs Role=Element" in bad[3]
            and "not only *" in bad[4] and "Lava" in bad[5], "X checkDragonEggs refuses Earth / Water (Aures' nests), unknown words, no =, a lone *: %s" % bad)
    # the most specific match wins
    C.DEGG_TXT = "Dragon_*=Air, Dragon_Fire=Fire, Trork_Warrior=Thunder, junk, X=Lava"
    K.eq([str(E.eggsFor("Dragon_Fire")), str(E.eggsFor("Dragon_Frost")), str(E.eggsFor("Trork_Warrior"))], [FIRE, AIR, THUNDER], "X a live edit: the most specific pattern wins, bad entries skipped")
    C.useDefaults()

    @JImplements("java.util.function.Predicate")
    class Pred(object):
        def __init__(self, fn):
            self.fn = fn

        @JOverride
        def test(self, x):
            return bool(self.fn(str(x)))
    E.ITEM_API = Pred(lambda x: True)
    told = []

    @JImplements("java.util.function.BiConsumer")
    class Tell(object):
        @JOverride
        def accept(self, u, t):
            told.append((str(u), str(t)))
    E.TELL_API = Tell()
    rn = Random(118)
    got = {}
    n = 20000
    for _ in range(n):
        x = E.roll("Dragon_Fire", rn)
        if x is not None:
            got[str(x)] = got.get(str(x), 0) + 1
    tot = sum(got.values())
    K.check(0.006 < tot / float(n) < 0.014 and set(got) == {FIRE, THUNDER}, "X 20,000 Fire-boss kills at 1 %%: %d eggs (%s)" % (tot, got))
    fr = sum(1 for _ in range(5000) if E.roll("Dragon_Frost", rn) is not None)
    C.DEGG_CHANCE = 100.0          # (clamped to 12 % in roll: the helpers below roll until one drops)

    def first(role, tries=400):
        for _ in range(tries):
            x = E.roll(role, rn)
            if x is not None:
                return str(x)
        return None

    def never(role, tries=2000):
        return all(E.roll(role, rn) is None for _ in range(tries))
    K.check(first("Dragon_Frost") == AIR and 0 < fr < 120, "X the Frost boss drops the Air egg (%d of 5,000 at 1 %%)" % fr)
    K.check(never("Trork_Chieftain") and never("Skeleton_Archer") and never(None, 10), "X a boss NOT in the table / a normal mob: never")
    C.DEGG_TXT = "Trork_Warrior=Fire, Dragon_Fire=Fire"
    K.check(never("Trork_Warrior") and first("Dragon_Fire") == FIRE, "X a normal mob in the table: never (only full bosses = the Mythic bag mobs)")
    C.useDefaults()
    C.DEGG_CHANCE = 0.0
    K.check(all(E.roll("Dragon_Fire", rn) is None for _ in range(2000)), "X chance 0 = never")
    C.DEGG_CHANCE = 50.0
    hi = sum(1 for _ in range(20000) if E.roll("Dragon_Fire", rn) is not None)
    K.check(0.10 < hi / 20000.0 < 0.14, "X a hand-set 50 %% is clamped to 12 %% (the Mythic boss bag): %.3f" % (hi / 20000.0))
    K.check(abs(float(C.dec("50", 1.0, 0.0, 12.0)) - 12.0) < 1e-9, "X MobCfg.dec clamps the row to 12")
    Props = JClass("java.util.Properties")
    pc, pb = Props(), Props()
    pc.setProperty("bosses.dragonEggChance", "40")
    pc.setProperty("bosses.dragonEggs", "Dragon_Frost=Thunder")
    C.apply(pc, pb)
    K.check(abs(float(C.DEGG_CHANCE) - 12.0) < 1e-9 and str(C.DEGG_TXT) == "Dragon_Frost=Thunder" and str(E.eggsFor("Dragon_Frost")) == THUNDER,
            "X MobCfg.apply reads both rows (40 -> 12 %%): %s / %s" % (C.DEGG_CHANCE, C.DEGG_TXT))
    C.apply(Props(), Props())
    K.check(abs(float(C.DEGG_CHANCE) - 1.0) < 1e-9 and str(C.DEGG_TXT) == "Dragon_Fire=Fire/Thunder, Dragon_Frost=Air", "X a file without the lines = the defaults")
    # a missing egg item (SkyyPets not loaded)
    C.DEGG_CHANCE = 100.0
    E.ITEM_API = Pred(lambda x: x != AIR)
    m0 = int(E.MISSING)
    K.check(never("Dragon_Frost", 400) and int(E.MISSING) > m0 and first("Dragon_Fire") in (FIRE, THUNDER), "X the Air egg item missing: no drop, counted (%d)" % (int(E.MISSING) - m0))
    E.ITEM_API = None
    K.check(never("Dragon_Fire", 400), "X no seam + no asset store here = the item counts as missing (no drop)")
    # addTo = what SpoilsSys spawns + the chat line
    E.ITEM_API = Pred(lambda x: True)
    l = AL()
    uu = UUID.fromString(U)
    r1 = None
    for _ in range(400):
        r1 = E.addTo(l, "Dragon_Frost", uu, rn)
        if r1 is not None:
            break
    K.check(told == [], "X addTo alone sends no line (review fix: only after the spawn)")
    K.check(not E.dropped(uu, r1, 0) and not E.dropped(None, r1, 1) and not E.dropped(uu, None, 1) and told == [], "X dropped(): nothing spawned / no owner / no egg = no line")
    K.check(E.dropped(uu, r1, 1), "X dropped(): the spawn put the drop in the world")
    K.check(str(r1) == AIR and l.size() == 1 and str(l.get(0)[0]) == AIR and int(l.get(0)[1]) == 1
            and told == [(U, "[Mobs] The boss dropped a Sky Dragon Egg! Hatch it in /pets > Hatchery (one dragon per profile).")], "X addTo: one Air egg in the drop list + the owner's line: %s" % told)
    K.check(E.addTo(l, "Dragon_Frost", None, rn) is None and E.addTo(None, "Dragon_Frost", uu, rn) is None and E.addTo(l, "Trork_Chieftain", uu, rn) is None and l.size() == 1,
            "X addTo: no owner / no list / no egg = nothing")
    # FIXER: the cap = SkyyGear's LIVE Boss Mythic bag chance (config:fn:SkyyGear "get" loot.boss.mythic), never above 12 %
    asked = []

    @JImplements("java.util.function.Function")
    class GearFn(object):
        def __init__(self, val):
            self.val = val

        @JOverride
        def apply(self, a):
            asked.append([str(x) for x in a])
            return self.val
    K.check(abs(float(E.cap()) - 12.0) < 1e-9 and float(E.gearMythic()) < 0, "X no SkyyGear on the bridge: the cap is 12 %%: %s" % E.cap())
    br.put("config:fn:SkyyGear", GearFn("3"))
    K.check(abs(float(E.cap()) - 3.0) < 1e-9 and asked[-1] == ["get", "loot.boss.mythic"], "X the REAL bridge path: config:fn:SkyyGear get loot.boss.mythic = 3 -> cap 3 %%: %s %s" % (E.cap(), asked[-1:]))
    br.remove("config:fn:SkyyGear")
    C.DEGG_CHANCE = 12.0
    E.GEAR_API = GearFn("5")
    lo = sum(1 for _ in range(20000) if E.roll("Dragon_Fire", rn) is not None)
    K.check(0.04 < lo / 20000.0 < 0.06 and abs(float(E.chance()) - 5.0) < 1e-9, "X Gear's Mythic bag at 5 %%: a 12 %% egg row rolls at 5 %% (%.3f)" % (lo / 20000.0))
    E.GEAR_API = GearFn("0")
    K.check(never("Dragon_Fire", 3000) and float(E.chance()) == 0.0, "X Gear's Mythic bag at 0 %%: no eggs")
    caps = []
    for v in ("junk", "40", "-3", None):
        E.GEAR_API = GearFn(v)
        caps.append(float(E.cap()))
    K.check(caps == [12.0, 12.0, 12.0, 12.0], "X Gear unreadable / above 12 / negative / null: the cap stays 12 %%: %s" % caps)
    C.DEGG_CHANCE = 1.0
    E.GEAR_API = GearFn("12")
    K.check(abs(float(E.chance()) - 1.0) < 1e-9, "X the row below the cap is used as is (1 %%)")
    E.GEAR_API = None
    C.useDefaults()
    t = str(E.text())
    K.check(t.startswith("dragon eggs: 2 boss rows, 1.0 % (cap 12.0 %, rolled ") and "dropped" in t, "X the ready-line text: %s" % t)
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    Cfg, S, E = JClass(PKG + "MobCfg"), JClass(PKG + "MobSpoils"), JClass(PKG + "MobEgg")
    P = JClass("java.nio.file.Paths")
    txt = open(os.path.join(home, "config.properties"), encoding="latin-1").read()

    def start():
        Cfg.DIR = P.get(home)
        Cfg.FILE = P.get(os.path.join(home, "config.properties"))
        Cfg.BANDS = P.get(os.path.join(home, "bands.properties"))
        o = [str(JClass(PKG + m).run(P.get(home))) for m in ("MobMig", "MobMig14", "MobMig11", "MobMig12", "MobMigP4")]
        Cfg.load()
        o.append(str(S.loadV3(P.get(home))))
        return o
    h0 = T117.tree_hash(home)
    o1 = start()
    h1 = T117.tree_hash(home)
    ch = sorted(k for k in set(h0) | set(h1) if h0.get(k) != h1.get(k))
    K.check(not ch, "D start 1 on a scratch COPY of the live data: 0.1.18 writes nothing (%s; %s)" % (ch, [x[:60] for x in o1 if x]))
    o2 = start()
    K.check(T117.tree_hash(home) == h1 and all(x == "" for x in o2[:-1]), "D start 2 changes nothing")
    if "bosses.dragonEgg" not in txt:
        K.check(str(Cfg.DEGG_TXT) == "Dragon_Fire=Fire/Thunder, Dragon_Frost=Air" and abs(float(Cfg.DEGG_CHANCE) - 1.0) < 1e-9
                and str(E.eggsFor("Dragon_Fire")) == "Skyy_PetEgg_Dragon_Fire/Skyy_PetEgg_Dragon_Thunder", "D the live file (no dragon egg lines) runs with the defaults")
    K.check(bool(Cfg.isBoss("Dragon_Fire")) and bool(Cfg.isBoss("Dragon_Frost")), "D with the live Boss roles both dragons are full bosses (eggs can drop)")
    K.save()


HK.run("SkyyMobs", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("static", run_static), ("exec", run_exec), ("el117", T117.run_exec), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyMobs"))
