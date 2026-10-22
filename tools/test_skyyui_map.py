"""Self-test of the skyyui KIT 1.8 NODE MAPS (tools/skyyui.py "KIT 1.8: NODE MAPS"; research/Radial-Trees-Spec.md round R1; Style Guide 16).

    python tools/test_skyyui_map.py [--dir <scratch folder>] [--no-java] [--keep]

Phase 1  Python: KIT_MAP_VERSION 1.8 while KIT_VERSION / KIT_HUB_VERSION / KIT_PAGE_VERSION stay 1.5 / 1.6 / 1.7 (pinned SET scripts assert
         them); TREE_COLOR (13 trees, valid colours); the map row = the hub page width; register_map_textures refuses @2x / underscores /
         paths outside <Mod>/Map/; map_pic refuses an unregistered texture; check_sky_paths accepts a registered map texture and still
         refuses every other unknown path; node_map on a real layout (tools/skyymap.py, the Crafting page at 100 % and 200 %): every
         markup passes check_markup / assert_proven / check_sky_paths, the page data text() round-trips (A / S / E / N lines, the node
         picture split pre + name + suf = the markup), elements() = the markup count, the halo of a selected node; map_scroll (the
         2-axis box, LeftScrolling proven by probe M7 = PROBED map-scroll); assert_map_elements refuses 1,001; map_rail_row /
         map_rail_parts / map_legend / map_zoom_row pass the checks, refuse a '+' text; EVERY kit 1.5-1.7 builder output unchanged
         against the COMMITTED kit (git HEAD:tools/skyyui.py loaded as a second module: buttons, labels, hub_page, hub previews,
         check_sky_paths on the old paths)
Phase 2  (a JVM; skipped with --no-java) NODE_MAP_JAVA compiled with javassist against the cached HytaleServer.jar (tools/serverjar.py),
         loaded with -Xverify:all and EXECUTED: mapRead of the page data out of a scratch jar (URLClassLoader), mapCount, mapDraw into a
         REAL UICommandBuilder / UIEventBuilder: the commands = the static appends + the lit edges + the halo + every node (disc, icon, hit),
         the b.set texts, one Activating binding per node with a = <prefix><k>, the element count = NodeMap.elements(lit, sel), the node
         picture names written into the paths, an empty / short line skipped, no lit array = no edge.
Scratch: tools/dev/scratch/skyyui-map-test (deleted unless --keep). Prints "N ok, 0 fail"; exit 1 on a failure.
"""
import os, re, sys, shutil, zipfile, subprocess, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import skyyui as UI
import skyymap as SM
import trees_v3_data as TD


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(HERE, "dev", "scratch", "skyyui-map-test")))
OKS, FAILS = [0], []
P = "SkyyMt"


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)


def raises(fn, exc, what, contains=None):
    try:
        fn()
    except exc as e:
        check(contains is None or contains in str(e), "%s (message: %s)" % (what, e))
        return
    except Exception as e:      # noqa
        FAILS.append("%s: raised %s instead of %s: %s" % (what, type(e).__name__, exc.__name__, e))
        return
    FAILS.append("%s: did not raise" % what)


