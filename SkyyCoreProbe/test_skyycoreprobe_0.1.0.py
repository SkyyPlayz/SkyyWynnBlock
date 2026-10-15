"""Harness for SkyyCoreProbe 0.1.0 + SkyyDepProbe 0.1.0 (phase 0 of research/Architecture-Spec.md). Game may stay open: nothing is
written outside tools/dev/scratch/coreprobe/ (TEMP / cwd of the JVM), and only the CACHED server jar is opened (tools/serverjar.py).

    python SkyyCoreProbe/test_skyycoreprobe_0.1.0.py

Checks (exit 0 = all ok):
  1. jar contents: stable-name manifests, Dependencies {"Skyy:SkyyCoreProbe": RANGE}, the texture ONLY in Core's jar (and in no SET jar,
     no other project jar, no installed mod, not in Assets.zip), Core classes only in Core's jar, ready-line strings, the page names
     "SkyyKit/Probe.png", /coreprobe = requirePermission + empty groups.
  2. ENGINE (HytaleServer.jar 0.7.2 classes, in the JVM): PluginManifest.CODEC decodes both manifest.json files with no unknown key and
     the Dependencies map comes out as PluginIdentifier Skyy:SkyyCoreProbe -> SemverRange; both range syntaxes (">=0.1.0 <1.0.0" and
     "^0.1.0") parse and accept 0.1.0; an out-of-range "^0.2.0" refuses it; a bare "0.1.1" is refused with the engine's message.
  3. C1 BRIDGE STAND-IN, -Xverify:all: Core loader = URLClassLoader(core jar, parent = server); Dep loader = URLClassLoader(dep jar,
     parent = Core loader) - the same visibility the engine's PluginBridgeClassLoader gives a plugin over its Dependencies. Every class of
     both jars loads, links (= verification) and initialises; DepCalls.c1() runs and returns PASS with "one class copy" (the harness
     publishes Core's CoreBox class on skyy.bridge like Core's setup() does); every constant-pool class / method / field reference of the
     Dep jar resolves against server + Core with legal access.
  4. NEGATIVE: Dep alone (parent = server, no Core): DepProbe.runC1() returns FAIL with NoClassDefFoundError and does NOT throw (so a
     missing Core can never kill the plugin's setup - on 0.7.2 a throwing setup() would shut the server down).
"""
import os, sys, json, re, zipfile, glob, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import serverjar

VERSION = "0.1.0"
RANGE = ">=0.1.0 <1.0.0"
JAR_C = os.path.join(ROOT, "SkyyCoreProbe", "SkyyCoreProbe-%s.jar" % VERSION)
JAR_D = os.path.join(ROOT, "SkyyDepProbe", "SkyyDepProbe-%s.jar" % VERSION)
TEX = "Common/UI/Custom/SkyyKit/Probe@2x.png"
SCRATCH = os.path.join(ROOT, "tools", "dev", "scratch", "coreprobe", "harness")
ok_n, bad = [0], []


def ok(cond, what):
    if cond:
        ok_n[0] += 1
    else:
        bad.append(what)
        print("FAIL", what)


# ---------------- 1. jar contents ----------------
zc, zd = zipfile.ZipFile(JAR_C), zipfile.ZipFile(JAR_D)
mc, md = json.loads(zc.read("manifest.json")), json.loads(zd.read("manifest.json"))
ok(mc["Group"] == "Skyy" and mc["Name"] == "SkyyCoreProbe" and mc["Version"] == VERSION, "Core manifest stable name")
ok(md["Group"] == "Skyy" and md["Name"] == "SkyyDepProbe" and md["Version"] == VERSION, "Dep manifest stable name")
ok(md.get("Dependencies") == {"Skyy:SkyyCoreProbe": RANGE}, "Dep Dependencies")
ok("Dependencies" not in mc and mc["IncludesAssetPack"] is True and md["IncludesAssetPack"] is False, "Core: no deps + asset pack; Dep: none")
ok(mc["Main"] == "com.skyy.coreprobe.SkyyCoreProbePlugin" and md["Main"] == "com.skyy.depprobe.SkyyDepProbePlugin", "Main classes")
nc, nd = zc.namelist(), zd.namelist()
ok(TEX in nc and TEX not in nd, "texture only in Core's jar")
ok(all(n.startswith("com/skyy/coreprobe/") for n in nc if n.endswith(".class")), "Core classes in its package")
ok(all(n.startswith("com/skyy/depprobe/") for n in nd if n.endswith(".class")), "Dep classes in its package (no Core copy)")
ok(len([n for n in nd if not n.endswith(".class") and n != "manifest.json"]) == 0, "Dep ships nothing but classes + manifest")
png = zc.read(TEX)
ok(png[:8] == b"\x89PNG\r\n\x1a\n" and png[16:24] == bytes.fromhex("0000020000000100"), "texture is a 512 x 256 PNG")


