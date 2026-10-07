"""make_staffs - game-ready ASSETS for the SkyWynn metal staffs + Bo staffs (Copper .. Onyxium), 2026-10-07.

Concepts (approved by Skyy 2026-10-07): research/cloud/weapon-art/staff-v2.png and bo-staff-v2.png (README rows "Staff", "Bo staff"),
research/cloud/Monk-Kit-Spec.md 1 (Bo: wood shaft + black leather centre grip + metal caps that grow per tier).

(a) Metal staffs, route R1 (vanilla re-texture, the metal wand recipe of tools/skyyart.py applied to each tier's OWN vanilla staff):
    keep Items/Weapons/Staff/<Metal>.blockymodel + its IconProperties, ship a new texture of the same size / UV:
      shaft nodes -> wood (gradient of the vanilla Wood Bo staff texture), a black leather hand grip painted onto the shaft texels that
      sit 30-42 % up from the butt (found from the model geometry), metal nodes -> the tier metal (SA.metal_gradient: vanilla
      pickaxe head + ingot), gem nodes -> the tier crystal (SA.gem_gradient: the tier's vanilla staff accent = the wand leaf colour),
      Mithril trim -> gold (SA.band_gradient: the vanilla Mithril staff band).
    Review fix 2026-10-07: Onyxium metal tinted purple + Mithril pale blue (CONCEPT_TINT, the concept ramps), Adamantite crystal ember
    orange + Mithril crystal clear white-aqua (CRYSTAL_TINT, the concept CRYSTAL ramps); the Bo caps / studs use the same colours.
(b) Bo staffs, own model: the vanilla Bo_Wood rig nodes (R-Attachment / Origin_Projectile / Origin_Item / Handle orientation, read
    from Assets.zip at run time so it is held exactly like the vanilla Bo) + our own boxes along the Handle axis (same 148-unit length,
    6-unit shaft): wood shaft, thicker black leather centre grip, metal caps growing 8 -> 20 units per tier, 1 -> 3 bands per end,
    Iron rivets, Cobalt pointed tips, Adamantite cap spikes, gold bands on Mithril + Onyxium, a crystal stud on the grip from Adamantite.
    Texture packed + painted from code; the wood colours are a gradient sampled from the vanilla Bo_Wood texture at run time.

Every output is vanilla-derived -> ONLY models-local/art/staffs/ (git-ignored). This script holds no vanilla bytes / pixels.
Run:  python tools/art/make_staffs.py         Deterministic: two runs = same bytes (no clocks, no randomness, fixed zlib).
"""
import copy
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyyart as SA  # noqa: E402

OUT = os.path.join(ROOT, "models-local", "art", "staffs")
METALS = SA.METALS
STAFF_ITEM = "Server/Item/Items/Weapon/Staff/Weapon_Staff_%s.json"
BO_ITEM = "Server/Item/Items/Weapon/Staff/Weapon_Staff_Bo_Wood.json"
TEX_DIR = "Common/Items/Weapons/Staff"
ICON_DIR = "Common/Icons/ItemsGenerated"


def hx(s):
    s = s.lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), 255)


# black leather = the approved light-armor leather ramp (research/cloud/light-armor/make_sheets.py, own colours, not vanilla)
LEATHER = [hx(c) for c in ("#0a090c", "#1c191f", "#2b2730", "#3f3946", "#58515f")]
THREAD = hx("#6b6372")

