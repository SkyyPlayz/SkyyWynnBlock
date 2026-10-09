#!/usr/bin/env python3
"""make_accessory_bag_icon - the SkyWynn Accessory Bag MENU icon (64x64), our own art drawn from code.

What: a chunky black-leather satchel with a gold carry handle, a small gold clasp bar on the flap tongue and 5 small gems in a
row in the 5 booster-line colours, left to right Health red, Stamina yellow, Mana blue, Regeneration green, Speed cyan
(Skyy 2026-10-08: "Use Option B gem colors"). It is meant to replace the vanilla
Utility_Bag_Seed icon on the SkyWynn Menu tile and the Workbench "Accessories & Bags" tab.

How:
  1. a small blocky 3D bag is built from boxes (Hytale-style: cubes only, no spheres / triangles),
  2. every face is painted procedurally in the same way a Hytale texture is painted (light from the top, a lit 1-unit bevel on
     top edges, AO in corners / under the flap / under the gold, hue-shifted dark tones - shadows go violet, lights go warm),
  3. it is rendered in 3/4 view (orthographic, the rasterizer approach of tools/art/render_blocky.py, adapted to shade faces
     straight from paint functions instead of a texture atlas) at 8x supersampling and box-filtered down to 64x64,
  4. 64x64 clean-up: hard alpha (0 or 255 only), a 1 px dark hue-shifted outline, a rim light on the top / left silhouette
     edge of the leather so it reads on dark menus, and HAND-PLACED pixel gems (4x4 px each) + gold glints.
No vanilla file is read, copied or traced. Pure numpy + Pillow. Deterministic: two runs = same bytes.

Leather: --look v2 (default, FINAL; Skyy 2026-10-08: "Make it a little brighter with a more leather look (still black leather,
just lighter") = lighter charcoal-black, soft sheen, worn edges, faint grain, lighter stitching; --look v1 = the previous darker
leather (kept so the sheet can show before / after).

Run:  python make_accessory_bag_icon.py [--out DIR] [--gems lines|model] [--look v2|v1]
      --gems lines (default, FINAL) = Health red, Stamina yellow, Mana blue, Regeneration green, Speed cyan
      --gems model (old draft only)  = the in-game bag model's gems: red, blue, yellow, green, violet (make_bags.py ACC_GEMS)
Out:  <out>/Common/Icons/ItemsGenerated/SkyyAccessories_Bag_Menu.png  (64x64 RGBA)
"""
import argparse
import math
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUT = os.path.join(os.path.dirname(os.path.dirname(HERE)), "art", "accessory-bag-icon")
ICON_REL = "Common/Icons/ItemsGenerated/SkyyAccessories_Bag_Menu.png"
SIZE = 64
SS = 8                     # supersampling
YAW, PITCH = 30.0, 22.0    # 3/4 view: shows the front, the top of the flap and the bag's left side
FILL = 58.0                # the bag's largest projected extent in px (outline ring added after)


def hx(s):
    s = s.lstrip("#")
    return np.array([int(s[i:i + 2], 16) for i in (0, 2, 4)], dtype=float)


def ramp(*cols):
    return np.array([hx(c) for c in cols])


def rs(r, t):
    """sample a dark -> light ramp at t (array, 0..1)"""
    t = np.clip(t, 0.0, 1.0) * (len(r) - 1)
    i = np.minimum(t.astype(int), len(r) - 2)
    f = (t - i)[..., None]
    return r[i] * (1 - f) + r[i + 1] * f


# ---------------------------------------------------------------------------------------------------------------- palettes
# black leather: never #000 - very dark warm plum; shadows lean violet / blue, lights lean warm (hue-shifted, no grey)
LEATHER_V1 = ramp("#0c0914", "#14101b", "#1d1823", "#28212c", "#352b37", "#4b3e48", "#6b5a60")   # v1 ("before")
# v2 (Skyy 2026-10-08: "Make it a little brighter with a more leather look (still black leather, just lighter"): a step or two
# lighter, soft charcoal-black - shadows cool violet, the top sheen stops a touch warm (leather, not grey plastic)
LEATHER_V2 = ramp("#0f0b16", "#18131f", "#221b28", "#2d2431", "#3a2e3b", "#4c3e47", "#67565c", "#8c7a7a")
THREAD = ramp("#4e4250", "#7a6c70", "#a39488")    # v2 stitching: lighter thread, warm-grey (reads as stitches, not gold)
LOOK = {"name": "v2"}                             # set by make_icon(); "v1" = the earlier darker draft (for the before / after)


