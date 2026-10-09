#!/usr/bin/env python3
"""Small software renderer for the Dark Leather armor previews.

Reads the REAL output .blockymodel + _Texture.png files and attaches every isPiece node to the matching bone of a
plain grey mannequin (ga_rig.py), the same way the Hytale Models plugin does: children of a piece are placed relative
to the bone's box centre. Draws boxes and quads with their textureLayout (cut-out alpha, double-sided, negative-stretch
mirroring). Lighting = a mild per-face factor (painted light dominates, like the 'flat' shading mode); in-game light,
bloom and AO are not simulated.
"""
import json, math, os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ga_common import quat_to_mat, mat4
import ga_rig as RIG

BODY_COL = np.array((168, 168, 172), float)


def load_piece(model_path):
    m = json.load(open(model_path, encoding="utf-8-sig"))
    tex = np.asarray(Image.open(model_path.replace(".blockymodel", "_Texture.png")).convert("RGBA"), float)
    return m, tex


def _box_faces(M, off, size, st, shp, tex_id, name, double):
    w, h, d = size
    hx, hy, hz = w / 2, h / 2, d / 2
    defs = {
        "front": ([(-hx, hy, hz), (hx, hy, hz), (hx, -hy, hz), (-hx, -hy, hz)], (w, h)),
        "back": ([(hx, hy, -hz), (-hx, hy, -hz), (-hx, -hy, -hz), (hx, -hy, -hz)], (w, h)),
        "left": ([(-hx, hy, -hz), (-hx, hy, hz), (-hx, -hy, hz), (-hx, -hy, -hz)], (d, h)),
        "right": ([(hx, hy, hz), (hx, hy, -hz), (hx, -hy, -hz), (hx, -hy, hz)], (d, h)),
        "top": ([(-hx, hy, -hz), (hx, hy, -hz), (hx, hy, hz), (-hx, hy, hz)], (w, d)),
        "bottom": ([(-hx, -hy, hz), (hx, -hy, hz), (hx, -hy, -hz), (-hx, -hy, -hz)], (w, d)),
    }
    flip = np.prod(np.sign(st)) < 0
    out = []
    for fname, tl in shp["textureLayout"].items():
        if shp["type"] == "quad" and fname != "front":
            continue
        corners, (uw, vh) = defs[fname]
        loc = np.array(corners) * st + off
        cw = (M @ np.c_[loc, np.ones(4)].T).T[:, :3]
        ox, oy = tl["offset"]["x"], tl["offset"]["y"]
        u0, u1 = (ox + uw, ox) if tl["mirror"]["x"] else (ox, ox + uw)
        v0, v1 = (oy + vh, oy) if tl["mirror"]["y"] else (oy, oy + vh)
        assert tl.get("angle", 0) == 0
        uvs = np.array([(u0, v0), (u1, v0), (u1, v1), (u0, v1)], float)
        if flip:
            cw = cw[[1, 0, 3, 2]]; uvs = uvs[[1, 0, 3, 2]]
        nrm = np.cross(cw[1] - cw[0], cw[3] - cw[0]); nrm /= (np.linalg.norm(nrm) or 1)
        out.append(dict(P=cw, UV=uvs, tex=tex_id, n=nrm, name=name, face=fname, double=double))
        if double:
            out.append(dict(P=cw[[1, 0, 3, 2]], UV=uvs[[1, 0, 3, 2]], tex=tex_id, n=-nrm, name=name, face=fname + "-in",
                            double=False))
    return out


def armor_faces(model, tex_id, pose=None, hide=()):
    faces = []
    def walk(node, frame):
        shp = node["shape"]
        if shp.get("settings", {}).get("isPiece"):
            F = RIG.bone_center_matrix(node["name"], pose)
            for c in node.get("children", []):
                walk(c, F)
            return
        if node["name"] in hide:
            return
        q = tuple(node["orientation"][k] for k in "xyzw")
        pos = [node["position"][k] for k in "xyz"]
        M = frame @ mat4(quat_to_mat(q), pos)
        off = np.array([shp["offset"][k] for k in "xyz"], float)
        if shp["type"] in ("box", "quad") and shp.get("visible", True):
            st = np.array([shp["stretch"][k] for k in "xyz"], float)
            sz = shp["settings"]["size"]
            faces.extend(_box_faces(M, off, (sz["x"], sz["y"], sz.get("z", 0)), st, shp, tex_id, node["name"],
                                    bool(shp.get("doubleSided"))))
        for c in node.get("children", []):
            walk(c, M @ mat4(None, off))
    for n in model["nodes"]:
        walk(n, np.eye(4))
    return faces


