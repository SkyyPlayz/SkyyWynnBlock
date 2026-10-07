#!/usr/bin/env python3
"""make_accessory_icons - the FINAL SkyyAccessories booster icons (11 lines x 4 rarities = 44), game-ready 64 x 64 PNGs.

Route R2c: our own art, drawn from code - NO vanilla pixels are read, copied or embedded (this script never opens Assets.zip), so the
icons may be tracked. Designs = the approved cloud concepts research/cloud/accessory-art/make_icons_v2.py (Skyy, docs/answered/gear.md
LOCKED 2026-10-06: accessory icons "Love them", detail to 64 x 64; Stamina redrawn as a lightning bolt, the rest approved).

What this script adds on top of the concept generator:
  * pure Python (stdlib + tools/skyyart.py) - the concept used Pillow; ellipse / polygon / line rasterizers are re-implemented here,
  * the "vanilla finish" (Hytale's generated item icons: soft shading, a dark edge instead of a hard black line, soft anti-aliased
    silhouette, no hard pixel noise): concept noise textures at 40 % strength, an edge-aware smoothing pass over the shading, the
    silhouette outline lifted from near-black to the part's own dark tone, and staircase anti-aliasing on the silhouette,
  * premultiplied alpha on write (like the game's own generated icons),
  * the item ids of every icon (from SkyyAccessories/build_skyyaccessories_0.5.6.py) in manifest.json.

Run:  python tools/art/make_accessory_icons.py [--out DIR]
Out:  <out>/Common/Icons/ItemsGenerated/SkyyAccessories_<Line>_<Rarity>.png (44), <out>/sheet.png, <out>/manifest.json
      (default out = models-local/art/accessories). Deterministic: two runs = same bytes.
"""
import json
import math
import os
import struct
import sys
import zlib

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyyart as SA  # noqa: E402

W = H = 64
CLEAR = (0, 0, 0, 0)


def hx(s):
    s = s.lstrip('#')
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def ramp(*cols):
    """[outline, dark, mid, light, highlight]"""
    return [hx(c) for c in cols]


def mix(a, b, t=0.5):
    return tuple(int(math.floor(a[i] + (b[i] - a[i]) * t + 0.5)) for i in range(3)) + (255,)


def lv(rp):
    """7 levels: 0 outline, 1 dark, 2 dark-mid, 3 mid, 4 mid-light, 5 light, 6 highlight"""
    return [rp[0], rp[1], mix(rp[1], rp[2]), rp[2], mix(rp[2], rp[3]), rp[3], rp[4]]


def h(x, y, s=0):
    """deterministic hash noise 0..1"""
    n = (x * 374761393 + y * 668265263 + s * 2147483647) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFF) / 65535.0


def rnd(v):
    return int(math.floor(v + 0.5))


# ---------------------------------------------------------------- rarities (the concept's rarity system, README section 2)
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
STAM = ramp('#4a1c00', '#a84c00', '#e8820e', '#ffb43a', '#ffe8a8')   # amber enamel (concept v3): the Unique gold frame + yellow gem read

NOISE_SCALE = 0.4      # vanilla finish: concept noise textures at 40 % strength ("no hard pixel noise")


# ---------------------------------------------------------------- masks (Pillow-free rasterizers, inclusive bounding boxes)
def rect(x0, y0, x1, y1):
    return {(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}


def _clip(m):
    return {p for p in m if 0 <= p[0] < W and 0 <= p[1] < H}


def ell(x0, y0, x1, y1):
    """filled ellipse inside the inclusive box (pixel centres)"""
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    rx, ry = (x1 - x0 + 1) / 2.0, (y1 - y0 + 1) / 2.0
    out = set()
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0:
                out.add((x, y))
    return _clip(out)


def ring(x0, y0, x1, y1, w):
    return ell(x0, y0, x1, y1) - (ell(x0 + w, y0 + w, x1 - w, y1 - w) if x1 - x0 > 2 * w and y1 - y0 > 2 * w else set())


def _seg_dist(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


def poly(pts):
    """filled polygon: pixel centre inside (even-odd) or within half a pixel of an edge"""
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    n = len(pts)
    out = set()
    for y in range(int(math.floor(min(ys))), int(math.ceil(max(ys))) + 1):
        for x in range(int(math.floor(min(xs))), int(math.ceil(max(xs))) + 1):
            inside = False
            j = n - 1
            for i in range(n):
                xi, yi = pts[i]
                xj, yj = pts[j]
                if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / float(yj - yi) + xi:
                    inside = not inside
                j = i
            if not inside:
                for i in range(n):
                    a, b = pts[i - 1], pts[i]
                    if _seg_dist(x, y, a[0], a[1], b[0], b[1]) <= 0.5:
                        inside = True
                        break
            if inside:
                out.add((x, y))
    return _clip(out)


def _bres(x0, y0, x1, y1):
    x0, y0, x1, y1 = rnd(x0), rnd(y0), rnd(x1), rnd(y1)
    out = []
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err = dx + dy
    while True:
        out.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy
    return out


def line(pts, w=1):
    out = set()
    for a, b in zip(pts, pts[1:]):
        if w <= 1:
            out.update(_bres(a[0], a[1], b[0], b[1]))
            continue
        ax, ay, bx, by = a[0], a[1], b[0], b[1]
        L = math.hypot(bx - ax, by - ay)
        ux, uy = (bx - ax) / L, (by - ay) / L
        r = w / 2.0
        for y in range(int(math.floor(min(ay, by) - r)), int(math.ceil(max(ay, by) + r)) + 1):
            for x in range(int(math.floor(min(ax, bx) - r)), int(math.ceil(max(ax, bx) + r)) + 1):
                t = (x - ax) * ux + (y - ay) * uy
                d = abs(-(x - ax) * uy + (y - ay) * ux)
                if -0.5 <= t <= L + 0.5 and d <= r - 0.01:
                    out.add((x, y))
    return _clip(out)


def grow(m, n=1):
    for _ in range(n):
        m = m | {(x + dx, y + dy) for x, y in m for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))}
    return m


