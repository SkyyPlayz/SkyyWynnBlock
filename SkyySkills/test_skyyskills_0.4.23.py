"""SkyySkills 0.4.23 - bare-JVM harness for THE ROLL REWORK + LOG FIXES (tools/skills_0_4_23_patch.py; Skyy LOCKED 2026-10-08 "make it roll the
moment you hit sprint ... no delay timer ... spam able"). The new parts run on the REAL classes of the 0.4.23 jar and, as the control, the SET
pin 0.4.22, with the REAL engine classes (HytaleServer.jar on the class path); the live save data is only ever READ and copied into scratch.

    python SkyySkills/test_skyyskills_0.4.23.py [--jar <SkyySkills-0.4.23.jar>] [--prev <SkyySkills-0.4.22.jar>] [--dir <scratch>]
                                                [--live <Skyy_SkyySkills folder>] [--keep] [--no22]

SECTIONS
  A   every class of both jars loads under -Xverify:all
  B   THE PRESS DETECTOR EXECUTED on the real Acro.tap / tapDone (both jars; 0.4.22 = the control, its tap-on-release): press while running
      = a roll on THAT tick; holding = no second roll (you stay sprinting); spam (no cooldown, a press during a roll waits for it); the buffer
      runs out; sprint resuming because W came back = no press; in the air / right after landing = no press; out of breath; the switch off;
      a busy chain (code 4) keeps the press, another refusal drops it; walking back (the client sends sprinting=false) = nothing to see
      REVIEW FIXES: a re-press while the client flags OUR roll 'rolling' waits and rolls at the roll's end (also a 1-tick 'rolling' lag);
      the landing roll still blocks + restarts the settle; Acro.dodgeNew executed (push on every roll, XP only past the gap)
  W   the wiring (bytecode): AcroSys.tick reads the MovementStates, then Stamina (only on a rise), then tap -> startRoll -> tapDone
  E   THE ENGINE (real asset stores + the real InteractionPacketGenerator, a setup packet consumer present = the server's startup), both jars:
      E1 the ENGINE ASSET VALIDATORS on every dodge file of the jar (decode, the codec's full validate, logOrThrowValidatorExceptions,
         contained assets) + the NEGATIVE CONTROL (a one-entry Parallel fails the same function); no Parallel with < 2 entries in any jar file
      E2 the jar's dodge files loaded in ONE batch like a pack: 'Missing interaction ..SkyySkills_Roll_..' lines (0.4.22: the 24-line kind;
         0.4.23: none), then RootInteraction.build() of the Dodge root - every op real (no placeholder SendMessage), and per direction the
         same op classes in both jars (the same roll)
      E3 InteractionManager.isOnCooldown (the real one, a real CooldownHandler) for the jar's Dodge root, 3 starts in a row: 0.4.22 (the
         vanilla root, 0.35 s default) = on cooldown from the 2nd; 0.4.23 (Cooldown 0) = never
      E4 the staff handover: vanilla staff items (their inline vars inherit Staff_Cast_*) -> SkyyArmory's files -> this jar's Staff_Cast_*
         overrides: the engine re-reads SkyyArmory's file under the SkyySkills pack (reproduced: label SkyySkills, path SkyyArmory's file);
         ManaGuard.armCheck() with AssetModule.findAssetPackForPath answering = INFO 're-read' (0.4.22 = the WARN Skyy saw); armReport keeps
         0.4.22's texts word for word for the same inputs
  J   the jar: 0.4.22's files + the 19 new named roll files + the Dodge root; the 6 roll files changed; every other file byte-identical
  H22 the 0.4.22 harness on the 0.4.23 jar (control: the 0.4.22 jar): nothing beyond its version-shape checks fails - its nested H21 / H20 ...
      = START TWICE on a scratch copy of the live data
  F   class compare 0.4.22 -> 0.4.23 METHOD BY METHOD: only the planned methods differ
  AU  the engine-access audit (every bytecode reference looked up with the JVM's own access rules; control refused)
"""
import os, sys, re, json, shutil, subprocess, zipfile, importlib.util, copy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, PREV_VERSION = "0.4.23", "0.4.22"
PKG = "com.skyy.skills."
ROLL_DIRS = ["Forward", "ForwardLeft", "ForwardRight", "Back", "BackLeft", "BackRight"]


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "rollfix01", "skills0423")))
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
    """the 0.4.15 harness module (JVM start, class loader, access audit, stand-ins) - imported, never run"""
    return tmod("test_skyyskills_0.4.15.py", "t0415")


def t20():
    """the 0.4.20 harness module (the method-by-method class compare) - imported, never run"""
    return tmod("test_skyyskills_0.4.20.py", "t0420")


# ============================================================================================ child: the press detector (one jar)
# a scenario = ticks (t ms, sprinting, horizontalIdle, onGround, rollOn, stamina read or -1, startRoll code if it fires)
def scen():
    S = {}
    run = lambda t, sp, ro=False, sta=-1.0, code=0: (t, sp, False, True, ro, sta, code)
    S["press"] = [run(0, False), run(33, True, sta=9.0)] + [run(t, True, ro=(66 <= t <= 280)) for t in range(66, 500, 33)] + [run(500, False)]
    S["quick_tap"] = [run(0, False), run(33, True, sta=9.0), run(100, False), run(133, False)]
    S["spam"] = [run(0, False), run(33, True, sta=9.0), run(80, False, ro=True), run(130, True, ro=True, sta=9.0), run(200, True, ro=True),
                 run(300, True), run(320, False), run(350, True, sta=9.0), run(383, True), run(420, False)]
    S["buffer_out"] = [run(0, False, ro=True), run(33, True, ro=True, sta=9.0)] + [run(t, True, ro=True) for t in range(66, 520, 33)] + [run(520, True)]
    S["w_again"] = [(0, False, True, True, False, -1.0, 0), (33, True, False, True, False, 9.0, 0), (66, True, False, True, False, -1.0, 0)]
    S["air_land"] = [(0, False, False, True, False, -1.0, 0), (33, False, False, False, False, -1.0, 0), (66, True, False, True, False, 9.0, 0),
                     (100, True, False, True, False, -1.0, 0), (200, False, False, True, False, -1.0, 0), (260, True, False, True, False, 9.0, 0),
                     (293, True, False, True, False, -1.0, 0)]
    S["air_press"] = [(0, False, False, False, False, -1.0, 0), (33, True, False, False, False, 9.0, 0), (66, True, False, False, False, -1.0, 0)]
    S["breath"] = [run(0, False), run(33, True, sta=0.3), run(66, True)]
    S["busy"] = [run(0, False), run(33, True, sta=9.0, code=4), run(66, True, code=0), run(100, True)]
    S["refused"] = [run(0, False), run(33, True, sta=9.0, code=3), run(66, True), run(100, True)]
    S["back"] = [run(t, False) for t in range(0, 400, 33)]          # walking back + the sprint key: the client reports sprinting = false
    # review fix: MovementStates.rolling (8th field). If the client flags OUR roll as 'rolling', a re-press during it waits and fires when
    # the roll ends; a 'rolling' tick that outlasts the roll effect by a tick delays it one tick; the LANDING roll ('rolling' with no roll
    # of ours) still blocks and restarts the 150 ms settle.
    rr = lambda t, sp, ro=False, sta=-1.0, rol=False: (t, sp, False, True, ro, sta, 0, rol)
    S["spam_rolling"] = [rr(0, False), rr(33, True, sta=9.0), rr(66, False, ro=True, rol=True), rr(100, True, ro=True, sta=9.0, rol=True),
                         rr(166, True, ro=True, rol=True), rr(283, True), rr(316, True)]
    S["rolling_lag"] = [rr(0, False), rr(33, True, sta=9.0), rr(66, False, ro=True, rol=True), rr(100, True, ro=True, sta=9.0, rol=True),
                        rr(166, True, ro=True, rol=True), rr(283, True, rol=True), rr(316, True), rr(350, True)]
    S["landing_roll"] = [(0, False, False, True, False, -1.0, 0), (33, False, False, False, False, -1.0, 0), rr(66, False, rol=True),
                         rr(100, True, sta=9.0, rol=True), rr(133, False), rr(200, True, sta=9.0), rr(300, False), rr(333, True, sta=9.0), rr(366, True)]
    return S


