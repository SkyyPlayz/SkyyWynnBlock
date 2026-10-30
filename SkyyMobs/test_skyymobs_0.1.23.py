"""Harness for SkyyMobs 0.1.23 (Augments round A1, the SkyyMobs part: element mobs put their element's state on players through SkyyClasses
0.1.51's classes:fn:elemHit; tools/mobs_0_1_23_patch.py). Build first:
    python tools/mobs_0_1_23_patch.py && python SkyyMobs/build_skyymobs_0.1.23.py
    python SkyyMobs/test_skyymobs_0.1.23.py [--keep] [--expect-dump]

Phases (fresh child JVMs, tools/harness_kit.py):
  S     static   the patch re-runs to identical bytes (--out), line endings kept, no new class / system / command; the jar changes only
                 classes + the manifest (every role / model / spawn file byte-identical to 0.1.22)
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.1.22 -> 0.1.23 (EXPECT below)
  X     exec     EXECUTES MobElem.stateHit with a stand-in classes:fn:elemHit: a Water mob -> { mob UUID, player UUID, int[5] power (Water =
                 elem.mobPower), double[5] parts (Water = the hit x elem.mobShare %), the hit, FALSE, the world } in the Wynn order; a Fire /
                 Thunder / Earth / Air mob the same on its index; a tougher version = its base role's element; no own element / no player /
                 no bridge / elem.mobStates OFF / a 0 hit = no call; a throwing bridge = FALSE + one WARN; elem.mobPower edits live;
                 the two rows + the default file lines; the ready text
  CS    exec     (fix round) CreditSys.handle EXECUTED on a REAL engine Store (the 0.1.8 harness pattern): an element mob's LANDED hit on
                 a player -> ONE classes:fn:elemHit call with the FINAL amount; a cancelled / zero hit, a mob with no element, a player
                 attacker, elem.mobStates OFF = no call; a player's hit on an NPC is still credited (0.1.7)
  W     wire     bytecode: CreditSys.handle (Inspect group) calls MobElem.stateHit; LevelDamage.handle (Filter group) never does
  EX122 0.1.22's exec phase EXECUTED on this jar (variants, factors, drops unchanged)
  D     live     start twice on a scratch COPY of Skyy's live Skyy_SkyyMobs (0.1.22's live phase: bytes untouched, no migration)
  AA    engine-access audit
NOT COVERED (UNVERIFIED in game): a real mob hit reaching CreditSys (the Inspect group) with a live SkyyClasses; the states on the
player in game (SkyyClasses' harness executes the engine side of this exact call).
Scratch: tools/dev/scratch/aug_a1/mobs (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, zipfile, json, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.1.23"
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "aug_a1", "mobs")]
import skyybuild as B
import harness_kit as HK
import skyyelem as EL

_run0 = HK.run
_cmp00 = HK.run_compare
HK.run = lambda *a, **k: None          # import 0.1.22's harness for its exec + live phases without running it
_s = importlib.util.spec_from_file_location("test_skyymobs_0_1_22", os.path.join(HERE, "test_skyymobs_0.1.22.py"))
T22 = importlib.util.module_from_spec(_s)
_s.loader.exec_module(T22)
HK.run = _run0

GEN = os.path.join(HERE, "build_skyymobs_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyymobs_0.1.22.py")
PATCH = os.path.join(ROOT, "tools", "mobs_0_1_23_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMobs-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMobs-0.1.22.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.mobs."
EXPECT = {
    "MobCfg": ["+f ELEM_POWER", "+f ELEM_STATES", "~<clinit>", "~m apply", "~m load", "~m reloadAll", "~m useDefaults"],   # the 2 rows (fields, load, the kit's apply / defaults)
    "MobElem": ["+f STATE_HITS", "+m stateHit", "~<clinit>", "~m text"],
    "CreditSys": ["~m handle"],          # fix round: the state call sits in the Inspect group (a LANDED hit); LevelDamage = 0.1.22
    "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "CfgFile": ["~<clinit>"],
    "SkyyMobsPlugin": ["~m setup"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyMobs 0.1.23 - build script') and g.count('VERSION = "0.1.23"') == 1, "S header + VERSION")
    K.eq([g.count(w) for w in ("registerSystem(", "registerCommand(", "makeClass(")], [o.count(w) for w in ("registerSystem(", "registerCommand(", "makeClass(")],
         "S no new system / command / class")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    K.eq((sorted(nb - na), sorted(na - nb)), ([], []), "S the jar adds / removes no file")
    K.eq(sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n)), ["manifest.json"],
         "S every role / model / spawn / lang file byte-identical to 0.1.22 (only the manifest changes)")
    K.save()


def run_exec(out, jar, scratch, home):
    from jpype import JClass, JImplements, JOverride, JArray, JObject
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    C, El = JClass(PKG + "MobCfg"), JClass(PKG + "MobElem")
    UUID = JClass("java.util.UUID")
    C.useDefaults()
    El.derive()
    d = str(C.DEF_CFG)
    K.check("\nelem.mobStates=true\n" in d and "\nelem.mobPower=5\n" in d, "X the default file carries elem.mobStates=true + elem.mobPower=5")
    K.check(bool(C.ELEM_STATES) and int(C.ELEM_POWER) == 5 and int(C.ELEM_SHARE) == 30 and bool(El.ANY), "X the defaults: on, power 5, mob share 30 %")
    CALLS = []
    MODE = {"r": True, "throw": False}

    @JImplements("java.util.function.Function")
    class Hit(object):
        @JOverride
        def apply(self, o):
            if MODE["throw"]:
                raise RuntimeError("boom")
            a = list(o)
            CALLS.append((str(a[0]), str(a[1]), [int(x) for x in a[2]], [round(float(x), 4) for x in a[3]], float(a[4]), bool(a[5]), str(a[6]) if a[6] is not None else None))
            return JClass("java.lang.Boolean").valueOf(MODE["r"])
    mob, pl = UUID(1, 2), UUID(3, 4)
    roles = {"Eel_Moray": "Water", "Golem_Crystal_Flame": "Fire", "Golem_Crystal_Thunder": "Thunder", "Golem_Crystal_Earth": "Earth"}
    own = dict((r, str(El.word(r))) for r in roles)
    K.eq(own, roles, "X the default table: Eel Water, Flame golem Fire, Thunder golem Thunder, Earth golem Earth")
    K.check(not bool(El.stateHit("Eel_Moray", mob, pl, 20.0, "w")), "X no classes:fn:elemHit (no SkyyClasses 0.1.51) = no call, FALSE")
    br.put("classes:fn:elemHit", Hit())
    K.check(bool(El.stateHit("Eel_Moray", mob, pl, 20.0, "NewBetaTest")), "X a Water mob's hit -> TRUE")
    K.eq(CALLS[-1], (str(mob), str(pl), [0, 0, 5, 0, 0], [0.0, 0.0, 6.0, 0.0, 0.0], 20.0, False, "NewBetaTest"),
         "X ... { mob, player, power Water 5, part Water = 20 x 30 %%, the hit, FALSE, the world } in the Wynn order (%s)" % EL.NAMES)
    for r, e in roles.items():
        del CALLS[:]
        El.stateHit(r, mob, pl, 10.0, "w")
        K.check(len(CALLS) == 1 and CALLS[0][2][EL.NAMES.index(e)] == 5 and sum(CALLS[0][2]) == 5 and abs(CALLS[0][3][EL.NAMES.index(e)] - 3.0) < 1e-9,
                "X %s (%s) puts only its own element: %s" % (r, e, CALLS[:1]))
    del CALLS[:]
    El.stateHit("Eel_Moray_SkyyArmored1", mob, pl, 10.0, "w")
    K.check(len(CALLS) == 1 and CALLS[0][2] == [0, 0, 5, 0, 0], "X a tougher version = its base role's element")
    del CALLS[:]
    n0 = int(El.STATE_HITS)
    for args in (("Trork_Warrior", mob, pl, 10.0), (None, mob, pl, 10.0), ("Eel_Moray", None, pl, 10.0), ("Eel_Moray", mob, None, 10.0),
                 ("Eel_Moray", mob, pl, 0.0), ("Eel_Moray", mob, pl, -1.0), ("Eel_Moray", mob, pl, float("nan")), ("Eel_Moray", mob, pl, 1.0e9)):
        K.check(not bool(El.stateHit(args[0], args[1], args[2], args[3], "w")), "X no call for %r" % (args,))
    K.eq((len(CALLS), int(El.STATE_HITS)), (0, n0), "X ... none of those reached the bridge")
    C.ELEM_STATES = False
    K.check(not bool(El.stateHit("Eel_Moray", mob, pl, 10.0, "w")) and not CALLS, "X elem.mobStates OFF = no call")
    C.ELEM_STATES = True
    C.ELEM_POWER = 9
    El.stateHit("Eel_Moray", mob, pl, 10.0, "w")
    K.check(CALLS[-1][2] == [0, 0, 9, 0, 0], "X elem.mobPower is read live (9)")
    C.ELEM_POWER = 5
    MODE["r"] = False
    n1 = int(El.STATE_HITS)
    K.check(not bool(El.stateHit("Eel_Moray", mob, pl, 10.0, "w")) and int(El.STATE_HITS) == n1, "X the bridge refusing (queue full) = FALSE, not counted")
    MODE["r"], MODE["throw"] = True, True
    K.check(not bool(El.stateHit("Eel_Moray", mob, pl, 10.0, "w")), "X a throwing bridge = FALSE (caught, one WARN)")
    MODE["throw"] = False
    t = str(El.text())
    K.check("states on players on (power 5)" in t, "X the ready text names the rows: %s" % t[-90:])
    g = open(GEN, encoding="utf8").read()
    K.check('("elem.mobStates", "Element mobs put states on players", "elem", "bool", "true"' in g and '("elem.mobPower", "Element mob state power", "elem", "int", "5", "1", "10"' in g,
            "X the two Server Setup rows (Mobs > Elements, live)")
    K.save()


def run_cs(out, jar, scratch, home):
    from jpype import JClass, JFloat, JInt, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    C, El, MC, CS = JClass(PKG + "MobCfg"), JClass(PKG + "MobElem"), JClass(PKG + "MobCredit"), JClass(PKG + "CreditSys")
    UUID = JClass("java.util.UUID")
    C.useDefaults()
    El.derive()
    CALLS = []

    @JImplements("java.util.function.Function")
    class Hit(object):
        @JOverride
        def apply(self, o):
            a = list(o)
            CALLS.append(([int(x) for x in a[2]], [round(float(x), 4) for x in a[3]], float(a[4]), str(a[0]), str(a[1])))
            return JClass("java.lang.Boolean").TRUE
    br.put("classes:fn:elemHit", Hit())
    us_f = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    us_f.setAccessible(True)
    us = us_f.get(None)

    def jfield(cls, name):
        cc = cls
        while cc is not None:
            try:
                f_ = cc.getDeclaredField(name)
                f_.setAccessible(True)
                return f_
            except Exception:
                cc = cc.getSuperclass()
        raise KeyError(name)

    @JImplements("java.util.function.Supplier")
    class Sup(object):
        @JOverride
        def get(self):
            return None
    ES = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore")
    ERS, AR = JClass("com.hypixel.hytale.component.EmptyResourceStorage"), JClass("com.hypixel.hytale.component.AddReason")
    UUIDC = JClass("com.hypixel.hytale.server.core.entity.UUIDComponent")
    PRF = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    NPCE = JClass("com.hypixel.hytale.server.npc.entities.NPCEntity")
    DMG = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage")
    DENT = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage$EntitySource")
    EMc, DMc, UNc = (JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule"), JClass("com.hypixel.hytale.server.core.modules.entity.damage.DamageModule"),
                     JClass("com.hypixel.hytale.server.core.universe.Universe"))
    REG = ES.REGISTRY
    T_UU, T_PR, T_NPC = REG.registerComponent(UUIDC, Sup()), REG.registerComponent(PRF, Sup()), REG.registerComponent(NPCE, Sup())
    G_INS = REG.registerSystemGroup()
    em = us.allocateInstance(EMc.class_)
    jfield(EMc.class_, "uuidComponentType").set(em, T_UU)
    ctm = JClass("java.util.HashMap")()
    ctm.put(NPCE.class_, T_NPC)
    jfield(EMc.class_, "classToComponentType").set(em, ctm)
    jfield(EMc.class_, "instance").set(None, em)
    dm = us.allocateInstance(DMc.class_)
    jfield(DMc.class_, "inspectDamageGroup").set(dm, G_INS)
    jfield(DMc.class_, "instance").set(None, dm)
    un = us.allocateInstance(UNc.class_)
    jfield(UNc.class_, "playerRefComponentType").set(un, T_PR)
    jfield(UNc.class_, "instance").set(None, un)
    ESMOD = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatsModule")
    esm = us.allocateInstance(ESMOD.class_)
    jfield(ESMOD.class_, "entityStatMapComponentType").set(esm, REG.registerComponent(JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap"), Sup()))
    jfield(ESMOD.class_, "instance").set(None, esm)
    st = REG.addStore(ES(None), ERS.get())
    sysc = CS()
    K.check(sysc.getGroup().equals(G_INS), "CS: CreditSys (the state call's home) runs in the Inspect damage group - after armour + ApplyDamage")

    def add(comps):
        h = REG.newHolder()
        for ty, c in comps:
            h.addComponent(ty, c)
        return st.addEntity(h, AR.SPAWN)

    def npc(role, u):
        n_ = us.allocateInstance(NPCE.class_)
        jfield(NPCE.class_, "roleName").set(n_, role)
        return add([(T_NPC, n_), (T_UU, UUIDC(u))])
    pu, qu, eu, tu, vu = UUID(0, 11), UUID(0, 12), UUID(0, 13), UUID(0, 14), UUID(0, 15)
    ava = add([(T_PR, PRF(None, pu, "Ava", "en-US", None, None)), (T_UU, UUIDC(pu))])
    ben = add([(T_PR, PRF(None, qu, "Ben", "en-US", None, None)), (T_UU, UUIDC(qu))])
    eel = npc("Eel_Moray", eu)
    trork = npc("Trork_Warrior", tu)
    victim = npc("Trork_Warrior", vu)

    def fire(target, src, amt, cancel=False):
        d = DMG(src, JInt(0), JFloat(amt))
        if cancel:
            d.setCancelled(True)

        @JImplements("java.util.function.BiConsumer")
        class Cn(object):
            @JOverride
            def accept(self, chunk, cb):
                for i_ in range(int(chunk.size())):
                    if chunk.getReferenceTo(i_).equals(target):
                        sysc.handle(JInt(i_), chunk, st, cb, d)
        st.forEachChunk(sysc.getQuery(), Cn())
    fire(ava, DENT(eel), 20.0)
    K.eq(CALLS, [([0, 0, 5, 0, 0], [0.0, 0.0, 6.0, 0.0, 0.0], 20.0, str(eu), str(pu))],
         "CS: a Water mob's LANDED 20 hit on a player -> ONE elemHit { eel, Ava, Water 5, part 20 x 30 %, the FINAL 20 }")
    for what, args in (("a cancelled hit", (ava, DENT(eel), 20.0, True)), ("a zero hit", (ava, DENT(eel), 0.0, False)),
                       ("a mob with no element", (ava, DENT(trork), 20.0, False)), ("a player attacker (PvP is not this path)", (ava, DENT(ben), 20.0, False)),
                       ("an element mob hitting a mob", (victim, DENT(eel), 20.0, False))):
        del CALLS[:]
        fire(args[0], args[1], args[2], cancel=args[3])
        K.eq(CALLS, [], "CS: %s -> no call" % what)
    C.ELEM_STATES = False
    fire(ava, DENT(eel), 20.0)
    K.eq(CALLS, [], "CS: elem.mobStates OFF -> no call")
    C.ELEM_STATES = True
    MC.T.clear()
    fire(victim, DENT(ava), 30.0)
    r = MC.read(str(vu), False)
    K.check(r is not None and str(r[0]) == str(pu) and float(r[1]) == 30.0 and not CALLS, "CS: a player's hit on an NPC is still credited (0.1.7), no state call: %s" % (list(r) if r else None))
    K.save()


def run_wire(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.JAVASSIST], verify=False)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(jar)

    def seq_of(cls):
        m = [x for x in cp.get(PKG + cls).getDeclaredMethods() if str(x.getName()) == "handle"]
        seq = []
        ci = m[0].getMethodInfo().getCodeAttribute().iterator()
        cpl = m[0].getMethodInfo().getConstPool()
        while ci.hasNext():
            pos = ci.next()
            if ci.byteAt(pos) == 0xb8:
                seq.append(str(cpl.getMethodrefName(ci.u16bitAt(pos + 1))))
        return seq
    sl, sc = seq_of("LevelDamage"), seq_of("CreditSys")
    K.check(sl.count("cutHit") == 2 and "stateHit" not in sl, "W LevelDamage.handle (Filter group) keeps its 2 cutHit calls and never calls stateHit: %s" % sl)
    K.check(sc.count("stateHit") == 1 and sc.index("stateHit") < sc.index("hit"), "W CreditSys.handle (Inspect group) calls stateHit once, before the credit: %s" % sc)
    K.save()


HK.run_compare = T22._cmp
if __name__ == "__main__":
    HK.run("SkyyMobs", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, [],
           [("static", run_static), ("exec", run_exec), ("cs", run_cs), ("wire", run_wire), ("ex122", T22.run_exec), ("live", T22.run_live)], __file__,
           live=(T22.LIVE_DIR, "Skyy_SkyyMobs"))
