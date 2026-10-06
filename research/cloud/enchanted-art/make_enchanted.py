#!/usr/bin/env python3
"""SkyWynn Enchanted materials - 64x64 icon concepts (cloud draft 2026-10-06).

Original pixel art drawn from code (no copied art, no game files).
Run:  python3 research/cloud/enchanted-art/make_enchanted.py
Writes icons/ench-<id>.png (64 x 64, transparent), enchanted-sheet.png and
glint-animated-demo.gif next to this script. Deterministic.
"""
# ---------------------------------------------------------------- painter
# Pure Python + Pillow (no numpy). Every shape is a "part" = a set of grid
# pixels. A part is filled from a colour ramp (dark -> light) using a light
# model lit from the top-left, then gets a 1-px dark outline. Deterministic.
import colorsys
import math
import os

from PIL import Image, ImageDraw, ImageFont

LIGHT = (-0.55, -0.68, 0.48)
_l = math.sqrt(sum(c * c for c in LIGHT))
LIGHT = tuple(c / _l for c in LIGHT)


def hx(s):
    s = s.lstrip('#')
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def _rgb(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, max(0, min(1, s)), max(0, min(1, v)))
    return (int(round(r * 255)), int(round(g * 255)), int(round(b * 255)))


def _hl(h, target, t):
    d = ((target - h + 0.5) % 1.0) - 0.5
    return (h + d * t) % 1.0


def ramp(base, n=6, dark=0.58, light=0.38, hs=1.0):
    """Hue-shifted ramp: darks lean blue-violet, lights lean warm.
    Returns {'o': outline colour, 'f': [n fills dark -> light]}."""
    r, g, b = [c / 255 for c in hx(base)]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    out = []
    for i in range(n):
        k = (i / (n - 1) - 0.5) * 2
        if k < 0:
            hh = _hl(h, 0.70, -k * 0.10 * hs)
            vv = v * (1 + k * dark)
            ss = min(1, s * (1 - k * 0.18) + (-k) * 0.04)
        else:
            hh = _hl(h, 0.13, k * 0.07 * hs)
            vv = min(1, v * (1 + k * light) + k * 0.10 * (1 - v))
            ss = s * (1 - k * 0.38)
        out.append(_rgb(hh, ss, vv))
    o = _rgb(_hl(h, 0.72, 0.3), min(1, s * 0.8 + 0.25), v * 0.20 + 0.04)
    return {'o': o, 'f': out}


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def nz(x, y, seed=0):
    n = (x * 374761393 + y * 668265263 + seed * 2246822519 + 1013904223) & 0xffffffff
    n = ((n ^ (n >> 13)) * 1274126177) & 0xffffffff
    return ((n ^ (n >> 16)) & 0xffff) / 65535.0


def vnoise(x, y, scale, seed=0):
    """smooth value noise 0..1"""
    fx, fy = x / scale, y / scale
    x0, y0 = int(math.floor(fx)), int(math.floor(fy))
    tx, ty = fx - x0, fy - y0
    tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
    a = nz(x0, y0, seed); b = nz(x0 + 1, y0, seed)
    c = nz(x0, y0 + 1, seed); d = nz(x0 + 1, y0 + 1, seed)
    return (a + (b - a) * tx) * (1 - ty) + (c + (d - c) * tx) * ty


class Cv:
    def __init__(self, w=64, h=64):
        self.w, self.h = w, h
        self.c = [[None] * w for _ in range(h)]

    def get(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.c[y][x]
        return None

    def put(self, x, y, col):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.c[y][x] = col

    def opaque(self):
        return {(x, y) for y in range(self.h) for x in range(self.w) if self.c[y][x] is not None}

    def img(self):
        im = Image.new('RGBA', (self.w, self.h), (0, 0, 0, 0))
        p = im.load()
        for y in range(self.h):
            for x in range(self.w):
                c = self.c[y][x]
                if c is not None:
                    p[x, y] = c if len(c) == 4 else c + (255,)
        return im


# ------------------------------------------------------------ mask makers
def _pm(w, h, fn):
    im = Image.new('L', (w, h), 0)
    fn(ImageDraw.Draw(im))
    p = im.load()
    return {(x, y) for y in range(h) for x in range(w) if p[x, y] > 127}


def poly(cv, pts):
    return _pm(cv.w, cv.h, lambda d: d.polygon([tuple(p) for p in pts], fill=255))


def ell(cv, cx, cy, rx, ry):
    return {(x, y) for y in range(cv.h) for x in range(cv.w)
            if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1.0}


def rell(cv, cx, cy, rx, ry, ang):
    ca, sa = math.cos(ang), math.sin(ang)
    out = set()
    for y in range(cv.h):
        for x in range(cv.w):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            u = dx * ca + dy * sa
            v = -dx * sa + dy * ca
            if (u / rx) ** 2 + (v / ry) ** 2 <= 1.0:
                out.add((x, y))
    return out


def rect(cv, x0, y0, x1, y1):
    return {(x, y) for y in range(max(0, y0), min(cv.h, y1 + 1)) for x in range(max(0, x0), min(cv.w, x1 + 1))}


def thick(cv, pts, width):
    def fn(d):
        d.line([tuple(p) for p in pts], fill=255, width=int(width), joint='curve')
        r = width / 2.0
        for p in (pts[0], pts[-1]):
            d.ellipse([p[0] - r + 0.5, p[1] - r + 0.5, p[0] + r - 0.5, p[1] + r - 0.5], fill=255)
    return _pm(cv.w, cv.h, fn)


def xf(pts, cx, cy, ang, s=1.0):
    """local points (x right, y down) -> rotated by ang (radians) and scaled, placed at cx, cy"""
    ca, sa = math.cos(ang), math.sin(ang)
    return [(cx + (x * ca - y * sa) * s, cy + (x * sa + y * ca) * s) for x, y in pts]


def edge(mask):
    return {(x, y) for (x, y) in mask
            if (x + 1, y) not in mask or (x - 1, y) not in mask or (x, y + 1) not in mask or (x, y - 1) not in mask}


def bbox(mask):
    xs = [p[0] for p in mask]; ys = [p[1] for p in mask]
    return min(xs), min(ys), max(xs), max(ys)


# ------------------------------------------------------------ the shader
def shade(cv, mask, rp, mode='grad', outline=True, bevel=0.16, noise=0.0, nscale=0, seed=0,
          level=0.0, tex=None, spec=True, contrast=1.0, **kw):
    """Fill `mask` from ramp rp. modes:
    grad   - top-left to bottom-right gradient (flat-ish faces)
    sphere - cx, cy, rx, ry  (round objects)
    cyl    - x0, y0, ang, r  (a cylinder whose axis runs through x0,y0 at angle ang)
    flat   - constant
    tex(x, y) may return an extra value offset."""
    if not mask:
        return
    f = rp['f']
    n = len(f)
    x0, y0, x1, y1 = bbox(mask)
    bw, bh = max(1, x1 - x0), max(1, y1 - y0)
    for (x, y) in mask:
        px, py = x + 0.5, y + 0.5
        if mode == 'sphere':
            dx = (px - kw['cx']) / kw['rx']; dy = (py - kw['cy']) / kw['ry']
            d2 = min(1.0, dx * dx + dy * dy)
            nzv = math.sqrt(1 - d2)
            lam = dx * LIGHT[0] + dy * LIGHT[1] + nzv * LIGHT[2]
            v = 0.10 + 0.92 * max(0.0, lam)
        elif mode == 'cyl':
            a = kw['ang']
            ux, uy = math.cos(a), math.sin(a)
            nx_, ny_ = -uy, ux
            s = ((px - kw['x0']) * nx_ + (py - kw['y0']) * ny_) / kw['r']
            s = max(-1.0, min(1.0, s))
            nzv = math.sqrt(1 - s * s)
            lam = s * nx_ * LIGHT[0] + s * ny_ * LIGHT[1] + nzv * LIGHT[2]
            v = 0.12 + 0.9 * max(0.0, lam)
        elif mode == 'flat':
            v = kw.get('v', 0.55)
        else:
            v = 0.60 - 0.30 * ((x - x0) / bw + (y - y0) / bh - 1.0)
        v = 0.5 + (v - 0.5) * contrast
        if bevel:
            if (x - 1, y) not in mask or (x, y - 1) not in mask:
                v += bevel
            elif (x + 1, y) not in mask or (x, y + 1) not in mask:
                v -= bevel
        if noise:
            if nscale:
                v += (vnoise(x, y, nscale, seed) - 0.5) * 2 * noise
            else:
                v += (nz(x, y, seed) - 0.5) * 2 * noise
        if tex:
            v += tex(x, y)
        v += level
        i = int(v * n)
        i = max(0, min(n - 1, i))
        if not spec and i == n - 1:
            i = n - 2
        cv.c[y][x] = f[i]
    if outline:
        for p in edge(mask):
            cv.c[p[1]][p[0]] = rp['o']


def dots(cv, mask, col, pts):
    for p in pts:
        if p in mask:
            cv.put(p[0], p[1], col)


def scatter(cv, mask, col, density, seed, edge_skip=True):
    e = edge(mask) if edge_skip else set()
    for (x, y) in mask:
        if (x, y) in e:
            continue
        if nz(x, y, seed) < density:
            cv.c[y][x] = col


def font(sz, bold=True):
    p = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    try:
        return ImageFont.truetype(p, sz)
    except Exception:
        return ImageFont.load_default()

# ======================================================================
# Enchanted materials: drawings
# ======================================================================
OUT = os.path.dirname(os.path.abspath(__file__))
PI = math.pi
LANG = math.atan2(LIGHT[1], LIGHT[0])  # screen angle the light comes from

STONE = ramp('#8a8f96', 6)
DSTONE = ramp('#5d6168', 6)


def facet_tex(cx, cy, r, n, seed, top=0.32, amp=0.26):
    rot = nz(seed, 3, seed) * 2 * PI

    def t(x, y):
        dx, dy = x + 0.5 - cx, y + 0.5 - cy
        d = math.hypot(dx, dy) / r
        if d < top:
            return 0.22
        ang = math.atan2(dy, dx) - rot
        k = int(((ang % (2 * PI)) / (2 * PI)) * n)
        mid = rot + (k + 0.5) * 2 * PI / n
        return amp * math.cos(mid - LANG) + (nz(k, 9, seed) - 0.5) * 0.08
    return t


def rock(cv, cx, cy, r, seed, rp, n=9, squash=0.86, facets=7, noise=0.06, level=0.0, outline=True):
    pts = []
    for i in range(n):
        a = 2 * PI * i / n + (nz(i, 0, seed) - 0.5) * 0.5
        rr = r * (0.80 + 0.28 * nz(i, 1, seed))
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr * squash))
    m = poly(cv, pts)
    pk = (cx - 0.22 * r, cy - 0.26 * r * squash)
    shade(cv, m, rp, 'flat', v=0.5, noise=noise, seed=seed, level=level, outline=outline,
          tex=facet_tex(pk[0], pk[1], r, facets, seed), bevel=0.14)
    return m


