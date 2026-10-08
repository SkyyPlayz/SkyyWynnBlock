"""Bare-JVM check for SkyyMonkProbe 0.1. UNTESTED draft from a cloud session - cannot compile here (no HytaleServer.jar).
Build first: python SkyyMonkProbe/build_skyymonkprobe_0.1.py

    python SkyyMonkProbe/test_skyymonkprobe_0.1.py [--keep]

  J  the jar: manifest (Main), exactly the expected classes, NO asset file at all (no item / block / lang / .ui: nothing overridden)
  K  the kit ids (Weapon_Staff_Bo_Wood / _Bamboo) are vanilla items in Assets.zip; the dagger dash VelocityConfig the NPC pushes copy
     still has the six keys SkyyArmory asserts
  A  every class loads and verifies (game JRE, -Xverify:all, -XX:-UsePerfData, HytaleServer.jar + the jar)
  L  MpLogic on plain data: the launch / air-time / forward-speed numbers of research/cloud/Monk-Probe-Plan.md (python3 maths), the timed
     window edges (-250 / +100 ms), the bound distance cap, the analytic slow fall + the cap way, the cone, the combo decay + cap,
     verdict / f1 / number / dnum
  E  the engine facts the probes lean on: PhysicsConstants.GRAVITY_ACCELERATION = 32; DamageSystems$FallDamagePlayers still runs BEFORE
     PlayerSystems$ProcessPlayerInput (the FALL damage of a landing comes from the queued input - why the bound HOLDS the fall damage
     100 ms); the protocol ApplicationEffects / MovementEffects still carry no gravity field (why M1 is a per-tick Set)
  X  MpCmds.help / MpLog.tell(null, ..) reach the harness SINK; MpCmds.isFall(null) = false; STATES empty at start
  P  /mprobe and both usage variants: permission node skyymonkprobe.admin, empty permission groups, getPermissionGroupsRecursive() gives
     the node to no group (crosscheck.py audits the same with the whole SET)
Not testable without the game: everything the probes are for (research/cloud/Monk-Probe-Plan.md test script).
Scratch: tools/dev/scratch/monkprobe01/test (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B

VERSION = "0.1"
JAR = os.path.join(HERE, "SkyyMonkProbe-%s.jar" % VERSION)
PKG = "com.skyy.monkprobe."
CLASSES = sorted(PKG + c for c in ["MpLog", "MpLogic", "MpState", "MpCmds", "MpTick", "MpFallSys", "MpHitSys", "MProbeArg2Cmd",
                                   "MProbeArgCmd", "MProbeCmd", "SkyyMonkProbePlugin"])
NODE = "skyymonkprobe.admin"
ASSETS = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
SCRATCH = os.path.join(TOOLS, "dev", "scratch", "monkprobe01", "test")
FAILS, OKS = [], [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def near(a, b, eps=1e-6):
    return abs(float(a) - float(b)) <= eps


def main():
    os.makedirs(SCRATCH, exist_ok=True)
    z, az = zipfile.ZipFile(JAR), zipfile.ZipFile(ASSETS)
    # ---------------- J
    man = json.loads(z.read("manifest.json"))
    check(man["Main"] == PKG + "SkyyMonkProbePlugin", "J. manifest Main")
    check(man.get("IncludesAssetPack") is False, "J. manifest IncludesAssetPack false (no assets shipped)")
    cls = sorted(n[:-6].replace("/", ".") for n in z.namelist() if n.endswith(".class"))
    check(cls == CLASSES, "J. classes: %s" % cls)
    other = sorted(n for n in z.namelist() if not n.endswith(".class") and n != "manifest.json")
    check(other == [], "J. no asset files (nothing overridden): %s" % other)

    # ---------------- K
    names = set(az.namelist())
    items = set(n.rsplit("/", 1)[1][:-5] for n in names if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    for i in ("Weapon_Staff_Bo_Wood", "Weapon_Staff_Bo_Bamboo"):
        check(i in items, "K. kit item %s is vanilla" % i)
    dash = [n for n in names if n.startswith("Server/") and n.endswith("/Daggers_Dash_Backward.json")]
    check(len(dash) == 1, "K. Daggers_Dash_Backward.json found once: %s" % dash)
    if dash:
        vc = json.loads(az.read(dash[0]).decode("utf-8-sig"))["Interactions"][0].get("VelocityConfig", {})
        check(sorted(vc) == sorted(["AirResistance", "AirResistanceMax", "GroundResistance", "GroundResistanceMax", "Threshold", "Style"]),
              "K. dash VelocityConfig keys %s" % sorted(vc))

    # ---------------- A
    import jpype
    from jpype import JClass
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + SCRATCH,
                   classpath=[B.SERVER_JAR, JAR, B.JAVASSIST], convertStrings=True)
    Cls = JClass("java.lang.Class")
    loader = JClass("java.lang.ClassLoader").getSystemClassLoader()
    for n in CLASSES:
        try:
            Cls.forName(n, True, loader)
            OKS[0] += 1
        except Exception as e:
            FAILS.append("A. load " + n + ": " + str(e))
            print("LOAD FAIL", n, e)
    print("A. loaded + verified %d classes (-Xverify:all)" % len(CLASSES))
    if FAILS:
        return

    # ---------------- L (expected numbers: python3 maths, g = 32)
    L = JClass(PKG + "MpLogic")
    g = 32.0
    check(near(L.vyFor(4.5, g), math.sqrt(2 * g * 4.5)) and near(L.vyFor(4.5, g), 16.970562748, 1e-6), "L. vault vy 16.97")
    check(near(L.vyFor(6.0, g), 19.595917942, 1e-6), "L. rise vy 19.60")
    check(near(L.hSpeed(7.0, L.vyFor(4.5, g), g), 7.0 / (2 * math.sqrt(2 * g * 4.5) / g), 1e-9), "L. vault forward 6.60 b/s")
    check(L.vyFor(0.0, g) == 0.0 and L.vyFor(-1.0, g) == 0.0 and L.airTime(0.0, g) == 0.0 and L.hSpeed(7.0, 0.0, g) == 0.0, "L. zero / negative inputs")
    for land, press, exp in ((1000, 760, True), (1000, 750, True), (1000, 749, False), (1000, 1100, True), (1000, 1101, False),
                             (0, 900, False), (1000, 0, False)):
        check(bool(L.timed(land, press, 250, 100)) == exp, "L. timed(%d, %d) = %s" % (land, press, exp))
    check(L.boundDist(5.0, 0.5, 8.0, 4.0) == 7.0 and L.boundDist(5.0, 0.5, 8.0, 40.0) == 13.0 and L.boundDist(5.0, 0.5, 8.0, -2.0) == 5.0,
          "L. bound distance 5 + 0.5 per block, cap +8")
    check(near(L.slowVy(0.15, g, 500), -0.85 * 32 * 0.5) and L.slowVy(0.15, g, 0) == 0.0 and near(L.slowVy(2.0, g, 500), 0.0),
          "L. analytic slow fall (and the 0..1 clamp)")
    check(L.capVy(-10.0, 6.0) == -6.0 and L.capVy(-3.0, 6.0) == -3.0 and L.capVy(2.0, 6.0) == 2.0 and L.capVy(-10.0, 0.0) == -10.0,
          "L. cap way")
    check(math.isnan(L.capVy(float("nan"), 6.0)), "L. cap way keeps an unreadable speed")
    check(near(L.expectRatio(0.15), 1 / math.sqrt(0.85), 1e-12) and L.expectRatio(0.0) == 1.0 and L.expectRatio(1.0) == 1.0, "L. expected ratio 1.0847")
    check(near(L.fallMs(4.5, g), math.sqrt(2 * 4.5 / g) * 1000, 1e-9), "L. vanilla fall 530 ms")
    for ox, oz, exp in ((2.0, 0.5, True), (2.0, -0.75, True), (2.0, 1.0, False), (-1.0, 0.0, False), (3.5, 0.0, False), (0.0, 0.0, True)):
        check(bool(L.inCone(ox, oz, 1.0, 0.0, 3.0, 0.75)) == exp, "L. cone (%s, %s) = %s" % (ox, oz, exp))
    AL, LG = JClass("java.util.ArrayList"), JClass("java.lang.Long")
    l = AL()
    for i in range(25):
        l.add(LG.valueOf(1000 + i * 100))
    check(L.prune(l, 6000, 5000, 20) == 20, "L. combo: the 5 s old stamp drops, cap 20")
    check(L.prune(l, 9000, 5000, 20) == 0 and L.prune(None, 1, 1, 1) == 0, "L. combo decays to 0")
    check(str(L.verdict(6.5, 7.0, 0.25)).startswith("PASS") and str(L.verdict(3.0, 7.0, 0.25)).startswith("OFF")
          and str(L.verdict(2.0, 0.0, 0.25)).startswith("n/a"), "L. verdict")
    check(str(L.f1(16.97)) == "17.0" and str(L.f1(-2.25)) in ("-2.3", "-2.2") and str(L.f1(float("nan"))) == "?", "L. f1")
    check(L.number("x", 30, 5, 300) == 30 and L.number("999", 30, 5, 300) == 300 and L.dnum("15", 0.0, 0.0, 90.0) == 15.0
          and L.dnum("NaN", 3.0, 0.0, 90.0) == 3.0, "L. number / dnum")

    # ---------------- E
    PHC = JClass("com.hypixel.hytale.server.core.modules.physics.util.PhysicsConstants")
    check(near(float(PHC.GRAVITY_ACCELERATION), 32.0), "E. PhysicsConstants.GRAVITY_ACCELERATION = 32 (%s)" % PHC.GRAVITY_ACCELERATION)
    IP = JClass("javassist.bytecode.InstructionPrinter")
    pool = JClass("javassist.ClassPool")(False)
    pool.appendSystemPath()
    pool.appendClassPath(B.SERVER_JAR)
    fdp = pool.get("com.hypixel.hytale.server.core.modules.entity.damage.DamageSystems$FallDamagePlayers")
    ci = fdp.getClassInitializer()
    lines = []
    if ci is not None:
        it, cp = ci.getMethodInfo().getCodeAttribute().iterator(), ci.getMethodInfo().getConstPool()
        while it.hasNext():
            lines.append(str(IP.instructionString(it, it.next(), cp)))
    check(any("Order.BEFORE" in x for x in lines) and any("PlayerSystems$ProcessPlayerInput" in x for x in lines),
          "E. FallDamagePlayers still runs BEFORE ProcessPlayerInput (the FALL damage comes from the queued landing)")
    fx = [str(f.getName()) for c in ("com.hypixel.hytale.protocol.ApplicationEffects", "com.hypixel.hytale.protocol.MovementEffects")
          for f in pool.get(c).getDeclaredFields()]
    check(not [f for f in fx if "ravity" in f or "fall" in f.lower()], "E. no gravity / slow-fall field in the effect protocol: %s" % fx)

    # ---------------- X
    Log, Cmds = JClass(PKG + "MpLog"), JClass(PKG + "MpCmds")
    sink = AL()
    Log.SINK = sink
    Cmds.help(None)
    check(sink.size() == 3, "X. help = 3 lines (%d)" % sink.size())
    check(not bool(Cmds.isFall(None)) and Cmds.STATES.isEmpty(), "X. isFall(null) false, no state at start")
    Log.SINK = None

    # ---------------- P
    AC = JClass("com.hypixel.hytale.server.core.command.system.AbstractCommand")
    fld = AC.class_.getDeclaredField("permissionGroups")
    fld.setAccessible(True)
    for cn in ("MProbeCmd", "MProbeArgCmd", "MProbeArg2Cmd"):
        try:
            c = JClass(PKG + cn)()
        except Exception as e:
            check(False, "P. construct %s: %s" % (cn, e))
            continue
        perm = c.getPermission()
        groups = fld.get(c)
        check(perm is not None and NODE in str(perm.getId() if hasattr(perm, "getId") else perm), "P. %s requires %s (%s)" % (cn, NODE, perm))
        check(groups is not None and len(groups) == 0, "P. %s permission groups empty (%s)" % (cn, groups))
        if cn == "MProbeCmd":
            rec = c.getPermissionGroupsRecursive()
            leak = [str(k) for k in rec.keySet() if rec.get(k) is not None and any(NODE in str(x) for x in rec.get(k))]
            check(not leak, "P. getPermissionGroupsRecursive gives %s to no group (leak: %s)" % (NODE, leak))
    print("P. permissions done")


try:
    main()
finally:
    if "--keep" not in sys.argv:
        shutil.rmtree(SCRATCH, ignore_errors=True)
print("%d ok, %d fail(s)" % (OKS[0], len(FAILS)))
sys.exit(1 if FAILS else 0)
