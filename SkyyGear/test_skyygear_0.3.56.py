"""Harness for SkyyGear 0.3.56 (round sig3b: the Gear half of signature round 3 - tools/gear_0_3_56_patch.py header).
Build first (the build needs Quirk's private art; in a worktree: SKYWYNN_PRIVATE_ART=<path to SkyWynn-PRIVATE-art>):
    python tools/gear_0_3_56_patch.py && python SkyyGear/build_skyygear_0.3.56.py
    python SkyyGear/test_skyygear_0.3.56.py [--keep] [--expect-dump]

Phases (fresh child processes / JVMs, tools/harness_kit.py; the 0.3.55 jar is the compare base):
  S  static    the patch re-runs to identical bytes, ONE new class (GearElemPowFn), no command / system; tools/ut_vanilla.py: the Doomed staff in LOOKS,
               ARMORY_LOOKS empty, check() clean; the fresh config text: the marker + the 2 sig.ut lines + the 10 rule rows
  A  verify    every class loads + initialises with -Xverify:all
  C  compare   0.3.55 -> 0.3.56 (EXPECT below)
  E  engine    the 0.2.11 harness's bare server boot (vanilla pack + THIS jar) - every new path EXECUTED:
               P  the pool: Weapon_Staff_Doomed out of GearPool.P_ID (a plain staff still in)
               L  leanHit whole families only (Warrior Katana / Monk Bo prefixes), leanId, pickType with a Warrior lean never picks a longsword,
                  GearUt.rerollItem runs with the lean
               R  the C+ rules: ruleOf / ruleFor on REAL stacks (UT docs vs normal / rules off), ruleRate, coneFactor, step2 sequences (Overtime
                  low / high / unknown Health, Combat arrows -25 %, our own add left out, The Pocket Knife hit-then-rise and rise-then-hit and stale,
                  The Paperweight's sig.ut -20 from the fresh config), hitAdd, halfDraw on Short Notice's REAL GearChg walk, clampAdd
               X  GearSigX.onHit on an ECS shim with a REAL EntityStatMap meter: Combat bash +3, Test Zoom long shot +2 / short 0, Pocket Knife
                  backstab (rise first) + front; OWN keeps the add out of the next step
               F  the sigfx guard: owns "W" = never called, "" = called with {uuid, weightedVortex, id, level, 0.0}, no bridge / no String answer = never;
                  a fired Paperweight meter (full -> 0) reaches it; the cache
               U  REAL tooltips (GearView.lines): the rarity-coloured Ability 1 name (UT orange, Mythic, gold), the UT move names + rule lines,
                  every rule line <= 70 characters, the Combat bow's Charge line x0.75
               M  migrateSig56 text step: absent -> added (2 log rows sig.ut[<id>] (none)), a hand value kept + noted, the marker = nothing,
                  CRLF kept; the real method on a scratch file twice (History copy, change log); the loader reads SIG_UT -20 / 25 and the rule rows
               W  gear:fn:elemPower: powText / powOf (a Fire line = Fire:3), GearElem.note on a REAL inventory puts it, the Fn (UUID / String / junk)
  E55 / E54    the 0.3.55 and 0.3.54 harnesses' engine phases against THIS jar (every 0.3.5x check still passes)
  D  live      start twice on a scratch COPY of Skyy's live NewBetaTest Skyy_SkyyGear: migrateSig56 adds the 2 lines once (or keeps hand lines),
               the second start changes nothing
  AA engine-access audit
NOT COVERED (UNVERIFIED in game): the engine order of a hit and its meter rise (both orders are handled + tested); a real bow bash reaching
GearHitSys as a melee weapon hit; Short Notice's half draws carrying a PARTIAL damage step at runtime (the walk says so); the client drawing
the tooltip colours; SkyyMenu reading gear:fn:elemPower in game.
Scratch: tools/dev/scratch/sig3b/harness (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, re, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.3.56"
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "sig3b", "harness")]
import skyybuild as B
import harness_kit as HK

GEN = os.path.join(HERE, "build_skyygear_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyygear_0.3.55.py")
PATCH = os.path.join(ROOT, "tools", "gear_0_3_56_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyGear-0.3.55.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.gear."
T55 = {"__file__": os.path.join(HERE, "test_skyygear_0.3.55.py"), "__name__": "t55"}
_s = open(T55["__file__"], encoding="utf8").read()
exec(compile(_s[:_s.index('HK.run_compare = T54["run_compare54"]')], T55["__file__"], "exec"), T55)
T54 = T55["T54"]
T54["SCRATCH"] = SCRATCH
T55["SCRATCH"] = SCRATCH
ADDED = ["GearElemPowFn"]
EXPECT = None if "--expect-dump" in sys.argv else {          # the first run's dump, reviewed: the config rows / fields / migration (Cfg*, GearCfg), the pool without the
    # Doomed staff (GearPool / GearPack tables), the rules + guard (GearSigX), the hit call (GearHitSys), the name / rule line (GearView), leanHit / leanId
    # (GearPool, GearUt.rerollItem), elemPower (GearElem + the plugin's setup / shutdown)
    'CfgFile': ['~<clinit>'],
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'CfgRows1': ['~<clinit>'],
    'CfgRows2': ['~<clinit>'],
    'GearCfg': ['+f ALLP', '+f ALLP_AT', '+f H56_IDS', '+f H56_MARK', '+f H56_MARK_ID', '+f H56_VALS', '+f H56_WHO', '+f SIG_CB_ARROWS', '+f SIG_CB_BASH', '+f SIG_OT_HIGH', '+f SIG_OT_LOW', '+f SIG_PK_BACK', '+f SIG_PK_FRONT', '+f SIG_RULES', '+f SIG_SN_HALF', '+f SIG_TZ_RANGE', '+f SIG_TZ_REFUND', '+m allLean', '+m migrateSig56', '+m s56Log', '+m s56Update', '~<clinit>', '~m apply', '~m defaultsText'],
    'GearElem': ['+f PW', '+m powOf', '+m powText', '~<clinit>', '~m clearAll', '~m forget', '~m note'],
    'GearHitSys': ['~m handle'],
    'GearPack': ['~<clinit>'],
    'GearPool': ['+m foreignId', '+m leanId', '+m leanLen', '~<clinit>', '~m candM', '~m idIdx', '~m leanHit', '~m levelsM', '~m liveType', '~m matchM', '~m packText', '~m pickItemM', '~m table', '~m typeOfId', '~m w'],
    'GearSigX': ['+f CR_ID', '+f CR_K', '+f CR_NAME', '+f C_BAD', '+f FX_FX', '+f FX_ID', '+f N6', '+f OWN', '+f OWNS', '+f OWNS_MS', '+f OWN_MS', '+f PAIR_MS', '+f PEND', '+f RISE', '+f R_CB', '+f R_OT', '+f R_PK', '+f R_SN', '+f R_TZ', '+m clampAdd', '+m coneFactor', '+m coneHit', '+m coneRise', '+m fired', '+m fxRow', '+m halfDraw', '+m hitAdd', '+m hpOf', '+m onHit', '+m ownAdd', '+m ownTake', '+m owns', '+m pctSeg', '+m ruleFor', '+m ruleLine', '+m ruleOf', '+m ruleRate', '+m seg', '+m sigfx', '+m step2', '+m utName', '~<clinit>', '~m forget', '~m statusText', '~m step', '~m tick'],
    'GearUt': ['~m rerollItem'],
    'GearView': ['~m sigRows'],
    'SkyyGearPlugin': ['~m setup', '~m shutdown'],
}
LIVE_DIR = T54["LIVE_DIR"]
U = "00000000-0000-0000-0000-000000000356"
RULE_LINES = {1: "Fills 35% faster under half Health, 15% slower above.", 2: "Backstabs fill it x2; front hits x0.5.",
              3: "Half-drawn hits fill it too (+0.5).", 4: "Bash hits fill +3; arrows fill 25% less.", 5: "Hits from 25+ blocks refund +2 energy."}
RULE_IDS = {1: "Weapon_Battleaxe_UT_Overtime", 2: "Weapon_Daggers_UT_PocketKnife", 3: "Weapon_Shortbow_UT_ShortNotice", 4: "Weapon_Shortbow_Combat",
            5: "Weapon_Shortbow_Test_Zoom"}
RULE_NAMES = {1: "Last-Hour Whirlwind", 2: "Quiet Edge", 3: "Snap Volley", 4: "Bashing Trishot", 5: "Long Volley"}
SIG_KEYS = ["sig.rules", "sig.rule.lowHp", "sig.rule.highHp", "sig.rule.back", "sig.rule.front", "sig.rule.halfDraw", "sig.rule.bash", "sig.rule.arrows",
            "sig.rule.range", "sig.rule.refund"]
SIG_DEFS = ["true", "35", "-15", "100", "-50", "0.5", "3", "-25", "25", "2"]


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyGear 0.3.56 - build script') and g.count('VERSION = "0.3.56"') == 1, "S header + VERSION")
    K.eq((g.count("registerSystem(") - o.count("registerSystem("), g.count("registerCommand(") - o.count("registerCommand("), g.count('mk("') - o.count('mk("')), (0, 0, 1), "S one new class (GearElemPowFn), no system / command")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    import ut_vanilla as UTV
    K.check("Weapon_Staff_Doomed" in UTV.LOOKS and UTV.ARMORY_LOOKS == [] and UTV.check() == [] and set(UTV.LOOKS) - set(UTV.LOOKS_GL1) == {"Weapon_Staff_Doomed"},
            "S tools/ut_vanilla.py: the Doomed staff joins LOOKS (Doomcaller shipped), ARMORY_LOOKS empty, check() clean")
    K.check(g.count("H56_LINES") >= 2 and "migrateSig56()" in g and "skyy.harness.nosig56" in g, "S migrateSig56 + its harness switch")
    K.save()


# ====================================================================================================== E: engine
def run_engine(out, jar, scratch, home):
    from jpype import JClass, JInt, JString, JImplements, JOverride, JObject, JArray, JLong, JDouble, JBoolean, JFloat, JShort, JByte
    K = HK.Child(out)
    h211 = os.path.join(HERE, "test_skyygear_0.2.11.py")
    t = open(h211, encoding="utf-8").read()
    t = t[:t.index("def run_engine(out):")]
    esc = os.path.join(scratch, "eng")
    os.makedirs(esc, exist_ok=True)
    argv0 = sys.argv
    sys.argv = [h211, "--jar", jar, "--dir", esc]
    H = {"__name__": "skyygear_h211_lib", "__file__": h211, "__builtins__": __builtins__}
    exec(compile(t, h211 + " (engine boot, library)", "exec"), H)
    sys.argv = argv0
    H.update({"JAR": jar, "SCRATCH": esc, "VERSION": VERSION})
    H["_jvm"]([B.SERVER_JAR, B.JAVASSIST, jar], verify=True, big=True)

    class KC(object):
        def __init__(self, k):
            self.k = k
            self.notes = k.notes

        def check(self, c, w):
            return self.k.check(c, "E boot: " + w)
    E = H["engine_boot"](KC(K))
    us = E["us"]
    P = lambda n: JClass(PKG + n)
    Cfg, Gear, Data, Roll, View, Defs, Pool, GUt, SX, Elem, Aug, Chg = (P("GearCfg"), P("Gear"), P("GearData"), P("GearRoll"), P("GearView"), P("GearDefs"),
                                                                     P("GearPool"), P("GearUt"), P("GearSigX"), P("GearElem"), P("GearAug"), P("GearChg"))
    Props = JClass("java.util.Properties")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    INV = JClass("com.hypixel.hytale.server.core.inventory.Inventory")
    BA = JClass("org.bson.BsonArray")
    BS = JClass("org.bson.BsonString")
    UUID = JClass("java.util.UUID")
    Paths = JClass("java.nio.file.Paths")
    AL = JClass("java.util.ArrayList")
    SysJ = JClass("java.lang.System")
    SA = JArray(JString)
    u = UUID.fromString(U)
    sysp = SysJ.getProperties()
    br = sysp.get("skyy.bridge")
    if br is None:
        br = JClass("java.util.concurrent.ConcurrentHashMap")()
        sysp.put("skyy.bridge", br)
    data = os.path.join(scratch, "data")
    os.makedirs(data, exist_ok=True)
    Cfg.DIR = Paths.get(data)
    fresh = str(Cfg.defaultsText())

    def apply(**kv):
        p = Props()
        p.load(JClass("java.io.StringReader")(fresh))
        for k, v in kv.items():
            p.setProperty(k.replace("__", "."), v)
        Cfg.apply(p, False)
    BASE = {"part__gate": "false"}
    apply(**BASE)

    def fld(cls, name):
        k = cls.class_ if hasattr(cls, "class_") else cls
        while k is not None:
            try:
                f = k.getDeclaredField(name)
                f.setAccessible(True)
                return f
            except Exception:
                k = k.getSuperclass()
        raise KeyError(name)

    @JImplements("java.util.function.Function")
    class PyFn(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def apply(self, a):
            return self.f(a)

    def doc(iid, r, lv=20):
        d_ = Roll.newDoc(JString(iid), JInt(r), True, JString("admin"), JInt(lv))
        d_.put("r", BS(Defs.R_ID[r]))
        return d_

    def stack(iid, d_):
        return Data.put(IS(JString(iid), JInt(1)), d_, u)
    RUT, RMY = int(Defs.R_UT), int(Defs.R_MY)

    # ================================================================================== C the fresh config
    K.check(("\n%s\n" % "\n".join(["sig.ut.Weapon_Sword_UT_Paperweight=-20", "sig.ut.Weapon_Shortbow_Ricochet=25"])) in fresh and "SkyyGear 0.3.56 signature defaults" in fresh
            and all(("\n%s=%s\n" % (k, v)) in fresh for k, v in zip(SIG_KEYS, SIG_DEFS)), "C the fresh config: the marker, the 2 sig.ut defaults, the 10 rule rows")
    sgu = dict((str(k), int(Cfg.SIG_UT.get(k))) for k in Cfg.SIG_UT.keySet())
    rf = (bool(Cfg.SIG_RULES), int(Cfg.SIG_OT_LOW), int(Cfg.SIG_OT_HIGH), int(Cfg.SIG_PK_BACK), int(Cfg.SIG_PK_FRONT), float(Cfg.SIG_SN_HALF), float(Cfg.SIG_CB_BASH),
          int(Cfg.SIG_CB_ARROWS), int(Cfg.SIG_TZ_RANGE), float(Cfg.SIG_TZ_REFUND))
    K.eq((sgu, rf), ({"Weapon_Sword_UT_Paperweight": -20, "Weapon_Shortbow_Ricochet": 25}, (True, 35, -15, 100, -50, 0.5, 3.0, -25, 25, 2.0)),
         "C the loader reads the 2 sig.ut defaults and the 10 rule rows")
    pr0 = Props()
    pr0.load(JClass("java.io.StringReader")("\n".join(l for l in fresh.split("\n") if not l.startswith("sig.rule"))))
    pr0.setProperty("sig.rule.lowHp", "999")
    Cfg.apply(pr0, False)
    K.eq((int(Cfg.SIG_OT_LOW), int(Cfg.SIG_OT_HIGH), float(Cfg.SIG_TZ_REFUND)), (200, -15, 2.0), "C a file without the rule lines = the defaults; a bad value is clamped")
    apply(**BASE)

    # ================================================================================== P the pool
    pid = [str(x) for x in Pool.P_ID]
    K.check("Weapon_Staff_Doomed" not in pid and "Weapon_Sword_Doomed" not in pid and [i for i in pid if i.startswith("Weapon_Staff_") and "Doomed" not in i],
            "P Weapon_Staff_Doomed (Doomcaller's look) is out of the random bags; other staves stay in")

    # ================================================================================== L lean
    war = SA(["Weapon_Sword_", "Weapon_Spear_", "Weapon_Shield_", "Weapon_Longsword_Katana"])
    monk = SA(["Weapon_Staff_Bo_", "Weapon_Bo_", "Weapon_Fist_"])
    lb = []
    if bool(Pool.leanHit(JString("Weapon_Longsword"), war)) or not bool(Pool.leanHit(JString("Weapon_Sword"), war)) or not bool(Pool.leanHit(JString("Weapon_Spear"), war)):
        lb.append("Warrior: Sword / Spear lean, Longsword does not")
    if bool(Pool.leanHit(JString("Weapon_Staff"), monk)) or not bool(Pool.leanHit(JString("Weapon_Bo"), monk)):
        lb.append("Monk: Bo lean, Staff does not")
    if not bool(Pool.leanId(JString("Weapon_Longsword_Katana"), war)) or bool(Pool.leanId(JString("Weapon_Longsword_Iron"), war)) or bool(Pool.leanId(None, war)) or bool(Pool.leanHit(None, war)):
        lb.append("leanId: the Katana's own id only")
    # fix F1: the LONGEST live class prefix owns an id (SkyyClasses 0.1.53) - a Spellblade's Weapon_Longsword_ no longer leans to the Katana
    spb = SA(["Weapon_Longsword_"])
    br.put("class:list", "Warrior:Swordsmanship,Spellblade:Battlemagic")
    br.put("class:weapons:Warrior", "Weapon_Sword_,Weapon_Spear_,Weapon_Shield_,Weapon_Longsword_Katana")
    br.put("class:weapons:Spellblade", "Weapon_Longsword_")
    Cfg.ALLP_AT = 0
    al = sorted(str(x) for x in Cfg.allLean())
    f1 = (al == sorted(["Weapon_Sword_", "Weapon_Spear_", "Weapon_Shield_", "Weapon_Longsword_Katana", "Weapon_Longsword_"]),
          bool(Pool.leanId(JString("Weapon_Longsword_Katana"), spb)), bool(Pool.foreignId(JString("Weapon_Longsword_Katana"), spb)),
          bool(Pool.leanId(JString("Weapon_Longsword_Iron"), spb)), bool(Pool.foreignId(JString("Weapon_Longsword_Iron"), spb)),
          bool(Pool.leanId(JString("Weapon_Longsword_Katana"), war)), bool(Pool.foreignId(JString("Weapon_Longsword_Katana"), war)), bool(Pool.foreignId(None, spb)))
    K.eq(f1, (True, False, True, True, False, True, False, False),
         "L fix F1: allLean reads every live class; a Spellblade's Weapon_Longsword_ leans Iron but not the Warrior's Katana (foreignId); the Warrior keeps the Katana")
    br.remove("class:list"); br.remove("class:weapons:Warrior"); br.remove("class:weapons:Spellblade")
    Cfg.ALLP_AT = 0
    K.check(len(list(Cfg.allLean())) == 0 and bool(Pool.leanId(JString("Weapon_Longsword_Katana"), spb)), "L fix F1: no class bridge = no foreign prefix (the plain prefix lean)")
    tk = [str(x) for x in Pool.T_KEY]
    lean0 = int(Cfg.CLASS_LEAN)
    Cfg.CLASS_LEAN = 100
    leaned = sorted(k_ for k_ in tk if bool(Pool.leanHit(JString(k_), war)))
    picks, bad_lv = {}, []
    try:
        for lv_ in (5, 15, 30, 50, 80):
            got_ = set()
            for _ in range(80):
                ty = int(Pool.pickType(False, JInt(lv_), war))
                if ty >= 0:
                    got_.add(tk[ty])
            picks[lv_] = sorted(got_)
            if got_ & set(leaned) and not got_ <= set(leaned):          # a leaned type exists at that level = every pick is one (class.lean 100)
                bad_lv.append((lv_, sorted(got_)))
    finally:
        Cfg.CLASS_LEAN = lean0
    K.notes.append("L Warrior lean: leaned loot types %s; pickType picks by level (class.lean 100) %s" % (leaned, picks))
    if bad_lv or "Weapon_Longsword" in leaned or "Weapon_Sword" not in leaned or not [v for v in picks.values() if set(v) & set(leaned)]:
        lb.append(("a Warrior lean: Sword / Spear (/ Shield) types only, never Longsword", leaned, bad_lv))
    rr = [GUt.rerollItem(JString("Weapon_Sword_UT_Paperweight"), JInt(1), JInt(120), war) for _ in range(20)]
    K.notes.append("L GearUt.rerollItem with the Warrior lean: %s" % sorted(set(str(x) for x in rr if x is not None))[:8])
    K.check(not lb, "L leanHit counts a class prefix only when it covers the whole family; leanId; a Warrior never leans to longswords: %s" % lb)

    # ================================================================================== R the rules (pure + REAL stacks)
    rb = []
    if [int(SX.ruleOf(JString(RULE_IDS[k]))) for k in range(1, 6)] != [1, 2, 3, 4, 5] or int(SX.ruleOf(JString("Weapon_Sword_UT_Paperweight"))) != 0 or int(SX.ruleOf(None)) != 0:
        rb.append("ruleOf")
    if [str(SX.utName(JString(RULE_IDS[k]))) for k in range(1, 6)] != [RULE_NAMES[k] for k in range(1, 6)]:
        rb.append("utName")
    ot_ut = stack(RULE_IDS[1], doc(RULE_IDS[1], RUT))
    ot_n = stack(RULE_IDS[1], doc(RULE_IDS[1], 0))
    if int(SX.ruleFor(JString(RULE_IDS[1]), ot_ut)) != 1 or int(SX.ruleFor(JString(RULE_IDS[1]), ot_n)) != 0 or int(SX.ruleFor(JString(RULE_IDS[1]), IS(JString(RULE_IDS[1]), JInt(1)))) != 0:
        rb.append("ruleFor: a UT document only")
    apply(sig__rules="false", **BASE)
    if int(SX.ruleFor(JString(RULE_IDS[1]), ot_ut)) != 0:
        rb.append("ruleFor: sig.rules off = none")
    apply(**BASE)
    rates = [round(float(SX.ruleRate(1, JDouble(0.3))), 4), round(float(SX.ruleRate(1, JDouble(0.5))), 4), float(SX.ruleRate(1, JDouble(-1.0))),
             float(SX.ruleRate(4, JDouble(-1.0))), float(SX.ruleRate(2, JDouble(0.1))), float(SX.coneFactor(1)), float(SX.coneFactor(-1)), float(SX.coneFactor(0))]
    if rates != [1.35, 0.85, 1.0, 0.75, 1.0, 2.0, 0.5, 1.0]:
        rb.append(("ruleRate / coneFactor", rates))
    T0 = 10000000

    def seq(iid, st, steps, hf=-1.0, mx=20.0):
        """steps = [(dt, v)] after a baseline at T0 (v 0); returns the adds of every step after the baseline"""
        SX.W.remove(u)
        SX.step2(u, JString(iid), 0, st, JFloat(0.0), JFloat(mx), False, JLong(T0), JDouble(hf))
        o = []
        for dt, v, *h in steps:
            o.append(round(float(SX.step2(u, JString(iid), 0, st, JFloat(v), JFloat(mx), False, JLong(T0 + dt), JDouble(h[0] if h else hf))), 4))
        return o
    a1 = seq(RULE_IDS[1], ot_ut, [(1000, 2.0, 0.3), (1100, 4.7, 0.8), (1200, 6.4, -1.0)])
    if a1 != [0.7, -0.3, 0.0]:
        rb.append(("Overtime: +2 under half = +0.7, +3 above = -0.45 rounded / held = -0.3 on +2.?", a1))
    cb = stack(RULE_IDS[4], doc(RULE_IDS[4], RUT))
    a2 = seq(RULE_IDS[4], cb, [(1000, 2.0)])
    SX.ownAdd(u, JFloat(3.0), JLong(T0 + 1050))
    n6 = int(SX.N6[6])
    a3 = round(float(SX.step2(u, JString(RULE_IDS[4]), 0, cb, JFloat(1.5 + 3.0), JFloat(20.0), False, JLong(T0 + 1100), JDouble(-1.0))), 4)
    if a2 != [-0.5] or a3 != 0.0 or int(SX.N6[6]) != n6 + 1:
        rb.append(("Combat bow: arrows -25 % (+2 -> -0.5), our +3 bash left out of the next step", a2, a3))
    SX.ownAdd(u, JFloat(-0.5), JLong(T0))
    if round(float(SX.ownTake(u, JLong(T0 + 100))), 3) != -0.5 or float(SX.ownTake(u, JLong(T0 + 100))) != 0.0:
        rb.append("ownTake: once")
    SX.ownAdd(u, JFloat(2.0), JLong(T0))
    if float(SX.ownTake(u, JLong(T0 + 5000))) != 0.0:
        rb.append("ownTake: a stale own add is dropped")
    pk = stack(RULE_IDS[2], doc(RULE_IDS[2], RUT))
    seq(RULE_IDS[2], pk, [])
    c1 = float(SX.coneHit(u, JString(RULE_IDS[2]), JDouble(2.0), JLong(T0 + 1000)))
    a4 = round(float(SX.step2(u, JString(RULE_IDS[2]), 0, pk, JFloat(1.0), JFloat(27.0), False, JLong(T0 + 1050), JDouble(-1.0))), 4)
    a5 = round(float(SX.step2(u, JString(RULE_IDS[2]), 0, pk, JFloat(3.0), JFloat(27.0), False, JLong(T0 + 1100), JDouble(-1.0))), 4)
    c2 = round(float(SX.coneHit(u, JString(RULE_IDS[2]), JDouble(0.5), JLong(T0 + 1200))), 4)
    a6 = round(float(SX.step2(u, JString(RULE_IDS[2]), 0, pk, JFloat(4.0), JFloat(27.0), False, JLong(T0 + 1300), JDouble(-1.0))), 4)
    c3 = float(SX.coneHit(u, JString(RULE_IDS[2]), JDouble(2.0), JLong(T0 + 3000)))
    if (c1, a4, a5, c2, a6, c3) != (0.0, 1.0, 0.0, -0.5, 0.0, 0.0):
        rb.append(("Pocket Knife: backstab then rise = +1 more; a +1 rise then a front hit = -0.5 (half); a lone rise / a stale hit = nothing", (c1, a4, a5, c2, a6, c3)))
    SX.PEND.clear()
    SX.RISE.clear()
    pw = stack("Weapon_Sword_UT_Paperweight", doc("Weapon_Sword_UT_Paperweight", RUT))
    a7 = seq("Weapon_Sword_UT_Paperweight", pw, [(1000, 5.0)])
    nrm = stack("Weapon_Sword_Iron", doc("Weapon_Sword_Iron", 0))
    a8 = seq("Weapon_Sword_Iron", nrm, [(1000, 5.0), (200, 6.0)])
    if a7 != [-1.0] or a8 != [0.0, 0.0]:
        rb.append(("The Paperweight: sig.ut -20 from the fresh config (+5 -> -1); a normal sword untouched", a7, a8))
    ha = [float(SX.hitAdd(3, True, True, JDouble(-1.0))), float(SX.hitAdd(3, True, False, JDouble(-1.0))), float(SX.hitAdd(3, False, True, JDouble(-1.0))),
          float(SX.hitAdd(4, False, False, JDouble(-1.0))), float(SX.hitAdd(4, True, False, JDouble(-1.0))), float(SX.hitAdd(5, True, False, JDouble(30.0))),
          float(SX.hitAdd(5, True, False, JDouble(25.0))), float(SX.hitAdd(5, True, False, JDouble(10.0))), float(SX.hitAdd(5, False, False, JDouble(40.0))),
          float(SX.hitAdd(5, True, False, JDouble(-1.0)))]
    if ha != [0.5, 0.0, 0.0, 3.0, 0.0, 2.0, 2.0, 0.0, 0.0, 0.0]:
        rb.append(("hitAdd", ha))
    if [round(float(SX.clampAdd(JFloat(c), JFloat(10.0), JFloat(a))), 3) for c, a in ((9.0, 3.0), (1.0, -2.0), (4.0, 2.0))] != [1.0, -1.0, 2.0]:
        rb.append("clampAdd")
    # halfDraw on a GearChg index entry (the bare boot has no interaction assets to walk - the runtime walk's PARTIAL flags on Short Notice's
    # 4 arrow configs are UNVERIFIED in game): a PARTIAL-only step = a half draw; FULL, PARTIAL|FULL (ambiguous) and unknown steps not
    OA = JArray(JObject)
    IHM = JClass("java.util.IdentityHashMap")
    cpart, cfull, camb, cnone = JClass("java.lang.Object")(), JClass("java.lang.Object")(), JClass("java.lang.Object")(), JClass("java.lang.Object")()
    ix = IHM()
    ix.put(cpart, JArray(JInt)([int(Chg.PART), 0, 600]))
    ix.put(cfull, JArray(JInt)([int(Chg.FULL), 2, 1200]))
    ix.put(camb, JArray(JInt)([int(Chg.FULL) | int(Chg.PART), 0, 1200]))
    ent = OA([ix, JClass("java.util.HashMap")(), JObject(JBoolean(True), "java.lang.Boolean"), JObject(JBoolean(True), "java.lang.Boolean"), JString("harness"),
              JObject(JBoolean(True), "java.lang.Boolean"), JObject(JLong(int(SysJ.currentTimeMillis())), "java.lang.Long"), JObject(JBoolean(True), "java.lang.Boolean")])
    Chg.ITEMS.put(JString(RULE_IDS[3]), ent)
    hd = [bool(SX.halfDraw(JString(RULE_IDS[3]), c_)) for c_ in (cpart, cfull, camb, cnone)] + [bool(SX.halfDraw(JString(RULE_IDS[3]), None)), bool(SX.halfDraw(None, cpart))]
    Chg.ITEMS.remove(JString(RULE_IDS[3]))
    if hd != [True, False, False, False, False, False]:
        rb.append(("halfDraw on an index entry: PARTIAL only = half; FULL / both / unknown / null = not", hd))
    K.check(not rb, "R the C+ rules: ruleOf / utName / ruleFor (UT documents, sig.rules), rates, step2 sequences (Overtime, Combat bow + own adds, "
            "Pocket Knife both orders + stale, Paperweight -20, a normal sword), hitAdd, clampAdd, halfDraw on the REAL walk: %s" % rb)

    # ================================================================================== X onHit on an ECS shim with a REAL EntityStatMap
    xb = []
    jpz = JClass("javassist.ClassPool")(True)
    jpz.appendClassPath(B.SERVER_JAR)
    CTFz, CTMz = JClass("javassist.CtField"), JClass("javassist.CtNewMethod")
    REFc = JClass("com.hypixel.hytale.component.Ref")
    CMPc, CTc, RFc = "com.hypixel.hytale.component.Component", "com.hypixel.hytale.component.ComponentType", "com.hypixel.hytale.component.Ref"
    cc_ = jpz.makeClass("com.hypixel.hytale.component.SkyySig56Buf", jpz.get("com.hypixel.hytale.component.CommandBuffer"))
    cc_.addField(CTFz.make("public static java.util.IdentityHashMap COMP = new java.util.IdentityHashMap();", cc_))
    cc_.addMethod(CTMz.make("public %s getComponent(%s r, %s t) { java.util.IdentityHashMap m = (java.util.IdentityHashMap) COMP.get(r); if (m == null) return null; return (%s) m.get(t); }" % (CMPc, RFc, CTc, CMPc), cc_))
    BufC = cc_.toClass(REFc.class_)
    Buf = JClass(BufC.getName())
    buf = us.allocateInstance(BufC)
    CTYc = JClass(CTc)
    MODc = JClass("java.lang.reflect.Modifier")

    def shim(modname):
        Mc = JClass(modname)
        for fd_ in Mc.class_.getDeclaredFields():
            if MODc.isStatic(fd_.getModifiers()) and fd_.getType() == Mc.class_:
                fd_.setAccessible(True)
                if fd_.get(None) is None:
                    o_ = us.allocateInstance(Mc.class_)
                    for f2 in Mc.class_.getDeclaredFields():
                        if f2.getType() == CTYc.class_ and not MODc.isStatic(f2.getModifiers()):
                            f2.setAccessible(True)
                            f2.set(o_, us.allocateInstance(CTYc.class_))
                    fd_.set(None, o_)
                return
    shim("com.hypixel.hytale.server.core.modules.entity.EntityModule")
    shim("com.hypixel.hytale.server.core.modules.entitystats.EntityStatsModule")
    ESMc = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap")
    DSTc = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes")
    SMO = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier")
    MTG = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier$ModifierTarget")
    CAL = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier$CalculationType")
    TCc = JClass("com.hypixel.hytale.server.core.modules.entity.component.TransformComponent")
    HRc = JClass("com.hypixel.hytale.server.core.modules.entity.component.HeadRotation")
    R3 = JClass("com.hypixel.hytale.math.vector.Rotation3f")
    V3 = JClass("org.joml.Vector3d")
    DMGc = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage")
    SE = int(DSTc.getSignatureEnergy())

    def ref(i):
        r_ = us.allocateInstance(REFc.class_)
        fld(REFc, "index").setInt(r_, JInt(i))
        return r_
    att, vic = ref(61), ref(62)
    em = ESMc()
    em.update()
    try:
        em.putModifier(JInt(SE), "sig56test", SMO(MTG.MAX, CAL.ADDITIVE, JFloat(20.0)))
    except Exception as ex_:
        xb.append(("the SignatureEnergy stat of a bare EntityStatMap", str(ex_)[:120]))
    sv = em.get(JInt(SE))
    K.notes.append("X SignatureEnergy index %d, max %s" % (SE, None if sv is None else float(sv.getMax())))

    def tcomp(x, y, z):
        o_ = us.allocateInstance(TCc.class_)
        try:
            fld(TCc, "position").set(o_, V3(JDouble(x), JDouble(y), JDouble(z)))
        except KeyError:
            for f_ in TCc.class_.getDeclaredFields():
                if f_.getType() == V3.class_:
                    f_.setAccessible(True)
                    f_.set(o_, V3(JDouble(x), JDouble(y), JDouble(z)))
                    break
        return o_
    hr = us.allocateInstance(HRc.class_)
    rot = us.allocateInstance(R3.class_)
    fld(HRc, "rotation").set(hr, rot)
    fw = hr.getDirection()
    fx_, fz_ = float(fw.x()), float(fw.z())
    K.notes.append("X the victim faces (%.2f, %.2f)" % (fx_, fz_))

    def place(ax, az):
        ma = JClass("java.util.IdentityHashMap")()
        ma.put(ESMc.getComponentType(), em)
        ma.put(TCc.getComponentType(), tcomp(ax, 64.0, az))
        mv = JClass("java.util.IdentityHashMap")()
        mv.put(TCc.getComponentType(), tcomp(0.0, 64.0, 0.0))
        mv.put(HRc.getComponentType(), hr)
        Buf.COMP.put(att, ma)
        Buf.COMP.put(vic, mv)

    def dmg(a):
        d_ = us.allocateInstance(DMGc.class_)
        fld(DMGc, "amount").setFloat(d_, JFloat(a))
        return d_

    def meter(v):
        cur = float(em.get(JInt(SE)).get())
        em.addStatValue(JInt(SE), JFloat(v - cur))
        return round(float(em.get(JInt(SE)).get()), 3)

    def baseline(iid, st):
        SX.W.remove(u)
        SX.OWN.remove(u)
        SX.step2(u, JString(iid), 0, st, JFloat(float(em.get(JInt(SE)).get())), JFloat(20.0), False, JLong(T0), JDouble(-1.0))
    if sv is not None and float(sv.getMax()) == 20.0:
        place(0.0, 30.0)
        baseline(RULE_IDS[4], cb)
        m0 = meter(5.0)
        SX.onHit(dmg(10.0), buf, att, vic, u, cb, False)
        m1 = round(float(em.get(JInt(SE)).get()), 3)
        SX.onHit(dmg(10.0), buf, att, vic, u, cb, True)
        m2 = round(float(em.get(JInt(SE)).get()), 3)
        own = round(float(SX.ownTake(u, JLong(int(SysJ.currentTimeMillis())))), 3)
        if (m0, m1, m2, own) != (5.0, 8.0, 8.0, 3.0):
            xb.append(("Combat bow: a bash adds +3 to the REAL meter (own 3), an arrow adds nothing at the hit", m0, m1, m2, own))
        meter(19.0)
        SX.onHit(dmg(10.0), buf, att, vic, u, cb, False)
        if round(float(em.get(JInt(SE)).get()), 3) != 20.0:
            xb.append("clamped at the meter max")
        tz = stack(RULE_IDS[5], doc(RULE_IDS[5], RUT))
        baseline(RULE_IDS[5], tz)
        meter(4.0)
        SX.onHit(dmg(10.0), buf, att, vic, u, tz, True)
        far = round(float(em.get(JInt(SE)).get()), 3)
        place(0.0, 10.0)
        SX.onHit(dmg(10.0), buf, att, vic, u, tz, True)
        near = round(float(em.get(JInt(SE)).get()), 3)
        if (far, near) != (6.0, 6.0):
            xb.append(("Test Zoom: +2 from 30 blocks, nothing from 10", far, near))
        SX.onHit(dmg(10.0), buf, att, vic, u, cb, False)
        if round(float(em.get(JInt(SE)).get()), 3) != 6.0:
            xb.append("a rule weapon that is not the held meter's (W) adds nothing")
        place(-fx_ * 2.0, -fz_ * 2.0)          # behind the victim
        baseline(RULE_IDS[2], pk)
        meter(2.0)
        SX.step2(u, JString(RULE_IDS[2]), 0, pk, JFloat(2.0), JFloat(20.0), False, JLong(int(SysJ.currentTimeMillis()) + 1000), JDouble(-1.0))
        # the rise first (2 -> 4), then the backstab: +2 more at the hit
        SX.W.get(u)[3][0] = 0
        SX.step2(u, JString(RULE_IDS[2]), 0, pk, JFloat(4.0), JFloat(20.0), False, JLong(int(SysJ.currentTimeMillis())), JDouble(-1.0))
        meter(4.0)
        SX.onHit(dmg(10.0), buf, att, vic, u, pk, False)
        back = round(float(em.get(JInt(SE)).get()), 3)
        place(fx_ * 2.0, fz_ * 2.0)          # in front
        SX.step2(u, JString(RULE_IDS[2]), 0, pk, JFloat(back + 2.0), JFloat(20.0), False, JLong(int(SysJ.currentTimeMillis())), JDouble(-1.0))
        meter(back + 2.0)
        SX.onHit(dmg(10.0), buf, att, vic, u, pk, False)
        front = round(float(em.get(JInt(SE)).get()), 3)
        if (back, front) != (6.0, 7.0):
            xb.append(("Pocket Knife on the shim: a +2 rise then a backstab = +2 more (6); a +2 rise then a front hit = -1 (7)", back, front))
        SX.onHit(dmg(0.0), buf, att, vic, u, pk, False)
        SX.onHit(None, buf, att, vic, u, pk, False)
    else:
        xb.append("no SignatureEnergy meter on the bare EntityStatMap - onHit not executed")
    SX.PEND.clear()
    SX.RISE.clear()
    SX.OWN.clear()
    K.check(not xb, "X GearSigX.onHit on an ECS shim + a REAL EntityStatMap: Combat bash +3 (own), clamp, Test Zoom far +2 / near 0, another weapon's "
            "meter untouched, Pocket Knife backstab / front corrections at the hit: %s" % xb)

    # ================================================================================== F the sigfx guard
    fb = []
    CALLS, ANS = [], {"owns": "W"}

    def sfx(a):
        if isinstance(a, str) or str(type(a)).find("String") >= 0:
            CALLS.append(("text", str(a)))
            o_ = ANS["owns"]
            return None if o_ is None else JString(o_)
        CALLS.append(("req", [str(x) for x in a]))
        return JObject(JBoolean(True), "java.lang.Boolean")
    SX.OWNS.clear()
    n8, n9 = int(SX.N6[8]), int(SX.N6[9])
    r0 = bool(SX.sigfx(u, JString("weightedVortex"), JString("Weapon_Sword_UT_Paperweight"), 20, JDouble(0.0)))
    br.put("armory:fn:sigfx", PyFn(sfx))
    r1 = bool(SX.sigfx(u, JString("weightedVortex"), JString("Weapon_Sword_UT_Paperweight"), 20, JDouble(0.0)))
    r1b = bool(SX.sigfx(u, JString("weightedVortex"), JString("Weapon_Sword_UT_Paperweight"), 20, JDouble(0.0)))          # cached owns: no second ask
    if r0 or r1 or r1b or CALLS != [("text", "owns:Weapon_Sword_UT_Paperweight")] or int(SX.N6[8]) != n8 + 3 or int(SX.N6[9]) != n9:
        fb.append(("no bridge / owns W = never called (owns asked once, cached)", r0, r1, r1b, CALLS))
    SX.OWNS.clear()
    ANS["owns"] = ""
    del CALLS[:]
    r2 = bool(SX.sigfx(u, JString("weightedVortex"), JString("Weapon_Sword_UT_Paperweight"), 20, JDouble(0.0)))
    if not r2 or len(CALLS) != 2 or CALLS[1][0] != "req" or CALLS[1][1] != [U, "weightedVortex", "Weapon_Sword_UT_Paperweight", "20", "0.0"] or int(SX.N6[9]) != n9 + 1:
        fb.append(("owns '' = called with {uuid, effect, item, level, hit}", r2, CALLS))
    SX.OWNS.clear()
    ANS["owns"] = None
    del CALLS[:]
    r3 = bool(SX.sigfx(u, JString("weightedVortex"), JString("Weapon_Sword_UT_Paperweight"), 20, JDouble(0.0)))
    if r3 or [c for c in CALLS if c[0] == "req"]:
        fb.append(("no String answer (an older SkyyArmory) = never", CALLS))
    # a fired Paperweight meter (full -> 0) reaches sigfx; the owns answer decides
    SX.OWNS.clear()
    ANS["owns"] = ""
    del CALLS[:]
    n7 = int(SX.N6[7])
    SX.W.remove(u)
    SX.step2(u, JString("Weapon_Sword_UT_Paperweight"), 0, pw, JFloat(20.0), JFloat(20.0), False, JLong(T0), JDouble(-1.0))
    SX.step2(u, JString("Weapon_Sword_UT_Paperweight"), 0, pw, JFloat(0.0), JFloat(20.0), False, JLong(T0 + 2000), JDouble(-1.0))
    reqs = [c for c in CALLS if c[0] == "req"]
    if int(SX.N6[7]) != n7 + 1 or len(reqs) != 1 or reqs[0][1][1] != "weightedVortex" or reqs[0][1][2] != "Weapon_Sword_UT_Paperweight":
        fb.append(("a fired Paperweight (20 -> 0) asks sigfx once", int(SX.N6[7]) - n7, CALLS))
    SX.OWNS.clear()
    ANS["owns"] = "W"
    del CALLS[:]
    SX.W.remove(u)
    SX.step2(u, JString("Weapon_Sword_UT_Paperweight"), 0, pw, JFloat(20.0), JFloat(20.0), False, JLong(T0 + 3000), JDouble(-1.0))
    SX.step2(u, JString("Weapon_Sword_UT_Paperweight"), 0, pw, JFloat(0.0), JFloat(20.0), False, JLong(T0 + 3100), JDouble(-1.0))
    if [c for c in CALLS if c[0] == "req"]:
        fb.append(("SkyyArmory owns it (W) = the fired window is NOT asked twice", CALLS))
    del CALLS[:]
    SX.step2(u, JString("Weapon_Sword_Iron"), 1, nrm, JFloat(20.0), JFloat(20.0), False, JLong(T0 + 4000), JDouble(-1.0))
    SX.step2(u, JString("Weapon_Sword_Iron"), 1, nrm, JFloat(20.0), JFloat(20.0), False, JLong(T0 + 5000), JDouble(-1.0))
    SX.step2(u, JString("Weapon_Sword_Iron"), 1, nrm, JFloat(0.0), JFloat(20.0), False, JLong(T0 + 5100), JDouble(-1.0))
    if CALLS:
        fb.append(("a weapon not in FX_ID asks nothing", CALLS))
    br.remove("armory:fn:sigfx")
    SX.OWNS.clear()
    st = str(SX.statusText())
    K.notes.append("F status: %s" % st[-260:])
    if "Untiered charge rules on" not in st or "sigfx left to SkyyArmory" not in st:
        fb.append(("statusText", st[-200:]))
    K.check(not fb, "F the sigfx guard: no bridge / owns W / no String answer = never called, owns '' = {uuid, effect, item, level, hit}, the owns "
            "answer cached; a fired Paperweight meter asks once, a normal sword never: %s" % fb)

    # ================================================================================== U the tooltips
    ub = []

    def tip(iid, d_):
        txt, col = AL(), AL()
        View.lines(JString(iid), d_, u, txt, col)
        return [str(x).replace(chr(2), "") for x in txt], [None if x is None else str(x) for x in col]
    hut, hmy, gold = str(Defs.R_HEX[RUT]), str(Defs.R_HEX[RMY]), str(Defs.C_GOLD)
    for k in range(1, 6):
        tl, tc = tip(RULE_IDS[k], doc(RULE_IDS[k], RUT))
        nm = [i for i, x in enumerate(tl) if x.startswith("Ability 1 - ")]
        if not nm or tl[nm[0]] != "Ability 1 - " + RULE_NAMES[k] or tc[nm[0]] != "*" + hut:
            ub.append((RULE_IDS[k], "the UT move name in orange", [tl[i] for i in nm], [tc[i] for i in nm]))
            continue
        if RULE_LINES[k] not in tl or len(RULE_LINES[k]) > 70:
            ub.append((RULE_IDS[k], "the rule line", tl[nm[0]:nm[0] + 5]))
        else:
            rc = tc[tl.index(RULE_LINES[k])]
            want_bad = k in (1, 2, 4)
            if not rc or (str(Defs.C_UP) not in rc) or (want_bad and str(SX.C_BAD) not in rc):
                ub.append((RULE_IDS[k], "the rule line colours (green / red)", rc))
        if k == 4:
            chl = [x for x in tl if x.startswith("Charge: ")]
            K.notes.append("U Combat bow charge line: %s" % chl)
            if not chl or "+2.3" not in chl[0] or "+0.4" not in chl[0]:
                ub.append(("the Combat bow's Charge line counts its arrow rate (x0.75: +0.5 -> +0.4, +3 -> +2.3)", chl))
    tl, tc = tip("Weapon_Sword_UT_Paperweight", doc("Weapon_Sword_UT_Paperweight", RUT))
    nm = [i for i, x in enumerate(tl) if x.startswith("Ability 1 - ")]
    if not nm or tc[nm[0]] != "*" + hut or "Fills 20% slower (Untiered)" not in tl:
        ub.append(("The Paperweight: orange name + 'Fills 20% slower (Untiered)'", [tl[i] for i in nm], tl[-6:]))
    tl, tc = tip("Weapon_Shortbow_Ricochet", doc("Weapon_Shortbow_Ricochet", RUT))
    if "Fills 25% faster (Untiered)" not in tl:
        ub.append(("Ricochet bow: 'Fills 25% faster (Untiered)'", tl[-6:]))
    tl, tc = tip("Weapon_Battleaxe_Scythe_Void", doc("Weapon_Battleaxe_Scythe_Void", RMY))
    nm = [i for i, x in enumerate(tl) if x.startswith("Ability 1 - ")]
    if not nm or tc[nm[0]] != "*" + hmy:
        ub.append(("a Mythic: the name in the Mythic colour", [tl[i] for i in nm], [tc[i] for i in nm]))
    tl, tc = tip("Weapon_Sword_Iron", doc("Weapon_Sword_Iron", 0))
    nm = [i for i, x in enumerate(tl) if x.startswith("Ability 1 - ")]
    if not nm or tl[nm[0]] != "Ability 1 - Vortexstrike" or tc[nm[0]] != "*" + gold or [x for x in tl if x in RULE_LINES.values()]:
        ub.append(("a normal sword: gold Vortexstrike, no rule line", [tl[i] for i in nm], [tc[i] for i in nm]))
    tl, tc = tip(RULE_IDS[1], doc(RULE_IDS[1], 0))
    if [x for x in tl if x == "Ability 1 - " + RULE_NAMES[1] or x in RULE_LINES.values()]:
        ub.append(("Overtime without a UT document: no UT name / rule line", tl[-6:]))
    apply(sig__rules="false", **BASE)
    tl, tc = tip(RULE_IDS[1], doc(RULE_IDS[1], RUT))
    apply(**BASE)
    if [x for x in tl if x in RULE_LINES.values()]:
        ub.append(("sig.rules off: no rule line", tl[-6:]))
    apply(sig__rule__lowHp="-10", sig__rule__highHp="20", **BASE)
    tl, tc = tip(RULE_IDS[1], doc(RULE_IDS[1], RUT))
    apply(**BASE)
    if "Fills 10% slower under half Health, 20% faster above." not in tl:
        ub.append(("live numbers in the rule line", [x for x in tl if x.startswith("Fills")]))
    K.check(not ub, "U REAL tooltips: UT move names in the UT orange + the 5 rule lines (<= 70, green / red), Paperweight -20 / Ricochet +25 lines, "
            "a Mythic in its colour, a normal sword gold, no rule line without a UT document / with sig.rules off, live numbers: %s" % ub)

    # ================================================================================== M the one-time update (text step + the real method)
    mb = []
    base_txt = "# SkyyGear 0.3.55 - x\r\npart.gate=true\r\nsig.tooltip=true\r\n"
    r = Cfg.s56Update(JString(base_txt))
    t1 = str(r[0])
    rows = [str(x) for x in r[3]]
    if "\r\nsig.ut.Weapon_Sword_UT_Paperweight=-20\r\n" not in t1 or "sig.ut.Weapon_Shortbow_Ricochet=25" not in t1 or "SkyyGear 0.3.56 signature defaults" not in t1 \
            or rows != ["sig.ut[Weapon_Sword_UT_Paperweight]", "-20", "sig.ut[Weapon_Shortbow_Ricochet]", "25"] or not t1.startswith(base_txt) or "\n" in t1.replace("\r\n", ""):
        mb.append(("absent -> added (CRLF kept, the old text untouched)", t1[-300:], rows))
    if Cfg.s56Update(JString(t1)) is not None:
        mb.append("the marker = run once")
    r2_ = Cfg.s56Update(JString("part.gate=true\nsig.ut.Weapon_Sword_UT_Paperweight=0\n"))
    t2 = str(r2_[0])
    notes = [str(x) for x in r2_[1]]
    if "sig.ut.Weapon_Sword_UT_Paperweight=0" not in t2 or t2.count("Weapon_Sword_UT_Paperweight") != 1 or "sig.ut.Weapon_Shortbow_Ricochet=25" not in t2 \
            or [str(x) for x in r2_[3]] != ["sig.ut[Weapon_Shortbow_Ricochet]", "25"] or not notes or "kept" not in notes[0]:
        mb.append(("a hand value kept + noted, only the missing one added", t2, notes))
    md = os.path.join(scratch, "mig")
    os.makedirs(md, exist_ok=True)
    fc = os.path.join(md, "config.properties")
    open(fc, "wb").write(base_txt.encode("latin-1"))
    Cfg.FILE = Paths.get(fc)
    Cfg.DIR = Paths.get(md)
    m1 = str(Cfg.migrateSig56())
    c1 = open(fc, "rb").read()
    m2 = str(Cfg.migrateSig56())
    c2 = open(fc, "rb").read()
    hist = [f for f in os.listdir(os.path.join(md, "config-history"))] if os.path.isdir(os.path.join(md, "config-history")) else []
    K.notes.append("M migrateSig56 on a scratch file: %r; history %s" % (m1[:200], hist[:3]))
    if b"sig.ut.Weapon_Sword_UT_Paperweight=-20\r\n" not in c1 or m2 != "" or c1 != c2 or not [h for h in hist if h.endswith(".bak")]:
        mb.append(("the real method: added once with a History copy, the second start nothing", m1[:120], m2, hist))
    clog = os.path.join(md, "config-changes.log")
    cl = open(clog, encoding="utf-8").read() if os.path.isfile(clog) else ""
    if "sig.ut[Weapon_Sword_UT_Paperweight]\t(none)\t-20\tok" not in cl or "sig.ut[Weapon_Shortbow_Ricochet]\t(none)\t25\tok" not in cl:
        mb.append(("2 change-log rows (Undo = remove)", cl[-300:]))
    SysJ.setProperty("skyy.harness.nosig56", "true")
    open(fc, "wb").write(base_txt.encode("latin-1"))
    m3 = str(Cfg.migrateSig56())
    SysJ.clearProperty("skyy.harness.nosig56")
    if m3 != "" or open(fc, "rb").read() != base_txt.encode("latin-1"):
        mb.append("the harness switch")
    Cfg.FILE = None
    Cfg.DIR = Paths.get(data)
    K.check(not mb, "M migrateSig56: absent ids added at the end (CRLF kept), a hand value kept + noted, the marker = once; the real method writes once "
            "with a History copy + 2 change-log rows (none -> value): %s" % mb)

    # ================================================================================== W gear:fn:elemPower
    wb = []
    z = str(Elem.powText(None))
    if z != "Earth:0,Thunder:0,Water:0,Fire:0,Air:0" or str(Elem.powText(JArray(JInt)([1, -2, 0, 4, 0]))) != "Earth:1,Thunder:0,Water:0,Fire:4,Air:0":
        wb.append(("powText", z))
    sw = "Weapon_Sword_Iron"
    dfire = doc(sw, 0)
    ml_ = AL()
    ml_.add(Data.mod(JString(str(Aug.FKEY[3])), JInt(4)))
    dfire.put("mods", BA(ml_))
    pf = str(Elem.powOf(JString(sw), dfire))
    p0 = str(Elem.powOf(JString(sw), None))
    if pf != "Earth:0,Thunder:0,Water:0,Fire:3,Air:0" or p0 != z:
        wb.append(("powOf: a rolled Fire line = Fire 3 (GearAug.power), no document = all 0", pf, p0))
    Fn = P("GearElemPowFn")()
    Elem.PW.remove(u)
    if Fn.apply(u) is not None:
        wb.append("not seen yet = null")
    Elem.PW.put(u, JString(pf))
    if str(Fn.apply(u)) != pf or str(Fn.apply(JString(U))) != pf or Fn.apply(JString("junk")) is not None or Fn.apply(None) is not None or Fn.apply(JInt(3)) is not None:
        wb.append("the Fn: UUID / uuid String / junk")
    # GearElem.note on a REAL inventory (the held weapon in hotbar slot 0)
    ICOMP = "com.hypixel.hytale.server.core.inventory.InventoryComponent$"
    SECS = (("hotbar", "Hotbar", 9), ("storage", "Storage", 36), ("backpack", "Backpack", 9), ("armor", "Armor", 4), ("utility", "Utility", 4), ("tools", "Tool", 4))

    def comp(kind, cont):
        Cc = JClass(ICOMP + kind)
        for args in ((cont, JByte(0)), (cont,)):
            try:
                return Cc(*args)
            except Exception:
                pass
        o_ = us.allocateInstance(Cc.class_)
        fld(Cc, "inventory").set(o_, cont)
        return o_
    try:
        inv = INV()
        cs = {}
        for f_, kind, n_ in SECS:
            cs[f_] = SIC(JShort(n_))
            try:
                fld(INV, f_).set(inv, comp(kind, cs[f_]))
            except Exception:
                fld(INV, f_).set(inv, cs[f_])
        cs["hotbar"].setItemStackForSlot(JShort(0), stack(sw, dfire))
        Elem.PW.remove(u)
        Elem.note(u, inv, JArray(JInt)(int(Defs.NS)))
        got = Fn.apply(u)
        cs["hotbar"].setItemStackForSlot(JShort(0), IS(JString("Rock_Stone"), JInt(1)))
        Elem.note(u, inv, JArray(JInt)(int(Defs.NS)))
        got2 = Fn.apply(u)
        Elem.forget(u)
        got3 = Fn.apply(u)
        if got is None or str(got) != pf or got2 is None or str(got2) != z or got3 is not None:
            wb.append(("GearElem.note: held Fire sword = Fire:3, a non-gear item = all 0, forget = null", got, got2, got3))
    except Exception as ex_:
        wb.append(("GearElem.note on a REAL inventory", str(ex_)[:200]))
    K.check(not wb, "W gear:fn:elemPower: powText / powOf (Fire line = Fire:3), the Fn (UUID / String / junk / not seen), GearElem.note on a REAL inventory "
            "(held weapon, a non-gear item, forget): %s" % wb)
    K.save()


# ====================================================================================================== D: start twice on the live copy
def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR, B.JAVASSIST], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Cfg = JClass(PKG + "GearCfg")
    fc = os.path.join(home, "config.properties")
    c0 = open(fc, "rb").read() if os.path.isfile(fc) else None
    K.check(c0 is not None, "D the live copy has a config.properties")
    had = [l for l in c0.decode("latin-1").splitlines() if l.startswith("sig.ut.")]
    K.notes.append("D the live file's sig.ut lines before: %s" % had)
    Paths = JClass("java.nio.file.Paths")
    Cfg.FILE = Paths.get(fc)
    Cfg.DIR = Paths.get(home)
    MIG = ["migrate0326", "migrate0330", "migrateP4", "migrateP5", "migrateP6", "migrateP7", "migrate39", "migrateUt28", "migrateCan2", "migrateAs51",
           "migrateUt53", "migrateMy53", "migrateSig56"]
    m0 = "\n".join(str(getattr(Cfg, x)()) for x in MIG if hasattr(Cfg, x))
    Cfg.load()
    c1 = open(fc, "rb").read()
    m1 = "".join(str(getattr(Cfg, x)()) for x in MIG if hasattr(Cfg, x))
    Cfg.load()
    K.notes.append("D start 1: one-time updates said %r" % m0[-600:])
    K.check(open(fc, "rb").read() == c1 and m1 == "", "D start 2 changes nothing")
    t1 = c1.decode("latin-1")
    K.check(t1.count("SkyyGear 0.3.56 signature defaults") == 1, "D the marker once")
    for i, v in (("Weapon_Sword_UT_Paperweight", -20), ("Weapon_Shortbow_Ricochet", 25)):
        line = [l for l in had if l.split("=")[0].strip() == "sig.ut." + i]
        want = int(line[0].split("=", 1)[1]) if line else v
        got = Cfg.SIG_UT.get(i)
        K.check(got is not None and int(got) == want, "D sig.ut.%s = %s (a live hand line is kept)" % (i, want))
    dl, dn = c0.decode("latin-1").splitlines(), t1.splitlines()
    extra = [l for l in dn if l not in dl]
    allowed = lambda l: (l.strip() == "" or l.startswith(("ut.", "utfx.", "utpow.", "gear.mythicItems=", "stats.as=", "sig.ut.", "# ---- ")) or "SkyyGear 0.3.5" in l)
    K.check(all(allowed(l) for l in extra), "D only the 0.3.5x one-time updates touch the file: %s" % [l for l in extra if not allowed(l)][:5])
    K.check(not [l for l in dl if l not in dn], "D no old line removed")
    K.check(bool(Cfg.SIG_RULES) and int(Cfg.SIG_OT_LOW) == 35 and b"sig.rule." not in c1, "D the rule rows are new keys: not written, defaults read")
    K.save()


HK.run_compare = T54["run_compare54"]
HK.run("SkyyGear", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("static", run_static), ("engine", run_engine), ("engine55", T55["run_engine"]), ("engine54", T54["run_engine"]), ("live", run_live)], __file__,
       live=(LIVE_DIR, "Skyy_SkyyGear"))
