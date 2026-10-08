#!/usr/bin/env python3
"""Generate Pebble (SkyWynn talking rock NPC): texture, .blockymodel, .blockyanim files.

Deterministic: two runs produce identical bytes. Original art only - no vanilla file is read.
Usage: python3 make_pebble.py [out_dir]   (default: ../../art/pebble relative to this file)
"""
import json, math, os, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pebble_model import NODES, SHARED_FACES
from pebble_common import (quat_from_euler_zyx, quat_to_mat, mat4, r6, FACE_NORMALS, face_uv_size,
                           face_texel_to_local)
import pebble_anims

OUT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.normpath(os.path.join(HERE, "../../art/pebble"))
NPC_DIR = os.path.join(OUT, "Common/NPC/SkyyTowns/Pebble")
BOX_FACES = ["front", "back", "left", "right", "top", "bottom"]
MIRROR_FACE = {"front": "front", "back": "back", "left": "right", "right": "left", "top": "top", "bottom": "bottom"}

# ------------------------------------------------------------------ nodes + transforms
by_name = {n["name"]: n for n in NODES}
for n in NODES:
    n.setdefault("rot", (0, 0, 0))
    n.setdefault("stretch", (1, 1, 1))
    n["quat"] = quat_from_euler_zyx(*n["rot"])
    shp = n["shape"]
    n["offset"] = tuple(shp[2]) if shp else (0, 0, 0)
    p = by_name.get(n["parent"]) if n["parent"] else None
    if p is None:
        n["position"] = tuple(n["pivot"])
    else:
        assert p["rot"] == (0, 0, 0), "parents must be un-rotated at rest"
        n["position"] = tuple(n["pivot"][i] - (p["pivot"][i] + p["offset"][i]) for i in range(3))

def world_matrix(name):
    n = by_name[name]
    local = mat4(quat_to_mat(n["quat"]), n["position"])
    if n["parent"] is None:
        return local
    p = by_name[n["parent"]]
    return world_matrix(p["name"]) @ mat4(None, p["offset"]) @ local

def box_size3(n):
    t, size, _ = n["shape"]
    return size if t == "box" else (size[0], size[1], 0)

def faces_of(n):
    if not n["shape"]:
        return []
    return BOX_FACES if n["shape"][0] == "box" else ["front"]

# ------------------------------------------------------------------ texture regions
regions = {}      # key -> dict(w,h,node,face)  (painted regions)
layout = {}       # (node, face) -> (region_key, mirror_x)
for n in NODES:
    for f in faces_of(n):
        name = n["name"]
        if "mirror_of" in n:
            layout[(name, f)] = ((n["mirror_of"], MIRROR_FACE[f]), True)
        elif "share_of" in n:
            layout[(name, f)] = ((n["share_of"], f), False)
        elif (name, f) in SHARED_FACES:
            layout[(name, f)] = (SHARED_FACES[(name, f)], False)
        else:
            w, h = face_uv_size(f, box_size3(n))
            regions[(name, f)] = dict(w=w, h=h, node=name, face=f)
            layout[(name, f)] = ((name, f), False)
# sanity: shared region must be at least as big as the face using it
for (name, f), (rk, mir) in layout.items():
    fw, fh = face_uv_size(f, box_size3(by_name[name]))
    assert regions[rk]["w"] >= fw and regions[rk]["h"] >= fh, (name, f, rk)

def pack(W, pad=1):
    items = sorted(regions.items(), key=lambda kv: (-kv[1]["h"], -kv[1]["w"], kv[0]))
    x = y = shelf_h = 0
    pos = {}
    for key, r in items:
        if x + r["w"] > W:
            x, y, shelf_h = 0, y + shelf_h + pad, 0
        pos[key] = (x, y)
        x += r["w"] + pad
        shelf_h = max(shelf_h, r["h"])
    return pos, y + shelf_h

TEX_W = int(sys.argv[2]) if len(sys.argv) > 2 else 256
positions, used_h = pack(TEX_W)
TEX_H = int(math.ceil(used_h / 32.0) * 32)
for k, p in positions.items():
    regions[k]["x"], regions[k]["y"] = p

# ------------------------------------------------------------------ painting helpers
def hash3(ix, iy, iz, seed):
    h = (ix * 374761393 + iy * 668265263 + iz * 2147483647 + seed * 144665) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 65535.0

