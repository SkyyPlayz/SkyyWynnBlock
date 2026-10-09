"""SkyyProfiles 0.1.8 - bare-JVM harness for THE MONK SKILL IS "ZEN" (tools/profiles_0_1_8_patch.py; Skyy LOCKED 2026-10-08): the fallback
roster's Monk card. Child JVMs run the game's own JRE with HytaleServer.jar on the class path, -Xverify:all, -XX:-UsePerfData, TEMP / TMP /
java.io.tmpdir in the scratch folder. The live save data is only ever READ and copied into scratch (checked afterwards).

    python SkyyProfiles/test_skyyprofiles_0.1.8.py --dir <empty folder inside tools/dev/scratch/> [--keep] [--no-cf]
         [--jar SkyyProfiles-0.1.8.jar] [--prev SkyyProfiles-0.1.7.jar] [--live <Skyy_SkyyProfiles folder>]

SECTIONS
  A   every class of both jars loads, verifies (-Xverify:all) and initialises (own class loader each)
  CC  CLASS COMPARE 0.1.7 -> 0.1.8 (javassist text of every method, constructor, static initialiser): nothing added or removed, no
      structural change; ProfRoster.<clinit> differs only by "Zen" for "Discipline"; the rest = the version string
  JT  jar texts: no "discipline" left anywhere; assets byte-identical; manifest = 0.1.7's but the version
  ZN  EXECUTED (both jars): the REAL ProfRoster.roster() / entry / skillOf - without SkyyClasses (no class:list) the Monk card says Zen
      (0.1.7 Discipline); with SkyyClasses' class:list it says what SkyyClasses lists (0.1.14 "Monk:Discipline" -> Discipline, 0.1.15
      "Monk:Zen" -> Zen) in both versions; the other six cards identical; "Shaman" still = the Monk
  ST  START TWICE on a scratch COPY of Skyy's live Skyy_SkyyProfiles (the 0.1.5 harness's start routine = SkyyProfilesPlugin.setup's
      data steps: upgradeDefault, capMigrate, load, scanIndex, CfgPub, the first expiry sweep): nothing changes, both starts read Skyy's
      profiles back the same as 0.1.7 (incl. the Monk profile 6)
  MX  the SkyySkills 0.4.27 harness's mixed-partner matrix: the Create Profile Monk card of 0.1.7 and 0.1.8 with SkyyClasses 0.1.14 /
      0.1.15 (= class:list) and without SkyyClasses
  CF  CARRY-FORWARD: the 0.1.7 harness (+ H16 / H15 = 80,000+ checks) on the 0.1.8 jar next to the control run on the 0.1.7 jar: the only
      new fails are its 0.1.6-comparison checks that see the Monk card's Zen or the version string
"""
import os, sys, re, json, shutil, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, PREV_VERSION = "0.1.8", "0.1.7"
PKG = "com.skyy.profiles."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "zen01", "profiles018")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyProfiles-%s.jar" % VERSION)))
PREV_JAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyyProfiles-%s.jar" % PREV_VERSION)))
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
MODS_LIVE = os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods")
LIVE = os.path.abspath(arg("--live", os.path.join(MODS_LIVE, "Skyy_SkyyProfiles")))
SKILLS_HARNESS = os.path.join(ROOT, "SkyySkills", "test_skyyskills_0.4.27.py")
CL14 = "Archer:Archery,Warrior:Swordsmanship,Mage:Sorcery,Berserker:Fury,Priest:Divinity,Assassin:Assassination,Monk:Discipline"
CL15 = CL14.replace("Monk:Discipline", "Monk:Zen")
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


def t15():
    return _mod(os.path.join(HERE, "test_skyyprofiles_0.1.5.py"), "tp015")


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
        Ros, Cfg = C("ProfRoster"), C("ProfCfg")
        br = Cfg.bridge()
        R["cards"] = {}
        for tag, lst in (("none", None), ("c14", CL14), ("c15", CL15)):
            if lst is None:
                br.remove("class:list")
            else:
                br.put("class:list", lst)
            R["cards"][tag] = [[str(x) for x in e] for e in Ros.roster()]
            R["skillOf_" + tag] = [str(Ros.skillOf(c)) for c in ("Monk", "Shaman", "monks", "Priest")]
        br.remove("class:list")
    except Exception:
        import traceback
        R["error"] = traceback.format_exc()[-3000:]
    json.dump(R, open(out, "w"), indent=1)
    os._exit(0)


