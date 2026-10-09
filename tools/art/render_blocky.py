#!/usr/bin/env python3
"""Tiny software renderer for .blockymodel (+ optional .blockyanim) files - used for Pebble previews.

Reads the REAL output files (model JSON, texture PNG, animation JSON) and draws every box / quad with its
textureLayout, so previews show exactly what was exported. Lighting is a mild per-face factor to mimic the
'flat' shading mode (painted light dominates); in-game lighting/bloom/AO are not simulated.
"""
import json, math, sys
import numpy as np
from PIL import Image
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from pebble_common import quat_to_mat, quat_mul, mat4, nlerp

FACE_SHADE = {"top": 1.0, "front": 0.96, "left": 0.93, "right": 0.90, "back": 0.88, "bottom": 0.78}

def load(path):
    with open(path) as fh:
        return json.load(fh)

# ---------------------------------------------------------------- animation sampling
def _catmull(p0, p1, p2, p3, t):
    t2, t3 = t * t, t * t * t
    return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)

def sample_track(kfs, time, duration, kind):
    if not kfs:
        return None
    keys = sorted(kfs, key=lambda k: k["time"])
    def val(k):
        d = k["delta"]
        if kind == "quat": return np.array([d["x"], d["y"], d["z"], d["w"]])
        if kind == "bool": return d
        return np.array([d["x"], d["y"], d["z"]])
    if kind == "bool":
        cur = keys[0]["delta"]
        for k in keys:
            if k["time"] <= time: cur = k["delta"]
        return cur
    if len(keys) == 1:
        return val(keys[0])
    # loop wrapping like the plugin: segment from last key back to first key (+duration)
    times = [k["time"] for k in keys]
    ext = [(keys[-1]["time"] - duration, keys[-1])] + [(k["time"], k) for k in keys] + [(k["time"] + duration, k) for k in keys[:2]]
    for i in range(1, len(ext) - 2):
        t0, k0 = ext[i]; t1, k1 = ext[i + 1]
        if t0 <= time <= t1:
            f = 0 if t1 == t0 else (time - t0) / (t1 - t0)
            if kind == "quat":
                return np.array(nlerp(tuple(val(k0)), tuple(val(k1)), f))
            if k1["interpolationType"] == "smooth" and k0["interpolationType"] == "smooth":
                return _catmull(val(ext[i - 1][1]), val(k0), val(k1), val(ext[i + 2][1]), f)
            return val(k0) + (val(k1) - val(k0)) * f
    return val(keys[0])

def pose(anim, time):
    """node name -> dict(pos, quat, stretch, visible) deltas"""
    out = {}
    if not anim:
        return out
    D = anim["duration"]
    if anim.get("holdLastKeyframe"):
        time = min(time, D)
    else:
        time = time % D
    for name, ch in anim["nodeAnimations"].items():
        out[name] = dict(pos=sample_track(ch["position"], time, D, "vec"),
                         quat=sample_track(ch["orientation"], time, D, "quat"),
                         stretch=sample_track(ch["shapeStretch"], time, D, "vec"),
                         visible=sample_track(ch["shapeVisible"], time, D, "bool"))
    return out

# ---------------------------------------------------------------- geometry
def collect_faces(model, anim=None, time=0):
    P = pose(anim, time)
    faces = []
    def walk(node, parent_M, parent_offset):
        d = P.get(node["name"], {})
        pos = np.array([node["position"][k] for k in "xyz"], dtype=float)
        if d.get("pos") is not None: pos = pos + d["pos"]
        q = tuple(node["orientation"][k] for k in "xyzw")
        if d.get("quat") is not None: q = quat_mul(q, tuple(d["quat"]))
        M = parent_M @ mat4(None, parent_offset) @ mat4(quat_to_mat(q), pos)
        shp = node["shape"]
        off = np.array([shp["offset"][k] for k in "xyz"], dtype=float)
        vis = shp.get("visible", True)
        if d.get("visible") is not None: vis = d["visible"]
        if shp["type"] in ("box", "quad") and vis:
            st = np.array([shp["stretch"][k] for k in "xyz"], dtype=float)
            if d.get("stretch") is not None: st = st * d["stretch"]
            sz = shp["settings"]["size"]
            size = np.array([sz["x"], sz["y"], sz.get("z", 0)], dtype=float)
            faces.extend(box_faces(M, off, size, st, shp, node["name"]))
        for c in node.get("children", []):
            walk(c, M, off)
    for n in model["nodes"]:
        walk(n, np.eye(4), np.zeros(3))
    return faces

