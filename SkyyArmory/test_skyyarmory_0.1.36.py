"""Harness for SkyyArmory 0.1.36 (the Priest wand launch x2 + its root cause, the Soul Orb one-handed; tools/armory_0_1_36_patch.py). Build first:
    python tools/armory_0_1_36_patch.py && python SkyyArmory/build_skyyarmory_0.1.36.py

    python SkyyArmory/test_skyyarmory_0.1.36.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.1.35 -> 0.1.36: exactly the planned members (EXPECT); non-class entries: manifest.json + the 16 Soul item files only
  H   physics  the launch distance tick by tick with the ENGINE's own numbers: the jar's TravMath (hopVector -> launchUp -> liftUp -> hopVy, the
               launch path) on 0.1.35 and 0.1.36, the jar's VelocityConfig (ArmoryTrav.dash = the vanilla dodge's), the engine's applied-velocity
               decay (MotionControllerBase.steer0: per tick resistance^(60 / tps), ground vs air, the Exp threshold blend - checked in the
               server jar's bytecode), gravity 32 (PhysicsConstants), 60 Hz. REPRO: a level launch at 18 stays on the ground and stops after ~4
               blocks; the same from a jump ~6 (Skyy: "four blocks", "8 if i walk backwards and jump" = + the walk). FIX: ~2x at every aim.
               The dodges: the vanilla Dodge_Left force 13 (Assets.zip) and SkyySkills' roll / lunge / flip pushes (the SET SkyySkills jar).
  X   exec     rows + loader (defaults 30 / 20 / 8, a file without hop.lift = 8, clamps), liftUp / hopVy table (the 0.1.20 damaging fall still
               kept), launchNow + ArmoryTrav.hop call liftUp BEFORE hopVy (bytecode), leapText; migrate036's text step (18 / 15 -> 30 / 20 +
               marker, hand values kept, CRLF kept, marker = never again, the 13 -> 30 -> 22 -> 18 -> 30 chain on an old file)
  S   soul     every Soul item in the jar: Utility Compatible (one-handed, = the vanilla Wood wand) + the right-click priority, the vanilla
               "Wand" animation set (exists in Assets.zip), Interactions identical to 0.1.35, nothing else changed; the 16 one-handed wands gain only
               the priority; HAND: the engine's hand choice (InteractionContext, SkyyMenu 0.3.40 T40's port) - empty / shield / torch off-hand:
               right-click stays ours (control: without the priority a shield takes it), left-click unchanged
  D   live     START TWICE on a scratch COPY of the live Skyy_SkyyArmory (every migration in setup's order + load): the 1st start changes exactly
               hop.force 18 -> 30, hop.maxUp 15 -> 20 + the marker (History copy + change-log lines), the 2nd start changes nothing
  AA  audit    the engine-access audit
Not executed here (UNVERIFIED until the game): the client's own movement (it runs the player physics; the model is the server's NPC copy of
the same split-velocity decay), the walk input on top, the exact feel of the 8 b/s lift.
Exit code 1 on any failure.
"""
import os, sys, json, zipfile, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(1, os.path.join(ROOT, "tools", "dev"))          # cpstrings (the constant-pool reader)
import skyybuild as B
import harness_kit as HK

