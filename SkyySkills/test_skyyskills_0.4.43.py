"""SkyySkills 0.4.43 - harness for tools/skills_0_4_43_patch.py: (A) the Spellblade's class skill Battlemagic (storage slot 19), (B) base
Health regen for everyone (HpRegen + skill:fn:hpregen), (C) Mining vs Foraging XP (XpEven: felled logs %, the Mining XP multiplier).
Build first: python tools/skills_0_4_43_patch.py && python SkyySkills/build_skyyskills_0.4.43.py
             (+ the jars the inherited 0.4.42 phases read - read only)

    python SkyySkills/test_skyyskills_0.4.43.py [--dir <empty folder inside tools/dev/scratch/>] [--keep] [--no-old]

Phases (each a fresh child JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch; tools/harness_kit.py):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.4.42 -> 0.4.43: + HpRegen, HpRegenFn, XpEven; the classes the three changes touch (EXPECT below); manifest.json only
  SB  the Spellblade: SkillDefs (slot 19 Combat.Spellblade / Battlemagic, N 20, CLASSES + CLASS_SLOT, nothing renumbered), class:<uuid>
      Spellblade -> slot 19 (SkillClass.slot / rowSlot / skillName = class:skill "Battlemagic" = the Skills row; PartyXp.slotFor), the
      class XP multiplier like every class skill, XP added to slot 19 (SkillStore.addK = the store step of every kill / party award),
      saved as Combat.Spellblade (snap) and read back, an OLD file without the key loads (0 XP, paid = level), the Overall Level counts
      Battlemagic exactly like Divinity, OverallCfg.TCLASSES unchanged (8 names, same order), KillSys / PartyXp route through
      SkillClass.slot (bytecode)
  OLD the 0.4.42 jar reading a file WITH Combat.Spellblade: no error, the known slots intact; its save drops the key (the ROLLBACK FLOOR)
  HP  base Health regen: the config (defaults, custom, clamps), rate (in / out of combat, Overall Level scaling, bridge flat / %),
      amount (cap at max, dead, empty, full), the combat timing (hurt or hitting, the 5 s edge, never / future stamps), the REAL
      HpRegen.tick on engine stand-ins (Store with a TimeResource, CommandBuffer with a DamageDataComponent, an EntityStatMap recording
      addStatValue, a DeathComponent): pulse every 0.5 s, in / out of combat amounts, the cap, dead / Health 0 = nothing, off = nothing;
      skill:fn:hpregen (add / addpct / remove / clear / get / now / fight / sources / row / bad args), the Stats row (<= 60 characters),
      the show action (<= 120), WIRE (AcroSys -> ManaRegen.tick + HpRegen.tick, SkillCfg.load -> read, Acro.retainOnline -> retain, the
      plugin publishes / removes skill:fn:hpregen, the fresh xp.properties lists the 0.4.43 block)
  EV  Mining vs Foraging: XpEven.pay (exact whole part, the fraction by chance), the averages (1 XP stone x 1.25 = 1.25, a 6 XP log at 70 %
      = 4.2), the config (defaults 70 / 1.25, custom, clamps), WIRE (BreakTask.run -> XpEven.mine, FellCredit.one -> XpEven.fellLog)
  0.4.42's phases on the 0.4.43 jar (its FORT phase + every inherited phase) - the checks pinning 0.4.42's row count / slot count are
      expected to differ (EXPECTED43 below, each with its reason).
  AA  engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW

VERSION = "0.4.43"
PKG = "com.skyy.skills."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySkills-0.4.42.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "skills0443", "sk")))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyySkills")
os.environ.setdefault("SKYYROUTE_SESSION", os.path.join(SCRATCH, "routesession"))
# 0.4.42 -> 0.4.43: SkillDefs.N 19 -> 20 is a compile-time constant javac / javassist inline (bipush 20) into every class that sizes or
# bounds by it (most entries below: readFile / snap / level / rows / pages / party / rebirth loops); + HpRegen.tick (AcroSys), retain (Acro),
# read (SkillCfg.load), XpEven (BreakTask.run, FellCredit.one), the setup / shutdown bridge key, the config rows + default file (CfgRows,
# CfgFile, CfgFn, ManaGuard version texts), SkillDefs' slot tables (+ Battlemagic)
EXPECT = {
    'Acro': ['~m retainOnline'],
    'AcroSys': ['~m tick'],
    'BreakTask': ['~m run'],
    'BridgeCfg': ['~m read'],
    'BridgeXp': ['~m grantSlot', '~m offerX', '~m paidX'],
    'CfgFile': ['~<clinit>'],
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'ClassMana': ['~m amountFor'],
    'ClassPower': ['~m boostRegen', '~m classLevel'],
    'Fell': ['~m end'],
    'FellCredit': ['~m one'],
    'GatherPace': ['~m read'],
    'ManaGuard': ['~<clinit>', '~m armReport2', '~m intReport', '~m packReport'],
    'ManaRegen': ['~m classPct'],
    'Overall': ['~m listText', '~m maxLevel', '~m sums'],
    'OverallCfg': ['~m exactSlot'],
    'OwnCurve': ['~m deliver', '~m moves', '~m start'],
    'PartyXp': ['~m add', '~m note', '~m routed', '~m text'],
    'SkillBonus': ['~m treeAvailable', '~m xpBonus'],
    'SkillCap': ['~m cap', '~m extra', '~m fetch', '~m level'],
    'SkillCfg': ['~m load'],
    'SkillClass': ['~m skillName'],
    'SkillDefs': ['~<clinit>', '~m rebirthResets', '~m setOwn'],
    'SkillKit': ['~m checkSkills'],
    'SkillLv': ['~m parseTable', '~m slotOf'],
    'SkillMsg': ['~m note', '~m takeArr'],
    'SkillRb': ['~m commit', '~m facts'],
    'SkillRunFn': ['~m apply'],
    'SkillStore': ['~m level', '~m moveLegacy', '~m owesK', '~m payLocked', '~m rbReset0', '~m readFile', '~m seedTop', '~m snap', '~m topPut'],
    'SkillTop': ['~<clinit>'],
    'SkillXp': ['~m gain4', '~m petXp'],
    'SkillsPage': ['~m build', '~m handleDataEvent'],
    'SkyySkillsPlugin': ['~m setup', '~m shutdown'],
    'StatsPage': ['~m build'],
}
ADDED = ["HpRegen", "HpRegenFn", "XpEven"]


def tmod(fn, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


_EQ0 = HK.Child.eq
T42 = tmod("test_skyyskills_0.4.42.py", "t0442")
HK.Child.eq = _EQ0


def _bridge():
    from jpype import JClass
    Sys = JClass("java.lang.System")
    br = Sys.getProperties().get("skyy.bridge")
    if br is None:
        br = JClass("java.util.concurrent.ConcurrentHashMap")()
        Sys.getProperties().put("skyy.bridge", br)
    return br


def _fn(f):
    from jpype import JImplements, JOverride

    @JImplements("java.util.function.Function")
    class Fn(object):
        @JOverride
        def apply(self, o):
            return f(o)
    return Fn()


# ============================================================================================ SB: the Spellblade's Battlemagic slot
def run_sb(out, jar, scratch, _home):
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    D, SC, Sto, Cfg, Ov, OC, PX = J("SkillDefs"), J("SkillClass"), J("SkillStore"), J("SkillCfg"), J("Overall"), J("OverallCfg"), J("PartyXp")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    br = _bridge()
    UUID = JClass("java.util.UUID")
    names, labels = [str(x) for x in D.NAMES], [str(x) for x in D.LABELS]
    K.check(int(D.N) == 20 and names[19] == "Combat.Spellblade" and labels[19] == "Battlemagic" and str(D.COLORS[19]) == "#6fd0d8",
            "SB slot 19 = Combat.Spellblade / Battlemagic / #6fd0d8, N 20")
    K.check(names[:19] == ["Mining", "Foraging", "Farming", "Combat", "Acrobatics", "Combat.Archer", "Combat.Warrior", "Combat.Assassin",
                           "Combat.Shaman", "Combat.Mage", "Alchemy", "Smithing", "Cooking", "Exploration", "Combat.Berserker", "Combat.Priest",
                           "Fishing", "Ranching", "Orchard"], "SB every 0.4.42 slot keeps its index + saved key: %s" % names[:19])
    K.check([str(x) for x in D.CLASSES] == ["Archer", "Warrior", "Assassin", "Monk", "Mage", "Berserker", "Priest", "Spellblade"]
            and [int(x) for x in D.CLASS_SLOT] == [5, 6, 7, 8, 9, 14, 15, 19], "SB CLASSES + CLASS_SLOT: Spellblade -> 19")
    K.check(bool(D.isClass(19)) and int(D.classIdx(19)) == 7 and int(D.perkRow(19)) == int(D.COMBAT), "SB slot 19 is a class slot (combat perk row)")
    K.check(int(D.indexOf("Battlemagic")) == 19 and int(D.indexOf("battle magic")) == 19 and int(D.indexOf("Spellblade")) == 19 and int(D.indexOf("Combat.Spellblade")) == 19,
            "SB indexOf: Battlemagic / battle magic / Spellblade / the saved key -> 19")
    K.check([str(x) for x in OC.TCLASSES] == ["Archer", "Warrior", "Assassin", "Monk", "Mage", "Berserker", "Priest", "Spellblade"],
            "SB OverallCfg.TCLASSES unchanged (the Spellblade table lines stay): %s" % [str(x) for x in OC.TCLASSES])
    u = UUID.fromString("00000000-0000-4000-8000-0000000005b1")
    br.put("class:fn:allowed", _fn(lambda o: JClass("java.lang.Boolean").TRUE))
    br.put("class:" + str(u), "Spellblade")
    K.check(int(SC.slotOfClass("Spellblade")) == 19 and int(SC.slotOfClass("spellblade")) == 19 and int(SC.slot(u)) == 19, "SB class:<uuid> Spellblade -> slot 19")
    K.check(int(SC.rowSlot(u, int(D.COMBAT))) == 19, "SB the Skills page's class row shows slot 19 (not 'choose a class')")
    K.check(str(SC.skillName(u, 19)) == "Battlemagic", "SB row title without class:skill = Battlemagic")
    br.put("class:skill:" + str(u), "Battlemagic")
    K.check(str(SC.skillName(u, 19)) == "Battlemagic", "SB row title = class:skill:<uuid> Battlemagic")
    K.check(int(PX.slotFor(u)) == 19, "SB party share / kill route: PartyXp.slotFor = 19")
    K.check(int(Cfg.classXp(19, 100)) == int(Cfg.classXp(15, 100)) and int(Cfg.classXp(19, 100)) > 0, "SB class XP multiplier like Divinity (%s)" % Cfg.classXp(19, 100))
    # saved data: an old file (no Combat.Spellblade) loads; XP added; saved under the new key; read back
    pdir = os.path.join(scratch, "sbplayers")
    os.makedirs(pdir, exist_ok=True)
    Paths, Arr = JClass("java.nio.file.Paths"), JClass("java.lang.reflect.Array")
    Sto.DIR = Paths.get(pdir, Arr.newInstance(JString.class_, 0))
    k = str(Sto.pkey(u))
    open(os.path.join(pdir, k + ".properties"), "w").write("name=Sb\nquiet=false\nMining=1200\nMining.paid=2\nCombat.Priest=1000\nCombat.Priest.paid=1\n")
    got = Sto.readFile(k, u)
    d = got[0]
    K.check(len(d) == 40 and int(d[0]) == 1200 and int(d[15]) == 1000 and int(d[19]) == 0 and int(d[20 + 19]) == 0,
            "SB an OLD file (no Combat.Spellblade) loads: Battlemagic 0 XP, paid = its level 0, the others intact")
    Sto.DATA.clear()
    r = Sto.addK(k, u, None, 19, 5000)
    dd = Sto.data(u)
    K.check(int(dd[19]) == 5000 and int(r[2]) == 5000, "SB XP into slot 19 (SkillStore.addK - the store step of every kill / party award)")
    p = Sto.snap(k)
    K.check(str(p.getProperty("Combat.Spellblade")) == "5000" and p.getProperty("Combat.Spellblade.paid") is not None, "SB saved as Combat.Spellblade (+ .paid)")
    open(os.path.join(pdir, k + ".properties"), "w").write("Combat.Spellblade=777\nCombat.Spellblade.paid=0\n")
    K.check(int(Sto.readFile(k, u)[0][19]) == 777, "SB Combat.Spellblade read back")
    # Overall Level: Battlemagic counts exactly like Divinity
    Cfg.FILE = Paths.get(os.path.join(scratch, "sbxp.properties"), Arr.newInstance(JString.class_, 0))
    K.notes.append("load: " + str(Cfg.load())[:200])
    tot = 1000
    while int(D.levelOf(19, tot)) < 10 and tot < 10 ** 12:
        tot *= 2
    K.check(int(D.levelOf(19, tot)) >= 10, "SB the class table reaches level 10 at %d XP" % tot)
    d1 = JClass("long[]")(40)
    d1[19] = tot
    d2 = JClass("long[]")(40)
    d2[15] = tot
    s1 = [int(x) for x in Ov.sums(u, d1)]
    br.put("class:" + str(u), "Priest")
    s2 = [int(x) for x in Ov.sums(u, d2)]
    br.put("class:" + str(u), "Spellblade")
    K.check(s1 == s2 and s1[0] >= int(D.levelOf(19, tot)), "SB Overall Level: Battlemagic level %d counts like Divinity (%s / %s)" % (int(D.levelOf(19, tot)), s1, s2))
    # bytecode: the kill and party paths take SkillClass.slot
    g = PW.calls(jar)
    has = lambda m, c: PKG + c in g.get(m, set())
    K.check(has("PartyXp.slotFor", "SkillClass.slot") and has("Perks.rowLevel", "SkillClass.slot"), "SB WIRE kill / party / perks route through SkillClass.slot")
    K.save()


def run_old(out, jar, scratch, _home):
    """the 0.4.42 jar (read only) on a file that has Combat.Spellblade"""
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, OLD_JAR], verify=True)
    Sto, D, Cfg = JClass(PKG + "SkillStore"), JClass(PKG + "SkillDefs"), JClass(PKG + "SkillCfg")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    _bridge()
    UUID = JClass("java.util.UUID")
    u = UUID.fromString("00000000-0000-4000-8000-0000000005b2")
    pdir = os.path.join(scratch, "oldplayers")
    os.makedirs(pdir, exist_ok=True)
    Paths, Arr = JClass("java.nio.file.Paths"), JClass("java.lang.reflect.Array")
    Sto.DIR = Paths.get(pdir, Arr.newInstance(JString.class_, 0))
    k = str(Sto.pkey(u))
    open(os.path.join(pdir, k + ".properties"), "w").write("Mining=1200\nCombat.Priest=1000\nCombat.Spellblade=5000\nCombat.Spellblade.paid=3\n")
    d = Sto.readFile(k, u)[0]
    K.check(int(D.N) == 19 and int(d[0]) == 1200 and int(d[15]) == 1000, "OLD 0.4.42 reads a 0.4.43 file without an error (known slots intact)")
    Sto.install(k, u, Sto.readFile(k, u))
    p = Sto.snap(k)
    dropped = p.getProperty("Combat.Spellblade") is None
    K.check(dropped, "OLD 0.4.42's save leaves Combat.Spellblade out (ROLLBACK FLOOR: Battlemagic XP is lost when a Spellblade plays on 0.4.42)")
    K.notes.append("rollback floor: 0.4.42 snap drops Combat.Spellblade = %s" % dropped)
    K.save()


# ============================================================================================ HP: base Health regen
def _fakes(out_dir):
    from jpype import JClass
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    CtField, CtNewMethod, CtNewConstructor = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    st_ = cp.makeClass("skyytest43.FakeStore")
    st_.setSuperclass(cp.get("com.hypixel.hytale.component.Store"))
    st_.addField(CtField.make("public com.hypixel.hytale.component.Resource time;", st_))
    st_.addConstructor(CtNewConstructor.make("public FakeStore() { super(null, 0, null, null); }", st_))
    st_.addMethod(CtNewMethod.make("public com.hypixel.hytale.component.Resource getResource(com.hypixel.hytale.component.ResourceType t) { return this.time; }", st_))
    st_.writeFile(out_dir)
    cb_ = cp.makeClass("skyytest43.FakeCB")
    cb_.setSuperclass(cp.get("com.hypixel.hytale.component.CommandBuffer"))
    for decl in ("stats", "dd", "death"):
        cb_.addField(CtField.make("public com.hypixel.hytale.component.Component %s;" % decl, cb_))
    for decl in ("statsType", "ddType", "deathType"):
        cb_.addField(CtField.make("public com.hypixel.hytale.component.ComponentType %s;" % decl, cb_))
    cb_.addMethod(CtNewMethod.make("""public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.ComponentType t) {
  if (t == this.statsType) return this.stats;
  if (t == this.ddType) return this.dd;
  if (t == this.deathType) return this.death;
  return null;
}""", cb_))
    cb_.writeFile(out_dir)
    sm_ = cp.makeClass("skyytest43.FakeStatMap")
    sm_.setSuperclass(cp.get("com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap"))
    for decl in ("int calls", "float added", "float last", "int lastIndex"):
        sm_.addField(CtField.make("public %s;" % decl, sm_))
    sm_.addMethod(CtNewMethod.make("""public float addStatValue(int i, float a) {
  this.calls = this.calls + 1;
  this.added = this.added + a;
  this.last = a;
  this.lastIndex = i;
  return a;
}""", sm_))
    sm_.writeFile(out_dir)


def run_hp(out, jar, scratch, _home):
    from jpype import JClass, JFloat, JArray, JInt
    K = HK.Child(out)
    fake = os.path.join(scratch, "hpfake")
    os.makedirs(fake, exist_ok=True)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, fake, jar], verify=True)
    _fakes(fake)
    J = lambda n: JClass(PKG + n)
    H, HF, Cfg = J("HpRegen"), J("HpRegenFn"), J("SkillCfg")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    br = _bridge()
    Props, UUID, Instant = JClass("java.util.Properties"), JClass("java.util.UUID"), JClass("java.time.Instant")
    near = lambda a, b, e=1e-4: abs(float(a) - float(b)) <= e
    # ---------------------------------------------------------------- CFG
    H.read(Props())
    K.check(bool(H.ON) and near(H.IN, 0.2) and near(H.OUT, 1.0) and int(H.COMBAT_MS) == 5000 and near(H.PL_IN, 0.02) and near(H.PL_OUT, 0.05),
            "HP CFG missing keys = 0.2 / 1 HP/s, 5 s, +0.02 / +0.05 per Overall Level")
    p = Props()
    for kk, vv in (("hp.regen.enabled", "false"), ("hp.regen.inCombat", "0.5"), ("hp.regen.outOfCombat", "2"), ("hp.regen.combatSeconds", "8"),
                   ("hp.regen.perLevel.inCombat", "0.1"), ("hp.regen.perLevel.outOfCombat", "0.2")):
        p.setProperty(kk, vv)
    H.read(p)
    K.check(not bool(H.ON) and near(H.IN, 0.5) and near(H.OUT, 2.0) and int(H.COMBAT_MS) == 8000 and near(H.PL_IN, 0.1) and near(H.PL_OUT, 0.2), "HP CFG the six keys are read")
    p = Props()
    for kk, vv in (("hp.regen.inCombat", "500"), ("hp.regen.outOfCombat", "-3"), ("hp.regen.combatSeconds", "abc"), ("hp.regen.perLevel.inCombat", "99")):
        p.setProperty(kk, vv)
    H.read(p)
    K.check(near(H.IN, 100.0) and near(H.OUT, 0.0) and int(H.COMBAT_MS) == 5000 and near(H.PL_IN, 10.0), "HP CFG clamps (500 -> 100, -3 -> 0, abc -> 5 s, 99 -> 10)")
    H.read(Props())
    # ---------------------------------------------------------------- RATE
    K.check(near(H.rate(True, 0, 0.0, 0.0), 0.2) and near(H.rate(False, 0, 0.0, 0.0), 1.0), "HP RATE level 0: 0.2 in combat, 1 out")
    K.check(near(H.rate(True, 50, 0.0, 0.0), 1.2) and near(H.rate(False, 50, 0.0, 0.0), 3.5), "HP RATE Overall Level 50: 1.2 / 3.5")
    K.check(near(H.rate(True, 100, 0.0, 0.0), 2.2) and near(H.rate(False, 100, 0.0, 0.0), 6.0), "HP RATE Overall Level 100: 2.2 / 6")
    K.check(near(H.rate(False, 0, 2.0, 0.0), 3.0) and near(H.rate(False, 0, 2.0, 50.0), 4.5) and near(H.rate(False, 0, 0.0, -100.0), 0.0)
            and near(H.rate(False, 0, -5.0, 0.0), 0.0) and near(H.rate(False, 0, 1e9, 0.0), 1000.0), "HP RATE flat / % sources, never below 0, at most 1000")
    H.ON = False
    K.check(near(H.rate(False, 50, 2.0, 0.0), 0.0), "HP RATE off = 0")
    H.ON = True
    # ---------------------------------------------------------------- AMOUNT
    K.check(near(H.amount(1.0, JFloat(0.5), JFloat(50.0), JFloat(100.0), False), 0.5), "HP AMOUNT 1 HP/s x 0.5 s = 0.5")
    K.check(near(H.amount(6.0, JFloat(1.0), JFloat(99.0), JFloat(100.0), False), 1.0), "HP AMOUNT never above max (the room left)")
    K.check(near(H.amount(6.0, JFloat(1.0), JFloat(100.0), JFloat(100.0), False), 0.0) and near(H.amount(6.0, JFloat(1.0), JFloat(0.0), JFloat(100.0), False), 0.0)
            and near(H.amount(6.0, JFloat(1.0), JFloat(40.0), JFloat(100.0), True), 0.0) and near(H.amount(6.0, JFloat(1.0), JFloat(0.0), JFloat(0.0), False), 0.0),
            "HP AMOUNT nothing at full Health, at 0 Health, while dead or without a pool")
    # ---------------------------------------------------------------- COMBAT TIMING (the world clock)
    now = Instant.parse("2026-10-15T12:00:00Z")
    K.check(bool(H.fighting(H.sinceFight(now.minusMillis(4999), None, now), H.COMBAT_MS)) and not bool(H.fighting(H.sinceFight(now.minusMillis(5000), None, now), H.COMBAT_MS)),
            "HP TIMING hurt 4.999 s ago = in combat, 5 s = out")
    K.check(bool(H.fighting(H.sinceFight(now.minusSeconds(30), now.minusSeconds(2), now), H.COMBAT_MS)), "HP TIMING hitting a monster 2 s ago (lastCombatAction) = in combat")
    K.check(int(H.sinceFight(Instant.MIN, None, now)) == -1 and int(H.sinceFight(now.plusSeconds(3), None, now)) == -1 and not bool(H.fighting(-1, 5000)),
            "HP TIMING never hit (Instant.MIN) / a future stamp = out of combat")
    # ---------------------------------------------------------------- TICK (the REAL HpRegen.tick on stand-ins)
    U_ = JClass("sun.misc.Unsafe")
    uf = U_.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)
    Mod = JClass("java.lang.reflect.Modifier")

    def setf(obj, cls, name, val):
        f = HK_jf(cls.class_, name)
        f.set(obj, val)

    def HK_jf(c, name):
        while c is not None:
            try:
                f = c.getDeclaredField(name)
                f.setAccessible(True)
                return f
            except Exception:
                c = c.getSuperclass()
        raise KeyError(name)
    EM = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
    DM = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DamageModule")
    SM = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatsModule")
    TM = JClass("com.hypixel.hytale.server.core.modules.time.TimeModule")
    CT, RT = JClass("com.hypixel.hytale.component.ComponentType"), JClass("com.hypixel.hytale.component.ResourceType")
    ddT, deT, stT, tiT = U.allocateInstance(CT.class_), U.allocateInstance(CT.class_), U.allocateInstance(CT.class_), U.allocateInstance(RT.class_)
    for cls, fname, val in ((EM, "damageDataComponentType", ddT), (DM, "deathComponentType", deT), (SM, "entityStatMapComponentType", stT), (TM, "timeResourceType", tiT)):
        inst = U.allocateInstance(cls.class_)
        for f in cls.class_.getDeclaredFields():
            if Mod.isStatic(f.getModifiers()) and f.getType() == cls.class_:
                f.setAccessible(True)
                f.set(None, inst)
        setf(inst, cls, fname, val)
    DST = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes")
    hi = int(DST.getHealth())
    K.notes.append("DefaultEntityStatTypes.getHealth() in a bare JVM = %d" % hi)
    TR = JClass("com.hypixel.hytale.server.core.modules.time.TimeResource")
    ESV = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue")
    ESM = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap")
    RGV = JClass("com.hypixel.hytale.server.core.modules.entitystats.RegeneratingValue")
    DDC = JClass("com.hypixel.hytale.server.core.entity.damage.DamageDataComponent")
    DTH = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent")
    tr = TR(now)
    store = U.allocateInstance(JClass("skyytest43.FakeStore").class_)
    store.time = tr
    hv = U.allocateInstance(ESV.class_)
    for name, val in (("id", "Health"), ("index", JInt(max(hi, 0))), ("value", JFloat(50.0)), ("min", JFloat(0.0)), ("max", JFloat(100.0)),
                      ("regeneratingValues", JArray(RGV)([]))):
        setf(hv, ESV, name, val)
    fsm = U.allocateInstance(JClass("skyytest43.FakeStatMap").class_)
    setf(fsm, ESM, "values", JArray(ESV)([hv] * (max(hi, 0) + 1)))
    dd = DDC()
    cb = U.allocateInstance(JClass("skyytest43.FakeCB").class_)
    cb.stats, cb.dd, cb.statsType, cb.ddType, cb.deathType = fsm, dd, stT, ddT, deT
    u = UUID.fromString("00000000-0000-4000-8000-0000000004e1")
    br.put("skill:overall:" + str(u), JClass("java.lang.Integer")(50))

    def val(v):
        setf(hv, ESV, "value", JFloat(v))

    def pulse(dt=0.5):
        c0 = int(fsm.calls)
        a0 = float(fsm.added)
        H.tick(u, store, cb, None, JFloat(dt))
        return int(fsm.calls) - c0, float(fsm.added) - a0
    dd.setLastDamageTime(now.minusSeconds(1))
    n1 = pulse(0.25)
    n2 = pulse(0.25)
    K.check(n1 == (0, 0.0) and n2[0] == 1 and near(n2[1], 0.6, 1e-3) and int(fsm.lastIndex) == max(hi, 0),
            "HP TICK one pulse per 0.5 s; hurt 1 s ago at Overall Level 50: 1.2 HP/s x 0.5 s = 0.6 onto the Health stat (%s, %s)" % (n1, n2))
    st = H.STATE.get(u)
    K.check(st is not None and float(st[0]) == 1.0 and near(st[1], 1.2), "HP TICK state: in combat, 1.2/s")
    dd.setLastDamageTime(now.minusSeconds(6))
    n3 = pulse()
    K.check(n3[0] == 1 and near(n3[1], 1.75, 1e-3), "HP TICK 6 s after the hit: 3.5 HP/s x 0.5 s = 1.75 (%s)" % (n3,))
    dd.setLastCombatAction(now.minusSeconds(2))
    n4 = pulse()
    K.check(near(n4[1], 0.6, 1e-3), "HP TICK hitting a monster 2 s ago = in combat again (0.6)")
    dd.setLastCombatAction(now.minusSeconds(60))
    val(99.5)
    n5 = pulse()
    K.check(near(n5[1], 0.5, 1e-3), "HP TICK capped at max (99.5 / 100 -> +0.5)")
    val(100.0)
    K.check(pulse()[0] == 0, "HP TICK full Health: nothing")
    val(0.0)
    K.check(pulse()[0] == 0, "HP TICK Health 0 (dead): nothing")
    val(40.0)
    cb.death = U.allocateInstance(DTH.class_)
    K.check(pulse()[0] == 0, "HP TICK DeathComponent on the player: nothing")
    cb.death = None
    H.ON = False
    K.check(pulse()[0] == 0 and not H.STATE.containsKey(u), "HP TICK hp.regen.enabled false: nothing")
    H.ON = True
    n6 = pulse(3.0)
    K.check(near(n6[1], 3.5, 1e-3), "HP TICK a long gap counts at most 1 s (3.5)")
    br.remove("skill:overall:" + str(u))
    K.check(near(pulse()[1], 0.5, 1e-3), "HP TICK no Overall Level published = the base 1 HP/s")
    br.put("skill:overall:" + str(u), JClass("java.lang.Integer")(50))
    # ---------------------------------------------------------------- BRIDGE skill:fn:hpregen
    fn = HF()
    Obj = JClass("java.lang.Object")
    Dbl, Int, Bool = JClass("java.lang.Double"), JClass("java.lang.Integer"), JClass("java.lang.Boolean")
    A = lambda *xs: JArray(Obj)(list(xs))
    g0 = fn.apply(A("get", u))
    K.check(near(g0[0], 1.2) and near(g0[1], 3.5), "HP BRIDGE get = {1.2 in combat, 3.5 out} at Overall Level 50")
    K.check(bool(fn.apply(A("add", u, "gear", Dbl(2.0)))) and bool(fn.apply(A("addpct", u, "trees", Dbl(50.0)))), "HP BRIDGE add (flat) + addpct")
    g1 = fn.apply(A("get", u))
    K.check(near(g1[0], (1.2 + 2) * 1.5) and near(g1[1], (3.5 + 2) * 1.5), "HP BRIDGE flat then %% on the whole regen: %s" % [float(x) for x in g1])
    srcs = [str(x) for x in fn.apply(A("sources", u))]
    K.check(srcs == ["gear=+2/s", "trees=+50%"], "HP BRIDGE sources sorted: %s" % srcs)
    K.check(near(pulse()[1], 5.5 * 1.5 * 0.5, 1e-3), "HP BRIDGE the tick applies the sources")
    K.check(not bool(fn.apply(A("add", u, "", Dbl(1.0)))) and not bool(fn.apply(A("add", u, "x", "1"))) and not bool(fn.apply(A("add", None, "x", Dbl(1.0))))
            and fn.apply(A("nope", u)) is None and fn.apply("x") is None, "HP BRIDGE bad arguments: FALSE / null, never a throw")
    row = [str(x) for x in fn.apply(A("row", u))]
    K.check(len(row) == 2 and row[0] == "8.25/s" and len(row[1]) <= 60 and "in combat" in row[1] and "Overall Lv 50" in row[1], "HP ROW Stats row %s" % row)
    for i in range(12):
        fn.apply(A("add", u, "src%02d" % i, Dbl(0.1)))
    row2 = [str(x) for x in fn.apply(A("row", u))]
    K.check(len(row2[1]) <= 60 and "more" in row2[1], "HP ROW many sources: '+N more', <= 60 characters: %s" % row2)
    sa = [str(x) for x in H.showAction(u, "Skyy")]
    K.check(sa[0] == "ok" and len(sa[2]) <= 120 and sa[2].startswith("Health Regen "), "HP SHOW %s" % sa[2])
    K.check(int(fn.apply(A("clear", "gear"))) == 1 and bool(fn.apply(A("remove", u, "trees"))) and not bool(fn.apply(A("remove", u, "trees"))),
            "HP BRIDGE clear (1 player) / remove (TRUE once)")
    for i in range(12):
        fn.apply(A("add", u, "src%02d" % i, Dbl(0.0)))
    g2 = fn.apply(A("get", u))
    K.check(near(g2[1], 3.5), "HP BRIDGE 0 removes a source (back to 3.5)")
    nowv = fn.apply(A("now", u))
    fight = fn.apply(A("fight", u))
    K.check(float(nowv) >= 0.0 and fight is not None, "HP BRIDGE now / fight answer (%s, %s)" % (nowv, fight))
    online = JClass("java.util.HashSet")()
    H.retain(online)
    K.check(H.CLK.isEmpty() and H.STATE.isEmpty(), "HP retain(online) drops players who left")
    # ---------------------------------------------------------------- WIRE
    g = PW.calls(jar)
    has = lambda m, c: PKG + c in g.get(m, set())
    K.check(has("AcroSys.tick", "ManaRegen.tick") and has("AcroSys.tick", "HpRegen.tick"), "WIRE AcroSys.tick -> ManaRegen.tick + HpRegen.tick")
    ht = g.get("HpRegen.tick", set())
    K.check("com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap.addStatValue" in ht
            and "com.hypixel.hytale.server.core.entity.damage.DamageDataComponent.getLastDamageTime" in ht
            and "com.hypixel.hytale.server.core.entity.damage.DamageDataComponent.getLastCombatAction" in ht
            and "com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent.getComponentType" in ht, "WIRE HpRegen.tick: Health stat, both combat stamps, DeathComponent")
    K.check(has("SkillCfg.load", "HpRegen.read") and has("SkillCfg.load", "XpEven.read") and has("Acro.retainOnline", "HpRegen.retain"), "WIRE SkillCfg.load -> read; retainOnline -> retain")
    z = zipfile.ZipFile(jar)
    plug = z.read("com/skyy/skills/SkyySkillsPlugin.class")
    K.check(b"skill:fn:hpregen" in plug, "WIRE the plugin publishes / removes skill:fn:hpregen")
    cfgc = b"".join(z.read(n) for n in z.namelist() if n.startswith("com/skyy/skills/SkillCfg") and n.endswith(".class"))
    K.check(b"hp.regen.outOfCombat=1" in cfgc and b"mining.xpMultiplier=1.25" in cfgc and b"fell.otherLogsPercent=70" in cfgc, "WIRE the fresh xp.properties lists the 0.4.43 block")
    K.save()


# ============================================================================================ EV: Mining vs Foraging
def run_ev(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    X, Cfg = JClass(PKG + "XpEven"), JClass(PKG + "SkillCfg")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    Props = JClass("java.util.Properties")
    X.read(Props())
    K.check(abs(float(X.FELL_PCT) - 70.0) < 1e-9 and abs(float(X.MINE) - 1.25) < 1e-9, "EV CFG defaults 70 %% / x1.25")
    K.check(int(X.pay(1.25, 0.2)) == 2 and int(X.pay(1.25, 0.25)) == 1 and int(X.pay(5.0, 0.999)) == 5 and int(X.pay(4.2, 0.1)) == 5
            and int(X.pay(4.2, 0.5)) == 4 and int(X.pay(0.0, 0.0)) == 0 and int(X.pay(-3.0, 0.0)) == 0, "EV pay: the whole part + 1 when r < the fraction")
    n = 40000
    m = sum(int(X.mine(1)) for _ in range(n)) / float(n)
    f = sum(int(X.fellLog(6.0)) for _ in range(n)) / float(n)
    K.check(abs(m - 1.25) < 0.02 and abs(f - 4.2) < 0.03, "EV averages: a 1 XP stone x1.25 = %.3f, a 6 XP felled log at 70 %% = %.3f" % (m, f))
    K.check(int(X.mine(8)) == 10, "EV Iron ore 8 x 1.25 = exactly 10")
    p = Props()
    p.setProperty("fell.otherLogsPercent", "100")
    p.setProperty("mining.xpMultiplier", "1")
    X.read(p)
    K.check(all(int(X.fellLog(6.0)) == 6 for _ in range(200)) and all(int(X.mine(1)) == 1 for _ in range(200)), "EV 100 %% / x1 = exactly the old XP")
    p.setProperty("fell.otherLogsPercent", "900")
    p.setProperty("mining.xpMultiplier", "abc")
    X.read(p)
    K.check(abs(float(X.FELL_PCT) - 500.0) < 1e-9 and abs(float(X.MINE) - 1.25) < 1e-9, "EV CFG clamps (900 -> 500, abc -> 1.25)")
    X.read(Props())
    g = PW.calls(jar)
    has = lambda mm, c: PKG + c in g.get(mm, set())
    K.check(has("BreakTask.run", "XpEven.mine") and has("FellCredit.one", "XpEven.fellLog"), "EV WIRE BreakTask.run -> XpEven.mine (Mining only), FellCredit.one -> XpEven.fellLog (logs, not leaves)")
    K.check(not has("BreakTask.run", "XpEven.fellLog") and not has("FellCredit.one", "XpEven.mine"), "EV WIRE the chopped log (BreakTask) keeps full XP")
    K.notes.append("XpEven %s" % X.text())
    K.save()


# 0.4.42's phases on this jar: the checks pinning the older row / slot counts - with why
EXPECTED43 = [
    ("G ROWS: the Sounds category, 249 rows (241 + 8)", "0.4.43: 261 rows (+ 6 hp.regen.*, fell.otherLogsPercent, mining.xpMultiplier, hp.regen.show)"),
    ("G facts: exactly two new keys, every 0.4.37 fact unchanged", "0.4.43: + x.Combat.Spellblade - Battlemagic is a class skill and a rebirth "
     "resets it like Combat.Priest (every slot but Exploration); SB checks the slot, the 0.4.37 facts are listed unchanged"),
    ("G1 SkillDefs: N 19, slots 16-18 Fishing / Ranching / Orchard", "0.4.43: N 20 (+ slot 19 Battlemagic); SB checks slots 0-18 unchanged"),
]
T42.T41.EXPECTED41.extend(EXPECTED43)


def wrap43(fn):
    def run(out, jar, scratch, home):
        tmp = out + ".i43.json"
        fn(tmp, jar, scratch, home)
        d = json.load(open(tmp))
        K = HK.Child(out)
        K.ok, K.notes = d["ok"], d["notes"]
        for f in d["fails"]:
            hit = [e for e in EXPECTED43 if f.startswith(e[0])]
            if hit:
                K.ok += 1
                K.notes.append("expected in 0.4.43 (%s): %s" % (hit[0][1], f[:160]))
            else:
                K.fails.append(f)
        K.save()
    return run


if __name__ == "__main__":
    phases = [("sb", run_sb), ("old42", run_old), ("hp", run_hp), ("ev", run_ev)]
    if "--no-old" not in sys.argv:
        phases += [("fort", wrap43(T42.run_fort)), ("hub", wrap43(T42.T41.run_hub))] + [(k, wrap43(T42.T41.wrap41(f))) for k, f in T42.T41.OLD_PHASES]
    try:
        HK.run(name="SkyySkills", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
               phases=phases, script=__file__, live=(LIVE_DIR, "Skyy_SkyySkills"))
    finally:
        if "--phase" not in sys.argv and os.path.isdir(T42.OLD_DIR):
            import shutil
            shutil.rmtree(T42.OLD_DIR, ignore_errors=True)
