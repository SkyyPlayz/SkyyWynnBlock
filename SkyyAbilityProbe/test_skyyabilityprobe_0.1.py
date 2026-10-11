"""Bare-JVM check for SkyyAbilityProbe 0.1.
UNTESTED draft from a cloud session - cannot compile here (no HytaleServer.jar); never pin or deploy before the local session builds + reviews it.
Build first: python SkyyAbilityProbe/build_skyyabilityprobe_0.1.py

    python SkyyAbilityProbe/test_skyyabilityprobe_0.1.py [--keep]

  J  the jar: manifest (Main), IncludesAssetPack FALSE, exactly the expected classes, NO asset file at all (nothing overridden)
  K  the vanilla Stun effect still disables movement (P8 / P12); the Mana stat file is there (P15 prints its Max)
  A  every class loads and verifies (game JRE, -Xverify:all, -XX:-UsePerfData, HytaleServer.jar + the jar) - on 0.6.8 AND on 0.7: the
     jar names no 0.7 class (AbChainSys gets the event class at run time)
  L  AbLogic on plain data: f1 / verdict / number / dnum / word (ids keep their case), ring points, the lethal test + saved Health,
     the write-fight test, slot range, gaps, chain kinds, the swing verdict, the tick budget
  X  AbRefl on JDK objects (call0, invoke picks a fillable method, fill, dump, findBy, cancel, static0, cls); help = 4 lines to the
     harness SINK; STATES empty at start
  R  THE STATE-RESET RULE (the SkyyMonkProbe review found stale timers / armed flags): every AbState probe field is set to a non-rest
     value, AbCmds.clear() must put EVERY one back; AbCmds.plan() (arming) clears first, so no probe inherits another's flags
     (p1 cancel -> p2, p5 save -> p6, p8 stun -> p8 hits, p9 name -> p10 ...); a refused plan leaves the state at rest; finish() clears
  E  engine facts the probes lean on: SystemDependency(Order, Class) public + Order.BEFORE / AFTER; DamageSystems$ArmorDamageReduction
     loads; EntityEventSystem(Class) exists; IF the server is 0.7: InteractionChainStartEvent is an EcsEvent with getType /
     setCancelled(boolean) / isCancelled / getContext, AbilitySlots + RuneBag have a static getComponentType and getInventory (the
     names P1-P4 / P14 reach by reflection); the CooldownHandler class names are printed for P3
  P  /aprobe and its 4 usage variants: permission node skyyabilityprobe.admin, empty permission groups, getPermissionGroupsRecursive()
     gives the node to no group (crosscheck.py audits the same with the whole SET)
Not testable without the game: everything the probes are for (research/cloud/Ability-Probe-Plan.md test script).
Scratch: tools/dev/scratch/abilityprobe01/test (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B

VERSION = "0.1"
JAR = os.path.join(HERE, "SkyyAbilityProbe-%s.jar" % VERSION)
PKG = "com.skyy.abilprobe."
CLASSES = sorted(PKG + c for c in ["AbLog", "AbLogic", "AbRefl", "AbState", "AbUnplace", "AbCmds", "AbTick", "AbEarlySys", "AbLateSys",
                                   "AbSeenSys", "AbInvSys", "AbChainSys", "AProbeArg1Cmd", "AProbeArg2Cmd", "AProbeArg3Cmd",
                                   "AProbeArg4Cmd", "AProbeCmd", "SkyyAbilityProbePlugin"])
CMDS = ["AProbeCmd", "AProbeArg1Cmd", "AProbeArg2Cmd", "AProbeArg3Cmd", "AProbeArg4Cmd"]
NODE = "skyyabilityprobe.admin"
CHAIN_EVT = "com.hypixel.hytale.server.core.modules.interaction.event.InteractionChainStartEvent"
ABSLOTS = "com.hypixel.hytale.server.core.inventory.InventoryComponent$AbilitySlots"
RUNEBAG = "com.hypixel.hytale.server.core.inventory.InventoryComponent$RuneBag"
ADRS = "com.hypixel.hytale.server.core.modules.entity.damage.DamageSystems$ArmorDamageReduction"
ASSETS = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
SCRATCH = os.path.join(TOOLS, "dev", "scratch", "abilityprobe01", "test")
KEEP = {"u", "ref", "st", "ns", "nsMax", "ticks"}          # identity + timing totals: never reset by clear()
REST_SPECIAL = {"fxIdx": -1, "p7LastM": -1.0, "p7LastS": -1.0}
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
    check(man["Main"] == PKG + "SkyyAbilityProbePlugin", "J. manifest Main")
    check(man.get("IncludesAssetPack") is False, "J. manifest IncludesAssetPack false (no assets shipped)")
    cls = sorted(n[:-6].replace("/", ".") for n in z.namelist() if n.endswith(".class"))
    check(cls == CLASSES, "J. classes: %s" % cls)
    other = sorted(n for n in z.namelist() if not n.endswith(".class") and n != "manifest.json")
    check(other == [], "J. no asset files (nothing overridden): %s" % other)

    # ---------------- K
    names = set(az.namelist())
    stun = "Server/Entity/Effects/Status/Stun.json"
    check(stun in names and json.loads(az.read(stun).decode("utf-8-sig"))["ApplicationEffects"]["MovementEffects"].get("DisableAll") is True,
          "K. vanilla Stun effect disables movement")
    mana = "Server/Entity/Stats/Mana.json"
    check(mana in names, "K. Mana stat file present")
    if mana in names:
        print("K. Mana.json Max = %s (0.6.8: 0, 0.7: 100)" % json.loads(az.read(mana).decode("utf-8-sig")).get("Max"))

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

    # ---------------- L
    L = JClass(PKG + "AbLogic")
    check(str(L.f1(16.97)) == "17.0" and str(L.f1(float("nan"))) == "?" and str(L.f1(-2.0)) == "-2.0", "L. f1")
    check(str(L.verdict(6.5, 7.0, 0.25)).startswith("PASS") and str(L.verdict(3.0, 7.0, 0.25)).startswith("OFF")
          and str(L.verdict(2.0, 0.0, 0.25)).startswith("n/a"), "L. verdict")
    check(L.number("x", 30, 5, 300) == 30 and L.number("999", 30, 5, 300) == 300 and L.dnum("NaN", 3.0, 0.0, 9.0) == 3.0
          and L.dnum("15", 0.0, 0.0, 90.0) == 15.0, "L. number / dnum")
    SA = JClass("java.lang.String")[:]
    check(L.word(SA(["p1", " "]), 1) is None and L.word(None, 0) is None and str(L.word(SA(["p4", "put", "0", "Rune_X"]), 3)) == "Rune_X",
          "L. word (ids keep their case)")
    r0, r4 = L.ring(10.0, 20.0, 4.0, 0, 16), L.ring(10.0, 20.0, 4.0, 4, 16)
    check(near(r0[0], 14) and near(r0[1], 20) and near(r4[0], 10) and near(r4[1], 24), "L. ring points")
    check(L.lethal(10.0, 10.0) and L.lethal(10.0, 12.0) and not L.lethal(10.0, 9.9) and not L.lethal(0.0, 5.0) and not L.lethal(10.0, 0.0),
          "L. lethal")
    check(near(L.saveHealth(100.0, 30.0), 30.0) and near(L.saveHealth(2.0, 30.0), 1.0) and near(L.saveHealth(0.5, 30.0), 0.5),
          "L. saved Health: 30%, at least 1, never above max")
    check(not L.fight(10.0, 0.5, 9.5, 0.01) and L.fight(10.0, 0.5, 10.0, 0.01), "L. write fight")
    check(L.slotOk(0) and L.slotOk(5) and not L.slotOk(6) and not L.slotOk(-1), "L. slot range 0-5")
    check(L.floorI(-0.5) == -1 and L.floorI(2.9) == 2, "L. floorI")
    check(L.gapOk(300, 1500) and not L.gapOk(0, 1500) and not L.gapOk(2000, 1500), "L. gaps")
    check(L.kind("Ability2") == 1 and L.kind("Ability3") == 1 and L.kind("Primary") == 2 and L.kind("Ability1") == 0 and L.kind(None) == 0,
          "L. chain kinds")
    check(str(L.swingVerdict(0, 0)).startswith("NO") and str(L.swingVerdict(10, 5)).startswith("PASS")
          and str(L.swingVerdict(5, 5)).startswith("UNCLEAR"), "L. swing verdict")
    check(str(L.budget(500.0, 1000.0)).startswith("PASS") and str(L.budget(1500.0, 1000.0)).startswith("OVER"), "L. budget")
    check(L.perSec(30, 1000) == 30.0 and L.perSec(5, 0) == 0.0 and L.avg(10, 0) == 0.0, "L. perSec / avg")

    # ---------------- X
    R = JClass(PKG + "AbRefl")
    AL = JClass("java.util.ArrayList")
    check(int(R.call0(AL(), "size")) == 0 and R.call0(None, "size") is None, "X. call0")
    check("returned Long 5" in str(R.invoke(JClass("java.util.concurrent.atomic.AtomicLong")(5), "addAndGet", "x", 0.0)), "X. invoke")
    check(str(R.invoke(AL(), "nope", "x", 0.0)).startswith("no public"), "X. invoke: missing method")
    CA = JClass("java.lang.Class")[:]
    jc = lambda n: Cls.forName(n)
    f = R.fill(CA([jc("java.lang.String"), JClass("java.lang.Float").TYPE, JClass("java.lang.Double").TYPE, JClass("java.lang.Integer").TYPE,
                   JClass("java.lang.Long").TYPE, JClass("java.lang.Boolean").TYPE, jc("[F")]), "id", 8.0)
    check(f is not None and str(f[0]) == "id" and float(f[1]) == 8.0 and float(f[2]) == 8.0 and int(f[3]) == 0 and int(f[4]) == 0
          and bool(f[5]) is False and float(f[6][0]) == 8.0, "X. fill")
    check(R.fill(CA([jc("java.lang.Object")]), "id", 1.0) is None, "X. fill refuses an Object parameter")
    out = AL()
    check(R.dump(AL(), "ensurecapacity", out, "x ") == 1 and out.size() == 1, "X. dump")
    wh = JClass("java.lang.StringBuilder")()
    check(R.findBy(AL(), "Iterator", wh) is not None and str(wh.toString()).startswith("ArrayList."), "X. findBy")
    check(not R.cancel(JClass("java.lang.Object")()) and not R.cancel(None), "X. cancel on a non-event")
    check(R.static0("java.lang.System", "lineSeparator") is not None and R.static0("no.Such", "x") is None, "X. static0")
    check(R.cls("no.Such") is None and R.cls("java.lang.String") is not None, "X. cls")
    Log, Cmds = JClass(PKG + "AbLog"), JClass(PKG + "AbCmds")
    sink = AL()
    Log.SINK = sink
    Cmds.help(None)
    check(sink.size() == 4, "X. help = 4 lines (%d)" % sink.size())
    check(Cmds.STATES.isEmpty(), "X. no state at start")

    # ---------------- R (the state-reset rule)
    St = JClass(PKG + "AbState")
    fields = [fl for fl in St.class_.getDeclaredFields() if str(fl.getName()) not in KEEP]

    def dirty(s):
        for fl in fields:
            t = str(fl.getType().getName())
            if t == "int":
                fl.setInt(s, 7)
            elif t == "long":
                fl.setLong(s, 7)
            elif t == "double":
                fl.setDouble(s, 7.5)
            elif t == "boolean":
                fl.setBoolean(s, True)
            elif t == "java.lang.String":
                fl.set(s, "x")
            elif t == "java.util.HashSet":
                fl.get(s).add("x")
            elif t == "java.lang.Object":
                fl.set(s, JClass("java.lang.Object")())
            else:
                FAILS.append("R. unhandled AbState field type %s %s - extend the harness" % (t, fl.getName()))

    def not_rest(s):
        bad = []
        for fl in fields:
            n, t, v = str(fl.getName()), str(fl.getType().getName()), fl.get(s)
            if t == "java.util.HashSet":
                if not v.isEmpty():
                    bad.append(n)
                continue
            if n in REST_SPECIAL:
                ok = float(v) == REST_SPECIAL[n]
            elif t in ("int", "long", "double"):
                ok = float(v) == 0.0
            elif t == "boolean":
                ok = not bool(v)
            elif t == "java.lang.String":
                ok = str(v) == ""
            else:
                ok = v is None
            if not ok:
                bad.append("%s=%s" % (n, v))
        return bad

    s = St(JClass("java.util.UUID").randomUUID(), None, None)
    check(not not_rest(s), "R. a fresh state is at rest: %s" % not_rest(s))
    dirty(s)
    Cmds.clear(s)
    check(not not_rest(s), "R. clear() resets EVERY probe field: %s" % not_rest(s))
    W = lambda *ws: SA(list(ws))
    check(Cmds.plan(s, W("p1", "cancel"), 1000) is None and s.mode == 1 and s.cancel and s.modeUntil == 61000, "R. p1 cancel armed")
    dirty(s)
    check(Cmds.plan(s, W("p2"), 2000) is None and s.mode == 2 and not s.cancel and s.p1CheckAt == 0 and s.modeUntil == 22000,
          "R. arming p2 drops p1's cancel flag + pending Mana check")
    s.lines = 5
    s.target = JClass("java.lang.Object")()
    check(Cmds.plan(s, W("p5", "save"), 0) is None and s.save and s.mode == 5 and s.lines == 0 and s.target is None, "R. p5 save")
    check(Cmds.plan(s, W("p6", "SkyyGear_Speed_Fast", "30"), 0) is None and not s.save and str(s.fxId) == "SkyyGear_Speed_Fast"
          and s.modeUntil == 30000 and s.fxIdx == -1, "R. p6 keeps the id's case and drops p5's save")
    check(Cmds.plan(s, W("p6", "none"), 0) is None and str(s.fxId) == "", "R. p6 none = baseline")
    check(Cmds.plan(s, W("p8", "stun"), 0) is None and s.p8Stun and s.modeUntil == 5000, "R. p8 stun")
    check(Cmds.plan(s, W("p8", "4", "10"), 0) is None and not s.p8Stun and s.p8Gap == 250 and s.modeUntil == 10000, "R. p8 hits drop the stun flag")
    check(Cmds.plan(s, W("p9"), 0) is not None and s.mode == 0 and not not_rest(s), "R. p9 without an id is refused, state at rest")
    check(Cmds.plan(s, W("p9", "Magic_Ring", "6"), 0) is None and s.radius == 6.0 and str(s.fxName) == "Magic_Ring", "R. p9")
    check(Cmds.plan(s, W("p10"), 0) is None and s.radius == 6.0 and str(s.fxName) == "", "R. p10 drops p9's particle id")
    check(Cmds.plan(s, W("p13", "500"), 0) is None and s.zones == 256 and s.modeUntil == 10000, "R. p13 zone cap 256")
    check(Cmds.plan(s, W("p4", "watch"), 0) is None and s.mode == 4, "R. p4 watch")
    check(Cmds.plan(s, W("p12", "stun"), 0) is None and s.mode == 12 and s.p8Stun, "R. p12 stun")
    check(Cmds.plan(s, W("zz"), 0) is not None and s.mode == 0 and not not_rest(s), "R. an unknown probe leaves the state at rest")
    for m in (1, 2, 4, 5, 6, 7, 8, 9, 10, 12, 13):
        s.mode, s.armedAt, s.fxId, s.fxName = m, 1, "", "x"
        sink.clear()
        Cmds.summary(s, None, None)
        check(sink.size() == 1, "R. summary P%d = 1 line" % m)
    s.mode = 5
    Cmds.EARLY.put("k", "v")
    Cmds.finish(s, None, "x")
    check(s.mode == 0 and not not_rest(s) and Cmds.EARLY.isEmpty(), "R. finish() clears the state (and P5's maps)")
    Log.SINK = None

    # ---------------- E
    IP = JClass("javassist.ClassPool")
    pool = IP(False)
    pool.appendSystemPath()
    pool.appendClassPath(B.SERVER_JAR)
    JM = JClass("javassist.Modifier")
    sdep = pool.get("com.hypixel.hytale.component.dependency.SystemDependency")
    check(JM.isPublic(sdep.getConstructor("(Lcom/hypixel/hytale/component/dependency/Order;Ljava/lang/Class;)V").getModifiers()),
          "E. SystemDependency(Order, Class) is public")
    for f_ in ("BEFORE", "AFTER"):
        check(JM.isPublic(pool.get("com.hypixel.hytale.component.dependency.Order").getField(f_).getModifiers()), "E. Order.%s" % f_)
    check(pool.getOrNull(ADRS) is not None, "E. DamageSystems$ArmorDamageReduction exists")
    try:
        pool.get("com.hypixel.hytale.component.system.EntityEventSystem").getConstructor("(Ljava/lang/Class;)V")
        OKS[0] += 1
    except Exception as e:
        FAILS.append("E. EntityEventSystem(Class): %s" % e)
    ce = pool.getOrNull(CHAIN_EVT)
    print("E. Hytale 0.7 InteractionChainStartEvent: %s" % ("present" if ce is not None else "absent (0.6.8 - P1 / P2 answer 'needs 0.7')"))
    if ce is not None:
        check(ce.subtypeOf(pool.get("com.hypixel.hytale.component.system.EcsEvent")), "E. the chain event is an EcsEvent")
        mn = set(str(m.getName()) for m in ce.getMethods())
        for need in ("getType", "setCancelled", "isCancelled", "getContext"):
            check(need in mn, "E. InteractionChainStartEvent.%s (P1 reaches it by name)" % need)
    for cn in (ABSLOTS, RUNEBAG):
        c = pool.getOrNull(cn)
        if c is None:
            print("E. %s absent (0.6.8)" % cn.rsplit("$", 1)[1])
            continue
        mn = set(str(m.getName()) for m in c.getMethods())
        check("getComponentType" in mn and "getInventory" in mn, "E. %s.getComponentType + getInventory (P4 / P14 reach them by name)" % cn)
    sj = zipfile.ZipFile(B.SERVER_JAR)
    print("E. CooldownHandler classes for P3: %s" % sorted(n[:-6].replace("/", ".") for n in sj.namelist()
                                                           if n.endswith(".class") and "CooldownHandler" in n)[:6])

    # ---------------- P
    AC = JClass("com.hypixel.hytale.server.core.command.system.AbstractCommand")
    fld = AC.class_.getDeclaredField("permissionGroups")
    fld.setAccessible(True)
    for cn in CMDS:
        try:
            c = JClass(PKG + cn)()
        except Exception as e:
            check(False, "P. construct %s: %s" % (cn, e))
            continue
        perm = c.getPermission()
        groups = fld.get(c)
        check(perm is not None and NODE in str(perm.getId() if hasattr(perm, "getId") else perm), "P. %s requires %s (%s)" % (cn, NODE, perm))
        check(groups is not None and len(groups) == 0, "P. %s permission groups empty (%s)" % (cn, groups))
        if cn == "AProbeCmd":
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
