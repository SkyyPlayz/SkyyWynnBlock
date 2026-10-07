"""make_fists - game-ready ASSETS for the Monk fist weapons: Gauntlets + Claws (Copper..Onyxium) and Hand wraps (cloth ladder).

Approved concepts: research/cloud/weapon-art/gauntlets-v2.png, claws-v2.png, hand-wraps-v2.png (Skyy 2026-10-07: "the accessories,
weapons, and fishing stuff are all ready to make"); Monk-Kit-Spec 2. Skyy locks: claws = Wolverine-like long straight blades from the
knuckles, the black part = black LEATHER.

Route R3 (own models): every model is built here from boxes, its UVs packed into a fresh atlas and the texture painted from code. No
vanilla pixel is copied; only COLOURS are sampled from Assets.zip at run time (metal = SA.metal_gradient like the metal wands, gold
trim = the vanilla Mithril staff band, set gems = SA.gem_gradient, cloth = the vanilla cloth bolt of that cloth). The outputs are
therefore vanilla-derived and go ONLY to the git-ignored models-local/art/fists/ (PROJECT-RULES 2). This script holds no vanilla bytes.

Anchor: the HELD-weapon frame (root node "R-Attachment", isPiece), the way the vanilla claw weapons are built
(NPC/Intelligent/Slothian/Models/Weapons/Claw/Tribal.blockymodel, .../Feran/Models/Weapons/Dagger/Claw_Bone.blockymodel) and every
one-handed weapon. Measured from Characters/Player.blockymodel: R-Attachment sits at the CENTRE of the hand cube, turned +90 deg about
X, so in this frame the bare hand fills x -5..5, y -7..7, z -7..5 and the forearm x -4..4, y -6..6, z -22..-7:
  +z = towards the knuckles / finger ends (claw blades point +z), -z = wrist / forearm,
  +y = forward (thumb side), -x = back of the hand (right hand: outward), +x = palm.
The glove shells are 1 unit bigger than the bare hand, so the player's own hand stays inside them.

Run:  python tools/art/make_fists.py            (reads Assets.zip read-only, writes models-local/art/fists/)
Deterministic: no clocks, no randomness, fixed zlib -> two runs give the same bytes (checked with --check).
"""
import colorsys
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyyart as SA  # noqa: E402

OUT = os.path.join(ROOT, "models-local", "art", "fists")
METALS = ("Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium")
# wraps: the cloth in the metal column of the same level band (README weapon-art sec 2); Mithril (Prisma / Moon cloth later) and
# Onyxium (empty) are skipped on purpose
CLOTHS = (("Linen", "Copper"), ("Cotton", "Iron"), ("Silk", "Thorium"), ("Cindercloth", "Cobalt"), ("Shadoweave", "Adamantite"))
BANDS = {"Copper": "10-18", "Iron": "15-23", "Thorium": "20-28", "Cobalt": "25-38", "Adamantite": "35-43", "Mithril": "40-49",
         "Onyxium": "50+"}
GOLD_TIERS = ("Mithril", "Onyxium")          # gold rims / straps / sockets (concept v2)
STITCHED = ("Cindercloth", "Shadoweave")     # stitched wrap edges (concept)
BOLT = "Server/Item/Items/Ingredient/Bolt/Ingredient_Bolt_%s.json"
GOLD_SOURCE = "Mithril"                      # SA.band_gradient(z, "Mithril") = the vanilla Mithril staff's gold band


def hx(s):
    return tuple(int(s[i:i + 2], 16) for i in (1, 3, 5))


# black leather = the light-armor LIGHT ramp (tools/make_light_bases.py) + its stitch thread (tools/make_light_chest.py)
LEATHER = [hx(c) for c in ("#151318", "#221f27", "#2f2b35", "#3e3946", "#504a59")]
THREAD = hx("#6b6372")
SKIN_GAP = hx("#0c0b0e")

# icon view (IconProperties): fist upright, blades / knuckles up and a little right, back of the hand towards the viewer, thumb side
# turned in. The renderer is proven for this kind of view on the vanilla glove icons (README "Icons").
ICON_ROT = [-65.0, 50.0, 10.0]
# Claws: the long blades made the family fit tall and thin (blades ~2 px wide, x17-47). This view lays the blades along the icon
# diagonal (up-right), back of the hand still to the viewer: icon scale 0.523 -> 0.664 (review 2026-10-07; picked by a search over
# views that keep the blades in the screen plane).
FAMILY_ROT = {"Claws": [-40.0, 50.0, 50.0]}