def leather_ramp():
    return LEATHER_V2 if LOOK["name"] == "v2" else LEATHER_V1


LEATHER = LEATHER_V1
# gold: shadows lean red-brown, the top glint warm cream (never #fff)
GOLD = ramp("#3e1f08", "#6e3f0e", "#a26818", "#d39a2c", "#efc552", "#fbe49a", "#fff2cc")
STITCH = ramp("#3a2a1c", "#5e4730", "#86683f")   # muted brass thread
OUTLINE_LEATHER = hx("#0a0710")
RIM_COOL = hx("#4c4060")                          # cool violet bounce light on the shadow-side silhouette
OUTLINE_GOLD = hx("#2a1406")

# 4-step gem ramps: [dark edge, mid, light, glint] (glint = the brightest pixel, never #fff)
GEMS_MODEL = [   # OLD draft default, not used by the final icon - tools/art/make_bags.py ACC_GEMS (the in-game Accessory Bag model, SkyyAccessories 0.5.8): ramp stops 1..4
    ("red", ["#8a1a20", "#d23a3a", "#ff8a80", "#ffe0dc"]),
    ("blue", ["#163f8f", "#2f6fe0", "#86b4ff", "#e2eeff"]),
    ("yellow", ["#8a6800", "#d6a800", "#ffe066", "#fff8d6"]),
    ("green", ["#17702f", "#2fb34f", "#86eb98", "#e2ffe6"]),
    ("violet", ["#6c1c78", "#a63cb8", "#d886e4", "#ffe2ff"]),
]
GEMS_LINES = [   # FINAL (Skyy 2026-10-08: "Use Option B gem colors") - the first 5 booster lines of SkyyAccessories
    # (build_skyyaccessories_0.5.8.py BOOSTERS: Vitality/Health Red, Endurance/Stamina Yellow, Intelligence/Mana Blue,
    #  Regeneration Green, Speed Cyan). Red / yellow / blue / green ramps = make_bags.py ACC_GEMS (stops 1..4);
    # cyan = the APPROVED Speed accessory icon's wing colour, tools/art/make_accessory_icons.py WING (stops 2-5).
    ("Health", ["#8a1a20", "#d23a3a", "#ff8a80", "#ffe0dc"]),        # red
    ("Stamina", ["#8a6800", "#d6a800", "#ffe066", "#fff8d6"]),       # yellow
    ("Mana", ["#163f8f", "#2f6fe0", "#86b4ff", "#e2eeff"]),          # blue
    ("Regeneration", ["#17702f", "#2fb34f", "#86eb98", "#e2ffe6"]),  # green
    ("Speed", ["#2a8a9a", "#4ac0cc", "#8ae6ee", "#dafcff"]),         # cyan (make_accessory_icons.py WING)
]
GEM_COLOUR_WORD = {"Health": "red", "Stamina": "yellow", "Mana": "blue", "Regeneration": "green", "Speed": "cyan"}


# ---------------------------------------------------------------------------------------------------------------- model
class Box:
    def __init__(self, name, lo, hi, mat, base=0.0):
        self.name, self.lo, self.hi, self.mat, self.base = name, np.array(lo, float), np.array(hi, float), mat, base


