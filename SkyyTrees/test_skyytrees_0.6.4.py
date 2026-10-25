"""Harness for SkyyTrees 0.6.4 (a capstone at the end of every A1-alt path + the Assassin's second A1-alt Shadow Mark; tools/trees_0_6_4_patch.py
+ tools/trees_v3_data.py r064_apply; pairs with SkyyClasses 0.1.50). Build first:
    python tools/art/make_r064_icons.py --check && python tools/classes_0_1_50_patch.py && python SkyyClasses/build_skyyclasses_0.1.50.py
    python tools/trees_0_6_4_patch.py && python SkyyTrees/build_skyytrees_0.6.4.py
    python SkyyTrees/test_skyytrees_0.6.4.py [--keep] [--expect-dump]
Phases (each its own child JVM, -Xverify:all where classes run; the kit's verify / class compare 0.6.3 -> 0.6.4 / engine-access audit around them):
  static  the generated script = the patch's output (re-run to identical bytes), 0.6.3's patch still regenerates 0.6.3 byte for byte, header /
          version, no new class / system / command, line endings kept
  data    the opt-in rule: WITHOUT r064_apply the class trees dump exactly like the committed (git HEAD) module - both the 0.6.2 base (r062 +
          v4) and the 0.6.3 layout (+ r063): every other build, the 0.6.3 pin too, is unchanged; WITH it: every A1-alt path of every class
          ends in its own capstone in row 6 (+ the trunk capstone where there was one), every path ALONE opens row 6, the moves are exactly
          the planned ones (8 new, 4 moved up, War March 4 -> 5), every 0.6.3 key kept, the Assassin's path B = Shadow Mark (4 modifier
          nodes + 3 passives + Death Sentence); r064 twice = once, after r063 / before v4 refused
  path    EXECUTED (SkyyTrees + SkyyClasses 0.1.50's reader list): every class has two locking paths (TreeV3.CPB, the Assassin too); an
          Assassin takes the Shadow Mark path (Vanishing Act's nodes + Shroud of Night lock, state 8), opens row 6 on that path alone and
          buys Death Sentence (tree:fn:abil: v5 + A4b + f.xSentence); a Warrior on the Challenge path: Oath of Legions locked, Aegis Eternal
          buyable; Warlord's Domain / No Mind / Prism Overload / Holy Land are row-6 capstones now; every new capstone is live (the reader
          list names its code); every layout painted with shipped pictures
  mig     EXECUTED the one-time alt063 update (altKeep) on an Assassin file not updated since 0.6.2: SkyyClasses' old pick "B" is ignored
          for the Assassin (its ranks / Vanishing Act are kept, nothing refunded); a Priest still follows the pick (0.6.3 unchanged)
  jar     the 12 new icon items (art/r064-icons byte for byte + item json + lang), every new node wears its own icon, the row-5 Shadow Mark
          node too; no other non-class entry but the map / icon / lang files
  integ   EXECUTED with the SkyyClasses 0.1.50 jar in the same JVM: its tree:reads lists the 8 new capstone codes + Class.Assassin.A4b;
          an Assassin on the Shadow Mark path -> tree:fn:abil -> SkyyClasses: Shadow Mark's line is on, syncPick = B, Death Sentence's code
          in the cast context
  farm / sap  0.6.3's EXEC phases on the 0.6.4 jar (unchanged behaviour)
  live    start twice on a scratch COPY of the live Skyy_SkyyTrees (+ Skyy_SkyyClasses): every migration in setup's order, every file
          reads, start 2 changes nothing, every player x layout map painted with shipped pictures
NOT COVERED (UNVERIFIED in game): the 2-3 capstones on branch 1's outer ring at 100-200 % zoom (labels), the new icons in the client.
"""
import os, sys, json, subprocess, importlib.util, zipfile, re, shutil, time, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "cap064", "trees")]
import skyybuild as B
import harness_kit as HK

_s = importlib.util.spec_from_file_location("test_skyytrees_0_6_3", os.path.join(HERE, "test_skyytrees_0.6.3.py"))
T63 = importlib.util.module_from_spec(_s)
_argv = list(sys.argv)
_s.loader.exec_module(T63)
sys.argv[:] = _argv
T60 = T63.T60