# Tier tints over the vanilla colour ramps (keep the vanilla tonal ramp, move hue / saturation / brightness to the approved concept
# colours). Skyy locked the same tier colours for the light armor (docs/answered/gear.md 2026-10-07: "Mithril pale blue, Onyxium
# purple"; Cobalt blue). (hue deg, saturation, brightness multiplier); None = untouched vanilla ramp.
METAL_TINT = {"Cobalt": (218.0, 0.62, 1.12), "Mithril": (188.0, 0.38, 1.08), "Onyxium": (272.0, 0.55, 1.9)}
# Cloth: the concept shows Silk PINK and Shadoweave PURPLE (vanilla bolts: light blue / brown-grey) -> concept colours.
CLOTH_TINT = {"Silk": (335.0, 0.34, 1.0), "Shadoweave": (275.0, 0.42, 1.25)}
ICON_MARGIN = 3.0                             # px kept free round the item in the 64 x 64 icon
TEX_W = 64


# ================================================================================================ geometry
def quat(axis, deg):
    s, c = math.sin(math.radians(deg) / 2.0), math.cos(math.radians(deg) / 2.0)
    q = [0.0, 0.0, 0.0, c]
    q["xyz".index(axis)] = s
    return {"x": round(q[0], 6), "y": round(q[1], 6), "z": round(q[2], 6), "w": round(q[3], 6)}


class Builder(object):
    """Boxes given by ABSOLUTE centre in the R-Attachment frame (flat tree: every box is a child of the root)."""

    def __init__(self):
        self.nodes = []
        self.kind = {}          # node name -> material key used by the painter
        self.n = 1

    def box(self, name, size, centre, kind, rot=None):
        if name in self.kind:
            raise ValueError("duplicate node %s" % name)
        self.n += 1
        node = {"id": str(self.n), "name": name,
                "position": {"x": centre[0], "y": centre[1], "z": centre[2]},
                "orientation": quat(rot[0], rot[1]) if rot else {"x": 0, "y": 0, "z": 0, "w": 1},
                "shape": {"offset": {"x": 0, "y": 0, "z": 0}, "stretch": {"x": 1, "y": 1, "z": 1}, "textureLayout": {},
                          "type": "box", "settings": {"size": {"x": size[0], "y": size[1], "z": size[2]}},
                          "unwrapMode": "custom", "visible": True, "doubleSided": False, "shadingMode": "flat"},
                "children": []}
        self.nodes.append(node)
        self.kind[name] = kind
        return node

    def model(self):
        root = {"id": "1", "name": "R-Attachment", "position": {"x": 0, "y": 0, "z": 0},
                "orientation": {"x": 0, "y": 0, "z": 0, "w": 1},
                "shape": {"offset": {"x": 0, "y": 0, "z": 0}, "stretch": {"x": 1, "y": 1, "z": 1}, "textureLayout": {},
                          "type": "none", "settings": {"isPiece": True}, "unwrapMode": "custom", "visible": True,
                          "doubleSided": False, "shadingMode": "flat"},
                "children": self.nodes}
        return {"nodes": [root], "lod": "auto"}


FINGER_Y = (-5.6, -1.9, 1.9, 5.6)            # 4 fingers across the knuckle end (pinky -y ... index +y)
GAP_Y = (-3.75, 0.0, 3.75)                   # the 3 finger gaps (claw blades come out here)


def leather_glove(b):
    """The black leather glove (claws): fist shell, 4 knuckle rolls, thumb, wrist, cuff + strap with a buckle."""
    b.box("Handle", (12, 16, 14), (0, 0, -1), "leather")                      # fist shell (bare hand + 1)
    for i, fy in enumerate(FINGER_Y):
        b.box("Finger%d" % (i + 1), (11, 3, 2), (0, fy, 7), "leather_finger")
    b.box("Thumb", (5, 3, 8), (3, 9.5, 0), "leather")
    b.box("Wrist", (11, 15, 2), (0, 0, -9), "leather_dark")
    b.box("Cuff", (13, 17, 6), (0, 0, -13), "leather")
    b.box("Strap", (14, 18, 2), (0, 0, -12.5), "strap")
    b.box("Buckle", (1, 4, 3), (-7.5, 0, -12.5), "buckle")