def outer_line(cv, mask, col):
    for p in edge(mask):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (p[0] + dx, p[1] + dy) not in mask and cv.get(p[0] + dx, p[1] + dy) is None:
                cv.put(p[0], p[1], col)
                break


def crack(cv, mask, pts, col):
    m = thick(cv, pts, 1)
    for p in m & mask:
        if p not in edge(mask):
            cv.put(p[0], p[1], col)


def nugget(cv, cx, cy, r, seed, rp, n=6):
    pts = []
    for i in range(n):
        a = 2 * PI * i / n + nz(i, 5, seed) * 0.6
        rr = r * (0.75 + 0.4 * nz(i, 6, seed))
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    m = poly(cv, pts)
    shade(cv, m, rp, 'flat', v=0.5, tex=facet_tex(cx - r * 0.2, cy - r * 0.25, r, 5, seed, top=0.35, amp=0.34),
          bevel=0.2)
    x0, y0, x1, y1 = bbox(m)
    # bright glint pixel
    for (x, y) in sorted(m, key=lambda p: p[0] + p[1]):
        if (x, y) not in edge(m):
            cv.put(x, y, rp['f'][-1]); cv.put(x + 1, y, rp['f'][-1]); break
    return m


# ---------------------------------------------------------------- mining
def d_cobble(cv, seed=11):
    rock(cv, 22, 40, 15, seed + 1, STONE)
    rock(cv, 42, 42, 14, seed + 2, ramp('#7d8189', 6))
    rock(cv, 32, 24, 15, seed + 3, ramp('#959aa1', 6))
    for s, (x, y) in enumerate([(26, 22), (36, 28), (20, 42), (44, 38)]):
        cv.put(x, y, hx('#5f7a4a')); cv.put(x + 1, y, hx('#6f8f55'))


def d_sand(cv, seed=21):
    rp = ramp('#d9c38c', 6)
    m = ell(cv, 32, 44, 26, 14) | ell(cv, 32, 36, 18, 16)
    m = {p for p in m if p[1] <= 54}
    shade(cv, m, rp, 'sphere', cx=30, cy=40, rx=26, ry=20, noise=0.10, seed=seed)
    scatter(cv, m, rp['f'][1], 0.06, seed + 1)
    scatter(cv, m, rp['f'][5], 0.04, seed + 2)
    # tiny shell
    sh = ell(cv, 42, 46, 3.5, 2.6)
    shade(cv, sh, ramp('#f0d8d0', 5), 'grad', bevel=0.2)


def d_rubble(cv, seed=31):
    cols = ['#8b8580', '#7a7f86', '#958a7c', '#6f747b', '#9a958e']
    spots = [(20, 44, 9), (40, 46, 10), (30, 30, 10), (48, 28, 7), (16, 26, 6)]
    for i, (x, y, r) in enumerate(spots):
        m = rock(cv, x, y, r, seed + i, ramp(cols[i], 6), n=6, facets=5)


def d_clay(cv, seed=41):
    rp = ramp('#a87a68', 6)
    m = ell(cv, 32, 36, 22, 18)
    shade(cv, m, rp, 'sphere', cx=30, cy=32, rx=24, ry=20, noise=0.04, seed=seed)
    for (x, y, r) in [(24, 30, 4), (38, 40, 3.5)]:
        d = ell(cv, x, y, r, r * 0.75)
        shade(cv, d, rp, 'sphere', cx=x + 2, cy=y + 2, rx=r * 1.4, ry=r * 1.4, outline=False, level=-0.18)
    scatter(cv, m, rp['f'][4], 0.03, seed + 1)


def d_sandstone(cv, seed=51):
    rp = ramp('#d0ac72', 6)
    m = rock(cv, 32, 34, 25, seed, rp, n=8, facets=6)
    x0, y0, x1, y1 = bbox(m)
    for i, yy in enumerate(range(y0 + 7, y1, 7)):
        wav = [(x, yy + int(1.5 * math.sin(x * 0.3 + i))) for x in range(x0, x1 + 1, 2)]
        crack(cv, m, wav, rp['f'][1])
        for (x, y) in wav:
            if (x, y + 1) in m and (x, y + 1) not in edge(m):
                cv.put(x, y + 1, rp['f'][4])


def d_slate(cv, seed=61):
    rp = ramp('#5c6a7a', 6)
    for i, (y, w, dx) in enumerate([(46, 25, 0), (36, 23, 3), (26, 20, -2)]):
        pts = [(32 + dx - w, y), (32 + dx - w + 6, y - 7), (32 + dx + w, y - 8), (32 + dx + w - 3, y + 1),
               (32 + dx + w - 6, y + 5), (32 + dx - w + 4, y + 5)]
        m = poly(cv, pts)
        top = poly(cv, pts[:4])
        shade(cv, m, rp, 'flat', v=0.32, noise=0.06, seed=seed + i)
        shade(cv, top - edge(m), rp, 'grad', outline=False, noise=0.08, seed=seed + i, level=0.12)
        scatter(cv, top - edge(m), rp['f'][1], 0.04, seed + 7 + i)


def d_basalt(cv, seed=71):
    rp = ramp('#4c4f57', 6)
    cols = [(18, 30, 10), (33, 20, 10), (48, 34, 9)]
    for i, (x, top, r) in enumerate(cols):
        h = 52 - top
        hexa = [(x - r, top), (x - r / 2, top - 5), (x + r / 2, top - 5), (x + r, top), (x + r / 2, top + 5), (x - r / 2, top + 5)]
        body = poly(cv, [(x - r, top), (x - r, top + h), (x - r / 2, top + h + 5), (x + r / 2, top + h + 5), (x + r, top + h), (x + r, top)])
        left = poly(cv, [(x - r, top), (x - r / 2, top + 5), (x - r / 2, top + h + 5), (x - r, top + h)])
        shade(cv, body, rp, 'flat', v=0.25, noise=0.05, seed=seed + i)
        shade(cv, left - edge(body), rp, 'flat', v=0.45, noise=0.05, seed=seed + i, outline=False, bevel=0)
        tm = poly(cv, hexa)
        shade(cv, tm, rp, 'grad', noise=0.07, seed=seed + i, level=0.18)
        for k in range(top + 12, top + h, 9):
            crack(cv, body, [(x - r + 1, k), (x + r - 1, k + 2)], rp['o'])


ORES = {
    'copper': ('#d9824a', '#8a8f96'),
    'iron': ('#cfc6b8', '#7a7f87'),
    'thorium': ('#7cc35a', '#7b8178'),
    'cobalt': ('#3e6fe0', '#6c7380'),
    'adamantite': ('#d23b3b', '#6e6a6a'),
    'mithril': ('#58d8d2', '#77808e'),
    'onyxium': ('#9b5cd6', '#3d3a44'),
    'silver': ('#dfe5ee', '#7f848c'),
    'gold': ('#f4c542', '#8a857a'),
}


