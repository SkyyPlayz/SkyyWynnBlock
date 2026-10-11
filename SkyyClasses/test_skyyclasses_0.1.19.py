"""SkyyClasses 0.1.19 - bare-JVM harness for THE LOADOUT BRIDGE ONLY (tools/classes_0_1_19_patch.py; the SkyyWardrobe 0.1 round).
Child JVMs run the game's own JRE with HytaleServer.jar on the class path, -Xverify:all, -XX:-UsePerfData, java.io.tmpdir in scratch.
Live save data is only ever READ and copied into scratch.

    python SkyyClasses/test_skyyclasses_0.1.19.py --dir <empty folder inside tools/dev/scratch/> [--keep]

SECTIONS
  A   every class of SkyyClasses 0.1.19 loads, verifies (-Xverify:all) and initialises
  CC  CLASS COMPARE 0.1.18 -> 0.1.19 (javassist instruction text, the version string normalised): AbilLoadout, LoadoutGetFn, LoadoutSetFn
      are the only new classes; the only structural change elsewhere is SkyyClassesPlugin.setup (the two b.put lines + the ready line)
  L   EXECUTED: class:fn:loadoutGet / class:fn:loadoutSet through the bridge after the real setup()-equivalent puts, on a Mage / Priest
      with a stand-in skill:fn:level and profile:class:<uuid>: no class -> null; the snapshot text (class, alt, p1 p2 a1 a2, the names,
      mods empty); the same snapshot -> "+" and NO file write; a re-order -> written and read back; the A / B alt pick (allowed at the
      unlock level, skipped below it); a re-order that moves a locked ability -> skipped; a wrong class -> "-" and nothing written; a
      bad snapshot / bad arguments; modifiers in the snapshot -> skipped "not in the game yet"; an unreadable ability file -> "-", never
      written; every result's first character
  ST  START TWICE on a scratch COPY of the live Skyy_SkyyClasses folder: nothing written
"""
import os, sys, re, json, shutil, subprocess, zipfile, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B

