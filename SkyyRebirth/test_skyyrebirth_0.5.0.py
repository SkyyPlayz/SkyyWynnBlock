"""SkyyRebirth 0.5.0 - harness for THE NEXUS AS A RADIAL MAP (tools/rebirth_0_5_0_patch.py; research/Radial-Trees-Spec.md round R3).
Build first: python tools/rebirth_0_5_0_patch.py && python SkyyRebirth/build_skyyrebirth_0.5.0.py

    python SkyyRebirth/test_skyyrebirth_0.5.0.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Phases (tools/harness_kit.py, fresh child JVMs, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  S    static   the patch re-runs to identical bytes; line endings kept; no new command / system
  J    jar      every map picture under Common/UI/Custom/SkyyRebirth/Map/ (@2x, even sizes, no underscore), no .ui file, the 3 page data
                files; every texture the page data names is shipped; the map RE-CHECKED on the coordinates parsed back out of the jar (each
                zoom: discs inside the canvas, >= 6 px apart, click squares apart, clear of the black hole; the 11 arm names inside the
                canvas and clear of every disc and of each other; all 21 nodes once, node k = RbTree node k)
  A    verify   every class loads + initialises (-Xverify:all)
  C    compare  0.4.3 -> 0.5.0: exactly the planned members (EXPECT; the map files are checked by J)
  V / F41 / F43 / L42   the 0.4.0 / 0.4.1 / 0.4.3 / 0.4.2 harness phases against the 0.5.0 jar (VP, buy, respec, migration, the gate, the
                Beastmastery VP, the live config started twice) - every rule unchanged
  P    page     the page built for real (UICommandBuilder, bare JVM): both views at every zoom through the kit checks (check_page, sky
                paths, assert_menu_page: 1600 x 980, rows 1 + 2, NO sub row), every b.set / binding names an element that exists, the 21
                node clicks n0..n20 + the black hole + Learn / Respec / Close, the requirements tooltip only on the black hole, the panel
                texts fit at 424 px, the worth line in the panel, <= 1,000 elements with every line lit
  X    exec     the SkyyMenu 0.3.19 harness engine (a player with the REAL PageManager + a recording packet handler) - EXECUTED:
       ANSWER   on every page variant (rebirth view / node view x 3 zooms), EVERY bound event read back out of the packet, clicked on a
                fresh page = exactly ONE page packet and the page still open, or the close (Close / the hub X); the safety net never needed
                for a bound event; unknown data / no 'a' = ONE empty update (the net)
       GOLD     RbMap.paint for a fresh / one-tool / full profile = the picture rule + the gold path rule, every picture name shipped
       FLOW     a node click selects it; Learn buys a rank (VP down, its picture + its gold path in the next packet); Respec twice (Void
                Charm) = every VP back; zoom in / out (clamped, the scroll box above 100 %); the black hole click (nothing to do = one
                answer); the rail: Gathering / Crafting / Adventure / Class run /tree mining | smithing | combat | class as the player (or
                tree:fn:classPage) and answer once while the page is still ours; "Your rebirth" = the rebirth view
  O    open     rebirth:fn:open: { Ref, Store } opens the page at once in place of another; { UUID } queues it on the player's world
                thread (TRUE) and the queued task opens it; rebirth off for a player = FALSE (nothing opened); junk = FALSE
  AA   engine-access audit
NOT COVERED (UNVERIFIED in game): the look on Skyy's screen (sizes, the Nexus art at 100 / 150 / 200 %), the black hole tooltip text
(unchanged 0.4.x code), the client scroll position after a click at 150 / 200 %, SkyyTrees opening its own pages from our rail.
"""
import os, sys, json, re, subprocess, importlib.util, zipfile, math, struct

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "radialr3", "rb")]
import skyybuild as B
import harness_kit as HK
import skyyui as SUI
import skyymap as SMAP


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp)
    _argv = list(sys.argv)
    sp.loader.exec_module(m)
    sys.argv[:] = _argv
    return m


