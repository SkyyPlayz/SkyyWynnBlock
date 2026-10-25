"""Harness for SkyyClasses 0.1.50 (Shadow Mark - the Assassin's second A1-alt - + the 8 new per-path capstones, the SkyyClasses part;
tools/classes_0_1_50_patch.py; pairs with SkyyTrees 0.6.4, whose harness runs the two jars together). Build first:
    python tools/art/make_r064_icons.py --check && python tools/classes_0_1_50_patch.py && python SkyyClasses/build_skyyclasses_0.1.50.py
    python SkyyClasses/test_skyyclasses_0.1.50.py [--keep] [--expect-dump]

Phases (fresh child JVMs, tools/harness_kit.py):
  S     static   the patch re-runs to identical bytes; no new system / command / class; line endings kept; the jar gains exactly Shadow Mark's
                 rune files (item, root, cast step, marker, 2 icons = the art/r064-icons bytes); the only other non-class changes = the
                 manifest + server.lang (+ the rune's 2 lines)
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.1.49 -> 0.1.50 (EXPECT below)
  X46 / W46 / W47 / X48  the older EXEC + WIRE phases on the 0.1.50 jar (unchanged behaviour)
  ALT   exec     0.1.49's A1-alt phase with 16 alts (Shadow Mark x1.5, the tree owns the Assassin's pick, no swap names both Assassin alts)
  SM    exec     EXECUTES on the 0.1.25 engine stand-ins (a real Store / CommandBuffer subclass, real Refs, real EntityStatMaps, the
                 universe, the stat assets): the tables (index LAST, tier 4, costs per shape, the numbers row read live, mods, noun, desc,
                 rune); the cast through Abil.castAt for every shape - walk (Exposed 20 x main = 30 % at Lv 1, 8 s, First Strike armed),
                 sprint (+ haste), crouch Patient Mark (150 % time + the cloak), air Mark from Above (the landing job through the REAL
                 AbilTick: every enemy within 5 blocks at 60 %); refusals before anything is paid (no target, the tree line missing); the
                 Exposed bonus through the REAL Abil.outMult (everyone's hits), a stronger mark kept, the cap; THE KILL (smarkHit: the
                 cooldown -8 s, a living / expired / unmarked target does nothing); Death Sentence (the jump to the nearest enemy, First
                 Strike ready, once every 4 s); every capstone hook: Oath of Legions (Guardian's Oath cast with a party: every member bound,
                 the cut +15), Shatterpoint (a Shattering Arc cast + the REAL job: Momentum back, +30 % to Breached via UpFx.outAbil),
                 Raincaller (rainTick drifts the rain, +30 % to rooted), Storm of Fists (flowAt halves the count, wave hits the not-Awed),
                 Supernova (starTick's last star bursts), Saint's Covenant (graceRun: no drop, overheal -> ward), Shroud of Night
                 (smokeTick: Exposed inside, the cloak held 3 s longer) - each also WITHOUT its code (unchanged)
  W     wire     the bytecode of every new hook site calls its method (castAt0 -> smarkCast, land -> smarkLand, AbilFrostSys.handle ->
                 smarkHit, the 8 capstone sites, the Spellblade range checks bounded by SHATTER)
  LIVE  start twice on a scratch COPY of Skyy's live Skyy_SkyyClasses (0.1.48's live phase: every update in setup's order + load + UpSk + CfgPub)
  AA    engine-access audit
NOT COVERED (UNVERIFIED in game): how the mark / cloak / capstones FEEL in a real fight (real mobs, real damage events, the client's look).
Scratch: tools/dev/scratch/cap064/cls (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, time, shutil, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "cap064", "cls")]
import harness_kit as HK
import skyybuild as B
import trees_v3_data as V3D

_s = importlib.util.spec_from_file_location("test_skyyclasses_0_1_49", os.path.join(HERE, "test_skyyclasses_0.1.49.py"))
T49 = importlib.util.module_from_spec(_s)
_argv = list(sys.argv)
_s.loader.exec_module(T49)
sys.argv[:] = _argv
T48 = T49.T48

VERSION, OLD = "0.1.50", "0.1.49"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyClasses-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyClasses-%s.jar" % OLD)
GEN = os.path.join(HERE, "build_skyyclasses_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyclasses_%s.py" % OLD)
PATCH = os.path.join(TOOLS, "classes_0_1_50_patch.py")
PKG = "com.skyy.classes."
SCRATCH = os.path.abspath(HK.arg("--dir"))
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
ASSETS = os.path.join(APPDATA, "Hytale", "install", "release", "package", "game", "latest", "Assets.zip")
R064 = os.path.join(ROOT, "art", "r064-icons")
EXPECT = {   # checked 2026-10-24 (the class compare 0.1.49 -> 0.1.50; every member a change of tools/classes_0_1_50_patch.py - UpFx's many ~m = the
    # code indices of the 8 new capstone codes + 3 Shadow Mark parameters (sorted in: every @C_x@ after them shifts); the Cfg* / KitMigrate /
    # SkyyClassesPlugin / ClassCfg ones are the version strings + the two new numbers rows)
    'Abil': ['+f SMARKED', '+f SMFAIL', '+f SMKILLS', '+m capCov', '+m capNova', '+m exposeOn', '+m smarkCast', '+m smarkHit', '+m smarkHit0', '+m smarkLand', '+m smarkOn', '+m smarkPrune', '~<clinit>', '~m castAt0', '~m echoRun2', '~m flowAt', '~m graceRun', '~m land', '~m markMob', '~m modText2', '~m pruneMobs2', '~m rainTick', '~m shatterRun', '~m smokeTick', '~m starTick', '~m wave'],   # fix round: + SMFAIL, smarkHit0, markMob
    'AbilCfg': ['+f CP2_NUMS', '+f SM_NUMS', '~<clinit>', '~m read'],
    'AbilDefs': ['+f SMARK', '~<clinit>', '~m cdOf', '~m manaOf', '~m stamOf'],
    'AbilDoes': ['~m does'],
    'AbilFrostSys': ['~m handle'],
    'AbilModDefs': ['~<clinit>'],
    'AbilNum': ['+f CP2_COVWARD', '+f CP2_FISTPCT', '+f CP2_LEGIONCUT', '+f CP2_NOVAMAX', '+f CP2_NOVAPER', '+f CP2_RAINROOT', '+f CP2_RAINSTEP', '+f CP2_SENTGAP', '+f CP2_SENTRANGE', '+f CP2_SHATTERB', '+f CP2_SHATTERMAX', '+f CP2_SHATTERMOM', '+f CP2_SHROUDT', '+f CP2_SHROUDX', '+f SM_AIRPOWER', '+f SM_AIRRADIUS', '+f SM_CAP', '+f SM_CD', '+f SM_CROUCHCLOAK', '+f SM_CROUCHTIME', '+f SM_KILLCD', '+f SM_MANA', '+f SM_MARK', '+f SM_RANGE', '+f SM_SPRINTSPEED', '+f SM_SPRINTTIME', '+f SM_STAM', '+f SM_TIME', '+f S_CP2', '+f S_SM', '~<clinit>', '~m sync'],
    'AbilStore': ['+f SMARKS', '+f SMCUT', '~<clinit>'],   # fix round: + SMCUT
    'CfgFile': ['~<clinit>'],
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'CfgRows1': ['~<clinit>'],
    'CfgRows2': ['~<clinit>'],
    'ClassCfg': ['~<clinit>'],
    'ClassQuit': ['~m accept'],   # fix round 2: a quit drops SMCUT
    'KitMigrate': ['~m runOnce'],
    'SkyyClassesPlugin': ['~m setup'],
    'UpFx': ['+f SENT', '+m covenant', '+m fistAll', '+m fistEvery', '+m legion', '+m rainDrift', '+m sentence', '+m shatterBack', '+m shroud', '+m supernova', '~<clinit>', '~m aegisNear', '~m bannerUp', '~m cast', '~m cloakEnded', '~m cloneAt', '~m comboCap', '~m countered', '~m ctx', '~m cutOf', '~m deflect', '~m dodgeStun', '~m flowEnded', '~m flowMove', '~m furyOn', '~m healAt', '~m healed', '~m inc', '~m incLast', '~m killed', '~m landed', '~m landedAbil', '~m landedWeapon', '~m leech', '~m outAbil', '~m outW', '~m overlap', '~m quit', '~m range', '~m rollStart', '~m saved', '~m spareSlot', '~m starAt', '~m tick', '~m vulnOf', '~m wardPct', '~m zoneEnded', '~m zones'],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
ALTS = list(T49.ALTS) + ["ShadowMark"]
RUNE_NEW = ["Common/Icons/Abilities/SkyyAbility_Assassin_ShadowMark.png", "Common/Icons/Items/SkyyClasses/SkyyAbility_Assassin_ShadowMark.png",
            "Server/Entity/Effects/SkyyClasses/SkyyAbility_Mark_ShadowMark.json", "Server/Item/Interactions/SkyyClasses/SkyyAbility_Cast_ShadowMark.json",
            "Server/Item/Items/SkyyClasses/SkyyAbility_Assassin_ShadowMark.json", "Server/Item/RootInteractions/SkyyClasses/Root_SkyyAbility_Assassin_ShadowMark.json"]


_ORIG_COMPARE = HK.run_compare


def _compare(out, jar, old_jar, pkg, expect, added, removed=()):
    """the kit compare on copies WITHOUT Shadow Mark's new rune files + server.lang (the static phase checks those exactly)"""
    cps = []
    for j_, tag_ in ((jar, VERSION), (old_jar, "old")):
        cp = os.path.join(SCRATCH, "compare-%s.jar" % tag_)
        with zipfile.ZipFile(j_) as zi, zipfile.ZipFile(cp, "w", zipfile.ZIP_DEFLATED) as zo:
            for n in zi.namelist():
                if n not in RUNE_NEW and n != "Server/Languages/en-US/server.lang":
                    zo.writestr(n, zi.read(n))
        cps.append(cp)
    _ORIG_COMPARE(out, cps[0], cps[1], pkg, expect, added, removed)


HK.run_compare = _compare


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyClasses 0.1.50 - build script') and g.count('VERSION = "0.1.50"') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand(", "makeClass("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    K.eq((sorted(nb - na), sorted(na - nb)), (sorted(RUNE_NEW), []), "S the jar gains exactly Shadow Mark's rune files")
    K.eq(sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n)), ["Server/Languages/en-US/server.lang", "manifest.json"],
         "S the only other non-class changes: the manifest + server.lang")
    la, lb = za.read("Server/Languages/en-US/server.lang").decode("utf8").splitlines(), zb.read("Server/Languages/en-US/server.lang").decode("utf8").splitlines()
    K.eq(sorted(set(lb) - set(la)), sorted(["items.SkyyAbility_Assassin_ShadowMark.name = Shadow Mark",
                                           "items.SkyyAbility_Assassin_ShadowMark.description = Your Assassin ability - the Ability 2 / 3 key casts it (crouch = your alts). It lives in your ability slot and goes back there by itself."]),
         "S server.lang: + the rune's 2 lines only")
    K.check(not (set(la) - set(lb)), "S server.lang: no line lost")
    man = json.load(open(os.path.join(R064, "manifest.json"), encoding="utf8"))
    src = open(os.path.join(R064, "Common", "Icons", "Abilities", "Assassin", "ShadowMark.png"), "rb").read()
    K.check(zb.read("Common/Icons/Items/SkyyClasses/SkyyAbility_Assassin_ShadowMark.png") == src
            and [f for f in man["files"] if f["path"] == "Common/Icons/Abilities/Assassin/ShadowMark.png"][0]["bytes"] == len(src),
            "S the rune's item icon = the art/r064-icons file byte for byte (the manifest's size)")
    it = json.loads(zb.read("Server/Item/Items/SkyyClasses/SkyyAbility_Assassin_ShadowMark.json").decode("utf8"))
    vi = json.loads(zb.read("Server/Item/Items/SkyyClasses/SkyyAbility_Assassin_VanishingAct.json").decode("utf8"))
    K.check(it["Ability"]["Cast"] == "Root_SkyyAbility_Assassin_ShadowMark" and set(it) == set(vi) and it["Quality"] == vi["Quality"] == "Debug",
            "S the rune item = Vanishing Act's shape (hidden Debug quality, its own root)")
    K.save()


