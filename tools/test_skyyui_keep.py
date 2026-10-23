"""Self-test of the skyyui KIT 1.9 KEEP-MODE NODE MAPS (tools/skyyui.py "KIT 1.9: NODE MAPS THAT KEEP THE VIEW"; research/UI-Queue-Spec.md 9).

    python tools/test_skyyui_keep.py [--dir <scratch folder>] [--keep]

Python only (the keep Java - mapDrawK / mapUpdK / mapAlloc - is compiled into SkyyTrees 0.5.1 + SkyyRebirth 0.5.1 and EXECUTED by their
harnesses through the real PageManager: SkyyTrees/test_skyytrees_0.5.1.py, SkyyRebirth/test_skyyrebirth_0.5.1.py):
  - KIT_KEEP_VERSION 1.9 while KIT_VERSION / KIT_HUB_VERSION / KIT_PAGE_VERSION / KIT_MAP_VERSION stay 1.5 / 1.6 / 1.7 / 1.8;
  - ADDITIVE: node_map(...).text(), markups(), elements() on a real layout (the Crafting page, 100 % and 200 %) are byte-identical to the
    COMMITTED kit (git HEAD:tools/skyyui.py loaded as a second module);
  - keep_text(): A / S / E / H / K lines, field counts, the K picture split (pre + name + suf = the state picture; altPre + j + altMid + name
    + suf = a hidden pre-placed picture), icons + click squares at absolute canvas places (= the 1.8 child places + the node's corner);
  - keep_markups(): every markup passes check_markup / assert_proven / check_sky_paths / check_page; keep_elements() = its element count;
    unlit edges and the halo without a selection carry Visible: false;
  - keep_alloc (= mapAlloc): depth by depth, never above the budget; keep_holder / java_show; keep_hide.
Scratch: tools/dev/scratch/skyyui-keep-test (deleted unless --keep). Prints "N ok, 0 fail"; exit 1 on a failure.
"""
import os, re, sys, shutil, subprocess, importlib.util

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


SCRATCH = os.path.abspath(arg("--dir", os.path.join(HERE, "dev", "scratch", "skyyui-keep-test")))
OKS, FAILS = [0], []
P = "SkyyKt"


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)


