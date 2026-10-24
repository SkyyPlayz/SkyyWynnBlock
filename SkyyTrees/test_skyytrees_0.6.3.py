"""Harness for SkyyTrees 0.6.3 (saplings from leaves + replant fixes, the Farming tree = crop Farming, the A1 alts = a late-game either / or;
tools/trees_0_6_3_patch.py + tools/trees_v3_data.py r063_apply; pairs with SkyyClasses 0.1.49). Build first:
    python tools/trees_0_6_3_patch.py && python SkyyTrees/build_skyytrees_0.6.3.py
    python tools/classes_0_1_49_patch.py && python SkyyClasses/build_skyyclasses_0.1.49.py
    python SkyyTrees/test_skyytrees_0.6.3.py [--keep] [--expect-dump]
Phases (each its own child JVM, -Xverify:all where classes run; the kit's verify / class compare 0.6.2 -> 0.6.3 / engine-access audit around them):
  static  the generated script = the patch's output (re-run to identical bytes), 0.6.2's patch still regenerates 0.6.2 byte for byte, header /
          version, one new class (TreeMig063), no new system / command, line endings kept
  data    the opt-in rule: WITHOUT r063_apply the class trees (r062 + v4_apply) dump exactly like the committed (git HEAD) module; WITH it:
          every class tree's branch 1 splits (the alts at row 5, the OR pair; path nodes only from the split row; A on the left / B on the
          right of every ring), each path ALONE opens every row up to its alt (and the capstone's path row 6), every saved key kept, the lent
          passives listed, branches 2 / 3 keep their rules; r063 twice = once, before v4 refused
  path    EXECUTED (SkyyTrees alone, a Priest + an Assassin): the first path node takes the path ("You took the Sanctuary path"), the other
          path's nodes lock (ustate 8, buy refused, the texts), the alt comes with row 5 only on its own path (lines, tree:fn:abil v5 +
          A4a only), the map pictures (yours / the other alt grey / its nodes locked), a respec frees the choice, a rebirth ends kept abilities,
          one-alt classes need no path; every layout painted with shipped pictures
  mig     EXECUTED the one-time alt063 update on crafted profile files: SkyyClasses' pick kept + the other path refunded (History copy byte
          for byte, unchanged lines byte for byte, CRLF kept, Class.<C>.gf, alt063=done, alt-changes.log), the path bought into without a
          pick, an A2-alt the lent passives would close kept (Berserker), the one-alt Assassin kept, waits read-only without SkyyClasses and
          applies once it answers, twice = once, a fresh file needs nothing
  farm    EXECUTED TreeMig063 (the pure step on 6 texts + run() on a scratch trees.properties: History, the change log, only that line) and
          the Farming tree's level = the crop Farming level (TreeCalc.level) unless farming.average is switched on
  sap     EXECUTED the leaf -> sapling table, leafRoll (chance, 0 = off, own island, profile switch), the replant anchor (radius 3, a log of
          the same fall within 1.5 s / 8 blocks joins), planting on soil / beside a stump, every skip reason counted
  integ   EXECUTED with the SkyyClasses 0.1.49 jar in the same JVM (its real bridge functions): tree:fn:abil v5 -> the tree owns the pick,
          class:fn:abilDo alt refused (no swap), syncPick follows the path, the alt's main effect x1.5 (AbilCtx), the growth text
  live    start twice on a scratch COPY of the live Skyy_SkyyTrees (+ Skyy_SkyyClasses for class:fn:migInfo): every migration in setup's
          order incl. TreeMig063 + alt063, every file reads, start 2 changes nothing, every player x layout map painted with shipped pictures
NOT COVERED (UNVERIFIED in game): the split's look on the radial map at 100-200 %, the leaf drop in a real fall (SkyySkills' felled
leaves), planting on a real world section, the panel texts' fit in the client.
"""
import os, sys, json, subprocess, importlib.util, zipfile, re, shutil, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "tree063", "trees")]
import skyybuild as B
import harness_kit as HK

_s = importlib.util.spec_from_file_location("test_skyytrees_0_6_0", os.path.join(HERE, "test_skyytrees_0.6.0.py"))
T60 = importlib.util.module_from_spec(_s)
_argv = list(sys.argv)
_s.loader.exec_module(T60)
sys.argv[:] = _argv