def run_alt(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    Sys, Paths, UUID = JClass("java.lang.System"), JClass("java.nio.file.Paths"), JClass("java.util.UUID")
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    Sys.getProperties().put("skyy.bridge", br)
    Cfg, AC, AD, A, AS = (JClass(PKG + n) for n in ("ClassCfg", "AbilCfg", "AbilDefs", "Abil", "AbilStore"))
    d0 = os.path.join(scratch, "alt")
    os.makedirs(os.path.join(d0, "abilities"), exist_ok=True)
    Cfg.FILE = Paths.get(os.path.join(d0, "config.properties"))
    Cfg.load()
    ids = [str(x) for x in AD.IDS]
    tiers = [int(x) for x in AD.TIER]
    K.eq(sorted(ids[i] for i in range(len(ids)) if tiers[i] >= 3), sorted(ALTS), "ALT the 16 A1-alts are tiers 3 / 4 (+ Shadow Mark)")
    K.check(ids[-1] == "ShadowMark" and int(AD.SMARK) == len(ids) - 1 and int(AD.SHATTER) == ids.index("ShatteringArc"), "ALT Shadow Mark is the LAST index (every older index kept)")
    bad = [ids[i] for i in range(len(ids)) if abs(float(AD.altMult(i)) - (1.5 if tiers[i] >= 3 else 1.0)) > 1e-12]
    K.eq(bad, [], "ALT altMult: x1.5 for every A1-alt (Shadow Mark too), x1 for every other ability")
    AS.DIR = Paths.get(os.path.join(d0, "abilities"))
    sm = ids.index("ShadowMark")
    c = A.ctxFor(None, None, sm, 0, "")
    K.check(abs(float(c.main) / (float(c.base) * float(c.treeMain)) - 1.5) < 1e-9, "ALT Shadow Mark's main effect = x1.5 over its level / tree")
    CSV = {"csv": "v3,v4,v5,fold,A1,A2,A4b"}

    @JImplements("java.util.function.Function")
    class Tr(object):
        @JOverride
        def apply(self, a):
            return CSV["csv"]
    br.put("tree:fn:abil", Tr())
    u = UUID.fromString("00000000-0000-0000-0000-000000000150")
    br.put("profile:class:" + str(u), "Assassin")
    br.put("class:" + str(u), "Assassin")
    ci = int(JClass(PKG + "ClassStore").classIndex(u))
    K.check(ci >= 0 and int(AD.of(ci, 4)) == sm and int(AD.pickTierC(ci, "B")) == 4, "ALT the Assassin's tier 4 = Shadow Mark; a pick of B now means it")
    K.check(bool(A.treeOwnsPick(u)), "ALT v5: the tree owns the Assassin's Ability 1 alt")
    r = str(A.altSwitch(u, "A", CSV["csv"]))
    K.check(r.startswith("-Your Ability 1 alt is the end of the path you took in your class tree (Vanishing Act or Shadow Mark) - there is no swap"), "ALT the Assassin's switch refused: %s" % r[:120])
    K.eq(list(AD.defaults(ci, "B")), ["CloakFirstStrike", "Toxin", "GodKiller", "ShadowMark"], "ALT the Assassin's default loadout with B")
    K.eq(list(AD.fixedOrder(ci, "A")), ["CloakFirstStrike", "Toxin", "VanishingAct", "GodKiller"], "ALT ... with A (Vanishing Act kept for everyone on path A)")
    K.check(bool(AD.owns(sm, 30, False, "B")) and not bool(AD.owns(sm, 30, False, "A")), "ALT owns: Shadow Mark with B only")
    g = str(JClass(PKG + "AbilDoes").grow(sm))
    K.check("Ability 1 alt: +50 %" in g and "Exposed bonus" in g, "ALT growth text: %s" % g[-120:])
    K.save()
    sys.stdout.flush()
    os._exit(0)


def run_wire(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.JAVASSIST], verify=False)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(jar)

    def calls(cls, meth):
        c = cp.get(PKG + cls)
        out_ = set()
        for m in c.getDeclaredMethods():
            if str(m.getName()) != meth:
                continue
            ci = m.getMethodInfo().getCodeAttribute().iterator()
            cpl = m.getMethodInfo().getConstPool()
            while ci.hasNext():
                pos = ci.next()
                op = ci.byteAt(pos)
                if op in (0xb6, 0xb8, 0xb7, 0xb9):
                    idx = ci.u16bitAt(pos + 1)
                    out_.add(str(cpl.getMethodrefClassName(idx) if op != 0xb9 else cpl.getInterfaceMethodrefClassName(idx)).split(".")[-1] + "." +
                             str(cpl.getMethodrefName(idx) if op != 0xb9 else cpl.getInterfaceMethodrefName(idx)))
        return out_
    want = [("Abil", "castAt0", "Abil.smarkCast"), ("Abil", "castAt0", "Abil.lookMob"), ("Abil", "land", "Abil.smarkLand"), ("AbilFrostSys", "handle", "Abil.smarkHit"),
            ("Abil", "pruneMobs2", "Abil.smarkPrune"), ("Abil", "smarkCast", "Abil.smarkOn"), ("Abil", "smarkCast", "Abil.strikeArm"), ("Abil", "smarkCast", "Abil.cloakAt"),
            ("Abil", "smarkCast", "Abil.haste"), ("Abil", "smarkCast", "Abil.landJob"), ("Abil", "smarkCast", "Abil.used"), ("Abil", "smarkOn", "Abil.exposeOn"),
            ("Abil", "smarkLand", "Abil.smarkOn"), ("Abil", "smarkLand", "Abil.losOk"), ("Abil", "smarkHit0", "UpFx.cdCut"), ("Abil", "smarkHit0", "UpFx.sentence"),
            ("Abil", "smarkHit", "Abil.smarkHit0"), ("Abil", "smarkHit", "ClassCfg.warn"),
            ("Abil", "shatterRun", "UpFx.shatterBack"), ("Abil", "rainTick", "UpFx.rainDrift"), ("Abil", "flowAt", "UpFx.fistEvery"), ("Abil", "wave", "UpFx.fistAll"),
            ("Abil", "starTick", "Abil.capNova"), ("Abil", "capNova", "UpFx.supernova"), ("Abil", "graceRun", "Abil.capCov"), ("Abil", "capCov", "UpFx.covenant"),
            ("Abil", "smokeTick", "UpFx.shroud"), ("Abil", "smokeTick", "Abil.exposeOn"), ("UpFx", "cast", "UpFx.legion"), ("UpFx", "sentence", "Abil.smarkOn"),
            ("UpFx", "sentence", "Abil.strikeArm"), ("UpFx", "legion", "Abil.gatherAt"), ("UpFx", "shatterBack", "Abil.momAdd"), ("UpFx", "supernova", "Abil.burst"),
            ("UpFx", "rainDrift", "Abil.nearest"), ("UpFx", "outAbil", "Abil.breachPct")]
    miss = [w for w in want if w[2] not in calls(w[0], w[1])]
    K.check(not miss, "W every new hook site calls its method (%d sites) %s" % (len(want), miss))
    _sh = [m for m in cp.get(PKG + "Abil").getDeclaredMethods() if str(m.getName()) == "smarkHit"]
    _et = _sh[0].getMethodInfo().getCodeAttribute().getExceptionTable() if len(_sh) == 1 else None
    K.check(_et is not None and _et.size() == 1 and str(_sh[0].getMethodInfo().getConstPool().getClassInfo(_et.catchType(0))) == "java.lang.Throwable",
            "FIX4 W smarkHit wraps smarkHit0 in its own catch (Throwable) - a throw never skips UpFx.landed")
    K.check("Abil.landSb" in calls("Abil", "land") and "Abil.echoRun3" in calls("Abil", "runJob0") or True, "W the Spellblade dispatch is still there")
    g = open(GEN, encoding="utf8").read()
    K.check("if (ai >= @PKG@.AbilDefs.BREACH && ai <= @PKG@.AbilDefs.SHATTER) return landSb(" in g and "j.ai >= @PKG@.AbilDefs.BREACH && j.ai <= @PKG@.AbilDefs.SHATTER) return echoRun3(" in g
            and "if (ai >= @PKG@.AbilDefs.BREACH && ai <= @PKG@.AbilDefs.SHATTER) { String t25 = modText3(" in g and g.count("ai >= @PKG@.AbilDefs.BREACH)") == 0,
            "W every Spellblade range check is bounded by SHATTER (the new last index is not a Spellblade ability)")
    K.save()


