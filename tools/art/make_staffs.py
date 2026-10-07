"""make_staffs - game-ready ASSETS for the SkyWynn metal staffs + Bo staffs (Copper .. Onyxium), 2026-10-07 (v2).

Skyy, 2026-10-07 (docs/answered/gear.md, LOCKED ART answers): "Match the wands.  New like the concept." ->
  (1) every tier uses the SAME colours as the built metal wands (tools/skyyart.py wand recipe, no own tints): metal = SA.metal_gradient
      (the tier's vanilla pickaxe head + ingot) with the wand head / band settings (SA.WAND_TUNE + SA.WAND_METAL_TUNE), bands =
      SA.band_gradient (vanilla gold trim on Mithril), crystal = SA.gem_gradient (the tier's vanilla staff gem = the wand leaf colour).
  (2) the 7 metal staffs get NEW models like the concept (research/cloud/weapon-art/staff-v2.png, make_weapons_v2.py draw_staff):
      a longer wood shaft, a black leather hand grip, a metal head CRADLE (neck + cup + riveted collar + 4 prongs) holding ONE big
      faceted crystal, bands 2 -> 5 per tier, side leaf crystals from Thorium, Cobalt fins + Adamantite spikes on the cradle, a metal
      ring round the crystal on Mithril + Onyxium, gold bands / collar / prongs / ring on Mithril.

(a) Metal staffs, own model per tier: the tier's vanilla rig nodes (R-Attachment / Origin_Projectile / Origin_Item / Handle position +
    orientation, read from Assets.zip at run time) are kept, so each staff is held, thrown and iconed like its vanilla staff; the
    Handle's own box becomes the leather grip, centred on the hand point (the R-Attachment origin on the Handle axis), and our boxes hang
    off it along the Handle x axis between the vanilla staff's butt and tip (same length -> the vanilla IconProperties fit unchanged).
    The side leaves / fins / spikes spread along the Handle axis (y or z) on which the vanilla head spreads (the side the icon shows).
(b) Bo staffs, own model (unchanged shape): the vanilla Bo_Wood rig + our boxes (wood shaft, leather centre grip, metal caps growing
    per tier, 1 -> 3 bands per end, Iron rivets, Cobalt points, Adamantite spikes, gold bands on Mithril + Onyxium, a crystal stud
    from Adamantite). Colours now = the wand recipe too (the concept tints of the first build are gone).
Textures are packed + painted from code, 1 texel per model unit (vanilla density), sizes multiples of 32; the wood colours are a gradient
sampled from the vanilla Bo_Wood texture at run time.

Every output is vanilla-derived -> ONLY models-local/art/staffs/ (git-ignored). This script holds no vanilla bytes / pixels.
Run:  python tools/art/make_staffs.py         Deterministic: two runs = same bytes (no clocks, no randomness, fixed zlib).
"""
import copy
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyyart as SA  # noqa: E402

OUT = os.path.join(ROOT, "models-local", "art", "staffs")
METALS = SA.METALS
STAFF_ITEM = "Server/Item/Items/Weapon/Staff/Weapon_Staff_%s.json"
BO_ITEM = "Server/Item/Items/Weapon/Staff/Weapon_Staff_Bo_Wood.json"
TEX_DIR = "Common/Items/Weapons/Staff"
ICON_DIR = "Common/Icons/ItemsGenerated"
STALE = ["%s/SkyyArmory_%s_Texture.png" % (TEX_DIR, m) for m in METALS]     # the v1 R1 re-textures (replaced by own models)


def hx(s):
    s = s.lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), 255)


# black leather = the approved light-armor leather ramp (research/cloud/light-armor/make_sheets.py, own colours, not vanilla)
LEATHER = [hx(c) for c in ("#0a090c", "#1c191f", "#2b2730", "#3f3946", "#58515f")]
THREAD = hx("#6b6372")


# ======================================================================================================== colours = the wand recipe
def wand_tune(metal, part):
    p = dict(SA.WAND_TUNE[part])
    p.update(SA.WAND_METAL_TUNE.get(metal, {}).get(part, {}))
    return p


def ramp(grad, n=5, lo=0.0, hi=1.0):
    return [SA.sample(grad, lo + (hi - lo) * i / (n - 1.0)) for i in range(n)]


def wood_gradient(z):
    _d, _m, tex, _i = SA.item_parts(z, BO_ITEM)
    return SA.palette_from([tex])


def tier_colours(z, metal):
    """5-step ramps (dark -> light) for wood, metal, band (trim) and crystal, from the metal-wand recipe of tools/skyyart.py:
    metal = SA.metal_gradient over the wand HEAD range, band = SA.band_gradient over the wand BANDS range, crystal = SA.gem_gradient
    over the wand LEAVES range."""
    h, b, g = wand_tune(metal, "head"), wand_tune(metal, "bands"), wand_tune(metal, "leaves")
    return {"wood": ramp(wood_gradient(z), 5, 0.1, 0.9),
            "metal": ramp(SA.metal_gradient(z, metal), 5, h["lo"], h["hi"]),
            "band": ramp(SA.band_gradient(z, metal), 5, b["lo"], b["hi"]),
            "gem": ramp(SA.gem_gradient(z, metal), 5, g["lo"], g["hi"])}


