"""make_soulcage - game-ready ASSETS for the 7 Soul Cages (Copper .. Onyxium), route R3: own model + own texture + a looping spin.

Concept (approved by Skyy, "the accessories, weapons, and fishing stuff are all ready to make", 2026-10-07):
research/cloud/weapon-art/soul-cage-v2.png + soul-cage-spin-v2.gif (make_weapons_v2.py draw_cage), research/cloud/Soul-Orb-Spec.md 1:
a glowing soul ball inside a dodecahedron lattice in the tier metal; of the 20 corners the front-most N are gems = tethers
2 / 4 / 6 / 10 / 14 / 16 / 20; soul + gems in the tier ESSENCE colour. Skyy lock (docs/answered/gear.md WEAPONS 2026-10-06): the cage
FLOATS above the palm and slowly SPINS round the soul.

What this writes (all under models-local/art/soulcage/, git-ignored: the colours are sampled from vanilla art at run time):
  Common/Items/Weapons/SoulCage/SkyyArmory_<Metal>.blockymodel      own geometry (boxes), 64 units / block, one per tier (gem count)
  Common/Items/Weapons/SoulCage/SkyyArmory_<Metal>_Texture.png      own 64x32 texture painted from code (same UV layout every tier)
  Common/Items/Weapons/SoulCage/SkyyArmory_SoulCage_Spin.blockyanim  looping turn of the node "Cage" about +Y (soul stays still)
  Common/Icons/ItemsGenerated/SkyyArmory_SoulCage_<Metal>.png       64x64 icon (skyyart.render_icon, premultiplied)
  sheet.png, spin-preview.png, preview-<Metal>.png, manifest.json

No vanilla pixels or bytes live in this file: it reads Assets.zip (read-only) at run time only for colour gradients
(metal = skyyart.metal_gradient = the tier's vanilla pickaxe head + ingot; essence = the vanilla essence / crystal / voidheart texture;
Mithril finial trim = skyyart.band_gradient = the vanilla Mithril staff's gold band). Deterministic: two runs give the same bytes.

Run:  python tools/art/make_soulcage.py
"""
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyyart as SA  # noqa: E402

OUT = os.path.join(ROOT, "models-local", "art", "soulcage")
ITEM_DIR = "Common/Items/Weapons/SoulCage"
ICON_DIR = "Common/Icons/ItemsGenerated"
ANIM_PATH = ITEM_DIR + "/SkyyArmory_SoulCage_Spin.blockyanim"

METALS = SA.METALS                                   # Copper, Iron, Thorium, Cobalt, Adamantite, Mithril, Onyxium
TETHERS = (2, 4, 6, 10, 14, 16, 20)                  # Soul-Orb-Spec 1 (gems = tethers)
LEVELS = ("10-18", "15-23", "20-28", "25-38", "35-43", "40-49", "40-49")   # Onyxium = level 40 (docs/answered/gear.md locks
# 2026-09-30 / 10-01 + the concept caption); Soul-Orb-Spec 1 still says "50+ (later)" - reported to Skyy
# soul + gem colour = the tier's essence (Soul-Orb-Spec 1), sampled from the vanilla texture of that essence. Mithril (Wind / Zephyr
# essence: no such vanilla item) uses the spec's own fallback, the White crystal shard; Onyxium (Voidheart) the vanilla Voidheart.
ESSENCE = (
    ("Life", "Resources/Ingredients/Essence_Textures/Life_Essence_Texture.png"),
    ("Fire", "Resources/Ingredients/Essence_Textures/Fire_Essence_Texture.png"),
    ("Ice", "Resources/Ingredients/Essence_Textures/Ice_Essence_Texture.png"),
    ("Lightning", "Resources/Ingredients/Essence_Textures/Lightning_Essence_Texture.png"),
    ("Void", "Resources/Ingredients/Essence_Textures/Void_Essence_Texture.png"),
    ("Wind (White crystal fallback, mint tint)", "Resources/Crystals/Crystal_Fragment_Textures/White.png"),
    ("Voidheart", "Resources/Ingredients/Voidheart_Texture.png"),
)
# per tier: (metal lo, metal hi) = which part of the vanilla metal gradient the bars use (Onyxium is near-black: lift it so the
# lattice still reads, like the wand recipe does), (essence lo, hi) for the soul / gems
METAL_SPAN = {"Onyxium": (0.3, 1.0), "Iron": (0.05, 1.0), "Mithril": (0.0, 0.65)}
ESS_SPAN = {"Voidheart": (0.3, 1.0), "Void": (0.10, 1.0)}
# hue tints (target rgb, strength 0..1), luminance kept: the vanilla source keeps the shading, the concept sets the hue. Mithril
# metal -> the concept's cyan lattice (#7ec4cc, make_weapons_v2 Mithril ramp mid); Mithril essence (White crystal fallback) -> the
# concept's mint "white-green" wind soul. Concept hex values only, no vanilla pixels.
METAL_TINT = {"Mithril": ((0x7e, 0xc4, 0xcc), 0.75)}
ESS_TINT = {"Wind (White crystal fallback, mint tint)": ((0x9c, 0xf0, 0xc0), 0.7)}