def shrink(m, n=1):
    for _ in range(n):
        m = {(x, y) for x, y in m if all(q in m for q in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))}
    return m


def mirror(m):
    return {(W - 1 - x, y) for x, y in m}


def blade(root, tip, wl, wr, bow=0.0, start=0.0, power=0.6, steps=40):
    """a tapered leaf / feather shape from root to tip -> (mask, centre(t), unit dir, unit normal)"""
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
        w = max(0.0, math.sin(math.pi * u)) ** power
        px, py = c(t)
        left.append((px - nx * wl * w, py - ny * wl * w))
        right.append((px + nx * wr * w, py + ny * wr * w))
    return poly(left + right[::-1]), c, (ux, uy), (nx, ny)


# ---------------------------------------------------------------- painter
class Icon(object):
    def __init__(self):
        self.px = [[CLEAR] * W for _ in range(H)]

    def get(self, x, y):
        return self.px[y][x] if 0 <= x < W and 0 <= y < H else CLEAR

    def set(self, x, y, col):
        if 0 <= x < W and 0 <= y < H:
            if len(col) == 4 and col[3] < 255:
                self.blend(x, y, col[:3], col[3] / 255.0)
            else:
                self.px[y][x] = tuple(col[:3]) + (255,)

    def blend(self, x, y, rgb, a):
        if not (0 <= x < W and 0 <= y < H):
            return
        o = self.px[y][x]
        if o[3] == 0:
            self.px[y][x] = tuple(rgb) + (rnd(255 * a),)
        else:
            oa = o[3] / 255.0
            na = a + oa * (1 - a)
            c = tuple(rnd((rgb[i] * a + o[i] * oa * (1 - a)) / na) for i in range(3))
            self.px[y][x] = c + (rnd(255 * na),)

    def darken(self, x, y, f=0.62):
        o = self.get(x, y)
        if o[3]:
            self.px[y][x] = (rnd(o[0] * f), rnd(o[1] * f), rnd(o[2] * f), o[3])

    def paint(self, mask, rp, depth=3, tex=None, outline=True, shadow=True, gl=0.18, light=0.42):
        """dome-shade a part: dark edge, distance-field bevel lit from the top-left, soft global gradient, optional texture, and a
        1-px cast shadow on what is already drawn below-right of it"""
        L = lv(rp)
        mask = _clip(mask)
        if not mask:
            return
        if shadow:
            for x, y in sorted(mask):
                q = (x + 1, y + 1)
                if q not in mask and self.get(*q)[3] == 255 and h(q[0], q[1], 7) < 0.9:
                    self.darken(q[0], q[1], 0.7)
        D = {}
        front = sorted(p for p in mask if any(q not in mask for q in
                       ((p[0] + 1, p[1]), (p[0] - 1, p[1]), (p[0], p[1] + 1), (p[0], p[1] - 1))))
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
        cx, cy = (min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0
        hw, hh = max(1, (max(xs) - min(xs)) / 2.0), max(1, (max(ys) - min(ys)) / 2.0)
        for (x, y) in sorted(mask):
            if outline and D[(x, y)] == 1:
                i = 0
            else:
                gx = D.get((x + 1, y), 0) - D.get((x - 1, y), 0)
                gy = D.get((x, y + 1), 0) - D.get((x, y - 1), 0)
                slope = max(-1, min(1, (gx + gy) / 2.0))
                glob = -((x - cx) / hw + (y - cy) / hh) / 2.0 * gl
                v = 0.42 + light * slope + glob
                i = 1 + max(0, min(5, int(v * 6)))
            if tex:
                i = tex(x, y, i)
            if isinstance(i, int):
                i = L[max(0, min(6, i))]
            self.px[y][x] = tuple(i[:3]) + (255,)


def noise(amount=0.22, seed=1, lo=1, hi=6):
    """texture: random +/-1 level on some pixels (keeps the edge); scaled down by NOISE_SCALE for the vanilla finish"""
    amount *= NOISE_SCALE

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


def chain(ic, pts, M):
    """alternating open oval links and side-on bars every 4 px along the path"""
    L = lv(M)
    path = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(abs(x1 - x0), abs(y1 - y0))
        for s in range(n):
            path.append((rnd(x0 + (x1 - x0) * s / float(n)), rnd(y0 + (y1 - y0) * s / float(n))))
    path.append(pts[-1])
    for k, (x, y) in enumerate(path):
        if k % 4 == 2:
            ic.set(x, y, L[5])
            if ic.get(x, y + 1)[3] == 0:
                ic.set(x, y + 1, L[0])
    for k, (x, y) in enumerate(path):
        if k % 4 == 0:
            for dx, dy, i in ((-1, -1, 6), (0, -1, 5), (1, -1, 4), (-1, 0, 5), (1, 0, 2),
                              (-1, 1, 3), (0, 1, 1), (1, 1, 0)):
                ic.set(x + dx, y + dy, L[i])


def rivet(ic, x, y, M):
    L = lv(M)
    ic.set(x, y, L[6])
    ic.set(x + 1, y, L[3])
    ic.set(x, y + 1, L[3])
    ic.set(x + 1, y + 1, L[0])


# ---------------------------------------------------------------- the rarity gem (README section 2)
def size_of(r):
    return (2, 3, 4, 6)[r]


def gem(ic, cx, cy, r):
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
    for x, y in sorted(bez):
        if any(q not in full for q in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))):
            ic.set(x, y, ML[0])
        else:
            t = (x - cx) + (y - cy)
            ic.set(x, y, ML[6] if t < -size_of(r) else ML[5] if t < 0 else ML[3] if t < size_of(r) else ML[1])
    if r == 3:   # milgrain beads on the bezel
        ring_px = sorted(grow(g, 2) - grow(g, 1), key=lambda p: (math.atan2(p[1] - cy, p[0] - cx), p))
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
    edge = {(x, y) for x, y in g if any(q not in g for q in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))}
    size = size_of(r)
    for x, y in sorted(g):
        dx, dy = x - cx + 0.5 * (r <= 1), y - cy + 0.5 * (r <= 1)
        if (x, y) in edge:
            ic.set(x, y, GL[1])
            continue
        if r <= 1:
            v = 0.55 - (dx + dy) / (2.0 * size) * 0.9
            i = 1 + max(0, min(5, int(v * 6)))
        else:
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
    if r == 0:
        ic.set(cx - 1, cy - 1, GL[6])
    elif r == 1:
        for p in ((cx - 2, cy - 1), (cx - 1, cy - 2), (cx - 1, cy - 1)):
            ic.set(p[0], p[1], GL[6])
        ic.set(cx + 1, cy + 1, GL[1])
    else:
        for p in ((cx - 1, cy - 1), (cx - 2, cy), (cx, cy - 2)):
            ic.set(p[0], p[1], GL[6])
        if r == 3:
            ic.set(cx - 1, cy - 2, GL[6])
            ic.set(cx - 2, cy - 1, GL[6])
            ic.set(cx + 2, cy + 2, GL[1])
            ic.set(cx + 3, cy + 1, GL[1])


