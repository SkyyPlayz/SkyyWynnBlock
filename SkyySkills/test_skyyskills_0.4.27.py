"""SkyySkills 0.4.27 - bare-JVM harness for THE MONK SKILL IS "ZEN" (tools/skills_0_4_27_patch.py; Skyy LOCKED 2026-10-08). Every child JVM
runs the game's own JRE with HytaleServer.jar on the class path, -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in the scratch
folder; each mod jar gets its own class loader (like separate plugins) and they share the one skyy.bridge map. The live save data is only
ever READ and copied into scratch (checked: the live folders' bytes are the same afterwards).

    python SkyySkills/test_skyyskills_0.4.27.py --dir <empty folder inside tools/dev/scratch/> [--keep]
         [--jar SkyySkills-0.4.27.jar] [--prev SkyySkills-0.4.26.jar] [--live <Skyy_SkyySkills folder>] [--no-cf]

SECTIONS
  A   every class of both jars loads, verifies (-Xverify:all) and initialises
  CC  CLASS COMPARE 0.4.26 -> 0.4.27, every method + constructor + static initialiser as javassist instruction text: no class / method /
      field added or removed; a changed method differs ONLY in string constants ("Zen" for "Discipline", "zen" for "discipline", the
      version); the structural changes = SkillDefs.<clinit> (ALIAS_FROM / ALIAS_TO one entry longer: "discipline" -> the Monk) and
      SkillDefs.indexOf (fixer 2: a 3+ letter prefix of the old label "discipline" -> the Monk, after every label / class prefix)
  JT  the jar texts: "discipline" (any case) only in SkillDefs (the alias); "Zen" in SkillDefs + the help / usage texts; manifest =
      0.4.26's but Version / Name / Description (Zen); every non-class file byte-identical
  ZN  EXECUTED on a scratch COPY of Skyy's live Skyy_SkyySkills (both jars): SkillDefs.LABELS / NAMES (slot 8 = Zen, saved key
      Combat.Shaman), indexOf for Zen / zen / Discipline / discipline / Shaman / Combat.Shaman / combat / Monk and the old-label prefixes
      dis / disc / DISCIP / disciplin (= 0.4.26's), the REAL skill:fn:level
      (SkillFn.apply) on Skyy's Monk profile (d8dd...-p6: Combat.Shaman=58) and on a synthetic Monk at level 30 by every name - the
      same XP and level as 0.4.26; levelsOf (skill:<uuid> = "...,Zen:30"), SkillMsg ("+123 Zen XP"), SkillClass.skillName; no player
      file written by any read
  ST  START TWICE on a scratch COPY of the live data (the 0.4.26 harness's start routine: every one-time migration, SkillCfg.load,
      ClassCurve / OwnCurve): 0.4.27 changes exactly what 0.4.26 changes, start 2 changes nothing, player files untouched
  MX  MIXED PARTNERS in ONE JVM (shared bridge): SkyySkills 0.4.26 / 0.4.27 x SkyyClasses 0.1.14 / 0.1.15 (the REAL ClassStore.publishKey
      -> class:skill) x SkyyTrees 0.3.4 / 0.3.5 (the REAL TreeClass.level) x SkyyProfiles 0.1.7 / 0.1.8 (the REAL ProfRoster.roster with
      class:list) + SkyyHud 0.3.17 (the REAL Widgets.skillVal of its class line) + the SkyyMobs / SkyyGear path (skill:fn:level asked
      with class:skill). Expected: the new set works everywhere; old Classes + new Skills works (Hud's class line "-" until Classes
      moves); NEW Classes + OLD Skills = level 0 for class:skill lookups (SkyyMobs / SkyyGear) = the STOP rule (deploy together)
  CF  CARRY-FORWARD: the 0.4.26 harness run on the 0.4.27 jar next to its control run on the 0.4.26 jar (prev 0.4.25 both): every check
      that passes for 0.4.26 passes for 0.4.27 except the two expected text checks (J: the manifest Description names Zen; F: its
      0.4.25 compare lists the classes holding the Zen texts) - the Fortune / skill:dmg / start-twice / access-audit checks all pass
"""
import os, sys, re, json, shutil, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, PREV_VERSION = "0.4.27", "0.4.26"
PKG = "com.skyy.skills."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "zen01", "skills0427")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
PREV_JAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyySkills-%s.jar" % PREV_VERSION)))
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
MODS_LIVE = os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods")
LIVE_DIR = os.path.abspath(arg("--live", os.path.join(MODS_LIVE, "Skyy_SkyySkills")))
MONK_U = "d8ddde89-98b2-4739-983e-a39773d582b6"          # Skyy's UUID; profile 6 (key <uuid>-p6) is the Monk profile (Combat.Shaman=58)
MONK_K = MONK_U + "-p6"
SYN_U = "00000000-0000-0000-0000-0000000005e1"            # a synthetic Monk at class level 30 (no profiles)
PARTNERS = {"S26": "SkyySkills/SkyySkills-0.4.26.jar", "S27": "SkyySkills/SkyySkills-0.4.27.jar",
            "C14": "SkyyClasses/SkyyClasses-0.1.14.jar", "C15": "SkyyClasses/SkyyClasses-0.1.15.jar",
            "T34": "SkyyTrees/SkyyTrees-0.3.4.jar", "T35": "SkyyTrees/SkyyTrees-0.3.5.jar",
            "P17": "SkyyProfiles/SkyyProfiles-0.1.7.jar", "P18": "SkyyProfiles/SkyyProfiles-0.1.8.jar",
            "H317": "SkyyHud/SkyyHud-0.3.17.jar"}
