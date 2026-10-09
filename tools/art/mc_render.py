#!/usr/bin/env python3
"""Small software renderer for the Monk claws previews + icons (based on tools/art/render_blocky.py).

Reads the REAL output .blockymodel + texture PNG (+ optional .blockyanim) and draws every box with its textureLayout.
Node frames follow the Hytale plugin: a child is placed relative to its parent's pivot + the parent's shape offset.
Any view rotation (3x3) is allowed; orthographic. Shading = painted texture x a mild per-face factor (in-game light not simulated).
"""
import math
import numpy as np
from PIL import Image
from pebble_common import quat_to_mat, quat_mul, mat4, nlerp


def _catmull(p0, p1, p2, p3, t):
    t2, t3 = t * t, t * t * t
    return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)


def sample_track(kfs, time, kind):
    if not kfs:
        return None
    keys = sorted(kfs, key=lambda k: k["time"])

    def val(k):
        d = k["delta"]
        if kind == "quat":
            return np.array([d["x"], d["y"], d["z"], d["w"]])
        if kind == "bool":
            return d
        return np.array([d["x"], d["y"], d["z"]])
    if kind == "bool":
        cur = keys[0]["delta"]
        for k in keys:
            if k["time"] <= time:
                cur = k["delta"]
        return cur
    if time <= keys[0]["time"]:
        return val(keys[0])
    if time >= keys[-1]["time"]:
        return val(keys[-1])
    for k0, k1 in zip(keys, keys[1:]):
        if k0["time"] <= time <= k1["time"]:
            f = (time - k0["time"]) / float(k1["time"] - k0["time"])
            if kind == "quat":
                return np.array(nlerp(tuple(val(k0)), tuple(val(k1)), f))
            return val(k0) + (val(k1) - val(k0)) * f


def pose(anim, time):
    out = {}
    if not anim:
        return out
    for name, ch in anim["nodeAnimations"].items():
        out[name] = dict(pos=sample_track(ch["position"], time, "vec"), quat=sample_track(ch["orientation"], time, "quat"),
                         stretch=sample_track(ch["shapeStretch"], time, "vec"),
                         visible=sample_track(ch["shapeVisible"], time, "bool"))
    return out


DEFS = None


def box_corners(hx, hy, hz):
    return {
        "front": [(-hx, hy, hz), (hx, hy, hz), (hx, -hy, hz), (-hx, -hy, hz)],
        "back": [(hx, hy, -hz), (-hx, hy, -hz), (-hx, -hy, -hz), (hx, -hy, -hz)],
        "left": [(-hx, hy, -hz), (-hx, hy, hz), (-hx, -hy, hz), (-hx, -hy, -hz)],
        "right": [(hx, hy, hz), (hx, hy, -hz), (hx, -hy, -hz), (hx, -hy, hz)],
        "top": [(-hx, hy, -hz), (hx, hy, -hz), (hx, hy, hz), (-hx, hy, hz)],
        "bottom": [(-hx, -hy, hz), (hx, -hy, hz), (hx, -hy, -hz), (-hx, -hy, -hz)],
    }


def collect_faces(model, anim=None, time=0):
    P = pose(anim, time)
    faces = []

    def walk(node, parent_M, parent_offset):
        d = P.get(node["name"], {})
        pos = np.array([node["position"][k] for k in "xyz"], dtype=float)
        if d.get("pos") is not None:
            pos = pos + d["pos"]
        q = tuple(node["orientation"][k] for k in "xyzw")
        if d.get("quat") is not None:
            q = quat_mul(q, tuple(d["quat"]))
        M = parent_M @ mat4(None, parent_offset) @ mat4(quat_to_mat(q), pos)
        shp = node["shape"]
        off = np.array([shp["offset"][k] for k in "xyz"], dtype=float)
        vis = shp.get("visible", True)
        if d.get("visible") is not None:
            vis = d["visible"]
        if shp["type"] == "box" and vis:
            st = np.array([shp["stretch"][k] for k in "xyz"], dtype=float)
            if d.get("stretch") is not None:
                st = st * d["stretch"]
            sz = shp["settings"]["size"]
            w, h, dd = sz["x"], sz["y"], sz["z"]
            C = box_corners(w * st[0] / 2, h * st[1] / 2, dd * st[2] / 2)
            uvwh = {"front": (w, h), "back": (w, h), "left": (dd, h), "right": (dd, h), "top": (w, dd), "bottom": (w, dd)}
            for fname, tl in shp["textureLayout"].items():
                cw = (M @ np.c_[np.array(C[fname]) + off, np.ones(4)].T).T[:, :3]
                uw, vh = uvwh[fname]
                ox, oy = tl["offset"]["x"], tl["offset"]["y"]
                uvs = np.array([(ox, oy), (ox + uw, oy), (ox + uw, oy + vh), (ox, oy + vh)], dtype=float)
                faces.append(dict(P=cw, UV=uvs, name=node["name"], face=fname))
        for c in node.get("children", []):
            walk(c, M, off)
    for n in model["nodes"]:
        walk(n, np.eye(4), np.zeros(3))
    return faces