def build_bag():
    """units: 1 = one model unit (x right, y up, z towards the front). Chunky proportions, cubes only."""
    B = []
    # body + a slightly inset bottom block (softens the silhouette like a stuffed satchel)
    B.append(Box("Body", (-15, 1.5, -6), (15, 19.5, 6), "leather", 0.0))
    B.append(Box("BodyBase", (-14, 0, -5.2), (14, 1.5, 5.2), "leather", -0.08))
    # side gussets bulge a little (a stitched side panel)
    B.append(Box("GussetL", (-15.8, 3, -4.6), (-15, 18, 4.6), "leather", -0.04))
    B.append(Box("GussetR", (15, 3, -4.6), (15.8, 18, 4.6), "leather", -0.04))
    # flap: lid over the top + the front flap + a centre tongue
    B.append(Box("FlapTop", (-15.6, 19.5, -6.6), (15.6, 21.0, 6.6), "flap", 0.14))
    B.append(Box("FlapCrown", (-14.6, 21.0, -5.6), (14.6, 21.8, 5.6), "flap", 0.12))      # stepped = rounded lid top
    top = 20.97 if LOOK["name"] == "v2" else 21.0       # v2: 20.97 = no z-fighting speckles with the lid (v1 kept as drawn)
    B.append(Box("FlapFront", (-15.6, 12.2, 6.0), (15.6, top, 7.6), "flap", 0.14))
    B.append(Box("FlapHem", (-14.4, 11.0, 6.0), (14.4, 12.2, 7.6), "flap", 0.12))       # stepped = rounded corners
    B.append(Box("FlapTongue", (-6.6, 1.4, 6.0), (6.6, 11.0, 7.4), "tongue", 0.16))
    B.append(Box("TongueTip", (-5.2, 0.4, 6.0), (5.2, 1.4, 7.4), "tongue", 0.12))     # stepped = rounded tip     # stepped = rounded tip
    # small gold clasp bar on the tongue (the gems are hand-placed on it at 64 px)
    B.append(Box("Clasp", (-8.4, 5.6, 7.4), (8.4, 10.2, 8.4), "gold", 0.0))
    # gold carry handle: two posts in small mounts + a thick top bar
    for s, x0, x1 in (("L", -9.2, -5.8), ("R", 5.8, 9.2)):
        B.append(Box("Mount" + s, (x0 - 0.8, 21.5, -2.0), (x1 + 0.8, 23.0, 2.0), "gold", -0.1))
        B.append(Box("Post" + s, (x0, 23.0, -1.3), (x1, 28.0, 1.3), "gold", 0.0))
    B.append(Box("HandleTop", (-9.2, 28.0, -1.3), (9.2, 30.8, 1.3), "gold", 0.08))
    return B


# faces: name -> (origin corner fn, u axis, v axis, normal); u runs right, v runs DOWN as seen from outside the face
def box_faces(b):
    (x0, y0, z0), (x1, y1, z1) = b.lo, b.hi
    W, H, D = x1 - x0, y1 - y0, z1 - z0
    return [
        ("front", (x0, y1, z1), (1, 0, 0), (0, -1, 0), W, H, (0, 0, 1)),
        ("back", (x1, y1, z0), (-1, 0, 0), (0, -1, 0), W, H, (0, 0, -1)),
        ("left", (x0, y1, z0), (0, 0, 1), (0, -1, 0), D, H, (-1, 0, 0)),
        ("right", (x1, y1, z1), (0, 0, -1), (0, -1, 0), D, H, (1, 0, 0)),
        ("top", (x0, y1, z0), (1, 0, 0), (0, 0, 1), W, D, (0, 1, 0)),
        ("bottom", (x0, y0, z1), (1, 0, 0), (0, 0, -1), W, D, (0, -1, 0)),
    ]


# ---------------------------------------------------------------------------------------------------------------- paint
FACE_T = {"top": 0.68, "front": 0.50, "left": 0.27, "right": 0.22, "back": 0.2, "bottom": 0.08}


def edge(d, w):
    """1 at the edge, 0 beyond w units in"""
    return np.clip(1 - d / w, 0, 1)


