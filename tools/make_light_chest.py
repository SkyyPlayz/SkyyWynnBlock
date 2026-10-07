"""make_light_chest - first-pass LIGHT ARMOR chest model + texture for Blockbench (2026-10-06, the Copper chest; RESUME "FIRST JOB").

Design: the Copper body of research/cloud/light-armor/light-armor-sheet-v2.png / copper-chest-v2.png (black quilted leather, copper
trim, a diagonal brown bandolier with a copper buckle, a buckled belt with a pouch, layered round pauldrons with a copper rim + emblem).

The vanilla chest (Assets.zip Common/Items/Armors/Copper/Chest.blockymodel, read-only) gives the rig (Pelvis / Belly / Chest / L-Arm /
R-Arm) and the base plates; this script adds our pieces, re-packs every UV into a fresh atlas and paints it from code (no vanilla
pixels). The output is vanilla-derived, so it goes ONLY to the git-ignored models-local/ folder (PROJECT-RULES 2), never into git.

Run:  python tools/make_light_chest.py [Copper]
Out:  models-local/light-armor/<tier>/Chest.blockymodel, Chest_Texture.png, preview-front.png, preview-back.png, preview-34.png
Open the .blockymodel in Blockbench (Hytale Models plugin), with Chest_Texture.png next to it. Deterministic: same run = same bytes.
"""
import copy
import json
import math
import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyyart as SA  # noqa: E402


def hx(s):
    s = s.lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


# palettes = research/cloud/light-armor/make_sheets.py (the approved v2 sheets)
LEATHER = [hx(c) for c in ("#0a090c", "#1c191f", "#2b2730", "#3f3946", "#58515f")]
STRAP = [hx(c) for c in ("#1c1009", "#3e2516", "#5c3a22", "#7b5032", "#9a6a44")]
THREAD = hx("#6b6372")
METALS = {
    "Copper": [hx(c) for c in ("#3b1a0c", "#8a4220", "#c26a34", "#e89558", "#ffc48e")],
}

TEX_W = 192


# ------------------------------------------------------------------------------------------------------------------ geometry
def box(name, size, pos, rot_z=0.0, children=None):
    s = math.sin(math.radians(rot_z) / 2.0)
    c = math.cos(math.radians(rot_z) / 2.0)
    return {
        "id": name, "name": name,
        "position": {"x": pos[0], "y": pos[1], "z": pos[2]},
        "orientation": {"w": c, "x": 0, "y": 0, "z": s},
        "shape": {"offset": {"x": 0, "y": 0, "z": 0}, "stretch": {"x": 1, "y": 1, "z": 1}, "textureLayout": {},
                  "type": "box", "settings": {"size": {"x": size[0], "y": size[1], "z": size[2]}},
                  "unwrapMode": "custom", "visible": True, "doubleSided": False, "shadingMode": "flat"},
        "children": children or [],
    }


def find(nodes, name):
    for n in nodes:
        if n.get("name") == name:
            return n
        r = find(n.get("children") or [], name)
        if r:
            return r
    return None


def build_model(vanilla):
    m = copy.deepcopy(vanilla)
    nodes = m["nodes"]
    front = find(nodes, "FrontPlate")
    back = find(nodes, "BackPlate")
    belt = find(nodes, "Belt")
    # chest: bandolier (viewer's upper left -> lower right) + buckle, copper collar strips front + back
    front["children"] += [
        box("Bandolier", (4, 33, 1), (0, 0, 2.5), rot_z=-48),
        box("BandolierBuckle", (5, 5, 1), (0.5, 0.5, 3.2)),
        box("CollarFront", (30, 3, 5), (0, 11.5, 0.5)),
    ]
    back["children"] += [box("CollarBack", (30, 3, 5), (0, 11.5, -0.5))]
    # belt: big copper buckle + a pouch on the right hip with a copper button
    belt["children"] += [
        box("BeltBuckle", (6, 6, 1), (0, 0, 11.5)),
        box("Pouch", (8, 8, 3), (9, -4.5, 12.3), children=[box("PouchButton", (2, 2, 1), (0, 1.5, 1.8))]),
    ]
    # shoulders: a lower leather plate, a copper rim round the upper plate, a copper emblem on top
    for side, sx in (("L", 1), ("R", -1)):
        sh = find(nodes, side + "-ShoulderWoodenArmor")
        sh["name"] = side + "-Pauldron"
        sh["children"] = (sh.get("children") or []) + [
            box(side + "-PauldronLower", (14, 4, 22), (sx * 2.5, -5, 0), rot_z=-sx * 12),
            box(side + "-PauldronRim", (16, 2, 24), (0, -3, 0)),
            box(side + "-PauldronEmblem", (5, 1, 5), (sx * 1, 4.5, 0)),
        ]
    return m


