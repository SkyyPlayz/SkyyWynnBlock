#!/usr/bin/env python3
"""SkyWynn Menu item (Skyy_Menu) - the new emblem: a small floating sky island with a gold compass star above it.

Writes (all ORIGINAL pixels / geometry, no vanilla file is read or copied):
  art/menu-emblem/Common/Items/SkyyMenu/Skyy_Menu.blockymodel     held item model (Hytale blockymodel, 1 texel per unit)
  art/menu-emblem/Common/Items/SkyyMenu/Skyy_Menu_Texture.png     128 x 64 texture
  art/menu-emblem/Common/Icons/ItemsGenerated/Skyy_Menu.png       64 x 64 item icon
  art/menu-emblem/sheet.png                                       review sheet (icon 1x/2x/4x/32 px, hotbar mock, 3D views, texture)
  art/menu-emblem/manifest.json                                   file list (bytes, sha256), parts, sizes, suggested item fields

Run:  python tools/art/make_menu_emblem.py            (deterministic: two runs = same bytes)
Pure Python 3 (no Pillow / numpy): PNG I/O + raster helpers live in tools/art/emblem_png.py.
"""
import hashlib, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import emblem_png as P

ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "art", "menu-emblem")
MODEL_REL = "Common/Items/SkyyMenu/Skyy_Menu.blockymodel"
TEX_REL = "Common/Items/SkyyMenu/Skyy_Menu_Texture.png"
ICON_REL = "Common/Icons/ItemsGenerated/Skyy_Menu.png"
TEX_W, TEX_H = 128, 64

# ====================================================================== geometry
# Emblem-local units (64 units = 1 block, 1 texel per unit like vanilla items). +Y up, +Z = the showcase side
# (waterfall + star face). The whole emblem sits in one group yawed 165 deg - the same yaw the vanilla Voidheart body
# uses - so it shows the same side in the hand as the Voidheart did.
GROUP_POS = (0.0, -4.0, 0.0)       # lifts the emblem so its box centre sits where the Voidheart's sits (checked by the validator)
GROUP_YAW = 165.0

# name, kind, centre (x, y, z), size (w, h, d) [quad: (w, h)], material  - UV origins are packed by pack_uvs()
PARTS = [
    ("Grass",      "box",  (0.0, 18.5, 0.0),    (20, 3, 18), "grass"),
    ("Soil",       "box",  (0.0, 15.0, 0.0),    (18, 4, 16), "soil"),
    ("Rock-Upper", "box",  (0.5, 11.0, -0.5),   (15, 4, 13), "rock"),
    ("Rock-Mid",   "box",  (-0.5, 7.0, 0.5),    (11, 4, 9),  "rock"),
    ("Rock-Low",   "box",  (0.5, 3.5, 0.0),     (7, 3, 6),   "rock"),
    ("Rock-Tip",   "box",  (0.0, 0.5, 0.5),     (3, 3, 3),   "rockd"),
    ("Rock-Chunk", "box",  (-7.5, 11.5, 3.0),   (4, 4, 4),   "rock"),
    ("Leaves",     "box",  (-7.0, 24.0, -5.0),  (5, 4, 5),   "leaves"),
    ("Trunk",      "box",  (-7.0, 21.0, -5.0),  (2, 2, 2),   "trunk"),
    ("Stream",     "box",  (4.5, 20.0, 6.0),    (3, 1, 6),   "water"),
    ("Cloud-A",    "box",  (-7.0, 5.5, 2.5),    (7, 2, 4),   "cloud"),
    ("Cloud-B",    "box",  (-8.5, 7.5, 3.0),    (4, 2, 3),   "cloud"),
    ("Cloud-R",    "box",  (8.0, 9.0, -3.0),    (5, 2, 3),   "cloud"),
    ("Star-Core",  "box",  (0.5, 29.0, 0.5),    (3, 3, 3),   "gold"),
    ("Star-Ray-A", "quad", (0.5, 29.0, 0.5),    (13, 13),    "star"),
    ("Star-Ray-B", "quad", (0.5, 29.0, 0.5),    (13, 13),    "star"),
    ("Waterfall",  "quad", (4.5, 10.75, 9.2),   (3, 18),     "fall"),
]
SHARED_UV = {"Star-Ray-B": "Star-Ray-A"}     # both star quads use the same pixels


def uv_rect(part):
    name, kind, c, size, mat = part
    if kind == "quad":
        return size[0], size[1]
    w, h, d = size
    return 2 * d + 2 * w, d + h


def pack_uvs():
    """first-fit packer on a texel grid (tallest first, then widest): name -> uv origin; asserts it fits"""
    occ = [[False] * TEX_W for _ in range(TEX_H)]
    order = sorted([p for p in PARTS if p[0] not in SHARED_UV], key=lambda p: (-uv_rect(p)[1], -uv_rect(p)[0], p[0]))
    out = {}
    for part in order:
        rw, rh = uv_rect(part)
        spot = None
        for y in range(TEX_H - rh + 1):
            for x in range(TEX_W - rw + 1):
                if not any(occ[y + j][x + i] for j in range(rh) for i in range(rw)):
                    spot = (x, y); break
            if spot: break
        assert spot, "UV pack: %s does not fit in %dx%d" % (part[0], TEX_W, TEX_H)
        for j in range(rh):
            for i in range(rw):
                occ[spot[1] + j][spot[0] + i] = True
        out[part[0]] = spot
    for a, b in SHARED_UV.items():
        out[a] = out[b]
    return out