def d_ore(cv, key, seed):
    ore, host = ORES[key]
    orp = ramp(ore, 6, light=0.45)
    m = rock(cv, 32, 34, 25, seed, ramp(host, 6), n=9)
    spots = [(24, 26, 6.5), (40, 30, 5.5), (30, 42, 6), (44, 43, 4), (18, 38, 3.5), (36, 20, 3.5)]
    for i, (x, y, r) in enumerate(spots):
        nugget(cv, x, y, r, seed + 10 + i, orp)
    for i in range(4):
        x = 14 + int(nz(i, 1, seed) * 36); y = 18 + int(nz(i, 2, seed) * 30)
        if (x, y) in m and cv.get(x, y) not in orp['f']:
            cv.put(x, y, orp['f'][3])


# --------------------------------------------------------------- foraging
WOODS = {
    # key: (bark, inner, ring, extra)
    'common': ('#6b4a2e', '#c9a06a', '#9a7144', None),          # oak
    'hard': ('#857565', '#e2c48e', '#b08a58', None),            # maple-ish
    'red': ('#7a3a2a', '#c8744e', '#94452e', None),             # redwood
    'azure': ('#3c5a8a', '#a8c8e8', '#6e94c4', None),           # azure
    'crystal': ('#4d4470', '#d8d0f4', '#a090d8', 'crystal'),    # crystalwood
}


def log(cv, key, seed, cx=33, cy=33, L=40, r=11, ang=-PI / 4):
    bark, inner, ring, extra = WOODS[key]
    brp, irp, rrp = ramp(bark, 6), ramp(inner, 6), ramp(ring, 5)
    ux, uy = math.cos(ang), math.sin(ang)
    a = (cx - ux * L / 2, cy - uy * L / 2)       # lower-left end (cap)
    b = (cx + ux * L / 2, cy + uy * L / 2)
    nx_, ny_ = -uy, ux
    body = poly(cv, [(a[0] + nx_ * r, a[1] + ny_ * r), (b[0] + nx_ * r, b[1] + ny_ * r),
                     (b[0] - nx_ * r, b[1] - ny_ * r), (a[0] - nx_ * r, a[1] - ny_ * r)])
    body |= rell(cv, b[0], b[1], r * 0.5, r, ang)
    cap = rell(cv, a[0], a[1], r * 0.5, r, ang)
    body -= cap

    def bark_tex(x, y):
        # grooves along the axis
        s = (x + 0.5 - a[0]) * nx_ + (y + 0.5 - a[1]) * ny_
        t = (x + 0.5 - a[0]) * ux + (y + 0.5 - a[1]) * uy
        g = math.sin(s * 1.9 + vnoise(t, s, 5, seed) * 3.0)
        return -0.16 if g > 0.75 else (0.06 if g < -0.6 else 0)
    shade(cv, body, brp, 'cyl', x0=a[0], y0=a[1], ang=ang, r=r, tex=bark_tex, noise=0.05, seed=seed)
    # cap rings
    ca, sa = math.cos(ang), math.sin(ang)
    for (x, y) in cap:
        dx, dy = x + 0.5 - a[0], y + 0.5 - a[1]
        u = dx * ca + dy * sa; v = -dx * sa + dy * ca
        rho = math.sqrt((u / (r * 0.5)) ** 2 + (v / r) ** 2)
        if rho > 0.80:
            col = brp['f'][2]
        else:
            rr = rho * 4.2 + vnoise(x, y, 4, seed) * 0.7
            col = rrp['f'][1] if (rr % 1.0) < 0.28 else irp['f'][3 if v < 0 else 2]
            if rho < 0.12:
                col = rrp['f'][0]
        cv.put(x, y, col)
    for p in edge(cap):
        cv.put(p[0], p[1], brp['o'])
    if extra == 'crystal':
        crp = ramp('#7fe0f0', 5, light=0.5)
        for i, t in enumerate([0.3, 0.62, 0.85]):
            px = a[0] + ux * L * t + nx_ * r * 0.7
            py = a[1] + uy * L * t + ny_ * r * 0.7
            pts = xf([(-2.5, 0), (0, -7 - i), (2.5, 0), (0, 2)], px, py, -0.4 + i * 0.3)
            shade(cv, poly(cv, pts), crp, 'grad', bevel=0.25)
    # a little branch stub on top side
    st = (a[0] + ux * L * 0.55 - nx_ * r * 0.95, a[1] + uy * L * 0.55 - ny_ * r * 0.95)
    sm = ell(cv, st[0], st[1], 3, 2.5)
    shade(cv, sm, brp, 'sphere', cx=st[0], cy=st[1], rx=3.5, ry=3.5)
    cv.put(int(st[0]), int(st[1]), irp['f'][2])


def d_fiber(cv, seed=81):
    rp = ramp('#c8b27a', 6)
    cx, cy, R, w = 32, 32, 16, 6.5
    m = set()
    for y in range(64):
        for x in range(64):
            d = math.hypot((x + 0.5 - cx), (y + 0.5 - cy) / 0.82)
            if abs(d - R) <= w:
                m.add((x, y))

    def tt(x, y):
        dx, dy = x + 0.5 - cx, (y + 0.5 - cy) / 0.82
        d = math.hypot(dx, dy)
        s = (d - R) / w
        ang = math.atan2(dy, dx)
        nzv = math.sqrt(max(0, 1 - s * s))
        lam = (dx / d) * s * LIGHT[0] + (dy / d) * s * LIGHT[1] + nzv * LIGHT[2]
        stripe = ((ang * 9 / (2 * PI) * 2 + s * 1.2) % 1.0) < 0.22
        return (0.1 + 0.9 * max(0, lam)) - 0.5 - (0.22 if stripe else 0)
    shade(cv, m, rp, 'flat', v=0.5, tex=tt, bevel=0.0)
    # loose end
    end = thick(cv, [(44, 44), (50, 50), (54, 56)], 5)
    end -= m
    shade(cv, end, rp, 'cyl', x0=44, y0=44, ang=PI / 4, r=3, tex=lambda x, y: -0.2 if (x + y) % 4 == 0 else 0)
    for (x, y) in [(55, 58), (53, 59), (57, 57)]:
        cv.put(x, y, rp['f'][4])


def d_sap(cv, seed=91):
    rp = ramp('#e09a2a', 6, light=0.5)
    m = ell(cv, 32, 38, 16, 16) | poly(cv, [(20, 30), (32, 6), (44, 30)])
    shade(cv, m, rp, 'sphere', cx=32, cy=33, rx=17, ry=24)
    # inner glow bottom right (translucent look)
    g = ell(cv, 37, 44, 8, 6) - edge(m)
    for (x, y) in g:
        cv.put(x, y, mix(cv.get(x, y), hx('#ffd060'), 0.45))
    for (x, y, r) in [(27, 28, 2.5), (38, 36, 1.6), (30, 45, 1.3)]:
        b = ell(cv, x, y, r, r)
        for p in b:
            cv.put(p[0], p[1], rp['f'][1])
        cv.put(int(x - r / 2), int(y - r / 2), rp['f'][5])
    for (x, y) in [(25, 22), (26, 21), (24, 24), (24, 25)]:
        cv.put(x, y, (255, 246, 214))


def d_stick(cv, seed=95):
    rp = ramp('#8a5e36', 6)
    m = thick(cv, [(12, 54), (34, 32), (52, 12)], 6)
    shade(cv, m, rp, 'cyl', x0=12, y0=54, ang=-PI / 4, r=3.2,
          tex=lambda x, y: -0.15 if nz(x, y, seed) < 0.12 else 0)
    br = thick(cv, [(34, 32), (42, 34), (50, 32)], 4) - m
    shade(cv, br, rp, 'grad')
    leaf = rell(cv, 53, 28, 6, 3, -0.6)
    shade(cv, leaf, ramp('#5fae3e', 5), 'grad')
    crack(cv, leaf, [(49, 31), (57, 25)], hx('#3f7a2a'))
    knot = ell(cv, 25, 41, 2, 2)
    for p in knot:
        cv.put(p[0], p[1], rp['f'][0])
    ends = ell(cv, 52, 12, 3, 3) & m
    for p in ends:
        cv.put(p[0], p[1], hx('#d8b07a'))


# ---------------------------------------------------------------- farming
GREEN = ramp('#5aa83e', 6)
DGREEN = ramp('#3f7f34', 6)


def leaf(cv, x, y, L, w, ang, rp=GREEN, vein=True):
    m = rell(cv, x + math.cos(ang) * L / 2, y + math.sin(ang) * L / 2, L / 2, w, ang)
    shade(cv, m, rp, 'grad')
    if vein:
        crack(cv, m, [(x, y), (x + math.cos(ang) * L * 0.85, y + math.sin(ang) * L * 0.85)], rp['f'][1])
    return m