def paint(box, face, u, v, W, H):
    """t value + ramp for every pixel of a face (u, v in units from the face's top-left corner)"""
    t = np.full(u.shape, FACE_T[face] + box.base)
    vn = v / max(H, 1e-6)
    if box.mat in ("leather", "flap", "tongue") and LOOK["name"] == "v2":
        return paint_leather_v2(box, face, u, v, W, H)
    if box.mat in ("leather", "flap", "tongue"):
        r = LEATHER_V1
        if face in ("front", "left", "right"):
            t += 0.16 * (0.5 - vn)                                    # imaginary spotlight: lighter at the top
            if box.mat == "leather":
                t -= 0.16 * edge(H - v, 1.4)                          # AO along the bottom edge
            else:                                                     # thick leather hem: lit rounded edge, dark lip
                t += 0.16 * ((H - v > 0.35) & (H - v < 1.0))
                t -= 0.18 * (H - v <= 0.35)
            t += 0.20 * edge(v, 0.7)                                  # lit bevel on the top edge
            t += 0.05 * np.sin(u * 0.9 + 1.3) * np.sin(v * 0.7)       # soft leather folds (low frequency, not noise)
            if face == "front" and box.mat == "leather":
                t -= 0.10                                             # the body sits a step darker than the flap
            if face == "front":
                t += 0.14 * edge(u, 0.7)                              # lit vertical edge (the corner facing the light)
            if face == "left":
                t += 0.10 * edge(W - u, 0.6)
        if face == "top":
            t += 0.16 * edge(u, 0.8) + 0.10 * edge(W - u, 0.8)        # lit rims on the lid
            t += 0.16 * edge(H - v, 0.8)                              # front rim of the lid (the edge facing the viewer)
        if face == "left" or face == "right":
            t -= 0.10 * edge(np.minimum(u, W - u), 0.9)               # corner AO
        col = rs(r, t)
        # muted brass stitching inset from the flap / tongue edges (front faces only)
        if box.mat in ("flap", "tongue") and face == "front":
            inset = 1.3
            if box.mat == "flap":
                on = (np.abs((H - v) - inset) < 0.35) & (u > inset) & (u < W - inset)
                on |= ((np.abs(u - inset) < 0.35) | (np.abs(W - u - inset) < 0.35)) & (v > 2.2) & (v < H - inset)
                on &= ~((u > 8.6) & (u < W - 8.6) & ((H - v) < 2.5))  # no stitch where the tongue sits
            else:
                on = ((np.abs(u - inset) < 0.35) | (np.abs(W - u - inset) < 0.35)) & (v < H - inset)
                on |= (np.abs((H - v) - inset) < 0.35) & (u > inset) & (u < W - inset)
            dash = (np.floor((u + v) / 1.2) % 2) == 0
            on &= dash
            col = np.where(on[..., None], col * 0.45 + rs(STITCH, 0.3 + 0.4 * (1 - vn)) * 0.55, col)
        return col
    if box.mat == "gold":
        r = GOLD
        t = np.full(u.shape, {"top": 0.82, "front": 0.62, "left": 0.42, "right": 0.36, "back": 0.3, "bottom": 0.12}[face] + box.base)
        if face in ("front", "left", "right"):
            t += 0.18 * (0.5 - vn)
            t += 0.30 * edge(v, 0.55)                                 # crisp highlight on the top metal edge
            t -= 0.22 * edge(H - v, 0.6)                              # dark lower edge
            t += 0.08 * edge(u, 0.5) - 0.08 * edge(W - u, 0.5)
        if face == "top":
            t += 0.15 * edge(H - v, 0.6)
        return rs(r, t)
    raise ValueError(box.mat)


def grain(u, v, seed):
    """faint pebbled leather grain: a few soft sine layers (smooth value variation, no per-pixel noise)"""
    a = np.sin(u * 3.1 + seed) * np.sin(v * 3.3 + seed * 0.7)       # small pebbles
    b = np.sin(u * 1.9 + v * 1.1 + seed * 1.9) * np.sin(v * 1.7 - u * 0.9 + seed)
    c = np.sin(u * 0.45 + seed * 0.3) * np.sin(v * 0.5 + seed)      # broad soft mottling
    return 0.007 * a + 0.010 * b + 0.028 * c


def stitches(u, v, W, H, lines, period=1.25, width=0.32):
    """dashed stitch mask: lines = list of ("h", offset_from_top_or_negative_from_bottom, u0, u1) / ("v", offset, v0, v1)"""
    on = np.zeros(u.shape, bool)
    for kind, off, a0, a1 in lines:
        if kind == "h":
            pos = off if off >= 0 else H + off
            m = (np.abs(v - pos) < width) & (u > a0) & (u < (W + a1 if a1 <= 0 else a1))
            m &= (np.floor(u / period) % 2) == 0
        else:
            pos = off if off >= 0 else W + off
            m = (np.abs(u - pos) < width) & (v > a0) & (v < (H + a1 if a1 <= 0 else a1))
            m &= (np.floor(v / period) % 2) == 0
        on |= m
    return on