def vnoise(p, scale, seed):
    """smooth 3D value noise in [0,1], p: (N,3) world positions"""
    q = np.asarray(p, dtype=np.float64) / scale
    i0 = np.floor(q).astype(np.int64)
    fr = q - i0
    fr = fr * fr * (3 - 2 * fr)
    out = np.zeros(len(q))
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                hv = hash3(i0[:, 0] + dx, i0[:, 1] + dy, i0[:, 2] + dz, seed)
                wgt = (fr[:, 0] if dx else 1 - fr[:, 0]) * (fr[:, 1] if dy else 1 - fr[:, 1]) * (fr[:, 2] if dz else 1 - fr[:, 2])
                out += hv * wgt
    return out

def ramp(values, stops):
    xs = np.array([s[0] for s in stops])
    cols = np.array([s[1] for s in stops], dtype=np.float64)
    v = np.clip(values, xs[0], xs[-1])
    return np.stack([np.interp(v, xs, cols[:, c]) for c in range(3)], axis=-1)

# hue-shifted stone ramp: violet-blue shadows -> neutral grey -> warm light (never pure black / white)
STONE = [(0.10, (44, 40, 64)), (0.25, (64, 61, 88)), (0.40, (92, 92, 112)), (0.55, (124, 126, 134)),
         (0.68, (152, 153, 150)), (0.80, (178, 176, 162)), (0.92, (204, 198, 176)), (1.0, (218, 211, 188))]
MOSS = [(0.10, (30, 50, 52)), (0.28, (40, 70, 54)), (0.45, (56, 94, 50)), (0.60, (76, 116, 50)),
        (0.75, (100, 142, 56)), (0.90, (132, 170, 74)), (1.0, (156, 190, 96))]
LEAF = [(0.2, (46, 92, 48)), (0.45, (78, 140, 52)), (0.7, (128, 186, 70)), (0.9, (176, 216, 104)), (1.0, (200, 228, 134))]
QUANT = 0.03   # value step -> painterly clusters instead of airbrush gradients / grain

# occluders for AO: every box at rest (world matrix inverse + half size)
OCCLUDERS = []
for n in NODES:
    if n["shape"] and n["shape"][0] == "box":
        M = world_matrix(n["name"]) @ mat4(None, n["offset"])
        OCCLUDERS.append((n["name"], np.linalg.inv(M), np.array(box_size3(n)) / 2.0))

def ao_term(P, Nrm, exclude):
    """fraction of hemisphere samples blocked by other boxes (deterministic directions)"""
    rng = np.random.RandomState(7)
    dirs = rng.normal(size=(40, 3)); dirs /= np.linalg.norm(dirs, axis=1, keepdims=True)
    dists = [1.0, 2.0, 3.5]
    occl = np.zeros(len(P)); total = 0
    for d in dirs:
        dd = np.where((Nrm @ d)[:, None] < 0, -d, d)            # flip into the hemisphere of the normal
        for dist in dists:
            S = P + Nrm * 0.25 + dd * dist
            hit = np.zeros(len(P), dtype=bool)
            for name, Minv, half in OCCLUDERS:
                if name in exclude:
                    continue
                L = (np.c_[S, np.ones(len(S))] @ Minv.T)[:, :3]
                hit |= np.all(np.abs(L) < half - 0.01, axis=1)
            occl += hit / dist
        total += sum(1 / x for x in dists)
    return occl / total

def region_texels(key):
    """world positions + normals of every texel centre in a region (painted from its owner node/face)"""
    r = regions[key]; n = by_name[r["node"]]; f = r["face"]
    size = box_size3(n)
    M = world_matrix(n["name"]) @ mat4(None, n["offset"])
    U, V = np.meshgrid(np.arange(r["w"]) + 0.5, np.arange(r["h"]) + 0.5)
    loc = np.array([face_texel_to_local(f, size, u, v) for u, v in zip(U.ravel(), V.ravel())])
    P = (np.c_[loc, np.ones(len(loc))] @ M.T)[:, :3]
    Nrm = M[:3, :3] @ np.array(FACE_NORMALS[f], dtype=float)
    Nrm = np.tile(Nrm, (len(P), 1))
    return P, Nrm, U.ravel() - 0.5, V.ravel() - 0.5

