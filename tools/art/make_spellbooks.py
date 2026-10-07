"""make_spellbooks - SkyWynn metal spellbook art, Copper .. Onyxium (7 tiers): models + textures + inventory icons + a review sheet.

Concept (approved by Skyy; "richer spellbooks", docs/answered/gear.md WEAPONS 2026-10-06): research/cloud/weapon-art/spellbook-v2.png
(+ make_weapons_v2.py draw_book / emblem), Spellbook-Ladder.md 1, weapon-art README spellbook row: tooled leather cover (tinted per
tier in v2), cream pages, tooled border, clasp, metal corner caps that grow per tier, metal spine bands (2, then 3 from Cobalt), a
leather medallion with the tier's cover EMBLEM (Copper sun ring, Iron riveted square, Thorium round boss, Cobalt diamond + gem,
Adamantite crystal shards, Mithril star, Onyxium gem in an oval setting), gold trim on Mithril, gilded page edges on Mithril / Onyxium,
a bookmark ribbon in the concept's ribbon colour.

Route: R1 + own boxes. Base = the vanilla Weapon_Spellbook_Grimoire_Brown (Items/Weapons/Spellbook/Grimoire.blockymodel: Handle =
spine, Book-Top / Book-Bot = the two boards, Lock-* = clasp, Gem = a fullbright gem box on the cover, Bookmark, Page-* quads). Every
vanilla node keeps its UV; the vanilla texels are recoloured per node rect (leather from the tier ramp below, clasp from the tier's
wand metal, bookmark in the concept's ribbon colour (CONCEPT_RIBBON), gilded page edges from the wand gold trim). The vanilla Gem
node is removed; our own boxes are added (children of the node that animates them - the book opens in the cast animations):
  Book-Top : 4 corner caps + the emblem (one box per run of texels per layer, so the cut-out shape has real side walls)
  Book-Bot : 4 corner caps on the back board
  Handle   : 2 / 3 spine bands
The texture grows from 64x64 to 64x96; the new rows hold our boxes' UV (painted from code). Colours come from Assets.zip at RUN
time. "Match the wands" (Skyy, LOCKED 2026-10-07, docs/answered/gear.md ART answers): every metal part (corner caps, spine bands,
clasp, emblem metal) and the emblem gems use the SAME colours as the built metal wands - wand_ramps() samples SA.wand_texture
(metal, "A") per part: head + shaft = the tier metal (SA.metal_gradient: vanilla pickaxe head + ingot, silver-blue Mithril,
black-violet Onyxium), bands = the band trim (the vanilla Mithril staff gold on Mithril, else the tier metal), leaves = the tier's
vanilla staff gem (SA.gem_gradient). Gold tooling / gilded page edges = the Mithril wand's gold bands. This file holds NO vanilla
pixels; the cover leather and ribbon ramps are ours (BOOK_LEATHER / CRYSTAL / ESSENCE of research/cloud/weapon-art/make_weapons_v2.py).

Icons: the vanilla IconProperties of Grimoire_Brown. Measured 2026-10-07 (SA.check_icon on the vanilla Grimoire_Brown icon):
geometry exact (alpha error 0.17 / 255) but colour 16.9 / 255, because the game's icon generator darkens faces whose shadingMode is
"standard" (x ~0.787 in this view) and leaves "flat" / "fullbright" faces alone (the Grimoire gem is fullbright: x 1.03; the Demon
spellbook, all "flat", matches at 4.1). render() below applies that factor; with it the vanilla Grimoire icon comes out within the
error printed at run time.

Run:  python tools/art/make_spellbooks.py
Out:  models-local/art/spellbooks/ (git-ignored: everything there is vanilla-derived)
        Common/Items/Weapons/Spellbook/SkyyArmory_<Metal>.blockymodel   (copy of the vanilla Grimoire model + our boxes)
        Common/Items/Weapons/Spellbook/SkyyArmory_<Metal>_Texture.png   (64x96)
        Common/Icons/ItemsGenerated/SkyyArmory_Spellbook_<Metal>.png      (64x64, premultiplied)
        previews/<Metal>_256.png (icon view), previews/<Metal>_34.png (3/4 view), sheet.png, manifest.json
Deterministic: no clocks / randomness; two runs give the same bytes.
"""
import copy
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyyart as SA  # noqa: E402

OUT = os.path.join(ROOT, "models-local", "art", "spellbooks")
BASE_ITEM = "Server/Item/Items/Weapon/Spellbook/Weapon_Spellbook_Grimoire_Brown.json"
MODEL_DIR = "Common/Items/Weapons/Spellbook"
ICON_DIR = "Common/Icons/ItemsGenerated"
METALS = SA.METALS   # Copper, Iron, Thorium, Cobalt, Adamantite, Mithril, Onyxium
TEX_H = 96           # 64 vanilla rows + 32 rows for our boxes
STANDARD_SHADE = 0.787   # icon generator factor for shadingMode "standard" faces in the [45, 90, 0] view (fitted on Grimoire_Brown)


