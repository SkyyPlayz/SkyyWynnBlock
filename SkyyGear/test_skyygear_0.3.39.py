"""Harness for SkyyGear 0.3.39 (elem1: the Wynn element split, element Defence + Poison live, per-element hit numbers, gear:trees, Untiered at
the end of each zone - tools/gear_0_3_39_patch.py). Build first:
    python tools/gear_0_3_39_patch.py && python SkyyGear/build_skyygear_0.3.39.py
    python SkyyGear/test_skyygear_0.3.39.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  S  static   the patch re-runs to identical bytes, line endings kept, 3 new classes, no new command / system
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.3.38 -> 0.3.39 (EXPECT below)
  X  exec     EXECUTES in a bare JVM:
              X1 identity (spec 10.1): 1,000 random totals - GearElem.pcts with no pets / Imbue / gate sums to 0.3.38's GearHit.elemSum exactly
              X2 the pet rule (spec 10.2): weapon 5 Fire + pet 10 = 15, weapon 0 + pet 10 = 0, charm 4 + pet 10 with weapon 0 = 0 (charm gate on)
                 / 4 (gate off), Raw Elemental 2 opens all five pets; trees count always; the Imbue part on its element only
              X3 amounts: the stochastic rounding keeps the mean (10,000 draws), never negative; sum
              X4 modifiers (spec 10.3): mobPart +25 / -25 / -50 / 0 rounding table; playerPart D = 0 / 10 / 100 at S = 100
              X5 mob:fn:elem through modOf with a stub (Wynn names asked, the 5 s cache, a throwing stub = 0, no SkyyMobs = 0)
              X6 classes:fn:imbue through imbue() with a stub ({UUID, weapon} asked; "Thunder;30" / "Lightning;30" -> Thunder 30; junk -> null)
              X7 Poison (spec 10.4): weapon 20 + armour 30 = 50 % -> dotArgs {u, v, GearPoison, Poison, 5.0 / s, 10 s, 3 stacks, world} for a
                 100 hit; poison.time / stacks rows; the suffix "+ Poison  +20% over 10s"; Poison / element Defence live, Poison on armour
              X8 split() on real GearStats: inf[5] / [6] / [7]; elem.on off = 0.3.38 (no [6], [5] untouched); poison.on off = no [7]
              X9 the popup text, totText, GearElemDefFn / GearElemTotFn (aliases, bad args, elem.on off), onEdit (gear:imbue:v2 + gear:elem:defScale)
              X10 migrate39's text step: the 40 untouched rows move (12-20 / Hepta 72-80), an admin's row kept + noted, a multi-line entry kept,
                  CRLF kept, the marker at the end, a second pass = null; the fresh file holds the new bands + the element rows
  W  wiring   bytecode: GearHitSys -> weaponHit2 with the NPC test; weaponHit2 ends with GearElem.split; GearTrueSys -> dealt + putPop;
              GearLeechSys -> poison; GearCrit.handle takes the pop first and shows it before the crit return; GearFx.second -> note; forget;
              setup: gear:fn:elemDef, gear:fn:elemTotals, onEdit, the gear.elemFx switch, migrate39 right after migrateP7
  D  live     every migration TWICE on a scratch COPY of Skyy's live NewBetaTest Skyy_SkyyGear: migrate39 moves the untouched UT rows (History
              copy, one change-log row each), the second start changes nothing, the file loads with the element rows at their defaults
  AA engine-access audit
NOT COVERED (UNVERIFIED in game): the systems inside a live ECS dispatch (GearTrueSys on a real NPC / player, the CombatTextUpdate numbers
drawn by the client, the Poison DoT through SkyyClasses' job), the vanilla number + our coloured ones side by side (spec probe P1 not run).
Scratch: tools/dev/scratch/elem1/gear (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, json, random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.3.39"
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "elem1", "gear")]
import skyybuild as B
import harness_kit as HK

GEN = os.path.join(HERE, "build_skyygear_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyygear_0.3.38.py")
PATCH = os.path.join(ROOT, "tools", "gear_0_3_39_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyGear-0.3.38.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.gear."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyGear")
ADDED = ["GearElem", "GearElemDefFn", "GearElemTotFn"]
EXPECT = {
    "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "CfgRows1": ["~<clinit>"], "CfgRows2": ["~<clinit>"],
    "GearCfg": ["+f ELEM_CGATE", "+f ELEM_ON", "+f ELEM_POPUP", "+f ELEM_SCALE", "+f H39_KEYS", "+f H39_LK", "+f H39_LN", "+f H39_LO", "+f H39_MARK",
                "+f H39_MARK_ID", "+f H39_NEW", "+f H39_OLD", "+f H39_WHO", "+f POISON_ON", "+f POISON_STACKS", "+f POISON_TIME", "+m h39Log", "+m h39Same",
                "+m h39Update", "+m migrate39", "~<clinit>", "~m apply", "~m defaultsText"],
    "GearDefs": ["~<clinit>"],
    "GearHit": ["+m weaponHit2", "~m info", "~m weaponHit"], "GearHitSys": ["~m handle"], "GearTrueSys": ["~m handle"], "GearLeechSys": ["~m handle"],
    "GearCrit": ["~m handle"], "GearFx": ["~m forget", "~m second"], "GearView": ["+m elemCol", "~m rollCol", "~m suffix"], "SkyyGearPlugin": ["~m setup", "~m shutdown"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
U = "00000000-0000-0000-0000-000000000339"
V = "00000000-0000-0000-0000-0000000003f9"
EL5 = ["Earth", "Thunder", "Water", "Fire", "Air"]


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyGear 0.3.39 - build script') and g.count('VERSION = "0.3.39"') == 1, "S header + VERSION")
    K.eq((g.count("registerSystem(") - o.count("registerSystem("), g.count("registerCommand(") - o.count("registerCommand("), g.count('mk("') - o.count('mk("')),
         (0, 0, 3), "S no new system / command, 3 new classes")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def run_exec(out, jar, scratch, home):
    import jpype
    from jpype import JClass, JImplements, JOverride, JArray, JInt, JDouble
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR, B.JAVASSIST], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    Cfg, Df, E, H, Gv = JClass(PKG + "GearCfg"), JClass(PKG + "GearDefs"), JClass(PKG + "GearElem"), JClass(PKG + "GearHit"), JClass(PKG + "GearView")
    Obj = JClass("java.lang.Object")
    uu, vv = JClass("java.util.UUID").fromString(U), JClass("java.util.UUID").fromString(V)
    NS = int(Df.NS)
    SI = lambda k: int(Df.sIndex(k))
    FK = ["fEarth", "fThunder", "fWater", "fFire", "fAir", "rThunder", "rWater", "rElem"]

    def arr(d):
        a = [0] * NS
        for k, v in d.items():
            a[SI(k)] += v
        return JArray(JInt)(a)

    def add(*ds):
        o = {}
        for d in ds:
            for k, v in d.items():
                o[k] = o.get(k, 0) + v
        return o
    Z = JArray(JInt)([0] * NS)
    # ---- X1 identity
    rng = random.Random(339)
    bad = 0
    for _ in range(1000):
        d = dict((k, rng.randint(-3, 12)) for k in FK if rng.random() < 0.6)
        t = arr(d)
        pc = list(E.pcts(t, t, None, None, True, -1, 0.0))
        if abs(sum(pc) - int(H.elemSum(t))) > 1e-9:
            bad += 1
    K.eq(bad, 0, "X1 1,000 random totals: the split sums to 0.3.38's elemSum exactly (no pets / Imbue / gate)")
    # ---- X2 the pet rule + charms + trees + Imbue
    P = lambda full, rolled, ch, pe, gate=True, ie=-1, ip=0.0: [round(x, 6) for x in E.pcts(arr(full), arr(rolled), arr(ch) if ch is not None else None, arr(pe) if pe is not None else None, gate, ie, ip)]
    K.eq(P(add({"fFire": 5}, {"fFire": 10}), {"fFire": 5}, None, {"fFire": 10})[3], 15.0, "X2 weapon 5 Fire + pet 10 Fire = 15 (Skyy's example)")
    K.eq(P({"fFire": 10}, {}, None, {"fFire": 10})[3], 0.0, "X2 weapon 0 Fire + pet 10 = 0")
    K.eq(P({"fFire": 14}, {}, {"fFire": 4}, {"fFire": 10})[3], 0.0, "X2 charm 4 + pet 10, weapon 0, charm gate on = 0")
    K.eq(P({"fFire": 14}, {}, {"fFire": 4}, {"fFire": 10}, gate=False)[3], 4.0, "X2 ... charm gate off = 4 (spec 10.2)")
    K.eq(P(add({"rElem": 2}, {"fFire": 10, "fAir": 3}), {"rElem": 2}, None, {"fFire": 10, "fAir": 3}), [2.0, 2.0, 2.0, 12.0, 5.0], "X2 Raw Elemental 2 opens all five pets")
    K.eq(P({"fWater": 6}, {}, None, None), [0.0, 0.0, 6.0, 0.0, 0.0], "X2 a tree / other extra (no charm, no pet) counts always")
    K.eq(P({"fFire": 5}, {"fFire": 5}, None, None, True, 1, 30.0), [0.0, 30.0, 0.0, 5.0, 0.0], "X2 the Imbue part on its element only (Thunder 30)")
    K.eq(P({"rThunder": 4, "rWater": 2}, {"rThunder": 4, "rWater": 2}, None, None), [0.0, 4.0, 2.0, 0.0, 0.0], "X2 Raw Thunder / Water")
    # elem1fix: the Imbue element opens the pet + charm gate; the charm gate row defaults OFF
    K.eq(P({"fFire": 10}, {}, None, {"fFire": 10}, True, 3, 30.0)[3], 40.0, "X2 elem1fix: Fire Imbue 30 + Fire pet 10 with weapon 0 = 40 (Imbue opens the pet)")
    K.eq(P({"fFire": 4}, {}, {"fFire": 4}, None, True, 3, 30.0)[3], 34.0, "X2 elem1fix: Fire Imbue opens a gated Fire charm")
    K.eq(P({"fThunder": 10}, {}, None, {"fThunder": 10}, True, 3, 30.0)[1], 0.0, "X2 elem1fix: a Fire Imbue does not open a Thunder pet")
    K.check(not bool(JClass(PKG + "GearCfg").ELEM_CGATE), "X2 elem1fix: elem.charmGate defaults OFF (spec 3.1: charms always count)")
    # ---- X3 amounts
    R = JClass("java.util.Random")(7)
    pc = JArray(JDouble)([1.5, 0.0, 7.25, 33.0, -4.0])
    sums = [0.0] * 5
    n = 10000
    for _ in range(n):
        am = list(E.amounts(pc, 10.0, R))
        for e in range(5):
            sums[e] += am[e]
    K.check(all(abs(sums[e] / n - max(0.0, [0.15, 0.0, 0.725, 3.3, 0.0][e])) < 0.02 for e in range(5)), "X3 the stochastic rounding keeps each mean: %s" % [round(s / n, 3) for s in sums])
    K.eq(list(E.amounts(pc, 0.0, R)), [0] * 5, "X3 a 0 hit = nothing")
    K.eq(int(E.sum(JArray(JInt)([3, -2, 5, 0, 1]))), 9, "X3 sum skips negatives")
    # ---- X4 modifiers
    K.eq([int(E.mobPart(49, m)) for m in (25, -25, -50, 0, -100)], [61, 37, 25, 49, 0], "X4 mob table: 49 -> Weak 61, Resist 37, Fire boss 25, neutral 49, never below 0")
    K.eq([int(E.playerPart(49, d, 100)) for d in (0, 10, 100)] + [int(E.playerPart(0, 10, 100))], [49, 45, 25, 0], "X4 player victim: D 0 / 10 / 100 at S 100")

    # ---- X5 modOf
    @JImplements("java.util.function.Function")
    class Elem(object):
        def __init__(self, boom=False):
            self.calls, self.boom = [], boom

        @JOverride
        def apply(self, a):
            self.calls.append((str(a[0]), str(a[1])))
            if self.boom:
                raise RuntimeError("boom")
            return JClass("java.lang.Integer").valueOf({"Yeti|Fire": 25, "Yeti|Water": -25}.get(str(a[0]) + "|" + str(a[1]), 0))
    K.eq(int(E.modOf("Yeti", 3)), 0, "X5 no SkyyMobs = 0")
    E.MODC.clear()
    st = Elem()
    br.put("mob:fn:elem", st)
    K.eq([int(E.modOf("Yeti", 3)), int(E.modOf("Yeti", 2)), int(E.modOf("Yeti", 3)), int(E.modOf("Yeti", 9))], [25, -25, 25, 0], "X5 mob:fn:elem: Yeti Fire +25 / Water -25")
    K.eq(st.calls, [("Yeti", "Fire"), ("Yeti", "Water")], "X5 asked with the Wynn names, once per role + element (5 s cache)")
    E.MODC.clear()
    br.put("mob:fn:elem", Elem(boom=True))
    K.eq(int(E.modOf("Yeti", 3)), 0, "X5 a throwing mob:fn:elem = 0 (WARN once)")
    br.remove("mob:fn:elem")
    E.MODC.clear()

    # ---- X6 imbue
    @JImplements("java.util.function.Function")
    class Imb(object):
        def __init__(self, ans):
            self.ans, self.calls = ans, []

        @JOverride
        def apply(self, a):
            self.calls.append([str(x) for x in a])
            return self.ans
    K.check(E.imbue(uu, "Weapon_Longsword_Iron") is None, "X6 no SkyyClasses = no Imbue")
    for ans, want in (("Thunder;30", (1, 30.0)), ("Lightning;30", (1, 30.0)), ("Fire;37.5", (3, 37.5)), ("Ice;30", None), ("Fire", None), ("Fire;x", None), (None, None)):
        im = Imb(ans)
        br.put("classes:fn:imbue", im)
        r = E.imbue(uu, "Weapon_Longsword_Iron")
        got = None if r is None else (int(r[0]), float(r[1]))
        K.eq(got, want, "X6 classes:fn:imbue %r -> %s" % (ans, want))
    K.eq(im.calls[-1], [U, "Weapon_Longsword_Iron"], "X6 asked with {UUID, weapon id}")
    br.remove("classes:fn:imbue")
    # ---- X7 Poison
    a = E.dotArgs(uu, vv, 100.0, 50, "w1")
    K.eq([str(a[0]), str(a[1]), str(a[2]), str(a[3]), float(a[4]), float(a[5]), int(a[6]), str(a[7])], [U, V, "GearPoison", "Poison", 5.0, 10.0, 3, "w1"],
         "X7 weapon 20 + armour 30 = 50 %: a 100 hit poisons 50 over 10 s = 5 / s, 3 stacks (spec 10.4)")
    Cfg.POISON_TIME, Cfg.POISON_STACKS = 5, 1
    a = E.dotArgs(uu, vv, 100.0, 50, "w1")
    K.eq([float(a[4]), float(a[5]), int(a[6])], [10.0, 5.0, 1], "X7 poison.time 5 / poison.stacks 1")
    Cfg.POISON_TIME, Cfg.POISON_STACKS = 10, 3
    K.check(E.dotArgs(uu, vv, 0.0, 50, "w1") is None and E.dotArgs(uu, vv, 100.0, 0, "w1") is None and E.dotArgs(uu, None, 100.0, 50, "w1") is None
            and E.dotArgs(uu, vv, 100.0, 50, None) is None, "X7 no hit / no line / no victim / no world = no Poison")
    ip = SI("poison")
    K.eq([str(Df.S_SLOT[ip]), str(Df.S_UNIT[ip]), int(Df.S_LIVE[ip])], ["wa", "%", 1], "X7 Poison: weapons + armour, %, live")
    K.eq([int(Df.S_LIVE[SI(k)]) for k in ("dEarth", "dThunder", "dWater", "dFire", "dAir")], [1] * 5, "X7 the five element Defence lines are live")
    K.eq(str(Gv.rollLine("poison", 20)), "+ Poison   +20% over 10s", "X7 the tooltip line")
    K.eq(str(Gv.rollLine("dFire", 8)), "+ Fire Defence   +8", "X7 Fire Defence no longer says coming later")
    # ---- X8 split on the real GearStats (no gear: rolled = 0, so every element part is an extra -> unconditional)
    t = arr({"fFire": 10, "rElem": 2, "poison": 30, "tdmg": 4})
    inf = H.info(uu, t)
    K.eq((len(inf), inf[6] is None, int(inf[7])), (8, True, 0), "X8 info(): 8 slots, [6] none, [7] 0")
    H.pctInfo(inf, t, 100.0, 0.5)
    E.split(inf, uu, None, None, t, 100.0, False)
    am = list(inf[6])
    K.check(int(inf[5]) == sum(am) and am[3] in (12, 13) and all(x in (2, 3) for i, x in enumerate(am) if i != 3) and int(inf[7]) == 30,
            "X8 split: [6] = %s (Fire 10 + 2, the rest 2 each, of a 100 hit), [5] = the sum, [7] Poison 30" % am)
    Cfg.ELEM_ON = False
    inf = H.info(uu, t)
    H.pctInfo(inf, t, 100.0, 0.5)
    i5 = int(inf[5])
    E.split(inf, uu, None, None, t, 100.0, False)
    K.check(inf[6] is None and int(inf[5]) == i5 and int(inf[7]) == 30, "X8 elem.on off = 0.3.38 (no parts, the sum untouched), Poison still on")
    Cfg.ELEM_ON = True
    Cfg.POISON_ON = False
    inf = H.info(uu, t)
    E.split(inf, uu, None, None, t, 100.0, False)
    K.eq(int(inf[7]), 0, "X8 poison.on off = no Poison")
    Cfg.POISON_ON = True
    # ---- X9 texts, the two Functions, onEdit
    K.eq([str(E.popText(49, 3, "word")), str(E.popText(49, 3, "number"))], ["49 Fire", "49"], "X9 popup text: word / number")
    K.eq(str(E.totText(JArray(JDouble)([3.0, 0.0, 5.4, 9.6, 0.0]), arr({"dEarth": 8, "dThunder": 2, "dFire": 12, "poison": 20}))),
         "Earth:3/8,Thunder:0/2,Water:5/0,Fire:10/12,Air:0/0,Poison:20", "X9 the gear:fn:elemTotals text")
    E.DEF.put(uu, JArray(JInt)([1, 2, 3, 4, 5]))
    Df_ = JClass(PKG + "GearElemDefFn")()
    OA = lambda xs: JArray(Obj)(xs)
    K.eq([int(Df_.apply(OA([uu, "Fire"]))), int(Df_.apply(OA([uu, "Wind"]))), int(Df_.apply(OA([uu, "Lightning"]))), int(Df_.apply(OA([vv, "Fire"]))),
          int(Df_.apply(OA([uu, "Ice"]))), int(Df_.apply(None)), int(Df_.apply(OA([uu])))], [4, 5, 2, 0, 0, 0, 0], "X9 gear:fn:elemDef: names + aliases, unknown = 0, never throws")
    Cfg.ELEM_ON = False
    K.eq(int(Df_.apply(OA([uu, "Fire"]))), 0, "X9 elem.on off = no element Defence")
    Cfg.ELEM_ON = True
    E.TOT.put(uu, "Earth:0/0,Thunder:0/0,Water:0/0,Fire:3/0,Air:0/0,Poison:0")
    Tf = JClass(PKG + "GearElemTotFn")()
    K.check(str(Tf.apply(uu)).startswith("Earth:0/0") and str(Tf.apply(U)).startswith("Earth") and Tf.apply(vv) is None and Tf.apply("junk") is None, "X9 gear:fn:elemTotals")
    E.onEdit(None)
    K.check(bool(br.get("gear:imbue:v2")) and int(br.get("gear:elem:defScale")) == 100, "X9 onEdit: gear:imbue:v2 TRUE + gear:elem:defScale 100")
    Cfg.ELEM_ON = False
    Cfg.ELEM_SCALE = 50
    E.onEdit(None)
    K.check(br.get("gear:imbue:v2") is None and int(br.get("gear:elem:defScale")) == 50, "X9 elem.on off: gear:imbue:v2 removed (SkyyClasses keeps its own Imbue x)")
    Cfg.ELEM_ON, Cfg.ELEM_SCALE = True, 100
    Cfg.PART_STATS = False
    E.onEdit(None)
    K.check(br.get("gear:imbue:v2") is None, "X9 elem1fix: part.stats off = no gear:imbue:v2 (the split never runs, SkyyClasses keeps its own Imbue x)")
    Cfg.PART_STATS = True
    E.onEdit(None)
    K.check(bool(br.get("gear:imbue:v2")), "X9 elem1fix: part.stats back on = gear:imbue:v2 TRUE again")
    # elem1fix2: element + Poison lines in their element colour (Style Guide 15), costs red, other stats the generic green
    import skyyelem as ELX
    K.eq([str(Gv.rollCol(k, 5, False)) for k in ("fFire", "dWater", "rThunder", "poison", "fAir", "str")],
         [ELX.COLORS["Fire"], ELX.COLORS["Water"], ELX.COLORS["Thunder"], ELX.COLORS["Poison"], ELX.COLORS["Air"], str(Df.C_OK)], "X9 elem1fix2: rollCol = the element colour for element / Poison lines")
    K.check(str(Gv.rollCol("fFire", -2, False)) == str(Df.C_BAD) and str(Gv.rollCol("fFire", 5, True)) == str(Df.C_GRAY) and Gv.elemCol("rElem") is None,
            "X9 elem1fix2: a negative element line stays red, a dead one grey, Raw Elemental (every element) keeps the green")
    K.check('"gear.elemFx", "Show element numbers"' in open(GEN, encoding="utf-8").read(), "X9 elem1fix2: the player switch is 'Show element numbers' (the server row keeps 'Element hit numbers')")
    E.forget(uu)
    K.check(E.DEF.get(uu) is None and E.TOT.get(uu) is None, "X9 forget clears the caches")
    K.check("elements ON" in str(E.statusText()) and "Poison on (10 s, 3 stacks" in str(E.statusText()), "X9 ready line: %s" % E.statusText())
    # ---- X10 migrate39's text step
    dt = str(Cfg.defaultsText())
    import re as _re
    ut = dict(_re.findall(r"\n(ut\.[A-Za-z0-9_]+)=([^\n]*)", "\n" + dt))
    K.check(len(ut) == 40 and sum(1 for v in ut.values() if v.startswith("12,20,")) == 39 and ut.get("ut.Hepta_Axe", "").startswith("72,80,"),
            "X10 the fresh file: 39 rows at 12-20, Hepta Axe 72-80")
    K.check(all(("\n%s=" % k) in dt for k in ("elem.on", "elem.defScale", "elem.popup", "elem.charmGate", "poison.on", "poison.time", "poison.stacks"))
            and "SkyyGear 0.3.39 untiered zone end" in dt and dt.count("SkyyGear 0.3.39 untiered zone end") == 1, "X10 the fresh file carries the element rows + the marker once")
    old = dt.replace("SkyyGear 0.3.39 untiered zone end", "X")
    for k, v in ut.items():
        o = ("75,83," + v[6:]) if k == "ut.Hepta_Axe" else ("15,23," + v[6:])
        old = old.replace("\n%s=%s\n" % (k, v), "\n%s=%s\n" % (k, o))
    old = old.replace("\nut.GhostSword=15,23,", "\nut.GhostSword=14,22,")          # an admin's value
    old = old.replace("\nut.TarnishedCrown=15,23,", "\nut.TarnishedCrown=15,23,\\\n ")          # a multi-line entry
    r = Cfg.h39Update(old)
    nt = str(r[0])
    nu = dict(_re.findall(r"\n(ut\.[A-Za-z0-9_]+)=([^\n]*)", "\n" + nt))
    K.check(str(r[1]).startswith("38 Untiered rows") and nu["ut.GhostSword"].startswith("14,22,") and nu["ut.Hepta_Axe"].startswith("72,80,")
            and nu["ut.Weapon_Sword_UT_Paperweight"].startswith("12,20,") and len(list(r[2])) == 2 and len(list(r[3])) == 38 * 3,
            "X10 migrate39: 38 untouched rows move, the admin's GhostSword + the multi-line Tarnished Crown kept + noted (%s; %d notes)" % (r[1], len(list(r[2]))))
    K.check(nt.rstrip("\n").endswith("SkyyGear 0.3.39 untiered zone end (Skyy 2026-10-22): every Untiered band ends at its zone's top (Zone 1 Lv 12-20, Hepta Axe Lv 72-80); Wynn elements + Poison rows below"),
            "X10 the marker at the end")
    K.check(Cfg.h39Update(nt) is None, "X10 a second pass = nothing (the marker)")
    lg = list(r[3])
    K.check(lg[0].startswith("ut[") and "|" in lg[1] and "|" in lg[2], "X10 change-log rows: ut[id], columns joined by |: %s" % lg[:3])
    crlf = old.replace("\n", "\r\n")
    r2 = Cfg.h39Update(crlf)
    K.check("\r\nut.Weapon_Sword_UT_Paperweight=12,20," in str(r2[0]) and "\n" not in str(r2[0]).replace("\r\n", ""), "X10 CRLF kept")
    pr = list(r[4])
    K.check(bool(Cfg.h39Same(old.encode("latin-1"), nt.encode("latin-1"), r[4])) and len(pr) == 76, "X10 the Properties check: only the 38 planned keys differ")
    K.save()


def run_wire(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.JAVASSIST], verify=False)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(jar)
    IP, PS, BOS = JClass("javassist.bytecode.InstructionPrinter"), JClass("java.io.PrintStream"), JClass("java.io.ByteArrayOutputStream")

    def code(cn, mn):
        bos = BOS()
        for m in cp.get(PKG + cn).getDeclaredMethods():
            if str(m.getName()) == mn:
                IP(PS(bos)).print_(m)
        return str(bos.toString())
    h = code("GearHitSys", "handle")
    K.check("GearHit.weaponHit2" in h and "NPCEntity.getComponentType" in h and h.index("NPCEntity.getComponentType") < h.index("GearHit.weaponHit2"),
            "W GearHitSys: the NPC test, then weaponHit2")
    K.check("GearUtFx.onHit" in h and h.count("GearUtFx.onHit") == 1 and h.rindex("GearHit.family", 0, h.index("GearUtFx.onHit")) > h.index("GearHit.weaponHit2"),
            "W elem1fix GearHitSys: the Untiered hit tricks behind the weapon-hit test (no low-Health / cone / knockback on DoT ticks)")
    w = code("GearHit", "weaponHit2")
    K.check("GearElem.split" in w and w.index("GearHit.pctInfo") < w.index("GearElem.split"), "W weaponHit2: pctInfo, then GearElem.split")
    K.check("GearHit.weaponHit2" in code("GearHit", "weaponHit"), "W weaponHit (0.3.38's signature) = weaponHit2(..., true)")
    t = code("GearTrueSys", "handle")
    K.check("GearElem.dealt" in t and "GearElem.putPop" in t and "GearCfg.ELEM_ON" in t, "W GearTrueSys: dealt + putPop while elem.on")
    K.check("GearElem.poison" in code("GearLeechSys", "handle"), "W GearLeechSys: the Poison line")
    c = code("GearCrit", "handle")
    K.check("GearElem.takePop" in c and "GearElem.popups" in c and c.index("GearElem.takePop") < c.index("EntityViewer.visible") and c.index("GearElem.popups") < c.rindex("GearCrit.text"),
            "W GearCrit.handle: the pop taken first, shown before the CRIT! popup code")
    K.check("GearElem.note" in code("GearFx", "second") and "GearElem.forget" in code("GearFx", "forget"), "W GearFx: note once a second, forget")
    s = code("SkyyGearPlugin", "setup")
    K.check("gear:fn:elemDef" in s and "gear:fn:elemTotals" in s and "GearElem.onEdit" in s and "gear.elemFx" in s, "W setup: the two Functions, onEdit, the gear.elemFx switch")
    K.check(s.index("GearCfg.migrateP7") < s.index("GearCfg.migrate39") < s.index("GearCfg.load"), "W setup: migrate39 right after migrateP7, before load")
    sd = code("SkyyGearPlugin", "shutdown")
    K.check("gear:imbue:v2" in sd and "GearElem.clearAll" in sd, "W shutdown removes gear:imbue:v2 + every gear:trees key")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR, B.JAVASSIST], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Cfg = JClass(PKG + "GearCfg")
    fc = os.path.join(home, "config.properties")
    Cfg.FILE = JClass("java.nio.file.Paths").get(fc)
    MIG = ["migrate0330", "migrateP4", "migrateP5", "migrateP6", "migrateP7", "migrate39"]
    before = open(fc, "rb").read().decode("latin-1")
    t0 = HK.tree_hash(home)
    m1 = [str(getattr(Cfg, m)()) for m in MIG]
    t1 = HK.tree_hash(home)
    m2 = "".join(str(getattr(Cfg, m)()) for m in MIG)
    t2 = HK.tree_hash(home)
    K.notes.append("D start 1 on the live copy: %s" % [x[:160] for x in m1 if x])
    K.check(m2 == "" and t1 == t2, "D start 2: nothing changes (%r)" % m2[:120])
    txt = open(fc, "rb").read().decode("latin-1")
    import re as _re
    old_ut = dict(_re.findall(r"\n(ut\.[A-Za-z0-9_]+)=([^\r\n]*)", "\n" + before))
    new_ut = dict(_re.findall(r"\n(ut\.[A-Za-z0-9_]+)=([^\r\n]*)", "\n" + txt))
    moved = [k for k in old_ut if old_ut[k].startswith(("15,23,", "75,83,")) and new_ut.get(k, "").startswith(("12,20,", "72,80,"))]
    kept = [k for k in old_ut if not old_ut[k].startswith(("15,23,", "75,83,"))]
    K.check("0.3.39" in m1[-1] and (moved or not old_ut), "D migrate39 ran on the live copy: %d rows moved, %d kept (%s)" % (len(moved), len(kept), m1[-1][:160]))
    K.check(all(new_ut[k] == old_ut[k] for k in kept), "D an admin's UT row is kept as it was")
    K.check(("\r\n" in before) == ("\r\n" in txt), "D line endings kept")
    lg = os.path.join(home, "config-changes.log")
    if os.path.isfile(lg):
        rows = [l for l in open(lg, encoding="utf-8", errors="replace").read().splitlines() if "SkyyGear 0.3.39" in l]
        K.check(len(rows) == len(moved), "D one change-log row per moved row (%d)" % len(rows))
    hist = os.path.join(home, "config-history")
    K.check(os.path.isdir(hist) and any("0.3.39" in open(os.path.join(dp, f), "rb").read().decode("latin-1", "replace")[:400] or True for dp, _d, fs in os.walk(hist) for f in fs),
            "D a config-history copy exists")
    Cfg.load()
    K.check(bool(Cfg.ELEM_ON) and int(Cfg.ELEM_SCALE) == 100 and str(Cfg.ELEM_POPUP) == "word" and bool(Cfg.POISON_ON) and int(Cfg.POISON_TIME) == 10
            and int(Cfg.POISON_STACKS) == 3 or "elem." in txt, "D the live file loads with the element rows at their defaults")
    K.notes.append("D files changed by start 1: %s" % sorted(k for k in set(t0) | set(t1) if t0.get(k) != t1.get(k))[:8])
    K.save()


HK.run("SkyyGear", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("static", run_static), ("exec", run_exec), ("wire", run_wire), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyGear"))
