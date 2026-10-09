#!/usr/bin/env python3
"""make_monk_claws - Monk claws v1 (redesign: skeletal metal frame over a black leather glove + 3 long curved knuckle blades).

ORIGINAL art: every box is placed here, the UVs are packed into a fresh atlas and every texel is painted from code with our own
hex palettes. No vanilla or third-party pixel, model or colour sample is used (Skyy's reference picture is only DESCRIBED in words).

Frame = the held-weapon frame used by tools/art/make_fists.py (root "R-Attachment", isPiece), measured from the player model:
  bare hand x -5..5, y -7..7, z -7..5; forearm x -4..4, y -6..6, z -22..-7
  +z = knuckles / finger ends (blades point +z), -z = wrist, -x = back of the hand, +x = palm, +y = thumb side.
1 texel per unit (64 px per block, the character / attachment density).

Run: python3 tools/art/make_monk_claws.py [out_dir]   (deterministic: two runs = same bytes)
"""
import json
import math
import os
import sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pebble_common import quat_to_mat, mat4, r6, face_texel_to_local, FACE_NORMALS  # noqa: E402

TIERS = ("Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium")
BANDS = {"Copper": "10-18", "Iron": "15-23", "Thorium": "20-28", "Cobalt": "25-38", "Adamantite": "35-43", "Mithril": "40-49",
         "Onyxium": "50+"}


def hx(s):
    return np.array([int(s[i:i + 2], 16) for i in (1, 3, 5)], float)


def R5(*c):
    return [hx(x) for x in c]


# our own tier ramps (dark -> light). Shared SkyWynn tier hues: Copper copper, Iron grey, Thorium green, Cobalt blue,
# Adamantite red, Mithril silver-blue (+ gold trim), Onyxium black-violet (Skyy 2026-10-07 "Match the wands").
METAL = {
    "Copper": R5("#3d1d10", "#73361b", "#a85a2c", "#d68548", "#f4b882"),
    "Iron": R5("#272b31", "#4a5058", "#757d87", "#a7afb8", "#d8dde2"),
    "Thorium": R5("#1f2e17", "#3b5726", "#5e8638", "#88b356", "#bddb8e"),
    "Cobalt": R5("#17223a", "#2b4369", "#46699e", "#7096c8", "#b2cbe8"),
    "Adamantite": R5("#330c10", "#661719", "#a2262a", "#d44d3c", "#f2906e"),
    "Mithril": R5("#34465a", "#62809a", "#94b2c8", "#c6dbe8", "#ecf4f7"),
    "Onyxium": R5("#150f1d", "#281b37", "#402d5c", "#664c8c", "#a088c8"),
}
GOLD = R5("#4f3208", "#8c5e12", "#c99328", "#eec25a", "#f8e2a0")
GOLD_TRIM = ("Mithril",)
LEATHER = R5("#1c1a21", "#2a2631", "#3a3443", "#4c4557", "#655d72")
THREAD = hx("#7a6f80")
SAFFRON = R5("#5c2a0c", "#9c4c16", "#d8702a", "#f08a30", "#f9b86a")   # Monk class colour (emblem Saffron #f08a30)
SLOT = hx("#100d14")


def ramp(cols, t):
    t = min(max(t, 0.0), 1.0) * (len(cols) - 1)
    i = min(int(t), len(cols) - 2)
    return cols[i] + (cols[i + 1] - cols[i]) * (t - i)


def noise(x, y, seed):
    h = (int(x) * 374761393 + int(y) * 668265263 + int(seed) * 2147483647) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 65535.0


# ============================================================================================ geometry
def quat_y(deg):
    a = math.radians(deg) / 2.0
    return {"x": 0, "y": r6(math.sin(a)), "z": 0, "w": r6(math.cos(a))}


class Node(object):
    def __init__(self, name, kind, size=None, pos=(0, 0, 0), offset=(0, 0, 0), rot_y=0.0):
        self.name, self.kind, self.size = name, kind, size
        self.pos, self.offset, self.rot_y = pos, offset, rot_y
        self.children = []

    def add(self, child):
        self.children.append(child)
        return child