def paint_leather_v2(box, face, u, v, W, H):
    """v2 black leather: lighter charcoal-black, soft sheen on top / rounded edges, worn lighter edges + corners, faint grain,
    a fold crease on the flap, lighter dashed stitching along the flap, tongue and body edges."""
    r = LEATHER_V2
    t = np.full(u.shape, FACE_T[face] + box.base)
    vn = v / max(H, 1e-6)
    un = u / max(W, 1e-6)
    seed = len(box.name) * 1.7 + {"front": 0, "left": 2.1, "right": 3.3, "top": 4.4}.get(face, 5.5)
    dmin = np.minimum(np.minimum(u, W - u), np.minimum(v, H - v))
    corner = edge(np.minimum(u, W - u), 1.2) * edge(np.minimum(v, H - v), 1.2)
    if face in ("front", "left", "right"):
        t += 0.14 * (0.5 - vn)                                        # imaginary spotlight: lighter at the top
        t += 0.10 * np.exp(-((vn - 0.30) / 0.22) ** 2 - ((un - 0.30) / 0.35) ** 2)   # soft sheen on the rounded surface
        if box.mat == "leather":
            t -= 0.15 * edge(H - v, 1.4)                              # AO along the bottom edge
        else:                                                         # thick leather hem: lit rounded edge, dark lip
            t += 0.18 * ((H - v > 0.35) & (H - v < 1.0))
            t -= 0.18 * (H - v <= 0.35)
        t += 0.22 * edge(v, 0.7)                                      # sheen on the top (rounded) edge
        t += 0.05 * np.sin(u * 0.9 + 1.3) * np.sin(v * 0.7)           # soft folds
        if face == "front" and box.mat == "leather":
            t -= 0.10                                                 # the body sits a step darker than the flap
        if face == "front":
            t += 0.15 * edge(u, 0.7)                                  # lit vertical edge (the corner facing the light)
        if face == "left":
            t += 0.12 * edge(W - u, 0.6)
        if face in ("left", "right"):
            t -= 0.08 * edge(np.minimum(u, W - u), 0.9)               # corner AO (under the worn edge below)
    if face == "top":
        t += 0.16 * edge(u, 0.8) + 0.10 * edge(W - u, 0.8)            # lit rims on the lid
        t += 0.18 * edge(H - v, 0.8)                                  # front rim of the lid
        t += 0.08 * np.exp(-((vn - 0.6) / 0.25) ** 2 - ((un - 0.35) / 0.35) ** 2)    # soft sheen on the lid
    # worn, lighter edges and corners (rubbed leather) + faint grain
    t += 0.06 * edge(dmin, 0.55) + 0.07 * corner
    t += grain(u, v, seed)
    # soft vertical slump folds in the body leather (a dark crease with a lit side), below the flap on both sides
    if box.name == "Body" and face == "front":
        for uc in (5.2, W - 5.2):
            t -= 0.07 * np.exp(-((u - uc) / 0.45) ** 2) * (vn > 0.5)
            t += 0.05 * np.exp(-((u - uc + 0.9) / 0.5) ** 2) * (vn > 0.5)
    col = rs(r, t)
    # lighter dashed stitches (thread), inset from the edges
    lines = []
    if face == "front":
        if box.name == "FlapFront":
            lines = [("v", 1.2, 3.2, 0), ("v", -1.2, 3.2, 0), ("h", -0.6, 1.2, -1.2)]   # sides + along the flap edge
        elif box.mat == "tongue" and box.name == "FlapTongue":
            lines = [("v", 1.0, 0.0, -1.0), ("v", -1.0, 0.0, -1.0), ("h", -1.0, 1.0, -1.0)]
        elif box.name == "Body":
            lines = [("v", 1.1, 9.0, -1.4), ("v", -1.1, 9.0, -1.4), ("h", -1.2, 1.1, -1.1)]
    elif face == "left" and box.name in ("GussetL",):
        lines = []
    elif face == "left" and box.name == "Body":
        lines = [("h", -1.2, 1.0, -1.0)]
    if lines:
        on = stitches(u, v, W, H, lines)
        thread = rs(THREAD, np.clip(0.25 + 0.6 * (1 - vn) + (0.15 if face == "top" else 0) - (0.25 if face == "left" else 0), 0, 1))
        col = np.where(on[..., None], col * 0.25 + thread * 0.75, col)
    return col


