#!/usr/bin/env python3
"""SkyWynn Enchanted materials v2 - 64x64 icon concepts (cloud draft 2026-10-07).

Skyy's art review 2026-10-06 (docs/answered/gear.md, ENCHANTED ICONS): every
Enchanted icon is a shiny copy of the REAL vanilla resource:
  metals = Enchanted INGOTS (Ingredient_Bar_<Metal>), stone = Enchanted
  Cobblestone (the approved cobble block) + Enchanted Rubble (approved),
  logs are BLOCKS (Wood_<X>_Trunk) - one Enchanted Log per key log,
  sap / stick / farming icons approved and kept as drawn in v1.
The item list follows research/Gathering-Progression-Spec.md section 4.

Original pixel art drawn from code (no copied art, no game files).
The painter, the approved v1 drawings and the glint are imported from
make_enchanted.py (v1, unchanged), so the glint recipe is identical.
Run:  python3 research/cloud/enchanted-art/make_enchanted_v2.py
Writes icons-v2/ench-<id>.png (64 x 64) and enchanted-sheet-v2.png. Deterministic.
2026-10-08: + 14 icons for the rest of the v1 list (ITEMS_REST, README section 7).
"""
import importlib.util
import math
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('ench_v1', os.path.join(HERE, 'make_enchanted.py'))
V1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V1)          # v1 only builds under __main__, so this just loads its functions

Cv, ramp, hx, mix, nz, vnoise = V1.Cv, V1.ramp, V1.hx, V1.mix, V1.nz, V1.vnoise
poly, ell, edge, bbox, shade, crack = V1.poly, V1.ell, V1.edge, V1.bbox, V1.shade, V1.crack
cube, glint, font, PI = V1.cube, V1.glint, V1.font, V1.PI
thick = V1.thick


# ---------------------------------------------------------------- ingots
# A cast bar seen from above-front: a trapezoid prism (top narrower than the
# base), long side facing down-left, lit from the top-left like v1.
# Metal colours are guesses at the vanilla bars (UNVERIFIED, see README v2).
METALS = {
    # key: (body colour, specular tint)
    'copper': ('#cf7440', '#ffd7a8'),
    'iron': ('#a3abb5', '#f4f7fb'),
    'thorium': ('#86b04e', '#e6ffb8'),
    'cobalt': ('#3c68d2', '#c8dcff'),
    'adamantite': ('#c23636', '#ffc4b4'),
    'mithril': ('#58d0cc', '#e4fffc'),
}

C30, S30 = math.cos(PI / 6), math.sin(PI / 6)


def _proj(p, s, ox, oy):
    x, y, z = p
    return (ox + (x - y) * C30 * s, oy + (x + y) * S30 * s - z * s)


def ingot(cv, key, seed):
    body, spc = METALS[key]
    rp = ramp(body, 7, dark=0.62, light=0.55)
    L, W, H, d = 1.0, 0.46, 0.30, 0.085
    s, ox, oy = 47.0, 22.0, 20.0
    # bottom corners b(x,y), top corners t(x,y)
    B = {k: (x, y, 0) for k, (x, y) in {'00': (0, 0), '10': (L, 0), '11': (L, W), '01': (0, W)}.items()}
    T = {k: (x, y, H) for k, (x, y) in {'00': (d, d), '10': (L - d, d), '11': (L - d, W - d), '01': (d, W - d)}.items()}
    P = lambda p: _proj(p, s, ox, oy)
    top = poly(cv, [P(T['00']), P(T['10']), P(T['11']), P(T['01'])])
    front = poly(cv, [P(T['01']), P(T['11']), P(B['11']), P(B['01'])]) - top          # long side, faces down-left
    end = poly(cv, [P(T['11']), P(T['10']), P(B['10']), P(B['11'])]) - top - front    # short end, faces down-right
    allm = top | front | end
    ux, uy = C30, S30                       # screen direction of the long axis

    def brushed(x, y, amt):
        # streaks along the long axis + a little grain
        t = -(x + 0.5) * uy + (y + 0.5) * ux
        return (vnoise(t * 3.0, 0, 2, seed) - 0.5) * amt + (nz(x, y, seed + 3) - 0.5) * 0.05

    # top face: bright, a soft specular band across it
    tx0, ty0, tx1, ty1 = bbox(top)

    def t_top(x, y):
        a = (x - tx0) / max(1, tx1 - tx0)
        band = math.exp(-((a - 0.38) / 0.13) ** 2) * 0.22
        return band + brushed(x, y, 0.14) - 0.1 * ((y - ty0) / max(1, ty1 - ty0))
    shade(cv, top, rp, 'flat', v=0.70, tex=t_top, bevel=0.10, outline=False)

    def t_front(x, y):
        a = (x - tx0) / max(1, tx1 - tx0)
        band = math.exp(-((a - 0.30) / 0.10) ** 2) * 0.20
        return band + brushed(x, y, 0.12)
    shade(cv, front, rp, 'flat', v=0.45, tex=t_front, bevel=0.0, outline=False)
    shade(cv, end, rp, 'flat', v=0.20, tex=lambda x, y: brushed(x, y, 0.10), bevel=0.0, outline=False)

    # stamped mark on the top face: a sunken lozenge (dark upper-left rim, light lower-right rim)
    cx_, cy_ = P((L / 2, W / 2, H))
    lz = poly(cv, [P((0.30, 0.17, H)), P((0.70, 0.17, H)), P((0.70, W - 0.17, H)), P((0.30, W - 0.17, H))])
    for (x, y) in lz:
        if (x - 1, y) not in lz or (x, y - 1) not in lz or (x + 1, y - 1) not in lz:
            cv.put(x, y, rp['f'][1])          # shadowed far rim
        elif (x + 1, y) not in lz or (x, y + 1) not in lz:
            cv.put(x, y, mix(rp['f'][6], hx(spc), 0.4))   # lit near rim
        else:
            cv.put(x, y, rp['f'][3] if nz(x, y, seed + 9) > 0.25 else rp['f'][4])
    # casting pits and scratches
    for i in range(7):
        x = int(tx0 + 3 + nz(i, 1, seed) * (tx1 - tx0 - 6)); y = int(ty0 + 2 + nz(i, 2, seed) * (ty1 - ty0 - 4))
        if (x, y) in top and (x, y) not in lz and (x + 1, y + 1) in top:
            cv.put(x, y, rp['f'][2]); cv.put(x + 1, y + 1, rp['f'][5])
    for i in range(3):
        x = int(tx0 + 6 + nz(i, 4, seed) * (tx1 - tx0 - 14)); y = int(ty0 + 3 + nz(i, 5, seed) * (ty1 - ty0 - 6))
        pts = [(x, y), (x + 5, y + 2 + i % 2)]
        for p in V1.thick(cv, pts, 1) & top:
            if p not in lz:
                cv.put(p[0], p[1], mix(cv.get(*p)[:3], hx(spc), 0.45))
    for i in range(5):  # pits on the long face
        fx0, fy0, fx1, fy1 = bbox(front)
        x = int(fx0 + 4 + nz(i, 7, seed) * (fx1 - fx0 - 8)); y = int(fy0 + 3 + nz(i, 8, seed) * (fy1 - fy0 - 6))
        if (x, y) in front and (x, y) not in edge(front):
            cv.put(x, y, rp['f'][1])

    # edges: bright rim where faces meet the top, dark crease front/end, outline
    hi = hx(spc)
    for (x, y) in front | end:
        if (x, y - 1) in top or (x - 1, y - 1) in top:
            cv.put(x, y, mix(cv.get(x, y)[:3], hi, 0.75 if (x, y) in front else 0.35))
    for (x, y) in end:
        if (x - 1, y) in front:
            cv.put(x, y, rp['f'][0])
    for (x, y) in edge(top):
        if (x, y) in allm and ((x - 1, y) not in allm or (x, y - 1) not in allm):
            cv.put(x, y, mix(rp['f'][6], hi, 0.5))
    for p in edge(allm):
        cv.put(p[0], p[1], rp['o'])
    # ground contact shadow is left out (icons sit on a slot background)
    return allm