VERSION = "0.5.0"
RB = "com.skyy.rebirth."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyRebirth-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyRebirth-0.4.3.jar")
GEN = os.path.join(HERE, "build_skyyrebirth_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyrebirth_0.4.3.py")
PATCH = os.path.join(TOOLS, "rebirth_0_5_0_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
T43 = _load("t_rb043", os.path.join(HERE, "test_skyyrebirth_0.4.3.py"))
T42, T41, T40 = T43.T42, T43.T41, T43.T40
for _m in (T43, T42, T41, T40, T40.T34):
    _m.VERSION, _m.JAR = VERSION, JAR
R = T40.R
ADDED = ["RbMap", "RbOpen"]
MAPRES = "com/skyy/rebirth/map/"
MAPDIR = "Common/UI/Custom/SkyyRebirth/Map/"
ZN = 3
RX = re.compile(r'#(\w+) \{ Anchor: \(Left: (-?\d+), Top: (-?\d+), Width: (\d+), Height: (\d+)\); Background: "([^"]+)"')
LX = re.compile(r'#(SkyyRbMAl\d+) \{ Anchor: \((?:Left: (-?\d+), Top: (-?\d+), )?Width: (\d+), Height: (\d+)(?:, Left: (-?\d+), Top: (-?\d+))?')
PROFILE = "n=2\nv=4\nvp=76\nvpSpent=36\nnode.Void.insight=2\nnode.Hand.farming=1\nnode.Mining.tool=1\n"
EXPECT = {   # checked 2026-10-22 (the first compare run): the version text, the setup / shutdown bridge key, the page
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "RbMig": ["~m migrate"], "RbStore": ["~m writeNow"],
    "SkyyRebirthPlugin": ["~m setup", "~m shutdown"],
    "RbCheck": ["~m tip"],   # fix round: the black hole tooltip names the right panel + Learn
    "RbPage": ["+f answered", "+f answers", "+f mapEls", "+f msg", "+f nets", "+f nvWorth", "+f railSub", "+f zoom", "+m ans", "+m handleIn",
               "+m stillOpen", "+m trees", "~m build", "~m buy", "~m fill", "~m fillNode", "~m fillTree", "~m handleDataEvent"],
}


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyRebirth 0.5.0 - build script') and g.count('VERSION = "0.5.0"') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.check("(or Your rebirth on the left, then Rebirth on the right)" in g and "(or Your rebirth on the left, then Continue on the right) twice" in g and "see it on the right, then Learn ranks" in g
            and "on the left)" not in g and "Buy ranks" not in g, "S FIX1: all three tooltip lines (rebirth / continue / the Nexus) name the right panel + Learn")
    K.save()


def parse(z, zi):
    """the page data of zoom zi -> (text, nodes [(k, l, t, s)], statics [(id, path, l, t, w, h)], edges {k: (l, t, w, h, path)}, labels [(id, l, t, w, h)])"""
    t = z.read(MAPRES + "Z%d.txt" % zi).decode("utf-8")
    nodes, statics, edges, labels = [], [], {}, []
    for ln in t.split("\n"):
        if not ln:
            continue
        f = ln.split("\t")
        if f[0] == "N":
            m = RX.search(f[2] + "Locked" + f[3])
            nodes.append((int(f[1]), int(m.group(2)), int(m.group(3)), int(m.group(4)), f[4], f[5], f[6], f[7]))
        elif f[0] == "A":
            m = RX.search(f[2])
            if m:
                statics.append((m.group(1), m.group(6), int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5))))
            ml = re.search(r"#(SkyyRbMAl\d+) \{", f[2])
            if ml:
                a = dict(re.findall(r"(Left|Top|Width|Height): (-?\d+)", f[2]))
                labels.append((ml.group(1), int(a["Left"]), int(a["Top"]), int(a["Width"]), int(a["Height"]), f[2]))
        elif f[0] == "E":
            m = RX.search(f[2])
            edges[int(f[1])] = (int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5)), m.group(6))
    return t, nodes, statics, edges, labels