# ======================================================================================================== (a) metal staffs (R1)
# parts per tier = node names of the vanilla <Metal>.blockymodel (or explicit texel rects). Order of painting: shaft (wood) ->
# grip (leather, a slice of the shaft) -> metal -> band (gold) -> gem; where two parts share texels the later one wins.
STAFF_PARTS = {
    "Copper": {"shaft": ["Handle", "Handle2", "Twig"], "metal": ["CopperHead*", "Pommel", "Rope"], "gem": ["Ribbon"]},
    "Iron": {"shaft": ["Handle"], "metal": ["Pommel", "Handle2", "Base", "Claw*", "ClawBig*"],
             "gem": [(6, 82, 20, 96), (20, 82, 26, 96)]},          # the glowing inner face of the claw socket
    "Thorium": {"shaft": ["Handle"], "metal": ["HandleDecoration*", "HandleOrb", "Pommel"], "gem": ["Staffhead*"]},
    "Cobalt": {"shaft": ["Handle"], "metal": ["Top", "Node", "Blade", "Pommel"], "gem": ["Knob"]},
    "Adamantite": {"shaft": ["Handle"], "metal": ["Knob", "Node", "Top", "Spike", "Middle", "Blade"], "gem": ["Gem"]},
    "Mithril": {"shaft": ["Handle"], "metal": ["Wing*"], "band": ["Pommel", "Pommel2", "Pommel-Spike", "Band", "Blade"],
                "gem": ["Gem", "Diamond"]},
    "Onyxium": {"shaft": ["Handle"], "metal": ["Band", "Band2", "Moon", "Handle2", "Diamond", "Blade", "Node", "Pommel", "Spike"],
                "gem": ["Gem"]},
}
GRIP_SPAN = (0.30, 0.42)       # the leather grip: share of the staff length measured from the butt (staff-v2.png)
TUNE = {
    "shaft": {"lo": 0.05, "hi": 0.95, "rank": 0.5, "smooth": 0.3},
    "metal": {"lo": 0.05, "hi": 1.0, "rank": 0.5, "smooth": 0.5, "rim": (0.10, -0.03)},
    "band": {"lo": 0.1, "hi": 0.9, "rank": 0.5, "smooth": 0.3, "rim": (0.08, 0.0)},
    "gem": {"lo": 0.15, "hi": 1.0, "rank": 0.5},
}
METAL_TUNE = {"Onyxium": {"metal": {"lo": 0.12}}}
# concept tint (research/cloud/weapon-art/README.md 3 = the light-armor ramps, own colours): the vanilla Onyxium metal reads navy-black
# and vanilla Mithril grey-white in game light, but the concept + gear.md (2026-10-07) lock Onyxium = purple, Mithril = pale blue.
# metal = vanilla pickaxe/ingot gradient blended towards this ramp by the given share (other tiers: vanilla only, share 0).
CONCEPT_TINT = {
    "Mithril": (("#1e3a44", "#4e8c98", "#7ec4cc", "#b4ecee", "#f2ffff"), 0.6),
    "Onyxium": (("#160c22", "#3e2460", "#6b3fa0", "#a06cda", "#e4c8ff"), 0.85),
}


# crystal override = the concept CRYSTAL ramp (research/cloud/weapon-art/make_weapons_v2.py, own colours) where the vanilla staff gem
# reads off-concept: Adamantite vanilla gem is light blue (concept: ember orange), Mithril pink (concept: clear white-aqua crystal).
CRYSTAL_TINT = {
    "Adamantite": ("#3e0c06", "#8a2410", "#d4461c", "#ff8a46", "#ffe0b0"),
    "Mithril": ("#1c3a40", "#5aa0aa", "#a8e4e4", "#e0fbf8", "#ffffff"),
}


def staff_gem(z, metal):
    """The crystal gradient: the tier's vanilla staff gem (SA.gem_gradient), or the concept ramp where CRYSTAL_TINT says."""
    if metal in CRYSTAL_TINT:
        return grad_of([hx(c) for c in CRYSTAL_TINT[metal]])
    return SA.gem_gradient(z, metal)


def tint_note(metal):
    out = ""
    if metal in CONCEPT_TINT:
        out += " Metal tinted %d%% towards the concept %s ramp." % (round(CONCEPT_TINT[metal][1] * 100), metal)
    if metal in CRYSTAL_TINT:
        out += " Crystal = the concept %s CRYSTAL ramp (not the vanilla gem)." % metal
    return out


def staff_metal(z, metal):
    """The tier metal gradient for staffs + Bo caps: SA.metal_gradient, tinted towards the concept ramp where CONCEPT_TINT says."""
    g = SA.metal_gradient(z, metal)
    if metal in CONCEPT_TINT:
        ramp_hex, share = CONCEPT_TINT[metal]
        g = SA.grad_mix(g, grad_of([hx(c) for c in ramp_hex]), share)
    return g


