"""make_fishing - game-ready ASSETS for the SkyWynn fishing gear (rods, reels, hooks, lines, sinkers), 2026-10-07.

Concept (approved by Skyy 2026-10-06, docs/answered/skills.md "fishing art + spec review" + "Keep all"):
research/cloud/fishing-art/fishing-gear-sheet.png + icons/ (61 icons), research/cloud/SkyyFishing-Spec-Draft.md section 4
(rod / reel tiers T0 Bamboo .. T7 Onyxium; parts tier I-IV: 4 hooks, 4 lines, 3 sinkers + the stage-3 Ember Sinker).

(a) RODS (held model). Assets.zip has an UNUSED vanilla fishing rod (Common/Items/Tools/Fishing_Rod/FishingRod.blockymodel +
    FishingRod_Texture.png 32x128; no item JSON uses it): a bamboo blank, wooden grip, reel box + crank, the line along the rod
    with guides, a line hanging from the tip to a red / white bobber and a hook. We build on it ("vanilla first"):
      T0 Bamboo        = the vanilla rod as it is (model + texture paths of the game itself, nothing shipped but the icon)
      T1 Copper, T2 Iron = route R1: the vanilla model, a new 32x128 texture with the same UV (per-node recolour)
      T3 .. T7         = route R1+: the vanilla model read at run time, nodes renamed (vanilla repeats 'Handle' / 'Node'), plus
                         our tier ornament boxes (collars, butt cap, Cobalt fin, Adamantite crystal shards, Mithril wing, Onyxium
                         gold + gem); the texture is widened to 64x128 - the left 32 columns keep the vanilla UV (recoloured),
                         the right columns hold the ornament texels painted from code.
    Colours: blank / reel / hook / guides = the tier metal (SA.metal_gradient: vanilla pickaxe head + ingot, like the metal wands),
    EXCEPT Mithril (pale cyan) and Onyxium (purple): Skyy's concept colour lock -> the concept's own ramps (vanilla Mithril is silver,
    vanilla Onyxium near-black). Onyxium trim = the vanilla Mithril gold trim (SA.band_gradient); gems = the tier's vanilla staff
    accent (SA.gem_gradient) except Adamantite (red shards = its metal) and Onyxium (concept pink); Mithril wing = Mithril cyan;
    grip = our cork ramp (T1-T5) / the approved black leather ramp (T6-T7). Line and red / white bobber keep the vanilla texels.
    Rod icon (shipped) = the approved concept-look icon (metal ramps -> the same gradients); the SA.render_icon of the model
    WITHOUT the hanging line (Rotation [45, 90, 0], one shared Scale / Translation) is written to alt/<key>_Render.png.
(b) PARTS (reel, hook, line, sinker): icon-only items (route R2c). Source = the approved concept icons (tracked, original art,
    research/cloud/fishing-art/icons/); their hand-picked metal ramps are swapped for the same metal gradients the rods
    use (Mithril / Onyxium keep the concept ramps) (so a Cobalt reel matches the Cobalt rod); fibres, stones, wood, paper, bobber colours stay as approved.

Every output is vanilla-derived -> ONLY models-local/art/fishing/ (git-ignored). This script holds no vanilla bytes / pixels: it
reads Assets.zip (read-only) at run time. Python stdlib + tools/skyyart.py only.
Run:  python tools/art/make_fishing.py         Deterministic: two runs = same bytes (no clocks, no randomness, fixed zlib).
"""
import copy
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyyart as SA  # noqa: E402

OUT = os.path.join(ROOT, "models-local", "art", "fishing")
CONCEPT = os.path.join(ROOT, "research", "cloud", "fishing-art", "icons")
ROD_MODEL = "Common/Items/Tools/Fishing_Rod/FishingRod.blockymodel"
ROD_TEX = "Common/Items/Tools/Fishing_Rod/FishingRod_Texture.png"
ROD_DIR = "Common/Items/Tools/Fishing_Rod"
ICON_DIR = "Common/Icons/ItemsGenerated"
ICON_VIEW = [45, 90, 0]          # the vanilla spear / staff icon rotation (check_icon proven family)

