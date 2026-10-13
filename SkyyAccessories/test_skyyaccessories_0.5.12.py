"""Bare-JVM harness for SkyyAccessories 0.5.12 - THE LANTERN HIDE WITHOUT THE WALK (tools/accessories_0_5_12_patch.py; audit finding 3b).

    python SkyyAccessories/test_skyyaccessories_0.5.12.py [--jar <0.5.12 jar>] [--old <0.5.11 jar>] [--dir <scratch>] [--live <folder>] [--keep]

Every JVM = the game's JRE, -Xverify:all, -XX:-UsePerfData, java.io.tmpdir / TEMP / TMP in the scratch folder.
JVM 1 (both jars, each in its own class loader):
  A  every class of both jars loads, verifies and initialises
  B  0.5.11 -> 0.5.12 class compare: the same classes; changed beyond the version string = exactly AccLantern + AccLanternHide (the config
     kit's Cfg* classes may follow tools/skyycfg.py - listed, never a fail); every non-class file byte-identical except manifest.json
  H  bytecode: AccLantern.hideKnown never calls Set.iterator / getArchetype / getComponent (Set.remove only); AccLanternHide's system tick
     builds the list once (helpersIn) and clears its ThreadLocal; the entity tick takes the fast path or the old walk (hideFrom); step()
     reads OWNER before it writes, and writes only on a change
  L  start twice on a scratch COPY of the live Skyy_SkyyAccessories folder: no file changed
JVMs 2-5 (one per jar per test, the REAL engine entity tracker: EntityStore.REGISTRY + the engine's CollectVisible / AddToVisible /
SendPackets ... + the jar's AccLanternSys / AccLanternHelp / AccLanternHide, see the 0.5.5 harness section Q21):
  Q21  the 0.5.5 harness's run_tracker (imported, unchanged) EXECUTED on 0.5.11 and on 0.5.12: the wearer-only light on the wire,
       lantern.shareReach + /hide, the ring, the view-radius clamp, the dead-man - the same pass / fail list on both jars
  S    A SEEDED SCENARIO run on both jars (6 players, 3 worlds of positions, 120 steps: equip / unequip every rarity, move, shareReach on /
       off, /hide on / off, ORPHAN marked entities injected (the safety net), a player leaving): after every step each viewer's visible
       set of marked entities (owner, slot) and every client's packet count per network id are recorded; the 0.5.11 and the 0.5.12 traces
       must be IDENTICAL (no behaviour change), and on 0.5.12 the fast path ran (FAST > 0), the old walk ran only on ticks with an
       injected orphan, and hideKnown on a counting set (javassist subclass of HashSet) never iterated it while removing exactly the
       foreign helpers; OWNER is written only when a player's entity ref changes (a counting map in its place)
Nothing outside the scratch folder is written (default tools/dev/scratch/perfstore/acc0512, deleted at the end unless --keep).
Exit code 1 on any failure.
"""
import os, sys, re, json, shutil, struct, zipfile, subprocess, random, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.5.12", "0.5.11"
PKG = "com.skyy.accessories."
BUILD = os.path.join(HERE, "build_skyyaccessories_%s.py" % VERSION)
H055 = os.path.join(HERE, "test_skyyaccessories_0.5.5.py")


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default


SCRATCH_ROOT = os.path.abspath(os.path.join(TOOLS, "dev", "scratch"))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCRATCH_ROOT, "perfstore", "acc0512")))
assert SCRATCH.startswith(SCRATCH_ROOT + os.sep), "--dir must be inside tools/dev/scratch/"
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyAccessories-%s.jar" % VERSION)))
OLD = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyAccessories-%s.jar" % OLD_VERSION)))
LIVE = os.path.abspath(arg("--live", os.path.join(os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming"), "Hytale", "UserData",
                                                   "Saves", "HUD mod", "mods", "Skyy_SkyyAccessories")))
KEEP = "--keep" in sys.argv
FAILS, OKS = [], [0]
LANS = ["Skyy_Talisman_Lantern_%s" % w for w in ("Common", "Uncommon", "Rare", "Epic")]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)
    return cond


def cp_utf8(b):
    n = struct.unpack(">H", b[8:10])[0]
    i, k, out = 10, 1, []
    while k < n:
        tag = b[i]
        if tag == 1:
            ln = struct.unpack(">H", b[i + 1:i + 3])[0]
            out.append((i, i + 3 + ln, b[i + 3:i + 3 + ln]))
            i += 3 + ln
        elif tag in (3, 4, 9, 10, 11, 12, 17, 18):
            i += 5
        elif tag in (5, 6):
            i += 9
            k += 1
        elif tag in (7, 8, 16, 19, 20):
            i += 3
        elif tag == 15:
            i += 4
        else:
            raise ValueError("cp tag %d" % tag)
        k += 1
    return out