def run_jar(out, jar, scratch, _home):
    K = HK.Child(out)
    z = zipfile.ZipFile(jar)
    names = z.namelist()
    K.check(not [n for n in names if n.lower().endswith(".ui")], "J no .ui file (inline pages only)")
    pics = [n for n in names if n.startswith(MAPDIR)]
    K.check(len(pics) > 40 and all(n.endswith("@2x.png") and "_" not in n.split("/")[-1] for n in pics), "J %d map pictures, all @2x, no underscore" % len(pics))
    bad = []
    for n in pics:
        w, h = struct.unpack(">II", z.read(n)[16:24])
        if w % 2 or h % 2:
            bad.append(n)
    K.eq(bad, [], "J every picture has even sizes (@2x)")
    K.eq(sorted(n for n in names if n.startswith(MAPRES)), [MAPRES + "Z%d.txt" % i for i in range(ZN)], "J the 3 page data files")
    other = [n for n in names if not n.endswith(".class") and not n.startswith(MAPDIR) and not n.startswith(MAPRES)
             and not n.startswith("Common/UI/Custom/SkyyKit/") and n != "manifest.json"]
    K.eq(other, [], "J nothing else beside classes, the kit art, the map files and the manifest")
    shipped = set(n[len("Common/UI/Custom/"):].replace("@2x.png", ".png") for n in pics)
    for zi in range(ZN):
        t, nodes, statics, edges, labels = parse(z, zi)
        zf = (1.0, 1.5, 2.0)[zi]
        W, H = int(round(840 * zf)), int(round(774 * zf))
        refs = set(re.findall(r'"(SkyyRebirth/Map/[^"]+\.png)"', t))
        K.check("@2x" not in t and refs and all(r_ in shipped for r_ in refs if "/Node/" not in r_ or r_.endswith("Locked.png")),
                "J z%d: every texture the page data names is shipped, written without @2x (%d)" % (zi, len(refs)))
        K.eq([n[0] for n in nodes], list(range(21)), "J z%d: 21 nodes, in RbTree order" % zi)
        emb = [s for s in statics if s[0] == "SkyyRbMEm"]
        K.check(len(emb) == 1 and emb[0][1].endswith("Map/Nexus.png") and emb[0][4] == int(round(140 * zf)), "J z%d: the black hole picture" % zi)
        ex, ey, er = emb[0][2] + emb[0][4] / 2.0, emb[0][3] + emb[0][5] / 2.0, emb[0][4] / 2.0
        mg, out_, hit = 1e9, [], []
        for i, (k, l, t_, s, *_r) in enumerate(nodes):
            if not (l >= 4 and t_ >= 4 and l + s <= W - 4 and t_ + s <= H - 4):
                out_.append(k)
            mg = min(mg, math.hypot(l + s / 2.0 - ex, t_ + s / 2.0 - ey) - s / 2.0 - er)
            for (k2, l2, t2, s2, *_r2) in nodes[i + 1:]:
                g = math.hypot(l + s / 2.0 - l2 - s2 / 2.0, t_ + s / 2.0 - t2 - s2 / 2.0) - (s + s2) / 2.0
                mg = min(mg, g)
                h1, h2 = int(round(s * 26 / 32.0)), int(round(s2 * 26 / 32.0))
                o1, o2 = (s - h1) // 2, (s2 - h2) // 2
                if max(l2 + o2 - (l + o1 + h1), l + o1 - (l2 + o2 + h2), t2 + o2 - (t_ + o1 + h1), t_ + o1 - (t2 + o2 + h2)) < 2:
                    hit.append((k, k2))
        K.check(not out_ and mg >= 6 and not hit, "J z%d: discs inside, >= 6 px apart (min %.1f), click squares apart (%s), off the black hole" % (zi, mg, hit[:3]))
        K.check(len(labels) == 11, "J z%d: 11 arm names" % zi)
        lb = []
        for i, (lid, l, t_, w, h, mk) in enumerate(labels):
            if not (l >= 4 and t_ >= 4 and l + w <= W - 4 and t_ + h <= H - 4):
                lb.append((lid, "outside"))
            for (k, nl, nt, s, *_r) in nodes:
                if SMAP._box_circle_gap(l, t_, w, h, nl + s / 2.0, nt + s / 2.0, s / 2.0) < 6:
                    lb.append((lid, "disc %d" % k))
            for (lid2, l2, t2, w2, h2, _m) in labels[i + 1:]:
                if max(l2 - (l + w), l - (l2 + w2), t2 - (t_ + h), t_ - (t2 + h2)) < 6:
                    lb.append((lid, lid2))
        K.eq(lb, [], "J z%d: the arm names inside the canvas, clear of every disc and of each other" % zi)
        K.check(len(edges) == 25 and all(e[4].startswith("SkyyRebirth/Map/E") for e in edges.values()), "J z%d: 25 drawn lines with their gold picture" % zi)
    K.save()


def _strs(pkt_or_b):
    return pkt_or_b


