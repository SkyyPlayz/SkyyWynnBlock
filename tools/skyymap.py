"""skyymap - radial NODE MAPS for SkyWynn pages (research/Radial-Trees-Spec.md, round R1; owner Skyy, they/them).

Where this goes / who uses it: tools/ (shared build-time tool, INDEX.md tools row). Imported at BUILD time by SkyyTrees 0.5.0+ (the radial
skill-tree pages) and, in round R3, by SkyyRebirth (the Nexus). The kit side (markup, the 1,000-element guard, TREE_COLOR) is
tools/skyyui.py "KIT 1.8: NODE MAPS"; the look rules are research/Vanilla-UI-Style-Guide.md section 16. Self-test: python tools/test_skyymap.py.

What it does (pure Python, no game files, our own geometry - nothing vanilla-derived):
  1. LAYOUT   radial_layout(groups, ...) = the spec's 2.5 generator: an emblem in the centre, one hub per group (a tree, or one class
              branch) on a small ring, each branch's rows on concentric ellipses, the row's free perk / ability as a DIAMOND on the branch
              spine, a relax pass along each ellipse until every gap >= 6 px. place() rounds everything to whole px, joins the
              junctions that sit on a node, puts the banners in the canvas corners; fit_page() tries node sizes / ring / spacing / start
              angle and keeps the layout with the largest smallest gap that passes check().
  2. CHECK    check(lay, want_ids) = the spec's 2.5 list: every disc / hub / emblem / banner inside the canvas (4 px margin), any two discs
              >= GAP apart, disc vs hub / emblem / banner >= GAP, hit squares (26 / 32 of a disc) >= 2 px apart, every wanted node
              placed exactly once, the spine never jumps a row and points outward. Raises MapError naming the crowded pair.
  3. ZOOM     scaled(lay, z): the same map at z (1.5 / 2.0), every coordinate multiplied then rounded (checked again) - the zoom buttons
              of the tree pages show it inside a 2-axis scroll box (probe M7: proven). The pictures are NOT redrawn per zoom: the
              client stretches the same @2x textures (M7 showed the 2x map that way).
  4. PICTURES base_picture(lay) = every edge as a grey dotted line + the junction diamonds (one @2x RGBA PNG of the whole canvas);
              gold_pictures(lay) = one small gold dotted PNG per drawn edge (its box + 4 px, the SAME dot positions as the base, so a lit
              edge covers its grey line exactly); node_pictures(colours, maxes) = the disc / diamond / capstone state pictures (rank pips
              in the ring = Skyy's "Pips in the ring"), hub_picture, halo_picture, emblem_picture (the SkyWynn crest placeholder until
              the R4 art). png() = filter 0 + zlib 9 (deterministic bytes: the same input gives the same jar).
  5. PREVIEW  python tools/skyymap.py --preview [--dir <folder under tools/dev/scratch/>] writes one composited PNG per Trees page (lines +
              discs) for a look before a build - never committed (default tools/dev/scratch/skyymap/).

Ids / names: picture names never hold an underscore (element ids derive from them; HANDOFF section 2).
"""
import math
import os
import struct
import sys
import zlib

MAP_VERSION = "1.0"
# 1.1 (2026-10-23, SkyyTrees 0.6.0 class tree rebuild; research/Class-Tree-Clarity-Spec.md 2 + 4): a row's free node marked "ability" is
# an ABILITY node (ABIL_FRAC x the node size, its own rounded-square pictures <C>Ability / <C>AbilityPicked / AbilityOther / AbilityLocked),
# a row may hold a second free node ("free2": the two A1-alts of one selection gate) joined to the first by an "or" edge (a dashed gold
# line in the base picture, never lit, no gold picture). Every 1.0 layout is unchanged (MAP_VERSION stays "1.0": pinned builds assert it).
MAP_ABIL_VERSION = "1.1"
ABIL_FRAC = 1.3                         # an ability node = 1.3 x the node size (40 px discs -> 52 px; 32 -> 42)
ABIL_MIN = 48                           # fix round (critic C2): never smaller than 48 px (the spec's 52 -> 48 floor)
OR_GAP = 36                             # fix round (critic C1): px between the two A1-alts of an OR pair (room for the OR pill)
NODE_SIZES = (44, 40, 36, 32, 30, 28)   # the largest that fits wins (whole page: start at 32; the class page: 40 or 44)
GAP = 6                                 # min px between two discs (and disc vs hub / emblem / banner)
MARGIN = 4                              # every box stays this far inside the canvas
HIT_NUM, HIT_DEN = 26, 32               # the click square = 26 / 32 of the disc, centred (spec 1.4)
HIT_APART = 2                           # two click squares never closer than this
FREE_FRAC = 0.7                         # the free perk diamond = 0.7 x the node size
JUNC_R = 6.0                            # a bare junction diamond's radius (canvas px) - lines stop short of it
DOT_STEP = 8.0                          # @2x px between two dots of a line (spec 2.6)
DOT_R_BASE, DOT_R_GOLD = 1.5, 1.9       # @2x dot radius: grey base line / the gold lit line (a touch bigger: it covers the grey)
BANNER_W, BANNER_H = 200, 44            # a tree's banner (name 15 bold + motto 14, skyyui.MAP_MOTTO_SIZE) in the canvas corner (spec 2.2)

# data colours of the pictures (our own; the tree colours come from the caller - skyyui.TREE_COLOR)
ART = {"disc": "#101822", "ringLocked": "#4a535c", "lock": "#8a939c", "gold": "#E8A93B", "pipLit": "#ffd36b", "pipDim": "#2a323a",
       "line": "#797b7c", "halo": "#6fe3ff", "emblemFill": "#14284a", "white": "#f4f8ff", "open": "#9aa3ad"}


class MapError(SystemExit):
    """A layout that does not fit / a broken map: the build stops and names the crowded pair."""


def rgb(h):
    if not (isinstance(h, str) and len(h) == 7 and h[0] == "#"):
        raise MapError("skyymap: colour must be #rrggbb, got %r" % (h,))
    return (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16))