# ---------------------------------------------------------------- log blocks
# A log in Hytale is a block (Wood_<X>_Trunk): bark on the four sides,
# growth rings on the cut top. Colours and bark styles are guesses (UNVERIFIED).
LOGS = {
    # key: (bark, inner wood, ring, bark style)
    'oak': ('#5f4129', '#c99d64', '#9b6e3f', 'plates'),
    'maple': ('#6c4636', '#dcaa78', '#ae744c', 'furrow'),
    'gumboab': ('#a29380', '#e3cb9c', '#b99c6b', 'smooth'),
    'redwood': ('#7d3624', '#c96e48', '#92402a', 'fibre'),
    'sallow': ('#5e5c48', '#e5c66c', '#b48e3a', 'diamond'),
}


def tex_log(key, seed):
    bark, inner, ring, style = LOGS[key]
    brp, irp, rrp = ramp(bark, 7, dark=0.6, light=0.42), ramp(inner, 6, light=0.3), ramp(ring, 5)
    sap_c = ramp('#%02x%02x%02x' % mix(hx(inner), (255, 245, 220), 0.35), 5)

    def bark_side(face, u, v):
        n1 = vnoise(u * 24, v * 24, 3, seed)
        if style == 'plates':        # oak: blocky plates split by deep furrows
            col = int(u * 6 + n1 * 0.8)
            fu = (u * 6 + n1 * 0.8) % 1.0
            row = int(v * 4 + nz(col, 3, seed) * 2)
            fv = (v * 4 + nz(col, 3, seed) * 2) % 1.0
            if fu < 0.16:
                return -0.34
            if fv < 0.07:
                return -0.22
            return 0.10 - fu * 0.14 + (nz(col, row, seed) - 0.5) * 0.12
        if style == 'furrow':        # maple: many narrow vertical furrows
            g = math.sin(u * 2 * PI * 9 + n1 * 3.5)
            return -0.30 if g > 0.72 else (0.10 if g < -0.4 else 0)
        if style == 'smooth':        # gumboab (baobab-like): smooth with horizontal folds / lenticels
            g = math.sin(v * 2 * PI * 5 + vnoise(u * 10, v * 10, 3, seed + 4) * 3)
            dot = nz(int(u * 28), int(v * 28), seed) < 0.05
            return (-0.24 if g > 0.86 else 0.04) - (0.2 if dot else 0) + (n1 - 0.5) * 0.12
        if style == 'fibre':         # redwood: long stringy vertical strands
            g = math.sin(u * 2 * PI * 13 + vnoise(u * 6, v * 40, 4, seed) * 2.2)
            return -0.28 if g > 0.6 else (0.14 if g < -0.75 else -0.02)
        # sallow: diamond (criss-cross) furrows
        a = (u * 5 + v * 3 + n1 * 0.4) % 1.0
        b = (u * 5 - v * 3 + n1 * 0.4) % 1.0
        return -0.30 if (a < 0.13 or b < 0.13) else 0.06

    def t(face, u, v):
        if face == 'top':
            du, dv = u - 0.5, v - 0.5
            dd = math.hypot(du, dv)
            border = min(u, v, 1 - u, 1 - v)
            if border < 0.075:                      # bark seen from above
                return brp, 0.56 + (nz(int(u * 40), int(v * 40), seed) - 0.5) * 0.3
            if border < 0.11:                       # pale sapwood / cambium ring
                return sap_c, 0.62
            wob = vnoise(u * 30, v * 30, 5, seed + 2) * 0.9
            rr = dd * 10.5 + wob
            if dd < 0.035:
                return rrp, 0.12                     # pith
            # radial check crack toward the lower right
            ang = math.atan2(dv, du)
            if abs(ang - 0.62) < 0.05 and 0.08 < dd < 0.36:
                return rrp, 0.04
            if rr % 1.0 < 0.24:
                return rrp, 0.16 + (0.08 if dd < 0.2 else 0)
            return irp, 0.74 - dd * 0.55 + (nz(int(u * 48), int(v * 48), seed + 1) - 0.5) * 0.08
        val = 0.55 + bark_side(face, u, v) + (nz(int(u * 48), int(v * 48), seed + 7) - 0.5) * 0.10
        # knot on the left face
        if face == 'left' and math.hypot((u - 0.62) * 1.0, (v - 0.42) * 1.4) < 0.09:
            k = math.hypot((u - 0.62), (v - 0.42) * 1.4)
            return (rrp, 0.15) if k < 0.04 else (brp, 0.25)
        # top lip: the sides catch light just under the top edge (bark overhang)
        if v < 0.05:
            val += 0.12
        return brp, val
    return t