FINGER_Y = (-6.0, -2.0, 2.0, 6.0)     # pinky ... index (2 wide bones, 2 wide gaps)
BLADE_Y = (-4.0, 0.0, 4.0)            # the 3 blades sit in the finger gaps
# blade chain: (length, bend added at this joint (deg, towards the palm = concave edge side), height spine->edge, thickness)
BLADE_SEGS = ((9, 0, 6, 2), (8, 5, 5, 2), (8, 7, 4, 2), (7, 9, 3, 2), (6, 12, 2, 1), (5, 16, 1, 1))
BLADE_ROOT = (-8.5, 2.0)               # spine x, z of the first segment's base (sunk in the glove between the knuckles)
OVERLAP = 1.0


def build():
    root = Node("R-Attachment", "root")
    a = root.add
    # black leather glove (fist shell = bare hand + 1) + leather thumb
    a(Node("Handle", "leather_glove", (12, 16, 14), (0, 0, -1)))
    a(Node("Thumb", "leather", (5, 3, 8), (3, 9.5, 0)))
    a(Node("ThumbBone", "bone", (3, 1, 7), (2.5, 11.5, 0)))
    a(Node("PinkyBone", "bone", (3, 1, 9), (-2.5, -8.5, 0)))          # outer bone strip on the pinky side
    # skeletal frame: carpal plate at the wrist, 4 finger bones along the back, knuckle caps, 2 segments down the fist front
    a(Node("BackPlate", "backplate", (2, 14, 4), (-7, 0, -6)))
    for i, fy in enumerate(FINGER_Y):
        k = i + 1
        a(Node("Bone%d" % k, "bone", (2, 2, 7), (-7, fy, -0.5)))
        a(Node("Knuckle%d" % k, "knuckle", (3, 2, 3), (-7.5, fy, 4.5)))
        a(Node("FingerMid%d" % k, "bone", (4, 2, 2), (-3.5, fy, 6.5)))
        a(Node("FingerTip%d" % k, "bone_tip", (3, 2, 1), (0, fy, 6.5)))
    # blades: a chain per blade, each segment pivots on the spine at its base; the box reaches forward (+z) and down (+x).
    # The blade roots sit inside the glove between the knuckle caps (Wolverine style: out from between the knuckles).
    for bi, by in enumerate(BLADE_Y):
        parent, prev = root, None
        for si, (L, bend, H, Tk) in enumerate(BLADE_SEGS):
            if by != 0.0 and si >= 2:
                L -= 1                       # outer blades a little shorter: the middle blade leads (reads in side view)
            name = "Blade%d_%d" % (bi + 1, si + 1)
            kind = "blade_tip" if si == len(BLADE_SEGS) - 1 else "blade"
            if prev is None:
                pos = (BLADE_ROOT[0], by, BLADE_ROOT[1])
            else:
                pL, pH = prev.size[2], prev.size[0]
                pos = (-pH / 2.0, 0, pL / 2.0 - OVERLAP)                                     # relative to parent box centre
            node = Node(name, kind, (H, Tk, L), pos, (H / 2.0, 0, L / 2.0), bend)
            parent.add(node)
            parent, prev = node, node
    # wrist: metal cuff ring, black leather wrap with a saffron cord + knot, metal end rim
    a(Node("CuffRing", "cuff", (13, 17, 3), (0, 0, -9.5)))
    a(Node("Wrap", "leather_wrap", (11, 15, 6), (0, 0, -14)))
    a(Node("Cord", "cord", (12, 16, 1), (0, 0, -13.5)))
    a(Node("Knot", "cord_knot", (2, 3, 2), (-6.5, -4, -13.5)))
    a(Node("EndRim", "cuff", (12, 16, 1), (0, 0, -17.5)))
    return root


def all_nodes(n):
    out = [n]
    for c in n.children:
        out += all_nodes(c)
    return out


# ============================================================================================ UV packing
FACES = ("front", "back", "left", "right", "top", "bottom")


def face_wh(face, size):
    w, h, d = size
    return {"front": (w, h), "back": (w, h), "left": (d, h), "right": (d, h), "top": (w, d), "bottom": (w, d)}[face]


