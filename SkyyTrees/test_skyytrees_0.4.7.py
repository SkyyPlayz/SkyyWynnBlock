"""Harness for SkyyTrees 0.4.7 (Balance P8c: the Beastmastery tree - points from the Beastmastery skill, 18 SkyyPets rows live; tools/trees_0_4_7_patch.py
+ tools/trees_v3_data.py + tools/trees_v3_effects.py). Build first:
    python tools/trees_0_4_7_patch.py && python SkyyTrees/build_skyytrees_0.4.7.py
    python SkyyTrees/test_skyytrees_0.4.7.py [--keep]
Phases (tools/harness_kit.py, fresh child JVMs, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  S    static   the patch re-runs to identical bytes; line endings kept; no class / system / command added
  A    verify   every class loads + initialises
  C    compare  0.4.6 -> 0.4.7: exactly the planned members (EXPECT)
  OLD  the 0.4.6 jar's TreeV3 tables (dumped in its own JVM)
  DATA vs 0.4.6: no upgrade max / cost / key / name / hook changed; the texts change exactly on the 6 P8C_TEXT upgrades; only the
       Beastmastery gates move (0/0/0/0/0/0 -> 0/5/10/15/20/25) and only rise; R3B unchanged; the budgets (check())
  X    exec     a bare JVM with scratch players: the Beastmastery points = skill:fn:level "Beastmastery" (a stub SkyySkills) + Head Start; the
       level-0 note; the 18 rows live only while tree:reads:SkyyPets lists them (every other Beastmastery upgrade stays coming soon); a
       saved rank answers tree:fn:level; row 2 locked at 4 points spent, open at 5; Pet Dig / Rally Cry still coming soon
  LIVE START TWICE on a scratch COPY of the live Skyy_SkyyTrees folder (setup's update chain + loadV3 + every player file read + derived):
       0.4.7 adds no one-time update; start 2 changes nothing
  AA   engine-access audit
NOT COVERED (UNVERIFIED in game): the page look of the Beastmastery tab with live rows; SkyyPets applies the rows (its own harness).
"""
import os, sys, json, hashlib, subprocess, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "balp8c", "trees")]
import skyybuild as B
import harness_kit as HK
import trees_v3_data as V3D
import trees_v3_effects as V3E

_s = importlib.util.spec_from_file_location("test_skyytrees_0_4_6", os.path.join(HERE, "test_skyytrees_0.4.6.py"))
T46 = importlib.util.module_from_spec(_s)
_argv = list(sys.argv)
_s.loader.exec_module(T46)
sys.argv[:] = _argv

