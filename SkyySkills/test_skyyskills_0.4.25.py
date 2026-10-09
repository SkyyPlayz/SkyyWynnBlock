"""SkyySkills 0.4.25 - bare-JVM harness for THE CLASS POWER SPLIT + SKILL STAT PERKS (tools/skills_0_4_25_patch.py; Skyy 2026-10-08,
research/Class-Power-Split.md). Every new code path runs on the REAL classes of the 0.4.25 jar (HytaleServer.jar on the class path, -Xverify:all,
-XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in the scratch folder); the live save data is only ever READ and copied into scratch.

    python SkyySkills/test_skyyskills_0.4.25.py [--jar <SkyySkills-0.4.25.jar>] [--prev <SkyySkills-0.4.24.jar>] [--dir <scratch>]
                                                [--live <Skyy_SkyySkills folder>] [--keep]

SECTIONS
  A   every class of both jars loads under -Xverify:all
  J   the jar's asset files = 0.4.24's (only manifest.json differs: Version / Name / Description)
  MG  PerkMig.plan / sameAfter on texts: the live file, CRLF, hand-edited values kept, a marker = nothing, the 0.4.25 default file = nothing,
      group gates (no perk.* / no overall.enabled / an emptied class Mana table), a class in another spelling, a multi-line value, 0.050
  M   START TWICE on a scratch copy of the live data (the plugin's setup() data steps, both jars): 0.4.25 start 1 = 0.4.24's file + exactly
      the planned rewrites + the appended block, History snapshot + change-log lines; start 2 changes nothing; player files never touched
  P   THE STAT POOLS on REAL EntityStatMaps through the REAL Perks.tick / Perks.ovl: every class at class level 0 / 25 / 50 / 100 (Health,
      Mana, Stamina, Defense, Mana regen %) = the spec maths; a second tick writes nothing new; class switch and profile switch replace the
      pools (never stack); the session hold; Mining 100 = +20 Stamina, Foraging 100 = +20 Defense and +0 Health; the Stats page lines
  D   SKILL DEFENSE: SkillDef.factor = SkyyGear's formula summed (random cases vs scale / (scale + G + S)), gear Defense from gear:stats +
      gear:extra, SkyyGear's settings over a stand-in config:fn:SkyyGear, SkillDef.reduce on real Damage events, the REAL DefSys.handle (player
      victim, not a player, cancelled, no entity source), DefSys(true) AFTER ArmorDamageReduction, DefSysU unordered
  H   MANA ON HIT: grant (cap), offer (cooldown, PvP switch, casters 0), hit (wrong weapon, no class, no SkyyClasses), the REAL ManaHitSys.handle
      (landed hit, cancelled, 0 damage, self hit, PvP), ManaHit.apply on a real EntityStatMap (never above max, dead = dropped), the Mana Regen
      sources, the REAL CombatDmgSys.handle with the class balance damage %
  F   class compare 0.4.24 -> 0.4.25 method by method: only the planned classes changed, the 8 new classes added
  AU  the engine-access audit (every bytecode reference looked up with the JVM's own access rules; control refused)
"""
import os, sys, re, json, shutil, subprocess, zipfile, importlib.util, random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, PREV_VERSION = "0.4.25", "0.4.24"
PKG = "com.skyy.skills."
CLS = ["Archer", "Warrior", "Assassin", "Monk", "Mage", "Berserker", "Priest"]
SAVED = {"Archer": "Combat.Archer", "Warrior": "Combat.Warrior", "Assassin": "Combat.Assassin", "Monk": "Combat.Shaman", "Mage": "Combat.Mage",
         "Berserker": "Combat.Berserker", "Priest": "Combat.Priest"}
# research/Class-Power-Split.md: base Mana, base Stamina bonus, Mana per level, Stamina per level
SPEC = {"Mage": (45, 4, 10, 0.05), "Priest": (42, 5, 5, 0.06), "Spellblade": (33, 7, 4, 0.09), "Archer": (24, 9, 2, 0.12),
        "Assassin": (24, 9, 2, 0.12), "Monk": (21, 10, 2, 0.13), "Warrior": (21, 10, 2, 0.13), "Berserker": (12, 12, 2, 0.16)}
BOOST = {"Archer": (12, 15, 5, 13, 2, 15), "Warrior": (3, 13, 5, 3, 5, 13), "Assassin": (13, 12, 5, 15, 2, 12), "Monk": (10, 12, 5, 10, 2, 12),
         "Mage": (15, 3, 13, 15, 2, 3), "Berserker": (5, 13, 3, 8, 2, 13), "Priest": (12, 3, 12, 12, 5, 3), "Spellblade": (8, 8, 8, 8, 2, 8)}
