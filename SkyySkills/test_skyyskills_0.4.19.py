"""SkyySkills 0.4.19 - bare-JVM harness for THE ROLL MOVE GATE + NO MOVE XP CAP (tools/skills_0_4_19_patch.py; Skyy LOCKED 2026-10-06 "add the
move gate like jumps but remove the xp cap on both"). The new parts run on the REAL classes of the 0.4.19 jar (and, as the control, the SET pin
0.4.18) with the REAL engine classes (HytaleServer.jar on the class path, -Xverify:all); the live save data is only ever READ and copied into
the scratch folder. Everything 0.4.18 already checked is guarded by the class compare (section F) - run SkyySkills/test_skyyskills_0.4.18.py
for the older parts.

    python SkyySkills/test_skyyskills_0.4.19.py [--jar <SkyySkills-0.4.19.jar>] [--prev <SkyySkills-0.4.18.jar>] [--dir <scratch>]
                                                [--live <Skyy_SkyySkills folder>] [--keep]

SECTIONS
  A   every class of both jars loads under -Xverify:all
  G   Acro.move + Acro.dodge EXECUTED tick by tick (30 ticks a second, real MovementStates / org.joml.Vector3d / EffectControllerComponent /
      EntityEffect asset map): the roll slide modelled with the vanilla VelocityConfig (13 b/s, x0.94 a tick above 5 b/s, x0.82 below,
      starting one tick BEFORE the server sees the effect). Rolling in place after a 3-block walk: only the first roll pays; rolling while
      sprinting: every roll pays; a roll inside the 400 ms cooldown is not counted; the push comes on every counted roll (paid or not);
      acro.dodgeMinMove 0 = every roll pays; Creative pays nothing. Control 0.4.18: every in-place roll pays (no gate).
  JG  jumps: the jump gate is unchanged (in place nothing, after 2 blocks +2, 800 ms cooldown) - identical on both jars
      + review fix: roll in place then jump x5 = 0 jump XP (the roll slide feeds no gate; 0.4.18 paid); sprint-roll-sprint-jump still +2
  NC  no cap: Acro.take pays 600 in one second and 10 a second for 60 s (600 in a minute); 0.4.18 stops at 240. A 60 s run of sprinting +
      jumping + rolling through move / dodge / take pays every whole XP it earned (> 240)
  M   START TWICE on a scratch copy of the live data (the real setup() order: every migration, then SkillCfg.load, ClassCurve, OwnCurve):
      start 1 = exactly the planned lines (dodge comment, marker + acro.dodgeMinMove=2.0 under the cooldown, cap comment, 240 -> 0), LF kept,
      config-history holds the old bytes, 2 change-log lines (Undo values 240 / 0); start 2 changes nothing. Variants (plan + run on
      copies): hand-set 500 kept, hand-set 0 kept + WARN, CRLF kept, gate already there kept, no cooldown line -> appended, no acro.* key ->
      nothing, the 0.4.18 default file -> exactly the 0.4.19 default file
  KC  through the REAL config kit on the migrated copy: get acro.dodgeMinMove 2.0 / acro.maxXpPerMinute 0; the Undo of each change-log line
      (set via undo) writes 240 / 0; the rows (label, default, place, 203 rows)
  F   class compare 0.4.18 -> 0.4.19 (version string normalised): only the planned classes differ, AcroMig new; no asset file changed
  AU  the engine-access audit (every bytecode reference looked up with the JVM's own access rules; control refused)
"""
import os, sys, re, json, math, shutil, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, PREV_VERSION = "0.4.19", "0.4.18"
PKG = "com.skyy.skills."
TPS = 30


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "skills0419", "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
PREV_JAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyySkills-%s.jar" % PREV_VERSION)))
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
LIVE_DIR = os.path.abspath(arg("--live", os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyySkills")))
KEEP = "--keep" in sys.argv
FAILS, OKS, GUARD_OK = [], [0], [False]

DODGE_DOC_OLD = "# Dodge (the vanilla strafe left/right dodge): XP per dodge, at most one per acro.dodgeCooldownMs."
DODGE_DOC_NEW = "# Dodge rolls (the dodge key, 8 directions): XP per roll, at most one counted roll per acro.dodgeCooldownMs."
MARK = "# A roll pays only after acro.dodgeMinMove blocks of your own movement since the last paid roll (SkyySkills 0.4.19 roll move gate)."
CAP_OLD_DOC = "# Running, jumping and dodging XP together pays at most this much in ANY 60 seconds (sliding window; movement is easy to macro)."
CAP_NEW_DOC = "# Running, jumping and dodging XP together pays at most this much in ANY 60 seconds (0 = no cap, the default since SkyySkills 0.4.19)."


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


def expected_migration(text):
    """the planned start-1 result of an LF file still on every 0.4.18 default (Python model of AcroMig.plan for that case)"""
    out = []
    for ln in text.split("\n"):
        if ln == DODGE_DOC_OLD:
            out.append(DODGE_DOC_NEW)
        elif ln == CAP_OLD_DOC:
            out.append(CAP_NEW_DOC)
        elif ln == "acro.maxXpPerMinute=240":
            out.append("acro.maxXpPerMinute=0")
        else:
            out.append(ln)
        if ln == "acro.dodgeCooldownMs=400":
            out.append(MARK)
            out.append("acro.dodgeMinMove=2.0")
    return "\n".join(out)


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

    # ---------------------------------------------------------------- the effect registry (real classes, filled here - as 0.4.18's harness)
    ILT = JClass("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap")
    FAS = JClass("skyytest.FakeAssetStore")
    AC = JClass("com.hypixel.hytale.assetstore.codec.AssetCodec")
    iputm = ILT.class_.getDeclaredMethod("putAll", JStr.class_, AC.class_, JClass("java.util.Map").class_, JClass("java.util.Map").class_,
                                         JClass("java.util.Map").class_)
    iputm.setAccessible(True)
    codec = jpype.JProxy("com.hypixel.hytale.assetstore.codec.AssetCodec", dict={"getData": lambda a: None})
    EFX = JClass("com.hypixel.hytale.server.core.asset.type.entityeffect.config.EntityEffect")
    work = os.path.join(SCRATCH, "engine-" + mode)
    os.makedirs(work, exist_ok=True)

    @JImplements("java.util.function.IntFunction")
    class NewArr(object):
        @JOverride
        def apply(self, n):
            return Arr.newInstance(EFX.class_, n)
    fmap = ILT(NewArr())
    EFFECT_IDS = ["Dodge_Left", "Dodge_Right", "Dodge_Forward", "Dodge_Back", "Dodge_Invulnerability"]
    a_, p_ = JClass("java.util.LinkedHashMap")(), JClass("java.util.LinkedHashMap")()
    for k in EFFECT_IDS:
        o = alloc(EFX)
        try:
            setany(o, "id", k)
        except Exception:
            pass
        a_.put(k, o)
        p_.put(k, path(os.path.join(work, "effects", k + ".json")))
    iputm.invoke(fmap, "Hytale:Hytale", codec, a_, p_, HM())
    fst = alloc(FAS)
    setany(fst, "assetMap", fmap)
    try:
        setany(fst, "tClass", EFX.class_)
    except Exception:
        pass
    setstatic(EFX, "STORE", fst)
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
    ECC = JClass("com.hypixel.hytale.server.core.entity.effect.EffectControllerComponent")
    AEE = JClass("com.hypixel.hytale.server.core.entity.effect.ActiveEntityEffect")
    VEL = JClass("com.hypixel.hytale.server.core.modules.physics.component.Velocity")
    Ref = JClass("com.hypixel.hytale.component.Ref")
    MapStore, DodgeCB = JClass("skyytest.MapStore"), JClass("skyytest.DodgeCB")
    MVT = JClass("com.hypixel.hytale.protocol.MovementStates")
    V3 = JClass("org.joml.Vector3d")
    SLOTS = 296

    class Sim(object):
        """one player ticked at 30 TPS through the REAL Acro.move + Acro.dodge (the AcroSys order: move, then dodge)"""

        def __init__(self, u, creative=False):
            self.u = u
            self.creative = creative
            self.ref = alloc(Ref)
            self.ecc = ECC()
            self.st = alloc(MapStore)
            self.st.comps = IHM()
            m = IHM()
            m.put(eccT, self.ecc)
            self.st.comps.put(self.ref, m)
            self.vel = VEL()
            self.vel.setClient(JDouble(5.0), JDouble(0.0), JDouble(0.0))
            self.cb = alloc(DodgeCB)
            self.cb.comps = IHM()
            m2 = IHM()
            m2.put(velT, self.vel)
            self.cb.comps.put(self.ref, m2)
            self.s = JArray(JDouble)(SLOTS)
            self.t = 10_000_000
            self.x = 0.0
            self.run = 0.0           # own speed, blocks a second (sprint 5.6)
            self.slide = 0.0         # roll slide speed (vanilla VelocityConfig)
            self.fx_left = 0         # ticks the roll effect stays on
            self.fx_lead = -1        # ticks until the server sees the effect (the slide starts first)
            self.jump = False
            self.idx = int(fmap.getIndex("Dodge_Back"))
            self.slide_total = 0.0
            d_ = JArray(JLong)(32)
            d_[4] = JLong(10 ** 15)            # max Acrobatics level: the level push (Acro.boost) is on
            Store.DATA.put(str(u), d_)

        def ms(self):
            m = MVT()
            setany(m, "onGround", JBoolean(True))
            setany(m, "jumping", JBoolean(self.jump))
            moving = self.run > 0.0 or self.slide > 0.0
            setany(m, "idle", JBoolean(not moving))
            setany(m, "horizontalIdle", JBoolean(not moving))
            setany(m, "sprinting", JBoolean(self.run > 4.0))
            setany(m, "walking", JBoolean(0.0 < self.run <= 4.0))
            return m

        def roll(self):
            self.slide = 13.0
            self.fx_lead = 1

        def tick(self):
            dt = 1.0 / TPS
            d = (self.run + self.slide) * dt
            self.slide_total += self.slide * dt
            self.x += d
            if self.slide > 0.0:
                self.slide *= 0.94 if self.slide > 5.0 else 0.82
                if self.slide < 0.05:
                    self.slide = 0.0
            if self.fx_lead >= 0:
                if self.fx_lead == 0:
                    self.fx_left = int(0.25 * TPS)
                self.fx_lead -= 1
            on = self.fx_left > 0
            ae = self.ecc.getActiveEffects()
            if on and not ae.containsKey(JInt(self.idx)):
                ae.put(JInt(self.idx), alloc(AEE))
            if not on:
                ae.remove(JInt(self.idx))
            if self.fx_left > 0:
                self.fx_left -= 1
            self.t += int(round(1000.0 / TPS))
            Acro.move(self.s, self.ms(), V3(JDouble(self.x), JDouble(64.0), JDouble(0.0)), JFloat(dt), JLong(self.t), JBoolean(self.creative))
            Acro.dodge(self.s, self.st, self.cb, self.ref, self.u, JLong(self.t), JBoolean(self.creative), JBoolean(False))

        def ticks(self, n):
            for _ in range(n):
                self.tick()

        def xp(self):
            return float(self.s[11])

        def pushes(self):
            return len(self.vel.getInstructions())

    # ================================================================ G: the roll move gate executed
    def sec_G():
        R = {}
        R["load"] = load_cfg(os.path.join(SCRATCH, "g-cfg-" + mode))
        R["cfg"] = [float(AcroCfg.DODGE_XP), int(AcroCfg.DODGE_CD), float(AcroCfg.MAX_PER_MIN), float(AcroCfg.JUMP_MOVE), int(AcroCfg.JUMP_CD),
                    float(AcroCfg.RUN), float(AcroCfg.SPRINT)]
        R["gate"] = float(AcroCfg.DODGE_MOVE) if NEW else None
        R["settle"] = int(Acro.ROLL_SETTLE_MS) if NEW else None
        fresh_store(os.path.join(SCRATCH, "g-players-" + mode))
        setstatic(AcroCfg, "RUN", JDouble(0.0))      # movement XP off: only roll / jump XP lands in s[11] below
        setstatic(AcroCfg, "SPRINT", JDouble(0.0))
        setstatic(AcroCfg, "WALK", JDouble(0.0))
        # (1) walk 3 blocks, stop, then 6 rolls in place 1.5 s apart (each slides ~4-5 blocks)
        sm = Sim(UUID(0x19, 1))
        sm.run = 3.0
        sm.ticks(TPS)                    # 1 s at 3 b/s = 3 blocks
        sm.run = 0.0
        sm.ticks(5)
        per = []
        for i in range(6):
            x0 = sm.x
            before = sm.xp()
            sm.roll()
            sm.ticks(int(1.5 * TPS))
            per.append([round(sm.xp() - before, 3), round(sm.x - x0, 3), round(float(sm.s[291]) if NEW else 0.0, 4)])
        R["inplace"] = {"per": per, "xp": sm.xp(), "pushes": sm.pushes()}
        # (2) sprinting 5.6 b/s, a roll every 1.6 s (window ~1 s, then ~0.6 s of own running = 3.4 blocks)
        sp = Sim(UUID(0x19, 2))
        sp.run = 5.6
        sp.ticks(TPS)
        per2 = []
        for i in range(6):
            before = sp.xp()
            sp.roll()
            sp.ticks(int(1.6 * TPS))
            per2.append(round(sp.xp() - before, 3))
        R["moving"] = {"per": per2, "xp": sp.xp(), "pushes": sp.pushes()}
        # (3) cooldown: two roll effects 200 ms apart while sprinting -> the second is not counted (no XP, no push)
        sc = Sim(UUID(0x19, 3))
        sc.run = 5.6
        sc.ticks(TPS)
        sc.roll()
        sc.ticks(6)                      # 200 ms: the first effect is still on - let it end, then the second starts inside 400 ms
        sc.fx_left = 0
        sc.ticks(1)
        sc.roll()
        sc.ticks(TPS)
        R["cooldown"] = {"xp": sc.xp(), "pushes": sc.pushes()}
        # (4) acro.dodgeMinMove 0: every in-place roll pays (new jar only)
        if NEW:
            setstatic(AcroCfg, "DODGE_MOVE", JDouble(0.0))
            sz = Sim(UUID(0x19, 4))
            for i in range(4):
                sz.roll()
                sz.ticks(int(1.5 * TPS))
            R["gate0"] = sz.xp()
            setstatic(AcroCfg, "DODGE_MOVE", JDouble(2.0))
        # (5) creative: rolls while moving pay nothing
        sr = Sim(UUID(0x19, 5), creative=True)
        sr.run = 5.6
        sr.ticks(TPS)
        for i in range(3):
            sr.roll()
            sr.ticks(int(1.6 * TPS))
        R["creative"] = {"xp": sr.xp(), "pushes": sr.pushes()}
        # the slide of one roll (the reason the slide cannot count)
        R["slide_blocks"] = round(sm.slide_total / 6.0, 3)
        return R
    safe("G", sec_G)

    # ================================================================ JG: jumps (unchanged)
    def sec_JG():
        R = {}
        load_cfg(os.path.join(SCRATCH, "jg-cfg-" + mode))
        setstatic(AcroCfg, "RUN", JDouble(0.0))
        setstatic(AcroCfg, "SPRINT", JDouble(0.0))
        setstatic(AcroCfg, "WALK", JDouble(0.0))
        sj = Sim(UUID(0x1A, 1))
        log = []

        def jump():
            sj.jump = True
            sj.tick()
            sj.jump = False
            sj.tick()
            log.append(sj.xp())
        jump()                         # in place: nothing
        sj.ticks(TPS)
        jump()                         # still in place, after the cooldown: nothing
        sj.run = 5.0
        sj.ticks(int(0.5 * TPS))       # 2.5 blocks
        jump()                         # +2
        sj.ticks(int(0.4 * TPS))       # 2 more blocks, only ~0.5 s after the paid jump: cooldown 800 ms -> nothing
        jump()
        sj.ticks(int(0.5 * TPS))       # past the cooldown, moved > 2
        jump()                         # +2
        sj.run = 0.0
        sj.ticks(TPS)
        jump()                         # stopped: moved < 2 since the last paid jump? (it moved ~0.1 after it) -> nothing
        R["log"] = log
        # roll in place, then jump after the 800 ms jump cooldown, 5 times: the roll slide (~5 blocks) must not fill the jump gate
        # (review fix: with no cap this farmed ~2 XP a cycle without walking; 0.4.18 paid it, bounded by its 240 cap). Roll XP off here.
        dxp = float(AcroCfg.DODGE_XP)
        setstatic(AcroCfg, "DODGE_XP", JDouble(0.0))
        sr = Sim(UUID(0x1A, 2))
        sr.ticks(5)
        rj = []
        for i in range(5):
            before = sr.xp()
            sr.roll()
            sr.ticks(int(1.0 * TPS))
            sr.jump = True
            sr.tick()
            sr.jump = False
            sr.ticks(int(0.5 * TPS))
            rj.append(round(sr.xp() - before, 3))
        R["rolljump"] = {"per": rj, "slide": round(sr.slide_total / 5.0, 3), "pushes": sr.pushes()}
        # sprint, roll, keep sprinting 1 s past the roll window, jump: own running after the window still pays the jump
        sk = Sim(UUID(0x1A, 3))
        sk.run = 5.6
        sk.ticks(TPS)
        sk.roll()
        sk.ticks(int(1.6 * TPS))
        b2 = sk.xp()
        sk.jump = True
        sk.tick()
        sk.jump = False
        sk.tick()
        R["sprintjump"] = round(sk.xp() - b2, 3)
        setstatic(AcroCfg, "DODGE_XP", JDouble(dxp))
        return R
    safe("JG", sec_JG)

    # ================================================================ NC: no cap
    def sec_NC():
        R = {}
        load_cfg(os.path.join(SCRATCH, "nc-cfg-" + mode))
        R["cap"] = float(AcroCfg.MAX_PER_MIN)
        s = JArray(JDouble)(SLOTS)
        t0 = 50_000_000
        R["one"] = float(Acro.take(s, JLong(t0), JDouble(600.0)))
        s2 = JArray(JDouble)(SLOTS)
        paid = 0.0
        for i in range(60):
            paid += float(Acro.take(s2, JLong(t0 + 1000 * i), JDouble(10.0)))
        R["minute"] = paid
        # a 60 s run through the real move / dodge, take() once a second like flush: sprint 5.6 b/s, a jump every 0.9 s, a roll every 1.6 s
        sim = Sim(UUID(0x1B, 1))
        sim.run = 5.6
        earned = paid2 = 0.0
        for sec in range(60):
            for k in range(TPS):
                tk = sec * TPS + k
                if tk % 27 == 0:
                    sim.jump = True
                elif tk % 27 == 2:
                    sim.jump = False
                if tk % int(1.6 * TPS) == 5:
                    sim.roll()
                sim.tick()
            whole = math.floor(float(sim.s[11]))
            if whole >= 1.0:
                sim.s[11] = float(sim.s[11]) - whole
                earned += whole
                paid2 += float(Acro.take(sim.s, JLong(sim.t), JDouble(whole)))
        R["run60"] = {"earned": earned, "paid": paid2}
        return R
    safe("NC", sec_NC)

    # ================================================================ M: start twice on the live copy + variants
    def start(d):
        names = ["ManaMig", "HealMig", "DocMig", "ClassManaMig", "SkillLvMig", "KillXpMig"] + (["AcroMig"] if NEW else [])
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
        r["acro"] = [float(AcroCfg.DODGE_MOVE) if NEW else None, float(AcroCfg.MAX_PER_MIN), float(AcroCfg.DODGE_XP), int(AcroCfg.DODGE_CD)]
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
        R["hist_has_old"] = any(v == s0["xp.properties"] for k, v in s1.items() if k.startswith("config-history/"))
        R["log_new"] = s1.get("config-changes.log", b"").decode("utf-8")[len(s0.get("config-changes.log", b"").decode("utf-8")):]
        R["players_same"] = all(s0.get(k) == s1.get(k) == s2.get(k) for k in set(s0) | set(s1) | set(s2) if k.startswith("players/"))
        if not NEW:
            return R
        # the variants: plan() on texts + run() on copies
        Amg = JClass(PKG + "AcroMig")
        live = open(os.path.join(LIVE_DIR, "xp.properties"), "rb").read().decode("latin-1")
        R["live_plain"] = "acro.maxXpPerMinute=240" in live.split("\n") and "acro.dodgeMinMove" not in live

        def plan(t):
            r = Amg.plan(JStr(t))
            if r is None:
                return None
            return {"text": str(r[0]), "rows": [str(x) for x in r[1]], "cap": bool(r[2].booleanValue()), "gate": bool(r[3].booleanValue()),
                    "docs": int(r[4].intValue()), "kept": str(r[5]), "warn": bool(r[6].booleanValue())}

        def runv(name, text):
            d = os.path.join(SCRATCH, "var-%s" % name)
            os.makedirs(os.path.join(d, "players"), exist_ok=True)
            f = os.path.join(d, "xp.properties")
            open(f, "wb").write(text.encode("latin-1"))
            Cfg.FILE = path(f)
            Hist.DIR = None
            Rows.HOME = None
            CLog.FILE = None
            CLog.Q.clear()
            m1 = str(Amg.run())
            b1 = open(f, "rb").read()
            m2 = str(Amg.run())
            b2 = open(f, "rb").read()
            lg = os.path.join(d, "config-changes.log")
            return {"m1": m1, "m2": m2, "after": b1.decode("latin-1"), "same2": b1 == b2,
                    "log": open(lg, "rb").read().decode("utf-8") if os.path.exists(lg) else ""}
        V = {}
        V["hand500"] = runv("hand500", live.replace("\nacro.maxXpPerMinute=240\n", "\nacro.maxXpPerMinute=500\n"))
        V["hand0"] = runv("hand0", live.replace("\nacro.maxXpPerMinute=240\n", "\nacro.maxXpPerMinute=0\n"))
        V["crlf"] = runv("crlf", live.replace("\n", "\r\n"))
        V["gate5"] = runv("gate5", live.replace("\nacro.dodgeCooldownMs=400\n", "\nacro.dodgeCooldownMs=400\nacro.dodgeMinMove=5\n"))
        nocd = "\n".join(ln for ln in live.split("\n") if not ln.startswith("acro.dodgeCooldownMs"))
        V["nocd"] = runv("nocd", nocd)
        noacro = "\n".join(ln for ln in live.split("\n") if not ln.startswith("acro."))
        V["noacro_plan"] = plan(noacro)
        R["V"] = V
        R["plan_live"] = plan(live)
        # the 0.4.18 default file -> exactly the 0.4.19 default file
        R["def_new"] = str(Cfg.DEFAULTS)
        return R
    safe("M", sec_M)

    if not NEW:
        D["def_prev"] = str(Cfg.DEFAULTS)
        json.dump(res, open(out, "w"), indent=1)
        return

    def sec_DEF():
        prevdef = open(os.path.join(SCRATCH, "def-prev.txt"), "rb").read().decode("latin-1") if os.path.exists(os.path.join(SCRATCH, "def-prev.txt")) else None
        if prevdef is None:
            return {"skip": True}
        r = JClass(PKG + "AcroMig").plan(JStr(prevdef))
        return {"planned": None if r is None else str(r[0]), "new": str(Cfg.DEFAULTS), "rows": [] if r is None else [str(x) for x in r[1]],
                "plan_new_default": JClass(PKG + "AcroMig").plan(JStr(str(Cfg.DEFAULTS))) is None}
    safe("DEF", sec_DEF)

    # ================================================================ KC: the real config kit on the migrated copy (get + Undo)
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
        R["get_gate"] = str(fn.apply(OA(["get", "acro.dodgeMinMove"])))
        R["get_cap"] = str(fn.apply(OA(["get", "acro.maxXpPerMinute"])))
        R["live_vals"] = [float(AcroCfg.DODGE_MOVE), float(AcroCfg.MAX_PER_MIN)]
        # SkyyMenu's Undo = a plain set back to the logged old value (via undo needs an admin UUID; the console path is the same set)
        R["undo_cap"] = op("set", "acro.maxXpPerMinute", "240", None, "console", "yes", "console")
        R["undo_gate"] = op("set", "acro.dodgeMinMove", "0", None, "console", "yes", "console")
        CfgPub.flush()
        txt = open(kf, "rb").read().decode("latin-1").split("\n")
        R["file_after_undo"] = [ln for ln in txt if ln.startswith(("acro.maxXpPerMinute", "acro.dodgeMinMove"))]
        try:
            Cfg.load()
        except Exception:
            pass
        R["vals_after_undo"] = [float(AcroCfg.DODGE_MOVE), float(AcroCfg.MAX_PER_MIN)]
        cols = ("KEYS", "LABELS", "CATS", "TYPES", "DEFS", "MINS", "MAXS", "OPTS", "UNITS", "FLAGS", "HELPS")
        arrs = [[str(x) for x in getattr(Rows, c)] for c in cols]
        rows = [list(r) for r in zip(*arrs)]
        R["rows"] = dict((r[0], r) for r in rows if r[0] in ("acro.dodgeMinMove", "acro.maxXpPerMinute", "acro.dodgeXp", "acro.jumpMinMove"))
        R["order"] = [r[0] for r in rows]
        CfgPub.shutdown()
        return R
    safe("KC", sec_KC)
    json.dump(res, open(out, "w"), indent=1)


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
    for mode, jar in (("prev", PREV_JAR), ("new", JAR)):     # prev first: its default file feeds section DEF of the new run
        outp = os.path.join(SCRATCH, "run-%s.json" % mode)
        logp = os.path.join(SCRATCH, "run-%s.log" % mode)
        with open(logp, "wb") as lf:
            p = subprocess.run([sys.executable, me, "--child", jar, "--out", outp, "--fakes", os.pathsep.join([fake, fake2]), "--mode", mode,
                                "--dir", SCRATCH], env=env, stdout=lf, stderr=subprocess.STDOUT)
        check(p.returncode == 0 and os.path.isfile(outp), "child JVM (%s) ran (log %s)" % (mode, logp))
        if os.path.isfile(outp):
            outs[mode] = json.load(open(outp))
            if mode == "prev" and "def_prev" in outs[mode]["data"]:
                open(os.path.join(SCRATCH, "def-prev.txt"), "wb").write(outs[mode]["data"]["def_prev"].encode("latin-1"))
    auo = os.path.join(SCRATCH, "audit.json")
    pa = subprocess.run([sys.executable, me, "--audit", JAR, "--fake", fake, "--out", auo, "--dir", SCRATCH], env=env, capture_output=True)
    check(pa.returncode == 0 and os.path.isfile(auo), "engine-access audit child ran: %s" % pa.stderr[-500:])
    if FAILS:
        return finish()
    for mode in ("new", "prev"):
        r = outs[mode]
        check(not r["load_fails"] and r["loaded"] == r["classes"], "A (%s): %d / %d classes load under -Xverify:all %s" % (mode, r["loaded"], r["classes"], r["load_fails"][:3]))
    N, P = outs["new"]["data"], outs["prev"]["data"]
    for k in ("G", "JG", "NC", "M", "DEF", "KC"):
        check(k in N and "error" not in N[k], "section %s ran: %s" % (k, (N.get(k) or {}).get("error")))
    for k in ("G", "JG", "NC", "M"):
        check(k in P and "error" not in P[k], "control (0.4.18) section %s ran: %s" % (k, (P.get(k) or {}).get("error")))
    if FAILS:
        return finish()
    print("A. both jars: every class loads under -Xverify:all (%d / %d classes)" % (outs["new"]["loaded"], outs["prev"]["loaded"]))

    # ---------------------------------------------------------------- G
    G, GP = N["G"], P["G"]
    check(G["cfg"][:5] == [3.0, 400, 0.0, 2.0, 800] and G["gate"] == 2.0 and G["settle"] == 700,
          "G: fresh default file: dodgeXp 3, cooldown 400, cap 0, jumpMinMove 2.0, jump cooldown 800; dodgeMinMove 2.0; settle 700 ms: %s %s %s" % (G["cfg"], G["gate"], G["settle"]))
    check(GP["cfg"][2] == 240.0, "G control: 0.4.18's default cap is 240: %s" % GP["cfg"])
    ip = G["inplace"]
    check([p_[0] for p_ in ip["per"]] == [3.0, 0.0, 0.0, 0.0, 0.0, 0.0] and ip["pushes"] == 6,
          "G: rolling IN PLACE after a 3-block walk: only the first roll pays (each roll slides %s blocks - not counted); the push comes on all 6: %s" % (G["slide_blocks"], ip))
    check(G["slide_blocks"] > 2.0 and max(p_[2] for p_ in ip["per"]) < 1.0,
          "G: one roll slides %s blocks (> the 2.0 gate - why the slide cannot count); the gate counter after each in-place roll stays < 1: %s" % (G["slide_blocks"], [p_[2] for p_ in ip["per"]]))
    check([p_[0] for p_ in GP["inplace"]["per"]] == [3.0] * 6, "G control: 0.4.18 pays every in-place roll: %s" % GP["inplace"]["per"])
    mv = G["moving"]
    check(mv["per"] == [3.0] * 6 and mv["pushes"] == 6, "G: rolling while SPRINTING (a roll every 1.6 s): every roll pays: %s" % mv)
    check(G["cooldown"]["xp"] == 3.0 and G["cooldown"]["pushes"] == 1, "G: a second roll 200 ms later (inside the 400 ms cooldown) is not counted: %s" % G["cooldown"])
    check(G["gate0"] == 12.0, "G: acro.dodgeMinMove 0 = no gate: 4 in-place rolls pay 12: %s" % G["gate0"])
    check(G["creative"]["xp"] == 0.0 and G["creative"]["pushes"] == 3, "G: Creative rolls pay nothing (push kept): %s" % G["creative"])
    print("G. roll gate: in place 3, 0, 0, 0, 0, 0 (slide %.2f blocks not counted; 0.4.18 paid 6 x 3); sprinting 6 x 3; cooldown; gate 0 = 12; Creative 0" % G["slide_blocks"])

    # ---------------------------------------------------------------- JG
    jl, jlp = N["JG"]["log"], P["JG"]["log"]
    check(jl == [0.0, 0.0, 2.0, 2.0, 4.0, 4.0] and jl == jlp, "JG: jumps unchanged (in place 0, after 2.5 blocks +2, inside 800 ms 0, after +2, stopped 0), same as 0.4.18: %s vs %s" % (jl, jlp))
    rjn, rjp = N["JG"]["rolljump"], P["JG"]["rolljump"]
    check(rjn["per"] == [0.0] * 5 and rjn["pushes"] == 5, "JG: roll in place + jump after the jump cooldown x5: the roll slide (%s blocks) does not fill the jump gate - 0 jump XP: %s" % (rjn["slide"], rjn))
    check(sum(rjp["per"]) > 0.0, "JG control: 0.4.18 paid jump XP from the roll slide (the farm the fix closes): %s" % rjp)
    check(N["JG"]["sprintjump"] == 2.0, "JG: sprint, roll, sprint on past the roll window, jump: the jump pays 2: %s" % N["JG"]["sprintjump"])
    print("JG. jumps: %s (0.4.18 identical); roll + jump in place: %s (0.4.18 %s); sprint-roll-jump +%s" % (jl, rjn["per"], rjp["per"], N["JG"]["sprintjump"]))

    # ---------------------------------------------------------------- NC
    NC, NCP = N["NC"], P["NC"]
    check(NC["cap"] == 0.0 and NC["one"] == 600.0 and NC["minute"] == 600.0, "NC: no cap - 600 XP in one second paid, 10 a second for 60 s = 600: %s" % NC)
    check(NCP["one"] == 240.0 and NCP["minute"] == 240.0, "NC control: 0.4.18 stops at 240: %s" % NCP)
    r6 = NC["run60"]
    check(r6["paid"] == r6["earned"] and r6["paid"] > 240.0, "NC: 60 s of sprint + jumps + rolls through move / dodge / take: every earned XP paid (%s > 240)" % r6)
    check(NCP["run60"]["paid"] <= 240.0, "NC control: 0.4.18 pays at most 240 of the same minute: %s" % NCP["run60"])
    print("NC. no cap: 600 in a second, 600 in a minute; 60 s run paid %d (0.4.18: %d)" % (r6["paid"], NCP["run60"]["paid"]))

    # ---------------------------------------------------------------- M
    M = N["M"]
    check(M["live_plain"], "M: the live file is still on 240 and has no acro.dodgeMinMove (the migration case)")
    exp = expected_migration(M["xp0"])
    check(M["xp1"] == exp, "M: start 1 writes exactly the planned lines (dodge comment, marker + acro.dodgeMinMove=2.0 under the cooldown, cap comment, 240 -> 0): %s"
          % [d for d in zip(M["xp1"].split("\n"), exp.split("\n")) if d[0] != d[1]][:3])
    check("\r" not in M["xp1"] and M["xp0"].count("\n") + 2 == M["xp1"].count("\n"), "M: LF kept, exactly 2 lines more")
    check(M["hist_has_old"], "M: config-history holds the old xp.properties bytes")
    lg = [ln.split("\t") for ln in M["log_new"].strip().split("\n") if ln.strip()]
    check(len(lg) == 2 and lg[0][1:] == ["SkyySkills 0.4.19", "-", "update", "acro.maxXpPerMinute", "240", "0", "ok"]
          and lg[1][1:] == ["SkyySkills 0.4.19", "-", "update", "acro.dodgeMinMove", "0", "2.0", "ok"], "M: 2 change-log lines (Undo 240 / 0): %s" % lg)
    check(M["r1"]["AcroMig"].startswith("xp.properties updated for 0.4.19") and M["r2"]["AcroMig"] == "" and M["changed2"] == [],
          "M: start 2 changes nothing (marker): %s / %s" % (M["changed2"], M["r1"]["AcroMig"][:120]))
    check(M["r1"]["acro"][:2] == [2.0, 0.0] and M["players_same"], "M: the loaded values after start 1: gate 2.0, cap 0; players/ untouched: %s" % M["r1"]["acro"])
    ch1 = [k for k in M["changed1"] if not k.startswith("config-history/")]
    chp = [k for k in P["M"]["changed1"] if not k.startswith("config-history/")]
    check(set(ch1) - set(chp) <= {"xp.properties", "config-changes.log"}, "M: start 1 touches only xp.properties / config-changes.log / config-history beyond what 0.4.18 does: %s vs %s" % (ch1, chp))
    check(P["M"]["changed2"] == [] and P["M"]["xp1"] == M["xp0"], "M control: 0.4.18 leaves the live copy as it is: %s" % P["M"]["changed1"])
    V = M["V"]
    h5 = V["hand500"]
    check("\nacro.maxXpPerMinute=500\n" in h5["after"] and "acro.dodgeMinMove=2.0" in h5["after"] and "kept (an admin's value)" in h5["m1"]
          and h5["m2"] == "" and h5["same2"] and "acro.maxXpPerMinute" not in h5["log"] and "acro.dodgeMinMove\t0\t2.0" in h5["log"],
          "M: hand-set 500 kept (INFO), gate added, only the gate logged; second run nothing: %s" % h5["m1"][:200])
    h0 = V["hand0"]
    check("\nacro.maxXpPerMinute=0\n" in h0["after"] and "0 means NO cap" in h0["m1"] and h0["m2"] == "" and h0["same2"],
          "M: hand-set 0 kept with the 'now means no cap' note: %s" % h0["m1"][-200:])
    cr = V["crlf"]
    check(cr["after"].count("\r\n") == cr["after"].count("\n") and expected_migration(M["xp0"]).replace("\n", "\r\n") == cr["after"] and cr["m2"] == "" and cr["same2"],
          "M: a CRLF file: the same lines, CRLF kept on every line")
    g5 = V["gate5"]
    check("\nacro.dodgeMinMove=5\n" in g5["after"] and g5["after"].count("acro.dodgeMinMove=") == 1 and MARK in g5["after"]
          and "acro.dodgeMinMove" not in g5["log"] and "acro.maxXpPerMinute\t240\t0" in g5["log"] and g5["m2"] == "",
          "M: a file that already has acro.dodgeMinMove=5 keeps it (marker only), cap still migrated: %s" % g5["m1"][:200])
    nc_ = V["nocd"]
    check(nc_["after"].endswith(MARK + "\nacro.dodgeMinMove=2.0\n") and nc_["m2"] == "", "M: no acro.dodgeCooldownMs line: marker + gate appended at the end")
    check(V["noacro_plan"] is None, "M: a file with no acro.* key: nothing (AcroCfg.ensureDefaults appends the whole section)")
    DF = N["DEF"]
    check(not DF.get("skip") and (DF["planned"] or "").replace("# SkyySkills %s - XP rules." % PREV_VERSION, "# SkyySkills %s - XP rules." % VERSION, 1) == DF["new"]
          and DF["plan_new_default"]
          and DF["rows"] == ["acro.maxXpPerMinute", "240", "0", "acro.dodgeMinMove", "0", "2.0"],
          "M: the 0.4.18 default file migrates to exactly the 0.4.19 default file (the version header line aside); the 0.4.19 default needs nothing")
    print("M. live copy: start 1 = %s (+2 lines, LF kept, History + 2 Undo lines), start 2 = nothing; variants 500 / 0 / CRLF / gate 5 / no cooldown / no acro / defaults" % ", ".join(ch1))

    # ---------------------------------------------------------------- KC
    KC = N["KC"]
    rr = KC["rows"]
    check(KC["get_gate"] in ("2.0", "2") and KC["get_cap"] == "0" and KC["live_vals"] == [2.0, 0.0], "KC: get acro.dodgeMinMove %s, acro.maxXpPerMinute %s" % (KC["get_gate"], KC["get_cap"]))
    check(KC["undo_cap"][0] == "ok" and KC["undo_gate"][0] == "ok" and "acro.maxXpPerMinute=240" in KC["file_after_undo"]
          and "acro.dodgeMinMove=0" in KC["file_after_undo"] and KC["vals_after_undo"] == [0.0, 240.0],
          "KC: Undo of both lines through the real kit -> 240 / 0 (= 0.4.18 behaviour): %s %s %s %s" % (KC["undo_cap"], KC["undo_gate"], KC["file_after_undo"], KC["vals_after_undo"]))
    g = rr["acro.dodgeMinMove"]
    check(g[1:10] == ["Move between paid rolls", "acrobatics", "dec", "2.0", "0", "1000", "", "blocks", "live,adv"] and len(g[10]) <= 100,
          "KC: the acro.dodgeMinMove row: %s" % g)
    check(rr["acro.maxXpPerMinute"][4] == "0" and "0 = no cap" in rr["acro.maxXpPerMinute"][10], "KC: the cap row default 0, help says 0 = no cap: %s" % rr["acro.maxXpPerMinute"])
    o_ = KC["order"]
    check(o_[o_.index("acro.dodgeCooldownMs") + 1] == "acro.dodgeMinMove" and o_[o_.index("acro.dodgeMinMove") + 1] == "acro.roll" and len(o_) == 203,
          "KC: acro.dodgeMinMove sits after the dodge cooldown row; 203 rows (%d)" % len(o_))
    print("KC. real kit: gate 2.0 / cap 0 read; Undo -> 240 / 0; row + place")

    # ---------------------------------------------------------------- F
    jz, pz = zipfile.ZipFile(JAR), zipfile.ZipFile(PREV_JAR)
    ca = dict((n, pz.read(n)) for n in pz.namelist() if n.endswith(".class"))
    cb = dict((n, jz.read(n)) for n in jz.namelist() if n.endswith(".class"))
    new_cls = sorted(n.split("/")[-1][:-6] for n in set(cb) - set(ca))
    gone_cls = sorted(set(ca) - set(cb))

    def vnorm(b):
        return b.replace(b"SkyySkills %s - " % PREV_VERSION.encode(), b"SkyySkills %s - " % VERSION.encode())
    changed = sorted(n.split("/")[-1][:-6] for n in set(ca) & set(cb) if ca[n] != cb[n] and ca[n].replace(PREV_VERSION.encode(), VERSION.encode()) != cb[n]
                     and vnorm(ca[n]) != cb[n])
    must = {"Acro", "AcroCfg", "SkillCfg", "CfgRows", "SkyySkillsPlugin"}
    allowed = must | {"CfgFile", "SkillKit"}
    check(new_cls == ["AcroMig"] and not gone_cls, "F: AcroMig is the only new class, none removed: %s %s" % (new_cls, gone_cls))
    check(set(changed) <= allowed and must <= set(changed), "F: classes changed beyond the version string: %s (allowed %s)" % (changed, sorted(allowed)))
    other = sorted(n for n in set(jz.namelist()) | set(pz.namelist()) if not n.endswith(".class") and n != "manifest.json"
                   and (n not in jz.namelist() or n not in pz.namelist() or jz.read(n) != pz.read(n)))
    check(other == [], "F: every asset file (the 11 dodge files, the spell overrides) byte-identical: %s" % other[:3])
    print("F. 0.4.18 -> 0.4.19: + AcroMig; changed %s; %d classes unchanged; assets identical" % (changed, len(ca) - len(changed)))
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