VERSION = "0.6.4"
PKG = "com.skyy.trees."
CPKG = "com.skyy.classes."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyTrees-0.6.3.jar")
CJAR = os.path.join(ROOT, "SkyyClasses", "SkyyClasses-0.1.50.jar")
GEN = os.path.join(HERE, "build_skyytrees_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyytrees_0.6.3.py")
PATCH = os.path.join(TOOLS, "trees_0_6_4_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
R064 = os.path.join(ROOT, "art", "r064-icons")
T60.JAR = JAR
T60.CJAR = CJAR      # the reader list (tree:reads:SkyyClasses) of SkyyClasses 0.1.50 - it names the new capstone codes
T63.JAR = JAR
T63.CJAR = CJAR
T60.SCRATCH = SCRATCH
T60.VERSION = VERSION
EXPECT = {   # checked 2026-10-24 (the class compare 0.6.3 -> 0.6.4 on the jars without the map / icon / lang entries): the table classes
    # (TreeV3 / TreeMap / TreeClass / TreeSk / TreeData sizes - 15 new nodes, the 12 icons, the moved capstones), NOPICK064 + altKeep's guard,
    # the version strings (CfgFn / CfgRows / SkyyTreesPlugin / TreeCfg)
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'SkyyTreesPlugin': ['~m setup'],
    'TreeCfg': ['~m load'],
    'TreeClass': ['~<clinit>'],
    'TreeData': ['~c '],
    'TreeMap': ['~<clinit>', '~m cand', '~m nodeRow', '~m nodeTv', '~m paint', '~m tex', '~m texRespec'],
    'TreePage': ['~m abClick'],
    'TreeSk': ['~<clinit>'],
    'TreeV3': ['+f NOPICK064', '~<clinit>', '~m buyText', '~m cellSub', '~m count', '~m detCost', '~m detHow', '~m detName', '~m detNeed', '~m detNext', '~m detNow', '~m detState', '~m effText', '~m fxLive', '~m fxNow', '~m live', '~m pathLocked', '~m r3bLive', '~m ustate'],
    'TreeV3Mig': ['~m altKeep', '~m readV3', '~m writeV3'],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
U1 = "64646464-0000-0000-0000-000000000001"   # path: an Assassin
U2 = "64646464-0000-0000-0000-000000000002"   # path: a Warrior
U3 = "64646464-0000-0000-0000-000000000003"   # integ: an Assassin with SkyyClasses
DUMP = r'''
import sys, json
sys.path.insert(0, sys.argv[1])
import trees_v3_data as D
D.V4_MODNAME_SUFFIX = True
D.r062_apply()
D.v4_apply()
if sys.argv[2] == "3":
    D.r063_apply()
print(json.dumps([t for t in D.TREES if t["kind"] == "class"], sort_keys=True))
'''
MOVES = {"Warrior": {("Class.Warrior.x.OathOfLegions", 0, 6, "B")},
         "Berserker": {("Class.Berserker.b2.r3a", 4, 5, "B"), ("Class.Berserker.b2.r6", 5, 6, "B")},
         "Spellblade": {("Class.Spellblade.x.Shatterpoint", 0, 6, "B")},
         "Monk": {("Class.Monk.b3.r6", 5, 6, "B"), ("Class.Monk.x.StormOfFists", 0, 6, "A")},
         "Assassin": {("Class.Assassin.x.ShroudOfNight", 0, 6, "A"), ("Class.Assassin.x.DeathSentence", 0, 6, "B")},
         "Archer": {("Class.Archer.x.Raincaller", 0, 6, "A")},
         "Mage": {("Class.Mage.b2.r6", 5, 6, "B"), ("Class.Mage.x.Supernova", 0, 6, "A")},
         "Priest": {("Class.Priest.b3.r6", 5, 6, "A"), ("Class.Priest.x.SaintsCovenant", 0, 6, "B")}}
NEW_ICONS = ["Skyy_NodeIcon_Archer_B1R6a", "Skyy_NodeIcon_Assassin_B1R2c", "Skyy_NodeIcon_Assassin_B1R3c", "Skyy_NodeIcon_Assassin_B1R5c",
             "Skyy_NodeIcon_Assassin_B1R5Free", "Skyy_NodeIcon_Assassin_B1R6a", "Skyy_NodeIcon_Assassin_B1R6b", "Skyy_NodeIcon_Mage_B1R6a",
             "Skyy_NodeIcon_Monk_B1R6a", "Skyy_NodeIcon_Priest_B1R6b", "Skyy_NodeIcon_Spellblade_B1R6b", "Skyy_NodeIcon_Warrior_B1R6b"]


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyTrees 0.6.4 - build script') and g.count('VERSION = "0.6.4"') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand(", "makeClass("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.check(g.count("V3D.r064_apply()") == 1 and "V3D.r063_apply()" not in g and "r064_apply" not in o, "S r064 is applied by this build only (in place of r063_apply)")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    for patch, ref in ((PATCH, GEN), (os.path.join(TOOLS, "trees_0_6_3_patch.py"), GEN_OLD)):
        cp = os.path.join(d, os.path.basename(ref))
        p = subprocess.run([sys.executable, patch, "--out", cp], capture_output=True, text=True)
        K.check(p.returncode == 0 and open(cp, "rb").read() == open(ref, "rb").read(), "S %s re-generates its script byte for byte: %s" % (os.path.basename(patch), p.stderr[-300:]))
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def _opens6(rows, p):
    """path p alone (trunk + p) opens row 6: rows 1..5 each >= 3 ranks and rows 1..n >= 5 n (the per-branch gates)"""
    cum = 0
    for i in range(1, 6):
        rk = sum(u["max"] for u in rows[i] if u.get("path") in (None, p))
        cum += rk
        if rk < 3 or cum < 5 * i:
            return False
    return True


def run_data(out, jar, scratch, _home):
    K = HK.Child(out)
    hd = os.path.join(scratch, "head")
    os.makedirs(hd, exist_ok=True)
    for m in ("trees_v3_data.py", "trees_v3_effects.py"):
        p = subprocess.run(["git", "show", "HEAD:tools/" + m], capture_output=True, cwd=ROOT)
        K.check(p.returncode == 0, "D git show HEAD:tools/%s" % m)
        open(os.path.join(hd, m), "wb").write(p.stdout)
    for lay, what in (("0", "the 0.6.2 base (r062 + v4)"), ("3", "the 0.6.3 layout (+ r063)")):
        d1 = subprocess.run([sys.executable, "-c", DUMP, TOOLS, lay], capture_output=True, text=True)
        d0 = subprocess.run([sys.executable, "-c", DUMP, hd, lay], capture_output=True, text=True)
        K.check(d1.returncode == 0 and d0.returncode == 0 and d1.stdout == d0.stdout and len(d1.stdout) > 100000,
                "D without r064_apply %s dumps byte-equal to git HEAD (every other build unchanged): %s %s" % (what, d1.stderr[-200:], d0.stderr[-200:]))
    import trees_v3_data as V3D
    V3D.V4_MODNAME_SUFFIX = True
    ok = False
    try:
        V3D.r064_apply()
    except AssertionError:
        ok = True
    K.check(ok and not V3D.R064_APPLIED, "D r064_apply before v4_apply is refused")
    V3D.r062_apply()
    V3D.v4_apply()
    keys3 = {}
    import copy
    V3D.r064_apply()
    V3D.r064_apply()
    K.check(len(V3D.R064_APPLIED) == 1 and len(V3D.R063_APPLIED) == 1, "D r064_apply twice = once (r063 ran once inside it)")
    newk = set(c[2] for c in V3D.R064_CAPS) | set(p["key"] for p in V3D.R064_PASSIVES) | set("Class.Assassin.m.ShadowMark.%s" % m for m in V3D.R064_ALT[3])
    K.eq(len(newk), 8 + 3 + 4, "D 15 new saved keys (8 capstones, 3 Shadow Mark passives, its 4 modifier unlocks)")
    d3 = json.loads(subprocess.run([sys.executable, "-c", DUMP, TOOLS, "3"], capture_output=True, text=True).stdout)
    old = dict((t["name"], dict((u["key"], (bi + 1, r["r"])) for bi, b in enumerate(t["branches"]) for r in b["rows"] for u in r["ups"])) for t in d3)
    for t in V3D.TREES:
        if t["kind"] != "class":
            continue
        cn = t["name"]
        L = V3D.CLASS_LINES[cn]
        paths = ["A", "B"]
        K.check("A4b" in L, "D %s has two A1-alts (%s / %s)" % (cn, L["A4a"], L.get("A4b")))
        b1 = t["branches"][0]["rows"]
        caps = b1[5]["ups"]
        K.check(b1[5]["cap"] and sorted(u.get("path") for u in caps if u.get("path")) == paths and sum(1 for u in caps if not u.get("path")) <= 1
                and all(u["max"] == 1 and u["cost"] == 1 for u in caps),
                "D %s row 6: a capstone per path (+ the trunk one): %s" % (cn, [(u["name"], u.get("path")) for u in caps]))
        rows = dict((r["r"], r["ups"]) for r in b1[:5])
        for p in paths:
            K.check(_opens6(rows, p), "D %s path %s alone opens row 6 (%d ranks with the trunk)" % (cn, p, sum(u["max"] for r in b1[:5] for u in r["ups"] if u.get("path") in (None, p))))
        now = dict((u["key"], (bi + 1, r["r"])) for bi, b in enumerate(t["branches"]) for r in b["rows"] for u in r["ups"])
        K.check(set(old[cn]) <= set(now) and set(now) - set(old[cn]) == set(k for k in newk if k.startswith("Class.%s." % cn)), "D %s: every 0.6.3 key kept, + its new ones" % cn)
        moved = set((k, (old[cn].get(k, (0, 0))[1]), now[k][1], [u.get("path") for b in t["branches"] for r in b["rows"] for u in r["ups"] if u["key"] == k][0])
                    for k in now if old[cn].get(k) != now[k] and not (k.startswith("Class.Assassin.") and k in newk and now[k][1] < 6))
        K.eq(moved, MOVES[cn], "D %s: exactly the planned moves" % cn)
        K.check(all(now[k][0] == old[cn][k][0] for k in old[cn]), "D %s: no node changes branch" % cn)
        for r in b1:
            order = [{"A": 0, None: 1, "B": 2}[u.get("path")] for u in r["ups"]]
            K.check(order == sorted(order), "D %s row %d: path A left, trunk middle, path B right (%s)" % (cn, r["r"], order))
    ab = V3D.tree("Assassin")["branches"][0]["rows"]
    pb = sorted(u["name"] for r in ab for u in r["ups"] if u.get("path") == "B")
    K.eq(pb, sorted(["Death Sentence", "Killing Intent", "Lingering Mark", "Quiet Mark", "Shadow Mark: Duration Modifier", "Shadow Mark: Efficiency Modifier",
                     "Shadow Mark: Power Modifier", "Shadow Mark: Radius Modifier"]), "D the Assassin's Shadow Mark path")
    K.check(ab[4]["free"]["hook"][1:] == ("A4a", "VanishingAct") and ab[4]["free2"]["hook"][1:] == ("A4b", "ShadowMark") and V3D.R063_PATHAB["Assassin"] == ("VanishingAct", "ShadowMark"),
            "D the Assassin's row-5 OR pair: Vanishing Act / Shadow Mark")
    K.check(all(c in V3D.FX_CLASSES for c in V3D.R064_CODES) and V3D.check() and V3D.r064_check(), "D the new codes are known; check + r064_check pass")
    K.save()


def _buyrow(V, T, u, d, ci, keys, K, what):
    for k in keys:
        x = T60._uk(T, ci, k)
        for _i in range(T["UMAX"][x] - int(d.rk[x])):
            m = str(V.buy(u, d, ci, x, False))
            K.check(m.startswith("Done:"), "%s buy %s: %s" % (what, T["UNAME"][x], m[:160]))


def _b1(T, P, ci, row, side):
    return [T["UKEY"][u] for u in range(T["TU0"][ci], T["TU0"][ci] + T["TUN"][ci]) if T["BN"][T["RB"][T["UROW"][u]]] == 1 and T["RNUM"][T["UROW"][u]] == row and P[u] == side]


def _env(scratch, tag, extra):
    from jpype import JClass, JImplements, JOverride
    E, J, V, T = T60._env(scratch, tag, extra)
    Paths, Int = JClass("java.nio.file.Paths"), JClass("java.lang.Integer")
    St, Cfg = J("TreeStore"), J("TreeCfg")
    d0 = os.path.join(scratch, tag)
    os.makedirs(os.path.join(d0, "players"), exist_ok=True)
    St.DIR = Paths.get(os.path.join(d0, "players"))
    Cfg.FILE = Paths.get(os.path.join(d0, "trees.properties"))
    Cfg.load()
    J("TreeSk").loadV3(Paths.get(d0))
    J("TreeSk").reads(True)
    br = St.bridge()
    T60._reads(br)
    br.put("skill:fn:level", T60._fn(JImplements, JOverride, lambda a: Int(60)))
    return E, J, V, T, br, d0


def run_path(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JString
    K = HK.Child(out)
    E, J, V, T, br, d0 = _env(scratch, "pa", [])
    UUID = JClass("java.util.UUID")
    St, TM = J("TreeStore"), J("TreeMap")
    P = [int(x) for x in V.UPATH]
    names = T["TNAME"]
    ai, wi, bi = names.index("Assassin"), names.index("Warrior"), names.index("Berserker")
    K.eq([bool(V.CPB[i]) for i in range(T["NCV"])], [True] * T["NCV"], "PA every class has two A1-alt paths that lock each other (the Assassin too)")
    K.eq([str(V.pathName(ai, 1)), str(V.pathName(ai, 2)), int(V.CSPLIT[ai])], ["Vanishing Act", "Shadow Mark", 3], "PA Assassin: paths Vanishing Act / Shadow Mark, split row 3")
    import trees_v3_data as V3D
    V3D.V4_MODNAME_SUFFIX = True
    V3D.r062_apply(); V3D.v4_apply(); V3D.r064_apply()
    capk = [c[2] for c in V3D.R064_CAPS] + list(V3D.R064_PROMOTE)
    ux = dict((T["UKEY"][u], u) for u in range(T["NU"]) if T["UT"][u] < T["NCV"])
    K.check(all(bool(V.RCAP[T["UROW"][ux[k]]]) and T["RNUM"][T["UROW"][ux[k]]] == 6 and T["BN"][T["RB"][T["UROW"][ux[k]]]] == 1 for k in capk),
            "PA the 8 new + 4 moved capstones sit in branch 1 row 6 (capstone rows)")
    K.check(all(bool(V.live(ux[k])) for k in capk), "PA every new capstone is live (SkyyClasses 0.1.50's reader list names its code)")
    want = {}
    for t in V3D.TREES:
        if t["kind"] == "class":
            for r in t["branches"][0]["rows"]:
                for x in r["ups"]:
                    want[(t["name"], x["key"])] = {"A": 1, "B": 2}.get(x.get("path"), 0)
    got = dict(((names[T["UT"][u]], T["UKEY"][u]), P[u]) for u in range(T["NU"]) if T["UT"][u] < T["NCV"] and T["BN"][T["RB"][T["UROW"][u]]] == 1)
    K.check(got == want, "PA TreeV3.UPATH = the table's path tags (capstones included)")
    # the Assassin takes the Shadow Mark path, opens row 6 alone, buys Death Sentence
    br.put("profile:class:" + U1, "Assassin")
    u = UUID.fromString(U1)
    d = St.data(u)
    _buyrow(V, T, u, d, ai, _b1(T, P, ai, 1, 0) + _b1(T, P, ai, 2, 0), K, "PA Assassin trunk")
    sb = _b1(T, P, ai, 3, 2)
    x = T60._uk(T, ai, sb[0])
    m = str(V.buy(u, d, ai, x, False))
    K.check(m.startswith("Done:") and "You took the Shadow Mark path: the Vanishing Act path is locked until a class-tree respec." in m and int(V.pathOf(d, ai)) == 2,
            "PA the first Shadow Mark node takes the path: %s" % m[:200])
    sh = ux["Class.Assassin.x.ShroudOfNight"]
    ds = ux["Class.Assassin.x.DeathSentence"]
    K.eq(int(V.ustate(d, sh, 60, int(V.spent(d, ai)), V.gatesD(d, ai))), 8, "PA Shroud of Night (the Vanishing Act path's capstone) = state 8 (other path)")
    K.check(not str(V.buy(u, d, ai, sh, False)).startswith("Done:") and int(d.rk[sh]) == 0, "PA ... its buy refused")
    for row in (3, 4, 5):
        _buyrow(V, T, u, d, ai, _b1(T, P, ai, row, 0) + _b1(T, P, ai, row, 2), K, "PA Assassin r%d" % row)
    m = str(V.buy(u, d, ai, ds, False))
    K.check(m.startswith("Done:") and int(d.rk[ds]) == 1, "PA on the Shadow Mark path alone row 6 opens: Death Sentence bought: %s" % m[:160])
    ln = [bool(z_) for z_ in V.lines(d, ai)]
    csv = str(V.classCsv(d, ai))
    K.check(ln[4] and not ln[3] and ",A4b" in csv and ",A4a" not in csv and "f.xSentence=1" in csv and csv.startswith("v3,v4,v5,"),
            "PA Shadow Mark is yours (Vanishing Act not); tree:fn:abil: v5 + A4b + f.xSentence (%s)" % csv[:120])
    K.check(all(int(V.ustate(d, y, 60, int(V.spent(d, ai)), V.gatesD(d, ai))) in (8, 2) for y in range(T["TU0"][ai], T["TU0"][ai] + T["TUN"][ai]) if P[y] == 1),
            "PA every Vanishing Act path node is locked out")
    # a Warrior on the Challenge path: Oath of Legions locked, Aegis Eternal buyable once row 6 opens
    br.put("profile:class:" + U2, "Warrior")
    u2 = UUID.fromString(U2)
    d2 = St.data(u2)
    for row in (1, 2, 3, 4, 5):
        _buyrow(V, T, u2, d2, wi, _b1(T, P, wi, row, 0) + _b1(T, P, wi, row, 1), K, "PA Warrior r%d" % row)
    ol, ae = ux["Class.Warrior.x.OathOfLegions"], ux["Class.Warrior.b1.r6"]
    K.eq(int(V.ustate(d2, ol, 60, int(V.spent(d2, wi)), V.gatesD(d2, wi))), 8, "PA Oath of Legions (Guardian's Oath's capstone) is locked on the Challenge path")
    m = str(V.buy(u2, d2, wi, ae, False))
    K.check(m.startswith("Done:"), "PA Aegis Eternal bought on the Challenge path: %s" % m[:120])
    K.check(T["RNUM"][T["UROW"][ux["Class.Berserker.b2.r6"]]] == 6 and P[ux["Class.Berserker.b2.r6"]] == 2, "PA Warlord's Domain = the Banner path's row-6 capstone")
    z = zipfile.ZipFile(jar)
    pics = set(n.split("/")[-1][:-7] for n in z.namelist() if n.startswith(T60.MAPDIR + "Node/"))
    names_ = set()
    for dd in (d, d2):
        for L in range(T60.NL):
            codes = TM.nodes(L)
            tex = jpype.JArray(JString)(len(codes))
            lit = jpype.JArray(jpype.JBoolean)(len(TM.edges(L)))
            TM.paint(None, dd, L, False, tex, lit)
            names_ |= set(str(x_) for x_ in tex)
    K.check(names_ and names_ <= pics, "PA every layout painted uses shipped pictures (%s)" % sorted(names_ - pics)[:4])
    K.save()
    sys.stdout.flush()
    os._exit(0)


def run_mig(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    E, J, V, T, br, d0 = _env(scratch, "mg", [])
    St, Mig = J("TreeStore"), J("TreeV3Mig")
    import trees_v3_data as V3D
    V3D.V4_MODNAME_SUFFIX = True
    V3D.r062_apply(); V3D.v4_apply(); V3D.r064_apply()
    maxof = dict((T["UKEY"][u], T["UMAX"][u]) for u in range(T["NU"]))
    ai, pi = T["TNAME"].index("Assassin"), T["TNAME"].index("Priest")
    head = "v=3\ntreesV3=1\ngates41=1\nrows52=1\nfold=done\nname=%s\n"

    def old_rows(cn, b, r, path=None):
        tags = dict((x["key"], x.get("path")) for t in V3D.TREES if t["name"] == cn for bb in t["branches"] for rr in bb["rows"] for x in rr["ups"])
        return [k for k, (bo, ro) in sorted(V3D.R063_OLDPOS[cn].items()) if bo == b and ro == r and (path is False or tags.get(k) == path)]
    r1 = [k for k in old_rows("Assassin", 1, 1)]
    lines, n = [], 0
    for k in r1:
        if n >= 6:
            break
        lines.append("%s=%d" % (k, maxof[k]))
        n += maxof[k]
    va = [k for k in old_rows("Assassin", 1, 2, "A")][:1] + [k for k in old_rows("Assassin", 1, 3, "A")][:1]
    K.check(n >= 5 and len(va) >= 1, "MG an Assassin of 0.6.2: old row 1 %d points + Vanishing Act nodes %s" % (n, va))
    p1 = [k for k in old_rows("Priest", 1, 1)]
    plines, pn = [], 0
    for k in p1:
        if pn >= 6:
            break
        plines.append("%s=%d" % (k, maxof[k]))
        pn += maxof[k]
    sa = [k for k in old_rows("Priest", 1, 2, "A")][:1]
    mg = [k for k in old_rows("Priest", 1, 2, "B")][:1] + [k for k in old_rows("Priest", 1, 3, "B")][:1]
    K.check(pn >= 5 and len(sa) == 1 and len(mg) >= 1, "MG a Priest of 0.6.2: old row 1 %d points, Sanctuary %s, Martyr's Grace %s" % (pn, sa, mg))
    files = {"asn": head % "Asn" + "\n".join(lines + ["%s=1" % k for k in va]) + "\n",
             "pri": head % "Pri" + "\n".join(plines + ["%s=1" % k for k in sa + mg]) + "\n"}
    keys = {"asn": "64646464-0000-0000-0000-0000000000a1", "pri": "64646464-0000-0000-0000-0000000000a2"}
    INFO = {keys["asn"]: "alt=B;cls=Assassin", keys["pri"]: "alt=B;cls=Priest"}
    for nm, k in keys.items():
        open(os.path.join(d0, "players", k + ".properties"), "wb").write(files[nm].encode("latin-1"))
    from jpype import JImplements, JOverride
    br.put("class:fn:migInfo", T60._fn(JImplements, JOverride, lambda a: INFO.get(str(a), "")))
    da = St.readFile(keys["asn"])
    ta = open(os.path.join(d0, "players", keys["asn"] + ".properties"), "rb").read().decode("latin-1")
    K.check(not bool(da.bad) and bool(da.a063) and ta.endswith("alt063=done\n"), "MG the Assassin file is updated once (alt063 done)")
    K.check(all(("\n%s=1" % k) in ta for k in va) and "Class.Assassin.gf=A4a" in ta and int(V.pathOf(da, ai)) == 1 and bool(V.lines(da, ai)[3]) and not bool(V.lines(da, ai)[4]),
            "MG the Assassin's old pick B is ignored (it predates Shadow Mark): Vanishing Act's ranks + the alt kept, nothing refunded, path A: %s" % [l for l in ta.split("\n") if ".gf" in l])
    dp = St.readFile(keys["pri"])
    tp = open(os.path.join(d0, "players", keys["pri"] + ".properties"), "rb").read().decode("latin-1")
    K.check(not bool(dp.bad) and "Class.Priest.gf=A4b" in tp and all(("\n%s=" % k) not in tp for k in sa) and all(("\n%s=1" % k) in tp for k in mg),
            "MG a Priest with pick B: Martyr's Grace kept, the Sanctuary ranks refunded (0.6.3's rule unchanged)")
    K.save()
    sys.stdout.flush()
    os._exit(0)


def run_jar(out, jar, scratch, _home):
    K = HK.Child(out)
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    want = set()
    for iid in NEW_ICONS:
        want |= {"Common/Icons/ItemsGenerated/%s.png" % iid, "Server/Item/Items/Utility/%s.json" % iid}
    add = nb - na
    K.check(want <= add and not [n for n in na - nb if not n.startswith(T60.MAPDIR)], "J the 12 new icon items are shipped (png + item json); nothing removed but renumbered map pictures (%d added)" % len(add))
    man = json.load(open(os.path.join(R064, "manifest.json"), encoding="utf8"))
    sha = dict((f["path"], f["sha256"]) for f in man["files"])
    for n_ in man["nodes"]:
        K.check(hashlib.sha256(zb.read(n_["file"])).hexdigest() == sha[n_["file"]], "J %s = the art/r064-icons file" % n_["icon_id"])
    K.check(hashlib.sha256(zb.read("Common/Icons/ItemsGenerated/Skyy_NodeIcon_Assassin_B1R5Free.png")).hexdigest() == sha[man["ability"]["file"]], "J the Shadow Mark row-5 node = the ability picture")
    lang = zb.read("Server/Languages/en-US/server.lang").decode("utf8")
    K.check(all(("items.%s.name=" % i) in lang for i in NEW_ICONS) and "items.Skyy_NodeIcon_Assassin_B1R6b.name=Death Sentence" in lang, "J the icon names in server.lang")
    other = sorted(n for n in add - want if not (n.startswith(T60.MAPDIR) or n.endswith(".class")))
    K.eq(other, [], "J no other new non-class entry (only the map pictures / page data may differ)")
    K.save()


def run_integ(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    E, J, V, T, br, d0 = _env(scratch, "ig", [CJAR])
    C = lambda n: JClass(CPKG + n)
    Paths, UUID = JClass("java.nio.file.Paths"), JClass("java.util.UUID")
    St = J("TreeStore")
    os.makedirs(os.path.join(d0, "cls", "abilities"), exist_ok=True)
    AS, A, AD, UF = C("AbilStore"), C("Abil"), C("AbilDefs"), C("UpFx")
    AS.DIR = Paths.get(os.path.join(d0, "cls", "abilities"))
    br.put("skill:fn:combat", T60._fn(JImplements, JOverride, lambda a: JClass("java.lang.Long")(0)))
    St.FN, St.AFN, St.MFN = J("TreeFn")(), J("TreeAbilFn")(), J("TreeModFn")()
    br.put("tree:fn:level", St.FN)
    br.put("tree:fn:abil", St.AFN)
    br.put("tree:fn:modOwned", St.MFN)
    rd = str(br.get("tree:reads:SkyyClasses"))
    import trees_v3_data as V3D
    K.check(all(("Class.fx." + c_) in rd for c_ in V3D.R064_CODES) and "Class.Assassin.A4b" in rd, "IG SkyyClasses 0.1.50's reader list names the 8 new capstone codes + Class.Assassin.A4b")
    ai = T["TNAME"].index("Assassin")
    br.put("profile:class:" + U3, "Assassin")
    br.put("class:" + U3, "Assassin")
    u = UUID.fromString(U3)
    k3 = str(C("ClassCfg").pkey(u))
    d = St.data(u)
    P = [int(x) for x in V.UPATH]
    for row in (1, 2, 3, 4, 5):
        _buyrow(V, T, u, d, ai, _b1(T, P, ai, row, 0) + _b1(T, P, ai, row, 2), K, "IG Assassin r%d" % row)
    ds = T60._uk(T, ai, "Class.Assassin.x.DeathSentence")
    K.check(str(V.buy(u, d, ai, ds, False)).startswith("Done:"), "IG Death Sentence bought")
    J("TreeFx").refresh(u)
    csv = str(A.treeCsv(u))
    sm = [str(x) for x in AD.IDS].index("ShadowMark")
    ci = int(C("ClassStore").classIndex(u))
    A.syncPick(k3, ci, csv)
    K.check(",A4b" in csv and bool(A.lineOn(csv, sm)) and str(AS.pick(k3)) == "B", "IG through the bridge: Shadow Mark's line is on, syncPick = B (%s)" % csv[:80])
    v = UF.vec(csv)
    K.check(v is not None and bool(UF.has(v, int(UF.idx("xSentence")))) and bool(UF.ON), "IG SkyyClasses reads Death Sentence's code from the tree list")
    # fix round 2 (critic: an owner of a capstone that moved row 5 -> 6 might lose its effect when row 6 needs more points): a Berserker file
    # holding ONLY Warlord's Domain (rank 1, nothing else - row 6 is shut for this file) still has it bought and SkyyClasses still reads xDomain
    U4 = "64646464-0000-0000-0000-000000000004"
    bi = T["TNAME"].index("Berserker")
    br.put("profile:class:" + U4, "Berserker")
    br.put("class:" + U4, "Berserker")
    u4 = UUID.fromString(U4)
    d4 = St.data(u4)
    wd = T60._uk(T, bi, "Class.Berserker.b2.r6")
    d4.rk[wd] = 1
    K.check(int(V.spent(d4, bi)) == 1 and int(d4.rk[wd]) == 1, "IG a 0.6.3 owner of Warlord's Domain alone (1 point spent - row 6 is shut for this file): still bought")
    J("TreeFx").refresh(u4)
    csv4 = str(A.treeCsv(u4))
    v4 = UF.vec(csv4)
    K.check("f.xDomain=1" in csv4 and v4 is not None and bool(UF.has(v4, int(UF.idx("xDomain")))),
            "IG ... its moved capstone still works (SkyyClasses reads xDomain: %s)" % csv4[:120])
    K.save()
    sys.stdout.flush()
    os._exit(0)


HK.run_compare = T60._compare

if __name__ == "__main__":
    HK.run(name="SkyyTrees", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("static", run_static), ("data", run_data), ("path", run_path), ("mig", run_mig), ("jar", run_jar), ("integ", run_integ),
                   ("farm", T63.run_farm), ("sap", T63.run_sap), ("live", T63.run_live)],
           script=__file__, live=(T60.LIVE_DIR, "Skyy_SkyyTrees"))