def run_page(out, jar, scratch, _home):
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    from jpype import JClass
    K = HK.Child(out)
    Bag, Part, Const = T40.fakes()
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    Cfg, St, Tr = R("RbCfg"), R("RbStore"), R("RbTree")
    home, pl, U, k = T40.world(scratch, "p")
    f = os.path.join(pl, k + ".properties")
    open(f, "w").write(PROFILE)
    Cfg.BRIDGE.put("acc:defs", T40.DEFS)
    Cfg.BRIDGE.put("acc:fn:bag", Bag(["Skyy_Talisman_Lantern_Common"]))
    Cfg.PERM_TEST = Const(JClass("java.lang.Boolean").TRUE)
    LIN_W = SUI.DETAIL_W - 24 - 8
    with zipfile.ZipFile(jar) as zj:   # the build registered its map pictures with the kit; the harness registers the shipped ones
        SUI.register_map_textures([n[len("Common/UI/Custom/"):].replace("@2x.png", ".png") for n in zj.namelist() if n.startswith(MAPDIR)])
    DECL = re.compile(r"\b([A-Za-z]+) #([A-Za-z0-9]+) \{")

    def built(pg, what):
        b_, e_ = UCB(), UEB()
        pg.build(None, b_, e_, None)
        c = T40.cmds_of(b_)
        ev = T40.events_of(e_)
        apps = SUI.Appends([(None if s_ is None else s_.lstrip("#"), t_) for ty, s_, t_, d_ in c if t_ is not None and ty and "Append" in ty])
        sets = [(s_, d_) for ty, s_, t_, d_ in c if ty == "Set"]
        try:
            SUI.check_page(apps, "Skyy")
            SUI.check_sky_paths(apps, tab_icons=True)
            info = SUI.assert_menu_page(apps, hub="character", what="P " + what, sets=[(s_, T40.unq(d_)) for s_, d_ in sets])
            K.check(info["rows"] == 2 and info["subs"] == 0, "P %s: check_page + sky paths + assert_menu_page (1600 x 980, rows 1 + 2, no sub row)" % what)
        except Exception as ex:
            K.check(False, "P %s: the page checks: %s" % (what, ex))
        ids = set()
        for _p, mk in apps:
            ids |= set(x.group(2) for x in DECL.finditer(SUI.render(mk)))
        bad = [s_ for s_, _d in sets if s_.lstrip("#").split(".")[0] not in ids] + [s_ for s_, _d in ev if s_.lstrip("#") not in ids]
        K.check(not bad, "P %s: every b.set / binding names an element that exists (%d sets, %d bindings): %s" % (what, len(sets), len(ev), bad[:4]))
        els = sum(SUI._strip_quoted(t_).count("{") for ty, s_, t_, d_ in c if t_ is not None and ty and "Append" in ty)
        return c, ev, dict((s_, T40.unq(d_)) for s_, d_ in sets), els

    def fits(sets, what):
        rows = {"SkyyRbNv": 13, "SkyyRbPt": 13, "SkyyRbVp": 13, "SkyyRbReq": 13}
        over = []
        for s_, v_ in sets.items():
            idv = s_.lstrip("#").split(".")[0]
            if not s_.endswith(".Text") or not any(idv.startswith(r_) for r_ in rows):
                continue
            lines = SUI.text_lines(v_, LIN_W, SUI.fs(16 if idv == "SkyyRbNvName" else 13), bold=idv in ("SkyyRbNvName", "SkyyRbNvSub", "SkyyRbNvLevel", "SkyyRbNvStatus"))
            mx = {"SkyyRbNvLive": 3, "SkyyRbNvStatus": 3, "SkyyRbNvNow": 2, "SkyyRbNvNext": 2, "SkyyRbNvKeep": 2, "SkyyRbPtHand": 2, "SkyyRbNvWorth": 2}.get(idv, 1)
            if lines > mx:
                over.append((idv, v_, lines))
        K.check(not over, "P %s: every panel text fits its rows at 424 px: %s" % (what, over[:3]))
    nodes = ["SkyyRbMN%dB" % i for i in range(21)]
    I = lambda nid: int(Tr.idx(nid))
    for zi in range(ZN):
        pg = R("RbPage")(U, "hub")
        pg.zoom = zi
        c0, ev0, s0, els0 = built(pg, "rebirth view z%d" % zi)
        binds = sorted(s_.lstrip("#") for s_, _d in ev0)
        K.check(all(n_ in binds for n_ in nodes) and "SkyyRbNexusB" in binds and "SkyyRbClose" in binds and "SkyyRbMN21B" not in binds
                and "SkyyRbMZmO" in binds and "SkyyRbMZmI" in binds and "SkyyRbMRyB" not in binds, "P z%d: 21 node bindings + the black hole + Close + zoom" % zi)
        acts = [T40.unq(d_) for _s, d_ in ev0]
        K.check(all(("n%d" % i) in acts for i in range(21)), "P z%d: node k binds 'n<k>' (the 0.4.x click ids)" % zi)
        tips = [s_ for s_ in s0 if s_.endswith(".TooltipText")]
        K.check(tips == ["#SkyyRbNexusB.TooltipText"], "P z%d: the only tooltip is the black hole's requirements (no node hovers - probe M6 not run): %s" % (zi, tips))
        tt = s0.get("#SkyyRbNexusB.TooltipText", "")
        K.check("on the left)" not in tt and "Buy ranks" not in tt and "see it on the right, then Learn ranks" in tt,
                "P z%d FIX1: the black hole tooltip names the right panel + Learn (no 'on the left' / 'Buy ranks')" % zi)
        K.check(s0.get("#SkyyRbTop.Text", "").startswith("Holding 76 VP: +19 % XP - spent 36 VP"), "P z%d: the VP counter: %r" % (zi, s0.get("#SkyyRbTop.Text")))
        K.check(s0.get("#SkyyRbMZmL.Text") == "%d %%" % (100, 150, 200)[zi], "P z%d: the zoom label" % zi)
        txt = "\n".join(t_ for ty, s_, t_, d_ in c0 if t_)
        K.check(("LayoutMode: LeftScrolling" in txt) == (zi > 0), "P z%d: the 2-axis scroll box only above 100 %%" % zi)
        K.check("SkyyRebirth/Map/Base.png" in txt and "SkyyRebirth/Map/Nexus.png" in txt, "P z%d: the map page data is drawn" % zi)
        K.check("SkyyRebirth/Map/Node/Locked.png" in txt and "locked - Hand Echo full" in txt, "P z%d FIX2: the legend has the padlock row" % zi)
        fits(s0, "rebirth view z%d" % zi)
        pg.handleDataEvent(None, None, '{"a":"n0"}')
        c1, ev1, s1, els1 = built(pg, "node view z%d" % zi)
        b1 = sorted(s_.lstrip("#") for s_, _d in ev1)
        K.check("SkyyRbBuy" in b1 and "SkyyRbRespec" in b1 and "SkyyRbClose" not in b1, "P z%d node view: Learn + Respec bound" % zi)
        K.check("Learn" in "\n".join(t_ for ty, s_, t_, d_ in c1 if t_ and "SkyyRbBuy" in t_), "P z%d: the button says Learn" % zi)
        K.check("SkyyRebirth/Map/Halo.png" in "\n".join(t_ for ty, s_, t_, d_ in c1 if t_), "P z%d node view: the halo on the selected node" % zi)
        K.check(s1.get("#SkyyRbNvWorth.Text") == "Worth +0.31 % all XP a VP (keeping: +0.25 % all XP a VP)" and s1.get("#SkyyRbNvCost.Text") == "Cost: 32 VP"
                and s1.get("#SkyyRbNvSub.Text") == "Beside the black hole", "P z%d node view: worth line + cost + place: %s" % (zi, [s1.get("#SkyyRbNvWorth.Text"), s1.get("#SkyyRbNvSub.Text")]))
        fits(s1, "node view z%d" % zi)
        K.check(max(els0, els1) <= 1000, "P z%d: %d / %d elements <= 1,000" % (zi, els0, els1))
    pg = R("RbPage")(U, "hub")
    pg.handleDataEvent(None, None, '{"a":"n%d"}' % I("Hand.cooking"))
    _c, _e, s2, _n = built(pg, "node view (Hand Cooking)")
    K.check(s2.get("#SkyyRbNvSub.Text") == "Cooking arm - the 6 Hand Echoes share 5 ranks" and s2.get("#SkyyRbNvLevel.Text") == "Rank 0 / 5 - Hand 1 / 5",
            "P a Hand Echo sits on its own skill's arm: %r" % s2.get("#SkyyRbNvSub.Text"))
    pg.handleDataEvent(None, None, '{"a":"n%d"}' % I("Mining.tool2"))
    _c, _e, s3, _n = built(pg, "node view (a tool)")
    K.check(s3.get("#SkyyRbNvSub.Text") == "Mining arm" and s3.get("#SkyyRbNvWorth.Text", "x") == "", "P a tool node: Mining arm, no worth line")
    pg.handleDataEvent(None, None, '{"a":"buy"}')
    K.check(str(pg.status).startswith("+Void-Forged Pick II rank 1 bought"), "P Learn from the page (inline job): %s" % pg.status)
    # every line lit (a full profile): the worst element count
    open(f, "w").write("n=9\nv=4\nvp=999999\n" + "".join("node.%s=%d\n" % (str(Tr.NID[i]), int(Tr.NMAX[i])) for i in range(21)))
    St.CACHE.clear()
    for zi in range(ZN):
        pg = R("RbPage")(U, "hub")
        pg.zoom = zi
        pg.handleDataEvent(None, None, '{"a":"n3"}')
        _c, _e, _s, els = built(pg, "full profile node view z%d" % zi)
        K.check(els <= 1000 and int(pg.mapEls) > 100, "P z%d full profile (every line lit): %d elements <= 1,000 (map %d)" % (zi, els, int(pg.mapEls)))
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
    from jpype import JClass, JImplements, JOverride, JString, JArray
    K = HK.Child(out)
    T19 = _load("test_skyymenu_0_3_19", os.path.join(ROOT, "SkyyMenu", "test_skyymenu_0.3.19.py"))
    hcls = os.path.join(scratch, "hcls_x")
    os.makedirs(hcls, exist_ok=True)
    os.chdir(scratch)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, hcls, jar], verify=True)
    E = T19.engine(scratch, hcls)
    Bag, Part, Const = T40.fakes()
    Cfg, St, Tr, Map, Pg = R("RbCfg"), R("RbStore"), R("RbTree"), R("RbMap"), R("RbPage")
    home, pl, U, k = T40.world(scratch, "x")
    f = os.path.join(pl, k + ".properties")
    Cfg.BRIDGE.put("acc:defs", T40.DEFS)
    bag = Bag(["Skyy_Talisman_Lantern_Common"])
    Cfg.BRIDGE.put("acc:fn:bag", bag)
    classpage = {"r": JClass("java.lang.Boolean").FALSE, "n": 0}
    Cfg.BRIDGE.put("tree:fn:classPage", _fn(JImplements, JOverride, lambda a: (classpage.__setitem__("n", classpage["n"] + 1), classpage["r"])[1]))
    I = lambda nid: int(Tr.idx(nid))
    P = E.player(uid=U, name="SkyyRebirthTester")
    z = zipfile.ZipFile(jar)
    shipped = set(n.split("/")[-1][:-7] for n in z.namelist() if n.startswith(MAPDIR + "Node/"))

    def profile(text):
        open(f, "w").write(text)
        St.CACHE.clear()

    def pkts(f0):
        return [p for p in E.sent(P)[f0:] if str(p.getClass().getSimpleName()) == "CustomPage"]

    def ptext(pkt):
        cs = pkt.commands if hasattr(pkt, "commands") else None
        return "\n".join(str(c.text) for c in (list(cs) if cs is not None else []) if c.text is not None)

    def open_page(view=0, sel=-1, zoom=0):
        E.pump(P)
        pg = Pg(P.pr)
        pg.view, pg.sel, pg.zoom = view, sel, zoom
        f0 = len(E.sent(P))
        P.pm.openCustomPage(P.ref, P.st, pg)
        pk = pkts(f0)
        E.pump(P)
        return pg, pk

    def click(a, raw=None):
        E.pump(P)
        f0 = len(E.sent(P))
        P.pm.handleLegacyCustomPageEvent(P.ref, P.st, E.CPE(E.CPT.Data, raw if raw is not None else '{"a":"%s"}' % a))
        pk = pkts(f0)
        E.pump(P)
        return pk

    def acts_of(pkt):
        evs = pkt.eventBindings if hasattr(pkt, "eventBindings") else None
        out_ = []
        for ev in (list(evs) if evs is not None else []):
            acc = []
            for f_ in ev.getClass().getDeclaredFields():
                f_.setAccessible(True)
                acc.append(str(f_.get(ev)))
            s_ = " ".join(acc)
            m_ = re.search(r'"a"\s*:\s*"([^"]+)"', s_) or re.search(r"a=([A-Za-z0-9:]+)", s_)
            out_.append(m_.group(1) if m_ else s_)
        return out_

    # ---- GOLD + the picture rule (fresh / one tool / full profile)
    def painted(text):
        profile(text)
        p_ = St.get(k)
        tex = JArray(JString)(21)
        lit = JArray(jpype.JBoolean)(len(Map.ELIT0))
        Map.paint(p_, True, tex, lit)
        return [str(x) for x in tex], [bool(x) for x in lit]
    t_, l_ = painted("n=1\nv=4\nvp=0\n")
    K.check(not any(l_) and all(x in ("Open", "Soon", "Ready") for x in t_), "GOLD fresh (0 VP): no gold line, every node open / coming soon: %s" % sorted(set(t_)))
    t_, l_ = painted("n=1\nv=4\nvp=500\nnode.Mining.tool=1\n")
    lit_k = [i for i, x in enumerate(l_) if x]
    _txt, _nodes, _st, edges, _lb = parse(z, 0)
    mine = I("Mining.tool")
    nx = [n for n in _nodes if n[0] == mine][0]
    em = [n for n in _nodes if n[0] == I("Mining.echo")][0]
    K.check(t_[mine] == "C8fc8ffL15" and t_[I("Mining.echo")] == "Ready" and t_[I("Mining.tool2")] == "Ready",
            "GOLD Mining Pick rank 1: its learnt picture (1 of 5 pips, Mining blue), its neighbours ready (500 VP): %s" % [t_[mine], t_[I("Mining.echo")]])
    ang = lambda x, y: math.degrees(math.atan2(x - 420.0, 387.0 - y)) % 360.0
    a_echo = ang(em[1] + 20, em[2] + 20)
    near = [kk for kk in lit_k if kk in edges and abs(((ang(edges[kk][0] + edges[kk][2] / 2.0, edges[kk][1] + edges[kk][3] / 2.0) - a_echo + 180) % 360) - 180) < 25]
    K.check(len(lit_k) == 3 and sorted(near) == sorted(lit_k), "GOLD the gold path black hole -> Mining Echo -> fork -> Pick (3 lines, all on the Mining arm): %s" % lit_k)
    t_, l_ = painted("n=9\nv=4\nvp=0\n" + "".join("node.%s=%d\n" % (str(Tr.NID[i]), int(Tr.NMAX[i])) for i in range(21)))
    K.check(all(l_[kk] for kk in edges) and all(x.endswith("Max%d" % int(Tr.NMAX[i])) for i, x in enumerate(t_)), "GOLD full: every drawn line gold, every node max")
    names = set()
    for txt_ in ("n=1\nv=4\nvp=0\n", "n=1\nv=4\nvp=9999\n", PROFILE, "n=1\nv=4\nvp=50\nnode.Hand.farming=2\nnode.Hand.cooking=3\n"):
        names |= set(painted(txt_)[0])
        for i in range(21):
            for rk in range(0, int(Tr.NMAX[i]) + 1):
                profile("n=1\nv=4\nvp=40\nnode.%s=%d\n" % (str(Tr.NID[i]), rk))
                names.add(str(Map.tex(St.get(k), i, True, 40)))
    K.check(names <= shipped, "GOLD every picture name RbMap.tex answers is shipped (%d names): %s" % (len(names), sorted(names - shipped)[:4]))
    profile("n=1\nv=4\nvp=50\nnode.Hand.farming=3\nnode.Hand.cooking=2\n")
    K.check(str(Map.tex(St.get(k), I("Hand.alchemy"), True, 50)) in ("Locked", "Soon"), "GOLD the 6th Hand Echo with all 5 Hand ranks placed: locked (or coming soon)")

    # ---- ANSWER: every bound event on every variant = one page packet
    variants = [(0, -1, zi) for zi in range(ZN)] + [(1, 0, zi) for zi in range(ZN)] + [(1, I("Beast.echo"), 0)]
    total, bad, kinds = 0, [], {}
    for view, sel, zi in variants:
        profile(PROFILE)
        bag.ids = ["Skyy_Talisman_Lantern_Common"]
        pg, pk = open_page(view, sel, zi)
        tag = "view %d sel %d z%d" % (view, sel, zi)
        K.eq(len(pk), 1, "OPEN %s: one CustomPage packet" % tag)
        if not pk:
            continue
        acts = acts_of(pk[0])
        K.eq(len(set(acts)), len(acts), "ANSWER %s: every event id unique (%d)" % (tag, len(acts)))
        for a in acts:
            profile(PROFILE)
            bag.ids = ["Skyy_Talisman_Lantern_Common"]
            pg, _pk = open_page(view, sel, zi)
            n0 = int(pg.nets)
            pk2 = click(a)
            cur = P.pm.getCustomPage()
            total += 1
            kind = re.sub(r"\d+$", "", a)
            kinds[kind] = kinds.get(kind, 0) + 1
            if a.startswith("hub:") or a == "close":
                ok = (len(pk2) == 1 and cur == pg) or (len(pk2) == 0 and cur != pg)
            else:
                ok = len(pk2) == 1 and cur == pg and int(pg.nets) == n0
            if not ok:
                bad.append((tag, a, len(pk2), cur == pg, int(pg.nets) - n0))
    K.eq(bad[:8], [], "ANSWER: %d bound events on %d page variants, each answered by exactly ONE page packet (Close / hub X = the close)" % (total, len(variants)))
    K.check(all(kk in kinds for kk in ("n", "nexus", "buy", "respec", "close", "rbzo", "rbzi", "rbtp", "rbnx", "back")),
            "ANSWER covered: %s" % ", ".join("%s %d" % kv for kv in sorted(kinds.items())))
    # the safety net: unknown data, no 'a'
    profile(PROFILE)
    pg, _pk = open_page()
    for raw, what in (('{"a":"zzz"}', "unknown data"), ('{"b":"x"}', "no 'a' field"), ('{"a":"rbtp9"}', "an unknown rail row"), ("", "no data")):
        n0 = int(pg.nets)
        pk2 = click(None, raw)
        K.check(len(pk2) == 1 and int(pg.nets) == n0 + 1 and P.pm.getCustomPage() == pg, "NET %s = ONE empty answer (the net)" % what)

    # ---- FLOW
    profile(PROFILE)
    bag.ids = ["Skyy_Talisman_Lantern_Common"]
    pg, pk = open_page()
    K.check("SkyyRbMRp0" in ptext(pk[0]) and "SkyyRbMRp4" in ptext(pk[0]), "FLOW the rail shows SkyyTrees' pages (tree:fn:classPage on the bridge) + Rebirth Nexus")
    ins = I("Void.insight")
    pk = click("n%d" % ins)
    K.check(len(pk) == 1 and int(pg.view) == 1 and int(pg.sel) == ins and "SkyyRebirth/Map/Halo.png" in ptext(pk[0]), "FLOW a node click selects it (halo, node view)")
    pk = click("buy")
    t1 = ptext(pk[0]) if pk else ""
    K.check(len(pk) == 1 and T40.props(f).get("node.Void.insight") == "3" and T40.props(f).get("vp") == "44" and "Cb58cffL35.png" in t1,
            "FLOW Learn: Void Insight rank 3, 32 VP spent, its picture 3 of 5 pips in the answer")
    pk = click("respec")
    K.check(len(pk) == 1 and "Press Respec again" in str(pg.status), "FLOW Respec press 1 = armed (one packet): %s" % pg.status)
    pg.respecArmed = pg.respecArmed - 2000
    pk = click("respec")
    K.check(len(pk) == 1 and "vpSpent" not in T40.props(f) and bag.ids == [None], "FLOW Respec press 2: every VP back, the Void Charm taken: %s" % pg.status)
    for a, want in (("rbzi", 1), ("rbzi", 2), ("rbzi", 2), ("rbzo", 1), ("rbzo", 0), ("rbzo", 0)):
        pk = click(a)
        K.check(len(pk) == 1 and int(pg.zoom) == want and (("LeftScrolling" in ptext(pk[0])) == (want > 0)), "FLOW %s -> zoom %d" % (a, want))
    pk = click("nexus")
    K.check(len(pk) == 1 and int(pg.view) == 0 and str(pg.last) == "=nothing", "FLOW the black hole with the requirements not met: back to the rebirth view, one answer (%s)" % pg.last)
    E.CM.lines.clear()
    classpage["n"] = 0
    for q, cmd in enumerate(("tree mining", "tree smithing", "tree combat", "tree class")):
        pk = click("rbtp%d" % q)
        K.check(len(pk) == 1 and P.pm.getCustomPage() == pg and list(E.CM.lines)[-1] == cmd and "if nothing opens" in str(pg.msg),
                "FLOW rail %d: /%s as the player, page still ours -> one answer + the hint line" % (q, cmd))
    K.check(classpage["n"] == 1, "FLOW the Class row asked tree:fn:classPage first")
    classpage["r"] = JClass("java.lang.Boolean").TRUE
    nl = len(list(E.CM.lines))
    pk = click("rbtp3")
    K.check(len(pk) == 1 and len(list(E.CM.lines)) == nl and str(pg.msg) == "", "FLOW Class row: tree:fn:classPage answered TRUE (no command), page still ours -> one answer")
    pk = click("rbnx")
    K.check(len(pk) == 1 and int(pg.view) == 0, "FLOW rail Rebirth Nexus = the rebirth view")
    click("n3")
    pk = click("back")
    K.check(len(pk) == 1 and int(pg.view) == 0 and int(pg.sel) == -1, "FLOW rail Your rebirth = back to the rebirth view")
    Cfg.BRIDGE.remove("tree:fn:classPage")
    pg, pk = open_page()
    K.check("SkyyRbMRp0" not in ptext(pk[0]) and "SkyyRbMRp4" in ptext(pk[0]), "FLOW without SkyyTrees: no Trees rows, the Nexus row stays")
    K.save()