VERSION, PREV_VERSION = "0.1.19", "0.1.18"
PKG = "com.skyy.classes."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "wardrobe01", "classes0119")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyClasses-%s.jar" % VERSION)))
PREV_JAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyyClasses-%s.jar" % PREV_VERSION)))
LIVE = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyClasses")
FAILS, OKS = [], [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def jvm(cp, verify=True):
    import jpype
    j = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(j):
        j = B._jvm()
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    opts = (["-Xverify:all"] if verify else []) + ["-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp]
    jpype.startJVM(j, *opts, classpath=list(cp), convertStrings=True)


def tree_hash(root):
    out = {}
    for d, _, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            out[os.path.relpath(p, root)] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


# ============================================================================================================ child: A + L
def run_l(out):
    from jpype import JClass, JImplements, JOverride, JArray, JObject, JInt
    R = {"checks": []}

    def ck(c, w):
        R["checks"].append([bool(c), w])
    jvm([B.SERVER_JAR, JAR])
    try:
        Cls, loader = JClass("java.lang.Class"), JClass("java.lang.ClassLoader").getSystemClassLoader()
        names = sorted(n[:-6].replace("/", ".") for n in zipfile.ZipFile(JAR).namelist() if n.endswith(".class"))
        bad = []
        for cn in names:
            try:
                Cls.forName(cn, True, loader)
            except Exception as e:
                bad.append("%s: %s" % (cn, e))
        ck(not bad, "A every class loads, verifies (-Xverify:all) and initialises (%d classes): %s" % (len(names), bad[:3]))
        P = lambda n: JClass(PKG + n)
        Paths = JClass("java.nio.file.Paths")
        base = os.path.join(SCRATCH, "l-home")
        shutil.rmtree(base, ignore_errors=True)
        os.makedirs(os.path.join(base, "players"))
        os.makedirs(os.path.join(base, "abilities"))
        P("ClassStore").DIR = Paths.get(os.path.join(base, "players"))
        P("AbilStore").DIR = Paths.get(os.path.join(base, "abilities"))
        P("AbilStore").SYNC = True
        br = JClass("java.util.concurrent.ConcurrentHashMap")()
        JClass("java.lang.System").getProperties().put("skyy.bridge", br)
        lv = {"Mage": 35, "Priest": 35}

        @JImplements("java.util.function.Function")
        class Level:
            @JOverride
            def apply(self, a):
                skill = str(a[1])
                return JInt(lv.get("now", 35))
        br.put("skill:fn:level", Level())
        # the two keys exactly as setup() puts them
        br.put("class:fn:loadoutGet", P("LoadoutGetFn")())
        br.put("class:fn:loadoutSet", P("LoadoutSetFn")())
        G, S = br.get("class:fn:loadoutGet"), br.get("class:fn:loadoutSet")
        UUID = JClass("java.util.UUID")
        u = UUID.fromString("00000000-0000-0000-0000-0000000000a1")

        def setfn(snap, who=None):
            a = JArray(JObject)(2)
            a[0] = who or u
            a[1] = snap
            return str(S.apply(a))

        def afile():
            p = os.path.join(base, "abilities", str(u) + ".properties")
            return open(p).read() if os.path.isfile(p) else None
        ck(G.apply(u) is None, "L no class -> loadoutGet null")
        ck(G.apply("x") is None and setfn("v=1;class=Mage", "x").startswith("-Bad arguments") and str(S.apply("x")) == "-Bad arguments.", "L bad arguments")
        br.put("profile:class:" + str(u), "Mage")
        g = str(G.apply(u))
        ck(g.startswith("v=1;class=Mage;alt=A;p1=Meteor;p2=ManaBarrier;a1=FrostNova;a2=Starfall;") and "n2=Mana Barrier" in g and "n3=Frost Nova" in g
           and g.endswith(";mods="), "L the Mage snapshot: %s" % g)
        saves0 = int(P("AbilStore").SAVES)
        r = setfn(g)
        ck(r.startswith("+Abilities: /cast 1 Meteor, /cast 2 Mana Barrier, alts Frost Nova and Starfall.") and int(P("AbilStore").SAVES) == saves0 and afile() is None,
           "L the same snapshot -> + and nothing written (%s)" % r)
        r = setfn(g.replace("p1=Meteor;p2=ManaBarrier", "p1=ManaBarrier;p2=Meteor"))
        ck(r.startswith("+Abilities: /cast 1 Mana Barrier, /cast 2 Meteor") and afile() is not None and "p1=ManaBarrier" in afile() and "p2=Meteor" in afile(),
           "L a re-order -> written (%s)" % r)
        ck("p1=ManaBarrier;p2=Meteor" in str(G.apply(u)), "L read back through loadoutGet")
        gB = g.replace("alt=A", "alt=B").replace("a2=Starfall", "a2=ArcaneBeam")
        r = setfn(gB)
        ck(r.startswith("+") and "alt=B" in afile() and "a2=ArcaneBeam" in str(G.apply(u)) and "p1=Meteor" in str(G.apply(u)), "L the A / B alt pick at level 35 (%s)" % r)
        lv["now"] = 15
        r = setfn(g)
        ck(r.startswith("=") and "Skipped: Starfall (choose it at" in r and "alt=B" in afile(), "L the alt pick below its unlock level -> skipped, B kept (%s)" % r)
        cur = str(G.apply(u))
        r = setfn(cur.replace("a1=FrostNova;a2=ArcaneBeam", "a1=ArcaneBeam;a2=FrostNova"))
        ck(r.startswith("=") and "the slot order (Arcane Beam is still locked)" in r or "is still locked" in r, "L a re-order that moves a locked ability -> skipped (%s)" % r)
        lv["now"] = 35
        before = afile()
        r = setfn(g.replace("class=Mage", "class=Priest"))
        ck(r.startswith("-These abilities are for a Priest - you are a Mage") and afile() == before, "L a wrong class -> - and nothing written (%s)" % r)
        r = setfn("hello")
        ck(r.startswith("-Not an ability loadout"), "L a bad snapshot (%s)" % r)
        r = setfn(cur.replace("mods=", "mods=Meteor:Echo+Split"))
        ck(r.startswith("=") and "modifiers Meteor:Echo+Split (modifiers are not in the game yet)" in r, "L modifiers -> skipped, listed (%s)" % r)
        # an unreadable ability file (a folder in its place) -> "-", never written
        u2 = UUID.fromString("00000000-0000-0000-0000-0000000000a2")
        br.put("profile:class:" + str(u2), "Priest")
        os.makedirs(os.path.join(base, "abilities", str(u2) + ".properties"))
        gp = str(G.apply(u2))
        ck(gp.startswith("v=1;class=Priest;alt=A;p1=SacredHeal;p2=ShieldBubble;"), "L the Priest snapshot (defaults while the file cannot be read): %s" % gp)
        r = setfn(gp.replace("p1=SacredHeal;p2=ShieldBubble", "p1=ShieldBubble;p2=SacredHeal"), u2)
        ck(r.startswith("-Your ability file could not be read") and os.path.isdir(os.path.join(base, "abilities", str(u2) + ".properties")), "L an unreadable ability file: - and never written (%s)" % r)
        ck(int(P("AbilLoadout").GETS) >= 6 and int(P("AbilLoadout").SETS) >= 6, "L counters")
    except Exception:
        import traceback
        R["checks"].append([False, "L crashed: " + traceback.format_exc()[-3000:]])
    json.dump(R, open(out, "w"), indent=1)
    os._exit(0)


# ============================================================================================================ child: CC
def run_cc(out):
    import jpype
    from jpype import JClass
    jpype.startJVM(B._jvm(), "-XX:-UsePerfData", classpath=[B.JAVASSIST], convertStrings=True)
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def text(m):
        mi = m.getMethodInfo()
        ca = mi.getCodeAttribute()
        if ca is None:
            return ""
        it, pool, lines = ca.iterator(), mi.getConstPool(), []
        while it.hasNext():
            lines.append(str(IP.instructionString(it, it.next(), pool)))
        t = "\n".join(lines)
        t = re.sub(r"#\d+ = ", "", t).replace("ldc_w ", "ldc ")
        t = re.sub(r"(?m)^((?:goto|goto_w|if\w*|jsr|tableswitch|lookupswitch)\b).*$", r"\1 L", t)
        return t.replace(VERSION, "V").replace(PREV_VERSION, "V")
    res = {}
    for tag, jp in (("new", JAR), ("prev", PREV_JAR)):
        cp = JClass("javassist.ClassPool")(False)
        cp.appendSystemPath()
        cp.appendClassPath(B.SERVER_JAR)
        cp.appendClassPath(jp)
        d = {}
        for n in [x[:-6].replace("/", ".") for x in zipfile.ZipFile(jp).namelist() if x.endswith(".class")]:
            cc = cp.get(n)
            ms = {}
            for m in list(cc.getDeclaredMethods()):
                ms["%s%s" % (m.getName(), m.getSignature())] = text(m)
            for c in list(cc.getDeclaredConstructors()):
                ms["<init>%s" % c.getSignature()] = text(c)
            ci = cc.getClassInitializer()
            if ci is not None:
                ms["<clinit>"] = text(ci)
            d[n.rsplit(".", 1)[-1]] = {"m": ms, "f": sorted("%s:%s" % (f.getName(), f.getSignature()) for f in cc.getDeclaredFields())}
        res[tag] = d
    N, Pv = res["new"], res["prev"]
    diff = {"added": sorted(set(N) - set(Pv)), "gone": sorted(set(Pv) - set(N)), "changed": {}}
    for c in sorted(set(N) & set(Pv)):
        a, b = Pv[c]["m"], N[c]["m"]
        ch = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
        if ch or N[c]["f"] != Pv[c]["f"]:
            diff["changed"][c] = ch + (["fields"] if N[c]["f"] != Pv[c]["f"] else [])
    json.dump(diff, open(out, "w"), indent=1)
    os._exit(0)


# ============================================================================================================ child: ST
def run_s(home, step, out):
    from jpype import JClass
    jvm([B.SERVER_JAR, JAR])
    Cfg, Pub, AS = JClass(PKG + "ClassCfg"), JClass(PKG + "CfgPub"), JClass(PKG + "AbilStore")
    Paths = JClass("java.nio.file.Paths")
    base = os.path.join(home, "Skyy_SkyyClasses")
    Cfg.FILE = Paths.get(os.path.join(base, "config.properties"))
    o = {"mig": str(Cfg.migrate0110()), "load": str(Cfg.load())}
    AS.DIR = Paths.get(os.path.join(base, "abilities"))
    Pub.start(Paths.get(home), None)
    Pub.flush()
    Pub.shutdown()
    json.dump(o, open(out, "w"))
    os._exit(0)


def child(env, *args):
    return subprocess.run([sys.executable, os.path.abspath(__file__)] + list(args) + ["--dir", SCRATCH], env=env)


def main():
    if "--l" in sys.argv:
        run_l(arg("--out"))
    if "--cc" in sys.argv:
        run_cc(arg("--out"))
    if "--s" in sys.argv:
        run_s(arg("--home"), arg("--step"), arg("--out"))
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(SCRATCH)
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp)
    env = dict(os.environ, TEMP=tmp, TMP=tmp)
    o = os.path.join(SCRATCH, "L.json")
    child(env, "--l", "--out", o)
    if os.path.isfile(o):
        for c, w in json.load(open(o))["checks"]:
            check(c, w)
    else:
        check(False, "L wrote no result")
    o = os.path.join(SCRATCH, "CC.json")
    child(env, "--cc", "--out", o)
    if os.path.isfile(o):
        d = json.load(open(o))
        check(d["added"] == ["AbilLoadout", "LoadoutGetFn", "LoadoutSetFn"] and d["gone"] == [], "CC added %s, gone %s" % (d["added"], d["gone"]))
        structural = dict((c, m) for c, m in d["changed"].items())
        check(list(structural) == ["SkyyClassesPlugin"] and structural["SkyyClassesPlugin"] == ["setup()V"],
              "CC the only change elsewhere: SkyyClassesPlugin.setup (%s)" % structural)
    else:
        check(False, "CC wrote no result")
    if os.path.isdir(LIVE):
        home = os.path.join(SCRATCH, "live")
        shutil.copytree(LIVE, os.path.join(home, "Skyy_SkyyClasses"))
        before = tree_hash(home)
        for step in ("1", "2"):
            child(env, "--s", "--home", home, "--step", step, "--out", os.path.join(SCRATCH, "s%s.json" % step))
            after = tree_hash(home)
            ch = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
            check(not ch, "ST start %s on a live copy writes nothing (%s)" % (step, ch))
    else:
        check(False, "ST the live Skyy_SkyyClasses folder is missing")
    print("%d checks passed, %d failed" % (OKS[0], len(FAILS)))
    for f in FAILS:
        print("  FAIL", f)
    if "--keep" not in sys.argv:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