def build_claws(metal):
    b = Builder()
    leather_glove(b)
    for i, gy in enumerate(GAP_Y):
        k = i + 1
        b.box("Socket%d" % k, (4, 2, 3), (-2.5, gy, 7.5), "socket")
        b.box("Blade%d" % k, (3, 1, 24), (-2.5, gy, 21), "blade")
        b.box("BladeTip%d" % k, (2, 1, 4), (-3, gy, 35), "blade")
        b.box("BladePoint%d" % k, (1, 1, 2), (-3.5, gy, 38), "blade_point")
        if metal == "Adamantite":                                            # barbed back edge
            b.box("Barb%dA" % k, (2, 1, 2), (-5, gy, 17), "blade_barb")
            b.box("Barb%dB" % k, (2, 1, 2), (-5, gy, 26), "blade_barb")
    return b


def build_gauntlets(metal):
    b = Builder()
    b.box("Handle", (12, 16, 14), (0, 0, -1), "leather")                      # leather under the plates (palm side)
    b.box("BackPlate", (2, 17, 12), (-6.5, 0, -2), "plate_lames")
    b.box("KnuckleBar", (3, 15, 3), (-6.5, 0, 4.5), "plate")
    for i, fy in enumerate(FINGER_Y):
        b.box("Finger%d" % (i + 1), (11, 3, 3), (-1, fy, 7), "plate_finger")
    b.box("SidePlate", (10, 1, 11), (-0.5, -8.5, -2), "plate_lames")          # pinky-side plate (the side the icon shows)
    b.box("Thumb", (5, 3, 8), (3, 9.5, 0), "plate_lames")
    b.box("Cuff", (14, 18, 9), (0, 0, -12.5), "plate_lames")
    b.box("CuffRim", (15, 19, 2), (0, 0, -9), "rim")
    if metal == "Thorium":                                                   # round knuckle bosses
        for i, fy in enumerate(FINGER_Y):
            b.box("Boss%d" % (i + 1), (2, 3, 3), (-8.5, fy, 4.5), "boss")
    if metal in ("Cobalt", "Adamantite"):                                     # pointed knuckle ridges / spikes
        h = 2 if metal == "Cobalt" else 3
        for i, fy in enumerate(FINGER_Y):
            z0 = 8.5
            for j, s in enumerate((3, 2, 1)):
                b.box("Spike%d_%d" % (i + 1, j + 1), (s, s, h), (-2, fy, z0 + h / 2.0), "spike")
                z0 += h
    if metal == "Adamantite":                                                # cuff side spikes
        for side, sy in (("L", 1), ("R", -1)):
            b.box("CuffSpike%s1" % side, (3, 2, 3), (0, sy * 10, -13), "spike")
            b.box("CuffSpike%s2" % side, (2, 2, 2), (0, sy * 12, -13), "spike")
            b.box("CuffSpike%s3" % side, (1, 2, 1), (0, sy * 14, -13), "spike")
    if metal in GOLD_TIERS:                                                  # set gem in a gold ring on the back plate
        b.box("GemRing", (1, 6, 6), (-8, 0, -2), "gold")
        b.box("Gem", (1, 4, 4), (-8.5, 0, -2), "gem")
    return b


def build_wraps(cloth):
    b = Builder()
    b.box("Handle", (11, 15, 11), (0, 0, -2.5), "cloth")                     # wrapped palm; the finger ends stay bare (concept)
    b.box("WristWrap", (10, 14, 8), (0, 0, -12), "cloth")
    b.box("Thumb", (5, 3, 6), (2.5, 9, -1), "cloth")
    for name, size, z, deg in (("Band1", (12, 16, 2), 1.5, 8), ("Band2", (12, 16, 2), -2.5, -8), ("Band3", (12, 16, 2), -6, 6),
                               ("Band4", (11, 15, 2), -10, -6), ("Band5", (11, 15, 2), -14, 7)):
        b.box(name, size, (0, 0, z), "cloth_band", rot=("x", deg))
    b.box("CrossA", (1, 3, 15), (-6.3, 0, -3), "cloth_strap", rot=("x", 40))
    b.box("CrossB", (1, 3, 15), (-6.4, 0, -3), "cloth_strap", rot=("x", -40))
    b.box("Tail", (1, 3, 7), (-1, -7.5, -17.5), "cloth_strap", rot=("x", 12))
    return b


