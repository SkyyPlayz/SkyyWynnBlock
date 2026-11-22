"""Harness for SkyyTrees 0.6.9 (LEAN MAP PICTURES: the 11 map bases ship at 1x, cut to their dots - the client UI texture atlas fits
again; tools/trees_0_6_9_patch.py, round atlas1).
Build first:
    python tools/trees_0_6_9_patch.py && python SkyyTrees/build_skyytrees_0.6.9.py
    python SkyyTrees/test_skyytrees_0.6.9.py [--keep] [--expect-dump] [--base <folder holding the older jars>]
--base: as the 0.6.8 / 0.6.7 harness (the checkout whose SkyyTrees / SkyyClasses / SkyyPets folders hold the older jars; default = this
        checkout, then the main checkout above .claude/worktrees).
Phases (each its own child JVM, -Xverify:all where classes run; the kit's verify / class compare 0.6.8 -> 0.6.9 / engine-access audit around them):
  static   the generated script = the patch's output (re-run to identical bytes), 0.6.8's patch still regenerates 0.6.8 byte for byte, header /
           version, no new class / system / command / method, line endings kept; the jar vs 0.6.8: 11 Base@2x.png gone, 11 Base.png added,
           changed non-class entries = manifest + the page data files whose ONLY changed line is the SkyyTrMBs base element (its Anchor);
           every other line / picture / class-free file byte-equal
  pics     EXECUTED (independent Python): every new Base.png = the 2 x 2 premultiplied average of 0.6.8's Base@2x.png, cut to a box on even px
           that holds every non-clear pixel; the box x 1 / 1.5 / 2 = the base element's Anchor in L<n>Z<z>.txt and L<n>Z<z>K.txt (whole px);
           every texture path named by any page data file or class constant resolves in the jar; UI picture area <= 40 % of 0.6.8's, the
           per-folder table printed
  zoom     EXECUTED in the JVM (the real TreePage on the SkyyMenu harness engine): every skill page + all 8 class pages opened at 100 / 150 /
           200 % (zoom buttons clicked tmzi / tmzo too): the base element is sent with the cut Anchor x the zoom and its picture path, and
           every Background / TexturePath in every sent packet resolves in the jar
  harv / effects / old66 / text / bridge / creative / g64 / data / sow / jar65 / path / mig / integ / farm / sap / live   the 0.6.8 harness's
           phases on the 0.6.9 jar (unchanged behaviour; live = start twice on a scratch COPY of the live Skyy_SkyyTrees folder)
Not executed here (UNVERIFIED until the game): the client's texture atlas (no "Texture atlas rejected" lines) and the look of the 1x grey
lines at 150 / 200 % (stretched from 1x: a touch softer than the @2x of 0.6.8).
"""
import os, sys, json, subprocess, importlib.util, zipfile, re, struct, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION = "0.6.9"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "atlas1", "trees")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)]
import skyybuild as B
import harness_kit as HK

_s = importlib.util.spec_from_file_location("test_skyytrees_0_6_8", os.path.join(HERE, "test_skyytrees_0.6.8.py"))
T68 = importlib.util.module_from_spec(_s)
_argv = list(sys.argv)
_s.loader.exec_module(T68)
sys.argv[:] = _argv
T67 = T68.T67
T66, T65, T64, T63, T60 = T67.T66, T67.T65, T67.T64, T67.T63, T67.T60
T60.VERSION = VERSION