def run_child(jar, out, mode):
    from jpype import JClass, JLong, JDouble
    T = t15()
    res, path = T.common(jar, [])
    if res["load_fails"]:
        json.dump(res, open(out, "w"), indent=1)
        return
    D = res["data"]
    Acro, ACfg = JClass(PKG + "Acro"), JClass(PKG + "AcroCfg")
    UUID, MST = JClass("java.util.UUID"), JClass("com.hypixel.hytale.protocol.MovementStates")
    B = {}
    base = 1000000

    def play(name, ticks, tap_on=True):
        ACfg.TAP_ON = tap_on
        s = Acro.state(UUID.fromString("00000000-0000-0000-0000-%012d" % (abs(hash(name)) % 10 ** 12)))
        fired, codes = [], []
        for tk_ in ticks:
            (t, sp, idle, ground, ro, sta, code), rol = tk_[:7], (tk_[7] if len(tk_) > 7 else False)
            m = MST()
            m.sprinting, m.horizontalIdle, m.onGround, m.running, m.idle, m.rolling = sp, idle, ground, not idle, idle, rol
            if bool(Acro.tap(s, m, JLong(base + t), ro, JDouble(sta))):
                fired.append(t)
                codes.append(code)
                Acro.tapDone(s, JLong(base + t), code)
        ACfg.TAP_ON = True
        return {"fired": fired, "codes": codes, "started": float(s[298]), "pending": float(s[296])}
    for name, ticks in sorted(scen().items()):
        B[name] = play(name, ticks)
    B["off"] = play("off", scen()["press"], tap_on=False)
    B["consts"] = [int(Acro.TAP_CD_MS), int(Acro.TAP_SETTLE_MS)]
    # review fix: Acro.dodgeNew EXECUTED (the new-roll bookkeeping dodge() calls on each roll edge): 3 rolls 0 / 260 / 520 ms apart with
    # acro.dodgeCooldownMs 400 + moved enough: the push is scheduled on EVERY roll, XP only on the 1st and the 3rd (the XP gap)
    try:
        from jpype import JArray, JBoolean
        ACfg.DODGE_BOOST, ACfg.DODGE_CD, ACfg.DODGE_XP, ACfg.DODGE_MOVE = True, JLong(400), JDouble(3.0), JDouble(2.0)
        sd = JArray(JDouble)(320)
        dn = []
        for t_, mv in ((0, 5.0), (260, 5.0), (520, 5.0)):
            sd[291] = JDouble(mv)
            sd[23] = JDouble(0.0)
            Acro.dodgeNew(sd, JLong(base + t_), JBoolean(False))
            dn.append([t_, float(sd[23]) - base if float(sd[23]) > 0 else 0.0, float(sd[11])])
        sd2 = JArray(JDouble)(320)
        sd2[291] = JDouble(5.0)
        Acro.dodgeNew(sd2, JLong(base), JBoolean(True))
        B["dodgeNew"] = {"rolls": dn, "creative_xp": float(sd2[11]), "creative_push": float(sd2[23]) - base}
    except Exception as e:
        B["dodgeNew"] = "no dodgeNew: %s" % str(e)[:200]
    try:
        B["buffer"] = int(Acro.PRESS_BUFFER_MS)
    except Exception:
        B["buffer"] = None
    D["B"] = B
    json.dump(res, open(out, "w"), indent=1)


# ============================================================================================ child: the bytecode wiring
def run_wiring(jar, out):
    import jpype
    from jpype import JClass
    import skyybuild as SB
    jpype.startJVM(SB._jvm(), "-XX:-UsePerfData", classpath=[SB.JAVASSIST], convertStrings=True)
    cp = JClass("javassist.ClassPool")(False)
    cp.insertClassPath(jar)
    cp.appendClassPath(SB.SERVER_JAR)
    cp.appendSystemPath()
    CP = JClass("javassist.bytecode.ConstPool")
    cc = cp.get(PKG + "AcroSys")
    m = [x for x in cc.getDeclaredMethods() if str(x.getName()) == "tick"][0]
    it, cpool = m.getMethodInfo().getCodeAttribute().iterator(), m.getMethodInfo().getConstPool()
    r = []
    while it.hasNext():
        p = it.next()
        op = it.byteAt(p)
        if op in (0xb6, 0xb7, 0xb8, 0xb9):
            i = it.u16bitAt(p + 1)
            r.append(str(cpool.getInterfaceMethodrefName(i)) if cpool.getTag(i) == CP.CONST_InterfaceMethodref else str(cpool.getMethodrefName(i)))
        elif op == 0xb4:
            r.append("." + str(cpool.getFieldrefName(it.u16bitAt(p + 1))))
    IP, PS, BOS = JClass("javassist.bytecode.InstructionPrinter"), JClass("java.io.PrintStream"), JClass("java.io.ByteArrayOutputStream")
    lst = {}
    for cn, mn in (("AcroCfg", "ensureDefaults"), ("SkillCfg", "load")):
        mm = [x for x in cp.get(PKG + cn).getDeclaredMethods() if str(x.getName()) == mn][0]
        bos = BOS()
        IP(PS(bos)).print_(mm)
        t = re.sub(r"#\d+ = ", "", str(bos.toString()))
        t = re.sub(r"(?m)^\s*\d+: ", "", t).replace("ldc_w ", "ldc ")
        lst[cn + "." + mn] = re.sub(r"(?m)^((?:goto|goto_w|if\w*|jsr) )-?\d+", r"\1L", t)
    calls = {}
    for cn, mn in (("Acro", "dodge"), ("Acro", "tap")):          # review fixes: dodge -> dodgeNew, tap -> tapHard (not tapBlocked)
        mm = [x for x in cp.get(PKG + cn).getDeclaredMethods() if str(x.getName()) == mn][0]
        it2, cp2 = mm.getMethodInfo().getCodeAttribute().iterator(), mm.getMethodInfo().getConstPool()
        cl = []
        while it2.hasNext():
            p2 = it2.next()
            if it2.byteAt(p2) in (0xb6, 0xb7, 0xb8):
                cl.append(str(cp2.getMethodrefName(it2.u16bitAt(p2 + 1))))
        calls[cn + "." + mn] = cl
    json.dump({"tick": r, "lst": lst, "calls": calls}, open(out, "w"), indent=1)