# ======================================================================================================== 1. LAYOUT
def items_of(row):
    """one row of one branch, left to right along its ellipse: the upgrades with the free diamond in the middle (1.1: + the row's second
    free node "free2" right after the first - the OR pair of a selection gate)"""
    ups = [("up", u["id"]) for u in row["ups"]]
    fr = [("free", "free")] if row.get("free") else []
    if row.get("free") and row.get("free2"):
        fr.append(("free", "free2"))
    h = len(ups) // 2
    return ups[:h] + fr + ups[h:]


def ring_f(ri, nrows, ring0):
    """row index 0.. -> ellipse fraction; a light tree's 4 rows spread over the same 6 rings (rows 1, 2.67, 4.33, 6)"""
    pos = ri if nrows == 6 else ri * 5.0 / max(1, nrows - 1)
    return ring0 + (1.0 - ring0) * pos / 5.0


def relax(nodes, cx, cy, rounds=200):
    """Deterministic: push same-ring neighbours apart along their own ellipse (radius kept) until every gap >= GAP."""
    rings = {}
    for n in nodes:
        rings.setdefault(n["ay"], []).append(n)
    for _ in range(rounds):
        moved = False
        for ay in sorted(rings):
            ring = rings[ay]
            for i in range(len(ring)):
                for j in range(i + 1, len(ring)):
                    p, q = ring[i], ring[j]
                    want = (p["size"] + q["size"]) / 2.0 + (OR_GAP if p.get("orp") and p.get("orp") == q.get("orp") else GAP) + 0.5
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
        abl = [n for n in nodes if n.get("abil")]   # fix round (critic C2): two ability squares on neighbouring rings - the outer one steps aside
        for i in range(len(abl)):
            for j in range(i + 1, len(abl)):
                p, q = abl[i], abl[j]
                if p["ay"] == q["ay"]:
                    continue
                if q["ay"] < p["ay"]:
                    p, q = q, p
                want = (p["size"] + q["size"]) / 2.0 + GAP + 0.5
                d = math.hypot(p["x"] - q["x"], p["y"] - q["y"])
                if d < want:
                    da = (want - d) / math.hypot(q["ax"] * math.cos(q["a"]), q["ay"] * math.sin(q["a"]))
                    q["a"] += da if q["a"] >= p["a"] else -da
                    q["x"], q["y"] = cx + q["ax"] * math.sin(q["a"]), cy - q["ay"] * math.cos(q["a"])
                    moved = True
        if not moved:
            return


def _base_start(n):
    """the default start angle (degrees) for n groups: 4 trees sit on the diagonals, 3 start at the top"""
    return {3: 0.0, 4: 45.0}.get(n, 0.0)


def radial_layout(groups, W=840, H=774, node=32, ring0=0.46, s=40.0, start=None, emb=96, hub=44, tree_gap=0.6, branch_gap=0.25):
    """groups = [(key, colour, [branch, ...])] in clockwise order (a skill page: one group per tree; the class page: one group per
    BRANCH); a branch = {"rows": [{"ups": [{"id": ...}], "free": {...} or None}, ...]}. Angles: 0 = up, clockwise. Returns the raw
    layout (float centres): dict(nodes, hubs, edges, junctions, W, H, node, emb, hub). The spec's 2.5 code, rows on rings."""
    cx, cy = W / 2.0, H / 2.0
    axm, aym = cx - 8 - node / 2.0, cy - 8 - node / 2.0
    avg = math.sqrt((axm * axm + aym * aym) / 2.0)
    need = []
    for _key, _col, branches in groups:
        bn = []
        for b in branches:
            m = max(((len(items_of(r)) - 1) * s + node + GAP) / (avg * ring_f(i, len(b["rows"]), ring0)) for i, r in enumerate(b["rows"]))
            bn.append(m + branch_gap * s / (avg * ring0))
        need.append(bn)
    tg = tree_gap * s / (avg * ring0)
    scale = 2 * math.pi / (sum(sum(b) for b in need) + tg * len(groups))
    if start is None:
        start = _base_start(len(groups))
    ang = math.radians(start) - (sum(need[0]) + tg) * scale / 2.0
    out = dict(nodes=[], hubs=[], edges=[], junctions=[], W=W, H=H, node=node, emb=emb, hub=hub)
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
                    fd = row.get(uid) if kind == "free" else None
                    isab = bool(fd and fd.get("ability"))   # 1.1: an ability node (bigger, its own pictures)
                    out["nodes"].append(dict(id=nid, kind=kind, a=a, ax=ax, ay=ay, col=col, cap=bool(row.get("cap")),
                                             size=node if kind == "up" else (max(int(round(node * ABIL_FRAC)), ABIL_MIN) if isab else int(node * FREE_FRAC)),
                                             x=cx + ax * math.sin(a), y=cy - ay * math.cos(a), abil=isab))
                    if kind == "free" and row.get("free2"):   # fix round: the OR pair (relax keeps OR_GAP between them)
                        out["nodes"][-1]["orp"] = (key, bi, ri)
                    if kind == "free" and uid == "free":
                        out["junctions"][-1].update(x=out["nodes"][-1]["x"], y=out["nodes"][-1]["y"], node=nid)
                    elif kind == "free":
                        out["edges"].append(((key, bi, ri, "free"), nid, "or", ri))   # 1.1: the OR pair (never lit)
                    else:
                        out["edges"].append((junc, nid, "spoke", ri))
                prev = junc
            ab += need[k][bi] * scale
        ang += span
    relax(out["nodes"], cx, cy)
    return out


