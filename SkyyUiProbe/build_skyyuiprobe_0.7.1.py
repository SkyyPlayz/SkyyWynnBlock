"""SkyyUiProbe 0.7.1 - build script (javassist via jpype). A small, OP-ONLY dev / test mod: round R0 of research/Radial-Trees-Spec.md
(section 1.7) - the RADIAL TREE MAP probe, cases M1-M7. Nothing a player can use, no saved data, no config, no items.

Run:   python SkyyUiProbe/build_skyyuiprobe_0.7.1.py    -> SkyyUiProbe/SkyyUiProbe-0.7.1.jar (no --deploy on purpose)
       --dump-only : build the layout, pictures and page data and stop before the JVM (prints the counts)
       --assets-out <dir under tools/dev/scratch/> : also write every jar asset + dump.json there (previews, the harness)
Check: python SkyyUiProbe/test_skyyuiprobe_0.7.1.py   (A verify -Xverify:all, X exec every case through the real PageManager,
       ANSWER every bound event of every case = exactly one page packet, AA engine-access audit)

0.7.1 (Skyy's test 2026-10-22: "clicking buttons in it bugged it" - after ONE node click on M1 and the 'Focus' stub the client showed
"Loading..." over the page until Esc): 0.7's node clicks (all cases but M5), the stub buttons (Whole page / Focus / Learn), the M2
squares, the M6 tooltip discs, an unknown case and unknown data only logged + chatted and NEVER sent a page update, so the client
waited for the server's answer forever. Now EVERY click answers with exactly one page packet (the SkyyExploration 0.2.3 answer()
pattern): a node click sets the right panel's caption + talent name to the clicked node (one short update, nothing redraws), the
stubs / squares / discs / unknown data set the caption to what happened, a case switch = its rebuild, Close = the close, Next state
and the M5 halo move as 0.7; a safety net in handleDataEvent sends an EMPTY update (CustomUIPage.sendUpdate() = no commands - the
engine's own no-op answer) when a path sent nothing (e.g. a thrown error). Only Rebuild 10x sends 10 packets (the load test, as 0.7).
Everything else is 0.7's (same layout, art, markup, bindings, log lines).

WHY A FRESH 0.7 (not a patch of build_skyyuiprobe_0.6.py): 0.6 is a 330 KB script pinned to kit 1.4 (it asserts KIT_VERSION == "1.4";
the kit is 1.5 today), its kit / minimap / window / hub-panel probes were for older questions, and SkyyUiProbe was retired on 2026-10-10
(Skyy: "clear all the probes we dont need so they arnt cluttering the pack."). The radial map probe needs none of that code, so 0.7 is a
new minimal jar under the same mod name (package com.skyy.uiprobe, same /skyprobe command, alias /uiprobe). The 0.5 / 0.6 probe
pages (kit k1c-k1h, t1, h1, hubpanel) are GONE from this jar - SkyyUiProbeB 0.5 (their cross-jar partner) should be RETIRED with it.

Skyy's words (docs/answered/ui.md 2026-10-22): "id like to do our trees like this" (the Hylterium radial skill-tree map) + popups
"Grouped pages (Recommended)", "Focus view (Recommended)", "One arm per skill (Recommended)", "Show greyed (Recommended)",
"Pips in the ring (Recommended)".

THE CASES (each a page of its own; /skyprobe help lists them; the nav row on every page switches case in place - a rebuild, never a
close + open):
  M1  map-count       the Gathering map at full size: grey base line picture + ALL 120 gold edge pictures + 143 nodes (disc, icon, hit box)
                      + 4 hubs + emblem + 4 banners + halo + left rail + right panel (688 elements: the real worst case of this layout -
                      70 spokes touch their junction and need no line, so 120 gold edge pictures, not the spec's 165); clicks print one chat line per
                      node; "Rebuild 10x" rebuilds the page 10 times in a row (build ms + markup bytes logged each time)
  M1b map-count-1200  M1 + dummy nodes in the right panel up to ~1,200 elements
  M1c map-count-1600  M1 + dummy nodes up to ~1,600 elements
  M2  map-order       the real-looking map (a mid-progress fixture player: a few gold edges) - lines under discs, clicks on nodes over
                      lines; two controls in the panel: a button UNDER a transparent picture and one OVER it (do pictures eat clicks?)
  M3  map-crisp       the same map: are the @2x dotted diagonals crisp, any seam where a gold edge sits on the grey base line?
  M4  map-assetimage  three state discs in the panel: AssetImage with the @2x file's asset path, AssetImage with a 1x copy's path, and
                      the proven Group Background control; "Next state" sends ONLY b.set(#Id.AssetPath) + a Text via sendUpdate
  M5  map-anchor      click any node: the cyan halo moves there with ONE b.setObject(#SkyyPrSel.Anchor) via sendUpdate (+ the panel
                      name / rank texts) - nothing else redraws
  M6  map-tooltip     three node discs in the panel with TooltipText (kit trial key "tooltip"): hover = name + rank; Esc with a tooltip
                      open must be safe
  M7  map-scroll      (optional, learn only) the map drawn at 2x (1680 x 1548) inside an 840 x 774 TopScrolling holding a
                      LeftScrolling - does the wheel / scrollbar pan both ways?
Every case logs + chats one line per result: "PASS", "FAIL" or "Skyy: look" (what to look at and what to report).

ART (all generated HERE at build time, pure Python, our own geometry - no vanilla pixels; written into the jar only, never committed):
  Common/UI/Custom/SkyyUiProbe/Map/Base@2x.png        one 1680 x 1548 picture: every edge as grey dotted line + junction diamonds
  Common/UI/Custom/SkyyUiProbe/Map/Edge/E<k>@2x.png   one gold dotted picture per edge (its box + 4 px), same dot phase as the base
  Common/UI/Custom/SkyyUiProbe/Map/Node/<Tree><State>@2x.png  disc / diamond / capstone state pictures (pips in the ring)
  .../Map/Hub<Tree>@2x.png, Emblem@2x.png, Halo@2x.png, Dummy@2x.png; .../Map/Asset/S<n>@2x.png + S<n>.png (M4)
The layout = the spec's radial_layout() (section 2.5) copied here (tools/skyymap.py is round R1's file and does not exist yet) on the
REAL Gathering data of tools/trees_v3_data.py (read only), with the spec's checks (in canvas, disc gaps >= 6 px, hit squares apart,
every node placed once, banners clear).
Page data: every case's markup is a text resource in the jar (com/skyy/uiprobe/pages/<case>.txt: A parent / markup, S b.set text,
E binding lines) read once by ProbeData - a 1,600-element page would not fit javassist's method / constant limits as Java literals.
"""
import sys, os, re, json, math, zlib, struct, zipfile, hashlib, time
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyyui as SUI
import serverjar
import trees_v3_data as TD

if "--deploy" in sys.argv:
    raise SystemExit("SkyyUiProbe: --deploy is not supported - tools/deploy_set.py is the only deploy path")
VERSION = "0.7.1"
PKG = "com.skyy.uiprobe"
P = "SkyyPr"                              # every element id starts with this (no underscores)
NODE_PERM = "skyyuiprobe.admin"
TEX_ROOT = "Common/UI/Custom/"
MAP_DIR = "SkyyUiProbe/Map/"               # markup paths are written WITHOUT @2x (the client loads the @2x file)
ASSET_NAME_ROOT = "UI/Custom/"             # an AssetImage AssetPath = the common asset name (the jar path without "Common/")
RES_DIR = "com/skyy/uiprobe/pages/"        # page data resources (next to the classes; never an asset)
T0 = time.time()

# ================================================================= colours (data colours for the map art; lint: UI_DATA_COLORS)
TREE_COLOR = {"Mining": "#8fc8ff", "Foraging": "#8fe08a", "Farming": "#f0d060", "Fishing": "#6fb7e8"}   # spec 2.3 (Q5 default)
ART_COLORS = {"disc": "#101822", "ringLocked": "#4a535c", "lock": "#8a939c", "gold": "#E8A93B", "pipLit": "#ffd36b",
              "pipDim": "#2a323a", "line": "#797b7c", "halo": "#6fe3ff", "emblemFill": "#14284a", "white": "#f4f8ff"}
UI_DATA_COLORS = list(TREE_COLOR.values()) + list(ART_COLORS.values())
GATHERING = ("Mining", "Foraging", "Farming", "Fishing")        # clockwise: sector centres 45 / 135 / 225 / 315 (spec 2.3)
MOTTO = {"Mining": "dig - smelt - prosper", "Foraging": "fell - gather - replant", "Farming": "sow - tend - harvest",
         "Fishing": "cast - reel - land"}
ICONS = {"Mining": ["Tool_Pickaxe_Iron", "Ore_Copper", "Ore_Cobalt"], "Foraging": ["Tool_Hatchet_Iron", "Tool_Hatchet_Copper", "Tool_Hatchet_Crude"],
         "Farming": ["Tool_Hoe_Iron", "Plant_Crop_Wheat_Item", "Plant_Seeds_Wheat"], "Fishing": ["Fish_Bluegill_Item", "Fish_Catfish_Item"]}
HUB_ICON = {"Mining": "Tool_Pickaxe_Iron", "Foraging": "Tool_Hatchet_Iron", "Farming": "Tool_Hoe_Iron", "Fishing": "Fish_Bluegill_Item"}
FIXTURE = {"Mining": 19, "Foraging": 8, "Farming": 3, "Fishing": 0}  # the mid-progress player of M2-M7 (points spent per tree)


def rgb(h):
    return (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16))


# ================================================================= 1. LAYOUT (spec 2.5 radial_layout, copied; R1 moves it to skyymap.py)
W, H = 840, 774                  # the map canvas (spec 2.1)
NODE, GAP, EMB, HUB = 32, 6, 96, 44
RING0, SPACING = 0.46, 40.0      # the prototype's numbers (spec 2.5: Gathering min gap 6.5 px)


def items_of(row):
    ups = [("up", u["id"]) for u in row["ups"]]
    fr = [("free", "free")] if row.get("free") else []
    h = len(ups) // 2
    return ups[:h] + fr + ups[h:]


def ring_f(ri, nrows, ring0):
    pos = ri if nrows == 6 else ri * 5.0 / 3.0
    return ring0 + (1.0 - ring0) * pos / 5.0


def relax(nodes, cx, cy, rounds=200):
    for _ in range(rounds):
        moved = False
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                p, q = nodes[i], nodes[j]
                if p["ay"] != q["ay"]:
                    continue
                want = (p["size"] + q["size"]) / 2.0 + GAP + 0.5
                d = math.hypot(p["x"] - q["x"], p["y"] - q["y"])
                if d < want:
                    da = (want - d) / math.hypot(p["ax"] * math.cos(p["a"]), p["ay"] * math.sin(p["a"])) / 2.0
                    if p["a"] > q["a"]:
                        da = -da
                    p["a"] -= da
                    q["a"] += da
                    for n in (p, q):
                        n["x"], n["y"] = cx + n["ax"] * math.sin(n["a"]), cy - n["ay"] * math.cos(n["a"])
                    moved = True
        if not moved:
            return