def committed_kit():
    src = subprocess.run(["git", "show", "HEAD:tools/skyyui.py"], cwd=os.path.dirname(HERE), capture_output=True, check=True).stdout
    path = os.path.join(SCRATCH, "skyyui_head.py")
    open(path, "wb").write(src)
    spec = importlib.util.spec_from_file_location("skyyui_head", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.SKY_ART_DIR, m.KIT_DIR = UI.SKY_ART_DIR, UI.KIT_DIR     # the art folder of the repo, not of the scratch copy (test_skyyui_hubs's way)
    return m


# ================================================================= phase 1
def phase_python():
    UI.verify(quiet=True)
    check(UI.KIT_MAP_VERSION == "1.8" and UI.KIT_VERSION == "1.5" and UI.KIT_HUB_VERSION == "1.6" and UI.KIT_PAGE_VERSION == "1.7",
          "versions: map 1.8, the pinned 1.5 / 1.6 / 1.7 unchanged")
    check(len(UI.TREE_COLOR) == 13 and all(re.fullmatch(r"#[0-9A-Fa-f]{6}", c) for c in UI.TREE_COLOR.values()), "TREE_COLOR: 13 tree colours")
    check(UI.MAP_RAIL_W + 2 * UI.MAP_GAP + UI.MAP_CANVAS_W + UI.MAP_PANEL_W == UI.HUB_PAGE_IW and UI.MAP_CANVAS_H == 774, "the map row = 1552 x 774")
    check("map-scroll" in UI.PROBED and UI.PROVEN_LAYOUTS["LeftScrolling"] == ("map-scroll",), "LeftScrolling proven by probe M7 (map-scroll)")
    for bad in ("SkyyTest/Map/X@2x.png", "SkyyTest/Map/A_B.png", "SkyyTest/Other/X.png", "../SkyyTest/Map/X.png", "SkyyTest/Map/X.ogg"):
        raises(lambda b=bad: UI.register_map_textures([b]), ValueError, "register_map_textures refuses %s" % bad)
    raises(lambda: UI.map_pic(P + "X", 0, 0, 10, 10, "SkyyTest/Map/Nope.png"), ValueError, "map_pic refuses an unregistered texture", "registered")
    raises(lambda: UI.check_sky_paths(['Group #%sX { Background: "SkyyTest/Map/Nope.png"; }' % P]), ValueError, "check_sky_paths refuses an unregistered map path")
    raises(lambda: UI.check_sky_paths(['Group #%sX { Background: "SkyyTest/Other.png"; }' % P]), ValueError, "check_sky_paths still refuses an unknown path")
    # a real layout: the Crafting page
    g = [(t, UI.TREE_COLOR[t], TD.tree(t)["branches"]) for t in ("Smithing", "Cooking", "Alchemy")]
    lay = SM.build(g, node=32, ring0=0.42, s=44.0, start=-5.0, want_ids=SM.want_of(g), what="Crafting")
    names = ["Base", "Emblem", "Halo"] + ["Node/" + n for n in SM.node_pictures(sorted(UI.TREE_COLOR[t] for t in ("Smithing", "Cooking", "Alchemy")), [1, 2, 3, 4, 5])] \
        + ["Hub" + SM.colour_name(UI.TREE_COLOR[t]) for t in ("Smithing", "Cooking", "Alchemy")]
    boxes = SM.edge_boxes(lay)
    names += ["E%d" % k for k in boxes]
    tex = dict((n, "SkyyTest/Map/" + n + ".png") for n in names)
    UI.register_map_textures(tex.values())
    UI.check_sky_paths(['Group #%sX { Background: "%s"; }' % (P, tex["Base"])])
    check(True, "check_sky_paths accepts a registered map texture")
    out = {}
    for z in (1.0, 2.0):
        lz = lay if z == 1.0 else SM.scaled(lay, z, "Crafting")
        bz = boxes if z == 1.0 else SM.scaled_boxes(boxes, z, lz["W"], lz["H"])
        nm = UI.node_map(P, P + "Cv", lz, tex=lambda n: tex[n],
                         node_tex=lambda k, n: "Node/FreeLocked" if n["kind"] == "free" else "Node/Locked",
                         node_icon=lambda k, n: None if n["kind"] == "free" else "Tool_Pickaxe_Iron",
                         hub_tex=lambda h: "Hub" + SM.colour_name(h["col"]), hub_icon=lambda h: "Tool_Hammer_Iron",
                         base_tex="Base", edge_tex=lambda k: "E%d" % k, emblem_tex="Emblem", halo_tex="Halo",
                         banner_texts=[("Smithing", "forge - temper - refine"), ("Cooking", "chop - season - feast"), ("Alchemist's", "brew, distil")],
                         banner_cols=[UI.TREE_COLOR[t] for t in ("Smithing", "Cooking", "Alchemy")], edge_boxes=bz)
        out[z] = nm
        mks = nm.markups(sel=3)
        for p_, mk in mks:
            UI.check_markup(mk, prefix=P)
        UI.assert_proven(mks, what="node map %d %%" % (z * 100))
        UI.check_sky_paths(mks)
        cv = [(None, "Group #%sR { Anchor: (Width: 1600, Height: 980); }" % P),
              ("#%sR" % P, "Group #%sCv { Anchor: (Width: %d, Height: %d); Background: %s; }" % (P, lz["W"], lz["H"], UI.COLOR["well"]))]
        UI.check_page(UI.Appends(cv + mks), P)
        check(True, "node map at %d %%: check_markup / assert_proven / check_sky_paths / check_page" % (z * 100))
        text = nm.text()
        lines = text.rstrip("\n").split("\n")
        kinds = [ln.split("\t")[0] for ln in lines]
        check(kinds.count("N") == len(lz["nodes"]) and kinds.count("E") == len(bz) and kinds.count("S") == 2 * len(lz["banners"]),
              "text(): one N line per node, one E per drawn edge, 2 S per banner")
        check(all(len(ln.split("\t")) == {"A": 3, "S": 3, "E": 3, "N": 8}[ln[0]] for ln in lines), "text(): the field counts")
        ns = [ln.split("\t") for ln in lines if ln[0] == "N"]
        check(all(f[2] + "Locked" + f[3] == nm.nodes[int(f[1])]["pre"] + "Locked" + nm.nodes[int(f[1])]["suf"] for f in ns), "text(): the N split round-trips")
        check(all(f[2].endswith("SkyyTest/Map/Node/") and f[3].startswith('.png"') for f in ns), "the node picture split: pre + <name> + suf in Map/Node/")
        check(any(ln.endswith("	ALCHEMIST'S") for ln in lines if ln[0] == "S") and any(ln.endswith("	brew, distil") for ln in lines if ln[0] == "S"),
              "banner texts with punctuation go by b.set (line 1 upper case)")
        n_all = nm.elements(lit=None, sel=3)
        check(n_all == sum(UI._strip_quoted(UI.render(m)).count("{") for _p, m in mks), "elements() = the markup count (%d)" % n_all)
        check(nm.elements(lit=set(), sel=None) == n_all - len(bz) - 1, "elements() without lit edges and halo")
        hz = int(round(UI.MAP_HALO * z))
        n3 = lz["nodes"][3]
        check(("Width: %d, Height: %d" % (hz, hz)) in nm.nodes[3]["halo"] and ("Left: %d" % int(round(n3["cx"] - hz / 2.0))) in nm.nodes[3]["halo"],
              "the halo of node 3 at %d %% (%d px, centred)" % (z * 100, hz))
    # map_scroll, the guard, the rail / legend / zoom row
    sc = UI.map_scroll(P + "Out", P + "In", P + "Cv", 840, 774, 1680, 1548)
    UI.assert_proven(sc, what="map_scroll")
    check("LayoutMode: TopScrolling" in sc[0] and "LayoutMode: LeftScrolling" in sc[1] and "Width: 1680, Height: 1548" in sc[2], "map_scroll: the M7 box")
    check(UI.assert_map_elements(1000) == 1000, "assert_map_elements accepts 1,000")
    raises(lambda: UI.assert_map_elements(1001), ValueError, "assert_map_elements refuses 1,001", "1001")
    parts = [UI.map_rail_row(P + "Rp0", "page", True), UI.map_rail_row(P + "Rt0", "tree")] + \
        [m for _p, m in UI.map_rail_parts(P + "Rp0", "page")] + [m for _p, m in UI.map_rail_parts(P + "Rt0", "tree", icon="Tool_Pickaxe_Iron", col="#8fc8ff")]
    lg = UI.map_legend(P, [(tex["Node/Ready"], "ready - gold ring"), (tex["Halo"], "selected - cyan halo")])
    parts += [r for r, _k in lg] + [m for _r, k in lg for _p, m in k]
    zr, zk = UI.map_zoom_row(P, 440)
    parts += [zr] + [m for _p, m in zk]
    for m in parts:
        UI.check_markup(m, prefix=P)
    UI.assert_proven(parts, what="rail / legend / zoom")
    UI.check_sky_paths(parts)
    check(True, "map_rail_row / map_rail_parts / map_legend / map_zoom_row pass the checks")
    raises(lambda: UI.map_zoom_row(P, 440, texts=("-", "+")), ValueError, "a '+' button text is refused (not a proven inline character)")
    raises(lambda: UI.map_rail_row(P + "X", "nope"), ValueError, "map_rail_row kind page / tree")
    raises(lambda: UI.map_legend(P, [("SkyyTest/Map/Nope.png", "x")]), ValueError, "map_legend refuses an unregistered picture")
    # every kit 1.5 - 1.7 builder unchanged against the COMMITTED kit
    H = committed_kit()
    H.verify(quiet=True)
    same = [("button", lambda m: m.button(P + "B", "Learn", "primary", w=440)), ("label", lambda m: m.label(P + "L", "", "bold", h=26, col="gold")),
            ("hover_row", lambda m: m.hover_row(P + "H", "selected", h=42, pad=0, w=232)),
            ("panel", lambda m: m.panel(P + "Pn", "well", w=456, h=774)), ("item_icon", lambda m: m.item_icon(P + "I", "Tool_Pickaxe_Iron", size=24)),
            ("scrollbar_style", lambda m: m.scrollbar_style()), ("group", lambda m: m.group(P + "G", layout="TopScrolling", w=840, h=774)),
            ("hub_page", lambda m: [x for x in m.hub_page(P + "F", "character", content_layout="Left").appends]),
            ("hub_page sub+foot", lambda m: [x for x in m.hub_page(P + "F", "character", sub=True, footer=True).appends]),
            ("java_hub_page", lambda m: m.java_hub_page(m.hub_page(P + "F", "character"), "trees", cls="HubBar")),
            ("hub_bar_java page", lambda m: m.hub_bar_java(row=True, page=True))]
    for nm_, fn in same:
        check(fn(UI) == fn(H), "unchanged against the committed kit: %s" % nm_)
    raises(lambda: UI.check_sky_paths(['Group #%sX { Background: "SomeMod/Pic.png"; }' % P]), ValueError, "check_sky_paths: an unknown path still refused (1.7 rule)")
    return out


# ================================================================= phase 2
def phase_java(maps):
    try:
        import jpype
        import skyybuild as B
        import serverjar
    except ImportError as e:
        print("java phase skipped: %s" % e)
        return
    os.environ["TEMP"] = os.environ["TMP"] = SCRATCH
    sj = serverjar.server_jar()
    out = os.path.join(SCRATCH, "classes")
    os.makedirs(out, exist_ok=True)
    jpype.startJVM(B._jvm(), "-XX:-UsePerfData", "-Xverify:all", "-Djava.io.tmpdir=" + SCRATCH,
                   "--add-opens=java.base/java.lang=ALL-UNNAMED", "--enable-native-access=ALL-UNNAMED",
                   classpath=[B.JAVASSIST, sj], convertStrings=True)
    Jc = jpype.JClass
    pool = Jc("javassist.ClassPool")(False)
    pool.appendSystemPath()
    pool.appendClassPath(sj)
    ct = pool.makeClass("skyymaptest.MapT")
    try:
        for src in UI.java_node_map_methods():
            ct.addMethod(Jc("javassist.CtNewMethod").make(src, ct))
        ct.writeFile(out)
        check(True, "NODE_MAP_JAVA compiles with javassist against HytaleServer.jar (%d methods)" % len(UI.NODE_MAP_JAVA))
    except Exception as e:      # noqa
        FAILS.append("NODE_MAP_JAVA does not compile: %s" % e)
        return
    res = os.path.join(SCRATCH, "res.jar")
    with zipfile.ZipFile(res, "w") as z:
        z.writestr("skyymaptest/map/C1.txt", maps[1.0].text())
        z.writestr("skyymaptest/map/C2.txt", maps[2.0].text())
    URL = Jc("java.net.URL")
    loader = Jc("java.net.URLClassLoader")(jpype.JArray(URL)([Jc("java.io.File")(out).toURI().toURL(), Jc("java.io.File")(res).toURI().toURL()]),
                                          Jc("java.lang.ClassLoader").getSystemClassLoader())
    T = Jc("skyymaptest.MapT", loader=loader)
    check(int(T.mapCount('Group #A { Text: "{x}"; Label { } }')) == 2, "mapCount skips braces inside quotes")
    for z, key in ((1.0, "C1"), (2.0, "C2")):
        nm = maps[z]
        lines = T.mapRead(loader, "skyymaptest/map/%s.txt" % key)
        check(len(lines) == len(nm.text().rstrip("\n").split("\n")), "mapRead: every line of the page data (%s)" % key)
        check(len(T.mapRead(loader, "skyymaptest/map/none.txt")) == 0 and len(T.mapRead(None, "x")) == 0, "mapRead: a missing resource = no lines")
        nN = len(nm.nodes)
        ek = sorted(nm.edges)
        lit = jpype.JArray(jpype.JBoolean)(max(ek) + 1)
        lit_set = set(ek[::3])
        for k in lit_set:
            lit[k] = True
        tex = jpype.JArray(Jc("java.lang.String"))(nN)
        for k in range(nN):
            tex[k] = "Ready" if k % 2 else "C8fc8ffL13"
        b = Jc("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")()
        ev = Jc("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")()
        els = int(T.mapDraw(b, ev, lines, "#%sCv" % P, lit, tex, 5, "tmn"))
        want = nm.elements(lit=lit_set, sel=5)
        check(els == want, "mapDraw at %d %%: element count %d = NodeMap.elements %d" % (z * 100, els, want))
        cmds = [(str(c.type), str(c.selector), str(c.text if c.text is not None else c.data)) for c in b.getCommands()]
        apps = [(c[1], c[2]) for c in cmds if "Append" in c[0]]
        sets = [(c[1], c[2]) for c in cmds if "Set" in c[0]]
        check(len(apps) == len(nm.static) + len(lit_set) + 1 + sum(2 + (1 if n["icon"] else 0) for n in nm.nodes),
              "mapDraw: the appends = static + lit edges + halo + every node (disc, icon, hit)")
        check(len(sets) == len(nm.sets) and any("ALCHEMIST'S" in c[1] for c in sets), "mapDraw: the banner b.set texts")
        check(("SkyyTest/Map/Node/Ready.png" in apps[-1][1] or "SkyyTest/Map/Node/Ready.png" in apps[-2][1] or
               any("SkyyTest/Map/Node/C8fc8ffL13.png" in a[1] for a in apps)), "mapDraw: the run-time picture names in the paths")
        halo = [a for a in apps if "#SkyyMtSel " in a[1]]
        check(len(halo) == 1 and apps.index(halo[0]) < [i for i, a in enumerate(apps) if "#SkyyMtN0 " in a[1]][0], "mapDraw: the halo of node 5, drawn under the nodes")
        evs = [(str(x.selector), str(x.data)) for x in ev.getEvents()]
        check(len(evs) == nN and evs[7][0] == "#SkyyMtN7B" and "tmn7" in evs[7][1], "mapDraw: one Activating binding per node, a = tmn<k>")
        b2 = Jc("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")()
        ev2 = Jc("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")()
        bad = jpype.JArray(Jc("java.lang.String"))(list(lines)[:3] + ["", "N\t1", "E\tzz\tx", "Q\tq\tq"])
        n2 = int(T.mapDraw(b2, ev2, bad, "#%sCv" % P, None, None, -1, "tmn"))
        check(n2 == sum(UI._strip_quoted(m).count("{") for _p, m in nm.static[:3]) and len(list(ev2.getEvents())) == 0,
              "mapDraw: short / odd lines skipped, no lit array = no edge, never throws")
    loader.close()          # Windows: release the scratch jar so the folder can be deleted


if __name__ == "__main__":
    sc = os.path.realpath(SCRATCH)
    assert sc.startswith(os.path.realpath(os.path.join(HERE, "dev", "scratch")) + os.sep), "scratch must be inside tools/dev/scratch/"
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(SCRATCH)
    try:
        maps = phase_python()
        if "--no-java" not in sys.argv:
            phase_java(maps)
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("skyyui kit %s node maps self-test: %d ok, %d fail" % (UI.KIT_MAP_VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)
