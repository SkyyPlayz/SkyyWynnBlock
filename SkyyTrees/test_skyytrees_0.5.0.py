"""Harness for SkyyTrees 0.5.0 (THE RADIAL TREE PAGES, research/Radial-Trees-Spec.md round R2; tools/trees_0_5_0_patch.py + tools/skyymap.py +
the kit 1.8 node maps). Build first:
    python tools/trees_0_5_0_patch.py && python SkyyTrees/build_skyytrees_0.5.0.py
    python SkyyTrees/test_skyytrees_0.5.0.py [--keep]
Phases (tools/harness_kit.py, fresh child JVMs, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  S    static   the patch re-runs to identical bytes; line endings kept; one class added (TreeMap); no new system / command
  J    jar      every map picture under Common/UI/Custom/SkyyTrees/Map/ (@2x, even sizes, no underscore), no .ui file, the 44 page data
       files; every texture the page data names is shipped and written without @2x; every node picture name the run time can answer is
       shipped; skyymap's checks RE-RUN on the coordinates parsed back out of the jar's page data (every layout x zoom: in the canvas,
       discs >= 6 px apart, click squares apart, every upgrade / free perk once); pictures byte-identical when drawn again (deterministic)
  A    verify   every class loads + initialises (-Xverify:all)
  C    compare  0.4.9 -> 0.5.0: exactly the planned members (EXPECT)
  OLD / DATA  the 0.4.9 jar's TreeV3 tables = 0.5.0's (no rule, number, key, gate or text changed)
  X    exec     the SkyyMenu 0.3.19 harness engine (a player with the REAL PageManager + a recording packet handler) - EXECUTED:
       OPEN    the four pages (Gathering / Crafting / Adventure / Class) at every zoom and the Class page's Loadout view: ONE CustomPage
               packet each holding the map page data (+ the scroll box above 100 %), at most 1,000 elements (every line lit)
       ANSWER  on every page variant, EVERY bound event (read back out of the packet) clicked through the real PageManager on a fresh
               page = exactly ONE page packet (a rebuild) and the page still open, or the close (the hub's own close / Home); no WARN,
               the safety net never needed for a bound event; unknown data / no data / a thrown error = ONE empty update (the net)
       GOLD    TreeMap.paint for a fresh / mid / full player on every layout = the gold rule (a spine into an open row, a spoke into an
               upgrade with a rank) and the picture rule (TreeV3.ustate), every picture name shipped, a dead upgrade never 'Ready'
       FLOW    click a ready node -> Learn: rank + 1, its picture + spoke change; Respec twice: every rank back; zoom in / out (clamped);
               a node of another tree switches the head; rail page / tree / class rows; the Nexus row (rebirth:fn:open, the /rebirth
               fallback, hidden without SkyyRebirth); the class probe page learns on its copy only; Loadout <-> Talents
  LIVE START TWICE on a scratch COPY of the live Skyy_SkyyTrees folder (setup's whole update chain incl. TreeMigP7, every player file read +
       derived): nothing changes on start 1 or 2 (0.5.0 has no one-time update); every live player painted on every layout (picture names
       shipped)
  AA   engine-access audit
NOT COVERED (UNVERIFIED in game): how the map looks on Skyy's screen (sizes, crispness at 150 / 200 % - the 100 % @2x pictures stretched),
scrolling the zoomed map (NOT BUILT: centring on the selected talent / keeping the view still after a click - needs probe M8), the
Nexus opening SkyyRebirth's page in place of ours (the /rebirth fallback needs a CommandManager), the SkyyClasses loadout panel content.
"""
import os, sys, json, subprocess, importlib.util, shutil, zipfile, struct, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "radial12", "trees")]
import skyybuild as B
import harness_kit as HK
import skyymap as SMAP

_s = importlib.util.spec_from_file_location("test_skyytrees_0_4_6", os.path.join(HERE, "test_skyytrees_0.4.6.py"))
T46 = importlib.util.module_from_spec(_s)
_argv = list(sys.argv)
_s.loader.exec_module(T46)
sys.argv[:] = _argv

VERSION = "0.5.0"
PKG = "com.skyy.trees."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyTrees-0.4.9.jar")
GEN = os.path.join(HERE, "build_skyytrees_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyytrees_0.4.9.py")
PATCH = os.path.join(TOOLS, "trees_0_5_0_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
LIVE_DIR = T46.LIVE_DIR
ADDED = ["TreeMap"]
EXPECT = {}
TABLES = T46.TABLES
MAPRES = "com/skyy/trees/map/"
MAPDIR = "Common/UI/Custom/SkyyTrees/Map/"
NL, ZN = 11, 3
U1 = "51515151-0000-0000-0000-000000000001"   # fresh: nothing bought
U2 = "51515151-0000-0000-0000-000000000002"   # mid: Mining 9 points
U3 = "51515151-0000-0000-0000-000000000003"   # full: every live upgrade maxed where the row is open
RX = re.compile(r'Anchor: \(Left: (-?\d+), Top: (-?\d+), Width: (\d+), Height: (\d+)\); Background: "([^"]+)"')


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyTrees 0.5.0 - build script') and g.count('VERSION = "0.5.0"') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.eq(g.count("makeClass(") - o.count("makeClass("), 1, "S one class added (TreeMap)")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def _parse_layout(z, L, zi):
    """the page data of layout L at zoom zi -> (nodes [(k, l, t, s, pre path)], static [(path, l, t, w, h)], edges {k: box}, sets)"""
    t = z.read(MAPRES + "L%dZ%d.txt" % (L, zi)).decode("utf-8")
    nodes, static, edges, sets = [], [], {}, []
    for ln in t.split("\n"):
        if not ln:
            continue
        f = ln.split("\t")
        if f[0] == "N":
            m = RX.search(f[2] + "Locked" + f[3])
            nodes.append((int(f[1]), int(m.group(1)), int(m.group(2)), int(m.group(3)), f[2].split('"')[-1], f[4], f[5], f[6], f[7]))
        elif f[0] == "A":
            m = RX.search(f[2])
            if m:
                static.append((m.group(5), int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)), f[2]))
            else:
                static.append((None, 0, 0, 0, 0, f[2]))
        elif f[0] == "E":
            m = RX.search(f[2])
            edges[int(f[1])] = (int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)), m.group(5))
        elif f[0] == "S":
            sets.append((f[1], f[2]))
    return t, nodes, static, edges, sets


