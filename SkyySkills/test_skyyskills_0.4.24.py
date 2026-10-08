"""SkyySkills 0.4.24 - bare-JVM harness for THE WOOD WAND SIGNATURE (tools/skills_0_4_24_patch.py; Skyy 2026-10-08 "Wand can shoot a shot
that ricochets through eight enemies"). The new item files run through the REAL engine (HytaleServer.jar on the class path) together with
the REAL SkyyArmory 0.1.14 files they name; the classes of the 0.4.24 jar and, as the control, the SET pin 0.4.23; the live save data is only
ever READ and copied into scratch.

    python SkyySkills/test_skyyskills_0.4.24.py [--jar <SkyySkills-0.4.24.jar>] [--prev <SkyySkills-0.4.23.jar>]
                                                [--armory <SkyyArmory-0.1.14.jar>] [--dir <scratch>] [--live <Skyy_SkyySkills folder>]
                                                [--keep] [--no23]

SECTIONS
  A   every class of both jars loads under -Xverify:all
  J   the jar: 0.4.23's files, only the 3 wood wand item overrides changed, each in exactly Interactions (+ Ability1) / Weapon /
      ItemAppearanceConditions, those = SkyyArmory 0.1.14's 7 metal wands field by field; every other file byte-identical; no Parallel with
      fewer than 2 entries in any jar JSON
  E   THE ENGINE (real asset stores, both jars' wands; SkyyArmory 0.1.14's real root / gate / launch / marker files):
      E1 NEGATIVE CONTROLS: a one-entry Parallel fails the validator function; a wand item naming an Ability1 root that is NOT in the store
         (SkyyArmory missing) - what the validators say
      E2 the ENGINE ASSET VALIDATORS on SkyyArmory's 4 signature files and on the 3 wood wands of the jar (decode, the codec's full
         validate, logOrThrowValidatorExceptions, contained assets), after SkyyArmory's files are in the stores (the load order)
      E3 THE ROOT RESOLVES THROUGH THE ENGINE STORES: the 3 wands loaded into the Item store under this jar's pack; Item.getInteractions()
         Ability1 = SkyyArmory_Wand_Signature; RootInteraction.getAssetMap() has it (SkyyArmory's pack); RootInteraction.build() =
         StatsCondition (the gate) -> ChangeStat (the spend) -> LaunchProjectile (the ricochet marker), no placeholder; Primary / Secondary
         still Wand_Primary; the 0.4.23 wand has no Ability1 (control)
      E4 THE METER: the decoded ItemWeapon (SignatureEnergy in EntityStatsToClear, StatModifiers MAX +20) applied by the engine's own
         StatModifiersManager.addItemStatModifiers (the held-weapon path, "*Weapon_" key) to a real EntityStatMap = max 20 (0.4.23's wand:
         0); the ready look (Item.itemAppearanceConditions decoded, SignatureEnergy)
      E5 THE ENGINE'S OWN SIGNATURE FIRE CHECK: StatsConditionInteraction.canAfford of SkyyArmory's decoded gate (from the store) on that
         stat map: full meter (20) = passes; 19 / 10 / 0 = refused
  S   THE BUILD BLOCK EXECUTED (the generated script's own text, every branch): the real inputs = the jar's 3 texts; THE STOP RULE
      (SkyyArmory 0.1.13 / not pinned); a SkyyArmory jar whose metal meter differs, without the root, or shipping a wood wand item; an
      override already carrying a Weapon block = the build stops; SkyyArmory not built here = a NOTE and the same texts
  M   START TWICE on a scratch copy of the live data (the plugin's setup() data steps, both jars): start 1 = 0.4.23's result, start 2
      changes nothing, the player files untouched
  H23 the 0.4.23 harness on the 0.4.24 jar (control: the 0.4.23 jar): nothing fails beyond its version-shape checks - its nested H22 /
      H21 ... = START TWICE on a scratch copy of the live data
  F   class compare 0.4.23 -> 0.4.24 METHOD BY METHOD (version strings normalised): no class differs
  AU  the engine-access audit (every bytecode reference looked up with the JVM's own access rules; control refused)
"""
import os, sys, re, json, shutil, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, PREV_VERSION = "0.4.24", "0.4.23"
PKG = "com.skyy.skills."
WANDS = ["Weapon_Wand_Wood", "Weapon_Wand_Wood_Rotten", "Weapon_Wand_Tribal"]
METALS = ["Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium"]
SIG_ROOT, SIG_CAST, SIG_LAUNCH, SIG_MARK = ("SkyyArmory_Wand_Signature", "SkyyArmory_Wand_Signature_Cast", "SkyyArmory_Wand_Signature_Launch",
                                            "SkyyArmory_Wand_Ricochet")
ARP = "Skyy:0.1.14 SkyyArmory"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "woodwand01", "skills0424")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
PREV_JAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyySkills-%s.jar" % PREV_VERSION)))
ARMORY_JAR = os.path.abspath(arg("--armory", os.path.join(ROOT, "SkyyArmory", "SkyyArmory-0.1.14.jar")))
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
    """the 0.4.15 harness module (JVM start with -Xverify:all, class loader, access audit, stand-ins) - imported, never run"""
    return tmod("test_skyyskills_0.4.15.py", "t0415")


def t20():
    """the 0.4.20 harness module (the method-by-method class compare) - imported, never run"""
    return tmod("test_skyyskills_0.4.20.py", "t0420")


def item_path(z, iid):
    h = [n for n in z.namelist() if n.startswith("Server/Item/Items/") and n.endswith("/%s.json" % iid)]
    assert len(h) == 1, (iid, h)
    return h[0]


# ============================================================================================ child: -Xverify:all load (one jar)
def run_child(jar, out):
    T = t15()
    res, path = T.common(jar, [])
    json.dump({"loaded": res["loaded"], "classes": res["classes"], "load_fails": res["load_fails"]}, open(out, "w"), indent=1)


# ============================================================================================ child: START TWICE on a live copy (one jar)
def run_start(jar, out, mode):
    """the plugin's setup() data steps in its own order (SkyySkillsPlugin.setup: the 7 migrations, SkillCfg.load, ClassCurve.start,
    OwnCurve.start) twice on a scratch COPY of the live Skyy_SkyySkills folder - the 0.4.20 harness's section M way (its nested chain can
    no longer reach it: the 0.4.19 jar it needs was tidied away)"""
    from jpype import JClass
    T = t15()
    res, path = T.common(jar, [])
    R = {"load_fails": res["load_fails"]}
    Cfg, Store, Hist, CLog, Rows = (JClass(PKG + "SkillCfg"), JClass(PKG + "SkillStore"), JClass(PKG + "CfgHist"), JClass(PKG + "CfgLog"),
                                    JClass(PKG + "CfgRows"))
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    lc = os.path.join(SCRATCH, "live-copy-" + mode)

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
        for nm in ("ManaMig", "HealMig", "DocMig", "ClassManaMig", "SkillLvMig", "KillXpMig", "AcroMig"):
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
        R["players"] = len([k for k in s0 if k.startswith("players/")])
        R["players_same"] = all(s0.get(k) == s1.get(k) == s2.get(k) for k in set(s0) | set(s1) | set(s2) if k.startswith("players/"))
    except Exception:
        import traceback
        R["error"] = traceback.format_exc()[-3000:]
    json.dump(R, open(out, "w"), indent=1)