PKG = "com.skyy.trees."
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyTrees-0.6.8.jar") if os.path.isfile(os.path.join(HERE, "SkyyTrees-0.6.8.jar")) else os.path.join(T67.BASE, "SkyyTrees", "SkyyTrees-0.6.8.jar")
GEN = os.path.join(HERE, "build_skyytrees_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyytrees_0.6.8.py")
PATCH = os.path.join(TOOLS, "trees_0_6_9_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
MAP = "Common/UI/Custom/SkyyTrees/Map/"
RES = "com/skyy/trees/map/"
UI = "Common/UI/Custom/"
OLD_UI_AREA = 35091796
ZOOMS = (1.0, 1.5, 2.0)
BS = "#SkyyTrMBs "
EXPECT = {   # the version strings only (0.6.8 -> 0.6.9; no Java change)
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'SkyyTreesPlugin': ['~m setup'],
    'TreeCfg': ['~m load'],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}


def png_rgba(data):
    """(w, h, bytearray RGBA) of a filter-0 / any-filter 8-bit RGBA PNG (our own pictures; filters undone for safety)"""
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    i, idat, w, h = 8, b"", 0, 0
    while i < len(data):
        n = struct.unpack(">I", data[i:i + 4])[0]
        t = data[i + 4:i + 8]
        if t == b"IHDR":
            w, h, bd, ct = struct.unpack(">IIBB", data[i + 8:i + 18])
            assert bd == 8 and ct == 6, (bd, ct)
        elif t == b"IDAT":
            idat += data[i + 8:i + 8 + n]
        i += 12 + n
    raw = zlib.decompress(idat)
    st = w * 4
    px = bytearray(w * h * 4)
    prev = bytearray(st)
    for y in range(h):
        f = raw[y * (st + 1)]
        row = bytearray(raw[y * (st + 1) + 1:(y + 1) * (st + 1)])
        assert f == 0, "filter %d" % f   # skyymap.png writes filter 0 on every row
        px[y * st:(y + 1) * st] = row
        prev = row
    return w, h, px


def half_avg(w, h, px):
    """the 2 x 2 premultiplied average (independent of the build's tm_half): (w/2, h/2, RGBA)"""
    W, H = w // 2, h // 2
    out = bytearray(W * H * 4)
    for y in range(H):
        for x in range(W):
            idx = [((2 * y + dy) * w + 2 * x + dx) * 4 for dy in (0, 1) for dx in (0, 1)]
            sa = sum(px[k + 3] for k in idx)
            if sa == 0:
                continue
            o = (y * W + x) * 4
            for c in range(3):
                out[o + c] = (sum(px[k + c] * px[k + 3] for k in idx) + sa // 2) // sa
            out[o + 3] = (sa + 2) // 4
    return W, H, out


def bs_anchor(text):
    ls = [l for l in text.splitlines() if BS in l]
    assert len(ls) == 1, ls
    m = re.search(r"Anchor: \(Left: (\d+), Top: (\d+), Width: (\d+), Height: (\d+)\); Background: \"([^\"]+)\"", ls[0])
    return tuple(int(m.group(i)) for i in range(1, 5)), m.group(5)


def tex_refs(text):
    """the whole texture paths of markup text (a node line's split state picture "...Node/<TAB>..." is the run-time name: left out here,
    the zoom phase checks the names actually sent)"""
    return set(p for p in re.findall(r'(?:Background|TexturePath|AssetPath|Texture): "([^"]+\.png)"', text) if "\t" not in p)


def resolves(names, p):
    return (UI + p) in names or (UI + p[:-4] + "@2x.png") in names


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyTrees 0.6.9 - build script') and g.count('VERSION = "0.6.9"') == 1 and 'VERSION = "0.6.8"' not in g, "S header + VERSION")
    K.check(g.count("registerCommand(") == o.count("registerCommand(") and g.count("registerSystem(") == o.count("registerSystem(")
            and g.count("makeClass(") == o.count("makeClass(") and g.count("\nM(") == o.count("\nM("), "S no new command / system / class / method")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    for patch, ref in ((PATCH, GEN), (os.path.join(TOOLS, "trees_0_6_8_patch.py"), GEN_OLD)):
        cp = os.path.join(d, os.path.basename(ref))
        p = subprocess.run([sys.executable, patch, "--out", cp], capture_output=True, text=True)
        K.check(p.returncode == 0 and open(cp, "rb").read() == open(ref, "rb").read(), "S %s re-generates its script byte for byte: %s" % (os.path.basename(patch), p.stderr[-300:]))
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    gone, new = sorted(na - nb), sorted(nb - na)
    K.check(len(gone) == 11 and all(re.fullmatch(re.escape(MAP) + r"[A-Za-z]+/Base@2x\.png", n) for n in gone), "S 11 Base@2x.png gone: %s" % gone[:3])
    K.eq(new, sorted(n.replace("Base@2x.png", "Base.png") for n in gone), "S 11 Base.png added (same folders)")
    chg = sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n))
    pd = [n for n in chg if n.startswith(RES)]
    K.eq(sorted(set(chg) - set(pd)), ["manifest.json"], "S changed non-class entries = manifest + page data only")
    K.eq(len(pd), 11 * 3 + 11 * 2, "S every L<n>Z<z>.txt (33) + L<n>Z<z>K.txt (22) changed")
    only_bs = True
    for n in pd:
        la, lb = za.read(n).decode("utf-8").split("\n"), zb.read(n).decode("utf-8").split("\n")
        diff = [(a, b) for a, b in zip(la, lb) if a != b]
        if len(la) != len(lb) or len(diff) != 1 or BS not in diff[0][0] or BS not in diff[0][1]:
            only_bs = False
            K.notes.append("S %s: %d changed lines" % (n, len(diff)))
            continue
        a, b = diff[0]
        if re.sub(r"Anchor: \([^)]*\)", "", a) != re.sub(r"Anchor: \([^)]*\)", "", b):
            only_bs = False
    K.check(only_bs, "S each changed page data file: ONLY the base element's Anchor differs (every node / line / label / hub keeps its place)")
    K.check(not [n for n in chg if n.endswith(".meta")], "S L<n>.meta unchanged")
    ma, mb = json.loads(za.read("manifest.json")), json.loads(zb.read("manifest.json"))
    K.check(mb["Version"] == VERSION and dict(ma, Version=VERSION, Name=ma["Name"].replace("0.6.8", VERSION)) == mb, "S manifest: only the Version changed")
    K.save()


