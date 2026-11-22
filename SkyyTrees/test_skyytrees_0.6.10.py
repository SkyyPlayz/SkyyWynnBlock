"""Harness for SkyyTrees 0.6.10 (THE SKILL TREE ON EVERY SKILL PAGE - the SkyyTrees half: tree:fn:map + tree:fn:act, class TreeLineFn;
tools/trees_0_6_10_patch.py, round treemap1, with SkyyMenu 0.3.61).
Build first:
    python tools/trees_0_6_10_patch.py && python SkyyTrees/build_skyytrees_0.6.10.py
    python tools/menu_0_3_61_patch.py && python SkyyMenu/build_skyymenu_0.3.61.py      (the inline phase draws with the real SkyyMenu 0.3.61)
    python SkyyTrees/test_skyytrees_0.6.10.py [--keep] [--expect-dump] [--base <folder holding the older jars>]
Phases (each its own child JVM, -Xverify:all where classes run; the kit's verify / class compare 0.6.9 -> 0.6.10 / engine-access audit around them):
  static   the generated script = the patch's output (re-run to identical bytes), 0.6.9's patch still regenerates 0.6.9 byte for byte, header /
           version, ONE new class (TreeLineFn), no new system / command, the two bridge keys put in setup and removed in shutdown; the jar vs
           0.6.9: + TreeLineFn.class only, every non-class entry but the manifest byte-equal (every picture: the UI picture area unchanged,
           tools/ci/ui_budget.py: no FAIL with this jar)
  line     EXECUTED (the real TreeV3 / TreeMap / TreeStore on the harness engine): tree:fn:map on EVERY skill tree by name and on every one of the
           8 classes ("Class" and "Combat"): the header (17 fields, 520 x 264), one b line per branch, every node of that tree once (= the /tree
           map's nodes, its state picture name = TreeMap.tex, a picture the jar ships), inside the canvas, none overlapping (re-checked here);
           a skill without a tree / class trees off / no class = "none|..."; the selected node's d line = the /tree page's texts.
           tree:fn:act: learn (Done, ONE rank), rank up (ONE more rank a click), a double click within 350 ms ("=One moment.", nothing
           bought), not enough points / a locked row / a free node / coming soon refused (nothing changes), a stale profile token / a profile
           switch in progress refused, a node that is no longer the k-th ("That tree changed"); respec = two presses (armed, then done; the
           price shown; nothing changes on the first), a changed price re-arms; the class tree through "Class"; apply() off the world thread
           = null, on it (Universe + Store stand-ins) = the answer
  inline   EXECUTED END TO END with the real SkyyMenu 0.3.61 jar in the same JVM: the Mining skill page draws SkyyTrees' map (every node, its
           picture path SkyyTrees/Map/Node/<state>.png in this jar, the click squares bound tn:<k>), a node click = ONE packet with the halo +
           the node panel, Learn = ONE tree:fn:act and one rank (the caption = SkyyTrees' own answer), Rank up, a double click = no second
           rank, Respec twice; Combat = the class tree; Ranching = SkyyTrees' none sentence; element count of every page printed
  zoom / harv / effects / old66 / text / bridge / creative / g64 / data / sow / jar65 / path / mig / integ / farm / sap / live   the 0.6.9
           harness's phases on the 0.6.10 jar (unchanged behaviour; live = start twice on a scratch COPY of the live Skyy_SkyyTrees folder)
Not executed here (UNVERIFIED until the game): the client drawing the inline map (picture scale at 20-32 px, the halo, the click squares).
"""
import os, sys, json, subprocess, importlib.util, zipfile, re, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION = "0.6.10"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "treemap1", "trees")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)]
import skyybuild as B
import harness_kit as HK

_s = importlib.util.spec_from_file_location("test_skyytrees_0_6_9", os.path.join(HERE, "test_skyytrees_0.6.9.py"))
T69 = importlib.util.module_from_spec(_s)
_argv = list(sys.argv)
_s.loader.exec_module(T69)
sys.argv[:] = _argv
T68, T67 = T69.T68, T69.T67
T66, T65, T64, T63, T60 = T67.T66, T67.T65, T67.T64, T67.T63, T67.T60
T60.VERSION = VERSION