def star(ic, sx, sy, arm, G):
    """4-point sparkle with fading arms"""
    GL = lv(G)
    ic.set(sx, sy, GL[6])
    for k in range(1, arm + 1):
        a = rnd(255 * (1 - (k - 1) / (arm + 0.5)))
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
    a = {(x, y) for y in range(H) for x in range(W) if ic.px[y][x][3] > 0}
    g1 = grow(a, 1) - a
    g2 = grow(a, 2) - a - g1
    for gset, al in ((g2, 60), (g1, 150)):
        for x, y in sorted(gset):
            ic.set(x, y, GLOW[:3] + (al,))
    for sx, sy, arm in ((55, 8, 4), (8, 55, 2), (56, 51, 2)):
        if ic.get(sx, sy)[3] > 160:
            continue
        star(ic, sx, sy, arm, G)


# ---------------------------------------------------------------- the 11 lines (designs = make_icons_v2.py, approved)
def health(ic, r):
    M = RARITIES[r][3]
    chain(ic, [(7, 4), (18, 15), (29, 19)], M)
    chain(ic, [(56, 4), (45, 15), (34, 19)], M)
    ic.paint(ring(26, 11, 37, 22, 3), M, depth=2)
    heart = ell(10, 20, 33, 43) | ell(30, 20, 53, 43) | poly([(12, 36), (51, 36), (32, 58)])
    ic.paint(heart, RED, depth=6, gl=0.25, tex=noise(0.06, 3, 1, 5))
    RL = lv(RED)
    for x, y in sorted(ell(15, 24, 21, 29) - ell(17, 26, 23, 31)):
        ic.set(x, y, RL[6])
    ic.set(16, 31, RL[5])
    ic.set(15, 32, RL[5])
    for x, y in ((37, 25), (38, 25), (39, 26)):
        ic.set(x, y, RL[5])
    for x, y in sorted(line([(44, 42), (34, 53)])):
        ic.set(x, y, RL[3])
    ic.paint(poly([(27, 21), (36, 21), (34, 25), (29, 25)]), M, depth=2)
    gem(ic, 32, 37, r)


def stamina(ic, r):
    """lightning-bolt charm (Skyy: 'a lightning bolt style like the vanilla symbol for stamina')"""
    M = RARITIES[r][3]
    ML = lv(M)
    ic.paint(ring(33, 4, 44, 15, 3), M, depth=2)
    bolt = poly([(29, 13), (47, 13), (39, 29), (50, 29), (22, 59), (29, 37), (16, 37)])
    ic.paint(bolt, M, depth=2, light=0.5)
    enamel = shrink(bolt, 2)
    ic.paint(enamel, STAM, depth=4, gl=0.3, tex=noise(0.05, 31, 1, 5))
    SL = lv(STAM)
    for x, y in sorted(line([(31, 17), (23, 33)])):
        if (x, y) in enamel and (x + 1, y) in enamel:
            ic.set(x + 1, y, SL[6])
    for x, y in sorted(line([(42, 35), (33, 47)])):
        if (x, y) in enamel:
            ic.set(x, y, SL[5])
    for k, (x, y) in enumerate(sorted(line([(37, 18), (34, 24)]) | line([(36, 41), (29, 52)]), key=lambda p: (p[1], p[0]))):
        if (x, y) in enamel and k % 4 != 3:
            ic.set(x, y, SL[2])
    rivet(ic, 40, 27, M)
    rivet(ic, 26, 38, M)
    for x, y in ((30, 14), (31, 14), (17, 36), (48, 30)):
        if (x, y) in bolt:
            ic.set(x, y, ML[6])
    ic.paint(poly([(34, 11), (43, 11), (42, 15), (35, 15)]), M, depth=2)
    gem(ic, 33, 32, r)