def pack(nodes, tex_w=64):
    rects = []
    for n in nodes:
        if n.size is None:
            continue
        for f in FACES:
            w, h = face_wh(f, n.size)
            rects.append((n.name, f, int(w), int(h)))
    order = dict((f, i) for i, f in enumerate(FACES))
    rects.sort(key=lambda r: (-r[3], -r[2], r[0], order[r[1]]))
    place, x, y, row = {}, 0, 0, 0
    for name, f, w, h in rects:
        if x + w > tex_w:
            x, y, row = 0, y + row, 0
        place[(name, f)] = (x, y)
        x += w
        row = max(row, h)
    height = ((y + row + 31) // 32) * 32
    return place, height


# ============================================================================================ model json
def to_json(root, place):
    ids = [1]

    def nj(n):
        nid = str(ids[0]); ids[0] += 1
        if n.size is None:
            shape = {"offset": {"x": 0, "y": 0, "z": 0}, "stretch": {"x": 1, "y": 1, "z": 1}, "textureLayout": {},
                     "type": "none", "settings": {"isPiece": True}, "unwrapMode": "custom", "visible": True,
                     "doubleSided": False, "shadingMode": "flat"}
        else:
            tl = dict((f, {"offset": {"x": place[(n.name, f)][0], "y": place[(n.name, f)][1]}, "mirror": {"x": False, "y": False},
                           "angle": 0}) for f in FACES)
            shape = {"offset": {"x": r6(n.offset[0]), "y": r6(n.offset[1]), "z": r6(n.offset[2])},
                     "stretch": {"x": 1, "y": 1, "z": 1}, "textureLayout": tl, "type": "box",
                     "settings": {"size": {"x": n.size[0], "y": n.size[1], "z": n.size[2]}},
                     "unwrapMode": "custom", "visible": True, "doubleSided": False, "shadingMode": "flat"}
        out = {"id": nid, "name": n.name,
               "position": {"x": r6(n.pos[0]), "y": r6(n.pos[1]), "z": r6(n.pos[2])},
               "orientation": quat_y(n.rot_y) if n.rot_y else {"x": 0, "y": 0, "z": 0, "w": 1},
               "shape": shape, "children": []}
        out["children"] = [nj(c) for c in n.children]
        return out
    return {"nodes": [nj(root)], "lod": "auto"}


def world_mats(root):
    """node name -> (M 4x4 of the node frame incl. its own shape offset, R 3x3)."""
    out = {}

    def walk(n, PM, poff):
        q = quat_y(n.rot_y) if n.rot_y else {"x": 0, "y": 0, "z": 0, "w": 1}
        M = PM @ mat4(None, poff) @ mat4(quat_to_mat((q["x"], q["y"], q["z"], q["w"])), n.pos)
        off = np.array(n.offset, float)
        out[n.name] = (M @ mat4(None, off), M[:3, :3])
        for c in n.children:
            walk(c, M, off)
    walk(root, np.eye(4), np.zeros(3))
    return out


# ============================================================================================ painting
LIGHT = np.array([-0.62, 0.48, 0.42]); LIGHT /= np.linalg.norm(LIGHT)   # from the back of the hand, thumb side, forward


class Painter(object):
    def __init__(self, tier, nodes, place, height, mats):
        self.tier = tier
        self.M = METAL[tier]
        self.trim = GOLD if tier in GOLD_TRIM else METAL[tier]
        self.img = np.zeros((height, 64, 4))
        self.seed = sum(ord(c) for c in tier)
        for fi, n in enumerate(nodes):
            if n.size is None:
                continue
            for f in FACES:
                self.face(n, f, place[(n.name, f)], mats[n.name], fi)

    def face(self, n, f, off, mats, fi):
        M, R = mats
        w, h = face_wh(f, n.size)
        nrm = R @ np.array(FACE_NORMALS[f], float)
        lit = float(nrm @ LIGHT)
        light = 0.86 + 0.22 * max(lit, 0.0) - 0.12 * max(-lit, 0.0)
        for v in range(int(h)):
            for u in range(int(w)):
                lp = np.array(face_texel_to_local(f, n.size, u + 0.5, v + 0.5))
                c = self.texel(n, f, u, v, int(w), int(h), lp, fi)
                k = light
                if w > 1 and h > 1 and not n.kind.startswith("leather"):
                    # painted bevel: light rim on edges facing the light, dark rim on the others
                    edge = None
                    if v == 0: edge = (0, 1)
                    elif v == h - 1: edge = (0, -1)
                    elif u == 0: edge = (-1, 0)
                    elif u == w - 1: edge = (1, 0)
                    if edge is not None:
                        lp2 = np.array(face_texel_to_local(f, n.size, u + 0.5 + edge[0] * 0.5, v + 0.5 - edge[1] * 0.5))
                        dirv = R @ (lp2 - lp)
                        dn = np.linalg.norm(dirv) or 1.0
                        d = float((dirv / dn) @ LIGHT)
                        k *= 1.14 if d > 0.05 else (0.80 if d < -0.05 else 0.95)
                c = np.clip(np.array(c, float) * k, 14, 242)
                self.img[off[1] + v, off[0] + u] = (c[0], c[1], c[2], 255)

    # ------------------------------------------------------------------------------- materials
    def texel(self, n, f, u, v, w, h, p, fi):
        kind, M, s = n.kind, self.M, self.seed
        nz = noise(u + 37 * fi, v + 11 * FACES.index(f), s)
        if kind.startswith("leather"):
            t = 0.55 + 0.07 * (nz - 0.5) + (0.06 if noise(u // 2, v // 2, fi + 9) > 0.86 else 0.0)
            if f in ("left", "right", "top", "bottom") and h >= 4:
                t += 0.10 * (1.0 - 2.0 * abs((v + 0.5) / h - 0.4))         # soft sheen across the face
            c = ramp(LEATHER, t)
            if kind == "leather_glove":
                if f == "left" and 1 <= u <= w - 2 and 1 <= v <= h - 2:
                    # back of the hand: stitched seam 1 texel in + two tendon creases
                    if (u in (1, w - 2) or v in (1, h - 2)) and (u + v) % 2 == 0:
                        c = THREAD
                if f in ("left", "right", "top", "bottom") and abs(p[2] - 0.0) < 0.5:
                    c = LEATHER[1]
                if f == "front":
                    c = ramp(LEATHER, 0.35 + 0.1 * nz)            # knuckle face under the finger frame
            if kind == "leather_wrap":
                # strap wound diagonally around the wrist: dark seam every 3 texels + lit top row on each turn
                k = int(math.floor(p[2] * 1.0 + (p[0] + p[1]) * 0.5 + 100)) % 3
                c = ramp(LEATHER, 0.30 if k == 0 else (0.78 if k == 1 else 0.58) + 0.1 * (nz - 0.5))
            if noise(u, v, fi + 77) > 0.975:
                c = LEATHER[3]
            return c
        if kind in ("cord", "cord_knot", "cord_tail"):
            k = (u + v) % 3 if kind != "cord_tail" else u % 2
            c = ramp(SAFFRON, (0.78 if k == 0 else 0.55 if k == 1 else 0.40) + 0.1 * (nz - 0.5))
            if kind == "cord_tail" and p[2] < -1.5:
                c = ramp(SAFFRON, 0.62 + 0.2 * (nz - 0.5))           # frayed tassel end
            return c
        if kind in ("bone", "bone_tip", "knuckle", "backplate", "housing", "cuff"):
            T = self.trim if kind == "cuff" else M
            t = 0.47 + 0.10 * (nz - 0.5)
            if kind in ("bone", "bone_tip"):
                # bone ridge: a lit groove-free centre line along the length on the outer faces
                if f in ("left", "front", "top") and w >= 2 and h >= 2:
                    if (f == "left" and u in (0,)) or False:
                        pass
                if kind == "bone_tip":
                    t += 0.08
                if noise(u, v, fi + 13) > 0.94:
                    t -= 0.18
            if kind == "knuckle":
                t = 0.62 + 0.12 * (nz - 0.5)
                # round joint: rivet in the middle of each side face
                cu, cv = (u + 0.5) - w / 2.0, (v + 0.5) - h / 2.0
                r = math.sqrt(cu * cu + cv * cv)
                if w >= 3 and h >= 2 and f in ("left", "top", "bottom", "front"):
                    if r < 0.8:
                        return ramp(M, 0.97)
            if kind == "housing":
                t = 0.50 + 0.10 * (nz - 0.5)
                if f == "front":
                    # three blade slots (dark) + lit lip
                    for by in BLADE_Y:
                        if abs(p[1] - by) < 1.6 and p[0] > -8.6:
                            return SLOT if abs(p[1] - by) < 1.1 else ramp(M, 0.25)
                if f == "left":
                    # top of the housing: engraved line + 4 rivets
                    if abs(p[2] - 2.0) < 0.5:
                        t -= 0.22
                    if abs(abs(p[1]) - 6.0) < 0.6 and abs(p[2] - 0.5) < 0.6 or abs(abs(p[1]) - 6.0) < 0.6 and abs(p[2] - 3.5) < 0.6:
                        return ramp(M, 0.98)
            if kind == "backplate" and f == "left":
                # saffron Monk diamond set in the back plate, in a trim ring
                d = abs(p[1]) + abs(p[2] + 5.5) * 1.1
                if d < 1.6:
                    return ramp(SAFFRON, 0.92 if (p[1] < 0 and p[2] > -5.5) else 0.68)
                if d < 2.6:
                    return ramp(self.trim, 0.85)
                if abs(abs(p[1]) - 5.0) < 0.6 and abs(abs(p[2] + 5.5) - 1.5) < 0.6:
                    return ramp(M, 0.98)                                 # corner rivets
            if kind == "cuff":
                t = 0.58 + 0.1 * (nz - 0.5)
                if f == "back" and n.name == "EndRim" and 1 <= u <= w - 2 and 1 <= v <= h - 2:
                    return ramp(LEATHER, 0.12) if 2 <= u <= w - 3 and 2 <= v <= h - 3 else ramp(LEATHER, 0.45)
                if f in ("left", "right", "top", "bottom") and h >= 2:
                    if v == 0:
                        t += 0.25
                    elif v == h - 1:
                        t -= 0.25
                    elif (u % 4 == 1) and n.name == "CuffRing":
                        t += 0.22                                        # embossed studs round the ring
            return ramp(T, t)
        if kind in ("blade", "blade_tip"):
            # flat sides = +-y faces ('top'/'bottom'), local x: spine (-x) -> edge (+x)
            half = n.size[0] / 2.0
            if f in ("top", "bottom"):
                rel = (p[0] + half) / max(n.size[0], 1)             # 0 spine .. 1 edge
                if n.size[0] >= 3:
                    if rel < 0.25:
                        t = 0.72                                     # spine band
                    elif rel < 0.5:
                        t = 0.48                                     # fuller (blood groove)
                    elif rel < 0.8:
                        t = 0.88
                    else:
                        t = 0.97                                     # honed edge
                elif n.size[0] == 2:
                    t = 0.76 if rel < 0.5 else 1.0
                else:
                    t = 0.95
                t += 0.06 * (nz - 0.5)
                if noise(u, v, fi + 5) > 0.95:
                    t -= 0.12
                c = ramp(M, t)
                if rel >= 0.8 or n.size[0] < 3 and rel >= 0.5:
                    c = c + (np.array([240, 240, 236.0]) - c) * 0.16        # polished edge
                if kind == "blade_tip" and p[2] > n.size[2] / 2.0 - 2:
                    c = c + (np.array([236, 238, 240.0]) - c) * 0.35         # tip glint
                return c
            if f == "left":                                          # spine
                return ramp(M, 0.80 + 0.06 * (nz - 0.5))
            if f == "right":                                         # cutting edge
                c = ramp(M, 1.0)
                return c + (np.array([240, 240, 236.0]) - c) * 0.35
            return ramp(M, 0.85)
        raise ValueError(kind)


# ============================================================================================ animation (optional)
def extend_anim(root):
    """Claws_Extend: on equip the 3 blades shoot out from between the knuckles, segment by segment. Each segment's shape is
    stretched along its length (0.05 -> 1) while a matching position key keeps its BASE in place (stretch scales about the
    shape centre), so the blade grows out of the glove. 60 fps units; holds the last key (blades out = the rest pose)."""
    D = 24
    tracks = {}
    S0 = 0.05
    by_name = dict((n.name, n) for n in all_nodes(root))
    nseg = len(BLADE_SEGS)
    for bi in range(len(BLADE_Y)):
        for si in range(nseg):
            name = "Blade%d_%d" % (bi + 1, si + 1)
            n = by_name[name]
            L, b = n.size[2], math.radians(n.rot_y)
            back = (1.0 - S0) * L / 2.0
            dlt = {"x": r6(-back * math.sin(b)), "y": 0, "z": r6(-back * math.cos(b))}
            zero = {"x": 0, "y": 0, "z": 0}
            t0 = 2 + si * 3 + bi            # small stagger per blade (middle blade a frame later)
            t1 = t0 + 3
            lin = "linear"
            st = [{"time": 0, "delta": {"x": 1, "y": 1, "z": S0}, "interpolationType": lin},
                  {"time": t0, "delta": {"x": 1, "y": 1, "z": S0}, "interpolationType": lin},
                  {"time": t1, "delta": {"x": 1, "y": 1, "z": 1}, "interpolationType": lin}]
            ps = [{"time": 0, "delta": dlt, "interpolationType": lin},
                  {"time": t0, "delta": dlt, "interpolationType": lin},
                  {"time": t1, "delta": zero, "interpolationType": lin}]
            vis = [{"time": 0, "delta": False, "interpolationType": lin},
                   {"time": t0, "delta": True, "interpolationType": lin}]
            tracks[name] = {"position": ps, "orientation": [], "shapeStretch": st, "shapeVisible": vis, "shapeUvOffset": []}
    return {"formatVersion": 1, "duration": D, "holdLastKeyframe": True, "nodeAnimations": tracks}


# ============================================================================================ icon
ICON_VIEW = dict(cam=(-1.0, -0.45, 0.2), up=(0.0, 1.0, 0.0), roll=42.0)


def icon_R():
    from mc_render import rot_basis
    return rot_basis(ICON_VIEW["cam"], ICON_VIEW["up"], ICON_VIEW["roll"])


def render_icon(model, tex_img, size=64, margin=2):
    from mc_render import render, bounds
    R = icon_R()
    lo, hi = bounds(model, R)
    ext = hi - lo
    scale = (size - 2 * margin) / max(ext[0], ext[1])
    img, _ = render(model, tex_img, R, size=size, scale=scale, center=(lo + hi) / 2, ss=3, shade_amt=0.25)
    return img


# ============================================================================================ main
def write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    mode = "wb" if isinstance(data, bytes) else "w"
    with open(path, mode) as fh:
        fh.write(data)


def png_bytes(img):
    import io
    b = io.BytesIO()
    img.save(b, "PNG", optimize=False, compress_level=9)
    return b.getvalue()


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "..", "art", "monk-claws")
    out = os.path.abspath(out)
    root = build()
    nodes = all_nodes(root)
    place, height = pack(nodes)
    model = to_json(root, place)
    mats = world_mats(root)
    boxes = [n for n in nodes if n.size is not None]
    manifest = {"item_family": "SkyyArmory_Fist_Claws", "version": "v1 (skeletal frame redesign, 2026-10-08)", "items": [],
                "nodes": [n.name for n in nodes], "boxes": len(boxes), "triangles": 12 * len(boxes),
                "texture_size": [64, height], "animations": []}
    anim = extend_anim(root)
    anim_rel = "Common/Items/Weapons/Animations/SkyyArmory_Claws/SkyyArmory_Claws_Extend.blockyanim"
    write(os.path.join(out, anim_rel), json.dumps(anim, indent=2) + "\n")
    manifest["animations"].append({"path": anim_rel, "name": "Claws_Extend", "frames": anim["duration"], "fps": 60,
                                   "seconds": round(anim["duration"] / 60.0, 3), "holdLastKeyframe": True,
                                   "nodes": sorted(anim["nodeAnimations"].keys())})
    for tier in TIERS:
        P = Painter(tier, nodes, place, height, mats)
        tex = Image.fromarray(np.clip(P.img, 0, 255).astype(np.uint8), "RGBA")
        base = "Common/Items/Weapons/Fist/SkyyArmory_Claws_%s" % tier
        icon_rel = "Common/Icons/ItemsGenerated/SkyyArmory_Fist_Claws_%s.png" % tier
        write(os.path.join(out, base + ".blockymodel"), json.dumps(model, indent=2) + "\n")
        write(os.path.join(out, base + "_Texture.png"), png_bytes(tex))
        icon = render_icon(model, tex)
        write(os.path.join(out, icon_rel), png_bytes(icon))
        manifest["items"].append({"item": "SkyyArmory_Fist_Claws_%s" % tier, "tier": tier, "level_band": BANDS[tier],
                                  "model": base + ".blockymodel", "texture": base + "_Texture.png", "icon": icon_rel,
                                  "icon_size": [64, 64], "texture_size": [64, height]})
    write(os.path.join(out, "manifest.json"), json.dumps(manifest, indent=2) + "\n")
    print("make_monk_claws: %d tiers, %d boxes (%d tris), texture 64x%d -> %s" % (len(TIERS), len(boxes), 12 * len(boxes),
                                                                                 height, out))


if __name__ == "__main__":
    main()