# ------------------------------------------------------------------------------------------------------------------ geometry
R_CIRC = 12.5             # cage circumradius in model units (64 / block): the cage is ~25 units = about 0.4 block across
FLOAT_Y = 22.0             # the float: soul centre above the grip point (R-Attachment); cage bottom cap ~8 units over the fist
BAR = (2, 2, 9)            # lattice bar (z = along the edge; edge length 8.9 so the ends tuck into the corner knobs)
KNOB = (3, 3, 3)           # bare metal corner
GEM = (4, 4, 4)            # tether gem: a cube stood on its corner (one corner points straight out) = a diamond point
SOUL = 7                   # two 7-cubes turned against each other = a round-ish soul, about half the cage across (concept)
FIN = (3, 4, 3)            # spin-axis finial (top + bottom face centre), with a 2-cube cap and 5 spokes to the face corners
CAP = (2, 2, 2)
SPIN_FRAMES = 660          # 60 frames / s: one full turn in 11 s (= the concept GIF's 72 deg per ~2.2 s)
SPIN_KEYS = 4              # 90 deg per key step (each step < 180 deg so the quaternion path is unambiguous)

TEX_W, TEX_H = 64, 32
# UV atlas: rect name -> (x, y, w, h); shared by every box of that part (one painted look per part, like vanilla re-use)
UV = {
    "bar_side": (0, 0, 9, 2), "bar_top": (0, 4, 2, 9), "bar_end": (4, 4, 2, 2),
    "knob": (8, 4, 3, 3),
    "gem_tip": (12, 4, 4, 4), "gem_side": (17, 4, 4, 4), "gem_top": (22, 4, 4, 4),
    "fin_side": (26, 4, 3, 4), "fin_top": (30, 4, 3, 3), "cap": (34, 4, 2, 2),
    "soul_a": (0, 15, 7, 7), "soul_b": (8, 15, 7, 7),
}
FACES_OF = {   # part -> {face: uv rect}
    "bar": {"front": "bar_end", "back": "bar_end", "left": "bar_side", "right": "bar_side", "top": "bar_top", "bottom": "bar_top"},
    "knob": dict((f, "knob") for f in ("front", "back", "left", "right", "top", "bottom")),
    "gem": {"front": "gem_tip", "back": "gem_tip", "left": "gem_side", "right": "gem_side", "top": "gem_top", "bottom": "gem_top"},
    "fin": {"front": "fin_side", "back": "fin_side", "left": "fin_side", "right": "fin_side", "top": "fin_top", "bottom": "fin_top"},
    "cap": dict((f, "cap") for f in ("front", "back", "left", "right", "top", "bottom")),
    "soul_a": dict((f, "soul_a") for f in ("front", "back", "left", "right", "top", "bottom")),
    "soul_b": dict((f, "soul_b") for f in ("front", "back", "left", "right", "top", "bottom")),
}
GLOW_PARTS = ("gem", "soul_a", "soul_b")     # shadingMode fullbright (the vanilla essence / Crystal Flame gem use it); metal = flat

