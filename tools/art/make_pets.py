#!/usr/bin/env python3
"""Generate the SkyWynn launch pets: texture PNG, .blockymodel and .blockyanim files per pet.

Deterministic (two runs = same bytes). Original art only - no vanilla file is read. Pipeline = the Pebble generator
(tools/art/make_pebble.py) generalised to many creatures: painted light + AO + hue-shifted ramps + per-material strokes.
Usage: python3 make_pets.py [out_art_dir] [Pet ...]
"""
import json, math, os, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pets_models import PETS
from pets_common import quat_from_euler_zyx, quat_to_mat, mat4, r6, FACE_NORMALS, face_uv_size, face_texel_to_local
import pets_anims

OUT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.normpath(os.path.join(HERE, "../../art/pets"))
ONLY = sys.argv[2:]
BOX_FACES = ["front", "back", "left", "right", "top", "bottom"]
MIRROR_FACE = {"front": "front", "back": "back", "left": "right", "right": "left", "top": "top", "bottom": "bottom"}
QUANT = 0.03

def hx(s):
    s = s.lstrip("#"); return np.array([int(s[i:i + 2], 16) for i in (0, 2, 4)], dtype=float)

def make_ramp(base):
    """hue-shifted ramp around a base colour (base sits at 0.60): violet shadows, warm highlights, never pure black/white"""
    b = hx(base); cool = np.array([52, 40, 86.0]); warm = np.array([255, 240, 206.0])
    st = [(0.10, b * 0.30 * 0.55 + cool * 0.45), (0.28, b * 0.52 * 0.72 + cool * 0.28), (0.44, b * 0.76 * 0.88 + cool * 0.12),
          (0.60, b), (0.74, b * 0.78 + warm * 0.22), (0.88, b * 0.60 + warm * 0.40), (1.0, b * 0.50 + warm * 0.50)]
    return [(x, tuple(np.clip(c, 22, 236))) for x, c in st]

def ramp(values, stops):
    xs = np.array([s[0] for s in stops]); cols = np.array([s[1] for s in stops], dtype=np.float64)
    v = np.clip(values, xs[0], xs[-1])
    return np.stack([np.interp(v, xs, cols[:, c]) for c in range(3)], axis=-1)

def hash3(ix, iy, iz, seed):
    h = (ix * 374761393 + iy * 668265263 + iz * 2147483647 + seed * 144665) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 65535.0

def vnoise(p, scale, seed):
    q = np.asarray(p, dtype=np.float64) / scale
    i0 = np.floor(q).astype(np.int64); fr = q - i0; fr = fr * fr * (3 - 2 * fr)
    out = np.zeros(len(q))
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                hv = hash3(i0[:, 0] + dx, i0[:, 1] + dy, i0[:, 2] + dz, seed)
                out += hv * (fr[:, 0] if dx else 1 - fr[:, 0]) * (fr[:, 1] if dy else 1 - fr[:, 1]) * (fr[:, 2] if dz else 1 - fr[:, 2])
    return out

def step(n, hi=0.62, lo=0.36, a=0.04, b=0.04):
    return np.where(n > hi, a, np.where(n < lo, -b, 0))