TIERS = ("Bamboo", "Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium")
R1_PLAIN = ("Copper", "Iron")    # vanilla model, texture swap only
GOLD_TRIM = ("Onyxium",)          # concept: gold wraps / cap ring only on T7
LOW_COLLAR = ("Mithril", "Onyxium")
# Skyy's concept colour lock (2026-10-06): Mithril = pale blue / cyan, Onyxium = purple. Vanilla Mithril is silver and vanilla
# Onyxium near-black, so these two tiers use the concept's OWN ramps (no vanilla colour) for metal, gem and wing.
CONCEPT_LOCK = ("Mithril", "Onyxium")
PART_TIERS = ("I", "II", "III", "IV")
PART_METAL = ("Copper", "Iron", "Cobalt", "Mithril")      # concept README section 3 (hook metal / spool flanges per part tier)
HOOKS = (("barbed-hook", "Barbed"), ("lost-property-hook", "LostProperty"), ("lure-hook", "Lure"), ("monster-hook", "Monster"))
LINES = (("braided-line", "Braided"), ("steady-line", "Steady"), ("twin-line", "Twin"), ("scholars-line", "Scholars"))
SINKERS = (("weighted-sinker", "Weighted"), ("clean-sinker", "Clean"), ("deep-sinker", "Deep"))


def hx(s):
    s = s.lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


def ramp_grad(cols):
    """Own 5-colour ramp -> a gradient tuple usable with SA.sample / SA.recolor."""
    return tuple(tuple(float(v) for v in hx(c)) for c in cols)


CORK = ramp_grad(("#3a2414", "#8a6038", "#b08050", "#cfa070", "#ead0a4"))       # concept CORK ramp (own colours)
PINK = ramp_grad(("#4a0c40", "#a02c90", "#e050c8", "#ff7af0", "#ffd8fa"))       # concept GLOW_PINK gem (own colours)
LEATHER = ramp_grad(("#0a090c", "#1c191f", "#2b2730", "#3f3946", "#58515f"))    # approved light-armor black leather
# the concept's own metal ramps (research/cloud/fishing-art/make_fishing.py) -> which vanilla gradient replaces each
CONCEPT_RAMPS = {
    "Copper": ("#3b1a0c", "#8a4220", "#c26a34", "#e89558", "#ffc48e"),
    "Iron": ("#24282e", "#5c646e", "#8e97a2", "#bcc4cc", "#eef2f5"),
    "Thorium": ("#1c3324", "#3f6b4a", "#5e9468", "#8cc08e", "#cdebc6"),
    "Cobalt": ("#121b3d", "#2a3f8a", "#3f63c4", "#6f95e6", "#b9d0ff"),
    "Adamantite": ("#3a0c10", "#7a1a20", "#b42c30", "#e0574f", "#ffa192"),
    "Mithril": ("#1e3a44", "#4e8c98", "#7ec4cc", "#b4ecee", "#f2ffff"),
    "Onyxium": ("#160c22", "#3e2460", "#6b3fa0", "#a06cda", "#e4c8ff"),
    "Gold": ("#4a3208", "#9a6e18", "#d4a234", "#f0c860", "#fff0b0"),
}
RAMP_POS = (0.0, 0.3, 0.6, 0.85, 1.0)    # where the 5 ramp steps land on the vanilla gradient
OUTLINE_MUL = 0.55                          # the outline step = the darkest vanilla tone darkened (icons need a dark rim)


def h01(x, y, s=0):
    n = (x * 374761393 + y * 668265263 + s * 2147483647) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFF) / 65535.0


def write(rel, data):
    p = os.path.join(OUT, *rel.split("/"))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as f:
        f.write(data)


def premul(img):
    out = img.copy()
    for i in range(0, len(out.px), 4):
        a = out.px[i + 3]
        if a < 255:
            for k in range(3):
                out.px[i + k] = (out.px[i + k] * a + 127) // 255
    return out