def rects_of(model, names):
    out = []
    for n in names:
        if isinstance(n, tuple):
            out.append(n)
        else:
            for r in SA.node_rects(model, [n]):
                if r not in out:
                    out.append(r)
    return out


def texel_uses(model, names):
    """{texel (x, y): [model-space points of every face spot that samples it]} for the named nodes."""
    ok = SA._name_match(names)
    uses = {}
    for f in SA.model_faces(model):
        if not ok(f["node"]):
            continue
        w, h = f["wh"]
        tl, tr, br, bl = f["corners"]
        for v in range(int(round(h))):
            for u in range(int(round(w))):
                a, b = (u + 0.5) / w, (v + 0.5) / h
                p = tuple(tl[k] + (tr[k] - tl[k]) * a + (bl[k] - tl[k]) * b for k in range(3))
                tu, tv = SA.uv_point(f["layout"], u + 0.5, v + 0.5)
                uses.setdefault((int(math.floor(tu)), int(math.floor(tv))), []).append(p)
    return uses


def staff_axis(model, shaft, gem):
    """(origin, unit axis, length): the butt -> head line of the staff (shaft long direction, pointing at the gem side)."""
    pts = [c for f in SA.model_faces(model) for c in f["corners"]]
    sp = [c for f in SA.model_faces(model) if SA._name_match(shaft)(f["node"]) for c in f["corners"]]
    best, pair = -1.0, None
    for i in range(len(sp)):
        for j in range(i + 1, len(sp)):
            d = sum((sp[i][k] - sp[j][k]) ** 2 for k in range(3))
            if d > best:
                best, pair = d, (sp[i], sp[j])
    ax = [pair[1][k] - pair[0][k] for k in range(3)]
    n = math.sqrt(sum(a * a for a in ax))
    ax = [a / n for a in ax]
    gp = [c for f in SA.model_faces(model) if SA._name_match([g for g in gem if not isinstance(g, tuple)] or ["\0"])(f["node"])
          for c in f["corners"]]
    proj = [sum(p[k] * ax[k] for k in range(3)) for p in pts]
    lo, hi = min(proj), max(proj)
    if gp:
        gmid = sum(sum(p[k] * ax[k] for k in range(3)) for p in gp) / len(gp)
        if gmid < (lo + hi) / 2.0:
            ax = [-a for a in ax]
            lo, hi = -hi, -lo
    return ax, lo, hi - lo


def grip_texels(model, parts):
    """{(x, y): distance in model units from the grip's lower end} of the shaft texels whose every use lies inside GRIP_SPAN."""
    ax, lo, length = staff_axis(model, parts["shaft"], parts["gem"])
    out = {}
    for (x, y), ps in texel_uses(model, parts["shaft"]).items():
        ts = [(sum(p[k] * ax[k] for k in range(3)) - lo) / length for p in ps]
        if all(GRIP_SPAN[0] <= t <= GRIP_SPAN[1] for t in ts):
            out[(x, y)] = sum(ts) / len(ts) * length - GRIP_SPAN[0] * length
    return out, (GRIP_SPAN[1] - GRIP_SPAN[0]) * length


def paint_grip(img, texels, span):
    """Black leather wrap painted over the grip texels: 3-unit wraps with a dark seam + a light edge, dark rims at both ends."""
    for (x, y), a in sorted(texels.items()):
        if a < 1.0 or a > span - 1.0:
            c = LEATHER[0]
        else:
            ph = a % 3.0
            n = noise(x, y, 5) * 0.35
            c = LEATHER[1] if ph < 0.75 else (mix(LEATHER[3], LEATHER[4], 0.4) if ph < 1.5 else mix(LEATHER[2], LEATHER[3], n))
        img.put(x, y, (c[0], c[1], c[2], img.get(x, y)[3]))


