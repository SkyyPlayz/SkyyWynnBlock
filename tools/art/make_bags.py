"""make_bags - ASSETS for the new Accessory Bag (SkyyAccessories) and the Pocket Dimension bags (SkyySacks Magic Bags).

Skyy 2026-10-07: "lets make new items for the accessory bag, and the pocket dimension bags too, the current ones are boring. (i want the
pocket dimension to be a bag in the hot bar icon, and when you scroll to it, you pull it up Infront of you, then pull the mouth of the
bag open and it has a swirling portal inside the bag."

Art + animation assets only (no item JSON wiring, no build, no deploy). Everything lands in models-local/art/bags/ (git-ignored):
  Common/Items/SkyyAccessories/SkyyAccessories_Bag.blockymodel + _Texture.png   own jewellery satchel (black leather, gold, gems)
  Common/Items/SkyySacks/SkyySacks_Bag_<Rarity>.blockymodel + _Texture.png       own drawstring bag per rarity (Normal .. Mythic)
  Common/Items/SkyySacks/SkyySacks_Bag_Open.blockyanim                           item-model anim: mouth opens, portal swirls (20 s)
  Common/Items/SkyySacks/SkyySacks_Bag_OpenLoop.blockyanim                       fallback: always open, portal swirls (no re-open)
  Common/Characters/Animations/Items/SkyySacks/SkyySack_Lift(_FPS).blockyanim    player one-shot: lift the bag up + tug the mouth
  Server/Item/Animations/SkyySack.json                                           DRAFT player animation set (Parent Block + SackLift)
  Common/Icons/ItemsGenerated/SkyyAccessories_Bag.png, SkyySacks_Bag_<Rarity>.png 64x64 icons (premultiplied, skyyart.render_icon)
  sheet.png (icons + held poses closed / opening / open / swirl), preview-*.png, manifest.json

Models, textures and icons are our own geometry and pixels painted from code with hex palettes (no vanilla pixels). The two player
lift animations are DERIVED from vanilla player animations (Item idle -> Block idle frame-0 poses, read from Assets.zip at run time),
so the folder stays local. Deterministic: two runs give the same bytes.

Run:  python tools/art/make_bags.py
"""
import copy
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyyart as SA  # noqa: E402

OUT = os.path.join(ROOT, "models-local", "art", "bags")
SACK_DIR = "Common/Items/SkyySacks"
ACC_DIR = "Common/Items/SkyyAccessories"
ICON_DIR = "Common/Icons/ItemsGenerated"
CHAR_DIR = "Common/Characters/Animations/Items/SkyySacks"
ANIM_OPEN = SACK_DIR + "/SkyySacks_Bag_Open.blockyanim"
ANIM_LOOP = SACK_DIR + "/SkyySacks_Bag_OpenLoop.blockyanim"
LIFT_3P = CHAR_DIR + "/SkyySack_Lift.blockyanim"
LIFT_FPS = CHAR_DIR + "/SkyySack_Lift_FPS.blockyanim"
ANIMSET_ID = "SkyySack"
ANIMSET = "Server/Item/Animations/%s.json" % ANIMSET_ID
LIFT_KEY = "SackLift"

DEN = 2                    # texels per model unit (every shape: size in texels, stretch 1 / DEN) = 2x vanilla item density
ST = 1.0 / DEN
TEX_W = 256

# ------------------------------------------------------------------------------------------------------------------ palettes


def hx(s):
    s = s.lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


def ramp(*cols):
    return [hx(c) for c in cols]


def rs(r, t):
    """sample a dark -> light ramp at t (0..1, clamped)"""
    t = min(max(t, 0.0), 1.0) * (len(r) - 1)
    i = min(int(t), len(r) - 2)
    f = t - i
    a, b = r[i], r[i + 1]
    return (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, a[2] + (b[2] - a[2]) * f)


LEATHER = ramp("#0b090b", "#171315", "#221c1e", "#2e2627", "#3e3434", "#5a4c48")     # black leather, warm hint
LINING = ramp("#0c0614", "#1a0d2c", "#2b1648", "#3d2266")                            # inner velvet (seen when the mouth is open)
CORD_BROWN = ramp("#2a1d14", "#4a3424", "#6d4f36", "#94714f")
GOLD = ramp("#4a300a", "#7a5414", "#b07f22", "#dcae46", "#f6d986", "#fff4cc")
PORTAL = ramp("#05030f", "#140a38", "#2a1670", "#4626b0", "#3f5fe6", "#6d9cff", "#b49cff", "#f0e8ff")

# per rarity (SkyySacks BAG_RARITY order + the Mythic Omni): (name, item ids, metal ramp, gem ramp, gem size tx, side gems, belly band,
# feet, gold runes, cord ramp, rarity colour)
RARITIES = [
    ("Normal", ["Skyy_Sack_%s_Small"], ramp("#2c2f34", "#4a4f57", "#6d737c", "#959ba4", "#c4c9cf", "#eef0f2"),
     ramp("#2c1446", "#4a2373", "#7440a8", "#a274d8", "#d9c2f5"), 4, 0, False, False, False, CORD_BROWN, "#ffffff"),
    ("Unique", ["Skyy_Sack_%s_Medium"], GOLD,
     ramp("#4d3500", "#8a6200", "#d1a200", "#ffd84a", "#fff6c8"), 6, 0, True, False, False, ramp("#3a2a10", "#6b4e1c", "#a07a30", "#d0aa58"),
     "#ffff55"),
    ("Rare", ["Skyy_Sack_%s_Rare"], ramp("#34363e", "#575b66", "#8a8f9b", "#babfc9", "#e6e9ef", "#ffffff"),
     ramp("#4a0a42", "#84187a", "#c235b2", "#ee76e0", "#ffd8f8"), 6, 2, True, False, False, ramp("#2a1830", "#4c2c55", "#74487f", "#a070aa"),
     "#ff55ff"),
    ("Legendary", ["Skyy_Sack_%s_Large"], ramp("#21363e", "#3c5e69", "#64909c", "#98c4ce", "#cdeef4", "#f4feff"),
     ramp("#063e48", "#0e7584", "#1fb6c6", "#72ecf2", "#dcffff"), 8, 2, True, True, False, ramp("#14262c", "#28464f", "#447079", "#6da0aa"),
     "#55ffff"),
    ("Mythic", ["Skyy_Sack_Omni"], ramp("#1c1626", "#30264a", "#4a3a6c", "#6c5a92", "#9c8cc0", "#d6ccec"),
     ramp("#3c0c44", "#6c1c78", "#a63cb8", "#d886e4", "#ffe2ff"), 8, 4, True, True, True, ramp("#2a1c06", "#5a3e10", "#9a7020", "#d8b050"),
     "#cc66cc"),
]
SACK_CATS = ("Mining", "Foraging", "Farming", "Combat", "Smithing")      # SkyySacks BAG_CATS (one look per rarity, all 5 types share it)
ACC_ITEM = "Skyy_Accessory_Bag"
ACC_GEMS = [ramp("#4a0a0e", "#8a1a20", "#d23a3a", "#ff8a80", "#ffe0dc"),      # health red
            ramp("#0a2050", "#163f8f", "#2f6fe0", "#86b4ff", "#e2eeff"),      # mana blue
            ramp("#4d3a00", "#8a6800", "#d6a800", "#ffe066", "#fff8d6"),      # stamina yellow
            ramp("#0b3d1a", "#17702f", "#2fb34f", "#86eb98", "#e2ffe6"),      # speed green
            ramp("#3c0c44", "#6c1c78", "#a63cb8", "#d886e4", "#ffe2ff")]      # luck violet
