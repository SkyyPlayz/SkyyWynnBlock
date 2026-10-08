#!/usr/bin/env python3
"""Build the SkyWynn Dark Leather light armor: 4 .blockymodel attachments (Head, Chest, Hands, Legs) + textures.

Deterministic (two runs = same bytes). Original geometry and pixels only (dl_design.py); the player rig numbers in
dl_rig.py are used only to place pieces on the right bones.
Usage: python3 make_dark_leather.py [out_dir]   (default: ../../art/dark-leather-armor)
"""
import json, math, os, sys, time
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dl_common import quat_from_euler_zyx, quat_to_mat, mat4, r6, FACE_NORMALS, face_uv_size, face_texel_to_local
import dl_rig as RIG
import dl_paint as P
import dl_design as D

OUT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.normpath(os.path.join(HERE, "../../art/dark-leather-armor"))
SET = "SkyyDarkLeather"
MODEL_DIR = os.path.join(OUT, "Common/Items/Armors", SET)
BOX_FACES = ["front", "back", "left", "right", "top", "bottom"]


# ------------------------------------------------------------------ expand mirrored nodes
def mirror_name(n):
    if n.startswith("R-"):
        return "L-" + n[2:]
    if n.endswith("R"):
        return n[:-1] + "L"
    raise ValueError(n)


def expand(nodes):
    out = []
    for n in nodes:
        n = dict(n)
        n.setdefault("rot", (0, 0, 0)); n.setdefault("offset", (0, 0, 0)); n.setdefault("stretch", (1, 1, 1))
        n.setdefault("skip", ()); n.setdefault("double", False); n.setdefault("parent", None)
        n["type"] = "quad" if len(n["size"]) == 2 else "box"
        out.append(n)
        if n.get("mirror"):
            m = dict(n)
            m["name"] = mirror_name(n["name"])
            m["bone"] = n["bone"].replace("R-", "L-", 1) if n["bone"].startswith("R-") else n["bone"]
            m["pivot"] = (-n["pivot"][0], n["pivot"][1], n["pivot"][2])
            m["rot"] = (n["rot"][0], -n["rot"][1], -n["rot"][2])
            m["offset"] = (-n["offset"][0], n["offset"][1], n["offset"][2])
            m["stretch"] = (-n["stretch"][0], n["stretch"][1], n["stretch"][2])
            m["parent"] = mirror_name(n["parent"]) if n["parent"] else None
            m["share_of"] = n["name"]
            m["mirror"] = False
            out.append(m)
    return out


PIECES = {k: expand(v) for k, v in D.PIECES.items()}
ALL = [n for v in PIECES.values() for n in v]
BYNAME = {}
for piece, nodes in PIECES.items():
    for n in nodes:
        n["piece"] = piece
        assert n["name"] not in BYNAME, n["name"]
        BYNAME[n["name"]] = n
        for s in n["stretch"]:
            assert 0.7 <= abs(s) <= 1.3, (n["name"], n["stretch"])
        for s in n["size"]:
            assert float(s).is_integer(), (n["name"], n["size"])


def node_matrix(n, pose=None):
    """world matrix of the node pivot (rotation included)."""
    local = mat4(quat_to_mat(quat_from_euler_zyx(*n["rot"])), n["pivot"])
    if n["parent"]:
        p = BYNAME[n["parent"]]
        return node_matrix(p, pose) @ mat4(None, p["offset"]) @ local
    return RIG.bone_center_matrix(n["bone"], pose) @ local


def box_matrix(n, pose=None):
    """maps unstretched box-local coords (centred) to world."""
    S = np.diag(list(n["stretch"]) + [1.0])
    return node_matrix(n, pose) @ mat4(None, n["offset"]) @ S


def size3(n):
    s = n["size"]
    return (s[0], s[1], 0) if n["type"] == "quad" else tuple(s)


def faces_of(n):
    if n["type"] == "quad":
        return ["front"]
    return [f for f in BOX_FACES if f not in n["skip"]]


# ------------------------------------------------------------------ occluders for AO (full set at rest + body)
OCC = []
for n in ALL:
    if n["type"] == "box":
        OCC.append((n["name"], np.linalg.inv(box_matrix(n)), np.array(size3(n), float) / 2))
for name, M, size in RIG.mannequin_boxes():
    OCC.append(("body:" + name, np.linalg.inv(M), size / 2))

_rs = np.random.RandomState(5)
_D = _rs.normal(size=(28, 3)); _D /= np.linalg.norm(_D, axis=1, keepdims=True)
DISTS = [(1.3, 1.0), (2.6, 0.8), (4.5, 0.55)]


