"""Derive SkyyTrees/build_skyytrees_0.5.0.py from SkyyTrees 0.4.9 (build_skyytrees_0.4.9.py = the tools/deploy_set.py SET pin, itself GENERATED
by tools/trees_0_4_9_patch.py). Edit THIS patch, never the generated script. Every anchor is asserted once; at the end every change is
undone on a copy and compared with 0.4.9 (tools/soundpass_gen.Patch).
Run:
    python tools/trees_0_5_0_patch.py && python SkyyTrees/build_skyytrees_0.5.0.py && python SkyyTrees/test_skyytrees_0.5.0.py
Round R2 of research/Radial-Trees-Spec.md: the RADIAL MAP PAGES. Needs tools/skyymap.py (layouts, checks, pictures) and the kit 1.8 node
maps (tools/skyyui.py KIT_MAP_VERSION; Style Guide section 16) - round R1, built with this round.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

NOTE = '''0.5.0 (2026-10-22) = THE RADIAL TREE PAGES (research/Radial-Trees-Spec.md round R2; FULL round with round R1 = tools/skyymap.py + the
  kit 1.8 node maps in tools/skyyui.py). Skyy's words (docs/answered/ui.md 2026-10-22): "i definitely want to do the rebirth page like this,
  but id like to do our trees like this." + popups "Grouped pages (Recommended)", "Separate per tree (Recommended)", "Pips in the ring
  (Recommended)", "Show greyed (Recommended)" (Beastmastery is LIVE since P8c: shown normally) + "is is posible to add shift scroll for in
  and out?" (the server never sees the mouse wheel: ZOOM BUTTONS - 100 % / 150 % / 200 % +, replacing the Focus view) + "work through your
  whole list."
  1. FOUR MAP PAGES replace the rows + detail wells (hub page 1600 x 980, rows 1 + 2, no sub-tab row, no footer): Gathering (Mining /
     Foraging / Farming / Fishing), Crafting (Smithing / Cooking / Alchemy), Adventure (Combat / Acrobatics / Exploration / Beastmastery),
     Class (the player's class tree: its 3 branches are the 3 hubs). Content row = left rail 232 | map 840 x 774 | right panel 456.
     The map (tools/skyymap.py layout, checked at build time: in the canvas, discs >= 6 px apart, click squares apart, every upgrade and
     free perk placed once): the SkyWynn crest placeholder in the centre (page emblems = art round R4), one hub per tree (per branch on the
     Class page) in the tree colour (kit TREE_COLOR; the class colour on the Class page), the branches as dotted lines (one build-time
     picture per map) with every row on a ring, the row's free perk / ability as a diamond on the spine, each upgrade a disc whose picture
     IS its state: locked (padlock), coming soon ("..."), open (row open, no point free), ready (gold ring), learnt k / m (the tree colour
     + k of m rank pips in the ring), max (all pips + glow), capstones with a star; a lit line = gold (a spine into an open row, a spoke into
     an upgrade with a rank: the 0.3.12 gold rule); a corner banner per tree (name + motto; branch name + theme on the Class page).
  2. ZOOM: Zoom out / Zoom in in the right panel (100 / 150 / 200 %; a '+' is no proven inline button text): the same map laid out at that size at build time (checked again) inside a 2-axis
     scroll box (probe M7 PROVED it: wheel / bars both ways, nodes clickable). The scroll box starts at the top left (no proven property can
     scroll it to the selected talent - UNVERIFIED, not built). NOT DONE YET (fix round 2): centring on the selected talent when zooming
     (Skyy's "if possible" is not met) and keeping the view still - at 150 / 200 % every click (a talent, Learn, Respec, zoom) rebuilds the
     page, so the view most likely goes back to the top left; 100 % needs no scrolling and is unaffected. The way to fix it needs probe M8
     (a picture shown / hidden on an open page + a map moved inside a clipping box) first. The zoomed pictures are the 100 % @2x pictures
     stretched (200 % = 1 picture pixel per screen pixel at 1080p): Skyy judges the look; real 150 / 200 % pictures only if it looks soft.
  3. LEFT RAIL: page rows Gathering / Crafting / Adventure / Class / Rebirth Nexus (shown while SkyyRebirth is loaded; opens its page
     through rebirth:fn:open when a later SkyyRebirth puts it, else /rebirth as the player - the hub fallback way) and under each its
     trees (icon, name in the tree colour, "Lv 23 - 4 points free"); legend learnt / ready / locked / selected at the foot.
  4. RIGHT PANEL: the tree head (icon, name, level, points free / spent + the next row's gate, the respec price) + the zoom row (+ the
     Loadout button on the Class page) + the talent clicked on the map (tree - branch - row, name, Rank n / m, state, Now / Next, Cost,
     what it needs or "Ready to unlock", How it works - TreeV3's own 0.4.x texts) + Learn (Primary; greyed when it cannot) + Respec (the
     10 s "Click again to respec" pattern, the same price rules) + the result line.
  5. CLASS PAGE LOADOUT: the Loadout button swaps the map for today's Abilities well + Lattice (the 0.3.13 / 0.4.0 code, unchanged; the
     detail well shows a hint until an ability is clicked); Talents swaps back.
  6. EVERY BOUND CLICK ANSWERS WITH EXACTLY ONE PAGE PACKET (HANDOFF section 2, probe 0.7.1: a click with no answer leaves the client on
     "Loading..."): each handled click rebuilds once; a hub click that opened another page sends nothing more; a safety net at the end of
     handleDataEvent sends the engine's empty update when nothing was sent and this page is still the open one (unknown data, an error,
     a hub / Nexus command that opened nothing).
  Everything the page shows is generated at build time: tools/skyymap.py pictures (our own geometry, no vanilla pixels) under
  Common/UI/Custom/SkyyTrees/Map/ (markup paths without @2x), the map page data as jar text resources com/skyy/trees/map/L<n>Z<z>.txt
  (+ L<n>.meta: which upgrade / free perk each node is, which row / upgrade lights each line) - drawn by the kit's mapDraw.
  UNCHANGED: every rule of TreeV3 (points, gates, buy, respec, prices, hooks), TreeData / the player files (no saved-data change, no
  migration), /tree and /tree <name> (open the page of that tree), /tree probe, the Trees tab, tree:fn:classPage (the Class page in Class
  tab mode), every bridge key. NOT USED (probes M4 / M5 / M6 not run in game): AssetImage swaps, the Anchor move of the halo, tooltips -
  every click is a plain rebuild.
  ROLLBACK to 0.4.9: safe (layout only; no data written differently).
'''

P = G.Patch(os.path.join(ROOT, "SkyyTrees", "build_skyytrees_0.4.9.py"), os.path.join(ROOT, "SkyyTrees", "build_skyytrees_0.5.0.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.4.9"') and P.has("0.4.9 (2026-10-22)") and not P.has("0.5.0 (2026-10-22)"), "not the generated SkyyTrees 0.4.9 script"
REG0, SYS0, CLS0 = P.s.count("registerCommand("), P.s.count("registerSystem("), P.s.count("makeClass(")

P.rep('''"""SkyyTrees 0.4.9 - build script (javassist via jpype, tools/skyybuild.py). Owner: Skyy (they/them).
GENERATED by tools/trees_0_4_9_patch.py from build_skyytrees_0.4.8.py (the SET pin) - edit the patch, not this file.
''', '''"""SkyyTrees 0.5.0 - build script (javassist via jpype, tools/skyybuild.py). Owner: Skyy (they/them).
GENERATED by tools/trees_0_5_0_patch.py from build_skyytrees_0.4.9.py (the SET pin) - edit the patch, not this file.
''' + NOTE + '''
SkyyTrees 0.4.9 - GENERATED by tools/trees_0_4_9_patch.py from build_skyytrees_0.4.8.py:
''')
P.rep('VERSION = "0.4.9"', 'VERSION = "0.5.0"')

# ---------- the engine probe: PageManager.getCustomPage (the safety net asks whether this page is still the open one)
P.rep('''for c, m in (("BOP", "setBlock"), ("WLD", "execute")):      # 0.3.11: the replant''',
      '''B.probe(pool, T["PGM"], "getCustomPage")                    # 0.5.0: the click safety net (is this page still the open one?)
for c, m in (("BOP", "setBlock"), ("WLD", "execute")):      # 0.3.11: the replant''')

TM_BLOCK = r'''
# ================= 0.5.0 THE RADIAL MAP PAGES (research/Radial-Trees-Spec.md round R2; tools/skyymap.py + kit 1.8 node maps) =================
# Four pages (Gathering, Crafting, Adventure, Class) in ONE TreePage: left rail 232 | map 840 x 774 | right panel 456. The map of a layout
# (3 skill pages + one per class = 11) at a zoom (100 / 150 / 200 %) is page data (com/skyy/trees/map/L<n>Z<z>.txt, made by the kit's
# node_map) drawn by TreeMap.mapDraw with the node pictures TreeMap.paint picks from the player's ranks; L<n>.meta says which upgrade /
# free perk every node is and which row / upgrade lights every line. Every coordinate and picture is fixed and checked here.
import time as _tmtime
import skyymap as SMAP
_TM_T0 = _tmtime.time()
assert SUI.KIT_MAP_VERSION == "1.8" and SMAP.MAP_VERSION == "1.0", "0.5.0: the kit 1.8 node maps + tools/skyymap.py 1.0"
TMP = "SkyyTrM"                    # every map page id starts with this (inside TR_PREFIX)
TM_RES = "com/skyy/trees/map/"     # the page data resources (next to the classes; never an asset)
TM_DIR = "SkyyTrees/Map/"          # markup texture paths (relative to Common/UI/Custom/, written WITHOUT @2x)
TM_JAR = "Common/UI/Custom/"
TM_SKILL_PAGES = [("Gathering", ["Mining", "Foraging", "Farming", "Fishing"]), ("Crafting", ["Smithing", "Cooking", "Alchemy"]),
                  ("Adventure", ["Combat", "Acrobatics", "Exploration", "Beastmastery"])]
TM_PAGE_NAMES = [p_[0] for p_ in TM_SKILL_PAGES] + ["Class"]
TM_ZOOMS = tuple(z_ / 100.0 for z_ in SUI.MAP_ZOOMS)   # (1.0, 1.5, 2.0): the kit's zoom steps
TM_MOTTO = {"Mining": "dig - smelt - prosper", "Foraging": "fell - gather - replant", "Farming": "sow - tend - harvest",
            "Fishing": "cast - reel - land", "Smithing": "forge - temper - refine", "Cooking": "chop - season - feast",
            "Alchemy": "brew - distil - transmute", "Combat": "fight - endure - prevail", "Acrobatics": "leap - roll - fly",
            "Exploration": "seek - map - discover", "Beastmastery": "tame - bond - command"}   # spec 2.3 (Q4 default)
# the layout numbers tools/skyymap.fit_page found (2026-10-22, the real data): a data change that no longer fits falls back to fit_page and
# prints the new numbers (pin them here then)
TM_PIN = {"Gathering": dict(node=32, ring0=0.46, s=40.0, start=40.0), "Crafting": dict(node=32, ring0=0.42, s=44.0, start=-5.0),
          "Adventure": dict(node=32, ring0=0.46, s=40.0, start=55.0)}
TM_CLASS_PIN = dict(node=36, ring0=0.38, s=52.0, start=0.0, banner_offset=60.0)
assert sorted(t_ for _p, ts in TM_SKILL_PAGES for t_ in ts) == sorted(V3_SKILL_ORDER), "0.5.0: every skill tree on exactly one page"
TM_SKTV = dict((n_, NC + V3_SKILL_ORDER.index(n_)) for n_ in V3_SKILL_ORDER)
TM_TCOL = list(CCOLOR) + [SUI.TREE_COLOR[n_] for n_ in V3_SKILL_ORDER]          # the map colour of every tree (tv): the class colour on Class
TM_TPAGE = [3] * NC + [[i_ for i_, (_p, ts) in enumerate(TM_SKILL_PAGES) if n_ in ts][0] for n_ in V3_SKILL_ORDER]
TM_NL = len(TM_SKILL_PAGES) + NC
TM_LNAME = [p_[0] for p_ in TM_SKILL_PAGES] + ["Class" + c_ for c_ in CLASSES]
assert all(re.fullmatch(r"[A-Z][A-Za-z]+", n_) for n_ in TM_LNAME)


def tm_mix(col, other, f):
    """a colour f of the way to other (the Class page hubs: the class colour, lighter, darker - spec 2.3)"""
    a, b = SMAP.rgb(col), SMAP.rgb(other)
    return "#%02x%02x%02x" % tuple(int(round(a[i] + (b[i] - a[i]) * f)) for i in range(3))


def tm_groups(L):
    """the skyymap groups of layout L: a skill page = one group per tree (clockwise); a class = one group per branch"""
    if L < len(TM_SKILL_PAGES):
        return [(n_, TM_TCOL[TM_SKTV[n_]], V3T[TM_SKTV[n_]]["branches"]) for n_ in TM_SKILL_PAGES[L][1]]
    ci_ = L - len(TM_SKILL_PAGES)
    return [("B%d" % i_, CCOLOR[ci_], [b_]) for i_, b_ in enumerate(V3T[ci_]["branches"])]


def tm_code(L, nid):
    """a map node id (group key, branch, row, item) -> its TreeV3 code: the upgrade index u (>= 0) or -(r + 1) for row r's free perk"""
    key, bi, ri, uid = nid
    if L < len(TM_SKILL_PAGES):
        tv_ = TM_SKTV[key]
        b_ = V3_TR[tv_]["b0"] + bi
    else:
        tv_ = L - len(TM_SKILL_PAGES)
        b_ = V3_TR[tv_]["b0"] + int(key[1:])
    r_ = V3_BR[b_]["r0"] + ri
    assert V3_RW[r_]["tv"] == tv_ and V3_RW[r_]["b"] == b_, nid
    if uid == "free":
        return -(r_ + 1)
    us = [k_ for k_ in range(V3_RW[r_]["u0"], V3_RW[r_]["u0"] + V3_RW[r_]["un"]) if V3_UP[k_]["id"] == uid]
    assert len(us) == 1, nid
    return us[0]


