#!/usr/bin/env python3
"""SkyWynn class emblems - shield crests, 64x64 + 128x128 (cloud draft 2026-10-06).

Original pixel art drawn from code (no copied art, no game files).
Run:  python3 research/cloud/class-art/make_emblems.py
Writes icons/class-<name>-64.png, -128.png, -64-locked.png and class-sheet.png
next to this script. Deterministic.
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
# Class emblems: shield crest + signature weapon / symbol
# ======================================================================
OUT = os.path.dirname(os.path.abspath(__file__))
PI = math.pi

# class colours: ClassDefs.COLORS (SkyyProfiles build 0.1.2) - Monk has none yet (proposal: Shaman's old #ff7a5c slot)
CLASSES = [
    ('Warrior', '#e0b060', 'Tank + crowd control', 'Swords, Spears'),
    ('Berserker', '#d9443f', 'Damage buffer + sustained melee', 'Axes, Maces'),
    ('Archer', '#8fd67a', 'Crowd control + focus marker', 'Shortbows, Crossbows'),
    ('Assassin', '#b58cff', 'Priority killer + debuffer', 'Daggers, Kunai'),
    ('Mage', '#7fb0e0', 'Burst damage + survival', 'Staffs, Spellbooks'),
    ('Priest', '#f2e6a0', 'Healer + protector', 'Wands, Soul Orb'),
    ('Monk', '#ff7a5c', 'Self-speed disruptor', 'Bo staff, Fist weapons'),
]

TRIM = ramp('#c9a24a', 6, light=0.45)      # gold ornament (vanilla frame ornaments read gold; UNVERIFIED exact)
RIM = ramp('#34465a', 6)                    # slate frame body
STEEL = ramp('#b9c6d2', 6, light=0.35)
DSTEEL = ramp('#8794a3', 6)
WOOD = ramp('#8a5a32', 6)
LEATHER = ramp('#3b3434', 6, light=0.7)
GOLDM = ramp('#e0aa3e', 6, light=0.45)


def erode(m, n):
    for _ in range(n):
        m = m - edge(m)
    return m


def shield_mask(cv, k):
    pts = [(7, 5), (57, 5), (57, 30)]
    # curved lower sides to the point (quadratic bezier)
    for i in range(1, 13):
        t = i / 12.0
        a, b, c = (57, 30), (56, 50), (32, 61)
        pts.append(((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * b[0] + t * t * c[0],
                    (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * b[1] + t * t * c[1]))
    for i in range(1, 13):
        t = i / 12.0
        a, b, c = (32, 61), (8, 50), (7, 30)
        pts.append(((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * b[0] + t * t * c[0],
                    (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * b[1] + t * t * c[1]))
    # notched top: two small shoulders + a raised centre for the gem
    top = [(7, 5), (20, 5), (26, 2.5), (32, 1), (38, 2.5), (44, 5)]
    pts = top + pts[1:]
    return poly(cv, [(x * k, y * k) for x, y in pts])


def part(cv, pts, cx, cy, ang, k, rp, ridge=0.0, mode='grad', level=0.0, outline=True, noise=0.0, seed=0):
    P = xf(pts, cx * k, cy * k, ang, k)
    m = poly(cv, P)
    tex = None
    if ridge:
        ca, sa = math.cos(ang), math.sin(ang)

        def tex(x, y):
            dx, dy = x + 0.5 - cx * k, y + 0.5 - cy * k
            lx = dx * ca + dy * sa
            return ridge if lx < 0 else -ridge * 0.7
    shade(cv, m, rp, mode, tex=tex, level=level, outline=outline, noise=noise, seed=seed)
    return m


def rod(cv, a, b, w, k, rp, bands=None, level=0.0):
    A, B = (a[0] * k, a[1] * k), (b[0] * k, b[1] * k)
    m = thick(cv, [A, B], max(2, w * k))
    ang = math.atan2(B[1] - A[1], B[0] - A[0])
    shade(cv, m, rp, 'cyl', x0=A[0], y0=A[1], ang=ang, r=max(1.0, w * k / 2), level=level)
    if bands:
        for t, col_rp in bands:
            px, py = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            ux, uy = (b[0] - a[0]), (b[1] - a[1])
            L = math.hypot(ux, uy); ux, uy = ux / L, uy / L
            bm = thick(cv, [((px - ux) * k, (py - uy) * k), ((px + ux) * k, (py + uy) * k)], max(2, (w + 1) * k))
            shade(cv, bm, col_rp, 'cyl', x0=A[0], y0=A[1], ang=ang, r=max(1.0, (w + 1) * k / 2))
    return m


# ------------------------------------------------------------ the weapons
def sword(cv, cx, cy, ang, k, L=34, w=3.6):
    # local: tip at -y; guard at y = 0
    blade = [(0, -L), (w, -L + 6), (w, 0), (-w, 0), (-w, -L + 6)]
    part(cv, blade, cx, cy, ang, k, STEEL, ridge=0.16)
    if k > 1:
        part(cv, [(0, -L + 8), (0.8, -L + 9), (0.8, -3), (-0.8, -3), (-0.8, -L + 9)], cx, cy, ang, k, DSTEEL, outline=False, level=-0.1)
    part(cv, [(-10, -1), (10, -1), (11, 1), (10, 3), (-10, 3), (-11, 1)], cx, cy, ang, k, GOLDM)
    part(cv, [(-2, 3), (2, 3), (2, 12), (-2, 12)], cx, cy, ang, k, LEATHER)
    if k > 1:
        for yy in (5, 8, 11):
            part(cv, [(-2, yy), (2, yy - 1.2), (2, yy - 0.4), (-2, yy + 0.8)], cx, cy, ang, k, ramp('#6a5a52', 4), outline=False)
    P = xf([(0, 14.5)], cx * k, cy * k, ang, k)[0]
    m = ell(cv, P[0], P[1], 3.4 * k, 3.4 * k)
    shade(cv, m, GOLDM, 'sphere', cx=P[0] - k, cy=P[1] - k, rx=4 * k, ry=4 * k)


def spear(cv, cx, cy, ang, k, L=50):
    ca, sa = math.cos(ang), math.sin(ang)
    a = (cx + sa * L * 0.45, cy - ca * L * 0.45 * -1)
    # shaft from bottom to top in local coords
    P0 = xf([(0, 22)], cx, cy, ang)[0]
    P1 = xf([(0, -16)], cx, cy, ang)[0]
    rod(cv, P0, P1, 2.6, k, WOOD, bands=[(0.82, GOLDM)])
    head = [(0, -32), (4.5, -24), (3, -18), (0, -16), (-3, -18), (-4.5, -24)]
    part(cv, head, cx, cy, ang, k, STEEL, ridge=0.16)
    part(cv, [(-2.6, -17), (2.6, -17), (2.2, -14), (-2.2, -14)], cx, cy, ang, k, GOLDM)


def battleaxe(cv, cx, cy, ang, k):
    P0 = xf([(0, 24)], cx, cy, ang)[0]
    P1 = xf([(0, -24)], cx, cy, ang)[0]
    rod(cv, P0, P1, 3, k, WOOD, bands=[(0.12, LEATHER), (0.2, LEATHER)])
    for s in (-1, 1):
        bl = [(1.5 * s, -18), (8 * s, -23), (13 * s, -22), (15 * s, -14), (13 * s, -6), (8 * s, -5), (1.5 * s, -10)]
        part(cv, bl, cx, cy, ang, k, STEEL, ridge=0.0)
        edgep = [(13 * s, -22), (15 * s, -14), (13 * s, -6), (11.8 * s, -7.5), (13.4 * s, -14), (11.8 * s, -20.5)]
        part(cv, edgep, cx, cy, ang, k, ramp('#e4ecf2', 5), outline=False)
    part(cv, [(-3, -20), (3, -20), (3, -9), (-3, -9)], cx, cy, ang, k, DSTEEL)
    part(cv, [(0, -30), (2.5, -25), (0, -22), (-2.5, -25)], cx, cy, ang, k, STEEL)


def mace(cv, cx, cy, ang, k):
    P0 = xf([(0, 24)], cx, cy, ang)[0]
    P1 = xf([(0, -12)], cx, cy, ang)[0]
    rod(cv, P0, P1, 2.6, k, DSTEEL, bands=[(0.1, LEATHER), (0.2, LEATHER)])
    C = xf([(0, -16)], cx, cy, ang)[0]
    for i in range(6):
        a = ang - PI / 2 + (i - 2.5) * 0.55
        fl = [(-2, 0), (2, 0), (1.2, -8), (-1.2, -8)]
        part(cv, fl, C[0], C[1], a + PI / 2, k, STEEL, ridge=0.12)
    m = ell(cv, C[0] * k, C[1] * k, 5.2 * k, 5.2 * k)
    shade(cv, m, DSTEEL, 'sphere', cx=(C[0] - 1.5) * k, cy=(C[1] - 1.5) * k, rx=6 * k, ry=6 * k)
    T = xf([(0, -22)], cx, cy, ang)[0]
    part(cv, [(0, -5), (2, 0), (0, 2), (-2, 0)], T[0], T[1], ang, k, STEEL)


def bow(cv, cx, cy, ang, k):
    # recurve: arc in local coords, string on the right
    pts = []
    for i in range(25):
        t = -1 + 2 * i / 24.0
        x = -9 * (1 - t * t) + (2.5 * t ** 4 if abs(t) > 0.8 else 0)
        y = t * 25
        pts.append((x, y))
    P = xf(pts, cx, cy, ang)
    m = thick(cv, [(p[0] * k, p[1] * k) for p in P], 3.6 * k)
    shade(cv, m, WOOD, 'grad')
    grip = xf([(-9, -4), (-9, 4)], cx, cy, ang)
    g = thick(cv, [(p[0] * k, p[1] * k) for p in grip], 4.6 * k)
    shade(cv, g, LEATHER, 'grad')
    for t in (-1, 1):
        tip = xf([(0, 25 * t)], cx, cy, ang)[0]
        m2 = ell(cv, tip[0] * k, tip[1] * k, 1.8 * k, 1.8 * k)
        shade(cv, m2, GOLDM, 'sphere', cx=tip[0] * k, cy=tip[1] * k, rx=2 * k, ry=2 * k)
    # string drawn back to the nock point
    s0, s1 = xf([(0, -25), (6, 0), (0, 25)], cx, cy, ang)[0:2], xf([(0, 25)], cx, cy, ang)[0]
    st = thick(cv, [(s0[0][0] * k, s0[0][1] * k), (s0[1][0] * k, s0[1][1] * k), (s1[0] * k, s1[1] * k)], max(1, k * 0.8))
    for p in st:
        if cv.get(*p) is None or True:
            cv.put(p[0], p[1], (236, 230, 214))
    # arrow, nocked at local (6, 0), pointing left (local -x)
    a0 = xf([(9, 0)], cx, cy, ang)[0]
    a1 = xf([(-20, 0)], cx, cy, ang)[0]
    rod(cv, a0, a1, 1.6, k, ramp('#c8a070', 5))
    part(cv, [(-26, 0), (-20, -3.5), (-19, 0), (-20, 3.5)], cx, cy, ang, k, STEEL)
    for s in (-1, 1):
        part(cv, [(4, 0), (9, 0), (11, 4.5 * s), (6, 4 * s)], cx, cy, ang, k, ramp('#d04a3a', 5))


def dagger(cv, cx, cy, ang, k):
    part(cv, [(0, -26), (3.6, -18), (3.2, 0), (-3.2, 0), (-3.6, -18)], cx, cy, ang, k, STEEL, ridge=0.16)
    part(cv, [(-7, -1), (7, -1), (8.5, 2.5), (-8.5, 2.5)], cx, cy, ang, k, DSTEEL)
    part(cv, [(-1.8, 2.5), (1.8, 2.5), (1.8, 10), (-1.8, 10)], cx, cy, ang, k, LEATHER)
    part(cv, [(0, 9), (3, 12), (0, 15), (-3, 12)], cx, cy, ang, k, ramp('#9a6ad8', 5))


def kunai(cv, cx, cy, ang, k):
    part(cv, [(0, -26), (5, -14), (2, -8), (-2, -8), (-5, -14)], cx, cy, ang, k, DSTEEL, ridge=0.16)
    part(cv, [(-1.6, -8), (1.6, -8), (1.6, 5), (-1.6, 5)], cx, cy, ang, k, LEATHER)
    if k > 1:
        for yy in (-5, -2, 1, 4):
            part(cv, [(-1.6, yy), (1.6, yy - 1), (1.6, yy - 0.3), (-1.6, yy + 0.7)], cx, cy, ang, k, ramp('#7a2a2a', 4), outline=False)
    C = xf([(0, 9)], cx, cy, ang)[0]
    o = ell(cv, C[0] * k, C[1] * k, 4.2 * k, 4.2 * k)
    i = ell(cv, C[0] * k, C[1] * k, 2.0 * k, 2.0 * k)
    shade(cv, o - i, DSTEEL, 'grad')


def staff(cv, cx, cy, ang, k, rp_orb):
    P0 = xf([(0, 27)], cx, cy, ang)[0]
    P1 = xf([(0, -14)], cx, cy, ang)[0]
    rod(cv, P0, P1, 3, k, WOOD, bands=[(0.55, GOLDM)])
    # claw holding the orb
    for s in (-1, 1):
        part(cv, [(0, -13), (6 * s, -18), (7.5 * s, -25), (5 * s, -19), (0, -16)], cx, cy, ang, k, GOLDM)
    C = xf([(0, -22)], cx, cy, ang)[0]
    gl = ell(cv, C[0] * k, C[1] * k, 9 * k, 9 * k)
    for p in gl:
        if cv.get(*p) is not None:
            cv.put(p[0], p[1], mix(cv.get(*p), hx('#dff0ff'), 0.18))
    m = ell(cv, C[0] * k, C[1] * k, 5.6 * k, 5.6 * k)
    shade(cv, m, rp_orb, 'sphere', cx=(C[0] - 1.5) * k, cy=(C[1] - 1.5) * k, rx=6.5 * k, ry=6.5 * k)
    cv.put(int((C[0] - 2) * k), int((C[1] - 2) * k), (255, 255, 255))
    for (dx, dy, r) in [(-10, 4, 2), (9, -6, 2), (8, 8, 1)]:
        sx, sy = int((C[0] + dx) * k), int((C[1] + dy) * k)
        rr = max(1, int(r * k))
        for j in range(-rr, rr + 1):
            cv.put(sx + j, sy, (240, 248, 255)); cv.put(sx, sy + j, (240, 248, 255))


def book(cv, cx, cy, k, rp):
    # small closed spellbook at the staff's foot
    part(cv, [(-7, -5), (9, -5), (9, 7), (-7, 7)], cx, cy, 0, k, ramp('#efe4c8', 5))   # pages
    m = part(cv, [(-8, -6), (8, -6), (8, 5), (-8, 5)], cx, cy, 0, k, rp)
    part(cv, [(-8, -6), (-5, -6), (-5, 6), (-8, 6)], cx, cy, 0, k, ramp('#4a2e5a', 4))
    part(cv, [(1.5, -4), (4.5, -0.5), (1.5, 3), (-1.5, -0.5)], cx, cy, 0, k, ramp('#8fd0ff', 5, light=0.6))
    part(cv, [(6, -6), (8, -6), (8, -3), (6, -4)], cx, cy, 0, k, GOLDM)


def soul_orb(cv, cx, cy, k):
    # glow
    gl = ell(cv, cx * k, cy * k, 12 * k, 12 * k)
    for p in gl:
        if cv.get(*p) is not None:
            cv.put(p[0], p[1], mix(cv.get(*p), hx('#fff6c8'), 0.22))
    soul = ell(cv, cx * k, cy * k, 6 * k, 6 * k)
    shade(cv, soul, ramp('#9ff0ff', 6, light=0.6), 'sphere', cx=(cx - 1) * k, cy=(cy - 1.5) * k, rx=7 * k, ry=7 * k, outline=False)
    # cage bars (meridians) + rings
    bars = set()
    for dx in (-8, -4, 0, 4, 8):
        h = math.sqrt(max(0, 81 - dx * dx))
        bx = dx * 0.9
        bars |= thick(cv, [((cx + bx) * k, (cy - h) * k), ((cx + bx * 1.08) * k, cy * k), ((cx + bx) * k, (cy + h) * k)], max(1.5, 1.4 * k))
    ring = ell(cv, cx * k, cy * k, 9.4 * k, 9.4 * k) - ell(cv, cx * k, cy * k, 7.9 * k, 7.9 * k)
    eq = thick(cv, [((cx - 9) * k, cy * k), ((cx + 9) * k, cy * k)], max(1.5, 1.2 * k))
    shade(cv, bars | ring | eq, GOLDM, 'grad', bevel=0.1)
    for t in (-1, 1):
        cap = ell(cv, cx * k, (cy + 9.8 * t) * k, 2.4 * k, 1.8 * k)
        shade(cv, cap, GOLDM, 'sphere', cx=cx * k, cy=(cy + 9.8 * t) * k, rx=2.6 * k, ry=2.6 * k)


def wand(cv, cx, cy, ang, k):
    P0 = xf([(0, 22)], cx, cy, ang)[0]
    P1 = xf([(0, -6)], cx, cy, ang)[0]
    rod(cv, P0, P1, 2.4, k, ramp('#e8dcc0', 6), bands=[(0.25, GOLDM), (0.9, GOLDM)])
    part(cv, [(0, -14), (3.5, -8), (0, -4), (-3.5, -8)], cx, cy, ang, k, ramp('#fff0a0', 5, light=0.5))


def halo(cv, cx, cy, k):
    o = ell(cv, cx * k, cy * k, 9 * k, 3 * k) - ell(cv, cx * k, cy * k, 6.6 * k, 1.6 * k)
    shade(cv, o, ramp('#ffe070', 6, light=0.6), 'grad', bevel=0.2)


def bo(cv, cx, cy, ang, k):
    P0 = xf([(0, 28)], cx, cy, ang)[0]
    P1 = xf([(0, -28)], cx, cy, ang)[0]
    rod(cv, P0, P1, 3.2, k, ramp('#a8743e', 6), bands=[(0.05, ramp('#c94a3a', 5)), (0.5, ramp('#c94a3a', 5)), (0.95, ramp('#c94a3a', 5))])


def claws(cv, cx, cy, ang, k):
    for i, dx in enumerate((-5, 0, 5)):
        part(cv, [(dx - 1.6, -4), (dx + 1.6, -4), (dx + 1.2, -26 + abs(dx) * 0.4), (dx, -30 + abs(dx) * 0.4), (dx - 1.2, -26 + abs(dx) * 0.4)],
             cx, cy, ang, k, STEEL, ridge=0.18)
    part(cv, [(-8.5, -5), (8.5, -5), (9.5, 0), (8.5, 9), (-8.5, 9), (-9.5, 0)], cx, cy, ang, k, LEATHER, noise=0.05, seed=3)
    if k > 1:
        for yy in (-1, 3, 7):
            part(cv, [(-8, yy), (8, yy - 0.6), (8, yy + 0.2), (-8, yy + 0.8)], cx, cy, ang, k, ramp('#6a5e58', 4), outline=False)
    for dx in (-5, 0, 5):
        P = xf([(dx, -5)], cx, cy, ang)[0]
        m = ell(cv, P[0] * k, P[1] * k, 1.6 * k, 1.6 * k)
        shade(cv, m, GOLDM, 'sphere', cx=P[0] * k, cy=P[1] * k, rx=2 * k, ry=2 * k, outline=k > 1)


def swirl(cv, cx, cy, k, col):
    for j, (r0, a0) in enumerate([(13, 0.2), (16, 2.4), (11, 4.3)]):
        pts = [((cx + math.cos(a0 + t * 0.12) * (r0 - t * 0.12)) * k, (cy + math.sin(a0 + t * 0.12) * (r0 - t * 0.12)) * k) for t in range(12)]
        m = thick(cv, pts, max(1.5, 1.3 * k))
        for p in m:
            if cv.get(*p) is not None:
                cv.put(p[0], p[1], mix(cv.get(*p), col, 0.75))


SYMBOLS = {
    'Warrior': lambda cv, k, rp: (spear(cv, 32, 32, -0.62, k), sword(cv, 33, 36, 0.62, k)),
    'Berserker': lambda cv, k, rp: (mace(cv, 34, 35, 0.6, k), battleaxe(cv, 30, 36, -0.55, k)),
    'Archer': lambda cv, k, rp: bow(cv, 33, 32, -PI / 4 - PI / 2 + PI, k),
    'Assassin': lambda cv, k, rp: (kunai(cv, 33, 36, 0.62, k), dagger(cv, 31, 36, -0.62, k)),
    'Mage': lambda cv, k, rp: (book(cv, 24, 44, k, ramp('#3a5aa0', 6)), staff(cv, 34, 33, 0.38, k, ramp('#c49cff', 6, light=0.6))),
    'Priest': lambda cv, k, rp: (wand(cv, 42, 38, 0.6, k), soul_orb(cv, 29, 30, k), halo(cv, 29, 16.5, k)),
    'Monk': lambda cv, k, rp: (swirl(cv, 32, 32, k, hx('#fff0e0')), bo(cv, 32, 32, -0.75, k), claws(cv, 36, 39, 0.45, k)),
}


def emblem(name, col, size):
    k = size / 64.0
    cv = Cv(size, size)
    sh = shield_mask(cv, k)
    t = max(1, int(round(1.5 * k)))
    shade(cv, sh, TRIM, 'grad', bevel=0.22)
    rim = erode(sh, t + 1)
    shade(cv, rim, RIM, 'grad', noise=0.04, seed=5, bevel=0.14)
    inner_trim = erode(rim, int(round(3 * k)))
    shade(cv, inner_trim, TRIM, 'grad', outline=False, bevel=0.0, level=0.05)
    field = erode(inner_trim, max(1, int(round(1 * k))))
    frp = ramp(col, 7, dark=0.62, light=0.25)
    x0, y0, x1, y1 = bbox(field)
    cxm = (x0 + x1) / 2.0
    step = 8 * k

    def ftex(x, y):
        v = -0.30
        v += 0.08 if x < cxm else -0.06            # parted "per pale": left lit, right shaded
        u = (x - cxm) / step; w = (y - y0) / step
        if ((int(math.floor(u + w)) + int(math.floor(u - w))) % 2) == 0:
            v += 0.05                               # lozenge (diaper) pattern
        return v
    shade(cv, field, frp, 'grad', outline=True, tex=ftex, bevel=0.12, seed=9)
    # rivets on the rim
    if size >= 128:
        for (rx, ry) in [(11, 9), (53, 9), (10, 24), (54, 24), (14, 41), (50, 41), (23, 53), (41, 53)]:
            m = ell(cv, rx * k, ry * k, 1.6 * k, 1.6 * k)
            if m <= rim:
                shade(cv, m, TRIM, 'sphere', cx=(rx - 0.5) * k, cy=(ry - 0.5) * k, rx=2 * k, ry=2 * k)
    else:
        for (rx, ry) in [(10.5, 9), (53.5, 9), (17, 47), (47, 47)]:
            cv.put(int(rx * k), int(ry * k), TRIM['f'][4])
    before = [row[:] for row in cv.c]
    SYMBOLS[name](cv, k, frp)
    for y in range(size):          # keep the symbol inside the shield; re-draw the outer outline
        for x in range(size):
            if (x, y) not in sh:
                cv.c[y][x] = before[y][x]
    for p in edge(sh):
        cv.put(p[0], p[1], TRIM['o'])
    # crest gem at the top centre, in the class colour
    gem = poly(cv, [(32 * k, 0), (36 * k, 4.5 * k), (32 * k, 9 * k), (28 * k, 4.5 * k)])
    shade(cv, gem, TRIM, 'grad', bevel=0.2)
    g2 = poly(cv, [(32 * k, 1.8 * k), (34.6 * k, 4.5 * k), (32 * k, 7.2 * k), (29.4 * k, 4.5 * k)])
    shade(cv, g2, ramp(col, 5, light=0.5), 'grad', outline=False, bevel=0.25)
    return cv


def locked(img):
    g = img.convert('LA').convert('RGBA')
    px = g.load(); src = img.load()
    for y in range(g.size[1]):
        for x in range(g.size[0]):
            r, gg, b, a = px[x, y]
            if a:
                px[x, y] = (int(r * 0.55 + 18), int(gg * 0.58 + 22), int(b * 0.62 + 30), a)
    return g


BG = (22, 30, 41)
ROW = (16, 25, 37)
SLOT_E = (58, 72, 90)
TXT = (214, 228, 238)
SUB = (143, 166, 186)
TITLE = (180, 200, 201)
GOLD = (232, 169, 59)


def build():
    os.makedirs(os.path.join(OUT, 'icons'), exist_ok=True)
    res = []
    for name, col, role, weapons in CLASSES:
        i64 = emblem(name, col, 64).img()
        i128 = emblem(name, col, 128).img()
        i64.save(os.path.join(OUT, 'icons', 'class-%s-64.png' % name.lower()), optimize=True)
        i128.save(os.path.join(OUT, 'icons', 'class-%s-128.png' % name.lower()), optimize=True)
        locked(i64).save(os.path.join(OUT, 'icons', 'class-%s-64-locked.png' % name.lower()), optimize=True)
        res.append((name, col, role, weapons, i64, i128))
    sheet(res)
    print('emblems:', len(res))


def sheet(res):
    cw = 300
    Wd = 20 + cw * len(res) + 10
    Hd = 980
    im = Image.new('RGBA', (Wd, Hd), BG + (255,))
    d = ImageDraw.Draw(im)
    d.text((20, 14), 'SkyWynn - class emblems (concept, 64 x 64 + 128 x 128)', fill=GOLD, font=font(26))
    d.text((20, 52), 'Row 1: the 128 icon at 2x.  Row 2: 128 at 1x, 64 at 2x, 64 at 1x, 64 "locked" (coming later).  '
           'Row 3: on a Profiles-style class card.  Original art, research/cloud/class-art/make_emblems.py',
           fill=SUB, font=font(15, False))
    for i, (name, col, role, weapons, i64, i128) in enumerate(res):
        x = 20 + i * cw
        y = 90
        d.rectangle([x, y, x + 272, y + 272], fill=ROW, outline=SLOT_E, width=2)
        im.alpha_composite(i128.resize((256, 256), Image.NEAREST), (x + 8, y + 8))
        d.text((x, y + 282), name.upper(), fill=hx(col), font=font(20))
        d.text((x, y + 310), col + ('  (proposal)' if name == 'Monk' else ''), fill=SUB, font=font(13, False))
        y = 430
        d.rectangle([x, y, x + 132, y + 132], fill=ROW, outline=SLOT_E)
        im.alpha_composite(i128, (x + 2, y + 2))
        d.rectangle([x + 140, y, x + 272, y + 132], fill=ROW, outline=SLOT_E)
        im.alpha_composite(i64.resize((128, 128), Image.NEAREST), (x + 142, y + 2))
        d.rectangle([x, y + 140, x + 66, y + 206], fill=ROW, outline=SLOT_E)
        im.alpha_composite(i64, (x + 1, y + 141))
        d.rectangle([x + 72, y + 140, x + 138, y + 206], fill=ROW, outline=SLOT_E)
        im.alpha_composite(locked(i64), (x + 73, y + 141))
        d.text((x + 146, y + 160), '64 / locked', fill=SUB, font=font(12, False))
        # class card mock (vanilla row colours from research/Vanilla-UI-Style-Guide.md section 5)
        y = 650
        card = Image.new('RGBA', (272, 300), (0, 0, 0, 0))
        cd = ImageDraw.Draw(card)
        cd.rectangle([0, 0, 271, 299], fill=(16, 25, 37, 255), outline=(94, 81, 44, 255), width=2)
        card.alpha_composite(i128, (72, 14))
        cd.text((136, 154), name.upper(), fill=hx(col), font=font(19), anchor='mt')
        cd.line([(30, 182), (242, 182)], fill=(94, 81, 44, 255), width=1)
        cd.text((136, 196), role, fill=(150, 169, 190), font=font(13, False), anchor='mt')
        cd.text((136, 222), weapons, fill=(183, 206, 221), font=font(13), anchor='mt')
        cd.text((136, 256), 'Lv 1', fill=(122, 138, 154), font=font(12, False), anchor='mt')
        im.alpha_composite(card, (x, y))
    im.convert('RGB').save(os.path.join(OUT, 'class-sheet.png'), optimize=True)


if __name__ == '__main__':
    build()
