"""Bare-JVM harness for SkyyAccessories 0.5.10 - THE MINING HELMET LIGHT (tools/accessories_0_5_10_patch.py; Skyy: "make sure that if those
mining helmets show a light, it works"). SkyyGear 0.2.15 posts gear:lamp:<uuid> (1-4); the player glows like a Lantern of that rarity.

    python SkyyAccessories/test_skyyaccessories_0.5.10.py [--jar <0.5.10 jar>] [--old <0.5.9 jar>] [--gear <SkyyGear-0.2.15.jar>]
                                                          [--dir <scratch>] [--live <folder>] [--keep]

One JVM (the game's JRE, -Xverify:all, -XX:-UsePerfData, java.io.tmpdir in the scratch folder), each jar in its own class loader:
  A  every class of both jars loads, verifies and initialises (+ SkyyGear 0.2.15's GearMine, the real poster of gear:lamp)
  B  0.5.9 -> 0.5.10 class compare: classes changed ONLY where the patch says (AccLantern: + helmetTier, pubLamp, step changed; AccDefs:
     + LAN_HELMET; AccCfg: + LAN_HELMET_KEY, load changed; AccTick.run; plugin setup / shutdown; the kit's rows / defaults), every other
     class byte-identical or version constants only; every non-class file byte-identical except manifest.json (Version)
  C  config: the Server Setup row lantern.helmet (bool, on, live), the fresh default file holds lantern.helmet=true, load(): missing = on,
     false = off; acc:lamp on / off (pubLamp)
  S  helmetTier on the bridge: absent / Integer 1-4 / clamp 9 -> 4 / String "2" / junk / profile:busy / lantern.helmet off
  W  THE REAL ENGINE ECS STORE (a ComponentRegistry with the engine's component classes, the jar's AccLanternSys + AccLanternHelp ticked by
     Store.tick, 30 ticks = 1 s):
     W0 Lantern ONLY, no gear:lamp key: the same tick script on 0.5.9 and 0.5.10 -> identical traces (glow, helpers, positions, lights)
     W1 key posted by SkyyGear's own GearMine.postLamp -> glow + hidden lights = a Lantern of that rarity (WANT row identical), <= 1 s
     W2 tier changes 1 -> 4 -> 2 follow within 1 s; W3 key removed (GearMine.clear) -> light and helpers gone within 1 s (+ despawn)
     W4 Lantern + helmet: the stronger wins, one DynamicLight only (never stacked), both directions
     W5 line.Lantern off: helmet still lights; lantern.helmet off: helmet light off within 1 s, Lantern unaffected
     W6 profile switch: profile:busy -> off; profile 2 (no Lantern) + helmet -> helmet tier; back to profile 1 -> max again
     W7 logout: entity removed + AccTick's prune -> no state left, helpers gone; rejoin without the key -> no light
  L  start twice on a scratch COPY of the live Skyy_SkyyAccessories folder: no file changed
Nothing outside the scratch folder is written (default tools/dev/scratch/acc0510/acc-harness, deleted at the end unless --keep).
"""
import os, sys, re, json, shutil, struct, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.5.10", "0.5.9"
PKG = "com.skyy.accessories."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default


SCRATCH_ROOT = os.path.abspath(os.path.join(TOOLS, "dev", "scratch"))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCRATCH_ROOT, "acc0510", "acc-harness")))
assert SCRATCH.startswith(SCRATCH_ROOT + os.sep), "--dir must be inside tools/dev/scratch/"
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyAccessories-%s.jar" % VERSION)))
OLD = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyAccessories-%s.jar" % OLD_VERSION)))
GEAR = os.path.abspath(arg("--gear", os.path.join(ROOT, "SkyyGear", "SkyyGear-0.2.15.jar")))
LIVE = os.path.abspath(arg("--live", os.path.join(os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming"), "Hytale", "UserData",
                                                   "Saves", "HUD mod", "mods", "Skyy_SkyyAccessories")))
KEEP = "--keep" in sys.argv
FAILS, OKS = [], [0]
LAN_IDS = ["Skyy_Talisman_Lantern_%s" % w for w in ("Common", "Uncommon", "Rare", "Epic")]


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
            raise ValueError("constant pool tag %d" % tag)
        k += 1
    return out


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