SKYYUI = re.compile(r"skyyui [0-9.]+ [0-9a-f]{12}")


def norm(t):
    """the shared UI kit's build hash in the ready line (tools/skyyui.py is edited by another round) is not a change of this mod"""
    return SKYYUI.sub("skyyui #", t)


def normcls(b):
    """class bytes with every constant-pool text normalised (version + the kit hash); lengths rewritten"""
    out, last = [], 0
    for s0, e0, t in cp_utf8(b):
        nt = norm(t.decode("utf8").replace(OLD_VERSION, VERSION)).encode("utf8")
        out.append(b[last:s0 + 1])
        out.append(struct.pack(">H", len(nt)) + nt)
        last = e0
    out.append(b[last:])
    return b"".join(out)


def jarfiles(jar):
    z = zipfile.ZipFile(jar)
    out = dict((n, z.read(n)) for n in z.namelist() if not n.endswith("/"))
    z.close()
    return out


def snap(dd):
    out = {}
    for root, _ds, fs in os.walk(dd):
        for f in fs:
            p = os.path.join(root, f)
            out[os.path.relpath(p, dd)] = open(p, "rb").read()
    return out


def startjvm(cp):
    import jpype
    import skyybuild as B
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR, B.JAVASSIST] + cp, convertStrings=True)


def method_code(jarbytes, cls, meth):
    """javassist InstructionPrinter text of every method `meth` of class `cls` (all overloads, joined)"""
    from jpype import JClass
    CP = JClass("javassist.ClassPool")
    pool = CP(True)
    BAIS = JClass("java.io.ByteArrayInputStream")
    cc = pool.makeClass(BAIS(jarbytes))
    IP, PS, BOS = JClass("javassist.bytecode.InstructionPrinter"), JClass("java.io.PrintStream"), JClass("java.io.ByteArrayOutputStream")
    out = []
    for m in cc.getDeclaredMethods():
        if str(m.getName()) != meth:
            continue
        bo = BOS()
        IP.print_(m, PS(bo))
        out.append(str(bo.toString()))
    cc.detach()
    return "\n".join(out)