# ============================================================================================ child: the engine (one jar)
def run_engine(jar, out, mode):
    import jpype
    from jpype import JClass, JArray, JString, JImplements, JOverride, JObject
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
    # the server singletons the stores read (the SkyyArmory harness way)
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

    @JImplements("java.util.function.Consumer")
    class Sink:
        def __init__(self): self.n = 0

        @JOverride
        def accept(self, p): self.n += 1
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
    sink = Sink()
    HAS.SETUP_PACKET_CONSUMERS.add(sink)          # the server's startup: every loaded batch builds its client packet
    # the interaction Type codecs exactly as InteractionModule.setup registers them (read from its bytecode)
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
    R["codecs"] = len(regs)
    AEI, ADT = JClass("com.hypixel.hytale.assetstore.AssetExtraInfo"), JClass("com.hypixel.hytale.assetstore.AssetExtraInfo$Data")
    RJR = JClass("com.hypixel.hytale.codec.util.RawJsonReader")
    EFXc = JClass("com.hypixel.hytale.server.core.asset.type.entityeffect.config.EntityEffect")
    ITMc = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    az = zipfile.ZipFile(os.path.join(os.path.dirname(SB.SERVER_JAR), "..", "Assets.zip"))
    jz = zipfile.ZipFile(jar)
    work = os.path.join(SCRATCH, "eng-" + mode)
    os.makedirs(work, exist_ok=True)

    def put(sub, name, text):
        d = os.path.join(work, sub)
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, name)
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
        return Paths.get(p)

    def jlist(xs):
        l_ = ArrayList()
        for x_ in xs:
            l_.add(x_)
        return l_

    def loadp(cls, pack, paths):
        l_ = ArrayList()
        for p in paths:
            l_.add(p)
        r = AR.getAssetStore(cls.class_).loadAssetsFromPaths(pack, l_)
        return not r.hasFailed()
    # the vanilla stat types (Stamina / Mana ...), their effect hooks left out (only the ids matter here)
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
    HLOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkillsHarness")
    KNOWN = set(os.path.basename(n).rsplit(".", 1)[0] for n in list(az.namelist()) + list(jz.namelist()))

    def validate(cls, key, text):
        """the engine's validators on one asset: decode, the codec's full validate, logOrThrowValidatorExceptions, the contained assets.
        A 'does not exist' line for a name that IS in Assets.zip or this jar = the bare JVM's empty stores (kept apart as a NOTE)"""
        n0 = len(records())
        st = AR.getAssetStore(cls.class_)
        ei = AEI(Paths.get(key + ".json"), ADT(cls.class_, key, None))
        try:
            o = st.getCodec().decodeJsonAsset(RJR.fromJsonString(text), ei)
        except Exception as e:
            return None, ["decode: " + str(e)[:300]], []
        prob, env = [], []
        uk = [str(x) for x in ei.getUnknownKeys()]
        if uk:
            prob.append("unknown keys %s" % uk)
        try:
            st.getCodec().validate(o, ei)
        except Exception as e:
            prob.append("validate threw %s" % str(e)[:300])
        vr = ei.getValidationResults()
        try:
            if vr is not None:
                vr.logOrThrowValidatorExceptions(HLOG)
        except Exception as e:
            for ln in re.findall(r"FAIL: ([^\n]*)", str(e)):
                m_ = re.search(r"'([^']+)'", ln)
                (env if (m_ and m_.group(1) in KNOWN and ("doesn't exist" in ln or "does not exist" in ln)) else prob).append(ln[:300])
        try:
            ei.getData().loadContainedAssets(False)
        except Exception as e:
            prob.append("contained assets: %s" % str(e)[:300])
        for lv, m_ in records()[n0:]:          # a WARNING-only result (the deprecated CancelOnItemChange default) is no failure
            for ln in re.findall(r"FAIL: ([^\n]*)", m_):
                m2_ = re.search(r"'([^']+)'", ln)
                (env if (m2_ and m2_.group(1) in KNOWN and ("doesn't exist" in ln or "does not exist" in ln)) else prob).append(ln[:300])
        return o, prob, env
    # ---- E1 validators: NEGATIVE CONTROL first (a one-entry Parallel - what once stopped the server), then every dodge file of the jar
    neg = validate(INTc, "SkyySkillsHarness_OneParallel", json.dumps({"Type": "Simple", "RunTime": 0.1, "Next": {"Type": "Parallel", "Interactions": [{"Interactions": ["Stamina_Bar_Flash"]}]}}))
    pos = validate(INTc, "SkyySkillsHarness_TwoParallel", json.dumps({"Type": "Simple", "RunTime": 0.1, "Next": {"Type": "Parallel", "Interactions": [{"Interactions": ["Stamina_Bar_Flash"]}, {"Interactions": ["Stamina_Bar_Flash"]}]}}))
    R["neg"] = [neg[0] is not None, neg[1][:2], pos[0] is not None, pos[1][:2]]
    # the vanilla pieces the rolls name first: the i-frames effect + the 2 vanilla side looks (EntityEffect), Stamina_Bar_Flash, Dodge_Left / Right
    for n in ("Server/Entity/Effects/Movement/Dodge_Invulnerability.json",):
        o, p, e = validate(EFXc, os.path.basename(n)[:-5], az.read(n).decode("utf-8-sig"))
        if o is not None:
            AR.getAssetStore(EFXc.class_).loadAssets("Hytale:Hytale", jlist([o]))
    van = [n for n in az.namelist() if n.startswith("Server/Item/Interactions/") and os.path.basename(n) in ("Stamina_Bar_Flash.json", "Dodge_Left.json", "Dodge_Right.json")]
    R["van_load"] = loadp(INTc, "Hytale:Hytale", [put("H", os.path.basename(n), az.read(n).decode("utf-8-sig")) for n in van])
    dfiles = sorted(n for n in jz.namelist() if n.endswith(".json") and (n.startswith("Server/Item/Interactions/Dodge") or n == "Server/Item/RootInteractions/Dodge.json"
                                                                        or (n.startswith("Server/Entity/Effects/Movement/Dodge_"))))
    R["dfiles"] = dfiles
    # the effects into their store (the rolls apply them)
    effs = [n for n in dfiles if "/Effects/" in n]
    R["eff_load"] = loadp(EFXc, "Skyy:%s SkyySkills" % mode, [put("S/fx", os.path.basename(n), jz.read(n).decode("utf-8")) for n in effs])
    # ---- E2 the jar's dodge interactions in ONE batch, like a pack load (real file paths, the packet generator on)
    ints = [n for n in dfiles if n.startswith("Server/Item/Interactions/")]
    n0 = len(records())
    s0 = sink.n
    R["load"] = loadp(INTc, "Skyy:%s SkyySkills" % mode, [put("S/int", os.path.basename(n), jz.read(n).decode("utf-8")) for n in ints])
    R["missing"] = [m_ for lv, m_ in records()[n0:] if "Missing interaction" in m_ and "SkyySkills_Roll" in m_]
    R["missing_kind"] = len([m_ for m_ in R["missing"] if re.search(r"\*\*SkyySkills_Roll_\w+_Next_Interactions_\d", m_)])
    R["packets"] = sink.n - s0
    rootn = "Server/Item/RootInteractions/Dodge.json"
    rtext = jz.read(rootn).decode("utf-8") if rootn in jz.namelist() else az.read(rootn).decode("utf-8-sig")
    R["root_from"] = "jar" if rootn in jz.namelist() else "Assets.zip"
    R["root_load"] = loadp(ROOTc, ("Skyy:%s SkyySkills" % mode) if rootn in jz.namelist() else "Hytale:Hytale", [put("S/root", "Dodge.json", rtext)])
    root = ROOTc.getAssetMap().getAsset("Dodge")
    ops, bad = [], []
    try:
        root.build()
        for i in range(int(root.getOperationMax())):
            op = root.getOperation(i)
            inner = op.getInnerOperation()
            if inner is not None and INTc.class_.isInstance(inner):
                ops.append([str(inner.getClass().getSimpleName()), str(inner.getId())])
                if SMI.class_.isInstance(inner):
                    bad.append("placeholder for " + str(inner.getId()))
            else:
                ops.append([str(op.getClass().getSimpleName()), None])
    except Exception as e:
        bad.append("build: " + str(e)[:300])
    R["ops"], R["bad"] = ops, bad
    # every roll's own steps (each interaction's compiled chain): the op classes in order, per direction
    per = {}
    for d_ in ROLL_DIRS:
        rid = "SkyySkills_Roll_" + d_
        tmp_root = ROOTc("SkyySkillsHarness_" + d_, JArray(JString)([rid]))
        AR.getAssetStore(ROOTc.class_).loadAssets("Test:Pack", jlist([tmp_root]))
        rr = ROOTc.getAssetMap().getAsset("SkyySkillsHarness_" + d_)
        cl = []
        try:
            rr.build()
            for i in range(int(rr.getOperationMax())):
                inner = rr.getOperation(i).getInnerOperation()
                if inner is not None and INTc.class_.isInstance(inner):
                    cl.append(str(inner.getClass().getSimpleName()))
                    if SMI.class_.isInstance(inner):
                        bad.append("%s: placeholder %s" % (rid, inner.getId()))
        except Exception as e:
            cl.append("build failed " + str(e)[:200])
        per[d_] = cl
    R["per"] = per
    # ---- E1 (after E2: the validators' loadContainedAssets puts inline children into the store, which would hide E2's warnings)
    val = {}
    ctl_fx = validate(EFXc, "Dodge_Left_VanillaControl", az.read("Server/Entity/Effects/Movement/Dodge_Left.json").decode("utf-8-sig"))[1]
    R["fx_control"] = ctl_fx
    for n in dfiles:
        cls = ROOTc if "/RootInteractions/" in n else (EFXc if "/Effects/" in n else INTc)
        o, p, e = validate(cls, os.path.basename(n)[:-5], jz.read(n).decode("utf-8"))
        if cls is EFXc:          # the bare JVM's EntityEffect validate throws the SAME for the vanilla Dodge_Left (no stat registry): test bed
            e = e + [x for x in p if x in ctl_fx]
            p = [x for x in p if x not in ctl_fx]
        val[n] = {"ok": o is not None, "prob": p, "env": e}
    R["val"] = val
    # ---- E3 the real InteractionManager.isOnCooldown for the loaded Dodge root, 3 starts in a row (a real CooldownHandler)
    CtNM = JClass("javassist.CtNewMethod")
    CP_ = "com.hypixel.hytale.component."
    sb = CPj.makeClass("skyyh23.NullBuf", CPj.get(CP_ + "CommandBuffer"))
    sb.addField(JClass("javassist.CtField").make("public static Object RES = null;", sb))
    sb.addMethod(CtNM.make("public " + CP_ + "Component getComponent(" + CP_ + "Ref r, " + CP_ + "ComponentType t) { return null; }", sb))
    sb.addMethod(CtNM.make("public " + CP_ + "Resource getResource(" + CP_ + "ResourceType t) { return (" + CP_ + "Resource) RES; }", sb))
    sb.writeFile(hcls)
    NullBuf = JClass("skyyh23.NullBuf")
    EMc = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
    em = U.allocateInstance(EMc.class_)
    setstatic_of_type(EMc, em)
    jfield(EMc, "playerComponentType").set(em, U.allocateInstance(jfield(EMc, "playerComponentType").getType()))
    IMG = JClass("com.hypixel.hytale.server.core.entity.InteractionManager")
    CDH = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.CooldownHandler")
    IT = JClass("com.hypixel.hytale.protocol.InteractionType")
    isc = IMG.class_.getDeclaredMethod("isOnCooldown", JClass("com.hypixel.hytale.component.Ref").class_, IT.class_, ROOTc.class_, JClass("java.lang.Boolean").TYPE)
    isc.setAccessible(True)
    im = U.allocateInstance(IMG.class_)
    jfield(IMG, "commandBuffer").set(im, U.allocateInstance(NullBuf.class_))
    jfield(IMG, "cooldownHandler").set(im, CDH())
    ref = JClass("com.hypixel.hytale.component.Ref")(None, 3)
    cds = []
    for i in range(3):
        try:
            cds.append(bool(isc.invoke(im, JArray(JClass("java.lang.Object"))([ref, IT.Dodge, root, JClass("java.lang.Boolean").FALSE]))))
        except Exception as e:
            c = e
            while c.getCause() is not None:
                c = c.getCause()
            cds.append("threw " + str(c)[:200])
    R["cooldown"] = [None if root.getCooldown() is None else float(root.getCooldown().cooldown), cds,
                     float(JClass(PI + "InteractionTypeUtils").getDefaultCooldown(IT.Dodge))]
    # ---- E4 the staff handover: reproduce the engine's re-read, then this jar's ManaGuard.armCheck with AssetModule answering
    MC = JClass(PKG + "ManaCost")
    MG = JClass(PKG + "ManaGuard")
    arm_ids = [str(x) for x in MC.ARM_IDS]
    bo_ids = ["Weapon_Staff_Bo_Wood", "Weapon_Staff_Bo_Bamboo"]
    SKP, ARP = "Skyy:%s SkyySkills" % mode, "Skyy:0.1.13 SkyyArmory"
    hroot, aroot, sroot = os.path.join(work, "packH"), os.path.join(work, "packA"), os.path.join(work, "packS")

    def strip(j):
        return dict((k, v) for k, v in j.items() if k not in ("Next", "Failed"))
    vi = []
    for b in ("Staff_Cast_Cost", "Staff_Cast_Summon_Charged"):
        n = [x for x in az.namelist() if x.startswith("Server/Item/Interactions/") and x.endswith("/%s.json" % b)][0]
        vi.append(put("packH/Server/Item/Interactions", b + ".json", json.dumps(strip(json.loads(az.read(n).decode("utf-8-sig"))))))
    R["h_ints"] = loadp(INTc, "Hytale:Hytale", vi)
    vp, ap = [], []
    for s_ in arm_ids + bo_ids:
        n = [x for x in az.namelist() if x.startswith("Server/Item/Items/") and x.endswith("/%s.json" % s_)][0]
        j = json.loads(az.read(n).decode("utf-8-sig"))
        j = dict((k, v) for k, v in j.items() if k in ("TranslationProperties", "InteractionVars", "Categories", "Tags"))
        j["InteractionVars"] = dict((k, v) for k, v in (j.get("InteractionVars") or {}).items() if isinstance(v, dict))
        vp.append(put("packH/Server/Item/Items", s_ + ".json", json.dumps(j)))
        # SkyyArmory's item: no vars of its own (its own roots), the minimum the bare JVM can decode
        ap.append(put("packA/Server/Item/Items", s_ + ".json", json.dumps({"TranslationProperties": {"Name": "server.items.%s.name" % s_},
                                                                           "Categories": ["Items.Weapons"], "Tags": {"Family": ["Staff"]}})))
    R["h_items"] = loadp(ITMc, "Hytale:Hytale", vp)
    R["a_items"] = loadp(ITMc, ARP, ap)
    imap = ITMc.getAssetMap()
    R["after_armory"] = sorted(set(str(imap.getAssetPack(s_)) for s_ in arm_ids + bo_ids))
    sp = []
    for b in ("Staff_Cast_Cost", "Staff_Cast_Summon_Charged"):
        n = [x for x in jz.namelist() if x.startswith("Server/Item/Interactions/") and x.endswith("/%s.json" % b)][0]
        sp.append(put("packS/Server/Item/Interactions", b + ".json", json.dumps(strip(json.loads(jz.read(n).decode("utf-8"))))))
    R["s_ints"] = loadp(INTc, SKP, sp)
    R["after_skills"] = dict((s_, [str(imap.getAssetPack(s_)), os.path.normcase(str(imap.getPath(s_))).startswith(os.path.normcase(aroot))]) for s_ in arm_ids + bo_ids)
    # the check, first with no AssetModule (what 0.4.22 had to go on), then with the engine's pack registry answering
    R["arm_nomod"] = [str(x) for x in MG.armCheck()]
    AP = JClass("com.hypixel.hytale.assetstore.AssetPack")
    PSrc = AP.class_.getDeclaredConstructors()[0].getParameterTypes()[6]
    mods = PSrc.getEnumConstants()[2]
    packs = ArrayList()
    for root_, name_ in ((hroot, "Hytale:Hytale"), (aroot, ARP), (sroot, SKP)):
        packs.add(AP(Paths.get(root_), name_, Paths.get(root_), Paths.get(root_).getFileSystem(), False, None, mods))
    AMc = JClass("com.hypixel.hytale.server.core.asset.AssetModule")
    am = U.allocateInstance(AMc.class_)
    jfield(AMc, "assetPacks").set(am, packs)
    setstatic_of_type(AMc, am)
    R["arm"] = [str(x) for x in MG.armCheck()]
    try:
        R["filePack"] = [str(MG.filePack(imap, arm_ids[0])), str(MG.filePack(imap, "No_Such_Item_ZZ")), str(MG.filePack(None, arm_ids[0]))]
    except Exception as e:
        R["filePack"] = "missing: " + str(e)[:100]
    # armReport's texts for fixed inputs (both jars must agree word for word)
    cases = {"all": [ARP] * len(arm_ids), "none": [None] * len(arm_ids), "mixed": [ARP] * (len(arm_ids) - 2) + ["Skyy:9 Other", None],
             "skills": [SKP] * len(arm_ids)}
    R["armReport"] = dict((k, [str(x) for x in MG.armReport(JArray(JString)(v))]) for k, v in cases.items())
    try:
        R["armReport2"] = {"reread": [str(x) for x in MG.armReport2(JArray(JString)([SKP] * len(arm_ids)), JArray(JString)([ARP] * len(arm_ids)))],
                           "other_file": [str(x) for x in MG.armReport2(JArray(JString)([SKP] * len(arm_ids)), JArray(JString)([SKP] * len(arm_ids)))]}
    except Exception as e:
        R["armReport2"] = "missing: " + str(e)[:100]
    setstatic_of_type(AMc, None)
    json.dump(R, open(out, "w"), indent=1)