FAILS, OKS = [], [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def tmod(fn, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.SCRATCH = SCRATCH
    return m


# ============================================================================================ shared JVM helpers (children)
def jvm_start(extra=()):
    import jpype
    import skyybuild as B
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")   # the game's own JRE
    if not os.path.exists(jvm):
        jvm = B._jvm()
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR, B.JAVASSIST] + list(extra), convertStrings=True)


def loader(jar):
    from jpype import JClass, JArray
    URL, URLCL, File = JClass("java.net.URL"), JClass("java.net.URLClassLoader"), JClass("java.io.File")
    urls = JArray(URL)(1)
    urls[0] = File(jar).toURI().toURL()
    return URLCL(urls, JClass("java.lang.ClassLoader").getSystemClassLoader())


def load_all(jar, ld):
    """every class of the jar loaded + linked + initialised in its own loader -> (count, fails)"""
    from jpype import JClass
    Cls = JClass("java.lang.Class")
    names = [n[:-6].replace("/", ".") for n in zipfile.ZipFile(jar).namelist() if n.endswith(".class")]
    fails = []
    for n in names:
        try:
            c = Cls.forName(n, True, ld)
            c.getDeclaredMethods()
            c.getDeclaredFields()
        except Exception as e:
            fails.append("%s: %s" % (n, str(e)[:200]))
    return len(names), fails


def jpath(p):
    from jpype import JClass
    return JClass("java.nio.file.Paths").get(p, JClass("java.lang.reflect.Array").newInstance(JClass("java.lang.String").class_, 0))


def snap(d):
    return dict((os.path.relpath(os.path.join(r, f), d).replace(os.sep, "/"), open(os.path.join(r, f), "rb").read())
                for r, _ds, fs in os.walk(d) for f in fs)