# ======================================================================================================== palettes (run time)
def palettes(z):
    P = {}
    for m in SA.METALS:
        P[m] = {"metal": SA.metal_gradient(z, m), "gem": SA.gem_gradient(z, m)}
    P["Gold"] = {"metal": SA.band_gradient(z, "Mithril")}     # vanilla Mithril staff gold trim
    for m in CONCEPT_LOCK:                                      # concept colour lock (own ramps)
        P[m] = {"metal": ramp_grad(CONCEPT_RAMPS[m]), "gem": ramp_grad(CONCEPT_RAMPS[m])}
    P["Onyxium"]["gem"] = PINK                                  # concept: glowing pink gem
    P["Adamantite"]["gem"] = P["Adamantite"]["metal"]           # concept: red crystal shards (vanilla staff gem is blue)
    P["Wing"] = P["Mithril"]["metal"]                           # concept: the wing is Mithril cyan
    return P


# ======================================================================================================== (a) rods
NODE_KEYS = {   # vanilla node -> our unique name, found by (vanilla name, shape type, size) - not by order
    ("Handle", "box", (5, 24, 5)): "Grip",
    ("Handle", "box", (4, 28, 4)): "Blank1",
    ("Handle", "box", (3, 37, 3)): "Blank2",
    ("Handle", "box", (2, 56, 2)): "Blank3",
    ("Node", "quad", (8, 119, 0)): "Guides",
    ("Node", "box", (8, 2, 2)): "Crank",
    ("Node", "box", (6, 10, 10)): "Reel",
}
LINE_NODES = ("Line1", "Line2", "Line3", "Line4", "Bait", "Hook")


def rod_base(z):
    """The vanilla rod model (dict) with unique node names; raises if Assets.zip changed the rod."""
    m = json.loads(SA._read(z, ROD_MODEL).decode("utf-8-sig"))
    seen = []

    def walk(n):
        sh = n.get("shape") or {}
        sz = (sh.get("settings") or {}).get("size") or {}
        key = (n.get("name"), sh.get("type"), (int(sz.get("x", 0)), int(sz.get("y", 0)), int(sz.get("z", 0))))
        if key in NODE_KEYS:
            n["name"] = NODE_KEYS[key]
            seen.append(n["name"])
        for c in n.get("children") or []:
            walk(c)
    for n in m["nodes"]:
        walk(n)
    names = SA.node_names(m)
    missing = [v for v in NODE_KEYS.values() if v not in seen] + [v for v in LINE_NODES if v not in names]
    if missing or len(seen) != len(NODE_KEYS):
        raise SA.ArtCheckError("make_fishing: the vanilla fishing rod changed (missing %s)" % missing)
    return m


def find(nodes, name):
    for n in nodes:
        if n.get("name") == name:
            return n
        r = find(n.get("children") or [], name)
        if r:
            return r
    return None


def qaxis(ax, deg):
    s, c = math.sin(math.radians(deg) / 2.0), math.cos(math.radians(deg) / 2.0)
    return ((s, 0.0, 0.0, c), (0.0, s, 0.0, c), (0.0, 0.0, s, c))[ax]


def qprod(*qs):
    q = (0.0, 0.0, 0.0, 1.0)
    for r in qs:
        q = SA._qmul(q, r)
    return q


def r6(v):
    return round(v, 6)


def ornament_node(nid, name, kind, size, pos, q=(0.0, 0.0, 0.0, 1.0)):
    return {"id": str(nid), "name": name, "children": [],
            "position": {"x": pos[0], "y": pos[1], "z": pos[2]},
            "orientation": {"x": r6(q[0]), "y": r6(q[1]), "z": r6(q[2]), "w": r6(q[3])},
            "shape": {"type": kind, "offset": {"x": 0, "y": 0, "z": 0}, "stretch": {"x": 1, "y": 1, "z": 1},
                      "settings": {"size": dict(zip("xyz", size))} if kind == "box" else {"size": {"x": size[0], "y": size[1]}},
                      "visible": True, "doubleSided": kind == "quad", "shadingMode": "flat", "unwrapMode": "custom",
                      "textureLayout": {}}}


# Ornaments, in the Grip node's frame (grip box 5 x 24 x 5 centred on its origin; the reel sits at -z, so flair goes to +z).
# (name, kind, size, position, rotation quaternion, paint) - paint = palette key: metal / trim / gem / wing
COLLAR = (7, 2, 7)