# ------------------------------------------------------------------ stone + moss painter
STONE_NODES = {"Body", "Body-Wide", "Body-Base", "L-Foot", "L-Arm", "Head", "Head-Wide", "Head-Bulge", "Head-Top", "Crown"}
MOSS_NODES = {"Moss-Cap", "Moss-Tuft", "L-Brow"}

# hand-placed cracks: node, face, polyline in face texel coords (kept away from the face area)
CRACKS = [
    ("Body-Wide", "left", [(4, 3), (8, 6), (7, 9), (11, 12)]),
    ("Body", "front", [(33, 3), (36, 6), (35, 9), (37, 12)]),
    ("Body", "back", [(9, 2), (13, 6), (12, 9), (16, 12)]),
    ("Head", "back", [(30, 5), (27, 9), (29, 13), (26, 17)]),
    ("Head", "back", [(9, 12), (13, 15)]),
    ("Head-Wide", "right", [(22, 10), (25, 13), (23, 17)]),
    ("Head-Wide", "left", [(7, 8), (10, 11), (9, 15)]),
    ("Head", "front", [(41, 14), (43, 17), (42, 20)]),
    ("Head-Bulge", "left", [(16, 3), (19, 7)]),
]

def raster_line(pts):
    cells = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(abs(x1 - x0), abs(y1 - y0))
        for i in range(n + 1):
            cells.append((round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n)))
    return sorted(set(cells))

def box_top_y(name):
    n = by_name[name]
    return (world_matrix(name) @ np.array([*n["offset"], 1.0]))[1] + box_size3(n)[1] / 2.0

# moss: thick on the crown, patchy lower down, drips over top edges (less on the face side)
TOP_BIAS = {"Crown": 0.34, "Head-Top": 0.0, "Head": -0.07, "Head-Wide": -0.12, "Head-Bulge": -0.16, "L-Arm": -0.12}
DRIP = {"Crown": 3.0, "Head-Top": 3.5, "Head": 6.5, "Head-Wide": 6.0, "Head-Bulge": 2.2}

def moss_mask(name, face, P, Nrm, U, V, w, h):
    if name in MOSS_NODES:
        return np.ones(len(P), dtype=bool)
    m = np.zeros(len(P), dtype=bool)
    streak = vnoise(np.c_[P[:, 0], np.zeros(len(P)), P[:, 2]], 3.5, 11)       # vertical streaks (no y)
    blob = vnoise(P, 5.5, 12) * 0.75 + vnoise(P, 2.5, 13) * 0.25
    if face == "top" and name in TOP_BIAS:
        m = blob + TOP_BIAS[name] > 0.56
    elif face in ("front", "back", "left", "right") and name in DRIP:
        depth = DRIP[name] * (0.15 + streak ** 1.3 * 1.3)
        if face == "left" or face == "back":
            depth = depth * 1.3
        top = box_top_y(name)
        m = P[:, 1] > top - depth
        if face == "front" and name == "Head":
            m &= P[:, 1] > 41.2                                                # keep the brows + eyes clean
    elif name in ("Body", "Body-Wide"):
        if face == "left":
            d = np.sqrt(((P[:, 2] + 7) / 7.5) ** 2 + ((P[:, 1] - 14) / 5.0) ** 2)
            m = d < 0.75 + 0.45 * blob
        elif face == "back":
            d = np.sqrt(((P[:, 0] - 9) / 5.0) ** 2 + ((P[:, 1] - 17) / 4.0) ** 2)
            m = d < 0.7 + 0.4 * blob
        elif face == "right":
            d = np.sqrt(((P[:, 2] - 8) / 3.5) ** 2 + ((P[:, 1] - 20) / 2.2) ** 2)
            m = d < 0.7 + 0.4 * blob
    return m

