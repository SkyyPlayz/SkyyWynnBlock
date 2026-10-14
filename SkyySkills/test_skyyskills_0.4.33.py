"""SkyySkills 0.4.33 - harness for MANA REGEN 3.3 A SECOND (tools/skills_0_4_33_patch.py; Skyy 2026-10-13 M11 "Vanilla 0.7's 3.3 per
second"): MANA_INTERVAL 0.2 -> 0.3 s, ManaRegen.PULSE follows it, the default config comments name 3.3 / 4 per second.
Build first: python tools/skills_0_4_33_patch.py && python SkyySkills/build_skyyskills_0.4.33.py

    python SkyySkills/test_skyyskills_0.4.33.py --dir <empty folder inside tools/dev/scratch/> [--keep]

Phases (every JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch):
  M0  (parent, pure Python) the generated script's own MANA GEN block exec'd on Assets.zip's 0.7 Mana.json with the script's MANA_INTERVAL:
      = the jar's Mana.json; flat refill +1 every 0.3 s (3.33 a second), Max / InitialValue 0, NoDamageTaken 6 s, Creative entry untouched;
      vs the 0.4.32 jar's file ONLY the flat refill's Interval differs (0.2 -> 0.3)
  M   (child JVMs = test_skyyskills_0.4.31.py's --m child on the REAL engine, both jars) the engine's EntityStatType.CODEC decodes the shipped
      Mana.json; out of combat the engine refills 3.333 a second and SkyySkills adds nothing; in combat (hit 1 s ago) the engine pauses and
      SkyySkills refills 75 % = 2.5 a second (REAL ManaRegen.state / rates / amount / combatLeft); Base Mana none 25 / Mage 45 / Priest 42;
      ManaGuard: the shipped file -> INFO (refill 3.333), vanilla 0.7's (another mod's file won) -> WARN for max 100 + no pause only.
      Control 0.4.32: 5 / 3.75 a second.
  A   verify      every class loads + initialises with -Xverify:all
  C   compare     0.4.32 -> 0.4.33: exactly the planned members differ; non-class entries: manifest.json + the Mana.json
  P   pulse       ManaRegen.PULSE 0.3; the REAL ManaRegen.tick pulse gate (0.25 s waits, 0.35 s pulses and resets the clock); amount() in /
                  out of combat on the 0.3 s rate; compact() / stateLine() texts on 3.333; the default xp.properties comments (3.3 / 4 per
                  second, +1 every 0.3 s; no "5 per second" left); the fresh default file = 0.4.32's except those comment lines
  X   exec        test_skyyskills_0.4.32.py's exec phase on the 0.4.33 jar (every 0.4.32 lag-fix path, vs 0.4.31 where it compares)
  D   live        test_skyyskills_0.4.32.py's live phase on the 0.4.33 jar: START TWICE on a scratch COPY of the live Skyy_SkyySkills (0.4.33
                  changes exactly what 0.4.31 + PollMig change, start 2 nothing, player files untouched, leaderboard = 0.4.31's)
  AA  engine-access audit
Scratch: <dir>/m (M0 / M) and <dir>/h (the kit phases); deleted at the end unless --keep. Exit code 1 on any failure.
"""
import os, sys, json, shutil, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.4.33"
PKG = "com.skyy.skills."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySkills-0.4.32.jar")
BASE = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "mana33", "h")))
# the kit phases get <dir>/h (HK.run wipes its folder); M0 / M get <dir>/m. A child is started with --dir <dir>/h already.
SCRATCH = BASE if "--phase" in sys.argv else os.path.join(BASE, "h")
MSCRATCH = os.path.join(BASE, "m")
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyySkills")
ASSETS = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
MANA_PATH = "Server/Entity/Stats/Mana.json"

EXPECT = {
    # PULSE 0.2f -> 0.3f: a static final constant, inlined into tick's compare (the field itself carries no initialiser code)
    "ManaRegen": ["~m tick"],
    # MANA_PS 5.0 -> 3.3333 inlined into manaReport + the version texts as in every round
    "ManaGuard": ["~m armReport2", "~m intReport", "~m manaReport", "~m packReport"],
    "SkyySkillsPlugin": ["~m setup"],
    # the default xp.properties text (inlined DEFAULTS / MREG_DEFAULTS / the base Mana block): the two rate comment blocks + the version header
    "SkillCfg": ["~m ensureManaRegen", "~m load"],
    "OverallCfg": ["~m ensureDefaults"],
    "ManaMig": ["~<clinit>"],   # DOC_NEW = the base Mana comment of the default file ("+1 every 0.3 s"); DOC_OLD unchanged
    "CfgRows": ["~<clinit>", "~m header"],
    "CfgFn": ["~m opExport"],
}
ADDED = []