def ornaments(tier):
    trim = "trim" if tier in GOLD_TRIM else "metal"
    o = [("ButtCap", "box", (8, 4, 8) if tier == "Thorium" else (7, 3, 7), (0, -13.5, 0), None, trim),
         ("CollarTop", "box", COLLAR, (0, 11, 0), None, trim)]
    if tier == "Thorium":
        o.append(("CollarTop2", "box", COLLAR, (0, 7.5, 0), None, "metal"))
    if tier == "Cobalt":
        o.append(("Fin", "box", (1, 9, 5), (0, 2, 5), qaxis(0, 22), "metal"))
        o.append(("FinEdge", "box", (1, 7, 1), (0, 2.5, 7.5), qaxis(0, 22), "gem"))
    if tier == "Adamantite":
        o.append(("Shard1", "box", (2, 6, 2), (0, -17.5, 0), qaxis(1, 45), "gem"))
        o.append(("Shard2", "box", (2, 5, 2), (2.5, -16.5, 0), qaxis(2, 32), "gem"))
        o.append(("Shard3", "box", (2, 5, 2), (-2.5, -16.5, 0), qaxis(2, -32), "gem"))
        o.append(("Shard4", "box", (2, 4, 2), (0, -16, 2.5), qaxis(0, -32), "gem"))
    if tier in LOW_COLLAR:
        o.append(("CollarLow", "box", COLLAR, (0, -9, 0), None, "trim"))
    if tier == "Mithril":
        o.append(("Wing", "quad", (10, 12), (0, 3, 7.5), qprod(qaxis(1, -90), qaxis(2, -15)), "wing"))
    if tier == "Onyxium":
        o.append(("Gem", "box", (3, 3, 3), (0, -17, 0), qprod(qaxis(1, 45), qaxis(0, 35.26)), "gem"))
    return o


WING_POLY = ((0, 12), (0, 5), (3, 2), (7, 0), (10, 0), (8.5, 3), (10, 3.5), (7, 6), (9, 6.5), (5, 9), (6.5, 9.5), (2, 12))


def inside(poly, x, y):
    c = False
    n = len(poly)
    for i in range(n):
        (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % n]
        if (y0 > y) != (y1 > y) and x < (x1 - x0) * (y - y0) / (y1 - y0) + x0:
            c = not c
    return c


FACE_T = {"top": 0.82, "front": 0.62, "right": 0.56, "left": 0.5, "back": 0.46, "bottom": 0.3}