def hx(s):
    s = s.lstrip("#")
    return (float(int(s[0:2], 16)), float(int(s[2:4], 16)), float(int(s[4:6], 16)))


def ramp(*cols):
    """24-step gradient through our 5 ramp colours (dark -> light)."""
    pts = [hx(c) for c in cols]
    out = []
    for i in range(24):
        f = i / 23.0 * (len(pts) - 1)
        k = min(int(f), len(pts) - 2)
        t = f - k
        out.append(tuple(pts[k][j] + (pts[k + 1][j] - pts[k][j]) * t for j in range(3)))
    return tuple(out)


# cover leather per tier = research/cloud/weapon-art/make_weapons_v2.py BOOK_LEATHER (the approved v2 sheet; our own colours)
BOOK_LEATHER = {
    "Copper": ramp("#1e0e07", "#4c2414", "#6e3820", "#8e4e2e", "#ae6a42"),       # tan brown
    "Iron": ramp("#140a06", "#34201a", "#4c3024", "#664232", "#825a46"),         # dark brown
    "Thorium": ramp("#0c1a10", "#1e3a24", "#2c5434", "#3e6e46", "#58905e"),      # deep green
    "Cobalt": ramp("#0a1024", "#1a2850", "#26386c", "#34508c", "#4c6cac"),       # navy
    "Adamantite": ramp("#1a0608", "#46121a", "#621c26", "#802a34", "#a0404a"),   # oxblood
    "Mithril": ramp("#141c22", "#34444e", "#4c606a", "#687e88", "#8aa2aa"),      # slate blue-grey
    "Onyxium": ramp("#0a0610", "#1e1428", "#2e2040", "#40305a", "#5a4878"),      # black-violet
}
# bookmark ribbons = the approved v2 concept (make_weapons_v2.py draw_book(); our own colours - cloth, not metal or gem). Emblem
# gems + all metal come from the built metal wands (wand_ramps; Skyy 2026-10-07 "Match the wands").
CONCEPT_RIBBON = {
    "Copper": ramp("#3e0806", "#8a1610", "#d22e1e", "#ff7448", "#ffd8b8"),       # ESSENCE Fire red
    "Iron": ramp("#0c2c4a", "#1f5f9a", "#3a8fd6", "#7cc0f2", "#e0f4ff"),         # CRYSTAL[1] blue
    "Thorium": ramp("#2e3a08", "#647a14", "#98b424", "#c8e050", "#f4ffc0"),      # CRYSTAL[2] lime
    "Cobalt": ramp("#08343e", "#13707e", "#22b0be", "#6ee6ee", "#e0ffff"),       # CRYSTAL[3] cyan
    "Adamantite": ramp("#3e0c06", "#8a2410", "#d4461c", "#ff8a46", "#ffe0b0"),   # CRYSTAL[4] red-orange
    "Mithril": ramp("#1c3a40", "#5aa0aa", "#a8e4e4", "#e0fbf8", "#ffffff"),      # CRYSTAL[5] pale cyan
    "Onyxium": ramp("#2a0626", "#6e1466", "#b42aa8", "#ec6ad8", "#ffd0f6"),      # CRYSTAL[6] magenta
}
CAP = {"Copper": 3, "Iron": 3, "Thorium": 4, "Cobalt": 4, "Adamantite": 4, "Mithril": 5, "Onyxium": 5}   # corner cap size (grows)
BANDS = {"Copper": (-7, 7), "Iron": (-7, 7), "Thorium": (-7, 7)}   # spine band z; 3 bands from Cobalt
BANDS_3 = (-9, 0, 9)
GEM_TIERS = ("Cobalt", "Adamantite", "Mithril", "Onyxium")   # emblems with gem texels
GILDED = ("Mithril", "Onyxium")         # gold tooled frame + gilded page edges
LATTICE = ("Cobalt", "Adamantite", "Mithril", "Onyxium")   # diamond tooling inside the frame (concept: from Cobalt)
EMBLEM_C = (8.5, 13.5)                   # emblem / medallion centre in cover texels (u from the spine, v from the top)
EMBLEM_O = (4, 9)                        # top-left cover texel of the 9x9 emblem grid

