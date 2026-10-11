"""SkyyClasses 0.1.15 - bare-JVM harness for THE MONK SKILL IS "ZEN" (tools/classes_0_1_15_patch.py; Skyy LOCKED 2026-10-08). Child JVMs run
the game's own JRE with HytaleServer.jar on the class path, -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in the scratch
folder. The live save data is only ever READ and copied into scratch (checked afterwards).

    python SkyyClasses/test_skyyclasses_0.1.15.py --dir <empty folder inside tools/dev/scratch/> [--keep] [--no-cf]
         [--jar SkyyClasses-0.1.15.jar] [--prev SkyyClasses-0.1.14.jar] [--live <Skyy_SkyyClasses folder>]

SECTIONS
  A   every class of both jars loads, verifies (-Xverify:all) and initialises (own class loader each)
  CC  CLASS COMPARE 0.1.14 -> 0.1.15 (every method, constructor and static initialiser as javassist instruction text): nothing added or
      removed; changed methods differ only in constants ("Zen" for "Discipline", the version) except ClassDefs.<clinit> (the alias
      arrays one entry longer)
  JT  jar texts: "discipline" (any case) only in ClassDefs (the alias); manifest = 0.1.14's but Version / Name; assets byte-identical
  ZN  EXECUTED (both jars): ClassDefs.SKILLS (Monk = Zen, the other six unchanged), indexOf for Zen / zen / Discipline / discipline /
      Shaman / Monk / Monks (all the Monk; 0.1.14: Zen unknown), class:list (listText), the REAL ClassStore.publishKey for a Monk profile
      (class:<uuid> Monk, class:skill:<uuid> Zen; 0.1.14 Discipline) and for profile:class = "Discipline" (old skill name as a class value
      -> still the Monk in both)
  ST  START TWICE on a scratch COPY of Skyy's live players folder (the 0.1.14 harness's MG routine: every live file loaded, the tick
      publish, a Shaman profile + a hand-written class=Shaman file): 0.1.15 reads + writes exactly what 0.1.14 does (Skyy's Monk
      profile p6 = Monk in both), start 2 writes nothing; only class:skill says Zen
  MX  the mixed-partner matrix of the SkyySkills 0.4.27 harness (its --mx child: Skills 0.4.26 / 0.4.27 x Classes 0.1.14 / 0.1.15 +
      Trees, Profiles, Hud): Classes 0.1.15 needs Skills 0.4.27 (with 0.4.26 its class:skill "Zen" resolves to level 0 = STOP rule)
  CF  CARRY-FORWARD: the 0.1.14 harness (19,000+ checks: weapon rules, kits, heal chain, page states, MG, access audit) on the 0.1.15
      jar next to its control run on the 0.1.14 jar: the only new fails are the expected Zen / version texts
"""
import os, sys, re, json, shutil, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, PREV_VERSION = "0.1.15", "0.1.14"
PKG = "com.skyy.classes."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "zen01", "classes0115")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyClasses-%s.jar" % VERSION)))
PREV_JAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyyClasses-%s.jar" % PREV_VERSION)))
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
MODS_LIVE = os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods")
LIVE = os.path.abspath(arg("--live", os.path.join(MODS_LIVE, "Skyy_SkyyClasses")))
SKILLS_HARNESS = os.path.join(ROOT, "SkyySkills", "test_skyyskills_0.4.27.py")
FAILS, OKS = [], [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def sk():
    """the SkyySkills 0.4.27 harness module (shared JVM helpers + run_cc); imported, never run"""
    spec = importlib.util.spec_from_file_location("ts0427", SKILLS_HARNESS)
    m = importlib.util.module_from_spec(spec)
    saved = list(sys.argv)
    sys.argv = [sys.argv[0], "--dir", SCRATCH]
    try:
        spec.loader.exec_module(m)
    finally:
        sys.argv = saved
    m.SCRATCH = SCRATCH
    return m


def t14():
    spec = importlib.util.spec_from_file_location("tc0114", os.path.join(HERE, "test_skyyclasses_0.1.14.py"))
    m = importlib.util.module_from_spec(spec)
    saved = list(sys.argv)
    sys.argv = [sys.argv[0], "--dir", SCRATCH]
    try:
        spec.loader.exec_module(m)
    finally:
        sys.argv = saved
    m.SCRATCH = SCRATCH
    return m


def snap(d):
    return dict((os.path.relpath(os.path.join(r, f), d).replace(os.sep, "/"), open(os.path.join(r, f), "rb").read())
                for r, _ds, fs in os.walk(d) for f in fs) if os.path.isdir(d) else {}


# ============================================================================================ child: ZN (one jar)
def run_zn(jar, out):
    from jpype import JClass
    S = sk()
    S.jvm_start()
    ld = S.loader(jar)
    R = {}
    R["classes"], R["load_fails"] = S.load_all(jar, ld)
    C = lambda n: JClass(PKG + n, loader=ld)
    try:
        D, St, Cfg = C("ClassDefs"), C("ClassStore"), C("ClassCfg")
        UUID = JClass("java.util.UUID")
        R["names"] = [str(x) for x in D.NAMES]
        R["skills"] = [str(x) for x in D.SKILLS]
        R["alias"] = [str(x) for x in D.ALIAS_FROM]
        R["idx"] = dict((s, int(D.indexOf(s))) for s in ["Zen", "zen", " ZEN ", "Discipline", "discipline", "Shaman", "Shaman skill", "Monk", "Monks",
                                                           "Archery", "Assassination", "zenith", ""])
        R["list"] = str(D.listText())
        R["choice"] = str(D.choiceText())
        br = Cfg.bridge()
        pub = {}
        for i, pc in enumerate(["Monk", "Discipline", "Zen", "Shaman"]):
            us = "00000000-0000-0000-0000-0000000005c%d" % i
            br.put("profile:class:" + us, pc)
            St.publishKey(UUID.fromString(us), us + "-p2")
            pub[pc] = [str(br.get("class:" + us)), str(br.get("class:skill:" + us))]
        R["pub"] = pub
    except Exception:
        import traceback
        R["error"] = traceback.format_exc()[-3000:]
    json.dump(R, open(out, "w"), indent=1)
    os._exit(0)


def run_mg(jar, home, step):
    m = t14()
    m.run_mg(jar, home, step)
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
        p = subprocess.run([sys.executable, os.path.join(HERE, "test_skyyclasses_0.1.14.py"), "--jar", j, "--dir", os.path.join(SCRATCH, "cf-" + tag)],
                           env=env, capture_output=True, encoding="utf8", errors="replace")
        t = p.stdout or ""
        m = re.findall(r"(\d+) checks passed, (\d+) failed", t)
        res[tag] = (sum(int(a) for a, b in m), fails_of(t))
    (okn, fn_), (okc, fc_) = res["new"], res["ctl"]
    extra = sorted(fn_ - fc_)
    VER_ONLY = ("CfgFn.class", "KitMigrate.class", "SkyyClassesPlugin.class")

    def expected(f):
        return (f.startswith("header 0-4 ") and "'0.1.15'" in f) or (f.startswith("kits.properties written: ") and "'version': '0.1.15'" in f) \
            or (f.startswith("class:list ") and f.endswith(",Monk:Zen")) or f.startswith("T14: the Monk row (index 6 = the old Shaman slot): Zen ") \
            or f == "T14: the alias table" or f == "Y-F: manifest: only the version, the name and the description differ: ['Description', 'Name', 'Version']" \
            or any(f.startswith("Y-F: %s: only the version string differs" % v) for v in VER_ONLY) \
            or (f.startswith("MG1: a class=Shaman file = the Monk") and "['Monk', 6, ['Monk', 'Zen']]" in f) \
            or (f.startswith("MG1: profile:class = Shaman -> class:<uuid> Monk") and "['Monk', 'Zen', 6, True] ['Monk', 'Zen', 6]" in f)
    bad = [f for f in extra if not expected(f)]
    check(okc > 19000 and len(fc_) <= 1 and all(f.startswith("MG1: the 9 live player files read the same class") for f in fc_),
          "CF: the 0.1.14 harness on the 0.1.14 jar (control): %d checks pass; its only fail = the live Monk profile 0.1.13 cannot read: %s" % (okc, sorted(fc_)))
    check(not bad and okn > 19000 and len(extra) == 11, "CF: on the 0.1.15 jar only the 11 expected Zen / version texts fail beyond the control (%d pass): unexpected %s"
          % (okn, [b[:200] for b in bad]))
    for f in extra:
        print("CF expected: " + f[:200])


def main():
    if "--zn" in sys.argv:
        return run_zn(arg("--zn"), arg("--out"))
    if "--mg" in sys.argv:
        return run_mg(arg("--mg"), arg("--home"), arg("--step"))
    if "--cc" in sys.argv:
        return sk().run_cc(arg("--cc"), arg("--prevjar"), arg("--out"), arg("--repl"))
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
        rules = [[r'"Zen"', '"Discipline"']]
        cc = child(["--cc", JAR, "--prevjar", PREV_JAR, "--repl", json.dumps({"versions": [VERSION, PREV_VERSION], "rules": rules})],
                   os.path.join(SCRATCH, "cc.json"))
        check(cc is not None, "CC: the compare child ran")
        if cc:
            cls_ = cc["classes"]
            struct = dict((c, v["structural"]) for c, v in cls_.items() if v["structural"])
            check(not cc["added"] and not cc["gone"] and all(v["same_shape"] and not v["fields_new"] and not v["fields_gone"] for v in cls_.values()),
                  "CC: no class / field added or removed: %s %s" % (cc["added"], cc["gone"]))
            check(struct == {"ClassDefs": ["<clinit>"]}, "CC: the only structural change = ClassDefs.<clinit> (the alias arrays): %s" % struct)
            print("CC. 0.1.14 -> 0.1.15 changed: " + "; ".join("%s %s" % (c, [m.split("(")[0] for m in v["const_only"] + v["structural"]]) for c, v in sorted(cls_.items())))
        # ---- JT
        zj, zp = zipfile.ZipFile(JAR), zipfile.ZipFile(PREV_JAR)
        hits = sorted(n for n in zj.namelist() if re.search(rb"(?i)discipline", zj.read(n)))
        check(hits == ["com/skyy/classes/ClassDefs.class"], "JT: 'discipline' only in ClassDefs (the alias): %s" % hits)
        nn = set(n for n in zj.namelist() if not n.endswith(".class"))
        check(nn == set(n for n in zp.namelist() if not n.endswith(".class")) and all(zj.read(n) == zp.read(n) for n in nn if n != "manifest.json"),
              "JT: every asset file byte-identical to 0.1.14's")
        mn, mp = json.loads(zj.read("manifest.json")), json.loads(zp.read("manifest.json"))
        check(json.dumps(mn, sort_keys=True) == json.dumps(mp, sort_keys=True).replace(PREV_VERSION, VERSION), "JT: manifest = 0.1.14's but the version")
        # ---- A + ZN
        zr = {}
        for tag, j in (("new", JAR), ("prev", PREV_JAR)):
            zr[tag] = child(["--zn", j], os.path.join(SCRATCH, "zn-%s.json" % tag))
            r = zr[tag] or {}
            check(r and "error" not in r, "ZN (%s) ran: %s" % (tag, r.get("error", "")[-1500:]))
            check(r and not r.get("load_fails") and r.get("classes", 0) >= 40, "A (%s): %s classes load, verify, initialise %s" % (tag, r.get("classes"), r.get("load_fails", [])[:3]))
        n, o = zr.get("new") or {}, zr.get("prev") or {}
        if n and o and "error" not in n and "error" not in o:
            check(n["names"] == o["names"] and n["skills"][6] == "Zen" and o["skills"][6] == "Discipline" and n["skills"][:6] == o["skills"][:6],
                  "ZN: SKILLS Monk Discipline -> Zen, names + the other six unchanged: %s" % n["skills"])
            check(n["alias"] == o["alias"] + ["Discipline"], "ZN: 'Discipline' appended to the aliases: %s" % n["alias"])
            want = dict(o["idx"])
            want.update({"Zen": 6, "zen": 6, " ZEN ": 6})
            check(n["idx"] == want and o["idx"]["Discipline"] == 6 and o["idx"]["Zen"] == -1, "ZN: indexOf Zen / Discipline / Shaman / Monk -> 6: %s (0.1.14 %s)" % (n["idx"], o["idx"]))
            check(n["list"] == o["list"].replace("Monk:Discipline", "Monk:Zen") and n["list"].endswith(",Monk:Zen") and n["choice"] == o["choice"],
                  "ZN: class:list says Monk:Zen; the class choice text unchanged: %s" % n["list"])
            check(n["pub"] == {"Monk": ["Monk", "Zen"], "Discipline": ["Monk", "Zen"], "Zen": ["Monk", "Zen"], "Shaman": ["Monk", "Zen"]}
                  and o["pub"]["Monk"] == ["Monk", "Discipline"] and o["pub"]["Discipline"] == ["Monk", "Discipline"],
                  "ZN: the REAL publishKey: a Monk profile (or Discipline / Zen / Shaman written as its class) -> class Monk, class:skill Zen: %s (0.1.14 %s)" % (n["pub"], o["pub"]))
        # ---- ST (the 0.1.14 harness's MG routine)
        T = t14()
        live_players = os.path.join(LIVE, "players")
        homes = {}
        for tag in ("new", "old"):
            h = os.path.join(SCRATCH, "mg-" + tag)
            shutil.copytree(live_players, os.path.join(h, "players"))
            open(os.path.join(h, "players", T.MG_SHAMAN_FILE + ".properties"), "w").write("class=Shaman\nplayed=Shaman\nprompted=1\n")
            open(os.path.join(h, "players", T.MG_PROFILE_K + ".properties"), "w").write("prompted=1\n")
            homes[tag] = h
        s0 = snap(os.path.join(homes["new"], "players"))
        mg = {}
        for step, j, h in (("1", JAR, homes["new"]), ("2", JAR, homes["new"]), ("old", PREV_JAR, homes["old"])):
            with open(os.path.join(SCRATCH, "mg-%s.log" % step), "wb") as lf:
                subprocess.run([sys.executable, me, "--mg", j, "--home", h, "--step", step, "--dir", SCRATCH], env=env, stdout=lf, stderr=subprocess.STDOUT)
            f = os.path.join(h, "mg-%s.json" % step)
            mg[step] = json.load(open(f)) if os.path.isfile(f) else None
            mg[step + "_snap"] = snap(os.path.join(h, "players"))
            check(mg[step] is not None, "ST: start %s ran" % step)
        if mg["1"] and mg["2"] and mg["old"]:
            ch1 = sorted(k for k in s0 if mg["1_snap"].get(k) != s0[k])
            cho = sorted(k for k in s0 if mg["old_snap"].get(k) != s0[k])
            def nots(sn):   # the date comment + chosenAt time stamp of the steady sync differ by the seconds between the runs
                return dict((k, re.sub(rb"(?m)^#[^\n]*\n|^chosenAt=\d+", b"", v)) for k, v in sn.items())
            check(ch1 == cho == [T.MG_PROFILE_K + ".properties"] and nots(mg["1_snap"]) == nots(mg["old_snap"]),
                  "ST: start 1 writes exactly what 0.1.14 writes (the Shaman profile's steady sync only; same bytes but its time stamp): %s / %s" % (ch1, cho))
            check(mg["2_snap"] == mg["1_snap"], "ST: start 2 writes nothing")

            def noskill(files):
                return dict((k, v[:2]) for k, v in files.items())
            check(noskill(mg["1"]["files"]) == noskill(mg["old"]["files"]) and mg["1"]["files"].get("d8ddde89-98b2-4739-983e-a39773d582b6-p6", [None])[0] == "Monk",
                  "ST: every live player file reads the same class as in 0.1.14 (Skyy's Monk profile p6 = Monk): %s" % dict(
                      (k, v[:2]) for k, v in mg["1"]["files"].items()))
            pubs = [(k, v[2]) for k, v in mg["1"]["files"].items() if len(v) > 2]
            pubo = dict((k, v[2]) for k, v in mg["old"]["files"].items() if len(v) > 2)
            check(all(v == [pubo[k][0], pubo[k][1].replace("Discipline", "Zen")] for k, v in pubs) and pubs,
                  "ST: the tick publishes the same class:<uuid> as 0.1.14; class:skill = 0.1.14's with Zen: %s" % pubs)
            check(mg["1"]["prof_first"] == ["Monk", "Zen", 6, True] and mg["old"]["prof_first"] == ["Monk", "Discipline", 6, True],
                  "ST: a Shaman profile = Monk / Zen (0.1.14 Monk / Discipline): %s" % mg["1"]["prof_first"])
        # ---- MX (the SkyySkills 0.4.27 harness's matrix child)
        mh = os.path.join(SCRATCH, "mx-home")
        shutil.copytree(os.path.join(MODS_LIVE, "Skyy_SkyySkills"), mh)
        mx = child(["--mx", "--home", mh], os.path.join(SCRATCH, "mx.json"), script=SKILLS_HARNESS)
        check(mx is not None and "error" not in mx, "MX ran: %s" % (mx or {}).get("error", "")[-1500:])
        if mx and "error" not in mx:
            rows = dict(((r["skills"], r["classes"]), r) for r in mx["rows"])
            a, b, c = rows[("S27", "C15")], rows[("S27", "C14")], rows[("S26", "C15")]
            check(a["class_skill"] == "Zen" and a["mobs_gear_level"] == 30 and a["hud_class_line"] == ["Zen", "30"] and a["skills_page_name"] == "Zen",
                  "MX: Classes 0.1.15 + Skills 0.4.27: class:skill Zen resolves (level 30), Hud + /skills say Zen: %s" % a)
            check(b["mobs_gear_level"] == 30 and c["mobs_gear_level"] == 0,
                  "MX: rollback Classes 0.1.14 next to Skills 0.4.27 still resolves (30); Classes 0.1.15 next to Skills 0.4.26 does NOT (0) - deploy together")
        # ---- CF
        if "--no-cf" not in sys.argv:
            carry_forward(env)
        check(snap(LIVE) == live_before, "the live Skyy_SkyyClasses folder was never written (only read + copied)")
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyClasses %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
