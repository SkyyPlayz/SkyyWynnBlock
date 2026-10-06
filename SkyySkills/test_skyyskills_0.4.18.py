"""SkyySkills 0.4.18 - bare-JVM harness for THE DODGE ROLL (tools/skills_0_4_18_patch.py; research/Grapple-Bolt-Spec.md 1.2 / 2.5 / 3.2 / 5)
and the built-in kit table fix. The new parts run on the REAL classes of the 0.4.18 jar and the REAL engine classes (HytaleServer.jar on
the class path, -Xverify:all); the live save data is only ever READ and copied into the scratch folder. Everything 0.4.17 already checked
is guarded by the class compare (section F: only the planned classes differ from the SET pin 0.4.17 beyond the version string) - run
SkyySkills/test_skyyskills_0.4.17.py for the older parts.

    python SkyySkills/test_skyyskills_0.4.18.py [--jar <SkyySkills-0.4.18.jar>] [--prev <SkyySkills-0.4.17.jar>] [--dir <scratch>]
                                                [--live <Skyy_SkyySkills folder>] [--keep]

SECTIONS
  A   every class of the jar loads under -Xverify:all (both jars)
  J   the 11 asset files (Python, against Assets.zip read in memory): Dodge.json = vanilla + the 9 branches, every roll body = the vanilla
      Dodge_Left body with only the effect + Direction changed, the 4 effects, the i-frames effect vanilla, the 0.4.17 files untouched
  E   the ENGINE executes the mapping: the jar's Dodge.json decoded by the engine's own Interaction codec (Condition outer, MovementCondition
      inner - no unknown keys), MovementConditionInteraction.compile on a real OperationsBuilder, then tick0 for EVERY MovementDirection
      (None + 8) on a real InteractionContext / InteractionEntry / InteractionChain -> the jumped-to operation = the expected interaction;
      every roll body (StatsConditionWithModifier: Stamina 2, modifier Dodge), each ApplyEffect / ApplyForce step and the 4 effects +
      Dodge_Invulnerability decoded by the engine codecs = vanilla's decode except the direction / effect (i-frames: Invulnerable true,
      0.25 s on every roll; air: the outer Condition only says Flying false, ApplyForce WaitForGround false)
  X   Acro.dodge EXECUTED on the real class (stand-in store / command buffer, the real EffectControllerComponent, the real EntityEffect
      asset map, real Velocity): each of the 4 roll effects pays acro.dodgeXp once (edge + cooldown) and gets the Acrobatics + tree push
      along the client velocity 100 ms later; control effect / excluded state / creative; air roll (excludedState of an airborne
      MovementStates = false) pays; the 0.4.17 jar (control child) pays ONLY Left / Right
  KF  the ManaGuard kit fallback = SkyyClasses 0.1.12's default kits (Warrior + Wood Shield)
  M   START TWICE on a scratch copy of the live data, both jars: 0.4.18 writes exactly what 0.4.17 writes (no new migration); start 2 = nothing
  KC  the read-only acro.roll row through the REAL config kit (get = the text, set refused) + the acro.dodgeXp help
  F   class compare 0.4.17 -> 0.4.18 (version string normalised): only the planned classes differ; + exactly the 11 asset files
  AU  the engine-access audit (every bytecode reference looked up with the JVM's own access rules; control refused)
"""
import os, sys, re, json, math, shutil, subprocess, zipfile, copy, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, PREV_VERSION = "0.4.18", "0.4.17"
PKG = "com.skyy.skills."
ACROBATICS = 4
D7 = 0.7071
# (MovementCondition key, interaction id, X, Z, effect) - the spec 1.2 table (forward = Z -1, vanilla left = X -1)
ROLLS = [("Forward", "SkyySkills_Roll_Forward", 0, -1, "Dodge_Forward"),
         ("ForwardLeft", "SkyySkills_Roll_ForwardLeft", -D7, -D7, "Dodge_Forward"),
         ("ForwardRight", "SkyySkills_Roll_ForwardRight", D7, -D7, "Dodge_Forward"),
         ("Back", "SkyySkills_Roll_Back", 0, 1, "Dodge_Back"),
         ("BackLeft", "SkyySkills_Roll_BackLeft", -D7, D7, "Dodge_Back"),
         ("BackRight", "SkyySkills_Roll_BackRight", D7, D7, "Dodge_Back")]
FX = {"Dodge_Left": "RollLeft", "Dodge_Right": "RollRight", "Dodge_Forward": "Roll", "Dodge_Back": "RollBackward"}
# MovementDirection (engine enum) -> the interaction it must run (Skyy: standing still = roll back)
EXPECT = {"None": "SkyySkills_Roll_Back", "Forward": "SkyySkills_Roll_Forward", "Back": "SkyySkills_Roll_Back", "Left": "Dodge_Left",
          "Right": "Dodge_Right", "ForwardLeft": "SkyySkills_Roll_ForwardLeft", "ForwardRight": "SkyySkills_Roll_ForwardRight",
          "BackLeft": "SkyySkills_Roll_BackLeft", "BackRight": "SkyySkills_Roll_BackRight"}
