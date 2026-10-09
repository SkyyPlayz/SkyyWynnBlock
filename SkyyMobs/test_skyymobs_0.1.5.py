"""Harness for SkyyMobs 0.1.5 (mob:fn:levelAt - the zone level at a block, for SkyyGear's loot chests and SkyyExploration's Unclaimed Luggage).
Build first: python tools/mobs_0_1_5_patch.py && python SkyyMobs/build_skyymobs_0.1.5.py

    python SkyyMobs/test_skyymobs_0.1.5.py [--jar <SkyyMobs-0.1.5.jar>] [--dir <scratch>] [--keep]

Children (fresh JVMs, the game's JRE, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in scratch):
  A  every class loads + verifies (-Xverify:all)
  X  EVERY NEW PATH EXECUTED (-Xverify:all): MobLevelAtFn.at on stand-in worlds through the REAL MobLevel.lookupAt / resolve (default band,
     a min of 0, the level cap, part.levels off, an island world through island:owner:fn, the world thread vs any other thread - the "-2d"
     step), MobLevelAtFn.apply (the world by name through a stand-in Universe, bad arguments, an unknown world, NaN / huge coordinates, 20,000
     calls from 4 threads), world() / onThread() never throw; setup() / shutdown() put + remove the bridge (bytecode)
  C  CLASS COMPARE 0.1.4 -> 0.1.5: one class added (MobLevelAtFn), the plugin's setup / shutdown and the version texts changed, nothing else
  D  START TWICE on a scratch COPY of the live Skyy_SkyyMobs folder in setup()'s order (MobMig.run, MobMig14.run, MobCfg.load): every file
     byte-identical (0.1.5 has no row, no file, no update)
  AA THE ENGINE-ACCESS AUDIT (MethodHandles.privateLookupIn every referencing class)
Scratch: tools/dev/scratch/loot01/mobs (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, re, threading

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B

VERSION = "0.1.5"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyMobs-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMobs-0.1.4.jar")
SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "loot01", "mobs")))
PKG = "com.skyy.mobs."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyMobs")
FAILS, OKS = [], [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def _jvm(cp, verify=True):
    import jpype
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    opts = (["-Xverify:all"] if verify else []) + ["-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp]
    jpype.startJVM(jvm, *opts, classpath=list(cp), convertStrings=True)


class Child(object):
    def __init__(self, out):
        self.out, self.ok, self.fails, self.notes = out, 0, [], []

    def check(self, cond, what):
        if cond:
            self.ok += 1
        else:
            self.fails.append(what)
            print("FAIL", what)

    def save(self):
        json.dump({"ok": self.ok, "fails": self.fails, "notes": self.notes}, open(self.out, "w"), indent=1)


def jar_classes(j):
    return sorted(n[:-6].replace("/", ".") for n in zipfile.ZipFile(j).namelist() if n.endswith(".class"))


def run_verify(out):
    from jpype import JClass
    K = Child(out)
    _jvm([B.SERVER_JAR, JAR])
    Cls, loader = JClass("java.lang.Class"), JClass("java.lang.ClassLoader").getSystemClassLoader()
    names = jar_classes(JAR)
    for n in names:
        try:
            Cls.forName(n, True, loader)
            K.ok += 1
        except Exception as e:
            K.check(False, "A: load + verify %s: %s" % (n, str(e)[:300]))
    K.notes.append("A: %d classes loaded + initialised with -Xverify:all" % len(names))
    K.save()


def run_x(out):
    from jpype import JClass, JArray, JObject, JInt, JDouble, JImplements, JOverride
    K = Child(out)
    _jvm([B.SERVER_JAR, B.JAVASSIST, JAR])
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    us = uf.get(None)

    def jf(c, n):
        k = c.class_ if hasattr(c, "class_") else c
        while k is not None:
            try:
                f = k.getDeclaredField(n)
                f.setAccessible(True)
                return f
            except Exception:
                k = k.getSuperclass()
        raise KeyError(n)
    Cfg, Lat, Lv = JClass(PKG + "MobCfg"), JClass(PKG + "MobLevelAtFn"), JClass(PKG + "MobLevel")
    WLD = JClass("com.hypixel.hytale.server.core.universe.world.World")
    UNI = JClass("com.hypixel.hytale.server.core.universe.Universe")
    CHM = JClass("java.util.concurrent.ConcurrentHashMap")
    br = CHM()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)

    def world(name):
        w_ = us.allocateInstance(WLD.class_)
        jf(WLD, "name").set(w_, name)
        return w_
    uni = us.allocateInstance(UNI.class_)
    worlds = CHM()
    jf(UNI, "worlds").set(uni, worlds)
    jf(UNI, "instance").set(None, uni)
    w1 = world("Default")
    worlds.put("default", w1)
    Cfg.useDefaults()

    def at(w_, on_):
        r_ = Lat.at(w_, JDouble(10.5), JDouble(70.0), JDouble(-3.2), on_)
        return None if r_ is None else [int(r_[0]), int(r_[1]), str(r_[2]), str(r_[3])]
    r0 = at(w1, False)
    K.check(r0 is None, "X: the shipped bands.default 0 (no level anywhere unmatched) -> null: %s" % r0)
    Cfg.DEF_A, Cfg.DEF_B = 12, 16
    r1, r2 = at(w1, False), at(w1, True)
    K.check(r1 == [12, 16, "default-2d", "bands.default"] and r2 == [12, 16, "default", "bands.default"],
            "X: default band 12-16: off the world thread the 2D lookup ('-2d'), on it the full lookup: %s / %s" % (r1, r2))
    Cfg.DEF_A, Cfg.DEF_B = 0, 5
    r3 = at(w1, False)
    Cfg.DEF_A, Cfg.DEF_B = 12, 16
    old_max = int(Cfg.MAX_LEVEL)
    Cfg.MAX_LEVEL = 14
    r4 = at(w1, False)
    Cfg.MAX_LEVEL = old_max
    K.check(r3 is not None and r3[:2] == [1, 5] and r4 is not None and r4[:2] == [12, 14],
            "X: a band min of 0 counts as 1 (levelFor's rule) %s; levels.max caps the high end %s" % (r3, r4))
    Cfg.ON = False
    r5 = at(w1, False)
    Cfg.ON = True
    K.check(r5 is None, "X: part.levels off -> null")

    @JImplements("java.util.function.Function")
    class Owner:
        @JOverride
        def apply(self, wn):
            return "someone" if str(wn).startswith("skyy-island-") else None
    br.put("island:owner:fn", Owner())
    wi = world("skyy-island-abc")
    r6 = at(wi, False)
    Cfg.ISL_A, Cfg.ISL_B = 1, 3
    r7 = at(wi, False)
    Cfg.ISL_A, Cfg.ISL_B = 0, 0
    K.check(r6 is None and r7 is not None and r7[:2] == [1, 3] and r7[2].startswith("island"),
            "X: a SkyyIslands island (island:owner:fn) -> bands.islands: 0 = null %s, 1-3 when set %s" % (r6, r7))
    fn = Lat()
    a1 = fn.apply(JArray(JObject)(["Default", JInt(10), JInt(70), JInt(-3)]))
    a2 = fn.apply(JArray(JObject)(["DEFAULT", JDouble(10.0), JDouble(70.0), JDouble(-3.0)]))
    bad = [fn.apply(x_) for x_ in (None, "Default", JArray(JObject)(["Default", JInt(1)]), JArray(JObject)([JInt(1), JInt(1), JInt(1), JInt(1)]),
                                   JArray(JObject)(["Nowhere", JInt(1), JInt(1), JInt(1)]),
                                   JArray(JObject)(["Default", JDouble(float("nan")), JInt(1), JInt(1)]),
                                   JArray(JObject)(["Default", JDouble(5.0e9), JInt(1), JInt(1)]),
                                   JArray(JObject)(["", JInt(1), JInt(1), JInt(1)]))]
    K.check(a1 is not None and [int(a1[0]), int(a1[1])] == [12, 16] and str(a1[2]).endswith("-2d") and a2 is not None and all(b_ is None for b_ in bad),
            "X: apply(): the world by name (any case, Universe.getWorld), a stand-in world is never 'in thread' (-2d); bad arguments / unknown "
            "world / NaN / huge coordinates / an empty name -> null")
    K.check(Lat.world(None) is None and Lat.world("x-none") is None and not bool(Lat.onThread(None)) and not bool(Lat.onThread(w1)),
            "X: world() / onThread() never throw")
    errs = []

    def hammer():
        try:
            for i in range(5000):
                r_ = fn.apply(JArray(JObject)(["Default", JInt(i), JInt(64), JInt(-i)]))
                if r_ is None or int(r_[0]) != 12:
                    errs.append(i)
                    return
        except Exception as e_:
            errs.append(str(e_))
    import jpype
    ths = [threading.Thread(target=hammer) for _ in range(4)]
    for t_ in ths:
        t_.start()
    for t_ in ths:
        t_.join()
    K.check(not errs and int(Lv.WG.size()) <= int(Lv.WG_MAX), "X: 20,000 calls from 4 threads: always 12-16, the worldgen cache stays bounded (%s)" % errs[:3])
    # setup() / shutdown(): the bridge put / removed (bytecode - setup needs a server)
    CP = JClass("javassist.ClassPool")(False)
    CP.appendSystemPath()
    CP.appendClassPath(B.SERVER_JAR)
    CP.appendClassPath(JAR)
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def bc(cn, m):
        out_ = []
        for mm in CP.get(cn).getDeclaredMethods():
            if str(mm.getName()) == m:
                bos = JClass("java.io.ByteArrayOutputStream")()
                IP(JClass("java.io.PrintStream")(bos)).print_(mm)
                out_.append(str(bos.toString()))
        return "\n".join(out_)
    su, sd = bc(PKG + "SkyyMobsPlugin", "setup"), bc(PKG + "SkyyMobsPlugin", "shutdown")
    K.check('"mob:fn:levelAt"' in su and "MobLevelAtFn.<init>" in su and su.index('"mob:fn:info"') < su.index('"mob:fn:levelAt"')
            and '"mob:fn:levelAt"' in sd and "Map.remove" in sd,
            "X: setup() puts mob:fn:levelAt (after mob:fn:info), shutdown() removes it")
    K.save()


def run_compare(out):
    from jpype import JClass
    K = Child(out)
    _jvm([B.JAVASSIST], verify=False)
    CPc = JClass("javassist.ClassPool")
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def pool_of(j):
        p_ = CPc(False)
        p_.appendSystemPath()
        p_.appendClassPath(B.SERVER_JAR)
        p_.appendClassPath(j)
        return p_
    pa, pb = pool_of(OLD_JAR), pool_of(JAR)

    def members(p_, cn):
        c_ = p_.get(cn)
        d_ = {}

        def code(b_):
            mi_ = b_.getMethodInfo()
            ca_ = mi_.getCodeAttribute()
            if ca_ is None:
                return ""
            it_ = ca_.iterator()
            lines_ = []
            while it_.hasNext():
                pos_ = it_.next()
                lines_.append(re.sub(r"#\d+ = ", "", str(IP.instructionString(it_, pos_, mi_.getConstPool()))))
            return "\n".join(lines_)
        for f_ in c_.getDeclaredFields():
            d_["f " + str(f_.getName())] = str(f_.getSignature())
        for m_ in c_.getDeclaredMethods():
            d_["m " + str(m_.getName()) + str(m_.getSignature())] = code(m_)
        for m_ in c_.getDeclaredConstructors():
            d_["c " + str(m_.getSignature())] = code(m_)
        if c_.getClassInitializer() is not None:
            d_["<clinit>"] = code(c_.getClassInitializer())
        return d_
    na, nb = jar_classes(OLD_JAR), jar_classes(JAR)
    added = sorted(set(nb) - set(na))
    K.check(added == [PKG + "MobLevelAtFn"] and not (set(na) - set(nb)), "C: one class added (MobLevelAtFn), none removed: %s" % added)
    diffs = {}
    for cn in sorted(set(na) & set(nb)):
        ma, mb = members(pa, cn), members(pb, cn)
        dd = sorted(k for k in set(ma) | set(mb) if ma.get(k) != mb.get(k))
        if dd:
            diffs[cn[len(PKG):]] = [("+" if k not in ma else ("-" if k not in mb else "~")) + k.split("(")[0] for k in dd]
    print("C. class compare 0.1.4 -> 0.1.5: %s" % json.dumps(diffs, sort_keys=True))
    # MobCfg.load / reloadAll / useDefaults hold the "# SkyyMobs <VERSION> settings / level bands" file headers (version text only)
    allowed = {"SkyyMobsPlugin": {"~m setup", "~m shutdown"}, "CfgRows": {"~<clinit>", "~m header"}, "CfgFn": {"~m opExport"},
               "MobCfg": {"~m load", "~m reloadAll", "~m useDefaults"}}
    K.check(all(k in allowed and set(v) <= allowed[k] for k, v in diffs.items()) and "SkyyMobsPlugin" in diffs,
            "C: only setup / shutdown + the version texts differ: %s" % diffs)
    for cn_, ms_ in (("MobCfg", ("load", "reloadAll", "useDefaults")), ("CfgRows", ("header",)), ("CfgFn", ("opExport",))):
        for m_ in ms_:
            for k_ in [k for k in members(pa, PKG + cn_) if k.startswith("m " + m_ + "(")]:
                o_, n_ = members(pa, PKG + cn_)[k_], members(pb, PKG + cn_)[k_]
                ol_, nl_ = o_.splitlines(), n_.splitlines()
                dl_ = [(x_, y_) for x_, y_ in zip(ol_, nl_) if x_ != y_ and x_.replace("0.1.4", "0.1.5") != y_]
                K.check(len(ol_) == len(nl_) and not dl_, "C: %s.%s differs only by the version text: %s" % (cn_, m_, str(dl_[:2])[:600]))
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    ed = sorted(n for n in set(za.namelist()) | set(zb.namelist()) if not n.endswith(".class") and (n not in za.namelist() or n not in zb.namelist() or za.read(n) != zb.read(n)))
    K.check(ed == ["manifest.json"], "C: non-class entries: only manifest.json changed: %s" % ed)
    K.save()


def run_live(out, home):
    from jpype import JClass
    K = Child(out)
    _jvm([B.SERVER_JAR, JAR])
    Cfg, Mig, Mig14 = JClass(PKG + "MobCfg"), JClass(PKG + "MobMig"), JClass(PKG + "MobMig14")
    Paths = JClass("java.nio.file.Paths")
    d = Paths.get(home)
    Cfg.DIR = d
    Cfg.FILE = d.resolve("config.properties")
    Cfg.BANDS = d.resolve("bands.properties")

    def snap():
        out_ = {}
        for r_, ds_, fs_ in os.walk(home):
            for f_ in fs_:
                p_ = os.path.join(r_, f_)
                out_[os.path.relpath(p_, home)] = open(p_, "rb").read()
        return out_
    before = snap()
    for step in (1, 2):
        m1, m2 = str(Mig.run(d)), str(Mig14.run(d))
        Cfg.load()
        after = snap()
        K.check(after == before and m1 == "" and m2 == "", "D start %d: setup()'s order changes no file (%d files) and runs no update (%r, %r)" % (step, len(after), m1, m2))
    K.save()


def run_audit(out):
    from jpype import JClass
    _jvm([B.SERVER_JAR, B.JAVASSIST, JAR], verify=False)
    Cls, loader = JClass("java.lang.Class"), JClass("java.lang.ClassLoader").getSystemClassLoader()
    CP = JClass("javassist.ClassPool")(False)
    CP.appendSystemPath()
    CP.appendClassPath(B.SERVER_JAR)
    CP.appendClassPath(JAR)
    MH = JClass("java.lang.invoke.MethodHandles")
    MTc, CPool, JMod_ = JClass("java.lang.invoke.MethodType"), JClass("javassist.bytecode.ConstPool"), JClass("java.lang.reflect.Modifier")
    XOPS = {0xb2: 1, 0xb3: 1, 0xb4: 1, 0xb5: 1, 0xb6: 1, 0xb7: 1, 0xb8: 1, 0xb9: 1, 0xba: 1, 0xbb: 1, 0xbd: 1, 0xc0: 1, 0xc1: 1, 0xc5: 1, 0x12: 1, 0x13: 1}

    def jc(n_):
        return Cls.forName(n_.replace("/", "."), False, loader)
    refused, n = [], 0
    for cn in jar_classes(JAR):
        D = jc(cn)
        lk = MH.privateLookupIn(D, MH.lookup())
        cc = CP.get(cn)
        sup = str(cc.getSuperclass().getName()) if cc.getSuperclass() is not None else None
        for mi in cc.getClassFile2().getMethods():
            ca = mi.getCodeAttribute()
            if ca is None:
                continue
            cp, it_ = mi.getConstPool(), ca.iterator()
            in_ctor = str(mi.getName()) == "<init>"
            while it_.hasNext():
                p_ = it_.next()
                op = it_.byteAt(p_)
                if op not in XOPS:
                    continue
                if op == 0xba:
                    refused.append("%s invokedynamic" % cn)
                    continue
                idx = it_.byteAt(p_ + 1) if op == 0x12 else it_.u16bitAt(p_ + 1)
                tag = cp.getTag(idx)
                if op in (0x12, 0x13) and tag != CPool.CONST_Class:
                    continue
                n += 1
                try:
                    if op in (0x12, 0x13, 0xbb, 0xbd, 0xc0, 0xc1, 0xc5):
                        lk.accessClass(jc(str(cp.getClassInfo(idx))))
                    elif op in (0xb2, 0xb3, 0xb4, 0xb5):
                        C_ = jc(str(cp.getFieldrefClassName(idx)))
                        ft = MTc.fromMethodDescriptorString("(" + str(cp.getFieldrefType(idx)) + ")V", loader).parameterType(0)
                        if op in (0xb2, 0xb3):
                            lk.findStaticGetter(C_, str(cp.getFieldrefName(idx)), ft)
                        else:
                            lk.findGetter(C_, str(cp.getFieldrefName(idx)), ft)
                    else:
                        if tag == CPool.CONST_InterfaceMethodref:
                            cname, name, desc = str(cp.getInterfaceMethodrefClassName(idx)), str(cp.getInterfaceMethodrefName(idx)), str(cp.getInterfaceMethodrefType(idx))
                        else:
                            cname, name, desc = str(cp.getMethodrefClassName(idx)), str(cp.getMethodrefName(idx)), str(cp.getMethodrefType(idx))
                        C_ = jc(cname)
                        mt = MTc.fromMethodDescriptorString(desc, loader)
                        if name == "<init>" and in_ctor and cname in (sup, cn):
                            md = int(C_.getDeclaredConstructor(mt.parameterArray()).getModifiers())
                            if not (JMod_.isPublic(md) or JMod_.isProtected(md) or cname == cn):
                                raise ValueError("constructor not accessible")
                        elif name == "<init>":
                            lk.findConstructor(C_, mt)
                        elif op == 0xb8:
                            lk.findStatic(C_, name, mt)
                        elif op == 0xb7:
                            lk.findSpecial(C_, name, mt, D)
                        else:
                            lk.findVirtual(C_, name, mt)
                except Exception as ex_:
                    if "caller-sensitive" not in str(ex_):
                        refused.append("%s: %s" % (cn, ex_))
    json.dump({"refused": refused, "refs": n}, open(out, "w"))


def child(env, *args):
    return subprocess.run([sys.executable, os.path.abspath(__file__)] + list(args) + ["--dir", SCRATCH, "--jar", JAR], env=env)


def take(path, label):
    if not os.path.isfile(path):
        check(False, "%s: the child wrote no result" % label)
        return
    d = json.load(open(path))
    OKS[0] += d["ok"]
    for f in d["fails"]:
        FAILS.append("%s: %s" % (label, f))
    for n in d.get("notes", []):
        print("  note (%s): %s" % (label, n))


def main():
    for flag, fn in (("--verify", lambda: run_verify(arg("--out"))), ("--x", lambda: run_x(arg("--out"))),
                     ("--compare", lambda: run_compare(arg("--out"))), ("--live", lambda: run_live(arg("--out"), arg("--live"))),
                     ("--audit", lambda: run_audit(arg("--out")))):
        if flag in sys.argv:
            try:
                fn()
            except Exception:
                import traceback
                traceback.print_exc()
                sys.exit(1)
            return
    sc = os.path.realpath(SCRATCH)
    assert sc.startswith(os.path.realpath(os.path.join(TOOLS, "dev", "scratch", "loot01")) + os.sep), "scratch must be inside tools/dev/scratch/loot01"
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(os.path.join(SCRATCH, "tmp"), exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    try:
        for label, flag in (("verify", "--verify"), ("x", "--x"), ("compare", "--compare")):
            out = os.path.join(SCRATCH, label + ".json")
            pr = child(env, flag, "--out", out)
            check(pr.returncode == 0, "%s: the child exited cleanly (%s)" % (label, pr.returncode))
            take(out, label)
        home = os.path.join(SCRATCH, "live")
        shutil.copytree(LIVE_DIR, home)
        out = os.path.join(SCRATCH, "live.json")
        pr = child(env, "--live", home, "--out", out)
        check(pr.returncode == 0, "D: the child exited cleanly")
        take(out, "live")
        outa = os.path.join(SCRATCH, "audit.json")
        pa = child(env, "--audit", "--out", outa)
        check(pa.returncode == 0 and os.path.isfile(outa), "AA: the audit child ran")
        if os.path.isfile(outa):
            a = json.load(open(outa))
            check(not a["refused"] and a["refs"] > 1000, "AA: engine-access audit: %d references, refused %s" % (a["refs"], a["refused"][:5]))
            print("AA. engine-access audit: %d references, 0 refused" % a["refs"])
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyMobs %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