def ao_for(Wp, nrm, exclude):
    """Wp: (N,3) world points, nrm (3,). Returns (N,) occlusion 0..1."""
    dirs = _D * np.sign(_D @ nrm)[:, None]
    dirs = dirs + nrm * 0.35
    dirs /= np.linalg.norm(dirs, axis=1, keepdims=True)
    base = Wp + nrm * 0.45
    total = np.zeros(len(Wp)); wsum = 0
    for dist, w in DISTS:
        pts = (base[:, None, :] + dirs[None] * dist).reshape(-1, 3)
        hit = np.zeros(len(pts), bool)
        ph = np.c_[pts, np.ones(len(pts))]
        for name, inv, half in OCC:
            if name == exclude:
                continue
            q = ph @ inv.T
            hit |= (np.abs(q[:, 0]) < half[0]) & (np.abs(q[:, 1]) < half[1]) & (np.abs(q[:, 2]) < half[2])
        total += w * hit.reshape(len(Wp), len(dirs)).mean(1); wsum += w
    return np.clip(total / wsum * 1.6, 0, 1)


# ------------------------------------------------------------------ paint every (non-shared) face
def face_context(n, face):
    sz = size3(n)
    fw, fh = face_uv_size(face, sz) if n["type"] == "box" else (sz[0], sz[1])
    fw, fh = int(fw), int(fh)
    vv, uu = np.mgrid[0:fh, 0:fw]
    L = np.stack(np.broadcast_arrays(*[np.asarray(c, float) for c in face_texel_to_local(face, sz, uu + 0.5, vv + 0.5)]), -1).astype(float)
    if n["type"] == "quad":
        L[..., 2] = 0
    M = box_matrix(n)
    W = (np.c_[L.reshape(-1, 3), np.ones(fw * fh)] @ M.T)[:, :3].reshape(fh, fw, 3)
    R = node_matrix(n)[:3, :3]
    nl = np.array(FACE_NORMALS[face], float) * np.sign(np.array(n["stretch"], float))
    nw = R @ nl; nw /= np.linalg.norm(nw)
    # edge directions (top, bottom, left, right of the texture region)
    cen = W.reshape(-1, 3).mean(0)
    def mid(points):
        return points.reshape(-1, 3).mean(0)
    edges = [mid(W[0]), mid(W[-1]), mid(W[:, 0]), mid(W[:, -1])]
    eu, ef = [], []
    for e in edges:
        d = e - cen; ln = np.linalg.norm(d)
        d = d / ln if ln > 1e-6 else d
        eu.append(float(d[1])); ef.append(float(d[2]))
    return P.Face(n, face, fw, fh, L, W, nw, eu, ef)


def paint_all():
    tiles = {}
    t0 = time.time()
    for n in ALL:
        if n.get("share_of"):
            continue
        for face in faces_of(n):
            F = face_context(n, face)
            ao = ao_for(F.W.reshape(-1, 3), F.n, n["name"]).reshape(F.fh, F.fw)
            base = P.base_light(F, ao)
            n["paint"](F)
            tiles[(n["name"], face)] = P.compose(F, base)
    print("painted %d faces in %.1fs" % (len(tiles), time.time() - t0))
    return tiles


# ------------------------------------------------------------------ pack + write
def pack(regions, W):
    items = sorted(regions.items(), key=lambda kv: (-kv[1].shape[0], -kv[1].shape[1], kv[0]))
    x = y = shelf = 0
    pos = {}
    for key, img in items:
        h, w = img.shape[:2]
        if x + w > W:
            x, y, shelf = 0, y + shelf, 0
        pos[key] = (x, y)
        x += w; shelf = max(shelf, h)
    return pos, y + shelf


def best_pack(regions):
    best = None
    for W in (64, 96, 128, 160, 192, 224, 256):
        if max(r.shape[1] for r in regions.values()) > W:
            continue
        pos, h = pack(regions, W)
        H = int(math.ceil(h / 32.0) * 32)
        score = (W * H, abs(W - H))
        if best is None or score < best[0]:
            best = (score, W, H, pos)
    return best[1], best[2], best[3]