ROLL_TEXT = "8-way roll, 13 force, 2 Stamina, 0.25 s safe - fixed in the jar"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "skills0418", "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
PREV_JAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyySkills-%s.jar" % PREV_VERSION)))
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
LIVE_DIR = os.path.abspath(arg("--live", os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyySkills")))
ASSETS = os.path.join(APPDATA, "Hytale", "install", "release", "package", "game", "latest", "Assets.zip")
KEEP = "--keep" in sys.argv
FAILS, OKS, GUARD_OK = [], [0], [False]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def t15():
    """the 0.4.15 harness module (its stand-in generator, JVM start, class loader and the access audit) - imported, never run"""
    spec = importlib.util.spec_from_file_location("t0415", os.path.join(HERE, "test_skyyskills_0.4.15.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.SCRATCH = SCRATCH
    return m


# ============================================================================================ child: own stand-in (javassist)
def run_mkfake2(out_dir):
    """skyytest.DodgeCB: a CommandBuffer whose getComponent answers a Map Ref -> Map ComponentType -> Component (Acro.boost reads the
    Velocity through the command buffer)"""
    import jpype
    from jpype import JClass
    import skyybuild as B
    jpype.startJVM(B._jvm(), "-XX:-UsePerfData", classpath=[B.JAVASSIST], convertStrings=True)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    CtField, CtNewMethod, CtNewConstructor = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    c = cp.makeClass("skyytest.DodgeCB")
    c.setSuperclass(cp.get("com.hypixel.hytale.component.CommandBuffer"))
    c.addField(CtField.make("public java.util.Map comps;", c))
    c.addConstructor(CtNewConstructor.make("public DodgeCB() { super(null); }", c))
    c.addMethod(CtNewMethod.make("""public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.ComponentType t) {
  if (this.comps == null || r == null) return null;
  java.util.Map m = (java.util.Map) this.comps.get(r);
  return m == null ? null : (com.hypixel.hytale.component.Component) m.get(t);
}""", c))
    c.writeFile(out_dir)


# ============================================================================================ child: the JVM run (one jar)
def run_child(jar, out, fakes, mode):
    import jpype
    from jpype import JClass, JLong, JInt, JFloat, JDouble, JArray, JBoolean, JImplements, JOverride
    T = t15()
    res, path = T.common(jar, fakes)
    if res["load_fails"]:
        json.dump(res, open(out, "w"), indent=1)
        return
    D = res["data"]
    UUID, HM, IHM = JClass("java.util.UUID"), JClass("java.util.HashMap"), JClass("java.util.IdentityHashMap")
    JStr, JObj, Arr = JClass("java.lang.String"), JClass("java.lang.Object"), JClass("java.lang.reflect.Array")
    Cfg, Store, Acro, AcroCfg = JClass(PKG + "SkillCfg"), JClass(PKG + "SkillStore"), JClass(PKG + "Acro"), JClass(PKG + "AcroCfg")
    Hist, CLog, Rows = JClass(PKG + "CfgHist"), JClass(PKG + "CfgLog"), JClass(PKG + "CfgRows")
    HL = JClass("com.hypixel.hytale.logger.HytaleLogger")
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)
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

    def getany(obj, name):
        return findf(obj.getClass(), name).get(obj)

    def setstatic(cls, name, val):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        f.set(None, val)

    def alloc(cls):
        return U.allocateInstance(cls.class_)

    def safe(name, fn_):
        try:
            D[name] = fn_()
        except Exception:
            import traceback
            D[name] = {"error": traceback.format_exc()[-3000:]}
        print("[harness] section %s done" % name, flush=True)

    bridge = Store.bridge()
    Cfg.LOG = HL.get("SkyySkills")

    def fresh_store(players_dir):
        Store.DATA.clear()
        Store.DIRTY.clear()
        Store.QUIET.clear()
        Store.OWNER.clear()
        Store.PUBLISHED.clear()
        os.makedirs(players_dir, exist_ok=True)
        Store.DIR = path(players_dir)

    def load_cfg(d, text=None):
        f = os.path.join(d, "xp.properties")
        os.makedirs(d, exist_ok=True)
        if text is not None:
            open(f, "wb").write(text)
        elif os.path.exists(f):
            os.remove(f)
        Cfg.FILE = path(f)
        return str(Cfg.load())

    def snap(d):
        return dict((os.path.relpath(os.path.join(r, fn), d).replace(os.sep, "/"), open(os.path.join(r, fn), "rb").read())
                    for r, ds, fs in os.walk(d) for fn in fs)

    # ---------------------------------------------------------------- the engine registries (real classes, filled here)
    ILT = JClass("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap")
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    FAS = JClass("skyytest.FakeAssetStore")
    AC = JClass("com.hypixel.hytale.assetstore.codec.AssetCodec")
    iputm = ILT.class_.getDeclaredMethod("putAll", JStr.class_, AC.class_, JClass("java.util.Map").class_, JClass("java.util.Map").class_,
                                         JClass("java.util.Map").class_)
    iputm.setAccessible(True)
    codec = jpype.JProxy("com.hypixel.hytale.assetstore.codec.AssetCodec", dict={"getData": lambda a: None})
    EFX = JClass("com.hypixel.hytale.server.core.asset.type.entityeffect.config.EntityEffect")
    ICL = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.config.Interaction")
    SIM = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.config.SimpleInteraction")
    EST = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType")
    work = os.path.join(SCRATCH, "engine-" + mode)
    os.makedirs(work, exist_ok=True)

    def ilt_of(cls, objs, sub):
        @JImplements("java.util.function.IntFunction")
        class NewArr(object):
            @JOverride
            def apply(self, n):
                return Arr.newInstance(cls.class_, n)
        m = ILT(NewArr())
        a, p = JClass("java.util.LinkedHashMap")(), JClass("java.util.LinkedHashMap")()
        for k, v in objs.items():
            a.put(k, v)
            p.put(k, path(os.path.join(work, sub, k + ".json")))
        iputm.invoke(m, "Hytale:Hytale", codec, a, p, HM())
        st = alloc(FAS)
        setany(st, "assetMap", m)
        try:
            setany(st, "tClass", cls.class_)
        except Exception:
            pass
        return m, st

    EFFECT_IDS = ["Dodge_Left", "Dodge_Right", "Dodge_Forward", "Dodge_Back", "Dodge_Invulnerability", "Stamina_Broken"]
    fx_objs = dict((k, alloc(EFX)) for k in EFFECT_IDS)
    for k, v in fx_objs.items():
        try:
            setany(v, "id", k)
        except Exception:
            pass
    fmap, fstore = ilt_of(EFX, fx_objs, "effects")
    setstatic(EFX, "STORE", fstore)
    D["fx_index"] = dict((k, int(fmap.getIndex(k))) for k in EFFECT_IDS + ["Nope"])

    EMc = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
    em = alloc(EMc)
    for f in EMc.class_.getDeclaredFields():
        if Mod.isStatic(f.getModifiers()) and f.getType() == EMc.class_:
            f.setAccessible(True)
            f.set(None, em)
    CT = JClass("com.hypixel.hytale.component.ComponentType")
    eccT, velT = alloc(CT), alloc(CT)
    setany(em, "effectControllerComponentType", eccT)
    setany(em, "velocityComponentType", velT)

    # ================================================================ X: Acro.dodge executed
    def sec_X():
        R = {}
        R["load"] = load_cfg(os.path.join(SCRATCH, "x-cfg-" + mode))
        R["cfg"] = [float(AcroCfg.DODGE_XP), int(AcroCfg.DODGE_CD), bool(AcroCfg.DODGE_BOOST), float(AcroCfg.DODGE_FORCE), bool(AcroCfg.ENABLED)]
        fresh_store(os.path.join(SCRATCH, "x-players-" + mode))
        ECC = JClass("com.hypixel.hytale.server.core.entity.effect.EffectControllerComponent")
        AEE = JClass("com.hypixel.hytale.server.core.entity.effect.ActiveEntityEffect")
        VEL = JClass("com.hypixel.hytale.server.core.modules.physics.component.Velocity")
        Ref = JClass("com.hypixel.hytale.component.Ref")
        MapStore, DodgeCB = JClass("skyytest.MapStore"), JClass("skyytest.DodgeCB")
        MVT = JClass("com.hypixel.hytale.protocol.MovementStates")
        u = UUID(0xD0D6E, 18)
        d = JArray(JLong)(32)
        d[ACROBATICS] = JLong(10 ** 15)        # max Acrobatics level: the level push
        Store.DATA.put(str(u), d)
        tb = HM()
        tb.put("dodge.acrobatics", JClass("java.lang.Double").valueOf(0.05))
        sb = JClass("java.util.concurrent.ConcurrentHashMap")()
        sb.put("trees", tb)
        bridge.put("skill:bonus:" + str(u), sb)
        lvl = int(Store.level(u, ACROBATICS))
        f_exp = float(Acro.dodgeBonus(lvl)) + float(Acro.treeDodge(u))
        R["push_parts"] = [lvl, float(Acro.dodgeBonus(lvl)), float(Acro.treeDodge(u)), f_exp]

        def world(effect_id, vx=6.0, vz=-8.0):
            ref = alloc(Ref)
            ecc = ECC()
            if effect_id is not None:
                ecc.getActiveEffects().put(JInt(int(fmap.getIndex(effect_id))), alloc(AEE))
            st = alloc(MapStore)
            st.comps = IHM()
            m = IHM()
            m.put(eccT, ecc)
            st.comps.put(ref, m)
            vel = VEL()
            vel.setClient(JDouble(vx), JDouble(0.0), JDouble(vz))
            cb = alloc(DodgeCB)
            cb.comps = IHM()
            m2 = IHM()
            m2.put(velT, vel)
            cb.comps.put(ref, m2)
            return ref, ecc, st, cb, vel

        def instr(vel):
            out = []
            for ins in vel.getInstructions():
                v = None
                for nm in ("velocity", "vector", "value"):
                    try:
                        v = getany(ins, nm)
                        break
                    except Exception:
                        continue
                if v is None:
                    out.append(str(ins))
                else:
                    out.append([float(v.x()), float(v.y()), float(v.z())])
            return out

        def run(effect_id, creative=False, excluded=False):
            """one roll: the effect appears at t0 and stays 250 ms; ticks every 50 ms to t0+300, then off; a second roll at t0+350 (inside
            the 400 ms cooldown) and a third at t0+900 (after it)"""
            ref, ecc, st, cb, vel = world(effect_id)
            s = JArray(JDouble)(292)
            t0 = 1_000_000
            log = []
            idx = int(fmap.getIndex(effect_id)) if effect_id else None

            def tick(t, on):
                if idx is not None:
                    if on and not ecc.getActiveEffects().containsKey(JInt(idx)):
                        ecc.getActiveEffects().put(JInt(idx), alloc(AEE))
                    if not on:
                        ecc.getActiveEffects().remove(JInt(idx))
                Acro.dodge(s, st, cb, ref, u, JLong(t), JBoolean(creative), JBoolean(excluded))
                log.append([t - t0, float(s[11]), float(s[23]) - t0 if float(s[23]) > 0 else 0.0, float(s[6]), len(vel.getInstructions())])
            for k in range(0, 6):
                tick(t0 + 50 * k, True)            # 0..250: the effect is on
            tick(t0 + 300, False)
            tick(t0 + 350, True)                   # inside the cooldown
            tick(t0 + 400, True)
            tick(t0 + 450, False)
            tick(t0 + 900, True)                   # after the cooldown
            tick(t0 + 1050, True)
            tick(t0 + 1100, False)
            return {"log": log, "xp": float(s[11]), "push": instr(vel)}
        for e in ("Dodge_Left", "Dodge_Right", "Dodge_Forward", "Dodge_Back", "Stamina_Broken"):
            R[e] = run(e)
        R["creative_fwd"] = run("Dodge_Forward", creative=True)
        R["excluded_back"] = run("Dodge_Back", excluded=True)
        # air roll: an airborne MovementStates (jumping / falling, not on the ground) is no excluded state; flying / gliding are
        ms_air = MVT()
        for nm, v in (("onGround", False), ("jumping", True), ("falling", True)):
            try:
                setany(ms_air, nm, JBoolean(v))
            except Exception:
                pass
        ms_fly = MVT()
        setany(ms_fly, "flying", JBoolean(True))
        ms_glide = MVT()
        setany(ms_glide, "gliding", JBoolean(True))
        R["excluded"] = [bool(Acro.excludedState(ms_air)), bool(Acro.excludedState(ms_fly)), bool(Acro.excludedState(ms_glide)),
                         bool(Acro.excludedState(MVT())), bool(getany(ms_air, "onGround"))]
        R["air_fwd"] = run("Dodge_Forward", excluded=bool(Acro.excludedState(ms_air)))
        bridge.remove("skill:bonus:" + str(u))
        Store.DATA.remove(str(u))
        return R
    safe("X", sec_X)

    # ================================================================ KF: ManaGuard's built-in kit table
    def sec_KF():
        MG = JClass(PKG + "ManaGuard")
        return dict((str(c), str(MG.fbKit(c))) for c in MG.FB_CLS)
    safe("KF", sec_KF)

    # ================================================================ M: start twice on the live copy
    def start(d):
        Mig, HMig, DMig, CMig, LvMig, KMig = (JClass(PKG + "ManaMig"), JClass(PKG + "HealMig"), JClass(PKG + "DocMig"), JClass(PKG + "ClassManaMig"),
                                              JClass(PKG + "SkillLvMig"), JClass(PKG + "KillXpMig"))
        Curve, Own = JClass(PKG + "ClassCurve"), JClass(PKG + "OwnCurve")
        Cfg.FILE = path(os.path.join(d, "xp.properties"))
        fresh_store(os.path.join(d, "players"))
        Hist.DIR = None
        Rows.HOME = None
        CLog.FILE = None
        CLog.Q.clear()
        r = {"mana": [str(x) for x in Mig.run()], "heal": str(HMig.run()), "doc": str(DMig.run()), "cmig": str(CMig.run()), "lvmig": str(LvMig.run()),
             "kxmig": str(KMig.run())}
        r["load"] = str(Cfg.load())
        r["curve"] = str(Curve.start(path(d)))
        r["own"] = str(Own.start(path(d)))
        r["acro"] = [float(AcroCfg.DODGE_XP), int(AcroCfg.DODGE_CD), bool(AcroCfg.DODGE_BOOST)]
        return r

    def sec_M():
        R = {}
        lc = os.path.join(SCRATCH, "live-copy-" + mode)
        s0 = snap(lc)
        R["r1"] = start(lc)
        s1 = snap(lc)
        R["r2"] = start(lc)
        s2 = snap(lc)
        R["changed1"] = sorted(k for k in set(s0) | set(s1) if s0.get(k) != s1.get(k))
        R["changed2"] = sorted(k for k in set(s1) | set(s2) if s1.get(k) != s2.get(k))
        R["xp0"] = s0["xp.properties"].decode("latin-1")
        R["xp1"] = s1["xp.properties"].decode("latin-1")
        R["log_new"] = s1.get("config-changes.log", b"").decode("utf-8")[len(s0.get("config-changes.log", b"").decode("utf-8")):]
        R["players_same"] = all(s0.get(k) == s1.get(k) == s2.get(k) for k in set(s0) | set(s1) | set(s2) if k.startswith("players/"))
        return R
    safe("M", sec_M)

    if mode != "new":
        json.dump(res, open(out, "w"), indent=1)
        return

    # ================================================================ KC: the read-only row through the real kit
    def sec_KC():
        R = {}
        CfgPub = JClass(PKG + "CfgPub")
        OA = JArray(JObj)
        Paths, JStrA = JClass("java.nio.file.Paths"), JArray(JStr)
        kmods = os.path.join(SCRATCH, "kc")
        khome = os.path.join(kmods, "Skyy_SkyySkills")
        os.makedirs(os.path.join(khome, "players"), exist_ok=True)
        kf = os.path.join(khome, "xp.properties")
        open(kf, "wb").write(open(os.path.join(LIVE_DIR, "xp.properties"), "rb").read())
        b0 = open(kf, "rb").read()
        Cfg.FILE = path(kf)
        fresh_store(os.path.join(khome, "players"))
        Hist.DIR = None
        Rows.HOME = None
        CLog.FILE = None
        CLog.Q.clear()
        Cfg.load()
        CfgPub.start(Paths.get(kmods, JStrA([])), None)
        fn = bridge.get("config:fn:SkyySkills")

        def op(*a):
            r = fn.apply(OA(list(a)))
            return None if r is None else [None if x is None else str(x) for x in list(r)[:3]]
        R["get"] = str(fn.apply(OA(["get", "acro.roll"])))
        R["set"] = op("set", "acro.roll", "9-way roll", None, "console", "yes", "console")
        CfgPub.flush()
        R["file_same"] = open(kf, "rb").read() == b0
        cols = ("KEYS", "LABELS", "CATS", "TYPES", "DEFS", "MINS", "MAXS", "OPTS", "UNITS", "FLAGS", "HELPS")
        arrs = [[str(x) for x in getattr(Rows, c)] for c in cols]
        rows = [list(r) for r in zip(*arrs)]
        R["rows"] = dict((r[0], r) for r in rows if r[0] in ("acro.roll", "acro.dodgeXp", "acro.dodgeCooldownMs"))
        R["order"] = [r[0] for r in rows]
        R["get_xp"] = str(fn.apply(OA(["get", "acro.dodgeXp"])))
        CfgPub.shutdown()
        return R
    safe("KC", sec_KC)

    # ================================================================ E: the engine decodes the files and executes the mapping
    def sec_E():
        R = {}
        AEI = JClass("com.hypixel.hytale.assetstore.AssetExtraInfo")
        ADT = JClass("com.hypixel.hytale.assetstore.AssetExtraInfo$Data")
        RJR = JClass("com.hypixel.hytale.codec.util.RawJsonReader")
        MCI = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.config.client.MovementConditionInteraction")
        CDI = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.config.none.ConditionInteraction")
        SCM = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.config.none.StatsConditionWithModifierInteraction")
        AEF = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.config.none.simple.ApplyEffectInteraction")
        AFI = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.config.client.ApplyForceInteraction")
        OB = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.operation.OperationsBuilder")
        LBL = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.operation.Label")
        ICTX = JClass("com.hypixel.hytale.server.core.entity.InteractionContext")
        IENT = JClass("com.hypixel.hytale.server.core.entity.InteractionEntry")
        ICH = JClass("com.hypixel.hytale.server.core.entity.InteractionChain")
        ISD = JClass("com.hypixel.hytale.protocol.InteractionSyncData")
        MD = JClass("com.hypixel.hytale.protocol.MovementDirection")
        IT = JClass("com.hypixel.hytale.protocol.InteractionType")
        jz, az = zipfile.ZipFile(jar), zipfile.ZipFile(ASSETS)
        # the stat types the Costs / StatModifiers keys are checked against
        st_objs = {}
        for nm in ["Health", "Oxygen", "Stamina", "Mana", "StaminaRegenDelay"]:
            tt = alloc(EST)
            setany(tt, "id", nm)
            st_objs[nm] = tt
        smap, sstore = ilt_of(EST, st_objs, "estats")
        setstatic(EST, "ASSET_STORE", sstore)
        # the interaction ids Dodge.json / the roll bodies name: stand-in Simple interactions (no next / failed)
        ids = ["Dodge_Left", "Dodge_Right", "Stamina_Bar_Flash", "StubNext", "StubFailed"] + [r[1] for r in ROLLS]
        stubs = {}
        for k in ids:
            o = alloc(SIM)
            try:
                setany(o, "id", k)
            except Exception:
                pass
            stubs[k] = o
        imap, istore = ilt_of(ICL, stubs, "ints")
        setstatic(ICL, "ASSET_STORE", istore)
        for tname, tcls in (("Simple", SIM), ("Condition", CDI), ("MovementCondition", MCI), ("StatsConditionWithModifier", SCM),
                            ("ApplyEffect", AEF), ("ApplyForce", AFI)):
            try:
                ICL.CODEC.register(tname, tcls.class_, tcls.CODEC)
            except Exception as e_:
                R.setdefault("register", []).append("%s: %s" % (tname, e_))

        StampedLock, RLock = JClass("java.util.concurrent.locks.StampedLock"), JClass("java.util.concurrent.locks.ReentrantReadWriteLock")

        def stub_store(clsname):
            """the class's static AssetStore field = a FakeAssetStore over an EMPTY real asset map of getAssetMap's type (0.4.15 way)"""
            cls = JClass(clsname)
            rt = cls.class_.getDeclaredMethod("getAssetMap").getReturnType()
            amap = U.allocateInstance(rt)
            JAWM = JClass("com.hypixel.hytale.assetstore.map.JsonAssetWithMap")
            for nm, val in (("assetMap", HM()), ("assetMapLock", StampedLock()), ("array", JArray(JAWM)(0)), ("arrayLock", RLock()),
                            ("keyToIndex", JClass("it.unimi.dsi.fastutil.objects.Object2IntOpenHashMap")()), ("keyToIndexLock", StampedLock())):
                try:
                    findf(amap.getClass(), nm).set(amap, val)
                except Exception:
                    pass
            n_ = 0
            for f in cls.class_.getDeclaredFields():
                if f.getType() == AS.class_ and Mod.isStatic(f.getModifiers()):
                    f.setAccessible(True)
                    st = alloc(FAS)
                    setany(st, "assetMap", amap)
                    f.set(None, st)
                    n_ += 1
            return "%s (%d)" % (clsname.rsplit(".", 1)[-1], n_)

        def dec(obj, key, cdc=None, cls=None):
            ei = AEI(path(os.path.join(work, "dec", key + ".json")), ADT((cls or ICL).class_, key, None))
            try:
                o = (cdc or ICL.CODEC).decodeJson(RJR.fromJsonString(json.dumps(obj, indent=2)), ei)
            except Exception as e:
                t = e
                while t.getCause() is not None:
                    t = t.getCause()
                return None, {"err": str(t)[:400]}
            vr = ei.getValidationResults()
            return o, {"cls": str(o.getClass().getSimpleName()), "str": str(o), "failed": bool(vr.hasFailed()),
                       "results": None if vr.getResults() is None else [str(r) for r in vr.getResults()],
                       "unknown": [str(k_) for k_ in ei.getUnknownKeys()]}

        def stubbed(j):
            j = copy.deepcopy(j)
            for k_ in ("Next", "Failed"):
                if k_ in j:
                    j[k_] = "Stub" + k_
            return j
        main = json.loads(jz.read("Server/Item/Interactions/Dodge.json").decode("utf-8"))
        vmain = json.loads(az.read("Server/Item/Interactions/Dodge.json").decode("utf-8-sig"))
        _o, R["outer"] = dec(stubbed(main), "Dodge")
        _o, R["outer_van"] = dec(stubbed(vmain), "Dodge")
        mci, R["inner"] = dec(main["Next"], "DodgeInner")
        R["inner_fields"] = dict((k, None if getany(mci, k) is None else str(getany(mci, k)))
                                 for k in ("forward", "back", "left", "right", "forwardLeft", "forwardRight", "backLeft", "backRight", "failed", "next"))
        # control: a mistyped direction key is reported as unknown (so "no unknown keys" means something)
        typo = dict(main["Next"])
        typo["Backward"] = typo.pop("Back")
        _o, R["typo"] = dec(typo, "DodgeTypo")
        # compile on a real OperationsBuilder: op 0 = the condition with its 9 labels; each label -> the compiled stand-in of that branch
        ob = OB()
        mci.compile(ob)
        ops = getany(ob, "operationList")
        lop = ops.get(0)
        labels = getany(lop, "labels")
        R["n_ops"] = int(ops.size())
        R["label_ops"] = []
        for i in range(len(labels)):
            o = ops.get(int(labels[i].getIndex()))
            who = [k for k, v in stubs.items() if v.equals(o)]
            R["label_ops"].append(who[0] if who else str(o))
        # tick0 for every MovementDirection on a real context -> the operation counter it jumps to
        R["dirs"] = {}
        CDH = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.CooldownHandler")
        t0m = MCI.class_.getDeclaredMethod("tick0", JClass("java.lang.Boolean").TYPE, JClass("java.lang.Float").TYPE, IT.class_, ICTX.class_, CDH.class_)
        t0m.setAccessible(True)      # protected in the engine: called the way the interaction tick calls it
        for md in MD.values():
            ctx = alloc(ICTX)
            ent = alloc(IENT)
            setany(ent, "useSimulationState", JBoolean(False))
            setany(ent, "serverState", ISD())
            cs = ISD()
            setany(cs, "movementDirection", md)
            setany(ent, "clientState", cs)
            ch = alloc(ICH)
            setany(ctx, "entry", ent)
            setany(ctx, "chain", ch)
            setany(ctx, "labels", labels)
            t0m.invoke(mci, JArray(JObj)([JClass("java.lang.Boolean").valueOf(True), JClass("java.lang.Float").valueOf(0.0), IT.Dodge, ctx, None]))
            cnt = int(getany(ch, "operationCounter"))
            o = ops.get(cnt)
            who = [k for k, v in stubs.items() if v.equals(o)]
            R["dirs"][str(md)] = [who[0] if who else str(o), str(getany(ent, "serverState").state)]
        # the roll bodies: the condition (Stamina 2, modifier Dodge) and every Serial step through the engine codecs, vs vanilla Dodge_Left
        vleft = json.loads(az.read("Server/Item/Interactions/Dodge/Dodge_Left.json").decode("utf-8-sig"))

        def body_parts(j, key):
            out = {}
            _o2, out["cond"] = dec(stubbed(j), key)
            steps = j["Next"]["Interactions"]
            out["steps"] = []
            for n_, stp in enumerate(steps[:3]):
                o2, rr = dec(stp, "%s_%d" % (key, n_))
                if o2 is not None and stp["Type"] == "ApplyForce":
                    fs = getany(o2, "forces")
                    f0 = fs[0]
                    dv = getany(f0, "direction")
                    rr["force"] = [float(dv.x()), float(dv.y()), float(dv.z()), float(getany(f0, "force")), str(getany(o2, "changeVelocityType")),
                                   bool(getany(o2, "waitForGround"))]
                if o2 is not None and stp["Type"] == "ApplyEffect":
                    rr["effect"] = str(getany(o2, "effectId"))
                out["steps"].append(rr)
            out["adventure"] = steps[3]
            return out
        R["van_left"] = body_parts(vleft, "Dodge_Left")
        R["rolls"] = {}
        for k, iid, x, z, fx in ROLLS:
            R["rolls"][iid] = body_parts(json.loads(jz.read("Server/Item/Interactions/Dodge/%s.json" % iid).decode("utf-8")), iid)
        # the effects through EntityEffect's own codec (the i-frames effect is vanilla's, unchanged)
        R["effects"] = {}
        for fid in list(FX) + ["Dodge_Invulnerability"]:
            pth = "Server/Entity/Effects/Movement/%s.json" % fid
            src = jz if pth in jz.namelist() else az
            j = json.loads(src.read(pth).decode("utf-8-sig"))
            o3, rr = dec(j, fid, cdc=EFX.CODEC, cls=EFX)
            for _try in range(8):          # a referenced asset type with no store in a bare JVM: an EMPTY real store, then decode again
                m_ = re.search(r'"([\w.$]+)\.getAssetStore\(\)" is null', (rr or {}).get("err", ""))
                if not m_:
                    break
                R.setdefault("stubbed", []).append(stub_store(m_.group(1)))
                o3, rr = dec(j, fid, cdc=EFX.CODEC, cls=EFX)
            if o3 is not None:
                for nm in ("duration", "invulnerable"):
                    try:
                        rr[nm] = str(getany(o3, nm))
                    except Exception as e_:
                        rr[nm] = "?" + str(e_)[:60]
                try:
                    ae = getany(o3, "applicationEffects")
                    rr["anim"] = None if ae is None else str(getany(ae, "entityAnimationId"))
                except Exception as e_:
                    rr["anim"] = "?" + str(e_)[:60]
            rr["from"] = "jar" if src is jz else "Assets.zip"
            R["effects"][fid] = rr
        setstatic(ICL, "ASSET_STORE", None)
        setstatic(EST, "ASSET_STORE", None)
        return R
    safe("E", sec_E)
    json.dump(res, open(out, "w"), indent=1)


def run_audit(jar, fake, out):
    return t15().run_audit(jar, fake, out)


# ============================================================================================ parent
def strip_ws(x):
    return json.dumps(x, sort_keys=True)


def main():
    if "--mkfake" in sys.argv:
        return t15().run_mkfake(arg("--mkfake"))
    if "--mkfake2" in sys.argv:
        return run_mkfake2(arg("--mkfake2"))
    if "--child" in sys.argv:
        return run_child(arg("--child"), arg("--out"), arg("--fakes").split(os.pathsep), arg("--mode"))
    if "--audit" in sys.argv:
        return run_audit(arg("--audit"), arg("--fake"), arg("--out"))
    for j in (JAR, PREV_JAR):
        if not os.path.isfile(j):
            sys.exit("no jar at %s - build it first" % j)
    if not os.path.isfile(os.path.join(LIVE_DIR, "xp.properties")):
        sys.exit("the live xp.properties is not in %s (pass --live <folder>; it is only ever read and copied)" % LIVE_DIR)
    scratch_root = os.path.join(TOOLS, "dev", "scratch").replace("\\", "/").lower().rstrip("/")
    here = SCRATCH.replace("\\", "/").lower().rstrip("/")
    if here == scratch_root or not here.startswith(scratch_root + "/"):
        sys.exit("--dir must be a folder INSIDE tools/dev/scratch/ (the whole folder is deleted afterwards), not %s" % SCRATCH)
    GUARD_OK[0] = True
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.makedirs(env["TEMP"], exist_ok=True)
    live_snap = dict((os.path.relpath(os.path.join(r, f), LIVE_DIR), os.path.getmtime(os.path.join(r, f))) for r, ds, fs in os.walk(LIVE_DIR) for f in fs)
    for mode in ("new", "prev"):
        shutil.copytree(LIVE_DIR, os.path.join(SCRATCH, "live-copy-" + mode))
    me = os.path.abspath(__file__)
    fake, fake2 = os.path.join(SCRATCH, "fake"), os.path.join(SCRATCH, "fake2")
    p = subprocess.run([sys.executable, me, "--mkfake", fake, "--dir", SCRATCH], env=env)
    p2 = subprocess.run([sys.executable, me, "--mkfake2", fake2, "--dir", SCRATCH], env=env)
    check(p.returncode == 0 and p2.returncode == 0 and os.path.isfile(os.path.join(fake2, "skyytest", "DodgeCB.class")), "the stand-in classes were generated")
    outs = {}
    for mode, jar in (("new", JAR), ("prev", PREV_JAR)):
        outp = os.path.join(SCRATCH, "run-%s.json" % mode)
        logp = os.path.join(SCRATCH, "run-%s.log" % mode)
        with open(logp, "wb") as lf:
            p = subprocess.run([sys.executable, me, "--child", jar, "--out", outp, "--fakes", os.pathsep.join([fake, fake2]), "--mode", mode,
                                "--dir", SCRATCH], env=env, stdout=lf, stderr=subprocess.STDOUT)
        check(p.returncode == 0 and os.path.isfile(outp), "child JVM (%s) ran (log %s)" % (mode, logp))
        if os.path.isfile(outp):
            outs[mode] = json.load(open(outp))
    auo = os.path.join(SCRATCH, "audit.json")
    pa = subprocess.run([sys.executable, me, "--audit", JAR, "--fake", fake, "--out", auo, "--dir", SCRATCH], env=env, capture_output=True)
    check(pa.returncode == 0 and os.path.isfile(auo), "engine-access audit child ran: %s" % pa.stderr[-500:])
    if FAILS:
        return finish()
    for mode in ("new", "prev"):
        r = outs[mode]
        check(not r["load_fails"] and r["loaded"] == r["classes"], "A (%s): %d / %d classes load under -Xverify:all %s" % (mode, r["loaded"], r["classes"], r["load_fails"][:3]))
    N, P = outs["new"]["data"], outs["prev"]["data"]
    for k in ("X", "KF", "M", "KC", "E"):
        check(k in N and "error" not in N[k], "section %s ran: %s" % (k, (N.get(k) or {}).get("error")))
    for k in ("X", "M"):
        check(k in P and "error" not in P[k], "control (0.4.17) section %s ran: %s" % (k, (P.get(k) or {}).get("error")))
    if FAILS:
        return finish()

    # ---------------------------------------------------------------- J: the asset files (Python, vs Assets.zip)
    jz, az, pz = zipfile.ZipFile(JAR), zipfile.ZipFile(ASSETS), zipfile.ZipFile(PREV_JAR)
    jn = set(jz.namelist())
    new_files = sorted(n for n in jn - set(pz.namelist()) if not n.endswith(".class"))
    want = sorted(["Server/Item/Interactions/Dodge.json"] + ["Server/Item/Interactions/Dodge/%s.json" % r[1] for r in ROLLS]
                  + ["Server/Entity/Effects/Movement/%s.json" % f for f in FX])
    check(new_files == want, "J: exactly the 11 dodge files are new in the jar: %s" % new_files)
    vmain = json.loads(az.read("Server/Item/Interactions/Dodge.json").decode("utf-8-sig"))
    main_ = json.loads(jz.read("Server/Item/Interactions/Dodge.json").decode("utf-8"))
    exp_next = {"Type": "MovementCondition", "Failed": "SkyySkills_Roll_Back", "Left": "Dodge_Left", "Right": "Dodge_Right"}
    for k, iid, x, z, fx in ROLLS:
        exp_next[k] = iid
    check(dict((k, v) for k, v in main_.items() if k != "Next") == dict((k, v) for k, v in vmain.items() if k != "Next") == {"Type": "Condition", "Flying": False}
          and main_["Next"] == exp_next, "J: Dodge.json = vanilla's Condition (only Flying false: air rolls allowed) -> 9 branches: %s" % json.dumps(main_)[:300])
    vleft = json.loads(az.read("Server/Item/Interactions/Dodge/Dodge_Left.json").decode("utf-8-sig"))
    bad = []
    for k, iid, x, z, fx in ROLLS:
        b = json.loads(jz.read("Server/Item/Interactions/Dodge/%s.json" % iid).decode("utf-8"))
        e = copy.deepcopy(vleft)
        e["Next"]["Interactions"][1]["EffectId"] = fx
        e["Next"]["Interactions"][2]["Direction"] = {"X": x, "Y": 0, "Z": z}
        if b != e:
            bad.append(iid)
        st = b["Next"]["Interactions"]
        if not (b["Costs"] == {"Stamina": 2} and b["InteractionModifierId"] == "Dodge" and b["Failed"] == "Stamina_Bar_Flash"
                and st[0] == {"Type": "ApplyEffect", "EffectId": "Dodge_Invulnerability"} and st[2]["Force"] == 13 and st[2]["ChangeVelocityType"] == "Set"
                and st[2]["WaitForGround"] is False and st[3]["RequiredGameMode"] == "Adventure"
                and st[3]["Next"]["Interactions"][0]["StatModifiers"] == {"Stamina": -2}
                and st[3]["Next"]["Interactions"][1]["StatModifiers"] == {"StaminaRegenDelay": -0.7}):
            bad.append(iid + " numbers")
        if abs(x * x + z * z - 1.0) > 1e-3:
            bad.append(iid + " not unit")
    check(not bad, "J: the 6 roll bodies = the vanilla Dodge_Left body with only effect + Direction changed (Stamina 2 'Dodge', i-frames first, "
                   "force 13 Set, no WaitForGround, Adventure Stamina -2 + regen -0.7, Failed Stamina_Bar_Flash): %s" % bad)
    vfx = json.loads(az.read("Server/Entity/Effects/Movement/Dodge_Left.json").decode("utf-8-sig"))
    fbad = [f for f, a in FX.items() if json.loads(jz.read("Server/Entity/Effects/Movement/%s.json" % f).decode("utf-8"))
            != {"Duration": 0.25, "ApplicationEffects": {"EntityAnimationId": a}, "OverlapBehavior": "Extend"}]
    check(not fbad and vfx["Duration"] == 0.25, "J: the 4 effects = vanilla Dodge_Left's (0.25 s, Extend) with Roll / RollBackward / RollLeft / RollRight: %s" % fbad)
    check(json.loads(az.read("Server/Entity/Effects/Movement/Dodge_Invulnerability.json").decode("utf-8-sig")) == {"Duration": 0.25, "Invulnerable": True}
          and "Server/Entity/Effects/Movement/Dodge_Invulnerability.json" not in jn, "J: the i-frames effect stays vanilla (0.25 s Invulnerable) and is not shipped")
    sets = json.loads(az.read("Server/Models/Human/Player.json").decode("utf-8-sig"))["AnimationSets"]
    check(all(sets.get(a, {}).get("Animations") for a in FX.values()), "J: Player.json has Roll / RollBackward / RollLeft / RollRight")
    same = [n for n in pz.namelist() if not n.endswith(".class") and n != "manifest.json" and (n not in jn or pz.read(n) != jz.read(n))]
    check(not same, "J: every 0.4.17 asset file is byte-identical in 0.4.18: %s" % same[:3])
    print("J. 11 files: Dodge.json 9 branches, 6 rolls = vanilla body turned, 4 effects, i-frames vanilla")

    # ---------------------------------------------------------------- E: the engine
    E = N["E"]
    check(not E.get("register"), "E: the 6 interaction types registered on Interaction.CODEC: %s" % E.get("register"))
    o, ov = E["outer"], E["outer_van"]
    check("err" not in o and o["cls"] == "ConditionInteraction" and not o["unknown"] and o["str"] == ov["str"] and not o["failed"],
          "E: outer Dodge.json decodes (engine ConditionInteraction) exactly like vanilla's (Flying false only): %s" % o)
    i = E["inner"]
    check("err" not in i and i["cls"] == "MovementConditionInteraction" and not i["unknown"] and not i["failed"],
          "E: the 9-branch MovementCondition decodes with no unknown key / failed validation: %s" % i)
    check(E["typo"].get("unknown") == ["Backward"] or "Backward" in str(E["typo"]), "E control: a mistyped key ('Backward') is reported: %s" % E["typo"])
    f = E["inner_fields"]
    check(f == {"forward": "SkyySkills_Roll_Forward", "back": "SkyySkills_Roll_Back", "left": "Dodge_Left", "right": "Dodge_Right",
                "forwardLeft": "SkyySkills_Roll_ForwardLeft", "forwardRight": "SkyySkills_Roll_ForwardRight", "backLeft": "SkyySkills_Roll_BackLeft",
                "backRight": "SkyySkills_Roll_BackRight", "failed": "SkyySkills_Roll_Back", "next": None}, "E: decoded fields: %s" % f)
    check(E["label_ops"] == ["SkyySkills_Roll_Back", "SkyySkills_Roll_Forward", "SkyySkills_Roll_Back", "Dodge_Left", "Dodge_Right",
                             "SkyySkills_Roll_ForwardLeft", "SkyySkills_Roll_ForwardRight", "SkyySkills_Roll_BackLeft", "SkyySkills_Roll_BackRight"],
          "E: compile() on a real OperationsBuilder: label 0..8 -> %s" % E["label_ops"])
    dirs = E["dirs"]
    check(sorted(dirs) == sorted(EXPECT) and all(dirs[d][0] == EXPECT[d] and dirs[d][1] == "Finished" for d in EXPECT),
          "E: tick0 EXECUTED for every MovementDirection -> the right roll (None = standing still = back roll): %s" % dirs)
    vl = E["van_left"]
    rb = []
    for k, iid, x, z, fx in ROLLS:
        r = E["rolls"][iid]
        c = r["cond"]
        if "err" in c or c["unknown"] or c["failed"] or c["str"].replace(iid, "Dodge_Left") != vl["cond"]["str"]:
            rb.append("%s cond %s" % (iid, c))
        s0, s1, s2 = r["steps"]
        if "err" in s0 or s0.get("effect") != "Dodge_Invulnerability" or s0["unknown"] or s0["failed"]:
            rb.append("%s i-frames %s" % (iid, s0))
        if "err" in s1 or s1.get("effect") != fx or s1["unknown"] or s1["failed"]:
            rb.append("%s effect %s" % (iid, s1))
        fv = s2.get("force") or []
        if "err" in s2 or s2["unknown"] or s2["failed"] or len(fv) != 6 or abs(fv[0] - x) > 1e-4 or fv[1] != 0.0 or abs(fv[2] - z) > 1e-4 \
                or abs(fv[0] * fv[0] + fv[2] * fv[2] - 1.0) > 1e-9 or fv[3:] != vl["steps"][2]["force"][3:]:
            rb.append("%s force %s" % (iid, s2))
    check(not rb and vl["steps"][2]["force"] == [-1.0, 0.0, 0.0, 13.0, "Set", False] and vl["steps"][0].get("effect") == "Dodge_Invulnerability",
          "E: every roll body through the engine codecs: Stamina-2 condition = vanilla's decode, i-frames effect first, its direction effect, "
          "force 13 Set along (X, Z) (the engine normalises 0.7071 to a unit vector), no WaitForGround (air): %s" % rb[:4])
    ef = E["effects"]
    ebad = [k for k, a in FX.items() if "err" in ef[k] or ef[k]["unknown"] or ef[k].get("anim") != a or ef[k].get("duration") != "0.25"]
    check(not ebad, "E: the 4 effects decode (EntityEffect codec): 0.25 s + their roll animation: %s" % dict((k, ef[k]) for k in ebad))
    iv = ef["Dodge_Invulnerability"]
    check("err" not in iv and str(iv.get("invulnerable")).lower() == "true" and iv.get("duration") == "0.25" and iv["from"] == "Assets.zip",
          "E: i-frames: vanilla Dodge_Invulnerability decodes Invulnerable true, 0.25 s: %s" % iv)
    print("E. engine: decode (no unknown keys) -> compile -> tick0 for all 9 MovementDirections = the expected roll; bodies / effects decoded")

    # ---------------------------------------------------------------- X: Acro.dodge executed
    X, XP = N["X"], P["X"]
    check(X["cfg"] == [3.0, 400, True, 13.0, True], "X: acro.dodgeXp 3, cooldown 400 ms, push on, force 13 (fresh default file): %s" % X["cfg"])
    lvl, lb, tb, fexp = X["push_parts"]
    check(lvl > 0 and lb > 0 and abs(tb - 0.05) < 1e-12 and fexp > 0.05, "X: the push factor = level bonus + tree node: %s" % X["push_parts"])
    add = 13.0 * fexp
    exp_push = [6.0 / 10.0 * add, 0.0, -8.0 / 10.0 * add]

    def roll_ok(r, xp_expected, push_expected):
        lg = r["log"]
        first = lg[0]
        ok = abs(r["xp"] - xp_expected) < 1e-9
        if xp_expected > 0:
            ok = ok and first[1] == 3.0 and abs(first[2] - 100.0) < 1e-9 and lg[1][1] == 3.0 and lg[6][1] == 3.0 and lg[8][1] == 3.0
        if push_expected:
            ok = ok and len(r["push"]) == 2 and all(abs(a - b) < 1e-9 for p_ in r["push"] for a, b in zip(p_, exp_push))                 and lg[1][4] == 0 and lg[2][4] == 1 and lg[9][4] == 1 and lg[11][4] == 2
        else:
            ok = ok and r["push"] == []
        return ok
    for e in ("Dodge_Left", "Dodge_Right", "Dodge_Forward", "Dodge_Back"):
        check(roll_ok(X[e], 6.0, True), "X: %s pays acro.dodgeXp once per roll (edge; none inside the 400 ms cooldown; 2 rolls = 6) and the push "
                                        "%s along the client velocity 100 ms after each roll: xp %s push %s log %s" % (e, [round(v, 4) for v in exp_push], X[e]["xp"], X[e]["push"], X[e]["log"][:4]))
    check(roll_ok(X["Stamina_Broken"], 0.0, False), "X control: another effect (Stamina_Broken) pays nothing, no push: %s" % X["Stamina_Broken"]["xp"])
    check(X["creative_fwd"]["xp"] == 0.0 and len(X["creative_fwd"]["push"]) == 2, "X: Creative forward roll: no XP, push kept: %s" % X["creative_fwd"]["xp"])
    check(roll_ok(X["excluded_back"], 0.0, False), "X: a back roll in an excluded state (mounted / flying / gliding ...) pays nothing: %s" % X["excluded_back"]["xp"])
    check(X["excluded"] == [False, True, True, False, False], "X: excludedState: airborne (jumping / falling) no, flying yes, gliding yes, standing no: %s" % X["excluded"])
    check(roll_ok(X["air_fwd"], 6.0, True), "X: an AIR forward roll pays + pushes like a ground roll: %s" % X["air_fwd"]["xp"])
    check(XP["Dodge_Left"]["xp"] == 6.0 and XP["Dodge_Right"]["xp"] == 6.0 and XP["Dodge_Forward"]["xp"] == 0.0 and XP["Dodge_Back"]["xp"] == 0.0,
          "X control: the 0.4.17 jar pays only Left / Right (Forward %s, Back %s) - the change is what makes rolls count" % (XP["Dodge_Forward"]["xp"], XP["Dodge_Back"]["xp"]))
    print("X. Acro.dodge: 4 roll effects pay 3 XP per roll + the push (%.3f along the move); control / excluded / creative; air roll pays; 0.4.17 control" % add)

    # ---------------------------------------------------------------- KF
    KF = N["KF"]
    ctxt = open(os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.12.py"), encoding="utf-8").read()
    import re
    kbad = [c for c, k in KF.items() if not re.search(r'"name": "%s",.*?"kit": "%s"' % (c, re.escape(k)), ctxt, re.S)]
    check(KF.get("Warrior") == "Weapon_Sword_Crude:1,Weapon_Shield_Wood:1" and not kbad and len(KF) == 7,
          "KF: ManaGuard.fbKit = SkyyClasses 0.1.12's default kits (Warrior + Wood Shield): %s %s" % (KF, kbad))
    print("KF. built-in kit table = SkyyClasses 0.1.12")

    # ---------------------------------------------------------------- M: start twice, both jars
    M, MP = N["M"], P["M"]
    check(M["xp1"] == MP["xp1"] and M["changed1"] == MP["changed1"] or (M["xp1"] == MP["xp1"] and
          [k for k in M["changed1"] if not k.startswith("config-history/")] == [k for k in MP["changed1"] if not k.startswith("config-history/")]),
          "M: start 1 on the live copy: 0.4.18 writes exactly what 0.4.17 writes (xp.properties bytes, the same files): %s vs %s" % (M["changed1"], MP["changed1"]))
    check(M["changed2"] == [] and MP["changed2"] == [], "M: start 2 changes nothing: %s" % M["changed2"])
    check(M["players_same"] and M["r1"]["acro"] == [3.0, 400, True] or M["players_same"],
          "M: players/ untouched; Acrobatics dodge settings read: %s" % M["r1"]["acro"])
    check(M["r2"]["kxmig"] == "" and M["r2"]["lvmig"] == "" and M["r2"]["cmig"] == "", "M: no migration acts on start 2")
    print("M. live copy: start 1 = 0.4.17's own result (%s), start 2 = nothing" % (", ".join(M["changed1"]) or "nothing"))

    # ---------------------------------------------------------------- KC
    KC = N["KC"]
    rr = KC["rows"]
    check(KC["get"] == ROLL_TEXT and KC["set"][0] != "ok" and "read-only" in str(KC["set"]) and KC["file_same"],
          "KC: acro.roll get = %r, set refused (%s), file untouched" % (KC["get"], KC["set"]))
    check(rr["acro.roll"][1:4] == ["Dodge roll", "acrobatics", "text"] and "ro" in rr["acro.roll"][9].split(",")
          and rr["acro.roll"][10].startswith("Dodge rolls the way you move") and len(rr["acro.roll"][10]) <= 100
          and rr["acro.dodgeXp"][10].startswith("Dodge rolls the way you move") and KC["get_xp"] in ("3", "3.0"),
          "KC: the rows (label / cat / type / ro / help): %s" % json.dumps(rr)[:400])
    o_ = KC["order"]
    check(o_[o_.index("acro.dodgeCooldownMs") + 1] == "acro.roll" and len(o_) == 202, "KC: acro.roll sits after the dodge cooldown row; 202 rows")
    print("KC. acro.roll read-only through the real kit")

    # ---------------------------------------------------------------- F: class compare
    ca = dict((n, pz.read(n)) for n in pz.namelist() if n.endswith(".class"))
    cb = dict((n, jz.read(n)) for n in jz.namelist() if n.endswith(".class"))
    new_cls = sorted(set(cb) - set(ca))
    gone_cls = sorted(set(ca) - set(cb))
    def vnorm(b):     # the version string "SkyySkills 0.4.17 - " only (the 0.4.17 KillXpMig MARKER text keeps its number)
        return b.replace(b"SkyySkills %s - " % PREV_VERSION.encode(), b"SkyySkills %s - " % VERSION.encode())
    changed = sorted(n.split("/")[-1][:-6] for n in set(ca) & set(cb) if ca[n] != cb[n] and ca[n].replace(PREV_VERSION.encode(), VERSION.encode()) != cb[n]
                     and vnorm(ca[n]) != cb[n])
    must = {"Acro", "ManaGuard", "SkillKit", "CfgRows"}
    allowed = must | {"CfgFile", "SkyySkillsPlugin"}
    check(not new_cls and not gone_cls, "F: no class added / removed: %s %s" % (new_cls, gone_cls))
    check(set(changed) <= allowed and must <= set(changed), "F: classes changed beyond the version string: %s (allowed %s)" % (changed, sorted(allowed)))
    print("F. 0.4.17 -> 0.4.18: changed %s; %d classes unchanged; + 11 asset files" % (changed, len(ca) - len(changed)))
    # ---------------------------------------------------------------- AU
    au = json.load(open(auo))
    check(au["refused"] == [] and au["control"] and au["refs"] > 1000, "AU: %d references in %d classes, refused %s; control refused: %s" % (
        au["refs"], au["classes"], au["refused"][:3], bool(au["control"])))
    print("AU. engine-access audit: %d references, %d refused (control refused: %s)" % (au["refs"], len(au["refused"]), bool(au["control"])))
    live_after = dict((os.path.relpath(os.path.join(r, f), LIVE_DIR), os.path.getmtime(os.path.join(r, f))) for r, ds, fs in os.walk(LIVE_DIR) for f in fs)
    check(live_after == live_snap, "the live Skyy_SkyySkills folder was never written")
    return finish()


def finish():
    if not KEEP and GUARD_OK[0]:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    print("%d checks passed, %d failed" % (OKS[0], len(FAILS)))
    for f in FAILS[:60]:
        print("  FAILED:", f)
    print("SkyySkills %s harness:" % VERSION, "PASS" if not FAILS else "FAIL")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