PKG = "com.skyy.trees."
PH = "com.hypixel.hytale."
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyTrees-0.6.9.jar") if os.path.isfile(os.path.join(HERE, "SkyyTrees-0.6.9.jar")) else os.path.join(T67.BASE, "SkyyTrees", "SkyyTrees-0.6.9.jar")
MENU_JAR = os.path.join(ROOT, "SkyyMenu", "SkyyMenu-0.3.61.jar")
GEN = os.path.join(HERE, "build_skyytrees_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyytrees_0.6.9.py")
PATCH = os.path.join(TOOLS, "trees_0_6_10_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
UI = "Common/UI/Custom/"
NODE = UI + "SkyyTrees/Map/Node/"
EXPECT = {   # 0.6.9 -> 0.6.10: the new class + the two bridge keys + the version strings
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'SkyyTreesPlugin': ['~m setup', '~m shutdown'],
    'TreeCfg': ['~m load'],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
U_A = "71717171-0000-0000-0000-000000000001"   # a Miner (skill trees)
U_W = "71717171-0000-0000-0000-000000000002"   # a Warrior (the class tree)


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyTrees 0.6.10 - build script') and g.count('VERSION = "0.6.10"') == 1 and 'VERSION = "0.6.9"' not in g, "S header + VERSION")
    K.check(g.count("registerCommand(") == o.count("registerCommand(") and g.count("registerSystem(") == o.count("registerSystem(")
            and g.count("makeClass(") == o.count("makeClass(") + 1 and 'pool.makeClass(PKG + ".TreeLineFn")' in g, "S ONE new class (TreeLineFn), no new command / system")
    K.check(g.count('b.put("tree:fn:map", @PKG@.TreeLineFn.MAPFN)') == 1 and g.count('b.put("tree:fn:act", @PKG@.TreeLineFn.ACTFN)') == 1
            and g.count('b.remove("tree:fn:map", @PKG@.TreeLineFn.MAPFN)') == 1 and g.count('b.remove("tree:fn:act", @PKG@.TreeLineFn.ACTFN)') == 1,
            "S the two keys are put in setup and removed in shutdown only while they still hold ours")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    for patch, ref in ((PATCH, GEN), (os.path.join(TOOLS, "trees_0_6_9_patch.py"), GEN_OLD)):
        cp = os.path.join(d, os.path.basename(ref))
        p = subprocess.run([sys.executable, patch, "--out", cp], capture_output=True, text=True)
        K.check(p.returncode == 0 and open(cp, "rb").read() == open(ref, "rb").read(), "S %s re-generates its script byte for byte: %s" % (os.path.basename(patch), p.stderr[-300:]))
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    K.eq(sorted(na - nb), [], "S nothing removed from the jar")
    K.eq(sorted(nb - na), ["com/skyy/trees/TreeLineFn.class"], "S added = TreeLineFn.class only")
    chg = sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n))
    K.eq(chg, ["manifest.json"], "S every non-class entry but the manifest byte-equal (every picture + page data file)")
    ma, mb = json.loads(za.read("manifest.json")), json.loads(zb.read("manifest.json"))
    K.check(mb["Version"] == VERSION and dict(ma, Version=VERSION, Name=ma["Name"].replace("0.6.9", VERSION)) == mb, "S manifest: only the Version changed")
    pa = sum(1 for n in na if n.startswith(UI) and n.endswith(".png"))
    pb = sum(1 for n in nb if n.startswith(UI) and n.endswith(".png"))
    K.eq(pb, pa, "S UI pictures: the same %d files (byte-equal above) - the UI picture area is 0.6.9's" % pa)
    sys.path.insert(0, os.path.join(TOOLS, "ci"))
    import ui_budget as UB
    _w, _f, _l = UB.check(ROOT, overrides=[os.path.abspath(jar)])
    K.eq(_f, [], "U SET with this jar: no ui_budget FAIL (%s)" % (_l[0][-60:] if _l else "-"))
    K.notes.append("U ui_budget with this jar: %s" % " | ".join(_l)[:400])
    K.save()


def _fn(f):
    from jpype import JImplements, JOverride
    return T60._fn(JImplements, JOverride, f)


def _setup(scratch, tag, extra=()):
    """one JVM: the engine kit + SkyyTrees (+ extra jars); the TreeV3 tables; a world-thread stand-in (Universe.getPlayer + Store.isInThread)"""
    import jpype
    from jpype import JClass
    _s2 = importlib.util.spec_from_file_location("test_skyymenu_0_3_19", os.path.join(ROOT, "SkyyMenu", "test_skyymenu_0.3.19.py"))
    T19 = importlib.util.module_from_spec(_s2)
    _s2.loader.exec_module(T19)
    hcls = os.path.join(scratch, "hcls_" + tag)
    os.makedirs(hcls, exist_ok=True)
    os.chdir(scratch)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, hcls, JAR] + list(extra), verify=True)
    E = T19.engine(scratch, hcls)
    J = lambda n: JClass(PKG + n)
    Paths = JClass("java.nio.file.Paths")
    St, Cfg = J("TreeStore"), J("TreeCfg")
    d = os.path.join(scratch, tag)
    os.makedirs(os.path.join(d, "players"), exist_ok=True)
    St.DIR = Paths.get(os.path.join(d, "players"))
    Cfg.FILE = Paths.get(os.path.join(d, "trees.properties"))
    Cfg.load()
    J("TreeSk").loadV3(Paths.get(d))
    J("TreeSk").reads(True)
    br = St.bridge()
    T60._reads(br)
    return E, J, br


def _thread(E, P, on):
    """Universe.get().getPlayer(uuid) -> P's PlayerRef, and P's Store.isInThread() = (this thread) when on, else another thread"""
    from jpype import JClass
    Uni = JClass(PH + "server.core.universe.Universe")
    StoreC = JClass(PH + "component.Store")
    Thr = JClass("java.lang.Thread")
    uni = Uni.get()
    if uni is None:
        return "no Universe instance"
    MapC = JClass("java.util.Map")
    maps = []
    for f in Uni.class_.getDeclaredFields():
        if MapC.class_.isAssignableFrom(f.getType()) and str(f.getName()).startswith("players"):
            f.setAccessible(True)
            mp = f.get(uni)
            if mp is None:
                mp = JClass("java.util.concurrent.ConcurrentHashMap")()
                f.set(uni, mp)
            maps.append(str(f.getName()))
            mp.put(P.pr.getUuid(), P.pr)
    if not maps:
        return "no Universe players map (%s)" % [str(f.getName()) + ":" + str(f.getType().getName()) for f in Uni.class_.getDeclaredFields()][:12]
    if Uni.get().getPlayer(P.pr.getUuid()) is None:
        return "Universe.getPlayer still null (maps %s)" % maps
    tf = [f for f in StoreC.class_.getDeclaredFields() if str(f.getType().getName()) == "java.lang.Thread"]
    if len(tf) != 1:
        return "Store thread fields: %d" % len(tf)
    tf[0].setAccessible(True)
    tf[0].set(P.st, Thr.currentThread() if on else Thr("skyy-other-thread"))
    return ""


