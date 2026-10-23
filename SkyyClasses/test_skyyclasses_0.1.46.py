"""Harness for SkyyClasses 0.1.46 (elem1: Wynn names, classes:fn:dot, tick causes, element affinity; tools/classes_0_1_46_patch.py). Build first:
    python tools/classes_0_1_46_patch.py && python SkyyClasses/build_skyyclasses_0.1.46.py
    python SkyyClasses/test_skyyclasses_0.1.46.py [--keep]
Phases (tools/harness_kit.py, fresh child JVMs, -Xverify:all, TEMP / TMP in tools/dev/scratch/elem1/cls):
  S   static   the patch re-runs to identical bytes; one class added (DotFn); no new system / command; line endings kept
  A   verify   every class loads + initialises
  C   compare  0.1.45 -> 0.1.46: exactly the planned members (EXPECT)
  X   exec     EXECUTED: ELN = the Wynn names, elemIdx reads Lightning / Wind; classes:fn:imbue -> "Thunder;30" for a Spellblade with an
               old "Lightning" attunement (and the { UUID, weapon } form: null for a non-Spellblade weapon); classes:fn:dot on bad args (FALSE,
               never throws) and good args (TRUE: a kind 28 job with the victim UUID, secs, stacks, the what -> cause row); abilities off =
               FALSE; a full job list = FALSE; causeId / causeOf (a cause the bare JVM has no asset for = PROJECTILE, cached, one WARN);
               causesText; elemOfWhat; affinity with a stub mob:fn:elem (Weak 1.25 / Resist 0.75 / boss 0.5 / none 1 / no SkyyMobs 1)
  W   wiring   bytecode: hit() takes causeId -> causeOf and multiplies by affinity for an NPC; runJob5 runs kind 28 through dotRun; dotRun
               resolves the Ref from the UUID and calls dotOn; dotTick's toxin puff for every *Poison what; setup puts classes:fn:dot
  ST  start twice on a scratch COPY of the live Skyy_SkyyClasses (every one-time update + load + UpSk.loadV3 + the kit): nothing written
  AA  engine-access audit
NOT COVERED (UNVERIFIED in game): a real Poison tick in the ECS (dotRun / dotTick / hit need a live Store), the engine DamageCause assets
(found only once the asset packs load - the smoke test's world), Thorium's Poison resistance on a player victim (SkyyGear's armour pass).
"""
import time
import os, sys, json, shutil, hashlib, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import trees_v3_effects as V3E

