#!/usr/bin/env python3
"""SkyWynn magic + new weapons - concept sheets (cloud draft 2026-10-06).

Original pixel art, drawn from code (no copied art, no game files).
Run:  python3 research/cloud/weapon-art/make_weapons.py
Writes the PNGs next to this script. Deterministic: same code -> same bytes.

Same method as research/cloud/light-armor/make_sheets.py (its palettes and
painter are copied here, that folder is not touched): every icon is painted
on a small 48 x 48 grid, one part (a set of grid pixels) at a time. Each part
gets a 1-px dark outline and a 4-step shade ramp lit from the top-left. The
grid is scaled up with NEAREST so the pixels stay chunky.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.dirname(os.path.abspath(__file__))
G = 48                 # icon grid (48 x 48, like an inventory icon)
SCALE = 4              # 192 x 192 per icon


def hx(s):
    s = s.lstrip('#')
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def ramp(*cols):
    """[outline, dark, mid, light, highlight]"""
    return [hx(c) for c in cols]


# ---------------------------------------------------------------- palettes (metal ramps copied from light-armor)
GOLD = ramp('#4a3208', '#9a6e18', '#d4a234', '#f0c860', '#fff0b0')
LEATHER = ramp('#0a090c', '#1c191f', '#2b2730', '#3f3946', '#58515f')        # black leather (cord, grips, claw glove)
WOOD = ramp('#24140a', '#5a3519', '#7d4c26', '#a06a38', '#c48e56')           # wand / staff / Bo wood (placeholder)
BOOK = ramp('#1e0e07', '#4c2414', '#6e3820', '#8e4e2e', '#ae6a42')           # spellbook brown leather
PAGES = ramp('#5a4c34', '#b4a27c', '#d8c8a0', '#ece0bc', '#fbf4dc')
SKIN = ramp('#4a453f', '#7e776c', '#968e81', '#ada596', '#c6bfb0')           # neutral mannequin grey (as light-armor)

TIERS = [
    # name, level band, metal ramp
    ('Copper', 'Lv 10-18', ramp('#3b1a0c', '#8a4220', '#c26a34', '#e89558', '#ffc48e')),
    ('Iron', 'Lv 15-23', ramp('#24282e', '#5c646e', '#8e97a2', '#bcc4cc', '#eef2f5')),
    ('Thorium', 'Lv 20-28', ramp('#1c3324', '#3f6b4a', '#5e9468', '#8cc08e', '#cdebc6')),
    ('Cobalt', 'Lv 25-38', ramp('#121b3d', '#2a3f8a', '#3f63c4', '#6f95e6', '#b9d0ff')),
    ('Adamantite', 'Lv 35-43', ramp('#3a0c10', '#7a1a20', '#b42c30', '#e0574f', '#ffa192')),
    ('Mithril', 'Lv 40-49', ramp('#1e3a44', '#4e8c98', '#7ec4cc', '#b4ecee', '#f2ffff')),
    ('Onyxium', 'Lv 40-49', ramp('#160c22', '#3e2460', '#6b3fa0', '#a06cda', '#e4c8ff')),
]
GLOW = {'Onyxium': hx('#ff7af0'), 'Mithril': hx('#ffffff'), 'Adamantite': hx('#ffd0c8')}

# leaf / staff crystal per tier (wand + staff). Placeholder guesses - the lock says "tier-coloured leaf crystals" and the
# 2026-10-02 art proof took them from each tier's vanilla staff gem (UNVERIFIED here: no game files in the cloud).
CRYSTAL = [
    ramp('#0c3a24', '#1f7a4a', '#34b06a', '#6ee09a', '#d2ffe2'),   # Copper  - green
    ramp('#0c2c4a', '#1f5f9a', '#3a8fd6', '#7cc0f2', '#e0f4ff'),   # Iron    - sky blue
    ramp('#2e3a08', '#647a14', '#98b424', '#c8e050', '#f4ffc0'),   # Thorium - lime
    ramp('#08343e', '#13707e', '#22b0be', '#6ee6ee', '#e0ffff'),   # Cobalt  - ice cyan
    ramp('#3e0c06', '#8a2410', '#d4461c', '#ff8a46', '#ffe0b0'),   # Adamantite - ember orange-red
    ramp('#1c3a40', '#5aa0aa', '#a8e4e4', '#e0fbf8', '#ffffff'),   # Mithril - white-aqua
    ramp('#2a0626', '#6e1466', '#b42aa8', '#ec6ad8', '#ffd0f6'),   # Onyxium - magenta
]
# soul + gems per Soul Cage tier = the tier's ESSENCE colour (research/cloud/Soul-Orb-Spec.md section 1), not the metal
ESSENCE = [
    ('Life', ramp('#0c3a14', '#1f7a2c', '#3cba4a', '#82ec7e', '#e0ffd8')),
    ('Fire', ramp('#3e0806', '#8a1610', '#d22e1e', '#ff7448', '#ffd8b8')),
    ('Ice', ramp('#08303e', '#136a86', '#28a8cc', '#78dcf2', '#e4fbff')),
    ('Lightning', ramp('#3e3006', '#8a6a10', '#d2aa1e', '#fae05a', '#fffbd0')),
    ('Void', ramp('#22083a', '#4e167a', '#8030c0', '#b674ec', '#ecd4ff')),
    ('Wind', ramp('#24382c', '#6a9478', '#a8d4b4', '#dcf6e2', '#ffffff')),
    ('Void heart', ramp('#06040a', '#1a1024', '#36204c', '#6a3a96', '#d08cff')),
]
TETHERS = [2, 4, 6, 10, 14, 16, 20]          # Soul-Orb-Spec section 1 (gems on the model = tethers)
# hand-wrap cloth ladder (Monk-Kit-Spec section 2), aligned to the metal columns by level band
CLOTH = [
    ('Linen Wraps', ramp('#4a3e2a', '#9a8660', '#c2ae84', '#ddcca4', '#f2e6c8')),
    ('Cotton Wraps', ramp('#4e5054', '#a4a8ae', '#cdd0d4', '#e8eaec', '#ffffff')),
    ('Silk Wraps', ramp('#4a2a3a', '#a4708a', '#d4a2b8', '#f0cede', '#fff0f6')),
    ('Cindercloth Wraps', ramp('#3e1206', '#8a2c10', '#c8521e', '#f08a3a', '#ffd08a')),
    ('Shadoweave Wraps', ramp('#0e0a16', '#2a2238', '#40355a', '#5c4e80', '#8c7cb4')),
    None,   # Mithril band: Prisma / Moon cloth later
    None,   # Onyxium band: none
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
    return {(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}


def ell(x0, y0, x1, y1):
    return _draw(lambda d: d.ellipse((x0, y0, x1, y1), fill=1))


def poly(pts):
    return _draw(lambda d: d.polygon([tuple(p) for p in pts], fill=1))


def ring(cx, cy, r0, r1):
    return ell(cx - r1, cy - r1, cx + r1, cy + r1) - ell(cx - r0, cy - r0, cx + r0, cy + r0)


class Axis:
    """a straight item axis from A (butt) to B (tip); t = 0..1 along it"""

    def __init__(self, a, b):
        self.a, self.b = a, b
        dx, dy = b[0] - a[0], b[1] - a[1]
        self.len = math.hypot(dx, dy)
        self.u = (dx / self.len, dy / self.len)
        self.n = (-self.u[1], self.u[0])

    def p(self, t, off=0.0):
        return (self.a[0] + (self.b[0] - self.a[0]) * t + self.n[0] * off,
                self.a[1] + (self.b[1] - self.a[1]) * t + self.n[1] * off)

    def seg(self, t0, t1, w, w1=None):
        """a (tapered) bar from t0 to t1, width w (-> w1)"""
        w1 = w if w1 is None else w1
        return poly([self.p(t0, -w / 2), self.p(t1, -w1 / 2), self.p(t1, w1 / 2), self.p(t0, w / 2)])

    def tri(self, t0, t1, w):
        """a point: base width w at t0, tip at t1"""
        return poly([self.p(t0, -w / 2), self.p(t1), self.p(t0, w / 2)])

    def leaf(self, t0, t1, w, off=0.0, ang=0.0):
        """leaf / diamond shape from t0 to t1, widest (w) at 40%, optionally turned by ang (radians)"""
        base = self.p(t0, off)
        L = (t1 - t0) * self.len
        ca, sa = math.cos(ang), math.sin(ang)
        ux, uy = self.u[0] * ca - self.u[1] * sa, self.u[0] * sa + self.u[1] * ca
        nx, ny = -uy, ux

        def q(s, o):
            return (base[0] + ux * s + nx * o, base[1] + uy * s + ny * o)
        return poly([q(0, 0), q(L * 0.4, -w / 2), q(L, 0), q(L * 0.4, w / 2)])


# ---------------------------------------------------------------- painter (copied from light-armor/make_sheets.py, grid G)
class Fig:
    def __init__(self):
        self.im = Image.new('RGBA', (G, G), (0, 0, 0, 0))
        self.px = self.im.load()

    def paint(self, mask, rp, pattern=None, outline=True, edge_ref=None):
        """Shade a part: outline on its edge, light top-left, dark bottom-right."""
        mask = {p for p in mask if 0 <= p[0] < G and 0 <= p[1] < G}
        ref = edge_ref if edge_ref is not None else mask
        edge = {(x, y) for x, y in mask
                if any(q not in ref for q in ((x, y - 1), (x - 1, y), (x + 1, y), (x, y + 1)))}
        inner = mask - edge if outline else mask

        def out(q):
            return q not in inner

        for (x, y) in mask:
            if outline and (x, y) in edge:
                i = 0
            else:
                lt = out((x, y - 1)) or out((x - 1, y))
                dk = out((x, y + 1)) or out((x + 1, y))
                if lt and dk:
                    i = 2
                elif lt:
                    i = 4 if out((x, y - 1)) and out((x - 1, y)) else 3
                elif dk:
                    i = 1
                else:
                    i = 2
            if pattern:
                i = pattern(x, y, i)
            self.px[x, y] = rp[i]

    def flat(self, mask, col):
        for x, y in mask:
            if 0 <= x < G and 0 <= y < G:
                self.px[x, y] = col

    def dots(self, pts, rp):
        """micro details: list of (x, y, ramp index)"""
        for x, y, i in pts:
            if 0 <= x < G and 0 <= y < G:
                self.px[x, y] = rp[i]

    def glow(self, x, y, col):
        if 0 <= x < G and 0 <= y < G:
            self.px[int(x), int(y)] = col


def stripes(step, keep=(0,)):
    """diagonal wrap lines (cord, grip, cloth)"""
    def f(x, y, i):
        if i == 0:
            return 0
        return 1 if (x + y) % step == 0 else i
    return f


def band_ramp(t, M):
    return GOLD if TIERS[t][0] == 'Mithril' else M


def rp_pt(ax, t, off=0.0):
    x, y = ax.p(t, off)
    return int(round(x)), int(round(y))


# ---------------------------------------------------------------- 1. wand (LOCKED style B)
def draw_wand(t):
    name, _, M = TIERS[t]
    C = CRYSTAL[t]
    B = band_ramp(t, M)
    f = Fig()
    ax = Axis((7, 42), (35, 14))
    # crystals behind the head first (side leaves), then the shaft, head, front crystal
    n_leaf = [1, 1, 3, 3, 3, 3, 3][t]
    if n_leaf >= 2:
        f.paint(ax.leaf(0.84, 1.10, 5, off=-1.5, ang=-0.55), C)
        f.paint(ax.leaf(0.84, 1.10, 5, off=1.5, ang=0.55), C)
    f.paint(ax.seg(0.0, 0.80, 3.4, 2.6), WOOD, pattern=lambda x, y, i: 1 if i in (2, 3) and (x - y) % 7 == 0 else i)
    f.paint(ax.seg(-0.02, 0.06, 4.2), M)                         # butt cap
    for b in [[0.42], [0.42], [0.30, 0.52], [0.30, 0.52], [0.30, 0.52], [0.22, 0.42, 0.60], [0.22, 0.42, 0.60]][t]:
        f.paint(ax.seg(b, b + 0.055, 4.4), B)                    # bands
    # metal head: socket + collar
    f.paint(ax.seg(0.70, 0.84, 4.4, 6.2), M)
    f.paint(ax.seg(0.80, 0.86, 6.8), B)
    if name == 'Cobalt':
        f.paint(poly([ax.p(0.72, -3), ax.p(0.86, -6.5), ax.p(0.84, -3)]), M)
        f.paint(poly([ax.p(0.72, 3), ax.p(0.86, 6.5), ax.p(0.84, 3)]), M)
    if name == 'Adamantite':
        for s in (-1, 1):
            f.paint(poly([ax.p(0.73, 2.5 * s), ax.p(0.80, 7 * s), ax.p(0.80, 2.5 * s)]), M)
    if n_leaf == 3:                                             # middle leaf
        f.paint(ax.leaf(0.84, 1.16, 6), C)
    elif n_leaf == 1:
        f.paint(ax.leaf(0.84, 1.14, 6), C)
    # prongs holding the crystal
    if t >= 1:
        for s in (-1, 1):
            f.paint(poly([ax.p(0.84, 2.6 * s), ax.p(0.95, 3.6 * s), ax.p(0.95, 2.4 * s), ax.p(0.84, 1.4 * s)]), B)
    # glints
    tip = rp_pt(ax, 0.96)
    f.dots([(tip[0] - 1, tip[1], 4)], C)
    if name in GLOW:
        f.glow(*rp_pt(ax, 0.77), GLOW[name])
    return f


# ---------------------------------------------------------------- 2. staff (same family, longer, bigger crystal)
def draw_staff(t):
    name, _, M = TIERS[t]
    C = CRYSTAL[t]
    B = band_ramp(t, M)
    f = Fig()
    ax = Axis((3, 46), (36, 13))
    side = t >= 2
    if side:                                                    # small side leaves behind the big crystal
        f.paint(ax.leaf(0.84, 1.06, 5, off=-3, ang=-0.8), C)
        f.paint(ax.leaf(0.84, 1.06, 5, off=3, ang=0.8), C)
    f.paint(ax.seg(0.0, 0.82, 3.6, 3.0), WOOD, pattern=lambda x, y, i: 1 if i in (2, 3) and (x - y) % 7 == 0 else i)
    f.paint(ax.seg(-0.02, 0.05, 4.6), M)
    f.paint(ax.seg(0.40, 0.52, 3.8), LEATHER, pattern=stripes(3))   # hand grip
    for b in [[0.35, 0.56], [0.35, 0.56], [0.25, 0.35, 0.56], [0.25, 0.35, 0.56, 0.66],
              [0.25, 0.35, 0.56, 0.66], [0.15, 0.25, 0.35, 0.56, 0.66], [0.15, 0.25, 0.35, 0.56, 0.66]][t]:
        f.paint(ax.seg(b, b + 0.04, 4.8), B)
    # head: socket flaring into a cradle
    f.paint(ax.seg(0.74, 0.86, 4.8, 8.0), M)
    f.paint(ax.seg(0.84, 0.88, 8.4), B)
    if name == 'Cobalt':
        for s in (-1, 1):
            f.paint(poly([ax.p(0.76, 3 * s), ax.p(0.90, 8 * s), ax.p(0.86, 3 * s)]), M)
    if name == 'Adamantite':
        for s in (-1, 1):
            f.paint(poly([ax.p(0.74, 3 * s), ax.p(0.80, 8 * s), ax.p(0.82, 3 * s)]), M)
            f.paint(poly([ax.p(0.80, 3.5 * s), ax.p(0.88, 9 * s), ax.p(0.87, 3.5 * s)]), M)
    # the big crystal
    f.paint(ax.leaf(0.86, 1.30, 9), C)
    # cradle prongs around it
    for s in (-1, 1):
        f.paint(poly([ax.p(0.86, 3.4 * s), ax.p(1.02, 5.2 * s), ax.p(1.06, 3.8 * s), ax.p(1.0, 3.4 * s), ax.p(0.88, 1.8 * s)]), B)
    if name in ('Mithril', 'Onyxium'):                         # a ring around the crystal
        f.paint(ax.seg(1.00, 1.04, 7.0) - ax.seg(1.00, 1.04, 3.2), B)
    c = rp_pt(ax, 1.06, -1.5)
    f.dots([(c[0], c[1], 4), (c[0] + 1, c[1], 3)], C)
    if name in GLOW:
        f.glow(*rp_pt(ax, 0.80), GLOW[name])
    return f


# ---------------------------------------------------------------- 3. spellbook (leather book + metal parts)
def draw_book(t):
    name, _, M = TIERS[t]
    f = Fig()
    x0, y0, x1, y1 = 11, 8, 36, 41                               # front cover
    pages = rect(x1 - 1, y0 + 2, x1 + 4, y1 - 1)
    f.paint(pages, PAGES, pattern=lambda x, y, i: 1 if i in (2, 3) and y % 2 == 0 else i)
    f.paint(rect(x1 + 1, y0 + 1, x1 + 5, y0 + 2) | rect(x1 + 4, y0 + 1, x1 + 5, y1), BOOK)   # back cover edge
    cover = rect(x0, y0, x1, y1)
    f.paint(cover, BOOK)
    f.paint(rect(x0 - 4, y0, x0 + 1, y1), BOOK)                  # spine (rounded look by its own shading)
    # tooled border
    f.dots([(x, y0 + 3, 1) for x in range(x0 + 4, x1 - 2)] + [(x, y1 - 3, 1) for x in range(x0 + 4, x1 - 2)]
           + [(x0 + 4, y, 1) for y in range(y0 + 3, y1 - 2)] + [(x1 - 3, y, 1) for y in range(y0 + 3, y1 - 2)], BOOK)
    # spine bands
    nb = 2 if t < 3 else 3
    for yy in ([y0 + 4, y1 - 6] if nb == 2 else [y0 + 4, (y0 + y1) // 2 - 1, y1 - 6]):
        f.paint(rect(x0 - 5, yy, x0 + 1, yy + 2), M)
    # corner caps (grow with tier)
    c = [4, 4, 5, 5, 6, 6, 7][t]
    for (cx, cy, sx, sy) in ((x1, y0, -1, 1), (x1, y1, -1, -1), (x0, y0, 1, 1), (x0, y1, 1, -1)):
        f.paint(poly([(cx, cy), (cx + sx * c, cy), (cx, cy + sy * c)]) | {(cx, cy)}, band_ramp(t, M) if name == 'Onyxium' else M)
    if name == 'Mithril' or name == 'Onyxium':                    # filigree lines from the corners
        G2 = GOLD
        f.dots([(x0 + c + 1, y0 + 4, 3), (x1 - c - 1, y0 + 4, 3), (x0 + c + 1, y1 - 4, 2), (x1 - c - 1, y1 - 4, 2)], G2)
    # clasp strap from the back cover over the pages
    cy = (y0 + y1) // 2
    f.paint(rect(x1 - 4, cy - 3, x1 + 6, cy + 3), BOOK if t < 6 else LEATHER)
    f.paint(rect(x1 - 6, cy - 4, x1 - 1, cy + 4), M)            # clasp plate
    f.dots([(x1 - 4, cy, 0), (x1 - 3, cy, 0)], M)
    # cover plate with the tier emblem (same signatures as the light-armor chest piece)
    ex, ey = (x0 + x1) // 2 - 1, cy - 1
    if name == 'Copper':
        f.paint(ring(ex, ey, 2, 4.6), M)
    elif name == 'Iron':
        f.paint(rect(ex - 4, ey - 4, ex + 4, ey + 4), M)
        f.dots([(ex - 3, ey - 3, 0), (ex + 3, ey - 3, 0), (ex - 3, ey + 3, 0), (ex + 3, ey + 3, 0)], M)
    elif name == 'Thorium':
        f.paint(ell(ex - 5, ey - 5, ex + 5, ey + 5), M)
        f.paint(ell(ex - 2, ey - 2, ex + 2, ey + 2), M)
    elif name == 'Cobalt':
        f.paint(poly([(ex, ey - 7), (ex + 5, ey), (ex, ey + 7), (ex - 5, ey)]), M)
        f.paint(poly([(ex, ey - 3), (ex + 2, ey), (ex, ey + 3), (ex - 2, ey)]), CRYSTAL[t])
    elif name == 'Adamantite':
        f.paint(poly([(ex - 6, ey + 5), (ex - 3, ey - 3), (ex - 1, ey + 5)]), M)
        f.paint(poly([(ex + 1, ey + 5), (ex + 4, ey - 3), (ex + 6, ey + 5)]), M)
        f.paint(poly([(ex - 3, ey + 6), (ex, ey - 8), (ex + 3, ey + 6)]), M)
    elif name == 'Mithril':
        f.paint(poly([(ex, ey - 7), (ex + 2, ey - 2), (ex + 7, ey), (ex + 2, ey + 2), (ex, ey + 7),
                      (ex - 2, ey + 2), (ex - 7, ey), (ex - 2, ey - 2)]), M)
        f.glow(ex, ey, GLOW['Mithril'])
    else:   # Onyxium: gold setting + big violet gem
        f.paint(ell(ex - 6, ey - 6, ex + 6, ey + 6), GOLD)
        f.paint(ell(ex - 3, ey - 4, ex + 3, ey + 4), M)
        f.glow(ex - 1, ey - 2, GLOW['Onyxium'])
    if name == 'Adamantite':
        f.glow(ex, ey - 4, GLOW['Adamantite'])
    return f


# ---------------------------------------------------------------- 4. Soul Cage (dodecahedron lattice, gems = tethers)
def dodeca():
    phi = (1 + 5 ** 0.5) / 2
    v = [(x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
    for a in (-1, 1):
        for b in (-1, 1):
            v += [(0, a / phi, b * phi), (a / phi, b * phi, 0), (a * phi, 0, b / phi)]
    e = [(i, j) for i in range(20) for j in range(i + 1, 20)
         if abs(math.dist(v[i], v[j]) - 2 / phi) < 1e-6]
    return v, e


def draw_cage(t):
    name, _, M = TIERS[t]
    ess_name, E = ESSENCE[t]
    f = Fig()
    v, e = dodeca()
    a, b = 0.42, 0.33                                           # fixed tilt so all 20 corners show

    def rot(p):
        x, y, z = p
        x, z = x * math.cos(a) - z * math.sin(a), x * math.sin(a) + z * math.cos(a)
        y, z = y * math.cos(b) - z * math.sin(b), y * math.sin(b) + z * math.cos(b)
        return x, y, z
    R = [rot(p) for p in v]
    cx, cy, s = 24, 26.5, 10.8
    P = [(cx + x * s, cy + y * s, z) for x, y, z in R]
    # hanging loop on top
    top = min(range(20), key=lambda i: P[i][1])
    f.paint(ring(cx, P[top][1] - 4, 1.5, 3.4), M)
    # back edges (dark), then the soul, then the front edges (bright)

    def edge_mask(i, j):
        (x0, y0, _), (x1, y1, _) = P[i], P[j]
        return _draw(lambda d: d.line((x0, y0, x1, y1), fill=1, width=2))
    back = [(i, j) for i, j in e if P[i][2] + P[j][2] > 0]
    front = [(i, j) for i, j in e if P[i][2] + P[j][2] <= 0]
    for i, j in back:
        f.flat(edge_mask(i, j), M[1])
    # the soul: glowing ball + wisps
    f.paint(ell(cx - 7, cy - 7, cx + 7, cy + 7), E)
    f.paint(ell(cx - 3, cy - 4, cx + 2, cy + 1), E, outline=False, pattern=lambda x, y, i: 4 if i >= 2 else 3)
    f.glow(cx - 2, cy - 3, hx('#ffffff') if t != 6 else GLOW['Onyxium'])
    for i, j in front:
        m = edge_mask(i, j)
        f.flat(m, M[2])
        (x0, y0, _), (x1, y1, _) = P[i], P[j]
        f.flat(_draw(lambda d: d.line((x0, y0 - 0.6, x1, y1 - 0.6), fill=1, width=1)) & m, M[3])
    # 20 corner nodes; the first TETHERS[t] (front-most first) are gems in the essence colour
    order = sorted(range(20), key=lambda i: (P[i][2], P[i][1], P[i][0]))
    gems = set(order[:TETHERS[t]])
    for i in sorted(range(20), key=lambda i: -P[i][2]):           # far nodes first
        x, y = int(round(P[i][0])), int(round(P[i][1]))
        if i in gems:
            f.paint(rect(x - 1, y - 1, x + 1, y + 1), E)
            f.dots([(x - 1, y - 1, 4)], E)
        else:
            f.paint(rect(x - 1, y - 1, x, y), M)
    return f


# ---------------------------------------------------------------- 5. kunai
def draw_kunai(t):
    name, _, M = TIERS[t]
    f = Fig()
    ax = Axis((9, 39), (41, 7))
    # ring pommel
    rx, ry = rp_pt(ax, -0.06)
    f.paint(ring(rx, ry, 1.6, 4.2), M)
    # cord-wrapped handle (the cord stays on every tier)
    f.paint(ax.seg(0.02, 0.40, 3.6), LEATHER, pattern=stripes(3))
    f.paint(ax.seg(0.38, 0.44, 4.8), GOLD if name in ('Mithril', 'Onyxium') else M)   # collar
    # blade: a leaf / diamond, widest at about 60%
    w = [8, 8, 9, 9, 9, 9, 10][t]
    if name == 'Cobalt':
        blade = poly([ax.p(0.43, -2), ax.p(0.58, -w / 2), ax.p(0.66, -w / 2 + 1), ax.p(1.0), ax.p(0.66, w / 2 - 1),
                      ax.p(0.58, w / 2), ax.p(0.43, 2)])
    else:
        blade = poly([ax.p(0.43, -2), ax.p(0.62, -w / 2), ax.p(1.0), ax.p(0.62, w / 2), ax.p(0.43, 2)])
    if name == 'Adamantite':                                    # serrated back edge
        for k in (0.66, 0.74, 0.82):
            blade -= poly([ax.p(k, -w / 2 + 0.5), ax.p(k + 0.04, -w / 2 + 2.6), ax.p(k + 0.08, -w / 2 + 0.5)])
    f.paint(blade, M)
    if t >= 1:                                                  # fuller / ridge line
        for k in range(14):
            x, y = rp_pt(ax, 0.48 + k * 0.032)
            f.dots([(x, y, 1)], M)
    if name in GLOW:
        f.glow(*rp_pt(ax, 0.62, 1), GLOW[name])
        if name == 'Onyxium':
            f.glow(*rp_pt(ax, 0.86, 1), GLOW[name])
    return f


# ---------------------------------------------------------------- 6. Bo staff (wood shaft + metal caps and bands)
def draw_bo(t):
    name, _, M = TIERS[t]
    B = band_ramp(t, M)
    if name == 'Onyxium':
        B = GOLD
    f = Fig()
    ax = Axis((4, 44), (44, 4))
    f.paint(ax.seg(0.02, 0.98, 3.6), WOOD, pattern=lambda x, y, i: 1 if i in (2, 3) and (x - y) % 9 == 0 else i)
    f.paint(ax.seg(0.42, 0.58, 4.2), LEATHER, pattern=stripes(3))   # centre grip
    cap = [0.08, 0.08, 0.10, 0.10, 0.11, 0.11, 0.12][t]
    cw = [4.6, 4.6, 5.4, 4.8, 5.0, 5.0, 5.4][t]
    for t0, t1 in ((-0.01, cap), (1 - cap, 1.01)):
        f.paint(ax.seg(t0, t1, cw), M)
    if name == 'Cobalt':                                        # pointed tips
        f.paint(ax.tri(1.0, 1.06, 4.2), M)
        f.paint(ax.tri(0.0, -0.06, 4.2), M)
    if name == 'Adamantite':                                    # cap spikes
        for tc in (cap * 0.5, 1 - cap * 0.5):
            for s in (-1, 1):
                f.paint(poly([ax.p(tc - 0.03, 2 * s), ax.p(tc, 5.5 * s), ax.p(tc + 0.03, 2 * s)]), M)
    nb = [1, 1, 2, 2, 2, 3, 3][t]
    for k in range(nb):
        for base, sgn in ((cap, 1), (1 - cap, -1)):
            b = base + sgn * (0.035 + k * 0.06)
            f.paint(ax.seg(min(b, b + sgn * 0.03), max(b, b + sgn * 0.03), 4.6), B)
    if name == 'Iron':
        for tc in (cap * 0.5, 1 - cap * 0.5):
            f.dots([(*rp_pt(ax, tc, -1), 4)], M)
    if name in GLOW:
        f.glow(*rp_pt(ax, 0.5, -1), GLOW[name])
    return f


# ---------------------------------------------------------------- 7-9. fist weapons (front view of a closed fist)
def fist_parts(dy=0):
    knuck = [rect(13 + 6 * k, 12 + dy + (1 if k in (0, 3) else 0), 18 + 6 * k, 19 + dy) for k in range(4)]
    hand = rect(13, 17 + dy, 36, 31 + dy)
    thumb = rect(8, 20 + dy, 14, 30 + dy) | rect(10, 18 + dy, 14, 20 + dy)
    cuff = poly([(14, 31 + dy), (35, 31 + dy), (38, 44), (11, 44)])
    return knuck, hand, thumb, cuff


def draw_gauntlet(t):
    name, _, M = TIERS[t]
    T = GOLD if name in ('Mithril', 'Onyxium') else M
    f = Fig()
    knuck, hand, thumb, cuff = fist_parts()
    f.paint(rect(12, 17, 37, 33), LEATHER)                      # leather under the plates
    f.paint(cuff, M)
    f.paint(rect(12, 31, 37, 33) | rect(11, 42, 38, 44), T)     # cuff rims
    f.paint(rect(14, 21, 35, 30), M)                            # back-of-hand plate
    f.paint(thumb, M)
    for k in knuck:
        f.paint(k, M)
    if name == 'Iron':
        f.dots([(15, 23, 0), (34, 23, 0), (15, 28, 0), (34, 28, 0), (16, 37, 0), (24, 37, 0), (33, 37, 0)], M)
    if name == 'Thorium':
        for k in range(4):
            f.paint(ell(14 + 6 * k, 13, 17 + 6 * k, 16), M)
    if name == 'Cobalt':
        for k in range(4):
            f.paint(poly([(14 + 6 * k, 13), (15.5 + 6 * k, 8), (17 + 6 * k, 13)]), M)
        f.paint(poly([(18, 22), (24.5, 28), (31, 22), (31, 24), (24.5, 30), (18, 24)]), M)
    if name == 'Adamantite':
        for k in range(4):
            f.paint(poly([(14 + 6 * k, 13), (16 + 6 * k, 5), (18 + 6 * k, 13)]), M)
        f.paint(poly([(36, 34), (42, 36), (37, 39)]), M)
        f.paint(poly([(13, 34), (7, 36), (12, 39)]), M)
    if name in ('Mithril', 'Onyxium'):
        f.paint(rect(14, 20, 35, 21), GOLD)
        f.paint(ell(21, 22, 28, 29), GOLD)
        f.paint(ell(23, 24, 26, 27), CRYSTAL[t] if name == 'Mithril' else M)
        f.glow(24, 25, GLOW[name])
    return f


def draw_claws(t):
    name, _, M = TIERS[t]
    f = Fig()
    dy = 4
    knuck, hand, thumb, cuff = fist_parts(dy)
    # blades first (they come out between the knuckles, behind the knuckle band)
    L = [12, 12, 13, 14, 15, 16, 16][t]
    for k in range(3):
        bx = 18 + 6 * k
        base_y = 18
        blade = poly([(bx - 1.5, base_y), (bx + 1.5, base_y), (bx + 3.0, base_y - L * 0.55), (bx + 2.5, base_y - L),
                      (bx + 0.8, base_y - L * 0.55)])
        if name == 'Adamantite':
            blade |= poly([(bx + 1.5, base_y - L * 0.4), (bx - 1.5, base_y - L * 0.5), (bx + 1.2, base_y - L * 0.6)])
        f.paint(blade, M)
        if name in GLOW:
            f.glow(bx + 2, base_y - L + 3, GLOW[name])
    f.paint(hand | thumb | rect(13, 17 + dy - 2, 36, 18 + dy), LEATHER)
    for k in knuck:
        f.paint(k, LEATHER)
    f.paint(cuff, LEATHER)
    f.dots([(x, y, 0) for x in (18, 24, 30) for y in range(25, 32)] + [(x, 28 + dy - 1, 1) for x in range(14, 36)], LEATHER)
    f.dots([(x + 1, y, 3) for x in (18, 24, 30) for y in range(25, 31)], LEATHER)
    T = GOLD if name in ('Mithril', 'Onyxium') else M
    f.paint(rect(12, 15 + dy, 37, 19 + dy), M)                   # knuckle band holding the blades
    f.paint(rect(13, 31 + dy, 36, 33 + dy) if dy < 10 else set(), T)   # wrist strap
    if t >= 1:
        f.dots([(15 + 6 * k, 17 + dy, 0) for k in range(4)], M)
    f.paint(rect(21, 34 + dy, 27, 38 + dy) & cuff, M)           # strap buckle
    return f


def draw_wraps(t):
    if CLOTH[t] is None:
        return None
    cname, C = CLOTH[t]
    f = Fig()
    knuck, hand, thumb, cuff = fist_parts()
    f.paint(rect(12, 12, 37, 31), SKIN)                          # bare finger tips show between
    for k in knuck:
        f.paint(k, SKIN)
    f.paint(thumb, SKIN)
    # cloth strips: around the knuckles, palm and wrist
    f.paint(rect(12, 15, 37, 19), C)
    f.paint(rect(12, 21, 37, 25), C)
    f.paint(rect(12, 26, 37, 31), C)
    f.paint(rect(8, 23, 14, 27), C)
    f.paint(cuff, C, pattern=lambda x, y, i: 1 if i in (2, 3) and y % 4 == 0 else i)
    # loose tail
    f.paint(poly([(33, 40), (38, 38), (44, 46), (40, 47)]), C)
    if t >= 3:                                                  # Cindercloth / Shadoweave: a stitched edge
        f.dots([(x, 20, 4 if t == 3 else 3) for x in range(13, 37, 3)], C)
    return f


# ---------------------------------------------------------------- output
ROWS = [
    ('Wand', 'style B (LOCKED): wood handle,\nmetal head + bands, leaf crystals;\ngold bands on Mithril', draw_wand),
    ('Staff', 'same family, longer,\nbig crystal in a metal cradle', draw_staff),
    ('Spellbook', 'brown leather book; metal\ncorners, spine bands, clasp,\ntier emblem plate', draw_book),
    ('Soul Cage', 'soul in a dodecahedron lattice;\ngems = tethers (2..20);\nsoul + gems = essence colour', draw_cage),
    ('Kunai', 'metal blade, black cord wrap,\nring pommel', draw_kunai),
    ('Bo staff', 'wood shaft, metal caps\n+ bands, leather centre grip', draw_bo),
    ('Gauntlets', 'fist weapon: metal plates\non a leather glove', draw_gauntlet),
    ('Claws', 'fist weapon: black leather\nglove + 3 metal blades', draw_claws),
    ('Hand wraps', 'fist weapon: CLOTH ladder\n(not metal), aligned by band', draw_wraps),
]


def font(n):
    return ImageFont.load_default(size=n)


def icon(f, s=SCALE):
    im = f.im.resize((G * s, G * s), Image.NEAREST)
    base = Image.new('RGBA', im.size, BG_CELL)
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
    for k, line in enumerate(lines):
        d.text((size // 2, size // 2 - 20 + k * 22), line, font=font(16), fill=DIM, anchor='mt')
    return im


def save(im, name):
    im = im.convert('RGB').quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    im.save(os.path.join(OUT, name), optimize=True)


def slug(s):
    return s.lower().replace(' ', '-')


def main():
    cell = G * SCALE
    gap, labh = 14, 44
    figs = {row: [fn(t) for t in range(len(TIERS))] for row, _, fn in ROWS}

    # per-type strips
    for row, note, _ in ROWS:
        w = len(TIERS) * cell + (len(TIERS) + 1) * gap
        h = 56 + cell + labh + gap
        im = Image.new('RGBA', (w, h), BG)
        d = ImageDraw.Draw(im)
        d.text((gap, 14), f'SkyWynn {row} - concept (cloud draft)', font=font(26), fill=INK)
        d.text((w - gap, 20), note.replace('\n', ' '), font=font(14), fill=SUB, anchor='ra')
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
        save(im, f'{slug(row)}.png')

    # combined sheet: rows = weapon type, columns = metal
    lw = 250
    top = 124
    rowh = cell + labh - 10
    w = lw + len(TIERS) * (cell + gap) + gap
    h = top + len(ROWS) * (rowh + gap) + gap
    sheet = Image.new('RGBA', (w, h), BG)
    d = ImageDraw.Draw(sheet)
    d.text((w // 2, 16), 'SkyWynn magic + new weapons - concept (cloud draft)', font=font(34), fill=INK, anchor='mt')
    for t, (name, band, M) in enumerate(TIERS):
        x = lw + t * (cell + gap)
        d.text((x + cell // 2, 62), name, font=font(24), fill=INK, anchor='mt')
        d.text((x + cell // 2, 88), band, font=font(14), fill=SUB, anchor='mt')
        for j, col in enumerate([M[3], M[2], M[1]]):
            sx = x + cell // 2 - 22 + j * 16
            d.rectangle((sx, 106, sx + 12, 118), fill=col, outline=M[0])
    for r, (row, note, _) in enumerate(ROWS):
        y = top + r * (rowh + gap)
        d.text((gap, y + 40), row, font=font(26), fill=INK)
        for k, line in enumerate(note.split('\n')):
            d.text((gap, y + 76 + k * 18), line, font=font(13), fill=SUB)
        for t in range(len(TIERS)):
            x = lw + t * (cell + gap)
            fg = figs[row][t]
            if fg is None:
                sheet.paste(placeholder(cell, ['later', '(Prisma / Moon cloth)' if t == 5 else '(no wraps)']), (x, y))
            else:
                sheet.paste(icon(fg), (x, y))
            sub = sub_for(row, t)
            if row in ('Soul Cage', 'Hand wraps'):
                d.text((x + cell // 2, y + cell + 6), sub, font=font(13), fill=SUB, anchor='mt')
    save(sheet, 'weapon-sheet.png')


if __name__ == '__main__':
    main()
