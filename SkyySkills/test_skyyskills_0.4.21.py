"""SkyySkills 0.4.21 - bare-JVM harness for THE MONK + ASSASSIN CLASS SKILLS (tools/skills_0_4_21_patch.py; Skyy LOCKED 2026-10-07 "1. make
the classes"). The new parts run on the REAL classes of the 0.4.21 jar and, as the control, the SET pin 0.4.20, with the REAL engine classes
(HytaleServer.jar on the class path, -Xverify:all); the live save data is only ever READ and copied into the scratch folder.

    python SkyySkills/test_skyyskills_0.4.21.py [--jar <SkyySkills-0.4.21.jar>] [--prev <SkyySkills-0.4.20.jar>] [--dir <scratch>]
                                                [--live <Skyy_SkyySkills folder>] [--keep] [--no20]

SECTIONS
  A   every class of both jars loads under -Xverify:all
  C   the class row: SkillDefs.CLASSES (Shaman -> Monk), LABELS[8] Discipline, NAMES[8] STILL Combat.Shaman, icon, colour; indexOf for
      every name of every slot (both jars: the same slot for every 0.4.20 name), the aliases (shaman / shamans / shaman skill), canonName
  X   SAVED XP on a scratch COPY of the live players folder + synthetic files: every live file read by both jars = the same long[] (every
      slot, paid markers too); re-saved by both jars = the same properties; a Combat.Shaman=12345 file -> slot 8 = 12345, re-saved as
      Combat.Shaman (no Combat.Monk key, nothing lost or doubled); the bridge skill:fn:xp / skill:fn:level answer the same XP for
      Discipline, Shaman, Shaman skill, Combat.Shaman, Monk (0.4.20: Shaman skill / Shaman / Combat.Shaman)
  S   (review fix) Overall.classOf: profile:class / class:<uuid> "Shaman" = "Monk" (the by-class Base Mana tables); 0.4.20 = "Shaman"
  S   SkillClass on the bridge: class:<uuid> Monk -> slot 8, rowSlot, skillName Discipline; profile:class still "Shaman" (an old
      SkyyProfiles) = consistent (no combat-XP pause); a real mismatch still pauses; weaponsText Monk = "Bo / Fist", every other class's
      text as 0.4.20 prints it
  DEF21 the fresh default xp.properties of 0.4.21 = 0.4.20's except the version header line
  O   OverallCfg.canonClass (the mana class tables) + the unknown-class texts; ManaGuard's built-in kit table
  H20 the 0.4.20 harness run against the 0.4.21 jar (control: the 0.4.20 jar): it fails nothing beyond the version-shape checks
      (class compare / default-file header) - its M section = START TWICE on a scratch copy of the live data, its KC / DEF / T / R parts
  F   class compare 0.4.20 -> 0.4.21 METHOD BY METHOD: only the planned methods / fields differ; every asset byte-identical
  AU  the engine-access audit (every bytecode reference looked up with the JVM's own access rules; control refused)
"""
import os, sys, re, json, shutil, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, PREV_VERSION = "0.4.21", "0.4.20"
PKG = "com.skyy.skills."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "classes014fix", "skills0421")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
PREV_JAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyySkills-%s.jar" % PREV_VERSION)))
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
LIVE_DIR = os.path.abspath(arg("--live", os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyySkills")))
KEEP = "--keep" in sys.argv
FAILS, OKS, GUARD_OK = [], [0], [False]
SYN_SHAMAN = "00000000-0000-0000-0000-0000000005b1"       # a player file with Discipline XP under the kept key Combat.Shaman
SYN_P2 = SYN_SHAMAN + "-p2"                                 # the same player's profile 2 (no slot 8 XP)


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


def t15():
    """the 0.4.15 harness module (JVM start, class loader, access audit, stand-ins) - imported, never run"""
    return tmod("test_skyyskills_0.4.15.py", "t0415")


def t20():
    """the 0.4.20 harness module (the method-by-method class compare) - imported, never run"""
    return tmod("test_skyyskills_0.4.20.py", "t0420")


def props(path):
    out = {}
    for l in open(path, encoding="latin-1").read().replace("\r\n", "\n").split("\n"):
        s = l.strip()
        if s and s[0] not in "#!" and "=" in s:
            k, v = s.split("=", 1)
            out[k.strip()] = v.strip()
    return out


# ============================================================================================ child: one jar
def run_child(jar, out, mode, home):
    from jpype import JClass, JImplements, JOverride, JArray, JObject
    T = t15()
    res, path = T.common(jar, [])
    if res["load_fails"]:
        json.dump(res, open(out, "w"), indent=1)
        return
    D = res["data"]
    NEW = mode == "new"
    Defs, Store, SC = JClass(PKG + "SkillDefs"), JClass(PKG + "SkillStore"), JClass(PKG + "SkillClass")
    OC, MG = JClass(PKG + "OverallCfg"), JClass(PKG + "ManaGuard")
    UUID, Paths, JStr, Arr = JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.lang.String"), JClass("java.lang.reflect.Array")

    def oa(*xs):
        a = JArray(JObject)(len(xs))
        for i, x in enumerate(xs):
            a[i] = x
        return a

    # ---------------- C
    names = ["mining", "foraging", "farming", "combat", "acrobatics", "archery", "swordsmanship", "assassination", "sorcery", "alchemy",
             "smithing", "cooking", "exploration", "fury", "divinity", "archer", "warrior", "assassin", "mage", "berserker", "priest",
             "combat.archer", "combat.assassin", "combat.shaman", "Combat.Priest", "shaman", "shaman skill", "Shamans", " SHAMAN ", "sha",
             "discipline", "Discipline", "monk", "Monk", "monks", "disc", "assa", "x", "", "combat.monk"]
    D["C"] = {"classes": [str(x) for x in Defs.CLASSES], "labels": [str(x) for x in Defs.LABELS], "names": [str(x) for x in Defs.NAMES],
              "icons": [str(x) for x in Defs.ICONS], "colors": [str(x) for x in Defs.COLORS], "slots": [int(x) for x in Defs.CLASS_SLOT],
              "idx": dict((n, int(Defs.indexOf(n))) for n in names)}
    if NEW:
        D["C"]["canon"] = dict((n, None if Defs.canonName(n) is None else str(Defs.canonName(n))) for n in ("Shaman", "shaman", "Shamans", "Shaman skill",
                                                                                                        "Monk", "Mage", "Priest", "x"))
        D["C"]["canon_null"] = Defs.canonName(None) is None
        D["C"]["alias"] = [[str(x) for x in Defs.ALIAS_FROM], [int(x) for x in Defs.ALIAS_TO]]

    # ---------------- X: saved XP on the copy (a fresh default xp.properties in scratch first: the level tables)
    Cfg = JClass(PKG + "SkillCfg")
    Cfg.FILE = path(os.path.join(home, "xp.properties"))
    D["load"] = str(Cfg.load())
    pdir = os.path.join(home, "players")
    Store.DIR = path(pdir)
    br = Store.bridge()
    X = {"data": {}, "resaved": {}}
    for fn in sorted(os.listdir(pdir)):
        if not fn.endswith(".properties"):
            continue
        k = fn[:-len(".properties")]
        u = UUID.fromString(k[:36])
        d = Store.dataK(k, u)
        X["data"][k] = [int(x) for x in d]
    for k in list(X["data"]):
        X["resaved"][k] = bool(Store.save(k))
    u5 = UUID.fromString(SYN_SHAMAN)

    @JImplements("java.util.function.Function")
    class KeyFn(object):
        @JOverride
        def apply(self, o):
            return str(o)
    br.put("profile:fn:key", KeyFn())
    xfn, lfn = br.get("skill:fn:xp"), br.get("skill:fn:level")
    if xfn is None:      # setup() is not run in a bare JVM: the bridge functions are the jar's own classes, made here
        xfn, lfn = JClass(PKG + "SkillXpFn")(), JClass(PKG + "SkillFn")()
    X["xp"] = dict((n, int(xfn.apply(oa(u5, n)))) for n in ("Discipline", "Shaman", "shaman skill", "Combat.Shaman", "Monk", "Assassination", "Archery"))
    X["lv"] = dict((n, int(lfn.apply(oa(u5, n)))) for n in ("Discipline", "Shaman", "Shaman skill", "Monk"))
    D["X"] = X

    # ---------------- S: SkillClass on the bridge
    us = UUID.fromString("00000000-0000-0000-0000-0000000005c1")
    S = {}
    for cls, w in (("Monk", "Weapon_Staff_Bo_,Weapon_Fist_,Weapon_Bo_"), ("Assassin", "Weapon_Daggers_,Weapon_Kunai"),
                   ("Mage", "Weapon_Staff_,Halloween_Broomstick,Weapon_Spellbook_"), ("Archer", "Weapon_Shortbow_,Weapon_Crossbow_,Weapon_Arrow_"),
                   ("Priest", "Weapon_Wand_,Weapon_Deployable_Healing_Totem"), ("Berserker", "Weapon_Battleaxe_,Weapon_Mace_,Weapon_Club_,Weapon_Axe_"),
                   ("Warrior", "Weapon_Longsword_,Weapon_Sword_,Weapon_Spear_")):
        br.put("class:weapons:" + cls, w)
    S["wtext"] = dict((c, None if SC.weaponsText(c) is None else str(SC.weaponsText(c)))
                      for c in ("Monk", "Assassin", "Mage", "Archer", "Priest", "Berserker", "Warrior", "Nobody"))
    S["slotOf"] = dict((c, int(SC.slotOfClass(c))) for c in ("Monk", "Shaman", " shaman ", "Assassin", "Mage", "Nope"))
    br.put("class:" + str(us), "Monk")
    br.put("class:skill:" + str(us), "Discipline")
    S["slot"] = int(SC.slot(us))
    S["row"] = int(SC.rowSlot(us, 3))
    S["name8"] = str(SC.skillName(us, 8))
    br.put("profile:class:" + str(us), "Shaman")
    S["cons_alias"] = bool(SC.consistent(us))
    br.put("profile:class:" + str(us), "Monk")
    S["cons_same"] = bool(SC.consistent(us))
    br.put("profile:class:" + str(us), "Mage")
    S["cons_diff"] = bool(SC.consistent(us))          # the first sighting of a real mismatch = pause (false)
    SC.resync(us)
    br.put("class:" + str(us), "Shaman")              # an old SkyyClasses still publishing Shaman
    br.put("class:skill:" + str(us), "Shaman skill")
    br.put("profile:class:" + str(us), "Shaman")
    S["old_classes"] = [int(SC.slot(us)), bool(SC.consistent(us)), str(SC.skillName(us, 8))]
    # review fix (critic 2 point 4): Overall.classOf = today's class name for the by-class Base Mana tables (profile:class first, else class:<uuid>)
    OV = JClass(PKG + "Overall")
    uo = UUID.fromString("00000000-0000-0000-0000-0000000005c2")

    def cof():
        c_ = OV.classOf(uo)
        return None if c_ is None else str(c_)
    co = {}
    for pc_, cc_ in (("Shaman", "Monk"), (" shaman ", "Monk"), ("Monk", "Monk"), ("Mage", "Mage"), (None, "Shaman"), (None, "Priest"), (None, None)):
        if pc_ is None:
            br.remove("profile:class:" + str(uo))
        else:
            br.put("profile:class:" + str(uo), pc_)
        if cc_ is None:
            br.remove("class:" + str(uo))
        else:
            br.put("class:" + str(uo), cc_)
        co["%s|%s" % (pc_, cc_)] = cof()
    S["classOf"] = co
    D["S"] = S

    # ---------------- O
    D["O"] = {"canon": dict((n, None if OC.canonClass(n) is None else str(OC.canonClass(n))) for n in ("shaman", "Shaman", "MONK", "Mage", "x")),
              "check": [None if OC.checkClasses("k", v) is None else str(OC.checkClasses("k", v)) for v in ("Monk", "Shaman", "Mage,Nope")],
              "fb": [[str(x) for x in MG.FB_CLS], [str(x) for x in MG.FB_KIT]]}
    json.dump(res, open(out, "w"), indent=1)


# ============================================================================================ parent
def main():
    if "--mkfake" in sys.argv:
        return t15().run_mkfake(arg("--mkfake"))
    if "--child" in sys.argv:
        return run_child(arg("--child"), arg("--out"), arg("--mode"), arg("--home"))
    if "--audit" in sys.argv:
        return t15().run_audit(arg("--audit"), arg("--fake"), arg("--out"))
    if "--compare" in sys.argv:
        m = t20()
        m.VERSION, m.PREV_VERSION = VERSION, PREV_VERSION
        return m.run_compare(arg("--compare"), arg("--prevjar"), arg("--out"))
    for j in (JAR, PREV_JAR):
        if not os.path.isfile(j):
            sys.exit("no jar at %s - build it first" % j)
    if not os.path.isdir(os.path.join(LIVE_DIR, "players")):
        sys.exit("the live players folder is not in %s (pass --live <folder>; it is only ever read and copied)" % LIVE_DIR)
    scratch_root = os.path.join(TOOLS, "dev", "scratch").replace("\\", "/").lower().rstrip("/")
    here = SCRATCH.replace("\\", "/").lower().rstrip("/")
    if here == scratch_root or not here.startswith(scratch_root + "/"):
        sys.exit("--dir must be a folder INSIDE tools/dev/scratch/ (the whole folder is deleted afterwards), not %s" % SCRATCH)
    GUARD_OK[0] = True
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.makedirs(env["TEMP"], exist_ok=True)
    live_snap = dict((os.path.relpath(os.path.join(r, f), LIVE_DIR), os.path.getmtime(os.path.join(r, f))) for r, ds, fs in os.walk(LIVE_DIR) for f in fs)
    me = os.path.abspath(__file__)
    homes, before = {}, {}
    for mode in ("new", "prev"):
        h = os.path.join(SCRATCH, "copy-" + mode)
        shutil.copytree(os.path.join(LIVE_DIR, "players"), os.path.join(h, "players"))
        open(os.path.join(h, "players", SYN_SHAMAN + ".properties"), "w").write(
            "name=Tester\nquiet=false\nCombat.Shaman=12345\nCombat.Shaman.paid=3\nCombat.Assassin=777\nCombat.Archer=5\nMining=40\n")
        open(os.path.join(h, "players", SYN_P2 + ".properties"), "w").write("Combat.Archer=9\n")
        homes[mode] = h
        before[mode] = dict((f, props(os.path.join(h, "players", f))) for f in os.listdir(os.path.join(h, "players")))
    fake = os.path.join(SCRATCH, "fake")
    p = subprocess.run([sys.executable, me, "--mkfake", fake, "--dir", SCRATCH], env=env)
    check(p.returncode == 0, "the stand-in classes were generated")
    outs = {}
    for mode, jar in (("prev", PREV_JAR), ("new", JAR)):
        outp = os.path.join(SCRATCH, "run-%s.json" % mode)
        logp = os.path.join(SCRATCH, "run-%s.log" % mode)
        with open(logp, "wb") as lf:
            p = subprocess.run([sys.executable, me, "--child", jar, "--out", outp, "--mode", mode, "--home", homes[mode], "--dir", SCRATCH],
                               env=env, stdout=lf, stderr=subprocess.STDOUT)
        check(p.returncode == 0 and os.path.isfile(outp), "child JVM (%s) ran (log %s)" % (mode, logp))
        if os.path.isfile(outp):
            outs[mode] = json.load(open(outp))
    cmpo = os.path.join(SCRATCH, "compare.json")
    pc = subprocess.run([sys.executable, me, "--compare", JAR, "--prevjar", PREV_JAR, "--out", cmpo, "--dir", SCRATCH], env=env, capture_output=True)
    check(pc.returncode == 0 and os.path.isfile(cmpo), "class compare child ran: %s" % pc.stderr[-500:])
    auo = os.path.join(SCRATCH, "audit.json")
    pa = subprocess.run([sys.executable, me, "--audit", JAR, "--fake", fake, "--out", auo, "--dir", SCRATCH], env=env, capture_output=True)
    check(pa.returncode == 0 and os.path.isfile(auo), "engine-access audit child ran: %s" % pa.stderr[-500:])
    h20 = None
    if "--no20" not in sys.argv:
        h20 = {}
        for tag, jj in (("new", JAR), ("ctl", PREV_JAR)):
            ph = subprocess.run([sys.executable, os.path.join(HERE, "test_skyyskills_0.4.20.py"), "--jar", jj, "--prev",
                                 os.path.join(HERE, "SkyySkills-0.4.19.jar"), "--dir", os.path.join(SCRATCH, "h20-" + tag), "--live", LIVE_DIR],
                                env=env, capture_output=True)
            h20[tag] = ph.stdout.decode("utf-8", "replace")
    if FAILS:
        return finish()
    for mode in ("new", "prev"):
        r = outs[mode]
        check(not r["load_fails"] and r["loaded"] == r["classes"], "A (%s): %d / %d classes load under -Xverify:all %s" % (mode, r["loaded"], r["classes"], r["load_fails"][:3]))
    if FAILS:
        return finish()
    N, P = outs["new"]["data"], outs["prev"]["data"]
    print("A. both jars: every class loads under -Xverify:all (%d / %d classes)" % (outs["new"]["loaded"], outs["prev"]["loaded"]))

    # ---------------------------------------------------------------- C
    C, CP = N["C"], P["C"]
    check(C["classes"] == ["Archer", "Warrior", "Assassin", "Monk", "Mage", "Berserker", "Priest"]
          and CP["classes"] == ["Archer", "Warrior", "Assassin", "Shaman", "Mage", "Berserker", "Priest"] and C["slots"] == CP["slots"] == [5, 6, 7, 8, 9, 14, 15],
          "C: CLASSES Shaman -> Monk in the same place (slots 5-9, 14, 15 unchanged): %s" % C["classes"])
    check(C["names"] == CP["names"] and C["names"][8] == "Combat.Shaman" and C["names"][7] == "Combat.Assassin",
          "C: every saved key is 0.4.20's - slot 8 STILL Combat.Shaman (players files unchanged): %s" % C["names"][5:10])
    dl = [i for i in range(len(C["labels"])) if C["labels"][i] != CP["labels"][i]]
    check(dl == [8] and C["labels"][8] == "Discipline" and CP["labels"][8] == "Shaman skill" and C["labels"][7] == "Assassination",
          "C: only label 8 changed: Shaman skill -> Discipline (%s)" % dl)
    check(C["icons"][8] == "Weapon_Staff_Bo_Wood" and C["colors"][8] == "#f08a30"
          and [i for i in range(16) if C["icons"][i] != CP["icons"][i] or C["colors"][i] != CP["colors"][i]] == [8],
          "C: slot 8 icon Bo staff + saffron, nothing else: %s %s" % (C["icons"][8], C["colors"][8]))
    same_ = [n for n in C["idx"] if n.strip().lower() not in ("sha", "discipline", "monk", "monks", "disc", "combat.monk", "shamans")]
    check(all(C["idx"][n] == CP["idx"][n] for n in same_), "C: every 0.4.20 skill / class / key name finds the same slot in 0.4.21: %s" % [
        (n, CP["idx"][n], C["idx"][n]) for n in same_ if C["idx"][n] != CP["idx"][n]])
    check(C["idx"]["shaman"] == C["idx"]["shaman skill"] == C["idx"][" SHAMAN "] == C["idx"]["Shamans"] == C["idx"]["combat.shaman"] == 8
          and C["idx"]["discipline"] == C["idx"]["Discipline"] == C["idx"]["monk"] == C["idx"]["Monk"] == C["idx"]["disc"] == 8
          and C["idx"]["assassination"] == C["idx"]["assassin"] == C["idx"]["assa"] == 7 and C["idx"]["x"] == C["idx"][""] == -1
          and C["idx"]["combat.monk"] == -1 and CP["idx"]["monk"] == -1 and CP["idx"]["discipline"] == -1,
          "C: indexOf - Shaman / Shamans / Shaman skill / Combat.Shaman / Discipline / Monk / disc = slot 8; Assassin 7; Combat.Monk is no key: %s"
          % dict((k, C["idx"][k]) for k in ("shaman", "shaman skill", "Shamans", "discipline", "monk", "disc", "sha", "combat.monk")))
    check(C["canon"] == {"Shaman": "Monk", "shaman": "Monk", "Shamans": "Monk", "Shaman skill": "Monk", "Monk": "Monk", "Mage": "Mage", "Priest": "Priest", "x": "x"}
          and C["canon_null"] and C["alias"] == [["shaman", "shamans", "shaman skill"], [3, 3, 3]], "C: canonName + the alias table: %s" % C["canon"])
    print("C. class row 3 = Monk, label 8 = Discipline, saved key Combat.Shaman kept; aliases Shaman / Shamans / Shaman skill -> slot 8; %d old names unchanged" % len(same_))

    # ---------------------------------------------------------------- X
    X, XP = N["X"], P["X"]
    live_keys = sorted(k for k in X["data"] if not k.startswith("00000000-0000-0000-0000-0000000005b1"))
    check(X["data"] == XP["data"] and len(live_keys) >= 1, "X: every player file (%d live + 2 synthetic) reads the SAME data in 0.4.21 as in 0.4.20 "
          "(every slot, every paid marker): %s" % (len(live_keys), [k for k in X["data"] if X["data"][k] != XP["data"].get(k)]))
    nslots = len(C["names"])
    syn = X["data"][SYN_SHAMAN]
    check(syn[8] == 12345 and syn[nslots + 8] == 3 and syn[7] == 777 and syn[5] == 5 and syn[0] == 40,
          "X: Combat.Shaman=12345 (paid 3) is slot 8 = Discipline XP; Assassination 777; Archery 5; Mining 40: %s" % syn[:16])
    check(all(X["resaved"].values()) and all(XP["resaved"].values()), "X: both jars saved every file")
    after = dict((m, dict((f, props(os.path.join(homes[m], "players", f))) for f in os.listdir(os.path.join(homes[m], "players"))
                          if f.endswith(".properties"))) for m in ("new", "prev"))
    check(after["new"] == after["prev"], "X: the files 0.4.21 writes = the files 0.4.20 writes, key for key: %s" % [
        f for f in after["new"] if after["new"][f] != after["prev"].get(f)])
    an = after["new"][SYN_SHAMAN + ".properties"]
    check(an.get("Combat.Shaman") == "12345" and an.get("Combat.Shaman.paid") == "3" and not [k for k in an if "Monk" in k or "Discipline" in k],
          "X: re-saved under the kept key Combat.Shaman (no Combat.Monk / Discipline key = nothing doubled): %s" % sorted(an))
    lost = [(f, k) for f in before["new"] for k, v in before["new"][f].items() if f.endswith(".properties") and after["new"][f].get(k) != v
            and not k.endswith(".paid")]
    check(not lost, "X: no saved value of any live or synthetic file changed by the re-save (0.4.21): %s" % lost[:5])
    check(X["xp"] == {"Discipline": 12345, "Shaman": 12345, "shaman skill": 12345, "Combat.Shaman": 12345, "Monk": 12345, "Assassination": 777, "Archery": 5}
          and XP["xp"]["shaman skill"] == XP["xp"]["Shaman"] == XP["xp"]["Combat.Shaman"] == 12345 and XP["xp"]["Discipline"] == 0,
          "X: skill:fn:xp - Discipline / Shaman / Shaman skill / Combat.Shaman / Monk all read slot 8 (12345); 0.4.20 knew no Discipline: %s | %s" % (X["xp"], XP["xp"]))
    check(len(set(X["lv"].values())) == 1 and X["lv"]["Discipline"] == XP["lv"]["Shaman skill"] > 0, "X: skill:fn:level the same for every name: %s %s" % (X["lv"], XP["lv"]))
    print("X. saved XP: %d live files + 2 synthetic read and re-saved identically by 0.4.20 and 0.4.21; Combat.Shaman=12345 = Discipline 12345, "
          "kept under Combat.Shaman; skill:fn:xp answers it for Discipline / Shaman / Shaman skill / Monk" % len(live_keys))

    # ---------------------------------------------------------------- DEF21: the fresh default xp.properties = 0.4.20's but the version header
    dn_ = open(os.path.join(homes["new"], "xp.properties"), "rb").read().decode("latin-1")
    dp_ = open(os.path.join(homes["prev"], "xp.properties"), "rb").read().decode("latin-1")
    LINES = lambda t_: t_.replace(chr(13), '').split(chr(10))
    dd_ = [x for x in zip(LINES(dn_), LINES(dp_)) if x[0] != x[1]]
    check(len(LINES(dn_)) == len(LINES(dp_)) and len(dd_) == 1 and VERSION in dd_[0][0] and PREV_VERSION in dd_[0][1]
          and dd_[0][0].replace(VERSION, "V") == dd_[0][1].replace(PREV_VERSION, "V"),
          "DEF21: the 0.4.21 default xp.properties = 0.4.20's except the version header line (no key, no comment changed): %s" % dd_[:3])
    print("DEF21. default file: only the version header differs (%d lines)" % len(LINES(dn_)))

    # ---------------------------------------------------------------- S
    S, SP = N["S"], P["S"]
    check(S["wtext"]["Monk"] == "Bo / Fist" and S["wtext"]["Assassin"] == "Daggers / Kunai" and S["wtext"]["Nobody"] is None
          and all(S["wtext"][c] == SP["wtext"][c] for c in ("Assassin", "Mage", "Archer", "Priest", "Berserker", "Warrior", "Nobody")),
          "S: weaponsText Monk = Bo / Fist (0.4.20: %s); every other class as 0.4.20: %s" % (SP["wtext"]["Monk"], S["wtext"]))
    check(S["slotOf"] == {"Monk": 8, "Shaman": 8, " shaman ": 8, "Assassin": 7, "Mage": 9, "Nope": -1}, "S: slotOfClass: %s" % S["slotOf"])
    check(S["slot"] == 8 and S["row"] == 8 and S["name8"] == "Discipline", "S: class:<uuid> Monk -> slot 8, the Combat row shows slot 8, named Discipline")
    check(S["cons_alias"] and S["cons_same"] and not S["cons_diff"] and not SP["cons_alias"],
          "S: profile:class Shaman vs class Monk = consistent (0.4.20 would pause combat XP: %s); a real mismatch still pauses" % SP["cons_alias"])
    check(S["old_classes"] == [8, True, "Shaman skill"], "S: an older SkyyClasses publishing Shaman still lands on slot 8: %s" % S["old_classes"])
    check(S["classOf"] == {"Shaman|Monk": "Monk", " shaman |Monk": "Monk", "Monk|Monk": "Monk", "Mage|Mage": "Mage", "None|Shaman": "Monk",
                           "None|Priest": "Priest", "None|None": None}
          and SP["classOf"]["Shaman|Monk"] == "Shaman" and SP["classOf"]["None|Shaman"] == "Shaman" and SP["classOf"]["Mage|Mage"] == "Mage",
          "S (review fix): Overall.classOf reads a Shaman profile / class as the Monk (0.4.20: Shaman), others unchanged: %s | 0.4.20 %s" % (S["classOf"], SP["classOf"]))
    print("S. SkillClass: Monk = slot 8 Discipline, weapons 'Bo / Fist'; profile Shaman = consistent; Overall.classOf Shaman -> Monk; others as 0.4.20")

    # ---------------------------------------------------------------- O
    O, OP = N["O"], P["O"]
    check(O["canon"] == {"shaman": "Monk", "Shaman": "Monk", "MONK": "Monk", "Mage": "Mage", "x": None} and OP["canon"]["Shaman"] == "Shaman",
          "O: canonClass (mana tables): a Shaman line counts for the Monk: %s" % O["canon"])
    check(O["check"][0] is None and O["check"][1] == "Unknown class Shaman - use Archer, Warrior, Mage, Berserker, Priest, Assassin or Monk."
          and O["check"][2].startswith("Unknown class Nope - use") and O["check"][2].endswith("Assassin or Monk."), "O: class list texts: %s" % O["check"])
    check(O["fb"][0] == ["Archer", "Warrior", "Assassin", "Monk", "Mage", "Berserker", "Priest"] and O["fb"][1][3] == "Weapon_Staff_Bo_Wood:1"
          and O["fb"][1][2] == "Weapon_Daggers_Crude:1", "O: ManaGuard's built-in kit table = SkyyClasses 0.1.14's kits: %s" % O["fb"])
    print("O. mana tables alias, texts, ManaGuard kit table")

    # ---------------------------------------------------------------- H20
    if h20 is not None:
        def fails_of(txt):
            return [ln.strip()[len("FAILED: "):] for ln in txt.splitlines() if ln.strip().startswith("FAILED: ")]
        fn_, fc_ = fails_of(h20["new"]), fails_of(h20["ctl"])
        ctl_keys = set(f[:60] for f in fc_)
        expected = ("F: 0.4.19 -> 0.4.20 differs only in the planned methods / fields", "DEF: the 0.4.20 default file = 0.4.19's",
                    "M: start 1 on the live copy writes exactly what 0.4.19 writes")
        other = [f for f in fn_ if f[:60] not in ctl_keys and not f.startswith(expected)]
        mn = (list(re.finditer(r"(\d+) checks passed, (\d+) failed", h20["new"])) or [None])[-1]     # the LAST line (H19 prints one too)
        mc_ = (list(re.finditer(r"(\d+) checks passed, (\d+) failed", h20["ctl"])) or [None])[-1]
        check(mn is not None and mc_ is not None and other == [] and int(mn.group(1)) > 40 and int(mc_.group(2)) == 0,
              "H20: the 0.4.20 harness on the 0.4.21 jar fails nothing it does not also fail on the 0.4.20 jar, beyond the version-shape checks: %s | new %s, control %s"
              % (other[:3], mn.group(0) if mn else h20["new"][-800:], mc_.group(0) if mc_ else h20["ctl"][-800:]))
        exp_m = [f for f in fn_ if f.startswith(expected[2])]
        check(all("0.4.21" in f or "V" in f for f in exp_m), "H20: an M difference may only be the version text: %s" % exp_m)
        print("H20. 0.4.20 harness: on the 0.4.21 jar %s, on the 0.4.20 jar %s; extra on 0.4.21 = %s" % (
            mn.group(0) if mn else "?", mc_.group(0) if mc_ else "?", [f[:70] for f in fn_ if f[:60] not in ctl_keys]))

    # ---------------------------------------------------------------- F
    cmpd = json.load(open(cmpo))
    plan = {"SkillDefs": {"methods": ["aliasIdx(Ljava/lang/String;)I", "canonName(Ljava/lang/String;)Ljava/lang/String;", "indexOf(Ljava/lang/String;)I"],
                          "fields": ["ALIAS_FROM:[Ljava/lang/String;", "ALIAS_TO:[I"]},
            "SkillClass": {"methods": ["consistent(Ljava/util/UUID;)Z", "slotOfClass(Ljava/lang/String;)I", "weaponsText(Ljava/lang/String;)Ljava/lang/String;",
                                       "argSlot(Lcom/hypixel/hytale/server/core/universe/PlayerRef;Ljava/lang/String;)I"], "fields": []},
            "OverallCfg": {"methods": ["canonClass(Ljava/lang/String;)Ljava/lang/String;", "checkClasses(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;",
                                       "checkClassBase(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;"], "fields": []},
            "ClassMana": {"methods": ["checkEntry(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;"], "fields": []},   # the unknown-class texts
            "StatsPage": {"methods": ["how(I)Ljava/lang/String;"], "fields": []},                                              # the Combat how-to line
            "Overall": {"methods": ["classOf(Ljava/util/UUID;)Ljava/lang/String;"], "fields": []}}                               # review fix: canonName                                              # the Combat how-to line
    allowed_extra = set()       # the version-only / constructor-text classes do not show here (constructors: code length only)
    bad = {}
    for c, v in cmpd.items():
        if isinstance(v, str):
            bad[c] = v
        elif c in plan:
            if sorted(v["methods"]) != sorted(plan[c]["methods"]) or sorted(v["fields"]) != sorted(plan[c]["fields"]):
                bad[c] = v
        elif c not in allowed_extra or v["fields"]:
            bad[c] = v
    print("F. compare 0.4.20 -> 0.4.21: %s" % json.dumps(cmpd)[:3000])
    check(not bad, "F: 0.4.20 -> 0.4.21 differs only in the planned methods / fields (+ text-only classes): %s" % json.dumps(bad)[:1500])
    jz, jp = zipfile.ZipFile(JAR), zipfile.ZipFile(PREV_JAR)
    other_files = sorted(n for n in set(jz.namelist()) | set(jp.namelist()) if not n.endswith(".class") and n != "manifest.json"
                         and (n not in jz.namelist() or n not in jp.namelist() or jz.read(n) != jp.read(n)))
    check(other_files == [], "F: every asset file byte-identical: %s" % other_files[:3])
    # ---------------------------------------------------------------- AU
    au = json.load(open(auo))
    check(au["refused"] == [] and au["control"] and au["refs"] > 1000, "AU: %d references in %d classes, refused %s; control refused: %s" % (
        au["refs"], au["classes"], au["refused"][:3], bool(au["control"])))
    print("AU. engine-access audit: %d references, %d refused (control refused: %s)" % (au["refs"], len(au["refused"]), bool(au["control"])))
    live_after = dict((os.path.relpath(os.path.join(r, f), LIVE_DIR), os.path.getmtime(os.path.join(r, f))) for r, ds, fs in os.walk(LIVE_DIR) for f in fs)
    check(live_after == live_snap, "the live Skyy_SkyySkills folder was never written")
    return finish()


def finish():
    if not KEEP and GUARD_OK[0]:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    print("%d checks passed, %d failed" % (OKS[0], len(FAILS)))
    for f in FAILS[:60]:
        print("  FAILED:", f)
    print("SkyySkills %s harness:" % VERSION, "PASS" if not FAILS else "FAIL")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