ACC_MAIN_GEM = ramp("#2c0a46", "#521682", "#8a34c8", "#c28af0", "#f4e6ff")   # the clasp amethyst

# ------------------------------------------------------------------------------------------------------------------ math


def r6(v):
    v = round(float(v), 5)
    return 0 if v == 0 else (int(v) if v == int(v) else v)


def axis_quat(axis, deg):
    n = math.sqrt(sum(a * a for a in axis))
    s = math.sin(math.radians(deg) / 2.0)
    return (axis[0] / n * s, axis[1] / n * s, axis[2] / n * s, math.cos(math.radians(deg) / 2.0))


def qmul(a, b):
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return (aw * bx + ax * bw + ay * bz - az * by, aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw, aw * bw - ax * bx - ay * by - az * bz)


def qd(q):
    return {"x": r6(q[0]), "y": r6(q[1]), "z": r6(q[2]), "w": r6(q[3])}


def hsh(x, y, s=0):
    n = (x * 374761393 + y * 668265263 + s * 2147483647) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFF) / 65535.0


# ------------------------------------------------------------------------------------------------------------------ model + atlas
FACES = ("front", "back", "left", "right", "top", "bottom")
FACE_LIGHT = {"top": 1.10, "front": 1.0, "left": 0.93, "right": 0.88, "back": 0.86, "bottom": 0.74}