def rot_basis(cam_dir, up_hint, roll_deg=0.0):
    """3x3 view rotation: model vector -> screen (x right, y up, z towards viewer). cam_dir = model-space direction to the viewer."""
    c = np.array(cam_dir, float); c /= np.linalg.norm(c)
    u = np.array(up_hint, float); u = u - c * (u @ c); u /= np.linalg.norm(u)
    r = np.cross(u, c)
    R = np.stack([r, u, c])
    a = math.radians(roll_deg)
    Rz = np.array([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]])
    return Rz @ R


def bounds(model, R, anim=None, time=0):
    faces = collect_faces(model, anim, time)
    allP = np.concatenate([f["P"] for f in faces]) @ R.T
    return allP.min(0), allP.max(0)


def render(model, tex, R, size=512, scale=None, center=None, ss=3, bg=(0, 0, 0, 0), anim=None, time=0, fill=0.86,
           light=(-0.45, 0.7, 0.55), shade_amt=0.22, wh=None):
    T = np.asarray(tex.convert("RGBA"), dtype=np.float64)
    TH, TW = T.shape[:2]
    faces = collect_faces(model, anim, time)
    allP = np.concatenate([f["P"] for f in faces]) @ R.T
    W, H = (size, size) if wh is None else wh
    if center is None:
        center = (allP.min(0) + allP.max(0)) / 2
    if scale is None:
        ext = allP.max(0) - allP.min(0)
        scale = fill * min(W / ext[0], H / ext[1])
    SW, SH = W * ss, H * ss
    color = np.zeros((SH, SW, 4)); color[...] = np.array(bg, dtype=float)
    zbuf = np.full((SH, SW), -1e9)
    Lv = np.array(light, float); Lv /= np.linalg.norm(Lv)
    for f in faces:
        V = f["P"] @ R.T
        n = np.cross(V[1] - V[0], V[3] - V[0])
        nn = np.linalg.norm(n)
        if nn < 1e-9:
            continue
        n /= nn
        k = (1.0 - shade_amt) + shade_amt * max(0.0, float(n @ Lv)) * 1.25
        Q = np.c_[(V[:, 0] - center[0]) * scale * ss + SW / 2, SH / 2 - (V[:, 1] - center[1]) * scale * ss, V[:, 2]]
        for tri in ((0, 1, 2), (0, 2, 3)):
            A, B, C = Q[list(tri)]
            uvA, uvB, uvC = f["UV"][list(tri)]
            area = (B[0] - A[0]) * (C[1] - A[1]) - (B[1] - A[1]) * (C[0] - A[0])
            if area <= 0:
                continue
            xmin = max(int(math.floor(min(A[0], B[0], C[0]))), 0); xmax = min(int(math.ceil(max(A[0], B[0], C[0]))), SW - 1)
            ymin = max(int(math.floor(min(A[1], B[1], C[1]))), 0); ymax = min(int(math.ceil(max(A[1], B[1], C[1]))), SH - 1)
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
            rgb = np.clip(texel[..., :3] * k, 0, 255)
            csub[ok] = np.c_[rgb[ok], np.full(ok.sum(), 255.0)]
    img = Image.fromarray(np.clip(color, 0, 255).astype(np.uint8), "RGBA")
    if ss > 1:
        img = img.resize((W, H), Image.LANCZOS)
    return img, dict(center=center, scale=scale)