def box_faces(M, off, size, st, shp, name):
    w, h, d = size
    hx, hy, hz = w * st[0] / 2, h * st[1] / 2, d * st[2] / 2
    # corners per face in order: top-left, top-right, bottom-right, bottom-left (as seen in the texture)
    defs = {
        "front": ([(-hx, hy, hz), (hx, hy, hz), (hx, -hy, hz), (-hx, -hy, hz)], (w, h)),
        "back": ([(hx, hy, -hz), (-hx, hy, -hz), (-hx, -hy, -hz), (hx, -hy, -hz)], (w, h)),
        "left": ([(-hx, hy, -hz), (-hx, hy, hz), (-hx, -hy, hz), (-hx, -hy, -hz)], (d, h)),
        "right": ([(hx, hy, hz), (hx, hy, -hz), (hx, -hy, -hz), (hx, -hy, hz)], (d, h)),
        "top": ([(-hx, hy, -hz), (hx, hy, -hz), (hx, hy, hz), (-hx, hy, hz)], (w, d)),
        "bottom": ([(-hx, -hy, hz), (hx, -hy, hz), (hx, -hy, -hz), (-hx, -hy, -hz)], (w, d)),
    }
    out = []
    for fname, tl in shp["textureLayout"].items():
        if shp["type"] == "quad" and fname != "front":
            continue
        corners, (uw, vh) = defs[fname]
        cw = (M @ np.c_[np.array(corners) + off, np.ones(4)].T).T[:, :3]
        ox, oy = tl["offset"]["x"], tl["offset"]["y"]
        # mirror: the axis runs from the offset towards negative (matches Blockbench 5.2.1 + Hytale Models 0.10.0)
        u0, u1 = (ox, ox - uw) if tl["mirror"]["x"] else (ox, ox + uw)
        v0, v1 = (oy, oy - vh) if tl["mirror"]["y"] else (oy, oy + vh)
        assert tl.get("angle", 0) == 0
        uvs = np.array([(u0, v0), (u1, v0), (u1, v1), (u0, v1)], dtype=float)
        out.append(dict(P=cw, UV=uvs, shade=FACE_SHADE[fname], double=bool(shp.get("doubleSided")),
                        name=name, face=fname))
        if shp["type"] == "quad" and shp.get("doubleSided"):
            out.append(dict(P=cw[[1, 0, 3, 2]], UV=uvs[[1, 0, 3, 2]], shade=0.85, double=False, name=name, face="back"))
    return out

# ---------------------------------------------------------------- raster
def view_matrix(yaw_deg, pitch_deg):
    y, p = math.radians(yaw_deg), math.radians(pitch_deg)
    Ry = np.array([[math.cos(y), 0, math.sin(y)], [0, 1, 0], [-math.sin(y), 0, math.cos(y)]])
    Rx = np.array([[1, 0, 0], [0, math.cos(p), -math.sin(p)], [0, math.sin(p), math.cos(p)]])
    return Rx @ Ry