# ============================================================================================ child: CC (class compare, javassist text)
def run_cc(jar, prev, out, repl):
    """repl = [[regex, replacement], ...] applied to the NEW method texts (and the version to both) -> per class the methods whose texts
    still differ (structural) and those that differ only in their constants"""
    import jpype
    from jpype import JClass
    import skyybuild as B
    jpype.startJVM(B._jvm(), "-XX:-UsePerfData", classpath=[B.JAVASSIST], convertStrings=True)
    IP, PS, BOS = JClass("javassist.bytecode.InstructionPrinter"), JClass("java.io.PrintStream"), JClass("java.io.ByteArrayOutputStream")
    vers = json.loads(repl)["versions"]
    rules = json.loads(repl)["rules"]

    def text(m):
        mi = m.getMethodInfo()
        ca = mi.getCodeAttribute()
        if ca is None:
            return ""
        it, pool, lines = ca.iterator(), mi.getConstPool(), []
        while it.hasNext():
            lines.append(str(IP.instructionString(it, it.next(), pool)))
        t = "\n".join(lines)
        t = re.sub(r"#\d+ = ", "", t)
        t = t.replace("ldc_w ", "ldc ")
        t = re.sub(r"(?m)^((?:goto|goto_w|if\w*|jsr|tableswitch|lookupswitch)\b).*$", r"\1 L", t)
        for v in vers:
            t = t.replace(v, "V")
        return t

    res = {}
    for tag, jp in (("new", jar), ("prev", prev)):
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
            d[n.rsplit(".", 1)[-1]] = {"m": ms, "f": sorted("%s:%s" % (f.getName(), f.getSignature()) for f in cc.getDeclaredFields()),
                                       "sup": str(cc.getClassFile().getSuperclass()), "if": sorted(str(x) for x in cc.getClassFile().getInterfaces())}
        res[tag] = d
    N, P = res["new"], res["prev"]
    diff = {"added": sorted(set(N) - set(P)), "gone": sorted(set(P) - set(N)), "classes": {}}
    for c in sorted(set(N) & set(P)):
        a, b = P[c]["m"], N[c]["m"]
        ch = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
        if not ch and N[c]["f"] == P[c]["f"]:
            continue
        const_only, structural = [], []
        for k in ch:
            if k not in a or k not in b:
                structural.append(k + (" (new)" if k in b else " (gone)"))
                continue
            t = b[k]
            for rx, rp in rules:
                t = re.sub(rx, rp, t)
            (const_only if t == a[k] else structural).append(k)
        diff["classes"][c] = {"const_only": const_only, "structural": structural,
                              "fields_new": sorted(set(N[c]["f"]) - set(P[c]["f"])), "fields_gone": sorted(set(P[c]["f"]) - set(N[c]["f"])),
                              "same_shape": N[c]["sup"] == P[c]["sup"] and N[c]["if"] == P[c]["if"]}
    json.dump(diff, open(out, "w"), indent=1)


# ============================================================================================ child: ZN (one Skills jar, a live copy)
def run_zn(jar, home, out):
    from jpype import JClass, JArray, JImplements, JOverride, JLong
    jvm_start()
    R = {}
    ld = loader(jar)
    R["classes"], R["load_fails"] = load_all(jar, ld)
    C = lambda n: JClass(PKG + n, loader=ld)
    Obj, UUID = JClass("java.lang.Object"), JClass("java.util.UUID")
    try:
        Defs, Store, Fn, Msg, SCl = C("SkillDefs"), C("SkillStore"), C("SkillFn"), C("SkillMsg"), C("SkillClass")
        R["labels"] = [str(x) for x in Defs.LABELS]
        R["names"] = [str(x) for x in Defs.NAMES]
        R["classes_"] = [str(x) for x in Defs.CLASSES]
        R["alias"] = [str(x) for x in Defs.ALIAS_FROM]
        R["idx"] = dict((s, int(Defs.indexOf(s))) for s in ["Zen", "zen", " ZEN ", "Discipline", "discipline", " DISCIPLINE", "Shaman", "shaman skill",
                                                               "Combat.Shaman", "Monk", "Archery", "Divinity", "zenith", "dis", "zen x",
                                                               "disc", "DISCIP", "disciplin", "di", "sha", "shamanx", "disciplines"])
        R["canon"] = [str(Defs.canonName(s)) for s in ("Shaman", "Discipline", "Monk", "Zen")]
        Cfg = C("SkillCfg")
        Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
        Cfg.FILE = jpath(os.path.join(home, "xp.properties"))
        R["cfg"] = str(Cfg.load())
        cum = [int(x) for x in Defs.ECUM]
        players = os.path.join(home, "players")
        open(os.path.join(players, SYN_U + ".properties"), "wb").write(("name=Syn\nCombat.Shaman=%d\nCombat.Shaman.paid=30\n" % (cum[30] + 5)).encode("latin-1"))
        s0 = snap(players)
        Store.DIR = jpath(players)
        Store.DATA.clear()
        br = Store.bridge()

        @JImplements("java.util.function.Function")
        class KeyFn(object):
            @JOverride
            def apply(self, o):
                return MONK_K if str(o) == MONK_U else str(o)
        br.put("profile:fn:key", KeyFn())
        fn = Fn()
        lv = {}
        for tag, us in (("live", MONK_U), ("syn", SYN_U)):
            u = UUID.fromString(us)
            br.put("class:" + us, "Monk")
            lv[tag] = {"xp": int(Store.data(u)[8]),
                       "by": dict((n, int(fn.apply(JArray(Obj)([u, n])))) for n in ["Zen", "zen", "Discipline", "discipline", "Combat.Shaman", "combat", "Monk", "Shaman"]),
                       "levelsOf": str(Store.levelsOf(u, Store.data(u)))}
            br.remove("class:skill:" + us)
            lv[tag]["name_plain"] = str(SCl.skillName(u, 8))
            for cs in ("Zen", "Discipline"):
                br.put("class:skill:" + us, cs)
                lv[tag]["name_" + cs] = str(SCl.skillName(u, 8))
            br.remove("class:skill:" + us)
            br.remove("class:" + us)
        R["lv"] = lv
        u2 = UUID.fromString(SYN_U)
        arr = JArray(JClass("long"))(len(R["labels"]))
        arr[8] = 123
        Msg.PEND.put(u2, arr)
        R["msg"] = str(Msg.take(u2))
        Store.DATA.clear()
        s1 = snap(players)
        R["players_unchanged"] = s0 == s1
    except Exception:
        import traceback
        R["error"] = traceback.format_exc()[-3000:]
    json.dump(R, open(out, "w"), indent=1)
    os._exit(0)