def run_pics(out, jar, scratch, _home):
    K = HK.Child(out)
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    nb = set(zb.namelist())
    layouts = sorted(n[len(MAP):-len("/Base@2x.png")] for n in za.namelist() if n.startswith(MAP) and n.endswith("/Base@2x.png"))
    K.eq(len(layouts), 11, "P 11 layouts")
    # layout index of each name: from the page data (L<n>Z0.txt names its base)
    lidx = {}
    for n in range(11):
        _bx, path = bs_anchor(zb.read(RES + "L%dZ0.txt" % n).decode("utf-8"))
        lidx[path.split("/")[-2]] = n
    K.eq(sorted(lidx), layouts, "P every layout's page data names its own base")
    ok_pix, ok_box, ok_anchor, tot_old, tot_new = 0, 0, 0, 0, 0
    for nm in layouts:
        L = lidx[nm]
        w2, h2, p2 = png_rgba(za.read(MAP + nm + "/Base@2x.png"))
        w1, h1, p1 = png_rgba(zb.read(MAP + nm + "/Base.png"))
        tot_old += w2 * h2
        tot_new += w1 * h1
        W, H, ph = half_avg(w2, h2, p2)
        (l, t, w, h), path = bs_anchor(zb.read(RES + "L%dZ0.txt" % L).decode("utf-8"))
        K.eq(path, "SkyyTrees/Map/%s/Base.png" % nm, "P %s base path unchanged" % nm)
        if (w, h) == (w1, h1) and all(v % 2 == 0 for v in (l, t, w, h)) and l + w <= W and t + h <= H:
            ok_box += 1
        # the cut = the averaged picture inside the box; nothing non-clear outside it
        same = all(p1[(y - t) * w1 * 4:(y - t + 1) * w1 * 4] == ph[(y * W + l) * 4:(y * W + l + w) * 4] for y in range(t, t + h))
        outside = sum(1 for y in range(H) for x in range(W) if ph[(y * W + x) * 4 + 3] and not (l <= x < l + w and t <= y < t + h))
        if same and outside == 0:
            ok_pix += 1
        else:
            K.notes.append("P %s: same %s, %d px outside the box" % (nm, same, outside))
        good = True
        for zi, z in enumerate(ZOOMS):
            want = tuple(int(round(v * z)) for v in (l, t, w, h))
            if any(abs(v * z - round(v * z)) > 1e-9 for v in (l, t, w, h)):
                good = False
            for f in ["L%dZ%d.txt" % (L, zi)] + (["L%dZ%dK.txt" % (L, zi)] if zi else []):
                bx, pth = bs_anchor(zb.read(RES + f).decode("utf-8"))
                ob, _op = bs_anchor(za.read(RES + f).decode("utf-8"))
                if bx != want or pth != path or ob != (0, 0, int(round(W * z)), int(round(H * z))):
                    good = False
                    K.notes.append("P %s %s: %s (want %s; 0.6.8 %s)" % (nm, f, bx, want, ob))
        ok_anchor += good
    K.eq(ok_box, 11, "P every Base.png has the size of its box (even px, inside the canvas)")
    K.eq(ok_pix, 11, "P every Base.png = the 2 x 2 premultiplied average of 0.6.8's Base@2x.png inside the box, nothing outside it (independent re-computation)")
    K.eq(ok_anchor, 11, "P every zoom's base Anchor (normal + keep page data) = the box x 1 / 1.5 / 2 on whole px; 0.6.8's was the full canvas")
    K.notes.append("P bases: %.2f -> %.2f Mpx" % (tot_old / 1e6, tot_new / 1e6))
    # every texture named by page data or a class constant resolves
    refs, miss = set(), []
    for n in zb.namelist():
        if n.startswith(RES) and n.endswith(".txt"):
            refs |= tex_refs(zb.read(n).decode("utf-8"))
    for p in sorted(refs):
        if not resolves(nb, p):
            miss.append(p)
    node_dirs = sorted(set(p.rsplit("/", 1)[0] for p in refs if "/Node/" in p))
    K.eq(miss, [], "P every one of the %d texture paths in the page data is in the jar (.png or @2x.png)" % len(refs))
    K.eq(node_dirs, [], "P no whole node picture path in the page data (the run time writes the name)")
    npre = set()
    for n in zb.namelist():
        if n.startswith(RES) and n.endswith(".txt"):
            npre |= set(re.findall(r'Background: "(SkyyTrees/Map/[A-Za-z/]*)\t', zb.read(n).decode("utf-8")))
    K.eq(sorted(npre), ["SkyyTrees/Map/Node/"], "P every node line's picture folder = Map/Node/ (its state pictures)")
    cls_refs = set()
    for n in zb.namelist():
        if n.endswith(".class"):
            cls_refs |= set(x.decode("latin-1") for x in re.findall(rb"SkyyTrees/Map/[A-Za-z0-9/]+\.png", zb.read(n)))
    K.eq(sorted(p for p in cls_refs if not resolves(nb, p)), [], "P every SkyyTrees/Map/... .png constant in the classes resolves (%d)" % len(cls_refs))
    # every Node picture name the old jar had is still there (the run time builds node names: nothing removed)
    K.eq(sorted(n for n in za.namelist() if n.startswith(MAP + "Node/") and n not in nb), [], "P every node picture kept")
    # the area
    tab = {}
    area = cnt = 0
    for n in zb.namelist():
        if n.startswith(UI) and n.endswith(".png"):
            w_, h_ = struct.unpack(">II", zb.read(n)[16:24])
            k = n[len(UI):].rsplit("/", 1)[0] if n.startswith(MAP) else n[len(UI):].split("/")[0]
            a_ = tab.setdefault(k, [0, 0])
            a_[0] += 1
            a_[1] += w_ * h_
            area += w_ * h_
            cnt += 1
    for k in sorted(tab, key=lambda k: -tab[k][1]):
        K.notes.append("P area %-40s %4d files %6.2f Mpx" % (k, tab[k][0], tab[k][1] / 1e6))
    K.check(area <= 0.40 * OLD_UI_AREA, "P UI picture area %.2f Mpx in %d files <= 40 %% of 0.6.8's 35.09 (-%.0f %%)" % (area / 1e6, cnt, 100.0 * (1 - area / float(OLD_UI_AREA))))
    # tools/ci/ui_budget.py (fixer, critic finding 1): thresholds tied to the evidence (45 = last known-good SET, 60 < known-bad 76),
    # and the SET with this jar in place of 0.6.8 is under FAIL (WARN is expected until SkyyShards part 2)
    sys.path.insert(0, os.path.join(TOOLS, "ci"))
    import ui_budget as UB
    K.eq((UB.WARN_MPX, UB.FAIL_MPX), (45.0, 60.0), "U ui_budget thresholds WARN > 45, FAIL > 60 Mpx")
    _w, _f, _l = UB.check(ROOT, overrides=[os.path.abspath(jar)])
    K.check(bool(_l) and "SkyyTrees 0.6.9" in " | ".join(_l), "U ui_budget counted this jar (SkyyTrees 0.6.9 row)")
    K.eq(_f, [], "U SET with this jar: no ui_budget FAIL (%s)" % (_l[0][-48:] if _l else "-"))
    _w0, _f0, _l0 = UB.check(ROOT)
    K.check(bool(_f0), "U control: the pinned SET (Trees 0.6.8, ~70 Mpx) FAILs ui_budget")
    K.save()