def body_faces(pose=None, skip=()):
    faces = []
    for name, M, size in RIG.mannequin_boxes(pose):
        if name in skip:
            continue
        shp = {"type": "box", "textureLayout": {f: {"offset": {"x": 0, "y": 0}, "mirror": {"x": False, "y": False}}
                                                for f in ("front", "back", "left", "right", "top", "bottom")}}
        for f in _box_faces(M, np.zeros(3), size, np.ones(3), shp, -1, "body:" + name, False):
            faces.append(f)
    return faces


def view_matrix(yaw_deg, pitch_deg):
    y, p = math.radians(yaw_deg), math.radians(pitch_deg)
    Ry = np.array([[math.cos(y), 0, math.sin(y)], [0, 1, 0], [-math.sin(y), 0, math.cos(y)]])
    Rx = np.array([[1, 0, 0], [0, math.cos(p), -math.sin(p)], [0, math.sin(p), math.cos(p)]])
    return Rx @ Ry


def render(faces, textures, yaw=0, pitch=0, size=512, scale=None, center=None, ss=2, bg=(0, 0, 0, 0), fill=0.86,
           light=True):
    """yaw 0 = looking at the front (+Z). Positive yaw turns the model so its LEFT side (+X) shows."""
    R = view_matrix(-yaw, pitch)
    allP = np.concatenate([f["P"] for f in faces]) @ R.T
    if center is None:
        center = (allP.min(0) + allP.max(0)) / 2
    if scale is None:
        ext = (allP.max(0) - allP.min(0))[:2].max()
        scale = fill * size / ext
    S = size * ss
    color = np.zeros((S, S, 4)); color[...] = np.array(bg, float)
    zbuf = np.full((S, S), -1e9)
    for f in faces:
        V = f["P"] @ R.T
        x = (V[:, 0] - center[0]) * scale * ss + S / 2
        y = S / 2 - (V[:, 1] - center[1]) * scale * ss
        Q = np.c_[x, y, V[:, 2]]
        nw = f["n"]
        shade = (0.88 + 0.12 * nw[1] + 0.03 * nw[2]) if light else 1.0
        if f["face"].endswith("-in"):
            shade *= 0.8
        T = textures[f["tex"]] if f["tex"] >= 0 else None
        for tri in ((0, 1, 2), (0, 2, 3)):
            A, B, C = Q[list(tri)]
            area = (B[0] - A[0]) * (C[1] - A[1]) - (B[1] - A[1]) * (C[0] - A[0])
            if area <= 0:
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
            sub = zbuf[ymin:ymax + 1, xmin:xmax + 1]
            if T is not None:
                uvA, uvB, uvC = f["UV"][list(tri)]
                u = w0 * uvA[0] + w1 * uvB[0] + w2 * uvC[0]
                v = w0 * uvA[1] + w1 * uvB[1] + w2 * uvC[1]
                TH, TW = T.shape[:2]
                ui = np.clip(np.floor(u).astype(int), 0, TW - 1); vi = np.clip(np.floor(v).astype(int), 0, TH - 1)
                texel = T[vi, ui]
                ok = inside & (texel[..., 3] > 127) & (z > sub)
                rgb = texel[..., :3] * shade
            else:
                # mannequin: plain grey, gentle top-down gradient
                ok = inside & (z > sub)
                g = BODY_COL * (0.80 + 0.2 * nw[1] + 0.05 * nw[2])
                rgb = np.broadcast_to(g, xs.shape + (3,))
            sub[ok] = z[ok]
            csub = color[ymin:ymax + 1, xmin:xmax + 1]
            csub[ok] = np.c_[rgb[ok], np.full(ok.sum(), 255.0)]
    img = Image.fromarray(np.clip(color, 0, 255).astype(np.uint8), "RGBA")
    if ss > 1:
        img = img.resize((size, size), Image.LANCZOS)
    return img, dict(center=center, scale=scale)


def load_set(model_dir, pieces=("Head", "Chest", "Hands", "Legs")):
    models, texs = [], []
    for i, p in enumerate(pieces):
        m, t = load_piece(os.path.join(model_dir, p + ".blockymodel"))
        models.append(m); texs.append(t)
    return models, texs


def set_faces(models, pose=None, body=True, body_skip=()):
    faces = []
    for i, m in enumerate(models):
        faces += armor_faces(m, i, pose)
    if body:
        faces += body_faces(pose, body_skip)
    return faces


if __name__ == "__main__":
    d = sys.argv[1]
    models, texs = load_set(d)
    faces = set_faces(models)
    out = Image.new("RGBA", (4 * 400, 520), (226, 226, 230, 255))
    sc = None
    for i, yaw in enumerate((0, 90, 180, -35)):
        img, info = render(faces, texs, yaw=yaw, pitch=8 if yaw != -35 else 14, size=400, bg=(226, 226, 230, 255),
                           center=np.array([0, 62, 0]) if False else None)
        out.paste(img, (i * 400, 60))
    out.save(sys.argv[2])