# ============================================================================================ parent
def main():
    if "--mkfake" in sys.argv:
        return t15().run_mkfake(arg("--mkfake"))
    if "--child" in sys.argv:
        return run_child(arg("--child"), arg("--out"), arg("--mode"))
    if "--engine" in sys.argv:
        return run_engine(arg("--engine"), arg("--out"), arg("--mode"))
    if "--wiring" in sys.argv:
        return run_wiring(arg("--wiring"), arg("--out"))
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
        sys.exit("--dir must be a sub-folder of a task folder inside tools/dev/scratch/ (e.g. tools/dev/scratch/<task>/skills0423; that folder is "
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
            p = subprocess.run([sys.executable, me, "--child", jar, "--out", outp, "--mode", mode, "--dir", SCRATCH], env=env, stdout=lf, stderr=subprocess.STDOUT)
        check(p.returncode == 0 and os.path.isfile(outp), "child JVM (%s) ran (log %s)" % (mode, logp))
        if os.path.isfile(outp):
            outs[mode] = json.load(open(outp))
        ver = VERSION if mode == "new" else PREV_VERSION
        oute = os.path.join(SCRATCH, "eng-%s.json" % mode)
        loge = os.path.join(SCRATCH, "eng-%s.log" % mode)
        with open(loge, "wb") as lf:
            p = subprocess.run([sys.executable, me, "--engine", jar, "--out", oute, "--mode", ver, "--dir", SCRATCH], env=env, stdout=lf, stderr=subprocess.STDOUT)
        check(p.returncode == 0 and os.path.isfile(oute), "engine child JVM (%s) ran (log %s)" % (mode, loge))
        if os.path.isfile(oute):
            engs[mode] = json.load(open(oute))
    wo = os.path.join(SCRATCH, "wiring.json")
    pw = subprocess.run([sys.executable, me, "--wiring", JAR, "--out", wo, "--dir", SCRATCH], env=env, capture_output=True)
    check(pw.returncode == 0 and os.path.isfile(wo), "wiring child ran: %s" % pw.stderr[-500:])
    wop = os.path.join(SCRATCH, "wiring-prev.json")
    pw = subprocess.run([sys.executable, me, "--wiring", PREV_JAR, "--out", wop, "--dir", SCRATCH], env=env, capture_output=True)
    check(pw.returncode == 0 and os.path.isfile(wop), "wiring child (0.4.22) ran: %s" % pw.stderr[-500:])
    cmpo = os.path.join(SCRATCH, "compare.json")
    pc = subprocess.run([sys.executable, me, "--compare", JAR, "--prevjar", PREV_JAR, "--out", cmpo, "--dir", SCRATCH], env=env, capture_output=True)
    check(pc.returncode == 0 and os.path.isfile(cmpo), "class compare child ran: %s" % pc.stderr[-500:])
    auo = os.path.join(SCRATCH, "audit.json")
    pa = subprocess.run([sys.executable, me, "--audit", JAR, "--fake", fake, "--out", auo, "--dir", SCRATCH], env=env, capture_output=True)
    check(pa.returncode == 0 and os.path.isfile(auo), "engine-access audit child ran: %s" % pa.stderr[-500:])
    h22 = None
    if "--no22" not in sys.argv:
        h22 = {}
        for tag, jj in (("new", JAR), ("ctl", PREV_JAR)):
            ph = subprocess.run([sys.executable, os.path.join(HERE, "test_skyyskills_0.4.22.py"), "--jar", jj, "--prev",
                                 os.path.join(HERE, "SkyySkills-0.4.21.jar"), "--dir", os.path.join(SCRATCH, "h22-" + tag), "--live", LIVE_DIR],
                                env=env, capture_output=True)
            h22[tag] = ph.stdout.decode("utf-8", "replace")
    if FAILS:
        return finish()
    for mode in ("new", "prev"):
        r = outs[mode]
        check(not r["load_fails"] and r["loaded"] == r["classes"], "A (%s): %d / %d classes load under -Xverify:all %s" % (mode, r["loaded"], r["classes"], r["load_fails"][:3]))
    if FAILS:
        return finish()
    N, P = outs["new"]["data"]["B"], outs["prev"]["data"]["B"]
    print("A. both jars: every class loads under -Xverify:all (%d / %d classes)" % (outs["new"]["loaded"], outs["prev"]["loaded"]))
    # ---------------------------------------------------------------- B
    f = lambda R_, k: R_[k]["fired"]
    check(N["consts"] == [0, 150] and N["buffer"] == 350 and P["consts"] == [400, 300] and P["buffer"] is None,
          "B: no own cooldown (TAP_CD_MS 0, was 400), TAP_SETTLE_MS 150 (was 300), PRESS_BUFFER_MS 350 (new): %s %s | 0.4.22 %s" % (N["consts"], N["buffer"], P["consts"]))
    check(f(N, "press") == [33] and N["press"]["started"] == 1.0 and f(P, "press") == [],
          "B: pressing sprint while running rolls ON THE PRESS TICK (33 ms) and holding the key never rolls again (you stay sprinting); 0.4.22 "
          "never rolled on a hold (it waited for a release under 200 ms): %s | 0.4.22 %s" % (N["press"], P["press"]))
    check(f(N, "quick_tap") == [33] and f(P, "quick_tap") == [100],
          "B: a quick tap rolls at the PRESS (33) - 0.4.22 rolled at the release (100): %s | 0.4.22 %s" % (f(N, "quick_tap"), f(P, "quick_tap")))
    check(f(N, "spam") == [33, 300, 350] and N["spam"]["started"] == 3.0 and f(P, "spam") == [320],
          "B: SPAM - 3 presses in 0.35 s = 3 rolls: the 2nd (during the roll) waits for the roll to end (300), the 3rd rolls at once (350); "
          "no cooldown. 0.4.22: 1 roll (own 0.4 s cooldown): %s | 0.4.22 %s" % (f(N, "spam"), f(P, "spam")))
    check(f(N, "buffer_out") == [] and N["buffer_out"]["pending"] == 0.0,
          "B: a press during a roll that lasts past PRESS_BUFFER_MS is dropped (no late roll): %s" % N["buffer_out"])
    check(f(N, "w_again") == [] and f(N, "air_press") == [] and f(N, "air_land") == [260] and f(N, "breath") == [] and f(N, "off") == [],
          "B: no false rolls - sprint resuming because W came back (the tick before was idle), a press in the air, sprint resuming ON landing "
          "(within 150 ms of the air tick; a real press 227 ms after it rolls), under 0.5 Stamina, the switch off: %s" % (
              [f(N, k) for k in ("w_again", "air_press", "air_land", "breath", "off")]))
    check(f(N, "busy") == [33, 66] and N["busy"]["codes"] == [4, 0] and N["busy"]["started"] == 1.0 and f(N, "refused") == [33] and N["refused"]["started"] == 0.0,
          "B: startRoll code 4 (a running chain blocks Dodge now) keeps the press - it rolls the next tick (code 0); another refusal (3) drops "
          "it, nothing counted: %s %s" % (N["busy"], N["refused"]))
    check(f(N, "back") == [] and f(P, "back") == [],
          "B: walking back with the sprint key = the server sees sprinting false on every tick (no flag, vanilla has no back sprint) -> "
          "nothing to roll on, in both jars (no fake trigger): %s" % f(N, "back"))
    check(f(N, "spam_rolling") == [33, 283] and N["spam_rolling"]["started"] == 2.0,
          "B (review fix): a re-press DURING our roll while the client flags 'rolling' is kept and rolls when the roll ends (283) - not dropped, "
          "no 150 ms settle after it: %s | 0.4.22 %s" % (N["spam_rolling"], f(P, "spam_rolling")))
    check(f(N, "rolling_lag") == [33, 316] and N["rolling_lag"]["started"] == 2.0,
          "B (review fix): 'rolling' one tick past the roll effect delays the waiting press one tick (316), no loss: %s" % N["rolling_lag"])
    check(f(N, "landing_roll") == [333],
          "B (review fix): the LANDING roll ('rolling' with no roll of ours) still blocks a press (100) and restarts the 150 ms settle (200 = "
          "100 ms after it, no roll); a press 233 ms after it rolls (333): %s | 0.4.22 (tap on release) %s" % (f(N, "landing_roll"), f(P, "landing_roll")))
    dnr = N.get("dodgeNew")
    check(isinstance(dnr, dict) and [r_[1] for r_ in dnr["rolls"]] == [100.0, 360.0, 620.0] and [r_[2] for r_ in dnr["rolls"]] == [3.0, 3.0, 6.0]
          and dnr["creative_xp"] == 0.0 and dnr["creative_push"] == 100.0 and isinstance(P.get("dodgeNew"), str),
          "B (review fix): Acro.dodgeNew - every roll schedules its push 100 ms later (also the one 260 ms after the last, inside the 400 ms XP "
          "gap); XP only when the gap has passed (3, 3, 6); Creative: push, no XP; 0.4.22 has no dodgeNew: %s | 0.4.22 %s" % (dnr, P.get("dodgeNew")))
    print("B. press detector: press %s, quick %s, spam %s, busy %s | 0.4.22 press %s, quick %s, spam %s" % (
        f(N, "press"), f(N, "quick_tap"), f(N, "spam"), f(N, "busy"), f(P, "press"), f(P, "quick_tap"), f(P, "spam")))
    # ---------------------------------------------------------------- W
    tk = json.load(open(wo))["tick"]
    try:
        i_g = max(i for i, x in enumerate(tk) if x == "getMovementStates" and i < tk.index("tap"))
        i_sp = [i for i, x in enumerate(tk) if x == ".sprinting" and i_g < i < tk.index("tap")]
        i_st = [i for i, x in enumerate(tk) if x == "stamina"]
        ok_w = (i_sp and len(i_st) == 1 and i_g < i_sp[0] < i_st[0] < tk.index("tap") < tk.index("startRoll") < tk.index("tapDone"))
    except ValueError:
        ok_w = False
    check(ok_w, "W: AcroSys.tick reads getMovementStates, then .sprinting (the rise), then Acro.stamina, then tap -> startRoll -> tapDone: %s" % (
        [x for x in tk if x in ("getMovementStates", ".sprinting", "stamina", "tap", "startRoll", "tapDone", "tapWatch", "rollFx")][-12:]))
    wc = json.load(open(wo)).get("calls", {})
    check("dodgeNew" in wc.get("Acro.dodge", []) and "tapHard" in wc.get("Acro.tap", []) and "tapBlocked" not in wc.get("Acro.tap", []),
          "W (review fixes): Acro.dodge calls dodgeNew on a roll edge; Acro.tap uses tapHard (rolling handled apart), not tapBlocked: %s" % wc)
    # ---------------------------------------------------------------- E
    En, Ep = engs["new"], engs["prev"]
    check(En["neg"][0] and any("Array size" in x for x in En["neg"][1]) and En["neg"][2] and not En["neg"][3],
          "E1 NEGATIVE CONTROL: the validator function refuses a one-entry Parallel with the engine's own 'Array size' message and passes it "
          "with 2 entries: %s" % En["neg"])
    vbad = dict((n, v) for n, v in En["val"].items() if not v["ok"] or v["prob"])
    venv = sorted(set(x for v in En["val"].values() for x in v["env"]))
    check(len(En["dfiles"]) == 31 and not vbad, "E1: the ENGINE ASSET VALIDATORS pass on all 31 dodge files of the 0.4.23 jar (25 named roll "
                                                "files, Dodge.json, the Dodge root, 4 effects): %s" % json.dumps(vbad)[:800])
    print("E1. validators: %d files pass; NOTE test-bed lines (a name in Assets.zip / the jar not loaded in the bare JVM): %s" % (len(En["dfiles"]), venv[:4]))
    par = []
    for jp_ in (JAR,):
        with zipfile.ZipFile(jp_) as z_:
            for n in z_.namelist():
                if n.endswith(".json"):
                    t_ = z_.read(n).decode("utf-8", "replace")
                    if '"Parallel"' in t_:
                        def walk(x):
                            if isinstance(x, dict):
                                if x.get("Type") == "Parallel" and len(x.get("Interactions") or []) < 2:
                                    par.append(n)
                                for v in x.values():
                                    walk(v)
                            elif isinstance(x, list):
                                for v in x:
                                    walk(v)
                        walk(json.loads(t_))
    check(not par, "E1: no Parallel with fewer than 2 entries in any JSON of the 0.4.23 jar (the check that once stopped the server): %s" % par[:3])
    check(Ep["load"] and Ep["missing_kind"] >= 24 and En["load"] and En["missing"] == [] and En["packets"] >= 1,
          "E2: the dodge files loaded in ONE batch like a pack (packet generator on): 0.4.22 logs the 'Missing interaction "
          "**SkyySkills_Roll_<dir>_Next_Interactions_N' kind (%d - Skyy's log had 24), 0.4.23 logs NONE: %s | 0.4.22 e.g. %s" % (
              Ep["missing_kind"], En["missing"][:3], Ep["missing"][:2]))
    names_n = [x[1] for x in En["ops"] if x[1]]
    want = set(["Dodge"] + ["SkyySkills_Roll_%s%s" % (d_, s_) for d_ in ROLL_DIRS for s_ in ("", "_Push")] +
               ["SkyySkills_Roll_Safe", "SkyySkills_Roll_Look_Forward", "SkyySkills_Roll_Look_Back", "SkyySkills_Roll_Spend",
                "SkyySkills_Roll_Spend_Stamina", "SkyySkills_Roll_Spend_Regen", "Dodge_Left", "Dodge_Right"])
    check(not En["bad"] and not Ep["bad"] and want <= set(names_n) and not [x for x in names_n if x.startswith("*") and "SkyySkills_Roll" in x]
          and En["root_from"] == "jar" and Ep["root_from"] == "Assets.zip",
          "E2: RootInteraction.build() of the Dodge root on the real stores - every op a real interaction (no placeholder in either jar: the "
          "0.4.22 warnings never broke a roll), 0.4.23's graph = only NAMED roll steps (the Serials compile into their steps): %s | %s" % (
              En["bad"][:2] + Ep["bad"][:2], sorted(want - set(names_n))[:5]))
    check(all(En["per"][d_] == Ep["per"][d_] and En["per"][d_][:1] == ["StatsConditionWithModifierInteraction"] and "ApplyForceInteraction" in En["per"][d_]
              for d_ in ROLL_DIRS),
          "E2: per direction the compiled roll has the SAME steps in both jars (check -> i-frames -> look -> push -> Adventure spend): %s" % (
              json.dumps(En["per"])[:600]))
    check(En["cooldown"][0] == 0.0 and En["cooldown"][1] == [False, False, False] and Ep["cooldown"][0] is None and Ep["cooldown"][1] == [False, True, True]
          and abs(En["cooldown"][2] - 0.35) < 1e-6,
          "E3: the real InteractionManager.isOnCooldown, 3 roll starts in a row: 0.4.23's Dodge root (Cooldown 0) is never on cooldown; "
          "0.4.22 (the vanilla root, no Cooldown = the %.2f s default) refuses the 2nd and 3rd - a server-started chain on cooldown fails "
          "silently: %s | 0.4.22 %s" % (En["cooldown"][2], En["cooldown"][:2], Ep["cooldown"][:2]))
    rep_n = En["after_skills"]
    check(En["h_ints"] and En["h_items"] and En["a_items"] and En["s_ints"] and En["after_armory"] == ["Skyy:0.1.13 SkyyArmory"]
          and all(v == ["Skyy:%s SkyySkills" % VERSION, True] for v in rep_n.values()) and len(rep_n) == 10,
          "E4: the engine's re-read REPRODUCED - after SkyyArmory's items load, this jar's Staff_Cast_* overrides make the store re-read the 10 "
          "staffs (8 ladder + 2 Bo, their vanilla inline vars inherit Staff_Cast_*): the pack label becomes SkyySkills while the file stays "
          "SkyyArmory's: %s" % json.dumps(rep_n)[:400])
    check(Ep["arm"][0] == "warn" and "8 of 8 ladder staffs do NOT come from SkyyArmory" in Ep["arm"][1]
          and En["arm"][0] == "info" and "all 8 ladder staffs (Wood to Onyxium) come from Skyy:0.1.13 SkyyArmory" in En["arm"][1]
          and "8 of them re-read from Skyy:0.1.13 SkyyArmory's own files under the name Skyy:%s SkyySkills" % VERSION in En["arm"][1]
          and En["arm_nomod"][0] == "warn",
          "E4: ManaGuard.armCheck() on that store: 0.4.22 = the WARN in Skyy's log; 0.4.23 = INFO naming the re-read (AssetModule."
          "findAssetPackForPath of each item's file); with no AssetModule answering it stays the WARN: %s | 0.4.22 %s" % (En["arm"][1][:300], Ep["arm"][1][:200]))
    vnorm = lambda d_: json.dumps(d_).replace(VERSION, "V").replace(PREV_VERSION, "V")
    check(vnorm(En["armReport"]) == vnorm(Ep["armReport"]) and En["filePack"] == ["Skyy:0.1.13 SkyyArmory", "None", "None"]
          and En["armReport2"]["reread"][0] == "info" and En["armReport2"]["other_file"][0] == "warn",
          "E4: armReport keeps 0.4.22's texts word for word (all / none / mixed / another pack); filePack: our file / unknown id / no map; "
          "armReport2: a SkyyArmory file = info, another pack's file = warn: %s" % json.dumps([En["filePack"], En["armReport2"]])[:500])
    print("E. engine: validators %d files; missing lines 0.4.22 %d -> 0.4.23 %d; cooldown %s -> %s; handover %s" % (
        len(En["dfiles"]), len(Ep["missing"]), len(En["missing"]), Ep["cooldown"][1], En["cooldown"][1], En["arm"][0]))
    print("E4. the 0.4.23 staff handover line: %s" % En["arm"][1])
    # ---------------------------------------------------------------- J
    jz, jp = zipfile.ZipFile(JAR), zipfile.ZipFile(PREV_JAR)
    nn, pn = set(n for n in jz.namelist() if not n.endswith(".class")), set(n for n in jp.namelist() if not n.endswith(".class"))
    added = sorted(nn - pn)
    changed = sorted(n for n in nn & pn if n != "manifest.json" and jz.read(n) != jp.read(n))
    want_add = sorted(["Server/Item/RootInteractions/Dodge.json"] + ["Server/Item/Interactions/Dodge/SkyySkills_Roll_%s%s.json" % (d_, s_)
                                                                    for d_ in ROLL_DIRS for s_ in ("_Steps", "_Push")] +
                      ["Server/Item/Interactions/Dodge/%s.json" % i_ for i_ in ("SkyySkills_Roll_Safe", "SkyySkills_Roll_Look_Forward",
                                                                              "SkyySkills_Roll_Look_Back", "SkyySkills_Roll_Spend", "SkyySkills_Roll_Spend_Steps",
                                                                              "SkyySkills_Roll_Spend_Stamina", "SkyySkills_Roll_Spend_Regen")])
    want_chg = sorted("Server/Item/Interactions/Dodge/SkyySkills_Roll_%s.json" % d_ for d_ in ROLL_DIRS)
    check(added == want_add and changed == want_chg and not (pn - nn),
          "J: the 0.4.23 jar = 0.4.22's files + the 19 new named roll files + the Dodge root; changed = exactly the 6 roll files (now naming "
          "their Steps); every other file byte-identical: added %s changed %s gone %s" % (sorted(set(added) ^ set(want_add))[:4], changed[:7], sorted(pn - nn)[:3]))
    # ---------------------------------------------------------------- H22
    if h22 is not None:
        def fails_of(txt):
            return [ln.strip()[len("FAILED: "):] for ln in txt.splitlines() if ln.strip().startswith("FAILED: ")]
        fn_, fc_ = fails_of(h22["new"]), fails_of(h22["ctl"])
        ctl_keys = set(f_[:60] for f_ in fc_)
        expected = ("J: the 0.4.22 jar = 0.4.21's files minus exactly the 2 vanilla Bo item overrides",
                    "F: 0.4.21 -> 0.4.22 differs only in the planned methods", "H21: the 0.4.21 harness on the 0.4.22 jar")
        other = [f_ for f_ in fn_ if f_[:60] not in ctl_keys and not f_.startswith(expected)]
        mn = (list(re.finditer(r"(?m)^(\d+) checks passed, (\d+) failed", h22["new"])) or [None])[-1]
        mc_ = (list(re.finditer(r"(?m)^(\d+) checks passed, (\d+) failed", h22["ctl"])) or [None])[-1]
        check(mn is not None and mc_ is not None and other == [] and int(mn.group(1)) > 10 and int(mc_.group(2)) == 0
              and int(mn.group(2)) == len([f_ for f_ in fn_ if f_.startswith(expected)]),
              "H22: the 0.4.22 harness on the 0.4.23 jar fails nothing it does not fail on the 0.4.22 jar beyond its version-shape checks (its jar "
              "file list, its class compare, its nested H21 for the same reasons): %s | new %s, control %s" % (
                  other[:3], mn.group(0) if mn else h22["new"][-800:], mc_.group(0) if mc_ else h22["ctl"][-800:]))
        print("H22. 0.4.22 harness: on the 0.4.23 jar %s, on the 0.4.22 jar %s; extra on 0.4.23 = %s" % (
            mn.group(0) if mn else "?", mc_.group(0) if mc_ else "?", [f_[:80] for f_ in fn_ if f_[:60] not in ctl_keys]))
        hm = [ln for ln in h22["new"].splitlines() if ln.startswith(("H21.", "B. flag"))]
        print("H22. evidence (nested start-twice lines): %s" % hm[:3])
    # ---------------------------------------------------------------- F
    cmpd = json.load(open(cmpo))
    AS = "FILcom/hypixel/hytale/component/ArchetypeChunk;Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/component/CommandBuffer;"
    plan = {"Acro": ({"tap([DLcom/hypixel/hytale/protocol/MovementStates;JZD)Z", "tapDone([DJI)V", "tapHard(Lcom/hypixel/hytale/protocol/MovementStates;)Z",
                      "dodgeNew([DJZ)V", "dodge([DLcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/component/CommandBuffer;Lcom/hypixel/hytale/component/Ref;Ljava/util/UUID;JZZ)V"},
                     {"PRESS_BUFFER_MS:J"}),
            "AcroSys": ({"tick(%s)V" % AS}, set()),
            "ManaGuard": ({"armReport([Ljava/lang/String;)[Ljava/lang/String;", "armReport2([Ljava/lang/String;[Ljava/lang/String;)[Ljava/lang/String;",
                           "armCheck()[Ljava/lang/String;", "filePack(Lcom/hypixel/hytale/assetstore/AssetMap;Ljava/lang/String;)Ljava/lang/String;"}, set())}
    bad = {}
    for c, v in cmpd.items():
        if isinstance(v, str):
            bad[c] = v
        elif c in plan:
            if not set(v["methods"]) <= plan[c][0] or not set(v["fields"]) <= plan[c][1]:
                bad[c] = v
        elif (c, v["methods"]) in (("AcroCfg", ["ensureDefaults(Ljava/util/Properties;)V"]), ("SkillCfg", ["load()Ljava/lang/String;"])) and not v["fields"]:
            continue          # they inline the default file text: checked below to differ ONLY in the sprint roll comment line
        elif c in ("SkillKit", "CfgRows") or c.startswith("Cfg"):
            # the config kit: the read-only roll text (customGet) and the 2 row labels / helps - data only
            if v["fields"]:
                bad[c] = v
        else:
            bad[c] = v
    print("F. compare 0.4.22 -> 0.4.23: %s" % json.dumps(cmpd)[:3000])
    LN, LP = json.load(open(wo))["lst"], json.load(open(wop))["lst"]
    OLD_DOC = "# Sprint-tap roll (SkyySkills 0.4.20): a sprint-key press shorter than acro.dodgeTapMs rolls the way you move (standing still = back)."
    NEW_DOC = "# Sprint roll (SkyySkills 0.4.23): pressing sprint rolls the way you move at once; hold it and you come out sprinting (acro.dodgeTapMs: unused)."
    dd = dict((k, LN[k] != LP[k] and LN[k].replace(NEW_DOC, OLD_DOC).replace(VERSION, "V") == LP[k].replace(PREV_VERSION, "V")) for k in LN)
    check(all(dd.values()), "F: AcroCfg.ensureDefaults and SkillCfg.load (they inline the default file text) differ ONLY in the sprint roll comment "
                            "line (0.4.20's tap text -> 0.4.23's press text): %s" % dd)
    check(not bad, "F: 0.4.22 -> 0.4.23 differs only in the planned methods (Acro tap / tapDone + PRESS_BUFFER_MS, AcroSys.tick, ManaGuard "
                   "armReport / armReport2 / armCheck / filePack, the config kit's texts): %s" % json.dumps(bad)[:1500])
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