def _corners(angles, W, H):
    """banner boxes (left, top, align) for hubs at these angles (radians, 0 = up, clockwise): each hub takes the free banner place
    nearest its direction among the 4 corners + top / bottom centre (4 trees at 45 / 135 / 225 / 315 -> the corners; 3 at 0 / 120 / 240
    -> top centre, bottom right, bottom left; the class page's branches at 60 / 180 / 300 -> top right, bottom centre, top left)"""
    a_c = math.degrees(math.atan2(W / 2.0, H / 2.0))
    spots = [(0.0, ((W - BANNER_W) // 2, MARGIN, "Center")), (a_c, (W - MARGIN - BANNER_W, MARGIN, "End")),
             (180.0 - a_c, (W - MARGIN - BANNER_W, H - MARGIN - BANNER_H, "End")), (180.0, ((W - BANNER_W) // 2, H - MARGIN - BANNER_H, "Center")),
             (180.0 + a_c, (MARGIN, H - MARGIN - BANNER_H, "Start")), (360.0 - a_c, (MARGIN, MARGIN, "Start"))]
    out, used = [], set()
    for a in angles:
        d = math.degrees(a) % 360.0
        best = min((i for i in range(len(spots)) if i not in used), key=lambda i: min(abs(d - spots[i][0]), 360.0 - abs(d - spots[i][0])))
        used.add(best)
        out.append(spots[best][1])
    return out


def place(raw, banners=True, banner_offset=0.0):
    """The raw layout -> whole px: every disc / hub its left / top (+ cx / cy of the rounded box), the emblem box, junctions that sit on
    a node (a free diamond, or an odd row's middle upgrade) joined to it, the banner boxes (banners=False: none; banner_offset = degrees
    added to each hub's direction when its corner is picked: the class page puts a branch's banner between two branches)."""
    W, H, emb, hub = raw["W"], raw["H"], raw["emb"], raw["hub"]
    lay = dict(W=W, H=H, node=raw["node"], emb=emb, hub=hub, edges=list(raw["edges"]), nodes=[], hubs=[], junctions=[], banners=[])
    for n in raw["nodes"]:
        m = dict((k, v) for k, v in n.items() if k in ("id", "kind", "size", "col", "cap", "abil", "orp"))
        m["l"], m["t"] = int(round(n["x"] - n["size"] / 2.0)), int(round(n["y"] - n["size"] / 2.0))
        m["cx"], m["cy"] = m["l"] + n["size"] / 2.0, m["t"] + n["size"] / 2.0
        lay["nodes"].append(m)
    for h in raw["hubs"]:
        m = dict(key=h["key"], col=h["col"], a=h["a"])
        m["l"], m["t"] = int(round(h["x"] - hub / 2.0)), int(round(h["y"] - hub / 2.0))
        m["cx"], m["cy"] = m["l"] + hub / 2.0, m["t"] + hub / 2.0
        lay["hubs"].append(m)
    by_id = dict((n["id"], n) for n in lay["nodes"])
    for j in raw["junctions"]:
        m = dict(id=j["id"], x=j["x"], y=j["y"])
        if "node" in j:
            m["node"] = j["node"]
        else:
            for n in lay["nodes"]:
                if n["id"][:3] == j["id"][:3] and math.hypot(n["cx"] - j["x"], n["cy"] - j["y"]) < 3:
                    m["node"] = n["id"]
        if "node" in m:
            n = by_id[m["node"]]
            m["x"], m["y"] = n["cx"], n["cy"]
        lay["junctions"].append(m)
    lay["emb_l"], lay["emb_t"] = W // 2 - emb // 2, H // 2 - emb // 2
    if banners:
        lay["banner_offset"] = banner_offset
        for h, (bl, bt, al) in zip(lay["hubs"], _corners([x["a"] + math.radians(banner_offset) for x in lay["hubs"]], W, H)):
            lay["banners"].append(dict(key=h["key"], l=bl, t=bt, w=BANNER_W, h=BANNER_H, align=al))
    lay["edge_dots"] = [edge_dots(lay, e) for e in lay["edges"]]
    return lay


def hit_of(n):
    """(side, offset) of a disc's click square: 26 / 32 of the disc, centred"""
    s = int(round(n["size"] * HIT_NUM / float(HIT_DEN)))
    return s, (n["size"] - s) // 2


def _box_circle_gap(bx, by, bw, bh, cx, cy, r):
    dx = max(bx - cx, 0, cx - (bx + bw))
    dy = max(by - cy, 0, cy - (by + bh))
    return math.hypot(dx, dy) - r


def _end(lay, e):
    """an edge end -> (centre x, centre y, radius the dots stop short of)"""
    if e[0] == "hub":
        h = [x for x in lay["hubs"] if x["key"] == e[1]][0]
        return h["cx"], h["cy"], lay["hub"] / 2.0 + 2
    if e[3] == "J":
        j = [x for x in lay["junctions"] if x["id"] == e][0]
        if "node" in j:
            n = [x for x in lay["nodes"] if x["id"] == j["node"]][0]
            return n["cx"], n["cy"], n["size"] / 2.0 + 1
        return j["x"], j["y"], JUNC_R
    n = [x for x in lay["nodes"] if x["id"] == e][0]
    return n["cx"], n["cy"], n["size"] / 2.0 + 1


def edge_dots(lay, e):
    """the dot centres of one edge in canvas px (trimmed short of both ends) - the same list for the base and the gold picture"""
    (ax, ay, ra), (bx, by, rb) = _end(lay, e[0]), _end(lay, e[1])
    L = math.hypot(bx - ax, by - ay)
    if L < 1e-6:
        return []
    ux, uy = (bx - ax) / L, (by - ay) / L
    pts, s = [], ra + 2.0
    while s <= L - rb - 2.0 + 1e-9:
        pts.append((ax + ux * s, ay + uy * s))
        s += DOT_STEP / 2.0
    return pts


def check(lay, want_ids=None, what="map"):
    """The spec's 2.5 checks; returns dict(min_gap, nodes, edges, drawn). Raises MapError on the first broken rule."""
    W, H, ns = lay["W"], lay["H"], lay["nodes"]

    def fail(msg):
        raise MapError("skyymap %s: %s" % (what, msg))
    ids = [n["id"] for n in ns]
    if len(set(ids)) != len(ids):
        fail("a node placed twice: %s" % sorted(set(i for i in ids if ids.count(i) > 1))[:3])
    if want_ids is not None and sorted(ids) != sorted(want_ids):
        fail("placed nodes != the tree data (missing %s, extra %s)" % (sorted(set(want_ids) - set(ids))[:3], sorted(set(ids) - set(want_ids))[:3]))
    for n in ns:
        if not (n["l"] >= MARGIN and n["t"] >= MARGIN and n["l"] + n["size"] <= W - MARGIN and n["t"] + n["size"] <= H - MARGIN):
            fail("node %s outside the canvas (%d, %d, %d)" % (n["id"], n["l"], n["t"], n["size"]))
    for h in lay["hubs"]:
        if not (h["l"] >= MARGIN and h["t"] >= MARGIN and h["l"] + lay["hub"] <= W - MARGIN and h["t"] + lay["hub"] <= H - MARGIN):
            fail("hub %s outside the canvas" % h["key"])
    for b in lay["banners"]:
        if not (b["l"] >= MARGIN and b["t"] >= MARGIN and b["l"] + b["w"] <= W - MARGIN and b["t"] + b["h"] <= H - MARGIN):
            fail("banner %s outside the canvas" % b["key"])
    mg = 1e9
    for i in range(len(ns)):
        p = ns[i]
        sp, op = hit_of(p)
        for j in range(i + 1, len(ns)):
            q = ns[j]
            g = math.hypot(p["cx"] - q["cx"], p["cy"] - q["cy"]) - (p["size"] + q["size"]) / 2.0
            if g < GAP - 0.01:
                fail("discs %s / %s only %.2f px apart (>= %d)" % (p["id"], q["id"], g, GAP))
            if p.get("orp") and p.get("orp") == q.get("orp") and g < OR_GAP - 1.01:   # fix round: the OR pill's room (its size does not zoom)
                fail("the OR pair %s / %s only %.2f px apart (>= %d)" % (p["id"], q["id"], g, OR_GAP))
            mg = min(mg, g)
            sq, oq = hit_of(q)
            gx = max(q["l"] + oq - (p["l"] + op + sp), p["l"] + op - (q["l"] + oq + sq))
            gy = max(q["t"] + oq - (p["t"] + op + sp), p["t"] + op - (q["t"] + oq + sq))
            if max(gx, gy) < HIT_APART:
                fail("click squares of %s / %s touch" % (p["id"], q["id"]))
        for h in lay["hubs"]:
            if math.hypot(p["cx"] - h["cx"], p["cy"] - h["cy"]) - (p["size"] + lay["hub"]) / 2.0 < GAP:
                fail("node %s on hub %s" % (p["id"], h["key"]))
        if math.hypot(p["cx"] - W / 2.0, p["cy"] - H / 2.0) - (p["size"] + lay["emb"]) / 2.0 < GAP:
            fail("node %s on the emblem" % (p["id"],))
        for b in lay["banners"]:
            if _box_circle_gap(b["l"], b["t"], b["w"], b["h"], p["cx"], p["cy"], p["size"] / 2.0) < GAP:
                fail("banner %s on node %s" % (b["key"], p["id"]))
    for b in lay["banners"]:
        for h in lay["hubs"]:
            if _box_circle_gap(b["l"], b["t"], b["w"], b["h"], h["cx"], h["cy"], lay["hub"] / 2.0) < GAP:
                fail("banner %s on hub %s" % (b["key"], h["key"]))
    c0 = (W / 2.0, H / 2.0)
    for e in lay["edges"]:
        a, b, kind, ri = e
        ax, ay, _r = _end(lay, a)
        bx, by, _r = _end(lay, b)
        if kind == "spine" and a[0] != "hub" and tuple(a[:3]) != (b[0], b[1], b[2] - 1):
            fail("spine %s -> %s jumps a row" % (a, b))
        if math.hypot(bx - c0[0], by - c0[1]) < math.hypot(ax - c0[0], ay - c0[1]) - 30 * (W / 840.0):
            fail("edge %s -> %s points inward" % (a, b))
    dots = lay["edge_dots"]
    for k, e in enumerate(lay["edges"]):
        if e[2] == "spine" and not dots[k]:
            fail("spine edge %s -> %s has no dots (too short to see)" % (e[0], e[1]))
    return dict(min_gap=mg, nodes=len(ns), edges=len(lay["edges"]), drawn=sum(1 for d in dots if d))


def build(groups, node=32, ring0=0.46, s=None, start=None, emb=96, hub=44, W=840, H=774, banners=True, want_ids=None, what="map",
          banner_offset=0.0):
    """radial_layout + place + check in one call (raises MapError when it does not fit)"""
    s = float(s if s is not None else node + 8)
    raw = radial_layout(groups, W=W, H=H, node=node, ring0=ring0, s=s, start=start, emb=emb, hub=hub)
    lay = place(raw, banners=banners, banner_offset=banner_offset)
    lay["info"] = check(lay, want_ids, what)
    lay["params"] = dict(node=node, ring0=ring0, s=s, start=start, emb=emb, hub=hub, banner_offset=banner_offset)
    return lay


def want_of(groups):
    """every node id the groups must place (for check's want_ids)"""
    return [(key, bi, ri, uid) for key, _c, brs in groups for bi, b in enumerate(brs) for ri, r in enumerate(b["rows"]) for _k, uid in items_of(r)]


def fit_page(groups, sizes=NODE_SIZES, ring0s=(0.46, 0.42, 0.50, 0.38, 0.54), spacing=(8, 6, 10, 12, 14, 16, 20), starts=(0, 5, -5, 10, -10),
             emb=96, hub=44, W=840, H=774, banners=True, what="map", banner_offset=0.0):
    """Try node sizes largest first; at the first size where anything passes, keep the passing (ring0, spacing, start) with the
    largest smallest gap. Raise MapError naming the crowded pair of the last try when nothing fits at any size."""
    want = want_of(groups)
    base_start = _base_start(len(groups))
    last = None
    for node in sizes:
        best = None
        for r0 in ring0s:
            for sp in spacing:
                for st in starts:
                    try:
                        lay = build(groups, node=node, ring0=r0, s=node + sp, start=base_start + st, emb=emb, hub=hub, W=W, H=H,
                                    banners=banners, want_ids=want, what=what, banner_offset=banner_offset)
                    except MapError as e:
                        last = e
                        continue
                    if best is None or lay["info"]["min_gap"] > best["info"]["min_gap"] + 1e-9:
                        best = lay
        if best is not None:
            return best
    raise MapError("skyymap %s: nothing fits at node sizes %s - last: %s" % (what, sizes, last))


def scaled(lay, z, what="map"):
    """the same map at zoom z (every coordinate x z, rounded; disc / hub / emblem sizes x z; the banners keep their size in the corners
    of the bigger canvas) - check()ed again"""
    W, H = int(round(lay["W"] * z)), int(round(lay["H"] * z))
    out = dict(W=W, H=H, node=int(round(lay["node"] * z)), emb=int(round(lay["emb"] * z)), hub=int(round(lay["hub"] * z)),
               edges=list(lay["edges"]), nodes=[], hubs=[], junctions=[], banners=[], zoom=z, banner_offset=lay.get("banner_offset", 0.0))
    for n in lay["nodes"]:
        m = dict(n)
        m["size"] = int(round(n["size"] * z))
        m["l"], m["t"] = int(round(n["cx"] * z - m["size"] / 2.0)), int(round(n["cy"] * z - m["size"] / 2.0))
        m["cx"], m["cy"] = m["l"] + m["size"] / 2.0, m["t"] + m["size"] / 2.0
        out["nodes"].append(m)
    for h in lay["hubs"]:
        m = dict(h)
        m["l"], m["t"] = int(round(h["cx"] * z - out["hub"] / 2.0)), int(round(h["cy"] * z - out["hub"] / 2.0))
        m["cx"], m["cy"] = m["l"] + out["hub"] / 2.0, m["t"] + out["hub"] / 2.0
        out["hubs"].append(m)
    by_id = dict((n["id"], n) for n in out["nodes"])
    for j in lay["junctions"]:
        m = dict(j)
        if "node" in j:
            m["x"], m["y"] = by_id[j["node"]]["cx"], by_id[j["node"]]["cy"]
        else:
            m["x"], m["y"] = j["x"] * z, j["y"] * z
        out["junctions"].append(m)
    out["emb_l"], out["emb_t"] = W // 2 - out["emb"] // 2, H // 2 - out["emb"] // 2
    for b, (bl, bt, al) in zip(lay["banners"], _corners([x["a"] + math.radians(lay.get("banner_offset", 0.0)) for x in lay["hubs"]][:len(lay["banners"])], W, H)):
        out["banners"].append(dict(key=b["key"], l=bl, t=bt, w=b["w"], h=b["h"], align=al))
    out["edge_dots"] = [[(x * z, y * z) for x, y in d] for d in lay["edge_dots"]]
    out["info"] = check(out, None, "%s at %d %%" % (what, int(round(z * 100))))
    return out


def edge_boxes(lay):
    """{edge index: (left, top, w, h)} of every drawn edge (its dots + 4 px), canvas px - the gold picture's element box (1.1: an "or"
    edge has none - it is drawn once in the base picture and never lit)"""
    out = {}
    for k, dots in enumerate(lay["edge_dots"]):
        if not dots or lay["edges"][k][2] == "or":
            continue
        xs, ys = [d[0] for d in dots], [d[1] for d in dots]
        l, t = int(math.floor(min(xs))) - 4, int(math.floor(min(ys))) - 4
        r, b = int(math.ceil(max(xs))) + 4, int(math.ceil(max(ys))) + 4
        l, t, r, b = max(0, l), max(0, t), min(lay["W"], r), min(lay["H"], b)
        out[k] = (l, t, r - l, b - t)
    return out


def scaled_boxes(boxes, z, W, H):
    """edge boxes at zoom z (the gold picture stretched with the map)"""
    out = {}
    for k, (l, t, w, h) in boxes.items():
        l2, t2 = int(math.floor(l * z)), int(math.floor(t * z))
        r2, b2 = min(W, int(math.ceil((l + w) * z))), min(H, int(math.ceil((t + h) * z)))
        out[k] = (l2, t2, r2 - l2, b2 - t2)
    return out


# ======================================================================================================== 4. PICTURES
class Pic(object):
    """an RGBA picture (straight alpha) with 'over' blending"""

    def __init__(self, w, h):
        self.w, self.h = int(w), int(h)
        self.px = bytearray(self.w * self.h * 4)

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
    """PNG bytes: RGBA 8 bit, filter 0 on every row, zlib 9 - fast in pure Python and deterministic"""
    w4 = pic.w * 4
    raw = b"".join(b"\x00" + bytes(pic.px[y * w4:(y + 1) * w4]) for y in range(pic.h))

    def chunk(typ, body):
        return struct.pack(">I", len(body)) + typ + body + struct.pack(">I", zlib.crc32(typ + body) & 0xffffffff)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", pic.w, pic.h, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def png_size(data):
    return struct.unpack(">II", data[16:24])


def disc(pic, cx, cy, r, c, a=1.0):
    """an anti-aliased filled circle (coverage = r + 0.5 - distance)"""
    for y in range(max(0, int(cy - r - 2)), min(pic.h, int(cy + r + 3))):
        for x in range(max(0, int(cx - r - 2)), min(pic.w, int(cx + r + 3))):
            cov = r + 0.5 - math.hypot(x + 0.5 - cx, y + 0.5 - cy)
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
    n = len(pts)

    def inside(x, y):
        ins = False
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


def node_picture(size_px, state, col=None, kmax=(0, 0), cap=False):
    """a disc state picture (size_px = @2x pixels; geometry in 64ths): locked (grey ring + padlock badge), soon (locked look + a '...'
    badge: the upgrade does nothing yet), open (row open, no free point: a light grey ring), ready (gold ring = can learn now), learnt
    (the tree colour ring, k of m rank pips lit along the bottom), max (all pips lit + a soft glow); cap = the capstone star on top"""
    k = size_px / 64.0
    pic = Pic(size_px, size_px)
    c = size_px / 2.0
    disc_c, lock_ring, lock_c, gold = rgb(ART["disc"]), rgb(ART["ringLocked"]), rgb(ART["lock"]), rgb(ART["gold"])
    if state == "max":
        ring(pic, c, c, 28 * k, 31.5 * k, rgb(col), 0.35)
    disc(pic, c, c, 27 * k, disc_c, 0.94)
    rc = {"locked": lock_ring, "soon": lock_ring, "ready": gold, "open": rgb(ART["open"])}.get(state, rgb(col) if col else lock_ring)
    ring(pic, c, c, 23 * k, 27.5 * k, rc, 1.0)
    if state == "ready":
        ring(pic, c, c, 20.5 * k, 22 * k, gold, 0.35)
    if state == "locked":                                          # padlock badge, bottom right
        disc(pic, 49 * k, 49 * k, 9 * k, disc_c, 1.0)
        ring(pic, 49 * k, 45 * k, 2.6 * k, 4.6 * k, lock_c, 1.0)
        poly(pic, [(43.5 * k, 46 * k), (54.5 * k, 46 * k), (54.5 * k, 55 * k), (43.5 * k, 55 * k)], lock_c, 1.0, ss=2)
    if state == "soon":                                            # "..." badge, bottom right (coming soon)
        disc(pic, 49 * k, 49 * k, 9 * k, disc_c, 1.0)
        for dx in (-4.2, 0.0, 4.2):
            disc(pic, (49 + dx) * k, 49 * k, 1.6 * k, lock_c, 1.0)
    m, lit = kmax
    if m:                                                          # rank pips along the bottom of the ring
        for i in range(m):
            a = math.radians(180 + (i - (m - 1) / 2.0) * 21)
            px_, py_ = c + 25.2 * k * math.sin(a), c - 25.2 * k * math.cos(a)
            disc(pic, px_, py_, 3.9 * k, disc_c, 1.0)
            disc(pic, px_, py_, 2.8 * k, rgb(ART["pipLit"]) if i < lit else rgb(ART["pipDim"]), 1.0)
    if cap:                                                        # capstone star badge on the top of the ring
        sc = gold if state in ("ready", "max") else lock_c
        poly(pic, star(c, 9 * k, 8.5 * k), disc_c, 1.0, ss=3)
        poly(pic, star(c, 9 * k, 6.5 * k), sc, 1.0, ss=3)
    return pic


def diamond_picture(size_px, col, opened):
    """the free perk / row ability diamond (on the branch spine): the tree colour when its row is open, grey when locked"""
    k = size_px / 44.0
    pic = Pic(size_px, size_px)
    c = size_px / 2.0
    cc = rgb(col) if (opened and col) else rgb(ART["ringLocked"])
    poly(pic, [(c, c - 20 * k), (c + 20 * k, c), (c, c + 20 * k), (c - 20 * k, c)], cc, 1.0, ss=3)
    poly(pic, [(c, c - 15 * k), (c + 15 * k, c), (c, c + 15 * k), (c - 15 * k, c)], rgb(ART["disc"]), 0.96, ss=3)
    poly(pic, [(c, c - 7 * k), (c + 7 * k, c), (c, c + 7 * k), (c - 7 * k, c)], cc, 0.9 if opened else 0.6, ss=3)
    return pic


def hub_picture(col, size_px=88):
    pic = Pic(size_px, size_px)
    k = size_px / 88.0
    c = size_px / 2.0
    disc(pic, c, c, 42 * k, rgb(ART["disc"]), 0.96)
    ring(pic, c, c, 35 * k, 42.5 * k, rgb(col), 1.0)
    ring(pic, c, c, 31 * k, 32.5 * k, rgb(col), 0.5)
    return pic


def halo_picture(size_px=88):
    pic = Pic(size_px, size_px)
    k = size_px / 88.0
    c = size_px / 2.0
    ring(pic, c, c, 36 * k, 43 * k, rgb(ART["halo"]), 0.45)
    ring(pic, c, c, 38 * k, 41 * k, rgb(ART["halo"]), 1.0)
    return pic


def emblem_picture(size_px=192):
    """the SkyWynn crest PLACEHOLDER (spec 2.6: page emblems = art round R4): a navy disc, gold rings, a 4-point gold star"""
    pic = Pic(size_px, size_px)
    k = size_px / 192.0
    c = size_px / 2.0
    gold = rgb(ART["gold"])
    disc(pic, c, c, 92 * k, rgb(ART["emblemFill"]), 1.0)
    ring(pic, c, c, 80 * k, 92 * k, gold, 1.0)
    ring(pic, c, c, 72 * k, 75 * k, gold, 0.6)
    poly(pic, star(c, c, 60 * k, inner=0.32, n=4), gold, 1.0, ss=3)
    poly(pic, star(c, c, 40 * k, inner=0.32, n=4, rot=math.pi / 4), rgb(ART["white"]), 0.85, ss=3)
    disc(pic, c, c, 11 * k, rgb(ART["emblemFill"]), 1.0)
    return pic


def base_picture(lay):
    """the whole canvas @2x: every edge as grey dotted line + a 10 px (@2x) diamond on every junction no node sits on (1.1: an "or" edge =
    gold dashes, every second pair of dots)"""
    pic = Pic(2 * lay["W"], 2 * lay["H"])
    lc = rgb(ART["line"])
    gc = rgb(ART["gold"])
    for k, dots in enumerate(lay["edge_dots"]):
        orl = lay["edges"][k][2] == "or"
        for i, (x, y) in enumerate(dots):
            if orl:
                if (i // 2) % 2 == 0:
                    disc(pic, 2 * x, 2 * y, DOT_R_GOLD, gc, 0.95)
            else:
                disc(pic, 2 * x, 2 * y, DOT_R_BASE, lc, 0.6)
    for j in lay["junctions"]:
        if "node" not in j:
            x, y = 2 * j["x"], 2 * j["y"]
            poly(pic, [(x, y - 10), (x + 10, y), (x, y + 10), (x - 10, y)], lc, 0.75, ss=3)
    return pic


# fix round 2 (critic: the ABILITY label fitted on few nodes at 100 %): the tag is baked into the square's own bottom band - every ability node
# says it at every zoom, no layout room, no kit change. A 5 x 7 pixel font (our own), only the letters the tags use.
TAG_GLYPHS = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "E": ("####", "#...", "#...", "###.", "#...", "#...", "####"),
    "I": ("###", ".#.", ".#.", ".#.", ".#.", ".#.", "###"),
    "L": ("#...", "#...", "#...", "#...", "#...", "#...", "####"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    " ": ("..", "..", "..", "..", "..", "..", ".."),
}
ABIL_TAGS = {"own": "ABILITY", "locked": "ABILITY", "picked": "IN USE", "other": "ALT"}   # the A1-alt in use / the other A1-alt


def tag_cols(text):
    """the width of a tag in font columns (1 column between letters)"""
    return sum(len(TAG_GLYPHS[ch][0]) for ch in text) + max(0, len(text) - 1)


def draw_tag(pic, text, cx, cy, sc, c):
    """a tag centred on (cx, cy), sc px a font pixel"""
    x = cx - tag_cols(text) * sc / 2.0
    y0 = cy - 7 * sc / 2.0
    for ch in text:
        g = TAG_GLYPHS[ch]
        for ry, row in enumerate(g):
            for rx, bit in enumerate(row):
                if bit == "#":
                    poly(pic, [(x + rx * sc, y0 + ry * sc), (x + (rx + 1) * sc, y0 + ry * sc), (x + (rx + 1) * sc, y0 + (ry + 1) * sc), (x + rx * sc, y0 + (ry + 1) * sc)], c, 1.0, ss=3)
        x += (len(g[0]) + 1) * sc


def ability_picture(size_px, col, state):
    """1.1: an ABILITY node (research/Class-Tree-Clarity-Spec.md 2.1): a rounded square frame - "own" (the class colour frame), "picked" (the
    A1-alt in use: the frame + a gold corner tick), "other" (the A1-alt not picked: a grey frame, the icon still drawn), "locked" (grey
    frame + padlock badge); the ability's icon sits on top (an ItemIcon), so the middle stays a dark plate. Fix round 2: the frame's bottom
    band carries a baked tag (ABIL_TAGS: ABILITY / IN USE / ALT) at every zoom."""
    k = size_px / 64.0
    pic = Pic(size_px, size_px)
    disc_c, lock_c, gold = rgb(ART["disc"]), rgb(ART["lock"]), rgb(ART["gold"])
    lit = bool(col) and state in ("own", "picked")                  # the class colour frame (else grey)
    fc = rgb(col) if lit else rgb(ART["ringLocked"])

    def rrect(x0, y0, x1, y1, r, c, a):
        pts = []
        for cx_, cy_, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
            for st in range(7):
                an = math.radians(a0 + st * 15)
                pts.append((cx_ + r * math.cos(an), cy_ + r * math.sin(an)))
        poly(pic, pts, c, a, ss=2)
    rrect(2 * k, 2 * k, 62 * k, 62 * k, 8 * k, fc, 1.0)
    rrect(7 * k, 7 * k, 57 * k, 49 * k, 6 * k, disc_c, 0.96)      # fix round 2: the plate ends at 49 - the frame's bottom band carries the tag
    tag = ABIL_TAGS[state]
    sc = min(50.0 / tag_cols(tag), 1.4) * k                        # at most 50 of the 64 px wide, 9.8 px high (the icon sits at 14..50)
    draw_tag(pic, tag, 32 * k, 55.6 * k, sc, disc_c if lit else rgb(ART["white"]))   # dark on the class colour, light on grey
    if state == "picked":                                          # gold corner tick, top right
        disc(pic, 52 * k, 12 * k, 9 * k, disc_c, 1.0)
        disc(pic, 52 * k, 12 * k, 7 * k, gold, 1.0)
        poly(pic, [(47.5 * k, 12 * k), (50 * k, 15.5 * k), (56.5 * k, 8.5 * k), (55 * k, 7.5 * k), (50 * k, 13 * k), (49 * k, 11 * k)], disc_c, 1.0, ss=3)
    if state == "locked":                                          # padlock badge, top right (fix round 2: the bottom band holds the tag)
        disc(pic, 52 * k, 12 * k, 9.5 * k, disc_c, 1.0)
        ring(pic, 52 * k, 8 * k, 2.6 * k, 4.6 * k, lock_c, 1.0)
        poly(pic, [(46.5 * k, 9 * k), (57.5 * k, 9 * k), (57.5 * k, 18 * k), (46.5 * k, 18 * k)], lock_c, 1.0, ss=2)
    return pic


def gold_pictures(lay):
    """{edge index: Pic} - one gold dotted picture per drawn edge, its box from edge_boxes(), @2x, the base's dot positions"""
    out = {}
    gold = rgb(ART["gold"])
    for k, (l, t, w, h) in sorted(edge_boxes(lay).items()):
        g = Pic(2 * w, 2 * h)
        for x, y in lay["edge_dots"][k]:
            disc(g, 2 * (x - l), 2 * (y - t), DOT_R_GOLD, gold, 1.0)
        out[k] = g
    return out


def colour_name(col):
    """a picture-name-safe word for a colour: #8fc8ff -> C8fc8ff"""
    rgb(col)
    return "C" + col[1:].lower()


def node_pictures(colours, maxes, ability=False):
    """{name: Pic} of every disc state the maps need (64 px = a 32 px disc @2x; the client scales it to the node size):
    shared Locked / Soon / Open / Ready / CapLocked / CapSoon / CapOpen / CapReady / FreeLocked; per colour (colour_name) <C>L<k><m> (k of m
    learnt), <C>Max<m>, <C>CapMax, <C>Free (an open diamond). maxes = the rank maxima in use (1..9)."""
    out = {"Locked": node_picture(64, "locked"), "Soon": node_picture(64, "soon"), "Open": node_picture(64, "open"),
           "Ready": node_picture(64, "ready"), "CapLocked": node_picture(64, "locked", cap=True), "CapSoon": node_picture(64, "soon", cap=True),
           "CapOpen": node_picture(64, "open", cap=True), "CapReady": node_picture(64, "ready", cap=True),
           "FreeLocked": diamond_picture(44, None, False)}
    for col in sorted(set(colours)):
        cn = colour_name(col)
        for m in sorted(set(maxes)):
            if not (1 <= m <= 9):
                raise MapError("skyymap: rank max %r outside 1..9 (pips)" % (m,))
            for kk in range(1, m):
                out["%sL%d%d" % (cn, kk, m)] = node_picture(64, "learnt", col, (m, kk))
            out["%sMax%d" % (cn, m)] = node_picture(64, "max", col, (m, m))
        out["%sCapMax" % cn] = node_picture(64, "max", col, (1, 1), cap=True)
        out["%sFree" % cn] = diamond_picture(44, col, True)
        if ability:   # 1.1: the ability node pictures
            out["%sAbility" % cn] = ability_picture(64, col, "own")
            out["%sAbilityPicked" % cn] = ability_picture(64, col, "picked")
    if ability:
        out["AbilityOther"] = ability_picture(64, None, "other")
        out["AbilityLocked"] = ability_picture(64, None, "locked")
    for n in out:
        if "_" in n:
            raise MapError("skyymap: picture name with an underscore: %s" % n)
    return out


def state_name(kind, col, cap, rank, mx, state):
    """the picture name of one node: kind up / free; state = TreeV3.ustate (0 locked, 1 ready, 2 owned, 3 max, 4 soon, 5 open, no
    point) for an upgrade, 1 = open / 0 = locked for a free diamond. The Java side mirrors this (TreeMap.tex)."""
    cn = colour_name(col)
    if kind == "ability":   # 1.1: state 0 locked, 1 yours, 2 the A1-alt in use, 3 the A1-alt not in use
        return {1: cn + "Ability", 2: cn + "AbilityPicked", 3: "AbilityOther"}.get(state, "AbilityLocked")
    if kind == "free":
        return (cn + "Free") if state else "FreeLocked"
    if rank >= mx:
        return (cn + "CapMax") if cap else "%sMax%d" % (cn, mx)
    if rank >= 1:
        return (cn + "CapMax") if (cap and mx == 1) else ("%sL%d%d" % (cn, rank, mx))
    pre = "Cap" if cap else ""
    return pre + {0: "Locked", 1: "Ready", 2: "Open", 3: "Ready", 4: "Soon", 5: "Open"}.get(state, "Locked")


# ======================================================================================================== 5. PREVIEW
def preview_picture(lay, states=None, cols=None):
    """a composited @1x preview of a layout: base lines, hubs, emblem, banners (boxes), discs (state colours) - for a look only"""
    pic = Pic(lay["W"], lay["H"])
    bg = (16, 22, 30)
    for i in range(0, len(pic.px), 4):
        pic.px[i], pic.px[i + 1], pic.px[i + 2], pic.px[i + 3] = bg[0], bg[1], bg[2], 255
    lc = rgb(ART["line"])
    for dots in lay["edge_dots"]:
        for x, y in dots:
            disc(pic, x, y, 0.8, lc, 0.8)
    for b in lay["banners"]:
        for x in range(b["l"], b["l"] + b["w"]):
            for y in (b["t"], b["t"] + b["h"] - 1):
                pic.blend(x, y, (90, 90, 120), 1.0)
    for h in lay["hubs"]:
        ring(pic, h["cx"], h["cy"], lay["hub"] / 2.0 - 3, lay["hub"] / 2.0, rgb(h["col"]), 1.0)
    disc(pic, lay["W"] / 2.0, lay["H"] / 2.0, lay["emb"] / 2.0, rgb(ART["emblemFill"]), 1.0)
    ring(pic, lay["W"] / 2.0, lay["H"] / 2.0, lay["emb"] / 2.0 - 4, lay["emb"] / 2.0, rgb(ART["gold"]), 1.0)
    for n in lay["nodes"]:
        r = n["size"] / 2.0
        c = rgb(n["col"])
        if n.get("abil"):   # 1.1: an ability node = a square in the tree colour
            poly(pic, [(n["cx"] - r, n["cy"] - r), (n["cx"] + r, n["cy"] - r), (n["cx"] + r, n["cy"] + r), (n["cx"] - r, n["cy"] + r)], c, 1.0, ss=2)
        elif n["kind"] == "free":
            poly(pic, [(n["cx"], n["cy"] - r), (n["cx"] + r, n["cy"]), (n["cx"], n["cy"] + r), (n["cx"] - r, n["cy"])], c, 1.0, ss=2)
        else:
            disc(pic, n["cx"], n["cy"], r, rgb(ART["disc"]), 1.0)
            ring(pic, n["cx"], n["cy"], r - 3, r, rgb(ART["gold"]) if n.get("cap") else c, 1.0)
    return pic


if __name__ == "__main__" and "--preview" in sys.argv:
    HERE = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, HERE)
    import trees_v3_data as TD
    import skyyui as SUI
    if "--v4" in sys.argv:   # 1.1: the 0.6.0 class trees (and the Adventure page without Combat)
        TD.v4_apply()
    out_dir = os.path.abspath(sys.argv[sys.argv.index("--dir") + 1]) if "--dir" in sys.argv else os.path.join(HERE, "dev", "scratch", "skyymap")
    if not os.path.realpath(out_dir).startswith(os.path.realpath(os.path.join(HERE, "dev", "scratch")) + os.sep):
        raise SystemExit("--dir: only under tools/dev/scratch/")
    os.makedirs(out_dir, exist_ok=True)
    pages = [("Gathering", ["Mining", "Foraging", "Farming", "Fishing"]), ("Crafting", ["Smithing", "Cooking", "Alchemy"]),
             ("Adventure", (["Acrobatics", "Exploration", "Beastmastery"] if "--v4" in sys.argv else ["Combat", "Acrobatics", "Exploration", "Beastmastery"]))]
    for name, trees in pages:
        lay = fit_page([(t, SUI.TREE_COLOR[t], TD.tree(t)["branches"]) for t in trees], sizes=(32, 30, 28), what=name)
        open(os.path.join(out_dir, name + ".png"), "wb").write(png(preview_picture(lay)))
        print("%s: %d nodes at %d px, min gap %.2f, params %s" % (name, lay["info"]["nodes"], lay["node"], lay["info"]["min_gap"], lay["params"]))
    for cn in ("Archer", "Warrior", "Mage", "Berserker", "Priest", "Assassin", "Monk", "Spellblade"):
        t = TD.tree(cn)
        lay = fit_page([("B%d" % i, SUI.TREE_COLOR["Class"], [b]) for i, b in enumerate(t["branches"])], sizes=(36, 32, 30, 28),
                       ring0s=(0.38, 0.34, 0.42), spacing=(16, 12, 8), starts=(0,), banner_offset=60.0, what=cn)
        open(os.path.join(out_dir, "Class" + cn + ".png"), "wb").write(png(preview_picture(lay)))
        print("%s: %d nodes at %d px, min gap %.2f, params %s" % (cn, lay["info"]["nodes"], lay["node"], lay["info"]["min_gap"], lay["params"]))
    print("previews in %s" % out_dir)