def tmod(fn, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# 0.4.32's harness: its exec / live phases run unchanged on the 0.4.33 jar (OLD_JAR there = 0.4.31, the behaviour they compare against)
T32 = tmod("test_skyyskills_0.4.32.py", "t0432")


def gen_block(src, start, end):
    i = src.index(start)
    return src[src.index("\n", i) + 1:src.index(end, i)]


# ====================================================================================================== M0 + M (parent, before the kit)
def mana_checks():
    os.makedirs(os.path.join(MSCRATCH, "tmp"), exist_ok=True)
    src = open(os.path.join(HERE, "build_skyyskills_%s.py" % VERSION), encoding="utf-8").read()
    ns = {}
    exec(compile([l for l in src.split("\n") if l.startswith("MANA_INTERVAL = ")][0], "MANA_INTERVAL", "exec"), ns)
    iv = ns["MANA_INTERVAL"]
    HK.check(iv == 0.3 and round(1.0 / iv, 2) == 3.33, "M0: the build script's MANA_INTERVAL = 0.3 s (3.33 Mana a second): %r" % iv)
    G = {"json": json}
    exec(compile(gen_block(src, "# >>> MANA GEN", "# <<< MANA GEN"), "MANA GEN", "exec"), G)
    v07 = json.loads(zipfile.ZipFile(ASSETS).read(MANA_PATH).decode("utf-8-sig"))
    new, ch = G["mana_gen"](v07, 6, iv)
    shipped = json.loads(zipfile.ZipFile(JAR).read(MANA_PATH).decode("utf-8"))
    old = json.loads(zipfile.ZipFile(OLD_JAR).read(MANA_PATH).decode("utf-8"))
    HK.check(shipped == new and list(shipped) == list(v07), "M0: the jar's Mana.json = MANA GEN on Assets.zip's 0.7 file: %s" % ch)
    fl = [r for r in shipped["Regenerating"] if r["RegenType"] == "Additive"]
    HK.check(shipped["InitialValue"] == 0 and shipped["Max"] == 0 and shipped["Min"] == v07["Min"] and len(fl) == 1 and fl[0]["Interval"] == 0.3
             and fl[0]["Amount"] == 1 and round(fl[0]["Amount"] / fl[0]["Interval"], 4) == 3.3333
             and fl[0]["Conditions"] == [{"Id": "Alive"}, {"Id": "NoDamageTaken", "Delay": 6}]
             and [r for r in shipped["Regenerating"] if r["RegenType"] != "Additive"] == [r for r in v07["Regenerating"] if r["RegenType"] != "Additive"],
             "M0: flat refill +1 every 0.3 s = 3.333 Mana a second, Alive + NoDamageTaken 6 s (no Charging pause), Max / Initial 0, Creative "
             "entry = 0.7's: %s" % json.dumps(shipped["Regenerating"]))
    HK.check(not any("every" in c and "->" in c for c in ch) and fl[0]["Interval"] == [r for r in v07["Regenerating"] if r["RegenType"] == "Additive"][0]["Interval"],
             "M0: the Interval is now vanilla 0.7's own (MANA GEN changes only Max / InitialValue + the pause): %s" % ch)
    back = json.loads(json.dumps(shipped))
    back["Regenerating"][[i for i, r in enumerate(back["Regenerating"]) if r["RegenType"] == "Additive"][0]]["Interval"] = 0.2
    HK.check(back == old, "M0: vs the 0.4.32 jar's Mana.json ONLY the flat refill's Interval differs (0.2 -> 0.3)")
    # M: the 0.4.31 harness's real-engine Mana child, on both jars
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(MSCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    t31 = os.path.join(HERE, "test_skyyskills_0.4.31.py")

    def child31(log, *a):
        with open(os.path.join(MSCRATCH, log), "wb") as lf:
            return subprocess.run([sys.executable, t31] + list(a) + ["--dir", MSCRATCH], env=env, stdout=lf, stderr=subprocess.STDOUT).returncode
    fake = os.path.join(MSCRATCH, "fake")
    HK.check(child31("mkfake.log", "--mkfake", fake) == 0, "M: stand-in classes generated (0.4.15 harness)")
    R = {}
    for tag, jar in (("new", JAR), ("old", OLD_JAR)):
        home = os.path.join(MSCRATCH, "home-" + tag)
        shutil.copytree(LIVE_DIR, home)
        out = os.path.join(MSCRATCH, "m-%s.json" % tag)
        rc = child31("m-%s.log" % tag, "--m", jar, "--fake", fake, "--home", home, "--out", out)
        R[tag] = json.load(open(out)) if rc == 0 and os.path.isfile(out) else {"error": "child rc %s" % rc}
        HK.check("error" not in R[tag] and not R[tag].get("load_fails"), "M %s: the child ran, every class loaded: %s" % (tag, R[tag].get("error")))
    M, O = R["new"], R["old"]
    if "error" in M or "error" in O:
        return
    print("M. 0.4.33 engine-decoded Mana stat: %s" % json.dumps(M["stat"]))
    print("   0.4.33: out %s | in %s" % (json.dumps(M["phase"]["out"]), json.dumps(M["phase"]["in"])))
    print("   0.4.32 (control): out %s | in %s" % (json.dumps(O["phase"]["out"]), json.dumps(O["phase"]["in"])))
    st = M["stat"]
    HK.check(M["shipped"] and st["initial"] == 0.0 and st["max"] == 0.0 and st["regen"][0][:3] == [1.0, 0.3, "ADDITIVE"]
             and st["regen"][0][3] == ["AliveCondition", "NoDamageTakenCondition"],
             "M1: the engine's EntityStatType.CODEC decodes the shipped Mana.json: Max / Initial 0, +1 every 0.3 s if Alive + NoDamageTaken")
    o, i = M["phase"]["out"], M["phase"]["in"]
    HK.check(o["states"] == [0] and o["vanilla_per_s"] == 3.3333 and o["skyy_per_s"] == 0.0 and o["total_per_s"] == 3.3333 and o["combat_left_ms"] == 0,
             "M2 out of combat: the engine refills 3.333 Mana a second, SkyySkills adds nothing, not in combat: %s" % o)
    HK.check(i["states"] == [1] and i["vanilla_per_s"] == 0.0 and i["skyy_per_s"] == 2.5 and i["total_per_s"] == 2.5 and 4990 <= i["combat_left_ms"] <= 5000,
             "M2 in combat (hit 1 s ago): the engine pauses, SkyySkills refills 75%% of 3.333 = 2.5 a second (was 3.75), %d ms left: %s" % (i["combat_left_ms"], i))
    oo, oi = O["phase"]["out"], O["phase"]["in"]
    HK.check(oo["vanilla_per_s"] == 5.0 and oi["skyy_per_s"] == 3.75, "M2 control 0.4.32: 5 a second out of combat, 3.75 in combat: %s / %s" % (oo, oi))
    b = M["base"]
    HK.check(b["none"]["max"] == 25.0 and b["Mage"]["max"] == 45.0 and b["Priest"]["max"] == 42.0 and b == O["base"],
             "M3: Base Mana unchanged (none 25, Mage 45, Priest 42; = 0.4.32): %s" % b)
    HK.check(M["gates"] == O["gates"] and M["ints"] == O["ints"] and M["arm"] == O["arm"], "M4: spell costs / checks unchanged vs 0.4.32")
    mg = M.get("mg") or {}
    sh, v7 = mg.get("shipped") or {}, mg.get("vanilla07") or {}
    ex = mg.get("exp") or [None, 0.0, None, None]
    HK.check([ex[0], round(ex[1], 4), ex[2], ex[3]] == [0.0, 3.3333, True, True] and sh.get("facts") == [0.0, 0.0, 3.3333, 1.0] and (sh.get("report") or [""])[0] == "info"
             and "refill 3.333 a second" in sh["report"][1], "MG: the shipped Mana.json -> ManaGuard INFO, refill 3.333 a second: %s" % sh.get("report"))
    vr = v7.get("report") or ["", ""]
    HK.check(vr[0] == "warn" and "max 100 instead of 0" in vr[1] and "no combat pause" in vr[1] and "refill" not in vr[1].split("NOT the one in effect")[1].split(". Another")[0],
             "MG: vanilla 0.7's file in effect -> WARN names max 100 + no combat pause, NOT the refill (both 3.333 now): %s" % vr[1])
    HK.check(mg.get("none", [None])[0] == "" and mg.get("check", ["THREW"])[0] in ("", "info", "warn"), "MG: manaCheck() runs in a bare JVM: %s" % mg.get("check"))


# ====================================================================================================== P: the pulse + texts (child)
def run_pulse(out, jar, scratch, _home):
    from jpype import JClass, JArray, JFloat
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    P = lambda n: JClass(PKG + n)
    Mana, Cfg, MG = P("ManaRegen"), P("SkillCfg"), P("ManaGuard")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    K.check(abs(float(Mana.PULSE) - 0.3) < 1e-6, "P: ManaRegen.PULSE = 0.3 s (the shipped Mana.json interval): %r" % float(Mana.PULSE))
    K.check(abs(float(MG.MANA_PS) - 3.3333) < 1e-4 and float(MG.MANA_MAX) == 0.0 and bool(MG.MANA_PAUSE) and bool(MG.MANA_SHIPPED),
            "P: ManaGuard expects max 0, 3.3333 a second, the combat pause, shipped: %r" % float(MG.MANA_PS))
    # the REAL tick's pulse gate: 0.25 s accumulates (no ECS touched - store / cb / ref are null), 0.35 s pulses (the store read throws
    # inside tick's own try, logged once) and the clock restarts at 0
    u = JClass("java.util.UUID")(0x33, 3)
    Mana.CLK.remove(u)
    Mana.FAILED_ONCE = False
    Mana.tick(u, None, None, None, JFloat(0.25))
    c = Mana.CLK.get(u)
    K.check(c is not None and abs(float(c[0]) - 0.25) < 1e-6 and not bool(Mana.FAILED_ONCE),
            "P: tick at 0.25 s waits for the 0.3 s pulse (clock %s, nothing read)" % (c is not None and float(c[0])))
    Mana.tick(u, None, None, None, JFloat(0.1))
    c = Mana.CLK.get(u)
    K.check(c is not None and float(c[0]) == 0.0 and bool(Mana.FAILED_ONCE), "P: tick at 0.35 s pulses (clock reset, the stand-in store read ran)")
    # amount() on the 0.3 s rate: out of combat with +20 % boosts, in combat at 75 %, at max nothing
    b = 1.0 / 0.3
    r_out = JArray(JFloat)([b, b, 0.0, 0.0, 0.0])
    r_in = JArray(JFloat)([b, 0.0, b, 0.0, 0.0])
    r_chg = JArray(JFloat)([b, 0.0, 0.0, b, 0.0])
    a1 = float(Mana.amount(r_out, 20.0, 75, JFloat(1.0), JFloat(0.0), JFloat(45.0)))
    a2 = float(Mana.amount(r_in, 0.0, 75, JFloat(1.0), JFloat(0.0), JFloat(45.0)))
    a3 = float(Mana.amount(r_in, 20.0, 75, JFloat(1.0), JFloat(0.0), JFloat(45.0)))
    a4 = float(Mana.amount(r_chg, 0.0, 75, JFloat(1.0), JFloat(0.0), JFloat(45.0)))
    a5 = float(Mana.amount(r_in, 0.0, 75, JFloat(0.3), JFloat(45.0), JFloat(45.0)))
    K.check(abs(a1 - 0.6667) < 1e-3 and abs(a2 - 2.5) < 1e-4 and abs(a3 - 3.0) < 1e-4 and abs(a4 - 3.3333) < 1e-3 and a5 == 0.0,
            "P: amount on 3.333 a second: +20%% out of combat adds 0.667 (total 4), in combat 2.5 (+20%%: 3.0), charging 3.333, at max 0: %s"
            % [round(x, 4) for x in (a1, a2, a3, a4, a5)])
    t = str(Mana.compact(0.0, JArray(JClass("java.lang.String"))(0), JFloat(b), 75))
    K.check("Refill 3.333/s" in t and "in combat 2.5/s (75%)" in t, "P: the Server Setup 'Mana Regen: show mine' line on 3.333: %s" % t)
    sl = str(Mana.stateLine(r_in, 0.0, 75, JFloat(45.0)))
    K.check("refills 2.5/s (75% of 3.333/s)" in sl, "P: /skills mana in combat: %s" % sl)
    # the default xp.properties comments
    d = str(Cfg.DEFAULTS)
    K.check("# Mana refills 3.3 per second, but not at all for 6 seconds" in d and "+20 percent = 4 per second" in d and "(+1 every 0.3 s after 6 s" in d
            and "5 per second" not in d and "6 per second" not in d and "every 0.2 s" not in d,
            "P: the default xp.properties comments say 3.3 / 4 per second and +1 every 0.3 s (no 5 / 6 per second, no 0.2 s left)")
    Lo = T32.loader_for(OLD_JAR, isolated=True)   # 0.4.32's classes, its own copy of the server jar
    try:
        od = str(JClass(PKG + "SkillCfg", loader=Lo).DEFAULTS)
        dl, ol = d.split("\n"), od.split("\n")
        diff = [(x, y) for x, y in zip(ol, dl) if x != y]
        K.check(len(dl) == len(ol) and len(diff) == 4 and all(x.startswith("#") and y.startswith("#") for x, y in diff)
                and [y for x, y in diff if not ("3.3 per second" in y or "4 per second" in y or "every 0.3 s" in y
                                                or y.startswith("# SkyySkills 0.4.33 - XP rules."))] == [],
                "P: the fresh default file = 0.4.32's except the 3 rate comment lines + the version header: %s" % diff)
        K.check(str(P("ManaMig").DOC_OLD[1]) == str(JClass(PKG + "ManaMig", loader=Lo).DOC_OLD[1]),
                "P: ManaMig still recognises the 0.4.6 / 0.4.7 comment it replaces (DOC_OLD unchanged)")
    except Exception as e:
        K.check(False, "P: 0.4.32 defaults readable: %s" % e)
    K.save()


def run_exec(out, jar, scratch, home):
    T32.SCRATCH = scratch
    return T32.run_exec(out, jar, scratch, home)


def run_live(out, jar, scratch, home):
    return T32.run_live(out, jar, scratch, home)


# the kit's class compare allows only manifest.json among the non-class entries; 0.4.33 also changes the generated Mana.json (the Interval,
# checked in M0) - that one entry is added to the expected list, every other check of the kit runs as it is
_orig_eq = HK.Child.eq


def _eq(self, got, want, what):
    if what == "C: non-class entries changed" and want == ["manifest.json"]:
        want = sorted(["manifest.json", MANA_PATH])
    return _orig_eq(self, got, want, what)


HK.Child.eq = _eq


if __name__ == "__main__":
    if "--phase" not in sys.argv:
        sc = os.path.realpath(BASE)
        assert sc.startswith(os.path.realpath(os.path.join(ROOT, "tools", "dev", "scratch")) + os.sep), "--dir must be inside tools/dev/scratch/"
        assert os.path.isfile(JAR) and os.path.isfile(OLD_JAR), (JAR, OLD_JAR)
        live0 = dict((os.path.relpath(os.path.join(r, f), LIVE_DIR), (os.path.getsize(os.path.join(r, f)), os.path.getmtime(os.path.join(r, f))))
                     for r, _d, fs in os.walk(LIVE_DIR) for f in fs) if os.path.isdir(LIVE_DIR) else None
        shutil.rmtree(MSCRATCH, ignore_errors=True)
        try:
            mana_checks()
        finally:
            if "--keep" not in sys.argv:
                shutil.rmtree(MSCRATCH, ignore_errors=True)
        live1 = dict((os.path.relpath(os.path.join(r, f), LIVE_DIR), (os.path.getsize(os.path.join(r, f)), os.path.getmtime(os.path.join(r, f))))
                     for r, _d, fs in os.walk(LIVE_DIR) for f in fs) if os.path.isdir(LIVE_DIR) else None
        HK.check(live0 == live1, "the live Skyy_SkyySkills folder is unchanged by M (read-only copies)")
        # fixer: the two code comments that described the current rate say 3.33, not 0.2 s / 5
        _bs = open(os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.33.py"), encoding="utf8").read()
        HK.check("(vanilla Mana: 1 / 0.2 s = 5)" not in _bs and "(shipped Mana: 1 / 0.3 s = 3.33)" in _bs,
                 "fix 1: per-entry rate comment says 1 / 0.3 s = 3.33")
        HK.check("(5 in vanilla;" not in _bs and "(3.33 as shipped since 0.4.33;" in _bs,
                 "fix 2: vanillaRate comment says 3.33")
    HK.run(name="SkyySkills", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("pulse", run_pulse), ("exec", run_exec), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyySkills"))