# ============================================================================================ child: the engine (one jar)
def run_engine(jar, out, mode):
    import jpype
    from jpype import JClass, JArray, JString, JImplements, JOverride, JFloat, JInt
    import skyybuild as SB
    hcls = os.path.join(SCRATCH, "hcls-" + mode)
    os.makedirs(hcls, exist_ok=True)
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jpype.startJVM(SB._jvm(), "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[SB.SERVER_JAR, jar, SB.JAVASSIST, hcls], convertStrings=True)
    R = {"mode": mode}
    Uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    Uf.setAccessible(True)
    U = Uf.get(None)
    CHM, ArrayList, Paths = JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.util.ArrayList"), JClass("java.nio.file.Paths")
    Mod = JClass("java.lang.reflect.Modifier")

    def jfield(cls, name):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        return f

    def setstatic_of_type(cls, obj):
        for f in cls.class_.getDeclaredFields():
            if f.getType() == cls.class_ and Mod.isStatic(f.getModifiers()):
                f.setAccessible(True)
                f.set(None, obj)
    # the server singletons the stores read (the 0.4.23 harness way)
    Options = JClass("com.hypixel.hytale.server.core.Options")
    Options.parse(JArray(JString)(["--universe", os.path.join(SCRATCH, "universe-" + mode)]))
    HS = JClass("com.hypixel.hytale.server.core.HytaleServer")
    hs = U.allocateInstance(HS.class_)
    jfield(HS, "eventBus").set(hs, JClass("com.hypixel.hytale.event.EventBus")(False))
    jfield(HS, "instance").set(None, hs)
    UNI = JClass("com.hypixel.hytale.server.core.universe.Universe")
    uni = U.allocateInstance(UNI.class_)
    pbu = CHM()
    jfield(UNI, "playersByUuid").set(uni, pbu)
    jfield(UNI, "players").set(uni, JClass("java.util.Collections").unmodifiableCollection(pbu.values()))
    wmap = CHM()
    jfield(UNI, "worlds").set(uni, wmap)
    jfield(UNI, "worldsByUuid").set(uni, CHM())
    jfield(UNI, "unmodifiableWorlds").set(uni, JClass("java.util.Collections").unmodifiableMap(wmap))
    jfield(UNI, "instance").set(None, uni)
    CAP = JClass("java.util.concurrent.CopyOnWriteArrayList")()
    JClass("com.hypixel.hytale.logger.backend.HytaleLoggerBackend").subscribe(CAP)

    def records():
        out_ = []
        for r in list(CAP):
            msg = str(r.getMessage())
            ps = r.getParameters()
            if ps is not None and len(ps) > 0:
                try:
                    msg = str(JClass("java.lang.String").format(msg, ps))
                except Exception:
                    msg = msg + " " + " ".join(str(p) for p in ps)
            out_.append((str(r.getLevel()), msg))
        return out_
    JClass("com.hypixel.hytale.server.core.asset.AssetRegistryLoader").init()
    AR = JClass("com.hypixel.hytale.assetstore.AssetRegistry")
    HAS = JClass("com.hypixel.hytale.server.core.asset.HytaleAssetStore")
    ILT = JClass("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap")
    ARR = JClass("java.lang.reflect.Array")
    PI = "com.hypixel.hytale.server.core.modules.interaction.interaction.config."
    INTc, ROOTc = JClass(PI + "Interaction"), JClass(PI + "RootInteraction")
    SMI = JClass(PI + "none.simple.SendMessageInteraction")

    @JImplements("java.util.function.Function")
    class GetId:
        @JOverride
        def apply(self, o): return o.getId()

    @JImplements("java.util.function.IntFunction")
    class ArrOf:
        def __init__(self, c): self.c = c

        @JOverride
        def apply(self, n): return ARR.newInstance(self.c.class_, n)

    @JImplements("java.util.function.Function")
    class Rep:
        def __init__(self, root=False): self.root = root

        @JOverride
        def apply(self, k):
            if self.root:
                return ROOTc(str(k), JArray(JString)([]))
            return SMI(str(k), "removed " + str(k))

    @JImplements("java.util.function.Predicate")
    class IsUnknown:
        @JOverride
        def test(self, o): return bool(o.isUnknown())

    @JImplements("java.util.function.Function")
    class WeaponMods:          # the engine's own lambda$recalculateEntityStatModifiers$0: item -> item.getWeapon().getStatModifiers()
        @JOverride
        def apply(self, it):
            w = it.getWeapon()
            return None if w is None else w.getStatModifiers()
    IPG = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.InteractionPacketGenerator")
    AR.register(HAS.builder(INTc.class_, ILT(ArrOf(INTc))).setPath("Item/Interactions").setCodec(INTc.CODEC).setKeyFunction(GetId())
                .setReplaceOnRemove(Rep()).setIsUnknown(IsUnknown()).setPacketGenerator(IPG()).build())
    UIc = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.UnarmedInteractions")
    AR.register(HAS.builder(UIc.class_, JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")()).setPath("Item/Unarmed/Interactions")
                .setCodec(UIc.CODEC).setKeyFunction(GetId()).build())
    AR.register(HAS.builder(ROOTc.class_, ILT(ArrOf(ROOTc))).setPath("Item/RootInteractions").setCodec(ROOTc.CODEC).setKeyFunction(GetId())
                .setReplaceOnRemove(Rep(True)).build())
    ESTc = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType")
    AR.register(HAS.builder(ESTc.class_, ILT(ArrOf(ESTc))).setPath("Entity/Stats").setCodec(ESTc.CODEC).setKeyFunction(GetId())
                .setReplaceOnRemove(Rep()).build())
    # the interaction Type codecs exactly as InteractionModule.setup registers them (read from its bytecode) + ProjectileModule's "Projectile"
    CPool = JClass("javassist.bytecode.ConstPool")
    CPj = JClass("javassist.ClassPool")(True)
    CPj.appendClassPath(SB.SERVER_JAR)
    imc = CPj.get("com.hypixel.hytale.server.core.modules.interaction.InteractionModule")
    ms_ = [x for x in imc.getDeclaredMethods() if str(x.getName()) == "setup"][0]
    cp_, it_ = ms_.getMethodInfo().getConstPool(), ms_.getMethodInfo().getCodeAttribute().iterator()
    last_s, last_c, regs = None, None, []
    while it_.hasNext():
        p_ = it_.next()
        op_ = it_.byteAt(p_)
        if op_ in (0x12, 0x13):
            idx = it_.byteAt(p_ + 1) if op_ == 0x12 else it_.u16bitAt(p_ + 1)
            t_ = cp_.getTag(idx)
            if t_ == CPool.CONST_String:
                last_s = str(cp_.getStringInfo(idx))
            elif t_ == CPool.CONST_Class:
                last_c = str(cp_.getClassInfo(idx))
        elif op_ == 0xb6:
            idx = it_.u16bitAt(p_ + 1)
            if str(cp_.getMethodrefClassName(idx)).endswith("AssetCodecMapCodec") and str(cp_.getMethodrefName(idx)) == "register":
                regs.append((last_s, last_c))
    for nm_, cl_ in regs:
        C_ = JClass(cl_)
        INTc.CODEC.register(nm_, C_.class_, jfield(C_, "CODEC").get(None))
    PRJIc = JClass("com.hypixel.hytale.server.core.modules.projectile.interaction.ProjectileInteraction")
    INTc.CODEC.register("Projectile", PRJIc.class_, PRJIc.CODEC)
    R["codecs"] = len(regs)
    AEI, ADT = JClass("com.hypixel.hytale.assetstore.AssetExtraInfo"), JClass("com.hypixel.hytale.assetstore.AssetExtraInfo$Data")
    RJR = JClass("com.hypixel.hytale.codec.util.RawJsonReader")
    ITMc = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    PRJc = JClass("com.hypixel.hytale.server.core.asset.type.projectile.config.Projectile")
    R["stores"] = [AR.getAssetStore(ITMc.class_) is not None, AR.getAssetStore(PRJc.class_) is not None]
    az = zipfile.ZipFile(os.path.join(os.path.dirname(SB.SERVER_JAR), "..", "Assets.zip"))
    jz = zipfile.ZipFile(jar)
    amz = zipfile.ZipFile(ARMORY_JAR)
    work = os.path.join(SCRATCH, "eng-" + mode)
    os.makedirs(work, exist_ok=True)

    def put(sub, name, text):
        d = os.path.join(work, sub)
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, name)
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
        return Paths.get(p)

    def loadp(cls, pack, paths):
        l_ = ArrayList()
        for p in paths:
            l_.add(p)
        r = AR.getAssetStore(cls.class_).loadAssetsFromPaths(pack, l_)
        return not r.hasFailed()
    # the vanilla stat types (SignatureEnergy, Mana ...), their effect hooks left out (only the ids / max matter here)
    stl = ArrayList()
    for n in az.namelist():
        if n.startswith("Server/Entity/Stats/") and n.endswith(".json"):
            d = json.loads(az.read(n).decode("utf-8-sig"))
            for x_ in ("Regenerating", "MinValueEffects", "MaxValueEffects"):
                d.pop(x_, None)
            k = os.path.basename(n)[:-5]
            try:
                stl.add(AR.getAssetStore(ESTc.class_).getCodec().decodeJsonAsset(RJR.fromJsonString(json.dumps(d)), AEI(Paths.get(k + ".json"), ADT(ESTc.class_, k, None))))
            except Exception:
                pass
    AR.getAssetStore(ESTc.class_).loadAssets("Hytale:Hytale", stl)
    DST = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes")
    DST.update()
    SIGI = int(DST.getSignatureEnergy())
    R["sig_index"] = [SIGI, int(ESTc.getAssetMap().getIndex("SignatureEnergy"))]
    HLOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkillsHarness")
    KNOWN = set(os.path.basename(n).rsplit(".", 1)[0] for n in list(az.namelist()) + list(jz.namelist()) + list(amz.namelist()))
    COMMON = set(n[len("Common/"):] for n in list(az.namelist()) + list(amz.namelist()) if n.startswith("Common/"))

    def known(ln):
        """a 'does not exist' line for a vanilla / SkyyArmory name the bare JVM did not load (never one of the 4 signature names)"""
        m2_ = re.search(r"'([^']+)'", ln)
        if not m2_ or not ("doesn't exist" in ln or "does not exist" in ln) or m2_.group(1) in (SIG_ROOT, SIG_CAST, SIG_LAUNCH, SIG_MARK):
            return False
        return m2_.group(1) in KNOWN or (ln.startswith("Common Asset") and m2_.group(1) in COMMON)

    def validate(cls, key, text):
        """the engine's validators on one asset: decode, the codec's full validate, logOrThrowValidatorExceptions, the contained assets.
        A 'does not exist' line for a name that IS in Assets.zip / this jar / SkyyArmory = the bare JVM's empty stores (a NOTE)"""
        n0 = len(records())
        st = AR.getAssetStore(cls.class_)
        ei = AEI(Paths.get(key + ".json"), ADT(cls.class_, key, None))
        try:
            o = st.getCodec().decodeJsonAsset(RJR.fromJsonString(text), ei)
        except Exception as e:
            return None, ["decode: " + str(e)[:300]], [], []
        prob, env, alln = [], [], []
        uk = [str(x) for x in ei.getUnknownKeys()]
        if uk:
            prob.append("unknown keys %s" % uk)
        try:
            st.getCodec().validate(o, ei)
        except Exception as e:
            prob.append("validate threw %s" % str(e)[:300])
        vr = ei.getValidationResults()
        lines = []
        try:
            if vr is not None:
                vr.logOrThrowValidatorExceptions(HLOG)
        except Exception as e:
            lines += re.findall(r"FAIL: ([^\n]*)", str(e))
        try:
            ei.getData().loadContainedAssets(False)
        except Exception as e:
            prob.append("contained assets: %s" % str(e)[:300])
        for lv, m_ in records()[n0:]:
            lines += re.findall(r"FAIL: ([^\n]*)", m_)
        for ln in lines:
            alln.append(ln[:300])
            (env if known(ln) else prob).append(ln[:300])
        return o, prob, env, alln

    def load(cls, pack, objs, own=False):
        """the decoded objects into the real store (the SkyyArmory harness way: the bare JVM lacks the models / sounds / vanilla parents
        the validators would look up again at a path load - those lines are E2's test-bed notes)"""
        l_ = ArrayList()
        for o_ in objs:
            if o_ is None:
                return False
            l_.add(o_)
        try:
            r_ = AR.getAssetStore(cls.class_).loadAssets(pack, l_)
            if r_.hasFailed():
                R.setdefault("load_fail", []).append("%s: failed keys %s, own loaded %d" % (
                    cls.class_.getSimpleName(), sorted(str(k) for k in r_.getFailedToLoadKeys())[:6], r_.getLoadedAssets().size()))
            if own:          # the assets themselves (an inline child's own validator result is reported apart by the caller)
                return r_.getFailedToLoadKeys().isEmpty() and r_.getLoadedAssets().size() == len(objs)
            return not r_.hasFailed()
        except Exception as e:
            R.setdefault("load_errors", []).append("%s: %s" % (cls.class_.getSimpleName(), str(e)[:300]))
            return False
    # ---- E1 NEGATIVE CONTROLS
    neg = validate(INTc, "SkyySkillsHarness_OneParallel", json.dumps({"Type": "Simple", "RunTime": 0.1, "Next": {"Type": "Parallel", "Interactions": [{"Interactions": ["Stamina_Bar_Flash"]}]}}))
    pos = validate(INTc, "SkyySkillsHarness_TwoParallel", json.dumps({"Type": "Simple", "RunTime": 0.1, "Next": {"Type": "Parallel", "Interactions": [{"Interactions": ["Stamina_Bar_Flash"]}, {"Interactions": ["Stamina_Bar_Flash"]}]}}))
    R["neg"] = [neg[0] is not None, neg[1][:2], pos[0] is not None, pos[1][:2]]
    # the vanilla interactions the wands' inline InteractionVars inherit by Parent (Mana / 5 overrides + the swing trails) - the game has them
    # loaded before any item; without them the Item store's load reports the bare JVM's 'Failed to find parent'
    vpar = []
    for b in ("Wand_Cast_Left_Charged", "Wand_Cast_Cost", "Sword_Swing_Left_Fast_Effect", "Sword_Swing_Right_Fast_Effect"):
        n = [x for x in az.namelist() if x.startswith("Server/Item/Interactions/") and x.endswith("/%s.json" % b)]
        o_ = None
        if len(n) == 1:
            st_ = AR.getAssetStore(INTc.class_)
            o_ = st_.getCodec().decodeJsonAsset(RJR.fromJsonString(az.read(n[0]).decode("utf-8-sig")), AEI(Paths.get(b + ".json"), ADT(INTc.class_, b, None)))
        vpar.append(o_)
    TRLc = JClass("com.hypixel.hytale.server.core.asset.type.trail.config.Trail")          # the swing trails' Small_Default
    tn = [x for x in az.namelist() if x.startswith("Server/") and x.endswith("/Small_Default.json")]
    to_ = None
    if len(tn) == 1 and AR.getAssetStore(TRLc.class_) is not None:
        to_ = AR.getAssetStore(TRLc.class_).getCodec().decodeJsonAsset(RJR.fromJsonString(az.read(tn[0]).decode("utf-8-sig")),
                                                                      AEI(Paths.get("Small_Default.json"), ADT(TRLc.class_, "Small_Default", None)))
    R["vpar_load"] = [load(TRLc, "Hytale:Hytale", [to_]), load(INTc, "Hytale:Hytale", vpar)]
    wtext = dict((w, jz.read(item_path(jz, w)).decode("utf-8")) for w in WANDS)
    nr = validate(ITMc, "Weapon_Wand_Wood", wtext["Weapon_Wand_Wood"])          # BEFORE SkyyArmory's root is in the store
    R["noroot"] = {"ok": nr[0] is not None, "prob": nr[1], "all": nr[3]}
    # ---- the vanilla pieces the signature chain names (the vanilla Wand_Primary chain the wand's Primary keeps is not needed here)
    # SkyyArmory 0.1.14's 4 signature files: validated, then into the stores under SkyyArmory's pack (it loads BEFORE SkyySkills)
    apaths = {}
    for n in amz.namelist():
        b = os.path.basename(n)[:-5]
        if n.endswith(".json") and b in (SIG_ROOT, SIG_CAST, SIG_LAUNCH, SIG_MARK):
            apaths[b] = n
    R["armory_files"] = sorted(apaths)
    val, aobj = {}, {}
    for b, cls in ((SIG_MARK, PRJc), (SIG_LAUNCH, INTc), (SIG_CAST, INTc), (SIG_ROOT, ROOTc)):
        o, p, e, a_ = validate(cls, b, amz.read(apaths[b]).decode("utf-8"))
        val[b] = {"ok": o is not None, "prob": p, "env": e}
        aobj[b] = o
    R["a_load"] = [load(PRJc, ARP, [aobj[SIG_MARK]]), load(INTc, ARP, [aobj[SIG_CAST], aobj[SIG_LAUNCH]]), load(ROOTc, ARP, [aobj[SIG_ROOT]])]
    # ---- E2 the jar's 3 wands through the validators (SkyyArmory's files present); the control = the 0.4.23 jar's same wand validated in
    # the same JVM right after (a line both give is the bare JVM, not this change)
    pz = zipfile.ZipFile(PREV_JAR)
    wobj = {}
    for w in WANDS:
        o, p, e, a_ = validate(ITMc, w, wtext[w])
        wobj[w] = o
        oc, pc_, ec, ac = validate(ITMc, w, pz.read(item_path(pz, w)).decode("utf-8"))
        same = [x for x in p if x in pc_]
        val[w] = {"ok": o is not None, "prob": [x for x in p if x not in pc_], "env": e + same, "root_lines": [x for x in a_ if SIG_ROOT in x]}
    R["val"] = val
    # ---- E3 the 3 wands into the Item store under this jar's pack, then resolve through the stores
    SKP = "Skyy:%s SkyySkills" % mode
    n0_ = len(records())
    R["i_load"] = load(ITMc, SKP, [wobj[w] for w in WANDS], own=True)
    # the inline InteractionVars children the store loads with the items: their validator lines (bare JVM: vanilla sounds / trails not
    # loaded) - the parent compares them with the 0.4.23 wands' (same JVM setup): this change adds none
    R["i_child_lines"] = sorted(set(re.sub(r"\s+", " ", m_)[:240] for lv_, m_ in records()[n0_:] if lv_ == "SEVERE"))
    IT = JClass("com.hypixel.hytale.protocol.InteractionType")
    imap, rmap = ITMc.getAssetMap(), ROOTc.getAssetMap()
    per = {}
    for w in WANDS:
        it = imap.getAsset(w)
        d = {"in_store": it is not None}
        if it is None:
            per[w] = d
            continue
        ints = dict((str(k), str(v)) for k, v in dict(it.getInteractions()).items())
        d["pack"] = str(imap.getAssetPack(w))
        d["interactions"] = ints
        rid = ints.get("Ability1")
        if rid is not None:
            ra = rmap.getAsset(rid)
            d["root_in_store"] = ra is not None
            d["root_pack"] = str(rmap.getAssetPack(rid)) if ra is not None else None
            ops, bad = [], []
            if ra is not None:
                try:
                    ra.build()
                    for i in range(int(ra.getOperationMax())):
                        op = ra.getOperation(i)
                        inner = op.getInnerOperation()
                        if inner is not None and INTc.class_.isInstance(inner):
                            ops.append([str(inner.getClass().getSimpleName()), str(inner.getId())])
                            if SMI.class_.isInstance(inner):
                                bad.append("placeholder for " + str(inner.getId()))
                        else:
                            ops.append([str(op.getClass().getSimpleName()), None])
                except Exception as e:
                    bad.append("build: " + str(e)[:300])
            d["ops"], d["bad"] = ops, bad
            la = INTc.getAssetMap().getAsset(SIG_LAUNCH)
            d["launch_projectile"] = str(la.getProjectileId()) if la is not None and hasattr(la, "getProjectileId") else None
        # ---- E4 the meter: the decoded weapon block, applied by the engine's own held-weapon path
        wp = it.getWeapon()
        d["weapon"] = wp is not None
        if wp is not None:
            sm = wp.getStatModifiers()
            mods = sm.get(JInt(SIGI)) if sm is not None else None
            d["weapon_mods"] = [] if mods is None else [[str(m_.getTarget()), str(m_.getCalculationType()), float(m_.getAmount())] for m_ in mods]
            esc = wp.getEntityStatsToClear()
            d["clear"] = [] if esc is None else [int(x) for x in esc]
        try:
            iac = jfield(ITMc, "itemAppearanceConditions").get(it)
            d["look"] = None if iac is None else sorted(str(ESTc.getAssetMap().getAsset(int(k)).getId()) if str(k).isdigit() else str(k)
                                                        for k in dict(iac).keys())
        except Exception as e:
            d["look"] = "no field: %s" % str(e)[:120]
        per[w] = d
    R["per"] = per
    # the stat map + a ComponentAccessor answering it (EntityStatMap.getComponentType needs the EntityStatsModule singleton)
    ESMc = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap")
    ESMOD = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatsModule")
    esmod = U.allocateInstance(ESMOD.class_)
    jfield(ESMOD, "entityStatMapComponentType").set(esmod, U.allocateInstance(jfield(ESMOD, "entityStatMapComponentType").getType()))
    jfield(ESMOD, "instance").set(None, esmod)
    CtNM = JClass("javassist.CtNewMethod")
    CP_ = "com.hypixel.hytale.component."
    sb = CPj.makeClass("skyyh24.StatBuf", CPj.get(CP_ + "CommandBuffer"))
    sb.addField(JClass("javassist.CtField").make("public static Object STAT = null;", sb))
    sb.addMethod(CtNM.make("public " + CP_ + "Component getComponent(" + CP_ + "Ref r, " + CP_ + "ComponentType t) { return (" + CP_ + "Component) STAT; }", sb))
    sb.writeFile(hcls)
    StatBuf = JClass("skyyh24.StatBuf")
    acc = U.allocateInstance(StatBuf.class_)
    ref = JClass("com.hypixel.hytale.component.Ref")(None, 7)
    SMM = JClass("com.hypixel.hytale.server.core.entity.StatModifiersManager")
    ISc = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    aim = [m_ for m_ in SMM.class_.getDeclaredMethods() if str(m_.getName()) == "addItemStatModifiers"]
    R["aim"] = [str(m_) for m_ in aim]
    SCIc = JClass(PI + "none.StatsConditionInteraction")
    ca = SCIc.class_.getDeclaredMethod("canAfford", JClass("com.hypixel.hytale.component.Ref").class_, JClass("com.hypixel.hytale.component.ComponentAccessor").class_)
    ca.setAccessible(True)
    gate = INTc.getAssetMap().getAsset(SIG_CAST)
    R["gate_class"] = None if gate is None else str(gate.getClass().getSimpleName())
    meter = {}
    for w in WANDS:
        r_ = {}
        try:
            m_ = ESMc()
            m_.update()
            r_["max0"] = float(m_.get(SIGI).getMax())
            if len(aim) == 1:
                aim[0].setAccessible(True)
                aim[0].invoke(None, JArray(JClass("java.lang.Object"))([ISc(w, 1), m_, "*Weapon_", WeaponMods()]))
            r_["max"] = float(m_.get(SIGI).getMax())
            StatBuf.STAT = m_
            res_ = []
            if gate is not None:
                for v_ in (20.0, 19.0, 10.0, 0.0):
                    m_.setStatValue(SIGI, JFloat(v_))
                    res_.append([float(m_.get(SIGI).get()), bool(ca.invoke(gate, JArray(JClass("java.lang.Object"))([ref, acc])))])
            r_["gate"] = res_
        except Exception as e:
            c = e
            try:
                while c.getCause() is not None:
                    c = c.getCause()
            except Exception:
                pass
            r_["error"] = str(c)[:400]
        meter[w] = r_
    R["meter"] = meter
    json.dump(R, open(out, "w"), indent=1)


# ============================================================================================ S: the build-time block, every branch EXECUTED
def run_block(armory_pin, armory_jar_bytes, prev_jar):
    """exec the 0.4.24 build script's WOOD WAND SIGNATURE block (the exact text between its header line and the pack scan) with the inputs
    the build gives it: SPELL_FILES = the 0.4.23 jar's item override texts, the pinned SkyyArmory version and (in a scratch fake project)
    its jar. Returns ("ok", SPELL_FILES after, printed) or ("stop", message)."""
    src = open(os.path.join(HERE, "build_skyyskills_%s.py" % VERSION), encoding="utf8").read().replace("\r\n", "\n")
    a = src.index("# ================= 0.4.24 THE WOOD WAND SIGNATURE")
    b = src.index("_pk_found, _other, _pk_mana = [], [], []\n", a)
    block = src[a:b]
    fake = os.path.join(SCRATCH, "sproj-%d" % len(os.listdir(SCRATCH)))
    os.makedirs(os.path.join(fake, "SkyySkills"))
    os.makedirs(os.path.join(fake, "SkyyArmory"))
    if armory_jar_bytes is not None:
        open(os.path.join(fake, "SkyyArmory", "SkyyArmory-%s.jar" % armory_pin), "wb").write(armory_jar_bytes)
    import skyybuild as SB
    pz = zipfile.ZipFile(prev_jar)
    sf = dict((n, pz.read(n).decode("utf-8")) for n in pz.namelist() if n.startswith("Server/Item/") and n.endswith(".json"))
    ns = {"os": os, "json": json, "zipfile": zipfile, "HERE": os.path.join(fake, "SkyySkills"), "_armory_pin": armory_pin, "SPELL_FILES": sf,
          "ASSETS": os.path.join(SB.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")}
    import io, contextlib
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            exec(compile(block, "build_skyyskills_%s.py:wood-sig" % VERSION, "exec"), ns)
    except SystemExit as e:
        return ("stop", str(e))
    finally:
        shutil.rmtree(fake, ignore_errors=True)
    return ("ok", ns["SPELL_FILES"], buf.getvalue(), ns.get("WOOD_SIG_CHECKED"))


def jar_with(src_jar, changes):
    """a copy of a jar (bytes) with some entries replaced (name -> bytes) or added"""
    import io
    out = io.BytesIO()
    with zipfile.ZipFile(src_jar) as zi, zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zo:
        for n in zi.namelist():
            zo.writestr(n, changes.pop(n) if n in changes else zi.read(n))
        for n, b in changes.items():
            zo.writestr(n, b)
    return out.getvalue()


def sec_S():
    jz, az_ = zipfile.ZipFile(JAR), zipfile.ZipFile(ARMORY_JAR)
    real = open(ARMORY_JAR, "rb").read()
    # S1 the real inputs (SkyyArmory 0.1.14 pinned + built) = exactly the jar's 3 wand files, every other override text untouched
    r1 = run_block("0.1.14", real, PREV_JAR)
    pz = zipfile.ZipFile(PREV_JAR)
    ok1 = False
    if r1[0] == "ok":
        sf = r1[1]
        diff = sorted(n for n in sf if sf[n] != pz.read(n).decode("utf-8"))
        ok1 = (diff == sorted(item_path(jz, w) for w in WANDS) and all(sf[n] == jz.read(n).decode("utf-8") for n in diff)
               and r1[3] == "0.1.14" and "checked equal to SkyyArmory 0.1.14's 7 metal wands" in r1[2])
    check(ok1, "S1: the build block on the real inputs (SkyyArmory 0.1.14 pinned + its jar) changes exactly the 3 wood wand texts, byte-equal "
               "to the jar's, and says it compared the 7 metal wands: %s" % (r1[0] if r1[0] != "ok" else r1[2].strip()[:300]))
    # S2 THE STOP RULE: SkyyArmory 0.1.13 pinned (or none) = the build stops with the deploy_set text
    r2, r2b = run_block("0.1.13", None, PREV_JAR), run_block(None, None, PREV_JAR)
    check(r2[0] == "stop" and "STOP: SkyySkills 0.4.24+ needs SkyyArmory 0.1.14+" in r2[1] and r2b[0] == "stop" and "STOP:" in r2b[1],
          "S2: STOP RULE - SkyyArmory 0.1.13 pinned / not pinned: the build stops ('SkyySkills 0.4.24+ needs SkyyArmory 0.1.14+'): %s | %s" % (
              r2[1][:200], r2b[1][:120]))
    # S3 a pinned SkyyArmory jar whose metal wand meter differs (Copper's max 15) = the build stops (the wood wands must match)
    cp = item_path(az_, "Weapon_Wand_Copper")
    cj = json.loads(az_.read(cp))
    cj["Weapon"]["StatModifiers"]["SignatureEnergy"][0]["Amount"] = 15
    r3 = run_block("0.1.14", jar_with(ARMORY_JAR, {cp: json.dumps(cj, indent=2).encode()}), PREV_JAR)
    check(r3[0] == "stop" and "Weapon_Wand_Copper does not carry the same signature fields" in r3[1],
          "S3: a SkyyArmory jar whose Copper wand meter is 15 stops the build (field-by-field compare): %s" % (r3[1][:200] if r3[0] == "stop" else r3[0]))
    # S4 a pinned SkyyArmory jar without the root / that ships a wood wand item = stops
    rp = [n for n in az_.namelist() if n.endswith("/%s.json" % SIG_ROOT)][0]
    import io
    out = io.BytesIO()
    with zipfile.ZipFile(ARMORY_JAR) as zi, zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zo:
        for n in zi.namelist():
            if n != rp:
                zo.writestr(n, zi.read(n))
    r4a = run_block("0.1.14", out.getvalue(), PREV_JAR)
    r4b = run_block("0.1.14", jar_with(ARMORY_JAR, {"Server/Item/Items/Weapon/Wand/Weapon_Wand_Wood.json": b"{}"}), PREV_JAR)
    check(r4a[0] == "stop" and "ships 0 x SkyyArmory_Wand_Signature.json" in r4a[1] and r4b[0] == "stop" and "two overrides of one id" in r4b[1],
          "S4: a SkyyArmory jar without the root stops the build; one that ships a wood wand item stops it too: %s | %s" % (
              r4a[1][:160] if r4a[0] == "stop" else r4a[0], r4b[1][:160] if r4b[0] == "stop" else r4b[0]))
    # S5 SkyyArmory pinned but not built here = a NOTE, the same 3 texts (generated from the vanilla sword alone)
    r5 = run_block("0.1.14", None, PREV_JAR)
    check(r5[0] == "ok" and r5[3] is None and "NOTE SkyyArmory 0.1.14 is not built here" in r5[2] and r1[0] == "ok"
          and all(r5[1][item_path(jz, w)] == r1[1][item_path(jz, w)] for w in WANDS),
          "S5: SkyyArmory pinned but its jar not built here: a NOTE, and the same 3 wand texts (the fields come from the vanilla sword): %s" % (
              r5[2].strip()[:200] if r5[0] == "ok" else r5[1][:200]))
    # S6 a 0.4.23 override that is not the expected shape (already has a Weapon block) = stops (never double-applied)
    pj = json.loads(pz.read(item_path(pz, "Weapon_Wand_Tribal")))
    pj["Weapon"] = {"x": 1}
    tmpj = os.path.join(SCRATCH, "prev-tampered.jar")
    open(tmpj, "wb").write(jar_with(PREV_JAR, {item_path(pz, "Weapon_Wand_Tribal"): json.dumps(pj, indent=2).encode()}))
    r6 = run_block("0.1.14", real, tmpj)
    check(r6[0] == "stop" and "Weapon_Wand_Tribal override is not the expected shape" in r6[1],
          "S6: an item override that already carries a Weapon block stops the build (never applied twice): %s" % (r6[1][:160] if r6[0] == "stop" else r6[0]))
    print("S. the build block executed on 7 inputs: real = the jar's 3 texts; STOP rule (0.1.13 / none), a changed metal meter, no root, a "
          "SkyyArmory wood wand, an unexpected override shape = stops; jar not built = NOTE")


# ============================================================================================ parent
def main():
    if "--mkfake" in sys.argv:
        return t15().run_mkfake(arg("--mkfake"))
    if "--child" in sys.argv:
        return run_child(arg("--child"), arg("--out"))
    if "--start" in sys.argv:
        return run_start(arg("--start"), arg("--out"), arg("--mode"))
    if "--engine" in sys.argv:
        return run_engine(arg("--engine"), arg("--out"), arg("--mode"))
    if "--audit" in sys.argv:
        return t15().run_audit(arg("--audit"), arg("--fake"), arg("--out"))
    if "--compare" in sys.argv:
        m = t20()
        m.VERSION, m.PREV_VERSION = VERSION, PREV_VERSION
        return m.run_compare(arg("--compare"), arg("--prevjar"), arg("--out"))
    for j in (JAR, PREV_JAR, ARMORY_JAR):
        if not os.path.isfile(j):
            sys.exit("no jar at %s - build it first" % j)
    if not os.path.isdir(os.path.join(LIVE_DIR, "players")):
        sys.exit("the live players folder is not in %s (pass --live <folder>; it is only ever read and copied)" % LIVE_DIR)
    scratch_root = os.path.join(TOOLS, "dev", "scratch").replace("\\", "/").lower().rstrip("/")
    here = SCRATCH.replace("\\", "/").lower().rstrip("/")
    rel = here[len(scratch_root) + 1:] if here.startswith(scratch_root + "/") else ""
    if here == scratch_root or not rel or "/" not in rel:
        sys.exit("--dir must be a sub-folder of a task folder inside tools/dev/scratch/ (e.g. tools/dev/scratch/<task>/skills0424; that folder is "
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
    p = subprocess.run([sys.executable, me, "--mkfake", fake, "--dir", SCRATCH], env=env)
    check(p.returncode == 0, "the stand-in classes were generated")
    outs, engs = {}, {}
    for mode, jar in (("prev", PREV_JAR), ("new", JAR)):
        outp = os.path.join(SCRATCH, "run-%s.json" % mode)
        logp = os.path.join(SCRATCH, "run-%s.log" % mode)
        with open(logp, "wb") as lf:
            p = subprocess.run([sys.executable, me, "--child", jar, "--out", outp, "--dir", SCRATCH], env=env, stdout=lf, stderr=subprocess.STDOUT)
        check(p.returncode == 0 and os.path.isfile(outp), "child JVM (%s) ran (log %s)" % (mode, logp))
        if os.path.isfile(outp):
            outs[mode] = json.load(open(outp))
        ver = VERSION if mode == "new" else PREV_VERSION
        oute = os.path.join(SCRATCH, "eng-%s.json" % mode)
        loge = os.path.join(SCRATCH, "eng-%s.log" % mode)
        with open(loge, "wb") as lf:
            p = subprocess.run([sys.executable, me, "--engine", jar, "--out", oute, "--mode", ver, "--dir", SCRATCH, "--armory", ARMORY_JAR, "--prev", PREV_JAR],
                               env=env, stdout=lf, stderr=subprocess.STDOUT)
        check(p.returncode == 0 and os.path.isfile(oute), "engine child JVM (%s) ran (log %s)" % (mode, loge))
        if os.path.isfile(oute):
            engs[mode] = json.load(open(oute))
    sts = {}
    for mode, jar in (("prev", PREV_JAR), ("new", JAR)):
        shutil.copytree(LIVE_DIR, os.path.join(SCRATCH, "live-copy-" + mode))
        outs_ = os.path.join(SCRATCH, "start-%s.json" % mode)
        with open(os.path.join(SCRATCH, "start-%s.log" % mode), "wb") as lf:
            p = subprocess.run([sys.executable, me, "--start", jar, "--out", outs_, "--mode", mode, "--dir", SCRATCH], env=env, stdout=lf, stderr=subprocess.STDOUT)
        check(p.returncode == 0 and os.path.isfile(outs_), "start-twice child JVM (%s) ran" % mode)
        if os.path.isfile(outs_):
            sts[mode] = json.load(open(outs_))
    cmpo = os.path.join(SCRATCH, "compare.json")
    pc = subprocess.run([sys.executable, me, "--compare", JAR, "--prevjar", PREV_JAR, "--out", cmpo, "--dir", SCRATCH], env=env, capture_output=True)
    check(pc.returncode == 0 and os.path.isfile(cmpo), "class compare child ran: %s" % pc.stderr[-500:])
    auo = os.path.join(SCRATCH, "audit.json")
    pa = subprocess.run([sys.executable, me, "--audit", JAR, "--fake", fake, "--out", auo, "--dir", SCRATCH], env=env, capture_output=True)
    check(pa.returncode == 0 and os.path.isfile(auo), "engine-access audit child ran: %s" % pa.stderr[-500:])
    h23 = None
    if "--no23" not in sys.argv:
        h23 = {}
        for tag, jj in (("new", JAR), ("ctl", PREV_JAR)):
            ph = subprocess.run([sys.executable, os.path.join(HERE, "test_skyyskills_0.4.23.py"), "--jar", jj, "--prev",
                                 os.path.join(HERE, "SkyySkills-0.4.22.jar"), "--dir", os.path.join(SCRATCH, "h23-" + tag), "--live", LIVE_DIR],
                                env=env, capture_output=True)
            h23[tag] = ph.stdout.decode("utf-8", "replace")
    if FAILS:
        return finish()
    # ---------------------------------------------------------------- A
    for mode in ("new", "prev"):
        r = outs[mode]
        check(not r["load_fails"] and r["loaded"] == r["classes"], "A (%s): %d / %d classes load under -Xverify:all %s" % (mode, r["loaded"], r["classes"], r["load_fails"][:3]))
    print("A. both jars: every class loads under -Xverify:all (%d / %d classes)" % (outs["new"]["loaded"], outs["prev"]["loaded"]))
    # ---------------------------------------------------------------- J
    jz, jp, az_ = zipfile.ZipFile(JAR), zipfile.ZipFile(PREV_JAR), zipfile.ZipFile(ARMORY_JAR)
    nn, pn = set(n for n in jz.namelist() if not n.endswith(".class")), set(n for n in jp.namelist() if not n.endswith(".class"))
    changed = sorted(n for n in nn & pn if n != "manifest.json" and jz.read(n) != jp.read(n))
    want_chg = sorted(item_path(jz, w) for w in WANDS)
    mn_, mp_ = json.loads(jz.read("manifest.json")), json.loads(jp.read("manifest.json"))
    mdiff = sorted(k for k in set(mn_) | set(mp_) if mn_.get(k) != mp_.get(k))
    check(nn == pn and changed == want_chg and mdiff == ["Name", "Version"] and mn_["Version"] == VERSION,
          "J: the 0.4.24 jar = 0.4.23's files; changed = exactly the 3 wood wand items (+ the manifest's Name / Version): added %s gone %s "
          "changed %s manifest %s" % (sorted(nn - pn)[:3], sorted(pn - nn)[:3], changed, mdiff))
    cop = json.loads(az_.read(item_path(az_, "Weapon_Wand_Copper")))
    metal = [json.loads(az_.read(item_path(az_, "Weapon_Wand_" + m))) for m in METALS]
    jbad = []
    for w in WANDS:
        a, b = json.loads(jp.read(item_path(jp, w))), json.loads(jz.read(item_path(jz, w)))
        keys = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
        ok = (keys == ["Interactions", "ItemAppearanceConditions", "Weapon"]
              and b["Interactions"] == dict(a["Interactions"], Ability1=SIG_ROOT) and a["Interactions"] == {"Primary": "Wand_Primary", "Secondary": "Wand_Primary"}
              and a["Weapon"] == {} and "ItemAppearanceConditions" not in a
              and all(b["Weapon"] == x["Weapon"] and b["ItemAppearanceConditions"] == x["ItemAppearanceConditions"]
                      and b["Interactions"]["Ability1"] == x["Interactions"]["Ability1"] for x in metal)
              and b["InteractionVars"] == a["InteractionVars"])
        if not ok:
            jbad.append([w, keys])
    check(not jbad and len(metal) == 7, "J: each wood wand (Wood, Rotten, Tribal) differs from 0.4.23's file in exactly Interactions (+ Ability1 "
                                        "%s; Primary / Secondary still Wand_Primary) / Weapon / ItemAppearanceConditions, and those equal SkyyArmory "
                                        "0.1.14's 7 metal wands field by field (Mana costs - InteractionVars - unchanged): %s" % (SIG_ROOT, jbad))
    par = []

    def walk(x, n):
        if isinstance(x, dict):
            if x.get("Type") == "Parallel" and len(x.get("Interactions") or []) < 2:
                par.append(n)
            for v in x.values():
                walk(v, n)
        elif isinstance(x, list):
            for v in x:
                walk(v, n)
    for n in jz.namelist():
        if n.endswith(".json"):
            walk(json.loads(jz.read(n).decode("utf-8")), n)
    check(not par, "J: no Parallel with fewer than 2 entries in any JSON of the 0.4.24 jar (the check that once stopped the server): %s" % par[:3])
    print("J. jar: 3 wood wand items changed (%s), every other file byte-identical; the fields = SkyyArmory 0.1.14 Copper's: Weapon %s" % (
        ", ".join(WANDS), json.dumps(cop["Weapon"])))
    # ---------------------------------------------------------------- S
    sec_S()
    # ---------------------------------------------------------------- E
    En, Ep = engs["new"], engs["prev"]
    check(En["stores"] == [True, True] and En["sig_index"][0] == En["sig_index"][1] >= 0 and En["codecs"] >= 70,
          "E: the engine stores (Item, Projectile from AssetRegistryLoader.init; Interaction / Root / EntityStat registered like the modules), "
          "%d interaction codecs, SignatureEnergy = DefaultEntityStatTypes index %s" % (En["codecs"], En["sig_index"]))
    check(En["neg"][0] and any("Array size" in x for x in En["neg"][1]) and En["neg"][2] and not En["neg"][3],
          "E1 NEGATIVE CONTROL: the validator function refuses a one-entry Parallel with the engine's own 'Array size' message and passes it "
          "with 2 entries: %s" % En["neg"])
    nr = En["noroot"]
    root_flag = [x for x in nr["all"] if SIG_ROOT in x]
    check(nr["ok"] and root_flag and all("doesn't exist" in x for x in root_flag)
          and all(not En["val"][w].get("root_lines") for w in WANDS),
          "E1 NEGATIVE CONTROL: the Wood wand validated BEFORE SkyyArmory's root is in the store = the engine's 'Asset %s of type "
          "RootInteraction doesn't exist' (SkyySkills 0.4.24 without SkyyArmory 0.1.14 - the STOP rule); with SkyyArmory's files loaded no "
          "validator line names the root: %s | after %s" % (SIG_ROOT, root_flag[:1], [En["val"][w].get("root_lines") for w in WANDS]))
    print("E1. the Wood wand validated with NO SkyyArmory root in the store: decoded %s, validator lines naming the root: %s" % (nr["ok"], root_flag[:1]))
    check(sorted(En["armory_files"]) == sorted([SIG_ROOT, SIG_CAST, SIG_LAUNCH, SIG_MARK]) and En["a_load"] == [True, True, True],
          "E2: SkyyArmory 0.1.14's 4 signature files (root, gate + spend, launch, ricochet marker) found and loaded into the real stores "
          "under %s: %s %s" % (ARP, En["armory_files"], En["a_load"]))
    vbad = dict((k, v) for k, v in En["val"].items() if not v["ok"] or v["prob"])
    venv = sorted(set(x for v in En["val"].values() for x in v["env"]))
    check(not vbad and len(En["val"]) == 7,
          "E2: the ENGINE ASSET VALIDATORS pass on SkyyArmory's 4 signature files and the jar's 3 wood wands (decode, the codec's full "
          "validate, logOrThrowValidatorExceptions, contained assets): %s" % json.dumps(vbad)[:900])
    print("E2. validators: %d assets pass; NOTE test-bed lines (vanilla names the bare JVM did not load): %s" % (len(En["val"]), venv[:4]))
    check(En["vpar_load"] == [True, True] and En["i_load"] and Ep["i_load"] and En["i_child_lines"] == Ep["i_child_lines"],
          "E3: the 3 wands load into the real Item store, none refused (their vanilla InteractionVars parents loaded first, as the game does): "
          "0.4.24 %s, 0.4.23 %s (parents %s); the inline vars' validator lines are the SAME as for the 0.4.23 wands (bare JVM: %d, e.g. %s)" % (
              En["i_load"], Ep["i_load"], En["vpar_load"], len(En["i_child_lines"]), En["i_child_lines"][:1]))
    e3bad = []
    for w in WANDS:
        d = En["per"].get(w, {})
        cls = [c for c, i in d.get("ops", []) if i is not None]
        named = [i for c, i in d.get("ops", []) if i is not None]
        ok = (d.get("in_store") and d.get("pack") == "Skyy:%s SkyySkills" % VERSION
              and d.get("interactions") == {"Primary": "Wand_Primary", "Secondary": "Wand_Primary", "Ability1": SIG_ROOT}
              and d.get("root_in_store") and d.get("root_pack") == ARP and not d.get("bad")
              and "StatsConditionInteraction" in cls and "ChangeStatInteraction" in cls and "LaunchProjectileInteraction" in cls
              and cls.index("StatsConditionInteraction") < cls.index("ChangeStatInteraction") < cls.index("LaunchProjectileInteraction")
              and SIG_CAST in named and SIG_LAUNCH in named and d.get("launch_projectile") == SIG_MARK)
        if not ok:
            e3bad.append([w, d])
    check(not e3bad, "E3: THE ROOT RESOLVES THROUGH THE ENGINE STORES - each wand from this jar's pack: Item.getInteractions() = Primary / Secondary "
                     "Wand_Primary + Ability1 %s; RootInteraction.getAssetMap() has it (SkyyArmory's pack); build() = StatsCondition -> ChangeStat "
                     "-> LaunchProjectile, no placeholder: %s" % (SIG_ROOT, json.dumps(e3bad)[:900]))
    pctl = [w for w in WANDS if "Ability1" in (Ep["per"].get(w, {}).get("interactions") or {"Ability1": 1})]
    check(not pctl, "E3 control: the 0.4.23 wands (same stores) have no Ability1: %s" % pctl)
    sigi = En["sig_index"][0]
    e4bad = []
    for w in WANDS:
        d = En["per"][w]
        if not (d.get("weapon") and d.get("weapon_mods") == [["MAX", "ADDITIVE", 20.0]] and d.get("clear") == [sigi] and d.get("look") == ["SignatureEnergy"]):
            e4bad.append([w, d.get("weapon_mods"), d.get("clear"), d.get("look")])
    check(not e4bad, "E4: the decoded ItemWeapon of each wand: SignatureEnergy in EntityStatsToClear, StatModifiers SignatureEnergy MAX ADDITIVE 20 "
                     "(the vanilla sword's); the ready look decoded (itemAppearanceConditions: SignatureEnergy): %s" % e4bad)
    check(len(En["aim"]) == 1 and all(En["meter"][w].get("max0") == 0.0 and En["meter"][w].get("max") == 20.0 for w in WANDS)
          and all(Ep["meter"][w].get("max") == 0.0 for w in WANDS),
          "E4: the engine's own StatModifiersManager.addItemStatModifiers (the held-weapon path, '*Weapon_') on a real EntityStatMap: the "
          "SignatureEnergy max goes 0 -> 20 for each 0.4.24 wand (0.4.23's wands: stays 0 - no meter): %s | 0.4.23 %s" % (
              json.dumps(En["meter"])[:600], json.dumps(dict((w, Ep["meter"][w].get("max")) for w in WANDS))))
    check(En["gate_class"] == "StatsConditionInteraction"
          and all([g[1] for g in En["meter"][w].get("gate", [])] == [True, False, False, False] and [g[0] for g in En["meter"][w]["gate"]] == [20.0, 19.0, 10.0, 0.0]
                  for w in WANDS),
          "E5: THE ENGINE'S OWN SIGNATURE FIRE CHECK - StatsConditionInteraction.canAfford of SkyyArmory's decoded gate (from the store) on "
          "the wand-held stat map: a FULL meter (20) passes, a partial one (19 / 10 / 0) is refused, for all 3 wood wands: %s" % (
              json.dumps(dict((w, En["meter"][w].get("gate")) for w in WANDS))))
    print("E. engine: root %s resolves for %s; meter max 0 -> %s; gate full / 19 / 10 / 0 = %s" % (
        SIG_ROOT, ", ".join(WANDS), En["meter"]["Weapon_Wand_Wood"].get("max"), [g[1] for g in En["meter"]["Weapon_Wand_Wood"].get("gate", [])]))
    # ---------------------------------------------------------------- H23
    if h23 is not None:
        def fails_of(txt):
            return [ln.strip()[len("FAILED: "):] for ln in txt.splitlines() if ln.strip().startswith("FAILED: ")]
        fn_, fc_ = fails_of(h23["new"]), fails_of(h23["ctl"])
        ctl_keys = set(f_[:60] for f_ in fc_)
        # its version-shape checks: they normalise only "0.4.23" / "0.4.22", so the "0.4.24" strings of this jar (manifest, version texts,
        # the inlined default-file header) count as changes there - section F here proves the classes equal 0.4.23's modulo the version
        expected = ("J: the 0.4.23 jar = 0.4.22's files + the 19 new named roll files", "E4: armReport keeps 0.4.22's texts word for word",
                    "H22: the 0.4.22 harness on the 0.4.23 jar", "F: AcroCfg.ensureDefaults and SkillCfg.load", "F: 0.4.22 -> 0.4.23 differs only")
        other = [f_ for f_ in fn_ if f_[:60] not in ctl_keys and not f_.startswith(expected)]
        mn = (list(re.finditer(r"(?m)^(\d+) checks passed, (\d+) failed", h23["new"])) or [None])[-1]
        mc_ = (list(re.finditer(r"(?m)^(\d+) checks passed, (\d+) failed", h23["ctl"])) or [None])[-1]
        # the control's own known failure: its nested chain H22 -> H21 -> H20 bottoms out at the 0.4.20 harness, which needs the
        # SkyySkills-0.4.19.jar that was tidied away (it prints "new , control " - no run); START TWICE is section M here instead
        pre = [f_ for f_ in fc_ if not f_.startswith("H22: the 0.4.22 harness on the 0.4.23 jar")]
        print("H23. control (0.4.23 jar) known failures: %s" % [f_[:90] for f_ in fc_])
        check(mn is not None and mc_ is not None and other == [] and int(mn.group(1)) > 10 and pre == []
              and int(mn.group(2)) == len([f_ for f_ in fn_ if f_.startswith(expected)]),
              "H23: the 0.4.23 harness on the 0.4.24 jar fails nothing it does not fail on the 0.4.23 jar beyond its version-shape checks (jar "
              "file list, version texts, class compare, nested H22): %s | new %s, control %s" % (other[:3], mn.group(0) if mn else h23["new"][-800:], mc_.group(0) if mc_ else h23["ctl"][-800:]))
        print("H23. 0.4.23 harness: on the 0.4.24 jar %s, on the 0.4.23 jar %s; extra on 0.4.24 = %s" % (
            mn.group(0) if mn else "?", mc_.group(0) if mc_ else "?", [f_[:100] for f_ in fn_ if f_[:60] not in ctl_keys]))
        hm = [ln for ln in h23["new"].splitlines() if ln.startswith(("H22.", "A. "))]
        print("H23. evidence (nested start-twice lines): %s" % hm[:4])
    # ---------------------------------------------------------------- M
    Mn, Mp = sts["new"], sts["prev"]
    vn = lambda x: json.dumps(x).replace(VERSION, "V").replace(PREV_VERSION, "V")
    check("error" not in Mn and "error" not in Mp and not Mn["load_fails"] and Mn["files"] > 0 and Mn["players"] > 0,
          "M: START TWICE ran on a scratch copy of the live data (%s files, %s player files): %s" % (Mn.get("files"), Mn.get("players"), (Mn.get("error") or Mp.get("error") or "")[-600:]))
    if "error" not in Mn and "error" not in Mp:
        check(vn(Mn["xp1"]) == vn(Mp["xp1"]) and Mn["changed1"] == Mp["changed1"] and vn(Mn["r1"]) == vn(Mp["r1"]),
              "M: start 1 on the live copy does exactly what 0.4.23 does (same files written, same xp.properties, same migration / load / "
              "curve results; version text aside): changed %s vs %s; %s" % (Mn["changed1"], Mp["changed1"],
                                                                           [k for k in Mn["r1"] if vn(Mn["r1"][k]) != vn(Mp["r1"].get(k))]))
        check(Mn["changed2"] == [] and Mn["players_same"] and vn(Mn["r2"]) == vn(Mp["r2"]),
              "M: start 2 changes nothing; the player files are never touched: %s" % Mn["changed2"])
        print("M. start twice on the live copy (%d files, %d players): start 1 wrote %s (= 0.4.23), start 2 nothing" % (
            Mn["files"], Mn["players"], Mn["changed1"] or "nothing"))
    # ---------------------------------------------------------------- F
    cmpd = json.load(open(cmpo))
    check(cmpd == {}, "F: 0.4.23 -> 0.4.24 METHOD BY METHOD (version strings normalised): no class differs: %s" % json.dumps(cmpd)[:1500])
    print("F. compare 0.4.23 -> 0.4.24: %s" % (json.dumps(cmpd)[:500] or "{}"))
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