VERSION, OLD = "0.1.36", "0.1.35"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyArmory-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyArmory-%s.jar" % OLD)
SKILLS_JAR = os.path.join(ROOT, "SkyySkills", "SkyySkills-0.4.52.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "arm36", "harness")))
PKG = "com.skyy.armory."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyArmory")
ASSETS = os.path.join(os.path.dirname(os.path.dirname(B.INSTALLED_SERVER_JAR)), "Assets.zip")
SOUL_FILES = ["Server/Item/Items/Weapon/Wand/Weapon_Wand_SoulOrb.json"] + [
    "Server/Item/Items/Weapon/Wand/Weapon_Wand_SoulCage_%s.json" % m for m in
    ("Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium") + tuple(w + "_SkyWynn" for w in
     ("Lead", "Dusk", "Chromium", "Azurvane", "Slag", "Cinder", "Titanium", "Lumen"))]
EXPECT = {"ArmoryCfg": ["+f M36_KEYS", "+f M36_OLD", "+f M36_NEW", "+f M36_MARK", "+f M36_MARK_ID", "+f M36_WHO", "+f M36_LAST", "+f HOP_LIFT",
                        "+m m36Key", "+m m36Update", "+m m36Log", "+m migrate036", "~<clinit>", "~m apply", "~m leapText", "~m load", "~m reloadAll",
                        "~m useDefaults"],
          "ArmoryCheck": ["~m packCheck", "~m packOf"],          # the version text
          "ArmoryTrav": ["~m hop"], "Leap": ["~m launchNow"], "TravMath": ["+m liftUp"],
          "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "CfgRows1": ["~<clinit>"], "CfgRows2": ["~<clinit>"], "CfgFile": ["~<clinit>"],
          "SkyyArmoryPlugin": ["~m setup", "~m start"]}          # migrate036 + its line, the version text
WAND_FILES = ["Server/Item/Items/Weapon/Wand/Weapon_Wand_%s.json" % m for m in
              ("Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium", "UT_SecondOpinion") + tuple(w + "_SkyWynn" for w in
               ("Lead", "Dusk", "Chromium", "Azurvane", "Slag", "Cinder", "Titanium", "Lumen"))]
ONE_HAND_CFG = {"Priorities": {"Secondary": {"MainHand": 1}}}
MIGS = ("migrate012", "migrate013", "migrate014", "migrate016", "migrate017", "migrate018", "migrate021", "migrate035", "migrate036")

# the non-class entries this round changes: manifest.json + the 16 Soul items + the 16 one-handed wands (harness_kit's compare knows manifest.json only)
_orig_compare = HK.run_compare


def _compare(out, jar, old_jar, pkg, expect, added, removed=()):
    E = HK.Child.eq

    def eq(self, got, want, what):
        if what == "C: non-class entries changed":
            want = sorted(["manifest.json"] + SOUL_FILES + WAND_FILES)
        return E(self, got, want, what)
    HK.Child.eq = eq
    try:
        _orig_compare(out, jar, old_jar, pkg, expect, added, removed)
    finally:
        HK.Child.eq = E
HK.run_compare = _compare


def setup_jvm(jar, *more):
    from jpype import JClass
    HK.jvm([B.SERVER_JAR] + list(more) + [jar], verify=True)
    JClass(PKG + "ArmoryLog").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyArmory")
    return JClass


# ---------------------------------------------------------------------------------------------------------------- H: the physics
def fly(vh, vy, cfg, g=32.0, hz=60, y0=0.0):
    """one Velocity Set (vh sideways, vy up) flown tick by tick: the applied velocity decays by the engine's split-velocity rule
    (MotionControllerBase.steer0): resistance = ground or air by contact, below Threshold blended toward the *Max value (Exp: t = v^2 / th^2,
    Linear: t = v / th), per tick r^(60 / hz); gravity on y; landing stops y. Returns (blocks, air seconds)."""
    air, airmax, gr, grmax, th, style = cfg
    dt = 1.0 / hz
    x, y, t, airt = 0.0, y0, 0, 0
    while t < 20 * hz:
        ground = y <= 1e-9 and vy <= 0.0
        r, rm = (gr, grmax) if ground else (air, airmax)
        if vh < th:
            k = (vh * vh) / (th * th) if style == "Exp" else vh / th
            r = r * k + rm * (1.0 - k)
        vh *= r ** (60.0 / hz)
        if not ground:
            vy -= g * dt
            airt += 1
        x += vh * dt
        y += vy * dt
        if y < 0.0:
            y, vy = 0.0, 0.0
        t += 1
        if vh < 0.05 and y <= 0.0:
            break
    return x, airt / float(hz)


def run_physics(out, jar, scratch, _home):
    K = HK.Child(out)
    JClass = setup_jvm(jar, B.JAVASSIST)
    TM, AT = JClass(PKG + "TravMath"), JClass(PKG + "ArmoryTrav")
    vc = AT.dash()
    cfg = (round(float(vc.getAirResistance()), 4), round(float(vc.getAirResistanceMax()), 4), round(float(vc.getGroundResistance()), 4),
           round(float(vc.getGroundResistanceMax()), 4), round(float(vc.getThreshold()), 4), str(vc.getStyle()))
    with zipfile.ZipFile(ASSETS) as z:
        dl = json.loads(z.read("Server/Item/Interactions/Dodge/Dodge_Left.json").decode("utf-8-sig"))
    push = [x for x in dl["Next"]["Interactions"] if x.get("Type") == "ApplyForce"][0]
    v = push["VelocityConfig"]
    vcfg = (v["AirResistance"], v["AirResistanceMax"], v["GroundResistance"], v["GroundResistanceMax"], v["Threshold"], v["Style"])
    K.eq(cfg, tuple(round(float(x), 4) if not isinstance(x, str) else x for x in vcfg),
         "H: the wand launch's VelocityConfig (ArmoryTrav.dash) = the vanilla dodge's (Dodge_Left.json)")
    # the engine's decay rule, read from the server jar (so the model above is the engine's, not a guess)
    CP = JClass("javassist.ClassPool")(True)
    CP.appendClassPath(B.SERVER_JAR)
    mcb = CP.get("com.hypixel.hytale.server.npc.movement.controllers.MotionControllerBase")
    IP, PS, BOS = JClass("javassist.bytecode.InstructionPrinter"), JClass("java.io.PrintStream"), JClass("java.io.ByteArrayOutputStream")

    def code(name):
        for m in mcb.getDeclaredMethods():
            if str(m.getName()) == name:
                b = BOS()
                IP(PS(b)).print_(m)
                return str(b.toString())
        return ""
    st, ex = code("steer0"), code("appliedVelocityDecayExponent")
    K.check("getGroundResistance" in st and "getAirResistanceMax" in st and "getThreshold" in st and "Math.pow" in st and "double 60.0" in ex and "ddiv" in ex,
            "H: the engine decays an applied velocity by resistance^(60 / tps), ground or air resistance, blended toward *Max below Threshold (steer0)")
    G = float(JClass("com.hypixel.hytale.server.core.modules.physics.util.PhysicsConstants").GRAVITY_ACCELERATION)
    g = G if G > 1.0 else 32.0

    def launch(force, maxup, lift, pitch, cvy=float("nan")):
        a = math.radians(pitch)
        hv = list(TM.hopVector(0.0, -math.sin(a), math.cos(a), force, False))
        up = float(TM.launchUp(hv[1], maxup))
        if lift is not None:
            up = float(TM.liftUp(up, lift, maxup))
        vy = float(TM.hopVy(up, cvy, 21.0))
        return fly(math.hypot(hv[0], hv[2]), vy, cfg, g)
    P = (0, 15, 30, 45, 60)
    old = dict((p, launch(18.0, 15.0, None, p)) for p in P)
    new = dict((p, launch(30.0, 20.0, 8.0, p)) for p in P)
    jump = fly(18.0, 0.0, cfg, g, y0=1.5)          # a level launch at the top of a jump: the Set replaces the jump's rise, you fall 1.5 blocks
    K.notes.append("H: gravity %s, cfg %s" % (g, cfg))
    K.notes.append("H: 0.1.35 (18 / 15, no lift) by look-down angle: %s" % {p: round(old[p][0], 2) for p in P})
    K.notes.append("H: 0.1.36 (30 / 20, lift 8): %s" % {p: round(new[p][0], 2) for p in P})
    K.notes.append("H: 0.1.35 level launch from a jump (1.5 blocks up): %.2f blocks" % jump[0])
    K.check(3.5 <= old[0][0] <= 4.5 and old[0][1] == 0.0, "H: REPRO - a level wand launch at 18 never leaves the ground and stops after %.2f blocks (Skyy: 'only sends me like four blocks')" % old[0][0])
    K.check(5.5 <= jump[0] <= 7.0, "H: REPRO - the same launch from a jump flies (air drag) %.2f blocks; + the walk back = Skyy's '8 if i walk backwards and jump'" % jump[0])
    K.check(all(new[p][1] > 0.3 for p in P), "H: FIX - every 0.1.36 launch leaves the ground (air time %s s)" % {p: round(new[p][1], 2) for p in P})
    rat = dict((p, new[p][0] / old[p][0]) for p in P)
    K.check(rat[0] >= 2.5 and all(1.75 <= rat[p] <= 2.2 for p in (15, 30, 45)) and max(new[p][0] for p in P) >= 2.0 * max(old[p][0] for p in P) * 0.95,
            "H: FIX - about 2x at every aim (x%s), the farthest %.1f vs %.1f blocks" % ({p: round(rat[p], 2) for p in P}, max(new[p][0] for p in P), max(old[p][0] for p in P)))
    hu = launch(30.0, 20.0, 8.0, 90)
    upx = float(TM.liftUp(float(TM.launchUp(30.0, 20.0)), 8.0, 20.0))
    K.check(upx == 20.0 and upx < 21.0, "H: straight down = %s b/s up = %.2f blocks up, landing at %s b/s (< MinFallSpeedToEngageRoll 21: no fall damage on flat ground)" % (upx, upx * upx / (2 * g), upx))
    K.check(hu[0] < 1e-6, "H: straight down = straight up (no sideways)")
    kept = float(TM.hopVy(float(TM.liftUp(0.0, 8.0, 20.0)), -30.0, 21.0))
    K.check(kept == -30.0, "H: 0.1.20 rule kept - falling at 30 b/s the lifted launch still keeps the fall (%s)" % kept)
    # the dodges
    dodges = {"vanilla Dodge_Left": fly(float(push["Force"]), 0.0, vcfg, g)}
    with zipfile.ZipFile(SKILLS_JAR) as z:
        for nm in ("Roll_Back", "Lunge_Back", "Flip_Back", "Flip_Left"):
            pj = json.loads(z.read("Server/Item/Interactions/Dodge/SkyySkills_%s_Push.json" % nm).decode("utf-8-sig"))
            d = pj["Direction"]
            n = math.sqrt(d["X"] ** 2 + d["Y"] ** 2 + d["Z"] ** 2)          # ApplyForce normalises its Direction (its codec)
            f = float(pj["Force"])
            pv = pj["VelocityConfig"]
            dodges["SkyySkills " + nm] = fly(f * math.hypot(d["X"], d["Z"]) / n, f * d["Y"] / n, (pv["AirResistance"], pv["AirResistanceMax"],
                                             pv["GroundResistance"], pv["GroundResistanceMax"], pv["Threshold"], pv["Style"]), g)
    best = max(x[0] for x in dodges.values())
    K.notes.append("H: dodges (blocks): %s" % {k: round(x[0], 2) for k, x in dodges.items()})
    K.check(best > old[0][0] * 0.9, "H: REPRO - the Priest flip dodge (%.2f) about matches / beats the grounded 0.1.35 launch (%.2f) - 'the dodge send you further'" % (
        dodges["SkyySkills Flip_Back"][0], old[0][0]))
    K.check(min(new[p][0] for p in (0, 15, 30, 45)) >= 2.0 * best, "H: FIX - the new launch (>= %.1f blocks at 0-45 deg) is over 2x the farthest dodge (%.2f)" % (
        min(new[p][0] for p in (0, 15, 30, 45)), best))
    K.save(old={p: old[p][0] for p in P}, new={p: new[p][0] for p in P}, dodges={k: x[0] for k, x in dodges.items()})


# ---------------------------------------------------------------------------------------------------------------- X: rows, rules, migration
def run_exec(out, jar, scratch, _home):
    K = HK.Child(out)
    JClass = setup_jvm(jar, B.JAVASSIST)
    Cfg, TM = JClass(PKG + "ArmoryCfg"), JClass(PKG + "TravMath")
    Props, SR = JClass("java.util.Properties"), JClass("java.io.StringReader")
    DEF = str(Cfg.DEF_CFG)
    want = ["hop.force=30", "hop.maxUp=20", "hop.lift=8"]
    K.check(all(("\n" + w + "\n") in DEF for w in want) and DEF.count(str(Cfg.M36_MARK)) == 1 and "\nhop.force=18\n" not in DEF,
            "X1: a fresh config.properties carries 30 / 20 / 8 + the 0.1.36 marker")

    def apply(drop=(), **kv):
        p = Props()
        p.load(SR(DEF))
        for k in drop:
            p.remove(k)
        for k, v in kv.items():
            p.setProperty(k.replace("__", "."), v)
        Cfg.apply(p)

    def cur():
        return [round(float(Cfg.HOP_FORCE), 3), round(float(Cfg.HOP_MAXUP), 3), round(float(Cfg.HOP_LIFT), 3)]
    apply()
    K.eq(cur(), [30.0, 20.0, 8.0], "X1: the loader reads the defaults")
    apply(drop=["hop.lift", "hop.force", "hop.maxUp"])
    K.eq(cur(), [30.0, 20.0, 8.0], "X1: missing lines = the defaults (hop.lift needs no update)")
    apply(hop__force="99", hop__maxUp="-3", hop__lift="40")
    K.eq(cur(), [50.0, 0.0, 20.0], "X1: hand edits clamped to the rows (force <= 50, maxUp >= 0, lift <= 20)")
    apply()
    lt = str(Cfg.leapText())
    K.check("launch 30" in lt and "at least 8.0 b/s up" in lt and "at most 20.0 b/s" in lt, "X1: leapText names the new numbers: %s" % lt[:200])
    # the pure rule
    lu = lambda v, l, m: round(float(TM.liftUp(v, l, m)), 4)
    rows = [((0.0, 8.0, 20.0), 8.0), ((12.0, 8.0, 20.0), 12.0), ((-13.0, 8.0, 20.0), 8.0), ((0.0, 0.0, 20.0), 0.0), ((0.0, 8.0, 5.0), 5.0),
            ((0.0, 8.0, 0.0), 8.0), ((20.0, 8.0, 20.0), 20.0)]
    bad = [(a, w, lu(*a)) for a, w in rows if lu(*a) != w]
    K.check(not bad, "X2: liftUp (level -> 8, already higher kept, a downward push lifted, lift 0 = off, never above maxUp, maxUp 0 = no cap): %s" % bad)
    hv = lambda up, cvy: round(float(TM.hopVy(float(TM.liftUp(up, 8.0, 20.0)), cvy, 21.0)), 4)
    K.eq([hv(0.0, -30.0), hv(0.0, -10.0), hv(0.0, float("nan")), hv(15.0, -25.0)], [-30.0, 8.0, 8.0, -25.0],
         "X2: the 0.1.20 damaging-fall rule still runs after the lift (a 30 / 25 b/s fall kept, a 10 b/s fall lifted)")
    # both launch paths: liftUp after launchUp, before hopVy (bytecode order)
    CP = JClass("javassist.ClassPool")(True)
    CP.appendClassPath(jar)
    order = {}
    for cn, mn in (("Leap", "launchNow"), ("ArmoryTrav", "hop"), ("Leap", "hopNow")):
        cc = CP.get(PKG + cn)
        for m in cc.getDeclaredMethods():
            if str(m.getName()) != mn:
                continue
            ca, cp = m.getMethodInfo().getCodeAttribute(), m.getMethodInfo().getConstPool()
            it, seq = ca.iterator(), []
            while it.hasNext():
                p = it.next()
                if it.byteAt(p) == 0xb8:
                    nm = str(cp.getMethodrefName(it.u16bitAt(p + 1)))
                    if nm in ("launchUp", "liftUp", "hopVy", "capUp", "upVy"):
                        seq.append(nm)
            order[cn + "." + mn] = seq
    K.check(order.get("Leap.launchNow") == ["launchUp", "liftUp", "hopVy"] and order.get("ArmoryTrav.hop") == ["launchUp", "liftUp", "hopVy"]
            and "liftUp" not in order.get("Leap.hopNow", []),
            "X2: the wand launch (Leap.launchNow) and the 0.1.2 hop job (ArmoryTrav.hop) lift, then keep a damaging fall; the bow leap (hopNow) is untouched: %s" % order)

    # ---- migrate036's text step
    def upd(t):
        r = Cfg.m36Update(t)
        return None if r is None else (str(r[0]), str(r[1]), [str(x) for x in r[2]], [str(x) for x in r[3]])
    MK = str(Cfg.M36_MARK)
    src = "# a\nhop.force=18\n# b\nhop.hangSeconds=0\nhop.maxUp=15\nhop.aimDelay=0.35\n"
    a = upd(src)
    K.check(a is not None and a[1] == "hop.force 18 -> 30, hop.maxUp 15 -> 20" and a[3] == ["hop.force", "18", "30", "hop.maxUp", "15", "20"]
            and a[0] == src.replace("hop.force=18", MK + "\nhop.force=30").replace("hop.maxUp=15", "hop.maxUp=20"),
            "X3: lines still at 18 / 15 -> 30 / 20 + the marker above hop.force, nothing else changed: %s" % (a and a[1]))
    K.check(upd(a[0]) is None, "X3: the marker = never again")
    h = upd(src.replace("hop.force=18", "hop.force=22").replace("hop.maxUp=15", "hop.maxUp=15.0"))
    K.check(h is not None and "hop.force=22" in h[0] and "hop.maxUp=20" in h[0] and h[1] == "hop.maxUp 15.0 -> 20" and len(h[2]) == 1 and "kept (custom)" in h[2][0],
            "X3: a hand-set hop.force 22 is kept + named, the untouched maxUp (15.0) still updates: %s / %s" % (h and h[1], h and h[2]))
    nl = upd("# x\nquick.size=40\n")
    K.check(nl is not None and nl[0] == "# x\nquick.size=40\n" + MK + "\n" and nl[1] == "", "X3: no hop lines = the marker only")
    cr = upd(src.replace("\n", "\r\n"))
    K.check(cr is not None and "hop.force=30\r\n" in cr[0] and "hop.maxUp=20\r\n" in cr[0] and cr[0].count("\r\n") == src.count("\n") + 1
            and "\n" not in cr[0].replace("\r\n", ""), "X3: CRLF kept (every line, the marker too)")
    # the chain on a pre-0.1.3 file (13, no markers): 13 -> 30 (0.1.3) -> 22 (0.1.16) -> 18 (0.1.17) -> 30 (0.1.36), in setup's order
    Paths = JClass("java.nio.file.Paths")
    home = os.path.join(scratch, "chain")
    os.makedirs(home, exist_ok=True)
    f = os.path.join(home, "config.properties")
    open(f, "wb").write(b"# old\r\nhop.force=13\r\norb.seconds=3.5\r\n")
    Cfg.DIR = Paths.get(home)
    Cfg.FILE = Paths.get(f)
    for m in MIGS:
        getattr(Cfg, m)()
    t = open(f, "rb").read().decode("latin-1")
    K.check("\r\nhop.force=30\r\n" in t and t.count("hop.force=") == 1 and MK in t and "\n" not in t.replace("\r\n", ""),
            "X3: an old file at 13 runs the whole chain to 30 (CRLF kept): %s" % [l for l in t.split("\r\n") if l.startswith("hop.")])
    K.save()


# ---------------------------------------------------------------------------------------------------------------- S: the Soul Orb one-handed
def prio(item, itype, slot):
    """InteractionConfiguration.getPriorityFor: no config / no entry = 0; a number = every slot; a map = that slot (else 0)"""
    p = ((item or {}).get("InteractionConfig") or {}).get("Priorities") or {}
    v = p.get(itype)
    if v is None:
        return 0
    if isinstance(v, (int, float)):
        return int(v)
    return int(v.get(slot, 0))


def route(main, off, itype):
    """InteractionContext.forInteraction (HytaleServer.jar, ported as in SkyyMenu 0.3.40's T40): 'off' = the off-hand item handles it"""
    if main is None and off is not None:
        return "off"
    if main is None or off is None:
        return "main"
    pm, po = prio(main, itype, "MainHand"), prio(off, itype, "OffHand")
    if pm == po:
        return "off" if itype == "Secondary" and (main.get("Utility") or {}).get("Compatible", False) else "main"
    if pm < po:
        return "off"
    if itype not in (main.get("Interactions") or {}):
        return "off"
    return "main"


def run_soul(out, jar, scratch, _home):
    K = HK.Child(out)
    JClass = setup_jvm(jar)
    ids = [str(x) for x in JClass(PKG + "ArmoryDefs").SOUL_IDS]
    K.eq(sorted(ids), sorted(os.path.basename(p)[:-5] for p in SOUL_FILES), "S: the 16 Soul item ids = the files checked")
    with zipfile.ZipFile(ASSETS) as z:
        vw = json.loads(z.read("Server/Item/Items/Weapon/Wand/Weapon_Wand_Wood.json").decode("utf-8-sig"))
        has_wand = "Server/Item/Animations/Wand.json" in z.namelist()
    K.check(vw.get("Utility") == {"Compatible": True} and vw.get("PlayerAnimationsId") == "Wand" and has_wand,
            "S: the vanilla one-handed wand = Utility Compatible + the Wand animation set (Server/Item/Animations/Wand.json exists)")
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    bad = []
    for p in SOUL_FILES:
        o, n = json.loads(za.read(p).decode("utf-8-sig")), json.loads(zb.read(p).decode("utf-8-sig"))
        o2 = dict(o)
        o2["Utility"] = {"Compatible": True}
        o2["InteractionConfig"] = ONE_HAND_CFG
        if not (n.get("Utility") == {"Compatible": True} and "Utility" not in o and "InteractionConfig" not in o and n.get("PlayerAnimationsId") == "Wand"
                and n["Interactions"] == o["Interactions"] and n == o2):
            bad.append(p)
    K.check(not bad, "S: every Soul Orb / Soul Cage is one-handed (Utility Compatible, was absent), keeps the Wand set and its Wings of Fate / "
            "Bindings interactions, gains the right-click priority, nothing else changed: %s" % bad)
    wb = []
    for p in WAND_FILES:
        o, n = json.loads(za.read(p).decode("utf-8-sig")), json.loads(zb.read(p).decode("utf-8-sig"))
        o2 = dict(o)
        o2["InteractionConfig"] = ONE_HAND_CFG
        if not (o.get("Utility") == {"Compatible": True} and (o.get("Interactions") or {}).get("Secondary") and "InteractionConfig" not in o and n == o2):
            wb.append(p)
    K.check(not wb, "S: the 16 one-handed wands (Compatible, own right-click guard) gain only the right-click priority: %s" % wb)
    # the engine's hand choice (InteractionContext.forInteraction - SkyyMenu 0.3.40 T40's port): shield / torch / empty off-hand
    from cpstrings import read_utf8_constants
    sj = zipfile.ZipFile(B.INSTALLED_SERVER_JAR)
    ic = read_utf8_constants(sj.read("com/hypixel/hytale/server/core/entity/InteractionContext.class"))
    K.check("isCompatible" in ic and "getPriorityFor" in ic, "HAND: the engine routes by isCompatible + getPriorityFor (InteractionContext)")
    with zipfile.ZipFile(ASSETS) as az:
        vit = dict((n.split("/")[-1][:-5], n) for n in az.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
        ld = lambda k: json.loads(az.read(vit[k]).decode("utf-8-sig"))
        hoe, shield, torch = ld("Tool_Hoe_Crude"), ld("Template_Weapon_Shield"), ld("Furniture_Crude_Torch")
    K.check(hoe.get("InteractionConfig") == ONE_HAND_CFG and hoe.get("Utility") == {"Compatible": True} and "Secondary" in (shield.get("Interactions") or {}),
            "HAND: the priority = the vanilla Tool_Hoe_Crude's; the vanilla shield has its own right-click")
    hb = []
    for p in SOUL_FILES + WAND_FILES:
        n, o = json.loads(zb.read(p).decode("utf-8-sig")), json.loads(za.read(p).decode("utf-8-sig"))
        got = [route(n, off, "Secondary") for off in (None, shield, torch)]
        ctl = dict(n)
        ctl.pop("InteractionConfig")
        if got != ["main"] * 3 or route(ctl, shield, "Secondary") != "off" or route(n, shield, "Primary") != route(o, shield, "Primary"):
            hb.append((p, got, route(ctl, shield, "Secondary")))
    K.check(not hb, "HAND: right-click stays the Bindings / the wand guard with an empty, shield or torch off-hand (control: without the priority a "
            "shield would take it); left-click routing unchanged: %s" % hb[:3])
    ia = set(json.loads(zb.read(SOUL_FILES[0]).decode("utf-8-sig"))["Interactions"].values())
    K.check(all(any(n.endswith("/%s.json" % i) for n in zb.namelist()) for i in ia), "S: the Soul interactions' root files are in the jar: %s" % sorted(ia))
    K.save()


# ---------------------------------------------------------------------------------------------------------------- D: Skyy's live file
def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    JClass(PKG + "ArmoryLog").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyArmory")
    Cfg = JClass(PKG + "ArmoryCfg")
    Paths = JClass("java.nio.file.Paths")
    Cfg.DIR = Paths.get(home)
    Cfg.FILE = Paths.get(home).resolve("config.properties")
    f = os.path.join(home, "config.properties")
    before = open(f, "rb").read()
    snaps, msgs = [], []
    for start in (1, 2):
        for m in MIGS:
            r = str(getattr(Cfg, m)())
            if m == "migrate036":
                msgs.append(r)
        Cfg.load()
        snaps.append(open(f, "rb").read())
    K.check(snaps[0] == snaps[1] and msgs[1] == "", "D: the 2nd start changes nothing")
    b, a = before.decode("latin-1"), snaps[0].decode("latin-1")
    eol = "\r\n" if "\r\n" in b else "\n"
    had = (eol + "hop.force=18" + eol) in b and (eol + "hop.maxUp=15" + eol) in b
    K.check(had, "D: Skyy's live file holds hop.force=18 and hop.maxUp=15 (the defaults this round updates)")
    exp = b.replace(eol + "hop.force=18" + eol, eol + str(Cfg.M36_MARK) + eol + "hop.force=30" + eol).replace(eol + "hop.maxUp=15" + eol, eol + "hop.maxUp=20" + eol)
    K.check(a == exp and a.count(str(Cfg.M36_MARK)) == 1, "D: the 1st start changed only hop.force 18 -> 30, hop.maxUp 15 -> 20 + added the marker (bytes + line ends kept): %s" % msgs[0][:200])
    K.eq([float(Cfg.HOP_FORCE), float(Cfg.HOP_MAXUP), float(Cfg.HOP_LIFT)], [30.0, 20.0, 8.0], "D: the loader reads 30 / 20 + the hop.lift default 8")
    hist = [os.path.join(dp, fn) for dp, _d, fns in os.walk(home) for fn in fns if fn != "config.properties"]
    held = [p for p in hist if open(p, "rb").read() == before]
    logl = [l for p in hist for l in open(p, "rb").read().decode("latin-1").splitlines() if "SkyyArmory 0.1.36" in l and "\tupdate\thop." in l]
    K.check(held and len(logl) == 2 and any("\thop.force\t18\t30\tok" in l for l in logl) and any("\thop.maxUp\t15\t20\tok" in l for l in logl),
            "D: a History copy holds the old bytes (%d) and the change log has both lines (Server Setup -> Changes can undo): %s" % (len(held), logl))
    K.notes.append("D: live config %d bytes, eol %r; files %s" % (len(before), eol, [os.path.relpath(p, home) for p in hist][:6]))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyArmory", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("physics", run_physics), ("exec", run_exec), ("soul", run_soul), ("live", run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyArmory"))
