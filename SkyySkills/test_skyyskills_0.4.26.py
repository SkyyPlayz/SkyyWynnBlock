"""SkyySkills 0.4.26 - bare-JVM harness for TOOL FORTUNE + skill:dmg (tools/skills_0_4_26_patch.py; Skyy 2026-10-05 / 2026-10-09; the other
half is SkyyGear 0.2.12). Every new code path runs on the REAL classes of the 0.4.26 jar (HytaleServer.jar on the class path, -Xverify:all,
-XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in the scratch folder); the live save data is only ever READ and copied into scratch.

    python SkyySkills/test_skyyskills_0.4.26.py [--jar <SkyySkills-0.4.26.jar>] [--prev <SkyySkills-0.4.25.jar>] [--dir <scratch>]
                                                [--live <Skyy_SkyySkills folder>] [--keep]

SECTIONS
  A   every class of both jars loads under -Xverify:all
  J   the jar's asset files = 0.4.25's (only manifest.json differs: Version / Name / Description)
  M   START TWICE on a scratch copy of the live data (setup()'s data steps, both jars): 0.4.26 changes exactly what 0.4.25 changes (nothing on
      today's live file), start 2 changes nothing, player files never touched; perk.fortuneMax reads its default 2 from a file without it
  X   TOOL FORTUNE: the fresh file (perk.fortuneMax under perk.doubleDropMax); Perks.extras (pure: 0 / 0.5 / 1.5 / 2 / NaN / 15); Perks.fortune
      against 0.4.25's chanceU on every case without a "gear" source (no skill:bonus key = an older partner, trees only, perk only, bonus off),
      with one (50 -> 0.5, 150 -> 1.5, the fortuneMax cap, a low cap never cuts the old chance, the doubleDropMax cap of the base, another
      skill's key, NaN / negative); Perks.rolls statistics for Fortune 0 / 50 / 150 / 250 (values and mean), doubleDropOnly (_Trunk);
      breakDouble on a PLACED block (tracked false: never, counted), breakDouble / harvestDouble / Sickle.award with a real PlayerRef +
      BlockType + InteractivelyPickupItemEvent (the new loops run, the extra rolls counted)
  G   skill:dmg:<uuid>: ClassPower.dmgPct = the class balance damage table at the class level; SkillDef.setDmg / dmgOf / retain (rounded,
      removed at 0 / NaN / when the player leaves); the REAL Perks.tick publishes it (Warrior 50 -> 2.5) and removes it without a class
  F   class compare 0.4.25 -> 0.4.26 method by method: only the planned classes changed, nothing added / removed
  AU  the engine-access audit (every bytecode reference looked up with the JVM's own access rules; control refused)
"""
import os, sys, re, json, shutil, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, PREV_VERSION = "0.4.26", "0.4.25"
PKG = "com.skyy.skills."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "tools01fix2", "skills0426")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
PREV_JAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyySkills-%s.jar" % PREV_VERSION)))
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
LIVE_DIR = os.path.abspath(arg("--live", os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyySkills")))
FAILS, OKS = [], [0]


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


def t25():
    return tmod("test_skyyskills_0.4.25.py", "t0425")


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
    migs = ["ManaMig", "HealMig", "DocMig", "ClassManaMig", "SkillLvMig", "KillXpMig", "AcroMig", "PerkMig"]

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
        R["xp1"] = s1.get("xp.properties", b"").decode("latin-1")
        R["players_same"] = all(s0.get(k) == s1.get(k) == s2.get(k) for k in set(s0) | set(s1) | set(s2) if k.startswith("players/"))
        pc = JClass(PKG + "PerkCfg")
        R["fortMax"] = float(pc.FORT_MAX) if mode == "new" else None
        R["ddMax"] = float(pc.DD_MAX)
    except Exception:
        import traceback
        R["error"] = traceback.format_exc()[-3000:]
    json.dump(R, open(out, "w"), indent=1)


# ============================================================================================ child: the behaviour (new jar)
def run_unit(jar, fake, out):
    from jpype import JClass, JFloat, JArray, JInt, JLong, JDouble, JImplements, JOverride, JObject
    T = t15()
    res, path = T.common(jar, [fake])
    R = {"load_fails": res["load_fails"]}
    if res["load_fails"]:
        json.dump(R, open(out, "w"), indent=1)
        return
    E = T.regen_env()
    U = E["U"]

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
    Cfg, Store, Defs, Perks, SBn, PCfg, BCfg = J("SkillCfg"), J("SkillStore"), J("SkillDefs"), J("Perks"), J("SkillBonus"), J("PerkCfg"), J("BridgeCfg")
    CPw, SDef, Sickle = J("ClassPower"), J("SkillDef"), J("Sickle")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    UUID, HM, CHM = JClass("java.util.UUID"), JClass("java.util.HashMap"), JClass("java.util.concurrent.ConcurrentHashMap")
    JObj, JBool, JStr, JDbl, JLng = JClass("java.lang.Object"), JClass("java.lang.Boolean"), JClass("java.lang.String"), JClass("java.lang.Double"), JClass("java.lang.Long")
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    BTY = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    IPE = JClass("com.hypixel.hytale.server.core.event.events.ecs.InteractivelyPickupItemEvent")
    bridge = Store.bridge()
    # ItemStack(id, n) needs an Item store: an empty one (every id -> Item.UNKNOWN, the 0.4.15 harness way)
    _am = alloc(JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap"))
    setany(_am, "assetMap", HM())
    setany(_am, "assetMapLock", JClass("java.util.concurrent.locks.StampedLock")())
    _ist = alloc(JClass("skyytest.FakeAssetStore"))
    setany(_ist, "assetMap", _am)
    setstatic(JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item"), "ASSET_STORE", _ist)
    work = os.path.join(SCRATCH, "unit")
    os.makedirs(os.path.join(work, "players"), exist_ok=True)
    Cfg.FILE = path(os.path.join(work, "xp.properties"))
    R["load"] = str(Cfg.load())
    dflt = open(os.path.join(work, "xp.properties"), "rb").read().decode("latin-1")
    Store.DIR = path(os.path.join(work, "players"))
    Store.DATA.clear()
    X = {}
    try:
        X["fresh"] = ("\nperk.doubleDropMax=1.0\n# fortuneMax (0.4.26): " in dflt) and ("\nperk.fortuneMax=2.0\n" in dflt)
        X["fortMax"] = float(PCfg.FORT_MAX)
        # ---- extras (pure)
        X["extras"] = [int(Perks.extras(JDouble(t), JDouble(r))) for t, r in ((0.0, 0.0), (0.5, 0.49), (0.5, 0.5), (1.5, 0.2), (1.5, 0.7), (1.0, 0.999),
                                                                               (2.0, 0.99), (float("nan"), 0.1), (15.0, 0.1), (-1.0, 0.0))]
        u = UUID(0x426, 1)
        FOR, MIN, FARM = int(Defs.FARMING) - 1, 0, int(Defs.FARMING)
        key = "skill:bonus:" + str(u)

        def srcs(**kw):
            bridge.remove(key)
            if not kw:
                return
            m = CHM()
            for k, v in kw.items():
                hm = HM()
                for kk, vv in v.items():
                    hm.put(kk, JDbl(vv) if isinstance(vv, float) else vv)
                m.put(k, JClass("java.util.Collections").unmodifiableMap(hm))
            bridge.put(key, m)

        def fo(lvl, row=FOR):
            return round(float(Perks.fortune(u, JInt(row), JInt(lvl))), 9)

        def cu(lvl, row=FOR):
            return round(float(Perks.chanceU(u, JInt(row), JInt(lvl))), 9)
        same = []
        for case in ({}, {"trees": {"dd.foraging": 0.3}}, {"trees": {"dd.foraging": 0.9}}, {"trees": {"dd.mining": 0.4}},
                     {"trees": {"dd.foraging": 0.3}, "acc": {"dd.foraging": 0.2}}):
            srcs(**case)
            for lvl in (0, 1, 40, 100):
                same.append((str(case), lvl, fo(lvl), cu(lvl)))
        X["same_as_0425"] = [s for s in same if s[2] != s[3]]
        X["same_n"] = len(same)
        srcs(gear={"dd.foraging": 0.5})
        X["g50"] = fo(0)
        srcs(gear={"dd.foraging": 1.5})
        X["g150"] = fo(0)
        srcs(gear={"dd.foraging": 1.5}, trees={"dd.foraging": 0.8})
        X["g150_full"] = fo(100)            # base min(0.5 + 0.8, 1.0) = 1.0 + 1.5 = 2.5 -> cap 2.0
        srcs(gear={"dd.foraging": 0.4}, trees={"dd.foraging": 0.8})
        X["base_cap"] = fo(100)             # base 1.3 -> 1.0, + 0.4 = 1.4
        PCfg.FORT_MAX = 1.0
        srcs(gear={"dd.foraging": 0.5}, trees={"dd.foraging": 0.5})
        X["cap1"] = fo(40)                  # base 0.7 + 0.5 -> 1.0
        PCfg.FORT_MAX = 0.5
        X["cap_low"] = fo(40)               # a cap below the old chance never cuts it: 0.7
        PCfg.FORT_MAX = 2.0
        srcs(gear={"dd.mining": 0.9})
        X["other_row"] = [fo(0), fo(0, MIN)]
        srcs(gear={"dd.foraging": float("nan")}, trees={"dd.foraging": -0.3})
        X["nan"] = fo(40)
        srcs(gear={"dd.foraging": 0.5}, trees={"dd.foraging": 0.3})
        BCfg.BONUS = False
        X["bonus_off"] = [fo(40), cu(40)]
        BCfg.BONUS = True
        X["split"] = [round(float(SBn.ddOf(u, JInt(FOR), "gear")), 9), round(float(SBn.ddExcept(u, JInt(FOR), "gear")), 9),
                      round(float(SBn.ddOf(u, JInt(FOR), "trees")), 9), round(float(SBn.ddOf(u, JInt(FOR), None)), 9)]
        # ---- fix round (critic B1): the tool's only.<skill> filter - a shovel (Soil_) never on stone / ore, a pickaxe (Rock_,Rubble_,Ore_) never on sand
        def f4(fam, lvl=0, row=MIN):
            return round(float(Perks.fortune(u, JInt(row), JInt(lvl), fam)), 9)
        srcs(gear={"dd.mining": 0.9, "only.mining": "Soil_"})
        X["only_shovel"] = [f4("Rock_Stone"), f4("Ore_Iron_Stone"), f4("Soil_Sand"), f4("Soil_Gravel"), f4(None), fo(0, MIN),
                            sorted(set(int(Perks.rolls(u, JInt(MIN), JInt(0), "Ore_Iron_Stone")) for _ in range(200))), str(SBn.onlyOf(u, JInt(MIN), "gear"))]
        srcs(gear={"dd.mining": 0.9, "only.mining": "Rock_,Rubble_,Ore_"})
        X["only_pick"] = [f4("Rock_Stone"), f4("Ore_Iron_Stone"), f4("Rubble_Stone"), f4("Soil_Sand")]
        srcs(gear={"dd.mining": 0.9, "only.mining": "  "})
        X["only_blank"] = [f4("Soil_Sand"), SBn.onlyOf(u, JInt(MIN), "gear") is None]
        # ---- fix round (critics A1/B2): an admin's doubleDropMax below 1 stays a hard cap with a tool; fortuneMax only while it is 1
        srcs(gear={"dd.foraging": 0.25}, trees={"dd.foraging": 0.1})
        PCfg.DD_MAX = 0.3
        X["admin_cap"] = [fo(40), cu(40)]          # base 0.2 + 0.1 = 0.3 (the cap); + 0.25 tool -> still 0.3 (0.4.26 first build: 0.55)
        PCfg.DD_MAX = 0.5
        X["admin_cap5"] = [fo(40), cu(40)]         # base 0.3 + 0.25 = 0.55 -> 0.5 (chanceU, which counts every source, also 0.5)
        PCfg.DD_MAX = 1.0
        X["admin_cap_def"] = fo(40)                # 0.3 + 0.25 = 0.55 (fortuneMax 2 applies)
        # ---- rolls statistics (Fortune 0 / 50 / 150 / 250; level 0 = no perk part)
        st = {}
        for name, g in (("f0", None), ("f50", 0.5), ("f150", 1.5), ("f250", 2.5)):
            if g is None:
                srcs()
            else:
                srcs(gear={"dd.foraging": g})
            n0 = int(Perks.FN[0])
            vs = [int(Perks.rolls(u, JInt(FOR), JInt(0), "Wood_Oak_Trunk")) for _ in range(3000)]
            st[name] = {"vals": sorted(set(vs)), "mean": sum(vs) / 3000.0, "counted": int(Perks.FN[0]) - n0}
        srcs(gear={"dd.foraging": 1.5})
        st["branch"] = sorted(set(int(Perks.rolls(u, JInt(FOR), JInt(0), "Wood_Oak_Branch")) for _ in range(200)))
        st["farm_any"] = sorted(set(int(Perks.rolls(u, JInt(FARM), JInt(0), "Plant_Crop_Wheat_Block")) for _ in range(200)))
        X["rolls"] = st
        # ---- the roll sites on real engine objects
        pr = alloc(PRef)
        setany(pr, "uuid", u)
        setany(pr, "username", "Fortune")
        bt = alloc(BTY)
        setany(bt, "id", "Wood_Oak_Trunk")
        f2 = int(Perks.FN[2])
        Perks.breakDouble(None, JInt(FOR), None, "w", False)
        Perks.breakDouble(pr, JInt(FOR), bt, "w", False)
        X["placed"] = [int(Perks.FN[2]) - f2, bool(Perks.DD_FAILED_ONCE)]
        srcs(gear={"dd.foraging": 1.5})
        a0, a1 = int(Perks.FN[0]), int(Perks.FN[1])
        for _ in range(50):
            Perks.breakDouble(pr, JInt(FOR), bt, "w", True)
        X["break"] = [int(Perks.FN[0]) - a0, int(Perks.FN[1]) - a1, bool(Perks.DD_FAILED_ONCE)]
        btc = alloc(BTY)
        setany(btc, "id", "Plant_Crop_Wheat_Block")
        srcs(gear={"dd.farming": 1.0})
        a0, a1 = int(Perks.FN[0]), int(Perks.FN[1])
        for _ in range(20):
            Perks.harvestDouble(pr, btc, "w")
        X["harvest"] = [int(Perks.FN[0]) - a0, int(Perks.FN[1]) - a1, bool(Perks.DD_FAILED_ONCE)]
        ks = HM()
        ks.put("Plant_Crop_Wheat_Item", JArray(JObj)([JLng(0), JBool.FALSE, JStr("Plant_Crop_Wheat_Block"), None]))
        Sickle.KEYS = ks
        ictor = [c for c in IPE.class_.getConstructors() if len(c.getParameterTypes()) == 1][0]
        evs = JClass("java.util.ArrayList")()
        evs.add(ictor.newInstance(JArray(JObj)([IS("Plant_Crop_Wheat_Item", JInt(2))])))
        srcs(gear={"dd.farming": 1.5})
        a0, a1 = int(Perks.FN[0]), int(Perks.FN[1])
        paid = [int(Sickle.award(pr, evs, "w")) for _ in range(20)]
        X["sickle"] = [sum(paid), int(Perks.FN[0]) - a0, int(Perks.FN[1]) - a1, bool(Perks.DD_FAILED_ONCE)]
        srcs()
        X["sickle_nofortune"] = [int(Sickle.award(pr, evs, "w")), int(Perks.FN[1]) - a1]
    except Exception:
        import traceback
        X["error"] = traceback.format_exc()[-3000:]
    R["X"] = X
    # ================================================================ G: skill:dmg:<uuid>
    G = {}
    try:
        CT = JClass("com.hypixel.hytale.component.ComponentType")
        Ref = JClass("com.hypixel.hytale.component.Ref")
        Universe = JClass("com.hypixel.hytale.server.core.universe.Universe")
        EMc = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
        ESM, ESV = E["ESM"], E["ESV"]
        EST = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType")
        DST = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes")
        ILT = JClass("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap")
        JAWM = JClass("com.hypixel.hytale.assetstore.map.JsonAssetWithMap")
        MapStore, FakeCB, FakeAS = JClass("skyytest.MapStore"), JClass("skyytest.FakeCB"), JClass("skyytest.FakeAssetStore")
        uni = alloc(Universe)
        setstatic(Universe, "instance", uni)
        setany(uni, "playerRefComponentType", alloc(CT))
        em = EMc.get()
        for fname in ("playerComponentType", "hotbarInventoryComponentType", "toolInventoryComponentType"):
            setany(em, fname, alloc(CT))

        def stype(id_, mn, mx):
            t = alloc(EST)
            setany(t, "id", id_)
            setany(t, "min", JFloat(mn))
            setany(t, "max", JFloat(mx))
            return t
        amap = alloc(ILT)
        setany(amap, "array", JArray(JAWM)([stype("Health", 0.0, 100.0), stype("Mana", 0.0, 0.0), stype("Stamina", -4.0, 10.0)]))
        fst = alloc(FakeAS)
        setany(fst, "assetMap", amap)
        setstatic(EST, "ASSET_STORE", fst)
        for nm, ix in (("HEALTH", 0), ("MANA", 1), ("STAMINA", 2)):
            setstatic(DST, nm, JInt(ix))

        def statmap():
            m = ESM()
            vals = []
            for idx, nm, v, mn in ((0, "Health", 100.0, 0.0), (1, "Mana", 0.0, 0.0), (2, "Stamina", 10.0, -4.0)):
                sv = alloc(ESV)
                for fn_, val in (("id", nm), ("index", JInt(idx)), ("value", JFloat(v)), ("min", JFloat(mn)), ("max", JFloat(v))):
                    setany(sv, fn_, val)
                vals.append(sv)
            setany(m, "values", JArray(ESV)(vals))
            return m

        def fakecb(m):
            cb = alloc(FakeCB)
            cb.stats, cb.statsType, cb.dd, cb.ddType = m, E["statsType"], None, E["ddType"]
            cb.arch = E["Arch"].empty()
            return cb

        @JImplements("java.util.function.Function")
        class Const(object):
            def __init__(self, v):
                self.v = v

            @JOverride
            def apply(self, o):
                return self.v
        bridge.put("class:fn:allowed", Const(JBool.TRUE))
        ECUM = [int(x) for x in Defs.ECUM]
        u2 = UUID(0x426, 2)
        open(os.path.join(work, "players", str(u2) + ".properties"), "wb").write(("name=T\nCombat.Warrior=%d\nCombat.Warrior.paid=50\n" % ECUM[50]).encode("latin-1"))
        for k in ("profile:class:", "class:"):
            bridge.put(k + str(u2), "Warrior")
        G["dmgPct"] = round(float(CPw.dmgPct(u2, Store.data(u2))), 6)
        G["boost"] = round(float(CPw.boost(JInt(6), "Warrior", JInt(50))), 6)
        G["boostDmg"] = round(float(CPw.boostDmg(J("SkillClass").slotOfClass("Warrior"), JInt(50))) * 100.0, 6)
        pr2 = alloc(PRef)
        setany(pr2, "uuid", u2)
        setany(pr2, "username", "Dmg")
        m = statmap()
        cb = fakecb(m)
        ref = Ref(alloc(MapStore), 0)
        J("Perks").tick(u2, pr2, cb, ref)
        bv = bridge.get("skill:dmg:" + str(u2))
        G["tick"] = None if bv is None else [str(bv.getClass().getName()), float(bv)]
        G["tick_failed"] = bool(J("Perks").FAILED_ONCE)
        for k in ("profile:class:", "class:"):
            bridge.remove(k + str(u2))
        J("Overall").SESS.put(u2, JArray(JObj)([pr2, JLng(int(JClass("java.lang.System").currentTimeMillis()) - 11000)]))
        J("Perks").tick(u2, pr2, cb, ref)
        G["tick_noclass"] = bridge.get("skill:dmg:" + str(u2)) is not None
        u3 = UUID(0x426, 3)
        SDef.setDmg(u3, JDouble(2.345))
        a = bridge.get("skill:dmg:" + str(u3))
        SDef.setDmg(u3, JDouble(float("nan")))
        b = bridge.get("skill:dmg:" + str(u3))
        SDef.setDmg(u3, JDouble(7.5))
        c = float(SDef.dmgOf(u3))
        SDef.setDmg(u3, JDouble(0.0))
        d = bridge.get("skill:dmg:" + str(u3))
        SDef.setDmg(u3, JDouble(4.0))
        SDef.retain(JClass("java.util.HashSet")())
        e = bridge.get("skill:dmg:" + str(u3))
        G["set"] = [None if a is None else float(a), b is None, c, d is None, e is None, int(SDef.DMGP.size())]
    except Exception:
        import traceback
        G["error"] = traceback.format_exc()[-3000:]
    R["G"] = G
    json.dump(R, open(out, "w"), indent=1)


# ============================================================================================ parent
def main():
    if "--mkfake" in sys.argv:
        return t15().run_mkfake(arg("--mkfake"))
    if "--mkfake25" in sys.argv:
        return t25().run_mkfake25(arg("--mkfake25"))
    if "--child" in sys.argv:
        return run_child(arg("--child"), arg("--out"))
    if "--start" in sys.argv:
        return run_start(arg("--start"), arg("--out"), arg("--mode"))
    if "--unit" in sys.argv:
        return run_unit(arg("--unit"), arg("--fake"), arg("--out"))
    if "--audit" in sys.argv:
        return t15().run_audit(arg("--audit"), arg("--fake"), arg("--out"))
    if "--compare" in sys.argv:
        m = t20()
        m.VERSION, m.PREV_VERSION = VERSION, PREV_VERSION
        return m.run_compare(arg("--compare"), arg("--prevjar"), arg("--out"))
    for j in (JAR, PREV_JAR):
        if not os.path.isfile(j):
            sys.exit("no jar at %s - build it first" % j)
    sr = os.path.realpath(os.path.join(TOOLS, "dev", "scratch", "tools01fix2"))
    if not os.path.realpath(SCRATCH).startswith(sr + os.sep):
        sys.exit("--dir must be inside tools/dev/scratch/tools01fix2 (deleted afterwards), not %s" % SCRATCH)
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.makedirs(env["TEMP"], exist_ok=True)
    live_snap = dict((os.path.relpath(os.path.join(r, f), LIVE_DIR), os.path.getmtime(os.path.join(r, f))) for r, ds, fs in os.walk(LIVE_DIR) for f in fs)
    me = os.path.abspath(__file__)
    fake = os.path.join(SCRATCH, "fake")
    try:
        p = subprocess.run([sys.executable, me, "--mkfake", fake, "--dir", SCRATCH], env=env, capture_output=True)
        p2 = subprocess.run([sys.executable, me, "--mkfake25", fake, "--dir", SCRATCH], env=env, capture_output=True)
        check(p.returncode == 0 and p2.returncode == 0, "the stand-in classes were generated: %s %s" % (p.stderr[-300:], p2.stderr[-300:]))
        outs = {}
        for mode, jar in (("prev", PREV_JAR), ("new", JAR)):
            outp = os.path.join(SCRATCH, "run-%s.json" % mode)
            with open(os.path.join(SCRATCH, "run-%s.log" % mode), "wb") as lf:
                p = subprocess.run([sys.executable, me, "--child", jar, "--out", outp, "--dir", SCRATCH], env=env, stdout=lf, stderr=subprocess.STDOUT)
            check(p.returncode == 0 and os.path.isfile(outp), "A: child JVM (%s) ran" % mode)
            if os.path.isfile(outp):
                outs[mode] = json.load(open(outp))
                r = outs[mode]
                check(not r["load_fails"] and r["loaded"] == r["classes"], "A (%s): %d / %d classes load under -Xverify:all %s" % (mode, r["loaded"], r["classes"], r["load_fails"][:3]))
        # J
        jz, jp = zipfile.ZipFile(JAR), zipfile.ZipFile(PREV_JAR)
        nn, pn = set(n for n in jz.namelist() if not n.endswith(".class")), set(n for n in jp.namelist() if not n.endswith(".class"))
        changed = sorted(n for n in nn & pn if n != "manifest.json" and jz.read(n) != jp.read(n))
        mn_, mp_ = json.loads(jz.read("manifest.json")), json.loads(jp.read("manifest.json"))
        mdiff = sorted(k for k in set(mn_) | set(mp_) if mn_.get(k) != mp_.get(k))
        check(nn == pn and not changed and set(mdiff) <= {"Name", "Version", "Description"} and mn_["Version"] == VERSION,
              "J: the asset files = 0.4.25's (added %s gone %s changed %s); manifest differs in %s" % (sorted(nn - pn)[:3], sorted(pn - nn)[:3], changed[:3], mdiff))
        # M
        sts = {}
        for mode, jar in (("prev", PREV_JAR), ("new", JAR)):
            shutil.copytree(LIVE_DIR, os.path.join(SCRATCH, "live-copy-" + mode))
            outs_ = os.path.join(SCRATCH, "start-%s.json" % mode)
            with open(os.path.join(SCRATCH, "start-%s.log" % mode), "wb") as lf:
                p = subprocess.run([sys.executable, me, "--start", jar, "--out", outs_, "--mode", mode, "--dir", SCRATCH], env=env, stdout=lf, stderr=subprocess.STDOUT)
            check(p.returncode == 0 and os.path.isfile(outs_), "M: start-twice child JVM (%s) ran" % mode)
            if os.path.isfile(outs_):
                sts[mode] = json.load(open(outs_))
                check("error" not in sts[mode], "M (%s): no error %s" % (mode, sts[mode].get("error", "")[-800:]))
        if "new" in sts and "prev" in sts and "error" not in sts["new"] and "error" not in sts["prev"]:
            sn, sp = sts["new"], sts["prev"]
            check(sn["changed1"] == sp["changed1"] and sn["xp1"] == sp["xp1"], "M: start 1 of 0.4.26 changes exactly what 0.4.25's does (%s vs %s)" % (sn["changed1"], sp["changed1"]))
            check(sn["changed2"] == [] and sn["players_same"], "M: start 2 changes nothing; player files untouched (%d files)" % sn["files"])
            check(sn["fortMax"] == 2.0 and "perk.fortuneMax" not in sn["xp1"] and sn["ddMax"] == sp["ddMax"],
                  "M: the live file has no perk.fortuneMax line and reads its default 2.0 (no one-time update); doubleDropMax unchanged %s" % sn["ddMax"])
            print("M. start twice on the live copy: start 1 changed %s (same as 0.4.25), start 2 nothing" % sn["changed1"])
        # X + G
        uo = os.path.join(SCRATCH, "unit.json")
        with open(os.path.join(SCRATCH, "unit.log"), "wb") as lf:
            p = subprocess.run([sys.executable, me, "--unit", JAR, "--fake", fake, "--out", uo, "--dir", SCRATCH], env=env, stdout=lf, stderr=subprocess.STDOUT)
        check(p.returncode == 0 and os.path.isfile(uo), "behaviour child JVM ran (log %s)" % os.path.join(SCRATCH, "unit.log"))
        if os.path.isfile(uo):
            R = json.load(open(uo))
            X, G = R.get("X", {}), R.get("G", {})
            check(not R.get("load_fails") and "error" not in X and "error" not in G, "X/G ran: %s %s" % (X.get("error", "")[-1500:], G.get("error", "")[-1500:]))
            if "error" not in X:
                check(X["fresh"] and X["fortMax"] == 2.0, "X: the fresh xp.properties lists perk.fortuneMax=2.0 (+ its comment) under perk.doubleDropMax; default read 2.0")
                check(X["extras"] == [0, 1, 0, 2, 1, 1, 2, 0, 10, 0], "X: extras 0 / 0.5 (r .49 -> 1, .5 -> 0) / 1.5 (2 or 1) / 1.0 / 2.0 / NaN / 15 -> 10 / -1: %s" % X["extras"])
                check(not X["same_as_0425"] and X["same_n"] == 20,
                      "X: without a gear source fortune = 0.4.25's chanceU in all %d cases (no key, trees, other skill, two sources): %s" % (X["same_n"], X["same_as_0425"][:3]))
                check(X["g50"] == 0.5 and X["g150"] == 1.5 and X["g150_full"] == 2.0 and X["base_cap"] == 1.4,
                      "X: Fortune 50 -> 0.5, 150 -> 1.5, full perk + trees + 150 -> the 2.0 cap, base capped at doubleDropMax first (1.4): %s %s %s %s" % (
                          X["g50"], X["g150"], X["g150_full"], X["base_cap"]))
                check(X["cap1"] == 1.0 and X["cap_low"] == 0.7, "X: fortuneMax 1 -> 1.0; a cap below the old chance never cuts it (0.7): %s %s" % (X["cap1"], X["cap_low"]))
                check(X["other_row"] == [0.0, 0.9] and X["nan"] == 0.2 and X["bonus_off"] == [0.2, 0.2],
                      "X: a mining tool's Fortune never reaches foraging; NaN / negative ignored; bridge.bonus off = the level perk only: %s %s %s" % (
                          X["other_row"], X["nan"], X["bonus_off"]))
                check(X["split"] == [0.5, 0.3, 0.3, 0.0], "X: ddOf / ddExcept split the sources: %s" % X["split"])
                check(X["only_shovel"] == [0.0, 0.0, 0.9, 0.9, 0.0, 0.0, [0], "Soil_"],
                      "X: fix B1 - a shovel's Fortune (only.mining Soil_) counts on sand / gravel only, never stone / ore / no block: %s" % X["only_shovel"])
                check(X["only_pick"] == [0.9, 0.9, 0.9, 0.0], "X: fix B1 - a pickaxe's Fortune counts on rock / ore / rubble, not sand: %s" % X["only_pick"])
                check(X["only_blank"] == [0.9, True], "X: a blank only.<skill> = no filter: %s" % X["only_blank"])
                check(X["admin_cap"] == [0.3, 0.3] and X["admin_cap5"] == [0.5, 0.5] and X["admin_cap_def"] == 0.55,
                      "X: fix A1/B2 - doubleDropMax 0.3 stays a hard cap with a tool (0.3), 0.5 caps the tool total at 0.5, at 1.0 fortuneMax applies (0.55): %s %s %s" % (
                          X["admin_cap"], X["admin_cap5"], X["admin_cap_def"]))
                rs = X["rolls"]
                check(rs["f0"]["vals"] == [0] and rs["f0"]["counted"] == 0, "X: Fortune 0 -> never an extra drop (no roll counted): %s" % rs["f0"])
                check(rs["f50"]["vals"] == [0, 1] and 0.45 <= rs["f50"]["mean"] <= 0.55, "X: Fortune 50 -> 0 or 1, mean %.3f" % rs["f50"]["mean"])
                check(rs["f150"]["vals"] == [1, 2] and 1.45 <= rs["f150"]["mean"] <= 1.55, "X: Fortune 150 -> 1 sure + 50%% a second, mean %.3f" % rs["f150"]["mean"])
                check(rs["f250"]["vals"] == [2] and rs["f250"]["counted"] == 3000, "X: Fortune 250 -> capped at 2 extra drops every time: %s" % rs["f250"]["vals"])
                check(rs["branch"] == [0] and rs["farm_any"] == [0], "X: doubleDropOnly=_Trunk: a branch never; a dd.foraging tool gives Farming nothing: %s %s" % (rs["branch"], rs["farm_any"]))
                check(X["placed"] == [2, False], "X: breakDouble on a PLACED block (tracked false) never rolls - counted twice, no failure: %s" % X["placed"])
                check(X["break"][0] == 50 and 50 <= X["break"][1] <= 100 and 60 <= X["break"][1] and not X["break"][2],
                      "X: the REAL breakDouble with Fortune 150: 50 rolls, %d extra drops (1-2 each), no failure" % X["break"][1])
                check(X["harvest"] == [20, 20, False], "X: the REAL harvestDouble with Fortune 100: one sure extra each (%s)" % X["harvest"])
                check(X["sickle"][0] == 20 and X["sickle"][1] == 20 and 20 <= X["sickle"][2] <= 40 and not X["sickle"][3] and X["sickle_nofortune"] == [1, X["sickle"][2]],
                      "X: the REAL Sickle.award (a real InteractivelyPickupItemEvent): 20 crops paid, 20 rolls, %d extras; no Fortune -> none: %s" % (X["sickle"][2], X["sickle_nofortune"]))
            if "error" not in G:
                check(G["dmgPct"] == G["boost"] == G["boostDmg"] == 2.5, "G: dmgPct = the class balance table 6 at Warrior 50 = boostDmg x 100 = 2.5: %s" % G)
                check(G["tick"] == ["java.lang.Double", 2.5] and not G["tick_failed"] and not G["tick_noclass"],
                      "G: the REAL Perks.tick publishes skill:dmg:<uuid> = Double 2.5 and removes it without a class: %s %s" % (G["tick"], G["tick_noclass"]))
                check(G["set"] == [2.35, True, 7.5, True, True, 0], "G: setDmg rounds (2.345 -> 2.35), NaN / 0 remove, retain drops a gone player: %s" % G["set"])
        # F
        cmpo = os.path.join(SCRATCH, "compare.json")
        pc = subprocess.run([sys.executable, me, "--compare", JAR, "--prevjar", PREV_JAR, "--out", cmpo, "--dir", SCRATCH], env=env, capture_output=True)
        check(pc.returncode == 0 and os.path.isfile(cmpo), "F: class compare child ran: %s" % pc.stderr[-500:])
        if os.path.isfile(cmpo):
            cmp_ = json.load(open(cmpo))
            added = sorted(k for k, v in cmp_.items() if v == "only in new")
            gone = sorted(k for k, v in cmp_.items() if v == "only in prev")
            chg = sorted(k for k, v in cmp_.items() if isinstance(v, dict))
            allowed = {"SkyySkillsPlugin", "PerkCfg", "Perks", "SkillBonus", "ClassPower", "SkillDef", "Sickle", "CfgRows", "SkillCfg", "SkillKit"}
            check(not added and not gone and set(chg) <= allowed and {"Perks", "SkillBonus", "ClassPower", "SkillDef", "Sickle", "PerkCfg"} <= set(chg),
                  "F: class compare 0.4.25 -> 0.4.26: added %s, gone %s, changed %s" % (added, gone, chg))
            print("F. class compare: changed %s" % ", ".join(chg))
            for c in chg:
                print("   %s: %s" % (c, ", ".join(m.split("(")[0] for m in cmp_[c]["methods"])[:300]))
        # AU
        auo = os.path.join(SCRATCH, "audit.json")
        pa = subprocess.run([sys.executable, me, "--audit", JAR, "--fake", fake, "--out", auo, "--dir", SCRATCH], env=env, capture_output=True)
        check(pa.returncode == 0 and os.path.isfile(auo), "AU: engine-access audit child ran: %s" % pa.stderr[-500:])
        if os.path.isfile(auo):
            au = json.load(open(auo))
            check(au["refused"] == [] and au["control"] and au["refs"] > 1000, "AU: %d references in %d classes, refused %s; control refused: %s" % (
                au["refs"], au["classes"], au["refused"][:3], bool(au["control"])))
            print("AU. engine-access audit: %d references, %d refused (control refused: %s)" % (au["refs"], len(au["refused"]), bool(au["control"])))
        live_after = dict((os.path.relpath(os.path.join(r, f), LIVE_DIR), os.path.getmtime(os.path.join(r, f))) for r, ds, fs in os.walk(LIVE_DIR) for f in fs)
        check(live_after == live_snap, "the live Skyy_SkyySkills folder was never written (only read + copied)")
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyySkills %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