def _meta(z, L):
    n, e = None, None
    for ln in z.read(MAPRES + "L%d.meta" % L).decode().split("\n"):
        f = ln.split("\t")
        if f[0] == "N":
            n = [int(x) for x in f[1].split(",")]
        elif f[0] == "E":
            e = dict((int(kv.split(":")[0]), int(kv.split(":")[1])) for kv in f[2].split(",") if kv)
            e["_n"] = int(f[1])
    return n, e


def run_jar(out, jar, scratch, _home):
    K = HK.Child(out)
    z = zipfile.ZipFile(jar)
    names = z.namelist()
    K.check(not [n for n in names if n.lower().endswith(".ui")], "J no .ui file (inline pages only)")
    pngs = [n for n in names if n.startswith(MAPDIR)]
    K.check(len(pngs) > 500 and all(n.endswith("@2x.png") and "_" not in n.split("/")[-1] for n in pngs), "J %d map pictures, all @2x, no underscore" % len(pngs))
    bad = [n for n in pngs if any(v % 2 for v in struct.unpack(">II", z.read(n)[16:24]))]
    K.eq(bad, [], "J every map picture has even (2x) sizes")
    data = sorted(n for n in names if n.startswith(MAPRES))
    K.eq(data, sorted([MAPRES + "L%dZ%d.txt" % (L, zi) for L in range(NL) for zi in range(ZN)] + [MAPRES + "L%d.meta" % L for L in range(NL)]),
         "J the 44 page data files")
    zo = zipfile.ZipFile(OLD_JAR)
    on = zo.namelist()
    ed = sorted(n for n in set(on) | set(names) if not n.endswith(".class") and (n not in on or n not in names or zo.read(n) != z.read(n)))
    K.eq([n for n in ed if not MAP_ENTRY.match(n)], ["manifest.json"], "J vs 0.4.9: only the manifest and the new map entries changed (%d map entries)" % len(ed))
    K.check(all(n not in on for n in ed if MAP_ENTRY.match(n)), "J the map entries are all new")
    nodepics = set(n[len(MAPDIR) + 5:-7] for n in pngs if n.startswith(MAPDIR + "Node/"))
    json.dump(sorted(nodepics), open(os.path.join(scratch, "nodepics.json"), "w"))
    worst, checked = 0, 0
    for L in range(NL):
        codes, ecodes = _meta(z, L)
        K.check(codes is not None and ecodes is not None, "J L%d meta read" % L)
        for zi in range(ZN):
            t, nodes, static, edges, sets = _parse_layout(z, L, zi)
            K.check("@2x" not in t, "J L%dZ%d: no @2x in the markup" % (L, zi))
            for p in re.findall(r'Background: "([^"]+\.png)"', t):
                if "Map/Node/" in p:
                    continue
                if (("Common/UI/Custom/" + p[:-4] + "@2x.png") not in names) and not p.startswith("SkyyKit/"):
                    K.check(False, "J L%dZ%d texture shipped: %s" % (L, zi, p))
            K.eq(len(nodes), len(codes), "J L%dZ%d one N line per node of the meta" % (L, zi))
            K.check(all(n[4].endswith("SkyyTrees/Map/Node/") for n in nodes), "J L%dZ%d every node picture lives in Map/Node/" % (L, zi))
            K.check(set(edges) == set(k for k in ecodes if k != "_n"), "J L%dZ%d the drawn edges = the meta's" % (L, zi))
            # skyymap's check re-run on the coordinates parsed back from the jar
            cv = [s for s in static if s[0] and s[0].endswith("/Base.png")][0]
            W, H = cv[3], cv[4]
            lay = dict(W=W, H=H, nodes=[], hubs=[], banners=[], edges=[], emb=0, hub=0, junctions=[])
            for k, l, tt, s, _pre, *_r in nodes:
                lay["nodes"].append(dict(id=k, l=l, t=tt, size=s, cx=l + s / 2.0, cy=tt + s / 2.0))
            hubs = [s for s in static if s[0] and "/Hub" in s[0]]
            emb = [s for s in static if s[0] and s[0].endswith("/Emblem.png")][0]
            lay["emb"] = emb[3]
            K.check(emb[1] == W // 2 - emb[3] // 2 and emb[2] == H // 2 - emb[3] // 2, "J L%dZ%d the emblem is centred" % (L, zi))
            lay["hub"] = hubs[0][3]
            for i, hb in enumerate(hubs):
                lay["hubs"].append(dict(key=i, l=hb[1], t=hb[2], cx=hb[1] + hb[3] / 2.0, cy=hb[2] + hb[3] / 2.0))
            for m in re.finditer(r"Label #SkyyTrMBn\d+A \{ Anchor: \(Width: (\d+), Height: \d+, Left: (\d+), Top: (\d+)\)", t):
                lay["banners"].append(dict(key="b", l=int(m.group(2)), t=int(m.group(3)), w=int(m.group(1)), h=SMAP.BANNER_H))
            lay["edge_dots"] = []
            try:
                info = SMAP.check(lay, None, "jar L%dZ%d" % (L, zi))
                ok = info["nodes"] == len(codes)
            except SystemExit as e:
                ok = False
                K.notes.append(str(e))
            K.check(ok and len(lay["banners"]) == len(hubs), "J L%dZ%d skyymap.check on the jar's own coordinates (%d nodes, %d banners)" % (L, zi, len(nodes), len(lay["banners"])))
            K.check(all(l >= 0 and tt >= 0 and l + w <= W and tt + h <= H for l, tt, w, h, _p in edges.values()),
                    "J L%dZ%d every gold line picture inside the canvas" % (L, zi))
            worst = max(worst, sum(SMAP_count(x) for x in t.split("\n")))
            checked += 1
    K.check(checked == NL * ZN, "J %d layout x zoom page data checked" % checked)
    K.notes.append("worst page data: %d elements" % worst)
    # deterministic pictures: redraw layout 0's base + every node state picture and compare with the jar's bytes
    import trees_v3_data as V3D
    import skyyui as SUI
    g0 = [(n, SUI.TREE_COLOR[n], V3D.tree(n)["branches"]) for n in ("Mining", "Foraging", "Farming", "Fishing")]
    lay0 = SMAP.build(g0, node=32, ring0=0.46, s=40.0, start=40.0)
    K.check(SMAP.png(SMAP.base_picture(lay0)) == z.read(MAPDIR + "Gathering/Base@2x.png"), "J the Gathering base picture drawn again = the jar's bytes (deterministic)")
    gp = SMAP.gold_pictures(lay0)
    k0 = sorted(gp)[7]
    K.check(SMAP.png(gp[k0]) == z.read(MAPDIR + "Gathering/E%d@2x.png" % k0), "J a gold line picture drawn again = the jar's bytes")
    npics = SMAP.node_pictures([SUI.TREE_COLOR["Mining"]], [1, 2, 3, 4, 5])
    K.check(all(SMAP.png(npics[n]) == z.read(MAPDIR + "Node/%s@2x.png" % n) for n in npics), "J the node pictures drawn again = the jar's bytes")
    K.save()


def SMAP_count(line):
    """elements of one page data line, every edge lit (A: its markup; E: 1; N: disc + icon + hit; S: 0)"""
    f = line.split("\t")
    if not f or not f[0]:
        return 0
    if f[0] == "A":
        return f[2].count("{")
    if f[0] == "E":
        return 1
    if f[0] == "N":
        return 2 + (0 if f[4] == "-" else 1)
    return 0


def run_old(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, OLD_JAR], verify=False)
    o = T46.dump(JClass(PKG + "TreeV3"))
    json.dump(o, open(os.path.join(scratch, "old049.json"), "w"))
    K.check(len(o["UKEY"]) > 0, "OLD the 0.4.9 tables read (%d upgrades)" % len(o["UKEY"]))
    K.save()