VERSION = "0.4.7"
PKG = "com.skyy.trees."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyTrees-0.4.6.jar")
GEN = os.path.join(HERE, "build_skyytrees_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyytrees_0.4.6.py")
PATCH = os.path.join(TOOLS, "trees_0_4_7_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
LIVE_DIR = T46.LIVE_DIR
ADDED = []
EXPECT = {}
P8C_KEYS = sorted(set(V3E.key(e[0], e[1], e[2]) for e in V3E.EFFECTS if e[0] == "Beastmastery"))
P8C_TEXTK = sorted("Skill." + k for k in V3D.P8C_TEXT)
NEW_NOTE = "Beastmastery points come from the Beastmastery skill - your pets' XP levels it (1 point a level)"
UB = "44444444-4444-4444-4444-444444444444"


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyTrees 0.4.7 - build script') and g.count('VERSION = "0.4.7"') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand(", "makeClass("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def run_old(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, OLD_JAR], verify=False)
    o = T46.dump(JClass(PKG + "TreeV3"))
    json.dump(o, open(os.path.join(scratch, "old046.json"), "w"))
    K.check(len(o["UKEY"]) > 0, "OLD the 0.4.6 tables read (%d upgrades)" % len(o["UKEY"]))
    K.save()


def run_data(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    V = JClass(PKG + "TreeV3")
    o, n = json.load(open(os.path.join(scratch, "old046.json"))), T46.dump(V)
    for t in ("UMAX", "UCOST", "UKEY", "UNAME", "UHK", "UROW", "TU0", "TUN", "TNAME", "RNUM", "RFK", "RFNAME", "RFTEXT", "R3B"):
        K.eq(n[t], o[t], "DATA %s unchanged" % t)
    txt = sorted(n["UKEY"][i] for i in range(len(n["UKEY"])) if n["UTEXT"][i] != o["UTEXT"][i])
    K.eq(txt, P8C_TEXTK, "DATA only the 6 P8C_TEXT texts change (fixer: + Kinship of the Wild; fixer 2: + Gentle Hand)")
    K.eq(n["UTEXT"][n["UKEY"].index("Skill.Beastmastery.b3.r1b")], "+1 Hatchery slot/rank", "DATA fixer 2: Gentle Hand = +1 Hatchery slot a rank")
    K.check(all(n["UTEXT"][n["UKEY"].index("Skill." + k)] == v for k, v in V3D.P8C_TEXT.items()), "DATA the jar's texts = tools/trees_v3_data.py P8C_TEXT")
    moved = []
    for tv in range(len(n["TNAME"])):
        for r in range(1, 7):   # the trees' real rows (slot 7 is never read)
            a, b = o["GATES"][tv * 8 + r], n["GATES"][tv * 8 + r]
            if a != b:
                moved.append((n["TNAME"][tv], r, a, b))
    K.check(all(int(x[3]) > int(x[2]) for x in moved), "DATA a gate only rises")
    K.eq(sorted(moved), [("Beastmastery", r, 0, 5 * (r - 1)) for r in range(2, 7)], "DATA only the Beastmastery gates move: 0/0/0/0/0/0 -> 0/5/10/15/20/25")
    K.check(bool(V3E.check()) and all(V3E.pet_xp(k) <= 0.30 + 1e-9 and V3E.pet_stat(k) <= 0.15 + 1e-9 for k in V3E.PET_KINDS),
            "DATA trees_v3_effects.check(): per pet kind XP <= 30 %, stats <= 15 %")
    K.save()


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JString, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    Paths, UUID = JClass("java.nio.file.Paths"), JClass("java.util.UUID")
    St, Cfg, V = JClass(PKG + "TreeStore"), JClass(PKG + "TreeCfg"), JClass(PKG + "TreeV3")
    d = os.path.join(scratch, "exec")
    os.makedirs(os.path.join(d, "players"), exist_ok=True)
    St.DIR = Paths.get(os.path.join(d, "players"))
    Cfg.FILE = Paths.get(os.path.join(d, "trees.properties"))
    Cfg.load()
    br = St.bridge()
    LEVEL = {"Beastmastery": 0}
    asked = []

    @JImplements("java.util.function.Function")
    class Lv(object):
        @JOverride
        def apply(self, a):
            asked.append(str(a[1]))
            return JClass("java.lang.Integer")(LEVEL.get(str(a[1]), 60))
    br.put("skill:fn:level", Lv())
    tv = [t for t in range(len(V.TNAME)) if str(V.TNAME[t]) == "Beastmastery"][0]
    T46._pfile(d, UB, {})
    u = UUID.fromString(UB)
    data = St.data(u)
    K.check(not bool(data.bad), "X the Beastmastery player file reads")
    K.eq((int(V.points(u, tv)), str(V.note(u, data, tv, 0))), (0, NEW_NOTE), "X Beastmastery level 0: 0 points + the new note")
    LEVEL["Beastmastery"] = 12
    K.check(int(V.level(u, tv)) == 12 and int(V.points(u, tv)) == 12 and "Beastmastery" in asked, "X the Beastmastery tree's points = skill:fn:level Beastmastery (12)")
    K.check(not str(V.note(u, data, tv, 12)).startswith("Beastmastery points"), "X a levelled player sees the normal tree note")
    ui = dict((str(V.UKEY[i]), i) for i in range(len(V.UKEY)))
    bm_all = [k for k in ui if k.startswith("Skill.Beastmastery.")]
    K.check(not any(bool(V.live(ui[k])) for k in P8C_KEYS), "X without tree:reads:SkyyPets the 18 rows are not live (SkyyPets 0.4.8 / none)")
    br.put("tree:reads:SkyyPets", JString(V3E.reads_csv("SkyyPets")))
    K.check(all(bool(V.live(ui[k])) for k in P8C_KEYS) and len(P8C_KEYS) == 18, "X with SkyyPets 0.4.9's tree:reads the 18 rows are live")
    K.check(bool(V.live(ui["Skill.Beastmastery.b3.r1b"])), "X fixer 2: Gentle Hand (+1 Hatchery slot a rank) is live")
    K.check(bool(V.live(ui["Skill.Beastmastery.b3.r6"])) and not bool(V.live(ui["Skill.Beastmastery.b1.r6"])) and not bool(V.live(ui["Skill.Beastmastery.b2.r6"])),
            "X fixer: the bottom capstone Kinship of the Wild (the +% global pet power) is live; Apex Bond / Heart of Stone stay coming soon")
    soon = [k for k in bm_all if k not in P8C_KEYS]
    K.check(len(soon) == len(bm_all) - 18 and not any(bool(V.live(ui[k])) for k in soon), "X the other %d Beastmastery upgrades stay coming soon" % len(soon))
    g = V.gates(tv)
    K.eq([int(g[r]) for r in range(1, 7)], [0, 5, 10, 15, 20, 25], "X the Beastmastery gates 0/5/10/15/20/25")
    T46._pfile(d, UB, {"Skill.Beastmastery.b1.r1a": 4})
    St.DATA.remove(St.pkey(u))
    data = St.data(u)
    sp = int(V.spent(data, tv))
    pb = ui["Skill.Beastmastery.b1.r4b"]
    p2 = ui["Skill.Beastmastery.b2.r1a"]
    K.check(sp == 4 and int(V.skillRank(u, "Skill.Beastmastery.b1.r1a")) == 4, "X a saved Whistle Training 4 answers tree:fn:level 4 (spent 4)")
    K.eq((int(V.ustate(data, p2, 12, sp, g)), int(V.ustate(data, pb, 12, sp, g))), (1, 0), "X with 12 points / 4 spent: Digger's Calling (row 1) buyable, Fang Tempering (row 4) locked")
    K.check(str(V.buyText(data, -1, p2, 1)).startswith("Buy rank 1"), "X the buy text of a live Beastmastery row: %s" % V.buyText(data, -1, p2, 1))
    sd = ui["Skill.Beastmastery.b2.r2a"]
    K.eq(int(V.ustate(data, sd, 12, sp, g)), 4, "X Deeper Dig (needs Pet Dig) stays coming soon (state 4)")
    LEVEL["Beastmastery"] = 0
    K.eq(int(V.points(u, tv)), 0, "X a rebirth (level 0 again) = 0 points (the tree resets with SkyyRebirth's rebirth:part:trees)")
    K.save()


def run_live(out, jar, scratch, home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    fp = os.path.join(home, "trees.properties")
    t0 = open(fp, "rb").read()
    had_eff = os.path.exists(os.path.join(home, "tree-effects.properties"))
    msgs, bad = T46.live_start(home)
    print("   live start 1:", [m[:80] for m in msgs if m])
    po, pn = T46._props(t0), T46._props(open(fp, "rb").read())
    dk = sorted(k for k in set(po) | set(pn) if po.get(k) != pn.get(k))
    K.check(dk in ([], ["Mining.MFortune.per"]), "LIVE start 1: trees.properties changes at most 0.4.5's own TreeMigP5 line (if the live world has not started 0.4.5+ yet): %s" % dk)
    K.check(open(os.path.join(home, "tree-effects.properties"), encoding="latin-1").read() == V3E.cfg_text("SkyyTrees") or had_eff,
            "LIVE tree-effects.properties seeded with 0.4.6's table (unchanged in 0.4.7)")
    K.eq(bad, [], "LIVE every player file reads")
    h1 = T46.tree_hash(home)
    msgs2, bad2 = T46.live_start(home)
    K.check(T46.tree_hash(home) == h1 and bad2 == [], "LIVE start 2 changes nothing")
    K.save()


EXPECT.update({   # checked by hand 2026-10-22: the version texts (CfgFn / CfgRows / setup's ready line / TreeCfg.load's header), TreeV3's tables
                 # (gates + the 5 texts in <clinit>) and the level-0 note
    "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "SkyyTreesPlugin": ["~m setup"], "TreeCfg": ["~m load"], "TreeV3": ["~<clinit>", "~m note"]})

if __name__ == "__main__":
    HK.run(name="SkyyTrees", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("old", run_old), ("data", run_data), ("exec", run_exec), ("live", run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyTrees"))