ICON_PROPS = {"Scale": 0.8, "Rotation": [22.5, 0, 0], "Translation": [0, -FLOAT_Y]}


def r6(v):
    v = round(float(v), 5)
    return 0 if v == 0 else (int(v) if v == int(v) else v)


def v_add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def v_sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def v_mul(a, k):
    return (a[0] * k, a[1] * k, a[2] * k)


def v_dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def v_cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def v_norm(a):
    n = math.sqrt(v_dot(a, a))
    return (a[0] / n, a[1] / n, a[2] / n)


def quat_from_axes(ex, ey, ez):
    """Unit quaternion (x, y, z, w) of the rotation whose matrix columns are the orthonormal axes ex, ey, ez."""
    m00, m10, m20 = ex
    m01, m11, m21 = ey
    m02, m12, m22 = ez
    tr = m00 + m11 + m22
    if tr > 0:
        s = math.sqrt(tr + 1.0) * 2
        q = ((m21 - m12) / s, (m02 - m20) / s, (m10 - m01) / s, 0.25 * s)
    elif m00 > m11 and m00 > m22:
        s = math.sqrt(1.0 + m00 - m11 - m22) * 2
        q = (0.25 * s, (m01 + m10) / s, (m02 + m20) / s, (m21 - m12) / s)
    elif m11 > m22:
        s = math.sqrt(1.0 + m11 - m00 - m22) * 2
        q = ((m01 + m10) / s, 0.25 * s, (m12 + m21) / s, (m02 - m20) / s)
    else:
        s = math.sqrt(1.0 + m22 - m00 - m11) * 2
        q = ((m02 + m20) / s, (m12 + m21) / s, 0.25 * s, (m10 - m01) / s)
    if q[3] < 0:
        q = (-q[0], -q[1], -q[2], -q[3])
    return q


def frame(ez, up):
    """Axes with z = ez and y as close to `up` as possible."""
    ez = v_norm(ez)
    ey = v_sub(up, v_mul(ez, v_dot(up, ez)))
    if v_dot(ey, ey) < 1e-9:
        ey = v_sub((1, 0, 0), v_mul(ez, ez[0]))
    ey = v_norm(ey)
    ex = v_cross(ey, ez)
    return ex, ey, ez


def axis_quat(axis, deg):
    s = math.sin(math.radians(deg) / 2.0)
    a = v_norm(axis)
    return (a[0] * s, a[1] * s, a[2] * s, math.cos(math.radians(deg) / 2.0))


def qmul(a, b):
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return (aw * bx + ax * bw + ay * bz - az * by, aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw, aw * bw - ax * bx - ay * by - az * bz)