def strings(z, cls):
    sys.path.insert(0, os.path.join(ROOT, "tools", "dev"))
    from cpstrings import read_utf8_constants
    return read_utf8_constants(z.read(cls))


sc = strings(zc, "com/skyy/coreprobe/SkyyCoreProbePlugin.class")
ok(any(s.startswith("[SkyyCoreProbe] 0.1.0 ready") for s in sc), "Core ready line")
sd = strings(zd, "com/skyy/depprobe/SkyyDepProbePlugin.class")
ok(any(s.startswith("[SkyyDepProbe] 0.1.0 ready") for s in sd), "Dep ready line")
scmd = strings(zd, "com/skyy/depprobe/CoreProbeCmd.class")
ok("coreprobe" in scmd and "skyydepprobe.admin" in scmd and "requirePermission" in scmd and "setPermissionGroups" in scmd,
   "/coreprobe admin gate")
spg = " ".join(strings(zd, "com/skyy/depprobe/CoreProbePage.class"))
ok('"SkyyKit/Probe.png"' in spg and "#CprClose" in spg, "page names Core's texture + Close binding")
scalls = strings(zd, "com/skyy/depprobe/DepCalls.class")
ok("com/skyy/coreprobe/CoreApi" in scalls and "com/skyy/coreprobe/CoreBox" in scalls, "DepCalls links Core's classes directly")
for other in ("DepProbe", "SkyyDepProbePlugin", "CoreProbeCmd", "CoreProbePage", "DepLog"):
    ok(not any("coreprobe/Core" in s for s in strings(zd, "com/skyy/depprobe/%s.class" % other)),
       "%s never names a Core class (only DepCalls does)" % other)
# texture path collisions: Assets.zip, every other project jar, every installed mod
with zipfile.ZipFile(serverjar.assets_zip()) as az:
    ok(TEX not in set(az.namelist()), "texture path not in Assets.zip")
clash = []
for p in glob.glob(os.path.join(ROOT, "Skyy*", "*.jar")) + glob.glob(os.path.join(B.MODS_DIR, "*")):
    if os.path.abspath(p) == os.path.abspath(JAR_C) or not p.lower().endswith((".jar", ".zip")):
        continue
    try:
        with zipfile.ZipFile(p) as z:
            if TEX in z.namelist():
                clash.append(p)
    except Exception:
        pass
ok(not clash, "no other jar ships %s: %s" % (TEX, clash))

# ---------------- JVM ----------------
os.makedirs(SCRATCH, exist_ok=True)
for k in ("TEMP", "TMP", "TMPDIR"):
    os.environ[k] = SCRATCH
os.chdir(SCRATCH)
import jpype
import jpype.imports  # noqa: F401
srv_jar = serverjar.server_jar()
jpype.startJVM(B._jvm(), "-Xverify:all", "-XX:-UsePerfData", "-Djava.io.tmpdir=" + SCRATCH, "-Xshare:off",
               "--add-opens=java.base/java.lang=ALL-UNNAMED", "--enable-native-access=ALL-UNNAMED",
               classpath=[srv_jar, B.JAVASSIST], convertStrings=True)
JC = jpype.JClass
Class, File, URL, ULC = JC("java.lang.Class"), JC("java.io.File"), JC("java.net.URL"), JC("java.net.URLClassLoader")
srv = JC("java.lang.ClassLoader").getSystemClassLoader()
Impl = JC("java.lang.management.ManagementFactory").getRuntimeMXBean().getInputArguments()
ok("-Xverify:all" in [str(x) for x in Impl], "JVM runs with -Xverify:all")
ok("0.7.2" in str(zipfile.ZipFile(srv_jar).read("META-INF/MANIFEST.MF")), "engine = HytaleServer 0.7.2")


def loader(path, parent):
    return ULC(jpype.JArray(URL)([File(path).toURI().toURL()]), parent)


# ---------------- 2. engine parse ----------------
SR, SV, PI = JC("com.hypixel.hytale.common.semver.SemverRange"), JC("com.hypixel.hytale.common.semver.Semver"), \
    JC("com.hypixel.hytale.common.plugin.PluginIdentifier")
v010 = SV.fromString("0.1.0")
for rs in (RANGE, "^0.1.0"):
    try:
        r = SR.fromString(rs)
        ok(bool(v010.satisfies(r)), "range %r accepts 0.1.0" % rs)
        print("  engine: SemverRange %r parses -> %s, 0.1.0 satisfies" % (rs, r.toString()))
    except Exception as e:
        ok(False, "range %r parse: %s" % (rs, e))