def run_open(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JArray
    K = HK.Child(out)
    T19 = _load("test_skyymenu_0_3_19", os.path.join(ROOT, "SkyyMenu", "test_skyymenu_0.3.19.py"))
    hcls = os.path.join(scratch, "hcls_o")
    os.makedirs(hcls, exist_ok=True)
    os.chdir(scratch)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, hcls, jar], verify=True)
    E = T19.engine(scratch, hcls)
    Cfg, St, Pg, Op = R("RbCfg"), R("RbStore"), R("RbPage"), R("RbOpen")
    home, pl, U, k = T40.world(scratch, "o")
    open(os.path.join(pl, k + ".properties"), "w").write(PROFILE)
    P = E.player(uid=U, name="SkyyRebirthOpen")
    UniC = JClass("com.hypixel.hytale.server.core.universe.Universe")
    E.jf(UniC.class_, "playersByUuid").get(UniC.get()).put(U, P.pr)
    fn = Op(None)
    OA = lambda *xs: (lambda a: [a.__setitem__(i, x) for i, x in enumerate(xs)] and a)(JArray(JClass("java.lang.Object"))(len(xs)))
    # { Ref, Store }: another page open -> ours replaces it at once
    other = Pg(P.pr)
    P.pm.openCustomPage(P.ref, P.st, other)
    E.pump(P)
    f0 = len(E.sent(P))
    r = fn.apply(OA(P.ref, P.st))
    cur = P.pm.getCustomPage()
    K.check(bool(r) and cur is not None and cur != other and str(cur.getClass().getSimpleName()) == "RbPage"
            and len([p for p in E.sent(P)[f0:] if str(p.getClass().getSimpleName()) == "CustomPage"]) == 1,
            "O { Ref, Store } (SkyyTrees' rail): TRUE, a new Nexus page opened at once (one packet)")
    E.pump(P)
    # { UUID }: queued on the player's world thread, the task opens it
    E.run_world(E.W1)
    before = P.pm.getCustomPage()
    r = fn.apply(OA(U))
    q = E.queued(E.W1)
    K.check(bool(r) and q == ["RbOpen"] and P.pm.getCustomPage() == before, "O { UUID }: TRUE, queued on the world thread (%s), nothing opened yet" % q)
    E.run_world(E.W1)
    K.check(P.pm.getCustomPage() != before and str(P.pm.getCustomPage().getClass().getSimpleName()) == "RbPage", "O the queued task opened the Nexus page")
    E.pump(P)
    K.check(not bool(fn.apply(OA(JClass("java.util.UUID").randomUUID()))), "O an unknown player: FALSE")
    K.check(not bool(fn.apply("junk")) and not bool(fn.apply(OA(1, 2))), "O junk: FALSE")
    Cfg.ON = False
    cur = P.pm.getCustomPage()
    K.check(not bool(fn.apply(OA(P.ref, P.st))) and not bool(fn.apply(OA(U))) and P.pm.getCustomPage() == cur and E.queued(E.W1) == [],
            "O rebirth OFF, a player (not admin): FALSE both ways, nothing opened or queued")
    Cfg.ON = True
    K.save()