# ---------------------------------------------------------------- catalogue
# (file id, display name, group, status, enchanted id, vanilla base id(s), draw)
def _ing(k, s):
    return lambda cv: ingot(cv, k, s)


def _log(k, s):
    return lambda cv: cube(cv, tex_log(k, s))


ITEMS = [
    # Mining - section 4.1 launch set + Rubble (Skyy 2026-10-06) + Mithril (staged, phase G)
    ('cobblestone', 'Enchanted Cobblestone', 'Mining', 'LAUNCH (v1 art)', 'Skyy_Ench_Cobblestone', 'Rock_Stone_Cobble',
     lambda cv: cube(cv, V1.tex_cobble(7))),
    ('rubble', 'Enchanted Rubble', 'Mining', 'NEW (v1 art)', 'Skyy_Ench_Rubble', 'Rubble_* (17 kinds)', V1.d_rubble),
    ('copper-ingot', 'Enchanted Copper Ingot', 'Mining', 'LAUNCH', 'Skyy_Ench_Copper', 'Ingredient_Bar_Copper', _ing('copper', 501)),
    ('iron-ingot', 'Enchanted Iron Ingot', 'Mining', 'LAUNCH', 'Skyy_Ench_Iron', 'Ingredient_Bar_Iron', _ing('iron', 502)),
    ('thorium-ingot', 'Enchanted Thorium Ingot', 'Mining', 'LAUNCH', 'Skyy_Ench_Thorium', 'Ingredient_Bar_Thorium', _ing('thorium', 503)),
    ('cobalt-ingot', 'Enchanted Cobalt Ingot', 'Mining', 'LAUNCH', 'Skyy_Ench_Cobalt', 'Ingredient_Bar_Cobalt', _ing('cobalt', 504)),
    ('adamantite-ingot', 'Enchanted Adamantite Ingot', 'Mining', 'LAUNCH', 'Skyy_Ench_Adamantite', 'Ingredient_Bar_Adamantite',
     _ing('adamantite', 505)),
    ('mithril-ingot', 'Enchanted Mithril Ingot', 'Mining', 'STAGED (phase G)', 'Skyy_Ench_Mithril', 'Ingredient_Bar_Mithril',
     _ing('mithril', 506)),
    # Foraging - the 5 key logs (one per tree tier)
    ('oak-log', 'Enchanted Oak Log', 'Foraging', 'LAUNCH', 'Skyy_Ench_Oak', 'Wood_Oak_Trunk', _log('oak', 601)),
    ('maple-log', 'Enchanted Maple Log', 'Foraging', 'LAUNCH', 'Skyy_Ench_Maple', 'Wood_Maple_Trunk', _log('maple', 602)),
    ('gumboab-log', 'Enchanted Gumboab Log', 'Foraging', 'LAUNCH', 'Skyy_Ench_Gumboab', 'Wood_Gumboab_Trunk', _log('gumboab', 603)),
    ('redwood-log', 'Enchanted Redwood Log', 'Foraging', 'LAUNCH', 'Skyy_Ench_Redwood', 'Wood_Redwood_Trunk', _log('redwood', 604)),
    ('sallow-log', 'Enchanted Sallow Log', 'Foraging', 'LAUNCH', 'Skyy_Ench_Sallow', 'Wood_Sallow_Trunk', _log('sallow', 605)),
    # Farming - the 7 key crops (v1 art, approved)
    ('wheat', 'Enchanted Wheat', 'Farming', 'LAUNCH (v1 art)', 'Skyy_Ench_Wheat', 'Plant_Crop_Wheat_Item', V1.d_wheat),
    ('carrot', 'Enchanted Carrot', 'Farming', 'LAUNCH (v1 art)', 'Skyy_Ench_Carrot', 'Plant_Crop_Carrot_Item', V1.d_carrot),
    ('cauliflower', 'Enchanted Cauliflower', 'Farming', 'LAUNCH (v1 art)', 'Skyy_Ench_Cauliflower', 'Plant_Crop_Cauliflower_Item',
     V1.d_cauliflower),
    ('pumpkin', 'Enchanted Pumpkin', 'Farming', 'LAUNCH (v1 art)', 'Skyy_Ench_Pumpkin', 'Plant_Crop_Pumpkin_Item', V1.d_pumpkin),
    ('tomato', 'Enchanted Tomato', 'Farming', 'LAUNCH (v1 art)', 'Skyy_Ench_Tomato', 'Plant_Crop_Tomato_Item', V1.d_tomato),
    ('cotton', 'Enchanted Cotton', 'Farming', 'LAUNCH (v1 art)', 'Skyy_Ench_Cotton', 'Plant_Crop_Cotton_Item', V1.d_cotton),
    ('potato', 'Enchanted Potato', 'Farming', 'LAUNCH (v1 art)', 'Skyy_Ench_Potato', 'Plant_Crop_Potato_Item', V1.d_potato),
    # Approved by Skyy, kept for later (not in the section 4.1 launch set)
    ('sap', 'Enchanted Tree Sap', 'Later', 'LATER (v1 art)', 'Skyy_Ench_Sap ?', 'Ingredient_Tree_Sap', V1.d_sap),
    ('stick', 'Enchanted Stick', 'Later', 'LATER (v1 art)', 'Skyy_Ench_Stick ?', 'Ingredient_Stick', V1.d_stick),
    ('lettuce', 'Enchanted Lettuce', 'Later', 'LATER (v1 art)', 'Skyy_Ench_Lettuce', 'Plant_Crop_Lettuce_Item', V1.d_lettuce),
    ('corn', 'Enchanted Corn', 'Later', 'LATER (v1 art)', 'Skyy_Ench_Corn', 'Plant_Crop_Corn_Item', V1.d_corn),
    ('turnip', 'Enchanted Turnip', 'Later', 'LATER (v1 art)', 'Skyy_Ench_Turnip', 'Plant_Crop_Turnip_Item', V1.d_turnip),
    ('aubergine', 'Enchanted Aubergine', 'Later', 'LATER (v1 art)', 'Skyy_Ench_Aubergine', 'Plant_Crop_Aubergine_Item', V1.d_aubergine),
    ('chilli', 'Enchanted Chilli', 'Later', 'LATER (v1 art)', 'Skyy_Ench_Chilli', 'Plant_Crop_Chilli_Item', V1.d_chilli),
    ('rice', 'Enchanted Rice', 'Later', 'LATER (v1 art)', 'Skyy_Ench_Rice', 'Plant_Crop_Rice_Item', V1.d_rice),
    ('onion', 'Enchanted Onion', 'Later', 'LATER (v1 art)', 'Skyy_Ench_Onion', 'Plant_Crop_Onion_Item', V1.d_onion),
]