# ======================================================================================================== shared model helpers
def box(name, size, pos, children=None, rot=None):
    q = rot or (0.0, 0.0, 0.0, 1.0)
    return {"id": name, "name": name,
            "position": {"x": pos[0], "y": pos[1], "z": pos[2]},
            "orientation": {"x": q[0], "y": q[1], "z": q[2], "w": q[3]},
            "shape": {"offset": {"x": 0, "y": 0, "z": 0}, "stretch": {"x": 1, "y": 1, "z": 1}, "textureLayout": {},
                      "type": "box", "settings": {"size": {"x": size[0], "y": size[1], "z": size[2]}},
                      "unwrapMode": "custom", "visible": True, "doubleSided": False, "shadingMode": "flat"},
            "children": children or []}


def find(nodes, name):
    for n in nodes:
        if n.get("name") == name:
            return n
        r = find(n.get("children") or [], name)
        if r:
            return r
    return None


def node_frame(nodes, name, pos=(0.0, 0.0, 0.0), rot=(0.0, 0.0, 0.0, 1.0), poff=(0.0, 0.0, 0.0)):
    """(world position, world rotation) of a node, walked the way SA.model_faces walks (a parent's shape offset moves its children)."""
    for n in nodes:
        lp = SA._add(SA._xyz(n.get("position")), poff)
        o = n.get("orientation") or {}
        lq = (float(o.get("x", 0)), float(o.get("y", 0)), float(o.get("z", 0)), float(o.get("w", 1)))
        wpos, wrot = SA._add(pos, SA._qrot(rot, lp)), SA._qmul(rot, lq)
        if n.get("name") == name:
            return wpos, wrot
        r = node_frame(n.get("children") or [], name, wpos, wrot, SA._xyz((n.get("shape") or {}).get("offset")))
        if r:
            return r
    return None


def qaxis(axis, deg):
    s, c = math.sin(math.radians(deg) / 2.0), math.cos(math.radians(deg) / 2.0)
    return {"x": (s, 0.0, 0.0, c), "y": (0.0, s, 0.0, c), "z": (0.0, 0.0, s, c)}[axis]


def r4(v):
    return round(v * 10000.0) / 10000.0


# ======================================================================================================== (a) metal staffs (own model)
# per tier (concept staff-v2 / make_weapons_v2.draw_staff): bands = which band slots (grip ends outwards), leaves = side leaf crystals,
# fins = Cobalt cradle fins, spikes = Adamantite cradle spikes, ring = a metal ring round the crystal.
STAFF = {
    "Copper": {"bands": ("lo1", "hi1")},
    "Iron": {"bands": ("lo1", "hi1")},
    "Thorium": {"bands": ("lo1", "lo2", "hi1"), "leaves": True},
    "Cobalt": {"bands": ("lo1", "lo2", "hi1", "hi2"), "leaves": True, "fins": True},
    "Adamantite": {"bands": ("lo1", "lo2", "hi1", "hi2"), "leaves": True, "spikes": True},
    "Mithril": {"bands": ("lo1", "lo2", "lo3", "hi1", "hi2"), "leaves": True, "ring": True},
    "Onyxium": {"bands": ("lo1", "lo2", "lo3", "hi1", "hi2"), "leaves": True, "ring": True},
}
GRIP_LEN = 16          # leather grip length (units), centred on the hand point
BAND_STEP = 0.07       # band spacing as a share of the staff length (concept: 0.10 of 1.35)
# head layout as shares of the staff length from the butt (concept draw_staff: shaft 0 .. 0.82, cradle 0.74 .. 0.885, crystal .. 1.32
# of 1.35 total; the crystal is kept at about a quarter of the length so the head stays the size of a vanilla staff head)
NECK, CUP, COLLAR, TIP = 0.625, 0.685, 0.735, 1.0
CRYSTAL = ((0.0, 0.10, 7), (0.10, 0.25, 10), (0.25, 0.55, 13), (0.55, 0.72, 11), (0.72, 0.87, 7), (0.87, 1.0, 3))   # (from, to, width)


def staff_rig(z, metal):
    """(item dict, vanilla model dict, butt x, tip x, hand x, side axis) in the vanilla Handle frame (x = staff axis, + = head)."""
    d, mb, _tb, _ib = SA.item_parts(z, STAFF_ITEM % metal)
    model = json.loads(mb.decode("utf-8-sig"))
    hp, hq = node_frame(model["nodes"], "Handle")
    inv = (-hq[0], -hq[1], -hq[2], hq[3])

    def loc(p):
        return SA._qrot(inv, (p[0] - hp[0], p[1] - hp[1], p[2] - hp[2]))
    pts = [loc(c) for f in SA.model_faces(model) for c in f["corners"]]
    xs = [p[0] for p in pts]
    hand = loc(node_frame(model["nodes"], "R-Attachment")[0])[0]
    spread_y = max(p[1] for p in pts) - min(p[1] for p in pts)
    spread_z = max(p[2] for p in pts) - min(p[2] for p in pts)
    return d, model, round(min(xs)), round(max(xs)), round(hand), ("y" if spread_y >= spread_z else "z")