def run_st(jar, home, out):
    t15().run_start(jar, home, out)
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
        p = subprocess.run([sys.executable, os.path.join(HERE, "test_skyyprofiles_0.1.7.py"), "--jar", j, "--dir", os.path.join(SCRATCH, "cf-" + tag)],
                           env=env, capture_output=True, encoding="utf8", errors="replace")
        res[tag] = (fails_of(p.stdout or ""), p.stdout or "")
    fn_, fc_ = res["new"][0], res["ctl"][0]
    extra = sorted(fn_ - fc_)

    def expected(f):
        if f.startswith("P: all 54 page states identical in 0.1.7 and 0.1.6"):
            return all(x.startswith("create") for x in re.findall(r"'([^']+)'", f.split("differ ", 1)[1]))   # the Create Profile cards (Monk: Zen)
        if f == "F: ProfCfg.capMigrate differs only by its version string (listing has 0.1.7)":
            return True
        if f.startswith("F: outside the plan only the config kit changes (KEEP 20 -> 10): "):
            return "'ProfRoster.class': (['<clinit>()V'], {})" in f and "'VERSION': ['0.1.6', '0.1.8']" in f
        if f.startswith("H16: the 0.1.6 harness on 0.1.7 fails nothing beyond"):
            items = re.findall(r'"([^"]+)"', f)
            return items and all(i.startswith("G16: entry / indexOf / canon: ['Monk', 'Zen',") for i in items)
        return False
    bad = [f for f in extra if not expected(f)]
    check(all(f.startswith("G17 files: the live players files hold no p.<id>.hp") for f in fc_),
          "CF: the 0.1.7 harness on the 0.1.7 jar (control): only its known live-data fail (Skyy's profile 7 has a saved Health now): %s" % sorted(fc_))
    check(not bad and 1 <= len(extra) <= 4, "CF: on the 0.1.8 jar only the expected Monk-card / version checks fail beyond the control: unexpected %s" % [b[:240] for b in bad])
    for f in extra:
        print("CF expected: " + f[:260])
    for ln in res["new"][1].splitlines():
        if ln.startswith("H16.") or ln.startswith("H15."):
            print("CF " + ln[:260])