def mana(ic, r):
    M = RARITIES[r][3]
    chain(ic, [(7, 3), (19, 9), (27, 11)], M)
    chain(ic, [(56, 3), (44, 9), (36, 11)], M)
    ic.paint(rect(26, 7, 37, 18), CORK, depth=3, tex=noise(0.4, 21, 1, 6))
    CL = lv(CORK)
    for x, y in ((28, 10), (33, 12), (30, 15), (35, 9)):
        ic.set(x, y, CL[1])
    body = ell(13, 24, 50, 60) | rect(24, 16, 39, 32)
    ic.paint(body, GLASS, depth=3, gl=0.3)
    GL = lv(GLASS)
    liquid = ell(17, 28, 46, 56) & rect(0, 37, 63, 63)
    ic.paint(liquid, MANA, outline=False, depth=6, gl=0.35, shadow=False, tex=noise(0.08, 22, 1, 5))
    ML = lv(MANA)
    top = min(y for _, y in liquid)
    for x, y in sorted(liquid):
        if y == top:
            ic.set(x, y, ML[6] if x % 3 else ML[5])
        elif y == top + 1:
            ic.set(x, y, ML[4])
    for bx, by, br in ((24, 45, 1), (30, 50, 2), (38, 44, 1), (34, 41, 0)):
        if br == 0:
            ic.set(bx, by, ML[6])
        else:
            for x, y in sorted(ring(bx - br, by - br, bx + br, by + br, 1)):
                ic.set(x, y, ML[5])
            ic.set(bx - br, by - br, ML[6])
    for x, y in sorted(ring(17, 27, 46, 56, 1) & rect(0, 0, 25, 41)):
        if (x, y) in body and (x - 17) + (y - 27) > 6:
            ic.set(x + 2, y + 1, GL[6][:3] + (220,))
    for x, y in ((43, 46), (43, 47), (42, 49)):
        ic.set(x, y, GL[5][:3] + (200,))
    for x, y in ((26, 20), (26, 21), (26, 22), (26, 23)):
        ic.set(x, y, GL[6][:3] + (200,))
    ic.paint(rect(22, 19, 41, 25), M, depth=2)
    for x in (24, 38):
        rivet(ic, x, 21, M)
    gem(ic, 32, 22, r)


def wing(ic, flip):
    F = mirror if flip else (lambda m: m)
    fx = (lambda x: W - 1 - x) if flip else (lambda x: x)
    WL = lv(WING)
    hole = ell(20, 32, 43, 51)
    feathers = [((27, 38), (14, 42), 4, 4), ((27, 36), (5, 37), 4.5, 4.5), ((27, 34), (2, 29), 4.5, 4.5),
                ((27, 32), (2, 20), 4.5, 4.5), ((27, 30), (5, 11), 4.5, 4.5)]
    for root, tip, a, b in feathers:
        m, c, _, _ = blade(root, tip, a, b, power=0.35)
        m = F(m) - hole
        ic.paint(m, WING, depth=2, gl=0.1)
        for k in range(4, 22):
            px, py = c(k / 24.0)
            q = (fx(rnd(px)), rnd(py))
            if q in m and ic.get(*q) != WL[0]:
                ic.set(q[0], q[1], WL[2])
    cov = F(poly([(28, 25), (17, 23), (13, 28), (17, 34), (24, 37), (28, 37)])) - hole
    ic.paint(cov, WING, depth=3, gl=0.2)
    for x, y in sorted(cov):
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
    for k in range(16):
        a = k / 16.0 * 2 * math.pi
        x, y = rnd(31.5 + math.cos(a) * 14.5), rnd(41.5 + math.sin(a) * 13)
        if (x, y) in band:
            ic.set(x, y, BL[1])
            ic.set(x - 1, y - 1, BL[6])
    gem(ic, 32, 51, r)


def leaf(ic, root, tip, wl, wr, bow, seed):
    LL = lv(LEAF)
    m, c, (ux, uy), (nx, ny) = blade(root, tip, wl, wr, bow=bow, power=0.75)
    ic.paint(m, LEAF, depth=4, gl=0.25, tex=noise(0.1, seed, 1, 6))
    for k in range(2, 38):
        px, py = c(k / 40.0)
        q = (rnd(px), rnd(py))
        if q in m and ic.get(*q) != LL[0]:
            ic.set(q[0], q[1], LL[1])
            q2 = (q[0] - 1, q[1]) if nx > 0 else (q[0], q[1] - 1)
            if q2 in m and ic.get(*q2) != LL[0]:
                ic.set(q2[0], q2[1], LL[5])
    for t in (0.25, 0.42, 0.59, 0.76):
        px, py = c(t)
        for side in (-1, 1):
            for s_ in range(2, 7):
                q = (rnd(px + (nx * side * 0.9 + ux * 0.7) * s_), rnd(py + (ny * side * 0.9 + uy * 0.7) * s_))
                if q in m and ic.get(*q) != LL[0]:
                    ic.set(q[0], q[1], LL[2])
    return m


def regeneration(ic, r):
    M = RARITIES[r][3]
    band = ring(14, 26, 49, 59, 6)
    ic.paint(band, M, depth=3, light=0.5)
    BL = lv(M)
    for x, y in sorted(ring(16, 28, 47, 57, 1) & rect(0, 0, 30, 44)):
        ic.set(x, y, BL[6])
    leaf(ic, (29, 27), (5, 11), 6, 6, -2, 41)
    leaf(ic, (34, 27), (58, 11), 6, 6, 2, 42)
    leaf(ic, (32, 26), (32, 2), 5, 5, 0, 43)
    ic.set(13, 17, hx('#e8fcff'))
    ic.set(14, 17, hx('#7ad0e8'))
    ic.set(13, 18, hx('#7ad0e8'))
    ic.set(14, 18, hx('#3a8aa8'))
    gem(ic, 32, 28, r)