# ============================================================================================ child: MX (the mixed partner matrix)
def run_mx(home, out):
    """home = a scratch copy of the live Skyy_SkyySkills (+ the synthetic Monk at level 30)"""
    from jpype import JClass, JArray, JImplements, JOverride
    jvm_start()
    R = {"load": {}}
    L = {}
    for k, rel in PARTNERS.items():
        p = os.path.join(ROOT, rel)
        L[k] = loader(p)
        R["load"][k] = load_all(p, L[k])[1][:3]
    Obj, UUID = JClass("java.lang.Object"), JClass("java.util.UUID")
    C = lambda k, n: JClass(n, loader=L[k])
    us = SYN_U
    u = UUID.fromString(us)
    R["rows"] = []
    try:
        for sk in ("S26", "S27"):
            Cfg = C(sk, PKG + "SkillCfg")
            Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
            Cfg.FILE = jpath(os.path.join(home, "xp.properties"))
            Cfg.load()
            St = C(sk, PKG + "SkillStore")
            St.DIR = jpath(os.path.join(home, "players"))
            St.DATA.clear()
        syn = os.path.join(home, "players", SYN_U + ".properties")
        if not os.path.isfile(syn):     # the synthetic Monk at class level 30 (the class table SkillCfg.load just built)
            cum = [int(x) for x in C("S27", PKG + "SkillDefs").ECUM]
            open(syn, "wb").write(("name=Syn\nCombat.Shaman=%d\nCombat.Shaman.paid=30\n" % (cum[30] + 5)).encode("latin-1"))
        br = C("S27", PKG + "SkillStore").bridge()
        br.put("profile:class:" + us, "Monk")
        br.put("class:" + us, "Monk")
        Wid = C("H317", "com.skyy.hud.Widgets")
        for sk in ("S26", "S27"):
            fn = C(sk, PKG + "SkillFn")()
            br.put("skill:fn:level", fn)
            St = C(sk, PKG + "SkillStore")
            for cl in ("C14", "C15"):
                Cs = C(cl, "com.skyy.classes.ClassStore")
                Cs.publishKey(u, us)
                cs = str(br.get("class:skill:" + us))
                lst = str(C(cl, "com.skyy.classes.ClassDefs").listText())
                br.put("class:list", lst)
                row = {"skills": sk, "classes": cl, "class_skill": cs, "class": str(br.get("class:" + us))}
                row["mobs_gear_level"] = int(fn.apply(JArray(Obj)([u, cs])))       # SkyyMobs / SkyyGear: skill:fn:level(uuid, class:skill)
                St.publishNow(u, True)
                lv = str(br.get("skill:" + us))
                row["skill_string"] = lv
                row["hud_class_line"] = [cs, str(Wid.skillVal(Wid.splitc(lv, ","), cs))]
                row["skills_page_name"] = str(C(sk, PKG + "SkillClass").skillName(u, 8))
                for tr in ("T34", "T35"):
                    row["trees_level_" + tr] = int(C(tr, "com.skyy.trees.TreeClass").level(u, 6))
                for pr in ("P17", "P18"):
                    ent = [list(map(str, e)) for e in C(pr, "com.skyy.profiles.ProfRoster").roster() if str(e[0]) == "Monk"]
                    row["profiles_card_" + pr] = ent[0][1] if ent else None
                R["rows"].append(row)
        br.remove("class:list")
        for pr in ("P17", "P18"):
            ent = [list(map(str, e)) for e in C(pr, "com.skyy.profiles.ProfRoster").roster() if str(e[0]) == "Monk"]
            R["profiles_fallback_" + pr] = ent[0][1] if ent else None
    except Exception:
        import traceback
        R["error"] = traceback.format_exc()[-3000:]
    json.dump(R, open(out, "w"), indent=1)
    os._exit(0)