# ============================================================================================================== JVM 1
def run_unit():
    from jpype import JClass, JArray
    startjvm([])
    Cls = JClass("java.lang.Class")
    sysl = JClass("java.lang.ClassLoader").getSystemClassLoader()
    URL, URLCL, File = JClass("java.net.URL"), JClass("java.net.URLClassLoader"), JClass("java.io.File")
    Paths, System = JClass("java.nio.file.Paths"), JClass("java.lang.System")

    def loader(jar):
        urls = JArray(URL)(1)
        urls[0] = File(jar).toURI().toURL()
        return URLCL(urls, sysl)

    L = {"old": loader(OLD), "new": loader(JAR)}
    F = {"old": jarfiles(OLD), "new": jarfiles(JAR)}
    CB = dict((k, dict((n[:-6].replace("/", "."), b) for n, b in F[k].items() if n.endswith(".class"))) for k in ("old", "new"))
    BR = JClass("java.util.concurrent.ConcurrentHashMap")()
    System.getProperties().put("skyy.bridge", BR)
    # ---------------- A
    na = {"old": 0, "new": 0}
    for k in ("old", "new"):
        for n in sorted(CB[k]):
            try:
                Cls.forName(n, True, L[k])
                OKS[0] += 1
                na[k] += 1
            except Exception as e:
                check(False, "A. %s: load %s: %s" % (k, n, e))
    print("A. loaded + verified + initialised: %s %d, %s %d classes (-Xverify:all)" % (OLD_VERSION, na["old"], VERSION, na["new"]))
    if FAILS:
        return
    # ---------------- B
    old, new = CB["old"], CB["new"]
    check(set(new) == set(old), "B. the same classes: %s" % sorted(set(old) ^ set(new)))
    same, vonly, other = 0, [], []
    for n in sorted(set(old) & set(new)):
        if old[n] == new[n]:
            same += 1
            continue
        co, cn = cp_utf8(old[n]), cp_utf8(new[n])
        ok = len(co) == len(cn)
        rebuilt = new[n]
        if ok:
            for (s0, e0, t0), (s1, e1, t1) in reversed(list(zip(co, cn))):
                if t0 == t1:
                    continue
                if norm(t0.decode("utf8").replace(OLD_VERSION, VERSION)) != norm(t1.decode("utf8")):
                    ok = False
                    break
                rebuilt = rebuilt[:s1] + old[n][s0:e0] + rebuilt[e1:]
        if ok and (rebuilt == old[n] or normcls(old[n]) == normcls(new[n])):
            vonly.append(n[len(PKG):])
        else:
            other.append(n[len(PKG):])
    kit = [n for n in other if n.startswith("Cfg")]
    real = sorted(n for n in other if not n.startswith("Cfg"))
    check(real == ["AccLantern", "AccLanternHide"], "B. changed beyond the version string = exactly AccLantern + AccLanternHide: %s" % real)
    print("B. classes: %d byte-identical, %d version string only, changed: %s; config kit classes following tools/skyycfg.py: %s"
          % (same, len(vonly), real, kit or "none"))
    fo_ = dict((k, v) for k, v in F["old"].items() if not k.endswith(".class"))
    fn_ = dict((k, v) for k, v in F["new"].items() if not k.endswith(".class"))
    diff = sorted(k for k in set(fo_) | set(fn_) if fo_.get(k) != fn_.get(k))
    check(diff == ["manifest.json"], "B. every non-class file byte-identical but manifest.json: %s" % diff)
    mo_, mn_ = json.loads(fo_["manifest.json"]), json.loads(fn_["manifest.json"])
    check(mn_["Version"] == VERSION and dict((k, v) for k, v in mo_.items() if k not in ("Version", "Name")) ==
          dict((k, v) for k, v in mn_.items() if k not in ("Version", "Name")), "B. manifest: only Version / Name")
    # ---------------- H. bytecode
    hk = method_code(new[PKG + "AccLantern"], PKG + "AccLantern", "hideKnown")
    hi = method_code(new[PKG + "AccLantern"], PKG + "AccLantern", "helpersIn")
    st = method_code(new[PKG + "AccLantern"], PKG + "AccLantern", "step")
    ht = method_code(new[PKG + "AccLanternHide"], PKG + "AccLanternHide", "tick")
    hf_old = method_code(old[PKG + "AccLanternHide"], PKG + "AccLanternHide", "tick")
    check("java.util.Set.remove" in hk and "iterator" not in hk and "getArchetype" not in hk and "getComponent" not in hk,
          "H1 hideKnown: Set.remove only - never iterates the visible set, never an archetype / component lookup")
    check("getEntityCountFor" in hi and "HELPER" in hi and "RING" in hi and "Ref.isValid" in hi and "Ref.getStore" in hi,
          "H2 helpersIn: the recorded HELPER + RING refs of this store, checked against the store's marked-entity count")
    check(ht.count("AccLantern.helpersIn") == 1 and ht.count("ThreadLocal.set") == 2 and "ThreadLocal.get" in ht and
          "AccLantern.hideKnown" in ht and "AccLantern.hideFrom" in ht and "getEntityCountFor" in ht,
          "H3 AccLanternHide: the list built once per store tick (ThreadLocal set + cleared), the entity tick = hideKnown or the old walk")
    check("AccLantern.hideFrom" in hf_old and "AccLantern.hideKnown" not in hf_old, "H3 control: 0.5.11 always walked (hideFrom)")
    i_get, i_put = st.find("ConcurrentHashMap.get"), st.find("ConcurrentHashMap.put")
    check(0 <= i_get < i_put and "OWNER" in st[:i_put], "H4 step(): OWNER read first, written after (only when the ref changed)")
    print("H. bytecode: hideKnown = Set.remove only; one helpersIn per store tick; the walk kept as the safety net; OWNER get-then-put")
    # ---------------- L. start twice on a scratch copy of the live folder
    if not os.path.isdir(LIVE):
        print("note: no live Skyy_SkyyAccessories folder - L skipped")
        return
    J = lambda n, k="new": JClass(PKG + n, loader=L[k])
    lm = os.path.join(SCRATCH, "l-mods")
    dlive = os.path.join(lm, "Skyy_SkyyAccessories")
    shutil.copytree(LIVE, dlive)
    before0 = snap(dlive)
    notes = []
    for rnd in range(2):
        J("AccStore").DIR = Paths.get(os.path.join(dlive, "bags"))
        J("AccCfg").FILE = Paths.get(os.path.join(dlive, "config.properties"))
        m51 = str(J("AccCfg").migrate051())
        m55 = str(J("AccCfg").migrate055())
        cs = str(J("AccCfg").load(True))
        J("AccNotice").FILE = Paths.get(os.path.join(dlive, "notices.properties"))
        J("AccNotice").load()
        J("AccLantern").pubLamp()
        J("CfgPub").start(Paths.get(lm), None)
        J("CfgPub").shutdown()
        notes.append((m51, m55, cs[:90]))
    after = snap(dlive)
    chg = sorted(k for k in set(before0) | set(after) if before0.get(k) != after.get(k))
    check(not chg, "L two starts on a copy of the live data: no file changed (%d files) %s" % (len(before0), chg[:4]))
    print("L. two starts on the live copy: %d files unchanged; %s" % (len(before0), notes[-1]))
    BR.clear()