def d_wheat(cv, seed=101):
    straw = ramp('#c9a24a', 6)
    grain = ramp('#e2b85a', 6)
    tops = [(16, 12), (25, 7), (34, 6), (43, 9), (51, 15)]
    base = (32, 58)
    tie = (32, 44)
    for i, t in enumerate(tops):
        st = thick(cv, [base, tie, t], 3)
        shade(cv, st, straw, 'grad', bevel=0.1)
    heads = set()
    for i, (tx, ty) in enumerate(tops):
        ang = math.atan2(ty - tie[1], tx - tie[0])
        for k in range(5):
            px = tx - math.cos(ang) * k * 3.2
            py = ty - math.sin(ang) * k * 3.2
            for side in (-1, 1):
                gx = px + math.cos(ang + side * 0.9) * 2.2
                gy = py + math.sin(ang + side * 0.9) * 2.2
                g = rell(cv, gx, gy, 2.4, 1.6, ang + side * 0.5)
                shade(cv, g, grain, 'grad', bevel=0.3, outline=False)
                heads |= g
        aw = thick(cv, [(tx, ty), (tx + math.cos(ang) * 5, ty + math.sin(ang) * 5)], 1)
        for p in aw:
            if cv.get(*p) is None:
                cv.put(p[0], p[1], straw['f'][4])
    outer_line(cv, heads, grain['o'])
    band = rect(cv, 26, 42, 38, 46)
    shade(cv, band, ramp('#a05a3a', 5), 'grad')


def d_carrot(cv, seed=111):
    rp = ramp('#ec7a28', 6)
    m = poly(cv, [(13, 55), (36, 22), (46, 30)]) | rell(cv, 41, 26, 7, 7.5, -PI / 4)
    shade(cv, m, rp, 'cyl', x0=41, y0=26, ang=PI * 0.7, r=8)
    for i, t in enumerate([0.3, 0.5, 0.7]):
        x = 41 + (13 - 41) * t; y = 26 + (55 - 26) * t
        crack(cv, m, [(x - 2, y - 2), (x + 2, y + 1)], rp['f'][1])
    for i, a in enumerate([-1.3, -0.9, -0.45]):
        leaf(cv, 44, 22, 18 - i * 2, 3, a, GREEN if i != 1 else DGREEN)


def d_corn(cv, seed=121):
    krp = ramp('#f2c63a', 6)
    ang = -PI / 4
    m = rell(cv, 35, 29, 22, 10, ang)
    def kern(x, y):
        u = (x - 35) * math.cos(ang) + (y - 29) * math.sin(ang)
        v = -(x - 35) * math.sin(ang) + (y - 29) * math.cos(ang)
        return -0.25 if (int(u / 2.6) + int(v / 2.6)) % 2 == 0 and nz(int(u / 2.6), int(v / 2.6), 1) < 0.7 else 0
    shade(cv, m, krp, 'cyl', x0=35, y0=29, ang=ang, r=10, tex=kern)
    husk = ramp('#7cb84a', 6)
    for i, (a, L) in enumerate([(-PI / 4 + 0.35, 30), (-PI / 4 - 0.3, 28), (-PI / 4 + 0.05, 20)]):
        hm = rell(cv, 12 + math.cos(a) * L / 2, 52 + math.sin(a) * L / 2, L / 2, 5.5 - i, a)
        shade(cv, hm, husk if i < 2 else DGREEN, 'grad')
    st = thick(cv, [(8, 57), (12, 52)], 4)
    shade(cv, st, DGREEN, 'grad')
    for (x, y) in [(52, 11), (54, 10), (55, 13), (51, 9)]:
        cv.put(x, y, hx('#b07a3a'))


def d_lettuce(cv, seed=131):
    lrp = ramp('#7ccc4e', 6, light=0.45)
    outer = ramp('#4f9a3a', 6)
    base = ell(cv, 32, 38, 25, 18)
    shade(cv, base, outer, 'sphere', cx=30, cy=36, rx=26, ry=20)
    leaves = [(20, 34, 11, 9), (44, 34, 11, 9), (32, 42, 13, 9), (27, 27, 10, 8), (38, 27, 10, 8), (32, 32, 9, 8)]
    for i, (x, y, rx, ry) in enumerate(leaves):
        m = ell(cv, x, y, rx, ry)
        shade(cv, m, lrp if i > 2 else outer, 'sphere', cx=x - 2, cy=y - 2, rx=rx + 2, ry=ry + 2,
              tex=lambda xx, yy: -0.12 if ((xx * 3 + yy) % 7) == 0 else 0)
        crack(cv, m, [(x, y + ry - 2), (x, y - 1)], lrp['f'][4])


def d_pumpkin(cv, seed=141):
    rp = ramp('#e07a22', 6)
    m = ell(cv, 32, 38, 26, 19)
    ribs = [-18, -9, 0, 9, 18]
    shade(cv, m, rp, 'sphere', cx=30, cy=35, rx=27, ry=21,
          tex=lambda x, y: -0.13 * (1 - abs(((x - 32 + 4.5) % 9) - 4.5) / 4.5) ** 0.3 + 0.07)
    for dx in ribs[1:-1]:
        crack(cv, m, [(32 + dx * 0.6, 21), (32 + dx * 1.15, 38), (32 + dx * 0.6, 55)], rp['f'][1])
    st = poly(cv, [(30, 22), (33, 10), (38, 9), (36, 22)])
    shade(cv, st, ramp('#6a8a3a', 5), 'grad')
    curl = thick(cv, [(38, 12), (44, 10), (46, 14)], 2)
    shade(cv, curl, GREEN, 'grad', bevel=0)


def d_cauliflower(cv, seed=151):
    for a in [-2.6, -0.5, -1.55, PI * 0.85, 0.2]:
        leaf(cv, 32, 44, 26, 7, a + PI if a > 0 else a, GREEN if a < -1 else DGREEN)
    frp = ramp('#ece6cc', 6, light=0.2)
    m = ell(cv, 32, 32, 18, 14)
    shade(cv, m, frp, 'sphere', cx=30, cy=30, rx=19, ry=15, outline=True)
    for i, (x, y) in enumerate([(24, 28), (32, 25), (40, 28), (27, 35), (37, 35), (32, 31), (20, 33), (44, 33)]):
        b = ell(cv, x, y, 5, 4.5) & m
        shade(cv, b, frp, 'sphere', cx=x - 1, cy=y - 1, rx=6, ry=5.5, outline=False, contrast=0.9)
        for p in edge(b):
            if p in m and p not in edge(m) and (p[0] - x) + (p[1] - y) > 1:
                cv.put(p[0], p[1], frp['f'][1])


def d_turnip(cv, seed=161):
    for a in [-1.9, -1.4, -1.0]:
        leaf(cv, 32, 22, 20, 4, a, GREEN)
    m = ell(cv, 32, 36, 16, 15) | poly(cv, [(28, 46), (36, 46), (33, 60)])
    white = ramp('#e8e2e8', 6, light=0.15)
    purp = ramp('#9a4aa0', 6)
    shade(cv, m, white, 'sphere', cx=30, cy=34, rx=18, ry=18)
    top = {p for p in m if p[1] < 32 + 3 * math.sin(p[0] * 0.4)} - edge(m)
    shade(cv, top, purp, 'sphere', cx=30, cy=34, rx=18, ry=18, outline=False)
    crack(cv, m, [(24, 40), (27, 44)], white['f'][2])


def d_aubergine(cv, seed=171):
    rp = ramp('#5a2a78', 6, light=0.6)
    m = ell(cv, 25, 41, 15, 14) | rell(cv, 35, 31, 15, 10, -PI / 4)
    shade(cv, m, rp, 'sphere', cx=26, cy=34, rx=24, ry=22)
    hl = thick(cv, [(16, 38), (20, 32)], 2) - edge(m)
    for p in hl:
        cv.put(p[0], p[1], rp['f'][5])
    cal = poly(cv, [(38, 18), (50, 16), (52, 28), (47, 26), (43, 30), (41, 24), (34, 26)])
    shade(cv, cal, DGREEN, 'grad')
    st = thick(cv, [(46, 20), (53, 10)], 4)
    shade(cv, st, ramp('#6a8a4a', 5), 'grad')