UV = pack_uvs()

PART_YAW = {"Star-Ray-B": 90.0}


def quat_yaw(deg):
    h = math.radians(deg) / 2
    return (0.0, round(math.sin(h), 6), 0.0, round(math.cos(h), 6))


# box faces: corners TL, TR, BR, BL as seen in the texture + the face's texel size (same convention as Blockbench / the plugin)
def face_defs(w, h, d):
    hx, hy, hz = w / 2, h / 2, d / 2
    return {
        "front": ([(-hx, hy, hz), (hx, hy, hz), (hx, -hy, hz), (-hx, -hy, hz)], (w, h)),
        "back": ([(hx, hy, -hz), (-hx, hy, -hz), (-hx, -hy, -hz), (hx, -hy, -hz)], (w, h)),
        "left": ([(-hx, hy, -hz), (-hx, hy, hz), (-hx, -hy, hz), (-hx, -hy, -hz)], (d, h)),
        "right": ([(hx, hy, hz), (hx, hy, -hz), (hx, -hy, -hz), (hx, -hy, hz)], (d, h)),
        "top": ([(-hx, hy, -hz), (hx, hy, -hz), (hx, hy, hz), (-hx, hy, hz)], (w, d)),
        "bottom": ([(-hx, -hy, hz), (hx, -hy, hz), (hx, -hy, -hz), (-hx, -hy, -hz)], (w, d)),
    }


def cross_layout(ox, oy, w, h, d):
    """standard box unwrap (the one vanilla uses): top row top + bottom, then left front right back"""
    return {"left": (ox, oy + d), "front": (ox + d, oy + d), "right": (ox + d + w, oy + d), "back": (ox + 2 * d + w, oy + d),
            "top": (ox + d, oy), "bottom": (ox + d + w, oy)}


# ====================================================================== palette (no #000000 / #ffffff; shadows lean violet / blue, lights warm)
def hx(s):
    return [int(s[i:i + 2], 16) for i in (1, 3, 5)]

GRASS = [hx(c) for c in ("#1f4a2a", "#2b6431", "#3a7e35", "#4f9a3a", "#6cb544", "#8fd05a", "#b6e57c")]
DIRT = [hx(c) for c in ("#2a1a1e", "#3b2621", "#523525", "#6b472c", "#855c37", "#a07448")]
ROCK = [hx(c) for c in ("#1e1d2c", "#2b2a3d", "#3b3b50", "#4f5166", "#676b7e", "#868a98", "#a7a9b1")]
CLOUD = [hx(c) for c in ("#8c9cc8", "#a9b9e0", "#c6d4f0", "#dfe8fa", "#f2f6fd")]
WATER = [hx(c) for c in ("#1d4f8f", "#2a6fb8", "#3c92d8", "#5db5ee", "#8ad3f7", "#c4ecfc", "#eefaff")]
GOLD = [hx(c) for c in ("#3e1f08", "#6a3a0e", "#9a5f16", "#c98d22", "#e9b83c", "#f8dc72", "#fff2cc")]
BARK = [hx(c) for c in ("#2a1712", "#43261a", "#5e3a22", "#7a4f2c")]
LEAF = [hx(c) for c in ("#173d26", "#22582e", "#2f7536", "#459442", "#62b14e", "#86cc63")]
FLOWER = [hx("#f6e27a"), hx("#f4f1f8"), hx("#e98fb8")]
SKY = hx("#5db5ee")
OUTLINE = hx("#120e1c")


def hsh(*a):
    """deterministic integer hash -> [0, 1)"""
    h = 2166136261
    for v in a:
        h = ((h ^ (int(v) & 0xffffffff)) * 16777619) & 0xffffffff
        h ^= h >> 13; h = (h * 1274126177) & 0xffffffff
    return (h & 0xffffff) / float(0x1000000)


def ramp(pal, t):
    t = max(0.0, min(0.999, t))
    return list(pal[int(t * len(pal))])