def brawler(ic, r):
    M = RARITIES[r][3]
    GL = lv(GRIP)
    LL = lv(LEATHER)
    ic.paint(rect(20, 47, 44, 59), LEATHER, depth=3, tex=noise(0.3, 51, 1, 5))
    for y in (50, 54):
        for x in range(21, 44):
            ic.set(x, y, LL[1])
            ic.set(x, y + 1, LL[4] if x % 3 else LL[3])
    for x, y in sorted(line([(21, 58), (32, 48)])):
        ic.set(x, y, LL[5])
    palm = ell(12, 18, 53, 52) | rect(16, 28, 49, 48)
    ic.paint(palm, GRIP, depth=5, tex=noise(0.12, 52, 1, 6))
    for x0 in (12, 22, 32, 42):
        f = ell(x0, 10, x0 + 11, 27) | rect(x0, 18, x0 + 11, 35)
        ic.paint(f, GRIP, depth=4, gl=0.2, tex=noise(0.12, 53 + x0, 1, 6))
        ic.set(x0 + 3, 13, GL[6])
        ic.set(x0 + 4, 13, GL[6])
        ic.set(x0 + 3, 14, GL[5])
        for x in range(x0 + 3, x0 + 9):
            ic.set(x, 32, GL[1])
            ic.set(x, 33, GL[4])
    ic.paint(poly([(14, 35), (38, 35), (42, 39), (38, 43), (16, 43)]), GRIP, depth=3)
    for x in range(19, 37, 3):
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
    RL = lv(RUNE)
    stone = poly([(18, 8), (44, 6), (54, 20), (52, 52), (38, 58), (16, 56), (10, 36), (12, 18)])

    def tex(x, y, i):
        if i == 0:
            return 0
        n = h(x, y, 61)
        i = i - (n < 0.14 * NOISE_SCALE) + (n > 1 - 0.1 * NOISE_SCALE)
        if h(x // 2, y // 2, 62) < 0.08 * NOISE_SCALE:
            i -= 1
        return max(1, min(6, i))
    ic.paint(stone, RUNE, depth=5, gl=0.3, tex=tex)
    for x, y in sorted(poly([(18, 9), (30, 8), (20, 16), (13, 19)]) & stone):
        if ic.get(x, y) != RL[0]:
            ic.set(x, y, RL[5] if h(x, y, 63) > 0.15 else RL[4])
    for x, y in sorted(poly([(51, 40), (51, 51), (40, 56), (47, 48)]) & stone):
        if ic.get(x, y) != RL[0]:
            ic.set(x, y, RL[1] if h(x, y, 64) > 0.2 else RL[2])
    for pts in ([(46, 12), (43, 17), (45, 22), (42, 26)], [(14, 44), (19, 46), (21, 51)]):
        for x, y in sorted(line(pts)):
            if (x, y) in stone:
                ic.set(x, y, RL[0])
                if (x - 1, y) in stone:
                    ic.set(x - 1, y, RL[5])
    rune = line([(24, 26), (32, 50)], 3) | line([(40, 26), (32, 50)], 3) | line([(22, 38), (42, 38)], 3)
    for n, a in ((4, 0.12), (3, 0.16), (2, 0.24)):
        for x, y in sorted(grow(rune, n) - rune):
            if (x, y) in stone and ic.get(x, y) != RL[0]:
                ic.blend(x, y, RUNEGLOW[:3], a)
    for x, y in sorted(grow(rune, 1) - rune):
        if (x, y) in stone and ic.get(x, y) != RL[0]:
            ic.set(x, y, RL[1] if (x + y) % 2 else RL[0])
    for x, y in sorted(rune):
        ic.set(x, y, RUNEGLOW)
    for x, y in sorted(line([(24, 26), (32, 50)]) | line([(40, 26), (32, 50)]) | line([(22, 38), (42, 38)])):
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
        i = i - (n < 0.15 * NOISE_SCALE) + (n > 1 - 0.12 * NOISE_SCALE)
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
    ic.paint(ell(13, 10, 50, 23), STONE, depth=2, shadow=False, light=-0.4, tex=noise(0.3, 72, 1, 4))
    ic.paint(ell(17, 12, 46, 21), [STONE[0]] * 5, outline=False, shadow=False)
    for x, y in sorted(ell(19, 15, 44, 21)):
        if y > 17:
            ic.set(x, y, mix(STONE[0], STONE[1], 0.35))
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
    cord = line([(5, 6), (12, 17), (22, 25), (32, 27), (42, 25), (52, 17), (59, 6)], 5)
    ic.paint(cord, CORD, depth=2, tex=lambda x, y, i: 0 if i == 0 else (2 if (x + y) % 4 < 2 else 5 if (x + y) % 4 == 2 else 4))
    BL = lv(BONE)

    def fang_tex(x, y, i):
        if i == 0:
            return 0
        return max(1, min(6, i - (h(x, y, 81) < 0.1 * NOISE_SCALE)))

    side = poly([(11, 21), (22, 26), (17, 45)])
    for f in (side, mirror(side)):
        ic.paint(f, BONE, depth=3, tex=fang_tex)
    mid = poly([(24, 31), (40, 31), (32, 61)]) | rect(26, 27, 38, 32)
    ic.paint(mid, BONE, depth=4, gl=0.3, tex=fang_tex)
    for x, y in sorted(line([(29, 33), (32, 55)])):
        ic.set(x, y, BL[6] if y < 44 else BL[5])
    for x, y in sorted(mid):
        if y > 53 and ic.get(x, y) != BL[0]:
            ic.set(x, y, mix(BL[3], hx('#8a7a5a'), 0.5))
    for x, y in ((35, 40), (36, 42), (35, 44)):
        ic.set(x, y, BL[1])
    for fx_, fy in ((15, 27), (48, 27)):
        ic.set(fx_, fy, BL[6])
        ic.set(fx_, fy + 1, BL[5])
    cap = poly([(11, 19), (20, 23), (19, 27), (12, 23)])
    ic.paint(cap, M, depth=2)
    ic.paint(mirror(cap), M, depth=2)
    gem(ic, 32, 30, r)


def feather(ic, r):
    M = RARITIES[r][3]
    FL = lv(FEATHER)
    root, tip = (13, 52), (55, 5)
    m1, c, (ux, uy), (nx, ny) = blade(root, tip, 8, 0.01, bow=2, start=0.16, power=0.4)
    m2 = blade(root, tip, 0.01, 10, bow=2, start=0.16, power=0.4)[0]

    def split(m, t, side):
        px, py = c(t)
        return m - line([(px + nx * side * 5, py + ny * side * 5),
                         (px + nx * side * 12 - ux * 4, py + ny * side * 12 - uy * 4)], 1)
    m1 = split(m1, 0.55, -1)
    m2 = split(m2, 0.42, 1)
    for m in (m1, m2):
        ic.paint(m, FEATHER, depth=4, gl=0.3)
        for x, y in sorted(m):
            if ic.get(x, y) == FL[0]:
                continue
            vx, vy = x - root[0], y - root[1]
            along = vx * ux + vy * uy
            across = abs(vx * nx + vy * ny)
            if (along - 0.7 * across) % 3 < 0.9:
                o = ic.get(x, y)
                i = next((j for j in range(7) if FL[j] == o), 3)
                ic.set(x, y, FL[max(1, i - 1)])
    for k in range(0, 41):
        t = k / 40.0
        px, py = c(t)
        q = (rnd(px), rnd(py))
        ic.set(q[0], q[1], FL[2] if t > 0.16 else FL[3])
        ic.set(q[0] + 1, q[1], FL[1])
        if 0.16 < t < 0.9:
            ic.set(q[0] - 1, q[1] - 1, FL[6])
    for x, y in ((12, 46), (16, 49), (11, 49), (18, 46)):
        ic.set(x, y, FL[5][:3] + (190,))
    clasp = rect(10, 45, 22, 58) & ell(8, 43, 24, 60)
    ic.paint(clasp, M, depth=3, light=0.5)
    CL = lv(M)
    for x, y in sorted(line([(11, 48), (19, 46)]) | line([(12, 56), (21, 51)])):
        if (x, y) in clasp:
            ic.set(x, y, CL[1])
    gem(ic, 16, 51, r)


def lantern(ic, r):
    M = RARITIES[r][3]
    ML = lv(M)
    oy = 2
    ic.paint(ring(25, 1 + oy, 38, 12 + oy, 3), M, depth=2)
    glass = rect(20, 22 + oy, 43, 49 + oy)
    ic.paint(glass, GLASS, depth=3, gl=0.3)
    for x, y in sorted(glass):      # warm light inside grows with the rarity
        d = math.hypot(x - 31.5, (y - 36 - oy) * 0.75)
        rad = 5 + 2.5 * r
        if d < rad and 21 <= x <= 42 and 23 + oy <= y <= 48 + oy:
            t = d / rad
            col = mix(hx('#fff4c8'), hx('#ffb84a'), t) if t > 0.4 else hx('#fff4c8')
            ic.blend(x, y, col[:3], 1.0 - 0.6 * t)
    flame = poly([(31, 27 + oy), (35, 33 + oy), (36, 39 + oy), (34, 43 + oy), (29, 43 + oy), (27, 39 + oy), (28, 33 + oy)])
    ic.paint(flame, FLAME, depth=3, shadow=False, light=-0.2)
    FLL = lv(FLAME)
    for x, y in sorted(poly([(31, 33 + oy), (33, 37 + oy), (33, 41 + oy), (30, 41 + oy), (30, 37 + oy)])):
        ic.set(x, y, FLL[6])
    ic.set(31, 44 + oy, hx('#2a1a10'))
    ic.set(32, 44 + oy, hx('#2a1a10'))
    ic.paint(rect(27, 45 + oy, 36, 48 + oy), M, depth=2)
    for y in range(24 + oy, 31 + oy):
        ic.set(22, y, (255, 255, 255, 200))
    ic.set(23, 24 + oy, (255, 255, 255, 160))
    for x0 in (18, 44):
        ic.paint(rect(x0, 20 + oy, x0 + 1, 50 + oy), M, depth=1, outline=False, shadow=False,
                 tex=lambda x, y, i, x0=x0: 5 if x == x0 else 2)
        for y in range(20 + oy, 51 + oy):
            ic.set(x0 - 1 if x0 == 18 else x0 + 2, y, ML[0])
    for x in range(20, 44):
        ic.set(x, 35 + oy, ML[3] if x % 2 else ML[2])
    cap = poly([(16, 19 + oy), (47, 19 + oy), (40, 12 + oy), (23, 12 + oy)]) | rect(16, 17 + oy, 47, 22 + oy)
    ic.paint(cap, M, depth=3, light=0.5)
    for x in (19, 43):
        rivet(ic, x, 19 + oy, M)
    for x in range(24, 40, 3):
        ic.set(x, 14 + oy, ML[0])
        ic.set(x, 15 + oy, ML[1])
    ic.paint(rect(17, 50 + oy, 46, 57 + oy), M, depth=3, light=0.5)
    for x in (20, 42):
        rivet(ic, x, 53 + oy, M)
    for x in range(19, 45):
        ic.set(x, 55 + oy, ML[2] if x % 2 else ML[1])
    gem(ic, 32, 18 + oy if r < 3 else 16 + oy, r)


# (file line name, booster-table family key or None for Lantern, what it is, painter)
LINES = [
    ('Health', 'Vitality', 'heart amulet', health),
    ('Stamina', 'Endurance', 'lightning bolt charm', stamina),
    ('Mana', 'Intelligence', 'mana vial pendant', mana),
    ('Speed', 'Speed', 'winged anklet', speed),
    ('Regeneration', 'Regeneration', 'leaf ring', regeneration),
    ('Brawler', 'Strength', 'knuckle charm (Strength)', brawler),
    ('Runic', 'MagicPower', 'rune stone (Magical Power)', runic),
    ('Stonehide', 'Defense', 'stone bracer (Defense)', stonehide),
    ('Razorfang', 'Crit', 'fang necklace (Crit)', razorfang),
    ('Feather', 'Feather', 'feather token (fall / jump)', feather),
    ('Lantern', 'Lantern', 'lantern charm (light)', lantern),
]

# item ids (SkyyAccessories/build_skyyaccessories_0.5.6.py: BOOSTERS + booster_id(), LAN_IDS, LEGACY_WORDS / LEGACY_IDS)
ID_WORD = ["", "Common", "Uncommon", "Rare", "Epic"]
WORD_FAMS = ("Vitality", "Endurance", "Intelligence", "Regeneration", "Speed", "Lantern")      # id style "word" (Lantern: LAN_IDS)
LEGACY_FAMS = ("Vitality", "Endurance", "Intelligence", "Regeneration", "Speed")               # FOLDED lines only
LEGACY_WORDS = [("Talisman", 2), ("Ring", 3), ("Artifact", 4), ("Legendary", 4)]


def item_ids(fam, tier):
    cur = ("Skyy_Talisman_%s_%s" % (fam, ID_WORD[tier])) if fam in WORD_FAMS else ("Skyy_Talisman_%s_T%d" % (fam, tier))
    legacy = ["Skyy_Talisman_%s_%s" % (fam, w) for w, t in LEGACY_WORDS if t == tier] if fam in LEGACY_FAMS else []
    return cur, legacy


# ---------------------------------------------------------------- fit inside the 2-px margin (concept fit(), Pillow-free)
MARGIN = 2
HALO = 2
LO, HI = MARGIN + HALO, W - 1 - MARGIN - HALO


def _bbox(px):
    xs = [x for y in range(len(px)) for x in range(len(px[0])) if px[y][x][3] > 0]
    ys = [y for y in range(len(px)) for x in range(len(px[0])) if px[y][x][3] > 0]
    return min(xs), min(ys), max(xs) + 1, max(ys) + 1


def _drop(px, axis, k, sym):
    """delete k whole columns (axis 0) / rows (axis 1) that are the closest copies of their neighbour (mirror pairs when sym)"""
    for _ in range(k):
        hgt, w = len(px), len(px[0])
        n = w if axis == 0 else hgt
        m = hgt if axis == 0 else w

        def at(i, j):
            return px[j][i] if axis == 0 else px[i][j]

        def cost(i):
            c = 0
            for j in range(m):
                a, b = at(i, j), at(i + 1, j)
                if a[3] == 0 and b[3] == 0:
                    continue
                c += sum(abs(a[q] - b[q]) for q in range(4)) + (40 if (a[3] == 0) != (b[3] == 0) else 0)
            return c
        bb = _bbox(px)
        lo, hi = (bb[0], bb[2] - 1) if axis == 0 else (bb[1], bb[3] - 1)
        best = None
        for i in range(lo + 1, hi - 1):
            if i + 1 >= n:
                continue
            c = cost(i)
            if sym:
                j = w - 2 - i
                if j <= i:
                    continue
                c += cost(j)
            if best is None or c < best[0]:
                best = (c, i)
        idx = [best[1]] + ([w - 2 - best[1]] if sym else [])
        for i in sorted(idx, reverse=True):
            if axis == 0:
                px = [row[:i] + row[i + 1:] + [CLEAR] for row in px]
            else:
                px = px[:i] + px[i + 1:] + [[CLEAR] * w]
    return px


def fit(ic):
    px = ic.px
    bb = _bbox(px)
    sym = all((px[y][x][3] > 0) == (px[y][W - 1 - x][3] > 0) and px[y][x][3] == px[y][W - 1 - x][3]
              for y in range(H) for x in range(W))
    span = HI - LO + 1
    kx = (bb[2] - bb[0]) - span
    ky = (bb[3] - bb[1]) - span
    if kx > 0:
        px = _drop(px, 0, (kx + 1) // 2 if sym else kx, sym)
    if ky > 0:
        px = _drop(px, 1, ky, False)
    bb = _bbox(px)
    x0, y0, ow, oh = bb[0], bb[1], bb[2] - bb[0], bb[3] - bb[1]
    x1, y1 = x0 + ow - 1, y0 + oh - 1
    dx = LO - x0 if x0 < LO else HI - x1 if x1 > HI else 0
    dy = LO - y0 if y0 < LO else HI - y1 if y1 > HI else 0
    if sym:
        dx = rnd((W - ow) / 2.0) - x0
    out = [[CLEAR] * W for _ in range(H)]
    for y in range(oh):
        for x in range(ow):
            out[y0 + dy + y][x0 + dx + x] = px[y0 + y][x0 + x]
    ic.px = out


# ---------------------------------------------------------------- the vanilla finish
def _l(c):
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


SMOOTH_T = 34.0     # neighbours closer than this (luminance + colour distance) are blended: ramp steps + noise soften, details stay
SMOOTH_W = 0.5      # how much of the neighbour average goes in (0 = off)


def vanilla_finish(ic):
    px = ic.px
    src = [row[:] for row in px]
    # 1. edge-aware smoothing (soft shading like the game's rendered icons; outlines / details / the gem keep their contrast)
    for y in range(H):
        for x in range(W):
            c = src[y][x]
            if c[3] < 255:
                continue
            acc, n = [0.0, 0.0, 0.0], 0
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
                q = src[y + dy][x + dx] if 0 <= x + dx < W and 0 <= y + dy < H else CLEAR
                if q[3] < 255:
                    continue
                d = abs(q[0] - c[0]) + abs(q[1] - c[1]) + abs(q[2] - c[2])
                if d / 1.5 <= SMOOTH_T:
                    wgt = 1.0 if dx == 0 or dy == 0 else 0.5
                    for i in range(3):
                        acc[i] += q[i] * wgt
                    n += wgt
            if n:
                px[y][x] = tuple(rnd(c[i] * (1 - SMOOTH_W) + acc[i] / n * SMOOTH_W) for i in range(3)) + (255,)
    # 2. silhouette edge: lift near-black outline pixels toward their inner neighbour (a dark edge, not a black line)
    src = [row[:] for row in px]
    for y in range(H):
        for x in range(W):
            c = src[y][x]
            if c[3] < 255:
                continue
            nb = [(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
            if not any(not (0 <= a < W and 0 <= b < H) or src[b][a][3] == 0 for a, b in nb):
                continue
            inner = [src[b][a] for a, b in nb if 0 <= a < W and 0 <= b < H and src[b][a][3] == 255]
            if not inner:
                continue
            ref = max(inner, key=_l)
            if _l(c) < _l(ref) * 0.6:
                px[y][x] = tuple(rnd(c[i] * 0.72 + ref[i] * 0.28 * 0.55) for i in range(3)) + (255,)
    # 3. staircase anti-aliasing: a clear pixel tucked into an inner corner of the silhouette gets a soft edge pixel
    src = [row[:] for row in px]
    for y in range(H):
        for x in range(W):
            if src[y][x][3] != 0:
                continue
            for (ax, ay), (bx, by) in (((1, 0), (0, 1)), ((-1, 0), (0, 1)), ((1, 0), (0, -1)), ((-1, 0), (0, -1))):
                A = src[y + ay][x + ax] if 0 <= x + ax < W and 0 <= y + ay < H else CLEAR
                B = src[y + by][x + bx] if 0 <= x + bx < W and 0 <= y + by < H else CLEAR
                if A[3] == 255 and B[3] == 255:
                    opp1 = src[y - ay][x - ax] if 0 <= x - ax < W and 0 <= y - ay < H else CLEAR
                    opp2 = src[y - by][x - bx] if 0 <= x - bx < W and 0 <= y - by < H else CLEAR
                    if opp1[3] == 0 and opp2[3] == 0:
                        px[y][x] = tuple(rnd((A[i] + B[i]) / 2.0) for i in range(3)) + (110,)
                        break


def make(fn, r):
    ic = Icon()
    fn(ic, r)
    fit(ic)
    vanilla_finish(ic)
    finish(ic, r)
    return ic.px


# ---------------------------------------------------------------- output
def to_img(px, premultiply=True):
    img = SA.Img(len(px[0]), len(px))
    for y, row in enumerate(px):
        for x, c in enumerate(row):
            a = c[3]
            if premultiply:
                img.put(x, y, (c[0] * a / 255.0, c[1] * a / 255.0, c[2] * a / 255.0, a) if a else CLEAR)
            else:
                img.put(x, y, c)
    return img


def png_fast(w, h, rows):
    """RGB PNG (filter Up, zlib 9) for the big contact sheet - deterministic, faster than SA.png_encode"""
    raw = bytearray()
    prev = bytes(w * 3)
    for r_ in rows:
        raw.append(2)
        raw += bytes((r_[i] - prev[i]) & 255 for i in range(w * 3))
        prev = r_

    def chunk(t, b):
        return struct.pack(">I", len(b)) + t + b + struct.pack(">I", zlib.crc32(t + b) & 0xffffffff)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))


SLOT = (43, 49, 61)
SLOT_EDGE = (69, 77, 92)
SHEET_BG = (22, 25, 31)


def sheet(icons, S=2):
    """label-free grid: rows = line (LINES order), columns = rarity (Normal, Unique, Rare, Legendary); each icon 2x on a dark slot"""
    pad, gap = 8, 12
    cell = W * S + 2 * pad
    cols, rows_n = len(RARITIES), len(LINES)
    sw = gap + cols * (cell + gap)
    sh = gap + rows_n * (cell + gap)
    can = [[SHEET_BG] * sw for _ in range(sh)]
    for li in range(rows_n):
        for r in range(cols):
            ox, oy = gap + r * (cell + gap), gap + li * (cell + gap)
            for y in range(cell):
                for x in range(cell):
                    edge = x < 2 or y < 2 or x >= cell - 2 or y >= cell - 2
                    can[oy + y][ox + x] = SLOT_EDGE if edge else SLOT
            px = icons[li][r]
            for y in range(H * S):
                for x in range(W * S):
                    c = px[y // S][x // S]
                    a = c[3] / 255.0
                    if a:
                        b = can[oy + pad + y][ox + pad + x]
                        can[oy + pad + y][ox + pad + x] = tuple(rnd(c[i] * a + b[i] * (1 - a)) for i in range(3))
    rows = [bytes(v for c in row for v in c) for row in can]
    return png_fast(sw, sh, rows)


def main(argv):
    out = os.path.join(ROOT, "models-local", "art", "accessories")
    if "--out" in argv:
        out = os.path.abspath(argv[argv.index("--out") + 1])
    icon_dir = os.path.join(out, "Common", "Icons", "ItemsGenerated")
    os.makedirs(icon_dir, exist_ok=True)
    icons, manifest = [], []
    for name, fam, what, fn in LINES:
        row = []
        for r, (rn, col, _, _) in enumerate(RARITIES):
            px = make(fn, r)
            # check: 2 px fully clear margin
            assert all(px[y][x][3] == 0 for y in range(H) for x in range(W)
                       if x < MARGIN or y < MARGIN or x >= W - MARGIN or y >= H - MARGIN), (name, rn)
            row.append(px)
            fname = "SkyyAccessories_%s_%s.png" % (name, rn)
            with open(os.path.join(icon_dir, fname), "wb") as f:
                f.write(SA.png_encode(to_img(px)))
            cur, legacy = item_ids(fam, r + 1)
            manifest.append({
                "item": cur,
                "legacy_ids": legacy,
                "line": name,
                "family_key": fam,
                "tier": r + 1,
                "rarity": rn,
                "rarity_colour": col,
                "model_path": None,
                "model_base": "vanilla (unchanged - the item keeps its current vanilla dropped / held model; no model work)",
                "texture_path": None,
                "icon_path": "Common/Icons/ItemsGenerated/" + fname,
                "notes": "R2c own art (%s), 64x64 RGBA premultiplied, 2 px clear margin; design = approved concept "
                         "research/cloud/accessory-art/icons-v2/%s-%s.png" % (what, name.lower(), rn.lower()),
            })
        icons.append(row)
    with open(os.path.join(out, "sheet.png"), "wb") as f:
        f.write(sheet(icons))
    with open(os.path.join(out, "manifest.json"), "w", newline="\n") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")
    print("icons: %d  sheet: %s  manifest: %d rows  out: %s" % (len(manifest), os.path.join(out, "sheet.png"), len(manifest), out))


if __name__ == "__main__":
    main(sys.argv[1:])