def d_tomato(cv, seed=181):
    rp = ramp('#d93a2c', 6, light=0.5)
    m = ell(cv, 32, 36, 22, 19)
    shade(cv, m, rp, 'sphere', cx=30, cy=33, rx=23, ry=21)
    for dx in (-8, 8):
        crack(cv, m, [(32 + dx * 0.5, 19), (32 + dx * 1.1, 32)], rp['f'][2])
    for p in [(22, 26), (23, 25), (24, 25), (22, 27), (25, 24)]:
        cv.put(p[0], p[1], (255, 220, 210))
    star = set()
    for k in range(5):
        a = -PI / 2 + k * 2 * PI / 5 + 0.3
        star |= thick(cv, [(32, 20), (32 + math.cos(a) * 9, 20 + math.sin(a) * 5)], 3)
    shade(cv, star, DGREEN, 'grad')
    st = thick(cv, [(32, 20), (33, 11), (37, 8)], 3)
    shade(cv, st, GREEN, 'grad')


def tube(cv, pts, rp, seed=0, outline=True, spec=True):
    """a round body that follows a curve: pts = [(x, y, radius), ...] sampled densely;
    each pixel is lit as a cylinder across the nearest centre point (curved fruit, stems)."""
    dense = []
    for (x0, y0, r0), (x1, y1, r1) in zip(pts, pts[1:]):
        n = max(2, int(math.hypot(x1 - x0, y1 - y0) * 2))
        for k in range(n):
            t = k / n
            dense.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, r0 + (r1 - r0) * t))
    dense.append(pts[-1])
    m = set()
    for x, y, r in dense:
        m |= ell(cv, x, y, max(0.8, r), max(0.8, r))

    def light(x, y):
        px, py = x + 0.5, y + 0.5
        best = min(dense, key=lambda c: (px - c[0]) ** 2 + (py - c[1]) ** 2)
        nx, ny = (px - best[0]) / max(1.0, best[2]), (py - best[1]) / max(1.0, best[2])
        d2 = min(1.0, nx * nx + ny * ny)
        lam = nx * LIGHT[0] + ny * LIGHT[1] + math.sqrt(1 - d2) * LIGHT[2]
        return 0.08 + 0.95 * max(0.0, lam)
    shade(cv, m, rp, 'flat', v=0.0, tex=light, bevel=0.0, outline=outline, spec=spec)
    return m, dense


def d_cotton(cv, seed=191):
    """three open cotton bolls on a woody branching stem: each boll = 4 fat white
    locks with soft cool shadows between them, dry brown bract points behind,
    two lobed leaves low on the stem."""
    wood = ramp('#7a5434', 5)
    bract = ramp('#6e4a2c', 6)
    white = ramp('#f1eef0', 7, dark=0.42, light=0.12)
    bolls = [(32, 16, 11.5, 0.15), (15, 32, 10.5, 0.9), (49, 32, 10.5, -0.6)]
    # stem + branches first (behind everything)
    for pts, w in (([(32, 63), (32, 50), (32, 40), (32, 26)], 4), ([(32, 47), (24, 42), (18, 38)], 3),
                   ([(32, 45), (41, 41), (46, 38)], 3)):
        shade(cv, thick(cv, pts, w), wood, 'grad', bevel=0.12)
    # lobed leaves (3 lobes each) low on the stem
    for side in (-1, 1):
        lx, ly = 32 + side * 2, 54
        base_a = PI if side < 0 else 0.0
        lm = set()
        for da, L in ((-0.55, 11), (0.0, 13), (0.55, 10)):
            a = base_a - side * 0.35 + da * side
            lm |= rell(cv, lx + math.cos(a) * L / 2, ly + math.sin(a) * L / 2 - 2, L / 2, 3.6, a)
        shade(cv, lm, GREEN if side < 0 else DGREEN, 'grad', bevel=0.18)
        for da, L in ((-0.55, 11), (0.0, 13), (0.55, 10)):
            a = base_a - side * 0.35 + da * side
            crack(cv, lm, [(lx, ly - 2), (lx + math.cos(a) * L * 0.8, ly - 2 + math.sin(a) * L * 0.8)],
                  (GREEN if side < 0 else DGREEN)['f'][1])
    for bx, by, r, rot in bolls:
        # bract: 5 dry pointed sepals poking out between the locks
        bm = set()
        for k in range(5):
            a = rot + k * 2 * PI / 5 + PI / 5
            tip = (bx + math.cos(a) * (r + 3.5), by + math.sin(a) * (r + 3.5))
            l = (bx + math.cos(a - 0.38) * r * 0.55, by + math.sin(a - 0.38) * r * 0.55)
            rr = (bx + math.cos(a + 0.38) * r * 0.55, by + math.sin(a + 0.38) * r * 0.55)
            bm |= poly(cv, [(bx, by), l, tip, rr])
        shade(cv, bm, bract, 'grad', bevel=0.2)
        # four locks
        locks = []
        um = set()
        for k in range(4):
            a = rot + k * PI / 2
            lx, ly = bx + math.cos(a) * r * 0.42, by + math.sin(a) * r * 0.42
            rr = r * 0.62
            locks.append((lx, ly, rr, ell(cv, lx, ly, rr, rr * 0.94)))
        # draw the lower / right locks first so the upper-left ones sit in front
        for lx, ly, rr, lm in sorted(locks, key=lambda q: -(q[0] + q[1])):
            shade(cv, lm, white, 'sphere', cx=lx - rr * 0.25, cy=ly - rr * 0.3, rx=rr * 1.15, ry=rr * 1.15,
                  outline=False, noise=0.05, seed=seed)
            um |= lm
            # soft cool crease where this lock meets the ones already drawn behind it
            for p in edge(lm):
                q = (p[0] + 1, p[1] + 1)
                if q in um and q not in lm:
                    cv.put(q[0], q[1], white['f'][1])
            for p in edge(lm):
                if any((p[0] + dx, p[1] + dy) in um and (p[0] + dx, p[1] + dy) not in lm
                       for dx, dy in ((1, 0), (0, 1), (-1, 0), (0, -1))):
                    cv.put(p[0], p[1], white['f'][2])
        # fluffy rim: a few 1-px tufts off the edge
        for p in sorted(edge(um)):
            if nz(p[0], p[1], seed + 3) < 0.10:
                dx, dy = p[0] - bx, p[1] - by
                d = max(1.0, math.hypot(dx, dy))
                q = (int(round(p[0] + dx / d)), int(round(p[1] + dy / d)))
                if cv.get(*q) is None:
                    um.add(q)
                    cv.put(q[0], q[1], white['f'][4])
        outer_line(cv, um, white['o'])
        # bright tops on each lock + dark seed-pit in the middle
        for lx, ly, rr, lm in locks:
            hx_, hy_ = int(lx - rr * 0.35), int(ly - rr * 0.4)
            for q in ((hx_, hy_), (hx_ + 1, hy_), (hx_, hy_ + 1)):
                if q in lm:
                    cv.put(q[0], q[1], white['f'][-1])
        cv.put(int(bx), int(by), white['f'][0])


def grow(m):
    return m | {(x + dx, y + dy) for x, y in m for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))}