class Atlas(object):
    """Shelf packer over a TEX_W wide texture; jobs = (x, y, w, h, painter(face, u, v, w, h) -> rgb / rgba / None, face)."""

    def __init__(self):
        self.x = self.y = self.row = 0
        self.jobs = []
        self.shared = {}

    def alloc(self, w, h):
        if self.x + w > TEX_W:
            self.x, self.y, self.row = 0, self.y + self.row + 1, 0
        p = (self.x, self.y)
        self.x += w + 1
        self.row = max(self.row, h)
        return p

    def height(self):
        h = self.y + self.row + 1
        return ((h + 31) // 32) * 32

    def paint(self):
        img = SA.Img(TEX_W, self.height())
        for (x0, y0, w, h, fn, face) in self.jobs:
            for v in range(h):
                for u in range(w):
                    c = fn(face, u, v, w, h)
                    if c is None:
                        continue
                    a = c[3] if len(c) > 3 else 255
                    img.put(x0 + u, y0 + v, (c[0], c[1], c[2], a))
        return img


class Ids(object):
    def __init__(self):
        self.n = 0

    def next(self):
        self.n += 1
        return str(self.n - 1)


class Builder(object):
    def __init__(self):
        self.ids = Ids()
        self.atlas = Atlas()
        root = self.node("R-Attachment")
        root["shape"]["settings"] = {"isPiece": True}
        root["shape"]["doubleSided"] = True
        self.root = root

    def node(self, name, pos=(0, 0, 0), quat=(0, 0, 0, 1), parent=None):
        n = {"id": self.ids.next(), "name": name, "children": [],
             "position": {"x": r6(pos[0]), "y": r6(pos[1]), "z": r6(pos[2])}, "orientation": qd(quat),
             "shape": {"type": "none", "offset": {"x": 0, "y": 0, "z": 0}, "stretch": {"x": 1, "y": 1, "z": 1}, "settings": {},
                       "visible": True, "doubleSided": False, "shadingMode": "standard", "unwrapMode": "custom", "textureLayout": {}}}
        if parent is not None:
            parent["children"].append(n)
        return n

    def _layout(self, key, sizes, fn):
        if key is not None and key in self.atlas.shared:
            return self.atlas.shared[key]
        lay = {}
        for face, (w, h) in sizes:
            x, y = self.atlas.alloc(w, h)
            self.atlas.jobs.append((x, y, w, h, fn, face))
            lay[face] = {"offset": {"x": x, "y": y}, "mirror": {"x": False, "y": False}, "angle": 0}
        if key is not None:
            self.atlas.shared[key] = lay
        return lay

    def box(self, name, size, pos, fn, parent, quat=(0, 0, 0, 1), key=None, shading="standard", offset=(0, 0, 0), visible=True):
        """size in TEXELS (w, h, d); pos / offset in model units; shown at size / DEN units."""
        w, h, d = size
        sizes = (("front", (w, h)), ("back", (w, h)), ("left", (d, h)), ("right", (d, h)), ("top", (w, d)), ("bottom", (w, d)))
        n = self.node(name, pos, quat, parent)
        n["shape"].update({"type": "box", "offset": {"x": r6(offset[0]), "y": r6(offset[1]), "z": r6(offset[2])},
                           "stretch": {"x": r6(ST), "y": r6(ST), "z": r6(ST)}, "settings": {"size": {"x": w, "y": h, "z": d}},
                           "visible": visible, "shadingMode": shading, "textureLayout": self._layout(key, sizes, fn)})
        return n

    def quad(self, name, size, pos, parent, layout, quat=(0, 0, 0, 1), shading="fullbright", visible=True):
        w, h = size
        n = self.node(name, pos, quat, parent)
        n["shape"].update({"type": "quad", "stretch": {"x": r6(ST), "y": r6(ST), "z": 1}, "settings": {"size": {"x": w, "y": h}},
                           "visible": visible, "doubleSided": True, "shadingMode": shading, "textureLayout": {"front": layout}})
        return n

    def model(self):
        return {"lod": "auto", "nodes": [self.root]}


# ------------------------------------------------------------------------------------------------------------------ materials


def lit(c, face, k=1.0):
    f = FACE_LIGHT[face] * k
    return (min(255, c[0] * f), min(255, c[1] * f), min(255, c[2] * f))


def leather(stitch=None, seam=2, wrinkle=True, base=0.45, seed=1):
    """black leather: grain noise, soft edge darkening, a dashed stitch line `seam` texels in from the edge (face sides only)."""
    def fn(face, u, v, w, h):
        e = min(u, v, w - 1 - u, h - 1 - v)
        t = base + 0.10 * (hsh(u, v, seed) - 0.5) + 0.06 * (hsh(u // 2, v // 3, seed + 7) - 0.5)
        if wrinkle and face in ("front", "back", "left", "right"):
            t += 0.07 * math.sin(u * 1.3 + 0.9 * math.sin(v * 0.45 + seed)) * (0.5 + 0.5 * math.sin(v * 0.21 + u * 0.07))
        if e == 0:
            t -= 0.07
        if stitch is not None and face in ("front", "back", "left", "right") and w > 2 * seam + 2 and h > 2 * seam + 2:
            ev = min(v, h - 1 - v)                                           # stitch rows run along the top / bottom seams only
            if ev == seam and (u % 3) != 0:
                return lit(rs(stitch, 0.30 + 0.15 * hsh(u, v, 3)), face)
            if ev == seam + 1 and (u % 3) != 0:
                t -= 0.06                                                    # the stitch's shadow line
        return lit(rs(LEATHER, t), face)
    return fn


def metal(r, glint=True):
    """bevelled metal: lit top-left edge, dark bottom-right edge, brushed body, a glint."""
    def fn(face, u, v, w, h):
        t = 0.55 + 0.08 * math.sin((u + v * 0.35) * 1.7) * 0.5
        if u == 0 or v == 0:
            t += 0.22
        if u == w - 1 or v == h - 1:
            t -= 0.25
        if glint and w >= 3 and h >= 3 and u == 1 and v == 1:
            t = 1.0
        return lit(rs(r, t), face, 1.0 if face != "bottom" else 0.95)
    return fn


def gem(r):
    """faceted gem: bright upper-left facet, a crease on the diagonals, white glint (fullbright in game)."""
    def fn(face, u, v, w, h):
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        d = (abs(u - cx) + abs(v - cy)) / max(1.0, cx + cy)
        t = 0.95 - 0.5 * d - 0.18 * ((u + v) / max(1.0, w + h - 2) - 0.5)
        if abs((u - cx) - (v - cy)) < 0.6 or abs((u - cx) + (v - cy)) < 0.6:
            t -= 0.08
        if u == 0 or v == 0 or u == w - 1 or v == h - 1:
            t -= 0.18
        if w >= 3 and u == int(cx * 0.5) and v == int(cy * 0.5):
            return (255, 255, 255)
        return rs(r, t)
    return fn


def cord(r):
    """twisted cord: diagonal twist bands."""
    def fn(face, u, v, w, h):
        t = 0.45 + 0.3 * math.sin((u + v) * 1.6) + 0.06 * (hsh(u, v, 11) - 0.5)
        return lit(rs(r, t), face)
    return fn


def petal(stitch, trim):
    """mouth flap: leather outside (front = outward), velvet lining inside (back), a metal-thread trim along the top edge."""
    out = leather(stitch, seam=2, base=0.48, seed=5)

    def fn(face, u, v, w, h):
        if face == "back":
            t = 0.55 + 0.25 * (v / max(1.0, h - 1)) + 0.08 * (hsh(u, v, 21) - 0.5)
            if v == 0:
                return rs(trim, 0.7)
            return rs(LINING, t)
        if face == "top" or (face in ("front", "left", "right") and v == 0):
            return lit(rs(trim, 0.75 if (u % 2) == 0 else 0.55), face)
        return out(face, u, v, w, h)
    return fn


def flat(c):
    def fn(face, u, v, w, h):
        return lit(c, face)
    return fn


def runes(gold, base):
    """belly band of the Mythic bag: dark metal with small glowing gold rune marks."""
    m = metal(base, glint=False)

    def fn(face, u, v, w, h):
        if face in ("front", "back", "left", "right") and h >= 3 and 0 < v < h - 1 and (u % 5) in (1, 2) and hsh(u // 5, 0, 31) > 0.3:
            return rs(gold, 0.85 if (u + v) % 2 else 0.65)
        return m(face, u, v, w, h)
    return fn


# ------------------------------------------------------------------------------------------------------------------ portal frames
PORTAL_PX = 22             # one swirl frame, texels (the disc quad is 22 x 22 texels = 11 x 11 units)
PORTAL_FRAMES = 8
PORTAL_STEP = 5            # animation frames per swirl frame (60 fps: 12 swirl frames / s, like the vanilla fire strip)


def portal_frame_fn(frames_y0):
    """the vertical strip of PORTAL_FRAMES swirl frames (frame k at y0 + k * PORTAL_PX). Round cut-out (alpha 0 outside)."""
    def fn(face, u, v, w, h):
        k, vv = divmod(v, PORTAL_PX)
        c = (PORTAL_PX - 1) / 2.0
        dx, dy = u - c, vv - c
        r = math.hypot(dx, dy) / (c + 0.5)
        if r > 1.0:
            return (0, 0, 0, 0)
        ang = math.atan2(dy, dx)
        ph = 2 * math.pi * k / PORTAL_FRAMES
        s = math.sin(3 * ang + 7.0 * r - ph)                     # 3 spiral arms, turning one arm-step per cycle
        depth = 0.18 + 0.55 * (1.0 - r) ** 0.8                   # brighter towards the core
        t = depth + 0.22 * s * (0.4 + r)
        if r < 0.16:
            t = 0.97                                             # white-violet core
        if r > 0.86:
            t = 0.42 + 0.25 * math.sin(10 * ang - ph * 2)        # bright churning rim
        return rs(PORTAL, t) + (255,)
    return fn


def portal_arms_fn(face, u, v, w, h):
    """a static 2-arm spiral (cut-out) that turns on its own node above the swirl frames."""
    c = (w - 1) / 2.0
    dx, dy = u - c, v - c
    r = math.hypot(dx, dy) / (c + 0.5)
    if r > 0.92 or r < 0.12:
        return (0, 0, 0, 0)
    ang = math.atan2(dy, dx)
    s = math.sin(2 * ang + 9.0 * r)
    if s < 0.55:
        return (0, 0, 0, 0)
    return rs(PORTAL, 0.62 + 0.36 * (s - 0.55) / 0.45 * (1.0 - r * 0.5)) + (255,)


# ------------------------------------------------------------------------------------------------------------------ the sack
# profile (units, y up from the bag bottom): (y0, y1, half width) - each level = two crossed boxes (an octagonal pouch)
SACK_LEVELS = ((0.0, 1.5, 5.0, False), (1.5, 4.0, 7.5, False), (4.0, 11.0, 9.0, True), (11.0, 14.0, 8.0, False),
               (14.0, 16.5, 6.2, False), (16.5, 19.5, 4.8, False))   # (y0, y1, half width, stitched)
NECK_Y = 19.5              # top of the cinched neck = the petal pivot ring height
PORTAL_LIFT = 1.4          # the portal disc sits this far above the neck top (inside the open flaps, easy to see)
PETALS = 8
PETAL_R = 4.2              # pivot ring radius
PETAL_TX = (12, 12, 3)     # 6 x 6 x 1.5 units
CLOSED_DEG, OPEN_DEG = -30.0, 30.0      # petal pitch (outward +) closed / open
BAG_DROP = -10.0           # the bag node below the grip (R-Attachment) so the body centre sits in the hands (Block hold)
CORD_TILT = 10.0


def build_sack(spec):
    name, _ids, M, G, gsz, side, band, feet, rune, C, _col = spec
    b = Builder()
    bag = b.node("Bag", (0, BAG_DROP, 0), parent=b.root)
    stitch = M
    for i, (y0, y1, hw, sti) in enumerate(SACK_LEVELS):
        hu = y1 - y0
        wa, wb, wc = int(round(hw * 2 * DEN)), int(round(hw * 2 * 0.62 * DEN)), int(round(hw * 2 * 0.86 * DEN))
        ht = int(round(hu * DEN))
        th = stitch if sti else None
        b.box("Body%dA" % i, (wa, ht, wb), (0, (y0 + y1) / 2.0, 0), leather(th, seam=2, seed=i + 1), bag)
        b.box("Body%dB" % i, (wb, ht, wa), (0, (y0 + y1) / 2.0, 0), leather(th, seam=2, seed=i + 11), bag)
        b.box("Body%dC" % i, (wc, ht, wc), (0, (y0 + y1) / 2.0, 0), leather(th, seam=2, seed=i + 21), bag)
    # the gathered neck cord (a ring of 4 cord boxes)
    ny = 17.6
    rr = 5.2
    for k, (pos, size) in enumerate((((0, ny, rr), (24, 3, 3)), ((0, ny, -rr), (24, 3, 3)),
                                     ((rr, ny, 0), (3, 3, 24)), ((-rr, ny, 0), (3, 3, 24)))):
        b.box("NeckCord%d" % k, size, pos, cord(C), bag, key="neckcord%d" % (k // 2))
    # inner floor of the mouth (dark velvet), just under the portal
    b.box("Throat", (18, 2, 18), (0, NECK_Y - 0.6, 0), lambda f, u, v, w, h: rs(LINING, 0.15 + 0.1 * hsh(u, v, 41)), bag)
    # mouth flaps
    for k in range(PETALS):
        yaw = 360.0 * k / PETALS
        pv = b.node("FlapPivot%d" % k, (PETAL_R * math.sin(math.radians(yaw)), NECK_Y - 0.4, PETAL_R * math.cos(math.radians(yaw))),
                    axis_quat((0, 1, 0), yaw), bag)
        b.box("Flap%d" % k, PETAL_TX, (0, 0, 0), petal(stitch, M), pv, quat=axis_quat((1, 0, 0), CLOSED_DEG), key="petal",
              offset=(0, PETAL_TX[1] / 2.0 / DEN, 0))
    # the portal (hidden at rest = closed; the Open animation shows it): swirl frames + a counter-turning spiral
    portal = b.node("Portal", (0, NECK_Y + PORTAL_LIFT, 0), parent=bag)
    spin_a = b.node("PortalSpinA", parent=portal)
    spin_b = b.node("PortalSpinB", (0, 0.15, 0), parent=portal)
    fx, fy = b.atlas.alloc(PORTAL_PX, PORTAL_PX * PORTAL_FRAMES)
    b.atlas.jobs.append((fx, fy, PORTAL_PX, PORTAL_PX * PORTAL_FRAMES, portal_frame_fn(fy), "front"))
    face_up = axis_quat((1, 0, 0), -90)
    lay = {"offset": {"x": fx, "y": fy}, "mirror": {"x": False, "y": False}, "angle": 0}
    b.quad("PortalDisc", (PORTAL_PX, PORTAL_PX), (0, 0, 0), spin_a, lay, quat=face_up, visible=False)
    ax_, ay_ = b.atlas.alloc(PORTAL_PX, PORTAL_PX)
    b.atlas.jobs.append((ax_, ay_, PORTAL_PX, PORTAL_PX, portal_arms_fn, "front"))
    lay2 = {"offset": {"x": ax_, "y": ay_}, "mirror": {"x": False, "y": False}, "angle": 0}
    b.quad("PortalArms", (PORTAL_PX, PORTAL_PX), (0, 0, 0), spin_b, lay2, quat=face_up, visible=False)
    # drawstrings: two cords from the front of the neck, a metal aglet and a gem bead each
    for side_, sx in (("L", -1), ("R", 1)):
        cp = b.node("Cord" + side_, (sx * 1.6, ny - 0.4, 5.9), axis_quat((0, 0, 1), sx * CORD_TILT), bag)
        b.box("CordRope" + side_, (2, 14, 2), (0, 0, 0), cord(C), cp, key="cordrope", offset=(0, -3.5, 0))
        b.box("Aglet" + side_, (3, 3, 3), (0, -7.4, 0), metal(M), cp, key="aglet", shading="flat")
        b.box("Bead" + side_, (4, 4, 4), (0, -9.2, 0), gem(G), cp, key="bead", shading="fullbright",
              quat=axis_quat((0, 1, 0), 45))
    # belly band, emblem plate + gem (rarity grows the gem), side gems, feet
    by = 9.5
    if band:
        bm = runes(GOLD, M) if rune else metal(M, glint=False)
        z_b, z_a = 9.0 * 0.62, 9.0
        b.box("BandF", (22, 3, 1), (0, by, z_a + 0.25), bm, bag, key="bandfb", shading="flat")
        b.box("BandB", (22, 3, 1), (0, by, -z_a - 0.25), bm, bag, key="bandfb", shading="flat")
        b.box("BandL", (1, 3, 22), (-z_a - 0.25, by, 0), bm, bag, key="bandlr", shading="flat")
        b.box("BandR", (1, 3, 22), (z_a + 0.25, by, 0), bm, bag, key="bandlr", shading="flat")
        b.box("BandCF", (36, 3, 1), (0, by, z_b + 0.25), bm, bag, key="bandc", shading="flat")
        b.box("BandCB", (36, 3, 1), (0, by, -z_b - 0.25), bm, bag, key="bandc", shading="flat")
        b.box("BandCL", (1, 3, 36), (-z_b - 0.25, by, 0), bm, bag, key="bandc2", shading="flat")
        b.box("BandCR", (1, 3, 36), (z_b + 0.25, by, 0), bm, bag, key="bandc2", shading="flat")
    plate = gsz + 4
    b.box("Emblem", (plate, plate, 2), (0, by, 9.25), metal(GOLD if rune else M), bag, quat=axis_quat((0, 0, 1), 45), shading="flat")
    b.box("Gem", (gsz, gsz, 3), (0, by, 9.7), gem(G), bag, quat=axis_quat((0, 0, 1), 45), shading="fullbright")
    sides = [(-5.6, by, 7.9), (5.6, by, 7.9), (-5.6, by, -7.9), (5.6, by, -7.9)][:side]
    for k, p in enumerate(sides):
        yaw = math.degrees(math.atan2(p[0], p[2]))
        b.box("SideGem%d" % k, (4, 4, 2), p, gem(G), bag, quat=qmul(axis_quat((0, 1, 0), yaw), axis_quat((0, 0, 1), 45)),
              key="sidegem", shading="fullbright")
    if feet:
        for k, (x, z) in enumerate(((-4.2, 4.2), (4.2, 4.2), (-4.2, -4.2), (4.2, -4.2))):
            b.box("Foot%d" % k, (4, 2, 4), (x, -0.4, z), metal(M), bag, key="foot", shading="flat")
    return b


# ------------------------------------------------------------------------------------------------------------------ accessory bag
def build_accessory():
    """a jewellery satchel hanging from the hand: black leather body + flap, gold piping / corners / handle, an amethyst clasp,
    five small line gems on the flap (the accessory lines), a ring and an amulet hanging on the sides."""
    b = Builder()
    s = b.node("Satchel", (0, -1.0, 0), parent=b.root)
    st = GOLD
    # handle (gold arch)
    b.box("HandleTop", (20, 3, 3), (0, 0, 0), metal(GOLD), s, shading="flat")
    for side, x in (("L", -4.6), ("R", 4.6)):
        b.box("HandleLeg" + side, (3, 9, 3), (x, -2.6, 0), metal(GOLD), s, key="handleleg", shading="flat")
        b.box("HandleRing" + side, (5, 3, 5), (x, -4.9, 0), metal(GOLD), s, key="handlering", shading="flat")
    # body
    b.box("Body", (36, 24, 14), (0, -11.5, 0), leather(st, seam=3, seed=3), s)
    b.box("BodyBase", (34, 2, 12), (0, -18.0, 0), leather(None, seed=4, wrinkle=False, base=0.35), s)
    for side, x in (("L", -9.25), ("R", 9.25)):
        b.box("Gusset" + side, (2, 20, 10), (x, -11.5, 0), leather(None, seed=6, base=0.3), s, key="gusset")
    # flap: top + front, gold piping along its lower edge, a tongue with the clasp
    b.box("FlapTop", (38, 2, 15), (0, -5.0, 0.2), leather(st, seam=2, seed=8, base=0.52), s)
    b.box("FlapFront", (38, 14, 2), (0, -8.5, 4.0), leather(st, seam=2, seed=9, base=0.52), s)
    b.box("FlapPiping", (38, 1, 3), (0, -12.1, 4.1), metal(GOLD, glint=False), s, shading="flat")
    b.box("FlapTongue", (10, 6, 2), (0, -13.5, 4.0), leather(st, seam=1, seed=12, base=0.5), s)
    b.box("ClaspPlate", (8, 8, 2), (0, -13.6, 4.6), metal(GOLD), s, shading="flat")
    b.box("ClaspGem", (6, 6, 3), (0, -13.6, 5.0), gem(ACC_MAIN_GEM), s, quat=axis_quat((0, 0, 1), 45), shading="fullbright")
    for k, g in enumerate(ACC_GEMS):
        x = -5.2 + 2.6 * k
        b.box("LineSet%d" % k, (4, 4, 1), (x, -7.6, 4.6), metal(GOLD, glint=False), s, key="lineset", shading="flat")
        b.box("LineGem%d" % k, (3, 3, 2), (x, -7.6, 4.85), gem(g), s, quat=axis_quat((0, 0, 1), 45), shading="fullbright")
    # gold corner caps on the bottom
    for k, (x, z) in enumerate(((-8.4, 2.9), (8.4, 2.9), (-8.4, -2.9), (8.4, -2.9))):
        b.box("Corner%d" % k, (4, 4, 4), (x, -17.2, z), metal(GOLD), s, key="corner", shading="flat")
    # hanging charms: a gold ring with a ruby (left), an amulet on a chain (right)
    ch = b.node("CharmL", (-9.9, -7.0, 2.0), axis_quat((0, 0, 1), -8), s)
    for k in range(3):
        b.box("ChainL%d" % k, (2, 3, 2), (0, -1.0 - 1.4 * k, 0), metal(GOLD, glint=False), ch, key="chain", shading="flat",
              quat=axis_quat((0, 1, 0), 90 * (k % 2)))
    ring = b.node("Ring", (0, -6.4, 0), axis_quat((0, 1, 0), 70), ch)
    for k, (pos, size) in enumerate((((0, 1.6, 0), (6, 2, 2)), ((0, -1.6, 0), (6, 2, 2)), ((1.6, 0, 0), (2, 6, 2)),
                                     ((-1.6, 0, 0), (2, 6, 2)))):
        b.box("RingBand%d" % k, size, pos, metal(GOLD), ring, key="ringband%d" % (k // 2), shading="flat")
    b.box("RingGem", (3, 3, 3), (0, 2.6, 0), gem(ACC_GEMS[0]), ring, quat=axis_quat((0, 1, 0), 45), shading="fullbright")
    ch2 = b.node("CharmR", (9.9, -7.0, 2.0), axis_quat((0, 0, 1), 8), s)
    for k in range(4):
        b.box("ChainR%d" % k, (2, 3, 2), (0, -1.0 - 1.4 * k, 0), metal(GOLD, glint=False), ch2, key="chain", shading="flat",
              quat=axis_quat((0, 1, 0), 90 * (k % 2)))
    b.box("AmuletFrame", (7, 9, 2), (0, -8.6, 0), metal(GOLD), ch2, shading="flat")
    b.box("AmuletGem", (5, 7, 3), (0, -8.6, 0.2), gem(ACC_GEMS[1]), ch2, shading="fullbright")
    return b


# ------------------------------------------------------------------------------------------------------------------ animations
OPEN_DUR = 1200            # 20 s at 60 fps: lcm of the swirl strip (8 x 5), the arms turn (120) and the disc turn (400)
ARMS_TURN = 120            # the spiral arms: one turn in 2 s
DISC_TURN = 400            # the swirl disc: one turn the other way in 6.7 s


def key(t, delta, interp="linear"):
    k = {"time": int(t), "delta": delta}
    if interp:
        k["interpolationType"] = interp
    return k


def chan(position=None, orientation=None, visible=None, uv=None):
    return {"position": position or [], "orientation": orientation or [], "shapeStretch": [], "shapeVisible": visible or [],
            "shapeUvOffset": uv or []}


def spin_keys(dur, turn, sign):
    """linear quaternion keys about +Y, 90 deg steps (each step < 180 deg: unambiguous path, like SpinningFire4)."""
    out = []
    steps = (dur // turn) * 4
    for k in range(steps + 1):
        out.append(key(turn * k // 4, qd(axis_quat((0, 1, 0), sign * 90.0 * k))))
    return out


def build_open_anim(loop_only):
    """Item-model animation. Open: frames 0-20 the mouth flaps swing open (closed rest -> open, small overshoot), the drawstrings
    loosen, the portal appears at frame 8; it stays open and swirling; frames 1180-1200 it closes again and the loop re-opens it
    (a 'breath' every 20 s). OpenLoop: open the whole time (no closing)."""
    na = {}
    d_open = OPEN_DEG - CLOSED_DEG
    if loop_only:
        pk = [key(0, qd(axis_quat((1, 0, 0), d_open))), key(OPEN_DUR, qd(axis_quat((1, 0, 0), d_open)))]
        vis = [key(0, True, None)]
    else:
        pk = [key(0, qd(axis_quat((1, 0, 0), 0))), key(6, qd(axis_quat((1, 0, 0), d_open * 0.35))),
              key(14, qd(axis_quat((1, 0, 0), d_open + 7))), key(20, qd(axis_quat((1, 0, 0), d_open))),
              key(OPEN_DUR - 20, qd(axis_quat((1, 0, 0), d_open))), key(OPEN_DUR - 8, qd(axis_quat((1, 0, 0), d_open * 0.4))),
              key(OPEN_DUR, qd(axis_quat((1, 0, 0), 0)))]
        vis = [key(0, False, None), key(8, True, None), key(OPEN_DUR - 6, False, None)]
    for k in range(PETALS):
        na["Flap%d" % k] = chan(orientation=pk)
    uv = []
    for i in range(OPEN_DUR // PORTAL_STEP):
        uv.append(key(i * PORTAL_STEP, {"x": 0, "y": -PORTAL_PX * (i % PORTAL_FRAMES)}, None))
    na["PortalDisc"] = chan(visible=vis, uv=uv)
    na["PortalArms"] = chan(visible=list(vis))
    na["PortalSpinA"] = chan(orientation=spin_keys(OPEN_DUR, DISC_TURN, -1))
    na["PortalSpinB"] = chan(orientation=spin_keys(OPEN_DUR, ARMS_TURN, 1))
    for side, sx in (("L", -1), ("R", 1)):
        ck = []
        if not loop_only:
            ck += [key(0, qd(axis_quat((0, 0, 1), 0))), key(10, qd(axis_quat((0, 0, 1), sx * 16))), key(20, qd(axis_quat((0, 0, 1), sx * 8)))]
            t0 = 60
        else:
            ck += [key(0, qd(axis_quat((0, 0, 1), sx * 8)))]
            t0 = 60
        t, n = t0, 0
        while t < OPEN_DUR - (20 if not loop_only else 0):
            ck.append(key(t, qd(axis_quat((0, 0, 1), sx * (8 + (3 if n % 2 == 0 else -1))))))
            t += 60
            n += 1
        ck.append(key(OPEN_DUR, qd(axis_quat((0, 0, 1), 0 if not loop_only else sx * 8))))
        na["Cord" + side] = chan(orientation=ck)
    return {"formatVersion": 1, "duration": OPEN_DUR, "holdLastKeyframe": False, "nodeAnimations": na}


def _first(keys, ident):
    return keys[0]["delta"] if keys else ident


def _qn(d):
    q = (d["x"], d["y"], d["z"], d["w"])
    n = math.sqrt(sum(c * c for c in q))
    return tuple(c / n for c in q)


def lift_anim(z, src_a, src_b, dur, plan):
    """A one-shot player animation from vanilla pose A (frame 0 of src_a) to pose B (frame 0 of src_b), shaped by plan:
    [(time, weight of B, {node: (extra quat about X deg, about Z deg, extra position (x, y, z))})]. holdLastKeyframe: the end pose
    = pose B exactly, so the set's Idle (vanilla Block idle) takes over without a jump."""
    A = json.loads(z.read("Common/Characters/Animations/Items/" + src_a).decode("utf-8-sig"))["nodeAnimations"]
    B = json.loads(z.read("Common/Characters/Animations/Items/" + src_b).decode("utf-8-sig"))["nodeAnimations"]
    na = {}
    for node in sorted(set(A) | set(B), key=lambda n: (list(B).index(n) if n in B else 99, n)):
        a, bb = A.get(node, chan()), B.get(node, chan())
        has_p = bool(a["position"] or bb["position"])
        has_o = bool(a["orientation"] or bb["orientation"])
        pk, ok = [], []
        for (t, wb, extra) in plan:
            ex = extra.get(node)
            if has_p or (ex and any(ex[2])):
                pa = _first(a["position"], {"x": 0, "y": 0, "z": 0})
                pb = _first(bb["position"], {"x": 0, "y": 0, "z": 0})
                p = [pa[c] + (pb[c] - pa[c]) * wb for c in "xyz"]
                if ex:
                    p = [p[i] + ex[2][i] for i in range(3)]
                pk.append(key(t, {"x": r6(p[0]), "y": r6(p[1]), "z": r6(p[2])}, "smooth"))
            if has_o or ex:
                qa = _qn(_first(a["orientation"], {"x": 0, "y": 0, "z": 0, "w": 1}))
                qb = _qn(_first(bb["orientation"], {"x": 0, "y": 0, "z": 0, "w": 1}))
                if sum(qa[i] * qb[i] for i in range(4)) < 0:
                    qb = tuple(-c for c in qb)
                q = tuple(qa[i] + (qb[i] - qa[i]) * wb for i in range(4))
                n = math.sqrt(sum(c * c for c in q))
                q = tuple(c / n for c in q)
                if ex:
                    q = qmul(q, qmul(axis_quat((1, 0, 0), ex[0]), axis_quat((0, 0, 1), ex[1])))
                ok.append(key(t, qd(q), "smooth"))
        if pk or ok:
            na[node] = chan(position=pk, orientation=ok)
    return {"formatVersion": 1, "duration": dur, "holdLastKeyframe": True, "nodeAnimations": na}


# 3rd person: from the one-hand Item idle (bag low at the side) up to the two-hand Block idle (held in front, both hands), with a lift
# overshoot (arms 14 deg higher, the grip 3 units up) and then the LEFT hand tugging the mouth open (left forearm up 22 deg, back).
LIFT_PLAN_3P = [
    (0, 0.0, {}),
    (10, 1.0, {"R-Arm": (-14, 0, (0, 0, 0)), "L-Arm": (-14, 0, (0, 0, 0)), "R-Attachment": (0, 0, (0, 3, 0))}),
    (16, 1.0, {"L-Forearm": (-22, 0, (0, 0, 0)), "L-Hand": (-10, 0, (0, 0, 0)), "R-Attachment": (0, 0, (0, 1, 0))}),
    (22, 1.0, {"L-Forearm": (-6, 0, (0, 0, 0))}),
    (30, 1.0, {}),
]
# 1st person (only the right arm is drawn): Item idle FPS -> Block idle FPS, the grip lifts 5 units with a small roll (the tug).
LIFT_PLAN_FPS = [
    (0, 0.0, {}),
    (9, 1.0, {"R-Attachment": (0, 0, (0, 5, 0)), "R-Forearm": (-8, 0, (0, 0, 0))}),
    (15, 1.0, {"R-Attachment": (0, 0, (0, 2, 0)), "R-Hand": (0, 10, (0, 0, 0))}),
    (22, 1.0, {}),
]


def animset_draft(z):
    blk = json.loads(z.read("Server/Item/Animations/Block.json").decode("utf-8-sig"))
    d = {"$Comment": "DRAFT (SkyWynn tools/art/make_bags.py): the Pocket Dimension bag's player animation set. Parent Block = the vanilla "
                     "two-hand 'hold it in front' idle / walk / run / ... ; SackLift = our one-shot lift + mouth tug, played by the "
                     "item's SwapTo interaction (Effects.ItemAnimationId).",
         "Parent": "Block",
         "Animations": {LIFT_KEY: {"ThirdPerson": LIFT_3P[len("Common/"):], "FirstPerson": LIFT_FPS[len("Common/"):],
                                   "Speed": 1, "Looping": False, "BlendingDuration": 0.1}}}
    for k in ("Camera", "WiggleWeights"):
        if k in blk:
            d[k] = blk[k]
    return d


# ------------------------------------------------------------------------------------------------------------------ posing (previews)
def _sample_q(keys, t):
    if t <= keys[0]["time"]:
        return _qn(keys[0]["delta"])
    for a, b in zip(keys, keys[1:]):
        if a["time"] <= t <= b["time"]:
            f = (t - a["time"]) / float(max(1, b["time"] - a["time"]))
            qa, qb = _qn(a["delta"]), _qn(b["delta"])
            if sum(qa[i] * qb[i] for i in range(4)) < 0:
                qb = tuple(-c for c in qb)
            q = tuple(qa[i] + (qb[i] - qa[i]) * f for i in range(4))
            n = math.sqrt(sum(c * c for c in q))
            return tuple(c / n for c in q)
    return _qn(keys[-1]["delta"])


def _step(keys, t):
    v = keys[0]["delta"]
    for k in keys:
        if k["time"] <= t:
            v = k["delta"]
    return v


def pose(model, anim, t):
    """the model at animation frame t (orientation = rest * delta, visibility, UV window = layout offset - delta)."""
    m = copy.deepcopy(model)
    idx = {}

    def walk(n):
        idx[n["name"]] = n
        for c in n["children"]:
            walk(c)
    for n in m["nodes"]:
        walk(n)
    for name, a in anim["nodeAnimations"].items():
        n = idx[name]
        if a["orientation"]:
            o = n["orientation"]
            q = qmul((o["x"], o["y"], o["z"], o["w"]), _sample_q(a["orientation"], t))
            n["orientation"] = qd(q)
        if a["shapeVisible"]:
            n["shape"]["visible"] = bool(_step(a["shapeVisible"], t))
        if a["shapeUvOffset"]:
            d = _step(a["shapeUvOffset"], t)
            for lay in n["shape"]["textureLayout"].values():
                lay["offset"] = {"x": lay["offset"]["x"] - d["x"], "y": lay["offset"]["y"] - d["y"]}
    return m


# ------------------------------------------------------------------------------------------------------------------ icons + sheets
def fit_props(model, rot, fill=56.0):
    q = SA._euler_yxz(*rot)
    xs, ys = [], []
    for f in SA.model_faces(model):
        for c in f["corners"]:
            v = SA._qrot(q, c)
            xs.append(v[0])
            ys.append(v[1])
    ext = max(max(xs) - min(xs), max(ys) - min(ys))
    scale = round(fill / (2.0 * ext), 3)
    return {"Scale": scale, "Rotation": list(rot), "Translation": [r6(round(-(max(xs) + min(xs)) / 2.0, 2)),
                                                                   r6(round(-(max(ys) + min(ys)) / 2.0, 2))]}


BG = (24, 24, 30)
SLOT = (44, 44, 54)


def over(dst, x, y, c):
    a = c[3] / 255.0
    b = dst.get(x, y)
    dst.put(x, y, (c[0] + b[0] * (1 - a), c[1] + b[1] * (1 - a), c[2] + b[2] * (1 - a), 255))


def blit(dst, src, ox, oy, k):
    for y in range(src.h):
        for x in range(src.w):
            c = src.get(x, y)
            if c[3]:
                for dy in range(k):
                    for dx in range(k):
                        over(dst, ox + x * k + dx, oy + y * k + dy, c)


def fill(img, x0, y0, w, h, c):
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            img.put(x, y, (c[0], c[1], c[2], 255))


def sheet(rows, gap=8):
    """rows = [(cell px, scale k, [Img])] stacked; each row its own cell size."""
    W = max(gap + len(r[2]) * (r[0] * r[1] + gap) for r in rows)
    H = gap + sum(r[0] * r[1] + gap for r in rows)
    img = SA.Img(W, H)
    fill(img, 0, 0, W, H, BG)
    y = gap
    for cell, k, ims in rows:
        x = gap
        for im in ims:
            fill(img, x, y, cell * k, cell * k, SLOT)
            blit(img, im, x, y, k)
            x += cell * k + gap
        y += cell * k + gap
    return img


# ------------------------------------------------------------------------------------------------------------------ main
def write(rel, data):
    p = os.path.join(OUT, *rel.split("/"))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as fh:
        fh.write(data)
    return p


def jbytes(obj):
    return (json.dumps(obj, indent=2) + "\n").encode("utf-8")


SACK_ICON_ROT = (16.0, 32.0, 0.0)
ACC_ICON_ROT = (12.0, 28.0, 0.0)
POSE_ROT = (48.0, 28.0, 0.0)          # previews from above, to look into the mouth
POSE_FRAMES = ((0, "closed"), (6, "opening"), (20, "open"), (20 + PORTAL_STEP * 4, "open, swirl +4 frames"))


def main():
    z = SA.assets()
    manifest = {"accessory_bag": None, "sacks": [], "animations": {}, "notes": "see README.md"}
    open_anim, loop_anim = build_open_anim(False), build_open_anim(True)
    write(ANIM_OPEN, jbytes(open_anim))
    write(ANIM_LOOP, jbytes(loop_anim))
    lift3 = lift_anim(z, "Main_Handed/Item/Idle.blockyanim", "Dual_Handed/Block/Idle.blockyanim", 30, LIFT_PLAN_3P)
    liftf = lift_anim(z, "Main_Handed/Item/Idle_FPS.blockyanim", "Dual_Handed/Block/Idle_FPS.blockyanim", 22, LIFT_PLAN_FPS)
    write(LIFT_3P, jbytes(lift3))
    write(LIFT_FPS, jbytes(liftf))
    write(ANIMSET, jbytes(animset_draft(z)))
    z.close()
    manifest["animations"] = {
        "item_open": ANIM_OPEN, "item_open_loop": ANIM_LOOP, "player_lift_3p": LIFT_3P, "player_lift_fps": LIFT_FPS,
        "player_set_draft": ANIMSET, "player_set_id": ANIMSET_ID, "lift_key": LIFT_KEY,
        "durations": {"item_open": OPEN_DUR, "player_lift_3p": 30, "player_lift_fps": 22}}

    icons, poses = [], []
    # accessory bag
    ab = build_accessory()
    am = ab.model()
    at = SA.png_encode(ab.atlas.paint())
    ap = fit_props(am, ACC_ICON_ROT)
    aicon = SA.render_icon(am, at, ap, 64)
    mp, tp, ip = ACC_DIR + "/SkyyAccessories_Bag.blockymodel", ACC_DIR + "/SkyyAccessories_Bag_Texture.png", ICON_DIR + "/SkyyAccessories_Bag.png"
    write(mp, jbytes(am))
    write(tp, at)
    write(ip, aicon)
    write("preview-AccessoryBag.png", SA.render_icon(am, at, ap, 256))
    icons.append(SA.png_decode(aicon))
    manifest["accessory_bag"] = {"item": ACC_ITEM, "model_path": mp, "texture_path": tp, "icon_path": ip, "icon_properties": ap,
                                 "texture_size": [TEX_W, ab.atlas.height()], "player_animations": "Item (unchanged)"}
    # sacks
    for spec in RARITIES:
        name, ids = spec[0], spec[1]
        sb = build_sack(spec)
        sm = sb.model()
        stx = SA.png_encode(sb.atlas.paint())
        sp = fit_props(sm, SACK_ICON_ROT)
        sicon = SA.render_icon(sm, stx, sp, 64)
        mp = "%s/SkyySacks_Bag_%s.blockymodel" % (SACK_DIR, name)
        tp = "%s/SkyySacks_Bag_%s_Texture.png" % (SACK_DIR, name)
        ip = "%s/SkyySacks_Bag_%s.png" % (ICON_DIR, name)
        write(mp, jbytes(sm))
        write(tp, stx)
        write(ip, sicon)
        icons.append(SA.png_decode(sicon))
        pp = fit_props(pose(sm, open_anim, 20), POSE_ROT, fill=52.0)
        row = [SA.render_icon(pose(sm, open_anim, t), stx, pp, 192, as_img=True) for t, _lbl in POSE_FRAMES]
        if name in ("Normal", "Legendary", "Mythic"):
            poses.append(row)
        write("preview-Sack-%s-open.png" % name, SA.png_encode(row[2]))
        item_ids = [i % c for i in ids for c in SACK_CATS] if "%s" in ids[0] else list(ids)
        manifest["sacks"].append({"rarity": name, "rarity_colour": spec[10], "items": item_ids, "model_path": mp, "texture_path": tp,
                                  "icon_path": ip, "icon_properties": sp, "texture_size": [TEX_W, sb.atlas.height()],
                                  "animation_path": ANIM_OPEN, "animation_fallback": ANIM_LOOP, "player_animations_id": ANIMSET_ID})
    rows = [(64, 2, icons)] + [(192, 1, r) for r in poses]
    write("sheet.png", SA.png_encode(sheet(rows)))
    write("manifest.json", jbytes(manifest))
    print("bags: 1 accessory bag + %d sack looks, 2 item anims, 2 player anims, 1 set draft -> %s" % (len(RARITIES), OUT))


if __name__ == "__main__":
    main()