def render(model, tex, yaw=0, pitch=0, size=512, anim=None, time=0, scale=None, center=None, ss=2,
           bg=(0, 0, 0, 0), ground=False, return_bounds=False):
    """yaw: degrees, 0 = looking at the model's front (+Z face). Positive yaw shows the model's left side (+X)."""
    T = np.asarray(tex, dtype=np.float64)
    TH, TW = T.shape[:2]
    faces = collect_faces(model, anim, time)
    R = view_matrix(-yaw, pitch)
    allP = np.concatenate([f["P"] for f in faces]) @ R.T
    if center is None:
        center = (allP.min(0) + allP.max(0)) / 2
    if scale is None:
        ext = (allP.max(0) - allP.min(0))[:2].max()
        scale = 0.8 * size / ext
    S = size * ss
    color = np.zeros((S, S, 4)); color[...] = np.array(bg, dtype=float)
    zbuf = np.full((S, S), -1e9)
    def proj(Pw):
        V = Pw @ R.T
        x = (V[:, 0] - center[0]) * scale * ss + S / 2
        y = S / 2 - (V[:, 1] - center[1]) * scale * ss
        return np.c_[x, y, V[:, 2]]
    for f in faces:
        Q = proj(f["P"])
        for tri in ((0, 1, 2), (0, 2, 3)):
            A, B, C = Q[list(tri)]
            uvA, uvB, uvC = f["UV"][list(tri)]
            area = (B[0] - A[0]) * (C[1] - A[1]) - (B[1] - A[1]) * (C[0] - A[0])
            if area <= 0:   # back-facing (TL,TR,BR order gives positive area on screen when facing the camera)
                continue
            xmin = max(int(math.floor(min(A[0], B[0], C[0]))), 0); xmax = min(int(math.ceil(max(A[0], B[0], C[0]))), S - 1)
            ymin = max(int(math.floor(min(A[1], B[1], C[1]))), 0); ymax = min(int(math.ceil(max(A[1], B[1], C[1]))), S - 1)
            if xmin > xmax or ymin > ymax:
                continue
            xs, ys = np.meshgrid(np.arange(xmin, xmax + 1) + 0.5, np.arange(ymin, ymax + 1) + 0.5)
            w0 = ((B[0] - xs) * (C[1] - ys) - (B[1] - ys) * (C[0] - xs)) / area
            w1 = ((C[0] - xs) * (A[1] - ys) - (C[1] - ys) * (A[0] - xs)) / area
            w2 = 1 - w0 - w1
            inside = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
            if not inside.any():
                continue
            z = w0 * A[2] + w1 * B[2] + w2 * C[2]
            u = w0 * uvA[0] + w1 * uvB[0] + w2 * uvC[0]
            v = w0 * uvA[1] + w1 * uvB[1] + w2 * uvC[1]
            ui = np.clip(np.floor(u).astype(int), 0, TW - 1); vi = np.clip(np.floor(v).astype(int), 0, TH - 1)
            texel = T[vi, ui]
            sub = zbuf[ymin:ymax + 1, xmin:xmax + 1]
            ok = inside & (texel[..., 3] > 127) & (z > sub)
            sub[ok] = z[ok]
            csub = color[ymin:ymax + 1, xmin:xmax + 1]
            rgb = texel[..., :3] * f["shade"]
            csub[ok] = np.c_[rgb[ok], np.full(ok.sum(), 255.0)]
    img = Image.fromarray(np.clip(color, 0, 255).astype(np.uint8), "RGBA")
    if ss > 1:
        img = img.resize((size, size), Image.LANCZOS)
    if return_bounds:
        return img, dict(center=center, scale=scale)
    return img

if __name__ == "__main__":
    model = load(sys.argv[1]); tex = Image.open(sys.argv[2]).convert("RGBA")
    anim = load(sys.argv[4]) if len(sys.argv) > 4 else None
    t = float(sys.argv[5]) if len(sys.argv) > 5 else 0
    render(model, tex, yaw=float(sys.argv[3]), pitch=12, anim=anim, time=t, bg=(214, 222, 228, 255)).save("/tmp/r.png")