def staff_parts(metal, butt, tip, hand, side):
    """[(name, kind, size, centre (Handle frame), rotation)] - the boxes of a staff. kind: wood / leather / metal / band / gem."""
    t = STAFF[metal]
    L = float(tip - butt)
    X = lambda f: butt + f * L                                  # noqa: E731
    other = "z" if side == "y" else "y"
    out = []

    def add(name, kind, x0, x1, w, off=(0.0, 0.0), rot=None, h=None):
        p = [0.0, 0.0, 0.0]
        p["xyz".index(side)] += off[0]
        p["xyz".index(other)] += off[1]
        p[0] = (x0 + x1) / 2.0
        h = w if h is None else h                               # w = size on the side axis, h = on the other axis
        size = [x1 - x0, w, h] if side == "y" else [x1 - x0, h, w]
        out.append((name, kind, tuple(r4(v) for v in size), tuple(r4(v) for v in p), rot))

    def ray(name, kind, start, deg, segs, sgn):
        """boxes along a ray tilted deg away from the staff axis towards sgn * side: segs = [(length, width), ...], each 45-rolled."""
        tilt = qaxis("z", sgn * deg) if side == "y" else qaxis("y", -sgn * deg)
        q = SA._qmul(tilt, qaxis("x", 45))
        d = SA._qrot(tilt, (1.0, 0.0, 0.0))
        a = 0.0
        for k, (ln, w) in enumerate(segs):
            c = [start[i] + d[i] * (a + ln / 2.0) for i in range(3)]
            out.append(("%s%d" % (name, k + 1), kind, (r4(ln), w, w), tuple(r4(v) for v in c), tuple(r4(v) for v in q)))
            a += ln - 0.5

    def side_pt(x, off):
        p = [x, 0.0, 0.0]
        p["xyz".index(side)] = off
        return p

    g0, g1 = hand - GRIP_LEN / 2.0, hand + GRIP_LEN / 2.0
    # butt: metal cap + end plate
    add("ButtCap", "metal", butt + 1, butt + 7, 8)
    add("ButtEnd", "metal", butt, butt + 1, 6)
    # wood shaft: butt cap .. grip, grip .. cradle neck
    add("ShaftLo", "wood", butt + 7, g0, 6)
    add("ShaftHi", "wood", g1, round(X(NECK)), 6)
    # bands: lo1 / hi1 frame the grip, lo2 / lo3 / hi2 further out (concept: 2 -> 5 per tier)
    pos = {"lo1": g0 - 3, "lo2": g0 - 3 - BAND_STEP * L, "lo3": g0 - 3 - 2 * BAND_STEP * L, "hi1": g1, "hi2": g1 + BAND_STEP * L}
    for k in t["bands"]:
        x0 = round(pos[k])
        add("Band" + k.capitalize(), "band", x0, x0 + 3, 8)
    # cradle: neck, cup, riveted collar (band metal), 4 prongs on the crystal faces (band metal)
    n0, c0, k0 = round(X(NECK)), round(X(CUP)), round(X(COLLAR))
    add("Neck", "metal", n0, c0, 7)
    add("Cup", "metal", c0, k0, 10)
    add("Collar", "band", k0, k0 + 4, 12)
    clen = L * (TIP - COLLAR)
    p0, p1, p2 = k0 + 4, round(k0 + 0.45 * clen), round(k0 + 0.58 * clen)
    for i, (sy, sz) in enumerate(((1, 1), (1, -1), (-1, 1), (-1, -1))):
        add("Prong%d" % (i + 1), "band", p0, p1, 2.4, off=(sy * 4.6, sz * 4.6))
        add("ProngTip%d" % (i + 1), "band", p1, p2, 2, off=(sy * 3.6, sz * 3.6))
    # the big crystal: a stack of 45-rolled square boxes (diamond profile), base inside the collar
    q45 = tuple(r4(v) for v in qaxis("x", 45))
    for i, (f0, f1, w) in enumerate(CRYSTAL):
        x0 = k0 + 1 if i == 0 else round(k0 + f0 * clen)
        add("Crystal%d" % (i + 1), "gem", x0, tip if f1 >= 1.0 else round(k0 + f1 * clen), w, rot=q45)
    if t.get("ring"):                                           # a square ring round the widest part of the crystal
        r0 = round(k0 + 0.40 * clen)
        add("RingS1", "band", r0, r0 + 3, 2, off=(10, 0), h=22)
        add("RingS2", "band", r0, r0 + 3, 2, off=(-10, 0), h=22)
        add("RingO1", "band", r0, r0 + 3, 18, off=(0, 10), h=2)
        add("RingO2", "band", r0, r0 + 3, 18, off=(0, -10), h=2)
    if t.get("leaves"):                                         # two side leaf crystals growing out of the cradle
        ll = 0.12 * L
        for sgn, tag in ((1, "A"), (-1, "B")):
            ray("Leaf" + tag, "gem", side_pt(k0 + 1, sgn * 5.0), 32, [(ll * 0.6, 5), (ll * 0.45, 3)], sgn)
    if t.get("fins"):                                           # Cobalt: swept fins on the cup
        for sgn, tag in ((1, "A"), (-1, "B")):
            ray("Fin" + tag, "metal", side_pt(c0 + 1, sgn * 4.0), 62, [(0.05 * L, 3), (0.035 * L, 2)], sgn)
    if t.get("spikes"):                                         # Adamantite: two pairs of spikes on the neck + cup
        for sgn, tag in ((1, "A"), (-1, "B")):
            ray("SpikeLo" + tag, "metal", side_pt(n0 + 2, sgn * 3.0), 58, [(0.045 * L, 3), (0.03 * L, 2)], sgn)
            ray("SpikeHi" + tag, "metal", side_pt(c0 + 2, sgn * 4.5), 52, [(0.055 * L, 3), (0.04 * L, 2)], sgn)
    return out, (g0, g1)