# ============================================================================================ child: ST (the 0.4.26 harness's start routine)
def run_st(jar, out, mode):
    m = tmod("test_skyyskills_0.4.26.py", "t0426")
    m.run_start(jar, out, mode)
    os._exit(0)


# ============================================================================================ parent
def jar_texts(jar):
    z = zipfile.ZipFile(jar)
    out = {}
    for n in z.namelist():
        d = z.read(n)
        out[n] = (len(re.findall(rb"(?i)discipline", d)), len(re.findall(rb"(?i)(?<![a-z])zen(?![a-z])", d)))
    return out


def carry_forward(env):
    """the 0.4.26 harness on the new jar and on the 0.4.26 jar (control); its scratch rule wants tools/dev/scratch/tools01fix2 under its
    TOOLS - a TOOLS inside OUR scratch folder is handed to it (nothing is written outside this harness's scratch)"""
    wrap = os.path.join(SCRATCH, "cf_wrap.py")
    open(wrap, "w").write(
        "import sys, os, importlib.util\n"
        "here, jar, prev, scratch = sys.argv[1:5]\n"
        "sys.argv = [sys.argv[0], '--dir', scratch, '--jar', jar, '--prev', prev]\n"
        "spec = importlib.util.spec_from_file_location('t0426', os.path.join(here, 'test_skyyskills_0.4.26.py'))\n"
        "m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)\n"
        "m.TOOLS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(scratch))))\n"
        "m.main()\n")
    ft = os.path.join(SCRATCH, "cf", "dev", "scratch", "tools01fix2")
    os.makedirs(ft, exist_ok=True)
    res = {}
    for tag, j in (("new", JAR), ("ctl", PREV_JAR)):
        p = subprocess.run([sys.executable, wrap, HERE, j, os.path.join(HERE, "SkyySkills-0.4.25.jar"), os.path.join(ft, tag)], env=env,
                           capture_output=True, encoding="utf8", errors="replace")
        t = p.stdout or ""
        m = re.search(r"SkyySkills 0\.4\.26 harness: (\d+) ok, (\d+) fail", t)
        res[tag] = (int(m.group(1)) if m else -1, [ln[len("FAIL: "):] for ln in t.splitlines() if ln.startswith("FAIL: ")])
    (okn, fn_), (okc, fc_) = res["new"], res["ctl"]
    extra = [f for f in fn_ if f not in fc_]
    allowed = [f for f in extra if (f.startswith("J: the asset files = 0.4.25's") and "changed []" in f and "added []" in f)
               or (f.startswith("F: class compare 0.4.25 -> 0.4.26: added [], gone []"))]
    check(okc > 30 and not fc_, "CF: the 0.4.26 harness passes on the 0.4.26 jar (control): %d ok, fails %s" % (okc, fc_))
    check(okn > 30 and extra == allowed and len(extra) == 2 and okn + len(fn_) == okc + len(fc_),
          "CF: on the 0.4.27 jar every 0.4.26 check passes but the 2 expected text ones (manifest Description; the 0.4.25 compare names the "
          "Zen-text classes): %d ok, extra fails %s" % (okn, [f[:160] for f in extra if f not in allowed]))
    for f in extra:
        print("CF expected: " + f[:220])