def run_data(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    o, n = json.load(open(os.path.join(scratch, "old049.json"))), T46.dump(JClass(PKG + "TreeV3"))
    for t in TABLES:
        K.eq(n[t], o[t], "DATA %s unchanged" % t)
    K.save()


def _fn(JImplements, JOverride, f):
    @JImplements("java.util.function.Function")
    class Fn(object):
        @JOverride
        def apply(self, a):
            return f(a)
    return Fn()


def run_exec(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JImplements, JOverride, JString
    K = HK.Child(out)
    _s2 = importlib.util.spec_from_file_location("test_skyymenu_0_3_19", os.path.join(ROOT, "SkyyMenu", "test_skyymenu_0.3.19.py"))
    T19 = importlib.util.module_from_spec(_s2)
    _s2.loader.exec_module(T19)
    hcls = os.path.join(scratch, "hcls_x")
    os.makedirs(hcls, exist_ok=True)
    os.chdir(scratch)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, hcls, jar], verify=True)
    E = T19.engine(scratch, hcls)
    J = lambda n: JClass(PKG + n)
    Paths, UUID, Int = JClass("java.nio.file.Paths"), JClass("java.util.UUID"), JClass("java.lang.Integer")
    St, Cfg, V, TM, Pg, Defs, TC = J("TreeStore"), J("TreeCfg"), J("TreeV3"), J("TreeMap"), J("TreePage"), J("TreeDefs"), J("TreeClass")
    d = os.path.join(scratch, "exec")
    os.makedirs(os.path.join(d, "players"), exist_ok=True)
    St.DIR = Paths.get(os.path.join(d, "players"))
    Cfg.FILE = Paths.get(os.path.join(d, "trees.properties"))
    Cfg.load()
    J("TreeSk").loadV3(Paths.get(d))
    J("TreeSk").reads(True)
    br = St.bridge()
    LV = {"lv": 30}
    br.put("skill:fn:level", _fn(JImplements, JOverride, lambda a: Int(LV["lv"])))
    nodepics = set(json.load(open(os.path.join(scratch, "nodepics.json"))))
    NT = int(Defs.NT)
    NV, NCV = int(V.NV), int(V.NCV)
    TPAGE = [int(x) for x in V.TPAGE]
    TNAME = [str(x) for x in V.TNAME]
    UMAX, UROW, RNUM, RFK, RT, UT = ([int(x) for x in getattr(V, n)] for n in ("UMAX", "UROW", "RNUM", "RFK", "RT", "UT"))
    RCAP = [bool(x) for x in V.RCAP]
    # ---- the players: fresh, mid (Mining 9 points in rows 1 + 2), full (every LIVE upgrade maxed where its row opens at level 60)
    live = [bool(V.live(u)) for u in range(int(V.NU))]
    mid = {}
    mt = TNAME.index("Mining")
    left = 9
    for u in range(int(V.TU0[mt]), int(V.TU0[mt]) + int(V.TUN[mt])):
        if live[u] and RNUM[UROW[u]] <= 2 and left > 0:
            k = min(UMAX[u], 2, left)
            mid[str(V.UKEY[u])] = k
            left -= k
    T46._pfile(d, U2, mid)
    full = dict((str(V.UKEY[u]), UMAX[u]) for u in range(int(V.NU)) if live[u] and UT[u] >= NCV)
    T46._pfile(d, U3, full)
    u1, u2, u3 = UUID.fromString(U1), UUID.fromString(U2), UUID.fromString(U3)
    for u_ in (u1, u2, u3):
        br.put("class:" + str(u_), "Warrior")
    K.check(not bool(St.data(u2).bad) and not bool(St.data(u3).bad), "X the mid + full player files read")
    K.eq(sum(int(V.spent(St.data(u2), mt)) for _ in [0]), 9, "X the mid player has 9 Mining points spent")

    # ---- GOLD + picture rule on every layout for the three players
    def exp_tex(dd, c, pts, sp, g, cp):
        if c < 0:
            r = -c - 1
            o = (sp >= g[RNUM[r]] or bool(V.gfRow(dd, r))) and RFK[r] != 0
            return cp + "Free" if o else "FreeLocked"
        mx, rk, cap = UMAX[c], int(dd.rk[c]), RCAP[UROW[c]]
        if rk >= mx:
            return cp + "CapMax" if cap else cp + "Max%d" % mx
        if rk >= 1:
            return cp + "L%d%d" % (rk, mx)
        st = int(V.ustate(dd, c, pts, sp, g))
        return ("Cap" if cap else "") + {1: "Ready", 4: "Soon", 5: "Open", 2: "Open"}.get(st, "Locked")
    gold_bad, pic_bad, dead_ready, unshipped, lit_n = [], [], [], set(), 0
    for u_ in (u1, u2, u3):
        dd = St.data(u_)
        for L in range(NL):
            codes = [int(x) for x in TM.nodes(L)]
            ecodes = [int(x) for x in TM.edges(L)]
            tex = JClass("java.lang.String[]")(len(codes)) if False else jpype.JArray(JString)(len(codes))
            lit = jpype.JArray(jpype.JBoolean)(len(ecodes))
            TM.paint(u_, dd, L, False, tex, lit)
            stats = {}
            for k, c in enumerate(codes):
                tv = int(TM.nodeTv(c))
                if tv not in stats:
                    s = [int(x) for x in TM.stat(u_, dd, tv, False)]
                    stats[tv] = (s, [int(x) for x in V.gates(tv)])
                (pts, sp, _l), g = stats[tv]
                want = exp_tex(dd, c, pts, sp, g, str(TM.CPIC[tv]))
                if str(tex[k]) != want:
                    pic_bad.append((L, k, str(tex[k]), want))
                if str(tex[k]) not in nodepics:
                    unshipped.add(str(tex[k]))
                if c >= 0 and not live[c] and str(tex[k]).endswith("Ready"):
                    dead_ready.append((L, k))
            for k, x in enumerate(ecodes):
                if x == -2147483648:
                    want = False
                elif x < 0:
                    want = int(dd.rk[-x - 1]) >= 1
                else:
                    tv = RT[x]
                    s = [int(y) for y in TM.stat(u_, dd, tv, False)]
                    want = s[1] >= int(V.gates(tv)[RNUM[x]])
                if bool(lit[k]) != want:
                    gold_bad.append((L, k))
                lit_n += 1 if want else 0
    K.eq(pic_bad[:5], [], "GOLD every node picture = the picture rule (fresh / mid / full, 11 layouts)")
    K.eq(gold_bad[:5], [], "GOLD every line lit = the gold rule (a spine into an open row, a spoke into an upgrade with a rank)")
    K.eq(sorted(unshipped), [], "GOLD every picture name the run time answers is shipped in the jar")
    K.eq(dead_ready, [], "GOLD a dead (coming soon) upgrade never shows Ready")
    K.notes.append("GOLD: %d lit lines over 3 players x 11 layouts" % lit_n)

    # ---- the pages
    def pkts(P, f0):
        return [p for p in E.sent(P)[f0:] if str(p.getClass().getSimpleName()) == "CustomPage"]

    def cmds_of(pkt):
        cs = pkt.commands if hasattr(pkt, "commands") else None
        return [] if cs is None else list(cs)

    def elements(pkt):
        n = 0
        for c in cmds_of(pkt):
            t = str(c.text) if c.text is not None else ""
            q = False
            for ch in t:
                if ch == '"':
                    q = not q
                elif ch == "{" and not q:
                    n += 1
        return n

    def actions(pkt):
        out_ = []
        evs = pkt.eventBindings if hasattr(pkt, "eventBindings") else None
        for ev in (list(evs) if evs is not None else []):
            s = "\n".join(E.strs_of_obj(ev)) if hasattr(E, "strs_of_obj") else str(ev.data)
            m = re.search(r'"a"\s*:\s*"([^"]+)"', s)
            out_.append(m.group(1) if m else s)
        return out_

    P = E.player(uid=u2, name="SkyyTreeTester")

    def open_page(t, zoom=0, lmode=False, msel=-1, probe=False):
        E.pump(P)
        pg = Pg(P.pr, t)
        pg.zoom = zoom
        pg.lmode = lmode
        pg.msel = msel
        if probe:
            pg.probe = True
            pg.pci = 1
            pg.pd = J("TreeClassOps").probeData(1)
        f0 = len(E.sent(P))
        P.pm.openCustomPage(P.ref, P.st, pg)
        pk = pkts(P, f0)
        E.pump(P)
        return pg, pk

    def click(a, raw=None):
        E.pump(P)
        f0 = len(E.sent(P))
        P.pm.handleLegacyCustomPageEvent(P.ref, P.st, E.CPE(E.CPT.Data, raw if raw is not None else '{"a":"%s"}' % a))
        pk = pkts(P, f0)
        return pk

    mining_t = TPAGE[TNAME.index("Mining")]
    smith_t = TPAGE[TNAME.index("Smithing")]
    combat_t = TPAGE[TNAME.index("Combat")]
    variants = []
    for t, nm in ((mining_t, "Gathering"), (smith_t, "Crafting"), (combat_t, "Adventure"), (NT, "Class")):
        for zi in range(ZN):
            variants.append((t, nm, zi, False))
    variants.append((NT, "Class", 0, True))
    # the probe Function that reads the bindings: CustomUIEventBinding data -> its strings
    bind_strs = {}
    total, bad, by_kind, warn0 = 0, [], {}, None
    for t, nm, zi, lm in variants:
        pg, pk = open_page(t, zi, lm)
        tag = "%s z%d%s" % (nm, zi, " Loadout" if lm else "")
        K.eq(len(pk), 1, "OPEN %s: one CustomPage packet" % tag)
        if not pk:
            continue
        txt = "\n".join(str(c.text) for c in cmds_of(pk[0]) if c.text is not None)
        els = elements(pk[0])
        K.check(els <= 1000, "OPEN %s: %d elements <= 1,000" % (tag, els))
        if not lm:
            lname = nm if nm != "Class" else "ClassWarrior"
            K.check(("SkyyTrees/Map/%s/Base.png" % lname) in txt and "#SkyyTrMN0B" in txt, "OPEN %s: the %s map page data is drawn" % (tag, lname))
            K.check(("LayoutMode: LeftScrolling" in txt) == (zi > 0), "OPEN %s: the 2-axis scroll box only above 100 %%" % tag)
            if zi == 2:
                K.check("Width: 1680, Height: 1548" in txt, "OPEN %s: the 200 %% canvas 1680 x 1548" % tag)
        else:
            K.check("#SkyyTrAp" in txt and "SkyyTrees/Map/" not in txt.replace("SkyyTrees/Map/Node/", "").replace("SkyyTrees/Map/Halo", ""), "OPEN %s: the Abilities well instead of the map" % tag)
        evs = pk[0].eventBindings if hasattr(pk[0], "eventBindings") else None
        acts = []
        for ev in (list(evs) if evs is not None else []):
            acc = []
            for f_ in ev.getClass().getDeclaredFields():
                f_.setAccessible(True)
                v_ = f_.get(ev)
                acc.append(str(v_))
            s_ = " ".join(acc)
            m_ = re.search(r'"a"\s*:\s*"([^"]+)"', s_) or re.search(r"a=([A-Za-z0-9:]+)", s_)
            acts.append(m_.group(1) if m_ else s_)
        if not acts:
            K.check(False, "ANSWER %s: bindings read from the packet" % tag)
            continue
        if not bind_strs:
            K.notes.append("a binding: %s" % acts[:3])
        bind_strs[tag] = acts
        K.eq(len(set(acts)), len(acts), "ANSWER %s: every event id unique (%d)" % (tag, len(acts)))
        for a in acts:
            pg, _pk = open_page(t, zi, lm)
            nets0 = int(pg.nets)
            pk2 = click(a)
            cur = P.pm.getCustomPage()
            total += 1
            kind = re.sub(r"\d+$", "", a)
            by_kind[kind] = by_kind.get(kind, 0) + 1
            if a.startswith("hub:"):
                ok = (len(pk2) == 1 and cur == pg) or (len(pk2) == 0 and cur is None)
            else:
                ok = len(pk2) == 1 and cur == pg and int(pg.nets) == nets0
            if not ok:
                bad.append((tag, a, len(pk2), cur is None, int(pg.nets) - nets0))
    K.eq(bad[:8], [], "ANSWER: %d bound events on %d page variants, each answered by exactly ONE page packet (hub X / Home = the close)" % (total, len(variants)))
    K.notes.append("ANSWER: %s" % ", ".join("%s %d" % kv for kv in sorted(by_kind.items())))
    json.dump(bind_strs, open(os.path.join(scratch, "binds.json"), "w"))
    # the safety net: unknown data, no 'a', a bad node number, no data
    pg, _pk = open_page(mining_t)
    for raw, what in (('{"a":"zzz"}', "unknown data"), ('{"b":"x"}', "no 'a' field"), ('{"a":"tmt999"}', "an unknown tree"),
                      ('{"a":"tmp9"}', "an unknown page"), ("not json", "not JSON"), ('{"a":"tyca9"}', "a Loadout click off the Class page")):
        n0 = int(pg.nets)
        pk2 = click(None, raw)
        K.check(len(pk2) == 1 and P.pm.getCustomPage() == pg and int(pg.nets) == n0 + 1 and not cmds_of(pk2[0]),
                "NET %s = ONE empty update (the safety net)" % what)
    for raw in ('{"a":"tmnzz"}', '{"a":"tmn99999"}'):
        n0 = int(pg.nets)
        pk2 = click(None, raw)
        K.check(len(pk2) == 1 and int(pg.nets) == n0 and "not on this page" in str(pg.msg), "NET a bad node number %s = the page's own answer (one rebuild + a line)" % raw)
    n0 = int(pg.nets)
    f0 = len(E.sent(P))
    pg.handleDataEvent(P.ref, P.st, None)
    K.check(len(pkts(P, f0)) == 1 and int(pg.nets) == n0 + 1, "NET no data = ONE empty update")

    # ---- FLOW: select a ready node, Learn, the picture + spoke change; Respec twice
    LV["lv"] = 30
    pg, pk = open_page(mining_t)
    d2 = St.data(u2)
    codes = [int(x) for x in TM.nodes(0)]
    s_ = [int(x) for x in TM.stat(u2, d2, mt, False)]
    g_ = [int(x) for x in V.gates(mt)]
    ready = [k for k, c in enumerate(codes) if c >= 0 and UT[c] == mt and int(V.ustate(d2, c, s_[0], s_[1], g_)) == 1 and int(d2.rk[c]) == 0]
    K.check(len(ready) > 0, "FLOW the mid player has ready Mining nodes (%d)" % len(ready))
    k = ready[0]
    c = codes[k]
    pk = click("tmn%d" % k)
    K.check(len(pk) == 1 and int(pg.msel) == k, "FLOW a node click selects it (one packet)")
    txt = "\n".join(str(x.text) for x in cmds_of(pk[0]) if x.text is not None) + "\n" + E.strs_of(P, len(E.sent(P)) - 1)
    K.check(str(V.UNAME[c]) in txt and "Ready to unlock" in txt and "SkyyTrMSel" in txt, "FLOW the panel names it + Ready to unlock + the halo")
    K.check('TextButton #SkyyTrMLe' in txt and "Primary" in txt, "FLOW Learn is the Primary button")
    pk = click("trbuy")
    K.check(len(pk) == 1 and int(St.data(u2).rk[c]) == 1, "FLOW Learn buys rank 1 (one packet)")
    tex = jpype.JArray(JString)(len(codes))
    lit = jpype.JArray(jpype.JBoolean)(len(TM.edges(0)))
    TM.paint(u2, St.data(u2), 0, False, tex, lit)
    K.eq(str(tex[k]), "%sL1%d" % (str(TM.CPIC[mt]), UMAX[c]) if UMAX[c] > 1 else "%sMax1" % str(TM.CPIC[mt]), "FLOW its picture is learnt 1 / m now")
    spokes = [e for e, x in enumerate([int(y) for y in TM.edges(0)]) if x == -(c + 1)]
    K.check(all(bool(lit[e]) for e in spokes), "FLOW its spoke is lit (%d)" % len(spokes))
    sp0 = int(V.spent(St.data(u2), mt))
    click("trrespec")
    K.check(int(V.spent(St.data(u2), mt)) == sp0 and int(pg.armT) == mining_t, "FLOW Respec click 1 arms only")
    pk = click("trrespec")
    K.check(len(pk) == 1 and int(V.spent(St.data(u2), mt)) == 0, "FLOW Respec click 2: every Mining point back (the free respec)")
    # zoom in / out, clamped
    for a, want in (("tmzi", 1), ("tmzi", 2), ("tmzi", 2), ("tmzo", 1), ("tmzo", 0), ("tmzo", 0)):
        pk = click(a)
        K.check(len(pk) == 1 and int(pg.zoom) == want, "FLOW %s -> zoom %d" % (a, want))
    # a node of another tree on the same page switches the head + LASTTREE
    codes = [int(x) for x in TM.nodes(0)]
    kf = [k_ for k_, c_ in enumerate(codes) if int(TM.nodeTv(c_)) == TNAME.index("Fishing")][0]
    pk = click("tmn%d" % kf)
    K.check(len(pk) == 1 and int(pg.tree) == TPAGE[TNAME.index("Fishing")] and int(Pg.LASTTREE.get(u2)) == int(pg.tree), "FLOW a Fishing node -> the Fishing head (LASTTREE)")
    # rail rows
    pk = click("tmp1")
    K.check(len(pk) == 1 and int(pg.tree) == TPAGE[int(TM.PTV[int(TM.PT0[1])])] and int(pg.msel) == -1, "FLOW rail Crafting -> its first tree, no selection")
    pk = click("tmt%d" % TNAME.index("Beastmastery"))
    K.check(len(pk) == 1 and int(pg.tree) == TPAGE[TNAME.index("Beastmastery")], "FLOW rail tree row Beastmastery")
    pk = click("tmc")
    K.check(len(pk) == 1 and int(pg.tree) == NT, "FLOW rail class row -> the Class page")
    pk = click("tmlo")
    K.check(len(pk) == 1 and bool(pg.lmode), "FLOW Loadout")
    pk = click("tmlo")
    K.check(len(pk) == 1 and not bool(pg.lmode), "FLOW Talents (back to the map)")
    pk = click("tmp0")
    K.check(len(pk) == 1 and int(pg.tree) == TPAGE[TNAME.index("Mining")], "FLOW rail Gathering -> Mining")
    # Nexus: hidden without SkyyRebirth; with rebirth:fn:open (answers TRUE but opens nothing here) -> our one answer; without it the
    # /rebirth fallback (no CommandManager in the harness) -> a line
    txt = E.strs_of(P, 0)
    K.check("SkyyTrMRp4" not in "\n".join(str(x.text) for x in cmds_of(pk[0]) if x.text is not None), "FLOW the Nexus row is hidden without SkyyRebirth")
    called = []
    br.put("rebirth:fn:count", _fn(JImplements, JOverride, lambda a: Int(0)))
    br.put("rebirth:fn:open", _fn(JImplements, JOverride, lambda a: (called.append(len(a)), JClass("java.lang.Boolean").TRUE)[1]))
    pg, pk = open_page(mining_t)
    K.check("#SkyyTrMRp4" in "\n".join(str(x.text) for x in cmds_of(pk[0]) if x.text is not None), "FLOW the Nexus row shows with SkyyRebirth")
    pk = click("tmnx")
    K.check(called == [2] and len(pk) == 1 and P.pm.getCustomPage() == pg and str(pg.msg) == "", "FLOW Nexus -> rebirth:fn:open { Ref, Store }, page still ours -> one answer")
    br.remove("rebirth:fn:open")
    pk = click("tmnx")
    K.check(len(pk) == 1 and P.pm.getCustomPage() == pg and str(pg.msg) in ("The Rebirth Nexus could not open here - try /rebirth", "The Rebirth Nexus did not open - see the chat line (Rebirth may be off on this server)"),
            "FLOW Nexus without rebirth:fn:open: the /rebirth fallback ran, nothing replaced our page -> one answer (%r)" % str(pg.msg))
    br.remove("rebirth:fn:count")
    # the class probe page: learns on its copy only
    pg, pk = open_page(NT, probe=True)
    codes = [int(x) for x in TM.nodes(int(TM.NSP) + 1)]
    pd = pg.pd
    s_ = [int(x) for x in TM.stat(u2, pd, 1, True)]
    g_ = [int(x) for x in V.gates(1)]
    rk = [k_ for k_, c_ in enumerate(codes) if c_ >= 0 and int(V.ustate(pd, c_, s_[0], s_[1], g_)) == 1]
    if rk:
        click("tmn%d" % rk[0])
        before = int(St.data(u2).rk[codes[rk[0]]])
        pk = click("trbuy")
        K.check(len(pk) == 1 and int(pd.rk[codes[rk[0]]]) >= 1 and int(St.data(u2).rk[codes[rk[0]]]) == before and "probe" in str(pg.msg),
                "FLOW probe: Learn changes the probe copy only: %s" % str(pg.msg)[:80])
    else:
        K.notes.append("probe: no ready class node (SkyyClasses absent: the class upgrades are dead here)")
        pk = click("trbuy")
        K.check(len(pk) == 1, "FLOW probe Learn with nothing selected answers once")
    # FIX (critic 1): a selection made on one layout is dropped when the layout under the open page changes (class / profile switch):
    # Learn then buys nothing and the map shows no halo
    pg, pk = open_page(NT, probe=True)
    pk = click("tmn0")
    K.check(len(pk) == 1 and int(pg.msel) == 0 and int(pg.mselL) == int(TM.NSP) + 1, "FIX1 a class-1 node click remembers its layout")
    pg.pci = 2
    pg.pd = J("TreeClassOps").probeData(2)
    pd2 = pg.pd
    sp2 = int(V.spent(pd2, 2))
    pk = click("trbuy")
    txt = "\n".join(str(x.text) for x in cmds_of(pk[0]) if x.text is not None) if pk else ""
    K.check(len(pk) == 1 and str(pg.msg) == "Click a talent on the map first" and int(V.spent(pd2, 2)) == sp2 and int(pg.msel) == -1
            and "SkyyTrMSel" not in txt, "FIX1 class changed under the page: Learn buys nothing, no halo (%r)" % str(pg.msg))
    # FIX (critic 3 #2): every map-page label is readable (>= 14 px; docs/answered/ui.md 'readable' 14-18 px)
    for t_ in (mining_t, NT):
        pg, pk = open_page(t_, probe=(t_ == NT))
        txt = "\n".join(str(x.text) for x in cmds_of(pk[0]) if x.text is not None) if pk else ""
        small = []
        for m_ in re.finditer(r"Label #(SkyyTrM\w*) \{", txt):
            seg = txt[m_.end():]
            nxt = re.search(r"(Label|Group|TextButton|Button|ItemIcon) #", seg)
            seg = seg[:nxt.start()] if nxt else seg
            f_ = re.search(r"FontSize: (\d+)", seg)
            if f_ and int(f_.group(1)) < 14:
                small.append((m_.group(1), int(f_.group(1))))
        K.check(len(pk) == 1 and "Label #SkyyTrM" in txt and not small, "FIX2 page %d: no map label under 14 px %s" % (t_, small[:6]))
    # elements with every line lit (the full player)
    P3 = E.player(uid=u3, name="SkyyTreeFull")
    E.pump(P3)
    for t in (mining_t, combat_t, smith_t):
        pg3 = Pg(P3.pr, t)
        f0 = len(E.sent(P3))
        P3.pm.openCustomPage(P3.ref, P3.st, pg3)
        pk = [p for p in E.sent(P3)[f0:] if str(p.getClass().getSimpleName()) == "CustomPage"]
        K.check(len(pk) == 1 and elements(pk[0]) <= 1000, "OPEN full player tree %d: %d elements <= 1,000" % (t, elements(pk[0]) if pk else -1))
        E.pump(P3)
    K.save()