def radial_layout(groups, W=840, H=774, node=32, ring0=0.46, s=40.0, start=None, emb=96, hub=44, tree_gap=0.6, branch_gap=0.25):
    cx, cy = W / 2.0, H / 2.0
    axm, aym = cx - 8 - node / 2.0, cy - 8 - node / 2.0
    avg = math.sqrt((axm * axm + aym * aym) / 2.0)
    need = []
    for _, _, branches in groups:
        bn = []
        for b in branches:
            m = max(((len(items_of(r)) - 1) * s + node + GAP) / (avg * ring_f(i, len(b["rows"]), ring0)) for i, r in enumerate(b["rows"]))
            bn.append(m + branch_gap * s / (avg * ring0))
        need.append(bn)
    tg = tree_gap * s / (avg * ring0)
    scale = 2 * math.pi / (sum(sum(b) for b in need) + tg * len(groups))
    if start is None:
        start = {3: 0.0, 4: 45.0}.get(len(groups), 0.0)
    ang = math.radians(start) - (sum(need[0]) + tg) * scale / 2.0
    out = dict(nodes=[], hubs=[], edges=[], junctions=[])
    hub_r = emb / 2.0 + hub / 2.0 + 14
    for k, (key, col, branches) in enumerate(groups):
        span = (sum(need[k]) + tg) * scale
        tc = ang + span / 2.0
        out["hubs"].append(dict(key=key, x=cx + hub_r * math.sin(tc), y=cy - hub_r * math.cos(tc), a=tc, col=col))
        ab = ang + tg * scale / 2.0
        for bi, b in enumerate(branches):
            bc = ab + need[k][bi] * scale / 2.0
            prev = ("hub", key)
            for ri, row in enumerate(b["rows"]):
                f = ring_f(ri, len(b["rows"]), ring0)
                ax, ay = axm * f, aym * f
                its = items_of(row)
                da = s / math.hypot(ax * math.cos(bc), ay * math.sin(bc))
                junc = (key, bi, ri, "J")
                out["junctions"].append(dict(id=junc, x=cx + ax * math.sin(bc), y=cy - ay * math.cos(bc)))
                out["edges"].append((prev, junc, "spine", ri))
                for j, (kind, uid) in enumerate(its):
                    a = bc + (j - (len(its) - 1) / 2.0) * da
                    nid = (key, bi, ri, uid)
                    out["nodes"].append(dict(id=nid, kind=kind, a=a, ax=ax, ay=ay, col=col,
                                             size=node if kind == "up" else int(node * 0.7),
                                             x=cx + ax * math.sin(a), y=cy - ay * math.cos(a)))
                    if kind == "free":
                        out["junctions"][-1].update(x=out["nodes"][-1]["x"], y=out["nodes"][-1]["y"], node=nid)
                    else:
                        out["edges"].append((junc, nid, "spoke", ri))
                prev = junc
            ab += need[k][bi] * scale
        ang += span
    relax(out["nodes"], cx, cy)
    return out


TREES = dict((n, TD.tree(n)) for n in GATHERING)
LAY = radial_layout([(n, TREE_COLOR[n], TREES[n]["branches"]) for n in GATHERING], W=W, H=H, node=NODE, ring0=RING0, s=SPACING,
                    emb=EMB, hub=HUB)
NODES, HUBS, EDGES, JUNC = LAY["nodes"], LAY["hubs"], LAY["edges"], LAY["junctions"]
for n in NODES:                                                  # whole px (spec check 4)
    n["l"], n["t"] = int(round(n["x"] - n["size"] / 2.0)), int(round(n["y"] - n["size"] / 2.0))
    n["cx"], n["cy"] = n["l"] + n["size"] / 2.0, n["t"] + n["size"] / 2.0
for h in HUBS:
    h["l"], h["t"] = int(round(h["x"] - HUB / 2.0)), int(round(h["y"] - HUB / 2.0))
    h["cx"], h["cy"] = h["l"] + HUB / 2.0, h["t"] + HUB / 2.0
NODE_BY_ID = dict((n["id"], k) for k, n in enumerate(NODES))
for j in JUNC:                                                   # a junction with a node right on it (odd rows: the middle up) = that node
    if "node" not in j:
        for n in NODES:
            if n["id"][:3] == j["id"][:3] and math.hypot(n["x"] - j["x"], n["y"] - j["y"]) < 3:
                j["node"] = n["id"]
HUB_BY_KEY = dict((h["key"], h) for h in HUBS)
JUNC_BY_ID = dict((j["id"], j) for j in JUNC)
EMB_L, EMB_T = W // 2 - EMB // 2, H // 2 - EMB // 2


def hit_of(n):
    s = int(round(n["size"] * 26 / 32.0))
    return s, (n["size"] - s) // 2


# ---- the spec's check() (2.5): every node placed once, inside, gaps, hit squares, edges outward, banners clear
_want = sorted((t, bi, ri, uid) for t in GATHERING for bi, b in enumerate(TREES[t]["branches"]) for ri, r in enumerate(b["rows"])
               for _k, uid in items_of(r))
assert sorted(n["id"] for n in NODES) == _want and len(set(n["id"] for n in NODES)) == len(NODES), "every node placed exactly once"
for n in NODES:
    assert n["l"] >= 4 and n["t"] >= 4 and n["l"] + n["size"] <= W - 4 and n["t"] + n["size"] <= H - 4, "node outside: %s" % (n["id"],)
_min_gap = 1e9
for i in range(len(NODES)):
    for j in range(i + 1, len(NODES)):
        p, q = NODES[i], NODES[j]
        g = math.hypot(p["cx"] - q["cx"], p["cy"] - q["cy"]) - (p["size"] + q["size"]) / 2.0
        assert g >= GAP - 0.01, "discs %s / %s only %.2f px apart" % (p["id"], q["id"], g)
        _min_gap = min(_min_gap, g)
        sp, op = hit_of(p)
        sq, oq = hit_of(q)
        gx = max(q["l"] + oq - (p["l"] + op + sp), p["l"] + op - (q["l"] + oq + sq))
        gy = max(q["t"] + oq - (p["t"] + op + sp), p["t"] + op - (q["t"] + oq + sq))
        assert max(gx, gy) >= 2, "hit squares of %s / %s touch" % (p["id"], q["id"])
for n in NODES:
    for h in HUBS:
        assert math.hypot(n["cx"] - h["cx"], n["cy"] - h["cy"]) - (n["size"] + HUB) / 2.0 >= GAP, "node %s on a hub" % (n["id"],)
    assert math.hypot(n["cx"] - W / 2.0, n["cy"] - H / 2.0) - (n["size"] + EMB) / 2.0 >= GAP, "node %s on the emblem" % (n["id"],)
BANNER_W, BANNER_H = 200, 44
BANNER_AT = {"Mining": (W - 4 - BANNER_W, 4), "Foraging": (W - 4 - BANNER_W, H - 4 - BANNER_H), "Farming": (4, H - 4 - BANNER_H),
             "Fishing": (4, 4)}


def box_circle_gap(bx, by, bw, bh, cx, cy, r):
    dx = max(bx - cx, 0, cx - (bx + bw))
    dy = max(by - cy, 0, cy - (by + bh))
    return math.hypot(dx, dy) - r


for t, (bl, bt) in BANNER_AT.items():
    for n in NODES:
        assert box_circle_gap(bl, bt, BANNER_W, BANNER_H, n["cx"], n["cy"], n["size"] / 2.0) >= GAP, "banner %s on %s" % (t, n["id"])


def end_of(e):
    """an edge end -> (centre x, centre y, radius the dots stop short of)"""
    if e[0] == "hub":
        h = HUB_BY_KEY[e[1]]
        return h["cx"], h["cy"], HUB / 2.0 + 2
    if e[3] == "J":
        j = JUNC_BY_ID[e]
        if "node" in j:
            n = NODES[NODE_BY_ID[j["node"]]]
            return n["cx"], n["cy"], n["size"] / 2.0 + 1
        return j["x"], j["y"], 6.0
    n = NODES[NODE_BY_ID[e]]
    return n["cx"], n["cy"], n["size"] / 2.0 + 1


C0 = (W / 2.0, H / 2.0)
for a, b, kind, ri in EDGES:                      # check 5: the spine never jumps a row and points outward
    ax_, ay_, _r = end_of(a)
    bx_, by_, _r = end_of(b)
    if kind == "spine" and a[0] != "hub":
        assert a[:3] == (b[0], b[1], b[2] - 1), "spine %s -> %s jumps a row" % (a, b)
    assert math.hypot(bx_ - C0[0], by_ - C0[1]) >= math.hypot(ax_ - C0[0], ay_ - C0[1]) - 30, "edge %s -> %s points inward" % (a, b)
print("layout: Gathering %d nodes, %d hubs, %d edges, %d junctions, min disc gap %.2f px (>= %d), hit squares apart, banners clear"
      % (len(NODES), len(HUBS), len(EDGES), len(JUNC), _min_gap, GAP))


# ---- the fixture player (M2-M7): ranks + which edges are lit (the spec's gold rule 1.3)
def fixture_ranks():
    ranks = {}
    for t in GATHERING:
        left, spent = FIXTURE[t], 0
        rows = max(len(b["rows"]) for b in TREES[t]["branches"])
        for ri in range(rows):
            for bi, b in enumerate(TREES[t]["branches"]):
                if ri >= len(b["rows"]) or b["rows"][ri]["gate"] > spent:
                    continue
                for u in b["rows"][ri]["ups"]:
                    give = min(u["max"], 2, left)
                    if give > 0:
                        ranks[(t, bi, ri, u["id"])] = give
                        left -= give
                        spent += give
        assert left == 0, "fixture %s: %d points left over" % (t, left)
    return ranks


RANKS = fixture_ranks()
SPENT = dict((t, sum(v for k, v in RANKS.items() if k[0] == t)) for t in GATHERING)


def row_open(t, bi, ri):
    return TREES[t]["branches"][bi]["rows"][ri]["gate"] <= SPENT[t]


def edge_lit(e):
    a, b, kind, ri = e
    if kind == "spine":
        return a[0] == "hub" or row_open(b[0], b[1], b[2])
    return RANKS.get(b, 0) >= 1


def up_of(nid):
    t, bi, ri, uid = nid
    row = TREES[t]["branches"][bi]["rows"][ri]
    if uid == "free":
        return None, row
    return [u for u in row["ups"] if u["id"] == uid][0], row


def state_of(nid):
    """the node's picture name under Node/: Locked / Ready / <Tree>L<k><m> / <Tree>Max<m> / <Tree>Free / FreeLocked / Cap*"""
    t, bi, ri, uid = nid
    u, row = up_of(nid)
    opened = row_open(t, bi, ri)
    if u is None:
        return ("%sFree" % t) if opened else "FreeLocked"
    k = RANKS.get(nid, 0)
    if row.get("cap"):
        return ("%sCapMax" % t) if k >= u["max"] else ("CapReady" if opened else "CapLocked")
    if k >= u["max"]:
        return "%sMax%d" % (t, u["max"])
    if k >= 1:
        return "%sL%d%d" % (t, k, u["max"])
    return "Ready" if opened else "Locked"


LIT_FIX_ALL = [k for k, e in enumerate(EDGES) if edge_lit(e)]



# ================================================================= 2. PICTURES (own fast PNG: filter 0 + zlib 9, deterministic)
class Pic(object):
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.px = bytearray(w * h * 4)

    def blend(self, x, y, c, a):
        if a <= 0 or x < 0 or y < 0 or x >= self.w or y >= self.h:
            return
        a = min(a, 1.0)
        i = (y * self.w + x) * 4
        px = self.px
        da = px[i + 3] / 255.0
        oa = a + da * (1.0 - a)
        for ch in range(3):
            px[i + ch] = int(round((c[ch] * a + px[i + ch] * da * (1.0 - a)) / oa))
        px[i + 3] = int(round(oa * 255))


def png(pic):
    raw = b"".join(b"\x00" + bytes(pic.px[y * pic.w * 4:(y + 1) * pic.w * 4]) for y in range(pic.h))

    def chunk(typ, body):
        return struct.pack(">I", len(body)) + typ + body + struct.pack(">I", zlib.crc32(typ + body) & 0xffffffff)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", pic.w, pic.h, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def png_size(data):
    return struct.unpack(">II", data[16:24])