_ORIG_COMPARE = HK.run_compare
MAP_ENTRY = re.compile(r"\A(?:Common/UI/Custom/SkyyRebirth/Map/|com/skyy/rebirth/map/)")


def _compare(out, jar, old_jar, pkg, expect, added, removed=()):
    """the kit compare on a copy of the new jar WITHOUT the map entries (J checks them and that nothing else but the manifest changed)"""
    cp = os.path.join(SCRATCH, "compare-%s.jar" % VERSION)
    with zipfile.ZipFile(jar) as zi, zipfile.ZipFile(cp, "w", zipfile.ZIP_DEFLATED) as zo:
        for n in zi.namelist():
            if not MAP_ENTRY.match(n):
                zo.writestr(n, zi.read(n))
    _ORIG_COMPARE(out, cp, old_jar, pkg, expect, added, removed)


HK.run_compare = _compare

if __name__ == "__main__":
    assert os.path.isfile(B.JAVASSIST), B.JAVASSIST
    HK.run(name="SkyyRebirth", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=RB, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("jar", run_jar), ("vp", T40.run_vp), ("f41", T41.run_f41), ("f43", T43.run_f43), ("page", run_page),
                   ("exec", run_exec), ("open", run_open), ("live42", T42.run_live42)],
           script=__file__, live=(T40.LIVE_RB, "Skyy_SkyyRebirth"))