# ============================================================================================================== JVMs 2-5
def load_h055():
    spec = importlib.util.spec_from_file_location("h055", H055)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def lantern_block():
    src = open(BUILD, encoding="utf8").read()
    a_, b_ = src.index("# ---- 0.5.3 NIGHT VISION, RETIRED in 0.5.4"), src.index("CAP = 60          # 0.5: bag STORAGE slots")
    L = {"print": lambda *x, **kw: None}
    exec(compile(src[a_:b_], BUILD + " [LANTERN block]", "exec"), L)
    return L


def child_common(jar):
    from jpype import JClass
    startjvm([jar])
    P = PKG[:-1]
    BR = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", BR)
    Defs, Store = JClass(P + ".AccDefs"), JClass(P + ".AccStore")
    UUID = JClass("java.util.UUID")
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    US = uf.get(None)
    Store.DIR = JClass("java.io.File")(os.path.join(SCRATCH, "bags-" + os.path.basename(jar))).toPath()
    Store.BAGS.clear()
    JClass(P + ".AccLantern").clearAll()
    Defs.lanTable()
    return P, Defs, Store, UUID, US


def run_child_q21(jar, out):
    h = load_h055()
    P, Defs, Store, UUID, US = child_common(jar)
    ll = lantern_block()["lan_light"]
    try:
        h.run_tracker(P, Defs, Store, UUID, US, ll)
    except Exception as e:
        import traceback
        traceback.print_exc()
        h.FAILS.append("run_tracker error: %s" % e)
    json.dump({"ok": h.OKS[0], "fails": h.FAILS}, open(out, "w"))