HIT = {"Archer": 1, "Warrior": 1, "Assassin": 1, "Monk": 1, "Mage": 0, "Berserker": 1, "Priest": 0}
LEVELS = [0, 25, 50, 100]


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "perks25", "skills0425")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
PREV_JAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyySkills-%s.jar" % PREV_VERSION)))
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
LIVE_DIR = os.path.abspath(arg("--live", os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyySkills")))
KEEP = "--keep" in sys.argv
FAILS, OKS, GUARD_OK = [], [0], [False]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def tmod(fn, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.SCRATCH = SCRATCH
    return m


def t15():
    return tmod("test_skyyskills_0.4.15.py", "t0415")


def t20():
    return tmod("test_skyyskills_0.4.20.py", "t0420")


def r2(x):
    return round(x + 1e-9, 2)


# ============================================================================================ child: the extra stand-in (CompCB)
def run_mkfake25(out_dir):
    """skyytest25.CompCB: a CommandBuffer answering getComponent per Ref / ComponentType from a map (the attacker's PlayerRef and hotbar
    for the REAL ManaHitSys / CombatDmgSys / weaponOk); created with Unsafe.allocateInstance"""
    import jpype
    from jpype import JClass
    import skyybuild as B
    jpype.startJVM(B._jvm(), "-XX:-UsePerfData", classpath=[B.JAVASSIST], convertStrings=True)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    CtField, CtNewMethod, CtNewConstructor = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    c = cp.makeClass("skyytest25.CompCB")
    c.setSuperclass(cp.get("com.hypixel.hytale.component.CommandBuffer"))
    c.addField(CtField.make("public java.util.Map comps;", c))
    c.addConstructor(CtNewConstructor.make("public CompCB() { super(null); }", c))
    c.addMethod(CtNewMethod.make("""public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.ComponentType t) {
  if (this.comps == null || r == null) return null;
  java.util.Map m = (java.util.Map) this.comps.get(r);
  return m == null ? null : (com.hypixel.hytale.component.Component) m.get(t);
}""", c))
    c.writeFile(out_dir)


# ============================================================================================ child: -Xverify:all load (one jar)
def run_child(jar, out):
    T = t15()
    res, path = T.common(jar, [])
    json.dump({"loaded": res["loaded"], "classes": res["classes"], "load_fails": res["load_fails"]}, open(out, "w"), indent=1)


# ============================================================================================ child: START TWICE on a live copy (one jar)
def run_start(jar, out, mode):
    from jpype import JClass
    T = t15()
    res, path = T.common(jar, [])
    R = {"load_fails": res["load_fails"]}
    Cfg, Store, Hist, CLog, Rows = (JClass(PKG + "SkillCfg"), JClass(PKG + "SkillStore"), JClass(PKG + "CfgHist"), JClass(PKG + "CfgLog"),
                                    JClass(PKG + "CfgRows"))
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    lc = os.path.join(SCRATCH, "live-copy-" + mode)
    migs = ["ManaMig", "HealMig", "DocMig", "ClassManaMig", "SkillLvMig", "KillXpMig", "AcroMig"] + (["PerkMig"] if mode == "new" else [])

    def snap(d):
        return dict((os.path.relpath(os.path.join(r, fn), d).replace(os.sep, "/"), open(os.path.join(r, fn), "rb").read())
                    for r, ds, fs in os.walk(d) for fn in fs)

    def start():
        Cfg.FILE = path(os.path.join(lc, "xp.properties"))
        Store.DATA.clear()
        Store.DIRTY.clear()
        Store.DIR = path(os.path.join(lc, "players"))
        Hist.DIR = None
        Rows.HOME = None
        CLog.FILE = None
        CLog.Q.clear()
        r = {}
        for nm in migs:
            v = JClass(PKG + nm).run()
            r[nm] = [str(x) for x in v] if nm == "ManaMig" else str(v)
        r["load"] = str(Cfg.load())
        r["curve"] = str(JClass(PKG + "ClassCurve").start(path(lc)))
        r["own"] = str(JClass(PKG + "OwnCurve").start(path(lc)))
        return r
    try:
        s0 = snap(lc)
        R["r1"] = start()
        s1 = snap(lc)
        R["r2"] = start()
        s2 = snap(lc)
        R["files"] = len(s0)
        R["changed1"] = sorted(k for k in set(s0) | set(s1) if s0.get(k) != s1.get(k))
        R["changed2"] = sorted(k for k in set(s1) | set(s2) if s1.get(k) != s2.get(k))
        R["xp0"] = s0.get("xp.properties", b"").decode("latin-1")
        R["xp1"] = s1.get("xp.properties", b"").decode("latin-1")
        R["log1"] = s1.get("config-changes.log", b"").decode("latin-1")
        R["log0"] = s0.get("config-changes.log", b"").decode("latin-1")
        R["hist_new"] = sorted(k for k in set(s1) - set(s0) if k.startswith("config-history/"))
        R["hist_new_bytes_eq"] = [s1[k] == s0.get("xp.properties") for k in R["hist_new"]]
        R["players"] = len([k for k in s0 if k.startswith("players/")])
        R["players_same"] = all(s0.get(k) == s1.get(k) == s2.get(k) for k in set(s0) | set(s1) | set(s2) if k.startswith("players/"))
        if mode == "new":
            CP, MH = JClass(PKG + "ClassPower"), JClass(PKG + "ManaHit")
            OC, CM = JClass(PKG + "OverallCfg"), JClass(PKG + "ClassMana")
            R["after"] = {"base": float(OC.BASE), "classBase": str(OC.tableText()), "classPer": str(CM.tableText()),
                          "inCombat": int(JClass(PKG + "ManaRegen").IN_COMBAT), "cp": str(CP.text()), "mh": str(MH.text()),
                          "sta": [float(x) for x in JClass(PKG + "PerkCfg").STA], "hp": [float(x) for x in JClass(PKG + "PerkCfg").HP],
                          "def": [float(x) for x in JClass(PKG + "PerkCfg").DEF]}
    except Exception:
        import traceback
        R["error"] = traceback.format_exc()[-3000:]
    json.dump(R, open(out, "w"), indent=1)


# ============================================================================================ child: the behaviour (new jar)
def run_unit(jar, fake, out, live_xp):
    from jpype import JClass, JFloat, JArray, JInt, JLong, JImplements, JOverride, JObject
    T = t15()
    res, path = T.common(jar, [fake])
    R = {"load_fails": res["load_fails"]}
    if res["load_fails"]:
        json.dump(R, open(out, "w"), indent=1)
        return
    E = T.regen_env()
    U = E["U"]
    Mod = JClass("java.lang.reflect.Modifier")

    def findf(c, name):
        while c is not None:
            for f in c.getDeclaredFields():
                if str(f.getName()) == name:
                    f.setAccessible(True)
                    return f
            c = c.getSuperclass()
        raise RuntimeError("no field " + name)

    def setany(obj, name, val):
        findf(obj.getClass(), name).set(obj, val)

    def setstatic(cls, name, val):
        findf(cls.class_, name).set(None, val)

    def alloc(cls):
        return U.allocateInstance(cls.class_)

    J = lambda n: JClass(PKG + n)
    Cfg, Store, Defs, Perks, Ovl = J("SkillCfg"), J("SkillStore"), J("SkillDefs"), J("Perks"), J("Overall")
    CPw, MHit, SDef, PMig, CTb, MReg = J("ClassPower"), J("ManaHit"), J("SkillDef"), J("PerkMig"), J("ClassTbl"), J("ManaRegen")
    OCfg, CMan, PCfg, SPg = J("OverallCfg"), J("ClassMana"), J("PerkCfg"), J("StatsPage")
    DefSys, DefSysU, MHS, CDS = J("DefSys"), J("DefSysU"), J("ManaHitSys"), J("CombatDmgSys")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    UUID, IHM, CHM = JClass("java.util.UUID"), JClass("java.util.IdentityHashMap"), JClass("java.util.concurrent.ConcurrentHashMap")
    JObj, JBool, JStr = JClass("java.lang.Object"), JClass("java.lang.Boolean"), JClass("java.lang.String")
    CT = JClass("com.hypixel.hytale.component.ComponentType")
    Ref = JClass("com.hypixel.hytale.component.Ref")
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    Universe = JClass("com.hypixel.hytale.server.core.universe.Universe")
    EMc = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
    ESM, ESV = E["ESM"], E["ESV"]
    EST = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType")
    DST = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes")
    ILT = JClass("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap")
    JAWM = JClass("com.hypixel.hytale.assetstore.map.JsonAssetWithMap")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    DMG = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage")
    DES = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage$EntitySource")
    MapStore, MapChunk, CompCB, FakeCB = JClass("skyytest.MapStore"), JClass("skyytest.MapChunk"), JClass("skyytest25.CompCB"), JClass("skyytest.FakeCB")
    FakeHotbar, FakeAS = JClass("skyytest.FakeHotbar"), JClass("skyytest.FakeAssetStore")
    bridge = Store.bridge()

    @JImplements("java.util.function.Function")
    class Const(object):
        def __init__(self, v):
            self.v = v

        @JOverride
        def apply(self, o):
            return self.v

    ACTIVE = {}

    @JImplements("java.util.function.Function")
    class PKey(object):
        @JOverride
        def apply(self, o):
            k = ACTIVE.get(str(o))
            return k if k is not None else str(o)

    GEARCFG = {"part.stats": "true", "combat.defScale": "100"}
    GEARCALLS = []

    @JImplements("java.util.function.Function")
    class GearFn(object):
        @JOverride
        def apply(self, o):
            GEARCALLS.append([str(x) for x in o])
            if str(o[0]) == "get":
                v = GEARCFG.get(str(o[1]))
                return None if v is None else JStr(v)
            return None

    # ---- engine statics: Universe + the PlayerRef type, the inventory / player component types, the stat types Health 0, Mana 1, Stamina 2
    uni = alloc(Universe)
    setstatic(Universe, "instance", uni)
    TPR = alloc(CT)
    setany(uni, "playerRefComponentType", TPR)
    em = EMc.get()
    TT = {}
    for fname in ("playerComponentType", "hotbarInventoryComponentType", "toolInventoryComponentType"):
        TT[fname] = alloc(CT)
        setany(em, fname, TT[fname])

    def fstore(amap):
        st = alloc(FakeAS)
        setany(st, "assetMap", amap)
        return st

    def stype(id_, mn, mx):
        t = alloc(EST)
        setany(t, "id", id_)
        setany(t, "min", JFloat(mn))
        setany(t, "max", JFloat(mx))
        return t
    amap = alloc(ILT)
    setany(amap, "array", JArray(JAWM)([stype("Health", 0.0, 100.0), stype("Mana", 0.0, 0.0), stype("Stamina", -4.0, 10.0)]))
    setstatic(EST, "ASSET_STORE", fstore(amap))
    for nm, ix in (("HEALTH", 0), ("MANA", 1), ("STAMINA", 2)):
        setstatic(DST, nm, JInt(ix))
    R["types"] = [int(DST.getHealth()), int(DST.getMana()), int(DST.getStamina()), float(Ovl.typeMax(2))]

    def statmap(mana_max=0.0, mana_val=None):
        m = ESM()
        vals = []
        for idx, nm, v, mn in ((0, "Health", 100.0, 0.0), (1, "Mana", mana_max, 0.0), (2, "Stamina", 10.0, -4.0)):
            sv = alloc(ESV)
            vv = v if not (idx == 1 and mana_val is not None) else mana_val
            for fn_, val in (("id", nm), ("index", JInt(idx)), ("value", JFloat(vv)), ("min", JFloat(mn)), ("max", JFloat(v))):
                setany(sv, fn_, val)
            vals.append(sv)
        setany(m, "values", JArray(ESV)(vals))
        return m

    def mods(m, i):
        mm = m.get(i).getModifiers()
        if mm is None:
            return {}
        return dict((str(k), round(float(mm.get(k).getAmount()), 4)) for k in mm.keySet())

    def maxes(m):
        return [round(float(m.get(i).getMax()), 4) for i in range(3)]

    def mkpr(u, name):
        pr = alloc(PRef)
        setany(pr, "uuid", u)
        setany(pr, "username", name)
        return pr

    def fakecb(m):
        cb = alloc(FakeCB)
        cb.stats, cb.statsType, cb.dd, cb.ddType = m, E["statsType"], None, E["ddType"]
        cb.arch = E["Arch"].empty()
        return cb

    # ---- config: a fresh xp.properties = the 0.4.25 default file
    work = os.path.join(SCRATCH, "unit")
    os.makedirs(work, exist_ok=True)
    Cfg.FILE = path(os.path.join(work, "xp.properties"))
    R["load"] = str(Cfg.load())
    defaults = open(os.path.join(work, "xp.properties"), "rb").read().decode("latin-1")
    pdir = os.path.join(work, "players")
    os.makedirs(pdir, exist_ok=True)
    Store.DIR = path(pdir)
    Store.DATA.clear()
    bridge.put("class:fn:allowed", Const(JBool.TRUE))
    bridge.put("class:weapons:Warrior", "Weapon_Sword_,Weapon_Longsword_,Weapon_Spear_")
    bridge.put("class:weapons:Mage", "Weapon_Staff_,Weapon_Spellbook_")
    bridge.put("class:weapons:Archer", "Weapon_Shortbow_,Weapon_Crossbow_,Weapon_Arrow_")
    R["tables"] = {"cp": str(CPw.text()), "mh": str(MHit.text()), "base": float(OCfg.BASE), "cbase": str(OCfg.tableText()), "cper": str(CMan.tableText())}
    ECUM = [int(x) for x in Defs.ECUM]

    def player(key, lines):
        open(os.path.join(pdir, key + ".properties"), "wb").write(("name=T\n" + "".join("%s=%d\n" % kv for kv in lines)).encode("latin-1"))

    def set_class(u, cls):
        for k in ("profile:class:", "class:"):
            if cls is None:
                bridge.remove(k + str(u))
            else:
                bridge.put(k + str(u), cls)

    # ================================================================ MG: PerkMig.plan
    MG = {}
    try:
        live = open(live_xp, "rb").read().decode("latin-1")

        def plan(text):
            r = PMig.plan(text)
            if r is None:
                return None
            return {"text": str(r[0]), "rows": [str(x) for x in r[1]], "rw": [bool(x) for x in r[2]], "add": [bool(x) for x in r[3]], "kept": str(r[4]),
                    "same": bool(PMig.sameAfter(text.encode("latin-1"), str(r[0]).encode("latin-1"), r[2], r[3]))}
        MG["keys"] = {"rw": [str(x) for x in PMig.RW_KEY], "old": [str(x) for x in PMig.RW_OLD], "new": [str(x) for x in PMig.RW_NEW],
                      "add": [str(x) for x in PMig.ADD_KEY], "grp": [int(x) for x in PMig.ADD_GRP], "head": str(PMig.HEAD)}
        MG["live"] = plan(live)
        MG["live_crlf"] = plan(live.replace("\n", "\r\n"))
        hand = live.replace("perk.mining.staminaPerLevel=0.05", "perk.mining.staminaPerLevel=0.1").replace("\nmana.base=10\n", "\nmana.base=30\n")
        MG["hand"] = plan(hand)
        MG["marked"] = plan(live + "# x " + str(PMig.MARK_ID) + "\n")
        MG["defaults"] = plan(defaults)
        MG["bare"] = plan("multiplier=1.0\nmana.regen.inCombat=50\n")
        MG["lower"] = plan(live.replace("mana.classBase.Mage=30", "mana.classBase.mage=30\nmana.classBase.wArRiOr=50"))
        MG["multi"] = plan(live.replace("\nmana.base=10\n", "\nmana.base=1\\\n  0\n"))
        MG["zero"] = plan(live.replace("perk.mining.staminaPerLevel=0.05", "perk.mining.staminaPerLevel=0.050"))
        MG["noper"] = plan("\n".join(l for l in live.split("\n") if not l.startswith("mana.classPerLevel.")))
        MG["tamper"] = bool(PMig.sameAfter(live.encode("latin-1"), (MG["live"]["text"] + "extra=1\n").encode("latin-1"),
                                           JArray(JClass("boolean"))(MG["live"]["rw"]), JArray(JClass("boolean"))(MG["live"]["add"])))
        MG["numEq"] = [bool(PMig.numEq("0.050", "0.05")), bool(PMig.numEq(" 10 ", "10")), bool(PMig.numEq("abc", "10")), bool(PMig.numEq("10.5", "10"))]
    except Exception:
        import traceback
        MG["error"] = traceback.format_exc()[-3000:]
    R["MG"] = MG

    # ================================================================ P: the stat pools on real stat maps
    P = {}
    try:
        OCfg.ON = False                                            # the table leaves the Overall Level out (class part only)
        grid = []
        n = 0
        for cls in CLS:
            for lv in LEVELS:
                n += 1
                u = UUID(0x25A, n)
                player(str(u), [(SAVED[cls], ECUM[lv]), (SAVED[cls] + ".paid", lv)])
                set_class(u, cls)
                pr = mkpr(u, "G%d" % n)
                m = statmap()
                cb = fakecb(m)
                ref = Ref(alloc(MapStore), 0)
                Perks.tick(u, pr, cb, ref)
                k1 = [mods(m, i) for i in range(3)]
                Perks.tick(u, pr, cb, ref)
                k2 = [mods(m, i) for i in range(3)]
                grid.append({"cls": cls, "lv": lv, "level": int(Store.level(u, J("SkillClass").slotOfClass(cls))),
                             "max": maxes(m), "mods": k1, "same2": k1 == k2, "def": float(SDef.of(u)), "regen": float(MReg.total(u)),
                             "bdef": bridge.get("skill:def:" + str(u)) is not None and float(bridge.get("skill:def:" + str(u))) or 0.0,
                             "hit": float(MHit.perHit(cls)), "src": [str(x) for x in MReg.sources(u)]})
        P["grid"] = grid
        P["tick_failed"] = bool(Perks.FAILED_ONCE) or bool(Perks.OVL_FAILED_ONCE)
        # class switch on one entity / one profile: Warrior 50, Mage 50, Berserker 100 in one file
        u = UUID(0x25A, 900)
        player(str(u), [("Combat.Warrior", ECUM[50]), ("Combat.Mage", ECUM[50]), ("Combat.Berserker", ECUM[100])])
        pr = mkpr(u, "Switch")
        m = statmap()
        cb = fakecb(m)
        ref = Ref(alloc(MapStore), 0)
        sw = []
        for cls in ("Warrior", "Mage", "Berserker", "Warrior", None):
            set_class(u, cls)
            if cls is None:                                        # past the 10 s session hold (a classless player is computed normally)
                Ovl.SESS.put(u, JArray(JObj)([pr, JClass("java.lang.Long")(int(JClass("java.lang.System").currentTimeMillis()) - 11000)]))
            Perks.tick(u, pr, cb, ref)
            sw.append({"cls": cls, "max": maxes(m), "mods": [mods(m, i) for i in range(3)], "def": float(SDef.of(u))})
        P["switch"] = sw
        # profile switch: profile 1 = Warrior 50, profile 2 = Mage 100 (one PlayerRef, one entity)
        u = UUID(0x25A, 901)
        k1, k2 = str(u), str(u) + "-p2"
        player(k1, [("Combat.Warrior", ECUM[50])])
        player(k2, [("Combat.Mage", ECUM[100])])
        bridge.put("profile:fn:key", PKey())
        ACTIVE[str(u)] = k1
        pr = mkpr(u, "Prof")
        m = statmap()
        cb = fakecb(m)
        ref = Ref(alloc(MapStore), 0)
        ps = []
        set_class(u, "Warrior")
        Perks.tick(u, pr, cb, ref)
        ps.append({"step": "p1 Warrior 50", "max": maxes(m), "mods": [mods(m, i) for i in range(3)]})
        ACTIVE[str(u)] = k2
        set_class(u, "Mage")
        Perks.switched(u)
        Perks.tick(u, pr, cb, ref)
        ps.append({"step": "p2 Mage 100", "max": maxes(m), "mods": [mods(m, i) for i in range(3)]})
        ACTIVE[str(u)] = k1
        set_class(u, "Warrior")
        Perks.switched(u)
        Perks.tick(u, pr, cb, ref)
        ps.append({"step": "p1 again", "max": maxes(m), "mods": [mods(m, i) for i in range(3)]})
        P["profile"] = ps
        bridge.remove("profile:fn:key")
        ACTIVE.clear()
        # the session hold: a relog (new PlayerRef) with SkyyClasses loaded and no class yet keeps the saved pools
        u = UUID(0x25A, 902)
        player(str(u), [("Combat.Berserker", ECUM[100])])
        set_class(u, "Berserker")
        m = statmap()
        cb = fakecb(m)
        ref = Ref(alloc(MapStore), 0)
        Perks.tick(u, mkpr(u, "Hold"), cb, ref)
        h0 = [mods(m, i) for i in range(3)]
        set_class(u, None)
        Perks.tick(u, mkpr(u, "Hold"), cb, ref)
        P["hold"] = {"before": h0, "held": [mods(m, i) for i in range(3)]}
        # Mining 100 / Foraging 100 (gathering perks; no class)
        u = UUID(0x25A, 903)
        player(str(u), [("Mining", 10 ** 13), ("Foraging", 10 ** 13)])
        m = statmap()
        cb = fakecb(m)
        Perks.tick(u, mkpr(u, "Gath"), cb, Ref(alloc(MapStore), 0))
        P["gather"] = {"mining": int(Store.level(u, 0)), "foraging": int(Store.level(u, 1)), "mods": [mods(m, i) for i in range(3)], "max": maxes(m),
                       "def": float(SDef.of(u)), "bdef": str(bridge.get("skill:def:" + str(u)))}
        # the Stats page lines: Warrior Swordsmanship 50 (now / next), Mage Sorcery 100, Foraging 100, Mining 100
        uw = UUID(0x25A, 4)                                       # Archer? -> the grid order: Archer 0/25/50/100 = 1..4, Warrior 5..8
        lines = {}
        for tag, cls, lv in (("Warrior50", "Warrior", 50), ("Mage100", "Mage", 100), ("Archer100", "Archer", 100), ("Priest25", "Priest", 25)):
            uu = UUID(0x25A, CLS.index(cls) * 4 + LEVELS.index(lv) + 1)
            slot = int(J("SkillClass").slotOfClass(cls))
            lines[tag] = {"now": [str(x) for x in SPg.lines(uu, slot, lv, False)], "next": [str(x) for x in SPg.lines(uu, slot, lv, True)]}
        ug = UUID(0x25A, 903)
        lines["Foraging100"] = {"now": [str(x) for x in SPg.lines(ug, 1, 100, False)], "next": [str(x) for x in SPg.lines(ug, 1, 100, True)]}
        lines["Mining100"] = {"now": [str(x) for x in SPg.lines(ug, 0, 100, False)]}
        P["lines"] = lines
        # the admin /skills mana breakdown names the class balance Mana
        u = UUID(0x25A, 8)                                        # Warrior 100
        m = statmap()
        Perks.tick(u, mkpr(u, "Brk"), fakecb(m), Ref(alloc(MapStore), 0))
        P["breakdown"] = str(CMan.breakdown(u, m, 1, m.get(1).getMax()))
        # the switches: class Stamina off / class balance off remove the pools on the next second
        CPw.STA_ON = False
        CPw.B_ON = False
        Perks.tick(u, mkpr(u, "Brk"), fakecb(m), Ref(alloc(MapStore), 0))
        P["off"] = {"mods": [mods(m, i) for i in range(3)], "def": float(SDef.of(u)), "regen": float(MReg.total(u)), "dmg": float(CPw.boostDmg(6, 100))}
        CPw.STA_ON = True
        CPw.B_ON = True
        # a broken table snapshot: amounts() = null, the saved pools stay (no dip), logged once
        Perks.tick(u, mkpr(u, "Brk"), fakecb(m), Ref(alloc(MapStore), 0))
        good = CPw.T
        before = [mods(m, i) for i in range(3)]
        CPw.T = JArray(JObj)(["broken"] * 8)                      # not a table snapshot: amounts() throws -> null
        Perks.tick(u, mkpr(u, "Brk"), fakecb(m), Ref(alloc(MapStore), 0))
        P["fault"] = {"before": before, "after": [mods(m, i) for i in range(3)], "logged": bool(CPw.FAILED_ONCE)}
        CPw.T = good
        # table reader: Spellblade is a class, a junk entry is reported, values clamped
        from jpype import JClass as _JC
        Props = _JC("java.util.Properties")
        p = Props()
        for k_, v_ in (("stamina.classBase.Spellblade", "7"), ("stamina.classBase.Nope", "3"), ("stamina.classBase.mage", "5000"),
                       ("stamina.classBase.Monk", "abc"), ("stamina.classBase.Shaman", "4")):
            p.setProperty(k_, v_)
        tr = CTb.parse(p, "stamina.classBase.", 1000.0)
        P["parse"] = {"cls": [str(x) for x in tr[0]], "v": [float(x) for x in tr[1]], "text": str(tr[2]), "bad": str(tr[3])}
        P["check"] = [None if CTb.checkEntry("stamina.classBase[Spellblade]", "3") is None else "x", str(CTb.checkEntry("mana.onHit[Druid]", "1")),
                      None if OCfg.checkClassBase("mana.classBase[Spellblade]", "33") is None else "x"]
        P["spellblade"] = [float(OCfg.baseFor("Spellblade")), float(CMan.perLevel("Spellblade")), float(CPw.stamFor("Spellblade", 0)),
                           float(CPw.boost(2, "Spellblade", 100))]
        OCfg.ON = True
    except Exception:
        import traceback
        P["error"] = traceback.format_exc()[-3000:]
    R["P"] = P

    # ================================================================ D: skill Defense
    D = {}
    try:
        rnd = random.Random(4250)
        cases = []
        for _ in range(400):
            g = rnd.choice([0, 0, rnd.randint(-50, 400)])
            sk = rnd.choice([0.0, rnd.uniform(0.0, 300.0)])
            sc = rnd.choice([100.0, 100.0, rnd.uniform(1.0, 5000.0)])
            on = rnd.random() < 0.8
            f = float(SDef.factor(float(g), sk, sc, on))
            gear = (sc / (sc + g)) if (on and g > 0) else 1.0      # what SkyyGear's GearArmorSys did
            want = (sc / (sc + (g if on else 0) + sk)) if ((g if on else 0) + sk) > 0 and sk > 0 else gear
            cases.append([g, sk, sc, on, f, gear * f, want])
        D["cases"] = cases
        D["table"] = [[s_, round(float(SDef.factor(0.0, float(s_), 100.0, True)), 6)] for s_ in (0, 5, 10, 20, 40)]
        D["sum_g50_s20"] = [round(float(SDef.factor(50.0, 20.0, 100.0, True)), 6), round(100.0 / 150.0 * float(SDef.factor(50.0, 20.0, 100.0, True)), 6)]
        u = UUID(0x25D, 1)
        D["defOf"] = [float(SDef.defOf("str:5,def:12,cc:3")), float(SDef.defOf("def:2,def:3.9,def:x,junk")), float(SDef.defOf(None)), float(SDef.defOf("def:-5"))]
        bridge.put("gear:stats:" + str(u), "str:5,def:12")
        bridge.put("gear:extra:" + str(u), "cc:4,def:3")
        D["gearDef"] = float(SDef.gearDef(u))
        # SkyyGear's settings
        bridge.remove("config:fn:SkyyGear")
        SDef.GAT = JLong(0)
        SDef.gearCfg(JLong(1000))
        D["nofn"] = [bool(SDef.GFN), bool(SDef.GON), float(SDef.GSC)]
        bridge.put("config:fn:SkyyGear", GearFn())
        GEARCFG.update({"part.stats": "false", "combat.defScale": "250"})
        SDef.GAT = JLong(0)
        SDef.gearCfg(JLong(2000))
        D["fn"] = [bool(SDef.GFN), bool(SDef.GON), float(SDef.GSC)]
        GEARCFG.update({"part.stats": "true", "combat.defScale": "100"})
        SDef.gearCfg(JLong(3000))                                   # within 5 s: not re-read
        D["cached"] = [bool(SDef.GON), float(SDef.GSC)]
        SDef.gearCfg(JLong(8000))
        D["reread"] = [bool(SDef.GON), float(SDef.GSC), len(GEARCALLS)]
        GEARCFG.update({"combat.defScale": "junk"})
        SDef.GAT = JLong(0)
        SDef.gearCfg(JLong(9000))
        D["junk"] = float(SDef.GSC)
        GEARCFG.update({"combat.defScale": "100"})
        SDef.GAT = JLong(0)
        SDef.gearCfg(JLong(10000))
        # reduce on real Damage events
        st = alloc(MapStore)
        st.comps = IHM()
        vref, aref = Ref(st, 1), Ref(st, 2)

        def dmg(amount, src=True, att=None):
            return DMG(DES(att if att is not None else aref) if src else None, JInt(0), JFloat(amount))
        SDef.set(u, 20.0)
        D["published"] = [float(SDef.of(u)), str(bridge.get("skill:def:" + str(u)))]
        d1 = dmg(100.0)
        f1 = float(SDef.reduce(d1, u, JLong(10001)))
        D["reduce"] = [f1, float(d1.getAmount()), round(100.0 * 100.0 / 115.0, 4), round(100.0 * 100.0 / 135.0, 4)]   # gear 15 + skill 20
        d2 = dmg(100.0, src=False)
        D["nosrc"] = [float(SDef.reduce(d2, u, JLong(10002))), float(d2.getAmount())]
        d3 = dmg(100.0)
        d3.setCancelled(True)
        D["cancelled"] = [float(SDef.reduce(d3, u, JLong(10003))), float(d3.getAmount())]
        u0 = UUID(0x25D, 2)
        d4 = dmg(100.0)
        D["noskill"] = [float(SDef.reduce(d4, u0, JLong(10004))), float(d4.getAmount())]
        # the REAL DefSys.handle: a player victim (PlayerRef in the store) / an NPC victim (no PlayerRef)
        ds = DefSys(True)
        deps = ds.getDependencies()
        dl = [str(x.getClass().getSimpleName()) for x in deps]
        dord = [str(x) for x in deps]
        dcls = [str(x.getSystemClass().getName()) for x in deps]
        D["deps"] = {"n": int(deps.size()), "types": dl, "order": dord, "class": dcls, "u": int(DefSysU().getDependencies().size())}
        prv = mkpr(u, "Victim")
        st.comps.put(vref, IHM())
        st.comps.get(vref).put(TPR, prv)
        ch = alloc(MapChunk)
        ch.comps = IHM()
        ch.ref = vref
        d5 = dmg(100.0)
        ds.handle(JInt(0), ch, st, None, d5)
        nref = Ref(st, 3)
        ch2 = alloc(MapChunk)
        ch2.comps = IHM()
        ch2.ref = nref
        d6 = dmg(100.0)
        ds.handle(JInt(0), ch2, st, None, d6)
        d7 = dmg(100.0)
        DefSysU().handle(JInt(0), ch, st, None, d7)
        D["handle"] = [float(d5.getAmount()), float(d6.getAmount()), float(d7.getAmount()), bool(DefSys.FAILED_ONCE)]
        SDef.set(u, 0.0)
        D["unpublished"] = [float(SDef.of(u)), bridge.get("skill:def:" + str(u)) is None]
        SDef.set(u, 7.4)
        SDef.retain(JClass("java.util.HashSet")())
        D["retain"] = [float(SDef.of(u)), bridge.get("skill:def:" + str(u)) is None]
    except Exception:
        import traceback
        D["error"] = traceback.format_exc()[-3000:]
    R["D"] = D

    # ================================================================ H: Mana on hit
    H = {}
    try:
        H["grant"] = [float(MHit.grant(JFloat(10.0), JFloat(30.0), JFloat(1.0))), float(MHit.grant(JFloat(29.5), JFloat(30.0), JFloat(1.0))),
                      float(MHit.grant(JFloat(30.0), JFloat(30.0), JFloat(1.0))), float(MHit.grant(JFloat(0.0), JFloat(0.0), JFloat(1.0))),
                      float(MHit.grant(JFloat(5.0), JFloat(30.0), JFloat(0.0)))]
        u = UUID(0x25E, 1)
        MHit.forget(u)
        t0 = 1000000
        H["offer"] = [float(MHit.offer(u, "Warrior", False, JLong(t0))), float(MHit.offer(u, "Warrior", False, JLong(t0 + 100))),
                      float(MHit.offer(u, "Warrior", False, JLong(t0 + 499))), float(MHit.offer(u, "Warrior", False, JLong(t0 + 500))),
                      float(MHit.offer(u, "Warrior", True, JLong(t0 + 2000))), float(MHit.offer(u, "Mage", False, JLong(t0 + 3000))),
                      float(MHit.offer(u, "Priest", False, JLong(t0 + 4000)))]
        H["pend"] = float(MHit.PEND.get(u))
        MHit.PVP = True
        H["pvp_on"] = float(MHit.offer(u, "Warrior", True, JLong(t0 + 5000)))
        MHit.PVP = False
        MHit.forget(u)
        # the REAL ManaHitSys.handle: a Warrior holding an iron sword hits an NPC (no PlayerRef) / a player / itself
        st = alloc(MapStore)
        st.comps = IHM()
        aref, nref, pref = Ref(st, 10), Ref(st, 11), Ref(st, 12)
        pra = mkpr(u, "Hitter")
        player(str(u), [("Combat.Warrior", ECUM[50])])
        set_class(u, "Warrior")
        Store.DATA.clear()
        hb = alloc(FakeHotbar)

        def item(iid):
            it = alloc(IS)
            setany(it, "itemId", iid)
            setany(it, "quantity", JInt(1))
            return it
        hb.item = item("Weapon_Sword_Iron")
        cbuf = alloc(CompCB)
        cbuf.comps = IHM()
        cbuf.comps.put(aref, IHM())
        cbuf.comps.get(aref).put(TPR, pra)
        cbuf.comps.get(aref).put(TT["hotbarInventoryComponentType"], hb)
        st.comps.put(pref, IHM())
        st.comps.get(pref).put(TPR, mkpr(UUID(0x25E, 2), "Target"))

        def chunk(r):
            c = alloc(MapChunk)
            c.comps = IHM()
            c.ref = r
            return c
        sysm = MHS()

        def hit(target, amount=6.0, cancel=False, att=aref):
            d = DMG(DES(att), JInt(0), JFloat(amount))
            if cancel:
                d.setCancelled(True)
            MHit.LAST.clear()
            MHit.PEND.clear()
            sysm.handle(JInt(0), chunk(target), st, cbuf, d)
            p = MHit.PEND.get(u)
            return 0.0 if p is None else float(p)
        H["sys"] = {"npc": hit(nref), "cancelled": hit(nref, cancel=True), "zero": hit(nref, amount=0.0), "self": hit(aref), "player": hit(pref)}
        MHit.PVP = True
        H["sys"]["player_on"] = hit(pref)
        MHit.PVP = False
        hb.item = item("Weapon_Axe_Iron")
        H["sys"]["axe"] = hit(nref)
        hb.item = item("Weapon_Sword_Iron")
        set_class(u, "Mage")
        H["sys"]["mage"] = hit(nref)
        set_class(u, None)
        H["sys"]["noclass"] = hit(nref)
        set_class(u, "Warrior")
        bridge.remove("class:fn:allowed")
        H["sys"]["noclasses"] = hit(nref)
        bridge.put("class:fn:allowed", Const(JBool.TRUE))
        H["sys"]["again"] = hit(nref)
        H["sys"]["failed"] = bool(MHS.FAILED_ONCE)
        # ManaHit.apply on a real stat map (Mana max 30)
        m = statmap(30.0, 29.5)
        cb = fakecb(m)
        MHit.PEND.put(u, JClass("java.lang.Float")(1.0))
        g1 = float(MHit.apply(u, cb, Ref(st, 13)))
        v1 = float(m.get(1).get())
        MHit.PEND.put(u, JClass("java.lang.Float")(1.0))
        g2 = float(MHit.apply(u, cb, Ref(st, 13)))
        m2 = statmap(30.0, 10.0)
        cb2 = fakecb(m2)
        MHit.PEND.put(u, JClass("java.lang.Float")(2.0))
        g3 = float(MHit.apply(u, cb2, Ref(st, 13)))
        v3 = float(m2.get(1).get())
        m3 = statmap(30.0, 10.0)
        cb3 = fakecb(m3)
        cb3.dd, cb3.ddType = JClass("com.hypixel.hytale.server.core.entity.damage.DamageDataComponent")(), E["deathType"]   # "dead": a component under the death type
        MHit.PEND.put(u, JClass("java.lang.Float")(2.0))
        g4 = float(MHit.apply(u, cb3, Ref(st, 13)))
        H["apply"] = {"capped": [g1, v1], "full": g2, "plain": [g3, v3], "dead": [g4, float(m3.get(1).get()), MHit.PEND.get(u) is None],
                      "none": float(MHit.apply(u, cb, Ref(st, 13))), "failed": bool(MHit.FAILED_ONCE)}
        Store.data(u)                                              # the profile data in memory (the regen sources read the cache only)
        H["source"] = str(MHit.sourceText(u))
        H["srcs"] = [str(x) for x in MReg.sources(u)]
        H["statsline"] = [str(MHit.statsLine(int(J("SkillClass").slotOfClass("Warrior")), False)), MHit.statsLine(int(J("SkillClass").slotOfClass("Mage")), False) is None,
                          MHit.statsLine(int(J("SkillClass").slotOfClass("Warrior")), True) is None]
        # the REAL CombatDmgSys.handle: Warrior Swordsmanship 50 with a sword on an NPC = x (1 + 0.002 x 50 + 5% x 0.5)
        d = DMG(DES(aref), JInt(0), JFloat(10.0))
        CDS().handle(JInt(0), chunk(nref), st, cbuf, d)
        H["cds"] = [float(d.getAmount()), round(10.0 * (1.0 + 0.002 * 50 + 0.05 * 0.5), 4), bool(CDS.FAILED_ONCE)]
        d = DMG(DES(aref), JInt(0), JFloat(10.0))
        CDS().handle(JInt(0), chunk(pref), st, cbuf, d)
        H["cds_pvp"] = float(d.getAmount())
        J("PerkCfg").ENABLED = False
        d = DMG(DES(aref), JInt(0), JFloat(10.0))
        CDS().handle(JInt(0), chunk(nref), st, cbuf, d)
        H["cds_perkoff"] = [float(d.getAmount()), round(10.0 * (1.0 + 0.05 * 0.5), 4)]
        J("PerkCfg").ENABLED = True
        MHit.retain(JClass("java.util.HashSet")())
        H["retain"] = [int(MHit.PEND.size()), int(MHit.LAST.size())]
    except Exception:
        import traceback
        H["error"] = traceback.format_exc()[-3000:]
    R["H"] = H
    json.dump(R, open(out, "w"), indent=1)


# ============================================================================================ parent
def expect(cls, lv):
    """the spec maths for one class at class level lv (class part only: no Overall Level, no gear, no gathering)"""
    bm, bs, mpl, spl = SPEC[cls]
    h, mn, sta, df, dm, rg = BOOST[cls]
    f = min(lv, 100) / 100.0
    health = 100 + r2(0.1 * lv) + r2(h * f)
    mana = bm + r2(mpl * lv) + r2(mn * f)
    stam = 10 + r2(bs + spl * lv) + r2(sta * f)
    regen = 7.0 * max(0, lv - 20) + rg * f
    return r2(health), r2(mana), r2(stam), r2(df * f), r2(regen)


def main():
    if "--mkfake" in sys.argv:
        return t15().run_mkfake(arg("--mkfake"))
    if "--mkfake25" in sys.argv:
        return run_mkfake25(arg("--mkfake25"))
    if "--child" in sys.argv:
        return run_child(arg("--child"), arg("--out"))
    if "--start" in sys.argv:
        return run_start(arg("--start"), arg("--out"), arg("--mode"))
    if "--unit" in sys.argv:
        return run_unit(arg("--unit"), arg("--fake"), arg("--out"), arg("--livexp"))
    if "--audit" in sys.argv:
        return t15().run_audit(arg("--audit"), arg("--fake"), arg("--out"))
    if "--compare" in sys.argv:
        m = t20()
        m.VERSION, m.PREV_VERSION = VERSION, PREV_VERSION
        return m.run_compare(arg("--compare"), arg("--prevjar"), arg("--out"))
    for j in (JAR, PREV_JAR):
        if not os.path.isfile(j):
            sys.exit("no jar at %s - build it first" % j)
    if not os.path.isdir(os.path.join(LIVE_DIR, "players")):
        sys.exit("the live players folder is not in %s (pass --live <folder>; it is only ever read and copied)" % LIVE_DIR)
    scratch_root = os.path.join(TOOLS, "dev", "scratch").replace("\\", "/").lower().rstrip("/")
    here = SCRATCH.replace("\\", "/").lower().rstrip("/")
    rel = here[len(scratch_root) + 1:] if here.startswith(scratch_root + "/") else ""
    if here == scratch_root or not rel or "/" not in rel:
        sys.exit("--dir must be a sub-folder of a task folder inside tools/dev/scratch/ (e.g. tools/dev/scratch/<task>/skills0425; that folder is "
                 "deleted afterwards), not %s" % SCRATCH)
    GUARD_OK[0] = True
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.makedirs(env["TEMP"], exist_ok=True)
    live_snap = dict((os.path.relpath(os.path.join(r, f), LIVE_DIR), os.path.getmtime(os.path.join(r, f))) for r, ds, fs in os.walk(LIVE_DIR) for f in fs)
    me = os.path.abspath(__file__)
    fake = os.path.join(SCRATCH, "fake")
    p = subprocess.run([sys.executable, me, "--mkfake", fake, "--dir", SCRATCH], env=env, capture_output=True)
    p2 = subprocess.run([sys.executable, me, "--mkfake25", fake, "--dir", SCRATCH], env=env, capture_output=True)
    check(p.returncode == 0 and p2.returncode == 0 and os.path.isfile(os.path.join(fake, "skyytest25", "CompCB.class")),
          "the stand-in classes were generated: %s %s" % (p.stderr[-300:], p2.stderr[-300:]))
    outs = {}
    for mode, jar in (("prev", PREV_JAR), ("new", JAR)):
        outp = os.path.join(SCRATCH, "run-%s.json" % mode)
        with open(os.path.join(SCRATCH, "run-%s.log" % mode), "wb") as lf:
            p = subprocess.run([sys.executable, me, "--child", jar, "--out", outp, "--dir", SCRATCH], env=env, stdout=lf, stderr=subprocess.STDOUT)
        check(p.returncode == 0 and os.path.isfile(outp), "child JVM (%s) ran" % mode)
        if os.path.isfile(outp):
            outs[mode] = json.load(open(outp))
    sts = {}
    for mode, jar in (("prev", PREV_JAR), ("new", JAR)):
        shutil.copytree(LIVE_DIR, os.path.join(SCRATCH, "live-copy-" + mode))
        outs_ = os.path.join(SCRATCH, "start-%s.json" % mode)
        with open(os.path.join(SCRATCH, "start-%s.log" % mode), "wb") as lf:
            p = subprocess.run([sys.executable, me, "--start", jar, "--out", outs_, "--mode", mode, "--dir", SCRATCH], env=env, stdout=lf, stderr=subprocess.STDOUT)
        check(p.returncode == 0 and os.path.isfile(outs_), "start-twice child JVM (%s) ran" % mode)
        if os.path.isfile(outs_):
            sts[mode] = json.load(open(outs_))
    shutil.copytree(LIVE_DIR, os.path.join(SCRATCH, "live-copy-unit"))
    uo = os.path.join(SCRATCH, "unit.json")
    with open(os.path.join(SCRATCH, "unit.log"), "wb") as lf:
        p = subprocess.run([sys.executable, me, "--unit", JAR, "--fake", fake, "--out", uo, "--livexp", os.path.join(SCRATCH, "live-copy-unit", "xp.properties"),
                            "--dir", SCRATCH], env=env, stdout=lf, stderr=subprocess.STDOUT)
    check(p.returncode == 0 and os.path.isfile(uo), "behaviour child JVM ran (log %s)" % os.path.join(SCRATCH, "unit.log"))
    cmpo = os.path.join(SCRATCH, "compare.json")
    pc = subprocess.run([sys.executable, me, "--compare", JAR, "--prevjar", PREV_JAR, "--out", cmpo, "--dir", SCRATCH], env=env, capture_output=True)
    check(pc.returncode == 0 and os.path.isfile(cmpo), "class compare child ran: %s" % pc.stderr[-500:])
    auo = os.path.join(SCRATCH, "audit.json")
    pa = subprocess.run([sys.executable, me, "--audit", JAR, "--fake", fake, "--out", auo, "--dir", SCRATCH], env=env, capture_output=True)
    check(pa.returncode == 0 and os.path.isfile(auo), "engine-access audit child ran: %s" % pa.stderr[-500:])
    if FAILS:
        return finish()
    # ---------------------------------------------------------------- A
    for mode in ("new", "prev"):
        r = outs[mode]
        check(not r["load_fails"] and r["loaded"] == r["classes"], "A (%s): %d / %d classes load under -Xverify:all %s" % (mode, r["loaded"], r["classes"], r["load_fails"][:3]))
    print("A. -Xverify:all: 0.4.25 %d / %d classes, 0.4.24 %d / %d" % (outs["new"]["loaded"], outs["new"]["classes"], outs["prev"]["loaded"], outs["prev"]["classes"]))
    # ---------------------------------------------------------------- J
    jz, jp = zipfile.ZipFile(JAR), zipfile.ZipFile(PREV_JAR)
    nn, pn = set(n for n in jz.namelist() if not n.endswith(".class")), set(n for n in jp.namelist() if not n.endswith(".class"))
    changed = sorted(n for n in nn & pn if n != "manifest.json" and jz.read(n) != jp.read(n))
    mn_, mp_ = json.loads(jz.read("manifest.json")), json.loads(jp.read("manifest.json"))
    mdiff = sorted(k for k in set(mn_) | set(mp_) if mn_.get(k) != mp_.get(k))
    check(nn == pn and not changed and set(mdiff) <= {"Name", "Version", "Description"} and mn_["Version"] == VERSION,
          "J: the asset files = 0.4.24's (added %s gone %s changed %s); manifest differs in %s" % (sorted(nn - pn)[:3], sorted(pn - nn)[:3], changed[:3], mdiff))
    print("J. jar: %d asset files = 0.4.24's; manifest: %s" % (len(nn), mdiff))
    U_ = json.load(open(uo))
    check(not U_.get("load_fails"), "unit child: classes load %s" % U_.get("load_fails"))
    for sec in ("MG", "P", "D", "H"):
        check("error" not in U_.get(sec, {}), "%s ran: %s" % (sec, (U_.get(sec, {}).get("error") or "")[-1500:]))
    if FAILS:
        return finish()
    # ---------------------------------------------------------------- MG
    MG = U_["MG"]
    keys = MG["keys"]
    live_txt = open(os.path.join(LIVE_DIR, "xp.properties"), "rb").read().decode("latin-1")
    L = MG["live"]
    check(L is not None and all(L["rw"]) and L["same"] and L["kept"] == "", "MG live: every rewrite planned (%s), sameAfter, nothing kept: %s" % (L and L["rw"], L and L["kept"]))
    old_lines = live_txt.split("\n")
    new_lines = L["text"].split("\n")
    rw_map = dict(zip(keys["rw"], keys["new"]))
    diffs = [(i, a, b) for i, (a, b) in enumerate(zip(old_lines, new_lines)) if a != b]
    okd = all(a.split("=", 1)[0] in rw_map and b == a.split("=", 1)[0] + "=" + rw_map[a.split("=", 1)[0]] for i, a, b in diffs)
    tail = "\n".join(new_lines[len(old_lines) - 1:])
    rewritten = "\n".join((l.split("=", 1)[0] + "=" + rw_map[l.split("=", 1)[0]]) if (not l.startswith("#") and "=" in l and l.split("=", 1)[0] in rw_map) else l
                           for l in old_lines)
    check(okd and len(diffs) == 6 and L["text"].startswith(rewritten) and live_txt.endswith("\n"),
          "MG live: exactly the 6 old-default lines rewritten in place (value text only), every other byte kept: %s" % diffs[:8])
    check(keys["head"].strip().split("\n")[0] in tail and "perk.foraging.defensePerLevel=0.2" in tail and "mana.classBase.Warrior=21" in tail
          and "mana.classPerLevel.Berserker=2" in tail and "mana.classPerLevel.Spellblade=4" in tail and "stamina.classBase.Berserker=12" in tail
          and "mana.onHit.Warrior=1" in tail and "classBoost.regen.Spellblade=8" in tail and "mana.classBase.Mage=" not in tail and "mana.classPerLevel.Mage=" not in tail,
          "MG live: the appended block = the marker header + only the missing lines (Mage / Priest Base Mana + their Mana per level were there)")
    rows = L["rows"]
    rowk = [rows[i] for i in range(0, len(rows), 3)]
    check(rowk[:6] == keys["rw"] and "perk.foraging.defensePerLevel" in rowk and "mana.classBase[Warrior]" in rowk and "mana.classPerLevel[Monk]" in rowk
          and not any(k.startswith(("stamina.", "classBoost.", "mana.onHit")) for k in rowk),
          "MG live: change-log rows = the 6 rewrites (Undo = old) + the added Defense / Base Mana / Mana per level lines: %s" % rowk)
    C = MG["live_crlf"]
    check(C is not None and C["same"] and "\r\n" in C["text"] and C["text"].count("\n") == C["text"].count("\r\n"), "MG CRLF: CRLF in = CRLF out, no bare LF")
    Hn = MG["hand"]
    check(Hn["rw"][0] is False and Hn["rw"][2] is False and "perk.mining.staminaPerLevel=0.1 kept" in Hn["kept"] and "mana.base=30 kept" in Hn["kept"]
          and "\nperk.mining.staminaPerLevel=0.1\n" in Hn["text"] and "\nmana.base=30\n" in Hn["text"] and Hn["same"] and all(Hn["rw"][i] for i in (1, 3, 4, 5)),
          "MG hand-edited: an admin's values kept + named in the INFO note, the other rewrites still made: %s" % Hn["kept"])
    check(MG["marked"] is None and MG["defaults"] is None, "MG: a file with the marker = nothing; the 0.4.25 default file = nothing")
    B_ = MG["bare"]
    check(B_ is not None and B_["rw"] == [False, False, False, False, False, True] and "perk.foraging.defensePerLevel" not in B_["text"]
          and "mana.classBase." not in B_["text"] and "mana.classPerLevel." not in B_["text"] and "stamina.classBase.Mage=4" in B_["text"] and B_["same"],
          "MG gates: no perk.* / overall.enabled / class Mana table = those lines left to SkyySkills' own section appends; the new tables added")
    Lo = MG["lower"]
    check("mana.classBase.Warrior=" not in Lo["text"].split(keys["head"].strip().split("\n")[0])[1] and "mana.classBase.mage=30" in Lo["text"],
          "MG: a class in another spelling counts as present (not added twice); mage=30 is not the exact key -> not rewritten")
    check(MG["multi"]["rw"][2] is False and MG["zero"]["rw"][0] is True and "perk.mining.staminaPerLevel=0.2" in MG["zero"]["text"],
          "MG: a multi-line mana.base is kept; 0.050 = the old default 0.05 -> rewritten")
    check("mana.classPerLevel.Warrior" not in MG["noper"]["text"], "MG: an emptied Max Mana per class level table stays empty")
    check(MG["tamper"] is False and MG["numEq"] == [True, True, False, False], "MG: sameAfter refuses an extra key; numEq")
    print("MG. PerkMig.plan: live file (6 rewrites in place + %d lines appended), CRLF, hand-edited kept, marker / defaults = nothing, gates, spelling, "
          "multi-line, 0.050, emptied table, tamper check" % sum(1 for x in L["add"] if x))
    # ---------------------------------------------------------------- M
    Mn, Mp = sts.get("new", {}), sts.get("prev", {})
    check("error" not in Mn and "error" not in Mp, "M: START TWICE ran: %s" % (Mn.get("error") or Mp.get("error") or "")[-800:])
    if "error" not in Mn and "error" not in Mp:
        pr1 = Mp["xp1"]
        nw1 = Mn["xp1"]
        expect_txt = L["text"]
        check(nw1 == expect_txt and pr1 == Mn["xp0"], "M: start 1 of 0.4.25 wrote exactly the planned file (= 0.4.24's untouched file + the rewrites + the block)")
        check(len(Mn["hist_new"]) >= 1 and all(Mn["hist_new_bytes_eq"]), "M: the config-history snapshot holds the old bytes: %s" % Mn["hist_new"])
        nlog = Mn["log1"][len(Mn["log0"]):]
        check(nlog.count("SkyySkills 0.4.25") == len(rowk) and "perk.mining.staminaPerLevel\t0.05\t0.2" in nlog and "mana.base\t10\t25" in nlog,
              "M: config-changes.log got one line per change (Undo): %d" % nlog.count("SkyySkills 0.4.25"))
        check(Mn["changed2"] == [] and Mn["players_same"] and Mp["players_same"], "M: start 2 changes nothing; player files never touched: %s" % Mn["changed2"])
        a = Mn["after"]
        check(a["base"] == 25.0 and a["inCombat"] == 75 and a["sta"][0] == 0.2 and a["hp"][1] == 0.0 and a["def"][1] == 0.2
              and "Mage 45" in a["classBase"] and "Berserker 12" in a["classBase"] and "Warrior 2" in a["classPer"] and "Spellblade 4" in a["classPer"],
              "M: after the update the live copy reads base 25, in-combat 75, Mining 0.2 Stamina, Foraging 0 Health / 0.2 Defense, the class tables: %s" % a)
        print("M. start twice on the live copy (%d files, %d players): start 1 = the planned file + History + %d log lines; start 2 nothing" % (
            Mn["files"], Mn["players"], nlog.count("SkyySkills 0.4.25")))
        print("   PerkMig: " + Mn["r1"].get("PerkMig", "")[:400])
    # ---------------------------------------------------------------- P
    P = U_["P"]
    check(not P["tick_failed"], "P: Perks.tick / ovl never failed")
    rows_out = []
    pbad = []
    for g in P["grid"]:
        want = expect(g["cls"], g["lv"])
        got = (r2(g["max"][0]), r2(g["max"][1]), r2(g["max"][2]), r2(g["def"]), r2(g["regen"]))
        if any(abs(x - y) > 0.011 for x, y in zip(got, want)) or not g["same2"] or abs(g["bdef"] - g["def"]) > 1e-9:
            pbad.append([g["cls"], g["lv"], got, want, g["same2"]])
        rows_out.append((g["cls"], g["lv"], got, g["hit"]))
    check(not pbad and len(P["grid"]) == 28, "P: every class at 0 / 25 / 50 / 100 = the spec maths (Health, Mana, Stamina, Defense, regen %%); 2nd tick the same: %s" % pbad[:4])
    sw = P["switch"]
    check(r2(sw[0]["max"][2]) == r2(expect("Warrior", 50)[2]) and r2(sw[1]["max"][2]) == r2(expect("Mage", 50)[2])
          and r2(sw[2]["max"][2]) == r2(expect("Berserker", 100)[2]) and sw[3]["max"] == sw[0]["max"]
          and set(sw[4]["mods"][2]) <= {"skyyskill_stamina"} and sw[4]["max"][2] == 10.0,
          "P: class switch Warrior -> Mage -> Berserker -> Warrior -> none: the pools are replaced each second, never stack: %s" % [x["max"] for x in sw])
    ps = P["profile"]
    check(r2(ps[0]["max"][1]) == r2(expect("Warrior", 50)[1]) and r2(ps[1]["max"][1]) == r2(expect("Mage", 100)[1])
          and r2(ps[1]["max"][2]) == r2(expect("Mage", 100)[2]) and ps[2]["max"] == ps[0]["max"],
          "P: profile switch p1 Warrior 50 -> p2 Mage 100 -> p1: pools follow the active profile: %s" % [x["max"] for x in ps])
    cl = lambda mm: [dict((k, v) for k, v in x.items() if k.startswith("skyyskill_class")) for x in mm]
    check(cl(P["hold"]["held"]) == cl(P["hold"]["before"]) and "skyyskill_classstamina" in P["hold"]["before"][2],
          "P: the session hold keeps the saved class pools (relog, no class yet): %s" % P["hold"])
    gth = P["gather"]
    check(gth["mining"] == 100 and gth["foraging"] == 100 and gth["mods"][2].get("skyyskill_stamina") == 20.0 and gth["def"] == 20.0
          and "skyyskill_health" not in gth["mods"][0] and gth["bdef"] == "20.0",
          "P: Mining 100 = +20 max Stamina, Foraging 100 = +20 Defense (skill:def 20.0) and no Health: %s" % gth)
    ln = P["lines"]
    w50 = ln["Warrior50"]["now"]
    check(any("max Mana (2 per level)" in x and "max Stamina (10 + 0.13 per level) - Warrior" in x for x in w50)
          and any(x.startswith("Class balance: +1.5 Health, +6.5 Mana, +2.5 Stamina, +1.5 Defense, +2.5% damage, +6.5% Mana regen") for x in w50)
          and any(x.startswith("+1 Mana per hit with Warrior weapons (every 0.5 s, monsters only)") for x in w50) and len(w50) <= 7,
          "P: the Warrior 50 Stats page lines: %s" % w50)
    check(any("+2 max Mana, +0.13 max Stamina" == x for x in ln["Warrior50"]["next"]), "P: next level line: %s" % ln["Warrior50"]["next"])
    check(any("+20 Defense (less damage taken)" == x for x in ln["Foraging100"]["now"]) and not any("Health" in x for x in ln["Foraging100"]["now"])
          and any("+20 max Stamina" == x for x in ln["Mining100"]["now"]), "P: Foraging / Mining 100 lines: %s / %s" % (ln["Foraging100"]["now"], ln["Mining100"]["now"]))
    check(all(len(v["now"]) <= 7 for v in ln.values()), "P: no Stats page list above 7 lines: %s" % dict((k, len(v["now"])) for k, v in ln.items()))
    check("class balance 13" in P["breakdown"], "P: /skills mana names the class balance Mana: %s" % P["breakdown"])
    off = P["off"]
    check(not any(k.startswith("skyyskill_classstamina") or k.startswith("skyyskill_classboost") for mm in off["mods"] for k in mm)
          and off["def"] == 0.0 and off["dmg"] == 0.0, "P: class Stamina off + class balance off remove the pools: %s" % off)
    check(P["fault"]["after"] == P["fault"]["before"] and P["fault"]["logged"], "P: a broken table keeps the saved pools (no dip), logged once")
    pa_ = P["parse"]
    check(pa_["cls"] == ["Monk", "Mage", "Spellblade"] and pa_["v"] == [4.0, 1000.0, 7.0] and "Nope is not a class" in pa_["bad"] and "Monk is listed twice" not in pa_["bad"]
          and "abc is not a number" in pa_["bad"], "P: ClassTbl.parse: Spellblade accepted, Shaman = Monk, clamp 1000, junk reported: %s" % pa_)
    check(P["check"][0] is None and "Spellblade" in P["check"][1] and P["check"][2] is None, "P: check hooks accept Spellblade: %s" % P["check"])
    check(P["spellblade"] == [33.0, 4.0, 7.0, 8.0], "P: Spellblade sits in the tables (base Mana 33, 4 a level, Stamina 7, balance 8): %s" % P["spellblade"])
    print("P. stat pools: 7 classes x 4 levels on real EntityStatMaps = the spec maths; class / profile switch, hold, gathering perks, Stats lines, switches, fault")
    # ---------------------------------------------------------------- D
    D = U_["D"]
    dbad = [c for c in D["cases"] if abs(c[5] - c[6]) > 1e-6 or not (0.0 <= c[4] <= 1.0)]
    check(not dbad and len(D["cases"]) == 400, "D: SkyyGear's step x SkillDef.factor = scale / (scale + G + S) in 400 random cases: %s" % dbad[:3])
    check(D["table"] == [[0, 1.0], [5, round(100 / 105, 6)], [10, round(100 / 110, 6)], [20, round(100 / 120, 6)], [40, round(100 / 140, 6)]]
          and abs(D["sum_g50_s20"][1] - round(100 / 170, 6)) < 1e-6, "D: no gear: x 100 / (100 + S); gear 50 + skill 20 = x 100 / 170: %s" % D["sum_g50_s20"])
    check(D["defOf"] == [12.0, 5.0, 0.0, -5.0] and D["gearDef"] == 15.0, "D: gear Defense = gear:stats def + gear:extra def (SkyyGear's parse rules): %s %s" % (D["defOf"], D["gearDef"]))
    check(D["nofn"] == [False, True, 100.0] and D["fn"] == [True, False, 250.0] and D["cached"] == [False, 250.0] and D["reread"][:2] == [True, 100.0]
          and D["junk"] == 100.0, "D: SkyyGear's settings read over config:fn:SkyyGear (none / off+250 / cached 5 s / re-read / junk = 100)")
    check(D["published"] == [20.0, "20.0"] and abs(D["reduce"][0] - 115.0 / 135.0) < 1e-6 and abs(D["reduce"][1] - 100.0 * 115.0 / 135.0) < 1e-3,
          "D: reduce on a real Damage: gear 15 + skill 20 -> SkyyGear's x100/115 then ours = x100/135 overall: %s" % D["reduce"])
    check(D["nosrc"] == [1.0, 100.0] and D["cancelled"] == [1.0, 100.0] and D["noskill"] == [1.0, 100.0], "D: no entity source / cancelled / no skill Defense = unchanged")
    check(D["deps"]["n"] == 1 and "AFTER" in D["deps"]["order"][0] and D["deps"]["class"] == ["com.hypixel.hytale.server.core.modules.entity.damage.DamageSystems$ArmorDamageReduction"]
          and D["deps"]["u"] == 0, "D: DefSys(true) runs AFTER ArmorDamageReduction (SkyyGear's Defense place); DefSysU unordered: %s" % D["deps"])
    check(abs(D["handle"][0] - 100.0 * 115.0 / 135.0) < 1e-3 and D["handle"][1] == 100.0 and abs(D["handle"][2] - D["handle"][0]) < 1e-6 and not D["handle"][3],
          "D: the REAL DefSys.handle: player victim reduced, NPC victim unchanged, DefSysU the same: %s" % D["handle"])
    check(D["unpublished"] == [0.0, True] and D["retain"] == [0.0, True], "D: Defense 0 removes skill:def; a player who left loses it")
    print("D. skill Defense: 400 random cases = SkyyGear's formula on G + S; real Damage + the REAL DefSys.handle; AFTER ArmorDamageReduction")
    # ---------------------------------------------------------------- H
    H = U_["H"]
    check(H["grant"] == [1.0, 0.5, 0.0, 0.0, 0.0], "H: grant never goes above max: %s" % H["grant"])
    check(H["offer"] == [1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0] and H["pend"] == 2.0 and H["pvp_on"] == 1.0,
          "H: offer: 1, cooldown 100 / 499 ms = 0, 500 ms = 1, a player = 0 (switch off), Mage / Priest 0; PvP switch on = 1: %s" % H["offer"])
    sy = H["sys"]
    check(sy["npc"] == 1.0 and sy["cancelled"] == 0.0 and sy["zero"] == 0.0 and sy["self"] == 0.0 and sy["player"] == 0.0 and sy["player_on"] == 1.0
          and sy["axe"] == 0.0 and sy["mage"] == 0.0 and sy["noclass"] == 0.0 and sy["noclasses"] == 0.0 and sy["again"] == 1.0 and not sy["failed"],
          "H: the REAL ManaHitSys.handle: NPC hit with a sword = 1; cancelled / 0 damage / self / player (off) / axe / Mage / no class / no SkyyClasses = 0: %s" % sy)
    ap = H["apply"]
    check(ap["capped"] == [0.5, 30.0] and ap["full"] == 0.0 and ap["plain"] == [2.0, 12.0] and ap["dead"][0] == 0.0 and ap["dead"][1] == 10.0 and ap["dead"][2]
          and ap["none"] == 0.0 and not ap["failed"], "H: ManaHit.apply on a real stat map: capped at max, full = 0, +2, dead = dropped: %s" % ap)
    check(H["source"] == "Mana on hit +1 (class weapon, every 0.5 s)" and H["source"] in H["srcs"] and any(x.startswith("class balance=+") for x in H["srcs"])
          and any(x.startswith("class level=+") for x in H["srcs"]), "H: the Mana Regen sources list Mana on hit + the class balance: %s" % H["srcs"])
    check(H["statsline"][0] == "+1 Mana per hit with Warrior weapons (every 0.5 s, monsters only)" and H["statsline"][1] and H["statsline"][2], "H: stats line: %s" % H["statsline"])
    check(abs(H["cds"][0] - H["cds"][1]) < 1e-4 and not H["cds"][2] and H["cds_pvp"] == 10.0 and abs(H["cds_perkoff"][0] - H["cds_perkoff"][1]) < 1e-4,
          "H: the REAL CombatDmgSys.handle: Warrior 50 sword on an NPC x (1 + 10%% + 2.5%%); a player unchanged; perks off = the class balance alone: %s %s %s" % (H["cds"], H["cds_pvp"], H["cds_perkoff"]))
    check(H["retain"] == [0, 0], "H: a player who left loses the queue and the cooldown")
    print("H. Mana on hit: grant / offer / cooldown / PvP / casters; the REAL ManaHitSys + CombatDmgSys handle; apply on a real stat map; sources")
    # ---------------------------------------------------------------- F
    cmp_ = json.load(open(cmpo))
    added = sorted(k for k, v in cmp_.items() if v == "only in new")
    gone = sorted(k for k, v in cmp_.items() if v == "only in prev")
    chg = sorted(k for k, v in cmp_.items() if isinstance(v, dict))
    allowed = {"SkyySkillsPlugin", "SkillCfg", "OverallCfg", "PerkCfg", "Perks", "CombatDmgSys", "ManaRegen", "AcroSys", "Acro", "StatsPage", "ClassMana",
               "MobXp", "ClassManaMig", "ManaMig", "CfgRows", "SkillKit", "Overall", "SkillMsg"}
    check(added == sorted(["ClassTbl", "ClassPower", "ManaHit", "SkillDef", "DefSys", "DefSysU", "ManaHitSys", "PerkMig"]) and not gone and set(chg) <= allowed,
          "F: class compare 0.4.24 -> 0.4.25: added %s, gone %s, changed %s" % (added, gone, chg))
    print("F. class compare: added %s; changed %s" % (", ".join(added), ", ".join(chg)))
    for c in chg:
        print("   %s: %s" % (c, ", ".join(m.split("(")[0] for m in cmp_[c]["methods"])[:300]))
    # ---------------------------------------------------------------- AU
    au = json.load(open(auo))
    check(au["refused"] == [] and au["control"] and au["refs"] > 1000, "AU: %d references in %d classes, refused %s; control refused: %s" % (
        au["refs"], au["classes"], au["refused"][:3], bool(au["control"])))
    print("AU. engine-access audit: %d references, %d refused (control refused: %s)" % (au["refs"], len(au["refused"]), bool(au["control"])))
    # ---------------------------------------------------------------- RB (fix round): the 0.4.25 header names the rollback steps
    hd = open(os.path.join(HERE, "build_skyyskills_%s.py" % VERSION), encoding="utf8").read().replace("\r\n", "\n")
    hd = hd.split("0.4.24: THE WOOD WAND SIGNATURE", 1)[0]
    rbt = " ".join(hd[hd.find("ROLLBACK below 0.4.25"):].split()) if "ROLLBACK below 0.4.25" in hd else ""
    check(all(k in rbt for k in ("skyyskill_classstamina", "_classboosthp", "_classboostmana", "_classbooststamina",
                                 '"Class Stamina"', '"Class balance boost"', "log in once")),
          "RB: the 0.4.25 header carries the rollback note (4 saved modifiers, both switches): %s" % rbt[:300])
    print("RB. rollback note in the 0.4.25 header; switching both off removes the 4 saved modifiers = check P (switches)")
    # ---------------------------------------------------------------- the live data was only read
    live_after = dict((os.path.relpath(os.path.join(r, f), LIVE_DIR), os.path.getmtime(os.path.join(r, f))) for r, ds, fs in os.walk(LIVE_DIR) for f in fs)
    check(live_after == live_snap, "the live Skyy_SkySkills folder was never written")
    # ---------------------------------------------------------------- the stat table (for the class balance chart)
    print()
    print("CLASS STAT TABLE (class part only: vanilla 100 Health / 0 Mana / 10 Stamina + class base + per level + class balance; no Overall Level,")
    print("no gear, no Mining / Foraging; regen = Mana Regen % (vanilla 5 a second; in combat x 75 %); Mana on hit per class weapon hit)")
    print("| Class | Lv | Health | Mana | Stamina | Defense | Mana regen % | regen / s out | regen / s in combat | Mana on hit |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for cls, lv, got, hit in rows_out:
        out_s = 5.0 * (1.0 + got[4] / 100.0)
        print("| %s | %d | %s | %s | %s | %s | %s | %s | %s | %s |" % (cls, lv, fmt(got[0]), fmt(got[1]), fmt(got[2]), fmt(got[3]), fmt(got[4]),
                                                              fmt(r2(out_s)), fmt(r2(out_s * 0.75)), fmt(hit)))
    return finish()


def fmt(x):
    return ("%.2f" % x).rstrip("0").rstrip(".")


def finish():
    print()
    if FAILS:
        print("%d FAILED, %d ok" % (len(FAILS), OKS[0]))
        for f in FAILS:
            print("  -", f[:600])
    else:
        print("ALL %d CHECKS PASSED" % OKS[0])
    if GUARD_OK[0] and not KEEP and not FAILS:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main() or 0)
