"""Harness for SkyyClasses 0.1.51 (Augments round A1: the element states engine + classes:fn:elemHit; tools/classes_0_1_51_patch.py; pairs
with SkyyMobs 0.1.23, whose harness checks its side of the call). Build first:
    python tools/classes_0_1_51_patch.py && python SkyyClasses/build_skyyclasses_0.1.51.py
    python SkyyClasses/test_skyyclasses_0.1.51.py [--keep] [--expect-dump]

Phases (fresh child JVMs, tools/harness_kit.py):
  S     static   the patch re-runs to identical bytes; +3 classes (ElemSt, ElemCtx, ElemHitFn), no new system / command; line endings kept;
                 the jar gains exactly the 2 look effects (SkyyElem_Burning = a damage-free child of vanilla Burn_Template, SkyyElem_Wet);
                 the only other non-class change = the manifest
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.1.50 -> 0.1.51 (EXPECT below)
  X46 / W46 / W47 / X48 / ALT / SM / W50  the older EXEC + WIRE phases on the 0.1.51 jar (unchanged behaviour; their element statuses run
                 through the engine now - the phases that read the old ones run with elem.on OFF = the 0.1.50 path, which is the point)
  EL    exec     EXECUTES the engine on the 0.1.25 engine stand-ins (real Store / CommandBuffer subclass, real Refs, real EntityStatMaps,
                 real NPCEntity role names): every state (Wet, Chill -> Frozen, Burning, Shocked + jump + flinch, Quaked, Gusted), every cell of
                 the matrix that has a reaction (STEAM, DOUSE, MELT, THAW, FANNED, ELECTROCUTE, GROUNDED x2, STORM x2, CONDUCT, MUD x2,
                 SMOTHER, SHATTER, SANDBLAST x2, WILDFIRE, WIND CHILL) with its damage / cause, the SNAPSHOT order (a Fire + Water hit soaks
                 AND burns, the next one steams), the reaction cooldown, one word a hit (the strongest), the same-hit guard, own-element
                 immunity (mob:fn:elemOf), water / rain (elem.rainWet on / off, the weather list), the Burning DoT ending in water through the
                 REAL AbilTick, BOSSES (x0.5, 8 s immunity, flinch once in 4 s, no knockback; 1,000 Thunder + Water + Earth hits never pass
                 the duty cap), PLAYERS (an element mob's hit: Wet, ELECTROCUTE through a non-entity source, x0.5 CC, 5 s immunity, element
                 Defence shortens the state, elem.players OFF; PvP off / on / party), Imbue routed through the engine (statusOn) vs
                 elem.on OFF (the 0.1.50 statuses), Poison never in the engine, gearStates
  BR    exec     classes:fn:elemHit: bad arguments FALSE (never throws), the clamps, the queued kind 29 job, its run through the REAL AbilTick
                 (refs from the UUIDs, the states land), the job cap (ELEM_DROP), elem.on OFF
  (EL)  FIX 2   the second critic pass, EXECUTED (E15): gearStates needs elem.on, the boss attack-start block (no Hurt flinch, never inside
                 Hit_Interrupt_Enraged, the 4 s gap live), Frozen = the real (cut) hold, the flood prune keeps CC clocks, ElemArc = no second
                 Weak / Resist (the class Shock jump keeps ElemShock + its one affinity), one jump per recipient per reactCd under an AoE,
                 Storm widens Electrocute, Wildfire after Douse / on this hit's own stack, the element-hit queue's own cap, the per-hit env
                 cache (<= 32 lookups), Sandblast weaken 0 = off
  W     wire     the bytecode of every new hook site calls its method
  LIVE  start twice on a scratch COPY of Skyy's live Skyy_SkyyClasses (0.1.48's live phase: every update in setup's order + load + UpSk + CfgPub)
  AA    engine-access audit
NOT COVERED (UNVERIFIED in game): the client showing SkyyElem_Burning / SkyyElem_Wet, Hit_Interrupt_Flinch on a real NPC / player, a
CombatTextUpdate sent from the AbilTick job (outside the damage group), the real fluid / weather reads (WorldUtil-style block read +
WeatherTracker / WorldSupport), knockback on a player, how it feels.
Scratch: tools/dev/scratch/aug_a1/cls (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, time, shutil, subprocess, zipfile, importlib.util, inspect, textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "aug_a1", "cls")]
import harness_kit as HK
import skyybuild as B
import skyyelem as EL

_ORIG_COMPARE0 = HK.run_compare
_s = importlib.util.spec_from_file_location("test_skyyclasses_0_1_50", os.path.join(HERE, "test_skyyclasses_0.1.50.py"))
T50 = importlib.util.module_from_spec(_s)
_argv = list(sys.argv)
_s.loader.exec_module(T50)
sys.argv[:] = _argv
HK.run_compare = _ORIG_COMPARE0
T48 = T50.T48

VERSION, OLD = "0.1.51", "0.1.50"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyClasses-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyClasses-%s.jar" % OLD)
GEN = os.path.join(HERE, "build_skyyclasses_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyclasses_%s.py" % OLD)
PATCH = os.path.join(TOOLS, "classes_0_1_51_patch.py")
PKG = "com.skyy.classes."
SCRATCH = os.path.abspath(HK.arg("--dir"))
NEW_FILES = ["Server/Entity/Effects/SkyyClasses/SkyyElem_Burning.json", "Server/Entity/Effects/SkyyClasses/SkyyElem_Wet.json"]
ADDED = ["ElemCtx", "ElemHitFn", "ElemSt"]
EXPECT = {   # checked 2026-10-30 (the class compare 0.1.50 -> 0.1.51; every member a change of tools/classes_0_1_51_patch.py: the engine
    # methods + fields in Abil, the 5 rows + 2 numbers rows (AbilCfg / AbilNum / the Cfg* kit classes / ClassCfg / KitMigrate / the plugin = the
    # version strings + rows), statusOn / hitLanded3 / dotTick / runJob5 / causeId / AbilWorld.dots hooks, setup / shutdown the bridge)
    'Abil': ['+f E2W', '+f ECB', '+f ECG', '+f ECR', '+f EF_BURNFX', '+f EF_FLINCH', '+f EF_INTERRUPT', '+f EF_WETFX', '+f ELEMENV', '+f ELEM_DMG', '+f ELEM_DROP', '+f ELEM_IN', '+f ELEM_POPS', '+f ELEM_REACT', '+f ELEM_RUN', '+f ELS2', '+f FX_BOLT2', '+f FX_ICEBRK', '+f FX_MUD', '+f FX_SAND', '+f FX_STEAM', '+f FX_STONE', '+f FX_WET', '+f FX_ZAP', '+f LAST_EL', '+f POPS', '+f RN', '+f W2E', '+f WN', '+m burnLive', '+m burnLive0', '+m burnMark', '+m burnMark0', '+m burnMarkNew', '+m burnSnap', '+m burnSnap0', '+m burnSum', '+m burnSum0', '+m elemAir', '+m elemBoss', '+m elemBurn', '+m elemBurnEnd', '+m elemBurnLone', '+m elemBurnOk', '+m elemCc', '+m elemCcSet', '+m elemChill', '+m elemClass', '+m elemDmg', '+m elemEarth', '+m elemEnv', '+m elemEnvBits', '+m elemFire', '+m elemFlinch', '+m elemFx', '+m elemIdle', '+m elemInWater', '+m elemJob', '+m elemJump', '+m elemNext', '+m elemOwn', '+m elemPop', '+m elemPrune', '+m elemPrune0', '+m elemRes', '+m elemRun', '+m elemRx', '+m elemSlow', '+m elemSoaked', '+m elemSpread', '+m elemSt', '+m elemText', '+m elemThunder', '+m elemTick', '+m elemUuid', '+m elemVictim', '+m elemWant', '+m elemWater', '+m elemWeaken', '+m elemWet', '+m elemWetAt', '+m elemWorld', '+m elemWorldReal', '+m elsOf', '+m envHit', '+m fluidWater', '+m gearStates', '+m isPl', '+m pvpOn', '+m rainAt', '+m rainy', '+m skyOpen', '~<clinit>', '~m attune', '~m bubCast', '~m bubPick', '~m bubText', '~m causeId', '~m dotTick', '~m hitLanded3', '~m imbueCast', '~m runJob5', '~m statusOn'],
    'AbilCfg': ['+f ELEM_ON', '+f ELEM_POP', '+f ELEM_PVP', '+f ELEM_RAIN', '+f ELEM_RAINIDS', '+f EX_NUMS', '+f RX_NUMS', '~<clinit>', '~m read'],
    'AbilNum': ['+f EX_BOSSFLINCH', '+f EX_BOSSIMMUNE', '+f EX_BURNPCT', '+f EX_CCGAP', '+f EX_CHAINMAX', '+f EX_CHAINRANGE', '+f EX_ENVEVERY', '+f EX_FANSTACKS', '+f EX_FLINCHEVERY', '+f EX_FLINCHGAP', '+f EX_FLINCHTIME', '+f EX_MUDSLOW', '+f EX_MUDTIME', '+f EX_PVPCC', '+f EX_PVPIMMUNE', '+f EX_PVPKB', '+f EX_REACTCD', '+f EX_SAMEHIT', '+f EX_SANDTIME', '+f EX_SANDWEAKEN', '+f EX_SHOCKPCT', '+f EX_WETTIME', '+f EX_WINDSWEPT', '+f RX_CLASSPART', '+f RX_DOUSE', '+f RX_ELECFLINCH', '+f RX_ELECTROCUTE', '+f RX_FANBURN', '+f RX_FANNED', '+f RX_FANTIME', '+f RX_GROUNDED', '+f RX_MELT', '+f RX_SANDBLAST', '+f RX_SHATTER', '+f RX_STEAM', '+f RX_STORMJUMPS', '+f RX_STORMRANGE', '+f RX_WILDRANGE', '+f S_EX', '+f S_RX', '~<clinit>', '~m sync'],
    'AbilStore': ['+f ELEMOWN', '+f ELEMS', '~<clinit>'],
    'AbilWorld': ['+m elemFull', '~m dots'],          # fix 2: + the element-hit queue's own cap
    'CfgFile': ['~<clinit>'],
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'CfgRows1': ['~<clinit>'],
    'CfgRows2': ['~<clinit>'],
    'ClassCfg': ['~<clinit>'],
    'KitMigrate': ['~m runOnce'],
    'SkyyClassesPlugin': ['~m setup', '~m shutdown'],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}


def _compare(out, jar, old_jar, pkg, expect, added, removed=()):
    """the kit compare on copies WITHOUT the 2 new effect files (the static phase checks those exactly)"""
    cps = []
    for j_, tag_ in ((jar, VERSION), (old_jar, "old")):
        cp = os.path.join(SCRATCH, "compare-%s.jar" % tag_)
        with zipfile.ZipFile(j_) as zi, zipfile.ZipFile(cp, "w", zipfile.ZIP_DEFLATED) as zo:
            for n in zi.namelist():
                if n not in NEW_FILES:
                    zo.writestr(n, zi.read(n))
        cps.append(cp)
    _ORIG_COMPARE0(out, cps[0], cps[1], pkg, expect, added, removed)


HK.run_compare = _compare


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyClasses 0.1.51 - build script') and g.count('VERSION = "0.1.51"') == 1, "S header + VERSION")
    K.eq((g.count("registerSystem("), g.count("registerCommand("), g.count("makeClass(")), (o.count("registerSystem("), o.count("registerCommand("), o.count("makeClass(") + 3),
         "S +3 classes, no new system / command")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    K.eq((sorted(n for n in nb - na if not n.endswith(".class")), sorted(na - nb)), (sorted(NEW_FILES), []), "S the jar gains exactly the 2 look effects")
    K.eq(sorted(n for n in nb - na if n.endswith(".class")), sorted("com/skyy/classes/%s.class" % c for c in ADDED), "S ... and the 3 classes")
    K.eq(sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n)), ["manifest.json"], "S the only other non-class change: the manifest")
    bj = json.loads(zb.read(NEW_FILES[0]).decode("utf8"))
    with zipfile.ZipFile(T50.ASSETS) as az:
        vb = json.loads(az.read("Server/Entity/Effects/Status/Burn.json").decode("utf-8-sig"))
        vt = json.loads(az.read("Server/Entity/Effects/Status/Burn_Template.json").decode("utf-8-sig"))
        wx = sorted(n.rsplit("/", 1)[1][:-5] for n in az.namelist() if n.startswith("Server/Weathers/") and n.endswith(".json"))
    K.check(bj["Parent"] == "Burn_Template" and "DamageCalculator" not in bj and bj["ApplicationEffects"] == vb["ApplicationEffects"]
            and vt["ApplyConditions"][0]["Id"] == "InFluid" and vt["ApplyConditions"][0]["Inverse"] is True,
            "S SkyyElem_Burning = vanilla Burn's look, no damage, Parent Burn_Template (its no-fire-in-water rule)")
    wj = json.loads(zb.read(NEW_FILES[1]).decode("utf8"))
    K.check(wj["ApplicationEffects"]["EntityTopTint"] == EL.COLORS["Water"] and wj["Debuff"] is True and "DamageCalculator" not in wj, "S SkyyElem_Wet = the Water blue tint, no damage")
    import re
    m = re.search(r'_r\("elem.rainWeathers", "ELEM_RAINIDS", "text", \'([^\']*)\'', g)
    rain = m.group(1).split(",") if m else []
    K.check("Zone1_Rain" in rain and "Zone4_Storm" in rain and all(w in wx for w in rain)
            and not [w for w in rain if any(x in w.lower() for x in ("sand", "ash", "snow", "void"))], "S the rain list = vanilla Rain / Storm weathers without sand / ash / snow / void: %s" % rain)
    K.check("elem.rainWet" in g and "Rain makes you Wet" in g, "S the rain setting row (Skyy \"Yes, with a setting\")")
    K.save()


def _elem_src():
    """the 0.1.50 SM phase's engine stand-ins (its run_exec up to its first own check) + THIS round's EL body below"""
    src = inspect.getsource(T50.run_exec)
    cut = src.index("    # ---------------- SM1 the tables")
    head = src[:cut].replace("def run_exec(out, jar, scratch, _home):", "def run_elem(out, jar, scratch, _home):", 1)
    body = inspect.getsource(_el_body)
    body = body[body.index(":\n") + 2:]          # the body of _el_body (already indented 4)
    return head + body


def _el_body():
    # ================================================================================================ 0.1.51 THE ELEMENT STATES ENGINE
    import jpype as _jp
    JIntA, JDblA = JArray(JInt), JArray(JDouble)
    TBc = JClass("abilharness.TBuf")
    DMGc = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage")
    AD_ = C("AbilDmg")
    ES_ = C("ElemSt")
    NPCc_ = JClass("com.hypixel.hytale.server.npc.entities.NPCEntity")
    AN.sync()
    WN = [str(x) for x in A.WN]
    EAR, THU, WAT, FIR, AIR = 0, 1, 2, 3, 4
    POPS = ArrayList()
    A.POPS = POPS
    ENV = {}
    A.ELEMENV = Fn(lambda o: JInt(ENV.get(int(list(o)[0].getIndex()), 0)))
    ROLEEL = {}
    br.put("mob:fn:elemOf", Fn(lambda o: None if ROLEEL.get(str(o)) is None else JString(ROLEEL[str(o)])))
    DEFS = {}
    br.put("gear:fn:elemDef", Fn(lambda o: JInt(DEFS.get((str(list(o)[0]), str(list(o)[1])), 0))))
    T0 = [10 ** 12]

    def at(ms_):
        return JLong(T0[0] + ms_)

    def rmob(i_, x, z, role, hp=1000.0):
        r_ = REFc(tst, i_)
        n_ = U.allocateInstance(NPCc_.class_)
        setf(n_, NPCc_, "roleName", role)
        put(r_, NPCc_.getComponentType(), n_)
        put(r_, ESMc.getComponentType(), stats(hp=hp, hpmax=hp))
        put(r_, TCc.getComponentType(), TCc(V3(x, 64.0, z), R3(0.0, 0.0, 0.0)))
        uu = UUID.fromString("00000000-0000-0000-00ee-%012d" % i_)
        ebu.put(uu, r_)
        return r_, uu

    def pw(**kw):
        a_ = [0, 0, 0, 0, 0]
        for k_, v_ in kw.items():
            a_[WN.index(k_)] = v_
        return JIntA(a_)

    def pt(**kw):
        a_ = [0.0] * 5
        for k_, v_ in kw.items():
            a_[WN.index(k_)] = float(v_)
        return JDblA(a_)

    def ev_clear():
        TBc.EVENTS.clear()

    def dmgs():
        o_ = []
        for e_ in TBc.EVENTS:
            d_ = e_[1]
            if isinstance(d_, DMGc) or "Damage" in str(d_.getClass().getName()):
                o_.append((int(e_[0].getIndex()), str(AD_.whatOf(d_)), round(float(d_.getAmount()), 3), str(d_.getSource().getClass().getName()).rsplit(".", 1)[-1]))
        return o_

    def reset():
        AS.ELEMS.clear()
        AS.ELEMOWN.clear()
        AS.DOTS.clear()
        AS.SHOCKD.clear()
        AS.STAGD.clear()
        AS.FROZEN.clear()
        AS.IMBUE.clear()
        EFX.clear()
        PUSH.clear()
        POPS.clear()
        PSEEN.clear()
        ev_clear()
        ENV.clear()
        aw.jobs.clear()
        AC.ELEM_ON = True
        AC.ELEM_RAIN = True
        AC.ELEM_PVP = True
        AC.ELEM_POP = True

    def H(t_, att_r, att_u, p_, q_, ms_, hit=100.0, heavy=False, src=0, st=1.0, du=1.0):
        r_ = A.elemRun(tbuf, t_, att_r, att_u, p_, q_, JDouble(hit), JBoolean(heavy), JInt(src), JDouble(st), JDouble(du), at(ms_))
        return None if r_ is None else str(r_)

    def S(t_):
        return AS.ELEMS.get(t_)

    def burns(t_):
        l_ = AS.DOTS.get(t_)
        return [] if l_ is None else [(round(float(j_.amount), 3), int(j_.left)) for j_ in l_ if str(j_.what) == "ElemBurn" and int(j_.left) > 0]

    def efx_has(pfx):
        return [x for x in efx() if x.startswith(pfx)]

    reset()
    eu, er_, epr, em, epl, emsc = player(151, 500.5, 64.0, 0.5, "Elem1")
    setclass(eu, "Warrior")
    m1, m1u = rmob(1511, 502.5, 0.5, "Trork_Warrior")
    m2, m2u = rmob(1512, 504.0, 0.5, "Trork_Warrior")
    m3, m3u = rmob(1513, 505.0, 2.5, "Trork_Warrior")
    NEARL[:] = [m1, m2, m3]

    # ---------------- E1 the tables
    ck(WN == EL.NAMES and [int(x) for x in A.E2W] == [3, 2, 0, 1, 4] and [int(A.W2E[int(A.E2W[e_])]) for e_ in range(5)] == [0, 1, 2, 3, 4]
       and [str(A.ELN[int(A.W2E[w_])]) for w_ in range(5)] == EL.NAMES, "E1: the Wynn bridge order = tools/skyyelem.py NAMES; E2W / W2E map Classes' ELN order")
    ck(len(list(A.RN)) == 15 and bool(AC.ELEM_ON) and bool(AC.ELEM_RAIN) and bool(AC.ELEM_PVP) and bool(AC.ELEM_POP), "E1: 15 reaction words; the 4 switches default ON")
    ck((float(AN.EX_WETTIME), float(AN.EX_BURNPCT), float(AN.EX_SHOCKPCT), float(AN.EX_REACTCD), float(AN.EX_BOSSIMMUNE), float(AN.EX_PVPCC), float(AN.RX_STEAM), float(AN.RX_SHATTER))
       == (6.0, 2.0, 30.0, 1.0, 8.0, 50.0, 25.0, 50.0), "E1: the spec numbers (Wet 6 s, Burning 2 %, jump 30 %, reaction cd 1 s, boss immunity 8 s, PvP CC 50 %, Steam 25 %, Shatter 50 %)")
    old_ex = str(AC.EX_NUMS)
    AC.EX_NUMS = "wetTime=9"
    AN.sync()
    ck(float(AN.EX_WETTIME) == 9.0 and float(AN.EX_BURNPCT) == 2.0, "E1: ab.ElemStates.numbers is read live (a missing key = its default)")
    AC.EX_NUMS = old_ex
    AN.sync()

    # ---------------- E2 Water: Wet -> Chilled -> Frozen (3 Chills in 3 s; a Chilled target counts double)
    r1 = H(m1, er_, eu, pw(Water=5), pt(Water=10), 0)
    ck(r1 is not None and r1.startswith("W") and efx_has("SkyyElem_Wet:6") and int(S(m1).wetUntil) == T0[0] + 6000, "E2: a Water hit = Wet 6 s (the look): %s" % r1)
    EFX.clear()
    r2 = H(m1, er_, eu, pw(Water=5), pt(Water=10), 300)
    ck("chill=1" in r2 and efx_has("SkyyAbility_Spd_15:3"), "E2: Water on a Wet target = Chilled (-15 %% speed 3 s): %s %s" % (r2, efx()))
    EFX.clear()
    r3 = H(m1, er_, eu, pw(Water=5), pt(Water=10), 600)
    ck("chill=3" in r3 and "frozen=1.5" in r3 and efx_has("Freeze:1.5") and int(S(m1).frozenUntil) == T0[0] + 600 + 1500,
       "E2: ... Water on a Chilled target counts double -> 3 Chills in 3 s = Frozen 1.5 s: %s" % r3)

    # ---------------- E3 Earth on Frozen = SHATTER (+50 % of the Earth part, the freeze ends) + the reaction cooldown
    EFX.clear()
    ev_clear()
    POPS.clear()
    r4 = H(m1, er_, eu, pw(Earth=5), pt(Earth=20), 900)
    ck("rx:SHATTER" in r4 and (1511, "ElemShatter", 10.0, "Damage$EntitySource") in dmgs() and efx_has("-Freeze") and int(S(m1).frozenUntil) == 0
       and AS.FROZEN.get(m1) is None and list(map(str, POPS)) == ["SHATTER:0"], "E3: Earth on Frozen = SHATTER, 10 damage (50 %% of 20, Earth cause), one word: %s %s %s" % (r4, dmgs(), list(POPS)))
    S(m1).frozenUntil = T0[0] + 5000
    r5 = H(m1, er_, eu, pw(Earth=5), pt(Earth=20), 1200)
    ck("rx:SHATTER" not in r5, "E3: ... a second SHATTER within reactCd 1 s does not happen: %s" % r5)
    S(m1).frozenUntil = 0

    # ---------------- E4 Fire: Burning; Fire on Wet = STEAM (no Burning); the snapshot (Fire + Water burns AND soaks)
    reset()
    r6 = H(m2, er_, eu, pw(Fire=5), pt(Fire=10), 0, hit=100.0)
    ck("burn=2" in r6 and burns(m2) == [(2.0, 4)] and efx_has("SkyyElem_Burning:4"), "E4: a Fire hit = Burning 2 %% of the hit a second (2 / s), 4 s, the look: %s %s" % (r6, burns(m2)))
    reset()
    S0 = A.elemSt(m2, at(0))
    S0.wetUntil = T0[0] + 5000
    r7 = H(m2, er_, eu, pw(Fire=5), pt(Fire=10), 0)
    ck("rx:STEAM" in r7 and burns(m2) == [] and (1512, "ElemFlare", 3.0, "Damage$EntitySource") in dmgs() and int(S(m2).wetUntil) == 0,
       "E4: Fire on Wet = STEAM (+25 %% of the Fire part = 3 rounded, Wet ends, no Burning): %s %s" % (r7, dmgs()))
    reset()
    r8 = H(m2, er_, eu, pw(Fire=5, Water=5), pt(Fire=10, Water=10), 0)
    ck(r8.startswith("WB") and burns(m2) and "rx:" not in r8, "E4: a Fire + Water hit on a dry target soaks AND burns (no self-reaction - the snapshot): %s" % r8)
    r9 = H(m2, er_, eu, pw(Fire=5, Water=5), pt(Fire=10, Water=10), 400)
    ck("rx:DOUSE" in r9 and "rx:STEAM" in r9 and burns(m2) == [], "E4: ... the next one: Water DOUSEs the fire, Fire STEAMs the wet (they alternate): %s" % r9)

    # ---------------- E5 DOUSE / SMOTHER / WILDFIRE / FANNED / THAW / MELT
    reset()
    H(m2, er_, eu, pw(Fire=5), pt(Fire=10), 0)
    ev_clear()
    r10 = H(m2, er_, eu, pw(Earth=5), pt(Earth=10), 300)
    ck("rx:SMOTHER" in r10 and burns(m2) == [] and (1512, "ElemBurn", 8.0, "Damage$EntitySource") in dmgs(), "E5: Earth on Burning = SMOTHER (its 4 ticks x 2 at once): %s %s" % (r10, dmgs()))
    reset()
    H(m2, er_, eu, pw(Fire=5), pt(Fire=10), 0)
    ev_clear()
    r11 = H(m2, er_, eu, pw(Water=5), pt(Water=12), 300)
    ck("rx:DOUSE" in r11 and burns(m2) == [] and (1512, "ElemSteam", 3.0, "Damage$EntitySource") in dmgs() and int(S(m2).wetUntil) > T0[0] + 300, "E5: Water on Burning = DOUSE (+25 %%, the target Wet): %s" % r11)
    reset()
    H(m2, er_, eu, pw(Fire=5), pt(Fire=10), 0)
    r12 = H(m2, er_, eu, pw(Air=5), pt(Air=10), 300)
    b12 = burns(m2)
    ck("rx:WILDFIRE" in r12 and len(b12) == 2 and max(a_ for a_, _l in b12) == 2.5 and 6 in [l_ for _a, l_ in b12] and burns(m1) == [(2.5, 4)],
       "E5: Air on Burning = WILDFIRE: x1.25 burn, +50 %% time, +1 stack, 1 stack spreads to the nearest enemy within 3: %s %s m1 %s" % (r12, b12, burns(m1)))
    reset()
    S(m2) if False else A.elemSt(m2, at(0)).__setattr__("gustUntil", T0[0] + 2000)
    r13 = H(m2, er_, eu, pw(Fire=5), pt(Fire=10), 0)
    ck("rx:FANNED" in r13 and burns(m2) == [(2.0, 6)], "E5: Fire on Windswept = FANNED (+50 %% time = 6 s): %s %s" % (r13, burns(m2)))
    reset()
    A.elemSt(m2, at(0)).chillUntil = T0[0] + 3000
    r14 = H(m2, er_, eu, pw(Fire=5), pt(Fire=10), 0)
    ck("rx:THAW" in r14 and burns(m2) == [] and int(S(m2).chillUntil) == 0 and int(S(m2).wetUntil) > 0, "E5: Fire on Chilled = THAW (Chill ends -> Wet): %s" % r14)
    reset()
    A.elemSt(m2, at(0)).frozenUntil = T0[0] + 1500
    ev_clear()
    r15 = H(m2, er_, eu, pw(Fire=5), pt(Fire=10), 0)
    ck("rx:MELT" in r15 and (1512, "ElemFlare", 5.0, "Damage$EntitySource") in dmgs() and int(S(m2).frozenUntil) == 0 and int(S(m2).wetUntil) > 0, "E5: Fire on Frozen = MELT (+50 %%, -> Wet): %s" % r15)

    # ---------------- E6 Thunder: Shocked + jump + flinch every 2nd; ELECTROCUTE on Wet (jumps to the Wet only); GROUNDED; STORM; CONDUCT
    reset()
    ev_clear()
    r16 = H(m1, er_, eu, pw(Thunder=5), pt(Thunder=10), 0)
    ck("shock" in r16 and "jump=1" in r16 and AS.SHOCKD.get(m1) is not None and abs(float(AS.SHOCKD.get(m1)[1]) - 5.0) < 1e-9 and (1512, "ElemArc", 3.0, "Damage$EntitySource") in dmgs()
       and not efx_has("Hit_Interrupt_Flinch") and S(m2) is not None and int(S(m2).shockUntil) == 0 and AS.SHOCKD.get(m2) is not None and int(S(m2).jumpAt) == T0[0] + 1000,
       "E6: a Thunder hit = Shocked (+5 %% taken), 30 %% of the part jumps to the nearest (m2), no flinch on the 1st: %s %s" % (r16, dmgs()))
    r17 = H(m1, er_, eu, pw(Thunder=5), pt(Thunder=10), 1500)
    ck(efx_has("Hit_Interrupt_Flinch:0.3"), "E6: ... the 2nd Thunder hit flinches 0.25 s: %s" % r17)
    ck(efx_has("Hit_Interrupt_Stunned:0.3"), "E6: ... + vanilla's attack-start block (Hit_Interrupt_Stunned) for the same 0.25 s (fix round): %s" % efx())
    reset()
    A.elemSt(m1, at(0)).wetUntil = T0[0] + 6000
    A.elemSt(m2, at(0)).wetUntil = T0[0] + 6000
    ev_clear()
    r18 = H(m1, er_, eu, pw(Thunder=5), pt(Thunder=10), 0)
    d18 = dmgs()
    ck("rx:ELECTROCUTE" in r18 and (1511, "ElemArc", 5.0, "Damage$EntitySource") in d18 and efx_has("Hit_Interrupt_Flinch:0.4") and (1512, "ElemArc", 3.0, "Damage$EntitySource") in d18
       and not [x for x in d18 if x[0] == 1513], "E6: Thunder on Wet = ELECTROCUTE (+50 %%, a sure 0.4 s flinch, jumps to the Wet m2 only): %s %s" % (r18, d18))
    reset()
    A.elemSt(m1, at(0)).quakeUntil = T0[0] + 4000
    ev_clear()
    r19 = H(m1, er_, eu, pw(Thunder=5), pt(Thunder=10), 0)
    ck("rx:GROUNDED" in r19 and AS.SHOCKD.get(m1) is None and (1511, "ElemGround", 3.0, "Damage$EntitySource") in dmgs() and "jump" not in r19,
       "E6: Thunder on Quaked = GROUNDED (+30 %%, no Shock, no jump): %s" % r19)
    reset()
    A.elemSt(m1, at(0)).gustUntil = T0[0] + 2000
    r20 = H(m1, er_, eu, pw(Thunder=5), pt(Thunder=10), 0)
    ck("rx:STORM" in r20 and "jump=2" in r20, "E6: Thunder on Windswept = STORM (+1 jump): %s" % r20)
    reset()
    H(m1, er_, eu, pw(Thunder=5), pt(Thunder=10), 0)
    A.elemSt(m3, at(0)).wetUntil = T0[0] + 6000
    ev_clear()
    r21 = H(m1, er_, eu, pw(Water=5), pt(Water=10), 300)
    ck("rx:CONDUCT" in r21 and [x for x in dmgs() if x[0] == 1513 and x[1] == "ElemArc"], "E6: Water on Shocked = CONDUCT (the Shock jumps to every Wet enemy within 4): %s %s" % (r21, dmgs()))

    # ---------------- E7 Earth: Quake every 3rd (0.4 s stun, -10 % Defence 4 s); MUD; SANDBLAST; Air: Gust, WIND CHILL, STORM, SANDBLAST
    reset()
    for k_ in range(3):
        rq = H(m3, er_, eu, pw(Earth=5), pt(Earth=10), 2000 * k_)
    sg = AS.STAGD.get(m3)
    ck("quake=0.4" in rq and efx_has("Stun:0.4") and sg is not None and abs(float(sg[1]) - 10.0) < 1e-9, "E7: every 3rd Earth hit = Quaked (0.4 s stun, -10 %% Defence): %s %s" % (rq, efx()))
    reset()
    A.elemSt(m3, at(0)).wetUntil = T0[0] + 6000
    r22 = H(m3, er_, eu, pw(Earth=5), pt(Earth=10), 0)
    ck("rx:MUD" in r22 and int(S(m3).wetUntil) == 0 and efx_has("SkyyAbility_Spd_5:3"), "E7: Earth on Wet = MUD (-25 %% speed 3 s, Wet ends): %s %s" % (r22, efx()))
    reset()
    A.elemSt(m3, at(0)).gustUntil = T0[0] + 2000
    ev_clear()
    r23 = H(m3, er_, eu, pw(Earth=5), pt(Earth=10), 0)
    ck("rx:SANDBLAST" in r23 and (1513, "ElemSand", 2.0, "Damage$EntitySource") in dmgs() and efx_has("SkyyAbility_Weaken_10:3"), "E7: Earth on Windswept = SANDBLAST (+20 %%, deals -10 %% 3 s): %s" % r23)
    reset()
    r24 = H(m3, er_, eu, pw(Air=5), pt(Air=10), 0, heavy=True)
    ck("gust=1" in r24 and len(PUSH) == 1 and int(S(m3).gustUntil) == T0[0] + 2000, "E7: an Air hit = Gusted (+1 block, Windswept 2 s): %s %s" % (r24, [list(p_) for p_ in PUSH]))
    reset()
    A.elemSt(m3, at(0)).wetUntil = T0[0] + 6000
    r25 = H(m3, er_, eu, pw(Air=5), pt(Air=10), 0)
    ck("rx:WIND CHILL" in r25 and "chill=1" in r25, "E7: Air on Wet = WIND CHILL: %s" % r25)
    reset()
    A.elemSt(m3, at(0)).quakeUntil = T0[0] + 4000
    r26 = H(m3, er_, eu, pw(Air=5), pt(Air=10), 0)
    ck("rx:SANDBLAST" in r26, "E7: Air on Quaked = SANDBLAST: %s" % r26)
    reset()
    H(m3, er_, eu, pw(Thunder=5), pt(Thunder=10), 0)
    r27 = H(m3, er_, eu, pw(Air=5), pt(Air=10), 300)
    ck("rx:STORM" in r27 and "jump=" in r27, "E7: Air on Shocked = STORM (the shock jumps again, +2 range): %s" % r27)
    reset()
    A.elemSt(m3, at(0)).quakeUntil = T0[0] + 4000
    r28 = H(m3, er_, eu, pw(Water=5), pt(Water=10), 0)
    ck("rx:MUD" in r28, "E7: Water on Quaked = MUD: %s" % r28)

    # ---------------- E8 one word a hit (the strongest), the same-hit guard, Power scales, Poison never in the engine
    reset()
    st8 = A.elemSt(m1, at(0))
    st8.wetUntil = T0[0] + 6000
    st8.quakeUntil = T0[0] + 4000
    r29 = H(m1, er_, eu, pw(Thunder=5), pt(Thunder=20), 0)
    ck("rx:ELECTROCUTE" in r29 and "rx:GROUNDED" in r29 and list(map(str, POPS)) == ["ELECTROCUTE:1"], "E8: two reactions, ONE word (the strongest): %s %s" % (r29, list(POPS)))
    reset()
    H(m1, er_, eu, pw(Water=5), pt(Water=10), 0)
    r30 = H(m1, er_, eu, pw(Water=5), pt(Water=10), 50)
    ck(r30 is None and int(S(m1).chillUntil) == 0, "E8: the same attacker + element within 0.1 s = the same hit (no second state): %s" % r30)
    reset()
    r31 = H(m2, er_, eu, pw(Fire=10), pt(Fire=10), 0)
    r32 = H(m3, er_, eu, pw(Fire=1), pt(Fire=10), 0)
    ck(burns(m2) == [(4.0, 4)] and burns(m3) == [(0.4, 4)], "E8: Power 10 = double (4 / s), Power 1 = a fifth (0.4 / s): %s %s" % (burns(m2), burns(m3)))
    ck(H(m2, er_, eu, pw(), pt(Fire=10), 5000) is None, "E8: no Power = no state (damage only)")
    reset()
    A.statusOn(tbuf, m1, er_, eu, JInt(5), JDouble(100.0), JDouble(1.0), JDouble(1.0), at(0), JBoolean(False))
    ck(S(m1) is None and [j_ for j_ in (AS.DOTS.get(m1) or []) if str(j_.what) == "ElemPoison"], "E8: Poison (a weapon modifier, not an element) keeps its own DoT, never the engine")

    # ---------------- E9 own element (mob:fn:elemOf): a Fire mob never burns, a Water mob is always Wet; water + rain
    reset()
    fm, fmu = rmob(1521, 503.0, -1.0, "Skeleton_Burnt_Soldier")
    wm, wmu = rmob(1522, 503.0, -2.0, "Eel_Moray")
    ROLEEL["Skeleton_Burnt_Soldier"] = "Fire"
    ROLEEL["Eel_Moray"] = "Water"
    NEARL[:] = [fm, wm]
    r33 = H(fm, er_, eu, pw(Fire=5), pt(Fire=10), 0)
    ck(burns(fm) == [] and int(S(fm).own) == 3, "E9: a Fire mob never burns: %s" % r33)
    r34 = H(wm, er_, eu, pw(Thunder=5), pt(Thunder=10), 0)
    ck("rx:ELECTROCUTE" in r34 and int(S(wm).own) == 2, "E9: a Water mob is always Wet - Thunder ELECTROCUTEs it at once: %s" % r34)
    r35 = H(wm, er_, eu, pw(Water=5), pt(Water=10), 300)
    ck("chill" not in r35, "E9: ... and never gets Chilled (its own element's state): %s" % r35)
    reset()
    ENV[1511] = 1
    NEARL[:] = [m1, m2, m3]
    r36 = H(m1, er_, eu, pw(Fire=5), pt(Fire=10), 0)
    ck(r36.startswith("W") and burns(m1) == [] and "rx:STEAM" in r36, "E9: standing in water = Wet (a Fire hit steams, never burns, and it stays Wet): %s" % r36)
    reset()
    ENV[1512] = 2
    r37 = H(m2, er_, eu, pw(Earth=5), pt(Earth=10), 0)
    ck("rx:MUD" in r37, "E9: out in rain = Wet (elem.rainWet on): %s" % r37)
    reset()
    AC.ELEM_RAIN = False
    ENV[1512] = 2
    r38 = H(m2, er_, eu, pw(Earth=5), pt(Earth=10), 0)
    ck("rx:MUD" not in r38 and not r38.startswith("W"), "E9: elem.rainWet OFF = rain makes nobody Wet: %s" % r38)
    AC.ELEM_RAIN = True
    ck(bool(A.rainy("zone1_rain")) and bool(A.rainy("Zone4_Storm")) and not bool(A.rainy("Zone2_Sand_Storm")) and not bool(A.rainy("Zone3_Snow")) and not bool(A.rainy(None)),
       "E9: the weather list (any case; sand / snow storms are not rain)")
    # the Burning DoT through the REAL AbilTick ends in water
    reset()
    H(m3, er_, eu, pw(Fire=5), pt(Fire=10), 0)
    ev_clear()
    run_world()
    t1 = [x for x in dmgs() if x[1] == "ElemBurn"]
    ENV[1513] = 1
    S(m3).envAt = 0
    for j_ in list(aw.jobs):
        j_.at = now_ms() - 10
    run_world()
    ck(len(t1) == 1 and t1[0][2] == 2.0 and burns(m3) == [] and len([x for x in dmgs() if x[1] == "ElemBurn"]) == 1,
       "E9: the Burning DoT ticks through the REAL AbilTick (2), then ends when the mob is in water: %s" % dmgs())

    # ---------------- E10 BOSSES: x0.5 CC, 8 s immunity, flinch once in 4 s, no knockback; the duty cap over 1,000 hits
    reset()
    bm, bmu = rmob(1531, 506.0, 0.5, "Goblin_Duke", hp=1.0e7)
    NEARL[:] = [bm]
    for k_ in range(6):
        H(bm, er_, eu, pw(Thunder=5), pt(Thunder=10), 1500 * k_)
    ck(efx_has("Hit_Interrupt_Stunned:0.1") and len(efx_has("Hit_Interrupt_Stunned")) == 2 and not efx_has("Hit_Interrupt_Flinch") and int(S(bm).ccFree) == 0,
       "E10 (fix 2): a boss 'flinch' = ONLY vanilla's attack-start block at x0.5 (0.125 s; no Hurt animation that could cut a wind-up), at most once in "
       "bossFlinch 4 s (6 Thunder hits 1.5 s apart = the 2nd + the 6th), no CC immunity spent: %s %s" % (efx(), int(S(bm).ccFree) - T0[0]))
    r39 = H(bm, er_, eu, pw(Air=5), pt(Air=10), 3000)
    ck("gust=boss" in r39 and len(PUSH) == 0, "E10: no knockback on a boss: %s" % r39)
    reset()
    NEARL[:] = [bm]
    cc_ = 0.0
    for k_ in range(1000):
        e_ = (THU, WAT, EAR)[k_ % 3]
        EFX.clear()
        kw_ = {WN[e_]: 10}
        H(bm, er_, eu, pw(**kw_), pt(**{WN[e_]: 10}), 60 * k_)
        for x_ in efx():
            if x_.split(":")[0] in ("Stun", "Freeze", "Hit_Interrupt_Flinch", "Hit_Interrupt_Stunned") and ":" in x_:
                cc_ += float(x_.split(":")[1]) if x_.split(":")[0] != "Stun" or True else 0.0
    ck(cc_ <= 60.0 * 0.12, "E10: 1,000 Thunder + Water + Earth hits over 60 s on a boss: %.2f s of CC (<= 12 %% duty)" % cc_)

    # ---------------- E11 PLAYERS: an element mob's hit (SkyyMobs' call), PvP off / on / party, elem.players OFF, element Defence
    reset()
    vu_, vr_, vpr, vm, vpl, vmsc = player(152, 520.5, 64.0, 0.5, "Victim1")
    wmob, wmobu = rmob(1541, 521.5, 0.5, "Eel_Moray")
    tmob, tmobu = rmob(1542, 522.5, 0.5, "Spirit_Thunder")
    ROLEEL["Spirit_Thunder"] = "Thunder"
    NEARL[:] = [vr_]
    r40 = H(vr_, wmob, wmobu, pw(Water=5), pt(Water=6), 0, hit=20.0)
    ck(r40 is not None and "player" in r40 and r40.startswith("W"), "E11: a Water mob's hit makes the player Wet: %s" % r40)
    ev_clear()
    r41 = H(vr_, tmob, tmobu, pw(Thunder=5), pt(Thunder=6), 300, hit=20.0)
    d41 = dmgs()
    ck("rx:ELECTROCUTE" in r41 and (152, "ElemArc", 3.0, "Source") in [(a_, b_, c_, "Source" if d_ in ("Source", "Damage$Source", "Damage$1") or "Source" in d_ else d_) for a_, b_, c_, d_ in d41]
       and not [x for x in d41 if x[3] == "Damage$EntitySource"] and efx_has("Hit_Interrupt_Flinch:0.2") and len(POPS) == 0,
       "E11: Wet player + Thunder mob = ELECTROCUTE (a non-entity damage source - SkyyMobs' hit hook never sees it; flinch x0.5; no word): %s %s" % (r41, d41))
    ccf = int(S(vr_).ccFree) - T0[0]
    EFX.clear()
    S(vr_).flinchAt = 0
    H(vr_, tmob, tmobu, pw(Thunder=5), pt(Thunder=6), 2000, hit=20.0)
    ck(ccf == 300 + 200 + 5000 and not efx_has("Hit_Interrupt_Flinch"), "E11: ... then 5 s CC immunity for a player: %s %s" % (ccf, efx()))
    reset()
    DEFS[(str(vu_), "Water")] = 100
    H(vr_, wmob, wmobu, pw(Water=5), pt(Water=6), 0)
    ck(efx_has("SkyyElem_Wet:3"), "E11: element Defence 100 (S 100) halves the Wet time (3 s): %s" % efx())
    DEFS.clear()
    reset()
    AC.ELEM_PVP = False
    ck(H(vr_, wmob, wmobu, pw(Water=5), pt(Water=6), 0) is None, "E11: elem.players OFF = no state on players")
    AC.ELEM_PVP = True
    reset()
    ck(H(vr_, er_, eu, pw(Fire=5), pt(Fire=6), 0) is None, "E11: PvP: the world's PvP off = no state from a player")
    ENV[152] = 4
    r42 = H(vr_, er_, eu, pw(Fire=5), pt(Fire=6), 0, hit=50.0)
    ck(r42 is not None and burns(vr_) == [(1.0, 4)], "E11: ... PvP on = Burning on the player: %s" % r42)
    MEMBERS[str(eu)] = MEMBERS[str(vu_)] = [str(eu), str(vu_)]
    ck(H(vr_, er_, eu, pw(Fire=5), pt(Fire=6), 5000) is None, "E11: ... never a party member")
    MEMBERS.clear()
    reset()
    ck(H(m1, wmob, wmobu, pw(Water=5), pt(Water=6), 0) is None, "E11: a mob's hit on a mob puts no state")
    # a mob's Burning DoT on a player ticks through the REAL AbilTick with a non-entity source
    reset()
    fm2, fm2u = rmob(1543, 521.0, 1.0, "Skeleton_Burnt_Soldier")
    H(vr_, fm2, fm2u, pw(Fire=5), pt(Fire=6), 0, hit=50.0)
    ev_clear()
    run_world()
    d43 = dmgs()
    ck([x for x in d43 if x[0] == 152 and x[1] == "ElemBurn" and x[3] != "Damage$EntitySource"], "E11: a Fire mob's Burning ticks on the player (REAL AbilTick, no entity source): %s" % d43)
    ebu.remove(fm2u)
    for j_ in list(aw.jobs):
        j_.at = now_ms() - 10
    ev_clear()
    run_world()
    d43b = dmgs()
    ck([x for x in d43b if x[0] == 152 and x[1] == "ElemBurn" and x[3] != "Damage$EntitySource"] and burns(vr_),
       "E11 (fix round): the Fire mob GONE (dead / despawned) - the player's Burning keeps ticking (REAL AbilTick): %s %s" % (d43b, burns(vr_)))
    AS.DOTS.clear()
    aw.jobs.clear()

    # ---------------- E12 Imbue (statusOn) THROUGH the engine; elem.on OFF = the 0.1.50 statuses; gearStates
    reset()
    NEARL[:] = [m1, m2, m3]
    A.statusOn(tbuf, m1, er_, eu, JInt(0), JDouble(100.0), JDouble(1.0), JDouble(1.0), at(0), JBoolean(False))
    ck(S(m1) is not None and burns(m1) == [(10.0, 4)] and efx_has("SkyyElem_Burning"), "E12: a class Fire status (Imbue) runs through the engine (the class Burn 10 %% / s kept): %s" % burns(m1))
    A.statusOn(tbuf, m2, er_, eu, JInt(1), JDouble(100.0), JDouble(1.0), JDouble(1.0), at(0), JBoolean(False))
    ck(int(S(m2).wetUntil) > 0 and not efx_has("SkyyAbility_Spd_15"), "E12: a class Water status = Wet first (spec 5.1), not the old Chill")
    reset()
    AC.ELEM_ON = False
    A.statusOn(tbuf, m2, er_, eu, JInt(1), JDouble(100.0), JDouble(1.0), JDouble(1.0), at(0), JBoolean(False))
    ck(S(m2) is None and efx_has("SkyyAbility_Spd_15"), "E12: elem.on OFF = the 0.1.50 status (Chill at once, no engine): %s" % efx())
    ck(H(m2, er_, eu, pw(Fire=5), pt(Fire=10), 0) is None, "E12: elem.on OFF = the engine does nothing")
    AC.ELEM_ON = True
    ck(not bool(A.gearStates()), "E12: gearStates false without SkyyGear A2")
    br.put("gear:elemStates", Bool.TRUE)
    ck(bool(A.gearStates()), "E12: gearStates true once SkyyGear publishes gear:elemStates")
    br.remove("gear:elemStates")
    reset()
    AS.IMBUE.put(eu, JDblA([float(now_ms() + 60000), 0.0, 30.0, 1.0, 0.0, 0.0]))
    r44 = H(m3, er_, eu, pw(Fire=2), pt(Fire=10), 0)
    ck(burns(m3) == [(2.0, 4)] and "Fire5" in r44, "E12: a bridge hit while Imbue Fire runs takes max(Power, 5) (spec 4.3): %s" % r44)
    AS.IMBUE.clear()

    # ---------------- E13 spam: 200 fast Thunder hits in 2 s on a pack of 4 - words, flinches, jumps stay bounded
    reset()
    pk = [rmob(1550 + i_, 530.0 + i_, 0.5, "Trork_Warrior")[0] for i_ in range(4)]
    NEARL[:] = pk
    POPS.clear()
    for k_ in range(200):
        H(pk[0], er_, eu, pw(Thunder=10, Water=10), pt(Thunder=10, Water=10), 10 * k_ + (k_ // 10) * 110)
    nfl = len(efx_has("Hit_Interrupt_Flinch"))
    ck(len(POPS) <= 2 * 4 and nfl <= 6, "E13: 200 Thunder + Water hits in ~4 s: %d words, %d flinches (reaction cd 1 s, flinch gap 1 s)" % (len(POPS), nfl))
    ck(int(AS.ELEMS.size()) <= 2048, "E13: the state map stays bounded")
    for i_ in range(2100):
        A.elemSt(REFc(tst, 90000 + i_), at(0))
    ck(int(AS.ELEMS.size()) <= 2048, "E13: ... past 2048 victims the old / invalid ones are pruned (%d)" % int(AS.ELEMS.size()))
    K.notes.append("EL counters: in %d run %d react %d pops %d dmg %d" % (int(A.ELEM_IN), int(A.ELEM_RUN), int(A.ELEM_REACT), int(A.ELEM_POPS), int(A.ELEM_DMG)))

    # ---------------- E14 FIX ROUND (2026-10-30): every critic finding that was fixed, EXECUTED on the engine
    reset()
    NEARL[:] = [m1, m2, m3]
    H(m2, er_, eu, pw(Fire=5), pt(Fire=10), 0)
    for k_ in range(6):
        H(m2, er_, eu, pw(Air=5), pt(Air=10), 300 + 1100 * k_)
    b14 = burns(m2)
    ck(b14 and max(a_ for a_, _l in b14) <= 2.5 + 1e-9 and max(l_ for _a, l_ in b14) <= 6 and max([a_ for a_, _l in burns(m1)] or [0.0]) <= 2.5 + 1e-9,
       "FX1 Wildfire fans each Burning stack ONCE: 6 Air hits on a Burning target stay at x1.25 (2.5 / s), <= 6 ticks; the spread stack too: %s m1 %s" % (b14, burns(m1)))
    reset()
    s14 = A.elemSt(m2, at(0))
    s14.gustUntil = T0[0] + 2000
    s14.wetUntil = T0[0] + 5000
    r14 = H(m2, er_, eu, pw(Fire=5), pt(Fire=10), 0)
    ck("rx:STEAM" in r14 and "rx:FANNED" not in r14 and burns(m2) == [], "FX2 Fire on Wet + Windswept: STEAM, no FANNED word (no Burning could start): %s" % r14)
    reset()
    A.elemSt(m2, at(0)).frozenUntil = T0[0] + 1500
    r14 = H(m2, er_, eu, pw(Air=5), pt(Air=10), 0)
    ck("chill=" in r14, "FX3 Air on Frozen adds a Chill (matrix: Chilled / Frozen: Chill +1): %s" % r14)
    reset()
    s14 = A.elemSt(m1, at(0))
    s14.wetUntil = T0[0] + 6000
    s14.shockUntil = T0[0] + 3000
    s14.shockPart = 10.0
    A.elemSt(m2, at(0)).wetUntil = T0[0] + 6000
    ev_clear()
    r14 = H(m1, er_, eu, pw(Thunder=5, Water=5), pt(Thunder=10, Water=10), 0)
    ck("rx:ELECTROCUTE" in r14 and "rx:CONDUCT" in r14 and len([x for x in dmgs() if x[0] == 1512 and x[1] == "ElemArc"]) == 1,
       "FX4 a Thunder + Water hit on a Wet + Shocked target: ELECTROCUTE and CONDUCT share one done set - the Wet neighbour is hit ONCE: %s %s" % (r14, dmgs()))
    reset()
    bu_, bref_, _bpr, _bm, _bpl, _bsc = player(153, 501.5, 64.0, 1.5, "Elem2")
    H(m1, er_, eu, pw(Water=5), pt(Water=10), 0)
    rb14 = H(m1, bref_, bu_, pw(Water=5), pt(Water=10), 40)
    ra14 = H(m1, er_, eu, pw(Water=5), pt(Water=10), 80)
    ck(rb14 is not None and ra14 is None, "FX5 the same-hit guard is per attacker x element: A, then B, then A's duplicate 80 ms later = still the same hit: B %s / A %s" % (rb14, ra14))
    reset()
    fnh14 = C("ElemHitFn")()
    ck(H(m3, er_, eu, pw(), pt(), 0) is None and not bool(fnh14.apply(JArray(JObject)([eu, m1u, pw(), pt(), JDouble(100.0), Bool.FALSE, JString("abil-test")]))),
       "FX6 no Power and no SkyyGear states = nothing (as before)")
    br.put("gear:elemStates", Bool.TRUE)
    AS.IMBUE.put(eu, JDblA([float(now_ms() + 60000), 0.0, 30.0, 1.0, 0.0, 0.0]))
    r14 = H(m3, er_, eu, pw(), pt(), 0, hit=100.0)
    ok14 = fnh14.apply(JArray(JObject)([eu, m1u, pw(), pt(), JDouble(100.0), Bool.FALSE, JString("abil-test")]))
    ck(r14 is not None and "Fire5" in r14 and burns(m3) == [(2.0, 4)] and bool(ok14),
       "FX6 SkyyGear sending the states (gear:elemStates) + Imbue Fire running: a weapon with NO Fire augment still puts Imbue's Burning (Power 5, part = classPart): %s" % r14)
    aw.jobs.clear()
    AS.IMBUE.clear()
    br.remove("gear:elemStates")
    reset()
    BOSSQ = []

    def boss_ans(o):
        a_ = list(o)
        BOSSQ.append((str(a_[0]), a_[1] is None, str(a_[2])))
        return JArray(JObject)([JInt(5)]) if str(a_[2]) == "Pack_Nightlord" else None
    br.put("mob:fn:boss", Fn(boss_ans))
    pm, pmu = rmob(1561, 540.0, 0.5, "Pack_Nightlord", hp=1.0e7)
    NEARL[:] = [pm]
    r14 = H(pm, er_, eu, pw(Air=5), pt(Air=10), 0)
    r14b = H(m1, er_, eu, pw(Air=5), pt(Air=10), 0)
    H(pm, er_, eu, pw(Air=5), pt(Air=10), 1500)
    ck("gust=boss" in r14 and " boss" in r14 and "boss" not in r14b and ("abil-test", True, "Pack_Nightlord") in BOSSQ and len([q_ for q_ in BOSSQ if q_[2] == "Pack_Nightlord"]) == 1,
       "FX7 a boss = abil.bossWords OR SkyyMobs' mob:fn:boss { world, null npc, role, 0, 0, 0 } (a pack boss: no knockback), cached per role: %s | %s %s" % (r14, r14b, BOSSQ))
    br.remove("mob:fn:boss")
    reset()
    NEARL[:] = [bm]
    for k_ in range(3):
        rq14 = H(bm, er_, eu, pw(Earth=5), pt(Earth=10), 2000 * k_)
    cf14 = int(S(bm).ccFree)
    EFX.clear()
    H(bm, er_, eu, pw(Thunder=5), pt(Thunder=10), 9000)          # after the Quake (4 s) - Thunder on Quaked = Grounded
    H(bm, er_, eu, pw(Thunder=5), pt(Thunder=10), 10500)
    ck("quake=" in rq14 and cf14 == 0 and efx_has("Hit_Interrupt_Stunned"), "FX8 a boss only SLOWED by Quake (no SkyyArmory stun clock) spends no CC immunity - the next Thunder flinch still lands: %s ccFree %d %s" % (rq14, cf14, efx()))
    reset()
    NEARL[:] = [vr_]
    g1 = H(vr_, wmob, wmobu, pw(Air=5), pt(Air=6), 0, hit=20.0)
    cg14 = int(S(vr_).ccFree) - T0[0]
    g2 = H(vr_, wmob, wmobu, pw(Air=5), pt(Air=6), 400, hit=20.0)
    ck("gust=" in g1 and "immune" not in g1 and cg14 == 5000 and "gust=immune" in g2 and len(PUSH) == 1,
       "FX9 an Air push on a PLAYER starts the 5 s CC immunity - the next push 0.4 s later does nothing (no knockback juggle): %s | %s ccFree %d" % (g1, g2, cg14))
    reset()
    DEFS[(str(vu_), "Water")] = 100
    A.elemSt(vr_, at(0)).wetUntil = T0[0] + 6000
    r14 = H(vr_, wmob, wmobu, pw(Air=5), pt(Air=6), 0, hit=20.0)
    ck("rx:WIND CHILL" in r14 and [x for x in efx() if x.startswith("SkyyAbility_Spd_") and x.endswith(":1.5")],
       "FX10 a player's WATER Defence shortens the Chill an AIR hit (Wind Chill) puts on: 3 s -> 1.5 s: %s %s" % (r14, efx()))
    DEFS.clear()
    reset()
    A.elemSt(tmob, at(0)).wetUntil = T0[0] + 6000
    NEARL[:] = [tmob]
    ev_clear()
    r14 = H(tmob, er_, eu, pw(Thunder=5), pt(Thunder=10), 0)
    ck("rx:ELECTROCUTE" in r14 and not efx_has("Hit_Interrupt_Flinch") and "jump" not in r14 and [x for x in dmgs() if x[0] == 1542 and x[1] == "ElemArc"],
       "FX11 a Wet THUNDER mob: Electrocute's damage, but never its flinch / chain (own element): %s %s" % (r14, efx()))
    reset()
    NEARL[:] = [m1, m2, m3]
    A.elemSt(m1, at(0)).wetUntil = T0[0] + 6000
    ENV[1513] = 1
    ev_clear()
    r14 = H(m1, er_, eu, pw(Thunder=5), pt(Thunder=10), 0)
    d14 = dmgs()
    ck("rx:ELECTROCUTE" in r14 and [x for x in d14 if x[0] == 1513 and x[1] == "ElemArc"] and not [x for x in d14 if x[0] == 1512] and S(m2) is None,
       "FX12 the Electrocute chain finds a mob standing in water (never hit before) and makes NO state for the dry bystander: %s %s" % (r14, d14))
    reset()
    A.elemSt(m1, at(0)).wetUntil = T0[0] + 600000
    for i_ in range(2100):
        A.elemSt(REFc(tst, 91000 + i_), at(0))
    ck(int(AS.ELEMS.size()) <= 2048 and S(m1) is not None and int(S(m1).wetUntil) == T0[0] + 600000,
       "FX13 a flood of 2,100 idle victims prunes the idle ones - the live Wet state survives (no clear()): %d" % int(AS.ELEMS.size()))
    reset()
    ck(str(A.elsOf(JInt(1))) == "Wet / Chill" and str(A.elsOf(JInt(2))) == "Quake" and str(A.elsOf(JInt(0))) == "Burning", "FX14 the player texts name the engine's states (Wet / Chill, Quake, Burning)")
    AC.ELEM_ON = False
    ck(str(A.elsOf(JInt(1))) == "Chill" and str(A.elsOf(JInt(2))) == "Stagger", "FX14 ... elem.on OFF = the 0.1.50 words")
    AC.ELEM_ON = True
    g14 = open(os.path.join(HERE, "build_skyyclasses_0.1.51.py"), encoding="utf8").read()
    ck("'Wet time (s)'" in g14 and "'Electrocute %'" in g14 and "Reaction words (element states)" in g14 and g14.count('"abilsb", \'wetTime\', \'wetTime\'') == 0,
       "FX15 every ab.ElemStates / ab.Reactions row has a real label + help (not the raw key)")

    # ---------------- E15 FIX 2 (second critic pass, 2026-10-30): every fixed finding, EXECUTED
    reset()
    NEARL[:] = [m1, m2, m3]
    br.put("gear:elemStates", Bool.TRUE)
    AC.ELEM_ON = False
    g15 = bool(A.gearStates())
    AC.ELEM_ON = True
    ck(not g15 and bool(A.gearStates()), "F2-1 gearStates needs elem.on: OFF + SkyyGear's gear:elemStates TRUE = false (Classes' own 0.1.50 Imbue status runs)")
    br.remove("gear:elemStates")
    # the boss: never inside vanilla's Hit_Interrupt_Enraged window
    reset()
    NEARL[:] = [bm]
    eff0 = A.EFFECT
    A.EFFECT = Fn(lambda o: Bool.valueOf(str(list(o)[1]) == "?Hit_Interrupt_Enraged" or not str(list(o)[1]).startswith("?")))
    for k_ in range(2):
        H(bm, er_, eu, pw(Thunder=5), pt(Thunder=10), 1500 * k_)
    A.EFFECT = eff0
    ck(not efx_has("Hit_Interrupt_Stunned") and not efx_has("Hit_Interrupt_Flinch"), "F2-2 a boss inside vanilla's anti-stunlock window (Hit_Interrupt_Enraged) is never flinched: %s" % efx())
    # Frozen = the REAL hold when the boss clock (armory:fn:stunhit) cut it
    reset()
    NEARL[:] = [m1, m2, m3]
    br.put("armory:fn:stunhit", Fn(lambda o: JLong(500)))
    for k_ in range(3):
        rz = H(m1, er_, eu, pw(Water=5), pt(Water=10), 300 * k_)
    br.remove("armory:fn:stunhit")
    ck("frozen=0.5" in rz and int(S(m1).frozenUntil) == T0[0] + 600 + 500 and int(AS.FROZEN.get(m1)[1]) == T0[0] + 600 + 500,
       "F2-3 the boss clock cuts the freeze to 0.5 s - Frozen (Shatter / Melt) ends with it, not 1.5 s later: %s %d" % (rz, int(S(m1).frozenUntil) - T0[0]))
    ev_clear()
    rz2 = H(m1, er_, eu, pw(Earth=5), pt(Earth=20), 1200)
    ck("rx:SHATTER" not in rz2, "F2-3 ... so Earth after the real thaw is no SHATTER: %s" % rz2)
    # the flood prune keeps a live CC clock
    reset()
    sb = A.elemSt(bm, at(0))
    sb.ccFree = T0[0] + 8000
    for i_ in range(2100):
        A.elemSt(REFc(tst, 92000 + i_), at(0)).wetUntil = T0[0] + 600000
    ck(int(AS.ELEMS.size()) <= 2048 and S(bm) is not None and int(S(bm).ccFree) == T0[0] + 8000,
       "F2-4 a flood of 2,100 LIVE (Wet) victims prunes down - a boss's live CC immunity survives (no chain-lock after a flood): %d" % int(AS.ELEMS.size()))
    # ElemArc: no second Weak / Resist; the class Shock jump keeps ElemShock + one affinity
    reset()
    NEARL[:] = [m1, m2, m3]
    br.put("mob:fn:elem", Fn(lambda o: JInt(25) if str(list(o)[1]) == "Thunder" else JInt(0)))
    A.elemSt(m1, at(0)).wetUntil = T0[0] + 6000
    A.elemSt(m2, at(0)).wetUntil = T0[0] + 6000
    ev_clear()
    ra = H(m1, er_, eu, pw(Thunder=5), pt(Thunder=10), 0)
    da = dmgs()
    ck("rx:ELECTROCUTE" in ra and (1511, "ElemArc", 5.0, "Damage$EntitySource") in da and (1512, "ElemArc", 3.0, "Damage$EntitySource") in da,
       "F2-5 a Thunder-Weak (+25) mob: Electrocute = 50 %% of the part (5), its jump 3 - the part's Weak counted ONCE (no x1.25 again): %s" % da)
    reset()
    NEARL[:] = [m1, m2, m3]
    ev_clear()
    A.statusOn(tbuf, m1, er_, eu, JInt(3), JDouble(100.0), JDouble(1.0), JDouble(1.0), at(0), JBoolean(False))
    dc = dmgs()
    ck([x for x in dc if x[1] == "ElemShock" and x[0] != 1511 and abs(x[2] - 50.0) < 1e-6],
       "F2-5 ... the CLASS Shock jump (raw hit x 40 %%) keeps 0.1.50's ElemShock and the neighbour's one affinity (40 x 1.25 = 50): %s" % dc)
    br.remove("mob:fn:elem")
    # one jump per recipient per reactCd under an AoE
    reset()
    pk5 = [rmob(1570 + i_, 560.0 + i_ * 0.8, 0.5, "Trork_Warrior")[0] for i_ in range(5)]
    NEARL[:] = pk5
    for r_ in pk5:
        A.elemSt(r_, at(0)).wetUntil = T0[0] + 6000
    ev_clear()
    for r_ in pk5:
        H(r_, er_, eu, pw(Thunder=5), pt(Thunder=10), 0)
    jr = {}
    for x in dmgs():
        if x[1] == "ElemArc" and abs(x[2] - 3.0) < 1e-6:
            jr[x[0]] = jr.get(x[0], 0) + 1
    ck(jr and max(jr.values()) == 1 and len([x for x in dmgs() if x[1] == "ElemArc" and abs(x[2] - 5.0) < 1e-6]) == 5,
       "F2-6 an AoE Thunder on 5 Wet mobs: 5 Electrocutes, but each mob takes at most ONE chain jump (was up to 4): %s" % jr)
    # Storm widens Electrocute's chain (+2 blocks) and is only spent when used
    reset()
    mf, mfu = rmob(1580, 507.0, 0.5, "Trork_Warrior")
    NEARL[:] = [m1, mf]
    s15 = A.elemSt(m1, at(0))
    s15.wetUntil = T0[0] + 6000
    A.elemSt(mf, at(0)).wetUntil = T0[0] + 6000
    rn = H(m1, er_, eu, pw(Thunder=5), pt(Thunder=10), 0)
    reset()
    s15 = A.elemSt(m1, at(0))
    s15.wetUntil = T0[0] + 6000
    s15.gustUntil = T0[0] + 2000
    A.elemSt(mf, at(0)).wetUntil = T0[0] + 6000
    rs = H(m1, er_, eu, pw(Thunder=5), pt(Thunder=10), 0)
    ck("jump" not in rn and "rx:ELECTROCUTE" in rs and "rx:STORM" in rs and "jump=1" in rs,
       "F2-7 a Wet mob 4.5 blocks away: no chain from a plain Electrocute; Windswept -> STORM widens it (+2) and the spark reaches it: %s | %s" % (rn, rs))
    reset()
    s15 = A.elemSt(m1, at(0))
    s15.quakeUntil = T0[0] + 4000
    s15.gustUntil = T0[0] + 2000
    rg = H(m1, er_, eu, pw(Thunder=5), pt(Thunder=10), 0)
    ck("rx:GROUNDED" in rg and "rx:STORM" not in rg, "F2-7 ... Grounded (no jump this hit) does not spend the Storm: %s" % rg)
    # Wildfire: not after this hit's Douse, never on the stack this hit's Fire lit
    reset()
    NEARL[:] = [m1, m2, m3]
    H(m2, er_, eu, pw(Fire=5), pt(Fire=10), 0)
    rw = H(m2, er_, eu, pw(Water=5, Air=5), pt(Water=10, Air=10), 300)
    ck("rx:DOUSE" in rw and "rx:WILDFIRE" not in rw and burns(m2) == [] and burns(m1) == [],
       "F2-8 Water + Air on Burning: DOUSE puts it out - no WILDFIRE word, no fire spread: %s" % rw)
    reset()
    H(m2, er_, eu, pw(Fire=5), pt(Fire=10), 0)
    rf = H(m2, er_, eu, pw(Fire=5, Air=5), pt(Fire=10, Air=10), 1200)
    bf = burns(m2)
    ck("rx:WILDFIRE" in rf and (2.0, 4) in bf and (2.5, 6) in bf, "F2-8 Fire + Air on Burning: the OLD stack is fanned (2.5 / s, 6), the stack this hit lit stays (2 / s, 4): %s %s" % (rf, bf))
    # the element-hit queue's own cap: live Burning stacks never block it
    reset()
    fn15 = C("ElemHitFn")()
    JOBc = C("AbilJob")
    for i_ in range(8 * int(AC.MAX_LIVE) + 5):
        j_ = JOBc(JInt(26), JLong(now_ms() + 60000), eu, JString("ElemBurn"), JDouble(0.0), JDouble(0.0), JDouble(0.0), JDouble(0.0), JDouble(1.0))
        aw.jobs.add(j_)
    ok15 = fn15.apply(JArray(JObject)([eu, m1u, pw(Fire=5), pt(Fire=5), JDouble(10.0), Bool.FALSE, JString("abil-test")]))
    ck(bool(aw.dotFull()) and bool(ok15), "F2-9 the DoT cap full of live Burning stacks: a new element hit still queues (its own cap)")
    aw.jobs.clear()
    # the per-hit env cache: <= 32 lookups, however many stateless bystanders
    reset()
    ENVN = [0]

    def env_count(o):
        ENVN[0] += 1
        return JInt(ENV.get(int(list(o)[0].getIndex()), 0))
    A.ELEMENV = Fn(env_count)
    crowd = [rmob(1600 + i_, 600.0 + (i_ % 7) * 0.5, (i_ // 7) * 0.5, "Trork_Warrior")[0] for i_ in range(40)]
    for i_ in (3, 17, 33):
        ENV[1600 + i_] = 1
    ct, ctu = rmob(1599, 601.5, 1.5, "Trork_Warrior")
    NEARL[:] = [ct] + crowd
    A.elemSt(ct, at(0)).wetUntil = T0[0] + 6000
    ENVN[0] = 0
    rc = H(ct, er_, eu, pw(Thunder=5), pt(Thunder=10), 0)
    A.ELEMENV = Fn(lambda o: JInt(ENV.get(int(list(o)[0].getIndex()), 0)))
    ck("rx:ELECTROCUTE" in rc and "jump=" in rc and ENVN[0] <= 33, "F2-10 Electrocute in a crowd of 40 stateless mobs: %d water / rain lookups (<= 32 + the target; was ~3 x 40): %s" % (ENVN[0], rc))
    # Sandblast weaken 0 = off
    reset()
    NEARL[:] = [m1, m2, m3]
    old_ex = str(AC.EX_NUMS)
    AC.EX_NUMS = "sandWeaken=0"
    AN.sync()
    A.elemSt(m3, at(0)).gustUntil = T0[0] + 2000
    rsw = H(m3, er_, eu, pw(Earth=5), pt(Earth=10), 0)
    AC.EX_NUMS = old_ex
    AN.sync()
    ck("rx:SANDBLAST" in rsw and not efx_has("SkyyAbility_Weaken_"), "F2-11 Sandblast weaken 0 = off (the burst stays, no weaken): %s %s" % (rsw, efx()))

    # ================================================================================================ BR classes:fn:elemHit
    reset()
    fnh = C("ElemHitFn")()
    NEARL[:] = [m1, m2, m3]
    bads = [None, JString("x"), JArray(JObject)([eu]), JArray(JObject)([eu, m1u, pw(Fire=5), pt(Fire=5), JDouble(float("nan")), Bool.FALSE, JString("abil-test")]),
            JArray(JObject)([eu, m1u, JDblA([1.0] * 5), pt(Fire=5), JDouble(10.0), Bool.FALSE, JString("abil-test")]),
            JArray(JObject)([eu, eu, pw(Fire=5), pt(Fire=5), JDouble(10.0), Bool.FALSE, JString("abil-test")]),
            JArray(JObject)([eu, m1u, pw(), pt(Fire=5), JDouble(10.0), Bool.FALSE, JString("abil-test")]),
            JArray(JObject)([eu, m1u, JIntA([1, 2]), pt(Fire=5), JDouble(10.0), Bool.FALSE, JString("abil-test")]),
            JArray(JObject)([eu, m1u, pw(Fire=5), pt(Fire=5), JDouble(10.0), Bool.FALSE])]
    ck(all(not bool(fnh.apply(b_)) for b_ in bads) and aw.jobs.size() == 0, "BR: bad arguments / no Power / no world (the attacker not online) = FALSE, nothing queued, never throws")
    ck(not bool(fnh.apply(JArray(JObject)([eu, m1u, pw(Fire=5), pt(Fire=5), JDouble(10.0), Bool.FALSE, JString("no-such-world")]))) and aw.jobs.size() == 0
       and not bool(AW.BY.containsKey("no-such-world")), "BR (fix round): a world name no server world has = FALSE, and no job list is made for it")
    ok_ = fnh.apply(JArray(JObject)([eu, m1u, JIntA([0, 0, 0, 12, -3]), JDblA([0.0, 0.0, 0.0, float("nan"), 4.0]), JDouble(100.0), Bool.TRUE, JString("abil-test")]))
    jb = [j_ for j_ in aw.jobs if int(j_.kind) == 29]
    ck(bool(ok_) and len(jb) == 1 and str(jb[0].tref) == str(m1u) and [float(x) for x in jb[0].cap] == [0.0, 0.0, 0.0, 10.0, 0.0]
       and [float(x) for x in jb[0].per] == [0.0, 0.0, 0.0, 0.0, 4.0] and int(jb[0].sh) == 1 and float(jb[0].amount) == 100.0,
       "BR: a good call queues ONE kind 29 job (Power clamped 0-10, NaN part = 0, heavy kept)")
    ev_clear()
    run_world()
    ck(aw.jobs.size() >= 0 and S(m1) is not None and burns(m1) == [(4.0, 4)], "BR: the REAL AbilTick runs it on the world thread: the refs from the UUIDs, Burning at Power 10 (4 / s): %s" % burns(m1))
    AC.ELEM_ON = False
    ck(not bool(fnh.apply(JArray(JObject)([eu, m1u, pw(Fire=5), pt(Fire=5), JDouble(10.0), Bool.FALSE, JString("abil-test")]))), "BR: elem.on OFF = FALSE")
    AC.ELEM_ON = True
    aw.jobs.clear()
    n_ = 0
    d0 = int(A.ELEM_DROP)
    while bool(fnh.apply(JArray(JObject)([eu, m1u, pw(Fire=5), pt(Fire=5), JDouble(10.0), Bool.FALSE, JString("abil-test")]))) and n_ < 5000:
        n_ += 1
    ck(n_ == 8 * int(AC.MAX_LIVE) and int(A.ELEM_DROP) == d0 + 1, "BR: the DoT job cap (8 x abil.maxLive = %d) drops the rest (ELEM_DROP)" % n_)
    aw.jobs.clear()
    K.save()
    sys.stdout.flush()
    os._exit(0)


_NS = dict(T50.__dict__)
_NS["EL"] = EL
exec(compile(_elem_src(), os.path.join(HERE, "test_skyyclasses_0.1.51.py") + ":run_elem", "exec"), _NS)
run_elem = _NS["run_elem"]


def run_wire(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.JAVASSIST], verify=False)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(jar)

    def calls(cls, meth):
        c = cp.get(PKG + cls)
        out_ = set()
        for m in c.getDeclaredMethods():
            if str(m.getName()) != meth:
                continue
            ci = m.getMethodInfo().getCodeAttribute().iterator()
            cpl = m.getMethodInfo().getConstPool()
            while ci.hasNext():
                pos = ci.next()
                op = ci.byteAt(pos)
                if op in (0xb6, 0xb8, 0xb7, 0xb9):
                    idx = ci.u16bitAt(pos + 1)
                    out_.add(str(cpl.getMethodrefClassName(idx) if op != 0xb9 else cpl.getInterfaceMethodrefClassName(idx)).split(".")[-1] + "." +
                             str(cpl.getMethodrefName(idx) if op != 0xb9 else cpl.getInterfaceMethodrefName(idx)))
        return out_
    want = [("Abil", "statusOn", "Abil.elemClass"), ("Abil", "elemClass", "Abil.elemRun"), ("Abil", "hitLanded3", "Abil.gearStates"),
            ("Abil", "dotTick", "Abil.elemBurnOk"), ("Abil", "dotTick", "Abil.elemInWater"), ("Abil", "dotTick", "Abil.elemTick"),
            ("Abil", "runJob5", "Abil.elemJob"), ("Abil", "elemJob", "Abil.elemRun"), ("ElemHitFn", "apply", "Abil.elemWant"),
            ("Abil", "elemRun", "Abil.elemVictim"), ("Abil", "elemRun", "Abil.elemEnv"), ("Abil", "elemRun", "Abil.elemPop"),
            ("Abil", "elemRun", "Abil.elemEarth"), ("Abil", "elemRun", "Abil.elemThunder"), ("Abil", "elemRun", "Abil.elemWater"),
            ("Abil", "elemRun", "Abil.elemFire"), ("Abil", "elemRun", "Abil.elemAir"), ("Abil", "elemEnvBits", "Abil.fluidWater"),
            ("Abil", "elemEnvBits", "Abil.rainAt"), ("Abil", "rainAt", "Abil.rainy"), ("Abil", "elemVictim", "Abil.pvpOn"),
            ("Abil", "elemVictim", "HealTask.inParty"), ("Abil", "elemDmg", "Abil.envHit"), ("Abil", "elemDmg", "Abil.hit"),
            ("Abil", "envHit", "DamageSystems.executeDamage"), ("Abil", "elemPop", "EntityTrackerSystems$EntityViewer.queueUpdate"),
            ("Abil", "fluidWater", "FluidSection.getFluidId"), ("Abil", "rainAt", "WeatherTracker.getWeatherIndex"),
            ("Abil", "rainAt", "WorldSupport.getCurrentWeatherIndex"), ("Abil", "pvpOn", "WorldConfig.isPvpEnabled"),
            ("Abil", "elemChill", "Abil.freezeOne"), ("Abil", "elemEarth", "Abil.stunMob"), ("Abil", "elemAir", "Abil.push"),
            ("Abil", "elemFlinch", "Abil.effect"), ("Abil", "elemOwn", "Function.apply"), ("Abil", "elemRes", "Function.apply"),
            # fix 2
            ("Abil", "elemFlinch", "Abil.hasFx"), ("Abil", "elemEnvBits", "Abil.skyOpen"), ("Abil", "skyOpen", "HeightmapColumn.getHeight"),
            ("Abil", "elemWant", "AbilWorld.elemFull"), ("Abil", "elemNext", "Abil.elemWetAt"), ("Abil", "elemAir", "Abil.burnSnap"),
            ("Abil", "elemAir", "Abil.burnMarkNew"), ("Abil", "elemRun", "Abil.burnSnap")]
    miss = [w for w in want if w[2] not in calls(w[0], w[1])]
    K.check(not miss, "W every new hook site calls its method (%d sites) %s" % (len(want), miss))
    g = open(GEN, encoding="utf8").read()
    K.check('b.put("classes:fn:elemHit", new @PKG@.ElemHitFn());' in g and 'remove("classes:fn:elemHit")' in g and "classes:fn:elemHit (element states" in g,
            "W setup puts classes:fn:elemHit, shutdown removes it, the ready line names it")
    K.check("if (j.kind == 26 || j.kind == 28 || j.kind == 29) n++;" in g, "W queued element hits count against the DoT job cap, never against class casts")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyClasses", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("exec46", T48.run_exec46), ("wire46", T48.run_wire46), ("wire47", T48.run_wire47), ("exec48", T48.run_exec),
                   ("alt", T50.run_alt), ("sm", T50.run_exec), ("wire50", T50.run_wire), ("elem", run_elem), ("wire", run_wire), ("live", T48.run_live)],
           script=__file__, live=(T48.LIVE_DIR, "Skyy_SkyyClasses"))