VERSION, OLD = "0.1.46", "0.1.45"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyClasses-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyClasses-%s.jar" % OLD)
GEN = os.path.join(HERE, "build_skyyclasses_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyclasses_%s.py" % OLD)
PATCH = os.path.join(TOOLS, "classes_0_1_46_patch.py")
PKG = "com.skyy.classes."
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "elem1", "cls")))
LIVE = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyClasses")
ADDED = ["DotFn"]
EXPECT = {
    "Abil": ["+f AFFIN", "+f CAUSES", "+f DOTS_IN", "+f DOTS_RUN", "+f WHATCAUSE", "+m affinity", "+m causeId", "+m causeOf", "+m causesText",
             "+m dotRun", "+m dotWant", "+m elemOfWhat", "~<clinit>", "~m attune", "~m dotTick", "~m elemIdx", "~m hit", "~m outHit3", "~m runJob5"],
    "AbilWorld": ["+m dotFull", "+m dots", "~m full"],          # elem1fix2
    "ImbueFn": ["~m apply"], "SkyyClassesPlugin": ["~m setup", "~m shutdown"],
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "KitMigrate": ["~m runOnce"],          # the version text
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
U = "00000000-0000-0000-0000-000000000146"
V = "00000000-0000-0000-0000-0000000001f6"


def tree_hash(root):
    o = {}
    for d, _x, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            o[os.path.relpath(p, root).replace(os.sep, "/")] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return o


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyClasses 0.1.46 - build script') and g.count('VERSION = "0.1.46"') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.eq(g.count("makeClass(") - o.count("makeClass("), 1, "S one class added (DotFn)")
    import zipfile as _zf
    _jb = b"".join(_zf.ZipFile(jar).read(_n) for _n in _zf.ZipFile(jar).namelist() if _n.endswith(".class"))
    K.check(b"Elements: Fire, Water, Earth, Thunder, Air." in _jb and b"Elements: Fire, Water, Earth, Lightning, Wind." not in _jb, "S the attune text says Thunder / Air")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def run_exec(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    A, CC, AS, AW, CD, CFG = J("Abil"), J("ClassCfg"), J("AbilStore"), J("AbilWorld"), J("ClassDefs"), J("AbilCfg")
    Obj = JClass("java.lang.Object")
    OA = lambda xs: jpype.JArray(Obj)(xs)
    br = CC.bridge()
    uu, vv = JClass("java.util.UUID").fromString(U), JClass("java.util.UUID").fromString(V)
    K.eq([str(x) for x in A.ELN], ["Fire", "Water", "Earth", "Thunder", "Air", "Poison"], "X ELN = the Wynn names (index order kept)")
    K.eq([int(A.elemIdx(x)) for x in ("Lightning", "Wind", "Thunder", "air", "Fire", "Poison", "Ice", None)], [3, 4, 3, 4, 0, 5, -1, -1],
         "X elemIdx reads the old saved words Lightning / Wind")
    # classes:fn:imbue: a Spellblade (profile:class) with a running Imbue on element 3 at 30 %
    sb = int(A.sbCi())
    br.put("profile:class:" + U, str(CD.NAMES[sb]))
    now = JClass("java.lang.System").currentTimeMillis()
    AS.IMBUE.put(uu, jpype.JArray(jpype.JDouble)([float(now + 60000), 3.0, 30.0, 1.0, 0.0, 0.0]))
    Fn = J("ImbueFn")()
    K.eq(str(Fn.apply(uu)), "Thunder;30", "X classes:fn:imbue = Thunder;30 (an old Lightning attunement reads as Thunder)")
    cands = ["Weapon_Longsword_Iron", "Weapon_Sword_Iron", "Weapon_Battleaxe_Iron", "Weapon_Staff_Iron", "Weapon_Spellblade_Iron", "Weapon_Daggers_Iron",
             "Weapon_Shortbow_Iron", "Weapon_Mace_Iron", "Weapon_Longsword_Crude", "Weapon_Sword_Crude", "Weapon_Spear_Iron", "Weapon_Axe_Iron"]
    own = [c for c in cands if int(CD.ownerOf(c)) == sb]
    other = [c for c in cands if int(CD.ownerOf(c)) not in (sb, int(CD.FREE))]
    K.check(own and other, "X a Spellblade weapon %s and another class's %s among the candidates" % (own[:2], other[:2]))
    if own and other:
        K.eq([str(Fn.apply(OA([uu, own[0]]))), Fn.apply(OA([uu, other[0]])) is None, Fn.apply(OA([uu, None])) is None], ["Thunder;30", True, True],
             "X classes:fn:imbue {UUID, weapon}: only a Spellblade weapon (%s yes, %s no)" % (own[0], other[0]))
    br.put("profile:class:" + U, str(CD.NAMES[(sb + 1) % len(list(CD.NAMES))]))
    K.check(Fn.apply(uu) is None, "X another class: no Imbue answer")
    # classes:fn:dot
    D = J("DotFn")()
    good = lambda: OA([uu, vv, "GearPoison", "Poison", JClass("java.lang.Double")(5.0), JClass("java.lang.Double")(10.0), JClass("java.lang.Integer")(3), "w1"])
    bad = [None, "x", OA([uu, vv]), OA([uu, vv, "GearPoison", "Ice", 5.0, 10.0, 3, "w1"]), OA([uu, vv, "ElemPoison", "Poison", 5.0, 10.0, 3, "w1"]),
           OA([uu, vv, "", "Poison", 5.0, 10.0, 3, "w1"]), OA([uu, vv, "GearPoison", "Poison", 0.0, 10.0, 3, "w1"]),
           OA([uu, vv, "GearPoison", "Poison", 5.0, 0.5, 3, "w1"]), OA([uu, vv, "GearPoison", "Poison", 5.0, 10.0, 0, "w1"]),
           OA([uu, vv, "GearPoison", "Poison", float("nan"), 10.0, 3, "w1"]), OA([uu, "not a uuid", "GearPoison", "Poison", 5.0, 10.0, 3, "w1"]),
           OA([uu, vv, "GearPoison", "Poison", 5.0, 10.0, 3, None]), OA([uu, vv, "X" * 33, "Poison", 5.0, 10.0, 3, "w1"])]
    K.eq([bool(D.apply(b)) for b in bad], [False] * len(bad), "X classes:fn:dot refuses bad args (shape, cause, Elem*, empty / long what, 0 / NaN dps, < 1 s, 0 stacks, no world) - never throws")
    CFG.PART = True
    aw = AW.of("w1")
    n0 = int(aw.size())
    K.check(bool(D.apply(good())), "X classes:fn:dot good args = TRUE")
    jobs = [j for j in list(aw.jobs) if int(j.kind) == 28]
    K.check(int(aw.size()) == n0 + 1 and len(jobs) == 1, "X one kind 28 job queued in the victim's world")
    if jobs:
        j = jobs[0]
        K.check(str(j.tref) == V and str(j.caster) == U and str(j.what) == "GearPoison" and abs(float(j.amount) - 5.0) < 1e-9
                and abs(float(j.secs) - 10.0) < 1e-9 and int(round(float(j.len))) == 3, "X the job: victim UUID, attacker, what, 5 / s, 10 s, 3 stacks")
    K.eq(str(A.causeId("GearPoison")), "Poison", "X the what -> cause row (GearPoison stacks apart from ElemPoison)")
    K.eq([str(A.causeId(w)) if A.causeId(w) is not None else None for w in ("ElemBurn", "ElemShock", "ElemPoison", "Meteor", None)],
         ["Fire", "Lightning", "Poison", None, None], "X causeId: the status ticks' element causes, direct ability hits none (PROJECTILE)")
    P = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DamageCause").PROJECTILE
    K.check(A.causeOf("Poison") == P and A.causeOf(None) == P and A.CAUSES.get("Poison") is not None, "X causeOf in a bare JVM (no asset map): PROJECTILE, cached, one WARN")
    K.check("0 / 6 tick causes found" in str(A.causesText()), "X causesText: %s" % A.causesText())
    CFG.PART = False
    K.check(not bool(D.apply(good())), "X abilities off = FALSE")
    CFG.PART = True
    old = CFG.MAX_LIVE
    CFG.MAX_LIVE = 0
    K.check(not bool(D.apply(good())), "X a full job list = FALSE")
    CFG.MAX_LIVE = old
    # elem1fix2: DoT jobs (26 ticks / 28 queued) never fill the cast gate full(); dotFull() = 8 x abil.maxLive of them
    for j in [j for j in list(aw.jobs)]:
        aw.jobs.remove(j)
    CFG.MAX_LIVE = 2
    AJ = J("AbilJob")
    far = int(time.time() * 1000) + 60000
    for i in range(15):
        aw.add(AJ(26 if i % 2 else 28, far, uu, "ElemBurn", 0.0, 0.0, 0.0, 0.0, 1.0))
    K.check(not bool(aw.full()) and int(aw.dots()) == 15 and not bool(aw.dotFull()), "X elem1fix2: 15 DoT jobs at abil.maxLive 2 = casts still allowed (full() false), DoT cap 16 not reached")
    K.check(bool(D.apply(good())), "X elem1fix2: classes:fn:dot still queues below the DoT cap")
    K.check(bool(aw.dotFull()) and not bool(aw.full()) and not bool(D.apply(good())), "X elem1fix2: at 16 DoT jobs classes:fn:dot = FALSE, casts still allowed")
    aw.add(AJ(5, far, uu, "Meteor", 0.0, 0.0, 0.0, 0.0, 1.0))
    aw.add(AJ(5, far, uu, "Meteor", 0.0, 0.0, 0.0, 0.0, 1.0))
    K.check(bool(aw.full()), "X elem1fix2: 2 non-DoT jobs at abil.maxLive 2 = full() (the cast gate still works)")
    for j in [j for j in list(aw.jobs)]:
        aw.jobs.remove(j)
    CFG.MAX_LIVE = old
    gsrc = open(GEN, encoding="utf-8").read()
    K.check('get("gear:imbue:v2")' in gsrc and 'get("gear:imbue")' not in gsrc, "X elem1fix2: outHit3 waits for gear:imbue:v2 (SkyyGear 0.3.39+), never the old gear:imbue")
    K.eq([str(A.elemOfWhat(w)) if A.elemOfWhat(w) is not None else None for w in ("ElemBurn", "Meteor", "ElemShock", "FrostNova", "ElemPoison", "GearPoison", "Sunder")],
         ["Fire", "Fire", "Thunder", "Water", None, None, None], "X elemOfWhat: Burn / Meteor Fire, Shock Thunder, Frost Nova Water, poisons none")
    K.eq(float(A.affinity("Yeti", "Fire")), 1.0, "X no SkyyMobs (no mob:fn:elem) = x1")

    @JImplements("java.util.function.Function")
    class Elem(object):
        @JOverride
        def apply(self, a):
            r, e = str(a[0]), str(a[1])
            v = {"Yeti|Fire": 25, "Yeti|Water": -25, "Dragon_Fire|Fire": -50, "Weird|Fire": -500}.get(r + "|" + e, 0)
            return JClass("java.lang.Integer").valueOf(v)
    br.put("mob:fn:elem", Elem())
    K.eq([round(float(A.affinity(r, e)), 6) for r, e in (("Yeti", "Fire"), ("Yeti", "Water"), ("Dragon_Fire", "Fire"), ("Trork", "Fire"), ("Weird", "Fire"), (None, "Fire"))],
         [1.25, 0.75, 0.5, 1.0, 0.0, 1.0], "X affinity: Weak 1.25 / Resist 0.75 / boss own 0.5 / none 1 / never below 0 / no role 1")
    K.save()


def run_wire(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.JAVASSIST], verify=False)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(jar)
    IP, PS, BOS = JClass("javassist.bytecode.InstructionPrinter"), JClass("java.io.PrintStream"), JClass("java.io.ByteArrayOutputStream")

    def code(cn, mn):
        bos = BOS()
        for m in cp.get(PKG + cn).getDeclaredMethods():
            if str(m.getName()) == mn:
                IP(PS(bos)).print_(m)
        return str(bos.toString())
    h = code("Abil", "hit")
    K.check("Abil.causeId" in h and "Abil.causeOf" in h and "Abil.elemOfWhat" in h and "Abil.affinity" in h and "getRoleName" in h
            and h.index("Abil.causeOf") < h.index("executeDamage") and h.index("Abil.affinity") < h.index("executeDamage"),
            "W hit(): the tick cause + the affinity (for an NPC) before executeDamage")
    r5 = code("Abil", "runJob5")
    K.check("Abil.dotRun" in r5 and "Abil.dotTick" in r5, "W runJob5: kind 26 dotTick, kind 28 dotRun")
    dr = code("Abil", "dotRun")
    K.check("getRefFromUUID" in dr and "Abil.dotOn" in dr and dr.index("getRefFromUUID") < dr.index("Abil.dotOn"), "W dotRun: Ref from the victim UUID, then dotOn")
    dt = code("Abil", "dotTick")
    K.check("endsWith" in dt and "Abil.hit" in dt, "W dotTick: the toxin puff for every *Poison what; the tick through hit()")
    s = code("SkyyClassesPlugin", "setup")
    K.check("classes:fn:dot" in s and "DotFn" in s, "W setup puts classes:fn:dot")
    K.check("classes:fn:dot" in code("SkyyClassesPlugin", "shutdown"), "W shutdown removes it")
    K.save()


def run_st(out, jar, scratch, step):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Cfg, Pub, AS, S = JClass(PKG + "ClassCfg"), JClass(PKG + "CfgPub"), JClass(PKG + "AbilStore"), JClass(PKG + "UpSk")
    Paths = JClass("java.nio.file.Paths")
    home = os.path.join(scratch, "st", "mods")
    base = os.path.join(home, "Skyy_SkyyClasses")
    if step == "1":
        shutil.rmtree(os.path.join(scratch, "st"), ignore_errors=True)
        shutil.copytree(LIVE, base)
        json.dump(tree_hash(LIVE), open(os.path.join(scratch, "st-live.json"), "w"))
    before = tree_hash(base)
    Cfg.FILE = Paths.get(os.path.join(base, "config.properties"))
    o = {"m10": str(Cfg.migrate0110()), "m29": str(Cfg.migrate0129()), "m32": str(Cfg.migrate0132()), "m41": str(Cfg.migrate0141()),
         "p4": str(Cfg.migrateP4()), "load": str(Cfg.load()), "sk": str(S.loadV3(Paths.get(base)))}
    AS.DIR = Paths.get(os.path.join(base, "abilities"))
    Pub.start(Paths.get(home), None)
    Pub.flush()
    Pub.shutdown()
    after = tree_hash(base)
    ch = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    if step == "1":
        K.check(ch in ([], ["trees.properties"]), "ST start 1 on a scratch COPY of the live data: 0.1.46 writes nothing of its own (%s; %s)" % (ch, o["p4"][:80]))
    else:
        K.check(not ch and o["p4"] == "", "ST start 2: nothing written (%s)" % ch)
        K.check(tree_hash(LIVE) == json.load(open(os.path.join(scratch, "st-live.json"))), "ST: the live Skyy_SkyyClasses folder was only read")
    K.save()
    sys.stdout.flush()
    os._exit(0)


def run_st1(out, jar, scratch, _home):
    run_st(out, jar, scratch, "1")


def run_st2(out, jar, scratch, _home):
    run_st(out, jar, scratch, "2")


if __name__ == "__main__":
    HK.run(name="SkyyClasses", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("exec", run_exec), ("wire", run_wire), ("st1", run_st1), ("st2", run_st2)], script=__file__)