def paint_face(img, rect, grad, face, seed, mask=None):
    x0, y0, w, h = rect
    base = FACE_T.get(face, 0.6)
    for v in range(h):
        for u in range(w):
            if mask is not None and not mask(u, v):
                continue
            t = base + (0.1 - 0.2 * v / max(h - 1, 1)) if h > 2 else base
            edge = w >= 3 and h >= 3 and (u in (0, w - 1) or v in (0, h - 1))
            if mask is not None:
                edge = any(not mask(u + du, v + dv) for du, dv in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                t = 0.35 + 0.55 * (1.0 - (u + v) / float(w + h)) - (0.16 if (u + 2 * v) % 4 == 0 else 0.0)
            if edge:
                t -= 0.18
            n = h01(x0 + u, y0 + v, seed)
            t += 0.06 if n > 0.92 else (-0.05 if n < 0.1 else 0.0)
            c = SA.sample(grad, t)
            img.put(x0 + u, y0 + v, (c[0], c[1], c[2], 255))


class Shelf(object):
    """Tiny deterministic shelf packer inside a texture column band (x0..x1), skipping reserved rects."""
    def __init__(self, x0, x1, h, reserved):
        self.x0, self.x1, self.h, self.res = x0, x1, h, list(reserved)
        self.x, self.y, self.row = x0, 0, 0

    def take(self, w, h):
        while True:
            if self.x + w > self.x1:
                self.x, self.y, self.row = self.x0, self.y + self.row + 1, 0
            if self.y + h > self.h:
                raise SA.ArtCheckError("make_fishing: ornament atlas full")
            r = (self.x, self.y, self.x + w, self.y + h)
            hit = [s for s in self.res if r[0] < s[2] and s[0] < r[2] and r[1] < s[3] and s[1] < r[3]]
            if not hit:
                self.x += w + 1
                self.row = max(self.row, h)
                self.res.append(r)
                return r
            self.x = max(s[2] for s in hit)


def recolor_where(img, grad, rects, keep, **kw):
    """SA.recolor limited to the texels for which keep(colour) is True (the guides on the line quad, not the white line)."""
    pts = [(x, y) for x, y, _ri in SA._region_points(img, rects) if keep(img.get(x, y))]
    rec = SA.recolor(img, grad, [(x, y, x + 1, y + 1) for x, y in pts], as_img=True, **kw)
    return rec


def rod_texture(z, P, base_model, tier, width):
    """The rod texture for a tier: vanilla UV recoloured in the left 32 columns (+ clamp-to-edge for faces that run past the
    vanilla width), widened to `width` columns."""
    van = SA.png_decode(SA._read(z, ROD_TEX))
    if tier == "Bamboo":
        return van
    metal = P[tier]["metal"]
    trim = P["Gold"]["metal"] if tier in GOLD_TRIM else metal
    R = lambda *names: SA.node_rects(base_model, list(names))   # noqa: E731
    img = van
    img = SA.recolor(img, metal, R("Blank1", "Blank2", "Blank3"), lo=0.05, hi=0.95, rank=0.5, smooth=0.3, as_img=True)
    img = SA.recolor(img, LEATHER if tier in LOW_COLLAR else CORK, R("Grip"), lo=0.05, hi=0.95, rank=0.6, as_img=True)
    img = SA.recolor(img, metal, R("Reel"), lo=0.0, hi=0.92, rank=0.6, smooth=0.2,
                     lift=SA.rim_lift(R("Reel"), 0.12, 0.0), as_img=True)
    img = SA.recolor(img, trim, R("Crank"), lo=0.3, hi=1.0, rank=0.5, as_img=True)
    img = recolor_where(img, trim, R("Guides"), lambda c: SA.luma(c) < 200, lo=0.25, hi=0.95, rank=0.6)
    img = SA.recolor(img, metal, R("Hook"), lo=0.25, hi=1.0, rank=0.5, as_img=True)
    if width == van.w:
        return img
    out = SA.Img(width, img.h)
    for y in range(img.h):
        out.px[y * width * 4:(y * width + img.w) * 4] = img.px[y * img.w * 4:(y + 1) * img.w * 4]
    # faces whose UV runs past the vanilla width sampled outside the texture; keep that look by clamping to the edge column
    for f in SA.model_faces(base_model):
        x0, y0, x1, y1 = SA.face_rect(f)
        for y in range(max(y0, 0), min(y1, img.h)):
            for x in range(max(x0, img.w), min(x1, width)):
                out.put(x, y, img.get(img.w - 1, y))
    return out


def overflow_rects(model, w):
    out = []
    for f in SA.model_faces(model):
        x0, y0, x1, y1 = SA.face_rect(f)
        if x1 > w:
            out.append((w, y0, x1 + 1, y1 + 1))
    return out


def build_rod(z, P, tier):
    """(model dict, texture Img, shipped_model: bool)."""
    base = rod_base(z)
    if tier == "Bamboo" or tier in R1_PLAIN:
        return base, rod_texture(z, P, base, tier, 32), False
    W = 64
    m = copy.deepcopy(base)
    tex = rod_texture(z, P, base, tier, W)
    grip = find(m["nodes"], "Grip")
    ids = []

    def collect(n):
        try:
            ids.append(int(n.get("id", 0)))
        except ValueError:
            pass
        for c in n.get("children") or []:
            collect(c)
    for n in m["nodes"]:
        collect(n)
    nid = max(ids) + 1
    shelf = Shelf(40, W, tex.h, overflow_rects(base, 32))
    pal = {"metal": P[tier]["metal"], "trim": P["Gold"]["metal"] if tier in GOLD_TRIM else P[tier]["metal"],
           "gem": P[tier]["gem"], "wing": P["Wing"]}
    for k, (name, kind, size, pos, q, paint) in enumerate(ornaments(tier)):
        node = ornament_node(nid, name, kind, size, pos, q or (0.0, 0.0, 0.0, 1.0))
        nid += 1
        grad = pal[paint]
        lay = node["shape"]["textureLayout"]
        if kind == "box":
            sx, sy, sz = size
            faces = (("front", sx, sy), ("back", sx, sy), ("left", sz, sy), ("right", sz, sy), ("top", sx, sz), ("bottom", sx, sz))
            for fname, fw, fh in faces:
                r = shelf.take(fw, fh)
                lay[fname] = {"offset": {"x": r[0], "y": r[1]}, "mirror": {"x": False, "y": False}, "angle": 0}
                paint_face(tex, (r[0], r[1], fw, fh), grad, fname, 11 + k)
        else:
            fw, fh = size
            r = shelf.take(fw, fh)
            lay["front"] = {"offset": {"x": r[0], "y": r[1]}, "mirror": {"x": False, "y": False}, "angle": 0}
            msk = lambda u, v: 0 <= u < fw and 0 <= v < fh and inside(WING_POLY, u + 0.5, v + 0.5)   # noqa: E731
            paint_face(tex, (r[0], r[1], fw, fh), grad, "front", 11 + k, mask=msk)
        grip["children"].append(node)
    return m, tex, True


def strip_line(model):
    m = copy.deepcopy(model)

    def walk(n):
        n["children"] = [c for c in n.get("children") or [] if c.get("name") not in LINE_NODES]
        for c in n["children"]:
            walk(c)
    for n in m["nodes"]:
        walk(n)
    return m


def fit_props(models, view, fill=58.0, focus=None, span=None):
    """IconProperties (Rotation `view`) that fit every model into `fill` of the 64-unit icon frame; focus / span = centre the
    view on one model-space point and show `span` model units (close-up previews)."""
    q = SA._euler_yxz(*view)
    if focus is not None:
        v = SA._qrot(q, focus)
        cx, cy = v[0], -v[1]
    else:
        xs, ys = [], []
        for m in models:
            for f in SA.model_faces(m):
                for c in f["corners"]:
                    v = SA._qrot(q, c)
                    xs.append(v[0])
                    ys.append(-v[1])
        span = max(max(xs) - min(xs), max(ys) - min(ys))
        cx, cy = (min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0
    return {"Scale": round(fill / (2.0 * span), 4), "Translation": [round(-cx, 2), round(cy, 2)], "Rotation": list(view)}


def icon_props(models):
    """One shared IconProperties (Rotation ICON_VIEW) that fits every rod (without its hanging line) into the 64 px icon."""
    return fit_props(models, ICON_VIEW)


# ======================================================================================================== (b) concept icons
def colour_map(P):
    """concept ramp colour -> vanilla-gradient colour, for every metal ramp of the concept."""
    cmap = {}
    for name, cols in sorted(CONCEPT_RAMPS.items()):
        if name in CONCEPT_LOCK:      # locked tiers keep the concept colours as drawn
            for c in cols:
                cmap[hx(c)] = tuple(float(v) for v in hx(c))
            continue
        g = P[name]["metal"]
        for i, c in enumerate(cols):
            nc = SA.sample(g, RAMP_POS[i])
            if i == 0:
                nc = tuple(v * OUTLINE_MUL for v in nc)
            key = hx(c)
            if key in cmap:
                raise SA.ArtCheckError("make_fishing: concept ramps share colour %s" % c)
            cmap[key] = nc
    return cmap


def concept_icon(cmap, fname):
    src = SA.png_decode(open(os.path.join(CONCEPT, fname), "rb").read())
    if (src.w, src.h) != (64, 64):
        raise SA.ArtCheckError("make_fishing: concept icon %s is not 64x64" % fname)
    out = src.copy()
    for y in range(64):
        for x in range(64):
            r, g, b, a = src.get(x, y)
            if a and (r, g, b) in cmap:
                c = cmap[(r, g, b)]
                out.put(x, y, (c[0], c[1], c[2], a))
    return premul(out)


# ======================================================================================================== sheet + previews
SLOT = (38, 44, 54)
BACK = (18, 22, 28)


def sheet(rows, scale=2, gap=10):
    """Labels-free grid: every icon at `scale` on a dark slot. rows = list of lists of premultiplied 64x64 Img (None = empty)."""
    cell = 64 * scale + 8
    cols = max(len(r) for r in rows)
    W, H = gap + cols * (cell + gap), gap + len(rows) * (cell + gap)
    img = SA.Img(W, H)
    for i in range(0, len(img.px), 4):
        img.px[i:i + 4] = bytes(BACK + (255,))
    for ri, row in enumerate(rows):
        for ci, ic in enumerate(row):
            if ic is None:
                continue
            ox, oy = gap + ci * (cell + gap), gap + ri * (cell + gap)
            for y in range(cell):
                for x in range(cell):
                    img.put(ox + x, oy + y, SLOT + (255,))
            for y in range(64 * scale):
                for x in range(64 * scale):
                    r, g, b, a = ic.get(x // scale, y // scale)
                    if a:
                        k = 1.0 - a / 255.0
                        img.put(ox + 4 + x, oy + 4 + y, (r + SLOT[0] * k, g + SLOT[1] * k, b + SLOT[2] * k, 255))
    return img


def strip_imgs(imgs, bg=BACK):
    w = sum(i.w for i in imgs)
    h = max(i.h for i in imgs)
    out = SA.Img(w, h)
    x0 = 0
    for im in imgs:
        for y in range(h):
            for x in range(im.w):
                c = im.get(x, y) if y < im.h else (0, 0, 0, 0)
                k = 1.0 - c[3] / 255.0
                out.put(x0 + x, y, (c[0] + bg[0] * k, c[1] + bg[1] * k, c[2] + bg[2] * k, 255))
        x0 += im.w
    return out


# ======================================================================================================== main
def main():
    z = SA.assets()
    P = palettes(z)
    manifest = []
    cmap = colour_map(P)
    # ---- rods
    built = [(t,) + build_rod(z, P, t) for t in TIERS]
    props = icon_props([strip_line(m) for _t, m, _x, _s in built])
    rod_icons, rod_alt, previews = [], [], []
    for ti, (tier, model, tex, shipped) in enumerate(built):
        key = "SkyyFishing_Rod_%s" % tier
        icon = concept_icon(cmap, "rod-t%d-%s.png" % (ti, tier.lower()))      # shipped: the approved concept look
        rod_icons.append(icon)
        write("%s/%s.png" % (ICON_DIR, key), SA.png_encode(icon))
        alt = SA.render_icon(strip_line(model), tex, props, 64, as_img=True)   # alt: the 3D model render
        rod_alt.append(alt)
        write("alt/%s_Render.png" % key, SA.png_encode(alt))
        previews.append(SA.render_icon(strip_line(model), tex, props, 256, as_img=True))
        if tier == "Bamboo":
            mp, tp, base, route = ROD_MODEL, ROD_TEX, ROD_MODEL, "vanilla rod as is (no model / texture shipped)"
        elif not shipped:
            mp, base = ROD_MODEL, ROD_MODEL
            tp = "%s/%s_Texture.png" % (ROD_DIR, key)
            write(tp, SA.png_encode(tex))
            route = "R1: vanilla model, new 32x128 texture (same UV)"
        else:
            mp = "%s/%s.blockymodel" % (ROD_DIR, key)
            tp = "%s/%s_Texture.png" % (ROD_DIR, key)
            write(mp, (json.dumps(model, indent=2) + "\n").encode("utf-8"))
            write(tp, SA.png_encode(tex))
            base = ROD_MODEL
            route = "R1+: vanilla model (nodes renamed) + tier ornaments %s, texture widened to 64x128" % (
                "/".join(o[0] for o in ornaments(tier)))
        manifest.append({"item": key, "tier": "T%d %s" % (ti, tier), "model_path": mp, "model_base": base,
                         "texture_path": tp, "icon_path": "%s/%s.png" % (ICON_DIR, key),
                         "notes": "%s. Icon = the approved concept look (concept ramps -> vanilla metal gradients, Mithril / Onyxium concept-locked). Model render (no hanging line, IconProperties %s): alt/%s_Render.png"
                                  % (route, json.dumps(props, sort_keys=True), key)})
    # ---- reels
    reel_icons = []
    for ti, tier in enumerate(TIERS):
        key = "SkyyFishing_Reel_%s" % tier
        ic = concept_icon(cmap, "reel-t%d-%s.png" % (ti, tier.lower()))
        reel_icons.append(ic)
        write("%s/%s.png" % (ICON_DIR, key), SA.png_encode(ic))
        manifest.append({"item": key, "tier": "T%d %s" % (ti, tier), "model_path": None, "model_base": "own",
                         "texture_path": None, "icon_path": "%s/%s.png" % (ICON_DIR, key),
                         "notes": "R2c icon-only: approved concept icon, metal ramps -> %s" % (
                             "(none: bamboo / wood)" if tier == "Bamboo" else
                             ("the concept %s ramp (colour lock)" % tier if tier in CONCEPT_LOCK else "vanilla %s gradient" % tier))})
    # ---- parts
    part_rows = []
    for group, kind in ((HOOKS, "Hook"), (LINES, "Line"), (SINKERS, "Sinker")):
        for slug, name in group:
            row = []
            for pi, pt in enumerate(PART_TIERS):
                key = "SkyyFishing_%s_%s_%s" % (kind, name, pt)
                ic = concept_icon(cmap, "%s-%s.png" % (slug, pt))
                row.append(ic)
                write("%s/%s.png" % (ICON_DIR, key), SA.png_encode(ic))
                manifest.append({"item": key, "tier": "part %s" % pt, "model_path": None, "model_base": "own",
                                 "texture_path": None, "icon_path": "%s/%s.png" % (ICON_DIR, key),
                                 "notes": "R2c icon-only: approved concept icon; metal ramps -> %s"
                                          % ("the concept Mithril ramp (colour lock)" if PART_METAL[pi] in CONCEPT_LOCK
                                             else "vanilla %s gradient" % PART_METAL[pi])})
            part_rows.append(row)
    key = "SkyyFishing_Sinker_Ember"
    ember = concept_icon(cmap, "ember-sinker-IV.png")
    write("%s/%s.png" % (ICON_DIR, key), SA.png_encode(ember))
    manifest.append({"item": key, "tier": "stage 3 (one item)", "model_path": None, "model_base": "own", "texture_path": None,
                     "icon_path": "%s/%s.png" % (ICON_DIR, key),
                     "notes": "R2c icon-only: approved concept icon; gold ring -> vanilla Mithril gold trim gradient"})
    part_rows[-1].append(ember)
    # ---- sheet (rows: rods (shipped concept look), rods 3D render alt, reels, then hooks / lines / sinkers two variants per row)
    rows = [rod_icons, rod_alt, reel_icons]
    for i in range(0, len(part_rows), 2):
        rows.append(part_rows[i] + (part_rows[i + 1] if i + 1 < len(part_rows) else []))
    write("sheet.png", SA.png_encode(sheet(rows)))
    write("preview/rods-3d.png", SA.png_encode(strip_imgs(previews)))
    wprops = fit_props([m for _t, m, _x, _s in built], [0, 90, -45], fill=60.0)
    full = [SA.render_icon(m, tx, wprops, 192, as_img=True) for _t, m, tx, _s in built]
    grip = (-3.0, 4.0, -3.0)    # R-Attachment (-3, 14, -6) + Grip (0, -6, 3) - 4 down: the butt / reel end
    close = [SA.render_icon(strip_line(m), tx, fit_props(None, [20, 60, 0], 60.0, grip, 44.0), 192, as_img=True)
             for _t, m, tx, _s in built]
    write("preview/rods-butt-closeup.png", SA.png_encode(strip_imgs(close)))
    write("preview/rods-with-line.png", SA.png_encode(strip_imgs(full)))
    write("manifest.json", (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    print("make_fishing: %d items, icon props %s -> %s" % (len(manifest), json.dumps(props), OUT))


if __name__ == "__main__":
    main()