# ------------------------------------------------------------------------------------------------------------------ UV atlas
FACE_WH = {"front": ("x", "y"), "back": ("x", "y"), "left": ("z", "y"), "right": ("z", "y"), "top": ("x", "z"), "bottom": ("x", "z")}


def all_boxes(nodes, out):
    for n in nodes:
        if (n.get("shape") or {}).get("type") == "box":
            out.append(n)
        all_boxes(n.get("children") or [], out)
    return out


def pack(model):
    """Shelf-pack every face of every box (largest first); returns {(node name, face): (x, y, w, h)} + the atlas height."""
    rects = []
    for n in all_boxes(model["nodes"], []):
        size = n["shape"]["settings"]["size"]
        for f, (a, b) in FACE_WH.items():
            w, h = int(math.ceil(size[a])), int(math.ceil(size[b]))
            if w and h:
                rects.append((n["name"], f, w, h))
    rects.sort(key=lambda r: (-r[3], -r[2], r[0], r[1]))
    place, x, y, row = {}, 0, 0, 0
    for name, f, w, h in rects:
        if x + w > TEX_W:
            x, y, row = 0, y + row, 0
        place[(name, f)] = (x, y, w, h)
        x += w
        row = max(row, h)
    height = y + row
    height = ((height + 31) // 32) * 32
    for n in all_boxes(model["nodes"], []):
        lay = {}
        for f in FACE_WH:
            if (n["name"], f) in place:
                px, py, _, _ = place[(n["name"], f)]
                lay[f] = {"offset": {"x": px, "y": py}, "mirror": {"x": False, "y": False}, "angle": 0}
        n["shape"]["textureLayout"] = lay
    return place, height


# ------------------------------------------------------------------------------------------------------------------ painting
def noise(x, y, seed):
    h = (x * 374761393 + y * 668265263 + seed * 2147483647) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 65535.0


def mul(c, f):
    return (c[0] * f, c[1] * f, c[2] * f)


def mix(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t)


class Face(object):
    def __init__(self, img, rect, seed):
        self.img, (self.x0, self.y0, self.w, self.h), self.seed = img, rect, seed

    def put(self, u, v, c):
        if 0 <= u < self.w and 0 <= v < self.h:
            self.img.put(self.x0 + u, self.y0 + v, (c[0], c[1], c[2], 255))

    def n(self, u, v):
        return noise(u, v, self.seed)


def leather(f, quilt=False, stitch=True, shade=1.0):
    for v in range(f.h):
        g = 1.08 - 0.22 * (v / max(1, f.h - 1))          # light from above
        for u in range(f.w):
            c = mix(LEATHER[2], LEATHER[3], f.n(u, v) * 0.35)
            if quilt:
                d, e = (u + v) % 6, (u - v) % 6
                if d == 0 or e == 0:
                    c = LEATHER[1]
                elif d == 1 or e == 5:
                    c = mix(c, LEATHER[3], 0.6)
            f.put(u, v, mul(c, g * shade))
    edge(f, LEATHER[0], LEATHER[3])
    if stitch and f.w >= 5 and f.h >= 5:
        for u in range(2, f.w - 2, 2):
            f.put(u, 1, THREAD)
            f.put(u, f.h - 2, THREAD)
        for v in range(3, f.h - 2, 2):
            f.put(1, v, THREAD)
            f.put(f.w - 2, v, THREAD)


def edge(f, dark, light):
    for u in range(f.w):
        f.put(u, f.h - 1, dark)
    for v in range(f.h):
        f.put(0, v, dark)
        f.put(f.w - 1, v, dark)
    for u in range(1, f.w - 1):
        f.put(u, 0, light if f.h > 2 else dark)


def strap(f, along_v=True):
    for v in range(f.h):
        for u in range(f.w):
            c = mix(STRAP[2], STRAP[3], f.n(u, v) * 0.5)
            f.put(u, v, c)
    if along_v:
        for v in range(f.h):
            f.put(0, v, STRAP[1])
            f.put(f.w - 1, v, STRAP[0])
            if f.w >= 4 and v % 3 != 2:
                f.put(1, v, STRAP[4]) if v % 3 == 0 else None
    else:
        for u in range(f.w):
            f.put(u, 0, STRAP[3])
            f.put(u, f.h - 1, STRAP[0])
            if f.h >= 5 and u % 3 == 0:
                f.put(u, 1, STRAP[4])
                f.put(u, f.h - 2, STRAP[4])


def metal(f, M, pits=True):
    for v in range(f.h):
        t = v / max(1, f.h - 1)
        base = mix(M[3], M[1], t) if f.h > 2 else (M[3] if v == 0 else M[1])
        for u in range(f.w):
            c = mix(base, M[2], 0.25 + 0.25 * f.n(u, v // 2 + 7))   # brushed along u
            if pits and f.n(u, v) > 0.93:
                c = M[1]
            f.put(u, v, c)
    if f.h > 2:
        for u in range(f.w):
            f.put(u, 0, M[4])
            f.put(u, f.h - 1, M[0])
    if f.w > 2:
        for v in range(f.h):
            f.put(0, v, M[2] if v else M[4])
            f.put(f.w - 1, v, M[0])


def rivet(f, u, v, M):
    f.put(u, v, M[4])
    f.put(u + 1, v, M[3])
    f.put(u, v + 1, M[2])
    f.put(u + 1, v + 1, M[0])


def buckle(f, M):
    metal(f, M, pits=False)
    for v in range(1, f.h - 1):
        for u in range(1, f.w - 1):
            if 1 < u < f.w - 2 and 1 < v < f.h - 2:
                f.put(u, v, STRAP[1])
    for v in range(1, f.h - 1):
        f.put(f.w // 2, v, M[3])                         # tongue


def paint(model, place, height, M):
    img = SA.Img(TEX_W, height)
    for i, ((name, face), rect) in enumerate(sorted(place.items())):
        f = Face(img, rect, i * 7 + 3)
        big = face in ("front", "back")
        if name in ("FrontPlate", "BackPlate"):
            leather(f, quilt=big)
            if big and f.w > 8 and f.h > 8:
                for (u, v) in ((2, 2), (f.w - 4, 2), (2, f.h - 4), (f.w - 4, f.h - 4)):
                    rivet(f, u, v, M)
        elif name in ("Braces", "R-Braces"):
            leather(f, shade=0.9)
        elif name == "Belt":
            strap(f, along_v=False)
            if big:
                for u in range(3, f.w - 3, 7):
                    rivet(f, u, 2, M)
        elif name in ("Front_Cloth_1", "Back_Cloth_1"):
            leather(f, stitch=False, shade=0.95)
            if big:
                for u in range(7, f.w - 1, 7):
                    for v in range(f.h - 1):
                        f.put(u, v, LEATHER[0])
                for u in range(f.w):
                    f.put(u, f.h - 1, M[2])
                    f.put(u, f.h - 2, M[1])
        elif name.endswith("-Pauldron"):
            leather(f, quilt=(face == "top"))
        elif name.endswith("-PauldronLower"):
            leather(f, shade=0.85)
        elif name in ("Bandolier",):
            strap(f, along_v=(face in ("front", "back", "left", "right")))
        elif name == "Pouch":
            strap(f, along_v=False)
            if face == "front":
                for u in range(f.w):
                    f.put(u, 3, STRAP[0])
                    for v in range(3):
                        f.put(u, v, mix(STRAP[1], STRAP[2], f.n(u, v) * 0.4))
        elif name in ("BandolierBuckle", "BeltBuckle"):
            if face == "front":
                buckle(f, M)
            else:
                metal(f, M, pits=False)
        else:                                            # collar, rims, emblem, button = copper
            metal(f, M)
            if name.endswith("Emblem") and face == "top":
                c = f.w // 2
                for v in range(f.h):
                    f.put(c, v, M[4])
                for u in range(f.w):
                    f.put(u, f.h // 2, M[4])
                f.put(c, f.h // 2, M[0])
    return img


# ------------------------------------------------------------------------------------------------------------------ main
def main():
    tier = sys.argv[1] if len(sys.argv) > 1 else "Copper"
    M = METALS[tier]
    z = SA.assets()
    vanilla = json.loads(z.read("Common/Items/Armors/%s/Chest.blockymodel" % tier).decode("utf-8-sig"))
    out = os.path.join(ROOT, "models-local", "light-armor", tier.lower())
    os.makedirs(out, exist_ok=True)
    model = build_model(vanilla)
    place, height = pack(model)
    img = paint(model, place, height, M)
    tex = SA.png_encode(img)
    with open(os.path.join(out, "Chest.blockymodel"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(model, fh, indent=2)
    with open(os.path.join(out, "Chest_Texture.png"), "wb") as fh:
        fh.write(tex)
    views = {"front": [0, 0, 0], "back": [0, 180, 0], "34": [15, 35, 0]}
    for k, rot in views.items():
        props = {"Rotation": rot, "Scale": 0.45, "Translation": [0, -8]}
        with open(os.path.join(out, "preview-%s.png" % k), "wb") as fh:
            fh.write(SA.render_icon(model, tex, props, size=256))
    print("wrote", out, "texture %dx%d" % (TEX_W, height), len(place), "faces")


if __name__ == "__main__":
    main()