# ---------------------------------------------------------------------------------------------------------------- render
def view_matrix(yaw, pitch):
    y, p = math.radians(yaw), math.radians(pitch)
    Ry = np.array([[math.cos(y), 0, math.sin(y)], [0, 1, 0], [-math.sin(y), 0, math.cos(y)]])
    Rx = np.array([[1, 0, 0], [0, math.cos(p), -math.sin(p)], [0, math.sin(p), math.cos(p)]])
    return Rx @ Ry


def render(boxes, size=SIZE, ss=SS, yaw=YAW, pitch=PITCH, fill=FILL):
    """orthographic z-buffered raster; returns (rgb float S x S x 3, alpha 0/1, material id map, projector)"""
    R = view_matrix(yaw, pitch)
    pts = []
    for b in boxes:
        for cx in (b.lo[0], b.hi[0]):
            for cy in (b.lo[1], b.hi[1]):
                for cz in (b.lo[2], b.hi[2]):
                    pts.append((cx, cy, cz))
    P = np.array(pts) @ R.T
    center = (P.min(0) + P.max(0)) / 2
    scale = fill / (P.max(0) - P.min(0))[:2].max()
    S = size * ss

    def proj(p):
        V = np.asarray(p, float) @ R.T
        return np.stack([(V[..., 0] - center[0]) * scale * ss + S / 2, S / 2 - (V[..., 1] - center[1]) * scale * ss, V[..., 2]], -1)

    rgb = np.zeros((S, S, 3))
    zbuf = np.full((S, S), -1e9)
    mat = np.full((S, S), -1, dtype=int)
    ys, xs = np.mgrid[0:S, 0:S] + 0.5
    for bi, b in enumerate(boxes):
        for face, o, ua, va, W, H, n in box_faces(b):
            if (R @ np.array(n, float))[2] <= 1e-6:
                continue                                              # facing away
            o, ua, va = np.array(o, float), np.array(ua, float), np.array(va, float)
            q0, qu, qv = proj(o), proj(o + ua * W), proj(o + va * H)
            A = np.array([[qu[0] - q0[0], qv[0] - q0[0]], [qu[1] - q0[1], qv[1] - q0[1]]])
            if abs(np.linalg.det(A)) < 1e-9:
                continue
            Ai = np.linalg.inv(A)
            corners = np.array([q0, qu, qv, qu + qv - q0])
            x0, x1 = int(max(corners[:, 0].min(), 0)), int(min(corners[:, 0].max() + 1, S))
            y0, y1 = int(max(corners[:, 1].min(), 0)), int(min(corners[:, 1].max() + 1, S))
            if x0 >= x1 or y0 >= y1:
                continue
            dx, dy = xs[y0:y1, x0:x1] - q0[0], ys[y0:y1, x0:x1] - q0[1]
            a = Ai[0, 0] * dx + Ai[0, 1] * dy
            c = Ai[1, 0] * dx + Ai[1, 1] * dy
            inside = (a >= 0) & (a <= 1) & (c >= 0) & (c <= 1)
            if not inside.any():
                continue
            z = q0[2] + a * (qu[2] - q0[2]) + c * (qv[2] - q0[2])
            sub = zbuf[y0:y1, x0:x1]
            ok = inside & (z > sub)
            sub[ok] = z[ok]
            col = paint(b, face, a * W, c * H, W, H)
            rgb[y0:y1, x0:x1][ok] = col[ok]
            mat[y0:y1, x0:x1][ok] = bi
    cast_shadow(rgb, zbuf, scale * ss)
    alpha = (mat >= 0).astype(float)
    render.zbuf = zbuf
    return rgb, alpha, mat, proj, scale


SHADOW_TINT = np.array([0.50, 0.44, 0.66])   # cast shadows / AO go violet, not grey