def run_live(out, jar, scratch, home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    import jpype
    from jpype import JClass, JString
    J = lambda n: JClass(PKG + n)

    def start():
        out_, bad_ = T46.live_start(home)
        out_.append(str(J("TreeMigP7").run(JClass("java.nio.file.Paths").get(home))))
        return out_, bad_
    fp = os.path.join(home, "trees.properties")
    t0 = open(fp, "rb").read()
    msgs, bad = start()
    K.eq(bad, [], "LIVE every player file reads")
    # the live world has not started 0.4.9 yet (pinned + deployed the same day): its TreeMigP7 may run once here; 0.5.0 adds no update
    K.check(all(m == "" for m in msgs[:-2]) and (msgs[-1] == "" or "SkyyTrees 0.4.9" in msgs[-1]),
            "LIVE start 1: no update but 0.4.9's own TreeMigP7: %s" % [m[:70] for m in msgs if m][:3])
    po, pn = T46._props(t0), T46._props(open(fp, "rb").read())
    K.eq(sorted(k for k in set(po) | set(pn) if po.get(k) != pn.get(k)), [], "LIVE start 1: no setting changes (at most 0.4.9's run-once marker)")
    h1 = T46.tree_hash(home)
    msgs2, bad2 = start()
    K.check(T46.tree_hash(home) == h1 and bad2 == [], "LIVE start 2 changes nothing")
    TM, St = J("TreeMap"), J("TreeStore")
    names = set()
    z = zipfile.ZipFile(jar)
    pics = set(n.split("/")[-1][:-7] for n in z.namelist() if n.startswith(MAPDIR + "Node/"))
    painted = 0
    for f in sorted(os.listdir(os.path.join(home, "players"))):
        if not f.endswith(".properties"):
            continue
        d = St.readFile(f[:-11])
        for L in range(NL):
            codes = TM.nodes(L)
            tex = jpype.JArray(JString)(len(codes))
            lit = jpype.JArray(jpype.JBoolean)(len(TM.edges(L)))
            TM.paint(None, d, L, False, tex, lit)
            names |= set(str(x) for x in tex)
            painted += 1
    K.check(painted > 0 and names <= pics, "LIVE %d live player x layout maps painted, every picture shipped (%s)" % (painted, sorted(names - pics)[:4]))
    K.save()


EXPECT.update({   # checked 2026-10-22: the version text (CfgFn opExport, CfgRows <clinit> / header, TreeCfg load), the ready line (setup), the page
    "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "SkyyTreesPlugin": ["~m setup"], "TreeCfg": ["~m load"],
    "TreePage": ["+f answered", "+f answers", "+f lastEls", "+f lmode", "+f msel", "+f mselL", "+f nets", "+f zoom", "+m ans", "+m curLayout", "+m go",
                 "+m handleIn", "+m nexus", "+m num", "+m stillOpen", "-f sel", "-f vbr", "-f vsel", "-m buildClass", "~c ", "~m build",
                 "~m handleDataEvent"]})   # simplify pass 1: sel / vbr / vsel (read only by the unused 0.4.x builders) removed
MAP_ENTRY = re.compile(r"\A(?:Common/UI/Custom/SkyyTrees/Map/|com/skyy/trees/map/)")
_ORIG_COMPARE = HK.run_compare


def _compare(out, jar, old_jar, pkg, expect, added, removed=()):
    """the kit compare on a copy of the new jar WITHOUT the map entries (run_jar checks them and that nothing else but the manifest changed)"""
    cp = os.path.join(SCRATCH, "compare-%s.jar" % VERSION)
    with zipfile.ZipFile(jar) as zi, zipfile.ZipFile(cp, "w", zipfile.ZIP_DEFLATED) as zo:
        for n in zi.namelist():
            if not MAP_ENTRY.match(n):
                zo.writestr(n, zi.read(n))
    _ORIG_COMPARE(out, cp, old_jar, pkg, expect, added, removed)


HK.run_compare = _compare

if __name__ == "__main__":
    HK.run(name="SkyyTrees", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("jar", run_jar), ("old", run_old), ("data", run_data), ("exec", run_exec), ("live", run_live)],
           script=__file__, live=(LIVE_DIR, "Skyy_SkyyTrees"))
