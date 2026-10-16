"""Shared build bootstrap for all Skyy* mods (Windows).

Usage from a build script:
    import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
    import skyybuild as B
    J = B.start()               # starts the JVM, returns dict of javassist classes + pool
    ... build classes with J["pool"], J["CtField"], ...
    B.assemble(jar_path, manifest_dict, class_out_dir, extra_files={"Common/UI/...": "text"})
    B.deploy(jar_path, "SkyyHud.jar")           # copies into UserData/Mods
    B.enable_in_world("HUD mod", "Skyy:0.2 SkyyHud", disable_prefix="Skyy:")  # edits Saves/<world>/config.json

Gotchas (javassist compiler): no lambdas, generics, varargs, autoboxing, enhanced-for,
inner classes, String switch, try-with-resources. Pass explicit arrays. Double braces in f-strings.
"""
import os, sys, json, shutil, zipfile, glob

PROJECT   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HYTALE    = os.path.join(os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming"), "Hytale")
INSTALLED_SERVER_JAR = os.path.join(HYTALE, "install", "release", "package", "game", "latest", "Server", "HytaleServer.jar")
# SERVER_JAR (B.SERVER_JAR / from skyybuild import SERVER_JAR) = a CACHED COPY (tools/serverjar.py), resolved on first use, so our JVMs
# never hold the installed jar open (2026-10-13: that broke the launcher's update). Never open INSTALLED_SERVER_JAR from a JVM.
def __getattr__(name):
    if name == "SERVER_JAR":
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import serverjar
        return serverjar.server_jar()
    raise AttributeError(name)
USERDATA  = os.path.join(HYTALE, "UserData")
MODS_DIR  = os.path.join(USERDATA, "Mods")
JAVASSIST = os.path.join(PROJECT, "tools", "javassist.jar")

def _jvm():
    try:
        import jdk4py
        p = os.path.join(str(jdk4py.JAVA_HOME), "bin", "server", "jvm.dll")
        if os.path.exists(p): return p
    except ImportError:
        pass
    p = os.path.join(HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if os.path.exists(p): return p
    raise SystemExit("no jvm.dll found (pip install jdk4py)")

def start(server_jar=None):
    import jpype
    if not os.path.exists(JAVASSIST):
        raise SystemExit("missing " + JAVASSIST + " (javassist-3.30.2-GA.jar from Maven Central)")
    server_jar = server_jar or (sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].endswith(".jar") else __getattr__("SERVER_JAR"))
    jpype.startJVM(_jvm(), "--add-opens=java.base/java.lang=ALL-UNNAMED", "--enable-native-access=ALL-UNNAMED",
                   classpath=[JAVASSIST], convertStrings=True)
    J = jpype.JClass
    pool = J("javassist.ClassPool")(False)
    pool.appendSystemPath(); pool.appendClassPath(server_jar)
    return {"pool": pool, "CtField": J("javassist.CtField"), "CtNewMethod": J("javassist.CtNewMethod"),
            "CtNewConstructor": J("javassist.CtNewConstructor"), "CtClass": J("javassist.CtClass"),
            "Modifier": J("javassist.Modifier"), "server_jar": server_jar}

def class_out(mod_dir, name="build_classes"):
    out = os.path.join(mod_dir, name)
    shutil.rmtree(out, ignore_errors=True); os.makedirs(out)
    return out

def probe(pool, cls, member):
    """Assert a class has a method/field named `member` (catches API drift early)."""
    c = pool.get(cls)
    names = set(str(m.getName()) for m in c.getMethods()) | set(str(f.getName()) for f in c.getFields())
    if member not in names:
        raise SystemExit("API probe failed: %s.%s not found" % (cls, member))

def assemble(jar, manifest, class_dir, extra_files=None):
    with zipfile.ZipFile(jar, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("manifest.json", json.dumps(manifest, indent=2))
        for path, text in (extra_files or {}).items():
            z.writestr(path, text)
        for root, _, files in os.walk(class_dir):
            for f in files:
                if f.endswith(".class"):
                    full = os.path.join(root, f)
                    z.write(full, os.path.relpath(full, class_dir).replace(os.sep, "/"))
    print("assembled", jar, os.path.getsize(jar), "bytes")

def deploy(jar, mods_name):
    dst = os.path.join(MODS_DIR, mods_name)
    shutil.copyfile(jar, dst); print("deployed", dst)

def key_parts(key):
    """world-config / plugin key -> (group, mod name): "Skyy:0.1.13 SkyyBank" (versioned) and "Skyy:SkyyBank" (stable, SkyyCore era)
    both give ("Skyy", "SkyyBank")."""
    g, _, n = key.partition(":")
    return g, (n.split(" ", 1)[1] if " " in n else n)

def same_mod_keys(keys, key):
    """the keys among `keys` that name the SAME mod as `key` (same group + mod name, any version, stable or versioned), except key."""
    g, n = key_parts(key)
    return [k for k in keys if k != key and key_parts(k) == (g, n)]

def enable_in_world(world, key, disable_prefix=None):
    """Set Mods[key].Enabled=true in Saves/<world>/config.json. If disable_prefix is given,
    every other key starting with it whose NAME PART matches key's name part is disabled
    (so old versions of the same mod don't stay enabled). 2026-10-15 (SkyyCore): a stable key "Skyy:<Mod>" and the versioned keys
    "Skyy:<ver> <Mod>" are the same mod both ways (key_parts), so switching a mod to its stable name - or back - leaves one key on."""
    cfg = os.path.join(USERDATA, "Saves", world, "config.json")
    d = json.load(open(cfg, encoding="utf-8"))
    mods = d.setdefault("Mods", {})
    if disable_prefix:
        for k in same_mod_keys([k for k in mods if k.startswith(disable_prefix)], key):
            mods[k] = {"Enabled": False}
    mods[key] = {"Enabled": True}
    json.dump(d, open(cfg, "w", encoding="utf-8"), indent=2)
    print("world", world, "enabled", key)

def manifest(name, version, description, main, stable=False, deps=None, assets=True):
    """stable=True (SkyyCore era, research/Architecture-Spec.md 2.2 / question 1): Name = the bare mod name, the version only in
    "Version" -> world key "Skyy:<name>" and auto permission nodes skyy.<name>.command.<cmd> that never change. deps = the manifest
    "Dependencies" map {"Group:Name": "<semver range>"} (only written when given, so every existing manifest stays byte-identical)."""
    m = {"Group": "Skyy", "Name": name if stable else "%s %s" % (version, name), "Version": version, "Description": description,
         "Authors": [{"Name": "Skyy"}], "ServerVersion": "*", "DisabledByDefault": False,
         "IncludesAssetPack": bool(assets), "Main": main}
    if deps:
        m["Dependencies"] = dict(deps)
    return m

def world_key(man):
    return "%s:%s" % (man.get("Group", ""), man.get("Name", ""))

def jar_manifest(jar):
    """manifest.json of a built jar (dict) or None."""
    try:
        with zipfile.ZipFile(jar) as z:
            return json.loads(z.read("manifest.json").decode("utf-8-sig"))
    except Exception:
        return None


# ================================================================================================================ SkyyCore 1.0
# 2026-10-15, research/Architecture-Spec.md phase 1, tools/CORE-CONTRACT.md. SkyyCore = ONE library jar (stable name "SkyyCore",
# world key Skyy:SkyyCore) that modules depend on instead of copying the kits: the Server Setup config kit (one template, a private
# copy of its state per module - tools/skyycfg.py emit(..., CORE=True)), HubBar + the UI kit's Java helpers + the Sky Window art,
# the profile / bridge helpers, MoveSync. A module built in "link against SkyyCore" mode:
#     CORE = B.link_core(pool)                       # the pool sees SkyyCore's classes; CORE["range"] = the Dependencies range
#     ... compile; call com.skyy.core.* (guarded: a module's setup() must never throw - Hytale 0.7 stops the server on MOD_ERROR) ...
#     m = B.core_manifest("SkyyBank", VERSION, "...", PKG + ".SkyyBankPlugin", CORE)   # stable name + Dependencies, no own kit art
# Engine facts (phase 0 probes, Hytale 0.7.2, docs/log/2026-10.md 2026-10-15): a dependent's classes link against Core's (C1); a
# stable Name gives the key Skyy:<Name> and nodes without the version (C2); a texture only Core ships renders in a dependent's page
# (C3); a missing / disabled Core drops ONLY the dependent ("Failed to load '<id>' because the dependency 'Skyy:SkyyCore' could not
# be found!") and the world starts (C4). Range syntax: ">=1.0.0 <2.0.0" and "^1.0.0" both parse; a bare "1.0.0" is refused.
CORE_NAME = "SkyyCore"
CORE_ID = "Skyy:SkyyCore"
CORE_RANGE = ">=1.0.0 <2.0.0"
CORE_DIR = os.path.join(PROJECT, "SkyyCore")
CORE_API = "com.skyy.core."          # the public package root; com.skyy.core.cfg.Cfg{Rows,...} (the kit TEMPLATE) is not API

def semver(s):
    """'1.2.3' -> (1, 2, 3); '1.2' -> (1, 2, 0). Anything else raises ValueError."""
    p = str(s).strip().split(".")
    if not 1 <= len(p) <= 3 or not all(x.isdigit() for x in p):
        raise ValueError("not a version: %r" % (s,))
    p = [int(x) for x in p] + [0] * (3 - len(p))
    return tuple(p)

def _range_one(part, v):
    part = part.strip()
    if part in ("", "*", "x"):
        return True
    for op in (">=", "<=", ">", "<", "="):
        if part.startswith(op):
            w = semver(part[len(op):])
            return {">=": v >= w, "<=": v <= w, ">": v > w, "<": v < w, "=": v == w}[op]
    if part[0] == "^":
        w = semver(part[1:])
        hi = (w[0] + 1, 0, 0) if w[0] > 0 else ((0, w[1] + 1, 0) if w[1] > 0 else (0, 0, w[2] + 1))
        return w <= v < hi
    if part[0] == "~":
        w = semver(part[1:])
        return w <= v < (w[0], w[1] + 1, 0)
    if ".x" in part or part.endswith(".*"):
        pre = [int(x) for x in part.replace(".*", ".x").split(".") if x != "x"]
        return list(v[:len(pre)]) == pre
    raise ValueError("range part %r: a bare version is not a range (the engine refuses it; use =1.0.0, ^1.0.0 or >=1.0.0 <2.0.0)" % part)

def range_ok(rng, version):
    """the engine's SemverRange forms (PluginManifest Dependencies): '*', '>=a <b', '^a', '~a', 'a.x', 'a - b', '=a', 'x || y'."""
    v = semver(version)
    for alt in str(rng).split("||"):
        alt = alt.strip()
        if " - " in alt:
            a, b = alt.split(" - ", 1)
            if semver(a) <= v <= semver(b):
                return True
            continue
        if all(_range_one(p, v) for p in alt.split()) if alt else True:
            return True
    return False

def core_jar(version=None):
    """the SkyyCore jar to link against: SkyyCore/SkyyCore-<version>.jar. version None = the tools/deploy_set.py SET pin when SkyyCore
    is pinned, else the NEWEST built one (a module round normally builds against the newest Core)."""
    if version is None:
        try:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            import deploy_set
            pins = dict(deploy_set.SET)
            version = pins.get(CORE_NAME)
        except Exception:
            version = None
    if version is None:
        have = []
        for f in (os.listdir(CORE_DIR) if os.path.isdir(CORE_DIR) else []):
            if f.startswith(CORE_NAME + "-") and f.endswith(".jar"):
                try:
                    have.append((semver(f[len(CORE_NAME) + 1:-4]), f))
                except ValueError:
                    pass
        if not have:
            raise SystemExit("no SkyyCore jar built - run python SkyyCore/build_skyycore_<ver>.py first")
        return os.path.join(CORE_DIR, max(have)[1])
    p = os.path.join(CORE_DIR, "%s-%s.jar" % (CORE_NAME, version))
    if not os.path.isfile(p):
        raise SystemExit("SkyyCore %s is not built: %s" % (version, p))
    return p

def link_core(pool, version=None, need="1.0.0"):
    """'Link against SkyyCore' mode: put the Core jar on the javassist pool's class path (compile-time references to com.skyy.core.*)
    and return {"jar", "version", "range", "need"}. need = the lowest Core version this module's code needs (its Dependencies range
    becomes '>=<need> <next major>'); the Core jar must carry the stable name SkyyCore and a version that satisfies the range."""
    jar = core_jar(version)
    man = jar_manifest(jar)
    if not man or world_key(man) != CORE_ID:
        raise SystemExit("%s is not SkyyCore (manifest key %s)" % (jar, man and world_key(man)))
    ver = str(man.get("Version"))
    nv = semver(need)
    rng = ">=%d.%d.%d <%d.0.0" % (nv[0], nv[1], nv[2], nv[0] + 1)
    if not range_ok(rng, ver):
        raise SystemExit("SkyyCore %s does not satisfy %s (this module needs %s)" % (ver, rng, need))
    pool.appendClassPath(jar)
    try:
        pool.get(CORE_API + "Core")
    except Exception:
        raise SystemExit("SkyyCore classes not visible from %s" % jar)
    print("linked against SkyyCore %s (%s), dependency range %s" % (ver, os.path.basename(jar), rng))
    return {"jar": jar, "version": ver, "range": rng, "need": need}

# fix round 2 (critic: the spec 2.4 INLINE_CORE switch is not built, so only a sentence kept a public mod from needing SkyyCore):
# the mods Skyy releases on CurseForge on their own (docs/answered/project.md LOCKED 2026-10-03: "each standalone OR together" -
# Pocket Dimension = SkyySacks code, Skyy Accessories, Skyy Menu; spec question 4 default = SkyyCore INLINED, zero dependencies).
# core_manifest refuses these names and assemble_modules refuses a module that REPLACES one, until the release kit round builds
# INLINE_CORE (spec 2.4 / 4 "Public releases") and that round passes public_ok=True for a pack build whose public cut is inlined.
PUBLIC_MODS = ("SkyySacks", "SkyyAccessories", "SkyyMenu")

def public_guard(names, public_ok=False, what="links against SkyyCore"):
    bad = sorted(set(n for n in names if n in PUBLIC_MODS))
    if bad and not public_ok:
        raise SystemExit("PUBLIC MOD: %s - refused: %s ship(s) on CurseForge on its own (docs/answered/project.md LOCKED 2026-10-03; "
                         "spec question 4: SkyyCore INLINED, zero dependencies). The INLINE_CORE switch (research/Architecture-Spec.md "
                         "2.4) is not built yet: build the public cut with INLINE_CORE first, then pass public_ok=True here."
                         % (what, ", ".join(bad)))

def core_manifest(name, version, description, main, core, assets=False, public_ok=False):
    """the manifest of a module built in 'link against SkyyCore' mode: STABLE name (world key Skyy:<name>, version only in "Version"),
    Dependencies {"Skyy:SkyyCore": core["range"]} (core = link_core()'s answer). assets=False: the Sky Window kit art ships ONCE, in
    SkyyCore's asset pack - a module ships only its own assets. Refused for a PUBLIC_MODS name unless public_ok (see above)."""
    public_guard([name], public_ok, "%s links against SkyyCore" % name)
    return manifest(name, version, description, main, stable=True, deps={CORE_ID: core["range"]}, assets=assets)


# ================================================================================================================ MODULE ASSEMBLE
# 2026-10-13 requirement (research/Architecture-Spec.md, "parallel work inside merged jars"; Skyy: "when condensing and refining mods
# later, can we keep the marketecture organized enough that you can work on several parts of the same mods at once?"): one jar =
# several MODULES. Each module is its OWN source file (Skyy<Jar>/modules/<id>_<ver>.py; a round derives the next one with its own patch
# script, tools/CORE-CONTRACT.md section 4),
# compiles into its OWN Java package com.skyy.<jar>.<id>, keeps its OWN data folder, its OWN Server Setup section (its own config kit
# data, emit(..., CORE=True) through ctx.cfg) and its OWN harness. One assemble step builds the jar from the module files: several
# builders can work on several modules of one jar at once without touching each other's files. Modules talk only through SkyyCore and
# skyy.bridge - the assemble step REFUSES a module whose classes reference another module's package (so a module can always be cut out
# again). Each module has its own version; the jar version is the assembler's (auto = bumped when any module changed). Next to the jar
# the step writes <Jar>-<ver>.modules.json: which modules + versions + source hashes are inside, the Core range, data folders, Server
# Setup sections and harnesses.
#
# A module file:
#     MODULE = "bank"                 # id: [a-z][a-z0-9]{0,15}
#     VERSION = "1.0.0"               # the module's own version
#     TITLE = "Bank"
#     DATA = "Skyy_SkyyBank"          # optional, default "Skyy_<Jar>/<id>" (a folder under the world's mods/); never the same
#                                     #   folder as (or nested in / around) another module's or another SET jar's (case-insensitive)
#     REPLACES = "SkyyBank"           # optional: the standalone SET mod whose data folder / Server Setup section this module takes
#                                     #   over (a merge); the old mod must leave the SET before the jar is pinned (crosscheck refuses
#                                     #   both); never a PUBLIC_MODS mod until INLINE_CORE exists (public_ok)
#     HARNESS = "SkyyEconomy/modules/test_bank.py"     # optional (recorded; must exist)
#     def build(ctx): ...             # make classes with ctx.make(...) / ctx.M / ctx.F / ctx.C; must make <pkg>.Module with
#                                     #   public static String setup(com.hypixel.hytale.server.core.plugin.JavaPlugin p)  (ready text;
#                                     #     loads data, starts the kit / ticks, publishes bridge keys - NO engine registrations)
#                                     #   public static void register(JavaPlugin p)  OPTIONAL: the ONLY place that may call
#                                     #     p.get*Registry() (systems, commands, events, tasks); runs after setup() succeeded
#                                     #   public static void shutdown()   (normal stop: save, stop, unpublish)
#                                     #   public static void abort()      (undo a FAILED / part-way setup or register: stop what was
#                                     #     started, NEVER save - the store may be empty or half-loaded)
#                                     # Server Setup: ctx.cfg(MOD="SkyyBank", TITLE=..., ...) = skyycfg.emit(..., CORE=True, HOME=ctx.data);
#                                     #   one MOD per section, never one another module or SET jar publishes (unless REPLACES)
# The jar's plugin class runs every module's setup() (+ register()) in the listed order, each guarded (a module that throws is
# logged, its abort() runs, the skyy.bridge map is put back as it was before that module started, and it stays OFF; the plugin
# never throws), prints "[<Jar>] part <id> <ver> ready - <text>" per module and "[<Jar>] <jar ver> ready (<id> <ver>, ...)".
MODULE_ID_RE = __import__("re").compile(r"^[a-z][a-z0-9]{0,15}$")
JAR_NAME_RE = __import__("re").compile(r"^Skyy[A-Z][A-Za-z]{1,30}$")
JP_CLASS = "com.hypixel.hytale.server.core.plugin.JavaPlugin"
JPI_CLASS = "com.hypixel.hytale.server.core.plugin.JavaPluginInit"
LOG_CLASS = "com.hypixel.hytale.logger.HytaleLogger"


class ModuleCtx(object):
    """What a module's build(ctx) gets. ctx.pkg = its Java package; ctx.data = its data folder under mods/; ctx.core = link_core's
    answer; ctx.make / M / F / C compile into the module's package (@PKG@ @DATA@ @MODULE@ @JAR@ are filled in sources);
    ctx.cfg(...) = its Server Setup section; ctx.asset(path, bytes) = a file in the jar's asset pack."""

    def __init__(self, J, jar, jar_version, mid, version, title, pkg, data, core, source):
        self.J, self.pool = J, J["pool"]
        self.CtField, self.CtNewMethod, self.CtNewConstructor = J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
        self.jar, self.jar_version, self.id, self.version, self.title = jar, jar_version, mid, version, title
        self.pkg, self.data, self.core, self.source = pkg, data, core, source
        self.classes, self.assets, self.kits, self.config = [], {}, [], []

    def jv(self, src):
        return (src.replace("@PKG@", self.pkg).replace("@DATA@", self.data).replace("@MODULE@", self.id)
                .replace("@JAR@", self.jar).replace("@MVER@", self.version))

    def make(self, name, sup=None, iface=None):
        if "." in name:
            raise SystemExit("module %s: ctx.make takes a simple class name (the package is %s)" % (self.id, self.pkg))
        c = self.pool.makeClass(self.pkg + "." + name, self.pool.get(sup)) if sup else self.pool.makeClass(self.pkg + "." + name)
        if iface:
            c.addInterface(self.pool.get(iface))
        self.classes.append(c)
        return c

    def M(self, cls, src):
        try:
            cls.addMethod(self.CtNewMethod.make(self.jv(src), cls))
        except Exception as e:
            raise SystemExit("module %s: compile failed in %s:\n%s\n---\n%s" % (self.id, cls.getName(), e, self.jv(src)[:2000]))

    def F(self, cls, src):
        try:
            cls.addField(self.CtField.make(self.jv(src), cls))
        except Exception as e:
            raise SystemExit("module %s: field failed in %s:\n%s\n---\n%s" % (self.id, cls.getName(), e, self.jv(src)[:600]))

    def C(self, cls, src):
        try:
            cls.addConstructor(self.CtNewConstructor.make(self.jv(src), cls))
        except Exception as e:
            raise SystemExit("module %s: constructor failed in %s:\n%s\n---\n%s" % (self.id, cls.getName(), e, self.jv(src)[:1500]))

    def cfg(self, **kw):
        """the module's Server Setup section: tools/skyycfg.py emit(pool, ctx.pkg, ..., CORE=True, HOME=ctx.data); write happens at
        assemble time (kit.write after every module compiled)."""
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import skyycfg
        kw.setdefault("HOME", self.data)
        kit = skyycfg.emit(self.pool, self.pkg, CORE=True, **kw)
        self.kits.append(kit)
        self.config.append(kw["MOD"])
        return kit

    def asset(self, path, data):
        if path in self.assets:
            raise SystemExit("module %s: asset %s added twice" % (self.id, path))
        self.assets[path] = data


def _sha256(path):
    import hashlib
    return hashlib.sha256(open(path, "rb").read()).hexdigest()

def _load_module_file(path, idx):
    import importlib.util
    spec = importlib.util.spec_from_file_location("skyy_module_%d_%s" % (idx, os.path.splitext(os.path.basename(path))[0]), path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def module_boundary_refs(ctclass, own_pkg):
    """class names a module class references that it must not: any com.skyy.* outside its own package, except SkyyCore's public
    API (com.skyy.core.*, never the kit template com.skyy.core.cfg.Cfg{Rows,...})."""
    bad = []
    tmpl = set("com.skyy.core.cfg." + c for c in ("CfgRows", "CfgLog", "CfgHist", "CfgSaveTask", "CfgFile", "CfgFn", "CfgPub"))
    for n in sorted(str(x) for x in ctclass.getRefClasses()):
        if not n.startswith("com.skyy."):
            continue
        if n.startswith(own_pkg + "."):
            continue
        if n.startswith(CORE_API) and n not in tmpl:
            continue
        bad.append(n)
    return bad

def data_clash(a, b):
    """True when two data folders (paths under the world's mods/) are one folder or one sits inside the other - compared
    case-insensitively (Windows folders: Skyy_Eco/Bank = Skyy_Eco/bank)."""
    a, b = a.replace("\\", "/").strip("/").lower(), b.replace("\\", "/").strip("/").lower()
    return a == b or a.startswith(b + "/") or b.startswith(a + "/")

def jar_data_folders(mod, jar_path):
    """the data folders a jar owns: an assembled jar's <Jar>-<ver>.modules.json next to it lists its modules' folders; any other
    Skyy jar owns Skyy_<mod> (the convention every standalone mod follows). Returns ([(folder, module id or None)], replaces list)."""
    mj = os.path.splitext(jar_path)[0] + ".modules.json"
    if os.path.isfile(mj):
        try:
            mm = json.load(open(mj, encoding="utf-8"))
            return ([(e["data"], e["id"]) for e in mm.get("modules", [])],
                    sorted(set(r for e in mm.get("modules", []) for r in (e.get("replaces") or []))))
        except Exception:
            pass
    return [("Skyy_" + mod, None)], []

def set_data_folders(skip):
    """[(SET mod, folder)] for every pinned jar in tools/deploy_set.py SET except the jar named skip (None when SET can't be read)."""
    try:
        import deploy_set
        pins = list(deploy_set.SET)
    except Exception:
        return None
    out = []
    for mod, ver in pins:
        if mod == skip:
            continue
        for f, _mid in jar_data_folders(mod, os.path.join(PROJECT, mod, "%s-%s.jar" % (mod, ver)))[0]:
            out.append((mod, f))
    return out

def class_string_const(data, field):
    """the String constant of a 'static final String <field> = "...";' in a class file (bytes), or None. Pure Python (no JVM): the
    field's ConstantValue attribute -> CONSTANT_String -> CONSTANT_Utf8 (modified UTF-8; our MOD names are ASCII)."""
    import struct
    try:
        if data[:4] != b"\xca\xfe\xba\xbe":
            return None
        n = struct.unpack(">H", data[8:10])[0]
        cp, i, k = [None] * n, 10, 1
        size = {3: 4, 4: 4, 5: 8, 6: 8, 7: 2, 8: 2, 9: 4, 10: 4, 11: 4, 12: 4, 15: 3, 16: 2, 17: 4, 18: 4, 19: 2, 20: 2}
        while k < n:
            tag = data[i]
            if tag == 1:
                ln = struct.unpack(">H", data[i + 1:i + 3])[0]
                cp[k] = (1, data[i + 3:i + 3 + ln].decode("utf-8", "replace"))
                i += 3 + ln
            else:
                cp[k] = (tag, data[i + 1:i + 1 + size[tag]])
                i += 1 + size[tag]
            k += 2 if tag in (5, 6) else 1
        i += 6                                                          # access, this, super
        ni = struct.unpack(">H", data[i:i + 2])[0]
        i += 2 + 2 * ni
        nf = struct.unpack(">H", data[i:i + 2])[0]
        i += 2
        for _ in range(nf):
            _acc, nm, _ds, na = struct.unpack(">HHHH", data[i:i + 8])
            i += 8
            for _ in range(na):
                an, al = struct.unpack(">HI", data[i:i + 6])
                if cp[nm][1] == field and cp[an][1] == "ConstantValue":
                    v = cp[struct.unpack(">H", data[i + 6:i + 8])[0]]
                    if v[0] == 8:
                        return cp[struct.unpack(">H", v[1])[0]][1]
                i += 6 + al
    except Exception:
        return None
    return None

def jar_config_sections(jar_path):
    """the Server Setup sections a jar publishes (config:def / config:fn / config:epoch:<MOD>): [(package, MOD)] from every config
    kit's CfgRows (old-way kit) / CfgData (Core-mode kit) 'MOD' constant. SkyyCore's own kit template is not a section."""
    out = []
    try:
        with zipfile.ZipFile(jar_path) as z:
            for n in z.namelist():
                if not (n.endswith("/CfgRows.class") or n.endswith("/CfgData.class")) or n.startswith("com/skyy/core/"):
                    continue
                v = class_string_const(z.read(n), "MOD")
                if v:
                    out.append((n.rsplit("/", 1)[0].replace("/", "."), v))
    except Exception:
        pass
    return sorted(set(out))

def set_config_sections(skip):
    """[(SET mod, MOD)] for every pinned jar in tools/deploy_set.py SET except the jar named skip (None when SET can't be read)."""
    try:
        import deploy_set
        pins = list(deploy_set.SET)
    except Exception:
        return None
    out = []
    for mod, ver in pins:
        if mod != skip:
            out += [(mod, sec) for _p, sec in jar_config_sections(os.path.join(PROJECT, mod, "%s-%s.jar" % (mod, ver)))]
    return out

REGISTRY_RE = __import__("re").compile(r"^get\w*Registry$|^getEventBus$")

def registry_calls(ctclass, Modifier=None):
    """[(method, 'Class.name')] for every call in a module class to an engine REGISTRY getter (PluginBase.getCommandRegistry /
    getEventRegistry / getEntityStoreRegistry / getChunkStoreRegistry / getTaskRegistry / getCodecRegistry / ... and any
    com.hypixel *.get*Registry / getEventBus): the ways a plugin registers engine things that the engine only removes when the whole
    plugin stops. Read from the bytecode (invokevirtual / special / static / interface method refs)."""
    out = []
    behaviors = list(ctclass.getDeclaredBehaviors())
    ci_ = ctclass.getClassInitializer()
    if ci_ is not None:
        behaviors.append(ci_)
    for b in behaviors:
        mi = b.getMethodInfo()
        code = mi.getCodeAttribute()
        if code is None:
            continue
        cp = mi.getConstPool()
        it = code.iterator()
        while it.hasNext():
            pos = it.next()
            op = it.byteAt(pos)
            if op not in (182, 183, 184, 185):
                continue
            idx = it.u16bitAt(pos + 1)
            if cp.getTag(idx) == 11:
                cn, mn = str(cp.getInterfaceMethodrefClassName(idx)), str(cp.getInterfaceMethodrefName(idx))
            else:
                cn, mn = str(cp.getMethodrefClassName(idx)), str(cp.getMethodrefName(idx))
            if cn.startswith("com.hypixel.") and REGISTRY_RE.match(mn):
                out.append(("%s.%s%s" % (ctclass.getName(), b.getName(), b.getSignature()), "%s.%s" % (cn, mn)))
    return out

def next_jar_version(jar_dir, jar_name, entries):
    """the jar version for a module list: the newest recorded <Jar>-<ver>.modules.json's version when its modules (id, version,
    source hash) are the same, else that version with the last number + 1 ("1.0.0" when nothing was recorded yet)."""
    import re as _re
    best = None
    for f in (os.listdir(jar_dir) if os.path.isdir(jar_dir) else []):
        m = _re.match(r"^%s-(\d+\.\d+\.\d+)\.modules\.json$" % _re.escape(jar_name), f)
        if m:
            v = semver(m.group(1))
            if best is None or v > best[0]:
                best = (v, os.path.join(jar_dir, f))
    if best is None:
        return "1.0.0"
    old = json.load(open(best[1], encoding="utf-8"))
    sig = lambda es: [(e["id"], e["version"], e["source_sha256"]) for e in es]
    v = best[0]
    if sig(old.get("modules", [])) == sig(entries):
        return "%d.%d.%d" % v
    return "%d.%d.%d" % (v[0], v[1], v[2] + 1)

def assemble_modules(J, jar_name, jar_version, module_files, description, here, core=None, out_jar=None, check_refs=True,
                     public_ok=False):
    """THE MODULE ASSEMBLE STEP (section comment above). J = start(); module_files = the module source files, in setup order;
    jar_version = "x.y.z" or "auto" (next_jar_version). Writes the jar (stable name jar_name, depends on SkyyCore) and
    <Jar>-<ver>.modules.json next to it. Returns (jar path, module manifest dict). Refuses: a bad / duplicate module id, a module
    without public static <pkg>.Module.setup(JavaPlugin) String / shutdown() / abort() (register(JavaPlugin) optional), a module
    class that calls an engine registry getter outside Module.register (registry_calls), a module class that references another
    module (or any com.skyy.* that is not its own package or SkyyCore's API), two modules (or a module and another SET jar) on one
    data folder or one Server Setup section (MOD) unless REPLACES names that jar, a REPLACES of a PUBLIC_MODS mod (public_ok), the
    same asset path from two modules, and a jar version already recorded with DIFFERENT module contents (bump it)."""
    import re as _re
    if not JAR_NAME_RE.match(jar_name):
        raise SystemExit("jar name %r must match Skyy[A-Z][A-Za-z]{1,30}" % jar_name)
    pool = J["pool"]
    core = core or link_core(pool)
    root = "com.skyy." + jar_name[4:].lower()
    entries, ctxs, mods, seen = [], [], [], set()
    for i, f in enumerate(module_files):
        f = os.path.abspath(f)
        m = _load_module_file(f, i)
        mid, ver = getattr(m, "MODULE", None), getattr(m, "VERSION", None)
        if not isinstance(mid, str) or not MODULE_ID_RE.match(mid):
            raise SystemExit("%s: MODULE must be an id like bank ([a-z][a-z0-9]{0,15}), got %r" % (f, mid))
        if mid in seen:
            raise SystemExit("%s: module id %s is used twice in %s" % (f, mid, jar_name))
        seen.add(mid)
        try:
            semver(ver)
        except Exception:
            raise SystemExit("%s: VERSION must be x.y.z, got %r" % (f, ver))
        data = getattr(m, "DATA", "Skyy_%s/%s" % (jar_name, mid))
        if not _re.match(r"^[A-Za-z0-9_.\-]+(/[A-Za-z0-9_.\-]+)*$", data) or ".." in data.split("/"):
            raise SystemExit("%s: DATA %r must be a plain folder under mods/" % (f, data))
        harness = getattr(m, "HARNESS", None)
        if harness is not None and not os.path.isfile(harness if os.path.isabs(harness) else os.path.join(PROJECT, harness)):
            raise SystemExit("%s: HARNESS %s does not exist" % (f, harness))
        if not callable(getattr(m, "build", None)):
            raise SystemExit("%s: no build(ctx)" % f)
        ctx = ModuleCtx(J, jar_name, jar_version, mid, ver, getattr(m, "TITLE", mid), root + "." + mid, data, core, f)
        m.build(ctx)
        ctxs.append(ctx)
        mods.append(m)
    # data folders (fix round: the old check caught only identical strings): no two modules share one folder or nest one in the
    # other (case-insensitive); no module lands on a folder another SET jar owns (a standalone mod's Skyy_<Mod>, an assembled jar's
    # module folders) unless it names that standalone mod in REPLACES (a merge: the old mod then has to leave the SET before the
    # pin - tools/ci/crosscheck.py refuses a set holding both).
    for i in range(len(ctxs)):
        for k in range(i + 1, len(ctxs)):
            if data_clash(ctxs[i].data, ctxs[k].data):
                raise SystemExit("two modules share one data folder: %s (%s) and %s (%s) - one folder per module, never nested, "
                                 "case-insensitive" % (ctxs[i].id, ctxs[i].data, ctxs[k].id, ctxs[k].data))
    replaces = {}
    for c, m in zip(ctxs, mods):
        r = getattr(m, "REPLACES", None)
        r = [] if r is None else ([r] if isinstance(r, str) else list(r))
        if not all(isinstance(x, str) and JAR_NAME_RE.match(x) and x != jar_name for x in r):
            raise SystemExit("%s: REPLACES must name standalone Skyy mods (not %s itself), got %r" % (c.source, jar_name, r))
        replaces[c.id] = sorted(set(r))
        public_guard(r, public_ok, "module %s REPLACES %s (its public cut would need SkyyCore)" % (c.id, ", ".join(r)))
    owned = set_data_folders(jar_name)
    if owned is None:
        print("WARN: tools/deploy_set.py SET not readable - the data folders were not checked against the SET's jars")
    for c in ctxs:
        for mod, f in owned or []:
            if data_clash(c.data, f) and not (mod in replaces[c.id] and f.lower() == ("skyy_" + mod).lower()):
                raise SystemExit("module %s: DATA %s is (inside / around) %s's data folder %s - two jars would write one folder "
                                 "(duplicate coins / items). Pick another folder, or for a merge name it in REPLACES = %r"
                                 % (c.id, c.data, mod, f, mod))
    # Server Setup sections (fix round 2, critic: the kit publishes config:def / config:fn / config:epoch:<MOD> with a plain put, so
    # two kits with one MOD silently overwrite each other - SkyyMenu's edits for one section would land in the other's rows): one
    # MOD per section, never two modules on one MOD (case-insensitive), never a MOD another SET jar publishes - unless the module
    # REPLACES that jar (a merge taking over its section, e.g. MOD="SkyyBank" with REPLACES = "SkyyBank").
    secs = {}
    for c in ctxs:
        for sec in c.config:
            if sec.lower() in secs:
                raise SystemExit("two Server Setup sections named %s: module %s (%s) and module %s (%s) - the second would overwrite "
                                 "the first's config:def / config:fn / config:epoch keys (one MOD per section, case-insensitive)"
                                 % (secs[sec.lower()][1], secs[sec.lower()][0], secs[sec.lower()][1], c.id, sec))
            secs[sec.lower()] = (c.id, sec)
    sset = set_config_sections(jar_name)
    if sset is None:
        print("WARN: tools/deploy_set.py SET not readable - the Server Setup sections were not checked against the SET's jars")
    for c in ctxs:
        for sec in c.config:
            for mod, other in sset or []:
                if sec.lower() == other.lower() and mod not in replaces[c.id]:
                    raise SystemExit("module %s: Server Setup section %s is already published by %s (MOD %s) - the two would overwrite "
                                     "each other's config:* keys. Pick another MOD, or for a merge name it in REPLACES = %r"
                                     % (c.id, sec, mod, other, mod))
    for c in ctxs:     # every kit's deferred checks (hooks may live in any class of that module)
        for k in c.kits:
            k.check()
    S, V = "Ljava/lang/String;", "V"
    for c in ctxs:
        try:
            mc = pool.get(c.pkg + ".Module")
        except Exception:
            raise SystemExit("module %s: no class %s.Module (setup / shutdown)" % (c.id, c.pkg))
        sigs = dict((str(x.getName()) + str(x.getSignature()), x) for x in mc.getDeclaredMethods())
        reg_sig = "register(L%s;)%s" % (JP_CLASS.replace(".", "/"), V)
        need = ["setup(L%s;)%s" % (JP_CLASS.replace(".", "/"), S), "shutdown()" + V, "abort()" + V]
        Mod = J["Modifier"]
        for n in need + ([reg_sig] if reg_sig in sigs or any(k.startswith("register(") for k in sigs) else []):
            x = sigs.get(n)
            if x is None or not Mod.isPublic(x.getModifiers()) or not Mod.isStatic(x.getModifiers()):
                raise SystemExit("module %s: %s.Module needs public static %s" % (c.id, c.pkg, n))
        c.has_register = reg_sig in sigs
        # engine registrations only in Module.register (fix round 2, critic: a module that registered a system / command / event
        # and then threw left it live against a module marked OFF - the engine removes them only when the whole plugin stops)
        allowed = "%s.Module.register(L%s;)V" % (c.pkg, JP_CLASS.replace(".", "/"))
        regs = [(w, t) for cl in c.classes for w, t in registry_calls(cl) if w != allowed]
        if regs:
            raise SystemExit("ENGINE REGISTRATION: module %s gets an engine registry outside %s.Module.register(JavaPlugin) - systems, "
                             "commands, events and tasks are registered ONLY there (the dispatcher calls it after setup() succeeded; "
                             "the engine has no unregister):\n  %s" % (c.id, c.pkg, "\n  ".join("%s -> %s" % x for x in regs)))
    if check_refs:
        bad = []
        for c in ctxs:
            for cl in c.classes + [k_ for kit in c.kits for k_ in kit.classes]:
                for n in module_boundary_refs(cl, c.pkg):
                    bad.append("%s: %s -> %s" % (c.id, cl.getName(), n))
        if bad:
            raise SystemExit("MODULE BOUNDARY: a module may use only its own package, SkyyCore's API, the engine and the JDK "
                             "(other modules only through skyy.bridge):\n  " + "\n  ".join(bad))
    assets = {}
    for c in ctxs:
        for p, d in c.assets.items():
            if p in assets:
                raise SystemExit("asset %s comes from two modules" % p)
            assets[p] = d
    for c in ctxs:
        entries.append({"id": c.id, "version": c.version, "title": c.title, "package": c.pkg, "data": c.data,
                        "config": c.config, "classes": sorted(str(x.getName()) for x in c.classes) +
                        sorted(str(k_.getName()) for kit in c.kits for k_ in kit.classes),
                        "source": os.path.relpath(c.source, PROJECT).replace(os.sep, "/"), "source_sha256": _sha256(c.source),
                        "harness": getattr(mods[ctxs.index(c)], "HARNESS", None), "replaces": replaces[c.id]})
    if jar_version == "auto":
        jar_version = next_jar_version(here, jar_name, entries)
    semver(jar_version)
    mpath = os.path.join(here, "%s-%s.modules.json" % (jar_name, jar_version))
    if os.path.isfile(mpath):
        old = json.load(open(mpath, encoding="utf-8"))
        sig = lambda es: [(e["id"], e["version"], e["source_sha256"]) for e in es]
        if sig(old.get("modules", [])) != sig(entries):
            raise SystemExit("%s %s was already assembled from DIFFERENT modules (%s) - bump the jar version (or pass 'auto')"
                             % (jar_name, jar_version, os.path.basename(mpath)))
    # the dispatcher + the plugin (generated; the only classes in the jar's root package)
    CtNewMethod, CtField, CtNewConstructor = J["CtNewMethod"], J["CtField"], J["CtNewConstructor"]
    disp = pool.makeClass(root + ".Modules")
    ids = [c.id for c in ctxs]
    vers = [c.version for c in ctxs]
    jl = lambda xs: "new String[] { " + ", ".join(json.dumps(x) for x in xs) + " }"
    disp.addField(CtField.make("public static final String[] IDS = %s;" % jl(ids), disp))
    disp.addField(CtField.make("public static final String[] VERSIONS = %s;" % jl(vers), disp))
    disp.addField(CtField.make("public static final boolean[] ON = new boolean[%d];" % len(ids), disp))
    disp.addField(CtField.make('public static volatile String SUMMARY = "";', disp))
    disp.addMethod(CtNewMethod.make(r"""
public static void say(%s log, boolean warn, String m) {
  try { if (log != null) log.at(warn ? java.util.logging.Level.WARNING : java.util.logging.Level.INFO).log(m); } catch (Throwable t) { }
}""" % LOG_CLASS, disp))
    # fix round (critic: a module whose setup() throws part-way was never shut down - its scheduled ticks / workers / bridge keys
    # kept running while the log said OFF) + fix round 2 (critics: calling shutdown() on a half-started module can SAVE an empty /
    # half-loaded store over the real file (coins wiped); the undo removed only NEW keys and never put back a key the failed module
    # overwrote, e.g. another jar's *:fn:* publisher). Now: the dispatcher takes a snapshot of the skyy.bridge map (key -> value)
    # before each module's setup(); when setup() (or its register()) throws it calls that module's abort() - NEVER shutdown(): abort
    # stops what setup started and saves NOTHING - and then puts the bridge map back: a key that appeared is removed, a key whose
    # value is no longer the SAME object is restored, a key that vanished is put back (one WARN line each). PluginManager runs the
    # plugins' setup() one after another (checked in HytaleServer.jar), so nothing else writes the map during that window.
    disp.addMethod(CtNewMethod.make(r"""
public static void sayAt(%s log, java.util.logging.Level lv, String m) {
  try { if (log != null) log.at(lv).log(m); } catch (Throwable t) { }
}""" % LOG_CLASS, disp))
    disp.addMethod(CtNewMethod.make(r"""
public static java.util.Map bridgeSnap() {
  try {
    Object o = System.getProperties().get("skyy.bridge");
    if (o instanceof java.util.Map) return new java.util.HashMap((java.util.Map) o);
  } catch (Throwable t) { }
  return new java.util.HashMap();
}""", disp))
    disp.addMethod(CtNewMethod.make(r"""
public static int undoKeys(java.util.Map before, %s log, String tag) {
  int n = 0;
  try {
    Object o = System.getProperties().get("skyy.bridge");
    if (before == null || !(o instanceof java.util.Map)) return 0;
    java.util.Map m = (java.util.Map) o;
    java.util.Iterator it = new java.util.ArrayList(m.keySet()).iterator();
    while (it.hasNext()) {
      Object k = it.next();
      try {
        if (!before.containsKey(k)) {
          m.remove(k);
          n = n + 1;
          say(log, true, tag + " removed bridge key " + k + " (added by its failed start)");
        } else {
          Object was = before.get(k);
          if (m.get(k) != was) {
            m.put(k, was);
            n = n + 1;
            say(log, true, tag + " restored bridge key " + k + " (its failed start had replaced it)");
          }
        }
      } catch (Throwable t1) { say(log, true, tag + " could not undo bridge key " + k + ": " + t1); }
    }
    it = new java.util.ArrayList(before.keySet()).iterator();
    while (it.hasNext()) {
      Object k = it.next();
      try {
        if (!m.containsKey(k)) {
          m.put(k, before.get(k));
          n = n + 1;
          say(log, true, tag + " restored bridge key " + k + " (its failed start had removed it)");
        }
      } catch (Throwable t1) { say(log, true, tag + " could not restore bridge key " + k + ": " + t1); }
    }
  } catch (Throwable t) { }
  return n;
}""" % LOG_CLASS, disp))
    body = ['public static String setupAll(%s p, %s log) {' % (JP_CLASS, LOG_CLASS), '  StringBuilder ok = new StringBuilder();',
            '  int n = 0;', '  java.util.Map before = null;', '  int stage = 0;', '  String d = null;']
    for i, c in enumerate(ctxs):
        tag = "[%s] part %s %s" % (jar_name, c.id, c.version)
        body += ['  before = bridgeSnap();',
                 '  stage = 0;',
                 '  try {',
                 '    d = %s.Module.setup(p);' % c.pkg,
                 '    stage = 1;']
        if getattr(c, "has_register", False):
            body += ['    %s.Module.register(p);' % c.pkg]
        body += ['    ON[%d] = true;' % i,
                 '    n = n + 1;',
                 '    say(log, false, %s + ((d == null || d.length() == 0) ? "" : " - " + d));' % json.dumps(tag + " ready"),
                 '    if (ok.length() > 0) ok.append(", ");',
                 '    ok.append(%s);' % json.dumps("%s %s" % (c.id, c.version)),
                 '  } catch (Throwable t) {',
                 '    ON[%d] = false;' % i,
                 '    if (stage == 0) say(log, true, %s + t);' % json.dumps(tag + " FAILED to start and stays OFF (the other modules run): "),
                 '    else sayAt(log, java.util.logging.Level.SEVERE, %s + t);'
                 % json.dumps(tag + " FAILED in register() and stays OFF - the engine things it registered before the throw stay "
                              "live until the server stops: "),
                 '    try { %s.Module.abort(); say(log, true, %s); } catch (Throwable t2) { say(log, true, %s + t2); }'
                 % (c.pkg, json.dumps(tag + " aborted after its failed start (nothing saved)"),
                    json.dumps(tag + " abort after its failed start failed: ")),
                 '    undoKeys(before, log, %s);' % json.dumps(tag),
                 '  }']
    body += ['  SUMMARY = ok.toString();', '  return n + " of %d modules: " + SUMMARY;' % len(ctxs), '}']
    disp.addMethod(CtNewMethod.make("\n".join(body), disp))
    body = ['public static void shutdownAll(%s log) {' % LOG_CLASS]
    for i in range(len(ctxs) - 1, -1, -1):
        c = ctxs[i]
        body += ['  if (ON[%d]) {' % i, '    try { %s.Module.shutdown(); } catch (Throwable t) { say(log, true, %s + t); }'
                 % (c.pkg, json.dumps("[%s] part %s shutdown failed: " % (jar_name, c.id))), '    ON[%d] = false;' % i, '  }']
    body += ['}']
    disp.addMethod(CtNewMethod.make("\n".join(body), disp))
    plc = pool.makeClass(root + "." + jar_name + "Plugin", pool.get(JP_CLASS))
    plc.addConstructor(CtNewConstructor.make("public %sPlugin(%s init) { super(init); }" % (jar_name, JPI_CLASS), plc))
    plc.addMethod(CtNewMethod.make(r"""
public void setup() {
  String s = "?";
  try { s = %s.Modules.setupAll(this, getLogger()); }
  catch (Throwable t) { try { getLogger().at(java.util.logging.Level.WARNING).log("[%s] module start failed: " + t); } catch (Throwable t2) { } }
  try { getLogger().at(java.util.logging.Level.INFO).log("[%s] %s ready (" + s + "; SkyyCore " + com.skyy.core.Core.version() + ")"); } catch (Throwable t) { }
}""" % (root, jar_name, jar_name, jar_version), plc))
    plc.addMethod(CtNewMethod.make(r"""
protected void shutdown() {
  try { %s.Modules.shutdownAll(getLogger()); } catch (Throwable t) { }
  super.shutdown();
}""" % root, plc))
    out = class_out(here)
    for c in ctxs:
        for cl in c.classes:
            cl.writeFile(out)
        for kit in c.kits:
            kit.write(out)
    disp.writeFile(out)
    plc.writeFile(out)
    jar = out_jar or os.path.join(here, "%s-%s.jar" % (jar_name, jar_version))
    man = core_manifest(jar_name, jar_version, description, root + "." + jar_name + "Plugin", core, assets=bool(assets))
    assemble(jar, man, out, assets)
    mm = {"jar": jar_name, "version": jar_version, "key": world_key(man), "core": {"id": CORE_ID, "range": core["range"],
          "built_against": core["version"]}, "plugin": root + "." + jar_name + "Plugin", "modules": entries}
    open(mpath, "w", encoding="utf-8", newline="\n").write(json.dumps(mm, indent=1) + "\n")
    print("module manifest", mpath, "-", ", ".join("%s %s" % (e["id"], e["version"]) for e in entries))
    return jar, mm