def main():
    if "--zn" in sys.argv:
        return run_zn(arg("--zn"), arg("--out"))
    if "--st" in sys.argv:
        return run_st(arg("--st"), arg("--home"), arg("--out"))
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
        cc = child(["--cc", JAR, "--prevjar", PREV_JAR, "--repl", json.dumps({"versions": [VERSION, PREV_VERSION], "rules": [[r'"Zen"', '"Discipline"']]})],
                   os.path.join(SCRATCH, "cc.json"))
        check(cc is not None, "CC: the compare child ran")
        if cc:
            cls_ = cc["classes"]
            check(not cc["added"] and not cc["gone"] and all(v["same_shape"] and not v["fields_new"] and not v["fields_gone"] and not v["structural"] for v in cls_.values())
                  and sorted(cls_) == ["ProfRoster"] and cls_["ProfRoster"]["const_only"] == ["<clinit>"],
                  "CC: only ProfRoster.<clinit> changed, and only by the Monk's Zen (the version normalised): %s" % dict(
                      (c, v["const_only"] + v["structural"]) for c, v in cls_.items()))
        # ---- JT
        zj, zp = zipfile.ZipFile(JAR), zipfile.ZipFile(PREV_JAR)
        hits = sorted(n for n in zj.namelist() if re.search(rb"(?i)discipline", zj.read(n)))
        check(hits == [], "JT: no 'discipline' left in the jar: %s" % hits)
        nn = set(n for n in zj.namelist() if not n.endswith(".class"))
        check(nn == set(n for n in zp.namelist() if not n.endswith(".class")) and all(zj.read(n) == zp.read(n) for n in nn if n != "manifest.json"),
              "JT: every asset file byte-identical to 0.1.7's")
        mn, mp = json.loads(zj.read("manifest.json")), json.loads(zp.read("manifest.json"))
        check(json.dumps(mn, sort_keys=True) == json.dumps(mp, sort_keys=True).replace(PREV_VERSION, VERSION), "JT: manifest = 0.1.7's but the version")
        # ---- A + ZN
        zr = {}
        for tag, j in (("new", JAR), ("prev", PREV_JAR)):
            zr[tag] = child(["--zn", j], os.path.join(SCRATCH, "zn-%s.json" % tag))
            r = zr[tag] or {}
            check(r and "error" not in r, "ZN (%s) ran: %s" % (tag, r.get("error", "")[-1500:]))
            check(r and not r.get("load_fails") and r.get("classes", 0) >= 40, "A (%s): %s classes load, verify, initialise %s" % (tag, r.get("classes"), r.get("load_fails", [])[:3]))
        n, o = zr.get("new") or {}, zr.get("prev") or {}
        if n and o and "error" not in n and "error" not in o:
            def monk(cards):
                return [c for c in cards if c[0] == "Monk"][0]
            check(monk(n["cards"]["none"])[1] == "Zen" and monk(o["cards"]["none"])[1] == "Discipline"
                  and [c for c in n["cards"]["none"] if c[0] != "Monk"] == [c for c in o["cards"]["none"] if c[0] != "Monk"]
                  and monk(n["cards"]["none"])[2:] == monk(o["cards"]["none"])[2:],
                  "ZN: without SkyyClasses the Monk card says Zen (0.1.7 Discipline); the other six cards + the Monk's text / colour / icons identical")
            check(n["cards"]["c14"] == o["cards"]["c14"] and monk(n["cards"]["c14"])[1] == "Discipline" and n["cards"]["c15"] == o["cards"]["c15"]
                  and monk(n["cards"]["c15"])[1] == "Zen", "ZN: with SkyyClasses' class:list the card says what it lists (0.1.14 Discipline, 0.1.15 Zen) - both versions alike")
            check(n["skillOf_none"] == ["Zen", "Zen", "Zen", "Divinity"] and n["skillOf_c15"] == ["Zen", "Zen", "Zen", "Divinity"],
                  "ZN: skillOf Monk / Shaman / monks = Zen: %s %s" % (n["skillOf_none"], n["skillOf_c15"]))
        # ---- ST (two starts per jar on its own live copy)
        T = t15()
        st = {}
        for tag, j in (("new", JAR), ("prev", PREV_JAR)):
            home = os.path.join(SCRATCH, "st-" + tag, "Skyy_SkyyProfiles")
            shutil.copytree(LIVE, home)
            h0 = T.all_hashes(home)
            runs = []
            for k in (1, 2):
                runs.append(child(["--st", j, "--home", home], os.path.join(SCRATCH, "st-%s-%d.json" % (tag, k))))
            st[tag] = (runs, h0, T.all_hashes(home))
            check(all(runs) and st[tag][1] == st[tag][2], "ST (%s): two starts on the live copy change nothing: %s" % (
                tag, sorted(set(st[tag][1].items()) ^ set(st[tag][2].items()))[:4]))
        if all(st["new"][0]) and all(st["prev"][0]):
            a, b = st["new"][0], st["prev"][0]
            check(a[0] == a[1] and json.dumps(a[0], sort_keys=True) == json.dumps(b[0], sort_keys=True) and "6 " in a[0].get("describe", ""),
                  "ST: both starts read Skyy's profiles back exactly like 0.1.7 (profile 6 = the Monk): %s" % a[0].get("describe", "")[:300])
        # ---- MX
        mh = os.path.join(SCRATCH, "mx-home")
        shutil.copytree(os.path.join(MODS_LIVE, "Skyy_SkyySkills"), mh)
        mx = child(["--mx", "--home", mh], os.path.join(SCRATCH, "mx.json"), script=SKILLS_HARNESS)
        check(mx is not None and "error" not in mx, "MX ran: %s" % (mx or {}).get("error", "")[-1500:])
        if mx and "error" not in mx:
            cards = [(r["classes"], r["profiles_card_P17"], r["profiles_card_P18"]) for r in mx["rows"]]
            check(all(p17 == p18 == ("Zen" if c == "C15" else "Discipline") for c, p17, p18 in cards) and mx["profiles_fallback_P18"] == "Zen",
                  "MX: the Monk card follows SkyyClasses' class:list in 0.1.7 and 0.1.8; 0.1.8 alone says Zen: %s %s" % (cards, mx["profiles_fallback_P18"]))
        # ---- CF
        if "--no-cf" not in sys.argv:
            carry_forward(env)
        check(snap(LIVE) == live_before, "the live Skyy_SkyyProfiles folder was never written (only read + copied)")
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyProfiles %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