def cast_shadow(rgb, zbuf, px_per_unit, reach=1.5, strength=0.8):
    """light from above, a little from the left: a pixel gets shadowed when something closer to the camera sits just above it on screen
    (the flap hem over the body, the clasp over the tongue, the handle over the lid) - soft, fades with distance."""
    S = zbuf.shape[0]
    L = max(1, int(reach * px_per_unit))
    sh = np.zeros_like(zbuf)
    valid = zbuf > -1e8
    for k in range(1, L + 1):
        above = np.full_like(zbuf, -1e9)
        kx = k // 2
        if kx:
            above[k:, kx:] = zbuf[:-k, :-kx]
        else:
            above[k:, :] = zbuf[:-k, :]
        diff = above - zbuf
        hit = valid & (above > -1e8) & (diff > 0.5)
        sh = np.maximum(sh, np.where(hit, (1 - (k - 1) / L) * np.clip(diff / 1.2, 0, 1), 0))
    f = 1 - strength * sh[..., None] * (1 - SHADOW_TINT)
    rgb *= f


def downsample(rgb, alpha, mat, boxes, ss=SS):
    S = rgb.shape[0]
    n = S // ss
    a = alpha.reshape(n, ss, n, ss).mean((1, 3))
    pm = (rgb * alpha[..., None]).reshape(n, ss, n, ss, 3).sum((1, 3))
    cnt = alpha.reshape(n, ss, n, ss).sum((1, 3))
    col = pm / np.maximum(cnt, 1)[..., None]
    # dominant material per pixel (gold vs leather) for the outline colour
    gold = np.isin(mat, [i for i, b in enumerate(boxes) if b.mat == "gold"]).astype(float)
    g = gold.reshape(n, ss, n, ss).sum((1, 3)) / np.maximum(cnt, 1)
    # per-pixel depth (mean over the covered samples) for the contact-line pass
    z = np.where(alpha > 0, render.zbuf, 0.0).reshape(n, ss, n, ss).sum((1, 3)) / np.maximum(cnt, 1)
    counts = np.stack([(mat == i).reshape(n, ss, n, ss).sum((1, 3)) for i in range(len(boxes))])
    contact_lines.bid = np.where(cnt > 0, counts.argmax(0), -1)                # dominant box per pixel
    contact_lines.gold = {i for i, b in enumerate(boxes) if b.mat == "gold"}
    return col, a, g, z


def contact_lines(out, solid, z, jump=0.8, k=0.55):
    """(v2: only between DIFFERENT parts - v1 also darkened steep top faces, whose depth changes fast per pixel)
    crisp 1 px crease where a surface disappears behind a nearer part (under the flap hem, round the tongue + clasp,
    under the handle mounts) - the painted 1-texel AO line of Hytale textures, done at the final pixel size"""
    n = solid.shape[0]
    dark = np.zeros((n, n), bool)
    for y in range(n):
        for x in range(n):
            if not solid[y, x]:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, -1), (0, 1)):
                xx, yy = x + dx, y + dy
                same = (LOOK["name"] == "v2" and contact_lines.bid[yy, xx] == contact_lines.bid[y, x]
                        and contact_lines.bid[y, x] not in contact_lines.gold)               # gold keeps its v1 look
                if 0 <= xx < n and 0 <= yy < n and solid[yy, xx] and z[yy, xx] - z[y, x] > jump and not same:
                    dark[y, x] = True
    out[dark, :3] = out[dark, :3] * (1 - k) + out[dark, :3] * SHADOW_TINT * 0.6 * k
    return out