def tm_jcode(L, e):
    """a junction / node edge end -> the edge's light code: a spine into row r = r (lit while the row is open); a spoke into upgrade u =
    -(u + 1) (lit while u has a rank)"""
    a_, b_, kind, ri = e
    if kind == "spine":
        key, bi, ri2, _j = b_
        tv_ = TM_SKTV[key] if L < len(TM_SKILL_PAGES) else L - len(TM_SKILL_PAGES)
        bb = V3_TR[tv_]["b0"] + (bi if L < len(TM_SKILL_PAGES) else int(key[1:]))
        return V3_BR[bb]["r0"] + ri2
    return -(tm_code(L, b_) + 1)


def tm_short(theme):
    """a class branch banner's line 2: its theme's leading comma parts that fit the 200 px banner at the motto size (the panel shows the rest)"""
    parts, out = [p_.strip() for p_ in theme.split(",")], ""
    for p_ in parts:
        t_ = (out + ", " + p_) if out else p_
        if SUI.text_width(t_, SUI.MAP_MOTTO_SIZE) > SMAP.BANNER_W - 4:
            break
        out = t_
    return out or "branch"


TM_ASSETS = {}            # jar path -> bytes (pictures + page data)
TM_PATHS = {}             # picture name -> markup path


def tm_ship(name, pic):
    data = SMAP.png(pic)
    w_, h_ = SMAP.png_size(data)
    assert w_ % 2 == 0 and h_ % 2 == 0 and "_" not in name, name
    jp = TM_JAR + TM_DIR + name + "@2x.png"
    assert jp not in TM_ASSETS, name
    TM_ASSETS[jp] = data
    TM_PATHS[name] = TM_DIR + name + ".png"
    SUI.register_map_textures([TM_PATHS[name]])
    return TM_PATHS[name]


# ---- the layouts (100 %), checked; then every zoom (checked again)
TM_LAY = []
for L_ in range(TM_NL):
    g_ = tm_groups(L_)
    pin = TM_PIN.get(TM_LNAME[L_], TM_CLASS_PIN)
    try:
        lay_ = SMAP.build(g_, want_ids=SMAP.want_of(g_), what=TM_LNAME[L_], **pin)
    except SMAP.MapError as e_:
        print("0.5.0 MAP PIN NO LONGER FITS (%s): %s - searching" % (TM_LNAME[L_], e_))
        lay_ = SMAP.fit_page(g_, sizes=(pin["node"], 30, 28) if L_ < len(TM_SKILL_PAGES) else (36, 32), what=TM_LNAME[L_],
                             banner_offset=pin.get("banner_offset", 0.0))
        print("0.5.0 NEW PIN for %s: %s" % (TM_LNAME[L_], lay_["params"]))
    TM_LAY.append(lay_)
TM_ZL = [[lay_ if z_ == 1.0 else SMAP.scaled(lay_, z_, TM_LNAME[L_]) for z_ in TM_ZOOMS] for L_, lay_ in enumerate(TM_LAY)]
TM_CODES = [[tm_code(L_, n_["id"]) for n_ in lay_["nodes"]] for L_, lay_ in enumerate(TM_LAY)]
TM_BOX = [SMAP.edge_boxes(lay_) for lay_ in TM_LAY]
TM_ECODE = [dict((k_, tm_jcode(L_, lay_["edges"][k_])) for k_ in TM_BOX[L_]) for L_, lay_ in enumerate(TM_LAY)]
for L_ in range(TM_NL):           # every upgrade + free perk of the page's trees is a node exactly once
    tvs_ = [TM_SKTV[n_] for n_ in TM_SKILL_PAGES[L_][1]] if L_ < len(TM_SKILL_PAGES) else [L_ - len(TM_SKILL_PAGES)]
    want_ = sorted([u_ for u_ in range(NU3) if V3_UP[u_]["tv"] in tvs_] + [-(r_ + 1) for r_ in range(NR3) if V3_RW[r_]["tv"] in tvs_ and V3_RW[r_]["fname"]])
    assert sorted(TM_CODES[L_]) == want_, "0.5.0: layout %s does not hold every upgrade / free perk once" % TM_LNAME[L_]

# ---- the pictures (pure Python, our own geometry): node states, hubs, halo, emblem, one base + the gold lines per layout
TM_MAXES = sorted(set(_u["max"] for _u in V3_UP))
assert TM_MAXES[0] >= 1 and TM_MAXES[-1] <= 9, "0.5.0: rank pips draw 1-9 ranks: %s" % TM_MAXES
for nm_, pic_ in sorted(SMAP.node_pictures(sorted(set(TM_TCOL)), TM_MAXES).items()):
    tm_ship("Node/" + nm_, pic_)
TM_HUBCOL = []            # per layout, per hub: its colour
for L_, lay_ in enumerate(TM_LAY):
    if L_ < len(TM_SKILL_PAGES):
        TM_HUBCOL.append([h_["col"] for h_ in lay_["hubs"]])
    else:
        c_ = CCOLOR[L_ - len(TM_SKILL_PAGES)]
        TM_HUBCOL.append([c_, tm_mix(c_, "#ffffff", 0.35), tm_mix(c_, "#000000", 0.3)])   # ui-data: the Class page hub colours (pictures)
for c_ in sorted(set(x_ for hc_ in TM_HUBCOL for x_ in hc_)):
    tm_ship("Hub" + SMAP.colour_name(c_), SMAP.hub_picture(c_))
tm_ship("Halo", SMAP.halo_picture())
tm_ship("Emblem", SMAP.emblem_picture())
for L_, lay_ in enumerate(TM_LAY):
    tm_ship(TM_LNAME[L_] + "/Base", SMAP.base_picture(lay_))
    for k_, pic_ in sorted(SMAP.gold_pictures(lay_).items()):
        tm_ship(TM_LNAME[L_] + "/E%d" % k_, pic_)
TM_CPIC = [SMAP.colour_name(c_) for c_ in TM_TCOL]
for tv_ in range(NV3):                         # every picture name TreeMap.tex can answer exists
    for m_ in TM_MAXES:
        for k_ in range(1, m_):
            assert ("Node/%sL%d%d" % (TM_CPIC[tv_], k_, m_)) in TM_PATHS
        assert ("Node/%sMax%d" % (TM_CPIC[tv_], m_)) in TM_PATHS
    for s_ in ("CapMax", "Free"):
        assert ("Node/" + TM_CPIC[tv_] + s_) in TM_PATHS
for s_ in ("Locked", "Soon", "Open", "Ready"):
    assert "Node/" + s_ in TM_PATHS and "Node/Cap" + s_ in TM_PATHS, s_
assert "Node/FreeLocked" in TM_PATHS

# ---- the page data: node_map per layout and zoom (kit 1.8), its element count, the meta file
TM_EL = {}
for L_, lay_ in enumerate(TM_LAY):
    cl_ = L_ >= len(TM_SKILL_PAGES)
    if cl_:
        brs_ = V3T[L_ - len(TM_SKILL_PAGES)]["branches"]
        btx_ = [(b_["name"], tm_short(b_["theme"])) for b_ in brs_]
        bcol_ = list(TM_HUBCOL[L_])
        hic_ = CICON[L_ - len(TM_SKILL_PAGES)]
    else:
        btx_ = [(n_, TM_MOTTO[n_]) for n_ in TM_SKILL_PAGES[L_][1]]
        bcol_ = [TM_TCOL[TM_SKTV[n_]] for n_ in TM_SKILL_PAGES[L_][1]]
    for t1_, t2_ in btx_:
        assert SUI.text_width(t1_.upper(), 15, True) <= SMAP.BANNER_W - 4 and SUI.text_width(t2_, SUI.MAP_MOTTO_SIZE) <= SMAP.BANNER_W - 4, (t1_, t2_)
    hcol_ = dict((h_["key"], TM_HUBCOL[L_][i_]) for i_, h_ in enumerate(lay_["hubs"]))
    for zi_, z_ in enumerate(TM_ZOOMS):
        lz_ = TM_ZL[L_][zi_]
        boxes_ = TM_BOX[L_] if z_ == 1.0 else SMAP.scaled_boxes(TM_BOX[L_], z_, lz_["W"], lz_["H"])
        nm_ = SUI.node_map(TMP, TMP + "Cv", lz_, tex=lambda n: TM_PATHS[n],
                           node_tex=lambda k, n: ("Node/" + ("FreeLocked" if n["kind"] == "free" else ("CapLocked" if n.get("cap") else "Locked"))),
                           node_icon=(lambda L: lambda k, n: None if TM_CODES[L][k] < 0 else V3_UP[TM_CODES[L][k]]["icon"])(L_),
                           hub_tex=(lambda hc: lambda h: "Hub" + SMAP.colour_name(hc[h["key"]]))(hcol_),
                           hub_icon=(lambda L: lambda h: (CICON[L - len(TM_SKILL_PAGES)] if L >= len(TM_SKILL_PAGES) else V3_ICON[TM_SKTV[h["key"]]]))(L_),
                           base_tex=TM_LNAME[L_] + "/Base", edge_tex=(lambda L: lambda k: TM_LNAME[L] + "/E%d" % k)(L_),
                           emblem_tex="Emblem", halo_tex="Halo", banner_texts=btx_, banner_cols=bcol_, edge_boxes=boxes_)
        # the node picture is chosen at run time: the sample name must be the last part of its path (Node/<name>.png)
        assert all(n_["pre"].endswith('"' + TM_DIR + "Node/") for n_ in nm_.nodes), "0.5.0: node pictures under Map/Node/"
        TM_ASSETS[TM_RES + "L%dZ%d.txt" % (L_, zi_)] = nm_.text().encode("utf-8")
        TM_EL[(L_, zi_)] = nm_.elements(lit=None, sel=0)
        if L_ == 0 and zi_ == 0:
            TM_NM00 = nm_
    TM_ASSETS[TM_RES + "L%d.meta" % L_] = ("N\t%s\nE\t%d\t%s\n" % (",".join(str(c_) for c_ in TM_CODES[L_]), len(lay_["edges"]),
                                            ",".join("%d:%d" % (k_, TM_ECODE[L_][k_]) for k_ in sorted(TM_ECODE[L_])))).encode("utf-8")
for _p in sorted(TM_ASSETS):
    assert "_" not in _p.split("/")[-1], _p