def committed_kit():
    src = subprocess.run(["git", "show", "HEAD:tools/skyyui.py"], cwd=os.path.dirname(HERE), capture_output=True, check=True).stdout
    path = os.path.join(SCRATCH, "skyyui_head.py")
    open(path, "wb").write(src)
    spec = importlib.util.spec_from_file_location("skyyui_head", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.SKY_ART_DIR, m.KIT_DIR = UI.SKY_ART_DIR, UI.KIT_DIR
    return m


def maps(kit, lay, boxes, tex):
    out = {}
    for z in (1.0, 2.0):
        lz = lay if z == 1.0 else SM.scaled(lay, z, "Crafting")
        bz = boxes if z == 1.0 else SM.scaled_boxes(boxes, z, lz["W"], lz["H"])
        out[z] = (lz, kit.node_map(P, P + "Cv", lz, tex=lambda n: tex[n],
                                   node_tex=lambda k, n: "Node/FreeLocked" if n["kind"] == "free" else "Node/Locked",
                                   node_icon=lambda k, n: None if n["kind"] == "free" else "Tool_Pickaxe_Iron",
                                   hub_tex=lambda h: "Hub" + SM.colour_name(h["col"]), hub_icon=lambda h: "Tool_Hammer_Iron",
                                   base_tex="Base", edge_tex=lambda k: "E%d" % k, emblem_tex="Emblem", halo_tex="Halo",
                                   banner_texts=[("Smithing", "forge - temper - refine"), ("Cooking", "chop - season - feast"), ("Alchemy", "brew, distil")],
                                   banner_cols=[UI.TREE_COLOR[t] for t in ("Smithing", "Cooking", "Alchemy")], edge_boxes=bz))
    return out


def main():
    UI.verify(quiet=True)
    check(UI.KIT_KEEP_VERSION == "1.9" and UI.KIT_MAP_VERSION == "1.8" and UI.KIT_VERSION == "1.5" and UI.KIT_HUB_VERSION == "1.6"
          and UI.KIT_PAGE_VERSION == "1.7", "versions: keep 1.9; the pinned 1.5 / 1.6 / 1.7 / 1.8 unchanged")
    g = [(t, UI.TREE_COLOR[t], TD.tree(t)["branches"]) for t in ("Smithing", "Cooking", "Alchemy")]
    lay = SM.build(g, node=32, ring0=0.42, s=44.0, start=-5.0, want_ids=SM.want_of(g), what="Crafting")
    names = ["Base", "Emblem", "Halo"] + ["Node/" + n for n in SM.node_pictures(sorted(UI.TREE_COLOR[t] for t in ("Smithing", "Cooking", "Alchemy")), [1, 2, 3, 4, 5])] \
        + ["Hub" + SM.colour_name(UI.TREE_COLOR[t]) for t in ("Smithing", "Cooking", "Alchemy")]
    boxes = SM.edge_boxes(lay)
    names += ["E%d" % k for k in boxes]
    tex = dict((n, "SkyyKeepTest/Map/" + n + ".png") for n in names)
    UI.register_map_textures(tex.values())
    old = committed_kit()
    old.verify(quiet=True)
    old.register_map_textures(tex.values())
    new_m, old_m = maps(UI, lay, boxes, tex), maps(old, lay, boxes, tex)
    for z in (1.0, 2.0):
        a, b = new_m[z][1], old_m[z][1]
        check(a.text() == b.text(), "ADDITIVE %d %%: node_map().text() = the committed kit's" % (z * 100))
        check(a.markups(sel=2) == b.markups(sel=2) and a.markups(lit=set([0, 1]), sel=None) == b.markups(lit=set([0, 1]), sel=None),
              "ADDITIVE %d %%: markups() = the committed kit's" % (z * 100))
        check(a.elements() == b.elements(), "ADDITIVE %d %%: elements() = the committed kit's" % (z * 100))
    for z in (1.0, 2.0):
        lz, nm = new_m[z]
        t = nm.keep_text()
        lines = t.rstrip("\n").split("\n")
        kinds = [ln.split("\t")[0] for ln in lines]
        check(kinds.count("K") == len(lz["nodes"]) and kinds.count("E") == len(nm.edges) and kinds.count("H") == 1 and "N" not in kinds,
              "keep_text %d %%: one K per node, one E per drawn edge, one H, no 1.8 N line" % (z * 100))
        check(all(len(ln.split("\t")) == {"A": 3, "S": 3, "E": 3, "H": 3, "K": 10}[ln[0]] for ln in lines), "keep_text %d %%: field counts" % (z * 100))
        ok_split, ok_place = True, True
        for ln in lines:
            f = ln.split("\t")
            if f[0] != "K":
                continue
            n = nm.nodes[int(f[1])]
            st = f[2] + "Ready" + f[3]
            al = f[4] + "3" + f[5] + "Ready" + f[3]
            m1 = re.fullmatch(r'Group #(\w+) \{ Anchor: \(Left: (\d+), Top: (\d+), Width: (\d+), Height: (\d+)\); Background: "([^"]+)"; \}', st)
            m2 = re.fullmatch(r'Group #(\w+)V3 \{ Anchor: \(Left: (\d+), Top: (\d+), Width: (\d+), Height: (\d+)\); Visible: false; Background: "([^"]+)"; \}', al)
            if not (m1 and m2 and m1.group(1) == n["id"] == m2.group(1) and m1.groups()[1:] == m2.groups()[1:] and m1.group(6).endswith("/Node/Ready.png")):
                ok_split = False
            l0, t0 = n["k_l"], n["k_t"]
            hm = re.search(r"Left: (\d+), Top: (\d+), Width: (\d+), Height: (\d+)", f[7])
            ho = n["k_ho"]
            if not hm or (int(hm.group(1)), int(hm.group(2))) != (l0 + ho, t0 + ho) or f[9] != "#" + n["id"] + "B":
                ok_place = False
            if f[6] != "-":
                im = re.search(r"Left: (\d+), Top: (\d+)", f[6])
                isz = n["k_isz"]
                if not im or (int(im.group(1)), int(im.group(2))) != (l0 + (n["k_s"] - isz) // 2, t0 + (n["k_s"] - isz) // 2):
                    ok_place = False
            if tuple(int(x) for x in f[8].split(",")) != tuple(n["k_halo"]):
                ok_place = False
        check(ok_split, "keep_text %d %%: the state / pre-placed picture split round-trips (same place, the pre-placed one hidden)" % (z * 100))
        check(ok_place, "keep_text %d %%: icons + click squares at the node's corner + the 1.8 child offsets; the halo box per node" % (z * 100))
        alts = [["Node/" + "Ready", "Node/Open"] if n["sample"] != "FreeLocked" else [] for n in nm.nodes]
        alts = [[a.split("/")[-1] for a in x] for x in alts]
        for sel, lit in ((None, set()), (2, None), (0, set(sorted(nm.edges)[:3]))):
            mks = nm.keep_markups(lit=lit, sel=sel, alts=alts)
            for p_, mk in mks:
                UI.check_markup(mk, prefix=P)
            UI.assert_proven(mks, what="keep map")
            UI.check_sky_paths(mks)
            cv = [(None, "Group #%sR { Anchor: (Width: 1600, Height: 980); }" % P),
                  ("#%sR" % P, "Group #%sCv { Anchor: (Width: %d, Height: %d); Background: %s; }" % (P, lz["W"], lz["H"], UI.COLOR["well"]))]
            UI.check_page(UI.Appends(cv + mks), P)
            n_alt = sum(len(a) for a in alts)
            els = sum(UI._strip_quoted(UI.render(mk)).count("{") for _p, mk in mks)
            check(els == nm.keep_elements(alts=n_alt), "keep_elements = the keep markups' element count (%d)" % els)
            hid = sum(1 for _p, mk in mks if "Visible: false;" in mk)
            want = n_alt + (len(nm.edges) - (len(nm.edges) if lit is None else len(lit))) + (1 if sel is None else 0)
            check(hid == want, "keep_markups %d %% sel %s: hidden = the pre-placed pictures + unlit edges + the halo without a selection (%d / %d)"
                  % (z * 100, sel, hid, want))
        check(True, "keep map %d %%: check_markup / assert_proven / check_sky_paths / check_page" % (z * 100))
    # keep_alloc = mapAlloc
    c = [["a", "b", "c"], [], None, ["x", "y"], ["p"]]
    check(UI.keep_alloc(c, 0) == [[], [], [], [], []], "keep_alloc: budget 0 = nothing")
    check(UI.keep_alloc(c, 3) == [["a"], [], [], ["x"], ["p"]], "keep_alloc: depth 0 first")
    check(UI.keep_alloc(c, 5) == [["a", "b"], [], [], ["x", "y"], ["p"]], "keep_alloc: then depth 1")
    check(UI.keep_alloc(c, 99) == [["a", "b", "c"], [], [], ["x", "y"], ["p"]], "keep_alloc: all when it fits")
    check(sum(len(x) for x in UI.keep_alloc(c, 4)) == 4, "keep_alloc: never above the budget")
    # keep_holder / java_show / keep_hide
    hm, kids = UI.keep_holder(P + "H", 100, 20, [UI.label(P + "A", "", "default", w=100, h=20, anchor={"left": 0, "top": 0}),
                                                 UI.label(P + "B", "", "default", w=100, h=20, col="error", anchor={"left": 0, "top": 0})])
    check("LayoutMode" not in hm and "Width: 100" in hm and [p for p, _m in kids] == ["#" + P + "H"] * 2, "keep_holder: a holder without LayoutMode + its variants")
    try:
        UI.keep_holder(P + "H", 10, 10, [UI.label(P + "A", ""), UI.label(P + "A", "")])
        FAILS.append("keep_holder: two variants with one id did not raise")
    except ValueError:
        check(True, "keep_holder refuses two variants with one id")
    js = UI.java_show([P + "A", P + "B"], "x ? 1 : 0")
    check(js == 'b.set("#%sA.Visible", (x ? 1 : 0) == 0);\nb.set("#%sB.Visible", (x ? 1 : 0) == 1);' % (P, P), "java_show: one .Visible per variant")
    check(UI.keep_hide('Group #%sE1 { Anchor: (Left: 1); }' % P) == 'Group #%sE1 { Visible: false; Anchor: (Left: 1); }' % P, "keep_hide")
    srcs = UI.java_node_map_keep_methods()
    check(len(srcs) == 11 and not any("@" in s_.replace("@Override", "") for s_ in srcs) and "com.hypixel.hytale.server.core.ui.Anchor" in srcs[5],
          "java_node_map_keep_methods: 11 methods, every type filled in")
    check("mapSel(" in srcs[6] and srcs.index(srcs[6]) < [i for i, s_ in enumerate(srcs) if "int mapDrawK(" in s_][0], "mapSel before its callers")
    # keep_at0 / java_bind / java_tset / KeepApp (the keep page builders' shared pieces)
    mk = 'Label #%sA { Anchor: (Width: 9, Height: 4); }' % P
    check(UI.keep_at0(mk) == 'Label #%sA { Anchor: (Width: 9, Height: 4, Left: 0, Top: 0); }' % P, "keep_at0: Left 0 / Top 0")
    check(UI.keep_at0(mk, 50) == UI.keep_at0(mk), "keep_at0: a set Width is kept")
    check(UI.keep_at0('Label #%sA { Anchor: (Height: 4); }' % P, 50) == 'Label #%sA { Anchor: (Height: 4, Width: 50, Left: 0, Top: 0); }' % P, "keep_at0: + a Width")
    check(UI.java_bind("X1", "go") == 'ev.addEventBinding(@BT@.Activating, "#X1", @EVD@.of("a", "go"));', "java_bind")
    check(UI.java_tset("X1", "s") == 'b.set("#X1.Text", s);', "java_tset")
    ka = UI.KeepApp(["m0"])
    ka(P + "A", mk)
    ka("#" + P + "B", mk, False)
    check(ka.marks == ["m0", mk, mk] and ka.pv == [("#" + P + "A", mk)], "KeepApp: every markup, the shown ones previewed")


if __name__ == "__main__":
    sc = os.path.realpath(SCRATCH)
    assert sc.startswith(os.path.realpath(os.path.join(HERE, "dev", "scratch")) + os.sep), "scratch must be inside tools/dev/scratch/"
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(SCRATCH)
    try:
        main()
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("skyyui kit %s keep-mode node maps self-test: %d ok, %d fail" % (UI.KIT_KEEP_VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)