def run_child_scen(jar, out, newjar):
    """the seeded scenario on the real tracker (setup = the 0.5.5 run_tracker's, copied): trace of every viewer's visible marked set"""
    from jpype import JClass, JImplements, JOverride
    P, Defs, Store, UUID, US = child_common(jar)
    Lan = JClass(P + ".AccLantern")
    Hide = JClass(P + ".AccLanternHide")
    Mark, MarkSup = JClass(P + ".AccLanternMark"), JClass(P + ".AccLanternMarkSup")
    ES = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore")
    ERS, AR = JClass("com.hypixel.hytale.component.EmptyResourceStorage"), JClass("com.hypixel.hytale.component.AddReason")
    RR = JClass("com.hypixel.hytale.component.RemoveReason")
    TC = JClass("com.hypixel.hytale.server.core.modules.entity.component.TransformComponent")
    DLC = JClass("com.hypixel.hytale.server.core.modules.entity.component.DynamicLight")
    NIDC = JClass("com.hypixel.hytale.server.core.modules.entity.tracker.NetworkId")
    INTC = JClass("com.hypixel.hytale.server.core.modules.entity.component.Intangible")
    DESC = JClass("com.hypixel.hytale.server.core.modules.entity.DespawnComponent")
    DTHC = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent")
    PRF = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    TRC = JClass("com.hypixel.hytale.server.core.modules.time.TimeResource")
    T_ = "com.hypixel.hytale.server.core.modules.entity.tracker.EntityTrackerSystems$"
    EVW, VSB = JClass(T_ + "EntityViewer"), JClass(T_ + "Visible")
    HRC = JClass("com.hypixel.hytale.server.core.modules.entity.component.HeadRotation")
    IAC = JClass("com.hypixel.hytale.server.core.modules.entity.component.Interactable")
    KDT = JClass("com.hypixel.hytale.component.spatial.KDTree")
    V3 = JClass("org.joml.Vector3d")
    EMc, TMc = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule"), JClass("com.hypixel.hytale.server.core.modules.time.TimeModule")

    @JImplements("java.util.function.Supplier")
    class Sup(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def get(self):
            return self.f()

    @JImplements("java.util.function.Predicate")
    class Valid(object):
        @JOverride
        def test(self, r_):
            return bool(r_.isValid())

    @JImplements("com.hypixel.hytale.server.core.receiver.IPacketReceiver")
    class Rec(object):
        def __init__(self):
            self.p = []

        @JOverride
        def write(self, pk):
            self.p.append(pk)

        @JOverride
        def writeNoCache(self, pk):
            self.p.append(pk)

    @JImplements("java.util.function.BiConsumer")
    class Collect(object):
        def __init__(self):
            self.refs = []

        @JOverride
        def accept(self, chunk, cb):
            for i_ in range(int(chunk.size())):
                self.refs.append(chunk.getReferenceTo(i_))

    def fld(C_, name_):
        f_ = C_.class_.getDeclaredField(name_)
        f_.setAccessible(True)
        return f_

    REG = ES.REGISTRY
    T_TC = REG.registerComponent(TC, "Transform", TC.CODEC)
    T_DL = REG.registerComponent(DLC, Sup(lambda: DLC()))
    T_NID = REG.registerComponent(NIDC, Sup(lambda: NIDC(0)))
    T_INT = REG.registerComponent(INTC, "Intangible", INTC.CODEC)
    T_DES = REG.registerComponent(DESC, "Despawn", DESC.CODEC)
    T_DTH = REG.registerComponent(DTHC, Sup(lambda: None))
    T_PR = REG.registerComponent(PRF, Sup(lambda: None))
    T_EV = REG.registerComponent(EVW, Sup(lambda: None))
    T_VIS = REG.registerComponent(VSB, Sup(lambda: VSB()))
    T_HR = REG.registerComponent(HRC, Sup(lambda: None))
    T_IA = REG.registerComponent(IAC, Sup(lambda: None))
    T_MARK = REG.registerComponent(Mark, MarkSup())
    R_TIME = REG.registerResource(TRC, "Time", TRC.CODEC)
    R_SP = REG.registerSpatialResource(Sup(lambda: KDT(Valid())))
    em = US.allocateInstance(EMc.class_)
    for name_, v_ in (("transformComponentType", T_TC), ("networkIdComponentType", T_NID), ("dynamicLightComponentType", T_DL),
                      ("visibleComponentType", T_VIS), ("entityViewerComponentType", T_EV), ("headRotationComponentType", T_HR),
                      ("despawnComponentComponentType", T_DES), ("interactableComponentType", T_IA), ("intangibleComponentType", T_INT),
                      ("networkSendableSpatialResourceType", R_SP)):
        fld(EMc, name_).set(em, v_)
    tm = US.allocateInstance(TMc.class_)
    fld(TMc, "timeResourceType").set(tm, R_TIME)
    fld(EMc, "instance").set(None, em)
    fld(TMc, "instance").set(None, tm)
    Lan.T_TC, Lan.T_DL, Lan.T_NID, Lan.T_INT, Lan.T_DES, Lan.T_DEATH, Lan.T_PR, Lan.T_EV = T_TC, T_DL, T_NID, T_INT, T_DES, T_DTH, T_PR, T_EV
    Lan.T_MARK, Lan.R_TIME = T_MARK, R_TIME
    Lan.clearAll()
    for s_ in [JClass("com.hypixel.hytale.server.core.modules.entity.system.NetworkSendableSpatialSystem")(R_SP),
               JClass(T_ + "ClearEntityViewers")(T_EV), JClass(T_ + "CollectVisible")(T_EV), JClass(T_ + "ClearPreviouslyVisible")(T_VIS),
               JClass(T_ + "EnsureVisibleComponent")(T_EV, T_VIS), JClass(T_ + "AddToVisible")(T_EV, T_VIS),
               JClass(T_ + "RemoveEmptyVisibleComponent")(T_VIS),
               JClass("com.hypixel.hytale.server.core.modules.entity.system.EntitySystems$DynamicLightTracker")(T_VIS),
               JClass("com.hypixel.hytale.server.core.modules.entity.dynamiclight.DynamicLightSystems$EntityTrackerRemove")(T_VIS),
               JClass("com.hypixel.hytale.server.core.modules.entity.system.TransformSystems$EntityTrackerUpdate")(),
               JClass(T_ + "SendPackets")(T_EV), JClass("com.hypixel.hytale.server.core.modules.entity.DespawnSystem")(T_DES),
               JClass(P + ".AccLanternSys")(), JClass(P + ".AccLanternHelp")(), JClass(P + ".AccLanternHide")()]:
        REG.registerSystem(s_)
    w1 = REG.addStore(ES(None), ERS.get())
    HPM = JClass("com.hypixel.hytale.server.core.entity.entities.player.HiddenPlayersManager")
    hid_f = fld(HPM, "hiddenPlayers")
    rnd = random.Random(5120)
    names = ["Ava", "Ben", "Cal", "Dee", "Eli", "Fay"]
    uu = [UUID.nameUUIDFromBytes(("acc0512-" + n).encode()) for n in names]
    byu = dict((str(u), n) for u, n in zip(uu, names))
    players = {}

    def spawn(i):
        rec = Rec()
        h_ = REG.newHolder()
        tc = TC()
        tc.setPosition(V3(0.5 + 9.0 * i, 64.0, 0.5 + 4.0 * (i % 3)))
        h_.addComponent(T_TC, tc)
        h_.addComponent(T_PR, PRF(None, uu[i], names[i], "en-US", None, None))
        h_.addComponent(T_NID, NIDC(int(w1.getExternalData().takeNextNetworkId())))
        h_.addComponent(T_EV, EVW(640, rec))
        players[i] = (w1.addEntity(h_, AR.SPAWN), rec)

    for i in range(len(names)):
        spawn(i)

    def tick(n=1):
        for _q in range(n):
            w1.tick(1.0 / 30.0)

    def marked():
        cl = Collect()
        w1.forEachChunk(T_MARK, cl)
        return cl.refs

    def view():
        """every viewer's visible marked entities as sorted (owner, slot) + the HIDDEN counter"""
        out = {}
        for i, (r_, _rec) in sorted(players.items()):
            v = w1.getComponent(r_, T_EV)
            lst = []
            for m_ in marked():
                if bool(v.visible.contains(m_)):
                    mk = w1.getComponent(m_, T_MARK)
                    lst.append("%s/%d" % (byu.get(str(mk.owner), "?") if mk.owner is not None else "-", int(mk.slot)))
            out[names[i]] = sorted(lst)
        return out

    def packets():
        """per client: how many entity updates / removals it got for each marked entity's owner (the wire, summed)"""
        out = {}
        nid_owner = {}
        for m_ in marked():
            nid_owner[int(w1.getComponent(m_, T_NID).getId())] = byu.get(str(w1.getComponent(m_, T_MARK).owner), "?")
        for i, (_r, rec) in sorted(players.items()):
            c = {}
            for pk in rec.p:
                if pk.updates is not None:
                    for eu in pk.updates:
                        o = nid_owner.get(int(eu.networkId))
                        if o is not None:
                            c[o] = c.get(o, 0) + 1
            out[names[i]] = sorted(c.items())
        return out

    trace = []
    orphan_steps = []
    tick(2)
    for step in range(120):
        a = rnd.random()
        i = rnd.randrange(len(names))
        u = uu[i]
        act = None
        if i not in players:
            spawn(i)
            act = "rejoin %s" % names[i]
        elif a < 0.30:
            t = rnd.randrange(4)
            Lan.SPAWNT.remove(u)
            Lan.RSPAWNT.remove(u)
            Store.unequipK(u, str(u), 0)
            Store.equipK(u, str(u), LANS[t])
            act = "equip %s %s" % (names[i], LANS[t])
        elif a < 0.42:
            Store.unequipK(u, str(u), 0)
            act = "unequip %s" % names[i]
        elif a < 0.55:
            r_ = players[i][0]
            w1.getComponent(r_, T_TC).setPosition(V3(rnd.uniform(-40, 40), 64.0, rnd.uniform(-40, 40)))
            act = "move %s" % names[i]
        elif a < 0.63:
            Defs.LAN_SHARE = not bool(Defs.LAN_SHARE)
            act = "share %s" % bool(Defs.LAN_SHARE)
        elif a < 0.75:
            j = rnd.randrange(len(names))
            if j != i and j in players:
                hs = hid_f.get(w1.getComponent(players[i][0], T_PR).getHiddenPlayersManager())
                if hs.contains(uu[j]):
                    hs.remove(uu[j])
                    act = "%s unhides %s" % (names[i], names[j])
                else:
                    hs.add(uu[j])
                    act = "%s hides %s" % (names[i], names[j])
        elif a < 0.85:
            # an ORPHAN: a marked entity nobody recorded (a parked copy coming back) - AccLanternHelp removes it on its tick
            h_ = REG.newHolder()
            tc = TC()
            tc.setPosition(V3(rnd.uniform(-20, 20), 90.0, rnd.uniform(-20, 20)))
            h_.addComponent(T_TC, tc)
            h_.addComponent(T_NID, NIDC(int(w1.getExternalData().takeNextNetworkId())))
            h_.addComponent(T_MARK, Mark(u, rnd.randrange(3)))
            w1.addEntity(h_, AR.SPAWN)
            orphan_steps.append(step)
            act = "orphan of %s" % names[i]
        elif a < 0.90 and len(players) > 2:
            r_ = players.pop(i)[0]
            w1.removeEntity(r_, RR.REMOVE)
            act = "leave %s" % names[i]
        if act is None:
            act = "idle"
        tick(1)
        v1 = view()
        tick(1)
        trace.append({"step": step, "act": act, "v1": v1, "v2": view()})
    trace.append({"packets": packets(), "HIDDEN": int(Lan.HIDDEN.get())})
    res = {"trace": trace, "orphans": orphan_steps}
    if newjar:
        res["FAST"], res["WALKS"] = int(Hide.FAST.get()), int(Hide.WALKS.get())
        # hideKnown on a COUNTING set: never iterated, removes exactly the foreign helpers of the list
        CP = JClass("javassist.ClassPool")
        pool = CP(True)
        cc = pool.makeClass("skyyacctest.CountSet", pool.get("java.util.HashSet"))
        cc.addField(JClass("javassist.CtField").make("public static int ITER = 0;", cc))
        cc.addMethod(JClass("javassist.CtNewMethod").make("public java.util.Iterator iterator() { ITER++; return super.iterator(); }", cc))
        cc.addConstructor(JClass("javassist.CtNewConstructor").make("public CountSet() { super(); }", cc))
        cdir = os.path.join(SCRATCH, "cls")
        cc.writeFile(cdir)
        URL, URLCL, File = JClass("java.net.URL"), JClass("java.net.URLClassLoader"), JClass("java.io.File")
        from jpype import JArray
        urls = JArray(URL)(1)
        urls[0] = File(cdir).toURI().toURL()
        tcl = URLCL(urls, JClass("java.lang.ClassLoader").getSystemClassLoader())
        CS = tcl.loadClass("skyyacctest.CountSet")
        for i in sorted(players):
            Lan.SPAWNT.remove(uu[i])
            Lan.RSPAWNT.remove(uu[i])
            Store.unequipK(uu[i], str(uu[i]), 0)
            Store.equipK(uu[i], str(uu[i]), LANS[3])
        Defs.LAN_SHARE = False
        tick(3)
        known = Lan.helpersIn(w1)
        refs, owners, full = list(known[0]), [str(x) for x in known[1]], bool(known[2])
        ok_cs = []
        for i in sorted(players):
            cs = CS.getDeclaredConstructor().newInstance()
            for r_ in marked():
                cs.add(r_)
            cs.add(players[i][0])
            n0 = int(cs.size())
            cls_ = CS
            itf = cls_.getDeclaredField("ITER")
            itf.setInt(None, 0)
            n = int(Lan.hideKnown(uu[i], None, cs, known))
            mine = sum(1 for o in owners if o == str(uu[i]))
            ok_cs.append(int(itf.getInt(None)) == 0 and n == len(refs) - mine and int(cs.size()) == n0 - n and
                         bool(cs.contains(players[i][0])) and all(not bool(cs.contains(r_)) for r_, o in zip(refs, owners) if o != str(uu[i])))
        res["countset"] = {"ok": all(ok_cs) and len(ok_cs) > 1 and full and len(refs) >= len(players) * 6, "refs": len(refs), "full": full}
        # OWNER writes: a counting map in its place, 60 ticks with nobody moving entity
        from jpype import JClass as JC
        cm = pool.makeClass("skyyacctest.CountMap", pool.get("java.util.concurrent.ConcurrentHashMap"))
        cm.addField(JClass("javassist.CtField").make("public static int PUTS = 0;", cm))
        cm.addMethod(JClass("javassist.CtNewMethod").make("public Object put(Object k, Object v) { PUTS++; return super.put(k, v); }", cm))
        cm.addConstructor(JClass("javassist.CtNewConstructor").make("public CountMap() { super(); }", cm))
        cm.writeFile(cdir)
        CM = URLCL(urls, JClass("java.lang.ClassLoader").getSystemClassLoader()).loadClass("skyyacctest.CountMap")
        ow_f = fld(Lan, "OWNER")
        mf = fld(JC("java.lang.reflect.Field"), "modifiers") if False else None
        res["ownerputs"] = None
        try:
            # OWNER is final: swap its contents through Unsafe (staticFieldBase / offset)
            UC_ = JClass("sun.misc.Unsafe").class_
            OBJ_, FLD_, LNG_ = JClass("java.lang.Object"), JClass("java.lang.reflect.Field"), JClass("java.lang.Long").TYPE

            def ucall(name, types, *vals):
                from jpype import JArray as JA
                m_ = UC_.getMethod(name, *types)
                a_ = JA(OBJ_)(len(vals))
                for q_, v_ in enumerate(vals):
                    a_[q_] = v_
                return m_.invoke(US, a_)
            base = ucall("staticFieldBase", [FLD_], ow_f)
            off = int(ucall("staticFieldOffset", [FLD_], ow_f))
            JL = JClass("java.lang.Long")
            prev = ucall("getObject", [OBJ_, LNG_], base, JL(off))
            cmap = CM.getDeclaredConstructor().newInstance()
            cmap.putAll(prev)
            CM.getDeclaredField("PUTS").setInt(None, 0)
            ucall("putObject", [OBJ_, LNG_, OBJ_], base, JL(off), cmap)
            tick(60)
            p60 = int(CM.getDeclaredField("PUTS").get(None))
            # a world change for one player = a new entity ref -> exactly one write for that player
            i0 = sorted(players)[0]
            w1.removeEntity(players.pop(i0)[0], RR.REMOVE)
            spawn(i0)
            tick(1)
            p61 = int(CM.getDeclaredField("PUTS").get(None))
            ucall("putObject", [OBJ_, LNG_, OBJ_], base, JL(off), prev)
            prev.putAll(cmap)
            res["ownerputs"] = [p60, p61 - p60]
        except Exception as e:
            import traceback
            traceback.print_exc()
            res["ownerputs"] = "error %s" % e
    json.dump(res, open(out, "w"))


# ============================================================================================================== parent
def child(mode, jar, out, extra=()):
    env = dict(os.environ)
    env.pop("JAVA_TOOL_OPTIONS", None)
    tmp = os.path.join(SCRATCH, "tmp")
    env["TEMP"], env["TMP"] = tmp, tmp
    return subprocess.call([sys.executable, os.path.abspath(__file__), "--child", mode, "--cjar", jar, "--out", out, "--dir", SCRATCH]
                           + list(extra), env=env, cwd=ROOT)


def main():
    if "--child" in sys.argv:
        mode, jar, out = arg("--child"), arg("--cjar"), arg("--out")
        if mode == "unit":
            try:
                run_unit()
            except Exception as e:
                import traceback
                traceback.print_exc()
                FAILS.append("harness error: %s" % e)
            json.dump({"ok": OKS[0], "fails": FAILS}, open(out, "w"))
        elif mode == "q21":
            run_child_q21(jar, out)
        elif mode == "scen":
            run_child_scen(jar, out, "--newjar" in sys.argv)
        return 0
    for j in (JAR, OLD):
        if not os.path.isfile(j):
            print("no jar at", j, "- build it first")
            return 1
    if os.path.getmtime(JAR) < os.path.getmtime(BUILD):
        print("the jar is older than", BUILD, "- rebuild it first")
        return 1
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(os.path.join(SCRATCH, "tmp"))
    os.environ["TEMP"] = os.environ["TMP"] = os.path.join(SCRATCH, "tmp")
    res = {}
    for name, mode, jar, extra in (("unit", "unit", JAR, ()), ("q21-old", "q21", OLD, ()), ("q21-new", "q21", JAR, ()),
                                   ("scen-old", "scen", OLD, ()), ("scen-new", "scen", JAR, ("--newjar",))):
        out = os.path.join(SCRATCH, name + ".json")
        print("---- JVM %s (%s)" % (name, os.path.basename(jar)))
        sys.stdout.flush()
        rc = child(mode, jar, out, extra)
        try:
            res[name] = json.load(open(out))
        except Exception as e:
            check(False, "%s: no result (exit %s): %s" % (name, rc, e))
    u = res.get("unit", {"ok": 0, "fails": ["missing"]})
    OKS[0] += u["ok"]
    FAILS.extend(u["fails"])
    qo, qn = res.get("q21-old"), res.get("q21-new")
    if qo and qn:
        check(qn["fails"] == qo["fails"], "Q21 the 0.5.5 tracker checks: the same result on both jars (old fails %s, new fails %s)"
              % (qo["fails"], qn["fails"]))
        check(not qn["fails"] and qn["ok"] >= 10, "Q21 the real tracker checks all pass on 0.5.12 (%d ok, fails %s)" % (qn["ok"], qn["fails"][:3]))
        print("Q21. run_tracker (0.5.5 harness, unchanged) on 0.5.11: %d ok %d fail; on 0.5.12: %d ok %d fail"
              % (qo["ok"], len(qo["fails"]), qn["ok"], len(qn["fails"])))
    so, sn = res.get("scen-old"), res.get("scen-new")
    if so and sn:
        to, tn = so["trace"], sn["trace"]
        first = next((k for k in range(min(len(to), len(tn))) if to[k] != tn[k]), None)
        check(len(to) == len(tn) and first is None, "S the scenario traces are IDENTICAL on 0.5.11 and 0.5.12 (first difference: %s)"
              % (None if first is None else (to[first], tn[first])))
        acts = [t.get("act") for t in tn if "act" in t]
        kinds = set(a.split(" ")[0] for a in acts)
        seen = sum(len(x) for t in tn if "v2" in t for x in t["v2"].values())
        check(set(["equip", "unequip", "move", "share", "orphan", "leave", "rejoin"]) <= kinds and seen > 50,
              "S the scenario covered every action (%s) and saw marked entities (%d sightings)" % (sorted(kinds), seen))
        check(sn["FAST"] > 0 and sn["WALKS"] > 0 and sn["FAST"] > 5 * sn["WALKS"], "S 0.5.12 took the fast path (%d viewer ticks) and the "
              "old walk only around injected orphans (%d viewer ticks, %d orphans)" % (sn["FAST"], sn["WALKS"], len(sn["orphans"])))
        check(sn.get("countset", {}).get("ok"), "S hideKnown on a counting set: never iterated, removed exactly the foreign helpers, kept the "
              "viewer's own and the player entity: %s" % sn.get("countset"))
        check(sn.get("ownerputs") == [0, 1], "S OWNER: 0 writes over 60 ticks with nobody's entity changing, exactly 1 for a player whose "
              "entity was replaced: %s" % (sn.get("ownerputs"),))
        print("S. scenario: %d steps identical on both jars (%d sightings, %d orphans); 0.5.12 fast %d / walk %d viewer ticks; counting set %s;"
              " OWNER writes %s" % (len(acts), seen, len(sn["orphans"]), sn["FAST"], sn["WALKS"], sn.get("countset"), sn.get("ownerputs")))
    print("SkyyAccessories %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS[:40]:
        print("  FAIL", f)
    return 1 if FAILS else 0


if __name__ == "__main__":
    code = main()
    if not KEEP and "--child" not in sys.argv:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    sys.stdout.flush()
    os._exit(code)
