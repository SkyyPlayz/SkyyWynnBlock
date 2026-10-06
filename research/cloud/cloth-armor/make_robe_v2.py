#!/usr/bin/env python3
"""SkyWynn Cloth tier 1 - Crude Robe, v2 detail pass (cloud draft 2026-10-06).

Original pixel art, drawn from code (no copied art, no game files).
Run:  python3 research/cloud/cloth-armor/make_robe_v2.py
Writes the *-v2.png files next to this script. Deterministic: same code -> same bytes.
The v1 script (make_robe.py) and its PNGs are left as they are.

Same approved design as v1 ("Both good", Skyy 2026-10-06), redrawn at 2x with the v2 painter of
research/cloud/light-armor/make_sheets_v2.py (imported, never changed):
  * 128 x 192 figure grid (v1 64 x 84): every v1 part keeps its place, v1 (x, y) -> v2 (2x, 2y + DY);
  * 7-step ramps, whole-part gradient lit top-left, 2-px bevel, 1-px dark outline;
  * hand-woven fibre: plain weave, slubs, dye mottling, soft cloth folds, frayed + tattered hems;
  * twisted rope (3-strand twist with lit crowns), wrapped fibre bindings, stitched rune trims;
  * faceted green crystal shards (lit facet, shaded facet, bright crown, glint) with a soft glow halo.
"""
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'light-armor'))
import make_sheets as ms  # noqa: E402  (ramp / font / colours only)
import make_sheets_v2 as v2  # noqa: E402  (painter + masks)
from PIL import Image, ImageDraw  # noqa: E402

from make_sheets_v2 import (rect, ell, poly, line, R, E, P, pv, Y, mirror, S, MX, clip, erode, dil,  # noqa: E402
                            ring, bottom_rim, top_rim, chain, Fig, hsh, mix, ramp7, W, H)

SET_SCALE, SHEET_SCALE, CHEST_SCALE = 4, 3, 4
BG, INK = v2.BG, v2.INK
SUB = (60, 64, 70, 255)

# ---------------------------------------------------------------- palettes (v1 colours -> 7 steps)
ROBE = ramp7(ms.ramp('#0f2414', '#2a5c31', '#3b7a42', '#519a55', '#72bb6e'))      # dyed green fibre
CLOAK = ramp7(ms.ramp('#10180a', '#273a17', '#364f20', '#48662a', '#5f803a'))     # moss-green cloak + mantle
LINING = ramp7(ms.ramp('#070d08', '#0f1c11', '#152718', '#1c321f', '#243d27'))    # hood lining / deep shadow
FIBRE = ramp7(ms.ramp('#3b3220', '#7a6a46', '#9a8a5e', '#b8a87a', '#d6c89c'))     # undyed fibre trims, wraps
ROPE = ramp7(ms.ramp('#33260f', '#6e5428', '#957238', '#b8924c', '#d8b46c'))      # rope belt + cords
CRYSTAL = ramp7(ms.ramp('#0b3320', '#178a4a', '#2fc46a', '#7cf0a0', '#d4ffe2'))   # green crystal
GLOW = ms.hx('#eafff0')
HALO = (120, 255, 170)
DUMMY = v2.DUMMY
FACE = v2.FACE
RUNE_INK = ms.hx('#4a3f26')        # dark stitched runes on the fibre trims
SEAM_G = ms.hx('#1d4423')          # seam stitches on the green robe


