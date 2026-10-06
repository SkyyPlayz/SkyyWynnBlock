#!/usr/bin/env python3
"""SkyWynn booster accessories - icon concepts v2 (cloud draft 2026-10-06).

Same 11 designs x 4 rarities as make_icons.py (v1, 32 x 32, Skyy: "Love them"),
redrawn at vanilla icon density: native 64 x 64 with much more surface detail
(dome shading from a distance field, 6-step ramps, cast shadows between parts,
real chain links, faceted gems, leather grain + stitching, feather barbs,
stone speckle + cracks, glass reflections, glow).

Original pixel art, drawn from code (no copied art, no game files).
Run:  python3 research/cloud/accessory-art/make_icons_v2.py
Writes icons-v2/<line>-<rarity>.png (64 x 64, transparent) and
accessory-sheet-v2.png next to this script. v1 files are not touched.
Deterministic: same code -> same bytes.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.dirname(os.path.abspath(__file__))
W = H = 64


def hx(s):
    s = s.lstrip('#')
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def ramp(*cols):
    """[outline, dark, mid, light, highlight]"""
    return [hx(c) for c in cols]


def mix(a, b, t=0.5):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3)) + (255,)


def lv(rp):
    """7 levels: 0 outline, 1 dark, 2 dark-mid, 3 mid, 4 mid-light, 5 light, 6 highlight"""
    return [rp[0], rp[1], mix(rp[1], rp[2]), rp[2], mix(rp[2], rp[3]), rp[3], rp[4]]


def h(x, y, s=0):
    """deterministic hash noise 0..1"""
    n = (x * 374761393 + y * 668265263 + s * 2147483647) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFF) / 65535.0


# ---------------------------------------------------------------- rarities (same as v1)
RARITIES = [
    ('Normal', '#FFFFFF',
     ramp('#3a3d44', '#9aa0a8', '#cdd2d8', '#eef0f3', '#ffffff'),
     ramp('#24282e', '#4e555e', '#77808a', '#a2abb4', '#cfd6dc')),          # iron
    ('Unique', '#FFFF55',
     ramp('#4a400a', '#b4a41c', '#e6e23e', '#ffff55', '#ffffd0'),
     ramp('#4a3208', '#9a6e18', '#d4a234', '#f0c860', '#fff0b0')),          # gold
    ('Rare', '#FF55FF',
     ramp('#4a0c48', '#a42aa4', '#e044e0', '#ff55ff', '#ffd4ff'),
     ramp('#3e1a1e', '#8e4a4c', '#c87c72', '#eeaa98', '#ffe2d4')),          # rose gold
    ('Legendary', '#55FFFF',
     ramp('#0a3a42', '#1c9aa4', '#34d4dc', '#55ffff', '#e4ffff'),
     ramp('#2a3440', '#6e7e90', '#a8b8c8', '#d8e4ee', '#ffffff')),          # platinum
]
GLOW = hx('#55ffff')

RED = ramp('#3a0a10', '#8a1422', '#c8283a', '#ec5a62', '#ffa8a8')
LEATHER = ramp('#1c1009', '#4a2c18', '#6e4426', '#946238', '#b88a5a')
SOLE = ramp('#120a06', '#2a1a0e', '#3e2816', '#56391f', '#6e4c2c')
LACE = ramp('#3a2a08', '#8a6a18', '#c89a2a', '#eac45a', '#fff0a0')
GLASS = ramp('#1a2a3a', '#4a6a86', '#7a9ab4', '#a8c6dc', '#e8f6ff')
MANA = ramp('#0c1a4a', '#1e3c9a', '#2e60d8', '#5a8cf0', '#a8c8ff')
CORK = ramp('#2a1a0c', '#6a4424', '#8e6034', '#b0824c', '#d2a874')
WING = ramp('#0c3a44', '#2a8a9a', '#4ac0cc', '#8ae6ee', '#dafcff')
LEAF = ramp('#0e2a12', '#24602a', '#3a8e3c', '#6cbc5a', '#b4e89a')
GRIP = ramp('#3a0c0c', '#7a1c1c', '#a83030', '#d05050', '#f08a80')
RUNE = ramp('#1a1622', '#3e3650', '#5a5070', '#7a7090', '#a49cb8')
RUNEGLOW = hx('#c070ff')
RUNECORE = hx('#f0d8ff')
STONE = ramp('#22221f', '#555349', '#7a776a', '#a09c8c', '#c8c4b2')
BONE = ramp('#3a3020', '#9a8a68', '#c8b890', '#e6dab8', '#fff8e8')
CORD = ramp('#1a0c08', '#4a2014', '#6e3420', '#904a30', '#b06a48')
FEATHER = ramp('#3a3d48', '#9aa2b4', '#c8d0de', '#e8eef6', '#ffffff')
FLAME = ramp('#5a1a00', '#c04a00', '#ff8a1a', '#ffc84a', '#fff4b0')

INK = (34, 36, 40, 255)
BG = hx('#b4b9bf')
SLOT = hx('#2b313d')
SLOT_EDGE = hx('#454d5c')


# ---------------------------------------------------------------- masks
def rect(x0, y0, x1, y1):
    return {(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}


def _draw(fn):
    im = Image.new('1', (W, H), 0)
    fn(ImageDraw.Draw(im))
    px = im.load()
    return {(x, y) for x in range(W) for y in range(H) if px[x, y]}


def ell(x0, y0, x1, y1):
    return _draw(lambda d: d.ellipse((x0, y0, x1, y1), fill=1))


def ring(x0, y0, x1, y1, w):
    return _draw(lambda d: d.ellipse((x0, y0, x1, y1), outline=1, width=w))


def poly(pts):
    return _draw(lambda d: d.polygon(pts, fill=1))


def line(pts, w=1):
    return _draw(lambda d: d.line(pts, fill=1, width=w))


def grow(m, n=1):
    for _ in range(n):
        m = m | {(x + dx, y + dy) for x, y in m for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))}
    return m


def mirror(m):
    return {(W - 1 - x, y) for x, y in m}


def blade(root, tip, wl, wr, bow=0.0, start=0.0, power=0.6, steps=40):
    """a tapered leaf / feather shape from root to tip: half-widths wl (left of
    the root->tip direction) and wr, an optional bow of the centre line.
    Returns (mask, centre(t) function, unit dir, unit normal)."""
    (x0, y0), (x1, y1) = root, tip
    L = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    nx, ny = -uy, ux

    def c(t):
        b = bow * math.sin(math.pi * t)
        return (x0 + (x1 - x0) * t + nx * b, y0 + (y1 - y0) * t + ny * b)

    left, right = [], []
    for k in range(steps + 1):
        t = start + (1 - start) * k / steps
        u = (t - start) / (1 - start)
        w = math.sin(math.pi * min(u, 1) * 0.5 + math.pi * 0.5 * u) ** power if u < 1 else 0
        w = max(0.0, math.sin(math.pi * u)) ** power
        px, py = c(t)
        left.append((px - nx * wl * w, py - ny * wl * w))
        right.append((px + nx * wr * w, py + ny * wr * w))
    m = poly(left + right[::-1])
    return m, c, (ux, uy), (nx, ny)


# ---------------------------------------------------------------- painter
class Icon:
    def __init__(self):
        self.im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        self.px = self.im.load()

    def get(self, x, y):
        return self.px[x, y] if 0 <= x < W and 0 <= y < H else (0, 0, 0, 0)

    def set(self, x, y, col):
        if 0 <= x < W and 0 <= y < H:
            if len(col) == 4 and col[3] < 255:
                self.blend(x, y, col[:3], col[3] / 255)
            else:
                self.px[x, y] = col

    def blend(self, x, y, rgb, a):
        if not (0 <= x < W and 0 <= y < H):
            return
        o = self.px[x, y]
        if o[3] == 0:
            self.px[x, y] = tuple(rgb) + (round(255 * a),)
        else:
            oa = o[3] / 255
            na = a + oa * (1 - a)
            c = tuple(round((rgb[i] * a + o[i] * oa * (1 - a)) / na) for i in range(3))
            self.px[x, y] = c + (round(255 * na),)

    def darken(self, x, y, f=0.62):
        o = self.get(x, y)
        if o[3]:
            self.px[x, y] = (round(o[0] * f), round(o[1] * f), round(o[2] * f), o[3])

    def paint(self, mask, rp, depth=3, tex=None, outline=True, shadow=True, gl=0.18, light=0.42):
        """Dome-shade a part: outline, distance-field bevel lit from the top-left,
        a soft global gradient, optional texture, and a 1-px cast shadow on what
        is already drawn below / right of it."""
        L = lv(rp)
        mask = {p for p in mask if 0 <= p[0] < W and 0 <= p[1] < H}
        if not mask:
            return
        if shadow:
            for x, y in mask:
                for q in ((x + 1, y + 1), (x + 1, y), (x, y + 1)):
                    if q not in mask and self.get(*q)[3] == 255 and h(*q, 7) < 0.9:
                        if q == (x + 1, y + 1):
                            self.darken(*q, 0.7)
        # distance field (capped)
        D = {}
        front = [p for p in mask if any(q not in mask for q in
                 ((p[0] + 1, p[1]), (p[0] - 1, p[1]), (p[0], p[1] + 1), (p[0], p[1] - 1)))]
        for p in front:
            D[p] = 1
        k = 1
        while front and k < depth:
            k += 1
            nf = []
            for x, y in front:
                for q in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if q in mask and q not in D:
                        D[q] = k
                        nf.append(q)
            front = nf
        for p in mask:
            D.setdefault(p, depth)
        xs = [p[0] for p in mask]
        ys = [p[1] for p in mask]
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        hw, hh = max(1, (max(xs) - min(xs)) / 2), max(1, (max(ys) - min(ys)) / 2)

        def d(q):
            return D.get(q, 0)

        for (x, y) in mask:
            if outline and D[(x, y)] == 1:
                i = 0
            else:
                gx = d((x + 1, y)) - d((x - 1, y))
                gy = d((x, y + 1)) - d((x, y - 1))
                slope = max(-1, min(1, (gx + gy) / 2))
                glob = -((x - cx) / hw + (y - cy) / hh) / 2 * gl
                v = 0.42 + light * slope + glob
                i = 1 + max(0, min(5, int(v * 6)))
            if tex:
                i = tex(x, y, i)
            if isinstance(i, int):
                i = L[max(0, min(6, i))]
            self.px[x, y] = i

    def dots(self, pts, rp):
        L = lv(rp)
        for x, y, i in pts:
            self.set(x, y, L[i] if isinstance(i, int) else i)


def noise(amount=0.22, seed=1, lo=1, hi=6):
    """texture: random +/-1 level on some pixels (keeps outline)"""
    def t(x, y, i):
        if i == 0:
            return 0
        n = h(x, y, seed)
        if n < amount / 2:
            i -= 1
        elif n > 1 - amount / 2:
            i += 1
        return max(lo, min(hi, i))
    return t


# ---------------------------------------------------------------- chain links
def chain(ic, pts, M):
    """real chain: alternating open oval links (3x3 ring) and side-on bars,
    every 4 px along the path so the links touch."""
    L = lv(M)
    path = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(abs(x1 - x0), abs(y1 - y0))
        for s in range(n):
            path.append((round(x0 + (x1 - x0) * s / n), round(y0 + (y1 - y0) * s / n)))
    path.append(pts[-1])
    for k, (x, y) in enumerate(path):
        if k % 4 == 2:              # side-on link: bright bar with a dark underside
            ic.set(x, y, L[5])
            if ic.get(x, y + 1)[3] == 0:
                ic.set(x, y + 1, L[0])
    for k, (x, y) in enumerate(path):
        if k % 4 == 0:              # open link, seen face-on
            for dx, dy, i in ((-1, -1, 6), (0, -1, 5), (1, -1, 4), (-1, 0, 5), (1, 0, 2),
                              (-1, 1, 3), (0, 1, 1), (1, 1, 0)):
                ic.set(x + dx, y + dy, L[i])


def rivet(ic, x, y, M):
    L = lv(M)
    ic.set(x, y, L[6])
    ic.set(x + 1, y, L[3])
    ic.set(x, y + 1, L[3])
    ic.set(x + 1, y + 1, L[0])


def stitch(ic, pts, rp, every=2, lvl=5, mask=None):
    L = lv(rp)
    k = 0
    for p in line(pts):
        pass
    seq = sorted(line(pts), key=lambda p: (p[0] - pts[0][0]) ** 2 + (p[1] - pts[0][1]) ** 2)
    for x, y in seq:
        if (mask is None or (x, y) in mask) and k % (every + 1) < every - 0:
            if k % (every + 1) == 0:
                ic.set(x, y, L[lvl])
                ic.set(x + 1, y + 1, L[1]) if mask is None or (x + 1, y + 1) in mask else None
        k += 1


# ---------------------------------------------------------------- the rarity gem
def size_of(r):
    return (2, 3, 4, 6)[r]


def gem(ic, cx, cy, r):
    """Rarity marker, same idea as v1 but faceted at 64 px:
    Normal 4x4 round iron-set cabochon; Unique 6x6 gold cabochon; Rare 9-wide
    diamond in rose gold, 4 claws; Legendary 13-wide diamond in platinum,
    claws + milgrain, then halo + sparkles (finish())."""
    _, _, G, M = RARITIES[r]
    GL, ML = lv(G), lv(M)
    if r == 0:
        g = ell(cx - 2, cy - 2, cx + 1, cy + 1)
    elif r == 1:
        g = ell(cx - 3, cy - 3, cx + 2, cy + 2)
    elif r == 2:
        g = poly([(cx, cy - 4), (cx + 4, cy), (cx, cy + 4), (cx - 4, cy)])
    else:
        g = poly([(cx, cy - 6), (cx + 6, cy), (cx, cy + 6), (cx - 6, cy)])
    full = grow(g, 1) if r == 0 else grow(g, 2)
    bez = full - g
    for x, y in bez:
        if any(q not in full for q in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))):
            ic.set(x, y, ML[0])
        else:
            t = (x - cx) + (y - cy)
            ic.set(x, y, ML[6] if t < -size_of(r) else ML[5] if t < 0 else ML[3] if t < size_of(r) else ML[1])
    if r == 3:   # milgrain beads on the bezel
        ring_px = sorted(grow(g, 2) - grow(g, 1), key=lambda p: math.atan2(p[1] - cy, p[0] - cx))
        for j, (x, y) in enumerate(ring_px):
            if j % 2 == 0:
                ic.set(x, y, ML[6] if (x - cx) + (y - cy) < 0 else ML[4])
    if r >= 2:   # claws on the diagonals
        n = 3 if r == 2 else 4
        for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            x, y = cx + dx * n, cy + dy * n
            ic.set(x, y, ML[6] if dx + dy < 0 else ML[3])
            ic.set(x + dx, y + dy, ML[0])
            ic.set(x + dx, y, ML[4] if dy < 0 else ML[2])
            ic.set(x, y + dy, ML[4] if dy < 0 else ML[2])
    # the gem: rim + facets lit from the top-left
    edge = {(x, y) for x, y in g if any(q not in g for q in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))}
    size = size_of(r)
    for x, y in g:
        dx, dy = x - cx + 0.5 * (r <= 1), y - cy + 0.5 * (r <= 1)
        if (x, y) in edge:
            ic.set(x, y, GL[1])
            continue
        if r <= 1:      # cabochon: smooth dome
            v = 0.55 - (dx + dy) / (2 * size) * 0.9
            i = 1 + max(0, min(5, int(v * 6)))
        else:           # brilliant: table + 4 crown facets split by darker girdle lines
            dd = abs(dx) + abs(dy)
            if dd <= size * 0.4:
                i = 5 if dx + dy < 0 else 4
            elif dd <= size * 0.4 + 1:
                i = 6 if dx + dy < 0 else 2
            elif dx == 0 or dy == 0:
                i = 3 if dx + dy < 0 else 1
            elif dx < 0 and dy < 0:
                i = 5
            elif dx > 0 and dy > 0:
                i = 1
            elif dx < 0:
                i = 4
            else:
                i = 3
        ic.set(x, y, GL[i])
    # specular highlight
    if r == 0:
        ic.set(cx - 1, cy - 1, GL[6])
    elif r == 1:
        ic.set(cx - 2, cy - 1, GL[6]); ic.set(cx - 1, cy - 2, GL[6]); ic.set(cx - 1, cy - 1, GL[6])
        ic.set(cx + 1, cy + 1, GL[1])
    else:
        ic.set(cx - 1, cy - 1, GL[6]); ic.set(cx - 2, cy, GL[6]); ic.set(cx, cy - 2, GL[6])
        if r == 3:
            ic.set(cx - 1, cy - 2, GL[6]); ic.set(cx - 2, cy - 1, GL[6])
            ic.set(cx + 2, cy + 2, GL[1]); ic.set(cx + 3, cy + 1, GL[1])


def star(ic, sx, sy, arm, G):
    """4-point sparkle with fading arms"""
    GL = lv(G)
    ic.set(sx, sy, GL[6])
    for k in range(1, arm + 1):
        a = round(255 * (1 - (k - 1) / (arm + 0.5)))
        col = (GL[5][:3] if k == 1 else GL[6][:3] if k == 2 else GL[5][:3]) + (a,)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ic.set(sx + dx * k, sy + dy * k, col)
    if arm >= 3:
        for dx, dy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
            ic.set(sx + dx, sy + dy, GL[5][:3] + (110,))


def finish(ic, r):
    _, _, G, _ = RARITIES[r]
    if r == 2:   # Rare: one pink glint top-right
        if ic.get(55, 8)[3] < 130:
            star(ic, 55, 8, 3, G)
        return
    if r < 3:
        return
    a = {(x, y) for x in range(W) for y in range(H) if ic.px[x, y][3] > 0}
    g1 = grow(a, 1) - a
    g2 = grow(a, 2) - a - g1
    g3 = grow(a, 3) - a - g1 - g2
    for gset, al in ((g3, 28), (g2, 70), (g1, 150)):
        for x, y in gset:
            ic.set(x, y, GLOW[:3] + (al,))
    for sx, sy, arm in ((55, 8, 4), (8, 55, 2), (56, 51, 2)):
        if ic.get(sx, sy)[3] > 160:
            continue
        star(ic, sx, sy, arm, G)


# ---------------------------------------------------------------- the lines
def health(ic, r):
    M = RARITIES[r][3]
    chain(ic, [(7, 4), (18, 15), (29, 19)], M)
    chain(ic, [(56, 4), (45, 15), (34, 19)], M)
    ic.paint(ring(26, 11, 37, 22, 3), M, depth=2)                         # bail
    heart = ell(10, 20, 33, 43) | ell(30, 20, 53, 43) | poly([(12, 36), (51, 36), (32, 58)])
    ic.paint(heart, RED, depth=6, gl=0.25, tex=noise(0.06, 3, 1, 5))
    RL = lv(RED)
    # glossy enamel reflections on both lobes + a soft rim light bottom-right
    for x, y in ell(15, 24, 21, 29) - ell(17, 26, 23, 31):
        ic.set(x, y, RL[6])
    ic.set(16, 31, RL[5]); ic.set(15, 32, RL[5])
    for x, y in ((37, 25), (38, 25), (39, 26)):
        ic.set(x, y, RL[5])
    for x, y in line([(44, 42), (34, 53)]):
        ic.set(x, y, RL[3])
    # metal cap where the bail meets the heart
    ic.paint(poly([(27, 21), (36, 21), (34, 25), (29, 25)]), M, depth=2)
    gem(ic, 32, 37, r)


def stamina(ic, r):
    M = RARITIES[r][3]
    ic.paint(ring(26, 1, 37, 12, 3), M, depth=2)                          # hang ring
    shaft = rect(22, 16, 43, 42)
    foot = (ell(14, 32, 55, 55) & rect(0, 40, 63, 55)) | rect(22, 32, 43, 50)
    leather = shaft | foot
    grain = noise(0.3, 11, 1, 5)
    ic.paint(leather, LEATHER, depth=4, tex=grain)
    LL = lv(LEATHER)
    # toe cap seam + heel counter seam
    for x, y in (ring(38, 38, 62, 62, 1) & leather):
        if y < 53 and x < 56:
            ic.set(x, y, LL[1])
    stitch(ic, [(41, 39), (52, 46)], LEATHER, mask=leather)
    stitch(ic, [(23, 44), (41, 44)], LEATHER, lvl=5, mask=leather)
    # sole with tread
    sole = (ell(13, 36, 56, 59) & rect(0, 51, 63, 58)) | rect(21, 51, 44, 58)
    ic.paint(sole, SOLE, depth=2, light=0.3)
    SL = lv(SOLE)
    for x in range(20, 54, 4):
        ic.set(x, 57, SL[0]); ic.set(x + 1, 57, SL[0])
    for x in range(18, 54):
        if (x, 51) in sole:
            ic.set(x, 51, SL[4] if x % 2 else SL[3])
    # cuff (turned-down top)
    cuff = rect(20, 13, 45, 21)
    ic.paint(cuff, LEATHER, depth=3, tex=noise(0.25, 12, 1, 6))
    stitch(ic, [(21, 20), (44, 20)], LEATHER, lvl=6, mask=cuff)
    # laces: eyelets + criss-cross
    LC = lv(LACE)
    ys = (25, 30, 35, 40)
    for y in ys:
        for x in (26, 38):
            rivet(ic, x, y, M)
    for y0, y1 in zip(ys, ys[1:]):
        for (a, b) in (((27, y0 + 1), (37, y1)), ((37, y0 + 1), (27, y1))):
            for x, y in line([a, b]):
                ic.set(x, y, LC[5] if (x + y) % 3 else LC[3])
                ic.set(x + 1, y + 1, LL[1]) if ic.get(x + 1, y + 1) not in LC else None
    for x, y in line([(37, 41), (43, 47)]) | line([(37, 42), (40, 49)]):   # loose lace ends
        ic.set(x, y, LC[4])
    ic.set(43, 47, LC[6]); ic.set(40, 49, LC[6])
    gem(ic, 32, 17, r)


def mana(ic, r):
    M = RARITIES[r][3]
    chain(ic, [(7, 3), (19, 9), (27, 11)], M)
    chain(ic, [(56, 3), (44, 9), (36, 11)], M)
    cork = rect(26, 7, 37, 18)
    ic.paint(cork, CORK, depth=3, tex=noise(0.4, 21, 1, 6))
    CL = lv(CORK)
    for x, y in ((28, 10), (33, 12), (30, 15), (35, 9)):
        ic.set(x, y, CL[1])
    body = ell(13, 24, 50, 60) | rect(24, 16, 39, 32)
    ic.paint(body, GLASS, depth=3, gl=0.3)
    GL = lv(GLASS)
    # liquid (no outline, sits inside the glass), meniscus, depth, bubbles
    liquid = ell(17, 28, 46, 56) & rect(0, 37, 63, 63)
    ic.paint(liquid, MANA, outline=False, depth=6, gl=0.35, shadow=False, tex=noise(0.08, 22, 1, 5))
    ML = lv(MANA)
    top = min(y for _, y in liquid)
    for x, y in liquid:
        if y == top:
            ic.set(x, y, ML[6] if x % 3 else ML[5])
        elif y == top + 1:
            ic.set(x, y, ML[4])
    for bx, by, br in ((24, 45, 1), (30, 50, 2), (38, 44, 1), (34, 41, 0)):
        if br == 0:
            ic.set(bx, by, ML[6])
        else:
            for x, y in ring(bx - br, by - br, bx + br, by + br, 1):
                ic.set(x, y, ML[5])
            ic.set(bx - br, by - br, ML[6])
    # glass reflections: curved streak upper-left, small one on the right
    for x, y in (ring(17, 27, 46, 56, 1) & rect(0, 0, 25, 41)):
        if (x, y) in body and (x - 17) + (y - 27) > 6:
            ic.set(x + 2, y + 1, GL[6][:3] + (220,))
    for x, y in ((43, 46), (43, 47), (42, 49)):
        ic.set(x, y, GL[5][:3] + (200,))
    for x, y in ((26, 20), (26, 21), (26, 22), (26, 23)):
        ic.set(x, y, GL[6][:3] + (200,))
    ic.paint(rect(22, 19, 41, 25), M, depth=2)                              # neck band
    for x in (24, 38):
        rivet(ic, x, 21, M)
    gem(ic, 32, 22, r)


def wing(ic, flip):
    """one wing: five primaries fanned from the root, then a covert patch"""
    F = mirror if flip else (lambda m: m)
    fx = (lambda x: W - 1 - x) if flip else (lambda x: x)
    WL = lv(WING)
    hole = ell(20, 32, 43, 51)
    feathers = [((27, 38), (14, 42), 4, 4), ((27, 36), (5, 37), 4.5, 4.5), ((27, 34), (2, 29), 4.5, 4.5),
                ((27, 32), (2, 20), 4.5, 4.5), ((27, 30), (5, 11), 4.5, 4.5)]
    for root, tip, a, b in feathers:
        m, c, (ux, uy), (nx, ny) = blade(root, tip, a, b, power=0.35)
        m = F(m) - hole
        ic.paint(m, WING, depth=2, gl=0.1)
        for k in range(4, 22):          # the shaft of each feather
            t = k / 24
            px, py = c(t)
            q = (fx(round(px)), round(py))
            if q in m and ic.get(*q) != WL[0]:
                ic.set(*q, WL[2])
    cov = F(poly([(28, 25), (17, 23), (13, 28), (17, 34), (24, 37), (28, 37)])) - hole
    ic.paint(cov, WING, depth=3, gl=0.2)
    for x, y in cov:                    # two rows of small scalloped coverts
        lx = fx(x)
        if ic.get(x, y) == WL[0]:
            continue
        if (y in (29, 33) and lx < 26) or (lx in (17, 21) and 27 < y < 35):
            ic.set(x, y, WL[2])


def speed(ic, r):
    M = RARITIES[r][3]
    wing(ic, False)
    wing(ic, True)
    band = ring(14, 26, 49, 57, 6)
    ic.paint(band, M, depth=3, light=0.5)
    BL = lv(M)
    for k in range(16):                 # engraved dots round the band
        a = k / 16 * 2 * math.pi
        x, y = round(31.5 + math.cos(a) * 14.5), round(41.5 + math.sin(a) * 13)
        if (x, y) in band:
            ic.set(x, y, BL[1]); ic.set(x - 1, y - 1, BL[6])
    gem(ic, 32, 51, r)


def leaf(ic, root, tip, wl, wr, bow, seed):
    LL = lv(LEAF)
    m, c, (ux, uy), (nx, ny) = blade(root, tip, wl, wr, bow=bow, power=0.75)
    ic.paint(m, LEAF, depth=4, gl=0.25, tex=noise(0.1, seed, 1, 6))
    # midrib (dark with a light edge) and paired side veins
    for k in range(2, 38):
        t = k / 40
        px, py = c(t)
        q = (round(px), round(py))
        if q in m and ic.get(*q) != LL[0]:
            ic.set(*q, LL[1])
            q2 = (q[0] - 1, q[1]) if nx > 0 else (q[0], q[1] - 1)
            if q2 in m and ic.get(*q2) != LL[0]:
                ic.set(*q2, LL[5])
    for t in (0.25, 0.42, 0.59, 0.76):
        px, py = c(t)
        for side in (-1, 1):
            for s_ in range(2, 7):
                q = (round(px + (nx * side * 0.9 + ux * 0.7) * s_), round(py + (ny * side * 0.9 + uy * 0.7) * s_))
                if q in m and ic.get(*q) not in (LL[0],):
                    ic.set(*q, LL[2])
    return m


def regeneration(ic, r):
    M = RARITIES[r][3]
    band = ring(14, 26, 49, 59, 6)
    ic.paint(band, M, depth=3, light=0.5)
    BL = lv(M)
    for x, y in ring(16, 28, 47, 57, 1) & rect(0, 0, 30, 44):
        ic.set(x, y, BL[6])
    leaf(ic, (29, 27), (5, 11), 6, 6, -2, 41)
    leaf(ic, (34, 27), (58, 11), 6, 6, 2, 42)
    leaf(ic, (32, 26), (32, 2), 5, 5, 0, 43)
    # dew drop on the left leaf
    ic.set(13, 17, hx('#e8fcff')); ic.set(14, 17, hx('#7ad0e8')); ic.set(13, 18, hx('#7ad0e8'))
    ic.set(14, 18, hx('#3a8aa8'))
    gem(ic, 32, 28, r)


def brawler(ic, r):
    """clenched fist in a red leather glove, metal knuckle band across it"""
    M = RARITIES[r][3]
    GL = lv(GRIP)
    LL = lv(LEATHER)
    wrap = rect(20, 47, 44, 59)
    ic.paint(wrap, LEATHER, depth=3, tex=noise(0.3, 51, 1, 5))
    for y in (50, 54):                                                     # wrap strips
        for x in range(21, 44):
            ic.set(x, y, LL[1]); ic.set(x, y + 1, LL[4] if x % 3 else LL[3])
    for x, y in line([(21, 58), (32, 48)]):
        ic.set(x, y, LL[5])
    palm = ell(12, 18, 53, 52) | rect(16, 28, 49, 48)
    ic.paint(palm, GRIP, depth=5, tex=noise(0.12, 52, 1, 6))
    for x0 in (12, 22, 32, 42):                                           # 4 fingers
        f = ell(x0, 10, x0 + 11, 27) | rect(x0, 18, x0 + 11, 35)
        ic.paint(f, GRIP, depth=4, gl=0.2, tex=noise(0.12, 53 + x0, 1, 6))
        # knuckle shine + finger crease
        ic.set(x0 + 3, 13, GL[6]); ic.set(x0 + 4, 13, GL[6]); ic.set(x0 + 3, 14, GL[5])
        for x in range(x0 + 3, x0 + 9):
            ic.set(x, 32, GL[1])
            ic.set(x, 33, GL[4])
    thumb = poly([(14, 35), (38, 35), (42, 39), (38, 43), (16, 43)])
    ic.paint(thumb, GRIP, depth=3)
    for x in range(19, 37, 3):                                            # glove stitching on the thumb
        ic.set(x, 41, GL[5])
    for x, y in ((40, 38), (40, 39)):
        ic.set(x, y, GL[1])
    band = rect(12, 21, 53, 29)
    ic.paint(band & (palm | grow(palm, 1)), M, depth=3, light=0.5)
    BL = lv(M)
    for x in range(14, 52):
        if (x, 23) in band:
            ic.set(x, 23, BL[5] if x % 2 else BL[4])
        ic.set(x, 27, BL[2])
    for x in (15, 23, 41, 49):
        rivet(ic, x, 24, M)
    gem(ic, 32, 25, r)


def runic(ic, r):
    M = RARITIES[r][3]
    RL = lv(RUNE)
    stone = poly([(18, 8), (44, 6), (54, 20), (52, 52), (38, 58), (16, 56), (10, 36), (12, 18)])

    def tex(x, y, i):
        if i == 0:
            return 0
        n = h(x, y, 61)
        i = i - (n < 0.14) + (n > 0.9)
        if h(x // 2, y // 2, 62) < 0.08:
            i -= 1
        return max(1, min(6, i))
    ic.paint(stone, RUNE, depth=5, gl=0.3, tex=tex)
    # chipped facets (flat lighter planes) top-left, darker planes bottom-right
    for x, y in poly([(18, 9), (30, 8), (20, 16), (13, 19)]) & stone:
        if ic.get(x, y) != RL[0]:
            ic.set(x, y, RL[5] if h(x, y, 63) > 0.15 else RL[4])
    for x, y in poly([(51, 40), (51, 51), (40, 56), (47, 48)]) & stone:
        if ic.get(x, y) != RL[0]:
            ic.set(x, y, RL[1] if h(x, y, 64) > 0.2 else RL[2])
    # cracks
    for pts in ([(46, 12), (43, 17), (45, 22), (42, 26)], [(14, 44), (19, 46), (21, 51)]):
        for x, y in line(pts):
            if (x, y) in stone:
                ic.set(x, y, RL[0]); ic.set(x - 1, y, RL[5]) if (x - 1, y) in stone else None
    # rune: glow halo, carved groove, bright core
    rune = line([(24, 26), (32, 50)], 3) | line([(40, 26), (32, 50)], 3) | line([(22, 38), (42, 38)], 3)
    for n, a in ((4, 0.12), (3, 0.16), (2, 0.24)):
        for x, y in grow(rune, n) - rune:
            if (x, y) in stone and ic.get(x, y) != RL[0]:
                ic.blend(x, y, RUNEGLOW[:3], a)
    for x, y in grow(rune, 1) - rune:
        if (x, y) in stone and ic.get(x, y) != RL[0]:
            ic.set(x, y, RL[1] if (x + y) % 2 else RL[0])
    for x, y in rune:
        ic.set(x, y, RUNEGLOW)
    for x, y in line([(24, 26), (32, 50)]) | line([(40, 26), (32, 50)]) | line([(22, 38), (42, 38)]):
        if h(x, y, 65) > 0.3:
            ic.set(x, y, RUNECORE)
    gem(ic, 32, 16, r)


def stonehide(ic, r):
    M = RARITIES[r][3]
    SL = lv(STONE)
    cuff = ell(8, 8, 55, 25) | rect(8, 16, 55, 49) | ell(8, 40, 55, 57)

    def tex(x, y, i):
        if i == 0:
            return 0
        n = h(x, y, 71)
        i = i - (n < 0.15) + (n > 0.88)
        # stone blocks: horizontal seams + staggered vertical seams
        row = (y - 18) // 8
        if y > 18 and (y - 18) % 8 == 0:
            return 1
        if y > 18 and (y - 18) % 8 == 1:
            i += 1
        if y > 18 and (x + (row % 2) * 6) % 12 == 0:
            return 1
        if y > 18 and (x + (row % 2) * 6) % 12 == 1:
            i += 1
        return max(1, min(6, i))
    ic.paint(cuff, STONE, depth=6, gl=0.25, tex=tex)
    # open top (arm hole): rim + dark inside
    ic.paint(ell(13, 10, 50, 23), STONE, depth=2, shadow=False, light=-0.4, tex=noise(0.3, 72, 1, 4))
    ic.paint(ell(17, 12, 46, 21), [STONE[0]] * 5, outline=False, shadow=False)
    for x, y in ell(19, 15, 44, 21):
        if y > 17:
            ic.set(x, y, mix(STONE[0], STONE[1], 0.35))
    # chips on the edge
    for x, y in ((9, 30), (9, 31), (54, 37), (20, 55)):
        ic.set(x, y, SL[1])
    for y in (28, 42):
        band = rect(8, y, 55, y + 5) & cuff
        ic.paint(band, M, depth=2, light=0.5)
        BL = lv(M)
        for x in range(9, 55):
            if (x, y + 1) in band:
                ic.set(x, y + 1, BL[5] if x % 2 else BL[6])
        for x in (13, 49):
            rivet(ic, x, y + 2, M)
    gem(ic, 32, 37, r)


def razorfang(ic, r):
    M = RARITIES[r][3]
    CL = lv(CORD)
    cordpts = [(5, 6), (12, 17), (22, 25), (32, 27), (42, 25), (52, 17), (59, 6)]
    cord = line(cordpts, 5)
    ic.paint(cord, CORD, depth=2, tex=lambda x, y, i: 0 if i == 0 else (2 if (x + y) % 4 < 2 else 5 if (x + y) % 4 == 2 else 4))
    BL = lv(BONE)

    def fang_tex(x, y, i):
        if i == 0:
            return 0
        n = h(x, y, 81)
        i = i - (n < 0.1)
        return max(1, min(6, i))

    side = poly([(11, 21), (22, 26), (17, 45)])
    for f in (side, mirror(side)):
        ic.paint(f, BONE, depth=3, tex=fang_tex)
    mid = poly([(24, 31), (40, 31), (32, 61)]) | rect(26, 27, 38, 32)
    ic.paint(mid, BONE, depth=4, gl=0.3, tex=fang_tex)
    # ridges, tip darkening, a hairline crack
    for x, y in line([(29, 33), (32, 55)]):
        ic.set(x, y, BL[6] if y < 44 else BL[5])
    for x, y in mid:
        if y > 53 and ic.get(x, y) != BL[0]:
            ic.set(x, y, mix(BL[3], hx('#8a7a5a'), 0.5))
    for x, y in ((35, 40), (36, 42), (35, 44)):
        ic.set(x, y, BL[1])
    for fx, fy in ((15, 27), (48, 27)):
        ic.set(fx, fy, BL[6]); ic.set(fx, fy + 1, BL[5])
    # metal caps binding the side fangs to the cord
    for cap in (poly([(11, 19), (20, 23), (19, 27), (12, 23)]),):
        ic.paint(cap, M, depth=2)
        ic.paint(mirror(cap), M, depth=2)
    gem(ic, 32, 30, r)


def feather(ic, r):
    M = RARITIES[r][3]
    FL = lv(FEATHER)
    root, tip = (13, 52), (55, 5)
    m1, c, (ux, uy), (nx, ny) = blade(root, tip, 8, 0.01, bow=2, start=0.16, power=0.4)
    m2, _, _, _ = blade(root, tip, 0.01, 10, bow=2, start=0.16, power=0.4)
    # two splits in the vane, like a real feather
    def split(m, t, side):
        px, py = c(t)
        cut = line([(px + nx * side * 5, py + ny * side * 5),
                    (px + nx * side * 12 - ux * 4, py + ny * side * 12 - uy * 4)], 1)
        return m - cut
    m1 = split(m1, 0.55, -1)
    m2 = split(m2, 0.42, 1)
    for m, side in ((m1, -1), (m2, 1)):
        ic.paint(m, FEATHER, depth=4, gl=0.3)
        for x, y in m:                      # barbs: fine lines sweeping to the tip
            if ic.get(x, y) == FL[0]:
                continue
            vx, vy = x - root[0], y - root[1]
            along = vx * ux + vy * uy
            across = abs(vx * nx + vy * ny)
            ph = (along - 0.7 * across) % 3
            if ph < 0.9:
                o = ic.get(x, y)
                i = next((j for j in range(7) if FL[j] == o), 3)
                ic.set(x, y, FL[max(1, i - 1)])
    for k in range(0, 41):                   # shaft (rachis) + quill
        t = k / 40
        px, py = c(t)
        q = (round(px), round(py))
        ic.set(*q, FL[2] if t > 0.16 else FL[3])
        ic.set(q[0] + 1, q[1], FL[1])
        ic.set(q[0] - 1, q[1] - 1, FL[6]) if t > 0.16 and t < 0.9 else None
    for x, y in ((12, 46), (16, 49), (11, 49), (18, 46)):   # fluffy down near the quill
        ic.set(x, y, FL[5][:3] + (190,))
    clasp = rect(10, 45, 22, 58) & ell(8, 43, 24, 60)
    ic.paint(clasp, M, depth=3, light=0.5)
    CL = lv(M)
    for x, y in line([(11, 48), (19, 46)]) | line([(12, 56), (21, 51)]):
        if (x, y) in clasp:
            ic.set(x, y, CL[1])
    gem(ic, 16, 51, r)


def lantern(ic, r):
    M = RARITIES[r][3]
    ML = lv(M)
    oy = 2
    ic.paint(ring(25, 1 + oy, 38, 12 + oy, 3), M, depth=2)                  # hang ring
    glass = rect(20, 22 + oy, 43, 49 + oy)
    ic.paint(glass, GLASS, depth=3, gl=0.3)
    # warm light inside grows with the rarity
    for x, y in glass:
        dx, dy = x - 31.5, (y - 36 - oy) * 0.75
        d = math.hypot(dx, dy)
        rad = 5 + 2.5 * r
        if d < rad and 21 <= x <= 42 and 23 + oy <= y <= 48 + oy:
            t = d / rad
            col = mix(hx('#fff4c8'), hx('#ffb84a'), t) if t > 0.4 else hx('#fff4c8')
            ic.blend(x, y, col[:3], 1.0 - 0.6 * t)
    flame = poly([(31, 27 + oy), (35, 33 + oy), (36, 39 + oy), (34, 43 + oy), (29, 43 + oy), (27, 39 + oy), (28, 33 + oy)])
    ic.paint(flame, FLAME, depth=3, shadow=False, light=-0.2)
    FLL = lv(FLAME)
    for x, y in poly([(31, 33 + oy), (33, 37 + oy), (33, 41 + oy), (30, 41 + oy), (30, 37 + oy)]):
        ic.set(x, y, FLL[6])
    ic.set(31, 44 + oy, hx('#2a1a10')); ic.set(32, 44 + oy, hx('#2a1a10'))       # wick
    ic.paint(rect(27, 45 + oy, 36, 48 + oy), M, depth=2)                       # wick holder
    # glass glint
    for y in range(24 + oy, 31 + oy):
        ic.set(22, y, hx('#ffffff')[:3] + (200,))
    ic.set(23, 24 + oy, hx('#ffffff')[:3] + (160,))
    # frame posts + cross bars
    for x0 in (18, 44):
        post = rect(x0, 20 + oy, x0 + 1, 50 + oy)
        ic.paint(post, M, depth=1, outline=False, shadow=False,
                 tex=lambda x, y, i, x0=x0: 5 if x == x0 else 2)
        for y in range(20 + oy, 51 + oy):
            ic.set(x0 - 1 if x0 == 18 else x0 + 2, y, ML[0])
    for x in range(20, 44):
        ic.set(x, 35 + oy, ML[3] if x % 2 else ML[2])
    cap = poly([(16, 19 + oy), (47, 19 + oy), (40, 12 + oy), (23, 12 + oy)]) | rect(16, 17 + oy, 47, 22 + oy)
    ic.paint(cap, M, depth=3, light=0.5)
    for x in (19, 43):
        rivet(ic, x, 19 + oy, M)
    for x in range(24, 40, 3):                                             # vent slots
        ic.set(x, 14 + oy, ML[0]); ic.set(x, 15 + oy, ML[1])
    base = rect(17, 50 + oy, 46, 57 + oy)
    ic.paint(base, M, depth=3, light=0.5)
    for x in (20, 42):
        rivet(ic, x, 53 + oy, M)
    for x in range(19, 45):
        ic.set(x, 55 + oy, ML[2] if x % 2 else ML[1])
    gem(ic, 32, 18 + oy if r < 3 else 16 + oy, r)


LINES = [
    ('Health', 'heart amulet', health),
    ('Stamina', 'boot charm', stamina),
    ('Mana', 'mana vial pendant', mana),
    ('Speed', 'winged anklet', speed),
    ('Regeneration', 'leaf ring', regeneration),
    ('Brawler', 'knuckle charm (Strength)', brawler),
    ('Runic', 'rune stone (Magical Power)', runic),
    ('Stonehide', 'stone bracer (Defense)', stonehide),
    ('Razorfang', 'fang necklace (Crit)', razorfang),
    ('Feather', 'feather token (fall / jump)', feather),
    ('Lantern', 'lantern charm (light)', lantern),
]


def make(fn, r):
    ic = Icon()
    fn(ic, r)
    finish(ic, r)
    return ic.im


# ---------------------------------------------------------------- output
def font(n):
    return ImageFont.load_default(size=n)


def slot(icon, s):
    big = icon.resize((W * s, H * s), Image.NEAREST)
    pad = s * 4
    base = Image.new('RGBA', (big.width + 2 * pad, big.height + 2 * pad), SLOT)
    d = ImageDraw.Draw(base)
    d.rectangle((0, 0, base.width - 1, base.height - 1), outline=SLOT_EDGE, width=2)
    base.alpha_composite(big, (pad, pad))
    return base


def main():
    os.makedirs(os.path.join(OUT, 'icons-v2'), exist_ok=True)
    S = 3
    icons = {}
    for name, _, fn in LINES:
        for r, (rn, _, _, _) in enumerate(RARITIES):
            im = make(fn, r)
            icons[name, r] = im
            im.save(os.path.join(OUT, 'icons-v2', f'{name.lower()}-{rn.lower()}.png'), optimize=True)

    cell = slot(icons['Health', 0], S)
    cw, chh = cell.size
    left, top, gap, tiny = 250, 96, 18, W + 8
    colw = cw + tiny + 10
    sheet_w = left + len(RARITIES) * (colw + gap) + gap
    sheet_h = top + len(LINES) * (chh + gap) + gap + 30
    sheet = Image.new('RGBA', (sheet_w, sheet_h), BG)
    d = ImageDraw.Draw(sheet)
    d.text((sheet_w // 2, 14), 'SkyWynn Booster Accessories - icon concepts v2 (cloud draft)', font=font(30), fill=INK, anchor='mt')
    d.text((sheet_w // 2, 52), 'rows = line, columns = rarity; each icon 64 x 64 shown 3x on a dark slot, plus 1x at the right',
           font=font(15), fill=(60, 64, 70, 255), anchor='mt')
    for c, (rn, col, G, M) in enumerate(RARITIES):
        x = left + c * (colw + gap)
        d.rectangle((x, top - 26, x + cw - 1, top - 6), fill=SLOT)
        d.text((x + cw // 2, top - 16), f'{rn}  {col}', font=font(15), fill=hx(col), anchor='mm')
    for i, (name, what, _) in enumerate(LINES):
        y = top + i * (chh + gap)
        d.text((16, y + chh // 2 - 12), name, font=font(22), fill=INK, anchor='lm')
        d.text((16, y + chh // 2 + 14), what, font=font(14), fill=(60, 64, 70, 255), anchor='lm')
        for c in range(len(RARITIES)):
            x = left + c * (colw + gap)
            sheet.alpha_composite(slot(icons[name, c], S), (x, y))
            t = Image.new('RGBA', (W + 8, H + 8), SLOT)
            t.alpha_composite(icons[name, c], (4, 4))
            sheet.alpha_composite(t, (x + cw + 8, y + chh - H - 8))
    d.text((16, sheet_h - 24), 'Original art, generated by research/cloud/accessory-art/make_icons_v2.py. Concept only; nothing built.',
           font=font(13), fill=(60, 64, 70, 255))
    sheet.convert('RGB').save(os.path.join(OUT, 'accessory-sheet-v2.png'), optimize=True)
    print('icons:', len(icons), 'sheet:', sheet.size)


if __name__ == '__main__':
    main()