VERSION = "0.6.3"
PKG = "com.skyy.trees."
CPKG = "com.skyy.classes."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyTrees-0.6.2.jar")
CJAR = os.path.join(ROOT, "SkyyClasses", "SkyyClasses-0.1.49.jar")
GEN = os.path.join(HERE, "build_skyytrees_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyytrees_0.6.2.py")
PATCH = os.path.join(TOOLS, "trees_0_6_3_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
T60.JAR = JAR
ADDED = ["TreeMig063"]
EXPECT = {   # checked 2026-10-24 against the harness's class compare 0.6.2 -> 0.6.3 (every member a change of tools/trees_0_6_3_patch.py)
    'CfgFile': ['~<clinit>'],
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'SkyyTreesPlugin': ['~m setup'],
    'TreeCfg': ['+f LEAF_SAP', '~<clinit>', '~m apply', '~m load'],
    'TreeData': ['+f a063'],
    'TreeMap': ['+m altWord', '~<clinit>', '~m abTex', '~m altLabels'],
    'TreePage': ['~m abTag', '~m build', '~m buildK', '~m kSets', '~m pickAlt'],
    'TreeReplant': ['+f LEAF', '+f LEAFDROPS', '+f LSAP', '+f SKIP', '+f SKIPW', '+m beside', '+m counts', '+m find', '+m leaf', '+m leafRoll', '+m leafSap', '+m skip', '-m find', '~<clinit>', '~m note', '~m note2', '~m plant'],   # fix round B4: find / near take the sapling
    'TreeReplantTask': ['+f ax', '+f az', '+f bx0', '+f bx1', '+f bz0', '+f bz1', '+m near', '-m near', '~c ', '~m add'],   # fix round B4: the fall's box, near(.., sap)
    'TreeStore': ['~m readFile'],
    'TreeV3': ['+f ALTROW', '+f CPB', '+f CSPLIT', '+f OLB', '+f OLR', '+f PATHN', '+f UOB', '+f UOR', '+f UPATH', '+m altOk', '+m pathLocked', '+m pathName', '+m pathOf', '+m pathTaken', '~<clinit>', '~m buy', '~m buyText', '~m cellSub', '~m classCsv', '~m detHow', '~m detNeed', '~m detState', '~m lines', '~m rbReset', '~m ustate'],
    'TreeV3Mig': ['+f ALT_APPLIED', '+f ALT_LAST', '+f ALT_LOG', '+f ALT_TOLD', '+f ALT_WAITS', '+m altIn', '+m altKeep', '+m altLocked', '+m altNeedsPick', '+m altQual', '+m altText', '+m altTry', '+m oldOpen', '+m pathRanks', '~<clinit>', '~m fresh', '~m readV3', '~m writeV3'],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
U1 = "63636363-0000-0000-0000-000000000001"   # path: a Priest
U2 = "63636363-0000-0000-0000-000000000002"   # path: an Assassin (one alt)
U3 = "63636363-0000-0000-0000-000000000003"   # integ: a Priest with SkyyClasses
UF = "63636363-0000-0000-0000-0000000000f0"   # farm
DUMP = r'''
import sys, json
sys.path.insert(0, sys.argv[1])
import trees_v3_data as D
D.V4_MODNAME_SUFFIX = True
D.r062_apply()
D.v4_apply()
print(json.dumps([t for t in D.TREES if t["kind"] == "class"], sort_keys=True))
'''


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyTrees 0.6.3 - build script') and g.count('VERSION = "0.6.3"') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.check(g.count("makeClass(") == o.count("makeClass(") + 1 and 'makeClass(PKG + ".TreeMig063")' in g, "S one new class: TreeMig063")
    K.check(g.count("V3D.r063_apply()") == 1 and "r063_apply" not in o, "S r063 is applied by this build only")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    for patch, ref in ((PATCH, GEN), (os.path.join(TOOLS, "trees_0_6_2_patch.py"), GEN_OLD)):
        cp = os.path.join(d, os.path.basename(ref))
        p = subprocess.run([sys.executable, patch, "--out", cp], capture_output=True, text=True)
        K.check(p.returncode == 0 and open(cp, "rb").read() == open(ref, "rb").read(), "S %s re-generates its script byte for byte: %s" % (os.path.basename(patch), p.stderr[-300:]))
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def _ranks_ok(rows, p, cap_side):
    """the per-branch gate rule for path p alone (trunk + p): every row up to the alt (row 5) opens; row 6 too when the capstone is p's / the trunk's"""
    cum = 0
    top = 6 if cap_side in (None, p) else 5
    for i in range(1, top):
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
    d1 = subprocess.run([sys.executable, "-c", DUMP, TOOLS], capture_output=True, text=True)
    d0 = subprocess.run([sys.executable, "-c", DUMP, hd], capture_output=True, text=True)
    K.check(d1.returncode == 0 and d0.returncode == 0 and d1.stdout == d0.stdout and len(d1.stdout) > 100000,
            "D without r063_apply the 8 class trees (r062 + v4) dump byte-equal to git HEAD (every other build unchanged): %s %s" % (d1.stderr[-200:], d0.stderr[-200:]))
    import trees_v3_data as V3D
    V3D.V4_MODNAME_SUFFIX = True
    ok = False
    try:
        V3D.r063_apply()
    except AssertionError:
        ok = True
    K.check(ok and not V3D.R063_APPLIED, "D r063_apply before v4_apply is refused")
    V3D.r062_apply()
    V3D.v4_apply()
    import copy
    keys0 = dict((t["name"], sorted(u["key"] for b in t["branches"] for r in b["rows"] for u in r["ups"])) for t in V3D.TREES if t["kind"] == "class")
    b2w0 = dict((t["name"], [sum(u["max"] for r in b["rows"] for u in r["ups"]) for b in t["branches"]]) for t in V3D.TREES if t["kind"] == "class")
    V3D.r063_apply()
    V3D.r063_apply()
    K.check(len(V3D.R063_APPLIED) == 1, "D r063_apply twice = once")
    for t in V3D.TREES:
        if t["kind"] != "class":
            continue
        cn = t["name"]
        L = V3D.CLASS_LINES[cn]
        b1 = t["branches"][0]["rows"]
        sp = V3D.R063_SPLIT[cn]
        two = "A4b" in L
        K.check(b1[4]["free"]["hook"][1:] == ("A4a", L["A4a"]) and (not two or b1[4]["free2"]["hook"][1:] == ("A4b", L["A4b"])) and all(r["free"] is None for r in b1[1:4]),
                "D %s: the A1-alts are the row-5 OR pair (%s / %s); rows 2-4 hold no free node" % (cn, L["A4a"], L.get("A4b")))
        K.check(all(not u.get("path") or r["r"] >= sp or r["cap"] for r in b1 for u in r["ups"]), "D %s: path nodes only from the split row %d" % (cn, sp))
        for r in b1[:5]:
            order = [{"A": 0, None: 1, "B": 2}[u.get("path")] for u in r["ups"]]
            K.check(order == sorted(order), "D %s row %d: path A left, trunk middle, path B right (%s)" % (cn, r["r"], order))
        rows = dict((r["r"], r["ups"]) for r in b1[:5])
        cap = b1[5]["ups"][0]
        for p in (["A", "B"] if two else ["A"]):
            K.check(_ranks_ok(rows, p, cap.get("path")), "D %s path %s alone opens every row up to its alt%s" % (cn, p, " and the capstone" if cap.get("path") in (None, p) else ""))
        K.eq(sorted(u["key"] for b in t["branches"] for r in b["rows"] for u in r["ups"]), keys0[cn], "D %s: every saved key of the class tree kept" % cn)
        lent = [(k, nm, bf) for k, nm, bf, rf in V3D.R063_LENT.get(cn, []) if "moved up" not in nm]
        K.check(all(any(u["key"] == k for r in b1 for u in r["ups"]) for k, nm, bf in lent), "D %s: the lent passives sit in branch 1 now (%s)" % (cn, [x[1] for x in lent]))
        K.check(all(u.get("hook") and u["hook"][0] == "fx" and V3D._v4_target(u) in ("M", "W") for r in b1 for u in r["ups"] if u["key"] in [x[0] for x in lent]), "D %s: lent = generic passives only" % cn)
        new_w = [sum(u["max"] for r in b["rows"] for u in r["ups"]) for b in t["branches"]]
        K.check(sum(new_w) == sum(b2w0[cn]) and new_w[1] >= 26, "D %s: ranks per branch %s -> %s (the total kept; branch 2 >= 26)" % (cn, b2w0[cn], new_w))
        for p in (["A", "B"] if two else ["A"]):
            K.notes.append("D %s path %s: %d ranks with the trunk (split row %d)" % (cn, p, sum(u["max"] for r in b1[:5] for u in r["ups"] if u.get("path") in (None, p)), sp))
    K.check(V3D.v4_check() and V3D.r063_check(), "D v4_check + r063_check pass")
    K.save()


def _buyrow(V, T, u, d, ci, keys, K, what):
    for k in keys:
        x = T60._uk(T, ci, k)
        for _i in range(T["UMAX"][x] - int(d.rk[x])):
            m = str(V.buy(u, d, ci, x, False))
            K.check(m.startswith("Done:"), "%s buy %s: %s" % (what, T["UNAME"][x], m[:140]))


def _b1(T, P, ci, row, side):
    """saved keys of branch-1 row `row` of class ci on path `side` (0 trunk, 1 A, 2 B)"""
    return [T["UKEY"][u] for u in range(T["TU0"][ci], T["TU0"][ci] + T["TUN"][ci]) if T["BN"][T["RB"][T["UROW"][u]]] == 1 and T["RNUM"][T["UROW"][u]] == row and P[u] == side]


def run_path(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JImplements, JOverride, JString
    K = HK.Child(out)
    E, J, V, T = T60._env(scratch, "pa", [])
    Paths, UUID, Int = JClass("java.nio.file.Paths"), JClass("java.util.UUID"), JClass("java.lang.Integer")
    St, Cfg, TM = J("TreeStore"), J("TreeCfg"), J("TreeMap")
    d0 = os.path.join(scratch, "pa")
    os.makedirs(os.path.join(d0, "players"), exist_ok=True)
    St.DIR = Paths.get(os.path.join(d0, "players"))
    Cfg.FILE = Paths.get(os.path.join(d0, "trees.properties"))
    Cfg.load()
    J("TreeSk").loadV3(Paths.get(d0))
    J("TreeSk").reads(True)
    br = St.bridge()
    T60._reads(br)
    br.put("skill:fn:level", T60._fn(JImplements, JOverride, lambda a: Int(60)))
    P = [int(x) for x in V.UPATH]
    pi, ai = T["TNAME"].index("Priest"), T["TNAME"].index("Assassin")
    K.eq([bool(V.CPB[i]) for i in (pi, ai)], [True, False], "PA Priest has two A1-alts (its paths lock), the Assassin one")
    K.eq([str(V.pathName(pi, 1)), str(V.pathName(pi, 2)), int(V.CSPLIT[pi]), int(V.ALTROW)], ["Sanctuary", "Martyr's Grace", 2, 5], "PA Priest: paths Sanctuary / Martyr's Grace, split row 2, alts at row 5")
    import trees_v3_data as V3D
    V3D.V4_MODNAME_SUFFIX = True
    V3D.r062_apply(); V3D.v4_apply(); V3D.r063_apply()
    want = {}
    for t in V3D.TREES:
        if t["kind"] == "class":
            for r in t["branches"][0]["rows"]:
                for x in r["ups"]:
                    want[(t["name"], x["key"])] = {"A": 1, "B": 2}.get(x.get("path"), 0)
    got = dict(((T["TNAME"][T["UT"][u]], T["UKEY"][u]), P[u]) for u in range(T["NU"]) if T["UT"][u] < T["NCV"] and T["BN"][T["RB"][T["UROW"][u]]] == 1)
    K.check(got == want and sum(1 for v in P if v) == sum(1 for v in want.values() if v), "PA TreeV3.UPATH = the table's path tags (%d path nodes)" % sum(1 for v in P if v))
    br.put("profile:class:" + U1, "Priest")
    u = UUID.fromString(U1)
    d = St.data(u)
    K.check(not bool(d.bad) and bool(d.a063), "PA a fresh file: alt063 done from the start")
    _buyrow(V, T, u, d, pi, _b1(T, P, pi, 1, 0), K, "PA trunk r1")
    a2 = _b1(T, P, pi, 2, 1)
    x = T60._uk(T, pi, a2[0])
    m = str(V.buy(u, d, pi, x, False))
    K.check(m.startswith("Done:") and "You took the Sanctuary path: the Martyr's Grace path is locked until a class-tree respec." in m and int(V.pathOf(d, pi)) == 1,
            "PA the first path node takes the path: %s" % m)
    bx = T60._uk(T, pi, _b1(T, P, pi, 2, 2)[0])
    K.eq(int(V.ustate(d, bx, 60, int(V.spent(d, pi)), V.gatesD(d, pi))), 8, "PA a Martyr's Grace node = state 8 (other path)")
    m = str(V.buy(u, d, pi, bx, False))
    K.check(not m.startswith("Done:") and "is on the Martyr's Grace path - you took the Sanctuary path" in m and int(d.rk[bx]) == 0, "PA buy on the other path refused: %s" % m)
    g = V.gatesD(d, pi)
    sp = int(V.spent(d, pi))
    K.eq([str(V.cellSub(d, bx, 8, g)), str(V.buyText(d, int(T["UROW"][bx]), bx, 8))], ["Other path", "Other path"], "PA cell + button texts")
    K.check(str(V.detState(d, int(T["UROW"][bx]), bx, 8, g, sp, 60)).startswith("Locked - you took the Sanctuary path; a class-tree respec frees the choice")
            and "respec" in str(V.detNeed(d, int(T["UROW"][bx]), bx, 8, g, sp, 60, 60)), "PA panel state / need texts")
    K.check("PATH: it is on the Martyr's Grace path" in str(V.detHow(int(T["UROW"][bx]), bx)), "PA How it works names the path rule")
    K.check(not bool(V.lines(d, pi)[3]), "PA Sanctuary not yet yours (row 5 closed)")
    for row in (2, 3, 4):
        _buyrow(V, T, u, d, pi, _b1(T, P, pi, row, 0) + _b1(T, P, pi, row, 1), K, "PA r%d" % row)
    ln = [bool(x) for x in V.lines(d, pi)]
    K.check(ln[3] and not ln[4], "PA row 5 open on the Sanctuary path: Sanctuary yours, Martyr's Grace not (%s)" % ln)
    csv = str(V.classCsv(d, pi))
    K.check(csv.startswith("v3,v4,v5,") and ",A4a" in csv and ",A4b" not in csv, "PA tree:fn:abil: v5 + A4a only (%s)" % csv[:60])
    # fix round 2 (critic A2): a file waiting for its one-time update sends no A1-alt line (SkyyClasses' syncPick keeps the stored pick)
    a0, w0 = bool(d.a063), bool(d.foldWait)
    d.a063, d.foldWait = False, True
    cw = str(V.classCsv(d, pi))
    d.a063 = True
    cd = str(V.classCsv(d, pi))
    d.a063, d.foldWait = a0, w0
    K.check(",A4a" not in cw and ",A4b" not in cw and ",A1" in cw and ",A4a" in cd, "PA waiting update: no A1-alt line (%s); done: A4a again" % cw[:60])
    NR = int(V.NR)
    rows = [r for r in range(T["TR0"][pi], T["TR0"][pi] + T["TRN"][pi]) if T["RFLINE"][r] == "A4a"]
    r5 = rows[0]
    tA = str(TM.tex(d, -(r5 + 1), 60, int(V.spent(d, pi)), V.gatesD(d, pi), "Pr"))
    tB = str(TM.tex(d, -(NR + r5 + 1), 60, int(V.spent(d, pi)), V.gatesD(d, pi), "Pr"))
    tBn = str(TM.tex(d, bx, 60, int(V.spent(d, pi)), V.gatesD(d, pi), "Pr"))
    K.eq([tA, tB, tBn], ["PrAbilityPicked", "AbilityOther", "Locked"], "PA map: Sanctuary = yours (picked frame), Martyr's Grace = grey (locked out), its nodes Locked")
    K.eq([str(TM.altWord(True, 1, 1)), str(TM.altWord(False, 1, 2)), str(TM.altWord(False, 1, 1)), str(TM.altWord(False, 0, 1))],
         ["ALT - IN USE", "ALT - LOCKED", "ALT - YOUR PATH", "ALT - OR"], "PA the alt label words")
    K.check(str(J("TreePage").abTag("A4b", "MartyrsGrace", False, True)) == "ABILITY 1 ALT - LOCKED (the other path)" and str(J("TreePage").abTag("A4a", "Sanctuary", True, False)).startswith("ABILITY 1 ALT - YOURS"),
            "PA the panel tags")
    # a respec frees the choice
    m = str(V.respec(u, d, pi, True))
    K.check(m.startswith("Respec done") and int(V.pathOf(d, pi)) == 0 and int(V.ustate(d, bx, 60, 0, V.gatesD(d, pi))) != 8, "PA a respec frees the choice: %s" % m)
    _buyrow(V, T, u, d, pi, _b1(T, P, pi, 1, 0), K, "PA again trunk r1")
    m = str(V.buy(u, d, pi, bx, False))
    K.check(m.startswith("Done:") and "You took the Martyr's Grace path" in m and int(V.pathOf(d, pi)) == 2, "PA after the respec the other path can be taken: %s" % m)
    # a rebirth ends the kept abilities (unlocked again by their rows; SkyyClasses keeps the levels)
    d.gfa[pi * 5 + 4] = True
    d.gfa[pi * 5 + 1] = True
    V.rbReset(d)
    K.check(not any(bool(d.gfa[pi * 5 + li]) for li in range(5)) and int(V.spent(d, pi)) == 0 and int(V.pathOf(d, pi)) == 0, "PA rebirth (rbReset): every rank and kept ability ends - the path is free again")
    # the Assassin: one alt, no path to take
    br.put("profile:class:" + U2, "Assassin")
    u2 = UUID.fromString(U2)
    d2 = St.data(u2)
    for row in (1, 2, 3, 4):
        _buyrow(V, T, u2, d2, ai, _b1(T, P, ai, row, 0) + _b1(T, P, ai, row, 1), K, "PA Assassin r%d" % row)
    K.check(bool(V.lines(d2, ai)[3]) and all(int(V.ustate(d2, x, 60, int(V.spent(d2, ai)), V.gatesD(d2, ai))) != 8 for x in range(T["TU0"][ai], T["TU0"][ai] + T["TUN"][ai])),
            "PA Assassin (one alt): Vanishing Act comes with row 5; nothing ever locks (no state 8)")
    z = zipfile.ZipFile(jar)
    pics = set(n.split("/")[-1][:-7] for n in z.namelist() if n.startswith(T60.MAPDIR + "Node/"))
    names = set()
    for dd in (d, d2):
        for L in range(T60.NL):
            codes = TM.nodes(L)
            tex = jpype.JArray(JString)(len(codes))
            lit = jpype.JArray(jpype.JBoolean)(len(TM.edges(L)))
            TM.paint(None, dd, L, False, tex, lit)
            names |= set(str(x) for x in tex)
    K.check(names and names <= pics and "AbilityOther" in pics, "PA every layout painted uses shipped pictures (%s)" % sorted(names - pics)[:4])
    K.save()
    sys.stdout.flush()
    os._exit(0)


def _key_rows(V3D, cn, b, r, path=None):
    """saved keys of class cn whose 0.6.2 place was branch b row r (and, for path, its 0.6.3 path tag)"""
    tags = {}
    for t in V3D.TREES:
        if t["name"] == cn:
            for bb in t["branches"]:
                for rr in bb["rows"]:
                    for x in rr["ups"]:
                        tags[x["key"]] = x.get("path")
    return [k for k, (bo, ro) in sorted(V3D.R063_OLDPOS[cn].items()) if bo == b and ro == r and (path is False or tags.get(k) == path)]


def run_mig(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    E, J, V, T = T60._env(scratch, "mg", [])
    Paths, UUID, Int = JClass("java.nio.file.Paths"), JClass("java.util.UUID"), JClass("java.lang.Integer")
    St, Cfg, Mig = J("TreeStore"), J("TreeCfg"), J("TreeV3Mig")
    d0 = os.path.join(scratch, "mg")
    pdir = os.path.join(d0, "players")
    os.makedirs(pdir, exist_ok=True)
    St.DIR = Paths.get(pdir)
    Cfg.FILE = Paths.get(os.path.join(d0, "trees.properties"))
    Cfg.load()
    J("TreeSk").loadV3(Paths.get(d0))
    J("TreeSk").reads(True)
    br = St.bridge()
    T60._reads(br)
    br.put("skill:fn:level", T60._fn(JImplements, JOverride, lambda a: Int(40)))
    import trees_v3_data as V3D
    V3D.V4_MODNAME_SUFFIX = True
    V3D.r062_apply(); V3D.v4_apply(); V3D.r063_apply()
    maxof = dict((T["UKEY"][u], T["UMAX"][u]) for u in range(T["NU"]))
    pi = T["TNAME"].index("Priest")
    head = "v=3\ntreesV3=1\ngates41=1\nrows52=1\nfold=done\nname=%s\n# a hand comment line\nSkill.Mining.b1.r1a=2\n"
    # PRIEST, had both alts (old branch-1 row 1 >= 5 points + 3 in it), Sanctuary + Martyr's Grace ranks, SkyyClasses pick B
    r1 = _key_rows(V3D, "Priest", 1, 1)
    lines = []
    n = 0
    for k in r1:
        if n >= 6:
            break
        lines.append("%s=%d" % (k, maxof[k]))
        n += maxof[k]
    sa = [k for k in _key_rows(V3D, "Priest", 1, 2, "A")][:2]
    mg = [k for k in _key_rows(V3D, "Priest", 1, 2, "B")][:1] + [k for k in _key_rows(V3D, "Priest", 1, 3, "B")][:1]
    K.check(len(sa) == 2 and len(mg) == 2 and n >= 5, "MG test keys: old row 1 %d points, Sanctuary %s, Martyr's Grace %s" % (n, sa, mg))
    txt_a = head % "PickB" + "\n".join(lines + ["%s=1" % k for k in sa + mg]) + "\n"
    files = {"pickb": txt_a}
    # PRIEST, bought into Martyr's Grace only at old row 1 (Blood Covenant) - no old row 2: the path bought into, no pick needed
    bc = [k for k in _key_rows(V3D, "Priest", 1, 1, "B")]
    K.check(len(bc) >= 1, "MG a Martyr's Grace node sat in old row 1 (%s)" % bc)
    files["bought"] = head % "Bought" + "%s=1\n" % bc[0]
    # BERSERKER, old branch 2 open to row 5 (Earthsplitter) with Adrenaline (lent to branch 1 now): the A2-alt stays (gf A3)
    bz = []
    for r in (1, 2, 3, 4):
        bz += ["%s=%d" % (k, maxof[k]) for k in _key_rows(V3D, "Berserker", 2, r, False)]
    files["berserk"] = head % "Berserk" + "\n".join(bz) + "\n"
    # ASSASSIN, old row 2 open (Vanishing Act had) - the new row 5 is not: kept
    az, n = [], 0
    for k in _key_rows(V3D, "Assassin", 1, 1):
        if n >= 6:
            break
        az.append("%s=%d" % (k, maxof[k]))
        n += maxof[k]
    files["assassin"] = head % "Assn" + "\n".join(az) + "\n"
    # CRLF without a final line ending (pick A)
    files["crlf"] = (head % "Crlf" + "\n".join(lines + ["%s=1" % k for k in sa + mg])).replace("\n", "\r\n")
    # fix round 2 (critic A1): a profile with TWO class trees - Priest (both paths, had) + Mage (had, ranks on path A only); the one
    # SkyyClasses pick (B) belongs to the profile's class: with cls=Priest only the Priest tree takes it, the Mage keeps its path A;
    # without cls= (an older SkyyClasses) two trees need a pick = each keeps the path its ranks show
    m1, n = [], 0
    mb = set(k for r in (1, 2, 3, 4, 5) for k in _key_rows(V3D, "Mage", 1, r, "B"))
    for k in _key_rows(V3D, "Mage", 1, 1, False):   # old row 1 (trunk + path A nodes - never a path B one)
        if n >= 6 or k in mb:
            continue
        m1.append("%s=%d" % (k, maxof[k]))
        n += maxof[k]
    ma = [k for r in (2, 3, 4) for k in _key_rows(V3D, "Mage", 1, r, "A")][:1]
    K.check(len(ma) == 1 and n >= 5, "MG Mage test keys: old row 1 %d points, path A %s" % (n, ma))
    two = head % "TwoCls" + "\n".join(lines + ["%s=1" % k for k in sa + mg] + m1 + ["%s=1" % k for k in ma]) + "\n"
    files["twocls"] = two
    files["twonocls"] = two
    INFO = {}
    keys = {}
    for i, (nm, tx) in enumerate(sorted(files.items())):
        k = "63636363-0000-0000-0000-0000000001%02d" % i
        keys[nm] = k
        open(os.path.join(pdir, k + ".properties"), "wb").write(tx.encode("latin-1"))
    INFO[keys["pickb"]] = "alt=B"
    INFO[keys["crlf"]] = "alt=A"
    INFO[keys["assassin"]] = "alt=A"
    INFO[keys["berserk"]] = "alt=A"
    INFO[keys["twocls"]] = "alt=B;cls=Priest"
    INFO[keys["twonocls"]] = "alt=B"
    # WAITS without SkyyClasses (a pick is needed)
    br.remove("class:fn:migInfo")
    w0 = int(Mig.ALT_WAITS)
    dw = St.readFile(keys["pickb"])
    K.check(bool(dw.bad) and bool(dw.foldWait) and int(Mig.ALT_WAITS) == w0 + 1 and open(os.path.join(pdir, keys["pickb"] + ".properties"), "rb").read() == txt_a.encode("latin-1"),
            "MG without SkyyClasses (a pick needed): the file waits unchanged, read-only")
    db = St.readFile(keys["bought"])
    K.check(not bool(db.bad) and bool(db.a063), "MG no pick needed (bought into one path, no old row 2): runs without SkyyClasses")
    br.put("class:fn:migInfo", T60._fn(JImplements, JOverride, lambda a: INFO.get(str(a), "")))
    out_d = {}
    for nm, k in keys.items():
        out_d[nm] = St.readFile(k)
        K.check(not bool(out_d[nm].bad) and bool(out_d[nm].a063), "MG %s: updated (alt063 done)" % nm)
    # pick B kept, Sanctuary refunded
    d = out_d["pickb"]
    t = open(os.path.join(pdir, keys["pickb"] + ".properties"), "rb").read().decode("latin-1")
    K.check(all(("\n%s=" % k) not in t for k in sa) and all(("\n%s=1" % k) in t for k in mg), "MG pick B: the Sanctuary ranks are gone from the file, Martyr's Grace stays")
    K.check("Class.Priest.gf=A4b\n" in t and t.endswith("alt063=done\n") and int(V.pathOf(d, pi)) == 2 and bool(V.lines(d, pi)[4]) and not bool(V.lines(d, pi)[3]),
            "MG pick B: Martyr's Grace kept (gf A4b) until a respec, path B, Sanctuary not theirs")
    kept = [l for l in txt_a.split("\n") if l and not any(l.startswith(k + "=") for k in sa)]
    K.check(t.split("\n")[:len(kept)] == kept, "MG every other line byte for byte, in its place")
    h = os.path.join(d0, "history", "alt063", keys["pickb"] + ".properties")
    K.check(os.path.isfile(h) and open(h, "rb").read() == txt_a.encode("latin-1"), "MG the History copy = the old file byte for byte")
    lg = open(os.path.join(d0, "alt-changes.log"), encoding="utf-8").read()
    K.check(keys["pickb"] in lg and "Martyr's Grace (the alt in use) kept until a respec" in lg and "refunded" in lg and "Undo:" in lg, "MG alt-changes.log names the case + Undo")
    # bought into B
    t = open(os.path.join(pdir, keys["bought"] + ".properties"), "rb").read().decode("latin-1")
    K.check(("%s=1" % bc[0]) in t and ".gf=" not in t and int(V.pathOf(db, pi)) == 2, "MG bought into Martyr's Grace: kept, nothing refunded, no gf (not had)")
    # Berserker A3 kept
    bi = T["TNAME"].index("Berserker")
    t = open(os.path.join(pdir, keys["berserk"] + ".properties"), "rb").read().decode("latin-1")
    K.check("Class.Berserker.gf=A3" in t and bool(V.lines(out_d["berserk"], bi)[2]), "MG Berserker: Earthsplitter (old branch 2 row 5) kept although Adrenaline moved to branch 1: %s" % [l for l in t.split("\n") if ".gf" in l])
    # Assassin kept
    t = open(os.path.join(pdir, keys["assassin"] + ".properties"), "rb").read().decode("latin-1")
    K.check("Class.Assassin.gf=A4a" in t and bool(V.lines(out_d["assassin"], T["TNAME"].index("Assassin"))[3]), "MG Assassin: Vanishing Act kept (one alt, old row 2 open)")
    # CRLF, pick A
    raw = open(os.path.join(pdir, keys["crlf"] + ".properties"), "rb").read()
    K.check(raw.endswith(b"alt063=done\r\n") and b"\r\n" in raw and b"\n" not in raw.replace(b"\r\n", b"") and int(V.pathOf(out_d["crlf"], pi)) == 1
            and all(("%s=" % k).encode() not in raw for k in mg), "MG CRLF file: its line ending kept, pick A -> the Martyr's Grace ranks refunded")
    # two class trees, one pick
    mi = T["TNAME"].index("Mage")
    t = open(os.path.join(pdir, keys["twocls"] + ".properties"), "rb").read().decode("latin-1")
    K.check("Class.Priest.gf=A4b" in t and all(("\n%s=" % k) not in t for k in sa) and ("\n%s=1" % ma[0]) in t and int(V.pathOf(out_d["twocls"], mi)) == 1
            and "Class.Mage.gf=A4a" in t, "MG cls=Priest: the pick B goes to the Priest tree only - the Mage keeps its path A ranks: %s" % [l for l in t.split("\n") if ".gf" in l])
    t = open(os.path.join(pdir, keys["twonocls"] + ".properties"), "rb").read().decode("latin-1")
    K.check(("\n%s=1" % ma[0]) in t and int(V.pathOf(out_d["twonocls"], mi)) == 1 and "Class.Mage.gf=A4a" in t,
            "MG no cls= and two trees needing a pick: the pick goes to neither - the Mage keeps path A (its ranks)")
    # twice = once
    before = dict((nm, open(os.path.join(pdir, k + ".properties"), "rb").read()) for nm, k in keys.items())
    St.DATA.clear()
    a0 = int(Mig.ALT_APPLIED)
    for nm, k in keys.items():
        St.readFile(k)
    K.check(int(Mig.ALT_APPLIED) == a0 and all(open(os.path.join(pdir, k + ".properties"), "rb").read() == before[nm] for nm, k in keys.items()), "MG a second read changes nothing")
    # the pure step: no change = alt063=done only
    dd = J("TreeData")()
    dd.v3 = True
    ch = Mig.altKeep(dd, "", JClass("java.util.ArrayList")(), JClass("java.lang.StringBuilder")())
    K.check(not any(bool(x) for x in ch) and bool(dd.a063), "MG an empty tree: nothing to keep")
    K.save()
    sys.stdout.flush()
    os._exit(0)


def run_farm(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    E, J, V, T = T60._env(scratch, "fa", [])
    Paths, UUID, Int = JClass("java.nio.file.Paths"), JClass("java.util.UUID"), JClass("java.lang.Integer")
    St, Cfg, M63, Calc = J("TreeStore"), J("TreeCfg"), J("TreeMig063"), J("TreeCalc")
    K.check("farming.average=false" in str(Cfg.DEFAULTS) and str(M63.MK) in str(Cfg.DEFAULTS) and "trees.leafSaplingPct=2.5" in str(Cfg.DEFAULTS), "FA a new server's file: farming.average=false + the marker + trees.leafSaplingPct=2.5")
    old = "# head\nfarming.average=true\ntrees.replant=true\n"
    r = M63.m063Update(old)
    K.check(r is not None and str(r[0]).startswith("# head\nfarming.average=false\ntrees.replant=true\n") and str(M63.MK) in str(r[0]) and [str(x) for x in r[1]] == ["farming.average", "true", "false"],
            "FA the old default true -> false (+ the marker, one change row)")
    r = M63.m063Update("farming.average=TRUE\r\n")
    K.check(r is not None and str(r[0]).startswith("farming.average=false\r\n") and str(r[0]).endswith("\r\n"), "FA TRUE counts as the old default; CRLF kept")
    r = M63.m063Update("farming.average=false\n")
    K.check(r is not None and len(r[1]) == 0 and "farming.average=false\n" in str(r[0]), "FA already false: nothing moves (marker only)")
    r = M63.m063Update("x=1\n")
    K.check(r is not None and len(r[1]) == 0, "FA no line: the new built-in default applies, nothing rewritten")
    r = M63.m063Update("farming.average=true\nfarming.average=true\n")
    K.check(r is not None and len(r[1]) == 0 and len(r[2]) == 1, "FA a doubled line is kept + named")
    r = M63.m063Update("# " + str(M63.MK) + "\nfarming.average=true\n")
    K.check(r is None, "FA the marker = never again")
    base = os.path.join(scratch, "fa", "base")
    os.makedirs(base, exist_ok=True)
    tp = os.path.join(base, "trees.properties")
    src = str(Cfg.DEFAULTS).replace("farming.average=false", "farming.average=true").replace(str(M63.MK), "an older marker").encode("latin-1")
    open(tp, "wb").write(src)
    Cfg.FILE = Paths.get(tp)
    Cfg.load()
    K.check(bool(Cfg.FARM_AVG), "FA the old file reads the average (true) before the update")
    J("TreeMig").mgKit(Paths.get(base))
    msg = str(M63.run(Paths.get(base)))
    t = open(tp, "rb").read()
    want = src.replace(b"farming.average=true", b"farming.average=false") + str(M63.MARK_LINE).encode("latin-1") + b"\n"
    K.check("farming.average" in msg and not bool(Cfg.FARM_AVG) and t == want, "FA run(): only the farming.average line moved + the marker appended; TreeCfg reads false: %s" % msg[:160])
    hist = os.path.join(base, "config-history")
    K.check(os.path.isdir(hist) and any(open(os.path.join(dp, f), "rb").read() == src for dp, _dn, fs in os.walk(hist) for f in fs), "FA the History copy = the old file")
    K.check(str(M63.run(Paths.get(base))) == "", "FA run() twice = once")
    # the Farming tree's level
    br = St.bridge()
    LV = {"Farming": 16, "farmingavg": 5, "Ranching": 1, "Orchard": 0}
    br.put("skill:fn:level", T60._fn(JImplements, JOverride, lambda a: Int(LV.get(str(a[1]), 0))))
    br.put("skill:farmavg:" + UF, Int(5))
    u = UUID.fromString(UF)
    tf = [str(x) for x in J("TreeDefs").TREES].index("Farming")
    K.eq(int(Calc.level(u, tf)), 16, "FA Farming tree level = the crop Farming level (16), not the average (5)")
    Cfg.FARM_AVG = True
    K.eq(int(Calc.level(u, tf)), 5, "FA farming.average switched on: the average again")
    Cfg.FARM_AVG = False
    fv = [str(x) for x in V.TNAME].index("Farming")
    K.eq(int(V.points(u, fv)), 16, "FA the Farming tree's points = 16 (1 a level)")
    K.save()


def run_sap(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    E, J, V, T = T60._env(scratch, "sa", [])
    Paths, UUID, Sys = JClass("java.nio.file.Paths"), JClass("java.util.UUID"), JClass("java.lang.System")
    St, Cfg, R, Task = J("TreeStore"), J("TreeCfg"), J("TreeReplant"), J("TreeReplantTask")
    d0 = os.path.join(scratch, "sa")
    os.makedirs(d0, exist_ok=True)
    Cfg.FILE = Paths.get(os.path.join(d0, "trees.properties"))
    Cfg.load()
    K.check(abs(float(Cfg.LEAF_SAP) - 2.5) < 1e-12, "SA trees.leafSaplingPct default 2.5 %")
    lm = {"Plant_Leaves_Oak": "Plant_Sapling_Oak", "Plant_Leaves_Fir": "Plant_Sapling_Spruce", "Plant_Leaves_Fir_Snow": "Plant_Sapling_Spruce_Frozen",
          "Plant_Leaves_Goldentree": "Plant_Sapling_Amber", "Plant_Leaves_Bottle": "Plant_Sapling_Gumboab", "Plant_Leaves_Palm_Arid": "Plant_Sapling_Palm",
          "Plant_Leaves_Burnt": None, "Plant_Leaves_Jungle_Floor": None, "Plant_Leaves_Snow": None, "Plant_Leaves_Nope": None, "Wood_Oak_Trunk": None}
    got = dict((k, (None if R.leafSap(k) is None else str(R.leafSap(k)))) for k in lm)
    K.eq(got, lm, "SA leafSap: the build-time leaf -> sapling table")
    u = UUID.fromString("63636363-0000-0000-0000-0000000000a1")
    Cfg.LEAF_SAP = 100.0
    K.check(bool(R.leafRoll(u, "w", "Plant_Leaves_Oak")) and not bool(R.leafRoll(u, "w", "Plant_Leaves_Burnt")), "SA leafRoll at 100 %: a sapling leaf rolls, Burnt never")
    Cfg.LEAF_SAP = 0.0
    K.check(not bool(R.leafRoll(u, "w", "Plant_Leaves_Oak")), "SA 0 % = off")
    Cfg.LEAF_SAP = 100.0
    St.bridge().put("profile:busy:" + str(u), JClass("java.lang.Boolean").TRUE)
    K.check(not bool(R.leafRoll(u, "w", "Plant_Leaves_Oak")), "SA never while the profile switches")
    St.bridge().remove("profile:busy:" + str(u))
    Cfg.REPLANT_ISLAND = True
    K.check(not bool(R.leafRoll(u, "w", "Plant_Leaves_Oak")), "SA replantWhere island + no island here = no leaf sapling")
    Cfg.REPLANT_ISLAND = False
    n, hit = 4000, 0
    Cfg.LEAF_SAP = 2.5
    for _i in range(n):
        if bool(R.leafRoll(u, "w", "Plant_Leaves_Birch")):
            hit += 1
    K.check(40 <= hit <= 170, "SA 2.5 %% a leaf: %d of %d rolls (~100)" % (hit, n))
    # the anchor
    TB = JClass("java.util.concurrent.ConcurrentHashMap")()
    R.TEST_BLOCKS = TB
    R.PEND.clear()
    g = Task(None, "w", u, 0, 70, 0, "Plant_Sapling_Oak")
    K.check(bool(R.keep(g)), "SA a pending replant")
    OAK = "Plant_Sapling_Oak"
    K.check(R.find("w", u, 2, -3, OAK) == g, "SA a log 3 away joins")
    K.check(R.find("w", u, 2, -3, "Plant_Sapling_Birch") is None, "SA fix B4: another kind of tree 3 away never joins")
    K.check(R.find("w", u, 4, 0, OAK) is None and R.find("w", u, 6, 0, OAK) is None, "SA fix B4: logs 4 / 6 away within 1.5 s but not next to the fall's logs (a second tree cut right after) get their own")
    g.add(1, 71, 0)
    K.check(R.find("w", u, 4, 0, OAK) == g, "SA a log 4 away of the same fall (within 1.5 s, next to its logs - SkyySkills reports a fall in BFS order) joins")
    g.add(3, 74, 0)
    K.check(int(g.bx0) == 0 and int(g.bx1) == 3 and int(g.y) == 70, "SA fix B4: a joined branch log widens the box, the plant spot stays on the lowest log")
    K.check(R.find("w", u, 6, 0, OAK) == g and R.find("w", u, 7, 0, OAK) is None, "SA fix B4: the crown grows outward (6 joins after a log at 3; 7 never)")
    g.last = Sys.currentTimeMillis() - 5000
    K.check(R.find("w", u, 2, 2, OAK) == g and R.find("w", u, 4, 0, OAK) is None, "SA later: radius 3 of the FIRST log only (a close second tree gets its own)")
    g.add(1, 68, 1)
    K.check(int(g.ax) == 0 and int(g.az) == 0 and int(g.y) == 68 and int(g.x) == 1, "SA the anchor stays on the first log; the plant spot follows the lowest log")
    # fix B2: the 2.5 % roll comes BEFORE the island lookup (trees.replantWhere=island: one bridge call per leaf only on a win)
    calls = [0]

    def _role(a):
        calls[0] += 1
        return None
    oldrole = St.bridge().get("island:role:fn")
    St.bridge().put("island:role:fn", T60._fn(JImplements, JOverride, _role))
    Cfg.REPLANT_ISLAND = True
    Cfg.LEAF_SAP = 0.0001
    for _i in range(300):
        R.leafRoll(u, "w", "Plant_Leaves_Oak")
    lost = calls[0]
    Cfg.LEAF_SAP = 100.0
    R.leafRoll(u, "w", "Plant_Leaves_Oak")
    K.check(lost <= 2 and calls[0] >= lost + 1, "SA fix B2: 300 losing leaf rolls made %d island lookups; a winning one asks the island (%d)" % (lost, calls[0] - lost))
    Cfg.REPLANT_ISLAND = False
    Cfg.LEAF_SAP = 2.5
    if oldrole is None:
        St.bridge().remove("island:role:fn")
    else:
        St.bridge().put("island:role:fn", oldrole)
    R.PEND.clear()

    def task(y=70):
        return Task(None, "w", u, 0, y, 0, "Plant_Sapling_Oak")

    def skips():
        return [int(x) for x in R.SKIP]
    s0 = skips()
    p0 = int(R.PLANTED)
    TB.clear()
    TB.put("0|69|0", "Soil_Grass")
    K.check(bool(R.plant(task())) and str(TB.get("0|70|0")) == "Plant_Sapling_Oak" and int(R.PLANTED) == p0 + 1, "SA planted on the soil under the lowest log")
    TB.clear()
    TB.put("0|69|0", "Wood_Oak_Trunk")
    TB.put("0|68|0", "Wood_Oak_Trunk")
    TB.put("0|67|0", "Soil_Grass")
    TB.put("0|67|-1", "Soil_Grass")
    K.check(bool(R.plant(task())) and str(TB.get("0|68|-1")) == "Plant_Sapling_Oak", "SA a stump (mid-trunk cut): planted beside it at its ground level")
    TB.clear()
    TB.put("0|69|0", "Wood_Oak_Trunk")
    TB.put("0|68|0", "Rock_Stone")
    for dx, dz in ((0, -1), (1, 0), (0, 1), (-1, 0), (1, -1), (1, 1), (-1, 1), (-1, -1)):
        TB.put("%d|68|%d" % (dx, dz), "Rock_Stone")
    K.check(not bool(R.plant(task())) and skips()[0] == s0[0] + 1, "SA a stump with no soil around: skipped (stump)")
    TB.clear()
    TB.put("0|69|0", "Rock_Stone")
    K.check(not bool(R.plant(task())) and skips()[1] == s0[1] + 1, "SA stone under the log: skipped (not soil)")
    TB.clear()
    TB.put("0|69|0", "Soil_Grass")
    TB.put("0|70|0", "Plant_Grass_Tall")
    K.check(not bool(R.plant(task())) and skips()[2] == s0[2] + 1, "SA something above the soil: skipped (blocked)")
    R.TEST_BLOCKS = None
    K.check(not bool(R.plant(task())) and skips()[3] == s0[3] + 1, "SA no world / section: skipped (unloaded)")
    c = str(R.counts())
    K.check(c.startswith("planted ") and "stump 1" in c and "not soil 1" in c and "blocked 1" in c and "unloaded 1" in c, "SA the log line's totals: %s" % c)
    K.save()


def run_integ(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    E, J, V, T = T60._env(scratch, "ig", [CJAR])
    C = lambda n: JClass(CPKG + n)
    Paths, UUID, Int = JClass("java.nio.file.Paths"), JClass("java.util.UUID"), JClass("java.lang.Integer")
    St, Cfg, TM, TC, Pg = J("TreeStore"), J("TreeCfg"), J("TreeMap"), J("TreeClass"), J("TreePage")
    d0 = os.path.join(scratch, "ig")
    os.makedirs(os.path.join(d0, "players"), exist_ok=True)
    os.makedirs(os.path.join(d0, "cls", "abilities"), exist_ok=True)
    St.DIR = Paths.get(os.path.join(d0, "players"))
    Cfg.FILE = Paths.get(os.path.join(d0, "trees.properties"))
    Cfg.load()
    J("TreeSk").loadV3(Paths.get(d0))
    J("TreeSk").reads(True)
    br = St.bridge()
    T60._reads(br)
    AS, A, AD = C("AbilStore"), C("Abil"), C("AbilDefs")
    AS.DIR = Paths.get(os.path.join(d0, "cls", "abilities"))
    br.put("skill:fn:level", T60._fn(JImplements, JOverride, lambda a: Int(60)))
    br.put("skill:fn:combat", T60._fn(JImplements, JOverride, lambda a: JClass("java.lang.Long")(0)))
    for k, cn in (("class:fn:abilPanel", "AbilPanelFn"), ("class:fn:abilMods", "AbilModsFn"), ("class:fn:abilDo", "AbilDoFn"), ("class:fn:migInfo", "AbilMigFn"),
                  ("class:fn:altPick", "AbilAltFn"), ("class:fn:abilDoes", "AbilDoesFn")):
        br.put(k, C(cn)())
    St.FN, St.AFN, St.MFN = J("TreeFn")(), J("TreeAbilFn")(), J("TreeModFn")()
    br.put("tree:fn:level", St.FN)
    br.put("tree:fn:abil", St.AFN)
    br.put("tree:fn:modOwned", St.MFN)
    pi = T["TNAME"].index("Priest")
    br.put("profile:class:" + U3, "Priest")
    br.put("class:" + U3, "Priest")
    u = UUID.fromString(U3)
    ci = int(C("ClassStore").classIndex(u))
    K.check(ci >= 0, "IG SkyyClasses sees a Priest")
    k3 = str(C("ClassCfg").pkey(u))
    AS.set(k3, jpype.JArray(jpype.JString)(["alt"]), jpype.JArray(jpype.JString)(["B"]))   # SkyyClasses' old pick: Martyr's Grace
    d = St.data(u)
    P = [int(x) for x in V.UPATH]
    for row in (1, 2, 3, 4):
        _buyrow(V, T, u, d, pi, _b1(T, P, pi, row, 0) + _b1(T, P, pi, row, 1), K, "IG r%d" % row)
    J("TreeFx").refresh(u)
    csv = str(A.treeCsv(u))
    K.check(csv.startswith("v3,v4,v5,") and ",A4a" in csv and ",A4b" not in csv, "IG tree:fn:abil through the bridge: v5 + Sanctuary only (%s)" % csv[:70])
    K.check(bool(A.treeOwnsPick(u)), "IG v5: the tree owns the Ability 1 alt (no pick on /cast)")
    r = str(A.altSwitch(u, "B", csv))
    K.check(r.startswith("-Your Ability 1 alt is the end of the path you took in your class tree") and "respec" in r, "IG class:fn:abilDo alt refused - no swap: %s" % r)
    r = str(TC.ado(u, "alt", "B", "", csv))
    K.check(r.startswith("-Your Ability 1 alt is the end of the path"), "IG the same through class:fn:abilDo: %s" % r[:80])
    A.syncPick(k3, ci, csv)
    K.eq(str(AS.pick(k3)), "A", "IG syncPick follows the path: SkyyClasses' pick B -> A (Sanctuary)")
    ids = [str(x) for x in AD.IDS]
    sh, sc, mg = ids.index("SacredHeal"), ids.index("Sanctuary"), ids.index("MartyrsGrace")
    K.eq([float(AD.altMult(sh)), float(AD.altMult(sc)), float(AD.altMult(mg))], [1.0, 1.5, 1.5], "IG altMult: Sacred Heal x1, Sanctuary / Martyr's Grace x1.5")
    c1, c2 = A.ctxFor(u, k3, sh, 0, csv), A.ctxFor(u, k3, sc, 0, csv)
    K.check(abs(float(c2.main) / float(c2.base) / float(c2.treeMain) - 1.5) < 1e-9 and abs(float(c1.main) / float(c1.base) / float(c1.treeMain) - 1.0) < 1e-9,
            "IG the cast context: Sanctuary's main effect x1.5 over its level / tree (%s), Sacred Heal x1 (%s)" % (float(c2.main), float(c1.main)))
    e2 = c2.echoOf(0.3)
    K.check(abs(float(e2.main) - float(c2.base) * float(c2.treeMain) * 0.3 * 1.5) < 1e-9, "IG the echo of an alt keeps the x1.5")
    C("AbilCfg").ALT_POW = 0.0
    K.eq(float(AD.altMult(sc)), 1.0, "IG abil.altPower 0 = no bonus")
    C("AbilCfg").ALT_POW = 50.0
    info = [str(x) for x in C("AbilDoes").info("Sanctuary")]
    K.check("Ability 1 alt: +50 %" in info[3] and "keeps the levels" in info[3] and "Ability 1 alt" not in [str(x) for x in C("AbilDoes").info("SacredHeal")][3], "IG growth texts: %s" % info[3][-120:])
    # the page: Learn on the Martyr's Grace node explains the path (no Classes call)
    pg = Pg(E.player(uid=u, name="SkyyPath").pr, int(J("TreeDefs").NT))
    rA = [r_ for r_ in range(T["TR0"][pi], T["TR0"][pi] + T["TRN"][pi]) if T["RFLINE"][r_] == "A4a"][0]
    m = str(pg.pickAlt(u, d, -(int(V.NR) + rA + 1)))
    K.check("is the end of the Martyr's Grace path" in m and str(AS.pick(k3)) == "A", "IG Learn on the other alt: the path rule, nothing switched: %s" % m)
    K.save()
    sys.stdout.flush()
    os._exit(0)


def run_live(out, jar, scratch, home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar, CJAR], verify=True)
    import jpype
    from jpype import JClass, JString
    J = lambda n: JClass(PKG + n)
    Paths = JClass("java.nio.file.Paths")
    cls = os.path.join(os.path.dirname(home), "Skyy_SkyyClasses")
    if os.path.isdir(T60.LIVE_CLS):
        shutil.copytree(T60.LIVE_CLS, cls)
        JClass(CPKG + "AbilStore").DIR = Paths.get(os.path.join(cls, "abilities"))
        J("TreeStore").bridge().put("class:fn:migInfo", JClass(CPKG + "AbilMigFn")())
    t0 = open(os.path.join(home, "trees.properties"), "rb").read()

    def start():
        J("TreeStore").DIR = Paths.get(os.path.join(home, "players"))
        J("TreeCfg").FILE = Paths.get(os.path.join(home, "trees.properties"))
        J("TreeStore").DATA.clear()
        J("TreeCfg").load()
        bp = Paths.get(home)
        msgs = [str(J(m).run(bp)) for m in ("TreeMig", "TreeMig32", "TreeMig33", "TreeMig317", "TreeMig321", "TreeMig323", "TreeMig324", "TreeMigP5", "TreeMigP7", "TreeMig052", "TreeMig063")]
        J("TreeSk").loadV3(bp)
        bad, ds = [], {}
        for f in sorted(os.listdir(os.path.join(home, "players"))):
            if f.endswith(".properties"):
                dd = J("TreeStore").readFile(f[:-11])
                if bool(dd.bad):
                    bad.append(f)
                ds[f[:-11]] = dd
        return msgs, bad, ds
    msgs, bad, ds = start()
    K.eq(bad, [], "LIVE every player file reads")
    K.check(all(bool(dd.fold) and bool(dd.a063) for dd in ds.values()), "LIVE every file is folded + A1-alt updated")
    t1 = open(os.path.join(home, "trees.properties"), "rb").read()
    K.check((b"farming.average=true" not in t0) or (b"farming.average=false" in t1 and not bool(J("TreeCfg").FARM_AVG)), "LIVE TreeMig063: farming.average true -> false (%s)" % msgs[-1][:160])
    K.notes.append("LIVE TreeMig063: %s" % msgs[-1][:300])
    K.notes.append("LIVE alt063 applied %d, waits %d, last %s" % (int(J("TreeV3Mig").ALT_APPLIED), int(J("TreeV3Mig").ALT_WAITS), str(J("TreeV3Mig").ALT_LAST)[:300]))
    lg = os.path.join(home, "alt-changes.log")
    if os.path.isfile(lg):
        for ln in open(lg, encoding="utf-8").read().splitlines():
            K.notes.append("LIVE alt-changes.log: " + ln[:400])
    h1 = T60.T46.tree_hash(home)
    msgs2, bad2, _ds = start()
    K.check(T60.T46.tree_hash(home) == h1 and bad2 == [] and all(m == "" for m in msgs2), "LIVE start 2 changes nothing")
    TM, St = J("TreeMap"), J("TreeStore")
    z = zipfile.ZipFile(jar)
    pics = set(n.split("/")[-1][:-7] for n in z.namelist() if n.startswith(T60.MAPDIR + "Node/"))
    names, painted = set(), 0
    for k in ds:
        dd = St.readFile(k)
        for L in range(T60.NL):
            codes = TM.nodes(L)
            tex = jpype.JArray(JString)(len(codes))
            lit = jpype.JArray(jpype.JBoolean)(len(TM.edges(L)))
            TM.paint(None, dd, L, False, tex, lit)
            names |= set(str(x) for x in tex)
            painted += 1
    K.check(painted > 0 and names <= pics, "LIVE %d live player x layout maps painted, every picture shipped (%s)" % (painted, sorted(names - pics)[:4]))
    K.save()
    sys.stdout.flush()
    os._exit(0)


HK.run_compare = T60._compare

if __name__ == "__main__":
    HK.run(name="SkyyTrees", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("data", run_data), ("path", run_path), ("mig", run_mig), ("farm", run_farm), ("sap", run_sap),
                   ("integ", run_integ), ("live", run_live)],
           script=__file__, live=(T60.LIVE_DIR, "Skyy_SkyyTrees"))