def dilate_rgb(img):
    """fill RGB of fully transparent texels with neighbour colours (alpha stays 0) - no dark fringes when filtered."""
    a = img[..., 3] > 0
    rgb = img[..., :3].astype(float)
    filled = a.copy()
    for _ in range(4):
        acc = np.zeros_like(rgb); cnt = np.zeros(a.shape)
        for dv, du in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            sh = np.roll(np.roll(filled, dv, 0), du, 1)
            acc += np.roll(np.roll(rgb, dv, 0), du, 1) * sh[..., None]; cnt += sh
        new = ~filled & (cnt > 0)
        rgb[new] = acc[new] / cnt[new][:, None]
        filled |= new
    out = img.copy(); out[..., :3] = np.round(rgb).astype(np.uint8)
    return out


def vec(v, keys="xyz"):
    return {k: r6(x) for k, x in zip(keys, v)}


def piece_bones(nodes):
    used = []
    for n in nodes:
        if n["bone"] not in used:
            used.append(n["bone"])
    return used


def bone_ancestor(b, used):
    p = RIG.BONE[b]["parent"]
    while p is not None and p not in used:
        p = RIG.BONE[p]["parent"]
    return p


def build_piece(piece, nodes, tiles):
    regions = {k: v for k, v in tiles.items() if BYNAME[k[0]]["piece"] == piece}
    TW, TH = best_pack(regions)[:2]
    _, _, pos = best_pack(regions)
    tex = np.zeros((TH, TW, 4), np.uint8)
    for (name, face), img in regions.items():
        x, y = pos[(name, face)]
        tex[y:y + img.shape[0], x:x + img.shape[1]] = img
    tex = dilate_rgb(tex)
    ids = iter(range(1, 1000))
    used = piece_bones(nodes)
    rest = {b: RIG.bone_center_matrix(b) for b in used}

    def shape_node(n):
        src = n.get("share_of") or n["name"]
        layout = {}
        for f in faces_of(n):
            x, y = pos[(src, f)]
            layout[f] = {"offset": {"x": x, "y": y}, "mirror": {"x": False, "y": False}, "angle": 0}
        sz = n["size"]
        settings = {"size": {"x": int(sz[0]), "y": int(sz[1])}} if n["type"] == "quad" else \
                   {"size": {"x": int(sz[0]), "y": int(sz[1]), "z": int(sz[2])}}
        if n["type"] == "quad":
            settings["normal"] = "+Z"
        q = quat_from_euler_zyx(*n["rot"])
        node = {"id": str(next(ids)), "name": n["name"], "position": vec(n["pivot"]),
                "orientation": vec(q, "xyzw"),
                "shape": {"type": n["type"], "offset": vec(n["offset"]), "stretch": vec(n["stretch"]),
                          "settings": settings, "textureLayout": layout, "unwrapMode": "custom", "visible": True,
                          "doubleSided": bool(n["double"]), "shadingMode": "flat"}}
        kids = [shape_node(c) for c in nodes if c["parent"] == n["name"]]
        if kids:
            node["children"] = kids
        return node

    def bone_node(b):
        anc = bone_ancestor(b, used)
        bo = RIG.bone_matrix(b)[:3, 3]
        if anc is None:
            position = bo
        else:
            position = bo - rest[anc][:3, 3]
        node = {"id": str(next(ids)), "name": b, "position": vec(position), "orientation": vec((0, 0, 0, 1), "xyzw"),
                "shape": {"type": "none", "offset": vec(RIG.BONE[b]["offset"]), "stretch": vec((1, 1, 1)),
                          "settings": {"isPiece": True}, "textureLayout": {}, "unwrapMode": "custom", "visible": True,
                          "doubleSided": False, "shadingMode": "flat"}}
        kids = [shape_node(c) for c in nodes if c["bone"] == b and c["parent"] is None]
        kids += [bone_node(c) for c in used if bone_ancestor(c, used) == b]
        node["children"] = kids
        return node

    roots = [bone_node(b) for b in used if bone_ancestor(b, used) is None]
    model = {"nodes": roots, "format": "character", "lod": "auto"}
    os.makedirs(MODEL_DIR, exist_ok=True)
    with open(os.path.join(MODEL_DIR, piece + ".blockymodel"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(model, fh, indent=2)
        fh.write("\n")
    Image.fromarray(tex, "RGBA").save(os.path.join(MODEL_DIR, piece + "_Texture.png"), optimize=True)
    return TW, TH


if __name__ == "__main__":
    tiles = paint_all()
    for piece, nodes in PIECES.items():
        TW, TH = build_piece(piece, nodes, tiles)
        nb = sum(1 for n in nodes if n["type"] == "box"); nq = sum(1 for n in nodes if n["type"] == "quad")
        print("%-6s %2d boxes %d quads -> %3d tris, texture %dx%d" % (piece, nb, nq, nb * 12 + nq * 2, TW, TH))