def disc(pic, cx, cy, r, c, a=1.0, x0=None, x1=None):
    """an anti-aliased filled circle (coverage = r + 0.5 - distance)"""
    for y in range(max(0, int(cy - r - 2)), min(pic.h, int(cy + r + 3))):
        for x in range(max(0, int(cx - r - 2)), min(pic.w, int(cx + r + 3))):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            cov = r + 0.5 - d
            if cov > 0:
                pic.blend(x, y, c, a * min(cov, 1.0))


def ring(pic, cx, cy, r0, r1, c, a=1.0):
    for y in range(max(0, int(cy - r1 - 2)), min(pic.h, int(cy + r1 + 3))):
        for x in range(max(0, int(cx - r1 - 2)), min(pic.w, int(cx + r1 + 3))):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            cov = min(r1 + 0.5 - d, d - r0 + 0.5, 1.0)
            if cov > 0:
                pic.blend(x, y, c, a * cov)


def poly(pic, pts, c, a=1.0, ss=4):
    """a filled polygon, ss x ss supersampled"""
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]

    def inside(x, y):
        n, ins = len(pts), False
        for i in range(n):
            (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % n]
            if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
                ins = not ins
        return ins
    for y in range(max(0, int(min(ys)) - 1), min(pic.h, int(max(ys)) + 2)):
        for x in range(max(0, int(min(xs)) - 1), min(pic.w, int(max(xs)) + 2)):
            hit = sum(1 for sy in range(ss) for sx in range(ss) if inside(x + (sx + 0.5) / ss, y + (sy + 0.5) / ss))
            if hit:
                pic.blend(x, y, c, a * hit / float(ss * ss))


def star(cx, cy, r, inner=0.45, n=5, rot=0.0):
    pts = []
    for i in range(2 * n):
        rr = r if i % 2 == 0 else r * inner
        a = rot + math.pi * i / n
        pts.append((cx + rr * math.sin(a), cy - rr * math.cos(a)))
    return pts


DISC_C, LOCK_RING, LOCK_C = rgb(ART_COLORS["disc"]), rgb(ART_COLORS["ringLocked"]), rgb(ART_COLORS["lock"])
GOLD, PIP_LIT, PIP_DIM = rgb(ART_COLORS["gold"]), rgb(ART_COLORS["pipLit"]), rgb(ART_COLORS["pipDim"])


def node_pic(size_px, state, col=None, kmax=(0, 0), cap=False):
    """a disc state picture, geometry in 64ths of size_px: locked / ready / learnt (k of m pips lit) / max (all lit + glow)"""
    k = size_px / 64.0
    pic = Pic(size_px, size_px)
    c = size_px / 2.0
    if state == "max":
        ring(pic, c, c, 28 * k, 31.5 * k, rgb(col), 0.35)
    disc(pic, c, c, 27 * k, DISC_C, 0.94)
    rc = {"locked": LOCK_RING, "ready": GOLD}.get(state, rgb(col) if col else LOCK_RING)
    ring(pic, c, c, 23 * k, 27.5 * k, rc, 1.0)
    if state == "ready":
        ring(pic, c, c, 20.5 * k, 22 * k, GOLD, 0.35)
    if state == "locked":                                          # padlock badge, bottom right
        disc(pic, 49 * k, 49 * k, 9 * k, DISC_C, 1.0)
        ring(pic, 49 * k, 45 * k, 2.6 * k, 4.6 * k, LOCK_C, 1.0)
        poly(pic, [(43.5 * k, 46 * k), (54.5 * k, 46 * k), (54.5 * k, 55 * k), (43.5 * k, 55 * k)], LOCK_C, 1.0, ss=2)
    m, lit = kmax
    if m:                                                          # rank pips along the bottom of the ring
        for i in range(m):
            a = math.radians(180 + (i - (m - 1) / 2.0) * 21)
            px_, py_ = c + 25.2 * k * math.sin(a), c - 25.2 * k * math.cos(a)
            disc(pic, px_, py_, 3.9 * k, DISC_C, 1.0)
            disc(pic, px_, py_, 2.8 * k, PIP_LIT if i < lit else PIP_DIM, 1.0)
    if cap:                                                        # capstone star badge on the top of the ring
        sc = GOLD if state in ("ready", "max") else LOCK_C
        poly(pic, star(c, 9 * k, 8.5 * k), DISC_C, 1.0, ss=3)
        poly(pic, star(c, 9 * k, 6.5 * k), sc, 1.0, ss=3)
    return pic


def diamond_pic(size_px, col, opened):
    k = size_px / 44.0
    pic = Pic(size_px, size_px)
    c = size_px / 2.0
    cc = rgb(col) if opened else LOCK_RING
    poly(pic, [(c, c - 20 * k), (c + 20 * k, c), (c, c + 20 * k), (c - 20 * k, c)], cc, 1.0, ss=3)
    poly(pic, [(c, c - 15 * k), (c + 15 * k, c), (c, c + 15 * k), (c - 15 * k, c)], DISC_C, 0.96, ss=3)
    poly(pic, [(c, c - 7 * k), (c + 7 * k, c), (c, c + 7 * k), (c - 7 * k, c)], cc, 0.9 if opened else 0.6, ss=3)
    return pic


def hub_pic(col):
    pic = Pic(88, 88)
    disc(pic, 44, 44, 42, DISC_C, 0.96)
    ring(pic, 44, 44, 35, 42.5, rgb(col), 1.0)
    ring(pic, 44, 44, 31, 32.5, rgb(col), 0.5)
    return pic


def halo_pic():
    pic = Pic(88, 88)
    ring(pic, 44, 44, 36, 43, rgb(ART_COLORS["halo"]), 0.45)
    ring(pic, 44, 44, 38, 41, rgb(ART_COLORS["halo"]), 1.0)
    return pic


def emblem_pic():
    pic = Pic(192, 192)
    disc(pic, 96, 96, 92, rgb(ART_COLORS["emblemFill"]), 1.0)
    ring(pic, 96, 96, 80, 92, GOLD, 1.0)
    ring(pic, 96, 96, 72, 75, GOLD, 0.6)
    poly(pic, star(96, 96, 60, inner=0.32, n=4), GOLD, 1.0, ss=3)
    poly(pic, star(96, 96, 40, inner=0.32, n=4, rot=math.pi / 4), rgb(ART_COLORS["white"]), 0.85, ss=3)
    disc(pic, 96, 96, 11, rgb(ART_COLORS["emblemFill"]), 1.0)
    return pic


ASSETS = {}            # jar path -> bytes
TEXPATH = {}           # picture name -> markup path (no @2x)


def ship(name, pic, sub=""):
    data = png(pic)
    w, h = png_size(data)
    assert w % 2 == 0 and h % 2 == 0, name
    jp = TEX_ROOT + MAP_DIR + sub + name + "@2x.png"
    assert "_" not in name and jp not in ASSETS, name
    ASSETS[jp] = data
    TEXPATH[sub + name] = MAP_DIR + sub + name + ".png"
    return TEXPATH[sub + name]


# node state pictures (64 px = 32 UI; diamonds 44 px = 22 UI)
MAXES = sorted(set(u["max"] for t in GATHERING for b in TREES[t]["branches"] for r in b["rows"] for u in r["ups"]))
ship("Locked", node_pic(64, "locked"), "Node/")
ship("Ready", node_pic(64, "ready"), "Node/")
ship("CapLocked", node_pic(64, "locked", cap=True), "Node/")
ship("CapReady", node_pic(64, "ready", cap=True), "Node/")
ship("FreeLocked", diamond_pic(44, "#000000", False), "Node/")   # ui-data (the colour is unused when locked)
for t in GATHERING:
    for m in MAXES:
        for kk in range(1, m):
            ship("%sL%d%d" % (t, kk, m), node_pic(64, "learnt", TREE_COLOR[t], (m, kk)), "Node/")
        ship("%sMax%d" % (t, m), node_pic(64, "max", TREE_COLOR[t], (m, m)), "Node/")
    ship("%sCapMax" % t, node_pic(64, "max", TREE_COLOR[t], (1, 1), cap=True), "Node/")
    ship("%sFree" % t, diamond_pic(44, TREE_COLOR[t], True), "Node/")
    ship("Hub%s" % t, hub_pic(TREE_COLOR[t]))
ship("Halo", halo_pic())
ship("Emblem", emblem_pic())
ship("Dummy", node_pic(28, "locked"))
# M4: five Mining states at 64 UI (128 px @2x) + a 1x copy of each (64 px) under the same name without @2x
M4_STATES = [("locked", (0, 0), "Locked"), ("ready", (0, 0), "Ready - can learn now"), ("learnt", (3, 1), "Learnt 1 / 3"),
             ("learnt", (3, 2), "Learnt 2 / 3"), ("max", (3, 3), "Max rank 3 / 3")]
for i, (st, km, _cap) in enumerate(M4_STATES):
    ship("S%d" % i, node_pic(128, st, TREE_COLOR["Mining"], km), "Asset/")
    ASSETS[TEX_ROOT + MAP_DIR + "Asset/S%d.png" % i] = png(node_pic(64, st, TREE_COLOR["Mining"], km))
M4_PATH_2X = [ASSET_NAME_ROOT + MAP_DIR + "Asset/S%d@2x.png" % i for i in range(len(M4_STATES))]
M4_PATH_1X = [ASSET_NAME_ROOT + MAP_DIR + "Asset/S%d.png" % i for i in range(len(M4_STATES))]
for p_ in M4_PATH_2X + M4_PATH_1X:
    assert "Common/" + p_ in ASSETS, p_
for n in NODES:
    assert ("Node/" + state_of(n["id"])) in TEXPATH, state_of(n["id"])
assert node_pic(64, "learnt", TREE_COLOR["Mining"], (5, 2)).px == node_pic(64, "learnt", TREE_COLOR["Mining"], (5, 2)).px, "deterministic"


# ---- the base picture (every edge grey) + one gold picture per edge (same dots, same phase)
DOT_STEP, DOT_R_BASE, DOT_R_GOLD = 8.0, 1.5, 1.9     # @2x px (spec 2.6: a dot every 8 px at @2x)
LINE_C = rgb(ART_COLORS["line"])


def edge_dots(e):
    """the dot centres of one edge in canvas UI px (trimmed short of both ends), the same list for the base and the gold picture"""
    (ax_, ay_, ra), (bx_, by_, rb) = end_of(e[0]), end_of(e[1])
    L = math.hypot(bx_ - ax_, by_ - ay_)
    if L < 1e-6:
        return []
    ux, uy = (bx_ - ax_) / L, (by_ - ay_) / L
    pts, s = [], ra + 2.0
    while s <= L - rb - 2.0 + 1e-9:
        pts.append((ax_ + ux * s, ay_ + uy * s))
        s += DOT_STEP / 2.0
    return pts


EDGE_DOTS = [edge_dots(e) for e in EDGES]
# a spoke into a node that sits on (or touches) its junction has no line to draw: no picture, no element (the disc touches the spine)
DRAWN = [k for k, d in enumerate(EDGE_DOTS) if d]
assert all(EDGES[k][2] == "spoke" for k in range(len(EDGES)) if k not in DRAWN), "every spine edge shows dots"
base = Pic(2 * W, 2 * H)
for dots in EDGE_DOTS:
    for x, y in dots:
        disc(base, 2 * x, 2 * y, DOT_R_BASE, LINE_C, 0.6)
for j in JUNC:                                       # the 10 px junction diamonds where no node sits on the junction
    if "node" not in j:
        x, y = 2 * j["x"], 2 * j["y"]
        poly(base, [(x, y - 10), (x + 10, y), (x, y + 10), (x - 10, y)], LINE_C, 0.75, ss=3)
