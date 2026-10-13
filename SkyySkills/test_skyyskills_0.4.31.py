"""SkyySkills 0.4.31 - bare-JVM harness for THE ACROBATICS XP LINE NO LONGER SPANS A LEVEL-UP (tools/skills_0_4_31_patch.py; Skyy's
2026-10-11 play test chat: "next: Acrobatics 12 at 1/7500 XP" then "+70 Acrobatics XP (40/7500)").
Every child JVM runs the game's own JRE with HytaleServer.jar on the class path, -Xverify:all, -XX:-UsePerfData, TEMP / TMP /
java.io.tmpdir in the scratch folder. Live save data is only ever READ and copied into scratch (checked: the live files are unchanged).

    python SkyySkills/test_skyyskills_0.4.31.py --dir <empty folder inside tools/dev/scratch/> [--keep]
         [--jar SkyySkills-0.4.31.jar] [--prev SkyySkills-0.4.30.jar] [--pre <pre-fix 0.4.31 jar>] [--live <Skyy_SkyySkills folder>]

SECTIONS (H runs the REAL Acro.flush -> Acro.award -> SkillXp.gain2 -> gain4 -> SkillMsg on a stand-in PlayerRef whose PacketHandler
keeps every chat text; the 0.4.30 jar run the same way = the control, which REPRODUCES the bug)
  A   every class of the new jar loads, verifies (-Xverify:all) and initialises
  H1  LEVEL-UP: 4950/5000-style start, three 1 s pays (the 2nd levels up), then the 30 s line. 0.4.31: "+N Acrobatics XP (p/M)" BEFORE
      "SKILL LEVEL UP", the next line's +N adds up from the "next: at p/M" number; 0.4.30: no line before the level-up and the 30 s line
      sums XP from before the level-up (p + N != shown) = the bug. Same XP stored by both jars.
  H2  NO LEVEL-UP: both jars print the same lines and keep the same counter (0.4.30's exact behaviour)
  H3  skills.xpGain OFF (settings:fn:get stub): nothing staged, no "+N" line, level-up lines still sent
  H4  FALL XP that levels up: the movement counter counted so far is shown with it, before SKILL LEVEL UP; counter restarts
  H5  an award that THROWS (no PacketHandler on the level-up line): the exception still leaves, no stage outlives it; the counter after
      it is 0 (the level-up line took the stage) or 0.4.30's
  --- fixer round (critic findings; --pre <the pre-fix 0.4.31 test jar> runs the same child on it = the control that REPRODUCES them):
  H6  an award that throws BEFORE paying (a corrupt profile entry -> ClassCastException in SkillStore.addK): the counter s[21] equals
      0.4.30's (the unpaid amount is taken back out), no stage left
  H7  Acro.retainOnline drops the STAGE entry of a player who left and keeps the online player's
  TH  Acro.award's handler catches java/lang/Throwable (Errors too: a LinkageError / StackOverflowError never leaves a stage behind)
  --- Hytale 0.7.0 port (skills07): Mana override + spell costs
  M0  MANA GEN (the generated script's own block, exec'd): the jar's Mana.json = MANA GEN on Assets.zip's 0.7 file (Max / InitialValue 0,
      +1 every 0.2 s if Alive + NoDamageTaken 6 s, Creative entry untouched); 0.6's file -> no override; 0.7-pre.4's -> Max only; every
      unknown shape stops the build
  S0  SPELL GEN: a 0.7 staff (drain var only) is planned, a 0.6 staff (dead check var + drain) still is; bad shapes still refused
  S1  the gate simulation (engine rules) on Assets.zip 0.7 + the jar's files: wand 5, staff 10, spellbook 20, blunderbuss 10, every paid
      cast checks what it spends; control = vanilla 0.7 staffs spend 50 with no check
  M1  (child JVM, real engine) the engine's EntityStatType.CODEC decodes the shipped Mana.json
  M2  out of combat 5 / s (engine) + 0; in combat (hit 1 s ago) engine 0 + SkyySkills 3.75 / s (75 %), 5 s of combat left (REAL ManaRegen
      .state / rates / amount / combatLeft + Condition.allConditionsMet); control 0.4.30 on 0.7: 3.33 / s in and out, never in combat
  M3  Overall.baseMana on the decoded max: none 25, Mage 45, Priest 42; control 0.4.30 on 0.7: everyone 100
  M4  ManaCost (the Java gate table) = S1's rows; staff check none -> 10, wand 25 -> 5, spellbook 25 -> 20
  --- 0.7 port fixer round (skills07fix, critic findings)
  O0  ONHIT GEN (exec'd) on Assets.zip 0.7: the 9 signature Mana-on-hit Amounts / 5; the jar ships exactly those, vanilla but the Amount;
      synthetic: only Mana entries change, unknown shapes stop the build; control: 0.4.30 ships none (Groundslam +25 fills a 25 pool)
  O1  the Mana consumer scan: nothing NOT COVERED on 0.7 + this jar (runes listed as not scaled); control: 0.4.30's files leave 11 uncovered
  O2  (fixer 2) onhit_inheritors on the live-set SkyyArmory jar: its 2 Wynn crossbows inherit the crossbow signature file (NOTE); synthetic
  MG  (child JVM) ManaGuard.manaFacts / manaReport on the engine-decoded shipped Mana.json -> INFO; on vanilla 0.7's (another mod's file
      won) -> one WARN naming max 100, refill 3.333, no combat pause and the pack; manaCheck() runs in a bare JVM (unreadable -> retry)
  CC  CLASS COMPARE 0.4.30 -> 0.4.31 (+ the 0.7 rebuild set: ManaCost, ManaGuard, setup, FellDefs, FellRead, blockIdAt): only SkillMsg (STAGE, stage, unstage, take, <clinit>) and Acro (award, flush) differ; no class added
  ST  START TWICE on a scratch COPY of the live Skyy_SkyySkills (the 0.4.25 harness's start routine), both jars: 0.4.31 changes exactly
      what 0.4.30 changes; start 2 changes nothing; player files untouched
  AU  the engine-access audit (every bytecode reference looked up with the JVM's own access rules; control refused)
"""
import os, sys, re, json, shutil, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, PREV_VERSION = "0.4.31", "0.4.30"
PKG = "com.skyy.skills."
ACRO = 4


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "skills0431", "h")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
PREV_JAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyySkills-%s.jar" % PREV_VERSION)))
PRE_JAR = os.path.abspath(arg("--pre")) if arg("--pre") else None
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
LIVE_DIR = os.path.abspath(arg("--live", os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyySkills")))
KEEP = "--keep" in sys.argv
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


def snap(d):
    return dict((os.path.relpath(os.path.join(r, f), d).replace(os.sep, "/"), open(os.path.join(r, f), "rb").read())
                for r, _ds, fs in os.walk(d) for f in fs)


# ============================================================================================ child: H (one jar)
def run_h(jar, fake, home, out, new):
    from jpype import JClass, JImplements, JOverride, JLong
    T = t15()
    res, path = T.common(jar, [fake])
    R = {"loaded": res["loaded"], "classes": res["classes"], "load_fails": res["load_fails"]}
    if res["load_fails"]:
        json.dump(R, open(out, "w"), indent=1)
        return
    UUID, CHM = JClass("java.util.UUID"), JClass("java.util.concurrent.ConcurrentHashMap")
    J = lambda n: JClass(PKG + n)
    Cfg, Xp, Store, Defs, Acro, Msg, ACfg = J("SkillCfg"), J("SkillXp"), J("SkillStore"), J("SkillDefs"), J("Acro"), J("SkillMsg"), J("AcroCfg")
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    Universe, Holder = JClass("com.hypixel.hytale.server.core.universe.Universe"), JClass("com.hypixel.hytale.component.Holder")
    FakeH, FakeW = JClass("skyytest.FakeHandler"), JClass("skyytest.FakeWorld")
    HL = JClass("com.hypixel.hytale.logger.HytaleLogger")
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)

    def setf(obj, cls, name, val):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        f.set(obj, val)

    def getf(obj, cls, name):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        return f.get(obj)

    def alloc(cls):
        return U.allocateInstance(cls.class_)
    D = {}
    try:
        Cfg.LOG = HL.get("SkyySkills")
        Cfg.FILE = path(os.path.join(home, "xp.properties"))
        D["cfg"] = str(Cfg.load())[:200]
        Store.DIR = path(os.path.join(home, "players"))
        Store.DATA.clear()
        bridge = Store.bridge()
        uni = alloc(Universe)
        PLAYERS, WORLDS = CHM(), CHM()
        setf(uni, Universe, "playersByUuid", PLAYERS)
        setf(uni, Universe, "players", PLAYERS.values())
        setf(uni, Universe, "worldsByUuid", WORLDS)
        setf(None, Universe, "instance", uni)
        wuid = UUID(0x3031D, 1)
        WORLDS.put(wuid, alloc(FakeW))
        handler, holder = alloc(FakeH), alloc(Holder)
        TEXTS = getf(None, FakeH, "TEXTS")

        def mkpr(u, name, h=handler):
            pr = alloc(PRef)
            setf(pr, PRef, "uuid", u)
            setf(pr, PRef, "username", name)
            setf(pr, PRef, "packetHandler", h)
            setf(pr, PRef, "worldUuid", wuid)
            setf(pr, PRef, "holder", holder)
            PLAYERS.put(u, pr)
            return pr
        OFF = set()

        @JImplements("java.util.function.Function")
        class Settings(object):
            @JOverride
            def apply(self, o):
                a = list(o)
                if str(a[0]) in OFF and str(a[1]) == "skills.xpGain":
                    return JClass("java.lang.Boolean").FALSE
                return JClass("java.lang.Boolean").TRUE
        bridge.put("settings:fn:get", Settings())
        D["mult"] = int(Cfg.scaled(JLong(1000)))
        D["acro_feedback_ms"] = int(ACfg.FEEDBACK_MS)
        D["acro_max_per_min"] = float(ACfg.MAX_PER_MIN)
        D["feedback"] = bool(Cfg.FEEDBACK)
        # the first total that is Acrobatics level 11 (whatever the curve) -> start 50 below it
        lo, hi = 0, 1
        while int(Defs.levelOf(ACRO, JLong(hi))) < 11:
            hi *= 2
        while lo < hi:
            mid = (lo + hi) // 2
            if int(Defs.levelOf(ACRO, JLong(mid))) >= 11:
                hi = mid
            else:
                lo = mid + 1
        T11 = lo
        D["T11"] = T11
        D["need11"] = int(Defs.needFor(ACRO, JLong(T11)))

        def total(u):
            return int(Store.dataK(str(u), u)[ACRO])

        def lines():
            return [str(t) for t in TEXTS if ("Acrobatics" in str(t))]

        def has_stage(u):
            return bool(new) and Msg.STAGE.containsKey(u)

        def scenario(tag, u, pr, start, steps, hooks=None):
            """steps = [(ms after t0, whole XP for s[11], fall XP for s[152])]; returns texts, totals, counter per step"""
            Store.addK(str(u), u, tag, ACRO, JLong(start))
            s = Acro.state(u)
            t0 = 10000000
            s[21] = 0.0
            s[22] = float(t0)
            TEXTS.clear()
            Msg.PEND.clear()
            Msg.LAST.clear()
            rec = []
            for i, (dt, w, f) in enumerate(steps):
                if hooks and i in hooks:
                    hooks[i]()
                s[11] = float(w)
                s[152] = float(f)
                if dt >= 30000:
                    Msg.LAST.clear()        # the 2 s chat throttle is wall clock: 30 s of game time have passed here
                err = None
                try:
                    Acro.flush(pr, s, JLong(t0 + dt))
                except Exception as e:
                    err = str(e)[:200]
                bad = bool(hooks and "corrupt" in hooks and i >= 1)   # H6: the profile entry is not readable after the hook
                rec.append({"dt": dt, "total": -1 if bad else total(u), "lv": -1 if bad else int(Store.level(u, ACRO)), "s21": float(s[21]), "s22": float(s[22]) - t0,
                            "staged": has_stage(u), "err": err})
            return {"texts": lines(), "all": [str(t) for t in TEXTS], "rec": rec, "start": start}
        # H1: the level-up the chat showed
        u1 = UUID(0x3031, 1)
        pr1 = mkpr(u1, "AcroLevel")
        D["H1"] = scenario("H1", u1, pr1, T11 - 50, [(1000, 20, 0), (2000, 20, 0), (3000, 20, 0), (33000, 0, 0)])
        # H2: no level-up
        u2 = UUID(0x3031, 2)
        pr2 = mkpr(u2, "AcroPlain")
        D["H2"] = scenario("H2", u2, pr2, 100, [(1000, 3, 0), (2000, 4, 0), (3000, 2, 0), (31000, 0, 0), (32000, 5, 0)])
        # H3: skills.xpGain off for that player
        u3 = UUID(0x3031, 3)
        pr3 = mkpr(u3, "AcroQuiet")
        OFF.add(str(u3))
        D["H3"] = scenario("H3", u3, pr3, T11 - 50, [(1000, 20, 0), (2000, 20, 0), (33000, 0, 0)])
        D["H3"]["stage_after"] = has_stage(u3)
        OFF.discard(str(u3))
        # H4: a big fall levels up while movement XP is still unshown
        u4 = UUID(0x3031, 4)
        pr4 = mkpr(u4, "AcroFall")
        D["H4"] = scenario("H4", u4, pr4, T11 - 50, [(1000, 10, 0), (2000, 0, 40), (33000, 4, 0)])
        # H5: no PacketHandler -> the level-up's sendMessage throws out of gain4 (AcroSys catches it in game)
        u5 = UUID(0x3031, 5)
        pr5 = mkpr(u5, "AcroThrow", None)
        D["H5"] = scenario("H5", u5, pr5, T11 - 50, [(1000, 20, 0), (2000, 20, 0)])
        D["H5"]["stage_after"] = has_stage(u5)
        D["H5"]["stage_size"] = int(Msg.STAGE.size()) if new else 0
        # H6 (fixer): the 2nd award throws BEFORE any XP is stored - the profile entry is not a long[] (ClassCastException in addK)
        u6 = UUID(0x3031, 6)
        pr6 = mkpr(u6, "AcroCorrupt")
        k6 = str(Store.pkey(u6))

        def corrupt():
            Store.DATA.put(k6, JClass("java.lang.String")("corrupt"))
        D["H6"] = scenario("H6", u6, pr6, 100, [(1000, 20, 0), (2000, 20, 0)], {1: corrupt, "corrupt": True})
        D["H6"]["stage_after"] = has_stage(u6)
        D["H6"]["stage_size"] = int(Msg.STAGE.size()) if new else 0
        Store.DATA.remove(k6)
        # H7 (fixer): a player who left keeps no stage (Acro.retainOnline); the online player's entry stays
        if new:
            gone = UUID(0x3031, 0x77)
            Msg.stage(gone, ACRO, JLong(5))
            Msg.stage(u1, ACRO, JLong(7))
            Acro.retainOnline()
            D["H7"] = {"gone_kept": bool(Msg.STAGE.containsKey(gone)), "online_kept": bool(Msg.STAGE.containsKey(u1))}
            Msg.STAGE.clear()
        Store.DATA.clear()
        Store.DIRTY.clear()
    except Exception:
        import traceback
        D["error"] = traceback.format_exc()[-3000:]
    R["D"] = D
    json.dump(R, open(out, "w"), indent=1)


# ============================================================================================ child: M (0.7 port: Mana + spell costs, one jar)
ASSETS = os.path.join(APPDATA, "Hytale", "install", "release", "package", "game", "latest", "Assets.zip")
MANA_PATH = "Server/Entity/Stats/Mana.json"


def run_m(jar, fake, home, out):
    """M1-M4 on the REAL engine (HytaleServer 0.7 on the class path) + the jar's REAL ManaRegen / Overall / ManaCost:
    the Mana stat this jar makes the server use (its shipped Mana.json, else Assets.zip's) DECODED by the engine's own EntityStatType.CODEC
    (the conditions registered under the ids EntityModule registers), its regen entries as real RegeneratingValues, then out of combat
    (last hit 60 s ago) and in combat (1 s ago): the engine's own flat-refill test (Condition.allConditionsMet = vanilla refills or not),
    ManaRegen.state / rates / amount / combatLeft, the Mana a second (vanilla's + SkyySkills'), and Overall.baseMana's modifier on the
    stat type's max (no class / Mage / Priest). Also ManaCost's gate table (what the jar's Java believes each caster checks / spends)."""
    from jpype import JClass, JArray, JFloat
    T = t15()
    res, path = T.common(jar, [fake])
    R = {"loaded": res["loaded"], "classes": res["classes"], "load_fails": res["load_fails"]}
    try:
        E = T.regen_env()
        Cond = JClass("com.hypixel.hytale.server.core.modules.entity.condition.Condition")
        P = "com.hypixel.hytale.server.core.modules.entity.condition."
        for k, cls in (("Alive", "AliveCondition"), ("NoDamageTaken", "NoDamageTakenCondition"),
                       ("CheckPlayerGameMode", "CheckPlayerGameModeCondition"), ("Charging", "ChargingCondition")):
            K = JClass(P + cls)
            Cond.CODEC.register(k, K.class_, K.CODEC)
        EST = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType")
        Bson, EI = JClass("org.bson.BsonDocument"), JClass("com.hypixel.hytale.codec.ExtraInfo")
        zj = zipfile.ZipFile(jar)
        shipped = MANA_PATH in zj.namelist()
        txt = zj.read(MANA_PATH).decode("utf-8") if shipped else zipfile.ZipFile(ASSETS).read(MANA_PATH).decode("utf-8-sig")
        t = EST.CODEC.decode(Bson.parse(txt), EI())
        R["shipped"] = shipped
        R["stat"] = {"initial": float(t.getInitialValue()), "min": float(t.getMin()), "max": float(t.getMax()), "reset": str(t.getResetBehavior()),
                     "regen": [[round(float(r.getAmount()), 4), round(float(r.getInterval()), 4), str(r.getRegenType()),
                                [str(c.getClass().getSimpleName()) for c in r.getConditions()]] for r in t.getRegenerating()]}
        Mana, Ovl, OCfg = JClass(PKG + "ManaRegen"), JClass(PKG + "Overall"), JClass(PKG + "OverallCfg")
        RGV, Instant = E["RGV"], E["Instant"]
        rv = JArray(RGV)([RGV(r) for r in t.getRegenerating()])
        flat = [r for r in t.getRegenerating() if str(r.getRegenType()) == "ADDITIVE" and float(r.getAmount()) > 0]
        acc, dd, now = E["acc"], E["dd"], E["now"]
        Mana.IN_COMBAT = 75
        R["phase"] = {}
        for tag, ago in (("out", 60), ("in", 1)):
            dd.setLastDamageTime(now.minusSeconds(ago))
            van = sum((float(r.getAmount()) / float(r.getInterval())) for r in flat if bool(Cond.allConditionsMet(acc, None, now, r)))
            rt = [float(x) for x in Mana.rates(acc, None, now, rv)]
            ours = float(Mana.amount(JArray(JFloat)(rt), 0.0, 75, JFloat(1.0), JFloat(0.0), JFloat(45.0)))
            R["phase"][tag] = {"states": [int(Mana.state(acc, None, now, r)) for r in flat], "rates": [round(x, 4) for x in rt],
                               "vanilla_per_s": round(van, 4), "skyy_per_s": round(ours, 4), "total_per_s": round(van + ours, 4),
                               "combat_left_ms": int(Mana.combatLeft(acc, None, now, rv))}
        # Base Mana: the StaticModifier amount Overall.baseMana posts on top of the stat type's max, and the max a player ends with
        Cfg, Store = JClass(PKG + "SkillCfg"), JClass(PKG + "SkillStore")
        Cfg.FILE = path(os.path.join(home, "xp.properties"))
        Cfg.load()
        UUID = JClass("java.util.UUID")
        R["base"] = {}
        for cls in ("", "Mage", "Priest", "Warrior"):
            u = UUID(0x707, len(cls) + 1)
            if cls:
                Store.bridge().put("profile:class:" + str(u), cls)
            mod = float(Ovl.baseMana(u, JFloat(t.getMax())))
            R["base"][cls or "none"] = {"target": float(Ovl.baseTarget(u)), "modifier": mod, "max": float(t.getMax()) + mod}
        MC = JClass(PKG + "ManaCost")
        R["gates"] = dict((str(MC.GIDS[i]), [str(MC.GCHECK[i]), int(MC.GATE_OLD[i]), int(MC.GATE[i]), int(MC.SPEND_OLD[i]), int(MC.SPEND[i])])
                          for i in range(int(MC.GN)))
        R["ints"] = dict((str(MC.INT_IDS[i]), [str(MC.INT_KIND[i]), int(MC.INT_OLD[i]), int(MC.INT_NEW[i])]) for i in range(int(MC.INT_N)))
        R["arm"] = dict((str(MC.ARM_IDS[i]), [int(MC.ARM_CHECK[i]), int(MC.ARM_SPEND[i])]) for i in range(len(MC.ARM_IDS)))
        # MG (fixer round): ManaGuard's live Mana stat check - the REAL manaFacts / manaReport on the engine-decoded stat this jar ships and
        # on vanilla 0.7's (= what another mod's Mana file loading later would leave), and manaCheck() itself (bare JVM: no asset map)
        MG = JClass(PKG + "ManaGuard")
        if hasattr(MG, "manaFacts"):
            van = EST.CODEC.decode(Bson.parse(zipfile.ZipFile(ASSETS).read(MANA_PATH).decode("utf-8-sig")), EI())
            R["mg"] = {}
            for tag, st in (("shipped", t), ("vanilla07", van)):
                f = MG.manaFacts(st)
                rp = MG.manaReport(f, "Skyy:test")
                R["mg"][tag] = {"facts": [round(float(x), 4) for x in f], "report": [str(rp[0]), str(rp[1])]}
            rn = MG.manaReport(None, None)
            R["mg"]["none"] = [str(rn[0]), str(rn[1])]
            try:
                rc = MG.manaCheck()
                R["mg"]["check"] = [str(rc[0]), str(rc[1])]
            except Exception as e:
                R["mg"]["check"] = ["THREW", str(e)]
            R["mg"]["exp"] = [float(MG.MANA_MAX), float(MG.MANA_PS), bool(MG.MANA_PAUSE), bool(MG.MANA_SHIPPED)]
    except Exception as e:
        import traceback
        R["error"] = traceback.format_exc()[-1500:]
    json.dump(R, open(out, "w"), indent=1)


def gen_block(src, start, end):
    """the text between two marker lines of the generated build script (the pure-Python generator blocks)"""
    i = src.index(start)
    return src[src.index("\n", i) + 1:src.index(end, i)]


def m_python_checks():
    """M0 / S0 (parent, pure Python): the REAL generator blocks of the generated 0.4.31 build script, executed on the 0.7 file, on 0.6's
    shape and on synthetic files; then the jar's asset files against a fresh generation from Assets.zip"""
    src = open(os.path.join(HERE, "build_skyyskills_%s.py" % VERSION), encoding="utf-8").read()
    G = {"json": json}
    exec(compile(gen_block(src, "# >>> MANA GEN", "# <<< MANA GEN"), "MANA GEN", "exec"), G)
    gen = G["mana_gen"]
    z = zipfile.ZipFile(ASSETS)
    v07 = json.loads(z.read(MANA_PATH).decode("utf-8-sig"))
    new, ch = gen(v07, 6, 0.2)
    jz = zipfile.ZipFile(JAR)
    shipped = json.loads(jz.read(MANA_PATH).decode("utf-8")) if MANA_PATH in jz.namelist() else None
    check(shipped is not None and shipped == new and list(shipped) == list(v07),
          "M0: the jar's Mana.json = MANA GEN on Assets.zip's 0.7 file (key order kept): %s" % ch)
    fl = [r for r in new["Regenerating"] if r["RegenType"] == "Additive"]
    check(new["InitialValue"] == 0 and new["Max"] == 0 and new["Min"] == v07["Min"] and len(fl) == 1 and fl[0]["Interval"] == 0.2
          and fl[0]["Amount"] == 1 and {"Id": "NoDamageTaken", "Delay": 6} in fl[0]["Conditions"]
          and [r for r in new["Regenerating"] if r["RegenType"] != "Additive"] == [r for r in v07["Regenerating"] if r["RegenType"] != "Additive"],
          "M0: 0.7 -> Max / InitialValue 0, flat +1 every 0.2 s with NoDamageTaken 6 s, the Creative entry untouched: %s" % json.dumps(new["Regenerating"]))
    v06 = {"InitialValue": 0, "Min": 0, "Max": 0, "Shared": False, "ResetType": "MaxValue",
           "Regenerating": [{"Interval": 0.2, "Amount": 1, "RegenType": "Additive",
                             "Conditions": [{"Id": "Alive"}, {"Id": "NoDamageTaken", "Delay": 6}, {"Id": "Charging", "Inverse": True}]}]}
    n6, c6 = gen(v06, 6, 0.2)
    pre4 = json.loads(json.dumps(v06))
    pre4["InitialValue"] = pre4["Max"] = 100
    n4, c4 = gen(pre4, 6, 0.2)
    check(n6 is None and c6 == [] and n4 is not None and n4["Max"] == 0 and n4["Regenerating"] == v06["Regenerating"] and len(c4) == 2,
          "M0: 0.6's file -> no override; 0.7-pre.4's (Max 100, 0.6 regen) -> only InitialValue / Max change: %s" % c4)
    bad = []
    for name, mut in (("two flat entries", lambda d: d["Regenerating"].append(dict(d["Regenerating"][0]))),
                      ("Amount 2", lambda d: d["Regenerating"][0].update(Amount=2)),
                      ("unknown condition", lambda d: d["Regenerating"][0]["Conditions"].append({"Id": "Wielding"})),
                      ("Min -1", lambda d: d.update(Min=-1)),
                      ("inverse NoDamageTaken", lambda d: d["Regenerating"][0]["Conditions"].append({"Id": "NoDamageTaken", "Inverse": True})),
                      ("no Alive", lambda d: d["Regenerating"][0].update(Conditions=[])),
                      ("Max text", lambda d: d.update(Max="100"))):
        d = json.loads(json.dumps(v07))
        mut(d)
        try:
            gen(d, 6, 0.2)
            bad.append(name)
        except SystemExit:
            pass
    check(bad == [], "M0: MANA GEN stops the build on every shape it does not know (none slipped through: %s)" % bad)
    # ---- S0: SPELL GEN's 0.7 rule (a drain-only item) on synthetic items + the real gate simulation on the jar's files over Assets.zip
    exec(compile(gen_block(src, "# >>> SPELL GEN", "# <<< SPELL GEN"), "SPELL GEN", "exec"), G)
    vstaff = {"Interactions": {"Primary": "Staff_Primary"}, "InteractionVars": {
        "Staff_Cast_Summon_Cost": {"Interactions": [{"Parent": "Staff_Cast_Cost", "StatModifiers": {"Mana": -50}}]}}}
    dead = json.loads(json.dumps(vstaff))
    dead["InteractionVars"]["Staff_Cast_Summon_Charged"] = {"Interactions": [{"Parent": "Staff_Cast_Summon_Charged", "Costs": {"Mana": 50}}]}
    plan, inh, unch = G["spell_plan"]({"S07": ("Server/Item/Items/W/S07.json", vstaff), "S06": ("Server/Item/Items/W/S06.json", dead)}, 5)
    pm = dict((p[0], p) for p in plan)
    check(sorted(pm) == ["S06", "S07"] and [(e[1], e[2], e[3]) for e in pm["S07"][2]] == [("StatModifiers", -50, -10)]
          and sorted((e[1], e[2], e[3]) for e in pm["S06"][2]) == [("Costs", 50, 10), ("StatModifiers", -50, -10)]
          and pm["S07"][3]["InteractionVars"]["Staff_Cast_Summon_Cost"]["Interactions"][0]["StatModifiers"]["Mana"] == -10,
          "S0: a 0.7 staff (drain var only) is planned (drain 50 -> 10), a 0.6 staff (dead check var + drain) still is: %s" % sorted(pm))
    refused = []
    for name, it in (("two cast check vars", {"InteractionVars": dict(dead["InteractionVars"], X={"Interactions": [{"Parent": "Wand_Cast_Left_Charged", "Costs": {"Mana": 25}}]})}),
                     ("cast check var only", {"InteractionVars": {"Staff_Cast_Summon_Charged": dead["InteractionVars"]["Staff_Cast_Summon_Charged"]}}),
                     ("two drains", {"InteractionVars": dict(vstaff["InteractionVars"], Y={"Interactions": [{"Parent": "Wand_Cast_Cost", "StatModifiers": {"Mana": -25}}]})})):
        try:
            G["spell_plan"]({"Z": ("Server/Item/Items/W/Z.json", it)}, 5)
            refused.append(name)
        except SystemExit:
            pass
    check(refused == [], "S0: still refused - two cast check vars, a check var without a drain, two drains (slipped: %s)" % refused)
    # the real gate simulation: Assets.zip 0.7 with the jar's item + interaction files laid over it
    items, ints, roots = {}, {}, {}
    for n in z.namelist():
        if n.endswith(".json") and n.startswith(("Server/Item/Items/", "Server/Item/Interactions/", "Server/Item/RootInteractions/")):
            k = os.path.basename(n)[:-5]
            tgt = items if n.startswith("Server/Item/Items/") else (ints if n.startswith("Server/Item/Interactions/") else roots)
            tgt[k] = (n, json.loads(z.read(n).decode("utf-8-sig")))
    new_items, new_ints = dict((k, v[1]) for k, v in items.items()), dict((k, v[1]) for k, v in ints.items())
    over_i, over_n = 0, 0
    for n in jz.namelist():
        if n.startswith("Server/Item/Items/") and n.endswith(".json"):
            new_items[os.path.basename(n)[:-5]] = json.loads(jz.read(n).decode("utf-8"))
            over_i += 1
        elif n.startswith("Server/Item/Interactions/") and n.endswith(".json") and os.path.basename(n)[:-5] in ints:
            new_ints[os.path.basename(n)[:-5]] = json.loads(jz.read(n).decode("utf-8"))
            over_n += 1
    for owned in ("Weapon_Staff_Wood", "Weapon_Staff_Copper", "Weapon_Staff_Iron", "Weapon_Staff_Thorium", "Weapon_Staff_Cobalt",
                  "Weapon_Staff_Adamantite", "Weapon_Staff_Mithril", "Weapon_Staff_Onyxium", "Weapon_Staff_Bo_Bamboo", "Weapon_Staff_Bo_Wood"):
        new_items.pop(owned, None)   # SkyyArmory's (its own files; the build checks them against its pinned jar)
    old_items = dict((k, v[1]) for k, v in items.items() if k in new_items)
    rows = G["spell_verify"](old_items, new_items, dict((k, v[1]) for k, v in ints.items()), new_ints,
                             dict((k, v[1]) for k, v in roots.items()), 5)
    fam = {}
    for r in rows:
        fam.setdefault((r[1], r[3], r[5]), []).append(r[0])
    S = {"rows": rows, "fam": dict(("%s check %d spend %d" % k, len(v)) for k, v in fam.items()), "over_items": over_i, "over_ints": over_n}
    want = {("Wand_Cast_Left_Charged", 5, 5), ("Spellbook_Cast_Hurl_Charged", 20, 20), ("Staff_Cast_Summon_Charged", 10, 10),
            ("Staff_Cast_Summon_Charged", 10, 0), ("Gun_Shoot_Flintlock_Charged", 10, 10), ("Gun_Shoot_Flintlock_Charged", 10, 0)}
    sm = dict((r[0], r) for r in rows)
    check(set(fam) == want and sm["Weapon_Wand_Wood"][3:] == (5, 25, 5) and sm["Halloween_Broomstick"][1:] == ("Staff_Cast_Summon_Charged", 0, 10, 50, 10)
          and all(sm[i][3] == 10 and sm[i][5] == 10 for i in ("Weapon_Staff_Bone", "Weapon_Staff_Wizard", "Weapon_Staff_Frost", "Weapon_Staff_Voidcrystal"))
          and all(sm[i][3] == 20 for i in ("Weapon_Spellbook_Fire", "Weapon_Spellbook_Frost", "Weapon_Spellbook_Demon")),
          "S1: gate simulation (engine rules) on Assets.zip 0.7 + the jar's %d item / %d interaction files: every paid cast checks what it "
          "spends - wand 5, staff 10 (Broomstick: no check in vanilla -> 10), spellbook 20, blunderbuss 10: %s" % (over_i, over_n, S["fam"]))
    # the same simulation on the vanilla 0.7 files alone = the control: the staffs spend 50 with NO check (free casts at 0 Mana)
    ctrl = G["spell_casts"](G["_spell_eff_item"](dict((k, v[1]) for k, v in items.items()), "Weapon_Staff_Bone", 0),
                            dict((k, v[1]) for k, v in ints.items()), dict((k, v[1]) for k, v in roots.items()))
    check(ctrl["free"] and not ctrl["casts"] and ctrl["free"][0][0] == -50,
          "S1 control: vanilla 0.7 Weapon_Staff_Bone spends 50 Mana with no check before it (a free cast at 0 Mana): %s" % ctrl["free"][:1])
    # ---- O0 / O1 (fixer round): ONHIT GEN on the 0.7 files + synthetic ones; the Mana consumer scan; control = the 0.4.30 jar
    exec(compile(gen_block(src, "# >>> ONHIT GEN", "# <<< ONHIT GEN"), "ONHIT GEN", "exec"), G)
    named, osrc = [], {}
    for n in z.namelist():
        if n.startswith("Server/") and n.endswith(".json"):
            t = z.read(n).decode("utf-8-sig", "replace")
            if '"Mana"' in t:
                named.append(n)
                if '"EntityStatsOnHit"' in t:
                    j = json.loads(t)
                    if G["_onhit_walk"](j, "", []):
                        osrc[n] = j
    oplan = G["onhit_plan"](osrc, 5)
    got = dict((p.rsplit("/", 1)[-1][:-5], [(c[1], c[2]) for c in ch]) for p, nj, ch in oplan)
    want_on = {"Weapon_Mace_Signature_Groundslam_Damage": [(25, 5)], "Weapon_Crossbow_Damage_Signature_Projectile": [(50, 10)],
               "Weapon_Shortbow_Signature_Volley_Damage": [(20, 4)], "Weapon_Daggers_Signature_Razorstrike_Lunge_Damage": [(15, 3)],
               "Weapon_Daggers_Signature_Razorstrike_Slash_Damage": [(5, 1)], "Weapon_Daggers_Signature_Razorstrike_Sweep_Damage": [(5, 1)],
               "Weapon_Sword_Signature_Vortexstrike_Stab_Damage": [(15, 3)], "Weapon_Sword_Signature_Vortexstrike_Spin_Damage": [(5, 1)],
               "Weapon_Battleaxe_Signature_Whirlwind_Damage": [(4, 1)]}
    check(got == want_on, "O0: ONHIT GEN on Assets.zip 0.7: the 9 signature Mana-on-hit Amounts / 5 (25->5, 50->10, 20->4, 15->3, 5->1, 4->1): %s" % got)
    jn = set(jz.namelist())
    shipped_ok = all(p in jn and json.loads(jz.read(p).decode("utf-8")) == nj for p, nj, ch in oplan)
    only_amount = True
    for p, nj, ch in oplan:
        a, b = json.loads(json.dumps(osrc[p])), json.loads(json.dumps(nj))
        for (w, e1), (w2, e2) in zip(G["_onhit_walk"](a, "", []), G["_onhit_walk"](b, "", [])):
            e1["Amount"] = e2["Amount"] = 0
            only_amount = only_amount and e1.get("MultipliersPerEntitiesHit") == e2.get("MultipliersPerEntitiesHit")
        only_amount = only_amount and a == b
    check(shipped_ok and only_amount, "O0: the jar ships exactly those 9 files, each = vanilla 0.7 but the Mana Amount (multipliers per target kept)")
    pj = zipfile.ZipFile(PREV_JAR)
    check(not [p for p, nj, ch in oplan if p in pj.namelist()],
          "O0 control: the 0.4.30 jar ships none of them - on 0.7 one Groundslam hit gives 25 Mana (a no-class 25 pool full), a crossbow signature bolt 50")
    syn = {"Type": "DamageEntity", "DamageCalculator": {"EntityStatsOnHit": [{"EntityStatId": "SignatureEnergy", "Amount": 2},
                                                                            {"EntityStatId": "Mana", "Amount": 12, "MultipliersPerEntitiesHit": [1, 0.5]}]}}
    sp = G["onhit_plan"]({"Server/Item/Interactions/X/Syn.json": syn}, 5)
    check(len(sp) == 1 and sp[0][1]["DamageCalculator"]["EntityStatsOnHit"][1]["Amount"] == 2
          and sp[0][1]["DamageCalculator"]["EntityStatsOnHit"][0] == {"EntityStatId": "SignatureEnergy", "Amount": 2}
          and G["onhit_plan"]({"Server/Item/Interactions/X/S0.json": {"EntityStatsOnHit": [{"EntityStatId": "SignatureEnergy", "Amount": 2}]}}, 5) == [],
          "O0: synthetic - only the Mana entry changes (12 -> 2), a SignatureEnergy entry / a file without Mana is left alone")
    slipped = []
    for name, ent in (("AmountType", {"EntityStatId": "Mana", "Amount": 10, "AmountType": "Percentage"}),
                      ("no Amount", {"EntityStatId": "Mana"}), ("text Amount", {"EntityStatId": "Mana", "Amount": "10"})):
        try:
            G["onhit_plan"]({"Server/Item/Interactions/X/B.json": {"EntityStatsOnHit": [ent]}}, 5)
            slipped.append(name)
        except SystemExit:
            pass
    check(slipped == [], "O0: ONHIT GEN stops the build on a Mana on-hit entry it does not know (slipped: %s)" % slipped)
    owned = ["Weapon_Staff_Wood", "Weapon_Staff_Copper", "Weapon_Staff_Iron", "Weapon_Staff_Thorium", "Weapon_Staff_Cobalt", "Weapon_Staff_Adamantite",
             "Weapon_Staff_Mithril", "Weapon_Staff_Onyxium", "Weapon_Staff_Bo_Bamboo", "Weapon_Staff_Bo_Wood"]
    cov = G["mana_consumers"](named, set(n for n in jn if n.startswith("Server/")), set(owned), set(["Weapon_Staff_Crystal_Red", "Weapon_Staff_Crystal_Ice"]))
    cov_prev = G["mana_consumers"](named, set(n for n in pj.namelist() if n.startswith("Server/")), set(owned), set(["Weapon_Staff_Crystal_Red", "Weapon_Staff_Crystal_Ice"]))
    check(cov["NOT COVERED"] == [] and len(cov["vanilla runes (not scaled)"]) == 7 and len(cov["overridden by this jar"]) == 40,
          "O1: Mana consumer scan on Assets.zip 0.7 + this jar: %s" % dict((k, len(v)) for k, v in cov.items()))
    nc = sorted(n.rsplit("/", 1)[-1][:-5] for n in cov_prev["NOT COVERED"])
    check(nc == sorted(list(want_on) + ["Weapon_Staff_Scrap_Lightbulb", "Weapon_Staff_Voidcrystal"]),
          "O1 control: with the 0.4.30 jar's files the scan flags the 9 signature Mana-on-hit files + 0.7's 2 new staffs as NOT COVERED: %s" % nc)
    # ---- O2 (fixer 2, critic: SkyyArmory's Wynn crossbows inherit the crossbow signature file): onhit_inheritors on the live-set Armory jar
    with open(os.path.join(os.path.dirname(HERE), "tools", "deploy_set.py"), encoding="utf-8") as df:
        apin = re.search(r'\("SkyyArmory", "([0-9][0-9.]*)"\)', df.read()).group(1)
    with zipfile.ZipFile(os.path.join(os.path.dirname(HERE), "SkyyArmory", "SkyyArmory-%s.jar" % apin)) as az:
        atx = dict((n, az.read(n).decode("utf-8-sig", "replace")) for n in az.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    ids = [p.rsplit("/", 1)[-1][:-5] for p, nj, ch in oplan]
    inh = G["onhit_inheritors"](atx, ids)
    want_inh = [("Weapon_Crossbow_Copper_Wynn", "Weapon_Crossbow_Damage_Signature_Projectile"),
                ("Weapon_Crossbow_Onyxium_Wynn", "Weapon_Crossbow_Damage_Signature_Projectile")]
    check(inh == want_inh, "O2: the build's inherit NOTE finds SkyyArmory %s's 2 Wynn crossbows (Big Arrow Parent = the crossbow signature file -> +10 Mana a hit): %s" % (apin, inh))
    syn_t = {"Server/Item/Items/A.json": json.dumps({"InteractionVars": {"X": {"Interactions": [{"Parent": "Weapon_Crossbow_Damage_Signature_Projectile"}]}}}),
             "Server/Item/Items/B.json": json.dumps({"InteractionVars": {"X": {"Interactions": [{"Parent": "Weapon_Crossbow_Damage_Charged"}]}}}),
             "Server/Item/Interactions/C.json": json.dumps({"Parent": "Weapon_Crossbow_Damage_Signature_Projectile"})}
    check(G["onhit_inheritors"](syn_t, ids) == [("A", "Weapon_Crossbow_Damage_Signature_Projectile")],
          "O2: synthetic - a nested Parent naming an on-hit file is found; another Parent and non-item files are ignored")
    S["onhit"] = got
    return S


# ============================================================================================ parent
def child(env, log, *a):
    with open(log, "wb") as lf:
        p = subprocess.run([sys.executable, os.path.abspath(__file__)] + list(a) + ["--dir", SCRATCH], env=env, stdout=lf, stderr=subprocess.STDOUT)
    return p.returncode


PROG = re.compile(r"^\+([\d,.]+k?) Acrobatics XP \(([\d,.]+k?)/([\d,.]+k?)\)$")
NEXT = re.compile(r"next: Acrobatics \d+ at ([\d,.]+k?)/([\d,.]+k?) XP")


def award_catch_types(jar):
    """the exception-table catch types of Acro.award(...) in the jar (plain class-file parse, no JVM)"""
    import struct
    b = zipfile.ZipFile(jar).read(PKG.replace(".", "/") + "Acro.class")
    pos = [10]
    cnt = struct.unpack(">H", b[8:10])[0]
    cp = [None] * cnt

    def u1():
        pos[0] += 1
        return b[pos[0] - 1]

    def u2():
        pos[0] += 2
        return struct.unpack(">H", b[pos[0] - 2:pos[0]])[0]

    def u4():
        pos[0] += 4
        return struct.unpack(">I", b[pos[0] - 4:pos[0]])[0]
    i = 1
    while i < cnt:
        t = u1()
        if t == 1:
            n = u2()
            cp[i] = ("utf8", b[pos[0]:pos[0] + n].decode("utf8", "replace"))
            pos[0] += n
        elif t in (7, 8, 16, 19, 20):
            cp[i] = ("ref", u2())
        elif t in (3, 4):
            pos[0] += 4
        elif t in (5, 6):
            pos[0] += 8
            i += 1
        elif t in (9, 10, 11, 12, 17, 18):
            pos[0] += 4
        elif t == 15:
            pos[0] += 3
        else:
            raise ValueError("constant pool tag %d" % t)
        i += 1
    u2()
    u2()
    u2()
    n_ = 2 * u2(); pos[0] += n_
    for _f in range(u2()):
        u2()
        u2()
        u2()
        for _a in range(u2()):
            u2()
            n_ = u4(); pos[0] += n_
    out = None
    for _m in range(u2()):
        u2()
        name = cp[u2()][1]
        u2()
        for _a in range(u2()):
            an = cp[u2()][1]
            ln = u4()
            start = pos[0]
            if an == "Code" and name == "award":
                u2()
                u2()
                n_ = u4(); pos[0] += n_
                out = []
                for _e in range(u2()):
                    u2()
                    u2()
                    u2()
                    ct = u2()
                    out.append("any" if ct == 0 else cp[cp[ct][1]][1])
            pos[0] = start + ln
    return out


def num(x):
    x = x.replace(",", "")
    return int(round(float(x[:-1]) * 1000)) if x.endswith("k") else int(x)


def main():
    if "--mkfake" in sys.argv:
        return t15().run_mkfake(arg("--mkfake"))
    if "--h" in sys.argv:
        return run_h(arg("--h"), arg("--fake"), arg("--home"), arg("--out"), arg("--new") == "1")
    if "--cc" in sys.argv:
        t27 = tmod("test_skyyskills_0.4.27.py", "t0427")
        return t27.run_cc(arg("--cc"), arg("--prev-jar"), arg("--out"), arg("--repl"))
    if "--start" in sys.argv:
        t25 = tmod("test_skyyskills_0.4.25.py", "t0425")
        t25.SCRATCH = arg("--start-dir")
        return t25.run_start(arg("--start"), arg("--out"), "new")
    if "--audit" in sys.argv:
        return t15().run_audit(arg("--audit"), arg("--fake"), arg("--out"))
    if "--m" in sys.argv:
        return run_m(arg("--m"), arg("--fake"), arg("--home"), arg("--out"))
    for j in (JAR, PREV_JAR):
        if not os.path.isfile(j):
            sys.exit("no jar at %s - build it first" % j)
    scratch_root = os.path.join(TOOLS, "dev", "scratch").replace("\\", "/").lower().rstrip("/")
    here = SCRATCH.replace("\\", "/").lower().rstrip("/")
    if here == scratch_root or not here.startswith(scratch_root + "/"):
        sys.exit("--dir must be a folder INSIDE tools/dev/scratch/, not %s" % SCRATCH)
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.makedirs(env["TEMP"], exist_ok=True)
    live0 = snap(LIVE_DIR)
    fake = os.path.join(SCRATCH, "fake")
    check(child(env, os.path.join(SCRATCH, "mkfake.log"), "--mkfake", fake) == 0, "stand-in classes generated")
    # ---------------------------------------------------------------- H (new jar) and the control (0.4.30)
    res = {}
    for tag, jar in (("new", JAR), ("prev", PREV_JAR)):
        home = os.path.join(SCRATCH, "home-" + tag)
        shutil.copytree(LIVE_DIR, home)
        out = os.path.join(SCRATCH, "h-%s.json" % tag)
        log = os.path.join(SCRATCH, "h-%s.log" % tag)
        rc = child(env, log, "--h", jar, "--fake", fake, "--home", home, "--out", out, "--new", "1" if tag == "new" else "0")
        check(rc == 0 and os.path.isfile(out), "H %s: child JVM ran (log %s)" % (tag, log))
        res[tag] = json.load(open(out)) if os.path.isfile(out) else {"D": {"error": "no output"}}
    N = res["new"]
    check(not N.get("load_fails") and N.get("loaded") == N.get("classes"), "A: %s / %s classes load + verify + initialise under -Xverify:all %s"
          % (N.get("loaded"), N.get("classes"), (N.get("load_fails") or [])[:3]))
    D, C = N["D"], res["prev"]["D"]
    check("error" not in D and "error" not in C, "H ran: %s | %s" % (D.get("error"), C.get("error")))
    if "error" in D or "error" in C:
        return finish()
    print("H. multiplier x%s/1000, acro.feedbackMs %s, acro.maxXpPerMinute %s, level 11 at %s XP (needs %s for 12)"
          % (D["mult"], D["acro_feedback_ms"], D["acro_max_per_min"], D["T11"], D["need11"]))

    def consistent(texts):
        """after a 'next: at p/M' line, the next '+N Acrobatics XP (a/M)' line must have p + N == a; returns (ok, pairs)"""
        pairs, last = [], None
        for t in texts:
            m = NEXT.search(t)
            if m:
                last = num(m.group(1))
                continue
            m = PROG.match(t)
            if m and last is not None:
                pairs.append((last, num(m.group(1)), num(m.group(2))))
                last = num(m.group(2))
        return all(p + n == a for p, n, a in pairs) and len(pairs) > 0, pairs

    for tag in ("H1", "H2", "H3", "H4", "H5", "H6"):
        print("  %s new : %s" % (tag, D[tag]["texts"]))
        print("  %s 0.4.30: %s" % (tag, C[tag]["texts"]))
    # H1
    a, b = D["H1"], C["H1"]
    check([r["total"] for r in a["rec"]] == [r["total"] for r in b["rec"]] and a["rec"][-1]["lv"] == 11 and b["rec"][-1]["lv"] == 11,
          "H1: both jars store the same XP and reach level 11: %s / %s" % ([r["total"] for r in a["rec"]], [r["total"] for r in b["rec"]]))
    okb, pb = consistent(b["texts"])
    check(not okb and pb, "H1 control 0.4.30 REPRODUCES the bug: the 30 s line after the level-up does not add up from 'next: at': %s" % pb)
    oka, pa = consistent(a["texts"])
    check(oka, "H1 0.4.31: every '+N Acrobatics XP' line after the level-up adds up from 'next: at': %s" % pa)
    ia = [i for i, t in enumerate(a["texts"]) if "SKILL LEVEL UP" in t]
    pre = [t for t in a["texts"][:ia[0]] if PROG.match(t)] if ia else []
    shown = sum(num(PROG.match(t).group(1)) for t in a["texts"] if PROG.match(t))
    paid = a["rec"][-1]["total"] - a["start"]
    check(len(ia) == 1 and len(pre) == 1 and num(PROG.match(pre[0]).group(2)) == a["rec"][1]["total"] - D["T11"],
          "H1 0.4.31: one '+N Acrobatics XP' line BEFORE 'SKILL LEVEL UP' showing the post-level progress: %s" % a["texts"])
    check(shown == paid, "H1 0.4.31: the lines add up to the XP paid (%d shown, %d paid) - nothing lost, nothing shown twice" % (shown, paid))
    check(a["rec"][1]["s21"] == 0.0 and a["rec"][1]["s22"] == 2000.0 and not any(r["staged"] for r in a["rec"]) and all(r["err"] is None for r in a["rec"]),
          "H1 0.4.31: the counter restarts at the level-up second, no stage left: %s" % a["rec"])
    # H2
    a, b = D["H2"], C["H2"]
    check(a["texts"] == b["texts"] and [(r["total"], r["s21"], r["s22"]) for r in a["rec"]] == [(r["total"], r["s21"], r["s22"]) for r in b["rec"]]
          and len(a["texts"]) == 1 and not any(r["staged"] for r in a["rec"]),
          "H2 no level-up: 0.4.31 = 0.4.30 exactly (one 30 s line, same counter): %s / %s" % (a["texts"], b["texts"]))
    # H3
    a = D["H3"]
    check(not any(PROG.match(t) for t in a["all"]) and any("SKILL LEVEL UP  Acrobatics" in t for t in a["all"]) and not a["stage_after"]
          and not any(r["staged"] for r in a["rec"]) and a["rec"][1]["s21"] > 0,
          "H3 xpGain off: no '+N' line, nothing staged, level-up still told, counter untouched: %s %s" % (a["all"], a["rec"]))
    # H4
    a, b = D["H4"], C["H4"]
    ia = [i for i, t in enumerate(a["texts"]) if "SKILL LEVEL UP" in t]
    pre = [t for t in a["texts"][:ia[0]] if PROG.match(t)] if ia else []
    mv = a["rec"][0]["total"] - a["start"]
    fall = a["rec"][1]["total"] - a["rec"][0]["total"]
    check(len(ia) == 1 and len(pre) == 1 and num(PROG.match(pre[0]).group(1)) == mv + fall and a["rec"][1]["s21"] == 0.0 and a["rec"][1]["lv"] == 11,
          "H4 fall level-up: movement %d + fall %d shown in one line before SKILL LEVEL UP, counter restarted: %s %s" % (mv, fall, a["texts"], a["rec"]))
    oka, pa = consistent(a["texts"])
    check(oka and [r["total"] for r in a["rec"]] == [r["total"] for r in b["rec"]], "H4: the line after adds up %s; same XP as 0.4.30" % pa)
    # H5
    a, b = D["H5"], C["H5"]
    check(a["rec"][1]["err"] is not None and b["rec"][1]["err"] is not None and not a["stage_after"] and a["stage_size"] == 0
          and a["rec"][1]["total"] == b["rec"][1]["total"],
          "H5 throwing award: the exception leaves as in 0.4.30, no stage outlives it, XP stored: %s" % a["rec"])
    # H5 counter (fixer): the stage the level-up line took -> the counter restarted; otherwise 0.4.30's counter
    a, b = D["H5"], C["H5"]
    check(a["rec"][1]["s21"] in (0.0, b["rec"][1]["s21"]) and a["rec"][0]["s21"] == b["rec"][0]["s21"],
          "H5 throwing award: the counter after it is 0 (line taken) or 0.4.30's: %s / %s" % ([r["s21"] for r in a["rec"]], [r["s21"] for r in b["rec"]]))

    # ---------------------------------------------------------------- fixer round: H6 / H7 / TH (+ the pre-fix control)
    def fixer_checks(R, label, record):
        X, ok = R["D"], []
        a, b = X.get("H6"), C["H6"]
        r6 = (a is not None and a["rec"][1]["err"] is not None and b["rec"][1]["err"] is not None and a["rec"][1]["s21"] == b["rec"][1]["s21"]
              and not a["stage_after"] and a["stage_size"] == 0)
        ok.append(r6)
        r7 = X.get("H7") == {"gone_kept": False, "online_kept": True}
        ok.append(r7)
        ct = award_catch_types(R["jar"])
        rt = bool(ct) and all(c in ("java/lang/Throwable", "any") for c in ct)
        ok.append(rt)
        if record:
            check(r6, "H6 %s: an award that throws BEFORE paying leaves the counter at 0.4.30's (%s vs %s), no stage: %s"
                  % (label, a and a["rec"][1]["s21"], b["rec"][1]["s21"], a and a["rec"]))
            check(r7, "H7 %s: Acro.retainOnline drops a left player's stage, keeps the online one: %s" % (label, X.get("H7")))
            check(rt, "TH %s: Acro.award catches java/lang/Throwable: %s" % (label, ct))
        return ok
    N["jar"] = JAR
    fixer_checks(N, VERSION, True)
    if PRE_JAR:
        home = os.path.join(SCRATCH, "home-pre")
        shutil.copytree(LIVE_DIR, home)
        out = os.path.join(SCRATCH, "h-pre.json")
        rc = child(env, os.path.join(SCRATCH, "h-pre.log"), "--h", PRE_JAR, "--fake", fake, "--home", home, "--out", out, "--new", "1")
        P = json.load(open(out)) if rc == 0 and os.path.isfile(out) else {"D": {}}
        P["jar"] = PRE_JAR
        print("  H6 pre-fix: %s" % (P["D"].get("H6") or {}).get("rec"))
        pk = fixer_checks(P, "pre-fix", False)
        check(rc == 0 and pk == [False, False, False],
              "CONTROL pre-fix 0.4.31 REPRODUCES all three findings (H6 counter keeps unpaid XP, H7 no prune, TH RuntimeException only): %s" % pk)
    # ---------------------------------------------------------------- M (0.7 port): Mana override + spell costs
    S = m_python_checks()
    mres = {}
    for tag, jar in (("new", JAR), ("prev", PREV_JAR)):
        home = os.path.join(SCRATCH, "mhome-" + tag)
        shutil.copytree(LIVE_DIR, home)
        out = os.path.join(SCRATCH, "m-%s.json" % tag)
        rc = child(env, os.path.join(SCRATCH, "m-%s.log" % tag), "--m", jar, "--fake", fake, "--home", home, "--out", out)
        check(rc == 0 and os.path.isfile(out), "M %s: child JVM ran" % tag)
        mres[tag] = json.load(open(out)) if os.path.isfile(out) else {"error": "no output"}
    M, MC = mres["new"], mres["prev"]
    check("error" not in M and "error" not in MC, "M ran: %s | %s" % (M.get("error"), MC.get("error")))
    if "error" in M or "error" in MC:
        return finish()
    print("M. engine-decoded Mana stat (0.4.31 ships it: %s): %s" % (M["shipped"], json.dumps(M["stat"])))
    print("   0.4.31: out %s | in %s" % (json.dumps(M["phase"]["out"]), json.dumps(M["phase"]["in"])))
    print("   0.4.30 on 0.7 (control): stat %s | out %s | in %s" % (json.dumps(MC["stat"]), json.dumps(MC["phase"]["out"]), json.dumps(MC["phase"]["in"])))
    print("   base Mana 0.4.31 %s | 0.4.30 on 0.7 %s" % (json.dumps(M["base"]), json.dumps(MC["base"])))
    st = M["stat"]
    check(M["shipped"] and st["initial"] == 0.0 and st["max"] == 0.0 and st["min"] == 0.0 and st["reset"] == "MaxValue"
          and st["regen"][0][:3] == [1.0, 0.2, "ADDITIVE"] and st["regen"][0][3] == ["AliveCondition", "NoDamageTakenCondition"],
          "M1: the engine's own EntityStatType.CODEC decodes the shipped Mana.json: Max / Initial 0, +1 every 0.2 s if Alive + NoDamageTaken")
    o, i = M["phase"]["out"], M["phase"]["in"]
    check(o["states"] == [0] and o["vanilla_per_s"] == 5.0 and o["skyy_per_s"] == 0.0 and o["total_per_s"] == 5.0 and o["combat_left_ms"] == 0,
          "M2 out of combat: the engine refills 5 Mana a second, SkyySkills adds nothing (no boosts), not in combat: %s" % o)
    check(i["states"] == [1] and i["vanilla_per_s"] == 0.0 and i["skyy_per_s"] == 3.75 and i["total_per_s"] == 3.75 and 4990 <= i["combat_left_ms"] <= 5000,
          "M2 in combat (hit 1 s ago): the engine's refill pauses, SkyySkills refills 75%% of 5 = 3.75 a second, %d ms of combat left: %s"
          % (i["combat_left_ms"], i))
    co, ci = MC["phase"]["out"], MC["phase"]["in"]
    check(not MC["shipped"] and MC["stat"]["max"] == 100.0 and co["total_per_s"] == ci["total_per_s"] and ci["states"] == [0] and ci["combat_left_ms"] == 0,
          "M2 control (0.4.30 on the 0.7 assets): Max 100, the same %s a second in and out of combat, never in combat (no 75%% rule, combat HUD dead)"
          % ci["total_per_s"])
    B4, B3 = M["base"], MC["base"]
    check(B4["none"]["max"] == 25.0 and B4["Mage"]["max"] == 45.0 and B4["Priest"]["max"] == 42.0 and B4["Warrior"]["max"] == B4["Warrior"]["target"]
          and all(v["modifier"] == v["target"] for v in B4.values()),
          "M3: Base Mana is the class table again (none 25, Mage 45, Priest 42, Warrior %s): %s" % (B4["Warrior"]["target"], B4))
    check(all(v["max"] == 100.0 and v["modifier"] == 0.0 for v in B3.values()),
          "M3 control (0.4.30 on 0.7): every class has 100 max Mana, the Base Mana table does nothing: %s" % B3)
    jg = M["gates"]
    pyg = dict((r[0], [r[1], r[2], r[3], r[4], r[5]]) for r in S["rows"])
    check(jg == pyg and len(jg) == 26 and len(M["ints"]) == 8 and all(v == [10, 50] for v in M["arm"].values()) and len(M["arm"]) == 8,
          "M4: ManaCost (the Java's gate table) = the gate simulation on the 0.7 assets + the jar's files: %d casters, 8 interactions, 8 "
          "SkyyArmory staffs (fallback check 10 / spend 50)" % len(jg))
    check(M["ints"].get("Staff_Cast_Summon_Charged") == ["check+", -1, 10] and M["ints"].get("Wand_Cast_Left_Charged") == ["check", 25, 5]
          and M["ints"].get("Spellbook_Cast_Hurl_Charged") == ["check", 25, 20], "M4: the charged cast checks staff none -> 10, wand 25 -> 5, spellbook 25 -> 20: %s" % M["ints"])
    # ---------------------------------------------------------------- MG (fixer round): the live Mana stat check
    mg = M.get("mg") or {}
    print("MG. ManaGuard live Mana check: %s" % json.dumps(mg)[:1200])
    sh, v7 = mg.get("shipped") or {}, mg.get("vanilla07") or {}
    check(mg.get("exp") == [0.0, 5.0, True, True] and sh.get("facts") == [0.0, 0.0, 5.0, 1.0] and (sh.get("report") or [""])[0] == "info"
          and "active" in sh["report"][1], "MG: the jar's own Mana.json, engine-decoded -> facts max 0 / refill 5 a second / combat pause -> INFO: %s" % sh.get("report"))
    vr = (v7.get("report") or ["", ""])
    check(v7.get("facts") == [100.0, 100.0, 3.3333, 0.0] and vr[0] == "warn" and "max 100 instead of 0" in vr[1]
          and "refill 3.333 a second instead of 5" in vr[1] and "no combat pause" in vr[1] and "Skyy:test" in vr[1],
          "MG: vanilla 0.7's Mana.json in effect (another mod's file won) -> ONE WARN naming max 100, refill 3.333, no combat pause, the pack: %s" % vr[1])
    check(mg.get("none", [None])[0] == "" and mg.get("check", ["THREW"])[0] in ("", "info", "warn"),
          "MG: unreadable stat -> try again (\"\"); manaCheck() runs without throwing in a bare JVM: %s" % mg.get("check"))
    # ---------------------------------------------------------------- CC
    out = os.path.join(SCRATCH, "cc.json")
    repl = json.dumps({"versions": [VERSION, PREV_VERSION], "rules": []})
    check(child(env, os.path.join(SCRATCH, "cc.log"), "--cc", JAR, "--prev-jar", PREV_JAR, "--out", out, "--repl", repl) == 0, "CC child ran")
    CC = json.load(open(out))
    ch = CC["classes"]
    struct = dict((c, v["structural"]) for c, v in ch.items() if v["structural"] or v["fields_new"] or v["fields_gone"])
    check(CC["added"] == [] and CC["gone"] == [], "CC: no class added / removed: %s %s" % (CC["added"], CC["gone"]))
    want_msg = sorted(["<clinit>", "stage(Ljava/util/UUID;IJ)V (new)", "unstage(Ljava/util/UUID;)Z (new)", "take(Ljava/util/UUID;)Ljava/lang/String;"])
    want_acro = sorted(["award(Lcom/hypixel/hytale/server/core/universe/PlayerRef;[DDJZ)V (new)", "flush(Lcom/hypixel/hytale/server/core/universe/PlayerRef;[DJ)V",
                        "retainOnline()V"])   # fixer round: + the STAGE prune
    got_msg = sorted(struct.get("SkillMsg", []))
    # 0.7 port (skills07): + what building on the Hytale 0.7.0 assets / server jar changes with no source change - ManaCost <clinit> (the
    # 0.7 gate table: 24 items / 26 casters), ManaGuard.packTick + SkyySkillsPlugin.setup (those counts in texts, the version line),
    # FellDefs <clinit> (0.7's wood / leaf ids) and FellRead.<init> / sec + SkillCfg.blockIdAt (javac-free recompile against 0.7:
    # World.getChunkStore() returns ChunkGrid, so getChunkSectionReferenceAtBlock / getStore resolve on ChunkGrid instead of ChunkStore)
    want_port = {"ManaCost": ["<clinit>"], "SkyySkillsPlugin": ["setup()V"], "FellDefs": ["<clinit>"],
                 "FellRead": sorted(["<init>(Lcom/hypixel/hytale/server/core/universe/world/World;I)V", "sec(III)[Ljava/lang/Object;"]),
                 "SkillCfg": ["blockIdAt(Lcom/hypixel/hytale/server/core/universe/world/World;III)Ljava/lang/String;"]}
    # fixer round: ManaGuard's live Mana stat check (manaFacts / manaReport / manaCheck + its fields; packTick runs it; <clinit> MANA_LAST)
    want_mg = sorted(["<clinit>", "packTick()V", "manaCheck()[Ljava/lang/String; (new)",
                      "manaFacts(Lcom/hypixel/hytale/server/core/modules/entitystats/asset/EntityStatType;)[F (new)",
                      "manaReport([FLjava/lang/String;)[Ljava/lang/String; (new)"])
    want_mgf = ["MANA_DONE:Z", "MANA_LAST:Ljava/lang/String;", "MANA_MAX:F", "MANA_PAUSE:Z", "MANA_PS:F", "MANA_SHIPPED:Z"]
    # the shared config kit's lock-free bridge (tools/skyycfg.py, another builder's change in the tree 2026-10-13: CfgRows.BRIDGE + bridge0)
    # is accepted only while the kit in the tree carries it - no SkyySkills source change
    kit_bridge = "BRIDGE_FIELD" in open(os.path.join(TOOLS, "skyycfg.py"), encoding="utf-8").read()
    want_kit = sorted(["bridge()Ljava/util/Map;", "bridge0()Ljava/util/Map; (new)"])
    kit_ok = ("CfgRows" not in struct) if not kit_bridge else (sorted(struct.get("CfgRows", [])) == want_kit
                                                                and ch["CfgRows"]["fields_new"] == ["BRIDGE:Ljava/util/Map;"])
    check(set(struct) - {"CfgRows"} == {"SkillMsg", "Acro", "ManaGuard"} | set(want_port) and got_msg == want_msg and sorted(struct["Acro"]) == want_acro
          and all(sorted(struct[c]) == want_port[c] and not ch[c]["fields_new"] and not ch[c]["fields_gone"] for c in want_port)
          and sorted(struct["ManaGuard"]) == want_mg and sorted(ch["ManaGuard"]["fields_new"]) == want_mgf and not ch["ManaGuard"]["fields_gone"]
          and kit_ok and ch["SkillMsg"]["fields_new"] == ["STAGE:Ljava/util/concurrent/ConcurrentHashMap;"] and not ch["Acro"]["fields_new"],
          "CC: only SkillMsg (STAGE, stage, unstage, take), Acro (award, flush, retainOnline), ManaGuard (+ the live Mana stat check) and the "
          "0.7 rebuild set (ManaCost, setup, FellDefs, FellRead, blockIdAt) differ%s: %s" % (
              " (+ the config kit's lock-free bridge in CfgRows)" if kit_bridge else "", json.dumps(struct)[:900]))
    print("CC. class compare: %s" % json.dumps(struct))
    # ---------------------------------------------------------------- ST
    st = {}
    for tag, jar in (("new", JAR), ("prev", PREV_JAR)):
        sd = os.path.join(SCRATCH, "st-" + tag)
        os.makedirs(sd)
        shutil.copytree(LIVE_DIR, os.path.join(sd, "live-copy-new"))
        out = os.path.join(SCRATCH, "st-%s.json" % tag)
        check(child(env, os.path.join(SCRATCH, "st-%s.log" % tag), "--start", jar, "--start-dir", sd, "--out", out) == 0, "ST %s child ran" % tag)
        st[tag] = json.load(open(out))
    a, b = st["new"], st["prev"]
    check("error" not in a and "error" not in b and not a["load_fails"], "ST ran: %s %s" % (a.get("error"), b.get("error")))
    check(a.get("changed1") == b.get("changed1") and a.get("changed2") == [] and b.get("changed2") == [] and a.get("players_same") and a.get("players", 0) > 0
          and a.get("xp1") == b.get("xp1"), "ST: start 1 changes what 0.4.30 changes %s, start 2 nothing, %s player files untouched"
          % (a.get("changed1"), a.get("players")))
    print("ST. start twice on a live copy: start 1 changed %s (= 0.4.30), start 2 nothing" % a.get("changed1"))
    # ---------------------------------------------------------------- AU
    auo = os.path.join(SCRATCH, "audit.json")
    check(child(env, os.path.join(SCRATCH, "audit.log"), "--audit", JAR, "--fake", fake, "--out", auo) == 0, "AU child ran")
    au = json.load(open(auo))
    check(au["refused"] == [] and au["control"] and au["refs"] > 1000, "AU: %d references, refused %s, control refused %s" % (au["refs"], au["refused"][:3], bool(au["control"])))
    print("AU. engine-access audit: %d references in %d classes, 0 refused (control refused)" % (au["refs"], au["classes"]))
    check(snap(LIVE_DIR) == live0, "the live Skyy_SkyySkills folder is byte-identical afterwards")
    return finish()


def finish():
    print("\n%d checks passed, %d failed" % (OKS[0], len(FAILS)))
    for f in FAILS:
        print("  FAIL", f)
    if not KEEP and not FAILS:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