print("0.5.0 maps: %d layouts x %d zooms; nodes %s; min disc gap %s px; %d pictures + %d page data files, %d KB; worst map %d elements; %.1f s" % (
    TM_NL, len(TM_ZOOMS), [len(l_["nodes"]) for l_ in TM_LAY], ["%.1f" % l_["info"]["min_gap"] for l_ in TM_LAY],
    sum(1 for p_ in TM_ASSETS if p_.endswith(".png")), sum(1 for p_ in TM_ASSETS if p_.startswith(TM_RES)),
    sum(len(v_) for v_ in TM_ASSETS.values()) // 1024, max(TM_EL.values()), _tmtime.time() - _TM_T0))

# ---- TreeMap: the tables + the kit's map reader / drawer + the node pictures and lit lines of a player
tmap = pool.makeClass(PKG + ".TreeMap")
for _d in ("public static final String RES = %s;" % json.dumps(TM_RES),
           "public static final int NL = %d;" % TM_NL, "public static final int NSP = %d;" % len(TM_SKILL_PAGES),
           "public static final int ZN = %d;" % len(TM_ZOOMS),
           "public static final int[] ZPCT = %s;" % jint([int(round(z_ * 100)) for z_ in TM_ZOOMS]),
           "public static final String[] LNAME = %s;" % jstr(TM_LNAME),
           "public static final String[] PNAME = %s;" % jstr(TM_PAGE_NAMES),
           "public static final int[] PT0 = %s;" % jint([sum(len(ts_) for _n, ts_ in TM_SKILL_PAGES[:i_]) for i_ in range(len(TM_SKILL_PAGES))]),
           "public static final int[] PTN = %s;" % jint([len(ts_) for _n, ts_ in TM_SKILL_PAGES]),
           "public static final int[] PTV = %s;" % jint([TM_SKTV[n_] for _n, ts_ in TM_SKILL_PAGES for n_ in ts_]),
           "public static final int[] TVPAGE = %s;" % jint(TM_TPAGE),
           "public static final String[] MCOL = %s;" % jstr(TM_TCOL),
           "public static final String[] CPIC = %s;" % jstr(TM_CPIC),
           "public static final String CLASS_COL = %s;" % json.dumps(SUI.TREE_COLOR["Class"]),
           "public static final String CLASS_ICON = %s;" % json.dumps(CICON[0]),
           "public static final int[] CW = %s;" % jint([TM_ZL[L_][z_]["W"] for L_ in range(TM_NL) for z_ in range(len(TM_ZOOMS))]),
           "public static final int[] CH = %s;" % jint([TM_ZL[L_][z_]["H"] for L_ in range(TM_NL) for z_ in range(len(TM_ZOOMS))]),
           "public static final java.lang.Object[] LINES = new java.lang.Object[%d];" % (TM_NL * len(TM_ZOOMS)),
           "public static final java.lang.Object[] NODES = new java.lang.Object[%d];" % TM_NL,
           "public static final java.lang.Object[] EDGES = new java.lang.Object[%d];" % TM_NL):
    F(tmap, _d)
for _m in SUI.java_node_map_methods(dict((k_, T[k_]) for k_ in ("UCB", "UEB", "BT", "EVD"))):
    M(tmap, _m)
M(tmap, r"""
public static synchronized String[] lines(int L, int z) {
  if (L < 0 || L >= NL) return new String[0];
  int zz = z < 0 ? 0 : (z >= ZN ? ZN - 1 : z);
  int i = L * ZN + zz;
  Object o = LINES[i];
  if (o == null) { o = mapRead(@PKG@.TreeMap.class.getClassLoader(), RES + "L" + L + "Z" + zz + ".txt"); LINES[i] = o; }
  return (String[]) o;
}""")
# L<n>.meta: "N\t<code>,<code>,..." (per node) and "E\t<edge count>\t<k>:<code>,..." (per drawn edge); undrawn edges = MIN_VALUE
M(tmap, r"""
public static synchronized void meta(int L) {
  if (L < 0 || L >= NL || NODES[L] != null) return;
  String[] l = mapRead(@PKG@.TreeMap.class.getClassLoader(), RES + "L" + L + ".meta");
  int[] n = new int[0];
  int[] e = new int[0];
  for (int i = 0; i < l.length; i++) {
    String[] f = l[i].split("\t", -1);
    if (f[0].equals("N") && f.length >= 2 && f[1].length() > 0) {
      String[] c = f[1].split(",");
      n = new int[c.length];
      for (int k = 0; k < c.length; k++) n[k] = Integer.parseInt(c[k].trim());
    } else if (f[0].equals("E") && f.length >= 3) {
      e = new int[Integer.parseInt(f[1].trim())];
      for (int k = 0; k < e.length; k++) e[k] = Integer.MIN_VALUE;
      if (f[2].length() > 0) {
        String[] c = f[2].split(",");
        for (int k = 0; k < c.length; k++) {
          int a = c[k].indexOf(':');
          e[Integer.parseInt(c[k].substring(0, a).trim())] = Integer.parseInt(c[k].substring(a + 1).trim());
        }
      }
    }
  }
  EDGES[L] = e;
  NODES[L] = n;
}""")
M(tmap, r"""
public static int[] nodes(int L) {
  if (L < 0 || L >= NL) return new int[0];
  meta(L);
  return (int[]) NODES[L];
}""")
M(tmap, r"""
public static int[] edges(int L) {
  if (L < 0 || L >= NL) return new int[0];
  meta(L);
  return (int[]) EDGES[L];
}""")
M(tmap, r"""
public static int pageOf(int tv) {
  return tv < 0 || tv >= TVPAGE.length ? 0 : TVPAGE[tv];
}""")
M(tmap, r"""
public static int nodeTv(int c) {
  if (c >= 0) return c < @PKG@.TreeV3.NU ? @PKG@.TreeV3.UT[c] : -1;
  int r = -c - 1;
  return r < @PKG@.TreeV3.NR ? @PKG@.TreeV3.RT[r] : -1;
}""")
M(tmap, r"""
public static int nodeRow(int c) {
  if (c >= 0) return c < @PKG@.TreeV3.NU ? @PKG@.TreeV3.UROW[c] : -1;
  int r = -c - 1;
  return r < @PKG@.TreeV3.NR ? r : -1;
}""")
# one tree's numbers for a player: { points (level + Head Start), spent, level (-1 = SkyySkills missing) }; probe = the class probe page
M(tmap, r"""
public static int[] stat(java.util.UUID u, @PKG@.TreeData d, int tv, boolean probe) {
  int lvl = probe ? @PKG@.TreeV3.PROBE_LVL : @PKG@.TreeV3.level(u, tv);
  int pts = (lvl < 0 ? 0 : lvl) + (probe ? 0 : @PKG@.TreeV3.head(u));
  return new int[] { pts, @PKG@.TreeV3.spent(d, tv), lvl };
}""")
# the picture name of node code c (tools/skyymap.state_name mirrors it): a free diamond open / locked; an upgrade maxed (capstone: CapMax),
# learnt k of m (pips), else its TreeV3.ustate: ready / coming soon / open (row open, no point free) / locked
M(tmap, r"""
public static String tex(@PKG@.TreeData d, int c, int pts, int sp, int[] g, String cp) {
  if (d == null) return c < 0 ? "FreeLocked" : "Locked";
  if (c < 0) {
    int r = -c - 1;
    if (r >= @PKG@.TreeV3.NR) return "FreeLocked";
    boolean o = (sp >= g[@PKG@.TreeV3.RNUM[r]] || @PKG@.TreeV3.gfRow(d, r)) && @PKG@.TreeV3.RFK[r] != 0;
    return o ? cp + "Free" : "FreeLocked";
  }
  if (c >= @PKG@.TreeV3.NU) return "Locked";
  int mx = @PKG@.TreeV3.UMAX[c];
  int rk = d.rk[c];
  boolean cap = @PKG@.TreeV3.RCAP[@PKG@.TreeV3.UROW[c]];
  if (rk >= mx) return cap ? cp + "CapMax" : cp + "Max" + mx;
  if (rk >= 1) return cp + "L" + rk + mx;
  int st = @PKG@.TreeV3.ustate(d, c, pts, sp, g);
  String pre = cap ? "Cap" : "";
  if (st == 1) return pre + "Ready";
  if (st == 4) return pre + "Soon";
  if (st == 5 || st == 2) return pre + "Open";
  return pre + "Locked";
}""")
# fill tex[] (every node's picture) and lit[] (every line: a spine into an open row, a spoke into an upgrade with a rank) of layout L
M(tmap, r"""
public static void paint(java.util.UUID u, @PKG@.TreeData d, int L, boolean probe, String[] texs, boolean[] lit) {
  int[] c = nodes(L);
  int[] e = edges(L);
  java.lang.Object[] st = new java.lang.Object[@PKG@.TreeV3.NV];
  java.lang.Object[] gs = new java.lang.Object[@PKG@.TreeV3.NV];
  for (int k = 0; k < c.length && k < texs.length; k++) {
    int tv = nodeTv(c[k]);
    if (tv < 0) { texs[k] = "Locked"; continue; }
    if (st[tv] == null) { st[tv] = stat(u, d, tv, probe); gs[tv] = @PKG@.TreeV3.gates(tv); }
    int[] s = (int[]) st[tv];
    int[] gg = (int[]) gs[tv];
    texs[k] = tex(d, c[k], s[0], s[1], gg, CPIC[tv]);
  }
  for (int k = 0; k < e.length && k < lit.length; k++) {
    int x = e[k];
    if (x == Integer.MIN_VALUE || d == null) { lit[k] = false; continue; }
    if (x < 0) { int up = -x - 1; lit[k] = up < @PKG@.TreeV3.NU && d.rk[up] >= 1; continue; }
    if (x >= @PKG@.TreeV3.NR) { lit[k] = false; continue; }
    int tv = @PKG@.TreeV3.RT[x];
    if (st[tv] == null) { st[tv] = stat(u, d, tv, probe); gs[tv] = @PKG@.TreeV3.gates(tv); }
    int[] s2 = (int[]) st[tv];
    int[] g2 = (int[]) gs[tv];
    lit[k] = s2[1] >= g2[@PKG@.TreeV3.RNUM[x]];
  }
}""")
# the rows still locked: " - row 4 opens at 15" (the next gate above the spent points), or " - every row is open"
M(tmap, r"""
public static String nextRow(int tv, int[] g, int sp) {
  if (tv < 0 || tv >= @PKG@.TreeV3.NV) return "";
  int rows = @PKG@.TreeV3.BRN[@PKG@.TreeV3.TB0[tv]];
  for (int n = 1; n <= rows && n < 8; n++) if (g[n] > sp) return " - row " + n + " opens at " + g[n];
  return " - every row is open";
}""")
M(tmap, r"""
public static String railSub(int[] s) {
  if (s == null || s[2] < 0) return "SkyySkills missing";
  int f = s[0] - s[1];
  return "Lv " + s[2] + " - " + f + (f == 1 ? " point" : " points") + " free";
}""")
M(tmap, r"""
public static boolean nexusOn() {
  try {
    java.util.Map b = @PKG@.TreeStore.bridge();
    return b.get("rebirth:fn:open") != null || b.get("rebirth:fn:count") != null;
  } catch (Throwable t) { return false; }
}""")

# ---- the page: geometry + the build() Java (kit 1.7 hub page, content row = rail | map | panel; kit 1.8 node map)
TM_INNER = SUI.MAP_PANEL_W - 2 * SUI.WELL_PAD                       # 440 inside the right panel
TM_TXT_W = TR_DET_TXT_W                                             # 424: the 0.3.25 detail text width (tr_fit_check / tv3_fit measure it)
assert TM_TXT_W <= TM_INNER
TM_HEAD_H, TM_LINE_H = 64, 22
TM_MSG_H = 44
TM_RESPEC_ON, TM_RESPEC_OFF = "Click again to respec", "Respec this tree"
for _t, _w in ((TM_RESPEC_ON, TM_INNER), (TM_RESPEC_OFF, TM_INNER), ("Learn", TM_INNER)):
    assert SUI.text_width(_t, 17, True, upper=True) + 48 <= _w, _t
TM_PANEL_PARTS = [TM_HEAD_H, TM_LINE_H, TM_LINE_H, SUI.BTN_SMALL_H + 6, SUI.BTN_SMALL_H + 6, 10, 20, TR_DET_NAME_H, TM_LINE_H,
                  TR_DET_STATE_H, TR_DET_LINE_H, TR_DET_LINE_H, 26, TR_DET_NEED_H, TR_DET_HOW_H, SUI.BTN_H + 6, SUI.BTN_H + 6, TM_MSG_H]
TM_PANEL_SLACK = SUI.fit(TM_PANEL_PARTS, SUI.MAP_CANVAS_H - 2 * SUI.WELL_PAD, "0.5.0 map page right panel")
TM_RAIL_SPACER = SUI.MAP_CANVAS_H - (5 * SUI.MAP_PAGE_ROW_H + (sum(len(ts_) for _n, ts_ in TM_SKILL_PAGES) + 1) * SUI.MAP_TREE_ROW_H
                                     + 4 * SUI.MAP_LEGEND_ROW_H)
assert TM_RAIL_SPACER >= 0, TM_RAIL_SPACER
for _n in V3_SKILL_ORDER + CLASSES + ["No class yet", "Class trees are off"]:
    assert SUI.text_width(_n, 15, True) <= SUI.MAP_RAIL_W - 50, _n
assert SUI.text_width("Lv 100 - 999 points free", SUI.MAP_CAP_SIZE) <= SUI.MAP_RAIL_W - 50
for _n in TM_PAGE_NAMES + ["Rebirth Nexus"]:
    assert SUI.text_width(_n.upper(), 16, True) <= SUI.MAP_RAIL_W - 16, _n


def tm_chain(conds, parent, markups, app):
    """if (c0) <markup 0> else if (c1) <markup 1> ... else <last> (app(parent, markup, show): only markup 0 goes into the preview)"""
    out = []
    for n_, mk in enumerate(markups):
        head = ("if (%s) " % conds[n_]) if n_ == 0 else (("else if (%s) " % conds[n_]) if n_ < len(conds) else "else ")
        out.append(head + app(parent, mk, n_ == 0))
    return "\n".join(out)


def tm_page_java():
    """TreePage.build(): the hub page (rows 1 + 2, no sub row, no footer), the content row rail | map | panel (Java) + the static preview"""
    sh = SUI.hub_page("SkyyTrF", HUB, sub=False, footer=False, body_id="SkyyTrFB", content_id="SkyyTrRoot", content_layout="Left")
    assert sh.content_w == SUI.HUB_PAGE_IW and sh.content_h == SUI.MAP_CANVAS_H, (sh.content_w, sh.content_h)
    hub_build = SUI.java_hub_page(sh, cls="@PKG@.HubBar", uuid="u", tab_expr="this.hubSel()")
    row = sh.content
    marks = list(sh.appends.markups())
    pv = []

    def app(parent, markup, show=True):
        marks.append(markup)
        if show:
            pv.append(("#" + parent if not parent.startswith("#") else parent, markup))
        return SUI.java_append(parent, markup)

    def chain(conds, parent, markups):
        return tm_chain(conds, parent, markups, app)

    def bind(sel, act):
        return 'ev.addEventBinding(@BT@.Activating, "#%s", @EVD@.of("a", "%s"));' % (sel, act)

    def tset(ident, expr):
        return 'b.set("#%s.Text", %s);' % (ident, expr)
    # ---- the left rail
    rail = [app(row, SUI.group(TMP + "Rail", layout="Top", w=SUI.MAP_RAIL_W, h=SUI.MAP_CANVAS_H))]
    rp = TMP + "Rail"

    def rail_row(rid, kind, cond, sets, act, **parts):
        """one rail row: the row (selected while cond; cond None = never selected), its parts, its texts (b.set), its click"""
        mk = SUI.map_rail_row(rid, kind, False)
        out = [app(rp, mk if cond is None else SUI.choose(cond, SUI.map_rail_row(rid, kind, True), mk))]
        out += [app(p2_, mk_) for p2_, mk_ in SUI.map_rail_parts(rid, kind, **parts)]
        return out + [tset(rid + k_, e_) for k_, e_ in sets] + [bind(rid, act)]
    for p_, (pname, trees) in enumerate(TM_SKILL_PAGES):
        rail += rail_row(TMP + "Rp%d" % p_, "page", "pg == %d" % p_, [("L", SUI.java_lit(pname))], "tmp%d" % p_)
        for n_ in trees:
            tv_ = TM_SKTV[n_]
            rail += rail_row(TMP + "Rt%d" % tv_, "tree", "tv == %d" % tv_,
                             [("N", SUI.java_lit(V3T[tv_]["name"])), ("S", "@PKG@.TreeMap.railSub(@PKG@.TreeMap.stat(u, d0, %d, false))" % tv_)],
                             "tmt%d" % tv_, icon=V3_ICON[tv_], col=TM_TCOL[tv_])
    rail += rail_row(TMP + "Rp3", "page", "pg == 3", [("L", '"Class"')], "tmp3")
    rail += rail_row(TMP + "Rc", "tree", "cl",
                     [("N", "rci >= 0 ? @PKG@.TreeClass.CLASSES[rci] : (rctab ? \"No class yet\" : \"Class trees are off\")"),
                      ("S", "rci >= 0 && rctab ? @PKG@.TreeMap.railSub(@PKG@.TreeMap.stat(u, rpb ? this.pd : d0, rci, rpb)) : (rctab ? \"Choose one with /class\" : \"Server Setup -> Trees\")")],
                     "tmc", icon=SUI.J("rcic", CICON[0]), col=SUI.J("rccol", CCOLOR[0]))
    rail.append("if (nexus) {")
    rail += rail_row(TMP + "Rp4", "page", None, [("L", '"Rebirth Nexus"')], "tmnx")
    rail.append("} else {")
    rail.append(app(rp, SUI.spacer(h=SUI.MAP_PAGE_ROW_H), show=False))
    rail.append("}")
    rail.append(app(rp, SUI.spacer(h=TM_RAIL_SPACER)))
    for lrow, kids in SUI.map_legend(TMP, [(TM_PATHS["Node/%sL13" % TM_CPIC[TM_SKTV["Mining"]]], "learnt - ring in the tree colour"),
                                           (TM_PATHS["Node/Ready"], "ready - gold ring"), (TM_PATHS["Node/Locked"], "locked - padlock"),
                                           (TM_PATHS["Halo"], "selected - cyan halo")]):
        rail.append(app(rp, lrow))
        rail += [app(p2_, mk_) for p2_, mk_ in kids]
    rail.append(app(row, SUI.spacer(w=SUI.MAP_GAP)))
    # ---- the map (or the Loadout view / the no-class text)
    W0, H0 = SUI.MAP_CANVAS_W, SUI.MAP_CANVAS_H
    cv1 = "Group #%sCv { Anchor: (Width: %d, Height: %d); Background: %s; }" % (TMP, W0, H0, SUI.COLOR["well"])
    mp = []
    mp.append("if (lm) {")
    mp.append("{{LOADOUT}}")
    mp.append("} else if (L < 0) {")
    mp.append(app(row, cv1, show=False))
    mp.append(app(TMP + "Cv", SUI.label(TMP + "NoC", "", "message", w=W0 - 120, h=140, wrap=True, anchor={"left": 60, "top": 300}), show=False))
    mp.append(tset(TMP + "NoC", 'ucls != null ? "Your class " + ucls + " has no skill tree yet - it comes in a later build." : "Choose a class with /class - or create a profile - and your class tree opens here: 3 branches of 6 rows, 1 point a class level, each row\'s ability comes free."'))
    mp.append("} else {")
    for zi_ in range(len(TM_ZOOMS)):
        head = "  if (z == 0) {" if zi_ == 0 else ("  } else if (z == %d) {" % zi_)
        mp.append(head)
        if zi_ == 0:
            mp.append(app(row, cv1))
        else:
            cw_, ch_ = TM_ZL[0][zi_]["W"], TM_ZL[0][zi_]["H"]
            # every layout of one zoom has the same canvas size (W x z, H x z)
            assert all(TM_ZL[L_][zi_]["W"] == cw_ and TM_ZL[L_][zi_]["H"] == ch_ for L_ in range(TM_NL))
            a_, b_, c_ = SUI.map_scroll(TMP + "Out", TMP + "In", TMP + "Cv", W0, H0, cw_, ch_)
            mp += [app(row, a_, False), app(TMP + "Out", b_, False), app(TMP + "In", c_, False)]
    mp.append("  }")
    mp.append("  String[] tex = new String[codes.length];")
    mp.append("  boolean[] lit = new boolean[@PKG@.TreeMap.edges(L).length];")
    mp.append("  @PKG@.TreeMap.paint(u, d, L, pb, tex, lit);")
    mp.append('  this.lastEls = @PKG@.TreeMap.mapDraw(b, ev, @PKG@.TreeMap.lines(L, z), "#%sCv", lit, tex, ms, "tmn");' % TMP)
    mp.append("  if (cl) {")
    for zi_ in range(len(TM_ZOOMS)):
        lz_ = TM_ZL[TM_NL - 1][zi_]
        isz = lz_["emb"] // 2
        mp.append(("    if (z == %d) " % zi_) + app(TMP + "Cv", SUI.item_icon(TMP + "EmI", SUI.J("eic", CICON[0]), size=isz,
                                                                           anchor={"left": lz_["emb_l"] + (lz_["emb"] - isz) // 2,
                                                                                   "top": lz_["emb_t"] + (lz_["emb"] - isz) // 2}), False))
    mp.append("  }")
    mp.append("}")
    mp.append(app(row, SUI.spacer(w=SUI.MAP_GAP)))
    # ---- the right panel
    pn = TMP + "Pn"
    pl = [app(row, SUI.panel(pn, "well", w=SUI.MAP_PANEL_W, h=SUI.MAP_CANVAS_H))]
    pl.append(app(pn, SUI.group(TMP + "Ph", layout="Left", w=TM_INNER, h=TM_HEAD_H)))
    pl.append(app(TMP + "Ph", SUI.item_icon(TMP + "PhI", SUI.J("tic", V3_ICON[NC]), size=40, anchor={"top": 12, "right": 10})))
    pl.append(app(TMP + "Ph", SUI.group(TMP + "PhC", layout="Top", w=TM_INNER - 50, h=TM_HEAD_H)))
    pl.append(app(TMP + "PhC", SUI.label(TMP + "PhN", "", "heading", col=SUI.J("col", TM_TCOL[NC]), h=34, w=TM_INNER - 50, wrap=False)))
    pl.append(app(TMP + "PhC", SUI.label(TMP + "PhL", "", "default", size=15, h=24, w=TM_INNER - 50)))
    pl.append(app(pn, SUI.label(TMP + "PhP", "", "bold", size=15, col="gold", h=TM_LINE_H, w=TM_TXT_W)))
    pl.append(app(pn, SUI.label(TMP + "PhR", "", "caption", size=SUI.MAP_CAP_SIZE, h=TM_LINE_H, w=TM_TXT_W)))
    zr, zk = SUI.map_zoom_row(TMP, TM_INNER)
    pl.append(app(pn, zr))
    pl += [app(p2_, mk_) for p2_, mk_ in zk]
    pl.append(app(pn, SUI.spacer(h=6)))
    pl += [bind(TMP + "ZmO", "tmzo"), bind(TMP + "ZmI", "tmzi"), tset(TMP + "ZmL", '@PKG@.TreeMap.ZPCT[z] + " %"')]
    pl.append("if (cl && ci >= 0) {")
    pl.append(app(pn, SUI.group(TMP + "LoR", layout="Left", w=TM_INNER, h=SUI.BTN_SMALL_H)))
    pl.append(chain(["lm"], TMP + "LoR", [SUI.button(TMP + "Lo", "Talents", "tertiary", "small", w=TM_INNER, selected=True),
                                          SUI.button(TMP + "Lo", "Loadout", "tertiary", "small", w=TM_INNER)]))
    pl.append(bind(TMP + "Lo", "tmlo"))
    pl.append("} else {")
    pl.append(app(pn, SUI.spacer(h=SUI.BTN_SMALL_H), False))
    pl.append("}")
    pl.append(app(pn, SUI.spacer(h=6)))
    pl.append(app(pn, SUI.separator("content", w=TM_TXT_W, anchor={"top": 2, "bottom": 2})))
    fg0 = SUI.color_by([("st0 == 1", "success"), ("st0 == 2", "info"), ("st0 == 3", "gold"), ("st0 == 6", "gold")], "disabled")
    pl.append(app(pn, SUI.label(TMP + "Cap", "", "caption", size=SUI.MAP_CAP_SIZE, h=20, w=TM_TXT_W)))
    pl.append(app(pn, SUI.label(TMP + "Name", "", "rowName", h=TR_DET_NAME_H, w=TM_TXT_W, col=SUI.J("col", TM_TCOL[NC]))))
    pl.append(app(pn, SUI.label(TMP + "Rank", "", "bold", size=15, col="gold", h=TM_LINE_H, w=TM_TXT_W)))
    pl.append(app(pn, SUI.label(TMP + "State", "", "bold", h=TR_DET_STATE_H, w=TM_TXT_W, wrap=True, col=fg0)))
    pl.append(app(pn, SUI.label(TMP + "Now", "", "default", h=TR_DET_LINE_H, w=TM_TXT_W, wrap=True, col="value")))
    pl.append(app(pn, SUI.label(TMP + "Next", "", "default", h=TR_DET_LINE_H, w=TM_TXT_W, wrap=True)))
    pl.append(app(pn, SUI.label(TMP + "Cost", "", "bold", h=26, w=TM_TXT_W, col="gold")))
    pl.append(app(pn, SUI.label(TMP + "Need", "", "default", h=TR_DET_NEED_H, w=TM_TXT_W, wrap=True, col=SUI.color_by([("nok", "success")], "error"))))
    pl.append(app(pn, SUI.label(TMP + "How", "", "summary", h=TR_DET_HOW_H, w=TM_TXT_W, wrap=True, max_lines=False)))
    pl.append(app(pn, SUI.spacer(h=TM_PANEL_SLACK)))
    pl.append(app(pn, SUI.group(TMP + "LeR", layout="Left", w=TM_INNER, h=SUI.BTN_H, anchor={"bottom": 6})))
    pl.append(chain(["can"], TMP + "LeR", [SUI.button(TMP + "Le", "Learn", "primary", w=TM_INNER),
                                           SUI.button(TMP + "Le", "Learn", "secondary", w=TM_INNER, disabled=True)]))
    pl.append(bind(TMP + "Le", "trbuy"))
    pl.append(app(pn, SUI.group(TMP + "RsR", layout="Left", w=TM_INNER, h=SUI.BTN_H, anchor={"bottom": 6})))
    pl.append(chain(["tv < 0", "armed"], TMP + "RsR", [SUI.button(TMP + "Rs", TM_RESPEC_OFF, "secondary", w=TM_INNER, disabled=True),
                                                       SUI.button(TMP + "Rs", TM_RESPEC_ON, "destructive", w=TM_INNER),
                                                       SUI.button(TMP + "Rs", TM_RESPEC_OFF, "secondary", w=TM_INNER)]))
    pl.append(bind(TMP + "Rs", "trrespec"))
    pl.append(app(pn, SUI.label(TMP + "Msg", "", "default", size=15, bold=True, h=TM_MSG_H, w=TM_TXT_W, wrap=True, align="Center",
                                col=SUI.J("infoColor(this.msg)", SUI.COLOR["success"]))))
    pl += [tset(TMP + "PhN", "tn"), tset(TMP + "PhL", "hl"), tset(TMP + "PhP", "pl"), tset(TMP + "PhR", "rl"),
           tset(TMP + "Cap", "cap"), tset(TMP + "Name", "nm"), tset(TMP + "Rank", "rkl"), tset(TMP + "State", "stl"),
           tset(TMP + "Now", "nowl"), tset(TMP + "Next", "nextl"), tset(TMP + "Cost", "costl"), tset(TMP + "Need", "need"),
           tset(TMP + "How", "how"), tset(TMP + "Msg", "this.msg == null ? \"\" : this.msg")]
    return sh, hub_build, rail, mp, pl, marks, pv


TM_SH, TM_HUBJ, TM_RAILJ, TM_MAPJ, TM_PANELJ, TM_MARKS, TM_PV = tm_page_java()


def tm_loadout_java():
    """the Class page's Loadout view (the map's place): today's Abilities well + the Lattice (0.3.13 / 0.4.0 code, unchanged markup;
    the detail well holds a hint until an ability is clicked) - the parts of v3_class_page_java, in the same order"""
    marks = TM_MARKS

    def app(parent, markup, _show=True):
        marks.append(markup)
        return SUI.java_append(parent, markup)

    def chain(conds, parent, markups):
        return tm_chain(conds, parent, markups, app)
    body = app("SkyyTrRoot", SUI.group("SkyyTrBody", "Left", w=SUI.MAP_CANVAS_W, h=SUI.MAP_CANVAS_H))
    j_, k2_ = SUI.J("j", "0"), SUI.J("k2", "0")
    apanel = [app("SkyyTrBody", SUI.panel("SkyyTrAp", "well", w=TRC_AP_W, h=TR_GRID_H, anchor={"left": TRC_AP_GAP})),
              app("SkyyTrAp", SUI.label("SkyyTrApT", "Abilities", "subtitle", h=TRC_AP_TITLE_H))]
    apno = app("SkyyTrAp", SUI.label("SkyyTrApNo", "", "message", h=TRC_AP_NO_H, wrap=True, anchor={"top": 6}))
    aphint = app("SkyyTrAp", SUI.label("SkyyTrApH", "", "caption", h=TRC_AP_HINT_H, wrap=True, anchor={"bottom": 6}))

    def card3(cid, item, state, gap):
        c = SUI.icon_cell(cid, item, state=state, w=TRC_AP_IN_W, h=TRC_CARD_H, icon=TRC_CARD_ICON, icon_left=TRC_CARD_IL, anchor={"bottom": gap})
        return _tr_in(c, SUI.label(cid + "N", "", "rowName", w=TRC_CARD_TXT_W, h=24, col="white" if state == "selected" else "rowName", anchor={"left": TRC_CARD_TXT_L, "top": 4}),
                      SUI.label(cid + "K", "", "rowSub", w=TRC_CARD_TXT_W, h=20, col="gold", anchor={"left": TRC_CARD_TXT_L, "top": 28}),
                      SUI.label(cid + "U", "", "rowSub", w=TRC_CARD_TXT_W, h=20, anchor={"left": TRC_CARD_TXT_L, "top": 48}))
    acard = app("SkyyTrAp", card3("SkyyTrAc" + j_, SUI.J("aicon", "Weapon_Staff_Iron"), "normal", TRC_CARD_GAP))

    def tile(state):
        c = SUI.icon_cell("SkyyTrFt" + k2_, SUI.J("tic2", "Rock_Gem_Ruby"), state=state, w=TRC_AP_IN_W, h=TRC_TILE_H, icon=TRC_TILE_ICON,
                          icon_left=TRC_TILE_IL, anchor={"bottom": TRC_TILE_GAP})
        ncol = {"selected": "white", "disabled": "disabled"}.get(state, "rowName")
        return _tr_in(c, SUI.label("SkyyTrFt" + k2_ + "N", "", "rowName", w=TRC_TILE_TXT_W, h=TRC_TILE_N_H, size=TRC_TILE_N_SIZE, col=ncol,
                                   anchor={"left": TRC_TILE_TXT_L, "top": TRC_TILE_N_T}),
                      SUI.label("SkyyTrFt" + k2_ + "S", "", "rowSub", w=TRC_TILE_TXT_W, h=TRC_TILE_S_H, size=TRC_TILE_S_SIZE, wrap=True,
                                col="disabled" if state == "disabled" else "rowSub", anchor={"left": TRC_TILE_TXT_L, "top": TRC_TILE_S_T}))
    focus = [app("SkyyTrAp", SUI.group("SkyyTrFbR", "Left", h=SUI.BTN_SMALL_H, anchor={"bottom": 6})),
             app("SkyyTrFbR", SUI.button("SkyyTrFb", TRC_ALL_TEXT, "secondary", size="small", w=TRC_AP_IN_W, sound="cancel")),
             chain(["fheld"], "SkyyTrAp", [card3("SkyyTrFc", SUI.J("ficon", "Weapon_Staff_Iron"), "selected", 6),
                                           card3("SkyyTrFc", SUI.J("ficon", "Weapon_Staff_Iron"), "normal", 6)]),
             app("SkyyTrAp", SUI.label("SkyyTrFsL", "", "rowSub", h=TRC_FS_L_H, size=TRC_FS_L_SIZE, wrap=True, col="gold")),
             app("SkyyTrAp", SUI.label("SkyyTrFsG", "", "default", h=TRC_FS_G_H, size=TRC_FS_G_SIZE, wrap=True, col="value", anchor={"bottom": 2})),
             app("SkyyTrAp", SUI.section(None, "Modifiers"))]
    ftile = chain(["ts == 0", "ts == 2"], "SkyyTrAp", [tile("disabled"), tile("selected"), tile("normal")])
    fmax = [app("SkyyTrAp", SUI.group("SkyyTrFxR", "Left", h=TRC_FX_H)),
            app("SkyyTrFxR", SUI.button("SkyyTrFx", "Max Up", "secondary", size="small", w=TRC_FB_W)),
            app("SkyyTrFxR", SUI.label("SkyyTrFxT", "", "rowSub", w=TRC_AP_IN_W - TRC_FB_W - 6, h=TRC_FX_H, size=TRC_FX_SIZE, wrap=True, anchor={"left": 6}))]
    detp = app("SkyyTrBody", SUI.panel("SkyyTrDet", "well", w=TR_DET_W, h=TR_GRID_H, anchor={"left": TRC_DET_GAP}))
    hint = app("SkyyTrDet", SUI.label("SkyyTrLyHint", "", "message", h=120, wrap=True, anchor={"top": 40}))
    r2_, q2_ = SUI.J("r2", "0"), SUI.J("q2", "0")
    lat = [app("SkyyTrDet", SUI.section(None, "Loadout")),
           app("SkyyTrDet", SUI.label("SkyyTrLyS", "", "default", h=TRC_LY_STATUS_H, wrap=True, col="value", anchor={"bottom": 4}))]

    def acellL(state):
        return SUI.icon_cell("SkyyTrLy" + r2_ + "A", None if state == "empty" else SUI.J("ric", "Weapon_Staff_Iron"), state=state,
                             w=TRC_LY_CELL, h=TRC_LY_CELL, icon=TRC_LY_ICON, anchor={"right": 8})

    def mcellL(state, lab_col):
        c = SUI.icon_cell("SkyyTrLyM" + q2_, None if state == "empty" else SUI.J("mic", "Rock_Gem_Ruby"), state=state, w=TRC_LY_MOD_W,
                          h=TRC_LY_CELL, icon=TRC_LY_MOD_ICON, icon_left=(TRC_LY_MOD_W - TRC_LY_MOD_ICON) // 2, anchor={"right": TRC_LY_GAP})
        return _tr_in(c, SUI.label("SkyyTrLyM" + q2_ + "T", "", "rowSub", w=TRC_LY_MOD_W - 2, h=TRC_LY_LAB_H, size=12, bold=True, align="Center",
                                   col=lab_col, anchor={"left": 1, "top": TRC_LY_LAB_T}))
    lrow = [app("SkyyTrDet", SUI.group("SkyyTrLy" + r2_, "Top", h=TRC_LY_KEY_H + TRC_LY_CELL, anchor={"bottom": TRC_LY_ROW_GAP})),
            app("SkyyTrLy" + r2_, SUI.label("SkyyTrLy" + r2_ + "K", "", "bold", h=TRC_LY_KEY_H, col=SUI.color_by([("ru", "rowName")], "disabled"))),
            app("SkyyTrLy" + r2_, SUI.group("SkyyTrLy" + r2_ + "C", "Left", h=TRC_LY_CELL)),
            chain(["rs == 0", "rs == 2"], "SkyyTrLy" + r2_ + "C", [acellL("empty"), acellL("selected"), acellL("normal")])]
    lmod = chain(["ms2 == 0", "ms2 == 1"], "SkyyTrLy" + r2_ + "C", [mcellL("empty", "disabled"), mcellL("empty", "value"), mcellL("normal", "rowName")])
    lelem = [app("SkyyTrDet", SUI.group("SkyyTrLyE", "Left", h=TRC_LY_ELEM_H, anchor={"bottom": 6})),
             app("SkyyTrLyE", SUI.label("SkyyTrLyEL", "", "rowSub", w=TRC_LY_ELEM_W, h=TRC_LY_ELEM_H, wrap=True)),
             app("SkyyTrLyE", SUI.button("SkyyTrLyEB", "Change", "secondary", size="small", w=TRC_FB_W, anchor={"left": 8}))]
    ltail = [app("SkyyTrDet", SUI.section(None, "What it does")),
             app("SkyyTrDet", SUI.label("SkyyTrLyH", "", "summary", h=TRC_LY_HOW_H, size=TRC_LY_HOW_SIZE, wrap=True, max_lines=False))]
    parts = {"BODY": body, "APANEL": "\n".join(apanel), "APNO": apno, "APHINT": aphint, "ACARD": acard, "FOCUS": "\n".join(focus),
             "FTILE": ftile, "FMAX": "\n".join(fmax), "DETP": detp, "HINT": hint, "LAT": "\n".join(lat), "LROW": "\n".join(lrow),
             "LMOD": lmod, "LELEM": "\n".join(lelem), "LTAIL": "\n".join(ltail)}
    return tv3_fill(TM_LOADOUT, parts, {"BODY": 2, "APANEL": 2, "APNO": 4, "APHINT": 4, "ACARD": 6, "FOCUS": 4, "FTILE": 6, "FMAX": 6,
                                        "DETP": 2, "HINT": 4, "LAT": 4, "LROW": 6, "LMOD": 8, "LELEM": 8, "LTAIL": 4})


# the Loadout view: the 0.4.0 class page's Abilities well + Lattice Java (TV3C_BUILD from 'String acsv' on), unchanged but for the hint
TM_LOADOUT = r"""
String acsv = @PKG@.TreeV3.classCsv(d, ci);
Object[] ap = @PKG@.TreeClass.apanel(u, acsv);
boolean apOk = ap != null && ap.length >= 129 && "ok".equals(ap[0]);
int fr = (apOk && this.amode) ? @PKG@.TreeClass.rowOf(ap, this.afoc) : -1;
if (fr >= 0 && !@PKG@.TreeClass.usable(ap, fr)) fr = -1;
boolean am = fr >= 0;
if (!am) { this.amode = false; this.hk = 0; this.hmod = ""; }
int hk = this.hk;
String hmod = this.hmod == null ? "" : this.hmod;
int fb0 = 12 + (am ? fr : 0) * 16;
String[] amr = null;
if (am) amr = @PKG@.TreeClass.amods(u, this.afoc, acsv);
if (amr == null) amr = new String[0];
String[] ah = amr.length > 0 ? amr[0].split("\\|", -1) : new String[0];
int rbp = 0;
try { if (ah.length > 10) rbp = Integer.parseInt(ah[10].trim()); } catch (Throwable x2) { rbp = 0; }
int[] ord = new int[4];
int nOwn = 0;
if (apOk) {
  for (int ln = 1; ln <= 4; ln++) for (int i = 0; i < 4; i++) if (@PKG@.TreeClass.usable(ap, i) && ((Integer) ap[12 + i * 16 + 5]).intValue() == ln) { ord[nOwn] = i; nOwn++; }
}
{{BODY}}
{{APANEL}}
if (!apOk) {
{{APNO}}
  b.set("#SkyyTrApNo.Text", @PKG@.TreeClass.apanelMsg(ap, ci, ucls));
} else if (!am) {
{{APHINT}}
  b.set("#SkyyTrApH.Text", (nOwn == 0 ? "No abilities yet - your first comes with branch 1 row 1 at class level 1." : "Click an ability: its modifiers show here and your loadout on the right.") + (pb ? " Probe: view only." : ""));
  for (int j = 0; j < nOwn; j++) {
    int i = ord[j];
    int b0 = 12 + i * 16;
    String ricon = String.valueOf(ap[b0 + 2]);
    String aicon = ricon.length() > 0 ? ricon : @PKG@.TreeClass.CICON[ci];
{{ACARD}}
    b.set("#SkyyTrAc" + j + "N.Text", @PKG@.TreeClass.nameText(ap, i));
    b.set("#SkyyTrAc" + j + "K.Text", @PKG@.TreeClass.keyShort(i));
    b.set("#SkyyTrAc" + j + "U.Text", @PKG@.TreeClass.usesText(ap, i));
    ev.addEventBinding(@BT@.Activating, "#SkyyTrAc" + j, @EVD@.of("a", "tyca" + i));
  }
} else {
  String fric = String.valueOf(ap[fb0 + 2]);
  String ficon = fric.length() > 0 ? fric : @PKG@.TreeClass.CICON[ci];
  boolean fheld = hk == 1;
{{FOCUS}}
  b.set("#SkyyTrFcN.Text", @PKG@.TreeClass.nameText(ap, fr));
  b.set("#SkyyTrFcK.Text", @PKG@.TreeClass.keyShort(fr) + (fheld ? " - held" : ""));
  b.set("#SkyyTrFcU.Text", @PKG@.TreeClass.usesText(ap, fr));
  b.set("#SkyyTrFsL.Text", String.valueOf(ap[125 + fr]));
  b.set("#SkyyTrFsG.Text", "Level bonus: " + String.valueOf(ap[103 + fr]));
  ev.addEventBinding(@BT@.Activating, "#SkyyTrFb", @EVD@.of("a", "tyfb"));
  ev.addEventBinding(@BT@.Activating, "#SkyyTrFc", @EVD@.of("a", "tyfc"));
  for (int k2 = 0; k2 < amr.length - 1 && k2 < 5; k2++) {
    String[] f = amr[k2 + 1].split("\\|", -1);
    if (f.length < 12) continue;
    boolean un = "1".equals(f[3]);
    int ts = !un ? 0 : ((hk == 2 && f[0].equals(hmod)) ? 2 : 1);
    int cnt = 0;
    try { cnt = Integer.parseInt(f[7].trim()); } catch (Throwable x6) { cnt = 0; }
    String tic2 = @PKG@.TreeClass.modIcon(f[0]);
{{FTILE}}
    b.set("#SkyyTrFt" + k2 + "N.Text", f[1] + (un ? " Lv " + f[4] + (cnt > 0 ? " - " + cnt + " slot" + (cnt == 1 ? "" : "s") : "") : ""));
    b.set("#SkyyTrFt" + k2 + "S.Text", @PKG@.TreeClass.tileText(un, f, String.valueOf(ap[fb0 + 1])));
    ev.addEventBinding(@BT@.Activating, "#SkyyTrFt" + k2, @EVD@.of("a", "tyft" + k2));
  }
  if (rbp > 0) {
{{FMAX}}
    b.set("#SkyyTrFxT.Text", "Rebirth: " + rbp + " upgrade" + (rbp == 1 ? "" : "s") + " - hold a modifier first");
    ev.addEventBinding(@BT@.Activating, "#SkyyTrFx", @EVD@.of("a", "tymx"));
  }
}
{{DETP}}
if (!am) {
{{HINT}}
  b.set("#SkyyTrLyHint.Text", apOk ? "Click an ability on the left: its modifiers show there and your loadout (the Lattice) here." : "");
} else {
  boolean fight = Boolean.TRUE.equals(ap[3]);
  String fnm = String.valueOf(ap[fb0 + 1]);
  int imb = ap[111] instanceof Integer ? ((Integer) ap[111]).intValue() : -1;
{{LAT}}
  b.set("#SkyyTrLyS.Text", fight ? "In combat - change your loadout out of combat." : (hk == 1 ? "Holding " + fnm + ": click an ability slot (the two trade places)." : (hk == 2 ? "Holding " + @PKG@.TreeClass.modNm(hmod) + ": click a modifier slot in " + fnm + "'s row (" + @PKG@.TreeClass.keyShort(fr) + ")." : "Click an ability or a modifier, then a slot. A filled modifier slot clicked with nothing held empties it.")) + (pb ? " Probe: view only." : ""));
  for (int r2 = 0; r2 < 4; r2++) {
    int rb0 = 12 + r2 * 16;
    boolean ru = @PKG@.TreeClass.usable(ap, r2);
    String rric = String.valueOf(ap[rb0 + 2]);
    String ric = rric.length() > 0 ? rric : @PKG@.TreeClass.CICON[ci];
    int rsl = ru ? ((Integer) ap[rb0 + 14]).intValue() : 0;
    int ncl = rsl > 2 ? rsl : 2;
    int rs = !ru ? 0 : ((hk == 1 && r2 == fr) ? 2 : 1);
{{LROW}}
    b.set("#SkyyTrLy" + r2 + "K.Text", @PKG@.TreeClass.keyShort(r2) + " - " + (ru ? String.valueOf(ap[rb0 + 1]) : "empty"));
    ev.addEventBinding(@BT@.Activating, "#SkyyTrLy" + r2 + "A", @EVD@.of("a", "tyla" + r2));
    for (int j2 = 0; j2 < ncl && j2 < 4; j2++) {
      int q2 = r2 * 4 + j2;
      String mn = @PKG@.TreeClass.modName(ap, r2, j2);
      boolean mo = j2 < rsl;
      int ms2 = !mo ? 0 : (mn.length() == 0 ? 1 : 2);
      String mic = @PKG@.TreeClass.modIcon(mn);
{{LMOD}}
      b.set("#SkyyTrLyM" + q2 + "T.Text", !mo ? (j2 >= 2 ? "Rebirth" : "Closed") : (mn.length() == 0 ? "Empty" : mn + " " + @PKG@.TreeClass.modLvl(ap, r2, j2)));
      ev.addEventBinding(@BT@.Activating, "#SkyyTrLyM" + q2, @EVD@.of("a", "tylm" + q2));
    }
    if (r2 == imb) {
{{LELEM}}
      String elx9 = ap.length > 129 && ap[129] instanceof String ? (String) ap[129] : "";
      b.set("#SkyyTrLyEL.Text", elx9.length() > 0 ? elx9 : "Imbue element: " + String.valueOf(ap[112]) + " (an Elemental sword uses its own)");
      ev.addEventBinding(@BT@.Activating, "#SkyyTrLyEB", @EVD@.of("a", "tymat"));
    }
  }
{{LTAIL}}
  String[] dl = @PKG@.TreeClass.doesOf(String.valueOf(ap[fb0]));
  String dlt = "Rows: the Ability 2 / 3 keys and crouch + each. An ability sits in one row; its modifiers go in its own row (2 slots, rebirths add up to 2). Out of combat only. Modifiers unlock with the ability level or a class tree rank.";
  if (dl != null && dl[1].length() > 0) dlt = dl[1];
  b.set("#SkyyTrLyH.Text", dlt);
}"""
TM_LOADOUT_JAVA = tm_loadout_java()

TM_BUILD = r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  java.util.UUID u = this.playerRef.getUuid();
  int t = this.tree;
  boolean ctab = this.probe || @PKG@.TreeCfg.CLASS_ON;
  if (t < 0 || t > @PKG@.TreeDefs.NT + 2) t = 0;
  if (t == @PKG@.TreeDefs.NT && !ctab) t = 0;
  boolean cl = t == @PKG@.TreeDefs.NT;
  boolean pb = this.probe && cl;
  int ci = -1;
  String ucls = null;
  if (cl) {
    ci = pb ? this.pci : @PKG@.TreeClass.classIdx(@PKG@.TreeClass.classOf(u));
    if (ci >= @PKG@.TreeClass.NC) ci = -1;
    if (!pb && ci < 0) { ucls = @PKG@.TreeClass.classOf(u); if (ucls != null && ucls.length() > 20) ucls = ucls.substring(0, 20); }
  }
  int tv = cl ? ci : @PKG@.TreeV3.tvOfPage(u, t);
  if (!cl && tv < 0) { t = 0; tv = @PKG@.TreeV3.tvOfPage(u, 0); }
  @PKG@.TreeData d0 = @PKG@.TreeStore.data(u);
  @PKG@.TreeData d = (pb && this.pd != null) ? this.pd : d0;
  int pg = cl ? 3 : @PKG@.TreeMap.pageOf(tv);
  int L = cl ? (ci < 0 ? -1 : @PKG@.TreeMap.NSP + ci) : pg;
  int z = this.zoom < 0 ? 0 : (this.zoom >= @PKG@.TreeMap.ZN ? @PKG@.TreeMap.ZN - 1 : this.zoom);
  boolean lm = cl && ci >= 0 && this.lmode;
  int lvl = tv < 0 ? -1 : (pb ? @PKG@.TreeV3.PROBE_LVL : @PKG@.TreeV3.level(u, tv));
  int pts = (lvl < 0 ? 0 : lvl) + ((pb || tv < 0) ? 0 : @PKG@.TreeV3.head(u));
  int sp = tv < 0 ? 0 : @PKG@.TreeV3.spent(d, tv);
  int[] g = @PKG@.TreeV3.gates(tv < 0 ? 0 : tv);
  String tn = tv < 0 ? "Class" : (cl ? @PKG@.TreeClass.CLASSES[ci] : @PKG@.TreeV3.TNAME[tv]);
  String col = tv < 0 ? @PKG@.TreeMap.CLASS_COL : @PKG@.TreeMap.MCOL[tv];
  String tic = tv < 0 ? @PKG@.TreeMap.CLASS_ICON : @PKG@.TreeV3.TICON[tv];
  String eic = ci < 0 ? @PKG@.TreeMap.CLASS_ICON : @PKG@.TreePage.cemblem(ci);
  if (eic == null || eic.length() == 0) eic = ci < 0 ? @PKG@.TreeMap.CLASS_ICON : @PKG@.TreeClass.CICON[ci];
  int[] codes = L < 0 ? new int[0] : @PKG@.TreeMap.nodes(L);
  int ms = this.msel;
  if (ms < 0 || ms >= codes.length || lm || this.mselL != L) ms = -1;
  int sc = ms < 0 ? 0 : codes[ms];
  int su = ms < 0 ? -1 : (sc >= 0 ? sc : -1);
  int sr = ms < 0 ? -1 : @PKG@.TreeMap.nodeRow(sc);
  if (sr >= 0 && @PKG@.TreeV3.RT[sr] != tv) { ms = -1; su = -1; sr = -1; }
  int st0 = su >= 0 ? @PKG@.TreeV3.ustate(d, su, pts, sp, g) : ((sr >= 0 && (sp >= g[@PKG@.TreeV3.RNUM[sr]] || @PKG@.TreeV3.gfRow(d, sr)) && @PKG@.TreeV3.RFK[sr] != 0) ? 6 : 7);
  boolean can = su >= 0 && st0 == 1 && d != null && !d.bad;
  boolean nexus = @PKG@.TreeMap.nexusOn();
  boolean armed = this.armT == t && System.currentTimeMillis() - this.armAt <= 10000L;
  boolean rpb = this.probe;
  boolean rctab = ctab;
  int rci = rpb ? this.pci : @PKG@.TreeClass.classIdx(@PKG@.TreeClass.classOf(u));
  if (rci >= @PKG@.TreeClass.NC) rci = -1;
  String rcic = rci < 0 ? @PKG@.TreeMap.CLASS_ICON : @PKG@.TreeClass.CICON[rci];
  String rccol = rci < 0 ? @PKG@.TreeMap.CLASS_COL : @PKG@.TreeClass.CCOLOR[rci];
  String hl = tv < 0 ? (ucls != null ? ucls + " - no tree yet" : "No class yet") : (lvl < 0 ? "SkyySkills missing" : (cl ? @PKG@.TreeClass.CSKILL[ci] + " " + lvl : "Level " + lvl) + (pb ? " (probe)" : ""));
  String pl = tv < 0 ? "" : (lvl < 0 ? "Points need SkyySkills" : (pts - sp) + " of " + pts + " points free" + @PKG@.TreeMap.nextRow(tv, g, sp));
  String rl = tv < 0 ? "" : (pb ? "Respec free (probe)" : @PKG@.TreeV3.priceText(d, tv, lvl < 0 ? 0 : lvl));
  String cap = L < 0 ? "" : (lm ? "Your abilities and loadout - Talents shows the tree again." : "Click a talent on the map to see its ranks and learn it.");
  String nm = "";
  String rkl = "";
  String stl = "";
  String nowl = "";
  String nextl = "";
  String costl = "";
  String need = "";
  String how = "";
  if (sr >= 0) {
    int bb = @PKG@.TreeV3.RB[sr];
    cap = tn + " - " + @PKG@.TreeV3.BNAME[bb] + " - Row " + @PKG@.TreeV3.RNUM[sr] + (@PKG@.TreeV3.RCAP[sr] ? " - capstone" : "");
    nm = su >= 0 ? @PKG@.TreeV3.UNAME[su] : @PKG@.TreeV3.RFNAME[sr];
    rkl = su >= 0 ? "Rank " + d.rk[su] + " / " + @PKG@.TreeV3.UMAX[su] : "Free " + (@PKG@.TreeV3.TKIND[tv] == 0 ? "ability" : "perk") + " of row " + @PKG@.TreeV3.RNUM[sr];
    stl = @PKG@.TreeV3.detState(d, sr, su, st0, g, sp, pts);
    nowl = @PKG@.TreeV3.detNow(d, sr, su, st0, sp, g);
    nextl = @PKG@.TreeV3.detNext(d, sr, su);
    costl = @PKG@.TreeV3.detCost(su, pts, sp);
    need = @PKG@.TreeV3.detNeed(d, sr, su, st0, g, sp, pts, lvl);
    how = @PKG@.TreeV3.detHow(sr, su);
  }
  boolean nok = need.length() == 0;
  if (sr >= 0 && nok) need = (su >= 0 && st0 == 1) ? "Ready to unlock" : (st0 == 3 ? "Max rank" : (st0 == 6 ? "Yours - it came free with its row" : ""));
{{SHELL}}
{{RAIL}}
{{MAP}}
{{PANEL}}
}"""
TM_BUILD_JAVA = tv3_fill(TM_BUILD, {"SHELL": TM_SH.java("b") + "\n" + TM_HUBJ, "RAIL": "\n".join(TM_RAILJ),
                                    "MAP": "\n".join(TM_MAPJ).replace("{{LOADOUT}}", "\n".join("  " + ln_ for ln_ in TM_LOADOUT_JAVA.split("\n"))),
                                    "PANEL": "\n".join(TM_PANELJ)},
                         {"SHELL": 2, "RAIL": 2, "MAP": 2, "PANEL": 2})
assert TM_BUILD_JAVA.count("@PKG@.HubBar.page17(") == 1 and '"< Back"' not in TM_BUILD_JAVA   # menu-pattern-ok: the check itself
# ---- the build-time checks of the page: the shell + rows 1 + 2 + the content (rail, the Gathering map at 100 %, the panel)
_pv = SUI.hub_page_preview(TM_SH, tabs=[(r_[0], SUI.hub_tab_label(HUB, r_[0])) for r_ in SUI.hub_page_tabs(HUB)], my_tab=HUB_TAB)
_pv_c = [(p_, mk_ if isinstance(mk_, str) else mk_.a) for p_, mk_ in TM_PV]   # a runtime choice: its first look
_cvi = [i_ for i_, (p_, mk_) in enumerate(_pv_c) if ("#" + TMP + "Cv {") in SUI.render(mk_ if isinstance(mk_, str) else mk_.a)][0]
_pv_c[_cvi + 1:_cvi + 1] = TM_NM00.markups(sel=0)
for p_, mk_ in _pv_c:
    _pv.append((p_, mk_))
_pv_chk = SUI.Appends(_pv)
SUI.check_page(_pv_chk, TR_PREFIX)
SUI.assert_proven(_pv_chk, what="TreePage 0.5.0 map page")
SUI.assert_proven(TM_MARKS, what="TreePage 0.5.0 every markup")
SUI.check_sky_paths(_pv_chk, tab_icons=True)
SUI.assert_menu_page(_pv_chk, TM_SH, what="TreePage 0.5.0 map page")
TM_PAGE_STATIC = sum(SUI._strip_quoted(SUI.render(mk_ if isinstance(mk_, str) else mk_.a)).count("{") for p_, mk_ in _pv) - TM_NM00.elements(lit=None, sel=0)
_pn_used = SUI.used_height(SUI.Appends([(p_, mk_) for p_, mk_ in TM_PV if p_.lstrip("#") == TMP + "Pn"]), TMP + "Pn")
assert _pn_used <= SUI.MAP_CANVAS_H - 2 * SUI.WELL_PAD, "0.5.0: the right panel holds %d px of %d" % (_pn_used, SUI.MAP_CANVAS_H - 2 * SUI.WELL_PAD)
TM_WORST = TM_PAGE_STATIC + max(TM_EL.values()) + 3
SUI.assert_map_elements(TM_WORST, what="SkyyTrees 0.5.0 worst map page (every line lit, scroll box, class emblem)")
print("0.5.0 map page: %d px content row (rail %d + map %d + panel %d), panel slack %d px, rail spacer %d px; %d elements without the map, "
      "worst page %d elements (guard %d); %d markups proven" % (SUI.HUB_PAGE_IW, SUI.MAP_RAIL_W, SUI.MAP_CANVAS_W, SUI.MAP_PANEL_W,
                                                               TM_PANEL_SLACK, TM_RAIL_SPACER, TM_PAGE_STATIC, TM_WORST, SUI.MAP_MAX_ELEMENTS, len(TM_MARKS)))

'''
P.rep('''F(page, "public int tree;")
F(page, "public int sel;")''', TM_BLOCK + '''F(page, "public int tree;")''')   # simplify: sel / vbr / vsel go (only the unused 0.4.x builders read them)

# ---------- the new page fields + the constructor
P.rep('''F(page, "public int vbr;")       # 0.4.0: the branch shown (0-2)
F(page, "public int vsel;")      # 0.4.0: the selected cell (row x 4 + column; column 0 = the row's free ability / perk)
''', '''F(page, "public int zoom;")      # 0.5.0: the map zoom (0 = 100 %, 1 = 150 %, 2 = 200 %)
F(page, "public int msel;")      # 0.5.0: the selected node of the map shown (-1 none)
F(page, "public int mselL;")     # 0.5.0 fix: the layout msel was picked on (a class / profile change under an open page drops it)
F(page, "public boolean lmode;")  # 0.5.0: the Class page shows the Loadout (Abilities + Lattice) instead of the map
F(page, "public boolean answered;")   # 0.5.0: this click's one page packet was sent (the safety net reads it)
F(page, "public int answers;")   # 0.5.0: page packets sent as click answers (the harness reads it)
F(page, "public int nets;")      # 0.5.0: how often the safety net sent the empty answer
F(page, "public int lastEls;")   # 0.5.0: the map elements the last build drew
''')
P.rep('''public TreePage(@PR@ pr, int tree) {
  super(pr, @LIFE@.CanDismiss);
  this.tree = tree;
  this.sel = 1;
''', '''public TreePage(@PR@ pr, int tree) {
  super(pr, @LIFE@.CanDismiss);
  this.tree = tree;
''')
P.rep('''  this.vbr = 0;
  this.vsel = 1;
}""")
# 0.3.16: the hub tab this page shows''', '''  this.zoom = 0;
  this.msel = -1;
  this.mselL = -1;
  this.lmode = false;
}""")
# 0.3.16: the hub tab this page shows''')

# ---------- build(): the map page (the 0.4.0 class tab buildClass is no longer a method; its Loadout part lives on in TM_LOADOUT)
P.rep('''M(page, TR_CBUILD_JAVA)   # 0.3 part 2: the class tab (build() calls it)
''', '''# 0.5.0: TR_CBUILD_JAVA (the 0.4.0 class tab) is built + checked above but no longer a method - the map page's Loadout view replaces it
''')
P.rep('''M(page, TR_BUILD_JAVA)
M(page, r"""
public void handleDataEvent(''', '''M(page, TM_BUILD_JAVA)   # 0.5.0: the radial map page (TR_BUILD_JAVA, the 0.4.0 rows page, is built + checked above, not a method)
M(page, r"""
public void handleDataEvent(''')

_i = P.s.index('M(page, r"""\npublic void handleDataEvent(')
_j = P.s.index("# ================= 0.2.2: admin config kit", _i)
OLD_EV = P.s[_i:_j]
assert OLD_EV.count("public void handleDataEvent(") == 1 and OLD_EV.rstrip().endswith('}""")')
NEW_EV = r'''# 0.5.0 THE CLICKS: every handled click answers with exactly ONE page packet (ans() = rebuild once; close(); a hub click that opened another
# page) and the safety net at the end of handleDataEvent sends the engine's empty update when nothing was sent and this page is still the
# player's open page (HANDOFF section 2; probe 0.7.1 "Loading..." fix). The rules of every click are TreeV3's / TreeClass's, unchanged.
M(page, r"""
public void ans() {
  this.answered = true;
  this.answers = this.answers + 1;
  rebuild();
}""")
M(page, r"""
public boolean stillOpen(@REF@ ref, @ST@ st) {
  try {
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    return p != null && p.getPageManager().getCustomPage() == this;
  } catch (Throwable t) { return false; }
}""")
M(page, r"""
public static int num(String a, int from) {
  try { return Integer.parseInt(a.substring(from)); } catch (Throwable t) { return -1; }
}""")
# the layout shown for the page's current tree (-1 = the Class page without a class tree)
M(page, r"""
public int curLayout(java.util.UUID u) {
  int t = this.tree;
  if (t < 0 || t > @PKG@.TreeDefs.NT + 2) t = 0;
  if (t == @PKG@.TreeDefs.NT) {
    if (!(this.probe || @PKG@.TreeCfg.CLASS_ON)) return 0;
    int ci = this.probe ? this.pci : @PKG@.TreeClass.classIdx(@PKG@.TreeClass.classOf(u));
    return (ci < 0 || ci >= @PKG@.TreeClass.NC) ? -1 : @PKG@.TreeMap.NSP + ci;
  }
  int tv = @PKG@.TreeV3.tvOfPage(u, t);
  return @PKG@.TreeMap.pageOf(tv < 0 ? @PKG@.TreeV3.tvOfPage(u, 0) : tv);
}""")
# go to page tree t (a page index of TreePage.tree): the selection, the respec arming and the Loadout view reset; LASTTREE as 0.4.x
M(page, r"""
public void go(java.util.UUID u, int t) {
  int l0 = curLayout(u);
  this.tree = t;
  if (curLayout(u) != l0) this.msel = -1;
  this.msg = "";
  this.armT = -1;
  this.lmode = false;
  this.amode = false;
  this.hk = 0;
  if (!(t == @PKG@.TreeDefs.NT && this.chub)) LASTTREE.put(u, Integer.valueOf(t));
}""")
# the Rebirth Nexus row: SkyyRebirth's page through rebirth:fn:open { Ref, Store } (a later SkyyRebirth), else /rebirth as the player (the hub
# fallback way); it opens in place of this page. Nothing opened -> this page answers with a line.
M(page, r"""
public void nexus(@REF@ ref, @ST@ st) {
  boolean ok = false;
  boolean cmd = false;
  try {
    Object f = @PKG@.TreeStore.bridge().get("rebirth:fn:open");
    if (f instanceof java.util.function.Function) ok = Boolean.TRUE.equals(((java.util.function.Function) f).apply(new Object[] { ref, st }));
  } catch (Throwable t) { ok = false; }
  if (!ok && @PKG@.TreeMap.nexusOn()) { cmd = true; ok = @PKG@.HubBar.run(this.playerRef, "rebirth") == 0; }
  if (stillOpen(ref, st)) {   // still our page: /rebirth was sent but opened nothing (it refused - e.g. Rebirth off - and says why in chat)
    this.msg = !ok ? "The Rebirth Nexus could not open here - try /rebirth" : (cmd ? "The Rebirth Nexus did not open - see the chat line (Rebirth may be off on this server)" : "");
    ans();
  }
}""")
M(page, r"""
public void handleIn(@REF@ ref, @ST@ st, String data) {
  if (data == null) return;
  java.util.UUID u = this.playerRef.getUuid();
  String a = @PKG@.HubBar.jsonStr(data, "a");
  if (this.chub && this.tree == @PKG@.TreeDefs.NT && "class".equals(hubSel()) && "hub:trees".equals(a)) {   // 0.3.16: Class tab mode -> Trees
    Object lo = LASTTREE.get(u);
    int lt = lo instanceof Integer ? ((Integer) lo).intValue() : 0;
    if (lt < 0 || lt > @PKG@.TreeDefs.NT + 2 || lt == @PKG@.TreeDefs.NT) lt = 0;
    this.chub = false;
    go(u, lt);
    this.msel = -1;
    ans();
    return;
  }
  String hr = @PKG@.HubBar.route(this.playerRef, data, "character", hubSel());
  if (hr != null) {
    if (hr.equals("close")) { this.answered = true; close(); return; }
    if (hr.equals("self")) { this.msg = ""; this.armT = -1; ans(); return; }
    if (!hr.equals("bridge") && !hr.equals("command") && !hr.equals("back")) { this.msg = "That tab could not open right now - try again."; ans(); }
    return;
  }
  boolean ctab = this.probe || @PKG@.TreeCfg.CLASS_ON;
  if (!ctab && this.tree == @PKG@.TreeDefs.NT) {   // class trees went OFF while the class page was open - show Mining, act on nothing
    go(u, 0);
    this.msg = "Class trees were switched off - this is the Mining tree now";
    ans();
    return;
  }
  if (a.startsWith("tmp") && a.length() == 4) {
    int p = num(a, 3);
    if (p == 3) {
      if (!ctab) { this.msg = "Class trees are switched off on this server"; ans(); return; }
      go(u, @PKG@.TreeDefs.NT);
      ans();
      return;
    }
    if (p < 0 || p >= @PKG@.TreeMap.NSP) return;
    int cur = this.tree == @PKG@.TreeDefs.NT ? -1 : @PKG@.TreeMap.pageOf(@PKG@.TreeV3.tvOfPage(u, this.tree));
    if (cur != p) go(u, @PKG@.TreeV3.TPAGE[@PKG@.TreeMap.PTV[@PKG@.TreeMap.PT0[p]]]);
    else { this.msg = ""; this.lmode = false; }
    ans();
    return;
  }
  if (a.equals("tmnx")) { nexus(ref, st); return; }
  if (a.equals("tmc")) {
    if (!ctab) { this.msg = "Class trees are switched off on this server"; ans(); return; }
    go(u, @PKG@.TreeDefs.NT);
    ans();
    return;
  }
  if (a.startsWith("tmt")) {
    int tv = num(a, 3);
    if (tv < @PKG@.TreeV3.NCV || tv >= @PKG@.TreeV3.NV) return;
    go(u, @PKG@.TreeV3.TPAGE[tv]);
    ans();
    return;
  }
  if (a.startsWith("tmn")) {
    int k = num(a, 3);
    int L = curLayout(u);
    int[] c = L < 0 ? new int[0] : @PKG@.TreeMap.nodes(L);
    if (k < 0 || k >= c.length) { this.msg = "That talent is not on this page any more"; ans(); return; }
    int ntv = @PKG@.TreeMap.nodeTv(c[k]);
    if (ntv >= @PKG@.TreeV3.NCV && @PKG@.TreeV3.TPAGE[ntv] != this.tree) {
      this.tree = @PKG@.TreeV3.TPAGE[ntv];
      this.armT = -1;
      LASTTREE.put(u, Integer.valueOf(this.tree));
    }
    this.msel = k;
    this.mselL = L;
    this.msg = "";
    ans();
    return;
  }
  if (a.equals("tmzo") || a.equals("tmzi")) {
    int z = this.zoom + (a.equals("tmzi") ? 1 : -1);
    this.zoom = z < 0 ? 0 : (z >= @PKG@.TreeMap.ZN ? @PKG@.TreeMap.ZN - 1 : z);
    this.lmode = false;
    this.msg = "";
    ans();
    return;
  }
  int t = this.tree;
  if (t < 0 || t > @PKG@.TreeDefs.NT + 2) t = 0;
  boolean cl = t == @PKG@.TreeDefs.NT;
  int tv = cl ? (this.probe ? this.pci : @PKG@.TreeClass.classIdx(@PKG@.TreeClass.classOf(u))) : @PKG@.TreeV3.tvOfPage(u, t);
  @PKG@.TreeData d = (this.probe && cl && this.pd != null) ? this.pd : @PKG@.TreeStore.data(u);
  if (a.equals("tmlo")) {
    if (!cl || tv < 0) return;
    this.lmode = !this.lmode;
    this.amode = false;
    this.hk = 0;
    this.msg = "";
    ans();
    return;
  }
  if (cl && a.startsWith("ty")) {   // the Loadout view: the Abilities well (the focus view) and the Lattice (0.3.13 - unchanged)
    int clv = this.probe ? @PKG@.TreeV3.PROBE_LVL : @PKG@.TreeClass.level(u, tv);
    if (a.equals("tyfb")) { this.msg = abilEv(u, d, tv, clv, "back", 0); ans(); return; }
    if (a.equals("tyfc")) { this.msg = abilEv(u, d, tv, clv, "holdab", 0); ans(); return; }
    if (a.equals("tymx")) { this.msg = abilEv(u, d, tv, clv, "maxup", 0); ans(); return; }
    if (a.equals("tymat")) { this.msg = abilEv(u, d, tv, clv, "attune", 0); ans(); return; }
    if (a.startsWith("tyca")) { int i = num(a, 4); if (i >= 0 && i < 4) { this.msg = abilEv(u, d, tv, clv, "focus", i); ans(); } return; }
    if (a.startsWith("tyla")) { int i = num(a, 4); if (i >= 0 && i < 4) { this.msg = abilEv(u, d, tv, clv, "slot", i); ans(); } return; }
    if (a.startsWith("tylm")) { int i = num(a, 4); if (i >= 0 && i < 16) { this.msg = abilEv(u, d, tv, clv, "mslot", i); ans(); } return; }
    if (a.startsWith("tyft")) { int i = num(a, 4); if (i >= 0 && i < 5) { this.msg = abilEv(u, d, tv, clv, "tile", i); ans(); } return; }
    return;
  }
  if (a.equals("trbuy")) {
    int L = curLayout(u);
    int[] c = L < 0 ? new int[0] : @PKG@.TreeMap.nodes(L);
    int k = this.msel;
    if (this.mselL != L) { k = -1; this.msel = -1; }   // picked on another layout (the class / profile changed): never buy what was not shown
    if (k < 0 || k >= c.length) this.msg = "Click a talent on the map first";
    else if (c[k] < 0) this.msg = @PKG@.TreeV3.RFNAME[-c[k] - 1] + " is free - it comes with its row (no point)";
    else this.msg = @PKG@.TreeV3.buy(u, d, @PKG@.TreeMap.nodeTv(c[k]), c[k], this.probe && cl);
    ans();
    return;
  }
  if (a.equals("trrespec")) {
    long now = System.currentTimeMillis();
    boolean pb = this.probe && cl;
    if (tv < 0 || d == null || d.bad || !@PKG@.TreeV3.anySpent(d, tv)) { this.armT = -1; this.msg = @PKG@.TreeV3.respec(u, d, tv, pb); ans(); return; }
    int lv = pb ? @PKG@.TreeV3.PROBE_LVL : @PKG@.TreeV3.points(u, tv);
    long pnow = pb ? 0L : @PKG@.TreeV3.price(d, tv, lv);
    boolean armedNow = this.armT == t && now - this.armAt <= 10000L;
    if (armedNow && pnow == this.armPrice) {
      this.armT = -1;
      this.msg = @PKG@.TreeV3.respec(u, d, tv, pb);
    } else {   // the first click, or the price changed since the first click: arm again with the price that will be charged
      this.armT = t;
      this.armAt = now;
      this.armPrice = pnow;
      this.msg = "Click Respec again within 10 s to reset your whole " + @PKG@.TreeV3.TNAME[tv] + " tree - every point comes back - " + (pb ? "free in the probe" : (pnow > 0L ? "it costs " + @PKG@.TreeDefs.grp(pnow) + " coins" : "free (your free respec of this run)")) + (armedNow ? " (the price changed since your first click)" : "");
    }
    ans();
    return;
  }
}""")
M(page, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  this.answered = false;
  try {
    handleIn(ref, st, data);
  } catch (Throwable e) {
    @PKG@.TreeCfg.warn("tree page event failed: " + e);
  } finally {
    if (!this.answered && stillOpen(ref, st)) {   // nothing was sent (unknown data, an error, a command that opened nothing): the empty answer
      this.answered = true;
      this.nets = this.nets + 1;
      this.answers = this.answers + 1;
      try { this.sendUpdate(); } catch (Throwable t2) { @PKG@.TreeCfg.warn("tree page: the empty answer failed: " + t2); }
    }
  }
}""")

'''
P.rep(OLD_EV, NEW_EV)

# ---------- the classes written + the jar assets
P.rep('''       tcur, migP7,   # 0.4.9: + TreeCurve (the coin curve) + the Balance P7 respec update''',
      '''       tcur, migP7,   # 0.4.9: + TreeCurve (the coin curve) + the Balance P7 respec update
       tmap,          # 0.5.0: + TreeMap (the radial map pages: tables, page data reader, node pictures + lit lines)''')
P.rep('''assert not set(_kit) & set(SWING_FILES), "0.3.15: a kit file clashes with a file of this jar"
B.assemble(jar, m, OUT, dict(SWING_FILES, **_kit))''', '''assert not set(_kit) & set(SWING_FILES), "0.3.15: a kit file clashes with a file of this jar"
assert not set(TM_ASSETS) & (set(SWING_FILES) | set(_kit)), "0.5.0: a map file clashes with a file of this jar"
assert all(p_.startswith(TM_JAR + TM_DIR) or p_.startswith(TM_RES) for p_ in TM_ASSETS), "0.5.0: map pictures under Common/UI/Custom/SkyyTrees/Map/"
B.assemble(jar, m, OUT, dict(dict(SWING_FILES, **_kit), **TM_ASSETS))   # 0.5.0: + the map pictures and page data
with zipfile.ZipFile(jar) as _tz:
    assert all(_tz.read(p_) == b_ for p_, b_ in TM_ASSETS.items()), "0.5.0: the map files in the jar"
    assert not [n_ for n_ in _tz.namelist() if n_.lower().endswith(".ui")], "0.5.0: inline pages only"''')
P.rep('''hub tab " + hubTab + "; class tab page " + clsTab + "; " + sum''',
      '''hub tab " + hubTab + "; class tab page " + clsTab + "; tree pages: radial maps (" + @PKG@.TreeMap.NL + " layouts x " + @PKG@.TreeMap.ZN + " zooms); " + sum''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0 and P.s.count("makeClass(") == CLS0 + 1
_k = P.s.index
assert _k("tmap = pool.makeClass(") < _k("M(page, TM_BUILD_JAVA)") < _k("public void handleDataEvent(")
assert _k("public void ans()") < _k("public void nexus(") < _k("public void handleIn(") < _k("public void handleDataEvent(")
P.finish()