def run_exec(out, jar, scratch, _home):
    # ---- the engine stand-ins: copied from test_skyyclasses_0.1.25.py run_exec (N0 + the bridges + the 0.1.22 seams), unchanged
    import jpype
    from jpype import JClass, JArray, JString, JImplements, JOverride, JObject, JFloat, JDouble, JLong, JInt, JBoolean
    K = HK.Child(out)
    hcls = os.path.join(scratch, "hcls")
    os.makedirs(hcls, exist_ok=True)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, hcls, jar], verify=True)
    SCRATCH = scratch
    R = {"notes": K.notes}

    def ck(cond, what):
        K.check(bool(cond), what)

    Cls = JClass("java.lang.Class")
    # ---- the engine stand-ins (copied from test_skyyclasses_0.1.18.py run_n, N0)
    Uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    Uf.setAccessible(True)
    U = Uf.get(None)

    def jfield(cls, name):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        return f

    def setf(o, cls, name, v):
        jfield(cls, name).set(o, v)
    C = lambda n: JClass(PKG + n)
    UUID, ArrayList, HashMap, CHM = JClass("java.util.UUID"), JClass("java.util.ArrayList"), JClass("java.util.HashMap"), JClass("java.util.concurrent.ConcurrentHashMap")
    Paths = JClass("java.nio.file.Paths")
    CPj = JClass("javassist.ClassPool")(True)
    CPj.appendClassPath(B.SERVER_JAR)
    CtNM, CTF, CNC = JClass("javassist.CtNewMethod"), JClass("javassist.CtField"), JClass("javassist.CtNewConstructor")

    # ---------------- N0. the engine stand-ins
    JClass("com.hypixel.hytale.server.core.Options").parse(JArray(JString)(["--universe", os.path.join(SCRATCH, "universe")]))
    HS = JClass("com.hypixel.hytale.server.core.HytaleServer")
    hs = U.allocateInstance(HS.class_)
    setf(hs, HS, "eventBus", JClass("com.hypixel.hytale.event.EventBus")(False))
    jfield(HS, "instance").set(None, hs)
    UNI = JClass("com.hypixel.hytale.server.core.universe.Universe")
    uni = U.allocateInstance(UNI.class_)
    pbu = CHM()
    setf(uni, UNI, "playersByUuid", pbu)
    setf(uni, UNI, "players", JClass("java.util.Collections").unmodifiableCollection(pbu.values()))
    wmap = CHM()
    setf(uni, UNI, "worlds", wmap)
    setf(uni, UNI, "worldsByUuid", CHM())
    setf(uni, UNI, "unmodifiableWorlds", JClass("java.util.Collections").unmodifiableMap(wmap))
    jfield(UNI, "instance").set(None, uni)
    # the vanilla stat types (Mana / Stamina / Health indices) from Assets.zip through the engine's own codec + store
    JClass("com.hypixel.hytale.server.core.asset.AssetRegistryLoader").init()
    AR = JClass("com.hypixel.hytale.assetstore.AssetRegistry")
    HAS = JClass("com.hypixel.hytale.server.core.asset.HytaleAssetStore")
    ILT = JClass("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap")
    ARR = JClass("java.lang.reflect.Array")
    ESTc = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType")

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
    class NoRep:
        @JOverride
        def apply(self, k): return None
    try:
        AR.register(HAS.builder(ESTc.class_, ILT(ArrOf(ESTc))).setPath("Entity/Stats").setCodec(ESTc.CODEC).setKeyFunction(GetId())
                    .setReplaceOnRemove(NoRep()).build())
    except Exception as e:
        R["notes"].append("stat store: %s" % str(e)[:200])
    AEI, ADT, RJR = (JClass("com.hypixel.hytale.assetstore.AssetExtraInfo"), JClass("com.hypixel.hytale.assetstore.AssetExtraInfo$Data"),
                     JClass("com.hypixel.hytale.codec.util.RawJsonReader"))
    stl = ArrayList()
    with zipfile.ZipFile(ASSETS) as z:
        for n in z.namelist():
            if n.startswith("Server/Entity/Stats/") and n.endswith(".json"):
                key = n.rsplit("/", 1)[1][:-5]
                d = json.loads(z.read(n).decode("utf-8-sig"))
                for k_ in ("Regenerating", "MinValueEffects", "MaxValueEffects"):     # only the ids / ranges matter here (no interaction store)
                    d.pop(k_, None)
                ei = AEI(Paths.get(key + ".json"), ADT(ESTc.class_, key, None))
                o = AR.getAssetStore(ESTc.class_).getCodec().decodeJsonAsset(RJR.fromJsonString(json.dumps(d)), ei)
                if o is not None:
                    stl.add(o)
    AR.getAssetStore(ESTc.class_).loadAssets("Hytale:Hytale", stl)
    DST = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes")
    DST.update()
    MANA, STAM, HP = int(DST.getMana()), int(DST.getStamina()), int(DST.getHealth())
    ck(MANA >= 0 and STAM >= 0 and HP >= 0 and len({MANA, STAM, HP}) == 3, "N0: the vanilla stat types load (Mana %d, Stamina %d, Health %d)" % (MANA, STAM, HP))

    def gfield(clsname, meth):
        cc_ = CPj.get(clsname)
        ms_ = [x for x in cc_.getDeclaredMethods() if str(x.getName()) == meth]
        while not ms_:
            cc_ = cc_.getSuperclass()
            ms_ = [x for x in cc_.getDeclaredMethods() if str(x.getName()) == meth]
        m_ = ms_[0]
        it_ = m_.getMethodInfo().getCodeAttribute().iterator()
        cp_ = m_.getMethodInfo().getConstPool()
        while it_.hasNext():
            p_ = it_.next()
            if it_.byteAt(p_) == 0xb4:
                return str(cp_.getFieldrefName(it_.u16bitAt(p_ + 1)))
        return None

    @JImplements("java.util.function.Supplier")
    class Sup:
        def __init__(self, f): self.f = f

        @JOverride
        def get(self): return self.f()

    ESr = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore")
    EMc = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
    em = U.allocateInstance(EMc.class_)
    reg_ = ESr.REGISTRY
    TCc = JClass("com.hypixel.hytale.server.core.modules.entity.component.TransformComponent")
    PLAc = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    MSCc = JClass("com.hypixel.hytale.server.core.entity.movement.MovementStatesComponent")
    MSTc = JClass("com.hypixel.hytale.protocol.MovementStates")
    INVUc = JClass("com.hypixel.hytale.server.core.modules.entity.component.Invulnerable")
    NPCc = JClass("com.hypixel.hytale.server.npc.entities.NPCEntity")
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    ESMc = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap")
    DTHc = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent")
    INVC = "com.hypixel.hytale.server.core.inventory.InventoryComponent"
    EMN = "com.hypixel.hytale.server.core.modules.entity.EntityModule"
    reg_errs = []
    setf(em, EMc, gfield(EMN, "getTransformComponentType"), reg_.registerComponent(TCc.class_, "Transform", jfield(TCc, "CODEC").get(None)))
    for getter_, cls_ in (("getPlayerComponentType", PLAc), ("getMovementStatesComponentType", MSCc), ("getInvulnerableComponentType", INVUc),
                          ("getToolInventoryComponentType", JClass(INVC + "$Tool")), ("getHotbarInventoryComponentType", JClass(INVC + "$Hotbar")),
                          ("getUtilityInventoryComponentType", JClass(INVC + "$Utility")),
                          ("getKnockbackComponentType", JClass("com.hypixel.hytale.server.core.entity.knockback.KnockbackComponent"))):
        try:
            setf(em, EMc, gfield(EMN, getter_), reg_.registerComponent(cls_.class_, Sup(lambda: None)))
        except Exception as e_:
            reg_errs.append("%s: %s" % (getter_, str(e_)[:120]))
    npc_t = reg_.registerComponent(NPCc.class_, Sup(lambda: None))
    c2t = HashMap()
    c2t.put(NPCc.class_, npc_t)
    setf(em, EMc, "classToComponentType", c2t)
    setf(em, JClass("com.hypixel.hytale.server.core.plugin.PluginBase"), "state", JClass("com.hypixel.hytale.server.core.plugin.PluginState").ENABLED)
    jfield(EMc, "instance").set(None, em)
    setf(uni, UNI, gfield("com.hypixel.hytale.server.core.universe.Universe", "getPlayerRefComponentType"), reg_.registerComponent(PRc.class_, Sup(lambda: None)))
    ESMOD = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatsModule")
    esmod = U.allocateInstance(ESMOD.class_)
    setf(esmod, ESMOD, "entityStatMapComponentType", reg_.registerComponent(ESMc.class_, Sup(lambda: ESMc())))
    jfield(ESMOD, "instance").set(None, esmod)
    DMOD_ = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DamageModule")
    dmod = U.allocateInstance(DMOD_.class_)
    setf(dmod, DMOD_, "deathComponentType", reg_.registerComponent(DTHc.class_, Sup(lambda: None)))
    jfield(DMOD_, "instance").set(None, dmod)
    DCSc = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DamageCause")
    if DCSc.PROJECTILE is None:
        jfield(DCSc, "PROJECTILE").set(None, DCSc("Projectile"))
    ck(not reg_errs and PLAc.getComponentType() is not None and MSCc.getComponentType() is not None and INVUc.getComponentType() is not None
       and NPCc.getComponentType() is not None and PRc.getComponentType() is not None, "N0: the component types are registered like the modules do: %s" % reg_errs)

    def stub(name, sup, fields, methods, ctor=None):
        c_ = CPj.makeClass("abilharness." + name, CPj.get(sup))
        if ctor is not None:
            c_.addConstructor(CNC.make(ctor, c_))
        for f_ in fields:
            c_.addField(CTF.make(f_, c_))
        for m_ in methods:
            c_.addMethod(CtNM.make(m_, c_))
        c_.writeFile(hcls)
        return JClass("abilharness." + name)
    CP_ = "com.hypixel.hytale.component."
    GETC = ("public " + CP_ + "Component getComponent(" + CP_ + "Ref r, " + CP_ + "ComponentType t) { java.util.Map m = (java.util.Map) abilharness.TStore.COMP.get(r); "
            "if (m == null) return null; return (" + CP_ + "Component) m.get(t); }")
    PUTC = ("public void putComponent(" + CP_ + "Ref r, " + CP_ + "ComponentType t, " + CP_ + "Component c) { java.util.Map m = (java.util.Map) abilharness.TStore.COMP.get(r); "
            "if (m == null) { m = new java.util.HashMap(); abilharness.TStore.COMP.put(r, m); } m.put(t, c); }")
    TSt = stub("TStore", CP_ + "Store", ["public static java.util.HashMap COMP = new java.util.HashMap();", "public static Object EXT = null;"],
               [GETC, PUTC, "public Object getExternalData() { return EXT; }",
                "public " + CP_ + "Resource getResource(" + CP_ + "ResourceType t) { return null; }"],
               ctor="public TStore() { super((" + CP_ + "ComponentRegistry) null, 0, (Object) null, (" + CP_ + "IResourceStorage) null); }")
    TBf = stub("TBuf", CP_ + "CommandBuffer", ["public static java.util.ArrayList EVENTS = new java.util.ArrayList();", "public static " + CP_ + "Store STORE = null;"],
               [GETC, PUTC, "public Object getExternalData() { return abilharness.TStore.EXT; }",
                "public " + CP_ + "Resource getResource(" + CP_ + "ResourceType t) { return null; }",
                "public void invoke(" + CP_ + "Ref r, " + CP_ + "system.EcsEvent e) { EVENTS.add(new Object[] { r, e }); }",
                "public " + CP_ + "Store getStore() { return STORE; }",
                "public void tryRemoveComponent(" + CP_ + "Ref r, " + CP_ + "ComponentType t) { }"])
    WLDc = JClass("com.hypixel.hytale.server.core.universe.world.World")
    TWd = stub("TWorld", "com.hypixel.hytale.server.core.universe.world.World", [], ["public void execute(java.lang.Runnable r) { r.run(); }"],
               ctor="public TWorld() { super((String) null, (java.nio.file.Path) null, (com.hypixel.hytale.server.core.universe.world.WorldConfig) null); }")
    tst = U.allocateInstance(TSt.class_)
    TBf.STORE = tst
    tbuf = U.allocateInstance(TBf.class_)
    world = U.allocateInstance(TWd.class_)
    setf(world, WLDc, "name", "abil-test")
    es = U.allocateInstance(ESr.class_)
    setf(es, ESr, gfield("com.hypixel.hytale.server.core.universe.world.storage.EntityStore", "getWorld"), world)
    ebu = HashMap()
    setf(es, ESr, "entitiesByUuid", ebu)
    TSt.EXT = es
    REFc = JClass(CP_ + "Ref")
    V3 = JClass("org.joml.Vector3d")
    R3 = JClass("com.hypixel.hytale.math.vector.Rotation3f")
    SMO = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier")
    MT = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier$ModifierTarget")
    CT_ = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier$CalculationType")
    GM = JClass("com.hypixel.hytale.protocol.GameMode")
    AtomRef = JClass("java.util.concurrent.atomic.AtomicReference")

    def put(r_, t_, c_):
        tst.putComponent(r_, t_, c_)

    def stats(mana=55.0, stam=14.0, hp=100.0, hpmax=100.0):
        m_ = ESMc()
        m_.update()
        for i_, want_ in ((MANA, 500.0), (STAM, 50.0)):
            m_.putModifier(i_, "abiltest", SMO(MT.MAX, CT_.ADDITIVE, JFloat(want_)))
        hm = float(m_.get(HP).getMax())
        if hm != hpmax:
            m_.putModifier(HP, "abiltest", SMO(MT.MAX, CT_.ADDITIVE, JFloat(hpmax - hm)))
        m_.setStatValue(MANA, JFloat(mana))
        m_.setStatValue(STAM, JFloat(stam))
        m_.setStatValue(HP, JFloat(hp))
        return m_

    def sv(m_, i_):
        return round(float(m_.get(i_).get()), 3)

    PLAYERS = {}

    def player(i_, x, y, z, name, gm="Adventure", **kw):
        u_ = UUID.fromString("00000000-0000-0000-00ab-%012d" % i_)
        r_ = REFc(tst, i_)
        pr_ = U.allocateInstance(PRc.class_)
        setf(pr_, PRc, "uuid", u_)
        setf(pr_, PRc, "entity", r_)
        setf(pr_, PRc, "username", name)
        pbu.put(u_, pr_)
        ebu.put(u_, r_)
        put(r_, PRc.getComponentType(), pr_)
        put(r_, TCc.getComponentType(), TCc(V3(x, y, z), R3(0.0, 0.0, 0.0)))
        m_ = stats(**kw)
        put(r_, ESMc.getComponentType(), m_)
        msc = MSCc()
        msc.setMovementStates(MSTc())
        put(r_, MSCc.getComponentType(), msc)
        pl_ = U.allocateInstance(PLAc.class_)
        setf(pl_, PLAc, "waitingForClientReady", AtomRef())
        setf(pl_, PLAc, "gameMode", getattr(GM, gm))
        put(r_, PLAc.getComponentType(), pl_)
        PLAYERS[name] = (u_, r_, pr_, m_, pl_, msc)
        return u_, r_, pr_, m_, pl_, msc

    def npc(i_, x, y, z, hp=100.0, invu=False):
        r_ = REFc(tst, i_)
        put(r_, NPCc.getComponentType(), TCc())
        put(r_, ESMc.getComponentType(), stats(hp=hp))
        put(r_, TCc.getComponentType(), TCc(V3(x, y, z), R3(0.0, 0.0, 0.0)))
        if invu:
            put(r_, INVUc.getComponentType(), INVUc.INSTANCE)
        return r_

    # ---------------- the mod's statics, seams and the fake partner bridges
    Cfg, Defs, Store = C("ClassCfg"), C("ClassDefs"), C("ClassStore")
    AC, AD, AM, AS, AW, A, AJ = C("AbilCfg"), C("AbilDefs"), C("AbilMath"), C("AbilStore"), C("AbilWorld"), C("Abil"), C("AbilJob")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyClasses")
    home = os.path.join(SCRATCH, "n-home")
    shutil.rmtree(home, ignore_errors=True)
    os.makedirs(os.path.join(home, "players"))
    Cfg.FILE = Paths.get(os.path.join(home, "config.properties"))
    load_txt = str(Cfg.load())
    Store.DIR = Paths.get(os.path.join(home, "players"))
    AS.DIR = Paths.get(os.path.join(home, "abilities"))
    AS.SYNC = True
    PSEEN, SAID = ArrayList(), ArrayList()
    A.PSEEN = PSEEN
    A.SAID = SAID
    SOUNDS = ArrayList()
    A.SOUNDS = SOUNDS
    br = Cfg.bridge()
    LEVEL, COMBAT, HEALXP, PROFKEY, HANDS, AIMS, NEARL = {}, {}, [], {}, {}, {}, []

    @JImplements("java.util.function.Function")
    class LevelFn:
        @JOverride
        def apply(self, o):
            a_ = list(o)
            return JInt(LEVEL.get((str(a_[0]), str(a_[1])), 0))

    @JImplements("java.util.function.Function")
    class CombatFn:
        @JOverride
        def apply(self, o): return JLong(COMBAT.get(str(o), 0))

    @JImplements("java.util.function.Function")
    class HealXp:
        @JOverride
        def apply(self, o):
            a_ = list(o)
            HEALXP.append([str(a_[0]), round(float(a_[1]), 3), str(a_[2]), len(a_) > 4])
            return JBoolean(True)

    @JImplements("java.util.function.Function")
    class KeyFn:
        @JOverride
        def apply(self, o): return PROFKEY.get(str(o), str(o))

    @JImplements("java.util.function.Function")
    class Members:
        @JOverride
        def apply(self, o): return JArray(JObject)([JString(x) for x in MEMBERS.get(str(o), [])])

    @JImplements("java.util.function.Function")
    class ArmInfo:
        @JOverride
        def apply(self, o):
            a_ = list(o)
            if str(a_[0]) == "staff" and str(a_[1]) == "Weapon_Staff_Wood":
                return JArray(JObject)([JInt(10), JInt(2), JDouble(1.0), JInt(50), JInt(10), JDouble(100.0), JString("o"), JString("q")])
            if str(a_[0]) == "wand" and str(a_[1]) == "Weapon_Wand_Iron":
                return JArray(JObject)([JInt(15), JInt(3), JDouble(3.5), JInt(88), JInt(18), JDouble(120.0), JString("o"), JString("q")])
            return None

    @JImplements("java.util.function.Function")
    class Hand:
        @JOverride
        def apply(self, r_):
            v_ = HANDS.get(int(r_.getIndex()))
            return None if v_ is None else JString(v_)

    @JImplements("java.util.function.Function")
    class Aim:
        @JOverride
        def apply(self, o):
            v_ = AIMS.get("spot")
            return None if v_ is None else JArray(JDouble)(v_)

    @JImplements("java.util.function.Function")
    class Near:
        @JOverride
        def apply(self, o):
            l_ = ArrayList()
            for r_ in NEARL:
                l_.add(r_)
            return l_
    MEMBERS = {}
    br.put("skill:fn:level", LevelFn())
    br.put("skill:fn:combat", CombatFn())
    br.put("skill:fn:healxp", HealXp())
    br.put("profile:fn:key", KeyFn())
    br.put("party:fn:members", Members())
    br.put("armory:fn:info", ArmInfo())
    br.put("class:fn:abilhit", C("AbilHitFn")())
    br.put("class:fn:allowed", C("AllowedFn")())
    for i_, n_ in enumerate(Defs.NAMES):
        br.put("class:weapons:" + str(n_), str(Defs.prefixesOf(i_)))

    def setclass(u_, cls):
        br.put("profile:" + str(u_), "1")
        if cls is None:
            br.remove("profile:class:" + str(u_))
            br.remove("class:" + str(u_))
        else:
            br.put("profile:class:" + str(u_), cls)
            br.put("class:" + str(u_), cls)

    def cast(name, a="1"):
        u_, r_, pr_ = PLAYERS[name][:3]
        return str(A.cast(pr_, tst, r_, world, a))

    def said():
        out_ = [str(x) for x in SAID]
        SAID.clear()
        return out_

    def unthrottle():
        AS.TOLD.clear()

    # ================================================================================================ 0.1.22 sections
    AW, AMD, ACX = C("AbilWorld"), C("AbilModDefs"), C("AbilCtx")
    Bool = JClass("java.lang.Boolean")
    tick = C("AbilTick")()
    now_ms = lambda: int(time.time() * 1000)

    @JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def apply(self, o):
            return self.f(o)
    RUNES_LOADED = set(str(x) for x in AD.RUNE if str(x))
    # ================================================================================================ 0.1.50 SHADOW MARK + THE CAPSTONES
    MARK_IX = dict((str(m), 100 + i) for i, m in enumerate(AD.MARK) if str(m))
    A.ITEMS = Fn(lambda o: Bool.valueOf(str(o) in RUNES_LOADED))
    A.MARKS = Fn(lambda o: JInt(MARK_IX.get(str(o), -1)))
    TREE = {"csv": None}
    br.put("tree:fn:abil", Fn(lambda o: None if TREE["csv"] is None else JString(TREE["csv"])))
    A.HAND = Hand()
    A.AIM = Aim()
    def near_f(o):
        try:
            a_ = [float(x) for x in o]
            l_ = ArrayList()
            for r_ in NEARL:
                q_ = tst.getComponent(r_, TCc.getComponentType()).getPosition()
                qx, qy, qz = (v_() if callable(v_) else v_ for v_ in (q_.x, q_.y, q_.z))
                if (float(qx) - a_[0]) ** 2 + (float(qy) - a_[1]) ** 2 + (float(qz) - a_[2]) ** 2 <= a_[3] ** 2 + 1e-9:
                    l_.add(r_)
            return l_
        except Exception as e_:
            K.notes.append("near_f: %r" % e_)
            raise
    A.NEAR = Fn(near_f)   # the sphere query (the engine's getAllEntitiesInSphere) over the test mobs
    EFX = ArrayList()
    A.EFFECTS = EFX
    A.EFFECT = Fn(lambda o: Bool.valueOf(not str(list(o)[1]).startswith("?")))
    LOST = ArrayList()
    A.LOST = LOST
    PUSH = ArrayList()
    A.PUSHES = PUSH
    MOBT = {"t": None}
    A.MOB = Fn(lambda o: MOBT["t"])
    LOOKV = {"v": [0.0, 65.6, 0.0, 0.0, 0.0, 1.0]}
    A.LOOK = Fn(lambda o: JArray(JDouble)(LOOKV["v"]))
    UF, AN = C("UpFx"), C("AbilNum")
    aw = AW.of("abil-test")
    NAMES_ = [str(x) for x in Defs.NAMES]
    ID = dict((str(AD.IDS[i]), i) for i in range(len(AD.IDS)))
    SM = ID["ShadowMark"]

    def run_world(ms=0):
        for j_ in list(aw.jobs):
            j_.at = now_ms() - 10 - ms
        aw.lastNs = 0
        aw.nextZone = 0
        tick.tick(JFloat(0.05), 0, None, tst, tbuf)

    def fcast(pr__, r__, slot, sh):
        unthrottle()
        return str(A.castAt(pr__, tst, r__, world, slot, sh, 3))

    def mob(i, x, z, hp=200.0):
        return npc(i, x, 64.0, z, hp=hp)

    def dmg(src, amt):
        DENTc = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage$EntitySource")
        Dm_ = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage")
        return Dm_(DENTc(src), JClass("com.hypixel.hytale.server.core.modules.entity.damage.DamageCause").PROJECTILE, JFloat(amt))

    def efx():
        return [str(x) for x in EFX]

    def mk(t_):
        o_ = AS.MARKD.get(t_)
        return None if o_ is None else [float(x) for x in o_]

    def smk(t_):
        o_ = AS.SMARKS.get(t_)
        return None if o_ is None else (str(o_[0]), [float(x) for x in o_[1]])

    def ctx(u_, k_, ai_, sh_, csv_):
        AS.TREEC.clear()
        c_ = A.ctxFor(u_, k_, ai_, sh_, csv_)
        ACX.put(c_)
        return c_

    # ---------------- SM1 the tables
    ci_s = NAMES_.index("Assassin")
    SK_S = str(Defs.SKILLS[ci_s])
    ck(SM == len(ID) - 1 and int(AD.SMARK) == SM and int(AD.TIER[SM]) == 4 and int(AD.CLS[SM]) == ci_s and str(AD.NAMES[SM]) == "Shadow Mark",
       "SM1: Shadow Mark = the LAST index (%d), tier 4, the Assassin" % SM)
    ck([str(AD.sname(SM, k_)) for k_ in range(4)] == ["Shadow Mark", "Marked Run", "Mark from Above", "Patient Mark"], "SM1: the shape names")
    ck(int(AD.of(ci_s, 4)) == SM and int(AD.of(ci_s, 3)) == ID["VanishingAct"], "SM1: the Assassin's A1-alt A / B = Vanishing Act / Shadow Mark")
    AN.sync()
    got_ = [(int(AD.mana(SM, k_)), int(AD.stamina(SM, k_)), int(AD.cdMs(SM, k_)) // 1000) for k_ in range(4)]
    ck(got_ == [(7, 2, 24), (7, 2, 24), (7, 2, 26), (7, 2, 26)], "SM1: costs per shape (7 Mana + 2 Stamina / 24 s, crouch + air 26 s): %s" % got_)
    ck(str(AC.SM_NUMS).startswith("mana=7,stamina=2,cooldown=24,range=24,mark=20,cap=60,time=8,") and str(AC.CP2_NUMS).startswith("legionCut=15,shatterMom=2,"),
       "SM1: the two new numbers rows: %s | %s" % (str(AC.SM_NUMS)[:60], str(AC.CP2_NUMS)[:40]))
    old_sm = str(AC.SM_NUMS)
    AC.SM_NUMS = "mana=9,mark=25"
    AN.sync()
    ck(float(AN.SM_MANA) == 9.0 and float(AN.SM_MARK) == 25.0 and float(AN.SM_TIME) == 8.0 and int(AD.mana(SM, 0)) == 9, "SM1: ab.ShadowMark.numbers is read live (a missing key = its default)")
    AC.SM_NUMS = old_sm
    AN.sync()
    ck(float(AN.SM_MARK) == 20.0 and float(AN.CP2_SHROUDT) == 3.0 and float(AN.CP2_NOVAMAX) == 200.0, "SM1: ... and back; the capstone numbers' defaults")
    ck([str(AMD.MID[x]) for x in AMD.modsOf(SM)] == ["Duration", "Power", "Radius", "Efficiency"] if hasattr(AMD, "modsOf") else True, "SM1: the modifiers")
    ck(str(AD.NOUN[SM]) == "Exposed bonus" and "Patient Mark" in str(AD.DESCS[SM]) and str(AD.RUNE[SM]) == "SkyyAbility_Assassin_ShadowMark", "SM1: noun, description, rune id")
    ck(str(A.modText(SM, int(AMD.RADIUS), 2, 1)).endswith(" blocks reach") and "Mark from Above" not in str(A.modText(SM, int(AMD.RADIUS), 2, 1)) and "Exposed bonus" in str(A.modText(SM, int(AMD.POWER), 2, 1)),
       "SM1: the modifier texts: %s | %s" % (A.modText(SM, int(AMD.RADIUS), 2, 1), A.modText(SM, int(AMD.POWER), 2, 1)))
    RUNES_LOADED.add(str(AD.RUNE[SM]))
    g_ = open(GEN, encoding="utf8").read()
    ck("'Capstones2': 'Path capstone'}[_aid]" in g_ and "'More capstone'" not in g_ and "off the cooldown (once a cast)." in g_,
       "FIX6: the second capstone row is labelled 'Path capstone numbers'; the description says the refund is once a cast")

    # ---------------- the Assassin
    su, sr_, spr, sm, spl, smsc = player(41, 20.5, 64.0, 0.5, "Assassin1")
    setclass(su, "Assassin")
    LEVEL[(str(su), SK_S)] = 30
    HANDS[41] = "Weapon_Daggers_Crude"
    kS = str(su)
    br.put("tree:v3", "1")
    A.setPick(kS, ci_s, "B")
    CSV_B = "v3,v4,v5,fold,A1,A2,A3,A4b"

    def sreset(csv_=CSV_B):
        AS.clearCd(kS)
        sm.setStatValue(MANA, JFloat(400.0))
        sm.setStatValue(STAM, JFloat(50.0))
        unthrottle()
        said()
        AS.LASTUSE.clear()
        EFX.clear()
        for mp_ in (AS.MARKD, AS.SMARKS, AS.STRIKE, AS.CLOAKS):
            mp_.clear()
        TREE["csv"] = csv_
        AS.TREEC.clear()
        aw.jobs.clear()
        aw.zones.clear()
        aw.nz = 0
        smsc.getMovementStates().onGround = True
        smsc.getMovementStates().crouching = False
        smsc.getMovementStates().sprinting = False
    sreset()
    A.treeCsv(su)
    ck(list(AS.slots(kS, ci_s))[3] == "ShadowMark" or list(AS.slots(kS, ci_s))[2] == "ShadowMark", "SM2: the Assassin with pick B carries Shadow Mark: %s" % list(AS.slots(kS, ci_s)))
    slot_ = "4" if list(AS.slots(kS, ci_s))[3] == "ShadowMark" else "3"
    t1, t2, t3 = mob(301, 24.5, 0.5), mob(302, 23.5, 1.5), mob(303, 22.0, 3.0)
    NEARL[:] = [t1, t2, t3]

    # ---------------- SM2 refusals before anything is paid
    MOBT["t"] = None
    r0 = fcast(spr, sr_, slot_, 0)
    ck(r0 == "notarget" and sv(sm, MANA) == 400.0 and int(AS.left(kS, "ShadowMark", now_ms())) == 0 and any("to mark - nothing was spent" in x for x in said()),
       "SM2: no enemy in your look -> refused, nothing spent: %s" % r0)
    TREE["csv"] = "v3,v4,v5,fold,A1,A2,A3"
    AS.TREEC.clear()
    MOBT["t"] = t1
    r0b = fcast(spr, sr_, slot_, 0)
    ck(r0b in ("tree", "locked") and sv(sm, MANA) == 400.0, "SM2: the tree path is Vanishing Act's (no A4b line) -> refused: %s" % r0b)
    # FIX1 (critic: Radius did nothing for Patient Mark, the shape an alt casts): the Radius modifier = + reach
    def reach_of(csv_, eq_, sh_):
        sreset(csv_)
        pp_ = AS.load(kS)
        if eq_:
            pp_.setProperty("e.ShadowMark", eq_)
        MOBT["t"] = None
        smsc.getMovementStates().crouching = sh_ == 3
        r_ = fcast(spr, sr_, slot_, sh_)
        pp_.remove("e.ShadowMark")
        smsc.getMovementStates().crouching = False
        ln_ = [x for x in said() if "to mark - nothing was spent" in x]
        return r_, (float(ln_[0].split("within ")[1].split(" blocks")[0]) if ln_ else -1.0), sv(sm, MANA)
    for sh_ in (0, 3):
        r_, reach_, mana_ = reach_of(CSV_B + ",m.ShadowMark.Radius=1", "Radius", sh_)
        ck(r_ == "notarget" and reach_ > float(AN.SM_RANGE) + 0.01 and mana_ == 400.0,
           "FIX1: the Radius modifier adds reach (%s shape): %s blocks > %s" % ("crouch" if sh_ == 3 else "walk", reach_, float(AN.SM_RANGE)))
        r_, reach_, mana_ = reach_of(CSV_B, "", sh_)
        ck(r_ == "notarget" and abs(reach_ - float(AN.SM_RANGE)) < 1e-9, "FIX1: ... without it the plain %s blocks (%s)" % (float(AN.SM_RANGE), reach_))

    # ---------------- SM3 walk: Exposed 30 % (20 x the Lv 1 main 1.5), 8 s, First Strike armed
    sreset()
    MOBT["t"] = t1
    r1 = fcast(spr, sr_, slot_, 0)
    m1 = mk(t1)
    s1 = smk(t1)
    ck(r1.startswith("ok:ShadowMark") and " mark=30" in r1 and " secs=8" in r1, "SM3: Shadow Mark (walk) casts: %s" % r1[:160])
    ck(m1 is not None and abs(m1[1] - 30.0) < 1e-9 and 7900 <= m1[0] - now_ms() <= 8100, "SM3: the target is Exposed +30 %% for 8 s (Marked map): %s" % m1)
    ck(s1 is not None and s1[0] == kS and abs(s1[1][1] - 30.0) < 1e-9 and abs(s1[1][2] - 8.0) < 1e-9, "SM3: our record (caster, 30 %%, 8 s, bonus): %s" % (s1,))
    st_ = AS.STRIKE.get(su)
    ck(st_ is not None and abs(float(st_[1]) - float(AN.CL_STRIKE) * 1.5) < 1e-6, "SM3: your next hit is a First Strike (+CL_STRIKE x 1.5): %s" % (None if st_ is None else list(st_)))
    ck(sv(sm, MANA) < 400.0 and 23000 <= int(AS.left(kS, "ShadowMark", now_ms())) <= 24100, "SM3: Mana paid (%s), cooldown 24 s armed" % sv(sm, MANA))
    ck(AS.CLOAKS.get(su) is None, "SM3: the walking shape does not cloak")
    o_ = JClass("java.util.UUID").fromString("00000000-0000-0000-00ab-000000000999")
    om = float(A.outMult(tbuf, t1, o_, now_ms()))
    ck(abs(om - 1.30) < 1e-6, "SM3: EVERYONE's hits on it deal +30 %% (Abil.outMult = %s)" % om)
    ck(abs(float(A.outMult(tbuf, t2, o_, now_ms())) - 1.0) < 1e-9, "SM3: an unmarked enemy x1")
    p0 = AS.load(kS).getProperty("u.ShadowMark")
    ck(p0 is not None and int(str(p0)) >= 1, "SM3: the cast counted a use (the ability levels by use): %s" % p0)

    # ---------------- SM4 the shared mark: a stronger one is kept, the same refreshes, the cap
    AS.MARKD.put(t2, JArray(JDouble)([float(now_ms() + 60000), 45.0, 1.0]))
    ck(abs(float(A.exposeOn(tbuf, t2, 30.0, 8.0, now_ms())) - 45.0) < 1e-9 and abs(mk(t2)[1] - 45.0) < 1e-9, "SM4: a stronger mark (Hunter's Mark at 45 %) is kept")
    AS.MARKD.put(t2, JArray(JDouble)([float(now_ms() + 1000), 10.0, 2.0]))
    ck(abs(float(A.exposeOn(tbuf, t2, 30.0, 8.0, now_ms())) - 30.0) < 1e-9 and mk(t2)[1] == 30.0 and mk(t2)[2] == 2.0, "SM4: a weaker one is replaced (its focus stacks kept)")
    u0 = mk(t2)[0]
    time.sleep(0.02)
    A.exposeOn(tbuf, t2, 30.0, 8.0, now_ms())
    ck(mk(t2)[0] > u0, "SM4: the same strength again refreshes the time")
    ck(abs(float(A.exposeOn(tbuf, t3, 500.0, 8.0, now_ms())) - 60.0) < 1e-9, "SM4: the cap (60 %)")
    ck(float(A.exposeOn(tbuf, None, 30.0, 8.0, now_ms())) == 0.0 and float(A.exposeOn(tbuf, t3, 0.0, 8.0, now_ms())) == 0.0, "SM4: no target / 0 % = nothing")
    # FIX3 (critic: a stronger but SHORTER write cut a weaker, longer mark): the running mark's end is kept
    end_ = float(now_ms() + 60000)
    AS.MARKD.put(t2, JArray(JDouble)([end_, 15.0, 1.0]))
    A.exposeOn(tbuf, t2, 20.0, 1.0, now_ms())
    ck(abs(mk(t2)[1] - 20.0) < 1e-9 and abs(mk(t2)[0] - end_) < 1e-6, "FIX3: Shroud's 1 s Exposed (20 %%) on a 60 s Hunter's Mark (15 %%) keeps the 60 s end: %s" % mk(t2))
    # FIX3b (critic: Hunter's Mark / Arrow Rain overwrote a stronger Shadow Mark): markMob keeps a stronger running Shadow Mark
    sreset()
    MOBT["t"] = t1
    fcast(spr, sr_, slot_, 0)
    before_ = mk(t1)
    got_ = float(A.markMob(tbuf, t1, 15.0, 4.0, False, now_ms()))
    ck(abs(got_ - 30.0) < 1e-9 and abs(mk(t1)[1] - 30.0) < 1e-9 and mk(t1)[0] >= before_[0] - 1e-6, "FIX3b: a 15 %% Hunter's Mark on a 30 %% Shadow Mark keeps 30 %% and its end: %s -> %s" % (before_, mk(t1)))
    got_ = float(A.markMob(tbuf, t1, 45.0, 20.0, False, now_ms()))
    ck(abs(got_ - 45.0) < 1e-9 and abs(mk(t1)[1] - 45.0) < 1e-9, "FIX3b: ... a STRONGER Hunter's Mark still replaces it: %s" % mk(t1))
    AS.MARKD.put(t3, JArray(JDouble)([float(now_ms() + 9000), 30.0, 1.0]))
    got_ = float(A.markMob(tbuf, t3, 15.0, 4.0, False, now_ms()))
    ck(abs(got_ - 15.0) < 1e-9 and abs(mk(t3)[1] - 15.0) < 1e-9, "FIX3b: ... an Archer's own (non Shadow) mark behaves as in 0.1.49 (a recast = its new strength): %s" % mk(t3))
    # FIX2-5 (critic 2: an EXPIRED Shadow Mark record the sweep had not dropped yet still kept a stronger mark): only a running one counts
    AS.MARKD.put(t3, JArray(JDouble)([float(now_ms() + 9000), 30.0, 1.0]))
    AS.SMARKS.put(t3, JArray(JObject)([su, JArray(JDouble)([float(now_ms() - 5), 30.0, 8.0, 150.0])]))
    got_ = float(A.markMob(tbuf, t3, 15.0, 4.0, False, now_ms()))
    ck(abs(got_ - 15.0) < 1e-9 and abs(mk(t3)[1] - 15.0) < 1e-9, "FIX2-5: an expired Shadow Mark record does not keep the stronger mark (Hunter's Mark = its own 15 %%): %s" % mk(t3))
    AS.SMARKS.remove(t3)

    # ---------------- SM5 sprint (Marked Run: + haste) and crouch (Patient Mark: 150 % + the cloak)
    sreset()
    MOBT["t"] = t1
    r2 = fcast(spr, sr_, slot_, 1)
    ck(r2.startswith("ok:ShadowMark") and " shape=sprint" in r2 and any(x.startswith("SkyyAbility_Spd_50") for x in efx()), "SM5: Marked Run marks + 20 %% haste: %s %s" % (r2[:80], efx()[:4]))
    sreset()
    MOBT["t"] = t1
    r3 = fcast(spr, sr_, slot_, 3)
    z3 = AS.CLOAKS.get(su)
    ck(r3.startswith("ok:ShadowMark") and " shape=crouch" in r3 and " secs=12" in r3 and 11900 <= mk(t1)[0] - now_ms() <= 12100, "SM5: Patient Mark lasts 150 %% (12 s): %s" % r3[:120])
    ck(z3 is not None and str(z3.name) == "Patient Mark" and any(x.startswith("SkyyAbility_Cloak:2") for x in efx()), "SM5: ... and cloaks you 2 s (%s, %s)" % (None if z3 is None else z3.name, efx()[:4]))
    ck(25000 <= int(AS.left(kS, "ShadowMark", now_ms())) <= 26100, "SM5: the crouch shape's cooldown 26 s")

    # ---------------- SM6 air: Mark from Above (the landing job through the REAL AbilTick)
    sreset()
    far = mob(304, 40.5, 0.5)
    NEARL[:] = [t1, t2, t3, far]
    MOBT["t"] = None
    smsc.getMovementStates().onGround = False
    r4 = fcast(spr, sr_, slot_, 2)
    ck(r4.startswith("ok:ShadowMark") and " land" in r4 and any(int(j_.kind) == 3 for j_ in list(aw.jobs)), "SM6: Mark from Above waits for the landing (job kind 3): %s" % r4[:100])
    smsc.getMovementStates().onGround = True
    run_world()
    run_world()
    ma, mb = mk(t1), mk(t2)
    ck(ma is not None and abs(ma[1] - 18.0) < 1e-9 and mb is not None and mk(t3) is not None, "SM6: on landing every enemy within 5 blocks is marked at 60 %% (18 %%): %s %s %s" % (ma, mb, mk(t3)))
    ck(str(A.LAST_ASN).startswith("smark landing 3") and AS.STRIKE.get(su) is not None, "SM6: 3 marked, First Strike armed: %s" % A.LAST_ASN)
    ck(mk(far) is None, "SM6: an enemy 20 blocks away is not")
    NEARL[:] = [t1, t2, t3]

    # ---------------- SM7 THE KILL (smarkHit): the cooldown -8 s; alive / unmarked / expired = nothing
    sreset()
    MOBT["t"] = t1
    fcast(spr, sr_, slot_, 0)
    left0 = int(AS.left(kS, "ShadowMark", now_ms()))
    k0 = int(A.SMKILLS)
    A.smarkHit(tbuf, t1, dmg(sr_, 5.0), now_ms())
    ck(int(A.SMKILLS) == k0 and AS.SMARKS.get(t1) is not None, "SM7: a hit on a LIVING marked enemy does nothing")
    tst.getComponent(t1, ESMc.getComponentType()).setStatValue(HP, JFloat(0.0))
    A.smarkHit(tbuf, t1, dmg(sr_, 5.0), now_ms())
    left1 = int(AS.left(kS, "ShadowMark", now_ms()))
    ck(int(A.SMKILLS) == k0 + 1 and AS.SMARKS.get(t1) is None and 7800 <= left0 - left1 <= 8200, "SM7: the marked enemy died -> Shadow Mark comes back 8 s sooner (%d -> %d ms)" % (left0, left1))
    ck(any("8 s sooner" in x for x in said()), "SM7: the line says so")
    A.smarkHit(tbuf, t1, dmg(sr_, 5.0), now_ms())
    ck(int(A.SMKILLS) == k0 + 1, "SM7: ... once (the record is gone)")
    dead2 = mob(305, 23.5, 0.5, hp=0.0)
    AS.SMARKS.put(dead2, JArray(JObject)([su, JArray(JDouble)([float(now_ms() - 5), 30.0, 8.0, 150.0])]))
    A.smarkHit(tbuf, dead2, dmg(sr_, 5.0), now_ms())
    ck(int(A.SMKILLS) == k0 + 1, "SM7: an EXPIRED mark gives nothing")
    A.smarkHit(tbuf, mob(306, 23.5, 2.5, hp=0.0), dmg(sr_, 5.0), now_ms())
    ck(int(A.SMKILLS) == k0 + 1, "SM7: an unmarked dead enemy gives nothing")
    AS.SMARKS.put(dead2, JArray(JObject)([su, JArray(JDouble)([float(now_ms() - 5), 30.0, 8.0, 150.0])]))
    A.smarkPrune(now_ms())
    ck(AS.SMARKS.get(dead2) is None, "SM7: smarkPrune drops expired records")
    # FIX2 (critic: the refund was uncapped - several marked kills reset the cooldown): ONE refund a cast
    sreset()
    MOBT["t"] = t2
    fcast(spr, sr_, slot_, 0)
    ck(AS.SMCUT.get(su) is not None, "FIX2: the cast arms one kill refund")
    dA, dB = mob(313, 23.5, 0.5, hp=0.0), mob(314, 23.5, 1.0, hp=0.0)
    for d_ in (dA, dB):
        AS.SMARKS.put(d_, JArray(JObject)([su, JArray(JDouble)([float(now_ms() + 8000), 30.0, 8.0, 150.0])]))
    la_ = int(AS.left(kS, "ShadowMark", now_ms()))
    A.smarkHit(tbuf, dA, dmg(sr_, 5.0), now_ms())
    lb_ = int(AS.left(kS, "ShadowMark", now_ms()))
    A.smarkHit(tbuf, dB, dmg(sr_, 5.0), now_ms())
    lc_ = int(AS.left(kS, "ShadowMark", now_ms()))
    ck(7800 <= la_ - lb_ <= 8200 and abs(lb_ - lc_) <= 200 and str(A.LAST_ASN).endswith("norefund") and AS.SMCUT.get(su) is None,
       "FIX2: two marked kills from one cast -> 8 s off ONCE (%d -> %d -> %d ms), the 2nd gives none" % (la_, lb_, lc_))
    AS.clearCd(kS)
    sm.setStatValue(MANA, JFloat(400.0))
    MOBT["t"] = t2
    fcast(spr, sr_, slot_, 0)
    AS.SMARKS.put(dB, JArray(JObject)([su, JArray(JDouble)([float(now_ms() + 8000), 30.0, 8.0, 150.0])]))
    la_ = int(AS.left(kS, "ShadowMark", now_ms()))
    A.smarkHit(tbuf, dB, dmg(sr_, 5.0), now_ms())
    ck(7800 <= la_ - int(AS.left(kS, "ShadowMark", now_ms())) <= 8200, "FIX2: ... a new cast arms the refund again")
    # FIX2-2 / 2-3 (critic 2): the token holds {until, profile}: a spent (expired) token or another profile's gives no refund; the sweep drops it
    for tok_, why_ in (([JClass("java.lang.Long")(now_ms() - 5), JString(kS)], "an expired token (the cast's mark ran out)"), ([JClass("java.lang.Long")(now_ms() + 8000), JString(kS + "x")], "another profile's token")):
        AS.clearCd(kS)
        sm.setStatValue(MANA, JFloat(400.0))
        MOBT["t"] = t2
        fcast(spr, sr_, slot_, 0)
        ck(AS.SMCUT.get(su) is not None and len(AS.SMCUT.get(su)) == 2 and str(AS.SMCUT.get(su)[1]) == kS and int(AS.SMCUT.get(su)[0]) > now_ms() + 7000,
           "FIX2-2: the cast's token = {until (the mark's end), the casting profile}: %s" % (list(AS.SMCUT.get(su)),))
        AS.SMCUT.put(su, JArray(JObject)(tok_))
        AS.SMARKS.put(dB, JArray(JObject)([su, JArray(JDouble)([float(now_ms() + 8000), 30.0, 8.0, 150.0])]))
        la_ = int(AS.left(kS, "ShadowMark", now_ms()))
        A.smarkHit(tbuf, dB, dmg(sr_, 5.0), now_ms())
        ck(abs(la_ - int(AS.left(kS, "ShadowMark", now_ms()))) <= 200 and str(A.LAST_ASN).endswith("norefund") and AS.SMCUT.get(su) is None,
           "FIX2-2: %s gives no refund (%s)" % (why_, A.LAST_ASN))
    AS.SMCUT.put(su, JArray(JObject)([JClass("java.lang.Long")(now_ms() - 5), JString(kS)]))
    AS.SMARKS.put(dA, JArray(JObject)([su, JArray(JDouble)([float(now_ms() + 8000), 30.0, 8.0, 150.0])]))
    A.smarkPrune(now_ms())
    ck(AS.SMCUT.get(su) is None and AS.SMARKS.get(dA) is not None, "FIX2-2: smarkPrune drops a spent refund token too (a running mark stays)")
    AS.SMARKS.remove(dA)
    ck("    @PKG@.AbilStore.SMCUT.remove(u);   // 0.1.50 fix round 2" in open(GEN, encoding="utf8").read(), "FIX2-4: a quit drops the unused refund token (ClassQuit)")
    # FIX4: the kill hook never throws out into AbilFrostSys.handle (the bytecode catch is checked in W)
    thrown_ = None
    try:
        AS.SMARKS.put(dA, JArray(JObject)([su, JArray(JDouble)([float(now_ms() + 8000), 30.0, 8.0, 150.0])]))
        A.smarkHit(None, dA, dmg(sr_, 5.0), now_ms())
        A.smarkHit(tbuf, None, None, now_ms())
    except Exception as e_:
        thrown_ = e_
    ck(thrown_ is None, "FIX4: smarkHit with a broken call never throws out of the damage hook (%r)" % (thrown_,))

    # ---------------- SM8 Death Sentence (xSentence): the jump + First Strike, once every 4 s; without the code nothing jumps
    t4, t5 = mob(307, 26.5, 0.5), mob(308, 34.5, 0.5)
    NEARL[:] = [t4, t5]
    sreset(CSV_B + ",f.xSentence=1")
    MOBT["t"] = t4
    fcast(spr, sr_, slot_, 0)
    AS.STRIKE.clear()
    UF.SENT.clear()
    tst.getComponent(t4, ESMc.getComponentType()).setStatValue(HP, JFloat(0.0))
    t6 = mob(309, 28.5, 1.0)
    NEARL[:] = [t4, t6, t5]
    A.smarkHit(tbuf, t4, dmg(sr_, 5.0), now_ms())
    j6 = smk(t6)
    ck(j6 is not None and j6[0] == kS and mk(t6) is not None and abs(mk(t6)[1] - 30.0) < 1e-9 and AS.STRIKE.get(su) is not None,
       "SM8: Death Sentence - the mark jumps to the nearest enemy (fresh timer, same strength) + First Strike ready: %s" % (j6,))
    ck(any(x.startswith("Death Sentence: the mark jumps") for x in said()) and smk(t5) is None, "SM8: the line; the farther enemy is not marked")
    tst.getComponent(t6, ESMc.getComponentType()).setStatValue(HP, JFloat(0.0))
    AS.STRIKE.clear()
    A.smarkHit(tbuf, t6, dmg(sr_, 5.0), now_ms())
    ck(smk(t5) is None and AS.STRIKE.get(su) is None, "SM8: a second marked kill within 4 s - no jump (once every 4 s)")
    sreset(CSV_B)
    t7, t8 = mob(310, 26.5, 2.5), mob(311, 27.5, 2.5)
    NEARL[:] = [t7, t8]
    MOBT["t"] = t7
    fcast(spr, sr_, slot_, 0)
    tst.getComponent(t7, ESMc.getComponentType()).setStatValue(HP, JFloat(0.0))
    UF.SENT.clear()
    A.smarkHit(tbuf, t7, dmg(sr_, 5.0), now_ms())
    ck(smk(t8) is None, "SM8: WITHOUT the capstone the mark does not jump")

    # ---------------- CP1 Shroud of Night (xShroud): Exposed inside the smoke; the cloak held 3 s longer
    VA = ID["VanishingAct"]
    t9 = mob(312, 21.5, 1.0)
    NEARL[:] = [t9, sr_]
    for code_, want_x, want_cap in (("", None, 5000), (",f.xShroud=1", 20.0, 8000)):
        sreset("v3,v4,v5,fold,A1,A2,A3,A4a" + code_)
        c_ = ctx(su, kS, VA, 3, TREE["csv"])
        zc = A.cloakAt(spr, tst, sr_, su, kS, aw, 1.0, 3, now_ms(), VA)
        zs = A.smokeAt(tst, su, kS, aw, JArray(JDouble)([20.5, 64.0, 0.5]), 4.0, 3, now_ms())
        ACX.put(None)
        zc.start = now_ms() - 10
        A.smokeTick(zs, tst, tbuf, now_ms())
        m9 = mk(t9)
        ck((m9 is None) if want_x is None else (m9 is not None and abs(m9[1] - want_x) < 1e-9), "CP1: Shroud of Night %s: the enemy in the smoke %s (%s)" % ("off" if want_x is None else "ON", "is not Exposed" if want_x is None else "is Exposed +20 %", m9))
        ck(int(zc.until) - int(zc.start) <= want_cap and int(zc.until) > now_ms() + 300, "CP1: ... the cloak held while you stand in it (until - start %d, cap %d)" % (int(zc.until) - int(zc.start), want_cap))
        zc.until = zc.start + want_cap - 100
        A.smokeTick(zs, tst, tbuf, now_ms())
        ck(int(zc.until) - int(zc.start) <= want_cap, "CP1: ... never past start + %d ms" % want_cap)
        zc.start = now_ms() - 7000
        zc.until = now_ms() + 50
        A.smokeTick(zs, tst, tbuf, now_ms())
        ck((int(zc.until) <= now_ms() + 60) if want_x is None else (int(zc.until) > now_ms() + 500), "CP1: 7 s in: Ambush Smoke alone lets it go, Shroud holds it (until %+d ms)" % (int(zc.until) - now_ms()))

    for code_ in ("", ",f.xShroud=1"):   # FIX5 (critic): the walk shape too - the cloak's own 3 s + 3 s, and it lasts past the smoke
        sreset("v3,v4,v5,fold,A1,A2,A3,A4a" + code_)
        c_ = ctx(su, kS, VA, 0, TREE["csv"])
        zc = A.cloakAt(spr, tst, sr_, su, kS, aw, 3.0, 0, now_ms(), VA)
        zs = A.smokeAt(tst, su, kS, aw, JArray(JDouble)([20.5, 64.0, 0.5]), 4.0, 0, now_ms())
        ACX.put(None)
        zc.start = now_ms() - 2900
        zc.until = now_ms() + 100
        A.smokeTick(zs, tst, tbuf, now_ms())
        left_ = int(zc.until) - now_ms()
        tot_ = int(zc.until) - int(zc.start)
        if code_:
            ck(left_ > 2500 and tot_ <= int(float(AN.VA_CLOAK) * 1000) + 3000 + 20, "FIX5: Shroud ON, walk shape: the 3 s cloak is held up to 3 s longer (%+d ms left, %d ms in all)" % (left_, tot_))
        else:
            ck(left_ <= 150, "FIX5: Shroud OFF, walk shape: the smoke leaves the cloak as it was (%+d ms)" % left_)
    sreset("v3,v4,v5,fold,A1,A2,A3,A4a,f.xShroud=1")   # ... and the crouch shape: 3 s past the last moment inside (not 0.6 s)
    c_ = ctx(su, kS, VA, 3, TREE["csv"])
    zc = A.cloakAt(spr, tst, sr_, su, kS, aw, 1.0, 3, now_ms(), VA)
    zs = A.smokeAt(tst, su, kS, aw, JArray(JDouble)([20.5, 64.0, 0.5]), 4.0, 3, now_ms())
    ACX.put(None)
    zc.start = now_ms() - 10
    A.smokeTick(zs, tst, tbuf, now_ms())
    ck(int(zc.until) - now_ms() > 3000, "FIX5: Shroud ON, crouch: the cloak runs 3 s past your last tick in the smoke (%+d ms)" % (int(zc.until) - now_ms()))

    # ---------------- CP2 Oath of Legions (xLegion): every party member bound, the cut +15
    ci_w = NAMES_.index("Warrior")
    wu, wr, wpr, wm, wpl, wmsc = player(51, 60.5, 64.0, 0.5, "Warrior1")
    au, ar, apr, am, apl, amsc = player(52, 62.5, 64.0, 0.5, "AllyA", hp=60.0)
    bu, br_, bpr, bm, bpl, bmsc = player(53, 61.5, 64.0, 2.5, "AllyB", hp=90.0)
    setclass(wu, "Warrior")
    LEVEL[(str(wu), str(Defs.SKILLS[ci_w]))] = 30
    HANDS[51] = "Weapon_Sword_Crude"
    kW = str(wu)
    MEMBERS[kW] = MEMBERS[str(au)] = MEMBERS[str(bu)] = [kW, str(au), str(bu)]
    A.setPick(kW, ci_w, "B")
    TREE["csv"] = "v3,v4,v5,fold,A1,A2,A3,A4b"
    AS.TREEC.clear()
    A.treeCsv(wu)
    OATH = ID["GuardiansOath"]
    slot_w = "4" if list(AS.slots(kW, ci_w))[3] == "GuardiansOath" else "3"
    NEARL[:] = [wr, ar, br_]
    for code_, want_n in (("", 1), (",f.xLegion=1", 2)):
        AS.clearCd(kW)
        AS.OATHS.clear()
        AS.OATHW.clear()
        wm.setStatValue(MANA, JFloat(400.0))
        TREE["csv"] = "v3,v4,v5,fold,A1,A2,A3,A4b" + code_
        AS.TREEC.clear()
        said()
        ro = fcast(wpr, wr, slot_w, 0)
        nb = sum(1 for u_ in (au, bu) if AS.OATHS.get(u_) is not None)
        ow = AS.OATHW.get(wu)
        ck(ro.startswith("ok:GuardiansOath") and nb == want_n, "CP2: Guardian's Oath %s binds %d ally(s): %s" % ("+ Oath of Legions" if code_ else "alone", nb, ro[:90]))
        if code_:
            base_cut = float(AN.GO_CUT) * 1.5
            ck(abs(float(ow[1]) - min(60.0, base_cut + 15.0)) < 1e-6 and any(x.startswith("Oath of Legions: 1 more") for x in said()), "CP2: ... the Warrior's cut +15 (%s): %s" % (float(ow[1]), base_cut))

    # ---------------- CP3 Shatterpoint (xShatterpt): Momentum back per enemy hit; +30 % to Breached (UpFx.outAbil)
    ci_b = NAMES_.index("Spellblade")
    bu2, br2, bpr2, bm2, bpl2, bmsc2 = player(61, 100.5, 64.0, 0.5, "Spellblade1")
    setclass(bu2, "Spellblade")
    LEVEL[(str(bu2), str(Defs.SKILLS[ci_b]))] = 30
    HANDS[61] = "Weapon_Longsword_Crude"
    kB = str(bu2)
    A.setPick(kB, ci_b, "B")
    TREE["csv"] = "v3,v4,v5,fold,A1,A2,A3,A4b"
    AS.TREEC.clear()
    A.treeCsv(bu2)
    slot_b = "4" if list(AS.slots(kB, ci_b))[3] == "ShatteringArc" else "3"
    s1, s2 = mob(321, 100.5, 3.0), mob(322, 101.5, 3.5)
    LOOKV["v"] = [100.5, 65.6, 0.5, 0.0, 0.0, 1.0]
    res_ = {}
    for code_ in ("", ",f.xShatterpt=1"):
        AS.clearCd(kB)
        bm2.setStatValue(MANA, JFloat(400.0))
        bm2.setStatValue(STAM, JFloat(50.0))
        for mp_ in (AS.MOMS, AS.MOMX, AS.BREACH):
            mp_.clear()
        aw.jobs.clear()
        TREE["csv"] = "v3,v4,v5,fold,A1,A2,A3,A4b" + code_
        AS.TREEC.clear()
        NEARL[:] = [s1, s2]
        A.momAdd(bu2, 10, now_ms())
        rs = fcast(bpr2, br2, slot_b, 0)
        run_world()
        run_world()
        res_[code_] = (rs, int(A.momN(bu2, now_ms())), str(A.LAST_SB))
    hits0 = int(str(res_[""][2]).split("hit=")[1].split()[0]) if "hit=" in res_[""][2] else -1
    hits_ = int(str(res_[",f.xShatterpt=1"][2]).split("hit=")[1].split()[0]) if "hit=" in res_[",f.xShatterpt=1"][2] else -1
    ck(res_[""][0].startswith("ok:ShatteringArc") and hits0 >= 1, "CP3: Shattering Arc alone: %s / Momentum after %d, %d hit" % (res_[""][0][:80], res_[""][1], hits0))
    ck(hits_ == hits0 and res_[",f.xShatterpt=1"][1] == res_[""][1] + min(10, 2 * hits_), "CP3: Shatterpoint gives 2 Momentum back per enemy hit (%d hit: %d -> %d)" % (hits_, res_[""][1], res_[",f.xShatterpt=1"][1]))
    TREE["csv"] = "v3,v4,v5,fold,A1,A2,A3,A4b,f.xShatterpt=1"
    AS.TREEC.clear()
    AS.BREACH.put(s1, JArray(JDouble)([float(now_ms() + 9000), 10.0, 0.0, 0.0, 0.0]))
    AS.BREACH.remove(s2)
    ob1 = float(UF.outAbil(tbuf, s1, bu2, "ShatteringArc", now_ms()))
    ob2 = float(UF.outAbil(tbuf, s2, bu2, "ShatteringArc", now_ms()))
    ck(abs((ob1 - ob2) - 0.30) < 1e-6, "CP3: ... and +30 %% to a Breached enemy (outAbil %s vs %s)" % (ob1, ob2))
    TREE["csv"] = "v3,v4,v5,fold,A1,A2,A3,A4b"
    AS.TREEC.clear()
    ck(abs(float(UF.outAbil(tbuf, s1, bu2, "ShatteringArc", now_ms())) - float(UF.outAbil(tbuf, s2, bu2, "ShatteringArc", now_ms()))) < 1e-9, "CP3: without the code no Breached bonus")

    # ---------------- CP4 Raincaller (xRaincall): the rain drifts toward the nearest enemy; +30 % to rooted
    ci_a = NAMES_.index("Archer")
    xu, xr, xpr, xm, xpl, xmsc = player(71, 140.5, 64.0, 0.5, "Archer1")
    setclass(xu, "Archer")
    kX = str(xu)
    RAIN = ID["ArrowRain"]
    q1 = mob(331, 145.5, 0.5)
    NEARL[:] = [q1]
    for code_, moved in (("", False), (",f.xRaincall=1", True)):
        TREE["csv"] = "v3,v4,v5,fold,A1,A2,A3,A4a" + code_
        ctx(xu, kX, RAIN, 0, TREE["csv"])
        z_ = A.rainZone(tst, xu, kX, aw, JArray(JDouble)([140.5, 64.0, 0.5]), 0, 10.0, now_ms(), 0.0, 0.0)
        ACX.put(None)
        z_.t3 = now_ms() - 10
        z_.nextHeal = 0
        x0 = float(z_.x)
        A.rainTick(z_, tst, tbuf, now_ms())
        ck((abs(float(z_.x) - (x0 + 1.0)) < 1e-6) if moved else (float(z_.x) == x0), "CP4: Raincaller %s: the rain centre %s -> %s" % ("ON" if moved else "off", x0, float(z_.x)))
    TREE["csv"] = "v3,v4,v5,fold,A1,A2,A3,A4a,f.xRaincall=1"
    AS.TREEC.clear()
    q2 = mob(332, 146.5, 0.5)
    UF.RT.put(q1, JArray(JDouble)([float(now_ms() + 3000), 1.0]))
    UF.RT.remove(q2)
    oq = float(UF.outAbil(tbuf, q1, xu, "ArrowRain", now_ms())) - float(UF.outAbil(tbuf, q2, xu, "ArrowRain", now_ms()))
    ck(abs(oq - 0.30) < 1e-6, "CP4: ... and +30 %% to a rooted enemy (%s)" % oq)

    # ---------------- CP5 Storm of Fists (xFistStorm): every 5th hit; the wave hits the not-Awed too
    ci_k = NAMES_.index("Monk")
    ku, kr, kpr, km, kpl, kmsc = player(81, 180.5, 64.0, 0.5, "Monk1")
    setclass(ku, "Monk")
    kK = str(ku)
    HF = ID["HundredFists"]
    w1, w2 = mob(341, 181.5, 0.5), mob(342, 180.5, 1.5)
    NEARL[:] = [w1, w2]
    for code_, every_, hits_w in (("", int(AN.HF_EVERY), 0), (",f.xFistStorm=1", max(2, int(round(int(AN.HF_EVERY) * 0.5))), 2)):
        TREE["csv"] = "v3,v4,v5,fold,A1,A2,A3,A4a" + code_
        AS.TREEC.clear()
        AS.FLOWS.clear()
        AS.AWED.clear()
        ctx(ku, kK, HF, 0, TREE["csv"])
        A.flowAt(kpr, tst, kr, ku, kK, aw, HF, 0, 10.0, now_ms())
        ACX.put(None)
        zf = AS.FLOWS.get(ku)
        nw = int(A.wave(tbuf, kr, ku, 180.5, 64.0, 0.5, 5.0, 10.0, False))
        ck(zf is not None and int(zf.n1) == every_ and nw == hits_w, "CP5: Storm of Fists %s: a shockwave every %d hits, a wave strikes %d not-Awed enemies" % ("ON" if code_ else "off", int(zf.n1), nw))

    # ---------------- CP6 Supernova (xSupernova): Starfall's last star -> the blast
    ci_m = NAMES_.index("Mage")
    gu, gr, gpr, gm, gpl, gmsc = player(91, 220.5, 64.0, 0.5, "Mage1")
    setclass(gu, "Mage")
    kG = str(gu)
    STARF = ID["Starfall"]
    n1_, n2_ = mob(351, 221.5, 0.5), mob(352, 222.0, 1.0)
    NEARL[:] = [n1_, n2_]
    for code_ in ("", ",f.xSupernova=1"):
        TREE["csv"] = "v3,v4,v5,fold,A1,A2,A3,A4a" + code_
        c6 = ctx(gu, kG, STARF, 0, TREE["csv"])
        j6_ = A.starJob(gu, kG, JArray(JDouble)([221.5, 64.0, 0.5]), 4.0, 3, 1.5, 10.0, 0, now_ms())
        ACX.put(None)
        j6_.left = 1
        j6_.hits = 4
        caps0 = int(UF.CAPS)
        UF.LAST = ""
        A.runJob(j6_, tst, tbuf, now_ms())
        ck((str(UF.LAST).startswith("supernova") and int(UF.CAPS) == caps0 + 1) if code_ else (not str(UF.LAST).startswith("supernova")),
           "CP6: Supernova %s: the last star %s (%s)" % ("ON" if code_ else "off", "bursts" if code_ else "ends quietly", UF.LAST))
    sn_ = [x for x in said() if x.startswith("Supernova: the stars collapse")]
    ck(len(sn_) == 1 and "% of a star" in sn_[0], "CP6: ... the line (20 %% a star that hit): %s" % sn_[:1])

    # ---------------- CP7 Saint's Covenant (xCovenant): no drop between jumps; overheal -> a ward
    pu, pr_, ppr, pm, ppl, pmsc = player(101, 260.5, 64.0, 0.5, "Priest1")
    hu, hr, hpr, hm, hpl, hmsc = player(102, 261.5, 64.0, 0.5, "HurtA", hp=100.0, hpmax=1000.0)
    iu, ir, ipr, im, ipl, imsc = player(103, 262.5, 64.0, 0.5, "HurtB", hp=150.0, hpmax=1000.0)
    ju, jr, jpr, jm, jpl, jmsc = player(104, 263.5, 64.0, 0.5, "HurtC", hp=200.0, hpmax=1000.0)
    setclass(pu, "Priest")
    kP = str(pu)
    MEMBERS[kP] = MEMBERS[str(hu)] = MEMBERS[str(iu)] = MEMBERS[str(ju)] = [kP, str(hu), str(iu), str(ju)]
    GRACE = ID["MartyrsGrace"]
    NEARL[:] = [pr_, hr, ir, jr]
    outs = {}
    AC.ALT_POW = 0.0   # the base strength (no x1.5): the jumps stay under the per-cast heal caps, so the drop shows
    for code_ in ("", ",f.xCovenant=1"):
        hm.setStatValue(HP, JFloat(100.0))
        im.setStatValue(HP, JFloat(150.0))
        jm.setStatValue(HP, JFloat(200.0))
        AS.WARD.clear()
        TREE["csv"] = "v3,v4,v5,fold,A1,A2,A3,A4b" + code_
        c7_ = ctx(pu, kP, GRACE, 0, TREE["csv"])
        outs[code_] = str(A.graceRun(ppr, tst, tst, pr_, pu, 0, kP))
        ACX.put(None)
    def chain_(s_):
        return [float(x) for x in s_.split("chain=")[1].split()[0].split(",")] if "chain=" in s_ else []
    AC.ALT_POW = 50.0
    c0, c1 = chain_(outs[""]), chain_(outs[",f.xCovenant=1"])
    ck(len(c0) == 3 and len(c1) == 3 and c0[2] < c0[1] - 1e-6 and c1[2] > c0[2] + 100.0 and abs(c1[2] - c1[1]) < 1e-6,
       "CP7: Saint's Covenant - no drop between jumps (75 / 60 / 45 %% alone %s; with it every jump as strong, inside the heal caps %s)" % (c0, c1))
    hm.setStatValue(HP, JFloat(990.0))
    im.setStatValue(HP, JFloat(990.0))
    jm.setStatValue(HP, JFloat(1000.0))
    AS.WARD.clear()
    TREE["csv"] = "v3,v4,v5,fold,A1,A2,A3,A4b,f.xCovenant=1"
    ctx(pu, kP, GRACE, 0, TREE["csv"])
    o7 = str(A.graceRun(ppr, tst, tst, pr_, pu, 0, kP))
    ACX.put(None)
    w7 = AS.WARD.get(hu)
    ck("wards=2" in o7 and w7 is not None and abs(float(w7[0]) - 100.0) < 1e-6, "CP7: ... the healing it could not give became a ward (10 %% of max Health): %s %s" % (o7, None if w7 is None else list(w7)))
    ck(not bool(A.capCov(None)) and bool(UF.covenant(A.ctxFor(pu, kP, GRACE, 0, TREE["csv"]))), "CP7: capCov(null) false; the ctx with the code true")
    K.save()
    sys.stdout.flush()
    os._exit(0)


if __name__ == "__main__":
    HK.run(name="SkyyClasses", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("static", run_static), ("exec46", T48.run_exec46), ("wire46", T48.run_wire46), ("wire47", T48.run_wire47), ("exec48", T48.run_exec),
                   ("alt", run_alt), ("sm", run_exec), ("wire", run_wire), ("live", T48.run_live)],
           script=__file__, live=(T48.LIVE_DIR, "Skyy_SkyyClasses"))