def run():
    import jpype
    from jpype import JClass, JArray, JImplements, JOverride
    import skyybuild as B
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR, B.JAVASSIST], convertStrings=True)
    Cls = JClass("java.lang.Class")
    sysl = JClass("java.lang.ClassLoader").getSystemClassLoader()
    URL, URLCL, File = JClass("java.net.URL"), JClass("java.net.URLClassLoader"), JClass("java.io.File")
    Paths = JClass("java.nio.file.Paths")
    System = JClass("java.lang.System")
    Integer = JClass("java.lang.Integer")
    UUID = JClass("java.util.UUID")

    def loader(jar):
        urls = JArray(URL)(1)
        urls[0] = File(jar).toURI().toURL()
        return URLCL(urls, sysl)

    L = {"old": loader(OLD), "new": loader(JAR), "gear": loader(GEAR)}
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
    gm_name = [n[:-6].replace("/", ".") for n in jarfiles(GEAR) if n.endswith("/GearMine.class")]
    check(len(gm_name) == 1, "A. SkyyGear 0.2.15 has GearMine")
    GearMine = Cls.forName(gm_name[0], True, L["gear"]) if gm_name else None
    GM = JClass(gm_name[0], loader=L["gear"]) if gm_name else None
    print("A. loaded + verified + initialised: %s %d, %s %d classes (-Xverify:all) + SkyyGear GearMine" % (OLD_VERSION, na["old"], VERSION, na["new"]))
    if FAILS:
        return

    # ---------------- B
    old, new = CB["old"], CB["new"]
    check(set(new) == set(old), "B. the same classes: %s" % sorted(set(old) ^ set(new)))
    CP = JClass("javassist.ClassPool")
    BAIS = JClass("java.io.ByteArrayInputStream")
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def ct(b):
        return CP(False).makeClass(BAIS(b))

    def code_of(m):
        mi = m.getMethodInfo()
        ca = mi.getCodeAttribute()
        cp = mi.getConstPool()
        if ca is None:
            return ["<no code>"]
        it, rows = ca.iterator(), []
        while it.hasNext():
            pos = it.next()
            rows.append((pos, re.sub(r"#\d+ = ", "", str(IP.instructionString(it, pos, cp)))))
        idx = dict((p, i) for i, (p, _t) in enumerate(rows))
        idx[int(ca.getCodeLength())] = len(rows)
        out = []
        for _p, t in rows:
            t = re.sub(r"^ldc_w ", "ldc ", t)
            mm = re.match(r"^(if\w*|goto(?:_w)?|jsr(?:_w)?) (\d+)$", t)
            if mm:
                t = "%s @%d" % (mm.group(1), idx[int(mm.group(2))])
            out.append(t)
        et = ca.getExceptionTable()
        for i in range(et.size()):
            ctp = et.catchType(i)
            out.append("try @%d @%d @%d %s" % (idx[et.startPc(i)], idx[et.endPc(i)], idx[et.handlerPc(i)], cp.getClassInfo(ctp) if ctp else "any"))
        return out

    def methods(c):
        out = {}
        for m in list(c.getDeclaredMethods()) + list(c.getDeclaredConstructors()):
            out[str(m.getMethodInfo().getName()) + str(m.getSignature())] = code_of(m)
        ci = c.getClassInitializer()
        if ci is not None:
            out["<clinit>"] = code_of(ci)
        return out

    def vonly(a, b):
        return len(a) == len(b) and all(x == y or x.replace(OLD_VERSION, VERSION) == y for x, y in zip(a, b))

    report = {}
    for n in sorted(set(old) & set(new)):
        short = n[len(PKG):]
        if old[n] == new[n]:
            continue
        co, cn = cp_utf8(old[n]), cp_utf8(new[n])
        if len(co) == len(cn):
            rebuilt, okv = new[n], True
            for (s0, e0, t0), (s1, e1, t1) in reversed(list(zip(co, cn))):
                if t0 == t1:
                    continue
                if t0.decode("utf8").replace(OLD_VERSION, VERSION) != t1.decode("utf8"):
                    okv = False
                    break
                rebuilt = rebuilt[:s1] + old[n][s0:e0] + rebuilt[e1:]
            if okv and rebuilt == old[n]:
                continue
        po, pn = ct(old[n]), ct(new[n])
        fo = set((str(f.getName()), str(f.getSignature())) for f in po.getDeclaredFields())
        fn = set((str(f.getName()), str(f.getSignature())) for f in pn.getDeclaredFields())
        mo, mn = methods(po), methods(pn)
        changed = sorted(k.split("(")[0] for k in mo if k in mn and mo[k] != mn[k] and not vonly(mo[k], mn[k]))
        report[short] = (sorted(f[0] for f in fn - fo), sorted(f[0] for f in fo - fn), sorted(k.split("(")[0] for k in set(mn) - set(mo)),
                         sorted(k.split("(")[0] for k in set(mo) - set(mn)), changed)
    for k_, v_ in sorted(report.items()):
        print("   B. %s: +fields %s -fields %s +methods %s -methods %s changed %s" % ((k_,) + v_))
    check(report.get("AccLantern") == ([], [], ["helmetTier", "pubLamp"], [], ["step"]), "B. AccLantern: + helmetTier, pubLamp; step changed: %s" % (report.get("AccLantern"),))
    check(report.get("AccDefs") == (["LAN_HELMET"], [], [], [], ["<clinit>"]), "B. AccDefs: + LAN_HELMET (its initialiser): %s" % (report.get("AccDefs"),))
    check(report.get("AccCfg") is not None and report["AccCfg"][0] == ["LAN_HELMET_KEY"] and report["AccCfg"][1:4] == ([], [], []) and
          set(report["AccCfg"][4]) <= {"load", "writeDefaults"}, "B. AccCfg: + LAN_HELMET_KEY; load + writeDefaults (the default text) changed: %s" % (report.get("AccCfg"),))
    check(report.get("AccTick") == ([], [], [], [], ["run"]), "B. AccTick: run changed (pubLamp): %s" % (report.get("AccTick"),))
    check(report.get("SkyyAccessoriesPlugin") is not None and report["SkyyAccessoriesPlugin"][:4] == ([], [], [], []) and
          set(report["SkyyAccessoriesPlugin"][4]) <= {"setup", "shutdown", "<clinit>"} and "shutdown" in report["SkyyAccessoriesPlugin"][4],
          "B. plugin: setup / shutdown changed: %s" % (report.get("SkyyAccessoriesPlugin"),))
    kit_ok = all(k_.startswith("Cfg") and v_[:4] == ([], [], [], []) for k_, v_ in report.items()
                 if k_ not in ("AccLantern", "AccDefs", "AccCfg", "AccTick", "SkyyAccessoriesPlugin"))
    check(kit_ok, "B. any other changed class is a config kit class with only data / method bodies changed: %s" % sorted(report))
    fo_, fn_ = dict((k, v) for k, v in F["old"].items() if not k.endswith(".class")), dict((k, v) for k, v in F["new"].items() if not k.endswith(".class"))
    check(set(fo_) == set(fn_), "B. no file added or removed: %s" % sorted(set(fo_) ^ set(fn_)))
    diff = sorted(k for k in fo_ if k in fn_ and fo_[k] != fn_[k])
    check(diff == ["manifest.json"], "B. only manifest.json changed among the assets (no art, item or lang change): %s" % diff)
    mo_, mn_ = json.loads(fo_["manifest.json"]), json.loads(fn_["manifest.json"])
    check(mn_["Version"] == VERSION and dict((k, v) for k, v in mo_.items() if k not in ("Version", "Name")) ==
          dict((k, v) for k, v in mn_.items() if k not in ("Version", "Name")), "B. manifest: only Version / Name")
    print("B. changed classes: %s; assets: only manifest.json" % sorted(report))

    # ---------------- C. config
    J = lambda n, k="new": JClass(PKG + n, loader=L[k])
    Defs, Store, Cfg, Lan = J("AccDefs"), J("AccStore"), J("AccCfg"), J("AccLantern")
    rows = new[PKG + "CfgRows"].decode("latin-1")
    check("lantern.helmet" in rows and "Mining helmet light" in rows and "LAN_HELMET" in rows and "Off = SkyyGear mining helmets light nothing" in rows,
          "C1 the Server Setup row lantern.helmet (Mining helmet light, field AccDefs.LAN_HELMET)")
    allb = b"".join(v for k, v in new.items()).decode("latin-1")
    check("lantern.helmet=true" in allb and "Set lantern.helmet to false to switch helmet lights off." in allb, "C2 the fresh default file has lantern.helmet=true + its comment")
    cdir = os.path.join(SCRATCH, "cfg")
    os.makedirs(cdir)
    cf = os.path.join(cdir, "config.properties")
    Cfg.FILE = Paths.get(cf)
    Store.DIR = Paths.get(os.path.join(cdir, "bags"))
    r0 = str(Cfg.load(True))
    txt = open(cf, encoding="latin-1").read()
    check("lantern.helmet=true" in txt and bool(Defs.LAN_HELMET), "C3 a first start writes lantern.helmet=true, LAN_HELMET on (%s)" % r0[:60])
    open(cf, "w", encoding="latin-1", newline="").write(txt.replace("lantern.helmet=true", "lantern.helmet=false"))
    r1 = str(Cfg.load(False))
    check(not bool(Defs.LAN_HELMET) and "mining helmet light switched off" in r1, "C4 lantern.helmet=false -> off, the load text says so")
    Lan.pubLamp()
    check(str(BR.get("acc:lamp")) == "off", "C5 acc:lamp = off while off")
    open(cf, "w", encoding="latin-1", newline="").write(txt.replace("lantern.helmet=true\n", "").replace("lantern.helmet=true\r\n", ""))
    r2 = str(Cfg.load(False))
    check(bool(Defs.LAN_HELMET) and "lantern.helmet=" not in open(cf, encoding="latin-1").read(), "C6 the key missing = on (the file is not rewritten)")
    Lan.pubLamp()
    check(str(BR.get("acc:lamp")) == "on", "C7 acc:lamp = on")
    print("C. config row, default, load on / off / missing, acc:lamp")

    # ---------------- S. helmetTier on the bridge
    u0 = UUID.randomUUID()
    k0 = "gear:lamp:" + str(u0)
    HT = lambda: int(Lan.helmetTier(u0))
    check(HT() == 0, "S1 no key -> 0")
    res = []
    for v in (1, 2, 3, 4):
        BR.put(k0, Integer.valueOf(v))
        res.append(HT())
    check(res == [1, 2, 3, 4], "S2 Integer 1-4 -> 1-4: %s" % res)
    BR.put(k0, Integer.valueOf(9))
    a9 = HT()
    BR.put(k0, "2")
    a2 = HT()
    BR.put(k0, "lamp")
    ax = HT()
    BR.put(k0, Integer.valueOf(0))
    a0 = HT()
    check((a9, a2, ax, a0) == (4, 2, 0, 0), "S3 9 -> 4, \"2\" -> 2, junk -> 0, 0 -> 0: %s" % ((a9, a2, ax, a0),))
    BR.put(k0, Integer.valueOf(3))
    BR.put("profile:busy:" + str(u0), True)
    ab = HT()
    BR.remove("profile:busy:" + str(u0))
    Defs.LAN_HELMET = False
    ao = HT()
    Defs.LAN_HELMET = True
    check((ab, ao, HT()) == (0, 0, 3), "S4 profile:busy -> 0, lantern.helmet off -> 0, both cleared -> 3")
    if GM is not None:
        GM.postLamp(u0, 2)
        g2 = BR.get(k0)
        check(isinstance(g2, int) or str(g2.getClass().getName()) == "java.lang.Integer", "S5 SkyyGear's postLamp posts a java.lang.Integer")
        check(HT() == 2, "S5 ... read as 2")
        GM.clear(u0)
        check(BR.get(k0) is None and HT() == 0, "S5 SkyyGear's clear removes it -> 0")
    BR.remove(k0)
    print("S. helmetTier: Integer / clamp / String / junk / busy / off / SkyyGear's own poster")

    # ---------------- W. the real engine ECS store
    CR = JClass("com.hypixel.hytale.component.ComponentRegistry")
    TC = JClass("com.hypixel.hytale.server.core.modules.entity.component.TransformComponent")
    DLC = JClass("com.hypixel.hytale.server.core.modules.entity.component.DynamicLight")
    NIDC = JClass("com.hypixel.hytale.server.core.modules.entity.tracker.NetworkId")
    INTC = JClass("com.hypixel.hytale.server.core.modules.entity.component.Intangible")
    DESC = JClass("com.hypixel.hytale.server.core.modules.entity.DespawnComponent")
    DTHC = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent")
    PRF = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    TRC = JClass("com.hypixel.hytale.server.core.modules.time.TimeResource")
    ES, ERS = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore"), JClass("com.hypixel.hytale.component.EmptyResourceStorage")
    AR, RR = JClass("com.hypixel.hytale.component.AddReason"), JClass("com.hypixel.hytale.component.RemoveReason")
    V3, Duration = JClass("org.joml.Vector3d"), JClass("java.time.Duration")
    DT = 1.0 / 30.0

    @JImplements("java.util.function.Supplier")
    class Sup(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def get(self):
            return self.f()

    @JImplements("java.util.function.BiConsumer")
    class Collect(object):
        def __init__(self):
            self.refs = []

        @JOverride
        def accept(self, chunk, cb):
            for i_ in range(int(chunk.size())):
                self.refs.append(chunk.getReferenceTo(i_))

    class World(object):
        def __init__(self, k):
            self.k = k
            self.Lan, self.Mark, self.MarkSup = J("AccLantern", k), J("AccLanternMark", k), J("AccLanternMarkSup", k)
            self.Defs, self.Store = J("AccDefs", k), J("AccStore", k)
            Lk = self.Lan
            reg = CR()
            Lk.T_TC = reg.registerComponent(TC, "Transform", TC.CODEC)
            Lk.T_DL = reg.registerComponent(DLC, Sup(lambda: DLC()))
            Lk.T_NID = reg.registerComponent(NIDC, Sup(lambda: NIDC(0)))
            Lk.T_INT = reg.registerComponent(INTC, "Intangible", INTC.CODEC)
            Lk.T_DES = reg.registerComponent(DESC, "Despawn", DESC.CODEC)
            Lk.T_DEATH = reg.registerComponent(DTHC, Sup(lambda: None))
            Lk.T_PR = reg.registerComponent(PRF, Sup(lambda: None))
            Lk.T_MARK = reg.registerComponent(self.Mark, self.MarkSup())
            Lk.R_TIME = reg.registerResource(TRC, "Time", TRC.CODEC)
            reg.registerSystem(JClass(PKG + "AccLanternSys", loader=L[k])())
            reg.registerSystem(JClass(PKG + "AccLanternHelp", loader=L[k])())
            self.reg = reg
            self.w = reg.addStore(ES(None), ERS.get())
            self.Store.DIR = Paths.get(os.path.join(SCRATCH, "bags-" + k))
            self.Store.BAGS.clear()
            Lk.clearAll()

        def player(self, u, name, x, y, z):
            h = self.reg.newHolder()
            tc = TC()
            tc.setPosition(V3(x, y, z))
            h.addComponent(self.Lan.T_TC, tc)
            h.addComponent(self.Lan.T_PR, PRF(None, u, name, "en-US", None, None))
            return self.w.addEntity(h, AR.SPAWN)

        def tick(self, n=1):
            for _q in range(n):
                self.w.tick(DT)

        def helpers(self, owner=None):
            cl = Collect()
            self.w.forEachChunk(self.Lan.T_MARK, cl)
            out = []
            for r_ in cl.refs:
                m_ = self.w.getComponent(r_, self.Lan.T_MARK)
                if owner is None or (m_ is not None and m_.owner is not None and m_.owner.equals(owner)):
                    out.append(r_)
            return out

        def gkey(self, r_):
            d_ = self.w.getComponent(r_, self.Lan.T_DL)
            return None if d_ is None else int(self.Defs.lanKeyOf(d_.getColorLight()))

        def pos(self, r_):
            p_ = self.w.getComponent(r_, self.Lan.T_TC).getPosition()
            return (round(float(p_.x()), 4), round(float(p_.y()), 4), round(float(p_.z()), 4))

        def move(self, r_, x, y, z):
            self.w.getComponent(r_, self.Lan.T_TC).setPosition(V3(x, y, z))

        def state(self, r_, u):
            hs = self.helpers(u)
            return (self.gkey(r_), tuple(sorted((self.pos(h), self.gkey(h)) for h in hs)))

        def want(self, u):
            w_ = self.Lan.WANT.get(u)
            return None if w_ is None else tuple(int(x) for x in w_)

    # W0: the Lantern-only script on both jars -> identical traces
    def script(Wd, u, ref, trace):
        def rec(n):
            for _ in range(n):
                Wd.tick()
                trace.append(Wd.state(ref, u))
        rec(35)
        for i, lid in enumerate(LAN_IDS):
            Wd.Store.equipK(u, str(u), lid)
            rec(40)
            for step_ in range(1, 11):
                Wd.move(ref, 10.5 + step_ * 0.7 + i, 64.0 + (step_ % 3), -3.25 - step_ * 0.5)
                rec(1)
        for i in range(4):
            Wd.Store.unequip(u, i)
        rec(40)
    ua = UUID.fromString("00000000-0000-0000-0000-0000000a0510")
    traces = {}
    worlds = {}
    for k in ("old", "new"):
        Wd = World(k)
        worlds[k] = Wd
        ra = Wd.player(ua, "Alice", 10.5, 64.0, -3.25)
        tr_ = []
        script(Wd, ua, ra, tr_)
        traces[k] = tr_
        Wd.w.removeEntity(ra, RR.REMOVE)
        Wd.Lan.prune(JClass("java.util.HashSet")())
    lit = sum(1 for t_ in traces["new"] if t_[0] is not None)
    withh = sum(1 for t_ in traces["new"] if t_[1])
    check(traces["old"] == traces["new"] and lit > 100 and withh > 50,
          "W0 Lantern only, no gear:lamp: 0.5.9 and 0.5.10 give the identical trace over %d ticks (%d lit, %d with hidden lights)" % (
              len(traces["new"]), lit, withh))
    first_diff = [i for i, (a_, b_) in enumerate(zip(traces["old"], traces["new"])) if a_ != b_][:1]
    if first_diff:
        print("   first difference at tick", first_diff[0], traces["old"][first_diff[0]], traces["new"][first_diff[0]])

    Wd = worlds["new"]
    LanN = Wd.Lan
    ub, uc = UUID.fromString("00000000-0000-0000-0000-0000000b0510"), UUID.fromString("00000000-0000-0000-0000-0000000c0510")
    kb = "gear:lamp:" + str(ub)

    def ticks_until(cond, limit=45):
        for n_ in range(1, limit + 1):
            Wd.tick()
            if cond():
                return n_
        return None

    def exp_key(t):
        g_ = int(Wd.Defs.lanGlow(t))
        return int(Wd.Defs.lanKey(g_)) if g_ > 0 else None

    rb = Wd.player(ub, "Bob", 40.5, 70.0, 12.5)            # helmet wearer, empty bag
    rc = Wd.player(uc, "Cara", -40.5, 70.0, -12.5)          # Lantern wearer (reference rows)
    Wd.tick(40)
    check(Wd.gkey(rb) is None and not Wd.helpers(ub), "W1 no key, no Lantern: Bob has no light")
    # W1: SkyyGear's own poster, tier by tier = the same WANT row / glow / hidden lights as a Lantern of that rarity
    rowsok = []
    for t in (1, 2, 3, 4):
        GM.postLamp(ub, t)
        Wd.Store.equipK(uc, str(uc), LAN_IDS[t - 1])
        n_ = ticks_until(lambda: Wd.want(ub) is not None and Wd.want(ub)[0] == t)
        Wd.tick(40)
        wb_, wc_ = Wd.want(ub), Wd.want(uc)
        hb, hc = Wd.helpers(ub), Wd.helpers(uc)
        sb = sorted(Wd.gkey(h) for h in hb)
        sc = sorted(Wd.gkey(h) for h in hc)
        ok = (n_ is not None and n_ <= 31 and wb_ == wc_ and Wd.gkey(rb) == Wd.gkey(rc) == exp_key(t) and sb == sc and
              len(hb) == len(hc) and (t == 1) == (len(hb) == 0))
        rowsok.append(ok)
        check(ok, "W1 helmet tier %d (posted by GearMine.postLamp): lit after %s ticks (<= 31), WANT %s = a Lantern's %s, glow %s, %d hidden lights %s = %s" % (
            t, n_, wb_, wc_, Wd.gkey(rb), len(hb), sb, sc))
        dl = Wd.w.getComponent(rb, LanN.T_DL)
        check(dl is not None, "W1 the glow is a DynamicLight on the player (one component: never two lights)")
    # W2: tier changes follow within a second
    for t in (4, 2):
        GM.postLamp(ub, t)
        n_ = ticks_until(lambda: Wd.want(ub) is not None and Wd.want(ub)[0] == t and Wd.gkey(rb) == exp_key(t))
        check(n_ is not None and n_ <= 31, "W2 tier -> %d within a second (%s ticks)" % (t, n_))
    Wd.tick(40)
    check((len(Wd.helpers(ub)) > 0), "W2 tier 2 keeps hidden lights (Unique)")
    # W3: GearMine.clear -> off within a second, helpers removed
    GM.clear(ub)
    n_ = ticks_until(lambda: Wd.want(ub) is None and Wd.gkey(rb) is None)
    check(BR.get(kb) is None and n_ is not None and n_ <= 31, "W3 key removed (GearMine.clear): no glow after %s ticks (<= 31)" % n_)
    Wd.tick(10)
    check(not Wd.helpers(ub) and LanN.HELPER.get(ub) is None, "W3 ... and the hidden lights are gone")
    # W4: Lantern + helmet: the stronger wins both ways, never stacked
    Wd.Store.equipK(ub, str(ub), LAN_IDS[1])               # Unique Lantern in Bob's bag
    GM.postLamp(ub, 3)                                      # Rare helmet
    Wd.tick(35)
    w4a = Wd.want(ub)
    GM.postLamp(ub, 1)                                      # Normal helmet < Unique Lantern
    Wd.tick(35)
    LanN.SPAWNT.remove(ub)                                  # the 1-spawn-per-REAL-second limit (the harness ticks faster than real time)
    LanN.RSPAWNT.remove(ub)
    Wd.tick(35)
    w4b = Wd.want(ub)
    check(w4a is not None and w4a[0] == 3 and Wd.want(uc) is not None and w4b is not None and w4b[0] == 2 and Wd.gkey(rb) == exp_key(2),
          "W4 Unique Lantern + Rare helmet -> Rare (%s); + Normal helmet -> the Lantern's Unique (%s): the stronger wins" % (w4a, w4b))
    hs4 = Wd.helpers(ub)
    check(len(hs4) > 0 and len(set(int(Wd.w.getComponent(h, LanN.T_MARK).slot) for h in hs4)) == len(hs4),
          "W4 one set of hidden lights only (%d, slots distinct) = the Unique row %s" % (len(hs4), Wd.want(ub)))
    # W5: line.Lantern off -> helmet still lights; lantern.helmet off -> helmet off within a second, the Lantern unaffected
    Wd.Defs.LINE_LANTERN = False
    Wd.tick(35)
    check(Wd.want(ub) is not None and Wd.want(ub)[0] == 1 and Wd.want(uc) is None, "W5 line.Lantern off: Bob keeps the helmet light (Normal), Cara's Lantern is off")
    Wd.Defs.LINE_LANTERN = True
    Wd.Defs.LAN_HELMET = False
    GM.postLamp(ub, 4)
    for i_ in range(4):
        Wd.Store.unequip(ub, i_)
    check(int(Wd.Defs.lanBest(Wd.Store.snapshot(ub))) == 0, "W5 Bob's bag has no Lantern now")
    n_ = ticks_until(lambda: Wd.want(ub) is None)
    Wd.tick(35)
    check(n_ is not None and n_ <= 31 and Wd.gkey(rb) is None and Wd.want(ub) is None and Wd.want(uc) is not None, "W5 lantern.helmet off: Bob dark within %s ticks, Cara's Lantern lit" % n_)
    Wd.Defs.LAN_HELMET = True
    n_ = ticks_until(lambda: Wd.want(ub) is not None and Wd.want(ub)[0] == 4)
    check(n_ is not None and n_ <= 31, "W5 back on: Legendary helmet light within %s ticks" % n_)
    # W6: profile switch (profile:fn:key decides the bag; profile:busy during the switch)
    prof = {"p": "1"}

    @JImplements("java.util.function.Function")
    class KeyFn(object):
        @JOverride
        def apply(self, x):
            return str(x) + "-p" + prof["p"] if str(x) == str(ub) else str(x)
    BR.put("profile:fn:key", KeyFn())
    Wd.Store.BAGS.clear()
    Wd.Store.equipK(ub, str(ub) + "-p1", LAN_IDS[3])         # profile 1: Legendary Lantern
    GM.postLamp(ub, 1)
    Wd.Store.LPOKE.put(ub, True)
    Wd.tick(35)
    p1 = Wd.want(ub)
    BR.put("profile:busy:" + str(ub), True)
    GM.clear(ub)                                            # SkyyGear clears on profile:busy
    prof["p"] = "2"
    Wd.Store.LPOKE.put(ub, True)
    Wd.tick(35)
    busy = Wd.want(ub)
    BR.remove("profile:busy:" + str(ub))
    GM.postLamp(ub, 3)                                      # the profile-2 inventory wears a Rare helmet
    Wd.tick(35)
    p2 = Wd.want(ub)
    BR.put("profile:busy:" + str(ub), True)
    Wd.tick(35)
    busy2 = Wd.want(ub)
    BR.remove("profile:busy:" + str(ub))
    prof["p"] = "1"
    Wd.Store.LPOKE.put(ub, True)
    Wd.tick(35)
    back = Wd.want(ub)
    check(p1 is not None and p1[0] == 4 and busy is None and p2 is not None and p2[0] == 3 and busy2 is None and back is not None and back[0] == 4,
          "W6 profile 1 (Legendary Lantern + Normal helmet) -> 4; switching (busy) -> dark; profile 2 (no Lantern, Rare helmet) -> 3; "
          "a stale key while busy -> dark; profile 1 again -> 4: %s" % ([None if x is None else x[0] for x in (p1, busy, p2, busy2, back)],))
    BR.remove("profile:fn:key")
    # W7: logout (entity removed + AccTick's prune), rejoin without the key
    LanN.SPAWNT.remove(ub)
    LanN.RSPAWNT.remove(ub)
    Wd.tick(35)
    hb7 = Wd.helpers(ub)
    Wd.w.removeEntity(rb, RR.REMOVE)
    GM.clear(ub)
    HS = JClass("java.util.HashSet")()
    HS.add(uc)
    LanN.prune(HS)
    Wd.tick(10)
    TRr = Wd.w.getResource(LanN.R_TIME)
    TRr.add(Duration.ofSeconds(6))
    Wd.tick(5)
    gone = all(getattr(LanN, f_).get(ub) is None for f_ in ("WANT", "OWNER", "HELPER", "RING", "CLK"))
    check(len(hb7) > 0 and gone and not Wd.helpers(ub), "W7 logout: no state left for Bob, his %d hidden lights gone" % len(hb7))
    rb2 = Wd.player(ub, "Bob", 40.5, 70.0, 12.5)
    Wd.tick(40)
    check(Wd.gkey(rb2) is None and not Wd.helpers(ub) and Wd.want(ub) is None, "W7 rejoin without the key and with an empty bag: no light")
    GM.postLamp(ub, 2)
    n_ = ticks_until(lambda: Wd.want(ub) is not None)
    check(n_ is not None and n_ <= 31 and Wd.want(ub)[0] == 2, "W7 rejoin + helmet on -> Unique within %s ticks" % n_)
    GM.clear(ub)
    print("W. real ECS store: Lantern-only = 0.5.9, helmet tiers = Lantern rows, max not stack, switches, profiles, logout")

    # ---------------- L. start twice on a scratch copy of the live folder
    if not os.path.isdir(LIVE):
        print("note: no live Skyy_SkyyAccessories folder - L skipped")
        return
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
        notes.append((m51, m55, cs[:90], bool(J("AccDefs").LAN_HELMET), str(BR.get("acc:lamp"))))
    after = snap(dlive)
    chg = sorted(k for k in set(before0) | set(after) if before0.get(k) != after.get(k))
    check(not chg, "L two starts on a copy of the live data: no file changed (%d files) %s" % (len(before0), chg[:4]))
    check(notes[-1][3] and notes[-1][4] == "on", "L the live config (no lantern.helmet line) -> helmet light on, acc:lamp on")
    print("L. two starts on the live copy: %d files unchanged; %s" % (len(before0), notes[-1]))
    BR.clear()


def main():
    for j in (JAR, OLD, GEAR):
        if not os.path.isfile(j):
            print("no jar at", j)
            return 1
    if os.path.exists(SCRATCH):
        shutil.rmtree(SCRATCH)
    os.makedirs(SCRATCH)
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    os.environ["TEMP"] = tmp
    os.environ["TMP"] = tmp
    try:
        run()
    except Exception as e:
        import traceback
        traceback.print_exc()
        FAILS.append("harness error: %s" % e)
    print("SkyyAccessories %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS[:40]:
        print("  FAIL", f)
    return 1 if FAILS else 0


if __name__ == "__main__":
    code = main()
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    sys.stdout.flush()
    os._exit(code)