# Emblems: 9x9, two layers (layer 2 sits on layer 1). '#' tier metal, 'd' engraved (dark) metal, 'r' rivet, 'o' gold,
# 'g' gem (fullbright), 'h' gem highlight (fullbright), '.' empty.
EMBLEMS = {
    "Copper": (["....#....",            # sun ring with rays round a boss
                "..#####..",
                ".##...##.",
                ".#.....#.",
                "##..#..##",
                ".#.....#.",
                ".##...##.",
                "..#####..",
                "....#...."],
               ["........."] * 4 + ["....r...."] + ["........."] * 4),
    "Iron": ([".........",              # riveted square, engraved cross
              ".#######.",
              ".###d###.",
              ".###d###.",
              ".#ddddd#.",
              ".###d###.",
              ".###d###.",
              ".#######.",
              "........."],
             [".........",
              ".........",
              "..r...r..",
              ".........",
              ".........",
              ".........",
              "..r...r..",
              ".........",
              "........."]),
    "Thorium": None,                    # round boss: generated (circle + groove ring, raised centre)
    "Cobalt": None,                     # diamond + gem: generated
    "Adamantite": (["....g....",        # crystal shards on a metal base
                    "....g....",
                    ".g.ggg.g.",
                    ".g.ggg.g.",
                    "gg.ggg.gg",
                    "gg.ggg.gg",
                    "#########",
                    ".#######.",
                    "........."],
                   [".........",
                    "....h....",
                    "....h....",
                    "....h....",
                    "....h....",
                    "....h....",
                    ".........",
                    ".........",
                    "........."]),
    "Mithril": (["....#....",           # 8-point star, glowing heart
                 "....#....",
                 "..#.#.#..",
                 "...###...",
                 "#########",
                 "...###...",
                 "..#.#.#..",
                 "....#....",
                 "....#...."],
                [".........",
                 ".........",
                 ".........",
                 "....h....",
                 "...hgh...",
                 "....h....",
                 ".........",
                 ".........",
                 "........."]),
    "Onyxium": None,                    # violet gem in a gold setting: generated
}


def _grid(fn):
    return ["".join(fn(i - 4, j - 4) for i in range(9)) for j in range(9)]


def emblem(metal):
    e = EMBLEMS[metal]
    if e is not None:
        return e
    if metal == "Thorium":
        l1 = _grid(lambda dx, dy: "." if math.hypot(dx, dy) > 4.4 else ("d" if 2.6 <= math.hypot(dx, dy) < 3.3 else "#"))
        l2 = _grid(lambda dx, dy: "." if math.hypot(dx, dy) > 1.9 else ("r" if (dx, dy) == (-1, -1) else "#"))
        return l1, l2
    if metal == "Cobalt":
        l1 = _grid(lambda dx, dy: "#" if abs(dx) + abs(dy) <= 4 else ".")
        l2 = _grid(lambda dx, dy: ("h" if (dx, dy) in ((0, -1), (-1, 0)) else "g") if abs(dx) + abs(dy) <= 2 else ".")
        return l1, l2
    # Onyxium: the gem in an Onyxium-metal oval setting (was gold; the wands keep gold trim for Mithril only)
    l1 = _grid(lambda dx, dy: "#" if (dx / 3.6) ** 2 + (dy / 4.5) ** 2 <= 1.0 else ".")
    l2 = _grid(lambda dx, dy: ("h" if (dx, dy) in ((-1, -2), (-1, -1)) else "g") if (dx / 2.2) ** 2 + (dy / 3.2) ** 2 <= 1.0 else ".")
    return l1, l2


# ================================================================= small helpers
def noise(x, y, seed):
    n = (x * 374761393 + y * 668265263 + seed * 2147483647) & 0xffffffff
    n = ((n ^ (n >> 13)) * 1274126177) & 0xffffffff
    return ((n ^ (n >> 16)) & 0xffff) / 65535.0


def mul(c, f):
    return (c[0] * f, c[1] * f, c[2] * f, c[3] if len(c) > 3 else 255)


def mix(a, b, t):
    return tuple(a[k] + (b[k] - a[k]) * t for k in range(3)) + (255,)


def col(grad, t):
    c = SA.sample(grad, t)
    return (c[0], c[1], c[2], 255)


def find(nodes, name):
    for n in nodes:
        if n.get("name") == name:
            return n
        r = find(n.get("children") or [], name)
        if r:
            return r
    return None


def iter_nodes(nodes):
    for n in nodes:
        yield n
        for c in iter_nodes(n.get("children") or []):
            yield c


# ================================================================= geometry (our boxes)
FACE_WH = {"front": ("x", "y"), "back": ("x", "y"), "left": ("z", "y"), "right": ("z", "y"), "top": ("x", "z"), "bottom": ("x", "z")}