def run_zoom(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    _s2 = importlib.util.spec_from_file_location("test_skyymenu_0_3_19", os.path.join(ROOT, "SkyyMenu", "test_skyymenu_0.3.19.py"))
    T19 = importlib.util.module_from_spec(_s2)
    _s2.loader.exec_module(T19)
    hcls = os.path.join(scratch, "hcls_z")
    os.makedirs(hcls, exist_ok=True)
    os.chdir(scratch)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, hcls, jar], verify=True)
    E = T19.engine(scratch, hcls)
    J = lambda n: JClass(PKG + n)
    Paths, UUID, Int = JClass("java.nio.file.Paths"), JClass("java.util.UUID"), JClass("java.lang.Integer")
    St, Cfg, V, TM, Pg, Defs = J("TreeStore"), J("TreeCfg"), J("TreeV3"), J("TreeMap"), J("TreePage"), J("TreeDefs")
    d = os.path.join(scratch, "zoom")
    os.makedirs(os.path.join(d, "players"), exist_ok=True)
    St.DIR = Paths.get(os.path.join(d, "players"))
    Cfg.FILE = Paths.get(os.path.join(d, "trees.properties"))
    Cfg.load()
    J("TreeSk").loadV3(Paths.get(d))
    J("TreeSk").reads(True)
    br = St.bridge()
    br.put("skill:fn:level", T60._fn(JImplements, JOverride, lambda a: Int(30)))
    zb = zipfile.ZipFile(jar)
    names = set(zb.namelist())
    cut = {}
    for n in range(int(TM.NL)):
        (l, t, w, h), path = bs_anchor(zb.read(RES + "L%dZ0.txt" % n).decode("utf-8"))
        cut[path] = (l, t, w, h)
    K.eq(int(TM.ZN), 3, "Z the jar has 3 zooms")
    K.eq([int(x) for x in TM.ZPCT], [100, 150, 200], "Z 100 / 150 / 200 %")
    u = UUID.fromString("69696969-0000-0000-0000-000000000001")
    br.put("class:" + str(u), "Warrior")
    br.put("profile:class:" + str(u), "Warrior")
    P = E.player(uid=u, name="SkyyZoomTester")

    def pkts(f0):
        return [p for p in E.sent(P)[f0:] if str(p.getClass().getSimpleName()) == "CustomPage"]

    def texts(pk):
        out_ = []
        for p in pk:
            cs = p.commands if hasattr(p, "commands") else None
            for c in (list(cs) if cs is not None else []):
                out_.append(str(c.text) if c.text is not None else "")
                if getattr(c, "data", None) is not None:
                    out_.append(str(c.data))
        return "\n".join(out_)

    def open_page(t, zoom):
        E.pump(P)
        pg = Pg(P.pr, t)
        pg.zoom = zoom
        f0 = len(E.sent(P))
        P.pm.openCustomPage(P.ref, P.st, pg)
        pk = pkts(f0)
        E.pump(P)
        return pg, pk

    def click(a):
        E.pump(P)
        f0 = len(E.sent(P))
        P.pm.handleLegacyCustomPageEvent(P.ref, P.st, E.CPE(E.CPT.Data, '{"a":"%s"}' % a))
        pk = pkts(f0)
        E.pump(P)
        return pk

    def base_ok(txt, z, what):
        m = re.findall(r"Group #SkyyTrMBs \{ Anchor: \(Left: (\d+), Top: (\d+), Width: (\d+), Height: (\d+)\); Background: \"([^\"]+)\"", txt)
        if len(m) != 1:
            return "%s: %d base elements" % (what, len(m))
        bx, path = tuple(int(x) for x in m[0][:4]), m[0][4]
        want = tuple(int(round(v * z)) for v in cut.get(path, (0, 0, 0, 0)))
        if path not in cut or bx != want:
            return "%s: base %s %s, want %s" % (what, path, bx, want)
        miss = sorted(p for p in tex_refs(txt) if p.startswith("Skyy") and not resolves(names, p))
        return ("%s: textures not in the jar %s" % (what, miss[:5])) if miss else ""

    TPAGE, TNAME = [int(x) for x in V.TPAGE], [str(x) for x in V.TNAME]
    NT = int(Defs.NT)
    bad, opened, seen = [], 0, set()
    pages = [(TPAGE[TNAME.index("Mining")], "Gathering"), (TPAGE[TNAME.index("Smithing")], "Crafting"), (TPAGE[TNAME.index("Acrobatics")], "Adventure")]
    for t, nm in pages:
        for zi, z in enumerate(ZOOMS):
            pg, pk = open_page(t, zi)
            txt = texts(pk)
            r = base_ok(txt, z, "%s at %d %%" % (nm, int(z * 100)))
            opened += 1
            if r:
                bad.append(r)
            else:
                seen.add((nm, zi))
    classes = ["Warrior", "Archer", "Mage", "Berserker", "Priest", "Assassin", "Monk", "Spellblade"]
    for cn in classes:
        br.put("class:" + str(u), cn)
        br.put("profile:class:" + str(u), cn)
        for zi, z in enumerate(ZOOMS):
            pg, pk = open_page(NT, zi)
            txt = texts(pk)
            r = base_ok(txt, z, "Class %s at %d %%" % (cn, int(z * 100)))
            opened += 1
            if r:
                bad.append(r)
            elif ("SkyyTrees/Map/Class%s/Base.png" % cn) not in txt:
                bad.append("Class %s at %d %%: another class's map" % (cn, int(z * 100)))
            else:
                seen.add((cn, zi))
    K.eq(bad, [], "Z every page x zoom opened (%d): the base element on its cut box x the zoom, every Skyy texture in the jar" % opened)
    K.eq(len(seen), 33, "Z 3 skill pages + 8 class pages x 3 zooms drawn")
    # the zoom buttons: 100 -> 150 -> 200 -> 150 -> 100 on the Crafting page
    pg, pk = open_page(TPAGE[TNAME.index("Smithing")], 0)
    steps = []
    for a, z in (("tmzi", 1.5), ("tmzi", 2.0), ("tmzi", 2.0), ("tmzo", 1.5), ("tmzo", 1.0)):
        pk = click(a)
        txt = texts(pk)
        steps.append((a, int(pg.zoom), base_ok(txt, z, "click %s" % a) if "SkyyTrMBs" in txt else "click %s: no rebuild" % a))
    K.eq([s[1] for s in steps], [1, 2, 2, 1, 0], "Z zoom buttons: 150 / 200 / stays 200 / 150 / 100 %")
    K.eq([s[2] for s in steps if s[2]], [], "Z every zoom click redraws the base on its cut box x the zoom")
    K.save()
    sys.stdout.flush()
    os._exit(0)


if __name__ == "__main__":
    for _p in (OLD_JAR, T68.OLD_JAR, T67.OLD_JAR, T67.CJAR, T67.PJAR, T65.OLD_JAR):
        assert os.path.isfile(_p), "missing %s (pass --base <the checkout with the built jars>)" % _p
    HK.run(name="SkyyTrees", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("static", run_static), ("pics", run_pics), ("zoom", run_zoom), ("harv", T68.run_harv), ("effects", T67.run_effects),
                   ("old66", T67.run_old66), ("text", T67.run_text), ("bridge", T67.run_bridge), ("creative", T66.run_creative), ("g64", T65.run_g64),
                   ("data", T65.run_data), ("sow", T65.run_sow), ("jar65", T65.run_jar), ("path", T64.run_path), ("mig", T64.run_mig),
                   ("integ", T64.run_integ), ("farm", T63.run_farm), ("sap", T63.run_sap), ("live", T63.run_live)],
           script=__file__, live=(T60.LIVE_DIR, "Skyy_SkyyTrees"))