def staff_model(vanilla, metal):
    """The vanilla rig of this tier with our boxes: the Handle box becomes the leather grip (centred on the hand point), the rest
    hang off the Handle along its x axis. Children positions are relative to the Handle position + its shape offset (engine rule)."""
    d_butt, d_tip, hand, side = vanilla["_rig"]
    m = copy.deepcopy(vanilla["model"])
    h = find(m["nodes"], "Handle")
    parts, (g0, g1) = staff_parts(metal, d_butt, d_tip, hand, side)
    sh = h["shape"]
    gc = (g0 + g1) / 2.0
    sh["type"] = "box"
    sh["offset"] = {"x": gc, "y": 0, "z": 0}
    sh["stretch"] = {"x": 1, "y": 1, "z": 1}
    sh["settings"] = {"size": {"x": GRIP_LEN, "y": 7, "z": 7}}
    sh["textureLayout"] = {}
    sh["visible"] = True
    sh["doubleSided"] = False
    kids, kinds = [], {"Handle": "leather"}
    for name, kind, size, c, rot in parts:
        kids.append(box(name, size, (r4(c[0] - gc), c[1], c[2]), rot=rot))
        kinds[name] = kind
    h["children"] = kids
    return m, kinds, side


# ======================================================================================================== (b) Bo staffs (own model)
HALF = 74          # half the vanilla Bo length (148 units along the Handle x axis)
CENTRE = 18        # where the vanilla Bo shaft is centred on the Handle x axis (Handle shape offset; children hang off it)
BO = {             # per tier: cap length, bands per end, extras
    "Copper": {"cap": 10, "bands": 1},
    "Iron": {"cap": 12, "bands": 1, "rivets": True},
    "Thorium": {"cap": 14, "bands": 2, "rivets": True},
    "Cobalt": {"cap": 16, "bands": 2, "rivets": True, "point": True},
    "Adamantite": {"cap": 18, "bands": 2, "rivets": True, "spikes": True, "stud": True},
    "Mithril": {"cap": 20, "bands": 3, "rivets": True, "gold": True, "stud": True},
    "Onyxium": {"cap": 22, "bands": 3, "rivets": True, "gold": True, "stud": True, "point": True},
}
TEX_W = 64


def bo_model(vanilla, metal):
    """The Bo rig of the vanilla Bo_Wood (kept: attachment, projectile + item origins, Handle orientation = held the same way) with our
    boxes as children of Handle. Handle frame: x = along the staff (-74 .. 74), the Handle's own box becomes the centre grip."""
    t = BO[metal]
    m = copy.deepcopy(vanilla)
    h = find(m["nodes"], "Handle")
    cap, nb, grip = t["cap"], t["bands"], 14
    sh = h["shape"]
    sh["offset"] = {"x": CENTRE, "y": 0, "z": 0}       # vanilla: the shaft centre sits 18 units along Handle x
    sh["stretch"] = {"x": 1, "y": 1, "z": 1}
    sh["settings"] = {"size": {"x": 2 * grip, "y": 7, "z": 7}}          # the leather centre grip (thicker than the shaft)
    sh["textureLayout"] = {}
    kids = []
    wood_len = HALF - cap - grip
    for s, tag in ((1, "Hi"), (-1, "Lo")):
        kids.append(box("Shaft" + tag, (wood_len, 6, 6), (s * (grip + wood_len / 2.0), 0, 0)))
        kids.append(box("Cap" + tag, (cap, 8, 8), (s * (HALF - cap / 2.0), 0, 0)))
        kids.append(box("CapEnd" + tag, (1, 6, 6), (s * (HALF + 0.5), 0, 0)))
        for i in range(nb):
            kids.append(box("Band%d%s" % (i + 1, tag), (2, 8.6, 8.6), (s * (HALF - cap - 1.5 - 3.5 * i), 0, 0)))
        if t.get("point"):
            kids.append(box("Point" + tag, (3, 3, 3), (s * (HALF + 2.5), 0, 0)))
        if t.get("spikes"):
            for k, (dy, dz) in enumerate(((1, 0), (-1, 0), (0, 1), (0, -1))):
                kids.append(box("Spike%d%s" % (k + 1, tag), (2, 2, 2), (s * (HALF - cap / 2.0), dy * 5, dz * 5)))
        kids.append(box("GripRim" + tag, (1, 7.6, 7.6), (s * (grip + 0.5), 0, 0)))
    if t.get("stud"):
        kids.append(box("Stud", (3, 3, 1), (0, 0, 3.6)))
        kids.append(box("Stud2", (3, 3, 1), (0, 0, -3.6)))
    h["children"] = kids
    return m