class Builder(object):
    """Adds our boxes; boxes with the same 'skin' key share one UV set (all corner caps, all bands)."""

    def __init__(self):
        self.next_id = 100
        self.boxes = []       # (node, skin key, faces, paint info)

    def box(self, parent, name, size, pos, skin, faces, info, shading="standard"):
        node = {
            "id": str(self.next_id), "name": name, "children": [],
            "position": {"x": pos[0], "y": pos[1], "z": pos[2]},
            "orientation": {"x": 0, "y": 0, "z": 0, "w": 1},
            "shape": {"type": "box", "offset": {"x": 0, "y": 0, "z": 0}, "stretch": {"x": 1, "y": 1, "z": 1},
                      "settings": {"size": {"x": size[0], "y": size[1], "z": size[2]}}, "visible": True, "doubleSided": False,
                      "shadingMode": shading, "unwrapMode": "custom", "textureLayout": {}},
        }
        self.next_id += 1
        parent.setdefault("children", []).append(node)
        self.boxes.append((node, skin, faces, info))
        return node


def build_model(vanilla, metal, b):
    m = copy.deepcopy(vanilla)
    nodes = m["nodes"]
    top, bot, handle = find(nodes, "Book-Top"), find(nodes, "Book-Bot"), find(nodes, "Handle")
    top["children"] = [c for c in top["children"] if c.get("name") != "Gem"]   # the emblem replaces the vanilla gem
    s = CAP[metal]
    allf = ("front", "back", "left", "right", "top", "bottom")
    # corner caps: s x 5 x s, 0.5 proud of the board on the outer sides, 1 above the cover (board = node frame x -3..17,
    # z -13..13; Book-Top board y 0..4 with the shape offset at y 2, Book-Bot board y -4..0 with offset y -2). The spine-side caps
    # start at the spine's edge (x 0; the Handle covers the board up to there).
    xs = ((10.5 - s / 2.0, "F"), (s / 2.0 - 7.0, "S"))
    zs = ((13.5 - s / 2.0, "B"), (-(13.5 - s / 2.0), "T"))
    for (px, ex) in xs:
        for (pz, ez) in zs:
            b.box(top, "Skyy-Cap-Top-%s%s" % (ex, ez), (s, 5, s), (px, 0.5, pz), "cap", allf, None)
            b.box(bot, "Skyy-Cap-Bot-%s%s" % (ex, ez), (s, 5, s), (px, -0.5, pz), "cap", allf, None)
    # spine bands: 7 x 10 x 2 round the Handle (Handle shape: 6 x 9 x 27, offset y -2), 0.5 proud everywhere
    for i, z in enumerate(BANDS.get(metal, BANDS_3)):
        b.box(handle, "Skyy-Band-%d" % (i + 1), (7, 10, 2), (0, 0, z), "band", allf, None)
    # emblem: one box per horizontal run of same-kind texels per layer (texel (u, v) of the cover = node frame x -3+u, z -13+v;
    # Book-Top's shape offset is (7, 2, 0); the cover top is y 4 -> layer 1 = y 4..5, layer 2 = y 5..6)
    for li, layer in enumerate(emblem(metal)):
        for j, row in enumerate(layer):
            i = 0
            while i < 9:
                ch = row[i]
                if ch == ".":
                    i += 1
                    continue
                gem = ch in "gh"
                k = i
                while k + 1 < 9 and row[k + 1] != "." and (row[k + 1] in "gh") == gem:
                    k += 1
                u0, u1 = EMBLEM_O[0] + i, EMBLEM_O[0] + k + 1
                v = EMBLEM_O[1] + j
                xc = -3 + (u0 + u1) / 2.0
                zc = -13 + v + 0.5
                yc = 4.5 + li
                b.box(top, "Skyy-Emblem-%d-%d-%d" % (li + 1, j, i), (k - i + 1, 1, 1), (xc - 7, yc - 2, zc),
                      "emblem-%d-%d-%d" % (li + 1, j, i), ("front", "back", "left", "right", "top"),
                      {"layer": li, "row": row[i:k + 1], "u0": u0, "v": v, "above": (layer if li == 0 else None)},
                      shading="fullbright" if gem else "standard")
                i = k + 1
    return m


def pack(b, y0, width=64):
    """Shelf-pack the faces of our boxes into rows y0.. (one UV set per skin); sets textureLayout. Returns {(skin, face): rect}."""
    want = []
    seen = set()
    for node, skin, faces, _info in b.boxes:
        if skin in seen:
            continue
        seen.add(skin)
        size = node["shape"]["settings"]["size"]
        for f in faces:
            a, c = FACE_WH[f]
            want.append((skin, f, int(size[a]), int(size[c])))
    want.sort(key=lambda r: (-r[3], -r[2], r[0], r[1]))
    place, x, y, row = {}, 0, y0, 0
    for skin, f, w, h in want:
        if x + w > width:
            x, y, row = 0, y + row, 0
        place[(skin, f)] = (x, y, w, h)
        x += w
        row = max(row, h)
    if y + row > TEX_H:
        raise SystemExit("make_spellbooks: our UV needs %d rows, the texture has %d" % (y + row, TEX_H))
    for node, skin, faces, _info in b.boxes:
        node["shape"]["textureLayout"] = dict(
            (f, {"offset": {"x": place[(skin, f)][0], "y": place[(skin, f)][1]}, "mirror": {"x": False, "y": False}, "angle": 0})
            for f in faces)
    return place