def light_term(name, face, P, Nrm, U, V, w, h):
    ny, nz, nx = Nrm[:, 1], Nrm[:, 2], Nrm[:, 0]
    L = np.where(ny > 0.5, 0.68, np.where(ny < -0.5, 0.34, np.where(nz > 0.5, 0.64, np.where(nz < -0.5, 0.53, 0.59))))
    L = L + 0.22 * np.clip(P[:, 1] / 58.0, 0, 1) - 0.10                      # imaginary spotlight above
    side = np.abs(ny) < 0.5
    t = V / max(h - 1, 1)
    L = L + np.where(side, 0.07 - 0.14 * t, 0)                                # per-face top->bottom falloff
    L = L + np.where(side & (V == 0), 0.11, 0) + np.where(side & (V == 1), 0.04, 0)   # top-edge bevel light
    L = L - np.where(side & (V == h - 1), 0.07, 0)
    L = L - np.where(side & ((U == 0) | (U == w - 1)), 0.05, 0) - np.where(side & ((U == 1) | (U == w - 2)), 0.015, 0)
    top = ny > 0.5
    edge = np.minimum.reduce([U, w - 1 - U, V, h - 1 - V])
    L = L + np.where(top & (edge == 0), 0.035, 0) + np.where(top, 0.04 * (V / max(h - 1, 1) - 0.5), 0)
    L = L - np.where(side, 0.20 * np.clip(1 - P[:, 1] / 6.0, 0, 1), 0)        # ground contact shadow
    L = np.where(top, np.minimum(L, 0.76), L)                                 # keep bare stone tops from going chalky
    return L

def paint_stone_region(key):
    r = regions[key]; name, face, w, h = r["node"], r["face"], r["w"], r["h"]
    P, Nrm, U, V = region_texels(key)
    L = light_term(name, face, P, Nrm, U, V, w, h)
    L -= 0.24 * ao_term(P, Nrm, exclude={name})
    n1 = vnoise(P, 8.0, 1); n2 = vnoise(P, 19.0, 2)
    L += np.where(n1 > 0.66, 0.035, np.where(n1 < 0.33, -0.03, 0))
    L += np.where(n2 > 0.62, 0.03, np.where(n2 < 0.36, -0.035, 0))
    if name == "L-Arm" and face == "bottom":   # the 'hand' end shows when Pebble waves - keep it readable
        L += 0.26
    if name == "Head" and face == "front":   # keep the face plane calm; faint warm cheeks
        for cx in (-10, 10):
            d = np.hypot((P[:, 0] - cx) / 4.0, (P[:, 1] - 28.5) / 2.0)
            L += np.where(d < 1, 0.02, 0)
    moss = moss_mask(name, face, P, Nrm, U, V, w, h)
    L2 = L.reshape(h, w); M2 = moss.reshape(h, w)
    sidef = face not in ("top", "bottom")
    if sidef:   # stone right under a moss edge gets a soft cast shadow
        below = np.zeros_like(M2); below[1:, :] = M2[:-1, :] & ~M2[1:, :]
        below2 = np.zeros_like(M2); below2[2:, :] = M2[:-2, :] & ~M2[2:, :] & ~M2[1:-1, :]
        L2 -= below * 0.12 + below2 * 0.05
    else:
        ring = np.zeros_like(M2)
        ring[1:, :] |= M2[:-1, :]; ring[:-1, :] |= M2[1:, :]; ring[:, 1:] |= M2[:, :-1]; ring[:, :-1] |= M2[:, 1:]
        L2 -= (ring & ~M2) * 0.06
    L2_clean = L2.copy()
    # cracks
    hl = np.zeros_like(M2, dtype=float); dk = np.zeros_like(M2, dtype=float)
    for cn, cf, pts in CRACKS:
        if cn == name and cf == face:
            for (cu, cv) in raster_line(pts):
                if 0 <= cv < h and 0 <= cu < w:
                    dk[cv, cu] = 1
                    if cv + 1 < h: hl[cv + 1, cu] = max(hl[cv + 1, cu], 1)
    hl[dk > 0] = 0
    L2 -= dk * 0.20; L2 += hl * 0.07
    Lq = np.round(L2 / QUANT) * QUANT
    col = ramp(Lq.ravel(), STONE).reshape(h, w, 3)
    if name == "Head" and face == "front":
        for cx in (-10, 10):
            d = np.hypot((P[:, 0] - cx) / 4.0, (P[:, 1] - 28.5) / 2.0).reshape(h, w)
            col += (d < 1)[..., None] * np.array([7, 1, -4])                # tiny orange subsurface hint
    # moss on top
    if M2.any():
        clump = vnoise(P * np.array([1, 1.6, 1]), 2.6, 5).reshape(h, w)
        Lm = np.minimum(L2_clean, 0.80) - 0.07 + np.where(clump > 0.62, 0.07, np.where(clump < 0.34, -0.06, 0))
        if sidef:
            lower_edge = np.zeros_like(M2); lower_edge[:-1, :] = M2[:-1, :] & ~M2[1:, :]
            lower_edge[-1, :] = M2[-1, :]
            Lm -= lower_edge * 0.08
            upper = np.zeros_like(M2); upper[1:, :] = M2[1:, :] & ~M2[:-1, :]
            Lm += upper * 0.05
        Lmq = np.round(Lm / QUANT) * QUANT
        mcol = ramp(Lmq.ravel(), MOSS).reshape(h, w, 3)
        col = np.where(M2[..., None], mcol, col)
    return col