def grad_of(colours):
    """A dark -> light gradient from a short own colour list (for recolor)."""
    strip = SA.Img(len(colours), 1)
    for i, c in enumerate(colours):
        strip.put(i, 0, c)
    return SA.palette_from([strip], steps=24, min_alpha=1)


def wood_gradient(z):
    _d, _m, tex, _i = SA.item_parts(z, BO_ITEM)
    return SA.palette_from([tex])


def staff_texture(z, metal):
    d, model, tex, _icon = SA.item_parts(z, STAFF_ITEM % metal)
    parts = STAFF_PARTS[metal]
    grads = {"shaft": wood_gradient(z), "grip": grad_of(LEATHER), "metal": staff_metal(z, metal),
             "band": SA.band_gradient(z, metal), "gem": staff_gem(z, metal)}
    img = SA.png_decode(tex)
    regions = {k: rects_of(model, v) for k, v in parts.items()}
    grip, span = grip_texels(model, parts)
    for part in ("shaft", "grip", "metal", "band", "gem"):
        if part == "grip":
            paint_grip(img, grip, span)
            continue
        if not regions.get(part):
            continue
        p = dict(TUNE[part])
        p.update(METAL_TUNE.get(metal, {}).get(part, {}))
        rim = p.pop("rim", None)
        if rim:
            p["lift"] = SA.rim_lift(regions[part], rim[0], rim[1])
        img = SA.recolor(img, grads[part], regions[part], as_img=True, **p)
    if (img.w % 32) or (img.h % 32):
        raise SystemExit("texture size %dx%d is not a multiple of 32" % (img.w, img.h))
    tex_out = SA.png_encode(img)
    return d, model, tex_out, len(grip)


# ======================================================================================================== (b) Bo staffs (own model)
HALF = 74          # half the vanilla Bo length (148 units along the Handle x axis)
CENTRE = 18        # where the vanilla Bo shaft is centred on the Handle x axis (Handle shape offset; children hang off it)
BO = {             # per tier: cap length, bands per end, extras
    "Copper": {"cap": 10, "bands": 1},
    "Iron": {"cap": 12, "bands": 1, "rivets": True},
    "Thorium": {"cap": 14, "bands": 2, "rivets": True},
    "Cobalt": {"cap": 16, "bands": 2, "rivets": True, "point": True},
    "Adamantite": {"cap": 18, "bands": 2, "rivets": True, "spikes": True, "stud": True},
    "Mithril": {"cap": 20, "bands": 3, "rivets": True, "gold": True, "stud": True},
    "Onyxium": {"cap": 22, "bands": 3, "rivets": True, "gold": True, "stud": True, "point": True},
}
TEX_W = 64


def box(name, size, pos, children=None, rot=None):
    q = rot or (0.0, 0.0, 0.0, 1.0)
    return {"id": name, "name": name,
            "position": {"x": pos[0], "y": pos[1], "z": pos[2]},
            "orientation": {"x": q[0], "y": q[1], "z": q[2], "w": q[3]},
            "shape": {"offset": {"x": 0, "y": 0, "z": 0}, "stretch": {"x": 1, "y": 1, "z": 1}, "textureLayout": {},
                      "type": "box", "settings": {"size": {"x": size[0], "y": size[1], "z": size[2]}},
                      "unwrapMode": "custom", "visible": True, "doubleSided": False, "shadingMode": "flat"},
            "children": children or []}


def find(nodes, name):
    for n in nodes:
        if n.get("name") == name:
            return n
        r = find(n.get("children") or [], name)
        if r:
            return r
    return None