def _parse(ans):
    ls = str(ans).split("\n")
    h = ls[0].split("|")
    bs = [l.split("|") for l in ls[1:] if l.startswith("b|")]
    ns = [l.split("|") for l in ls[1:] if l.startswith("n|")]
    ds = [l.split("|") for l in ls[1:] if l.startswith("d|")]
    return h, bs, ns, ds


def run_line(out, jar, scratch, _home):
    from jpype import JClass, JString, JArray
    K = HK.Child(out)
    E, J, br = _setup(scratch, "line")
    V, TM, TL, St, Cfg, TC = J("TreeV3"), J("TreeMap"), J("TreeLineFn"), J("TreeStore"), J("TreeCfg"), J("TreeClass")
    UUID, Int, Obj = JClass("java.util.UUID"), JClass("java.lang.Integer"), JClass("java.lang.Object")
    OA = lambda xs: JArray(Obj)(xs)
    LV = {"lv": 30}
    br.put("skill:fn:level", _fn(lambda a: Int(LV["lv"])))
    TOK = {"k": "prof-1"}
    br.put("profile:fn:key", _fn(lambda a: JString(TOK["k"])))
    zb = zipfile.ZipFile(jar)
    names = set(zb.namelist())
    TNAME = [str(x) for x in V.TNAME]
    NV, NCV = int(V.NV), int(V.NCV)
    UNAME, UMAX = [str(x) for x in V.UNAME], [int(x) for x in V.UMAX]
    W, H = int(TL.W), int(TL.H)
    K.eq((W, H), (520, 264), "L the canvas = 520 x 264 (SkyyMenu 0.3.61's)")
    ua, uw = UUID.fromString(U_A), UUID.fromString(U_W)
    br.put("profile:class:" + U_W, "Warrior")
    br.put("class:" + U_W, "Warrior")
    MAP, ACT = TL.MAPFN, TL.ACTFN
    K.check(MAP is None and ACT is None, "L the functions exist only once the plugin's setup made them (static fields null before)")
    MAP, ACT = TL(0), TL(1)

    def rd(u, sk, sel=-1):
        return MAP.apply(OA([u, JString(sk), Int(sel)]))

    def check_tree(u, sk, tv, what):
        a = rd(u, sk)
        if a is None:
            return "%s: null" % what
        h, bs, ns, ds = _parse(a)
        prob = []
        if len(h) != 17 or h[0] != "ok" or int(h[2]) != tv or h[3] != TNAME[tv] or (int(h[10]), int(h[11])) != (W, H):
            prob.append("header %s" % h[:4])
        s = int(h[12])
        nb = int(V.TNB[tv])
        if len(bs) != nb or [int(b[1]) for b in bs] != list(range(nb)):
            prob.append("%d b lines (want %d)" % (len(bs), nb))
        want = sorted(int(c) for c in TM.nodes(int(TM.TVPAGE[tv]) if tv >= NCV else int(TM.NSP) + tv) if int(TM.nodeTv(int(c))) == tv)
        got = [int(n[2]) for n in ns]
        if sorted(got) != want or len(set(got)) != len(got) or [int(n[1]) for n in ns] != list(range(len(ns))):
            prob.append("nodes %d vs the /tree map's %d" % (len(got), len(want)))
        box = [(int(n[3]), int(n[4])) for n in ns]
        if not all(0 <= l and 0 <= t and l + s <= W and t + s <= H for l, t in box):
            prob.append("a node outside the canvas")
        ov = [(i, j) for i in range(len(box)) for j in range(i + 1, len(box)) if abs(box[i][0] - box[j][0]) < s and abs(box[i][1] - box[j][1]) < s]
        if ov:
            prob.append("%d overlapping pairs" % len(ov))
        miss = sorted(set(n[5] for n in ns if (NODE + n[5] + "@2x.png") not in names and (NODE + n[5] + ".png") not in names))
        if miss:
            prob.append("pictures not in the jar: %s" % miss[:4])
        if any(not re.fullmatch(r"[A-Za-z0-9]+", n[5]) or not re.fullmatch(r"[A-Za-z0-9_]+|-", n[6]) for n in ns):
            prob.append("a picture / icon name with other characters")
        for b in bs:
            if not (0 <= int(b[3]) and 0 <= int(b[4]) and int(b[5]) > 0 and int(b[3]) + int(b[5]) <= W and int(b[4]) + 16 <= H):
                prob.append("branch %s outside" % b[2])
        return ("%s: %s" % (what, "; ".join(prob))) if prob else ""
    bad, done, worst = [], 0, 0
    for tv in range(NCV, NV):
        r = check_tree(ua, TNAME[tv], tv, TNAME[tv])
        done += 1
        if r:
            bad.append(r)
        worst = max(worst, int(TL.TN[tv]))
    for ci in range(NCV):
        br.put("profile:class:" + U_W, TNAME[ci])
        br.put("class:" + U_W, TNAME[ci])
        for nm in ("Class", "Combat"):
            r = check_tree(uw, nm, ci, "%s as %s" % (nm, TNAME[ci]))
            done += 1
            if r:
                bad.append(r)
        worst = max(worst, int(TL.TN[ci]))
    K.eq(bad, [], "L tree:fn:map on all %d skill trees by name + all %d classes as Class / Combat (%d reads): header, branches, every node of the /tree map once, inside, no overlap, pictures in the jar" % (NV - NCV, NCV, done))
    K.check(worst <= 120, "L the biggest tree has %d nodes (SkyyMenu draws at most 120)" % worst)
    K.notes.append("L node sizes: %s" % ", ".join("%s %d" % (TNAME[tv], int(TL.TS[tv])) for tv in range(NV)))
    br.put("profile:class:" + U_W, "Warrior")
    br.put("class:" + U_W, "Warrior")
    # none answers
    K.eq(str(rd(ua, "Ranching")), "none|No Ranching skill tree on this server", "L a skill without a tree = none")
    K.eq(str(rd(ua, "Class")), "none|Choose a class first (/class) - your class tree shows here", "L no class yet = none (says how)")
    Cfg.CLASS_ON = False
    K.eq(str(rd(uw, "Combat")), "none|Class trees are switched off on this server", "L class trees off = none")
    Cfg.CLASS_ON = True
    K.check(MAP.apply(OA([JString("x"), JString("Mining")])) is None and MAP.apply(JString("x")) is None, "L a bad argument = null")
    # ---- the Miner: Mining at Lv 30
    mi = TNAME.index("Mining")
    d = St.data(ua)
    h, bs, ns, ds = _parse(rd(ua, "Mining"))
    K.eq(h[1], "prof-1", "L the header carries the profile token (TreeStore.pkey)")
    K.check(h[6] == "30" and h[7] == "0" and h[8].startswith("30 of 30 points free"), "L points 30, spent 0, the points line (%s)" % h[8])
    ready = [n for n in ns if n[5] == "Ready" and int(n[2]) >= 0 and UMAX[int(n[2])] >= 2]
    locked = [n for n in ns if n[5] == "Locked" and int(n[2]) >= 0]
    free = [n for n in ns if int(n[2]) < 0]
    K.check(bool(ready) and bool(locked) and bool(free), "L fresh Mining: Ready upgrades (row 1), Locked ones, free nodes (%d / %d / %d)" % (len(ready), len(locked), len(free)))
    k0, c0 = int(ready[0][1]), int(ready[0][2])
    h2, _b, _n, ds = _parse(rd(ua, "Mining", k0))
    dw = [str(x) for x in (V.detState(d, int(V.UROW[c0]), c0, int(V.ustate(d, c0, 30, 0, V.gatesD(d, mi))), V.gatesD(d, mi), 0, 30),)]
    K.check(len(ds) == 1 and len(ds[0]) == 14 and int(ds[0][1]) == k0 and ds[0][4] == UNAME[c0] and ds[0][5] == "Rank 0 / %d" % UMAX[c0] and ds[0][6] == dw[0]
            and ds[0][13] == "1" and ds[0][9].startswith("Cost: "), "L the selected node's d line = the /tree page's texts (name, rank, state, cost; can learn) %s" % ds[0][4:8] if ds else "-")
    K.eq(_parse(rd(ua, "Mining", 999))[3], [], "L a selection out of range = no d line")

    def act(tok, op, arg, u=ua):
        return str(TL.act(u, JString(tok) if tok is not None else None, JString(op), JString(arg)))
    arg0 = "Mining|%d|%d" % (k0, c0)
    r = act("prof-1", "learn", arg0)
    K.check(r.startswith("+Done: ") and int(d.rk[c0]) == 1, "A learn = TreeV3.buy: Done, rank 1 (%s)" % r)
    r = act("prof-1", "learn", arg0)
    K.check(r == "=One moment." and int(d.rk[c0]) == 1, "A the same Learn again within 350 ms = One moment, nothing bought (%s)" % r)
    time.sleep(0.4)
    r = act("prof-1", "learn", arg0)
    K.check(r.startswith("+Done: ") and int(d.rk[c0]) == 2 and ("rank 2/%d" % UMAX[c0]) in r, "A rank up = ONE more rank a click (%s)" % r)
    h, bs, ns, ds = _parse(rd(ua, "Mining"))
    K.check(h[7] == "2" and ns[k0][8] == "2 / %d" % UMAX[c0], "A the next read shows 2 spent and the node's rank 2 / %d" % UMAX[c0])
    # locked row
    time.sleep(0.4)
    kl, cl = int(locked[0][1]), int(locked[0][2])
    r = act("prof-1", "learn", "Mining|%d|%d" % (kl, cl))
    K.check(r.startswith("-") and ("needs" in r or "is in" in r) and int(d.rk[cl]) == 0, "A a node in a locked row is refused, nothing bought (%s)" % r)
    # a free node
    kf, cf = int(free[0][1]), int(free[0][2])
    r = act("prof-1", "learn", "Mining|%d|%d" % (kf, cf))
    K.check(r.startswith("-") and "free" in r, "A a free node = its own answer, nothing changes (%s)" % r)
    # that node is not the k-th any more
    r = act("prof-1", "learn", "Mining|%d|%d" % (k0, c0 + 1))
    K.check(r.startswith("=That tree changed") and int(d.rk[c0]) == 2, "A a code that is no longer the k-th node = That tree changed (%s)" % r)
    r = act("prof-1", "learn", "Mining|x|y")
    K.check(r.startswith("=That tree changed"), "A a bad arg = That tree changed (%s)" % r)
    # not enough points
    LV["lv"] = 2
    time.sleep(0.4)
    other = [n for n in ready if int(n[2]) != c0]
    ko, co = (int(other[0][1]), int(other[0][2])) if other else (k0, c0)
    rk0 = int(d.rk[co])
    r = act("prof-1", "learn", "Mining|%d|%d" % (ko, co))
    K.check(r.startswith("-No free points") and int(d.rk[co]) == rk0, "A not enough points = TreeV3's refusal, nothing bought (%s)" % r)
    LV["lv"] = 30
    # stale token, profile switch in progress
    s0 = int(TL.STALE.get())
    r = act("prof-OLD", "learn", arg0)
    K.check(r.startswith("=Your profile changed") and int(d.rk[c0]) == 2 and int(TL.STALE.get()) == s0 + 1, "A a stale profile token = refused, nothing bought (%s)" % r)
    r = act(None, "learn", arg0)
    K.check(r.startswith("=Your profile changed"), "A no token = refused")
    br.put("profile:busy:" + U_A, "1")
    r = act("prof-1", "learn", arg0)
    K.check(r.startswith("=Wait for the profile switch") and int(d.rk[c0]) == 2, "A a profile switch in progress = refused (%s)" % r)
    br.remove("profile:busy:" + U_A)
    K.check(rd(ua, "Mining").split("\n")[0].split("|")[15] == "0", "A the header's busy flag is 0 again")
    # respec: two presses
    time.sleep(0.4)
    r1 = act("prof-1", "respec", "Mining")
    K.check(r1.startswith("=Click Respec again within 10 s to reset your whole Mining tree") and "free (your free respec of this run)" in r1 and int(d.rk[c0]) == 2,
            "R the first press arms it with the price, nothing changes (%s)" % r1)
    K.eq(rd(ua, "Mining").split("\n")[0].split("|")[13], "1", "R the header says armed")
    r2q = act("prof-1", "respec", "Mining")
    K.check(r2q == "=One moment." and int(d.rk[c0]) == 2, "R a double click (second press within 350 ms) never confirms a respec (%s)" % r2q)
    time.sleep(0.4)
    r2 = act("prof-1", "respec", "Mining")
    K.check(r2.startswith("+Respec done") and int(d.rk[c0]) == 0 and int(V.spent(d, mi)) == 0, "R the second press = TreeV3.respec: every point back (%s)" % r2)
    K.eq(rd(ua, "Mining").split("\n")[0].split("|")[13], "0", "R disarmed after the respec")
    time.sleep(0.4)
    r3 = act("prof-1", "respec", "Mining")
    K.check(r3.startswith("-Nothing to respec"), "R nothing spent = TreeV3's own answer (%s)" % r3)
    # a paid respec whose price changes between the presses re-arms
    time.sleep(0.4)
    K.check(act("prof-1", "learn", arg0).startswith("+Done"), "R buy again")
    COINS = []
    br.put("coins:fn:take", _fn(lambda a: (COINS.append(int(a[1])), JClass("java.lang.Boolean").TRUE)[1]))
    time.sleep(0.4)
    r4 = act("prof-1", "respec", "Mining")
    LV["lv"] = 40
    time.sleep(0.4)
    r5 = act("prof-1", "respec", "Mining")
    K.check("it costs" in r4 and r5.startswith("=Click Respec again") and "(the price changed since your first click)" in r5 and int(d.rk[c0]) == 1 and COINS == [],
            "R the price changed between the presses = armed again with the new price, nothing taken (%s / %s)" % (r4[-60:], r5[-60:]))
    time.sleep(0.4)
    r6 = act("prof-1", "respec", "Mining")
    K.check(r6.startswith("+Respec done") and len(COINS) == 1 and int(d.rk[c0]) == 0, "R the press at the same price = done, the coins taken once (%s)" % COINS)
    # treemap1fix: the arm belongs to the profile that armed it - a switch to another profile within 10 s never confirms there
    time.sleep(0.4)
    TOK["k"] = "prof-2"
    d2 = St.data(ua)
    K.check(act("prof-2", "learn", arg0).startswith("+Done") and int(d2.rk[c0]) == 1, "P profile 2 buys a rank (its own data)")
    TOK["k"] = "prof-1"
    time.sleep(0.4)
    K.check(act("prof-1", "learn", arg0).startswith("+Done") and int(d.rk[c0]) == 1, "P profile 1 buys a rank")
    time.sleep(0.4)
    p1 = act("prof-1", "respec", "Mining")
    K.check(p1.startswith("=Click Respec again") and int(d.rk[c0]) == 1, "P profile 1 arms its respec (%s)" % p1[:40])
    TOK["k"] = "prof-2"
    K.eq(rd(ua, "Mining").split("\n")[0].split("|")[13], "0", "P after the switch profile 2's header is NOT armed (no Confirm label)")
    time.sleep(0.4)
    c0n = len(COINS)
    p2 = act("prof-2", "respec", "Mining")
    K.check(p2.startswith("=Click Respec again") and "price changed" not in p2 and int(d2.rk[c0]) == 1 and int(d.rk[c0]) == 1 and len(COINS) == c0n,
            "P the first press on profile 2 arms ITS respec - profile 1's arm never confirms it, nothing taken (%s)" % p2[:60])
    time.sleep(0.4)
    p3 = act("prof-2", "respec", "Mining")
    K.check(p3.startswith("+Respec done") and int(d2.rk[c0]) == 0 and int(d.rk[c0]) == 1, "P the second press on profile 2 resets profile 2 only (%s)" % p3[:40])
    TOK["k"] = "prof-1"
    K.eq(rd(ua, "Mining").split("\n")[0].split("|")[13], "0", "P back on profile 1: not armed (profile 2's press replaced the arm)")
    time.sleep(0.4)
    p4 = act("prof-1", "respec", "Mining")
    time.sleep(0.4)
    p5 = act("prof-1", "respec", "Mining")
    K.check(p4.startswith("=Click Respec again") and p5.startswith("+Respec done") and int(d.rk[c0]) == 0, "P profile 1 then respecs with its own two presses (%s / %s)" % (p4[:30], p5[:30]))
    LV["lv"] = 30
    # the class tree through "Class"
    wi = TNAME.index("Warrior")
    dW = St.data(uw)
    hW, bW, nW, _d = _parse(rd(uw, "Class"))
    rw = [n for n in nW if n[5] == "Ready" and int(n[2]) >= 0]
    K.check(bool(rw), "C the Warrior's class tree has Ready nodes")
    if rw:
        kw, cw = int(rw[0][1]), int(rw[0][2])
        r = act(hW[1], "learn", "Class|%d|%d" % (kw, cw), u=uw)
        K.check(r.startswith("+Done") and int(dW.rk[cw]) == 1, "C Learn on the class tree (Class) = TreeV3.buy on the Warrior tree (%s)" % r)
    K.eq(act("prof-1", "nope", "Mining"), "-Unknown tree action.", "A an unknown op")
    # apply(): the world thread only
    P = E.player(uid=ua, name="SkyyLineTester")
    o0 = int(TL.OFF.get())
    K.check(ACT.apply(OA([ua, JString("prof-1"), JString("learn"), JString(arg0)])) is None and int(TL.OFF.get()) == o0 + 1, "T apply() off the world thread (no player there) = null, nothing bought")
    why = _thread(E, P, False)
    if why:
        K.notes.append("T world-thread stand-in not set up: " + why + " - the on-thread apply path UNVERIFIED here")
    else:
        K.check(ACT.apply(OA([ua, JString("prof-1"), JString("learn"), JString(arg0)])) is None, "T apply() with the player's store on ANOTHER thread = null")
        _thread(E, P, True)
        time.sleep(0.4)
        r = ACT.apply(OA([ua, JString("prof-1"), JString("learn"), JString(arg0)]))
        K.check(r is not None and str(r).startswith("+Done") and int(d.rk[c0]) == 1, "T apply() on the player's world thread = the act answer (%s)" % r)
    K.check(ACT.apply(OA([ua, JString("prof-1")])) is None, "T apply() with too few arguments = null")
    K.notes.append("L counters: reads %d, acts %d, stale %d, guard %d, off %d" % (int(TL.READS.get()), int(TL.ACTS.get()), int(TL.STALE.get()), int(TL.GUARD.get()), int(TL.OFF.get())))
    K.save()
    sys.stdout.flush()
    os._exit(0)


