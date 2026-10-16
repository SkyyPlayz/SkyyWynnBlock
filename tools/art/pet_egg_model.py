#!/usr/bin/env python3
"""pet_egg_model - the PET EGG's own ROUND held / dropped model + its 6 rarity textures (pure Python, deterministic, original).

Skyy 2026-10-16 (art review, docs/answered/pets.md): Q "Pet egg art - approve?" -> "can you make the held item texture look more round? or
no?" -> the egg ICONS stay (art/pet-eggs, tools/art/make_pet_eggs.py); the egg in the hand / on the ground gets its OWN rounder model instead
of the vanilla one-box Items/Consumables/Food/Egg.blockymodel: six stacked boxes tapering to the top and the bottom (an egg silhouette in
blocks), the same outer size as the vanilla egg box (14 wide, 16 high) and the same anchor nodes (R-Attachment > Origin_Projectile >
Origin_Item - the names the hand / drop / pickup poses use; their positions are asserted against the vanilla model by SkyyPets' build,
numbers only, nothing copied).

Why a module of its own: tools/art/make_pet_eggs.py (the icons) needs numpy + Pillow, which the build Python does not have; SkyyPets'
build (tools/pets_0_4_0_patch.py) calls model() / texture_png(rarity) here at BUILD time, with tools/skyyart.py's pure-Python PNG
encoder. Nothing is written to the repo: the 7 files go straight into the jar. Palettes = art/pet-eggs/manifest.json (the approved cup
metal + gem ramps per rarity) + the ivory shell of make_pet_eggs.TEX_SHELL.

Texture (32 x 64, 1 texel = 1 model unit like the vanilla egg): column x 0..13 = the side strips of the six layers stacked bottom-up from
y 0 (all four sides of a layer share its strip); column x 16..29 = one w x w square per layer for its top + bottom faces.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(HERE))
import skyyart as SA  # noqa: E402

# (width = depth, height), BOTTOM -> TOP: 16 high and 14 wide (= the vanilla egg box), fat below the middle, narrow at the top
LAYERS = [(8, 1), (12, 2), (14, 5), (12, 4), (10, 2), (6, 2)]
CUP_LAYERS = 2                       # the bottom two layers = the rarity's egg cup metal (the icons' cup)
TEX_W, TEX_H = 32, 64
SQ_X = 16
MODEL_PATH = "Items/Pets/Skyy_PetEgg.blockymodel"
TEXTURE_PATH = "Items/Pets/Skyy_PetEgg_%s_Round_Texture.png"
CENTER_Y = 1                         # the vanilla egg box's centre in Origin_Item (its node position y)
ANCHORS = [("R-Attachment", (0, 0, 0)), ("Origin_Projectile", (0, 8, 0)), ("Origin_Item", (0, -2, 0))]
SHELL = ["#5a4636", "#8a705a", "#b49c82", "#d4c0a4", "#eadcc4", "#f8f0e2"]        # make_pet_eggs.TEX_SHELL (warm ivory)
PRISM = ["#ff9ad8", "#c49cff", "#8cc8ff", "#8cf0d8", "#fff09c"]                   # make_pet_eggs.PRISM (the Mythic shimmer)
RARITIES = ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic"]


def layout():
    """[(w, h, side_y, square_y, centre_y)] per layer, bottom -> top"""
    out, sy, qy = [], 0, 0
    y = CENTER_Y - sum(h for _w, h in LAYERS) / 2.0
    for w, h in LAYERS:
        out.append((w, h, sy, qy, y + h / 2.0))
        sy += h
        qy += w
        y += h
    assert sy <= TEX_H and qy <= TEX_H and max(w for w, _h in LAYERS) + SQ_X <= TEX_W
    return out


def _face(x, y):
    return {"offset": {"x": x, "y": y}, "mirror": {"x": False, "y": False}, "angle": 0}


def _node(nid, name, pos, shape, children):
    return {"id": str(nid), "name": name, "children": children, "position": {"x": pos[0], "y": pos[1], "z": pos[2]},
            "orientation": {"x": 0, "y": 0, "z": 0, "w": 1}, "shape": shape}


def _none_shape():
    return {"type": "none", "offset": {"x": 0, "y": 0, "z": 0}, "stretch": {"x": 1, "y": 1, "z": 1}, "settings": {"isPiece": True},
            "visible": True, "doubleSided": False, "shadingMode": "flat", "unwrapMode": "custom", "textureLayout": {}}


def model():
    """the .blockymodel as a dict (the vanilla egg's top-level keys + node / shape fields)"""
    kids = []
    for i, (w, h, sy, qy, cy) in enumerate(layout()):
        tl = dict((f, _face(0, sy)) for f in ("front", "back", "left", "right"))
        tl["top"] = _face(SQ_X, qy)
        tl["bottom"] = _face(SQ_X, qy)
        shape = {"type": "box", "offset": {"x": 0, "y": 0, "z": 0}, "stretch": {"x": 1, "y": 1, "z": 1},
                 "settings": {"size": {"x": w, "y": h, "z": w}}, "visible": True, "doubleSided": False, "shadingMode": "flat",
                 "unwrapMode": "custom", "textureLayout": tl}
        kids.append(_node(10 + i, "Egg%d" % i, (0, cy, 0), shape, []))
    nid = 3
    node = None
    for name, pos in reversed(ANCHORS):
        node = _node(nid, name, pos, _none_shape(), kids if node is None else [node])
        nid -= 1
    return {"nodes": [node], "lod": "auto"}


def model_bytes():
    return (json.dumps(model(), indent=2) + "\n").encode("utf-8")


def _hx(c):
    c = c.lstrip("#")
    return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16))