def bo_model(vanilla, metal):
    """The Bo rig of the vanilla Bo_Wood (kept: attachment, projectile + item origins, Handle orientation = held the same way) with our
    boxes as children of Handle. Handle frame: x = along the staff (-74 .. 74), the Handle's own box becomes the centre grip."""
    t = BO[metal]
    m = copy.deepcopy(vanilla)
    h = find(m["nodes"], "Handle")
    cap, nb, grip = t["cap"], t["bands"], 14
    sh = h["shape"]
    sh["offset"] = {"x": CENTRE, "y": 0, "z": 0}       # vanilla: the shaft centre sits 18 units along Handle x
    sh["stretch"] = {"x": 1, "y": 1, "z": 1}
    sh["settings"] = {"size": {"x": 2 * grip, "y": 7, "z": 7}}          # the leather centre grip (thicker than the shaft)
    sh["textureLayout"] = {}
    kids = []
    wood_len = HALF - cap - grip
    for s, tag in ((1, "Hi"), (-1, "Lo")):
        kids.append(box("Shaft" + tag, (wood_len, 6, 6), (s * (grip + wood_len / 2.0), 0, 0)))
        kids.append(box("Cap" + tag, (cap, 8, 8), (s * (HALF - cap / 2.0), 0, 0)))
        kids.append(box("CapEnd" + tag, (1, 6, 6), (s * (HALF + 0.5), 0, 0)))
        for i in range(nb):
            kids.append(box("Band%d%s" % (i + 1, tag), (2, 8.6, 8.6), (s * (HALF - cap - 1.5 - 3.5 * i), 0, 0)))
        if t.get("point"):
            kids.append(box("Point" + tag, (3, 3, 3), (s * (HALF + 2.5), 0, 0)))
        if t.get("spikes"):
            for k, (dy, dz) in enumerate(((1, 0), (-1, 0), (0, 1), (0, -1))):
                kids.append(box("Spike%d%s" % (k + 1, tag), (2, 2, 2), (s * (HALF - cap / 2.0), dy * 5, dz * 5)))
        kids.append(box("GripRim" + tag, (1, 7.6, 7.6), (s * (grip + 0.5), 0, 0)))
    if t.get("stud"):
        kids.append(box("Stud", (3, 3, 1), (0, 0, 3.6)))
        kids.append(box("Stud2", (3, 3, 1), (0, 0, -3.6)))
    h["children"] = kids
    return m


FACE_WH = {"front": ("x", "y"), "back": ("x", "y"), "left": ("z", "y"), "right": ("z", "y"), "top": ("x", "z"), "bottom": ("x", "z")}


def all_boxes(nodes, out):
    for n in nodes:
        if (n.get("shape") or {}).get("type") == "box":
            out.append(n)
        all_boxes(n.get("children") or [], out)
    return out


