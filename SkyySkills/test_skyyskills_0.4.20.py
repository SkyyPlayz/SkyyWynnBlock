"""SkyySkills 0.4.20 - bare-JVM harness for THE SPRINT-TAP ROLL (tools/skills_0_4_20_patch.py; Skyy LOCKED 2026-10-06 roll trigger = "Tap the
sprint key"). The new parts run on the REAL classes of the 0.4.20 jar (and, as the control, the SET pin 0.4.19) with the REAL engine classes
(HytaleServer.jar on the class path, -Xverify:all); the live save data is only ever READ and copied into the scratch folder.

    python SkyySkills/test_skyyskills_0.4.20.py [--jar <SkyySkills-0.4.20.jar>] [--prev <SkyySkills-0.4.19.jar>] [--dir <scratch>]
                                                [--live <Skyy_SkyySkills folder>] [--keep] [--no19]

SECTIONS
  A   every class of both jars loads under -Xverify:all
  T   Acro.tap EXECUTED tick by tick (30 ticks a second, real MovementStates): tap vs hold (133 / 198 ms tap, 231 ms / 600 ms / 3 s hold),
      standing still, every blocked state (mounted, flying, gliding, swimming, in fluid, climbing, sitting, sleeping, mantling, crouching,
      sliding, rolling, in the air - for the whole tap, only at the release, only on a held tick, 99 ms before the press), a roll already
      on, the fixed 400 ms cooldown (whatever acro.dodgeCooldownMs says), no movement states, acro.dodgeTap=false, acro.dodgeTapMs 350 /
      clamps; review fixes: movement keys up with the sprint, out of breath, a refused start spends no cooldown, the watchdog
  DIR the direction: the REAL MovementConditionInteraction.tick0 for every MovementDirection (a real InteractionContext / InteractionEntry /
      InteractionChain, the chosen label read back) -> the 0.4.20 jar's Dodge.json branch -> that roll's Direction / effect / Stamina 2 /
      Failed = Stamina_Bar_Flash (no Stamina: no roll); the vanilla Dodge root in Assets.zip is still {"Interactions": ["Dodge"]}
  R   Acro.startRoll on REAL engine objects: a real InteractionManager (its own constructor), a real RootInteraction "Dodge" in a real asset
      map, the real InteractionModule / EntityModule singletons: canRun, InteractionContext.forInteraction, initChain and queueExecuteChain
      all run for real - one chain of type Dodge on the root "Dodge" waits in the manager's start queue. Codes 1 / 2 / 3 on the same objects
      (code 4 - a running chain whose rules block Dodge - is the engine's own canRun, not staged here); a whole tap -> roll loop as AcroSys runs it
  M   START TWICE on a scratch copy of the live data (the real setup() order): 0.4.20 writes exactly what 0.4.19 writes (no migration of
      its own), start 2 changes nothing; the tap keys read their defaults from the live file (it has none)
  KC  the real config kit on the copy: get acro.dodgeTap / acro.dodgeTapMs, set them (the kit appends the line), the rows (label, place)
  DEF the 0.4.20 default file = the 0.4.19 one + the comment and the 2 keys after acro.dodgeMinMove (version header aside)
  H19 the 0.4.19 harness run against the 0.4.20 jar (control 0.4.18): every 0.4.19 check passes except the 3 that name the jar's
      version-specific shape (classes changed, row count, default file) - the roll gate, jump gate, no cap and AcroMig stay as they were
  F   class compare 0.4.19 -> 0.4.20 METHOD BY METHOD (bytecode text, constant-pool numbers stripped): only the planned methods differ
  AU  the engine-access audit (every bytecode reference looked up with the JVM's own access rules; control refused)
"""
import os, sys, re, json, shutil, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, PREV_VERSION = "0.4.20", "0.4.19"
PKG = "com.skyy.skills."
TPS = 30
STEP = 33   # ms per tick in section T (30 ticks a second, rounded down: 6 ticks = 198 ms)


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "skills0420", "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
PREV_JAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyySkills-%s.jar" % PREV_VERSION)))
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
LIVE_DIR = os.path.abspath(arg("--live", os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyySkills")))
KEEP = "--keep" in sys.argv
FAILS, OKS, GUARD_OK = [], [0], [False]
TAP_DOC = ("# Sprint-tap roll (SkyySkills 0.4.20): a sprint-key press shorter than acro.dodgeTapMs rolls the way you move (standing still"
           " = back).")
BLOCKED = ["mounting", "flying", "gliding", "swimming", "inFluid", "climbing", "sitting", "sleeping", "mantling", "crouching",
           "forcedCrouching", "sliding", "rolling", "air"]


def bkw(st):
    """the MovementStates keywords of a blocked state ("air" = onGround false - review fix: the sprint tap is ground only)"""
    return {"onGround": False} if st == "air" else {st: True}


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
    """the 0.4.15 harness module (stand-in generator, JVM start, class loader, access audit) - imported, never run"""
    return tmod("test_skyyskills_0.4.15.py", "t0415")


def t18():
    """the 0.4.18 harness module (the DodgeCB stand-in) - imported, never run"""
    return tmod("test_skyyskills_0.4.18.py", "t0418")


# ============================================================================================ child: the JVM run (one jar)
def run_child(jar, out, fakes, mode):
    import jpype
    from jpype import JClass, JLong, JInt, JFloat, JDouble, JArray, JBoolean, JImplements, JOverride, JShort
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
    NEW = mode == "new"

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

    MVT = JClass("com.hypixel.hytale.protocol.MovementStates")

    def mstate(**kw):
        m = MVT()
        setany(m, "onGround", JBoolean(True))
        for k, v in kw.items():
            setany(m, k, JBoolean(bool(v)))
        return m

    # ================================================================ T: the tap detector executed
    def sec_T():
        R = {}
        R["load"] = load_cfg(os.path.join(SCRATCH, "t-cfg"))
        R["cfg"] = [bool(AcroCfg.TAP_ON), int(AcroCfg.TAP_MS), int(AcroCfg.DODGE_CD)]

        class P(object):
            def __init__(self):
                self.s = JArray(JDouble)(304)
                self.t = 50_000_000
                self.fired = []
                self.n = 0
                self.code = 0

            def tick(self, roll_on=False, ms_none=False, sta=10.0, **kw):
                self.t += STEP
                self.n += 1
                ms = None if ms_none else mstate(**kw)
                if bool(Acro.tap(self.s, ms, JLong(self.t), JBoolean(roll_on), JDouble(sta))):
                    self.fired.append(self.n)
                    Acro.tapDone(self.s, JLong(self.t), JInt(self.code))   # as AcroSys: the cooldown only for a queued roll

            def ticks(self, k, **kw):
                for _ in range(k):
                    self.tick(**kw)

        def walk_tap(k, before=10, after=20, **extra):
            p = P()
            p.ticks(before, walking=True, **extra)
            p.ticks(k, sprinting=True, **extra)
            p.ticks(after, walking=True, **extra)
            return p

        R["tap4"] = walk_tap(4).fired             # 4 ticks = 132 ms
        R["tap6"] = walk_tap(6).fired             # 198 ms (<= 200)
        R["tap7"] = walk_tap(7).fired             # 231 ms
        R["hold18"] = walk_tap(18).fired          # 594 ms
        R["hold90"] = walk_tap(90).fired          # 3 s sprint
        R["tap1"] = walk_tap(1).fired             # one tick (33 ms)
        p = P()                                   # standing still: idle, sprint key 3 ticks (the server needs no movement)
        p.ticks(10, idle=True, horizontalIdle=True)
        p.ticks(3, sprinting=True, idle=True, horizontalIdle=True)
        p.ticks(10, idle=True, horizontalIdle=True)
        R["still"] = p.fired
        bl = {}
        for st in BLOCKED:
            whole = walk_tap(4, **bkw(st)).fired
            p = P()
            p.ticks(10, walking=True)
            p.ticks(4, sprinting=True)
            p.tick(walking=True, **bkw(st))       # the release tick is blocked (e.g. a crouch-slide out of a short sprint)
            p.ticks(20, walking=True)
            rel = p.fired
            p = P()
            p.ticks(10, walking=True)
            p.ticks(2, sprinting=True)
            p.tick(sprinting=True, **bkw(st))     # a held tick is blocked
            p.ticks(1, sprinting=True)
            p.ticks(20, walking=True)
            held = p.fired
            p = P()
            p.ticks(10, walking=True, **bkw(st))  # blocked, then 10 free ticks (330 ms > the 300 ms settle): a normal tap
            p.ticks(10, walking=True)
            p.ticks(4, sprinting=True)
            p.ticks(20, walking=True)
            pre = p.fired
            p = P()
            p.ticks(10, walking=True, **bkw(st))  # blocked, the press 3 ticks (99 ms) later = sprint resuming: no tap
            p.ticks(2, walking=True)
            p.ticks(4, sprinting=True)
            p.ticks(20, walking=True)
            bl[st] = [whole, rel, held, pre, p.fired]
        R["blocked"] = bl
        p = P()                                   # a roll effect is on at the release
        p.ticks(10, walking=True)
        p.ticks(4, sprinting=True)
        p.tick(walking=True, roll_on=True)
        p.ticks(20, walking=True)
        R["rollon"] = p.fired
        p = P()                                   # cooldown: taps 7 ticks apart (231 ms) -> the second is refused; 13 ticks (429 ms) later -> yes
        p.ticks(10, walking=True)
        p.ticks(3, sprinting=True)                # release at tick 14
        p.ticks(4, walking=True)
        p.ticks(3, sprinting=True)                # release at tick 21 (231 ms after the first roll)
        p.ticks(6, walking=True)
        p.ticks(3, sprinting=True)                # release at tick 30 (528 ms after the first roll)
        p.ticks(10, walking=True)
        R["cooldown"] = p.fired
        p = P()                                   # no movement states for a tick right after a short press: no roll (the press is dropped)
        p.ticks(10, walking=True)
        p.ticks(2, sprinting=True)
        p.tick(ms_none=True)
        p.ticks(10, walking=True)
        R["msnull"] = p.fired
        R["counters"] = [float(walk_tap(4).s[298])]
        # review fixes: the movement keys came up with the sprint (let go of W while holding sprint / toggle sprint + a short W tap)
        p = P()
        p.ticks(10, walking=True)
        p.ticks(4, sprinting=True)
        p.ticks(20, idle=True, horizontalIdle=True)
        R["wrel"] = p.fired
        p = P()                                   # still moving at the release (W held, the sprint key let go) = the normal tap
        p.ticks(10, idle=True, horizontalIdle=True)
        p.ticks(4, sprinting=True)
        p.ticks(20, walking=True)
        R["wkeep"] = p.fired
        # out of breath: Stamina 0.2 at the fall = sprint ran out, no tap; 1.0 = a tap (the chain's own Stamina check flashes the bar)
        p = P()
        p.ticks(10, walking=True)
        p.ticks(4, sprinting=True)
        p.tick(walking=True, sta=0.2)
        p.ticks(20, walking=True)
        R["sta0"] = p.fired
        p = P()
        p.ticks(10, walking=True)
        p.ticks(4, sprinting=True)
        p.tick(walking=True, sta=1.0)
        p.ticks(20, walking=True)
        p2 = P()
        p2.ticks(10, walking=True)
        p2.ticks(4, sprinting=True)
        p2.tick(walking=True, sta=-1.0)           # Stamina unknown: no Stamina rule
        p2.ticks(20, walking=True)
        R["sta1"] = [p.fired, p2.fired]
        # a refused start (code 4: a running chain blocks Dodge) spends no cooldown: the next tap 231 ms later rolls
        p = P()
        p.code = 4
        p.ticks(10, walking=True)
        p.ticks(3, sprinting=True)
        p.ticks(4, walking=True)
        p.code = 0
        p.ticks(3, sprinting=True)
        p.ticks(10, walking=True)
        R["refused"] = [p.fired, float(p.s[298]), float(p.s[299])]
        # the cooldown is the fixed 400 ms even with acro.dodgeCooldownMs 5000 / 100 in the file
        load_cfg(os.path.join(SCRATCH, "t-cfg-cd"), b"acro.dodgeCooldownMs=5000\n")
        p = P()
        p.ticks(10, walking=True)
        p.ticks(3, sprinting=True)
        p.ticks(10, walking=True)
        p.ticks(3, sprinting=True)                # 429 ms after the first
        p.ticks(10, walking=True)
        cd5 = [int(AcroCfg.DODGE_CD), p.fired]
        load_cfg(os.path.join(SCRATCH, "t-cfg-cd2"), b"acro.dodgeCooldownMs=100\n")
        p = P()
        p.ticks(10, walking=True)
        p.ticks(3, sprinting=True)
        p.ticks(4, walking=True)
        p.ticks(3, sprinting=True)                # 231 ms after the first
        p.ticks(10, walking=True)
        R["cdrow"] = [cd5, [int(AcroCfg.DODGE_CD), p.fired], int(Acro.TAP_CD_MS)]
        load_cfg(os.path.join(SCRATCH, "t-cfg"))
        # the watchdog: a queued roll whose effect never shows -> s[303] + one warning; a roll that shows clears it
        s = JArray(JDouble)(304)
        Acro.TAP_NOROLL = False
        Acro.tapDone(s, JLong(1_000_000), JInt(0))
        Acro.tapWatch(s, JLong(1_000_500), JBoolean(False))
        mid = [float(s[302]) > 0, float(s[303])]
        Acro.tapWatch(s, JLong(1_001_100), JBoolean(False))
        lost = [float(s[302]), float(s[303]), bool(Acro.TAP_NOROLL)]
        Acro.tapDone(s, JLong(2_000_000), JInt(0))
        Acro.tapWatch(s, JLong(2_000_100), JBoolean(True))
        Acro.tapWatch(s, JLong(2_002_000), JBoolean(False))
        R["watch"] = [mid, lost, [float(s[302]), float(s[303])]]
        Acro.TAP_NOROLL = False
        # config: off, a longer window, the clamps
        load_cfg(os.path.join(SCRATCH, "t-cfg-off"), b"acro.dodgeTap=false\n")
        R["off_cfg"] = bool(AcroCfg.TAP_ON)
        R["off"] = walk_tap(4).fired
        load_cfg(os.path.join(SCRATCH, "t-cfg-350"), b"acro.dodgeTapMs=350\n")
        R["w350"] = [int(AcroCfg.TAP_MS), walk_tap(9).fired, walk_tap(11).fired]    # 297 ms tap, 363 ms
        load_cfg(os.path.join(SCRATCH, "t-cfg-lo"), b"acro.dodgeTapMs=5\n")
        lo = int(AcroCfg.TAP_MS)
        load_cfg(os.path.join(SCRATCH, "t-cfg-hi"), b"acro.dodgeTapMs=99999\n")
        R["clamp"] = [lo, int(AcroCfg.TAP_MS)]
        load_cfg(os.path.join(SCRATCH, "t-cfg"))
        return R

    # ================================================================ DIR: the real MovementCondition branch for every direction
    def sec_DIR():
        R = {}
        MCI = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.config.client.MovementConditionInteraction")
        ICX = JClass("com.hypixel.hytale.server.core.entity.InteractionContext")
        IEN = JClass("com.hypixel.hytale.server.core.entity.InteractionEntry")
        ICH = JClass("com.hypixel.hytale.server.core.entity.InteractionChain")
        ISD = JClass("com.hypixel.hytale.protocol.InteractionSyncData")
        LBL = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.operation.Label")
        MDIR = JClass("com.hypixel.hytale.protocol.MovementDirection")
        ITY = JClass("com.hypixel.hytale.protocol.InteractionType")
        CDH = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.CooldownHandler")
        idx = {}
        for nm in ("FAILED", "FORWARD", "BACK", "LEFT", "RIGHT", "FORWARD_LEFT", "FORWARD_RIGHT", "BACK_LEFT", "BACK_RIGHT"):
            f = MCI.class_.getDeclaredField(nm + "_LABEL_INDEX")
            f.setAccessible(True)
            idx[int(f.getInt(None))] = nm
        R["labels"] = idx
        tick0 = MCI.class_.getDeclaredMethod("tick0", JBoolean.class_, JFloat.class_, ITY.class_, ICX.class_, CDH.class_)
        tick0.setAccessible(True)
        mci = alloc(MCI)
        got = {}
        for d in MDIR.VALUES:
            ctx = alloc(ICX)
            en = alloc(IEN)
            setany(en, "serverState", ISD())
            cs = ISD()
            setany(cs, "movementDirection", d)
            setany(en, "clientState", cs)
            setany(ctx, "entry", en)
            labs = JArray(LBL)(9)
            for i in range(9):
                lb = alloc(LBL)
                setany(lb, "index", JInt(1000 + i))
                labs[i] = lb
            setany(ctx, "labels", labs)
            ch = alloc(ICH)
            setany(ctx, "chain", ch)
            tick0.invoke(mci, JBoolean(True), JFloat(0.0), ITY.Dodge, ctx, None)
            oc = int(getany(ch, "operationCounter"))
            got[str(d.name())] = [idx.get(oc - 1000), str(getany(en, "serverState").state)]
        R["got"] = got
        return R

    # ================================================================ R: startRoll on real engine objects
    def sec_R():
        R = {}
        ILT = JClass("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap")
        FAS = JClass("skyytest.FakeAssetStore")
        AC = JClass("com.hypixel.hytale.assetstore.codec.AssetCodec")
        RTI = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.config.RootInteraction")
        IMG = JClass("com.hypixel.hytale.server.core.entity.InteractionManager")
        IMM = JClass("com.hypixel.hytale.server.core.modules.interaction.InteractionModule")
        EMc = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
        ITY = JClass("com.hypixel.hytale.protocol.InteractionType")
        CT = JClass("com.hypixel.hytale.component.ComponentType")
        Ref = JClass("com.hypixel.hytale.component.Ref")
        MapStore, DodgeCB = JClass("skyytest.MapStore"), JClass("skyytest.DodgeCB")
        PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
        iputm = ILT.class_.getDeclaredMethod("putAll", JStr.class_, AC.class_, JClass("java.util.Map").class_, JClass("java.util.Map").class_,
                                             JClass("java.util.Map").class_)
        iputm.setAccessible(True)
        codec = jpype.JProxy("com.hypixel.hytale.assetstore.codec.AssetCodec", dict={"getData": lambda a: None})

        @JImplements("java.util.function.IntFunction")
        class NewArr(object):
            @JOverride
            def apply(self, n):
                return Arr.newInstance(RTI.class_, n)

        def root_store(with_dodge):
            m = ILT(NewArr())
            if with_dodge:
                a_, p_ = JClass("java.util.LinkedHashMap")(), JClass("java.util.LinkedHashMap")()
                ro = RTI(JStr("Dodge"), JArray(JStr)(["Dodge"]))
                a_.put("Dodge", ro)
                p_.put("Dodge", path(os.path.join(SCRATCH, "engine", "RootInteractions", "Dodge.json")))
                iputm.invoke(m, "Hytale:Hytale", codec, a_, p_, HM())
            fst = alloc(FAS)
            setany(fst, "assetMap", m)
            try:
                setany(fst, "tClass", RTI.class_)
            except Exception:
                pass
            setstatic(RTI, "ASSET_STORE", fst)
            return m

        def module(on):
            for cls in (IMM, EMc):
                for f in cls.class_.getDeclaredFields():
                    if Mod.isStatic(f.getModifiers()) and f.getType() == cls.class_:
                        f.setAccessible(True)
                        f.set(None, (alloc(cls) if on else None))
            if on:
                imm = IMM.get()
                imt = alloc(CT)
                setany(imm, "interactionManagerComponent", imt)
                return imm, imt
            return None, None

        imm, imt = module(True)
        rmap = root_store(True)
        R["root_found"] = str(RTI.getAssetMap().getAsset("Dodge").getId())
        # a REAL InteractionManager through its own constructor (PlayerRef / simulation handler are only stored)
        handler = jpype.JProxy("com.hypixel.hytale.server.core.modules.interaction.IInteractionSimulationHandler", dict={})
        im = IMG(alloc(PRc), handler)
        ref = alloc(Ref)
        st = alloc(MapStore)
        st.comps = IHM()
        cm = IHM()
        cm.put(imt, im)
        st.comps.put(ref, cm)
        cb = alloc(DodgeCB)
        cb.comps = IHM()
        cb.comps.put(ref, IHM())
        q = getany(im, "chainStartQueue")
        Acro.TAP_FAILED = False
        code = int(Acro.startRoll(st, cb, ref))
        R["code"] = code
        R["failed_flag"] = bool(Acro.TAP_FAILED)
        R["queue"] = int(q.size())
        if q.size() > 0:
            ch = q.get(0)
            R["chain"] = {"type": str(ch.getType()), "root": str(ch.getRootInteraction().getId()),
                          "ctx_im": ch.getContext().getInteractionManager() == im, "ctx_ref": ch.getContext().getEntity() == ref,
                          "running": int(im.getChains().size())}
        # the other codes on the same objects
        q.clear()
        st2 = alloc(MapStore)
        st2.comps = IHM()
        st2.comps.put(ref, IHM())
        R["code_noim"] = int(Acro.startRoll(st2, cb, ref))
        root_store(False)
        R["code_noroot"] = int(Acro.startRoll(st, cb, ref))
        root_store(True)
        module(False)
        R["code_nomod"] = int(Acro.startRoll(st, cb, ref))
        imm, imt = module(True)
        cm2 = IHM()
        cm2.put(imt, im)
        st.comps.put(ref, cm2)
        R["queue_after"] = int(q.size())
        # the whole loop as AcroSys runs it: walk, tap, the queue gets exactly one chain; a hold adds none
        q.clear()
        s = JArray(JDouble)(304)
        t = 60_000_000
        fired = 0
        seq = [dict(walking=True)] * 10 + [dict(sprinting=True)] * 4 + [dict(walking=True)] * 20 + [dict(sprinting=True)] * 30 + [dict(walking=True)] * 10
        for kw in seq:
            t += STEP
            if bool(Acro.tap(s, mstate(**kw), JLong(t), JBoolean(s[6] > 0.5), JDouble(10.0))):
                Acro.tapDone(s, JLong(t), Acro.startRoll(st, cb, ref))
                fired += 1
        R["loop"] = {"fired": fired, "queue": int(q.size()), "last": float(s[299]), "count": float(s[298])}
        R["helpers"] = [bool(Acro.rollFx(st, ref)), float(Acro.stamina(st, ref)), bool(Acro.rollFx(None, ref)), float(Acro.stamina(None, ref))]
        q.clear()
        return R

    if NEW:
        safe("T", sec_T)
        safe("DIR", sec_DIR)
        safe("R", sec_R)

    # ================================================================ M: start twice on the live copy
    def start(d):
        names = ["ManaMig", "HealMig", "DocMig", "ClassManaMig", "SkillLvMig", "KillXpMig", "AcroMig"]
        Cfg.FILE = path(os.path.join(d, "xp.properties"))
        fresh_store(os.path.join(d, "players"))
        Hist.DIR = None
        Rows.HOME = None
        CLog.FILE = None
        CLog.Q.clear()
        r = {}
        for nm in names:
            v = JClass(PKG + nm).run()
            r[nm] = [str(x) for x in v] if nm == "ManaMig" else str(v)
        r["load"] = str(Cfg.load())
        r["curve"] = str(JClass(PKG + "ClassCurve").start(path(d)))
        r["own"] = str(JClass(PKG + "OwnCurve").start(path(d)))
        r["acro"] = [float(AcroCfg.DODGE_MOVE), float(AcroCfg.MAX_PER_MIN), float(AcroCfg.DODGE_XP), int(AcroCfg.DODGE_CD)]
        if NEW:
            r["tap"] = [bool(AcroCfg.TAP_ON), int(AcroCfg.TAP_MS)]
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
        R["log1"] = s1.get("config-changes.log", b"").decode("utf-8")[len(s0.get("config-changes.log", b"").decode("utf-8")):]
        R["players_same"] = all(s0.get(k) == s1.get(k) == s2.get(k) for k in set(s0) | set(s1) | set(s2) if k.startswith("players/"))
        R["def"] = str(Cfg.DEFAULTS)
        return R
    safe("M", sec_M)

    if not NEW:
        json.dump(res, open(out, "w"), indent=1)
        return

    # ================================================================ KC: the real config kit on a copy
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
        Cfg.FILE = path(kf)
        fresh_store(os.path.join(khome, "players"))
        Hist.DIR = None
        Rows.HOME = None
        CLog.FILE = None
        CLog.Q.clear()
        R["mig"] = str(JClass(PKG + "AcroMig").run())
        Cfg.load()
        CfgPub.start(Paths.get(kmods, JStrA([])), None)
        fn = bridge.get("config:fn:SkyySkills")

        def op(*a):
            r = fn.apply(OA(list(a)))
            return None if r is None else [None if x is None else str(x) for x in list(r)[:3]]
        R["get_on"] = str(fn.apply(OA(["get", "acro.dodgeTap"])))
        R["get_ms"] = str(fn.apply(OA(["get", "acro.dodgeTapMs"])))
        R["set_ms"] = op("set", "acro.dodgeTapMs", "300", None, "console", "yes", "console")
        R["set_bad"] = op("set", "acro.dodgeTapMs", "5000", None, "console", "yes", "console")
        R["set_off"] = op("set", "acro.dodgeTap", "false", None, "console", "yes", "console")
        CfgPub.flush()
        txt = open(kf, "rb").read().decode("latin-1").split("\n")
        R["file"] = [ln for ln in txt if ln.startswith("acro.dodgeTap")]
        try:
            Cfg.load()
        except Exception:
            pass
        R["vals"] = [bool(AcroCfg.TAP_ON), int(AcroCfg.TAP_MS)]
        cols = ("KEYS", "LABELS", "CATS", "TYPES", "DEFS", "MINS", "MAXS", "OPTS", "UNITS", "FLAGS", "HELPS")
        arrs = [[str(x) for x in getattr(Rows, c)] for c in cols]
        rows = [list(r) for r in zip(*arrs)]
        R["rows"] = dict((r[0], r) for r in rows if r[0] in ("acro.dodgeTap", "acro.dodgeTapMs"))
        R["order"] = [r[0] for r in rows]
        CfgPub.shutdown()
        return R
    safe("KC", sec_KC)
    json.dump(res, open(out, "w"), indent=1)


# ============================================================================================ child: the method-by-method class compare
def run_compare(jar, prev, out):
    import jpype
    from jpype import JClass
    import skyybuild as B
    jpype.startJVM(B._jvm(), "-XX:-UsePerfData", classpath=[B.JAVASSIST], convertStrings=True)
    IP, PS, BOS = JClass("javassist.bytecode.InstructionPrinter"), JClass("java.io.PrintStream"), JClass("java.io.ByteArrayOutputStream")
    res = {}
    for tag, jp in (("new", jar), ("prev", prev)):
        cp = JClass("javassist.ClassPool")(False)
        cp.appendSystemPath()
        cp.appendClassPath(B.SERVER_JAR)
        cp.appendClassPath(jp)
        names = [n[:-6].replace("/", ".") for n in zipfile.ZipFile(jp).namelist() if n.endswith(".class")]
        d = {}
        for n in names:
            cc = cp.get(n)
            ms = {}
            for m in list(cc.getDeclaredMethods()):
                key = "%s%s" % (m.getName(), m.getSignature())
                if m.getMethodInfo().getCodeAttribute() is None:
                    ms[key] = ""
                    continue
                bos = BOS()
                IP(PS(bos)).print_(m)
                t = str(bos.toString())
                t = re.sub(r"#\d+ = ", "", t)
                # a bigger constant pool turns some ldc into ldc_w (3 bytes, not 2) and shifts the later offsets: compare the
                # instruction SEQUENCE (offsets and branch targets dropped, ldc_w = ldc) - same opcodes, same operands, same order
                t = re.sub(r"(?m)^\s*\d+: ", "", t).replace("ldc_w ", "ldc ")
                t = re.sub(r"(?m)^((?:goto|goto_w|if\w*|jsr) )-?\d+", r"\1L", t)
                t = t.replace(VERSION, "V").replace(PREV_VERSION, "V")   # the version string (AcroMig's WHO is "0.4.19" in both: no change hidden)
                ms[key] = t
            for c in list(cc.getDeclaredConstructors()):
                ms["<init>" + str(c.getSignature())] = str(c.getMethodInfo().getCodeAttribute().getCodeLength()) if c.getMethodInfo().getCodeAttribute() else ""
            flds = sorted("%s:%s" % (f.getName(), f.getSignature()) for f in cc.getDeclaredFields())
            d[n.rsplit(".", 1)[-1]] = {"m": ms, "f": flds}
        res[tag] = d
    N, P = res["new"], res["prev"]
    diff = {}
    for c in sorted(set(N) | set(P)):
        if c not in N or c not in P:
            diff[c] = "only in " + ("new" if c in N else "prev")
            continue
        a, b = P[c]["m"], N[c]["m"]
        ch = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
        fd = sorted(set(N[c]["f"]) ^ set(P[c]["f"]))
        if ch or fd:
            diff[c] = {"methods": ch, "fields": fd}
    json.dump(diff, open(out, "w"), indent=1)


def run_audit(jar, fake, out):
    return t15().run_audit(jar, fake, out)


# ============================================================================================ parent
def main():
    if "--mkfake" in sys.argv:
        return t15().run_mkfake(arg("--mkfake"))
    if "--mkfake2" in sys.argv:
        return t18().run_mkfake2(arg("--mkfake2"))
    if "--child" in sys.argv:
        return run_child(arg("--child"), arg("--out"), arg("--fakes").split(os.pathsep), arg("--mode"))
    if "--audit" in sys.argv:
        return run_audit(arg("--audit"), arg("--fake"), arg("--out"))
    if "--compare" in sys.argv:
        return run_compare(arg("--compare"), arg("--prevjar"), arg("--out"))
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
    for mode, jar in (("prev", PREV_JAR), ("new", JAR)):
        outp = os.path.join(SCRATCH, "run-%s.json" % mode)
        logp = os.path.join(SCRATCH, "run-%s.log" % mode)
        with open(logp, "wb") as lf:
            p = subprocess.run([sys.executable, me, "--child", jar, "--out", outp, "--fakes", os.pathsep.join([fake, fake2]), "--mode", mode,
                                "--dir", SCRATCH], env=env, stdout=lf, stderr=subprocess.STDOUT)
        check(p.returncode == 0 and os.path.isfile(outp), "child JVM (%s) ran (log %s)" % (mode, logp))
        if os.path.isfile(outp):
            outs[mode] = json.load(open(outp))
    cmpo = os.path.join(SCRATCH, "compare.json")
    pc = subprocess.run([sys.executable, me, "--compare", JAR, "--prevjar", PREV_JAR, "--out", cmpo, "--dir", SCRATCH], env=env, capture_output=True)
    check(pc.returncode == 0 and os.path.isfile(cmpo), "class compare child ran: %s" % pc.stderr[-500:])
    auo = os.path.join(SCRATCH, "audit.json")
    pa = subprocess.run([sys.executable, me, "--audit", JAR, "--fake", fake, "--out", auo, "--dir", SCRATCH], env=env, capture_output=True)
    check(pa.returncode == 0 and os.path.isfile(auo), "engine-access audit child ran: %s" % pa.stderr[-500:])
    h19 = None
    if "--no19" not in sys.argv:
        h19d = os.path.join(SCRATCH, "h19")
        prev18 = os.path.join(HERE, "SkyySkills-0.4.18.jar")
        h19 = {}
        for tag, jj in (("new", JAR), ("ctl", PREV_JAR)):   # ctl = the same 0.4.19 harness on its own jar today (the live data moved on)
            ph = subprocess.run([sys.executable, os.path.join(HERE, "test_skyyskills_0.4.19.py"), "--jar", jj, "--prev", prev18, "--dir",
                                 h19d + "-" + tag, "--live", LIVE_DIR], env=env, capture_output=True)
            h19[tag] = ph.stdout.decode("utf-8", "replace")
    if FAILS:
        return finish()
    for mode in ("new", "prev"):
        r = outs[mode]
        check(not r["load_fails"] and r["loaded"] == r["classes"], "A (%s): %d / %d classes load under -Xverify:all %s" % (mode, r["loaded"], r["classes"], r["load_fails"][:3]))
    N, P = outs["new"]["data"], outs["prev"]["data"]
    for k in ("T", "DIR", "R", "M", "KC"):
        check(k in N and "error" not in N[k], "section %s ran: %s" % (k, (N.get(k) or {}).get("error")))
    check("M" in P and "error" not in P["M"], "control (0.4.19) section M ran: %s" % (P.get("M") or {}).get("error"))
    if FAILS:
        return finish()
    print("A. both jars: every class loads under -Xverify:all (%d / %d classes)" % (outs["new"]["loaded"], outs["prev"]["loaded"]))

    # ---------------------------------------------------------------- T
    Tt = N["T"]
    check(Tt["cfg"] == [True, 200, 400], "T: fresh defaults: tap on, window 200 ms, cooldown 400 ms: %s" % Tt["cfg"])
    check(Tt["tap4"] == [15] and Tt["tap6"] == [17] and Tt["tap1"] == [12], "T: taps of 33 / 132 / 198 ms roll once, on the release tick: %s %s %s" % (Tt["tap1"], Tt["tap4"], Tt["tap6"]))
    check(Tt["tap7"] == [] and Tt["hold18"] == [] and Tt["hold90"] == [], "T: a 231 ms / 594 ms / 3 s press only sprints: %s %s %s" % (Tt["tap7"], Tt["hold18"], Tt["hold90"]))
    check(Tt["still"] == [14], "T: standing still, a sprint tap rolls (the chain's no-direction branch = back roll): %s" % Tt["still"])
    for st, (whole, rel, held, pre, soon) in Tt["blocked"].items():
        check(whole == [] and rel == [] and held == [] and pre == [25] and soon == [],
              "T: %s blocks the tap (whole press, release tick, a held tick, a press 99 ms after it); 330 ms after it a tap rolls: %s" % (st, [whole, rel, held, pre, soon]))
    check(Tt["wrel"] == [] and Tt["wkeep"] == [15], "T: moving, sprint + movement keys up together = no tap (W let go / toggle sprint); W still held = tap: %s %s" % (Tt["wrel"], Tt["wkeep"]))
    check(Tt["sta0"] == [] and Tt["sta1"] == [[15], [15]], "T: Stamina 0.2 at the fall = ran out of breath, no tap; 1.0 / unknown = tap: %s %s" % (Tt["sta0"], Tt["sta1"]))
    check(Tt["refused"] == [[14, 21], 1.0, 0.0], "T: a refused start (code 4) spends no cooldown / count; the next tap 231 ms later rolls: %s" % Tt["refused"])
    check(Tt["cdrow"] == [[5000, [14, 27]], [100, [14]], 400], "T: the tap cooldown is a fixed 400 ms whatever acro.dodgeCooldownMs says (5000 / 100): %s" % Tt["cdrow"])
    check(Tt["watch"] == [[True, 0.0], [0.0, 1.0, True], [0.0, 1.0]], "T: watchdog - no roll effect 1 s after a queued roll = s[303] + 1 and one warning; a roll that shows clears it: %s" % Tt["watch"])
    check(Tt["rollon"] == [], "T: no tap roll while a roll effect is on: %s" % Tt["rollon"])
    check(Tt["cooldown"] == [14, 30], "T: a second tap 231 ms after a tap roll is refused (cooldown 400 ms), the third 528 ms after rolls: %s" % Tt["cooldown"])
    check(Tt["msnull"] == [], "T: a tick without movement states drops the press: %s" % Tt["msnull"])
    check(Tt["counters"] == [1.0], "T: s[298] counts the tap rolls: %s" % Tt["counters"])
    check(Tt["off_cfg"] is False and Tt["off"] == [], "T: acro.dodgeTap=false - no tap rolls: %s" % Tt["off"])
    check(Tt["w350"] == [350, [20], []], "T: acro.dodgeTapMs=350 - a 297 ms tap rolls, 363 ms does not: %s" % Tt["w350"])
    check(Tt["clamp"] == [50, 1000], "T: acro.dodgeTapMs clamps to 50-1000: %s" % Tt["clamp"])
    print("T. tap detector: 33 / 132 / 198 ms roll, 231 ms+ sprint; standing still rolls; %d blocked states (air too) x 4 refused + 300 ms settle; "
          "W-up / out of breath refused; refused start free; fixed 400 ms cooldown; watchdog; roll on / off / 350 ms / clamps" % len(Tt["blocked"]))

    # ---------------------------------------------------------------- DIR (+ the jar's chain files)
    jz = zipfile.ZipFile(JAR)
    dj = json.loads(jz.read("Server/Item/Interactions/Dodge.json"))
    mc = dj["Next"]
    check(dj["Type"] == "Condition" and dj["Flying"] is False and mc["Type"] == "MovementCondition", "DIR: Dodge.json = Condition Flying false -> MovementCondition")
    key_of = {"FAILED": "Failed", "FORWARD": "Forward", "BACK": "Back", "LEFT": "Left", "RIGHT": "Right", "FORWARD_LEFT": "ForwardLeft",
              "FORWARD_RIGHT": "ForwardRight", "BACK_LEFT": "BackLeft", "BACK_RIGHT": "BackRight"}
    import skyybuild as B
    az = zipfile.ZipFile(os.path.join(os.path.dirname(os.path.dirname(B.SERVER_JAR)), "Assets.zip"))   # read-only

    def body(iid):
        p_ = "Server/Item/Interactions/Dodge/%s.json" % iid
        if p_ in jz.namelist():
            return json.loads(jz.read(p_))
        return json.loads(az.read(p_).decode("utf-8-sig"))
    want = {"None": ("Failed", (0, 1), "Dodge_Back"), "Forward": ("Forward", (0, -1), "Dodge_Forward"), "Back": ("Back", (0, 1), "Dodge_Back"),
            "Left": ("Left", (-1, 0), "Dodge_Left"), "Right": ("Right", (1, 0), "Dodge_Right"),
            "ForwardLeft": ("ForwardLeft", (-0.7071, -0.7071), "Dodge_Forward"), "ForwardRight": ("ForwardRight", (0.7071, -0.7071), "Dodge_Forward"),
            "BackLeft": ("BackLeft", (-0.7071, 0.7071), "Dodge_Back"), "BackRight": ("BackRight", (0.7071, 0.7071), "Dodge_Back")}
    G = N["DIR"]["got"]
    rows_ = []
    for dname, (branch, vec, fx) in want.items():
        lab, state = G.get(dname, [None, None])
        iid = mc.get(key_of.get(lab, "?"))
        b = body(iid) if iid else {}
        seq = (b.get("Next") or {}).get("Interactions") or [{}, {}, {}]
        dv = seq[2].get("Direction", {}) if len(seq) > 2 else {}
        ok = (lab is not None and key_of[lab] == branch and b.get("Costs") == {"Stamina": 2} and b.get("Failed") == "Stamina_Bar_Flash"
              and seq[0] == {"Type": "ApplyEffect", "EffectId": "Dodge_Invulnerability"} and seq[1].get("EffectId") == fx
              and abs(dv.get("X", 0) - vec[0]) < 1e-3 and abs(dv.get("Z", 0) - vec[1]) < 1e-3 and seq[2].get("Force") == 13
              and state == "Finished")
        check(ok, "DIR: MovementDirection.%s -> the real tick0 picks %s -> %s (Direction %s, %s, Stamina 2, no Stamina = Stamina_Bar_Flash): %s %s %s" % (
            dname, branch, iid, vec, fx, lab, dv, b.get("Costs")))
        rows_.append("%s->%s" % (dname, iid))
    vroot = json.loads(az.read("Server/Item/RootInteractions/Dodge.json").decode("utf-8-sig"))
    check(vroot == {"Interactions": ["Dodge"], "RequireNewClick": True} and "Server/Item/RootInteractions/Dodge.json" not in jz.namelist(),
          "DIR: the vanilla Dodge root (started by startRoll) runs Dodge.json; the jar does not override the root: %s" % vroot)
    print("DIR. real MovementCondition: %s" % ", ".join(rows_))

    # ---------------------------------------------------------------- R
    Rr = N["R"]
    ch = Rr.get("chain") or {}
    check(Rr["root_found"] == "Dodge" and Rr["code"] == 0 and not Rr["failed_flag"] and Rr["queue"] == 1,
          "R: startRoll on a REAL InteractionManager: canRun + forInteraction + initChain + queueExecuteChain ran, code 0, one chain queued: %s" % {k: Rr[k] for k in ("code", "queue", "failed_flag")})
    check(ch.get("type") == "Dodge" and ch.get("root") == "Dodge" and ch.get("ctx_im") and ch.get("ctx_ref") and ch.get("running") == 0,
          "R: the queued chain = type Dodge, root Dodge, context of this player's manager / entity, not yet running (the manager's tick starts it): %s" % ch)
    check(Rr["code_noim"] == 2 and Rr["code_noroot"] == 3 and Rr["code_nomod"] == 1 and Rr["queue_after"] == 0,
          "R: no manager = 2, no Dodge root = 3, no InteractionModule = 1, nothing queued: %s %s %s" % (Rr["code_noim"], Rr["code_noroot"], Rr["code_nomod"]))
    lp = Rr["loop"]
    check(lp == {"fired": 1, "queue": 1, "last": 0.0, "count": 1.0}, "R: walk, tap, walk, hold 1 s: exactly one roll chain queued: %s" % lp)
    check(Rr["helpers"] == [False, -1.0, False, -1.0], "R: rollFx / stamina on a store without the components (and null) = false / -1, no throw: %s" % Rr["helpers"])
    print("R. real engine path: code 0, 1 Dodge chain queued (root Dodge); codes 1 / 2 / 3; tap + hold loop = 1 chain")

    # ---------------------------------------------------------------- M
    M, MP = N["M"], P["M"]
    check(M["xp1"] == MP["xp1"] and M["log1"].replace(VERSION, "V") == MP["log1"].replace(PREV_VERSION, "V"),
          "M: start 1 on the live copy writes exactly what 0.4.19 writes (no migration of its own): %s" % [d for d in zip(M["xp1"].split("\n"), MP["xp1"].split("\n")) if d[0] != d[1]][:3])
    check(M["changed2"] == [] and M["players_same"] and M["r1"]["tap"] == [True, 200] and "acro.dodgeTap" not in M["xp1"],
          "M: start 2 changes nothing; players untouched; the tap keys read their defaults (the live file has none): %s %s" % (M["changed2"], M["r1"]["tap"]))
    check(M["r1"]["acro"] == MP["r1"]["acro"], "M: dodge gate / cap / XP / cooldown read the same as 0.4.19: %s %s" % (M["r1"]["acro"], MP["r1"]["acro"]))
    print("M. live copy: start 1 = 0.4.19's result (%s), start 2 = nothing; tap keys default true / 200" % ", ".join(k for k in M["changed1"] if not k.startswith("config-history/")))

    # ---------------------------------------------------------------- DEF
    dn, dp = M["def"], MP["def"]
    exp = dp.replace("# SkyySkills %s - XP rules." % PREV_VERSION, "# SkyySkills %s - XP rules." % VERSION, 1).replace(
        "\nacro.dodgeMinMove=2.0\n", "\nacro.dodgeMinMove=2.0\n" + TAP_DOC + "\nacro.dodgeTap=true\nacro.dodgeTapMs=200\n", 1)
    check(dn == exp, "DEF: the 0.4.20 default file = 0.4.19's + the tap comment and 2 keys after acro.dodgeMinMove: %s" % [d for d in zip(dn.split("\n"), exp.split("\n")) if d[0] != d[1]][:3])
    print("DEF. default file = 0.4.19 + 3 lines")

    # ---------------------------------------------------------------- KC
    KC = N["KC"]
    check(KC["get_on"] == "true" and KC["get_ms"] == "200", "KC: get acro.dodgeTap %s, acro.dodgeTapMs %s (absent from the file = defaults)" % (KC["get_on"], KC["get_ms"]))
    check(KC["set_ms"][0] == "ok" and KC["set_bad"][0] != "ok" and KC["set_off"][0] == "ok" and sorted(KC["file"]) == ["acro.dodgeTap=false", "acro.dodgeTapMs=300"]
          and KC["vals"] == [False, 300], "KC: set 300 ok, 5000 refused, off ok; the kit appended both lines; live values: %s %s %s %s %s" % (KC["set_ms"], KC["set_bad"], KC["set_off"], KC["file"], KC["vals"]))
    r1, r2 = KC["rows"]["acro.dodgeTap"], KC["rows"]["acro.dodgeTapMs"]
    check(r1[1:10] == ["Roll on sprint tap", "acrobatics", "bool", "true", "", "", "", "", "live"] and len(r1[10]) <= 100
          and r2[1:10] == ["Sprint tap window", "acrobatics", "int", "200", "50", "1000", "", "ms", "live,adv"] and len(r2[10]) <= 100,
          "KC: the two rows: %s / %s" % (r1, r2))
    o_ = KC["order"]
    check(o_[o_.index("acro.roll") + 1:o_.index("acro.roll") + 3] == ["acro.dodgeTap", "acro.dodgeTapMs"] and len(o_) == 205,
          "KC: the rows sit right after the read-only Dodge roll row; 205 rows (%d)" % len(o_))
    print("KC. real kit: get true / 200, set 300 / off, 5000 refused; rows after acro.roll")

    # ---------------------------------------------------------------- H19
    if h19 is not None:
        def fails_of(txt):
            return [ln.strip()[len("FAILED: "):] for ln in txt.splitlines() if ln.strip().startswith("FAILED: ")]
        fn_, fc_ = fails_of(h19["new"]), fails_of(h19["ctl"])
        expected = ("F: classes changed beyond the version string", "KC: acro.dodgeMinMove sits after the dodge cooldown row; 203 rows",
                    "M: the 0.4.18 default file migrates to exactly the 0.4.19 default file")
        ctl_keys = set(f[:60] for f in fc_)
        other = [f for f in fn_ if f[:60] not in ctl_keys and not f.startswith(expected)]
        mn = re.search(r"(\d+) checks passed, (\d+) failed", h19["new"])
        mc_ = re.search(r"(\d+) checks passed, (\d+) failed", h19["ctl"])
        check(mn is not None and mc_ is not None and other == [] and int(mn.group(1)) > 40,
              "H19: the 0.4.19 harness on the 0.4.20 jar fails nothing that it does not also fail on the 0.4.19 jar today, beyond the 3 "
              "version-shape checks: %s | new %s, control %s" % (other[:3], mn.group(0) if mn else h19["new"][-600:], mc_.group(0) if mc_ else h19["ctl"][-600:]))
        exp_f = [f for f in fn_ if f.startswith(expected[0])]
        check(all("AcroSys" in f for f in exp_f), "H19: its class check differs only by AcroSys (the tap hook): %s" % exp_f)
        gone = [f for f in fc_ if f[:60] not in set(x[:60] for x in fn_)]
        print("H19. 0.4.19 harness: on the 0.4.20 jar %s, on the 0.4.19 jar %s (control: %d checks need the pre-0.4.19 live file - already "
              "migrated by the 0.4.19 deploy); extra on 0.4.20 = the %d version-shape checks only%s" % (
                  mn.group(0), mc_.group(0), len(fc_), len([f for f in fn_ if f.startswith(expected)]), (" (gone: %s)" % gone[:2]) if gone else ""))

    # ---------------------------------------------------------------- F
    cmpd = json.load(open(cmpo))
    plan = {"Acro": {"methods": ["startRoll(Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/component/CommandBuffer;Lcom/hypixel/hytale/component/Ref;)I",
                                 "state(Ljava/util/UUID;)[D", "tap([DLcom/hypixel/hytale/protocol/MovementStates;JZD)Z",
                                 "tapBlocked(Lcom/hypixel/hytale/protocol/MovementStates;)Z", "tapDone([DJI)V", "tapWatch([DJZ)V",
                                 "rollFx(Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/component/Ref;)Z",
                                 "stamina(Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/component/Ref;)D"],
                     "fields": ["TAP_FAILED:Z", "TAP_NOROLL:Z", "TAP_CD_MS:J", "TAP_SETTLE_MS:J"]},
            "AcroCfg": {"methods": ["ensureDefaults(Ljava/util/Properties;)V", "read(Ljava/util/Properties;)V"], "fields": ["TAP_MS:J", "TAP_ON:Z"]},
            "AcroSys": {"methods": ["tick(FILcom/hypixel/hytale/component/ArchetypeChunk;Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/component/CommandBuffer;)V"], "fields": []}}
    allowed_extra = {"SkillCfg", "CfgRows", "SkyySkillsPlugin", "CfgFile", "SkillKit"}   # default text (SkillCfg.load) / rows / setup text
    bad = {}
    for c, v in cmpd.items():
        if c in plan:
            if sorted(v["methods"]) != sorted(plan[c]["methods"]) or sorted(v["fields"]) != sorted(plan[c]["fields"]):
                bad[c] = v
        elif c not in allowed_extra:
            bad[c] = v
    check(not bad and all(c in cmpd for c in plan), "F: 0.4.19 -> 0.4.20 differs only in the planned methods / fields: %s" % json.dumps(bad)[:1500])
    ex = dict((c, cmpd[c]) for c in allowed_extra if c in cmpd)
    jp = zipfile.ZipFile(PREV_JAR)
    other_files = sorted(n for n in set(jz.namelist()) | set(jp.namelist()) if not n.endswith(".class") and n != "manifest.json"
                         and (n not in jz.namelist() or n not in jp.namelist() or jz.read(n) != jp.read(n)))
    check(other_files == [], "F: every asset file (the 11 dodge files, the spell overrides) byte-identical: %s" % other_files[:3])
    print("F. 0.4.19 -> 0.4.20: Acro +tap/tapBlocked/tapDone/tapWatch/rollFx/stamina/startRoll (+state 304), AcroCfg +TAP_ON/TAP_MS (read, ensureDefaults text), AcroSys.tick; other changed: %s; assets identical"
          % {c: v["methods"] for c, v in ex.items()})
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