ship("Base", base)
EDGE_BOX = {}
for k in DRAWN:
    dots = EDGE_DOTS[k]
    xs, ys = [d[0] for d in dots], [d[1] for d in dots]
    l, t = int(math.floor(min(xs))) - 4, int(math.floor(min(ys))) - 4
    r, b = int(math.ceil(max(xs))) + 4, int(math.ceil(max(ys))) + 4
    l, t, r, b = max(0, l), max(0, t), min(W, r), min(H, b)
    g = Pic(2 * (r - l), 2 * (b - t))
    for x, y in dots:
        disc(g, 2 * (x - l), 2 * (y - t), DOT_R_GOLD, GOLD, 1.0)
    ship("E%d" % k, g, "Edge/")
    EDGE_BOX[k] = (l, t, r - l, b - t)
LIT_FIX = [k for k in LIT_FIX_ALL if k in EDGE_BOX]
print("fixture player: spent %s -> %d of %d drawn edges lit (%d edges in all; %d touching spokes need no line)" % (
    SPENT, len(LIT_FIX), len(DRAWN), len(EDGES), len(EDGES) - len(DRAWN)))
print("pictures: %d files, %d KB (base %d KB, %d gold edges), %.1f s" % (
    len(ASSETS), sum(len(v) for v in ASSETS.values()) // 1024, len(ASSETS[TEX_ROOT + MAP_DIR + "Base@2x.png"]) // 1024,
    len(EDGE_BOX), time.time() - T0))