def pack(model):
    """Shelf-pack every box face (long faces first). Faces longer than the atlas width are laid with angle 90 (along v).
    Returns {(node, face): (x, y, w, h, rotated)} and the atlas height (multiple of 32)."""
    rects = []
    for n in all_boxes(model["nodes"], []):
        size = n["shape"]["settings"]["size"]
        for f, (a, b) in FACE_WH.items():
            w, h = int(math.ceil(size[a])), int(math.ceil(size[b]))
            rot = w > TEX_W
            rects.append((n["name"], f, h if rot else w, w if rot else h, rot))
    rects.sort(key=lambda r: (-r[3], -r[2], r[0], r[1]))
    place, x, y, row = {}, 0, 0, 0
    for name, f, w, h, rot in rects:
        if x + w > TEX_W:
            x, y, row = 0, y + row, 0
        place[(name, f)] = (x, y, w, h, rot)
        x += w
        row = max(row, h)
    height = ((y + row + 31) // 32) * 32
    for n in all_boxes(model["nodes"], []):
        lay = {}
        for f in FACE_WH:
            px, py, w, h, rot = place[(n["name"], f)]
            if rot:      # angle 90: face (u, v) -> texel offset + (-v, u); offset at the right edge of the rect
                lay[f] = {"offset": {"x": px + w, "y": py}, "mirror": {"x": False, "y": False}, "angle": 90}
            else:
                lay[f] = {"offset": {"x": px, "y": py}, "mirror": {"x": False, "y": False}, "angle": 0}
        n["shape"]["textureLayout"] = lay
    return place, height


def noise(x, y, seed):
    h = (x * 374761393 + y * 668265263 + seed * 2147483647) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 65535.0


def mix(a, b, t):
    return tuple(a[k] + (b[k] - a[k]) * t for k in range(3)) + (255,)


def ramp(grad, n=5, lo=0.0, hi=1.0):
    return [SA.sample(grad, lo + (hi - lo) * i / (n - 1.0)) for i in range(n)]


class Face(object):
    """Paint a face in FACE coordinates: u along the box's first size axis (the staff length on side faces), v across."""

    def __init__(self, img, rect, seed, model_layout, wh):
        self.img, self.seed, self.lay = img, seed, model_layout
        self.w, self.h = wh

    def put(self, u, v, c):
        if 0 <= u < self.w and 0 <= v < self.h:
            tu, tv = SA.uv_point(self.lay, u + 0.5, v + 0.5)
            self.img.put(int(math.floor(tu)), int(math.floor(tv)), (c[0], c[1], c[2], 255))

    def n(self, u, v):
        return noise(u, v, self.seed)


def paint_wood(f, W, along):
    """Plain grained wood in the vanilla Bo wood colours (W = 5-step ramp): long streaks down the staff, lit edge, shaded edge."""
    L = f.w if along == "u" else f.h
    C = f.h if along == "u" else f.w
    for a in range(L):
        for c in range(C):
            streak = noise(c, (a + f.seed) // 7, f.seed) * 0.5 + noise(c, (a + f.seed + 3) // 3, f.seed + 1) * 0.25
            t = 0.25 + 0.5 * streak
            if c == 0 and C > 2:
                t += 0.2
            elif c == C - 1 and C > 2:
                t -= 0.2
            if noise(a, c, f.seed + 9) > 0.97:
                t -= 0.25                              # small knots / pores
            t = min(max(t, 0.0), 1.0) * 3.999
            i = int(t)
            col = mix(W[i], W[i + 1], t - i)
            f.put(a if along == "u" else c, c if along == "u" else a, col)


def paint_metal(f, M, along, seed_rivets=False, engrave=False):
    """Metal: light top edge, dark bottom edge, brushed along the staff, a few pits, optional engraved line + rivets."""
    L = f.w if along == "u" else f.h
    C = f.h if along == "u" else f.w
    for a in range(L):
        for c in range(C):
            t = c / max(1.0, C - 1.0)
            base = mix(M[3], M[1], t)
            col = mix(base, M[2], 0.2 + 0.3 * noise(a // 2, c, f.seed))
            if noise(a, c, f.seed + 11) > 0.95:
                col = M[1]
            if C > 2 and c == 0:
                col = M[4]
            elif C > 2 and c == C - 1:
                col = M[0]
            if L > 6 and a in (0, L - 1):
                col = M[1] if c else M[3]
            if engrave and L > 7 and a == L // 2 and 0 < c < C - 1:
                col = M[0]
            f.put(a if along == "u" else c, c if along == "u" else a, col)
    if seed_rivets and L > 7 and C >= 5:
        for a in (2, L - 3):
            cc = C // 2
            for (da, dc, k) in ((0, 0, 4), (1, 0, 3), (0, 1, 2), (1, 1, 0)):
                aa, c2 = a + da - (1 if a > L // 2 else 0), cc + dc - 1
                f.put(aa if along == "u" else c2, c2 if along == "u" else aa, M[k])


def paint_leather(f, along):
    L = f.w if along == "u" else f.h
    C = f.h if along == "u" else f.w
    for a in range(L):
        for c in range(C):
            col = mix(LEATHER[2], LEATHER[3], noise(a, c, f.seed) * 0.4)
            if (a + c) % 4 == 0:                       # diagonal wrap seams
                col = LEATHER[1]
            elif (a + c) % 4 == 1:
                col = mix(LEATHER[3], LEATHER[4], 0.3)
            if c == 0:
                col = mix(col, LEATHER[4], 0.5)
            if c == C - 1:
                col = LEATHER[0]
            if a % 4 == 2 and c in (1, C - 2):          # stitches
                col = THREAD
            f.put(a if along == "u" else c, c if along == "u" else a, col)


def paint_gem(f, G):
    for v in range(f.h):
        for u in range(f.w):
            col = G[2]
            if u == 0 or v == 0:
                col = G[4]
            elif u == f.w - 1 or v == f.h - 1:
                col = G[1]
            elif u == 1 and v == 1:
                col = G[4]
            f.put(u, v, col)


def bo_texture(z, metal, model, place, height):
    wood = ramp(wood_gradient(z), 5, 0.1, 0.9)        # the vanilla Bo_Wood texture colours (no vanilla pixels copied)
    t = BO[metal]
    M = ramp(staff_metal(z, metal), 5, 0.12 if metal == "Onyxium" else 0.05, 1.0)
    B = ramp(SA.band_gradient(z, "Mithril"), 5, 0.1, 0.95) if t.get("gold") else M
    G = ramp(staff_gem(z, metal), 5, 0.15, 1.0)
    img = SA.Img(TEX_W, height)
    sizes = dict((n["name"], n["shape"]["settings"]["size"]) for n in all_boxes(model["nodes"], []))
    lays = dict((n["name"], n["shape"]["textureLayout"]) for n in all_boxes(model["nodes"], []))
    for i, ((name, face), (px, py, w, h, rot)) in enumerate(sorted(place.items())):
        a, b = FACE_WH[face]
        wh = (int(math.ceil(sizes[name][a])), int(math.ceil(sizes[name][b])))
        f = Face(img, None, i * 7 + 3, lays[name][face], wh)
        side = face in ("front", "back", "top", "bottom")    # u runs along the staff (box x axis) on these faces
        along = "u" if side else "v"
        if name.startswith("Shaft"):
            paint_wood(f, wood, along)
        elif name == "Handle":
            paint_leather(f, along)
        elif name.startswith(("Cap", "Point", "Spike")):
            paint_metal(f, M, along, seed_rivets=t.get("rivets") and name.startswith("Cap") and side,
                        engrave=name.startswith("Cap") and t["cap"] >= 12)
        elif name.startswith("Band") or name.startswith("GripRim"):
            paint_metal(f, B if name.startswith("Band") else M, along)
        elif name.startswith("Stud"):
            paint_gem(f, G)
        else:
            raise SystemExit("unpainted box %s" % name)
    return SA.png_encode(img)


# ======================================================================================================== output
def write(rel, data):
    p = os.path.join(OUT, rel.replace("/", os.sep))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as fh:
        fh.write(data)
    return "models-local/art/staffs/" + rel


def contact_sheet(icons, cols=7):
    """Every icon at 2x on a dark slot (vanilla-like inventory slot), no labels: row 1 staffs, row 2 Bo staffs."""
    S, pad = 128, 12
    rows = (len(icons) + cols - 1) // cols
    W, H = cols * (S + pad) + pad, rows * (S + pad) + pad
    img = SA.Img(W, H)
    bg, slot, rim = (24, 26, 34), (44, 48, 60), (66, 72, 88)
    for y in range(H):
        for x in range(W):
            img.put(x, y, bg + (255,))
    for k, png in enumerate(icons):
        ic = SA.png_decode(png)
        ox, oy = pad + (k % cols) * (S + pad), pad + (k // cols) * (S + pad)
        for y in range(S):
            for x in range(S):
                base = rim if x in (0, S - 1) or y in (0, S - 1) else slot
                r, g, b, a = ic.get(x // 2, y // 2)          # premultiplied
                fa = a / 255.0
                img.put(ox + x, oy + y, (r + base[0] * (1 - fa), g + base[1] * (1 - fa), b + base[2] * (1 - fa), 255))
    return SA.png_encode(img)


def main():
    SA.verify(quiet=True)
    z = SA.assets()
    manifest, icons, notes = [], [], {}
    checks = {}
    for metal in METALS:                                 # (a)
        d, model, tex, ngrip = staff_texture(z, metal)
        props = d["IconProperties"]
        icon = SA.render_icon(model, tex, props, 64)
        _d, _m, vtex, vicon = SA.item_parts(z, STAFF_ITEM % metal)
        ec, ea = SA.check_icon(model, vtex, props, vicon)
        checks[metal] = (round(ec, 2), round(ea, 2), props["Rotation"])
        tp = write("%s/SkyyArmory_%s_Texture.png" % (TEX_DIR, metal), tex)
        ip = write("%s/SkyyArmory_Staff_%s.png" % (ICON_DIR, metal), icon)
        icons.append(icon)
        parts = STAFF_PARTS[metal]
        manifest.append({
            "item": "Weapon_Staff_%s" % metal, "tier": metal,
            "model_path": "Items/Weapons/Staff/%s.blockymodel" % metal,
            "model_base": "Common/Items/Weapons/Staff/%s.blockymodel" % metal,
            "texture_path": tp, "icon_path": ip,
            "notes": "R1 re-texture of the vanilla %s staff (same model, UV, %dx%d, IconProperties %s). shaft=%s -> wood; grip=%s; "
                     "metal=%s; %sgem=%s. check_icon on the vanilla %s staff: colour %.2f, alpha %.2f / 255."
                     % (metal, SA.png_decode(tex).w, SA.png_decode(tex).h, json.dumps(props), "/".join(parts["shaft"]),
                        "black leather wrap painted on %d shaft texels at %d-%d%% of the length from the butt" % (
                            ngrip, GRIP_SPAN[0] * 100, GRIP_SPAN[1] * 100),
                        "/".join(parts["metal"]), ("band (gold)=%s; " % "/".join(parts["band"])) if "band" in parts else "",
                        "/".join(str(g) for g in parts["gem"]), metal, ec, ea)
                     + tint_note(metal)})
    bd, _bm, _bt, _bi = SA.item_parts(z, BO_ITEM)
    vanilla_bo = json.loads(z.read("Common/" + bd["Model"]).decode("utf-8-sig"))
    for metal in METALS:                                 # (b)
        model = bo_model(vanilla_bo, metal)
        place, height = pack(model)
        tex = bo_texture(z, metal, model, place, height)
        icon = SA.render_icon(model, tex, bd["IconProperties"], 64)
        mj = (json.dumps(model, indent=2) + "\n").encode("utf-8")
        mp = write("%s/SkyyArmory_Bo_%s.blockymodel" % (TEX_DIR, metal), mj)
        tp = write("%s/SkyyArmory_Bo_%s_Texture.png" % (TEX_DIR, metal), tex)
        ip = write("%s/SkyyArmory_Bo_%s.png" % (ICON_DIR, metal), icon)
        icons.append(icon)
        t = BO[metal]
        manifest.append({
            "item": "SkyyArmory_Bo_%s" % metal, "tier": metal,
            "model_path": mp, "model_base": "own (rig nodes R-Attachment/Origin_Projectile/Origin_Item/Handle copied from "
                                            "Common/Items/Weapons/Staff/Bo_Wood.blockymodel)",
            "texture_path": tp, "icon_path": ip,
            "notes": "own boxes, texture %dx%d; cap %d units, %d band(s) per end%s%s%s%s%s; IconProperties = vanilla Bo_Wood %s"
                     % (TEX_W, height, t["cap"], t["bands"], ", gold bands" if t.get("gold") else "",
                        ", rivets" if t.get("rivets") else "", ", pointed tips" if t.get("point") else "",
                        ", cap spikes" if t.get("spikes") else "", ", crystal stud on grip" if t.get("stud") else "",
                        json.dumps(bd["IconProperties"])) + tint_note(metal)})
    bo_vanilla = SA.check_icon(SA._read(z, bd["Model"]), SA._read(z, bd["Texture"]), bd["IconProperties"],
                               SA._read(z, bd["Icon"]))
    write("sheet.png", contact_sheet(icons))
    write("manifest.json", (json.dumps(manifest, indent=2) + "\n").encode("utf-8"))
    z.close()
    for m, c in checks.items():
        print("check_icon vanilla staff %-10s colour %6.2f alpha %5.2f rotation %s" % (m, c[0], c[1], c[2]))
    print("check_icon vanilla Bo_Wood       colour %6.2f alpha %5.2f" % bo_vanilla)
    print("wrote %d items to %s" % (len(manifest), OUT))


if __name__ == "__main__":
    main()