# ================================================================ v2 rest (2026-10-08)
# The v1 items that were not yet in v2, each redrawn as a shiny copy of a REAL
# vanilla resource (ids from the repo's live build scripts; UNVERIFIED vs Assets.zip).
# Nothing above this line changed, so the first 29 icons keep their bytes.
METALS.update({
    'onyxium': ('#5a3a8c', '#f2cf72'),     # purple bar, gold sheen (Onyxium = purple / gold)
    'silver': ('#c3ccd8', '#ffffff'),      # cooler and brighter than iron
    'gold': ('#e2ae2c', '#fff2b4'),
})


def tex_stonecob(seed, cols, mortar, stretch=1.0, n=4, grain=None):
    """Cobble of one stone kind: Voronoi stones with a lit upper-left rim, a
    shaded lower-right rim and a recessed mortar line; grain(u, v, i) adds the
    stone's own pattern (strata, vesicles, cleavage)."""
    rps = [ramp(c, 7, dark=0.6, light=0.42) for c in cols]
    mrp = ramp(mortar, 6)
    pts = [((i % n + 0.15 + nz(i, 1, seed) * 0.7) / n, (i // n + 0.15 + nz(i, 2, seed) * 0.7) / n) for i in range(n * n)]

    def t(face, u, v):
        best = []
        for i, (px, py) in enumerate(pts):
            du = min(abs(u - px), 1 - abs(u - px)) / stretch
            dv = min(abs(v - py), 1 - abs(v - py))
            best.append((du * du + dv * dv, i))
        best.sort()
        d1, i1 = best[0]
        gap = math.sqrt(best[1][0]) - math.sqrt(d1)
        if gap < 0.028:
            return mrp, 0.10 + (nz(int(u * 64), int(v * 64), seed + 5) - 0.5) * 0.12
        px, py = pts[i1]
        val = 0.58 - (u - px) * 1.3 - (v - py) * 1.3
        if gap < 0.06:                      # rim: lit toward the light, dark away from it
            val += 0.16 if (u - px) + (v - py) < 0 else -0.16
        val += (nz(int(u * 48), int(v * 48), seed + i1) - 0.5) * 0.14
        val += (vnoise(u * 40, v * 40, 3, seed + 11) - 0.5) * 0.12
        if grain:
            val += grain(u, v, i1)
        return rps[i1 % len(rps)], val
    return t


def g_sandstone(u, v, i):
    # thin horizontal strata through each stone
    s = math.sin((v * 34 + u * 3 + i * 0.7) + vnoise(u * 20, v * 20, 4, 77) * 2.2)
    return -0.14 if s > 0.78 else (0.07 if s < -0.6 else 0)


def g_slate(u, v, i):
    # flat cleavage plates: sharp horizontal splits and a dull sheen
    s = (v * 18 + nz(int(u * 6), i, 61) * 0.6) % 1.0
    return -0.20 if s < 0.10 else (0.06 if s > 0.85 else 0)


def g_basalt(u, v, i):
    # gas vesicles (little pits) in dark rock
    k = nz(int(u * 30), int(v * 30), 71 + i)
    return -0.32 if k < 0.06 else (0.12 if k > 0.97 else 0)


def tex_sand(seed):
    rp = ramp('#dcc386', 7, light=0.3)
    dk = ramp('#9a8156', 5)

    def t(face, u, v):
        g = (nz(int(u * 64), int(v * 64), seed) - 0.5) * 0.30
        if face == 'top':
            # wind ripples across the top
            r = math.sin((u * 1.0 + v * 0.35) * 2 * PI * 5 + vnoise(u * 18, v * 18, 3, seed + 1) * 2.5)
            val = 0.58 + (0.10 if r > 0.55 else -0.10 if r < -0.65 else 0) + g
        else:
            val = 0.55 - v * 0.12 + g
            if v > 0.86 and nz(int(u * 30), 3, seed) < 0.5:      # slumped grains at the foot
                val -= 0.08
        k = nz(int(u * 64), int(v * 64), seed + 9)
        if k < 0.03:
            return dk, 0.35                  # dark grains
        if k > 0.985:
            return rp, 0.98                  # glittering quartz grains
        return rp, val
    return t


def tex_clay(seed):
    rp = ramp('#a9705a', 7, dark=0.55, light=0.35)

    def t(face, u, v):
        g = (vnoise(u * 50, v * 50, 6, seed) - 0.5) * 0.22 + (nz(int(u * 64), int(v * 64), seed) - 0.5) * 0.06
        val = 0.55 + g
        # drying cracks: thin dark lines along a coarse Voronoi
        cells = [((i % 3 + 0.2 + nz(i, 1, seed + 3) * 0.6) / 3, (i // 3 + 0.2 + nz(i, 2, seed + 3) * 0.6) / 3) for i in range(9)]
        ds = sorted((min(abs(u - px), 1 - abs(u - px)) ** 2 + min(abs(v - py), 1 - abs(v - py)) ** 2) for px, py in cells)
        gap = math.sqrt(ds[1]) - math.sqrt(ds[0])
        lim = 0.020 if face == 'top' else 0.014
        if gap < lim:
            return rp, 0.08
        if gap < lim + 0.016:
            val += 0.10                       # raised lip beside each crack
        # smooth wet sheen on the top
        if face == 'top':
            val += math.exp(-(((u - 0.35) ** 2 + (v - 0.3) ** 2) / 0.03)) * 0.18
        # tool smears on the sides
        if face != 'top' and math.sin(v * 40 + u * 6 + vnoise(u * 12, v * 12, 3, seed) * 3) > 0.9:
            val -= 0.08
        return rp, val
    return t


def stone_block(tex):
    return lambda cv: cube(cv, tex)


# ---- more logs (same cube as the key logs, own bark per species)
LOGS2 = {
    # key: (bark, inner wood, ring, style)
    'birch': ('#e6e1d4', '#e8d2a2', '#c3a46c', 'birch'),
    'ash': ('#7a7266', '#d8bf8c', '#a98c5c', 'ash'),
    'azure': ('#3f5f9e', '#a9c4e8', '#6d8ec4', 'azure'),
    'crystal': ('#584c74', '#d8d2f2', '#9c8fc8', 'crystal'),
}


def tex_log2(key, seed):
    bark, inner, ring, style = LOGS2[key]
    LOGS['_tmp_' + key] = (bark, inner, ring, 'plates')
    base = tex_log('_tmp_' + key, seed)       # reuses the key-log top (rings, pith, check crack)
    del LOGS['_tmp_' + key]
    brp = ramp(bark, 7, dark=0.62, light=0.40)
    blk = ramp('#2b2724', 5)
    cyan = ramp('#7fe6f0', 6, light=0.5)

    def side(face, u, v):
        n1 = vnoise(u * 24, v * 24, 3, seed)
        if style == 'birch':
            # white bark, black horizontal lenticel dashes (2 px tall), dark scars
            row = int(v * 9)
            fv = v * 9 - row
            seg = u * 4 + nz(row, 1, seed) * 3
            k = nz(int(seg), row, seed)
            fs = seg - int(seg)
            if k < 0.55 and 0.38 < fv < 0.62 and fs < 0.55 + k * 0.4:
                return blk, 0.22 + (0.15 if fv < 0.48 else 0)
            if face == 'left' and math.hypot(u - 0.3, (v - 0.70) * 1.6) < 0.08:
                return blk, 0.12             # eye-shaped scar
            return brp, 0.64 + (n1 - 0.5) * 0.14 - (0.10 if 0.62 <= fv < 0.70 else 0)
        if style == 'ash':
            # interlacing diamond ridges (corky, regular), wider than Sallow's
            a = (u * 3.5 + v * 1.6 + n1 * 0.25) % 1.0
            b = (u * 3.5 - v * 1.6 + n1 * 0.25) % 1.0
            if a < 0.12 or b < 0.12:
                return brp, 0.22
            ridge = min(a, b)
            return brp, 0.50 + (0.16 if ridge < 0.22 else 0.02) + (n1 - 0.5) * 0.08
        if style == 'azure':
            # smooth blue bark with pale vertical streaks and rings of lenticels
            g = math.sin(u * 2 * PI * 7 + vnoise(u * 8, v * 30, 4, seed) * 2.5)
            val = 0.55 + (0.14 if g > 0.8 else -0.18 if g < -0.82 else 0) + (n1 - 0.5) * 0.12
            if abs(((v * 5) % 1.0) - 0.5) < 0.04 and nz(int(u * 20), int(v * 5), seed) < 0.5:
                val -= 0.2
            return brp, val
        # crystal: dark violet bark with glowing cyan veins
        vein = abs(math.sin(u * 2 * PI * 2.2 + v * 5 + vnoise(u * 14, v * 14, 4, seed + 5) * 4))
        if vein < 0.07:
            return cyan, 0.7 + (nz(int(u * 40), int(v * 40), seed) - 0.5) * 0.3
        g = math.sin(u * 2 * PI * 10 + n1 * 3)
        return brp, 0.52 + (-0.22 if g > 0.75 else 0.06) + (n1 - 0.5) * 0.1

    def t(face, u, v):
        if face == 'top':
            if style == 'crystal' and min(u, v, 1 - u, 1 - v) >= 0.11 and math.hypot(u - 0.5, v - 0.5) < 0.06:
                return cyan, 0.85                # glowing crystal core instead of plain pith
            return base(face, u, v)
        rpv = side(face, u, v)
        val = rpv[1] + (nz(int(u * 48), int(v * 48), seed + 7) - 0.5) * 0.08
        if v < 0.05:
            val += 0.10
        return rpv[0], val
    return t


def crystal_shards(cv, pts, seed):
    """small cyan prisms growing out of the crystal log (left lit, right shaded)"""
    rp = ramp('#62d8ea', 7, light=0.55)
    for k, (bx, by, h, lean) in enumerate(pts):
        tip = (bx + lean, by - h)
        w = 2.5 + h * 0.12
        left = poly(cv, [(bx - w, by), tip, (bx + 0.5, by + 1.5)])
        right = poly(cv, [(bx + 0.5, by + 1.5), tip, (bx + w + 0.5, by)]) - left
        shade(cv, left, rp, 'flat', v=0.80, bevel=0.0, outline=False)
        shade(cv, right, rp, 'flat', v=0.42, bevel=0.0, outline=False)
        for (x, y) in edge(left | right):
            cv.put(x, y, rp['o'])
        cv.put(int(tip[0]), int(tip[1]) + 1, rp['f'][6])


def d_crystal_log(cv):
    cube(cv, tex_log2('crystal', 609))
    crystal_shards(cv, [(13, 30, 11, -2), (19, 29, 7, 1), (46, 31, 10, 2), (52, 33, 6, 1), (40, 46, 8, 0)], 609)


# ---- Fibre: a tied bundle of plant fibre lying on the diagonal
def d_fibre(cv, seed=811):
    cols = [ramp(c, 6, light=0.35) for c in ('#c9b27a', '#b7a868', '#d6c38e', '#a99a5c')]
    ang = -PI / 4
    ux, uy = math.cos(ang), math.sin(ang)
    nx_, ny_ = -uy, ux
    cx, cy = 31, 34
    strands = []
    for i in range(15):
        off = (i - 7) * 1.5
        L1 = 23 + nz(i, 1, seed) * 5          # toward the top-right
        L2 = 23 + nz(i, 2, seed) * 4          # toward the bottom-left
        spread1 = off * 1.7            # ends fan out wider than the waist
        spread2 = off * 1.15
        bend = (nz(i, 3, seed) - 0.5) * 3
        p0 = (cx - ux * L2 + nx_ * spread2, cy - uy * L2 + ny_ * spread2)
        pm = (cx + nx_ * off * 0.45, cy + ny_ * off * 0.45)
        p1 = (cx + ux * L1 + nx_ * (spread1 + bend), cy + uy * L1 + ny_ * (spread1 + bend))
        strands.append((i, [p0, ((p0[0] + pm[0]) / 2 + nx_ * bend * 0.5, (p0[1] + pm[1]) / 2 + ny_ * bend * 0.5), pm,
                            ((pm[0] + p1[0]) / 2, (pm[1] + p1[1]) / 2), p1]))
    allm = set()
    order = sorted(strands, key=lambda s: -abs(s[0] - 7))   # outer strands behind, middle in front
    for i, pts in order:
        m = thick(cv, pts, 3 if i % 3 else 4)
        rp = cols[i % 4]
        side = (i - 7) / 7.0
        shade(cv, m, rp, 'flat', v=0.62 - side * 0.18, bevel=0.0, outline=False,
              tex=lambda x, y, i=i: (nz(x, y, seed + i) - 0.5) * 0.18)
        # dark crease on one side of each strand so they read separately
        for (x, y) in edge(m):
            if (x + 1, y + 1) not in m:
                cv.put(x, y, rp['f'][1])
        allm |= m
    # frayed tips: a few split ends
    for i, pts in strands:
        if i % 2 == 0:
            ex, ey = pts[-1]
            cv.put(int(ex + ux * 2), int(ey + uy * 2), cols[i % 4]['f'][3]); allm.add((int(ex + ux * 2), int(ey + uy * 2)))
    # the tie: three wraps of twisted fibre around the waist
    tie_rp = ramp('#7a5a34', 6)
    for k in (-2.6, 0, 2.6):
        a = (cx + ux * k - nx_ * 12, cy + uy * k - ny_ * 12)
        b = (cx + ux * k + nx_ * 12, cy + uy * k + ny_ * 12)
        m = thick(cv, [a, b], 2.6)
        shade(cv, m, tie_rp, 'cyl', x0=cx + ux * k, y0=cy + uy * k, ang=ang + PI / 2, r=12,
              tex=lambda x, y: -0.22 if (x - y) % 3 == 0 else 0, bevel=0.0, outline=False)
        allm |= m
    knot = ell(cv, cx + nx_ * 10 + 1, cy + ny_ * 10, 2.6, 2.2)
    shade(cv, knot, tie_rp, 'sphere', cx=cx + nx_ * 10 + 1, cy=cy + ny_ * 10, rx=2.6, ry=2.2, outline=False)
    allm |= knot
    tail = thick(cv, [(cx + nx_ * 10 + 2, cy + ny_ * 10 + 2), (cx + nx_ * 10 + 4, cy + ny_ * 10 + 6)], 1.5)
    shade(cv, tail, tie_rp, 'flat', v=0.5, bevel=0, outline=False)
    allm |= tail
    for p in edge(allm):
        cv.put(p[0], p[1], ramp('#8a7448', 6)['o'])
    return allm


# ---- Bundle of Hay (Plant_Hay_Bundle): straw block, two twine bands, stray straws
def tex_hay2(seed=17):
    rp = ramp('#d8b24e', 7, light=0.35)
    tw = ramp('#8a5a32', 6)

    def band(x):
        return abs(x - 0.27) < 0.055 or abs(x - 0.73) < 0.055

    def t(face, u, v):
        if face == 'top':
            if band(u):
                tw_v = 0.55 + (0.15 if int(v * 30) % 2 else -0.1)
                return tw, tw_v
            # cut straw ends: many tiny tubes, light rims with dark holes
            k = nz(int(u * 40), int(v * 40), seed)
            return rp, 0.58 + (k - 0.5) * 0.5 - (0.25 if k < 0.08 else 0)
        if band(u):
            return tw, 0.55 + (0.15 if int((v * 28 + u * 10)) % 2 else -0.1) - abs(v - 0.5) * 0.2
        s = math.sin(v * 2 * PI * 13 + vnoise(u * 30, v * 30, 2, seed) * 5 + u * 3)
        k = nz(int(u * 48), int(v * 48), seed + 3)
        val = 0.56 + (0.18 if s > 0.6 else -0.20 if s < -0.7 else 0) + (k - 0.5) * 0.12
        if abs(u - 0.27) < 0.09 or abs(u - 0.73) < 0.09:
            val -= 0.12                        # straw pinched in beside the twine
        return rp, val
    return t


def d_hay(cv, seed=17):
    m = cube(cv, tex_hay2(seed))
    rp = ramp('#e2c060', 6)
    straws = [((5, 22), (1, 19)), ((4, 34), (0, 36)), ((59, 21), (63, 18)), ((60, 30), (63, 31)), ((24, 6), (21, 2)),
              ((40, 6), (44, 2)), ((14, 52), (11, 56)), ((50, 52), (54, 55)), ((33, 62), (35, 63))]
    for (a, b) in straws:
        s = thick(cv, [a, b], 1)
        for (x, y) in s:
            if (x, y) not in m:
                cv.put(x, y, rp['f'][4] if (x + y) % 2 else rp['f'][2])
    return m


ITEMS_REST = [
    # Mining: the other metal bars (Ingredient_Bar_*); the v1 ore chunks became ingots
    ('onyxium-ingot', 'Enchanted Onyxium Ingot', 'RestMining', 'LATER (new)', 'Skyy_Ench_Onyxium ?', 'Ingredient_Bar_Onyxium',
     _ing('onyxium', 507)),
    ('silver-ingot', 'Enchanted Silver Ingot', 'RestMining', 'LATER (new)', 'Skyy_Ench_Silver ?', 'Ingredient_Bar_Silver',
     _ing('silver', 508)),
    ('gold-ingot', 'Enchanted Gold Ingot', 'RestMining', 'LATER (new)', 'Skyy_Ench_Gold ?', 'Ingredient_Bar_Gold', _ing('gold', 509)),
    # Mining: the v1 stones, as the real blocks / cobble you mine (stone groups S2-S4)
    ('sand', 'Enchanted Sand', 'RestMining', 'OPTION (new)', 'Skyy_Ench_Sand ?', 'Soil_Sand', stone_block(tex_sand(331))),
    ('clay', 'Enchanted Clay', 'RestMining', 'OPTION (new)', 'Skyy_Ench_Clay ?', 'Soil_Clay', stone_block(tex_clay(341))),
    ('sandstone', 'Enchanted Sandstone', 'RestMining', 'OPTION (new)', 'Skyy_Ench_Sandstone ?', 'Rock_Sandstone_Cobble',
     stone_block(tex_stonecob(351, ['#d9b47a', '#cfa66a', '#e2c18c'], '#8c6a42', 1.0, 4, g_sandstone))),
    ('slate', 'Enchanted Slate', 'RestMining', 'OPTION (new)', 'Skyy_Ench_Slate ?', 'Rock_Slate_Cobble',
     stone_block(tex_stonecob(361, ['#5f6a7a', '#566070', '#6b7686'], '#2c323c', 2.2, 4, g_slate))),
    ('basalt', 'Enchanted Basalt', 'RestMining', 'OPTION (new)', 'Skyy_Ench_Basalt ?', 'Rock_Basalt_Cobble',
     stone_block(tex_stonecob(371, ['#4a4a52', '#424249', '#55555e'], '#1f1f25', 1.0, 3, g_basalt))),
    # Foraging: the v1 made-up woods, as the real logs closest to them
    ('birch-log', 'Enchanted Birch Log', 'RestForaging', 'LATER (new)', 'Skyy_Ench_Birch ?', 'Wood_Birch_Trunk',
     lambda cv: cube(cv, tex_log2('birch', 606))),
    ('ash-log', 'Enchanted Ash Log', 'RestForaging', 'LATER (new)', 'Skyy_Ench_Ash ?', 'Wood_Ash_Trunk',
     lambda cv: cube(cv, tex_log2('ash', 607))),
    ('azure-log', 'Enchanted Azure Log', 'RestForaging', 'LATER (new)', 'Skyy_Ench_Azure', 'Wood_Azure_Trunk',
     lambda cv: cube(cv, tex_log2('azure', 608))),
    ('crystal-log', 'Enchanted Crystal Log', 'RestForaging', 'LATER (new)', 'Skyy_Ench_Crystal ?', 'Wood_Crystal_Trunk', d_crystal_log),
    ('fibre', 'Enchanted Fibre', 'RestForaging', 'LATER (new)', 'Skyy_Ench_Fibre ?', 'Ingredient_Fibre', d_fibre),
    # Farming: the v1 Hay Bale, as the real Bundle of Hay
    ('hay-bundle', 'Enchanted Hay Bundle', 'RestForaging', 'OPTION (new)', 'Skyy_Ench_Hay ?', 'Plant_Hay_Bundle', d_hay),
]
ITEMS.extend(ITEMS_REST)


GROUPS = [
    ('Mining', 'MINING - Cobblestone + Rubble + ingots (100 base = 1 Enchanted)'),
    ('Foraging', 'FORAGING - the key log of each tree tier (a log is a block)'),
    ('Farming', 'FARMING - the key crop of each Farmer\'s Workbench pair'),
    ('Later', 'APPROVED ART, NOT IN THE LAUNCH SET (kept for later, same generator)'),
    ('RestMining', 'THE REST OF v1, MINING (2026-10-08) - other metal bars + the stones as the real blocks / cobble'),
    ('RestForaging', 'THE REST OF v1, FORAGING + FARMING (2026-10-08) - the v1 woods as real logs, Fibre, Bundle of Hay'),
]


def build():
    out_dir = os.path.join(HERE, 'icons-v2')
    os.makedirs(out_dir, exist_ok=True)
    rendered = []
    for e in ITEMS:
        b = Cv(64, 64)
        e[6](b)
        g = Cv(64, 64)
        g.c = [row[:] for row in b.c]
        glint(g)                      # the v1 recipe, unchanged
        g.img().save(os.path.join(out_dir, 'ench-%s.png' % e[0]), optimize=True)
        rendered.append((e, b.img(), g.img()))
    sheet(rendered)
    print('icons:', len(rendered))


BG, SLOT, SLOT_E = V1.BG, V1.SLOT, V1.SLOT_E
TXT, SUB, GOLD = V1.TXT, V1.SUB, V1.GOLD
STATUS_COL = {'LAUNCH': (120, 210, 130), 'NEW': (120, 200, 240), 'STAGED': (232, 169, 59), 'LATER': (160, 160, 175), 'OPTION': (214, 150, 220)}


def sheet(rendered):
    S = 3
    cw, ch = 64 * S + 58, 64 * S + 136
    cols = 9
    head = 126
    rows = []
    for g, title in GROUPS:
        items = [r for r in rendered if r[0][2] == g]
        rows.append((title, [items[i:i + cols] for i in range(0, len(items), cols)]))
    nrows = sum(len(r[1]) for r in rows)
    Wd = cols * cw + 40
    Hd = head + nrows * ch + len(rows) * 42 + 20
    im = Image.new('RGBA', (Wd, Hd), BG + (255,))
    d = ImageDraw.Draw(im)
    d.text((20, 14), 'SkyWynn - Enchanted materials v2 (shiny copies of the vanilla resources, 64 x 64)', fill=GOLD, font=font(26))
    d.text((20, 52), 'Big = 3x with the baked glint (same recipe as v1).  Under it at 1x: plain base (left), enchanted (right).  '
           'Ingots + log blocks are new; Cobblestone block, Rubble, Sap, Stick and crops are the approved v1 art.',
           fill=SUB, font=font(15, False))
    d.text((20, 74), 'Ids from research/Gathering-Progression-Spec.md section 4.  Colours of bars / logs = guesses, '
           'UNVERIFIED until compared with Assets.zip.  research/cloud/enchanted-art/make_enchanted_v2.py',
           fill=SUB, font=font(15, False))
    d.text((20, 96), '2026-10-08: the rest of v1 redrawn as real vanilla resources (last two groups). Ids marked ? are suggestions; '
           'OPTION = Skyy decides if it gets an Enchanted form at all.  Metal / wood blocks: none (see README 7).',
           fill=SUB, font=font(15, False))
    y = head
    for title, chunks in rows:
        d.text((20, y + 6), title, fill=(180, 200, 201), font=font(19))
        d.line([(20, y + 32), (Wd - 20, y + 32)], fill=(94, 81, 44), width=2)
        y += 42
        for chunk in chunks:
            for i, (e, bimg, gimg) in enumerate(chunk):
                x = 20 + i * cw
                d.rectangle([x, y, x + 64 * S + 16, y + 64 * S + 16], fill=SLOT, outline=SLOT_E, width=2)
                im.alpha_composite(gimg.resize((64 * S, 64 * S), Image.NEAREST), (x + 8, y + 8))
                yy = y + 64 * S + 22
                d.rectangle([x, yy, x + 66, yy + 66], fill=SLOT, outline=SLOT_E)
                im.alpha_composite(bimg, (x + 1, yy + 1))
                d.rectangle([x + 72, yy, x + 138, yy + 66], fill=SLOT, outline=SLOT_E)
                im.alpha_composite(gimg, (x + 73, yy + 1))
                name = e[1].replace('Enchanted ', 'Enchanted\n', 1)
                if len(name.split('\n')[1]) > 12:
                    a, b = name.split('\n')[1].rsplit(' ', 1)
                    name = 'Enchanted\n%s\n%s' % (a, b)
                d.multiline_text((x + 146, yy + 2), name, fill=TXT, font=font(12), spacing=2)
                st = e[3]
                d.text((x, yy + 72), st, fill=STATUS_COL[st.split(' ')[0]], font=font(11))
                d.text((x, yy + 87), e[4], fill=TXT, font=font(11, False))
                d.text((x, yy + 101), 'from ' + e[5], fill=SUB, font=font(11, False))
            y += ch
    im.convert('RGB').save(os.path.join(HERE, 'enchanted-sheet-v2.png'), optimize=True)


if __name__ == '__main__':
    build()
