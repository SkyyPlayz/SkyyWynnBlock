#!/usr/bin/env python3
"""SkyWynn magic + new weapons - concept sheets v2 (cloud draft 2026-10-06).

v2 = Skyy's art review (docs/answered/gear.md, WEAPONS lock 2026-10-06): 2x the pixel density of v1, richer spellbook
covers, a reworked Soul Cage that floats above an open palm (+ a 4-frame cage-spin strip), Wolverine-style claws
with a black LEATHER glove, everything else as v1 with more surface detail.

Original pixel art, drawn from code (no copied art, no game files). Deterministic.
Run:  python3 research/cloud/weapon-art/make_weapons_v2.py
Writes *-v2.png (and soul-cage-spin-v2.gif) next to this script; the v1 files are not touched.

Method (v1 painter, extended): every icon is painted on a 96 x 96 grid (v1: 48 x 48), one part at a time. Each part
gets a 1-px dark outline, a 2-px bevel lit from the top-left (light rim top-left, dark rim bottom-right), a soft
gradient across big parts, and per-material texture (wood grain, pebbled / tooled leather, metal scratches + pits,
crystal facets, cloth weave). Shown x2 with NEAREST (192 px cells, same sheet size as v1).
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.dirname(os.path.abspath(__file__))
G = 96                 # icon grid (2x v1)
SCALE = 2              # 192 x 192 per icon on the sheet


def hx(s):
    s = s.lstrip('#')
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def ramp(*cols):
    """[outline, dark, mid, light, highlight]"""
    return [hx(c) for c in cols]


def hsh(x, y, seed=0):
    """deterministic 0..999 noise"""
    v = (x * 73856093) ^ (y * 19349663) ^ (seed * 83492791)
    v = (v ^ (v >> 13)) * 1274126177
    return (v ^ (v >> 16)) % 1000


# ---------------------------------------------------------------- palettes (v1 values, same metals as light-armor)
GOLD = ramp('#4a3208', '#9a6e18', '#d4a234', '#f0c860', '#fff0b0')
LEATHER = ramp('#08070a', '#18151b', '#25212a', '#37323e', '#4e4858')       # black leather
SHEEN = hx('#7a7388')                                                       # leather sheen streak
STITCH = hx('#6e6676')                                                      # thread on black leather
WOOD = ramp('#24140a', '#5a3519', '#7d4c26', '#a06a38', '#c48e56')
PAGES = ramp('#5a4c34', '#b4a27c', '#d8c8a0', '#ece0bc', '#fbf4dc')
SKIN = ramp('#4a453f', '#7e776c', '#968e81', '#ada596', '#c6bfb0')           # neutral mannequin grey

TIERS = [
    ('Copper', 'Lv 10-18', ramp('#3b1a0c', '#8a4220', '#c26a34', '#e89558', '#ffc48e')),
    ('Iron', 'Lv 15-23', ramp('#24282e', '#5c646e', '#8e97a2', '#bcc4cc', '#eef2f5')),
    ('Thorium', 'Lv 20-28', ramp('#1c3324', '#3f6b4a', '#5e9468', '#8cc08e', '#cdebc6')),
    ('Cobalt', 'Lv 25-38', ramp('#121b3d', '#2a3f8a', '#3f63c4', '#6f95e6', '#b9d0ff')),
    ('Adamantite', 'Lv 35-43', ramp('#3a0c10', '#7a1a20', '#b42c30', '#e0574f', '#ffa192')),
    ('Mithril', 'Lv 40-49', ramp('#1e3a44', '#4e8c98', '#7ec4cc', '#b4ecee', '#f2ffff')),
    ('Onyxium', 'Lv 40-49', ramp('#160c22', '#3e2460', '#6b3fa0', '#a06cda', '#e4c8ff')),
]
GLOW = {'Onyxium': hx('#ff7af0'), 'Mithril': hx('#ffffff'), 'Adamantite': hx('#ffd0c8')}
CRYSTAL = [
    ramp('#0c3a24', '#1f7a4a', '#34b06a', '#6ee09a', '#d2ffe2'),
    ramp('#0c2c4a', '#1f5f9a', '#3a8fd6', '#7cc0f2', '#e0f4ff'),
    ramp('#2e3a08', '#647a14', '#98b424', '#c8e050', '#f4ffc0'),
    ramp('#08343e', '#13707e', '#22b0be', '#6ee6ee', '#e0ffff'),
    ramp('#3e0c06', '#8a2410', '#d4461c', '#ff8a46', '#ffe0b0'),
    ramp('#1c3a40', '#5aa0aa', '#a8e4e4', '#e0fbf8', '#ffffff'),
    ramp('#2a0626', '#6e1466', '#b42aa8', '#ec6ad8', '#ffd0f6'),
]
ESSENCE = [
    ('Life', ramp('#0c3a14', '#1f7a2c', '#3cba4a', '#82ec7e', '#e0ffd8')),
    ('Fire', ramp('#3e0806', '#8a1610', '#d22e1e', '#ff7448', '#ffd8b8')),
    ('Ice', ramp('#08303e', '#136a86', '#28a8cc', '#78dcf2', '#e4fbff')),
    ('Lightning', ramp('#3e3006', '#8a6a10', '#d2aa1e', '#fae05a', '#fffbd0')),
    ('Void', ramp('#22083a', '#4e167a', '#8030c0', '#b674ec', '#ecd4ff')),
    ('Wind', ramp('#24382c', '#6a9478', '#a8d4b4', '#dcf6e2', '#ffffff')),
    ('Void heart', ramp('#06040a', '#1a1024', '#36204c', '#6a3a96', '#d08cff')),
]
TETHERS = [2, 4, 6, 10, 14, 16, 20]
# v2: spellbook cover leather per tier (v1 was the same brown on every tier) - placeholder guesses
BOOK_LEATHER = [
    ramp('#1e0e07', '#4c2414', '#6e3820', '#8e4e2e', '#ae6a42'),   # Copper  - tan brown
    ramp('#140a06', '#34201a', '#4c3024', '#664232', '#825a46'),   # Iron    - dark brown
    ramp('#0c1a10', '#1e3a24', '#2c5434', '#3e6e46', '#58905e'),   # Thorium - deep green
    ramp('#0a1024', '#1a2850', '#26386c', '#34508c', '#4c6cac'),   # Cobalt  - navy
    ramp('#1a0608', '#46121a', '#621c26', '#802a34', '#a0404a'),   # Adamantite - oxblood
    ramp('#141c22', '#34444e', '#4c606a', '#687e88', '#8aa2aa'),   # Mithril - slate blue-grey
    ramp('#0a0610', '#1e1428', '#2e2040', '#40305a', '#5a4878'),   # Onyxium - black-violet
]
CLOTH = [
    ('Linen Wraps', ramp('#4a3e2a', '#9a8660', '#c2ae84', '#ddcca4', '#f2e6c8')),
    ('Cotton Wraps', ramp('#4e5054', '#a4a8ae', '#cdd0d4', '#e8eaec', '#ffffff')),
    ('Silk Wraps', ramp('#4a2a3a', '#a4708a', '#d4a2b8', '#f0cede', '#fff0f6')),
    ('Cindercloth Wraps', ramp('#3e1206', '#8a2c10', '#c8521e', '#f08a3a', '#ffd08a')),
    ('Shadoweave Wraps', ramp('#0e0a16', '#2a2238', '#40355a', '#5c4e80', '#8c7cb4')),
    None,
    None,
]

BG = hx('#b4b9bf')
BG_CELL = hx('#aab0b6')
INK = (34, 36, 40, 255)
SUB = (60, 64, 70, 255)
DIM = (110, 114, 120, 255)


# ---------------------------------------------------------------- mask helpers
def _draw(fn):
    im = Image.new('1', (G, G), 0)
    fn(ImageDraw.Draw(im))
    px = im.load()
    return {(x, y) for x in range(G) for y in range(G) if px[x, y]}


def rect(x0, y0, x1, y1):
    return {(x, y) for x in range(int(x0), int(x1) + 1) for y in range(int(y0), int(y1) + 1)}


def ell(x0, y0, x1, y1):
    return _draw(lambda d: d.ellipse((x0, y0, x1, y1), fill=1))


def poly(pts):
    return _draw(lambda d: d.polygon([tuple(p) for p in pts], fill=1))


def line(pts, w=1):
    return _draw(lambda d: d.line([tuple(p) for p in pts], fill=1, width=w))


def ring(cx, cy, r0, r1):
    return ell(cx - r1, cy - r1, cx + r1, cy + r1) - ell(cx - r0, cy - r0, cx + r0, cy + r0)


def rrect(x0, y0, x1, y1, r):
    return _draw(lambda d: d.rounded_rectangle((x0, y0, x1, y1), radius=r, fill=1))


class Axis:
    def __init__(self, a, b):
        self.a, self.b = a, b
        dx, dy = b[0] - a[0], b[1] - a[1]
        self.len = math.hypot(dx, dy)
        self.u = (dx / self.len, dy / self.len)
        self.n = (-self.u[1], self.u[0])

    def p(self, t, off=0.0):
        return (self.a[0] + (self.b[0] - self.a[0]) * t + self.n[0] * off,
                self.a[1] + (self.b[1] - self.a[1]) * t + self.n[1] * off)

    def ip(self, t, off=0.0):
        x, y = self.p(t, off)
        return int(round(x)), int(round(y))

    def seg(self, t0, t1, w, w1=None):
        w1 = w if w1 is None else w1
        return poly([self.p(t0, -w / 2), self.p(t1, -w1 / 2), self.p(t1, w1 / 2), self.p(t0, w / 2)])

    def tri(self, t0, t1, w):
        return poly([self.p(t0, -w / 2), self.p(t1), self.p(t0, w / 2)])

    def leaf(self, t0, t1, w, off=0.0, ang=0.0, mid=0.4):
        base = self.p(t0, off)
        L = (t1 - t0) * self.len
        ca, sa = math.cos(ang), math.sin(ang)
        ux, uy = self.u[0] * ca - self.u[1] * sa, self.u[0] * sa + self.u[1] * ca
        nx, ny = -uy, ux

        def q(s, o):
            return (base[0] + ux * s + nx * o, base[1] + uy * s + ny * o)
        pts = [q(0, 0), q(L * mid, -w / 2), q(L, 0), q(L * mid, w / 2)]
        return poly(pts), (q(0, 0), q(L, 0))

    def t_of(self, x, y):
        return ((x - self.a[0]) * self.u[0] + (y - self.a[1]) * self.u[1]) / self.len

    def o_of(self, x, y):
        return (x - self.a[0]) * self.n[0] + (y - self.a[1]) * self.n[1]


# ---------------------------------------------------------------- painter (v1 painter + bevel, gradient, textures)
class Fig:
    def __init__(self):
        self.im = Image.new('RGBA', (G, G), (0, 0, 0, 0))
        self.px = self.im.load()

    def paint(self, mask, rp, tex=None, outline=True, bev=2, grad=True):
        """outline on the edge; light rim top-left (bev px), dark rim bottom-right; soft gradient; texture hook"""
        mask = {p for p in mask if 0 <= p[0] < G and 0 <= p[1] < G}
        if not mask:
            return
        edge = {(x, y) for x, y in mask
                if any(q not in mask for q in ((x, y - 1), (x - 1, y), (x + 1, y), (x, y + 1)))}
        inner = mask - edge if outline else mask
        xs = [p[0] for p in mask]
        ys = [p[1] for p in mask]
        x0, y0 = min(xs), min(ys)
        w, h = max(1, max(xs) - x0), max(1, max(ys) - y0)
        big = len(mask) > 140

        def out(q):
            return q not in inner

        for (x, y) in mask:
            if outline and (x, y) in edge:
                i = 0
            else:
                up, lf = out((x, y - 1)), out((x - 1, y))
                dn, rt = out((x, y + 1)), out((x + 1, y))
                if (up and lf):
                    i = 4
                elif up or lf:
                    i = 3
                elif dn or rt:
                    i = 1
                else:
                    i = 2
                    if bev >= 2:
                        if out((x, y - 2)) or out((x - 2, y)):
                            i = 3
                        elif out((x, y + 2)) or out((x + 2, y)):
                            i = 1 if not big else 2
                    if i == 2 and grad and big:
                        g = (x - x0) / w + (y - y0) / h
                        if g > 1.35:
                            i = 1 if hsh(x, y, 7) < 650 or g > 1.6 else 2
                        elif g < 0.45 and hsh(x, y, 8) < 500:
                            i = 3
            if tex:
                i = tex(x, y, i)
            self.px[x, y] = rp[max(0, min(4, i))]

    def flat(self, mask, col):
        for x, y in mask:
            if 0 <= x < G and 0 <= y < G:
                self.px[x, y] = col

    def dots(self, pts, rp):
        for x, y, i in pts:
            if 0 <= x < G and 0 <= y < G:
                self.px[int(x), int(y)] = rp[i]

    def put(self, x, y, col):
        if 0 <= x < G and 0 <= y < G:
            self.px[int(x), int(y)] = col

    def blend(self, x, y, col, a):
        """alpha-blend a colour onto what is there (glows, palm hint)"""
        if not (0 <= x < G and 0 <= y < G):
            return
        r, g, b, al = self.px[int(x), int(y)]
        if al == 0:
            self.px[int(x), int(y)] = (col[0], col[1], col[2], int(255 * a))
        else:
            self.px[int(x), int(y)] = (int(r + (col[0] - r) * a), int(g + (col[1] - g) * a),
                                       int(b + (col[2] - b) * a), max(al, int(255 * a)))

    def glow(self, x, y, col, r=2):
        self.put(x, y, col)
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                d = math.hypot(dx, dy)
                if 0 < d <= r + 0.3:
                    self.blend(x + dx, y + dy, col, 0.55 * (1 - d / (r + 1)))


# ---------------------------------------------------------------- textures
def chain(*fs):
    def f(x, y, i):
        for g in fs:
            if g:
                i = g(x, y, i)
        return i
    return f


def metal_tex(seed=1, wear=True):
    """scratches + pits on the flat metal, sparkle on the light rim"""
    def f(x, y, i):
        if i == 0:
            return 0
        h = hsh(x, y, seed)
        if i == 2 and wear:
            if h < 22:
                return 1
            if h < 34:
                return 3
        if i == 3 and h < 45:
            return 4
        return i
    return f


def wood_tex(seed=3):
    """grain along a 45-degree item axis (constant x + y)"""
    def f(x, y, i):
        if i == 0:
            return 0
        k = x + y + (1 if hsh((x - y) // 7, 0, seed) < 300 else 0)
        if i in (2, 3) and k % 4 == 0 and hsh((x - y) // 5, k, seed) < 700:
            return i - 1
        if i == 2 and hsh(x, y, seed + 1) < 40:
            return 3
        return i
    return f


def leather_tex(seed=5, amt=120):
    """pebbled leather grain"""
    def f(x, y, i):
        if i in (1, 2, 3):
            h = hsh(x, y, seed)
            if h < amt:
                return i - 1 if i > 1 else 1
            if h > 1000 - amt // 2:
                return min(3, i + 1)
        return i
    return f


def wrap_tex(axis_fn, step=4, seed=9):
    """cord / strap wrap: dark groove every `step` along the axis + a lit ridge after it"""
    def f(x, y, i):
        if i == 0:
            return 0
        k = axis_fn(x, y) % step
        if k == 0:
            return 1 if i > 1 else i
        if k == 1 and i >= 2:
            return min(4, i + 1)
        return i
    return f


def facet_paint(f, mask, C, a, b, extra_split=True):
    """crystal with facets: lit half / shaded half split along its long axis, bright ridge + sparkle"""
    f.paint(mask, C, bev=1, grad=False)
    ax = Axis(a, b)
    for (x, y) in mask:
        if f.px[x, y] == C[0]:
            continue
        o = ax.o_of(x, y)
        t = ax.t_of(x, y)
        cur = C.index(f.px[x, y]) if f.px[x, y] in C else 2
        if o > 0.6:
            f.px[x, y] = C[max(1, cur - 1)]
        elif -0.6 <= o <= 0.6 and 0.08 < t < 0.92:
            f.px[x, y] = C[4] if t < 0.5 else C[3]
        elif extra_split and t > 0.62 and o < -0.6:
            f.px[x, y] = C[3]
    s = ax.ip(0.3, -1.5)
    f.put(s[0], s[1], C[4])


def stitch_line(f, pts, col, on=2, off=2):
    """a dashed thread line along a polyline"""
    k = 0
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        n = int(max(abs(xb - xa), abs(yb - ya)))
        for s in range(n + 1):
            x = round(xa + (xb - xa) * s / max(1, n))
            y = round(ya + (yb - ya) * s / max(1, n))
            if k % (on + off) < on:
                f.put(x, y, col)
            k += 1


def band_ramp(t, M):
    return GOLD if TIERS[t][0] == 'Mithril' else M


def rivet(f, x, y, M):
    f.dots([(x, y, 4), (x + 1, y, 2), (x, y + 1, 2), (x + 1, y + 1, 0)], M)


# ---------------------------------------------------------------- 1. wand (style B)
def draw_wand(t):
    name, _, M = TIERS[t]
    C = CRYSTAL[t]
    B = band_ramp(t, M)
    f = Fig()
    ax = Axis((14, 84), (70, 28))
    n_leaf = [1, 1, 3, 3, 3, 3, 3][t]
    if n_leaf >= 2:
        for s in (-1, 1):
            m, (a, b) = ax.leaf(0.84, 1.10, 10, off=3 * s, ang=0.55 * s)
            facet_paint(f, m, C, a, b)
    f.paint(ax.seg(0.0, 0.80, 7, 5.4), WOOD, tex=wood_tex())
    f.paint(ax.seg(-0.03, 0.07, 8.6), M, tex=metal_tex(2))
    f.paint(ax.seg(-0.04, -0.01, 6), M)
    for b in [[0.42], [0.42], [0.30, 0.52], [0.30, 0.52], [0.30, 0.52], [0.22, 0.42, 0.60], [0.22, 0.42, 0.60]][t]:
        f.paint(ax.seg(b, b + 0.055, 8.6), B, tex=metal_tex(3))
        c = ax.ip(b + 0.027, -2.4)
        rivet(f, c[0], c[1], B)
    f.paint(ax.seg(0.70, 0.84, 8.8, 12.4), M, tex=metal_tex(4))
    for k in range(3):
        g = [ax.ip(0.72 + k * 0.04, o) for o in (-3, 3)]
        f.flat(line(g), M[1])
    f.paint(ax.seg(0.80, 0.865, 13.6), B, tex=metal_tex(5))
    if name == 'Cobalt':
        for s in (-1, 1):
            f.paint(poly([ax.p(0.72, 6 * s), ax.p(0.87, 13 * s), ax.p(0.84, 6 * s)]), M, tex=metal_tex(6))
    if name == 'Adamantite':
        for s in (-1, 1):
            f.paint(poly([ax.p(0.73, 5 * s), ax.p(0.80, 14 * s), ax.p(0.80, 5 * s)]), M)
    if n_leaf == 3:
        m, (a, b) = ax.leaf(0.84, 1.16, 12)
    else:
        m, (a, b) = ax.leaf(0.84, 1.14, 12)
    facet_paint(f, m, C, a, b)
    if t >= 1:
        for s in (-1, 1):
            f.paint(poly([ax.p(0.84, 5.2 * s), ax.p(0.96, 7.4 * s), ax.p(0.97, 5.0 * s), ax.p(0.84, 2.8 * s)]), B)
    if name in GLOW:
        f.glow(*ax.ip(0.77), GLOW[name])
        f.glow(*ax.ip(1.02, -1), GLOW[name], 1)
    return f


# ---------------------------------------------------------------- 2. staff
def draw_staff(t):
    name, _, M = TIERS[t]
    C = CRYSTAL[t]
    B = band_ramp(t, M)
    f = Fig()
    ax = Axis((6, 92), (70, 28))
    if t >= 2:
        for s in (-1, 1):
            m, (a, b) = ax.leaf(0.84, 1.07, 10, off=6 * s, ang=0.8 * s)
            facet_paint(f, m, C, a, b)
    f.paint(ax.seg(0.0, 0.82, 7.4, 6.2), WOOD, tex=wood_tex(4))
    f.paint(ax.seg(-0.02, 0.05, 9.4), M, tex=metal_tex(7))
    f.paint(ax.seg(-0.03, 0.0, 6.4), M)
    f.paint(ax.seg(0.40, 0.52, 8.0), LEATHER, tex=wrap_tex(lambda x, y: x - y, 4))
    for b in [[0.35, 0.56], [0.35, 0.56], [0.25, 0.35, 0.56], [0.25, 0.35, 0.56, 0.66],
              [0.25, 0.35, 0.56, 0.66], [0.15, 0.25, 0.35, 0.56, 0.66], [0.15, 0.25, 0.35, 0.56, 0.66]][t]:
        f.paint(ax.seg(b, b + 0.04, 9.6), B, tex=metal_tex(8))
    f.paint(ax.seg(0.74, 0.86, 9.6, 16), M, tex=metal_tex(9))
    f.paint(ax.seg(0.84, 0.885, 17), B, tex=metal_tex(10))
    for o in (-4, 0, 4):
        c = ax.ip(0.862, o)
        rivet(f, c[0], c[1], B)
    if name == 'Cobalt':
        for s in (-1, 1):
            f.paint(poly([ax.p(0.76, 6 * s), ax.p(0.90, 16 * s), ax.p(0.86, 6 * s)]), M, tex=metal_tex(11))
    if name == 'Adamantite':
        for s in (-1, 1):
            f.paint(poly([ax.p(0.74, 6 * s), ax.p(0.80, 16 * s), ax.p(0.82, 6 * s)]), M)
            f.paint(poly([ax.p(0.80, 7 * s), ax.p(0.88, 18 * s), ax.p(0.87, 7 * s)]), M)
    m, (a, b) = ax.leaf(0.86, 1.32, 18)
    facet_paint(f, m, C, a, b)
    for s in (-1, 1):
        f.paint(poly([ax.p(0.86, 6.8 * s), ax.p(1.02, 10.4 * s), ax.p(1.07, 7.6 * s), ax.p(1.0, 6.8 * s),
                      ax.p(0.88, 3.6 * s)]), B, tex=metal_tex(12))
    if name in ('Mithril', 'Onyxium'):
        f.paint(ax.seg(1.00, 1.035, 14.0) - ax.seg(0.99, 1.045, 6.4), B)
    if name in GLOW:
        f.glow(*ax.ip(0.80), GLOW[name])
        f.glow(*ax.ip(1.12, -2), GLOW[name], 3)
    return f


# ---------------------------------------------------------------- 3. spellbook (tooled leather, filigree, page edges, ribbon)
def emblem(f, t, ex, ey, M):
    name = TIERS[t][0]
    mt = metal_tex(20 + t)
    if name == 'Copper':                                         # sun ring with rays
        for k in range(8):
            a = k * math.pi / 4
            f.paint(poly([(ex + math.cos(a - 0.18) * 7, ey + math.sin(a - 0.18) * 7),
                          (ex + math.cos(a) * 13, ey + math.sin(a) * 13),
                          (ex + math.cos(a + 0.18) * 7, ey + math.sin(a + 0.18) * 7)]), M, bev=1)
        f.paint(ring(ex, ey, 4, 9), M, tex=mt)
    elif name == 'Iron':                                         # riveted square, engraved cross
        f.paint(rect(ex - 9, ey - 9, ex + 9, ey + 9), M, tex=mt)
        f.flat(rect(ex - 1, ey - 6, ex, ey + 6) | rect(ex - 6, ey - 1, ex + 6, ey), M[1])
        for dx in (-7, 6):
            for dy in (-7, 6):
                rivet(f, ex + dx, ey + dy, M)
    elif name == 'Thorium':                                      # round boss, concentric rings
        f.paint(ell(ex - 11, ey - 11, ex + 11, ey + 11), M, tex=mt)
        f.flat(ring(ex, ey, 7, 8), M[1])
        f.paint(ell(ex - 5, ey - 5, ex + 5, ey + 5), M)
        f.put(ex - 2, ey - 2, M[4])
    elif name == 'Cobalt':                                       # diamond with a gem
        f.paint(poly([(ex, ey - 15), (ex + 10, ey), (ex, ey + 15), (ex - 10, ey)]), M, tex=mt)
        m = poly([(ex, ey - 8), (ex + 5, ey), (ex, ey + 8), (ex - 5, ey)])
        facet_paint(f, m, CRYSTAL[t], (ex, ey + 8), (ex, ey - 8))
    elif name == 'Adamantite':                                   # crystal shards
        for (dx, h, w) in ((-8, 12, 6), (8, 12, 6), (0, 18, 7)):
            m = poly([(ex + dx - w, ey + 11), (ex + dx, ey + 11 - h - 6), (ex + dx + w, ey + 11)])
            facet_paint(f, m, M, (ex + dx, ey + 11), (ex + dx, ey + 11 - h - 6), extra_split=False)
        f.paint(rect(ex - 13, ey + 10, ex + 13, ey + 13), M)
        f.glow(ex, ey - 5, GLOW['Adamantite'])
    elif name == 'Mithril':                                      # 8-point star + glow
        pts = []
        for k in range(16):
            a = k * math.pi / 8 - math.pi / 2
            r = 15 if k % 4 == 0 else (8 if k % 2 == 0 else 4)
            pts.append((ex + math.cos(a) * r, ey + math.sin(a) * r))
        f.paint(poly(pts), M, tex=mt, bev=1)
        f.glow(ex, ey, GLOW['Mithril'], 3)
    else:                                                        # Onyxium: violet gem in a gold setting
        f.paint(ell(ex - 12, ey - 13, ex + 12, ey + 13), GOLD, tex=metal_tex(30))
        for k in range(8):
            a = k * math.pi / 4
            rivet(f, round(ex + math.cos(a) * 10), round(ey + math.sin(a) * 11), GOLD)
        m = ell(ex - 7, ey - 8, ex + 7, ey + 8)
        facet_paint(f, m, M, (ex, ey + 8), (ex, ey - 8))
        f.glow(ex - 2, ey - 3, GLOW['Onyxium'], 2)


def draw_book(t):
    name, _, M = TIERS[t]
    L = BOOK_LEATHER[t]
    FM = GOLD if name in ('Mithril', 'Onyxium') else M          # filigree metal
    f = Fig()
    x0, y0, x1, y1 = 20, 10, 72, 82                             # front cover
    # back cover + page block (seen at a slight 3/4: right + bottom edges show)
    f.paint(rect(x0 + 2, y0 + 4, x1 + 6, y1 + 6), L, bev=1, grad=False)
    PG = GOLD if name in ('Mithril', 'Onyxium') else PAGES
    f.paint(rect(x1 - 2, y0 + 3, x1 + 4, y1 + 3), PG, bev=1, grad=False,
            tex=lambda x, y, i: (1 if (y % 2 == 0 and i in (2, 3, 4)) else i))
    f.paint(rect(x0 + 2, y1 - 2, x1 + 4, y1 + 4), PG, bev=1, grad=False,
            tex=lambda x, y, i: (1 if (x % 2 == 0 and i in (2, 3, 4)) else i))
    # bookmark ribbon out of the bottom of the pages
    RB = CRYSTAL[t] if name != 'Copper' else ESSENCE[1][1]
    rx = 54
    rib = rect(rx, y1 + 2, rx + 4, y1 + 12) - {(rx + 2, y1 + 12), (rx + 2, y1 + 11)}
    f.paint(rib, RB, bev=1, grad=False)
    # spine (left), rounded with raised bands
    spine = rect(x0 - 8, y0, x0 + 3, y1)
    f.paint(spine, L, tex=leather_tex(40), grad=False)
    for xx in range(x0 - 6, x0 + 2):
        for yy in range(y0 + 1, y1):
            if (xx - (x0 - 6)) in (0, 1):
                f.put(xx, yy, L[3])
    # cover
    cover = rect(x0, y0, x1, y1)
    f.paint(cover, L, tex=leather_tex(41 + t, 140))
    # tooled border: an embossed double frame (dark groove + light ridge)
    for inset, dark in ((5, True), (9, False)):
        a0, b0, a1, b1 = x0 + inset, y0 + inset, x1 - inset, y1 - inset
        fr = line([(a0, b0), (a1, b0), (a1, b1), (a0, b1), (a0, b0)])
        fr2 = line([(a0 + 1, b0 + 1), (a1 + 1, b0 + 1), (a1 + 1, b1 + 1), (a0 + 1, b1 + 1), (a0 + 1, b0 + 1)])
        f.flat(fr, L[0] if dark else L[1])
        f.flat(fr2 - fr, L[3] if dark else L[4])
    # tooled dot row between the frames (higher tiers: diamond lattice tooling inside)
    for xx in range(x0 + 8, x1 - 6, 3):
        f.put(xx, y0 + 7, L[1])
        f.put(xx, y1 - 7, L[1])
    for yy in range(y0 + 8, y1 - 6, 3):
        f.put(x0 + 7, yy, L[1])
        f.put(x1 - 7, yy, L[1])
    if t >= 3:
        for (x, y) in rect(x0 + 11, y0 + 11, x1 - 11, y1 - 11):
            if (x + y) % 8 == 0 or (x - y) % 8 == 0:
                if math.hypot(x - 46, y - 46) > 20:
                    f.put(x, y, L[1])
    # spine bands (metal) across the spine
    nb = 2 if t < 3 else 3
    ys = [y0 + 8, y1 - 12] if nb == 2 else [y0 + 8, (y0 + y1) // 2 - 2, y1 - 12]
    for yy in ys:
        f.paint(rect(x0 - 9, yy, x0 + 3, yy + 4), M, tex=metal_tex(50))
        rivet(f, x0 - 5, yy + 1, M)
    # embossed leather medallion under the emblem
    ex, ey = 46, 46
    med = ell(ex - 18, ey - 18, ex + 18, ey + 18)
    f.paint(med, L, tex=leather_tex(60), grad=False)
    f.flat(ring(ex, ey, 15, 16), L[1])
    emblem(f, t, ex, ey, M)
    # filigree corners: metal plate + scroll curls running along both edges
    c = [9, 9, 10, 10, 11, 12, 13][t]
    for (cx, cy, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        plate = poly([(cx, cy), (cx + sx * c, cy), (cx + sx * c * 0.45, cy + sy * c * 0.45), (cx, cy + sy * c)]) | {(cx, cy)}
        f.paint(plate, M, tex=metal_tex(60), bev=1, grad=False)
        rivet(f, cx + sx * 3 - (1 if sx < 0 else 0), cy + sy * 3 - (1 if sy < 0 else 0), M)
        if t >= 2:                                               # curls along the edges
            for (px_, py_) in ((cx + sx * (c + 4), cy + sy * 3), (cx + sx * 3, cy + sy * (c + 4))):
                f.paint(ring(px_, py_, 1.2, 2.6), FM, bev=1, grad=False)
            f.flat(line([(cx + sx * c, cy + sy * 1), (cx + sx * (c + 3), cy + sy * 2)]), FM[2])
            f.flat(line([(cx + sx * 1, cy + sy * c), (cx + sx * 2, cy + sy * (c + 3))]), FM[2])
        if t >= 5:                                               # long gold vine to the frame
            f.flat(line([(cx + sx * (c + 6), cy + sy * 3), (cx + sx * (c + 12), cy + sy * 6)]), FM[3])
            f.flat(line([(cx + sx * 3, cy + sy * (c + 6)), (cx + sx * 6, cy + sy * (c + 12))]), FM[3])
    # clasp strap from the back cover over the pages onto the front
    cy = (y0 + y1) // 2
    strap = rect(x1 - 8, cy - 5, x1 + 9, cy + 5)
    f.paint(strap, L if t < 6 else LEATHER, tex=leather_tex(70), grad=False)
    stitch_line(f, [(x1 - 6, cy - 3), (x1 + 7, cy - 3)], L[3] if t < 6 else STITCH)
    stitch_line(f, [(x1 - 6, cy + 3), (x1 + 7, cy + 3)], L[3] if t < 6 else STITCH)
    f.paint(rect(x1 - 12, cy - 7, x1 - 3, cy + 7), M, tex=metal_tex(80))
    f.flat(rect(x1 - 9, cy - 2, x1 - 6, cy + 1), M[0])
    f.put(x1 - 8, cy - 1, M[3])
    if name in GLOW and name != 'Mithril':
        f.glow(x1 - 7, cy + 4, GLOW[name], 1)
    return f


# ---------------------------------------------------------------- 4. Soul Cage (floats above an open palm; the cage spins)
def dodeca():
    phi = (1 + 5 ** 0.5) / 2
    v = [(x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
    for a in (-1, 1):
        for b in (-1, 1):
            v += [(0, a / phi, b * phi), (a / phi, b * phi, 0), (a * phi, 0, b / phi)]
    e = [(i, j) for i in range(20) for j in range(i + 1, 20)
         if abs(math.dist(v[i], v[j]) - 2 / phi) < 1e-6]
    # turn it so a 5-fold axis (a face centre) points straight up: that is the spin axis
    phi_ = phi
    fc = (0, 1, phi_)                                           # direction of a face normal (icosahedron vertex)
    n = math.hypot(*fc)
    fc = tuple(c / n for c in fc)
    # rotate fc onto (0,-1,0) (screen up = -y) about the x axis
    ang = math.atan2(fc[2], fc[1]) - math.atan2(0, -1)
    ca, sa = math.cos(-ang), math.sin(-ang)
    v = [(x, y * ca - z * sa, y * sa + z * ca) for x, y, z in v]
    return v, e


def draw_palm(f, cx, top):
    """open hand held flat, palm up, seen from the side (forearm bottom-left, fingers to the right, thumb up):
    a low-contrast 'hint' under the floating item"""
    P = SKIN
    tmp = Fig()
    arm = poly([(12, G), (32, G), (38, top + 14), (24, top + 12)])
    palm = ell(22, top + 2, 64, top + 20)
    fingers = poly([(56, top + 4), (76, top + 5), (82, top + 2), (87, top + 4), (84, top + 11), (74, top + 15), (58, top + 17)])
    thumb = ell(30, top - 5, 40, top + 9)
    tmp.paint(arm | palm | fingers | thumb, P)
    # cupped palm surface (lit), thumb edge, finger separations, creases
    for (x, y) in ell(30, top + 3, 60, top + 10):
        tmp.put(x, y, P[3] if y < top + 6 else P[2])
    tmp.flat(_draw(lambda d: d.arc((30, top - 5, 40, top + 9), 20, 140, fill=1)), P[1])
    for y in (top + 7, top + 10, top + 13):
        tmp.flat(line([(64, y), (79, y - 3)]), P[0])
        tmp.flat(line([(64, y + 1), (78, y - 2)]), P[3])
    tmp.flat(line([(62, top + 4), (62, top + 16)]), P[1])
    tmp.flat(line([(36, top + 13), (50, top + 14)]), P[1])
    tmp.flat(line([(28, top + 16), (34, top + 19)]), P[1])
    tmp.flat({(84, top + 3), (85, top + 3), (33, top - 3), (34, top - 4)}, P[4])
    for x in range(G):
        for y in range(G):
            c = tmp.px[x, y]
            if c[3]:
                f.blend(x, y, c, 0.88)


def cage_fig(t, theta=0.0, palm=True):
    name, _, M = TIERS[t]
    _, E = ESSENCE[t]
    f = Fig()
    cx, cy, s = 48, 33, 21.0
    if palm:
        draw_palm(f, cx, 72)
        # soft essence glow on the palm, under the soul
        for x in range(cx - 14, cx + 15):
            for y in range(72, 84):
                d = math.hypot((x - cx) / 14, (y - 77) / 4)
                if d < 1:
                    f.blend(x, y, E[3], 0.45 * (1 - d))
        # float gap marks
        for (gx, gy) in ((cx - 28, 66), (cx + 24, 67)):
            f.flat(line([(gx, gy), (gx + 2, gy - 1), (gx + 4, gy)]), (255, 255, 255, 150))
    v, e = dodeca()
    tilt = 0.30

    def rot(p):
        x, y, z = p
        x, z = x * math.cos(theta) - z * math.sin(theta), x * math.sin(theta) + z * math.cos(theta)
        y, z = y * math.cos(tilt) - z * math.sin(tilt), y * math.sin(tilt) + z * math.cos(tilt)
        return x, y, z
    R = [rot(p) for p in v]
    P = [(cx + x * s / 1.4, cy + y * s / 1.4, z) for x, y, z in R]
    # soul glow halo (behind everything)
    for x in range(cx - 20, cx + 21):
        for y in range(cy - 20, cy + 21):
            d = math.hypot(x - cx, y - cy)
            if 10 < d < 22:
                f.blend(x, y, E[3], 0.30 * (1 - (d - 10) / 12))

    def bar(i, j, w):
        (x0, y0, _), (x1, y1, _) = P[i], P[j]
        return line([(x0, y0), (x1, y1)], w)
    back = [(i, j) for i, j in e if P[i][2] + P[j][2] > 0]
    front = [(i, j) for i, j in e if P[i][2] + P[j][2] <= 0]
    for i, j in back:                                          # back bars: thin, dark
        f.flat(bar(i, j, 2), M[1])
    # the soul: glowing orb, swirl, bright core
    f.paint(ell(cx - 11, cy - 11, cx + 11, cy + 11), E, grad=True)
    f.flat(_draw(lambda d: d.arc((cx - 8, cy - 8, cx + 8, cy + 8), 20, 160, fill=1)), E[1])     # inner swirl
    f.flat(_draw(lambda d: d.arc((cx - 6, cy - 5, cx + 6, cy + 7), 200, 320, fill=1)), E[3])
    f.paint(ell(cx - 6, cy - 7, cx + 1, cy), E, outline=False, tex=lambda x, y, i: 4 if i >= 2 else 3, grad=False)
    f.glow(cx - 3, cy - 4, hx('#ffffff') if t != 6 else GLOW['Onyxium'], 2)
    # wisps rising off the soul
    for (wx, wy) in ((cx + 4, cy - 12), (cx - 6, cy - 13), (cx + 9, cy - 9)):
        f.blend(wx, wy, E[4], 0.7)
        f.blend(wx, wy - 1, E[3], 0.4)
    # front bars: 2 px, mid with a highlight line + a dark lower line
    for i, j in front:
        m = bar(i, j, 3)
        f.flat(m, M[2])
        (x0, y0, _), (x1, y1, _) = P[i], P[j]
        f.flat(line([(x0, y0 - 1), (x1, y1 - 1)]) & m, M[3])
        f.flat(line([(x0, y0 + 1), (x1, y1 + 1)]) & m, M[1])
    for i, j in front:                                        # outline the front bars where they cross the soul
        m = bar(i, j, 3)
        for (x, y) in m:
            for q in ((x, y + 1), (x + 1, y)):
                if q not in m and 0 <= q[0] < G and 0 <= q[1] < G and f.px[q][3] and f.px[q] in E[1:]:
                    f.put(q[0], q[1], M[0])
    # nodes; the gem corners are fixed vertex ids (tethers stay on the same corners while it spins)
    gem_ids = set(sorted(range(20), key=lambda i: (v[i][2], v[i][1], v[i][0]))[:TETHERS[t]])
    for i in sorted(range(20), key=lambda i: -P[i][2]):
        x, y = int(round(P[i][0])), int(round(P[i][1]))
        front_ = P[i][2] <= 0
        if i in gem_ids:
            if front_:
                facet_paint(f, poly([(x, y - 4), (x + 3, y), (x, y + 4), (x - 3, y)]), E, (x, y + 4), (x, y - 4))
                f.put(x - 1, y - 1, E[4])
            else:
                f.paint(rect(x - 1, y - 1, x + 1, y + 1), E, bev=1, grad=False)
                f.put(x, y, E[3])
        else:
            if front_:
                f.paint(ell(x - 2, y - 2, x + 2, y + 2), M, bev=1, grad=False)
                f.put(x - 1, y - 1, M[4])
            else:
                f.flat(rect(x - 1, y - 1, x, y), M[1])
    # spin-axis finials (top + bottom poles)
    top_y = min(p[1] for p in P)
    bot_y = max(p[1] for p in P)
    f.paint(poly([(cx - 3, top_y - 1), (cx, top_y - 8), (cx + 3, top_y - 1)]), M, bev=1, grad=False)
    f.paint(ell(cx - 2, top_y - 11, cx + 2, top_y - 7), E if t >= 3 else M, bev=1, grad=False)
    f.paint(poly([(cx - 3, bot_y + 1), (cx, bot_y + 7), (cx + 3, bot_y + 1)]), M, bev=1, grad=False)
    if name in GLOW:
        f.glow(cx, top_y - 9, GLOW[name], 1)
    return f


def draw_cage(t):
    return cage_fig(t, theta=0.25)


SPIN_STEPS = [0.25, 0.25 + 0.3142, 0.25 + 0.6283, 0.25 + 0.9425]   # 4 frames = 18 degrees each (5-fold cage: 72 = full cycle)


# ---------------------------------------------------------------- 5. kunai
def draw_kunai(t):
    name, _, M = TIERS[t]
    f = Fig()
    ax = Axis((18, 78), (84, 12))
    rx, ry = ax.ip(-0.07)
    f.paint(ring(rx, ry, 3.6, 8.6), M, tex=metal_tex(90), bev=1)
    f.paint(ax.seg(-0.02, 0.03, 6), M)
    f.paint(ax.seg(0.02, 0.40, 7.4), LEATHER,
            tex=chain(wrap_tex(lambda x, y: x - y, 5), lambda x, y, i: (4 if i == 3 and hsh(x, y, 3) < 300 else i)))
    for k in range(9):                                          # cord criss-cross
        a = ax.ip(0.04 + k * 0.04, -3)
        b = ax.ip(0.06 + k * 0.04, 3)
        f.flat(line([a, b]), LEATHER[3])
    col = GOLD if name in ('Mithril', 'Onyxium') else M
    f.paint(ax.seg(0.38, 0.45, 10.4), col, tex=metal_tex(91))
    c = ax.ip(0.415, -2.5)
    rivet(f, c[0], c[1], col)
    w = [16, 16, 18, 18, 18, 18, 20][t]
    if name == 'Cobalt':
        blade = poly([ax.p(0.44, -4), ax.p(0.58, -w / 2), ax.p(0.66, -w / 2 + 2), ax.p(1.0), ax.p(0.66, w / 2 - 2),
                      ax.p(0.58, w / 2), ax.p(0.44, 4)])
    else:
        blade = poly([ax.p(0.44, -4), ax.p(0.62, -w / 2), ax.p(1.0), ax.p(0.62, w / 2), ax.p(0.44, 4)])
    if name == 'Adamantite':
        for k in (0.66, 0.74, 0.82):
            blade -= poly([ax.p(k, -w / 2 + 1), ax.p(k + 0.04, -w / 2 + 5.2), ax.p(k + 0.08, -w / 2 + 1)])
    f.paint(blade, M, tex=metal_tex(92), bev=1, grad=False)
    # bevels: lit half (above the ridge), shaded half, bright ridge, honed edge line
    for (x, y) in blade:
        if f.px[x, y] == M[0]:
            continue
        o = ax.o_of(x, y)
        tt = ax.t_of(x, y)
        if o > 0.7:
            f.px[x, y] = M[1] if hsh(x, y, 4) > 80 else M[2]
        elif -0.7 <= o <= 0.7 and tt > 0.47:
            f.px[x, y] = M[4]
    for (x, y) in blade:
        if f.px[x, y] != M[0] and any(q not in blade for q in ((x - 1, y), (x, y - 1))) is False:
            pass
    for k in range(20):                                         # honed edge (lit side)
        tt = 0.50 + k * 0.024
        o = -(w / 2 - 2) * (min(tt, 0.62) - 0.44) / 0.18 if tt < 0.62 else -(w / 2 - 2) * (1 - tt) / 0.38
        f.put(*ax.ip(tt, o), M[3])
    if name in GLOW:
        f.glow(*ax.ip(0.62, 2), GLOW[name])
        if name == 'Onyxium':
            f.glow(*ax.ip(0.86, 1), GLOW[name])
    return f


# ---------------------------------------------------------------- 6. Bo staff
def draw_bo(t):
    name, _, M = TIERS[t]
    B = band_ramp(t, M)
    if name == 'Onyxium':
        B = GOLD
    f = Fig()
    ax = Axis((8, 88), (88, 8))
    f.paint(ax.seg(0.02, 0.98, 7.4), WOOD, tex=wood_tex(6))
    f.paint(ax.seg(0.41, 0.59, 8.6), LEATHER, tex=chain(wrap_tex(lambda x, y: x - y, 5),
                                                        lambda x, y, i: (4 if i == 3 and hsh(x, y, 5) < 250 else i)))
    for tt in (0.41, 0.59):
        f.paint(ax.seg(tt - 0.008, tt + 0.008, 9.4), LEATHER, grad=False)
    stitch_line(f, [ax.ip(0.42, 0), ax.ip(0.58, 0)], STITCH)
    cap = [0.08, 0.08, 0.10, 0.10, 0.11, 0.11, 0.12][t]
    cw = [9.4, 9.4, 11, 9.8, 10.2, 10.2, 11][t]
    for t0, t1 in ((-0.01, cap), (1 - cap, 1.01)):
        f.paint(ax.seg(t0, t1, cw), M, tex=metal_tex(100))
        for k in range(2):
            tt = t0 + (t1 - t0) * (0.33 + 0.33 * k)
            f.flat(line([ax.ip(tt, -cw / 2 + 1.5), ax.ip(tt, cw / 2 - 1.5)]), M[1])
    if name == 'Cobalt':
        f.paint(ax.tri(1.0, 1.06, 8.4), M)
        f.paint(ax.tri(0.0, -0.06, 8.4), M)
    if name == 'Adamantite':
        for tc in (cap * 0.5, 1 - cap * 0.5):
            for s in (-1, 1):
                f.paint(poly([ax.p(tc - 0.03, 4 * s), ax.p(tc, 11 * s), ax.p(tc + 0.03, 4 * s)]), M)
    nb = [1, 1, 2, 2, 2, 3, 3][t]
    for k in range(nb):
        for base, sgn in ((cap, 1), (1 - cap, -1)):
            b = base + sgn * (0.035 + k * 0.06)
            f.paint(ax.seg(min(b, b + sgn * 0.03), max(b, b + sgn * 0.03), 9.2), B, tex=metal_tex(101))
    for tc in (cap * 0.5, 1 - cap * 0.5):
        c = ax.ip(tc, -2)
        rivet(f, c[0], c[1], M)
    if name in GLOW:
        f.glow(*ax.ip(0.5, -2), GLOW[name])
    return f


# ---------------------------------------------------------------- 7-9. fist weapons (front view of a closed fist)
def fist(ox, oy, k=1.0):
    """finger blocks, back of hand, thumb, cuff; v1 fist x2, scaled by k around (ox, oy)"""
    def P(x, y):
        return (ox + x * k, oy + y * k)
    fingers = []
    for j in range(4):
        x0, y0 = P(-22 + 11.5 * j, -24 + (2 if j in (0, 3) else 0))
        x1, y1 = P(-12 + 11.5 * j, -8)
        fingers.append(rrect(x0, y0, x1, y1, max(1, int(3 * k))))
    hand = rect(*P(-23, -12), *P(24, 16))
    thumb = poly([P(-32, -6), P(-22, -8), P(-22, 14), P(-30, 12)])
    cuff = poly([P(-21, 16), P(22, 16), P(27, 40), P(-26, 40)])
    return fingers, hand, thumb, cuff


def draw_gauntlet(t):
    name, _, M = TIERS[t]
    T = GOLD if name in ('Mithril', 'Onyxium') else M
    mt = metal_tex(110 + t)
    f = Fig()
    fingers, hand, thumb, cuff = fist(48, 48)
    f.paint(rect(24, 34, 72, 66), LEATHER, tex=leather_tex(1))
    stitch_line(f, [(25, 64), (71, 64)], STITCH)
    f.paint(cuff, M, tex=mt)
    for yy in (73, 80):
        f.flat(line([(25, yy), (71, yy)]), M[1])
        f.flat(line([(25, yy + 1), (71, yy + 1)]), M[3])
    f.paint(rect(22, 62, 74, 66) | rect(21, 85, 75, 88), T, tex=metal_tex(5))
    for x in (26, 38, 58, 70):
        rivet(f, x, 86, T)
    # back-of-hand lames (overlapping plates)
    for k, (ya, yb) in enumerate(((40, 48), (47, 55), (54, 62))):
        f.paint(rect(27, ya, 69, yb), M, tex=mt)
        rivet(f, 29, ya + 2, M)
        rivet(f, 66, ya + 2, M)
    f.paint(thumb, M, tex=mt)
    f.flat(line([(18, 50), (26, 49)]), M[1])
    # fingers: knuckle plate + mid plate per finger, leather gaps
    for j, fm in enumerate(fingers):
        f.paint(fm, M, tex=mt, grad=False)
        xs = [p[0] for p in fm]
        ys = [p[1] for p in fm]
        ymid = (min(ys) + max(ys)) // 2 + 1
        f.flat({(x, ymid) for x in range(min(xs) + 1, max(xs))}, M[0])
        f.flat({(x, ymid + 1) for x in range(min(xs) + 1, max(xs))}, M[3])
    if name == 'Iron':
        for x in (31, 43, 54, 66):
            rivet(f, x, 30, M)
    if name == 'Thorium':
        for j in range(4):
            bx = 31 + 11.5 * j
            f.paint(ell(bx - 4, 25, bx + 4, 33), M, tex=mt, bev=1)
            f.put(int(bx) - 1, 27, M[4])
    if name == 'Cobalt':
        for j in range(4):
            bx = 31 + 11.5 * j
            f.paint(poly([(bx - 4, 27), (bx, 16), (bx + 4, 27)]), M, tex=mt, bev=1)
        f.paint(poly([(36, 42), (48, 54), (60, 42), (60, 46), (48, 58), (36, 46)]), M, bev=1)
    if name == 'Adamantite':
        for j in range(4):
            bx = 31 + 11.5 * j
            f.paint(poly([(bx - 4, 27), (bx, 8), (bx + 4, 27)]), M, bev=1)
        f.paint(poly([(73, 68), (86, 72), (74, 78)]), M)
        f.paint(poly([(23, 68), (10, 72), (22, 78)]), M)
    if name in ('Mithril', 'Onyxium'):
        f.paint(rect(27, 39, 69, 41), GOLD)
        f.paint(ell(40, 43, 56, 59), GOLD, tex=metal_tex(9))
        m = ell(44, 47, 52, 55)
        facet_paint(f, m, CRYSTAL[t] if name == 'Mithril' else M, (48, 55), (48, 47))
        f.glow(48, 50, GLOW[name], 2)
    return f


def draw_claws(t):
    """Wolverine-style: 3 long straight parallel blades out of the gaps between the knuckles of a black leather glove"""
    name, _, M = TIERS[t]
    T = GOLD if name in ('Mithril', 'Onyxium') else M
    f = Fig()
    # glove geometry (own, shorter than the gauntlet so the blades get the height)
    fx = [26, 37, 48, 59]                                       # finger left edges, 10 wide, 1 px gaps
    ftop = [55, 53, 53, 55]
    fingers = [rrect(fx[j], ftop[j], fx[j] + 10, 68, 3) for j in range(4)]
    hand = rrect(25, 62, 70, 82, 2)
    thumb = poly([(16, 64), (26, 63), (27, 79), (19, 77)])
    cuff = poly([(27, 82), (68, 82), (70, 95), (25, 95)])
    bxs = [36.5, 47.5, 58.5]                                    # blade centres = the finger gaps
    top = [6, 6, 5, 4, 4, 3, 3][t]
    for j, bx in enumerate(bxs):
        bw = 7
        x0, x1 = bx - bw / 2, bx + bw / 2
        tip = top + (2 if j != 1 else 0)
        blade = poly([(x0, 64), (x0, tip + 8), (x1, tip), (x1, 64)])
        if name == 'Adamantite':                                # barb on the back edge
            blade |= poly([(x0, tip + 20), (x0 - 3, tip + 25), (x0, tip + 27)])
        f.paint(blade, M, bev=1, grad=False)
        for (x, y) in blade:                                    # bevels: lit left facet, ridge, darker right facet
            if f.px[x, y] == M[0]:
                continue
            rel = x - int(x0)
            if rel <= 1:
                f.px[x, y] = M[3]
            elif rel == 2:
                f.px[x, y] = M[4]
            elif rel >= bw - 1:
                f.px[x, y] = M[1]
            else:
                f.px[x, y] = M[2] if hsh(x, y, 3) > 40 else M[1]
        for k in range(5):                                      # bright cutting-edge glints at the tip
            f.put(int(x1) - 1, tip + 2 + k, M[4] if k < 2 else M[3])
        for yy in range(tip + 16, 54, 11):                      # faint scratches
            f.put(int(x0) + 4, yy, M[3])
        # socket collar where the blade leaves the glove
        f.paint(rect(bx - 4, 50, bx + 3, 53), T, bev=1, grad=False)
        if name in GLOW:
            f.glow(int(x0) + 2, tip + 12, GLOW[name], 1)
    # black leather glove
    lt = leather_tex(11, 70)
    f.paint(cuff, LEATHER, tex=lt)
    f.paint(hand, LEATHER, tex=lt)
    f.paint(thumb, LEATHER, tex=lt)
    for fm in fingers:
        f.paint(fm, LEATHER, tex=lt, grad=False)
    # sheen: a curved soft highlight on each knuckle, a long streak on the back of the hand, one on the thumb
    for j in range(4):
        a, b = fx[j] + 2, ftop[j] + 2
        f.flat({(a + 1, b), (a + 2, b), (a + 3, b), (a + 4, b), (a, b + 1), (a, b + 2)}, SHEEN)
        f.flat({(a + 1, b + 1), (a + 2, b + 1), (a + 5, b)}, LEATHER[4])
    f.flat(line([(29, 67), (40, 65), (52, 65)]), LEATHER[4])
    f.flat(line([(30, 67), (38, 66)]), SHEEN)
    f.flat(line([(19, 67), (20, 74)]), LEATHER[4])
    f.flat(line([(29, 85), (40, 84)]), LEATHER[4])
    # creases: across each finger joint + two on the back of the hand
    for j in range(4):
        y = 63 + (j % 2)
        f.flat(line([(fx[j] + 2, y), (fx[j] + 5, y - 1), (fx[j] + 8, y)]), LEATHER[0])
        f.flat(line([(fx[j] + 3, y + 1), (fx[j] + 7, y + 1)]), LEATHER[3])
    for (pa, pb) in (((33, 73), (39, 75)), ((52, 75), (58, 72)), ((44, 78), (50, 78))):
        f.flat(line([pa, pb]), LEATHER[0])
        f.flat(line([(pa[0], pa[1] - 1), (pb[0], pb[1] - 1)]), LEATHER[3])
    # stitching: thread seams down from the finger gaps + round the cuff top
    for bx in bxs:
        stitch_line(f, [(round(bx) - 1, 70), (round(bx) - 1, 80)], STITCH, 1, 2)
    stitch_line(f, [(28, 84), (67, 84)], STITCH, 2, 2)
    stitch_line(f, [(27, 93), (68, 93)], STITCH, 2, 2)
    # wrist strap + buckle in the tier metal
    f.paint(rect(26, 86, 69, 90), LEATHER, grad=False)
    f.paint(rect(43, 84, 52, 92), T, tex=metal_tex(121), bev=1, grad=False)
    f.flat(rect(45, 86, 50, 90), LEATHER[0])
    f.flat(rect(47, 86, 48, 90), T[3])
    return f


def draw_wraps(t):
    if CLOTH[t] is None:
        return None
    cname, C = CLOTH[t]
    f = Fig()
    fingers, hand, thumb, cuff = fist(48, 48)
    f.paint(rect(24, 24, 72, 62), SKIN)
    for fm in fingers:
        f.paint(fm, SKIN, grad=False)
    f.paint(thumb, SKIN)

    def weave(x, y, i):
        if i in (2, 3) and (x % 3 == 0) and (y % 2 == 0):
            return i - 1
        return i
    # knuckle wrap + diagonal crossing straps + palm bands
    f.paint(rect(23, 28, 73, 37), C, tex=weave)
    f.paint(poly([(24, 40), (34, 38), (72, 52), (72, 58), (62, 58), (24, 46)]), C, tex=weave)
    f.paint(rect(23, 41, 73, 48) - poly([(24, 40), (34, 38), (72, 52), (72, 58), (62, 58), (24, 46)]), C, tex=weave)
    f.paint(poly([(72, 40), (62, 38), (24, 52), (24, 58), (34, 58), (72, 46)]), C, tex=weave)
    f.paint(rect(23, 54, 73, 63), C, tex=weave)
    f.paint(rect(16, 44, 28, 52), C, tex=weave)
    # cuff: overlapping turns
    for k, ya in enumerate(range(63, 88, 6)):
        sh = (k % 2) * 2
        f.paint(poly([(23 + sh, ya), (73 + sh, ya - 2), (75 + sh, ya + 6), (22 + sh, ya + 7)]), C, tex=weave)
    f.paint(poly([(66, 80), (76, 76), (90, 92), (82, 95)]), C, tex=weave)
    f.flat(line([(76, 82), (86, 93)]), C[1])
    if t >= 3:
        stitch_line(f, [(25, 30), (71, 30)], C[4] if t == 3 else C[3])
        stitch_line(f, [(25, 61), (71, 61)], C[4] if t == 3 else C[3])
    return f


# ---------------------------------------------------------------- output
ROWS = [
    ('Wand', 'style B (LOCKED): wood handle,\nmetal head + bands, faceted\nleaf crystals; gold bands on Mithril', draw_wand),
    ('Staff', 'same family, longer, big\nfaceted crystal in a riveted\nmetal cradle', draw_staff),
    ('Spellbook', 'v2: tier-tinted tooled leather,\nembossed medallion + emblem,\nfiligree corners, page edges,\nribbon, stitched clasp strap', draw_book),
    ('Soul Cage', 'v2: floats above the open palm;\ncage spins round the soul (axis\nfinials); gems = tethers (2..20)', draw_cage),
    ('Kunai', 'bevelled blade + ridge,\ncriss-cross cord wrap,\nring pommel', draw_kunai),
    ('Bo staff', 'grained wood, engraved caps,\nstitched leather centre grip', draw_bo),
    ('Gauntlets', 'fist weapon: plate lames,\njointed finger plates, rivets,\nstitched leather under', draw_gauntlet),
    ('Claws', 'v2: Wolverine-style - 3 long\nstraight blades from the knuckles;\nblack LEATHER glove (stitching,\ncreases, sheen)', draw_claws),
    ('Hand wraps', 'fist weapon: CLOTH ladder\n(not metal), crossed straps,\nweave texture', draw_wraps),
]


def font(n):
    return ImageFont.load_default(size=n)


def icon(f, s=SCALE, bg=BG_CELL):
    im = f.im.resize((G * s, G * s), Image.NEAREST)
    base = Image.new('RGBA', im.size, bg)
    base.alpha_composite(im)
    return base


def sub_for(row, t):
    name, band, _ = TIERS[t]
    if row == 'Soul Cage':
        return f'{band}  |  {TETHERS[t]} gems, {ESSENCE[t][0]}'
    if row == 'Hand wraps':
        return f'{CLOTH[t][0] if CLOTH[t] else "-"}  ({band})'
    return band


def placeholder(size, lines):
    im = Image.new('RGBA', (size, size), (166, 171, 177, 255))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, size - 1, size - 1), outline=(140, 145, 151, 255), width=3)
    for k, ln in enumerate(lines):
        d.text((size // 2, size // 2 - 20 + k * 22), ln, font=font(16), fill=DIM, anchor='mt')
    return im


def save(im, name, colors=192):
    im = im.convert('RGB').quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    im.save(os.path.join(OUT, name), optimize=True)


def slug(s):
    return s.lower().replace(' ', '-')


def spin_strip():
    """soul-cage-spin-v2.png: 7 tiers x 4 frames (18 degrees apart) + an animated GIF of all 7"""
    cell = G * SCALE
    gap = 14
    w = 140 + 4 * (cell + gap) + gap
    h = 80 + len(TIERS) * (cell + gap) + gap
    im = Image.new('RGBA', (w, h), BG)
    d = ImageDraw.Draw(im)
    d.text((gap, 14), 'Soul Cage v2 - slow cage spin around the soul (4 frames, 18 deg each; soul + palm stay still)',
           font=font(20), fill=INK)
    d.text((gap, 38), 'engine animation = UNVERIFIED (local check)', font=font(13), fill=SUB)
    frames = {t: [cage_fig(t, th) for th in SPIN_STEPS] for t in range(len(TIERS))}
    for t, (name, band, M) in enumerate(TIERS):
        y = 80 + t * (cell + gap)
        d.text((gap, y + cell // 2 - 10), name, font=font(20), fill=INK)
        d.text((gap, y + cell // 2 + 14), f'{TETHERS[t]} gems', font=font(13), fill=SUB)
        for k, fg in enumerate(frames[t]):
            im.paste(icon(fg), (140 + k * (cell + gap), y))
            if t == 0:
                d.text((140 + k * (cell + gap) + cell // 2, 62), f'frame {k + 1}', font=font(12), fill=SUB, anchor='mt')
    save(im, 'soul-cage-spin-v2.png')
    # GIF: all 7 tiers side by side, 12 frames over one 72-degree turn (looks seamless: 5-fold cage)
    gw = len(TIERS) * (G + 4) + 4
    gif = []
    for k in range(12):
        th = 0.25 + k * (2 * math.pi / 5) / 12
        fr = Image.new('RGBA', (gw, G + 8), BG)
        for t in range(len(TIERS)):
            fr.paste(icon(cage_fig(t, th), 1), (4 + t * (G + 4), 4))
        gif.append(fr.convert('RGB').resize((gw * 2, (G + 8) * 2), Image.NEAREST)
                   .quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE))
    gif[0].save(os.path.join(OUT, 'soul-cage-spin-v2.gif'), save_all=True, append_images=gif[1:],
                duration=180, loop=0, optimize=True)
    return frames


def main():
    cell = G * SCALE
    gap, labh = 14, 44
    figs = {row: [fn(t) for t in range(len(TIERS))] for row, _, fn in ROWS}
    frames = spin_strip()

    for row, note, _ in ROWS:
        w = len(TIERS) * cell + (len(TIERS) + 1) * gap
        h = 56 + cell + labh + gap
        im = Image.new('RGBA', (w, h), BG)
        d = ImageDraw.Draw(im)
        d.text((gap, 14), f'SkyWynn {row} v2 - concept (cloud draft)', font=font(26), fill=INK)
        d.text((w - gap, 20), note.replace('\n', ' '), font=font(13), fill=SUB, anchor='ra')
        for t, (name, band, M) in enumerate(TIERS):
            x, y = gap + t * (cell + gap), 56
            fg = figs[row][t]
            if fg is None:
                im.paste(placeholder(cell, ['later', '(Prisma / Moon cloth)' if t == 5 else '(no wraps)']), (x, y))
            else:
                im.paste(icon(fg), (x, y))
            label = (CLOTH[t][0].replace(' Wraps', '') if row == 'Hand wraps' and CLOTH[t] else name)
            d.text((x + cell // 2, y + cell + 6), label, font=font(20), fill=INK, anchor='mt')
            d.text((x + cell // 2, y + cell + 28), sub_for(row, t), font=font(13), fill=SUB, anchor='mt')
        save(im, f'{slug(row)}-v2.png')

    lw = 250
    top = 124
    rowh = cell + labh - 10
    nrows = len(ROWS) + 1
    w = lw + len(TIERS) * (cell + gap) + gap
    h = top + nrows * (rowh + gap) + gap
    sheet = Image.new('RGBA', (w, h), BG)
    d = ImageDraw.Draw(sheet)
    d.text((w // 2, 16), 'SkyWynn magic + new weapons - concept v2 (cloud draft)', font=font(34), fill=INK, anchor='mt')
    for t, (name, band, M) in enumerate(TIERS):
        x = lw + t * (cell + gap)
        d.text((x + cell // 2, 62), name, font=font(24), fill=INK, anchor='mt')
        d.text((x + cell // 2, 88), band, font=font(14), fill=SUB, anchor='mt')
        for j, col in enumerate([M[3], M[2], M[1]]):
            sx = x + cell // 2 - 22 + j * 16
            d.rectangle((sx, 106, sx + 12, 118), fill=col, outline=M[0])
    for r, (row, note, _) in enumerate(ROWS):
        y = top + r * (rowh + gap)
        d.text((gap, y + 30), row, font=font(26), fill=INK)
        for k, ln in enumerate(note.split('\n')):
            d.text((gap, y + 66 + k * 18), ln, font=font(13), fill=SUB)
        for t in range(len(TIERS)):
            x = lw + t * (cell + gap)
            fg = figs[row][t]
            if fg is None:
                sheet.paste(placeholder(cell, ['later', '(Prisma / Moon cloth)' if t == 5 else '(no wraps)']), (x, y))
            else:
                sheet.paste(icon(fg), (x, y))
            if row in ('Soul Cage', 'Hand wraps'):
                d.text((x + cell // 2, y + cell + 6), sub_for(row, t), font=font(13), fill=SUB, anchor='mt')
    # last row: the cage-spin strip (Cobalt, 4 frames) + a note
    y = top + len(ROWS) * (rowh + gap)
    d.text((gap, y + 30), 'Cage spin', font=font(26), fill=INK)
    for k, ln in enumerate(['Cobalt, 4 frames x 18 deg:', 'the cage turns slowly round', 'the soul; soul + palm still.',
                            'All tiers: soul-cage-spin-v2.png', '+ soul-cage-spin-v2.gif',
                            'engine animation UNVERIFIED']):
        d.text((gap, y + 66 + k * 18), ln, font=font(13), fill=SUB)
    for k in range(4):
        x = lw + k * (cell + gap)
        sheet.paste(icon(frames[3][k]), (x, y))
        d.text((x + cell // 2, y + cell + 6), f'frame {k + 1}', font=font(13), fill=SUB, anchor='mt')
    x = lw + 4 * (cell + gap)
    for k, ln in enumerate(['v1 -> v2', 'grid 48 -> 96 px (2x), shown x2', 'bevel + gradient shading,',
                            'wood grain, leather grain,', 'metal scratches + rivets,', 'crystal facets, cloth weave.',
                            'v1 files kept: weapon-sheet.png', 'and <type>.png (unchanged).']):
        d.text((x + 10, y + 20 + k * 20), ln, font=font(15), fill=SUB)
    save(sheet, 'weapon-sheet-v2.png')


if __name__ == '__main__':
    main()