# ================================================================================================ UV atlas
FACE_WH = (("front", 0, 1), ("back", 0, 1), ("left", 2, 1), ("right", 2, 1), ("top", 0, 2), ("bottom", 0, 2))


def pack(model):
    """Shelf-pack every box face (tallest first) into a TEX_W-wide atlas; sets each textureLayout. Height -> multiple of 32."""
    nodes = model["nodes"][0]["children"]
    rects = []
    for n in nodes:
        sz = n["shape"]["settings"]["size"]
        s = (sz["x"], sz["y"], sz["z"])
        for f, a, c in FACE_WH:
            rects.append((n["name"], f, int(s[a]), int(s[c])))
    order = dict((f, i) for i, (f, _a, _c) in enumerate(FACE_WH))
    rects.sort(key=lambda r: (-r[3], -r[2], r[0], order[r[1]]))
    place, x, y, row = {}, 0, 0, 0
    for name, f, w, h in rects:
        if w > TEX_W:
            raise ValueError("face %s %s wider than the atlas" % (name, f))
        if x + w > TEX_W:
            x, y, row = 0, y + row, 0
        place[(name, f)] = (x, y)
        x += w
        row = max(row, h)
    height = ((y + row + 31) // 32) * 32
    for n in nodes:
        n["shape"]["textureLayout"] = dict(
            (f, {"offset": {"x": place[(n["name"], f)][0], "y": place[(n["name"], f)][1]}, "mirror": {"x": False, "y": False},
                 "angle": 0}) for f, _a, _c in FACE_WH)
    return height


# ================================================================================================ colours + painting
def noise(x, y, seed):
    h = (x * 374761393 + y * 668265263 + seed * 2147483647) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 65535.0


def mix(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t)


def mul(c, f):
    return (c[0] * f, c[1] * f, c[2] * f)


def ramp(cols, t):
    """Piecewise-linear sample of a short colour list (t 0..1)."""
    t = min(max(t, 0.0), 1.0) * (len(cols) - 1)
    i = min(int(t), len(cols) - 2)
    return mix(cols[i], cols[i + 1], t - i)


def gsample(grad, t):
    return SA.sample(grad, min(max(t, 0.0), 1.0))[:3]


def cloth_gradient(z, cloth):
    """The cloth colour of the vanilla bolt of that cloth (Cotton_Bolt model node 'Node' minus the wooden 'base' texels)."""
    _d, model, tex, _icon = SA.item_parts(z, BOLT % cloth)
    img = SA.png_decode(tex)
    cloth_r, base_r = SA.node_rects(model, ["Node"]), SA.node_rects(model, ["base"])
    pix = []
    for y in range(img.h):
        for x in range(img.w):
            if any(r[0] <= x < r[2] and r[1] <= y < r[3] for r in cloth_r) and \
                    not any(r[0] <= x < r[2] and r[1] <= y < r[3] for r in base_r):
                c = img.get(x, y)
                if c[3] >= 128:
                    pix.append(c)
    pix.sort(key=lambda c: (SA.luma(c), c))
    pix = pix[len(pix) // 12:]                       # drop the darkest seam / shadow texels
    strip = SA.Img(len(pix), 1)
    for i, c in enumerate(pix):
        strip.put(i, 0, c)
    return SA.palette_from([strip])


def tint(grad, spec):
    """Re-hue a gradient: every step gets hue spec[0], saturation spec[1] (scaled by the step's own saturation relative to the
    gradient's mean, so the ramp keeps its shape) and its luminance times spec[2]; luminance order is kept."""
    if not spec:
        return grad
    hue, sat, bright = spec
    sats = [colorsys.rgb_to_hsv(*[v / 255.0 for v in c[:3]])[1] for c in grad]
    mean = sum(sats) / len(sats) or 1.0
    out = []
    for c, s0 in zip(grad, sats):
        L = SA.luma(c) * bright
        s = min(1.0, sat * (0.75 + 0.25 * s0 / mean))
        r, g, b = colorsys.hsv_to_rgb(hue / 360.0, s, 1.0)
        k = L / (SA.luma((r * 255, g * 255, b * 255)) or 1.0)
        rgb = [r * 255 * k, g * 255 * k, b * 255 * k]
        top = max(rgb)
        if top > 255.0:                       # too bright for this hue: desaturate towards white instead of clipping
            rgb = [L + (v - L) * (255.0 - L) / (top - L) for v in rgb] if top > L else [L] * 3
        out.append(tuple(min(255.0, max(0.0, v)) for v in rgb))
    return tuple(out)


def view_light(rot):
    """Light direction in MODEL space: from the icon's upper left, towards the viewer (so baked light reads right in the icon)."""
    rx, ry, rz = rot
    q = SA._euler_yxz(rx, ry, rz)
    qi = (-q[0], -q[1], -q[2], q[3])
    L = (-0.45, 0.75, 0.55)
    n = math.sqrt(sum(v * v for v in L))
    return SA._qrot(qi, (L[0] / n, L[1] / n, L[2] / n))


class Tex(object):
    """Paints every texel of every face through paint_texel (3D-aware: each texel knows its model-space point and normal)."""

    def __init__(self, model, height, kinds, pal, seed, rot):
        self.img = SA.Img(TEX_W, height)
        self.kinds, self.pal, self.seed = kinds, pal, seed
        self.L = view_light(rot)
        for fi, f in enumerate(SA.model_faces(model)):
            self.face(f, fi)

    def face(self, f, fi):
        w, h = int(f["wh"][0]), int(f["wh"][1])
        tl, tr, br, bl = f["corners"]
        du = [(tr[i] - tl[i]) / max(w, 1) for i in range(3)]
        dv = [(bl[i] - tl[i]) / max(h, 1) for i in range(3)]
        nrm = f["normal"]
        lit = sum(nrm[i] * self.L[i] for i in range(3))
        light = 0.80 + 0.28 * max(lit, 0.0) - 0.10 * max(-lit, 0.0)
        ox, oy = int(f["layout"]["offset"]["x"]), int(f["layout"]["offset"]["y"])
        kind = self.kinds[f["node"]]
        for v in range(h):
            for u in range(w):
                p = tuple(tl[i] + du[i] * (u + 0.5) + dv[i] * (v + 0.5) for i in range(3))
                c = self.texel(kind, f, u, v, w, h, p, fi)
                # bevel: a light rim on the edges that face the light, a dark rim on the others (blocky Hytale style)
                rim = None
                if u == 0:
                    rim = [-x for x in du]
                elif u == w - 1:
                    rim = du
                elif v == 0:
                    rim = [-x for x in dv]
                elif v == h - 1:
                    rim = dv
                k = light
                if rim is not None and w > 1 and h > 1:
                    ln = math.sqrt(sum(x * x for x in rim)) or 1.0
                    d = sum(rim[i] / ln * self.L[i] for i in range(3))
                    k *= 1.0 + (0.16 if d > 0.05 else (-0.22 if d < -0.05 else -0.05)) * self.rim_strength(kind)
                self.img.put(ox + u, oy + v, (c[0] * k, c[1] * k, c[2] * k, 255))

    @staticmethod
    def rim_strength(kind):
        return 0.5 if kind.startswith("cloth") else 1.0

    # ---------------------------------------------------------------------------------------------- materials
    def texel(self, kind, f, u, v, w, h, p, fi):
        P = self.pal
        n = noise(u + 31 * fi, v, self.seed)
        name = f["node"]
        if kind in ("leather", "leather_dark", "leather_finger"):
            base = 0.5 if kind == "leather_dark" else 0.68
            c = ramp(LEATHER, base + 0.18 * (n - 0.5) + (0.1 if noise(u // 2, v // 2, fi + 9) > 0.8 else 0.0))   # pebble grain
            if kind == "leather_finger":
                if f["face"] in ("front", "top", "bottom", "back") and (u == 0 or u == w - 1):
                    c = LEATHER[0]
                elif p[2] > 7.5 or (f["face"] == "front" and 0 < u < w - 1 and v == 0):
                    c = ramp(LEATHER, 0.9)                              # rounded knuckle catches the light
            if kind == "leather" and name == "Handle" and f["face"] == "left" and w >= 8 and h >= 8:
                # stitched seams 1 texel in from the edge + joint creases across the back
                if (u in (1, w - 2) and v % 2 == 0 and 1 <= v <= h - 2) or (v in (1, h - 2) and u % 2 == 0 and 1 <= u <= w - 2):
                    c = THREAD
            if kind == "leather" and name == "Handle" and f["face"] in ("left", "right") and abs(p[2] - 2.0) < 0.5:
                c = LEATHER[1]                                          # joint crease across the back / palm
            if noise(u, v, fi + 77) > 0.96:
                c = LEATHER[4]                                          # sheen fleck
            return c
        if kind == "strap":
            c = gsample(P["gold"], 0.45 + 0.3 * n) if P["gold_trim"] else ramp(LEATHER, 0.35 + 0.15 * n)
            if f["face"] in ("left", "right", "top", "bottom") and h >= 2 and (v == 0 or v == h - 1):
                c = mul(c, 0.7)
            return c
        if kind == "buckle" or kind == "socket" or kind == "gold" or kind == "rim":
            gold = kind == "gold" or (P["gold_trim"] and kind in ("buckle", "socket", "rim"))
            g = P["gold"] if gold else P["metal"]
            t = 0.55 + 0.25 * (1.0 - v / max(h - 1, 1)) + 0.12 * (n - 0.5)
            c = gsample(g, t)
            if kind == "buckle" and f["face"] == "left" and 0 < u < w - 1 and 0 < v < h - 1:
                c = ramp(LEATHER, 0.3)
            if kind == "rim" and noise(u // 3, v, fi) > 0.85:
                c = gsample(g, 0.95)
            return c
        if kind == "gem":
            g = P["gem"]
            # faceted: lit upper-left half, shaded lower-right, bright ridge + glint
            d = (u + 0.5) / w - (v + 0.5) / h
            c = gsample(g, 0.8 if d > 0.1 else (0.45 if d < -0.1 else 1.0))
            if u == 1 and v == 1:
                c = (255, 255, 255)
            return c
        if kind in ("blade", "blade_point", "blade_barb"):
            g = P["metal"]
            # flat sides (+-y faces = 'top'/'bottom' of a blade box): spine (-x) mid, centre ridge bright, honed edge (+x) brightest
            if f["face"] in ("top", "bottom"):
                xs = p[0]
                if kind == "blade_point" or kind == "blade_barb":
                    c = gsample(g, 0.75)
                elif xs < -3.0:
                    c = gsample(g, 0.62)
                elif xs < -2.0:
                    c = gsample(g, 0.88)
                else:
                    c = mix(gsample(g, 1.0), (255, 255, 255), 0.22)      # honed edge
                if noise(u, v, fi + 5) > 0.93:                       # scratches
                    c = mul(c, 0.86)
                if p[2] > 35.5:                                       # tip glint
                    c = mix(c, (255, 255, 255), 0.45)
                return c
            c = gsample(g, 0.95 if p[0] > -2.5 else 0.78)               # edge / spine faces
            if f["face"] in ("left", "right") and noise(u, v, fi + 3) > 0.9:
                c = mul(c, 0.88)
            return c
        if kind in ("plate", "plate_lames", "plate_finger", "spike", "boss"):
            metal = self.pal["metal"]
            t = 0.5 + 0.18 * (n - 0.5)
            if kind == "plate_lames" and f["face"] not in ("front", "back"):
                # lames: bands along z (every 3 units): lit top row, dark seam
                k = int(math.floor(p[2] + 100)) % 3
                t += 0.22 if k == 2 else (-0.22 if k == 0 else 0.0)
            if kind == "plate_finger" and f["face"] in ("left", "right", "top", "bottom"):
                if abs(p[0] - (-2.0)) < 0.5 or abs(p[0] - 2.0) < 0.5:   # finger joints
                    t -= 0.25
            if kind == "spike":
                t = 0.55 + 0.35 * (p[2] - 8.0) / 9.0 if abs(p[1]) < 9 else 0.55 + 0.3 * (abs(p[1]) - 9.0) / 6.0
            c = gsample(metal, t)
            if kind == "boss" and f["face"] == "left":
                # round boss: circle with a lit upper-left
                cu, cv = (u + 0.5) - w / 2.0, (v + 0.5) - h / 2.0
                r = math.sqrt(cu * cu + cv * cv)
                c = gsample(metal, 0.95 - 0.3 * r) if r < 1.3 else gsample(metal, 0.35)
            if P["rivets"] and kind == "plate_lames" and f["face"] in ("left", "right", "top", "bottom") and w >= 6:
                k = int(math.floor(p[2] + 100)) % 3
                if k == 1 and (u == 1 or u == w - 2):
                    c = gsample(metal, 1.0)
            if P["vplate"] and name == "BackPlate" and f["face"] == "left":
                # Cobalt V plate: a lighter V on the back of the hand
                cy = abs(p[1])
                if abs((p[2] + 6.0) - cy * 0.75) < 0.8 and cy < 7:
                    c = gsample(metal, 1.0)
            if P["gold_trim"] and name == "BackPlate" and f["face"] == "left" and (u in (0, w - 1) or v in (0, h - 1)):
                c = gsample(P["gold"], 0.7)
            if noise(u, v, fi + 13) > 0.95:
                c = mul(c, 0.85)                                       # pits
            return c
        if kind.startswith("cloth"):
            g = P["cloth"]
            # weave: alternate warp / weft texels, darker between bands
            wv = ((u + v) % 2 == 0)
            t = 0.55 + (0.08 if wv else -0.06) + 0.1 * (n - 0.5)
            if kind == "cloth":
                # wrap turns: a darker line every 3 units along z
                if int(math.floor(p[2] + 100)) % 3 == 0:
                    t -= 0.18
            if kind == "cloth_band" and f["face"] in ("left", "right", "front", "back") and (v == 0):
                t += 0.15
            if kind == "cloth_strap":
                t += 0.08
            c = gsample(g, t)
            if P["stitched"] and kind in ("cloth_band", "cloth_strap") and w >= 4 and h >= 2 and \
                    (v == h - 1 or u == 0) and (u + v) % 2 == 0:
                c = gsample(g, 0.98)
            return c
        raise ValueError("no painter for %s" % kind)


# ================================================================================================ icons + sheet
def fit_props(models, rot):
    """IconProperties for rot that fit every model of a family into 64 x 64 with ICON_MARGIN (same scale for the whole family)."""
    q = SA._euler_yxz(*rot)
    xs, ys = [], []
    for m in models:
        for f in SA.model_faces(m):
            for c in f["corners"]:
                v = SA._qrot(q, c)
                xs.append(v[0])
                ys.append(v[1])
    span = max(max(xs) - min(xs), max(ys) - min(ys))
    s = (64.0 - 2 * ICON_MARGIN) / span                   # pixels per model unit (renderer: s = 2 * Scale at size 64)
    scale = math.floor(s / 2.0 * 1000) / 1000.0
    cx, cy = (max(xs) + min(xs)) / 2.0, (max(ys) + min(ys)) / 2.0
    return {"Rotation": list(rot), "Scale": scale, "Translation": [round(-cx, 1), round(-cy, 1)]}


def upscale_onto(sheet, icon, x0, y0, k, bg):
    for y in range(icon.h):
        for x in range(icon.w):
            r, g, b, a = icon.get(x, y)
            f = 1.0 - a / 255.0
            c = (r + bg[0] * f, g + bg[1] * f, b + bg[2] * f, 255)    # icons are premultiplied
            for dy in range(k):
                for dx in range(k):
                    sheet.put(x0 + x * k + dx, y0 + y * k + dy, c)


def contact_sheet(rows, cell, k):
    """rows = [[Img or None, ...], ...]; every icon at k x on a dark slot, no labels."""
    pad, gap = 16, 8
    cols = max(len(r) for r in rows)
    W = pad * 2 + cols * cell * k + (cols - 1) * gap
    H = pad * 2 + len(rows) * cell * k + (len(rows) - 1) * gap
    bg, slot = hx("#121316"), hx("#25272e")
    sheet = SA.Img(W, H)
    for y in range(H):
        for x in range(W):
            sheet.put(x, y, bg + (255,))
    for ri, row in enumerate(rows):
        for ci, icon in enumerate(row):
            x0, y0 = pad + ci * (cell * k + gap), pad + ri * (cell * k + gap)
            if icon is None:
                continue
            upscale_onto(sheet, icon, x0, y0, k, slot)
    return SA.png_encode(sheet)


# ================================================================================================ main
def write(rel, data):
    path = os.path.join(OUT, rel.replace("/", os.sep))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if isinstance(data, str):
        data = data.encode("utf-8")
    with open(path, "wb") as fh:
        fh.write(data)
    return path


def main():
    z = SA.assets()
    gold = SA.band_gradient(z, GOLD_SOURCE)
    families = []          # (family, [(item, tier, builder, palette, label)])
    claws, gaunts, wraps = [], [], []
    for m in METALS:
        metal = tint(SA.metal_gradient(z, m), METAL_TINT.get(m))
        pal = {"metal": metal, "gold": gold, "gem": SA.gem_gradient(z, m), "gold_trim": m in GOLD_TIERS,
               "rivets": m not in ("Copper",), "vplate": m == "Cobalt"}
        gaunts.append(("Gauntlets", m, m, build_gauntlets(m), pal))
        claws.append(("Claws", m, m, build_claws(m), pal))
    for cloth, col in CLOTHS:
        pal = {"cloth": tint(cloth_gradient(z, cloth), CLOTH_TINT.get(cloth)), "stitched": cloth in STITCHED}
        wraps.append(("Wraps", cloth, col, build_wraps(cloth), pal))
    families = [gaunts, claws, wraps]

    manifest, rows, previews = [], [], []
    for fam in families:
        models = [it[3].model() for it in fam]
        heights = [pack(mdl) for mdl in models]
        rot = FAMILY_ROT.get(fam[0][0], ICON_ROT)
        props = fit_props(models, rot)
        row, prow = [], []
        for (family, tier, col, b, pal), mdl, hgt in zip(fam, models, heights):
            item = "SkyyArmory_Fist_%s_%s" % (family, tier)
            seed = sum(ord(ch) for ch in item)
            tex = SA.png_encode(Tex(mdl, hgt, b.kind, pal, seed, rot).img)
            base = "Common/Items/Weapons/Fist/SkyyArmory_%s_%s" % (family, tier)
            model_path, tex_path = base + ".blockymodel", base + "_Texture.png"
            icon_path = "Common/Icons/ItemsGenerated/%s.png" % item
            icon = SA.render_icon(mdl, tex, props, 64)
            write(model_path, json.dumps(mdl, indent=2) + "\n")
            write(tex_path, tex)
            write(icon_path, icon)
            row.append(SA.png_decode(icon))
            prow.append(SA.render_icon(mdl, tex, props, 160, as_img=True))
            notes = []
            if family == "Wraps":
                notes.append("cloth column %s (Lv %s); cloth colour = vanilla Ingredient_Bolt_%s" % (col, BANDS[col], tier))
                if tier in CLOTH_TINT:
                    notes.append("re-hued to the concept colour (hue/sat/bright %s)" % (CLOTH_TINT[tier],))
            else:
                notes.append("Lv %s; metal = SA.metal_gradient (vanilla pickaxe head + ingot, like the metal wands)" % BANDS[tier])
                if tier in METAL_TINT:
                    notes.append("ramp re-hued to the concept / locked tier colour (hue/sat/bright %s)" % (METAL_TINT[tier],))
                if tier in GOLD_TIERS:
                    notes.append("gold trim = vanilla Mithril staff band")
            notes.append("held model, root R-Attachment (isPiece); item JSON: Model/Texture/Icon as here, IconProperties %s, "
                         "Weapon.RenderDualWielded true (UNVERIFIED for fists)" % json.dumps(props, separators=(",", ":")))
            notes.append("texture %dx%d, %d boxes" % (TEX_W, hgt, len(b.nodes)))
            manifest.append({"item": item, "tier": tier, "model_path": model_path, "model_base": "own", "texture_path": tex_path,
                             "icon_path": icon_path, "icon_properties": props, "notes": "; ".join(notes)})
        rows.append(row)
        previews.append(prow)
    z.close()
    write("sheet.png", contact_sheet(rows, 64, 2))
    write("preview-sheet.png", contact_sheet(previews, 160, 1))
    write("manifest.json", json.dumps(manifest, indent=2) + "\n")
    print("make_fists: %d items -> %s" % (len(manifest), OUT))


if __name__ == "__main__":
    main()