def dodecahedron():
    """20 vertices (model frame: +Y up, +Z front) + 30 edges, turned so a 5-fold (face) axis is vertical = the spin axis, and the
    concept's gem order (make_weapons_v2.py: front-most first, then top-most, then left-most) as `order`. Note: the concept's own
    turn put a VERTEX on top (3-fold axis); this one puts a pentagon face on top as the concept README describes."""
    phi = (1 + 5 ** 0.5) / 2
    v = [(x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
    for a in (-1, 1):
        for b in (-1, 1):
            v += [(0, a / phi, b * phi), (a / phi, b * phi, 0), (a * phi, 0, b / phi)]
    e = [(i, j) for i in range(20) for j in range(i + 1, 20) if abs(math.dist(v[i], v[j]) - 2 / phi) < 1e-6]
    # turn about X so the face normal (0, phi, 1) points straight up: a 5-fold axis = the spin axis (top + bottom = pentagons)
    ang = math.atan2(-1.0, phi)
    ca, sa = math.cos(ang), math.sin(ang)
    k = R_CIRC / math.sqrt(3.0)
    model = [(x * k, (y * ca - z * sa) * k, (y * sa + z * ca) * k) for x, y, z in v]
    # gem order as the concept: front-most first (+Z), then top-most (+Y), then left-most (-X)
    order = sorted(range(20), key=lambda i: (round(-model[i][2], 6), round(-model[i][1], 6), round(model[i][0], 6)))
    return model, e, order


def shape(kind, size, part, stretch=(1, 1, 1)):
    lay = {}
    if part:
        for f, rect in FACES_OF[part].items():
            x, y, _w, _h = UV[rect]
            lay[f] = {"offset": {"x": x, "y": y}, "mirror": {"x": False, "y": False}, "angle": 0}
    s = {"type": kind, "offset": {"x": 0, "y": 0, "z": 0},
         "stretch": {"x": r6(stretch[0]), "y": r6(stretch[1]), "z": r6(stretch[2])}}
    if kind == "none":
        s["settings"] = {}
    else:
        s["settings"] = {"size": {"x": size[0], "y": size[1], "z": size[2]}}
    s.update({"visible": True, "doubleSided": False,
              "shadingMode": "fullbright" if part in GLOW_PARTS else ("flat" if part else "standard"),
              "unwrapMode": "custom", "textureLayout": lay})
    return s


class Ids(object):
    def __init__(self):
        self.n = 0

    def next(self):
        self.n += 1
        return str(self.n - 1)


def node(ids, name, pos=(0, 0, 0), quat=(0, 0, 0, 1), kind="none", size=None, part=None, stretch=(1, 1, 1), children=None):
    return {"id": ids.next(), "name": name, "children": children or [],
            "position": {"x": r6(pos[0]), "y": r6(pos[1]), "z": r6(pos[2])},
            "orientation": {"x": r6(quat[0]), "y": r6(quat[1]), "z": r6(quat[2]), "w": r6(quat[3])},
            "shape": shape(kind, size, part, stretch)}


def build_model(tier):
    """The cage of tier index `tier`: R-Attachment > Float > (Soul, SoulB, Cage > bars + corners + finials)."""
    verts, edges, order = dodecahedron()
    gems = set(order[:TETHERS[tier]])
    ids = Ids()
    root = node(ids, "R-Attachment")
    root["shape"]["settings"] = {"isPiece": True}
    root["shape"]["doubleSided"] = True
    flt = node(ids, "Float", (0, FLOAT_Y, 0))
    root["children"].append(flt)
    flt["children"].append(node(ids, "Soul", quat=qmul(axis_quat((0, 1, 0), 45), axis_quat((1, 0, 0), 35.26)),
                                kind="box", size=(SOUL, SOUL, SOUL), part="soul_a"))
    flt["children"].append(node(ids, "SoulB", quat=qmul(axis_quat((0, 0, 1), 45), axis_quat((1, 0, 0), -20)),
                                kind="box", size=(SOUL, SOUL, SOUL), part="soul_b"))
    cage = node(ids, "Cage")                       # the spinning node (SkyyArmory_SoulCage_Spin.blockyanim)
    flt["children"].append(cage)
    kids = cage["children"]
    for n, (i, j) in enumerate(edges):
        a, b = verts[i], verts[j]
        mid = v_mul(v_add(a, b), 0.5)
        axes = frame(v_sub(b, a), mid)             # bar y axis points outward: its "top" face is the outer face
        kids.append(node(ids, "Bar%02d" % n, mid, quat_from_axes(*axes), "box", BAR, "bar"))
    for i in range(20):
        p = verts[i]
        axes = frame(p, (0, 1, 0))
        if i in gems:
            corner = quat_from_axes(*frame((1, 1, 1), (0, 1, 0)))           # local z -> the cube's body diagonal
            q = qmul(quat_from_axes(*axes), (-corner[0], -corner[1], -corner[2], corner[3]))   # diagonal -> outward
            kids.append(node(ids, "Gem%02d" % i, v_add(p, v_mul(v_norm(p), 0.5)), q, "box", GEM, "gem"))
        else:
            kids.append(node(ids, "Knob%02d" % i, p, quat_from_axes(*axes), "box", KNOB, "knob"))
    # finials on the spin axis: the top / bottom faces are pentagons, centre at +-inradius; 5 spokes to each pentagon's corners
    top_y = max(p[1] for p in verts)
    r_in = (sum(p[1] for p in verts if abs(p[1] - top_y) < 1e-4)) / 5.0
    for tag, sgn in (("Top", 1), ("Bottom", -1)):
        c = (0, sgn * r_in, 0)
        kids.append(node(ids, "Finial" + tag, (0, sgn * (r_in + FIN[1] / 2.0 - 0.5), 0), kind="box", size=FIN, part="fin"))
        kids.append(node(ids, "FinialCap" + tag, (0, sgn * (r_in + FIN[1] + CAP[1] / 2.0 - 0.5), 0), kind="box", size=CAP,
                         part="cap"))
        ring = [p for p in verts if abs(p[1] - sgn * r_in) < 1e-4]
        ring.sort(key=lambda p: math.atan2(p[2], p[0]))
        for k, p in enumerate(ring):
            d = v_sub(p, c)
            ln = math.sqrt(v_dot(d, d))
            axes = frame(d, (0, sgn, 0))
            kids.append(node(ids, "Spoke%s%d" % (tag, k), v_add(c, v_mul(d, 0.5)), quat_from_axes(*axes), "box", BAR, "bar",
                             stretch=(1, 1, ln / BAR[2])))
    return {"lod": "auto", "nodes": [root]}


def build_anim():
    keys = []
    for k in range(SPIN_KEYS + 1):
        a = 360.0 * k / SPIN_KEYS
        h = math.radians(a) / 2.0
        keys.append({"time": int(round(SPIN_FRAMES * k / float(SPIN_KEYS))),
                     "delta": {"x": 0, "y": r6(math.sin(h)), "z": 0, "w": r6(math.cos(h))}, "interpolationType": "linear"})
    return {"formatVersion": 1, "duration": SPIN_FRAMES, "holdLastKeyframe": False,
            "nodeAnimations": {"Cage": {"position": [], "orientation": keys, "shapeStretch": [], "shapeVisible": [],
                                        "shapeUvOffset": []}}}


# ------------------------------------------------------------------------------------------------------------------ texture
def painter(img, rect):
    x0, y0, w, h = UV[rect]

    def put(u, v, c, a=255):
        if 0 <= u < w and 0 <= v < h:
            img.put(x0 + u, y0 + v, (c[0], c[1], c[2], a))
    return put, w, h


def mixc(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t)


def paint(M, T, E):
    """M(t) = metal, T(t) = finial trim metal, E(t) = essence colour (t 0 dark .. 1 light)."""
    img = SA.Img(TEX_W, TEX_H)
    # bar long side (8 x 2, tangential): lit top row, mid lower row, darker ends where it meets the corners, a glint
    put, w, h = painter(img, "bar_side")
    for u in range(w):
        end = 0.18 if u in (0, w - 1) else 0.0
        put(u, 0, M(0.72 - end))
        put(u, 1, M(0.42 - end))
    put(2, 0, M(0.95))
    put(5, 1, M(0.55))
    # bar outer face (2 x 8): the lit face seen from outside
    put, w, h = painter(img, "bar_top")
    for v in range(h):
        end = 0.2 if v in (0, h - 1) else 0.0
        put(0, v, M(0.86 - end))
        put(1, v, M(0.62 - end))
    put(0, 3, M(1.0))
    put, w, h = painter(img, "bar_end")
    for u in range(w):
        for v in range(h):
            put(u, v, M(0.3))
    # bare corner knob: bevel lit top-left
    put, w, h = painter(img, "knob")
    kn = ((0.95, 0.78, 0.55), (0.78, 0.62, 0.40), (0.55, 0.40, 0.22))
    for v in range(3):
        for u in range(3):
            put(u, v, M(kn[v][u]))
    # gem (a cube on its corner): each face = a facet lit from one corner, a darker crease, a white-hot glint; the three face
    # kinds turn the light differently so neighbouring facets differ
    for rect, (lu, lv) in (("gem_tip", (0, 0)), ("gem_side", (3, 0)), ("gem_top", (0, 3))):
        put, w, h = painter(img, rect)
        for v in range(h):
            for u in range(w):
                d = (abs(u - lu) + abs(v - lv)) / float(w + h - 2)
                t = 1.0 - 0.62 * d
                if u == v or u + v == w - 1:
                    t -= 0.06
                put(u, v, E(t))
        put(min(lu, w - 1) + (1 if lu == 0 else -1), lv + (1 if lv == 0 else -1), mixc(E(1.0), (255, 255, 255), 0.5))
    # finial (trim metal: gold on Mithril like the wand bands, else the cage metal): ribbed collar + lit cap
    put, w, h = painter(img, "fin_side")
    for v in range(h):
        for u in range(w):
            t = (0.85, 0.65, 0.45)[u] - (0.25 if v == h - 1 else 0.0) + (0.1 if v == 0 else 0.0)
            put(u, v, T(t))
    put, w, h = painter(img, "fin_top")
    for v in range(3):
        for u in range(3):
            put(u, v, T(kn[v][u]))
    put, w, h = painter(img, "cap")
    for v in range(2):
        for u in range(2):
            put(u, v, T((1.0, 0.8, 0.8, 0.55)[v * 2 + u]))
    # soul: radial glow (bright core, essence edge), a darker swirl arc, a white-hot heart; two faces = two swirl turns
    for rect, turn in (("soul_a", 0.0), ("soul_b", 2.1)):
        put, w, h = painter(img, rect)
        c = (w - 1) / 2.0
        for v in range(h):
            for u in range(w):
                dx, dy = u - c, v - c
                d = math.hypot(dx, dy) / (c * 1.4142)
                t = 1.0 - 0.75 * d
                ang = (math.atan2(dy, dx) + turn) % (2 * math.pi)
                rr = math.hypot(dx, dy)
                if 1.6 < rr < 2.8 and 0.4 < ang < 2.6:
                    t -= 0.28                                           # swirl
                if 1.8 < rr < 2.6 and 3.6 < ang < 5.0:
                    t += 0.12                                           # counter-swirl highlight
                put(u, v, E(t))
        m = int(c)
        for (u, v, k) in ((m, m, 0.6), (m - 1, m, 0.3), (m, m - 1, 0.3), (m - 2, m - 2, 0.25)):
            put(u, v, mixc(E(1.0), (255, 255, 255), k))
    return img


def ramp_fn(grad, lo, hi, tint=None):
    if tint is None:
        return lambda t: SA.sample(grad, lo + (hi - lo) * min(max(t, 0.0), 1.0))
    base = ramp_fn(grad, lo, hi)
    (tr, tg, tb), k = tint
    tl = 0.299 * tr + 0.587 * tg + 0.114 * tb

    def f(t):
        c = base(t)
        l = 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]
        h = (tr * l / tl, tg * l / tl, tb * l / tl)          # the target hue at this texel's luminance
        out = [min(255, max(0, int(round(c[i] + (h[i] - c[i]) * k)))) for i in range(3)]
        return tuple(out) + tuple(c[3:])
    return f


# ------------------------------------------------------------------------------------------------------------------ sheets
BG = (24, 24, 30)
SLOT = (44, 44, 54)


def over(dst, x, y, c_premul):
    a = c_premul[3] / 255.0
    b = dst.get(x, y)
    dst.put(x, y, (c_premul[0] + b[0] * (1 - a), c_premul[1] + b[1] * (1 - a), c_premul[2] + b[2] * (1 - a), 255))


def blit(dst, src, ox, oy, k):
    for y in range(src.h):
        for x in range(src.w):
            c = src.get(x, y)
            if c[3]:
                for dy in range(k):
                    for dx in range(k):
                        over(dst, ox + x * k + dx, oy + y * k + dy, c)


def fill(img, x0, y0, w, h, c):
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            img.put(x, y, (c[0], c[1], c[2], 255))


def contact_sheet(icons, cell, k, cols, gap=8):
    rows = (len(icons) + cols - 1) // cols
    W, H = gap + cols * (cell * k + gap), gap + rows * (cell * k + gap)
    img = SA.Img(W, H)
    fill(img, 0, 0, W, H, BG)
    for n, ic in enumerate(icons):
        x, y = gap + (n % cols) * (cell * k + gap), gap + (n // cols) * (cell * k + gap)
        fill(img, x, y, cell * k, cell * k, SLOT)
        if ic is not None:
            blit(img, ic, x, y, k)
    return img


def turned(model, deg):
    """A copy of the model with the Cage node turned by deg about +Y (what the spin animation does), for previews."""
    m = json.loads(json.dumps(model))
    cage = m["nodes"][0]["children"][0]["children"][2]
    assert cage["name"] == "Cage"
    q = axis_quat((0, 1, 0), deg)
    cage["orientation"] = {"x": q[0], "y": q[1], "z": q[2], "w": q[3]}
    return m


# ------------------------------------------------------------------------------------------------------------------ main
def write(rel, data):
    p = os.path.join(OUT, *rel.split("/"))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as fh:
        fh.write(data)
    return p


def jbytes(obj):
    return (json.dumps(obj, indent=2) + "\n").encode("utf-8")


def main():
    z = SA.assets()
    manifest, icons, previews, spin_rows = [], [], [], []
    write(ANIM_PATH, jbytes(build_anim()))
    for t, metal in enumerate(METALS):
        ess_name, ess_tex = ESSENCE[t]
        mlo, mhi = METAL_SPAN.get(metal, (0.0, 1.0))
        elo, ehi = ESS_SPAN.get(ess_name, (0.0, 1.0))
        M = ramp_fn(SA.metal_gradient(z, metal), mlo, mhi, METAL_TINT.get(metal))
        T = ramp_fn(SA.band_gradient(z, metal), *((0.1, 0.9) if metal == "Mithril" else (mlo, mhi)))
        E = ramp_fn(SA.palette_from([SA._read(z, ess_tex)]), elo, ehi, ESS_TINT.get(ess_name))
        model = build_model(t)
        tex = SA.png_encode(paint(M, T, E))
        icon = SA.render_icon(model, tex, ICON_PROPS, 64)
        mp = "%s/SkyyArmory_%s.blockymodel" % (ITEM_DIR, metal)
        tp = "%s/SkyyArmory_%s_Texture.png" % (ITEM_DIR, metal)
        ip = "%s/SkyyArmory_SoulCage_%s.png" % (ICON_DIR, metal)
        write(mp, jbytes(model))
        write(tp, tex)
        write(ip, icon)
        write("preview-%s.png" % metal, SA.render_icon(model, tex, ICON_PROPS, 256))
        icons.append(SA.png_decode(icon))
        for deg in (0, 60, 120, 180, 240, 300):
            spin_rows.append(SA.render_icon(turned(model, deg), tex, ICON_PROPS, 128, as_img=True))
        manifest.append({
            "item": "SkyyArmory_SoulCage_%s" % metal, "tier": metal, "level_band": LEVELS[t], "tethers": TETHERS[t],
            "essence": ess_name, "model_path": mp, "model_base": "own", "texture_path": tp, "icon_path": ip,
            "animation_path": ANIM_PATH, "icon_properties": ICON_PROPS,
            "notes": "R3 own model (%d gems + %d bare knobs, 30 bars, 2 finials + 10 spokes, 2-box soul); soul + gems fullbright; "
                     "item JSON: Model/Texture/Icon as here, Animation = animation_path (the vanilla Weapon_Staff_Crystal_Flame "
                     "pattern), IconProperties = icon_properties; Light colour = the essence (UNVERIFIED)."
                     % (TETHERS[t], 20 - TETHERS[t])})
    z.close()
    write("sheet.png", SA.png_encode(contact_sheet(icons, 64, 2, 7)))
    write("spin-preview.png", SA.png_encode(contact_sheet(spin_rows, 128, 1, 6)))
    write("manifest.json", jbytes(manifest))
    print("soulcage: %d models, %d textures, %d icons, 1 animation -> %s" % (len(METALS), len(METALS), len(METALS), OUT))


if __name__ == "__main__":
    main()