# ======================================================================================================== texture packing + painting
FACE_WH = {"front": ("x", "y"), "back": ("x", "y"), "left": ("z", "y"), "right": ("z", "y"), "top": ("x", "z"), "bottom": ("x", "z")}


def all_boxes(nodes, out):
    for n in nodes:
        if (n.get("shape") or {}).get("type") == "box":
            out.append(n)
        all_boxes(n.get("children") or [], out)
    return out


def pack(model):
    """Shelf-pack every box face (long faces first). Faces longer than the atlas width are laid with angle 90 (along v).
    Returns {(node, face): (x, y, w, h, rotated)} and the atlas height (multiple of 32)."""
    rects = []
    for n in all_boxes(model["nodes"], []):
        size = n["shape"]["settings"]["size"]
        for f, (a, b) in FACE_WH.items():
            w, h = int(math.ceil(size[a] - 1e-6)), int(math.ceil(size[b] - 1e-6))
            rot = w > TEX_W
            rects.append((n["name"], f, h if rot else w, w if rot else h, rot))
    rects.sort(key=lambda r: (-r[3], -r[2], r[0], r[1]))
    place, x, y, row = {}, 0, 0, 0
    for name, f, w, h, rot in rects:
        if x + w > TEX_W:
            x, y, row = 0, y + row, 0
        place[(name, f)] = (x, y, w, h, rot)
        x += w
        row = max(row, h)
    height = ((y + row + 31) // 32) * 32
    for n in all_boxes(model["nodes"], []):
        lay = {}
        for f in FACE_WH:
            px, py, w, h, rot = place[(n["name"], f)]
            if rot:      # angle 90: face (u, v) -> texel offset + (-v, u); offset at the right edge of the rect
                lay[f] = {"offset": {"x": px + w, "y": py}, "mirror": {"x": False, "y": False}, "angle": 90}
            else:
                lay[f] = {"offset": {"x": px, "y": py}, "mirror": {"x": False, "y": False}, "angle": 0}
        n["shape"]["textureLayout"] = lay
    return place, height


def noise(x, y, seed):
    h = (x * 374761393 + y * 668265263 + seed * 2147483647) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 65535.0


def mix(a, b, t):
    return tuple(a[k] + (b[k] - a[k]) * t for k in range(3)) + (255,)


class Face(object):
    """Paint a face in FACE coordinates: u along the box's first size axis (the staff length on side faces), v across."""

    def __init__(self, img, seed, model_layout, wh):
        self.img, self.seed, self.lay = img, seed, model_layout
        self.w, self.h = wh

    def put(self, u, v, c):
        if 0 <= u < self.w and 0 <= v < self.h:
            tu, tv = SA.uv_point(self.lay, u + 0.5, v + 0.5)
            self.img.put(int(math.floor(tu)), int(math.floor(tv)), (c[0], c[1], c[2], 255))


def paint_wood(f, W, along):
    """Plain grained wood in the vanilla Bo wood colours (W = 5-step ramp): long streaks down the staff, lit edge, shaded edge."""
    L = f.w if along == "u" else f.h
    C = f.h if along == "u" else f.w
    for a in range(L):
        for c in range(C):
            streak = noise(c, (a + f.seed) // 7, f.seed) * 0.5 + noise(c, (a + f.seed + 3) // 3, f.seed + 1) * 0.25
            t = 0.25 + 0.5 * streak
            if c == 0 and C > 2:
                t += 0.2
            elif c == C - 1 and C > 2:
                t -= 0.2
            if noise(a, c, f.seed + 9) > 0.97:
                t -= 0.25                              # small knots / pores
            t = min(max(t, 0.0), 1.0) * 3.999
            i = int(t)
            col = mix(W[i], W[i + 1], t - i)
            f.put(a if along == "u" else c, c if along == "u" else a, col)


def paint_metal(f, M, along, seed_rivets=False, engrave=False, studs=False):
    """Metal: light top edge, dark bottom edge, brushed along the staff, a few pits, optional engraved line, rivets or a stud row."""
    L = f.w if along == "u" else f.h
    C = f.h if along == "u" else f.w
    for a in range(L):
        for c in range(C):
            t = c / max(1.0, C - 1.0)
            base = mix(M[3], M[1], t)
            col = mix(base, M[2], 0.2 + 0.3 * noise(a // 2, c, f.seed))
            if noise(a, c, f.seed + 11) > 0.95:
                col = M[1]
            if C > 2 and c == 0:
                col = M[4]
            elif C > 2 and c == C - 1:
                col = M[0]
            if L > 6 and a in (0, L - 1):
                col = M[1] if c else M[3]
            if engrave and L > 7 and a == L // 2 and 0 < c < C - 1:
                col = M[0]
            f.put(a if along == "u" else c, c if along == "u" else a, col)
    if seed_rivets and L > 7 and C >= 5:
        for a in (2, L - 3):
            cc = C // 2
            for (da, dc, k) in ((0, 0, 4), (1, 0, 3), (0, 1, 2), (1, 1, 0)):
                aa, c2 = a + da - (1 if a > L // 2 else 0), cc + dc - 1
                f.put(aa if along == "u" else c2, c2 if along == "u" else aa, M[k])
    if studs and L >= 3 and C >= 6:                    # the collar rivets (concept: 3 rivets on the cradle collar)
        a = L // 2
        for c in range(2, C - 2, 3):
            for (da, dc, k) in ((-1, 0, 4), (0, 0, 3), (-1, 1, 2), (0, 1, 0)):
                aa, c2 = a + da, c + dc
                f.put(aa if along == "u" else c2, c2 if along == "u" else aa, M[k])


def paint_leather(f, along):
    L = f.w if along == "u" else f.h
    C = f.h if along == "u" else f.w
    for a in range(L):
        for c in range(C):
            col = mix(LEATHER[2], LEATHER[3], noise(a, c, f.seed) * 0.4)
            if (a + c) % 4 == 0:                       # diagonal wrap seams
                col = LEATHER[1]
            elif (a + c) % 4 == 1:
                col = mix(LEATHER[3], LEATHER[4], 0.3)
            if c == 0:
                col = mix(col, LEATHER[4], 0.5)
            if c == C - 1:
                col = LEATHER[0]
            if a % 4 == 2 and c in (1, C - 2):          # stitches
                col = THREAD
            f.put(a if along == "u" else c, c if along == "u" else a, col)


def paint_gem(f, G):
    """Small square gem (Bo stud): light top-left rim, dark bottom-right rim, a sparkle."""
    for v in range(f.h):
        for u in range(f.w):
            col = G[2]
            if u == 0 or v == 0:
                col = G[4]
            elif u == f.w - 1 or v == f.h - 1:
                col = G[1]
            elif u == 1 and v == 1:
                col = G[4]
            f.put(u, v, col)


def paint_crystal(f, G, face, along):
    """Faceted crystal face (concept facet_paint): a lit half and a shaded half split by a bright ridge down the long axis, darker
    seams at the segment ends, the faces under the light (top / front) one step lighter than those away from it."""
    L = f.w if along == "u" else f.h
    C = f.h if along == "u" else f.w
    lift = {"top": 1, "front": 1, "right": 1, "back": 0, "left": 0, "bottom": -1}[face]
    for a in range(L):
        for c in range(C):
            if along == "v":                          # end caps: a small facet star
                k = 2 + lift + (1 if (a + c) == (L + C) // 2 - 1 else 0)
            else:
                mid = (C - 1) / 2.0
                if abs(c - mid) < 0.6:
                    k = 4 if a < L * 0.7 else 3        # the ridge
                elif c < mid:
                    k = 3 if noise(a // 3, c, f.seed) > 0.25 else 2
                else:
                    k = 1 if noise(a // 3, c, f.seed) > 0.4 else 2
                k += lift
                if a == L - 1 and L > 3 and c != int(mid):
                    k -= 1                            # facet edge where the crystal steps in
            k = min(max(k, 0), 4)
            f.put(a if along == "u" else c, c if along == "u" else a, G[k])
    if along == "u" and L > 5 and C > 3 and lift > 0:
        f.put(1, 1, G[4])                             # sparkle


def paint_texture(model, place, height, kinds, P, extra=None):
    """Paint every packed face by its part kind (kinds: node name -> wood / leather / metal / band / gem / cap ...)."""
    img = SA.Img(TEX_W, height)
    sizes = dict((n["name"], n["shape"]["settings"]["size"]) for n in all_boxes(model["nodes"], []))
    lays = dict((n["name"], n["shape"]["textureLayout"]) for n in all_boxes(model["nodes"], []))
    for i, ((name, face), (px, py, w, h, rot)) in enumerate(sorted(place.items())):
        a, b = FACE_WH[face]
        wh = (int(math.ceil(sizes[name][a] - 1e-6)), int(math.ceil(sizes[name][b] - 1e-6)))
        f = Face(img, i * 7 + 3, lays[name][face], wh)
        side = face in ("front", "back", "top", "bottom")    # u runs along the staff (box x axis) on these faces
        along = "u" if side else "v"
        kind = kinds[name]
        if kind == "wood":
            paint_wood(f, P["wood"], along)
        elif kind == "leather":
            paint_leather(f, along)
        elif kind == "metal":
            paint_metal(f, P["metal"], along)
        elif kind == "band":
            paint_metal(f, P["band"], along, studs=name == "Collar" and side)
        elif kind == "gem":
            paint_crystal(f, P["gem"], face, along)
        elif extra:
            extra(f, name, kind, side, along)
        else:
            raise SystemExit("unpainted box %s (%s)" % (name, kind))
    if (img.w % 32) or (img.h % 32):
        raise SystemExit("texture size %dx%d is not a multiple of 32" % (img.w, img.h))
    return SA.png_encode(img)


def bo_texture(z, metal, model, place, height, P):
    t = BO[metal]
    B = ramp(SA.band_gradient(z, "Mithril"), 5, 0.1, 0.9) if t.get("gold") else P["band"]   # concept Q5: gold on Mithril + Onyxium
    kinds = {}
    for n in all_boxes(model["nodes"], []):
        nm = n["name"]
        kinds[nm] = ("wood" if nm.startswith("Shaft") else "leather" if nm == "Handle" else
                     "bocap" if nm.startswith(("Cap", "Point", "Spike")) else "boband" if nm.startswith("Band") else
                     "metal" if nm.startswith("GripRim") else "stud" if nm.startswith("Stud") else "?")

    def extra(f, name, kind, side, along):
        if kind == "bocap":
            paint_metal(f, P["metal"], along, seed_rivets=t.get("rivets") and name.startswith("Cap") and side,
                        engrave=name.startswith("Cap") and t["cap"] >= 12)
        elif kind == "boband":
            paint_metal(f, B, along)
        elif kind == "stud":
            paint_gem(f, P["gem"])
        else:
            raise SystemExit("unpainted box %s" % name)
    return paint_texture(model, place, height, kinds, P, extra)


# ======================================================================================================== output
def write(rel, data):
    p = os.path.join(OUT, rel.replace("/", os.sep))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as fh:
        fh.write(data)
    return "models-local/art/staffs/" + rel


def contact_sheet(icons, cols=7):
    """Every icon at 2x on a dark slot (vanilla-like inventory slot), no labels: row 1 = the built metal wands (colour reference,
    not shipped here), row 2 = staffs, row 3 = Bo staffs."""
    S, pad = 128, 12
    rows = (len(icons) + cols - 1) // cols
    W, H = cols * (S + pad) + pad, rows * (S + pad) + pad
    img = SA.Img(W, H)
    bg, slot, rim = (24, 26, 34), (44, 48, 60), (66, 72, 88)
    for y in range(H):
        for x in range(W):
            img.put(x, y, bg + (255,))
    for k, png in enumerate(icons):
        ic = SA.png_decode(png)
        ox, oy = pad + (k % cols) * (S + pad), pad + (k // cols) * (S + pad)
        for y in range(S):
            for x in range(S):
                base = rim if x in (0, S - 1) or y in (0, S - 1) else slot
                r, g, b, a = ic.get(x // 2, y // 2)          # premultiplied
                fa = a / 255.0
                img.put(ox + x, oy + y, (r + base[0] * (1 - fa), g + base[1] * (1 - fa), b + base[2] * (1 - fa), 255))
    return SA.png_encode(img)


def main():
    SA.verify(quiet=True)
    z = SA.assets()
    manifest, notes = [], {}
    wand_icons, staff_icons, bo_icons = [], [], []
    checks = {}
    pal = dict((m, tier_colours(z, m)) for m in METALS)
    for metal in METALS:                                 # (a)
        d, vmodel, butt, tip, hand, side = staff_rig(z, metal)
        props = d["IconProperties"]
        _d, vmb, vtex, vicon = SA.item_parts(z, STAFF_ITEM % metal)
        ec, ea = SA.check_icon(vmb, vtex, props, vicon)       # the renderer on THIS tier's vanilla staff + view first
        checks[metal] = (round(ec, 2), round(ea, 2), props["Rotation"])
        model, kinds, side = staff_model({"model": vmodel, "_rig": (butt, tip, hand, side)}, metal)
        place, height = pack(model)
        tex = paint_texture(model, place, height, kinds, pal[metal])
        icon = SA.render_icon(model, tex, props, 64)
        mj = (json.dumps(model, indent=2) + "\n").encode("utf-8")
        mp = write("%s/SkyyArmory_Staff_%s.blockymodel" % (TEX_DIR, metal), mj)
        tp = write("%s/SkyyArmory_Staff_%s_Texture.png" % (TEX_DIR, metal), tex)
        ip = write("%s/SkyyArmory_Staff_%s.png" % (ICON_DIR, metal), icon)
        staff_icons.append(icon)
        t = STAFF[metal]
        extras = [x for x, k in (("side leaf crystals", "leaves"), ("cradle fins", "fins"), ("cradle spikes", "spikes"),
                                 ("ring round the crystal", "ring")) if t.get(k)]
        manifest.append({
            "item": "Weapon_Staff_%s" % metal, "tier": metal,
            "model_path": mp,
            "model_base": "own boxes on the vanilla rig (R-Attachment / Origin_Projectile / Origin_Item / Handle position + orientation "
                          "copied from Common/Items/Weapons/Staff/%s.blockymodel)" % metal,
            "texture_path": tp, "icon_path": ip,
            "item_json": "keep Weapon_Staff_%s's IconProperties %s; Model / Texture / Icon -> the three files above" % (metal, json.dumps(props)),
            "notes": "concept staff-v2 head: wood shaft (butt %d .. tip %d on the Handle axis = the vanilla length %d), %d-unit black leather "
                     "grip centred on the hand point (Handle x %d), metal cradle (neck + cup + riveted collar + 4 prongs), one big "
                     "faceted crystal; %d band(s)%s%s; side axis %s. Texture %dx%d (1 texel / unit). Colours = the metal-wand recipe "
                     "(SA.metal_gradient head range, SA.band_gradient%s, SA.gem_gradient). check_icon on the vanilla %s staff: "
                     "colour %.2f, alpha %.2f / 255."
                     % (butt, tip, tip - butt, GRIP_LEN, hand, len(t["bands"]), ", " if extras else "", ", ".join(extras), side,
                        TEX_W, height, " = vanilla gold trim" if metal == "Mithril" else "", metal, ec, ea)})
        wtex, wicon = SA.wand_art(z, metal, "B")
        wand_icons.append(wicon)
    bd, _bm, _bt, _bi = SA.item_parts(z, BO_ITEM)
    vanilla_bo = json.loads(z.read("Common/" + bd["Model"]).decode("utf-8-sig"))
    for metal in METALS:                                 # (b)
        model = bo_model(vanilla_bo, metal)
        place, height = pack(model)
        tex = bo_texture(z, metal, model, place, height, pal[metal])
        icon = SA.render_icon(model, tex, bd["IconProperties"], 64)
        mj = (json.dumps(model, indent=2) + "\n").encode("utf-8")
        mp = write("%s/SkyyArmory_Bo_%s.blockymodel" % (TEX_DIR, metal), mj)
        tp = write("%s/SkyyArmory_Bo_%s_Texture.png" % (TEX_DIR, metal), tex)
        ip = write("%s/SkyyArmory_Bo_%s.png" % (ICON_DIR, metal), icon)
        bo_icons.append(icon)
        t = BO[metal]
        manifest.append({
            "item": "SkyyArmory_Bo_%s" % metal, "tier": metal,
            "model_path": mp, "model_base": "own (rig nodes R-Attachment/Origin_Projectile/Origin_Item/Handle copied from "
                                            "Common/Items/Weapons/Staff/Bo_Wood.blockymodel)",
            "texture_path": tp, "icon_path": ip,
            "notes": "own boxes, texture %dx%d; cap %d units, %d band(s) per end%s%s%s%s%s; IconProperties = vanilla Bo_Wood %s. "
                     "Colours = the metal-wand recipe%s."
                     % (TEX_W, height, t["cap"], t["bands"], ", gold bands" if t.get("gold") else "",
                        ", rivets" if t.get("rivets") else "", ", pointed tips" if t.get("point") else "",
                        ", cap spikes" if t.get("spikes") else "", ", crystal stud on grip" if t.get("stud") else "",
                        json.dumps(bd["IconProperties"]), " (gold bands = the vanilla Mithril gold trim)" if t.get("gold") else "")})
    bo_vanilla = SA.check_icon(SA._read(z, bd["Model"]), SA._read(z, bd["Texture"]), bd["IconProperties"],
                               SA._read(z, bd["Icon"]))
    for rel in STALE:
        p = os.path.join(OUT, rel.replace("/", os.sep))
        if os.path.exists(p):
            os.remove(p)
    write("sheet.png", contact_sheet(wand_icons + staff_icons + bo_icons))
    write("manifest.json", (json.dumps(manifest, indent=2) + "\n").encode("utf-8"))
    z.close()
    for m, c in checks.items():
        print("check_icon vanilla staff %-10s colour %6.2f alpha %5.2f rotation %s" % (m, c[0], c[1], c[2]))
    print("check_icon vanilla Bo_Wood       colour %6.2f alpha %5.2f" % bo_vanilla)
    print("wrote %d items to %s" % (len(manifest), OUT))


if __name__ == "__main__":
    main()