def main():
    if "--cc" in sys.argv:
        return run_cc(arg("--cc"), arg("--prevjar"), arg("--out"), arg("--repl"))
    if "--zn" in sys.argv:
        return run_zn(arg("--zn"), arg("--home"), arg("--out"))
    if "--mx" in sys.argv:
        return run_mx(arg("--home"), arg("--out"))
    if "--st" in sys.argv:
        return run_st(arg("--st"), arg("--out"), arg("--mode"))
    for j in [JAR, PREV_JAR] + [os.path.join(ROOT, p) for p in PARTNERS.values()]:
        if not os.path.isfile(j):
            sys.exit("no jar at %s - build it first" % j)
    sroot = os.path.realpath(os.path.join(TOOLS, "dev", "scratch"))
    if not os.path.realpath(SCRATCH).startswith(sroot + os.sep):
        sys.exit("--dir must be inside tools/dev/scratch/ (deleted afterwards): %s" % SCRATCH)
    if os.path.exists(SCRATCH) and os.listdir(SCRATCH):
        sys.exit("%s is not empty - pass an empty --dir" % SCRATCH)
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.makedirs(env["TEMP"], exist_ok=True)
    live_before = snap(LIVE_DIR)
    me = os.path.abspath(__file__)

    def child(args_, out_):
        with open(out_ + ".log", "wb") as lf:
            p = subprocess.run([sys.executable, me] + args_ + ["--out", out_, "--dir", SCRATCH], env=env, stdout=lf, stderr=subprocess.STDOUT)
        ok = os.path.isfile(out_)
        if not ok:
            print(open(out_ + ".log", encoding="utf8", errors="replace").read()[-3000:])
        return json.load(open(out_)) if ok else None
    try:
        # ---- CC
        rules = [[r'"Zen"', '"Discipline"'], [r'\bzen\b', "discipline"], [r'\bZen\b', "Discipline"]]
        cc = child(["--cc", JAR, "--prevjar", PREV_JAR, "--repl", json.dumps({"versions": [VERSION, PREV_VERSION], "rules": rules})],
                   os.path.join(SCRATCH, "cc.json"))
        check(cc is not None, "CC: the compare child ran")
        if cc:
            cls_ = cc["classes"]
            struct = dict((c, v["structural"]) for c, v in cls_.items() if v["structural"])
            check(not cc["added"] and not cc["gone"] and all(v["same_shape"] and not v["fields_new"] and not v["fields_gone"] for v in cls_.values()),
                  "CC: no class / field added or removed, same supers: %s %s" % (cc["added"], cc["gone"]))
            check(struct == {"SkillDefs": ["<clinit>", "indexOf(Ljava/lang/String;)I"]},
                  "CC: the only structural changes = SkillDefs.<clinit> (the alias arrays) + indexOf (old-label prefix, fixer 2): %s" % struct)
            print("CC. 0.4.26 -> 0.4.27 changed (constants only unless noted): " + "; ".join(
                "%s %s" % (c, [m.split("(")[0] for m in v["const_only"] + v["structural"]]) for c, v in sorted(cls_.items())))
        # ---- JT
        tn, tp = jar_texts(JAR), jar_texts(PREV_JAR)
        dn = sorted(n for n, (d, z) in tn.items() if d)
        check(dn == ["com/skyy/skills/SkillDefs.class"], "JT: 'discipline' (any case) is left only in SkillDefs (the alias): %s" % dn)
        zn = sorted(n.split("/")[-1] for n, (d, z) in tn.items() if z)
        check(set(n.split("/")[-1] for n, (d, z) in tp.items() if d) - {"SkillDefs.class"} <= set(zn) and "manifest.json" in zn,
              "JT: every file that named Discipline names Zen now: %s" % zn)
        zj, zp = zipfile.ZipFile(JAR), zipfile.ZipFile(PREV_JAR)
        nn = set(n for n in zj.namelist() if not n.endswith(".class"))
        check(nn == set(n for n in zp.namelist() if not n.endswith(".class")) and
              all(zj.read(n) == zp.read(n) for n in nn if n != "manifest.json"), "JT: every asset file byte-identical to 0.4.26's")
        mn, mp = json.loads(zj.read("manifest.json")), json.loads(zp.read("manifest.json"))
        check(sorted(k for k in set(mn) | set(mp) if mn.get(k) != mp.get(k)) == ["Description", "Name", "Version"]
              and mn["Description"] == mp["Description"].replace("Assassination, Discipline)", "Assassination, Zen)")
              and mn["Name"] == mp["Name"].replace(PREV_VERSION, VERSION),
              "JT: manifest = 0.4.26's but the version (Version, Name) and 'Zen' in the description")
        # ---- ZN
        zr = {}
        for tag, j in (("new", JAR), ("prev", PREV_JAR)):
            h = os.path.join(SCRATCH, "zn-" + tag)
            shutil.copytree(LIVE_DIR, h)
            zr[tag] = child(["--zn", j, "--home", h], os.path.join(SCRATCH, "zn-%s.json" % tag))
            r = zr[tag]
            check(r is not None and "error" not in r, "ZN (%s) ran: %s" % (tag, (r or {}).get("error", "")[-1500:]))
            if r:
                check(not r["load_fails"] and r["classes"] > 100, "A (%s): %d classes load, verify (-Xverify:all) and initialise %s" % (tag, r["classes"], r["load_fails"][:3]))
        n, o = zr.get("new") or {}, zr.get("prev") or {}
        if "error" not in n and "error" not in o and n and o:
            check(n["labels"][8] == "Zen" and o["labels"][8] == "Discipline" and n["names"] == o["names"] and n["names"][8] == "Combat.Shaman"
                  and [x for i, x in enumerate(n["labels"]) if i != 8] == [x for i, x in enumerate(o["labels"]) if i != 8],
                  "ZN: slot 8's label Discipline -> Zen, every saved key (NAMES) and every other label unchanged: %s" % n["labels"])
            check(n["alias"] == o["alias"] + ["discipline"] and n["classes_"] == o["classes_"], "ZN: 'discipline' appended to the aliases: %s" % n["alias"])
            want = dict(o["idx"])
            want.update({"Zen": 8, "zen": 8, " ZEN ": 8, "Discipline": 8, "discipline": 8, " DISCIPLINE": 8})
            # fixer 2: every 3+ letter prefix of the old label still opens the Monk slot exactly like 0.4.26 (dis / disc / DISCIP / disciplin);
            # "di" (too short), "sha", "shamanx", "disciplines" stay what 0.4.26 gave
            check(n["idx"] == want and o["idx"]["Discipline"] == 8 and o["idx"]["Zen"] == -1 and n["idx"]["zenith"] == -1
                  and all(n["idx"][k] == 8 == o["idx"][k] for k in ("dis", "disc", "DISCIP", "disciplin")) and n["idx"]["di"] == o["idx"]["di"],
                  "ZN: indexOf - Zen / Discipline / Shaman / Combat.Shaman / Monk -> slot 8 in 0.4.27 (0.4.26: Zen unknown): %s (0.4.26 %s)" % (n["idx"], o["idx"]))
            check(n["canon"] == ["Monk", "Monk", "Monk", "Zen"], "ZN: canonName Shaman / Discipline -> Monk: %s" % n["canon"])
            for t in ("live", "syn"):
                a, b = n["lv"][t], o["lv"][t]
                same = dict((k, v) for k, v in a["by"].items() if k not in ("Zen", "zen"))
                check(a["xp"] == b["xp"] and same == dict((k, v) for k, v in b["by"].items() if k not in ("Zen", "zen"))
                      and a["by"]["Zen"] == a["by"]["Discipline"] == b["by"]["Discipline"],
                      "ZN (%s Monk): the same saved XP %d and level by every old name; Zen = Discipline = %d: %s / 0.4.26 %s" % (
                          t, a["xp"], a["by"]["Discipline"], a["by"], b["by"]))
                check(a["levelsOf"] == b["levelsOf"].replace("Discipline:", "Zen:") and ("Zen:" in a["levelsOf"]),
                      "ZN (%s Monk): skill:<uuid> = 0.4.26's with Zen: %s" % (t, a["levelsOf"]))
                check(a["name_plain"] == "Zen" and a["name_Zen"] == "Zen" and a["name_Discipline"] == "Discipline" and b["name_plain"] == "Discipline",
                      "ZN (%s): skillName = class:skill when SkyyClasses publishes one, else the label Zen: %s" % (t, [a["name_plain"], a["name_Zen"], a["name_Discipline"]]))
            check(n["lv"]["live"]["xp"] == 58 and n["lv"]["syn"]["by"]["Zen"] == 30, "ZN: Skyy's live Monk profile keeps its 58 XP; the synthetic Monk is level 30: %s %s" % (
                n["lv"]["live"]["xp"], n["lv"]["syn"]["by"]))
            check(n["msg"] == "+123 Zen XP (" + n["msg"].split("(", 1)[1] and o["msg"].replace("Discipline", "Zen") == n["msg"],
                  "ZN: the XP chat line says Zen: %s" % n["msg"])
            check(n["players_unchanged"] and o["players_unchanged"], "ZN: no player file written by the reads (both jars)")
        # ---- ST
        sts = {}
        for mode, j in (("prev", PREV_JAR), ("new", JAR)):
            shutil.copytree(LIVE_DIR, os.path.join(SCRATCH, "live-copy-" + mode))
            sts[mode] = child(["--st", j, "--mode", mode], os.path.join(SCRATCH, "st-%s.json" % mode))
            check(sts[mode] is not None and "error" not in sts[mode], "ST (%s) ran: %s" % (mode, (sts[mode] or {}).get("error", "")[-800:]))
        if sts.get("new") and sts.get("prev") and "error" not in sts["new"] and "error" not in sts["prev"]:
            sn, sp = sts["new"], sts["prev"]
            check(sn["changed1"] == sp["changed1"] and sn["xp1"] == sp["xp1"] and sn["r1"] == sp["r1"],
                  "ST: start 1 of 0.4.27 changes exactly what 0.4.26's does (%s vs %s)" % (sn["changed1"], sp["changed1"]))
            check(sn["changed2"] == [] and sn["players_same"], "ST: start 2 changes nothing; player files untouched (%d files)" % sn["files"])
            print("ST. start twice on the live copy: start 1 changed %s (same as 0.4.26), start 2 nothing" % sn["changed1"])
        # ---- MX
        mh = os.path.join(SCRATCH, "mx-home")
        shutil.copytree(LIVE_DIR, mh)
        mx = child(["--mx", "--home", mh], os.path.join(SCRATCH, "mx.json"))
        check(mx is not None and "error" not in mx and not any(mx["load"].values()), "MX ran, every partner jar loads: %s %s" % (
            (mx or {}).get("error", "")[-1500:], (mx or {}).get("load")))
        if mx and "error" not in mx:
            rows = dict(((r["skills"], r["classes"]), r) for r in mx["rows"])
            for k, r in sorted(rows.items()):
                print("MX %s+%s: class:skill %s, Mobs/Gear level %d, Hud %s, /skills title %s, Trees %d/%d, Profiles card %s/%s" % (
                    k[0], k[1], r["class_skill"], r["mobs_gear_level"], r["hud_class_line"], r["skills_page_name"], r["trees_level_T34"],
                    r["trees_level_T35"], r["profiles_card_P17"], r["profiles_card_P18"]))
            new, base = rows[("S27", "C15")], rows[("S26", "C14")]
            check(new["class_skill"] == "Zen" and new["mobs_gear_level"] == 30 and new["hud_class_line"] == ["Zen", "30"] and new["skills_page_name"] == "Zen"
                  and new["trees_level_T34"] == new["trees_level_T35"] == 30 and new["profiles_card_P17"] == new["profiles_card_P18"] == "Zen"
                  and "Zen:30" in new["skill_string"],
                  "MX: THE NEW SET (Skills 0.4.27 + Classes 0.1.15): Zen everywhere, level 30 for Mobs / Gear, Hud, Trees 0.3.4 + 0.3.5: %s" % new)
            check(base["class_skill"] == "Discipline" and base["mobs_gear_level"] == 30 and base["hud_class_line"] == ["Discipline", "30"]
                  and base["trees_level_T34"] == base["trees_level_T35"] == 30, "MX: the live set (0.4.26 + 0.1.14) as today, Trees 0.3.5 works with it: %s" % base)
            oc = rows[("S27", "C14")]
            check(oc["class_skill"] == "Discipline" and oc["mobs_gear_level"] == 30 and oc["trees_level_T34"] == oc["trees_level_T35"] == 30
                  and oc["hud_class_line"] == ["Discipline", "-"],
                  "MX: Skills 0.4.27 + OLD Classes 0.1.14: levels work (alias); only SkyyHud's class line shows '-' (label Zen vs class:skill Discipline): %s" % oc)
            os_ = rows[("S26", "C15")]
            check(os_["class_skill"] == "Zen" and os_["mobs_gear_level"] == 0 and os_["trees_level_T34"] == os_["trees_level_T35"] == 30,
                  "MX: NEW Classes 0.1.15 + OLD Skills 0.4.26: class:skill lookups (SkyyMobs / SkyyGear) get 0 - the STOP rule (Classes 0.1.15 needs Skills 0.4.27): %s" % os_)
            check(mx["profiles_fallback_P17"] == "Discipline" and mx["profiles_fallback_P18"] == "Zen",
                  "MX: without SkyyClasses the Profiles fallback card: 0.1.7 Discipline, 0.1.8 Zen: %s %s" % (mx["profiles_fallback_P17"], mx["profiles_fallback_P18"]))
        # ---- CF
        if "--no-cf" not in sys.argv:
            carry_forward(env)
        check(snap(LIVE_DIR) == live_before, "the live Skyy_SkyySkills folder was never written (only read + copied)")
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyySkills %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