# ---------------------------------------------------------------- textures
def weave(seed=0, amt=1.0, folds=None):
    """hand-woven fibre: plain weave, horizontal slubs, dye mottling; optional cloth folds"""
    def f(x, y, L):
        L += (0.07 if ((x // 2) + (y // 2)) % 2 else -0.06) * amt          # plain weave (2 x 2 over-under)
        if x % 6 == 0 and hsh(x, y // 3, seed + 4) < 0.6:
            L -= 0.07 * amt                                                 # warp threads
        L += (hsh(x // 7, y // 5, seed) - 0.5) * 0.16 * amt                # uneven dye
        h = hsh(x // 4, y, seed + 1)
        if h > 0.94:
            L += 0.13 * amt                                                 # thick slub thread
        elif h < 0.05:
            L -= 0.13 * amt                                                 # thin / pulled thread
        if hsh(x, y, seed + 2) < 0.03:
            L -= 0.15
        if folds:
            L += folds(x, y)
        return L
    return f


def skirt_folds(cx, y0):
    """soft vertical folds that widen towards the hem"""
    def g(x, y):
        k = 4.0 + max(0, y - y0) * 0.045
        s = math.sin((x - cx) / k * 1.15 + 0.6)
        return 0.16 * s if s > -0.6 else 0.16 * s - 0.08
    return g


def rope_tex(x, y, L):
    """3-strand twist: diagonal strands, lit crown, dark groove"""
    u = (x + y) % 5
    return {0: 0.95, 1: 0.70, 2: 0.50, 3: 0.30, 4: -0.02}[u] + (L - 0.5) * 0.4


def rope_v(x, y, L):
    u = (y - x) % 4
    return {0: 0.9, 1: 0.6, 2: 0.35, 3: 0.0}[u] + (L - 0.5) * 0.3


def wraps(P_=3, seed=0):
    """fibre wrapping: diagonal bands of wound twine"""
    def f(x, y, L):
        u = (x + 2 * y) % (P_ * 2)
        if u == 0:
            return 0.05
        if u == 1:
            return L + 0.24
        return L + (hsh(x, y, seed) - 0.5) * 0.1
    return f


# ---------------------------------------------------------------- details
RUNES = [["#...#", ".#.#.", "..#..", ".#.#.", "#...#"],
         ["###..", "#..#.", "###..", "#..#.", "###.."],
         ["..#..", "#.#.#", ".###.", "..#..", "..#.."],
         ["#....", "##...", "#.#..", "#..#.", "#...#"],
         ["..#..", ".#.#.", "#...#", ".#.#.", "..#.."],
         ["#.#..", "#.#..", "###..", "..#..", "..#.."]]


def rune_band(f, x0, x1, y0, step=5):
    """a v1 5-px tall fibre trim (10 px in v2): lit top cord, woven body, stitched runes, dark lower cord"""
    band = R(x0, y0, x1, y0 + 4)
    top, bot = Y(y0), Y(y0 + 4) + 1

    def tex(x, y, L):
        if y == top + 1 or y == top + 2:
            return rope_tex(x, y, L) * 0.8 + 0.2
        if y == bot - 1 or y == bot - 2:
            return rope_tex(x, y, L) * 0.7
        return L + (0.04 if (x + y) % 2 else -0.04)
    f.paint(band, FIBRE, kind='trim', tex=tex, grad=0.15)
    k = 0
    for gx in range(2 * x0 + 4, 2 * x1 - 4, 2 * step):
        g = RUNES[(k * 3 + gx) % len(RUNES)]
        for dy, row in enumerate(g):
            for dx, ch in enumerate(row):
                if ch == '#' and (gx + dx, top + 3 + dy) in band:
                    f.put(gx + dx, top + 3 + dy, RUNE_INK, 'trim')
        k += 1


def rune_strip(f, x0, y0, y1, side):
    """a vertical fibre trim (v1 3 px -> 6 px) with a stitched cross every 8 rows"""
    m = S(R(x0, y0, x0 + 2, y1), side)
    xs = sorted({x for x, _ in m})
    xa = xs[0]
    f.paint(m, FIBRE, kind='trim', tex=lambda x, y, L: L + (0.18 if x == xa + 1 else 0) + (0.04 if (x + y) % 2 else -0.03),
            grad=0.2)
    cx = xa + 3
    for y in range(Y(y0) + 4, Y(y1) - 3, 8):
        for d in (-1, 0, 1):
            f.put(cx + d, y + d, RUNE_INK, 'trim')
            f.put(cx - d, y + d, RUNE_INK, 'trim')


def shard(f, cx, y, h, w):
    """faceted green crystal (v2 px): top point (cx, y), height h, half-width w; lit left facet,
    shaded right facet, bright crown facets, a centre ridge, a glint and a soft glow halo"""
    ys = y + int(h * 0.38)
    m = poly([(cx, y), (cx + w, ys), (cx + w * 0.6, y + h), (cx - w * 0.6, y + h), (cx - w, ys)])
    halo1 = dil(m, 1) - m
    halo2 = dil(m, 3) - dil(m, 1)
    for ring_m, a in ((halo2, 0.2), (halo1, 0.4)):
        for (x, yy) in ring_m:
            if 0 <= x < W and 0 <= yy < H:
                c = f.px[x, yy]
                if c[3]:
                    f.px[x, yy] = mix(c, HALO, a)
                else:
                    f.px[x, yy] = HALO + (int(255 * a * 1.2),)

    def tex(x, yy, L):
        if yy < ys:   # crown facets
            return 0.95 if x < cx else 0.7
        if abs(x - cx) < 0.6:
            return 0.85                         # centre ridge
        if x < cx:
            return 0.62 + (0.12 if (x - cx) > -w * 0.4 else 0)
        return 0.28 - (0.12 if (x - cx) > w * 0.45 else 0) + (0.15 if yy > y + h - 3 else 0)
    f.paint(m, CRYSTAL, kind='crystal', tex=tex, bevel=False)
    gx, gy = int(round(cx - w * 0.35)), ys + 1
    f.put(gx, gy, GLOW, 'crystal')
    f.put(gx, gy + 1, CRYSTAL[6], 'crystal')
    f.put(int(cx) - 1, y + 2, GLOW, 'crystal')
    sx, sy = int(cx + w + 2), y + 1
    for q in ((sx, sy), (sx - 1, sy), (sx + 1, sy), (sx, sy - 1), (sx, sy + 1)):
        if 0 <= q[0] < W and 0 <= q[1] < H:
            f.px[q] = GLOW if q == (sx, sy) else HALO + (150,)


def ragged(m, y_from, period=10, depth=7, seed=0):
    """cut a tattered hem: zig-zag points with uneven depth below y_from (v2 px)"""
    out = set()
    for (x, y) in m:
        tri = abs((x % period) - period / 2) / (period / 2)
        lim = y_from + depth * (1 - tri) + hsh(x // period, 0, seed) * 4
        if y <= lim or y < y_from:
            out.add((x, y))
    return out


def frayed(f, x, y, rp, n=3, seed=0):
    """a few loose fibre ends hanging from (x, y)"""
    for k in range(n):
        dx = k - n // 2
        ln = 2 + int(hsh(x + k, y, seed) * 3)
        for j in range(ln):
            f.put(x + dx + (j // 2) * (1 if dx > 0 else -1 if dx < 0 else 0), y + j, rp[4 - min(2, j)])


# ---------------------------------------------------------------- the figure
def draw_robe(back=False, bust=False):
    f = Fig()
    sides = (0, 1)

    # --- mannequin (same neutral faceless figure as the Light v2 sheets)
    if not bust:
        for side in sides:
            f.paint(S(R(21, 48, 31, 81), side), DUMMY, kind='dummy')
    for side in sides:
        f.paint(S(R(13, 22, 19, 58), side), DUMMY, kind='dummy')
    f.paint(R(27, 14, 36, 22), DUMMY, kind='dummy')
    face = E(25, 6, 38, 26) & R(0, 0, 63, 21)       # the hood opening: only this part of the head shows
    if not bust and not back:
        f.paint(v2.HEAD & face, FACE, kind='dummy', outline=False, grad=0.35)

    # --- outer cloak, back layer (seen at the sides on the front view, whole on the back view)
    cb = P([(17, 24), (46, 24), (49, 75), (14, 75)])
    if not bust and not back:
        f.paint(cb, LINING, tex=weave(1, 0.7))
        for side in sides:
            sm = S(P([(14, 40), (18, 40), (18, 75), (14, 75)]), side) & cb
            f.paint(sm, CLOAK, tex=weave(2 + side, 1.0, skirt_folds(30, Y(40))), edge_ref=cb)

    # --- feet: fibre-wrapped shoes peeking under the robe
    if not bust:
        for side in sides:
            sh = S(R(21, 78, 30, 82) | R(20, 80, 30, 82), side)
            f.paint(sh, FIBRE, tex=wraps(3, 5 + side), grad=0.35)
            sole = S(R(20, 82, 30, 82), side)
            f.paint(sole, v2.SOLE, tex=lambda x, y, L: L - 0.3 if x % 4 == 0 else L)

    # --- inner robe: long skirt flaring to the ankles, rune hem, ragged notches
    if not bust:
        skirt = P([(20, 44), (43, 44), (47, 79), (16, 79)])
        yb = max(y for _, y in skirt)
        for x in (19, 26, 33, 41):     # notches cut out of the hem (v1 single px -> small V)
            skirt -= {(2 * x + dx, yb - dy) for dy in range(3) for dx in range(-2 + dy, 3 - dy + 1)}
        f.paint(skirt, ROBE, tex=weave(10, 1.0, skirt_folds(63.5, Y(44))), grad=0.3)
        rune_band(f, 17, 46, 73)
        for x in (19, 26, 33, 41):
            frayed(f, 2 * x - 3, yb - 1, FIBRE, 2, x)
            frayed(f, 2 * x + 4, yb - 1, FIBRE, 2, x + 1)
        if back:   # the closed cloak hangs over the robe on the back
            cbr = ragged(cb, Y(74) - 2, 9, 5, 3)
            f.paint(cbr, CLOAK, tex=weave(12, 1.1, skirt_folds(63.5, Y(24))), grad=0.3)
            rune_band(f, 15, 48, 70)
            for x in range(36, 96, 12):          # long fold shadows + a few darns
                for y in range(Y(40), Y(68), 2):
                    xx = x + int(math.sin(y / 9.0) * 1.5)
                    if (xx, y) in cbr:
                        f.put(xx, y, CLOAK[1])
                        f.put(xx - 1, y, CLOAK[4])

    # --- torso of the robe
    torso = R(20, 21, 43, 46)
    f.paint(torso, ROBE, tex=weave(14), grad=0.3)
    if not back:   # front seam where the robe crosses over, stitched
        for y in range(Y(30), Y(44), 3):
            f.put(70, y, SEAM_G)
            f.put(71, y + 1, ROBE[5])

    # --- outer cloak, front: two long open panels framing the robe
    if not back:
        y1 = 72 if not bust else 60
        for side in sides:
            pn = S(P([(19, 24), (28, 24), (27, 45), (25, y1), (17, y1 - 1)]), side)
            if not bust:
                pn = ragged(pn, Y(y1) - 4, 7, 4, 7 + side)
            f.paint(pn, CLOAK, tex=weave(16 + side, 1.1, skirt_folds(40 if side == 0 else 88, Y(30))), grad=0.32)
            rune_strip(f, 25 if side == 0 else 25, 30, y1 - 3, side)

    # --- wide bell sleeves with fibre cuffs, bare hands
    for side in sides:
        sl = S(P([(13, 24), (20, 24), (22, 51), (9, 53)]), side)
        f.paint(sl, ROBE, tex=weave(18 + side, 1.0, skirt_folds(30, Y(24))), grad=0.32)
        for y in range(Y(26), Y(48), 3):        # sleeve seam stitches
            f.put(MX(40, side), y, SEAM_G)
        cuff = S(P([(10, 49), (22, 48), (22, 52), (9, 53)]), side)
        f.paint(cuff, FIBRE, kind='trim', tex=wraps(3, 20 + side), grad=0.3)
        hand = S(R(14, 53, 18, 58), side)
        f.paint(hand, DUMMY, kind='dummy',
                tex=lambda x, y, L: -1 if y > Y(56) and x in (31, 34, 93, 96) else L)

    # --- rope belt: twisted rope, knot on the wearer's right, hanging ends; crystal medallion on a cord
    belt = R(19, 43, 44, 45)
    f.paint(belt, ROPE, tex=rope_tex, kind='trim')
    if not back:
        knot = E(22, 41, 27, 47)
        f.paint(knot, ROPE, kind='trim',
                tex=lambda x, y, L: rope_tex(x, -y, L) if (x + y) % 9 < 6 else 0.1)
        for x0, y1 in ((23, 60), (26, 57)):
            cord = rect(2 * x0, Y(47), 2 * x0 + 3, Y(y1) + 1)
            f.paint(cord, ROPE, kind='trim', tex=rope_v)
            wrap = rect(2 * x0 - 1, Y(y1) - 2, 2 * x0 + 4, Y(y1) + 1)          # twine whipping at the end
            f.paint(wrap, FIBRE, kind='trim', tex=wraps(2, x0), grad=0.4)
            frayed(f, 2 * x0 + 1, Y(y1) + 2, ROPE, 4, x0)
        # medallion: twin cords from the belt + a rough shard in a fibre-wrapped setting
        for x in (72, 77):
            f.paint(rect(x, Y(45) + 1, x + 1, Y(48) + 2), ROPE, kind='trim', tex=rope_v)
        setting = E(33, 48, 41, 56)
        f.paint(setting, FIBRE, kind='trim', tex=wraps(3, 9), grad=0.4)
        f.paint(erode(setting, 3), LINING, kind='trim', grad=0.2)
        shard(f, 74.5, Y(48) + 2, 13, 4)
    else:
        knot = E(29, 41, 34, 47)
        f.paint(knot, ROPE, kind='trim', tex=lambda x, y, L: rope_tex(x, -y, L) if (x + y) % 9 < 6 else 0.1)

    # --- layered mantle (short cape over the shoulders) with a tattered hem
    mant = E(11, 15, 52, 40) & R(0, 18, 63, 35)
    mant = ragged(mant, Y(32), 10, 7, 21)
    f.paint(mant, CLOAK, tex=weave(22, 1.15), grad=0.35)
    hem = bottom_rim(mant, 3) - bottom_rim(mant, 1)
    f.paint(hem, FIBRE, outline=False, kind='trim', tex=lambda x, y, L: L + (0.1 if (x + y) % 2 else -0.05))
    for x in range(30, 100, 10):                  # moss-like fuzz flecks + fold lines on the mantle
        for y in range(Y(22), Y(31)):
            xx = x + (y - Y(22)) // 4 * (1 if x < 64 else -1)
            if (xx, y) in erode(mant, 2):
                f.put(xx, y, CLOAK[1])
                f.put(xx - 1, y, CLOAK[5])
    if not back:
        m2 = E(19, 20, 44, 34) & R(0, 22, 63, 30)
        m2 = ragged(m2, Y(29), 8, 4, 23)
        f.paint(m2, ROBE, tex=weave(24), grad=0.35)                               # 2nd layer under the hood
        f.paint(bottom_rim(m2, 2) - bottom_rim(m2, 1), FIBRE, outline=False, kind='trim')

    # --- hood (up): deep opening, face in shadow, crystal clasp at the throat
    hood = E(18, 0, 45, 30) & R(0, 0, 63, 26)
    if not back:
        hm = hood - face
        f.paint(hm, ROBE, tex=weave(26, 1.0, lambda x, y: 0.14 * math.sin((x - 63.5) / 3.2) if y < Y(8) else 0),
                grad=0.35)
        f.paint(top_rim(face, 8), LINING, outline=False, tex=weave(27, 0.5), kind='trim')     # deep shadow under the brow
        f.paint(top_rim(face, 12) - top_rim(face, 8), LINING, outline=False, kind='trim',
                tex=lambda x, y, L: 0.25 if (x + y) % 2 else 0.6)                             # shadow fading onto the face
        edge = (dil(face, 4) & hood) - face
        f.trim(edge, hood, FIBRE, tex=lambda x, y, L: L + (0.12 if (x + y) % 2 else -0.04))  # fibre rim on the hood
        f.stitch(edge | face, RUNE_INK, d=3, per=4, on=2, ys=(Y(0), Y(18)))
        cord = R(29, 21, 34, 25)
        f.paint(cord, ROPE, kind='trim', tex=rope_tex)                                         # clasp cord
        shard(f, 63.5, Y(20) - 2, 22, 6)                                                       # crystal clasp
    else:
        hb = hood | (v2.HEAD & R(0, 0, 63, 20))
        f.paint(hb, ROBE, tex=weave(28, 1.0, lambda x, y: 0.14 * math.sin((x - 63.5) / 3.5)), grad=0.35)
        seam = P([(31.5, 6), (33, 22), (30, 22)])
        f.paint(seam, ROBE, outline=False, tex=lambda x, y, L: 0.0 if x in (62, 63, 64, 65) else 0.3)  # back seam fold
        for y in range(Y(4), Y(22), 3):
            f.put(61, y, SEAM_G)
            f.put(66, y + 1, SEAM_G)
        tab = R(28, 26, 35, 27)
        f.paint(tab, FIBRE, kind='trim', tex=wraps(3, 31))
        frayed(f, 64, Y(28), FIBRE, 3, 9)       # hood point tassel
    return f


# ---------------------------------------------------------------- output
font = ms.font


def save(im, name):
    im = im.convert('RGB').quantize(colors=176, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    p = os.path.join(HERE, name)
    im.save(p, optimize=True)
    return os.path.getsize(p)


def closeup(f, box, s=CHEST_SCALE):
    crop = f.im.crop(box)
    ch = crop.resize((crop.width * s, crop.height * s), Image.NEAREST)
    base = Image.new('RGBA', ch.size, BG)
    base.alpha_composite(ch)
    return base


def main():
    sizes = {}
    fr, bk = draw_robe(), draw_robe(back=True)
    a, b = v2.scaled(fr, SET_SCALE), v2.scaled(bk, SET_SCALE)
    pair = Image.new('RGBA', (a.width * 2 + 16, a.height), BG)
    pair.paste(a, (0, 0))
    pair.paste(b, (a.width + 16, 0))
    d = ImageDraw.Draw(pair)
    d.text((10, 8), 'front', font=font(16), fill=INK)
    d.text((a.width + 26, 8), 'back', font=font(16), fill=INK)
    sizes['crude-robe-set-v2.png'] = save(v2.label(pair, 'Crude Robe (Cloth tier 1, v2)',
                                                   'Lv 1-13  |  2x detail  |  concept, cloud draft'), 'crude-robe-set-v2.png')

    # close-up: hood, clasp, mantle and the belt medallion (head included - the hood is the robe's face)
    box = (8, Y(0) - 4, 120, Y(60))
    ch = closeup(fr, box)
    sizes['crude-robe-chest-v2.png'] = save(v2.label(ch, 'Crude Robe - hood + chest (v2)',
                                                     'front close-up: crystal clasp, rope belt, shard medallion'),
                                            'crude-robe-chest-v2.png')

    a3, b3 = v2.scaled(fr, SHEET_SCALE), v2.scaled(bk, SHEET_SCALE)
    chs = closeup(fr, box, 4)
    light = v2.scaled(v2.draw_figure(1), SHEET_SCALE)
    gap, top, labh = 20, 96, 56
    cells = [(a3, 'Crude Robe - front', 'Lv 1-13  |  Cloth tier 1'),
             (b3, 'Crude Robe - back', ''),
             (chs, 'Hood + chest close-up', 'front, 4x'),
             (light, 'Light Copper v2 (for scale)', 'existing design')]
    sw = sum(c[0].width for c in cells) + gap * (len(cells) + 1)
    sheet = Image.new('RGBA', (sw, top + a3.height + labh + 60), BG)
    d = ImageDraw.Draw(sheet)
    d.text((sw // 2, 16), 'SkyWynn Cloth tier 1 - Crude Robe v2 (cloud draft)', font=font(40), fill=INK, anchor='mt')
    d.text((sw // 2, 62), '2x detail (128 x 192 figure grid, v1 was 64 x 84)  |  same approved design  |  woven fibre, '
           'twisted rope, stitched runes, faceted glowing crystals', font=font(18), fill=SUB, anchor='mt')
    x = gap
    for im, t1, t2 in cells:
        sheet.paste(im, (x, top + (a3.height - im.height) // 2))
        d.text((x + im.width // 2, top + a3.height + 6), t1, font=font(24), fill=INK, anchor='mt')
        d.text((x + im.width // 2, top + a3.height + 34), t2, font=font(15), fill=SUB, anchor='mt')
        x += im.width + gap
    y = top + a3.height + labh + 22
    x = gap
    for nm, rp in (('robe', ROBE), ('cloak', CLOAK), ('fibre trim', FIBRE), ('rope', ROPE), ('crystal', CRYSTAL)):
        for j, col in enumerate(rp[1:]):
            d.rectangle((x + j * 16, y, x + 12 + j * 16, y + 12), fill=col, outline=rp[0])
        d.text((x + 104, y - 2), nm, font=font(15), fill=INK)
        x += 210
    sizes['crude-robe-sheet-v2.png'] = save(sheet, 'crude-robe-sheet-v2.png')
    k = list(fr.kind.values())
    print('front: crystal px', k.count('crystal'), 'of', len(k) - k.count('dummy'), 'armor px')
    for n, s in sizes.items():
        print(f'{n:30s} {s // 1024:5d} KB')


if __name__ == '__main__':
    main()
