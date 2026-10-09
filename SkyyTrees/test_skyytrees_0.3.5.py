"""SkyyTrees 0.3.5 - bare-JVM harness for THE MONK SKILL IS "ZEN" (tools/trees_0_3_5_patch.py; Skyy LOCKED 2026-10-08). Child JVMs run the
game's own JRE with HytaleServer.jar on the class path, -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in the scratch folder.
The live save data is only ever READ and copied into scratch (checked afterwards).

    python SkyyTrees/test_skyytrees_0.3.5.py --dir <empty folder inside tools/dev/scratch/> [--keep] [--no-cf]
         [--jar SkyyTrees-0.3.5.jar] [--prev SkyyTrees-0.3.4.jar] [--live <Skyy_SkyyTrees folder>]

SECTIONS
  A   every class of both jars loads, verifies (-Xverify:all) and initialises (own class loader each)
  CC  CLASS COMPARE 0.3.4 -> 0.3.5 (javassist text of every method, constructor, static initialiser): nothing added or removed but the
      field TreeClass.CSKILL_KEY; TreeClass.level() differs ONLY by reading CSKILL_KEY where 0.3.4 read CSKILL; every other change is a
      constant ("Zen" for "Discipline" - the texts and the fresh-file comment "# Monk (Zen)" - and the version); structural only
      TreeClass.<clinit> (the new array)
  JT  jar texts: "discipline" only in TreeClass (CSKILL_KEY, the skill:fn:level name); assets + manifest = 0.3.4's but the version
  ZN  EXECUTED (both jars, config loaded from a scratch copy of the live trees.properties): TreeClass.CSKILL / CSKILL_KEY; the REAL
      reasonText ("<node> needs Zen 5 (you are 3)"), TreeClassOps.armText (the respec price text) and note (the Ability Points help) for
      the Monk; every other class's texts identical to 0.3.4's
  ST  START TWICE on a scratch COPY of Skyy's live Skyy_SkyyTrees (the 0.3.4 harness's start routine: TreeCfg.load, TreeMig, TreeMig32,
      TreeMig33, CfgPub.start, a fresh loader per start): 0.3.5 changes exactly what 0.3.4 changes, the 2nd start nothing
  MX  the SkyySkills 0.4.27 harness's mixed-partner matrix: the REAL TreeClass.level of 0.3.4 AND 0.3.5 for a level-30 Monk = 30 with
      SkyySkills 0.4.26 and 0.4.27 and either SkyyClasses (0.3.5 asks with CSKILL_KEY "Discipline", which both Skills resolve)
  CF  CARRY-FORWARD: the 0.3.4 harness (+ its H33 = the 0.3.3 harness, 467,000+ checks incl. the class tree page states) on the 0.3.5 jar
      next to the control run on the 0.3.4 jar: the only new fails are its version-text checks and the page's Monk level label now
      reading 'Zen 30' / 'Zen 99' (it expected 'Discipline ...')
"""
import os, sys, re, json, shutil, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, PREV_VERSION = "0.3.5", "0.3.4"
PKG = "com.skyy.trees."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "zen01", "trees035")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)))
PREV_JAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyyTrees-%s.jar" % PREV_VERSION)))
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
MODS_LIVE = os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods")
LIVE = os.path.abspath(arg("--live", os.path.join(MODS_LIVE, "Skyy_SkyyTrees")))
SKILLS_HARNESS = os.path.join(ROOT, "SkyySkills", "test_skyyskills_0.4.27.py")
FAILS, OKS = [], [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def _mod(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    saved = list(sys.argv)
    sys.argv = [sys.argv[0], "--dir", SCRATCH]
    try:
        spec.loader.exec_module(m)
    finally:
        sys.argv = saved
    m.SCRATCH = SCRATCH
    return m


def sk():
    return _mod(SKILLS_HARNESS, "ts0427")


def t34():
    return _mod(os.path.join(HERE, "test_skyytrees_0.3.4.py"), "tt034")


def snap(d):
    return dict((os.path.relpath(os.path.join(r, f), d).replace(os.sep, "/"), open(os.path.join(r, f), "rb").read())
                for r, _ds, fs in os.walk(d) for f in fs) if os.path.isdir(d) else {}


# ============================================================================================ child: ZN (one jar)
def run_zn(jar, home, out):
    from jpype import JClass, JArray, JBoolean
    S = sk()
    S.jvm_start()
    ld = S.loader(jar)
    R = {}
    R["classes"], R["load_fails"] = S.load_all(jar, ld)
    C = lambda n: JClass(PKG + n, loader=ld)
    try:
        TC, Ops, Cfg = C("TreeClass"), C("TreeClassOps"), C("TreeCfg")
        Cfg.FILE = S.jpath(os.path.join(home, "trees.properties"))
        R["load"] = str(Cfg.load())
        R["cskill"] = [str(x) for x in TC.CSKILL]
        R["ckey"] = [str(x) for x in TC.CSKILL_KEY] if "CSKILL_KEY" in [str(f.getName()) for f in TC.class_.getDeclaredFields()] else None
        NN = int(TC.NN)
        nid = [str(x) for x in TC.NID]
        t1 = nid.index("T1")
        own, it = JArray(JBoolean)(NN * int(TC.NC)), JArray(JBoolean)(NN * int(TC.NC))
        R["texts"] = {}
        for ci in range(int(TC.NC)):
            R["texts"][str(TC.CLASSES[ci])] = [str(TC.reasonText(own, it, ci, t1, 3, 2, 7)), str(Ops.armText(ci, 30, False, False, 900)),
                                               str(Ops.note(ci, 30, it, 3, False, False, None))]
    except Exception:
        import traceback
        R["error"] = traceback.format_exc()[-3000:]
    json.dump(R, open(out, "w"), indent=1)
    os._exit(0)


# ============================================================================================ parent
def fails_of(text):
    out = set()
    for ln in text.splitlines():
        s = ln.strip()
        if s.startswith("FAILED: "):
            out.add(s[len("FAILED: "):])
        elif ln.startswith("FAIL "):
            out.add(ln[len("FAIL "):])
    return out


def carry_forward(env):
    res = {}
    for tag, j in (("new", JAR), ("ctl", PREV_JAR)):
        p = subprocess.run([sys.executable, os.path.join(HERE, "test_skyytrees_0.3.4.py"), "--jar", j, "--dir", os.path.join(SCRATCH, "cf-" + tag)],
                           env=env, capture_output=True, encoding="utf8", errors="replace")
        t = p.stdout or ""
        m = re.search(r"(\d+) passed", t)
        res[tag] = (t.count("\n"), fails_of(t), t)
    fn_, fc_ = res["new"][1], res["ctl"][1]
    extra = sorted(fn_ - fc_)
    VER = ["CfgFn", "CfgRows", "SkyyTreesPlugin", "TreeCfg", "TreeMig"]

    def expected(f):
        if f.startswith("F: changed classes differ ONLY in the version text"):
            return sorted(re.findall(r"com/skyy/trees/(\w+)\.class", f)) == sorted(VER + ["TreeClass"])
        if f == "F: com/skyy/trees/TreeClass.class: no method / field added or removed":
            return True     # CSKILL_KEY (the CC section proves it is the only one)
        if f == "J: manifest.json differs only in Version / Name (the version)":
            return True     # its check replaces 0.3.4 only; JT here proves the manifest = 0.3.4's but the version
        if f.startswith("H33: the 0.3.3 harness on the 0.3.4 jar:"):
            import ast
            items = ast.literal_eval(f.split("only its 2 jar-shape checks fail: ", 1)[1].split(" (shape:")[0])
            return items and all(i == "K1: 7 classes, their skills, magic flags" or re.match(r"K3 Monk .*: level label 'Zen \d+'$", i) for i in items)
        return False
    bad = [f for f in extra if not expected(f)]
    hc = re.search(r"H33: the 0\.3\.3 harness on the 0\.3\.4 jar: (\d+) passed", res["new"][2])
    check(not [f for f in fc_ if not f.startswith("H33")] , "CF: the 0.3.4 harness on the 0.3.4 jar (control) passes its own checks: %s" % sorted(fc_)[:3])
    check(not bad and len(extra) >= 3 and hc and int(hc.group(1)) > 400000,
          "CF: on the 0.3.5 jar only the expected version / Zen texts fail beyond the control (%s H33 checks): unexpected %s" % (
              hc.group(1) if hc else "?", [b[:240] for b in bad]))
    for f in extra:
        print("CF expected: " + f[:260])


def main():
    if "--zn" in sys.argv:
        return run_zn(arg("--zn"), arg("--home"), arg("--out"))
    if "--cc" in sys.argv:
        return sk().run_cc(arg("--cc"), arg("--prevjar"), arg("--out"), arg("--repl"))
    if "--st" in sys.argv:
        return t34().run_start(arg("--st"), arg("--fake"), arg("--live"), arg("--out"), arg("--tag"))
    if "--mkfake" in sys.argv:
        t34().t33().H.run_mkfake(arg("--mkfake"))
        return
    for j in (JAR, PREV_JAR):
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
    live_before = snap(LIVE)
    me = os.path.abspath(__file__)

    def child(args_, out_, script=None):
        with open(out_ + ".log", "wb") as lf:
            subprocess.run([sys.executable, script or me] + args_ + ["--out", out_, "--dir", SCRATCH], env=env, stdout=lf, stderr=subprocess.STDOUT)
        if not os.path.isfile(out_):
            print(open(out_ + ".log", encoding="utf8", errors="replace").read()[-3000:])
            return None
        return json.load(open(out_))
    try:
        # ---- CC
        rules = [[r'\bZen\b', "Discipline"], [r"CSKILL_KEY", "CSKILL"]]
        cc = child(["--cc", JAR, "--prevjar", PREV_JAR, "--repl", json.dumps({"versions": [VERSION, PREV_VERSION], "rules": rules})],
                   os.path.join(SCRATCH, "cc.json"))
        check(cc is not None, "CC: the compare child ran")
        if cc:
            cls_ = cc["classes"]
            struct = dict((c, v["structural"]) for c, v in cls_.items() if v["structural"])
            fnew = dict((c, v["fields_new"]) for c, v in cls_.items() if v["fields_new"] or v["fields_gone"])
            check(not cc["added"] and not cc["gone"] and fnew == {"TreeClass": ["CSKILL_KEY:[Ljava/lang/String;"]} and all(v["same_shape"] for v in cls_.values()),
                  "CC: nothing added or removed but the field TreeClass.CSKILL_KEY: %s %s %s" % (cc["added"], cc["gone"], fnew))
            check(struct == {"TreeClass": ["<clinit>"]}, "CC: the only structural change = TreeClass.<clinit> (the CSKILL_KEY array): %s" % struct)
            lv = [m for m in cls_.get("TreeClass", {}).get("const_only", []) if m.startswith("level(")]
            check(lv == ["level(Ljava/util/UUID;I)I"], "CC: TreeClass.level reads CSKILL_KEY where 0.3.4 read CSKILL - otherwise identical: %s" % lv)
            print("CC. 0.3.4 -> 0.3.5 changed: " + "; ".join("%s %s" % (c, [m.split("(")[0] for m in v["const_only"] + v["structural"]]) for c, v in sorted(cls_.items())))
        # ---- JT
        zj, zp = zipfile.ZipFile(JAR), zipfile.ZipFile(PREV_JAR)
        hits = sorted(n for n in zj.namelist() if re.search(rb"(?i)discipline", zj.read(n)))
        check(hits == ["com/skyy/trees/TreeClass.class"], "JT: 'discipline' only in TreeClass (CSKILL_KEY, the bridge name): %s" % hits)
        nn = set(n for n in zj.namelist() if not n.endswith(".class"))
        check(nn == set(n for n in zp.namelist() if not n.endswith(".class")) and all(zj.read(n) == zp.read(n) for n in nn if n != "manifest.json"),
              "JT: every asset file (173 interactions, effects, roots) byte-identical to 0.3.4's")
        mn, mp = json.loads(zj.read("manifest.json")), json.loads(zp.read("manifest.json"))
        check(json.dumps(mn, sort_keys=True) == json.dumps(mp, sort_keys=True).replace(PREV_VERSION, VERSION), "JT: manifest = 0.3.4's but the version")
        # ---- A + ZN
        zr = {}
        for tag, j in (("new", JAR), ("prev", PREV_JAR)):
            h = os.path.join(SCRATCH, "zn-" + tag)
            shutil.copytree(LIVE, h)
            zr[tag] = child(["--zn", j, "--home", h], os.path.join(SCRATCH, "zn-%s.json" % tag))
            r = zr[tag] or {}
            check(r and "error" not in r, "ZN (%s) ran: %s" % (tag, r.get("error", "")[-1500:]))
            check(r and not r.get("load_fails") and r.get("classes", 0) >= 30, "A (%s): %s classes load, verify, initialise %s" % (tag, r.get("classes"), r.get("load_fails", [])[:3]))
        n, o = zr.get("new") or {}, zr.get("prev") or {}
        if n and o and "error" not in n and "error" not in o:
            check(n["cskill"][6] == "Zen" and n["ckey"] == o["cskill"] and n["cskill"][:6] == o["cskill"][:6] and o["ckey"] is None,
                  "ZN: CSKILL Monk = Zen; CSKILL_KEY = 0.3.4's CSKILL exactly: %s / %s" % (n["cskill"], n["ckey"]))
            mk = n["texts"]["Monk"]
            check(mk[0].endswith("needs Zen 5 (you are 3)") and "(Zen 30 x " in mk[1] and "Ability Points come from your Zen level" in mk[2]
                  and [t.replace("Zen", "Discipline") for t in mk] == o["texts"]["Monk"],
                  "ZN: the Monk's tree texts say Zen (needs / respec price / AP help), else 0.3.4's: %s" % mk)
            check(all(n["texts"][c] == o["texts"][c] for c in n["texts"] if c != "Monk"), "ZN: every other class's tree texts identical to 0.3.4's")
        # ---- ST (the 0.3.4 harness's start routine, both jars)
        fake = os.path.join(SCRATCH, "fake")
        subprocess.run([sys.executable, me, "--mkfake", fake, "--dir", SCRATCH], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        sts = {}
        for tag, j in (("new", JAR), ("prev", PREV_JAR)):
            sts[tag] = child(["--st", j, "--fake", fake, "--live", LIVE, "--tag", tag], os.path.join(SCRATCH, "st-%s.json" % tag))
            check(sts[tag] is not None and len(sts[tag].get("starts", [])) == 2, "ST (%s): two starts ran" % tag)
        if sts.get("new") and sts.get("prev"):
            T = t34()
            sn, sp = sts["new"]["starts"], sts["prev"]["starts"]
            check(T.norm_start(sn[0]).replace("0.3.5", "0.3.X") == T.norm_start(sp[0]).replace("0.3.5", "0.3.X"),
                  "ST: start 1 of 0.3.5 = 0.3.4's (same summary, migrations, changed files): %s / %s" % (sn[0]["changed"], sp[0]["changed"]))
            check(sn[1]["changed"] == [] and sn[1]["sum"] == sn[0]["sum"], "ST: start 2 changes nothing and reads the same: %s" % sn[1]["changed"])
            print("ST. start twice on the live copy: start 1 changed %s (same as 0.3.4), start 2 nothing" % sn[0]["changed"])
        # ---- MX
        mh = os.path.join(SCRATCH, "mx-home")
        shutil.copytree(os.path.join(MODS_LIVE, "Skyy_SkyySkills"), mh)
        mx = child(["--mx", "--home", mh], os.path.join(SCRATCH, "mx.json"), script=SKILLS_HARNESS)
        check(mx is not None and "error" not in mx, "MX ran: %s" % (mx or {}).get("error", "")[-1500:])
        if mx and "error" not in mx:
            lv = [(r["skills"], r["classes"], r["trees_level_T34"], r["trees_level_T35"]) for r in mx["rows"]]
            check(len(lv) == 4 and all(a == b == 30 for _s, _c, a, b in lv),
                  "MX: TreeClass.level of 0.3.4 and 0.3.5 = 30 for a level-30 Monk with SkyySkills 0.4.26 / 0.4.27 and SkyyClasses 0.1.14 / 0.1.15: %s" % lv)
        # ---- CF
        if "--no-cf" not in sys.argv:
            carry_forward(env)
        check(snap(LIVE) == live_before, "the live Skyy_SkyyTrees folder was never written (only read + copied)")
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyTrees %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