# ================================================================= texture
def leather_grad(metal):
    return BOOK_LEATHER[metal]


def flatten_gold(img, rect, thresh=104.0):
    """Painted gold corners in the vanilla cover / board texels -> the rect's median leather tone (caps cover them now)."""
    x0, y0, x1, y1 = rect
    pix = [img.get(x, y) for y in range(y0, y1) for x in range(x0, x1) if img.get(x, y)[3] and SA.luma(img.get(x, y)) < thresh]
    pix.sort(key=lambda c: (SA.luma(c), c))
    med = pix[len(pix) // 2]
    for y in range(y0, y1):
        for x in range(x0, x1):
            c = img.get(x, y)
            if c[3] and SA.luma(c) >= thresh:
                img.put(x, y, med)


def cover_paint(img, rect, metal, flip_v, front, G):
    """Tooling on a board: double frame, medallion (front), lattice (from Cobalt). rect = the 20 x 26 board texels."""
    x0, y0, x1, y1 = rect
    L = leather_grad(metal)

    def P(u, v):
        return (x0 + u, (y1 - 1 - v) if flip_v else (y0 + v))

    def tint(u, v, f):
        x, y = P(u, v)
        img.put(x, y, mul(img.get(x, y), f))

    def setc(u, v, c):
        x, y = P(u, v)
        img.put(x, y, c)
    cu, cv = EMBLEM_C
    gilded = metal in GILDED
    for v in range(26):
        for u in range(3, 20):
            on_outer = (u in (4, 18) and 1 <= v <= 24) or (v in (1, 24) and 4 <= u <= 18)
            on_inner = (u in (6, 16) and 3 <= v <= 22) or (v in (3, 22) and 6 <= u <= 16)
            r = math.hypot(u + 0.5 - cu, v + 0.5 - cv) if front else 99.0
            if r < 6.0:
                continue
            if on_outer:
                if gilded:
                    setc(u, v, col(G["gold"], 0.55 + 0.25 * noise(u, v, 3)))
                else:
                    tint(u, v, 0.55)
            elif on_inner:
                if gilded:
                    setc(u, v, col(G["gold"], 0.35 + 0.2 * noise(u, v, 4)))
                else:
                    tint(u, v, 1.3)
            elif ((u + 1 == 5 and 2 <= v <= 23) or (v - 1 == 1 and 5 <= u <= 17)):
                tint(u, v, 1.18)                           # light lip under the outer groove (top / spine side)
            elif metal in LATTICE and 7 <= u <= 15 and 4 <= v <= 21 and ((u + v) % 4 == 0 or (u - v) % 4 == 0):
                tint(u, v, 0.72)
    if front:   # leather medallion under the emblem: a sunken well (so the metal reads), dark groove, light raised rim;
        l1 = emblem(metal)[0]  # the emblem casts a 1-texel shadow down / away from the spine
        on = set((EMBLEM_O[0] + i, EMBLEM_O[1] + j) for j, rw in enumerate(l1) for i, ch in enumerate(rw) if ch != ".")
        for v in range(26):
            for u in range(3, 20):
                r = math.hypot(u + 0.5 - cu, v + 0.5 - cv)
                if r < 4.9:
                    if (u, v) in on:
                        tint(u, v, 0.78)
                    elif (u - 1, v - 1) in on or (u - 1, v) in on or (u, v - 1) in on:
                        tint(u, v, 0.42)       # shadow + outline so the metal reads on same-hue leather
                    elif (u + 1, v) in on or (u, v + 1) in on:
                        tint(u, v, 0.6)
                    else:
                        tint(u, v, 0.8)
                elif r < 5.6:
                    if gilded:
                        setc(u, v, col(G["gold"], 0.45 + 0.2 * noise(u, v, 5)))
                    else:
                        tint(u, v, 0.5)
                elif r < 6.2:
                    tint(u, v, 1.25)
    else:       # back board: blind-tooled ring
        for v in range(26):
            for u in range(3, 20):
                r = math.hypot(u + 0.5 - 11.0, v + 0.5 - 13.0)
                if 3.3 <= r < 4.1:
                    tint(u, v, 0.6)


class Face(object):
    def __init__(self, img, rect):
        self.img, (self.x, self.y, self.w, self.h) = img, rect

    def put(self, u, v, c):
        if 0 <= u < self.w and 0 <= v < self.h:
            self.img.put(self.x + u, self.y + v, c)


def metal_face(f, grad, base=0.55, seed=1, bevel=True):
    for v in range(f.h):
        for u in range(f.w):
            t = base + 0.08 * (noise(u, v, seed) - 0.5)
            if bevel:
                if u == 0 or v == 0:
                    t += 0.22
                elif u == f.w - 1 or v == f.h - 1:
                    t -= 0.22
            f.put(u, v, col(grad, t))


def paint_ours(img, b, place, metal, G):
    M = G["metal"]
    band = G["band"]   # the wand's band texels: gold trim on Mithril, the tier metal elsewhere
    done = set()
    for node, skin, faces, info in b.boxes:
        if skin in done:
            continue
        done.add(skin)
        for fname in faces:
            f = Face(img, place[(skin, fname)])
            if skin == "cap":
                metal_face(f, M, 0.68 if fname == "top" else 0.5, seed=7)
                if fname == "top" and f.w >= 3:          # rivet near the outer corner + a scratch line
                    f.put(f.w // 2, f.h // 2, col(M, 0.95))
                    f.put(f.w // 2 + 1, f.h // 2 + 1, col(M, 0.15))
            elif skin == "band":
                metal_face(f, band, 0.62 if fname in ("left", "top", "bottom") else 0.45, seed=11)
                if fname == "left":                     # the spine face: a raised ridge + rivet
                    for v in range(f.h):
                        f.put(0, v, col(band, 0.85))
                        f.put(f.w - 1, v, col(band, 0.2))
                    f.put(0, f.h // 2, col(band, 1.0))
            else:
                paint_emblem_face(f, fname, info, metal, G)


def emblem_colour(ch, u, v, edge, G, metal):
    """Top-face colour of one emblem texel. edge: -1 = lit edge (top / spine side), 1 = shadow edge, 0 = inside."""
    M = G["metal"]
    if ch in "#":
        t = 0.8 + 0.14 * (-edge) + 0.08 * (noise(u, v, 21) - 0.5)
        return col(M, t)
    if ch == "d":
        return col(M, 0.3)
    if ch == "r":
        return col(M, 0.97)
    if ch == "o":
        return col(G["gold"], 0.62 + 0.2 * (-edge) + 0.06 * (noise(u, v, 23) - 0.5))
    if ch == "g":
        return col(G["gem"], 0.55 + 0.18 * (-edge) + 0.06 * (noise(u, v, 25) - 0.5))
    return col(G["gem"], 1.0)   # 'h'


def paint_emblem_face(f, fname, info, metal, G):
    row, u0, v = info["row"], info["u0"], info["v"]
    for i, ch in enumerate(row):
        u = u0 + i
        lit = (i == 0) or (v == EMBLEM_O[1])
        dark = (i == len(row) - 1)
        edge = -1 if lit and not dark else (1 if dark and not lit else 0)
        c = emblem_colour(ch, u, v, edge, G, metal)
        if fname == "top":
            f.put(i, 0, c)
        elif fname in ("front", "back"):
            # front (+z, toward the book's bottom edge) in shadow, back (toward the top edge) a bit lighter
            f.put(i if fname == "front" else len(row) - 1 - i, 0, mul(c, 0.62 if fname == "front" else 0.85))
    if fname in ("left", "right"):
        c = emblem_colour(row[0] if fname == "left" else row[-1], u0, v, 0, G, metal)
        f.put(0, 0, mul(c, 0.8 if fname == "left" else 0.6))


def wand_ramps(z, metal):
    """The tier's colours exactly as on the built metal wand (Skyy 2026-10-07 "Match the wands"): SA.wand_texture(metal, "A") is
    the wand recipe (metal_gradient = vanilla pickaxe head + ingot, band_gradient = the vanilla Mithril gold trim, gem_gradient =
    the tier's vanilla staff gem, with the wand's per-part tuning); each ramp = palette_from over that wand's texels of one part."""
    _d, wmodel, _t, _i = SA.item_parts(z, SA.WAND_ITEM)
    tex = SA.wand_texture(z, metal, "A")
    part = lambda names: SA.palette_from([(tex, SA.node_rects(wmodel, names))])   # noqa: E731
    return {"metal": part(SA.WAND_PARTS["head"] + SA.WAND_PARTS["shaft"]), "band": part(SA.WAND_PARTS["bands"]),
            "gem": part(SA.WAND_PARTS["leaves"])}


def make_texture(z, base_tex, vmodel, metal, b, place):
    W = wand_ramps(z, metal)
    G = {"metal": W["metal"], "band": W["band"], "gold": wand_ramps(z, "Mithril")["band"], "gem": W["gem"],
         "ribbon": CONCEPT_RIBBON[metal]}
    van = SA.png_decode(base_tex)
    img = SA.Img(64, TEX_H)
    for y in range(64):
        for x in range(64):
            img.put(x, y, van.get(x, y))
    L = leather_grad(metal)
    R = lambda names: SA.node_rects(vmodel, names)   # noqa: E731
    # the vanilla gem's texels are unused now
    for (x0, y0, x1, y1) in R(["Gem"]):
        for y in range(y0, y1):
            for x in range(x0, x1):
                img.put(x, y, (0, 0, 0, 0))
    front_cover, back_cover = (1, 29, 21, 55), (21, 29, 41, 55)
    # board edges: rows 55-56 + 61-62 = board leather, 57-60 = page edges (Book-Top front/back/right + Book-Bot ones)
    board_rows = [(1, 55, 47, 57), (1, 61, 47, 63)]
    page_rows = [(1, 57, 47, 61)]
    for r in [front_cover, back_cover] + board_rows:
        flatten_gold(img, r)
    img = SA.recolor(img, L, [front_cover, back_cover], lo=0.08, hi=0.78, rank=0.45, as_img=True)
    img = SA.recolor(img, L, board_rows, lo=0.05, hi=0.7, rank=0.4, as_img=True)
    if metal in GILDED:
        img = SA.recolor(img, G["gold"], page_rows, lo=0.25, hi=0.95, rank=0.5, as_img=True)
    # spine (Handle) -> tooled leather: the vanilla ornament becomes blind tooling
    img = SA.recolor(img, L, R(["Handle"]), lo=0.1, hi=0.85, rank=0.55, smooth=0.2, as_img=True)
    # clasp -> tier metal, bookmark -> the concept ribbon colour
    lock = R(["Lock-Top", "Lock-Front", "Lock-Bot"])
    img = SA.recolor(img, G["metal"], lock, lo=0.1, hi=0.95, rank=0.5, smooth=0.4, lift=SA.rim_lift(lock, 0.1, -0.03), as_img=True)
    img = SA.recolor(img, G["ribbon"], R(["Bookmark"]), lo=0.1, hi=0.95, rank=0.5, as_img=True)
    cover_paint(img, front_cover, metal, False, True, G)
    cover_paint(img, back_cover, metal, True, False, G)
    paint_ours(img, b, place, metal, G)
    return SA.png_encode(img), G


# ================================================================= icon renderer with the game's "standard" face shading
QUAD_TURN = {"-Y": (math.sqrt(0.5), 0.0, 0.0, math.sqrt(0.5)),     # the kit draws every quad in its x-y plane facing +z; a
             "+Y": (-math.sqrt(0.5), 0.0, 0.0, math.sqrt(0.5))}   # "normal" setting turns it (Page-Top / Page-Bot are -Y)


def _quads_upright(m):
    """Copy of the model with each quad's settings.normal folded into its orientation (offsets here lie on x only, which the
    x-axis turn keeps)."""
    m = copy.deepcopy(m)
    for n in iter_nodes(m["nodes"]):
        sh = n.get("shape") or {}
        q = QUAD_TURN.get((sh.get("settings") or {}).get("normal")) if sh.get("type") == "quad" else None
        if q:
            o = n.get("orientation") or {}
            a = (float(o.get("x", 0)), float(o.get("y", 0)), float(o.get("z", 0)), float(o.get("w", 1)))
            r = SA._qmul(a, q)
            n["orientation"] = {"x": r[0], "y": r[1], "z": r[2], "w": r[3]}
    return m


def render(model_json, tex_png, props, size=64, ss=2):
    m = json.loads(model_json) if isinstance(model_json, (str, bytes)) else model_json
    m = _quads_upright(m)
    faces = SA.model_faces(m)
    shading = dict((n.get("name"), (n.get("shape") or {}).get("shadingMode", "standard")) for n in iter_nodes(m["nodes"]))
    tex = SA.png_decode(tex_png) if not isinstance(tex_png, SA.Img) else tex_png
    hit, N = SA._raster(faces, tex, props, size, ss)
    out = SA.Img(size, size)
    n = float(ss * ss)
    for y in range(size):
        for x in range(size):
            acc, k = [0.0, 0.0, 0.0], 0
            for sy in range(ss):
                row = (y * ss + sy) * N + x * ss
                for sx in range(ss):
                    hv = hit[row + sx]
                    if hv is not None:
                        c = hv[1]
                        f = STANDARD_SHADE if shading.get(faces[hv[0]]["node"]) == "standard" else 1.0
                        acc[0] += c[0] * f
                        acc[1] += c[1] * f
                        acc[2] += c[2] * f
                        k += 1
            if k:
                a = SA._alpha_of(k / n)
                out.put(x, y, (acc[0] / k * a, acc[1] / k * a, acc[2] / k * a, a * 255))
    return out


def icon_error(mine, van):
    e_c = e_a = 0.0
    n = 0
    for y in range(64):
        for x in range(64):
            a, b = van.get(x, y), mine.get(x, y)
            e_a += abs(a[3] - b[3])
            if a[3] == 255 and b[3] == 255:
                e_c += (abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])) / 3.0
                n += 1
    return e_c / max(n, 1), e_a / 4096.0


# ================================================================= sheet
def sheet(icons, scale=2, pad=8, bg=(28, 28, 34), slot=(44, 44, 54)):
    cell = 64 * scale + pad
    W = pad + cell * len(icons)
    H = pad * 2 + 64 * scale
    img = SA.Img(W, H)
    for y in range(H):
        for x in range(W):
            img.put(x, y, bg + (255,))
    for i, ic in enumerate(icons):
        ox = pad + i * cell
        for y in range(64 * scale):
            for x in range(64 * scale):
                c = ic.get(x // scale, y // scale)
                a = c[3] / 255.0
                img.put(ox + x, pad + y, (c[0] + slot[0] * (1 - a), c[1] + slot[1] * (1 - a), c[2] + slot[2] * (1 - a), 255))
    return img


def unpremul_on(img, bg=(36, 36, 44)):
    o = SA.Img(img.w, img.h)
    for y in range(img.h):
        for x in range(img.w):
            c = img.get(x, y)
            a = c[3] / 255.0
            o.put(x, y, (c[0] + bg[0] * (1 - a), c[1] + bg[1] * (1 - a), c[2] + bg[2] * (1 - a), 255))
    return o


def write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    mode = "wb" if isinstance(data, (bytes, bytearray)) else "w"
    with open(path, mode, **({} if mode == "wb" else {"encoding": "utf-8", "newline": "\n"})) as fh:
        fh.write(data)


def main():
    z = SA.assets()
    d, vmodel_b, vtex, vicon = SA.item_parts(z, BASE_ITEM)
    props = d["IconProperties"]
    vanilla = json.loads(vmodel_b.decode("utf-8-sig"))
    # icon check on the vanilla base first (plain kit renderer, then with the standard-face shading)
    plain = SA.check_icon(vmodel_b, vtex, props, vicon)
    shaded = icon_error(render(vanilla, vtex, props), SA.png_decode(vicon))
    print("check_icon vanilla Grimoire_Brown: plain render colour %.2f alpha %.2f | with standard shading x%.3f: colour %.2f alpha %.2f"
          % (plain[0], plain[1], STANDARD_SHADE, shaded[0], shaded[1]))
    manifest, icons = [], []
    for metal in METALS:
        b = Builder()
        model = build_model(vanilla, metal, b)
        place = pack(b, 64)
        tex, G = make_texture(z, vtex, vanilla, metal, b, place)
        icon = render(model, tex, props)
        icons.append(icon)
        mpath = "%s/SkyyArmory_%s.blockymodel" % (MODEL_DIR, metal)
        tpath = "%s/SkyyArmory_%s_Texture.png" % (MODEL_DIR, metal)
        ipath = "%s/SkyyArmory_Spellbook_%s.png" % (ICON_DIR, metal)
        write(os.path.join(OUT, mpath), json.dumps(model, indent=2) + "\n")
        write(os.path.join(OUT, tpath), tex)
        write(os.path.join(OUT, ipath), SA.png_encode(icon))
        write(os.path.join(OUT, "previews", "%s_256.png" % metal), SA.png_encode(unpremul_on(render(model, tex, props, 256))))
        p34 = {"Scale": 0.62, "Translation": [-8.5, -9.0], "Rotation": [25, 125, 0]}
        write(os.path.join(OUT, "previews", "%s_34.png" % metal), SA.png_encode(unpremul_on(render(model, tex, p34, 256))))
        n_ours = len(b.boxes)
        manifest.append({
            "item": "SkyyArmory_Spellbook_%s" % metal, "tier": metal,
            "model_path": mpath, "model_base": "Common/" + d["Model"],
            "texture_path": tpath, "icon_path": ipath,
            "icon_properties": props,
            "notes": "R1 + own boxes: vanilla Grimoire nodes keep their UV (recoloured), Gem node removed, %d own boxes "
                     "(8 corner caps %dx5x%d, %d spine bands, emblem); texture 64x%d. Colours = the built %s metal wand (wand_ramps: metal %s, "
                     "bands %s, gem %s); ribbon = concept" % (
                         n_ours, CAP[metal], CAP[metal], len(BANDS.get(metal, BANDS_3)), TEX_H, metal,
                         SA.grad_hex(SA.grad_span(G["metal"], 0, 1, 3)), SA.grad_hex(SA.grad_span(G["band"], 0, 1, 3)),
                         SA.grad_hex(SA.grad_span(G["gem"], 0, 1, 3)) if metal in GEM_TIERS else "none (no gem in this emblem)"),
        })
    write(os.path.join(OUT, "manifest.json"), json.dumps(manifest, indent=2) + "\n")
    write(os.path.join(OUT, "sheet.png"), SA.png_encode(sheet(icons)))
    print("wrote %d spellbooks to %s" % (len(METALS), OUT))


if __name__ == "__main__":
    main()