def paint_moss_box_region(key):
    r = regions[key]; name, face, w, h = r["node"], r["face"], r["w"], r["h"]
    P, Nrm, U, V = region_texels(key)
    L = light_term(name, face, P, Nrm, U, V, w, h) - 0.30 * ao_term(P, Nrm, exclude={name})
    clump = vnoise(P * np.array([1, 1.4, 1]), 2.6, 6)
    L = np.minimum(L, 0.80) + np.where(clump > 0.62, 0.07, np.where(clump < 0.34, -0.06, 0)) - 0.06
    L = np.round(L / QUANT) * QUANT
    return ramp(L, MOSS).reshape(h, w, 3)

def paint_sprout_region(key):
    r = regions[key]; name, face, w, h = r["node"], r["face"], r["w"], r["h"]
    P, Nrm, U, V = region_texels(key)
    ny = Nrm[:, 1]
    if name == "Sprout":
        L = 0.42 + 0.30 * np.clip((P[:, 1] - 52.5) / 7.0, 0, 1) + np.where(Nrm[:, 0] < -0.5, 0.06, 0) + np.where(Nrm[:, 2] > 0.5, 0.04, 0)
        L = L - np.where(ny < -0.5, 0.15, 0) + np.where(ny > 0.5, 0.1, 0)
    else:  # leaf: bright top with a pale vein, darker underside/edges
        L = np.where(ny > 0.3, 0.80, np.where(ny < -0.3, 0.38, 0.58))
        if face == "top":
            L = L + np.where(V == h // 2 - 0.0, 0.0, 0)
            L = L + np.where((V == 1) | (V == 2), 0.08, 0) * (U >= 1)           # vein
            L = L - np.where((V == 0) | (V == h - 1), 0.06, 0)
            L = L + 0.10 * (U / max(w - 1, 1)) - 0.05                            # lighter towards the tip
    L = np.round(L / QUANT) * QUANT
    return ramp(L, LEAF).reshape(h, w, 3)

def paint_eye():
    D = (34, 28, 50); D2 = (52, 42, 72); HI = (228, 232, 226); H2 = (120, 118, 150)
    px = np.zeros((6, 5, 4), dtype=np.uint8)
    for v in range(6):
        for u in range(5):
            c = D2 if v >= 4 else D
            px[v, u] = (*c, 255)
    for (u, v) in [(0, 0), (4, 0), (0, 5), (4, 5)]:
        px[v, u] = (0, 0, 0, 0)
    for (u, v) in [(1, 1), (2, 1), (1, 2)]:
        px[v, u] = (*HI, 255)
    px[4, 3] = (*H2, 255)
    return px

def paint_mouth():
    D = (40, 28, 46); IN = (92, 46, 62)
    px = np.zeros((3, 10, 4), dtype=np.uint8)
    for u in (0, 9): px[0, u] = (*D, 255)
    for u in range(1, 9): px[1, u] = (*D, 255)
    for u in range(2, 8): px[2, u] = (*IN, 255)
    return px

# ------------------------------------------------------------------ build texture
tex = np.zeros((TEX_H, TEX_W, 4), dtype=np.uint8)
for key, r in sorted(regions.items()):
    name = r["node"]
    if name in STONE_NODES:
        col = paint_stone_region(key)
    elif name in MOSS_NODES:
        col = paint_moss_box_region(key)
    elif name.startswith("Sprout"):
        col = paint_sprout_region(key)
    else:
        continue
    col = np.clip(np.round(col), 22, 236).astype(np.uint8)
    tex[r["y"]:r["y"] + r["h"], r["x"]:r["x"] + r["w"], :3] = col
    tex[r["y"]:r["y"] + r["h"], r["x"]:r["x"] + r["w"], 3] = 255

# toes: two notches on the foot front
fr = regions[("L-Foot", "front")]
for u in (4, 9):
    for v in range(2, 7):
        y, x = fr["y"] + v, fr["x"] + u
        tex[y, x, :3] = (tex[y, x, :3] * 0.72).astype(np.uint8)
    y, x = fr["y"] + 1, fr["x"] + u
    tex[y, x, :3] = (tex[y, x, :3] * 0.85).astype(np.uint8)

def put(key, px):
    r = regions[key]
    tex[r["y"]:r["y"] + r["h"], r["x"]:r["x"] + r["w"]] = px

put(("L-Eye", "front"), paint_eye())
put(("Mouth", "front"), paint_mouth())
# eyelid = the head-front stone right where the eye sits, with a dark lash line at the bottom
hf = regions[("Head", "front")]
lid = np.zeros((6, 5, 4), dtype=np.uint8)
# head front: u = x + 23, v = 44 - y ; eye L at x 7.5..12.5, y 30..36
patch = tex[hf["y"] + (44 - 36): hf["y"] + (44 - 30), hf["x"] + 31: hf["x"] + 36, :3].astype(float)
lid[..., :3] = np.clip(patch * 1.02, 22, 236).astype(np.uint8); lid[..., 3] = 255
lid[5, :, :3] = (58, 50, 76); lid[4, :, :3] = np.clip(lid[4, :, :3] * 0.86, 22, 236)
for (u, v) in [(0, 0), (4, 0), (0, 5), (4, 5)]:
    lid[v, u] = (0, 0, 0, 0)
lid[5, 1] = (58, 50, 76, 255); lid[5, 3] = (58, 50, 76, 255)
put(("L-Eyelid", "front"), lid)

os.makedirs(NPC_DIR, exist_ok=True)
Image.fromarray(tex, "RGBA").save(os.path.join(NPC_DIR, "Pebble_Texture.png"), optimize=False)

# ------------------------------------------------------------------ blockymodel
_id = [0]
def node_json(n):
    _id[0] += 1
    shp = n["shape"]
    shape = {"type": "none", "offset": vec(n["offset"]), "stretch": vec((1, 1, 1)), "settings": {"isPiece": False},
             "textureLayout": {}, "unwrapMode": "custom", "visible": True, "doubleSided": False, "shadingMode": "flat"}
    if shp:
        t, size, _ = shp
        shape["type"] = t
        shape["stretch"] = vec(n["stretch"])
        shape["settings"] = {"size": {"x": size[0], "y": size[1], "z": size[2]}} if t == "box" else {"size": {"x": size[0], "y": size[1]}}
        tl = {}
        for f in faces_of(n):
            rk, mir = layout[(n["name"], f)]
            r = regions[rk]
            tl[f] = {"offset": {"x": r["x"], "y": r["y"]}, "mirror": {"x": mir, "y": False}, "angle": 0}
        shape["textureLayout"] = tl
    q = n["quat"]
    out = {"id": str(_id[0]), "name": n["name"], "position": vec(n["position"]),
           "orientation": {"x": r6(q[0]), "y": r6(q[1]), "z": r6(q[2]), "w": r6(q[3])}, "shape": shape}
    kids = [c for c in NODES if c["parent"] == n["name"]]
    if kids:
        out["children"] = [node_json(c) for c in kids]
    return out

def vec(v):
    return {"x": r6(v[0]), "y": r6(v[1]), "z": r6(v[2])}

model = {"nodes": [node_json(n) for n in NODES if n["parent"] is None], "format": "character", "lod": "auto"}
with open(os.path.join(NPC_DIR, "Pebble.blockymodel"), "w") as fh:
    json.dump(model, fh, indent=2)
    fh.write("\n")

# ------------------------------------------------------------------ animations
anim_files = pebble_anims.write_all(NPC_DIR)

print(f"texture {TEX_W}x{TEX_H}, regions {len(regions)}, nodes {len(NODES)}, anims {len(anim_files)} -> {OUT}")
for f in anim_files: print(f"  {f['folder']}/{f['name']}: {f['duration_frames']} frames ({f['seconds']} s) hold={f['holdLastKeyframe']}")
