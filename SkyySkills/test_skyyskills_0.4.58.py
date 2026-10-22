"""SkyySkills 0.4.58 - harness for BALANCE PASS P4 (research/Balance-P4-Combat-Spec.md; tools/skills_0_4_58_patch.py; tools/balance_model.py).
Build first: python tools/skills_0_4_58_patch.py && python SkyySkills/build_skyyskills_0.4.58.py

    python SkyySkills/test_skyyskills_0.4.58.py [--keep]

Phases (each a fresh child JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch; tools/harness_kit.py):
  S   static   the patch re-runs to identical bytes, line endings kept, setup order P3 -> P4Mig -> load
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.4.57 -> 0.4.58: + ClassStat, P4Mig; only the planned members differ
  P4  EXECUTED: ClassStat.read on the fresh default file (every table = balance_model), healthPct / defense / damage per class, speedPct for
      every class x Cloth / Light / Heavy = balance_model.p4_speed (the Warrior / Mage rule), the ceiling capPct (+ ClassStat.post on the real
      MoveSync protocol map: class source + cap source, total = min(sum, 1.8)), the Health layer amount (-20 / +35 %), RbStat.skip of our key,
      dmgFactor per class slot, CombatDmgSys / ManaRegen.tick / Acro.bonuses / Perks.tick bytecode (the new calls in place, the class factor
      after the pvp test), skill:fn:manaregen {"cast"} -> ClassStat.CAST, the MANA TIMING: ManaRegen.amount + ClassStat.dryNow / refill
      driven pulse by pulse (0.1 s) for Mage / Priest / Spellblade at Lv 1 / 5 / 10 / 20 / 30 / 40 / 60 / 80 / 100 (runs dry in 18-30 s
      under non-stop casting = balance_model.p4_tempty within 0.25 s, then the refill to 80 % of the bar in 4-9 s), the dry latch, the
      class.damage defaults = balance_model's measurement (60-250 %)
  PM  P4Mig.plan / sameAfter: the 0.4.57 jar's default file -> exactly the 0.4.58 one; admin values kept + noted; CRLF; marker once
  LIVE58  every one-time update in setup() order (0.4.57's list + P4Mig) on a scratch COPY of the live data + SkillCfg.load, started TWICE
  SIX all six Balance P4 jars (Gear 0.3.34, Mobs 0.1.14, Skills 0.4.58, Classes 0.1.44, Armory 0.1.42, Trees 0.4.4) in ONE JVM: every class
      loads + initialises together (-Xverify:all); Gear's F x Mobs' Normal Health = flat 4-6 trash hits at Lv 20-100; SkyyClasses' cast and
      SkyyArmory's charged shot reach ClassStat through skill:fn:manaregen {"cast"}; gear:fn:weight -> the armor load; THE FINAL MANA
      TIMING with SkyyClasses' real costs x its per-level cost + SkyySkills' real pools / regen / refill (18-30 s at every level); SkyyTrees'
      fxCsv -> SkyyClasses' UpFx parse at max ranks
  AA  engine-access audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util, shutil, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import balance_model as BM


def _mod(fn, name):
    s = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "balp4b", "sk")]
T57 = _mod("test_skyyskills_0.4.57.py", "test_skyyskills_0_4_57")
T48, T53 = T57.T48, T57.T53
VERSION = "0.4.58"
PKG = "com.skyy.skills."
GEN = os.path.join(HERE, "build_skyyskills_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyskills_0.4.57.py")
PATCH = os.path.join(TOOLS, "skills_0_4_58_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySkills-0.4.57.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyySkills")
ADDED = ["ClassStat", "P4Mig"]
EXPECT = {"Acro": ["~m bonuses"], "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],
          "ClassMana": ["~<clinit>"], "ClassPower": ["~<clinit>"], "OverallCfg": ["~<clinit>"],   # the P4 code defaults (Mana pools, Stamina)
          "CombatDmgSys": ["~m handle"], "CurveP3Mig": ["~m run"],   # run: the inlined fresh default file (SkillCfg.DEFAULTS, + the P4 block)
          "ManaGuard": ["~m armReport2", "~m intReport", "~m packReport"],   # the version in its report texts
          "ManaRegen": ["~<clinit>", "~m tick"], "ManaRegenFn": ["~m apply"], "Perks": ["~m switched", "~m tick"], "RbStat": ["~m skip"],
          "SkillCfg": ["~m load"], "SkyySkillsPlugin": ["~m setup"]}
CLASSES = ["Archer", "Warrior", "Assassin", "Monk", "Mage", "Berserker", "Priest", "Spellblade"]


def old_defaults():
    from jpype import JClass, JArray
    arr = JArray(JClass("java.net.URL"))(2)
    arr[0] = JClass("java.io.File")(OLD_JAR).toURI().toURL()
    arr[1] = JClass("java.io.File")(B.SERVER_JAR).toURI().toURL()
    ld = JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getPlatformClassLoader())
    return str(JClass(PKG + "SkillCfg", loader=ld).DEFAULTS)


def _props(t):
    from jpype import JClass
    p = JClass("java.util.Properties")()
    p.load(JClass("java.io.StringReader")(t))
    return dict((str(k), str(p.getProperty(k))) for k in p.stringPropertyNames())


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyySkills 0.4.58 - build script') and g.count('VERSION = "0.4.58"') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.check(g.count("makeClass(") == o.count("makeClass(") + 2 and ", cst, p4m, lvf," in g, "S two new classes (ClassStat, P4Mig), written out")
    su = g[g.index("{PKG}.CurveP3Mig.run(base)"):]
    K.check(su.index("P3Mig.run()") < su.index("{PKG}.P4Mig.run();") < su.index("SkillCfg.load"), "S setup: the P3 updates -> P4Mig -> SkillCfg.load")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def run_p4(out, jar, scratch, _home):
    from jpype import JClass, JString, JArray, JObject
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    CS, Cfg, MR, MRF, MS, RB, SD, MH = J("ClassStat"), J("SkillCfg"), J("ManaRegen"), J("ManaRegenFn"), J("MoveSync"), J("RbStat"), J("SkillDefs"), J("ManaHit")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Props = JClass("java.util.Properties")
    p = Props()
    p.load(JClass("java.io.StringReader")(str(Cfg.DEFAULTS)))
    CS.read(p)
    # ---- the tables = balance_model
    K.eq([float(CS.healthPct(c)) for c in CLASSES], [float(BM.P4_CLASSES[c][1]) for c in CLASSES], "P1 class Health % = balance_model (Warrior +35, Mage -20)")
    K.eq([float(CS.defenseOf(c)) for c in CLASSES], [float(BM.P4_CLASSES[c][2]) for c in CLASSES], "P1 class Defense = balance_model (Warrior 45)")
    K.eq([round(float(CS.damageOf(c)) * 100.0, 6) for c in CLASSES], [float(BM.P4_CLASS_DAMAGE[c]) for c in CLASSES], "P1 class damage % = balance_model")
    meas = BM.p4_damage_factors()
    K.check(all(m is not None and 60.0 <= m <= 250.0 and abs(BM.P4_CLASS_DAMAGE[c] - m) <= 0.1 * m for c, m in meas.items()),
            "P1 the class damage defaults = the Assets.zip measurement (60-250 %%): %s" % dict((c, round(m)) for c, m in meas.items()))
    K.eq([round(float(CS.regenOf(c)), 3) for c in CLASSES], [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5], "P1 Mana regen by class: Spellblade 50 %, others 100 %")
    K.eq([round(float(CS.refillOf(c)), 3) for c in CLASSES], [0.0, 0.0, 0.0, 0.0, 0.15, 0.0, 0.15, 0.15], "P1 quick refill: Mage / Priest / Spellblade 15 %/s")
    K.eq((float(CS.PER_LOAD), float(CS.MAX_FACTOR), float(CS.REFILL_DELAY), float(CS.SH_HEAD) + float(CS.SH_CHEST) + float(CS.SH_HANDS) + float(CS.SH_LEGS)),
         (4.0, 1.8, 1.0, 1.0), "P1 scalars: 4 % a load point, x1.8 ceiling, 1 s refill wait, slot shares sum to 1")
    K.eq(float(CS.REFILL_BELOW), 20.0, "P1 the quick refill starts under 20 % (mana.refillBelow)")
    # Stamina / Mana pool defaults read from the file by ClassPower / ClassMana / OverallCfg
    sta = dict((c, float(p.getProperty("stamina.classBase." + c))) for c in CLASSES)
    K.eq(sta, dict((c, float(BM.P4_CLASSES[c][3])) for c in CLASSES), "P1 stamina.classBase = balance_model (Berserker / Monk 13, Priest 4)")
    K.eq(tuple(p.getProperty(k) for k in ("mana.classBase.Mage", "mana.classBase.Priest", "mana.classBase.Spellblade", "mana.classPerLevel.Mage",
                                          "mana.classPerLevel.Priest", "mana.classPerLevel.Spellblade", "mana.regen.perLevel", "mana.refillBelow")),
         ("80", "60", "70", "14.5", "10", "6", "3", "20"), "P1 Mana (build re-tune, fix round): Mage 80 + 14.5, Priest 60 + 10, Spellblade 70 + 6 a level, regen growth 3 %, dry under 20 %")
    # ---- speed rule = balance_model for every class x armor type
    bad = []
    for c in CLASSES:
        for typ, load in (("Cloth", 0.0), ("Light", 1.0), ("Heavy", 3.0)):
            got, want = float(CS.speedPct(c, load)), BM.p4_speed(c, typ)
            if abs(got - want) > 1e-9:
                bad.append((c, typ, got, want))
        if abs(float(CS.speedPct(c, -1.0)) - BM.P4_CLASSES[c][5]) > 1e-9:
            bad.append((c, "unknown", float(CS.speedPct(c, -1.0))))
    K.check(not bad, "P2 speed %% (class x Cloth / Light / Heavy, unknown = own armor = rated) = balance_model.p4_speed: %s" % bad)
    K.check(abs(float(CS.speedPct("Warrior", 3.0)) - float(CS.speedPct("Warrior", 0.0)) + 3.0) < 1e-9 and abs(float(CS.speedPct("Mage", 3.0)) - float(CS.speedPct("Mage", 0.0)) + 24.0) < 1e-9,
            "P2 heavy armor slows a Warrior 3 %, a Mage 24 % (Mage -18 in heavy)")
    K.eq([float(CS.typeLoad(w)) for w in (1, 2, 3, 0)], [3.0, 1.0, 0.0, -1.0], "P2 gear:fn:weight 1 Heavy / 2 Light / 3 Cloth -> load 3 / 1 / 0; unknown -1")
    K.eq([round(float(CS.share(s)), 3) for s in range(5)], [0.2, 0.35, 0.15, 0.3, 0.0], "P2 slot shares in the engine's ItemArmorSlot order (Head, Chest, Hands, Legs)")
    # the ceiling through the real protocol map
    U = JClass("java.util.UUID").fromString("00000000-0000-0000-0000-000000000058")
    MS.post(U, "test.flat", "flat", 0.9, 0.0, 0.0)
    MS.post(U, "test.pct", "pct", 0.2, 0.0, 0.0)
    CS.post(U, "Monk", 0.0)        # Monk in cloth: +18 % flat
    r = list(MS.sums(U))
    K.check(abs(float(MS.speedFactor(r)) - 1.8) < 1e-4 and abs(r[0] - (0.9 + 0.18)) < 1e-5,
            "P2 ClassStat.post: class source +18 %%, the ceiling source brings (1 + 1.08) (1 + 0.2) = 2.50 down to x%.3f (1.8)" % float(MS.speedFactor(r)))
    MS.post(U, "test.flat", "flat", 0.0, 0.0, 0.0)
    MS.post(U, "test.pct", "pct", 0.0, 0.0, 0.0)
    CS.post(U, "Monk", 0.0)
    m = MS.sources(U, False)
    K.check(m is not None and not m.containsKey("skills.speedcap") and abs(float(MS.speedFactor(list(MS.sums(U)))) - 1.18) < 1e-4,
            "P2 under the ceiling: no cap source, factor x1.18")
    CS.post(U, None, -1.0)
    K.check(MS.sources(U, False) is None or not MS.sources(U, False).containsKey("skills.classweight"), "P2 no class: the class source is removed")
    K.eq((round(float(CS.capPct(0.9, 0.2)), 6), float(CS.capPct(0.5, 0.1))), (round(1.8 / 1.9 - 1.0 - 0.2, 6), 0.0), "P2 capPct (pure): over x1.8 -> the cancelling pct, under -> 0")
    # ---- the Health percent layer
    K.check(abs(float(CS.amount(200.0, -20.0)) + 40.0) < 1e-4 and abs(float(CS.amount(210.0, 35.0)) - 73.5) < 1e-4 and float(CS.amount(200.0, 0.0)) == 0.0,
            "P3 Health layer amount: 200 x -20 % = -40, 210 x 35 % = +73.5, 0 % = none")
    K.check(bool(RB.skip(JString("skyyskill_classhp"))) and bool(CS.skip(JString("skyyacc_hp"))) and bool(CS.skip(JString("skyyskill_classhp"))) and not bool(CS.skip(JString("skyyskill_health"))),
            "P3 percent layers never feed each other: RbStat skips ours, ours skips RbStat's / SkyyAccessories' / itself, flat keys count")
    # ---- dmgFactor per class slot
    got = {}
    for s in range(int(SD.N)):
        if bool(SD.isClass(s)):
            got[str(SD.CLASSES[int(SD.classIdx(s))])] = round(float(CS.dmgFactor(s)), 4)
    K.eq(dict((c, v) for c, v in got.items() if c in BM.P4_CLASS_DAMAGE), dict((c, BM.P4_CLASS_DAMAGE[c] / 100.0) for c in got if c in BM.P4_CLASS_DAMAGE),
         "P4 CombatDmgSys factor per class skill slot (%d classes)" % len(got))
    CS.ON = False
    K.check(all(float(CS.dmgFactor(s)) == 1.0 for s in range(int(SD.N))) and float(CS.healthPct("Warrior")) == 0.0 and float(CS.speedPct("Mage", 3.0)) == 0.0,
            "P4 class.stats.enabled off: factor 1, Health 0, no speed")
    CS.ON = True
    # ---- bytecode: the new calls where they belong
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
    cd = code("CombatDmgSys", "handle")
    K.check("ClassStat.dmgFactor" in cd and cd.index("PlayerRef.getComponentType") < cd.index("ClassStat.dmgFactor") < cd.rindex("setAmount"), "P5 CombatDmgSys: the pvp test, then the class factor, then setAmount")
    # FIX (critic 3.6, spec 2.4): the class factor is for WEAPON hits only - an ability hit cast by this player keeps factor 1
    K.check("SkillClass.abilCaster" in cd and "ClassStat.weaponOnly" in cd and cd.index("ClassStat.dmgFactor") < cd.index("ClassStat.weaponOnly") < cd.rindex("setAmount"),
            "FIX CombatDmgSys: abilCaster -> ClassStat.weaponOnly between the class factor and setAmount")
    UA, UB = JClass("java.util.UUID").fromString("00000000-0000-0000-0000-0000000000a1"), JClass("java.util.UUID").fromString("00000000-0000-0000-0000-0000000000b2")
    K.eq([float(CS.weaponOnly(2.02, UA, UA)), float(CS.weaponOnly(2.02, None, UA)), float(CS.weaponOnly(2.02, UB, UA))], [1.0, 2.02, 2.02],
         "FIX weaponOnly: own ability hit = 1 (Monk 202 %% not applied), weapon hit / someone else's ability = the class factor")
    # FIX (critic 2.1): the Spellblade 50 % share takes back at most half of what vanilla can still add -> the bar reaches full
    sh = [float(CS.share(0.0, 3.333, 1.0, 0.5, 100.0, 99.5)), float(CS.share(0.0, 3.333, 1.0, 0.5, 100.0, 50.0)), float(CS.share(2.0, 3.333, 1.0, 1.0, 100.0, 99.9)),
          float(CS.share(4.0, 3.333, 1.0, 0.5, 100.0, 50.0))]
    K.check(abs(sh[0] + 0.25) < 1e-9 and abs(sh[1] + 1.6665) < 1e-9 and sh[2] == 2.0 and abs(sh[3] - (2.0 - 1.6665)) < 1e-9,
            "FIX ClassStat.share: k 0.5 near full takes back half the ROOM (99.5/100: -0.25, vanilla adds 0.5 -> net +0.25), mid bar half the rate, k 1 unchanged: %s" % sh)
    mana_, steps_ = 95.0, 0
    while mana_ < 100.0 - 1e-6 and steps_ < 200:   # vanilla's own +3.333/s (room-capped) then our share, pulse by pulse (out of combat, no boost)
        before_ = mana_
        mana_ = min(100.0, mana_ + 3.333 * 0.25)
        mana_ = mana_ + float(CS.share(0.0, 3.333, 0.25, 0.5, 100.0, float(before_)))
        steps_ += 1
    K.check(mana_ >= 100.0 - 1e-3, "FIX a Spellblade bar at 95/100 reaches full out of combat (%d pulses; the old formula settled about half a pulse below)" % steps_)
    mt = code("ManaRegen", "tick")
    # FIX (dry latch never cleared): ClassStat.dry runs BEFORE the full-bar early return (the first ManaRegen.rates call comes after it)
    K.check("ClassStat.dry" in mt and "ClassStat.share" in mt and mt.index("ClassStat.dry") < mt.index("ManaRegen.amount") and mt.index("ClassStat.dry") > mt.index("getMax"),
            "FIX ManaRegen.tick: the dry latch is updated right after max / cur are read, before the full-bar return (a bar topped up to full clears it); the share via ClassStat.share")
    # FIX (critic 1.1 / 2.3): a profile switch forgets the dry latch / last cast / speed pct
    UF = JClass("java.util.UUID").fromString("00000000-0000-0000-0000-0000000000f3")
    CS.dry(UF, 100.0, 5.0)
    CS.cast(UF, 1000)
    CS.LAST.put(UF, JClass("java.lang.Double")(3.0))
    had = bool(CS.DRY.containsKey(UF)) and bool(CS.CAST.containsKey(UF)) and bool(CS.LAST.containsKey(UF))
    CS.forget(UF)
    K.check(had and not CS.DRY.containsKey(UF) and not CS.CAST.containsKey(UF) and not CS.LAST.containsKey(UF) and int(CS.sinceCast(UF, 5000)) == -1,
            "FIX ClassStat.forget: the dry latch, last cast and speed pct of that player are gone")
    K.check("ClassStat.forget" in code("Perks", "switched"), "FIX Perks.switched (profile switch) calls ClassStat.forget")
    K.check("ClassStat.refill" in mt and "ClassStat.regenOf" in mt and "ClassStat.sinceCast" in mt and "subtractStatValue" in mt, "P5 ManaRegen.tick: the class regen share + the quick refill")
    ab = code("Acro", "bonuses")
    K.check(ab.index("MoveSync.post") < ab.index("ClassStat.move") < ab.index("MoveSync.sync"), "P5 Acro.bonuses: Acrobatics source, the class source, then the sync")
    pk = code("Perks", "tick")
    K.check("ClassStat.defense" in pk and pk.index("RbStat.tick") < pk.index("ClassStat.health"), "P5 Perks.tick: + the class Defense; the Health layer after RbStat")
    # ---- skill:fn:manaregen {"cast"}
    A = JArray(JClass("java.lang.Object"))
    r1 = MRF().apply(A([JString("cast"), U]))
    K.check(bool(r1) and int(CS.sinceCast(U, JClass("java.lang.System").currentTimeMillis())) >= 0, "P6 skill:fn:manaregen {\"cast\", UUID} -> TRUE, the cast time kept")
    K.check(not bool(MRF().apply(A([JString("cast"), JString("x")]))), "P6 {\"cast\", not a UUID} -> FALSE")
    # ---- THE MANA TIMING (build re-tune): balance_model's benchmark (every owned ability on cooldown + a charged band-weapon shot every 4 s)
    # driven pulse by pulse (0.1 s) by the REAL Java maths: ManaRegen.amount (in-combat regen, growth 3 % a level past 20) x ClassStat.regenOf,
    # the DRY latch ClassStat.dryNow and the quick refill ClassStat.refill (1 s after a cast). Runs dry = the next cast cannot be paid or the
    # bar is under mana.refillBelow. The pools / costs = the shipped defaults (balance_model P4_MANA / P4_COST_PER_LEVEL = Classes 0.1.44).
    rates = JArray(JClass("float"))([5.0, 0.0, 3.3333, 0.0, 0.0])   # in combat: vanilla's 3.33 / s paused (the in-combat share applies)
    notes = []
    ok_empty, ok_refill, ok_twin = True, True, True
    abil = BM.p4_abilities()
    DT = 0.1

    def pulse(c, L, mana, pool_, since, dry):
        pct = 3.0 * max(0, L - 20)
        a = float(MR.amount(rates, pct, 65, DT, float(mana), float(pool_))) * float(CS.regenOf(c))
        mana = min(pool_, mana + a)
        dry = bool(CS.dryNow(dry, float(pool_), float(mana)))
        mana += float(CS.refill(float(CS.refillOf(c)), float(pool_), float(mana), DT, int(round(since * 1000)), True, dry))
        return min(pool_, mana), dry
    for c in ("Mage", "Priest", "Spellblade"):
        for L in BM.P4_MANA_LEVELS:
            pool_ = BM.p4_pool(c, L)
            per = 1.0 + (BM.P4_COST_PER_LEVEL.get(c, 1.5) / 100.0) * L
            rows = [r_ for r_ in abil.get(c, []) if BM.P4_UNLOCK.get(r_[1], 99) <= L and r_[1] != 4]
            ready = dict((r_[0], 0.0) for r_ in rows)
            shot = {"Mage": 2 * BM.p4_wand(L), "Priest": BM.p4_wand(L)}.get(c, 0)
            t, mana, last_cast, empty, nxt, dry = 0.0, pool_, -99.0, None, 0.0, False
            while t < 300.0 and empty is None:
                for r_ in rows:
                    if t >= ready[r_[0]] - 1e-9:
                        if mana < r_[2] * per:
                            empty = t
                            break
                        mana -= r_[2] * per
                        ready[r_[0]] = t + r_[3]
                        last_cast = t
                if empty is None and shot and t >= nxt - 1e-9:
                    if mana < shot:
                        empty = t
                    else:
                        mana -= shot
                        nxt = t + 4.0
                        last_cast = t
                if empty is None and mana < float(CS.REFILL_BELOW) / 100.0 * pool_:
                    empty = t
                if empty is None:
                    mana, dry = pulse(c, L, mana, pool_, t - last_cast, dry)
                    t += DT
            # refill: from an empty, dry bar right after a cast - basic attacks only (one quick shot a second at 1/5 of the charged cost)
            t2, m2, nq, dry2 = 0.0, 0.0, 0.0, True
            quick = shot / 5.0
            while m2 < 0.8 * pool_ and t2 < 60.0:
                m2, dry2 = pulse(c, L, m2, pool_, t2, dry2)
                if t2 >= nq - 1e-9:
                    m2 = max(0.0, m2 - quick)
                    nq = t2 + 1.0
                t2 += DT
            bm = BM.p4_tempty(c, L, abil=abil)
            notes.append("%s Lv %d: pool %.0f, runs dry after %s s of non-stop casting (balance_model %s), 80 %% back after %.1f s of basic attacks"
                         % (c, L, pool_, "%.1f" % empty if empty is not None else "never (300+)", "%.1f" % bm if bm is not None else "never", t2))
            ok_empty = ok_empty and empty is not None and 18.0 - 1e-6 <= empty <= 30.0 + 1e-6
            ok_twin = ok_twin and bm is not None and empty is not None and abs(bm - empty) <= 0.25
            if L in (20, 60):
                ok_refill = ok_refill and 4.0 <= t2 <= 9.0
    K.notes.extend(notes)
    print("\n".join("  MANA " + n for n in notes))
    K.check(ok_empty, "P7 Mana timing (the real ManaRegen.amount + ClassStat.dryNow / refill): Mage / Priest / Spellblade run dry in 18-30 s at Lv %s" % "/".join(str(L) for L in BM.P4_MANA_LEVELS))
    K.check(ok_twin, "P7 the Java pulse sim = balance_model.p4_tempty (within 0.25 s) at every level")
    K.check(ok_refill, "P7 80 %% back in 4-9 s of basic attacks (Lv 20 / 60)")
    K.check(int(CS.sinceCast(JClass("java.util.UUID").randomUUID(), 1000)) == -1 and float(CS.refill(0.15, 100.0, 0.0, 1.0, 500, True, True)) == 0.0
            and abs(float(CS.refill(0.15, 100.0, 0.0, 1.0, 1000, True, True)) - 15.0) < 1e-6 and float(CS.refill(0.15, 100.0, 0.0, 1.0, 5000, False, True)) == 0.0
            and float(CS.refill(0.15, 100.0, 50.0, 1.0, 5000, True, False)) == 0.0,
            "P7 the refill waits 1 s after a cast (500 ms: none, 1000 ms: 15 %), only in combat, only while dry; never cast = long ago")
    K.check([bool(CS.dryNow(False, 100.0, 25.0)), bool(CS.dryNow(False, 100.0, 19.0)), bool(CS.dryNow(True, 100.0, 90.0)), bool(CS.dryNow(True, 100.0, 100.0)), bool(CS.dryNow(True, 0.0, 0.0))]
            == [False, True, True, False, False], "P7 the dry latch: on under 20 %, kept until full, off at full / no pool")
    U2 = JClass("java.util.UUID").fromString("00000000-0000-0000-0000-000000000059")
    K.check([bool(CS.dry(U2, 100.0, 10.0)), bool(CS.dry(U2, 100.0, 60.0)), bool(CS.dry(U2, 100.0, 100.0)), bool(CS.dry(U2, 100.0, 60.0))] == [True, True, False, False],
            "P7 ClassStat.dry keeps the latch per player (DRY map): dry at 10, still at 60, off at full, not again at 60")
    mt2 = code("ManaRegen", "tick")
    K.check(mt2.index("ClassStat.dry") < mt2.index("ClassStat.refill"), "P7 ManaRegen.tick: the latch before the refill")
    K.save()


def run_pm(out, jar, scratch, _home):
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    M, Cfg = JClass(PKG + "P4Mig"), JClass(PKG + "SkillCfg")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    OLD = old_defaults()
    NEW = str(Cfg.DEFAULTS)
    r = M.plan(JString(OLD))
    K.check(r is not None and _props(str(r[0])) == _props(NEW), "PM the 0.4.57 jar's default file -> exactly the 0.4.58 one (Properties)")
    rows = [str(x) for x in r[1]]
    K.check(len(rows) == 3 * (len(M.KEYS) + len(M.ADDK)) and "mana.classBase[Mage]" in rows and "stamina.classPerLevel[Priest]" in rows and "class.damage[Monk]" in rows,
            "PM change-log rows: %d moved + %d added (table rows as table[entry])" % (len(M.KEYS), len(M.ADDK)))
    K.check(bool(M.sameAfter(JString(OLD).getBytes("ISO-8859-1"), JString(str(r[0])).getBytes("ISO-8859-1"), r)), "PM sameAfter: only the planned keys differ")
    K.check(M.plan(r[0]) is None and M.plan(JString(NEW)) is None, "PM the marker: a second plan / a fresh file = null")
    hand = OLD.replace("\nmana.classBase.Mage=45\n", "\nmana.classBase.Mage=60\n").replace("\nmana.regen.perLevel=5\n", "\nmana.regen.perLevel=4\n")
    rh = M.plan(JString(hand))
    ph = _props(str(rh[0]))
    K.check(ph["mana.classBase.Mage"] == "60" and ph["mana.regen.perLevel"] == "4" and ph["mana.classBase.Priest"] == "60" and "mana.classBase.Mage=60 kept" in str(rh[3])
            and "mana.regen.perLevel=4 kept" in str(rh[3]), "PM hand-edited Mage 60 / regen 4 kept + noted, Priest moved: %s" % str(rh[3])[:200])
    crlf = OLD.replace("\n", "\r\n")
    rc = M.plan(JString(crlf))
    K.check(_props(str(rc[0])) == _props(NEW) and "\n" not in str(rc[0]).replace("\r\n", ""), "PM CRLF: same settings, every line ending CRLF")
    K.save()


def run_live58(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    lc = os.path.join(os.path.dirname(home), "copy58")
    shutil.copytree(home, lc)
    L = T48.loader_for(jar)
    J = lambda n: JClass(PKG + n, loader=L)
    Cfg, Sto, Hist, CLog, Rows, LF, C, M, M4, CS = J("SkillCfg"), J("SkillStore"), J("CfgHist"), J("CfgLog"), J("CfgRows"), J("LvFloor"), J("CurveP3Mig"), J("P3Mig"), J("P4Mig"), J("ClassStat")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    xp = os.path.join(lc, "xp.properties")

    def start():
        Cfg.FILE = T48.jpath(xp)
        Sto.DATA.clear()
        Sto.DIR = T48.jpath(os.path.join(lc, "players"))
        Hist.DIR = None
        Rows.HOME = None
        CLog.FILE = None
        CLog.Q.clear()
        LF.NEW_FARM = False
        r = dict((nm, str(J(nm).run())) for nm in T57.MIGS)
        ok = bool(C.run(T48.jpath(lc)))
        r["P3Mig"] = str(M.run()) if ok else ""
        if ok:
            C.after(T48.jpath(lc))
        r["P4Mig"] = str(M4.run())
        r["load"] = str(Cfg.load())
        return r
    s0 = T53.snapd(lc)
    before = _props(open(xp, encoding="latin-1").read())
    r1 = start()
    s1 = T53.snapd(lc)
    K.notes.append("LIVE58 start 1: P4Mig: %s" % r1["P4Mig"][:300])
    K.check("updated for 0.4.58" in r1["P4Mig"], "LIVE58 start 1: P4Mig ran: %s" % r1["P4Mig"][:160])
    after = _props(open(xp, encoding="latin-1").read())
    K.eq((after.get("mana.classBase.Mage"), after.get("mana.classPerLevel.Priest"), after.get("mana.regen.perLevel"), after.get("stamina.classBase.Monk"), after.get("class.damage.Archer")),
         ("80", "10", "3", "13", "200"), "LIVE58 the live copy holds the P4 numbers")
    planned = set(str(k) for k in M4.KEYS) | set(str(k) for k in M4.ADDK) | set(str(k) for k in M.KEYS) | set(str(k) for k in M.ADDK) | set(["bridge.bonus.xpSkills"])   # + Xp56Mig (0.4.56, the live copy never ran it)
    other = sorted(k for k in set(before) | set(after) if after.get(k) != before.get(k) and k not in planned)
    K.check(not other, "LIVE58 only the P3 / P4 planned keys changed: %s" % other[:12])
    K.check(float(CS.healthPct("Warrior")) == 35.0 and abs(float(CS.speedPct("Mage", 3.0)) + 18.0) < 1e-9, "LIVE58 SkillCfg.load of the migrated copy: ClassStat holds the P4 tables")
    found = any(open(os.path.join(r_, f_), "rb").read() == s0["xp.properties"] for r_, _d, fs in os.walk(os.path.join(lc, "config-history")) for f_ in fs) or \
        any(b"mana.classBase.Mage=45" in open(os.path.join(r_, f_), "rb").read() for r_, _d, fs in os.walk(os.path.join(lc, "config-history")) for f_ in fs)
    K.check(found, "LIVE58 config-history holds the pre-P4 xp.properties")
    cl = s1.get("config-changes.log", b"").decode("utf-8", "replace")
    K.check(cl.count("\tSkyySkills 0.4.58\t") == len(M4.KEYS) + len(M4.ADDK), "LIVE58 one change-log row per P4 change (%d)" % cl.count("\tSkyySkills 0.4.58\t"))
    r2 = start()
    s2 = T53.snapd(lc)
    K.check(all(s1.get(k) == s2.get(k) for k in set(s1) | set(s2)) and r2["P4Mig"] == "", "LIVE58 start 2 changes nothing")
    K.save()



# ============================================================================================ SIX: all six Balance P4 jars in ONE JVM (spec 6.4)
SIX = [os.path.join(ROOT, "SkyyGear", "SkyyGear-0.3.34.jar"), os.path.join(ROOT, "SkyyMobs", "SkyyMobs-0.1.14.jar"), JAR,
       os.path.join(ROOT, "SkyyClasses", "SkyyClasses-0.1.44.jar"), os.path.join(ROOT, "SkyyArmory", "SkyyArmory-0.1.42.jar"),
       os.path.join(ROOT, "SkyyTrees", "SkyyTrees-0.4.4.jar")]


def run_six(out, jar, scratch, _home):
    from jpype import JClass, JString, JImplements, JOverride, JArray
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST] + SIX, verify=True)
    Sys = JClass("java.lang.System")
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    Sys.getProperties().put("skyy.bridge", br)
    Cls, loader = JClass("java.lang.Class"), JClass("java.lang.ClassLoader").getSystemClassLoader()
    bad, n = [], 0
    for j in SIX:
        for c in HK.jar_classes(j):
            try:
                Cls.forName(c, True, loader)
                n += 1
            except Exception as e:
                bad.append((os.path.basename(j), c, str(e)[:120]))
    K.check(not bad and n > 500, "SIX all six jars' classes load + initialise together with -Xverify:all (%d classes): %s" % (n, bad[:3]))
    JClass("com.skyy.skills.SkillCfg").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    JClass("com.skyy.armory.ArmoryLog").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyArmory")
    # ---- 1. ONE curve: Gear's F (its own parser + eval) x Mobs' Normal Health table -> the same trash hits at every level (spec 1.2)
    GC, GB, MC = JClass("com.skyy.gear.GearCfg"), JClass("com.skyy.gear.GearBase"), JClass("com.skyy.mobs.MobCfg")
    MC.useDefaults()
    pF = GC.curvePts(GC.CURVE_DEF)
    hits = []
    for L in range(20, 101, 10):
        f = float(GB.eval(pF, float(L)))
        hit = BM.P4_REF_HIT * f * BM.p4_bonus(L) * BM.p4_perk(L) * BM.P4_KIT["expected"]
        hits.append((L, BM.P4_HP_FLOOR * float(MC.hpMult(L)) / hit))
    K.notes.append("SIX trash hits (expected kit, M) with the jars' own curves: %s" % ", ".join("Lv %d %.2f" % x for x in hits))
    K.check(all(4.0 <= h <= 6.0 for _L, h in hits) and max(h for _L, h in hits) / min(h for _L, h in hits) < 1.06,
            "SIX Gear F x Mobs Health: trash 4-6 hits at Lv 20-100, flat within 6 %% (%.2f-%.2f)" % (min(h for _L, h in hits), max(h for _L, h in hits)))
    # ---- 2. the shared registry: SkyySkills' skill:fn:manaregen {"cast"} reached by SkyyClasses' cast and SkyyArmory's charged shot
    CS, MR, MRF = JClass("com.skyy.skills.ClassStat"), JClass("com.skyy.skills.ManaRegen"), JClass("com.skyy.skills.ManaRegenFn")
    AB, AD, AN, AC, CD = (JClass("com.skyy.classes." + x) for x in ("Abil", "AbilDefs", "AbilNum", "AbilCfg", "ClassDefs"))
    SPN = JClass("com.skyy.armory.ArmorySpawn")
    br.put("skill:fn:manaregen", MRF())
    U1, U2 = JClass("java.util.UUID").fromString("00000000-0000-0000-0000-0000000005a1"), JClass("java.util.UUID").fromString("00000000-0000-0000-0000-0000000005a2")
    now = Sys.currentTimeMillis()
    K.check(int(CS.sinceCast(U1, now)) == -1 and bool(AB.manaCast(U1)) and 0 <= int(CS.sinceCast(U1, Sys.currentTimeMillis())) < 5000,
            "SIX SkyyClasses' cast (Abil.manaCast) -> SkyySkills ClassStat keeps the cast time")
    K.check(int(CS.sinceCast(U2, now)) == -1 and bool(SPN.castNote(U2)) and 0 <= int(CS.sinceCast(U2, Sys.currentTimeMillis())) < 5000,
            "SIX SkyyArmory's charged shot (ArmorySpawn.castNote) -> SkyySkills ClassStat keeps the cast time")
    br.put("gear:fn:weight", JClass("com.skyy.gear.GearLLFn")(6))
    w = br.get("gear:fn:weight").apply(JString("Armor_Iron_Chest"))
    K.check(w is not None and float(CS.typeLoad(int(w))) in (0.0, 1.0, 3.0), "SIX SkyyGear's gear:fn:weight -> SkyySkills' armor load (%s -> %s)" % (w, float(CS.typeLoad(int(w)))))
    # ---- 3. THE FINAL MANA TIMING: SkyyClasses' real walking costs (AbilDefs.mana) x its real per-level cost (Abil.costLvl through a fake
    # skill:fn:level), SkyySkills' real default pools (the file) + regen + dry latch + refill, SkyyArmory's cost ladder (balance_model P4_WANDS
    # = SkyyArmory's WANDS, asserted by the Armory build) - a charged shot every 4 s, every owned ability on cooldown
    p = JClass("java.util.Properties")()
    p.load(JClass("java.io.StringReader")(str(JClass("com.skyy.skills.SkillCfg").DEFAULTS)))
    CS.read(p)
    AN.sync()
    LV = {"lv": 1}

    @JImplements("java.util.function.Function")
    class Lvl(object):
        @JOverride
        def apply(self, a):
            return JClass("java.lang.Integer").valueOf(LV["lv"])
    br.put("skill:fn:level", Lvl())
    names = [str(x) for x in CD.NAMES]
    K.eq(dict((c, float(AC.costPct(names.index(c)))) for c in names), dict((c, float(BM.P4_COST_PER_LEVEL.get(c, 1.5))) for c in names),
         "SIX SkyyClasses' abil.costPerLevel = balance_model's (the Mana budget's input)")
    abil = BM.p4_abilities()
    rates = JArray(JClass("float"))([5.0, 0.0, 3.3333, 0.0, 0.0])
    DT = 0.1
    res, ok = [], True
    for c in ("Mage", "Priest", "Spellblade"):
        for L in BM.P4_MANA_LEVELS:
            LV["lv"] = L
            pool_ = float(p.getProperty("mana.classBase." + c)) + float(p.getProperty("mana.classPerLevel." + c)) * L + 0.1 * L
            rows = []
            for r_ in abil.get(c, []):
                if BM.P4_UNLOCK.get(r_[1], 99) <= L and r_[1] != 4:
                    ai = int(AD.find(r_[0]))
                    rows.append((r_[0], float(AD.mana(ai, 0)) * float(AB.costLvl(U1, ai)), int(AD.cdMs(ai, 0)) / 1000.0))   # the jar's own cost + cooldown
            ready = dict((r_[0], 0.0) for r_ in rows)
            shot = {"Mage": 2 * BM.p4_wand(L), "Priest": BM.p4_wand(L)}.get(c, 0)
            t, mana, last, empty, nxt, dry = 0.0, pool_, -99.0, None, 0.0, False
            while t < 300.0 and empty is None:
                for nm, cost, cd in rows:
                    if t >= ready[nm] - 1e-9:
                        if mana < cost:
                            empty = t
                            break
                        mana -= cost
                        ready[nm] = t + cd
                        last = t
                if empty is None and shot and t >= nxt - 1e-9:
                    if mana < shot:
                        empty = t
                    else:
                        mana -= shot
                        nxt = t + 4.0
                        last = t
                if empty is None and mana < float(CS.REFILL_BELOW) / 100.0 * pool_:
                    empty = t
                if empty is None:
                    a = float(MR.amount(rates, 3.0 * max(0, L - 20), 65, DT, float(mana), float(pool_))) * float(CS.regenOf(c))
                    mana = min(pool_, mana + a)
                    dry = bool(CS.dryNow(dry, float(pool_), float(mana)))
                    mana = min(pool_, mana + float(CS.refill(float(CS.refillOf(c)), float(pool_), float(mana), DT, int(round((t - last) * 1000)), True, dry)))
                    t += DT
            res.append((c, L, pool_, empty))
            ok = ok and empty is not None and 18.0 - 1e-6 <= empty <= 30.0 + 1e-6
    for c in ("Mage", "Priest", "Spellblade"):
        line = "%s: %s" % (c, ", ".join("Lv %d pool %.0f runs dry after %s s" % (L, pl, "%.1f" % e if e is not None else "never") for cc, L, pl, e in res if cc == c and L in (1, 20, 60, 100)))
        print("  SIX MANA " + line)
        K.notes.append("SIX MANA " + line)
    K.check(ok, "SIX the six jars together: Mage / Priest / Spellblade run dry in 18-30 s at Lv %s (%s)" % (
        "/".join(str(L) for L in BM.P4_MANA_LEVELS), "; ".join("%s %s" % (c, "/".join("%.0f" % (e or 999) for cc, L, pl, e in res if cc == c)) for c in ("Mage", "Priest", "Spellblade"))))
    # ---- 4. SkyyTrees' fx totals -> SkyyClasses' UpFx parse (the P4 per-rank numbers arrive as written)
    TV, TS, TC, UF = JClass("com.skyy.trees.TreeV3"), JClass("com.skyy.trees.TreeStore"), JClass("com.skyy.trees.TreeCfg"), JClass("com.skyy.classes.UpFx")
    Paths = JClass("java.nio.file.Paths")
    base = os.path.join(scratch, "six")
    os.makedirs(os.path.join(base, "players"), exist_ok=True)
    TS.DIR = Paths.get(os.path.join(base, "players"))
    TC.FILE = Paths.get(os.path.join(base, "trees.properties"))
    TC.load()
    keys = [str(x) for x in TV.UKEY]
    tn = [str(x) for x in TV.TNAME]
    got = {}
    for cls, uid, code in (("Archer", "b1.r5b", "dmgFocus"), ("Warrior", "b1.r5b", "drStill"), ("Monk", "b1.r1a", "move")):
        k = "Class.%s.%s" % (cls, uid)
        i = keys.index(k)
        f = "six" + cls.lower()
        with open(os.path.join(base, "players", f + ".properties"), "w") as fh:
            fh.write("v=3" + chr(10) + "treesV3=1" + chr(10) + "gates41=1" + chr(10) + "%s=%d" % (k, int(TV.UMAX[i])) + chr(10))
        csv = str(TV.fxCsv(TS.readFile(f), tn.index(cls)))
        v = UF.vec("v3,A1" + csv)
        got[code] = (float(UF.g(v, UF.idx(code))) if v is not None else None, int(TV.UMAX[i]))
    K.eq(got, {"dmgFocus": (3.0, 3), "drStill": (9.0, 3), "move": (15.0, 5)}, "SIX SkyyTrees fxCsv -> SkyyClasses UpFx at max ranks: Focus Fire 3 x 1, Anchor 3 x 3, Haste 5 x 3")
    K.save()

if __name__ == "__main__":
    phases = [("static", run_static), ("p4", run_p4), ("pm", run_pm), ("live58", run_live58), ("six", run_six)]
    HK.run(name="SkyySkills", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=phases, script=__file__, live=(LIVE_DIR, "Skyy_SkyySkills"))