def d_rice(cv, seed=201):
    """a small burlap sack, open, heaped with white rice grains; a tied rice
    panicle (drooping golden heads) tucked in behind; a few grains spilled."""
    straw = ramp('#a8b05a', 6)
    hull = ramp('#d8b25a', 6)
    sackc = ramp('#b48c58', 6)
    rice = ramp('#f2ecd8', 6, dark=0.40, light=0.15)
    # --- two rice panicles tucked in behind the heap, heads drooping out to each side
    for (sx, sy), (tx, ty), (ex, ey) in (((34, 24), (40, 5), (58, 19)), ((24, 24), (20, 6), (5, 18))):
        shade(cv, thick(cv, [(sx, sy), ((sx + tx) / 2, (sy + ty) / 2 + 1), (tx, ty)], 2), straw, 'grad', bevel=0.1)
        arc = [(tx + (ex - tx) * t, ty + (ey - ty) * t - math.sin(t * PI) * 4) for t in [k / 9 for k in range(10)]]
        for a_, b_ in zip(arc, arc[1:]):
            for q in thick(cv, [a_, b_], 1):
                cv.put(q[0], q[1], straw['f'][2])
        gm = set()
        sgn = 1 if ex > tx else -1
        for k, (gx, gy) in enumerate(arc[1:]):
            for side in (-1, 1):
                ang = (1.2 + side * 0.45) if sgn > 0 else (PI - 1.2 - side * 0.45)
                g = rell(cv, gx + side * 1.4 * sgn, gy + 2.4, 2.3, 1.35, ang)
                shade(cv, g, hull, 'grad', bevel=0.35, outline=False, level=-0.18 if (k + (side > 0)) % 2 else 0.0)
                gm |= g
        outer_line(cv, gm, hull['o'])
    # --- the sack: rounded body, pinched neck, folded-open lip
    body = ell(cv, 29, 46, 19, 15) | poly(cv, [(14, 44), (17, 32), (41, 32), (44, 44)])
    def weave(x, y):
        return (-0.07 if (x % 3 == 0) else 0.0) + (-0.05 if (y % 3 == 1) else 0.03) + (nz(x, y, seed) - 0.5) * 0.1
    shade(cv, body, sackc, 'sphere', cx=24, cy=40, rx=24, ry=20, tex=weave)
    # seam + stitches down the right side, a patch stripe
    for y in range(36, 58, 3):
        for q in ((41, y), (42, y + 1)):
            if q in body and q not in edge(body):
                cv.put(q[0], q[1], sackc['f'][0])
    for x in range(16, 43):
        for y in (49, 50):
            if (x, y) in body and (x, y) not in edge(body):
                cv.put(x, y, mix(cv.get(x, y)[:3], hx('#6e8a46'), 0.55))
    lip = ell(cv, 28, 28, 17, 6.5)
    shade(cv, lip, sackc, 'grad', bevel=0.25, noise=0.06, seed=seed + 1)
    inner = ell(cv, 28, 28, 14, 4.2)
    shade(cv, inner, sackc, 'flat', v=0.05, outline=False, bevel=0)
    # --- the heap of rice in the mouth (dome + individual grains, no grid)
    heap = (ell(cv, 28, 26, 13, 9) & rect(cv, 0, 0, 63, 29)) | (inner & rect(cv, 0, 26, 63, 63))
    shade(cv, heap, rice, 'sphere', cx=24, cy=21, rx=15, ry=12, outline=False)
    outer_line(cv, heap - inner, rice['o'])
    taken = set()
    for k in range(260):
        x = 15 + int(nz(k, 1, seed + 2) * 27)
        y = 18 + int(nz(k, 2, seed + 2) * 12)
        diag = nz(k, 3, seed + 2) < 0.4
        cells = [(x, y), (x + 1, y)] if not diag else [(x, y), (x + 1, y - 1)]
        if any(c not in heap or c in edge(heap) or c in taken for c in cells):
            continue
        if any((c[0] + dx, c[1] + dy) in taken for c in cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            continue
        lit = (x - 28) * 0.8 + (y - 22) < 3
        cv.put(cells[0][0], cells[0][1], rice['f'][5 if lit else 4])
        cv.put(cells[1][0], cells[1][1], rice['f'][4 if lit else 3])
        sh = (cells[0][0], cells[0][1] + 1)
        if sh in heap and sh not in taken:
            cv.put(sh[0], sh[1], rice['f'][1 if lit else 0])
        taken |= set(cells) | {sh}
    # --- twine round the neck with a knot and two ends
    tw = ramp('#8a6a3a', 5)
    band = (ell(cv, 28, 34, 16, 3.2) - ell(cv, 28, 32.5, 16, 2.4)) & body
    shade(cv, band, tw, 'grad', bevel=0.2, outline=False)
    knot = ell(cv, 16, 35, 2.4, 2.2)
    shade(cv, knot, tw, 'sphere', cx=15, cy=34, rx=3, ry=3)
    for pts_ in ([(15, 37), (12, 42), (13, 46)], [(17, 37), (18, 43)]):
        shade(cv, thick(cv, pts_, 1), tw, 'flat', v=0.5, bevel=0, outline=False)
    # --- spilled grains in front, bottom-right (3 x 2 px each, own outline)
    gm = set()
    for (x, y, d) in [(48, 56, 0), (52, 59, 1), (56, 55, 0), (45, 60, 0), (57, 60, 1), (52, 53, 1)]:
        cells = [(x, y), (x + 1, y), (x + 2, y), (x, y + 1), (x + 1, y + 1), (x + 2, y + 1)] if not d else \
                [(x + 1, y), (x + 2, y), (x, y + 1), (x + 1, y + 1), (x + 2, y + 1), (x, y + 2), (x + 1, y + 2)]
        g = set(cells)
        shade(cv, g, rice, 'grad', bevel=0.0, outline=False, level=0.15)
        gm |= g
    outer_line(cv, grow(gm), rice['o'])


def d_chilli(cv, seed=231):
    """one curved red chilli, glossy, green calyx + hooked stem (Crop-Armor-Spec Chilli)."""
    red = ramp('#d8301e', 6, light=0.55)
    body = [(44, 16, 7.0), (40, 26, 7.4), (33, 37, 6.6), (25, 46, 5.4), (17, 53, 3.8), (10, 57, 2.2), (6, 58, 0.9)]
    m, dense = tube(cv, body, red, seed)
    # gloss streak + a second small one, wrinkles near the shoulder
    for x, y, r in dense[4:-12:3]:
        hx_, hy_ = int(round(x - r * 0.45)), int(round(y - r * 0.5))
        if (hx_, hy_) in m and (hx_, hy_) not in edge(m):
            cv.put(hx_, hy_, red['f'][-1])
    for x, y, r in dense[::6]:
        q = (int(round(x + r * 0.55)), int(round(y + r * 0.25)))
        if q in m and q not in edge(m) and y < 40:
            cv.put(q[0], q[1], red['f'][1])
    crack(cv, m, [(38, 20), (35, 27)], red['f'][2])
    # calyx (cap) + stem
    cal = set()
    for a in (-2.4, -1.75, -1.1, -0.45, 0.25):
        cal |= poly(cv, [(46, 12), (46 + math.cos(a - 0.35) * 5, 12 + math.sin(a - 0.35) * 5),
                         (46 + math.cos(a) * 9.5, 13 + math.sin(a) * 6 + 5),
                         (46 + math.cos(a + 0.35) * 5, 12 + math.sin(a + 0.35) * 5)])
    cal |= ell(cv, 45, 12, 6.5, 4.2)
    shade(cv, cal, DGREEN, 'grad', bevel=0.22)
    tube(cv, [(46, 10, 2.0), (48, 5, 1.8), (52, 3, 1.5), (55, 5, 1.3)], GREEN)


def d_potato(cv, seed=211):
    rp = ramp('#b08a52', 6)
    m = rell(cv, 32, 35, 22, 15, -0.35) | ell(cv, 22, 40, 9, 8) | ell(cv, 43, 28, 9, 8)
    shade(cv, m, rp, 'sphere', cx=30, cy=31, rx=26, ry=20, noise=0.05, seed=seed)
    for (x, y) in [(28, 33), (38, 38), (20, 42), (44, 26), (33, 26)]:
        cv.put(x, y, rp['f'][0]); cv.put(x + 1, y, rp['f'][1]); cv.put(x, y - 1, rp['f'][4])
    scatter(cv, m, rp['f'][2], 0.05, seed + 1)


def d_onion(cv, seed=221):
    rp = ramp('#c88a3e', 6, light=0.45)
    m = ell(cv, 32, 40, 19, 17) | poly(cv, [(24, 28), (32, 12), (40, 28)])
    shade(cv, m, rp, 'sphere', cx=30, cy=36, rx=20, ry=22)
    for dx in (-10, -4, 4, 10):
        crack(cv, m, [(32 + dx * 0.3, 16), (32 + dx * 1.2, 36), (32 + dx * 0.6, 55)], rp['f'][1])
    sp = thick(cv, [(32, 14), (31, 6), (35, 2)], 3)
    shade(cv, sp, GREEN, 'grad')
    for k in range(5):
        r = thick(cv, [(28 + k * 2, 56), (26 + k * 3, 61)], 1)
        for p in r:
            if cv.get(*p) is None:
                cv.put(p[0], p[1], hx('#d8c8a0'))


# -------------------------------------------------------------- cube blocks
CT, CL, CR, CC = (32, 3), (4, 17), (60, 17), (32, 31)
CBL, CBC, CBR = (4, 47), (32, 61), (60, 47)


def _inv(p, o, e1, e2):
    det = e1[0] * e2[1] - e1[1] * e2[0]
    dx, dy = p[0] - o[0], p[1] - o[1]
    u = (dx * e2[1] - dy * e2[0]) / det
    v = (e1[0] * dy - e1[1] * dx) / det
    return u, v


def cube(cv, tex, seed=0):
    """tex(face, u, v) -> (ramp, value 0..1) ; face in 'top','left','right'; u,v in 0..1"""
    faces = {
        'top': (CT, (CR[0] - CT[0], CR[1] - CT[1]), (CL[0] - CT[0], CL[1] - CT[1]), 0.16),
        'left': (CL, (CC[0] - CL[0], CC[1] - CL[1]), (CBL[0] - CL[0], CBL[1] - CL[1]), -0.02),
        'right': (CC, (CR[0] - CC[0], CR[1] - CC[1]), (CBC[0] - CC[0], CBC[1] - CC[1]), -0.20),
    }
    allm = set()
    fm = {}
    for name, (o, e1, e2, lv) in faces.items():
        fm[name] = set()
        for y in range(cv.h):
            for x in range(cv.w):
                u, v = _inv((x + 0.5, y + 0.5), o, e1, e2)
                if -0.001 <= u <= 1.001 and -0.001 <= v <= 1.001 and (x, y) not in allm:
                    rp, val = tex(name, min(0.999, max(0, u)), min(0.999, max(0, v)))
                    val += lv
                    f = rp['f']
                    cv.put(x, y, f[max(0, min(len(f) - 1, int(val * len(f))))])
                    fm[name].add((x, y)); allm.add((x, y))
    # edges: silhouette dark, front top edges bright, centre vertical darker
    out = rp['o']
    for p in edge(allm):
        cv.put(p[0], p[1], out)
    hi = (255, 255, 255)
    for name in ('left', 'right'):
        for p in fm[name]:
            if (p[0], p[1] - 1) in fm['top'] and p not in edge(allm):
                cv.put(p[0], p[1], mix(cv.get(*p), hi, 0.35))
    for p in fm['right']:
        if (p[0] - 1, p[1]) in fm['left'] and p not in edge(allm):
            cv.put(p[0], p[1], mix(cv.get(*p), (0, 0, 0), 0.35))
    return allm


def tex_cobble(seed):
    rps = [ramp('#8a8f96', 6), ramp('#7b8088', 6), ramp('#969aa0', 6)]
    pts = [((i % 4 + 0.2 + nz(i, 1, seed) * 0.6) / 4, (i // 4 + 0.2 + nz(i, 2, seed) * 0.6) / 4) for i in range(16)]

    def t(face, u, v):
        ds = sorted(((min(abs(u - px), 1 - abs(u - px)) ** 2 + min(abs(v - py), 1 - abs(v - py)) ** 2, i) for i, (px, py) in enumerate(pts)))
        d1, i1 = ds[0]; d2 = ds[1][0]
        rp = rps[i1 % 3]
        if math.sqrt(d2) - math.sqrt(d1) < 0.035:
            return DSTONE, 0.05
        px, py = pts[i1]
        val = 0.62 - (u - px) * 1.6 - (v - py) * 1.6 + (nz(int(u * 32), int(v * 32), seed) - 0.5) * 0.12
        return rp, val
    return t


def tex_metal(key):
    ore = ORES[key][0]
    rp = ramp(ore, 6, light=0.4)

    def t(face, u, v):
        b = min(u, v, 1 - u, 1 - v)
        if b < 0.07:
            return rp, 0.78 if (u < 0.07 or v < 0.07) else 0.22
        if b < 0.10:
            return rp, 0.12
        # 2x2 plates
        pu, pv = (u - 0.1) / 0.8 * 2, (v - 0.1) / 0.8 * 2
        fu, fv = pu % 1.0, pv % 1.0
        if fu < 0.06 or fv < 0.06:
            return rp, 0.10
        if (abs(fu - 0.18) < 0.07 and abs(fv - 0.18) < 0.07) or (abs(fu - 0.82) < 0.07 and abs(fv - 0.82) < 0.07):
            return rp, 0.92  # rivets
        val = 0.55 - (fu + fv - 1) * 0.18 + (0.08 if (int(pu) + int(pv)) % 2 else 0)
        # brushed streaks
        val += (nz(int(u * 40), 7, len(key)) - 0.5) * 0.10
        return rp, val
    return t


def tex_wood(key):
    bark, inner, ring, extra = WOODS[key]
    brp, irp, rrp = ramp(bark, 6), ramp(inner, 6), ramp(ring, 5)

    def t(face, u, v):
        if face == 'top':
            d = math.hypot(u - 0.5, v - 0.5)
            if d > 0.44 or min(u, v, 1 - u, 1 - v) < 0.06:
                return brp, 0.5 + (nz(int(u * 30), int(v * 30), 3) - 0.5) * 0.2
            rr = d * 9 + vnoise(u * 30, v * 30, 4, 5) * 0.8
            if d < 0.04:
                return rrp, 0.1
            return (rrp, 0.25) if rr % 1.0 < 0.3 else (irp, 0.62 - d * 0.5)
        g = math.sin(u * 40 + vnoise(u * 20, v * 20, 3, 9) * 4)
        val = 0.55 + (-0.2 if g > 0.7 else 0.08 if g < -0.5 else 0)
        if extra == 'crystal' and nz(int(u * 10), int(v * 10), 4) < 0.12:
            return ramp('#7fe0f0', 5), 0.8
        return brp, val
    return t


def tex_hay(seed=5):
    rp = ramp('#d6b04a', 6)
    tw = ramp('#8a5a32', 5)

    def t(face, u, v):
        if face == 'top':
            if abs(u - 0.28) < 0.05 or abs(u - 0.72) < 0.05:
                return tw, 0.5
            return rp, 0.55 + (nz(int(u * 32), int(v * 32), seed) - 0.5) * 0.45
        along = u
        if abs(along - 0.28) < 0.05 or abs(along - 0.72) < 0.05:
            return tw, 0.55 - abs(v - 0.5) * 0.2
        s = math.sin(v * 70 + vnoise(u * 30, v * 30, 2, seed) * 5)
        return rp, 0.55 + (0.18 if s > 0.6 else -0.18 if s < -0.7 else 0)
    return t


def tex_pumpkin():
    rp = ramp('#e07a22', 6)
    st = ramp('#6a8a3a', 5)

    def t(face, u, v):
        if face == 'top':
            if math.hypot(u - 0.5, v - 0.5) < 0.1:
                return st, 0.6 - (u + v - 1) * 0.6
            ang = math.atan2(v - 0.5, u - 0.5)
            return rp, 0.55 + 0.15 * math.cos(ang * 8)
        rib = math.cos(u * 2 * PI * 4)
        return rp, 0.5 + 0.2 * rib - 0.15 * abs(v - 0.5)
    return t


# ---------------------------------------------------------------- glint
GLINT_TINT = (168, 88, 255)
GLINT_HI = (238, 206, 255)


def glint(cv, phase=0.42, sparkles=True, tint=0.07, halo=True):
    """SkyBlock-style enchant look, baked: violet tint + two diagonal shimmer
    bands (bottom-left -> top-right) + four-point sparkles + soft halo."""
    m = cv.opaque()
    span = cv.w + cv.h
    c1 = phase * span
    c2 = c1 + 0.28 * span
    for (x, y) in m:
        col = cv.c[y][x][:3]
        col = mix(col, GLINT_TINT, tint)
        u = x + (cv.h - 1 - y)              # along a "/" diagonal -> bands look like "\" stripes moving
        u = (x + y)
        for c, w, s in ((c1, 7.5, 0.62), (c2, 3.0, 0.45)):
            d = abs(((u - c + span / 2) % span) - span / 2)
            if d < w:
                f = 1 - d / w
                f = 1.0 if f > 0.66 else 0.66 if f > 0.33 else 0.33
                col = mix(col, GLINT_HI, s * f)
        cv.c[y][x] = col
    if halo:
        e = set()
        for (x, y) in m:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q = (x + dx, y + dy)
                if q not in m and 0 <= q[0] < cv.w and 0 <= q[1] < cv.h:
                    e.add(q)
        for (x, y) in e:
            cv.c[y][x] = (150, 70, 230, 70)
    if sparkles:
        for (x, y, r) in sparkle_spots(m, cv.w):
            star(cv, x, y, r)


def sparkle_spots(m, w):
    # deterministic: top-right corner area, left edge, bottom-right
    cands = [(w - 11, 9, 3), (8, 26, 2), (w - 15, w - 13, 2), (22, 8, 1)]
    return cands


def star(cv, x, y, r):
    cols = [(255, 255, 255), (232, 196, 255), (186, 120, 255)]
    cv.put(x, y, cols[0] + (255,))
    for k in range(1, r + 1):
        c = cols[min(2, k)] + (255,)
        for dx, dy in ((k, 0), (-k, 0), (0, k), (0, -k)):
            cv.put(x + dx, y + dy, c)
    if r >= 2:
        for dx, dy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
            cv.put(x + dx, y + dy, (200, 150, 255, 160))


# ---------------------------------------------------------------- catalogue
# (file id, label, group, drawing)
ITEMS = [
    ('cobblestone', 'Ench. Cobblestone', 'Mining', d_cobble),
    ('sand', 'Ench. Sand', 'Mining', d_sand),
    ('rubble', 'Ench. Rubble', 'Mining', d_rubble),
    ('clay', 'Ench. Clay', 'Mining', d_clay),
    ('sandstone', 'Ench. Sandstone', 'Mining', d_sandstone),
    ('slate', 'Ench. Slate', 'Mining', d_slate),
    ('basalt', 'Ench. Basalt', 'Mining', d_basalt),
    ('copper', 'Ench. Copper', 'Mining', lambda cv: d_ore(cv, 'copper', 301)),
    ('iron', 'Ench. Iron', 'Mining', lambda cv: d_ore(cv, 'iron', 302)),
    ('thorium', 'Ench. Thorium', 'Mining', lambda cv: d_ore(cv, 'thorium', 303)),
    ('cobalt', 'Ench. Cobalt', 'Mining', lambda cv: d_ore(cv, 'cobalt', 304)),
    ('adamantite', 'Ench. Adamantite', 'Mining', lambda cv: d_ore(cv, 'adamantite', 305)),
    ('mithril', 'Ench. Mithril', 'Mining', lambda cv: d_ore(cv, 'mithril', 306)),
    ('onyxium', 'Ench. Onyxium', 'Mining', lambda cv: d_ore(cv, 'onyxium', 307)),
    ('silver', 'Ench. Silver (later)', 'Mining', lambda cv: d_ore(cv, 'silver', 308)),
    ('gold', 'Ench. Gold (later)', 'Mining', lambda cv: d_ore(cv, 'gold', 309)),
    ('common-wood', 'Ench. Common Wood', 'Foraging', lambda cv: log(cv, 'common', 401)),
    ('hardwood', 'Ench. Hardwood', 'Foraging', lambda cv: log(cv, 'hard', 402)),
    ('redwood', 'Ench. Redwood', 'Foraging', lambda cv: log(cv, 'red', 403)),
    ('azurewood', 'Ench. Azurewood', 'Foraging', lambda cv: log(cv, 'azure', 404)),
    ('crystalwood', 'Ench. Crystalwood', 'Foraging', lambda cv: log(cv, 'crystal', 405)),
    ('fiber', 'Ench. Fiber (Rope)', 'Foraging', d_fiber),
    ('sap', 'Ench. Sap (Resin)', 'Foraging', d_sap),
    ('stick', 'Ench. Stick', 'Foraging', d_stick),
    ('wheat', 'Ench. Wheat', 'Farming', d_wheat),
    ('carrot', 'Ench. Carrot', 'Farming', d_carrot),
    ('corn', 'Ench. Corn', 'Farming', d_corn),
    ('lettuce', 'Ench. Lettuce', 'Farming', d_lettuce),
    ('pumpkin', 'Ench. Pumpkin', 'Farming', d_pumpkin),
    ('cauliflower', 'Ench. Cauliflower', 'Farming', d_cauliflower),
    ('turnip', 'Ench. Turnip', 'Farming', d_turnip),
    ('aubergine', 'Ench. Aubergine', 'Farming', d_aubergine),
    ('tomato', 'Ench. Tomato', 'Farming', d_tomato),
    ('chilli', 'Ench. Chilli', 'Farming', d_chilli),
    ('cotton', 'Ench. Cotton', 'Farming', d_cotton),
    ('rice', 'Ench. Rice', 'Farming', d_rice),
    ('potato', 'Ench. Potato', 'Farming', d_potato),
    ('onion', 'Ench. Onion', 'Farming', d_onion),
]
BLOCKS = [
    ('block-cobblestone', 'Ench. Cobblestone Block', tex_cobble(7)),
    ('block-copper', 'Ench. Copper Block', tex_metal('copper')),
    ('block-iron', 'Ench. Iron Block', tex_metal('iron')),
    ('block-thorium', 'Ench. Thorium Block', tex_metal('thorium')),
    ('block-cobalt', 'Ench. Cobalt Block', tex_metal('cobalt')),
    ('block-adamantite', 'Ench. Adamantite Block', tex_metal('adamantite')),
    ('block-mithril', 'Ench. Mithril Block', tex_metal('mithril')),
    ('block-onyxium', 'Ench. Onyxium Block', tex_metal('onyxium')),
    ('block-common-wood', 'Ench. Common Wood Block', tex_wood('common')),
    ('block-hardwood', 'Ench. Hardwood Block', tex_wood('hard')),
    ('block-redwood', 'Ench. Redwood Block', tex_wood('red')),
    ('block-azurewood', 'Ench. Azurewood Block', tex_wood('azure')),
    ('block-crystalwood', 'Ench. Crystalwood Block', tex_wood('crystal')),
    ('block-hay-bale', 'Ench. Hay Bale', tex_hay()),
    ('block-pumpkin', 'Ench. Pumpkin Block', tex_pumpkin()),
]


def base_icon(entry):
    cv = Cv(64, 64)
    if entry[0].startswith('block-'):
        cube(cv, entry[2])
    else:
        entry[3](cv)
    return cv


def copy_cv(cv):
    n = Cv(cv.w, cv.h)
    n.c = [row[:] for row in cv.c]
    return n


def build():
    os.makedirs(os.path.join(OUT, 'icons'), exist_ok=True)
    entries = [(e[0], e[1], e[2]) + (e[3],) for e in ITEMS] + [(b[0], b[1], 'Blocks', b[2]) for b in BLOCKS]
    rendered = []
    for e in entries:
        ent = (e[0], e[1], e[3]) if e[0].startswith('block-') else (e[0], e[1], e[2], e[3])
        b = base_icon(ent)
        g = copy_cv(b)
        glint(g)
        g.img().save(os.path.join(OUT, 'icons', 'ench-%s.png' % e[0]), optimize=True)
        rendered.append((e, b.img(), g.img()))
    sheet(rendered)
    demo_gif([r for r in rendered if r[0][0] in ('iron', 'common-wood', 'wheat', 'block-mithril')])
    print('icons:', len(rendered))


BG = (22, 30, 41)
SLOT = (16, 25, 37)
SLOT_E = (58, 72, 90)
TXT = (214, 228, 238)
SUB = (143, 166, 186)
GOLD = (232, 169, 59)


def sheet(rendered):
    S = 3
    cw, ch = 64 * S + 50, 64 * S + 112
    cols = 8
    groups = ['Mining', 'Foraging', 'Farming', 'Blocks']
    rows = []
    for g in groups:
        items = [r for r in rendered if r[0][2] == g]
        rows.append((g, [items[i:i + cols] for i in range(0, len(items), cols)]))
    head = 96
    nrows = sum(len(r[1]) for r in rows)
    Wd = cols * cw + 40
    Hd = head + nrows * ch + len(groups) * 40 + 30
    im = Image.new('RGBA', (Wd, Hd), BG + (255,))
    d = ImageDraw.Draw(im)
    d.text((20, 16), 'SkyWynn - Enchanted materials (concept icons, 64 x 64)', fill=GOLD, font=font(26))
    d.text((20, 54), 'Big = 3x with the baked glint.  Under it at 1x: the plain base (left) and the enchanted icon (right).  '
           'Original art, research/cloud/enchanted-art/make_enchanted.py', fill=SUB, font=font(15, False))
    y = head
    for g, chunks in rows:
        d.text((20, y + 6), g.upper(), fill=(180, 200, 201), font=font(19))
        d.line([(20, y + 32), (Wd - 20, y + 32)], fill=(94, 81, 44), width=2)
        y += 40
        for chunk in chunks:
            for i, (e, bimg, gimg) in enumerate(chunk):
                x = 20 + i * cw
                d.rectangle([x, y, x + 64 * S + 16, y + 64 * S + 16], fill=SLOT, outline=SLOT_E, width=2)
                big = gimg.resize((64 * S, 64 * S), Image.NEAREST)
                im.alpha_composite(big, (x + 8, y + 8))
                yy = y + 64 * S + 22
                d.rectangle([x, yy, x + 66, yy + 66], fill=SLOT, outline=SLOT_E)
                im.alpha_composite(bimg, (x + 1, yy + 1))
                d.rectangle([x + 72, yy, x + 138, yy + 66], fill=SLOT, outline=SLOT_E)
                im.alpha_composite(gimg, (x + 73, yy + 1))
                lab = e[1].replace('Ench. ', 'Enchanted ').replace(' Block', '\nBlock')
                d.multiline_text((x + 146, yy + 2), lab.replace(' (', '\n(').replace('Enchanted ', 'Enchanted\n'),
                                 fill=TXT, font=font(12), spacing=2)
            y += ch
    im = im.convert('RGB')
    im.save(os.path.join(OUT, 'enchanted-sheet.png'), optimize=True)


def demo_gif(rs):
    """the animated-overlay option: the shimmer band slides across (12 frames)"""
    frames = []
    S = 2
    for f in range(16):
        fr = Image.new('RGBA', (len(rs) * (64 * S + 12) + 12, 64 * S + 24), BG + (255,))
        for i, (e, bimg, gimg) in enumerate(rs):
            ent = (e[0], e[1], e[3]) if e[0].startswith('block-') else (e[0], e[1], e[2], e[3])
            cv = base_icon(ent)
            glint(cv, phase=f / 16.0, sparkles=(f % 8) < 5)
            fr.alpha_composite(cv.img().resize((64 * S, 64 * S), Image.NEAREST), (12 + i * (64 * S + 12), 12))
        frames.append(fr.convert('P', palette=Image.ADAPTIVE, colors=128))
    frames[0].save(os.path.join(OUT, 'glint-animated-demo.gif'), save_all=True, append_images=frames[1:],
                   duration=90, loop=0, optimize=True)


if __name__ == '__main__':
    build()