ok(not bool(v010.satisfies(SR.fromString("^0.2.0"))), "^0.2.0 refuses 0.1.0 (the 'does not satisfy' path)")
try:
    SR.fromString("0.1.1")
    ok(False, "bare 0.1.1 should be refused")
except Exception as e:
    ok("Bare version" in str(e), "bare 0.1.1 refused: %s" % e)
    print("  engine: bare '0.1.1' -> %s" % str(e)[:140])
ok(str(PI.fromString("Skyy:SkyyCoreProbe").toString()) == "Skyy:SkyyCoreProbe", "PluginIdentifier round trip")
PM, RJR, EI = JC("com.hypixel.hytale.common.plugin.PluginManifest"), JC("com.hypixel.hytale.codec.util.RawJsonReader"), \
    JC("com.hypixel.hytale.codec.ExtraInfo")
SRd = JC("java.io.StringReader")
for nm, z in (("Core", zc), ("Dep", zd)):
    txt = z.read("manifest.json").decode("utf-8")
    ei = EI()
    man = PM.CODEC.decodeJson(RJR(SRd(txt), jpype.JArray(jpype.JChar)(32768)), ei)
    unk = [str(u) for u in ei.getUnknownKeys()]
    ok(not unk, "%s manifest: no unknown keys %s" % (nm, unk))
    ok(str(man.getGroup()) == "Skyy" and str(man.getVersion()) == VERSION, "%s manifest decodes (group / version)" % nm)
    deps = man.getDependencies()
    if nm == "Dep":
        keys = [str(k) for k in deps.keySet()]
        ok(keys == ["Skyy:SkyyCoreProbe"], "Dep manifest Dependencies keys %s" % keys)
        rng = deps.get(PI.fromString("Skyy:SkyyCoreProbe"))
        ok(rng is not None and bool(v010.satisfies(rng)), "Dep manifest range decodes and accepts Core 0.1.0")
        print("  engine: PluginManifest.CODEC -> %s, Dependencies %s" % (man.getName(), deps))
    else:
        ok(deps.isEmpty(), "Core manifest has no dependencies")


# ---------------- 3. C1 with a bridge stand-in ----------------
def load_all(z, ld, what):
    names = sorted(n[:-6].replace("/", ".") for n in z.namelist() if n.endswith(".class"))
    out = {}
    for n in names:
        try:
            c = Class.forName(n, False, ld)
            c.getDeclaredMethods(); c.getDeclaredFields(); c.getDeclaredConstructors()
            out[n] = c
        except Exception as e:
            ok(False, "%s VERIFY %s: %s" % (what, n, e))
    for n, c in out.items():
        try:
            Class.forName(n, True, ld)
        except Exception as e:
            ok(False, "%s INIT %s: %s" % (what, n, e))
    ok(len(out) == len(names), "%s: %d classes verified + initialised" % (what, len(names)))
    return out


core_ld = loader(JAR_C, srv)
dep_ld = loader(JAR_D, core_ld)
cc = load_all(zc, core_ld, "Core")
dc_ = load_all(zd, dep_ld, "Dep (bridge stand-in)")
api = cc["com.skyy.coreprobe.CoreApi"]
ok(str(api.getMethod("hello", Class.forName("java.lang.String")).invoke(None, "x")) == "SkyyCoreProbe 0.1.0 says hello to x", "CoreApi.hello")
bridge = JC("java.util.concurrent.ConcurrentHashMap")()
JC("java.lang.System").getProperties().put("skyy.bridge", bridge)
bridge.put("coreprobe:boxclass", cc["com.skyy.coreprobe.CoreBox"])          # what Core's setup() publishes
r = str(dc_["com.skyy.depprobe.DepCalls"].getMethod("c1").invoke(None))
print("  C1 stand-in: " + r.replace("\t", " | ")[:400])
ok(r.startswith("PASS\t") and "one class copy" in r, "C1 PASS through the bridge stand-in")
ok(dc_["com.skyy.depprobe.DepCalls"].getClassLoader() == dep_ld, "DepCalls loaded by the Dep loader")
dep_box = Class.forName("com.skyy.coreprobe.CoreBox", False, dep_ld)
ok(dep_box == cc["com.skyy.coreprobe.CoreBox"], "the Dep loader resolves CoreBox to Core's own Class (one copy)")
res = dep_ld.getResource(TEX)
ok(res is not None and "SkyyCoreProbe" in str(res), "Core's texture resource visible from the Dep loader (bridge resources stand-in)")