def cluster(x, y, seed, s=2):
    """blocky 2x2-ish clusters (vanilla-style texel variation, not per-pixel noise)"""
    return 0.6 * hsh(x // s, y // s, seed) + 0.4 * hsh(x, y, seed + 7)


# ====================================================================== texture painting
def paint_face(tex, part, face, origin, uv, mat):
    name, kind, c, size = part[0], part[1], part[2], part[3]
    if kind == "quad":
        w, h = size
        for v in range(h):
            for u in range(w):
                col = mat_quad(mat, u, v, w, h)
                tex[origin[1] + v][origin[0] + u] = col
        return
    w, h, d = size
    corners, (uw, vh) = face_defs(w, h, d)[face]
    for v in range(vh):
        for u in range(uw):
            fu, fv = (u + 0.5) / uw, (v + 0.5) / vh
            p = [corners[0][k] + (corners[1][k] - corners[0][k]) * fu + (corners[3][k] - corners[0][k]) * fv + c[k] for k in range(3)]
            col = mat_box(mat, name, face, u, v, uw, vh, p)
            tex[origin[1] + v][origin[0] + u] = col + [255] if len(col) == 3 else col


LIGHT = {"top": 1.0, "front": 0.0, "left": -0.06, "right": -0.12, "back": -0.14, "bottom": -0.32}


def mat_box(mat, name, face, u, v, uw, vh, p):
    gx, gy, gz = p
    L = LIGHT[face]
    seed = sum(map(ord, name)) * 31 + sum(map(ord, face))
    if mat == "grass":
        if face == "top":
            t = 0.55 + 0.25 * cluster(u, v, seed) + L * 0.1
            edge = min(u, v, uw - 1 - u, vh - 1 - v)
            if edge == 0: t += 0.18                      # lit bevel rim
            elif edge == 1: t += 0.06
            if u <= 2 and v <= 2: t += 0.05              # warm top-left light
            col = ramp(GRASS, t)
            r = hsh(u, v, 991)
            if edge >= 2 and r < 0.035: col = list(FLOWER[int(hsh(u, v, 5) * 3) % 3])
            elif edge >= 2 and r < 0.09: col = ramp(GRASS, t + 0.2)   # blade tips
            return col
        if face == "bottom":
            return ramp(DIRT, 0.3 + 0.2 * cluster(u, v, seed))
        # sides: bright rim on the top row, grass, then a dark hanging fringe
        drip = 1 + int(hsh(u, 0, seed) * 2.2)
        if v == 0: return ramp(GRASS, 0.86 + L * 0.3)
        if v < 3 - (1 if drip == 1 else 0):
            return ramp(GRASS, 0.5 + 0.2 * cluster(u, v, seed) + L)
        return ramp(GRASS, 0.25 + 0.15 * hsh(u, v, seed) + L)
    if mat == "soil":
        if face in ("top", "bottom"):
            return ramp(DIRT, 0.18 + 0.2 * cluster(u, v, seed) + (0.15 if face == "top" else 0))
        drip = int(hsh(u, 1, seed) * 3.2)                  # 0..3 rows of grass hanging over the dirt
        if v < drip:
            return ramp(GRASS, 0.3 + 0.12 * hsh(u, v, seed) + L)
        depth = v / max(1, vh - 1)
        t = 0.72 - 0.42 * depth + 0.2 * (cluster(u, v, seed) - 0.5) + L
        col = ramp(DIRT, t)
        r = hsh(u, v, seed + 3)
        if r < 0.07: col = ramp(ROCK, 0.55 + L)             # pebbles
        elif r < 0.12 and v >= 2: col = ramp(BARK, 0.35)    # roots
        if v == vh - 1: col = ramp(DIRT, t - 0.18)          # AO onto the rock below
        return col
    if mat in ("rock", "rockd"):
        if face == "top":
            return ramp(ROCK, 0.45 + 0.25 * cluster(u, v, seed))
        depth = 1.0 - (gy + 1.0) / 14.0                      # darker further down the island
        t = 0.66 - 0.32 * depth + 0.24 * (cluster(u, v, seed, 2) - 0.5) + L * 0.8
        if mat == "rockd": t -= 0.08
        if v == 0 and face != "bottom": t += 0.12           # lit upper edge
        if v == vh - 1 and face != "bottom": t -= 0.10      # dark lower edge
        if face != "bottom":
            k = (u + int(gy * 1.7) + seed) % 7              # thin cracks
            if k == 0 and hsh(u, v, seed + 9) < 0.55: t -= 0.22
        col = ramp(ROCK, t)
        if face != "bottom" and v <= 1 and hsh(u, v, seed + 4) < 0.25 and gy > 8:
            col = ramp(GRASS, 0.25)                          # moss specks under the soil
        return col
    if mat == "leaves":
        t = 0.45 + 0.3 * cluster(u, v, seed) + L * 0.9 + (0.12 if face == "top" else 0)
        if face != "top" and v == vh - 1: t -= 0.15
        if hsh(u, v, seed + 2) < 0.08: t += 0.25
        return ramp(LEAF, t)
    if mat == "trunk":
        t = 0.45 + 0.25 * hsh(u // 1, v // 2, seed) + L
        if u % 2 == 0: t -= 0.1
        return ramp(BARK, t)
    if mat == "water":
        if face == "top":
            t = 0.55 + 0.25 * ((u + v * 2) % 3 == 0) + 0.1 * hsh(u, v, seed)
            if v == vh - 1: t = 0.9                         # foam at the lip
            return ramp(WATER, t)
        return ramp(WATER, 0.45 + L)
    if mat == "cloud":
        t = 0.7 + (0.22 if face == "top" else 0) + L * 0.9
        if face not in ("top", "bottom"):
            t -= 0.28 * (v / max(1, vh - 1))
            if hsh(u, v, seed) < 0.15: t += 0.08
        return ramp(CLOUD, t)
    if mat == "gold":
        # star core: gold block with a sky-blue gem in the middle of every side
        if u == uw // 2 and v == vh // 2:
            return list(hx("#8ad3f7")) if face in ("front", "back", "top") else list(hx("#3c92d8"))
        t = 0.62 + L * 0.8 + (0.12 if (u + v) == 0 else 0) - (0.1 if (u == uw - 1 or v == vh - 1) else 0)
        return ramp(GOLD, t)
    raise ValueError(mat)


def star_mask(u, v, n=13):
    """8-point compass star on an n x n grid: long N / E / S / W points, short diagonal points, a round core"""
    c = (n - 1) / 2.0
    x, y = u - c, v - c
    ax, ay = abs(x), abs(y)
    hw = max(1.6, n * 0.16)                                # half-width of a long point at its base
    long_v = ax <= hw * (1 - ay / (c + 0.6)) and ay <= c + 0.01
    long_h = ay <= hw * (1 - ax / (c + 0.6)) and ax <= c + 0.01
    dl = c * 0.66                                          # diagonal point length
    dd = (ax + ay) / math.sqrt(2); dp = abs(ax - ay) / math.sqrt(2)
    diag = dd <= dl and dp <= max(1.05, n * 0.095) * (1 - dd / (dl + 0.5))
    core = ax + ay <= max(2.2, n * 0.2)
    return long_v or long_h or diag or core


def star_pixel(u, v, n):
    """RGBA of the compass star at texel (u, v): pinwheel bevel (each point = a lit half + a shaded half), sky-blue gem core,
    1 px dark-gold outline, clear elsewhere (cut-out alpha)"""
    if not star_mask(u, v, n):
        for du, dv in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if 0 <= u + du < n and 0 <= v + dv < n and star_mask(u + du, v + dv, n):
                return GOLD[0] + [255]
        return [0, 0, 0, 0]
    c = (n - 1) / 2.0
    x, y = u - c, -(v - c)                                 # y up
    if abs(x) + abs(y) <= 0.01:
        return hx("#eefaff") + [255]                       # gem glint
    if abs(x) + abs(y) <= 1.01:
        return (hx("#8ad3f7") if (x < 0 or y > 0) else hx("#3c92d8")) + [255]   # sky-blue gem
    ang = math.degrees(math.atan2(y, x)) % 360
    lit = (ang % 90) < 45 - 1e-6 if not (abs(x) < 0.01 or abs(y) < 0.01) else None
    if lit is None:                                        # the spine row / column: a bright ridge
        t = 0.9
    else:
        t = 0.78 if lit else 0.47
    dist = max(abs(x), abs(y)) / c
    t -= 0.1 * dist
    if y > 0.5 and x < -0.5: t += 0.05                     # global light from the top-left
    return ramp(GOLD, t) + [255]


def mat_quad(mat, u, v, w, h):
    if mat == "star":
        return star_pixel(u, v, w)
    if mat == "fall":
        # waterfall: vertical streaks, foam at the top lip, breaks into mist near the bottom
        fade = (v - (h - 6)) / 6.0
        if fade > 0 and hsh(u, v, 77) < fade * 0.9:
            return [0, 0, 0, 0]
        t = 0.5 + 0.18 * ((u + v // 3) % 2) + 0.12 * hsh(u, v // 2, 31)
        if u == 0: t -= 0.12
        if v <= 1: t = 0.9 + 0.05 * v
        if fade > 0: t = 0.85 + 0.1 * hsh(u, v, 4)       # white mist
        return ramp(WATER, t) + [255]
    raise ValueError(mat)


def build_texture():
    tex = P.new(TEX_W, TEX_H)
    for part in PARTS:
        name, kind, c, size, mat = part; org = UV[name]
        if kind == "quad":
            if name == "Star-Ray-B":
                continue                                  # shares Star-Ray-A's pixels
            paint_face(tex, part, "front", org, None, mat)
            continue
        lay = cross_layout(org[0], org[1], *size)
        for face, o in lay.items():
            paint_face(tex, part, face, o, None, mat)
    return tex


# ====================================================================== model JSON (vanilla structure: see the Voidheart / validator)
def vec(x, y, z):
    return {"x": round(x, 6), "y": round(y, 6), "z": round(z, 6)}


def layout_json(offsets):
    return {f: {"offset": {"x": o[0], "y": o[1]}, "mirror": {"x": False, "y": False}, "angle": 0} for f, o in offsets.items()}


def build_model():
    nid = [0]
    def next_id():
        s = str(nid[0]); nid[0] += 1; return s
    def node(name, pos, quat, shape, children=()):
        return {"id": next_id(), "name": name, "children": list(children), "position": vec(*pos),
                "orientation": {"x": quat[0], "y": quat[1], "z": quat[2], "w": quat[3]}, "shape": shape}
    root = node("R-Attachment", (0, 0, 0), (0, 0, 0, 1),
                {"type": "none", "offset": vec(0, 0, 0), "stretch": vec(1, 1, 1), "settings": {"isPiece": False}, "visible": True,
                 "doubleSided": False, "shadingMode": "standard", "unwrapMode": "custom", "textureLayout": {}})
    group = node("Emblem", GROUP_POS, quat_yaw(GROUP_YAW),
                 {"type": "none", "offset": vec(0, 0, 0), "stretch": vec(1, 1, 1), "settings": {"isPiece": False}, "visible": True,
                  "doubleSided": False, "shadingMode": "standard", "unwrapMode": "custom", "textureLayout": {}})
    root["children"].append(group)
    for name, kind, c, size, mat in PARTS:
        org = UV[name]
        q = quat_yaw(PART_YAW.get(name, 0.0))
        if kind == "box":
            shape = {"type": "box", "offset": vec(0, 0, 0), "stretch": vec(1, 1, 1),
                     "settings": {"size": {"x": size[0], "y": size[1], "z": size[2]}}, "visible": True, "doubleSided": False,
                     "shadingMode": "fullbright" if mat in ("gold",) else "standard", "unwrapMode": "full",
                     "textureLayout": layout_json(cross_layout(org[0], org[1], *size))}
        else:
            shape = {"type": "quad", "offset": vec(0, 0, 0), "stretch": vec(1, 1, 1),
                     "settings": {"size": {"x": size[0], "y": size[1]}, "normal": "+Z"}, "visible": True, "doubleSided": True,
                     "shadingMode": "fullbright" if mat == "star" else "standard", "unwrapMode": "custom",
                     "textureLayout": layout_json({"front": org})}
        group["children"].append(node(name, c, q, shape))
    return {"nodes": [root], "lod": "auto"}


# ====================================================================== tiny software renderer (pure Python)
def qmat(q):
    x, y, z, w = q
    return [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]


def mmul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]


def m4(R, t):
    return [[R[0][0], R[0][1], R[0][2], t[0]], [R[1][0], R[1][1], R[1][2], t[1]], [R[2][0], R[2][1], R[2][2], t[2]], [0, 0, 0, 1]]


def apply(M, p):
    return [M[i][0] * p[0] + M[i][1] * p[1] + M[i][2] * p[2] + M[i][3] for i in range(3)]


SHADE = {"top": 1.0, "front": 0.95, "left": 0.9, "right": 0.86, "back": 0.84, "bottom": 0.72}


def collect_faces(model, skip_group_yaw=False):
    faces = []
    I3 = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    def walk(n, PM, poff):
        q = (n["orientation"]["x"], n["orientation"]["y"], n["orientation"]["z"], n["orientation"]["w"])
        if skip_group_yaw and n["name"] == "Emblem":
            q = (0, 0, 0, 1)
        pos = [n["position"][k] for k in "xyz"]
        M = mmul(mmul(PM, m4(I3, poff)), m4(qmat(q), pos))
        s = n["shape"]; off = [s["offset"][k] for k in "xyz"]
        if s["type"] in ("box", "quad") and s.get("visible", True):
            sz = s["settings"]["size"]
            w, h, d = sz["x"], sz["y"], sz.get("z", 0)
            defs = face_defs(w, h, d)
            for fname, tl in s["textureLayout"].items():
                corners, (uw, vh) = defs[fname]
                cw = [apply(M, [cc[k] + off[k] for k in range(3)]) for cc in corners]
                ox, oy = tl["offset"]["x"], tl["offset"]["y"]
                uvs = [(ox, oy), (ox + uw, oy), (ox + uw, oy + vh), (ox, oy + vh)]
                faces.append(dict(P=cw, UV=uvs, shade=SHADE[fname] if s["shadingMode"] != "fullbright" else 1.0,
                                  double=bool(s.get("doubleSided")), name=n["name"]))
        for ch in n.get("children", []):
            walk(ch, M, off)
    for n in model["nodes"]:
        walk(n, m4(I3, (0, 0, 0)), (0, 0, 0))
    return faces


def view(yaw, pitch):
    y, p = math.radians(yaw), math.radians(pitch)
    Ry = [[math.cos(y), 0, math.sin(y)], [0, 1, 0], [-math.sin(y), 0, math.cos(y)]]
    Rx = [[1, 0, 0], [0, math.cos(p), -math.sin(p)], [0, math.sin(p), math.cos(p)]]
    return mmul(Rx, Ry)


def render(model, tex, yaw, pitch, size, ss=2, fill=0.86, skip_group_yaw=True, bounds=None, light=True, hide=()):
    """orthographic render; yaw 0 looks at the emblem's showcase (+Z) side, positive yaw turns it to show its right"""
    faces = collect_faces(model, skip_group_yaw)
    R = view(-yaw, pitch)
    def rot(p): return [sum(R[i][k] * p[k] for k in range(3)) for i in range(3)]
    allp = [rot(p) for f in faces for p in f["P"]]
    mn = [min(p[i] for p in allp) for i in range(3)]; mx = [max(p[i] for p in allp) for i in range(3)]
    if bounds is None:
        cen = [(mn[0] + mx[0]) / 2, (mn[1] + mx[1]) / 2]
        scale = fill * size / max(mx[0] - mn[0], mx[1] - mn[1])
    else:
        cen, scale = bounds[0], bounds[1]
    S = size * ss
    img = P.new(S, S); zb = [[-1e9] * S for _ in range(S)]
    for f in faces:
        if f["name"] in hide:
            continue
        Q = []
        for p in f["P"]:
            v = rot(p)
            Q.append(((v[0] - cen[0]) * scale * ss + S / 2, S / 2 - (v[1] - cen[1]) * scale * ss, v[2]))
        for tri in ((0, 1, 2), (0, 2, 3)):
            A, B, C = (Q[i] for i in tri); ua, ub, uc = (f["UV"][i] for i in tri)
            area = (B[0] - A[0]) * (C[1] - A[1]) - (B[1] - A[1]) * (C[0] - A[0])
            if area == 0 or (area < 0 and not f["double"]):
                continue
            x0 = max(int(math.floor(min(A[0], B[0], C[0]))), 0); x1 = min(int(math.ceil(max(A[0], B[0], C[0]))), S - 1)
            y0 = max(int(math.floor(min(A[1], B[1], C[1]))), 0); y1 = min(int(math.ceil(max(A[1], B[1], C[1]))), S - 1)
            sh = f["shade"] if light else 1.0
            if area < 0: sh *= 0.92
            for yy in range(y0, y1 + 1):
                py = yy + 0.5; row = img[yy]; zrow = zb[yy]
                for xx in range(x0, x1 + 1):
                    px = xx + 0.5
                    w0 = ((B[0] - px) * (C[1] - py) - (B[1] - py) * (C[0] - px)) / area
                    w1 = ((C[0] - px) * (A[1] - py) - (C[1] - py) * (A[0] - px)) / area
                    w2 = 1 - w0 - w1
                    if w0 < -1e-6 or w1 < -1e-6 or w2 < -1e-6:
                        continue
                    z = w0 * A[2] + w1 * B[2] + w2 * C[2]
                    if z <= zrow[xx]:
                        continue
                    u = w0 * ua[0] + w1 * ub[0] + w2 * uc[0]; v = w0 * ua[1] + w1 * ub[1] + w2 * uc[1]
                    ui = min(max(int(math.floor(u - 1e-7)), 0), TEX_W - 1); vi = min(max(int(math.floor(v - 1e-7)), 0), TEX_H - 1)
                    t = tex[vi][ui]
                    if t[3] < 128:
                        continue
                    zrow[xx] = z
                    row[xx] = [t[0] * sh, t[1] * sh, t[2] * sh, 255]
    out = P.downsample(img, ss) if ss > 1 else img
    return out, (cen, scale, R)


def project(pt, b, size):
    cen, scale, R = b
    v = [sum(R[i][k] * pt[k] for k in range(3)) for i in range(3)]
    return (v[0] - cen[0]) * scale + size / 2, size / 2 - (v[1] - cen[1]) * scale


# ====================================================================== the 64 px icon
ICON_YAW, ICON_PITCH = 24.0, 20.0
VOIDHEART_BBOX = (28.6, 34.3, 19.7)    # measured by validate_menu_emblem.py from Assets.zip (read only), rotations applied


ICON_STAR = 17          # the icon draws the star flat-on as a crisp 17 px sprite (same painter as the 13 px star quads)
STAR_PARTS = ("Star-Ray-A", "Star-Ray-B", "Star-Core")


def make_icon(model, tex):
    big, b = render(model, tex, ICON_YAW, ICON_PITCH, 64, ss=8, fill=0.90, hide=STAR_PARTS)
    ic = P.new(64, 64)
    for y in range(64):
        for x in range(64):
            p = big[y][x]
            if p[3] >= 110:                                  # hard alpha: every pixel fully solid or fully clear
                ic[y][x] = [p[0], p[1], p[2], 255]
    solid = [[ic[y][x][3] > 0 for x in range(64)] for y in range(64)]
    # rim light on the upper-left silhouette edge (reads on dark hotbars), cool shade on the lower-right edge
    for y in range(64):
        for x in range(64):
            if not solid[y][x]: continue
            up = y > 0 and solid[y - 1][x]; lf = x > 0 and solid[y][x - 1]
            dn = y < 63 and solid[y + 1][x]; rt = x < 63 and solid[y][x + 1]
            c = ic[y][x]
            if not up or not lf:
                ic[y][x] = [min(250, c[0] * 1.18 + 14), min(250, c[1] * 1.18 + 12), min(250, c[2] * 1.12 + 8), 255]
            elif not dn or not rt:
                ic[y][x] = [c[0] * 0.82, c[1] * 0.84, c[2] * 0.95, 255]
    out = [row[:] for row in ic]
    for y in range(64):                                      # 1 px violet-black outline round the island
        for x in range(64):
            if solid[y][x]: continue
            if any(0 <= x + dx < 64 and 0 <= y + dy < 64 and solid[y + dy][x + dx] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                out[y][x] = OUTLINE + [255]
    # the star sprite, centred on the projected star centre (its own dark-gold outline is part of the sprite)
    sc = [c for n, k, c, s, m in PARTS if n == "Star-Core"][0]
    gp = (sc[0], sc[1], sc[2])
    sx, sy = project(gp, b, 64)
    n = ICON_STAR; x0 = int(round(sx - n / 2.0)); y0 = int(round(sy - n / 2.0))
    y0 = max(1, y0)
    for v in range(n):
        for u in range(n):
            px = star_pixel(u, v, n)
            if px[3]:
                out[y0 + v][x0 + u] = px
    # a tiny glint beside the star (the item glows in game)
    for cx, cy in ((x0 + n + 2, y0 + 3),):
        for dx, dy, c in ((0, 0, "#fff2cc"), (1, 0, "#f8dc72"), (-1, 0, "#f8dc72"), (0, 1, "#f8dc72"), (0, -1, "#f8dc72")):
            x, y = cx + dx, cy + dy
            if 0 <= x < 64 and 0 <= y < 64 and not out[y][x][3]:
                out[y][x] = hx(c) + [255]
    for row in out:                                          # no pure black / white
        for p in row:
            if p[3]:
                for k in range(3):
                    p[k] = int(round(max(10, min(250, p[k]))))
    return out


# ====================================================================== review sheet
BG = [24, 26, 36, 255]
PANEL = [36, 39, 54, 255]
LABEL = [222, 226, 236, 255]
DIM = [150, 156, 176, 255]


def panel(img, x, y, w, h, title):
    P.fill_rect(img, x, y, x + w, y + h, PANEL)
    P.text(img, x + 8, y + 8, title, LABEL, 2)


def checker(img, x0, y0, w, h, a=(58, 62, 80), b=(48, 52, 68), s=8):
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            c = a if ((x - x0) // s + (y - y0) // s) % 2 == 0 else b
            img[y][x] = list(c) + [255]


def hotbar_slot(img, x, y, n=76, selected=False):
    """a generic dark item slot (drawn here, not vanilla UI art)"""
    P.fill_rect(img, x, y, x + n, y + n, [70, 62, 52, 255] if not selected else [214, 178, 92, 255])
    P.fill_rect(img, x + 2, y + 2, x + n - 2, y + n - 2, [20, 22, 30, 255])
    P.fill_rect(img, x + 3, y + 3, x + n - 3, y + n - 3, [32, 34, 46, 255])


def build_sheet(model, tex, icon):
    W, H = 1180, 1000
    img = P.new(W, H, BG)
    P.text(img, 24, 20, "SKYWYNN MENU ITEM - NEW EMBLEM (SKYY_MENU V1)", [248, 220, 114, 255], 3)
    P.text(img, 24, 52, "Floating sky island + gold compass star. Item id Skyy_Menu. Original pixels, 1 texel per unit.", DIM, 2)

    # 1. icon sizes on dark + light
    panel(img, 20, 84, 560, 330, "ICON 64 PX - 1X 2X 4X")
    checker(img, 36, 116, 64, 64); P.blit(img, icon, 36, 116, 1)
    checker(img, 112, 116, 128, 128); P.blit(img, icon, 112, 116, 2)
    checker(img, 252, 116, 256, 256); P.blit(img, icon, 252, 116, 4)
    P.fill_rect(img, 36, 196, 100, 260, [214, 220, 228, 255]); P.blit(img, icon, 36, 196, 1)
    P.text(img, 36, 268, "LIGHT", DIM, 1)
    # 32 px (half size, nearest of 2x2 averaged)
    half = P.downsample(icon, 2)
    for row in half:
        for p in row:
            p[3] = 255 if p[3] >= 128 else 0
    checker(img, 36, 290, 32, 32, s=4); P.blit(img, half, 36, 290, 1)
    P.text(img, 36, 328, "32 PX", DIM, 1)
    P.text(img, 36, 388, "64 / 128 / 256 PX", DIM, 1)

    # 2. hotbar mock: 9 slots, menu item in the LAST slot; then the 1-slot view enlarged
    panel(img, 600, 84, 560, 330, "HOTBAR MOCK")
    xs = 616
    for i in range(9):
        hotbar_slot(img, xs + i * 60, 120, 56, selected=(i == 8))
    # the in-game slot shows the 64 px icon at about 48 px in a 56 px slot: nearest 3/4 scale
    small = [[icon[int(y * 64 / 48)][int(x * 64 / 48)][:] for x in range(48)] for y in range(48)]
    P.blit(img, small, xs + 8 * 60 + 4, 124, 1)
    P.text(img, 616, 186, "LAST SLOT, 48 PX IN A 56 PX SLOT (SELECTED)", DIM, 1)
    hotbar_slot(img, 616, 210, 76, False); P.blit(img, icon, 622, 216, 1)
    hotbar_slot(img, 708, 210, 76, True); P.blit(img, icon, 714, 216, 1)
    P.text(img, 616, 294, "1-SLOT VIEW AT 64 PX", DIM, 1)
    hotbar_slot(img, 820, 200, 140, True); P.blit(img, icon, 826, 206, 2)
    P.text(img, 820, 348, "2X", DIM, 1)
    # vanilla-sized neighbour: compare to a plain block-sized square
    P.text(img, 616, 320, "SLOT RIM DRAWN HERE, NOT GAME ART", DIM, 1)

    # 3. 3D renders of the real model + texture
    panel(img, 20, 430, 1140, 330, "MODEL - RENDERED FROM THE BLOCKYMODEL + TEXTURE")
    views = [("FRONT 3/4", 24, 20), ("FRONT", 0, 8), ("RIGHT", 90, 10), ("BACK 3/4", 200, 20), ("BELOW", 30, -35)]
    ref = None
    for i, (lab, yw, pt) in enumerate(views):
        r, b = render(model, tex, yw, pt, 200, ss=2, fill=0.9, bounds=ref[:2] if ref else None)
        if ref is None: ref = b
        x0 = 36 + i * 224
        checker(img, x0, 470, 200, 200, (44, 48, 64), (40, 43, 58), 10)
        P.blit(img, r, x0, 470, 1)
        P.text(img, x0, 680, lab, LABEL, 2)
    P.text(img, 36, 712, "VIEWS SHOW THE EMBLEM UNYAWED. IN HAND ITS GROUP IS YAWED 165 DEG LIKE THE VOIDHEART BODY. STAR = FULLBRIGHT.", DIM, 1)
    fz = collect_faces(model, skip_group_yaw=False); pts = [q for f in fz for q in f["P"]]
    ext = [max(q[i] for q in pts) - min(q[i] for q in pts) for i in range(3)]
    P.text(img, 36, 728, "SIZE IN HAND: %.1f X %.1f X %.1f UNITS (VOIDHEART %.1f X %.1f X %.1f). TEXTURE %d X %d, ITEM SCALE 1.2 LIKE THE VOIDHEART."
           % tuple(ext + list(VOIDHEART_BBOX) + [TEX_W, TEX_H]), DIM, 1)

    # 4. texture
    panel(img, 20, 776, 560, 210, "TEXTURE 128 X 64 (2X)")
    checker(img, 36, 808, 256, 128, s=8); P.blit(img, tex, 36, 808, 2)
    P.text(img, 308, 812, "GRASS SOIL ROCK LEAVES", DIM, 1)
    P.text(img, 308, 826, "WATER CLOUD GOLD STAR", DIM, 1)
    P.text(img, 308, 846, "CUT-OUT ALPHA ON THE", DIM, 1)
    P.text(img, 308, 860, "STAR + WATERFALL QUADS", DIM, 1)

    # 5. palette
    panel(img, 600, 776, 560, 210, "PALETTE")
    rows = [("GRASS", GRASS), ("DIRT", DIRT), ("ROCK", ROCK), ("CLOUD", CLOUD), ("WATER", WATER), ("GOLD", GOLD)]
    for i, (n, pal) in enumerate(rows):
        y = 812 + i * 26
        P.text(img, 616, y + 4, n, DIM, 1)
        for j, c in enumerate(pal):
            P.fill_rect(img, 680 + j * 30, y, 680 + j * 30 + 26, y + 20, c + [255])
    return img


# ====================================================================== main
def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    os.makedirs(os.path.join(OUT, "Common", "Items", "SkyyMenu"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "Common", "Icons", "ItemsGenerated"), exist_ok=True)
    tex = build_texture()
    model = build_model()
    mbytes = (json.dumps(model, indent=2) + "\n").encode("utf-8")
    with open(os.path.join(OUT, *MODEL_REL.split("/")), "wb") as fh:
        fh.write(mbytes)
    tbytes = P.write_png(os.path.join(OUT, *TEX_REL.split("/")), tex)
    icon = make_icon(model, tex)
    ibytes = P.write_png(os.path.join(OUT, *ICON_REL.split("/")), icon)
    sheet = build_sheet(model, tex, icon)
    sbytes = P.write_png(os.path.join(OUT, "sheet.png"), sheet)

    faces = collect_faces(model, skip_group_yaw=True)
    pts = [p for f in faces for p in f["P"]]
    mn = [round(min(p[i] for p in pts), 3) for i in range(3)]; mx = [round(max(p[i] for p in pts), 3) for i in range(3)]
    man = {
        "what": "SkyWynn Menu item (Skyy_Menu) emblem: floating sky island + gold compass star. Original art.",
        "generator": "tools/art/make_menu_emblem.py (+ tools/art/emblem_png.py); check: tools/art/validate_menu_emblem.py",
        "files": [
            {"path": MODEL_REL, "bytes": len(mbytes), "sha256": sha(mbytes)},
            {"path": TEX_REL, "bytes": len(tbytes), "sha256": sha(tbytes), "size": [TEX_W, TEX_H]},
            {"path": ICON_REL, "bytes": len(ibytes), "sha256": sha(ibytes), "size": [64, 64]},
            {"path": "sheet.png", "bytes": len(sbytes), "sha256": sha(sbytes)},
        ],
        "model": {
            "format": "Hytale blockymodel (same node / shape / textureLayout keys as vanilla Ingredient_Voidheart)",
            "root": "R-Attachment (none) > Emblem (none, yaw %.0f deg, position %s) > %d parts" % (GROUP_YAW, list(GROUP_POS), len(PARTS)),
            "parts": [{"name": n, "type": k, "centre": list(c), "size": list(s), "material": m} for n, k, c, s, m in PARTS],
            "bounds_units_unyawed": {"min": mn, "max": mx, "size": [round(mx[i] - mn[i], 3) for i in range(3)]},
            "texel_density": "1 texel per unit (vanilla item density)",
            "texture": [TEX_W, TEX_H],
        },
        "suggested_item_fields": {
            "Model": "Items/SkyyMenu/Skyy_Menu.blockymodel",
            "Texture": "Items/SkyyMenu/Skyy_Menu_Texture.png",
            "Icon": "Icons/ItemsGenerated/Skyy_Menu.png",
            "Scale": 1.2,
            "PlayerAnimationsId": "Item",
            "IconProperties": {"Scale": 0.9, "Rotation": [0, 0, 0], "Translation": [0, -13]},
            "Light": {"Color": "#432", "Radius": 1},
        },
        "icon_view": {"yaw": ICON_YAW, "pitch": ICON_PITCH, "supersample": 8, "alpha": "hard (0 or 255)", "outline": "1 px #120e1c / #3e1f08"},
        "palettes": {"grass": GRASS, "dirt": DIRT, "rock": ROCK, "cloud": CLOUD, "water": WATER, "gold": GOLD, "bark": BARK, "leaf": LEAF},
    }
    with open(os.path.join(OUT, "manifest.json"), "wb") as fh:
        fh.write((json.dumps(man, indent=2) + "\n").encode("utf-8"))
    print("model", len(mbytes), "B; texture", len(tbytes), "B; icon", len(ibytes), "B; sheet", len(sbytes), "B")
    print("bounds (unyawed):", mn, mx)


if __name__ == "__main__":
    main()
