"""SkyyMenu 0.3.13 - bare-JVM harness for THE MONK SKILL IS ZEN + THE CLASS BALANCE DAMAGE ON THE STATS PAGE (tools/menu_0_3_13_patch.py).
Child JVMs run the game's own JRE with HytaleServer.jar on the class path, -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in
the scratch folder; every jar gets its own class loader and they share the one skyy.bridge map. Nothing outside the scratch folder is
written (the live Skyy_SkyyMenu folder is checked afterwards).

    python SkyyMenu/test_skyymenu_0.3.13.py --dir <empty folder inside tools/dev/scratch/> [--keep] [--no-cf]
         [--jar SkyyMenu-0.3.13.jar] [--prev SkyyMenu-0.3.12.jar]

SECTIONS
  A   every class of both jars loads, verifies (-Xverify:all) and initialises
  CC  CLASS COMPARE 0.3.12 -> 0.3.13 (javassist text of every method, constructor, static initialiser): added only StatsCalc.skillDmg;
      structural changes only StatsCalc.classDamage (the class balance part) and StatsCalc.<clinit> (CLASS_SKILLS + the old label);
      every other change = constants (Zen for Discipline, the round's four Mods versions, the own version)
  JT  jar texts: "discipline" only in StatsCalc (CLASS_SKILLS' old label, an internal match); no Mods / menu text says Discipline; the
      Skills Mods entry + the Skills tile say Zen; assets byte-identical but manifest (version)
  DM  THE CLASS WEAPON DAMAGE ROW EXECUTED with 0.3.12's StatsCalc (own loader, same bridge) beside 0.3.13's, a Monk (class:skill Zen,
      Zen 30): skill:dmg:<uuid> absent / a String / Float / Integer / Long / NaN / +inf / negative / 0 -> every tab of 0.3.13 = 0.3.12
      row for row; a Double 2.5 -> "+8.5%" = level part 6% + "Class balance +2.5%", every other row 0.3.12's, under 80 characters;
      huge -> clamped 100000; perk.enabled off -> the class balance only; no class / class syncing -> 0.3.12's row; the key PUBLISHED BY
      THE REAL SkyySkills 0.4.27 SkillDef.setDmg (2.345 -> 2.35, then removed at 0)
  ZN  the Skills tab with the old / new label pairs: 0.3.13 files "Zen" AND "Discipline" (a SkyySkills 0.4.26 next to it) under the class
      skills; 0.3.12 files "Zen" as a plain skill row (why the menu ships with this round)
  CF  CARRY-FORWARD: the 0.3.12 harness (every check since 0.3.x: settings, Server Setup, page guard, the Stats page incl. the Defense row)
      on the 0.3.13 jar next to its control run on the 0.3.12 jar: the only new fails are its version / Mods-version / Zen-text / K6
      compare checks
"""
import os, sys, re, json, shutil, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, PREV_VERSION = "0.3.13", "0.3.12"
PKG = "com.skyy.menu."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "zen01", "menu0313")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)))
PREV_JAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyyMenu-%s.jar" % PREV_VERSION)))
SKILLS_JAR = os.path.join(ROOT, "SkyySkills", "SkyySkills-0.4.27.jar")
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
LIVE = os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyyMenu")
SKILLS_HARNESS = os.path.join(ROOT, "SkyySkills", "test_skyyskills_0.4.27.py")
FAILS, OKS = [], [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def sk():
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


def snap(d):
    return dict((os.path.relpath(os.path.join(r, f), d).replace(os.sep, "/"), open(os.path.join(r, f), "rb").read())
                for r, _ds, fs in os.walk(d) for f in fs) if os.path.isdir(d) else {}


# ============================================================================================ child: DM + ZN (both jars, one JVM)
def run_dm(out):
    from jpype import JClass, JImplements, JOverride, JArray, JObject, JDouble
    S = sk()
    S.jvm_start()
    R = {"load": {}}
    L = {}
    for tag, j in (("new", JAR), ("prev", PREV_JAR), ("skills", SKILLS_JAR)):
        L[tag] = S.loader(j)
        R["load"][tag] = S.load_all(j, L[tag])
    try:
        N, P = JClass(PKG + "StatsCalc", loader=L["new"]), JClass(PKG + "StatsCalc", loader=L["prev"])
        BRG = JClass(PKG + "MenuUtil", loader=L["new"]).bridge()
        UUID = JClass("java.util.UUID")
        Dbl, Lng, Flt, Int, JStr = JClass("java.lang.Double"), JClass("java.lang.Long"), JClass("java.lang.Float"), JClass("java.lang.Integer"), JClass("java.lang.String")

        @JImplements("java.util.function.Function")
        class SFn:
            def __init__(s_, f):
                s_.f = f

            @JOverride
            def apply(s_, a):
                return s_.f(a)
        CFG = {"perk.enabled": "true"}

        def cfg_fn(a):
            if str(a[0]) == "get":
                return CFG.get(str(a[1]))
            return None
        U = UUID.fromString("00000000-0000-0000-0000-0000000005d9")
        us = str(U)
        BRG.put("gear:fn:stats", SFn(lambda a: None))
        BRG.put("gear:stats:" + us, "str:10,def:12")
        BRG.put("skill:" + us, "Mining:12,Foraging:8,Farming:5,Acrobatics:3,Alchemy:0,Smithing:2,Cooking:1,Exploration:4,Zen:30")
        BRG.put("class:" + us, "Monk")
        BRG.put("class:skill:" + us, "Zen")
        BRG.put("profile:name:" + us, "Monkey")
        BRG.put("config:fn:SkyySkills", SFn(cfg_fn))
        BRG.put("skill:fn:level", SFn(lambda a: Int.valueOf(0)))
        KD = "skill:dmg:" + us

        def rows(C, tab, u=U):
            r_ = C.rows(u, tab, None)
            return [tuple(str(x) for x in r_.get(i)) for i in range(int(r_.size()))]

        def tabs(C, u=U):      # tab 3 (Skills) files Zen differently in 0.3.12 by design - section ZN
            return [rows(C, t, u) for t in (0, 1, 2, 4)]

        def cwd(C, u=U):
            m_ = [r for r in rows(C, 1, u) if r[0] == "Class Weapon Damage"]
            return list(m_[0]) if m_ else None

        def long_rows(tb):
            return [r for t in tb for r in t if len(r[0]) + len(r[1]) + len(r[2]) + 2 >= 80]

        D = {}
        BRG.remove(KD)
        D["absent"] = [tabs(N) == tabs(P), cwd(N), cwd(P)]
        bad = []
        for what, v in (("String", JStr("2.5")), ("Float", Flt.valueOf(2.5)), ("Integer", Int.valueOf(3)), ("Long", Lng.valueOf(3)),
                        ("NaN", Dbl.valueOf(float("nan"))), ("+inf", Dbl.valueOf(float("inf"))), ("negative", Dbl.valueOf(-2.0)), ("0", Dbl.valueOf(0.0))):
            BRG.put(KD, v)
            bad.append([what, tabs(N) == tabs(P), cwd(N)])
        D["bad"] = bad
        BRG.put(KD, Dbl.valueOf(2.5))
        tn, tp = tabs(N), tabs(P)
        D["present"] = [cwd(N), cwd(P), [[r for r in t if r[0] != "Class Weapon Damage"] for t in tn] == [[r for r in t if r[0] != "Class Weapon Damage"] for t in tp],
                        [[r[0] for r in t] for t in tn] == [[r[0] for r in t] for t in tp], long_rows(tn)]
        BRG.put(KD, Dbl.valueOf(1.0e9))
        D["huge"] = cwd(N)
        D["tiny"] = []      # FIX zen01fix: below the part() floor 0.05 = the row is exactly 0.3.12's (was: lost the class weapons ending)
        for v in (0.01, 0.02, 0.04, 0.0499):
            BRG.put(KD, Dbl.valueOf(v))
            D["tiny"].append([v, tabs(N) == tabs(P), cwd(N)])
        BRG.put(KD, Dbl.valueOf(0.05))
        D["edge"] = cwd(N)
        BRG.put(KD, Dbl.valueOf(2.5))
        CFG["perk.enabled"] = "false"
        D["perk_off"] = [cwd(N), cwd(P)]
        CFG["perk.enabled"] = "true"
        CFG["perk.combat.damagePerLevel"] = "0.004"
        D["rate"] = cwd(N)
        del CFG["perk.combat.damagePerLevel"]
        BRG.remove("class:skill:" + us)
        D["noclass"] = [cwd(N), cwd(P)]
        BRG.put("class:skill:" + us, "Zen")
        BRG.put("profile:class:" + us, "Warrior")
        BRG.put("class:fn:get", SFn(lambda a: None))
        D["syncing"] = [cwd(N), cwd(P)]
        BRG.remove("profile:class:" + us)
        BRG.remove("class:fn:get")
        # the REAL publisher: SkyySkills 0.4.27 SkillDef.setDmg (rounding, removal at 0)
        SDef = JClass("com.skyy.skills.SkillDef", loader=L["skills"])
        BRG.remove(KD)
        SDef.setDmg(U, JDouble(2.345))
        D["real"] = [str(BRG.get(KD).getClass().getName()) if BRG.get(KD) is not None else None, cwd(N)]
        SDef.setDmg(U, JDouble(0.0))
        D["real_removed"] = [BRG.get(KD) is None, cwd(N), cwd(N) == cwd(P)]
        SDef.setDmg(U, JDouble(0.02))      # FIX zen01fix: a level-1 Monk (balance 2% x 1/100) publishes 0.02 -> 0.3.12's row
        D["real_tiny"] = [str(BRG.get(KD)), tabs(N) == tabs(P), cwd(N)]
        SDef.setDmg(U, JDouble(0.0))
        R["DM"] = D
        # ---- ZN: the Skills tab with old / new label pairs
        Z = {}
        for lab in ("Zen", "Discipline"):
            BRG.put("skill:" + us, "Mining:12,Foraging:8,%s:30" % lab)
            BRG.put("class:skill:" + us, lab)
            Z[lab] = [[list(r) for r in rows(N, 3) if r[0] in ("Zen", "Discipline")], [list(r) for r in rows(P, 3) if r[0] in ("Zen", "Discipline")]]
        Z["isClass"] = [[bool(N.isClassSkill(x)) for x in ("Zen", "Discipline", "Mining", "zen")], [bool(P.isClassSkill(x)) for x in ("Zen", "Discipline", "Mining")]]
        R["ZN"] = Z
    except Exception:
        import traceback
        R["error"] = traceback.format_exc()[-3000:]
    json.dump(R, open(out, "w"), indent=1)
    os._exit(0)


# ============================================================================================ parent
def cp_strings(data):
    """the UTF8 constants of a class file"""
    import struct
    out, i, k = set(), 10, 1
    n = struct.unpack(">H", data[8:10])[0]
    while k < n:
        t = data[i]
        if t == 1:
            ln = struct.unpack(">H", data[i + 1:i + 3])[0]
            out.add(data[i + 3:i + 3 + ln].decode("utf8", "replace"))
            i += 3 + ln
        elif t in (3, 4, 9, 10, 11, 12, 17, 18):
            i += 5
        elif t in (5, 6):
            i += 9
            k += 1
        elif t in (7, 8, 16, 19, 20):
            i += 3
        elif t == 15:
            i += 4
        else:
            raise ValueError("constant tag %d" % t)
        k += 1
    return out


def fails_of(text):
    return set(ln[len("FAIL "):] for ln in text.splitlines() if ln.startswith("FAIL "))


def carry_forward(env):
    res = {}
    for tag, j in (("new", JAR), ("ctl", PREV_JAR)):
        p = subprocess.run([sys.executable, os.path.join(HERE, "test_skyymenu_0.3.12.py"), "--jar", j, "--dir", os.path.join(SCRATCH, "cf-" + tag)],
                           env=env, capture_output=True, encoding="utf8", errors="replace")
        res[tag] = (fails_of(p.stdout or ""), p.stdout or "")
    fn_, fc_ = res["new"][0], res["ctl"][0]
    extra = sorted(fn_ - fc_)
    pats = [r"^F\. Skyy(Classes|Menu) version 0\.(1\.14|3\.12) \(SET\)$", r"^F\. 0\.3\.7: 26 mods \(SkyyMenu 0\.3\.13\): 26$",
            r"^F2\. Skyy(Skills|Trees) [\d.]+ in the Mods list \(got (0\.4\.27|0\.3\.5)\)$",
            r"^F4\. Skyy(Classes|Skills|Profiles) [\d.]+ in the Mods list \(this round, ROUND_PINS; got (0\.1\.15|0\.4\.27|0\.1\.8)\)$",
            r"^F4\. SkyySkills description: the seven class skills", r"^F4\. the main menu Skills tile names .*Assassination or Zen\)",
            r"^K\. manifest\.json", r"^K6\. "]
    bad = [f for f in extra if not any(re.search(p, f) for p in pats)]
    known = [r"^F\. SkyyAuctions version", r"^F\. SkyyMerchants version", r"^F\. MODS lists exactly the SET mods", r"^F\. 26 mods, each listed once"]
    check(all(any(re.search(p, f) for p in known) for f in fc_), "CF: the 0.3.12 harness on the 0.3.12 jar (control): only its known Mods-list-behind-SET fails: %s" % sorted(fc_))
    check(not bad and len(extra) >= 10, "CF: on the 0.3.13 jar only the expected version / Mods-version / Zen-text / K6 checks fail beyond the control (%d): unexpected %s"
          % (len(extra), [b[:240] for b in bad]))
    m = re.search(r"checks passed per part: (.*)", res["new"][1])
    print("CF: %d extra (expected) fails; parts passed on 0.3.13: %s" % (len(extra), (m.group(1)[:300] if m else "?")))


def main():
    if "--dm" in sys.argv:
        return run_dm(arg("--out"))
    if "--cc" in sys.argv:
        return sk().run_cc(arg("--cc"), arg("--prevjar"), arg("--out"), arg("--repl"))
    for j in (JAR, PREV_JAR, SKILLS_JAR):
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

    def child(args_, out_):
        with open(out_ + ".log", "wb") as lf:
            subprocess.run([sys.executable, me] + args_ + ["--out", out_, "--dir", SCRATCH], env=env, stdout=lf, stderr=subprocess.STDOUT)
        if not os.path.isfile(out_):
            print(open(out_ + ".log", encoding="utf8", errors="replace").read()[-3000:])
            return None
        return json.load(open(out_))
    try:
        # ---- CC
        rules = [[r'\bZen\b', "Discipline"], [r'"0\.4\.27"', '"0.4.21"'], [r'"0\.1\.15"', '"0.1.14"'], [r'"0\.3\.5"', '"0.3.2"'], [r'"0\.1\.8"', '"0.1.6"'],
                 [r"menu_0_3_13_patch", "menu_0_3_10_patch"]]
        cc = child(["--cc", JAR, "--prevjar", PREV_JAR, "--repl", json.dumps({"versions": [VERSION, PREV_VERSION], "rules": rules})], os.path.join(SCRATCH, "cc.json"))
        check(cc is not None, "CC: the compare child ran")
        if cc:
            cls_ = cc["classes"]
            struct = dict((c, sorted(v["structural"])) for c, v in cls_.items() if v["structural"])
            check(not cc["added"] and not cc["gone"] and all(v["same_shape"] and not v["fields_new"] and not v["fields_gone"] for v in cls_.values()),
                  "CC: no class / field added or removed: %s %s" % (cc["added"], cc["gone"]))
            check(struct == {"MenuData": ["<clinit>"], "StatsCalc": ["<clinit>", "classDamage(Ljava/util/ArrayList;Ljava/util/UUID;Ljava/util/HashMap;)V",
                                           "skillDmg(Ljava/util/UUID;)D (new)"]},
                  "CC: structural changes = StatsCalc.skillDmg (new), classDamage, <clinit> (CLASS_SKILLS + the old label) + MenuData.<clinit> "
                  "(its data strings - JT2 lists them) only: %s" % struct)
            print("CC. 0.3.12 -> 0.3.13 changed: " + "; ".join("%s %s" % (c, [m.split("(")[0] for m in v["const_only"] + v["structural"]]) for c, v in sorted(cls_.items())))
        # ---- JT
        zj, zp = zipfile.ZipFile(JAR), zipfile.ZipFile(PREV_JAR)
        hits = sorted(n for n in zj.namelist() if re.search(rb"(?i)discipline", zj.read(n)))
        check(hits == ["com/skyy/menu/StatsCalc.class"], "JT: 'discipline' only in StatsCalc (CLASS_SKILLS' old label, an internal match): %s" % hits)
        md = zj.read("com/skyy/menu/MenuData.class")
        check(b"Assassination or Zen, on its own XP curve" in md and b"Assassination or Zen) and more" in md,
              "JT: the Skills Mods entry + the main menu Skills tile say Zen")
        dn, dp = cp_strings(md), cp_strings(zp.read("com/skyy/menu/MenuData.class"))
        new_s, old_s = sorted(dn - dp), sorted(dp - dn)
        check([x[:12] for x in new_s] == ["0.1.15", "0.3.5", "0.4.27", "Skills - Min", "Your skill l"] and [x[:12] for x in old_s] == ["0.1.14", "0.3.12", "0.3.2", "0.4.21", "Skills - Min", "Your skill l"]
              and new_s[3] == old_s[4].replace("Assassination or Discipline,", "Assassination or Zen,") and new_s[4] == old_s[5].replace("or Discipline)", "or Zen)"),
              "JT2: MenuData's data strings: + Classes 0.1.15 / Trees 0.3.5 / Skills 0.4.27 (Profiles 0.1.8 = an existing string) and the two Zen texts; "
              "- 0.1.14 / 0.3.2 / 0.4.21, the own 0.3.12 and the two Discipline texts: %s / %s" % ([x[:40] for x in new_s], [x[:40] for x in old_s]))
        nn = set(n for n in zj.namelist() if not n.endswith(".class"))
        check(nn == set(n for n in zp.namelist() if not n.endswith(".class")) and all(zj.read(n) == zp.read(n) for n in nn if n != "manifest.json"),
              "JT: every asset file byte-identical to 0.3.12's")
        mn, mp = json.loads(zj.read("manifest.json")), json.loads(zp.read("manifest.json"))
        check(json.dumps(mn, sort_keys=True) == json.dumps(mp, sort_keys=True).replace(PREV_VERSION, VERSION), "JT: manifest = 0.3.12's but the version")
        # ---- A + DM + ZN
        r = child(["--dm"], os.path.join(SCRATCH, "dm.json"))
        check(r is not None and "error" not in r, "DM ran: %s" % (r or {}).get("error", "")[-1500:])
        if r:
            for tag, (n_, f_) in r["load"].items():
                check(not f_ and n_ >= 30, "A (%s): %d classes load, verify, initialise %s" % (tag, n_, f_[:3]))
        if r and "error" not in r:
            D = r["DM"]
            base = ["Class Weapon Damage", "+6%", "Zen level 30, with your class weapons"]
            check(D["absent"] == [True, base, base], "DM1 no skill:dmg key: every tab = 0.3.12's; Class Weapon Damage %s" % D["absent"][1:])
            check(all(b[1] and b[2] == base for b in D["bad"]), "DM2 a String / Float / Integer / Long / NaN / inf / negative / 0 -> every tab 0.3.12's: %s" % [b[:2] for b in D["bad"] if not (b[1] and b[2] == base)])
            pr = D["present"]
            check(pr[0] == ["Class Weapon Damage", "+8.5%", "Zen level 30 +6%, Class balance +2.5%"] and pr[1] == base and pr[2] and pr[3] and not pr[4],
                  "DM3 skill:dmg 2.5 (Double): +8.5%% = level 6%% + Class balance 2.5%% (0.3.12: +6%%); every other row + the order = 0.3.12's; all under 80: %s" % pr)
            check(D["huge"] == ["Class Weapon Damage", "+100,006%", "Zen level 30 +6%, Class balance +100,000%"], "DM4 huge -> clamped at 100000: %s" % D["huge"])
            check(all(t[1] and t[2] == base for t in D["tiny"]), "DM4 FIX 0.01 / 0.02 / 0.04 / 0.0499 (below the 0.05 part floor) -> every tab = 0.3.12's: %s" % D["tiny"])
            check(D["edge"] is not None and D["edge"][2].startswith("Zen level 30 +6%, Class balance +") and D["edge"][1] != "-",
                  "DM4 FIX 0.05 (the floor) -> the class balance part shows: %s" % D["edge"])
            check(D["perk_off"] == [["Class Weapon Damage", "+2.5%", "Zen level 30, Class balance +2.5%"], ["Class Weapon Damage", "0%", "Zen level 30, with your class weapons"]],
                  "DM5 perk.enabled off: the class balance alone (SkyySkills adds it without the level perk): %s" % D["perk_off"])
            check(D["rate"] == ["Class Weapon Damage", "+14.5%", "Zen level 30 +12%, Class balance +2.5%"], "DM5 perk.combat.damagePerLevel 0.004: %s" % D["rate"])
            check(D["noclass"][0] == D["noclass"][1] == ["Class Weapon Damage", "-", "no class on this profile yet"]
                  and D["syncing"][0] == D["syncing"][1] == ["Class Weapon Damage", "-", "class syncing, Refresh in a moment"],
                  "DM6 no class / class syncing -> 0.3.12's row even with the key: %s %s" % (D["noclass"][0], D["syncing"][0]))
            check(D["real"] == ["java.lang.Double", ["Class Weapon Damage", "+8.4%", "Zen level 30 +6%, Class balance +2.4%"]]
                  and D["real_removed"] == [True, base, True]
                  and D["real_tiny"][0] in ("0.02", "0.020000000000000004") and D["real_tiny"][1] and D["real_tiny"][2] == base,
                  "DM7 the key from the REAL SkyySkills 0.4.27 SkillDef.setDmg(2.345) = Double 2.35 -> +8.4%%; setDmg(0) removes it -> 0.3.12's row; "
                  "FIX setDmg(0.02) (level-1 Monk) -> 0.3.12's row: %s %s %s" % (D["real"], D["real_removed"], D["real_tiny"]))
            Z = r["ZN"]
            check(Z["Zen"][0] == [["Zen", "Level 30", "your class weapon skill"]] and Z["Zen"][1] == [["Zen", "Level 30", ""]],
                  "ZN: label Zen (SkyySkills 0.4.27): 0.3.13 shows it as the class weapon skill; 0.3.12 as a plain skill row: %s" % Z["Zen"])
            check(Z["Discipline"][0] == Z["Discipline"][1] == [["Discipline", "Level 30", "your class weapon skill"]],
                  "ZN: label Discipline (SkyySkills 0.4.26 + SkyyClasses 0.1.14): 0.3.13 = 0.3.12: %s" % Z["Discipline"])
            check(Z["isClass"] == [[True, True, False, False], [False, True, False]], "ZN: isClassSkill: %s" % Z["isClass"])
        # ---- CF
        if "--no-cf" not in sys.argv:
            carry_forward(env)
        check(snap(LIVE) == live_before, "the live Skyy_SkyyMenu folder was never written")
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyMenu %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