# ================================================================= 3. THE PAGES (markup data; kit 1.5 blocks + raw map elements)
SUI.verify(assets_zip=serverjar.assets_zip(), quiet=True)
with zipfile.ZipFile(serverjar.assets_zip()) as _az:
    _vanilla_items = set(n.rsplit("/", 1)[-1][:-5] for n in _az.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    assert not any(n.startswith(TEX_ROOT + "SkyyUiProbe/") for n in _az.namelist()), "our texture folder exists in Assets.zip"
for _ids in list(ICONS.values()) + [list(HUB_ICON.values())]:
    for _i in _ids:
        assert _i in _vanilla_items, "node icon %s is not a vanilla item" % _i

CASES = [  # key, name, title line, what to see (one line each; the page shows them, the chat repeats WHAT)
    ("m1", "map-count", "PROBE M1 - map-count: the Gathering map at full size, every line lit gold",
     "Skyy: look - did it open in about 1 second, no disconnect? Click 10 nodes fast (10 chat lines), then Rebuild 10x (still connected?)."),
    ("m1b", "map-count-1200", "PROBE M1b - map-count: the same map plus dummy nodes, about 1,200 elements",
     "Skyy: look - did it open in about 1 second, no disconnect? Click a few nodes, then Rebuild 10x."),
    ("m1c", "map-count-1600", "PROBE M1c - map-count: the same map plus dummy nodes, about 1,600 elements",
     "Skyy: look - did it open in about 1 second, no disconnect? Click a few nodes, then Rebuild 10x."),
    ("m2", "map-order", "PROBE M2 - map-order: grey lines under gold lines under the node discs",
     "Skyy: look - lines run UNDER the discs? Click 3 nodes that sit on a line (3 chat lines). Click a bare line: nothing. Click both squares at the right."),
    ("m3", "map-crisp", "PROBE M3 - map-crisp: the dotted lines at 2x",
     "Skyy: look - are the diagonal dotted lines crisp at your resolution? Any gap or double dots where a gold line sits on the grey one? Send a screenshot."),
    ("m4", "map-assetimage", "PROBE M4 - map-assetimage: swap a disc picture without a rebuild",
     "Skyy: look - press Next state 5 times: which of the 3 discs at the right change picture each time? Any empty disc?"),
    ("m5", "map-anchor", "PROBE M5 - map-anchor: move the cyan halo with one Anchor update",
     "Skyy: look - click 5 nodes: does the cyan ring jump to each one, with nothing else flickering?"),
    ("m6", "map-tooltip", "PROBE M6 - map-tooltip: hover text on 3 node discs",
     "Skyy: look - hover the 3 discs at the right: does a tooltip show the name and rank? Then press Esc while a tooltip shows."),
    ("m7", "map-scroll", "PROBE M7 - map-scroll (optional): the map at double size in a 2-way scroll box",
     "Skyy: look - can you scroll the map up / down AND left / right (mouse wheel, scrollbars)? Nodes still clickable?"),
]
CASE_KEYS = [c[0] for c in CASES]
CASE_NAME = dict((c[0], c[1]) for c in CASES)
PAGE_W, PAGE_H = 1600, 980
RAIL_W, CV_W, PANEL_W, MAIN_H = 232, W, 456, H


def raw_group(ident, l, t, w, h, tex=None, extra=""):
    bg = (' Background: "%s";' % tex) if tex else ""
    return "Group #%s { Anchor: (Left: %d, Top: %d, Width: %d, Height: %d);%s%s }" % (ident, l, t, w, h, bg, extra)


def hit_button(ident, l, t, s, tip=None):
    tt = (" " + SUI.tooltip(tip, trial=True)) if tip else ""
    return ("Button #%s { Anchor: (Left: %d, Top: %d, Width: %d, Height: %d); Style: ButtonStyle(Hovered: (Background: %s));%s }"
            % (ident, l, t, s, s, SUI.COLOR["hover"], tt))


def tree_label(t):
    return t.upper()


def node_label(nid):
    t, bi, ri, uid = nid
    u, row = up_of(nid)
    b = TREES[t]["branches"][bi]
    nm = row["free"]["name"] if u is None else u["name"]
    rank = "free perk" if u is None else "Rank %d / %d" % (RANKS.get(nid, 0), u["max"])
    return "%s - %s - Row %d - %s (%s)" % (t, b["name"], ri + 1, nm, rank)


def add_node(ap, parent, k, n, state_name, scale=1, tip=None):
    """one map node = 3 elements: the state picture (Group Background), the icon, the transparent hit box (on top)"""
    t, bi, ri, uid = n["id"]
    s = n["size"] * scale
    ap.append((parent, raw_group(P + "N%d" % k, n["l"] * scale, n["t"] * scale, s, s, TEXPATH["Node/" + state_name])))
    hs, ho = hit_of(n)
    if n["kind"] == "up":
        ic = 18 * scale
        ap.append(("#" + P + "N%d" % k, SUI.item_icon(P + "N%dI" % k, ICONS[t][bi % len(ICONS[t])], size=ic,
                                                       anchor={"left": (s - ic) // 2, "top": (s - ic) // 2})))
    ap.append(("#" + P + "N%d" % k, hit_button(P + "N%dB" % k, ho * scale, ho * scale, hs * scale, tip)))


def canvas(ap, parent, lit, scale=1, halo_k=None, base_id="Base"):
    """the map: base picture, gold edges (lit), emblem, hubs, banners, halo, nodes - in that (draw) order"""
    sw, sh = W * scale, H * scale
    ap.append((parent, raw_group(P + base_id, 0, 0, sw, sh, TEXPATH["Base"])))
    if scale == 1:
        for k in lit:
            l, t, w_, h_ = EDGE_BOX[k]
            ap.append((parent, raw_group(P + "E%d" % k, l, t, w_, h_, TEXPATH["Edge/E%d" % k])))
    ap.append((parent, raw_group(P + "Emb", EMB_L * scale, EMB_T * scale, EMB * scale, EMB * scale, TEXPATH["Emblem"])))
    for i, h in enumerate(HUBS):
        ap.append((parent, raw_group(P + "H%d" % i, h["l"] * scale, h["t"] * scale, HUB * scale, HUB * scale, TEXPATH["Hub" + h["key"]])))
        ap.append(("#" + P + "H%d" % i, SUI.item_icon(P + "H%dI" % i, HUB_ICON[h["key"]], size=26 * scale,
                                                       anchor={"left": 9 * scale, "top": 9 * scale})))
    if scale == 1:
        for i, t in enumerate(GATHERING):
            bl, bt = BANNER_AT[t]
            al = "End" if bl > W // 2 else "Start"
            ap.append((parent, SUI.label(P + "Bn%dA" % i, tree_label(t), "default", size=15, bold=True, col=TREE_COLOR[t], w=BANNER_W,
                                         h=22, align=al, anchor={"left": bl, "top": bt})))
            ap.append((parent, SUI.label(P + "Bn%dB" % i, MOTTO[t], "caption", size=12, w=BANNER_W, h=20, align=al,
                                         anchor={"left": bl, "top": bt + 22})))
    if halo_k is not None:                                         # the halo sits UNDER the nodes (a ring wider than the disc)
        n = NODES[halo_k]
        hs_ = 44 * scale
        ap.append((parent, raw_group(P + "Sel", int(n["cx"] * scale - hs_ / 2.0), int(n["cy"] * scale - hs_ / 2.0), hs_, hs_,
                                     TEXPATH["Halo"])))
    for k, n in enumerate(NODES):
        add_node(ap, parent, k, n, state_of(n["id"]), scale)


def rail(ap, parent):
    """the left rail stub (spec 2.1): 5 page rows (28) + 13 tree rows (42) + the legend (4 x 21) = 770 of 774"""
    pages = [("Gathering", [("Mining", 23, 4), ("Foraging", 11, 3), ("Farming", 7, 4), ("Fishing", 3, 3)]),
             ("Crafting", [("Smithing", 5, 5), ("Cooking", 9, 2), ("Alchemy", 2, 2)]),
             ("Adventure", [("Combat", 14, 6), ("Acrobatics", 4, 4), ("Exploration", 6, 6), ("Beastmastery", 0, 0)]),
             ("Class", [("Warrior", 12, 1)]), ("Rebirth Nexus", [("Void", 0, 0)])]
    used, i = 0, 0
    for pi, (pg, trees) in enumerate(pages):
        rid = P + "Rp%d" % pi
        ap.append((parent, SUI.hover_row(rid, "selected" if pi == 0 else "normal", h=28, pad=0, w=RAIL_W)))
        ap.append(("#" + rid, SUI.label(P + "Rp%dL" % pi, pg, "section", h=28, w=RAIL_W - 8, anchor={"left": 8})))
        used += 28
        for t, lv, pts in trees:
            tid = P + "Rt%d" % i
            ap.append((parent, SUI.hover_row(tid, "selected" if t == "Mining" else "normal", h=42, pad=0, w=RAIL_W)))
            ap.append(("#" + tid, SUI.item_icon(P + "Rt%dI" % i, HUB_ICON.get(t, "Tool_Pickaxe_Iron"), size=24,
                                                anchor={"left": 10, "right": 8})))
            ap.append(("#" + tid, SUI.group(P + "Rt%dC" % i, layout="Top", w=RAIL_W - 50, h=42)))
            ap.append(("#" + P + "Rt%dC" % i, SUI.label(P + "Rt%dN" % i, t, "default", size=15, bold=True,
                                                        col=TREE_COLOR.get(t, "rowName"), h=22, w=RAIL_W - 50)))
            ap.append(("#" + P + "Rt%dC" % i, SUI.label(P + "Rt%dS" % i, "Lv %d - %d points" % (lv, pts), "rowSub", size=13, h=18,
                                                        w=RAIL_W - 50)))
            used += 42
            i += 1
    for li, (pic, cap) in enumerate((("Node/MiningL13", "learnt - ring in the tree colour"), ("Node/Ready", "ready - gold ring"),
                                     ("Node/Locked", "locked - grey with a padlock"), ("Halo", "selected - cyan halo"))):
        lid = P + "Lg%d" % li
        ap.append((parent, SUI.group(lid, layout="Left", w=RAIL_W, h=21)))
        ap.append(("#" + lid, 'Group #%s { Anchor: (Width: 20, Height: 20, Right: 6); Background: "%s"; }' % (P + "Lg%dP" % li, TEXPATH[pic])))
        ap.append(("#" + lid, SUI.label(P + "Lg%dT" % li, cap, "caption", size=13, h=20, w=RAIL_W - 26)))
        used += 21
    assert i == 13 and used <= MAIN_H, (i, used)
    return used


SEL0 = [k for k, n in enumerate(NODES) if RANKS.get(n["id"], 0) >= 1][0]      # the selected node of the stub panel (first learnt)


def panel(ap, parent, case, extra_h=0):
    """the right panel stub (spec 2.1): tree head + Whole page / Focus + the talent detail; returns the height left for the case block"""
    n = NODES[SEL0]
    t, bi, ri, uid = n["id"]
    u, row = up_of(n["id"])
    br = TREES[t]["branches"][bi]
    inner = PANEL_W - 2 * 8
    hd = P + "Ph"
    used = 0
    ap.append((parent, SUI.group(hd, layout="Left", w=inner, h=64)))
    ap.append(("#" + hd, SUI.item_icon(P + "PhI", HUB_ICON[t], size=40, anchor={"top": 12, "right": 10})))
    ap.append(("#" + hd, SUI.group(P + "PhC", layout="Top", w=inner - 50, h=64)))
    ap.append(("#" + P + "PhC", SUI.label(P + "PhN", tree_label(t), "heading", col=TREE_COLOR[t], h=30, w=inner - 50)))
    ap.text("#" + P + "PhC", P + "PhL", "Level 23 / 50  -  %d points spent" % SPENT[t], "default", size=15, h=24, w=inner - 50)
    used += 64
    ap.text(parent, P + "PhX", "XP 12,400 / 20,000 to level 24", "gold", size=15, h=22, w=inner)
    ap.append((parent, SUI.label(P + "PhP", "4 points free - row 5 opens at 20", "default", size=15, h=22, w=inner)))
    ap.text(parent, P + "PhR", "Respec tree - 2,300 coins", "caption", size=13, h=22, w=inner)
    used += 66
    ap.append((parent, SUI.group(P + "Seg", layout="Left", w=inner, h=40)))
    ap.append(("#" + P + "Seg", SUI.button(P + "SegW", "Whole page", "tertiary", "small", w=inner // 2 - 3, selected=True,
                                           anchor={"right": 6})))
    ap.append(("#" + P + "Seg", SUI.button(P + "SegF", "Focus", "tertiary", "small", w=inner // 2 - 3)))
    used += 40
    ap.text(parent, P + "TCap", "%s - %s - Row %d" % (t, br["name"], ri + 1), "caption", size=13, h=22, w=inner)
    ap.text(parent, P + "TName", u["name"], "tipName", col=TREE_COLOR[t], h=28, w=inner)
    ap.text(parent, P + "TRank", "Rank %d / %d" % (RANKS.get(n["id"], 0), u["max"]), "gold", size=15, h=24, w=inner)
    ap.text(parent, P + "TText", u["text"], "default", size=15, h=22, w=inner)
    ap.append((parent, SUI.label(P + "TReqH", "Requirements", "section", h=24, w=inner)))
    ap.append((parent, SUI.label(P + "TReq", "Row %d is open - %d points in %s" % (ri + 1, SPENT[t], t), "success", size=14,
                                 bold=False, h=22, w=inner)))
    ap.append((parent, SUI.label(P + "TCostH", "Cost", "section", h=24, w=inner)))
    ap.append((parent, SUI.label(P + "TCost", "1 point", "gold", size=15, h=22, w=inner)))
    ap.append((parent, SUI.label(P + "TState", "Ready to unlock", "success", size=15, h=24, w=inner)))
    ap.append((parent, SUI.button(P + "TLearn", "Learn", "primary", "normal", w=inner)))
    used += 22 + 28 + 24 + 22 + 24 + 22 + 24 + 22 + 24 + SUI.BTN_H
    return MAIN_H - 2 * 8 - used


def page(case, dummies=0):
    key, name, head, what = [c for c in CASES if c[0] == case][0]
    sh = SUI.page_shell(P, PAGE_W, PAGE_H, "SkyyUiProbe %s - radial tree map probe" % VERSION, kind="decorated")
    ap, body, iw = sh.appends, sh.body, sh.inner_w
    ap.text(body, P + "Head", head, "strong", size=17, h=28, w=iw)
    ap.text(body, P + "What", what, "default", size=15, h=26, w=iw)
    ap.append((body, SUI.group(P + "Nav", layout="Left", w=iw, h=SUI.BTN_SMALL_H + 6)))
    for c in CASE_KEYS:
        ap.append(("#" + P + "Nav", SUI.button(P + "Go" + c.capitalize(), c.upper(), "tertiary", "small", w=72, selected=(c == case),
                                               anchor={"right": 6})))
    if case in ("m1", "m1b", "m1c"):
        ap.append(("#" + P + "Nav", SUI.button(P + "Rb", "Rebuild 10x", "secondary", "small", w=150, anchor={"left": 18, "right": 6})))
    ap.append(("#" + P + "Nav", SUI.button(P + "Close", "Close", "secondary", "small", w=120, sound="cancel", anchor={"left": 18})))
    ap.append((body, SUI.spacer(h=8)))
    ap.append((body, SUI.group(P + "Main", layout="Left", w=RAIL_W + 12 + CV_W + 12 + PANEL_W, h=MAIN_H)))
    used_h = 28 + 26 + SUI.BTN_SMALL_H + 6 + 8 + MAIN_H
    SUI.fit([used_h], sh.inner_h, "probe page body")
    ap.append(("#" + P + "Main", SUI.group(P + "Rail", layout="Top", w=RAIL_W, h=MAIN_H)))
    rail(ap, "#" + P + "Rail")
    ap.append(("#" + P + "Main", SUI.spacer(w=12)))
    if case == "m7":
        ap.append(("#" + P + "Main", SUI.group(P + "Out", layout="TopScrolling", w=CV_W, h=MAIN_H,
                                               extra="ScrollbarStyle: %s;" % SUI.scrollbar_style())))
        ap.append(("#" + P + "Out", "Group #%s { Anchor: (Height: %d); LayoutMode: LeftScrolling; ScrollbarStyle: %s; }" % (
            P + "In", 2 * H, SUI.scrollbar_style())))
        ap.append(("#" + P + "In", "Group #%s { Anchor: (Width: %d, Height: %d); Background: %s; }" % (P + "Cv", 2 * W, 2 * H,
                                                                                                      SUI.COLOR["well"])))
        canvas(ap, "#" + P + "Cv", [], scale=2)
    else:
        ap.append(("#" + P + "Main", "Group #%s { Anchor: (Width: %d, Height: %d); Background: %s; }" % (P + "Cv", W, H, SUI.COLOR["well"])))
        canvas(ap, "#" + P + "Cv", list(DRAWN) if case in ("m1", "m1b", "m1c") else LIT_FIX, halo_k=SEL0)
    ap.append(("#" + P + "Main", SUI.spacer(w=12)))
    ap.append(("#" + P + "Main", SUI.panel(P + "Pn", "well", w=PANEL_W, h=MAIN_H)))
    left = panel(ap, "#" + P + "Pn", case)
    pn = "#" + P + "Pn"
    inner = PANEL_W - 16
    if dummies:                                   # M1b / M1c: dummy nodes (disc, icon, hit box = 3 elements each) in a grid
        ap.text(pn, P + "DmH", "Load test: %d dummy nodes, 3 elements each" % dummies, "caption", size=13, h=20, w=inner)
        cols = inner // 18
        rows_ = (dummies + cols - 1) // cols
        assert 20 + rows_ * 18 <= left, ("dummy grid", rows_, left)
        ap.append((pn, SUI.group(P + "Dm", layout=None, w=inner, h=rows_ * 18)))
        for d in range(dummies):
            l, t = (d % cols) * 18, (d // cols) * 18
            ap.append(("#" + P + "Dm", raw_group(P + "D%d" % d, l, t, 14, 14, TEXPATH["Dummy"])))
            ap.append(("#" + P + "D%d" % d, SUI.item_icon(P + "D%dI" % d, "Ore_Copper", size=10, anchor={"left": 2, "top": 2})))
            ap.append(("#" + P + "D%d" % d, hit_button(P + "D%dB" % d, 1, 1, 12)))
    if case == "m2":                              # pictures vs clicks: a button UNDER a picture, a button OVER it
        ap.text(pn, P + "CtH", "Click both squares - left: a button under a picture, right: a button over it", "caption", size=13,
                h=20, w=inner)
        ap.append((pn, SUI.group(P + "Ct", layout=None, w=inner, h=56)))
        ap.append(("#" + P + "Ct", hit_button(P + "CtU", 40, 4, 48)))
        ap.append(("#" + P + "Ct", raw_group(P + "CtUP", 40, 4, 48, 48, TEXPATH["Node/Ready"])))
        ap.append(("#" + P + "Ct", raw_group(P + "CtOP", 240, 4, 48, 48, TEXPATH["Node/Ready"])))
        ap.append(("#" + P + "Ct", hit_button(P + "CtO", 240, 4, 48)))
        assert 20 + 56 <= left
    if case == "m4":                              # AssetImage @2x path / 1x path / the proven Background control
        ap.text(pn, P + "A4H", "AssetImage 2x path  |  AssetImage 1x path  |  control", "caption",
                size=13, h=20, w=inner)
        ap.append((pn, SUI.group(P + "A4", layout=None, w=inner, h=70)))
        ap.append(("#" + P + "A4", 'AssetImage #%s { Anchor: (Left: 30, Top: 3, Width: 64, Height: 64); AssetPath: "%s"; }'
                   % (P + "A1", M4_PATH_2X[0])))
        ap.append(("#" + P + "A4", 'AssetImage #%s { Anchor: (Left: 188, Top: 3, Width: 64, Height: 64); AssetPath: "%s"; }'
                   % (P + "A2", M4_PATH_1X[0])))
        ap.append(("#" + P + "A4", raw_group(P + "A3", 346, 3, 64, 64, TEXPATH["Asset/S0"])))
        ap.append((pn, SUI.group(P + "A4R", layout="Left", w=inner, h=SUI.BTN_SMALL_H + 4)))
        ap.append(("#" + P + "A4R", SUI.button(P + "A4N", "Next state", "secondary", "small", w=150, anchor={"right": 12})))
        ap.text("#" + P + "A4R", P + "A4S", "State 1 of 5 - " + M4_STATES[0][2], "default", size=15, h=SUI.BTN_SMALL_H, w=inner - 170)
        assert 20 + 70 + SUI.BTN_SMALL_H + 4 <= left
    if case == "m6":                              # 3 node discs with TooltipText (kit trial key "tooltip")
        ap.text(pn, P + "TtH", "Hover each disc - a tooltip should name it and its rank", "caption", size=13, h=20, w=inner)
        ap.append((pn, SUI.group(P + "Tt", layout=None, w=inner, h=50)))
        for i, (nm, st, km) in enumerate((("Quick Swing - Rank 2 / 5", "MiningL25", None), ("Rich Seams - Rank 0 / 3", "Ready", None),
                                          ("Deep Veins - locked - Row 3", "Locked", None))):
            gid = P + "Tt%d" % i
            ap.append(("#" + P + "Tt", raw_group(gid, 40 + i * 140, 3, 44, 44, TEXPATH["Node/" + st])))
            ap.append(("#" + gid, SUI.item_icon(gid + "I", "Tool_Pickaxe_Iron", size=24, anchor={"left": 10, "top": 10})))
            ap.append(("#" + gid, hit_button(gid + "B", 4, 4, 36, tip=nm)))
        assert 20 + 50 <= left
    return sh


DUMMY = {}
_base = None


def count_elements(appends):
    return sum(SUI._strip_quoted(SUI.render(mk)).count("{") for _p, mk in appends)


def bindings(case, appends):
    b = [("#" + P + "Go" + c.capitalize(), "case:" + c) for c in CASE_KEYS] + [("#" + P + "Close", "close")]
    if case in ("m1", "m1b", "m1c"):
        b.append(("#" + P + "Rb", "rebuild10"))
    b += [("#" + P + "N%dB" % k, "n%d" % k) for k in range(len(NODES))]
    if case == "m2":
        b += [("#" + P + "CtU", "ctlunder"), ("#" + P + "CtO", "ctlover")]
    if case == "m4":
        b.append(("#" + P + "A4N", "m4next"))
    if case == "m6":
        b += [("#" + P + "Tt%dB" % i, "tip%d" % i) for i in range(3)]
    b += [("#" + P + "SegW", "stub:Whole page"), ("#" + P + "SegF", "stub:Focus"), ("#" + P + "TLearn", "stub:Learn")]
    return b


PROBE_TOKENS = {"m4": {"element AssetImage", "AssetPath"}, "m6": {"TooltipText", "TextTooltipStyle", "MaxWidth"},
                "m7": {"LayoutMode: LeftScrolling"}}
PAGES = {}
_base_n = count_elements(page("m1").appends)
DUMMY = {"m1b": int(math.ceil((1200 - _base_n) / 3.0)), "m1c": int(math.ceil((1600 - _base_n) / 3.0))}
for c in CASE_KEYS:
    sh = page(c, DUMMY.get(c, 0))
    ap = sh.appends
    sets = list(ap.sets) + list(sh.sets)
    chk = SUI.Appends(ap)
    chk.sets = sets
    for _p, mk in ap:                                              # every markup: syntax / id / text rules (our own texture paths)
        SUI.check_markup(mk, prefix=P, root=(_p is None), kit_paths=False)
    SUI.check_page(chk, P)
    SUI.assert_page_size(sh.w, sh.h)
    toks = SUI.proven_tokens(chk)
    # "base" = the kit's core look (frame, buttons, WrapMaxLines...) every deployed hub page uses; anything else unproven must be
    # exactly this case's own probe tokens (M4 AssetImage / AssetPath, M6 the tooltip trial key, M7 LeftScrolling)
    unproven = set(k for k, g in toks.items() if g == "unknown" or (g is not None and "base" not in g))
    assert unproven == PROBE_TOKENS.get(c, set()), "%s: unproven tokens %s (the case's own: %s)" % (c, sorted(unproven), sorted(PROBE_TOKENS.get(c, ())))
    for _p, mk in ap:                                              # every texture path = a kit texture or one this jar ships
        for m in re.finditer(r'(?:Background|TexturePath|Handle|HoveredHandle|DraggedHandle|Default|Hovered|Pressed): *"([^"]+\.png)"', mk):
            pth = m.group(1)
            assert pth in set(SUI.TEX.values()) or (pth.startswith(MAP_DIR) and TEX_ROOT + pth[:-4] + "@2x.png" in ASSETS), pth
        for m in re.finditer(r'AssetPath: *"([^"]+)"', mk):
            assert "Common/" + m.group(1) in ASSETS, m.group(1)
    binds = bindings(c, ap)
    ids = set(i for _p, mk in ap for i in SUI._static_ids(mk))
    for sel, act in binds:
        assert sel[1:] in ids, "%s: binding %s has no element" % (c, sel)
    lines = []
    for _p, mk in ap:
        mk_ = SUI.render(mk)
        assert "\t" not in mk_ and "\n" not in mk_
        lines.append("A\t%s\t%s" % ("" if _p is None else SUI.render(_p if _p.startswith("#") else "#" + _p), mk_))
    for ident, prop, val in sets:
        assert isinstance(val, str) and not SUI.has_j(val) and "\t" not in val and "\n" not in val, (ident, prop, val)
        lines.append("S\t#%s.%s\t%s" % (SUI.render(ident).lstrip("#"), prop, val))
    for sel, act in binds:
        lines.append("E\t%s\t%s" % (sel, act))
    text = "\n".join(lines) + "\n"
    PAGES[c] = dict(text=text, elements=count_elements(ap), appends=len(ap), sets=len(sets), binds=len(binds), bytes=len(text.encode("utf-8")),
                    markup=sum(len(SUI.render(mk)) for _p, mk in ap), dummies=DUMMY.get(c, 0))
    ASSETS[RES_DIR + c + ".txt"] = text.encode("utf-8")
# node metadata for the click lines + the M5 halo move: k, label, left, top, size, centre x, centre y (canvas px, scale 1)
NODE_LINES = ["%d\t%s\t%d\t%d" % (k, node_label(n["id"]), int(round(n["cx"])), int(round(n["cy"]))) for k, n in enumerate(NODES)]
ASSETS[RES_DIR + "nodes.txt"] = ("\n".join(NODE_LINES) + "\n").encode("utf-8")
for c in CASE_KEYS:
    print("page %-4s %-15s %5d elements, %4d appends, %3d b.set, %3d bindings, %6d bytes markup%s" % (
        c, CASE_NAME[c], PAGES[c]["elements"], PAGES[c]["appends"], PAGES[c]["sets"], PAGES[c]["binds"], PAGES[c]["markup"],
        (", %d dummy nodes" % PAGES[c]["dummies"]) if PAGES[c]["dummies"] else ""))
assert 600 <= PAGES["m1"]["elements"] <= 900 and 1200 <= PAGES["m1b"]["elements"] <= 1210 and 1600 <= PAGES["m1c"]["elements"] <= 1610
DUMP = {"cases": CASES, "pages": dict((c, dict((k, v) for k, v in PAGES[c].items() if k != "text")) for c in CASE_KEYS),
        "nodes": len(NODES), "edges": len(EDGES), "lit_fixture": LIT_FIX, "sel0": SEL0, "m4_2x": M4_PATH_2X, "m4_1x": M4_PATH_1X,
        "m4_states": [s[2] for s in M4_STATES], "node_xy": [(int(round(n["cx"])), int(round(n["cy"]))) for n in NODES],
        "node_labels": [node_label(n["id"]) for n in NODES], "assets": sorted(ASSETS),
        "binds": dict((c, [act for _sel, act in bindings(c, None)]) for c in CASE_KEYS)}   # 0.7.1: the harness clicks every one
if "--assets-out" in sys.argv:               # dev preview: every jar asset (pictures + page data) + dump.json into a scratch folder
    _od = os.path.realpath(sys.argv[sys.argv.index("--assets-out") + 1])
    assert _od.startswith(os.path.realpath(os.path.join(ROOT, "tools", "dev", "scratch")) + os.sep), "--assets-out: only under tools/dev/scratch/"
    for _pth, _b in ASSETS.items():
        os.makedirs(os.path.dirname(os.path.join(_od, _pth)), exist_ok=True)
        with open(os.path.join(_od, _pth), "wb") as _f:
            _f.write(_b)
    with open(os.path.join(_od, "dump.json"), "w", encoding="utf-8") as _f:
        json.dump(DUMP, _f, indent=1)
    print("assets written to %s" % _od)
if "--dump-only" in sys.argv:
    print("dump-only: stop before the JVM (%.1f s)" % (time.time() - T0))
    raise SystemExit(0)

# ================================================================= 4. JAVA
import skyybuild as B
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)
T = {
    "PKG": PKG, "VERSION": VERSION, "NODE": NODE_PERM, "RES": RES_DIR, "PFX": P,
    "JP": "com.hypixel.hytale.server.core.plugin.JavaPlugin",
    "JPI": "com.hypixel.hytale.server.core.plugin.JavaPluginInit",
    "PR": "com.hypixel.hytale.server.core.universe.PlayerRef",
    "REF": "com.hypixel.hytale.component.Ref",
    "ST": "com.hypixel.hytale.component.Store",
    "WLD": "com.hypixel.hytale.server.core.universe.world.World",
    "APC": "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand",
    "CTX": "com.hypixel.hytale.server.core.command.system.CommandContext",
    "RA": "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg",
    "ATY": "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes",
    "MSG": "com.hypixel.hytale.server.core.Message",
    "LOG": "com.hypixel.hytale.logger.HytaleLogger",
    "PLA": "com.hypixel.hytale.server.core.entity.entities.Player",
    "PAGE": "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage",
    "LIFE": "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime",
    "UCB": "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder",
    "UEB": "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder",
    "EVD": "com.hypixel.hytale.server.core.ui.builder.EventData",
    "BT": "com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType",
    "ANC": "com.hypixel.hytale.server.core.ui.Anchor",
    "VAL": "com.hypixel.hytale.server.core.ui.Value",
}
for c, m in ((T["JP"], "getLogger"), (T["JP"], "getCommandRegistry"), (T["APC"], "requirePermission"), (T["APC"], "setPermissionGroups"),
             (T["APC"], "addAliases"), (T["APC"], "addUsageVariant"), (T["APC"], "withRequiredArg"), (T["CTX"], "get"),
             (T["ATY"], "STRING"), (T["PR"], "sendMessage"), (T["PR"], "getUsername"), (T["MSG"], "raw"), (T["PLA"], "getComponentType"),
             (T["PLA"], "getPageManager"), ("com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager", "openCustomPage"),
             (T["PAGE"], "build"), (T["PAGE"], "handleDataEvent"), (T["PAGE"], "close"), (T["PAGE"], "rebuild"), (T["PAGE"], "sendUpdate"),
             (T["PAGE"], "onDismiss"), (T["LIFE"], "CanDismiss"), (T["UCB"], "appendInline"), (T["UCB"], "set"), (T["UCB"], "setObject"),
             (T["UEB"], "addEventBinding"), (T["EVD"], "of"), (T["BT"], "Activating"), (T["ANC"], "setLeft"), (T["ANC"], "setTop"),
             (T["ANC"], "setWidth"), (T["ANC"], "setHeight"), (T["VAL"], "of"), (T["ST"], "getComponent")):
    B.probe(pool, c, m)
TOKEN = re.compile(r"@([A-Z0-9]{2,7})@")


def jv(src):
    def rep(mm):
        k = mm.group(1)
        if k not in T:
            raise SystemExit("unknown token @%s@ in:\n%s" % (k, src[:300]))
        return T[k]
    out = TOKEN.sub(rep, src)
    if re.search(r"@[A-Za-z0-9]+@", out):
        raise SystemExit("an @TOKEN@ was left in the Java source (tokens are 2-7 capitals / digits): %s" % out[:300])
    return out


def M(cls, src):
    try:
        cls.addMethod(CtNewMethod.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("compile failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:2500]))


def F(cls, src):
    try:
        cls.addField(CtField.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("field failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:600]))


def C(cls, src):
    try:
        cls.addConstructor(CtNewConstructor.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("constructor failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:1500]))


def mk(name, sup=None):
    return pool.makeClass(PKG + "." + name, pool.get(sup)) if sup else pool.makeClass(PKG + "." + name)


def jl(s):
    return SUI.java_lit(s)


def jarr(xs):
    return "new String[] { %s }" % ", ".join(jl(x) for x in xs)


log = mk("ProbeLog")
data = mk("ProbeData")
page_c = mk("MapPage", T["PAGE"])
cmds = mk("ProbeCmds")

# ---- ProbeLog: server log + chat; the last 300 lines kept in memory (the harness reads them; nothing is written anywhere)
F(log, "public static @LOG@ LOG;")
F(log, "public static java.util.LinkedList TAIL = new java.util.LinkedList();")
M(log, r"""
public static synchronized void remember(String s) {
  TAIL.add(s);
  while (TAIL.size() > 300) TAIL.removeFirst();
}""")
M(log, r"""
public static void info(String s) {
  remember("I " + s);
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyUiProbe] " + s); } catch (Throwable t) { }
}""")
M(log, r"""
public static void warn(String s) {
  remember("W " + s);
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyUiProbe] " + s); } catch (Throwable t) { }
}""")
M(log, r"""
public static void chat(@PR@ pr, String s) {
  try { if (pr != null) pr.sendMessage(@MSG@.raw("[SkyyUiProbe] " + s)); } catch (Throwable t) { }
}""")
M(log, r"""
public static void tell(@PR@ pr, String s) {
  info(s);
  chat(pr, s);
}""")

# ---- ProbeData: the cases + the page data resources (read once from the jar, cached)
F(data, "public static final String[] KEYS = %s;" % jarr(CASE_KEYS))
F(data, "public static final String[] NAMES = %s;" % jarr([c[1] for c in CASES]))
F(data, "public static final String[] HEADS = %s;" % jarr([c[2] for c in CASES]))
F(data, "public static final String[] WHAT = %s;" % jarr([c[3] for c in CASES]))
F(data, "public static final int[] ELEMENTS = new int[] { %s };" % ", ".join(str(PAGES[c]["elements"]) for c in CASE_KEYS))
F(data, "public static final String[] M4_2X = %s;" % jarr(M4_PATH_2X))
F(data, "public static final String[] M4_1X = %s;" % jarr(M4_PATH_1X))
F(data, "public static final String[] M4_TEXT = %s;" % jarr(["State %d of %d - %s" % (i + 1, len(M4_STATES), s[2]) for i, s in enumerate(M4_STATES)]))
F(data, "public static final int SEL0 = %d;" % SEL0)
F(data, "public static final int NODES = %d;" % len(NODES))
F(data, "public static java.util.HashMap CACHE = new java.util.HashMap();")
F(data, "public static String[] LABEL;")
F(data, "public static int[] NX;")
F(data, "public static int[] NY;")
M(data, r"""
public static int index(String c) {
  if (c == null) return -1;
  String t = c.trim().toLowerCase();
  for (int i = 0; i < KEYS.length; i++) if (KEYS[i].equals(t) || NAMES[i].equals(t)) return i;
  return -1;
}""")
M(data, r"""
public static String[] read(String name) {
  java.io.InputStream in = @PKG@.ProbeData.class.getClassLoader().getResourceAsStream("@RES@" + name + ".txt");
  if (in == null) throw new IllegalStateException("page data @RES@" + name + ".txt is missing from the jar");
  java.util.ArrayList out = new java.util.ArrayList();
  try {
    java.io.BufferedReader r = new java.io.BufferedReader(new java.io.InputStreamReader(in, java.nio.charset.StandardCharsets.UTF_8));
    String s = r.readLine();
    while (s != null) { if (s.length() > 0) out.add(s); s = r.readLine(); }
  } catch (java.io.IOException e) {
    throw new IllegalStateException("page data " + name + " unreadable: " + e);
  } finally {
    try { in.close(); } catch (Throwable t) { }
  }
  return (String[]) out.toArray(new String[0]);
}""")
M(data, r"""
public static synchronized String[] lines(String c) {
  String[] l = (String[]) CACHE.get(c);
  if (l == null) { l = read(c); CACHE.put(c, l); }
  return l;
}""")
M(data, r"""
public static synchronized void nodes() {
  if (LABEL != null) return;
  String[] l = read("nodes");
  String[] lab = new String[l.length];
  int[] x = new int[l.length];
  int[] y = new int[l.length];
  for (int i = 0; i < l.length; i++) {
    String[] p = l[i].split("\t");
    int k = Integer.parseInt(p[0]);
    lab[k] = p[1];
    x[k] = Integer.parseInt(p[2]);
    y[k] = Integer.parseInt(p[3]);
  }
  NX = x; NY = y; LABEL = lab;
}""")
M(data, r"""
public static String act(String d) {
  if (d == null) return "";
  int i = d.indexOf("\"a\"");
  if (i < 0) return "";
  int c = d.indexOf(':', i + 3);
  if (c < 0) return "";
  int q = d.indexOf('"', c + 1);
  if (q < 0) return "";
  int e = d.indexOf('"', q + 1);
  if (e < 0) return "";
  return d.substring(q + 1, e);
}""")

# ---- MapPage: one inline page per case (switched in place by rebuild); every click answered, every result logged
F(page_c, "public String cs;")
F(page_c, "public int ci;")
F(page_c, "public int clicks;")
F(page_c, "public int builds;")
F(page_c, "public int m4;")
F(page_c, "public int sel;")
F(page_c, "public int lastElements;")
F(page_c, "public int lastBytes;")
F(page_c, "public int lastBinds;")
F(page_c, "public long lastMs;")
F(page_c, "public long sumMs;")
F(page_c, "public boolean quiet;")
F(page_c, "public boolean answered;")         # 0.7.1: this click's answer was sent (handleDataEvent's safety net reads it)
F(page_c, "public int answers;")              # 0.7.1: answers sent by say() + the safety net (the harness reads it)
F(page_c, "public int nets;")                 # 0.7.1: how often the safety net had to send the empty answer
C(page_c, r"""
public MapPage(@PR@ pr, String c) {
  super(pr, @LIFE@.CanDismiss);
  this.cs = c;
  this.ci = @PKG@.ProbeData.index(c);
  this.sel = @PKG@.ProbeData.SEL0;
}""")
M(page_c, r"""
public String tag() { return this.cs.toUpperCase() + " " + @PKG@.ProbeData.NAMES[this.ci]; }""")
M(page_c, r"""
public void dyn(@UCB@ b) {
  if (this.cs.equals("m4")) {
    b.set("#@PFX@A1.AssetPath", @PKG@.ProbeData.M4_2X[this.m4]);
    b.set("#@PFX@A2.AssetPath", @PKG@.ProbeData.M4_1X[this.m4]);
    b.set("#@PFX@A4S.Text", @PKG@.ProbeData.M4_TEXT[this.m4]);
  }
}""")
M(page_c, r"""
public static @ANC@ anchor(int l, int t, int w, int h) {
  @ANC@ a = new @ANC@();
  a.setLeft(@VAL@.of(Integer.valueOf(l)));
  a.setTop(@VAL@.of(Integer.valueOf(t)));
  a.setWidth(@VAL@.of(Integer.valueOf(w)));
  a.setHeight(@VAL@.of(Integer.valueOf(h)));
  return a;
}""")
M(page_c, r"""
public void haloTo(@UCB@ b, int k) {
  @PKG@.ProbeData.nodes();
  int sz = this.cs.equals("m7") ? 88 : 44;
  int f = this.cs.equals("m7") ? 2 : 1;
  if (this.cs.equals("m7")) return;
  b.setObject("#@PFX@Sel.Anchor", anchor(@PKG@.ProbeData.NX[k] * f - sz / 2, @PKG@.ProbeData.NY[k] * f - sz / 2, sz, sz));
}""")
# 0.7.1: THE answer to a click that changes nothing else: ONE short page update (the right panel's caption, + the talent name for a
# node click) - the client's "Loading..." ends and Skyy sees the click worked. (SkyyExploration 0.2.3 answer() pattern.)
M(page_c, r"""
public void say(String cap, String name) {
  @UCB@ ub = new @UCB@();
  ub.set("#@PFX@TCap.Text", cap == null ? "" : cap);
  if (name != null) ub.set("#@PFX@TName.Text", name);
  this.answered = true;
  this.answers = this.answers + 1;
  this.sendUpdate(ub);
}""")
M(page_c, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  long t0 = System.nanoTime();
  String[] l = @PKG@.ProbeData.lines(this.cs);
  int els = 0;
  int bytes = 0;
  int binds = 0;
  for (int i = 0; i < l.length; i++) {
    String s = l[i];
    char k = s.charAt(0);
    int a = s.indexOf('\t', 2);
    String x = s.substring(2, a);
    String y = s.substring(a + 1);
    if (k == 'A') {
      b.appendInline(x.length() == 0 ? (String) null : x, y);
      bytes = bytes + y.length();
      for (int j = 0; j < y.length(); j++) if (y.charAt(j) == '{') els = els + 1;
    } else if (k == 'S') {
      b.set(x, y);
    } else if (k == 'E') {
      ev.addEventBinding(@BT@.Activating, x, @EVD@.of("a", y));
      binds = binds + 1;
    }
  }
  dyn(b);
  if (this.cs.equals("m5") || this.sel != @PKG@.ProbeData.SEL0) haloTo(b, this.sel);
  long ms = (System.nanoTime() - t0) / 1000000L;
  this.builds = this.builds + 1;
  this.lastElements = els;
  this.lastBytes = bytes;
  this.lastBinds = binds;
  this.lastMs = ms;
  this.sumMs = this.sumMs + ms;
  if (!this.quiet) @PKG@.ProbeLog.info(tag() + " build #" + this.builds + ": " + els + " elements, " + (bytes / 1024) + " KB markup, " + binds + " click bindings, built in " + ms + " ms");
}""")
M(page_c, r"""
public void node(@PR@ pr, int k) {
  @PKG@.ProbeData.nodes();
  if (k < 0 || k >= @PKG@.ProbeData.NODES) { @PKG@.ProbeLog.tell(pr, tag() + " FAIL - click on an unknown node " + k); say("Unknown node " + k + " - nothing selected", null); return; }
  this.clicks = this.clicks + 1;
  String nm = @PKG@.ProbeData.LABEL[k];
  if (this.cs.equals("m5")) {
    this.sel = k;
    @UCB@ ub = new @UCB@();
    haloTo(ub, k);
    ub.set("#@PFX@TName.Text", nm);
    ub.set("#@PFX@TCap.Text", "Selected by the M5 Anchor update (click " + this.clicks + ")");
    this.answered = true;
    this.sendUpdate(ub);
    @PKG@.ProbeLog.tell(pr, "M5 sent: ONE Anchor update moved the halo to node " + k + " (" + nm + ") + 2 panel texts, no rebuild - Skyy: look, did only the halo jump?");
    return;
  }
  int cut = nm.lastIndexOf(" - ");
  say("Click " + this.clicks + ": " + (cut > 0 ? nm.substring(0, cut) : nm), cut > 0 ? nm.substring(cut + 3) : nm);
  @PKG@.ProbeLog.tell(pr, this.cs.toUpperCase() + " click " + this.clicks + " reached the server: node " + k + " = " + nm + " (answered: the panel names it)");
  if (this.clicks == 10 && (this.cs.startsWith("m1"))) @PKG@.ProbeLog.tell(pr, tag() + " PASS (server) - 10 node clicks reached the server; Skyy: look - was each click answered at once?");
  if (this.cs.equals("m2") && this.clicks == 3) @PKG@.ProbeLog.tell(pr, "M2 map-order PASS (server) - 3 clicks on nodes over lines reached the server. Skyy: look - a click on a bare line printed nothing?");
  if (this.cs.equals("m7") && this.clicks == 1) @PKG@.ProbeLog.tell(pr, "M7 map-scroll PASS (server) - a node inside the 2-way scroll box is clickable. Skyy: look - does it scroll both ways?");
}""")
M(page_c, r"""
public void rebuild10(@PR@ pr) {
  int b0 = this.builds;
  long s0 = this.sumMs;
  this.quiet = true;
  try {
    for (int i = 0; i < 10; i++) rebuild();
  } finally { this.quiet = false; }
  int n = this.builds - b0;
  long avg = n > 0 ? (this.sumMs - s0) / n : -1L;
  if (n == 10) @PKG@.ProbeLog.tell(pr, tag() + " PASS (server) - Rebuild 10x: 10 full pages of " + this.lastElements + " elements (" + (this.lastBytes / 1024) + " KB markup) sent in a row, " + avg + " ms each to build. Skyy: look - still connected, page fine?");
  else @PKG@.ProbeLog.tell(pr, tag() + " FAIL - Rebuild 10x built " + n + " of 10 pages (see the server log)");
}""")
M(cmds, r"""
public static void announce(@PR@ pr, @PKG@.MapPage pg) {
  @PKG@.ProbeLog.tell(pr, pg.tag() + " opened (" + pg.lastElements + " elements, " + (pg.lastBytes / 1024) + " KB markup, built in " + pg.lastMs + " ms) - PASS (server) if the page shows. " + @PKG@.ProbeData.WHAT[pg.ci]);
}""")
M(page_c, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String d) {
  @PR@ pr = this.playerRef;
  String a = @PKG@.ProbeData.act(d);
  this.answered = false;                         // 0.7.1: every path below answers with exactly ONE page packet
  try {
    if (a.equals("close")) { @PKG@.ProbeLog.info(tag() + " closed with the Close button by " + pr.getUsername()); this.answered = true; close(); return; }
    if (a.startsWith("case:")) {
      String c = a.substring(5);
      int i = @PKG@.ProbeData.index(c);
      if (i < 0) { @PKG@.ProbeLog.tell(pr, "FAIL - unknown case " + c); say("No case '" + c + "' - nothing changed", null); return; }
      this.cs = @PKG@.ProbeData.KEYS[i]; this.ci = i; this.clicks = 0; this.m4 = 0; this.sel = @PKG@.ProbeData.SEL0;
      this.answered = true;
      rebuild();
      @PKG@.ProbeCmds.announce(pr, this);
      return;
    }
    if (a.startsWith("n")) { node(pr, Integer.parseInt(a.substring(1))); return; }
    if (a.equals("rebuild10")) { this.answered = true; rebuild10(pr); return; }
    if (a.equals("m4next")) {
      this.m4 = (this.m4 + 1) % @PKG@.ProbeData.M4_2X.length;
      @UCB@ ub = new @UCB@();
      dyn(ub);
      this.answered = true;
      this.sendUpdate(ub);
      @PKG@.ProbeLog.tell(pr, "M4 sent: " + @PKG@.ProbeData.M4_TEXT[this.m4] + " - only 2 AssetPath sets + 1 text, no rebuild. Skyy: look - which discs changed (left 2x path, middle 1x path; right = control, never changes)?");
      return;
    }
    if (a.equals("ctlunder")) { @PKG@.ProbeLog.tell(pr, "M2 control: the button UNDER a picture got the click -> a picture does NOT block clicks"); say("M2: the square UNDER the picture got the click", null); return; }
    if (a.equals("ctlover")) { @PKG@.ProbeLog.tell(pr, "M2 control: the button OVER a picture got the click (expected)"); say("M2: the square OVER the picture got the click", null); return; }
    if (a.startsWith("tip")) { @PKG@.ProbeLog.tell(pr, "M6 click on tooltip disc " + a.substring(3) + " reached the server"); say("M6: tooltip disc " + a.substring(3) + " clicked", null); return; }
    if (a.startsWith("stub:")) { @PKG@.ProbeLog.tell(pr, "'" + a.substring(5) + "' is only a stub in the probe (how the real page will look)"); say("'" + a.substring(5) + "' is a stub in the probe - click answered", null); return; }
    @PKG@.ProbeLog.warn(tag() + " unknown click data: " + d);
    say("Unknown click - nothing changed", null);
  } catch (Throwable t) {
    @PKG@.ProbeLog.warn(tag() + " FAIL - the click '" + a + "' failed: " + t);
    @PKG@.ProbeLog.chat(pr, tag() + " FAIL - the click failed: " + t);
  } finally {
    if (!this.answered) {                        // the safety net: nothing was sent (an error) - the engine's empty update ends "Loading..."
      this.answered = true;
      this.nets = this.nets + 1;
      this.answers = this.answers + 1;
      try { this.sendUpdate(); } catch (Throwable t2) { @PKG@.ProbeLog.warn(tag() + " the empty answer failed: " + t2); }
    }
  }
}""")
M(page_c, r"""
public void onDismiss(@REF@ ref, @ST@ st) {
  @PKG@.ProbeLog.info(tag() + " page closed (Esc or Close) by " + this.playerRef.getUsername() + " after " + this.clicks + " clicks - server OK" + (this.cs.equals("m6") ? ". M6: Skyy: look - was a tooltip showing when you pressed Esc, and did the game stay fine?" : ""));
}""")

# ---- ProbeCmds: the help list + opening a case
M(cmds, r"""
public static void help(@PR@ pr) {
  @PKG@.ProbeLog.chat(pr, "Radial tree map probe (op only, R0 of research/Radial-Trees-Spec.md). Open a case with /skyprobe <case> or /skyprobe map <case>; the buttons on the page switch case:");
  for (int i = 0; i < @PKG@.ProbeData.KEYS.length; i++) @PKG@.ProbeLog.chat(pr, @PKG@.ProbeData.KEYS[i] + " (" + @PKG@.ProbeData.NAMES[i] + ", " + @PKG@.ProbeData.ELEMENTS[i] + " elements) - " + @PKG@.ProbeData.HEADS[i].substring(@PKG@.ProbeData.HEADS[i].indexOf(':') + 2));
  @PKG@.ProbeLog.chat(pr, "Each result prints PASS, FAIL or 'Skyy: look' here and in the server log. Start with /skyprobe m1.");
  @PKG@.ProbeLog.info("help listed for " + (pr == null ? "?" : pr.getUsername()));
}""")
M(cmds, r"""
public static void open(@REF@ ref, @ST@ store, @PR@ pr, String c) {
  int i = @PKG@.ProbeData.index(c);
  if (i < 0) { @PKG@.ProbeLog.chat(pr, "No case '" + c + "'. /skyprobe help lists them (m1, m1b, m1c, m2 ... m7)."); return; }
  @PLA@ p = null;
  try { p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t) { p = null; }
  if (p == null) { @PKG@.ProbeLog.tell(pr, "FAIL - the page could not be opened (no player component)"); return; }
  @PKG@.MapPage pg = new @PKG@.MapPage(pr, @PKG@.ProbeData.KEYS[i]);
  try {
    p.getPageManager().openCustomPage(ref, store, pg);
  } catch (Throwable t) {
    @PKG@.ProbeLog.warn(pg.tag() + " FAIL - could not open: " + t);
    @PKG@.ProbeLog.chat(pr, pg.tag() + " FAIL - the page could not be opened: " + t);
    return;
  }
  announce(pr, pg);
}""")
M(cmds, r"""
public static void arg(@REF@ ref, @ST@ store, @PR@ pr, String a) {
  String t = a == null ? "" : a.trim();
  if (t.length() == 0 || t.equalsIgnoreCase("help") || t.equalsIgnoreCase("list") || t.equalsIgnoreCase("map")) { help(pr); return; }
  open(ref, store, pr, t);
}""")
M(cmds, r"""
public static void two(@REF@ ref, @ST@ store, @PR@ pr, String w, String c) {
  if (w == null || !w.trim().equalsIgnoreCase("map")) { @PKG@.ProbeLog.chat(pr, "Use /skyprobe map <case> or /skyprobe <case> - /skyprobe help lists the cases"); return; }
  open(ref, store, pr, c);
}""")

EXEC = "protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world)"
cmdM = mk("SkyProbeMapCmd", T["APC"])
F(cmdM, "public @RA@ whatArg;")
F(cmdM, "public @RA@ caseArg;")
C(cmdM, r"""
public SkyProbeMapCmd() {
  super("(admin) /skyprobe map <case> opens one radial tree map probe case (m1, m1b, m1c, m2, m3, m4, m5, m6, m7)");
  requirePermission("@NODE@");
  setPermissionGroups(new String[0]);
  this.whatArg = withRequiredArg("map", "the word map", @ATY@.STRING);
  this.caseArg = withRequiredArg("case", "m1, m1b, m1c, m2, m3, m4, m5, m6 or m7 (or its name, e.g. map-count)", @ATY@.STRING);
}""")
M(cmdM, EXEC + r""" {
  try { @PKG@.ProbeCmds.two(ref, store, pr, String.valueOf(ctx.get(this.whatArg)), String.valueOf(ctx.get(this.caseArg))); }
  catch (Throwable t) { @PKG@.ProbeLog.warn("/skyprobe map failed: " + t); @PKG@.ProbeLog.chat(pr, "Usage: /skyprobe map <case> - /skyprobe help lists the cases"); }
}""")
cmdA = mk("SkyProbeArgCmd", T["APC"])
F(cmdA, "public @RA@ caseArg;")
C(cmdA, r"""
public SkyProbeArgCmd() {
  super("(admin) /skyprobe <case> opens one radial tree map probe case; /skyprobe help lists them");
  requirePermission("@NODE@");
  setPermissionGroups(new String[0]);
  this.caseArg = withRequiredArg("case", "help, or a case: m1, m1b, m1c, m2, m3, m4, m5, m6, m7", @ATY@.STRING);
}""")
M(cmdA, EXEC + r""" {
  try { @PKG@.ProbeCmds.arg(ref, store, pr, String.valueOf(ctx.get(this.caseArg))); }
  catch (Throwable t) { @PKG@.ProbeLog.warn("/skyprobe failed: " + t); @PKG@.ProbeLog.chat(pr, "Usage: /skyprobe help, /skyprobe <case>"); }
}""")
cmd = mk("SkyProbeCmd", T["APC"])
C(cmd, r"""
public SkyProbeCmd() {
  super("skyprobe", "(admin) PROBE: the radial tree map test pages M1-M7 - /skyprobe help lists them, /skyprobe <case> opens one");
  requirePermission("@NODE@");
  setPermissionGroups(new String[0]);
  addAliases(new String[] { "uiprobe" });
  addUsageVariant(new @PKG@.SkyProbeArgCmd());
  addUsageVariant(new @PKG@.SkyProbeMapCmd());
}""")
M(cmd, EXEC + r""" {
  @PKG@.ProbeCmds.help(pr);
}""")

pl = mk("SkyyUiProbePlugin", T["JP"])
C(pl, "public SkyyUiProbePlugin(@JPI@ init) { super(init); }")
M(pl, r"""
public void setup() {
  @PKG@.ProbeLog.LOG = getLogger();
  getCommandRegistry().registerCommand(new @PKG@.SkyProbeCmd());
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyUiProbe] @VERSION@ ready - PROBE (op only): /skyprobe help (alias /uiprobe) lists the radial tree map cases M1-M7; no data, nothing for players");
}""")
M(pl, "protected void shutdown() { super.shutdown(); }")
CLASSES = [log, data, page_c, cmds, cmdM, cmdA, cmd, pl]
for c in CLASSES:
    c.writeFile(OUT)
print("classes written: %d" % len(CLASSES))

jar = os.path.join(HERE, "SkyyUiProbe-%s.jar" % VERSION)
man = B.manifest("SkyyUiProbe", VERSION, "SkyWynn DEV PROBE (op only): /skyprobe (alias /uiprobe) opens the radial skill-tree map test pages M1-M7 (element count, draw order + clicks, 2x line sharpness, AssetImage swap, Anchor move, tooltip, 2-way scroll) for one test session - no data, no config, nothing for players. Retire after the test.", PKG + ".SkyyUiProbePlugin")
assert man["IncludesAssetPack"] is True
B.assemble(jar, man, OUT, dict(sorted(ASSETS.items())))
with zipfile.ZipFile(jar) as _jz:
    names = _jz.namelist()
    assert not [n for n in names if n.lower().endswith(".ui")], "inline pages only"
    for n in names:
        if n.endswith(".png"):
            assert n.startswith(TEX_ROOT + "SkyyUiProbe/"), n
    for p_, b_ in ASSETS.items():
        assert _jz.read(p_) == b_, p_
print("jar: %d entries, %d pictures, %d page data files; build %.1f s" % (len(names), sum(1 for n in names if n.endswith(".png")),
                                                                        sum(1 for n in names if n.startswith(RES_DIR)), time.time() - T0))
