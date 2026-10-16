"""harness_kit - the phases every SkyWynn jar harness repeats, shared by the perfecon round's harnesses (SkyyCoins 0.1.6, SkyyBazaar 0.1.8,
SkyyGuilds 0.1.7, SkyyAuctions 0.1.4). Copied from SkyyAuctions/test_skyyauctions_0.1.3.py (its A / C / AA phases), parameterised.

A harness script imports this module and calls run(...) with its own child phases:

    import harness_kit as HK
    HK.run(name="SkyyCoins", version="0.1.6", jar=..., old_jar=..., pkg="com.skyy.coins.", scratch=..., expect={...},
           phases=[("exec", run_exec), ("live", run_live)], live=(LIVE_DIR, "Skyy_SkyyCoins"))

Every phase runs in a FRESH child JVM (jpype starts one JVM per process): the game's JRE, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in
the scratch folder (never AppData). Built-in phases:
  A  verify   every class of the jar loads + initialises with -Xverify:all (the server jar on the classpath)
  C  compare  class compare old -> new jar (javassist members + resolved bytecode): exactly the EXPECTED members differ, added classes
              listed; non-class entries: only manifest.json
  AA audit    every class / field / method reference resolved with MethodHandles.privateLookupIn the referencing class (the JVM's access
              rules at link time), plus a control (a protected engine call from outside) that MUST be refused
Scratch: the folder given (must be under tools/dev/scratch/), deleted at the end unless --keep. Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, re, hashlib

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)
import skyybuild as B

FAKE_PKG = "skyyhktest"
FAILS, OKS = [], [0]


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def jvm(cp, verify=True):
    import jpype
    tmp = os.environ.get("TEMP") or os.path.join(arg("--dir", "."), "tmp")
    os.makedirs(tmp, exist_ok=True)
    j = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(j):
        j = B._jvm()
    opts = (["-Xverify:all"] if verify else []) + ["-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp]
    # 2026-10-15 (SkyyCore): a module built in "link against SkyyCore" mode needs the Core jar on every child JVM's class path - the
    # harness sets SKYY_HARNESS_CP (os.pathsep-separated jars; inherited by the child processes). Unset = exactly the old class path.
    extra = [p for p in os.environ.get("SKYY_HARNESS_CP", "").split(os.pathsep) if p]
    jpype.startJVM(j, *opts, classpath=list(cp) + [p for p in extra if p not in cp], convertStrings=True)


class Child(object):
    def __init__(self, out):
        self.out, self.ok, self.fails, self.notes = out, 0, [], []

    def check(self, cond, what):
        if cond:
            self.ok += 1
        else:
            self.fails.append(what)
            print("FAIL", what)
        return cond

    def eq(self, got, want, what):
        return self.check(got == want, "%s: got %r, want %r" % (what, got, want))

    def save(self, **extra):
        d = {"ok": self.ok, "fails": self.fails, "notes": self.notes}
        d.update(extra)
        json.dump(d, open(self.out, "w"), indent=1)


def jar_classes(j):
    return sorted(n[:-6].replace("/", ".") for n in zipfile.ZipFile(j).namelist() if n.endswith(".class"))


def tree_hash(d):
    out_ = {}
    for base, _dirs, files in os.walk(d):
        for f in files:
            p_ = os.path.join(base, f)
            out_[os.path.relpath(p_, d)] = hashlib.sha1(open(p_, "rb").read()).hexdigest()
    return out_


# ---------------------------------------------------------------------------------------------------------------- F: the audit's stand-ins
def run_mkfake(out_dir, jar):
    from jpype import JClass
    jvm([B.JAVASSIST], verify=False)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(jar)
    CtNewMethod = JClass("javassist.CtNewMethod")
    lk = cp.makeClass(FAKE_PKG + ".LookupIn")
    lk.addMethod(CtNewMethod.make(
        "public static java.lang.invoke.MethodHandles$Lookup lookupIn(java.lang.Class c) throws java.lang.Exception {\n"
        "  return java.lang.invoke.MethodHandles.privateLookupIn(c, java.lang.invoke.MethodHandles.lookup());\n}", lk))
    lk.writeFile(out_dir)
    ba = cp.makeClass(FAKE_PKG + ".BadAccess")
    ba.addMethod(CtNewMethod.make(
        "public static void send(com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage p) {\n"
        "  p.sendUpdate(new com.hypixel.hytale.server.core.ui.builder.UICommandBuilder());\n}", ba))
    ba.writeFile(out_dir)


# ---------------------------------------------------------------------------------------------------------------- A: verify
def run_verify(out, jar):
    from jpype import JClass
    K = Child(out)
    jvm([B.SERVER_JAR, jar], verify=True)
    Cls, loader = JClass("java.lang.Class"), JClass("java.lang.ClassLoader").getSystemClassLoader()
    names = jar_classes(jar)
    for n in names:
        try:
            Cls.forName(n, True, loader)
            K.ok += 1
        except Exception as e:
            K.check(False, "A: load + verify %s: %s" % (n, str(e)[:300]))
    K.notes.append("A: %d classes loaded + initialised with -Xverify:all" % len(names))
    K.save()


# ---------------------------------------------------------------------------------------------------------------- C: class compare
def run_compare(out, jar, old_jar, pkg, expect, added, removed=()):
    from jpype import JClass
    K = Child(out)
    jvm([B.JAVASSIST], verify=False)
    CPc = JClass("javassist.ClassPool")
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def pool_of(j):
        p_ = CPc(False)
        p_.appendSystemPath()
        p_.appendClassPath(B.SERVER_JAR)
        p_.appendClassPath(j)
        return p_
    pa, pb = pool_of(old_jar), pool_of(jar)

    def members(p_, cn):
        c_ = p_.get(cn)
        d_ = {}
        for f_ in c_.getDeclaredFields():
            d_["f " + str(f_.getName())] = str(f_.getSignature()) + " " + str(f_.getModifiers())

        def code(b_):
            mi_ = b_.getMethodInfo()
            ca_ = mi_.getCodeAttribute()
            if ca_ is None:
                return ""
            it_ = ca_.iterator()
            cpl_ = mi_.getConstPool()
            lines_ = []
            while it_.hasNext():
                pos_ = it_.next()
                ln_ = re.sub(r"^ldc_w ", "ldc ", re.sub(r"#\d+ = ", "", str(IP.instructionString(it_, pos_, cpl_))))
                lines_.append(re.sub(r"^((?:if\w*|goto(?:_w)?|jsr(?:_w)?)) -?\d+$", r"\1", ln_))
            return str(b_.getModifiers()) + "\n" + "\n".join(lines_)
        for m_ in c_.getDeclaredMethods():
            d_["m " + str(m_.getName()) + str(m_.getSignature())] = code(m_)
        for m_ in c_.getDeclaredConstructors():
            d_["c " + str(m_.getSignature())] = code(m_)
        ci = c_.getClassInitializer()
        if ci is not None:
            d_["<clinit>"] = code(ci)
        return d_
    na, nb = jar_classes(old_jar), jar_classes(jar)
    K.eq(sorted(set(nb) - set(na)), sorted(pkg + a for a in added), "C: classes added")
    K.eq(sorted(set(na) - set(nb)), sorted(pkg + r for r in removed), "C: classes removed")
    diffs, same = {}, 0
    for cn in sorted(set(na) & set(nb)):
        ma, mb = members(pa, cn), members(pb, cn)
        dd = sorted(k for k in set(ma) | set(mb) if ma.get(k) != mb.get(k))
        if dd:
            diffs[cn[len(pkg):] if cn.startswith(pkg) else cn] = sorted(("+" if k not in ma else ("-" if k not in mb else "~")) + k for k in dd)
        else:
            same += 1
    print("C. class compare %s -> %s: %d classes identical, %d differ" % (os.path.basename(old_jar), os.path.basename(jar), same, len(diffs)))
    for k in sorted(diffs):
        print("   %-22s %s" % (k, ", ".join(x.split("(")[0] for x in diffs[k])))
    K.eq(sorted(diffs), sorted(expect), "C: the classes that differ")
    for k in sorted(expect):
        got = sorted(x.split("(")[0] if not x[1:].startswith("c ") else x[:3] for x in diffs.get(k, []))
        K.eq(got, sorted(expect[k]), "C: %s members" % k)
    za, zb = zipfile.ZipFile(old_jar), zipfile.ZipFile(jar)
    ea = [n for n in za.namelist() if not n.endswith(".class")]
    eb = [n for n in zb.namelist() if not n.endswith(".class")]
    ed = sorted(n for n in set(ea) | set(eb) if n not in ea or n not in eb or za.read(n) != zb.read(n))
    K.eq(ed, ["manifest.json"], "C: non-class entries changed")
    K.notes.append("C: %d identical, changed: %s" % (same, {k: [x.split("(")[0] for x in v] for k, v in diffs.items()}))
    K.save()


# ---------------------------------------------------------------------------------------------------------------- AA: engine-access audit
def run_audit(out, jar, fake_dir):
    from jpype import JClass
    jvm([B.SERVER_JAR, B.JAVASSIST, jar, fake_dir], verify=False)
    Cls, loader = JClass("java.lang.Class"), JClass("java.lang.ClassLoader").getSystemClassLoader()
    CP = JClass("javassist.ClassPool")(False)
    CP.appendSystemPath()
    for p_ in (B.SERVER_JAR, jar, fake_dir):
        CP.appendClassPath(p_)
    LIN, MTc, CPool, JMod_ = (JClass(FAKE_PKG + ".LookupIn"), JClass("java.lang.invoke.MethodType"), JClass("javassist.bytecode.ConstPool"),
                              JClass("java.lang.reflect.Modifier"))
    XOPS = {0xb2: "getstatic", 0xb3: "putstatic", 0xb4: "getfield", 0xb5: "putfield", 0xb6: "invokevirtual", 0xb7: "invokespecial",
            0xb8: "invokestatic", 0xb9: "invokeinterface", 0xba: "invokedynamic", 0xbb: "new", 0xbd: "anewarray", 0xc0: "checkcast",
            0xc1: "instanceof", 0xc5: "multianewarray", 0x12: "ldc", 0x13: "ldc_w"}

    def jvm_class(name):
        return Cls.forName(name.replace("/", "."), False, loader)

    def lookup_audit(cn):
        D = jvm_class(cn)
        lk = LIN.lookupIn(D)
        cc = CP.get(cn)
        sup = str(cc.getSuperclass().getName()) if cc.getSuperclass() is not None else None
        refused, n = [], 0
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
                where = "%s.%s @%d %s" % (cn.rsplit(".", 1)[-1], mi.getName(), p_, XOPS[op])
                if op == 0xba:
                    refused.append(where + ": invokedynamic")
                    continue
                idx = it_.byteAt(p_ + 1) if op == 0x12 else it_.u16bitAt(p_ + 1)
                tag = cp.getTag(idx)
                if op in (0x12, 0x13) and tag != CPool.CONST_Class:
                    continue
                n += 1
                C_ = None
                name = None
                mt = None
                try:
                    if op in (0x12, 0x13, 0xbb, 0xbd, 0xc0, 0xc1, 0xc5):
                        lk.accessClass(jvm_class(str(cp.getClassInfo(idx))))
                    elif op in (0xb2, 0xb3, 0xb4, 0xb5):
                        C_ = jvm_class(str(cp.getFieldrefClassName(idx)))
                        ft = MTc.fromMethodDescriptorString("(" + str(cp.getFieldrefType(idx)) + ")V", loader).parameterType(0)
                        if op in (0xb2, 0xb3):
                            lk.findStaticGetter(C_, str(cp.getFieldrefName(idx)), ft)
                        else:
                            lk.findGetter(C_, str(cp.getFieldrefName(idx)), ft)
                    else:
                        if tag == CPool.CONST_InterfaceMethodref:
                            cname, name, desc = (str(cp.getInterfaceMethodrefClassName(idx)), str(cp.getInterfaceMethodrefName(idx)), str(cp.getInterfaceMethodrefType(idx)))
                        else:
                            cname, name, desc = (str(cp.getMethodrefClassName(idx)), str(cp.getMethodrefName(idx)), str(cp.getMethodrefType(idx)))
                        C_ = jvm_class(cname)
                        mt = MTc.fromMethodDescriptorString(desc, loader)
                        if name == "<init>" and in_ctor and cname in (sup, cn):
                            md = int(C_.getDeclaredConstructor(mt.parameterArray()).getModifiers())
                            if not (JMod_.isPublic(md) or JMod_.isProtected(md) or cname == cn
                                    or (not JMod_.isPrivate(md) and str(C_.getPackageName()) == str(D.getPackageName()))):
                                raise ValueError("constructor %s %s%s is not accessible from %s" % (JMod_.toString(md), cname, desc, cn))
                        elif name == "<init>":
                            lk.findConstructor(C_, mt)
                        elif op == 0xb8:
                            lk.findStatic(C_, name, mt)
                        elif op == 0xb7:
                            lk.findSpecial(C_, name, mt, D)
                        else:
                            lk.findVirtual(C_, name, mt)
                except Exception as ex_:
                    ok_ = False
                    if "caller-sensitive" in str(ex_) and op in (0xb6, 0xb8, 0xb9) and C_ is not None:
                        try:
                            mm_ = C_.getMethod(name, mt.parameterArray())
                            ok_ = JMod_.isPublic(int(C_.getModifiers())) and JMod_.isPublic(int(mm_.getModifiers()))
                        except Exception:
                            ok_ = False
                    if not ok_:
                        refused.append("%s: %s" % (where, ex_))
        return refused, n
    names = jar_classes(jar)
    res = {"classes": len(names), "refs": 0, "refused": []}
    for cn in names:
        try:
            r_, k_ = lookup_audit(cn)
        except Exception as ex_:
            r_, k_ = ["%s: could not audit: %s" % (cn, ex_)], 0
        res["refused"] += r_
        res["refs"] += k_
    res["control"] = lookup_audit(FAKE_PKG + ".BadAccess")[0]
    json.dump(res, open(out, "w"), indent=1)


# ---------------------------------------------------------------------------------------------------------------- parent
def take(path, label):
    if not os.path.isfile(path):
        check(False, "%s: the child wrote no result" % label)
        return None
    d = json.load(open(path))
    OKS[0] += d["ok"]
    for f in d["fails"]:
        FAILS.append("%s: %s" % (label, f))
    for n in d.get("notes", []):
        print("  note (%s): %s" % (label, n))
    return d


def run(name, version, jar, old_jar, pkg, scratch, expect, added, phases, script, live=None, removed=()):
    """phases: [(label, fn(out, jar, scratch, live_home_or_None))] - each runs in its own child process (flag --phase <label>).
    2026-10-15 (SkyyCore): removed = classes the new jar no longer has (the compare checks exactly these); every label that starts
    with "live" gets its own scratch COPY of the live folder (live, live2, ...)."""
    builtin = {"mkfake": lambda: run_mkfake(os.path.join(scratch, "fake"), jar),
               "verify": lambda: run_verify(arg("--out"), jar),
               "compare": lambda: run_compare(arg("--out"), jar, old_jar, pkg, expect, added, removed),
               "audit": lambda: run_audit(arg("--out"), jar, os.path.join(scratch, "fake"))}
    if "--phase" in sys.argv:
        ph = arg("--phase")
        try:
            if ph in builtin:
                builtin[ph]()
            else:
                dict(phases)[ph](arg("--out"), jar, scratch, arg("--home"))
        except SystemExit:
            raise
        except Exception:
            import traceback
            traceback.print_exc()
            sys.exit(1)
        return
    assert os.path.isfile(jar), jar
    assert os.path.isfile(old_jar), old_jar
    sc = os.path.realpath(scratch)
    assert sc.startswith(os.path.realpath(os.path.join(TOOLS, "dev", "scratch")) + os.sep), "the scratch folder must be inside tools/dev/scratch/"
    shutil.rmtree(scratch, ignore_errors=True)
    os.makedirs(os.path.join(scratch, "tmp"), exist_ok=True)
    os.makedirs(os.path.join(scratch, "fake"), exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(scratch, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.environ["TEMP"] = os.environ["TMP"] = env["TEMP"]

    def child(label, *extra):
        out = os.path.join(scratch, "%s.json" % label)
        p = subprocess.run([sys.executable, os.path.abspath(script), "--phase", label, "--out", out, "--dir", scratch, "--jar", jar] + list(extra), env=env)
        check(p.returncode == 0, "%s: the child exited cleanly (%s)" % (label, p.returncode))
        return out
    try:
        p_ = child("mkfake")
        for label in ("verify", "compare"):
            take(child(label), label)
        for label, _fn in phases:
            if label.startswith("live"):
                if live is None or not os.path.isdir(live[0]):
                    check(False, "D: no live folder %s" % (live and live[0]))
                    continue
                home = os.path.join(scratch, label, live[1])
                shutil.copytree(live[0], home)
                print("D. live %s copied (read-only source %s)" % (live[1], live[0]))
                take(child(label, "--home", home), label)
            else:
                take(child(label), label)
        outa = child("audit")
        if os.path.isfile(outa):
            a = json.load(open(outa))
            check(not a["refused"] and a["refs"] > 100, "AA: engine-access audit: %d references in %d classes, refused %s" % (a["refs"], a["classes"], a["refused"][:5]))
            check(len(a["control"]) == 1 and "sendUpdate" in a["control"][0], "AA: the control is refused: %s" % a["control"])
            print("AA. engine-access audit: %d references in %d classes, %d refused, control refused" % (a["refs"], a["classes"], len(a["refused"])))
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(scratch, ignore_errors=True)
    print("%s %s harness: %d ok, %d fail(s)" % (name, version, OKS[0], len(FAILS)))
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)