# access audit of every constant-pool ref of the Dep jar (server + Core visible), like tools/ci/crosscheck.py section 2
CF, DIS, BAIS, Mod = JC("javassist.bytecode.ClassFile"), JC("java.io.DataInputStream"), JC("java.io.ByteArrayInputStream"), \
    JC("java.lang.reflect.Modifier")
PRIM = {"boolean": "Z", "byte": "B", "char": "C", "short": "S", "int": "I", "long": "J", "float": "F", "double": "D", "void": "V"}


def desc(c):
    n = str(c.getName())
    return PRIM[n] if n in PRIM else (n.replace(".", "/") if n.startswith("[") else "L" + n.replace(".", "/") + ";")


def find(c, kind, key):
    k = c
    while k is not None:
        mem = k.getDeclaredFields() if kind == "f" else (list(k.getDeclaredMethods()) + list(k.getDeclaredConstructors()))
        for m in mem:
            if kind == "f":
                d = (str(m.getName()), desc(m.getType()))
            else:
                nm = "<init>" if m in list(k.getDeclaredConstructors()) else str(m.getName())
                rt = "V" if nm == "<init>" else desc(m.getReturnType())
                d = (nm, "(" + "".join(desc(p) for p in m.getParameterTypes()) + ")" + rt)
            if d == key:
                return k, int(m.getModifiers())
        for i in k.getInterfaces():
            h = find(i, kind, key)
            if h:
                return h
        k = k.getSuperclass()
    return None


nref, refused = 0, []
for n in sorted(dc_):
    cf = CF(DIS(BAIS(zd.read(n.replace(".", "/") + ".class"))))
    cp = cf.getConstPool()
    me = dc_[n]
    for i in range(1, cp.getSize()):
        t = cp.getTag(i)
        if t not in (7, 9, 10, 11):
            continue
        if t == 7:
            owner, key, kind = str(cp.getClassInfo(i)), None, None
        elif t == 9:
            owner, key, kind = str(cp.getFieldrefClassName(i)), (str(cp.getFieldrefName(i)), str(cp.getFieldrefType(i))), "f"
        elif t == 10:
            owner, key, kind = str(cp.getMethodrefClassName(i)), (str(cp.getMethodrefName(i)), str(cp.getMethodrefType(i))), "m"
        else:
            owner = str(cp.getInterfaceMethodrefClassName(i))
            key, kind = (str(cp.getInterfaceMethodrefName(i)), str(cp.getInterfaceMethodrefType(i))), "m"
        if owner.startswith("["):
            continue
        nref += 1
        try:
            oc = Class.forName(owner, False, dep_ld)
        except Exception as e:
            refused.append("%s -> %s: class not found" % (n, owner))
            continue
        if not (Mod.isPublic(oc.getModifiers()) or str(oc.getPackageName()) == str(me.getPackageName())):
            refused.append("%s -> %s: class not accessible" % (n, owner))
            continue
        if key is None:
            continue
        h = find(oc, kind, key)
        if h is None:
            refused.append("%s -> %s.%s%s: no such member" % (n, owner, key[0], key[1]))
        elif not (Mod.isPublic(h[1]) or (Mod.isProtected(h[1]) and h[0].isAssignableFrom(me))
                  or (not Mod.isPrivate(h[1]) and str(h[0].getPackageName()) == str(me.getPackageName()) and h[0].getClassLoader() == me.getClassLoader())
                  or h[0] == me):
            refused.append("%s -> %s.%s%s: not accessible" % (n, owner, key[0], key[1]))
ok(not refused, "Dep access audit: %d refs, refused %s" % (nref, refused))
print("  access audit (Dep jar, server + Core visible): %d refs, %d refused" % (nref, len(refused)))

# ---------------- 4. negative: Dep without Core ----------------
alone = loader(JAR_D, srv)
dpc = Class.forName("com.skyy.depprobe.DepProbe", True, alone)
try:
    arr = dpc.getMethod("runC1").invoke(None)
    s = [str(x) for x in arr]
    ok(s[0] == "FAIL" and "NoClassDefFoundError" in s[1], "without Core: runC1 -> FAIL NoClassDefFoundError (%s)" % s[1][:100])
    print("  without Core: " + s[1][:160])
except Exception as e:
    ok(False, "without Core, runC1 threw instead of reporting: %s" % e)
plug = Class.forName("com.skyy.depprobe.SkyyDepProbePlugin", False, alone)
plug.getDeclaredMethods()
ok(True, "the Dep plugin class itself verifies without Core (only DepCalls links Core)")

print("%s: %d ok, %d failed" % ("ALL OK" if not bad else "FAILED", ok_n[0], len(bad)))
sys.stdout.flush()
os.chdir(ROOT)
shutil.rmtree(SCRATCH, ignore_errors=True)
os._exit(0 if not bad else 1)
