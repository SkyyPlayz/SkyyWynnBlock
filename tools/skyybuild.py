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
SERVER_JAR= os.path.join(HYTALE, "install", "release", "package", "game", "latest", "Server", "HytaleServer.jar")
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
    server_jar = server_jar or (sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].endswith(".jar") else SERVER_JAR)
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

def enable_in_world(world, key, disable_prefix=None):
    """Set Mods[key].Enabled=true in Saves/<world>/config.json. If disable_prefix is given,
    every other key starting with it whose NAME PART matches key's name part is disabled
    (so old versions of the same mod don't stay enabled)."""
    cfg = os.path.join(USERDATA, "Saves", world, "config.json")
    d = json.load(open(cfg, encoding="utf-8"))
    mods = d.setdefault("Mods", {})
    modname = key.split(" ", 1)[1] if " " in key else key
    for k in list(mods):
        if disable_prefix and k.startswith(disable_prefix) and k != key and k.endswith(" " + modname):
            mods[k] = {"Enabled": False}
    mods[key] = {"Enabled": True}
    json.dump(d, open(cfg, "w", encoding="utf-8"), indent=2)
    print("world", world, "enabled", key)

def manifest(name, version, description, main):
    return {"Group": "Skyy", "Name": "%s %s" % (version, name), "Version": version, "Description": description,
            "Authors": [{"Name": "Skyy"}], "ServerVersion": "*", "DisabledByDefault": False,
            "IncludesAssetPack": True, "Main": main}