# ---------------------------------------------------------------------------------------------------------------- 64 px clean-up
def finish(col, a, g, z, proj, boxes, gems):
    n = col.shape[0]
    solid = a >= 0.5
    out = np.zeros((n, n, 4))
    out[..., :3] = col
    out[..., 3] = np.where(solid, 255, 0)
    contact_lines(out, solid, z)
    isgold = (g > 0.5) & solid

    def at(x, y):
        return 0 <= x < n and 0 <= y < n and solid[y, x]

    # rim light: leather pixels on the top / left silhouette edge get a warm lift (reads on dark menu tiles)
    for y in range(n):
        for x in range(n):
            if not solid[y, x] or isgold[y, x]:
                continue
            if not at(x, y - 1):
                out[y, x, :3] = out[y, x, :3] * 0.55 + leather_ramp()[6] * 0.45
            elif not at(x - 1, y):
                out[y, x, :3] = out[y, x, :3] * 0.7 + leather_ramp()[5] * 0.3
            elif not at(x + 1, y) or not at(x, y + 1):
                out[y, x, :3] = out[y, x, :3] * 0.72 + RIM_COOL * 0.28     # faint cool back-rim (reads on dark tiles)

    # value floor on the rendered leather / gold (before the gems, so gem hexes stay exact): no near-#000 pixels
    out[solid, :3] = np.maximum(out[solid, :3], OUTLINE_LEATHER)

    # hand-placed gems on the clasp bar: five 3x3 cut gems, 1 px gold between them, each centred on its spot along the bar
    # (the bar slopes with the 3/4 view, so the row steps like the bar instead of floating flat over it)
    clasp = [b for b in boxes if b.name == "Clasp"][0]
    zf = clasp.hi[2]
    cy = (clasp.lo[1] + clasp.hi[1]) / 2 + 0.25
    gw, gap = 3, 1
    ux = (proj((1.0, cy, zf)) - proj((0.0, cy, zf)))[0] / SS     # px per model unit along x on screen
    step = (gw + gap) / ux
    for k, (_, cols) in enumerate(gems):
        dk, md, lt, gl = [hx(c) for c in cols]
        q = proj(((k - (len(gems) - 1) / 2) * step, cy, zf)) / SS
        x0, y0 = int(round(q[0] - gw / 2)), int(round(q[1] - gw / 2))
        sprite = [[gl, lt, md],
                  [lt, md, dk],
                  [md, dk, dk]]
        for j in range(gw):
            for i in range(gw):
                out[y0 + j, x0 + i, :3] = sprite[j][i]
        out[y0 + gw, x0:x0 + gw, :3] = GOLD[1]                       # AO under the gem's setting
        out[y0:y0 + gw, x0 - 1, :3] = GOLD[2]                         # recessed setting between the gems
        out[y0:y0 + gw, x0 + gw, :3] = GOLD[2]
        out[y0 - 1, x0:x0 + gw, :3] = GOLD[5]                        # lit rim of the setting above the gem
    # gold glints: brightest pixel on the handle's top-left corner and both mounts
    hb = [b for b in boxes if b.name == "HandleTop"][0]
    for p in ((hb.lo[0] + 0.6, hb.hi[1], hb.hi[2]), (hb.lo[0] + 3.0, hb.hi[1], hb.hi[2])):
        q = proj(p) / SS
        x, y = int(q[0]), int(round(q[1]))
        if at(x, y):
            out[y, x, :3] = GOLD[6]

    # 1 px dark outline ring (hue-shifted: violet-black next to leather, brown-black next to gold), never #000
    ring = np.zeros((n, n), bool)
    ringgold = np.zeros((n, n), bool)
    for y in range(n):
        for x in range(n):
            if solid[y, x]:
                continue
            nb = [(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
            hit = [(xx, yy) for xx, yy in nb if at(xx, yy)]
            if hit:
                ring[y, x] = True
                ringgold[y, x] = sum(isgold[yy, xx] for xx, yy in hit) * 2 > len(hit)
    out[ring, :3] = OUTLINE_LEATHER
    out[ringgold, :3] = OUTLINE_GOLD
    out[ring, 3] = 255
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def make_icon(gems, look="v2"):
    LOOK["name"] = look
    boxes = build_bag()
    rgb, alpha, mat, proj, _ = render(boxes)
    col, a, g, z = downsample(rgb, alpha, mat, boxes)
    return Image.fromarray(finish(col, a, g, z, proj, boxes, gems), "RGBA")


def save_png(img, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path, format="PNG", optimize=False, compress_level=9)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--gems", choices=("lines", "model"), default="lines")
    ap.add_argument("--look", choices=("v2", "v1"), default="v2")
    ap.add_argument("--name", default=ICON_REL)
    args = ap.parse_args()
    gems = GEMS_MODEL if args.gems == "model" else GEMS_LINES
    img = make_icon(gems, look=args.look)
    p = os.path.join(args.out, args.name)
    save_png(img, p)
    print("icon:", p, img.size, img.mode, "gems:", ", ".join(n for n, _ in gems))


if __name__ == "__main__":
    main()