def _ramp(hexes, t):
    t = 0.0 if t < 0 else (1.0 if t > 1 else t)
    p = t * (len(hexes) - 1)
    i = min(int(p), len(hexes) - 2)
    f = p - i
    a, b = _hx(hexes[i]), _hx(hexes[i + 1])
    return tuple(a[k] * (1 - f) + b[k] * f for k in range(3))


def _mix(a, b, f):
    return tuple(a[k] * (1 - f) + b[k] * f for k in range(3))


def _rnd(*keys):
    h = hashlib.sha256(("|".join(str(k) for k in keys)).encode("utf-8")).digest()
    return [b / 255.0 for b in h]


def palettes(manifest_path=None):
    """{rarity: (cup metal hexes, gem hexes, quality colour)} from art/pet-eggs/manifest.json"""
    p = manifest_path or os.path.join(ROOT, "art", "pet-eggs", "manifest.json")
    m = json.load(open(p, encoding="utf8"))["rarities"]
    return dict((r, (m[r]["cup_metal"], m[r]["gem"], m[r]["quality_colour"])) for r in RARITIES)


def texture(rarity, pal=None):
    """one rarity's 32 x 64 texture (skyyart.Img): ivory shell layers shaded top-lit, rarity speckles (more with the rarity), a faint
    rarity tint from Uncommon up, the bottom two layers in the cup metal with a gem dot (Uncommon up), Mythic = a prism shimmer"""
    pal = pal or palettes()
    metal, gem, qcol = pal[rarity]
    r = RARITIES.index(rarity)
    img = SA.Img(TEX_W, TEX_H)
    tint = _hx(qcol)
    lay = layout()
    for i, (w, h, sy, qy, _cy) in enumerate(lay):
        cup = i < CUP_LAYERS
        # side strip: the light falls from the top of the egg; the middle of each face a little brighter (a round look)
        for y in range(h):
            for x in range(w):
                u = (x + 0.5) / w * 2 - 1
                vt = (i + (h - y - 0.5) / h) / len(lay)          # 0 = the bottom of the egg, 1 = the top
                if cup:
                    c = _ramp(metal, 0.35 + 0.45 * vt * len(lay) / CUP_LAYERS * 0.5 + 0.18 * (1 - abs(u)) - 0.08 * u)
                else:
                    c = _ramp(SHELL, 0.42 + 0.42 * vt + 0.16 * (1 - abs(u)) - 0.06 * u)
                    if r >= 1:
                        c = _mix(c, tint, 0.03 * min(r, 4))
                    if rarity == "Mythic":
                        c = _mix(c, _hx(PRISM[int((x + y + i) % len(PRISM))]), 0.22)
                img.put(x, sy + y, (c[0], c[1], c[2], 255))
        if cup and r >= 1 and i == 1:                          # the gem dot in the middle of the cup's upper band (every side)
            g = _ramp(gem, 0.75)
            img.put(w // 2 - 1, sy, (g[0], g[1], g[2], 255))
            img.put(w // 2, sy, (g[0], g[1], g[2], 255))
            if h > 1:
                g2 = _ramp(gem, 0.5)
                img.put(w // 2 - 1, sy + 1, (g2[0], g2[1], g2[2], 255))
                img.put(w // 2, sy + 1, (g2[0], g2[1], g2[2], 255))
        if not cup:                                             # speckles on the shell
            n = ((1, 1, 2, 2, 3, 3)[r] if h <= 2 else (2, 3, 4, 5, 6, 7)[r])
            rr = _rnd("speck", rarity, i)
            for k in range(n):
                sx, sy2 = int(rr[2 * k % 32] * w) % w, int(rr[(2 * k + 1) % 32] * h) % h
                c = _hx(PRISM[k % len(PRISM)]) if rarity == "Mythic" else _ramp(gem, 0.62 if r else 0.3)
                img.put(sx, sy + sy2, (c[0], c[1], c[2], 255))
        # the top / bottom square: a round light in the middle
        for y in range(w):
            for x in range(w):
                u, v = (x + 0.5) / w * 2 - 1, (y + 0.5) / w * 2 - 1
                d = (u * u + v * v) ** 0.5
                if cup:
                    c = _ramp(metal, 0.62 - 0.2 * d)
                else:
                    c = _ramp(SHELL, 0.85 - 0.22 * d - 0.05 * (u + v))
                    if r >= 1:
                        c = _mix(c, tint, 0.03 * min(r, 4))
                img.put(SQ_X + x, qy + y, (c[0], c[1], c[2], 255))
    return img


def texture_png(rarity, pal=None):
    return SA.png_encode(texture(rarity, pal))


def check(m=None):
    """structural checks of the model: anchors, 6 boxes, every face inside the texture, the vanilla egg box's outer size"""
    m = m or model()
    n = m["nodes"][0]
    names = []
    while True:
        names.append(n["name"])
        if n["shape"]["type"] != "none":
            break
        if n["name"] == "Origin_Item":
            boxes = n["children"]
            break
        n = n["children"][0]
    assert names == [a for a, _p in ANCHORS], names
    assert len(boxes) == len(LAYERS)
    lo = min(b["position"]["y"] - b["shape"]["settings"]["size"]["y"] / 2.0 for b in boxes)
    hi = max(b["position"]["y"] + b["shape"]["settings"]["size"]["y"] / 2.0 for b in boxes)
    wid = max(b["shape"]["settings"]["size"]["x"] for b in boxes)
    assert (lo, hi, wid) == (CENTER_Y - 8, CENTER_Y + 8, 14), (lo, hi, wid)
    for b in boxes:
        sz = b["shape"]["settings"]["size"]
        for f, t in b["shape"]["textureLayout"].items():
            fw, fh = (sz["x"], sz["y"]) if f in ("front", "back") else ((sz["z"], sz["y"]) if f in ("left", "right") else (sz["x"], sz["z"]))
            x, y = t["offset"]["x"], t["offset"]["y"]
            assert 0 <= x and x + fw <= TEX_W and 0 <= y and y + fh <= TEX_H, (b["name"], f)
    for a in range(len(boxes) - 1):            # stacked: each layer sits right on the one below
        b0, b1 = boxes[a], boxes[a + 1]
        assert abs((b0["position"]["y"] + b0["shape"]["settings"]["size"]["y"] / 2.0) - (b1["position"]["y"] - b1["shape"]["settings"]["size"]["y"] / 2.0)) < 1e-9
    return True


if __name__ == "__main__":
    check()
    print("model ok:", len(LAYERS), "layers", [w for w, _h in LAYERS], "textures", [len(texture_png(r)) for r in RARITIES])