def run_inline(out, jar, scratch, _home):
    """the REAL SkyyMenu 0.3.61 skill page drawing this jar's tree:fn:map, its clicks through tree:fn:act"""
    from jpype import JClass, JString
    K = HK.Child(out)
    if not os.path.isfile(MENU_JAR):
        K.check(False, "I SkyyMenu 0.3.61 jar missing: %s" % MENU_JAR)
        K.save()
        return
    E, J, br = _setup(scratch, "inline", [MENU_JAR])
    MJ = lambda n: JClass("com.skyy.menu." + n)
    V, TL, St = J("TreeV3"), J("TreeLineFn"), J("TreeStore")
    UUID, Int = JClass("java.util.UUID"), JClass("java.lang.Integer")
    K.check(MJ("MenuUtil").bridge() is St.bridge() or MJ("MenuUtil").bridge().equals(St.bridge()), "I the two mods share one skyy.bridge map")
    LV = {"lv": 30}
    br.put("skill:fn:level", _fn(lambda a: Int(LV["lv"])))
    br.put("profile:class:" + U_W, "Warrior")
    br.put("class:" + U_W, "Warrior")
    br.put("tree:fn:map", TL(0))   # as SkyyTreesPlugin.setup puts them (0.6.10)
    br.put("tree:fn:act", TL(1))
    ua = UUID.fromString(U_A)
    P = E.player(uid=ua, name="SkyyInlineTester")
    why = _thread(E, P, True)
    K.check(why == "", "I the world-thread stand-in (Universe.getPlayer + Store thread): %s" % (why or "ok"))
    SKP = MJ("SkillPage")
    zb = zipfile.ZipFile(jar)
    names = set(zb.namelist())

    def pages(f0):
        return [p for p in E.sent(P)[f0:] if str(p.getClass().getSimpleName()) == "CustomPage"]

    def cmds(pk):
        cs = pk.commands if hasattr(pk, "commands") else None
        return [] if cs is None else list(cs)

    def cmap(pk):
        d_ = {}
        for c in cmds(pk):
            d_[str(c.selector)] = (str(c.data) if c.data is not None else "") + (str(c.text) if c.text is not None else "")
        return d_

    def sval(cm, k):
        v = cm.get(k)
        if v is None:
            return None
        try:
            j = json.loads(v)
            return j.get("0") if isinstance(j, dict) else j
        except Exception:
            return v

    def markup(pk):
        return "\n".join(str(c.text) for c in cmds(pk) if c.text is not None)

    def binds(pk):
        b = pk.eventBindings if hasattr(pk, "eventBindings") else None
        return [] if b is None else [(str(x.selector), str(x.data)) for x in b]

    def elements(pk):
        return len(re.findall(r"(?:^|(?<=[;{}]))\s*[A-Z][A-Za-z]*(?:\s+#[A-Za-z0-9]+)?\s*\{", re.sub(r'"(?:[^"\\]|\\.)*"', '""', markup(pk))))

    def click(obj, what):
        E.pump(P)
        f0 = len(E.sent(P))
        P.pm.getCustomPage().handleDataEvent(P.ref, P.st, json.dumps(obj))
        ps = pages(f0)
        K.eq(len(ps), 1, what + ": exactly ONE page packet")
        E.pump(P)
        return ps[0] if ps else None
    E.pump(P)
    f0 = len(E.sent(P))
    pg = SKP.open(P.ref, P.st, P.pr, "Mining", "harness")
    E.pump(P)
    ps = pages(f0)
    K.check(pg is not None and len(ps) == 1, "I the Mining skill page opens (ONE packet)")
    pk = ps[0] if ps else None
    cm = cmap(pk) if pk else {}
    mi = [str(x) for x in V.TNAME].index("Mining")
    tn = int(TL.TN[mi])
    mk = markup(pk) if pk else ""
    nodes = re.findall(r'Group #SkyySkpTn(\d+) \{ Anchor: \(Left: (\d+), Top: (\d+), Width: (\d+), Height: \d+\); Background: "SkyyTrees/Map/Node/([A-Za-z0-9]+)\.png"; \}', mk)
    hits = [b for b in (binds(pk) if pk else []) if b[0].startswith("#SkyySkpTn")]
    K.check(len(nodes) == tn and [int(n[0]) for n in nodes] == list(range(tn)) and all((NODE + n[4] + "@2x.png") in names for n in nodes),
            "I Mining: every one of the %d nodes drawn with SkyyTrees' own state picture (in this jar) (%d)" % (tn, len(nodes)))
    K.check(len(hits) == tn and all(json.loads(b[1]).get("a") == "tn:%d" % i for i, b in enumerate(hits)), "I every node's click square bound tn:<k> (%d)" % len(hits))
    K.check(sval(cm, "#SkyySkpTrV1.Visible") in (True, "true") and sval(cm, "#SkyySkpTrV0.Visible") in (False, "false") and sval(cm, "#SkyySkpTrO.Text") == "Full tree"
            and sval(cm, "#SkyySkpTrL.Visible") in (True, "true") and str(sval(cm, "#SkyySkpTrP.Text")).startswith("30 of 30 points free"),
            "I the inline view shows (Learn, Respec, Full tree; the points line %s)" % sval(cm, "#SkyySkpTrP.Text"))
    K.eq(sval(cm, "#SkyySkpDn.Text"), "PICK A NODE", "I nothing selected = how to use it")
    el = elements(pk) if pk else 0
    K.check(el < 1600, "I the Mining page packet: %d elements (budget ~1,600)" % el)
    K.notes.append("I Mining page: %d elements, %d commands" % (el, len(cmds(pk)) if pk else 0))
    # pick a Ready node with 2+ ranks
    ready = [n for n in nodes if n[4] == "Ready"]
    k0 = None
    for n in ready:
        c = int(TL.C[int(TL.T0[mi]) + int(n[0])])
        if c >= 0 and int(V.UMAX[c]) >= 2:
            k0, c0 = int(n[0]), c
            break
    K.check(k0 is not None, "I a Ready node with 2+ ranks")
    if k0 is None:
        K.save()
        sys.stdout.flush()
        os._exit(0)
    pk = click({"a": "tn:%d" % k0}, "I a node click")
    cm = cmap(pk) if pk else {}
    K.check("#SkyySkpTs " in markup(pk) and sval(cm, "#SkyySkpDn.Text") == str(V.UNAME[c0]) and str(sval(cm, "#SkyySkpDr.Text")).startswith("Rank 0 /")
            and sval(cm, "#SkyySkpTrL.Text") == "Learn", "I the click = the halo + the node panel (%s, %s)" % (sval(cm, "#SkyySkpDn.Text"), sval(cm, "#SkyySkpDr.Text")))
    d = St.data(ua)
    pk = click({"a": "tl"}, "I Learn")
    cm = cmap(pk) if pk else {}
    K.check(int(d.rk[c0]) == 1 and str(sval(cm, "#SkyySkpCap.Text")).startswith("Done: ") and sval(cm, "#SkyySkpTrL.Text") == "Rank up"
            and str(sval(cm, "#SkyySkpDr.Text")).startswith("Rank 1 /"), "I Learn = ONE rank, SkyyTrees' answer as the caption, the button now Rank up (%s)" % sval(cm, "#SkyySkpCap.Text"))
    E.pump(P)
    f1 = len(E.sent(P))
    P.pm.getCustomPage().handleDataEvent(P.ref, P.st, '{"a":"tl"}')
    ps = pages(f1)
    K.check(len(ps) == 1 and int(d.rk[c0]) == 1 and sval(cmap(ps[0]), "#SkyySkpCap.Text") == "One moment.", "I a double click = One moment (caption only), no second rank")
    E.pump(P)
    time.sleep(0.4)
    pk = click({"a": "tl"}, "I Rank up")
    K.check(int(d.rk[c0]) == 2, "I Rank up = one more rank (%d)" % int(d.rk[c0]))
    # stale token: the profile key changes after the draw
    br.put("profile:fn:key", _fn(lambda a: JString("other-profile")))
    time.sleep(0.4)
    pk = click({"a": "tl"}, "I Learn with a stale token")
    K.check(int(d.rk[c0]) == 2 and str(sval(cmap(pk), "#SkyySkpCap.Text")).startswith("Your profile changed") and int(pg.tsel) == -1,
            "I a stale token = nothing bought, said, the selection cleared")
    br.remove("profile:fn:key")
    click({"a": "sk:%d" % [str(x) for x in MJ("SkillData").ORDER].index("Mining")}, "I redraw on the first profile")
    time.sleep(0.4)
    pk = click({"a": "tl"}, "I Learn with nothing selected")
    K.eq(sval(cmap(pk), "#SkyySkpCap.Text"), "Click a node on the map first", "I Learn with nothing selected = said")
    # respec twice
    pk = click({"a": "trs"}, "I Respec 1")
    K.check(str(sval(cmap(pk), "#SkyySkpCap.Text")).startswith("Click Respec again") and sval(cmap(pk), "#SkyySkpTrR.Text") == "Confirm" and int(d.rk[c0]) == 2,
            "I the first Respec arms it (Confirm), nothing changes")
    time.sleep(0.4)
    pk = click({"a": "trs"}, "I Respec 2")
    K.check(str(sval(cmap(pk), "#SkyySkpCap.Text")).startswith("Respec done") and int(V.spent(d, mi)) == 0, "I the second = done, every point back")
    # Combat = the class tree; Ranching = none; every skill draws
    order = [str(x) for x in MJ("SkillData").ORDER]
    pk = click({"a": "sk:%d" % order.index("Combat")}, "I Combat without a class")
    K.eq(sval(cmap(pk), "#SkyySkpTmM.Text"), "Choose a class first (/class) - your class tree shows here", "I Combat without a class = SkyyTrees' sentence in the map box")
    br.put("profile:class:" + U_A, "Warrior")
    br.put("class:" + U_A, "Warrior")
    pk = click({"a": "sk:%d" % order.index("Combat")}, "I Combat")
    mk = markup(pk) if pk else ""
    wi = [str(x) for x in V.TNAME].index("Warrior")
    K.check(len(re.findall(r"Group #SkyySkpTn\d+ ", mk)) == int(TL.TN[wi]), "I Combat = the Warrior class tree (%d nodes)" % int(TL.TN[wi]))
    pk = click({"a": "sk:%d" % order.index("Ranching")}, "I Ranching")
    cm = cmap(pk) if pk else {}
    K.check(sval(cm, "#SkyySkpTmM.Text") == "No Ranching skill tree on this server" and sval(cm, "#SkyySkpTrL.Visible") in (False, "false")
            and "#SkyySkpTn0 " not in markup(pk), "I Ranching = SkyyTrees' none sentence in the map box, no Learn")
    worst = 0
    for i, s in enumerate(order):
        pk = click({"a": "sk:%d" % i}, "I %s" % s)
        el = elements(pk) if pk else 0
        worst = max(worst, el)
        K.notes.append("I %s page: %d elements" % (s, el))
    K.check(worst < 1600, "I every skill page under the ~1,600 element budget (worst %d)" % worst)
    K.save()
    sys.stdout.flush()
    os._exit(0)


if __name__ == "__main__":
    for _p in (OLD_JAR, T69.OLD_JAR, T68.OLD_JAR, T67.OLD_JAR, T67.CJAR, T67.PJAR, T65.OLD_JAR):
        assert os.path.isfile(_p), "missing %s (pass --base <the checkout with the built jars>)" % _p
    HK.run(name="SkyyTrees", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=["TreeLineFn"],
           phases=[("static", run_static), ("line", run_line), ("inline", run_inline), ("zoom", T69.run_zoom), ("harv", T68.run_harv),
                   ("effects", T67.run_effects), ("old66", T67.run_old66), ("text", T67.run_text), ("bridge", T67.run_bridge), ("creative", T66.run_creative),
                   ("g64", T65.run_g64), ("data", T65.run_data), ("sow", T65.run_sow), ("jar65", T65.run_jar), ("path", T64.run_path), ("mig", T64.run_mig),
                   ("integ", T64.run_integ), ("farm", T63.run_farm), ("sap", T63.run_sap), ("live", T63.run_live)],
           script=__file__, live=(T60.LIVE_DIR, "Skyy_SkyyTrees"))