# ======================================================================================== one pet
def build_pet(pname, spec):
    NODES = [dict(n) for n in spec["nodes"]]
    mats = {k: (make_ramp(v[0]), v[1], v[0]) for k, v in {**spec["mats"], **spec.get("extra_mats", {})}.items()}
    H = float(spec["height"])
    by_name = {n["name"]: n for n in NODES}
    assert len(by_name) == len(NODES), "duplicate node names"
    for n in NODES:
        n.setdefault("stretch", (1, 1, 1))
        n["quat"] = quat_from_euler_zyx(*n["rot"])
        shp = n["shape"]; n["offset"] = tuple(shp[2]) if shp else (0, 0, 0)
    for n in NODES:
        p = by_name.get(n["parent"]) if n["parent"] else None
        if p is None:
            n["position"] = tuple(n["pivot"])
        else:
            # children of a rotated parent are designed in the parent's un-rotated frame; the parent's rotation turns the whole subtree
            n["position"] = tuple(n["pivot"][i] - (p["pivot"][i] + p["offset"][i]) for i in range(3))

    def world_matrix(name):
        n = by_name[name]; local = mat4(quat_to_mat(n["quat"]), n["position"])
        if n["parent"] is None:
            return local
        p = by_name[n["parent"]]
        return world_matrix(p["name"]) @ mat4(None, p["offset"]) @ local

    def size3(n):
        t, s, _ = n["shape"]; return s if t == "box" else (s[0], s[1], 0)

    def faces_of(n):
        if not n["shape"]:
            return []
        return BOX_FACES if n["shape"][0] == "box" else ["front"]

    regions, layout = {}, {}
    for n in NODES:
        for f in faces_of(n):
            nm = n["name"]
            if "mirror_of" in n:
                layout[(nm, f)] = ((n["mirror_of"], MIRROR_FACE[f]), True)
            elif "share_of" in n:
                layout[(nm, f)] = ((n["share_of"], f), False)
            else:
                w, h = face_uv_size(f, size3(n))
                assert w == int(w) and h == int(h), (pname, nm, f, w, h)
                regions[(nm, f)] = dict(w=int(w), h=int(h), node=nm, face=f)
                layout[(nm, f)] = ((nm, f), False)

    area = sum(r["w"] * r["h"] for r in regions.values())
    TW = 128 if area < 128 * 128 * 0.62 else 256

    def pack(W, pad=1):
        items = sorted(regions.items(), key=lambda kv: (-kv[1]["h"], -kv[1]["w"], kv[0]))
        x = y = shelf = 0; pos = {}
        for key, r in items:
            if x + r["w"] > W:
                x, y, shelf = 0, y + shelf + pad, 0
            pos[key] = (x, y); x += r["w"] + pad; shelf = max(shelf, r["h"])
        return pos, y + shelf
    pos, used = pack(TW)
    TH = int(math.ceil(used / 32.0) * 32)
    for k, p in pos.items():
        regions[k]["x"], regions[k]["y"] = p

    OCC = []
    for n in NODES:
        if n["shape"] and n["shape"][0] == "box":
            M = world_matrix(n["name"]) @ mat4(None, n["offset"])
            OCC.append((n["name"], np.linalg.inv(M), np.array(size3(n)) / 2.0))
    rng = np.random.RandomState(7)
    DIRS = rng.normal(size=(24, 3)); DIRS /= np.linalg.norm(DIRS, axis=1, keepdims=True)

    def ao_term(P, Nrm, exclude):
        occl = np.zeros(len(P)); total = 0
        for d in DIRS:
            dd = np.where((Nrm @ d)[:, None] < 0, -d, d)
            for dist in (1.0, 2.0, 3.5):
                S = P + Nrm * 0.25 + dd * dist
                hit = np.zeros(len(P), dtype=bool)
                for nm, Minv, half in OCC:
                    if nm in exclude:
                        continue
                    L = (np.c_[S, np.ones(len(S))] @ Minv.T)[:, :3]
                    hit |= np.all(np.abs(L) < half - 0.01, axis=1)
                occl += hit / dist
            total += sum(1 / x for x in (1.0, 2.0, 3.5))
        return occl / total

    def texels(key):
        r = regions[key]; n = by_name[r["node"]]; f = r["face"]; s = size3(n)
        M = world_matrix(n["name"]) @ mat4(None, n["offset"])
        U, V = np.meshgrid(np.arange(r["w"]) + 0.5, np.arange(r["h"]) + 0.5)
        loc = np.array([face_texel_to_local(f, s, u, v) for u, v in zip(U.ravel(), V.ravel())])
        P = (np.c_[loc, np.ones(len(loc))] @ M.T)[:, :3]
        Nrm = np.tile(M[:3, :3] @ np.array(FACE_NORMALS[f], dtype=float), (len(P), 1))
        return P, Nrm, U.ravel() - 0.5, V.ravel() - 0.5

    def light_term(P, Nrm, U, V, w, h):
        ny, nz = Nrm[:, 1], Nrm[:, 2]
        L = np.where(ny > 0.5, 0.70, np.where(ny < -0.5, 0.36, np.where(nz > 0.5, 0.65, np.where(nz < -0.5, 0.54, 0.60))))
        L = L + 0.20 * np.clip(P[:, 1] / H, 0, 1) - 0.09
        side = np.abs(ny) < 0.5
        t = V / max(h - 1, 1)
        L = L + np.where(side, 0.06 - 0.12 * t, 0)
        L = L + np.where(side & (V == 0), 0.09, 0) + np.where(side & (V == 1), 0.03, 0)
        L = L - np.where(side & (V == h - 1) & (h > 2), 0.05, 0)
        L = L - np.where(side & ((U == 0) | (U == w - 1)) & (w > 2), 0.04, 0)
        top = ny > 0.5
        edge = np.minimum.reduce([U, w - 1 - U, V, h - 1 - V])
        L = L + np.where(top & (edge == 0), 0.03, 0)
        L = L - np.where(side, 0.16 * np.clip(1 - P[:, 1] / 5.0, 0, 1), 0)
        return np.where(top, np.minimum(L, 0.80), L)

    def style_term(style, P, Nrm, U, V, w, h, seed):
        if style == "fur":
            strand = vnoise(P * np.array([1.0, 0.35, 1.0]), 1.6, seed)
            clump = vnoise(P, 4.0, seed + 1)
            return step(strand, 0.64, 0.34, 0.035, 0.04) + step(clump, 0.64, 0.36, 0.025, 0.03)
        if style == "wool":
            c = vnoise(P, 2.2, seed); c2 = vnoise(P, 5.0, seed + 3)
            return step(c, 0.60, 0.40, 0.07, 0.07) + step(c2, 0.62, 0.38, 0.02, 0.03)
        if style == "feather":
            row = (np.floor(P[:, 1] + 0.5 * (np.floor((P[:, 0] + P[:, 2]) / 3.0) % 2)) % 3)
            side = np.abs(Nrm[:, 1]) < 0.5
            return np.where(side & (row == 0), -0.05, np.where(side & (row == 2), 0.03, 0)) + step(vnoise(P, 3.0, seed), 0.66, 0.34, 0.02, 0.02)
        if style == "horn":
            return np.where(V % 3 == 0, -0.07, 0.02) + step(vnoise(P, 2.0, seed), 0.66, 0.34, 0.02, 0.02)
        if style == "leather":
            return np.where((U == 1) | (U == w - 2), np.where(V % 2 == 0, 0.06, 0), 0) + step(vnoise(P, 3.0, seed), 0.66, 0.34, 0.015, 0.02)
        if style == "cloth":
            return np.where((U + V) % 2 == 0, 0.015, -0.015) + np.where((V == 0) | (V == h - 1), -0.04, 0)
        if style == "gold":
            return np.where(V == 0, 0.12, 0) + 0.06
        if style == "membrane":
            return step(vnoise(P, 2.5, seed), 0.64, 0.36, 0.03, 0.03)
        if style == "flat":
            return 0
        return step(vnoise(P, 2.5, seed), 0.66, 0.34, 0.015, 0.02)   # smooth

    zones = spec.get("zones", [])
    def matmap(name, face, P, Nrm, U, V, w, h):
        base = by_name[name]["mat"]
        m = np.array([base] * len(P), dtype=object)
        for zn, zf, pred, mat in zones:
            names = (zn,) if isinstance(zn, str) else zn
            if name not in names or (zf is not None and face not in zf):
                continue
            sel = np.ones(len(P), dtype=bool) if pred is None else pred(P, Nrm, U, V, w, h)
            m[sel] = mat
        return m

    tex = np.zeros((TH, TW, 4), dtype=np.uint8)
    for key, r in sorted(regions.items()):
        n = by_name[r["node"]]; w, h = r["w"], r["h"]
        if n["shape"][0] == "quad":
            continue
        P, Nrm, U, V = texels(key)
        L = light_term(P, Nrm, U, V, w, h) - 0.26 * ao_term(P, Nrm, exclude={n["name"]})
        M = matmap(n["name"], r["face"], P, Nrm, U, V, w, h)
        col = np.zeros((len(P), 3))
        for mk in sorted(set(M)):
            sel = M == mk
            stops, style, _ = mats[mk]
            Ls = L + style_term(style, P, Nrm, U, V, w, h, seed=sum(map(ord, mk)) % 97)
            if style in ("flat",):
                Ls = 0.52 + 0.4 * (Ls - 0.6)
            if mk == "blush":
                Ls = np.maximum(Ls, 0.56)
            Lq = np.round(Ls / QUANT) * QUANT
            col[sel] = ramp(Lq[sel], stops)
        col = np.clip(np.round(col), 22, 236).reshape(h, w, 3).astype(np.uint8)
        tex[r["y"]:r["y"] + h, r["x"]:r["x"] + w, :3] = col
        tex[r["y"]:r["y"] + h, r["x"]:r["x"] + w, 3] = 255

    # eyes + lids (quads)
    for key, r in sorted(regions.items()):
        n = by_name[r["node"]]
        if n["shape"][0] != "quad":
            continue
        w, h = r["w"], r["h"]
        px = np.zeros((h, w, 4), dtype=np.uint8)
        if n["mat"] == "eye":
            rim = np.array([40, 30, 54]); pup = np.array([50, 38, 64]); iris = hx(n["iris"])
            for v in range(h):
                for u in range(w):
                    c = pup if 0 < u < w - 1 and 0 < v < h - 1 else rim
                    if 0 < u < w - 1 and v >= h * 0.5 and v < h - 1:
                        t = (v - h * 0.5) / max(h * 0.5 - 1, 1)
                        c = pup * 0.35 + iris * (0.65 + 0.25 * t)
                    px[v, u] = (*np.clip(c, 22, 236).astype(int), 255)
            for (u, v) in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
                px[v, u] = 0
            gl = [(1, 1), (2, 1)] if h < 5 else ([(1, 1), (2, 1), (1, 2), (2, 2)] if w >= 5 else [(1, 1), (1, 2)])
            for (u, v) in gl:
                px[v, u] = (236, 234, 226, 255)
            px[h - 2, w - 2] = (*np.clip(iris * 0.5 + 236 * 0.5, 22, 236).astype(int), 255)
        else:   # lid: the head colour + a dark lash line at the bottom
            stops, _, _ = mats[n["lid_mat"]]
            for v in range(h):
                c = ramp(np.array([0.66 - 0.04 * v / h]), stops)[0]
                px[v, :, :3] = np.clip(c, 22, 236); px[v, :, 3] = 255
            px[h - 1, :, :3] = (58, 44, 62); px[h - 2, :, :3] = (px[h - 2, :, :3] * 0.88).astype(np.uint8)
            for (u, v) in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
                px[v, u] = 0
            px[h - 1, 1] = (58, 44, 62, 255); px[h - 1, w - 2] = (58, 44, 62, 255)
        tex[r["y"]:r["y"] + h, r["x"]:r["x"] + w] = px

    pdir = os.path.join(OUT, "Common/NPC/SkyyPets", pname)
    os.makedirs(pdir, exist_ok=True)
    mdir = os.path.join(pdir, "Models"); os.makedirs(mdir, exist_ok=True)
    Image.fromarray(tex, "RGBA").save(os.path.join(mdir, f"{pname}_Texture.png"), optimize=False)

    # ---- blockymodel
    _id = [0]
    def vec(v):
        return {"x": r6(v[0]), "y": r6(v[1]), "z": r6(v[2])}
    def node_json(n):
        _id[0] += 1
        shp = n["shape"]
        shape = {"type": "none", "offset": vec(n["offset"]), "stretch": vec((1, 1, 1)), "settings": {"isPiece": False},
                 "textureLayout": {}, "unwrapMode": "custom", "visible": True, "doubleSided": False, "shadingMode": "flat"}
        if shp:
            t, size, _ = shp
            shape["type"] = t; shape["stretch"] = vec(n["stretch"])
            shape["settings"] = {"size": {"x": size[0], "y": size[1], "z": size[2]}} if t == "box" else {"size": {"x": size[0], "y": size[1]}}
            tl = {}
            for f in faces_of(n):
                rk, mirr = layout[(n["name"], f)]; rr = regions[rk]
                # Hytale/Blockbench: with mirror.x the U axis runs from offset.x towards -U, so the offset is the region's RIGHT edge
                ox = rr["x"] + (face_uv_size(f, size3(n))[0] if mirr else 0)
                tl[f] = {"offset": {"x": ox, "y": rr["y"]}, "mirror": {"x": mirr, "y": False}, "angle": 0}
            shape["textureLayout"] = tl
        q = n["quat"]
        out = {"id": str(_id[0]), "name": n["name"], "position": vec(n["position"]),
               "orientation": {"x": r6(q[0]), "y": r6(q[1]), "z": r6(q[2]), "w": r6(q[3])}, "shape": shape}
        kids = [c for c in NODES if c["parent"] == n["name"]]
        if kids:
            out["children"] = [node_json(c) for c in kids]
        return out
    model = {"nodes": [node_json(n) for n in NODES if n["parent"] is None], "format": "character", "lod": "auto"}
    with open(os.path.join(mdir, f"{pname}.blockymodel"), "w") as fh:
        json.dump(model, fh, indent=2); fh.write("\n")

    anims = pets_anims.write_all(pdir, spec, by_name)
    boxes = sum(1 for n in NODES if n["shape"] and n["shape"][0] == "box")
    quads = sum(1 for n in NODES if n["shape"] and n["shape"][0] == "quad")
    info = dict(name=pname, texture=[TW, TH], nodes=len(NODES), boxes=boxes, quads=quads, tris=boxes * 12 + quads * 2,
                node_names=[n["name"] for n in NODES], anims=anims, rig=spec["rig"], mount=bool(spec.get("mount")),
                height_units=H)
    print(f"{pname:8s} tex {TW}x{TH} nodes {len(NODES)} boxes {boxes} tris {info['tris']} anims {[a['name'] for a in anims]}")
    return info

if __name__ == "__main__":
    infos = {}
    for pname, fn in PETS.items():
        if ONLY and pname not in ONLY:
            continue
        infos[pname] = build_pet(pname, fn())
    os.makedirs(os.path.join(OUT, "source"), exist_ok=True)
    if not ONLY:
        with open(os.path.join(HERE, "..", "..", "work", "build_info.json"), "w") as fh:
            json.dump(infos, fh, indent=1)
